# 2. Tactile Representation and Sweeping Policy Design

[이전 문서: Research Motivation](01_Research_Motivation.md)

> **문서 상태: 연구 설계 초안.** 선행연구에서 확인된 내용과 본 연구의 설계 제안을 구분한다. 비교 근거가 확보되지 않은 항목은 **추가 조사 필요**로 남긴다.

<<<<<<< HEAD
=======
(지시 사항: 문서의 풀 네임을 언급할 때는, 저자 - 논문 제목 형태로서 언급하고, 재언급시는, 츄축약 제목 형태로 언급할 것. 반드시 상대 경로 참조로 걸어둘 것)

(추가 지시 사항: Reference를 찾아야 한다고 명시한 것은, 이미 레포에 존재하는 논문을 근거로 삼으라는 의미가 아니다. 이런 관련 연구를 찾아야 한다는, TODO 성의 코멘트이다. 지금 찾지 않는다.)

<<<<<<< HEAD
>>>>>>> b2731ec (Refine tactile representation and policy design document with additional instructions and clarifications)
=======
>>>>>>> b2731ec (Refine tactile representation and policy design document with additional instructions and clarifications)
## 2.1. 연구 질문

[첫 번째 문서](01_Research_Motivation.md)에서는 초기 시각 관측 이후 물체 상태를 지속적으로 갱신할 수 없는 상황에서, **영역별 Binary 촉각과 손목 F/T를 결합하는 Blind Sweeping**을 연구 방향으로 제시했다.

이 문서에서는 그 방향을 다음 질문으로 구체화한다.

> **기존 촉각 표현은 조작에 필요한 정보를 어떻게 제공하며, 본 연구의 제한된 촉각 관측에서 부족한 정보를 손목 Wrench와 행동·관측 이력으로 얼마나 보완할 수 있는가?**

연구의 목표는 모든 접촉 상태와 물체 물성을 완전히 복원하는 것이 아니다. 초기 정보 이후의 상호작용을 관측하고, **물체를 목표 방향으로 이동시키면서 필요한 접촉을 유지하고 적절한 하중을 인가하는 행동**을 학습하는 것이다.

따라서 **촉각의 어떤 정보가 축약되거나 관측되지 않으며, F/T가 그중 무엇을 보완하는지**를 정의하고 실제 기여를 비교 실험으로 검증한다.

---

## 2.2. 기존 연구는 Tactile 정보를 어떻게 사용하는가?

촉각 활용 방식은 **명시적 상태 추정**, **고차원 영상 인코딩**, **저차원 접촉 표현**의 세 방향으로 정리한다. 이어서 2.2.4절에서는 표현을 직접 비교한 연구를 통해, 어떤 정보를 남기거나 제거하는 것이 조작과 실물 전이에 유효했는지 살펴본다.

### 2.2.1. Contact Point·Pose·Shape 등을 명시적으로 추정하는 접근

이 접근은 촉각 신호를 바로 행동으로 연결하기보다, **접촉 위치·접촉면 자세·물체 자세와 같은 해석 가능한 상태로 변환한 뒤 제어에 활용**한다. 여기서는 각 연구가 실제로 추정하는 대상과, 제한된 관측에 대응하는 방법을 구분한다.

[**Max Yang et al. - Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing**](../literature/papers/2023-yang-sim-to-real-tactile-pushing.md)는 TacTip 영상에서 **접촉 깊이와 각도**를 추정하고, 이를 로봇·목표 정보와 결합하여 밀기 정책 또는 동역학 모델의 입력으로 사용한다. 촉각의 국소 관측으로 물체 중심과 전체 형상·물성을 얻기 어렵다는 문제에 대해, **물체 전체 상태를 복원하는 대신 접촉면의 자세와 접촉 위치를 제어 대상으로 선택**한다. 접촉면에 수직으로 밀도록 정렬하면서 접촉 위치를 목표로 이동시키는 방식이며, 성공 판정도 물체 중심의 목표 도달과 구분된다. 즉, 이 연구의 대응은 모호한 전체 상태를 모두 추정하는 것이 아니라 **관측·제어 대상을 국소 접촉 관계로 한정하는 것**이다. (원문 §III-B–C)

[**John Lloyd and Nathan F. Lepora - Pose-and-shear-based tactile servoing**](../literature/papers/2024-lloyd-pose-and-shear-based-tactile-servoing.md)는 **접촉 자세와 접촉 이후의 Shear 변형**을 함께 추정한다. 여기서 Shear는 접선 방향 변위와 비틀림이며, 뉴턴 단위의 전단력이나 손목 Wrench가 아니다. 이 연구는 미끄러짐 때문에 서로 다른 접촉·Shear 상태가 유사한 영상을 만드는 **Tactile aliasing**을 명시적으로 다룬다. 하나의 상태값만 출력하는 회귀 대신 **평균과 불확실성을 출력하는 Gaussian-density network(GDN)**를 사용하고, 로봇 운동학에 따른 시간적 예측과 **SE(3) Bayesian filtering**으로 결합한다. 따라서 현재 영상만으로 확정하기 어려운 상태를 불확실성과 시간 정보를 이용해 제어에 활용하는 접근이다. (원문 §1, §3.1–3.3, §6.1)

