# Sweep Omni v4 — 독립 환경 요약

[환경 변화·계층](ENVIRONMENT_EVOLUTION.md) · [부모 Omni v3](SWEEP_OMNI_V3_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기준일: **2026-10-22**. Gym ID는 `Isaac-Inspire-Sweep-Omni-v4`다. 현재 코드의 과거 실험 환경 계약을 요약한다. 이번 문서화는 코드 정독 기준이며 새 학습·재생·실물 검증 결과가 아니다.

## 기본 구성

Omni v3의 높이 조건을 갖는 수평 Reaching을 유지하면서 속도 종료를 완화하고, 물체·Arm의 허용 속도 초과를 연속 비용으로 학습시키는 분기다. 선반 XY 범위 이탈만으로는 바로 종료하지 않도록 변경했다.

| 항목 | 현재 설정 |
| --- | --- |
| 설정 클래스 / 직접 부모 | `InspireSweepOmniV4EnvCfg` / `InspireSweepOmniV3EnvCfg` |
| 실행 클래스 | `InspireSweepEnv` |
| 장면 | UR5e–Axia80 하우징–Inspire Hand, 높이 1.05 m 선반, 반지름 4 cm·높이 10 cm 원통 1개 |
| 물성 | 질량 평균 0.365 kg·표준편차 0.0675 kg를 `[0.230,0.500]` kg로 제한; 선반·원통·Hand 마찰 무작위화 |
| Reset / 목표 | 선반 중앙 반지름 2 cm 원판·yaw 무작위; 전방향 목표 최대 15 cm, 원통 반지름+2 cm edge clearance |
| Action | Arm Joint Position 6D(기본각 + `0.5 × action`) + Hand 굽힘/opposition 개방도 2D |
| 시간 / 기본 규모 | 물리 0.01 s × decimation 2 → 50 Hz, 10초, 기본 4096환경 |
| v3 대비 종료 변경 | Arm 1.5 → 5.0 rad/s, 물체 0.3 → 0.5 m/s; `object_outside_shelf` 제거 |

물체 스폰·목표 분포, 로봇 기본 관절 자세와 센서는 v3를 상속한다. 선반 반폭은 X/Y 0.20/0.50 m다. 물성 분포는 [Realistic Physics](SWEEP_REALISTIC_PHYSICS_ENVIRONMENT.md)의 helper와 같다.

## 관측 정보

Actor와 Critic 모두 아래 순서의 `policy` **41D**를 사용한다. 별도 privileged 입력이나 observation history stack은 없다.

| Term | 차원 | 의미 |
| --- | --- | --- |
| `joint_pos` | 6 | 기본각 대비 Arm 관절각 |
| `joint_vel` | 6 | 기본속도 대비 Arm 관절속도 |
| `actions` | 8 | 직전 raw Arm 6D + Hand 2D action |
| `target_obs_state` | 3 | 현재 물체 바닥 위치, Robot root 좌표계 |
| `target_obj_width` | 1 | 실제 값은 반지름 0.04 m |
| `ee_pose` | 7 | Robot root 기준 EEF 위치·quaternion |
| `goal_pos` | 3 | Robot root 기준 episode 고정 목표 위치 |
| `tactile` | 1 | palm pad 접촉력 크기 ≥0.05 N의 bit |
| `wrist_wrench` | 6 | EEF 축·원점의 미상쇄 fixed-joint 반력, N 및 N·m |

물체 위치·반지름은 ±0.01 m 가산 균등 노이즈를 받는다. 물체 위치는 현재 GT에서 갱신하므로 Blind actor가 아니다. Hand 관절 상태·물성은 직접 입력하지 않는다. Reset 직후 센서가 미갱신된 행은 tactile·F/T가 0이다.

## 보상 구조

**활성 10항**과 제거된 3항을 아래 한 표에 정리한다. RewardManager가 `weight × Δt`를 곱한다. Reaching·Goal은 내부 `/Δt`를 사용하고 나머지 비용에는 `Δt=0.02 s`가 남는다.

| Term | Weight / 상태 | 함수와 계산·역할 |
| --- | ---: | --- |
| `reaching` | +30.0 | `HeightGatedPlanarReachProgress`: 현재 물체 XY 접근의 기록 개선에 높이 게이트, 기록에서 멀어지면 음의 값 |
| `goal_distance` | +40.0 | `PlanarGoalProgress`: XY 목표 1 cm까지 새 최고 진행률 증가, 예산 최대 +40 |
| `arm_action_rate` | −0.03 | raw Arm 6D 변화량 제곱합, 합산 후 상한 100 |
| `hand_action_rate` | −0.03 | raw Hand 2D 변화량 제곱합, 합산 후 상한 100 |
| `arm_joint_velocity` | −0.03 | Arm 실제 관절속도 제곱합, 합산 후 상한 100 |
| `hand_joint_velocity` | −0.01 | Hand 12관절 실제 속도 제곱합, 합산 후 상한 100 |
| `object_tilt` | −2.0 | 선반 법선 대비 5°까지 비용 0, 0.9 rad까지 증가하는 제곱 비용, 원시 상한 1 |
| `shelf_collision` | −0.5 | 선반 움직임·가상 손가락/손목 근접 비용 |
| `pushing_speed` | −0.05 | 물체 3D 속력의 0.3 m/s 초과분을 0.2 m/s로 나눈 제곱 |
| `arm_speed_excess` | −0.03 | Arm 관절 최대 절대속도의 1.0 rad/s 초과분을 1.0 rad/s로 나눈 제곱 |
| `time` | 제거 (`None`) | 시간 비용 없음 |
| `success` | 제거 (`None`) | 성공 terminal 보너스 없음 |
| `failure` | 제거 (`None`) | 실패 terminal 비용 없음 |

Reaching은 EEF–현재 물체의 XY 거리에서 10 cm를 뺀 남은 거리를 사용한다. 새 최단 기록 개선은 EEF 높이가 **물체 바닥 +9 cm의 ±2 cm** 안일 때만 지급한다. 높이 밖에서도 기록은 갱신하여 Z만 바꿔 이전 진행을 재수령하지 못하게 한다. 현재 공통 함수는 이전 최단 기록보다 멀어져 있으면 매 step 음의 비용을 주며, 이 비용에는 높이 게이트가 없다. 초기 접근거리가 0이면 정규화 분모로 10 cm를 사용한다.

새 `pushing_speed`는 0.3 m/s 이하에서 0이고 0.5 m/s에서 원시값 1이다. `arm_speed_excess`는 Arm 중 가장 빠른 관절 하나의 절대속도를 기준으로 1 rad/s 이하에서 0, 2 rad/s에서 원시값 1이다. 두 항은 **제곱 초과 비용**이며 Renewal 계열의 지수 비용과 다르다. 기준속도에서 포화되는 함수가 아니다.

기존 네 운동 비용은 별도로 유지한다. 로컬 `goal_rewards.action_rate_l2`·`joint_vel_l2`를 사용하며 raw action·실제 속도를 Arm/Hand별로 제곱합한다. 평균·정규화·Hand 입력 clamp는 보상 계산에 적용하지 않는다.

## 터미네이션

| Term | 현재 종료 조건 | 종류 |
| --- | --- | --- |
| `time_out` | 10초 | Timeout |
| `object_drop` | 물체 바닥 높이 <1.04 m 또는 선반 법선 대비 기울기 ≥0.9 rad | 실패 |
| `push_fast` | 물체 3D 속력 >0.5 m/s | 실패 |
| `shelf_collision` | 선반 6D 속도 norm >0.1, 가상 손목 판 위 높이 <7 cm, 또는 가상 손가락 <1 cm | 실패 |
| `hand_velocity` | **Arm** 6관절 중 속도 절댓값 >5.0 rad/s | 실패 |
| `shelf_displacement` | 선반 초기 위치 대비 이동 >5 cm | 실패 |
| `object_outside_shelf` | 제거 (`None`); XY 경계를 넘는 것만으로 종료하지 않음 | 비활성 |
| `success` | 제거 (`None`); 목표 도달 후에도 계속 실행 | 비활성 |

XY 이탈 종료 제거 후에도 물체 낙하·기울기와 선반 충돌 종료는 남는다. 속도 임계값과 정확히 같으면 해당 속도 term은 종료하지 않는다.

## 커리큘럼

| 항목 | 적용 여부·설명 |
| --- | --- |
| CurriculumManager 항 | 없음 |
| Reset 무작위화 | 원판 위치·yaw·목표 방향·질량·마찰; 진행도별 일정 없음 |

## 근거와 연결

- [Omni v4 설정·상속](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_envs.py), [Reaching·속도 비용](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_rewards.py)
- [v4 속도 비용 도입](../logs/2026-10-15_omni_v4_speed_penalty.md), [Arm 추가 비용](../logs/2026-10-15_omni_v4_arm_speed_excess.md), [저장 run 기준값 반영](../logs/2026-10-15_omni_v4_saved_parameters.md)
- [공통 제곱 비용 상한](../logs/2026-10-18_omni_squared_cost_caps.md), [부모 v3 상세 문서](SWEEP_OMNI_V3_ENVIRONMENT.md)

기존 v3 상세 문서와 개발 로그는 작성 당시 계약을 담는다. Reaching의 후퇴 비용·합산 상한은 현재 공통 함수 기준으로 위에 명시했다. 이번 작업에서 속도 억제 성능이나 학습 성공률은 평가하지 않았다.
