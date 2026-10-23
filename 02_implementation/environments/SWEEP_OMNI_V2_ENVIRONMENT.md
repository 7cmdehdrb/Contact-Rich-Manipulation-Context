# Sweep Omni v2 — 독립 환경 요약

[환경 변화·계층](ENVIRONMENT_EVOLUTION.md) · [부모 Omni v1](SWEEP_OMNI_V1_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기준일: **2026-10-22**. Gym ID는 `Isaac-Inspire-Sweep-Omni-v2`다. 과거 실험 환경의 현재 코드 계약을 요약한다. 이번 확인은 코드 정독이며 새 학습·재생·실물 검증 결과가 아니다.

## 기본 구성

상시 음의 목표 거리 비용을 **새 목표 진행량에 대한 양의 보상**으로 바꾼 분기다. 물체에 먼저 접근한 뒤 실제 목표 이동을 만들도록 Reaching과 Goal을 나누고, 비용을 피하기 위해 일찍 끝내는 유인을 줄이려는 의도다. 성공 종료·terminal 보너스·시간 비용을 제거한다.

| 항목 | 현재 설정 |
| --- | --- |
| 설정 클래스 / 직접 부모 | `InspireSweepOmniV2EnvCfg` / `InspireSweepOmniV1EnvCfg` |
| 실행 클래스 | `InspireSweepEnv` |
| 장면 | UR5e–Axia80 하우징–Inspire Hand, 선반 높이 1.05 m, 반지름 4 cm·높이 10 cm 원통 1개 |
| 물성 | 질량 평균 0.365 kg·표준편차 0.0675 kg를 `[0.230,0.500]` kg로 제한; 선반·물체·Hand 마찰 무작위화 |
| Reset / 목표 | 선반 중앙 반지름 2 cm 원판·yaw 무작위; 전방향 목표 최대 15 cm, 가장자리에서 거리 단축 |
| Action | Arm Joint Position 6D(기본각 + `0.5 × action`) + Hand 굽힘/opposition 개방도 2D |
| 시간 / 기본 규모 | 물리 0.01 s × decimation 2 → 50 Hz; 10초, 기본 4096환경 |
| 부모에서 유지 | 41D 관측, 로봇 기본 관절 자세, 질량·마찰·센서, Arm 종료 임계값 1.5 rad/s |

선반 반폭은 X/Y 0.20/0.50 m이며 목표는 원통 반지름+2 cm 여유를 남긴다. 물성 상세는 같은 helper를 쓰는 [Realistic Physics](SWEEP_REALISTIC_PHYSICS_ENVIRONMENT.md)와 같다.

## 관측 정보

Actor와 Critic은 모두 아래 순서의 `policy` **41D**다. 목표는 episode 동안 고정되지만 물체 위치는 계속 갱신한다.

| Term | 차원 | 의미 |
| --- | --- | --- |
| `joint_pos` | 6 | Arm 관절각 − 기본각 |
| `joint_vel` | 6 | Arm 관절속도 − 기본속도 |
| `actions` | 8 | 직전 raw Arm 6D + Hand 2D action |
| `target_obs_state` | 3 | 현재 물체 바닥 위치, Robot root 좌표계 |
| `target_obj_width` | 1 | 물체 반지름 0.04 m |
| `ee_pose` | 7 | EEF 위치·quaternion, Robot root 좌표계 |
| `goal_pos` | 3 | 고정 목표 위치, Robot root 좌표계 |
| `tactile` | 1 | palm pad 접촉력 크기 ≥0.05 N 여부 |
| `wrist_wrench` | 6 | EEF 축·원점의 미상쇄 fixed-joint 반력, N 및 N·m |

물체 위치·반지름에는 ±0.01 m 균등 가산 노이즈를 적용한다. Hand 관절 상태·물성의 직접 입력, privileged 그룹, history stack은 없다. Reset 직후 센서 미갱신 행은 tactile·F/T가 0이다. 현재 물체 위치 GT를 입력하므로 최종 Blind actor와 구분한다.

## 보상 구조

**활성 8항**과 부모에서 제거한 3항을 함께 표기한다. RewardManager는 `weight × Δt`를 곱한다. 두 진행 함수는 내부에서 `Δt=0.02 s`로 나누므로 누적 진행 보상은 시간 간격에 다시 비례하지 않는다.

| Term | Weight / 상태 | 함수와 계산·역할 |
| --- | ---: | --- |
| `reaching` | +30.0 | `CurrentObjectReachProgress`: **현재 물체**의 3D 반경 10 cm 구까지 새 최단 접근 기록; 총 양의 예산 최대 +30 |
| `goal_distance` | +40.0 | `PlanarGoalProgress`: XY 목표 1 cm 이내까지 새 최고 진행률 증가; 총 예산 최대 +40 |
| `arm_action_rate` | −0.03 | raw Arm 6D action 변화량 제곱합, 합산 후 상한 100 |
| `hand_action_rate` | −0.03 | raw Hand 2D action 변화량 제곱합, 합산 후 상한 100 |
| `arm_joint_velocity` | −0.03 | Arm 실제 관절속도 제곱합, 합산 후 상한 100 |
| `hand_joint_velocity` | −0.01 | Hand 12관절 실제 속도 제곱합, 합산 후 상한 100 |
| `object_tilt` | −2.0 | 선반 법선 대비 5° 초과 기울기부터 제곱 비용; 0.9 rad에서 원시값 1로 포화 |
| `shelf_collision` | −0.5 | 선반 움직임 및 가상 손가락/손목의 선반 근접 비용 |
| `time` | 제거 (`None`) | 시간 비용 없음 |
| `success` | 제거 (`None`) | 성공 terminal 보너스 없음 |
| `failure` | 제거 (`None`) | 실패 terminal 비용 없음; 실패 종료 자체는 유지 |

`reaching`은 reset 때의 EEF–물체 거리를 정규화 기준으로 삼되 매 step 현재 물체 위치로 거리를 계산한다. 10 cm 구까지의 남은 거리에서 새 episode 최단 기록을 만든 몫만 지급한다. 정지·왕복으로 같은 기록을 반복해도 재지급하지 않는다. 물체가 EEF 쪽으로 움직여 상대 거리가 줄어도 진행으로 계산한다.

`goal_distance`는 초기 목표 거리에서 허용 오차 1 cm를 뺀 거리를 전체 과제로 삼는다. 현재 진행률을 `[0,1]`로 제한하고 episode 최고 진행률의 증가분만 지급한다. 목표 도달·대기·이탈 후 재진입으로 같은 예산을 반복 수령할 수 없고, 이미 목표 안에서 시작하면 예산은 0이다.

네 운동 비용은 로컬 `goal_rewards.action_rate_l2`·`joint_vel_l2`의 raw 제곱합이다. Arm/Hand를 나누며 평균·정규화·Hand 입력 clamp를 사용하지 않는다. 과거 개발 로그의 +200/+400 등 중간 계수와 구분해 **현재 코드의 +30/+40**을 기재했다.

## 터미네이션

| Term | 현재 종료 조건 | 종류 |
| --- | --- | --- |
| `time_out` | 10초 | Timeout |
| `object_drop` | 물체 바닥 높이 <1.04 m 또는 선반 법선 대비 기울기 ≥0.9 rad | 실패 |
| `push_fast` | 물체 3D 속력 >0.3 m/s | 실패 |
| `shelf_collision` | 선반 6D 속도 norm >0.1, 가상 손목 판 위 높이 <7 cm, 또는 가상 손가락 <1 cm | 실패 |
| `hand_velocity` | **Arm** 6관절 중 속도 절댓값 >1.5 rad/s | 실패 |
| `object_outside_shelf` | 물체 바닥 원점이 선반 X/Y 반폭 0.20/0.50 m 밖 | 실패 |
| `shelf_displacement` | 선반 초기 위치 대비 이동 >5 cm | 실패 |
| `success` | 제거 (`None`); 목표에 도달해도 episode 계속 진행 | 비활성 |

성공 종료를 제거했으므로 목표 1 cm 도달 보상과 종료를 혼동하지 않는다. 모든 양의 진행 예산을 소진한 뒤에도 실패 또는 10초 timeout까지 실행한다.

## 커리큘럼

| 항목 | 적용 여부·설명 |
| --- | --- |
| CurriculumManager 항 | 없음 |
| Reset 무작위화 | 원판 위치·yaw·목표 방향·질량·마찰; 학습 진도에 따른 변경 없음 |

## 근거와 연결

- [Omni v2 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_envs.py), [진행·비용 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_rewards.py)
- [종료 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/goal_terminations.py), [v2 도입·후속 변경 이력](../logs/2026-10-15_omni_v2_rewards.md)
- [운동 비용 계약 이력](../logs/2026-10-15_omni_penalty_contract.md), [공통 상한 이력](../logs/2026-10-18_omni_squared_cost_caps.md)
- 다음 분기: [Omni v3](SWEEP_OMNI_V3_ENVIRONMENT.md), [Dex Omni v0](DEX_OMNI_V0_ENVIRONMENT.md)

학습 성과와 목표 정착 품질은 이번 문서 작업에서 평가하지 않았다. 과거 checkpoint의 저장 설정은 별도로 확인해야 한다.
