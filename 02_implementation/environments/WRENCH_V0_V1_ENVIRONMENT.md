# Inspire-Wrench-v0 / v1 최종 환경 명세

2026-11-04 추가: v0의 feasibility 파생인 [Wrench-v0_1](WRENCH_V0_1_ENVIRONMENT.md)은 contact 보상 제거·연속 접촉/각도 거리 보상·3cm 미만 alpha=1·40° 고정·4.0–7.5cm 목표 거리를 사용한다. 아래 부모 v0/v1/v2 계약은 보존한다.

2026-11-04 현재 작업트리 기준. 활성 패키지는 `src/inspire_sweep_baseline`이다. 이 문서는 **v0의 전체 환경과 v1의 차이를 함께 설명하는 기준 문서**다. 이후 Hydra override나 코드 수정이 있으면 실행 시점의 설정이 우선한다. 아래 수치는 기본 설정이며, 학습 성능이 검증된 최적값이라는 의미는 아니다.

[환경 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/wrench_envs.py) · [v0 구현 기록](../logs/2026-11-04_wrench_v0_implementation.md) · [v1 구현·후속 변경 기록](../logs/2026-11-04_wrench_v1_osc.md)

## 1. 과업과 두 버전의 관계

선반의 장애물 사이에서 Inspire Hand로 타겟 물체를 목표 XY 위치까지 밀고, 정지 상태를 유지하는 과업이다. Actor는 초기 타겟·초기 장애물 정보와 실행 중 관절·EEF·촉각·F/T 정보를 사용한다. Critic은 추가로 현재 타겟과 실제 활성 장애물 위치를 받는다. Actor에 현재 타겟 위치 GT를 제공하는 환경은 아니다.

**v0는 pose OSC, v1은 wrench OSC다.** `Wrench`라는 환경 이름만으로 v0도 Desired Wrench를 출력한다고 해석하면 안 된다.

| 항목 | v0 | v1 |
| --- | --- | --- |
| Gym ID | `Inspire-Wrench-v0` | `Inspire-Wrench-v1` |
| EnvCfg | `WrenchEnvCfg(ManagerBasedRLEnvCfg)` | `WrenchV1EnvCfg(WrenchEnvCfg)` |
| Runtime | `WrenchEnv(ManagerBasedRLEnv)` | v0와 동일 |
| Scene | 독립 `WrenchSceneCfg` | v0와 동일 |
| Arm 명령 | 상대 위치·RPY 6D | Desired Wrench 6D |
| OSC 제어점 | `axia80_link`에서 +Z 142.7mm의 EEF | `axia80_link` 중심 |
| Arm action-rate | 클리핑 전 raw 출력 차이 | 목표 범위로 정규화한 Desired Wrench 차이 |
| PPO 실험명 | `inspire_wrench_v0` | `inspire_wrench_v1` |

v0는 Revision-Test-v2의 기능을 계승하지만 기존 EnvCfg·Runtime·Scene·PPO 설정 클래스를 상속하지 않는다. 자산 spawner, MDP 함수, `RevisionGoalCommand`, `RevisionModel` 등 계산 구현은 재사용한다. v1은 v0를 직접 상속하며 Arm 제어와 그에 대응하는 action-rate 보상만 바꾼다. Hand, 관측, 물체 배치, 다른 보상, 성공·실패, 커리큘럼, PPO 수치는 같다.

## 2. 시간·장면·좌표 기준

| 설정 | 값 |
| --- | --- |
| 기본 병렬 환경 수 / 간격 | 2048 / 2.5m |
| 물리 timestep | 0.01s, 100Hz |
| decimation / 정책·보상 timestep | 2 / 0.02s, 50Hz |
| 최대 episode | 10s, 500 policy steps |
| 물리 객체 | 타겟1 + 장애물 후보9 = 10개 |
| 최대 활성 장애물 | Gray4 + White5 |
| 장애물 관측 슬롯 | 16개; 실제 물리 객체 수와 다름 |
| 선반 초기 위치 | 환경 원점 기준 (-0.7, 0, 0)m |
| 선반 작업면 | shelf-local Z=1.05m, XY 반폭 (0.20, 0.50)m |
| 선반 질량 | 100kg |
| 물리 복제 | `replicate_physics=False` |
| Arm actuator PD | stiffness=0, damping=0; OSC가 effort를 지정 |
| Arm simulator 속도 제한 | 관절 순서대로 (2,2,2,4,4,4)rad/s |

로봇은 기존 Arm–Axia80–Inspire 조립 자산을 사용한다. Hand 관절 위치 제어는 별도로 유지한다. EEF는 손목 센서 중심에서 센서 local +Z 방향으로142.7mm 이동한 가상 프레임이다. 손가락·손목 높이 판정에는 별도의 `finger_frame`, `wrist_frame`을 쓴다. 따라서 **EEF 높이, sensor 높이, wrist clearance는 서로 다른 값**이다.

위치는 world, robot root, shelf-local을 구분한다. 목표 거리·성공은 world XY 거리이고 속력은 world 3D 선속력이다. Actor의 위치 관측은 robot-root 좌표다. 물체 낙하 판정은 현재 shelf 프레임에서 실제 scaled bbox의 가장 낮은 점을 사용한다.

PhysX 주요 설정은 bounce threshold0.2, friction correlation distance0.00625, found/lost aggregate pairs `2**25`, total aggregate pairs `16*1024*16`, max rigid patches `5*2**17`이다. 이것은 현재 설정값이며 대규모 GPU 동시 접촉에서의 충분성은 별도 검증 대상이다.

## 3. 형상·물성·배치 랜덤화

