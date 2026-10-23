# Inspire Sweep Omni 환경 구성

[활성 환경 현황](../08_ACTIVE_ENVIRONMENTS.md) · [문서 안내](../../01_plan/README.md) · [보상 제안 초안](../../01_plan/environments/OMNI_REWARD_PLAN.md)

2026-10-14 문서 위치 정리: 기존 패키지 문서의 내용과 초기 시험값을 보존하고 구현 링크를 갱신했다.

2026-10-14 후속 변경: Omni v0/v1의 Arm action 변화 비용과 속도 비용을 Baseline의 제곱합/가중치 −0.03 수준으로 변경했다. 아래 보상 설명은 변경 후 코드 기준이며, [변경·검증 로그](../logs/2026-10-14_omni_arm_costs_baseline.md)에 이전 값과 검증을 기록했다.

`Isaac-Inspire-Sweep-Omni-v0`는 UR5e와 Inspire Hand로 선반 위의 단일 실린더를 임의의 수평 방향 목표로 이동시키는 환경이다. Initial Joint에서 접근을 시작하고, 목표에서 물체를 안정적으로 정지시키면 성공한다. 목표 도달 후 Homing은 수행하지 않는다.

환경 설정은 `InspireSweepOmniEnvCfg`가 `InspireSweepEnvCfg`를 직접 상속한다. Scene, Action, Observation, 목표 Command와 제어 주기는 Baseline을 사용하며, Event, Reward, Termination은 새 구성으로 교체한다. 질량·마찰은 Realistic Physics의 함수를 재사용한다. PPO는 `InspireSweepPPORunnerCfg`를 그대로 사용한다.

아래 값은 현재 코드의 기본 설정이다. 보상 가중치와 일부 임계값은 초기 시험값이며, 학습 결과에 따라 조정할 수 있다. 별도로 표시하지 않은 거리·높이는 m, 각도는 rad, 관절 속도는 rad/s다. Quaternion 순서는 `(w, x, y, z)`다.

## 1. Scene 구성

### 1.1 좌표계와 환경 복제

현재 환경에서 수평 평면은 월드 XY이고 높이는 Z다. `env_origins`는 병렬 환경마다 더해지는 월드 위치 오프셋이다. 아래 초기 위치는 해당 오프셋을 더하기 전의 환경 로컬 위치다.

로봇 root는 Z축으로 180° 회전되어 있으므로, 로봇 root 기준 관측 좌표와 월드 좌표의 X/Y 방향은 다르다. 스폰은 선반 로컬 좌표에서 계산한 뒤 현재 선반 pose로 월드에 변환한다. 목표 거리 보상과 성공의 평면 오차·속도는 월드 XY에서 계산한다.

| 파라미터 | 기본값 | 의미 |
| --- | --- | --- |
| `scene.num_envs` | 4096 | 병렬 시뮬레이션 환경 개수. 실행 시 `--num_envs`로 변경 가능 |
| `scene.env_spacing` | 2.5 m | 병렬 환경 배치 간격 |
| `sim.dt` | 0.01 s | 물리 시뮬레이션 한 Step의 시간 |
| `decimation` | 2 | Action 하나를 유지하며 진행하는 물리 Step 수 |
| `step_dt` | 0.02 s | `sim.dt × decimation`. 정책 제어 주기이며 제어 주파수는 50 Hz |
| `episode_length_s` | 10 s | 에피소드 최대 길이. 기본 제어 주기에서 최대 500 Step |
| `sim.render_interval` | 2 | 물리 Step 두 번마다 렌더링 |

### 1.2 자산과 물체

| Scene 항목 | 구성 | 의미 |
| --- | --- | --- |
| `ground` | `/World/ground`, GroundPlane | 전체 월드의 바닥. 에피소드별 선반 마찰 랜덤화의 대상은 아님 |
| `light` | DomeLight, 색 `(0.75, 0.75, 0.75)`, intensity 2500 | Scene 조명 |
| `shelf` | 초기 root `(-0.7, 0, 0)`, 질량 100 kg | 실린더를 지지하는 선반. 이동 상태를 보상·종료 검사에 사용 |
| `robot` | UR5e + Axia80 모티브 F/T 하우징 + Inspire Hand | Arm 6개와 Hand 12개 관절을 가진 articulation |
| `object_collection` | `mass_cylinder` 한 개 | 밀기 대상인 단일 실린더. 장애물이나 비대상 물체는 없음 |

선반 중간 상판은 기본 pose에서 월드 X `[-0.9, -0.5]`, Y `[-0.5, 0.5]`, Z `1.05`에 위치한다. 선반 로컬 XY 반폭은 `(0.20, 0.50)`이다. 선반 root의 Z=0과 상판 높이 Z=1.05를 구분해야 한다.

로봇 USD는 패키지 내부 자산을 사용하고 선반 USD는 외부 경로를 사용한다. `INSPIRE_SWEEP_SHELF_USD_PATH` 또는 호환 변수 `SWEEP_POLICY_SHELF_USD_PATH`가 있으면 파일 경로를 직접 지정한다. 없으면 `INSPIRE_SWEEP_ASSET_ROOT` 또는 `SWEEP_POLICY_ASSET_ROOT`에 `Arena/Collected_speedrack_shape/speedrack_shape.usd`를 붙인다. 이들 변수를 지정하지 않은 기본 root는 `omniverse://192.168.0.13/Library/Shelf`다. 같은 종류의 두 변수 중에서는 `INSPIRE_SWEEP_*` 값을 우선한다. 선반 자산을 바꾸면 아래 상판 크기와 높이도 맞춰야 한다.

