# Isaac-Inspire-Sweep-Omni-v3 — 환경 구성

[구현 문서 안내](../README.md) · [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)

기준일: **2026-10-15**. 대상은 Gym ID `Isaac-Inspire-Sweep-Omni-v3`, 설정 클래스 `InspireSweepOmniV3EnvCfg`, 실행 클래스 `InspireSweepEnv`다. 이 문서는 현재 작업트리의 기본 설정을 기준으로 관측·리워드·터미네이션·이벤트를 독립적으로 설명한다. 코드 정독과 CPU 검증에 근거하며 새 학습·재생·실물 검증 결과를 뜻하지 않는다.

코드 기준은 workspace commit `21bbae5f0fcaeaf3eb4014dd92f026b6cae9158c`와 확인 당시 미커밋 변경이다. 특히 `omni_env_cfg.py`의 Arm 속도 종료 기준을 **1.5 rad/s로 바꾼 기존 변경**을 포함한다. CLI override와 과거 checkpoint에 저장된 config는 이 기본 설정과 별도로 확인한다.

## 1. 관측 입력

`ObservationsCfg.PolicyCfg`의 term을 아래 순서로 이어 붙여 **41D** 벡터를 만든다. 기본 PPO runner는 Actor와 Critic 모두 `policy` 그룹을 사용한다. 별도 privileged Critic 입력이나 observation history stack은 없다. Runner의 Actor/Critic 관측 정규화도 꺼져 있다.

| 순서 | Term | 차원 / 인덱스(0부터) | 값·단위·좌표계 |
| --- | --- | --- | --- |
| 1 | `joint_pos` | 6D / 0–5 | Arm 현재 관절각 − 기본 관절각, rad |
| 2 | `joint_vel` | 6D / 6–11 | Arm 현재 관절속도 − 기본 관절속도, rad/s |
| 3 | `actions` | 8D / 12–19 | ActionManager에 저장된 최근 raw action. Arm 6D + Hand 2D |
| 4 | `target_obs_state` | 3D / 20–22 | 현재 대상 물체 위치, Robot root 좌표계, m |
| 5 | `target_obj_width` | 1D / 23 | `target_width` 값. 이름은 width이지만 reset에서 물체 **반지름 0.04 m**를 기록 |
| 6 | `ee_pose` | 7D / 24–30 | EEF 위치 3D(m) + quaternion 4D(w,x,y,z), Robot root 좌표계. Quaternion은 `quat_unique` 적용 |
| 7 | `goal_pos` | 3D / 31–33 | 에피소드 고정 목표 위치, Robot root 좌표계, m |
| 8 | `tactile` | 1D / 34 | 실제 palm pad의 순접촉력 크기가 0.05 N 이상이면 1, 아니면 0 |
| 9 | `wrist_wrench` | 6D / 35–40 | EEF 축과 EEF 원점으로 변환한 `[Fx,Fy,Fz,Mx,My,Mz]`, N 및 N·m |

Arm 6개 관절 순서는 `shoulder_pan_joint`, `shoulder_lift_joint`, `elbow_joint`, `wrist_1_joint`, `wrist_2_joint`, `wrist_3_joint`다. Hand 관절각·관절속도는 관측에 직접 포함하지 않는다.

`enable_corruption=True`이며 현재 물체 위치의 각 성분과 `target_obj_width`에 `Uniform(-0.01, +0.01)` m 가산 노이즈를 넣는다. 다른 term에는 이 설정의 추가 노이즈가 없다. 목표는 reset 때 고정되지만 **물체 위치는 매 step 현재 simulation GT에서 갱신**된다. 따라서 실행 중 물체 위치를 관측하는 환경이다.

EEF는 손가락 끝이 아니라 손목 조립체에 고정된 기준점이다. `axia80_link` 기준 위치 `(0, 0, 0.13 + sensor_height/2)`에 두며, Hand-local `(0, 0, 0.13)`에 해당한다. 손가락만 굽혀도 이 점은 이동하지 않는다.