근거: [Scene](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/wrench.py), [spawner](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/revision_spawners.py), [Event 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/events/wrench.py), [reset 구현](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/wrench.py).

### 3.1 최초 생성 때 고정하는 형상

타겟은 물리 슬롯0 `mass_cylinder`의 원통이며, 기본 반지름0.04m·높이0.10m에 균일 scale U(0.9,1.1)을 적용한다. 따라서 반지름3.6~4.4cm, 높이9~11cm다. 나머지9개 슬롯은 다음8종에서 생성 시 종류를 선택하고 각각 균일 scale U(0.9,1.1)을 한 번 적용한다.

| 종류 | 기준 |
| --- | --- |
| cylinder | 반지름4cm·높이10cm |
| cube, mug, bottle | 절차적 mesh 생성의 기준 치수 (0.06,0.08,0.10)m; 각 형상의 실제 bbox를 사용 |
| `003_cracker_box`, `004_sugar_box` | NVIDIA YCB Axis_Aligned, 기준 size_fraction0.9 |
| `005_tomato_soup_can`, `002_master_chef_can` | NVIDIA YCB Axis_Aligned, 기준 size_fraction0.9 |

형상과 scale은 각 환경·슬롯별로 고정된다. reset에서 종류나 크기를 다시 뽑지 않는다. 시각 mesh와 collider의 크기를 함께 적용하고, 실제 scaled bounds를 저장해 배치·바닥 정렬·낙하 판정에 쓴다. 기준 geometry의 재사용과 각 환경 rigid body의 상태 독립성을 구분한다.

### 3.2 startup에 한 번 샘플링하는 물성

[물성 분포](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/realistic_physics.py)의 질량은 `1.5 * clamp(N(0.365,0.0675²), 0.230,0.500)`kg이다. 최종 범위0.345~0.750kg, 중심값0.5475kg다. **환경당 하나의 질량 샘플을 그 환경의 타겟·장애물에 공통 적용**한다. 물체별 독립 질량 샘플이 아니다. 관성은 각 형상의 원래 inertia/mass 비율을 유지해 새 질량으로 조정한다.

마찰은 아래 역할별4096개 Gaussian quantile bucket에서 샘플링한다. 음수는0으로 제한한다. static/dynamic은 독립 permutation으로 상관을 줄인 유한 pool이며 환경별·역할별 선택한다.

| 역할 | 정지마찰 평균 / 표준편차 | 동마찰 평균 / 표준편차 |
| --- | --- | --- |
| Floor | 0.315 / 0.051 | 0.252 / 0.041 |
| Object | 0.315 / 0.040 | 0.252 / 0.032 |
| Tool(Hand) | 0.585 / 0.145 | 0.468 / 0.116 |

같은 환경의 해당 역할 collider들은 같은 샘플을 공유한다. Arm/Axia의 다른 material 값과 restitution 등은 기존 값을 유지한다. v0/v1에서는 이 함수를 **startup**에 실행하므로 episode 사이에는 물성이 고정된다. 함수 이름에 `episode`가 포함되어 있어도 매 reset 랜덤화라는 뜻은 아니다.

### 3.3 타겟·목표 샘플링

타겟 XY는 선반 중심 반지름2cm 원판 안에서 면적 균등하게 뽑는다. 방향은 shelf-local ±X 주변의 Dead Zone을 제외한 두 각도 구간에서 뽑는다. 목표 거리의 상한은15cm이며, 타겟 실제 footprint와 선반 가장자리2cm 여유를 고려해 경계까지의 거리로 줄인다. 최소5cm의 가능한 방향을 선택한다. 따라서 거리를5~15cm에서 균등 추출하는 방식은 아니다. 방향 후보32개와 ±Y fallback을 사용한다.

목표는 reset 때 초기 타겟 위치에 샘플링한 변위를 더해 고정한다. Command의7D는 world 목표 XYZ와 초기 타겟 quaternion이며, 성공/거리 보상에는 XY만 사용한다. `resampling_time_range=(1e6,1e6)`이므로10초 episode 중간에 목표를 바꾸지 않는다.

### 3.4 RED / Gray / White 배치

[OBB 배치](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/bbox_scene_layout.py)는 회전된 bbox footprint와 최소 물체 간격20mm, board wall margin5mm를 검사한다. 타겟 실제 shelf yaw는0이고 장애물에는 배치 결과 yaw를 적용한다.

- **RED:** 타겟의 시작→목표 swept footprint와 손목 진입 extrusion을 포함하는 금지 영역. margin23mm로 기존3mm보다20mm 확장했다.
- **Gray:** 확장된 RED의 외곽65mm 영역과 타겟 후방의160×220mm 사각형을 포함한다. RED와 겹치는 부분은 제외한다.
- **후방 사각형:** 크기를 유지한 채 타겟→목표 반대 방향으로20mm 후퇴했다. 사각형 자체를 RED로 바꾸지 않았다.
- **White:** RED·Gray 바깥의 허용 영역에 배치한다.

배치 검색은 후보32개, restart4회, pass2회를 사용한다. 모든 요청 수를 배치하지 못하면 best-count 결과를 보존하며 객체를 겹치게 강제로 넣지 않는다. `actual`은 실제 Gray/White 수, `complete`는 요청 수 충족 여부다. 따라서 커리큘럼 표의 개수는 **요청 수**다.

활성 물체 root Z는 `1.05 - scaled_bounds_min_z`로 계산하여 실제 바닥을 작업면에 맞춘다. 비활성 물체는 shelf-local Z=`50+2*slot`m에 분리 주차하고 중력을 끈다. 활성 mask에서 제외된 물체는 관측·객체 비용·낙하 판정의 대상으로 삼지 않는다.