| 실린더 파라미터 | 기본값 | 의미 |
| --- | --- | --- |
| `radius` | 0.04 m | 반지름 4 cm. 지름은 8 cm |
| `height` | 0.10 m | 높이 10 cm |
| `axis` | `Z` | 직립 시 실린더 길이 방향 |
| `init_state.pos` | `(-0.7, 0, 1.05)` | 생성 시 기준 pose. 에피소드 리셋에서 원판 샘플 위치로 교체 |
| `mass_props.mass` | 0.365 kg | 생성 시 평균 질량. 리셋마다 새 질량을 적용 |
| 물체 link 원점 | 바닥면 중심 | 물체 위치 관측과 목표·높이 검사가 참조하는 점 |
| 기하학적 중심 | 바닥에서 +0.05 m | 실린더 형상의 중심 |
| 질량 중심 COM | 바닥에서 +0.02 m | 아래쪽이 무거운 질량 분포의 중심 |

질량 분포는 아래 20% 높이 구간에 전체 질량의 80%, 나머지 위 구간에 20%를 둔다. 에피소드 질량이 바뀌어도 이 분포와 COM은 유지하고, 관성을 원래 관성에 질량 비율을 곱해 재설정한다.

실린더 표시 색상인 `visual_material.diffuse_color=(0.1, 0.4, 0.8)`은 RGB 값이다. 마찰 계수나 관측 노이즈를 뜻하지 않는다.

### 1.3 로봇 초기 상태와 구동기

로봇 root 위치는 `(0, 0, 0.79505)`, 회전은 `(0, 0, 0, 1)`이다. 초기 관절 속도는 모두 0이고, Hand는 모든 관절 위치가 0인 편 상태로 시작한다.

| Arm 관절 순서 | 초기 위치 | stiffness | damping | effort limit | velocity limit |
| --- | ---: | ---: | ---: | ---: | ---: |
| `shoulder_pan_joint` | 0.0 | 3328.7 | 368.8 | 150 Nm | 3.14 rad/s |
| `shoulder_lift_joint` | −2.2 | 4989.4 | 561.2 | 150 Nm | 3.14 rad/s |
| `elbow_joint` | 2.2 | 2394.2 | 274.1 | 150 Nm | 3.14 rad/s |
| `wrist_1_joint` | 0.0 | 3500.2 | 396.2 | 28 Nm | 6.28 rad/s |
| `wrist_2_joint` | 1.57 | 3174.8 | 363.1 | 28 Nm | 6.28 rad/s |
| `wrist_3_joint` | 0.785 | 3032.4 | 345.0 | 28 Nm | 6.28 rad/s |

`stiffness`는 위치 오차에 대한 구동 강성(Nm/rad), `damping`은 속도 오차에 대한 감쇠(Nm·s/rad)다. `effort_limit_sim`은 시뮬레이터 구동 토크 한도이고, `velocity_limit_sim`은 구동 관절 속도 한도다. 이 구동기 속도 한도와 에피소드 종료의 Arm 1 rad/s 임계값은 서로 다른 설정이다.

| Hand 구동기 파라미터 | 기본값 | 의미 |
| --- | ---: | --- |
| `effort_limit_sim` | 0.20 Nm | 각 Hand 관절의 구동 토크 한도 |
| `velocity_limit_sim` | 1.0 rad/s | 각 Hand 관절의 구동 속도 한도 |
| `stiffness` | 1.2 | 위치 추종 강성 |
| `damping` | 0.06 | 속도 감쇠 |
| `armature` | 0.0001 kg·m² | 관절 구동계에 추가되는 관성 값 |

로봇 중력은 활성화하고 articulation self-collision은 비활성화한다. 로봇의 `activate_contact_sensors=True`는 접촉 정보 수집을 활성화한다. F/T 하우징은 반지름 0.041 m, 높이 0.0254 m, 질량 0.001 kg이며 손목과 Hand 사이에 삽입된다.

### 1.4 Frame과 센서

| 항목 | 기준과 offset | 용도 |
| --- | --- | --- |
| `ee_frame` | `axia80_link`에서 `(0, 0, 0.13 + sensor_height/2)` = `(0, 0, 0.1427)` | EEF pose 관측, 접근 진척, F/T의 표현 좌표·모멘트 기준점 |
| `finger_frame` | `inspire_base_link`에서 `(±0.07, 0, 0.13)` | 기존 선반 보상·종료에 쓰는 두 가상 finger 기준점 |
| `wrist_frame` | `inspire_base_link`에서 `(0, 0, −0.17)` | 기존 선반 보상·종료에 쓰는 가상 wrist 기준점 |
| `palm_tactile` | `inspire_palm_force_sensor` | 손바닥 한 영역의 접촉 여부 관측 |

Frame offset 회전은 공통으로 `(0.5, −0.5, −0.5, −0.5)`다. `ee_frame`은 Hand 기준 `(0, 0, 0.13)`에 해당하는 고정점으로, 손가락 굽힘만 바뀌어도 위치가 변하지 않는다. `finger_frame`은 실제 손끝의 실시간 위치를 추적하는 센서가 아니라 Hand base에 고정된 가상 기준점이다.

`palm_tactile.update_period=0.0`은 Scene 갱신마다 센서를 업데이트한다는 의미이고, `history_length=1`은 현재 샘플 한 개를 보관한다는 의미다. `force_threshold=0.05`는 센서의 접촉 관련 임계값이며, 관측의 접촉 bit는 별도 함수의 `threshold_n=0.05 N`으로 계산한다. Frame 시각화 marker 크기는 각 축 0.05 m이고 `ee_frame.debug_vis=True`다. Viewer의 기본 `eye=(3.5, 3.5, 3.5)`, `lookat=(0, 0, 0.3)`은 화면 시점만 결정한다.

### 1.5 물리 계산 파라미터

