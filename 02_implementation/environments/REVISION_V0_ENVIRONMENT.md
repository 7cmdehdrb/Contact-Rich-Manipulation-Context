# Revision v0 구현 계약

2026-11-01 작성. 기능 기준은 `Isaac-Inspire-Final-GoalAccuracy-v0_2`이며, [통합 수정 계획](../../01_plan/FINAL_YCB_SIZE_RANDOMIZATION_FIX.md)의 요구를 **새 Revision 계열**에 구현한다. 최신 사용자 지시에 따라 기존 환경을 직접 수정하거나 상속하지 않는다. 기존 custom CFG·runtime·command·model 상속을 끊고 Isaac Lab/RSL 기본 클래스에서 새 구성을 선언한다. 기존 계산 함수·센서 term·제어 구현의 재사용은 허용된 범위다.

**현재 상태는 구현·CPU 검사, 64 env의 정확한 scale 끝값, 실제 2048 env의 sparse/dense reset·rollout 및 2 iterations 학습 검증 완료다.** `train.py`로 147456 transitions를 수행하고 체크포인트의 유한값과 Actor/Critic encoder 갱신을 확인했다. 고정 접촉 높이는 120 mm로 설정했으며 실제 collider 기하·고정 로봇 root의 두 IK 자세·실제 접촉에 따른 높이 gate 분기를 확인했다. 접촉 검사는 별도 통제 fixture를 사용했으며 학습 후 상부 누르기 억제나 작업 성공률을 입증하지 않는다. 검증 이력과 남은 항목은 [개발 로그](../logs/2026-11-01_revision_v0_implementation.md)에 기록한다.

## 등록과 독립 구성

| 구성 | 등록 또는 클래스 | 직접 기반 |
| --- | --- | --- |
| Gym task | `Isaac-Inspire-Revision-v0` | 독립 등록 |
| EnvCfg | `RevisionEnvCfg` | `ManagerBasedRLEnvCfg` |
| runtime | `RevisionEnv` | `ManagerBasedRLEnv` |
| Scene | `RevisionSceneCfg` | `InteractiveSceneCfg` |
| 관측 그룹 | `RevisionObservationsCfg` 내부 각 그룹 | `ObservationGroupCfg` |
| Action CFG | `RevisionOSCActionCfg`, `RevisionHandActionCfg` | Isaac Lab Action CFG |
| Command | `RevisionGoalCommandCfg`, `RevisionGoalCommand` | `CommandTermCfg`, `CommandTerm` |
| Reward·Termination·Curriculum·Event CFG | 각 `Revision*Cfg` | 독립 `configclass` |
| PPO | `RevisionPPORunnerCfg` | `RslRlOnPolicyRunnerCfg` |
| 모델 CFG·모델 | `RevisionModelCfg`, `RevisionModel` | `RslRlMLPModelCfg`, `MLPModel` |

등록은 [패키지 진입점](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py), 조합은 [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/revision_envs.py), 실행 수명은 [runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/revision.py)에 있다. 역할별 디렉터리는 유지한다. 비교 기준 커밋은 `e2ace682083970760e1e0e32fe7a681b483d2199`다. 새 파일과 task 등록 외에 기존 환경의 설정·함수를 변경하지 않는다.

## 물체와 reset

[스포너](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/revision_spawners.py)와 [Scene](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/revision.py)은 **환경당 실제 rigid body 10개**를 생성한다. 이는 로봇과 선반을 제외한 물체 collection 수다. 타겟 슬롯 0 하나, Gray 용량 4, White 용량 5이며 장애물 관측 16슬롯과 물리 수를 구분한다.

