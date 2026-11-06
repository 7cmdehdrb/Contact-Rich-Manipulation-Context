# Refactor v3-Test: 왼쪽 전용 진단 환경

2026-11-06. 사용자가 wr2의 v1/v2/v3 정책 재생에서 공통적으로 왼쪽 밀기 실패를 관찰하여 v3를 부모로 한 임시 환경을 요청했다. 원인 규명이나 정책 성능 개선은 이번 작업의 검증 대상이 아니다.

## 기준과 요청 범위

Workspace 기준 commit: `89833ab4b5017ae91ba140d06d8add9393907dad`. 시작 시 README, layout sampler, reset 함수, events, CPU/GPU probe 및 문서 저장소에 사용자 변경이 있었다. 특히 목표 거리6–12cm 변경을 작업 시작 기준으로 보존했다. 기존 변경·submodule commit·학습 로그는 보존하고 새 commit은 만들지 않았다.

## 최종 계약과 전체 차이

| 항목 | 부모 v3 → v3-Test |
| --- | --- |
| Gym ID | `Inspire-Wrench-Refactor-v3` → `Inspire-Wrench-Refactor-v3-Test` |
| EnvCfg | `WrenchRefactorV3TestEnvCfg(WrenchRefactorV3EnvCfg)` |
| runtime | 동일 `runtime.wrench_refactor:WrenchRefactorEnv` |
| PPO | `WrenchRefactorV3TestPPORunnerCfg(WrenchRefactorV3PPORunnerCfg)`; experiment_name만 `inspire_wrench_refactor_v3_test` |
| reset | `events.object_spawn.params["sweep_direction"] = "left"` 추가 |
| 목표 방향 | 양쪽 허용 반평면 → shelf-local −Y 반평면; 현재 shelf 회전 identity이므로 world −Y. 기존 sweep.py의 left 정의와 동일 |
| 목표 거리/타겟 초기 위치 | 동일6–12cm 및 반경2cm 원판 |
| 방향 커리큘럼 | 동일 ±X 금지 반각30도,10000 iteration부터5도 감소, 이후3000간격; 왼쪽 반평면 안에서 적용 |
| Scene/자산/물성/장애물/reset lifecycle | 동일; 장애물 Gray/White 각각0–3 균등 |
| Actor/Critic/Action/Command | 동일74+64 관측, EEF task-space OSC,8D action |
| Reward/Termination/Curriculum/log term | 전체 이름·순서·callable·params·weight·일정 동일; 목표 판정 경계 변경 없음 |

`envs/wrench_refactor_envs.py`에 파생 설정, `agent/wrench_refactor_ppo_cfg.py`에 파생 runner, 패키지 `__init__.py`에 등록했다. 공통 `sample_commands`와 `reset_scene`는 선택 인자 sweep_direction을 추가했다. 기본값 both에서는 기존 난수 draw 크기/순서와 theta 계산을 그대로 사용하여 기존 v0–v3 분포·동작을 보존한다. 왼쪽은 허용 반평면 내부 방위 균등과 조건부 거리 균등을 사용하고 이후 OBB 배치는 기존 함수를 따른다. v3 checkpoint를 그대로 로드할 수 있는 입력/정책 구성이다.

## 실행

Workspace 루트, 활성화된 Isaac Lab conda 환경에서 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/play.py \
  --task Inspire-Wrench-Refactor-v3-Test \
  --checkpoint logs/TEMP/wr2/inspire_wrench_refactor_v3/2026-11-06_01-42-12/model_4550.pt \
  --num_envs 32 --real-time
```

## 검증

- CPU: `env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_wrench_refactor.py -q`.
- 실제 config import 및 전체 to_dict 비교: v3-Test는 v3 대비 reset 방향 인자만 다르며 runner는 experiment_name만 다름. 자식 구성 후 부모 재조회도 동일함을 확인했다.
- CPU는 모든 커리큘럼 반각0/5/10/15/20/25/30도에서 왼쪽 부호·방위 균등·거리6–12cm를 검사한다. OBB는0/30도에서 정확한 장애물 수·간격·선반 경계·주차를 검사한다. 기존 양쪽 방향 균등 검사도 유지한다.
- GPU 명령: 아래 probe. 최초 sandbox 실행은 CUDA 접근 차단으로 시뮬레이션 생성에 실패했다. 이를 드라이버 부재로 해석하지 않고 sandbox 밖 GPU 실행으로 재검증한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/tests/_wrench_refactor_probe.py --task Inspire-Wrench-Refactor-v3-Test --num_envs 32 --headless --device cuda:0 --output outputs/wrench_refactor_v3_test_validation
```