| 적용 대상·파라미터 | 기본값 | 의미 |
| --- | --- | --- |
| 실린더 `solver_position_iteration_count` | 16 | 위치·접촉 제약을 푸는 반복 횟수 |
| 실린더 `solver_velocity_iteration_count` | 1 | 속도 제약을 푸는 반복 횟수 |
| 실린더 `max_angular_velocity` | 1000 rad/s | 물리 엔진의 각속도 상한 |
| 실린더 `max_linear_velocity` | 1000 m/s | 물리 엔진의 선속도 상한. 종료 속도 0.3 m/s와 다름 |
| 로봇·실린더 `max_depenetration_velocity` | 5 m/s | 겹침을 해소할 때 허용하는 최대 분리 속도 |
| 실린더 `disable_gravity` | `False` | 중력 활성화 |
| 실린더 `collision_enabled` | `True` | 충돌 활성화 |
| 실린더 `contact_offset` | 0.001 m | 접촉 생성에 사용하는 형상 주변 offset |
| 실린더 `rest_offset` | 0 m | 접촉 정지 상태의 형상 offset |
| `physx.bounce_threshold_velocity` | 0.2 m/s | 저속 접촉에서 반발을 억제하는 속도 기준 |
| `physx.friction_correlation_distance` | 0.00625 m | 근접 접촉점의 마찰 patch 연관 거리에 사용하는 값 |
| `gpu_found_lost_aggregate_pairs_capacity` | `1024 × 1024 × 16 × 16` | 생성·소멸하는 aggregate pair용 GPU 버퍼 용량 |
| `gpu_total_aggregate_pairs_capacity` | `16 × 1024 × 16` | 전체 aggregate pair용 GPU 버퍼 용량 |
| `gpu_max_rigid_patch_count` | `5 × 2^17` | GPU rigid contact patch 용량 |

버퍼 용량은 병렬 접촉 계산의 저장 공간을 설정한다. 보상 임계값이나 물체의 물리 질량·마찰을 의미하지 않는다.

구현: [env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_envs.py), [robot.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/robot.py), [mass_cylinder.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/mass_cylinder.py).

## 2. Action 구성

Action은 총 8차원이며 Arm 6개와 Hand 2개 순서로 연결한다.

| Action 구간 | 설정 항목 | 제어 내용 |
| --- | --- | --- |
| `[0:6]` | `arm_action` | 위 표 순서의 UR5e 6개 관절 위치 명령 |
| `[6]` | `gripper_action` 채널 0 | 엄지 opposition을 제외한 11개 Hand 관절의 공통 openness |
| `[7]` | `gripper_action` 채널 1 | `inspire_left_thumb_1_joint`의 별도 opposition openness |

### 2.1 Arm Action

```text
q_target[j] = q_default[j] + 0.5 × action[j]
```

| 파라미터 | 기본값 | 의미 |
| --- | --- | --- |
| `asset_name` | `robot` | 명령을 적용하는 articulation |
| `joint_names` | `ARM_JOINT_NAMES` | 제어 대상 Arm 관절 6개 |
| `preserve_order` | `True` | Action 차원과 관절 이름 순서의 대응 유지 |
| `scale` | 0.5 | Action 한 단위를 목표 관절 위치 0.5 rad로 변환 |
| `use_default_offset` | `True` | 목표 위치의 기준을 초기 관절 위치로 설정 |

Arm Action은 이전 Step 목표에 더하는 증분 명령이 아니다. 매 Step 초기 관절 위치를 기준으로 목표를 계산한다. 이 환경 Cfg에는 별도의 Arm Action clip 범위를 추가하지 않는다.

### 2.2 Hand Action

두 입력은 실제 적용 전에 각각 `[0, 1]`로 clip한다. 1은 편 상태, 0은 굽힌 상태다. 각 관절의 목표는 다음 식으로 보간한다.

```text
q_target[j] = q_closed[j] + openness[j] × (q_open[j] − q_closed[j])
```

| Hand 관절 | 사용하는 채널 | `q_open` | `q_closed` |
| --- | ---: | ---: | ---: |
| `inspire_left_thumb_1_joint` | 1 | 0 | 1.1641 |
| `inspire_left_thumb_2_joint` | 0 | 0 | 0.5864 |
| `inspire_left_thumb_3_joint` | 0 | 0 | 0.47052736 |
| `inspire_left_thumb_4_joint` | 0 | 0 | 0.446389306432 |
| `inspire_left_index_1_joint` | 0 | 0 | 1.4381 |
| `inspire_left_index_2_joint` | 0 | 0 | 1.55933183 |
| `inspire_left_middle_1_joint` | 0 | 0 | 1.4381 |
| `inspire_left_middle_2_joint` | 0 | 0 | 1.55933183 |
| `inspire_left_ring_1_joint` | 0 | 0 | 1.4381 |
| `inspire_left_ring_2_joint` | 0 | 0 | 1.55933183 |
| `inspire_left_little_1_joint` | 0 | 0 | 1.4381 |
| `inspire_left_little_2_joint` | 0 | 0 | 1.55933183 |

`gripper_action.asset_name="robot"`은 제어 대상 articulation을 지정한다. Hand 12개 관절의 대응과 open/closed 위치는 `HAND_JOINT_NAMES`, `HAND_OPEN_TARGETS`, `HAND_CLOSED_TARGETS`에 정의되어 있다.

리셋 시 Arm Action 이력은 0, Hand의 두 입력과 이력은 `[1, 1]`이 된다. 따라서 Hand Action 0은 초기의 편 자세가 아니라 굽히는 명령에 대응한다. 추가 Action 필터는 없다.

구현: [actions.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/action_functions/hand_openness.py), [env.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/sweep.py).

## 3. Event 구성

### 3.1 이벤트 종류와 순서

| Event 이름 | 실행 시점 | 함수 | 역할 |
| --- | --- | --- | --- |
| `physics_materials` | `startup` | `initialize_realistic_materials` | 물리 view의 질량·관성·재질 버퍼, Hand 충돌 형상 인덱스와 마찰 풀을 한 번 준비 |
| `reset_all` | `reset` | `reset_scene_to_default` | 선반과 로봇의 root·속도 및 로봇 관절 상태를 초기 상태로 복원 |
| `object_spawn` | `reset` | `randomize_goal_object_scene` | 단일 실린더 pose와 목표 이동 벡터를 새로 샘플링 |
| `physics_randomization` | `reset` | `randomize_episode_physics` | 해당 환경의 물체 질량·관성과 선반·물체·Hand 마찰을 새로 설정 |

