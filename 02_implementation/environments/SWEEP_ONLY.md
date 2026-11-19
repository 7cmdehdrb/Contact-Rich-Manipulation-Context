# Inspire-Sweep-Only-v0 상세 환경 설명

계열 전체의 버전 비교와 최신 사용자 보고 학습 현황은 [Inspire-Sweep-Only 계열 안내](SWEEP_ONLY_FAMILY.md)를 먼저 참고한다. 이 문서는 일반 v0의 상세 구현과 파생 환경별 기술 설명을 유지한다.

2026-11-19 기준 실제 구현을 설명한다. `Inspire-Sweep-Only-v0`는 손을 타겟의 밀기 반대편에 IK로 배치한 뒤 곧바로 밀기를 수행하는 환경이다. 접촉 안정화 보상, 초기 물체 이동·회전 비용, Stabilize Gate는 사용하지 않는다. 압착 페널티와 Phase 관측도 사용하지 않는다. 내부 Sweep 상태와 나머지 제약은 유지한다.

이 문서의 중심은 `-Test`가 없는 일반 환경이다. 부모와 Test의 설계 이력은 [Stabilize 계열 설명](STABILIZE_SWEEP.md), 기존 성능 측정은 [일반 IK 초기화 성능 기록](../logs/2026-11-19_sweep_only_ik_performance.md)을 참고한다. 아래 설명은 코드의 현재 동작이며 학습된 정책의 성공을 뜻하지 않는다.

## 등록·상속과 네 환경의 차이

| Gym ID | EnvCfg / runtime | 초기화 | 안정화·Gate | Reach |
| --- | --- | --- | --- | --- |
| `Inspire-Stabilize-Sweep-v0` | `StabilizeSweepEnvCfg` / `StabilizeSweepEnv` | 물체 옆 IK, 충돌 검사, 제한 재추출 | 사용 | 없음 |
| `Inspire-Sweep-Only-v0` | `SweepOnlyEnvCfg` / `SweepOnlyEnv` | 위 일반 초기화 공유 | 없음 | 없음 |
| `Inspire-Stabilize-Sweep-v0-Test` | `StabilizeSweepTestEnvCfg` / `StabilizeSweepEnv` | Finger 원형 배치, 기본 방향 단일 Warp IK | 사용 | weight 30 |
| `Inspire-Sweep-Only-v0-Test` | `SweepOnlyTestEnvCfg` / `SweepOnlyEnv` | 위 Test 초기화 공유 | 없음 | weight 30 |

`SweepOnlyEnvCfg`는 `StabilizeSweepEnvCfg`의 직접 자식이며 보상과 Phase 없는 관측 설정을 교체한다. 각 Test 설정은 해당 일반 설정을 직접 상속해 초기화 이벤트, Reach 보상, 대표점 표시를 바꾼다. `SweepOnlyEnv`는 공통 runtime에서 `SweepOnlyState`를 사용한다. 초기화와 모든 reset 이후 내부 phase는 1이며 Actor·Critic 관측에는 제공하지 않는다. `StabilizeState`를 사용하는 부모의 Gate를 기다리지 않는다.

Test도 IK를 사용한다. 일반 환경의 물체 옆 자세 탐색과 충돌 검사를 간소화한 것이며, IK가 없는 환경은 아니다. Test 원형 배치는 선반·RED·물체 간 간격을 검사하지만 일반 환경과 같은 초기 로봇 전체 점유 공간 검사를 수행하지 않는다.

네 환경은 Scene, Action, Termination, Curriculum, 센서 계산 및 대부분의 Reward를 공유한다. Sweep Only 두 환경은 Phase 관측과 압착 비용을 제외한다. PPO 알고리즘·encoder는 같지만 Sweep Only는 66D 직접 관측을 받는 `SweepOnlyModel`을 사용하며 Stabilize는 기존 67D 모델을 유지한다. 일반 Sweep Only runner는 `SweepOnlyPPORunnerCfg`이며 `StabilizeSweepPPORunnerCfg`를 직접 상속한다. 두 Test runner는 각각 `StabilizeSweepTestPPORunnerCfg`, `SweepOnlyTestPPORunnerCfg`다. 일반 Sweep Only 로그 이름은 `inspire_sweep_only_v0`다.

근거: [등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py), [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/stabilize_sweep_envs.py), [runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/stabilize_sweep.py), [PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/stabilize_sweep_ppo_cfg.py).

## 시뮬레이션과 로봇

| 항목 | 설정 |
| --- | --- |
| 로봇 | UR5e + Axia80 형상·측정 joint + RH56E2 오른손 |
| 손 질량 | 총 0.790 kg; 공급자 URDF 질량·관성 비율을 유지하며 정규화 |
| Axia80 | 질량 0.280 kg, 반지름 0.041 m, 높이 0.0254 m |
| 물리 시간 간격 | 0.01초, 100 Hz |
| 정책 시간 간격 | decimation 2 → 0.02초, 50 Hz |
| 최대 에피소드 | 10초, 500 policy step |
| 기본 병렬 환경 수 / 간격 | 2048 / 2.5 m |
| 선반 | 질량 30 kg, 기본 위치 `(-0.7, 0, 0)` |
| 작업 상판 | 선반 로컬 Z = 1.05 m |
| 로봇 베이스 | 기본 위치 `(0, 0, 0.79505)`, quaternion `(0,0,0,1)` |
| EEF | `axia80_link`에서 로컬 Z로 0.1427 m 이동한 제어·관측 원점 |

손 자산은 공급자의 **오른손 URDF**에서 메쉬, 관절 원점·축·가동 범위, COM·관성을 읽어 생성한 `ur5e_inspire_right.usda`다. 내부의 `inspire_left_*` 이름은 이전 코드와 호환하기 위해 남긴 식별자다. 왼손 자산을 그대로 사용한다는 뜻이 아니다. URDF 원본 질량 합 0.8783 kg에 공통 비율을 적용하여 총 0.790 kg로 맞췄다.

