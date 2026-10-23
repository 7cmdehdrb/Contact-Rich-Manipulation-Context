# Dex Tactile Sweep Omni Renewal OSC v2

[환경 변화 지도](ENVIRONMENT_EVOLUTION.md) · [부모: Dex Tactile Renewal v2](DEX_TACTILE_OMNI_RENEWAL_V2_ENVIRONMENT.md) · [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)

기준일: 2026-10-22. 과거 실험 환경의 간략 참조 문서이며, 현재 작업트리의 등록·Cfg·MDP를 정적으로 확인한 계약이다. 학습 성과나 이번 작업의 simulator 실행 결과를 뜻하지 않는다.

## 기본 구성과 변경 의도

v2의 안정 체류 보상과 실패 조건을 유지하면서 Arm 제어만 stiffness 100의 상대 pose OSC로 교체한다. 한 명령의 이동·회전 norm을 각각 5 mm·0.025 rad로 제한해 초기 제어 응답을 줄이는 분기다. 이 명령 제한 자체가 실제 관절 과속을 보장해서 막는 것은 아니다.

| 항목 | 적용 내용 |
| --- | --- |
| Gym ID | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2` |
| 환경 Cfg | `InspireDexTactileSweepOmniRenewalV2OSCEnvCfg` |
| 직접 부모 | `InspireDexTactileSweepOmniRenewalV2EnvCfg` |
| Runtime | `InspireSweepEnv` → `ManagerBasedRLEnv` |
| 장면 | UR5e–Axia80 하우징–Inspire Hand, 선반, 반지름 4 cm·높이 10 cm 원통 1개 |
| 주기·환경 수 | physics 0.01 s, decimation 2 → 제어 0.02 s; 기본 4096개, 간격 2.5 m |
| Action | 8D: 상대 EEF pose 6D → OSC; stiffness 100, damping ratio 1; scale 0.005 m / 0.025 rad, 각 벡터 norm도 같은 값으로 제한; Hand openness 2D |
| 물체 질량 | 생성 0.365 kg; reset은 평균 0.365·표준편차 파라미터 0.0675 kg의 Gaussian을 0.230–0.500 kg로 clamp |
| Reset·목표 | 고정 로봇 초기 자세; 선반 중심 반경 2 cm 원판 스폰·yaw 균등; 선반 로컬 ±X 각각 ±15°를 제외한 허용 방향에서 각도 균등 샘플 |
| 목표 거리 | 최대 15 cm; 선반 반폭 (0.20, 0.50) m에서 물체 반지름 4 cm+여유 2 cm를 남기도록 방향을 유지하며 단축 |
| 마찰 | Realistic Physics의 episode별 재샘플링과 Average 결합 재사용 |
| 학습 입력 | Actor와 Critic 모두 동일한 `policy` 57D; 별도 privileged group 없음 |

Hand의 두 입력은 공통 굽힘과 엄지 opposition을 12개 관절 위치로 매핑한다. 제어용 openness는 [0,1]로 제한되지만 보상은 처리 전 raw action을 사용한다.

현재 Arm `velocity_limit_sim`은 앞 3개(shoulder pan/lift·elbow) 각각 2 rad/s, wrist 3개 각각 4 rad/s다. 종료 검사는 별도로 실제 Arm 속도 >5 rad/s를 사용한다.

OSC는 현재 EEF 기준 상대 pose, 고정 impedance, 관성 동역학 decoupling·중력 보상을 사용한다. Arm implicit PD stiffness/damping은 0이며 Hand 위치 제어는 유지한다.

## 관측 정보

`policy`는 아래 순서로 연결한다. 현재 물체 위치가 매 step 입력되므로 Blind actor가 아니다. 일반 observation stack은 없다.

| 항 | 차원 | 의미 |
| --- | ---: | --- |
| `joint_pos` | 6 | Arm 관절 위치 − 기본 위치 |
| `joint_vel` | 6 | Arm 관절 속도 − 기본 속도 |
| `actions` | 8 | 직전 제어에 사용된 raw action; OSC에서는 앞 6개가 Cartesian 명령 |
| `target_obs_state` | 3 | 현재 물체 원점 XYZ, robot root 기준; 매 관측 uniform ±1 cm 노이즈 |
| `target_obj_width` | 1 | 이름은 width지만 값은 물체 반지름 0.04 m; uniform ±1 cm 노이즈 |
| `ee_pose` | 7 | robot root 기준 EEF XYZ + quaternion |
| `goal_pos` | 3 | robot root 기준 목표 XYZ |
| `tactile` | 17 | 각 pad 직접 접촉 또는 해당 영역에 투영된 parent–물체 접촉의 bit; 임계값 0.01 N |
| `wrist_wrench` | 6 | EEF 기준점·좌표계의 Fx,Fy,Fz,Mx,My,Mz; N/N·m, 중력·관성 미보정 |
| 합계 | 57 | Actor/Critic 공통 |

Reset 직후에는 sensor freshness mask로 촉각·wrench를 0 처리한다. Arm 상태 외에 Hand 관절 위치·속도를 별도로 관측하지 않는다.

17채널은 기존 pad 형상을 유지한다. 직접 pad 접촉은 상대 물체를 제한하지 않고, parent 접촉 보충은 원통과의 접촉점 중 pad 영역에 들어오는 점만 사용한다. 접촉 물체 ID는 관측에 넣지 않는다.

## 보상 구조

아래 표는 상속과 `__post_init__` 변경을 반영한 전체 활성 보상이다. RewardManager는 기본적으로 `weight × term × 0.02 s`를 합산하며, 진행·일회성 event는 함수 내부의 `/step_dt`로 시간 곱을 상쇄한다.

| 항 | 함수 | weight | 의미·주요 파라미터 |
| --- | --- | ---: | --- |
| `reaching` | DexReachProgress | +30 | 현재 물체 밑면 원점까지 3D 거리의 새 최고 접근량(m); 10 cm 이내 제외 |
| `goal_distance` | DexPlanarGoalProgress | +300 | 목표 XY까지 새 최고 진행량(m); 1 cm 허용 반경 |
| `arm_action_rate` | 로컬 `goal_rewards.action_rate_l2` | −0.03 | Arm raw action 6개의 변화량 제곱합; 합산 후 상한 100 |
| `hand_action_rate` | 로컬 `goal_rewards.action_rate_l2` | −0.03 | Hand raw action 2개의 변화량 제곱합; 합산 후 상한 100 |
| `arm_joint_velocity` | 로컬 `goal_rewards.joint_vel_l2` | −0.03 | 실제 Arm 6개 관절 속도 제곱합; 합산 후 상한 100 |
| `hand_joint_velocity` | 로컬 `goal_rewards.joint_vel_l2` | −0.01 | 실제 Hand 12개 관절 속도 제곱합; 합산 후 상한 100 |
| `object_tilt` | `object_tilt_cost` | −2 | 선반 법선 대비 기울기; 5° 이내 0, 0.9 rad에서 포화하는 정규화 제곱 비용 |
| `shelf_collision` | `ShelfCollisionPenalty` | −0.5 | 선반 변위+속도 norm 합 >0.005; EEF 근처에서 가상 finger·wrist 낮은 높이 비용 추가 |
| `pushing_speed` | `exponential_pushing_speed_cost_limit` | −1 | 물체 3D 선속도 norm의 0.3 m/s 초과; 출력 상한 100 |
| `arm_speed_excess` | `exponential_joint_speed_cost_limit` | −1 | Arm 최대 절대 관절 속도의 1 rad/s 초과; 출력 상한 100 |
| `success` | `StableGoalAchievement` | +100 | 아래 안정 조건을 0.5초 연속 만족한 최초 1회, 종료 없음 |
| `goal_hold` | `stable_goal_hold` | +20 | 연속 유지 시간/0.5초를 [0,1]로 제한; 최대 +20/초 |

`time`·`failure` 보상은 없고, 성공 보너스 외 별도 종료 보상도 없다. Baseline의 orientation·sweeping_object·homing_after_sweep·object_collision은 Renewal 보상 Cfg에 포함되지 않는다.

Dex 접근은 현재 물체 밑면 원점까지의 **3D 거리**를 사용하며 높이 gate·초기 거리 정규화가 없다. 접근·목표 보상 모두 episode 최고 기록을 새로 갱신한 거리만 지급하므로 대기·후퇴·이미 방문한 거리로 복귀하면 다시 받지 않는다.

속도 지수 비용은 `0.5 × expm1(2 × max(speed − free_speed, 0))`다. 네 운동 제곱합 항은 평균·정규화·Hand 입력 clamp 없이 계산한 후 최종 scalar 비용만 100으로 제한한다.

이 환경의 두 지수 비용은 overflow를 막도록 지수 계산 전에도 제한한다. weight·dt 반영 후 `pushing_speed`의 1 step 최저 기여는 −2, `arm_speed_excess`는 −2이며 전체 reward의 하한을 뜻하지 않는다.

안정 조건은 목표 XY 오차 <1 cm, XY 속도 <0.02 m/s, 기울기 ≤10°, 원통 반지름을 포함한 선반 내부 지지 및 밑면 높이 오차 ≤1 cm, 기존 실패 없음이다. 연속 0.5초(25 step)에 +100을 처음 한 번만 받고, 유지 보상은 이후에도 계속된다. 이탈 시 유지 timer만 0으로 돌아가며 재진입으로 +100을 다시 받지 않는다.

## 터미네이션

| 항 | 조건 | 결과 |
| --- | --- | --- |
| `time_out` | 10초, 최대 500 제어 step | timeout |
| `object_drop` | 물체 원점 높이 <1.04 m(환경 원점 기준) 또는 선반 법선 대비 기울기 ≥0.9 rad | 실패 |
| `push_fast` | 물체 3D 선속도 norm >0.8 m/s | 실패 |
| `shelf_collision` | 선반 root 6D velocity norm >0.1 또는 가상 wrist의 선반 표면 위 높이 <0.03 m; finger 높이 검사는 꺼짐 | 실패 |
| `hand_velocity` | 실제 Arm 6개 중 하나라도 절대속도 >5 rad/s; 이름과 달리 Hand 검사가 아님 | 실패 |
| `shelf_displacement` | 선반 위치가 초기 위치에서 3D 거리 >0.05 m | 실패 |
| `object_outside_shelf` | `None`, 별도 외곽 종료 없음 | 비활성 |
| `success` | `None`; 안정 달성은 보상 event로만 처리 | 성공 종료 없음 |

## 커리큘럼

| 항목 | 적용 |
| --- | --- |
| CurriculumManager 일정 | 없음; iteration에 따른 보상·목표·종료 변경을 등록하지 않음 |
| Reset randomization | 질량·마찰·위치·방향 재샘플링은 episode randomization이며 curriculum이 아님 |

## 근거와 확인 범위

- [현재 환경 Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_renewal_envs.py) · [등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py) · [공통 Renewal Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_renewal_envs.py)
- [관측 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/sweep.py) · [보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_rewards.py) · [종료 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/goal_terminations.py)
- [Dex 보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/dex_rewards.py)
- [최초 달성 latch·유지 timer](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_hold_rewards.py)
- 변경 의도·당시 실행 기록: [2026-10-18_dex_tactile_renewal_v2_osc](../logs/2026-10-18_dex_tactile_renewal_v2_osc.md) · [2026-10-18_v2_inherits_v1](../logs/2026-10-18_v2_inherits_v1.md)

이번 문서화에서는 새 train/play·성공률 평가·실물 실험을 실행하지 않았다. 과거 로그의 검증 결과는 해당 날짜·설정에 한정하며, 위 계약은 2026-10-22 작업트리 기준이다. 코드 링크는 통합 workspace checkout을 전제로 한다.
