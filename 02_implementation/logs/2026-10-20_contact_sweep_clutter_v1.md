# Contact Sweep Clutter v1: 초기 타겟 관측과 보상 균형

> 2026-10-21 로그 정리 후 참조 run의 현재 위치는 `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-v0/2026-10-20_14-04-31`다. 아래 당시 경로·실행 명령은 수행 이력으로 보존한다. [정리 기록](2026-10-21_temp_training_log_cleanup.md).

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-v1--2026-10-20) · [부모 v0 구현](2026-10-20_contact_sweep_clutter.md) · [패키지 계약](../../../../src/inspire_sweep_baseline/README.md#contact-sweep-clutter-v1--초기-타겟-관측과-보상-균형)

기준일: 2026-10-20. 사용자 요청에 따라 Clutter v0를 상속하는 v1을 구현했다. 초기 타겟 관측, Critic 전용 현재 타겟 위치, 목표 유지·접촉·장애물 이동 비용을 추가하고 기존 학습 로그로 초기 계수를 정했다. 아래 가정별 보상 비중은 v1 장기 학습 성능과 구분한다.

## 기준 코드와 변경 범위

작업 시작 workspace commit은 `b8adfaaee54d8f2dad9b792e9b90085d2fd46fba`, 문서 submodule commit은 `23bcface86c3439452f2444db42b5c8718765132`다. 시작부터 존재한 상위 저장소의 submodule revision 차이와 untracked `Isaac-Inspire-Contact-Sweep-Clutter-v0.ini`는 보존했다. 이 기록의 구현은 해당 commit 위의 작업트리 변경이며 새 commit·원격 반영 완료를 의미하지 않는다.

| 구분 | v1 구현 |
| --- | --- |
| Gym task | `Isaac-Inspire-Contact-Sweep-Clutter-v1` |
| Runtime | `ContactSweepClutterV1Env` → `ContactSweepClutterEnv` |
| 환경 설정 | `ContactSweepClutterV1EnvCfg` → `ContactSweepClutterEnvCfg` |
| 관측·보상 설정 | v0의 각 Manager Cfg를 상속한 v1 Cfg |
| PPO | `ContactSweepClutterV1PPORunnerCfg` → `ContactSweepClutterPPORunnerCfg` |
| Critic 모델 | `PrivilegedObstacleEncoderModel` → `ObstacleEncoderModel` |
| 로그 | `logs/rsl_rl/inspire_contact_sweep_clutter_v1` |

주요 코드는 [v1 패키지](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/contact_sweep_clutter_envs.py)와 [보상 비교 스크립트](../../../../src/inspire_sweep_baseline/scripts/analyze_clutter_rewards.py)다. v0 등록·설정과 기존 checkpoint는 별도의 기준선이다.

## 관측·reset 계약

Actor의 기존 `policy.target_obs_state` 3D를 `InitialObjectPositionInRoot`로 교체한다. Command가 타겟 배치 뒤 저장한 `target_init_state_w`의 link 원점을 robot-root frame으로 변환해 episode 동안 고정한다. 초기 측정 오차는 각 좌표에 reset당 한 번 샘플링한 Uniform ±0.01 m이며 per-step 새 noise는 0이다. ObservationManager가 CommandManager보다 먼저 reset되는 순서를 고려해 최초 관측 때 새 snapshot을 읽는다.

Critic 전용 `privileged.target_position`은 현재 타겟 link 원점의 robot-root 좌표 3D다. 관측 오차를 추가하지 않고 매 step 실제 위치를 읽는다. [Initial Privileged PPO](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/sweep_ppo_cfg.py)의 Actor/Critic 라우팅 원칙을 참조했으며 추가 정보는 위치 3D다.

| 모델 | rollout의 원시 입력 | 네트워크 입력 |
| --- | --- | --- |
| Actor | policy 57D + obstacles 40D = 97D | policy 57D + 장애물 latent 16D = 73D |
| Critic | policy 57D + privileged 3D + obstacles 40D = 100D | policy 57D + 현재 타겟 3D + 장애물 latent 16D = 76D |

장애물 초기 관측은 부모의 `[HEADER,x,y,z] × 10`, 실제 3개·더미 7개, robot-root frame과 reset당 ±1 cm noise를 상속한다. 각 네트워크는 별도 `40 → 32(ReLU) → 16` 인코더를 PPO로 학습한다. Actor JIT/ONNX 입력은 초기 타겟을 포함한 원시 97D이며 현재 타겟 좌표를 요구하지 않는다.

장애물 이동 비용은 관측 snapshot을 사용하지 않는다. Runtime이 전체 reset 배치 완료 뒤 `_initial_object_positions_w`에 모든 실제 물체의 **노이즈 없는 월드 XYZ**를 저장한다. 부분 reset에서는 선택한 환경만, 자동 reset에서는 새 episode 환경만 갱신한다. 이 정확한 snapshot과 노이즈가 섞인 Actor 초기 관측을 분리한다.

촉각은 기존 17개 bit의 접촉 판정을 공유한다. 보상 계산이 관측 계산보다 먼저 실행되므로 직전 관측 버퍼를 읽지 않고 현재 sensor 상태를 읽는다. 같은 제어 step의 두 보상과 관측은 마지막 physics step의 동일한 판독값을 사용하고 reset 때 cache를 무효화한다. 접촉 물체 ID를 Actor에 추가하지 않는다.

## 보상식과 계수

정책 주기는 `dt=0.02 s`, 최대 episode 길이는 10초다. RewardManager는 각 term에 `weight × raw × dt`를 적용한다. 기존 `DexReachProgress`와 `DexPlanarGoalProgress`는 raw에서 dt를 상쇄하므로 해당 계수는 거리 개선량 1 m당 보상이다.

| 항목 | 계수 | 조건·단위 |
| --- | ---: | --- |
| `reaching` | 30.0 | 기존 최선 접근 거리 개선량, reward/m |
| `goal_distance` | 100.0 | 기존 최선 목표 XY 거리 개선량, reward/m; v0은 94.0 |
| `goal_hold` | 0.9 | 월드 XY 목표 반경 0.01 m 이내, reward/s |
| `contact_any` | 0.16 | 하나 이상 ON, reward/s |
| `contact_count` | 0.16 | `min(ON 개수,5)/5`, 최대 reward/s |
| `obstacle_displacement` | −5.0 | 타겟 제외 XYZ 이동 제곱합, raw 상한 0.04 m² |

현재 타겟 위치를 $p_T$, 목표 위치를 $g$, ON tactile 수를 $n$, 장애물 위치·초기 위치를 $p_i$·$p_{i,0}$라 하면 신규 항의 가중 보상률은 다음과 같다.

```math
r_{\mathrm{hold}} = 0.9\,\mathbf{1}_{\{\|p_{T,xy}-g_{xy}\|_2\leq0.01\}}.
```

```math
r_{\mathrm{contact}} = 0.16\,\mathbf{1}_{\{n>0\}} + 0.16\,\frac{\min(n,5)}{5}.
```

```math
r_{\mathrm{obstacle}} = -5\,\min\left(\sum_{i\ne T}\|p_i-p_{i,0}\|_2^2,\ 0.04\right).
```

XY는 월드 Z를 수직으로 둔 수평면이다. Goal 유지 조건은 타겟 높이·속도·선반 기울기·과거 체류 시간에 의존하지 않는다. 요청의 “증가하는 보상”은 조건 만족 시간에 비례해 누적 보상이 증가하는 것으로 구현했다. 순간 보상률은 +0.9/초로 일정하며 5초에 +4.5다. 연속 유지 시간에 따라 보상률 자체가 증가하는 ramp나 일회성 성공 보너스는 추가하지 않았다.

Contact 두 항의 최대값은 각각 +0.16/초다. 5개 이상 접촉을 7초 유지하면 각각 +1.12, 합 +2.24다. 개수는 물체·손가락 수가 아닌 ON tactile 채널 수이며 6개 이상도 5개와 같다. 부모가 제공하는 동일한 tactile 판정을 사용하므로 타겟 접촉만으로 제한하지 않는다.

장애물 비용은 **XYZ 전체 거리**의 제곱합이다. 매 환경의 `target_id`를 제외한 실제 물체만 합산하고, 더미 관측 슬롯과 관측 noise는 사용하지 않는다. 2개가 각각 10 cm 떨어진 상태면 raw 0.02 m², 10초 누적 −1.0이다. 전체 raw를 0.04 m²로 제한하여 최대 −0.2/초·−2.0/10초이며 비유한 비용도 상한으로 포화시킨다. 이 상한은 해당 보상 출력의 폭주를 제한하며 모든 PPO 오류를 방지한다는 보장은 아니다.

`pushing_speed.free_speed`를 0.2→1.0 m/s, `arm_speed_excess.free_speed`를 1.0→0.5 rad/s로 변경했다. 두 항의 기존 가중치 −2/−1과 함수 출력 상한 100은 유지한다. Arm/Hand action rate·joint velocity는 로컬 `goal_rewards.action_rate_l2`·`joint_vel_l2`, raw 제곱합·출력 상한·분리된 네 항을 유지하고 계수도 −0.03/−0.03/−0.03/−0.01이다.

## v0 로그를 이용한 보정

원본은 workspace `logs/TEMP/2026-10-20_14-04-31`의 `events.out.tfevents.1792472685.ssu-System-Product-Name.3898329.0`와 `params/env.yaml`이다. 전체 iteration은 0–9654, 총 9,655개이며 마지막 1,000개는 8655–9654다. 모든 보상 scalar의 step 정렬·중복 없음·유한값을 확인했다.

| 측정된 가중 평균 | 전체 | 마지막 1,000개 |
| --- | ---: | ---: |
| Reaching, weight 30 | 0.772235612 | 0.781901242 |
| Goal distance, weight 94 | 0.719579951 | 0.800755456 |
| 기존 페널티 합 | −0.230437437 | −0.226081236 |

이는 TensorBoard `Episode_Reward/*`의 iteration별 단순 평균이다. 각 값은 가중 보상 누적값을 **설정된 최대 episode 시간 10초**로 나눈 값이며, 실제 episode 길이로 나눈 값이나 모든 episode에 같은 가중치를 준 평균은 아니다.

양의 목표 비중 35+35+20+10이 100%이므로 보정 분모는 **Reaching·Goal distance·Goal 유지·Contact 네 양의 그룹 합**으로 정의했다. 기존 페널티와 신규 장애물 비용은 별도 비중으로 비교한다. 순보상 또는 모든 항 절댓값 합을 분모로 한 비중과 혼용하지 않는다.

기존 progress 측정값을 계수에 비례해 재가중하고 Goal 5초·5개 접촉 7초를 가정했다. 전체 로그의 10초 기준 환산은 Reaching +7.722356, Goal distance +7.655106, Goal 유지 +4.5, Contact +2.24, 합 +22.117462다.

| 양의 그룹 비중 | 전체 로그 기반 | 마지막 1,000개 기반 |
| --- | ---: | ---: |
| Reaching | 34.9152% | 33.8813% |
| Goal distance | 34.6111% | 36.9130% |
| Goal 유지 | 20.3459% | 19.4994% |
| Contact 합 | 10.1277% | 9.7063% |

두 contact 항은 전체 로그 기준 각각 5.0639%다. 장애물 2개의 10 cm·10초 시나리오 −1.0은 양의 합 대비 4.5213%, 마지막 1,000개 기준 4.3332%로 요청한 10% 이내다.

이 계산은 **새 행동을 시뮬레이션한 결과가 아니다**. 초기 위치 Actor와 속도 비용 변경 때문에 progress 분포·체류·접촉 시간이 달라질 수 있다. v0 scalar만으로 신규 항의 실제 값을 복원할 수 없으며, 새 v1 run의 측정 비중을 비교해 후속 계수를 판단한다.

## 실행과 재현

모든 명령의 작업 디렉터리는 workspace `/home/min/7cmdehdrb/grad`다. 향후 학습·재생 명령:

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-v1 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-v1 --num_envs 1 \
  --checkpoint "<clutter-v1-checkpoint.pt>" --real-time
```

부모의 타겟·목표·장애물 배치, 물성, Arm 6D+Hand 2D Joint Position action, 0.02초 제어와 10초 timeout을 상속한다. Goal 도달 성공 종료는 추가하지 않는다. 기존 물체 낙하·전도, 선반 충돌·변위, Arm 속도 종료와 **`push_fast` 0.8 m/s** 종료도 유지한다. 보상 free speed 1.0 m/s는 실패 종료 속도를 변경하지 않는다.

실제로 실행한 보상 분석 명령:

```bash
python src/inspire_sweep_baseline/scripts/analyze_clutter_rewards.py \
  --log-dir logs/TEMP/2026-10-20_14-04-31 \
  --output /tmp/clutter_v1_calibration_all.json

python src/inspire_sweep_baseline/scripts/analyze_clutter_rewards.py \
  --log-dir logs/TEMP/2026-10-20_14-04-31 --last-n 1000 \
  --output /tmp/clutter_v1_calibration_last1000.json
```

두 명령 모두 종료 코드 0이었다. 분석기는 simulator import 없이 TensorBoard scalar 전체를 읽고, 안전한 숫자 필드 추출로 저장 YAML의 계수·episode 시간을 확인한다. `--last-n 0`은 전체를 사용하며 `--output` 없이 stdout JSON만 받을 수도 있다. v1 run에 `goal_hold`, `contact_any`, `contact_count`가 있으면 실제 네 그룹 비중을 추가 출력한다. Synthetic TensorBoard 입력으로 v1 그룹 집계·tail 선택과 중복·step 불일치·비유한 값·음수 `--last-n` 거부를 확인했고 `py_compile`도 통과했다.

원시 결과 보관본: [전체 로그 보정 JSON](../../03_assets/artifacts/contact_sweep_clutter_v1_2026-10-20/calibration_all.json), [마지막 1,000개 보정 JSON](../../03_assets/artifacts/contact_sweep_clutter_v1_2026-10-20/calibration_last1000.json).

## 실제 검증과 미확인 범위

최종 활성 패키지 CPU 회귀는 다음 명령으로 **320 passed, 2 warnings, 13.96초**였다. 경고 2개는 Torch ONNX 내부 deprecation이다. 앞서 보상·reset·설정·모델 관련 45개와 모델 라우팅 관련 18개를 별도로 실행했으며, 중복 집합이므로 최종 320개에 더하지 않는다. [CPU 출력](../../03_assets/artifacts/contact_sweep_clutter_v1_2026-10-20/cpu.log).

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests \
  > outputs/contact_sweep_clutter_v1_2026-10-20/cpu.log 2>&1
```

최초 전체 CPU 실행에서는 모든 task가 단일 runtime을 쓴다고 가정한 기존 등록 검사가 1개 실패했다. 해당 가정은 기존 Contact v0의 독립 runtime에도 맞지 않았다. 환경 계열별 명시적 runtime mapping으로 검사 계약을 고친 뒤 최종 320개가 통과했다.

첫 GPU smoke run `2026-10-20_20-34-46_smoke_clutter_v1`에서는 ObservationManager에 없는 term getter를 호출해 실패했다. 실제 매니저가 해석한 `manager.cfg.policy.tactile`의 callable을 사용하도록 수정했다. 아래 수정 후 재실행은 모두 종료 코드 0이다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/bin/conda run --no-capture-output -n env_isaaclab \
  python -u src/inspire_sweep_baseline/tests/_clutter_v1_lifecycle_probe.py \
  --headless --num_envs 4 \
  --output outputs/contact_sweep_clutter_v1_2026-10-20/lifecycle.json \
  > outputs/contact_sweep_clutter_v1_2026-10-20/lifecycle.log 2>&1

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/bin/conda run --no-capture-output -n env_isaaclab \
  python -u src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-v1 --num_envs 8 \
  --max_iterations 2 --run_name smoke_clutter_v1 --headless \
  > outputs/contact_sweep_clutter_v1_2026-10-20/train_smoke.log 2>&1
```

Lifecycle은 seed 42, 4환경, 일반 제어 20 step과 상태를 조작한 계약 검사를 실행했다. 제어 step당 physics step은 2회다. [Lifecycle JSON](../../03_assets/artifacts/contact_sweep_clutter_v1_2026-10-20/lifecycle.json), [stdout](../../03_assets/artifacts/contact_sweep_clutter_v1_2026-10-20/lifecycle.log)에 다음 결과를 보관했다.

- 관측 `policy [4,57]`, `obstacles [4,40]`, `privileged [4,3]`와 Actor 초기 타겟 고정·Critic 현재 타겟 추적을 확인했다. 초기 타겟 관측 오차 최대는 0.0096495748 m였다.
- 목표 XY 조건의 Z 독립성, 타겟 이동의 장애물 비용 제외, 노이즈 없는 초기 XYZ 사용, 부분 reset·timeout 자동 reset의 snapshot 갱신을 확인했다.
- 장애물 2개·10 cm 시나리오 raw는 약 0.02000000887 m², 10초 환산 비용은 약 −1.0000004433이었다. float 오차 범위에서 이론값과 같고 cap 0.04 m²도 확인했다.
- 일반 20 step에서는 양의 tactile 접촉이 없었다. 별도로 실제 장애물과 palm의 접촉을 만들어 parent contact point 4개·활성 tactile 1개를 확인했다. 이때 두 보상률은 약 +0.16/+0.032로 1채널의 기대값과 일치했다. GPU에서 5개 동시 접촉까지 만들지는 않았으며 5개 포화 경계는 CPU 입력 검사로 확인했다.
- v0 설정, 네 운동 페널티, 기존 종료·event 설정의 보존과 현재 tactile 기반 보상을 확인했다.

PPO smoke는 seed 42, 8환경 ×36 step ×2 iteration = **576 transitions**였다. Run은 `logs/rsl_rl/inspire_contact_sweep_clutter_v1/2026-10-20_20-37-27_smoke_clutter_v1`, checkpoint는 `model_0.pt`와 `model_1.pt`다. 두 checkpoint의 모델 tensor와 optimizer 상태가 모두 유한했고, iteration 1의 value loss 223.3433·surrogate loss −0.0230을 확인했다. [학습 stdout](../../03_assets/artifacts/contact_sweep_clutter_v1_2026-10-20/train_smoke.log). 이 수치는 초기화·연결·PPO 업데이트 검증이며 학습 성능 지표로 평가하지 않는다.

같은 분석 스크립트로 v1 smoke의 신규 term이 실제 측정 그룹에 포함됨을 확인했다. [Smoke 보상 분석](../../03_assets/artifacts/contact_sweep_clutter_v1_2026-10-20/smoke_reward_analysis.json). 두 iteration만으로 목표 비중의 달성·수렴을 판단하지 않는다.

문서 저장소에서 `python 00_guidelines/scripts/check_document_links.py --check-external`을 실행했다. 기존 `2026-10-14_omni_immediate_termination.md`의 과거 TEMP run 링크 3건과 `2026-10-15_dex_omni_rewards.md`의 DexTouch PDF 링크 1건이 누락되어 전체 검사는 통과하지 않았다. 이번에 추가한 문서·코드·artifact 링크의 누락은 없었다.

변경 Markdown 7개 수식 검사와 양쪽 저장소의 `git diff --check`가 통과했다. 문서 저장소에서 실행한 수식 검사 명령:

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  01_plan/00_HANDOFF_BRIEF.md 01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md \
  01_plan/04_NEXT_ACTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-20_contact_sweep_clutter_v1.md \
  ../../src/inspire_sweep_baseline/README.md
```

긴 학습, 정책 재생 품질, 목표 유지 성공률, 실제 보상 비중의 수렴, 다중 seed, 수천 환경 처리량과 실물 전이는 이번 짧은 검사로 입증하지 않는다.

## 독립 MDP 설명 문서

사용자 요청에 따라 [Contact Sweep Clutter v1 MDP](../environments/CONTACT_SWEEP_CLUTTER_V1_MDP.md)를 작성하고 구현 문서 목차에 연결했다. 다른 환경과의 관계 설명을 제외하고, 상태 전이 순서에 따라 Actor·Critic 관측, 8D Action의 관절 명령 변환, 14개 보상의 식·계수·시간 적분, reset과 종료 조건을 기술했다. 관측 차원과 보상 설정을 실제 코드 및 저장된 설정과 대조했다.

이번 후속 작업은 문서만 변경했으며 물리 시뮬레이션과 PPO 검사를 다시 실행하지 않았다. 문서 저장소에서 다음 명령을 실행하여 수식 검사와 diff 공백 검사를 통과했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/environments/CONTACT_SWEEP_CLUTTER_V1_MDP.md \
  02_implementation/README.md \
  02_implementation/logs/2026-10-20_contact_sweep_clutter_v1.md
git diff --check
```

`python 00_guidelines/scripts/check_document_links.py --check-external`도 재실행했다. 위에 기록한 기존 누락 링크 4건 때문에 종료 코드 1이었으며, 새 MDP 문서의 링크 오류는 없었다.
