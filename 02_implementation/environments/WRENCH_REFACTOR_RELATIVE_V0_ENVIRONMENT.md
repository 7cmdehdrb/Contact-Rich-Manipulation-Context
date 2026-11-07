# Refactor-Relative-v0 환경 명세

2026-11-07 갱신: 보정·noise 이후 F/T 관측 힘±150N·모멘트±8N·m 및 raw Action Rate 그룹별 cap100을 추가했다. v2/v3에 공통 상속된다. [구현·검증 기록](../logs/2026-11-07_relative_observation_action_limits.md).

2026-11-06 최종 갱신: Axia 질량을 v0부터 **0.280kg**으로 설정한다. 활성 Relative 환경은 v0·v2·v3이며 v1은 삭제했다. EEF pose를 제외한 공간 관측은 EEF 기준이다. [변경·검증 기록](../logs/2026-11-06_relative_family_280g_v3.md).

2026-11-07 실제 코드의 기본 설정 기준. 이 문서는 다른 환경 설명서를 읽지 않아도 환경의 생성, 초기화, 입력과 출력, 보상, 종료, 학습 난이도 변화를 이해할 수 있도록 작성했다. 명령행으로 설정을 덮어쓴 실행은 아래 기본값과 다를 수 있다.

## 1. 과업과 기본 구성

오른손이 장착된 로봇으로 선반 위 타겟 물체를 밀어 목표 XY 위치에 옮기고 안정적으로 정지시키는 과업이다. 초기 물체 위치 정보와 실행 중 관절·촉각·손목 F/T를 사용한다. Actor와 Critic은 동일한 관측을 받고, 현재 타겟·장애물의 실제 위치는 보상·종료·평가 계산에 사용한다.

| 항목 | 설정 |
| --- | --- |
| Gym 환경 ID | `Inspire-Wrench-Refactor-Relative-v0` |
| 기본 병렬 환경 수 | 2048 |
| 환경 간격 | 2.5m |
| 물리 간격 | 0.01초, 100Hz |
| 제어 간격 | 물리 2step당 1회, 0.02초, 50Hz |
| 에피소드 시간 한도 | 10초, 최대500 제어step |
| 로봇 | UR5e 6축 Arm + Inspire 오른손12관절 |
| Axia 하우징 질량 | 0.280kg; Relative-v0 및 모든 파생 환경 공통 |
| 손 질량 | 0.790kg; 손의 질량·관성 비례 보정 |
| 선반 | 질량30kg; 기본 위치는 환경 원점 대비 (−0.7, 0, 0)m |
| 작업면 | 선반 local Z=1.05m, XY 범위 약 [−0.20, 0.20]×[−0.50, 0.50]m |
| 물리 물체 수 | 환경마다 타겟1개 + 장애물 후보16개 = 17개 |
| 실제 활성 물체 수 | 타겟1개 + 장애물0–6개 |
| 정책 입력 | 직접 관측58D + 장애물64D = 122D |
| encoder 이후 입력 | 직접 관측58D + 장애물 embedding16D = 74D |
| 액션 | Arm6D + Hand2D = 8D |

### 1.1 좌표계와 기준점

- **World**: 시뮬레이터 전체 좌표계다. 여러 환경은 서로 다른 world 원점에 배치된다.
- **Base**: 로봇 root 좌표계다. EEF pose 관측을 이 좌표계로 표현한다.
- **Shelf**: 선반의 local 좌표계다. 초기 배치 영역·목표 방향·물체 바닥 검증에 사용한다.
- **EEF**: 손목 센서 링크 `axia80_link`에 붙은 제어·관측 좌표계다. 위치 offset은 (0, 0, 0.1427)m, 회전 offset quaternion은 (0.5, −0.5, −0.5, −0.5)다. quaternion 순서는 `(w, x, y, z)`다.

EEF는 손가락 관절의 굽힘과 독립적인 손목 부착 기준점이다. Arm 액션, 초기 타겟·goal·장애물의 상대 위치, 보정 F/T는 이 EEF를 기준으로 한다. EEF 자체의 pose는 base 기준으로 관측한다.

타겟 위치는 물체 link 원점이다. 원통 타겟의 원점은 바닥에 있으며, 물체 중심이나 윗면을 의미하지 않는다. 목표 거리와 성공 반경은 world XY 평면에서 계산한다. 관측이 XYZ라는 사실이 성공 판정을 3D 거리로 바꾸지는 않는다.

### 1.2 로봇 초기 상태와 구동 한도

로봇 root는 환경 원점 대비 (0, 0, 0.79505)m, quaternion (0, 0, 0, 1)이다. Arm 초기 위치는 아래 순서의 rad 값이며, 초기 속도는0이다. Hand는 모든 관절0rad의 열린 자세로 시작한다.

| Arm 관절 | 초기 위치 | 토크 한도 | 물리 속도 한도 |
| --- | --- | --- | --- |
| shoulder_pan | 0 | 150Nm | 3.14rad/s |
| shoulder_lift | −2.2 | 150Nm | 3.14rad/s |
| elbow | 2.2 | 150Nm | 3.14rad/s |
| wrist_1 | 0 | 28Nm | 3.14rad/s |
| wrist_2 | 1.57 | 28Nm | 3.14rad/s |
| wrist_3 | −π/2 | 28Nm | 3.14rad/s |

Arm actuator의 position stiffness/damping은0이며 OSC가 토크를 계산한다. Hand12관절은 URDF 한도인 effort10Nm·velocity1rad/s를 사용하고 stiffness1.2, damping0.06, armature0.0001이다. Hand action은12관절을2개 openness 명령으로 제어한다. 소스의 `inspire_left_*` 관절명은 호환용 이름이며 실제 형상·관절축은 오른손이다.

### 1.3 물체 구성과 초기 물성

