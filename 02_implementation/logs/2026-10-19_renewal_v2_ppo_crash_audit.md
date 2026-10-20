# Renewal v2 두 실행의 PPO 수치 오류 진단

[개발 로그](README.md) · [재현 스크립트](../../03_assets/artifacts/ppo_crash_2026-10-19/audit.py) · [지표 CSV](../../03_assets/artifacts/ppo_crash_2026-10-19/scalars.csv) · [체크포인트 검사](../../03_assets/artifacts/ppo_crash_2026-10-19/checkpoints.csv)

## 요청과 조사 범위

2026-10-19 사용자 요청: 아래 두 실행이 `normal expects all elements of std >= 0.0`로 중단된 원인을 조사한다. 사용자는 특히 reward/termination 이상치로 인한 loss 폭발을 의심한다고 추가 설명했다.

- `logs/rsl_rl/inspire_dex_tactile_sweep_omni_renewal_v2/2026-10-19_12-16-03`
- `logs/rsl_rl/inspire_dex_tactile_sweep_omni_renewal_v2/2026-10-19_17-52-20_resume_8500`

두 실행의 저장 Git commit과 조사 시 workspace HEAD는 `2cca359d747edad0782a93119af1992842cb4979`로 같다. 당시 diff는 문서 submodule 참조뿐이다. 현재 활성 소스 변경은 없고, 기존 문서 submodule 참조 및 미추적 UR Description 디렉터리는 보존했다. 조사에서는 학습 코드·보상·설정·체크포인트를 수정하지 않았다.

저장된 env.yaml은 log_dir만 다르고 agent.yaml은 resume/run_name/load 경로만 다르다. 2048 env, 36 step/iteration, step_dt 0.02 s, seed 42, 8 epochs, 4 minibatches, Adam, adaptive LR, gamma 0.98, lambda 0.95다. Actor/Critic 모두 policy 관측을 사용하며 obs_normalization=false, 관측 clip/scale 없음, Gaussian std_type=scalar다. 설치된 RSL-RL 소스를 읽었으며 당시 설치 패키지 내용까지 불변이었다는 별도 스냅샷은 없다.

## 확인한 시간 순서

수치는 TensorBoard의 기록된 iteration이다. 마지막 기록은 정확한 예외 발생 iteration을 보장하지 않는다.

| 실행 | iteration | Loss/value | 의미 |
| --- | ---: | ---: | --- |
| 최초 | 8845 | 3.5075 | 폭발 직전 |
| 최초 | 8846 | 5.3007e7 | 처음 1000 초과 |
| 최초 | 8847 | 5.1449e12 | 급격한 악화 |
| 최초 | 8935 | inf | 첫 비유한 loss |
| 최초 | 9843, 9966 | inf | 재발 |
| 최초 | 9967 | NaN | 마지막 기록 |
| resume | 8501 | 4.9574e7 | 재시작 직후 이상치 |
| resume | 8502 | 3.3892 | 다음 iteration 정상 범위 복귀 |
| resume | 9568 | 4.9732e12 | 반복 이상치 |
| resume | 11069, 11070 | 1.1062e28, 2.1612e29 | 극단값 |
| resume | 11071 | 3.9770 | 다시 정상 범위 복귀 |
| resume | 11203 | inf | 첫 비유한 loss |
| resume | 11204 | 3.6899 | 다시 정상 범위 복귀 |
| resume | 11474 | 2.6892e14 | 마지막 기록 |

최초 9968개, resume 2975개 iteration과 각 30개 scalar tag를 확인했다. 모든 Episode_Reward/Termination scalar는 유한하다. 최초 8846의 mean_reward는 24.0186, resume 마지막은 22.7940으로 평균 보상이 동시에 거대해지지는 않았다. 단, Episode_Reward는 종료된 환경들의 누적 보상을 평균하고 최대 에피소드 시간 10초로 나눈 값이다. iteration 평균과 종료 시점에 의존하며 개별 step 최대값을 기록하지 않으므로, 평균만으로 reward spike를 배제할 수 없다.

200+60개 저장 checkpoint에서 모델과 optimizer의 모든 tensor는 유한했다. 전체 최소 std는 각각 0.0223709, 0.0319071로 모두 양수다. 원본 8500 checkpoint도 정상 범위다. 마지막 checkpoint는 9950/11450으로 실제 예외 순간은 담지 않는다. 음수 std와 NaN std가 동일한 오류 문구를 발생시킴을 CPU에서 확인했다. 따라서 실제 실패 당시 std가 음수였는지 NaN이었는지는 미확정이다.