손은 12개 물리 가동 관절을 가지며 정책은 6개 주 구동 관절만 제어한다. 나머지 관절 목표는 URDF의 mimic 비율에 따라 소프트웨어에서 계산한다. 손 내부 일부 인접 충돌 메쉬가 정상 자세에서도 겹치므로 articulation의 native self-collision은 꺼져 있다. 일반 reset은 별도 기하 검사로 새 팔–팔·팔–손 겹침을 검사하며, 기존 손 내부 겹침만 예외로 둔다.

근거: [Scene](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/stabilize_sweep.py), [조립 스포너](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/robot.py), [오른손 생성기](../../../../src/inspire_sweep_baseline/scripts/build_wrench_right_hand.py), [구동 관절·mimic](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/hand_kinematics.py).

## 물체와 물성 랜덤화

타겟은 기본 반지름 4 cm, 높이 10 cm의 원통이다. 장애물 물리 pool은 원통, cube, mug, bottle, cracker box, sugar box, tomato soup can, master chef can의 8종을 각각 2개씩 가진 16개 물체다. 매 reset에서 이 pool의 활성 물체를 선택한다. 매 episode마다 자산 종류나 메쉬를 새로 생성하지 않는다.

| 물성 | 범위 | 재추출 시점 |
| --- | --- | --- |
| 물체 크기 | 각 물체별 등방 scale `U(0.9,1.1)` | spawn/startup 1회 |
| 물체 질량 | 각 물체별 0.345–0.750 kg | startup 1회 |
| 선반 정지 / 동마찰 | 0.213–0.417 / 0.170–0.334 | 환경별 startup 1회 |
| 물체 정지 / 동마찰 | 0.235–0.395 / 0.188–0.316 | 물체별 startup 1회 |
| 손 정지 / 동마찰 | 0.295–0.875 / 0.236–0.700 | 환경별 startup 1회 |

마찰은 4096개 유한 material bucket에서 추출하므로 실제 값은 위 연속 구간의 중점 표본이다. 손 이외 로봇 collider의 material은 이 손 마찰 랜덤화 대상이 아니다. 메쉬와 충돌 형상은 같은 scale을 사용하고, 관성에는 크기의 제곱 및 질량 변경 비율을 반영한다. 물성은 이후 episode reset에서 고정된다. 따라서 “랜덤화가 있다”와 “매 reset에 다시 뽑는다”를 구분해야 한다.

근거: [이벤트 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/events/stabilize_sweep.py), [물성 초기화](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/wrench_refactor.py), [범위](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/realistic_physics.py), [물체 생성·scale](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/revision_spawners.py).

## 일반 환경의 reset과 스폰

### 타겟·목표

타겟 XY는 선반 중앙 반지름 2 cm 원판에서 면적 기준 균일하게 뽑는다. 실제 bounds의 최하단을 상판에 맞추고 yaw는 −90도로 설정한다. 타겟을 선반 전체에 균일하게 뿌리는 방식은 아니다.

목표 방향은 선반 로컬 `atan2(Y,X)` 기준 `[30°,150°]`와 `[210°,330°]`에서 추출한다. 선반 +X는 로봇 쪽, −Y는 로봇이 선반을 바라볼 때 왼쪽이다. ±X 축 양쪽의 30도 제외각을 항상 유지하며 방향 커리큘럼은 없다.

목표 거리는 6–12 cm에서 추출하되, 실제 타겟 크기와 선반 가장자리 2 cm 여유를 반영한 방향별 최대 거리를 넘지 않는다. 각도와 조건부 거리를 균일하게 추출하는 방식으로, 환형 영역의 면적 균일 표집과 다르다. 목표 Z는 초기 타겟 link root Z이고 보상·성공 거리는 XY를 사용한다.

### 손 위치·IK

손은 타겟에서 목표로 향하는 방향의 반대편에 놓인다. 오른손의 손바닥은 항상 로봇 기준 왼쪽 반구를 향한다. 왼쪽으로 밀 때 손바닥, 오른쪽으로 밀 때 손등을 사용하며 좌우 목표를 모두 유지한다.

초기 손 자세는 실제 손 충돌 정점의 지지점과 타겟 반지름을 이용해 마주 보는 표면 사이의 명목 간격을 5 cm로 만든다. EEF 원점–타겟 중심 거리가 5 cm라는 뜻은 아니다. 손 충돌 정점 최하단은 상판 위 5 mm가 되도록 높이를 계산한다. 손 관절은 모두 0 rad에서 시작한다.

손목 축은 로봇 베이스 쪽으로 향하게 정렬한다. 후보별 손목 고도각은 `0°, 2°, 0°, 2°`이며, 각각 XY ±1 cm와 yaw ±10도 jitter를 새로 뽑는다. 5 cm는 jitter 이전 명목 표면 간격이다. 각 후보에서 Warp IK 수렴과 관절 한계를 확인한 뒤, FK로 계산한 실제 충돌 기하에 대해 타겟·선반·로봇 자기충돌을 검사한다.

한 타겟·목표에 최대 4개 후보를 시도한다. 모두 실패한 환경만 타겟·목표를 최대 8회 추가로 재추출한다. 성공한 환경의 배치는 유지한다. 따라서 최대 9개 배치 × 4개 자세 후보이며, 모든 배치가 실패하면 진단 `RuntimeError`로 중단한다. 초기화 실패를 정책의 Termination으로 넘기거나 무제한 반복하지 않는다. 최종 분포는 IK·충돌 검사를 통과한 배치에 조건부다.

### 장애물의 금지 공간

장애물 수는 0–6에서 균일하게 요청하고 16개 pool에서 후보를 선택한다. 선반 로컬 XY 범위 `[-0.2,0.2] × [-0.5,0.5] m`를 5 mm 셀로 나누어 유효 셀과 셀 안 jitter로 배치한다. yaw는 `[-π,π]`에서 추출한다. 다음 조건을 모두 적용한다.

