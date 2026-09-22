# 2. Related Works

[발표 문서 안내](README.md) · [Research Motivation and Contributions](01_Research_Motivation.md) · [Method](03_Method.md)

> **문서 상태: 선행연구 정리.** F/T·Wrench와 Tactile 활용 방식, RL 보상 설계와 Domain Randomization 사례를 정리한다. 본 연구의 Contribution은 [01 문서](01_Research_Motivation.md), 실행 설계는 [03 문서](03_Method.md)에서 다룬다.

## 2.1. F/T·Wrench를 활용하는 선행연구

힘 피드백의 사용 위치에 따라 **규칙 기반 조향·행동 전환**, **운동·제어 파라미터를 학습하는 정책**, **접촉 예측을 결합한 반응형 정책** 순서로 정리한다. 외장 F/T 측정과 관절 토크 기반 외력 추정, 정책이 실제로 사용하는 힘·모멘트 성분을 구분한다.

### 2.1.1. Force Push — 힘 방향 기반 조향과 접촉 복구

[**Adam Heins and Angela P. Schoellig - Force Push: Robust Single-Point Pushing With Force Feedback**](../literature/papers/2024-heins-force-push.md), 2024. 물체의 현재 Pose와 형상·마찰 모델 없이, 손목 F/T에서 얻은 **평면 접촉력의 방향과 크기**로 단일 접촉점 밀기를 조절하는 규칙 기반 제어다. 로봇의 위치와 주어진 경로는 사용하며, 힘 방향과 경로 방향의 차이 및 횡방향 경로 오차로 **EEF의 미는 속도 방향**을 정한다. 물체와 힘 방향이 반시계 방향으로 틀어지면 미는 방향을 그보다 더 반시계 방향으로 기울여, 결과적으로 물체가 시계 방향으로 돌아오도록 유도한다. 따라서 단순히 오차의 반대쪽으로 툴 자세를 회전시키는 제어와는 다르다.

힘이 하한보다 작으면 힘 방향 기반 조향을 중단하고 **경로로 돌아가는 방향으로 서서히 전환하여 재접촉을 시도**한다. 반대로 하중이 상한을 넘으면 Admittance 속도 보정으로 힘 방향의 진행을 줄인다. 핵심은 힘을 일정 목표값에 계속 맞추는 것이 아니라, **방향은 조향에, 작은 힘은 접촉 복구에, 큰 힘은 과부하 완화에 사용**한다는 점이다. (원문 §IV-A–C, 식 (1)–(4), 상세 리뷰 §5–6)

### 2.1.2. 1 kHz Behavior Tree — 접촉 상태에 따른 행동 전환

[**Yansong Wu et al. - 1 kHz Behavior Tree for Self-adaptable Tactile Insertion**](../literature/papers/2024-wu-1khz-tactile-insertion.md), 2024. Peg-in-Hole 삽입에서 **삽입축 위치·속도와 상호작용 힘 추정값으로 접촉 상태를 판단하고, Behavior Tree가 행동 Primitive를 전환**한다. 전체 과정에는 다음 행동이 포함된다.

| 행동 | 역할 |
| --- | --- |
| **Approach** | 초기 위치에서 Hole 방향으로 접근 |
| **Contact** | 삽입 전 접촉 형성 |
| **Wiggle** | 진동하는 Feed-forward Force로 탐색·정렬 및 걸림 해소 |
| **Push** | 정렬되면 Wiggle을 멈추고, 마지막 Feed-forward Force를 유지하여 삽입 |

접촉 이후의 핵심 선택은 **Wiggle과 Push의 전환**이다. Searching·Stuck·Unstuck·Aligned 상태를 갱신하여 Aligned이면 Push를 선택하고, Push 도중 다시 걸리면 Wiggle로 복귀한다. 계속 흔드는 고정 순서 대신 **현재 접촉 상태에 맞는 행동을 선택**한다는 데 의미가 있다. 원문에서 사용한 힘은 관절 토크·로봇 동역학 기반 추정이며 외장 손목 F/T 장착은 확인되지 않는다. 1 kHz는 Behavior Tree의 판단 주기다. (원문 §II-B–C, Algorithm 1, 상세 리뷰 §5.2·6·8–9)

### 2.1.3. Learning Force Control — 위치·힘 제어의 결합과 파라미터 학습

[**Cristian Camilo Beltran-Hernandez et al. - Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots**](../literature/papers/2020-beltran-hernandez-learning-force-control.md), 2020. SAC 정책은 **목표 EEF Pose 오차·EEF 속도·F/T 피드백**을 관측하고, 운동 보정과 Force Controller 파라미터를 함께 출력한다. RL이 기존 힘 제어기를 대체하는 것이 아니라 **어떻게 움직일지와 접촉에 얼마나 반응할지를 함께 조절**하는 구조다.