[**Idil Ozdamar et al. - Pushing in the Dark: A Reactive Pushing Strategy for Mobile Robots Using Tactile Feedback**](../literature/papers/2024-ozdamar-pushing-in-the-dark.md)는 모바일 베이스의 정전용량 촉각에서 **대표 접촉점**을 계산한다. Taxel별 신호를 저역통과 필터와 임계값으로 처리한 뒤, 하나만 활성화되면 해당 Taxel의 위치를, 여러 개가 활성화되면 접촉 영역 **양 끝 Taxel 위치의 중점**을 사용한다. 이는 하중 가중 중심이나 물체 중심의 추정이 아니다. 물체의 Pose·형상·물성을 직접 복원하지 않고, 알려진 센서 배치와 Point/Line contact 근사를 이용하여 접촉을 하나의 제어 변수로 축약한다. 접촉점이 범퍼 가장자리로 이동하면 횡이동으로 재정렬하고 회전을 제한하여 접촉 소실에 대응한다. 다만 Point/Line 전환 자체가 계산된 접촉점의 불연속을 만들 수 있으며, 이를 확률적 상태 추정기로 해소한 연구는 아니다. (원문 §II-B–C, §III-B, §IV)

이 세 연구에서 관측의 제한에 대응하는 방식은 각각 **추정·제어 대상의 한정**, **불확실성 추정과 시간적 필터링**, **대표 접촉점 모델과 반응형 제어**다. 따라서 공통된 시사점은 **국소 접촉 상태를 얻는 것과 전체 물체 상태·작용 하중을 확보하는 것은 다르며, 추정값의 의미는 사용한 센서 정보와 모델에 의해 결정된다**는 것이다.

특히 [**Pushing in the Dark**](../literature/papers/2024-ozdamar-pushing-in-the-dark.md)처럼 센서 위치와 활성 영역을 알면 간단한 접촉점 계산은 가능하다. 따라서 Binary 관측으로 접촉 추정 자체가 불가능하다고 단정하지 않는다. 본 연구에서 구분해야 할 것은 **영역별 접촉 여부에는 센서 내부의 세부 접촉 형상·변형 분포가 남지 않으므로, 그 분포를 입력으로 사용하는 영상 기반 Pose 추정기를 그대로 적용할 수 없다는 점**이다.

이에 따라 본 연구에서는 정밀한 접촉 Pose 복원을 필수 전처리로 두기보다, **관측 가능한 접촉 영역과 연속적인 하중 반응을 행동 결정에 직접 제공하는 방향**을 제안한다.

> **추가 조사 필요:** 물체 전체 Pose·Shape 추정 연구의 사전 형상 모델, 접촉 횟수, 탐색 동작, 시간 이력과 실패 조건. 위 세 연구의 국소 접촉 표현만으로 전체 Pose·Shape 추정 계열의 한계를 일반화하지 않는다.

### 2.2.2. 고차원 Tactile Image를 인코딩하여 사용하는 접근

이 접근은 **촉각 영상 또는 분포형 촉각을 영상 형태로 표현한 입력**을 Encoder로 처리하고, 생성된 특징을 정책에 제공한다. 접촉점이나 자세 하나로 먼저 축약하지 않고, 공간적인 접촉 패턴·변형·하중 분포를 행동 학습에 활용한다.

[**Yijiong Lin et al. - Tactile Gym 2.0: Sim-to-Real Deep Reinforcement Learning for Comparing Low-Cost High-Resolution Robot Touch**](../literature/papers/2022-lin-tactile-gym-2-0.md)는 TacTip, DIGIT, DigiTac을 같은 Sim-to-Real 방법론에서 비교한다. 실제 촉각 영상을 **시뮬레이션의 Depth-image 표현으로 변환하는 GAN**과 PPO 정책을 결합하여 Edge-following, Surface-following, Pushing을 수행한다. 센서마다 영상 외형뿐 아니라 피부 형상·강성·접촉 거동이 다르므로, 센서별 데이터 수집·영상 변환·정책 학습이 필요하다. 하나의 변환 모델과 정책을 모든 센서에 그대로 교체 적용한 결과는 아니다. (원문 §III-B–F, §IV)

[**Yijiong Lin et al. - Bi-Touch: Bimanual Tactile Manipulation With Sim-to-Real Deep Reinforcement Learning**](../literature/papers/2023-lin-bi-touch.md)는 두 TacTip 영상을 각각 **Real-to-Sim GAN**으로 변환하고, 영상 특징과 고유감각·목표 정보를 PPO 정책에 제공하여 양팔 밀기·재정렬·모으기를 수행한다. 그러나 실물 재정렬에서는 시뮬레이션과 실제 접촉 동역학의 차이로 과도한 압착이 발생하여, 시뮬레이션 센서 동역학과 학습 조건을 수정했다. 이는 **영상 관측을 변환하는 것만으로 실제 접촉 반응까지 일치하는 것은 아니라는 사례**다. (원문 §III–V)

