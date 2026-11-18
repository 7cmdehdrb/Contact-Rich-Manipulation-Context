# Prof-v2 · Finger-ForceDirection-v0 상세 명세

2026-11-14 현재 코드 기준. 대상은 `Inspire-Sweep-Simple-Prof-v2`와 `Inspire-Sweep-Simple-Finger-ForceDirection-v0`이다. 두 환경의 공통 Scene·관측·제어를 먼저 설명하고, 서로 다른 보상 설계를 구분한다. CLI/Hydra override 없이 등록된 기본 설정을 기준으로 한다.

[Simple 계열 전체 안내](SWEEP_SIMPLE_ENVIRONMENTS.md) · [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md) · [작성·검증 기록](../logs/2026-11-14_prof_force_direction_detail.md)

## 1. 목적과 구성 방식

두 환경은 선반 위 원통 타겟을 목표 XY 위치로 밀어 옮기는 과제다. 시작할 때 얻은 물체 위치 추정은 에피소드 중 갱신하지 않는다. 정책은 현재 로봇 상태·촉각·손목 F/T와 초기 장면 정보를 사용하고, 보상과 성공 평가는 시뮬레이터의 현재 물체 상태를 사용한다.

| 항목 | Prof-v2 | Finger-ForceDirection-v0 |
| --- | --- | --- |
| 직접 EnvCfg 부모 | `SweepSimpleProfV1EnvCfg` | `SweepSimpleFingerV0TestEnvCfg` |
| EnvCfg | `SweepSimpleProfV2EnvCfg` | `SweepSimpleFingerForceDirectionEnvCfg` |
| runtime | `SweepSimpleFingerEnv` | `SweepSimpleFingerForceDirectionEnv` |
| PPO 설정 | `SweepSimpleProfV2PPORunnerCfg` | `SweepSimpleFingerForceDirectionPPORunnerCfg` |
| 실험명 | `inspire_sweep_simple_prof_v2` | `inspire_sweep_simple_finger_force_direction_v0` |
| 주요 목적 | Prof-v1의 위에서 누르기·빠른 왕복 행동에 액션 범위와 팔 속도 종료 제약을 적용 | Test의 안정성을 전제로 힘 방향과 목표 근방의 접촉 보상 조건을 바꿔 정밀도를 개선 |
| 목표 접근 보상 | 접촉 중 직전 스텝 대비 접근량 | 에피소드 최고 접근 기록의 갱신량 |
| 방향 유도 | 초기 이동 방향에서 벗어난 **변위** 비용 | 현재 목표 방향과 실제 **힘**의 코사인 보상/비용 |
| 접촉 유지 보상 | 없음 | 있음. 목표 1cm 미만에서는 무조건 최대값 |

EnvCfg 상속 경로는 다음과 같다. 공통 기반은 Simple-v0이며, Prof-v2가 Finger-v0-Test를 상속하는 구조는 아니다.

```text
Simple-v0 → Prof-v0 → Prof-v1 → Prof-v2
Simple-v0 → Simple-v1 → Finger-v0 → Finger-v0-Test → Finger-ForceDirection-v0
```

Isaac Lab의 Manager-based RL 구성이다. EnvCfg가 Scene, Observation, Action, Command, Event, Reward, Termination, Curriculum 설정을 조합한다. Gym 등록은 runtime·EnvCfg·PPO 설정을 연결한다. runtime은 reset/step, 센서 유효성, 통계와 손 액션 이력 초기화를 관리한다. ForceDirection runtime에는 물리 substep별 타겟 접촉력 수집이 추가된다.

두 환경 모두 **팔 6축 + 손 6축**이다. Prof-v2의 과거 손 2축/전체 액션 8D 구성은 현재 사양이 아니다. 해당 구형 체크포인트를 현재 12D 모델로 직접 재개할 수 없다. 보상 높이 제한은 현재 두 환경 모두 12cm이며, 전 계열 통일 이후에는 Prof-v1도 같은 12cm를 사용한다.

## 2. Scene 구성

