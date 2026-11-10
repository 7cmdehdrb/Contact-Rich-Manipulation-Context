# Sweep Simple 환경 계열

2026-11-10 기준 실제 코드에 근거한 환경 설명서. 베이스 전체 구성과 파생 환경의 변경·실험 의도를 함께 정리한다. 기존 실험 환경에서 상속을 분리한 계열이며, 실제 코드의 후속 변경도 반영한다. [환경 안내](../08_ACTIVE_ENVIRONMENTS.md) · [개발·검증 기록](../logs/2026-11-10_sweep_simple_family.md).

2026-11-10 후속 변경: **Simple-v0·Simple-v1·Simple-Hard-v0는 타겟 root와 목표의 XY 거리가3cm 미만이면 접촉 유지 count/reward를 즉시20으로 인정한다.** 접촉·이력·EEF 높이 조건을 우회한다. Prof 계열은 접촉 유지 보상이 없어 영향이 없다. 따라서 Simple-v0/v1은 이제 과거 v0_2_2_4/6와 이 한 가지 차이가 있다. [변경 기록](../logs/2026-11-10_simple_goal_full_contact.md).

## 등록과 상속

```text
ManagerBasedRLEnvCfg
└── SweepSimpleEnvCfg                         Inspire-Sweep-Simple-v0
    ├── SweepSimpleProfEnvCfg                 Inspire-Sweep-Simple-Prof-v0
    │   └── SweepSimpleProfV1EnvCfg           Inspire-Sweep-Simple-Prof-v1
    │       └── SweepSimpleProfHardEnvCfg     Inspire-Sweep-Simple-Prof-Hard-v0
    └── SweepSimpleV1EnvCfg                   Inspire-Sweep-Simple-v1
        └── SweepSimpleHardEnvCfg             Inspire-Sweep-Simple-Hard-v0
```

| 새 task ID | 동작 기준 | 직접 부모와 차이 | PPO experiment_name |
| --- | --- | --- | --- |
| `Inspire-Sweep-Simple-v0` | Relative-IK `v0_2_2_4` | 과거 환경 상속 없는 독립 기준 | `inspire_sweep_simple_v0` |
| `Inspire-Sweep-Simple-Prof-v0` | Relative-IK `v0_2_2_5` | Goal Distance·방향 이탈·접촉 유지 보상 | `inspire_sweep_simple_prof_v0` |
| `Inspire-Sweep-Simple-v1` | Relative-IK `v0_2_2_6` | Reach만 변경 | `inspire_sweep_simple_v1` |
| `Inspire-Sweep-Simple-Prof-v1` | Prof-v0 + `v0_2_2_6` Reach | Prof-v0에서 Reach만 변경 | `inspire_sweep_simple_prof_v1` |
| `Inspire-Sweep-Simple-Hard-v0` | Simple-v1 | 목표 거리 확대·DeadZone 삭제 | `inspire_sweep_simple_hard_v0` |
| `Inspire-Sweep-Simple-Prof-Hard-v0` | Simple-Prof-v1 | 동일한 목표 샘플링 변경 | `inspire_sweep_simple_prof_hard_v0` |

공통 런타임 `SweepSimpleEnv`는 `ManagerBasedRLEnv`를 직접 상속한다. EnvCfg·SceneCfg·Manager Cfg·PPO도 과거 테스트 Cfg를 상속하거나 인스턴스화하지 않는다. 보상/종료/리셋 함수, Warp IK, OSC 구현, 자산 스포너, 정책 모델 구현은 그대로 공유한다. 따라서 독립성의 범위는 **환경 구성과 런타임의 과거 상속 제거**이며, 모든 연산 함수와 자산을 복제한 계열은 아니다.

## 베이스 환경: Inspire-Sweep-Simple-v0

목표는 선반 위 타겟을 손으로 밀어 지정된 XY 목표점에 가까이 옮기면서, 선반·장애물에 과도한 영향을 주지 않는 정책을 학습하는 것이다. 초기 물체 배치 관측 이후에는 로봇 상태·촉각·손목 F/T를 활용한다. 아래 내용은 베이스의 전체 구성이고, 파생 환경에서 명시적으로 바뀌는 항목은 뒤 비교표에 정리했다.