[**Dane Brouwer et al. - Gentle Object Retraction in Dense Clutter Using Multimodal Force Sensing and Imitation Learning**](../literature/papers/2026-brouwer-gentle-object-retraction.md)는 도구 양 측면의 분포형 3축 촉각을 **20×5×3 Force Image**로 표현하고, 촉각 전용 ResNet-18로 인코딩한다. 이 영상의 채널은 광학 촉각 카메라의 색을 관측한 것이 아니라 **측정된 힘 성분을 영상화한 표현**이다. 별도의 시각 Encoder와 TCP Pose·Wrench 등의 저차원 입력을 결합한 Diffusion Policy로 선반 인출을 수행하며, 센서 Ablation으로 분포형 촉각과 Wrench의 기여를 비교한다. 다만 **실제 시연 기반 모방학습**이므로, 고차원 촉각 인코딩의 활용 사례로 포함하되 이 논문이 Sim-to-Real 전이의 어려움을 직접 검증했다고 해석하지 않는다. (원문 §III-B, §IV–V, Fig. 3)

**종합하면, 고차원 촉각 표현은 공간적인 접촉 정보를 정책에 전달하는 데 유효하지만, 시뮬레이션 학습을 실물로 이전하려면 영상 표현과 실제 접촉 반응을 함께 대응시켜야 한다.** [**Tactile Gym 2.0**](../literature/papers/2022-lin-tactile-gym-2-0.md)의 센서별 영상 변환과 [**Bi-Touch**](../literature/papers/2023-lin-bi-touch.md)의 접촉 동역학 수정은 이 대응에 별도 작업이 필요함을 보여준다. 문제의 초점은 Encoder 자체의 부적절함이 아니라 **센서 고유의 영상·변형·접촉 특성을 두 환경에서 일관되게 제공하는 부담**에 있다.

이에 본 연구에서는 고해상도 촉각 영상의 정밀 재현에 대한 의존도를 낮추고, **영역별 접촉 여부는 촉각으로, 연속적인 합력·합모멘트는 F/T로 제공하는 구성**을 제안한다.

> **추가 조사 필요:** 고차원 영상 인코딩과 Binary–Wrench 표현의 학습 효율, 추론 지연, 데이터 요구량 및 전이 성능을 동일 조건에서 비교한 근거. 위 사례만으로 고차원 표현의 일반적인 성능 열세나 본 제안의 우위를 확정하지 않는다.

### 2.2.3. 촉각을 저차원으로 표현하는 접근

저차원 표현에서는 입력 차원뿐 아니라 **접촉 여부만 남기는지, 연속 하중이나 대표 접촉 위치까지 남기는지**를 구분해야 한다.

**접촉 여부를 남기는 Binary 표현**

[**Zihan Ding et al. - Sim-to-Real Transfer for Robotic Manipulation with Tactile Sensory**](../literature/papers/2021-ding-sim-to-real-tactile-manipulation.md)는 그리퍼 양쪽 Finger Pad의 **30개 저항식 촉각 Element**와 시뮬레이션 접촉 신호를 모두 Binary로 축약하고, TD3 관측에 넣어 문 열기를 학습한다. 연속 센서 응답을 정밀하게 일치시키는 대신 접촉 여부를 공통 표현으로 사용하는 방식이며, 실물에서 촉각 사용 여부에 따른 문 열기 성능 차이를 확인했다. 다만 이 결과는 **Binary 촉각을 추가한 효과**이며, Binary가 연속 하중 정보보다 항상 우수하다는 뜻은 아니다. (원문 §IV–V, Table III)

[**Zhao-Heng Yin et al. - Rotating without Seeing: Towards In-hand Dexterity through Touch**](../literature/papers/2023-yin-rotating-without-seeing.md)는 손가락과 손바닥의 **16개 FSR 접촉 Bit**를 관절 위치·이전 제어 목표·회전축 및 **4-Frame 이력**과 함께 사용해 시각 없이 손 안의 물체를 회전시킨다. 시뮬레이션 접촉 힘과 실제 FSR 출력을 이진화하여 관측 표현을 맞춘다. 이 연구의 특징은 단순한 접촉 Bit를 단독으로 사용하는 것이 아니라, **접촉 영역과 손의 움직임·명령 이력을 결합**한다는 점이다. (원문 §III–V)

[**Kang-Won Lee et al. - DexTouch: Learning to Seek and Manipulate Objects With Tactile Dexterity**](../literature/papers/2024-lee-dextouch.md)는 손가락·손바닥의 **16개 FSR 신호를 부위별 Binary 접촉으로 변환**하고, 관절 상태·손바닥 Pose·손끝 위치·과업 사전정보와 함께 사용한다. PPO로 팔과 손을 함께 제어하여 물체 탐색·파지·운반, 문 열기, 밸브 회전을 과업별로 학습한다. 부위별 접촉 분포는 물체와 실제로 만난 위치를 행동에 반영하는 역할을 하며, 시뮬레이션 힘과 실물 전압의 정밀한 일치를 요구하지 않는 표현을 사용한다. 촉각 감도·배치와 사용 여부를 비교했지만, 해당 출판본은 동일 조건의 Binary 대 연속 촉각 비교를 제시하지 않는다. (원문 §III–V, Table II–III)

**연속 하중·대표 위치를 보존하는 저차원 표현**

