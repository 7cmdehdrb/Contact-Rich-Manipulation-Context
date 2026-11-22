# 2026-11-22 wr1122 학습 중단 원인 진단

## 요청과 작업 범위

사용자는 `logs/TEMP/wr1122`의 강제 종료된 세 학습에 대해 로그·체크포인트를 조사하고 원인과 해결 방안을 제시하되, 수정을 시작하지 않도록 요청했다. GPU 사용은 허용했다. 환경·보상·PPO·IsaacLab 소스, 학습 로그, 체크포인트는 수정하지 않았다. 이 진단 기록과 별도 `outputs/wr1122_diagnosis` 분석 산출물만 추가했다. 학습 재시작·추가 학습·물리 시뮬레이터 실행은 하지 않았다.

## 결론

세 실행의 직접 원인은 **큰 정책 원본 action → 상한 없는 action 변화량/범위 초과 제곱 비용 → 큰 음의 reward → GAE return → value MSE 1e6 초과**이다. NaN/Inf 발생이 아니라, 유한한 value loss가 명시적 안전 상한을 넘어서 `NumericalTrainingError`가 발생했다.

방아쇠는 같지 않다. Single Contact v0는 제한된 F/T 입력에도 이미 큰 이득을 가진 정책이 극단 출력을 냈다. Sweep v0와 Single Contact v1은 작은 F/T 입력에서도 이전 action 관측을 거쳐 출력이 증폭됐다. **입력 제한은 정책 출력이나 보상 비용의 상한을 보장하지 않는다.** 특히 v1 실패 배치 전체의 F/T 관측 최대 절댓값은 0.087552로, F/T 입력 제한이 뚫린 사례가 아니다.

## 자료와 재생 방법

| 환경/실행 | 실패 iteration | 기록된 value loss | 원본 action 최대 절댓값 | 저장 reward 최솟값 | 저장 return 최솟값 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sweep v0 / 2026-11-20_20-46-02 | 27491 | 1116138.884766 | 4748.4453 | -26744.6602 | -89431.5078 |
| Single Contact v0 / 2026-11-20_20-56-01 | 29969 | 2409849.125000 | 7497.9370 | -158471.2188 | -158471.2188 |
| Single Contact v1 / 2026-11-21_19-05-47 | 7204 | 1775409.953125 | 5979.5659 | -74722.6328 | -74761.0391 |

각 실행의 `numerical_failure.pt/json`, TensorBoard 전체 scalar, `params/env.yaml`, `params/agent.yaml`, 초기·중간·최근 체크포인트 각 7개(총 21개)를 확인했다. 실패 dump에는 업데이트 직전/직후 모델과 Adam 상태, 36 step × 2048 환경의 관측·action·reward·done·value·return·advantage가 있다.