### 환경 구성과 시뮬레이션

| 구성 | 설정과 역할 |
| --- | --- |
| 환경 구조 | Isaac Lab Manager-based RL. EnvCfg가 Scene·Observation·Action·Command·Event·Reward·Termination·Curriculum을 조합하고, 별도 runtime이 reset/step과 통계를 관리 |
| 로봇 | UR5e 6축 팔 + Inspire 오른손 12관절 + Axia80 손목 F/T. 팔은 OSC 토크 제어, 손은 위치 목표 제어 |
| 선반·배경 | 40×100cm 선반 표면, 표면 높이1.05m. 선반 질량30kg, 초기 위치(−0.7,0,0). 지면과 조명 포함 |
| 물체 구성 | 타겟 cylinder1개 + 장애물16개를 생성해 고정 유지. 장애물8종을2개씩 보유: cylinder, cube, mug, bottle, cracker box, sugar box, tomato soup can, master chef can |
| 활성 물체 | 타겟은 슬롯0 고정. 에피소드마다 장애물0–6개 균등 추첨 후 활성화. 나머지는 선반 밖 높은 위치에 격리 |
| 병렬 실행 | 기본2,048환경, 간격2.5m, `replicate_physics=False` |
| 시간 | physics dt0.01초(100Hz), decimation2, policy dt0.02초(50Hz). 에피소드 최대10초=500 policy steps |
| 물리 설정 | 마찰 재질을 로봇·선반·물체 스포너에 전달. PhysX 접촉 버퍼 용량, bounce threshold0.2, friction correlation distance0.00625 설정 |
| 제어 프레임 | `ee_frame`은 손목 센서 링크에 고정된 EEF. 별도로 finger/wrist frame을 두어 선반 근접도를 평가 |
| 시각화 | 목표와 EEF 프레임 표시 설정 포함. IK 초기화 박스 기본 OFF. 스폰 영역은 play에서만 ON(기본 최대4환경), train에서는 영상 촬영 시에도 OFF |

### 초기화·랜덤화·리셋

| 시점/항목 | 동작 |
| --- | --- |
| 최초 자산 생성 | 물체 스케일을0.9–1.1 균등 추출. 각 슬롯의 종류·크기는 이후 reset에서 유지 |
| prestartup | 스케일 반영 BBOX·바닥 정렬 높이·외접원·배치 셀 등 불변 기하를 캐시 |
| startup 물성 | 물체별 질량0.345–0.750kg 균등 추출(원래0.230–0.500kg에1.5배), 관성 비례 조정. 선반 접촉면·물체·손의 마찰은 역할별 범위에서 추출. 물성은 reset마다 다시 뽑지 않음 |
| 타겟 시작점 | 선반 중앙의 반경2cm 원판 안에서 균등 배치, yaw −90도, 물체 바닥이 선반에 맞도록 높이 설정 |
| 목표 거리 |6–12cm. 선택한 방향에서 물체가 선반 가장자리2cm 여유를 지키는 최대 거리까지 상한을 제한한 후 범위 내 균등 추출 |
| 목표 방향 | 선반 로컬 +X는 로봇 쪽 Pull, −X는 Push. 초기에는 ±X 주변 각30도 반각의 DeadZone을 제외하고 나머지 각도에서 균등 추출. 이후 curriculum으로 축소 |
| RED 금지 구역 | 타겟의 외접원 이동 궤적을 선반의 로봇 쪽 앞 경계까지 연장한 영역. 장애물이 밀기 경로를 막지 않도록 제외 |
| WHITE 배치 구역 | 나머지 선반 영역. 물체 외접원 반지름에1cm를 더한 영역끼리 겹치지 않도록 배치.5mm 안전 셀 사용. GRAY 없음 |
| 로봇 초기 자세 | 타겟·이동 방향으로 초기 EEF 위치를 결정. 선반 앞 경계 바깥8–10cm, 타겟 좌우10–18cm 범위와 높이 jitter 사용. Warp IK로 팔 관절 자세 계산 |
| reset 적용 | 새로운 목표와 배치·IK를 계산한 뒤 선택된 환경의 최종 상태 기록. 손은 펼친 자세로 초기화. 보상 이력·접촉 카운트·에피소드 통계·초기 물체 관측 스냅샷 갱신 |
| 난수 | 배치·IK·startup 물성의 난수 스트림을 분리하며 reset seed에 따른 재현성 유지 |