현재 코드로 생성한 [4단계 배치 이미지](../../../../outputs/wrench_layout_preview/layout_samples.png) · [타겟 주변 확대](../../../../outputs/wrench_layout_preview/layout_zoom.png) · [콜라이더 크기 도감](../../../../outputs/wrench_layout_preview/collider_atlas.png) · [재현 코드](../../../../outputs/wrench_layout_preview/generate.py) · [출처·검증 설명](../../../../outputs/wrench_layout_preview/README.md).

![실제 크기 collider와 현재 Wrench 배치 규칙의4단계 샘플](../../../../outputs/wrench_layout_preview/layout_samples.png)

채운 윤곽은 실제 크기 collider의 XY 투영, 진한 점선은 배치 OBB다. 배경은 point membership이며 후보 중심의 허용 공간이 아니다. Gray 배치는 OBB가 Gray와 일부 교차하면 되고 전체가 Gray 안에 있을 필요는 없다. 후방 사각형은 갈색 점선이 현재, 옅은 점선이20mm 후퇴 전이다.4개 샘플은 같은 형상/scale의 환경에서 각각 현재 단계 bank의 후보0을 선택했다. 시뮬레이터를 실행한 화면이 아니며 YCB 크기는 기존 USD 실측 자료를 사용했다.

### 3.5 초기화와 reset의 작업 분리

| 시점 | 수행 내용 |
| --- | --- |
| Scene 생성 / prestartup | 형상·scale 결정, geometry metadata·scaled bounds 준비 |
| startup | 환경별 실제 형상에 대해9개 커리큘럼 상태×16개 배치 bank 생성; material buffer 준비와 물성 샘플링 |
| reset | 기본 scene 상태 복원; 현재 단계의 bank 후보 하나를 환경별 균등 복원추출; 물체 pose·속도·gravity·mask 복원; 목표와 초기 관측/noise/visibility/swap 갱신 |
| step | 물리 실행, 센서, 보상·종료·관측; OBB 후보 검색 없음 |

`layout_bank_size=16`, `layout_build_batch_size=256`. 2048환경에서 bank 자체는 약54.84MiB이며 생성 임시 tensor는 별도다. 같은 환경의 같은 단계는 유한16개 레이아웃을 반복 사용한다. 환경별 형상·물성 다양성과 episode별 무한 신규 배치를 혼동하면 안 된다. reset seed는 후보 선택 등의 RNG를 재설정하고 기존 bank·물성을 재생성하지 않는다. 커리큘럼 조합을 바꾸려면 `LAYOUT_STAGES`도 함께 맞춰야 한다.

## 4. 관측: Actor와 Critic

근거: [관측 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/wrench.py), [장애물 관측](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/revision.py), [Hand·noise·action 관측](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/final.py).

### 4.1 공통 policy 그룹57D

| 구간 | 항목 | 의미·단위·갱신 |
| --- | --- | --- |
| [0:6] | Arm joint_pos | 실제6관절 각도rad, default pose 차감 없음 |
| [6:12] | Arm joint_vel | 실제6관절 각속도rad/s |
| [12:14] | Hand configuration | 실제12관절에서 역산한 flexion/opposition2D, [0,1] |
| [14:21] | EEF pose | robot-root 기준 XYZ(m)+quaternion(w,x,y,z), 실시간 |
| [21:24] | 초기 타겟 XYZ | reset snapshot, root 기준; 축별 U(-0.01,0.01)m bias를 episode마다 샘플링 |
| [24:26] | 초기 목표 polar | 초기 타겟→목표 root 변위의 거리와 각도; 각도는 `atan2(-dy,dx) mod 2π` |
| [26:34] | 이전 실행 action8D | `tanh(action_manager.action)`; policy가 다음 action을 계산할 때 직전 실행 명령에 해당 |
| [34:51] | tactile17D | 투영된 촉각 접촉 bit, threshold0.01N, 각 bit 독립1% flip noise |
| [51:57] | compensated wrist wrench6D | **EEF 원점·EEF 축**의 보정 wrench; force N, moment Nm |

초기 타겟 bias는 매 관측 독립 jitter가 아니다. 관절·EEF에는 이 설정에서 별도 noise를 추가하지 않는다. F/T 관측에는 force 표준편차0.05N, moment0.005Nm의 독립 zero-mean Gaussian noise를 더한다. 손목 관측은 downstream Hand의 중력·관성 support를 제거한 값이며, reset 직후 stale 샘플은 유효 데이터로 쓰지 않는다. 촉각과 F/T는 동일 step의 캐시를 재사용한다.

### 4.2 장애물64D와 비대칭 정보

각 슬롯은 `[presence, x, y, z]`이며16×4=64D다. 타겟은 장애물 슬롯에서 제외하고 비보고 슬롯은 정확히0으로 채운다.

| 그룹 | Actor `obstacles` | Critic `critic_obstacles` |
| --- | --- | --- |
| 위치 | 초기 reset snapshot, 이후 고정 | 매 관측 실제 현재 위치 |
| 대상 | 초기 가시성에 의해 보고된 활성 장애물 | 실제 배치된 모든 활성 장애물 |
| 가시성 | scaled footprint 기반 occlusion, threshold0.35 | 필터 없음 |
| visibility bit 오류 | 실제 활성 장애물에 한해1% flip | 없음 |
| 좌표 noise | reset 때 축별±1cm 균등 noise | 없음 |
| 순서 | 보고된 root Y 내림차순 후 인접 쌍10% swap, reset 때1회 | 같은 정렬·swap을 매 관측 적용 |

Critic도 인접 swap 때문에 순서는 확률적일 수 있으나 위치값에는 noise가 없다. 비활성 주차 슬롯은 가시성 flip으로도 생성되지 않는다. 움직이거나 떨어진 활성 장애물은 reset 전까지 Critic 대상에 남는다.

