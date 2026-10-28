# Final GoalAccuracy v0 환경 상세 명세

[환경 문서 목록](README.md) · [등록·실행 안내](../08_ACTIVE_ENVIRONMENTS.md) · [개발·검증 기록](../logs/2026-10-27_final_goal_accuracy.md)

기준일: 2026-10-27. 이 문서는 `Isaac-Inspire-Final-GoalAccuracy-v0`의 실제 적용 설정과 계산 함수를 기준으로 관측, Scene, Action, Reward, Curriculum, Termination, 학습 Metric을 설명한다. 모든 수치는 실행 시 설정 변경이 없는 기본값이다. Gym ID는 2026-10-28에 기존 오타 `GoalAccuacy`에서 `GoalAccuracy`로 교정했다. 이름 외 v0 동작은 보존한다. `FinalV1EnvCfg`를 직접 상속하지만, 현재 환경의 동작을 이 문서만으로 파악할 수 있도록 상속된 설정도 함께 적었다.

과업은 선반 위의 타겟을 지정한 평면 목표 위치로 **1cm 이내**까지 밀고, 장애물과 선반을 안정적으로 유지하는 것이다. 정책은 에피소드 시작 시의 타겟·장애물 위치와 목표를 받고, 실행 중에는 관절 상태, EEF 자세, 촉각, 손목 wrench로 행동한다. 목표에 도달해도 계속 행동하며, 10초 만료 시의 위치로 성공 여부를 분류한다. 목표 인정 반경은 학습 처음부터 0.01m로 고정한다.

| 항목 | 설정 |
| --- | --- |
| Gym ID / 설정 클래스 | `Isaac-Inspire-Final-GoalAccuracy-v0` / `FinalGoalAccuracyEnvCfg` |
| 직접 부모 / 실행 클래스 | `FinalV1EnvCfg` / `FinalGoalAccuracyEnv` (`FinalV1Env` 상속) |
| PPO 설정 / experiment | `FinalGoalAccuracyPPORunnerCfg` / `inspire_final_goal_accuracy_v0` |
| 기본 병렬 환경 수 / 간격 | 4096개 / 2.5m |
| 물리 시간 간격 | 0.01초, 100Hz |
| 정책·제어 시간 간격 | 0.02초, 50Hz; 한 Action당 물리 2스텝 |
| 최대 에피소드 길이 | 10초, 제어 500스텝 |
| 물체 용량 | 타겟 1개 + Gray 10개 + White 10개 |
| 정책 출력 | Arm 6D + Hand 2D = 8D |

위치의 단위는 m, 각도는 rad, 힘은 N, 모멘트는 N·m이다. **Robot root 좌표**, **선반 좌표**, **world 좌표**를 구분한다. 물체 위치는 별도 언급이 없으면 바닥을 기준으로 배치한 rigid-body/link 원점 위치이며, 질량중심 위치와 같다고 가정하지 않는다.

## 1. 관측 정보

### 1.1. 입력 그룹과 차원

| 그룹 | 차원 | 제공 대상 | 내용 |
| --- | --- | --- | --- |
| `policy` | 57 | Actor·Critic | 관절, 직전 Action, 초기 타겟, EEF, 목표, 촉각, wrench, 실제 Hand 구성 |
| `obstacles` | 80 | Actor·Critic | 초기 장애물 20슬롯 × `[present, x, y, z]` |
| `privileged` | 3 | Critic | 현재 타겟 위치의 정확한 시뮬레이터 값 |

Actor의 원시 입력은 137D, Critic은 140D다. 장애물 그룹은 각 모델의 `80 → 32 → 16` ReLU encoder를 통과한다. 따라서 최종 MLP에 들어가는 차원은 Actor 73D, Critic 76D다. 영상이나 관측 history stack은 입력하지 않는다. 타겟·장애물의 종류, 크기, 질량, 마찰 계수를 명시적인 상태 채널로 제공하지 않는다.

### 1.2. `policy`의 순서·의미·노이즈

아래 인덱스는 0부터 시작하고 양 끝을 포함한다. “추가 노이즈 없음”은 관측 함수에 인공 노이즈를 더하지 않는다는 뜻이며, 접촉 solver나 물리 계산의 오차까지 없다는 의미는 아니다.

| 인덱스 | 이름 | 차원 | 값의 의미·좌표 | 갱신·추가 노이즈 |
| --- | --- | --- | --- | --- |
| 0–5 | `joint_pos` | 6 | 실제 Arm 관절 위치 − 초기 관절 위치, rad | 매 스텝; 없음 |
| 6–11 | `joint_vel` | 6 | 실제 Arm 관절 속도 − 기본 속도 0, rad/s | 매 스텝; 없음 |
| 12–19 | `actions` | 8 | 직전 raw Action의 Arm·Hand 전체 8D에 `tanh`를 적용한 명령 피드백 | 매 스텝; 없음 |
| 20–22 | `target_obs_state` | 3 | 에피소드 시작 시 타겟 원점의 Robot root 기준 XYZ | reset 때 고정; 각 축에 독립 `U(-0.01,0.01)`m bias |
| 23–29 | `ee_pose` | 7 | 현재 EEF의 Robot root 기준 XYZ와 quaternion `(w,x,y,z)` | 매 스텝; quaternion 부호 정규화; 없음 |
| 30–31 | `goal_pos` | 2 | 초기 타겟에서 목표까지의 평면 거리와 방향각 | reset 때 고정; 없음 |
| 32–48 | `tactile` | 17 | 각 촉각 영역의 접촉 여부 0/1 | 각 관측 계산마다 셀별 독립 확률 0.01로 0/1 반전 |
| 49–54 | `wrist_wrench` | 6 | EEF 원점·EEF 축 기준 외력·외모멘트 `[Fx,Fy,Fz,Mx,My,Mz]` | 각 관측 계산마다 독립 가우시안; 힘 σ=0.05N, 모멘트 σ=0.005N·m |
| 55–56 | `hand_configuration` | 2 | 실제 Hand 관절 위치로 추정한 굴곡·엄지 opposition 열림 정도 | 매 스텝; `[0,1]`; 없음 |

타겟 관측 bias는 reset마다 다시 뽑아 에피소드 동안 유지한다. 매 스텝 새 위치 노이즈를 뽑지 않으며, 이동 중 타겟의 실제 위치로 갱신하지도 않는다. 노이즈 설정의 `operation="abs"`는 노이즈 샘플로 bias를 설정한다는 의미로, 음수 bias를 절댓값으로 바꾸는 처리가 아니다.

목표 관측의 거리·각도는 Robot root 축으로 변환한 **초기 타겟→목표 변위**에서 계산한다. 각도는 `atan2(-dy, dx)`를 `[0,2π)`로 옮긴 시계방향 각도다. 현재 타겟→목표 오차가 아니므로, 정책은 목표 오차를 직접 계속 관측하지 않는다.

