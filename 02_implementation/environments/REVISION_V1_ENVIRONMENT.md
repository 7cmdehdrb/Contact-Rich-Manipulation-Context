# Isaac-Inspire-Revision-v1 — 환경 상세 문서

2026-11-02 실제 구현 기준. 이 문서는 `Isaac-Inspire-Revision-v1`의 최종 구성을 독립적으로 설명한다. 다른 버전의 변경 내역을 읽지 않아도 과업, 관측, 제어, 장면 생성, 모든 보상·종료 조건, 커리큘럼과 학습 설정을 확인할 수 있도록 작성했다.

[활성 환경 색인](../08_ACTIVE_ENVIRONMENTS.md) · [개발 명세·보상 그래프](../../01_plan/environments/2026-11-02_REVISION_V1_SPEC.md) · [구현·리뷰·검증 기록](../logs/2026-11-02_revision_v1_implementation.md)

## 1. 과업과 기본 설정

UR5e–Axia80–Inspire Hand로 선반 위 타겟 물체를 목표 XY 위치로 밀어 이동시키는 과업이다. 장애물이 있는 장면에서 접촉 정보를 사용하며, 목표 반경은 3cm다. 목표에 들어가면 최초 진입 보상을 받고, 목표 안에서 중앙에 가까울수록 Hold 보상을 더 받는다. 목표 도달로 즉시 종료하지 않으며, 10초 timeout 시점의 XY 위치로 성공을 판정한다.

Actor는 타겟·장애물의 초기 위치, 현재 로봇 상태와 접촉 센서를 받는다. Critic은 여기에 현재 타겟 위치와 현재 장애물 위치를 사용한다. 보상·종료 판정은 시뮬레이터의 현재 실제 상태를 사용한다.

| 항목 | 최종 값 |
| --- | --- |
| Gym ID | `Isaac-Inspire-Revision-v1` |
| EnvCfg | `RevisionV1EnvCfg(RevisionEnvCfg)` |
| 실행 클래스 | `RevisionEnv(ManagerBasedRLEnv)` |
| 기본 병렬 환경 수 / 간격 | 2048 / 2.5m |
| 물리 dt / decimation | 0.01s / 2 |
| 정책·제어 step | 0.02s, 50Hz |
| 에피소드 | 최대 10s, 500 control steps |
| 물체 수 | 타겟 1 + 장애물 후보 9 = 물리 객체 10개 |
| 초기 장애물 요청 수 | Gray 3 / White 3 |
| 최종 장애물 요청 수 | Gray 4 / White 5 |
| 장애물 관측 용량 | 16슬롯 × 4값 |
| Actor / Critic 원시 관측 | 121D / 124D |
| 행동 | Arm 상대 pose 6D + Hand 2D = 8D |
| 보상 / 종료 / 커리큘럼 term 수 | 15 / 6 / 3 |
| 목표 성공 | timeout AND 유한 XY 오차 ≤0.03m |
| 기본 타겟 bbox 표시 | 꺼짐 |

별도 비교 환경 `Isaac-Inspire-Revision-Test-v1`은 v1을 직접 상속하여 타겟 형상만 cylinder로 고정한다. 이하 내용은 다양한 타겟 형상을 사용하는 **일반 v1**의 계약이다.