Parallel Position/Force Control에서는 **위치 오차를 처리하는 PD 경로**와 **측정 힘을 처리하는 PI 경로**를 구분하고, 축별 Selection Matrix로 두 경로의 비중을 조절한 뒤 RL의 운동 보정을 결합한다. 정책은 위치·힘 Gain과 Selection Matrix를 선택하며, 비교한 Admittance 방식에서는 위치 Gain과 Stiffness를 선택한다. 최종 결과는 Pose 명령과 IK를 거쳐 위치 제어 로봇에서 실행된다. 따라서 정책이 독립적인 목표 힘 벡터를 바로 출력한다기보다, **힘 피드백을 사용하는 제어 경로의 파라미터까지 행동 공간에 포함한 방식**이다. (원문 §III, 상세 리뷰 §5–6·8·10–15)

### 2.1.4. Zero-Shot Transfer — 하중 관측을 이용한 슬롯 삽입

[**Samarth Brahmbhatt et al. - Zero-Shot Transfer of Haptics-Based Object Insertion Policies**](../literature/papers/2023-brahmbhatt-zero-shot-haptics-insertion.md), 2023. 이미 파지한 접시 등의 물체를 **슬롯형 홀더에 삽입**하는 접촉 구간을 대상으로 한다. 실행 전 시각으로 얻은 근사 목표와 현재 EEF의 상대 Pose, 관절 토크 기반 **추정 6축 Wrench**를 정책에 제공하며, 삽입 중 물체 Pose를 계속 추적하지 않는다.

SAC 정책은 상대 Pose와 Wrench의 시간 Stack을 사용하여 **목표로 향하는 기본 운동에 더할 병진·회전 보정**을 출력하고, OSC가 이를 실행한다. 목표 오차나 막힌 슬롯에서 발생한 접촉을 이용해 삽입 동작을 조절하며, 시뮬레이션에서 학습한 정책을 실물 미세조정 없이 이전한다. 이는 하중 관측을 실제 삽입 행동의 보정에 연결한 사례지만, **Wrench 자체를 제거한 비교는 없어 그 입력만의 독립 효과를 분리한 결과는 아니다.** (원문 §III–IV, 상세 리뷰 §1–4·6)

### 2.1.5. FORGE — 허용 힘으로 조건화한 조립 정책

[**Michael Noseworthy et al. - FORGE: Force-Guided Exploration for Robust Contact-Rich Manipulation under Uncertainty**](../literature/papers/2025-noseworthy-forge.md), 2025. **Peg 삽입, 기어 맞물림, M16 너트 체결**의 정책을 PPO로 학습하고, Snap-fit과 여러 Primitive를 연결한 Planetary Gearbox 조립에서도 평가한다. 정책에는 EEF 상태·고정부품 Pose 추정값과 함께 **관절 토크에서 추정한 3축 힘 및 사용자가 지정한 허용 힘**을 제공한다. 손목 6축 Wrench 전체를 입력하는 방식과는 다르다.

핵심은 **허용 힘을 정책의 조건으로 제공하고, 그 한계를 초과한 힘에 벌점을 주는 것**이다. 학습 중 허용 힘과 제어 Gain·물성을 변화시켜, 배포 시 지정한 힘 수준에 맞춰 운동을 조절하도록 한다. 따라서 매번 Gain을 다시 조정하는 대신 정책이 힘 관측에 반응하도록 학습한다. Snap-fit에서는 성공 예측 결과에 따라 다음 시도의 허용 힘을 높이는 절차도 사용한다. 다만 Force Limitation은 **허용 힘으로 조건화한 정책과 초과 페널티**로 구현되며, 힘 초과 자체를 불가능하게 만드는 하드 제약은 아니다. (원문 §III-A–C, §V-D–E, 식 (3), 상세 리뷰 §2–6)

### 2.1.6. FoAR — 미래 접촉 예측과 반응형 행동 보정

[**Zihao He et al. - FoAR: Force-Aware Reactive Policy for Contact-Rich Robotic Manipulation**](../literature/papers/2025-he-foar.md), 2025. 외장 OptoForce의 **6축 F/T 이력**과 현재 RGB-D 장면 정보를 사용하는 모방학습 정책으로, Wiping·Peeling·Chopping을 수행한다. 힘 정보를 단순히 시각 특징에 이어 붙이는 대신, **Future Contact Predictor**가 현재 RGB와 F/T 이력으로 접촉 가능성을 예측하고, 그 값에 따라 힘 특징과 중립 특징의 혼합 비율을 조절한다. 접촉이 예상되는 구간에서는 힘 정보를 강조하고, 비접촉 구간에서는 힘 잡음의 영향을 줄이는 구성이다.

예측은 센서 융합에만 쓰이지 않는다. **접촉이 예상되지만 현재 힘·모멘트가 부족하면, 예측한 Action 궤적의 진행 방향으로 위치 명령을 보정**한다. 이때 보정 방향은 측정 힘의 방향이 아니라 정책이 예측한 움직임에서 얻는다. 따라서 핵심은 **미래 접촉 예측 → 힘 특징 반영 비율 조절 → 실행 중 부족한 접촉에 대한 행동 보정**의 연결이다. 실행 중 시각을 계속 사용하는 모방학습이며, RL이나 별도의 힘 추종 제어기를 제안한 연구는 아니다. (원문 §III-B–C, Algorithm 1, 상세 리뷰 §6·9–11)