Palm 입력은 `inspire_palm_force_sensor` **한 영역**의 Binary 값이다. 물체 전용 접촉 필터나 접촉 대상 ID가 아니며, 17개 영역 입력도 아니다. F/T는 fixed-joint 반력을 사용하며 힘의 회전과 기준점 이동에 따른 모멘트 변환을 수행한다. Hand 무게를 포함하고 중력 상쇄·tare·추가 필터는 적용하지 않는다. Reset 직후에는 `sensor_data_fresh=False`인 행의 tactile과 F/T를 0으로 내보낸다.

`actions`는 step 이후 관측 시 방금 적용한 action이며, 이를 입력받는 다음 정책 판단 기준으로는 직전 action이다. Reset 관측에서는 Arm 이력 6개는 0, Hand 이력 2개는 open을 뜻하는 1이다.

## 2. 리워드 설계

활성 보상은 접근 진행 1개, 목표 진행 1개, 보조 페널티 6개로 **총 8개**다. 시간 비용, 성공 보너스, 실패 terminal 비용은 모두 비활성이다.

물리 step은 0.01 s, decimation은 2이므로 정책 step `Δt=0.02 s`다. RewardManager는 각 함수 출력에 `weight × Δt`를 곱해 합산한다. 두 진행 함수는 내부에서 `Δt`로 나누므로 진행량에 대한 최종 보상은 step 시간에 다시 비례하지 않는다. 아래 페널티는 내부에서 나누지 않아 초당 비용처럼 누적된다.

### 접근 진행: `reaching`

함수는 `HeightGatedPlanarReachProgress`, 가중치는 **30.0**, `near_radius=0.10 m`, `z_offset=0.09 m`, `z_tolerance=0.02 m`다. 아래 식에서 `p_E`는 EEF, `p_O`는 물체 바닥 원점의 월드 위치다. EEF와 **현재 물체 바닥 원점** 사이의 XY 거리에서 10 cm를 뺀 나머지를 접근 거리로 사용한다.

```math
d_t=\max(\lVert p_{E,xy}(t)-p_{O,xy}(t)\rVert-0.10,0),\qquad b_t=\min(b_{t-1},d_t).
```

Reset 시 `d₀`를 구하고 최단 기록 `b₀=d₀`로 초기화한다. 현재 step이 기록을 갱신한 만큼 `(b이전 − b현재)/max(d₀, 10⁻⁶)`을 계산한다. 다음 높이 조건을 만족할 때만 이 진행량에 가중치 30을 곱해 지급한다.

```math
\left|p_{E,z}(t)-(p_{O,z}(t)+0.09)\right|\leq 0.02.
```

물체 바닥 원점이 1.05 m인 정상 배치라면 EEF 허용 높이는 약 **1.12–1.16 m**다. 기준은 물체 중심 높이가 아니라 바닥 원점 + 0.09 m이며, 물체가 움직이면 높이 기준도 갱신된다.

**높이 범위 밖에서도 XY 최단 기록은 갱신**된다. 따라서 잘못된 높이에서 먼저 접근한 다음 Z만 조정해 이전 접근량을 다시 받을 수 없다. 정지·후퇴 후 이전 기록까지 복귀해도 보상은 없다. 높이 조건을 모두 지키며 접근 거리를 소진할 경우 누적 접근 보상 상한은 **30**이다. Reset 때 이미 10 cm 안이면 접근 거리와 지급 가능한 보상은 0이다. 물체가 EEF 쪽으로 움직여 상대 거리가 줄어도 진행으로 계산한다.

#### 수식의 의미와 계산 예시

이 수식은 **올바른 높이에서, 물체와의 수평 거리를 에피소드의 이전 최단 기록보다 더 줄인 비율**에 보상을 준다. 현재 위치가 가깝다는 사실만으로 매 step 보상을 지급하지 않는다.

