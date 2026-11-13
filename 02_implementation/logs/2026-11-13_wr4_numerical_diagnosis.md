# wr4 Finger 두 실행 수치 중단 원인 진단

2026-11-13. 사용자 요청은 `logs/TEMP/wr4`의 두 환경 중단 원인 조사이며 GPU 테스트도 허용했다. **진단만 수행했고 환경·보상·PPO·검사 임계값은 변경하지 않았다.** 원본 로그와 `logs/rsl_rl`, 기존 문서 작업트리 변경을 보존했다.

## 결론

공통 취약점은 유한한 F/T 입력을 무제한 Gaussian 평균으로 크게 증폭할 수 있는 정책이다. 그러나 **동일한 NaN/물리 발산 사건으로 묶을 수는 없다.** 두 덤프의 관측·모델·optimizer·gradient·rollout 텐서는 모두 유한했다.

- **Finger-v0-Test:** 희귀 F/T 관측 → 정책 평균 약 9,046 → raw action 변화 제곱 비용 약 −146,234 → 큰 음수 return → value MSE 약 196.7만. 실패 업데이트 이전에 이미 오차가 형성됐다. 표준편차는 약 0.44–1.18로 정상적인 크기이며 v1 같은 분포 폭주는 아니다.
- **Finger-v1:** 실행은 clip되지만 PPO의 raw Gaussian 엔트로피는 무제한 증가 가능하다. 수천 iteration 동안 평균·표준편차가 커지고 손 출력이 거의 항상 경계로 잘렸다. 이 상태에서 F/T 관측이 평균을 −1,019,958까지 증폭해 actor guard가 중단했다. 이때 보상·return 크기는 정상 범위였다.

## 대상과 코드 대조

| 실행 디렉토리 | 환경 | 진단 iteration | 원래 오류 |
| --- | --- | ---: | --- |
| `inspire_sweep_simple_finger_v0_test/2026-11-11_12-35-32` | `Inspire-Sweep-Simple-Finger-v0-Test` | 8043 | `loss/value: 1967222.318359375` |
| `inspire_sweep_simple_finger_v1/2026-11-11_12-40-32` | `Inspire-Sweep-Simple-Finger-v1` | 7261 | `actor/mean ... indices=[[135, 6]]` |
| `inspire_sweep_simple_finger_v1/2026-11-11_03-38-59` | Finger-v1 비교 실행 | TensorBoard 마지막 4632 | failure dump 없음; 중단 원인은 판단하지 않음 |

두 실패 실행의 기록 commit과 현재 HEAD는 `1ab6e579cf1c4f4152954b1c6fb0120a99729eb5`. 해당 실행의 git diff는 문서 submodule 차이만 기록한다. 비교 실행은 `65bb0a395c3b48338ddcef21ed5e27d48d46cf35`이며 별도 실행으로 취급했다.

사용한 증거: 각 `numerical_failure.pt/json`, `params/agent.yaml`, `params/env.yaml`, 체크포인트, 세 TensorBoard 파일. 실제 등록·runtime·모델·보상·관측·installed RSL-RL PPO를 대조했다. 아래 소스 경로는 활성 패키지 기준이다.

- `agent/numerical_ppo.py`: 관측/평균/return 한계 1e6, update 평균 value loss 한계 1e6. guard가 원인이 아니라 이미 생성된 이상 크기를 검출한다.
- `agent/sweep_simple_models.py`, `agent/wrench_refactor_models.py`: 실제 66D direct 관측과 16D 장애물 임베딩을 사용하는 ELU MLP, 두 실행 `obs_normalization: false`.
- `runtime/sweep_simple.py`: v1은 `ActionManager` 진입 전에 out-of-place clip. PPO 원본 샘플은 보존하고 action-rate/Last Action에는 clip 후 값이 들어간다.
- `mdp/reward_functions/sweep_simple.py::finger_action_rate_l2`: manager current/previous action의 제곱 차이 합. cap 없음.
- `mdp/observation_functions/final.py::previous_action_command`: v0-Test Last Action은 tanh이지만 manager raw action과 비용은 그대로다.
- `agent/sweep_simple_distributions.py::FingerGaussian`: v1은 log std, 일반 Gaussian entropy, 초기 std만 축별 설정. 상한 없음. v0-Test는 라이브러리 scalar std Gaussian이다.
- `runtime/sweep_simple.py::load_managers`: F/T는 noise 후 force ±150 N, moment ±8 N·m clip. 크기 정규화는 하지 않는다.

