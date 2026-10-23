# Renewal Tactile v1 지수 속도 페널티

> 현재 두 v1 환경은 삭제됐다. 당시 실행 기록이며 현행 환경과 실행 방법은 [촉각 v0 통합·v1 삭제 기록](2026-10-16_tactile_v0_exponential_cleanup.md)을 따른다.

> 후속 사용자 정정: 지수 비용을 OSC Renewal v0와 Dex Renewal v0에 직접 적용하고 파생 환경에 상속하도록 변경했다. 이 문서는 최초 v1 추가 시점의 기록이며 현재 적용 범위는 [부모 적용 정정 기록](2026-10-16_renewal_exponential_parent_scope.md)을 따른다.

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md)

기준일: 2026-10-16. Workspace 기준 commit은 `38920288f1b5748c046eb4a5965c28a3f851d187`, 문서 저장소 기준은 `d0ef00c70df2ce33bfcb9cd4132617f52776725b`다. 작업 시작 시 상위 저장소의 문서 submodule 참조 변경을 보존했다. 이번 변경은 미커밋 상태다.

## 요청과 상속

사용자는 두 촉각 Renewal v0를 각각 상속하는 v1을 요청했다. 변경 범위는 `pushing_speed`, `arm_speed_excess`의 수식과 음수 계수이며 기존 함수를 보존하고 새 함수를 추가한다.

| Gym ID | 직접 상속 | 등록 PPO Cfg |
| --- | --- | --- |
| `Isaac-Inspire-Tactile-Sweep-Omni-Renewal-v1` | `InspireTactileSweepOmniRenewalV1EnvCfg(InspireTactileSweepOmniRenewalEnvCfg)` | `InspireTactileSweepOmniRenewalV1PPORunnerCfg` |
| `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1` | `InspireDexTactileSweepOmniRenewalV1EnvCfg(InspireDexTactileSweepOmniRenewalEnvCfg)` | `InspireDexTactileSweepOmniRenewalV1PPORunnerCfg` |

양쪽 실행 클래스는 `InspireSweepEnv(ManagerBasedRLEnv)`다. 당시 `tactile_omni_renewal_v1_env_cfg.py`(후속 정리에서 삭제)의 두 rewards Cfg는 각각 `OmniRenewalRewardsCfg`, `DexOmniRenewalRewardsCfg`를 상속하여 두 항만 교체한다. 환경 Cfg는 각각 v0를 직접 상속한다. [PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/sweep_omni_renewal_ppo_cfg.py)은 각 v0 runner를 상속하고 실험 이름에 `_v1`을 추가한다. 기본 로그 폴더는 `logs/rsl_rl/inspire_tactile_sweep_omni_renewal_v1`, `logs/rsl_rl/inspire_dex_tactile_sweep_omni_renewal_v1`다.

## 수식 계약

[goal_rewards.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_rewards.py)에 `exponential_pushing_speed_cost`, `exponential_joint_speed_cost`를 추가했다. 기존 `pushing_speed_cost`, `joint_speed_cost`의 본문과 v0 환경 설정은 변경하지 않았다.

두 새 함수는 양의 비용 `expm1(2 * max(x - t, 0)) / 2`를 반환한다. 두 RewardTerm의 weight는 **-1.0**이며 가중치 적용 후 식은 다음과 같다.

```math
r(x)=-\frac{\exp(2\max(x-t,0))-1}{2}.
```

`x <= t`에서 0이고 초과하면 지수적으로 감소한다. `torch.expm1`로 임계값 바로 위의 작은 차이도 계산한다. reference_speed 정규화, 포화 상한, 기존 가중치 -5.0 또는 -0.1의 중복 곱셈은 없다.

| 항 | x | 임계값 t | weight |
| --- | --- | --- | --- |
| pushing_speed | env.target_id로 선택한 물체의 월드 3D 선속도 norm | 0.3 m/s | -1.0 |
| arm_speed_excess | `_arm()`의 6개 관절 `velocity.abs()` 중 최댓값 | 1.0 rad/s | -1.0 |

