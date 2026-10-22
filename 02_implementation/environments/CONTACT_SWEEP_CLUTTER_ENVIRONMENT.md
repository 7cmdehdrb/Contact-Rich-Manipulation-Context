# Contact Sweep Clutter v0

[환경 변화·계층 지도](ENVIRONMENT_EVOLUTION.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

**기준일: 2026-10-22, 현재 작업트리 코드 확인.** `Isaac-Inspire-Contact-Sweep-Clutter-v0`의 간결한 독립 설명이다. 현재 타겟 위치를 Actor에 계속 제공하는 장애물 확장 기준이다. 이 문서 작성에서 학습·재생·실물 성능은 새로 검증하지 않았다.

## 기본 구성

`ContactSweepClutterEnvCfg`와 runtime `ContactSweepClutterEnv`는 각각 [Contact Sweep v0](CONTACT_SWEEP_ENVIRONMENT.md)의 Cfg와 runtime을 상속한다. 타겟·목표 분포를 유지하면서 장애물, 초기 장애물 임베딩, 전체 물체의 전도 검사를 추가한다.

| 항목 | 설정 |
| --- | --- |
| 로봇·장면 | UR5e–Axia80–Inspire Hand, 선반 작업면 1.05 m |
| 물체 | 반지름 4 cm·높이 10 cm 원기둥 타겟 1개 + 장애물 3개 |
| 배치 | 타겟: 선반 중앙 반경 2 cm; 목표: 최대 15 cm; 장애물: 뒤쪽 GRAY 1개·WHITE 2개 |
| 초기 상태·물성 | 고정 로봇 관절 자세; reset마다 질량·마찰 랜덤화; 장애물은 같은 환경의 타겟 물성 샘플 공유 |
| Action | 8D: Arm 6D Joint Position, 기본 자세 + 0.5 × raw action; Hand 2D 개방도 |
| 시간·병렬 환경 | 물리 0.01초, decimation 2, 제어 50 Hz, 최대 10초; 기본 4,096환경 |
| 목표 방향 | 선반 ±X 주변 각각 ±15° 제외, episode 중 목표 고정 |

목표를 먼저 확정한 뒤 `scene_randomization`의 기하 규칙으로 장애물을 배치한다. RED 제외 반경은 10.3 cm, 초기 물체 중심 최소 간격은 9.6 cm다. 배치 실패 시 타겟·목표나 제약을 바꾸지 않고 장애물 배치만 재시도한다.

## 관측

| Term | 차원 | 의미 |
| --- | --- | --- |
| `joint_pos`, `joint_vel` | 6 + 6 | Arm 상대 관절 위치·속도 |
| `actions` | 8 | 직전 raw Action |
| `target_obs_state` | 3 | 현재 타겟 root XYZ; 매 관측 ±1 cm 노이즈 |
| `target_obj_width` | 1 | 실제 값은 반지름 0.04 m; ±1 cm 노이즈 |
| `ee_pose` | 7 | root frame EEF XYZ·quaternion |
| `goal_pos` | 3 | root frame 목표 XYZ |
| `tactile` | 17 | 0.01 N 기준 접촉 bit; 직접 패드·부모 body 투영 접촉 |
| `wrist_wrench` | 6 | EEF 기준점·축의 미보정 반력, N·Nm |

`obstacles`는 10개 슬롯 × `[HEADER, x, y, z]` = 40D다. 실제 장애물 3칸에는 초기 root XYZ와 reset 때 한 번 샘플링한 ±1 cm 오차를 저장하고 나머지 7칸은 0으로 채운다. 현재 장애물 위치로 갱신하지 않는다. Actor·Critic의 별도 MLP 40→32→16 인코더로 각각 압축한다.

Actor·Critic 모두 원시 `policy57 + obstacles40` = **97D**, 임베딩 결합 후 **73D**다. 촉각은 실제 물체 4개 전체를 포함하지만 접촉 물체 ID를 제공하지 않는다. 초기 장애물 관측만 고정이며 타겟 위치는 계속 갱신된다.

## 보상 구조

부모의 10개 항 전체를 유지하며 `object_tilt`의 대상만 확장한다.

| Term | Weight | 계산·적용 범위 |
| --- | --- | --- |
| `reaching` | +30 | EEF–타겟 3D 거리의 새 최선 개선량; 0.10 m 이내 제외 |
| `goal_distance` | +94 | 타겟–목표 XY 거리의 새 최선 개선량; 허용 반경 0.01 m |
| `arm_action_rate` | −0.03 | raw Arm Action 변화량 제곱합 |
| `hand_action_rate` | −0.03 | raw Hand Action 변화량 제곱합 |
| `arm_joint_velocity` | −0.03 | 실제 Arm 6개 관절 속도 제곱합 |
| `hand_joint_velocity` | −0.01 | 실제 Hand 12개 관절 속도 제곱합 |
| `object_tilt` | −2 | 타겟·장애물 4개의 tilt 비용 합; 각 5°→0.9 rad, 각 상한 1 |
| `shelf_collision` | −0.5 | 선반 이동·속도와 가상 finger/wrist의 선반 근접 비용 |
| `pushing_speed` | −2 | 타겟 3D 선속도 >0.2 m/s의 지수 비용, 최대 100 |
| `arm_speed_excess` | −1 | Arm 최대 절대 관절 속도 >1 rad/s의 지수 비용, 최대 100 |

일반 항의 실제 step 기여는 `weight × 반환값 × 0.02초`다. `reaching`·`goal_distance`는 함수 내부에서 dt를 상쇄하므로 `weight × 새 최선 거리 개선량(m)`으로 기여한다. 후퇴 후 이전 기록으로 복귀하는 행동에는 진행 보상이 반복되지 않는다.

네 Arm/Hand 운동 비용은 로컬 `mdp/goal_rewards.py`의 raw 변화량·실제 속도 제곱합을 사용하고 각 출력만 100으로 제한한다. 평균·정규화 또는 Hand 제어 clamp 이후 값을 쓰지 않는다.

`object_tilt`는 개별 기울기 비용을 **합산**하여 [0,4]가 된다. `pushing_speed`는 여전히 타겟만 평가한다. 장애물 이동 거리 비용과 goal-hold·접촉 보상은 이 버전에 없다.

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
| 활성 Curriculum term | 없음 |
| 고정 조건 | 장애물 3개; 목표 방향·free speed·계수는 학습 iteration으로 바뀌지 않음 |

## 근거와 확인 범위

[Env Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter/env_cfg.py) · [배치](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter/layout.py) · [관측](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter/observations_cfg.py) · [보상](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter/rewards_cfg.py) · [다중 물체 MDP](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter/mdp.py) · [개발 이력](../logs/2026-10-20_contact_sweep_clutter.md)

물성·encoder·실행의 상세는 기존 [Contact/Clutter 비교](CONTACT_SWEEP_ENVIRONMENTS.md), 후속 Blind Actor·접촉 보상은 [Clutter v1](CONTACT_SWEEP_CLUTTER_V1_MDP.md)을 참조한다.

현재 설명은 등록, 설정 상속, MDP 계산의 정적 대조 결과다. 과거 로그의 실행 검증은 해당 기록의 조건에만 해당하며 이번 문서 작성의 새 실행 결과로 해석하지 않는다.
