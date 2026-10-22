# Contact Sweep Clutter Curriculum v1

[환경 변화·계층 지도](ENVIRONMENT_EVOLUTION.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

**기준일: 2026-10-22, 현재 작업트리 코드 확인.** `Isaac-Inspire-Contact-Sweep-Clutter-Curriculum-v1`의 간결한 독립 설명이다. Actor는 초기 타겟 위치, Critic은 추가 현재 타겟 위치를 사용한다. 이 문서 작성에서 학습·재생·실물 성능은 새로 검증하지 않았다.

## 기본 구성

`ContactSweepClutterV1CurriculumEnvCfg`와 runtime은 [Clutter v1](CONTACT_SWEEP_CLUTTER_V1_MDP.md)을 상속한다. 접촉을 유지하고 주변 물체 교란을 줄이는 v1 위에서, 물체·Arm 운동을 점차 느리고 부드럽게 유도하도록 네 일정을 추가했다.

| 항목 | 설정 |
| --- | --- |
| 로봇·장면 | UR5e–Axia80–Inspire Hand, 선반 작업면 1.05 m |
| 물체 | 반지름 4 cm·높이 10 cm 원기둥 타겟 1개 + 장애물 3개 |
| 배치 | 타겟: 선반 중앙 반경 2 cm; 목표: 최대 15 cm; 장애물: 뒤쪽 GRAY 1개·WHITE 2개 |
| 초기 상태·물성 | 고정 로봇 관절 자세; reset마다 질량·마찰 랜덤화; 장애물은 같은 환경의 타겟 물성 샘플 공유 |
| Action | 8D: Arm 6D Joint Position, 기본 자세 + 0.5 × raw action; Hand 2D 개방도 |
| 시간·병렬 환경 | 물리 0.01초, decimation 2, 제어 50 Hz, 최대 10초; 기본 4,096환경 |
| 목표 방향 | 선반 ±X 주변 각각 ±15° 제외, episode 중 목표 고정 |

물체·장애물 배치는 Clutter v0와 같으며 RED 제외 반경 10.3 cm다. 40D 초기 장애물 정보와 정책 모델도 v1을 유지한다.

## 관측

| Term | 차원 | 의미 |
| --- | --- | --- |
| `joint_pos`, `joint_vel` | 6 + 6 | Arm 상대 관절 위치·속도 |
| `actions` | 8 | 직전 raw Action |
| `target_obs_state` | 3 | 초기 타겟 root XYZ; reset 때 고정 ±1 cm 오차 |
| `target_obj_width` | 1 | 실제 값은 반지름 0.04 m; ±1 cm 노이즈 |
| `ee_pose` | 7 | root frame EEF XYZ·quaternion |
| `goal_pos` | 3 | root frame 목표 XYZ |
| `tactile` | 17 | 0.01 N 기준 접촉 bit; 직접 패드·부모 body 투영 접촉 |
| `wrist_wrench` | 6 | EEF 기준점·축의 미보정 반력, N·Nm |

`obstacles`는 10개 슬롯 × `[HEADER, x, y, z]` = 40D다. 실제 장애물 3칸에는 초기 root XYZ와 reset 때 한 번 샘플링한 ±1 cm 오차를 저장하고 나머지 7칸은 0으로 채운다. 현재 장애물 위치로 갱신하지 않는다. Actor·Critic의 별도 MLP 40→32→16 인코더로 각각 압축한다.

Actor는 `policy57 + obstacles40`의 원시 97D를 받아 임베딩 결합 후 73D를 사용한다. Critic은 현재 타겟 XYZ 3D인 `privileged`를 더해 원시 100D, 결합 후 76D다. 현재 타겟 좌표는 Actor에 추가되지 않으며 촉각에는 접촉 물체 ID가 없다.

## 보상 구조

활성 15개 항 전체다. 화살표는 iteration에 따른 계수·허용 속도의 변화다.

| Term | Weight | 계산·적용 범위 |
| --- | --- | --- |
| `reaching` | +30 | EEF–타겟 3D 거리의 새 최선 개선량; 0.10 m 이내 제외 |
| `goal_distance` | +100 | 타겟–목표 XY 거리의 새 최선 개선량; 허용 반경 0.01 m |
| `arm_action_rate` | −0.03→−0.06 | raw Arm Action 변화량 제곱합 |
| `hand_action_rate` | −0.03 | raw Hand Action 변화량 제곱합 |
| `arm_joint_velocity` | −0.03→−0.06 | 실제 Arm 6개 관절 속도 제곱합 |
| `hand_joint_velocity` | −0.01 | 실제 Hand 12개 관절 속도 제곱합 |
| `object_tilt` | −2 | 타겟·장애물 4개의 tilt 비용 합; 각 5°→0.9 rad, 각 상한 1 |
| `shelf_collision` | −0.5 | 선반 이동·속도와 가상 finger/wrist의 선반 근접 비용 |
| `pushing_speed` | −2 | 타겟 3D 선속도 초과의 지수 비용; free speed 0.1→0.05 m/s, 최대 100 |
| `arm_speed_excess` | −1 | Arm 최대 절대 관절 속도 초과의 지수 비용; free speed 1.0→0.8 rad/s, 최대 100 |
| `goal_hold` | +0.9 | 타겟이 목표의 월드 XY 반경 1 cm 안에 있는 동안 1 |
| `contact_any` | +0.16 | 17개 촉각 중 하나 이상 ON이면 1 |
| `contact_count` | +0.16 | ON 영역 수 / 5, 최대 1 |
| `obstacle_displacement` | −5 | 장애물의 정확한 초기 위치 대비 3D 이동 제곱합; 상한 0.04 m² |
| `shelf_failure` | −3 | shelf_collision 종료 전이에서 한 번 −3; dt 내부 상쇄 |

일반 항의 실제 step 기여는 `weight × 반환값 × 0.02초`다. `reaching`·`goal_distance`는 함수 내부에서 dt를 상쇄하므로 `weight × 새 최선 거리 개선량(m)`으로 기여한다. 후퇴 후 이전 기록으로 복귀하는 행동에는 진행 보상이 반복되지 않는다.

네 Arm/Hand 운동 비용은 로컬 `mdp/goal_rewards.py`의 raw 변화량·실제 속도 제곱합을 사용하고 각 출력만 100으로 제한한다. 평균·정규화 또는 Hand 제어 clamp 이후 값을 쓰지 않는다.

`goal_hold`는 월드 XY 1 cm 안에 있는 동안 +0.9/초이며 속도·기울기·체류시간 조건은 없다. `contact_any`·`contact_count`는 같은 현재 촉각 17bit를 공유하고 타겟/장애물을 구분하지 않는다. `obstacle_displacement`는 노이즈 없는 초기 실제 위치를 기준으로 하며 최대 −0.2/초다. `shelf_failure`는 해당 실패 전이에서 한 번 −3이다.

## 터미네이션

| Term | 종료 조건 |
| --- | --- |
| `time_out` | 10초; timeout 처리 |
| `object_drop` | 타겟·장애물 중 하나라도 밑면 높이 <1.04 m 또는 선반 법선 대비 tilt ≥0.9 rad |
| `push_fast` | 타겟 3D 선속도 norm >0.8 m/s |
| `shelf_collision` | 선반 root velocity norm >0.1 또는 wrist 선반면 위 높이 <0.03 m; finger 검사는 비활성 |
| `hand_velocity` | 이름과 달리 Arm 6개 중 절대 속도 >5 rad/s |
| `shelf_displacement` | 선반 초기 위치 대비 이동 거리 >0.05 m |

`object_outside_shelf`는 비활성이다. 성공 종료는 없으며 목표 도달 뒤에도 실패 또는 timeout까지 진행한다. `shelf_collision`의 0.1은 접촉력 임계값이 아니라 선반의 선속도·각속도 성분이 함께 든 root velocity 벡터 norm 기준이다.

## 커리큘럼

| Term / 적용값 | 초기→최종 | 갱신 주기 / 변화량 |
| --- | --- | --- |
| `pushing_free_speed` / 물체 free speed | 0.1→0.05 m/s | 3,000 iteration마다 −0.01 |
| `arm_free_speed` / Arm free speed | 1.0→0.8 rad/s | 5,000 iteration마다 −0.05 |
| `arm_action_rate_weight` | −0.03→−0.06 | 3,000 iteration마다 −0.005 |
| `arm_joint_velocity_weight` | −0.03→−0.06 | 3,000 iteration마다 −0.005 |

단위는 환경 step이 아닌 runner의 **0부터 시작하는 Learning iteration**이다. 매 구간의 감소량을 누적 실행하지 않고 `초기값 − 감소량 × floor(iteration / 주기)`를 하한으로 제한해 다시 계산한다. rollout 전에 적용되므로 진행 중 episode의 보상에도 반영되고, checkpoint 재개 시 복원한 iteration에 맞춰 재계산한다.

## 근거와 확인 범위

[Env Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_v1_curriculum/env_cfg.py) · [상속 보상](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_v1/rewards_cfg.py) · [커리큘럼](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_v1_curriculum/curriculum_cfg.py) · [일정 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_v1_curriculum/mdp.py) · [개발 이력](../logs/2026-10-20_clutter_v1_curriculum.md)

설계 의도는 지정 [Notion 환경 기록](https://app.notion.com/p/3f7bd3c55e1b80e5a161c6e0dd175773)의 변경 설명과 개발 이력을 참고했다. 기록의 학습 관찰은 이번에 재평가한 결과가 아니다.

현재 설명은 등록, 설정 상속, MDP 계산의 정적 대조 결과다. 과거 로그의 실행 검증은 해당 기록의 조건에만 해당하며 이번 문서 작성의 새 실행 결과로 해석하지 않는다.
