# Prof Revision 거리 기반 정밀 도달 개발명세 작성

2026-11-26 KST. 상태: 명세 작성·CPU 보상 재평가 완료, 환경 구현 전.

**최신 상태:** 같은 날 후속 사용자 지시로 Reach×2·Formation×0.7·이탈−40·장애물 변위−300(cap0.04 유지)로 명세를 수정했다. 아래 초기+100/−100 기록은 당시 이력이며 현재 계약은 마지막 후속 절과 연결된 최신 명세를 따른다.

## 요청과 결정

사용자가 목표에 가까워질수록 힘 정렬 중요도 감소·거리 개선 중요도 증가·역방향 비용을 정방향 보상과 동등하게 만드는 개발명세를 요청했다. 비동기 질문에 **v0_3_1 상속 새 환경**, **성공 반경3cm 유지**로 답변했다. 환경 이름은 지정하지 않아 `Inspire-Sweep-Prof-Revision-v0_3_2`를 제안 이름으로 기록했다. 사용자 허락을 요구하는 절차가 아니라 대상·성공 정의를 확인하는 질문이었다.

기준 루트commit `4bff6449f2cbc8b7ee09abbe2a1956c86e2a060a`, 문서commit `e35db19a646c0bbfe33de499f49f8ac4195a3b9f`. 기존 분석 scripts/문서 작업트리·IsaacLab·사용자 PLAN22.md를 보존했다.

## 설계와 전후 차이

[개발명세](../../01_plan/environments/2026-11-26_PROF_REVISION_V0_3_2_SPEC.md)에 계약·수식·구현 파일·reset/terminal 수명·dt·telemetry·회귀/학습 비교를 정의했다. 원거리6cm 이상 기존 힘 정렬 유지,3cm 이하는 영향0,사이는smoothstep이다. 별도 거리 민감도는6cm에서1·3cm에서1.5·중심에서2로 연속 증가한다. 초안의3cm 안 고정2배 대신, 중심까지 더 정밀하게 접근한다는 요청에 맞춰 중심까지 증가하는 함수를 최종안으로 채택했다.

거리 민감도 적분 `H`의 차이를 양·음 양쪽에 사용한다. 양의 항은 기존 접촉 조건과 완화된 힘 정렬을 적용하고, 이탈에는 gate를 곱하지 않는다. weight+100/−100. 할인하지 않은 두 항의 닫힌 왕복 합≤0이라는 제한된 성질만 보장하며, PPO gamma0.98의 할인 수익·다른 보상까지 악용이 사라진다고 주장하지 않았다.

보상 근거로 기존model15550의512episode를 재평가했다. 최종안 Sweep6.734→9.703,이탈−0.375→−3.132,순보상12.477→12.690. 성공334건13.469→14.517,진입 후 실패157건11.801→10.350. 새 학습 효과가 아니라 동일 궤적의 예산 변화다. 근거리 최대배수1/1.5/2/3 민감도도 보존했다.

## 실행과 검증

workspace 루트에서 다음 CPU 명령을 실행했다.

```powershell
python outputs/prof_revision_precision_spec_20261126/check_design.py
```

산출물은 [요약과 수학 검사](../../../../outputs/prof_revision_precision_spec_20261126/summary.json), [전체 episode](../../../../outputs/prof_revision_precision_spec_20261126/episodes.csv), [계수 그림](../../../../outputs/prof_revision_precision_spec_20261126/proposed_weights.png)이다. 두seed×4개 배수 각각200개 구간을 analytic 적분과1001점 수치적분으로 대조했다.1,000개 닫힌 경로의 할인하지 않은 합≤0·분할 불변성·finite 검사 통과. 첫step 양의 gate0을 확인하고 저장 raw retreat로 첫step 이탈을 포함했다. reset 간 위치·거리를 섞지 않았다.

환경 패키지·훈련 checkpoint·기존 분석 코드는 이번 작업에서 수정하지 않았다. GPU·Isaac Sim·새 정책 학습은 실행하지 않았다. 새 환경 이름 확정·구현·실제 성공률 개선은 남아 있으며, 명세의 초기 계수는 검증할 실험값이다. 문서 검사·그림 확인 결과는 완료 기록에 남긴다.

완료 확인: 수치적분 최대오차1.42e−11,분할합 오차2.78e−17.0/3/4.5/6cm 계수·H의 단조성·정지차분0 검사 통과. 계수 PNG를 직접 확인했다. CPU 검산 스크립트 py_compile 통과. 변경 Markdown3파일 수식 검사 통과, 외부 산출물 포함 링크 오류0(외부7·내부222),루트/문서 git diff --check 통과(LF/CRLF 안내만 존재). 명세는 구현 계획으로 전달하며 환경 계약이 이미 변경됐다고 표기하지 않는다.

## 후속: 보상 비율 변경과 장애물 cap 조사

사용자가 기존 term 평균을 근거로 Reach2배,Formation0.7배,이탈은현재2배,장애물 변위는cap에 막혔으면cap10배·아니면비용2배를 명세에 추가하도록 지시했다. 현재 코드의기준weight를 확인해 Reach4.9→9.8,Formation0.245→0.1715,이탈−20→−40으로 반영했다. 이탈H의 근거리 가중은 유지하므로 같은 궤적의 평균이탈은−0.375→−1.253이며 정확히2배로 고정되는 것은 아니다.

원본 `active_obstacle_displacement_cost`는 활성 비타겟의reset 대비3D 제곱변위를 합산하고raw0.04m²에cap한다. seed42/43 전체254,165step의현재/초기 위치·활성mask로독립 재계산하여cap 도달0step·0episode,잘린비용0을 확인했다. 최대raw0.0083983504m²(상한21.0%),다른seed최대0.0062048709m²(15.5%). 저장된비용과재계산값의 최대step 오차7.13e−9. 사용자 조건에 따라 **weight−300,raw cap0.04 유지**로 확정했다. cap10배안은 조건이 성립하지 않아 적용하지 않는다.

초기 명세·스크립트의 근거를 보존하기 위해 최신 산출물은 `outputs/prof_revision_precision_spec_20261126/revision2/`에 분리했다. [요약/cap 근거](../../../../outputs/prof_revision_precision_spec_20261126/revision2/summary.json) · [term별최신비중](../../../../outputs/prof_revision_precision_spec_20261126/revision2/rewards.csv) · [재평가기](../../../../outputs/prof_revision_precision_spec_20261126/revision2/check_weights.py).

```powershell
python outputs/prof_revision_precision_spec_20261126/revision2/check_weights.py
```

같은512episode에서Sweep9.703·이탈−1.253·Reach2.350·Formation4.797·장애물−0.278,전체순보상13.549. 양의예산Sweep57.1%·Reach14.7%·Formation28.2%. 진입 후 실패157건도11.801→12.215로 증가한다. 새학습 성능 개선으로 주장하지 않는다.

명세의목적·범위·계수표·최종식·예산·구현계획·검증·인계를 함께 수정했다. +100/−40은 더이상대칭이 아니므로초기'닫힌왕복 합≤0' 보장을 삭제하고 ΔH0.01 왕복시+0.6 반례를 명시했다. Reach의음의기여도2배임을 명시했다. 부모환경·훈련코드·checkpoint·과거보고서는변경하지 않았다. 이번 작업은명세수정과저장궤적 CPU검증이며환경구현·새Play·학습은미실행이다.
