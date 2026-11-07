# Relative v0·v2·v3 학습 로그 분석

2026-11-07. 사용자 요청은 `logs/TEMP/relative`의 환경 구성·학습 성능·중단 원인 분석이다. 사용자는 최초 v0/v2 중단·v3 진행 중이라고 정정했고, 분석 중 v3도 중단됐다고 추가 보고했다. 환경·보상·학습 설정은 수정하지 않았다.

## 결론과 증거 수준

- **v0 최신 실행과 v2의 직접 중단 원인은 확인됨**: `NumericalPPO.update()`가 value loss 상한 1,000,000 초과를 감지하여 `NumericalTrainingError`를 발생시켰다. 제공된 `curriculum_runner.py:72`는 상위 `learn()`을 호출하는 전파 지점이다.
- 저장 rollout과 업데이트 직전 정책을 CPU에서 재생했다. 큰 F/T 입력에서 정책 평균 출력이 수천~수만으로 커지고, 상한 없는 raw Arm action 변화량의 제곱 페널티가 큰 음수 보상과 return을 만들었다. 업데이트 이전 value/return의 평균 제곱 오차부터 이미 상한을 넘는다.
- 덤프 전체의 tensor에서 NaN/Inf는 발견하지 못했다. 정상 범위를 벗어난 **유한값** 문제이며, 탐색 잡음만으로 설명되지 않는다.
- **v3의 새 중단 원인은 미확정**: 사용자 보고는 반영했으나 현재 복사본은 iteration 6571까지만 있고 failure 덤프가 없다. 기존 로그에는 큰 value loss 및 action-rate 페널티 급증이 있어 동일 경로의 위험이 관찰된다.
- 성능은 v2가 동일 학습 구간에서 성공 지표가 높다. v3는 더 오래 학습하면서 목표까지의 평균 거리가 작아졌지만 정지 유지 성공은 약 11%이며 timeout이 약 86%다. v3 총보상은 거리 weight 변경 때문에 직접 비교 지표로 쓰면 안 된다.

## 자료와 분석 방법

입력은 각 실행의 `params/env.yaml`, `params/agent.yaml`, TensorBoard event, git 기록, 두 failure JSON/PT, 마지막 저장 checkpoint다. 현재 workspace HEAD와 23시 세 실행의 기록된 commit은 `eb95e4281a0188cb12d7fcf42072df1984fa25ac`이다. 실행 환경별 설치 라이브러리·GPU·USD 내용의 완전 동일성은 검증하지 않았다.

재현 자료:

- [스칼라 집계 및 실제 보상 함수 재생 스크립트](../../../../outputs/relative_analysis_2026-11-07/analyze.py)
- [저장 정책 입력 재생 스크립트](../../../../outputs/relative_analysis_2026-11-07/replay.py)
- [전체 스칼라 CSV](../../../../outputs/relative_analysis_2026-11-07/scalars.csv)
- [집계·실패 샘플 JSON](../../../../outputs/relative_analysis_2026-11-07/summary.json)
- [설정 차이 JSON](../../../../outputs/relative_analysis_2026-11-07/config_diffs.json)
- [정책 재생 및 F/T 제거 비교](../../../../outputs/relative_analysis_2026-11-07/replay.json)

TensorBoard의 scalar reservoir를 0으로 지정하여 모든 기록을 읽었다. 아래 마지막 구간은 각 실행 마지막 100개 iteration의 **로그 값 산술평균**이다. 실패 iteration의 PPO update는 반환하지 않으므로 그 iteration의 loss가 TensorBoard에 기록되지 않을 수 있다. failure 파일을 별도로 확인해야 한다.

중요한 지표 해석:

