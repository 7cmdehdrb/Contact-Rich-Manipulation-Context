# Sweep Omni v1 — 독립 환경 요약

[환경 변화·계층](ENVIRONMENT_EVOLUTION.md) · [부모 Omni v0](OMNI_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기준일: **2026-10-22**. Gym ID는 `Isaac-Inspire-Sweep-Omni-v1`다. 과거 실행값이 아닌 현재 코드의 기본 설정을 정리한다. 이번 문서화는 코드 정독이며 새 학습·재생·실물 검증 결과가 아니다.

## 기본 구성

Omni v0에서 Arm 속도에 의한 조기 종료를 완화하려고 만든 분기다. 현재 v1의 변경은 Arm 속도 종료 기준 **1.0 → 1.5 rad/s** 한 가지다. 보상 계수나 물리 actuator 속도 제한을 함께 바꾸는 설정은 아니다.

| 항목 | 현재 설정 |
| --- | --- |
| 설정 클래스 / 직접 부모 | `InspireSweepOmniV1EnvCfg` / `InspireSweepOmniEnvCfg` |
| 실행 클래스 | `InspireSweepEnv` |
| 장면 | UR5e–Axia80 하우징–Inspire Hand, 선반 높이 1.05 m, 반지름 4 cm·높이 10 cm 원통 1개 |
| 물성 | 질량 평균 0.365 kg·표준편차 0.0675 kg, `[0.230,0.500]` kg 제한; 선반·물체·Hand 마찰 무작위화 |
| Reset | 선반 중심의 반지름 2 cm 원판에서 면적 균일 위치, yaw 무작위; 로봇 기본 관절 자세 |
| 목표 | 선반 XY 전방향 균일, 최대 15 cm; 원통 반지름+2 cm edge clearance를 남기도록 거리만 단축 |
| Action | Arm Joint Position 6D(기본각 + `0.5 × action`) + Hand 굽힘/opposition 개방도 2D |
| 시간 / 기본 규모 | 물리 0.01 s, decimation 2 → 정책 50 Hz; 10초, 기본 4096환경 |

선반 반폭은 X 0.20 m, Y 0.50 m다. 물성은 [Realistic Physics](SWEEP_REALISTIC_PHYSICS_ENVIRONMENT.md)의 같은 helper를 사용하지만 **EnvCfg 상속은 Baseline → Omni v0 → v1**이다.

소스 v1의 docstring에는 3 rad/s가 남아 있고 과거 생성 로그에는 2 rad/s가 기록되어 있다. 실제 현재 `__post_init__`의 값은 **1.5 rad/s**이므로 이 문서는 그 값을 따른다.

## 관측 정보

Actor와 Critic 모두 `policy` **41D**를 사용하며, 아래 순서로 연결한다. 현재 물체 위치를 계속 읽는 환경이다.

| Term | 차원 | 의미 |
| --- | --- | --- |
| `joint_pos` | 6 | 기본각 대비 Arm 관절각 |
| `joint_vel` | 6 | 기본속도 대비 Arm 관절속도 |
| `actions` | 8 | 직전 raw action, Arm 6D + Hand 2D |
| `target_obs_state` | 3 | 현재 물체 바닥 위치, Robot root 좌표계 |
| `target_obj_width` | 1 | 물체 반지름 0.04 m |
| `ee_pose` | 7 | Robot root 기준 EEF 위치·quaternion |
| `goal_pos` | 3 | Robot root 기준 episode 고정 목표 위치 |
| `tactile` | 1 | palm pad 접촉력 크기 ≥0.05 N 여부 |
| `wrist_wrench` | 6 | EEF 축·원점의 미상쇄 fixed-joint 힘/모멘트, N 및 N·m |

물체 위치·반지름에는 ±0.01 m 가산 균등 노이즈가 있다. Hand 관절 상태·질량·마찰은 직접 관측하지 않는다. F/T는 중력·관성 상쇄나 tare를 적용하지 않으며 센서 미갱신 reset 행은 tactile·F/T가 0이다. 별도 privileged Critic 그룹이나 이력 stack은 없다.

## 보상 구조

Omni v0의 **전체 11항**을 유지한다. RewardManager가 `weight × Δt`를 곱하며 `Δt=0.02 s`다. 진행·terminal 함수는 내부 `/Δt`로 시간 곱셈을 상쇄한다. 나머지는 초당 비용처럼 누적된다.

| Term | Weight | 함수와 계산·역할 |
| --- | ---: | --- |
| `reaching` | +1.0 | `ReachProgress`: **초기 물체 바닥 위치**의 반경 10 cm 구까지 새 최단 접근 기록을 보상, 누적 최대 +1 |
| `goal_distance` | +6.0 | `planar_goal_cost`: 월드 XY 목표 거리 `d`에 `exp(−d/0.10)−1`; 목표 밖에서 음수 |
| `arm_action_rate` | −0.03 | 로컬 `action_rate_l2`: raw Arm 6D 변화량 제곱합, 합산 후 상한 100 |
| `hand_action_rate` | −0.03 | 같은 함수의 raw Hand 2D 변화량 제곱합, 합산 후 상한 100 |
| `arm_joint_velocity` | −0.03 | 로컬 `joint_vel_l2`: Arm 실제 관절속도 제곱합, 합산 후 상한 100 |
| `hand_joint_velocity` | −0.01 | 같은 함수의 Hand 12관절 실제 속도 제곱합, 합산 후 상한 100 |
| `object_tilt` | −2.0 | 선반 법선 대비 기울기; 5°까지 0, 0.9 rad까지 정규화한 제곱 비용, 원시값 최대 1 |
| `shelf_collision` | −0.5 | 선반 이동·속도와 가상 손가락/손목의 선반 근접 비용 |
| `time` | −0.1 | 매초 일정 비용 |
| `success` | +30.0 | 안정 목표 성공 종료 시 1회 지급 |
| `failure` | −80.0 | 실패 6항 중 하나 이상 발동 시 1회; timeout은 제외 |

`goal_distance`는 이름과 양의 weight만 보면 양의 보상처럼 보이지만 함수 출력은 음수다. `reaching`은 물체가 움직여도 **처음 있던 위치**를 기준으로 하며, 정지하거나 이전 최단 거리까지 돌아오는 동작에는 재지급하지 않는다.

네 운동 비용은 Arm/Hand를 분리하고 raw action 변화 및 실제 관절속도의 **제곱합**을 사용한다. 평균·정규화나 Hand 입력 clamp를 보상 계산에 넣지 않는다. 합산 뒤 적용하는 비용 상한 100은 현재 공통 함수의 동작이다.

## 터미네이션

| Term | 현재 종료 조건 | 종류 |
| --- | --- | --- |
| `time_out` | 10초 | Timeout |
| `object_drop` | 바닥 높이 <1.04 m 또는 선반 법선 대비 물체 기울기 ≥0.9 rad | 실패 |
| `push_fast` | 물체 3D 속력 >0.3 m/s | 실패 |
| `shelf_collision` | 선반 6D 속도 norm >0.1, 가상 손목 판 위 높이 <7 cm, 또는 가상 손가락 <1 cm | 실패 |
| `hand_velocity` | **Arm** 6관절 중 속도 절댓값 >1.5 rad/s | 실패 |
| `object_outside_shelf` | 물체 바닥 원점의 선반 좌표 X/Y가 반폭 0.20/0.50 m 밖 | 실패 |
| `shelf_displacement` | 선반이 초기 위치에서 5 cm 초과 이동 | 실패 |
| `success` | XY 목표 오차 <1 cm, XY 속력 <0.02 m/s, 기울기 ≤10°, 선반 지지 및 실패 없음이 연속 0.3초 | 성공 |

성공의 지지 조건은 원통 반지름을 뺀 선반 영역 안에 있고, 기울기를 반영한 원통 최저 가장자리의 높이가 선반 면에서 ±1 cm 이내인 것이다. `hand_velocity`의 이름은 손가락 속도가 아닌 Arm 검사라는 기존 명칭을 유지한다.

## 커리큘럼

| 항목 | 적용 여부·설명 |
| --- | --- |
| CurriculumManager 항 | 없음 |
| Reset 무작위화 | 원판 위치·yaw·목표 방향·질량·마찰을 매 episode 추출; 난이도 일정 없음 |

## 근거와 연결

- [Omni v0/v1 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_envs.py), [현재 보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_rewards.py)
- [목표·실패 판정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/goal_terminations.py), [목표 reset](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/goal_events.py)
- [최초 v1 생성 이력](../logs/2026-10-14_omni_v1_arm_velocity.md), [공통 제곱 비용 상한 이력](../logs/2026-10-18_omni_squared_cost_caps.md)
- 다음 분기: [Omni v2](SWEEP_OMNI_V2_ENVIRONMENT.md)

과거 저장 YAML·checkpoint의 임계값과 이 문서의 현재 기본값은 별도로 확인해야 한다. 이번 문서 작업에서 시뮬레이터 실행이나 성능 평가는 하지 않았다.