[**Xinyuan Zhao et al. - Unknown Object Retrieval in Confined Space through Reinforcement Learning with Tactile Exploration**](../literature/papers/2024-zhao-unknown-object-retrieval.md)는 Tool Stick의 **4×4 Taxel, Taxel당 3축 촉각**을 **9차원 연속 특징**으로 축약한다. 구성은 열별 법선력 최댓값 4개, 열별 절댓값이 가장 큰 x축 전단력 값 4개, 전단력 이력의 FFT로 얻은 고주파 특징 1개다. 따라서 공간 분포를 축약하면서도 **하중 크기와 일부 전단·시간 정보를 유지**한다. 물체 Pose나 명시적인 물성 추정치를 입력하지 않고 이 특징만으로 실물 SAC 정책을 학습하며, Binary로 접촉 여부만 남기는 접근과 구분된다. (원문 §III-B.1)

[**Jiahe Pan et al. - Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation**](../literature/papers/2026-pan-beyond-binary-cop-tactile.md)는 촉각 Array별 접촉을 **합력과 대표 접촉 위치를 결합한 CoP**로 표현한다. 검토한 2026년 Preprint의 실물 Peg-in-Hole 실험에서는 CoP가 Binary보다 높은 전체 성공률을 보였다. 이는 단순한 접촉 여부를 넘어 하중·위치를 보존하는 것이 해당 과업에서 유효했던 근거다. 다만 힘은 **촉각 Array에서 복원한 국소 접촉력**이며 손목 F/T가 아니다. 실제 Sim-to-Real 실험에서는 전단 성분의 정합 문제 때문에 Surface-normal CoP Force를 사용했다. (원문 §3.4, §4.1, Table 1)

이처럼 [**Unknown Object Retrieval**](../literature/papers/2024-zhao-unknown-object-retrieval.md)과 [**Beyond Binary**](../literature/papers/2026-pan-beyond-binary-cop-tactile.md)는 저차원에서도 연속적인 하중 정보를 보존한다. 반면 영역별 Binary 표현은 접촉 영역을 남기지만, 같은 영역 안의 하중 크기·방향과 세부 접촉 위치를 표현하지 않는다. 따라서 핵심은 **저차원화 자체가 아니라, 조작에 필요한 정보를 무엇까지 제거했는가**다.

본 연구는 영역별 Binary 촉각을 사용하는 구성에서 제거되는 정보 중, **연속적인 전체 하중 정보를 손목 F/T로 보완하는 방향**을 제안한다. 촉각 자체의 연속 하중을 사용하는 기존 저차원 표현과는 정보의 취득 위치와 공간적 의미가 다르다.

### 2.2.4. 촉각 표현을 직접 비교한 연구에서 얻는 근거

앞의 세 절이 정보를 사용하는 방식을 정리했다면, 여기서는 **같은 연구 안에서 표현을 바꾸어 비교한 결과**를 살펴본다. 특히 영상의 세부 표현을 단순화하는 것과, 접촉력을 Binary로 바꾸는 것을 구분한다.

[**Entong Su et al. - Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning**](../literature/papers/2024-su-sim2real-tactile-manipulation.md)는 DIGIT 촉각 영상을 **RGB·Diff·Binary**, 각각의 Augmentation 유무로 나누어 Pivoting 정책의 전이를 비교한다. 검토한 v1의 비증강 조건에서는 시뮬레이션 성공률이 유사했지만, 실물 성공률은 RGB 0.50, Diff 0.60, Binary 0.80으로 달랐다. 저자들은 조명·색·젤 차이를 줄이고 접촉 패턴을 남기는 표현의 이점을 설명한다. 다만 여기서 Binary는 **센서별 1 Bit가 아니라 64×64 픽셀의 접촉 패턴**이다. 따라서 이 결과는 **영상 외형의 단순화가 실물 전이에 유효할 수 있다는 근거**이지, 센서 영역 전체를 하나의 Bit로 축약해도 같은 정보와 성능이 유지된다는 근거가 아니다. (원문 §III-B, §V-B, Table I)

[**Boya Zhang et al. - The Role of Tactile Sensing for Learning Reach and Grasp**](../literature/papers/2025-zhang-role-of-tactile-sensing.md)는 2-Finger Reach-and-Grasp에서 **측정량**과 **공간 해상도**를 분리하여 비교한다. 전역 Binary(B)·힘 크기(M)·3축 힘 벡터(V), 그리고 K개 국소 영역별 BK·MK·VK가 비교 대상이다. 정확한 시각 정보에서는 촉각의 추가 효과가 작았지만, 시각 Pose에 잡음이 있으면 특히 **V와 VK가 유효**했고 국소 VK에 전역 V를 함께 제공한 구성도 국소 정보만 사용하는 구성보다 좋았다. 이때 전역 V는 **촉각에서 얻는 3축 힘 표현**으로, 별도 손목 6축 Wrench와 동일하지 않다. (원문 §III-C, §IV-A–C, Fig. 7–8, Table III)

두 연구의 결과는 다음과 같이 구분해 본 연구에 연결한다.