리셋 이벤트는 `reset_all → object_spawn → physics_randomization` 순서로 실행한다. `env_ids`는 리셋할 병렬 환경의 인덱스다. 나머지 환경의 상태는 유지한다. Scene 기본 리셋 함수의 `reset_joint_targets` 기본값은 `False`이며, Action term 리셋에서 제어 이력을 초기화한다. 실린더 collection의 새 상태는 `object_spawn`이 직접 작성한다.

### 3.2 물체 스폰과 목표 샘플링

| 파라미터 | 기본값 | 의미 |
| --- | --- | --- |
| `spawn_radius` | 0.02 m | 선반 정중앙의 가상 스폰 원판 반지름 |
| `goal_distance` | 0.15 m | 초기 물체 위치에서 목표까지 요청하는 수평 이동 거리 |
| `object_radius` | 0.04 m | 목표의 가장자리 간격 계산과 `target_width`에 사용하는 물체 반지름 |
| `edge_clearance` | 0.02 m | 물체 반지름에 추가하는 가장자리 여유 |
| `shelf_half_extents` | `(0.20, 0.50)` m | 선반 로컬 X/Y 방향의 상판 반폭 |
| `shelf_surface_height` | 1.05 m | 선반 root 기준 상판 높이. 물체 바닥 원점의 스폰 높이 |

스폰 반경은 `r = spawn_radius × sqrt(U)`, `U ~ Uniform(0, 1)`로 샘플링한다. 방위도 균일하게 샘플링하므로 원판의 면적에 대해 균일한 분포가 된다. 스폰 높이는 상판 높이로 고정하고, 실린더 yaw는 `[−π, π)`에서 무작위로 설정한다. 초기 선속도와 각속도는 0이다.

목표 방위는 스폰 방위와 독립적으로 `[−π, π)` 전체에서 균일하게 샘플링한다. 목표 중심이 들어갈 수 있는 안전 영역의 선반 로컬 반폭은 다음과 같다.

```text
safe_half_extents = shelf_half_extents − object_radius − edge_clearance
                  = (0.14, 0.44) m
```

스폰 위치에서 샘플링한 방향으로 뻗는 직선과 이 안전 영역 경계의 교점을 구한다. 실제 목표 이동 거리는 `min(goal_distance, 경계까지의 거리)`다. 목표가 가장자리에 가까워지면 이동 거리만 줄이며 스폰 위치와 목표 방위는 유지한다.

예를 들어 선반 로컬 X=+2 cm에서 +X 방향으로 밀면 안전 경계 X=+14 cm까지 이동할 수 있으므로 목표 거리는 15 cm에서 12 cm로 줄어든다. 현재 기본값에서 목표 거리는 대략 12–15 cm 범위다. 스폰 원판 전체가 안전 영역에 들어가지 않는 설정은 예외로 거부하며, 이 경우 스폰 반지름을 자동으로 변경하지 않는다.

### 3.3 목표 Command

이벤트는 `env.sweep_dir`에 실제 목표의 월드 이동 벡터를 저장한다. 상속된 `SweepGoalCommand`는 리셋 후 초기 물체 pose를 저장하고 다음 목표를 만든다.

```text
goal_position_world = initial_object_position_world + env.sweep_dir
```

| Command 파라미터 | 기본값 | 의미 |
| --- | --- | --- |
| Command 이름 | `target_goal_pos` | 보상·성공·관측 함수가 참조하는 목표 이름 |
| `asset_name` | `object_collection` | 초기 상태를 가져오는 물체 collection |
| `resampling_time_range` | `(1e6, 1e6)` s | 실행 중 재샘플링 간격. 10초 에피소드에서는 목표가 리셋 시에만 갱신됨 |
| `debug_vis` | `False` | 목표 Command 디버그 표시 비활성화 |

Command의 반환값은 목표 위치 3D와 초기 물체 quaternion 4D를 합친 7D다. 이 환경의 목표 관측·보상은 위치만 사용하므로 실린더 yaw를 초기 방향으로 맞출 필요는 없다. 물체가 움직여도 월드 목표 위치는 고정된다.

### 3.4 질량과 마찰 랜덤화

질량은 매 에피소드 `Normal(0.365, 0.0675²)` kg에서 샘플링하고 `[0.230, 0.500]` kg으로 clip한다.

| 상수 | 기본값 | 의미 |
| --- | --- | --- |
| `MASS_MEAN` | 0.365 kg | 질량 분포 평균 및 생성 기본 질량 |
| `MASS_STD` | 0.0675 kg | 질량 분포 표준편차 |
| `MASS_LIMITS` | `(0.230, 0.500)` kg | 샘플 질량의 하한·상한 |
| `FRICTION_BUCKET_COUNT` | 4096 | 접촉 역할별 유한 마찰 재질 풀 크기 |

| 접촉 역할 | 정적 평균 | 정적 표준편차 | 동적 평균 | 동적 표준편차 |
| --- | ---: | ---: | ---: | ---: |
| 선반 | 0.315 | 0.051 | 0.252 | 0.041 |
| 물체 | 0.315 | 0.040 | 0.252 | 0.032 |
| Hand | 0.585 | 0.145 | 0.468 | 0.116 |

마찰 계수는 무차원이다. 위 값은 `STATIC_FRICTION_MEANS/STDS`, `DYNAMIC_FRICTION_MEANS/STDS`에 선반·물체·Hand 순서로 정의한다. Gaussian 분위값으로 역할별 4096개 재질 풀을 구성하고, 리셋 시 각 역할이 독립적으로 재질 ID를 선택한다. 음수 계수는 0으로 제한한다. ±2σ로 clip하지 않으며, 동적 마찰은 정적 마찰의 0.8배로 고정하지 않는다.

