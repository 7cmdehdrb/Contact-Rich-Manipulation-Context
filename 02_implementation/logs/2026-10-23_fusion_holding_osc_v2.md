# Fusion Holding OSC v2 — UR10 Reach 제어 이식

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

2026-10-23 사용자 요청에 따라 Holding v1 직접 파생의 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2`를 추가했다. 기준 workspace commit은 `e6e36207cfa7ccffd7ba7b249809ffff54df88d4`이며 앞선 Holding v1 계열 작업과 `docs/plan/PLAN4.md` 등 기존 작업트리 변경을 보존했다. 기존 환경을 수정하지 않고 새 Cfg·PPO·등록을 추가했다.

## 구현과 부모 차이

`FusionHoldingOSCV2EnvCfg` → `FusionHoldingV1EnvCfg`, runtime `ContactSweepClutterFusionV1_0Env`, runner `CurriculumOnPolicyRunner`다. `FusionHoldingOSCV2PPORunnerCfg`는 Holding v1 PPO를 상속하고 experiment 이름만 `inspire_contact_sweep_clutter_fusion_holding_osc_v2`로 구분한다.

참조는 workspace의 `IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/reach/config/ur_10/ur10_osc_reach_env_cfg.py`다. Action을 로컬 `contact_sweep_clutter_fusion_holding_osc_v2/actions.py`로 이식하여 참고 task 모듈을 실행 의존성으로 만들지 않았다. BSD-3-Clause 출처를 보존한다.

| 항목 | 최종 설정 |
| --- | --- |
| 제어 관절·기준점 | Arm6개, 부모 EEF Frame의 body와 position/rotation offset |
| 명령 | Robot Base 기준 상대 XYZ + RPY,8D 전체 Action 중 Arm6D·Hand2D |
| scale | 위치0.03m, 회전0.15rad; RPY를 quaternion/axis-angle로 변환 |
| 모드 | pose_rel, fixed impedance,6축 motion·wrench0 |
| stiffness / damping ratio | 위치80×3·회전25×3 / 1×6 |
| dynamics | 관성 분리false, 부분 관성 분리false, 중력 보상false, nullspace none |
| effort | 실제 Arm 관절 limit×1.0, nonfinite 행은0, saturation 상태 기록 |
| Arm implicit PD | stiffness/damping0 |

부모 전체 설정에서 변경한 것은 Arm action과 Arm actuator의 두 PD gain이다. 특히 물리적 로봇 중력 설정은 부모를 유지한다. Reach 예제는 별도로 로봇 중력을 끄지만 사용자는 컨트롤러 부분만 변경하도록 요청했으므로 해당 Scene 변경은 적용하지 않았다. Hand, 보상·종료·curriculum, 장애물16슬롯64→32→16 인코더는 유지한다. OSC v1과 scale·회전 표현·토크 제어가 달라 기존 checkpoint의 동일 동작을 보장하지 않는다.

## 실행

Workspace 루트:

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2 --num_envs 2048 --headless
```

## 검증

실제 실행 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_sweep_baseline/tests/_fusion_holding_osc_v2_probe.py \
  > outputs/fusion_holding_osc_v2_validation/probe.log 2>&1

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_fusion_holding_osc.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v1.py \
  > outputs/fusion_holding_osc_v2_validation/pytest.log 2>&1
```

CPU 회귀14 passed, upstream ONNX deprecation warning1개,3.10초. GPU는 RTX3090/cuda:0에서 seed42·2환경·32step을 실행했다. 결과 JSON은 `outputs/fusion_holding_osc_v2_validation/result.json`에 있다. 실제 IsaacLab reference Cfg와 제어점·관절·로컬 class_type을 제외한 Action 설정 전체가 일치하며 부모 전체 Cfg는 Arm action·PD gain만 다르다. EEF는 `axia80_link`의 position offset `(0,0,0.1427)`, quaternion `(0.5,-0.5,-0.5,-0.5)`다.

혼합 RPY 명령을 identity/Z90° EEF에 적용하여 Base 기준 이동·RPY 변환·raw action 보존을 검증했다. 가짜 controller 출력으로 한 행의 NaN 토크 전체0 처리, 다른 행의2배 limit 토크 clamp, saturation flag 및 부분 reset을 검증하고 원래 controller를 복원했다. 실제32step은 앞16step Arm0, 뒤16step raw X0.03(목표 delta0.0009m), Hand열림으로 실행했다. 보상·관측·관절 위치 유한값과 매 step effort 상한을 확인했다.

장기 학습·성공률·실물 성능은 미검증이며 학습 로그는 수정하지 않았다. 기능 검사 통과와 동적 안정성 확보는 구분한다.


두 번의 동일 조건 GPU 실행 모두 기능 검사는 exit0/`HOLDING OSC V2 PROBE PASSED`지만, 64 env-step 중56개에서 마지막 physics substep의 토크 포화를 관찰했다. 추가 종료 진단에서는 step15와31에 각각 두 환경의 `shelf_collision` 종료가 확인되었다(총4 env 종료). 따라서 짧은 영 명령에서도 선반 충돌이 발생한 상태이며 안정적인 자세 유지나 학습 성능을 입증하지 않는다. 요청 설정과 부모 Scene을 보존했고 원인 분리·gain 조정·중력 조건 변경은 수행하지 않았다.

문서 검증: 이번 변경 Markdown4개에 수식·workspace 링크 검사를 적용하며, 실제 명령·결과는 `outputs/fusion_holding_osc_v2_validation/docs.log`에 저장한다.