| 기호·연산 | 의미 |
| --- | --- |
| `t` | 현재 정책 step. `t−1`은 직전 정책 step |
| `p_E,xy(t)`, `p_O,xy(t)` | 현재 EEF와 물체 바닥 원점의 월드 X·Y 위치 |
| `‖p_E,xy − p_O,xy‖` | 두 점의 수평 직선거리. X·Y 차이의 제곱을 더하고 제곱근을 취한 값 |
| `dₜ` | 10 cm 근접 영역까지 남은 수평 접근 거리. 실제 수평 거리가 18 cm면 8 cm, 10 cm 이하면 0 |
| `max(거리 − 0.10, 0)` | 근접 영역 안으로 더 들어가도 접근 거리를 음수로 만들지 않고 0에 고정 |
| `bₜ₋₁`, `bₜ` | 현재 step 계산 전·후의 에피소드 최단 접근 거리 기록. `min`을 사용하므로 기록은 작아지거나 유지됨 |
| `bₜ₋₁ − bₜ` | 이번 step에서 새로 개선한 기록의 길이(m). 직전 위치에서 움직인 거리 전체와는 다름 |
| `d₀` | Reset 직후의 남은 수평 접근 거리. 이번 에피소드에서 처음 주어진 접근 과제의 크기 |

계산은 **수평 거리 → 10 cm 영역까지 남은 거리 → 최단 기록 갱신 → 초기 거리로 나눈 개선 비율 → 높이 조건 확인 → 가중치 적용** 순서다. 높이 조건이 참일 때 RewardManager까지 반영한 접근 보상은 다음과 같다.

```math
r_t^{\mathrm{reach}}=30\frac{b_{t-1}-b_t}{\max(d_0,10^{-6})}.
```

높이 조건이 거짓이면 이 step의 접근 보상은 0이다. 분모는 초기 접근 거리 대비 이번 개선량의 **비율**을 만든다. `10⁻⁶`은 초기 거리가 0일 때 0으로 나누는 것을 피한다. 높이식의 절댓값은 EEF가 `물체 바닥 높이 + 9 cm`에서 위아래로 얼마나 벗어났는지를 나타내며, 그 오차가 2 cm 이하여야 한다.

예를 들어 reset 수평 거리가 30 cm라면 `d₀=b₀=20 cm`다. 다음은 보조 페널티를 제외한 접근 보상만 계산한 예시다.

| Step | 현재 수평 거리 | 남은 거리 `dₜ` | 최단 기록 변화 | 높이 조건 | 접근 보상 |
| --- | --- | --- | --- | --- | --- |
| 1 | 25 cm | 15 cm | 20 → 15 cm | 만족 | `30 × 5/20 = 7.5` |
| 2 | 28 cm | 18 cm | 15 → 15 cm | 만족 | 0: 후퇴했으므로 새 기록 없음 |
| 3 | 25 cm | 15 cm | 15 → 15 cm | 만족 | 0: 이전 최선 위치로 복귀 |
| 4 | 20 cm | 10 cm | 15 → 10 cm | 불만족 | 0: 기록은 갱신하지만 지급하지 않음 |
| 5 | 20 cm | 10 cm | 10 → 10 cm | 만족 | 0: 높이만 맞춰도 이전 개선량은 재지급하지 않음 |
| 6 | 10 cm | 0 cm | 10 → 0 cm | 만족 | `30 × 10/20 = 15` |

이 예시의 누적 접근 보상은 **22.5**다. Step 4에서 높이 조건을 지키지 못한 개선 비율만큼은 이후에 회수할 수 없다. 모든 기록 개선을 허용 높이에서 수행했다면 같은 초기 거리에서 총 30을 받을 수 있다. 코드가 반환하는 값은 위 최종 보상을 만들기 위해 개선 비율을 `Δt`로 나눈 값이며, RewardManager의 `× Δt`와 상쇄된다.

### 목표 진행: `goal_distance`

함수는 `PlanarGoalProgress`, 가중치는 **40.0**, 목표 허용오차는 **0.01 m**다. 물체 바닥 원점에서 에피소드 고정 목표까지 **월드 XY 거리**를 사용한다. Reset 물체 위치와 새 목표 사이 거리를 `D₀`, 현재 거리를 `Dₜ`라 둔다.

```math
P_t=\mathrm{clamp}\left(\frac{D_0-D_t}{\max(D_0-0.01,10^{-6})},0,1\right),\qquad B_t=\max(B_{t-1},P_t).
```

최종 step 보상은 `40 × (B현재 − B이전)`이다. Reset 위치는 reward reset에서 먼저 저장하고 새 command를 첫 계산 때 읽으므로 첫 action의 개선도 포함한다. `D₀ − 0.01 ≤ 10⁻⁶`이면 진행량을 0으로 처리한다.

