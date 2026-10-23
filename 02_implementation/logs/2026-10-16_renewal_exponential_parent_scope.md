# 지수 속도 비용의 OSC·Dex 부모 적용 정정

> 후속 변경: 일반 촉각 v0에도 지수 비용을 적용하고 두 촉각 v1을 삭제했다. 이 문서는 부모 적용 시점의 기록이며 현재 상태는 [통합·삭제 기록](2026-10-16_tactile_v0_exponential_cleanup.md)을 따른다.

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [최초 v1 구현](2026-10-16_tactile_renewal_v1_exponential.md)

기준일: 2026-10-16. Workspace 기준 commit `38920288f1b5748c046eb4a5965c28a3f851d187`, 문서 저장소 기준 `d0ef00c70df2ce33bfcb9cd4132617f52776725b`다. 앞선 촉각 v1 구현과 미커밋 변경을 보존했다. 이번 작업도 미커밋 상태다.

## 사용자 정정과 적용 범위

지수 속도 비용을 `Isaac-Inspire-Sweep-Omni-Renewal-OSC-v0`와 `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0`에 직접 적용하고 이를 상속하는 모든 환경에 전달한다. 기존 제곱 비용 함수는 유지한다.

공통 `ExponentialSpeedRewardsCfg(OmniRenewalRewardsCfg)`를 [Renewal 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_renewal_envs.py)에 추가했다. 두 보상 항만 교체하며 나머지 rewards는 기존 부모를 상속한다.

| 항 | 함수 | 입력과 임계값 | weight |
| --- | --- | --- | --- |
| pushing_speed | goal_rewards.exponential_pushing_speed_cost | 대상 물체 3D 선속도 norm, free_speed 0.3m/s | -1.0 |
| arm_speed_excess | goal_rewards.exponential_joint_speed_cost | Arm 6개 관절 최대 절대 속도, free_speed 1.0rad/s | -1.0 |

양의 비용은 `expm1(2 * max(x - t, 0)) / 2`다. 임계값 이하에서 0, 초과하면 지수 증가하며 가중치로 음수가 된다. reference_speed 정규화와 상한이 없고 RewardManager의 step_dt 곱셈을 유지한다.

- [OSC 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_renewal_envs.py)의 rewards를 공통 Cfg로 지정했다. 기존 OSC EEF·relative/fixed·stiffness 200·damping ratio 1·scale·Arm actuator 설정은 유지한다.
- [Dex Renewal 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_renewal_envs.py)의 `DexOmniRenewalRewardsCfg`가 공통 Cfg를 상속하게 했다. Dex reaching과 goal_distance는 유지한다.
- Dex Tactile v0는 Dex Renewal의 rewards를 그대로 상속하므로 지수 비용을 적용받는다. Dex Tactile v1도 동일하다.
- 앞선 촉각 v1 등록과 동작을 보존했다. v1 rewards의 중복된 두 항 선언은 제거하고 공통 Cfg 또는 Dex rewards 상속으로 재사용한다. 일반 촉각 v1은 여전히 공통 지수 비용을 사용한다.
- 일반 Sweep Renewal v0와 일반 Tactile v0는 기존 제곱 비용을 유지한다. 두 지정 부모의 종료·reset·물성·센서·관측·나머지 보상은 이번 정정으로 변경하지 않았다. 속도 종료는 물체 >0.8m/s, Arm 관절 절대 속도 >5.0rad/s다.

기존 `pushing_speed_cost`, `joint_speed_cost`, `action_rate_l2`, `joint_vel_l2` 함수 본문은 HEAD와 동일함을 확인했다. 네 필수 운동 페널티 함수와 계수도 유지한다.

## CPU 검증

실제 실행한 관련 검사는 다음과 같다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_exponential_speed_costs.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_v1_configuration.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  -k 'not test_renewal_composes_complete_v4_behavior_without_v4_inheritance'

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests
```

관련 검사 **45 passed, 1 deselected**, 전체 패키지 **219 passed, 1 failed**다. 기존 Renewal/V4 완전 동등성 가정 검사는 이전부터 실패했으며 실제 부모 설정을 보존하여 그대로 남아 있다. 앞선 Dex 검사에서 속도 보상이 기존 계수라고 가정하던 부분은 이번 새 요구사항에 맞춰 지수 함수·공통 Cfg를 검증하도록 변경했다.

OSC·Dex 본체와 실제 등록된 Dex Tactile v0·v1, 추가 테스트용 하위 클래스에서 지수 비용이 상속되는지 확인했다. 두 속도 항 외 설정 동등성, 개별 환경 설정의 변경 격리, 제곱 함수 보존, 기존 운동 페널티, 수치·임계값 검사도 포함한다.

## GPU 실행

다음 명령은 workspace 루트에서 실제 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  TERM=xterm PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Sweep-Omni-Renewal-OSC-v0 \
  --num_envs 8 --max_iterations 1 \
  --experiment_name renewal_exponential_parent_smoke --run_name osc --headless

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  TERM=xterm PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0 \
  --num_envs 8 --max_iterations 1 \
  --experiment_name renewal_exponential_parent_smoke --run_name dex --headless
```

RTX 3090 / Isaac Sim 5.1에서 양쪽 모두 종료 코드 0으로 PPO 1 iteration을 완료했다. 관측 41D·행동 8D와 갱신된 저장 설정을 확인했다. OSC는 토크 제어를 유지한다. 짧은 무작위 정책 실행이므로 종료율이나 보상값을 학습 성능으로 해석하지 않는다.

실행 출력은 workspace의 `logs/rsl_rl/renewal_exponential_parent_smoke/2026-10-16_15-06-14_osc/`、`2026-10-16_15-07-08_dex/`에 있다. 각 `params/env.yaml`、`params/agent.yaml`、TensorBoard event、`model_0.pt`、`run.log`를 저장하고 상위에 `cpu_tests.log`를 저장했다. 변경 Python 문법·diff, 변경 Markdown 수식·링크 검사도 실행했다. 장시간 학습 수렴, 2048개 환경 성능과 실물 성능은 미검증이다.