- `Episode_Termination/*`: 현재 로컬 IsaacLab 코드에서는 각 병렬 환경의 마지막 종료 원인을 평균한 뒤 runner에서 집계한다. 아래 성공/timeout은 이 **로그 지표**이며, 전체 종료 episode를 직접 세어 산출한 독립 평가 성공률이 아니다. 원격 실행의 IsaacLab 구현 동일성은 미검증이다.
- `Metrics/target_goal_distance_xy_mean`: 종료된 episode들의 **진행 중 시간 평균 거리**를 집계한 값이다. 최종 거리 오차가 아니다.
- `Metrics/max_force`: episode별 최대 힘을 평균한 값이다. 모든 sample 중 최대 힘이 아니다.
- `Episode_Reward/*`: 가중치와 dt가 적용된 episode 합을 최대 episode 시간 10초로 나눈 로그다. `Train/mean_reward`와 집계 방식이 다르다.
- 단일 seed 42, 서로 다른 실행 장비 및 학습 길이이므로 버전 변경의 인과 효과나 통계적 우위를 확정하지 않는다.

## 실행 식별

| 환경 / 실행 시작 폴더 | 마지막 event iteration | 마지막 checkpoint | event 시간 차이 | 중단 증거 |
| --- | ---: | ---: | ---: | --- |
| v0 / 20-02-36 | 2319 | 2300 | 2.84시간 | failure 파일 없음, 종료 원인 미상 |
| v0 / 23-01-49 | 1544 | 1500 | 1.85시간 | iteration 1545, value loss 1,783,097.3164 |
| v2 / 23-02-03 | 1636 | 1600 | 2.65시간 | iteration 1637, value loss 1,501,288.7344 |
| v3 / 23-02-27 | 6571 | 6550 | 14.90시간 | 사용자 중단 보고, 복사본에 failure 없음 |

모든 시작 폴더의 날짜는 2026-11-06이다. 시간 차이는 첫 event와 마지막 event의 wall time 차이로, 초기화 시간을 포함한 실제 총 실행시간은 아니다. iteration은 0부터 시작한다. v0의 두 실행은 모두 `resume: false`이며 합쳐서 연속 학습으로 취급하지 않았다.

## 저장된 환경 구성 비교

23시 세 실행의 공통 설정은 2048환경, rollout 36step, control dt 0.02초, episode 10초/500step, seed42다. 한 iteration은 73,728 transition이다. PPO는 8epoch×4 minibatch, gamma0.98, lambda0.95, 초기 learning rate0.001/adaptive, entropy0.005, gradient norm1.0이다. Actor/Critic observation normalization은 false이고 `clip_actions: null`이다.

관측은 직접58D, 장애물64D를 별도 encoder64→32→16으로 압축하여 본체 MLP에74D를 전달한다. 본체는256→128→64/ELU이며 Actor/Critic은 독립 모델이다. EEF pose는 base 기준이고 초기 타겟·장애물 snapshot은 현재 EEF 기준으로 변환한다.

| 항목 | v0 최신 | v2 | v3 |
| --- | --- | --- | --- |
| Actor 타겟 | 초기 위치 | 초기 위치 | 초기 위치 |
| Critic 타겟 | 초기 위치 | 현재 위치 | 초기 위치 |
| 별도 접촉 유지 보상 | weight0.1 | 동일 | 삭제 |
| 거리 보상 | 누적 변위 cosine, weight5 | 동일 | 현재 접촉 gate + 동일 cosine, weight25 |
| raw action-rate | 상한 없는 Arm 제곱 변화량 | 동일 | 동일 |

세 환경 공통 Axia 질량은0.280kg, Arm 물리 속도3.14rad/s, effort150/150/150/28/28/28Nm, 종료 속도 임계값4rad/s다. 10,000iteration 이전이므로 목표 방향 deadzone30°와 종료 속도4rad/s가 유지됐다. **이번 중단을 10k 이후 커리큘럼 전환으로 설명할 수 없다.**

20시 v0는 별도 조건이다. 저장 YAML의 Axia 질량은 **0.001kg**, 물리 속도는 proximal2/wrist4rad/s, 속도 종료 임계값3rad/s이며 속도 커리큘럼이 없다. 현재 문서의 질량을 소급 적용하지 않는다. 오래된 v0에서 속도 종료가 매우 높은 결과를 23시 버전과 동일 조건의 차이로 해석하면 안 된다.