타겟은 원통으로 고정되어 있다. 원통 기준 반지름은0.04m, 높이는0.10m이고, 개체마다 한 번 정한 등방 크기 배율 U(0.9, 1.1)을 적용한다. 따라서 타겟 반지름은3.6–4.4cm, 높이는9–11cm다.

장애물 후보는 다음8종을 각각2개씩 보유한다.

| 종류 | 기준 형상 |
| --- | --- |
| cylinder | 반지름4cm·높이10cm 원통 |
| cube | 6×8×10cm 기준 형상 |
| mug | 6×8×10cm 기준 mesh 생성 입력 |
| bottle | 6×8×10cm 기준 mesh 생성 입력 |
| 003_cracker_box | YCB asset, size_fraction0.9 |
| 004_sugar_box | YCB asset, size_fraction0.9 |
| 005_tomato_soup_can | YCB asset, size_fraction0.9 |
| 002_master_chef_can | YCB asset, size_fraction0.9 |

모든 개체의 크기 배율은 환경 생성 때만 추출한다. 실제 mesh bounds를 크기에 맞춰 읽어 배치·충돌 회피·바닥 정렬에 사용하므로 mug/bottle의 생성 입력 크기를 최종 실측 bounding box라고 가정하지 않는다. reset 때 종류·크기를 다시 생성하지 않는다.

각 물체의 질량은 startup에 독립적으로 U(0.230, 0.500)×1.5kg, 즉 **0.345–0.750kg**로 정하고 관성도 질량 비율에 맞춰 조정한다. 마찰은 아래 범위의4096개 균등 bucket에서 선택한다. 선반·손은 환경별, 물체는 개체별로 할당한다.

| 접촉 재질 역할 | 정지 마찰 범위 | 동마찰 범위 |
| --- | --- | --- |
| 선반 작업면 | 0.213–0.417 | 0.170–0.334 |
| 물체 | 0.235–0.395 | 0.188–0.316 |
| 손 | 0.295–0.875 | 0.236–0.700 |

이 질량·마찰·크기는 이후 reset에서도 유지한다. reset은 물체의 위치·자세·활성 여부를 다시 정하는 과정이다.

## 2. 초기화와 목표 설정

### 2.1 생성 시 초기화

1. 로봇·선반·17개 물리 물체와 센서를 생성한다. 물체는 작업면에 바로 놓기 전에 중력을 끈 주차 위치에 둔다.
2. 물리 시작 전 각 개체의 실제 크기와 local bounds를 읽는다. 작업면에 바닥이 닿도록 `spawn_z = 1.05 − local_bbox_min_z`를 계산해 저장한다.
3. startup에서 질량·관성·마찰을 설정한다. 실행 중 이 초기화가 중복 적용되지 않도록 보호한다.
4. reset에서 로봇·선반·물체의 기본 상태를 복원하고, 아래 배치 절차로 활성 물체의 상태를 덮어쓴다. 배치가 끝난 후 goal command와 초기 관측을 확정한다.

### 2.2 에피소드 reset

1. Gray 장애물 수와 White 장애물 수를 각각 `{0,1,2,3}`에서 균등하게 뽑는다. 두 수는 별도로 추출하며 합계는0–6이다.
2. 타겟 초기 XY와 목표 XY를 정한다.
3. 후보16개에서 서로 다른6개를 무작위로 뽑고, 요청된 Gray/White 수만큼 배치한다. 활성 후보·위치·yaw는 reset마다 바뀔 수 있다.
4. 실제 크기를 반영한 회전 bounding box인 OBB로 작업면 경계, 금지 구역, 물체 간 간격을 검사한다. 활성 물체의 바닥을 캐시된 높이로 작업면에 정렬하고 선속도·각속도를0으로 쓴다.
5. 활성 물체는 중력을 켜고, 나머지는 선반 local 위치 `(0, 0, 50+2i)m`로 분리 주차하고 중력을 끈다. `i`는0–16의 물리 슬롯 번호다. 중력 flag를 바꾼 물체는 wake-up한다. 주차 물체는 활성 판정·관측·보상·종료의 물체 목록에서 제외한다.
6. command가 타겟 초기 link state와 고정 goal을 저장한다. 장애물의 초기 위치·가시성·노이즈·순서를 저장한다. 보상·성공 누적 시간·센서 history를 reset한다.
7. Hand action history를 열린 값1로 두고 초기 관측을 계산한다. reset 직후 아직 신선하지 않은 접촉/F/T 물리 샘플은 유효한 접촉으로 쓰지 않는다. 이후 관측 노이즈가 적용되므로 정책에 보이는 값이 항상 정확히0인 것은 아니다.

부분 reset은 선택된 환경에만 적용한다. 타겟·장애물 생성과 배치는 이 reset 과정에서 수행하며 에피소드 중간에 새 물체를 추가 생성하지 않는다. 배치 탐색이 실패하면 같은 목표·요청 개수로 재시도한다. 재시도도 실패하면 오류를 내며 목표를 몰래 바꾸거나 장애물 수를 줄이지 않는다.

### 2.3 타겟 초기 위치와 goal 샘플링

타겟 초기 XY는 선반 중심 반지름2cm 원판에서 **면적 균등**으로 추출한다. 반지름을 `0.02×sqrt(U)`로 뽑으며 방위각은0–2π 균등이다. 타겟 초기 yaw는0이고 장애물 yaw는 OBB 배치 탐색에서 정한다.

목표는 타겟 시작점에서6–12cm 떨어진 XY 위치다. 선반 local +X/−X 방향 주변은 현재 curriculum 금지 반각만큼 제외하고 나머지 방향에서 방위각을 균등 추출한다. +Y와−Y 양쪽 방향을 모두 사용한다.

목표 방향의 단위벡터를 `v`, 타겟 시작점을 `p0`, 타겟의 보수적 XY 반폭을 `h`라고 하면 목표 중심의 허용 범위는 다음과 같다.