`actions`는 직전에 출력한 명령의 피드백이다. Arm·Hand 전체 8개 raw 성분에 `tanh`를 적용하여 큰 값이 관측으로 되돌아오는 크기를 제한한다. 예를 들어 raw `0.5`, `1`, `2`는 약 `0.462`, `0.762`, `0.964`로 관측된다. Hand raw 출력이 음수이면 피드백도 음수이며, 실제 Hand 제어에 사용하는 `[0,1]` 열림 값과는 구분한다. 이 관측용 변환은 실행한 raw Action이나 보상 계산용 Action을 수정하지 않는다. reset 직후 저장된 raw Action은 Arm 0, Hand `[1,1]`이므로 관측 피드백은 Arm 0, Hand 약 `[0.762,0.762]`다. 관측 차원과 순서는 그대로지만 입력값의 의미가 바뀌므로 변경 전 checkpoint 재생은 그 의미 차이를 고려해야 한다.

### 1.3. 촉각과 손목 wrench

17개 촉각 채널의 순서는 손바닥 1개, 엄지 4개, 검지·중지·약지·소지 각각 3개다. 각 영역의 접촉력 크기 기준은 0.01N이다. 직접 pad 접촉에 더해, Hand의 부모 링크에서 검출한 타겟·장애물 접촉점을 해당 pad의 기하 영역에 투영한다. 어떤 pad 영역에도 속하지 않는 접촉점은 촉각 채널을 켜지 않는다. 직접 pad 접촉과 물체 접촉 투영은 서로 다른 경로이므로, 손 전체의 접촉 여부와 17개 bit의 합을 동일한 값으로 해석하지 않는다.

손목 wrench는 Axia80 아래 Hand 계통의 반력을 이용하고, Hand 모델과 운동학으로 중력·관성 성분을 보상한다. 외력은 EEF 원점으로 옮긴 뒤 EEF 축으로 표현한다. 보상에 타겟의 정답 위치나 접촉 상대의 정체를 사용하지 않는다. reset 시 측정값을 영점으로 저장하는 tare도 적용하지 않는다. reset 직후 아직 유효한 물리 센서 샘플이 없으면 원본 촉각과 wrench를 0으로 마스킹한다.

관측을 만들 때 이 원본 센서값의 복사본에 다음 노이즈를 적용한다. 촉각은 환경·셀별로 독립적인 Bernoulli(0.01)를 추출하여 해당 셀의 0/1을 반전한다. F/T는 각 축에 평균 0인 독립 가우시안 노이즈를 더하며, 힘 XYZ의 표준편차는 각각 0.05N, 모멘트 XYZ는 각각 0.005N·m다. 두 노이즈 모두 관측 계산마다 다시 추출하며 에피소드 고정 bias가 아니다.

이 노이즈는 Actor와 Critic이 공유하는 `policy` 그룹에만 적용한다. 물리 센서·공유 센서 cache와 접촉·wrench 보상 계산에는 노이즈를 넣지 않는다. reset의 원본 0에도 관측 단계의 노이즈가 적용되므로, reset 직후 최종 관측은 모두 0이라고 보장하지 않는다. `policy.enable_corruption=False`로 설정하면 인공 관측 노이즈가 비활성화되며, 기본값은 True다.

### 1.4. 실제 Hand Configuration 2D

첫 채널은 엄지 opposition을 제외한 11개 관절의 굴곡 열림 정도, 두 번째는 엄지 opposition 관절의 열림 정도다. 0은 닫힘 기준, 1은 열림 기준이다. 이 값은 Action target이 아니라 **현재 관절 위치**에서 계산하므로, 접촉이나 제어 지연으로 명령을 따라가지 못하면 Hand Action과 달라질 수 있다.

관절의 닫힘 기준을 `c`, 열림 기준을 `o`, 실제 위치를 `q`, `s=o-c`라 할 때 다음을 사용한다. 관절 0은 opposition이다.

```math
u_f=\mathrm{clip}\left(\frac{\sum_{i=1}^{11}(q_i-c_i)s_i}{\sum_{i=1}^{11}s_i^2},0,1\right),\qquad
u_o=\mathrm{clip}\left(\frac{q_0-c_0}{s_0},0,1\right).
```

첫 채널은 11개 관절을 하나의 open/closed target 선분에 최소제곱 투영한 값이다. 각 관절을 단순 평균한 값이 아니다. 개별 손가락의 모든 자세를 복원할 수 있는 관측도 아니다.

### 1.5. 초기 장애물 관측과 가림

각 슬롯은 `[present,x_root,y_root,z_root]`다. 위치는 reset 당시의 장애물 원점이며, 각 XYZ에 독립 `U(-0.01,0.01)`m 노이즈를 한 번 더한다. 이후 에피소드 동안 그대로 유지한다.

실제 크기가 반영된 물체별 외접반경으로 초기 가림을 계산한다. 가시성 판정 threshold는 0.35이며, 활성 장애물의 visible 여부를 독립적으로 1% 확률로 뒤집는다. 따라서 가려진 장애물이 보고되거나 보이는 장애물이 누락될 수 있다. 비활성 물체가 관측에 생기는 것은 아니다.

보고할 장애물은 **노이즈가 포함된 root Y 위치를 기준으로 왼쪽→오른쪽** 정렬한다. 이후 인접한 점유 슬롯 `(0,1)`, `(1,2)`, …를 순차적으로 훑으며 각각 10% 확률로 교환한다. 뒤쪽 교환은 앞선 교환 결과를 사용한다. 빈 슬롯은 `[0,0,0,0]`으로 끝부분을 채운다. 따라서 관측 슬롯 순서와 물리 collection의 Gray/White 슬롯 순서는 일치하지 않으며, `present`는 관측에 보고된 물체라는 뜻이다.

Critic의 `privileged` 3D는 현재 타겟의 Robot root 기준 XYZ를 매 스텝 제공하며 인공 노이즈가 없다. Actor에는 이 그룹을 전달하지 않는다.

## 2. 환경 정보

### 2.1. Scene과 좌표계

Scene은 ground plane, dome light, 선반, UR5e–Axia80–Inspire Hand, 물체 collection, 프레임·접촉 센서로 구성한다. 환경별 형상·크기를 다르게 만들기 위해 `replicate_physics=False`로 구성한다.

