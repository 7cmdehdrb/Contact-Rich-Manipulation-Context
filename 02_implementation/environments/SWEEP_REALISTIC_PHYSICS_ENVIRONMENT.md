# Sweep Realistic Physics v0 — 독립 환경 요약

[환경 변화·계층](ENVIRONMENT_EVOLUTION.md) · [부모 Baseline](SWEEP_BASELINE_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기준일: **2026-10-22**. Gym ID는 `Isaac-Inspire-Sweep-Realistic-Physics-v0`다. 과거 실험의 현재 코드 계약을 정리하며, 이번 문서화는 새 학습·재생·실물 검증 결과가 아니다.

## 기본 구성

Baseline의 제어·관측·보상·종료를 유지하면서 물체 질량과 접촉 마찰만 episode마다 바꾸는 분기다. 고정 1 kg 물체의 조건에서 더 가벼운 물체와 접촉 물성 변화로 실험 범위를 넓힌다. 환경 이름의 Realistic은 실물 일치가 검증되었다는 뜻이 아니다.

| 항목 | 현재 설정 |
| --- | --- |
| 설정 클래스 / 직접 부모 | `InspireSweepRealisticPhysicsEnvCfg` / `InspireSweepEnvCfg` |
| 실행 클래스 | `InspireSweepEnv` |
| 장면 | UR5e–Axia80 하우징–Inspire Hand, 높이 1.05 m 선반, 반지름 4 cm·높이 10 cm 원통 1개 |
| 물체 배치 / 목표 | `(−0.75,0,1.05)` m에서 X/Y ±2 cm, yaw 무작위; 시작점에서 월드 ±Y로 18 cm 목표 |
| 물체 질량 | 평균 0.365 kg, 표준편차 0.0675 kg 정규 표본을 `[0.230,0.500]` kg로 clamp; 관성도 질량 비율로 변경 |
| 마찰 적용 | 선반·물체·Hand 역할별 정/동마찰을 reset마다 추출, combine mode `Average` |
| Action | Arm Joint Position 6D(기본각 + `0.5 × action`) + Hand 굽힘/opposition 개방도 2D |
| 시간 / 기본 규모 | 물리 0.01 s × decimation 2 → 50 Hz, 10초, 기본 4096환경 |
| PPO | Actor/Critic 모두 동일한 `policy` 그룹 |

| 마찰 역할 | 정마찰 평균 / 표준편차 | 동마찰 평균 / 표준편차 |
| --- | --- | --- |
| 선반 | 0.315 / 0.051 | 0.252 / 0.041 |
| 원통 | 0.315 / 0.040 | 0.252 / 0.032 |
| Hand | 0.585 / 0.145 | 0.468 / 0.116 |

마찰은 음수를 0으로 제한한 정규분포 기반 4096개 bucket에서 선택한다. Spawn 시 재질을 연결하고 reset 시 Tensor API로 갱신한다. 로봇 초기 자세, 원통 형상·하단 COM 구조와 선반 배치는 Baseline을 유지한다.

## 관측 정보

Actor와 Critic은 모두 **41D**다. 물성 값은 직접 관측에 추가되지 않으며 현재 물체 위치는 매 step 갱신된다.

| Term | 차원 | 의미 |
| --- | --- | --- |
| `joint_pos` | 6 | Arm 관절각 − 기본각, rad |
| `joint_vel` | 6 | Arm 관절속도 − 기본속도, rad/s |
| `actions` | 8 | 직전 raw action, Arm 6D + Hand 2D |
| `target_obs_state` | 3 | 현재 물체 바닥 위치, Robot root 기준, m |
| `target_obj_width` | 1 | 물체 반지름 0.04 m |
| `ee_pose` | 7 | Robot root 기준 EEF 위치 + quaternion |
| `goal_pos` | 3 | Robot root 기준 고정 목표 위치 |
| `tactile` | 1 | palm pad 접촉력 크기 ≥0.05 N의 bit |
| `wrist_wrench` | 6 | EEF 축·원점의 힘/모멘트, N 및 N·m |

물체 위치·반지름에는 ±0.01 m 균등 가산 노이즈를 적용한다. Hand 관절 상태는 직접 넣지 않는다. F/T는 중력·관성 상쇄 없는 fixed-joint 반력이며 reset 직후 센서 미갱신 행은 tactile·F/T가 0이다. 현재 물체 위치를 사용하므로 Blind actor가 아니다.

## 보상 구조

Baseline의 **전체 8항**을 유지한다. 최종 step 보상은 각 함수 출력에 아래 weight와 `Δt=0.02 s`를 곱한 합이다.

| Term | Weight | 계산·역할 |
| --- | ---: | --- |
| `action_rate` | −0.03 | 전체 raw 8D action 변화량 제곱합 |
| `joint_vel` | −0.03 | Arm 6관절의 실제 속도 제곱합 |
| `shelf_collision` | −0.5 | 선반 이동·속도와 가상 손가락/손목 근접 비용 |
| `object_collision` | −0.5 | 비타겟 물체 움직임 비용; 현재 단일 원통에서는 0 |
| `reaching` | +3.0 | 현재 물체 측면 접근점과 EEF의 거리에 `exp(−10 × 거리)` |
| `orientation` | +2.0 | EEF +Y와 선반 +Z의 정렬값 `sign(cos) × cos²` |
| `sweeping_object` | +6.0 | 목표 거리·Y속도 shaping 및 목표 3 cm 이내 근접 보상 |
| `homing_after_sweep` | +9.0 | 목표 YZ 거리 약 3 cm 안에서 Arm 앞 5관절 기본각 복귀 |

이 분기에서 새로 바꾼 보상은 없다. 접근점은 물체 바닥에서 X −2 cm·밀기 반대 Y 방향으로 반지름·Z +9 cm다. 밀기는 EEF 거리 4 cm 및 손목 Y 오차 4 cm 게이트를 쓰며, 목표 3 cm 안에서는 게이트 없이 `2 × exp(−5 × 거리)`를 반환한다. 센서 신호 자체의 보상 항도 없다.

## 터미네이션

| Term | 현재 종료 조건 | 종류 |
| --- | --- | --- |
| `time_out` | 10초 | Timeout |
| `object_drop` | 바닥 높이 <1.04 m 또는 roll/pitch 절댓값 >0.9 rad | 실패 |
| `push_fast` | 물체 3D 속력 >0.3 m/s | 실패 |
| `shelf_collision` | 선반 6D 속도 norm >0.1, 가상 손목 판 위 높이 <7 cm, 또는 가상 손가락 높이 <1 cm | 실패 |
| `hand_velocity` | Arm 6개 중 한 관절이라도 속도 절댓값 >1.0 rad/s | 실패 |
| 성공 종료 | 별도 항 없음 | 없음 |

`hand_velocity`는 Hand가 아닌 Arm을 검사한다. 물성 분포가 바뀌어도 위 임계값은 그대로다.

## 커리큘럼

| 항목 | 적용 여부·설명 |
| --- | --- |
| CurriculumManager 항 | 없음 |
| 물성 무작위화 | 매 reset 같은 질량·마찰 분포에서 추출; 학습 진행에 따른 분포 변화 없음 |
| 배치 무작위화 | X/Y·yaw·좌우 방향을 reset마다 추출 |

## 근거와 연결

- [파생 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/realistic_physics_env_cfg.py), [부모 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/env_cfg.py)
- [질량·마찰 표본과 적용](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/realistic_physics.py), [Spawn 재질 연결](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/realistic_spawners.py)
- [보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards.py), [종료 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations.py), [환경 구조 기록](../logs/2026-10-14_inspire_sweep_uml.md)
- 다음 분기: [Initial Privileged](SWEEP_INITIAL_PRIVILEGED_ENVIRONMENT.md)

물성 변화에 대한 실제 학습 성능·실물 적합성은 이번 문서 작업에서 확인하지 않았다.
