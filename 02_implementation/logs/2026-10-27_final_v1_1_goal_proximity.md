# Final v1-1 Goal Distance 지수형 근접 보상

[환경 계약·학습 명령](../environments/FINAL_V1_V2_ENVIRONMENTS.md#final-v1-1--goal-distance-지수형-근접-보상) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [로그 목록](README.md)

## 요청과 기준

2026-10-27 사용자 요청: `Isaac-Inspire-Final-v1`을 상속한 v1-1을 만들고, Goal Distance를 목표와 타겟의 월드 XY 거리에 따라 감소하는 `exp(-ad)`형 보상으로 바꾼다. 전체 보상 규모를 크게 바꾸지 않으면서 1cm 이내 접근을 더 유도한다. 사용자가 제시한 run은 workspace `logs/TEMP/2026-10-26_17-11-27`이다. 이 run은 읽기만 했으며 정리·이동·삭제하지 않았다.

| 저장소 | 작업 기준 |
| --- | --- |
| Workspace `main` | `efc09658ca8b9cbf7b1fbeda54da364c47460029` |
| 문서 submodule `main` | `7059478e2711df434b50704370a402acdcddda59` |

작업 시작 시 root `git status --short`는 문서 submodule이 현재 checkout 위치 때문에 수정 상태로 보였고, submodule 내부 `git status --short`는 비어 있었다. 사용자 코드와 기존 run/checkpoint는 보존했다.

## 지정 run에서 실제 확인한 값

`tensorboard.backend.event_processing.event_accumulator.EventAccumulator`로 event 파일을 읽었다. 마지막 scalar 기록은 iteration 9503이며 `Episode_Reward/goal_distance=1.16486`, `Episode_Reward/goal_hold=0.37655`, `Episode_Termination/success=0.09856`, `Episode_Termination/time_out=0.74961`, `Curriculum/goal_position_tolerance=0.01083`이다. 저장된 `params/env.yaml`에서 기존 Goal Distance가 `DexPlanarGoalProgress`, weight100, `position_tolerance=0`인 것도 확인했다. 이는 신규 최단 XY 거리의 개선량을 미터로 지급하는 보상이다.

event에는 매 step의 XY 거리 분포나 1cm 통과 비율이 없다. 위 scalar만으로 1cm 부근의 정체 원인 또는 새 수식의 성공률 개선을 확정할 수 없다. 사용자가 관찰한 위치 정착 문제에 대해 보상 기울기를 바꾸는 실험용 환경을 추가한다.

## 구현 계약

`Isaac-Inspire-Final-v1-1`은 `FinalV1_1EnvCfg(FinalV1EnvCfg)`를 등록하고 기존 `FinalV1Env` runtime을 사용한다. `FinalV1_1RewardsCfg(FinalV1RewardsCfg)`에서 `goal_distance` 하나만 `exponential_planar_goal_proximity`로 교체한다. `FinalV1_1PPORunnerCfg(FinalV1PPORunnerCfg)`는 experiment를 `inspire_final_v1_1`로 분리한다. v1과 v2의 Goal Distance는 기존 함수·계수 그대로다.

현재 타겟과 명령 목표의 월드 XY 거리 $d$에 대해 매 control step의 보상률은 $1.5\exp(-d/0.05)$다. 거리 단위는 미터, 기울기 $a=20\mathrm{m}^{-1}$이고 RewardManager가 `step_dt=0.02`를 곱한다. 최대 보상률은1.5/초다. 10초 정확한 목표 유지의 상한15는 시작 거리가15cm인 v1 episode의 최대 진행 보상15와 맞춘 값이다. `goal_hold`를 포함한 다른 보상·종료·커리큘럼은 유지한다. 실제 평균 보상 규모는 지급 시점과 거리 분포에 따라 달라질 수 있다.

## 실행한 검증

Workspace 루트에서 다음 명령을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_final_versions.py \
  src/inspire_sweep_baseline/tests/test_final_configuration.py \
  src/inspire_sweep_baseline/tests/test_termination_debug.py
```

첫 실행은 **39 passed, 1 failed**였다. 실패는 런타임 기대 목록에서 신규 v1-1 및 기존 `Final-Test-v2` ID가 빠져 있었기 때문이다. 기대 목록을 보완하고 XY 전용 계산을 추가로 검사한 최종 재실행에서 **40 passed in 11.70s**를 확인했다. 새 검사는 실제 보상 함수의 XY 거리 단조성·근거리 기울기·10초 상한, v1 보상과의 설정 분리, 잘못된 거리 척도 거부를 확인한다.

Isaac Sim launcher를 headless CPU로 열고 `load_cfg_from_registry('Isaac-Inspire-Final-v1-1', ...)`로 실제 EnvCfg·PPO를 생성했다. `FinalV1_1EnvCfg.__bases__ == (FinalV1EnvCfg,)`, 등록 runtime `FinalV1Env`, Goal Distance 함수·weight·params, experiment 이름의 assertion이 모두 통과했고 프로세스 exit code는0이었다. 실행한 명령의 핵심은 다음과 같다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B - <<'PY'
import sys
sys.path.insert(0, 'src/inspire_sweep_baseline')
from isaaclab.app import AppLauncher
app = AppLauncher(headless=True, device='cpu').app
try:
    import gymnasium as gym
    import inspire_sweep_baseline
    from isaaclab_tasks.utils import load_cfg_from_registry
    from inspire_sweep_baseline.envs.final_envs import FinalV1EnvCfg, FinalV1_1EnvCfg
    from inspire_sweep_baseline.mdp.reward_functions.final import exponential_planar_goal_proximity
    task = 'Isaac-Inspire-Final-v1-1'
    cfg = load_cfg_from_registry(task, 'env_cfg_entry_point')
    agent = load_cfg_from_registry(task, 'rsl_rl_cfg_entry_point')
    assert FinalV1_1EnvCfg.__bases__ == (FinalV1EnvCfg,)
    assert isinstance(cfg, FinalV1_1EnvCfg)
    assert cfg.rewards.goal_distance.func is exponential_planar_goal_proximity
    assert cfg.rewards.goal_distance.weight == 1.5
    assert cfg.rewards.goal_distance.params == {'distance_scale': 0.05}
    assert agent.experiment_name == 'inspire_final_v1_1'
    assert gym.spec(task).entry_point == 'inspire_sweep_baseline.runtime.final:FinalV1Env'
finally:
    app.close()
PY
```

launcher는 이 호스트의 CUDA 장치 부재, Kit cache lock과 user.config 쓰기 실패를 출력했지만 설정 import/assertion은 통과했다. 물리 rollout, GPU 장기 학습, 1cm 미만 도달률 개선은 검증하지 않았다. 향후 v1과 v1-1의 동일 조건 평가에서 실제 XY 최종 거리 분포·1cm 미만 비율·goal_distance 평균·success/time_out 및 다른 보상 비중을 비교해야 한다.

학습 명령은 [환경 계약](../environments/FINAL_V1_V2_ENVIRONMENTS.md#final-v1-1--goal-distance-지수형-근접-보상)의 `train.py` 예시를 따른다. 새 학습은 실행하지 않았다.