| 구성 | 기본값·역할 |
| --- | --- |
| 선반 | 환경 원점 기준 `(-0.7,0,0)`, 질량 100kg인 rigid object |
| 사용 선반 면 | 선반 좌표 X 폭 0.40m, Y 폭 1.00m; 바닥 지지면 Z=1.05m |
| Robot root | 환경 원점 기준 `(0,0,0.79505)`; quaternion `(0,0,0,1)`, 즉 Z축 180° 회전 |
| 초기 Arm 관절 | shoulder pan/lift, elbow, wrist 1/2/3 순서로 `(0,-2.2,2.2,0,1.57,0.785)`rad |
| 초기 Hand | 12개 관절 모두 open 위치 0rad; 초기 관절 속도 0 |
| 광원 | RGB `(0.75,0.75,0.75)`, intensity 2500 |
| EEF | `axia80_link`의 local Z `0.1427`m 지점; offset quaternion `(0.5,-0.5,-0.5,-0.5)` |
| 가상 손가락 프레임 | `inspire_base_link` 기준 `(±0.07,0,0.13)`m 두 점; 선반 근접 보상용 |
| 가상 손목 프레임 | `inspire_base_link` 기준 `(0,0,-0.17)`m; 선반 근접·종료 검사에 사용 |

실제 물체는 항상 collection index 0의 타겟과, 뒤따르는 Gray 10·White 10 용량으로 구성한다. 타겟 prim 이름 `mass_cylinder`는 식별용 이름이며 실제 형상을 뜻하지 않는다. 비활성 슬롯은 선반 local Z=100m에 주차하고 중력을 끈다. 활성 마스크를 통해 장애물 관측·관련 물체 보상·낙하 검사에서 제외한다.

접촉 센서는 Hand 17개 pad, 부모 링크의 물체 접촉점, 전체 Hand 합력, 물체별 Hand 접촉력을 읽는다. 접촉 센서의 `update_period=0`, `history_length=0`으로 현재 물리 샘플을 사용한다. 목표 command `target_goal_pos`는 reset 당시 타겟 위치와 샘플링한 이동 벡터로 만들어 에피소드 동안 고정한다.

### 2.2. 타겟·장애물 형상과 크기

타겟은 **실린더 / 큐브 / 랜덤 물체 그룹을 각각 1/3 확률**로 선택한다. 장애물은 랜덤 물체 그룹에서 선택한다. 랜덤 그룹은 다음 14개 variant를 균등 선택한다.

| 형상 | 기본 치수 또는 variant 구성 |
| --- | --- |
| 실린더 타겟 | 반경 0.04m, 높이 0.10m; 바닥 쪽 질량중심 설정 |
| 큐브 타겟 | 한 변 0.08m |
| Cracker box | NVIDIA YCB `003_cracker_box`, 크기 variant 3개 |
| Sugar box | NVIDIA YCB `004_sugar_box`, 크기 variant 3개 |
| Tomato soup can | NVIDIA YCB `005_tomato_soup_can`, 크기 variant 3개 |
| Master chef can | NVIDIA YCB `002_master_chef_can`, 크기 variant 3개 |
| 머그컵 | 높이 0.10m, 바깥 반경 0.035m, 안쪽 반경 0.029m의 빈 몸체와 손잡이; 전체 기본 XY bounds 약 `[-0.047,0.054] × [-0.035,0.035]`m |
| 뚜껑 있는 병 | 몸통 반경 0.03m; 몸통·어깨·목·뚜껑의 총 높이 0.135m |

스캔 물체 4종에는 크기 계수 `f=0.8,0.9,1.0`을 적용한다. 원본 upright 치수를 `dx,dy,dz`라 할 때 기본 균일 배율은 다음과 같다. 이에 따라 추가 ±10% 적용 전 외접반경은 최대 `0.06f`m, 높이는 최대 `0.18f`m다.

```math
k=1.5f\min\left(\frac{0.04}{\sqrt{d_x^2+d_y^2}/2},\frac{0.12}{d_z}\right).
```

스캔 물체는 외관 mesh와 평평한 바닥의 상자·캔 충돌 형상을 사용한다. 머그컵은 바닥·16개 벽 조각·손잡이 3조각의 convex collider 20개로 빈 내부와 손잡이를 표현한다. 병은 몸통·어깨·목·뚜껑의 4개 convex collider로 구성한다.

`object_size_randomization`은 각 환경의 타겟·장애물별로 `U(0.9,1.1)`의 등방 배율을 샘플링한다. **형상과 크기는 환경 생성 시 한 번 선택하며 reset마다 바꾸지 않는다.** 시각 형상과 충돌 형상에 같은 배율을 적용하고 실제 bounds를 저장한다. reset 시 원점 Z를 `1.05 - scaled_min_z`로 두어 확대된 물체도 밑면이 선반 면과 맞게 배치한다. 명시된 관성에는 크기 배율의 제곱을 반영한다.

### 2.3. 타겟 위치·목표·장애물 배치

타겟의 초기 XY는 선반 중심의 **반경 0.02m 원판 내부에서 면적 균일**하게 추출한다. 타겟 yaw는 0이다. 목표 방향은 선반 평면에서 추출하되, 초기에는 ±X축 양쪽으로 각각 반각 30°인 방향 구간을 제외한다. 이 제외 각도는 커리큘럼에 따라 줄어든다.

목표는 해당 방향으로 최대 0.15m 떨어진 점이다. 무작위로 5~15cm 거리를 뽑는 방식은 아니며, 최대 15cm로 진행하되 선반의 안전영역에 닿는 방향은 거리를 줄인다. 실제 타겟 footprint, 선반 가장자리 여유 0.02m, 접근 경로 생성기의 내부 경계, 목표 보상의 유효 XY 범위를 함께 반영한다. 가능한 길이가 0.05m보다 짧으면 방향을 다시 추출하고, 유한 횟수 뒤에는 안쪽 Y방향을 사용한다. 목표만 사후 clamp하여 잘못된 방향을 만드는 방식은 사용하지 않는다.

장애물은 타겟·목표·손 접근 경로를 기준으로 Red/Gray/White 영역을 나눠 배치한다. Gray가 있으면 첫 Gray는 타겟 뒤쪽 영역에, 추가 Gray는 Gray 영역에 둔다. White는 Red/Gray 영역 밖에 둔다. Gray 안쪽 경계의 완화량은 커리큘럼이 정한다. 장애물 yaw는 `U(-π,π)`다. 최종 배치는 실제 크기를 반영한 회전 bounding box 사이 최소 2mm 간격, 선반 내부 지지, 손 접근 경로와의 여유를 검사한다.

배치 요청 수는 처음 Gray 1·White 1이며 커리큘럼으로 최대 8·8까지 증가한다. 저장 용량의 상한 10·10과 요청 수, 실제 활성 수는 서로 다르다. 요청 수로 배치하지 못하면 다음 순서로 감소시킨다.

```text
(Gray, White) = (8,8) → (8,7) → (7,7) → (7,6) → (6,6) → … → (0,0)
```

각 수량 단계마다 최대 8회 배치 생성기를 호출하고, 각 호출의 scene attempt는 4회다. 성공하면 즉시 사용한다. 타겟과 목표는 이 과정에서 바꾸지 않는다. 마지막 0·0 단계는 안전한 타겟 단독 배치로 반환한다. 일부 환경만 reset할 때 다른 환경의 배치를 변경하지 않는다. 기하적 혼잡 때문에 요청 수를 줄이는 처리이며, 잘못된 자산이나 잘못된 설정을 모두 무시하는 예외 처리는 아니다.

