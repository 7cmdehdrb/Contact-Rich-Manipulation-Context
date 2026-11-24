# Prof Revision 종료 사건 비용 추가 후 학습 행동 변화 진단

## 요청·의도

사용자는 TEMP/2026-11-24에 추가한 v0_1·v1의 학습 로그와 실제 실행 결과를 함께 보고, 특히 기존 팔 속도 종료에 사건 비용을 추가한 것만으로 왜 밀기를 하지 못하는지 분석하도록 요청했다. v1의 추가 손 자세 규칙도 분리해서 확인한다. 이번 작업은 진단·보고서 작성이며 환경 수정·학습 요청이 아니다.

## 시작 상태와 보존

루트 기준 commit은 `8ce37bfbfc7df5e85608f7c46f5b62d032e6869a`, 문서 저장소는 `cc69933d013a0a050aa360e2b984cae9ada05337`이다. 이전 Zone 분석 문서2개와 자산 폴더가 미추적 상태였고 그대로 보존했다. IsaacLab의 기존 미추적 `2.7.0+cu128`도 보존했다. 이번에 기존 환경·보상·제어·등록·PPO·서브모듈 commit을 변경하지 않는다. 학습 로그와 checkpoint는 읽기만 하며 `logs/rsl_rl` 정리·이동을 하지 않는다.

## 변경 전후와 실제 범위

이전 분석은 v0 model6100과 Reach5cm model7950이었다. 새 로그는 v0_1의2026-11-24_18-45-33/model1750, v1의2026-11-24_14-22-20/model6600이다. 네 run의 학습 scalar를 전부 추출하고 초기0~99·100~499·901~1000·1651~1750·최신100개 iteration 구간을 대조했다. `Episode_Reward`는 최대 episode 길이10초로 나눈 값이라10을 곱해 누적 규모로 복원했다. logger 기록 평균과 원시 episode 확률을 혼동하지 않았다.

`outputs/prof_revision_penalty_diagnosis_20261124/`에 기존 계측기의 별도 복사본을 두고 팔 속도·joint 이름·저장된 Gaussian action 표본추출 옵션을 추가했다. 활성 패키지를 수정하지 않았고 원래 RewardManager/물리 sample의 값을 자동 reset 전에 복사했다. 원래 함수는 한 번만 호출하며 추가 관측 noise나 보상을 재계산하지 않았다. 분석기의 numpy 계산은 저장 데이터에 대해서만 수행했다.

실제 재생은 RTX4070·env_isaaclab Python·headless에서 다음과 같다.

| 목적 | 실행 | episode |
| --- | --- | ---: |
| 새 최신 mean 정책 | v0_1·v1,각 seed42·43,256환경 | 1,024 |
| 동일 model1000 대조 | v0·v0_1·v1,각 seed42·43,128환경 | 768 |
| 저장 action 분포 sample | 최신 v0·v0_1·v1,seed42,128환경 | 384 |
| 같은 v0 정책/새 환경 | v0 model6100→v0_1,seed42,256환경 | 256 |
| 재사용 대조군 | 이전 v0 model6100,seed42·43,256환경 | 512 |

새 실행14회·2,432episode는 모두 process exit0·metadata complete·각 환경 첫 terminal1회로 완료했다. 이전512회를 합쳐 총2,944회지만 cohort별로 나누며 하나의 성공률로 합치지 않는다. metadata의 첫 episode만 분석하고 Joint Termination을 평가 종료로 유지한다. 목표 도달은 종료 시 XY 거리≤3cm다.

문서 저장소에 [진단 보고서](../experiments/2026-11-24_prof_revision_penalty_diagnosis.md), [검증·CSV·그림 자산](../../03_assets/prof_revision_penalty_diagnosis_2026-11-24/)을 추가한다. 앞선 Zone 보고서는 수정하지 않는다.

## 최종 대조와 핵심 결과