## Reward 반환 범위 감사

아래 값은 정상적인 유한 상태에서 `weight * step_dt`까지 적용한 환경별 1 step 기여다. 실행 당시 source와 저장 params를 함께 대조했다.

| 활성 항 | 1 step 기여 범위/조건 | 판단 |
| --- | --- | --- |
| arm_action_rate, hand_action_rate, arm_joint_velocity | 각각 [-0.06, 0] | 당시 함수에 제곱합 후 기본 cap=100이 이미 존재 |
| hand_joint_velocity | [-0.02, 0] | 동일 cap=100 |
| pushing_speed, arm_speed_excess | 각각 [-2, 0] | `_limit` 함수, 지수 계산 전 입력 제한 및 max_cost=100 |
| object_tilt | [-0.04, 0] | 비율을 [0,1]로 제한 후 제곱 |
| shelf_collision | [-0.04, 0] | moved 1 + finger 2 + wrist 1 최대 4 |
| success | 0 또는 +100 | Boolean 최초 달성 / dt, 에피소드당 한 번 |
| goal_hold | [0, 0.4] | 유지 비율 [0,1] |
| goal_distance | 정상 reset/goal에서 에피소드 누적 최대 약 +42 | 0.15 m 목표, 0.01 m 허용오차, 300/m; 기록 갱신만 지급 |
| reaching | 30 × 초기 잔여 접근거리 이내의 누적 보상 | 초기 거리 자체의 절대 상한·유한성 검사는 없음 |

당시 cap의 존재를 관찰한 것이며 이번 조사에서 추가하거나 계수를 바꾼 것이 아니다. NaN 입력을 안전하게 처리한다는 보장은 이 범위표에 포함하지 않는다.

따라서 정상 reset 상태에서 **기존 무제한 exp(speed)가 큰 음수 보상을 만드는 경로는 이번 저장 설정에 해당하지 않는다.** 음수 항들의 합계 하한은 -4.28/step이다. 현재 소스에서 정상 유한 상태의 속도만 증가시켜 1e10 규모 음수 reward를 만들 수는 없다.

남은 구체적인 reward 취약 후보는 `DexReachProgress`의 reset snapshot이다. `_best_distance`에 잘못된 큰 거리 또는 inf가 저장되면, 다음 정상 step에서 `old_best - new_best`가 거대한 양수/inf가 된다. `DexPlanarGoalProgress`도 초기 위치와 command가 일관된 정상 reset이라는 전제가 필요하다. 두 shaping 함수 모두 초기 거리로 나누지 않으므로 작은 분모에 의한 발산은 아니다. dt=0.02로 고정되어 있고 RewardManager에서 다시 곱한다.

[합성 입력 probe](../../03_assets/artifacts/ppo_crash_2026-10-19/probe_rewards.py)에서 실제 DexReachProgress에 reset 거리 1e10을 주고 다음 호출에서 정상 위치로 복귀시키면 최종 reaching reward=299999985664가 나왔다. 정상 reset 거리 0.6에서는 +15였다. 정상 goal snapshot에서 이후 물체 위치만 1e20으로 만들었을 때 goal reward는 0이었다. **이는 취약 경로의 존재를 검증한 것이며 두 실행의 reset 오류를 재현한 것이 아니다.** 저장 reaching 평균의 전역 최대는 최초 0.77965, resume 0.77844로, 해당 보상이 실제 폭발했다는 직접 로그는 없다.

## Termination과 학습 target 경로

활성 time_out/object_drop/push_fast/shelf_collision/hand_velocity/shelf_displacement는 비교·any·논리 연산을 통한 Boolean 반환이다. 이름이 hand_velocity지만 실제 callable과 asset 선택은 Arm이다. object_outside_shelf와 success termination은 꺼져 있다. 거대한 실수 termination 값을 직접 반환하는 함수는 발견하지 못했다.

종료 판정은 reward보다 먼저 계산하지만, done이 된 환경도 그 step의 reward 계산은 수행하고 이후 reset한다. 따라서 termination이 이상치 reward 계산을 미리 건너뛰게 해주지는 않는다. NaN 비교가 False가 되는 경우도 있어 Boolean 종료만으로 물리 상태 유효성을 검사할 수 없다.

별도로 RSL-RL `PPO.process_env_step`은 환경 보상에 `gamma * V(s) * time_out`을 더한다. 이 값은 Episode_Reward 로그에 포함되지 않는다. 따라서 환경 reward가 정상이어도 Critic이 크면 학습용 reward/return은 커질 수 있다. 특히 `V=inf, timeout=False`도 곱셈상 `inf*0=NaN`이 된다. 현재 구현 식으로 CPU에서 재현했다. GAE에도 `next_is_not_terminal * next_values`가 있어 같은 전파 위험이 있다. 이것은 Critic이 먼저 비유한 값이 되었을 경우의 증폭 경로이며 최초 원인을 증명하지 않는다.