실제 활성 수는 `Metrics/obstacle_actual_gray`, `Metrics/obstacle_actual_white`에서 확인한다. `Curriculum/obstacle_actual_*` 키는 이 환경에서 기록하지 않는다. 기하 검사를 통과했다는 사실만으로 로봇 전체의 IK 도달성이나 접촉을 포함한 과업 성공을 보장하지는 않는다.

### 2.4. 질량·마찰 및 Event 시점

reset마다 환경별로 질량을 한 번 뽑아 **그 환경의 타겟과 모든 장애물에 동일하게** 적용한다.

```math
m=1.5\,\mathrm{clip}\bigl(0.365+0.0675\epsilon,\ 0.230,\ 0.500\bigr)\ \mathrm{kg},\qquad
\epsilon\sim\mathcal{N}(0,1).
```

최종 범위는 0.345~0.750kg다. clip 전 평균은 0.5475kg, 표준편차는 0.10125kg다. 관성은 각 형상의 기본 관성/질량 비율로 갱신한다. 크기로부터 밀도를 고정해 질량을 결정하는 설정은 아니다.

마찰은 다음 정규분포의 분위수로 만든 역할별 4096개 bucket에서 reset마다 선택한다. 음수는 0으로 제한하며 static/dynamic bucket 순열은 분리한다. 선반·물체·Hand는 각각 추출하고, 같은 환경의 물체들은 같은 물체 마찰값을 공유한다.

| 역할 | 정지 마찰 평균 / 표준편차 | 동적 마찰 평균 / 표준편차 |
| --- | --- | --- |
| 선반 | 0.315 / 0.051 | 0.252 / 0.041 |
| 타겟·장애물 | 0.315 / 0.040 | 0.252 / 0.032 |
| Hand 링크·pad | 0.585 / 0.145 | 0.468 / 0.116 |

| Event 이름 | 시점 | 실행 내용 |
| --- | --- | --- |
| `object_size_randomization` | prestartup | 실제 물체 크기 ±10%, bounds·관성 준비 |
| `object_materials` | startup | 마찰 bucket과 PhysX 질량·관성·재질 buffer 준비 |
| `reset_all` | reset | 로봇·선반·물체 기본 상태 복원 |
| `object_spawn` | reset | 타겟·목표·장애물 배치, 활성 마스크, 초기 관측 snapshot |
| `object_physics_randomization` | reset | 질량·형상별 관성·마찰 재추출 |

### 2.5. 재생 시 타겟 표시

`play.py` 실행 시 타겟에 노란 3D wire bounding box를 표시한다. 타겟의 자세와 실제 크기를 따라가며 padding은 3mm, 선 폭은 2mm다. 12개 edge를 표시하는 순수 시각화로 충돌·질량을 추가하지 않는다. 학습 기본값 `target_bounding_box=False`에서는 박스 prim을 생성하지 않는다.

## 3. Action 정보

### 3.1. 8D 출력의 구성

| 인덱스 | 채널 | 변환과 의미 |
| --- | --- | --- |
| 0–2 | Arm XYZ | 출력 × 0.03m의 상대 위치 명령 |
| 3–5 | Arm roll/pitch/yaw | 출력 × 0.15rad의 상대 회전 명령 |
| 6 | Hand flexion | `[0,1]`로 제한한 전체 굴곡 열림 정도 |
| 7 | Hand opposition | `[0,1]`로 제한한 엄지 opposition 열림 정도 |

### 3.2. Arm Operational Space Control

Arm의 상대 명령은 **Robot root 축**으로 해석한다. 현재 EEF pose에서 목표 pose를 만들고, 회전 명령은 scaled Euler XYZ를 quaternion·axis-angle로 변환하여 적용한다. 위치 0.03m와 회전 0.15rad는 출력에 곱하는 scale이지, 최종 명령의 hard limit이 아니다. Arm Action 함수에서 raw 입력을 `[-1,1]`로 clamp하지 않는다.

OSC는 위치·회전 6축을 모두 제어한다. 고정 impedance, 병진 stiffness `(100,100,100)`, 회전 stiffness `(50,50,50)`, 각 축 damping ratio 1.0을 사용한다. 완전 관성 decoupling과 중력 보상을 켜며, 별도 contact-wrench 제어축과 nullspace 제어는 사용하지 않는다. Arm 관절의 내부 position PD stiffness/damping은 0으로 두고 OSC가 계산한 관절 effort를 적용한다.

관절 effort 상한은 앞 세 관절 150N·m, 손목 세 관절 28N·m다. 계산된 effort를 이 한계로 제한하고, 비유한 effort가 있는 환경 행은 0 effort로 처리한다. 시뮬레이터 관절 속도 한계는 `(2,2,2,4,4,4)`rad/s다. 이는 6절의 별도 종료 검사 threshold와 다른 설정이다.

### 3.3. Hand 위치 제어

Hand는 12개 관절을 2개 채널로 묶어 절대 위치 target을 만든다. opposition 관절에는 채널 7을, 나머지 11개 굴곡 관절에는 채널 6을 적용한다.

```math
q_i^{\mathrm{target}}=c_i+u_i(o_i-c_i),\qquad 0\le u_i\le1.
```

모든 open target은 0rad다. closed target은 다음과 같다.

| 관절 | closed target, rad |
| --- | --- |
| thumb 1, opposition | 1.1641 |
| thumb 2 / 3 / 4 | 0.5864 / 0.47052736 / 0.446389306432 |
| index·middle·ring·little의 첫 관절 | 각각 1.4381 |
| index·middle·ring·little의 둘째 관절 | 각각 1.55933183 |

Hand implicit actuator는 stiffness 1.2, damping 0.06, effort limit 0.20N·m, velocity limit 1.0rad/s, armature 0.0001을 사용한다. 명령은 50Hz로 갱신하고 물리는 100Hz로 적분한다. Action에 추가 확률적 제어 노이즈를 넣지 않는다. 관측의 `hand_configuration`은 이 target이 아니라 실제 움직인 관절 위치를 역투영한 값이다.

## 4. Reward 정보

### 4.1. 합산 규칙과 전체 항

RewardManager는 각 함수값에 설정 weight와 제어 간격 `Δt=0.02`초를 한 번 곱해 합산한다. 아래에서 `ρ`는 **weight까지 적용한 보상률**, `R`은 실제 한 스텝 기여량이다. 진행 보상과 선반 종료 보상은 함수 내부에서 `Δt`를 나누어 스텝별 거리 증가량·일회성 비용을 보존한다.

```math
R_t=\Delta t\sum_k\rho_{k,t},\qquad \rho_{k,t}=w_k f_k(t),\qquad \Delta t=0.02.
```

