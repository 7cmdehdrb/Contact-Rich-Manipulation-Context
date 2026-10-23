# Contact Sweep Clutter Fusion v2

[환경 변화·계층 지도](ENVIRONMENT_EVOLUTION.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

**기준일: 2026-10-22, 현재 작업트리 코드 확인.** `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v2`의 간결한 독립 설명이다. 초기 가림이 있는 장애물 정보와 보정 F/T를 사용하는 Fusion 분기다. 이 문서 작성에서 학습·재생·실물 성능은 새로 검증하지 않았다.

## 기본 구성

`ContactSweepClutterFusionV2EnvCfg`는 [Fusion v0](CONTACT_SWEEP_CLUTTER_FUSION_ENVIRONMENT.md)를 상속하고 `eef_orientation` 보상만 제거한다. EEF 자세 정렬 비용이 반대쪽으로 돌아가 미는 행동을 방해한다는 기록에 따른 변형이다. 등록 runtime은 v0와 같은 `ContactSweepClutterFusionEnv`다.

| 항목 | 설정 |
| --- | --- |
| 로봇·장면 | UR5e–Axia80–Inspire Hand, 선반 작업면 1.05 m |
| 물체 | 반지름 4 cm·높이 10 cm 원기둥 타겟 1개 + 장애물 3개 |
| 배치 | 타겟: 선반 중앙 반경 2 cm; 목표: 최대 15 cm; 장애물: 뒤쪽 GRAY 1개·WHITE 2개 |
| 초기 상태·물성 | 고정 로봇 관절 자세; reset마다 질량·마찰 랜덤화; 장애물은 같은 환경의 타겟 물성 샘플 공유 |
| Action | 8D: Arm 6D Joint Position, 기본 자세 + 0.5 × raw action; Hand 2D 개방도 |
| 시간·병렬 환경 | 물리 0.01초, decimation 2, 제어 50 Hz, 최대 10초; 기본 4,096환경 |
| 목표 방향 | 선반 ±X 주변 각각 ±60° 제외로 시작; 커리큘럼으로 해제 |

장애물은 3개이며 RED 제외 반경 10.3 cm다. Fusion v0는 Curriculum v1·Clutter v2의 설계를 통합한 독립 Cfg이므로 이 분기가 그 두 Env Cfg를 직접 상속하는 것은 아니다.

## 관측

| Term | 차원 | 의미 |
| --- | --- | --- |
| `joint_pos`, `joint_vel` | 6 + 6 | Arm 상대 관절 위치·속도 |
| `actions` | 8 | 직전 raw Action |
| `target_obs_state` | 3 | 초기 타겟 root XYZ; reset 때 고정 ±1 cm 오차 |
| `ee_pose` | 7 | root frame EEF XYZ·quaternion |
| `goal_pos` | 2 | 초기 타겟→목표 거리·root 기준 시계 방향 방위각 |
| `tactile` | 17 | 0.01 N 기준 접촉 bit; 직접 패드·부모 body 투영 접촉 |
| `wrist_wrench` | 6 | EEF 기준점·축의 Hand 중력·관성 보정 외력 반력 추정값 |

`policy`는 **55D**다. 폭 1D를 제거하고 목표 XYZ 3D를 초기 타겟→목표의 거리·방위각 2D로 바꾸었다. root +X=0, −Y=π/2, −X=π, +Y=3π/2이며 초기 목표 벡터는 episode 동안 고정된다.

`obstacles` 40D는 10개 `[HEADER, x, y, z]` 슬롯이다. 초기 장애물 3개의 가시성을 임계값 0.35로 분류한 뒤 각 판정을 독립 1% 확률로 뒤집는다. 숨긴 슬롯 전체와 더미 7칸을 0으로 만든다. 이후 위치·가시성을 갱신하지 않으며 실제 장애물을 제거하는 것은 아니다.

초기 위치에는 reset 시 ±1 cm 오차를 적용한다. 장애물 encoder는 Actor·Critic별 40→32→16 MLP다. Actor는 원시 **95D**, 결합 후 **71D**; Critic은 현재 타겟 XYZ 3D를 더해 원시 **98D**, 결합 후 **74D**다. Actor에 현재 타겟 위치나 접촉 물체 ID는 추가하지 않는다.

## 보상 구조

활성 **14개** 항 전체다. `eef_orientation`은 비활성(`None`)이며 계수·free speed의 변화는 아래 커리큘럼 표를 따른다.

| Term | Weight | 계산·적용 범위 |
| --- | --- | --- |
| `reaching` | +30 | EEF–타겟 3D 새 최선 개선량; 0.10 m 이내 제외 |
| `goal_distance` | +100 | 타겟–목표 XY 새 최선 개선량; 허용 반경 0.01 m |
| `goal_hold` | +0.9 | 타겟이 목표 월드 XY 1 cm 안에 있는 동안 1 |
| `contact_any` | +0.4 | 현재 촉각 하나 이상 ON이면 1 |
| `contact_count` | +0.4 | 현재 촉각 ON 영역 수 / 5, 최대 1 |
| `action_rate` | −0.03→−0.06 | Arm·Hand raw 변화량 제곱합을 각각 상한 100으로 제한한 뒤 합 |
| `joint_velocity` | −0.03 | Arm 속도 제곱합 + Hand 속도 제곱합 / 3; 각 그룹 상한 100 |
| `object` | −30 | 전체 tilt 비용 + 2.5 × 장애물 이동 제곱합; 이동 항 상한 0.04 m² |
| `shelf_collision` | −0.5 | 선반 이동·속도 및 가상 finger/wrist 근접 비용 |
| `pushing_speed` | −5 | 타겟 3D 선속도 초과 지수 비용; raw 상한 100 |
| `arm_speed_excess` | −1 | Arm 최대 절대 관절 속도 초과 지수 비용; raw 상한 100 |
| `shelf_failure` | −3 | 선반 실패 종료 전이에서 실제 −3 한 번 |
| `eef_linear_speed` | −1 | 실제 EEF 점 선속도 초과 지수 비용; raw 상한 100 |
| `wrench_change` | −0.1 | 보정 F/T 변화율의 bounded 지수 비용; raw 상한 1·양의 보상 5% 예산 |

일반 term은 `weight × 반환값 × 0.02초`로 합산한다. 진행 보상과 `shelf_failure`는 내부에서 dt를 상쇄해 각각 미터 단위 개선량 보상·일회성 실패 비용이 된다. 목표 체류는 시간 누적 조건 없이 월드 XY 1 cm 판정이며 성공으로 종료하지 않는다.

`object`는 기존 −2 tilt·−5 장애물 이동 비용을 15배 강화한 조합이다. `action_rate`와 `joint_velocity`는 로컬 raw 제곱합 함수를 호출해 그룹별 상한을 유지한다. Action 계수 curriculum은 합쳐진 Arm·Hand 양쪽에 적용되고 joint velocity의 실효 계수는 Arm −0.03·Hand −0.01로 고정된다.

`wrench_change`는 월드 축에서 보정 힘·모멘트의 step 변화 norm을 dt로 나눈 **변화율**을 사용한다. 자유 구간~포화 구간의 정규화 초과율 중 큰 값을 bounded 지수 함수에 넣는다. 최대 −0.1/초이면서 episode 누적 양의 보상의 5% 안에서만 비용을 부과한다. 첫 유효 샘플은 비용 없이 이력을 시작한다. 이는 Clutter v2의 변화량 제곱 비용과 다르다.

## 터미네이션

| Term | 종료 조건 |
| --- | --- |
| `time_out` | 10초; timeout 처리 |
| `object_drop` | 타겟·장애물 중 하나라도 밑면 높이 <1.04 m 또는 선반 법선 대비 tilt ≥0.9 rad |
| `push_fast` | 타겟 3D 선속도 norm >1.0 m/s |
| `shelf_collision` | 선반 root velocity norm >0.1 또는 wrist 선반면 위 높이 <0.03 m; finger 검사는 비활성 |
| `hand_velocity` | 이름과 달리 Arm 6개 중 절대 속도 >5 rad/s |
| `shelf_displacement` | 선반 초기 위치 대비 이동 거리 >0.05 m |

`object_outside_shelf`는 비활성이다. 성공 종료는 없으며 목표 도달 뒤에도 실패 또는 timeout까지 진행한다. `shelf_collision`의 0.1은 접촉력 임계값이 아니라 선반의 선속도·각속도 성분이 함께 든 root velocity 벡터 norm 기준이다.

**현재 코드와 과거 기록의 차이:** v0의 `terminations_cfg.py`가 `push_fast=1.0`을 선언하고 v2는 이를 바꾸지 않는다. 과거 비교·로그에는 0.8로 적혀 있으나 이 표는 현재 코드의 1.0을 따른다. [v3](CONTACT_SWEEP_CLUTTER_FUSION_V3_ENVIRONMENT.md)는 명시적으로 0.8을 설정한다.

## 커리큘럼

| Term / 적용값 | 초기→최종 | 일정 |
| --- | --- | --- |
| `pushing_free_speed` | 0.1→0.05 m/s | 300 iteration마다 −0.01 |
| `arm_free_speed` | 1.0→0.8 rad/s | 300 iteration마다 −0.02 |
| `action_rate_weight` | −0.03→−0.06 | 300 iteration마다 −0.005 |
| `eef_free_speed` | 1.5→0.7 m/s | 300 iteration마다 −0.02 |
| `goal_deadzone` / ±X 각 제외 반각 | 60°→0° | 500까지 유지; 700부터 200 iteration마다 −1° |

0부터 시작하는 Learning iteration의 절대값으로 매번 다시 계산한다. 첫 네 항은 `floor(iteration / 300)`으로 갱신한다. Goal 일정은 `floor((iteration−500)/200)`의 음수를 0으로 제한하므로 첫 감소는 700이다. 보상 변경은 진행 중 episode에도 적용되지만 목표 방향은 다음 reset부터 적용된다. 접촉 weight +0.4와 F/T 자유/포화 구간 2000/5000 N/s, 100/250 Nm/s는 고정이다.

## 근거와 확인 범위

[Env Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/contact_sweep_clutter_fusion_envs.py) · [공통 관측](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/contact_sweep_clutter_fusion.py) · [공통 보상](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/contact_sweep_clutter_fusion.py) · [F/T 비용](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/contact_sweep_clutter_fusion.py) · [커리큘럼](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/contact_sweep_clutter_fusion.py) · [개발 이력](../logs/2026-10-21_clutter_fusion_v3.md)

설계 의도는 지정 [Notion 환경 기록](https://app.notion.com/p/3f7bd3c55e1b80e5a161c6e0dd175773)과 [Fusion 버전 비교](CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md)를 참고했다. 기존 문서의 일정·종료 수치가 다르면 위에 명시한 현재 코드 기준을 따른다.

현재 설명은 등록, 설정 상속, MDP 계산의 정적 대조 결과다. 과거 로그의 실행 검증은 해당 기록의 조건에만 해당하며 이번 문서 작성의 새 실행 결과로 해석하지 않는다.
