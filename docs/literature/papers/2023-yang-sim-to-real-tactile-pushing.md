# Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing — 원문 상세 정리

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing** |
| 저자 | Max Yang, Yijiong Lin, Alex Church, John Lloyd, Dandan Zhang, David A. W. Barton, Nathan F. Lepora |
| 출판 | IEEE Robotics and Automation Letters, 8(9), 5480–5487, September 2023 |
| DOI | [10.1109/LRA.2023.3295236](https://doi.org/10.1109/LRA.2023.3295236) |
| 기존 조사본 식별자 | [2026-09-14 문헌조사](../reviews/2026-09-14_blind-sweep-force-torque-tactile.md)의 **R4** |
| 정리일 | 2026-09-15 |
| 확인한 원문 | 제공된 출판본 PDF 8쪽 전체. 본문 §I–V, 식 (1)–(4), 번호 없는 모델·계획 수식, Fig. 1–7, Table I–III, References |
| 확인하지 않은 자료 | 인용된 선행논문의 개별 원문, 저자 구현 코드·설정 파일·체크포인트, 보충 영상, 제조사 데이터시트 |
| 원문 PDF SHA-256 | `924f25a41346a6146e2861bc126197364149d66da79797d19145906af4a77652` |

[개별 논문 색인](README.md) · [문헌조사 자료](../README.md)

이 문서는 해당 논문 자체의 문제 상황, 관련 연구, 플랫폼·센서, 촉각 정보 처리, 강화학습 방법과 실험을 정리한다. 다른 연구 주제에 대한 적용안은 포함하지 않는다. `[원문 §…, PDF p.…]`는 첨부 출판본의 위치이며, **PDF 1–8쪽은 인쇄 페이지 5480–5487**에 대응한다. `[10]`과 같은 번호는 원문의 참고문헌 번호이고, 기존 조사본의 R 번호와 다르다. 수식의 해설·흐름 재구성은 원문에 근거한 설명이지 별도 구현·재현 결과가 아니다.

**핵심:** 이 논문은 별도 F/T 센서의 힘·토크를 제어하는 연구가 아니다. **TacTip 영상 또는 영상에서 추정한 접촉면 자세를 사용하여, 목표 방향 정렬과 접촉면에 수직인 pushing을 학습하는 연구**다. 실제 행동은 고정 전진 증분에 더하는 횡이동·회전 증분이다. 같은 과업에서 image-based SAC, pose-based SAC, pose-based PETS/MPC를 비교하고, 시뮬레이션에서 학습한 정책 또는 동역학 모델을 관측 변환 모델과 결합해 실물에 이전한다. [원문 §III, PDF pp. 2–5]

## 1. 제시하는 문제 상황

### 1.1 일반 물체 pushing이 어려운 이유

저자들은 평면 pushing에서도 물체·접촉 상태의 부분 관측성과 모델링하기 어려운 물리 때문에 범용적인 제어가 어렵다고 설명한다. 분석적 모델은 가정이 성립하는 범위에서 장점이 있지만, 물체와 마찰 조건이 달라지면 적용이 제한될 수 있다. 데이터 기반 모델은 이를 보완할 수 있으나 많은 실제 pushing 데이터가 필요하고 새로운 상황에 일반화하지 못할 수 있다. [원문 §I, PDF p. 1]

기존 deep RL 기반 pushing의 상당수는 카메라 영상을 직접 정책에 넣거나, 시각에서 얻은 물체 중심 상태를 사용한다. 이 경우 가림과 시각 측정 정확도 문제가 남는다. 반면 촉각은 물체와 실제로 상호작용하는 접촉 영역의 정보를 제공하므로, 정밀한 접촉 제어와 새로운 물체에 대한 일반화에 유용할 수 있다는 것이 이 연구의 출발점이다. [원문 §I, PDF pp. 1–2]

### 1.2 정해진 짧은 waypoint 추종에서 먼 단일 목표 도달로

저자들이 비교하는 기존 tactile RL 연구 [11], [12]는 짧은 간격의 목표점으로 구성된 미리 정해진 경로를 따라 물체를 밀었다. 본 논문은 **작업 영역 안에 임의로 배치된 먼 목표점까지 한 번에 가는 goal-conditioned pushing**을 다룬다. 따라서 정책이나 planner가 목표까지의 이동 경로를 정해야 하며, 경로를 미세 waypoint로 미리 제공받는 문제와 다르다. [원문 §I, PDF p. 2]

다만 ‘임의 목표’는 무제한 공간의 모든 목표가 아니다. 작업 영역, 초기 접촉, 행동 범위가 정해져 있고, 가까운 목표 중 일부는 이 행동 제약으로 도달하기 어렵거나 불가능할 수 있음을 저자들이 인정한다. [원문 §III-B-2, §III-B-4, §V, PDF pp. 3–4, 7–8]

### 1.3 물체 중심 대신 접촉면의 자세를 제어 대상으로 선택

촉각만으로는 물체 중심과 전체 형상·물성을 명시적으로 얻기 어렵다. 이에 저자들은 물체 중심의 상태를 복원하는 대신, **pusher에 대한 물체 접촉면의 자세를 조절하는 문제**로 과업을 구성한다. 지속적인 접촉을 유지하고, pusher가 접촉면에 수직에 가깝게 밀도록 유도하면서 접촉 위치를 목표로 이동시킨다. [원문 §III-B, PDF p. 3]

따라서 논문의 성공 판정은 **접촉 위치가 목표에 도달했는가**이며, 물체 중심이 정확히 목표점에 도달하거나 물체 전체의 최종 orientation이 지정값과 일치하는지를 판정하는 것은 아니다. [원문 §III-B-4, Fig. 6, PDF pp. 4, 6]

### 1.4 저자들이 제시한 기여

원문은 세 가지 기여를 명시한다. 첫째는 먼 목표에 도달하는 goal-conditioned tactile pushing 정식화, 둘째는 tactile pose 관측을 위한 sim-to-real pipeline과 그 표현의 장점, 셋째는 model-free 정책과 model-based online planner의 미지 물체·목표·외란에 대한 비교다. [원문 §I, PDF p. 2]

이 중 핵심 비교는 ‘어느 RL이 무조건 우수한가’가 아니라, **관측 표현, 학습 샘플 수, 최종 보상, 새로운 물체에서의 성공률, 실물 외란 조건의 경로가 어떻게 달라지는가**다. 실험별로 서로 다른 방법이 유리한 결과를 그대로 구분해야 한다. [원문 §IV–V, PDF pp. 5–8]

## 2. Related Work — 원문이 설정한 비교 구도

원문은 독립적인 **§II. Related Work**를 두며, §I에서도 촉각 pushing 선행연구와 문제 차이를 설명한다. 아래는 저자들이 선행연구를 소개한 범위를 정리한 것이며, 인용된 논문들을 별도로 정독해 검증한 결과는 아니다.

### 2.1 분석적 모델과 촉각 pushing의 출발점

Mason [15]의 voting theorem은 미는 물체의 회전 방향을 판단하는 기초로 소개된다. Lynch 등 [9]은 limit surface 개념을 이용해 촉각 피드백만으로 물체를 이동·회전시키는 연구로 소개된다. 본 논문은 이 계열이 촉각만으로 조작할 수 있음을 보여 주었다는 점을 인정하면서도, 복잡한 비선형 접촉에서 분석적 가정이나 직접 설계한 제어기의 제한이 남는다고 본다. [원문 §I–II, PDF pp. 1–2]

### 2.2 학습된 동역학 모델과 MPC

| 원문 인용 | 원문에서 설명하는 접근 | 본 논문이 주목하는 비교점 |
| --- | --- | --- |
| Kloss 등 [3], Ajay 등 [16] | 분석적 모델과 신경망을 결합하고 MIT Push Dataset을 이용 | 순수 분석 모델의 한계를 데이터로 보완 |
| Bauza 등 [2], Arruda 등 [17] | 실제 pushing 데이터로 Gaussian Process 모델을 학습 | 예측 모델을 이용한 제어·계획 |
| Cong 등 [18] | Domain randomization이 있는 시뮬레이션에서 expert policy가 생성한 데이터로 LSTM 동역학 모델 학습 | 시뮬레이션 학습과 모델 기반 일반화 |
| Manuelli 등 [7] | 물체 keypoint와 작은 무작위 상호작용 데이터셋을 이용한 시각 기반 동역학 모델 | 저차원 상태 표현과 미래 예측 |
| Hogan와 Rodriguez [1] | 복잡한 접촉 동역학을 다루는 MPC 관련 기반 | 모델로 미래 행동 결과를 평가 |

[원문 §II, PDF p. 2]

본 논문의 model-based 접근도 미래 상태 예측에 기반하지만, 입력 상태를 **촉각 접촉면 자세와 로봇 상태에서 구성**하고, 시뮬레이션에서 학습한 모델을 실물에서 online planning에 사용한다. 별도의 물체 중심 시각 추적을 planner의 입력으로 사용하는 구조로 설명하지 않는다. [원문 §III-A–C, Fig. 2, PDF pp. 3–5]

### 2.3 직접 피드백 제어와 model-free RL

Krivic와 Piater [8]의 모바일 pushing은 adaptive feedforward/feedback controller를 사용하지만 시각 측정의 정확도에 의존하는 사례다. Lloyd와 Lepora [10]는 촉각과 고유감각을 이용한 안정적인 goal-driven pushing 사례지만, 목표에 매우 가까워질 때의 복잡한 거동에서 한계가 있는 것으로 소개된다. [원문 §I–II, PDF pp. 1–2]

이후 원문은 pushing이 deep RL의 대표적인 조작 benchmark가 되었음을 설명하며 [19], 시각 기반 RL 연구 [20]–[22]가 접촉 정보를 충분히 활용하지 않는다는 점을 지적한다. 여기서 Related Work의 ‘model-free control’은 전통 피드백 제어까지 넓게 다루는 설명이고, 본 논문의 **model-free RL 실험 알고리즘은 SAC**다. [원문 §II–III-A-1, PDF pp. 2–3]

### 2.4 촉각 표현과 sim-to-real

Dong 등 [23]의 tactile RL insertion은 촉각이 미지 형상에 대한 일반화에 유용할 수 있다는 배경이다. 광학식 촉각 시뮬레이션과 이전 연구 [24]–[28]은 실제 로봇 상호작용에만 의존하지 않고 학습할 수 있는 기반으로 소개된다. 본 논문이 실제로 사용하는 환경은 **Tactile Gym [11], [12]와 PyBullet**이다. [원문 §II, §III-C-1, PDF pp. 2, 4]

특히 Church 등 [11]의 real-to-sim image translation을 영상 기반 비교군에 사용하고, Lepora와 Lloyd [14]의 pose estimation 접근을 이용한 **PoseNet을 pose 기반 관측 이전에 사용**한다. 즉, 본 논문의 새로운 비교는 기존 촉각 시뮬레이션을 대체하는 새 센서 물리 모델이 아니라, **같은 pushing 과업에서 무엇을 관측으로 표현하고 어떻게 학습·이전할 것인가**에 가깝다. [원문 §III-C, PDF pp. 4–5]

## 3. 환경과 로봇·센서 상세 사양

### 3.1 로봇 플랫폼

| 항목 | 원문 명시 내용 | 해석상 구분 |
| --- | --- | --- |
| 로봇 | **Dobot MG400** desktop robot arm | 실제 실험 장비 |
| 축·자유도 | **4-axis, 4 DoF** | 6축 자세 제어 로봇으로 기술하지 않음 |
| 말단 회전 | **z축 주위 회전만 가능** | 평면 pushing의 yaw에 대응 |
| 최대 가반하중 | **750 g** | 밀 수 있는 물체의 최대 질량을 뜻하지 않음 |
| 최대 reach | **440 mm** | 아래에서 정의하는 과업 workspace와 구분 |
| 반복정밀도 | **±0.05 mm** | 원문 표현은 maximum repeatability. 절대 위치 정확도나 촉각 분해능과 구분 |
| 말단 구성 | TacTip을 수평 장착하여 sensor와 pusher로 사용 | 손가락 파지 대신 센서 자체로 접촉 |
| 과업 제어 | Pusher 좌표계의 position increment control | 센서에 수직인 힘을 직접 명령하지 않음 |
| 정책이 선택하는 행동 | 횡이동 증분과 yaw 증분 | 4개 로봇 자유도를 모두 독립 RL action으로 사용하는 것이 아님 |
| 관절 범위·최대 속도·가속도 | 미명시 | 제품명에서 외부 사양을 가져와 채우지 않음 |
| 실험 접촉 높이·플랫폼 전체 치수 | 수치 미명시 | 사진에서 길이를 추정하지 않음 |

[원문 §III-B-2, §III-D, Fig. 1, PDF pp. 1, 3, 5]

### 3.2 TacTip과 실제로 사용한 접촉 정보

| 항목 | 원문 확인 결과 |
| --- | --- |
| 센서명 | **TacTip** |
| 원리·형상 | 부드러운 반구형 광학식 촉각 센서. 감지면 아래 pin motion으로 접촉 정보를 제공 |
| Pin 수 | **331개** |
| 배치 | 로봇 말단에 수평 장착한 한 개의 tactile sensor/pusher |
| 영상 기반 경로의 정보 | 접촉에 따른 촉각 영상 |
| Pose 기반 경로의 정보 | 접촉 깊이와 각도 → Cartesian 접촉면 자세 |
| 별도 손목 F/T 센서 | 본 논문의 실험 구성과 제어 입력에 제시되지 않음 |
| Pin당 힘 출력 | 제시되지 않음. 331개를 독립적인 331축 힘 측정값으로 취급하지 않음 |
| 뉴턴·압력·모멘트 단위의 복원 | 제시되지 않음 |
| 최대 힘·압력·토크 측정 범위 | 미명시 |
| 힘 분해능·최소 검출 힘·감도 | 미명시 |
| 힘 측정 정확도·선형성·히스테리시스 | 미명시 |
| 공간 pitch·접촉 위치 분해능 | 미명시. Pin 수만으로 환산하지 않음 |
| 촬영 해상도·모델 입력 영상 크기 | 본 논문에 수치 미명시 |
| 촉각 카메라 frame rate·센서 대역폭 | 미명시 |
| Tip 직경·재료 경도·두께 | 본 논문에 수치 미명시 |
| Force threshold·과부하 제한 | 정량적인 force 기반 판정·제한이 제시되지 않음 |

[원문 §I, §III-C–D, Table I, Fig. 1–3, PDF pp. 2, 4–5]

**Table I의 pose sampling 범위와 validation accuracy는 센서의 최대 측정 범위·분해능이 아니다.** 이 논문에서 직접 보고하지 않은 TacTip 사양을 같은 센서명을 사용하는 다른 논문의 값으로 보충하지 않았다.

### 3.3 고유감각과 외부 카메라의 역할

Fig. 2(a)는 촉각 정보에 **proprioceptive states와 goal states**를 결합하는 구조를 보여 준다. 로봇 자신의 상태를 이용해 접촉면·목표의 상대 표현을 구성하는 것이며, 촉각만으로 전역 좌표계 전체를 새로 복원하는 것은 아니다. 정확한 로봇 상태 취득 API, 좌표 변환 구현, 동기화 주기는 원문에 없다. [원문 식 (3), Fig. 2, PDF pp. 3–4]

실물에서는 물체 위에 **ArUco marker**를 붙여 궤적을 검증한다. Fig. 7의 파란 점은 이 방식으로 추적한 **물체 중심**이고, RL 과업의 목표 도달 판단에 쓰는 **접촉 위치**와 다르다. 카메라가 실험실에 존재하지 않는다는 뜻으로 ‘without visual input’을 읽으면 안 된다. 원문은 ArUco를 trajectory validation 용도로 설명하고, 정책·planner의 관측식에는 이 물체 중심 추적값을 넣지 않는다. [원문 §III-D, Fig. 7 caption, PDF pp. 5, 7]

### 3.4 시간 특성과 소프트웨어

| 항목 | 원문에 있는 내용 | 없는 내용 |
| --- | --- | --- |
| 물리 시뮬레이션 | Tactile Gym의 **PyBullet rigid-body physics** | timestep, solver 설정 수치, 버전·커밋 |
| 물성 설정 | 원래 Tactile Gym의 default physics parameters | 마찰·접촉 강성·감쇠의 수치 |
| Model-free 학습 | **SAC**, **stable-baselines3** | 라이브러리 버전, 상세 runner·network 설정 |
| Model-based 학습 | **PETS**, **MBRL-LIB** | ensemble 수, hidden layer, update schedule 수치 |
| MPC optimizer | CEM과 MPPI를 시험했으며 CEM이 더 좋았다고 보고 | 비교 수치, horizon, candidate·elite 수 |
| 실제 제어·추론 | Position increment를 반복 실행 | action 주기, 카메라 주기, planner latency, 통신 지연 |
| 계산 장비·시간 | 정량 사양 미명시 | CPU/GPU, wall-clock 학습 시간, 초당 planning 횟수 |

[원문 §III-A–D, PDF pp. 2–5]

따라서 **1 mm/action을 1 mm/s로 환산하지 않는다.** 샘플 효율과 실제 계산 시간도 별개다. 이후의 25k·2.8m·3.2m 수치는 Table II의 학습 샘플 지표이지 초·분 단위의 실행 시간이나 센서 샘플링률이 아니다.

## 4. Task formulation — 무엇을 받고 무엇을 움직이는가

### 4.1 목표·초기조건·학습 환경

| 항목 | 원문 설정 |
| --- | --- |
| 과업 | 초기 접촉에서 시작해 미지 물체를 지정된 목표 위치로 pushing |
| 평면 workspace | x: **[0, 400] mm**, y: **[−300, 300] mm** |
| 학습 목표 분포 | Workspace 경계 부근에서 균일하게 샘플링 |
| 목표 유지 | Episode 시작 시 샘플링하고 해당 episode 동안 고정 |
| 초기 상태 | 원점의 **stable push configuration에서 물체와 이미 접촉** |
| RL 학습 물체 | 단일 cube |
| Cube 크기 | §III-C-1은 edge 75 mm, Fig. 5는 80 × 80 × 80 mm로 표시. 두 표기는 §9에서 별도 기록 |
| Domain randomization | 사용하지 않음 |
| 다양한 물체 curriculum | 사용하지 않음 |
| 성공·종료 | **접촉 위치가 목표에서 25 mm 이내** |
| Episode 최대 step·timeout | 수치 미명시 |
| 접촉 소실·workspace 이탈의 상세 종료 조건 | 명시적인 식·threshold 미제시 |

[원문 §III-A-1, §III-B-4, §III-C-1, Fig. 3, PDF pp. 3–5]

학습 목표를 경계 부근에서 뽑는 이유는 시작점에 너무 가까워 도달이 어려운 목표를 피하고 workspace를 충분히 탐색하게 하기 위해서다. 평가에서는 더 넓은 목표 집합을 사용한다. 다만 ‘경계 부근’의 정확한 띠 너비와 모든 좌표를 수치로 나열하지는 않는다. Fig. 3의 도식만으로 이를 임의의 sampling code로 확정하지 않는다. [원문 §III-B-4, PDF p. 4]

### 4.2 행동 공간: 전진은 고정, 횡이동과 회전을 선택

본문의 action 정의를 모으면 다음과 같다.

$$
a_t=(\Delta y_t,\Delta\theta_t),\qquad
\Delta y_t\in[-1,1]\ \mathrm{mm},\qquad
\Delta\theta_t\in[-1,1]^{\circ}.
$$

$$
\Delta x_t=1\ \mathrm{mm}.
$$

모두 **pusher의 좌표계에서 한 time step에 적용하는 위치·회전 증분**이다. 로봇은 매 step 전진하고, 정책 또는 planner가 전진 중 옆으로 얼마나 이동하고 yaw를 얼마나 바꿀지 결정한다. [원문 §III-B-2, PDF p. 3]

저자들의 의도는 행동 차원을 줄이고 전진 접촉을 유지하기 쉽게 만드는 것이다. 반대로 행동의 자유도가 줄어 가까운 목표로 급격히 방향을 바꾸거나 접촉면을 따라 자유롭게 탐색하는 능력은 제한된다. 고정 전진은 force feedback으로 계산되는 값이 아니고, 실제 물체의 전진 변위를 보장하는 값도 아니다. [원문 §III-B-2, §V, PDF pp. 3, 7–8]

### 4.3 관측식의 o는 물체 중심이 아니다

원문은 위첨자 a와 아래첨자 b를 이용한 상대 상태를 설명한다. p는 pusher, o는 **object contact surface**, g는 goal이다. 위첨자가 없는 값은 해당 변수의 비상대 값이다. 이 구분을 유지해야 S2·S3의 좌표를 전체 물체 pose나 CAD 모델 상태로 오해하지 않는다. [원문 §III-B-1, PDF p. 3]

**원문 식 (3)**

$$
\begin{aligned}
S_1&=[I_{\mathrm{tactile}},x_g^p,y_g^p,\theta_g^p],\\
S_2&=[x_o^p,y_o^p,\theta_o^p,x_g^o,y_g^o,\theta_g^o],\\
S_3&=[x_o^p,y_o^p,\theta_o^p,x_o,y_o,\theta_o].
\end{aligned}
$$

| 관측 | 사용 주체 | 구성과 의미 |
| --- | --- | --- |
| **S1** | Tactile-image SAC | 촉각 이미지와 pusher에 대한 goal의 상대 위치·각도 |
| **S2** | Tactile-pose SAC | Pusher에 대한 접촉면의 상대 pose 3개와, 접촉면에 대한 goal의 상대 상태 3개 |
| **S3** | Tactile-pose PETS 동역학 모델 | 접촉면의 pusher-relative pose 3개와 비상대 contact pose 3개. Goal은 planning의 reward 평가에 별도로 사용 |

[원문 식 (3), Fig. 2(a), PDF pp. 3–4]

S2와 S3는 식상 각각 여섯 scalar다. 그러나 **PoseNet이 서로 독립인 접촉 변수 여섯 개를 영상에서 추정한다는 뜻은 아니다.** PoseNet의 직접 출력은 2D 접촉 깊이·각도이고, 이후 Cartesian 변환과 로봇·목표 상태 결합으로 관측을 구성한다. S1과 S2는 촉각 표현뿐 아니라 goal을 표현하는 기준도 다르다. [원문 §III-B-1, §III-C-2, PDF pp. 3, 5]

## 5. 힘·촉각 정보 처리 — 원신호에서 제어 입력까지

### 5.1 센서의 물리적 변형을 무엇으로 읽는가

접촉으로 TacTip 감지면 아래의 pin들이 움직이고, 광학식 센서의 영상에 이 변화가 나타난다. 논문은 이 영상을 바로 힘·토크 벡터로 복원하지 않는다. 대신 다음 두 표현을 비교한다. [원문 §I, §III-B-1, §III-C-2, PDF pp. 2–5]

```text
실제 TacTip 영상
  ├─ Real-to-sim GAN → 시뮬레이션과 같은 영상 표현 → S1 → SAC
  └─ PoseNet → 접촉 깊이·각도 → Cartesian 접촉면 자세
                 ├─ 상대 goal 결합 → S2 → SAC
                 └─ contact state 구성 → S3 → PETS 동역학 모델 + MPC
```

이 분기는 **전처리 모델과 RL 알고리즘의 역할을 분리**한다. GAN/PoseNet은 촉각 관측을 변환하고, SAC나 MPC가 실제 pushing action을 정한다. 접촉면 각도의 오차를 고정된 비례 gain에 곱해 바로 행동으로 만드는 제어기를 제시하는 것은 아니다. [원문 Fig. 2, §III, PDF pp. 2–5]

### 5.2 시뮬레이션에서 촉각 관측을 생성하는 방법

Tactile Gym은 PyBullet로 rigid-body physics를 시뮬레이션한다. Image-based 관측은 **시뮬레이션 센서의 렌더링된 depth image**를 사용한다. Pose-based 관측은 **근사 센서와 물체 사이의 접촉 정보로 contact surface pose를 추론**한다. [원문 §III-C-1, PDF p. 4]

즉, 시뮬레이션에서도 반드시 실제 TacTip의 모든 내부 pin과 부드러운 피부 변형을 정밀하게 재현한 다음 PoseNet을 적용하는 구조는 아니다. 원문은 depth image와 접촉 기하를 이용하는 경로를 설명한다. 시뮬레이션 관측을 실물에서 얻을 수 있게 만드는 역할은 다음의 observation model이 담당한다. 세부 접촉점 선택·depth rendering·여러 접촉점 집계 규칙은 이 논문에 제시되지 않는다. [원문 §III-C-1–2, Fig. 2(b), PDF pp. 4–5]

### 5.3 Image-based 경로: Real-to-Sim GAN

실제 TacTip 영상과 시뮬레이션 depth image는 외형이 다르다. 영상 기반 정책이 실물에서도 학습 시와 같은 종류의 입력을 받을 수 있도록, **실제 영상에서 시뮬레이션 영상으로 변환하는 GAN**을 학습한다. 방향은 sim-to-real image generation이 아니라 **real-to-sim image translation**이다. [원문 §III-C-2, PDF p. 5]

Generator는 **pix2pix의 U-net 구조**, discriminator는 **일반 CNN**이다. 시뮬레이션과 실물에서 동일한 데이터 수집 절차를 수행하여 실제·시뮬레이션 영상의 대응 쌍을 만들고, 이를 이용해 supervised image-to-image translation을 학습한다. 상세 방법은 원문 [11]을 참조하도록 되어 있다. [원문 §III-C-2, PDF p. 5]

이 경로에서는 RL이 접촉 관련 특징을 영상에서 학습한다. GAN이 명시적인 접촉력이나 마찰계수를 출력하는 것은 아니다. 본 논문은 U-net의 채널 수, discriminator 층 수, 이미지 크기, loss 항의 계수, 영상 정규화·필터링 세부 설정을 직접 제시하지 않는다. 다른 논문의 구현을 이 실험의 확정 설정으로 대입할 수 없다. [원문 §III-C-2의 확인 범위, PDF p. 5]

### 5.4 Pose-based 경로: PoseNet

PoseNet은 **실제 촉각 영상에서 물체 표면과 센서 사이의 상대 접촉 pose를 추정하는 CNN**이다. 본 논문이 다루는 2D 표면에서는 접촉 pose를 **깊이와 각도, 즉 polar-coordinate 표현**으로 설명한다. 이 값을 Cartesian coordinates로 바꾸어 식 (3)의 tactile pose 성분으로 사용한다. [원문 §III-C-2, PDF p. 5]

| 처리 단계 | 입력·출력 | 기능 |
| --- | --- | --- |
| 표면 접촉 데이터 수집 | 고정된 평면 자극과 여러 센서 pose | 접촉 영상과 알려진 pose의 대응 확보 |
| Label 구성 | 고정 contact surface에 대한 robot pose | CNN의 supervised pose label |
| PoseNet 추론 | 실제 촉각 영상 → 접촉 깊이·각도 | 영상 변형을 접촉 기하로 압축 |
| 좌표 표현 변환 | Polar → Cartesian | Relative contact pose 구성 |
| 로봇·goal 상태 결합 | 접촉면 pose와 고유감각·goal | S2 또는 S3 구성 |
| 행동 결정 | S2 → 정책, 또는 S3 → 모델·planner | 횡이동·회전 증분 선택 |

[원문 §III-B-1, §III-C-2, Fig. 2, PDF pp. 3–5]

PoseNet의 출력은 **표면의 어느 방향에 어느 깊이로 접촉해 있는가**를 나타낸다. 물체 중심, COF, 질량, 마찰, 전단력, 손목 wrench를 출력하는 구조가 아니다. 또한 본 논문에는 이 PoseNet 출력에 Bayesian filter를 추가하거나, 별도 uncertainty를 함께 예측하는 처리 단계가 제시되지 않는다. [원문 §III-C-2, PDF p. 5]

Cartesian 변환의 구체식, 센서 중심·표면 원점의 정의, 반경 보정, 각도 부호, 통신·관측 필터는 원문 [14], [35]를 참조하는 수준이며 본문에서 완전히 전개하지 않는다. 따라서 여기서는 **깊이·각도 → 접촉면 상대 pose**라는 연결까지만 원문 확인 사실로 기록하고, 누락된 수치나 식을 채우지 않는다.

### 5.5 Observation model의 데이터 수집과 성능

두 observation model 모두 **고정된 3D-printed stimulus의 평면**에 센서를 무작위로 샘플링한 pose로 접촉시키면서 영상과 label을 수집한다. 동일한 pose sampling 범위를 사용해 서로 대응하는 접촉 특징을 다루지만, 학습·검증 표본 수는 다르다. [원문 §III-C-2, Table I, PDF p. 5]

**Table I — 원문 표기 유지**

| 항목 | Tactile GAN | PoseNet |
| --- | --- | --- |
| Depth range (mm) | **[−1, −5]** | **[−1, −5]** |
| Angle range (deg) | **[−30, 30]** | **[−30, 30]** |
| Train samples | **5,000** | **1,476** |
| Validation samples | **2,000** | **524** |
| Validation accuracy | **SSIM: 0.99** | **[±0.05 mm, ±0.6 deg]** |

[원문 Table I, PDF p. 5 / 인쇄 p. 5484]

깊이는 표에 실제로 **[−1, −5]** 순서로 적혀 있다. 이를 정렬된 수학적 구간이나 양의 깊이 [1, 5]로 조용히 바꾸지 않는다. 부호와 원점의 세부 정의를 추가 확인하지 않았으므로 원문 수치 표기를 유지한다.

또한 다음을 구분해야 한다. **SSIM 0.99는 변환 이미지의 검증 지표**, **±0.05 mm·±0.6 deg는 PoseNet의 validation accuracy 표기**다. 두 지표는 같은 물리량이 아니고, 해당 ±가 표준편차·신뢰구간·최대오차 중 무엇인지는 원문 표에서 정의하지 않는다. 이 수치를 센서의 물리적 분해능이나 미지 물체 pushing 중의 보장 오차로 바꾸어 기록하지 않는다. [원문 Table I, PDF p. 5]

### 5.6 ‘시뮬레이션 학습’과 ‘실제 데이터 없음’은 다르다

RL 정책과 동역학 모델은 시뮬레이션에서 학습하지만, **관측 변환 모델은 실제 촉각 데이터를 포함한 supervised learning으로 준비**한다. 따라서 zero-shot transfer는 ‘실제 촉각 데이터가 한 장도 필요 없다’는 의미가 아니다. 학습된 observation model을 붙인 뒤 **실물 pushing으로 RL 정책이나 동역학 모델을 추가 학습하지 않고** 실행한다는 범위로 이해해야 한다. [원문 §III-C, §V, PDF pp. 4–5, 7]

### 5.7 접촉 정보가 행동에 영향을 주는 구체적인 경로

접촉면 자세는 두 곳에서 작동한다. 첫째, 현재 상태 표현으로 policy 또는 dynamics model에 들어간다. 둘째, reward에서 **pusher와 접촉면의 정렬 상태 및 접촉면과 목표 방향의 정렬 상태**를 평가한다. 따라서 촉각의 역할은 단순히 입력 채널을 추가하는 것이 아니라, **어떤 행동이 안정적인 pushing인지 정의하는 학습 신호와 행동 선택의 상태 표현을 함께 제공**하는 데 있다. [원문 §III-B-1–3, PDF pp. 3–4]

Model-free에서는 이 보상의 영향을 학습 과정에서 정책 가중치에 반영한다. Model-based에서는 후보 행동이 만들 접촉 상태를 예측하고 같은 reward를 online으로 평가한다. 두 경로 모두 실행 중 새 촉각을 다시 받지만, 현재 관측에서 행동을 선택하는 계산 구조는 다르다. [원문 §III-A, Fig. 2, PDF pp. 2–4]

**원문이 제시하지 않는 연결:** 힘 크기 추정 → 목표 힘 추종, force threshold → 정지, slip classifier → 접촉 모드 전환, wrench → admittance 또는 stiffness 조절. 본 논문의 정보 활용을 이런 방식으로 바꾸어 설명하면 안 된다.

## 6. Reward shaping — 접촉 기하를 학습 목표로 만드는 방법

### 6.1 Sparse reward와 단순 거리 reward의 문제

저자들은 먼 목표까지 가는 과업에서 sparse reward는 탐색이 어렵고 planning에도 효과적이지 않다고 설명한다. 목표까지의 거리만 줄이는 dense reward 역시 물체를 먼저 회전시키기 위해 잠시 목표에서 멀어져야 하는 경우에 local optimum을 만들 수 있다. 그래서 멀리 있을 때와 가까이 있을 때의 목표 항을 다르게 두고, 공통으로 contact-normality 항을 추가한다. [원문 §III-B-3, PDF pp. 3–4]

### 6.2 Reward에 사용하는 변수

| 기호 | 원문에서의 의미 |
| --- | --- |
| $o_{xy}$ | 물체 접촉 위치의 평면 좌표 |
| $g_{xy}$ | 목표 위치 |
| $o_\theta$ | Contact surface orientation |
| $p_\theta$ | Pusher orientation |
| $g_\theta$ | 접촉 위치에서 목표를 향하는 desired contact orientation, 즉 goal-bearing angle |
| $f(a,b)$ | Euclidean distance |
| $g(a,b)$ | Cosine distance |
| $d$ | Approaching zone 경계, **100 mm** |

[원문 §III-B-3, 식 (4), PDF pp. 3–4]

기호 g는 goal, goal-bearing angle의 일부 표기, cosine-distance 함수에 중복 사용된다. 아래 식은 원문 표기를 유지한다. 원문은 bearing을 $g_\theta=\mathrm{atan2}(o_{xy},g_{xy})$로 적는데, 두 위치 벡터에서 방향각을 구한다는 의미이며 성분별 구현식은 풀어 쓰지 않는다. 이를 일반 프로그래밍 API의 scalar 인수 두 개와 동일한 완전한 구현 정의로 취급하지 않는다. [원문 §III-B-3, PDF p. 3]

### 6.3 멀리 있을 때는 방향, 가까이 있을 때는 거리

**원문 식 (4)**

$$
r=
\begin{cases}
-\bigl(g(o_\theta,g_\theta)+g(p_\theta,o_\theta)\bigr),
&\lVert o_{xy}-g_{xy}\rVert>d,\\
-\bigl(f(o_{xy},g_{xy})+g(p_\theta,o_\theta)\bigr),
&\lVert o_{xy}-g_{xy}\rVert\le d.
\end{cases}
$$

**먼 구간:** 접촉면 방향을 목표 bearing과 맞추는 항을 사용한다. 전진이 고정되어 있으므로, 목표로 향하는 접촉 방향을 만들면 목표 쪽으로 진행할 수 있다는 설계다. 이 구간의 식에는 목표 Euclidean distance를 직접 줄이는 항이 없다. [원문 §III-B-3, PDF p. 4]

**가까운 구간:** 목표 가까이에서는 bearing 기반 reward가 바람직하지 않은 거동을 만들었다고 보고한다. 이에 100 mm 안에서는 방향 항을 접촉 위치–목표 위치의 Euclidean distance로 교체한다. **100 mm는 목표 도달 허용 오차 25 mm가 아니라 reward 전환 경계**다. [원문 §III-B-3–4, PDF p. 4]

원문은 Euclidean·cosine distance의 함수명과 역할을 제시하지만, 거리 단위의 정규화, cosine distance의 상세 구현, 두 종류 항 사이의 scale 처리를 수치로 설명하지 않는다. 본 문서에서도 임의의 weight나 표준 라이브러리 정의를 추가하지 않는다.

### 6.4 두 구간 모두 유지하는 contact-normality 항

두 reward에 공통인 $g(p_\theta,o_\theta)$는 **pusher가 접촉면에 수직인 방향으로 밀도록** 유도한다. 저자들은 이 항이 성공적인 학습에 중요했다고 보고하며, 마찰 중심 **COF**(center of friction)를 통과하는 pushing을 유도한다는 설명을 제시한다. [원문 §III-B-3, PDF p. 4]

원문이 설명하는 효과는 세 가지다. 큰 goal-bearing angle에서 무리하게 방향을 바꾸다 접촉을 잃는 것을 줄이고, normality가 유지되면 접촉점의 목표 방향 진행이 COF의 진행과도 연결되며, 안정된 pushing은 동역학 학습과 장기 예측의 오차 누적을 완화해 planning에도 유리하다는 것이다. [원문 §III-B-3, PDF p. 4]

다만 **COF를 센서로 직접 측정하거나, 관측식에 COF 좌표를 넣거나, 이를 별도 상태로 추정하는 모듈은 없다.** 위 내용은 저자들의 reward 설계 근거다. 임의 형상·마찰에서 normality만으로 항상 COF를 통과한다는 일반 정리를 증명한 것으로 확대하지 않는다. [원문 식 (3)–(4), §III-B-3, §V, PDF pp. 3–4, 7]

### 6.5 접촉 유지의 soft 유도와 hard 보장은 다르다

접촉 유지는 **고정 전진 action과 normality reward**를 통해 유도한다. 원문은 reward 구성요소가 빠지면 pushing이 불안정해지고 학습에 실패했다고 서술하지만, 구성요소별 ablation 수치를 별도 표로 제공하지 않는다. [원문 §III-B-2–3, PDF pp. 3–4]

따라서 contact 유지가 hard constraint로 강제되거나 성공이 이론적으로 보장되는 것은 아니다. 실제 평가에는 contact loss 사례가 있다. 또한 이 reward에는 뉴턴 단위 힘 제한, 모멘트 제한, 에너지 비용, 물체 전도 지표가 명시적으로 들어 있지 않다. 접촉면 정렬을 힘 제어 또는 전도 방지 보상으로 바꾸어 부르지 않는다. [원문 식 (4), §IV-C, PDF pp. 4, 6–7]

## 7. 상세 학습·행동 결정 메소드

### 7.1 공통 goal-conditioned 정식화

원문은 과업을 continuous state·action, 확률적 state transition, finite horizon을 갖는 **MDP**로 정식화한다. Goal은 episode 시작에 샘플링하고 episode 안에서는 유지한다. [원문 §III-A, PDF pp. 2–3]

**원문 식 (1)**

$$
\pi_\theta^{\ast}
=\underset{\pi}{\mathrm{arg\,max}}\;
\mathbb{E}_{\tau\sim p_\pi(\tau),\,g\sim q(g)}
\left[\sum_{t=0}^{T}\gamma^t r(s_t,a_t,g)\right].
$$

$p_\pi(\tau)$는 정책에 따른 episode 분포, $q(g)$는 goal 분포이고, discount factor는 $\gamma\in[0,1)$이다. 원문은 정확한 gamma 값과 T의 수치를 제시하지 않는다. [원문 식 (1), PDF pp. 2–3]

Introduction은 시스템의 partial observability를 문제로 든다. 그러나 Method는 MDP 형식으로 설명하고, 별도의 belief state·RNN·observation history 설계를 제시하지 않는다. 따라서 본 정리도 이를 POMDP 전용 알고리즘이나 recurrent policy로 바꾸어 설명하지 않는다. [원문 §I, §III-A–B, PDF pp. 1–3]

### 7.2 Model-free RL: 두 관측 표현을 각각 SAC로 학습

Model-free 방법은 **off-policy Soft Actor-Critic**(SAC)이며 stable-baselines3 구현을 사용한다. S1과 S2에 대해 각각 정책을 학습한다. 학습된 정책은 goal-aware 관측에서 action을 직접 출력하고, 실행 중에는 후보 행동열을 dynamics model로 rollout하는 planning 단계가 없다. [원문 §III-A-1, §III-B-1, Fig. 2(a), PDF pp. 2–4]

```text
시뮬레이션 학습
  S1 또는 S2 + goal-conditioned reward → SAC 정책 학습

실물 실행
  TacTip 영상 → GAN 또는 PoseNet → goal-aware 관측
  → 학습된 SAC 정책 → 횡이동·회전 증분 + 고정 전진 증분
```

이 도식은 원문 설명을 재구성한 것이며, 원문에 별도 Algorithm 번호는 없다.

원문 식 (1)은 일반적인 discounted return을 제시한다. SAC의 구체적인 actor·critic loss, entropy coefficient·target entropy, replay buffer 크기, batch size, network layer, optimizer learning rate는 이 논문 본문에 전개되어 있지 않다. ‘SAC를 사용했다’는 사실을 근거로 특정 버전의 기본 설정을 실제 사용값으로 채우지 않는다. [원문 §III-A-1의 확인 범위, PDF pp. 2–3]

### 7.3 Model-based RL: 접촉 상태 변화의 확률적 ensemble 모델

Model-based 방법은 **PETS**(Probabilistic Ensemble Trajectory Sampling)이며 MBRL-LIB 구현을 사용한다. Probabilistic ensemble neural networks로 transition을 근사하고, 평균과 diagonal covariance를 갖는 Gaussian을 출력한다. [원문 §III-A-2, PDF p. 3]

**원문 본문의 모델 정의**

$$
f_\theta(s_t,a_t)
\equiv\mathcal{N}\bigl(\mu_\theta(s_t,a_t),\Sigma_\theta(s_t,a_t)\bigr).
$$

$$
\Delta s_t=s_{t+1}-s_t,\qquad
\Delta s_t\sim f_\theta(s_t,a_t).
$$

여기서 모델에 제공하는 state는 S3이며, action을 적용했을 때 **관측으로 표현한 contact state가 어떻게 변할지**를 예측한다. 물체 질량·마찰계수를 각각 물리 파라미터로 출력하는 identification 모델이나, 촉각 이미지 자체를 생성하는 GAN과는 역할이 다르다. [원문 §III-A-2, 식 (3), Fig. 2, PDF pp. 3–4]

원문은 transition 데이터셋을 다음과 같이 정의한다.

$$
\mathcal{D}=\{(s_t,a_t,s_{t+1})_{1,\ldots,N}\}.
$$

**원문 식 (2) — 표기 유지**

$$
\mathcal{L}_{\mathrm{NLL}}
=\sum_{n=1}^{N}
[s_{n+1}-\mu_\theta]^{\mathsf{T}}
\Sigma_\theta^{-1}
[s_{n+1}-\mu_\theta]
+\log\bigl(\det(\Sigma_\theta)\bigr).
$$

[원문 식 (2), PDF p. 3]

이 식의 설명상 역할은 예측 오차와 Gaussian covariance를 함께 고려하는 **one-step negative log-likelihood 학습**이다. 오차의 이차형식에는 inverse covariance가 들어가고, log-determinant 항도 포함된다. 원문에는 모델 입력 의존성과 표본별 표기가 축약되어 있다.

**표기상 주의:** 바로 앞 문장은 예측 대상을 $\Delta s_t$로 설명하지만 식 (2)의 잔차는 $s_{n+1}-\mu_\theta$로 적는다. 원문만으로 next-state mean과 state-difference mean의 구현 관계를 확정할 수 없으므로, 위 식을 조용히 고쳐 쓰지 않았다. 재현 시에는 실제 코드에서 target과 state 정규화·차분 처리를 확인해야 한다. [원문 §III-A-2, PDF p. 3]

### 7.4 MPC: 예측 결과의 reward로 행동열을 선택

학습한 모델은 **MPC framework**에서 사용한다. 현재 state에서 horizon H 동안의 행동열을 평가하여 누적 reward가 높은 행동열을 찾고, **첫 행동만 실행한 뒤 다음 관측에서 다시 계획**한다. [원문 §III-A-2, PDF p. 3]

원문에 번호 없이 제시된 planning 목적을 같은 의미로 정리하면 다음과 같다.

$$
\underset{a_{t:t+H}}{\mathrm{arg\,max}}\;
\mathbb{E}_{f}
\left[\sum_{k=t}^{t+H}r(s_k,a_k,g)\right].
$$

이 식은 저자들의 horizon reward 최대화를 나타낸다. 현재 tactile pose는 출발 state를 정하고, dynamics model은 후보 action 뒤의 접촉 상태를 예측하며, 식 (4)는 예측된 상태의 **목표 진행과 접촉 정렬**을 평가한다. 이 결과가 첫 횡이동·yaw 명령의 선택으로 이어진다. [원문 §III-A-2–B, Fig. 2(a), PDF pp. 3–4]

Optimizer로 **CEM**(cross-entropy method)과 **MPPI**(model-predictive path integral)를 시험했고, 이 과업에서는 CEM이 가장 좋았다고 보고한다. 다만 CEM의 sampling distribution·candidate 수·elite 비율·iteration 수, PETS의 ensemble 수·particle 수·trajectory sampling 세부, 실제 horizon과 계산 시간은 본문에 없다. 표준 PETS의 흔한 설정을 이 실험의 값으로 가져오지 않는다. [원문 §III-A-2, PDF p. 3]

### 7.5 학습 중 model update와 실물 online planning을 구분

**시뮬레이션 학습 중**에는 planner가 수행한 trajectory를 데이터로 저장하고 동역학 모델을 주기적으로 다시 학습한다. 개선된 모델이 다시 planner의 데이터 수집에 사용되므로 모델 학습과 데이터 수집이 교대로 진행된다. [원문 §III-A-2, PDF p. 3]

**실물 실행 중**에는 학습한 dynamics model을 이전하고 optimizer가 online으로 행동을 계획한다. 원문은 이를 zero-shot transfer로 설명하며, 실제 pushing 데이터를 수집해 동역학 network weights를 계속 갱신하는 온라인 학습을 제시하지 않는다. **Online replanning과 online model retraining은 다르다.** [원문 §III-C-3, §V, PDF pp. 5, 7]

### 7.6 세 실험 pipeline 비교

| 항목 | Model-free + tactile image | Model-free + tactile pose | Model-based + tactile pose |
| --- | --- | --- | --- |
| RL 알고리즘 | SAC | SAC | PETS |
| 입력 표현 | S1 | S2 | S3 + planner의 goal |
| 실물 observation model | Real-to-sim GAN | PoseNet | PoseNet |
| 시뮬레이션에서 학습하는 실행 핵심 | 정책 | 정책 | 확률적 동역학 모델 |
| 실행 중 action 선택 | 정책 forward pass | 정책 forward pass | 모델 예측 + MPC/CEM |
| Reward 사용 위치 | 정책 학습 | 정책 학습 | 학습 중 planning·데이터 수집 및 실행 중 planning |
| 고정 전진 | 1 mm/step | 1 mm/step | 1 mm/step |
| 선택 action | 횡이동·yaw 증분 | 횡이동·yaw 증분 | 횡이동·yaw 증분 |
| 실물 RL 추가 학습 | 제시하지 않음 | 제시하지 않음 | 제시하지 않음. 재계획은 수행 |

[원문 §III, Fig. 2, PDF pp. 2–5]

## 8. 실험 조건과 결과

### 8.1 시뮬레이션 학습: 샘플 효율과 최종 보상

**Table II — 각 방법의 best reward 10% 이내에 도달하는 training samples와 final best reward**

| 방법 | Samples | Best reward |
| --- | --- | --- |
| Model-free + tactile image | **3.2m = 3,200,000** | **−124.86** |
| Model-free + tactile pose | **2.8m = 2,800,000** | **−122.85** |
| Model-based + tactile pose | **25k = 25,000** | **−144.70** |

[원문 Table II, Fig. 4, §IV-A, PDF p. 5]

저자들은 model-based 방법이 약 100배 적은 samples를 필요로 했다고 설명한다. 표의 숫자를 직접 나누면 image SAC 대비 128배, pose SAC 대비 112배이며, 이는 **표에 제시된 기준의 비율**이다. 세 방법이 정확히 같은 reward 수준에 도달하는 데 걸린 시간이나, 최종 학습 전체에 사용한 샘플 수를 비교한 것으로 바꾸어 해석하지 않는다. Fig. 4는 Table II의 해당 지점 이후까지 학습 곡선을 제시한다.

최종 best reward는 model-free 두 방법이 높고, 그중 pose SAC가 가장 높다. Pose SAC는 image SAC보다 이 표의 학습 샘플 지표도 작다. 따라서 이 실험에서는 **빠른 sample efficiency는 model-based, 더 많은 학습 후의 높은 최종 reward는 model-free**라는 구분이 필요하다. [원문 §IV-A, PDF p. 5]

### 8.2 학습·평가 물체의 질량과 치수

다음은 **Fig. 5에 인쇄된 질량·치수**를 그대로 옮긴 것이다. 그림은 simulation train/test objects를 설명하며, 일상 물체는 YCB Object Set [36]에서 가져왔다. 두 수치로만 표시된 원형 물체 등의 치수는 도면에 축·직경·높이 순서를 별도로 정의하지 않으므로 원문 표기 순서를 유지한다.

| 물체 | 용도 | 질량 | Fig. 5의 치수 표기 |
| --- | --- | --- | --- |
| Cube | Train, 이후 평가에도 사용 | **491 g** | **80 × 80 × 80 mm** |
| Cylinder | 미학습 test object | **200 g** | **80 × 100 mm** |
| Hexagonal prism | 미학습 test object | **80 g** | **86.5 × 100 mm** |
| Gelatin box | 미학습 test object | **97 g** | **28 × 85 × 90 mm** |
| Master chef can | 미학습 test object | **431 g** | **102 × 139 mm** |
| Mug | 미학습 test object | **118 g** | **80 × 82 mm** |
| Potted meat can | 미학습 test object | **370 g** | **50 × 97 × 82 mm** |
| Chip can | 미학습 test object | **205 g** | **75 × 250 mm** |
| Rubiks cube | 미학습 test object | **290 g** | **60 × 60 × 60 mm** |
| Tomato soup can | 미학습 test object | **349 g** | **66 × 101 mm** |

[원문 Fig. 5, PDF p. 5 / 인쇄 p. 5484]

**크기 불일치:** 학습 큐브를 §III-C-1에서는 한 변 **75 mm**, Fig. 5에서는 **80 mm**로 설명한다. 둘 중 하나를 실제 simulator 설정으로 확정하지 않는다. Fig. 7 실물의 soft toy·rubber duck·wooden hand에 위 질량·치수를 옮겨 붙이지도 않는다. 이들의 상세 질량·치수는 별도로 보고되지 않는다.

### 8.3 시뮬레이션의 미지 물체·목표 일반화

평가는 cube를 포함한 **10개 물체**, workspace 전반에 고르게 분포한 **54개 goal**, **5 trials 평균**으로 제시된다. 시작 위치에서 최소 0.1 m 이상 떨어진 목표만 고려한다. 학습에서 보지 못한 물체는 9개다. [원문 §IV-B, Table III, PDF pp. 5–6]

**Table III — 성공률. 원문의 0–1 표기 유지**

| 물체 | Model-free image | Model-free pose | Model-based pose |
| --- | --- | --- | --- |
| Cube | 0.91 | 0.89 | **0.96** |
| Cylinder | 0.85 | **0.91** | **0.91** |
| Hexagonal prism | 0.93 | 0.89 | **0.94** |
| Gelatin box | 0.71 | 0.74 | **0.75** |
| Master chef can | 0.57 | **0.76** | 0.66 |
| Mug | 0.81 | 0.83 | **0.95** |
| Potted meat can | 0.80 | 0.89 | **0.90** |
| Chip can | 0.94 | 0.91 | **0.98** |
| Rubiks cube | 0.96 | 0.94 | **0.99** |
| Tomato soup can | 0.89 | 0.89 | **0.94** |

[원문 Table III, PDF p. 6 / 인쇄 p. 5485]

원문은 model-based가 10개 중 9개에서 가장 좋았다고 서술한다. 표의 정밀도에서는 **8개 단독 최고 + cylinder 공동 최고**이며, master chef can은 model-free pose가 높다. 또한 model-free pose가 image보다 모든 물체에서 우수한 것도 아니다. Cube·hexagonal prism·chip can·Rubiks cube에서는 image SAC의 수치가 더 높고, tomato soup can은 같다.

저자들은 gelatin box가 가늘고 긴 형상 때문에 cube보다 쉽게 회전하고, master chef can은 크기가 커 조작하기 어려웠다고 설명한다. 이는 특정 물체의 실패 난도에 대한 설명이지 두 방법의 일반적인 우열을 모든 상황에 확정하는 결과가 아니다. [원문 §IV-B, PDF p. 6]

### 8.4 실물의 목표 일반화: 40개 goal

실물 cube 환경에서는 workspace에 고르게 분포한 **40개 goal**을 사용한다. 원문은 **110 mm보다 먼 목표에서 모든 agent가 100% 성공**했다고 보고하면서, 가까우면서 bearing이 큰 목표에서는 신뢰도가 낮아진다고 설명한다. 각 목표의 반복 횟수와 전체 40개에 대한 방법별 성공률 표는 별도로 제시하지 않는다. [원문 §IV-C-1, PDF p. 6]

Fig. 6은 다음 다섯 goal의 simulation/real trajectory를 예시로 보여 준다.

| Fig. 6 열 | Goal 좌표 (mm) |
| --- | --- |
| (a) | (100, 100) |
| (b) | (150, 100) |
| (c) | (100, 180) |
| (d) | (270, 280) |
| (e) | (270, 50) |

[원문 Fig. 6, PDF p. 6]

저자들은 bearing이 큰 도달 가능한 목표에서는 model-free가 model-based보다 짧은 경로를 만들지만, 더 가까운 어려운 목표에서는 model-based가 더 안정적이고 해석 가능한 경로를 보이며 model-free는 제어하기 어려운 영역으로 물체를 보낼 수 있다고 설명한다. 실물과 simulation의 유사성은 PoseNet의 관측 이전이 작동한다는 근거로 해석하고, 남은 차이에는 마찰 등 물성 불일치가 영향을 줄 수 있다고 본다. [원문 §IV-C-1, PDF p. 6]

**110 mm 문구의 확인 한계:** 본문은 그 거리의 기준점·축을 별도 식으로 정의하지 않고, 바로 옆 Fig. 6(a), (b)를 가까운 목표의 어려운 사례로 든다. 따라서 이 수치를 곧바로 ‘원점에서 유클리드 거리 110 mm를 넘는 모든 점’이라는 재현 규칙으로 확정하지 않는다. 원문 조건부 성공 서술과 그림의 목표 좌표를 함께 보존한다.

### 8.5 실물의 불규칙 물체

모든 물체는 안정적인 초기 접촉에서 시작하며, 목표는 **x = 100 mm, y = 180 mm**다. 물체는 다음 네 가지 접촉 난도를 대표하도록 선택했다. [원문 §IV-C-2, PDF p. 6]

| 물체 | 저자들이 부여한 시험 목적 | 보고 결과 |
| --- | --- | --- |
| Cylinder | 큰 pushing 방향 변화 중 곡면 접촉 유지 | 두 pose 기반 방법 모두 목표 도달 |
| Soft deformable toy | 순응적인 접촉면, 마찰 축적에 따른 interaction 변화와 불확실한 tactile signal | 두 pose 기반 방법 모두 목표 도달 |
| Rubber duck | 부리에 접촉하여 불안정한 접촉점과 관측 모델 학습에서 보지 못한 변형 유발 | Image SAC는 contact loss로 실패. 두 pose 기반 방법은 도달 |
| Wooden hand | 지지면과 불균일하게 접촉하는 물체의 민감한 거동 | 두 pose 기반 방법 모두 목표 도달 |

[원문 §IV-C-2, Fig. 7(a)–(d), PDF pp. 6–7]

이 네 사례에서 pose SAC의 경로가 model-based보다 짧다고 보고한다. 다만 실험별 반복 수·분산·평균 path length를 별도 표로 제공하지 않으므로, Fig. 7의 대표 trajectory와 reward를 전체 물체 분포에 대한 정량 보장으로 해석하지 않는다.

### 8.6 외란 시험의 조건

| 외란 | 원문 설정 | 접촉에서 어려워지는 점 |
| --- | --- | --- |
| Initial contact angular offset | **±20°** | 처음부터 접촉면과 pusher가 정렬되지 않음 |
| Center of mass offset | 속이 빈 상자의 한쪽에 **100 g 추 2개** | 비대칭 하중과 COF offset에 대응해야 함 |
| Obstacle contact | 밀리는 물체와 **같은 질량의 cylinder**를 경로에 배치 | 물체가 장애물과 만나 지속적인 저항·거동 변화를 겪음 |

[원문 §IV-C-3, Fig. 7(e)–(j), PDF p. 7]

원문은 image SAC가 **−20° 초기 오차**에서 실패했다고 설명한다. 지속적인 외란이 있는 경우에는 sticking contact가 접촉면을 따라 pushing 위치를 옮기는 것을 제한하여, COF offset을 상쇄하기 어렵다고 설명한다. 하지만 COF 위치나 slip 상태를 별도로 측정하는 모듈은 제시하지 않는다. 이 설명은 관찰한 거동에 대한 저자들의 해석이다. [원문 §IV-C-3, PDF p. 7]

장애물은 사전 경로 계획·시각 회피 성능을 평가하기 위한 장애물 지도가 아니라, **미는 물체의 경로에 놓인 외란**이다. ‘장애물을 보지 않고도 우회 경로를 계획했다’거나 ‘추가 물체의 접촉을 분류했다’는 결과로 확장하지 않는다. [원문 §IV-C-3, Fig. 7(i)–(j), PDF p. 7]

### 8.7 Fig. 7의 episode reward와 None 표시

아래는 그림의 세 방법별 **표시값을 그대로 기록**한 것이다. 단위는 거리·힘이 아니고 episode reward다. `None`은 원문 그림의 비수치 표시이며 0점으로 치환하지 않는다.

| 패널·조건 | Model-free image | Model-free pose | Model-based pose |
| --- | --- | --- | --- |
| (a) Cylinder | −80.2 | −60.7 | −159.0 |
| (b) Soft toy | −79.3 | −60.1 | −121.9 |
| (c) Rubber duck | None | −98.3 | −168.3 |
| (d) Wooden hand | −122.5 | −102.7 | −126.4 |
| (e) Rotation offset 1 | −23.8 | −24.7 | −34.1 |
| (f) Rotation offset 2 | None | −57.5 | −68.2 |
| (g) Center of mass offset 1 | −16.7 | −17.4 | None |
| (h) Center of mass offset 2 | None | −19.2 | None |
| (i) Obstacle 1 | −25.7 | −19.9 | −42.8 |
| (j) Obstacle 2 | −46.1 | −21.8 | −37.9 |

[원문 Fig. 7, PDF p. 7 / 인쇄 p. 5486]

그림 caption은 red arrow를 tactile sensor, blue dot을 ArUco로 추적한 물체 중심, green circle을 goal region으로 정의한다. **접촉점 목표와 물체 중심 궤적은 서로 다른 정보**이므로 그림에서 물체 중심이 goal circle의 중심과 일치해야만 성공이라고 판단하지 않는다. [원문 Fig. 7 caption, §III-B-4, PDF pp. 4, 7]

본문은 duck와 −20°의 image-based 실패를 명시적으로 설명한다. 한편 Fig. 7(g), (h)의 model-based 결과에도 `None`이 있으며, (h)의 image-based 결과도 `None`이다. 원문은 이들 각각의 `None` 의미와 종료 원인을 caption에서 정의하지 않는다. **모든 pose 기반 방법이 모든 외란에서 성공했다는 문장으로 덮어 쓰지 않고**, 그림의 표시와 저자들의 일반적 결론을 구분한다.

또한 (e), (g)에서는 image SAC의 수치가 pose SAC보다 약간 높다. 저자들이 전반적으로 강조하는 pose 기반 방법의 안정성과 일반화가 모든 개별 reward의 엄격한 우위를 뜻하지는 않는다. 서로 다른 목표·조건의 누적 reward도 동일 길이 경로의 직접 비교값이 아니므로, 수치만으로 미터 단위 path length나 wall-clock 수행 시간을 계산할 수 없다.

## 9. 저자들의 결론, 한계와 원문 내부 주의사항

### 9.1 저자들의 종합 결론

저자들은 contact surface pose가 이 과업에 유효한 tactile feature이며, 단일 물체·제한된 목표 분포에서 domain randomization 없이 학습해도 여러 미지 물체·상황으로 이전할 수 있음을 강조한다. Model-based는 적은 샘플로 넓은 물체·목표 집합에서 높은 성공률을 보였고, 충분히 더 학습한 pose SAC는 높은 reward와 짧고 안정적인 경로를 보였다는 것이 논문의 주된 해석이다. [원문 §V, PDF pp. 7–8]

저자들은 normal contact를 장려하는 reward가 안정성과 일반화에 중요하다고 본다. 이는 이 실험에 대한 설명과 향후 기대이며, 임의 물체·센서·마찰에 대해 normality만으로 pushing 안정성을 보장하는 일반 증명은 아니다. [원문 §V, PDF p. 7]

### 9.2 저자들이 직접 남긴 한계와 후속 과제

고정 전진 action은 제어 자유도를 줄이고 가까운 목표의 reachability와 접촉면 탐색을 제한한다. 향후에는 이 제약을 없애고 신뢰성과 성능 사이의 trade-off를 더 조사할 수 있다고 제안한다. [원문 §V, PDF pp. 7–8]

또한 model-based의 sample efficiency를 이용하면 실물 학습도 가능할 수 있다고 보지만, **사람의 개입과 시각 없이 환경을 reset하는 문제**는 아직 해결할 과제로 남긴다. 본 논문이 실물에서 자동 reset을 포함한 자율 RL 학습을 완료했다는 뜻이 아니다. [원문 §V, PDF p. 8]

### 9.3 수치·표기를 임의로 통일하지 않은 항목

| 항목 | 원문에서 확인한 차이·한계 | 본 정리의 처리 |
| --- | --- | --- |
| 학습 cube 크기 | §III-C-1: 75 mm. Fig. 5: 80 × 80 × 80 mm | 둘 다 출처와 함께 기록. 실제 코드값 미확인 |
| Pose sampling depth | Table I: [−1, −5] | 부호·순서 유지. 양수 범위나 정렬 구간으로 무표시 수정하지 않음 |
| Dynamics prediction target | 본문: state difference. 식 (2): next-state 형태의 잔차 | 원문 식을 보존하고 불일치 명시 |
| Goal bearing 식 | atan2에 두 위치 벡터를 인수로 표기 | 방향각이라는 의미와 미명시 구현을 구분 |
| 110 mm 조건부 성공 | 거리의 기준·축을 별도 정의하지 않으며 Fig. 6(a), (b)를 어려운 근접 목표로 설명 | 모든 유클리드 반경 조건으로 단정하지 않음 |
| 9/10 objects 최고 성능 | Table III의 cylinder는 공동 최고 | 8개 단독 + 1개 공동으로 구분 |
| 외란 일반화 | Fig. 7 일부 model-based·image-based 결과는 None | 성공·실패 집계로 임의 변환하지 않고 표시 유지 |
| PoseNet validation accuracy | ± 수치의 통계적 정의가 없음 | 표준편차·신뢰구간·센서 분해능으로 재명명하지 않음 |
| Action 제약 절 참조 | §IV-C-1은 §III-A를 가리키지만 실제 action 설명은 §III-B-2 | 관련 본문 위치를 함께 안내 |

[원문 §III–IV, Table I–III, Fig. 5–7, PDF pp. 3–7]

### 9.4 재현에 필요한데 원문에 없는 정보

| 분야 | 미명시 또는 상세 확인이 필요한 항목 |
| --- | --- |
| 센서 하드웨어 | Tip 치수·재료, 영상 해상도·fps, force range·resolution·sensitivity·accuracy |
| 촉각 전처리 | Crop·resize·normalization·filter, 영상 acquisition timing |
| 접촉 pose 복원 | Depth 원점·부호, polar-to-Cartesian 구체식, 센서 반경·calibration, 접촉 다중점 처리 |
| 로봇 연결 | Command·observation 주기, action 적용 시간, trajectory interpolation, 센서–로봇 동기화 |
| Reward 구현 | Distance scaling, cosine distance 정의, bearing의 성분식, terminal reward 여부 |
| SAC | Network·learning rate·batch·buffer·entropy·seed·학습 반복 설정 |
| PETS/MPC | Ensemble·particle 수, horizon, CEM 설정, bootstrap·초기 탐색, update frequency, runtime |
| 종료·안전 | Timeout, contact loss 판정, workspace 이탈 기준, 과부하 제한과 emergency stop 연결 |
| 물리 환경 | Default physics의 구체 수치, 실물 지지면 마찰·재료, 불규칙 물체 질량·치수 |
| 통계·결과 | 실물 반복 횟수·분산, Fig. 7 None의 개별 의미, force·path length·시간의 독립 정량 지표 |

이 표는 논문 본문만으로 확인하지 못한 부분을 구분하기 위한 것이다. 해당 코드나 실제 시스템에 관련 처리가 없다는 뜻은 아니다. 본 논문이 참조한 라이브러리와 과거 연구에 상세 구현이 있을 수 있으나, 이번 원문 정독에서는 그 내용까지 확인한 것으로 취급하지 않았다.

### 9.5 비교 결과를 읽는 범위

S1·S2 비교는 영상 대 pose 외에도 **goal의 상대 좌표계와 관측 모델 학습 표본 수가 다르다.** 따라서 결과는 저자들이 구성한 전체 pipeline의 비교로 읽어야 한다. ‘영상에서 특정 특징 하나만 제거했을 때의 순수 인과 효과’를 분리한 실험으로 설명하지 않는다. [원문 식 (3), Table I, Fig. 2, PDF pp. 3–5]

마찬가지로 model-free와 model-based의 최종 비교는 학습량이 크게 다른 조건의 최종 agent를 비교한다. Table II의 sample efficiency, Table III의 성공률, Fig. 7의 사례 reward를 한 지표로 합쳐 한쪽이 언제나 우수하다고 결론내리지 않는다. [원문 §IV–V, PDF pp. 5–8]

## 10. 원문을 다시 읽을 때의 위치 안내

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 문제 동기, 기존 tactile pushing과의 차이 | §I, PDF pp. 1–2 / 인쇄 pp. 5480–5481 |
| Related Work 비교 구도 | §II, PDF p. 2 / 인쇄 p. 5481 |
| Goal-conditioned objective와 SAC | §III-A-1, 식 (1), PDF pp. 2–3 |
| PETS dynamics model, NLL, MPC·CEM | §III-A-2, 식 (2), PDF p. 3 |
| S1·S2·S3의 정확한 구성 | §III-B-1, 식 (3), Fig. 2(a), PDF pp. 3–4 |
| 횡이동·회전 action과 고정 전진 | §III-B-2, PDF p. 3 |
| Contact-normality와 goal shaping | §III-B-3, 식 (4), PDF pp. 3–4 |
| Workspace, 초기 접촉, goal sampling, 25 mm 종료 | §III-B-4, Fig. 3, PDF p. 4 |
| Simulated depth·contact pose, 단일 cube·DR 없음 | §III-C-1, PDF p. 4 |
| GAN·PoseNet 데이터와 변환 | §III-C-2, Table I, Fig. 2(b), PDF pp. 4–5 |
| Zero-shot transfer와 robot specs | §III-C-3–D, Fig. 1, PDF pp. 1, 5 |
| 학습 샘플과 best reward | §IV-A, Fig. 4, Table II, PDF p. 5 |
| 물체 질량·치수 | Fig. 5, PDF p. 5 |
| 10개 물체·54개 목표 성공률 | §IV-B, Table III, PDF pp. 5–6 |
| 실물 40개 목표와 가까운 목표의 한계 | §IV-C-1, Fig. 6, PDF p. 6 |
| 불규칙 물체·각도·하중·장애물 외란 | §IV-C-2–3, Fig. 7, PDF pp. 6–7 |
| None을 포함한 사례별 reward | Fig. 7, PDF p. 7 |
| 저자 결론과 action·실물 reset의 후속 과제 | §V, PDF pp. 7–8 |
| 인용 선행연구의 서지 | References, PDF p. 8 |

## 11. 핵심 메커니즘 요약

이 논문의 주된 정보–행동 연결은 **촉각 영상 → 영상 변환 또는 접촉 깊이·각도 추정 → goal-aware 접촉 상태 → 접촉면 정렬과 목표 진행을 평가하는 reward → SAC 정책 또는 PETS/MPC → 횡이동·회전 증분**이다. 전진은 고정된 1 mm 증분으로 제공한다. [원문 §III, PDF pp. 2–5]

접촉 상태를 잘 표현하고 normal pushing을 장려하는 학습 목표를 사용하면, 물체 중심의 시각적 추적이나 물체별 동역학 파라미터를 입력하지 않아도 여러 물체를 목표 방향으로 밀 수 있다는 것이 저자들의 결과다. 그러나 그 결과는 **안정적인 초기 접촉, 제한된 평면 행동, 접촉점 기준 목표, 준비된 관측 변환 모델**을 전제로 한다. 센서 force 제어, 모든 근접 목표 도달, 임의 물체 자세 제어, 모든 외란에서의 성공을 입증한 논문으로 확대하지 않는다. [원문 §III–V, Table III, Fig. 6–7, PDF pp. 3–8]


---


저자들이 논문 서론(Section I)과 결론(Section V)에서 밝힌 본 연구의 의의와 핵심 기여(Main Contributions)는 단순한 3가지 방식의 비교를 넘어 크게 세 가지 축으로 제시됩니다. 세 방식의 비교 평가는 이러한 파이프라인의 효용성과 특성을 증명하기 위한 실증 분석(Empirical study)의 일환입니다.

**저자들이 명시한 핵심 기여 3가지**

* **시각 정보 없는 목표 조건부(Goal-Conditioned) 촉각 푸싱 정식화**: 외부 카메라나 전역 비전 센서 없이 오직 촉각과 로봇 고유수용성 감각(Proprioception)만으로 임의의 먼 목표 지점까지 물체를 안정적으로 밀어 이동시키는 RL 문제를 성공적으로 정식화했습니다. 기존 연구들이 사전 정의된 경로 추종(Trajectory following)이나 짧은 거리에 머물렀던 한계를 넘었습니다.

* **포즈 기반 촉각 관측의 Sim-to-Real 파이프라인 구축**: 촉각 이미지에서 추출한 접촉면 포즈(Tactile Pose)를 관측으로 활용하는 Sim-to-Real 프레임워크를 제안했습니다. 특히 저자들은 이것이 **촉각 기반 Sim-to-Real 환경에서 모델 기반 강화학습(Model-Based RL)을 성공적으로 적용한 최초의 사례**임을 강조합니다.

* **도메인 무작위화(Domain Randomization) 없는 제로샷 일반화 실증**: 큐브 단 하나와 단순한 물리 엔진(PyBullet) 환경에서 학습했음에도, 별도의 도메인 무작위화 없이 실물 환경의 다양한 미지의 물체(오리 인형, 장난감 등)와 외란(질량 편중, 회전 오차, 장애물)에 성공적으로 일반화됨을 입증했습니다.


**3가지 방식 비교 연구의 역할**
저자들은 제안한 파이프라인 안에서 촉각 표현 방식(이미지 vs 포즈)과 RL 패러다임(Model-Free vs Model-Based) 간의 실질적인 트레이드오프를 규명하기 위해 비교 실험을 수행했습니다.

* 원시 촉각 이미지보다 **접촉면 포즈(Tactile Pose)가 푸싱 학습에 훨씬 효과적인 저차원 특징**임을 확인했습니다.

* 모델 기반 RL(MBRL)은 100배 적은 샘플로 학습이 가능해 온라인 플래닝에 강점을 보인 반면, 충분한 샘플을 학습한 모델 프리 RL(MFRL)은 큰 외란 속에서도 더 짧고 최적화된 경로를 안정적으로 생성한다는 것을 실험적으로 비교 검증했습니다.


결과적으로 저자들의 궁극적인 의의는 "시각 없이 촉각 정보와 접촉 수직성 보상 설계를 적절히 활용하면, 복잡한 시뮬레이션 튜닝 없이도 미지의 물체들을 제어하는 범용 로봇 조작 정책을 학습할 수 있음을 증명한 것"에 있습니다.

---

논문에서는 **PyBullet** 물리 엔진을 기반으로 구축된 로봇 촉각 강화학습 환경인 **Tactile Gym**을 사용했습니다. 실물의 광학식 소프트 촉각 센서(TacTip)를 시뮬레이션 내에서 구현하고 데이터를 추출한 방식은 다음과 같습니다.

**1. 시뮬레이션 플랫폼**

* **물리 엔진**: 강체 역학(rigid-body physics) 시뮬레이터인 **PyBullet** 기반의 **Tactile Gym** 프레임워크를 사용했습니다.
* **물리 파라미터**: 도메인 무작위화(Domain Randomization)를 일체 적용하지 않고, Tactile Gym에서 사전에 설정된 기본 물리 파라미터(default physics parameters)를 그대로 활용해 훈련했습니다.

**2. 시뮬레이션 내 Tactile 센서 구현 방식**
실제 로봇에 장착된 TacTip은 부드러운 반구형 고무 표면 아래에 박힌 331개 핀의 변형을 내부 카메라로 포착하는 광학식 센서입니다. 시뮬레이션에서는 계산 비용이 큰 유연체 유한요소해석(FEM) 대신 시뮬레이터 특성에 맞춰 두 가지 방식으로 신호를 근사(approximation)하여 모델링했습니다.

* **촉각 이미지($I_{\text{tactile}}$) 생성**: 가상 센서와 물체 사이의 접촉 표면을 렌더링한 깊이 이미지(Rendered Depth Image)를 생성하여 촉각 이미지로 사용했습니다. 실환경으로 전이할 때는 pix2pix 구조의 GAN(Real-to-Sim GAN)을 통해 실물 카메라의 핀 변형 패턴 이미지를 시뮬레이션 깊이 영상 도메인으로 변환해 일치시켰습니다.
* **접촉면 포즈(Tactile Pose) 추출**: 시뮬레이터 내부에서 근사된 센서 형상과 물체 간의 기하학적 접촉 정보(Contact information)를 물리 엔진에서 직접 읽어와 접촉면의 상대 포즈($x_o^p, y_o^p, \theta_o^p$)를 생성했습니다. 실물 로봇에서는 이 접촉 포즈를 직접 읽어올 수 없으므로, 사전 학습된 CNN 추정기(PoseNet)가 실물 촉각 이미지로부터 동일한 형식의 포즈 벡터를 추정하도록 구성했습니다.