| 이름 | Manager weight | 의미 |
| --- | --- | --- |
| `hand_reaching` | +30 | 손–타겟 접근 거리의 새 기록 |
| `goal_distance` | +100 | 타겟–목표 평면 접근 거리의 새 기록 |
| `goal_hold` | +8 | `d ≤ 0.01m`에서 목표 중심·저속 유지 보상 |
| `hand_contact` | +1.45 | 손 접촉 또는 유효한 목표 반경 내부 점유 |
| `action_rate_penalty` | −1 | 내부 Arm/Hand 계수 각각 0.03 |
| `joint_velocity_penalty` | −1 | 내부 Arm 0.03, Hand 0.01 |
| `object_penalty` | −1 | 기울기·장애물 변위·물체 가속도의 합성 비용 |
| `target_speed_penalty` | −5 | 타겟 선속도의 커리큘럼 무료 기준 초과 비용 |
| `shelf_penalty` | −1 | 선반 충돌 조건의 일회성 비용과 근접·움직임 비용 |
| `obstacle_contact_penalty` | 0 → −0.1 | 장애물–Hand 접촉력 초과 비용 |
| `wrench_change_penalty` | 0 → −0.1 | 보상된 wrench 크기 변화 비용 |

수식에서 `clip(x,0,1)`은 0~1 제한, `A`는 타겟을 포함한 활성 물체 집합, `O`는 활성 장애물 집합이다. 속도·가속도·힘 비용에 사용하는 공통 함수는 다음과 같다. threshold `b` 이하에서는 0이고, threshold로 나누어 정규화하지 않는다.

```math
E(x;b)=\min\left(\frac{\exp(2\max(x-b,0))-1}{2},\ 100\right).
```

실제 구현은 지수를 계산하기 전에 상한을 적용해 overflow를 막는다.

### 4.2. 목표 점유의 공통 유효성

`d`는 현재 타겟과 목표의 **world XY 거리**, `v`는 타겟의 3D 선속도 크기다. `r=0.01`m은 고정된 `goal_hold.position_tolerance`, `s=0.05`m/s는 고정된 `goal_hold.speed_scale`이다. 두 값에 대한 커리큘럼은 없다.

아래 조건을 모두 만족할 때 보상에서 사용하는 타겟 유효성 `V`가 참이다.

- 타겟 위치·속도, 목표 XY, 위쪽 축의 정렬값이 유한하다.
- 선반 좌표에서 타겟 원점의 `|x|≤0.16`, `|y|≤0.46`, `1.04≤z≤1.07`이다.
- 타겟 up축과 선반 up축의 내적이 `cos(0.9)` 이상이다.

`hand_contact`의 목표 간주, `goal_hold`, `hand_reaching`의 인정 반경 전환은 모두 `V`와 **`d≤r`**을 사용한다. 이 유효성 검사에 실제 선반 접촉력 검사는 포함하지 않는다. 시간 만료 성공 조건은 6절에서 별도로 정의한다.

### 4.3. `hand_reaching`과 `goal_distance`

`hand_reaching`은 현재 EEF와 타겟의 3D 거리에서 near radius를 뺀 양의 gap을 추적한다. Final-v1과 같이 평소 near radius는 **0.10m**, 유효한 타겟의 `d≤r` 점유 중에는 **1.0m**다. `r`만 커리큘럼 없이 0.01m로 고정한다. EEF–타겟 거리가 1m 이내라면 목표 점유 중 gap은 0이므로 더 가까워져도 접근 보상이 늘지 않는다. reset 때의 gap을 초기 최저 기록으로 두고, 그보다 더 가까워진 양에 대해서만 **1m당 +30**을 지급한다.

```math
g_t=\max(\|p_{\mathrm{eef},t}-p_{T,t}\|-n_t,0),\qquad
b_t=\min(b_{t-1},g_t),\qquad
R_{\mathrm{reach},t}=30(b_{t-1}-b_t).
```

뒤로 갔다가 같은 지점으로 돌아오는 행동은 다시 보상하지 않는다. 목표 첫 진입에서 인정 반경이 커지면 남은 접근 진전을 한 번 지급할 수 있지만, 최저 gap 기록을 유지하므로 목표 안팎을 반복해서 오가도 재지급하지 않는다. 타겟이 손 쪽으로 움직이는 경우도 상대 거리를 줄인다.

`goal_distance`는 reset 시 타겟–목표 거리 `D0` 대비 접근한 거리의 최고 기록을 추적한다. tolerance는 0m이며 `r` 커리큘럼과 독립적이다.

```math
P_t=\max(D_0-d_t,0),\qquad B_t=\max(B_{t-1},P_t),\qquad
R_{\mathrm{distance},t}=100(B_t-B_{t-1}),\qquad B_0=0.
```

목표까지 0.15m인 에피소드에서 목표 중심까지 진전하면 이 항의 누적 보상은 최대 15다. 후퇴에 별도 음의 진행 보상을 주지는 않지만, 이전 기록까지 재접근해도 추가 지급하지 않는다.

### 4.4. `goal_hold`과 `hand_contact`

`goal_hold`의 weighted rate는 다음과 같다.

```math
\rho_{\mathrm{hold}}=
8\,\mathbf{1}_{\{V\ \mathrm{and}\ d\le r\}}
2^{-((d/r)^2+(v/s)^2)}
\left(1+\max(1-d/r,0)^2\right).
```

중심에 정지해 있으면 초당 +16, 즉 한 스텝 +0.32다. 정지 상태에서 **정확히 `d=r`이면 초당 +4**이고, `d>r`에서는 0이다. `r<d<2r`에도 지급하지 않는다. 중심에 가까울수록, 선속도가 작을수록 높다. 누적 지급 시간 제한이나 연속 유지시간 ramp가 없어 에피소드가 끝날 때까지 받을 수 있다. weight 4→8은 지급 범위가 `2r`에서 `r`로 줄어든 데 대한 초기 계수 조정이며 학습 성능 향상이 입증된 값은 아니다.

`hand_contact`는 Final-v1과 같은 함수·계수를 사용한다. 전체 Hand의 현재 유효한 합력 크기가 0.01N 이상이거나, 타겟이 `V`를 만족하며 **`d≤r`**이면 초당 +1.45, 즉 한 스텝 +0.029다. 두 조건을 동시에 만족해도 한 번만 지급한다. 목표 간주에는 별도의 저속 조건이 없고, 이 간주가 실제 촉각 bit를 켜지는 않는다. 실제 접촉력 조건은 목표 거리와 무관하다.

전체 Hand 합력은 링크·pad의 **normal contact force 벡터를 먼저 합한 뒤** 크기를 취한다. 접선 마찰력은 이 센서 합력에 포함하지 않으며, 선반·바닥과의 Hand 접촉도 포함한다. 물체별 힘 크기를 각각 더한 값과 다르므로 반대 방향 힘이 상쇄될 수 있다.