Actor 원시 입력은 `policy57 + obstacles64 = 121D`. Critic은 `policy57 + privileged3 + critic_obstacles64 = 124D`이며 privileged3은 noise 없는 현재 타겟 root XYZ다. Critic도 policy 그룹의 초기 타겟 bias와 촉각/F/T noise를 공유한다. Critic 전체가 noise-free인 것은 아니다.

## 5. v0 액션과 pose OSC

근거: [Action 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/actions/wrench.py), [pose Action 구현](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/action_functions/contact_sweep_clutter_fusion_holding_osc.py).

액션은 Arm6D + Hand2D다. Arm 앞3축은 상대 XYZ, 뒤3축은 상대 RPY다. 위치 scale0.03m, 회전 scale0.15rad를 곱하고 RPY→quaternion→axis-angle로 변환하여 pose_rel OSC에 전달한다. 기본 설정에서 별도 Arm 정규화 clamp를 지정하지 않으므로 scale0.03을 하드 최대 이동3cm로 해석하면 안 된다. task frame을 별도로 지정하지 않아 로봇 base 기준의 상대 pose 명령이다. 제어점은 EEF offset을 포함한다.

| OSC 파라미터 | v0 |
| --- | --- |
| target_types / impedance_mode | `["pose_rel"]` / `fixed` |
| motion_control_axes_task | (1,1,1,1,1,1) |
| contact_wrench_control_axes_task | (0,0,0,0,0,0) |
| motion_stiffness_task | (100,100,100,50,50,50) |
| motion_damping_ratio_task | (1,1,1,1,1,1) |
| inertial_dynamics_decoupling | True |
| partial_inertial_dynamics_decoupling | False |
| gravity_compensation / nullspace_control | True / none |
| effort_limit_scale | 1.0; 실제 joint effort limits로 clamp |

비유한 effort 행은0으로 처리하고 포화 상태를 기록한다. 물리 substep마다 동역학·Jacobian·EEF 상태를 갱신하여 effort를 계산한다.

Hand 첫 채널은 전체 flexion, 두 번째는 thumb opposition openness다. 입력을 [0,1]로 clamp하며0은 닫힘,1은 열림이다. `closed + openness*(open-closed)`로12관절 목표를 만든다. reset 시 Hand Action의 내부 목표는 열린 상태로 초기화된다.

## 6. v0 보상15항

근거: [보상 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/wrench.py), [거리·Hold·진입·wrench-change](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/revision.py), [객체 비용](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/contact_sweep_clutter_fusion.py).

일반 항의 step 보상은 **`weight * raw_value * step_dt`**다. 아래의 순간 진입·성공 및 reaching은 함수에서 dt를 나눠 이 적분을 상쇄한다. 음수 weight 항은 비용이며 아래 raw는 비음수다. `d`는 타겟–목표 XY 거리, `v`는 타겟3D 선속력이다.

공통 초과 비용을 `E(x,b)=min(100, 0.5*expm1(2*max(x-b,0)))`로 표기한다. 구현은 overflow 전에 exponent를 제한한다.

| term | weight | raw 계산·조건 |
| --- | ---: | --- |
| target_reaching | 30 | EEF–현재 타겟3D 거리에서10cm를 뺀 양수부의 **역대 최소값 개선량 / dt**. 후퇴·같은 거리 재방문에는 지급 없음 |
| target_goal_distance | 3.7 | `exp(-d/0.05)`, 공통 EEF 높이 gate 필요 |
| target_goal_hold | 10 | 아래 Smoothstep, 정상 타겟 상태와 높이 gate 필요 |
| target_contact | 1.45 | fresh·finite 타겟–Hand 접촉 합력 크기≥0.01N AND 높이 gate. 목표 점유만으로 지급하지 않음 |
| robot_action_rate_penalty | -1 | `0.03*min(sum(Δraw_arm²),100) + 0.03*min(sum(Δraw_hand²),100)` |
| robot_joint_velocity_penalty | -1 | `0.03*min(sum(qdot_arm²),100) + 0.01*min(sum(qdot_hand²),100)` |
| object_tilt_penalty | -30 | 활성 타겟·장애물 각각 `clip((angle-5°)/(0.9rad-5°),0,1)²` 합 |
| obstacle_displacement_penalty | -150 | 활성 비타겟의 초기 대비3D 변위 제곱을 합산한 후0.04로 제한 |
| object_acceleration_penalty | -0.05 | 활성 물체별 `E(norm(COM linear acceleration),15)` 합. 각 물체 상한100 |
| shelf_penalty | -1 | `3*collision/dt + 0.5*continuous_shelf_cost`, 아래 상세 |
| obstacle_contact_penalty | -0.05 | 비타겟 장애물–Hand의 world 접촉 힘 벡터를 합한 크기에 `E(force,50)`. stale이면0 |
| target_goal_first_entry_bonus | 25 | 최초 `d<0.03` 진입 때 `exp(-(max(v-0.01,0)/0.02)²)/dt` |
| target_goal_success_bonus | 75 | 성공 termination 발생 시 `1/dt`, 실제 지급+75 |
| wrist_wrench_change_penalty | -0.1 | EEF 보정 F/T의 힘·모멘트 **크기 변화** 기반0~1 비용, 아래 상세 |
| target_speed_penalty | -5 | `E(v,free_speed)`; free_speed만 커리큘럼으로 변경 |

### 6.1 높이 gate와 Hold

거리·Hold·접촉 보상은 EEF world Z가 **초기 선반 Z+1.05+0.12m 미만**일 때만 지급한다. 정확히12cm는 gate 밖이다. 실제 물체 높이에 따라 움직이는 상한이 아니며, 초기화 때 `contact_height_limit`도 같은 값에 맞춘다.