| 구성 요소 | 설정 및 역할 |
| --- | --- |
| 병렬 환경 | 기본 2,048개, 환경 간격 2.5m, `replicate_physics=False` |
| 로봇 | UR5e 6축 팔 + Inspire 오른손 12개 물리 관절 + AXIA80 손목 센서 |
| 손 제어 자유도 | 독립 구동 6관절. 나머지 관절은 mimic 관계로 연동 |
| 로봇 자산 | 패키지의 `assets/data/wrench_right_hand/ur5e_inspire_right.usda`를 로봇 스포너로 생성 |
| 선반 | 표면 40×100cm, 표면 높이 1.05m, 질량 30kg, root 초기 위치 (−0.7, 0, 0)m |
| 타겟 | `mass_cylinder`, 슬롯 0에 고정된 cylinder 1개 |
| 장애물 풀 | `obstacle_0`~`obstacle_15`, 총 16개. 아래 8종을 2개씩 보유 |
| 장애물 종류 | cylinder, cube, mug, bottle, `003_cracker_box`, `004_sugar_box`, `005_tomato_soup_can`, `002_master_chef_can` |
| 실제 활성 장애물 | 매 reset 0~6개. 타겟 포함 활성 물체 총 1~7개 |
| 비활성 물체 | 선반 밖 높은 주차 위치로 이동하고 중력을 끄며, 활성 물체 마스크로 보상·배치·관측에서 제외 |
| 배경 | 지면 plane, dome light 색 (0.75, 0.75, 0.75), intensity 2500 |
| 시간 | physics dt 0.01초(100Hz), decimation 2, policy dt 0.02초(50Hz) |
| 에피소드 | 최대 10초, 500 policy steps |

물체를 매번 새로 생성하지 않고 고정 풀을 재배치한다. 설정에 남은 Gray/White 용량 메타데이터를 실제 장애물 수로 해석하면 안 된다. 이 두 환경의 fast layout은 **GRAY 없이 RED 금지 영역과 WHITE 배치 영역**을 사용한다.

### 프레임과 센서

- `ee_frame`: AXIA80 링크에 고정된 EEF 기준점. 링크 기준 z offset은 `0.13 + sensor_height/2`이며 sensor height 0.0254m에서 0.1427m다. 손가락 굽힘에 따라 이동하는 손끝이 아니다.
- `finger_frame`, `wrist_frame`: 선반 근접/충돌 비용과 종료 조건용 보조 프레임이다. EEF 12cm 보상 게이트와 손목 3cm 실패 조건은 서로 다른 판정이다.
- `hand_tactile`: 손바닥·손등의 접촉 영역을 정책의 17개 촉각 상태로 변환한다. 접촉 판정 기준은 0.05N이다.
- `whole_hand_contact`와 물체별 hand-filter 센서: 타겟/장애물 접촉의 식별과 보상 계산에 사용한다. 모든 접촉 정보가 정책 관측으로 전달되는 것은 아니다.
- 손목 F/T: 손의 모델·운동학을 사용하는 보상된 외력 측정이다. EEF 원점·축에서 힘과 모멘트를 표현한다. 타겟 GT나 접촉 물체의 정체를 이용해 관측을 계산하지 않는다.

## 3. 랜덤화 대상과 적용 시점

### 생성·startup 시 정해지고 reset 간 유지되는 항목

| 대상 | 분포/설정 | 유지 범위 |
| --- | --- | --- |
| 물체 종류 | 타겟 cylinder 고정, 장애물 8종×2 슬롯 고정 | 환경 생존 기간 |
| 물체 크기 | 각 기본 형상에 단일 등방성 배율 U(0.9, 1.1) | 생성 후 고정. reset에서 크기를 재추출하지 않음 |
| 물체 질량 | 물체별 U(0.230, 0.500)kg × 1.5 = U(0.345, 0.750)kg | startup 후 고정 |
| 물체 관성 | 해당 형상의 기준 관성에 새 질량/기준 질량 비율 적용 | startup 후 고정 |
| 선반 접촉면 마찰 | 정지 0.213~0.417, 동마찰 0.170~0.334 | 환경별 startup 추출 |
| 물체 마찰 | 정지 0.235~0.395, 동마찰 0.188~0.316 | 물체별 startup 추출 |
| 손 마찰 | 정지 0.295~0.875, 동마찰 0.236~0.700 | 환경별 startup 추출 |

마찰은 위 범위를 표현하는 역할별 4,096개 유한 uniform bucket에서 추출한다. Gaussian 질량/마찰 sampler나 `randomize_reset_physics`가 소스에 존재하더라도, 이 두 환경의 Event는 **startup `initialize_physics`**를 사용한다. 크기 반영 BBOX·바닥 정렬 높이·외접원·배치 셀은 prestartup에 캐시한다.

### 매 에피소드 reset에서 다시 정하는 항목