1. 실제 scale을 반영한 물체의 외접원과 1 cm 여유가 선반 경계 안에 있어야 한다.
2. 타겟→목표 구간과 선반 앞쪽 가장자리를 잇는 **RED 사각 영역**을 비운다. RED는 얇은 이동 선분만을 뜻하지 않는다. 타겟·장애물 반경 및 셀 jitter 여유를 포함한다.
3. 채택한 초기 로봇의 충돌 OBB를 축 정렬 외곽으로 변환하고 1 cm 확장한 공간을 비운다. 물체와 로봇 형상의 Z 구간이 겹칠 때 해당 XY 점유 영역을 제외한다.
4. 먼저 배치한 활성 물체와의 간격을 확보한다.

큰 후보부터 배치하며 공간이 부족한 후보는 생략하고 뒤의 작은 후보를 계속 검사한다. 장애물 배치를 위해 타겟·목표를 다시 뽑지는 않는다. 최종 활성 수는 요청 수보다 작아질 수 있다. 외접원·확장 상자를 사용하는 보수적 공간 검사이므로 실제 자유 공간의 엄밀한 균일 표집은 아니다.

대표점 생성 결과에서 타겟이 보이지 않거나 장애물 조각이 16개를 넘으면 해당 환경의 장애물을 제거하고 한 번 더 관측을 만든다. 타겟 단독 상태에서도 유효 대표점이 없으면 오류로 종료한다. 사용하지 않는 pool 물체는 로봇 작업 공간 밖 XY 주차 격자에 놓고 중력을 비활성화한다. 활성 mask에서 제외되어 관측·보상·종료 대상으로 취급하지 않는다.

근거: [reset](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/stabilize_sweep.py), [손 자세](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_reset.py), [로봇 충돌 검사](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_geometry.py), [로봇 포함 장애물 배치](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_layout.py), [공통 목표·RED](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/wrench_refactor_layout.py).

## Action과 정책

Action은 총 12차원이며 앞 6개는 팔, 뒤 6개는 손이다.

| 채널 | 의미 | 처리 |
| --- | --- | --- |
| 0–2 | 현재 EEF 축 기준 상대 위치 명령 | raw 입력 × 0.03 m |
| 3–5 | 현재 EEF 축 기준 상대 회전 RPY 명령 | raw 입력 × 0.15 rad 후 회전 표현 변환 |
| 6–11 | 엄지 굽힘·검지·중지·약지·소지·엄지 대립 | 절대 목표 rad, 0부터 URDF 상한까지 clamp |

팔은 상대 pose OSC다. 명령 좌표계는 해당 policy step의 EEF 자세로 고정하며 두 물리 substep 동안 제어한다. 위치 stiffness는 100, 회전 stiffness는 50, damping ratio는 모두 1이다. 전체 관성 decoupling과 중력 보상을 사용한다. 관절 effort 한계는 앞 세 축 150 N·m, 뒤 세 축 28 N·m다. 실제 effort를 이 범위에 제한하며 팔 implicit position drive의 stiffness·damping은 0이다.

손은 Joint Position Control이다. 6개 상한은 순서대로 `[0.5864,1.4381,1.4381,1.4381,1.4381,1.1641] rad`다. 12개 물리 관절 목표는 mimic 비율로 생성한다. 손 effort 한계는 10 N·m, velocity 한계는 1 rad/s, stiffness 1.2, damping 0.06이다.

사용자 후속 확인에 따라 PPO 설정의 **`clip_actions=π/2`를 유지한다.** RSL wrapper가 환경 실행 직전에 전체 12차원을 ±π/2로 clip한다. Actor는 표준 Gaussian을 사용하고 PPO는 원래 샘플과 그 log probability를 저장한다. 따라서 실행 입력은 제한되지만 Actor의 샘플·평균·단독 export가 원천적으로 범위 안에만 있는 것은 아니다. 손에는 이 wrapper clip 이후 URDF clamp가 추가로 적용된다. 정책의 Last Action은 wrapper clip을 거친 raw 12D이며 손 최종 목표나 OSC scale 이후 값이 아니다.

사용자가 요청한 action clip은 이 기존 `clip_actions` 설정을 뜻하므로 해당 조건을 만족한다. 이를 정책 분포 자체가 bounded라는 의미로 확대하지 않는다. Gaussian 분포·PPO 확률 계산은 유지한다.

근거: [Action 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/actions/stabilize_sweep.py), [EEF OSC](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/action_functions/wrench_refactor.py), [손 제어](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/action_functions/sweep_simple.py), [RSL wrapper](../../../../IsaacLab/source/isaaclab_rl/isaaclab_rl/rsl_rl/vecenv_wrapper.py).

## Observation과 정보 경계

Phase는 내부 상태로만 유지하며 관측 term은 없다. Actor와 Critic은 동일한 `policy` 66D와 `obstacles` 64D를 입력받는다. Critic에 현재 타겟 GT를 별도로 제공하지 않는다. 반면 보상·종료는 실제 현재 타겟·장애물 상태를 사용한다.

| 순서 | 관측 | 차원 | 단위·기준 |
| --- | --- | --- | --- |
| 1 | Arm joint position | 6 | 실제 절대 관절각 rad |
| 2 | Arm joint velocity | 6 | 실제 부호 있는 관절속도 rad/s |
| 3 | Hand configuration | 6 | 실제 제어 가능 주 구동 관절각 rad |
| 4 | EEF pose | 7 | 현재 로봇 root frame의 XYZ와 quaternion wxyz |
| 5 | Target surface point | 3 | 초기 표면점을 현재 EEF frame으로 변환한 XYZ m |
| 6 | Goal position | 3 | 고정 목표를 현재 EEF frame으로 변환한 XYZ m |
| 7 | Last Action | 12 | 직전 실행 raw 명령, wrapper clip 이후 |
| 8 | Paired tactile | 17 | 없음 0 / 손바닥 1 / 손등 −1 / 양쪽 2 |
| 9 | Compensated wrench | 6 | EEF 원점·축의 N, N·m |