재배치 때 USD 자산을 다시 생성하지 않는다. 새 목표·배치를 사용하되, 고정 기하 캐시와 통합 상태 기록으로 reset 부담을 줄이는 Fast 방식이다. IK/배치 실패 시 성공한 것처럼 대체 상태를 기록하지 않는다.

### 관측과 센서

Actor와 Critic은 동일한 `policy` 58차원 + `obstacles` 64차원 그룹을 사용한다. 별도의 특권 Critic 관측은 없다(`critic=None`, `critic_obstacles=None`). 초기 물체 위치는 월드에 고정된 스냅샷을 현재 EEF 좌표계로 바꾸므로, 로봇이 움직이면 관측 좌표는 변하지만 물체의 실제 이동을 새로 관측하는 것은 아니다.

| 그룹/term | 차원 | 의미 |
| --- | ---: | --- |
| policy / `joint_pos` |6| 팔6관절 위치 |
| policy / `joint_vel` |6| 팔6관절 속도 |
| policy / `hand_configuration` |2| 손의 굽힘과 엄지 opposition 상태를0–1로 요약 |
| policy / `ee_pose` |7| 로봇 root 기준 EEF 위치3 + quaternion4 |
| policy / `target_obs_state` |3| 초기 타겟 위치를 현재 EEF 좌표계로 표현 |
| policy / `goal_pos` |3| 고정된 에피소드 목표 위치를 현재 EEF 좌표계로 표현 |
| policy / `actions` |8| 직전 액션 명령을 tanh 처리한 값 |
| policy / `tactile` |17| 손바닥·손등 대응 영역의 접촉 상태를 결합. 무접촉0, 손바닥1, 손등−1, 양쪽2 |
| policy / `wrist_wrench` |6| 손목 힘3 + 모멘트3 |
| obstacles / `initial_positions` |64|16슬롯×(가시성1 + 초기 위치3). 위치는 현재 EEF 기준, 비가시 슬롯은0 |

촉각용 손 접촉 센서, 손 전체 접촉 센서, 손 부위별 물체 필터 센서, 물체별 손 필터 센서를 구성한다. 관측의 촉각 임계값은0.05N이고, 보상의 타겟 접촉 임계값0.01N과 구분한다. 접촉 센서는 history length0이며 필요한 보상 이력은 term 내부에서 관리한다.

관측 오차도 학습 구성에 포함한다. 타겟 초기 위치는 에피소드별 좌표 편향 ±1cm, 장애물 초기 관측은1cm 위치 노이즈·가시성 기준0.35·가시성 반전 확률1%·관측 순서 교환 확률10%를 사용한다. 촉각은 원래 접촉 bit별1% 반전 후 결합한다. 손목 wrench는 힘 표준편차0.05N, 모멘트0.005Nm의 Gaussian noise를 더하고 각 축을 ±150N/±8Nm로 제한한다. 장애물 그룹은 reset에서 만든 노이즈를 유지하며 매 step 추가 corruption은 없다.

보상·종료·평가 함수는 시뮬레이터의 **현재 타겟/장애물 상태**를 읽는다. 이는 정책에 현재 물체 위치를 제공한다는 뜻이 아니다.

### 액션과 제어

| 항목 | 구성 |
| --- | --- |
| 총 액션 |8차원: 팔6 + 손2 |
| 팔 | 로봇 root 기준 상대 EEF pose 명령(병진3·회전3). 위치 scale0.03m, 회전 scale0.15rad |
| OSC | fixed impedance, 위치/회전 전 축 제어, 관성 decoupling 및 중력 보상 ON, nullspace 제어 OFF. stiffness=(100,100,100,50,50,50), damping ratio 전 축1 |
| 토크/속도 제한 | 팔 토크 앞3관절150Nm·뒤3관절28Nm, 속도 제한3.14rad/s. OSC effort limit scale1 |
| 손 | 채널0은 굽힘, 채널1은 엄지 opposition의 열림 정도.0–1로 clamp 후 open/closed 관절 자세 사이 보간,1은 펼침 |
| 손 제한 |12관절에 effort10Nm·속도1rad/s |