```text
safe = (0.20, 0.50) - h - 0.02
목표 중심의 각 좌표 절댓값 <= safe
Lmax = min(0.12, 해당 방향으로 safe 경계까지의 거리)
L ~ Uniform(0.06, Lmax)
goal_xy = p0_xy + L * v
```

방향을 먼저 균등 추출한 다음 그 방향에서 가능한 거리를 균등 추출한다. 환형 영역의 면적 균등 분포를 의미하지 않는다. 마지막0.02m는 목표 물체 footprint와 선반 경계 사이 여유다.

goal Z는 타겟 초기 link 원점 Z로 두며, command에는 초기 orientation도 저장하지만 정책에는 goal XYZ만 제공한다. goal은 에피소드 동안 고정된다. command 재추출 주기는1,000,000초로 설정되어10초 에피소드 중 시간 경과에 따른 goal 변경은 일어나지 않는다. 시각화 구의 반지름은3cm이며 실제 도달 판정은 XY 거리3cm 이하이다.

### 2.4 장애물 배치 구역

구역은 타겟 시작점·goal·물체 footprint를 이용해 reset마다 정한다. Gray/White는 배치 구역 이름이며 별도의 물리 재질 종류가 아니다.

- **Red**: 타겟이 goal까지 이동하며 차지하는 swept footprint와 손목 진입 방향 확장 영역에23mm 여유를 둔 금지 구역이다. 장애물을 놓지 않는다.
- **Gray**: Red 주변으로65mm 확장한 영역과 타겟 뒤쪽 접근 직사각형의 합집합에서 Red를 제외한다. 뒤쪽 직사각형은 길이160mm·폭220mm이며 타겟에서20mm 후퇴시킨다.
- **White**: 작업면에서 Red·Gray를 제외한 영역이다.

구역 소속은 물체 중심만이 아니라 OBB footprint의 교차로 판정한다. 배치의 작업면 경계 여유는5mm, 초기 물체 간 최소 분리 간격은20mm다. 목표 샘플링의 경계 여유20mm와 서로 다른 값이다.

## 3. 관측

### 3.1 Actor·Critic·Rollout Storage

Actor와 Critic은 모두 `policy`와 `obstacles`라는 **동일한 관측 텐서**를 입력으로 받는다. 노이즈도 이미 적용된 같은 값이다. Critic 전용 현재 타겟 위치나 현재 장애물 GT 그룹은 없다. Rollout Storage에도 이 두 그룹만 저장한다.

Actor와 Critic의 네트워크 및 장애물 encoder 가중치는 별개다. 관측을 공유한다는 것이 가중치까지 공유한다는 뜻은 아니다. 보상·종료는 현재 실제 물체 상태를 조회할 수 있지만 이 값을 별도 관측으로 붙이지 않는다.

### 3.2 직접 관측: policy 58차원

인덱스는 Python slice 표기이며 끝 인덱스는 포함하지 않는다.

| 인덱스 | 차원 | 내용 | 기준·단위·갱신 |
| --- | --- | --- | --- |
| 0:6 | 6 | Arm joint position | 실제6관절 위치, rad, 매step |
| 6:12 | 6 | Arm joint velocity | 실제6관절 속도, rad/s, 매step |
| 12:14 | 2 | Hand configuration | 실제 관절에서 역산한 flexion/opposition openness, [0,1] |
| 14:21 | 7 | EEF pose | base 기준 XYZ(m) + quaternion(w,x,y,z), 매step |
| 21:24 | 3 | 초기 타겟 추정 위치 | 현재 EEF 기준 XYZ(m) |
| 24:27 | 3 | 고정 goal 위치 | 현재 EEF 기준 XYZ(m) |
| 27:35 | 8 | 직전 실행 action | raw8D에 성분별 tanh 적용 |
| 35:52 | 17 | tactile | palm/dorsal 대응쌍 상태, −1/0/1/2 |
| 52:58 | 6 | 손목 F/T | EEF 기준 Fx,Fy,Fz(N), Mx,My,Mz(Nm) |

Arm 관절은 기본 자세를 뺀 값이 아니라 실제 위치·속도다. 순서는 shoulder_pan, shoulder_lift, elbow, wrist_1, wrist_2, wrist_3이다. Hand configuration은 action 복사본이 아니다. thumb1의 실제 위치에서 opposition을, 나머지11관절의 open/closed 목표에 대한 최소제곱 투영에서 flexion을 계산하고0–1로 제한한다.

EEF quaternion은 부호를 정규화한 표현이다. EEF pose를 EEF 기준으로 표현하면 항상 항등 pose가 되므로 이7차원만 base 기준을 유지한다. 관절·Hand configuration·action 이력은 관절 또는 명령 공간의 값으로 좌표변환 대상이 아니다.

### 3.3 초기 타겟과 goal의 EEF 표현

관측의 타겟 위치는 **현재 타겟 위치가 아니라 에피소드 초기 위치**다. reset마다 초기 base 좌표의 각 성분에 U(−0.01, 0.01)m bias를 한 번 추출해 고정한다. 이후 해당 추정점을 현재 EEF로 변환한다.

```math
\mathbf{p}^{E}_t = (R^{W}_{E,t})^{T}
\left(\hat{\mathbf{p}}^{W}_0-\mathbf{p}^{W}_{E,t}\right)
```

여기서 초기 추정점은 에피소드 동안 고정되고 EEF 위치·회전만 매step 바뀐다. 타겟을 실제로 밀어도 그 이동이 타겟 위치 관측에 직접 갱신되지 않는다. bias를 EEF 변환 전에 더하므로 EEF 회전에 따라 world상의 초기 추정 오차가 함께 회전하는 문제를 피한다. `enable_corruption=False`이면 bias를 적용하지 않는다.

goal도 같은 식으로 현재 EEF에 대한 상대 XYZ를 계산하되, 고정된 실제 command 위치를 사용하며 추가 위치 noise는 없다. goal 관측으로 현재 타겟의 변위를 제공하지 않는다.