## 학습 성능

마지막100개 로그 평균:

| 지표 | v0 20시 참고 | v0 최신 | v2 | v3 복사본 |
| --- | ---: | ---: | ---: | ---: |
| Train 평균 보상 | 13.27 | -47.09 | 24.80 | 117.15 |
| 성공 종료 지표 | 2.40% | 3.50% | 10.22% | 10.96% |
| timeout 지표 | 22.24% | 86.74% | 82.30% | 85.98% |
| Arm 속도 종료 지표 | 74.75% | 0.060% | 0.144% | 0.019% |
| 낙하·기울어짐 종료 | 0.60% | 2.72% | 6.17% | 2.98% |
| 선반 종료 | 0.037% | 7.05% | 1.19% | 0.11% |
| episode 평균 길이, step | 143.17 | 451.45 | 447.41 | 461.73 |
| 시간 평균 목표 거리 | 8.25cm | 9.10cm | 9.05cm | 6.14cm |
| value loss | 33.68 | 22,416.82 | 27.81 | 106.50 |
| raw action-rate 보상 로그 | -0.424 | -6.322 | -1.229 | -0.632 |

같은 iteration1400–1499에서 성공 지표는 v0 **3.17%**, v2 **8.32%**, v3 **1.31%**다. 평균 보상은 각각-36.89/19.18/100.69로, v3의 보상 증가가 성공 증가와 같은 의미가 아님을 보여준다. 이 구간에서 v2는 v0 대비 현재 타겟을 보는 Critic이 유리할 가능성을 지지하지만, 반복 seed 검증은 없다.

v0 최신은 action-rate 페널티가400–499의-0.687에서1400–1499의-5.173으로 커지고, value loss도7.46→21,623.86으로 악화됐다. 점진적인 불안정 뒤 최종 큰 이상치가 발생했다.

v2는 마지막 정상 iteration의 value loss가3.83이고 마지막100 평균27.81이었지만 바로 다음 iteration에서150만으로 중단됐다. 평균 곡선만으로 드문 큰 sample 위험을 배제할 수 없다.

v3는 성공 지표가1400–1499의1.31%에서5900–5999의11.31%로 증가했다. 그러나 마지막 구간의 timeout85.98%, 목표 시간 평균 거리6.14cm, 목표 물체 평균 속도0.01024m/s를 보면 정밀 정지 유지가 아직 부족하다. 성공 계약은 **XY 거리3cm 이내·물체 속도0.005m/s 이하를 연속3초**다. 평균 속도만으로 개별 실패 원인을 판정할 수는 없지만, 단순 접근과 이 성공 조건은 구분해야 한다.

v3는 이미 iteration4078에서 value loss670,373, iteration4187에서722,091을 기록했다. action-rate 보상 로그는4078에서-94.84까지 떨어졌고, Train 보상은2571에서-491.64였다. 이후 회복했더라도 수치 안정성이 확보됐다는 뜻은 아니다. 새 중단이 같은 원인인지는 새 failure/traceback 확인이 필요하다.

## 실패 경로 재생

현재 구현의 실제 `policy_action_rate_penalty()` 함수 AST를 추출하여 **저장 action**에 실행했다. 이웃 step 사이에 reset이 없는 sample만 이전 action을 재구성했다. rollout의 첫 step은 이전 action이 없으므로 해당 비교에서 제외했다. 가중치-1과 dt0.02를 적용한다.

```math
r_{rate}=-0.02\times0.03\left(\sum_{i=1}^{6}(a_{t,i}-a_{t-1,i})^2+\sum_{j=7}^{8}(\mathrm{clip}(a_{t,j},0,1)-\mathrm{clip}(a_{t-1,j},0,1))^2\right)
```