## 재현과 검증 경계

저장 관측·모델로 실제 `NumericalPPO.act`를 호출해 v1의 동일 인덱스 오류를 재현했다. v0-Test는 저장된 update 이전 모델·Adam, 36×2048 rollout, return/advantage를 로드해 실제 `NumericalPPO.update`를 실행했다. 덤프에 없는 old likelihood와 분포 파라미터는 update 이전 actor로 재계산했다. 원래 minibatch 난수 상태와 원격 머신 연산 차이도 있으므로 loss의 bitwise 일치는 주장하지 않는다.

| 장치 | v1 `[135,6]` 평균 | v0-Test update value loss | 판정 |
| --- | ---: | ---: | --- |
| CPU | −1,019,958.3125 | 1,967,211.646484375 | 두 원래 guard 재현 |
| RTX 3090 CUDA | −1,019,958.4375 | 1,967,238.208984375 | 두 원래 guard 재현 |

처음 sandbox 안의 `nvidia-smi`는 driver 연결에 실패했으나, 승인된 sandbox 밖 실행에서 RTX 3090/driver 560.35.03을 확인하고 GPU 재생까지 완료했다. GPU 부재로 판단하지 않는다.

재현 산출물은 [outputs/wr4_diagnosis](../../../../outputs/wr4_diagnosis)에 보존했다. 재현기는 실패가 재현되면 `REPRODUCED`와 함께 정상 종료하고, 재현되지 않으면 assertion으로 실패한다. `assets` package initializer의 USD 의존 import만 우회하며 실제 hand kinematics·모델·분포·PPO 코드를 사용한다. 시뮬레이터/새 학습을 시작하는 스크립트는 아니다.

```bash
# workspace root에서 실행
/home/min/miniconda3/envs/env_isaaclab/bin/python outputs/wr4_diagnosis/replay.py
WR4_DEVICE=cuda:0 /home/min/miniconda3/envs/env_isaaclab/bin/python outputs/wr4_diagnosis/replay.py
/home/min/miniconda3/envs/env_isaaclab/bin/python outputs/wr4_diagnosis/causal_probe.py
```

## Finger-v0-Test: 비용과 value loss의 원인 연결

실패 rollout의 zero-based step 15, env 211에서 F/T는 `[8.4378, 64.5631, 0.3902, 0.0434, -0.0421, 5.7877]`. 이 관측은 허용 센서 범위 안의 유한값이다. 이 batch의 force 절댓값 99%/99.9% 분위수는 약 3.93/8.21 N으로 64.56 N은 드문 입력이다. 실제 원시 센서·접촉 상태는 덤프에 없어 물리적 충돌의 정당성은 판정할 수 없다.

update 이전 actor를 재생하면 손 ring 평균이 `9045.7324`, 실제 샘플이 `9045.0957`이다. std 최대가 `1.18423`이므로 거대한 Gaussian 난수보다 **관측에 대한 평균 출력의 증폭**이 원인이다. 해당 step에서 이전 action 대비 실제 비용을 대조했다.

```text
dt = 0.01 × decimation 2 = 0.02
r_action = -0.03 × 0.02 × sum((action - prev_action)^2)
arm contribution  =   -2,109.3210
hand contribution = -144,125.1563
combined cost     = -146,234.46875
stored reward     = -146,234.46875
```

동일 정책·동일 관측에서 **마지막 F/T 6개만 0으로 치환한 진단 대조**는 평균 출력 최댓값 `9045.73 → 7.2914`, 이전 raw action 대비 평균의 변화 비용 `−0.009854`를 만든다. 센서를 제거하라는 수정 제안이 아니라 입력의 원인 기여를 분리한 실험이다. 이전/현재 샘플을 모두 v1 경계로 clip하는 계산 대조에서는 비용이 `−0.009779`다. 보상·물리 전체를 재계산한 대체 rollout은 아니다.