### 3.4 장애물: obstacles 64차원과 MLP

16슬롯 각각이 `[mask, x, y, z]`의4차원으로 총64차원이다. reset에서 실제 배치한 장애물에 대해 가시성 판단과 노이즈를 적용한 초기 snapshot을 만든다.

| 항목 | 설정 |
| --- | --- |
| 가시성 | 선반 기준 초기 위치·크기의 보수적 평면 반경으로 occlusion 판정; 전체 지름 대비 보이는 투영 폭의 비율이0.35 이상이면 visible |
| 가시성 오류 | 실제 활성 장애물의 visible bit를 확률1%로 반전 |
| 좌표 오차 | 초기 base XYZ 각 성분에 U(−0.01,0.01)m |
| 순서 | 보고된 장애물을 base Y 내림차순 정렬 후 인접한 유효쌍을 확률10%로 교환 |
| 시간 갱신 | 선택·오차·순서는 reset 시 고정; 매step 좌표만 현재 EEF로 변환 |
| 미관측/빈 슬롯 | mask와 XYZ를 모두0으로 유지 |

가시성 반전으로 주차 후보가 관측에 생기지는 않는다. 활성 장애물 중 관측되는 것만 포함한다. 관측에서 빠진 활성 장애물도 물리·보상·종료에는 존재한다. 실제 장애물이 이동해도 입력은 초기 추정 위치를 유지하며, EEF 축을 기준으로 재정렬하지 않는다.

각 네트워크는64차원을 `64→32(ReLU)→16` MLP로 인코딩한다. encoder 입력에서 mask가0인 행은 다시0으로 만든다. 그16차원과 직접58차원을 합쳐74차원을 Actor/Critic 본체에 넣는다. 본체 hidden 크기는256/128/64, 활성화는ELU, 관측 정규화는 비활성이다. Actor 출력은8차원, Critic 출력은1차원이다. 따라서 **122D는 저장·외부 입력 차원**, **74D는 encoder 결합 후 본체 입력 차원**이다.

### 3.5 촉각17차원

17개 palm 채널과 각각 대응하는17개 dorsal 채널을 한 쌍으로 묶는다. 순서는 손바닥1개, 엄지4개, 검지·중지·약지·소지 각각3개다. 같은 부모 link의 앞·뒤 표면 접촉점을 분리하여 검출하며, 각 채널의 힘 크기가0.05N 이상이면 bit1이다.

| Palm | Dorsal | 의미 | 코드 |
| --- | --- | --- | --- |
| 0 | 0 | 접촉 없음 | 0 |
| 1 | 0 | 손바닥 면 접촉 | +1 |
| 0 | 1 | 손등 면 접촉 | −1 |
| 1 | 1 | 양쪽 접촉 | +2 |

인코딩은 `palm − dorsal + 2×palm×dorsal`이다. 센서 오류는 원래34개의 bit 각각을 독립적으로1% 확률로 반전시킨 것과 같은 방식으로 적용한 후17개 상태로 표현한다. 코드2는 힘이2배라는 뜻이 아니라 양쪽 접촉 상태다. 이 촉각 관측의0.05N 기준과 접촉 보상의 타겟–손0.01N 기준은 별개다.

### 3.6 F/T 6차원

손목 반력에서 손의 질량·관성·운동으로 설명되는 성분을 보정하여 EEF 기준 외부 wrench를 추정한다. 기준점 이동에 따른 moment도 EEF 위치로 맞춘다. 물체 정답 위치나 접촉 대상의 identity를 입력으로 사용해 보정하지 않는다.

관측에는 힘 성분별 표준편차0.05N, 모멘트 성분별 표준편차0.005Nm의 독립 영평균 Gaussian noise를 더한다. 초기 무효 물리 샘플은0으로 처리한 뒤 관측 noise를 적용한다. wrench 변화 보상은 이 보정 신호의 관측 noise 적용 전 값을 사용한다.

2026-11-07부터 **보정·EEF 변환·noise 이후** 최종 관측을 각 힘 성분±150N, 각 모멘트 성분±8N·m로 제한한다. `wrist_wrench_observation_limits`는 Relative-v0에 정의하며 v2의 별도 Critic과 v3에도 상속된다. noise를 끈 평가에서도 동일한 한도를 적용한다. raw joint reaction, 손의 질량·관성 보정, 보상/진단의 보정 wrench는 clipping하지 않는다. [구현·보정 검증](../logs/2026-11-07_relative_observation_action_limits.md).

## 4. 액션

### 4.1 8차원 구성

| 인덱스 | 의미 | 처리 |
| --- | --- | --- |
| 0:3 | EEF local XYZ 위치 증분 | raw 값×0.03m |
| 3:6 | EEF local roll/pitch/yaw 증분 | raw 값×0.15rad |
| 6 | Hand flexion openness | [0,1] clamp; 0닫힘·1열림 |
| 7 | Hand thumb opposition openness | [0,1] clamp; 0닫힘·1열림 |

Arm 명령은 현재 EEF pose에서의 **상대 pose 명령**이다. 속도 명령이나 직접 토크 명령이 아니다. Arm raw action은 기본 설정에서±1로 clip하지 않으므로0.03m와0.15rad는 배율이며 절대 이동 상한이 아니다. 관측에 반환하는 tanh(action)도 실제 제어값과 Action Rate 계산값을 바꾸지 않는다.

### 4.2 EEF 기준 OSC

매 제어step 시작 시 offset을 포함한 현재 EEF pose를 task frame으로 복사하고, 그step의 두 물리 substep 동안 명령 기준축을 고정한다. EEF가 회전하면 다음step의 +X 명령은 새 EEF의 +X 방향을 따른다.