물리 액추에이터의 속도 제한과 뒤의 episode 종료용 관절 속도 임계값은 서로 다른 설정이다.

### 목표 명령

`target_goal_pos`는 reset에서 정한 에피소드 목표를 전달한다. command의 resampling interval은1,000,000초로 설정되어10초 에피소드 중 별도 목표 변경은 없다. 성공 반경 설정은3cm이며, 방향 기준은 초기 타겟→목표 벡터다. 목표 지점 도착만으로 조기 종료하지 않는다.

### 보상 전체 목록

아래 weight는 설정값이다. RewardManager는 일반적으로 term 출력에 weight와 policy dt를 곱한다. 단, 거리 증가분 기반 term과 `shelf_failure`는 함수 내부에서 dt를 나눠 이를 상쇄한다. 따라서 서로 다른 term의 weight 숫자만으로 실제 기여도를 비교하면 안 된다.

| 활성 term | weight | 의미와 핵심 조건 |
| --- | ---: | --- |
| `reaching` |30| 현재 EEF–타겟 root 3D 거리에서10cm를 뺀 값의 **에피소드 최솟값 개선분**. 기존 기록까지 복귀하거나 정지하면 추가 보상 없음 |
| `goal_distance` |100| 타겟–목표 XY 거리의 에피소드 최고 접근 기록 개선분. 접촉 조건 없음, tolerance0 |
| `hand_contact` |0.1| 타겟 접촉 유지 카운트. 목표 XY 거리<3cm이면 무조건20, 그 밖에서는 아래 접촉 인정 규칙 적용 |
| `arm_action_rate` |−0.03| 팔 액션 변화 비용, max_cost100 |
| `hand_action_rate` |−0.03| 손 액션 변화 비용, max_cost100 |
| `arm_joint_velocity` |−0.03| 팔 관절 속도 비용, max_cost100 |
| `hand_joint_velocity` |−0.01| 손 관절 속도 비용, max_cost100 |
| `shelf_collision` |−0.5| 선반 움직임 및 EEF가 가까울 때 가상 손가락/손목 프레임의 표면 근접 비용 |
| `shelf_failure` |−3| 선반 속도·손목 높이 실패 판정에 대한 비용. 종료의 선반 변위 조건 전체와 동일한 함수는 아님 |
| `obstacle_contact` |초기0| 장애물 접촉력 비용. free_force80N, max_cost100에서 curriculum 적용 |
| `wrench_change` |초기0| 손목 힘/모멘트 크기 변화 비용. 초기 free_force_change50N·free_moment_change5Nm, curriculum 적용 |
| `object_tilt` |−30| 활성 물체 기울기 비용. free angle5도, fail angle0.9rad |
| `obstacle_displacement` |−150| 활성 장애물 변위 비용. displacement_max_cost0.04 |
| `target_inverse_distance` |−25.94| 직전 policy step보다 목표 XY 거리가 늘어난 부분만 비용. 이름과 달리 거리의 역수 보상이 아님 |

목표 XY 거리<3cm에서는 count와 term 출력을20으로 설정한다. 접촉 없음·EEF 높이15cm 이상이어도 지급하며, 실패/성공 종료 조건 자체는 바꾸지 않는다. weight0.1과 dt0.02에서 이 term의 step 기여는0.04다. 목표 내부를 실제 접촉 이력으로 꾸미지는 않는다. 목표에서 벗어나면 저장된 count20에서 원래 접촉 인정/감쇠 규칙을 적용한다.