Absolute 관절 관측은 default 자세를 빼지 않는다는 뜻이다. 속도에서 부호를 없앤 절댓값을 관측한다는 뜻은 아니다. 관측 전체 정규화는 꺼져 있다.

### 정면 대표 표면점

reset 때 선반 +X 쪽에서 −X를 보는 고정 정사영 정면 시야를 사용한다. 실제 시각 메쉬에 대해 YZ 1 mm 격자에서 첫 표면 hit를 구한다. 선반과 활성 물체 사이 가림을 반영하고 로봇 자체의 가림은 반영하지 않는다. 렌더 카메라의 원근 투영이나 실제 카메라 calibration을 사용하는 것은 아니다.

노출 mask를 4방향 연결 성분으로 나누고, 각 성분의 가로 폭이 `max(2 cm, 전체 투영 가로 폭의 20%)` 이상일 때 사용한다. 타겟은 살아남은 가장 큰 성분 하나만 사용한다. 장애물은 분리되어 보이는 각 성분을 별도 관측으로 취급한다.

대표점은 **가시 mask 면적 중심에 가장 가까운 유효 픽셀의 실제 표면 XYZ**다. 2D Bounding Box 중앙, 물체 전체 centroid, 표면점 XYZ의 산술평균과는 다르다. Bounding Box 대표점과 정확히 동일하다는 해석은 현재 구현에 맞지 않는다. 물체 종류·크기·orientation·물리 ID는 정책에 제공하지 않는다.

대표점의 월드 좌표는 reset 때 고정된다. 이후 실제 물체가 움직여도 갱신하지 않고 현재 EEF의 이동·회전으로 좌표만 변환한다. 장애물은 유효성 mask를 포함한 `[Mask,x,y,z] × 16`을 펼친 64D다. 빈 슬롯은 모두 0이다. 보이지 않는 물체를 임의로 visible로 뒤집는 noise는 없다. 촉각의 확률 flip과 별개다.

장애물 입력은 mask가 없는 좌표를 다시 0으로 만든 뒤 `64 → 32(ReLU) → 16` MLP로 인코딩한다. Actor와 Critic은 독립된 encoder를 학습하며, 각각 `66 + 16 = 82D`를 본체 MLP에 넣는다. 단독 모델 export 입력은 `66 + 64 = 130D`다.

근거: [관측 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/stabilize_sweep.py), [현재 EEF 변환](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/stabilize_sweep.py), [표면 추출](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_surface.py), [encoder](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/wrench_refactor_models.py).

### Tactile

17개 손바닥 측 물리 pad와 그에 대응하는 17개 손등 측 가상 표면 영역으로 34개 접촉 bit를 만든다. 손등 영역은 손 parent link의 실제 접촉점을 메쉬 영역에 투영하여 계산한다. 접촉 크기 기준은 0.05 N 이상이다. 두 bit를 묶어 17차원 상태로 인코딩하며 손바닥과 손등의 구분을 보존한다.

기본 학습 관측에서는 각 원래 bit를 독립적으로 1% 확률로 뒤집은 뒤 다시 17차원으로 인코딩한다. 관측 corruption을 끄면 flip도 꺼진다. 이 17D는 관측용이며 밀기 보상의 접촉 카운트는 별도의 타겟–손 실제 접촉 데이터로 계산한다.

손등 투영용 contact sensor는 물체 pool을 filter로 사용한다. 선반 접촉은 이 투영 경로에 포함되지 않는다. 직접 손바닥 pad의 net contact에는 filter가 없으므로 이러한 범위 차이가 있다. 34개의 독립된 실물 pad를 모두 물리 body로 배치한 모델로 해석하면 안 된다.

### F/T 보상과 clipping

Axia80–손 사이의 보존된 fixed joint에서 child인 `inspire_base_link`의 incoming joint wrench를 읽는다. 측정 joint는 Axia 하우징 중심보다 12.7 mm 손 쪽에 있다. 이를 EEF 원점으로 모멘트 이동하고 EEF 축으로 변환한다.

손 link와 tactile pad 전체의 실제 PhysX 질량·관성·COM·속도·같은 물리 step의 가속도로 다음 지지 wrench를 계산해 뺀다.

```math
\mathbf{F}_{\mathrm{hand}}=\sum_i m_i(\mathbf{a}_i-\mathbf{g})
```

```math
\mathbf{M}_{\mathrm{hand}}=\sum_i\left(\mathbf{I}_i\boldsymbol{\alpha}_i+\boldsymbol{\omega}_i\times\mathbf{I}_i\boldsymbol{\omega}_i+(\mathbf{c}_i-\mathbf{p}_{\mathrm{EEF}})\times m_i(\mathbf{a}_i-\mathbf{g})\right)
```

보상은 손의 중력·병진 관성·회전 관성·자이로 항을 포함한다. 물체 상태나 접촉 ID를 이용해 외력을 지우지 않으며 reset tare도 수집하지 않는다. 반력 부호는 parent-on-child 기준이므로 손에 작용한 외력은 보정 반력에서 반대 부호로 나타난다.

이후 힘 각 축 표준편차 0.05 N, 모멘트 각 축 0.005 N·m의 독립 Gaussian noise를 추가한다. 최종 정책 관측은 힘 각 축 ±150 N, 모멘트 각 축 ±8 N·m로 clip한다. **EEF 변환·보상·noise 이후 관측 clip**이며 native Axia 축의 원시 센서 포화를 먼저 모사하는 방식은 아니다. 보상 및 진단용 compensated wrench에는 이 관측 clip을 적용하지 않는다. PhysX의 이산 시간 반력·solver 오차·모델에 넣지 않은 damping 잔차는 남을 수 있다.

