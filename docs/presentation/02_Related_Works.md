# 2. Related Works

[발표 문서 안내](README.md) · [Research Motivation and Contributions](01_Research_Motivation.md) · [Method](03_Method.md)

> **문서 상태: 기존 문헌 정리의 재구성.** F/T·Tactile 관련 선행연구와 기존 DR 비교를 모은다. 본 연구의 Contribution은 [01 문서](01_Research_Motivation.md), 실행 설계는 [03 문서](03_Method.md)에서 다룬다. RL 정책 학습과 Reward Formulation의 추가 정리는 TODO로 남긴다.

## 2.1. F/T·Wrench를 활용하는 선행연구

### 2.1.1. 연속적인 하중 피드백과 조작

| 연구 | 확인된 내용 |
| --- | --- |
| [**Heins and Schoellig - Force Push: Robust Single-Point Pushing with Force Feedback**](../literature/papers/2024-heins-force-push.md) | 물체의 현재 Pose와 정확한 물성 모델 없이 접촉력 피드백으로 밀기를 수행한다. 힘의 방향으로 조향하고, 크기에 따라 접촉 회복과 과부하 시 속도 보정을 수행한다. |
| [**Beltran-Hernandez et al. - Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots**](../literature/papers/2020-beltran-hernandez-learning-force-control.md) | F/T 기반 interaction feedback을 EEF pose error·velocity와 함께 SAC observation에 넣고, parallel position/force 또는 admittance controller의 motion·gain을 학습한다. 같은 force signal을 reward와 fail-safe에도 사용하여 실물 precision insertion을 학습한다. Tactile과의 병용 우위나 Sweeping 성능을 검증한 연구는 아니다. |
| [**Brouwer et al. - Gentle Object Retraction in Dense Clutter Using Multimodal Force Sensing and Imitation Learning**](../literature/papers/2026-brouwer-gentle-object-retraction.md) | 분포형 촉각과 관절 토크 기반 추정 Wrench를 정책에 함께 사용한다. 저자들은 Wrench가 여러 접촉의 개별 하중을 구분하지 못하고, 촉각은 센서가 덮지 못한 접촉을 놓친다는 차이를 설명한다. |

[**Force Push**](../literature/papers/2024-heins-force-push.md)는 힘의 크기와 방향이 접촉 여부를 넘어 행동을 조절하는 데 사용되는 사례다. [**Gentle Object Retraction**](../literature/papers/2026-brouwer-gentle-object-retraction.md)은 촉각의 국소 접촉 정보와 Wrench의 전체 하중 정보가 서로 다른 관측 한계를 갖는다는 점을 보여준다.

### 2.1.2. 학습 정책의 Wrench 관측과 비교 결과

[2026-09-21 Wrist Wrench 조사](../literature/reviews/2026-09-21_wrist-wrench-manipulation-survey.md)는 기존 상세 리뷰 28편을 제외하고, 2022년 이후 RA-L·ICRA·IROS·RSS 연구에서 Wrench가 학습 정책의 관측에 들어가는 7편과 제어기·플래너 피드백으로 쓰이는 2편을 비교했다. 외장 F/T, 로봇 내장 F/T와 관절 토크 기반 말단 외력 추정을 구분하고, 실제로 사용한 성분이 6D Wrench인지 3D force 또는 Fz인지도 분리했다.

[FoAR](../literature/papers/2025-he-foar.md)는 flange와 gripper 사이의 외장 OptoForce에서 얻은 6D Wrench 약 2초 이력을 Transformer로 처리해 시각 특징과 결합하고, 접촉 예정 구간의 행동 보정에도 사용했다. 이는 외장 손목 F/T의 이력을 정책에 넣은 직접 사례다. 다만 실행 중 RGB-D를 계속 사용하고, FoAR와 vision-only 기준선은 센서뿐 아니라 fusion·predictor·reactive correction도 함께 다르다.