| 비교 관점 | 선행연구에서 확인된 내용 | 본 연구 설계에 주는 근거 |
| --- | --- | --- |
| **영상의 외형과 접촉 패턴** | [**Sim2Real Manipulation**](../literature/papers/2024-su-sim2real-tactile-manipulation.md): RGB 세부를 줄이되 공간적 접촉 패턴을 남긴 Binary 영상이 해당 실물 Pivoting에서 유효 | 정밀한 영상 외형을 모두 유지할 필요는 없으나, 픽셀 단위 Binary와 영역별 Binary를 구분해야 함 |
| **하중의 크기·방향과 공간적 분포** | [**The Role of Tactile Sensing**](../literature/papers/2025-zhang-role-of-tactile-sensing.md): 잡음 있는 시각 조건에서 힘 벡터와 전역·국소 정보의 결합이 유효 | 접촉 여부만 남길 때 제거되는 연속 하중 정보의 가치를 검토해야 함 |

따라서 본 연구의 방향은 **모든 촉각 정보를 최대한 축약하는 것**이 아니라, **촉각으로 접촉 영역을 남기고 손목 F/T로 연속 하중을 추가하여, 단순한 관측 표현에서도 조작에 필요한 정보를 유지하는 것**이다. 두 비교 연구는 이 설계의 근거를 제공하지만, 각각 Pivoting과 Reach-and-Grasp의 결과이므로 본 Sweeping에서의 센서 결합 효과는 별도로 검증한다.

---

## 2.3. 본 연구에서 F/T를 추가하는 이유와 한계

### 2.3.1. F/T는 촉각을 대체하는 센서가 아니다

제안하는 역할 분담은 다음과 같다.

- **Binary 촉각:** 어느 감지 영역이 접촉했는지 제공
- **손목 Wrench:** 손목 센서를 통해 전달되는 전체 힘과 모멘트의 크기·방향·변화 제공
- **행동·고유감각 이력:** 이 관측이 어떤 명령과 실제 로봇 운동 이후 발생했는지 제공

(여기 부분의 근거는 추가 조사해야 하니, 현 시점에서는 내용을 작성하지 않는다. 논리 구조는 유지한다.)

---

## 2.4. Sweeping에서 중요하게 다뤄야 할 것은 무엇인가?

(
지시 사항 : 여기 내용은 전면 개편한다. 관련 연구를 2종류로 나눈다. (관련 리서치 필요)

- 주변 환경의 물성치를 추가하는 별도의 모델을 구축하는 방향의 논문
- 이력 데이터를 기반으로 정책이 환경 파라미터를 간접 추정하게 하는 방향의 논문

그리고, 우리는 후자를 사용한다. (적당한 이유를 만들어 볼 것)
그리고, 추가적인 강건성을 위해, 이 부분에 Domain Randomization 개념을 도입한다. (Ref 추가 필요. 검색은 보류한다.)

)

---

## 2.5. State와 Observation 설계


(지시 사항 : 여기 내용도 전면 개편한다. 구성 흐름은 다음과 같다.

- 우리가 제공하고자 하는 입력 차원
	- 이 중에서, "이력" 으로서 부여하고자 하는 차원과 그 이유 (Reference 필요)
- 추가적으로, 입력 차원은 아니지만, Privileged 하게 부여되는 정보와 그 이유 (Reference 필요)

)


### ~~2.5.1. 물리적 State와 정책 Observation을 분리한다~~

~~물리 환경에는 물체의 실제 Pose·속도·접촉 상태·물성 등이 존재하지만, Blind 실행 정책은 이를 모두 직접 관측하지 못한다.~~

~~본 초안에서는 물체·환경 파라미터를 포함한 물리적 State를 개념적으로 다음과 같이 둔다.~~

~~$$~~
~~s_t=(x_t,\phi),\qquad \phi=(\text{shape},\text{mass},\text{friction},\text{support configuration},\ldots).~~
~~$$~~

~~$x_t$는 시간에 따라 변하는 로봇·물체·접촉 상태이며, $\phi$는 해당 Episode의 물체·환경 조건이다.~~

~~그러나 Actor는 $s_t$ 전체가 아니라 제한된 관측을 받으므로, **정책의 문제는 부분 관측 문제로 구성한다.** 과거 관측을 추가하는 목적은 숨겨진 상태에 관한 정보를 보완하는 것이며, 유한 길이의 이력을 붙였다는 이유만으로 Markov 성질이 보장된다고 표현하지 않는다.~~

### ~~2.5.2. 현재 시점의 관측 후보~~

| 구성 | 관측 후보 | 설계상 역할 |
| --- | --- | --- |
| 초기 과업 정보 | 목표 방향·거리, 초기 대상 Pose, 제공 가능한 초기 크기·형상 정보 | 시작 조건과 수행 목표 |
| Arm 고유감각 | 관절 위치·속도, 실제 EEF Pose·Twist | 로봇이 실제로 어떻게 움직였는지 |
| Hand 고유감각 | 구동부 위치, 취득 가능한 속도·이전 목표 | 촉각 영역의 위치·자세와 손의 실제 반응 |
| 접촉 관측 | 영역별 Binary 촉각, 보정된 6축 Wrench | 감지된 접촉 영역과 전체 하중 |
| 이력·유효성 | 이전 적용 명령, 센서 Timestamp·유효 여부 | 행동과 반응의 대응, 무접촉과 데이터 누락의 구분 |