최종 결과: **CPU59개 통과(5.92초)**. sandbox 밖 실제GPU32환경 검사 통과: config 전체 차이 비교, 실제Gym생성, EEF action 축 검증, 관측차원74/74/64/64,17물체·790g손·30kg선반, 부분reset, iteration0/9999/10000/13000/16000/19000/22000/25000 각각 reset+36step 유한 rollout, 고정 물성·bounds 보존, 매reset 왼쪽 방향·거리6–12cm를 확인했다. 산출물: `outputs/wrench_refactor_v3_test_validation/probe_32.json`, 실행로그 `/tmp/wrench_refactor_v3_test_probe.log`.

문서5개 math 검사와 수정 코드·문서 저장소의 diff whitespace 검사는 통과했다. workspace 전체 diff 검사에는 작업 시작부터 있던 `docs/plan/PLAN12.md:109` trailing whitespace가 검출되었으며 요청 범위 밖이므로 수정하지 않았다. 정책 play/추가 학습/왼쪽 성공률 평가는 수행하지 않았다. 기존 checkpoint·logs/rsl_rl·logs/TEMP는 수정하지 않았다.

변경문서5개의 링크268개 검사에서 기존 README의 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1개가 검출되었다. 새로 추가한 링크는 정상이다. 기존 누락 문서는 이번 요청 범위 밖으로 보존했다.

## 후속: 종료 시 원인 출력

사용자 요청: 왼쪽으로 이동할 때 왜 종료되는지 확인하기 위해 v3-Test에서 termination 발생 시 print를 추가한다.

`runtime/wrench_refactor.py::WrenchRefactorEnv._reset_idx` 진입부에 임시 출력 블록을 추가했다. `type(self.cfg).__name__ == 'WrenchRefactorV3TestEnvCfg'`에서만 실행하며, reset 대상별 termination_manager의 이미 평가된 활성 term 중 True인 이름을 모두 출력한다. 출력은 reset으로 manager 상태·episode step을 지우기 전에 실행하며 flush=True다. 출력 항목은 env ID, episode step, reasons다. timeout과 성공 종료도 발동하면 해당 이름을 출력한다. term이 없는 초기 reset에서는 출력하지 않는다.

```text
[Wrench-Refactor-v3-Test termination] env=1 step=17 reasons=shelf_failure, arm_joint_velocity
```

종료 함수는 재평가하지 않으며 기존 판정·임계값·보상·커리큘럼·reset 순서는 보존한다. 부모 v0–v3 및 다른 설정 클래스는 출력 대상에서 제외한다. 앞의 play 명령을 그대로 사용하고 이미 실행 중인 play 프로세스는 재시작해야 반영된다.

전체 대조: Gym/EnvCfg/runtime 클래스/PPO/Scene/Command/Event/reset 의미/Observation/Action/Reward/Termination/Curriculum 설정 변화 없음. runtime에 v3-Test 전용 출력만 추가했다. 기존 작업트리 변경과 학습 로그는 보존했다.

검증: CPU 회귀59개 통과(5.58초). 실제 runtime 클래스를 가짜 simulator base와 최소 상태로 실행한 별도 검사에서 동시 원인2개 출력·env/step 정확성·초기 reset 무출력·부모v3 무출력·출력 후 정상 reset을 확인했다. GPU32환경 재검증은 `outputs/wrench_refactor_v3_test_termination_validation`, 실행로그는 `/tmp/wrench_refactor_v3_test_termination_probe.log`를 사용한다. 실제 학습 정책의 왼쪽 종료 원인은 이 계측으로 play 결과를 확인해야 하며 이번 변경만으로 단정하지 않는다.