목표 1 cm 이내까지 진행하면 누적 목표 보상 **40**을 소진한다. 거리를 줄이지 않고 머물거나, 후퇴한 뒤 과거 최선 거리로 복귀하면 추가 보상은 없다. 후퇴에 대한 별도 음의 진행 보상도 없다. 위치 허용오차에 도달하는 것은 보상 소진 조건이며 종료 조건은 아니다.

### 보조 페널티

| Term | 함수 | 가중치 | 함수가 계산하는 값 |
| --- | --- | --- | --- |
| `arm_action_rate` | `goal_rewards.action_rate_l2` | −0.03 | Arm raw action 6개의 이전 step 대비 변화량 제곱합 |
| `hand_action_rate` | `goal_rewards.action_rate_l2` | −0.03 | Hand raw action 2개의 이전 step 대비 변화량 제곱합 |
| `arm_joint_velocity` | `goal_rewards.joint_vel_l2` | −0.03 | Arm 실제 관절속도 6개의 제곱합 |
| `hand_joint_velocity` | `goal_rewards.joint_vel_l2` | −0.01 | `HAND_JOINT_NAMES`로 지정한 Hand 실제 관절속도 **12개**의 제곱합 |
| `object_tilt` | `goal_rewards.object_tilt_cost` | −2.0 | 선반 법선과 물체 local up 사이 기울기에 대한 bounded 제곱 비용 |
| `shelf_collision` | `mdp.ShelfCollisionPenalty` | −0.5 | 선반 이동·속도 및 가상 finger/wrist 기준점의 낮은 높이 비용 |

Action 변화 비용은 action 크기 자체, 평균, 정규화 값 또는 제어 입력으로 clamp한 Hand 값에 대한 비용이 아니다. ActionManager의 raw 값 차이를 그대로 제곱해서 더한다. 관절속도 비용은 목표 속도가 아닌 실제 속도를 사용한다. 네 항은 각각 유지하며 별도 시간 미분이나 속도 정규화를 하지 않는다.

기울기 각도 `θ`에 대한 함수 값은 `clamp((θ − 5°)/(0.9 rad − 5°), 0, 1)²`다. 5° 이하는 0, 0.9 rad 이상은 1이다. 자세의 yaw 회전 자체를 벌점으로 주지 않는다.

`ShelfCollisionPenalty`는 접촉력 기반 충돌 검출기가 아니다. 다음 값을 더한다.

- 선반 기본 위치 대비 이동 거리와 `root_vel_w` 6D norm의 합이 0.005보다 크면 1.
- 선반 root 위치의 Z에 1.06 m를 더한 기준점에서 EEF까지 거리가 0.2 m 미만일 때, 가상 finger 두 점과 wrist 한 점의 높이 비용. Finger 각각은 `clamp(1 − 높이/0.02, 0, 1)`, wrist는 `clamp(1 − 높이/0.08, 0, 1)`을 사용한다.

여기서 높이는 위 기준점 Z에 대한 상대 높이다. Finger 두 점과 wrist는 Hand base에 고정한 가상 프레임이며 실제 접촉 센서 값이 아니다. 이 비용의 높이 기준 1.06 m는 종료 조건의 1.05 m와 다르다.

## 3. 터미네이션 조건

기본 에피소드 길이는 10 s이며 정책 주기 0.02 s 기준 최대 500 step이다. 아래 조건 중 하나라도 만족하면 해당 환경이 reset된다.

| Term | 종료 조건 | 분류 |
| --- | --- | --- |
| `time_out` | `episode_length_buf >= max_episode_length` | Timeout / truncated |
| `object_drop` | 물체 바닥 원점의 환경 원점 대비 Z가 **1.04 m 미만**, 또는 선반 법선 대비 기울기가 **0.9 rad 이상** | 실패 / terminated |
| `push_fast` | 대상 물체의 월드 선속도 **3D norm > 0.3 m/s** | 실패 / terminated |
| `shelf_collision` | 아래 선반 속도·가상 프레임 높이 조건 중 하나라도 만족 | 실패 / terminated |
| `hand_velocity` | Arm 6개 중 어느 관절이든 **절대속도 > 1.5 rad/s** | 실패 / terminated |
| `object_outside_shelf` | 선반 local 좌표에서 물체 바닥 중심의 **abs(x) > 0.20 m 또는 abs(y) > 0.50 m** | 실패 / terminated |
| `shelf_displacement` | 선반 기본 root 위치 대비 현재 root 위치의 **3D 거리 > 0.05 m** | 실패 / terminated |