Friction Combine Mode는 `average`이므로 두 접촉면 계수의 평균이 접촉쌍에 적용된다. Hand의 충돌 링크·패드만 Tool 역할로 랜덤화하고, Arm·Axia80 하우징·GroundPlane의 마찰은 유지한다. Restitution과 compliant contact 설정도 보존한다.

초기 재질 바인딩은 PhysX 시작과 환경 복제 전에 스포너가 수행한다. 이후 에피소드 랜덤화는 Tensor API로 처리한다. 질량·마찰은 정책 관측에 추가하지 않는다.

구현: [goal_events.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/goal_events.py), [commands.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/command_functions/sweep_goal.py), [물성 Event Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/events/sweep.py), [물성 적용 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/realistic_physics.py), [물성 분포·계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/realistic_physics.py).

## 4. Observation 구성

Actor와 Critic은 동일한 `policy` 41D 관측을 사용한다. `enable_corruption=True`로 명시된 노이즈를 적용하고, `concatenate_terms=True`로 아래 순서대로 연결한다.

| 구간 | 관측 term | 차원 | 의미·좌표계 |
| --- | --- | ---: | --- |
| `[0:6]` | `joint_pos` | 6 | 현재 Arm 관절 위치 − 초기 Arm 관절 위치, rad |
| `[6:12]` | `joint_vel` | 6 | 현재 Arm 관절 속도 − 초기 Arm 관절 속도, rad/s. 초기 속도는 0 |
| `[12:20]` | `actions` | 8 | 현재 ActionManager에 저장된 가장 최근 입력 Action |
| `[20:23]` | `target_obs_state` | 3 | 현재 물체 바닥 원점 위치, 로봇 root 기준, m |
| `[23:24]` | `target_obj_width` | 1 | 이름은 width지만 실제 값은 실린더 반지름 0.04 m |
| `[24:31]` | `ee_pose` | 7 | EEF 위치 3D와 quaternion 4D, 로봇 root 기준 |
| `[31:34]` | `goal_pos` | 3 | 목표 위치, 로봇 root 기준, m |
| `[34:35]` | `tactile` | 1 | 손바닥 한 영역의 접촉 bit 0 또는 1 |
| `[35:41]` | `wrist_wrench` | 6 | EEF 기준 `[Fx, Fy, Fz, Mx, My, Mz]`, N 및 Nm |

### 4.1 관측 파라미터

| 파라미터 | 적용 관측 | 기본값·의미 |
| --- | --- | --- |
| `asset_cfg` | `joint_pos`, `joint_vel` | `robot`의 `ARM_JOINT_NAMES` 6개를 순서대로 선택 |
| `noise.n_min`, `noise.n_max` | 물체 위치·width | 각각 −0.01, +0.01 m. 관측 계산 시 균일 노이즈를 더함 |
| `command_name` | `goal_pos` | `target_goal_pos`에서 목표를 조회 |
| `sensor_name` | `tactile` | 함수 기본값 `palm_tactile` |
| `threshold_n` | `tactile` | 함수 기본값 0.05 N. 손바닥 net contact force norm이 이 값 이상이면 1 |
| `asset_name` | `wrist_wrench` | 함수 기본값 `robot` |
| `frame_name` | `wrist_wrench` | 함수 기본값 `ee_frame`. Wrench 좌표와 모멘트 기준점 지정 |

물체 위치는 매 Step 갱신되는 현재 위치다. 접근 진척 계산용 초기 물체 위치 snapshot과 구분한다. 물체 위치와 width의 노이즈는 에피소드당 고정 오차가 아니라 관측 계산마다 샘플링된다. EEF quaternion은 동등한 부호 표현의 변화가 줄도록 `quat_unique`를 적용한다.

`actions` 관측은 Hand의 `[0, 1]` clip 전 입력을 포함한다. 따라서 관측의 Hand Action 값과 실제 적용된 openness 값은 다를 수 있다. Hand 관절 위치·속도, 물체 quaternion·선속도·각속도, 질량·마찰을 독립적인 관측 항으로 제공하지 않는다. Actor와 Critic에 별도 privileged 관측도 없다.

### 4.2 촉각과 Wrench

촉각은 Hand 전체 접촉을 합친 값이 아니라 실제 손바닥 패드 한 영역의 값이다. Wrench는 Hand mount의 고정 조인트 반력을 읽어 EEF 축으로 회전하고, 모멘트 기준점을 EEF로 이동한다. 힘의 단위는 N, 모멘트의 단위는 Nm다.

Wrench에는 손의 무게와 동역학 반력이 포함된다. 중력 보상, tare, 추가 필터를 적용하지 않는다. 리셋 직후 아직 갱신되지 않은 촉각·Wrench 샘플은 해당 환경에서 0으로 마스킹한다. 두 센서 관측을 보상이나 성공 게이트의 직접 입력으로 사용하지 않는다.

구현: [observations.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/sweep.py), [sensors.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/sensors.py), [env.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/sweep.py).

## 5. Reward 구성

### 5.1 보상 합산과 시간 단위

`RewardManager`는 모든 term의 반환값에 `weight × step_dt`를 곱한다. 접근 진척과 성공·실패 함수는 반환 전에 `step_dt`로 나누므로 실제 지급량은 제어 주기와 무관하게 유지된다. 나머지는 초당 누적되는 보상·비용으로 해석한다. 계획서의 `T_ref`는 1초다.

```text
r_step = reaching_progress + 30 × success − 80 × failure
       + Δt × [6 × goal_cost
               − 0.03 × arm_action_rate − 0.03 × hand_action_rate
               − 0.03 × arm_joint_velocity − 0.01 × hand_joint_velocity
               − 2 × object_tilt − 0.5 × shelf_collision − 0.1]
```