env 1640에서도 `−15,470.49`의 큰 비용이 존재한다. GAE는 두 사건의 음수 return을 이전 step들로 전파한다. 저장 value/return MSE는 `1,967,218.875`이며 두 env를 제외하면 `0.392423`. 두 env가 전체 squared error의 약 `99.999988%`를 차지한다. update 이전 critic을 다시 계산해도 MSE가 `1,967,222.25`로 이미 guard 임계값을 넘는다. 따라서 이번 실패를 마지막 optimizer step이 처음 만들어낸 것으로 볼 수 없다.

같은 실패 관측을 과거 checkpoint에 넣은 평균 출력 절댓값 최대는 iteration 0: `1.28`, 1000: `14.35`, 3000: `156.09`, 5000: `1092.24`, 7000: `2712.20`, 7950: `10348.37`, 8000: `13231.28`. 단조 증가까지는 아니지만 학습 중 드문 F/T 입력에 대한 증폭이 커진 증거다. 동일 checkpoint의 현재 정상 관측 batch 출력은 대체로 8–13 수준이다. 왜 각 optimizer update가 그 외삽을 만들었는지까지의 전체 인과 경로는 저장 로그만으로 확정하지 않는다.

TensorBoard에도 iteration 7977에서 value loss `596147.06`, episode hand action-rate `−46.4621`, mean reward `−998.39`의 선행 이상이 있다. 8042에는 value loss `0.09393`으로 돌아왔으므로 평균 지표만 보면 희귀 입력 위험을 놓칠 수 있다.

팔 속도 1 rad/s 종료는 이를 막지 못한다. `ManagerBasedRLEnv.step`은 종료 판정 뒤 같은 transition의 보상도 계산한 다음 reset한다. 실제 큰 비용 사건은 done=1이고 return도 저장됐다. 종료 조건은 raw policy 평균이나 비용 크기의 상한이 아니다.

## Finger-v1: raw Gaussian entropy와 실행 clip의 불일치

| iteration | thumb std | thumb 평균의 환경 평균 | thumb clip 비율 | entropy |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0.09773 | 0.29229 | 0.00292 | 0.353 |
| 1000 | 0.46614 | −0.14965 | 0.72948 | 9.901 |
| 2000 | 12.55473 | −14.61521 | 0.99124 | 33.845 |
| 3000 | 1005.97589 | −1021.81665 | 0.99986 | 64.440 |
| 4000 | 21021.99023 | −10213.95801 | 1.00000 | 84.076 |
| 6000 | 139509.64062 | −45981.95312 | 1.00000 | 99.299 |
| 7260 | 317625.625 | −63217.14062 | 1.00000 | 104.190 |

실패 직후가 아니라 수천 iteration 전부터 폭주했다. failure dump의 thumb std는 마지막 update 후 `318107.31`이다. 별도 03:38 실행도 std가 iteration 2000 `0.9868` → 4000 `98.4514` → 4632 `349.7888`로 커지고 clip 비율이 99.7% 이상에 이른다. 다만 그 실행의 최종 중단 이유는 남은 자료로 알 수 없다.

실행 clip 때문에 범위를 넘는 raw 값은 대부분 같은 경계 명령으로 바뀐다. action-rate 역시 clip 후 값을 사용하므로 raw 크기의 확대를 벌점으로 인식하지 않는다. 반면 PPO loss에는 `-0.005 * raw_Gaussian_entropy`가 있고 Gaussian entropy는 각 축의 `log(std)`에 비례한다. 실제 분포를 미분하면 모든 `log_std`에 대해 엔트로피 loss 기울기는 약 `−0.005`였다. 즉 std가 커져도 확대를 유도하는 항이 사라지지 않는다.