목표 밖의 접촉 유지에서는 타겟–손 접촉력0.01N 이상·유효 센서·EEF가 초기 선반 표면 위15cm 미만인지를 매 step 기록한다. 최근3회 중2회 이상 만족하고 현재 높이도 유효하면 인정한다. 인정 시 count+1(상한20), 불인정 시 count−2(하한0). 인정 step만 남은 count에 비례한 보상을 지급하며, 불인정 step은0이다. 따라서 현재 순간 접촉이 끊겼더라도2-of-3 이력상 인정될 수 있고, 목표 밖에서 높이15cm 이상이면 이력에 관계없이 불인정이다.

비활성 term도 명시한다: `goal_hold`(Holding), `object`(통합 물체 비용; tilt/변위로 분리), `pushing_speed`, `eef_linear_speed`, `eef_orientation`, `object_acceleration`. 베이스에는 `direction_deviation`도 없다.

### 터미네이션 전체 목록

| term | 조건 | 처리 |
| --- | --- | --- |
| `object_fall_or_tilt` | 활성 타겟/장애물 중 물체 바닥 높이가 선반 표면보다1cm 넘게 낮거나, 기울기≥0.9rad, 또는 바닥 높이가 비유한 값 | 실패 종료 |
| `shelf_failure` | 선반 root의 선형/각속도를 합친6D norm>0.1, 손목 프레임의 선반 위 높이<3cm, 또는 선반 위치 변위>5cm | 실패 종료. 별도 손가락 높이 종료는 OFF |
| `arm_joint_velocity` | 팔 관절 중 절댓값 속도가 현재 임계값 초과(초기4rad/s) | 실패 종료 |
| `timeout` |10초 도달 | time-limit truncation, bootstrap 유지. 종료 전 평가 메트릭 기록 |
| `success` | timeout이면서 타겟 root–목표 XY 거리<3cm이고 위 실패3항목이 모두 거짓 | 성공 진단용 truncation 항목. 별도 조기 종료나 추가 성공 보상 없음 |

`success`는 `timeout`의 부분집합이므로 두 종료 항목은 동시에 참일 수 있다. 두 비율을 합쳐1로 해석하면 안 된다. 속도나 Holding 시간은 성공 조건에 포함하지 않는다.

### 커리큘럼 전체 목록

기준은 환경 step 수가 아닌 **학습 iteration**이다. 아래 보상 일정은 지정 지점 사이에서250 iteration 간격으로 값을 갱신하는 선형 일정이다. `(iteration:값)`으로 표시했다.

| 활성 term | 변경 대상 | 일정 |
| --- | --- | --- |
| `wrench_free_force_change` | wrench 변화 무비용 범위(N) |0:50, 3000:50, 6000:30, 10000:30, 12000:20 |
| `wrench_free_moment_change` | 모멘트 변화 무비용 범위(Nm) |0:5, 3000:5, 6000:3, 10000:3, 12000:2 |
| `obstacle_free_force` | 장애물 접촉력 무비용 범위(N) |0:80, 3000:80, 6000:50, 10000:50, 12000:30 |
| `wrench_weight` | wrench 변화 weight |0:0, 1000:0, 3000:−0.03, 6000:−0.1 |
| `obstacle_weight` | 장애물 접촉 weight |0:0, 1000:0, 3000:−0.02, 6000:−0.05, 10000:−0.05, 12000:−0.1 |
| `target_goal_direction_deadzone` | ±X 방향 제외 반각 |0–9999:30도, 10000:25도, 이후3000 iteration마다5도 감소, 25000부터0도 |
| `arm_joint_velocity_threshold` | 팔 관절 속도 종료 임계값 |초기4rad/s, 10000 이후250 iteration마다0.05 감소, 최저2rad/s |

비활성 일정: `eef_free_speed`, `pushing_free_speed`, `object_free_acceleration`, `acceleration_weight`, `goal_speed_scale`. 장애물 개수 증가나 성공 반경 축소 일정은 없다. checkpoint 재개 시 학습 iteration에 맞춰 활성 일정을 적용한다.

### 평가 메트릭과 학습 설정