Arm의 속도 축약은 기존 `joint_speed_cost` 및 `arm_velocity` 종료와 같은 최대 절대 속도다. 손가락이나 다른 관절의 속도는 포함하지 않으며, Arm 여러 관절의 비용을 합산하지 않는다. 음수 관절 속도도 절댓값으로 동일하게 취급한다.

RewardManager는 기존처럼 가중치와 step_dt를 각각 한 번 적용한다. 함수 내에서 dt를 보정하지 않으므로 위 식은 step_dt 적용 전 값이며, 한 policy step의 기여는 위 값 ×0.02s다. 물체 0.5m/s에서 약 -0.245912 / step -0.004918, Arm 최대 절대 속도 2.0rad/s에서 약 -3.194528 / step -0.063891이다.

관측 57D, 촉각 17개 0/1, Action 8D, 제어·물성·중력·reset·이벤트·나머지 보상과 종료는 각 v0와 같다. 네 운동 페널티의 raw 제곱합 함수와 계수도 유지한다. 종료 기준은 대상 물체 3D 속도 >0.8m/s, Arm 관절 중 하나라도 절대 속도 >5.0rad/s다. 비용 시작 임계값 0.3/1.0과 종료 기준 0.8/5.0을 구분한다.

## 실제 검증

다음 CPU 명령을 실제 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_exponential_speed_costs.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_v1_configuration.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests
```

선별 검사 **55 passed**, 전체 패키지 **217 passed, 2 failed**다. 신규 12개 검사는 모두 통과했다. math.expm1 기준 수치, 임계값 이하·동일·미세 초과, 대상 물체 선택과 3D 방향, Arm 음수 속도·최댓값·관절 선택, 비정상 임계값, weight와 step_dt, 상속·인스턴스 격리, 보상 두 항 외 전체 설정 동등성, 등록·PPO를 확인한다. 기존 제곱 수식 검사도 통과했다.

두 기존 실패는 [v0 개발 로그](2026-10-16_tactile_renewal_environments.md)에 기록된 것과 같다. `test_renewal_composes_complete_v4_behavior_without_v4_inheritance`는 현재 Renewal과 V4가 완전히 같다고 가정하고, `test_dex_renewal_changes_exactly_the_two_dex_reward_terms`는 현재 -0.1인 부모의 arm_speed_excess.weight를 -0.03으로 가정한다. 이번 작업에서 기존 부모 설정이나 검사는 수정하지 않았다.

다음 GPU 명령도 실제 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  TERM=xterm PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Tactile-Sweep-Omni-Renewal-v1 \
  --num_envs 8 --max_iterations 1 \
  --experiment_name tactile_renewal_v1_smoke --run_name sweep --headless

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  TERM=xterm PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1 \
  --num_envs 8 --max_iterations 1 \
  --experiment_name tactile_renewal_v1_smoke --run_name dex --headless
```

RTX 3090 / Isaac Sim 5.1에서 양쪽 모두 종료 코드 0으로 PPO 1 iteration을 완료했다. 각 8개 환경 ×36 policy step을 수집했으며 실제 Observation Manager에서 57D, tactile 17D, Action Manager에서 8D를 확인했다. GPU 저장 설정에도 두 새 함수와 weight=-1.0, free_speed=0.3/1.0이 적용됐다. Physics dt 0.01s, policy/render dt 0.02s를 유지했다. 짧은 무작위 정책 실행이므로 종료 비율이나 비용 크기를 학습 성능으로 해석하지 않는다.

산출물은 `logs/rsl_rl/tactile_renewal_v1_smoke/2026-10-16_15-01-35_sweep/`, `2026-10-16_15-02-08_dex/`다. 각 `params/env.yaml`, `params/agent.yaml`, TensorBoard event, `model_0.pt`, `run.log`를 남기고 상위 폴더에 `cpu_tests.log`를 보존했다. 변경 Python 문법·diff 및 변경 Markdown 수식·링크 검사도 수행했다.

학습 명령은 [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)에 있다. 장시간 학습 수렴, 2048개 환경의 처리량과 실물 성능은 미검증이다.