| 종류 | 새 기준 bounds 크기 X×Y×Z, mm | 기준 |
| --- | --- | --- |
| 원통 | 80.000×80.000×100.000 | 반지름 40 mm |
| 직육면체 | 60.000×80.000×100.000 | 절차적 mesh |
| mug | 101.000×70.000×100.000 | 몸통·손잡이 전체 bounds |
| bottle | 60.000×60.000×135.000 | 몸통·어깨·목·뚜껑 전체 bounds |
| cracker box | 98.937×43.306×128.733 | YCB 정규화 `size_fraction=0.9` |
| sugar box | 85.183×41.484×162.000 | YCB 정규화 `size_fraction=0.9` |
| tomato soup can | 76.337×76.398×114.918 | YCB 정규화 `size_fraction=0.9` |
| master chef can | 76.403×76.332×104.586 | YCB 정규화 `size_fraction=0.9` |

모든 슬롯은 생성 시 8종에서 독립 균등 추출하고, 각 기준 크기에 `U(0.9,1.1)`을 한 번 적용한다. YCB의 최종 비율은 기존 정규화 `size_fraction=1.0` 대비 0.81~0.99다. Mesh에는 YCB용 0.9 보정을 추가하지 않는다. 표는 [64 env 끝값 검증 결과](../../../../outputs/revision_validation/probe_64_endpoints.json)의 실제 배치 bounds를 인스턴스 scale로 나눈 값이다. 검증 전용 `--scale_endpoints`는 scale을 정확히 0.9 또는 1.1로 설정해 **8종×2끝값의 collider/bounds 일치와 실제 활성 물체 rollout 참여**를 확인한다. 학습 환경의 연속 균등 분포는 변경하지 않는다.

**구현 선택: 형상·scale은 환경 생성 때 결정하고 PhysX 초기화 이후에는 고정한다.** 매 reset은 타겟·목표·장애물 위치와 yaw, 실제 활성 장애물 구성, 질량·마찰을 재추출한다. 타겟은 계속 슬롯 0이며 환경 안에서 다른 물리 슬롯으로 역할을 바꾸지 않는다. 따라서 단일 env playback의 타겟 종류·크기는 고정이고, 전체 벡터 환경의 분포로 종류·크기 다양성을 제공한다. 이는 매 reset 모든 형상을 바꾸라는 조건이 없는 최신 계획을 따른 선택이다. 64 env에서 실제 활성 타겟·Gray·White 모두 8종이 등장했고 두 scale 끝값의 모든 종류가 실제 rollout에 참여했다. 단순 사전 슬롯 수와 실제 역할별 커버리지를 분리 집계하며, 이 표본이 장기 학습의 모든 조합·배치 성공 편향을 입증하지는 않는다.

프로토타입 8개는 생성 준비 후 off-stage USD layer에 보관해 물리 후보 body로 남기지 않는다. 수정 가능한 rigid root 아래 geometry/collider는 instance reference로 공유한다. 각 root의 등방 scale이 visual·collider에 같이 적용되고, 명시된 관성은 scale 제곱으로 보정한다. reset의 질량 변경은 해당 형상의 기본 관성/질량 비율을 보존한다. 물리 재질은 역할별로 공유한다.

[reset event](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/revision.py)는 모든 pose·속도를 쓴 뒤 active mask와 중력 mask를 맞춘다. 활성 물체의 root Z는 `1.05 - scaled_local_min_z`로 설정한다. 비활성 슬롯은 선반 로컬 Z=50+2×slot m에 분리 주차하고 중력을 끈다. **active=false 자체는 collider 비활성화를 뜻하지 않는다.** 64 env의 sparse/dense 검사에서 비활성 sample 2270개를 별도로 집계해 최대 속도 0, 최대 변위 약 3.815 μm를 확인했다. 타겟 bbox를 켜면 실제 타겟인 `mass_cylinder` 슬롯의 자식으로만 시각화를 만든다.

물리 수 최적화와 함께 `gpu_found_lost_aggregate_pairs_capacity`를 기능 기준의 `2**28`에서 Isaac Lab 기본 `2**25`로 낮췄다. 16 env 실행의 CUDA 가용 메모리가 약 1051 MiB에서 8666 MiB로 증가했다. 이는 해당 시점의 free memory 비교이며 전체 peak 사용량 측정은 아니다. 다른 환경의 PhysX 설정은 바꾸지 않았다.