[Zero-Shot Transfer](../literature/reviews/2026-09-21_wrist-wrench-manipulation-survey.md#w4-zero-shot-transfer--초기-시각-이후-wrench고유감각-이력)는 초기 시각 이후 상대 EE pose와 추정 6D Wrench의 8시점 이력으로 삽입 행동을 선택했고, [Symmetry-aware RL](../literature/reviews/2026-09-21_wrist-wrench-manipulation-survey.md#w5-symmetry-aware-rl--ft행동-이력의-recurrent-policy)은 위치·F/T·행동 이력을 recurrent policy에 제공했다. 두 연구는 Wrench를 단일 시점 값보다 행동·운동의 시간 맥락과 함께 사용한 사례다.

F/T 관측의 효과는 과업에 따라 달랐다. [Comp-ACT](../literature/reviews/2026-09-21_wrist-wrench-manipulation-survey.md#w2-comp-act--ft-관측의-포함제거-비교)의 동일 논문 내 포함·제거 비교에서 F/T를 포함한 정책은 세 삽입 과업에서 성공률이 높았지만 wiping은 70% 대 100%로 낮았고 drawing은 같았다. 따라서 **Wrench가 접촉 조작의 행동 선택에 유용할 수 있다는 근거는 있으나, 항상 성능을 높이거나 접촉 위치·물체 상태를 유일하게 복원한다는 근거는 아니다.**

또한 이 조사에는 Binary 촉각과 Wrist Wrench의 역할을 같은 조건에서 직접 분리한 실험이 없다. Binary 또는 희소 촉각과 손목 F/T를 결합했을 때 두 입력의 기여를 구분한 근거는 추가 확인이 필요하다.

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

[**Gentle Object Retraction**](../literature/papers/2026-brouwer-gentle-object-retraction.md)는 도구 양 측면의 분포형 3축 촉각을 **20×5×3 Force Image**로 표현하고, 촉각 전용 ResNet-18로 인코딩한다. 이 영상의 채널은 광학 촉각 카메라의 색을 관측한 것이 아니라 **측정된 힘 성분을 영상화한 표현**이다. 별도의 시각 Encoder와 TCP Pose·Wrench 등의 저차원 입력을 결합한 Diffusion Policy로 선반 인출을 수행하며, 센서 Ablation으로 분포형 촉각과 Wrench의 기여를 비교한다.

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

### 2.3.1. RL 기반 정책 학습 — TODO

> **TODO:** 기존 접촉 기반 조작 연구에서 RL 정책을 어떻게 학습했는지 정리할 예정이다. 이번 재구성에서는 내용을 채우지 않는다.

### 2.3.2. 선행연구의 Reward Formulation — TODO

> **TODO:** 기존 연구들의 Reward Formulation을 정리할 예정이다. 이번에는 항목만 마련하며, 보상식·보상 항·가중치 등의 내용은 채우지 않는다.

## 2.4. 선행연구의 Domain Randomization

이미 검토한 RL 기반 연구에서는 물체·환경·로봇·센서 조건을 다양하게 무작위화하여 학습한다. 여기서는 **각 연구가 어떤 항목을 Randomization 했는지만 정리하며, 구체적인 수치 범위는 생략한다.**

| 연구 | Randomization 대상 |
| --- | --- |
| [**Rotating without Seeing**](../literature/papers/2023-yin-rotating-without-seeing.md) | 물체 질량·마찰·형상·초기 위치, Hand 마찰, PD Gain, 외력, 관절 관측 잡음, Action 잡음, Tactile Dropout·지연 |
| [**Beyond Binary**](../literature/papers/2026-pan-beyond-binary-cop-tactile.md) | 물체 질량·마찰, 물체·Hand 초기 Pose, Hand 초기 관절 상태·마찰, PD Gain, 관절 관측 잡음, Contact Force·Position 잡음, Contact Observation 지연 |
| [**Sim-to-Real Transfer**](../literature/papers/2021-ding-sim-to-real-tactile-manipulation.md) | 손잡이 마찰, 문 경첩 Stiffness·Damping·Friction, 문·손잡이 질량, 환경 위치 Offset, Observation·Action 잡음, Observation 지연, Binary Tactile Bit Flip |
| [**DexTouch**](../literature/papers/2024-lee-dextouch.md) | 물체·문·밸브의 초기 위치, 물체·밸브의 초기 Orientation |
| [**Sim2Real Manipulation**](../literature/papers/2024-su-sim2real-tactile-manipulation.md) | 물체 형상·길이, 지지면 높이, 초기 물체 자세, 목표 자세 |