실제 `SweepOnlyModel`, `RolloutStorage`, `NumericalPPO.update()`를 CUDA에서 실행했다. 저장된 업데이트 전 actor로 누락된 old Normal distribution/log probability를 재구성하고, 저장 배치·optimizer·하이퍼파라미터를 복원했다. seed 42 재생을 두 번 실행해 같은 안전 중단을 확인했다. 물리 재현 대신 실제 실패 업데이트의 재생으로 원인 경계를 좁혔다.

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python outputs/wr1122_diagnosis/replay.py
/home/min/miniconda3/envs/env_isaaclab/bin/python outputs/wr1122_diagnosis/replay_cap100.py
```

위 명령은 workspace root에서 실행한다. 분석 산출물만 덮어쓰며 원본 로그에는 쓰지 않는다. 로컬 재생은 torch 2.7.0, rsl-rl-lib 5.0.1, tensordict 0.13.0, RTX3090을 사용했다. 저장 YAML의 `share_cnn_encoders`는 현재 설치된 PPO 생성자에 없는 항목이므로 전달하지 않았다. 현재 모델에는 CNN이 없다. 원 서버의 정확한 패키지 버전·minibatch 순서·GPU 연산 설정은 저장되지 않아 bitwise 재생은 아니다. 저장 value와 재평가 value의 최대 차이는 각각 Sweep v0 0.2232, Contact v0 0.3071, Contact v1 1.4063이다. 실패 MSE 규모와 결론에는 영향을 주지 않는다.

| 환경 | 업데이트 전 전체 배치 MSE | 실제 PPO 재생 value loss | 저장된 오류와 같은 중단 |
| --- | ---: | ---: | --- |
| Sweep v0 | 1116145.625 | 1116139.034180 | 재현 |
| Single Contact v0 | 2409857.000 | 2409849.110352 | 재현 |
| Single Contact v1 | 1775407.125 | 1775400.937500 | 재현 |

## 보상이 커진 경로

현재 정책은 출력 평균에 상한이 없는 일반 Gaussian이다. wrapper의 `clip_actions`는 null이며, arm/hand 실행 제한은 Action term 내부에서 수행한다. ActionManager의 원본 action과 이전 action은 제한 전 값으로 남는다. Last Action 관측만 전 채널 ±π/2로 제한한다.

- `mdp/reward_functions/sweep_simple.py:32`의 `finger_action_rate_l2`: 원본 action 차이의 제곱합. 상한 없음.
- `mdp/reward_functions/stabilize_sweep.py:42`의 `action_limit_excess`: 원본 action과 실행 제한값 사이 차이를 허용 폭으로 나눈 제곱평균. 상한 없음.
- 네 항 모두 weight -0.03, policy dt 0.02. 각 raw 비용에 -0.0006이 곱해진다.
- `mdp/observation_functions/stabilize_sweep.py:23`: Last Action만 clamp한다. 보상에 쓰이는 원본 action은 변경하지 않는다.
- F/T는 runtime의 ObservationManager에서 noise 후 clip, 그 다음 축별 scale을 적용한다. 물리 F/T reward 읽기는 별도이나 `WrenchMagnitudeChangePenalty` 자체 raw 비용은 [0,1]로 제한되므로 step당 최저 -0.002이다.

실제 함수 정의를 AST로 추출하여 저장 action으로 네 비용을 재계산했다. t=1..35에는 이전 action을 정확히 복원했고, 이전 step에 done이면 ActionManager 계약에 맞춰 0으로 reset했다. t=0의 제한 전 이전 action은 저장되지 않아 비용 분해 집계에서 제외했다.

| 환경, 최악 reward 샘플(t는 0부터) | Arm rate | Hand rate | Arm limit | Hand limit | 비용 합 외 나머지 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sweep v0, t22/env887 | -8926.8184 | -15734.0479 | -187.1300 | -1896.6801 | +0.0156 |
| Contact v0, t26/env1131 | -36780.4688 | -110841.6797 | -620.5361 | -10228.4678 | -0.0625 |
| Contact v1, t24/env1442 | -6994.9268 | -60762.6523 | -127.2196 | -6834.8354 | -3.0000 |

Contact v1의 나머지 -3은 arm joint failure 일회 비용과 일치한다. 세 최악 샘플의 큰 보상은 timeout bootstrapping이나 물리 F/T 비용 없이 action 비용으로 설명된다. 저장 reward에는 일부 timeout bootstrap이 포함되지만 timeout flags는 별도 저장되지 않았으므로 다른 샘플의 정확한 물리 reward 분해까지 주장하지 않는다.

오차도 소수 환경에 집중된다. Sweep v0와 Contact v0는 각 한 환경이 배치 squared error의 사실상 전부를 차지한다. Contact v1은 상위 5개 환경이 사실상 전부를 차지하며, 최악 한 환경은 약 30.44%이다.

## 방아쇠를 구분한 입력 제거 실험

업데이트 전 모델과 실제 저장 관측을 고정하고 특정 관측 그룹만 0으로 바꿔 정책 평균을 재평가했다. 이는 원인 경로를 구분하는 진단이며 관측 삭제를 해결안으로 적용한 것이 아니다.

### Single Contact v0: 제한 안의 F/T에도 큰 정책 이득

t26/env1131의 F/T 관측은 `[1.0, 0.650716, 0.094560, 0.000519, 0.028045, -0.064674]`이다. 제한 범위 [-1,1] 안이지만 실패 배치의 F/T 절댓값 중앙값 0.000346, 99.9%값 0.026654에 비하면 큰 입력이다.

- 원본 평균 최대 절댓값 7496.25 → F/T 6축만 0으로 바꾸면 3.28.
- 이전 action만 0으로 바꾸면 8525.14로 큰 출력이 남는다.
- std는 채널별 0.338~0.583이다. 큰 action은 Gaussian 꼬리 샘플이 아니라 평균에서 발생한다.
- 동일 실패 관측에 대한 체크포인트 평균 최대 절댓값은 model_0 0.213 → model_7500 286.24 → model_15000 953.05 → model_22500 4572.24 → model_29950 7797.11이다.

즉 F/T가 무제한으로 MLP에 들어간 것이 아니라, **제한된 드문 입력에 대한 모델 반응이 학습 중 커져 있었다.** 원 물리 F/T, 접촉력·상태는 dump에 없어 실제 큰 접촉인지 센서 이상인지는 구분할 수 없다.

### Single Contact v1: Last Action 입력을 통한 증폭

env1183의 t5→6→7 원본 action 최대 절댓값은 88.32→3569.77→5979.57이다. 세 step 모두 F/T 관측 최대 절댓값은 0.001 미만이다.

- t7 평균 5980.12 → F/T만 0으로 바꾸면 5979.85.
- t7 평균 5980.12 → 이전 action만 0으로 바꾸면 2.84; critic은 -11474.21→-2.17.
- 실패 배치 전체에서 이전 action만 0으로 바꾸면 평균 최대 절댓값 5980.12→9.36, |평균|>10 샘플 43→0, critic 최대 절댓값 11688.05→3.47.
- 실패 배치 전체 F/T 최대 절댓값도 0.087552이며 std는 0.734~1.454이다.

t5에서는 촉각 ch8=-1이 함께 존재한다. 촉각만 제거하면 평균 88.63→36.08이지만, 이전 action을 제거하면 2.45다. 촉각이 해당 출력을 키우는 데 기여했으나 이 비트가 실제 접촉인지 1% 관측 noise인지는 저장 자료로 구분할 수 없다. 이후 두 step에는 촉각이 모두 0인데도 증폭이 이어진다.

### Sweep v0: 작은 촉각 사건 이후 Last Action 경로

env887 t16은 tactile ch0=2, ch7=-1이며 action 최대 12.61이다. 촉각만 제거하면 평균 12.27→2.94, 이전 action을 제거하면 3.42다. t17에서 action 329.21, 이후 최대 4748.45까지 커진다. 이때 F/T 관측은 작다.

- t22 평균 4757.16 → F/T만 0이면 4753.98, 이전 action만 0이면 2.98.
- 전체 배치의 이전 action만 0이면 평균 최대 4757.16→3.91, |평균|>10 샘플 20→0.

전 채널 clamp된 Last Action도 포화 부호 조합이 모델의 큰 출력 영역을 자극할 수 있다. 이 경로는 단순한 raw 관측 크기 초과 검증으로 검출되지 않는다.

## 학습 이력과 체크포인트

| 환경 | 최초 기록 value loss >1000 | 해당 spike 횟수 | 최근 1000회 중 spike | 기록된 최대 loss |
| --- | ---: | ---: | ---: | ---: |
| Sweep v0 | 17712 | 46 | 3 | 737417.50 (22515) |
| Contact v0 | 6967 | 261 | 3 | 811172.94 (27325) |
| Contact v1 | 3044 | 499 | 374 | 759802.69 (7178) |

특히 v1은 한 번의 갑작스러운 고장이 아니다. 3044부터 큰 spike가 기록됐고 최근 1000 iteration 중 374회가 1000을 넘었다. 실패 직전에는 loss가 0.274로 작았지만 드문 실패 상태가 다음 배치에 등장하며 크게 뛰었다. 평균 scalar 하나가 정상처럼 보이는 순간에도 위험한 입력 영역은 남아 있다.

최근 체크포인트에도 같은 관측에 대한 극단 출력이 존재한다. Contact v1 model_7200은 실패 t7 관측에 평균 최대 5212.38, critic -11413.01을 출력한다. 실패 업데이트가 새로 만든 불안정성만으로 설명할 수 없다. 기존 checkpoint가 유한하다는 이유만으로 정상이라고 판단하거나 그대로 resume해서는 안 된다.

모든 dump의 rollout·최종 관측·업데이트 전후 모델/Adam·저장 gradient는 유한하다. 실패 배치 관측 전체 최대 절댓값도 2.3~2.8 수준이다. 마지막 저장 action과 재평가 정책 평균의 차이를 std로 나눈 값은 전체 배치 최대 약 4.71~5.44 범위로, 수천 action의 원인이 std 폭증이 아님을 확인했다.

## 단일 변수 개입: 비용 경로 차단

원본 파일은 그대로 두고, 메모리에서 네 action raw 비용 각각에 임의의 진단 상한 100을 적용했다. 그 reward 차이만 GAE를 따라 전파하고 advantage를 재정규화해 같은 실제 PPO 업데이트를 수행했다. t0 비용은 이전 action이 없어 원본을 유지했다. 모델·optimizer·관측·action·done·bootstrap·PPO 설정은 유지했다.

| 환경 | 원본 실제 PPO 재생 loss | 비용 상한 개입 후 loss | 안전 중단 여부 |
| --- | ---: | ---: | --- |
| Sweep v0 | 1116139.034 | 0.412 | 통과 |
| Contact v0 | 2409849.110 | 0.072 | 통과 |
| Contact v1 | 1775400.938 | 9647.402 | 통과하나 여전히 큼 |

이 실험은 **상한 없는 비용이 이번 중단 규모를 만든 경로**임을 검증한다. 100은 원인 분리용 숫자이며 최종 권장 하이퍼파라미터가 아니다. v1은 critic이 이미 극단 값을 출력하여 비용만 바꿔도 잔여 오차가 크다. 정책 평균의 불안정성도 그대로이므로 비용 상한만으로 장기 문제 해결을 선언할 수 없다.

추가로 기존 checkpoint에서 Last Action을 실제 손 실행 범위로 재해석하거나 tanh만 붙여도 보편적 해결은 되지 않았다. v1의 전체 배치 평균 최대값은 손 실행 범위 대체 후에도 4671.24, tanh 적용 후에도 2305.45였다. 관측 의미를 변경한다면 별도 학습·검증이 필요하다.

## 후속: OSC와 Hand 클립·비용 대조 및 손 출력이 커지는 이유

사용자 후속 요청에 따라 실행 클립, term 내부 raw buffer, ActionManager 원본, Last Action 관측, 비용 정규화, 초기 분포를 대조했다. 새 분석은 `outputs/wr1122_diagnosis/compare_arm_hand.py`로 수행했다. source·설정·원본 로그는 계속 보존했다.

| 항목 | OSC 6D | Hand 6D |
| --- | --- | --- |
| 정책/ActionManager 원본 | 일반 Gaussian, 출력 상한 없음 | 동일 |
| 실행 전 제한 | 전 6축 ±π/2 | 각 축 [0, URDF 상한], 상한 0.5864~1.4381 rad |
| 실제 제어 의미 | 제한값 ×0.03 m / ×0.15 rad, 상대 EEF pose | 제한값을 절대 손 구동각으로 사용, mimic 변환 |
| Action term 내부 raw buffer | 부모를 호출하기 전에 clamp하여 이미 제한됨 | 클립 전 값을 그대로 보관 |
| Last Action 관측 | 원본을 ±π/2로 clamp, 실행 전 제한값과 일치 | 원본을 ±π/2로 clamp, 실제 실행과 다름 |
| 변화량 비용 | 원본 6축 차이의 제곱합 ×-0.03×dt | 동일, 채널 폭 정규화 없음 |
| 범위 초과 비용 | mean((원본-제한값)/π)^2 ×-0.03×dt | mean((원본-제한값)/각 URDF 상한)^2 ×-0.03×dt |

term 내부 raw buffer에는 비대칭이 있지만, **두 비용 모두 term buffer가 아니라 ActionManager의 원본을 읽는다.** 따라서 OSC 비용만 클립 후 값으로 작아지고 손 비용만 원본으로 커지는 구현은 아니다. OSC 제한 후 최대 상대 이동 명령은 축별 약 0.04712 m, Euler 회전 명령 약 0.23562 rad이며, OSC의 ±π/2를 손 관절각과 같은 물리량으로 해석하면 안 된다.

먼저 손만 폭주한다는 전제는 실제 배치와 다르다.

| 실패 배치 | OSC 원본 최대 절댓값 | Hand 원본 최대 절댓값 | OSC 범위 밖 채널 비율 | Hand 범위 밖 채널 비율 |
| --- | ---: | ---: | ---: | ---: |
| Sweep v0 | 3458.90 | 4748.45 | 4.87% | 92.22% |
| Contact v0 | 7497.94 | 7271.32 | 6.20% | 89.73% |
| Contact v1 | 3270.81 | 5979.57 | 19.47% | 86.25% |

비율은 마지막 36×2048×6 채널의 집계이며 전체 학습 이력 비율은 아니다. 손의 하한 미만 비율은 각각 90.56%, 86.99%, 76.25%로, 대부분 음수 출력이 0으로 실행되는 경우다. 이 배치의 손 평균 출력도 다수 채널에서 음수로 치우쳐 있다.

### 가설 1: 손의 실행과 이력 관측 불일치가 증폭 경로를 만든다 — 기여 확인

OSC의 관측 이력을 실제 이전 실행 제한값과 대조하면 t1~35 최대 오차가 0이다. 손은 같은 비교에서 약 85.72~91.96%의 채널이 다르고 최대 차이는 1.5708이다. 예를 들어 -0.2와 -1.5는 모두 0 rad 손 목표로 실행되지만 Last Action에는 서로 다른 음수로 들어간다. 이는 실행되지 않은 명령의 차이가 다음 행동에 영향을 줄 수 있는 구조다.

- Sweep v0에서 손 이력 6개만 0으로 바꾸면 전체 배치 정책 평균 최대값 4757.16→5.52, |평균|>10 샘플 20→0. 팔 이력만 제거하면 최대값 912.09로 큰 출력이 남는다.
- Contact v1에서는 손 이력만 제거해도 최대값이 5980.12→1265.92로 낮아지지만 남는 극단 출력이 있다. 팔 이력만 제거하면 2212.61, 두 이력을 모두 제거하면 9.36이다. **v1은 팔·손 이력의 공동 작용**으로 해석해야 한다.
- Contact v1의 최초 큰 action 샘플 t5/env1183에서 손 이력만 제거하면 손 평균 최대 88.63→2.51, 팔 이력만 제거하면 3.44이다. 다른 샘플에는 한 그룹 제거로 출력이 오히려 증가하는 경우도 있으므로 단일 관측 수정만으로 안정성을 보장하지 않는다.
- Contact v0의 F/T-trigger 샘플은 이력 제거로 해소되지 않는다. 이 가설은 세 실행 전체의 유일한 원인이 아니다.

0 대체는 진단 개입이며 실행 의미를 정합화한 새 정책의 물리 재현은 아니다. 관측 불일치가 큰 출력을 학습하게 된 역사적 원인을 단독으로 입증한 것도 아니다.

### 가설 2: 같은 Gaussian 초기화가 손의 비대칭·좁은 범위에 맞지 않는다 — 구조와 현재 포화 확인, 역사적 인과는 추론

초기 std=1은 12채널에 동일하다. 평균이 0인 N(0,1)을 기준으로 계산하면 OSC의 ±1.5708 초과 확률은 11.62%지만 손의 [0,h] 이탈 확률은 채널별 57.52~77.88%다. 이는 이론적 기준값이며 실제 초기 state별 actor 평균을 0이라고 단정한 측정은 아니다.

손은 평균을 음수로 옮기면 여러 원본 값이 같은 완전 개방 목표 0으로 실행된다. 일정한 평균 offset 자체는 동일 상태·일정 std에서 기대 action 차이 제곱을 늘리지 않으며, 고정 명령의 정상 구간 변화량 비용은 0이다. 남는 범위 초과 비용의 예로 6개 손 출력을 모두 -1로 고정하면 실행은 모두 0이고, limit 비용은 한 step -0.000558, 500 step 누적 -0.279이다. -3이면 각각 -0.005022, -2.511이다. 초기/reset 변화량이나 확률적 noise 비용은 이 결정론적 예에 포함하지 않았다.

따라서 손을 펼쳐 유지하는 편익이 있는 상황이라면 음수 평균과 다량의 클립을 유지할 여지가 있다. 실제 데이터의 높은 음수 비율과 일치하는 설명이지만, 그 학습 선택의 정확한 원인은 전체 과거 rollout을 보유하지 않아 확정하지 않는다. 이렇게 학습된 원본 이력이 ±π/2로 압축된 뒤 다음 policy 입력으로 돌아오는 점이 가설 1과 연결된다. 수천 단위 숫자가 그대로 재입력되는 것은 아니며, 포화된 부호 조합에도 큰 정책 반응이 발생한다.

실패 직전 채널 평균 std는 OSC/Hand 각각 Sweep v0 0.422/0.508, Contact v0 0.449/0.544, Contact v1 0.979/1.284다. 손 탐색이 상대 허용 폭에 비해 더 크지만, std가 수천인 것은 아니며 극단 값은 정책 평균에서 발생한다.

### 가설 3: 공통 MLP의 큰 이득이 손 출력에서 더 크게 나타난다 — 현재 모델에서 확인

공통 관측을 처리하는 shared MLP 끝에 12개 선형 출력이 있고, 평균에 별도 채널별 출력 상한은 없다. Contact v1 t7/env1183에서 Last Action 12D에 대한 정책 평균의 국소 미분을 계산했다. 손 이력→손 출력 Jacobian Frobenius norm은 2533.38, 같은 손 이력→OSC 출력은 869.49다. 팔 이력→손 출력도 2115.44로 팔 이력→OSC 출력 730.35보다 크다. 동일 차원의 블록 비교에서 손 출력 경로가 약 2.9배 민감했다. 이 값은 clamp 이후 관측에 대한 국소 미분이며 실제 물리 closed-loop 안정성의 고유값으로 해석하지 않는다.

이 샘플의 손 평균 최대 5980.12, OSC 평균 최대 3272.52라는 차이는 학습된 큰 이득이 두 출력 그룹에 다르게 투영된 결과로 설명할 수 있다. 손만의 별도 clipping 누락이나 손 std 폭증을 가정할 필요는 없다.

### 가설 4: 손 범위 초과 벌점이 OSC보다 약하다 — 같은 절대 초과 기준으로 기각

동일한 절대 초과량을 비교하면 손의 정규화 분모가 더 작아 limit 제곱 비용은 OSC보다 **4.77~28.70배 강하다**. 손 초과 페널티 누락이나 상대적으로 작은 계수를 이유로 들 수 없다.

다만 변화량 비용은 물리 단위·허용 폭을 정규화하지 않는다. 각 그룹이 전체 허용 폭의 같은 비율만큼 움직이면 손의 rate 제곱 비용은 OSC의 3.48~20.95%다. 동일 숫자 변화에서는 비용이 같고, 동일 범위 비율 변화에서는 손 비용이 작으며, 동일 절대 초과의 limit 비용은 손이 더 강하다. 세 비교 기준을 혼동하지 않는다.

추론의 우선순위는 **손의 좁고 양수인 실행 범위 + 맞지 않는 Gaussian 초기 스케일 → 빈번한 포화/음수 원본 이력 → 공통 MLP의 과민한 이력 반응 → 양쪽 출력 폭주, 손 출력에서 더 큰 투영 → 상한 없는 원본 비용 폭증**이다. 각 연결의 강도는 위 실험에 따른 것이며 역사적 전체 인과를 모두 재현한 결론은 아니다. 손 이력 정합과 채널별 정책 스케일을 우선 검토하되, limit 벌점 계수만 더 높이는 처방의 근거는 약하다.

추가 산출물: [OSC·Hand 채널별 비교와 이력 제거/미분 결과](../../../../outputs/wr1122_diagnosis/compare_arm_hand.json), [일정 음수 손 명령 비용 예시](../../../../outputs/wr1122_diagnosis/hand_constant_negative_cost.json). 이 후속에서도 소스·설정·로그를 수정하지 않았으며, 새 분석 스크립트의 AST 검사와 GPU 전방/미분 계산을 수행했다. 후속 문서 수식 검사·외부 링크 12개 검사·전체 문서 링크 검사·git diff --check도 오류 없이 통과했다.

## 후속: example/Sweep-Policy의 이질적 action 결합 방식 확인

사용자 요청으로 참고 저장소 `example/Sweep-Policy` HEAD `baa3740e38c1a693b2094dc4d141b72de0dd3142`를 읽었다. 등록 ID·Cfg 상속·Action term·관측·보상·runner·공식 trainer wrapper를 대조했다. 참고 저장소 작업트리는 조사 전후 clean이며 소스/학습 로그는 수정하지 않았다.

### 대상 계열 구분

- `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v1` 및 v1-mass/v1-mass-limit/v2/v2-mass/v3-mass/v3/v4는 **JointPosition 팔 6D + Inspire 손 openness 2D = 8D**다. Inspire-Open-v0는 손을 고정해 팔 6D뿐이다.
- 별도의 OSC 계열 Random-v2/Single-Offset 및 관련 파생은 **OSC 팔 + Robotiq binary 개폐 action**을 사용한다. 등록된 Inspire 2D 손 계열을 현재 Single Contact의 OSC+6D 손과 같은 제어 조합으로 취급하지 않는다.

### Inspire 8D 제어와 현재 환경의 차이

| 항목 | 참고 Sweep-Policy Inspire 계열 | 현재 Single Contact v1 |
| --- | --- | --- |
| 팔 | JointPosition: q_target=q_default+0.5×a_arm | OSC: 원본을 ±π/2로 제한하고 상대 위치/회전 scale 적용 |
| 손 정책 차원 | 2D: 공통 굽힘 개방도 + 엄지 대립 개방도 | 6D: 독립 구동 관절 목표 rad |
| 손 실행 범위 | 각 개방도를 [0,1] clamp 후 12관절에 선형 배분 | 각 구동값을 [0,URDF 상한] clamp 후 mimic 적용 |
| 손 action 방향 | 0=완전히 굽힘, 1=완전히 펼침 | 0 rad=펼침, 상한=굽힘 |
| 손 목표 변환 | q_closed+o×(q_open-q_closed), q_open=0 | 클립한 구동각 자체를 사용 |
| reset 손 이력 | ActionManager 현재/이전 및 term raw/processed 모두 [1,1] | 0 초기화가 0 rad 개방 의미 |
| Last Action | 기본 mdp.last_action: ActionManager 원본 전체, 관측 clip 없음 | ActionManager 원본을 ±π/2 clamp |
| 변화량 비용 | 전체 8D 원본 차이 제곱합, weight -0.03 | 팔6D/손6D 원본 차이 제곱합, 각각 weight -0.03 |
| 범위 초과 비용 | 해당 Inspire 계열에 없음 | 정규화된 초과량 제곱평균, 각 weight -0.03 |
| 정책 스케일 | init_noise_std=1, 채널별 std/평균 범위 제한 override 없음 | init_std=1, 채널별 평균 상한 없음 |

참고 팔 설정은 `JointPositionActionCfg(scale=0.5,use_default_offset=True)`이며 별도 clip은 지정하지 않는다. 현재 IsaacLab JointAction은 `cfg.clip`이 주어졌을 때만 처리 명령을 clamp한다. 물리 관절 한계·액추에이터 제한을 별도의 정책 action clipping으로 간주하지 않는다.

손은 [공통 개방도, 엄지 대립 개방도] 두 값이다. 공통 값은 엄지 2~4 및 나머지 손가락에, 두 번째 값은 엄지 1에 적용한다. `InspireHandOpennessAction.process_actions`는 원본을 raw buffer에 보관하고, 별도 processed buffer만 [0,1]로 제한한다. smoothing·rate limit·sigmoid/tanh policy 변환은 없다. 따라서 -3은 개방도 0으로 실행되며 **최대 굽힘**을 뜻한다. 현재 rad 손의 음수→0 rad→완전 개방과 의미가 반대다.

`train.py`는 공식 IsaacLab RSL-RL trainer로 위임한다. 참고 runner는 wrapper clip을 override하지 않으며, 현재 workspace `RslRlOnPolicyRunnerCfg` 기본 `clip_actions=None`, trainer는 이를 wrapper로 전달한다. 이는 현재 소스 조합의 확인이며, 과거 학습 당시 다른 IsaacLab 설치나 CLI override까지 복원한 결과는 아니다.

### 비용·관측의 실제 데이터 경로

기본 `mdp.last_action`은 `env.action_manager.action`을 그대로 반환한다. `mdp.action_rate_l2`도 같은 manager의 원본 현재/이전 값을 읽는다. 이 참고 계열은 `legacy_clipped_previous_action` 같은 별도 관측 압축을 사용하지 않는다. 관련 cfg·runtime·reward 전체 검색에서 현재 활성의 `action_limit_excess`에 해당하는 원본 범위 초과 비용을 찾지 못했다.

```text
정책 8D 원본
  → ActionManager 원본 저장
      → 팔: ×0.5 + default pose → JointPosition target
      → 손: [0,1] clip → 개방도 선형 변환 → 12개 joint target
  → Last Action: 원본 그대로
  → action_rate: -0.03 × dt × sum((원본 현재−이전)^2)