`cfg.seed`를 지정한 생성과 같은 호출 순서로 재현성을 관리한다. 레이아웃은 별도 torch generator를 쓰고 `reset(seed=...)`에서 재설정한다. 이미 생성한 형상·scale은 이 reset seed로 다시 추출하지 않는다. Actor visibility·인접 교환·센서 noise는 프레임워크가 seed를 관리하는 torch 난수를 쓴다. 부분 reset은 지정 env의 상태만 갱신하며 64 env에서 다른 env의 state 보존을 6회 확인했다.

## OBB 배치

[Revision adapter](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/revision_layout.py)는 독립 [OBB 배치 모듈](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/bbox_scene_layout.py)의 `LayoutConfig`와 `generate_layout`을 사용한다. 적용 기준은 `outputs/bbox_scene_layout`이며 원통 중심 배치 알고리즘을 이식하지 않는다.

타겟은 중앙 반경 20 mm 원판에서 시작하고 목표는 주어진 방향의 최대 150 mm, 최소 50 mm 유효 이동으로 뽑는다. 타겟 yaw는 선반 좌표 0이다. 실제 크기와 edge clearance 20 mm를 반영해 타겟·목표가 선반 안에 있도록 한다. 초기 ±X 제외각은 30°이며 기존 방향 커리큘럼을 유지한다.

선반 `(x,y)`를 board `(y,0.20-x)`로 바꾸고 yaw는 −π/2를 적용한다. 비대칭 bounds 중심 offset을 root 좌표에 더해 배치하고, 물리 pose로 돌아올 때 뺀다. 타겟 시작·목표 OBB의 swept RED와 전면 board −Y 확장, 접근 영역을 포함한 Gray, 나머지 White를 검사한다. **Gray padding은 65 mm 고정**, 물체 간격은 20 mm, board 경계 여유는 5 mm다. 후보 32×restart 4×pass 2 예산 안에서 실제 배치 수가 가장 많은 결과를 선택하고 동률이면 Gray 수를 우선한다.

실패 슬롯은 실제 active=false이며 좌표 0을 스폰 위치로 사용하지 않는다. 요청 수보다 적게 배치할 수 있고 `complete=False`를 로그로 남긴다. 물체 수 커리큘럼과 성공 반경을 바꾸어 빈 자리를 채우지 않는다. CPU 검사는 합성 비대칭 bounds의 경계·간격·바닥 정렬·난수 재현성을 확인했으며 실제 USD·PhysX 안전성을 대신하지 않는다.

## 관측과 모델

[관측 CFG](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/revision.py)의 policy 그룹은 다음 57D 순서다. slice의 끝은 제외한다.

| slice | 항목 | 계약 |
| --- | --- | --- |
| 0:12 | Arm 위치 6+속도 6 | 실제 관절값; default 차감 없음 |
| 12:14 | Hand 개방도 2 | 실제 관절에서 계산 |
| 14:21 | EEF pose 7 | 로봇 root 기준 XYZ 다음 quaternion |
| 21:24 | 초기 타겟 XYZ 3 | reset 시 latch, episode 고정 ±10 mm bias |
| 24:26 | 목표 2 | 초기 타겟 기준 거리·방향 |
| 26:34 | 이전 행동 8 | raw action의 tanh 피드백 |
| 34:51 | tactile 17 | 물리 접촉 비트, 각 비트 1% 반전 |
| 51:57 | F/T 6 | 보상된 EEF wrench, force 0.05 N·moment 0.005 Nm 표준편차 noise |

| 구분 | Actor | Critic |
| --- | --- | --- |
| 라우팅 | `policy`, `obstacles` | `policy`, `privileged`, `critic_obstacles` |
| 직접 입력 | policy57 | policy57+현재 타겟3 |
| 장애물 원시 입력 | reset 초기 캐시64 | 실제 활성 장애물의 현재 좌표64 |
| 가시성·noise | 초기 가시성, 1% 반전, ±10 mm 좌표 noise | 가림 필터·반전·좌표 noise 없음 |
| raw 입력 | 121D | 124D |
| encoder 후 본체 입력 | 73D | 76D |