회전3성분은 RPY로 quaternion을 만든 뒤 OSC가 사용하는 axis-angle 형식으로 변환한다. OSC는 물리step마다 실제 pose·속도·Jacobian·질량행렬·중력을 갱신하고 관절 토크를 계산한다. EEF offset에 대한 Jacobian과 선속도 lever-arm 보정을 적용한다.

| OSC 설정 | 값 |
| --- | --- |
| target type | pose_rel |
| 병진 stiffness | XYZ 각각100 |
| 회전 stiffness | RPY 각각50 |
| damping ratio | 6축 모두1 |
| impedance | fixed |
| motion 제어 | 6축 활성 |
| wrench 목표 제어 | 비활성 |
| 관성 분리 | full inertial dynamics decoupling |
| 중력 보상 | 활성 |
| nullspace 제어 | 없음 |

출력 토크는 각 Arm 관절 한도로 제한한다. 한 환경의 계산 토크 중 nonfinite가 있으면 그 환경6축 토크를0으로 만든다. F/T 관측이 존재하지만 F/T 목표를 추종하는 force-control action은 아니다.

### 4.3 Hand mapping

Hand 목표는 `q_target = q_closed + openness×(q_open−q_closed)`다. open 목표는12관절 모두0이다. thumb1은 action7, 나머지11관절은 action6을 사용한다.

| 관절 | 닫힘 목표(rad) |
| --- | --- |
| thumb1 | 1.1641 |
| thumb2 | 0.5864 |
| thumb3 | 0.47052736 |
| thumb4 | 0.446389306432 |
| index1 / middle1 / ring1 / little1 | 각각1.4381 |
| index2 / middle2 / ring2 / little2 | 각각1.55933183 |

이 목표를 position actuator에 전달한다. 닫힘 목표는 action mapping의 끝점이며 URDF의 모든 위치 상한과 같은 개념은 아니다.

## 5. 리워드

### 5.1 지급 규칙과 전체 항목

활성 보상은13개다. RewardManager는 기본적으로 각 함수 반환값에 `weight×dt`를 곱한다. 여기서 `dt=0.02초`다. 아래 식은 혼동을 피하기 위해 **weight와 dt를 적용한 실제 한 제어step 보상**으로 쓴다. Reaching과 일회성 이벤트는 함수 내부에서 dt를 나누어 상쇄한다.

`d`는 현재 타겟 link 원점과 goal 사이 world XY 거리(m), `H`는 EEF world Z가 **초기 선반 작업면+0.14m보다 엄격히 낮음**을 뜻한다. 정확히14cm 높이에서는 H가 거짓이다. H의 기준은 움직이는 선반의 현재 높이나 타겟 윗면이 아니다.

| term | weight | 실제 지급 개요 |
| --- | --- | --- |
| target_reaching | +30 | EEF–타겟 최단 접근 기록 개선1m당+30 |
| target_goal_distance | +5 | `dt×5×exp(−d/0.05)×cosine`, H 필요 |
| target_goal_hold | +10 | `dt×10×Smoothstep 점유 점수`, H 및 유효 타겟 필요 |
| target_contact | +0.1 | `dt×0.1×인정 누적 count`, count 최대10 |
| robot_action_rate_penalty | −1 | raw Arm 및 clamp Hand action 변화 제곱 비용 |
| robot_joint_velocity_penalty | −1 | Arm6축·독립 Hand6축 관절속도 제곱 비용 |
| object_tilt_penalty | −30 | 활성 타겟·장애물의 기울기 비용 합 |
| obstacle_displacement_penalty | −150 | 활성 장애물 초기 대비3D 변위 제곱 합, cap0.04 |
| shelf_penalty | −1 | 선반 충돌 이벤트−3 + 연속 상태 비용 |
| obstacle_contact_penalty | −0.05 | 장애물–손 합력30N 초과 비용 |
| target_goal_first_entry_bonus | +10 | episode 최초 `d<=0.03` 진입 때+10 |
| target_goal_success_bonus | +75 | 안정 유지 성공 종료 때+75 |
| wrist_wrench_change_penalty | −0.1 | 힘/모멘트 크기 변화의 bounded 비용 |

보상 계산은 현재 GT를 사용한다. 초기 위치 관측에 노이즈가 있어도 보상의 goal 거리나 접촉 대상은 그 noisy 관측으로 계산하지 않는다.

### 5.2 Reaching: 새로운 최단 접근만 보상

현재3D EEF–타겟 거리에서0.10m를 빼고0으로 하한 처리한 값을 `D_t`라고 한다. reset 당시 값으로 최단 기록 `B`를 초기화한다.

```text
D_t = max(||eef_t - target_t||_3D - 0.10, 0)
B_new = min(B_old, D_t)
r_reaching = 30 * (B_old - B_new)
```

정지·후퇴·기존 최단 거리까지 재접근은 추가 보상을 주지 않는다. 10cm 안쪽에서는 이 항의 추가 개선량이 없다. 현재 타겟 위치를 사용하므로 타겟이 EEF 쪽으로 움직이는 경우도 개선으로 계산될 수 있다.

### 5.3 거리: 누적 변위 cosine

타겟 시작 XY를 `p0`, 현재 XY를 `p`, goal XY를 `g`라고 한다.

```math
c=\mathrm{clip}\left(
\frac{(\mathbf{g}-\mathbf{p}_0)\cdot(\mathbf{p}-\mathbf{p}_0)}
{\|\mathbf{g}-\mathbf{p}_0\|\,\|\mathbf{p}-\mathbf{p}_0\|},-1,1\right),
\qquad r_{distance}=0.02\times5\times e^{-d/0.05}\times c\times H.
```

두 벡터 중 길이가1e−8m 이하이면0이다. **현재 속도 방향이 아니라 시작점부터의 누적 이동 방향**을 사용한다. 같은 직선상에서 goal을 지나치거나 goal 쪽 위치에서 잠시 후퇴해도 누적 변위가 goal 방향이면 cosine은 양수일 수 있다. 반대 방향이면 음수다. 현재step 접촉 조건은 없으며, goal3cm 내부라고 cosine을1로 강제하지 않는다.