근거: [34→17 촉각](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/wrench_refactor.py), [noise](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/final.py), [동적 하중 보상](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/compensated_wrench.py), [공유 wrench reader](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/contact_sweep_clutter.py), [clip 연결 runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/stabilize_sweep.py).

## Reward

일반 Sweep Only에는 Reaching이 없다. 아래 식에서 $\Delta t=0.02$초이며 대부분의 cost는 RewardManager가 `weight × cost × Δt`로 누적한다. 거리 감소·증가 항과 선반 실패 event는 함수에서 `Δt`를 나누므로 아래에 기재한 step 보상이 그대로 지급된다.

### 밀기와 멀어짐

$d_t$는 **현재 실제 타겟 기하 centroid**와 목표 사이 XY 거리다. 관측에 제공하는 초기 표면점을 보상 계산에 사용하지 않는다. $p_t=d_{t-1}-d_t$로 둔다.

매 0.01초마다 타겟–손 개별 접촉의 법선력과 마찰력을 합산한다. 법선 하중은 각 접촉 법선력 크기의 합이다. 두 물리 substep 중 유효한 접촉의 법선 하중이 한 번이라도 0.01 N 이상이면 해당 policy interval에 접촉이 있었다고 기록한다. 방향 계산에는 두 substep의 평균 합력을 사용하며, 모든 substep 데이터가 유효해야 한다.

최근 3개 policy interval 중 2개 이상 접촉을 인정하고, 현재 EEF Z가 **초기 상판보다 엄격히 12 cm 미만**일 때 접촉 카운트를 1 증가시킨다. 불인정 시 2 감소시키며 0–20 범위로 제한한다. 인정된 step의 계수는 $h_t=n_t/20$, 불인정 step의 계수는 0이다. 설정 이름은 `sweep_contact_height_limit=0.12`다. 정확히 12 cm인 경우 양의 밀기 보상을 받지 않는다.

현재 타겟→목표 XY 단위 방향을 $\mathbf{u}_t$, 평균 합력을 $\bar{\mathbf{F}}_t$라 하면 정렬 계수는 다음과 같다.

```math
 a_t=\mathrm{clip}\left(\frac{\bar{\mathbf{F}}_{t,xy}\cdot\mathbf{u}_t}{\|\bar{\mathbf{F}}_t\|},0,1\right),\qquad
 r_{\mathrm{sweep},t}=30\max(p_t,0)h_ta_t
```

정렬 계수는 현재 interval에도 실제 접촉이 있고 데이터가 유효하며 평균 수평 힘이 1 N 이상, 현재 목표 거리가 0보다 클 때만 사용한다. 나머지는 0이다. 수평으로 목표 방향에 밀면 최대이며 수직 힘은 분모에 포함되어 점수를 낮춘다. 목표 근처에서 접촉이나 방향 조건을 우회하는 별도 규칙은 없다. 정확히 목표 중심이면 방향 계수는 0이다.

멀어짐은 별도로 다음 step 패널티를 받는다.

```math
 r_{\mathrm{inverse},t}=-20\max(-p_t,0)
```

이 비용에는 접촉·높이·힘 방향 조건이 없다. 이전 거리는 매 step 갱신하므로, 보상 불인정 중 이동해 둔 거리를 나중에 접촉했을 때 소급하여 받지 않는다. Sweep Only에서는 처음부터 두 항이 활성 상태다.

### 보조 비용

| Term | Weight | raw cost / 의미 |
| --- | --- | --- |
| `arm_action_rate` | −0.03 | 팔 6개 raw 실행 명령의 직전 step 대비 차이 제곱합; 상한 없음 |
| `hand_action_rate` | −0.03 | 손 6개 raw 실행 명령의 차이 제곱합; 상한 없음 |
| `arm_joint_velocity` | −0.03 | 실제 팔 6관절 속도 제곱합, 합계 상한 100 |
| `hand_joint_velocity` | −0.01 | 실제 손 12관절 속도 제곱합, 합계 상한 100 |
| `shelf_collision` | −0.5 | 선반 이동 flag와 가상 finger/wrist의 근접 cost |
| `shelf_failure` | −3/event | 선반 속도·wrist 높이 실패 조건에 해당하는 종료 step에서 1회 |
| `obstacle_contact` | 0 → −0.1 | 타겟 제외 손–장애물 합력 크기의 임계 초과 지수 비용, 상한 100 |
| `wrench_change` | 0 → −0.1 | 보정 F/T 크기 변화의 정규화 지수 비용, raw 상한 1; 5% 상한 없음 |
| `object_tilt` | −30 | 활성 타겟·장애물의 tilt 정규화 제곱합 |
| `obstacle_displacement` | −150 | 활성 장애물의 초기 대비 3D 변위 제곱합, 합계 상한 0.04 m² |

관절 속도 비용은 **최대 관절 속도 초과량** 비용이 아니라 모든 해당 관절의 제곱합이다. 손 Action은 6D지만 손 속도 비용은 mimic follower를 포함한 12개 물리 관절을 본다.

`object_tilt`는 물체별로 `clip((θ−5°)/(0.9 rad−5°),0,1)²`를 계산하여 합한다. 장애물 변위는 타겟을 제외하고 초기 root 위치와 현재 root 위치를 비교한다. 비활성 주차 물체는 두 비용에서 제외한다.

장애물 합력 크기를 $f$, 해당 iteration의 free-force를 $f_0$라 하면 `obstacle_contact` 비용은 `min(0.5 × (exp(2 × max(f−f0,0))−1),100)`이다. 구현은 overflow를 피하도록 지수 입력도 사전에 제한한다. 접촉별 힘 크기의 합이 아니라 합력 크기이므로 서로 반대인 장애물 접촉력이 상쇄될 수 있다.