후속 최종 검증: GPU32환경 config/부분reset/8개 iteration 지점별36step rollout·왼쪽 목표·고정물성 검사 통과. 이 zero-action rollout에서는 종료 print가 발생하지 않았으므로 실제 정책 종료의 출력 사례를 확보한 것은 아니다. 출력 경로는 위 별도 실행 검사로 확인했다. 변경문서2개 math·링크 검사(5링크, 오류0) 및 코드 diff whitespace 검사 통과.

## 후속: Arm 관절속도6축 실시간 출력

사용자가 종료 원인을 Joint Velocity로 확인하고6축 실시간 출력 추가를 요청했다. `mdp/termination_functions/sweep.py::arm_velocity`에서 기존 velocity 텐서를 읽은 직후 v3-Test 전용 print를 추가했다. 별도 속도 계산이나 termination 함수 재호출 없이, 종료 판정에 쓰는 바로 그 실제 joint_vel을 매 제어step(0.02초), 모든 env에 대해 출력한다. 자동reset 이전이므로 종료를 일으킨 순간 값도 남는다.

출력에는 env ID·episode step·6개 관절 이름과 부호 있는 rad/s 속도·실제 threshold·exceeded를 포함한다. 순서는 termination의 resolved asset_cfg.joint_ids와 동일하며, 일반적으로 shoulder_pan_joint, shoulder_lift_joint, elbow_joint, wrist_1_joint, wrist_2_joint, wrist_3_joint다. threshold는3rad/s, 기존 strict abs(velocity)>threshold 판정을 유지한다. 기존 종료 원인 print도 유지한다. type(cfg)가 WrenchRefactorV3TestEnvCfg인 경우만 출력하며 v0–v3와 다른 환경은 출력하지 않는다.

전체 대조: 등록/상속/PPO/Scene/reset/관측/Action/보상/종료term·함수·인자·threshold·커리큘럼 변경 없음. 공유 함수의 반환식도 기존과 동일하며 v3-Test의 진단 출력만 추가했다.6축×전체 환경 출력을 매step 동기화하므로 디버깅 중 재생 속도가 느려질 수 있다. 기존 play 명령을 재시작하면 적용된다.

별도 실행 검사: resolved joint 순서·6축 이름·부호·step/ID·정확히3에서미종료/−3.1에서종료·부모v3 무출력 및 반환값 동일을 확인했다. GPU probe는 `outputs/wrench_refactor_v3_test_joint_velocity_validation`, 실행로그는 `/tmp/wrench_refactor_v3_test_joint_velocity_probe.log`를 사용한다. 실제 정책에서 어느 joint가 왜 과속되는지의 원인 분석은 이번 출력 추가로 단정하지 않는다.

6축 출력 최종 검증: CPU59개 통과(5.66초). GPU32환경×8구간×36step reset/rollout 통과. 실제 로그의 속도 출력9216줄 모두6축이 포함됨을 확인했다. 변경문서2개 math·링크5개(오류0)·diff whitespace 검사 통과.

## 후속: v3-Test의 Joint Velocity 종료 임시 비활성화

사용자 요청으로 `WrenchRefactorV3TestEnvCfg.__post_init__`에서 `self.terminations.arm_joint_velocity = None`을 적용했다. 기존 v0–v3의3rad/s 종료는 유지한다. 물리 actuator 속도 제한(Arm2/2/2/4/4/4rad/s), 다른 종료4종, 보상·제어·목표·관측·PPO·커리큘럼은 변경하지 않는다.

속도 종료 term을 제거하면 기존 term 내부 print도 호출되지 않으므로, 실시간6축 출력은 runtime의 v3-Test 전용 `_print_joint_velocities`로 옮겼다. 일반 환경은 step 직후 출력하고, 다른 조건으로 종료되는 환경은 `_reset_idx`에서 reset 직전에 출력한다. 따라서 매step마다 각 환경을 한 번씩 출력하며 자동reset으로 종료 직전 속도를 덮어쓰지 않는다. 이름·단위·출력 접두사는 유지하고,3rad/s는 `reference_limit`로 명시하며 `termination_enabled=False`를 함께 출력한다. 기존 종료 사유 출력도 유지한다. 공유 `arm_velocity` 함수는 진단 코드 추가 전 반환식 그대로 복원했다.