```

policy dt는 이 계열도 0.02이므로 action_rate의 최종 계수는 -0.0006이다. 예를 들어 손 원본 180→5700이 발생하면 실행 개방도는 모두 1(완전 펼침)이지만 원본 변화량 비용은 여전히 매우 커진다. 일정한 범위 밖 원본값을 유지하면 변화량 비용은 0이며, 이 구현에는 원본 범위 이탈 자체를 벌하는 별도 항이 없다.

### 해석과 검증

확인된 참고 설계의 장점은 **손 action을 관절별 rad 대신 동일한 [0,1] 개방도로 표현하고 2D로 줄인 점**, **reset 목표와 현재/이전 action 이력을 일치시킨 점**이다. 그러나 정책 원본 범위 제한·원본과 실행 이력의 일치·원본 변화량 비용의 상한을 보장하는 별도 해결책이 구현된 것은 아니다. 참고 구현만으로 현재 폭주가 해결된다고 주장하지 않는다. 수렴 여부는 별도의 학습 이력/체크포인트 검증이 필요하다.

기존 CPU 테스트를 다음 명령으로 실행해 실제 손 action의 매핑·클립·원본 보존·부분 reset·이력 초기화 등 6개를 통과했다. 최초 pytest 실행은 ROS pytest plugin 자동 로딩 중 `lark` 부재로 시작 전 실패했고, 아래처럼 불필요한 plugin 자동 로딩을 끈 재실행은 통과했다. 패키지는 설치/수정하지 않았다.

```bash
cd example/Sweep-Policy
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q -p no:cacheprovider tests/test_inspire_hand_action.py
```

학습·GPU simulator·참고 checkpoint 평가는 실행하지 않았다. 실제 소스 근거:

- [JointPosition 팔 설정](../../../Sweep-Policy/sweeping_policy/config/ur5e/joint_pos_random_sweep_env_cfg.py)
- [Inspire 2D 손 매핑·클립](../../../Sweep-Policy/sweeping_policy/src/ur5e_inspire_hand.py)
- [손 action 이력 reset](../../../Sweep-Policy/sweeping_policy/env_inspire_hand.py)
- [기본 Last Action 관측](../../../Sweep-Policy/sweeping_policy/shelf_sweep_random_env_cfg.py)
- [Inspire action-rate 설정](../../../Sweep-Policy/sweeping_policy/config/ur5e/joint_pos_random_single_inspire_open_env_cfg.py)
- [상속 PPO 설정](../../../Sweep-Policy/sweeping_policy/config/ur5e/agents/rsl_rl_ppo_cfg_02.py)

## 제안: 구현하지 않음

1. **정책 출력의 채널별 스케일을 제한한다.** arm/hand의 허용 폭에 맞춰 평균을 매끄럽게 제한하고 std도 채널별 스케일·상한을 갖게 하는 방안이 우선이다. 일반 Gaussian의 평균만 제한하면 샘플 전체가 수학적으로 bounded해지는 것은 아니므로 raw 비용/실행 경계 보호도 필요하다. bounded distribution을 선택한다면 실제 저장 action에 대한 올바른 likelihood를 사용하고 포화 샘플에 역변환을 적용하는 수치 실패를 별도로 검증해야 한다. 기존 checkpoint 의미가 달라지면 새 학습으로 검증한다.
2. **비용의 의미와 수치 상한을 함께 설계한다.** 실행의 거칠기를 벌하는 action rate는 실제 실행 action 또는 채널 폭으로 정규화한 변화량을 사용한다. 원본 초과명령을 벌하는 목적은 별도의 action-limit 비용으로 유지하되 작은 초과에서는 기존 제곱 형태를 보존하고 큰 초과에서는 Huber/로그/포화형과 명시적 최종 상한을 검토한다. 물리 실행은 이미 제한되므로 수천 raw action에 수십만 비용을 계속 부과할 필요와 학습 영향을 구분해 결정한다. dt·허용 최대 episode 비용·양의 보상 규모를 기준으로 상한을 산정한다.
3. **Last Action 관측 의미를 정합화한다.** 현재는 arm/hand 모두 ±π/2지만 실제 hand 실행 범위는 [0, 각 URDF 한계]이다. 실행 이력을 관측한다면 실제 실행 값으로 통일하고 채널별 정규화한다. 원본 명령을 관측해야 한다면 그 목적과 압축을 명시한다. 기존 정책에 clamp/tanh를 사후 삽입하는 것만으로 해결됐다고 보지 않는다.
4. **실패 경계를 rollout 초기에 둔다.** 현재 actor 평균 ceiling 1e6은 수천 출력도 허용하고 value loss는 8 epochs/32 minibatches 뒤 평균으로 검사한다. 채널 허용 폭 기준 mean/raw-action·비용의 최대값과 분위수·초과 비율을 기록하고 극단 명령은 환경 적용 전, 큰 value loss는 해당 minibatch backward 전에 중단해 증거를 보존한다. std 평균만으로는 이번 문제를 잡지 못한다. 자동 재시작·배치 무시·안전 ceiling 상향은 제안하지 않는다.

학습률 감소·entropy 감소·critic Huber loss·reward/return normalization은 보조책이다. Contact v1의 실패 전 학습률은 이미 1e-5였고, 실패 전 모델을 그대로 재평가해 극단 출력을 재현했다. max_grad_norm은 backward gradient를 제한하며 rollout reward나 actor forward 출력의 상한을 보장하지 않는다. PPO value clipping 역시 loss 자체를 0.2로 제한하지 않는다.

검증은 저장된 실패 관측 bank에 대한 최대 mean/std/value, 원본 reward 항별 상한, raw/실행/관측 action 정합, PPO update 유한성에서 시작하고, 그 다음 동일 seed의 실제 물리 rollout과 충분한 장기 학습으로 진행해야 한다. 현재 진단은 어떤 변경도 구현하지 않았고 성공률 개선이나 재발 방지를 검증한 것이 아니다.

## 산출물과 검증 경계

- [분석 재현 안내와 산출물](../../../../outputs/wr1122_diagnosis/README.md)
- [전체 loss 이력 그림](../../../../outputs/wr1122_diagnosis/value_loss_history.png)
- [원본 PPO 재생 결과](../../../../outputs/wr1122_diagnosis/replay.json), [비용 개입 재생 결과](../../../../outputs/wr1122_diagnosis/replay_cap100.json)
- [보상 분해](../../../../outputs/wr1122_diagnosis/decompose.json), [채널 제거·체크포인트 대조](../../../../outputs/wr1122_diagnosis/ablate.json), [발단 step 기록](../../../../outputs/wr1122_diagnosis/triggers.json)
- [전체 이력 요약](../../../../outputs/wr1122_diagnosis/scalars_summary.json), [유한성 검사·런타임](../../../../outputs/wr1122_diagnosis/integrity.json), [원본 로그 SHA-256](../../../../outputs/wr1122_diagnosis/source_hashes.json)

코드/설정 변경 전후 차이: 없음. 학습 로그/모델 변경: 없음. 추가는 진단 문서 및 outputs 산출물뿐이다. 저장 원본 상태를 이용한 실제 GPU PPO 재생·비용 분해·관측 제거 실험·21개 checkpoint 전방 계산·전체 TensorBoard 이력 확인을 수행했다. 실제 물리 상태 복원, 원 센서 spike 생성 원인, 정확한 원 서버 RNG/패키지 재현, 제안안 장기 학습·성공률은 미검증이다. 문서 수식 검사·신규 문서 외부 링크 10개 검사·git diff --check를 통과했다. loss 이력 PNG를 렌더링해 축·범례·실패점이 보이는지 직접 확인했다. 전체 문서 링크 검사도 통과했다(653개 Markdown, internal links 5567개, external links 1251개, errors 0).