~~초기 물체 정보는 **Pose와 Shape를 별도로 명세**한다. 초기 Pose가 제공된다고 해서 정확한 CAD 형상이나 마찰까지 제공되는 것은 아니다.~~

~~또한 초기 물체 Pose를 현재 EEF 좌표계로 다시 표현할 수는 있지만, 이것은 **초기 위치에 대한 상대 좌표를 갱신한 것**이지 현재 물체 Pose를 관측한 것이 아니다.~~

~~현재 물체 GT Pose·속도·접촉 물체 ID·정확한 물성은 필요에 따라 Critic·Reward·평가에 사용할 수 있으나, 최종 Blind Actor 입력에는 포함하지 않는다.~~

### ~~2.5.3. Tactile뿐 아니라 행동과 로봇 상태의 이력을 함께 유지한다~~

~~Tactile 패턴의 변화만 저장하면, 그 변화가 어떤 동작 이후 나타났는지 알기 어렵다. 따라서 촉각과 Wrench를 **동일 시간대의 실제 EEF 운동·Hand 상태·적용 명령**과 연결한다.~~

~~현재 센서·고유감각 묶음을 $y_t$라고 하면, 순서를 보존하는 이력 후보는 다음과 같다.~~

~~$$~~
~~H_t=\left(y_{t-K+1:t},a^{\mathrm{applied}}_{t-K+1:t-1}\right).~~
~~$$~~

~~여기서 $a^{\mathrm{applied}}$는 정책의 원래 출력과 구분되는, 제한·변환을 거쳐 실제 제어기에 적용된 명령이다.~~

~~시간 이력의 활용 사례로 [**Rotating without Seeing**](../literature/papers/2023-yin-rotating-without-seeing.md)는 현재 상태와 이전 상태들을 함께 입력한다. 이는 촉각 Bit만의 누적이 아니라 관절 상태와 이전 제어 목표를 포함하는 이력이다.~~

~~**제안:** 현재 시점만 사용하는 정책을 기준선으로 두고, 순서를 보존한 짧은 이력을 추가하는 구성을 비교한다. 이력 길이와 샘플 간격은 임의로 확정하지 않고 실물 제어 주기·센서 지연·접촉 반응 시간에 맞춰 정한다.~~

### ~~2.5.4. Sliding-window Sum은 이력의 대체물이 아니라 요약 후보로 둔다~~

~~영역 $i$의 Binary 접촉을 $b_{t,i}$라고 하면, 최근 $K$개 관측의 접촉 비율을 다음과 같이 정의할 수 있다.~~

~~$$~~
~~\bar b_{t,i}=\frac{1}{K}\sum_{k=0}^{K-1}b_{t-k,i}.~~
~~$$~~

~~이 값은 일정한 샘플 간격에서 **최근 구간에 해당 영역이 얼마나 지속적으로 활성화되었는지**를 나타낸다. 순간적인 접촉 여부보다 지속성에 관한 정보를 추가하려는 제안이다.~~

~~그러나 합산은 시간 순서를 제거한다. 예를 들어 $(1,0,1)$과 $(0,1,1)$은 합계가 같지만 접촉 변화 순서는 다르다.~~

~~따라서 합산값만으로는 **접촉 유지, 소실 후 재접촉, 새 접촉 형성**을 충분히 구분하지 못할 수 있다.~~

~~**현재 설계 제안은 현재 Binary 값을 유지하면서 합산·평균값을 보조 특징으로 추가하는 것**이다. 순서 보존 이력을 대체하는 기본 표현으로 바로 확정하지 않는다.~~

> ~~**추가 조사 필요:** Tactile Window Sum·접촉 비율·접촉 지속시간 표현을 사용한 선행연구와, 본 Sweeping 과업에서 이러한 요약이 실제 성능을 개선하는지에 대한 비교.~~

### ~~2.5.5. Last EEF Pose는 실제 과거 관측과 연결한다~~

~~이전 EEF Pose를 넣는 목적은 단순히 입력 차원을 늘리는 것이 아니라, **명령에 대해 실제로 얼마나 움직였고 그때 접촉 관측이 어떻게 바뀌었는지**를 연결하는 것이다.~~

~~최근 $k$시점에 대한 실제 상대 운동은 다음과 같이 표현할 수 있다.~~

~~$$~~
~~\Delta T_{t,k}=(T^{S}_{E,t-k})^{-1}T^{S}_{E,t}.~~
~~$$~~

~~$T^{S}_{E,t}$는 선반 좌표계에서 표현한 실제 EEF Pose다. 이 상대 운동은 해당 구간의 촉각·Wrench·Hand 상태와 함께 사용한다.~~

~~단순히 $T_{t-1}$ 하나를 추가했다고 임의의 과거 상태를 조회할 수 있는 것은 아니다. 여러 시점의 정보를 활용하려면 **명시적인 관측 버퍼 또는 순환 상태**가 필요하다.~~

~~[**Beyond Binary**](../literature/papers/2026-pan-beyond-binary-cop-tactile.md)는 순환 정책과 여러 길이의 이력을 평탄화한 MLP를 비교한다. 이를 시간적 표현을 검토할 근거로 사용할 수 있지만, 본 Sweeping에서도 순환 구조가 반드시 우수하다고 확정하지 않는다.~~