### 5.4 Hold: 2.5–3.5cm Smoothstep

```text
u = clamp((d - 0.025) / 0.010, 0, 1)
score = 1 - 3*u^2 + 2*u^3
r_hold = dt * 10 * score * H * valid_target
```

2.5cm 이하는 score1, 3cm는0.5, 3.5cm 이상은0이다. 최대step 보상은0.2다. 속도에 따른 감쇠는 없다. 다만 valid_target은 다음을 모두 검사한다.

- 타겟 활성 및 위치·속도·goal XY·바닥·기울기 관련 값이 finite.
- 현재 선반 local 원점 위치가 `|x|<=0.16m`, `|y|<=0.46m`.
- 실제 회전 bbox의 최저점이 선반 local Z의1.04–1.07m 안에 존재.
- 타겟 up 축과 선반 up 축의 내적이 `cos(0.9)` 이상.

Hold 외곽3.5cm와 성공 반경3cm는 서로 다른 기준이다.

### 5.5 Contact: 3step 중2step 인정

신선한 타겟–손 접촉 합력 크기가0.01N 이상이고 H가 참이면 그step의 실제 접촉을 인정한다. 별도로 `d<=0.03`이고 H가 참이면 목표 내부 점유로 접촉을 간주한다.

최근3step의 `(실제 접촉 OR 목표 내부 점유)` 기록 중2개 이상이면 현재step을 인정한다. 단, **현재 목표 내부 점유는 history와 무관하게 즉시 인정**하며 어느 경우에도 현재 H가 참이어야 한다.

인정step마다 누적 count를1 증가시켜 최대10으로 제한한다. 불인정step은 보상0이고 count는4회까지 유지하다가 **연속5회 불인정**이면0으로 초기화한다. 따라서 무조건 연속 접촉 횟수만 세는 구조는 아니다. 실제 지급은 `dt×0.1×count`로 최대0.02/step이다. reset에서 history·count·불인정 횟수를 초기화한다.

### 5.6 Action Rate와 관절속도

Arm은 OSC 배율 적용 전 raw action6축을 사용한다. Hand는 현재와 직전 raw action2축을 각각0–1로 clamp한 뒤 차이를 계산한다.

```text
C_action = 0.03*min(sum((a_arm[t]-a_arm[t-1])^2), 100)
         + 0.03*min(sum((clamp(a_hand[t])-clamp(a_hand[t-1]))^2), 100)
r_action_rate = -dt*C_action
```

2026-11-07부터 Arm·Hand 그룹별 합산 cap100을 적용한다. OSC 출력 토크 변화나 tanh(action) 변화로 계산하지 않는다. Hand의0–1 제한으로 Hand 제곱합은 실제 최대2이며, dt0.02초에서 전체 action-rate 페널티의 최대 절댓값은0.0612다. 이 cap은 Relative-v0에서 지정하여 v2/v3가 상속하며, 기존 Refactor-v3_1 등의 uncapped 기본 동작은 유지한다.

```text
C_velocity = 0.03*min(sum(qdot_arm^2), 100)
           + 0.01*min(sum(qdot_hand_independent^2), 100)
r_joint_velocity = -dt*C_velocity
```

Hand 대상은 thumb1·thumb2·index1·middle1·ring1·little1의 독립 구동6축이다. mimic follower6축은 이 비용 합산에서 제외한다.

### 5.7 물체 기울기·장애물 이동·장애물 접촉

기울기는 현재 선반 up 축 대비 활성 물체 up 축의 각도다. 타겟도 포함한다.

```text
r_tilt = -dt*30*sum(clamp((tilt_i - 5deg)/(0.9rad - 5deg), 0, 1)^2)
```

각 물체는5도 이내 비용0, 0.9rad 이상 비용1이다. 주차 물체는 제외한다.

```text
C_move = min(sum_active_obstacles(||position_i - initial_position_i||_3D^2), 0.04)
r_obstacle_displacement = -dt*150*C_move
```

타겟은 이동 비용에서 제외한다. cap0.04는 거리4cm가 아니라 **여러 장애물의 변위 제곱 합(m²)** 상한이다. 최대step 비용은−0.12다.

장애물–손 접촉에서는 타겟 접촉을 제외한 world force 벡터를 합한 뒤 크기 `F`를 구한다. 개별 힘 크기를 더하는 방식이 아니므로 반대 힘은 상쇄될 수 있다.

```text
C_contact = min(0.5*(exp(2*max(F-30, 0))-1), 100)
r_obstacle_contact = -dt*0.05*C_contact
```

실제 구현은 overflow 방지를 위해 지수 입력을 먼저 제한한다. 신선하지 않은 센서 데이터에는 비용0을 반환한다. 최대step 비용은−0.1이다.

### 5.8 Shelf penalty

다음 둘 중 하나면 충돌 이벤트 비용−3을 준다.

- 선반 root 선속도3축·각속도3축을 합친6D 벡터 norm이0.1 초과.
- wrist frame의 높이가 현재 선반 root Z+1.05m 기준3cm 미만.

종료에 쓰이는 선반 변위5cm 조건만 참인 경우에는 이−3 이벤트를 직접 추가하지 않는다. 별도로 연속 비용 `−dt×0.5×C_shelf`를 더한다.

`C_shelf`는 다음 합이다.

1. `선반 초기 대비3D 이동거리 + 선반 root 6D 속도 norm > 0.005`이면1.
2. EEF가 `(현재 선반 root 위치 + Z 1.06m)` 기준점에서3D 거리20cm 미만일 때, 가상 finger frame2개의 높이 비용 `clamp(1−height/0.02,0,1)` 합과 wrist frame 높이 비용 `clamp(1−height/0.08,0,1)`을 추가한다. 이 연속 비용의 height 기준은1.06m다.