저장된 36×2048×6 손 raw 샘플 중 `99.999094%`가 경계 밖이었다. 같은 샘플의 손 성분만 10배로 바꿔 clip하면 442,368개 성분 중 단 4개만 실행값이 달라진다. Gaussian 손 평균·std를 함께 10배로 확대하는 대응 분포는 entropy bonus를 `0.005 × 6 × log(10) = 0.069078` 높일 수 있다. 실행 동작이 거의 변하지 않아도 최적화 목적에 이득이 생기는 구조다. mean은 entropy의 직접 미분 대상은 아니며, 분포의 큰 scale과 경계 선택 확률을 유지하는 학습·입력 증폭이 함께 작용한 것으로 해석한다. entropy 제거 후 장기 학습으로 기여도를 정량 분리하지는 않았다.

마지막 env 135의 force는 `[150, -10.6851, -143.0762]` N, moment는 `[-0.1092, -5.2200, -0.3344]` N·m이다. 그 입력에서 thumb 평균이 `−1,019,958.31`. F/T 6개만 0으로 바꾸면 `−43,386.03`이 되어 guard 아래로 내려가지만 여전히 거대하다. **F/T는 마지막 임계값 통과의 방아쇠이고, 분포 폭주 자체는 그 전부터 존재했다.** 현재 관측을 제외한 storage는 중단 중인 rollout과 이전 rollout의 잔여 데이터가 섞일 수 있으므로 저장 36 step을 모두 실패 iteration의 완성 rollout으로 해석하지 않았다.

## 배제한 설명과 후속 수정 방향

- 두 덤프에 NaN/Inf는 없다. 일반 Gaussian 경로이므로 과거 tanh→atanh 포화 오류와 다르다.
- 기록된 커리큘럼 지표는 두 실패 실행 모두 6000 이후 고정이다. 중단 시점의 새 일정 변경이 직접 방아쇠였다는 증거는 없다.
- v0-Test의 큰 return/오차는 PPO update 전에 존재한다. 단순히 learning rate만 낮추거나 value guard를 높이는 것으로 이미 생성된 보상 문제를 해결할 수 없다.
- v1은 clip 후 action-rate가 작게 유지되므로 action-rate 출력 cap 제거만으로 설명할 수 없다. v0-Test는 cap 없는 raw 제곱 비용이 큰 보상을 직접 만들었다. 공통된 하나의 보상 cap 회귀로 단정하지 않는다.

수정 시 우선순위는 (1) 실행 가능한 action과 정책의 평균·std·entropy 목적을 함께 일치시키고, (2) v0-Test의 희귀 F/T 입력 증폭과 raw 제곱 비용 경로를 제어하는 것이다. v0-Test를 v1처럼 clip만 추가하면 이번 value spike는 줄일 수 있지만 v1의 entropy 확대 문제를 그대로 도입할 수 있다. 센서 scale 조정, 정책 분포의 유효 범위, raw 크기에 대한 제약, 실제 실행 분포의 entropy를 함께 설계해야 한다. 이는 **미적용 제안**이며 보상 상한 복원·entropy 계수 변경·정규화 도입을 임의로 수행하지 않았다.

## 최종 대조와 미검증 범위

- 추가: 본 진단 기록, 로그 색인 링크, `outputs/wr4_diagnosis`의 read-only replay/probe·결과·시계열 발췌.
- 보존: 환경 구성, 정책·보상·관측·종료·커리큘럼 수치, guard 임계값, 기존 사용자 작업, 모든 학습 원본 로그.
- 검증: 실제 모델/PPO의 CPU와 CUDA 오류 재현, 저장 reward와 raw 비용 대조, F/T 입력 대조, loss 집중도·과거 checkpoint 대조, entropy gradient·clip 동작 대조, TensorBoard 시계열 대조.
- 문서 검사: 변경 2개 Markdown 수식 검사, 변경 문서의 외부 경로 포함 링크 검사, 전체 579개 Markdown 링크 검사, workspace/문서 저장소 `git diff --check` 모두 통과. 렌더링 별도 미검증.
- 미검증: 실패 당시 PhysX 상태/원시 접촉 재현, F/T 급변의 물리적 원인, 최초부터 동일 시드 장기 재학습, 수정 후보의 장기 안정성과 성능. 덤프는 simulator 상태를 포함하지 않으며 이번 검증은 시뮬레이터 학습이 아니다.