### ~~2.5.6. 센서 전처리도 Observation 설계에 포함한다~~

~~실물 전이를 위해 Wrench는 **기준 좌표계·모멘트 기준점·부호·단위·부하 보정 방식**을 명확히 한다. 무접촉 상태의 자세 변화와 운동만으로 발생하는 센서 변화도 확인하여, 정책이 이를 물체 접촉 변화로 오해하지 않도록 구성한다.~~

~~촉각 역시 Binary 임계값뿐 아니라 센서 유효 상태와 시간 정보를 관리한다. **정상 무접촉, 감지 임계값 이하의 접촉, 비센서 부위 접촉, 통신 누락**을 모두 동일한 의미의 0으로 단정하지 않는다.~~

~~이는 관측을 늘리기 위한 부가 기능이 아니라, 정책이 학습한 신호와 실물에서 제공되는 신호의 의미를 맞추기 위한 설계 조건이다.~~

---

## 2.6. Action 설계

### ~~2.6.1. Cartesian 표현과 OSC 사용 여부를 분리한다~~

(지시 사항: Cartesian Space Action으로 제공한다는 정도의 내용으로 간단하게 수정. 왜? 에 대한 근거는 추후 추가)

~~Cartesian Space로 행동을 표현하는 것과 OSC로 실행하는 것은 별개의 선택이다.~~

~~Differential IK는 EEF 목표와 Jacobian을 이용하여 관절 목표를 계산한다. 반면 OSC는 동역학 정보를 이용한 Task-space 제어로, 특정 Pose 오차 동역학이나 방향별 힘·운동 제어 등을 구성할 때 사용된다. 따라서 **OSC를 사용하지 않아도 Cartesian 행동 표현을 유지할 수 있다.**~~

~~본 초안에서는 다음 구조를 채택한다.~~

~~$$~~
~~\text{Policy}\rightarrow\text{Cartesian motion command}\rightarrow\text{Differential IK}\rightarrow\text{Joint target}\rightarrow\text{Robot}.~~
~~$$~~

~~**채택 이유는 먼저 단순한 운동 실행 경로에서 접촉 관측의 기여를 검증하기 위해서다.** 최대 속도나 정밀한 힘 추종을 일차 목표로 두기보다, 접촉·하중 반응에 따라 운동을 조절하는 정책부터 구성한다.~~

~~다만 “빠르게 밀지 않으므로 OSC가 필요 없다”는 일반적인 결론을 내리지는 않는다. 특정 접촉력 추종이나 순응 동작이 요구된다면 제어 구조를 다시 검토해야 한다.~~

> **추가 조사 필요:** Joint-space Action 대비 Cartesian Action이 본 과업의 학습 효율·일반화·실물 전이에 실제로 유리한지. “정책이 이해하기 쉽다”는 설명은 현재 설계 동기이며 검증된 비교 결과가 아니다.

### 2.6.2. Arm Action: Cartesian 증분을 생성한다

Arm의 기본 행동 후보는 EEF의 위치·회전 증분이다.

$$
a_t^{\mathrm{arm}}=(\Delta p_x,\Delta p_y,\Delta p_z,\Delta\theta_x,\Delta\theta_y,\Delta\theta_z).
$$

각 성분에는 물리 단위의 크기 제한을 적용하고, 좌표계는 EEF 기준으로 일관되게 정의한다. ~~평면 Sweeping 실험에서 일부 회전 성분을 고정하는 안은 가능하지만, 이를 물체의 엄격한 무회전 제약과 동일시하지 않는다.~~

~~Differential IK의 한 구현 후보는 Damped Least Squares다. 동일 좌표계에서 표현된 작은 Task-space 변위 $\Delta\xi_t$에 대해 다음과 같은 관절 증분을 계산할 수 있다.~~

~~$$~~
~~\Delta q_t=J_t^{\mathsf T}(J_tJ_t^{\mathsf T}+\lambda^2I)^{-1}\Delta\xi_t.~~
~~$$~~

~~이는 기구학적 명령 변환이며, 접촉력을 직접 지정하는 식은 아니다. 관절 한계·특이점·속도 제한과 실제 관절 제어기의 응답은 별도로 처리한다.~~

~~F/T는 이 구조에서 **다음 Cartesian 명령을 선택하기 위한 정책 입력**으로 사용된다. 정책이 하중을 관측하고 동작을 줄이거나 보정할 수는 있지만, 이것만으로 특정 힘의 정확한 추종이나 안전성이 보장되지는 않는다. 독립적인 실물 안전 제한은 유지한다.~~

### 2.6.3. Hand Action: 직접 제어와 저차원 근사를 비교 후보로 둔다

(지시 사항: 이 부분은 확정이 아닌, 논의 해야 할 사항임을 명확하게 표기할 것.)

Hand의 행동 표현은 현재 논의하는 6개 구동 입력을 직접 제어하는 방식과, 사전 정의된 자세 변화로 근사하는 방식으로 나눈다. 

