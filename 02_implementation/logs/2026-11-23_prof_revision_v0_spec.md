# Prof Revision v0 개발 명세 작성 기록

작성일: 2026-11-23. 작업 종류: **설계 문서 작성만 수행**. 새 환경은 미구현·미등록이며 학습을 실행하지 않았다.

## 요청과 기준

사용자는 Single Contact v0을 참조하여 `Inspire-Sweep-Prof-Revision-v0`의 개발 명세를 요청했다. 새 계열은 기존 환경 상속을 끊고, 초기 가시 OBB·5개 손끝 Pose·증분 Reach·Contact Formation·Sweep 계수2배·EEF 높이 제한 제거를 반영한다. 후속 답변으로 Actor는 초기 OBB를 고정하고 현재 EEF로만 변환한다고 확정했다.

- Workspace 기준 branch/HEAD: `main` / `d59007b3a946805c69a7181d5b9d7688dbb0b875`.
- 문서 submodule 기준 branch/HEAD: `main` / `c66eef0a7638fd901284eef84a3bbbd84c5a36db`.
- 작업 시작 시 root status는 문서 submodule 차이와 사용자 미추적 파일 `docs/plan/PLAN20.md`였다. 문서 submodule 내부 작업트리는 clean이었다. 기존 커밋·사용자 파일을 보존했다.
- [개발 명세](../../01_plan/environments/2026-11-23_PROF_REVISION_V0_SPEC.md)를 기준 문서로 추가하고 현재 인계에 미구현 상태로 연결한다. 활성 환경 등록 목록에는 실행 가능한 환경으로 추가하지 않는다.

## 실제 코드에서 확인한 사항

1. Single Contact v0은 Sweep v0의 자식이며 v1은 v0의 자식이다. v1의 Reaching은 5cm 초과 거리의 대칭 증분·weight4.9지만 접근점과 방향 보상·팔 종료 비용도 바뀐다. 새 명세는 그중 대칭 증분 방식만 가져온다.
2. v0 실제 직접 관측은 손 구동 위치6D를 포함한66D다. tactile은34D bit가 아니라17D paired 상태이며 action은12D다. 사용자의 관측 목록대로 손 구동 위치를 손끝 Pose로 대체하고 타겟3D를7D로 바꾸면99D가 된다.
3. v0의 초기 타겟·장애물 대표점은 월드 snapshot을 유지하고 EEF로만 변환한다. Actor/Critic은 같은 입력을 사용한다. 기존 모델은 장애물64D와 export 폭을 고정하고 있어 새 모델 계약이 필요하다.
4. `observed_obb`는 가로 가시 구간·최소2cm 및20%·전체 깊이와 높이 유지·XY 최소 면적 직사각형을 사용한다. 원본 물체 ID를 반환하지 않고 조각이 여러 개일 수 있어 새 adapter의 source mapping과 타겟 선택 규칙이 필요하다.
5. 기존 EEF 높이 제한은 독립 reward term이 아니라 Sweep 접촉 인정 state의12cm 비교다. 선반 충돌·실패 조건까지 제거하지 않는다.
6. 기존 Scene `finger_frame`은 두 고정 tool offset이다. 5개 손가락 현재 Pose는 distal tactile pad body와 `tactile_regions.json`의 sensor-local bounds를 사용하도록 명세화했다.
7. 현재 v0 성공 callable은 실제 기하 중심에 대한 엄격한 `<0.03`이다. 새 과업은 가시 조각 중심을 옮기므로 성공·거리 지표도 같은 중심으로 바꾸고 workspace 개발 지침에 따라 `<=0.03`을 적용한다. 기존 환경은 그대로 둔다.

## 설계 선택과 영향