학습 env.yaml 전체와 agent.yaml 비교에서 v0_1은 기존−3 사건 항 추가 외 의미 있는 차이가 없고 v1은 그 항과 Formation 모드/weight 변경만 다르다. 다른 차이는 학습 PC별 USD 절대 경로·log_dir·PPO experiment_name이다. 재생 때 환경 수·seed·출력·자산 경로·PhysX aggregate-pair capacity2²⁵→2²¹만 override했다. 같은 환경 수·seed의 초기 타겟·OBB·목표·로봇·방향 해시는 모든 비교에서 일치했다.

- 최신 목표 도달: v0 447/512, v0_1 19/512, v1 202/512. 평균 순거리 감소7.44→0.53·3.93cm, 평균 episode 길이1.33→9.45·9.69초다.
- v0_1은447회 접촉했지만 수평 접촉력1N이 한 번이라도 발생한 경우86회뿐이다. 접근은 하지만 실제 밀기 힘으로 전환하지 않는 행동이 주 병목이다.
- 같은 model1000에서도 도달196/256→14/256·61/256으로 갈린다. 단순히 v0_1의 최신 iteration이 짧다는 설명만으로 전체 차이가 설명되지 않는다. 더 긴 v0_1 학습의 회복 여부는 미검증이다.
- v0 model6100을 v0_1에 넣은256회는 이전 v0 seed42와 타겟·action·힘·관절 속도·Reach 거리의 최대 차이0,초기 해시 동일,terminal flag 동일,보상 차이 대조 오차0이다. 도달224/256회도 같다. reward 항이 실행 중 물리를 직접 바꾸는 설명은 배제할 근거가 강하다.
- 실제 v0 궤적을 공통 v0_1 보상으로 재평가해도 평균 return5.145·γ0.98 할인합2.023으로 v0_1의−0.013·0.434보다 높다. 페널티가 있는 모든 좋은 밀기가 전역적으로 손해라는 설명은 반증된다. 유한 궤적 물리 보상 할인합이며 PPO timeout critic bootstrap은 포함하지 않았다.
- v1은 종료 시 Tip–OBB 거리 합이 v0_1 35.34→15.25cm로 작아졌지만 Zone3 목표0/80·Zone4 7/174,유효 힘 각도148.2°·128.4°다. 같은 Zone의 Hand9.20·9.29는 다른 Zone과 비슷하다. 수식 오류가 아니라 자세와 목표 방향의 분리다.
- v1 Hand는 raw 최대1→5·weight1.5배로 최대 가중 rate가7.5배다. 미할인 누적 Hand가 Sweep보다 크지만 할인 시 Hand0.443<Sweep1.108이므로 단순 누적 크기만으로 PPO 목표의 우선순위를 단정하지 않았다.
- 실제 action std·loss·actor 파라미터가 유한하며,팔 std는 새 모델에서 더 크다. std 붕괴 설명을 배제하고 mean 제어·힘 형성·시간 체류와 구분했다.

가장 지지되는 설명은 초반부터 종료 회피와 긴 생존 쪽으로 학습 경로가 이동했고, v1에서는 크고 지속적인 자세 보상이 목표 미완수 상태에서도 대안을 제공했다는 것이다. 여러 훈련 seed의 처음부터 재학습·warm start·보상 curriculum ablation은 하지 않아 학습 인과 자체를 확정하지 않는다.

## 검증·오류 수정·미검증

원래 RewardManager 합계와 실제 항별 합,종료 boolean과 실제 팔 속도>1rad/s,최근3step 중2접촉 Gate를 대조했다. numpy로 Reach·Sweep·Retreat·기존/새 Hand의 기하·normal·weight·dt·사건 비용을 독립 재계산했다. 원본 event·모든 checkpoint·학습 설정·활성 소스의 전후 해시가 같았다. 상세 오차는 자산의 validation.json에 있다.

새 시뮬레이션 실패는 없었다. 중간 분석을 실행 중인 폴더까지 읽어 metadata 미생성 오류가 난 뒤, 완료 metadata가 있는 폴더만 읽도록 수정했다. 최종 검증에서는 별도로14회 전체 완료를 assert한다. 또 CSV에서 v0에 존재하지 않는 사건 항이 빈 칸으로 저장되어 그림의 float 변환이 실패한 문제는 해당 미존재 보상항을0으로 처리해 해결했다. 실제 결측인 생존 구간·힘 각도는0으로 채우지 않았다.

