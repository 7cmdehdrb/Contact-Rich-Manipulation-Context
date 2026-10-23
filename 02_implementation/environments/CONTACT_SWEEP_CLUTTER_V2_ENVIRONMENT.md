# Contact Sweep Clutter v2

[환경 변화·계층 지도](ENVIRONMENT_EVOLUTION.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

**기준일: 2026-10-22, 현재 작업트리 코드 확인.** `Isaac-Inspire-Contact-Sweep-Clutter-v2`의 간결한 독립 설명이다. 관측 차원과 제어·나머지 보상은 v1을 유지한다. 이 문서 작성에서 학습·재생·실물 성능은 새로 검증하지 않았다.

## 기본 구성

`ContactSweepClutterV2EnvCfg`와 runtime은 [Clutter v1](CONTACT_SWEEP_CLUTTER_V1_MDP.md)을 직접 상속한다. Curriculum v1의 자식이 아니다. 손 자체의 중력·관성 하중과 외력 신호를 구분하도록 6축 F/T를 보정하고 급격한 변화 비용 하나를 추가했다.

| 항목 | 설정 |
| --- | --- |
| 로봇·장면 | UR5e–Axia80–Inspire Hand, 선반 작업면 1.05 m |
| 물체 | 반지름 4 cm·높이 10 cm 원기둥 타겟 1개 + 장애물 3개 |
| 배치 | 타겟: 선반 중앙 반경 2 cm; 목표: 최대 15 cm; 장애물: 뒤쪽 GRAY 1개·WHITE 2개 |
| 초기 상태·물성 | 고정 로봇 관절 자세; reset마다 질량·마찰 랜덤화; 장애물은 같은 환경의 타겟 물성 샘플 공유 |
| Action | 8D: Arm 6D Joint Position, 기본 자세 + 0.5 × raw action; Hand 2D 개방도 |
| 시간·병렬 환경 | 물리 0.01초, decimation 2, 제어 50 Hz, 최대 10초; 기본 4,096환경 |
| 목표 방향 | 선반 ±X 주변 각각 ±15° 제외, episode 중 목표 고정 |

장애물 RED 제외 반경은 10.3 cm이며 물성·배치 분포는 v1과 같다. 환경 수나 관측 폭을 늘리는 변경은 없다.

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
| `wrist_wrench` | 6 | EEF 기준점·축의 Hand 중력·관성 보정 외력 반력 추정값 |

`obstacles`는 10개 슬롯 × `[HEADER, x, y, z]` = 40D다. 실제 장애물 3칸에는 초기 root XYZ와 reset 때 한 번 샘플링한 ±1 cm 오차를 저장하고 나머지 7칸은 0으로 채운다. 현재 장애물 위치로 갱신하지 않는다. Actor·Critic의 별도 MLP 40→32→16 인코더로 각각 압축한다.

Actor는 `policy57 + obstacles40`의 원시 97D를 받아 임베딩 결합 후 73D를 사용한다. Critic은 현재 타겟 XYZ 3D인 `privileged`를 더해 원시 100D, 결합 후 76D다. 현재 타겟 좌표는 Actor에 추가되지 않으며 촉각에는 접촉 물체 ID가 없다.

`PureWristWrench`는 Hand 모델과 운동학으로 지지 하중을 추정하고 반력에서 제거한다. 보정에 물체 GT pose·접촉 ID를 쓰지 않는다. reset 직후 무효 샘플을 영점으로 저장하지 않아 실제 접촉을 tare로 지우지 않는다. 이는 모델 기반 시뮬레이션 보정이며 실물 보정 정확도를 뜻하지 않는다.

## 보상 구조

활성 16개 항 전체다.

| Term | Weight | 계산·적용 범위 |
| --- | --- | --- |
| `reaching` | +30 | EEF–타겟 3D 거리의 새 최선 개선량; 0.10 m 이내 제외 |
| `goal_distance` | +100 | 타겟–목표 XY 거리의 새 최선 개선량; 허용 반경 0.01 m |
| `arm_action_rate` | −0.03 | raw Arm Action 변화량 제곱합 |
| `hand_action_rate` | −0.03 | raw Hand Action 변화량 제곱합 |
| `arm_joint_velocity` | −0.03 | 실제 Arm 6개 관절 속도 제곱합 |
| `hand_joint_velocity` | −0.01 | 실제 Hand 12개 관절 속도 제곱합 |
| `object_tilt` | −2 | 타겟·장애물 4개의 tilt 비용 합; 각 5°→0.9 rad, 각 상한 1 |
| `shelf_collision` | −0.5 | 선반 이동·속도와 가상 finger/wrist의 선반 근접 비용 |
| `pushing_speed` | −2 | 타겟 3D 선속도 초과의 지수 비용; free speed 0.1 m/s, 최대 100 |
| `arm_speed_excess` | −1 | Arm 최대 절대 관절 속도 초과의 지수 비용; free speed 1.0 rad/s, 최대 100 |
| `goal_hold` | +0.9 | 타겟이 목표의 월드 XY 반경 1 cm 안에 있는 동안 1 |
| `contact_any` | +0.16 | 17개 촉각 중 하나 이상 ON이면 1 |
| `contact_count` | +0.16 | ON 영역 수 / 5, 최대 1 |
| `obstacle_displacement` | −5 | 장애물의 정확한 초기 위치 대비 3D 이동 제곱합; 상한 0.04 m² |
| `shelf_failure` | −3 | shelf_collision 종료 전이에서 한 번 −3; dt 내부 상쇄 |
| `wrench_change` | −0.1 | 보정 F/T의 제어 step 간 변화 비용; raw 상한 1, 누적 양의 보상 5% 예산 |

일반 항의 실제 step 기여는 `weight × 반환값 × 0.02초`다. `reaching`·`goal_distance`는 함수 내부에서 dt를 상쇄하므로 `weight × 새 최선 거리 개선량(m)`으로 기여한다. 후퇴 후 이전 기록으로 복귀하는 행동에는 진행 보상이 반복되지 않는다.

네 Arm/Hand 운동 비용은 로컬 `mdp/reward_functions/goal_rewards.py`의 raw 변화량·실제 속도 제곱합을 사용하고 각 출력만 100으로 제한한다. 평균·정규화 또는 Hand 제어 clamp 이후 값을 쓰지 않는다.

`goal_hold`는 목표 월드 XY 1 cm 안에서 +0.9/초, 두 접촉 항은 현재 촉각의 존재·개수에 대한 보상이다. `shelf_failure`는 선반 실패 전이에서 실제 −3 한 번을 지급한다.

### 보정 F/T 변화 비용

같은 물리 샘플을 관측과 보상이 공유한다. 보상은 EEF 기준점의 wrench를 **월드 축**으로 표현한 뒤 이전 제어 step과 비교하여 단순 손목 축 회전의 영향을 줄인다. 모멘트 기준점은 움직이는 EEF다.

힘 벡터 변화량의 norm 0.5 N, 모멘트 벡터 변화량의 norm 0.01 Nm까지는 무료다. 초과량을 각각 5 N·0.1 Nm로 나눈 두 제곱의 합에 0.5를 곱하고 1로 제한한다. 이는 시간 미분이 아닌 **step 간 벡터 변화량**이며, 두 시점의 힘 크기만 뺀 값과 다르다. 최대 −0.1/초이면서, 해당 episode에 실제 획득한 누적 양의 보상의 5% 이내만 사용한다. 첫 유효 샘플은 이력만 만들고 비용을 내지 않는다.

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

| 항목 | 설정 |
| --- | --- |
| 활성 Curriculum term | 없음; Curriculum v1을 상속하지 않음 |
| 고정값 | 물체 free speed 0.1 m/s, Arm free speed 1 rad/s; F/T 변화 deadband·예산 고정 |

## 근거와 확인 범위

[Env Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/contact_sweep_clutter_envs.py) · [관측](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/contact_sweep_clutter.py) · [보정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/compensated_wrench.py) · [보상 Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/contact_sweep_clutter.py) · [변화 비용](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/contact_sweep_clutter.py) · [개발 이력](../logs/2026-10-20_contact_sweep_clutter_v2.md)

보정 신호를 기존 정책 밖에서 수집하는 별도 분기는 [FT Test](CONTACT_SWEEP_CLUTTER_FT_TEST_ENVIRONMENT.md), 보정·커리큘럼의 독립 통합은 [Fusion v0](CONTACT_SWEEP_CLUTTER_FUSION_ENVIRONMENT.md)다.

현재 설명은 등록, 설정 상속, MDP 계산의 정적 대조 결과다. 과거 로그의 실행 검증은 해당 기록의 조건에만 해당하며 이번 문서 작성의 새 실행 결과로 해석하지 않는다.