| Reward term | weight | 용도 |
| --- | ---: | --- |
| `goal_distance` | +6.0 | 목표 평면 거리 비용 |
| `reaching` | +1.0 | 새롭게 갱신한 최단 접근 거리의 진척 |
| `arm_action_rate` | −0.03 | Arm 6개 명령 변화량의 제곱합 |
| `hand_action_rate` | −0.03 | Hand 명령 급변 억제 |
| `arm_joint_velocity` | −0.03 | 실제 Arm 6개 관절 속도의 제곱합 |
| `hand_joint_velocity` | −0.01 | 실제 Hand 관절 속도 비용 |
| `object_tilt` | −2.0 | 허용 범위 이상의 기울기 억제 |
| `shelf_collision` | −0.5 | 기존 선반 이동·가상 손 기준점 높이 비용 |
| `time` | −0.1 | 대기와 장시간 수행에 초당 비용 부여 |
| `success` | +30.0 | 성공 종료 전이에 한 번 지급 |
| `failure` | −80.0 | 실패 종료 전이에 한 번 지급 |

아래 수식은 `step_dt` 역보정 전의 진척량 또는 dense 비용을 나타낸다. 최종 학습 보상에서는 위 합산식을 따른다.

### 5.2 목표 거리

```text
d = norm(object_position_world[:2] − goal_position_world[:2])
goal_cost = exp(−d / sigma) − 1
```

`sigma=0.10 m`는 거리 비용이 변하는 공간 척도다. 목표에서 0이고, 멀어질수록 −1에 가까워진다. `command_name` 함수 기본값은 `target_goal_pos`다. 높이는 이 거리 계산에 포함하지 않는다. EEF 접근 게이트, 특정 축 속도 보상, 목표 방향 속도 보상은 없다.

### 5.3 접근 진척

```text
d_reach[t] = max(norm(p_ref[t] − p_object_initial) − near_radius, 0)
b[0] = d_reach[0]
b[t] = min(b[t−1], d_reach[t])
reaching_progress[t] = (b[t−1] − b[t]) / max(d_reach[0], epsilon)
```

| 파라미터 | 기본값 | 의미 |
| --- | --- | --- |
| `near_radius` | 0.10 m | 초기 물체 원점 주변에 설정하는 근접 영역 반경 |
| `frame_name` | `ee_frame` | 접근 거리의 손 측 고정 기준점 |
| `epsilon` | `1e-6` m | 함수 기본값. 초기 접근 거리가 0일 때 나눗셈을 보호하는 하한 |

접근 거리는 3D 거리이며 물체의 **초기 바닥 원점**을 사용한다. 실린더가 이동해도 접근 목표가 따라가지 않는다. 물체 중심이나 바닥+9 cm를 접근 목표로 사용하지 않는다. 손가락 굽힘으로 움직이는 fingertip도 참조하지 않는다.

이전보다 가까워진 새 기록에만 양의 보상을 준다. 가까이 멈추거나, 멀어졌다가 같은 거리로 돌아오면 0이다. 근접 영역을 처음 달성하면 이후 진척 보상은 없다. 비할인 에피소드 합계는 `weight=1.0`을 넘지 않으며, 초기부터 근접 영역 안에 있으면 접근 보상은 0이다. 리셋된 환경의 기록만 새 Scene 상태로 초기화한다.

### 5.4 Arm과 Hand Action Rate

2026-10-15부터 Omni 베이스와 모든 파생(Dex Omni 포함)은 로컬 `mdp/reward_functions/goal_rewards.py`의 `action_rate_l2`를 사용한다.

```text
arm_cost = sum((raw_action_current[:6] − raw_action_previous[:6])²)
hand_cost = sum((raw_action_current[6:8] − raw_action_previous[6:8])²)
```

두 항의 weight는 각각 −0.03이다. 평균·정규화·보상 내부 clamp는 없다. Hand raw 입력이 [0, 1] 밖에 있어도 변화량을 계산한다. 실제 Hand 제어에서 openness를 clamp하는 동작은 유지한다. Action Rate는 명령 크기 자체나 시간 미분에 대한 페널티가 아니다.

### 5.5 Arm과 Hand 관절 속도

로컬 `goal_rewards.joint_vel_l2`는 이름으로 선택한 실제 관절 속도의 제곱합을 반환한다. Arm 6개/Hand 12개를 별도 항으로 유지하며 weight는 각각 −0.03/−0.01이다. 평균이나 기준 속도 정규화는 없다. 관절 배열의 앞 6개를 Arm이라고 가정하지 않는다.

네 항 모두 RewardManager가 weight와 step_dt를 한 번 곱한다. 참고 Inspire 환경의 수식을 로컬로 구현하며 해당 환경에서 import하지 않는다. [필수 개발 규칙](../../00_guidelines/09_DEVELOPMENT_GUIDE.md)과 [검증 로그](../logs/2026-10-15_omni_penalty_contract.md)를 따른다.

### 5.6 물체 기울기

```text
theta = acos(clip(dot(object_up_axis, current_shelf_normal), −1, 1))
cost = clip((theta − free_angle) / (fail_angle − free_angle), 0, 1)²
```

| 파라미터 | 기본값 | 의미 |
| --- | --- | --- |
| `free_angle` | 5° = 약 0.08727 rad | 이 각도 이하에서는 기울기 비용 0 |
| `fail_angle` | 0.9 rad = 약 51.57° | 비용이 1에 도달하는 각도. 전도 종료도 동일 값 사용 |

두 축은 현재 pose의 회전 행렬 열 벡터로 계산한다. 수평 yaw 회전은 물체 up axis를 바꾸지 않으므로 이 비용에 포함되지 않는다.

### 5.7 기존 선반 페널티

`ShelfCollisionPenalty`의 기존 계산을 유지한다. 함수에 별도 `params`를 전달하지 않으며 아래 숫자는 함수 내부 상수다.

```text
moved = (norm(shelf_position − initial_shelf_position) + norm(shelf_root_velocity_6D)) > 0.005
surface_ref = shelf_position + (0, 0, 1.06)
near = norm(surface_ref − eef_position) < 0.20
finger_cost = sum(clip(1 − finger_height / 0.02, 0, 1))
wrist_cost = clip(1 − wrist_height / 0.08, 0, 1)
shelf_cost = float(moved) + float(near) × (finger_cost + wrist_cost)
```

