# Inspire-Wrench-v1: F/T 센서 기준 6축 closed-loop wrench OSC

최종 통합 명세: [Wrench-v0 전체 환경 및 v1 변경점](WRENCH_V0_V1_ENVIRONMENT.md). 랜덤화·관측·액션·전체 보상·커리큘럼·종료와 최신 v1 스케일/action-rate는 통합 문서를 기준으로 읽는다. 아래는 버전별 구현 배경과 검증 기록을 보존한 설명이다.

2026-11-04 구현. [Wrench-v0](WRENCH_V0_ENVIRONMENT.md)를 **직접 상속**하고 arm OSC와 그 목표 명령의 action-rate 정규화를 변경한다. [개발·검증 기록](../logs/2026-11-04_wrench_v1_osc.md).

## 등록·상속과 범위

| 항목 | 값 |
| --- | --- |
| Gym ID | `Inspire-Wrench-v1` |
| EnvCfg | `WrenchV1EnvCfg(WrenchEnvCfg)` |
| Actions | `WrenchV1ActionsCfg(WrenchActionsCfg)`, gripper는 그대로 |
| Arm Action Cfg | `WrenchV1OSCActionCfg(WrenchOSCActionCfg)` |
| Arm 실행 | `SensorFrameWrenchAction(ActionTerm)` |
| Runtime/Scene | v0의 `WrenchEnv`/`WrenchSceneCfg` 재사용 |
| PPO | `WrenchV1PPORunnerCfg(WrenchPPORunnerCfg)`, 실험명만 `inspire_wrench_v1` |

robot_action_rate_penalty의 Arm 입력 정규화를 제외한 보상15항·성공/실패·Dead Zone·배치 bank·물성·Scene·센서·PPO 수치·Actor121D/Critic124D는 v0와 같다. EEF 관측과 높이 보상 기준도 기존 `ee_frame`이다. arm6D+hand2D의 총 행동8D는 유지하지만 **앞6D의 의미는 pose 증분에서 wrench 목표로 바뀐다**. v0 정책을 같은 동작의 checkpoint로 간주하지 않는다.

## 참고 구현과 확장 이유

다음 실제 로컬 코드와 공식 문서를 확인했다.