### 4.5. Action·관절 속도 페널티

`a`는 실행 경로에 전달된 raw Action, `q̇`는 실제 관절 속도다. 아래는 각각 weighted rate이며 실제 스텝에는 다시 0.02를 곱한다.

```math
\rho_{\mathrm{action}}=-0.03\min\left(\sum_{i=0}^{5}(a_{t,i}-a_{t-1,i})^2,100\right)
-0.03\min\left(\sum_{i=6}^{7}(a_{t,i}-a_{t-1,i})^2,100\right).
```

```math
\rho_{\mathrm{velocity}}=-0.03\min\left(\sum_{i\in\mathrm{Arm}}\dot q_i^2,100\right)
-0.01\min\left(\sum_{i\in\mathrm{Hand}}\dot q_i^2,100\right).
```

Arm·Hand별 상한을 먼저 적용한 뒤 합산한다. Action 변화량을 시간으로 나누지 않고, 관절 수로 평균하지도 않는다. Hand 제어의 `[0,1]` clamp나 관측의 8D `tanh`를 raw Action 페널티에 적용하지 않는다. 각 항의 최대 비용은 한 스텝 각각 0.12, 0.08이다.

### 4.6. `object_penalty`와 `target_speed_penalty`

물체 기울기 `θ`는 선반 up축에 대한 각도다. 5°까지 허용하고 0.9rad에서 물체별 기울기 비용이 1이 된다. 장애물 변위는 노이즈 없는 reset 위치로부터의 **world 3D 변위 제곱합**이다.

```math
T=\sum_{j\in A}\mathrm{clip}\left(\frac{\theta_j-5\pi/180}{0.9-5\pi/180},0,1\right)^2,\qquad
D=\min\left(\sum_{j\in O}\|p_j-p_{j,0}\|^2,0.04\right),
```

```math
\rho_{\mathrm{object}}=-30(T+5D)+w_a\sum_{j\in A}E(\|\alpha_j\|;a_{\mathrm{free}}).
```

타겟은 기울기와 가속도 비용에는 포함하지만 변위 비용에서는 제외한다. `α`는 PhysX가 제공하는 물체 COM의 현재 3D 선가속도이며, 제어 스텝 사이 속도 차분으로 대체하지 않는다. 가속도는 물체마다 100 상한을 적용한 뒤 더한다. reset·가속도 비용 최초 활성화 후 유효한 첫 이력이 준비되기 전에는 가속도 비용을 지급하지 않는다. `w_a`는 0에서 −0.05, `a_free`는 50에서 20m/s²로 바뀐다.

`target_speed_penalty`의 weighted rate는 `−5 E(v;v_free)`이다. 대상은 타겟 하나의 3D 선속도 크기이고 각속도가 아니다. `v_free`는 Final-v1과 같은 커리큘럼으로 0.1→0.02m/s로 감소한다. 함수·weight·파라미터·일정은 Final-v1과 같고, Manager term 이름만 `object_speed_penalty`에서 바꿨다. 이 보상 threshold와 1.0m/s인 속도 종료 threshold는 별개다.

### 4.7. `shelf_penalty`

스텝 비용은 **선반 충돌 종료 구성요소가 참이면 일회성 −3**, 여기에 매 스텝 `−0.5 × Δt × C_shelf`를 더한다. 일회성 구성요소는 선반 root의 6D 속도 norm이 0.1을 넘거나 가상 손목이 선반 면 위 0.03m보다 낮은 경우다. 선반 위치 변위만으로 종료되면 일회성 −3은 발생하지 않는다.

지속 비용 `C_shelf`는 다음과 같다.

- `moved`: 선반 초기 위치 대비 거리와 root 6D 속도 norm의 합이 0.005를 넘으면 1.
- `near`: EEF와 `shelf root + (0,0,1.06)` 사이 3D 거리가 0.2m 미만이면 1.
- `finger`: 두 가상 손가락의 해당 기준면 대비 높이 `h`에 대해 `clip(1-h/0.02,0,1)`을 합산.
- `wrist`: 가상 손목의 해당 기준면 대비 높이 `h_w`에 대해 `clip(1-h_w/0.08,0,1)`.
- 최종 `C_shelf = moved + near × (finger + wrist)`.

이 항은 물리 접촉센서의 충돌 impulse를 직접 읽는 항이 아니다. 지속 비용의 기준 높이는 1.06m, 일회성 충돌 조건의 선반 면은 1.05m다. 또한 6D 속도 norm에는 선속도와 각속도가 함께 들어가므로 threshold를 순수 선속도 단위로 해석하면 안 된다.

### 4.8. `obstacle_contact_penalty`

활성 장애물과 Hand 사이 normal contact force의 벡터 합 크기를 `F_obs`라 하면 weighted rate는 `w_o E(F_obs;F_free)`다. 타겟 접촉과 비활성 물체는 제외한다. `w_o`는 0에서 −0.1, `F_free`는 80에서 30N으로 바뀐다. 유효한 최신 센서 데이터가 없으면 비용은 0이다. 여러 장애물에서 발생한 힘은 벡터 합이므로 상쇄될 수 있다.

### 4.9. `wrench_change_penalty`

보상된 손목 힘·모멘트의 **크기 차이의 절댓값**을 사용한다. 벡터 차이의 norm이나 시간으로 나눈 미분값이 아니다.

```math
\delta_F=\bigl|\|F_t\|-\|F_{t-1}\|\bigr|,\qquad
\delta_M=\bigl|\|M_t\|-\|M_{t-1}\|\bigr|,
```

```math
z=\max\left(\mathrm{clip}\left(\frac{\delta_F-F_f}{1.5F_f},0,1\right),
\mathrm{clip}\left(\frac{\delta_M-M_f}{1.5M_f},0,1\right)\right),\qquad
C_w=\frac{\exp(3z)-1}{\exp(3)-1}.
```

무료 변화량 `F_f`, `M_f` 이하에서는 0이고, 각각 무료 변화량의 2.5배에서 포화한다. 힘·모멘트 severity 중 큰 값을 사용한다. raw 비용은 `[0,1]`, weighted rate는 `w_w C_w`이며 weight는 0에서 −0.1로 변한다.

추가로 에피소드에서 이미 얻은 양의 보상 누적액의 **5%**를 이 항의 누적 비용 한도로 적용한다. 현재 스텝의 양의 보상도 예산에 반영하며, 남은 예산이 부족하면 비용을 더 줄인다. reset이나 weight 0→활성 전환 시 이력을 무효화하고, 유효한 연속 샘플이 없는 첫 계산에는 변화 비용을 주지 않는다.

## 5. Curriculum 정보

### 5.1. 기준 시계와 고정값