| 증거 | v0 최신 | v2 |
| --- | ---: | ---: |
| 최악 sample, rollout step/env | 4 / 1439 | 19 / 1732 |
| 저장된 reward | -185,702.83 | -62,790.58 |
| 재생한 action-rate 기여 | -185,699.78 | -62,790.54 |
| rollout 최소 return | -185,702.83 | -122,887.55 |
| 업데이트 전 value/return MSE | 1,783,101.38 | 1,501,295.25 |
| 덤프의 실패 value loss | 1,783,097.32 | 1,501,288.73 |
| reward가-1000 미만인 sample | 4 / 73,728 | 4 / 73,728 |
| 위 sample이 발생한 env 수 | 3 / 2048 | 1 / 2048 |
| 최대 기여 env의 전체 squared error 비중 | 99.493% | 99.9997% |

별도로 실제 `WrenchRefactorRelativeModel` / `WrenchRefactorRelativeV2Model`에 업데이트 직전 state dict를 로드하여 저장 관측을 입력했다. 체크포인트에는 정상적인 유한 weight와 양수 std가 있고, 덤프 전체 tensor에도 NaN/Inf가 없다.

| 최악 sample 정책 재생 | v0 최신 | v2 |
| --- | ---: | ---: |
| F/T force 최대 성분 절댓값 | 1,319.19N | 691.44N |
| 재생된 Arm 평균 최대 절댓값 | 11,981.53 | 7,403.10 |
| F/T 6채널만0으로 바꾼 Arm 평균 최대 절댓값 | 9.17 | 3.02 |
| Arm6축 std 범위 | 1.91–2.32 | 1.69–2.06 |

실제 sampled action과 재생 정책 평균의 차이는 해당 std에 비해 통상적인 범위다. 최악 sample의 최대 절댓값 z-score는 약2.11/1.40이다. **수천 단위 action은 높은 Gaussian 잡음의 우연한 꼬리값이 아니라 정책 평균에서 이미 발생한다.**

F/T 제거는 원인 분리를 위한 offline 개입이다. F/T 센서를 제거하거나 학습 중 값을0으로 만들라는 제안이 아니다. 이 replay는 정책이 큰 F/T 입력에 매우 민감함을 확인한다. 그 F/T가 실제 충돌·센서 보정·접촉 solver·reset 과정 중 무엇에서 발생했는지는 덤프에 물리 내부 상태와 접촉별 기록이 없어 확정할 수 없다.

확인된 경로는 **큰 F/T 입력 → 큰 raw 정책 평균 → 큰 Arm action 변화 → 상한 없는 제곱 페널티 → 큰 음수 return → value loss 상한 초과**다. 최종 effort saturation은 존재하지만 보상은 raw action을 사용하므로 이 경로를 막지 않는다. 관측의 previous action은 tanh로 제한되지만 실제 raw action과 해당 비용은 제한되지 않는다.

정책 재생의 `catastrophic_actor_check`는 두 덤프 모두 `FAIL: captured actor mean exceeds 1000`을 출력했다. 진단용1000 기준은 runtime의1e6 보호 상한과 별도이며, 실제 물리 시뮬레이션 crash 전체 재현 또는 수정 검증으로 간주하지 않는다.

## 별도의 Hand 분포 문제

저장된 std는 다음과 같다. `Policy/mean_std` 하나만 보면 Arm 탐색까지 크게 증가한 것으로 오해할 수 있다.

| 시점 | Arm6축 std | Hand2축 std |
| --- | --- | --- |
| v0 최신 실패 직전 | 1.91–2.32 | 16.06 / 16.23 |
| v2 실패 직전 | 1.69–2.06 | 37.89 / 42.33 |
| v3 checkpoint6550 | 0.18–1.17 | 40.29 / 73.03 |

Hand는 실행 및 action-rate 계산에서[0,1]로 clamp하지만 정책 분포는 raw Gaussian이며 entropy 보상이 있다. 실제 동작은 포화된 채 raw 분포의 entropy가 커지는 학습 유인이 있을 가능성이 있다. 이는 설정과 checkpoint에 근거한 해석이며, 이 유인이 std 증가의 유일한 원인인지는 미검증이다. Arm의 이번 실패를 Hand std 증가 하나로 설명하지 않는다.

