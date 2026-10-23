# Sweep Initial Privileged v0 — 독립 환경 요약

[환경 변화·계층](ENVIRONMENT_EVOLUTION.md) · [부모 Realistic Physics](SWEEP_REALISTIC_PHYSICS_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기준일: **2026-10-22**. Gym ID는 `Isaac-Inspire-Sweep-Realistic-Physics-Initial-Privileged-v0`다. 과거 실험의 현재 코드 계약을 요약하며 이번 작업은 새 학습·재생·실물 검증이 아니다.

## 기본 구성

Realistic Physics에서 Actor의 물체 위치를 **episode 시작 위치**로 고정하고 Critic에만 현재 물체 상태를 추가한 비대칭 관측 실험이다. 조작 중 물체 정답 위치를 Actor가 계속 읽는 경로를 제거하면서 학습용 Critic에는 더 많은 정보를 제공한다.

| 항목 | 현재 설정 |
| --- | --- |
| 설정 클래스 / 직접 부모 | `InspireSweepRealisticInitialPrivilegedEnvCfg` / `InspireSweepRealisticPhysicsEnvCfg` |
| 실행 클래스 | `InspireSweepEnv` |
| 장면 | UR5e–Axia80 하우징–Inspire Hand, 높이 1.05 m 선반, 반지름 4 cm·높이 10 cm 원통 1개 |
| Reset / 목표 | 물체 `(−0.75,0,1.05)` m 주변 X/Y ±2 cm, 무작위 yaw; 월드 ±Y로 18 cm 목표, 로봇 기본 관절 자세 |
| 질량 | 정규분포 평균 0.365 kg·표준편차 0.0675 kg, `[0.230,0.500]` kg 제한; 질량 비례 관성 |
| 마찰 | 선반·원통·Hand별 정/동마찰 무작위화, `Average` combine; 부모와 같은 분포 |
| Action | Arm Joint Position 6D(기본각 + `0.5 × action`) + Hand 굽힘/opposition 2D |
| 시간 / 규모 | 물리 0.01 s × decimation 2, 50 Hz, 10초, 기본 4096환경 |
| PPO 입력 | Actor=`policy` 41D, Critic=`policy + privileged` 54D |

마찰의 정마찰 평균/표준편차는 선반 `0.315/0.051`, 원통 `0.315/0.040`, Hand `0.585/0.145`다. 동마찰은 각각 `0.252/0.041`, `0.252/0.032`, `0.468/0.116`이며 음수 제한·4096 bucket 표본을 사용한다.

## 관측 정보

| 그룹 / Term | 차원 | 정보와 갱신 시점 |
| --- | --- | --- |
| policy / `joint_pos` | 6 | Arm 기본각 대비 현재 관절각, rad |
| policy / `joint_vel` | 6 | Arm 기본속도 대비 현재 관절속도, rad/s |
| policy / `actions` | 8 | 직전 raw action, Arm 6D + Hand 2D |
| policy / `target_obs_state` | 3 | **시작 물체 바닥 위치**를 Robot root 좌표계로 저장하고 reset까지 고정 |
| policy / `target_obj_width` | 1 | 반지름 0.04 m; ±0.01 m 균등 노이즈는 매 관측 적용 |
| policy / `ee_pose` | 7 | 현재 EEF 위치 + quaternion, Robot root 좌표계 |
| policy / `goal_pos` | 3 | episode 고정 목표 위치, Robot root 좌표계 |
| policy / `tactile` | 1 | 실제 palm pad 힘 크기 ≥0.05 N 여부 |
| policy / `wrist_wrench` | 6 | EEF 축·원점의 미상쇄 fixed-joint 힘/모멘트 |
| privileged / `target_state` | 13 | 현재 물체 위치 3D·quaternion 4D·선속도 3D·각속도 3D, Robot root 좌표계 |

Actor 초기 위치의 측정 오차는 각 성분 ±0.01 m에서 **reset마다 한 번 추출하고 episode 동안 고정**한다. 이전 episode의 command snapshot을 쓰지 않도록 새 command가 생성된 뒤 초기 위치를 저장한다.

Critic의 13D 추가 입력에는 관측 노이즈를 넣지 않는다. 물체 위치·속도 기준은 원통 바닥 원점이다. Critic은 policy 41D도 함께 읽으므로 Actor의 초기 측정 오차까지 포함해 54D다.

F/T는 Hand 중력·관성 보정 없는 반력이며 tactile과 함께 reset 직후 미갱신 행에서 0이다. Hand 관절 상태와 물성은 직접 입력하지 않는다. Actor의 실행 중 물체 위치 제한을 구현한 것이며 실물 Blind Sweep 성능을 입증한 결과는 아니다.

## 보상 구조

관측만 바꾸므로 Baseline의 **전체 8항**을 그대로 사용한다. 보상은 Actor가 보지 못하는 현재 물체 정답 상태를 이용한다. 각 weight에는 RewardManager가 `Δt=0.02 s`를 곱한다.

| Term | Weight | 계산·역할 |
| --- | ---: | --- |
| `action_rate` | −0.03 | raw 8D action 변화량의 제곱합 |
| `joint_vel` | −0.03 | Arm 6관절 실제 속도 제곱합 |
| `shelf_collision` | −0.5 | 선반 이동·속도 및 가상 손가락/손목 근접 비용 |
| `object_collision` | −0.5 | 비타겟 물체 움직임; 단일 원통 구성에서는 0 |
| `reaching` | +3.0 | 현재 물체 측면 접근점까지 거리의 지수 보상 |
| `orientation` | +2.0 | EEF +Y와 선반 +Z 정렬에 `sign(cos) × cos²` |
| `sweeping_object` | +6.0 | EEF/손목 접근 게이트를 갖는 목표 거리·Y속도 보상 |
| `homing_after_sweep` | +9.0 | 목표 YZ 거리 약 3 cm 안에서 Arm 앞 5관절의 기본각 복귀 |

이 환경만을 위한 보상 변경은 없다. 접근점은 현재 물체 바닥에서 X −2 cm·밀기 반대 Y 방향으로 반지름·Z +9 cm다. 밀기는 목표 3 cm 밖에서 EEF 4 cm/손목 Y 4 cm 게이트를 사용하고, 목표 3 cm 안에서는 `2 × exp(−5 × 거리)`를 반환한다. 성공/실패 terminal 보너스나 센서 직접 보상은 없다.

## 터미네이션

| Term | 현재 종료 조건 | 종류 |
| --- | --- | --- |
| `time_out` | 10초 | Timeout |
| `object_drop` | 물체 바닥 높이 <1.04 m 또는 roll/pitch 절댓값 >0.9 rad | 실패 |
| `push_fast` | 물체 3D 속력 >0.3 m/s | 실패 |
| `shelf_collision` | 선반 6D 속도 norm >0.1, 가상 손목 판 위 높이 <7 cm, 또는 가상 손가락 <1 cm | 실패 |
| `hand_velocity` | Arm 6관절 중 하나라도 속도 절댓값 >1.0 rad/s | 실패 |
| 성공 종료 | 별도 항 없음 | 없음 |

`hand_velocity`는 이름과 달리 Arm을 검사한다. 물체 GT를 이용한 실패 판정은 학습 환경의 종료 조건이며 실물 Actor가 같은 판정을 관측만으로 수행한다는 뜻은 아니다.

## 커리큘럼

| 항목 | 적용 여부·설명 |
| --- | --- |
| CurriculumManager 항 | 없음 |
| Reset 무작위화 | 배치·방향·질량·마찰·초기 위치 측정오차 재추출 |
| 정보 제한의 일정 | Actor 시작 위치 고정은 처음부터 적용; 단계별 GT 제거 일정 없음 |

## 근거와 연결

- [파생 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_envs.py), [초기 위치 저장·Critic 상태](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/asymmetric_observations.py)
- [Actor/Critic 입력 연결](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/sweep_ppo_cfg.py), [부모 물성](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_envs.py)
- [보상](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/sweep.py), [종료](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/sweep.py), [환경 구조 기록](../logs/2026-10-14_inspire_sweep_uml.md)

관측 분리와 상속을 코드로 확인했다. 이번 문서 작업에서 정책 성능, simulator 통합 동작, 센서·실물 이전은 평가하지 않았다.