## 현재 결론과 미확인 원인

확인된 사실은 **표준편차 오류에 앞서 반복적인 value/target 수치 불안정이 있었다**는 것이다. resume은 같은 설정으로 같은 위험 경로에 다시 노출된 실행이다. 원본 checkpoint 8500 자체의 비유한 파라미터를 복원한 증거는 없다.

가능한 최초 원인은 (1) reset snapshot 등에서 발생한 드문 reward spike, (2) 관측 이상치로 인한 Critic 출력/target 폭발, (3) 저장 사이 구간에서의 업데이트 불안정이다. 특히 raw F/T, 관절 속도, last_action 등은 관측에 무제한으로 들어가며 Actor/Critic 정규화가 없다. F/T 입력부는 비유한 raw를 검사하지만 큰 유한값은 통과한다. 재학습에서 극단 loss 직후 정상 범위로 복귀하고 저장 가중치 최대 절댓값은 11.63 이하라는 점은 일시적인 batch 이상치 가설과 부합한다. **F/T 또는 특정 reward를 실제 원인으로 확정할 수는 없다.**

RSL-RL `check_for_nan=true`는 env 출력의 isnan만 검사한다. inf, 큰 유한값, bootstrap 이후 rewards, values, returns, gradients와 optimizer 상태를 검사하지 않는다. gradient clipping도 비유한 gradient를 정상화해주는 보장이 없다. scalar std에는 양수 보장이 없으므로 최종 오류를 만들 수 있지만, log std만 바꾸면 value 폭발까지 해결된다는 근거는 없다.

## 다음 검증 제안 — 아직 미적용

PPO 계수 조정보다 첫 이상치 순간을 저장하는 계측이 우선이다. 환경별 reward term raw/weighted 값, reset 전후 reaching `_best_distance`, goal 초기 위치/command, termination Boolean, 관측 term별 최대값과 env_id를 기록한다. 동시에 PPO에서 환경 reward와 timeout 가산 후 reward를 분리하고 values/returns/advantages/loss/gradient/std의 유한성을 검사한다. 첫 비정상 업데이트 전에 batch·모델·optimizer를 보존한다. 정상 범위 안의 이상치도 잡을 수 있도록 물리량별 임계값은 별도 정의해야 한다.

해당 근거를 얻은 뒤 원인별로 reset 검증, 관측 전처리, 비유한 업데이트 중단, 양수 std parameterization을 검토한다. std parameterization 변경 시 기존 checkpoint·optimizer state의 변환도 필요하다. 사용자 지정 네 운동 페널티와 계수를 임의 변경하지 않는다.

## 실행한 검사와 한계

Workspace 루트, `/home/ssu/miniconda3/envs/jd_isaaclab/bin/python` 사용:

```bash
/home/ssu/miniconda3/envs/jd_isaaclab/bin/python example/Contact-Rich-Manipulation-Context/03_assets/artifacts/ppo_crash_2026-10-19/audit.py
PYTHONDONTWRITEBYTECODE=1 /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B example/Contact-Rich-Manipulation-Context/03_assets/artifacts/ppo_crash_2026-10-19/probe_rewards.py
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_goal_rewards.py src/inspire_sweep_baseline/tests/test_dex_rewards.py src/inspire_sweep_baseline/tests/test_goal_hold_rewards.py src/inspire_sweep_baseline/tests/test_goal_terminations.py src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py
```

결과: audit는 12943 iteration·260 checkpoint 검사 완료, CPU probe는 위 합성 결과, pytest는 **97 passed in 2.59s**. 속도 1e30/inf에서 limited reward가 100으로 포화되는 기존 테스트를 포함한다. 물리 시뮬레이션·재학습·GPU 오류 순간 재현은 실행하지 않았다. 원본 로그에는 step별 reward/obs extrema, KL, gradient, minibatch, 예외 순간 dump가 없어 최초 원인과 std 손상 형태는 미확정이다.

문서 검사: 변경 Markdown 2개 수식 검사와 `git diff --check` 통과. `python 00_guidelines/scripts/check_document_links.py --check-external`은 기존 문서의 누락된 TEMP 로그 3경로와 DexTouch PDF 1경로 때문에 실패했으며 새 문서의 링크 오류는 보고되지 않았다.