| 메트릭 | 의미 |
| --- | --- |
| `target_goal_distance_xy_m_mean` | 에피소드 내 목표 XY 거리 평균 |
| `eef_linear_speed_m_s_mean`, `target_linear_speed_m_s_mean` | EEF/타겟 선형 속력의 에피소드 평균 |
| `target_within_goal_radius_fraction_mean` | 목표 반경 **이하(≤3cm)** 상태의 시간 비율. 성공 판정의 엄격한<3cm와 경계가 다름 |
| `eef_linear_speed_m_s_episode_max`, `target_linear_speed_m_s_episode_max` | EEF/타겟의 에피소드 최대 속력 |
| `target_goal_distance_xy_m_final`, `target_goal_distance_xy_m_min` | 종료 순간/에피소드 최솟값 목표 거리 |
| `timeout_episode_count` | 최근 완료N개 에피소드 중 timeout 시점까지 도달한 개수 |
| `timeout_success_count` | 같은 창 안에서 timeout 성공 조건을 만족한 개수 |
| `timeout_success_rate` | 위 성공 개수/timeout 개수. 분모0이면0 |

위 custom metric은 TensorBoard의 `Metrics/` 아래 기록한다. 평균/최대/최종 거리 통계는 해당 reset 배치의 에피소드 값들을 평균한다. timeout 집계는 기본N=10,000의 rolling window이며 조기실패도 창의 한 자리를 차지한다. 같은 step의 완료 순서는 env ID 오름차순이다. 이외 RewardManager/TerminationManager/CurriculumManager와 runner의 기본 보상·종료·학습 로그도 사용한다.

PPO는 actor/critic 각각 장애물 encoder(hidden32, embedding16, ReLU)와 MLP `[256,128,64]`(활성함수 ELU)를 사용한다. 입력 정규화는 OFF, Gaussian 초기 std1이다. 환경당 rollout36 steps, 최대90,000 iteration,50 iteration마다 저장한다. PPO는 epoch8·minibatch4, learning rate0.001(adaptive, desired KL0.02), gamma0.98, GAE lambda0.95, clip0.2, entropy0.005, value loss coefficient1, clipped value loss ON, gradient norm1을 사용한다. 모든 파생 환경에서 같은 설정이며 로그 실험명만 구분한다.

## 파생 환경 비교와 실험 의도

아래 의도는 **검증하려는 가설**이며 학습 결과로 확인된 우월성을 뜻하지 않는다. 표에 없는 구성은 직접 부모에서 유지된다.

| 환경(접두사 Inspire-Sweep- 생략) | 직접 부모 | 무엇이 어떻게 바뀌는가 | 무엇을 테스트하기 위한 변경인가 |
| --- | --- | --- | --- |
| `Simple-v0` | 독립 베이스 | Relative-IK v0_2_2_4에서 상속 분리 후, 목표3cm 미만의 접촉 풀 카운트 추가 | 독립 실험 기준을 관리하며, 목표 도달 후 접촉을 놓아도 접촉 유지 보상이 사라지지 않도록 설정 |
| `Simple-Prof-v0` | Simple-v0 | Goal Distance: 최고 기록 개선100→현재 step의 접촉 조건부 접근120. 고정 지시 방향 이탈 비용−6 추가. 접촉 유지 카운트 보상 제거 | 교수님 제안에 따라 직접 미는 동안의 목표 접근과 방향 정렬이 접촉 카운트 중심 구성보다 의도한 sweeping을 유도하는지 비교 |
| `Simple-v1` | Simple-v0 | Reach30의 최고 기록 개선분→현재3D 중심–EEF 근접도 역수 보상. 기존 규모에 맞춰 보정 | 한 번 접근한 뒤 후퇴해도 다시 접근할 보상이 없는 문제를 줄이고, 움직이는 타겟 근처에 머물며 추종하도록 유도할 수 있는지 확인 |
| `Simple-Prof-v1` | Simple-Prof-v0 | Prof 보상은 유지하고 Reach만 Simple-v1 방식으로 교체 | 접촉 조건부 접근/방향 보상과 지속 근접 보상을 결합했을 때 추종·밀기 행동이 개선되는지 확인 |
| `Simple-Hard-v0` | Simple-v1 | 목표6–12cm→7–15cm 또는 방향별 최대 가능 거리. DeadZone curriculum 제거, 처음부터0도 | 접촉 유지 보상+v1 Reach 정책이 더 긴 이동과 Pull/Push 포함 전방향 과제를 초기부터 학습할 수 있는지 확인 |
| `Simple-Prof-Hard-v0` | Simple-Prof-v1 | Simple-Hard와 동일한 목표·DeadZone 변경 | 같은 어려운 목표 분포에서 Prof 보상 구성이 어떻게 작동하는지, Simple-Hard와 비교 |

