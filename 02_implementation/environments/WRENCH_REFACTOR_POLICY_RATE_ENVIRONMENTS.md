# Wrench Refactor v0_1 · v1_1 · v2_1 · v3_1

2026-11-06. [개발·검증 기록](../logs/2026-11-06_wrench_refactor_policy_action_rate.md).

## 등록과 직접 상속

최근 대화에서 비교한 Wrench-Refactor v0–v3를 각각 직접 상속한다. 별도 Wrench 계열이나 v3-Test를 부모로 사용하지 않는다.

| Gym ID | EnvCfg → 직접 부모 | PPO → 직접 부모 | experiment_name |
| --- | --- | --- | --- |
| Inspire-Wrench-Refactor-v0_1 | WrenchRefactorV0_1EnvCfg → WrenchRefactorEnvCfg | WrenchRefactorV0_1PPORunnerCfg → WrenchRefactorPPORunnerCfg | inspire_wrench_refactor_v0_1 |
| Inspire-Wrench-Refactor-v1_1 | WrenchRefactorV1_1EnvCfg → WrenchRefactorV1EnvCfg | WrenchRefactorV1_1PPORunnerCfg → WrenchRefactorV1PPORunnerCfg | inspire_wrench_refactor_v1_1 |
| Inspire-Wrench-Refactor-v2_1 | WrenchRefactorV2_1EnvCfg → WrenchRefactorV2EnvCfg | WrenchRefactorV2_1PPORunnerCfg → WrenchRefactorV2PPORunnerCfg | inspire_wrench_refactor_v2_1 |
| Inspire-Wrench-Refactor-v3_1 | WrenchRefactorV3_1EnvCfg → WrenchRefactorV3EnvCfg | WrenchRefactorV3_1PPORunnerCfg → WrenchRefactorV3PPORunnerCfg | inspire_wrench_refactor_v3_1 |

등록은 패키지 `__init__.py`, EnvCfg는 `envs/wrench_refactor_envs.py`, PPO는 `agent/wrench_refactor_ppo_cfg.py`에 있다. runtime은 부모와 동일한 `runtime.wrench_refactor:WrenchRefactorEnv`다.

## 유일한 보상 변경

네 환경 모두 `rewards.robot_action_rate_penalty.func`를 `mdp.reward_functions.wrench_refactor:policy_action_rate_penalty`로 교체한다. term 이름·순서·weight −1·params는 보존한다.

```python
arm_delta = action[:, :6] - previous_action[:, :6]
hand_delta = action[:, -2:].clamp(0., 1.) - previous_action[:, -2:].clamp(0., 1.)
cost = 0.03 * arm_delta.square().sum(-1) + 0.03 * hand_delta.square().sum(-1)
```

Arm은 OSC에 들어가기 전 raw 정책 출력의 위치XYZ3축·RPY회전3축 변화다. 물리 명령을 위치0.03m·회전0.15rad 배율로 정규화하면 동일한 raw 공간이므로 추가 배율은 적용하지 않는다. 위치·회전 계수는 각각0.03으로 같고 합산 cap100은 제거한다. Hand는 부모의 openness0–1 clamp와 계수0.03을 보존한다. action 자체의 크기 제한을 추가하거나 제거하는 변경은 아니다.

이 함수는 action_manager의 현재/이전 정책 action을 읽는 stateless callable이다. reset은 기존 action_manager의 history reset을 따른다. torque history를 사용하지 않는다. 비용은 양수이며 RewardManager에서 weight−1×정책dt0.02초가 적용된다. action 변화 비용이고 action 크기·wrist3 속도 직접 비용은 아니다.

## 보존되는 부모 계약

- [v0](WRENCH_REFACTOR_V0_ENVIRONMENT.md), [v1](WRENCH_REFACTOR_V1_ENVIRONMENT.md), [v2](WRENCH_REFACTOR_V2_ENVIRONMENT.md), [v3](WRENCH_REFACTOR_V3_ENVIRONMENT.md)의 모든 다른 설정과 동작을 직접 상속한다.
- v0_1/v1_1/v2_1은 root-frame OSC, v3_1은 EEF task-space OSC다. v1의 contact-gated distance 및 별도접촉보상제거, v2/v3의 누적변위cosine distance를 유지한다.
- 목표 방향 양쪽 분포·거리6–12cm·금지각 커리큘럼을 유지한다. v3-Test의 왼쪽전용 및 Joint Velocity 종료 해제를 상속하지 않는다. Arm 속도 종료3rad/s는 네 환경 모두 활성이다.
- Scene17물체·오른손USD/물성·reset·Actor/Critic74+64·8D action·goal command·성공/실패/timeout·모든 다른 reward/커리큘럼·PPO 수치는 부모와 동일하다. 목표 판정 경계도 유지한다.
- 기존 부모와 v3-Test의 임시 print는 변경하지 않는다. 새 환경에는 v3-Test 전용 OSC/종료/비교 print가 활성화되지 않는다.

## 실행

Workspace 루트에서 Isaac Lab conda 환경을 활성화하고 실행한다. 네 명령은 각 환경을 별도로 학습하는 예시이며 이번 구현에서 학습을 수행한 것은 아니다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-v0_1 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-v1_1 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-v2_1 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-v3_1 --num_envs 2048 --headless
```

기존 checkpoint를 play하는 경우 관측·정책 구조는 유지되지만, 후보 보상으로 새로 학습한 정책은 아니다. 기존 paired play에서 같은0.03 계수의 후보 비용은 기존보다 훨씬 컸다. 사용자 요청에 따라 계수는 조정하지 않고 cap만 제거했으며 학습 성능은 미검증이다.