## 다음 수정·검증의 우선순위

이번 요청에서는 아래 사항을 적용하지 않았다.

1. v3의 최신 `numerical_failure.json/.pt` 또는 traceback 마지막 예외를 확보하여 동일 failure인지 확정한다.
2. F/T의 단위별 scaling/normalization과 물리적 이상치 진단을 우선 설계한다. 입력 전체가 normalization=false인 상태에서 F/T만 큰 수치 범위를 차지한다. 임의의 cutoff로 데이터를 삭제하기 전에 접촉·보정 원인을 구분한다.
3. Arm action의 유효 범위와 raw action-rate 목적을 함께 검토한다. 실제 bounded 명령에 대한 변화량 비용, robust loss 또는 명시적인 포화 등은 목적함수를 바꾸므로 사용자 의도에 맞춰 하나씩 검증한다. 단순히 value loss 상한을 올리거나 보호 기능을 끄면 큰 return을 그대로 학습하게 된다.
4. Hand bounded action과 Gaussian entropy/std의 관계를 별도로 수정·검증한다. 축별 std와 saturation 비율을 분리 계측하면 평균 std의 오해를 줄일 수 있다.
5. 수치 경로를 해결한 뒤 같은 rollout 예산과 여러 seed로 v0/v2/v3를 비교한다. 현재 자료는 v2의 초기 성공 성능, v3의 접근 성능을 각각 지지한다. 보상 합계보다 도달·정지 유지·최종 오차·실패 이유를 분리 평가한다.

현재 중단은 학습률을 낮추기 전부터 rollout target의 MSE가 이미 매우 큰 사례다. learning rate 조정만으로 원인이 해결됐다고 판단하면 안 된다. 기존 checkpoint는 보존했으며 동일 설정으로 resume한 결과는 검증하지 않았다.

## 변경·검증 기록

- 변경 전: 입력 로그와 현재 환경 코드가 존재하며 분석 산출물 없음.
- 변경 후: 본 개발 기록 및 `outputs/relative_analysis_2026-11-07`의 분석 스크립트·CSV·JSON만 추가. 환경 함수·수치·일정·학습 로그는 그대로 유지했다.
- 원본의 상대적인 위치를 유지하여 파일을 읽었고 pickle은 PyTorch `weights_only=True`로 로드했다. 다른 서브모듈의 기존 변경을 보존했다.
- 실행 명령은 workspace 루트에서 아래와 같다. 기존 `env_isaaclab` Python의 torch/tensorboard를 사용했으며 추가 package 설치는 없었다.

```powershell
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' outputs/relative_analysis_2026-11-07/analyze.py
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' outputs/relative_analysis_2026-11-07/replay.py
```

- 수행: 네 event의 전체 scalar 집계, 설정 전개 결과 차이, 두 failure tensor의 finite 검사, 실제 reward 함수 재생, 실제 정책 CPU forward 및 F/T 제거 대조, 마지막 checkpoint의 축별 std 확인.
- 미수행: Isaac Sim/PhysX rollout 재현, 학습 재시작, 실제 제어 안전성 평가, 원격 서버 상태 확인, v3 신규 crash 판정, 여러 seed 평가, 원격 설치 버전 일치 검증.
- 최종 검증: `check_markdown_math.py` 변경1문서 통과, `check_document_links.py --check-external` 변경문서 외부6링크 오류0, 전체 문서511개 링크 검사 오류0, workspace 및 문서 저장소 `git diff --check` 통과. 문서 렌더링은 별도 확인하지 않았다.
- 전체 scalar486,136개에서 nonfinite0. 두 failure 덤프 전체 tensor에서도 nonfinite0. v3 event 파일 크기는 최종 재확인 시17,958,962byte로 동일하며 failure 파일은 여전히 없었다.