`wrench_change`는 힘·모멘트 벡터 차이의 norm이 아니라 **각 벡터 norm의 변화량**을 사용한다. 힘 크기 변화 $\delta_F$와 모멘트 크기 변화 $\delta_M$, 각각의 free threshold $F_0,M_0$로 아래를 계산한다.

```math
 s=\mathrm{clip}\left(\max\left(\frac{\max(\delta_F-F_0,0)}{1.5F_0},\frac{\max(\delta_M-M_0,0)}{1.5M_0}\right),0,1\right),\qquad
 C_{\mathrm{wrench}}=\frac{e^{3s}-1}{e^3-1}
```

크기가 같은 채 방향만 바뀌면 이 비용은 0이다. 시간 미분이 아니며 threshold의 2.5배에서 포화한다. 정책 관측 noise·clip 이전 compensated wrench를 읽는다. reset 뒤 첫 유효 sample은 이력만 설정하며, 0인 weight를 활성화할 때도 이력을 초기화한다.

선반 보조 비용은 기존 함수를 유지한다. `shelf_collision`의 moved flag는 `선반 초기 대비 위치 변위 norm + 선반 6D 속도 norm > 0.005`다. 선반 root에서 Z로 1.06 m인 기준점과 EEF의 3D 거리가 0.2 m 미만일 때, 두 가상 finger의 `clip(1−높이/0.02,0,1)`과 wrist의 `clip(1−높이/0.08,0,1)`을 추가한다. 이 1.06 m는 해당 기존 근접 비용의 기준이며 reset·밀기 높이·종료에서 사용하는 상판 1.05 m와 구분된다.

`shelf_failure` event는 선반 6D 속도 norm > 0.1 또는 wrist의 상판 위 clearance < 3 cm일 때만 적용한다. 선반 변위만으로 종료되는 경우에는 이 −3 event가 추가되지 않는다.

안정화 점수, 초기 이동·회전 비용, 별도 goal-distance·hold·contact 보상, EEF 속도·방향 비용, 물체 속도·가속도 비용은 비활성이다. 성공 종료 bonus도 없다. Sweep Only 일반·Test 모두 압착 비용을 제거했다. 접촉 법선 하중 계측과 접촉 카운트는 밀기 보상 계산에 계속 사용하지만, 하중 5N 초과 자체에 벌점을 주지 않는다.

Test에만 있는 Reach는 현재 타겟 BBOX centroid–EEF의 3D 거리 $r$에 대해 `0.1/(0.1+max(r−0.1,0))`의 근접 계수를 사용한다. 10 cm 이내에서 계수가 최대다. 여기에 reset 초기 거리 budget을 episode 10초로 나눈 지급률과 weight 30이 적용된다. 초기 budget이 0이면 Reach도 0이다. 일반 Sweep Only에는 이 항이 없다.

근거: [보상 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/stabilize_sweep.py), [상태·거리·접촉 카운트](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_state.py), [타겟 접촉 계측](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_contact.py), [공유 보조 비용](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/contact_sweep_clutter_fusion.py), [선반 근접 비용](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/sweep.py).

## Curriculum

방향 제외각은 30도 고정이고 팔 속도 종료 threshold는 1 rad/s 고정이다. 이 두 커리큘럼은 비활성이다. 아래 보조 비용 일정만 사용하며 250 iteration 단위로 양자화한 구간별 선형 보간을 적용한다.

| 항목 | iteration 0 | 1000 | 3000 | 6000 | 10000 | 12000 이후 |
| --- | --- | --- | --- | --- | --- | --- |
| Wrench 힘 변화 허용값 N | 50 | 50 | 50 | 30 | 30 | 20 |
| Wrench 모멘트 변화 허용값 N·m | 5 | 5 | 5 | 3 | 3 | 2 |
| 장애물 합력 허용값 N | 80 | 80 | 80 | 50 | 50 | 30 |
| Wrench weight | 0 | 0 | −0.03 | −0.1 | −0.1 | −0.1 |
| 장애물 접촉 weight | 0 | 0 | −0.02 | −0.05 | −0.05 | −0.1 |

처음 1000 iteration까지 Wrench·장애물 접촉 비용의 weight는 0이다. term이 존재한다고 학습 시작부터 페널티가 적용되는 것은 아니다. 일정은 저장된 learning iteration을 기준으로 복원되며, 목표 반경·장애물 수를 늘리는 커리큘럼은 없다.

근거: [커리큘럼 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/stabilize_sweep.py), [보간·활성화 처리](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curriculum_functions/contact_sweep_clutter_fusion_holding.py).

## Termination과 성공 판정

| Term | 정확한 조건 |
| --- | --- |
| `arm_joint_velocity` | 팔 6관절 중 하나라도 `abs(qdot) > 1.0 rad/s`; 정확히 1.0은 허용 |
| `object_fall_or_tilt` | 활성 타겟·장애물의 실제 bounds 바닥이 상판보다 1 cm 아래이거나 tilt ≥ 0.9 rad, 또는 바닥 높이가 비유한값 |
| `shelf_failure` | 선반 6D root 속도 norm > 0.1, 또는 wrist clearance < 3 cm, 또는 선반 초기 대비 3D 변위 > 5 cm |
| `timeout` | episode step ≥ 500, 모든 deadline에서 참 |
| `success` | deadline이고 현재 타겟 centroid–목표 XY 거리 < 3 cm이며 위 세 물리 실패가 모두 거짓 |

팔 속도 종료는 손 관절을 검사하지 않는다. 손의 물리 velocity 한계와 종료 term은 별개다. 선반 속도 norm은 기존 구현대로 선속도·각속도를 합친 6D 벡터 norm이다. 선반 종료의 가상 finger 높이 검사는 꺼져 있다.