| 대상 | 방법과 범위 |
| --- | --- |
| 타겟 시작 XY | 선반 중앙 반경 2cm 원판 내 균등 배치 |
| 타겟 자세/높이 | yaw −90도 고정. 스케일 반영 바닥이 선반 표면에 맞도록 root z 설정 |
| 목표 방향 | 선반 로컬 ±X 주변의 제외 각도를 뺀 방향에서 추출. 초기 제외 반각은 각각 30도 |
| 목표 거리 | 6~12cm. 해당 방향에서 물체가 선반 가장자리 여유 2cm를 지키는 최대 거리로 상한 제한 |
| 장애물 수 | 정수 0~6 균등 추출 |
| 활성 장애물 정체 | 16개 풀의 무작위 순열에서 필요한 개수 선택. 종류·크기 자체는 재추출하지 않음 |
| 장애물 XY | 유효한 WHITE 셀에서 선택하고 셀 내부 jitter 적용. 셀 크기 5mm |
| 장애물 yaw | U(−π, π). BBOX 중심 offset을 회전시켜 root 위치 보정 |
| 장애물 z | 각 물체의 바닥 정렬 높이 사용 |
| 로봇 초기 EEF | 선반 로봇 쪽 앞 경계 밖 8~10cm, 타겟 좌우 offset 10~18cm, 기본 높이 offset +1cm와 ±2cm jitter |
| 팔 초기 관절 | 위 EEF 위치와 기본 자세를 만족하도록 Warp IK 계산. 허용 오차를 통과하지 못하면 reset 오류 |
| 손 초기 관절 | 펼친 0rad 상태. 손 current/previous 액션 이력도 0으로 초기화 |
| 초기 타겟 관측 오차 | root 좌표 각 축 U(−1cm, +1cm), reset마다 1회 추출 후 고정 |
| 초기 장애물 관측 오차 | 좌표 각 축 U(−1cm, +1cm), reset 스냅샷에 적용 |
| 장애물 가시성 | 초기 기하 가시성 threshold 0.35, 가시성 bit 1% 반전. 비활성 물체는 반전 후에도 제외 |
| 장애물 슬롯 순서 | 관측 packing의 정렬 후 10% 확률 인접 교환 |

선반 로컬 +X는 로봇 쪽 Pull, −X는 Push 방향이다. 목표 방향 제외 반각은 커리큘럼에 따라 줄어들며, 거리 분포는 계속 6~12cm 계열을 유지한다.

### 배치와 reset 순서

1. 타겟 시작점과 목표를 선택한다.
2. 타겟의 외접원 이동 경로를 로봇 쪽 선반 앞 경계까지 연장한 RED 금지 영역을 만든다.
3. 타겟/장애물 외접원에 1cm 여유를 더한 영역을 이용해 경계·RED·이미 배치된 장애물과 겹치지 않는 WHITE 위치를 선택한다. 유효 배치를 만들지 못하면 오류를 내며 요청 개수를 조용히 줄이지 않는다.
4. 타겟과 이동 방향을 기준으로 EEF 초기 위치를 추출하고 Warp IK를 계산한다.
5. 선택된 환경의 선반·로봇·물체 최종 상태를 기록한다. 활성 마스크, 중력 설정, 목표 이동 벡터를 갱신한다.
6. 초기 시각 스냅샷을 만들고 보상 이력·접촉 카운트·통계를 초기화한다. reset 직후 센서는 신선한 물리 측정이 생기기 전까지 무효로 취급한다.

목표 명령 `target_goal_pos`는 reset에서 정해진 에피소드 목표를 유지한다. 명령 재표본 간격은 1,000,000초로, 정상 10초 에피소드 중 목표를 임의 재추출하지 않는다. 실제 물체는 이후 물리에 따라 움직이지만 시각 위치 스냅샷은 고정된다.

## 4. 관측: 두 환경 모두 동일한 130D

Actor와 Critic 모두 `policy` 66D + `obstacles` 64D를 받는다. 별도의 현재 물체 GT를 받는 Critic 그룹은 없다. 다음 표는 policy 그룹의 연결 순서다.

| term | 차원 | 의미·단위·좌표계 | 갱신/오차 |
| --- | ---: | --- | --- |
| `joint_pos` | 6 | 실제 팔 관절 위치, rad | 매 step, 별도 관측 noise 없음 |
| `joint_vel` | 6 | 실제 팔 관절 속도, rad/s | 매 step, 별도 관측 noise 없음 |
| `hand_configuration` | 6 | 독립 구동 손 관절 위치, rad | 매 step. openness 2D 압축·정규화 없음 |
| `ee_pose` | 7 | robot root 기준 EEF 위치 3(m) + quaternion 4 | 매 step |
| `target_obs_state` | 3 | 초기 타겟 root 위치 추정, 현재 EEF 기준(m) | 초기 위치+고정 ±1cm bias를 현재 프레임으로만 변환 |
| `goal_pos` | 3 | 고정 목표 위치, 현재 EEF 기준(m) | EEF가 움직이면 좌표 표현만 변함 |
| `actions` | 12 | 직전 실행에 사용된 Runner Clip 후·scale 전 raw 명령 | 그대로 입력. tanh·추가 관측 Clip 없음 |
| `tactile` | 17 | 대응 palm/dorsal 영역의 접촉 상태 | 매 step. 두 측면 bit에 각각 1% 반전 noise |
| `wrist_wrench` | 6 | EEF 기준 외력 3(N) + 모멘트 3(N·m) | 매 step. 아래 Gaussian noise와 관측 Clip |
| **policy 합계** | **66** | 위 순서로 concatenate | Actor/Critic 공통 |
| `obstacles / initial_positions` | **64** | 16슬롯 × (가시성 1 + 초기 위치 3) | 초기 스냅샷을 현재 EEF로 변환. 비가시 슬롯 전체 0 |