| 선택 | 근거와 영향 |
| --- | --- |
| 관측 snapshot과 보상 추적 분리 | 사용자 후속 답변 반영. Actor GT 누출을 막고 보상은 초기 가시 조각을 실제 물체와 함께 추적 |
| yaw 관측과 full rotation 계산 분리 | 기울어진 EEF에서7D OBB의 표현 한계를 명시. 실제 표면 거리는 full rigid transform 사용 |
| encoder128→64→32→16 | 요청한 후보를 초기 구조로 채택, Actor/Critic 독립 encoder·rollout 원시 입력 저장 |
| Reach weight4.9 | v1 방식과 수치 참조, 반경만10cm·접근점은 가시 OBB 중심 |
| Formation 거리 합 척도0.05m·weight0.245 | 기준 접근 속도0.10m/s에서 최대 실제 step 보상이 Reach의 절반. 정지 시 양의 rate와 episode 누적 가능성 명시 |
| 단일 타겟 조각과16 장애물 슬롯 | 가장 넓은 타겟 조각, 장애물 조각별 슬롯, 동률·정렬·fallback 규칙 확정 |
| 독립 구성 | 새 역할별 파일·프레임워크 직접 상속, 기존 runtime 전체 우회 호출 금지, 계산 helper 재사용 허용 |

영향 대상은 문서와 인계뿐이다. 새 환경 Python 파일·Gym 등록·PPO·물리 자산·공용 함수·기존 환경·`logs/rsl_rl`을 수정하지 않는다.

## 최종 요청 대조

| 요청 | 명세 반영 |
| --- | --- |
| 새 이름과 envs 새 파일 | 정확한 ID, `envs/prof_revision_envs.py` 예정 경로 |
| 기존 상속 단절·함수 재사용 가능 | EnvCfg/runtime/Scene/state/모델/PPO 독립 계약 |
| 초기 정면 가시 OBB | reference 알고리즘, 노출 문턱, reset snapshot·조각·source mapping |
| 타겟7D·장애물8×16·encoder 추천 | frame·단위·yaw 한계·128→64→32→16·mask 처리 |
| EEF 뒤 Finger Pose35D | distal pad5개·순서·xyzw·현재 EEF 변환 |
| Reach 대칭 변화·가시 중심·10cm | 식·weight·dt·경계·reset cache |
| Formation 표면 거리 합 역비례·내부0·대략 절반 | 회전 OBB 거리식·정규화 역수·기준 속도 산정·비율의 적용 범위 |
| Sweep 가시 중심·형상 고정·2배 | local rigid attachment·현재 중심 거리·+100/−20 |
| EEF Z 제한 삭제 | 접촉 인정의12cm 비교 제거, 별개 선반 실패 보존 |
| 실제 구현 아님 | 문서만 추가, 향후 검사와 이번 검사를 구분 |

## 검증과 미검증 범위

실제 수행: 관련 EnvCfg·runtime·state·관측·reward·termination·reset·encoder/export·Scene·tactile metadata·observed_obb 소스를 읽고 대조했다. 표준 Python 산술 검사로99D/115D/227D, Reach 예시5개, Formation 예시4개, 기준 속도에서0.5 비율을 확인했다.

문서 형식·상대 링크·공백 검사는 다음 명령으로 수행했다.

```bash
cd example/Contact-Rich-Manipulation-Context
python 00_guidelines/scripts/check_markdown_math.py \
  01_plan/environments/2026-11-23_PROF_REVISION_V0_SPEC.md \
  02_implementation/logs/2026-11-23_prof_revision_v0_spec.md \
  01_plan/00_HANDOFF_BRIEF.md
python 00_guidelines/scripts/check_document_links.py --check-external \
  01_plan/environments/2026-11-23_PROF_REVISION_V0_SPEC.md \
  02_implementation/logs/2026-11-23_prof_revision_v0_spec.md
python 00_guidelines/scripts/check_document_links.py 01_plan/00_HANDOFF_BRIEF.md
git diff --check
```

결과: 수식 형식3파일 통과, 새 명세·로그의 내부3개 및 workspace 외부14개 링크 오류0, 인계 내부187개 링크 오류0. 문서 저장소와 workspace의 `git diff --check` 통과. 새 미추적 문서2개의 줄 끝 공백도 별도 검사했다. workspace에서 `git diff --exit-code -- src/inspire_sweep_baseline src/observed_obb`가0으로 종료하여 두 코드 경로의 tracked 변경이 없음을 확인했다. 최종 문서 변경은 새 명세·새 로그·인계 첫 항목뿐이다.