전체 대조: 직전 v3-Test 대비 종료 term1개 None 및 위 출력 호출 위치만 변경. v3 대비 최종 설정 차이는 왼쪽 목표와 arm_joint_velocity=None, runner의 experiment_name뿐이다. 부모를 구성 후 재조회하여 보존을 검사한다. 기존 checkpoint와 모든 학습 로그는 변경하지 않는다. 동일 play 명령 재시작으로 반영한다.

검증 명령은 기존 CPU 회귀와 GPU probe를 재사용했다. GPU 산출물은 `outputs/wrench_refactor_v3_test_no_velocity_termination/probe_32.json`, 로그는 `/tmp/wrench_refactor_v3_test_no_velocity_termination.log`다. 실제 정책의 종료 없는 동작 안정성이나 성공률은 별도 play 관찰 범위다.

속도 종료 비활성화 최종 검증: CPU59개 통과(6.14초), 실제 config 전체 비교 통과(자식 arm_joint_velocity=None·부모3rad/s 유지). GPU32환경×8구간×36step reset/rollout 통과. 속도 출력9216줄 모두6축과 termination_enabled=False를 확인했다. 변경문서 math/링크5개/코드·문서 diff whitespace 검사 통과.

## 후속: wrist3 위치 차분 속도와 joint_vel 대조 출력

사용자 요청: 이전 wrist3 position과 현재 position의 차이를 delta t로 나눈 값과 실제 입력 joint velocity를 나란히 출력한다. 기존6축 속도 print를 wrist_3_joint 전용 비교 출력으로 교체했다.

`runtime/wrench_refactor.py::step`의 v3-Test 전용 분기에서 매 제어step 직전 `robot.data.joint_pos[:, wrist3_id].clone()`을 저장한다. step 후에는 현재 joint_pos, joint_vel과 비교한다. dt는 wall clock이 아닌 `self.step_dt`(물리0.01초×decimation2=0.02초)다. 출력은 env/episode step, last_pos(rad), current_pos(rad), dt(s), delta_pos/dt(rad/s), joint_vel(rad/s) 순서다. 차분은 unwrapped 관절값의 직접 차이며 별도 ±pi 정규화를 하지 않는다.

다른 종료가 발생한 env는 reset 직전에 기존 `_reset_idx` 진단 경로에서 출력하고, 미종료 env는 step 후에 출력한다. 이전 위치는 매step 시작 시 이미 reset된 실제 위치로 다시 저장하므로 reset 전후의 불연속을 속도로 계산하지 않는다. 초기화 단계에서 이전 snapshot이 없으면 출력하지 않는다. Joint Velocity 종료 비활성화와 다른 종료 print는 유지한다. 설정/제어/보상/관측/물리/부모v0–v3에는 변경이 없다.

유의: delta_pos/dt는0.02초 구간 평균 속도이며 joint_vel은 구간 끝 순간 속도다. 두 물리 substep 사이 가속이 있으면 두 값이 정확히 같을 필요는 없다. 이번 출력은 비교 수단이며 상태값 오류나 과속 원인을 단정하지 않는다.

GPU 검증 산출물은 `outputs/wrench_refactor_v3_test_wrist3_difference/probe_32.json`, 실행로그는 `/tmp/wrench_refactor_v3_test_wrist3_difference.log`다. 기존 play 명령 재시작으로 적용한다.

최종 검증: CPU59개 통과(5.67초), 별도 출력 실행 검사에서 부호 있는 차분·dt0.02·독립 joint_vel 출력 통과. GPU32환경×8구간×36step reset/rollout 통과. 실제 출력9216줄의 위치 차분 산술과 연속step의 이전/현재 위치 연결을 검증했다. 초기 step1은 reset 위치−π/2에서 시작했다. 문서2개 math·링크5개 오류0 및 코드 diff whitespace 검사 통과.

## 후속: 관절속도 비교 출력을 제거하고 OSC 전체 입출력 출력

사용자 요청: Joint 출력을 지우고 OSC 출력, 후속으로 OSC 입출력 전부를 print한다. OSC 출력은 controller.compute의6축 joint torque 및 제한 후 effort target을 의미하며, policy action과 controller의 모든 명시적 계산 입력을 함께 출력한다.

