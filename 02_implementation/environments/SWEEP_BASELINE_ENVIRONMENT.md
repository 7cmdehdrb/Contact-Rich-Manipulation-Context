# Sweep Baseline v0 — 독립 환경 요약

[환경 변화·계층](ENVIRONMENT_EVOLUTION.md) · [구현 안내](../README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기준일: **2026-10-22**. Gym ID는 `Isaac-Inspire-Sweep-Baseline-v0`다. 과거 실험 환경의 등록과 현재 코드 계약을 간결히 기록한다. 이번 문서는 코드 정독 기준이며 새 학습·재생·실물 검증 결과가 아니다.

## 기본 구성

기존 Sweep 실험을 외부 환경 import 없이 실행할 수 있도록 만든 독립 기준선이다. UR5e–Axia80 하우징–Inspire Hand로 선반의 원통 하나를 좌우로 민다. 초기 접근, 밀기, 목표 부근에서의 Arm 복귀를 보상한다.

| 항목 | 현재 설정 |
| --- | --- |
| 설정 클래스 / 직접 부모 | `InspireSweepEnvCfg` / `ManagerBasedRLEnvCfg` |
| 실행 클래스 | `InspireSweepEnv` → `ManagerBasedRLEnv` |
| 장면 | 선반 원점 `(−0.7, 0, 0)` m, 높이 1.05 m 판, 단일 원통 |
| 물체 | 반지름 0.04 m, 높이 0.10 m, 질량 1 kg; 질량 80%를 아래 20% 높이에 배치, 바닥 기준 COM 0.02 m |
| Reset | 물체 바닥 `(−0.75, 0, 1.05)` m에 X/Y 각각 ±0.02 m; yaw 무작위, 로봇은 기본 관절 자세 |
| 목표 | 시작 위치에서 월드 ±Y로 0.18 m; 에피소드 중 고정 |
| Action | 8D: Arm 6개 Joint Position 목표 = 기본각 + `0.5 × action`, Hand 2개 개방도 |
| Hand 제어 | 전체 굽힘·엄지 opposition을 분리; 제어 입력을 `[0,1]`로 제한하여 12개 관절 목표로 변환 |
| 시간 / 기본 규모 | 물리 0.01 s, decimation 2 → 정책 50 Hz; 10초, 기본 4096환경 |
| PPO | Actor/Critic 모두 `policy`; 별도 privileged 입력·관측 이력 stack 없음 |

EEF는 Hand-local `(0,0,0.13)` m에 해당하는 손목 조립체의 고정 기준점이다. 손가락만 굽혀도 EEF는 이동하지 않는다. 가상 손가락·손목 점은 선반 근접 비용과 종료에 사용한다.

## 관측 정보

Actor와 Critic 모두 아래 순서의 **41D**를 사용한다. 현재 물체 위치를 계속 받으므로 실행 중 시각을 제거한 Blind actor와 구분한다.

| Term | 차원 | 의미 |
| --- | --- | --- |
| `joint_pos` | 6 | Arm 관절각 − 기본각, rad |
| `joint_vel` | 6 | Arm 관절속도 − 기본속도, rad/s |
| `actions` | 8 | 다음 정책 판단 기준 직전 raw Arm 6D + Hand 2D action |
| `target_obs_state` | 3 | 현재 물체 바닥 원점 위치, Robot root 좌표계, m |
| `target_obj_width` | 1 | 이름은 width이나 실제 값은 반지름 0.04 m |
| `ee_pose` | 7 | Robot root 기준 EEF 위치 3D + quaternion 4D |
| `goal_pos` | 3 | Robot root 기준 고정 목표 위치 |
| `tactile` | 1 | 실제 palm pad 접촉력 크기 0.05 N 이상 여부 |
| `wrist_wrench` | 6 | EEF 축·원점에서 표현한 힘/모멘트, N 및 N·m |

물체 위치와 반지름 관측에는 각각 ±0.01 m 균등 가산 노이즈를 적용한다. Hand 관절 상태는 직접 관측하지 않는다. F/T는 fixed-joint 반력을 좌표 변환한 값으로 Hand 중력·관성 상쇄나 tare가 없다. Reset 직후 센서가 아직 갱신되지 않은 행은 tactile·F/T를 0으로 반환한다.

## 보상 구조

아래는 상속을 포함한 **전체 8항**이다. RewardManager는 함수 출력에 `weight × 0.02 s`를 곱한다. 성공·실패 terminal 보너스는 없다.

| Term | Weight | 계산·역할 |
| --- | ---: | --- |
| `action_rate` | −0.03 | 전체 raw 8D action 변화량의 제곱합 |
| `joint_vel` | −0.03 | Arm 실제 6개 관절속도의 제곱합 |
| `shelf_collision` | −0.5 | 선반 이동·속도 및 가상 손가락/손목의 선반 근접 비용 |
| `object_collision` | −0.5 | 비타겟 물체 속도의 절댓값 합에 tanh; 단일 물체이므로 항상 0 |
| `reaching` | +3.0 | 현재 물체 측면 접근점까지 거리의 `exp(−10 × 거리)` |
| `orientation` | +2.0 | EEF의 +Y축과 선반 +Z축 내적에 `sign(cos) × cos²` 적용 |
| `sweeping_object` | +6.0 | 접근 게이트를 갖는 목표 거리·Y속도 shaping, 목표 3 cm 안에서는 별도 근접 보상 |
| `homing_after_sweep` | +9.0 | 목표 YZ 오차 약 3 cm 안에서 Arm 앞 5관절의 기본각 복귀를 보상 |

접근점은 물체 바닥에서 X −2 cm, Y는 밀기 방향 반대쪽으로 반지름만큼, Z +9 cm 떨어진 점이다. 물체 중심 기준으로는 Z +4 cm다.

`sweeping_object`는 목표와 물체의 3D 거리가 3 cm 미만이면 `2 × exp(−5 × 거리)`를 반환한다. 그 밖에는 EEF–접근점 4 cm 이내 및 손목 Y 오차 4 cm 이내일 때 `1 − 거리/0.18`과 Y속도 항을 더한다. Y속도 절댓값이 0.05 m/s 초과·0.1 m/s 미만이면 +0.5, 0.1 m/s 이상이면 −0.5다.

`homing_after_sweep`는 XYZ 목표 도달 전체가 아니라 **YZ 거리**로 복귀 게이트를 정한다. 센서 입력 자체를 직접 보상하지 않으며, 현재 물체 정답 상태를 보상 계산에 사용한다.

## 터미네이션

| Term | 현재 종료 조건 | 종류 |
| --- | --- | --- |
| `time_out` | 10초 경과 | Timeout |
| `object_drop` | 물체 바닥 높이 <1.04 m 또는 roll/pitch 절댓값 >0.9 rad | 실패 |
| `push_fast` | 물체 3D 속력 >0.3 m/s | 실패 |
| `shelf_collision` | 선반 6D 속도 벡터 norm >0.1, 또는 가상 손목 높이 <판 위 0.07 m, 또는 가상 손가락 높이 <0.01 m | 실패 |
| `hand_velocity` | **Arm** 6관절 중 하나라도 속도 절댓값 >1.0 rad/s | 실패 |
| 성공 종료 | 별도 항 없음; 목표 도달 이후에도 실패 또는 timeout까지 진행 | 없음 |

`hand_velocity`는 역사적 term 이름이며 손가락 속도를 검사하지 않는다. `shelf_collision` 또한 접촉력 임계값이 아니라 이동·속도 및 가상 점 높이를 검사한다.

## 커리큘럼

| 항목 | 적용 여부·설명 |
| --- | --- |
| CurriculumManager 항 | 없음 |
| Reset 무작위화 | 위치·yaw·좌우 방향만 매 episode 재추출; 학습 진도별 난이도 일정 없음 |

## 근거와 연결

- [환경·Manager 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/env_cfg.py), [등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py)
- [관측](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations.py), [보상](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards.py), [종료](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations.py)
- [원통 자산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/mass_cylinder.py), [10월 14일 환경 구조 기록](../logs/2026-10-14_inspire_sweep_uml.md)
- 다음 분기: [Realistic Physics](SWEEP_REALISTIC_PHYSICS_ENVIRONMENT.md), [Omni v0](OMNI_ENVIRONMENT.md), [Baseline Tactile](TACTILE_ENVIRONMENT.md)

과거 checkpoint의 저장 설정과 현재 기본값은 다를 수 있다. 이 문서 작성에서 simulator 생성, 정책 평가, 성능 비교는 실행하지 않았다.