이 항의 속도 norm·이동거리 혼합 기준, 1.05m와1.06m의 기준 차이는 실제 구현을 그대로 설명한 것이다. 촉각 contact force로 직접 선반 충돌을 판단하는 항은 아니다.

### 5.9 최초 진입과 안정 유지 성공 보너스

- **최초 진입+10**: 유한한 `d<=0.03`을 episode에서 처음 만족한step에 한 번 지급한다. EEF 높이·타겟 속도 조건은 없다. 이탈 후 재진입해도 재지급하지 않는다. 같은step에 다른 실패가 발생해도 최초 진입 latch 자체에는 실패 배제 조건이 없다.
- **성공+75**: 아래 termination의 안정 유지 성공이 참인step에 지급한다. 목표 안에서 저속 상태를 연속3초 유지해야 한다. 같은step의 실패 종료는 성공보다 우선하므로+75를 주지 않는다.

두 이벤트는 dt를 상쇄해 각각 정확히+10/+75다. timeout 자체에 추가 보너스는 없다.

### 5.10 손목 wrench 변화

관측 noise를 더하기 전 보정 F/T에서 힘·모멘트 **크기의 변화량**을 계산한다.

```text
dF = abs(norm(F_t)-norm(F_previous))
dM = abs(norm(M_t)-norm(M_previous))
s = clamp(max(max(dF-20,0)/30, max(dM-2,0)/3), 0, 1)
C_wrench = (exp(3*s)-1)/(exp(3)-1)
r_wrench_change = -dt*0.1*C_wrench
```

힘 변화20N·모멘트 변화2Nm까지 비용0, 각각50N·5Nm에서 포화한다. 크기가 같고 방향만 달라지는 경우는 비용이 없다. reset 후 첫 유효 샘플은 비교 history가 없어 비용0이다. 최대step 비용은−0.002이며, 누적 양의 보상에 연동하는 별도 budget 제한은 없다.

## 6. 터미네이션

아래 순서로5개 term을 평가한다. 실패3개가 성공보다 먼저 평가되므로 같은step 실패와 성공이 겹치면 성공 보너스를 억제한다.

| 순서·term | 조건 | 분류 |
| --- | --- | --- |
| 1. object_fall_or_tilt | 활성 물체 중 바닥 nonfinite, 바닥<작업면−0.01m, 기울기>=0.9rad 중 하나 | 실패 terminated |
| 2. shelf_failure | 선반6D 속도 norm>0.1, wrist 높이<작업면+0.03m, 선반 초기 대비3D 변위>0.05m 중 하나 | 실패 terminated |
| 3. arm_joint_velocity | Arm6관절 중 `abs(qdot)>현재 threshold` (4.0→2.0rad/s 커리큘럼) | 실패 terminated |
| 4. target_goal_success | `d<=0.03m` AND 타겟3D 속력<=0.005m/s를 연속3초 유지, 현재 실패 없음 | 성공 terminated |
| 5. timeout | episode 길이가500 제어step 도달 | 시간 제한 truncated |

### 6.1 물체·선반 실패의 세부 조건

물체 바닥은 원점 높이가 아니라, 현재 물체 자세와 실제 크기가 반영된 bbox8개 꼭짓점의 선반 좌표 최저점이다. 기본 작업면1.05m에서 바닥1.04m 미만이면 낙하 실패다. 정확히1.04m는 이 조건만으로 실패하지 않는다. 기울기는0.9rad와 같아도 실패한다. 타겟과 모든 활성 장애물을 검사하며 주차 물체는 검사하지 않는다.

선반 변위와 속도 조건은 엄격한 `>`이고 wrist clearance는 엄격한 `<`다. finger clearance를 직접 검사하는 종료 조건은 비활성(`check_fingers=False`)이다. Arm 속도는 현재 threshold와 정확히 같으면 실패하지 않는다. 물리 속도 한도는6관절 모두3.14rad/s 고정이며, 종료 threshold는4.0에서2.0rad/s까지 감소한다. 초기 threshold는 물리 한도보다 높고,14,500iteration부터3.1rad/s로 물리 한도보다 낮아진다.

### 6.2 성공 유지 시간

타겟의 현재 위치·속력·goal 거리가 유한해야 한다. 조건을 만족하는 제어step마다 카운터를1 올리고 한 번이라도 조건을 벗어나면 해당 환경 카운터를0으로 되돌린다. 기본 설정에서150step 연속 만족하면3초다. 여러 번의 짧은 체류 시간을 누적해 성공시키지 않는다.

성공 조건 자체에 EEF14cm 높이 gate는 없다. 따라서 Hold/Contact/Distance 보상 조건과 성공 종료 조건은 완전히 같지 않다. timeout 시점에 단순히 goal 안에 있다는 사실만으로 성공을 추가 선언하지 않는다. 종료 뒤 해당 환경은 reset되어 다음 episode의 배치와 goal을 받는다.

## 7. 커리큘럼

활성 curriculum term은 목표 방향의 금지 반각 `target_goal_direction_deadzone`과 관절 속도 종료 임계값 `arm_joint_velocity_threshold`의2개다. 물체 수·목표 거리·성공 반경·물리 속도 한도·보상 계수는 curriculum으로 변경하지 않는다. 목표 방향은 기존대로 선반 local +X와−X 주변을 제외하는 반각을30도에서0도로 줄인다.

| PPO learning iteration | 금지 반각 α |
| --- | --- |
| 0–9,999 | 30° |
| 10,000–12,999 | 25° |
| 13,000–15,999 | 20° |
| 16,000–18,999 | 15° |
| 19,000–21,999 | 10° |
| 22,000–24,999 | 5° |
| 25,000 이후 | 0° |

기본 허용 방위각은 `[α, π−α]`와`[π+α, 2π−α]` 두 구간이다. 처음에는±X 주변을 피하는 방향 위주로 학습하고, 이후 허용 방향을 넓힌다.0도에 도달하면 전 방향을 허용한다.