runtime의 wrist3 snapshot·위치차분 helper·step후/종료시 속도 print 호출을 제거했다. runtime step은 원래 sensor freshness 갱신과 super.step 호출로 복원했다. 종료 원인 print는 유지한다.

`mdp/action_functions/contact_sweep_clutter_fusion_holding_osc.py::UR10OperationalSpaceControllerAction.apply_actions`에 cfg type이 WrenchRefactorV3TestEnvCfg인 경우에만 활성화되는 임시 계측을 추가했다. v3의 WrenchRefactorOSCAction이 이 경로를 상속한다. 다른 환경에서는 snapshot·출력 없이 기존 제어 계산을 실행한다.

`[Wrench-Refactor-v3-Test OSC]` 뒤 JSON 한 줄을 모든 env·물리substep마다 출력한다. 정책주기0.02초당2회, 물리dt0.01초다. JSON은 행렬을 생략하지 않으며 아래 필드를 포함한다.

- 명령 입력: action_raw, command_processed(위치m·axis-angle회전rad), task_frame_pose_b, desired_ee_pose_b.
- compute에 전달한 인자9개: jacobian_b, current_ee_pose_b, current_ee_vel_b, current_ee_force_b, mass_matrix, gravity, current_joint_pos, current_joint_vel, nullspace_joint_pos_target.
- 실제 사용 gain: motion_p_gains_b, motion_d_gains_b.
- 출력/제한: torque_raw_Nm(비유한값 거부·clamp전), torque_command_Nm(실제 set_joint_effort_target 전달값), effort_limits_Nm, finite_efforts, torque_saturated.
- 메타데이터: env, episode step(현재물리계산이 속한제어step), physics_step, physics_dt, joints(실제 resolve된순서), body_name, body_offset_pos/rot, units. pose quaternion은wxyz, _b는robot-root기준이다. action_raw는무차원이다.

Joint Velocity 종료 비활성화·왼쪽 목표·물리제한·OSC계산·토크clamp·보상·관측·다른 종료·PPO는 유지한다. 계측은 실제 제어 수식을 변경하지 않는다. 데이터가 많으므로2환경 GPU probe로 검사하며, 실제 사용자 재생 환경수는 그대로 선택할 수 있다.

검증 경로: `outputs/wrench_refactor_v3_test_osc_io/probe_2.json`, `/tmp/wrench_refactor_v3_test_osc_io.log`. 동일 play 명령 재시작으로 반영한다.

OSC계측 최종 검증: CPU67개 통과(Refactor+기존OSC회귀,6.34초). GPU2환경×8구간×36step rollout/부분reset·config보존 검사 통과. JSON1152줄을 파싱하여 모든 입출력 필드·6×6 Jacobian/질량행렬·6축 순서·dt0.01·raw→명령 clamp 일치를 확인했다. 기존 joint_velocity 출력0줄을 확인했다. 실제 학습정책 OSC동작이나 과속 원인은 이번 zero-action probe만으로 판단하지 않는다.

## 후속: 기존 토크 변화 페널티와 정책 action 변화 페널티의 실제 play 대조

사용자는 개념 설명 대신 코드를 수정하여 두 비용을 동시 출력하고, 실제 play 로그를 수집해 비교하도록 요청했다. `RefactorActionRatePenalty.__call__`의 기존 step cache 안에 v3-Test 전용 진단을 추가했다. 반환값과 기존 토크 history 갱신은 보존한다. 실제 reward는 여전히 기존 방식이며 후보 비용은 출력만 한다.

기존 비용: 0.03×sum((tau_t/limit−tau_prev/limit)^2)의 Arm합산100cap + 0.03×clamped Hand action 변화 제곱합. 후보 비용: 0.03×sum((raw Arm action_t−raw Arm action_prev)^2) + 동일 Hand 비용. 후보의 위치3축과 RPY회전3축은 raw 정책 공간에서 각각 계산한다.3cm·0.15rad를 다시 나누는 연산은 하지 않는다(물리 명령을 해당 배율로 정규화한 값이 raw다). 후보는 앞서 제안한 식처럼 cap이 없으며, cap100을 유지할 때의 별도 후보값도 함께 출력해 구분한다.