장애물 16슬롯은 각각 `[Mask,x_root,y_root,z_root]`다. 미사용·주차 물체는 모든 값이 0이고 Actor visibility 반전도 이 규칙을 깨지 않는다. Critic은 `_active_object_mask`에서 현재 타겟을 제외한 물체만 읽으며, 실제 장애물이 에피소드 중 선반 밖으로 움직여도 reset 전까지 현재 위치를 제공한다. 선반 근처 좌표인지로 activity를 추측하지 않는다.

두 그룹 모두 보고되는 좌표의 Y 내림차순 정렬 후 유효 인접 쌍에 10% 교환을 적용한다. Actor는 reset 때 한 번 정하고 고정한다. **Critic은 매 관측 호출마다 다시 읽고 교환 난수를 재추출하며 좌표 noise는 0으로 결정했다.**

[RevisionModel](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/revision_models.py)은 각 모델에 독립 `64→32→16` ReLU encoder를 둔다. mask=0 좌표는 encoder에 들어가기 전에 0이 되며 NaN dummy 좌표도 제거한다. 본체는 `73/76→256→128→64→8/1`, ELU다. Actor와 Critic은 가중치를 공유하지 않는다. rollout에는 raw 관측을 보관하고 PPO 갱신마다 encoder를 재계산해 양쪽 gradient를 전달한다. Actor export는 초기 정보 121D만 받는다. 입력 순서·슬롯 수가 달라 기존 Final checkpoint 호환성을 보장하지 않는다.

## 행동·보상·종료

행동은 Arm 6D 상대 EEF pose + Hand 2D다. OSC 위치 scale 0.03 m, 회전 scale 0.15 rad, 강성 `(100,100,100,50,50,50)`, 감쇠비 1, 관성 decoupling·중력 보상·effort 제한을 유지한다. 물리 dt=0.01 s, decimation=2로 정책 dt=0.02 s, episode 최대 10 s다.

[보상 CFG](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/revision.py)는 아래 순서로 계산한다. weight는 초기값이며 일부 threshold·weight에 커리큘럼이 있다.

| term | weight | 핵심 조건·계수 |
| --- | --- | --- |
| `target_reaching` | 30 | EEF–타겟 접근 반경 0.10 m |
| `target_goal_distance` | 3.7 | XY 지수 거리, scale 0.05 m |
| `target_goal_hold` | 8 | 내부 반경 0.03 m, 외곽 0.08 m, speed scale 0.05 m/s |
| `target_contact` | 1.45 | 실제 타겟–손 force norm ≥0.01 N AND EEF 고정 높이 미만 |
| `robot_action_rate_penalty` | −1 | Arm 0.03·Hand 0.03 내부 계수 |
| `robot_joint_velocity_penalty` | −1 | Arm 0.03·Hand 0.01 내부 계수 |
| `object_penalty` | −1 | tilt·displacement 비용 ×30, 초기 acceleration weight 0 |
| `shelf_penalty` | −1 | 기존 선반 충돌·힘 비용 |
| `obstacle_contact_penalty` | 0 | 초기 free force 80 N, max cost 100 |
| `target_goal_timeout_bonus` | 30 | 성공 timeout에 한 번 +30, reward dt 보정 |
| `wrist_wrench_change_penalty` | 0 | 초기 force/moment 변화 50 N/5 Nm, positive budget 비율 0.05 |
| `target_speed_penalty` | −5 | 초기 free speed 0.1 m/s, 지수 비용 max 100 |

성공은 timeout 시 **유한 XY 거리 ≤0.03 m**이며 속도·체류시간 조건은 추가하지 않는다. 성공/실패 timeout을 모두 truncation으로 분리한다. 3 cm는 성공 분할·timeout bonus·Hold 내부 반경·명령 시각화가 공유한다. 반경 커리큘럼은 없다. Hold는 정확히 3 cm에서 raw 위치 score 0.5로 이어지고, 8 cm에서 0이다. 유효한 물체 자세·바닥 높이와 속도 감쇠는 계속 적용한다.