촉각 상태는 무접촉 0, palm만 1, dorsal만 −1, 양쪽 2다. 손목 관측 noise 표준편차는 힘 0.05N, 모멘트 0.005N·m다. **현재 runtime은 noise 적용 후 힘 각 축 ±150N, 모멘트 각 축 ±8N·m로 관측을 Clip한다.** 센서 원자료와 보상이 직접 읽는 F/T를 같은 범위로 잘라 버리는 처리는 아니다.

초기 물체 관측이 EEF 이동에 따라 변하는 것은 실시간 물체 위치 갱신을 뜻하지 않는다. 장애물이 실제로 이동해도 초기 위치 추정은 따라가지 않는다. 따라서 정책은 촉각·F/T와 자신의 움직임으로 상호작용 상태를 추론해야 한다. 보상은 이 제한과 별도로 현재 GT를 사용한다.

모델은 장애물 64D를 16D embedding으로 압축하고 policy 66D와 결합해 82D를 MLP에 입력한다. 장애물 encoder hidden은 32, 활성화 ReLU, 본체 hidden은 256/128/64, 활성화 ELU다. Actor 출력은 12D, Critic 출력은 scalar이며 observation normalization은 꺼져 있다.

## 5. 액션·제어와 Last Action

공통 처리 순서는 `Gaussian sample → RslRlVecEnvWrapper의 ±π/2 Clip → ActionManager → 팔 scale/손 관절 목표 처리 → 물리 제어`다. Runner 설정 키는 `clip_actions`이며, 표준 `train.py`/`play.py`의 wrapper가 이를 적용한다. wrapper 없이 환경을 직접 호출하면 이 Runner Clip 경로도 직접 연결해야 한다.

| 채널 | manager 입력 범위 | 제어 의미 |
| --- | --- | --- |
| 팔 병진 3축 | 각 축 ±π/2 | EEF 기준 상대 pose, scale 0.03m → 각 축 최대 약 ±4.71cm |
| 팔 회전 3축 | 각 축 ±π/2 | scale 0.15rad → Euler 증분 각 축 ±0.235619rad(13.5도), 이후 quaternion/axis-angle 변환 |
| 손 6축 | 각 축 ±π/2 | 독립 구동 관절의 절대 rad 목표. 아래 URDF 범위로 최종 제한 |

| 손 채널 순서 | drive 관절 suffix | 실제 목표 범위(rad) |
| --- | --- | --- |
| 0 | `thumb_2_joint` | 0~0.5864 |
| 1 | `index_1_joint` | 0~1.4381 |
| 2 | `middle_1_joint` | 0~1.4381 |
| 3 | `ring_1_joint` | 0~1.4381 |
| 4 | `little_1_joint` | 0~1.4381 |
| 5 | `thumb_1_joint` | 0~1.1641 |

손의 URDF 한계와 mimic mapping은 기존 구동 처리다. Last Action은 이 최종 손 관절 목표가 아니라 **manager가 받은 12D raw 값**이다. 예를 들어 손 명령 −1은 Last Action에 −1로 남지만 실제 목표는 0rad가 된다. PPO는 원본 Gaussian sample/log probability를 사용하며, 실행 Clip이 정책 분포 자체를 bounded 분포로 바꾸지는 않는다.

팔 OSC는 fixed impedance, 중력 보상·관성 decoupling 활성, nullspace 제어 없음이다. stiffness는 병진 100/100/100, 회전 50/50/50, damping ratio는 모두 1이다. 물리 effort limit은 팔 앞 3축 150N·m, 뒤 3축 28N·m이며 속도 limit은 3.14rad/s다. 손 effort limit은 10N·m, 속도 limit은 1rad/s다. **팔 1rad/s 실패 종료는 물리 속도 제한과 별도의 판정**이다.

## 6. 보상 공통 규칙과 전체 목록