정확히 3 cm인 timeout은 성공이 아니다. 목표에 일찍 도달해도 즉시 종료하지 않고 10초까지 진행한다. 성공에는 추가 유지 시간·속도 조건이 없다. 동일 step에 물리 실패가 있으면 성공으로 분류하지 않는다.

`timeout`과 `success`는 상호 배타적 term이 아니다. 성공 시 둘 다 참이고, timeout 실패는 `timeout AND NOT success`로 해석한다. 두 term은 `time_out=True`이며 wrapper에 time-limit 정보가 전달된다. 초기화 IK 실패는 이 TerminationManager를 거치지 않는다.

최근 완료 episode 10,000개 ring에서 timeout 수·timeout 성공 수와 그 비율을 집계한다. 조기 실패도 ring에 들어가지만 timeout 분모에는 포함되지 않는다. 이 로그 비율을 전체 episode 성공률과 혼동하면 안 된다.

근거: [종료 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations/stabilize_sweep.py), [엄격한 timeout 성공](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/stabilize_sweep.py), [활성 물체 실패](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/revision.py), [선반 실패](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/final.py).

## PPO와 실행

Phase 제거 이전 67D 직접 관측/131D export 체크포인트는 새 66D/130D 모델에 그대로 로드할 수 없다. 첫 MLP 입력도 83D에서 82D로 바뀌므로 새 학습이 필요하며, 이 변경에서는 기존 체크포인트를 변환하지 않는다.

PPO는 rollout 36 step, 8 epoch × 4 minibatch, learning rate 0.001의 adaptive schedule, γ 0.98, λ 0.95, clip parameter 0.2, entropy coefficient 0.005, desired KL 0.02, max grad norm 1.0을 사용한다. Actor·Critic 본체는 256/128/64 ELU MLP다. 초기 Gaussian 표준편차는 1.0이며 observation normalization은 꺼져 있다. 기본 max iteration은 90,000, checkpoint 저장 간격은 50이다.

프로젝트 루트에서 학습한다.

```bash
conda activate env_isaaclab
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Only-v0 --num_envs 2048 --headless
```

작은 GUI 장면으로 학습 초기화를 볼 때는 `--headless`를 빼고 환경 수를 줄인다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Only-v0 --num_envs 4
```

일반 환경의 대표점 빨간 marker 기본값은 꺼져 있다. 두 Test에서는 GUI 또는 RGB 렌더 환경에 한해 켜져 있으며 물리 body나 collider를 만들지 않는다. marker는 episode 초기 월드 표면점을 표시하므로 이후 물체가 이동하면 marker가 물체를 따라가지 않는 것이 정상이다.

기존 통합 검사 실행기는 실제 배치·관측·접촉·부분 reset을 확인한다. 아래는 64환경 실행 예시다. 이번 공통 코드 정리 후에는 네 ID 각각 4환경·reset seed 0–1로 실행하여 모두 통과했다.

```bash
python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py \
  --task Inspire-Sweep-Only-v0 --headless --num-envs 64 \
  --audit-resets 8 --output /tmp/sweep_only_check.json
```

## 성능 근거와 확인 범위

Phase·압착 제거 후 CPU 95개(66D/67D 모델 forward·gradient·TorchScript export 포함) 및 네 ID 각각 GPU 4환경 reset·step·부분 reset 검사를 통과했다. Sweep Only는 66D와 활성 Phase/squeeze term 부재를, Stabilize는 기존 67D와 두 term 유지를 확인했다. 새 학습 성능은 측정하지 않았다.

이번 공통 코드 정리 후 CPU 회귀 211개 및 네 환경 각각 GPU reset·step·부분 reset 검사를 통과했다. 실제 등록 설정을 전후 직렬화하여 높이 필드 정리 외 Scene·Manager·PPO 설정이 동일함을 확인했다. 아래 성능 수치와는 별도 검증이며 이번 작업에서 2048환경 학습을 재측정하지 않았다. [이번 조건 검토·검증 기록](../logs/2026-11-19_stabilize_family_audit.md)과 [보존 자료](../../03_assets/validation/2026-11-19_stabilize_family_audit.json)를 참고한다.

2026-11-19 이전 성능 작업에서 RTX 3090, 2048환경, headless, seed 42, 실제 `train.py` 32 iteration을 측정했다. rollout·PPO·보상·관측을 유지한 최종 실행의 collection time은 최소 4.905초, 중앙값 8.322초, 최대 9.579초였고 32회 모두 10초 미만이었다. learning을 포함한 iteration time은 중앙값 8.69초, 최대 9.98초였다.

주 병목은 IK 수치 solve 자체보다 반복 FK와 충돌 검사였다. GPU FK·SAT, 실제 hull 분리 증명과 원래 LP fallback, 채택 FK 재사용, IK 실패 행의 불필요한 충돌 검사 생략, 로봇 포함 배치의 GPU 처리를 적용했다. 원래 충돌 판정을 제거해서 얻은 수치는 아니다.

같은 성능 작업에서 CPU 회귀 143개와 GPU 64환경·seed 0–7의 실제 배치·관측·부분 reset 검사를 통과했다. 원본 IK/배치와 관절·목표·valid·난수 결과를 대조했고 FK 좌표는 FP32 수치 허용 오차 안에서 비교했다. 이는 **이전 작업의 검증 결과**다. 본 문서 작성·공통 코드 정리 후의 새로운 학습 성능 측정으로 재분류하지 않는다.

상세 명령·원시 결과·실패한 중간 후보·수치 허용 오차는 [성능 개발 기록](../logs/2026-11-19_sweep_only_ik_performance.md)과 [보존한 검증 자료](../../03_assets/validation/2026-11-19_sweep_only_ik_performance.json)에 있다.

현재 검증으로 다음을 보장하지 않는다.

- 모든 seed·장기 학습·다른 하드웨어의 collection time 10초 미만. 최초 simulator 생성·최초 reset도 위 collection 지표 밖이다.
- 학습된 밀기 정책의 장기 성공률이나 실물 전이 성공.
- 원시 Axia 센서의 electronics 포화·대역폭까지 포함한 완전한 장치 모사.
- 로봇 가림·원근 카메라를 포함한 현실의 시각 관측 동등성.
- Test의 초기 로봇 전체 점유 공간 비겹침이나 무제한 reset 복구.

현재 조건 검토에서는 사용자 확인대로 기존 PPO `clip_actions`를 유지한다. mask 중심과 bbox 중심의 차이, startup에서만 적용되는 물성 랜덤화, Test 초기 로봇 충돌 검사 부재는 현재 구현의 범위로 구분해 기록한다.

## Sweep Only v1 Test

`Inspire-Sweep-Only-v1-Test`는 `Inspire-Sweep-Only-v0-Test`를 직접 상속한다. `SweepOnlyV1TestEnvCfg`는 부모 post-init 이후 `sweep_progress.weight=50.0`, `sweep_retreat.weight=-10.0`만 변경한다. 기존 `SweepOnlyEnv` runtime을 사용하고, `SweepOnlyV1TestPPORunnerCfg`는 부모 runner에서 experiment name만 `inspire_sweep_only_v1_test`로 변경한다.

일반 물체 옆 시작이 아니라 Test의 Finger 초기화·Reach를 유지한다. 관측 66D+64D, Phase 관측·압착 없음, 제어·물성·reset·종료·커리큘럼·모델·PPO는 v0-Test와 동일하다. 앞 절의 30/−20 계수는 v0 및 v0-Test에 대한 설명이다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Only-v1-Test --num_envs 2048 --headless
```