| 후보               | 행동 표현                                             | 표현 구조상 차이                          |
| ---------------- | ------------------------------------------------- | ---------------------------------- |
| **A. 6차원 직접 제어** | 각 구동부의 목표 또는 목표 증분                                | 부위별 접촉 조절 자유도를 유지하지만 탐색할 행동 공간이 커짐 |
| ~~**B. 1차원 열림–닫힘**~~ | ~~$u\in[0,1]$, 0은 닫힘·1은 열림~~                          | ~~행동을 사전 정의된 하나의 자세 변화 경로로 제한~~        |
| **C. 2차원 근사**    | $u_{\mathrm{fingers}},u_{\mathrm{thumb}}\in[0,1]$ | 나머지 손가락과 엄지의 자세 변화를 분리             |


> **추가 조사 필요:** Sweeping·비파지 조작에서 직접 관절 제어와 저차원 Hand Synergy를 비교한 연구. 현재 근거만으로 1차원·2차원 근사가 더 잘 학습된다거나, 6차원 제어가 반드시 필요하다고 결정하지 않는다.

---

## 2.7. Domain Randomization 설계

### 2.7.1. 목표는 특정 설정에 대한 의존도를 줄이는 것이다

본 연구에서는 물체·환경·로봇·Base 조건이 달라져도 동작하는 정책을 학습하기 위해 Domain Randomization을 적용하는 방향을 잡는다. 다만 **Randomization을 적용했다는 사실만으로 강건성이 확보됐다고 판단하지 않는다.**

[**Rotating without Seeing**](../literature/papers/2023-yin-rotating-without-seeing.md)는 물체 질량·마찰·크기·초기 위치, Hand 마찰, PD Gain과 센서·제어 불확실성을 무작위화한다. [**Beyond Binary**](../literature/papers/2026-pan-beyond-binary-cop-tactile.md) 역시 물체·초기 상태·제어·접촉 관측 조건의 변화를 학습에 포함한다. 이는 해당 파라미터를 검토할 근거지만, 논문의 수치 범위를 본 플랫폼에 그대로 옮기는 근거는 아니다.

반대로 [**Yang et al.의 Tactile Pushing**](../literature/papers/2023-yang-sim-to-real-tactile-pushing.md)는 Domain Randomization 없이도 미지 물체에 적용한 결과를 보고한다. 따라서 DR은 모든 전이에 필수인 보편 조건이 아니라, **본 연구에서 예상하는 변화에 대비하기 위한 설계 수단**으로 위치시킨다.

### 2.7.2. 네 가지 Randomization 대상

| 구분            | Randomization 후보                        | 본 연구에서 확인할 내용                   |
| ------------- | --------------------------------------- | ------------------------------- |
| **환경 파라미터**   | Object–Shelf 마찰, 선반 접촉 특성, 허용 범위의 지지 조건 | 같은 물체에서도 지지면 조건이 달라질 때 적응하는가    |
| **물체 파라미터**   | 종류·형상·크기·질량·질량중심·관성·초기 Pose             | 접촉 기하와 하중 반응 변화에 대응하는가          |
| **로봇 파라미터**   | 시작 관절 상태·Hand 자세·제어 Gain·명령 지연·추종 오차    | 특정 로봇 자세나 제어 응답에 과도하게 의존하는가     |
| **Base 파라미터** | 선반에 대한 Base 위치와 허용 방향 오차                | 접근 가능한 자세와 작업 공간 관계가 달라져도 수행하는가 |

위 항목은 **본 연구의 후보 목록**이다. 물체별 모든 파라미터를 독립적으로 넓게 무작위화하는 것이 목적은 아니다.
### 2.7.3. Base Randomization은 좌표 이동과 구분한다

(지시 사항: Base Randomization은, XY 평면 상에서만 이루어지며, 수행하는 목적이 Base가 이동해와서, 정지한 위치가 매번 다를 수 있기 때문임을 명시. 상위 단과 연결되어야 의미가 있으나, 상위단에 대한 설명은 생략한다.)

~~본 연구에서 의미 있는 Base Randomization은 **선반에 대한 Base의 상대 위치·자세를 변화시키는 것**이다. 로봇·선반·물체를 모두 동일하게 평행 이동시키는 것은 상대적인 작업 조건을 바꾸지 않으므로 별개의 문제다.~~

~~Base를 변경한 뒤에는 시작 상태의 도달 가능성, 관절 한계, 충돌 여부, 접근 완료 조건을 확인한다. Episode마다 고정된 Base 조건을 바꾸는 것과, 실행 중 Base가 움직이는 동적 과업도 구분한다.~~

~~또한 다음 두 경우를 섞지 않는다.~~

- ~~**실제 Base 배치 변화:** 변경된 Base–Shelf 변환을 로봇이 알고 있다고 설정할 수 있다.~~
- ~~**Base 위치 추정 오차:** 실제 변환과 정책·제어기가 사용하는 추정 변환을 별도로 정의해야 한다.~~

> ~~**추가 조사 필요:** 기존 리뷰에서 본 Sweeping과 직접 대응하는 Base Randomization의 효과는 확인되지 않았다. 따라서 본 항목은 강건성 확보를 위한 제안으로 두고, 적용 범위와 실제 이득을 별도로 검증한다.~~