RewardManager는 각 함수 원점수에 `weight × step_dt`를 곱해 합산한다. 아래 `step_dt=0.02초`다. 접근량·멀어짐 등 함수가 이미 `1/step_dt`를 포함하는 항은 dt가 상쇄된다. 표의 weight만 비교하면 서로 다른 단위를 혼동할 수 있다.

| term | Prof-v2 weight | ForceDirection-v0 weight | 원점수/조건 |
| --- | ---: | ---: | --- |
| `reaching` | 30 | 30 | 현재 타겟 BBOX 중심과 EEF 사이 3D 근접도. 아래 수식 |
| `goal_distance` | 120 | 100 | Prof: 접촉 조건부 step 접근량. Finger: 최고 접근 기록 개선량 |
| `direction_deviation` | −6 | 없음 | 초기 지시 방향에서 벗어난 step 변위. Prof 접촉 조건 적용 |
| `hand_contact` | 없음 | 0.1 | 접촉 유지 count 0~20. 목표 1cm 미만 예외 |
| `force_direction` | 없음 | 0.33 | 현재 목표 방향과 3D 타겟 접촉 합력의 signed cosine |
| `arm_action_rate` | −0.03 | −0.03 | 팔 6축의 current−previous raw action 제곱합. 상한 없음 |
| `hand_action_rate` | −0.03 | −0.03 | 손 6축의 같은 제곱합. 상한 없음 |
| `arm_joint_velocity` | −0.03 | −0.03 | 팔 6관절 속도 제곱합, 원점수 최대 100 |
| `hand_joint_velocity` | −0.01 | −0.01 | mimic 포함 손 12관절 속도 제곱합, 원점수 최대 100 |
| `shelf_collision` | −0.5 | −0.5 | 선반 움직임과 EEF 근접 시 finger/wrist 보조 프레임의 선반 표면 근접 비용 |
| `shelf_failure` | −3 | −3 | 선반 속도·손목 높이 실패 predicate/step_dt. 발생 step 지급량 −3 |
| `obstacle_contact` | 초기 0 | 초기 0 | 비타겟 장애물이 손에 가하는 합력의 free_force 초과 지수 비용, 원점수 최대 100 |
| `wrench_change` | 초기 0 | 초기 0 | 연속 F/T 크기 변화 비용. 무비용 범위·weight 커리큘럼 및 기존 예산 제한 |
| `object_tilt` | −30 | −30 | 활성 물체별 `clip((angle−5도)/(0.9rad−5도),0,1)²` 합 |
| `obstacle_displacement` | −150 | −150 | 활성 비타겟 물체의 초기 대비 3D 변위 제곱합, 최대 0.04 |
| `target_inverse_distance` | −25.94 | −25.94 | 직전 step보다 증가한 타겟–목표 XY 거리/step_dt |

`goal_hold`, 별도 `object` 통합 비용, `pushing_speed`, `eef_linear_speed`, `eef_orientation`, `object_acceleration`은 비활성이다. 별도의 목표 도달 보너스나 성공 즉시 종료 보상도 없다. action-rate 상한 제거는 **모든 비용의 기존 상한을 없앴다는 뜻이 아니다**. 위 관절 속도·기울기·변위·wrench 비용의 기존 제한은 남아 있다.

### 공통 Reaching과 멀어짐 비용

EEF와 현재 타겟 BBOX 중심의 3D 거리를 D, reset 때 EEF와 타겟 root 거리에서 10cm를 뺀 양수 부분을 B라고 한다. 실제 한 스텝 지급량은 다음과 같다.

```math
B = \max(D_{\mathrm{root},0}-0.10, 0),\qquad
R_{\mathrm{reach},t}=30\,\Delta t\,\frac{B}{10}\,
\frac{0.10}{0.10+\max(D_t-0.10,0)}.
```

현재 BBOX 중심에서 10cm 이내면 근접도 계수는 1이다. 접촉·높이·최고 기록 조건이 없어 근처에 머무르면 지속 보상을 받는다. 분자 B는 초기 보상 규모를 맞추는 값으로, 현재 거리가 바뀌어도 고정이다.

타겟 root와 목표의 XY 거리를 d라고 하면 멀어짐 비용은 `−25.94 × max(d_t−d_(t−1), 0)`이다. 함수 이름 `RelativeInverseDistance`와 달리 거리의 역수가 아니다. 실제 접촉 여부와 무관하게 계산한다.

### 공통 wrench 변화 비용

`abs(||F_t||−||F_(t−1)||)`와 `abs(||M_t||−||M_(t−1)||)`를 사용한다. 방향만 바뀌고 크기가 같으면 이 항의 변화 비용은 0이다. 무비용 범위를 넘은 힘/모멘트 변화 중 큰 severity를 지수 함수(sharpness 3)로 변환하고, 각 무비용 범위의 2.5배에서 포화하며 원점수는 최대 1이다.