활성 일정은 절대 `learning_iteration`을 읽는다. 에피소드 번호나 제어 스텝 수가 아니다. 기본 PPO rollout은 환경당 iteration마다 36 제어 스텝이다. checkpoint 재개·iteration 변경 시 해당 절대 iteration에 맞는 값을 다시 적용한다. Reward threshold의 두 점 사이에서는 지정한 interval 간격으로 보간값을 갱신하며, interval 1은 매 iteration 갱신이다. 첫 점 이전과 마지막 점 이후에는 끝값을 유지한다.

다음 두 항은 **커리큘럼 term 자체가 비활성**이다. 보상 설정의 초기값이 전체 학습 동안 유지된다.

| 제거한 일정 | 고정 대상·값 | 기존 v1과의 차이 |
| --- | --- | --- |
| `goal_speed_scale` | `goal_hold.speed_scale=0.05m/s` | 후반 0.02m/s로 좁히지 않음 |
| `goal_position_tolerance` | `goal_hold.position_tolerance=0.01m` | 초반 0.02m를 사용하지 않음 |

이 고정 `r`은 goal hold, Reaching 인정 반경 전환, 목표 내 접촉 간주와 만료 성공의 공통 기준이다. `goal_distance` 자체의 tolerance는 0m로 유지한다. `object_free_speed` 일정은 Final-v1과 같은 점·간격을 사용하며 갱신 대상 term만 `target_speed_penalty`로 바꿨다.

### 5.2. 활성 11개 일정

| 이름 | 대상·단위 | 일정 | interval |
| --- | --- | --- | --- |
| `obstacle_population` | 요청 Gray/White 수 | 초기 1/1; White 2000, Gray 2500부터 번갈아 증가; 최종 8/8 | 전체 500마다 1개, 각 색 1000마다 |
| `object_free_speed` | `target_speed_penalty.free_speed`, m/s | `(0:0.1), (499:0.1), (500:0.09), (1900:0.02)` | 250 |
| `obstacle_gray_zone_padding` | Gray 내측 완화 비율 | `(4000:0) → (10000:0.15)` | 1000 |
| `object_free_acceleration` | 무료 가속도, m/s² | `(3000:50) → (10000:20)` | 1 |
| `object_acceleration_weight` | `object_penalty` 내부 가속도 weight | `(3000:0) → (10000:−0.05)` | 1 |
| `goal_deadzone` | ±X축 목표 방향 제외 반각 | 3000까지 30°; 3500부터 5°씩 감소; 6000부터 0° | 500 |
| `wrench_free_force_change` | 무료 힘 크기 변화, N | `(3000:50) → (10000:20)` | 250 |
| `wrench_free_moment_change` | 무료 모멘트 크기 변화, N·m | `(3000:5) → (10000:2)` | 250 |
| `wrench_weight` | wrench Manager weight | `(0:0), (1000:0), (3000:−0.03), (6000:−0.1)` | 250 |
| `obstacle_free_force` | 무료 장애물 접촉력, N | `(0:80), (3000:80), (6000:50), (10000:50), (12000:30)` | 250 |
| `obstacle_weight` | 장애물 접촉 Manager weight | `(0:0), (1000:0), (3000:−0.02), (6000:−0.05), (10000:−0.05), (12000:−0.1)` | 250 |

요청 개수의 경계는 다음과 같다. 2000에 첫 증가가 시작되지만 실제 물리 배치가 어려우면 해당 reset에서 White, Gray 순으로 한 개씩 줄여 배치한다. `Metrics/obstacle_actual_*`은 **요청 수가 아니라 실제 배치 수**다.

| learning iteration | 요청 Gray | 요청 White |
| --- | --- | --- |
| 0–1999 | 1 | 1 |
| 2000–2499 | 1 | 2 |
| 2500–2999 | 2 | 2 |
| 3000–3499 | 2 | 3 |
| 3500–3999 | 3 | 3 |
| 4000–4499 | 3 | 4 |
| 7500–7999 | 7 | 7 |
| 8000–8499 | 7 | 8 |
| 8500 이후 | 8 | 8 |

Gray padding은 미터가 아니라 형상에 맞춘 Red 반경의 비율이다. 4000에서는 0, 5000에서는 0.025, 10000에서는 0.15다. 물체 간 비겹침·손 접근 clearance 검사는 그대로 적용한다. 개수·Gray 영역·방향 변경은 이후 reset의 새 장면에 반영되며 진행 중인 에피소드의 활성 마스크를 바꾸지 않는다.

### 5.3. 보상·종료와의 연결

`r=0.01m`는 학습 iteration에 따라 바뀌지 않는다. `goal_hold`의 거리 감쇠 scale·지급 cutoff, `hand_reaching`의 인정 반경 전환, `hand_contact`의 목표 간주, `success`·`time_out`의 만료 분류는 이 반경을 공유하되, 보상은 타겟 유효성 `V`를 추가로 검사하고 만료 분류는 XY 거리만 검사한다. 모든 목표 점유 판정의 경계는 `d≤r`다. `hand_reaching`의 EEF–타겟 3D 인정 반경은 별도로 평소 0.10m, 유효한 목표 점유 중 1.0m다.

`object_acceleration_weight`는 RewardManager의 −1 weight가 아니라 `object_penalty` 내부 가속도 계수를 갱신한다. 다른 고정 weight는 위 표의 일정으로 바뀌지 않는다.

## 6. Termination 정보

### 6.1. 실패 종료

다음 네 조건은 매 제어 스텝 검사하며 하나라도 참이면 조기 종료할 수 있다. 서로 배타적이지 않으므로 같은 스텝에 여러 항이 참일 수 있다.

| 이름 | 정확한 조건·대상 |
| --- | --- |
| `object_drop` | 활성 타겟 또는 장애물 중 하나라도 환경 원점 대비 물체 원점 높이가 **1.04m 미만**, 또는 선반 대비 기울기가 **0.9rad 이상** |
| `object_speed` | 타겟의 3D 선속도 norm이 **1.0m/s 초과** |
| `shelf_termination` | 선반 root 6D 속도 norm **0.1 초과**, 또는 가상 손목의 `shelf root Z + 1.05` 대비 높이 **0.03m 미만**, 또는 선반 초기 root 위치 대비 3D 변위 **0.05m 초과** |
| `joint_velocity` | Arm 6개 관절 중 하나라도 실제 관절 속도 절댓값 **5.0rad/s 초과** |

`object_drop`의 기울기 0.9rad는 약 51.57°다. 비활성 주차 물체는 검사하지 않는다. `joint_velocity`는 이름과 관계없이 대상 selector가 **Arm 관절**이며 Hand 속도를 이 항에서 검사하지 않는다. `shelf_termination`은 가상 손가락 높이를 사용하지 않고, 선반 접촉 impulse도 직접 읽지 않는다. 선반 6D 속도 norm은 선속도와 각속도를 함께 계산한다. 선반 XY 경계 이탈 자체를 검사하는 별도 종료 항은 없다.

### 6.2. 10초 만료의 성공·시간 초과 분류