Hold는 `u=clip((d-0.025)/0.010,0,1)`에 대해 `1-3u²+2u³`이다. 2.5cm 이내1, 3.5cm 이상0, 중간은 부드럽게 감소한다. 속도 감쇠는 없다. 정상 상태란 유한 위치·속도·목표·기울기, 활성 타겟, shelf-local root |X|≤0.16m·|Y|≤0.46m, bbox 바닥1.04~1.07m, 선반 상방 대비 기울기≤0.9rad를 뜻한다.

최초 진입 보상은 높이 gate가 없다. 최초 진입의 속도가 커서 보상이 거의0이어도 진입 기회는 소진되며 다음 재진입 때 다시 지급하지 않는다. 최초 진입의 `d<3cm`와 성공의 `d≤3cm`는 경계가 다르다.

### 6.2 객체·선반·wrench 비용의 해석

객체 가속도는 정책 step 간 속도 차분이 아니라 **직전 physics step의 PhysX world COM 선가속도**다. 가속·감속 모두 같은 norm으로 계산하며 reset/활성화 직후 첫 표본은 억제한다. 장애물 접촉 비용은 힘 벡터를 합산한 후 norm을 취하므로 접촉별 크기 합과 다르다.

Shelf의 collision은 종료 함수와 같은 선반6D root velocity norm>0.1 또는 wrist clearance<3cm 조건이다. 해당 step의 이벤트 비용은-3이며, 선반 위치 변위>5cm만으로 collision 이벤트 비용을 만드는 것은 아니다.

연속 shelf cost는 다음과 같다. `moved`는 선반 초기 위치와의 거리 + 6D root velocity norm이0.005를 넘으면1이다. 표면 proxy는 live shelf root Z+1.06m이며, 이 proxy와 EEF의3D 거리가20cm 미만일 때 두 가상 finger의 `clip(1-height/0.02,0,1)` 합과 wrist의 `clip(1-height/0.08,0,1)`을 더한다. 반환값은 `moved + near*(finger_cost+wrist_cost)`다. 이 부분만 weight와0.5·dt가 적용된다. 작업면1.05m와 연속 비용 proxy1.06m를 구분한다.

Wrench-change는 `ΔF=abs(norm(F_now)-norm(F_prev))`, `ΔM=abs(norm(M_now)-norm(M_prev))`이다. 힘20N, 모멘트2Nm까지 무료이며 `s=clip(max((ΔF-20)/30,(ΔM-2)/3),0,1)`에 대해 `(exp(3s)-1)/(exp(3)-1)`을 반환한다. 힘50N 또는 모멘트5Nm의 크기 변화에서 포화한다. **벡터 차이의 norm도, 초당 변화율도 아니다.** reward budget 제한은 없고 raw 상한1이다. 관측 noise를 더하기 전 EEF 보정값을 사용하며 첫 유효 표본과 stale 이력은 비용을 만들지 않는다.

## 7. 커리큘럼

기준은 PPO learning iteration이다. 환경 step 수나 episode 수가 아니다. runner가 `set_learning_iteration()`을 통해 현재 절대 iteration을 전달한다. 값은 해당 iteration에서 다시 계산되며 배치 변화는 이후 reset에서 적용된다.

| iteration | ±X 제외 반각 | Gray / White 요청 |
| --- | ---: | ---: |
| 0~9999 | 30° | 3 / 3 |
| 10000~11999 | 25° | 3 / 4 |
| 12000~12999 | 25° | 4 / 4 |
| 13000~13999 | 20° | 4 / 4 |
| 14000~15999 | 20° | 4 / 5 |
| 16000~18999 | 15° | 4 / 5 |
| 19000~21999 | 10° | 4 / 5 |
| 22000~24999 | 5° | 4 / 5 |
| 25000 이후 | 0° | 4 / 5 |

Dead Zone은10000에서 처음5° 줄고 이후3000마다5°씩 줄어든다. 제외 구간이 작아져 이전에 제외했던 목표 방향도 허용된다. Gray 외곽 padding65mm는 커리큘럼 대상이 아니다.

타겟 속도 비용의 free_speed는 별도 일정이다. `scheduled_value`는 구간 내250 iteration 단위 계단 보간을 사용한다.

| iteration | free_speed (m/s) |
| --- | ---: |
| 0~499 | 0.1000 |
| 500~749 | 0.0900 |
| 750~999 | 0.0775 |
| 1000~1249 | 0.0650 |
| 1250~1499 | 0.0525 |
| 1500~1749 | 0.0400 |
| 1750~1899 | 0.0275 |
| 1900 이후 | 0.0200 |

이는 속도 **보상 비용의 무료 구간**이다. 성공 속력0.005m/s와 과속 종료1m/s는 바뀌지 않는다.

## 8. 종료·성공과 보상 지급 순서

근거: [종료 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations/wrench.py), [성공 타이머](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/wrench.py).

| term | 판정 | time_out |
| --- | --- | --- |
| object_fall_or_tilt | 활성 물체 중 bbox 최저점 비유한, shelf-local 바닥<1.04m, 또는 기울기≥0.9rad 하나라도 성립 | False |
| target_speed | 타겟 world 3D 선속력>1m/s | False |
| shelf_failure | 선반6D root velocity norm>0.1, wrist clearance<0.03m, 초기 대비 선반 위치 변위>0.05m 중 하나 | False |
| arm_joint_velocity | Arm 어느 관절이든 abs(qdot)>5rad/s | False |
| target_goal_success | `d≤0.03m AND v≤0.005m/s`를 연속3초 만족, 같은 step 선행 실패 없음 | False |
| target_goal_miss_at_timeout |10초 time limit이면서 success 아님 | True |