두 환경 모두 `max_positive_fraction=0.05`가 유지된다. 에피소드의 양의 weight 항 누적 보상을 바탕으로 기존 5% 비용 예산을 적용한다. ForceDirection-v0는 이 계산 전에 힘 방향 항을 평가하도록 배치되어 있다. signed cosine이라 양의 weight라도 개별 step 값은 음수가 될 수 있다. 보상은 관측 noise/Clip 이후 텐서가 아니라 관측 callable의 원래 보상된 F/T 측정을 직접 읽는다.

## 7. Prof-v2의 핵심 보상

현재 타겟 접촉 센서의 hand-filter별 법선력 **크기를 합산**한 값이 0.01N 이상이고 데이터가 신선하며, 현재 EEF가 초기 선반 표면보다 12cm 미만 높이에 있어야 접촉 조건 C=1이다. 여러 접촉의 방향이 반대여도 크기 합산이므로 상쇄되지 않는다. **2-of-3 이력은 사용하지 않고 현재 step을 판정한다.**

```math
R_{\mathrm{goal},t}=120\,C_t\,\max(d_{t-1}-d_t,0),
\qquad
R_{\mathrm{direction},t}=-6\,C_t\left(\|\Delta\mathbf{p}_t\|-\hat{\mathbf{s}}\cdot\Delta\mathbf{p}_t\right).
```

여기서 p는 현재 타겟 root XY, s는 **reset 때의 타겟→목표 방향**이다. 정방향 이동의 방향 비용은 0, 직각 이동은 이동 거리만큼, 역방향 이동은 이동 거리의 2배에 weight −6을 곱한다. 이 항은 힘 방향 보상이 아니다.

접촉이 없어도 내부 previous position을 매 step 갱신하므로 비접촉 이동을 나중에 소급 보상하지 않는다. 그러나 **에피소드 최고 기록을 보상하는 구조도 아니다**. 멀어졌다가 다시 가까워지면 재접근량을 보상할 수 있다. 현재 v2는 이 접근식을 유지하면서 Runner Clip·팔 속도 종료를 적용한 버전이며, 왕복 보상의 구조 자체를 제거한 버전으로 설명하면 안 된다.

예를 들어 접촉 조건을 만족하며 1cm 접근한 한 step은 목표 접근 +1.2를 받는다. 반대로 1cm 멀어진 step의 공통 멀어짐 비용은 −0.2594이며 초기 방향과의 관계에 따라 방향 비용도 더해진다. 실제 총보상에는 나머지 항이 모두 포함된다.

## 8. Finger-ForceDirection-v0의 핵심 보상

### 최고 기록 기반 목표 접근

초기 XY 거리 d0를 기준으로 지금까지 가장 많이 접근한 양을 b로 유지한다.

```math
b_t=\max\left(b_{t-1},\max(d_0-d_t,0)\right),\qquad
R_{\mathrm{goal},t}=100(b_t-b_{t-1}).
```

접촉·EEF 높이 조건 없이 현재 GT로 계산한다. 허용 거리 tolerance는 0이므로 목표 중심까지 기록을 개선할 수 있다. 이전 최단 거리까지 돌아오는 이동에는 추가 지급이 없다. 새 기록을 1cm 개선하면 +1이다. 이 환경은 Semi-Prof의 로그 거리식이나 접촉 조건부 거리식을 사용하지 않는다.

### 접촉 유지: 1cm 예외와 12cm 높이

목표 XY 거리 **1cm 이상**에서는 다음 규칙을 사용한다.

1. 타겟–손 접촉 합력 크기 ≥0.01N, 신선하고 유한한 데이터, EEF 높이 <12cm를 모두 만족한 sample을 접촉으로 기록한다.
2. 최근 3회 중 2회 이상이 위 접촉 sample이고 현재 높이도 유효하면 인정한다.
3. 인정 step은 count를 1 증가시키고, 불인정 step은 2 감소시킨다. count 범위는 0~20이다.
4. 인정 step에만 count를 원점수로 반환한다. 불인정 step 지급량은 0이다.

**목표 XY 거리 <1cm에서는 실제 접촉·센서·높이에 무관하게 count와 원점수를 20으로 만든다.** 이 예외가 실제 접촉 이력을 인위적으로 채우지는 않는다. 최대 step 지급량은 `0.1 × 20 × 0.02 = 0.04`다. 1cm 이상으로 나가면 일반 접촉 조건으로 복귀한다.

### 힘 방향: signed cosine