1. [UR10 Reach OSC 예제](../../../../IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/reach/config/ur_10/ur10_osc_reach_env_cfg.py): `source/isaaclab_tasks`의 기존 예제는 pose 제어다. 여기서 effort clamp, 비유한 effort0 처리, saturation 상태, gravity compensation을 참고했다.
2. [wrench-only closed-loop 테스트](../../../../IsaacLab/source/isaaclab/test/controllers/test_operational_space.py): `test_franka_wrench_abs_closed_loop`는 `wrench_abs`, motion6축0, wrench6축1, force P gain0.2, moment gain0을 사용한다.
3. [OSC 튜토리얼 코드](../../../../IsaacLab/scripts/tutorials/05_controllers/run_osc.py): hybrid 제어와10N 목표, 힘 gain0.1 사용 예제다. v1은 hybrid가 아니라6축 wrench-only다.
4. [기본 OSC 계산](../../../../IsaacLab/source/isaaclab/isaaclab/controllers/operational_space.py)과 [공식 OSC 문서](https://isaac-sim.github.io/IsaacLab/main/source/how-to/run_osc.html): `contact_wrench_stiffness_task`가 있으면 feedforward+P 제어지만 기본 `compute(current_ee_force_b=...)`는 **힘3축만 측정**한다. 모멘트 측정값을 desired moment로 대체하므로 moment gain을0.2로 지정하기만 해서는 모멘트 closed-loop가 되지 않는다.

따라서 Isaac Lab 소스를 수정하지 않고 로컬 전용 `SensorFrameWrenchAction`과 순수 tensor 계산 함수 `sensor_wrench_efforts`를 추가했다. 기존 공식 force-loop 수식은 유지하고 현재 wrench 입력을6D로 확장했다. 기본 `OperationalSpaceController` 인스턴스를 숨겨서 사용하는 방식이 아니며, `OperationalSpaceControllerCfg`를 받아 검증하는 **wrench-only OSC 전용 구현**이다. 미지원 pose/hybrid/variable impedance/nullspace/inertial-decoupling 설정은 생성 시 오류로 처리한다.

## 최종 파라미터

[Action Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/actions/wrench.py) · [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/wrench_envs.py)

| 파라미터 | v1 값 | 근거·의미 |
| --- | --- | --- |
| `target_types` | `["wrench_abs"]` | Isaac Lab이 지원하는 절대 wrench 목표 문자열. `"wrench"` 단독은 아님 |
| `impedance_mode` | `"fixed"` | 행동6D 모두 wrench 목표. gain을 행동에 추가하지 않음 |
| `motion_control_axes_task` | `(0,0,0,0,0,0)` | pose 제어 없음 |
| `contact_wrench_control_axes_task` | `(1,1,1,1,1,1)` | Fx/Fy/Fz/Mx/My/Mz 전부 제어 |
| `contact_wrench_stiffness_task` | `(0.2,0.2,0.2,0.2,0.2,0.2)` | 힘 gain0.2는 공식 wrench-only 테스트를 참고. 모멘트0.2는 이번6축 확장의 초기 설계값이며 튜닝 결과가 아님 |
| `inertial_dynamics_decoupling` | `False` | pure wrench 경로는 mass inverse를 쓰지 않음 |
| `partial_inertial_dynamics_decoupling` | `False` | 동일 |
| `gravity_compensation` | `True` | 실제 arm/hand에 중력이 활성화되어 기존 g(q) 보상 유지 |
| `nullspace_control` | `"none"` | 기존6DoF arm 계약 유지 |
| `body_name` | `"axia80_link"` | F/T housing 중심의 기존 body frame |
| `body_offset` | `None` | 기존 EEF +142.7mm 오프셋 제거. 부모 post-init 후 v1에서 재설정 |
| `task_frame_rel_path` | `None` | 별도 Scene frame/sensor를 만들지 않음. 실행 코드가 현재 F/T 축에서 직접 계산 |
| `wrench_scale` | `(100,100,100,5,5,5)` | 사용자 제공 센서 계측 범위150N/8Nm에 여유를 둔 목표 스케일 |
| `normalized_wrench_limit` | `1.0` | policy 입력을 축별[-1,1] clip 후 scale. 결과 축별±100N/±5Nm |
| `commanded_wrench_limit` | `(120,120,120,6,6,6)` | FF+P 보정 후 센서 축별 명령 clamp, Jacobian 변환 이전 |
| `effort_limit_scale` | `1.0` | 실제 articulation joint effort limit 적용 |
| `minimum_effort_limit` | `1e-6` | 기존 clamp 하한 유지 |
| `saturation_tolerance` | `1e-6` | 기존 saturation 검출 허용오차 유지 |
| Arm actuator stiffness/damping | `0/0` | v0 그대로, joint PD가 별도로 작동하지 않음 |
| 제어/정책 주기 | `0.01s / 0.02s` | 피드백100Hz, policy wrench50Hz. 기존 sim dt/decimation 유지 |

`contact_wrench_stiffness_task`는 여기서 N/N 및 Nm/Nm의 **무차원 비례 게인**이다. pose stiffness(N/m 등)가 아니다. 기존 motion stiffness/damping 및 position/orientation scale 필드는 Cfg 기반형에 존재하지만 이 제어 경로에서 사용하지 않는다. integral·derivative wrench feedback, force 저역통과 필터, pose 복원력은 추가하지 않았다. 원하는 wrench0은 위치 유지 명령이 아니며, 측정 wrench 보정과 중력 보상만 적용한다.

## 센서 원점·축·부호와 실물 입력

[제어 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/wrench_control.py) · [시뮬레이터 adapter](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/action_functions/wrench.py)

제어 원점 S는 `axia80_link` 중심이며, wrench와 Jacobian 모두 **같은 S 원점·현재 S 축**을 사용한다. 목표 wrench는 정책 주기 사이에 센서 축 성분으로 고정하고, 매 physics substep에 현재 센서 자세로 Jacobian을 회전한다. 이전 policy step의 world 방향으로 고정하는 방식이 아니다. 세계/로봇 root 위치가 변해도 root 원점까지 moment를 운반하지 않는다.

```math
w_{cmd}^{S}=\mathrm{clip}(w_{des}^{S}+K_p(w_{des}^{S}-w_{measured}^{S}),-L,L),
\qquad \tau=J_S^{T}w_{cmd}^{S}+g(q)
```

- 원시 F/T는 기존 `axia80_measurement_joint`의 child인 `inspire_base_link`에서 `body_incoming_joint_wrench_b`로 읽는다. 이 joint 원점은 sensor housing 중심보다+Z12.7mm 떨어져 있다.
- 기존 `PureWrenchReader.read(sensor_pos_w, sensor_quat_w, ...)`에 **EEF 대신 센서 pose**를 전달한다. joint 원점→센서 중심의 고정 moment arm만 보정하고, downstream hand의 중력·관성 support를 제거한다. 반환 필드의 역사적 이름은 `pure_eef`지만 값의 실제 reference는 전달한 센서다.
- 측정값 부호는 보정된 parent-on-child 반력, 즉 로봇이 환경에 가하는 wrench 기준이다. 센서에 손바닥 쪽으로 들어오는 외력과는 반대 부호다. 실물 장치가 environment-on-tool 부호로 출력하면 hardware adapter에서 부호를 반전한다.
- 센서 Jacobian은 해당 body의 world Jacobian을 sensor 축으로 회전하여 사용한다. 현재 자산은 중심에 COM을 갖는 cylinder housing이므로 제어점과 이 body Jacobian 기준점이 일치한다. 기존 EEF offset Jacobian을 재사용하지 않는다.
- 원시 F/T에서 tool 중력/관성을 빼는 것은 외부 접촉값 추정이다. 별도의 `gravity_compensation=True`는 실제 관절 토크에서 robot 중력을 상쇄하는 것으로, 두 계산의 역할이 다르다.

실물 adapter가 준비할 것은 보정된6축 F/T, 같은 센서 원점의6×6 geometric Jacobian, joint gravity torque다. 센서 제조사의 실제 reporting frame이 housing 중심과 다르면 **센서 내부의 고정 transform**을 적용해야 한다. 구현상12.7mm는 현재 시뮬레이션 자산의 joint 위치이며 실제 장치의 reporting frame을 입증한 치수가 아니다. hand 질량/COM/관성·FT bias·축 부호는 실물 모델에 맞춰 보정해야 한다. EEF 위치에서의 current wrench 추정은 요구하지 않는다.

`mdp/common/wrench_control.py`는 torch만 사용하며 Isaac Lab/PhysX를 import하지 않는다. 다음 인터페이스에 외부 측정값을 직접 공급할 수 있다.

```python
from inspire_sweep_baseline.mdp.common.wrench_control import sensor_wrench_efforts

# 각 tensor는 batch 포함. w_des_s/current_wrench_s: [N,6], J_s: [N,6,6].
# current_wrench_s는 tool 보정 후 robot-on-environment 부호, 센서 원점/축 기준.
raw_tau = sensor_wrench_efforts(
    w_des_s, current_wrench_s, J_s,
    p_gains=w_des_s.new_tensor([0.2] * 6), gravity=gravity_joint,
    commanded_wrench_limit=w_des_s.new_tensor([120, 120, 120, 6, 6, 6]),
)
# 하드웨어 adapter에서도 실제 관절 effort limit을 적용한다.
```

## 샘플 수명과 보존 범위

Action은 자기 physics-rate reader를 사용한다. Actor의 noisy F/T 관측이나20ms observation cache를 피드백에 사용하지 않는다. 각 `apply_actions()`는 직전 완료된 물리 step의 raw reaction/COM acceleration을 함께 읽는다. reset 직후 첫 substep은 stale sample이므로 feedback correction을0으로 하고 feedforward+gravity만 사용한다. 다음 물리 샘플부터 feedback을 켠다. 부분reset은 선택된 환경만 마스킹한다. raw action·processed target·feedback·effort·saturation 상태도 선택 행만 초기화한다.

비유한 action/effort는 해당 행의 effort0 및 saturation=True로 처리하고, 유한 effort는 기존 joint effort limits로 clip한다. 센서 측정의 비유한 live 데이터는 기존 `PureWrenchReader`의 오류 검사를 그대로 따른다. `arm_action.current_wrench_s`에서 실제 controller feedback을 확인할 수 있다.

기존 관측/보상용 F/T는 계속 EEF 기준이고 기존 noise·cache 계약을 따른다. `scene.ee_frame`, USD, 접촉 센서, 측정 joint topology, 물리 timestep은 변경하지 않았다. Isaac Lab submodule도 수정하지 않았다.

## 실행과 확인된 범위

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-v1 --num_envs 2048 --headless
```

CPU80개 통과: v0와의 설정 격리, 기본 Isaac OSC와 힘 feedback 일치, 모멘트6축 확장, sensor 기준점/회전/부호, gravity 보정·가상일 일치, 실제 action의 raw 입력/clip/선택 joint 매핑/부분reset/physics-rate feedback, 기존 v0·Revision·Holding 회귀다. Sim asset과 ActionTerm 기반형을 CPU double로 대체한 검사는 실제 simulator 실행과 구분한다.

NVIDIA 드라이버를 사용할 수 없어 실제 Isaac Sim 접촉 추종·GPU rollout·PPO 학습·게인 안정성·collection 시간은 미검증이다. GPU 환경에서는 아래 기존 probe의 v1 모드를 먼저 실행할 수 있다. 이 명령은 이번 세션에서 실행하지 않았다.

```bash
python src/inspire_sweep_baseline/tests/_wrench_probe.py \
  --version v1 --headless --device cuda:0 --num_envs 64 \
  --output outputs/wrench_v1_validation
```

이 probe는 전체 Cfg 차이가 `actions.arm_action`에만 있는지와 finite rollout/feedback/effort limit을 확인한다. zero-action rollout은 접촉 force tracking 성능 시험을 대체하지 않는다. 실제 접촉 시 desired/current6축 추종 오차와 진동·포화율을 측정한 뒤0.2 gain 및±10N/±1Nm 범위를 조정해야 한다.

## 2026-11-04 센서 범위 반영 후속 수정

목표 축별100N/5Nm, 보정 후 명령 축별120N/6Nm로 변경했다. 측정0에서 최대 목표의 FF+P는120N/6Nm이며 반대 방향 측정으로 오차가 증가해도 같은 명령 한계로 제한된다. 사용자 제공150N/8Nm를 축별 범위로 해석했다. 이는 검증된 하드웨어 안전 한계가 아니다. 합력 크기·충격·실제 센서 원시 측정값은 제한하지 않으며, tool 보정 전 센서값에는 중력·관성 하중도 포함된다. 센서의 축별/복합하중 정격과 실물 안정성은 미검증이다. 기존 체크포인트의 동일 출력은 더 큰 목표가 되므로 이전 정책과 동작이 같지 않다.

후속 CPU 회귀43개 통과. v0/비OSC 구성은 유지하며 GPU 물리 검증은 수행하지 않았다.

## 2026-11-04 Desired Wrench action-rate 정규화

v1의 `robot_action_rate_penalty`만 `desired_wrench_action_rate_penalty`로 교체한다. Arm 현재·이전 Desired Wrench를 축별 정책 목표 범위100N/5Nm로 나눈 [-1,1] 값의 차이를 제곱 합산한다. 실제 계산은 `clip(raw, -L, L) / L`이며 `L=normalized_wrench_limit`이다. Desired Wrench의 `wrench_scale`이 분자·분모에서 상쇄되므로 힘과 모멘트가 같은 상대 변화율로 평가된다. feedback 이후120N/6Nm 명령이나 측정 wrench를 평가하지 않는다.

비용은 `0.03 * sum((u_now-u_prev)**2) + 0.03 * hand_raw_rate_l2`이며 기존 각 그룹 상한100, term weight=-1, RewardManager dt 적용은 유지한다. Arm6축의 최대 제곱합은24다. Hand는 기존 raw2D 계산을 유지한다. 예: Fx 0→50N과 Mx 0→2.5Nm는 각각0.0075의 비용이다(dt/weight 적용 전). raw2→3처럼 같은 최대 목표를 만드는 변화는 Arm 비용0이다. ActionManager의 prev_action을 사용하여 부분reset 이력을 그대로 따른다. v0 보상은 변경하지 않았다.

CPU 회귀44개 통과(4.55s). GPU 물리/학습 검증은 미수행이다.
