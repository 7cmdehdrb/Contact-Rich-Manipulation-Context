# Sweep Omni Renewal OSC v0

[환경 변화 지도](ENVIRONMENT_EVOLUTION.md) · [부모: Omni Renewal v0](SWEEP_OMNI_RENEWAL_ENVIRONMENT.md) · [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)

기준일: 2026-10-22. 과거 실험 환경의 간략 참조 문서이며, 현재 작업트리의 등록·Cfg·MDP를 정적으로 확인한 계약이다. 학습 성과나 이번 작업의 simulator 실행 결과를 뜻하지 않는다.

## 기본 구성과 변경 의도

Renewal의 과업·보상·종료를 유지하면서 Arm을 관절 위치 명령에서 상대 Cartesian pose OSC로 교체한 제어 비교 분기다. OSC가 effort를 출력하므로 Arm의 기존 implicit PD stiffness/damping을 0으로 설정한다.

| 항목 | 적용 내용 |
| --- | --- |
| Gym ID | `Isaac-Inspire-Sweep-Omni-Renewal-OSC-v0` |
| 환경 Cfg | `InspireSweepOmniRenewalOSCEnvCfg` |
| 직접 부모 | `InspireSweepOmniRenewalEnvCfg` |
| Runtime | `InspireSweepEnv` → `ManagerBasedRLEnv` |
| 장면 | UR5e–Axia80 하우징–Inspire Hand, 선반, 반지름 4 cm·높이 10 cm 원통 1개 |
| 주기·환경 수 | physics 0.01 s, decimation 2 → 제어 0.02 s; 기본 4096개, 간격 2.5 m |
| Action | 8D: 상대 EEF pose 6D → OSC; stiffness 200, damping ratio 1; position/orientation scale 1.0; Hand openness 2D |
| 물체 질량 | 생성 0.365 kg; reset은 평균 0.365·표준편차 파라미터 0.0675 kg의 Gaussian을 0.230–0.500 kg로 clamp |
| Reset·목표 | 고정 로봇 초기 자세; 선반 중심 반경 2 cm 원판 스폰·yaw 균등; 선반 로컬 XY 360° 방향을 각도 균등 샘플 |
| 목표 거리 | 최대 15 cm; 선반 반폭 (0.20, 0.50) m에서 물체 반지름 4 cm+여유 2 cm를 남기도록 방향을 유지하며 단축 |
| 마찰 | Realistic Physics의 episode별 재샘플링과 Average 결합 재사용 |
| 학습 입력 | Actor와 Critic 모두 동일한 `policy` 41D; 별도 privileged group 없음 |

Hand의 두 입력은 공통 굽힘과 엄지 opposition을 12개 관절 위치로 매핑한다. 제어용 openness는 [0,1]로 제한되지만 보상은 처리 전 raw action을 사용한다.

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
| `tactile` | 1 | 손바닥 단일 pad 접촉 bit; 임계값 0.05 N |
| `wrist_wrench` | 6 | EEF 기준점·좌표계의 Fx,Fy,Fz,Mx,My,Mz; N/N·m, 중력·관성 미보정 |
| 합계 | 41 | Actor/Critic 공통 |

Reset 직후에는 sensor freshness mask로 촉각·wrench를 0 처리한다. Arm 상태 외에 Hand 관절 위치·속도를 별도로 관측하지 않는다.

## 보상 구조

아래 표는 상속과 `__post_init__` 변경을 반영한 전체 활성 보상이다. RewardManager는 기본적으로 `weight × term × 0.02 s`를 합산하며, 진행·일회성 event는 함수 내부의 `/step_dt`로 시간 곱을 상쇄한다.