| 내부 상수 | 의미 |
| --- | --- |
| `0.005` | 이동 거리 norm과 6D root 속도 norm을 더한 값의 판정 기준. 서로 다른 단위를 섞은 기존 heuristic이며 단순한 5 mm 변위 기준으로 해석할 수 없음 |
| `1.06 m` | 페널티 높이 기준점. 실제 상판 1.05 m보다 1 cm 위 |
| `0.20 m` | EEF가 선반 중심의 높이 기준점과 가까운지 판단하는 3D 반경 |
| `0.02 m` | 각 가상 finger 높이 비용의 감소 척도 |
| `0.08 m` | 가상 wrist 높이 비용의 감소 척도 |

Finger/wrist 높이는 `surface_ref`의 월드 Z를 뺀 값이다. 두 finger 비용과 wrist 비용은 `near`일 때만 적용하고, 선반 이동 비용은 이 게이트와 무관하게 적용한다. 반환 범위는 0–4다. 이 항은 접촉력 크기를 직접 측정하는 보상이 아니다.

### 5.8 시간과 성공·실패

시간 항은 매 Step 1을 반환한다. 기본 weight −0.1과 `step_dt=0.02 s`를 적용하면 Step당 −0.002다.

성공 항의 `termination_name` 함수 기본값은 `success`다. 이 종료 term의 결과를 읽어 +30을 지급한다. 실패 항의 `failure_terms`는 다음 여섯 term의 OR이다.

```text
object_drop, push_fast, shelf_collision, hand_velocity,
object_outside_shelf, shelf_displacement
```

여러 실패가 동시에 발생해도 −80 한 번만 지급한다. `time_out`과 `success`는 실패 목록에 포함하지 않는다. 성공·실패는 Termination 계산 후, 자동 리셋 전에 보상으로 지급하므로 에피소드 종료 전이에서 한 번 발생한다.

기존의 지속적인 양의 Reaching, EEF 방향 정렬, Y축 속도, Homing 및 비대상 물체 보상은 새 Reward 구성에 포함하지 않는다.

구현: [omni_env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_envs.py), [goal_rewards.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_rewards.py), [rewards.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/sweep.py).

## 6. Termination 구성

### 6.1 실패와 시간 제한

| Termination term | 파라미터·기준 | 종료 조건 |
| --- | --- | --- |
| `time_out` | `time_out=True`, `episode_length_s=10` | 에피소드가 10초 제한에 도달. 실패가 아닌 timeout/truncation으로 처리 |
| `object_drop` | `height_condition=1.04 m`, `fail_angle=0.9 rad` | 환경 원점을 뺀 물체 바닥 월드 Z가 1.04 m 미만, 또는 상판 법선 기준 물체 기울기가 0.9 rad 이상 |
| `push_fast` | `speed_condition=0.3 m/s` | 물체의 3D 선속도 norm이 0.3 m/s 초과 |
| `shelf_collision` | `threshold=0.1` 및 내부 높이 상수 | 아래 설명의 선반 속도·가상 finger/wrist 높이 중 하나라도 위반 |
| `hand_velocity` | Arm `asset_cfg`, `threshold=1.0 rad/s` | 선택한 Arm 6개 관절 중 하나라도 속도 절댓값이 1 rad/s 초과 |
| `object_outside_shelf` | `half_extents=(0.20, 0.50)` m | 현재 선반 로컬 좌표에서 물체 바닥 원점의 `abs(X)>0.20` 또는 `abs(Y)>0.50` |
| `shelf_displacement` | `threshold=0.05 m` | 선반 root가 초기 월드 위치에서 3D 거리 5 cm 초과 이동 |

`hand_velocity`는 기존 로그 이름을 유지한 term이며 실제로는 **Arm 관절**을 검사한다. Hand 손가락 속도를 검사하는 종료 항이 아니다.

`object_outside_shelf`는 물체 바닥 원점의 중심 좌표를 검사한다. 물체 반지름이나 목표의 추가 여유 2 cm를 빼지 않는다. 따라서 목표 안전 영역, 성공의 지지 영역, 물체 영역 이탈 종료 경계는 서로 다르다. `shelf_displacement`는 위치 이동만 검사하며 선반 회전 각도 자체에 대한 별도 임계값은 없다.

기존 `shelf_collision` 종료의 구체적인 조건은 다음과 같다. 셋 중 하나만 만족해도 종료하며, Reward의 `near` 게이트는 없다.

```text
norm(shelf_root_velocity_6D) > threshold
OR any(virtual_finger_z − (shelf_root_z + 1.05) < 0.01)
OR virtual_wrist_z − (shelf_root_z + 1.05) < 0.07
```

`threshold=0.1`은 선속도 3D와 각속도 3D를 연결한 6D root 속도 norm의 기준이다. 따라서 선반 선속도만의 0.1 m/s 제한으로 해석하면 안 된다. 높이 상수 0.01 m와 0.07 m는 각각 가상 finger·wrist가 상판 높이보다 위에 유지되어야 하는 최소 여유다. 이 기존 검사는 월드 Z 높이를 사용한다.

### 6.2 성공 조건

`StableGoalSuccess`는 모든 실패 term 이후에 계산한다. 아래 조건이 연속으로 유지되어야 한다.

