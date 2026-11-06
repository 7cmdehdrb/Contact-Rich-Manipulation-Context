# Inspire-Wrench-Refactor-v1

2026-11-06 기반 변경 상속: 목표 중심은 물체 시작점에서 **6–12cm** 범위만 사용한다. 방향 금지각 커리큘럼은 유지한다. [영역·검증](../logs/2026-11-06_wrench_refactor_goal_annulus.md).

2026-11-06 기반 변경 상속: OSC는 Final·Revision과 같은 root-frame 공통 구현이며, 목표 최소 거리는 시작점으로부터6cm다. 오른손 자산·EEF offset은 유지한다. [후속 기록](../logs/2026-11-06_wrench_refactor_root_osc_min_goal.md).

[부모 v0 전체 명세](WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [개발 및 검증 기록](../logs/2026-11-06_wrench_refactor_v1.md)

2026-11-06. `WrenchRefactorV1EnvCfg(WrenchRefactorEnvCfg)`의 직접 상속 환경이다. runtime은 부모의 `WrenchRefactorEnv`, 보상은 `WrenchRefactorV1RewardsCfg(WrenchRefactorRewardsCfg)`를 사용한다. 부모 v0는 보존한다.

## 변경 계약

| 항목 | v0 | v1 |
| --- | --- | --- |
| target_contact | 2-of-3 접촉/목표 내부 인정, count최대10 | term을None으로 비활성화. 유지 보상·count 없음 |
| target_goal_distance | EEF 높이 제한,weight5 | 같은 높이 제한 + 현재step 타겟–손 접촉 필요,weight25 |
| 거리 척도 | .05m | .05m 유지 |
| 활성 보상 수 | 13 | 12 |
| PPO experiment_name | inspire_wrench_refactor_v0 | inspire_wrench_refactor_v1 |

거리 보상의 현재step 조건은 fresh하고 유한한 타겟–손 접촉 합력 크기가0.01N 이상이며, EEF world Z가 초기 선반 표면+0.14m 미만인 것이다. 타겟별 object→hand force matrix의 벡터합을 사용한다. tactile bit의0.05N 임계값이나 노이즈가 포함된 tactile 관측은 사용하지 않는다. 선반·장애물 접촉만으로는 인정되지 않는다.

최근3step 이력,연속접촉 조건,count는 없다. 단 한step 접촉해도 즉시 지급하고,다음step 접촉이 끊기면 즉시0이다. 목표3cm 내부도 접촉이 없으면 거리 보상0이다. 엄밀한 코드는 `contact_gated_goal_distance`이며 기존 `target_contact_below_height`와 `goal_distance_v2`를 재사용한다.

```math
r_{distance,t}=25\exp(-d_{XY,t}/0.05)\,\Delta t\,
\mathbf{1}[\|F_{target-hand,t}\|\ge0.01]\,
\mathbf{1}[z_{EEF,t}<z_{surface,initial}+0.14].
```

위 식에는 센서fresh/finite 조건도 적용한다. 기본dt=.02초에서 최대거리보상은0.5/step이다. 예를 들어거리5cm이고현재접촉·높이조건을만족하면약0.18394/step이다.

## 부모에서 유지하는 계약

전체Scene·reset·목표분포·17물체고정풀·물성·오른손자산·질량·제어·센서·관측·터미네이션·커리큘럼은 부모를 상속한다. Wrist3−π/2,Arm속도종료3rad/s,Hand속도페널티독립구동6축 선택도 포함한다. Actor/Critic의 raw74+장애물64,장애물encoder64→32→16,MLP입력90을 유지한다.

`target_goal_hold`, 최초진입+15,성공+75는 그대로다. 특히 **목표유지 보상에 새 접촉 조건을 추가하지 않았다.** 3초안정유지성공도 기존 거리·속도·실패우선조건을 유지한다. `target_contact` 보상 제거는 촉각관측이나 접촉센서 제거가 아니다.

PPO는 `WrenchRefactorV1PPORunnerCfg(WrenchRefactorPPORunnerCfg)`이며 학습설정은 같고 로그experiment_name만 분리한다.

## 코드 위치와 실행

- 등록: `inspire_sweep_baseline/__init__.py`의 `Inspire-Wrench-Refactor-v1`
- EnvCfg: `envs/wrench_refactor_envs.py::WrenchRefactorV1EnvCfg`
- 보상Cfg: `mdp/rewards/wrench_refactor.py::WrenchRefactorV1RewardsCfg`
- 거리함수: `mdp/reward_functions/wrench_refactor.py::contact_gated_goal_distance`
- PPO: `agent/wrench_refactor_ppo_cfg.py::WrenchRefactorV1PPORunnerCfg`

Workspace 루트에서 실행한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-v1 --num_envs 2048 --device cuda:0 --headless
```

학습 로그는 `logs/rsl_rl/inspire_wrench_refactor_v1/`이다. 이 작업에서는 학습을 실행하지 않았다. 검증 범위는 아래 개발 기록을 따른다.