2026-11-03 임시 출력: Test-v1의 `debug_print_eef_height = True` 설정으로 `target_contact_below_height` reward 호출마다 모든 env의 EEF 높이(mm)를 출력한다. 기준은 접촉 보상과 동일한 초기 선반 작업면이며, 해당 설정 한 줄을 주석 처리하면 출력이 꺼진다. 보상 값과 제어는 유지한다. [작업 기록](../logs/2026-11-02_revision_v1_implementation.md#2026-11-03-test-v1-eef-높이-임시-출력).

## 2. 좌표계·로봇·센서

Test-v1 임시 시각화(2026-11-03 후속 수정): 초기 작업면 위90/95/100mm에 파랑/초록/주황 면을 표시한다. 크기0.4×1.0m, 두께0.5mm, opacity0.90이며 면 중심이 각 기준 높이다. `AssetBaseCfg` 시각 자산으로 collider·rigid body·mass·contact sensor를 추가하지 않는다. `assets/scenes/revision.py`의 `_add_temporary_eef_height_guides(self)` 호출을 주석 처리하면 모두 사라진다. 최종 정리 시 해당 호출과 helper를 삭제한다. 일반 v1은 추가하지 않는다.

### 2.1 좌표와 기준점

- **world**: 시뮬레이터 월드 좌표. 목표 보상·성공 거리에는 world XY를 사용한다.
- **robot root**: 로봇 베이스 좌표. 관측 위치와 EEF pose의 기준이다. 로봇 root의 초기 위치는 `(0,0,0.79505)m`, quaternion은 wxyz `(0,0,0,1)`이다.
- **shelf local**: 선반 좌표. 선반 root 초기 위치는 `(-0.7,0,0)m`; 작업면은 local Z=1.05m, 평면 범위는 X ±0.20m, Y ±0.50m다. 벡터 환경 origin이 월드 위치에 더해진다.
- **EEF**: `axia80_link`에서 로컬 Z 방향 0.1427m 이동한 제어·관측 기준점. F/T는 이 점으로 모멘트를 이동하고 EEF 축으로 표현한다.
- quaternion은 wxyz 순서이며 EEF 관측은 부호 중복을 제거한 quaternion을 사용한다.

### 2.2 로봇 상태와 제어 대상

Arm 순서는 `shoulder_pan_joint`, `shoulder_lift_joint`, `elbow_joint`, `wrist_1_joint`, `wrist_2_joint`, `wrist_3_joint`다. 초기 각도는 `(0,-2.2,2.2,0,1.57,0.785)rad`, 초기 관절 속도는 0이다. Inspire Hand는 12개 관절을 두 채널로 제어하며 초기 자세는 열린 손이다.

Arm actuator의 시뮬레이션 속도 제한은 `(2,2,2,4,4,4)rad/s`, effort 한계는 `(150,150,150,28,28,28)Nm`다. OSC가 torque를 직접 계산하므로 Arm actuator stiffness/damping은 0으로 설정한다.

### 2.3 접촉과 F/T

촉각은 실제 물리 접촉을 손의 정의된 영역에 투영한 17개 이진값이다. 임계값은 0.01N이다. 손목 wrench는 측정 반력에서 손 모델의 중력·관성 성분을 보상한 외력·외부 모멘트 6D이며, 단위는 N/Nm다. 보상 계산에 타겟 위치나 접촉 물체의 정체를 사용하는 방식으로 보상하지 않는다.

물체별 손 접촉 센서는 타겟과 비타겟 접촉을 구분한다. `target_contact`는 실제 타겟–손 합력, `obstacle_contact_penalty`는 비타겟 장애물–손 합력을 사용한다. 후자는 world 축 힘 벡터를 합친 뒤 norm을 취하므로 개별 접촉 힘 크기의 합과 다르다.

센서는 physics step에 갱신되고 control step에서 관측·보상에 사용된다. reset 직후 유효하지 않은 샘플은 `sensor_data_fresh`로 제외한다. 보상과 관측은 같은 물리 샘플을 공유하지만, 관측에 추가하는 촉각 반전·wrench 노이즈는 보상 계산값에 적용하지 않는다.

## 3. 관측 — 차원·순서·정보 수명

### 3.1 공통 policy 그룹: 57D

아래 인덱스는 Python의 `[start:end)` 규칙이다. 이 57D는 Actor와 Critic 모두에 들어간다.

| 인덱스 | term | 차원 | 내용·단위·좌표 | 갱신과 노이즈 |
| --- | --- | ---: | --- | --- |
| 0:6 | `joint_pos` | 6 | 실제 Arm 관절각, rad | 매 step; default pose를 빼지 않음 |
| 6:12 | `joint_vel` | 6 | 실제 Arm 관절 각속도, rad/s | 매 step |
| 12:14 | `hand_configuration` | 2 | 실제 관절에서 역산한 flexion/opposition openness, [0,1] | 매 step; 명령값과 구분 |
| 14:21 | `ee_pose` | 7 | EEF root-relative XYZ(m)+quaternion(wxyz) | 매 step |
| 21:24 | `target_obs_state` | 3 | reset 당시 타겟 위치, robot root, m | 에피소드 동안 고정; 성분별 U(−0.01,0.01)m bias를 reset 시 추출 |
| 24:26 | `goal_pos` | 2 | 초기 타겟→목표의 평면 거리(m), 시계 방향 각도(rad) | 에피소드 고정 |
| 26:34 | `actions` | 8 | 직전 실행 raw action에 tanh 적용 | 매 step; 실제 실행 action과 비용용 raw action은 별도 보존 |
| 34:51 | `tactile` | 17 | 접촉 bit | 매 관측 bit별 독립 1% 반전 |
| 51:57 | `wrist_wrench` | 6 | EEF 축의 Fx,Fy,Fz,Mx,My,Mz | 매 관측 독립 정규 노이즈: force σ=0.05N, moment σ=0.005Nm |

Hand flexion은 12개 중 thumb opposition 관절을 제외한 실제 관절값을 open/closed 범위에 최소제곱 투영한 값이다. opposition은 첫 thumb 관절에서 역산한다. 두 값은 [0,1]로 제한한다.

목표 각도는 robot root에서 `atan2(-dy,dx) mod 2π`다. +X, −Y, −X, +Y가 각각 0, π/2, π, 3π/2다. **현재 타겟에서 목표까지 남은 거리**가 아니라 초기 타겟과 고정 목표 사이의 이동 지시다.

### 3.2 장애물 그룹: 각 64D

슬롯 하나는 `[mask,x_root,y_root,z_root]`이고 16슬롯을 평탄화한다. 물리 장애물 후보는 9개여도 입력 용량은 16개다. 보고되지 않는 슬롯은 mask와 XYZ 모두 정확히 0이다.

| 구분 | Actor `obstacles` | Critic `critic_obstacles` |
| --- | --- | --- |
| 위치 | reset 당시 위치 | 현재 실제 위치 |
| 대상 | 실제 배치된 장애물 중 초기 가시성 판정 결과 | 실제 배치된 모든 활성 비타겟 |
| 가시성 | scaled bounds의 보수적 footprint 기반, threshold 0.35 | 가림 필터 없음 |
| visibility 오류 | 실제 활성 장애물에만 1% bit 반전 | 없음 |
| XYZ 노이즈 | 초기 성분별 U(−0.01,0.01)m | 없음 |
| 정렬 | 보고되는 root Y 내림차순 | 현재 root Y 내림차순 |
| 인접 순서 교환 | 유효 인접 쌍마다 10%, reset 때 추출 | 유효 인접 쌍마다 10%, 관측 호출 때 추출 |
| 수명 | reset 때 만든 64D 캐시 고정 | 매 관측 다시 계산 |

visibility 반전은 비활성·배치 실패·주차 슬롯을 관측으로 생성하지 않는다. Critic의 activity는 실제 배치 mask로 판단하므로, 활성 장애물이 에피소드 도중 밀려 선반 밖으로 나가더라도 reset 전까지 현재 위치가 보고된다. 인접 교환은 순서대로 적용되며 뒤쪽 교환은 앞선 교환 결과를 사용한다.

### 3.3 Critic 전용 현재 타겟

`privileged.target_position`은 현재 타겟 XYZ(robot root, m) 3D다. 추가 노이즈는 없다. Actor에는 이 현재 타겟 위치가 직접 제공되지 않는다.

| 입력 경로 | 그룹 순서 | 원시 차원 | 장애물 encoder 이후 |
| --- | --- | ---: | ---: |
| Actor | policy + obstacles | 57+64=121 | 57+16=73 |
| Critic | policy + privileged + critic_obstacles | 57+3+64=124 | 57+3+16=76 |

새 first-entry 지급 상태는 관측에 포함하지 않는다. Critic도 공통 policy 그룹의 센서 노이즈를 받으며, Critic 전용 현재 위치 그룹에만 추가 좌표 노이즈가 없다.

## 4. 행동과 OSC

| 채널 | 의미 | 전처리·실행 |
| --- | --- | --- |
| 0:3 | EEF 상대 위치 Δx,Δy,Δz | scale 0.03m |
| 3:6 | 상대 roll,pitch,yaw | scale 0.15rad, Euler XYZ→quaternion→axis-angle 변환 |
| 6 | Hand flexion openness | [0,1] clamp, 모든 flexion 관절의 open/closed 보간 |
| 7 | thumb opposition openness | [0,1] clamp, thumb opposition 관절 open/closed 보간 |

Hand는 1이 완전 열림, 0이 닫힘이다. Arm은 `UR10OperationalSpaceControllerAction` 구현을 UR5e 관절·EEF 설정과 함께 사용한다. 별도 task frame을 지정하지 않아 robot base 기준으로 상대 pose를 처리한다. 같은 파일의 `EEFRelativeOSCAction`을 선택한 환경이 아니다. Arm scale은 단위 action당 변환량이며 별도의 ±1 action clamp를 의미하지 않는다.

OSC는 pose_rel, fixed impedance, 6축 motion control을 사용한다. 강성은 위치 `(100,100,100)`, 회전 `(50,50,50)`, 감쇠비는 전 축1이다. full inertial dynamics decoupling과 중력 보상을 켜며 force-control 축과 nullspace control은 없다. 계산한 torque는 actuator effort limit으로 포화시키고 비유한 torque는 0으로 처리한다.

## 5. 장면·물체·reset·랜덤화

### 5.1 형상과 크기

타겟 슬롯 이름은 `mass_cylinder`지만 **일반 v1에서는 cylinder로 고정되지 않는다**. 타겟과 장애물 후보의 각 슬롯은 생성 시 8종 중 독립 균등 추출한다.

| 종류 | 기준 bounds X×Y×Z, mm |
| --- | --- |
| cylinder | 80×80×100, 반지름40mm |
| cube | 60×80×100 |
| mug | 101×70×100, 손잡이 포함 |
| bottle | 60×60×135 |
| YCB cracker box | 약98.937×43.306×128.733 |
| YCB sugar box | 약85.183×41.484×162.000 |
| YCB tomato soup can | 약76.337×76.398×114.918 |
| YCB master chef can | 약76.403×76.332×104.586 |

YCB 표의 기준은 정규화 size_fraction=0.9를 적용한 bounds다. 모든 종류의 이 기준에 U(0.9,1.1) 등방 scale을 한 번 적용한다. 형상·scale은 환경 생성 후 고정되고 reset 때 다시 선택하지 않는다. 타겟은 항상 슬롯0, Gray 후보는 다음4개, White 후보는 마지막5개다.

### 5.2 배치

타겟 초기 XY는 선반 중앙 반경20mm 원판에서 추출한다. 목표 방향을 샘플링하고, 형상 크기·선반 경계 여유20mm를 고려하여 최대150mm, 유효 이동 최소50mm 조건의 목표를 만든다. 타겟 yaw는 shelf local 0이다.

타겟 시작·목표 OBB가 만드는 이동 통로 RED, 접근 영역과 65mm 고정 padding을 포함한 Gray, 나머지 White 영역으로 장애물 역할을 배치한다. 실제 scaled bounds와 yaw를 사용하는 OBB 검사이며 물체 간격20mm, board 경계 여유5mm를 적용한다. 후보32 × restart4 × pass2의 제한 탐색에서 실제 배치 수가 가장 많은 결과를 선택하고 동률이면 Gray 수를 우선한다.

요청 수를 모두 배치하지 못하면 해당 슬롯을 비활성으로 남긴다. `layout_complete`와 actual Gray/White 수를 별도 기록하므로 요청 수와 실제 수를 구분해야 한다. 장애물 수 부족을 해결하기 위해 목표나 성공 반경을 바꾸지 않는다.

활성 물체 root Z는 scaled local bottom이 선반 위에 오도록 정한다. reset은 upright 배치이며 물체 바닥은 shelf local Z=1.05m에 정렬한다. 비활성 슬롯은 local Z=50+2×slot m에 주차하고 중력을 끈다. 비활성 mask는 collider flag를 끈다는 의미가 아니다.

### 5.3 물성 랜덤화

기본 물체 질량은 0.5475kg다. reset마다 에피소드 질량을 `1.5 × clamp(N(0.365,0.0675²),0.230,0.500)`kg로 뽑는다. 따라서 범위는 0.345~0.750kg다. **한 env의 모든 물체에 같은 에피소드 질량**을 적용한다. 각 형상의 기본 관성/질량 비율을 보존하여 관성을 갱신한다.

마찰은 아래 분포를 근사하는 4096개 bucket에서 role별로 추출한다. 음수는0으로 제한한다. static/dynamic은 독립 permutation으로 짝지으며 같은 env·같은 role의 collider들은 해당 샘플을 공유한다.

| role | static 평균 / 표준편차 | dynamic 평균 / 표준편차 |
| --- | --- | --- |
| 선반 | 0.315 / 0.051 | 0.252 / 0.041 |
| 물체 | 0.315 / 0.040 | 0.252 / 0.032 |
| 손 | 0.585 / 0.145 | 0.468 / 0.116 |

물체 contact offset은1mm, rest offset은0이다. 생성 시 geometry·collider를 scale하고 명시적 관성은 scale 제곱으로 보정한다. 형상별 prototype geometry는 공유하지만 환경별 rigid root와 물리 상태는 독립이다.

### 5.4 에피소드 수명

reset은 기본 scene 상태 복원 → 타겟/목표/장애물 배치와 초기 관측 생성 → 물성 추출을 수행한다. command는 초기 타겟 pose와 고정 목표를 저장한다. 물리 실행 후 종료 판정, 보상 계산, 종료 env의 자동 reset, 다음 관측 생성 순서로 진행하므로 terminal bonus는 reset 전 상태에서 계산된다. 부분 reset은 지정 env의 보상 history·entry latch·관측 캐시만 초기화한다.

## 6. 보상 전체 정의

### 6.1 합산과 공통 기호

control dt를 Δt=0.02s라 하면 RewardManager는 모든 term에 `weight × callable × Δt`를 적용한다. 따라서 표의 weight를 매 step 고정 금액으로 해석하면 안 된다. 최초 진입·timeout·reaching 진행량 등은 callable에서 dt를 나누어 1회 금액 또는 이동 거리당 크기를 유지한다.

공통으로 d는 타겟–목표의 world XY 거리(m), v는 타겟의 world 3D 선속도 norm(m/s), A는 실제 활성 물체 집합, O는 A에서 타겟을 제외한 집합이다. `clip(x,0,c)`는 0~c 제한이다. 지수 비용의 공통 함수는 다음과 같다.

```math
E(x;f,c)=\min\left(c,\frac{1}{2}\left[e^{2\max(0,x-f)}-1\right]\right)
```

구현은 지수를 계산하기 전에 excess를 `0.5 ln(2c+1)`까지 제한하므로 과대 입력에 대한 지수 overflow를 막는다. 아래 15항의 합이 전체 reward다.

| 순서 | term | weight | 계약 |
| ---: | --- | ---: | --- |
| 1 | `target_reaching` | 30 | 아래 항별 정의 참조 |
| 2 | `target_goal_distance` | 3.7 | 아래 항별 정의 참조 |
| 3 | `target_goal_hold` | 8 | 아래 Gaussian·free speed |
| 4 | `target_contact` | 1.45 | 아래 항별 정의 참조 |
| 5 | `robot_action_rate_penalty` | −1 | 아래 항별 정의 참조 |
| 6 | `robot_joint_velocity_penalty` | −1 | 아래 항별 정의 참조 |
| 7 | `object_tilt_penalty` | −30 | 활성 모든 물체의 기존 tilt cost |
| 8 | `obstacle_displacement_penalty` | −150 | 활성 비타겟 3D 변위 제곱합, 합산 후 cap 0.04 |
| 9 | `object_acceleration_penalty` | −0.05 | 활성 모든 물체의 기존 COM acceleration cost, free 20, 물체별 cap 100 |
| 10 | `shelf_penalty` | −1 | 아래 항별 정의 참조 |
| 11 | `obstacle_contact_penalty` | −0.05 | free force 50N, cap 100 |
| 12 | `target_goal_first_entry_bonus` | 30 | 최초 유한 XY 오차 <3cm, event/dt |
| 13 | `target_goal_timeout_bonus` | 40 | timeout 성공 event/dt |
| 14 | `wrist_wrench_change_penalty` | −0.1 | 유계 지수 곡선, 다른 보상과 budget 연동 삭제 |
| 15 | `target_speed_penalty` | −5 | 3D 속도 비용·free speed 커리큘럼 |


### 6.2 양의 연속 보상과 접근 진행량

**① target_reaching**: EEF–현재 타겟 root의 3D 거리에서 0.10m를 뺀 뒤 0 이상으로 제한한다. 이 값의 에피소드 내 최솟값을 갱신한 만큼만 보상한다.

```math
\ell_t=\max(\|\mathbf{p}_{eef,t}-\mathbf{p}_{target,t}\|-0.10,0),\quad
b_t=\min(b_{t-1},\ell_t),\quad R_{reach,t}=30(b_{t-1}-b_t)
```

기존 최단거리로 되돌아오는 움직임은 다시 보상하지 않는다. 타겟 자체가 EEF에 가까워져도 거리가 줄면 보상을 받을 수 있다. 단위는 이동한 최선 거리1m당30이며 위 R은 dt 적용 후 step 기여다.

**② target_goal_distance**: 현재 XY 오차의 지수 근접도다. 진행량 보상이 아니라 매 step 누적되는 위치 보상이다.

```math
R_{distance,t}=3.7\,e^{-d_t/0.05}\,\Delta t
```

정확히 목표 중심에서 rate3.7, step0.074다. 목표 밖에서도 양수이며 거리와 함께 감소한다.

**③ target_goal_hold**: 거리와 속도의 곱에 물리 유효성 mask V를 적용한다.

```math
P(d)=\mathbf{1}_{d<0.03}\,2\,2^{-4(d/0.03)^2},\qquad
S(v)=2^{-\left(\max(0,v-0.05)/0.05\right)^2}
```

```math
R_{hold,t}=8\,V_t\,P(d_t)\,S(v_t)\,\Delta t
```

| 거리, 속도≤0.05m/s | 위치 raw | 가중 rate | step 보상 |
| --- | ---: | ---: | ---: |
| 0cm | 2 | 16 | 0.32 |
| 1.5cm | 1 | 8 | 0.16 |
| 3cm 바로 안쪽 | 약0.125 | 약1 | 약0.02 |
| 정확히3cm 또는 바깥 | 0 | 0 | 0 |

0~0.05m/s에서는 S=1, 0.10m/s에서는 S=0.5, 0.15m/s에서는 S=0.0625다. 3cm 내부에서는 하나의 Gaussian 위치식을 쓰며 중앙에서 유한하고 미분가능하다. cutoff인3cm에는 불연속이 있다. `goal_hold_outer_radius=None`이며 8cm outer tail은 없다.

V=1 조건은 다음을 모두 만족해야 한다: 타겟 active, 위치·속도·목표XY·bottom·up alignment 유한, shelf local root X 절댓값≤0.16m 및 Y≤0.46m, 회전된 scaled bbox의 최저점이 local Z 1.04~1.07m, 타겟 up과 선반 up의 내적≥cos(0.9). 따라서 단순 XY 내부 진입과 Hold 유효 상태는 다르다.

**④ target_contact**: fresh 센서에서 실제 타겟–손 합력 norm≥0.01N이고, EEF world Z가 `초기 선반 root Z+1.05+0.12m` 미만이면 raw1이다. EEF 높이·힘은 유한해야 한다. 가중 step 보상은0.029다. 현재 타겟 크기나 선반 이동에 따라 높이 임계값을 바꾸지 않으며, 정확히120mm 높이는 지급하지 않는다.

### 6.3 로봇과 물체 비용

**⑤ robot_action_rate_penalty**: Arm raw action6D와 Hand raw action2D에 대해 직전 raw action과의 차이 제곱합을 각각100으로 제한한다. 실행용 scale·Hand clamp·관측용 tanh를 적용하기 전 값이며 dt로 미분하지 않는다.

```math
R_{action,t}=-\left[0.03\min(\|\Delta\mathbf{a}_{arm}\|^2,100)
+0.03\min(\|\Delta\mathbf{a}_{hand}\|^2,100)\right]\Delta t
```

**⑥ robot_joint_velocity_penalty**: 실제 Arm6관절과 Hand12관절 속도의 제곱합을 각각100으로 제한한다.

```math
R_{joint,t}=-\left[0.03\min(\|\dot{\mathbf{q}}_{arm}\|^2,100)
+0.01\min(\|\dot{\mathbf{q}}_{hand}\|^2,100)\right]\Delta t
```

**⑦ object_tilt_penalty**: 활성 모든 물체의 선반 법선 대비 기울기 θ를 사용한다. 5°까지 무료, 0.9rad에서 물체별 cost1이다.

```math
R_{tilt,t}=-30\sum_{i\in A}\left[\mathrm{clip}\left(
\frac{\theta_i-5\pi/180}{0.9-5\pi/180},0,1\right)\right]^2\Delta t
```

**⑧ obstacle_displacement_penalty**: 타겟을 제외한 활성 장애물의 reset 위치 대비 **3D 변위 제곱합**이다. 모든 장애물을 합산한 뒤0.04m²로 제한한다.

```math
R_{displacement,t}=-150\min\left(\sum_{i\in O}
\|\mathbf{p}_{i,t}-\mathbf{p}_{i,reset}\|^2,0.04\right)\Delta t
```

최대 비용 크기는 rate6, step0.12다. 타겟의 이동은 이 항에 포함되지 않는다.

**⑨ object_acceleration_penalty**: 활성 모든 물체의 PhysX COM 3D 선가속도 norm을 사용한다. control step 속도 차분으로 새 가속도를 계산하지 않는다.

```math
R_{acceleration,t}=-0.05\sum_{i\in A}E(\|\mathbf{a}_{COM,i}\|;20,100)\Delta t
```

20m/s²까지 무료이며 cap100은 물체마다 적용한다. reset·새 활성화 후 첫 유효 sample은 억제하고 동일 step 재호출은 cache를 사용한다. 가속과 감속을 norm으로 동일하게 취급한다. 활성10개에서 이 항의 step 비용 상한은1이다.

### 6.4 선반·접촉·손목·타겟 속도 비용

**⑩ shelf_penalty**: 선반 collision predicate C에 대한 사건 비용과 근접/움직임 비용을 합친다.

```math
R_{shelf,t}=-3C_t-0.5Q_t\Delta t
```

C는 선반 root_vel_w의6D norm>0.1 또는 wrist frame의 작업면 높이<0.03m일 때1이다. finger collision 검사는 꺼져 있다. 여기서 C는 접촉 센서의 실제 충돌 이벤트만을 뜻하는 이름이 아니며 아래 종료와 같은 상태 predicate다. 선반5cm 변위 종료 자체는 C에 추가하지 않는다.

Q는 다음과 같다. 선반 위치변화 norm과 root_vel_w norm의 합>0.005이면1을 더한다. 선반 root의 Z에1.06m를 더한 점과 EEF의 거리가0.2m 미만이면, 이 기준면 대비 두 finger frame 높이에 `clip(1-h/0.02,0,1)`을 각각 더하고 wrist frame 높이에 `clip(1-h/0.08,0,1)`을 더한다. root_vel_w는 선속도·각속도가 함께 있는6D 값이며 코드 그대로의 합산이다.

**⑪ obstacle_contact_penalty**: fresh 비타겟 장애물–손 합력의 크기 F에 대해 다음 비용을 사용한다. 다른 양의 보상과 연동되지 않는다.

```math
R_{obstacle\ contact,t}=-0.05E(F;50,100)\Delta t
```

50N까지 무료, 최대 step 비용0.1이다. stale sample은0, 비유한 힘 크기는 cap 비용으로 처리한다.

**⑭ wrist_wrench_change_penalty**: 보상용 무노이즈 EEF wrench를 사용한다. 힘·모멘트는 벡터 차이 norm이 아니라 **벡터 크기의 차이 절댓값**이다. 따라서 크기를 유지한 방향 변화만으로는 비용이 생기지 않는다.

```math
\Delta F=\left|\|\mathbf{F}_t\|-\|\mathbf{F}_{t-1}\|\right|,\quad
\Delta M=\left|\|\mathbf{M}_t\|-\|\mathbf{M}_{t-1}\|\right|
```

```math
u=\mathrm{clip}\left(\max\left(
\frac{\max(\Delta F-20,0)}{30},
\frac{\max(\Delta M-2,0)}{3}\right),0,1\right),\quad
R_{wrench,t}=-0.1\frac{e^{3u}-1}{e^3-1}\Delta t
```

20N/2Nm까지 무료, 변화50N 또는5Nm에서 포화한다. ΔF/ΔM 자체를 dt로 나누지 않는다. raw 상한1, step 비용 상한0.002다. 첫 sample·이전 invalid history·stale sample은 억제하고 부분 reset은 해당 env만 초기화한다. 이전 sample이 유효한 상태에서 현재 fresh sample이 비유한이면 raw 포화 비용을 사용하고 이후 history는 무효화한다. 양의 보상 누적액에 대한5% budget은 없다.

**⑮ target_speed_penalty**: 타겟의 3D 선속도 v에 대해 다음 비용을 사용한다.

```math
R_{speed,t}=-5E(v;v_{free}(k),100)\Delta t
```

상한은 step10이며 free speed만 커리큘럼으로 변경한다. Hold의 무감쇠 한계0.05m/s와 **서로 다른 파라미터**다. 후반에는 이 항의 free speed가0.02m/s이므로 0.02~0.05m/s 움직임은 Hold 속도 감쇠는 없지만 target speed 비용은 받을 수 있다.

### 6.5 최초 진입·timeout 사건 보상

**⑫ target_goal_first_entry_bonus**는 에피소드에서 처음으로 유한 XY 거리 d<0.03m를 관측한 step에+30이다. 속도·높이·자세·접촉·Hold 유효성 조건을 추가하지 않는다. 같은 step에 실패해도 지급하며 재진입은 중복 지급하지 않는다. env별 latch는 reset에서 초기화하고 같은 step 재호출은 기존 결과를 반환한다.

**⑬ target_goal_timeout_bonus**는 timeout 성공 term이 참일 때+40이다. 기존 성공 판정인 유한 d≤0.03m를 그대로 사용한다. 두 callable 모두 event/Δt를 반환하여 dt가 바뀌어도 사건 금액을 유지한다.

| 에피소드 상황 | entry 총액 | timeout 금액 | 두 보너스 합 |
| --- | ---: | ---: | ---: |
| 내부 최초 진입 후 timeout도 내부 | 30 | 40 | 70 |
| 진입했지만 timeout 때 외부 | 30 | 0 | 30 |
| 처음 진입한 step이 성공 timeout | 30 | 40 | 70 |
| 최초 strict 진입 없이 정확히3cm에서 timeout | 0 | 40 | 40 |
| timeout 전 고속/공중 진입과 실패 동시 발생 | 30 | 0 | 30 |
| 진입 없음, timeout 외부 | 0 | 0 | 0 |

두 보너스의 episode 합 상한은70이며 전체 reward 상한을 뜻하지 않는다. 처음과 끝에 나누어 지급하므로 PPO 할인 return에서70을 한 번에 받는 것과 다르다. 현재 control step의 위치만 검사하므로 두 sample 사이에만 목표 영역을 통과한 궤적은 검출을 보장하지 않는다.

## 7. 종료·성공·실패

| term | 조건 | 분류 |
| --- | --- | --- |
| `object_fall_or_tilt` | 활성 물체 중 bbox bottom 비유한 또는 작업면보다10mm 초과 낮음 또는 tilt≥0.9rad | terminated |
| `target_speed` | 타겟3D 선속도>1m/s | terminated |
| `shelf_failure` | C 조건(선반6D root velocity norm>0.1 또는 wrist 높이<3cm) 또는 선반 root 초기 대비3D 변위>5cm | terminated |
| `arm_joint_velocity` | Arm 어느 관절이든 절대 각속도>5rad/s | terminated |
| `target_goal_success_at_timeout` | timeout AND 유한 d≤3cm | truncated |
| `target_goal_miss_at_timeout` | timeout AND 성공 조건 불만족 | truncated |

여러 조건이 동시에 참일 수 있다. 실패와 성공 timeout이 동시에 참인 경우 성공 timeout 보너스를 제거하는 우선순위를 추가하지 않는다. 목표 도달 자체는 조기 종료 조건이 아니다. 성공 판정에는 속도·체류시간·Hold 유효성 검사가 없으므로 “성공 timeout”과 “부드럽게 중앙 정지”를 동일한 지표로 해석하면 안 된다.

## 8. 커리큘럼과 고정값

iteration k는 PPO learning iteration이며 simulation step 수가 아니다. 활성 term은 다음3개다. runner가 rollout 전에 절대 iteration을 반영하므로 resume·rewind에서도 해당 시점 값을 재계산한다.

| iteration | Gray 요청 | White 요청 |
| --- | ---: | ---: |
| 0~9999 | 3 | 3 |
| 10000~11999 | 3 | 4 |
| 12000~13999 | 4 | 4 |
| 14000 이후 | 4 | 5 |

`obstacle_population`은 White start10000, Gray start12000, 역할별 interval4000으로 위 교대 일정을 만든다. 수 변경은 다음 reset에 적용하며 진행 중 episode의 active mask를 바꾸지 않는다.

`target_free_speed`는 점 `(0,0.10),(499,0.10),(500,0.09),(1900,0.02)`와 interval250을 사용한다. 500≤k<1900에서 실제 값은 다음처럼 구간 시작점500을 기준으로250 단위 양자화한 보간이다.

```math
v_{free}(k)=0.09-0.07\frac{250\lfloor(k-500)/250\rfloor}{1400}
```

k<500은0.10, k≥1900은0.02m/s다. 예를 들어500→0.09,750→0.0775,1000→0.065,1250→0.0525,1500→0.04,1750→0.0275,1900→0.02다.

`target_goal_direction_deadzone`은 ±X 방향 제외 반각을30°로 시작한다. 실제 식은 `max(0,30−5×max(0,floor((k−3000)/500)))`도다. 따라서3000에서도30°, 최초 감소3500에서25°, 이후500마다5°씩 줄어6000에서0°다. 새 방향 조건도 다음 reset 배치에 적용한다.

다음은 커리큘럼 없이 처음부터 끝까지 고정이다.

| 대상 | 고정값 |
| --- | --- |
| object acceleration | weight −0.05 / free20m/s² / 물체별 cap100 |
| obstacle contact | weight −0.05 / free50N / cap100 |
| wrist wrench change | weight −0.1 / free20N·2Nm / raw cap1 |
| 목표 반경 | 0.03m |
| Hold free speed / scale | 0.05 / 0.05m/s |
| Gray padding | 0.065m |

`object_acceleration_weight`, `object_free_acceleration`, `obstacle_contact_free_force`, `obstacle_contact_weight`, `wrist_wrench_change_weight`, `wrist_wrench_free_force_change`, `wrist_wrench_free_moment_change`는 모두 비활성이다.

## 9. 정책·Critic·PPO

Actor와 Critic은 독립 장애물 encoder를 가진다. 각 encoder는64→32→16, ReLU이며 mask0인 슬롯의 좌표는 encoder 전에0으로 만든다. 두 encoder는 가중치를 공유하지 않는다. rollout에는 raw 관측을 저장하고 PPO 학습에서 encoder를 다시 계산해 각각 gradient를 전달한다.

| 항목 | 설정 |
| --- | --- |
| Actor 본체 | 73→256→128→64→8, ELU |
| Critic 본체 | 76→256→128→64→1, ELU |
| 관측 정규화 | 꺼짐 |
| 정책 분포 | Gaussian, 초기 std1.0 |
| Runner | CurriculumOnPolicyRunner |
| rollout | 36 steps/env, 기본2048 env에서73728 transitions/iteration |
| 최대 iterations / 저장 간격 | 90000 / 50 |
| learning rate / schedule | 0.001 / adaptive |
| epochs / minibatches | 8 / 4 |
| PPO clip / value loss coefficient | 0.2 / 1.0, clipped value loss 사용 |
| entropy coefficient | 0.005 |
| gamma / GAE lambda | 0.98 / 0.95 |
| desired KL / max gradient norm | 0.02 / 1.0 |
| experiment_name | inspire_revision_v1 |

## 10. 로그와 실행

`Episode_Reward/<term>`으로15개 보상 항을 개별 기록한다. 연속 항·사건 항이 섞여 있으므로 logged episode 값과 사건당30/40을 구분해야 한다. RewardManager의 episode 요약은 누적 기여를 `max_episode_length_s`로 나눈 값이다.

runtime은 episode 중 유한 sample의 target_goal_distance_xy, eef_linear_speed, target_linear_speed, target_linear_acceleration 평균과 force/moment 최대값을 기록한다. 배치 지표는 `Metrics/obstacle_actual_gray`, `Metrics/obstacle_actual_white`, `Metrics/layout_complete`다. `max_force`/`max_moment` 로그는 reset된 env 각각의 episode 최대값을 평균한 값이다. 거리 평균과 timeout 최종 오차는 서로 다른 통계다.

Workspace 루트에서 Isaac Lab Python 환경을 활성화한 뒤 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Revision-v1 --num_envs 2048 --headless
```

기본 학습 로그는 `logs/rsl_rl/inspire_revision_v1/<timestamp>/`다. 선반은 기본 `omniverse://192.168.0.13/Library/Shelf/Arena/Collected_speedrack_shape/speedrack_shape.usd`를 사용하고, `INSPIRE_SWEEP_SHELF_USD_PATH`로 에셋 위치를 지정할 수 있다. 로봇은 패키지 USD, YCB는 NVIDIA 자산 경로를 사용한다.

## 11. 코드 위치와 검증 범위

아래 파일은 `src/inspire_sweep_baseline/inspire_sweep_baseline/` 기준이다. 직접 확인할 핵심 소스는 [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/revision_envs.py), [관측 CFG](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/revision.py), [보상 CFG](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/revision.py), [v1 보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/revision.py)다.

| 역할 | 파일 |
| --- | --- |
| 환경 조합·v1 override | `envs/revision_envs.py` |
| step/reset·계측 | `runtime/revision.py` |
| scene·spawner | `assets/scenes/revision.py`, `assets/revision_spawners.py` |
| 관측 | `mdp/observations/revision.py`, `mdp/observation_functions/revision.py`, `final.py`, `contact_sweep_clutter.py` |
| 제어 | `mdp/actions/revision.py`, `mdp/action_functions/hand_openness.py`, `contact_sweep_clutter_fusion_holding_osc.py` |
| 배치·reset | `mdp/event_functions/revision.py`, `mdp/common/revision_layout.py`, `bbox_scene_layout.py` |
| 보상 등록 | `mdp/rewards/revision.py` |
| Hold·entry·wrist | `mdp/reward_functions/revision.py` |
| 비용 공통 계산 | `mdp/reward_functions/contact_sweep_clutter_fusion.py`, `final.py`, `goal_rewards.py`, `sweep.py` |
| Hold 물리 유효성 | `mdp/common/revision_goal.py` |
| 종료 | `mdp/terminations/revision.py`, `mdp/termination_functions/revision.py`, `final.py`, `sweep.py` |
| 커리큘럼 | `mdp/curricula/revision.py`, `mdp/curriculum_functions/contact_sweep_clutter_fusion_holding.py` |
| 모델·학습 | `agent/revision_models.py`, `agent/revision_ppo_cfg.py`, `agent/curriculum_runner.py` |

구현 시 CPU·회귀111개, v1의 GPU64/2048환경 초기화·rollout·부분reset, 실제 최초 진입/timeout/실패 보상 순서, 공식 train.py의2048환경 PPO2iterations를 검증했다. 체크포인트·optimizer tensor와 로그 scalar가 유한하고 Actor/Critic의 장애물 encoder가 갱신됨을 확인했다. 규칙·명세 독립 리뷰의 최종 지적은0건이다.

이 검증은 장기 성공률이나 정확한 중앙 정지 개선을 입증하지 않는다. 상세 실행 조건과 산출물은 [구현 로그](../logs/2026-11-02_revision_v1_implementation.md)에 있다. 본 문서 작성에서는 소스 변경·추가 GPU 실행 없이 실제 코드와 기존 검증 결과를 확인했다.