이 항은 손목 F/T가 아니라 **손이 타겟에 가하는 물체 측 법선력+마찰력**을 사용한다. 각 policy step의 두 physics substep에서 힘을 수집해 평균 합력을 만든다. 목표 방향은 매 step의 **현재 타겟 위치→목표 위치**이며 초기 방향에 고정되지 않는다.

초기 선반 좌표계로 변환한 평균 3D 합력을 F, 현재 타겟→목표의 평면 벡터를 g=(gx,gy,0)라고 한다. 유효 판정 V는 해당 policy 구간의 실제 접촉, 신선하고 유한한 수집 결과, 평균 수평 합력 크기 ≥1N을 요구한다.

```math
r_{\mathrm{force},t}=
\begin{cases}
0, & V_t=0,\\
1, & V_t=1\ \text{and}\ \|\mathbf{g}_t\|<0.01,\\
\dfrac{\mathbf{F}_t\cdot\mathbf{g}_t}{\|\mathbf{F}_t\|\,\|\mathbf{g}_t\|}, & \text{otherwise},
\end{cases}
\qquad
R_{\mathrm{force},t}=0.33\,\Delta t\,r_{\mathrm{force},t}.
```

| 힘과 목표 방향의 각도 | 원점수 | 한 step 지급량 |
| --- | ---: | ---: |
| 0도 | +1 | +0.0066 |
| 45도 | 약 +0.7071 | 약 +0.00467 |
| 90도 | 0 | 0 |
| 135도 | 약 −0.7071 | 약 −0.00467 |
| 180도 | −1 | −0.0066 |

표는 1cm 밖에서 유효 조건을 만족하는 경우다. 분모는 수평 힘이 아닌 **3D 힘의 크기**이므로 수직 성분이 커지면 정방향 점수가 약해진다. 순수 수직 힘은 수평 1N 조건을 통과하지 못해 0이다. 실제 접촉은 수집 구간 내 타겟–손 법선력 크기 합 ≥0.01N으로 확인한다.

1cm 내부에서는 각도만 무시하고 원점수 1을 준다. 실제 접촉·유효 수평 힘 조건은 여전히 필요하므로, 접촉 유지 보상의 무조건 인정과는 다르다. 힘 방향 항에는 **EEF 높이·속도·진행량 조건이 없다**. 목표를 지나치면 목표 벡터가 바뀌며, 다시 1cm 밖으로 나가면 즉시 코사인 계산으로 복귀한다.

## 9. 높이·반경·종료 판정의 구분

12cm는 월드 z=0.12m를 뜻하지 않는다. 실제 보상 높이 조건은 `eef_world_z < initial_shelf_root_world_z + 1.05 + 0.12`다. 경계와 정확히 같은 높이는 인정하지 않는다. EnvCfg의 일반 `goal_reward_height_limit/contact_height_limit=0.14`가 남아 있지만 여기 설명한 활성 보상은 명시적인 `eef_height_limit=0.12`를 사용한다.

| 판정 | Prof-v2 | ForceDirection-v0 |
| --- | --- | --- |
| 12cm 게이트 | 목표 접근·방향 이탈 비용 | 1cm 밖의 접촉 유지 |
| 높이 게이트 없는 주요 항 | Reaching·멀어짐 비용 | Reaching·최고 기록 접근·힘 방향·멀어짐 비용 |
| 1cm 내부 예외 | 없음 | 접촉 유지 무조건 최대값, 유효 힘의 방향 점수 1 |
| 성공 종료 | timeout에서 XY <3cm, 동시 실패 없음 | 동일 |
| 목표 내부 비율 metric | XY ≤3cm | 동일 |

목표에 들어가도 즉시 에피소드가 끝나지 않는다. 1cm는 ForceDirection 보상의 예외 반경이고, 성공 평가 반경은 계속 3cm다. 정확히 1cm에서는 일반 보상 조건을 사용한다. 현재 구현은 성공에 `<3cm`, 내부 비율 metric에 `≤3cm`를 사용하므로 경계 연산자 차이도 유지해서 해석해야 한다.

| termination | 조건 |
| --- | --- |
| `arm_joint_velocity` | 팔 6축 중 절댓값 속도 >1.0rad/s. 정확히 1.0은 허용, 임계값 커리큘럼 없음 |
| `object_fall_or_tilt` | 활성 물체 바닥이 선반보다 1cm 넘게 낮음, 기울기 ≥0.9rad, 또는 비유한 바닥 높이 |
| `shelf_failure` | 선반 root 선형/각속도 6D norm >0.1, 손목 높이 <3cm, 또는 선반 위치 변위 >5cm |
| `timeout` | 10초 도달. time-limit truncation |
| `success` | timeout이면서 목표 XY <3cm이고 위 실패 항목이 모두 거짓. 성공 진단용 truncation |

