# Inspire-Wrench-Refactor-v3

2026-11-06: 임시 파생 **Inspire-Wrench-Refactor-v3-Test**는 왼쪽(world −Y) 반평면에만 목표를 생성한다. 거리6–12cm·금지각 커리큘럼·관측·제어·보상은 v3를 보존한다. [파생 계약·실행·검증](../logs/2026-11-06_wrench_refactor_v3_test_left.md).

2026-11-06 기반 변경 상속: 목표 중심은 물체 시작점에서 **6–12cm** 범위만 사용한다. 방향 금지각 커리큘럼은 유지한다. [영역·검증](../logs/2026-11-06_wrench_refactor_goal_annulus.md).

2026-11-06. [v2 부모 계약](WRENCH_REFACTOR_V2_ENVIRONMENT.md) · [v0 전체 계약](WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [개발·검증](../logs/2026-11-06_wrench_refactor_v2_fix_v3.md).

## 상속과 최종 차이

`WrenchRefactorV3EnvCfg(WrenchRefactorV2EnvCfg)`는 v2를 직접 상속한다. v2는 v0의 별도 접촉 유지 보상과 weight5 거리 보상을 보존하면서 거리 항에 시작점 기준 누적 변위 signed cosine을 곱하는 버전이다. v3는 이13개 보상 및 모든 관측·Scene·Command·Event·종료·커리큘럼을 유지하고 Arm Action class_type만 `WrenchRefactorOSCAction`으로 바꾼다. PPO는 v2 직접 상속이며 experiment_name만 `inspire_wrench_refactor_v3`다.

## EEF task space

현재 offset EEF pose를 매 정책 step 처음 task frame으로 복사하여 두 물리 substep 동안 고정한다. 위치 action은 현재 EEF 축에서 해석한다. EEF가 root Z축으로90도 회전해 있으면 +X 명령은 root +Y 방향이다. 회전 delta도 EEF task frame 기준이다. 이 task frame과 제어점은 `axia80_link` offset (0,0,0.1427), quaternion (0.5,-0.5,-0.5,-0.5)를 사용한다.

이는 이전 Refactor에서 사용했던 구현을 다시 선택하는 것이다. 해당 클래스의 offset Jacobian 보정(lever arm을 root로 회전, 각속도 Jacobian은 root축 유지)과 link-origin 속도 + omega×offset 보정도 함께 적용한다. v2의 root-frame OSC는 Final·Revision 공통 구현이다. gain·action scale·주기·effort limit은 같다: 위치 stiffness100·회전50, damping ratio1, position_scale0.03m, orientation_scale0.15rad, 정책0.02초/물리0.01초, full inertial decoupling·중력 보상 활성.

오른손 USD·초기 Wrist3−π/2·Hand mapping·790g 질량·촉각34·F/T·EEF 관측은 그대로다. Actor/Critic raw74+장애물64, encoder64→32→16, MLP입력90을 유지한다. 목표 최소6cm·iteration0 ±X반각30도·방위/조건부거리 균등도 동일하다. 거리 항에는 접촉 gate가 없고 EEF14cm 제한은 적용한다. 별도 접촉 유지 보상은 v0과 동일하다.

## 코드와 실행

EnvCfg는 `envs/wrench_refactor_envs.py::WrenchRefactorV3EnvCfg`, OSC는 `mdp/action_functions/wrench_refactor.py::WrenchRefactorOSCAction`, PPO는 `agent/wrench_refactor_ppo_cfg.py::WrenchRefactorV3PPORunnerCfg`다. runtime은 공통 `WrenchRefactorEnv`이며 Gym ID는 `Inspire-Wrench-Refactor-v3`다.

Workspace 루트에서 실행한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-v3 --num_envs 2048 --device cuda:0 --headless
```

로그는 `logs/rsl_rl/inspire_wrench_refactor_v3/`이다. 기존 root-frame 정책 checkpoint는 action 의미가 달라진다는 점을 고려해야 한다. 이번 작업에서 RL 학습은 수행하지 않았다.

임시 v3-Test는 종료 시 `[Wrench-Refactor-v3-Test termination]` 접두사로 env ID·episode step·발동한 종료 term 전체를 출력한다. timeout과 성공 종료도 포함하며, 기존 v3는 출력하지 않는다. 이미 실행 중이면 play를 재시작한다.

v3-Test는 매 제어step 종료 판정 시점의 Arm 실제 관절속도6축도 `[Wrench-Refactor-v3-Test joint_velocity]`로 출력한다. 모든 env에 대해 관절명·부호 있는 rad/s·threshold3·초과 여부를 표시한다. 자동reset 전 속도이며 기존 종료 판정은 보존한다.

2026-11-06 최신 임시 설정: **v3-Test의 arm_joint_velocity 종료를 None으로 비활성화**했다. 기존 v3의 종료와 물리 속도 제한은 유지한다.6축 실시간 출력은 runtime으로 옮겨 유지하며,3rad/s 초과는 참고값이고 `termination_enabled=False`로 표시한다. 다른 종료 원인 출력도 유지한다.

최신 출력: v3-Test의6축 속도 목록을 wrist3 전용 `last_pos`, `current_pos`, `dt`, `delta_pos/dt`, `joint_vel` 비교로 교체했다. dt=정책주기0.02초이며 위치 차분은 구간 평균, joint_vel은 구간 끝 순간 속도다. 자동reset 이전에 종료 샘플을 출력하고 다음step은 reset 이후 위치를 기준으로 한다.

최신 계측: wrist3 위치/속도 비교 print를 제거하고 **OSC 전체 입출력 JSON**으로 교체했다. `[Wrench-Refactor-v3-Test OSC]`로 모든 env의 매물리substep(0.01초) action·목표·현재 상태·Jacobian·질량행렬·중력·gain·raw/제한후토크·제한값·포화 여부를 출력한다. 종료 원인 print와 속도 종료 비활성화는 유지한다. [필드·검증](../logs/2026-11-06_wrench_refactor_v3_test_left.md).

v3-Test는 추가로 `[Wrench-Refactor-v3-Test action_penalty]`에서 기존 정규화토크 변화 비용과 후보raw정책출력 변화 비용(위치/회전 분리)을 같은step에 출력한다. 공통계수0.03·Hand비용을 유지한 비교이며 실제 반환reward는 기존 방식이다. [실제play비교](../logs/2026-11-06_wrench_refactor_v3_test_left.md).