Prof-v0/v1의 접근 보상과 방향 비용은 현재 타겟 접촉·EEF15cm 미만을 요구한다. 접촉 유지의2-of-3 이력을 사용하지 않는다. 방향 이탈 비용은 각 step의 XY 이동거리에서 초기 지시 방향 성분을 뺀 양으로, 측면·역방향 이동을 비용화한다. 접근은 과거 최고 기록을 넘지 않아도 이전 step보다 가까워지면 보상한다. 비접촉 동안의 이동은 나중에 재접촉할 때 소급 보상하지 않는다.

비교 실험에서는 Simple-v0↔v1 및 Prof-v0↔v1이 Reach 단독 변경이다. Simple-v0↔Prof-v0는 세 보상 변경의 묶음이며, v1↔Hard는 목표 거리와 방향 curriculum 두 변경의 묶음이다. 후자에서 관찰된 차이를 단일 요인의 효과로 단정하지 않는다.

## 보상 차이

| 항목 | Simple-v0 | Simple-v1 | Prof-v0 | Prof-v1 |
| --- | --- | --- | --- | --- |
| Reach weight | 30 | 30 | 30 | 30 |
| Reach 함수 | `DexReachProgress` | `InverseDistanceReach` | `DexReachProgress` | `InverseDistanceReach` |
| Goal Distance | `DexPlanarGoalProgress`, 100 | 동일 | `ContactConditionedSweep`, approach, 120 | 동일 |
| 방향 이탈 | 없음 | 없음 | `ContactConditionedSweep`, direction, −6 | 동일 |
| 접촉 유지 | `GoalContactMaintenance`, 0.1 | 동일 | 없음 | 없음 |
| 목표에서 멀어짐 | `RelativeInverseDistance`, −25.94 | 동일 | 동일 | 동일 |

Simple의 접촉 유지 보상은 목표3cm 미만에서 무조건20이다. 그 밖에서는 기존과 같이 상한20, 인정 시+1, 불인정 시−2(최소0), 최종 불인정 step의 보상0이다. 기존2-of-3 접촉 인정과 초기 선반 표면 기준 EEF 높이15cm 미만 조건을 보존한다. 목표 내부 예외는 Simple-v1/Hard에도 상속된다. Prof의 접근/방향 이탈은 현재 타겟 접촉·EEF 높이15cm 미만 조건을 사용한다.

v1 Reach는 현재 타겟의3D BBOX 중심과 EEF 프레임 사이 거리에서10cm를 뺀 값을0으로 하한 처리한다. 이 값을 `g`, 기존 reset 시 Reach 예산 거리를 `g0`, 에피소드 길이를 `T=10초`라 하면, weight 적용 전 보상 함수는 다음과 같다.

```math
r_{reach} = \frac{g_0}{T}\frac{0.1}{0.1 + g}
```

RewardManager의 policy dt 곱을 그대로 사용한다. 초기 `g0`는 기존 Reach reset 구현을 유지하므로 현재 BBOX 중심 거리와 기준이 다를 수 있다. 처음부터 기존 초기 거리 기준10cm 안이면 `g0=0`이고 해당 에피소드 Reach 보상도0인 기존 v0_2_2_6 동작을 보존한다. Holding·물체 가속도 보상/커리큘럼은 모든 버전에서 비활성이다.

## Hard-v0 공통 변경

2026-11-10 추가. Simple-Hard-v0는 Simple-v1, Simple-Prof-Hard-v0는 Simple-Prof-v1를 직접 상속한다. [개발·검증 기록](../logs/2026-11-10_sweep_simple_hard.md).