| 항 | 함수 | weight | 의미·주요 파라미터 |
| --- | --- | ---: | --- |
| `reaching` | HeightGatedPlanarReachProgress | +30 | 현재 물체까지 XY 접근; 10 cm deadzone, Z=물체 원점+9 cm의 ±2 cm 높이 조건; 최고 기록 대비 후퇴 비용 |
| `goal_distance` | PlanarGoalProgress | +40 | 초기 목표 거리로 정규화한 새 최고 XY 진행량; 1 cm 허용 반경 |
| `arm_action_rate` | 로컬 `goal_rewards.action_rate_l2` | −0.03 | Arm raw action 6개의 변화량 제곱합; 합산 후 상한 100 |
| `hand_action_rate` | 로컬 `goal_rewards.action_rate_l2` | −0.03 | Hand raw action 2개의 변화량 제곱합; 합산 후 상한 100 |
| `arm_joint_velocity` | 로컬 `goal_rewards.joint_vel_l2` | −0.03 | 실제 Arm 6개 관절 속도 제곱합; 합산 후 상한 100 |
| `hand_joint_velocity` | 로컬 `goal_rewards.joint_vel_l2` | −0.01 | 실제 Hand 12개 관절 속도 제곱합; 합산 후 상한 100 |
| `object_tilt` | `object_tilt_cost` | −2 | 선반 법선 대비 기울기; 5° 이내 0, 0.9 rad에서 포화하는 정규화 제곱 비용 |
| `shelf_collision` | `ShelfCollisionPenalty` | −0.5 | 선반 변위+속도 norm 합 >0.005; EEF 근처에서 가상 finger·wrist 낮은 높이 비용 추가 |
| `pushing_speed` | `exponential_pushing_speed_cost` | −1 | 물체 3D 선속도 norm의 0.3 m/s 초과; 유한 상한 없음 |
| `arm_speed_excess` | `exponential_joint_speed_cost` | −1 | Arm 최대 절대 관절 속도의 1 rad/s 초과; 유한 상한 없음 |

`time`·`failure` 보상은 없고, `success`·`goal_hold` 보상도 없다. Baseline의 orientation·sweeping_object·homing_after_sweep·object_collision은 Renewal 보상 Cfg에 포함되지 않는다.

Reaching은 현재 물체에 대한 **XY 거리**를 사용한다. 새 최고 접근은 EEF가 물체 원점+9 cm의 ±2 cm 높이 범위에 있을 때만 지급한다. 최고 기록보다 멀어지면 높이와 무관하게 매 step 음수가 되며, 높이 밖에서 세운 XY 기록도 갱신되어 나중에 Z만 바꾸어 재수령할 수 없다. Goal은 초기 목표 거리로 정규화한 새 최고 진행만 지급하고, 목표 허용 반경 도달 시 총 +40 예산을 소진한다.

속도 지수 비용은 `0.5 × expm1(2 × max(speed − free_speed, 0))`다. 네 운동 제곱합 항은 평균·정규화·Hand 입력 clamp 없이 계산한 후 최종 scalar 비용만 100으로 제한한다.

## 터미네이션

| 항 | 조건 | 결과 |
| --- | --- | --- |
| `time_out` | 10초, 최대 500 제어 step | timeout |
| `object_drop` | 물체 원점 높이 <1.04 m(환경 원점 기준) 또는 선반 법선 대비 기울기 ≥0.9 rad | 실패 |
| `push_fast` | 물체 3D 선속도 norm >0.8 m/s | 실패 |
| `shelf_collision` | 선반 root 6D velocity norm >0.1 또는 가상 wrist의 선반 표면 위 높이 <0.07 m; finger 높이 검사는 꺼짐 | 실패 |
| `hand_velocity` | 실제 Arm 6개 중 하나라도 절대속도 >5 rad/s; 이름과 달리 Hand 검사가 아님 | 실패 |
| `shelf_displacement` | 선반 위치가 초기 위치에서 3D 거리 >0.05 m | 실패 |
| `object_outside_shelf` | `None`, 별도 외곽 종료 없음 | 비활성 |
| `success` | 활성 term 없음 | 성공 종료 없음 |

## 커리큘럼

| 항목 | 적용 |
| --- | --- |
| CurriculumManager 일정 | 없음; iteration에 따른 보상·목표·종료 변경을 등록하지 않음 |
| Reset randomization | 질량·마찰·위치·방향 재샘플링은 episode randomization이며 curriculum이 아님 |

## 근거와 확인 범위

- [현재 환경 Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/omni_renewal_osc_env_cfg.py) · [등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py) · [공통 Renewal Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/omni_renewal_env_cfg.py)
- [관측 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations.py) · [보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/goal_rewards.py) · [종료 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/goal_terminations.py)
- 변경 의도·당시 실행 기록: [2026-10-15_renewal_osc](../logs/2026-10-15_renewal_osc.md) · [2026-10-16_renewal_only_exponential](../logs/2026-10-16_renewal_only_exponential.md)

이번 문서화에서는 새 train/play·성공률 평가·실물 실험을 실행하지 않았다. 과거 로그의 검증 결과는 해당 날짜·설정에 한정하며, 위 계약은 2026-10-22 작업트리 기준이다. 코드 링크는 통합 workspace checkout을 전제로 한다.