## Sweep Only v2 Test

`Inspire-Sweep-Only-v2-Test`는 `SweepOnlyV2TestEnvCfg`에서 v1-Test를 직접 상속하며 부모 post-init 이후 `events.object_spawn.params['excluded_x_half_angle']=0.0`만 변경한다. 기존 방향 커리큘럼은 비활성이므로 0°가 학습 내내 유지된다. 목표 거리 6–12cm·RED·물체 배치 제약·Finger 초기화·IK는 유지하며 방향 제외 구간만 없앤다. 정방향 50, 역방향 −10 및 나머지 v1-Test 구성은 같다. runner도 v1-Test 직접 자식이고 로그 이름만 `inspire_sweep_only_v2_test`다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Only-v2-Test --num_envs 2048 --headless
```

사용자가 이 컴퓨터에서 학습 중이므로 GPU 테스트를 금지했다. 코드 구문·실제 파생 클래스 정의의 CPU 실행·등록·변경 범위 정적 검사만 통과했으며, 신규 ID의 Isaac Sim reset·step·학습은 미실행이다.


## Sweep Only v1_2 Test

`Inspire-Sweep-Only-v1_2-Test`의 `SweepOnlyV1_2TestEnvCfg`는 v1-Test를 직접 상속한다. 정방향 Weight는 50에서 100, 역방향 Weight는 −10에서 −25로 변경한다. `sweep_normalize_contact_count=False`를 runtime에서 상태 계산으로 전달하여 접촉 계수에 `count / 20` 대신 카운트 `count`를 그대로 사용한다. 카운트 범위 0–20, 증가·감소 규칙, 접촉 인식·높이·방향 조건은 그대로다.

따라서 유효 접촉 조건에서 정방향 보상은 `100 * max(d_prev - d, 0) * count * alignment`, 역방향은 `-25 * max(d - d_prev, 0)`이다. 동일 상태·이력·방향에서 v1 대비 각각 40배와 2.5배이며, 실제 학습 중 누적 수령액이 같은 배수임을 의미하지 않는다. v1의 Deadzone 30° 고정·Finger 초기화·Reach·관측·제어·다른 보상·종료·커리큘럼·PPO를 유지한다. v2-Test의 Deadzone 0°는 상속하지 않는다.

등록 runtime은 기존 `SweepOnlyEnv`, runner는 v1 runner의 직접 자식 `SweepOnlyV1_2TestPPORunnerCfg`이며 experiment name만 `inspire_sweep_only_v1_2_test`로 바뀐다. 기존 모든 환경은 새 정규화 설정의 기본값 True로 이전 동작을 유지한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Only-v1_2-Test --num_envs 2048 --headless
```

위 명령은 안내이며 실행하지 않았다. CPU 회귀 10개와 별도 378행 상태·수식 검사 및 등록·구문·상속 정적 검사를 통과했다. GPU·Isaac Sim reset/step·학습 성능은 미검증이다. [개발 기록](../logs/2026-11-19_sweep_only_v1_2_test.md).


## Sweep Only v2_2 Test

`Inspire-Sweep-Only-v2_2-Test`의 `SweepOnlyV2_2TestEnvCfg`는 v1_2-Test를 직접 상속한다. 부모 post-init 후 `events.object_spawn.params['excluded_x_half_angle']=0.0`만 변경한다. 방향 커리큘럼은 비활성이므로 Deadzone은 0° 고정이다. 정방향 Weight 100, 역방향 −25, 원시 접촉 카운트(20으로 나누지 않음), 접촉·높이·방향 조건과 그 외 전체 환경 구성은 v1_2-Test와 같다. 기존 v2-Test의 보상 50/−10과 혼동하지 않는다.

Runtime은 `SweepOnlyEnv`를 유지한다. `SweepOnlyV2_2TestPPORunnerCfg`도 v1_2 runner를 직접 상속하며 experiment name만 `inspire_sweep_only_v2_2_test`로 변경한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Only-v2_2-Test --num_envs 2048 --headless
```

명령은 안내이며 실행하지 않았다. 표준 라이브러리만 사용하여 구문·등록·직접 상속·파생 설정 및 기존 코드 보존을 검사했다. GPU·Isaac Sim reset/step·학습은 미실행이다. [개발 기록](../logs/2026-11-19_sweep_only_v2_2_test.md).