`hand_velocity`라는 이름은 과거 로그 호환을 위해 남아 있으며, 검사 대상은 **Hand가 아니라 Arm**이다. 1.5 rad/s는 2026-10-15 확인한 작업트리 값이다. 저장된 학습 config나 CLI override가 있으면 실행값은 별도로 확인해야 한다.

`shelf_collision`은 선반 `root_vel_w`(선속도 3D + 각속도 3D)의 norm이 0.1보다 크거나, finger 두 점 중 하나의 높이가 0.01 m 미만이거나, wrist 점 높이가 0.07 m 미만이면 참이다. 높이 기준은 현재 선반 root Z + 1.05 m다. 이 조건에는 보상 함수의 EEF 근접 gate가 없다. 속도 norm은 선속도와 각속도를 함께 포함하므로 단일 선속도 임계값으로 해석하지 않는다.

`object_outside_shelf`는 물체 **중심**이 판 외곽을 넘는지 검사한다. 물체 반지름이나 reset 시 edge clearance를 차감하지 않는다. `object_drop`은 물체의 전체 바닥 면 최저점이 아닌 바닥 원점 높이를 검사한다.

**목표 도달에 따른 성공 종료 term은 비활성(`success=None`)이다.** 목표 허용오차 1 cm에 도달해도 즉시 reset되지 않는다. 목표 도달 후 실패 조건 또는 timeout이 발생할 때까지 실행한다. 성공·실패 terminal reward도 없으며, 이 문서의 목표 허용오차는 보상 계산 기준이다.

## 4. 이벤트 구성

이벤트는 초기화 시 `startup`과 에피소드 reset 시 `reset`으로 구성한다. 주기적 외란을 주는 `interval` 이벤트는 없다.

| Mode | Term | 함수 | 역할 |
| --- | --- | --- | --- |
| `startup` | `physics_materials` | `initialize_realistic_materials` | 물성 Tensor API 버퍼와 마찰 pool을 한 번 준비 |
| `reset` | `reset_all` | `mdp.reset_scene_to_default` | 선반·로봇의 기본 pose/velocity 및 로봇 기본 관절 상태 복원 |
| `reset` | `object_spawn` | `randomize_goal_object_scene` | 물체 시작 pose와 Sweep 방향·거리 생성 |
| `reset` | `physics_randomization` | `randomize_episode_physics` | 해당 에피소드의 물체 질량·관성 및 마찰 변경 |

Reset 이벤트는 위 reset 행 순서로 실행한다. 물체 배치 후 reward manager가 거리 기록을 초기화하고, command manager가 새 목표를 설정한다. `reset_all`은 선반 rigid object와 로봇 articulation을 복원한다. `object_collection`의 실린더 상태는 뒤의 `object_spawn`이 직접 기록한다. 기본 장면 복원은 임의 접근 자세를 샘플링하는 기능이 아니다.

### 물체 배치와 목표 생성

선반 기본 root 위치는 환경 원점 기준 `(-0.7, 0, 0)`이며, 기하 샘플링은 reset된 선반의 **local 좌표계**에서 수행한다.