실패 종료는 활성 물체의 실제 bbox 최저점이 작업면보다 10 mm 이상 낮거나 tilt≥0.9 rad, 타겟 속도>1 m/s, 기존 선반 실패, Arm 관절 속도 임계값 5 rad/s를 사용한다. shape에 따라 root 높이가 달라지는 문제를 막기 위해 Hold 유효성·낙하 판정에서 회전된 8개 bbox 꼭짓점의 실제 최저점을 계산한다.

**고정 접촉 높이는 작업면 위 0.12 m로 결정했다.** 측정한 중앙 기준 8종의 윗면 높이 평균은 0.118154574 m다. 균등 종류 추출과 평균 1.0인 scale 분포를 기준으로 평균에 가까운 0.12 m를 적용한다. EEF Frame 중심 Z를 초기 선반 origin Z+작업면 1.05 m+0.12 m와 비교하며, 현재 타겟 크기·자세·선반 이동에 따라 임계값을 바꾸지 않는다. 같은 높이·비유한 높이·stale sensor는 실패한다. EEF는 axia80_link 로컬 Z offset 0.1427 m다.

[접촉 기하 probe](../../../../src/inspire_sweep_baseline/tests/revision_contact_geometry_probe.py)는 실제 mesh collider 정점·primitive 보수적 bounds와 현재 PhysX tensor body pose를 사용한다. 열린 손 관절 형상을 고정한 채 손바닥 법선을 수평으로 회전시키는 기하 계산에서, 바닥 여유 1 mm를 확보하고 가장 작은 scale 0.9의 8종 옆면 높이와 겹치는 **공통 EEF 높이 구간은 작업면 위 약 47.399~99.493 mm**였다. 예시 공통 높이는 73.446 mm로 120 mm 문턱 아래다. 이로써 보상을 받으려면 손 collider가 반드시 바닥과 겹쳐야 한다는 기하적 모순은 발견되지 않았다.

이 기하 검사는 **열린 손의 가상 강체 회전·높이 중첩 가능성**만 확인한다. 별도 [접촉 물리 probe](../../../../src/inspire_sweep_baseline/tests/_revision_contact_probe.py)는 로봇 root를 유지하고 실제 PhysX Jacobian으로 EEF 목표 높이95/150 mm의 관절 자세를 구한 뒤, OSC와 실제 접촉 센서로 높이 gate를 검증했다. IK 위치 오차는 각각68.8/1.86 μm였다. 이는 관절 상태를 재설정해 얻은 자세이며 초기 자세부터의 충돌 없는 이동 경로를 검증한 것은 아니다.

[접촉 결과](../../../../outputs/revision_validation/contact_physics.json)는 cylinder 하나(scale1.047294)의 손바닥 접촉을0/1 mm 침투량으로 구성한 통제 fixture다. 낮은 경우는 작업면에 놓고 중력을 켠다. 높은 경우는 높이 분기만 분리하기 위해 타겟을 띄우고 중력을 끈다. 실제 EEF·force를 가짜 값으로 덮어쓰지 않았으며 일반 reset의 스폰 알고리즘 검증으로 사용하지 않는다. 낮은 접촉10표본은 EEF97.072~98.016 mm, force .966~5.733 N에서 raw reward1, 높은 접촉2표본은 EEF148.524~148.526 mm, force12.382~12.396 N에서 raw reward0이었다. 총80개 env·physics-substep 관측에서 조건식 불일치0, 로봇 root 변경0이었다. 낮은 자세에서 측정한 hand/wrist collider 바닥 여유는 IK 직후36.955 mm, 접촉 후39.137 mm였다.

이 결과로 실제 접촉과120 mm 조건의 AND 동작 및 바닥과 겹치지 않는 낮은 접촉 자세를 확인했다. 닫힌 손·모든 종류의 동적 밀기·학습 후 상부 누르기 억제는 검증하지 않았다. 평균 높이는 가장 작은 물체의 윗면보다 높을 수 있으므로 이 단일 조건이 모든 상부 누르기를 막는다고 주장하지 않는다.