출력은 `[Wrench-Refactor-v3-Test action_penalty]` JSON으로 env/episode step/global policy step, 기존/후보/cap유지후보 비용, 기존관절별6개 기여, 후보위치/회전/축별 기여, 공통Hand비용, raw action과변화량, 정규화토크, weight−1×dt를 반영한 기존/후보 step reward를 포함한다. 기존 OSC 전체 출력과 종료 원인 출력도 유지한다. 부모v0–v3는 진단 대상에서 제외한다.

반복 가능한 실제 play 종료를 위해 play.py에 `--max_steps`(기본None,양수검사)를 추가했다. 미지정 실행·기존 video 종료 조건은 보존한다. 원본checkpoint와 logs/TEMP·logs/rsl_rl을 수정하지 않도록 checkpoint를 outputs에 복사하고, play의 JIT/ONNX export도 복사본 폴더에 생성하도록 했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/play.py --task Inspire-Wrench-Refactor-v3-Test --checkpoint outputs/wrench_refactor_v3_test_action_penalty/model_4550.pt --num_envs 4 --headless --device cuda:0 --seed 42 --max_steps 1000 > outputs/wrench_refactor_v3_test_action_penalty/play.log 2>&1
```

실험 조건: model4550, 왼쪽전용v3-Test, Joint Velocity 종료 비활성화, 기타 종료 유지,4환경×1000step, seed42. GPU에서 실제 inference policy를 실행하며 zero-action probe가 아니다. 후보 페널티로 재학습한 결과가 아니므로 성능 개선 효과는 판단하지 않는다.

### 실제 play 결과

CPU59개 통과(5.59초). 위 play 명령은 exit0으로 완료했다.4환경 각각1000policy step, 총4000쌍·중복0을 수집하고 기존비용=기존6축기여합+공통Hand, 후보비용=후보6축기여합+공통Hand, step reward=−0.02×cost 산술을 검증했다. summary.json, penalties.jsonl, penalties.csv, 전체play.log를 동일 outputs 폴더에 남겼다.

| cost(0.03계수 포함, dt곱 전) | 평균 | 중앙값 | p95 | 최대 |
| --- | ---: | ---: | ---: | ---: |
| 기존 정규화토크변화 | 0.03739927 | 0.01876202 | 0.13896003 | 0.49007756 |
| 후보raw정책출력변화, cap없음 | 25.10649467 | 5.42485332 | 40.92789078 | 24538.46679688 |
| 후보raw정책출력변화, Arm제곱합cap100 | 2.34805399 | 3.00000000 | 3.02999997 | 3.05999994 |

비용평균 비율은 후보/기존 671.310배, 중앙값 비율은 289.140배다. cap100을 유지해도 평균 62.783배이며 후보Arm비용은 64.6%샘플에서cap에 걸린다. 기존 정규화토크변화는6축 각각[-1,1]차분이므로 제곱합이 최대24이며 cap100은 실질적으로 작동하지 않는다. 반면 unbounded raw action의 후보cap100은 자주 작동한다.

후보위치3축평균 17.18590549, 회전3축평균 7.91558497, 공통Hand평균 0.00500384다. 후보Arm비용의 위치/회전 기여는 약68.5%/31.5%다. 기존관절별 평균(shoulder_pan/lift,elbow,wrist1/2/3)은 [0.01124407177996872, 0.011157797037060473, 0.005316287665056878, 0.003146661585484863, 0.0015288135134869563, 1.8001038114791533e-06]이며 wrist3의평균은 0.0000018001, 기존Arm기여의약 0.0056%뿐이다. 실제정규화토크변화가wrist3의움직임억제대리값으로아주작게나온다는사용자의우려를뒷받침한다. 후보회전3축은EEF RPY action축이며wrist3전용비용으로해석하지않는다.

초기episode step1은37샘플이며 이를제외해도평균비율 675.663배다. 따라서reset초기차이만으로큰차이가발생한것은아니다. 최대outlier는env2, globalpolicy step158, episodestep158, 후보비용24538.466797, 기존비용0.33279139다. 평균은outlier영향이있으므로중앙값/p95를함께보고한다.

실제반환된reward는기존이며, 평균기존step기여는 -0.000747985, 후보를동일계수로적용할경우평균step기여는 -0.502129879다. 비용함수를바꾸면서0.03을그대로유지하면학습보상규모가크게달라진다. 이번실험에서는reward를교체하거나재학습하지않았으므로성능개선·원인확정을주장하지않는다. 종료로그는object_fall_or_tilt18/shelf_failure14/timeout1회이며JointVelocity종료는없었다. seed1개·checkpoint1개·왼쪽분포에서의paired진단이다.

최종대조: 제어/보상반환값/기존history·reset/환경설정·부모동작 보존. v3-Test 비교print와play의선택적max_steps만추가. 원본학습로그·checkpoint는보존했고추론export는outputs복사본폴더에생성했다. 변경문서math·링크검사와코드diff whitespace검사를수행했다.

### 후속 분석: wrist3 고속 시점의 paired 비용

사용자가 wrist3속도가큰시점의기존/후보비용을질문했다. 재실행없이동일play.log의OSC JSON과penalties.jsonl을(env,physics_step//2=policy_step)로join했다. 최종substep(짝수physics_step)만선택하고episode step동일성을assert하여4000행을일대일매칭했다. 주의: OSC의current_joint_vel은마지막물리substep을적용하기직전입력상태다. reward비용은그계산에서출력된최종토크를사용하여해당substep후계산한다. 따라서같은제어step의paired값이지만속도샘플은reward평가시점보다물리1step(0.01초)앞서며, reward시점속도를별도수집한것은아니다.

abs(wrist3속도)>3rad/s인468행에서기존비용평균0.03730876/중앙값0.02204877, 후보평균17.29136576/중앙값6.55173898, 후보cap100유지평균2.59480411/중앙값3.0이었다. 기존wrist3단독기여평균은0.0000008421이다. abs속도>3.5인232행에서는기존평균0.03376859, 후보평균12.80331910, cap유지후보평균2.53306245였다.

예시: env0/globalstep289/episodestep117, wrist3−5.37373161rad/s, 기존전체0.14118490/후보전체17.65510368/cap후보3.0/기존wrist3기여0.00000011328. env3/globalstep40/episodestep40, +4.08329010rad/s, 기존0.00096597/후보1.55923390. env3/globalstep107/episodestep107, +4.00000334rad/s, 기존0.00060072/후보0.46722436. 이값은0.03계수포함,dt곱전이다. 후보는고속에서일관되게같은크기의비용을보장하는것은아니며,속도직접페널티가아닌action변화비용이다.

산출물: `outputs/wrench_refactor_v3_test_action_penalty/wrist3_penalty_comparison.json`에threshold별집계와속도상위10행을남겼다. 기존코드/실험/보상은추가변경하지않았다.

### 후속 분석: 후보Arm제곱합100초과의축별기여

penalties.jsonl에서후보Arm비용0.03×제곱합이3을넘는2584행을선택했다. 전체초과행의제곱합을누적한축별비중은positionX8.40%,Y37.02%,Z23.16%,rotationRoll20.93%,Pitch4.69%,Yaw5.79%였다. 큰outlier영향을구분하기위해합산비용상위1%를제외하면X16.97%,Y45.82%,Z6.77%,Roll12.90%,Pitch5.98%,Yaw11.57%다. positionY는2584행중1348행(52.2%)에서최대기여축이며,1338행에서는Y한축의변화제곱만100을넘었다. 즉주요원인은EEF위치Y명령의변화이며wrist3관절또는Yaw한축의변화로단정할수없다.

중앙초과샘플env3/globalstep169/episodestep50의raw변화량은[4.9022,−13.1925,−0.4514,−9.4400,4.5984,−5.1700]이다. Y변화제곱은약174.04로한축만으로100을넘고,전체제곱합은약335.26이다. 후보비용10.0579가cap유지시Arm3.0으로제한되는사례다. 산출물은 `outputs/wrench_refactor_v3_test_action_penalty/action_axis_cap100_analysis.json`이다. 분석은raw action의변화량제곱기준이며실제관절축과일대일대응하지않는다. 코드·reward·학습상태추가변경없음.