1. 선반 중앙의 반지름 **0.02 m 원판**에서 XY를 면적 균일하게 샘플링한다. 반지름은 `0.02 × sqrt(U)`로 뽑으며, Z는 **1.05 m**다.
2. 물체 yaw를 `Uniform(-π, π)`로 뽑는다. 선반 자세에 이 yaw를 곱하고 선속도·각속도는 0으로 설정한다.
3. 별도로 Sweep 방위각을 `Uniform(-π, π)`로 뽑는다. 목표 이동 거리는 최대 **0.15 m**다.
4. 물체 반지름 **0.04 m**와 edge clearance **0.02 m**를 제외한 안전 반폭 `(0.14, 0.44)` m 안에 목표가 들어오게 한다. 같은 방향의 ray를 유지하면서 필요한 경우 거리를 줄인다. 현재 수치에서는 주로 짧은 X축 가장자리 방향에서 거리가 줄어들 수 있다.
5. `target_id=0`, `target_width=0.04`로 기록하고 변위를 월드 좌표로 변환해 `sweep_dir`에 저장한다. `SweepGoalCommand`가 reset 물체 위치에 이 변위를 더해 목표를 고정한다.

Command 자체는 위치 3D와 초기 quaternion 4D를 반환하지만, 관측은 목표 위치 3D만 사용하고 목표 진행 보상은 월드 XY 거리만 사용한다. Command 재샘플 간격은 1,000,000 s로 기본 10 s 에피소드 도중에는 바뀌지 않는다. 물체 yaw 샘플링 외에 로봇 자세·선반 자세의 랜덤화나 IK·초기 접촉 보장 검사는 이 이벤트에 없다.

### 질량·마찰 랜덤화

물체 질량은 `Normal(0.365, 0.0675²)` kg에서 뽑아 **[0.230, 0.500] kg로 clamp**한다. Rejection sampling 방식의 절단 정규분포가 아니다. 물체 관성 텐서는 기본 관성에 `새 질량 / 기본 질량`을 곱해 함께 조정한다.

| 적용 대상 | 정마찰 평균 / 표준편차 | 동마찰 평균 / 표준편차 |
| --- | --- | --- |
| 선반 | 0.315 / 0.051 | 0.252 / 0.041 |
| 물체 | 0.315 / 0.040 | 0.252 / 0.032 |
| Hand 접촉 collider | 0.585 / 0.145 | 0.468 / 0.116 |

각 대상별로 Gaussian quantile로 만든 **4096개** 마찰 쌍 pool을 준비하고 음수는 0으로 clamp한다. 동마찰 순서를 별도로 섞어 정·동마찰의 상관을 줄이며, reset마다 대상별 pool index를 독립적으로 뽑는다. 같은 대상 역할에 속한 collider에는 같은 샘플을 적용한다. Arm·Axia80의 마찰과 restitution은 이 reset 랜덤화에서 바꾸지 않는다. 질량·마찰 샘플은 관측 벡터에 직접 제공하지 않는다.

## 코드 근거와 확인 범위

| 확인 대상 | 실제 소스 |
| --- | --- |
| Gym 등록 | [__init__.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py) |
| 최종 환경 설정 | [omni_env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/omni_env_cfg.py) |
| 관측·기본 장면·종료·이벤트 선언 | [env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/env_cfg.py) |
| 관측 계산과 센서 변환 | [observations.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations.py), [sensors.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/sensors.py) |
| 진행 보상 | [mdp/goal_rewards.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/goal_rewards.py) |
| Action·관절속도·기울기 비용 | [goal_rewards.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/goal_rewards.py) |
| 선반 비용 | [rewards.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards.py) |
| 종료 판정 | [terminations.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations.py), [goal_terminations.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/goal_terminations.py) |
| 물체·목표 reset | [goal_events.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/goal_events.py), [commands.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/commands.py) |
| 물성 이벤트 | [realistic_physics_env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/realistic_physics_env_cfg.py), [realistic_physics.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/realistic_physics.py) |
| 센서 유효 상태·Action 이력 reset | [env.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/env.py) |
| Actor/Critic 관측 그룹 | [rsl_rl_ppo_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agents/rsl_rl_ppo_cfg.py) |

코드 링크는 통합 workspace 기준이다. 문서 저장소만 clone하면 외부 소스 링크는 연결되지 않는다. 관측·리워드·종료·이벤트 관련 CPU 검사와 문서 검사의 실제 명령·결과는 [작성·검증 로그](../logs/2026-10-15_environment_contract_notes.md)에 기록했다. 시뮬레이터에서의 실제 센서 출력·접촉·정책 성능과 저장 checkpoint의 적용 설정은 이번 문서 작성에서 검증하지 않았다.