## 커리큘럼과 PPO

[커리큘럼](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/revision.py)은 절대 learning iteration으로 계산한다. 보상 schedule은 명시 지점 사이를 보간하고 interval에 따라 갱신한다.

| 대상 | 일정 |
| --- | --- |
| 장애물 수 | Gray/White 1/1 시작; Gray 2500, White 2000부터 1000마다 +1; 상한 4/5 |
| 타겟 free speed | `(0,.1),(499,.1),(500,.09),(1900,.02)`; interval 250 |
| 물체 free acceleration | 3000에서 50 →10000에서 20; interval 1 |
| 물체 acceleration weight | 3000에서 0 →10000에서 −0.05; interval 1 |
| 목표 방향 제외각 | 30°, iteration 3000까지 유지; 이후 500마다 5° 감소, 하한 0° |
| 손목 force 변화 허용량 | 3000에서 50 →10000에서 20; interval 250 |
| 손목 moment 변화 허용량 | 3000에서 5 →10000에서 2; interval 250 |
| 손목 변화 weight | `(0,0),(1000,0),(3000,−.03),(6000,−.1)`; interval 250 |
| 장애물 free force | `(0,80),(3000,80),(6000,50),(10000,50),(12000,30)`; interval 250 |
| 장애물 접촉 weight | `(0,0),(1000,0),(3000,−.02),(6000,−.05),(10000,−.05),(12000,−.1)`; interval 250 |

Gray padding·성공 반경·Hold speed scale을 변경하는 커리큘럼은 추가하지 않는다. iteration 되감기·resume 시에도 3 cm와 65 mm를 유지한다.

[PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/revision_ppo_cfg.py)은 runner `CurriculumOnPolicyRunner`, rollout 36 steps/env, 최대 90000 iterations, save interval 50이다. Gaussian 초기 std=1, learning rate 0.001, adaptive schedule, epochs 8, minibatches 4, clip 0.2, entropy 0.005, gamma 0.98, lambda 0.95, desired KL 0.02, max gradient norm 1, value loss coefficient 1을 사용한다.

## 실행과 검증 범위

Windows PowerShell에서 workspace 루트와 `env_isaaclab`을 사용한다. 실제 장비는 NVIDIA GeForce RTX 4070 12 GiB, driver 621.01이다. 아래 명령으로 검증을 수행했다. 학습 출력은 `outputs/revision_training`에 보존하며 `logs/rsl_rl`은 변경하지 않는다.

```powershell
conda activate env_isaaclab
cd C:\python\Contact-Rich-Manipulation
python -m pytest src\inspire_sweep_baseline\tests\test_revision_cfg.py src\inspire_sweep_baseline\tests\test_revision_layout.py src\inspire_sweep_baseline\tests\test_revision_observations.py -q
python src\inspire_sweep_baseline\tests\_revision_probe.py --num_envs 64 --steps 30 --resets 6 --headless --bbox --scale_endpoints
python src\inspire_sweep_baseline\tests\_revision_probe.py --num_envs 2048 --steps 30 --resets 6 --headless
python src\inspire_sweep_baseline\tests\_revision_contact_probe.py --num_envs 4 --headless
python src\inspire_sweep_baseline\scripts\train.py --task Isaac-Inspire-Revision-v0 --num_envs 2048 --headless --max_iterations 2 --experiment_name C:/python/Contact-Rich-Manipulation/outputs/revision_training --run_name smoke_2048
```

CPU **20개 통과(최종 합산 실행 4.22 s)**: 관측 순서·실제 관절값·zero padding·Critic 현재 좌표·gradient 분리, 실제 CPU PPO encoder 갱신·checkpoint 복원·Actor JIT export, 목표·Hold·접촉 경계, 비대칭 bounds 바닥 정렬, OBB 간격·경계·seed를 검사했다.