선반6D 속도 norm은 선속도3축과 각속도3축을 그대로 합친 벡터의 norm이라는 현재 코드 계약이다. 단순 선속력0.1m/s 판정으로 설명하면 부정확하다. `check_fingers=False`여서 finger clearance는 실패 조건에 포함되지 않지만 연속 shelf 비용에는 포함된다.

성공은 정책 timestep0.02s에서150개 연속 표본이 필요하다. 중간 조건 이탈이나 비유한 거리·속도는 해당 타이머를0으로 되돌린다. 같은 step 재조회로 중복 증가하지 않고 부분reset에서는 선택 행만 초기화한다. 별도 각속도·EEF 높이 gate는 성공에 없다. 다만 선행 실패 판정이 동시에 있으면 성공을 억제한다.

네 실패 term → success → timeout 순으로 계산한다. 같은 step 성공과 시간 제한이 겹치면 성공을 우선한다. 보상은 종료 판정 후 reset 전에 계산하므로 성공 전이에 정확히+75가 지급된다. timeout 때3cm 안에 있다는 이유만으로 성공 보상을 지급하지 않는다. 실패와 timeout의 동시 발생은 기존 Manager 동작을 따른다.

## 9. PPO와 실행·로그

[Runner 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/wrench_ppo_cfg.py)은 `CurriculumOnPolicyRunner`, rollout36 steps/env, max_iterations90000, save_interval50이다. 기본2048환경이면 iteration당73728 transitions다.

Actor와 Critic은 각각 독립 장애물 encoder64→32(ReLU)→16 embedding을 사용한다. Actor MLP 입력은57+16=73D, Critic은57+3+16=76D다. 두 MLP hidden은256/128/64, ELU, observation normalization=False다. Actor Gaussian 초기 std=1.0이다.

| PPO 항목 | 값 |
| --- | --- |
| gamma / lambda | 0.98 / 0.95 |
| learning rate / schedule | 0.001 / adaptive |
| desired KL | 0.02 |
| epoch / minibatch | 8 / 4 |
| clip / entropy coefficient | 0.2 / 0.005 |
| value loss coefficient / clipped value loss | 1.0 / True |
| max gradient norm | 1.0 |

Workspace 루트에서 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-v0 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-v1 --num_envs 2048 --headless
```

보상은 `Episode_Reward/<term>`, 종료는 `Episode_Termination/<term>`으로 확인한다. 특히 success, shelf_failure, object_fall_or_tilt와 `Metrics/obstacle_actual_gray`, `Metrics/obstacle_actual_white`, `Metrics/layout_complete`를 구분해서 본다. 요청 장애물 수와 실제 배치 수가 다를 수 있다. 기존 runtime의 목표 오차·힘/모멘트 통계도 유지한다. 로그 해석 시 v1의 OSC feedback은 sensor 기준이고 기존 관측·보상·telemetry는 EEF 기준이라는 점을 구분한다.

## 10. v1의 변경: F/T 센서 기준 closed-loop wrench

### 10.1 정책 출력과 설정

v1에서는 앞6개 행동이 현재 F/T sensor 축의 `[Fx,Fy,Fz,Mx,My,Mz]` 목표다. Arm raw를 [-1,1]로 clamp하고 `(100,100,100,5,5,5)`를 곱한다. 따라서 축별 목표 범위는±100N/±5Nm다. 정책 자체는 여전히 정규화 좌표를 출력하며 **Action 처리 후 값이 물리 단위 Desired Wrench**다.

| OSC 설정 | v1 최종값 |
| --- | --- |
| target_types / impedance_mode | `["wrench_abs"]` / fixed |
| motion_control_axes_task | (0,0,0,0,0,0) |
| contact_wrench_control_axes_task | (1,1,1,1,1,1) |
| contact_wrench_stiffness_task | (0.2,0.2,0.2,0.2,0.2,0.2) |
| inertial / partial inertial decoupling | False / False |
| gravity compensation / nullspace | True / none |
| body / offset / task frame path | axia80_link / None / None |
| wrench_scale | (100,100,100,5,5,5) |
| normalized_wrench_limit | 1.0 |
| commanded_wrench_limit | (120,120,120,6,6,6) |
| effort_limit_scale | 1.0 |

사용자 제공 센서 계측 범위150N/8Nm를 축별 범위로 해석하고 여유를 두었다. 피드백 보정 후에도 축별±120N/±6Nm로 제한한다. 이것은 합력 norm 제한이나 실제 충격력 제한이 아니다. tool 중력·관성 보정 전 센서 원시 하중도 이 값으로 보장되지 않는다. 실제 축별·복합하중 정격과 추종 안정성은 미검증이다.

### 10.2 제어식과 구현 근거

[순수 계산 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/wrench_control.py)와 [sensor Action](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/action_functions/wrench.py)은 다음 순서다.

```python
w_des_s = clamp(raw_arm, -1, 1) * [100, 100, 100, 5, 5, 5]
w_cmd_s = clamp(w_des_s + 0.2 * (w_des_s - w_current_s),
                -[120, 120, 120, 6, 6, 6], [120, 120, 120, 6, 6, 6])
