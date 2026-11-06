# Inspire-Wrench-Refactor-v2

2026-11-06 기반 변경 상속: 목표 중심은 물체 시작점에서 **6–12cm** 범위만 사용한다. 방향 금지각 커리큘럼은 유지한다. [영역·검증](../logs/2026-11-06_wrench_refactor_goal_annulus.md).

2026-11-06 기반 변경 상속: OSC는 Final·Revision과 같은 root-frame 공통 구현이며, 목표 최소 거리는 시작점으로부터6cm다. 오른손 자산·EEF offset은 유지한다. [후속 기록](../logs/2026-11-06_wrench_refactor_root_osc_min_goal.md).

2026-11-06. [v0 부모 계약](WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [v0 전체 명세](WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [개발 기록](../logs/2026-11-06_wrench_refactor_v2.md).

## 상속과 변경 범위

`Inspire-Wrench-Refactor-v2`는 `WrenchRefactorV2EnvCfg(WrenchRefactorEnvCfg)`로 v0을 직접 상속한다. V2RewardsCfg와 V2PPORunnerCfg도 각각 v0을 직접 상속한다. 사용자 정정으로 기존 v1 기반 구현을 교체했다. runtime은 공통 `WrenchRefactorEnv`다. v0/v1은 수정하지 않는다.

유일한 MDP 변경은 `target_goal_distance` 함수에 시작점 기준 누적 변위 코사인을 곱하는 것이다. weight5, distance_scale0.05m, EEF 높이14cm 제한은 v0과 같다. 거리 항에는 현재 접촉 조건이 없다. 별도 `target_contact` 유지 보상(weight0.1)을 포함하며 활성 보상은13개다. PPO는 experiment_name만 `inspire_wrench_refactor_v2`로 분리한다.

## 거리 보상

월드 XY에서 시작점 p0는 매 reset 직후 runtime이 저장한 `_initial_object_positions_w[env_id,target_id,:2]`다. 현재점 pt는 타겟 object_pos_w, 목표점 g는 `target_goal_pos`다. 부분 reset 때 해당 환경의 시작점만 갱신된다. 환경별 world origin을 포함한 동일 좌표계에서 차이를 취한다.

```math
\mathbf{a}=\mathbf{g}-\mathbf{p}_0,\qquad
\mathbf{b}_t=\mathbf{p}_t-\mathbf{p}_0,
\qquad
c_t=\frac{\mathbf{a}\cdot\mathbf{b}_t}{\|\mathbf{a}\|\|\mathbf{b}_t\|}.
```

```math
r_{distance,t}=5\exp(-\|\mathbf{g}-\mathbf{p}_t\|/0.05)\,c_t\,\Delta t\,
\mathbf{1}[z_{EEF,t}<z_{surface,initial}+0.14].
```

거리 항은 접촉 여부·센서 fresh 여부와 무관하다. 별도 접촉 유지 보상은 v0의2-of-3/count/목표 내부 규칙을 유지한다. 코사인에는 목표3cm 내부 예외가 없다. 두 벡터 중 하나의 길이가1e-8m 이하이거나 계산 결과가 비유한이면0을 반환한다. 코사인은[-1,1]로 제한한다. 별도의 의미 있는 이동 거리 문턱이나 시간 필터는 없다.

| 시작점 기준 두 벡터의 각도 | 코사인 배율 |
| --- | --- |
| 0° | +1 |
| 45° | 약+0.7071 |
| 90° | 0 |
| 135° | 약−0.7071 |
| 180° | −1 |

이는 순간 이동 방향이나 경로 직진도를 직접 평가하지 않는다. 목표 쪽으로 이동한 뒤 조금 후퇴해도 시작점보다 목표 쪽이면 양수이며, 목표를 직선으로 지나쳐도+1이다. 멈춰도 높이 조건을 만족하고 누적 변위가 남아 있으면 보상이 발생한다. 거리 지수항은 현재 목표까지의 거리에 따라 계속 바뀐다. 시작점 근처의 아주 작은 진동에는 코사인도 민감할 수 있다. 음수는 이 거리 항에만 적용되며 전체 보상이 반드시 음수가 되는 것은 아니다.

## 유지되는 구성

Scene·자산·17물체·물성·reset·목표분포(최소6cm)·관측·OSC·Hand·센서·다른12개 보상·터미네이션5개·커리큘럼은 v0의 최종 설정을 상속한다. Actor/Critic raw74와 장애물64, encoder64→32→16, MLP입력90을 유지한다. Hold·최초진입·성공 보상에 코사인이나 새 접촉 조건을 추가하지 않는다.

코드: `mdp/reward_functions/wrench_refactor.py::displacement_cosine_goal_distance`, `mdp/rewards/wrench_refactor.py::WrenchRefactorV2RewardsCfg`, `envs/wrench_refactor_envs.py::WrenchRefactorV2EnvCfg`, `agent/wrench_refactor_ppo_cfg.py::WrenchRefactorV2PPORunnerCfg`. 등록은 패키지 `__init__.py`다.

## 실행

Workspace 루트에서 실행한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-v2 --num_envs 2048 --device cuda:0 --headless
```

학습 로그는 `logs/rsl_rl/inspire_wrench_refactor_v2/`다. 이번 작업에서 학습은 실행하지 않았다. 최신 상속 정정 및 v3 검증은 [후속 개발 기록](../logs/2026-11-06_wrench_refactor_v2_fix_v3.md)을 따른다.