`shelf_failure` 보상 함수는 선반 변위 종료 조건 전체와 동일하지 않다. 종료 순간 추가 성공 보너스도 없다. 평가에는 최종/최소/평균 XY 거리, EEF·타겟 속력 평균/최대, 목표 내부 시간 비율, 최근 완료 에피소드 창의 timeout 성공률 등을 기록한다.

## 10. 커리큘럼과 PPO

아래 일정은 두 환경에 공통이다. 보상 schedule은 제어점 사이를 보간하며 250 iteration 간격으로 반영한다. 팔 속도 종료 임계값과 12cm 높이에는 curriculum을 적용하지 않는다.

| 변경 대상 | iteration: 값 |
| --- | --- |
| 힘 크기 변화 무비용 범위(N) | 0:50, 3000:50, 6000:30, 10000:30, 12000:20 |
| 모멘트 크기 변화 무비용 범위(N·m) | 0:5, 3000:5, 6000:3, 10000:3, 12000:2 |
| 장애물 접촉 무비용 범위(N) | 0:80, 3000:80, 6000:50, 10000:50, 12000:30 |
| `wrench_change` weight | 0:0, 1000:0, 3000:−0.03, 6000:−0.1 |
| `obstacle_contact` weight | 0:0, 1000:0, 3000:−0.02, 6000:−0.05, 10000:−0.05, 12000:−0.1 |
| 목표 방향 제외 반각 | 0~9999:30도, 10000:25도, 이후 3000 iteration마다 5도 감소, 25000부터 0도 |

PPO 기본값은 rollout 36 steps/env, 최대 90,000 iterations, 저장 간격 50이다. 일반 Gaussian 초기 표준편차 1.0, gamma 0.98, GAE lambda 0.95, learning rate 0.001/adaptive, desired KL 0.02, epochs 8, minibatches 4, clip parameter 0.2, entropy coefficient 0.005, value loss coefficient 1, max gradient norm 1이다. Finger-v1의 축별 초기 표준편차 설정과 혼동하지 않는다.

## 11. 코드 근거와 검증 범위

아래 경로는 활성 패키지 기준이며, 공통 helper를 재사용하는 경우 실제 호출되는 함수까지 대조했다.

| 주제 | 실제 코드 |
| --- | --- |
| EnvCfg·상속 | [envs/sweep_simple_envs.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_simple_envs.py) |
| reset/step·관측 Clip·힘 수집 연결 | [runtime/sweep_simple.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/sweep_simple.py) |
| Scene·고정 물체 풀 | [assets/scenes/sweep_simple.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/sweep_simple.py) |
| Event 구성 | [mdp/events/sweep_simple.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/events/sweep_simple.py) |
| fast reset·Warp IK 연결 | [mdp/event_functions/wrench_refactor_relative_ik_test.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/wrench_refactor_relative_ik_test.py) |
| startup 물성 | [mdp/event_functions/wrench_refactor.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/wrench_refactor.py) |
| 원형 배치 | [mdp/common/wrench_refactor_layout.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/wrench_refactor_layout.py) |
| 관측 term | [mdp/observations/sweep_simple.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/sweep_simple.py) |
| 초기 위치·촉각 관측 | [mdp/observation_functions/wrench_refactor.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/wrench_refactor.py) |
| 전체 보상 설정 | [mdp/rewards/sweep_simple.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/sweep_simple.py) |
| 접촉 예외·cosine | [mdp/reward_functions/sweep_simple.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/sweep_simple.py) |
| Prof 접근·방향·Reaching | [mdp/reward_functions/wrench_refactor_relative_ik_test.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/wrench_refactor_relative_ik_test.py) |
| 물리 substep 힘 집계 | [mdp/common/sweep_simple_force.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/sweep_simple_force.py) |
| PPO·모델·Runner Clip | [agent/sweep_simple_ppo_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/sweep_simple_ppo_cfg.py) |

문서 작성 작업에서는 실행 코드를 변경하거나 추가 학습을 실행하지 않았다. 기존 [Prof-v2 검증](../logs/2026-11-13_sweep_simple_prof_v2.md)과 [12cm·cosine 검증](../logs/2026-11-13_simple_height_cosine.md)의 CPU 및 짧은 GPU smoke 결과를 참고했다. 이는 장기 수렴·왕복 행동 제거·정확도 향상을 보증하는 결과가 아니다. 2026-11-13의 머신별 학습 진행 보고는 해당 날짜의 이력이며, 이 문서에서 현재 프로세스 상태를 재확인한 것은 아니다.
