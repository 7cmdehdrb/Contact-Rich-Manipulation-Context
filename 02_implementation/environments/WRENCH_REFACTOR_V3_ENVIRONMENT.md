# Inspire-Wrench-Refactor-v3

2026-11-06. [v2 부모 계약](WRENCH_REFACTOR_V2_ENVIRONMENT.md) · [v0 전체 계약](WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [개발·검증](../logs/2026-11-06_wrench_refactor_v2_fix_v3.md).

## 상속과 최종 차이

`WrenchRefactorV3EnvCfg(WrenchRefactorV2EnvCfg)`는 v2를 직접 상속한다. v2는 v0의 별도 접촉 유지 보상과 weight5 거리 보상을 보존하면서 거리 항에 시작점 기준 누적 변위 signed cosine을 곱하는 버전이다. v3는 이13개 보상 및 모든 관측·Scene·Command·Event·종료·커리큘럼을 유지하고 Arm Action class_type만 `WrenchRefactorOSCAction`으로 바꾼다. PPO는 v2 직접 상속이며 experiment_name만 `inspire_wrench_refactor_v3`다.

## EEF task space

현재 offset EEF pose를 매 정책 step 처음 task frame으로 복사하여 두 물리 substep 동안 고정한다. 위치 action은 현재 EEF 축에서 해석한다. EEF가 root Z축으로90도 회전해 있으면 +X 명령은 root +Y 방향이다. 회전 delta도 EEF task frame 기준이다. 이 task frame과 제어점은 `axia80_link` offset (0,0,0.1427), quaternion (0.5,-0.5,-0.5,-0.5)를 사용한다.

이는 이전 Refactor에서 사용했던 구현을 다시 선택하는 것이다. 해당 클래스의 offset Jacobian 보정(lever arm을 root로 회전, 각속도 Jacobian은 root축 유지)과 link-origin 속도 + omega×offset 보정도 함께 적용한다. v2의 root-frame OSC는 Final·Revision 공통 구현이다. gain·action scale·주기·effort limit은 같다: 위치 stiffness100·회전50, damping ratio1, position_scale0.03m, orientation_scale0.15rad, 정책0.02초/물리0.01초, full inertial decoupling·중력 보상 활성.

오른손 USD·초기 Wrist3−π/2·Hand mapping·790g 질량·촉각34·F/T·EEF 관측은 그대로다. Actor/Critic raw74+장애물64, encoder64→32→16, MLP입력90을 유지한다. 목표 최소5cm·iteration0 ±X반각30도·방위/조건부거리 균등도 동일하다. 거리 항에는 접촉 gate가 없고 EEF14cm 제한은 적용한다. 별도 접촉 유지 보상은 v0과 동일하다.

## 코드와 실행

EnvCfg는 `envs/wrench_refactor_envs.py::WrenchRefactorV3EnvCfg`, OSC는 `mdp/action_functions/wrench_refactor.py::WrenchRefactorOSCAction`, PPO는 `agent/wrench_refactor_ppo_cfg.py::WrenchRefactorV3PPORunnerCfg`다. runtime은 공통 `WrenchRefactorEnv`이며 Gym ID는 `Inspire-Wrench-Refactor-v3`다.

Workspace 루트에서 실행한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-v3 --num_envs 2048 --device cuda:0 --headless
```

로그는 `logs/rsl_rl/inspire_wrench_refactor_v3/`이다. 기존 root-frame 정책 checkpoint는 action 의미가 달라진다는 점을 고려해야 한다. 이번 작업에서 RL 학습은 수행하지 않았다.
