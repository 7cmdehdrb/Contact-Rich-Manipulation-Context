# Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention — 원문 상세 정리

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention** |
| 저자 | Nils Dengler, Juan Del Aguila Ferrandis, João Moura, Sethu Vijayakumar, Maren Bennewitz. 첫 두 저자는 공동 기여로 표시되어 있다. |
| 출판 | 2025 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), Hangzhou, China, October 19–25, 2025, pp. 7600–7606 |
| DOI | [10.1109/IROS60139.2025.11246809](https://doi.org/10.1109/IROS60139.2025.11246809) |
| 문헌 관리 식별자 | [IROS 제목 선별 보고서](../reviews/2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md)의 **IROS-S03**. 사용자 임시 선정 목록의 세 번째 논문이며 R1–R7과 별개다. |
| 정리일 | 2026-09-16 |
| 확인한 원문 | 제공된 출판본 PDF 7쪽 전체. 본문 §I–V, 식 (1), Fig. 1–7, Table I–II, References [1]–[34] |
| 확인하지 않은 자료 | 저자 코드·설정·체크포인트·원시 실험 로그, 보충 영상, 인용된 선행논문의 개별 원문, 제조사 데이터시트 |
| 원문 PDF SHA-256 | `bfb651b2b02d330d2ea70e8021143dee6ab4a5036d520a952db3dca8a9e29584` |

[개별 논문 색인](README.md) · [문헌조사 자료](../README.md)

이 문서는 논문 자체의 문제, 관련 연구, 환경·센서, 관측과 행동의 연결, 학습법, 결과, 저자 명시 한계와 향후 연구를 정리한다. 다른 연구 주제에 대한 적용안은 포함하지 않는다. `[원문 §…, PDF p.…]`는 제공된 출판본의 위치이며 **PDF 1–7쪽은 인쇄 페이지 7600–7606**에 대응한다. `[12]` 같은 번호는 원문의 참고문헌 번호다. 그림·표·수식은 PDF 렌더링과 대조했다. 원문 설정을 대수적으로 해설한 부분은 실제 코드 확인 결과와 구분한다.

**핵심:** 이 연구는 F/T 또는 tactile feedback으로 미는 정책이 아니다. **현재 물체 pose·목표 pose·pusher 위치와 장애물 occupancy grid를 관측하고, location-based attention으로 장면의 공간 정보를 추출한 뒤 LSTM과 categorical PPO로 pusher의 평면 속도를 결정하는 연구**다. 목표는 물체와 pusher가 장애물에 충돌하지 않으면서 물체의 위치와 방향을 모두 맞추는 것이다. `Guidance-free`는 사전 global path·그 경로상의 subgoal을 사용하지 않는다는 뜻이며, 실시간 외부 지각이나 목표 정보를 사용하지 않는다는 뜻이 아니다. [원문 §I–III, §IV-E, PDF pp. 1–3, 6]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 정의·기여와 Related Work |
| 3–4 | 로봇·센서 상세 사양, 힘·접촉 정보의 실제 사용 범위 |
| 5 | Occupancy grid, patch별 위치 문맥, location-based attention |
| 6–8 | 관측·행동·LSTM, reward·종료, PPO·randomization·sim-to-real |
| 9–11 | 비교군 설계, 시뮬레이션 전체 결과, 실물 정량·정성 실험 |
| 12–14 | 저자 명시 한계, Future Work 확인 결과, 미명시·표기 주의사항 |
| 15 | 원문 위치 안내와 문서 검증 범위 |

## 1. 제시하는 문제 상황과 연구의 범위

### 1.1 왜 이 pushing 문제를 다루는가

저자들은 pick-and-place만으로 다루기 어려운 물체를 재배치하거나, 파지할 수 있는 위치·방향으로 바꾸기 위해 non-prehensile manipulation이 필요하다고 설명한다. Pushing은 로봇이 물체 pose를 직접 명령하는 완전 구동 문제가 아니다. 접촉 위치와 접촉 모드에 따라 물체의 이동·회전이 달라지므로 장기적인 결과와 접촉 전환을 함께 고려해야 한다. [원문 Abstract, §I, PDF p. 1]

Clutter가 추가되면 원하는 물체를 이동시키는 것만으로는 충분하지 않다. **밀고 있는 물체뿐 아니라 pusher도 다른 물체와 충돌하지 않아야 한다.** 따라서 현재 물체를 어느 방향으로 미는지, 어떤 면으로 접촉을 바꾸는지, 장애물 주변의 어느 공간을 이용하는지를 함께 결정해야 한다. Fig. 1의 cake 전달 장면은 이러한 사용 상황을 보여 주는 예시다. [원문 §I, §III-B.3, Fig. 1, PDF pp. 1, 3]

### 1.2 기존의 global path guidance에 대한 문제의식

원문이 대비하는 구조는 미리 global path를 계산하고, 그 경로상의 subgoal을 RL 정책에 제공하는 방식이다. 저자들은 이러한 guidance가 학습 문제를 쉽게 해 주지만 탐색을 사전 경로에 제한한다고 본다. 예컨대 좁고 막힌 짧은 경로보다 조금 더 길지만 덜 혼잡한 경로가 실제 pushing에는 유리할 수 있다. [원문 §I, PDF p. 1]

이 연구는 occupancy grid와 현재/목표 상태를 직접 받는 정책이 그러한 행동을 학습하게 한다. **Attention이 명시적인 global path를 출력한 뒤 다른 제어기가 그 경로를 추종하는 구조는 아니다.** 공간 feature가 정책 입력이 되고, 정책은 즉시 실행할 pusher 속도를 출력한다. [원문 §III, Fig. 2, PDF pp. 2–3]

### 1.3 과업 정의와 포함하지 않는 것

| 항목 | 원문의 정의와 범위 |
| --- | --- |
| 조작 공간 | 경계가 있는 평면 workspace |
| 조작 대상 | Pusher로 미는 하나의 물체 |
| 목표 | 대상 물체의 평면 pose $(x,y,\theta)$ |
| 주변 물체 | 의도적으로 치워야 하는 대상이 아니라 회피해야 하는 장애물 |
| 성공에 필요한 접촉 | Pusher–조작 대상 접촉 |
| 억제하는 접촉 | Pusher 또는 조작 대상과 장애물 사이의 접촉 |
| 행동 | Pusher의 평면 병진 속도 $(v_x,v_y)$ |
| 명시적인 사전 guidance | Global path, 그 경로에 따른 subgoal을 사용하지 않음 |
| 실행 중 지각 | 현재 물체 pose와 장애물 지도가 필요함. 실물에서는 MoCap 또는 3-camera 지각 경로 사용 |
| 다루지 않는 과업 | 파지 후 운반, 여러 장애물을 함께 밀어 치우기, 힘 추종, 촉각만으로 물체 상태 추정 |

[원문 §II–III, §IV-E, PDF pp. 2–3, 6]

물체의 **목표 방향을 조건으로 준다는 것**과 로봇이 **물체 각속도를 직접 명령한다는 것**은 다르다. 정책은 pusher의 이동만 결정하고, 물체의 회전은 접촉 상호작용을 통해 발생한다. 또한 `model-free RL`이라고 해도 지각 처리·시뮬레이터·실물의 로봇 기구학 변환까지 없는 것은 아니다. [원문 §III-B, §IV-A·E, PDF pp. 3–4, 6]

### 1.4 저자들이 제시하는 기여

저자들의 기여는 **global guidance 없는 장애물 회피 pushing**, **occupancy grid를 처리하는 경량 location-based attention**, **미지 장애물·동적 장애물·실물 이전과 feature extractor ablation**의 세 축이다. Categorical exploration과 LSTM의 기반은 선행연구 [12]에서 가져온다. 따라서 PPO, LSTM 또는 categorical distribution 자체를 새로 제안한 논문으로 설명하지 않는다. [원문 §I, §III-B, PDF pp. 1–4]

## 2. Related Work — 원문이 구성한 비교 구도

이 절은 **이 논문의 §II가 인용 연구를 어떻게 설명하는지**를 정리한 것이다. 인용 논문들을 이번 작업에서 별도로 정독·검증한 것은 아니다.

### 2.1 Model-based pushing과 MPC

저자들은 [4], [14], [15]를 offline nominal trajectory를 생성한 뒤 MPC로 추종하는 계열로 소개한다. 정밀하고 매끄러운 pushing이라는 장점과 함께, 짧은 horizon 때문에 큰 물체 외란이나 장애물 배치 변화가 생기면 nominal trajectory를 다시 계산해야 한다는 문제를 제시한다. 이에 대비하여 여러 장면에서 학습한 RL 정책으로 변화된 관측에 반응한다. **이는 저자들이 선택한 비교 구도이며 모든 MPC 방법의 일반적 불가능성을 증명한 결과는 아니다.** [원문 §II, PDF p. 2]

### 2.2 Clutter-free pushing과 push–grasp synergy

[5], [12], [16]은 clutter-free pushing 정책 계열로 분류한다. [7], [17], [18]의 push–grasp 계열은 clutter를 움직여 대상에 접근한 뒤 grasp로 회수하는 것이 목적이므로, 다른 물체와의 접촉을 금지하는 이번 과업과 요구 조건이 다르다고 설명한다. [원문 §II, PDF p. 2]

### 2.3 장애물 회피 pushing의 직접 비교 대상

| 원문 인용 | 저자들이 설명한 방식 | 이 논문이 제기하는 제약 |
| --- | --- | --- |
| Pasricha et al. [10] | RRT를 이용한 obstacle-avoiding poking | 비연속적 운동과 최종 pose 제어의 어려움, non-prehensile 문제에서의 확장성 |
| Krivic et al. [19] | 사전 corridor 안에서 로봇·물체를 움직임 | 좁은 장면에서 local minimum과 oscillation 발생 가능 |
| Dengler et al. [9] | Global path의 subgoal로 학습형 pushing을 안내 | 사전 guidance 의존, 목표 위치만 고려하고 방향은 제외 |
| Del Aguila Ferrandis et al. [12] | Categorical exploration을 이용한 model-free planar pushing | 본 연구가 계승하는 free-space 기반. 여기서는 장애물 지도와 attention을 추가 |

[원문 §I–II, PDF pp. 1–2]

직접 재구현한 외부 baseline은 [9]다. 반면 최종 orientation-aware 성능표의 주 비교군은 **본 연구의 구성에서 attention을 CNN으로 바꾼 ablation**이다. 두 종류를 같은 baseline으로 혼동하지 않는다. [원문 §IV-B–D, PDF pp. 4–6]

### 2.4 Location-based attention을 선택한 이유

원문은 attention 전반 [20]–[22], navigation 응용 [23], [24], location-based attention [13], [25], 그리고 관련 navigation 연구 [26]을 소개한다. 핵심 차이는 **모든 입력 token 쌍 사이의 관계를 계산하지 않고 위치에 근거해 feature의 중요도를 매기는 것**이다. 이는 큰 occupancy grid와 다수의 병렬 RL 환경을 함께 처리할 때 계산·메모리 부담을 줄이기 위한 선택이다. [원문 §II, PDF p. 2]

[26]도 location-based attention을 사용하지만 global path에서 뽑은 subgoal에 의존한다고 설명한다. 이 연구는 patch 처리에서 Vision Transformer [27]의 아이디어를 참고하되, 일반적인 multi-head self-attention을 그대로 채택하지 않는다. [원문 §II–III-A, PDF pp. 2–3]

## 3. 환경과 로봇·센서 상세 사양

### 3.1 시뮬레이션과 실제 로봇은 같은 모델로 학습하지 않는다

시뮬레이션 학습에서는 계산량을 줄이기 위해 로봇을 **spherical pusher**로 추상화한다. 실제 KUKA arm 전체를 학습 환경에서 그대로 움직였다고 서술하지 않는다. 실물에서는 task-space 속도 행동을 **OpTaS [34]를 통해 로봇 관절 configuration으로 변환**한다. 구체적인 inverse-kinematics 목적함수, low-level 제어기, interpolation 및 gain은 본문에 없다. [원문 §IV-A·E, PDF pp. 4, 6]

| 구성 | 원문에 명시된 내용 | 수치·세부 확인 한계 |
| --- | --- | --- |
| 실물 arm | KUKA iiwa | 정확한 세부 모델, 자유도 숫자, 가반하중, reach, 반복정밀도, 관절 속도 한계 미명시 |
| 실물 task-space→joint 변환 | OpTaS 사용 | Solver·비용·제약·servo 주기·명령 interface 미명시 |
| 시뮬레이션 robot 표현 | Spherical pusher | 기준 반지름·질량·관성·재질 및 접촉 높이 미명시 |
| 시뮬레이션 환경 | Isaac Sim 기반 custom clutter-pushing environment | 구체적인 버전·physics time step·solver 설정 미명시. 인용 [30]의 서지 제목은 Orbit |
| 주 학습 장면 | 단일 rectangular obstacle | 절대 크기와 위치·각도 sampling 범위 미명시 |
| 추가 학습 장면 | 두 장애물 환경 | 구체적인 sampling 제약·간격 범위 미명시 |
| GPU | NVIDIA A6000, 48 GB VRAM을 MHA 실험에서 명시 | 본문 전체 학습의 총 GPU 수·CPU·RAM·wall-clock time 미명시 |
| 정책 동작 주파수 | 10 Hz | 센서 frame rate나 arm 내부 servo 주파수와 다름 |

[원문 §IV-A·C·E, PDF pp. 4–6]

사진에 있는 물체를 보고 상세 제품명·질량·치수를 임의로 채우지 않는다. Table I의 object mass와 scale은 **훈련 randomization 범위**이며, 실물 물체의 측정 사양이 아니다.

### 3.2 실물 지각: MoCap과 3Cam

| 경로 | 사용 장비·처리 | 정책에 전달되는 정보 | 원문 명시 수준 |
| --- | --- | --- | --- |
| MoCap | Vicon motion capture로 object·obstacle pose 추적 | 물체 pose, 장애물 pose에서 생성한 occupancy grid | 정적 장면의 정량 평가에 사용. 저자는 높은 추적 정밀도·noise 강인성을 장점으로 설명하지만 수치는 없음 |
| 3Cam | Intel RealSense D435 3대, AprilTags 기반 object tracking, 여러 point cloud의 fusion | 물체 pose, point cloud에서 구성한 occupancy grid | 일상 물체가 있는 장면에서 정성 시연. Raw RGB-D를 actor에 직접 입력하는 구조는 아님 |
| Pusher 위치 | 정책 관측의 $(x,y)$ | 별도의 비영상 수치 feature 경로 | 실물에서 이 위치를 취득하는 정확한 처리 경로·오차는 미명시 |

[원문 §III-B.1, §IV-E, PDF pp. 3, 6]

Vicon은 평가용 정답만 제공하는 장치가 아니다. **MoCap 실험에서는 실제 정책이 사용할 물체 pose와 장애물 지도 생성에 참여한다.** 마찬가지로 3Cam에서는 AprilTag tracking과 point cloud가 실행 중 상태 입력을 만든다. [원문 §IV-E, PDF p. 6]

### 3.3 센서 사양과 알고리즘 표현의 해상도 구분

| 항목 | 원문에 명시된 값 또는 확인 결과 |
| --- | --- |
| D435 수량 | 3대 |
| D435 RGB·depth 영상 해상도 | 미명시 |
| D435 frame rate·depth 측정 범위·depth 정확도·최소 분해능 | 미명시 |
| 카메라 intrinsics/extrinsics·동기화·point-cloud fusion 설정 | 미명시 |
| Vicon 모델·카메라 수·추적 주기·정확도·marker 배치 | 미명시 |
| Occupancy grid cell 크기 | **0.005 m × 0.005 m**, 즉 한 변 5 mm |
| Grid 크기 | **100 × 140 cells** |
| Patch 크기 | **16 × 16 cells** |
| F/T 센서 | 정책 관측·구현 설명에 F/T 측정 경로가 제시되지 않음 |
| Tactile 센서 | 전용 tactile sensor 또는 tactile observation이 제시되지 않음 |
| 힘·토크 측정 범위·분해능 | 사용 센서의 성능으로 보고된 값 없음. Grid 해상도나 충돌 penalty로 대신하지 않음 |

[원문 §III-A·B, §IV-A·E, Table I, PDF pp. 3–4, 6]

**5 mm는 카메라의 측정 정확도도, 촉각 공간 해상도도 아니다.** 센서 처리 이후 장애물 지도를 이산화하는 cell 크기다. 명시된 수치의 단순 계산상 지도는 0.50 m × 0.70 m에 대응하고 patch 한 변은 0.08 m다. 이는 계산상 대응값이며, 별도로 보고된 실물 table 전체 크기나 정확한 workspace 좌표 경계는 아니다. [원문 수치의 계산 해설]

## 4. 힘·접촉 정보는 어떻게 사용되는가

### 4.1 실제 관측 경로: 힘 신호가 아니라 기하 상태의 피드백

```text
시뮬레이션 object pose / 실물 MoCap·AprilTag object tracking
                       ┐
Pusher 위치와 목표 pose ├→ 수치 관측 MLP ───────────────────────┐
                       ┘                                       │
장애물 pose 또는 fused point cloud                             │
 → binary occupancy grid                                       │
 → patch embedding + patch 기준 object/target 위치              │
 → location-based attention → 장면 feature ─────────────────────┤
                                                               ↓
                                                       LSTM → MLP
                                                               ↓
                                                x·y별 categorical logits
                                                               ↓
                                                     pusher 평면 속도
                                                               ↓
                                         실제 로봇은 OpTaS → 관절 configuration
                                                               ↓
                                             물체가 움직이고 다음 관측 갱신
```

[원문 §III, §IV-E, Fig. 2, PDF pp. 2–3, 6의 설명을 흐름도로 재구성]

따라서 이 논문의 자세한 접촉 설명은 `raw wrench → filtering → contact estimate`가 아니라, **접촉 모드가 만들어 내는 행동의 다봉성을 어떻게 탐색하고, 장애물 접촉을 어떻게 학습 목표에서 억제하는지**에 관한 것이다.

### 4.2 구분해야 하는 네 종류의 접촉 관련 정보

| 개념 | 논문에서의 역할 | 그 자체로 뜻하지 않는 것 |
| --- | --- | --- |
| Sticking·sliding·separation | Planar pushing의 hybrid dynamics를 설명하고 categorical exploration을 선택하는 동기 | 센서로 접촉 모드를 분류해 actor에 입력함 |
| 물체·pusher pose의 시간 변화 | LSTM이 hidden temporal dynamics를 포착하는 근거 | 명시적 힘·마찰계수·관성 추정값을 출력함 |
| Obstacle contact 여부 | 학습 중 매 step 충돌 penalty와 평가 실패 판정 | F/T 또는 tactile의 thresholded 관측을 actor에 제공함 |
| 장애물 occupancy | 회피를 위한 공간 배치 표현 | 실제 접촉력 크기나 센서 압력 분포 |

[원문 §III-B, §IV-D, PDF pp. 3–5]

### 4.3 Categorical action은 접촉 모드 label이 아니다

저자들은 Gaussian 계열 unimodal exploration이 접촉 전환에 따른 multimodal interaction을 표현하기 어렵다고 설명한다. 대신 속도축마다 categorical distribution을 사용한다. **정책이 `stick`, `slide`, `separate` 중 하나의 이산 primitive를 출력하는 구조는 아니다.** 이산화된 것은 pusher 속도값이다. 접촉면 전환은 그 속도 행동이 만드는 실행 결과로 나타난다. [원문 §III-B, Fig. 4(a), PDF pp. 3, 5]

### 4.4 LSTM은 힘 센서의 대체 측정기가 아니다

원문은 LSTM을 통해 마찰·관성 등 hidden temporal dynamics를 포착한다고 설명한다. 현재 관측에 명시적 object velocity, force, friction coefficient 또는 inertia가 포함된다고 쓰지는 않는다. **LSTM hidden state를 이용하는 것**과 **마찰·관성을 물리 단위로 식별하고 검증하는 것**은 구분해야 한다. 본문에는 이러한 물리 파라미터 추정 오차나 hidden-state 해석 실험이 없다. [원문 §III-B.4, PDF pp. 3–4]

### 4.5 충돌 penalty의 역할과 한계

충돌 penalty는 pusher 또는 대상 물체가 장애물에 접촉했는지에 대한 **binary 판정**을 사용한다. 따라서 힘의 크기·충격량·접촉 면적·손상 가능성에 비례하는 penalty가 아니다. 충돌마다 뉴턴 단위 힘을 조절하거나 admittance로 회피하는 경로도 제시되지 않는다. [원문 §III-B.3, §IV-A, PDF pp. 3–4]

금지 접촉은 장애물 접촉이며, 밀기에 필요한 대상 물체와의 정상 접촉 전체를 벌점 처리하는 것이 아니다. Table II에 잔여 collision rate가 있으므로 **학습에 penalty를 넣었다는 사실을 충돌 불가능성의 보장으로 바꾸지 않는다.** [원문 §III-B.3, Table II, PDF pp. 3, 5]

## 5. 핵심 메소드 I — 지도와 location-based attention

### 5.1 Binary occupancy grid

각 episode 시작 시 workspace의 binary grid를 만든다. 값 1은 obstacle, 0은 free space다. 물체·목표 pose와 pusher 위치는 별도의 관측으로도 제공한다. Fig. 2의 object cell·target cell은 과업의 위치 문맥을 attention에 주는 데 사용된다. **지도 자체가 여러 tactile channel이나 힘 값의 영상이라는 의미는 없다.** [원문 §III-A.1·B.1, Fig. 2, PDF p. 3]

학습 비용을 줄이기 위해 한 episode 내부에서는 장애물 grid layout을 고정한다. 이는 모든 episode가 같은 배치라는 뜻이 아니다. Episode가 새로 시작될 때 object·pusher·obstacle·target pose를 다시 뽑는다. 실물에서는 지도 갱신이 가능하며, 동적 장애물에도 대응하는 것을 보인다. [원문 §III-B.1, §IV-A·E, PDF pp. 3–4, 6]

### 5.2 Patch embedding

Occupancy map을 16 × 16 patch로 나누고, 각 patch를 크기 **(192, 128)의 MLP**로 embed한다. 해당 patch의 장애물과 통과 가능한 공간에 대한 feature를 추출하는 과정으로 설명한다. 픽셀 자체를 actor의 거대한 단일 벡터로 바로 투입하는 것과 구분된다. [원문 §III-A.2, PDF p. 3]

단, **100 × 140 grid는 16 × 16 patch로 양 방향 모두 나누어떨어지지 않는다.** 원문은 padding·cropping·stride·중첩 여부를 설명하지 않는다. 따라서 patch 수를 특정 정수로 확정하거나 임의의 zero padding을 논문의 구현으로 적지 않는다. 이 문제는 §14에 따로 기록했다.

### 5.3 위치 문맥: 각 patch에서 물체와 목표가 어디에 있는가

각 patch의 embedding에 **그 patch의 좌상단을 기준으로 한 object position과 target position**을 concatenate한다. 같은 모양의 장애물이 있어도 현재 물체와 목표에 대한 상대 위치가 다르면 행동에 필요한 중요도가 다를 수 있기 때문이다. 이는 원문의 구조를 설명한 것이며, 어느 patch에 실제로 높은 attention이 나왔는지에 대한 별도 측정 결과는 아니다. [원문 §III-A.2, Fig. 2(c), PDF p. 3]

표현의 의미만 수식으로 쓰면, patch $i$의 좌상단 위치를 $c_i$, 물체·목표의 평면 위치를 $p_o,p_g$로 둘 때 다음의 위치 정보를 붙이는 구조다. **아래 기호는 해설용이며 원문에 번호가 붙은 수식이 아니다.**

$$
q_i=[p_o-c_i,\;p_g-c_i].
$$

차분의 개념은 원문을 따른다. 실제 코드가 meter·cell index 중 무엇을 쓰는지, 값을 어떤 범위로 정규화하는지는 미명시다. 물체·목표의 **방향**은 별도의 수치 관측 경로에 있고, 이 patch별 문맥의 본문 설명은 **위치**를 말한다. Pusher 위치까지 patch마다 concatenate한다고 임의 확장하지 않는다. [원문 §III-A.2·B.1, PDF p. 3]

### 5.4 Feature branch와 score branch

Embedding과 positional context에서 별도의 MLP들을 통해 **attention feature와 attention score**를 구한다. 원문은 MLP 크기를 (128, 100, 64)로 기재하며, Fig. 2(c)는 feature와 score를 곱한 결과를 weighted sum으로 모으는 흐름을 보여 준다. 최종 장면 feature는 **64차원**이다. [원문 §III-A.2·B.4, Fig. 2(c), PDF p. 3]

동작을 나누어 보면 다음과 같다.

| 처리 | 만드는 정보 | 다음 단계 |
| --- | --- | --- |
| Patch embedding | Patch 내부의 공간 feature | Object/target의 patch-relative 위치와 결합 |
| Feature MLP | 해당 patch에서 전달할 feature | Score와 결합 |
| Score MLP | 해당 feature의 가중 중요도 | Weighted aggregation |
| Weighted sum | 여러 patch에서 모은 64차원 장면 요약 | Robot/object/goal 수치 feature와 concatenate |

이 구조는 patch 간 모든 쌍의 self-attention을 계산하는 방식과 다르다. 다만 본문은 **score의 scalar/vector 여부, 최종 score head, softmax 유무·축, pooling의 정확한 수식**을 제시하지 않는다. 익숙한 Transformer 구현을 대입하여 이 부분을 채우지 않는다. 또한 attention map 시각화나 특정 patch 중요도의 정량 검증은 보고하지 않는다. [원문 §II–III-A, Fig. 2, PDF pp. 2–3]

## 6. 핵심 메소드 II — 관측·행동·정책과 value network

### 6.1 관측 항목

| 항목 | 명시된 표현 | 역할 |
| --- | --- | --- |
| 현재 대상 물체 pose | $(x_o,y_o,\theta_o)$ | 현재 물체 위치와 방향 |
| 목표 pose | $(x_g,y_g,\theta_g)$ | 최종 위치와 방향 조건 |
| Pusher position | $(x_p,y_p)$ | 현재 로봇 접촉 도구 위치 |
| Binary occupancy grid | 100 × 140 | 장애물 배치 |

[원문 §III-B.1, Table I, PDF pp. 3–4]

단순히 기재된 수치를 세면 비지도 상태는 8개 scalar이고 grid는 14,000 cells다. 이 합은 **원문 항목의 산술적 계산**이며, 실제 코드의 최종 observation tensor 크기·angle encoding·normalization까지 확인한 값이 아니다. Critic이 추가 privileged state를 받는 asymmetric 구조는 설명되지 않는다. Actor와 value network가 같은 architecture를 쓴다고 명시한다. [원문 §III-B.1·4, PDF p. 3]

### 6.2 속도 이산화와 22 logits

정책 행동은 pusher의 $(v_x,v_y)$이고 **각 축**을 −0.1~0.1 m/s로 제한한다. Bin 간격은 0.02 m/s다. 원문의 범위와 간격을 풀면 각 축의 후보는 다음과 같다.

$$
\mathcal V=\{-0.10,-0.08,-0.06,-0.04,-0.02,0,0.02,0.04,0.06,0.08,0.10\}\;\mathrm{m/s}.
$$

각 축 11개 후보이므로 출력은 **x축 categorical distribution의 11 logits + y축의 11 logits = 22 logits**다. 두 축 후보의 조합은 계산상 121개지만, 원문 정책이 121차원 단일 categorical head를 사용하는 것은 아니다. 실행 시 sample과 argmax 중 무엇을 택하는지 등 상세 선택 규칙은 본문에 없다. [원문 §III-B.2·4, PDF p. 3]

이산화가 연속 행동 공간에 Gaussian noise를 더하는 기존 방식과 다른 탐색 분포를 제공한다는 것이 저자들의 의도다. **`multimodal`은 여러 센서 modality를 뜻하는 것이 아니라 여러 행동 모드를 표현할 수 있다는 의미**다. [원문 §III-B, PDF p. 3]

또한 제한은 축별이므로 전체 속도 벡터 norm의 최대를 무조건 0.1 m/s라고 쓰면 안 된다. 두 축이 동시에 최대인 조합의 계산상 norm은 약 0.1414 m/s다. 추가 norm clipping이 있는지는 미명시다. 정책 주파수 10 Hz도 bin 간격 자체를 위치 분해능으로 바꾸지는 않는다. [원문 수치의 계산 해설]

### 6.3 정책·value network의 구조와 크기

```text
Occupancy grid + patch-relative object/target positions
 → Location-based attention → 64-D ──────────┐
                                             ├→ Concatenate: 128-D
Object pose + Target pose + Pusher position  │
 → MLP: 64-D ────────────────────────────────┘
 → LSTM: 256
 → MLP: 128
    ├─ Policy head: 22 logits, x/y별 categorical distribution
    └─ Value head: 1 scalar state-value estimate
```

위 도식의 두 head는 출력 차이를 비교하기 위해 나란히 표시했다. **원문이 같은 architecture라고 밝힌 것을 동일한 가중치를 공유하는 하나의 trunk라고 확정한 것은 아니다.** Encoder·LSTM의 weight sharing 여부는 미명시다. [원문 §III-B.4, Fig. 2(b), PDF p. 3]

물체와 pusher의 최근 움직임은 마찰·관성처럼 현재 pose만으로 완전히 설명되지 않는 동역학에 영향을 받는다. 저자들은 이를 위해 LSTM을 사용한다고 설명한다. Categorical/LSTM과 기존 Gaussian/MLP의 상세 비교는 [12]로 넘기며, 본 논문에는 이 두 요소 각각의 독립적인 새로운 정량 ablation 표가 없다. 본 연구에서도 기존 결과와 다른 경향을 관찰하지 않았다고만 적는다. [원문 §III-B.4, PDF pp. 3–4]

## 7. 핵심 메소드 III — reward, 종료와 성공 판정

### 7.1 원문 식 (1)

$$
r_{\mathrm{total}}=r_{\mathrm{term}}+k_1(1-r_{\mathrm{dist}})+k_2(1-r_{\mathrm{ang}})+r_{\mathrm{coll}}.
$$

| 항 | 정의 | 실제 설정·의미 |
| --- | --- | --- |
| $r_{\mathrm{dist}}$ | 물체와 목표 위치 사이 Euclidean distance를 [0,1]로 정규화 | 작을수록 위치 보상 증가. 정확한 정규화 분모·clipping은 미명시 |
| $r_{\mathrm{ang}}$ | 물체 방향과 목표 방향 사이 angular distance를 [0,1]로 정규화 | 작을수록 방향 보상 증가. 각도 wrap·대칭 처리·정규화 세부 미명시 |
| $k_1$ | 위치 항 scale | 0.1 |
| $k_2$ | 방향 항 scale | 0.02 |
| $r_{\mathrm{term}}$ | Sparse termination reward | 성공 +50, workspace boundary 위반에 따른 실패 −10 |
| $r_{\mathrm{coll}}$ | Pusher 또는 물체의 장애물 접촉에 대한 binary penalty | 접촉 step −5, 무충돌 step 0 |

[원문 §III-B.3, 식 (1), §IV-A, PDF pp. 3–4]

이 reward는 **매 step의 현재 목표 근접도**를 더하는 형태다. 이전 step과의 distance 차분이나 사전 global path에 대한 tracking error라고 설명하지 않는다. 물체의 위치·방향을 각각 보상하므로 단순한 position-only pushing과도 다르다. [원문 식 (1)의 해설]

### 7.2 Reward가 접촉과 방향 결정을 어떻게 유도하는가

위치 항만으로는 물체 중심이 가까워져도 최종 방향이 맞지 않을 수 있다. 방향 항은 대상 물체의 최종 orientation을 맞출 필요성을 부여한다. 장애물 penalty는 pusher가 안전하더라도 물체가 부딪히는 행동, 또는 물체만 피하고 pusher가 부딪히는 행동을 모두 억제한다. Categorical action과 LSTM은 이 목적 아래 접촉 위치·접촉면을 바꾸는 속도 행동을 학습한다. [원문 §III-B, §IV-A, Fig. 4, PDF pp. 3–5의 구조 해설]

명시된 범위상 위치·방향 dense 항의 합은 0~0.12다. 따라서 −5의 충돌 penalty는 한 step의 최대 dense 항보다 크다. 이는 **원문 식의 대수적 비교**이지 장기 return에서 충돌이 절대 선택되지 않는다는 보장이 아니다. Terminal reward, 남은 horizon, value estimate 등이 함께 영향을 받는다. 원문에는 별도 constrained-RL 안전 보장이나 control barrier function이 제시되지 않는다.

힘 크기를 제한하는 항, 최소 접촉력 유지 항, 접촉점 중심 유지 항, 속도·가속도·jerk penalty는 **기재된 식 (1)에 없다.** 원문이 보고하는 smooth trajectory를 이러한 미기재 항의 결과로 설명하지 않는다.

### 7.3 종료의 종류를 구분한다

| 상황 | 원문이 밝힌 처리 | 주의 |
| --- | --- | --- |
| 목표 성공 | 큰 양의 termination reward +50 | 평가 성공에는 pose뿐 아니라 무충돌·workspace·시간 조건도 있음 |
| Workspace 위반 실패 | Termination reward −10 | 정확한 경계 좌표와 중심/형상 기준은 미명시 |
| 장애물 접촉 | 매 step −5, 평가에서는 성공 조건을 위반 | 접촉 즉시 reset하는지, 접촉 이력을 누적해 종료 시 판정하는지는 명확히 기재되지 않음 |
| 학습 time limit | 최대 160 steps, value estimate로 마지막 reward를 bootstrap | Boundary failure와 같은 −10을 무조건 부여한다고 쓰지 않음 |
| 평가 time limit | 최대 200 steps | 더 복잡한 장애물 장면을 고려해 학습보다 늘림 |

[원문 §III-B.3, §IV-A·D, PDF pp. 3–5]

§III-B.3은 성공 이외의 termination을 음수로 개괄하지만, 구체 설정인 §IV-A는 −10을 workspace 위반에 연결하고 timeout에는 bootstrapping을 별도로 설명한다. Timeout의 정확한 식·보상 부호를 일반 PPO 지식으로 보충하지 않는다.

### 7.4 시뮬레이션 정량 평가의 성공 조건

물체를 목표 **위치 1.5 cm 이내, 방향 $\pi/6$ rad 이내**로 옮기고, pusher와 물체가 장애물에 충돌하지 않으며, 물체가 workspace 안에 남아 있고, 200 steps 이내에 완료해야 성공이다. $\pi/6$ rad는 **30°다.** 목표 방향을 고려한다는 사실을 1° 수준의 고정밀 정렬 검증으로 확대하지 않는다. [원문 §IV-D, PDF p. 5]

이 기준의 대상은 pusher가 아니라 **조작 물체의 pose**다. 또한 위치 허용 오차 1.5 cm는 카메라나 로봇의 측정·반복정밀도가 아니라 task success threshold다.

## 8. RL 학습 환경·hyperparameter·sim-to-real

### 8.1 학습 장면과 reset

Isaac Sim의 custom environment에서 massively parallel PPO를 학습한다. 기본 장면은 단일 직사각형 장애물이며, episode 시작마다 pusher·물체·장애물·목표의 pose를 랜덤화하되 **장애물이 물체와 목표 사이에 위치하도록** 구성한다. 이후 두 장애물 장면에서 fine-tuning한다. [원문 §IV-A, PDF p. 4]

여기서 시작 pose의 정확한 분포, 비겹침 검사, 항상 해결 가능한 장면만 남기는지, 초기 pusher–object 접촉을 강제하는지, 물체의 기준 치수는 미명시다. 단일 장애물이 두 상태 사이에 놓인다는 설명을 상세한 path feasibility sampler로 바꾸지 않는다.

### 8.2 Table I — PPO 설정

| 원문 parameter | 원문 값 | 해설·주의 |
| --- | --- | --- |
| Grid Size | 100 × 140 | 지도 cells 수 |
| Parallel Environments | 1,440 | 동시 환경 수 |
| Batch Size | 14,400 | 표의 명칭 그대로. Mini-batch와 전체 rollout buffer의 관계는 별도 설명 없음 |
| Rollout Length | 120 | Rollout 수집 길이 |
| Update Epochs | 5 | Update epoch 수 |
| Clip range $(\epsilon)$ | 0.2 | PPO clip 설정 |
| Discount factor $(\lambda)$ | 0.99 | **원문이 discount에 lambda를 사용**함 |
| GAE parameter $(\gamma)$ | 0.95 | **원문이 GAE에 gamma를 사용**함 |
| Entropy bonus coefficient | 0 | 별도 entropy 보너스의 계수. Categorical sampling의 부재를 뜻하지 않음 |
| Value function coefficient | 0.5 | Value loss 계수 |
| Optimizer | Adam | Adam 세부 파라미터 미명시 |

[원문 Table I, PDF p. 4]

원문 표의 discount/GAE 기호는 흔히 사용하는 표기와 반대다. **이 문서는 parameter 이름과 수치를 원문대로 보존**하며, 코드 변수의 `gamma`·`lambda`에 어떤 값이 들어가는지 확인한 것으로 취급하지 않는다.

Learning rate는 policy KL divergence에 따른 adaptive schedule [31]을 사용하고 **target KL은 0.01**이다. 초기 learning rate, 상·하한, 증가·감소 배율, gradient clipping, activation, recurrent sequence sampling·hidden-state reset 설정은 본문에 없다. [원문 §IV-A, PDF p. 4]

명시된 병렬 수와 rollout length를 곱하면 172,800 transitions다. 이는 두 설정의 산술적 곱이며, **Batch Size 14,400을 전체 수집량이라고 바꾸거나 코드 확인 없이 정확히 12 mini-batches라고 단정하지 않는다.** 학습 곡선 Fig. 5는 3 × 10^9 training steps까지 표시되지만, 집계 step의 내부 정의·checkpoint 선택 규칙·학습 시간은 미명시다.

### 8.3 Table I — dynamics·geometry randomization과 observation noise

| Parameter | 원문 분포 | 구분 |
| --- | --- | --- |
| Static friction | $\mathcal U[0.5,0.7]$ | 동역학 |
| Dynamic friction | $\mathcal U[0.2,0.4]$ | 동역학 |
| Restitution | $\mathcal U[0.4,0.6]$ | 동역학 |
| Object mass | $\mathcal U[0.4,0.6]$ kg | 물체 질량 |
| Object scale | $\mathcal U[0.9,1.1]$ | 기준 형상에 대한 scale |
| Obstacle scale | $\mathcal U[0.8,1.2]$ | 장애물 scale |
| Pusher scale | $\mathcal U[0.95,1.05]$ | Pusher scale |
| Position noise | $\mathcal N[0,0.001^2]$ m | 위치 관측 noise |
| Orientation noise | $\mathcal N[0,0.02^2]$ rad | 방향 관측 noise |

[원문 Table I, PDF p. 4]

원문은 uniform과 normal distribution을 각각 U와 N으로 표시한다. Noise의 제곱 표기는 위와 같이 보존한다. 표가 나타내는 위치·방향 표준편차는 각각 0.001 m와 0.02 rad로 읽을 수 있으나, 이는 **합성 관측 잡음 설정**이지 실제 Vicon·D435 성능의 실측치가 아니다.

물체 pose와 pusher position에 **episode 시작 때 뽑는 correlated noise**와 **매 step 뽑는 uncorrelated noise**를 더한다. 전자는 한 episode에 공통되는 오차, 후자는 시간별 변동을 반영하려는 구성이다. 다만 두 성분 각각에 표의 분산을 그대로 사용하는지, 축 간 covariance, 추가적인 시간 필터가 있는지는 명시되지 않는다. Target pose나 occupancy grid에도 동일 잡음을 넣었다고 확장하지 않는다. [원문 §IV-A, PDF p. 4]

### 8.4 학습과 평가에서의 시간·장애물 조건

정책은 10 Hz로 동작하고, 최대 길이는 훈련 160 steps·평가 200 steps다. 주파수로 환산한 nominal policy time은 각각 16 s·20 s이지만, 시뮬레이션 wall-clock이나 실물에서 측정한 평균 소요 시간은 아니다. [원문 §IV-A 수치의 해설]

훈련 episode 안의 지도는 고정되어 있고 **동적 장애물을 학습에서 경험하지 않았다**고 명시한다. 평가의 동적 장애물은 y축을 따라 0.1 m/s로 이동하며 workspace 경계에서 방향을 반전한다. 실물 동적 시연은 사람이 장애물을 물체 경로와 교차하도록 재배치하는 경우다. 두 실험을 동일한 속도·운동 분포로 수행한 것으로 취급하지 않는다. [원문 §III-B.1, §IV-D·E, PDF pp. 3, 5–6]

### 8.5 Sim-to-real의 실제 구성: GAN·시연은 없음

이 논문의 sim-to-real은 **dynamics/geometry randomization + 합성 pose noise + 실제 지각 결과를 같은 상태 표현으로 변환 + OpTaS를 통한 로봇 행동 변환**으로 설명된다. GAN, real-to-sim tactile image translation, diffusion model, human demonstration dataset은 제시하지 않는다. [원문 §IV-A·E, PDF pp. 4, 6]

Policy는 변화된 지도·물체 pose에 매번 반응하지만, 실물 실행 중 PPO 가중치를 갱신하는 online retraining은 제시하지 않는다. **상태 변화에 대한 recurrent policy 반응**과 **두 장애물 시뮬레이션에서의 추가 학습**은 다른 과정이다.

## 9. 비교 실험 설계

### 9.1 [9] 재구현: global path guidance의 영향

Dengler et al. [9]는 가장 가까운 외부 baseline이다. 저자들은 이를 **PyBullet에서 재구현**한다. 사전 global path를 필요로 하는 방식이 GPU 병렬화에 부적합하여 Isaac Sim 통합이 어렵다는 이유를 든다. 이 비교에서는 [9]를 따라 **목표 방향을 제외하고 2D 목표 위치만** 평가한다. [원문 §IV-B, PDF p. 4]

처음에는 target orientation을 관측·reward에 넣어 보았으나 수렴하지 않았다고 보고한다. 이어 path subgoal을 주는 경우와 제거하는 경우를 비교한 Fig. 3에서 guidance가 있는 baseline은 수렴하지만 없는 경우는 실패한다. 저자들은 orientation-aware global path를 만들려면 $(x,y,\theta)$ configuration space 탐색이 필요해 공간 이산화 또는 계산량 문제가 커진다고 설명한다. [원문 §IV-B, Fig. 3, PDF p. 4]

**해석 범위:** Fig. 3은 외부 baseline의 guidance 의존성을 확인하는 실험이다. 제안법과 모든 조건을 동일하게 놓은 orientation-aware 최종 성공률 비교가 아니다. Fig. 3의 x축은 10^6 steps, Fig. 5의 x축은 10^9 steps이고 simulator·과업 조건도 다르므로 두 그림만으로 sample efficiency의 우열을 직접 산출하지 않는다.

### 9.2 공간 feature extractor ablation

| 비교군 | 변경 | 원문 결과·조건 |
| --- | --- | --- |
| Location-based attention | 제안한 score-weighted feature aggregation | 기준 방법 |
| CNN | Occupancy grid를 3개 CNN layer로 처리 | 초기 수렴은 더 빠르지만 최종 성능은 낮음 |
| No-attention MLP | Weighted score sum을 없애고 feature concatenate 후 [2048,512,64] MLP로 압축 | 학습 수렴 실패 |
| Multi-head self-attention (MHA) | ViT에서 흔히 쓰는 pairwise attention을 시험 | A6000 48 GB에서 병렬 학습을 진행하기 어려워 최종 비교에서 제외 |

[원문 §IV-C, PDF pp. 4–5]

CNN·MLP 대안의 learnable parameter 수는 제안법과 대략 맞췄다고 설명한다. 정확한 parameter 수, CNN kernel·stride·channel, MHA head 수·embedding 설정은 미명시다. **MHA가 완료된 실험에서 낮은 성공률을 보였다는 뜻이 아니라, 해당 구성에서 학습 비용 문제가 발생해 제외되었다는 뜻**이다.

### 9.3 Fig. 5의 학습 곡선과 메모리

Fig. 5는 세 training seeds의 평균과 표준편차를 보고한다. 본문이 적은 최종 success rate는 attention **96%**, CNN **87%다.** CNN은 더 빨리 수렴하기 시작하지만 최종 수준이 낮으며, no-attention MLP는 수렴하지 못한다. [원문 §IV-C, Fig. 5, PDF p. 5]

CNN은 제안법보다 **GPU memory를 70% 더 사용**한다고 보고한다. 저자들은 convolution의 큰 intermediate feature map을 이유로 든다. 이를 attention이 메모리를 70% 절감한다는 표현으로 바꾸지 않는다. 기준 분모가 다르고, 절대 사용량·처리량·전체 wall-clock은 본문에 없다. MHA의 불가능성 역시 모든 크기의 self-attention 일반론이 아니라 해당 병렬 학습 실험 조건에 관한 결과다.

## 10. 시뮬레이션 정량 평가

### 10.1 평가 조건

각 정책을 **환경별 2,000 episodes**에서 평가한다. 시작·목표 pose, 장애물 pose·크기·형상을 바꾸며, 미지 circular·cross·T·L shape, dynamic obstacle, dual obstacles를 시험한다. 성공·collision rate와 나머지 timeout·workspace 실패를 구분한다. [원문 §IV-D, Table II, PDF pp. 5–6]

`Training`이라는 표의 첫 행은 **학습과 같은 종류의 장면에 대한 평가 결과**이며, Fig. 5의 training curve 최종 평균 수치와 동일한 통계로 취급하지 않는다. Table II의 97.1%와 Fig. 5 설명의 96%를 하나로 임의 통일하지 않는다.

### 10.2 Table II 전체 결과

단위는 모두 %. `DFT`는 **dual-obstacle fine-tuning 이후 정책**을 뜻한다. Fine-tuning을 하지 않은 정책과 한 표에 섞여 있으므로 행 이름을 유지한다.

| Experimental setup | Attention 성공률 | Attention 충돌률 | CNN 성공률 | CNN 충돌률 |
| --- | ---: | ---: | ---: | ---: |
| Training | 97.1 | 1.26 | 88.5 | 4.83 |
| Circular | 95.6 | 2.66 | 84.7 | 0.56 |
| Cross-Shape | 94.1 | 2.90 | 84.5 | 1.75 |
| T-Shape | 93.5 | 4.72 | 85.3 | 0.97 |
| L-Shape | 90.2 | 7.75 | 83.8 | 2.47 |
| Dynamic | 84.3 | 12.0 | 73.5 | 14.9 |
| Dual Obstacles | 48.1 | 50.7 | 57.9 | 34.3 |
| Dual fine-tuned (DFT) | 91.2 | 3.54 | 61.1 | 3.22 |
| Circular (DFT) | 96.4 | 0.20 | 72.1 | 0.34 |
| Cross-Shape (DFT) | 96.7 | 0.33 | 73.8 | 0.54 |
| T-Shape (DFT) | 96.3 | 1.32 | 71.9 | 1.01 |
| L-Shape (DFT) | 94.9 | 1.58 | 71.2 | 1.22 |
| Dynamic (DFT) | 91.4 | 5.2 | 61.6 | 10.8 |

[원문 Table II, PDF p. 5. 표의 수치·소수 자릿수 보존]

### 10.3 단일 장애물: 낮은 충돌률만으로 성공을 판단할 수 없다

미지 단일 형상과 동적 장애물에서는 attention의 성공률이 CNN보다 높다. 그러나 fine-tuning 이전 circular·cross·T·L shape의 collision rate는 CNN이 더 낮다. 저자들은 CNN 정책이 pushing을 완전히 멈추는 **inaction** 때문에 충돌 대신 timeout이 늘어났다고 설명한다. [원문 §IV-D, PDF p. 6]

이는 저자들의 실행 관찰에 따른 설명이다. 본문에는 각 형상의 inaction 발생 횟수나 timeout 세부 비율을 분리한 표가 없으므로, 남은 실패를 모두 멈춤 하나로 정확하게 분해할 수는 없다. 성공률과 충돌률을 함께 읽어야 한다는 결론은 유지하되 미제시 통계를 만들지 않는다.

### 10.4 두 장애물: zero-shot 일반화와 추가 학습을 구분한다

단일 장애물로 학습한 정책을 두 장애물 장면에 바로 적용하면 attention은 **성공 48.1%, 충돌 50.7%**, CNN은 **성공률 57.9%·충돌률 34.3%를 기록했다.** **이 조건에서는 제안 attention이 CNN보다 나쁘다.** Table II caption의 ‘모든 장면에서 더 높은 성공률’이라는 포괄 서술을 그대로 반복하면 이 예외가 사라진다. 본문 §IV-D는 이 성능 역전을 명시적으로 인정한다. [원문 Table II, §IV-D, PDF pp. 5–6]

이후 두 장애물 환경에서 **5 × 10^8 steps**를 추가 학습하면 attention의 성공률은 **91.2%**, 충돌률은 **3.54%로 낮아진다.** CNN도 fine-tuning하지만 성공률은 **61.1%**, 충돌률은 **3.22%다.** 따라서 여기서 강하게 뒷받침되는 것은 모든 복잡도에 대한 즉시 일반화가 아니라 **더 복잡한 장면에 추가 학습했을 때의 적응 능력**이다. [원문 §IV-D, PDF p. 6]

### 10.5 Fine-tuning 이후 단일 장애물 재평가

Attention은 DFT 후 미지 단일 형상·동적 장면에서도 성공률이 개선된다. 예를 들어 dynamic은 84.3%에서 91.4%로, L-shape은 90.2%에서 94.9%로 오른다. 반대로 CNN은 DFT 후 해당 단일 장애물 성공률이 낮아진다. 원문은 이를 feature representation과 fine-tuning을 통한 일반화 차이로 해석한다. [원문 §IV-D, Table II, PDF pp. 5–6]

**DFT 정책이 dynamic에서 잘했다고 해서 dynamic obstacle로 추가 학습한 것은 아니다.** 추가 학습은 dual-obstacle 장면이고, 동적 장애물은 미경험 평가 조건이다. 또한 미지 형상에 대한 주 정량 평가는 **장애물 형상**을 바꾼 실험이다. 이를 조작 대상의 임의 형상·재질 전반에 대한 동일 수준의 검증이라고 확대하지 않는다.

## 11. 실물 실험과 관측→행동의 실제 예

### 11.1 정량 MoCap 실험

실물은 KUKA iiwa와 OpTaS, Vicon 기반 상태 추적을 사용한다. 논문은 세 MoCap scenario에서 random initial configuration 10개를 시험하고 다음 성공률을 보고한다. **실물의 target pose는 setup을 단순화하기 위해 고정**하며, 시뮬레이션에서는 target pose까지 랜덤화한다. [원문 §IV-E, PDF p. 6]

| MoCap scenario | 실물 결과 | 원문이 설명하는 행동 |
| --- | --- | --- |
| (a) 단일 rectangular obstacle | 성공률 100% | 접촉면을 바꾸며 물체를 우회시킴 |
| (b) 미지 형상의 단일 장애물 | 성공률 100% | Fig. 4(b)의 L-shape 주변으로 매끄럽게 우회 |
| (c) 분리된 두 장애물 | 성공률 90% | 좁은 틈에 물체를 맞춰 통과. 한 번의 collision 실패 |

[원문 §IV-E, Fig. 4, PDF pp. 5–6]

두 장애물에서의 90%와 한 번 실패라는 설명은 10회의 평가에 대응한다. 다만 본문은 전체 실물 trial ledger나 scenario별 시작 pose 목록·실물 전용 성공 tolerance를 별도로 제시하지 않는다. **세 비율을 시뮬레이션의 2,000-episode 결과와 같은 표본 규모로 취급하지 않는다.** 실물 CNN과의 동일 조건 정량 비교도 보고하지 않는다.

### 11.2 Fig. 4: 정책이 생성한 물체 경로

Fig. 4는 offline reference path가 아니라 **정책이 실제 robot에서 실행되어 나온 물체 trajectory**를 보여 준다. 파란 궤적과 연속된 물체 pose로 위치·방향의 변화를 나타낸다. 단일 장애물에서의 contact-surface switching, L-shaped 장애물 우회, 두 장애물 사이의 좁은 틈 통과가 각각 제시된다. [원문 Fig. 4 caption, PDF p. 5]

이는 정책이 선택한 속도 행동으로 물체의 translation과 orientation을 함께 바꾸는 예다. 해당 그림이 힘 벡터나 tactile contact map을 시각화하는 것은 아니다.

### 11.3 Fig. 6: 움직이는 장애물

물체를 밀기 시작한 이후 장애물을 물체의 경로와 교차하도록 옮긴다. Fig. 6은 로봇이 그 변화를 반영하여 장애물을 피해 목표로 가는 keyframes를 보인다. 이 실물 dynamic 평가에 대해 **성공률·반복 수·장애물 이동 속도 수치**는 제시하지 않는다. 정성 시연을 Table II의 simulation dynamic 84.3% 또는 DFT 91.4%와 혼용하지 않는다. [원문 §IV-E, Fig. 6, PDF p. 6]

### 11.4 Fig. 7: 3Cam의 일상 물체 장면

RealSense D435 3대와 AprilTags로 대상 pose를 추적하고 point cloud를 융합해 지도를 구성한다. Fig. 7의 dining-table scenario에서는 여러 물체 사이의 좁은 통로를 통과한 뒤 대상 물체의 방향을 바꾸어 target pose에 도달한다. 이는 **3Cam 지각 경로의 정성 검증**이며, MoCap의 100%·100%·90%를 3Cam 결과로 옮겨 적지 않는다. [원문 §IV-E, Fig. 7, PDF pp. 6–7]

원문은 recorded scenario에서 smooth, continuous trajectory를 보였다고 설명한다. 속도 bin을 쓰면서도 이런 실행 결과를 보일 수 있다는 관찰과, 수학적으로 연속적인 가속도·jerk 제한을 보장하는 것은 다르다. 별도 smoothing filter의 구현이나 smoothness 지표는 미명시다.

## 12. Limitation — 저자들이 밝힌 한계와 실험상 제약

원문에는 독립된 `Limitation` 절이 없다. 다음은 본문에서 저자들이 직접 인정한 자기 방법의 실패·제약·평가 제한을 모은 것이며, 미명시 구현 정보는 §14와 구분한다.

### 12.1 단일 장애물 학습만으로 두 장애물에 충분히 일반화되지 않음

가장 명확한 잔여 실패는 two-obstacle direct transfer다. 성공률 48.1%, 충돌률 50.7%이고 CNN보다도 낮다. 저자들은 이를 더 어려운 환경의 성능 격차로 설명하고 dual-obstacle fine-tuning으로 보완한다. **추가 학습의 개선은 이미 수행한 실험이지 향후 계획이 아니다.** [원문 §IV-D, PDF p. 6]

### 12.2 충돌·timeout·workspace 실패가 남음

미지 형상·동적 조건에서도 성공률은 100%가 아니며 Table II가 collision과 기타 실패를 보고한다. 원문이 언급하는 기타 실패는 time limit와 workspace boundary 위반이다. 실물 dual-obstacle 평가에서도 한 collision이 있었다. 이를 전 장면의 안전 보장으로 해석할 수 없다. [원문 Table II caption, §IV-D·E, PDF pp. 5–6]

### 12.3 학습 환경의 추상화와 static layout

저자들은 계산 효율을 위해 robot을 spherical pusher로 추상화하고 훈련 episode 내부의 obstacle layout을 고정한다고 명시한다. 동적 장애물 결과는 이런 static training에서의 일반화 실험이다. 실제 arm 전체의 동역학·자가충돌까지 포함한 학습 결과로 바꾸지 않는다. [원문 §III-B.1, §IV-A, PDF pp. 3–4]

### 12.4 실물 target 고정과 일부 정성 평가

실물에서는 목표 pose를 고정했다고 직접 설명한다. 정량 결과는 MoCap의 세 scene 유형에 대해 제공하고, dynamic·3Cam의 복잡한 일상 장면은 qualitative evaluation으로 보고한다. 따라서 모든 목표·모든 지각 조건에서 같은 통계로 검증되었다고 표현하지 않는다. [원문 §IV-E, PDF pp. 6–7]

### 12.5 비교 실험의 계산·과업 제약

MHA는 높은 memory 사용 때문에 해당 대규모 병렬 조건에서 최종 학습 비교에서 제외했다. 외부 baseline [9]는 target orientation을 포함할 때 수렴하지 않아 position-only guidance 비교만 남겼다. 이는 **비교 범위의 제약**이며, 본 연구 정책 자체가 MHA를 포함한다거나 모든 경쟁 방법에 동일 조건으로 승리했다는 의미가 아니다. [원문 §IV-B·C, PDF pp. 4–5]

## 13. Future Work — 저자들이 제시한 향후 연구

**원문에 명시된 구체적인 Future Work 계획 없음.** §V Conclusion은 수행한 framework·attention·categorical exploration·sim-to-real 결과를 요약하며, 별도의 후속 연구 항목을 제안하지 않는다. [원문 §V, PDF p. 7]

두 장애물 fine-tuning, dynamic obstacle 대응, 3Cam 실물 실행은 이미 보고된 내용이므로 미래 과제로 분류하지 않는다. 또한 force/tactile 추가, occlusion 처리, 더 많은 물체, 다른 로봇 전이 등을 정리자가 저자의 계획처럼 만들어 넣지 않는다. Future Work가 미명시라는 사실은 개선 여지나 한계가 없다는 뜻이 아니다.

## 14. 원문만으로 확인되지 않는 사항과 표기 주의점

### 14.1 재현 정보의 공개 수준

| 확인 항목 | 본문에서 직접 확인 가능 | 추가 확인이 필요한 것 |
| --- | --- | --- |
| RL 종류 | On-policy PPO, categorical exploration | 사용 라이브러리·실제 코드 버전 |
| Reward | 식 (1), dense scale·collision·success·boundary 값 | Distance 정규화, angular wrap·대칭, collision 종료, timeout 구현 |
| 정책 입력 | 물체/목표 pose·pusher 위치·grid | 좌표 원점·단위 정규화·각도 encoding, hidden-state 처리 |
| 네트워크 | Patch/feature/score MLP 크기, 64-D scene feature, LSTM256, MLP128, outputs22/1 | Activation, weight sharing, score head·normalization |
| Patch 분할 | 16 × 16, 지도100 × 140 | Padding·cropping·stride·실제 patch 수 |
| PPO 설정 | Table I, KL target0.01, 5 epochs | 초기 LR·schedule bounds, gradient clip, optimizer 세부, batch 구성 |
| Randomization | Table I 범위, 두 시간척도의 pose noise | 각 noise 성분의 분산 배분·axis covariance, 세부 물리 적용 대상 |
| Geometry·reset | Spherical pusher, 기본 직사각형 장애물, pose randomization | 원래 치수·radius·sampling 범위·초기 접촉·해결 가능성 검사 |
| Training budget | Fig. 5 표시범위, DFT5 × 10^8 steps | Step 집계 정의·실제 최종 stop·checkpoint selection·wall-clock |
| 실물 지각 | Vicon 또는 D4353대+AprilTags+point clouds | 장비별 성능, extrinsics·fusion·grid projection·갱신 지연 |
| 실제 제어 | OpTaS, 평면 속도 action, policy10Hz | 하위 제어법·gain·force limit·IK formulation·servo 주기 |
| 힘·촉각 | 정책 관측에 없음, binary collision penalty | 별도 raw force/tactile 처리법을 추정하여 채우지 않음 |
| 실물 성능 | MoCap 세 scene의 성공률과 정성 시연 | 3Cam/dynamic 반복 통계, 전체 trial 목록, 실물 전용 tolerance |

[원문 §III–V, Fig. 2–7, Table I–II, PDF pp. 2–7]

### 14.2 Grid와 patch 크기의 정합성

Table I의 100 × 140은 14,000 cells이고 16 × 16 patch는 256 cells다. $14000/256=54.6875$이며 각 축도 16으로 나누어떨어지지 않는다. 본문은 patch들이 원래 지도 크기와 맞는다고 설명하지만 가장자리 처리 방식은 없다. **정리본에서 54개·55개·63개 등 어느 숫자도 실제 patch 수로 확정하지 않는다.** [원문 §III-A.2, Table I, PDF pp. 3–4]

### 14.3 Discount factor와 GAE의 기호

Table I는 `Discount factor (λ) = 0.99`, `GAE parameter (γ) = 0.95`라고 인쇄되어 있다. 일반적인 표기와 다르지만, 여기서는 이름·수치를 보존하고 이 기호 문제를 명시한다. 실제 코드의 변수명과 값이 어떻게 대응하는지는 이번 확인 범위 밖이다. [원문 Table I, PDF p. 4]

### 14.4 Table II caption의 포괄 주장과 반례

Caption은 모든 scenario에서 더 높은 성공률을 보인다고 적지만, fine-tuning 전 Dual Obstacles 행은 CNN 57.9%가 attention 48.1%보다 높다. 본문은 이 예외를 인정하므로 **표와 본문의 조건부 설명을 함께 보존**한다. Caption을 근거로 ‘모든 조건에서 우수’라고 결론 내리지 않는다. [원문 Table II, §IV-D, PDF pp. 5–6]

### 14.5 성능 수치·속도·일반화 범위의 혼동 방지

Fig. 5의 training success 평균 96%/87%와 Table II의 training-layout 평가 97.1%/88.5%는 서로 다른 보고다. 축별 속도0.1 m/s와 전체 속도 norm, policy10Hz와 sensor frame rate, grid5mm와 측정 정확도, orientation tolerance30°와 실제 평균 각도 오차도 각각 다른 수치다.

동적 장애물에 대한 일반화는 **현재 지도와 pose가 계속 제공되는 조건**이다. 현재 장애물 지도를 갱신하지 않아도 동적 물체를 예측하여 회피했다거나, 시각 가림 상황에서 tactile로 대신 추적했다고 쓰지 않는다. 미지 **장애물 형상**을 바꾸는 실험과 임의의 **조작 대상 형상**에 대한 일반화도 구분한다. [원문 §III-B.1, §IV-C–E, PDF pp. 3, 5–6]

### 14.6 원문 figure 참조와 인용 자료

§III-A.2의 patch embedding 설명은 `2.a`를 가리키지만, Fig. 2에서 attention module의 상세 도식은 **(c)다.** 그림의 실제 label을 따라 위치를 안내한다. 또한 §IV-A가 simulator를 Isaac Sim [30]으로 소개할 때 [30]의 참고문헌 제목은 *Orbit: A Unified Simulation Framework for Interactive Robot Learning Environments*다. 이를 근거로 실제 사용 환경을 최신 Isaac Lab 특정 버전으로 바꾸지 않는다. [원문 §III-A.2, §IV-A, References [30], PDF pp. 3–4, 7]

## 15. 원문 위치 안내와 확인 기록

### 15.1 재독할 위치

| 읽고 싶은 내용 | 원문 위치 |
| --- | --- |
| 문제·guidance-free의 의미·기여 | Abstract, §I, PDF pp. 1–2 |
| MPC·push–grasp·corridor·기존 RL과의 관계 | §II, PDF p. 2 |
| 실제 관측과 attention 구조 | §III-A·B.1·B.4, Fig. 2, PDF p. 3 |
| Categorical 속도 action | §III-B.2·4, PDF p. 3 |
| Reward와 변수 정의 | §III-B.3, 식 (1), PDF p. 3 |
| PPO 값·물리 randomization·noise | §IV-A, Table I, PDF p. 4 |
| 외부 baseline guidance 비교 | §IV-B, Fig. 3, PDF p. 4 |
| CNN·MLP·MHA ablation | §IV-C, Fig. 5, PDF pp. 4–5 |
| 전체 quantitative 결과·성공 기준 | §IV-D, Table II, PDF pp. 5–6 |
| 두 장애물 direct transfer와 fine-tuning | §IV-D, PDF p. 6 |
| 실물 센서 구성·성공률·정성 시연 | §IV-E, Fig. 4·6·7, PDF pp. 5–7 |
| 결론·Future Work 미명시 확인 | §V, PDF p. 7 |

### 15.2 외부 자료의 확인 경계

원문은 구현 저장소 [LearnToPush/attention-pushing](https://github.com/LearnToPush/attention-pushing)와 [보충 영상](https://youtu.be/Ef0_oQiDq2E)을 제공한다. 이 링크는 **원문에 제시된 자료 위치를 기록한 것**이며, 이번 작업에서 해당 코드·영상·제조사 데이터시트를 분석하거나 학습·실물 실험을 재현하지 않았다. 미명시 정보는 그 자료의 내용을 추정해 채우지 않았다.

### 15.3 문서 검증 범위

출판본 7쪽의 본문·수식·표·그림을 확인하고, Table I의 기호와 Table II의 수치를 실제 PDF 표시와 대조했다. Markdown 수식은 블록 `$$`와 인라인 `$…$`로 작성했다. 수식 35개(블록 3개·인라인 32개)의 로컬 MathJax 구문 검사에서 오류가 없었고, 블록 수식 전체의 렌더링과 표 19개의 열 구조를 확인했다. 로컬 Chromium에서 문서 표시를 확인하고 `git diff --check`를 통과했다. GitHub 웹페이지 자체의 최종 렌더링은 접근 제한으로 확인하지 못했다. 코드·학습·실물 실험 재현은 수행하지 않았다.