- 기존6–12cm 목표를7–15cm 목표로 확대한다. 방향은 전체360도 균등분포로 추출하며 Pull(+X), Push(−X)를 처음부터 포함한다.
- 해당 시작점·방향에서 타겟 전체가 선반 안전 영역 안에 머무는 최대 이동거리를 `L`이라 한다. `L≥15cm`면7–15cm 균등 추출, `L<15cm`면 `L`을 선택한다. `L<7cm`도 그대로 `L`이다. 짧은 방향을 버리거나 방향을 다시 추출하지 않는다.
- 타겟의 고정 yaw −90도와 스케일 반영 BBOX, 기존 선반 가장자리 여유2cm로 root 위치의 유효 사각형을 startup에 캐시한다. 실제 `L`은 무작위 시작점·연속 방향에 따라 달라지므로 reset에서 ray와 캐시된 경계의 교점을 닫힌 수식으로 한 번 산출한다. 후보 반복·사후 유효성 검사·추가 기하 스캔·목표 sampler의 GPU→CPU readback이 없다.
- `target_goal_direction_deadzone` curriculum을 `None`으로 제거하고, spawn의 `excluded_x_half_angle=0`으로 고정한다. 다른 보상/팔 종료 커리큘럼은 유지한다.
- 변경된 목표를 기존 RED 계산·장애물 배치·Warp IK·goal command 생성 전에 전달한다. 목표 거리 계산 외의 Fast reset 흐름은 그대로다. 부모의 보상·관측·제어·종료·메트릭·PPO 하이퍼파라미터를 유지한다.

## 공통 보존 계약

- physics dt0.01초, decimation2, policy dt0.02초, timeout10초, 기본2,048환경.
- 타겟 cylinder1개·물리 장애물16개 고정 roster, 활성 장애물0–6 균등 추첨, 관측 슬롯16개.
- 외접원 기반 RED/WHITE, 간격1cm, 안전 셀5mm, 기존 Warp IK 리셋과 시드 유지. GRAY 배치 없음. 호환 필드는 초기 구성 후 `None`으로 남는다.
- 현재 관측·노이즈·센서·OSC·로봇 제한·자산·마찰/질량 설정 유지. 정책과 value 입력 및 모델 구조 유지.
- 목표 XY 거리3cm 미만이고 동시 실패가 없는10초 timeout을 success로 기록한다. timeout과 success는 중첩되는 truncation 항목이며 기존 bootstrap 계약을 유지한다.
- 최근 완료 에피소드10,000개(조기실패 포함) 안의 timeout/success count와 rate 유지. 같은 step 완료의 순서는 env ID 오름차순.
- 스폰 영역 표시는 `play.py`에서만 켜지고 `train.py`에서는 영상 촬영도 포함해 꺼진다. 기존 스크립트의 공통 `debug_spawn_regions` 처리로 동작한다.
- 나머지 보상, term 순서, 파라미터, 커리큘럼 일정, PPO 설정은 대응하는 기존 버전과 같다. Hard는 위 목표 이벤트와 DeadZone 변경만 예외다. task ID·구성 클래스 이름·로그 실험명은 새 이름이다.

## 파일과 실행

활성 패키지 `src/inspire_sweep_baseline/inspire_sweep_baseline` 기준:

- `envs/sweep_simple_envs.py`: 여섯 EnvCfg 조합.
- `runtime/sweep_simple.py`: 독립 런타임 및 최근 에피소드 통계.
- `assets/scenes/sweep_simple.py`: 독립 씬 구성.
- `mdp/{actions,commands,observations,events,rewards,curricula,terminations}/sweep_simple.py`: 역할별 구성.
- `mdp/common/sweep_simple.py`, `mdp/event_functions/sweep_simple.py`: Hard 목표 도메인 캐시와 startup 연결.
- `agent/sweep_simple_ppo_cfg.py`: 독립 PPO 기본과 여섯 로그 실험명.
- `__init__.py`: 여섯 Gym ID 등록.

workspace root에서 기존 Isaac Lab Python 환경을 활성화한 뒤 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-v0 --headless
```

나머지 버전은 위 표의 task ID로 교체한다. 기존 체크포인트 모델 구조는 유지했지만 실제 체크포인트 로드·GPU rollout·렌더링·학습 성능은 이번 작업에서 실행하지 않았다.