최종 소규모 기준은 64 env 끝값 검증이다. 초기화 7.38 s, 전체 probe 14.17 s이며 5개 일정의 reset, 부분 reset 6회, sparse 5 policy steps(10 physics steps)와 dense 30 policy steps(60 physics steps)를 수행했다. 실제 collection body는 USD·PhysX 모두 640개, 추가 World body 0개, bbox는 타겟 자식 64개다.

| phase | 실제 평균 Gray/White | 최대 활성 속도 | 최대 활성 변위 | 최소 바닥 높이 | 비활성 sample | 자동 reset |
| --- | --- | --- | --- | --- | --- | --- |
| sparse, iteration 0 | 1/1 | 0.0097973 m/s | 0.011001 mm | 1.0499954 m | 2240 | 0 |
| dense, iteration 10000 | 3.984375/5 | 0.2598948 m/s | 4.645498 mm | 1.0497968 m | 30 | 0 |

dense에서 Gray 한 자리가 배치되지 않은 env가 있었다. 이는 허용한 탐색 예산 내 부분 배치이며 요청 수가 모든 reset에서 보장된다는 뜻은 아니다. 검사 임계값은 최대 속도 1 m/s, 변위 50 mm, 물체 바닥 1.04 m 이상, 비활성 변위 0.1 mm·속도 0.001 m/s 이하다. 실제 측정치와 이 판정 범위를 함께 기록한다. 실제 활성 target/Gray/White 모두 8종이며 8종×scale 0.9/1.1이 sparse/dense 물리에 참여했다.

[2048 env 보고서](../../../../outputs/revision_validation/probe_2048.json)는 연속 scale 분포에서 초기화 66.4078 s, 전체 probe 80.8699 s, sparse5+dense30 policy steps와 부분 reset6회를 통과했다. 실제 object body는 USD·PhysX 모두20480개, 전체 enabled USD body는100352개, 자동 reset0회다. 역할별8종이 실제 등장했다. 최대 활성 속도0.0328386 m/s, 변위1.450674 mm, 최소 바닥1.0488784 m였고, 주차 sample71950개에서 최대 변위7.6294 μm·속도0이었다. dense phase 실제 평균 Gray/White는3.995605/5로 일부 Gray 배치 실패를 active mask로 제외했다. 이 실행에서는 bbox를 껐으며 타겟 전용 bbox는64 env 검사로 확인했다.

2048 env probe의 PyTorch peak allocated/reserved는325.93/392.00 MiB, 보고 시 CUDA free는6514.91 MiB다. 이것을 Isaac Sim 전체 peak VRAM으로 해석하지 않는다. probe의 전체 GPU 모니터링은 종료 전19초·19표본에서5490 MiB 최대를 관측했으나 초기화 이후 시작했으므로 **전체 probe 실행 peak는 미측정**이다.

[2048 env 학습 요약](../../../../outputs/revision_validation/training_summary.json)과 [학습 로그](../../../../outputs/revision_validation/train2048.log)는2048×36×2=147456 transitions, 학습16.99 s를 기록한다. 두 iteration의 로그 처리량은8797/11735 steps/s이며 수집·최적화 구간의 측정치로 초기화 시간을 포함하지 않는다. 저장한 `model_0.pt`와 `model_1.pt` 각각의 optimizer 포함100개 tensor가 모두 유한했고, 두 체크포인트 사이 Actor/Critic encoder 최대 가중치 변화는0.276063/0.137532였다. 학습 과정에 fatal error·OOM·PhysX capacity overflow는 없었으며 경고가 전혀 없었다는 뜻은 아니다. 1초 간격으로 관측한 전체 GPU 사용량 최대는5689 MiB이며 다른 프로세스도 포함한 장치 표본값으로 allocator의 실제 peak가 아니다.

이 학습은 업데이트·저장 경로의 짧은 검증이다. 초기 정책에서 선반 실패 종료가 발생했고 목표 접촉·Hold·성공 보너스 평균은0이었다. 실제 접촉에 대한 높이 gate는 별도 통제 fixture로 확인했으며, 학습 후 눌러밀기 억제와 장기 성공률은 검증하지 않았다.