미실행: 신규 환경 import·등록·CPU 구현 테스트·GPU/Isaac Sim·실제 pad marker·2048환경 reset·PPO·학습 성능 평가. 환경이 아직 구현되지 않았으므로 명세의 향후 검증 항목은 통과 결과가 아니다. Markdown 렌더러의 시각적 확인도 수행하지 않았다.

## 후속 수정 OBB 필터와 손가락 Frame 및 collection 성능

2026-11-23 사용자 추가 지시를 기존 명세에 반영했다. 이번에도 문서 수정만 수행하며, 앞선 작성 기록의 고정 필터 설명은 아래 최종 계약으로 대체한다. 작업 시작 시 이미 있던 명세·로그·인계 변경과 사용자 `docs/plan/PLAN20.md`는 보존했다.

| 요청 | 변경 전 | 변경 후와 의도 |
| --- | --- | --- |
| OBB에 맞는 유사 수준의 저비용 노출 필터 허용 | 2cm AND 20% 고정, 전체 reference Box 집합 일치 요구 | 기존 문턱은 비교 기준. 가시 구간 폭·비율·투영 면적 등 허용, 재사용 가능한 기하량과 batch 계산 우선. 동일 채택 구간의 기하 검증과 필터 집합 변경의 유사성 검증을 분리 |
| 손가락 Frame 생성 통일 | 다섯 pad body·표면점 선정법 기술 | 모든 손가락에 동일한 bounds 중점/max-z 원점, pad 축·identity 로컬 회전, rigid transform·quaternion 규칙, 공통 함수와 배치 계산을 명시. body 이름·bounds 데이터만 다름 |
| Collection10초 미만·권장5초 이하 | reset 비용 측정만 요구, 성능 완료 기준 없음 | 2048환경×rollout36step에서 iteration0부터 연속32회 모두10초 미만, 권장 모두5초 이하. 자동reset·OBB 산출·정책 추론 포함, 전체 iteration 시간과 learning time은 별도 보고 |

명세 도입부·가시성 정의·필터 선택 기준·reference 비교·손끝 Frame·reset 계산·성능 절·검증 표를 함께 수정했다. 기존의 “2cm·20%를 반드시 유지” 및 “필터 변경 후에도 전체 채택 집합이 reference와 같아야 함”이라는 제약이 남지 않도록 대조했다. 새로운 필터 문턱 자체는 아직 선택하지 않았으며, 같은 장면 bank에서 인정 수준과 비용을 비교해 구현 시 기록하도록 했다. 기존 가림 기하·초기 관측 고정·보상 추적·관측 차원·reward 수식·가중치·종료 계약은 보존했다.

성능 기준은 현재 `CurriculumOnPolicyRunner`가 `num_steps_per_env`로 rollout 경계를 전달하는 구조와 기준 계열의 [collection 성능 검증 기록](2026-11-19_sweep_only_ik_performance.md)을 확인해 정의했다. 해당 과거 측정값을 새 환경이나 현재 Single Contact v0의 실측 성능으로 인용하지 않았다. 동일 장비에서 두 환경을 직접 비교하도록 명시했다.

성능상 정상 timeout·부분reset·fallback까지 포함하고, 평균만으로 통과하거나 환경 수/rollout/물리 검사 축소로 시간을 맞추지 못하도록 했다. GPU 비동기 timing·반올림 경계·profiling overhead·초기화와 collection 구간 차이도 구분했다. 구현이 없으므로 현재 성능 달성 여부는 미검증이다.

검증 결과: 변경 문서3개 수식 형식 통과, 명세·로그 내부4개 및 workspace 외부14개 링크 오류0, 인계 내부187개 링크 오류0. 두 저장소 `git diff --check`와 신규 문서 줄 끝 공백 검사를 통과했다. `git diff --exit-code -- src/inspire_sweep_baseline src/observed_obb`도0으로 종료했다. Python 환경 코드·Gym 등록·자산·학습 로그는 수정하지 않았다. 실제 성능 benchmark·GPU·학습은 실행하지 않았다.