`expired`는 `episode_length_buf ≥ 500`, `d`는 타겟–목표 world XY 거리, `r=0.01m`은 고정 목표 반경이다.

```math
\mathrm{success}=\mathrm{expired}\ \land\ (d\le r),\qquad
\mathrm{time\_out}=\mathrm{expired}\ \land\ \neg(d\le r).
```

두 항은 상호 배타적이며, 합치면 정확히 10초 시간 한계다. 10초 전에 목표 반경에 들어와도 이 이유로 종료하지 않는다. **정확히 경계 `d=r`인 경우는 `success`**다. 비교할 거리가 NaN이면 `d≤r`가 거짓이므로 `time_out`으로 분류한다.

성공 분류는 **시간 만료와 거리만** 검사한다. 속도 조건, 연속 유지시간, 추가 접촉 조건, 4.2절의 보상 유효성 `V`를 추가하지 않는다. 따라서 `goal_hold`의 지급 여부와 `success` 여부가 완전히 같은 판정은 아니다.

`success`와 `time_out`은 둘 다 `time_out=True`로 등록하여 시간 한계에 의한 **truncation**으로 처리하고 value bootstrapping을 유지한다. 실패 종료 항은 **termination**이다. 만료 스텝에 실패 조건까지 충족하면 실패 항과 `success` 또는 `time_out`이 함께 참일 수 있다. 그러므로 `success` 로그를 “어떤 실패도 없었던 성공” 지표로 해석해서는 안 된다. 성공 종료에 별도의 추가 일회성 성공 보상은 없다.

## 7. 학습 Metric 정보

`FinalGoalAccuracyEnv`는 각 제어 스텝의 물리 업데이트 뒤, 자동 reset 전에 Metric을 수집한다. 구현상 `success` 종료 term이 매 제어 스텝 평가될 때 수집 함수를 호출하므로, 성공 여부와 관계없이 실패·시간 만료 에피소드의 마지막 상태도 포함한다. 이 값은 별도의 정책 관측 채널이나 보상 항이 아니다.

| TensorBoard `Metrics/` 키 | 원본 계산 | 에피소드 집계·단위 |
| --- | --- | --- |
| `target_goal_distance_xy_mean` | 현재 타겟 원점과 command 목표의 world XY 거리 | 유한한 제어 스텝의 평균, m |
| `eef_linear_speed_mean` | `axia80_link` 원점의 world 선속도에 각속도 × EEF offset을 더한 EEF 지점의 3D 속력 | 유한한 제어 스텝의 평균, m/s |
| `target_linear_speed_mean` | 현재 타겟의 world 3D 선속도 norm | 유한한 제어 스텝의 평균, m/s |
| `target_linear_acceleration_mean` | PhysX가 제공하는 현재 타겟 COM의 world 3D 선가속도 norm | 유한한 제어 스텝의 평균, m/s² |
| `max_force` | 보정된 손목 F/T 관측의 EEF 축 힘 XYZ norm | 에피소드 내 최대, N |
| `max_moment` | 같은 관측의 EEF 축 모멘트 XYZ norm | 에피소드 내 최대, N·m |
| `obstacle_actual_gray`, `obstacle_actual_white` | fallback 뒤 실제 배치된 Gray·White 개수 | reset 대상 환경의 평균, 개 |

`*_mean`은 각 환경의 에피소드 안에서 유한 샘플의 시간 평균을 먼저 구하고, 같은 reset 호출에서 종료된 환경끼리 평균한 스칼라다. `max_force`·`max_moment`도 각 환경별 최대를 구한 뒤 reset 대상끼리 평균한다. 유한 샘플이 하나도 없는 항은 그 reset에서 키를 생략한다. F/T는 `policy.wrist_wrench`와 같은 보정 관측 함수를 직접 읽지만, ObservationManager가 Actor·Critic 입력에 추가하는 가우시안 노이즈를 넣기 **전** 값이다. 물리 센서의 원시 전체 하중이나 선반 접촉력으로 해석하지 않는다.

`obstacle_actual_*`은 부모 runtime이 기록하던 `Curriculum/obstacle_actual_*`에서 `Metrics/`로 옮긴 키다. reset 이후 새로 배치된 환경의 실제 개수를 나타내므로, 직전 에피소드의 시간 평균과 시점이 다르다. 요청 개수와 실제 개수의 차이는 과밀 배치 fallback의 빈도를 해석하는 데 사용한다. TensorBoard 스칼라는 에피소드 종료가 발생해 `extras['log']`가 채워질 때 기록되므로 학습 iteration마다 반드시 새 값이 생긴다는 보장은 없다.

## 8. 실행과 검증 범위

Workspace 루트에서 새 task ID로 학습한다. `train.py`가 사용하는 기본 PPO는 `num_steps_per_env=36`, `max_iterations=90000`, `save_interval=50`이며 Actor·Critic 모델과 나머지 PPO 하이퍼파라미터는 v1과 같다. 새 experiment 폴더는 `logs/rsl_rl/inspire_final_goal_accuracy_v0`다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Final-GoalAccuracy-v0 --num_envs 256 --headless
```

`play.py`에서는 같은 task ID와 이 환경의 checkpoint를 지정한다. v1 checkpoint는 관측·모델 차원이 같지만 보상 목적과 커리큘럼이 다르므로 이어 학습한 결과와 신규 학습 결과를 구분해야 한다. 학습 로그 정리는 이 문서의 실행 절차에 포함되지 않는다.

## 코드 근거와 검증 범위

이 명세의 기준은 아래 실제 설정과 계산 함수다. 파일 링크는 문서 저장소와 코드 workspace를 함께 checkout한 경로를 기준으로 한다.

- [환경 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/final_envs.py), [runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/final.py)
- [관측 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/final.py), [Hand 관측 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/final.py)
- [Scene](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/final.py), [물체 생성](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/final_spawners.py), [배치 기하](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/final_geometry.py), [Event 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/final.py)
- [Action 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/actions/final.py), [로봇·관절 기준](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/robot.py)
- [Reward 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/final.py), [목표 보상·합성 비용](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/final.py), [공유 목표 측정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/contact_sweep_clutter_fusion_holding.py)
- [Curriculum 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/final.py), [Termination 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations/final.py), [만료 분류 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/final.py)

초기 환경 CPU 계약 검사는 43개, 이번 경계·상속 변경을 포함한 관련 CPU 검사는 56개가 통과했다. GPU 물리 reset/step, 실제 TensorBoard 이벤트 생성, 1cm 성공률, play 화면 외관, 학습 수렴은 아직 검증하지 못했다. 이 문서는 구현된 동작의 명세이며 과업 성능의 실험 결과를 주장하지 않는다. 실행한 검사와 미실행 범위는 [개발·검증 기록](../logs/2026-10-27_final_goal_accuracy.md)에 구분해 두었다.