보고서는 raw 문자열로 작성해 수식을 보존했다. 그림은 실제 계측·로그에서 matplotlib로 생성하고,축 단위와 sample 모집단을 표시했다. 시간 곡선은 생존한 초기 episode만 평균하며 남은 표본 수를 CSV로 제공한다. 그림의 접촉·힘·진행·목표 열은 같은 초기 모집단의 사건 검사이며 인과 funnel로 제시하지 않았다.

PPO의 timeout/GAE 해석은 현재 설치된 RSL source를 직접 읽고 snapshot·버전·해시를 보존했다. `is_finite_horizon=false`의 timeout bootstrap과 일반 속도 terminal을 구분했다. 이는 기존 환경에도 공통인 설정이며 학습 노출 경로가 달라진 보조 설명이다. 원격 학습 PC의 정확한 라이브러리 설치본과 byte 동일성은 검증하지 못했다.

GPU 재학습·checkpoint 수정·정지 유지 성능 개선·제안한 보상 변경 효과·실물 조작은 미검증이다. 다음 실험 제안은 보고서에만 기록하고 실행하지 않는다. 로그·checkpoint·활성 코드·이전 보고서를 보존했다. 이번 결과에 대한 git commit·push는 수행하지 않았다.

## 최종 검증 결과

- 신규14회 metadata·exit 파일과2,432회 terminal을 대조했고, 기존512회를 포함한 CSV2,944행·10cohort의 수·Zone별 목표 도달 수·가중 return을 재대조했다.
- 독립 보상 오차 최대:Reach2.98e−7·Sweep3.58e−7·Retreat2.24e−8·Hand1.31e−8·사건 비용0. 총합 오차2.39e−7 이하,팔 속도 flag/접촉 이력 Gate 불일치0개,접촉 sample 유효율100%다.
- 원본380개 파일 SHA256 불변. 작업 Python5개와 설치 PPO snapshot1개 AST 통과,새 report의 제어문자·수식2개·trailing whitespace 대조 통과. JSON에 NaN을 넣지 않았고, 실제 결측은 CSV/내부 요약에서 구분했다.
- 변경 Markdown2개 수식 검사 통과. 전체 문서673개 링크 검사 오류0개(internal5,699개),새 문서2개 외부 workspace 포함 검사 오류0개(internal23·external9개). 루트·문서 저장소 diff 공백 검사와 새 Markdown 별도 공백 대조를 수행했다.
- 그림6개를 실제로 열어 확인했다. 기전 그림의 긴x축 라벨은 짧은 두 줄 표기로 바꿔 잘림을 수정하고 최종 그림을 재확인했다. 시간 그래프는 생존 표본의 평균이라는 한계를 본문에 유지했다.
- 자산의 `analysis_sources.json`에 최종 스크립트 해시를 보존했다. 보고서는 종료 페널티의 물리 영향·계산 오류와 학습 경로·지속 자세 보상 문제를 구분한다. 실제로 수익이 더 높은 기존 밀기 궤적이 남아 있으므로 전역 최적해나 불가피한 보상 손해로 설명하지 않았다.

## 재현·인계

보고서에 정확한 입력 run·모델·명령과 분석 순서를 적었다. 기본 실행기는 `outputs/prof_revision_penalty_diagnosis_20261124/collect.py`이고 표본추출은 `--stochastic`이다. 학습 scalar 추출·해시 기록은 `read_training.py`, 원시 분석은 `analyze.py`, 공통 목표·할인·std·그림은 `mechanisms.py`, 보고서는 `report.py`다. 같은 폴더의 원시 NPZ·metadata·콘솔·exit 파일을 함께 보존한다. 재실행은 기존 폴더를 덮어쓰지 않고 새 이름을 지정한다.