tau = J_sensor.T @ w_cmd_s + gravity_joint
tau = clamp(tau, -joint_effort_limits, joint_effort_limits)
```

위 코드는 계산 순서를 나타낸 의사코드다. gain0.2는 N/N 및 Nm/Nm의 무차원 비례 게인이며 pose stiffness가 아니다. 측정0에서 최대 목표는 보정 후120N/6Nm가 된다. 반대 방향의 측정 때문에 오차가 더 커져도 명령 clamp가 적용된다. 중력 보상은 wrench clamp 다음에 joint 공간에서 한 번 더한다.

참고한 로컬 원본은 [UR10 Reach 예제](../../../../IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/reach/config/ur_10/ur10_osc_reach_env_cfg.py), [OSC closed-loop 테스트](../../../../IsaacLab/source/isaaclab/test/controllers/test_operational_space.py), [OSC 튜토리얼](../../../../IsaacLab/scripts/tutorials/05_controllers/run_osc.py)이다. UR10 예제의 effort 처리와 wrench-only 테스트의 force P gain0.2를 참고했다. 모멘트 gain0.2는 로컬6축 확장의 초기값이며 안정성 튜닝 결과가 아니다.

현재 설치된 기본 Isaac OSC는 `current_ee_force_b`3D만 받아 moment 오차를 실측 피드백하지 않는다. 따라서 `OperationalSpaceControllerCfg`를 사용하되 실제6축 계산은 로컬 `SensorFrameWrenchAction`에서 수행한다. 기본 OSC에 config만 바꿔 완전한6축 closed-loop가 된 것으로 설명하지 않는다. IsaacLab 소스·USD·센서 topology는 수정하지 않았다.

### 10.3 F/T 기준점·측정 부호·주기

제어점과 Jacobian 원점은 sensor housing 중심 `axia80_link`다. Jacobian 선형·각 블록을 **현재 sensor 축**으로 회전한다. EEF +142.7mm offset을 적용하지 않고 robot root 원점까지 힘을 이동시키는 불필요한 moment 항도 만들지 않는다. 현재 자산에서 sensor body COM과 housing 중심은 일치한다.

원시 wrench는 기존 `axia80_measurement_joint`의 child `inspire_base_link`에서 읽는다. 현재 시뮬레이션 joint plane은 sensor 중심의 local +Z12.7mm에 있으므로 이 고정 offset만 sensor 중심으로 운반한다. `PureWrenchReader`에 sensor pose를 전달하고 downstream Hand의 중력·관성 support를 제거한다. 반환 필드명 `pure_eef`는 과거 이름이지만 이 호출에서는 **sensor 기준**이다.

부호는 로봇이 환경에 가하는 wrench 기준이다. 실물 F/T가 환경이 tool에 가하는 힘 부호를 보고하면 adapter에서 반전해야 한다. 실제 reporting frame이 다르면 센서 내부의 고정 좌표변환이 필요하다.12.7mm는 시뮬레이션 자산 값이며 실물 센서의 reporting frame 치수를 입증한 값이 아니다.

정책 목표는50Hz로 바뀌고 feedback은100Hz로 갱신한다. 정책 관측의 noisy·cached EEF wrench를 제어 입력으로 쓰지 않고 전용 reader에서 별도 sensor 측정을 읽는다. reset 직후 첫 substep은 이전 물리 샘플이므로 P 보정을 끄고 feedforward+gravity만 적용한다. 이후 fresh 샘플부터 P 보정을 켠다.

pose holding, 적분·미분 wrench 제어, 저역통과 필터는 없다. 목표 wrench0은 위치 유지 명령이 아니다. `current_wrench_s`로 controller feedback, `processed_actions`로 Desired Wrench, `joint_efforts`로 실제 제출 effort를 확인한다.

### 10.4 v1 action-rate 페널티

v0의 클리핑 전 raw 차이 대신 **Desired Wrench를 정책 목표 범위로 나눈 값**을 비교한다. 힘은100N, 모멘트는5Nm가 정규화1에 해당한다. 현재·이전 값을 각각 정규화한 뒤 차이를 계산한다.

```python
u_now  = clip(raw_now_arm,  -limit, limit) / limit
u_prev = clip(raw_prev_arm, -limit, limit) / limit
cost = 0.03 * min(sum((u_now - u_prev)**2), 100)
cost += 0.03 * min(sum((raw_now_hand - raw_prev_hand)**2), 100)
```

`limit=normalized_wrench_limit`이며 기본1이다. 물리 Desired Wrench와 목표 범위 양쪽에 같은 `wrench_scale`이 곱해져 상쇄되므로 위 식이 동일하다. measured wrench나120N/6Nm의 보정 후 명령을 평가하지 않는다.

- Fx 0→50N과 Mx 0→2.5Nm는 각각 정규화 변화0.5, raw 비용0.0075다.
- raw2→3은 같은 최대 Desired Wrench를 만들므로 Arm 비용0이다.
- 한 축 -1→+1은 비용0.12,6축 모두 반전하면0.72다(dt·weight 적용 전).
- Hand는 기존 raw 방식, term weight=-1·계수0.03·dt 적용도 유지한다.
- ActionManager의 prev_action을 사용하므로 별도 이력 buffer 없이 기존 부분reset 규칙을 따른다.

기존 `wrist_wrench_change_penalty`는 그대로 EEF 보정 측정값의 크기 변화를 평가한다. 두 페널티는 각각 **목표 명령의 변화**와 **측정된 접촉 반응의 변화**를 다룬다.

### 10.5 v1에서 보존하는 부분

EEF 관측·높이 보상·촉각/F/T 관측 noise, Scene·물성·배치 bank, Hand action, 나머지14개 보상, 모든 종료·성공 타이머, 커리큘럼, PPO 수치는 v0와 같다. v1의 actor 입력 F/T는 여전히 EEF 기준이며 controller의 sensor 기준 F/T와 구분한다. PPO experiment_name만 v1로 분리한다. v0 checkpoint는 행동 의미가 달라 v1의 동등한 정책으로 간주할 수 없다. 이전 작은 wrench 스케일의 v1 checkpoint도 현재 scale에서는 동일한 행동을 만들지 않는다.

## 11. 검증 결과와 한계

이 문서는 코드·설정 대조로 작성했으며 문서 작성 과정에서 환경 실행 코드를 변경하지 않았다. 기존 작업 기록의 검증을 다음과 같이 구분한다.

| 검증 | 결과·범위 |
| --- | --- |
| v0 구현 당시 CPU 회귀 |82 passed, CUDA4 skipped |
| v1 최초 구현 CPU 회귀 |80 passed; frame·부호·6축 feedback·기존 환경 격리 등 |
| v1 명령 제한 후속 CPU |43 passed; 양/음 command clamp와 gravity 순서 포함 |
| v1 action-rate 후속 CPU |44 passed; 포화 목표·정규화·Hand 보존·구성 차이 포함 |
|2048환경 크기 CPU 배치 비교 |기존 OBB 검색 약4.04s, bank선택 평균0.000234s; 전체 reset/collection 시간이 아님 |
| 실제 GPU rollout·학습 |당시 NVIDIA 드라이버 사용 불가로 미수행 |
| 실물 F/T deploy·접촉 안정성 |미검증 |

따라서 collection1~2초 달성, shelf termination 감소, 최종 성공률 개선, 유한 bank 반복의 학습 영향, 현재 wrench scale/gain의 접촉 안정성을 입증한 상태가 아니다. GPU 확인용 `_wrench_probe.py --version v0|v1`는 준비되어 있으나 준비된 명령과 실제 수행한 검증을 구분한다.

```bash
python src/inspire_sweep_baseline/tests/_wrench_probe.py --version v1 --headless --device cuda:0 --num_envs 64 --output outputs/wrench_v1_validation
```

## 12. 설정 수정 위치

| 변경하려는 항목 | 파일 |
| --- | --- |
| timestep·episode·높이·bank 크기·버전 구성 | [envs/wrench_envs.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/wrench_envs.py) |
| OSC gain·wrench scale·command limit | [mdp/actions/wrench.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/actions/wrench.py) |
| 센서 기준 wrench 실행·effort 제출 | [mdp/action_functions/wrench.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/action_functions/wrench.py) |
| 보상 weight·params·v1 override | [mdp/rewards/wrench.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/wrench.py) |
| v1 action-rate 계산 | [mdp/reward_functions/wrench.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/wrench.py) |
| 커리큘럼 | [mdp/curricula/wrench.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/wrench.py) |
| 단계별 bank 조합 | [mdp/common/wrench_layout.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/wrench_layout.py) |
| 종료 조건 | [mdp/terminations/wrench.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations/wrench.py) |
| 관측 구성 | [mdp/observations/wrench.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/wrench.py) |
| 초기화/reset 모드 | [mdp/events/wrench.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/events/wrench.py) |
| PPO·실험명 | [agent/wrench_ppo_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/wrench_ppo_cfg.py) |


## 13. Inspire-Wrench-v2: v1의 Arm 범위를1/10로 축소

2026-11-04 추가. `WrenchV2EnvCfg(WrenchV1EnvCfg)`가 v1을 직접 상속한다. Gym ID는 **`Inspire-Wrench-v2`**, runtime은 기존 `WrenchEnv`, runner는 `WrenchV2PPORunnerCfg(WrenchV1PPORunnerCfg)`이고 experiment_name은 `inspire_wrench_v2`다. 이 절은 v0/v1 설정을 바꾸지 않는다.

| 항목 | v1 | v2 |
| --- | --- | --- |
| Arm 목표 force 축별 | ±100N | ±10N |
| Arm 목표 moment 축별 | ±5Nm | ±0.5Nm |
| 보정 후 force 명령 축별 | ±120N | ±12N |
| 보정 후 moment 명령 축별 | ±6Nm | ±0.6Nm |
| raw clamp / 정규화 범위 | [-1,1] | [-1,1] |
| Hand openness | [0,1] | [0,1] |
| P gain / 중력 보상 | 0.2 / True | 동일 |

v2 post-init은 v1 초기화를 완료한 뒤 `wrench_scale`과 `commanded_wrench_limit`만 각각10으로 나눈다. F/T sensor 기준점, 정책/물리 주기, 관측, 배치, 보상·종료·커리큘럼은 상속한다. 관절 effort 제한과 중력 보상은 로봇 동역학 기준이므로1/10로 줄이지 않는다. 실제 접촉력의 하드 보장을 뜻하지 않는다.

**Action-rate 정규화도 축소된 목표 범위를 기준으로 유지한다.** 상속된 함수는 `clip(raw,-limit,limit)/limit`의 변화량을 사용한다. 이는 v2 Desired Wrench를 축별10N/0.5Nm로 나눈 값과 정확히 같으며 물리 scale이 분자·분모에서 상쇄된다. 따라서 reward 계수0.03을1/10 또는1/100로 추가 축소하지 않는다. Fx 0→5N, Mx 0→0.25Nm는 각각0.0075의 raw 비용으로, v1의0→50N·0→2.5Nm와 같은 상대비용이다. Hand raw 비용과 실제 측정 wrench-change 페널티도 보존한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-v2 --num_envs 2048 --headless
```

CPU46개 통과: 최종 v1/v2 구성 차이가 두 범위뿐임, 기존 부모 불변, Gym/runner 연결, 실제 Action의 목표 변환 및 반대 방향 feedback의12N/0.6Nm clamp, 정규화 비용 동등성을 검사했다. GPU probe는 `--version v2`를 지원하지만 이번 작업에서 실행하지 않았다. 실제 접촉 안정성·학습 성능은 미검증이다.