| 성공 파라미터 | 기본값 | 의미 |
| --- | --- | --- |
| `command_name` | 함수 기본값 `target_goal_pos` | 비교할 목표 위치 Command |
| `position_tolerance` | 0.01 m | 월드 XY 목표 오차가 이 값 **미만**이어야 함 |
| `speed_tolerance` | 0.02 m/s | 월드 XY 물체 선속도 norm이 이 값 **미만**이어야 함 |
| `upright_angle` | 10° = 약 0.17453 rad | 물체 기울기가 이 값 **이하**이어야 함 |
| `hold_time` | 0.3 s | 성공 후보 상태를 끊김 없이 유지할 시간 |
| `surface_height` | 1.05 m | 선반 로컬 상판 높이 |
| `support_tolerance` | 0.01 m | 추정 바닥 최저점과 상판 높이 차이 절댓값의 허용 범위 |
| `half_extents` | `(0.20, 0.50)` m | 지지 영역 계산에 사용하는 상판 반폭 |
| `object_radius` | 0.04 m | 수평 영역 여유와 기울어진 바닥 최저점 계산에 사용하는 실린더 반지름 |
| `failure_terms` | 위 여섯 실패 term | 하나라도 발생하면 성공 후보를 해제하는 실패 목록 |

기본 제어 주기에서는 `ceil(0.3 / 0.02)=15` Step 연속으로 조건을 만족해야 한다. 중간에 조건 하나라도 깨지면 누적 카운터는 0으로 초기화한다. 실패와 성공 후보가 동시에 발생하면 실패를 우선하여 성공 보상을 지급하지 않는다. 해당 환경이 리셋될 때 성공 카운터도 초기화한다.

### 6.3 상판 지지 판정

성공의 지지 상태는 **현재 물체와 선반 pose를 이용한 기하학적 추정**이다. 물체와 선반 사이의 실제 접촉력으로 지지를 확인하지 않는다.

현재 선반 로컬 좌표의 물체 바닥 원점을 `(x, y, z)`, 기울기를 `theta`라고 하면 다음 조건을 검사한다.

```text
abs(x) <= half_extents[0] − object_radius  # 기본 0.16 m
abs(y) <= half_extents[1] − object_radius  # 기본 0.46 m
abs(z − object_radius × sin(theta) − surface_height) <= support_tolerance
```

`object_radius × sin(theta)`는 직립에 가까운 실린더의 바닥 테두리 중 가장 낮은 점이 바닥 원점보다 내려가는 높이다. 수평 영역은 고정 반지름을 이용한 여유 검사이며, 기울어진 실린더 전체 형상의 정확한 투영 영역을 계산하는 방식은 아니다. 지지 판정의 높이 허용 범위 안에서는 작은 떠 있음이나 침투도 허용될 수 있다.

목표 중심의 안전 영역은 기본 `(0.14, 0.44)` m, 성공의 수평 지지 영역은 `(0.16, 0.46)` m, 영역 이탈 실패는 `(0.20, 0.50)` m다. 목표에는 물체 반지름에 추가 여유까지 적용하고, 성공에는 물체 반지름만 적용하며, 실패는 물체 원점이 실제 상판 범위를 벗어나는지를 검사하기 때문이다.

성공은 물체의 최종 상태에 대한 조건이다. 손 자세나 초기 Arm 관절 위치로의 복귀를 요구하지 않는다. 순수 timeout에는 −80 실패 이벤트가 없지만, timeout과 실패가 같은 Step에 발생하면 해당 실패에 대한 −80을 지급한다. Timeout은 성공의 `failure_terms`에도 포함하지 않으므로 제한 시간 마지막 Step에 성공 유지 조건을 완성하면 성공 보상이 발생할 수 있다.

구현: [goal_terminations.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/goal_terminations.py), [terminations.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/sweep.py).

## 설정 변경 위치와 실행

| 변경할 내용 | 위치 |
| --- | --- |
| 스폰 반경·목표 거리·가장자리 여유 | `envs/sweep_omni_envs.py`의 `OmniEventsCfg.object_spawn.params` |
| 보상 가중치·정규화·접근 반경 | `envs/sweep_omni_envs.py`의 `OmniRewardsCfg` |
| 전도·영역 이탈·선반 변위·성공 유지 조건 | `envs/sweep_omni_envs.py`의 `OmniTerminationsCfg` |
| 상속한 물체 속도·Arm 속도·선반 기존 종료 | `envs/sweep_envs.py`의 `TerminationsCfg`. Omni만 조정하려면 파생 Cfg에서 해당 term을 override |
| 질량·마찰 분포 | `mdp/common/realistic_physics.py`의 상수. Realistic Physics 환경도 같은 함수를 사용 |
| 로봇 초기 관절·구동기·Hand open/closed 매핑 | `assets/robot.py` |
| 관측 구성·노이즈·Action scale·제어 주기 | `envs/sweep_envs.py`. Baseline에서 상속하는 설정 |
| 선반 페널티 내부 상수 | `mdp/reward_functions/sweep.py`의 `ShelfCollisionPenalty` |

동일한 반지름·상판 크기·높이가 Event와 Termination에 함께 사용된다. 형상을 바꿀 때는 Scene 형상과 이 값들을 함께 맞춰야 한다. `free_angle`과 전도·성공 각도처럼 연결된 기준도 각 용도를 구분해 조정한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Sweep-Omni-v0 \
  --num_envs 2048 \
  --experiment_name inspire_sweep_omni \
  --run_name centered_spawn_goal15cm \
  --headless
```

`--sweep-direction`은 사용하지 않는다. 새 환경의 방위는 항상 전방향으로 샘플링하며, 이 옵션을 전달하면 오류로 안내한다. PPO 기본 `experiment_name`은 `inspire_sweep_baseline`이므로 위처럼 CLI에서 로그 폴더를 구분할 수 있다.

PPO의 Actor/Critic 입력은 둘 다 `policy`이고, `gamma=0.98`을 포함한 기존 학습 파라미터를 유지한다. 초기 시험 가중치를 적용한 것이며 이 구성 자체가 학습 성공을 보장하는 것은 아니다. 보상 정의와 초기 제안은 [Omni 보상 제안 초안](../../01_plan/environments/OMNI_REWARD_PLAN.md), 실행·패키지 안내는 [패키지 README](../../../../src/inspire_sweep_baseline/README.md)를 참조한다.