일정의 단위는 물리step·episode 수가 아니라 **PPO iteration**이다. runner가 iteration을 전달하면 다음 object_spawn의 `excluded_x_half_angle`을 갱신한다. 진행 중인 episode의 고정 goal을 바꾸지는 않으며 다음 reset부터 새 각도 범위를 사용한다. 기본 rollout은 환경당36 제어step/iteration이다. 환경만 직접 생성하면 learning_iteration 기본값은0이다.

### 7.1 관절 속도 종료 임계값

Relative-v0/v1/v2 공통으로10,000iteration까지4.0rad/s를 유지한다. 첫 감소는10,250이며 이후250iteration마다0.05rad/s 감소하고20,000부터2.0rad/s를 유지한다.

```math
n(i)=\max\left(0,\left\lfloor\frac{i-10000}{250}\right\rfloor\right),\qquad
v_{\mathrm{term}}(i)=\max(2.0,4.0-0.05n(i))
```

| PPO iteration | 종료 threshold(rad/s) |
| --- | --- |
| 0–10,249 | 4.0 |
| 10,250–10,499 | 3.95 |
| 14,250–14,499 | 3.15 |
| 14,500–14,749 | 3.1 |
| 19,750–19,999 | 2.05 |
| 20,000 이후 | 2.0 |

매번 절대 iteration에서 재계산하므로 reset·부분 reset·checkpoint resume·iteration 되감기 시 누적 감소가 없다. 기존 runner의 `set_learning_iteration` 경로로 TerminationManager 설정을 갱신하여 진행 중인 episode에도 적용된다. 별도 print 출력은 없다. Axia 질량은 v0부터0.280kg이며 v2·v3가 상속한다. 이전 Base 장애물 관측 실험인 v1은 삭제했다.

## 8. 실행·학습 설정·코드 위치

Isaac Lab 의존성이 설치된 Python에서 workspace 루트를 기준으로 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-v0 --num_envs 2048 --headless
```

기본 로그 디렉토리는 `logs/rsl_rl/inspire_wrench_refactor_relative_v0/`다. 다른 관측 차원의 checkpoint를 그대로 적용하면 입력 크기와 의미가 맞지 않는다.

PPO는 rollout36, 최대90,000 iteration, 저장 간격50, learning rate0.001/adaptive, gamma0.98, lambda0.95, epochs8, minibatches4, clip0.2, entropy0.005, value loss coefficient1, desired KL0.02, gradient norm cap1이다. Actor Gaussian 초기 표준편차는1이다.

아래 경로는 모두 `src/inspire_sweep_baseline/inspire_sweep_baseline/` 기준이다. 구현 추적을 위한 위치이며 이 문서 이해에 다른 설명서는 필요하지 않다.

| 역할 | 코드 |
| --- | --- |
| 최종 환경 설정 | `envs/wrench_refactor_envs.py::WrenchRefactorRelativeEnvCfg` |
| 실행·reset·step | `runtime/wrench_refactor.py::WrenchRefactorEnv` |
| Scene | `assets/scenes/wrench_refactor.py` |
| 생성·배치 | `mdp/event_functions/wrench_refactor.py`, `mdp/common/wrench_refactor_layout.py`, `mdp/common/bbox_scene_layout.py` |
| 관측 설정·변환 | `mdp/observations/wrench_refactor.py`, `mdp/observation_functions/wrench_refactor.py` |
| action | `mdp/actions/wrench_refactor.py`, `mdp/action_functions/wrench_refactor.py`, `mdp/action_functions/hand_openness.py` |
| reward | `mdp/rewards/wrench_refactor.py`, `mdp/reward_functions/wrench_refactor.py` 및 해당 callable의 구현 파일 |
| termination | `mdp/terminations/wrench_refactor.py`, `mdp/termination_functions/wrench.py`, `revision.py`, `final.py` |
| curriculum | `mdp/curricula/wrench_refactor.py`, `mdp/curriculum_functions/wrench.py` |
| PPO·encoder | `agent/wrench_refactor_ppo_cfg.py`, `agent/wrench_refactor_models.py` |

문서 작성 시 실행 코드는 변경하지 않았다. 기존 구현 검증에서 CPU65개, GPU64/2048환경 각각180step·부분 reset·초기 바닥 정렬·고정 물성 검사가 통과했고,64환경에서 `train.py`2 iteration과 양쪽 encoder 갱신을 확인했다. 이는 장기 수렴·최종 성공률·실물 성능의 검증은 아니다. 문서 작성 자체에서는 시뮬레이션이나 학습을 추가 실행하지 않았다.

## 9. Relative 계열 비교와 F/T 검증

| 환경 | Actor 타겟 | Critic 타겟 | 접촉·거리 보상 |
| --- | --- | --- | --- |
| v0 | 초기 위치 | 초기 위치 | 별도 접촉 유지 + cosine 거리 weight5 |
| v2 | 초기 위치 | 현재 위치 | v0와 동일 |
| v3 | 초기 위치 | 초기 위치 | 접촉 유지 삭제 + 현재 step 접촉 조건부 cosine 거리 weight25 |

세 환경 모두 현재 EEF 기준으로 타겟·목표·장애물을 표현하며, EEF pose만 base 기준이다. v2·v3는 각각 v0의 직접 자식이다. Axia 280g은 공통이고, 손 질량790g은 유지한다. F/T 측정 joint는 Axia와 손 사이에 있으므로 하우징은 측정 경계 위쪽이며 보정 대상은 하위 손이다. 기존 보정기는 실제 PhysX 질량·관성으로 하위 손의 중력·관성 wrench를 제거한다. 하우징 질량을 손 보정 합계에 추가하지 않는다. GPU 정적·동적·기지 외력 검증 결과는 [최종 개발 로그](../logs/2026-11-06_relative_family_280g_v3.md)에 기록한다.