## 2.2. Tactile 정보를 활용하는 선행연구

촉각 활용 방식은 **명시적 상태 추정**, **고차원 영상 인코딩**, **저차원 접촉 표현**의 세 방향으로 정리한다. 이어서 [2.2.4절](#224-촉각-표현을-직접-비교한-연구)에서는 표현을 직접 비교한 연구를 통해, 어떤 정보를 남기거나 제거하는 것이 조작과 실물 전이에 유효했는지 살펴본다.

### 2.2.1. Contact Point·Pose·Shape 등을 명시적으로 추정하는 접근

이 접근은 촉각 신호를 바로 행동으로 연결하기보다, **접촉 위치·접촉면 자세·물체 자세와 같은 해석 가능한 상태로 변환한 뒤 제어에 활용**한다. 여기서는 각 연구가 실제로 추정하는 대상과, 제한된 관측에 대응하는 방법을 구분한다.

[**Max Yang et al. - Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing**](../literature/papers/2023-yang-sim-to-real-tactile-pushing.md)는 센서 영상에서 **접촉 깊이와 각도**를 추정하고, 이를 로봇·목표 정보와 결합하여 밀기 정책 또는 동역학 모델의 입력으로 사용한다. 촉각의 국소 관측으로 물체 중심과 전체 형상·물성을 얻기 어렵기 때문에, **물체 전체 상태를 복원하는 대신 접촉면의 자세와 접촉 위치를 제어 대상으로 선택**한다. 접촉면에 수직으로 밀도록 정렬하면서 접촉 위치를 목표로 이동시킨다.

[**John Lloyd and Nathan F. Lepora - Pose-and-shear-based tactile servoing**](../literature/papers/2024-lloyd-pose-and-shear-based-tactile-servoing.md)는 **접촉 자세와 접촉 이후의 Shear 변형**을 함께 추정한다. 이 연구는 미끄러짐 때문에 서로 다른 접촉·Shear 상태가 유사한 영상을 만드는 **Tactile aliasing**을 다룬다. 하나의 상태값만 출력하는 회귀 대신 **평균과 불확실성을 출력하는 Gaussian-density network(GDN)**를 사용하고, 로봇 운동학에 따른 시간적 예측과 **SE(3) Bayesian filtering**으로 결합한다.

[**Idil Ozdamar et al. - Pushing in the Dark: A Reactive Pushing Strategy for Mobile Robots Using Tactile Feedback**](../literature/papers/2024-ozdamar-pushing-in-the-dark.md)는 모바일 베이스의 정전용량 촉각에서 **대표 접촉점**을 계산한다. Taxel별 신호를 저역통과 필터와 임계값으로 처리한 뒤, 하나만 활성화되면 해당 Taxel의 위치를, 여러 개가 활성화되면 접촉 영역 **양 끝 Taxel 위치의 중점**을 사용한다. 물체의 Pose·형상·물성을 직접 복원하지 않고, 알려진 센서 배치와 Point/Line contact 근사를 이용하여 접촉을 하나의 제어 변수로 축약한다.

[**Pose-and-shear-based tactile servoing**](../literature/papers/2024-lloyd-pose-and-shear-based-tactile-servoing.md)에서는 제시하는 모델이 **평면 또는 완만한 곡면**을 중심으로 하기 때문에, 모서리와 같은 다른 표면 특징으로 확장할 때, 별도의 추정·제어 구성이 필요하다고 설명한다. 따라서 이러한 방법은 **촉각 영상에서 국소 상태를 안정적으로 추정하는 정확도와 동일한 접촉 모델을 다양한 표면 형상에 적용하는 것에 한계가 존재한다.**

### 2.2.2. 고차원 Tactile Image를 인코딩하여 사용하는 접근

이 접근은 **고차원 촉각 영상 또는 분포형 촉각을 영상 형태로 표현한 입력**을 Encoder로 처리하고, 생성된 특징을 정책에 제공한다. 접촉점이나 자세 하나로 먼저 축약하지 않고, 공간적인 접촉 패턴·변형·하중 분포를 행동 학습에 활용한다.

[**Yijiong Lin et al. - Tactile Gym 2.0: Sim-to-Real Deep Reinforcement Learning for Comparing Low-Cost High-Resolution Robot Touch**](../literature/papers/2022-lin-tactile-gym-2-0.md)는 TacTip, DIGIT, DigiTac을 같은 Sim-to-Real 방법론에서 비교한다. 실제 촉각 영상을 **시뮬레이션의 Depth-image 표현으로 변환하는 GAN**과 PPO 정책을 결합하여 Edge-following, Surface-following, Pushing을 수행한다.

[**Yijiong Lin et al. - Bi-Touch: Bimanual Tactile Manipulation With Sim-to-Real Deep Reinforcement Learning**](../literature/papers/2023-lin-bi-touch.md)는 두 TacTip 영상을 각각 **Real-to-Sim GAN**으로 변환하고, 영상 특징과 고유감각·목표 정보를 PPO 정책에 제공하여 양팔 밀기·재정렬·모으기를 수행한다.

[**Brouwer et al. - Gentle Object Retraction in Dense Clutter Using Multimodal Force Sensing and Imitation Learning**](../literature/papers/2026-brouwer-gentle-object-retraction.md)는 도구 양 측면의 분포형 3축 촉각을 **20×5×3 Force Image**로 표현하고, 촉각 전용 ResNet-18로 인코딩한다. 이 영상의 채널은 광학 촉각 카메라의 색을 관측한 것이 아니라 **측정된 힘 성분을 영상화한 표현**이다. 별도의 시각 Encoder와 TCP Pose·Wrench 등의 저차원 입력을 결합한 Diffusion Policy로 선반 인출을 수행하며, 센서 Ablation으로 분포형 촉각과 Wrench의 기여를 비교한다.

[**Tactile Gym 2.0**](../literature/papers/2022-lin-tactile-gym-2-0.md)의 센서별 영상 변환과 [**Bi-Touch**](../literature/papers/2023-lin-bi-touch.md)의 접촉 동역학 수정 작업은 **고차원 촉각 표현이 공간적인 접촉 정보를 정책에 전달하는 데 유효하지만, 시뮬레이션 학습을 실물로 이전하려면 영상 표현과 실제 접촉 반응을 함께 대응시켜야 한다는 점**을 보여준다.

### 2.2.3. 촉각을 저차원으로 표현하는 접근

이 접근은 비교적 단순한 데이터 후처리를 통해 촉각 정보를 단순화하여 행동 학습에 활용한다. 기존 문서에서 다룬 표현은 접촉 여부를 남기는 Binary와 연속 하중을 일부 보존하는 저차원 특징이다.

[**Zihan Ding et al. - Sim-to-Real Transfer for Robotic Manipulation with Tactile Sensory**](../literature/papers/2021-ding-sim-to-real-tactile-manipulation.md)는 그리퍼 양쪽 Finger Pad의 **30개 저항식 촉각 Element**와 시뮬레이션 접촉 신호를 모두 Binary로 축약하고, TD3 관측에 넣어 문 열기를 학습한다. 연속 센서 응답을 정밀하게 일치시키는 대신 접촉 여부를 공통 표현으로 사용하는 방식이며, 실물에서 촉각 사용 여부에 따른 문 열기 성능 차이를 확인했다. 이 결과는 **Binary 촉각을 추가한 효과**를 보여준다.

[**Zhao-Heng Yin et al. - Rotating without Seeing: Towards In-hand Dexterity through Touch**](../literature/papers/2023-yin-rotating-without-seeing.md)는 손가락과 손바닥의 **16개 FSR 접촉 Bit**를 관절 위치·이전 제어 목표·회전축 및 **4-Frame 이력**과 함께 사용해 시각 없이 손 안의 물체를 회전시킨다. 시뮬레이션 접촉 힘과 실제 FSR 출력을 이진화하여 관측 표현을 맞춘다. 이 연구의 특징은 단순한 접촉 Bit를 단독으로 사용하는 것이 아니라, **접촉 영역과 손의 움직임·명령 이력을 결합**한다는 점이다.

[**Kang-Won Lee et al. - DexTouch: Learning to Seek and Manipulate Objects With Tactile Dexterity**](../literature/papers/2024-lee-dextouch.md)는 손가락·손바닥의 **16개 FSR 신호를 부위별 Binary 접촉으로 변환**하고, 관절 상태·손바닥 Pose·손끝 위치·과업 사전정보와 함께 사용한다. PPO로 팔과 손을 함께 제어하여 물체 탐색·파지·운반, 문 열기, 밸브 회전을 과업별로 학습한다. 부위별 접촉 분포는 물체와 실제로 만난 위치를 행동에 반영하는 역할을 하며, 시뮬레이션 힘과 실물 전압의 정밀한 일치를 요구하지 않는 표현을 사용한다.

[**Xinyuan Zhao et al. - Unknown Object Retrieval in Confined Space through Reinforcement Learning with Tactile Exploration**](../literature/papers/2024-zhao-unknown-object-retrieval.md)는 Tool Stick의 **4×4 Taxel, Taxel당 3축 촉각**을 **9차원 연속 특징**으로 축약한다. 구성은 열별 법선력 최댓값 4개, 열별 절댓값이 가장 큰 x축 전단력 값 4개, 전단력 이력의 FFT로 얻은 고주파 특징 1개다. 따라서 공간 분포를 축약하면서도 **하중 크기와 일부 전단·시간 정보를 유지**한다. 물체 Pose나 명시적인 물성 추정치를 입력하지 않고 이 특징만으로 실물 SAC 정책을 학습한다.

Tactile 정보를 저차원화할 때는 **조작에 필요한 정보를 무엇까지 제거했는가**에 유의해야 한다.

### 2.2.4. 촉각 표현을 직접 비교한 연구

**같은 연구 안에서 표현을 바꾸어 비교한 결과**를 살펴본다. 특히 영상의 세부 표현을 단순화하는 것과, 접촉력을 Binary로 바꾸는 것을 구분한다.

[**Entong Su et al. - Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning**](../literature/papers/2024-su-sim2real-tactile-manipulation.md)는 DIGIT 촉각 영상을 **RGB·Diff·Binary**, 각각의 Augmentation 유무로 나누어 Pivoting 정책의 전이를 비교한다. 검토한 v1의 비증강 조건에서는 시뮬레이션 성공률이 유사했지만, 실물 성공률은 RGB 0.50, Diff 0.60, Binary 0.80으로 달랐다. 이 결과는 **영상 외형의 단순화가 실물 전이에 유효할 수 있다는 근거**를 제공한다.

[**Sim2Real Manipulation**](../literature/papers/2024-su-sim2real-tactile-manipulation.md)의 Binary는 **64×64 픽셀의 접촉 이미지**이며, 본 연구의 센서 영역별 1비트 접촉 벡터와는 공간 정보량이 다르다. 증강된 RGB의 실물 성공률은 76%, Binary는 증강 유무 모두 80%이므로 Binary가 모든 처리 조건보다 크게 우수하다는 뜻은 아니다. 저자들은 센서별 임계값을 grid search로 정하며, **잡음 감소와 유효한 접촉 정보 누락 사이의 trade-off**를 명시한다. (기존 Motivation의 비교 근거를 이관. 원문 §III-B·IV·V-B, Table I)

[**Boya Zhang et al. - The Role of Tactile Sensing for Learning Reach and Grasp**](../literature/papers/2025-zhang-role-of-tactile-sensing.md)는 2-Finger Reach-and-Grasp에서 **측정량**과 **공간 해상도**를 분리하여 비교한다. 전역 Binary(B)·힘 크기(M)·3축 힘 벡터(V), 그리고 K개 국소 영역별 BK·MK·VK가 비교 대상이다. 정확한 시각 정보에서는 촉각의 추가 효과가 작았지만, 시각 Pose에 잡음이 있으면 특히 **V와 VK가 유효**했고 국소 VK에 전역 V를 함께 제공한 구성도 국소 정보만 사용하는 구성보다 좋았다.

[**Jiahe Pan et al. - Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation**](../literature/papers/2026-pan-beyond-binary-cop-tactile.md)는 blind peg-in-hole에서 array별 Binary 접촉(전체 성공률 0.53)보다 **접촉 하중과 local contact position을 함께 보존한 CoP 표현(0.78)**이 높은 성공률을 보였고, OOD 초기조건에서도 0.20 대비 0.63을 기록했다. Raw taxel은 0.48로 CoP보다 낮았다. 이는 **Binary로 과도하게 축약하면 필요한 하중·공간 정보가 부족할 수 있고, raw tactile을 그대로 쓰는 것 역시 sim-to-real mismatch와 차원 문제를 가질 수 있음**을 같은 실물 과업에서 보여주는 근거다. 다만 이 연구의 force는 **XELA tactile taxel에서 복원한 local force**이며 별도 손목 F/T가 아니고, 실제 전이 실험에서는 shear simulation 불일치 때문에 surface-normal force만 사용했다. (기존 Motivation의 비교 근거를 이관. arXiv v1, §3.4·4.1·6, Table 1)

## 2.3. Reinforcement Learning

기존 연구의 **Reward Formulation이 어떤 행동을 유도하는지**를 중심으로 정리한다. 목표 달성, 접촉·하중 조절, 과업 단계의 진행을 구분하며, 보상 계산에 사용하는 물체 정답이나 외부 측정값을 실행 정책의 관측과 혼동하지 않는다. 수식과 설명은 연결한 상세 리뷰를 기준으로 한다.

### 2.3.1. Bi-Touch — 목표 위치·방위와 접촉면 정렬

[**Bi-Touch**](../literature/papers/2023-lin-bi-touch.md) — Lin et al., 2023. 여기서는 **Bi-pushing만** 다룬다. 보상은 **물체의 목표 위치**, **목표 방위**, **두 툴과 접촉면의 정렬**을 함께 고려한다.

```math
R_t^{\mathrm{BP}}=-w_1\lVert p_t^g-p_t^o\rVert_2-w_2S(\theta_t^g,\theta_t^o)-w_3\sum_{i=1}^{2}S(\theta_t^{e_i},\theta_t^o),\qquad S(\phi,\psi)=1-\cos(\phi-\psi).
```

$p_t^g,p_t^o$는 현재 목표와 물체의 위치, $\theta_t^g,\theta_t^o$는 각 방위, $\theta_t^{e_i}$는 각 툴 TCP의 방위다. 첫 두 항은 물체가 경로상의 위치·방위 목표를 따르게 하고, 마지막 항은 두 TacTip이 **접촉면에 수직으로 정렬된 밀기**를 유지하도록 유도한다.

따라서 이 보상은 목표점 도달만이 아니라 **어떤 자세로 물체를 미는가**를 함께 다룬다. 다만 마지막 항은 기하학적 정렬 항이며, 접촉력 추종이나 활성 촉각 수 보상이 아니다. Bi-reorienting·Bi-gathering의 접촉 위치 항은 여기에 포함하지 않는다. 가중치의 수치는 상세 리뷰에서 미명시로 정리되어 있다. (원문 §III-C-1, 식 (1))

### 2.3.2. Location-Based Attention Pushing — 목표 근접도와 장애물 충돌

[**Dengler et al. - Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention**](../literature/papers/2025-dengler-location-based-attention-pushing.md), 2025. 현재 목표에 가까워지는 정도와 종료 결과를 보상하고, 장애물과의 접촉을 벌점 처리한다.

```math
r_{\mathrm{total}}=r_{\mathrm{term}}+k_1(1-r_{\mathrm{dist}})+k_2(1-r_{\mathrm{ang}})+r_{\mathrm{coll}}.
```

$r_{\mathrm{dist}}$와 $r_{\mathrm{ang}}$는 각각 정규화된 **물체–목표 위치 거리와 방위 차이**다. 두 항은 이전 시점 대비 진행량이 아니라 **현재 목표 근접도**를 보상한다. $r_{\mathrm{term}}$은 성공 또는 작업영역 이탈에 따른 종료 보상이고, $r_{\mathrm{coll}}$은 Pusher나 대상 물체가 장애물에 접촉한 시점의 Binary 페널티다.

밀기에 필요한 Pusher–대상 물체 접촉 전체를 금지하거나, 접촉력의 크기에 비례해 벌점을 주는 구조는 아니다. 이 연구는 F/T·촉각 관측 대신 물체 Pose와 장애물 정보를 사용하는 밀기 사례로 구분한다. (원문 §III-B.3, 식 (1), §IV-A)

### 2.3.3. Precision-Focused Pushing — 목표 허용범위의 희소 보상

[**Bergmann et al. - Precision-Focused Reinforcement Learning Model for Robotic Object Pushing**](../literature/papers/2025-bergmann-precision-focused-pushing.md), 2025. 물체 중심이 목표 위치의 허용범위에 들어왔는지만으로 보상을 구성한다.

```math
r(p_o,p_g)=\begin{cases}-1,&\lVert p_o-p_g\rVert_2\ge 0.01\ \mathrm{m}\\0,&\text{otherwise}.\end{cases}
```

$p_o,p_g$는 물체 중심과 목표 위치다. 목표에서 **1 cm 이상 떨어지면 매 Step −1**, 범위 안에서는 0을 준다. 별도의 방위 정렬·접촉력·촉각 활성 보상은 포함하지 않는다.

목표에 일찍 도달해도 즉시 종료하지 않고, 고정된 Episode의 **마지막 시점에도 목표 범위 안에 있어야 성공**으로 판정한다. 이 조건은 목표를 잠시 통과한 뒤 다시 밀어내는 경우와 최종 위치를 유지한 경우를 구분한다. 보상에 사용하는 정답 중심 좌표는 Actor 입력이 아니며, 정책은 시각 특징과 EEF 위치를 사용한다. (상세 리뷰 §11–12)

### 2.3.4. Unknown Object Retrieval — 전진 진행량과 접촉 하중 조절

[**Unknown Object Retrieval**](../literature/papers/2024-zhao-unknown-object-retrieval.md) — Zhao et al., 2024. 목표 방향으로 물체를 꺼내는 진행량과 접촉 하중을 함께 고려한다.

```math
r=r_t+r_o+r_f+r_g+r_p.
```

$r_t$는 시간 페널티, $r_o$는 **현재 Step의 물체 전진 변위**에 비례하는 보상, $r_f$는 촉각 법선력 보상이다. $r_g$는 목표 인출 거리 달성 시의 보상이며, $r_p$는 후퇴·조정 Primitive 이후 정해진 시간 안에 재접촉하지 못했을 때의 페널티다. Primitive 실행에도 동등한 이동에 필요한 시간 비용을 반영한다.

접촉 하중 항은 최대 촉각 법선력 $f_n^{\max}$를 세 구간으로 나눈다.

```math
r_f=\begin{cases}0,&f_n^{\max}<f_n^l\\r_f^h,&f_n^{\max}>f_n^h\\(f_n^{\max}-f_n^l)^2,&\text{otherwise}.\end{cases}
```

하한 $f_n^l$ 미만에서는 보상하지 않고, 하한과 상한 $f_n^h$ 사이에서는 위 제곱 항을 주며, 상한을 넘으면 음수인 $r_f^h$를 적용한다. **접촉을 모두 줄이기보다 필요한 하중을 형성하도록 유도하면서 과도한 누름은 제한**하는 구성이다. 상한 초과 시에는 보상과 별도로 누름을 해제하는 동작도 사용하므로, 하중 제한을 보상 하나의 효과로 설명하지 않는다.

전진 변위는 학습 중 OptiTrack으로 측정하지만 실행 정책에는 입력하지 않는다. 또한 재접촉 실패 페널티는 **조정 후 접촉 회복**에 관한 것이며, 모든 순간의 접촉 소실을 동일하게 벌점 처리하는 항은 아니다. (원문 식 (1)–(3), 상세 리뷰 §10.1–10.5)

### 2.3.5. Learning Force Control — 목표 오차·동작·하중·안전

[**Beltran-Hernandez et al. - Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots**](../literature/papers/2020-beltran-hernandez-learning-force-control.md), 2020. 목표 Pose 도달과 함께 큰 동작·접촉 하중을 억제하고, 시간과 안전 결과를 반영한다.

```math
r(s,a)=w_1L_m\left(\left\|x_e/x_{\max}\right\|_{1,2}\right)+w_2L_m\left(\left\|a/a_{\max}\right\|_2\right)+w_3L_m\left(\left\|F_{\mathrm{ext}}/F_{\max}\right\|_2\right)+w_4\rho+w_5\kappa.
```

$x_e$는 목표 Pose 오차, $a$는 Action, $F_{\mathrm{ext}}$는 접촉 하중이며 각각 기준값으로 정규화한다. $L_m$은 보상 범위로의 선형 매핑, $\rho$는 Step·시간 페널티, $\kappa$는 과업 완료·안전 위반 결과를 나타낸다. **목표 오차 감소, 동작 크기 억제, 낮은 상호작용 하중, 빠른 완료, 안전 위반 회피**를 함께 고려하는 구조다. 개별 가중치와 정규화 기준의 수치는 상세 리뷰에서 미명시로 정리되어 있다.

하중 항은 특정 목표 힘과의 추종 오차가 아니라 **측정된 접촉 하중의 크기**에 작용한다. 안전 위반 페널티와 별도로 명령 유효성 검사·힘 한계 초과 시 종료하는 Fail-safe를 사용하므로, 보상과 안전 감독도 구분한다. (상세 리뷰 §17–20)

### 2.3.6. DexTouch — 접근과 과업별 진행의 분리

[**DexTouch**](../literature/papers/2024-lee-dextouch.md) — Lee et al., 2024. 보상은 **접근 보상**과 **과업 실행 보상**으로 구성하고, 급격한 동작을 억제하기 위한 관절 속도의 L1 Norm 페널티를 추가한다.

공통 접근 항은 손끝이 물체에 대해 달성한 최고 근접 기록을 갱신할 때 보상한다.

```math
r_{\mathrm{reach}}=\sum_{\mathrm{finger}}\alpha_{\mathrm{reach}}\max(d_{\mathrm{closest}}-d,0).
```

$d$는 현재 손끝–물체 거리, $d_{\mathrm{closest}}$는 지금까지 달성한 최소 거리다. 따라서 물러났다가 이미 도달했던 거리로 돌아오는 것만으로는 새 접근 보상이 생기지 않는다. 이전 Step 대비 거리 차분과도 구분된다.

실행 보상은 **파지·운반에서는 들어 올린 높이와 이후 목표 운반 진행**, **문 열기에서는 손잡이 회전 이후 문 열림 진행**, **밸브에서는 최대 회전각 기록 갱신**을 반영한다. 과업 단계의 달성 보너스도 사용한다. 즉 촉각을 관측한다고 해서 보상이 활성 센서 수로 정의되는 것은 아니며, 이 논문의 핵심은 **접근과 실제 물체 조작의 진행을 분리해 보상하는 것**이다. (원문 §IV-B, 식 (1)–(4), 상세 리뷰 §8)

### 2.3.7. Sim-to-Real Transfer — 파지 유지와 활성 촉각 수

[**Sim-to-Real Transfer for Robotic Manipulation with Tactile Sensory**](../literature/papers/2021-ding-sim-to-real-tactile-manipulation.md) — Ding et al., 2021. 문 열기 보상은 다음 다섯 항으로 구성된다.

```math
R=\omega_{\mathrm{door}}r_{\mathrm{door}}+\omega_{\mathrm{dist}}r_{\mathrm{dist}}+\omega_{\mathrm{ori}}r_{\mathrm{ori}}+\omega_{\mathrm{grasp}}r_{\mathrm{grasp}}+\omega_{\mathrm{tactile}}r_{\mathrm{tactile}}.
```

$r_{\mathrm{door}}$는 **파지가 유지될 때의 문 경첩 각도**, $r_{\mathrm{dist}}$는 Gripper–손잡이 거리, $r_{\mathrm{ori}}$는 Gripper와 목표 방위의 정렬을 반영한다. $r_{\mathrm{grasp}}$는 **양손가락이 손잡이와 접촉한 파지 상태**를 보상한다.

촉각 항은 활성 Binary 촉각 Unit의 수를 사용한다.

```math
r_{\mathrm{tactile}}=\|\hat{\mathbf{c}}\|_1.
```

이 항은 **파지 상태이며 문 열림 각도가 시작 기준을 넘었을 때** 적용한다. 따라서 아무 물체나 많이 접촉하면 항상 보상을 주는 것이 아니라, **과업에 필요한 파지를 유지하며 문을 여는 구간에서 접촉 영역을 넓히도록 유도**하는 구조다. 문 각도 자체를 보상하는 항과 활성 촉각 수를 보상하는 항을 구분한다. (원문 §IV-C-c, 식 (4)–(9), 상세 리뷰 §5.4–5.5)

### 2.3.8. 접촉 유지 보상과 촉각 개수 보상의 구분

| 구분 | 해당 연구와 항 | 실제 보상 조건 |
| --- | --- | --- |
| **접촉·파지 상태 유지** | [**Sim-to-Real Transfer**](../literature/papers/2021-ding-sim-to-real-tactile-manipulation.md)의 $r_{\mathrm{grasp}}$ | 양손가락이 손잡이와 접촉한 현재 파지 상태를 보상. 접촉 시간을 별도 변수로 누적하는 식은 아님 |
| **활성 촉각 수** | [**Sim-to-Real Transfer**](../literature/papers/2021-ding-sim-to-real-tactile-manipulation.md)의 $r_{\mathrm{tactile}}$ | 파지 상태이며 문 열림이 시작된 조건에서 활성 Binary Unit 수를 보상 |

[**Bi-Touch**](../literature/papers/2023-lin-bi-touch.md)의 툴–접촉면 정렬, [**Unknown Object Retrieval**](../literature/papers/2024-zhao-unknown-object-retrieval.md)의 하중 구간·재접촉 실패, [**DexTouch**](../literature/papers/2024-lee-dextouch.md)의 손끝 거리 항은 접촉에 관련되지만, 위 두 보상과 같은 식은 아니다. **접촉 여부·접촉 하중·접촉 기하·활성 센서 수 중 무엇을 직접 보상하는지**를 구분해야 한다.

## 2.4. 선행연구의 Domain Randomization

기존에 검토한 다섯 연구의 Randomization 대상을 **물리·초기 조건**과 **관측·명령 불확실성**으로 나누어 정리한다. 구체적인 수치 범위는 상세 리뷰에서 확인한다.

### 2.4.1. 물체·환경·로봇 조건

| 연구 | 물체·환경·과업 | 로봇·제어·외란 |
| --- | --- | --- |
| [**Rotating without Seeing**](../literature/papers/2023-yin-rotating-without-seeing.md) | 물체 질량·마찰<br>형상 배율·초기 위치 | Hand 마찰<br>PD Gain·외력 |
| [**Beyond Binary**](../literature/papers/2026-pan-beyond-binary-cop-tactile.md) | Peg·Ball·Plate 질량<br>물체·접촉면 마찰<br>물체 초기 위치·방향(과업별) | Hand 초기 Pose·관절 상태<br>Hand 마찰·PD Gain |
| [**Sim-to-Real Transfer**](../literature/papers/2021-ding-sim-to-real-tactile-manipulation.md) | 문·손잡이 질량, 손잡이 마찰<br>경첩 Stiffness·Damping·Friction loss<br>Table의 XY 위치 | 로봇 파라미터는 동정 후 고정 |
| [**DexTouch**](../literature/papers/2024-lee-dextouch.md) | 물체·문·밸브 초기 위치<br>물체·밸브 초기 Orientation | — |
| [**Sim2Real Manipulation**](../literature/papers/2024-su-sim2real-tactile-manipulation.md) | 물체 형상·길이, 지지면 높이<br>초기 물체 각도·목표 상대 각도 | — |

### 2.4.2. 센서 관측·명령 불확실성

| 연구 | 촉각·접촉 관측 | 기타 관측·명령 |
| --- | --- | --- |
| [**Rotating without Seeing**](../literature/papers/2023-yin-rotating-without-seeing.md) | 활성 접촉 누락(Dropout)<br>센서 지연 | 관절 관측 잡음<br>Action 잡음 |
| [**Beyond Binary**](../literature/papers/2026-pan-beyond-binary-cop-tactile.md) | 접촉력 크기·방향 잡음<br>접촉 위치 잡음·접촉 관측 지연 | 관절 위치 관측 잡음 |
| [**Sim-to-Real Transfer**](../literature/papers/2021-ding-sim-to-real-tactile-manipulation.md) | Binary Bit Flip<br>관측 지연 | 촉각 외 관측 잡음<br>Gripper 외 Action 잡음<br>관측 지연 |

**—는 검토한 상세 리뷰에서 해당 항목의 DR 보고를 확인하지 못했다는 뜻이다.** 같은 이유로 DexTouch와 Sim2Real Manipulation에는 별도의 센서 잡음 DR 항목을 추가하지 않았다. 접촉 누락만 만드는 Dropout과 양방향으로 값을 반전하는 Bit Flip은 구분한다.
