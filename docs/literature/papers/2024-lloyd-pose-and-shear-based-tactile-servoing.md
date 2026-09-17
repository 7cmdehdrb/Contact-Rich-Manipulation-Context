# Pose-and-shear-based tactile servoing — 원문 상세 정리

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 조사 · R3](../reviews/2026-09-14_blind-sweep-force-torque-tactile.md#r3)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Pose-and-shear-based tactile servoing** |
| 저자 | John Lloyd, Nathan F. Lepora |
| 출판 | The International Journal of Robotics Research, 43(7), 1024–1055, 2024 |
| DOI | [10.1177/02783649231225811](https://doi.org/10.1177/02783649231225811) |
| 기존 조사본 식별자 | [2026-09-14 문헌조사](../reviews/2026-09-14_blind-sweep-force-torque-tactile.md#r3)의 **R3** |
| 정리일 | 2026-09-15 |
| 확인한 원문 | 제공된 출판본 PDF 32쪽 전체. 본문 §1–6, Appendix A–D, 식 (1)–(54), Algorithm 1–3, Figure 1–20, Table 1–9 |
| 확인하지 않은 자료 | 인용된 선행논문의 개별 원문, 저자 코드·데이터의 구현 및 실행 결과, 보충 영상, 제조사 데이터시트 |
| 원문 PDF SHA-256 | `bddb6ee52583f7d9cfb43bae9e9df4e5d8ea61d27296cb41f2cb6b52c9f6d391` |

이 문서는 논문 자체의 문제 설정, 관련 연구, 플랫폼·센서, 계산 방법, 제어, 실험과 한계를 정리한다. 별도 연구 주제에 대한 적용안은 포함하지 않는다. `[원문 §…, PDF p.…]`는 첨부 출판본의 위치이며, **PDF 1–32쪽은 인쇄 페이지 1024–1055**에 대응한다. 그림과 표는 PDF의 실제 표시를 기준으로 확인했다. 수식에서 직접 따라 나오는 해설과 표의 비교는 원문 결과에 대한 설명이며, 별도의 재현 실험 결과가 아니다.

**핵심 구분:** 이 논문의 shear는 주로 **접촉 후 접선 방향 변위와 비틀림 회전**이다. 뉴턴 단위 전단력이나 손목의 6축 wrench를 추정하는 방법이 아니다. TacTip 이미지에서 **접촉 자세·전단 변형을 나타내는 상태와 그 불확실성**을 추정하고, 로봇 운동학을 이용한 필터를 거쳐 Cartesian 속도를 생성한다. 또한 물체 전체의 global pose와 센서 접촉면의 local pose를 구분해야 한다. [원문 §2.1, §3.1–3.3, PDF pp. 3–12]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 제시하는 문제와 Related Work의 비교 구도 |
| 3 | 로봇·촉각 센서의 상세 사양, 실험 물체, 소프트웨어 |
| 4–5 | 접촉·shear 상태의 정의, 데이터 수집, 영상 전처리, CNN·GDN |
| 6 | 불확실성을 갖는 SE(3) 상태의 Bayesian filtering |
| 7–9 | 속도 제어, pushing·양팔 제어, Appendix D의 실제 파라미터 |
| 10 | 힘·접촉 정보가 실제 운동으로 이어지는 연결의 재정리 |
| 11–12 | 모델·필터 평가와 네 가지 로봇 과업의 실험 |
| 13–15 | 부록의 수학적 근거, 한계·미명시·원문 내부 불일치, 원문 위치 색인 |

## 1. 제시하는 문제 상황

### 1.1 기존 tactile servoing의 한계

Tactile servoing은 접촉 중 얻은 촉각 피드백으로 로봇 말단의 위치나 속도를 수정하는 방법이다. 저자들은 visual servoing과 달리, 부드러운 센서의 촉각 영상에는 현재 접촉뿐 아니라 **최근의 normal motion과 shear motion 이력**이 함께 반영되므로, 제어에 필요한 상태를 안정적으로 추정하기 어렵다고 설명한다. [원문 §1, PDF p. 1]

저자들의 이전 pose-based tactile servoing은 CNN으로 표면에 대한 접촉 깊이·기울기를 추정했지만, 접촉 이후 발생하는 shear를 pose 추정을 방해하는 nuisance variable로 취급했다. 이 논문은 반대로 **shear를 제어에 유용한 정보로 사용**한다. 예를 들어 접촉 중인 물체가 표면 접선 방향으로 이동하거나 접촉 법선 주위로 회전하면, 법선 접촉 상태만으로는 그 운동을 충분히 따라갈 수 없다. [원문 §1, PDF pp. 1–2]

### 1.2 첫 번째 기술 문제: slip에 의한 tactile aliasing

센서를 접촉시킨 뒤 접선 방향으로 움직였다고 해서 그 이동량이 모두 탄성 변형으로 저장되지는 않는다. 센서가 표면에서 미끄러지면 서로 다른 post-contact shear 변위가 유사한 촉각 영상을 만들 수 있다. 저자들은 이처럼 **유사한 영상에 다른 상태 label이 대응하는 현상**을 tactile aliasing으로 설명한다. 특히 작은 접촉 깊이에서 translational shear를 가하면 slip이 발생하기 쉬워진다. [원문 §1, §5.2, §6.1, PDF pp. 2, 14, 22–23]

일반 회귀 CNN이 하나의 상태값만 출력하면 이런 모호성을 제어기가 알기 어렵다. 따라서 저자들은 상태의 평균과 불확실성을 함께 출력하는 **Gaussian-density network, GDN**을 만들고, 로봇 운동학에 의한 시간적 예측과 결합한다. 이는 slip이 발생하지 않도록 모든 접촉을 보장하는 방법이나 slip을 별도 Boolean으로 검출하는 방법과는 다르다.

### 1.3 두 번째 기술 문제: 3차원 연속 운동과 SE(3)

이전의 불연속적인 위치 명령 대신, 물체·표면과 접촉하면서도 부드럽게 이어지는 **velocity-based control**을 구현하려 한다. 그런데 회전과 병진을 포함하는 pose는 SE(3)에 속한다. Euclidean 공간의 벡터처럼 pose를 그대로 더하거나 평균내고, Gaussian 분포의 곱을 그대로 Gaussian이라고 간주할 수 없다는 점이 문제가 된다. [원문 §1, §3.2–3.3, PDF pp. 2, 8–12]

따라서 이 논문의 계산 구조는 단순한 `CNN → PID`가 아니다. **확률적 접촉 상태 예측 → SE(3) 상태 전파·융합 → SE(3) 오차를 tangent-space 벡터로 변환 → 속도 제어**를 일관된 좌표계로 구성한다.

### 1.4 실제로 다루는 과업과 기여

| 과업 | 논문에서 수행하는 것 |
| --- | --- |
| Object pose tracking | 한 팔이 움직이는 표면·물체를 다른 팔의 촉각 센서가 접촉 상태로 추종 |
| Surface-following | 곡면 위를 일정 접촉 깊이와 법선 정렬 상태로 연속 이동 |
| Single-arm pushing | 한 팔로 물체를 목표점 쪽으로 밀며 접촉 관계와 진행 방향 조정 |
| Dual-arm pushing | 한 팔은 밀고 다른 팔은 촉각으로 따라가며 물체를 지지하여 전도 억제 |

저자들이 제시하는 네 가지 기여는 **통합 pose-and-shear GDN**, **SE(3) discriminative Bayesian filter**, **feedforward-feedback velocity control**, **네 과업에서의 단일·양팔 실물 평가**다. 목표 orientation까지 포함하는 일반적인 물체 pose planning이나 장애물 회피는 본 논문에서 완성한 기능이 아니다. [원문 §1, §3.3, §5.4–5.7, §6.2, PDF pp. 2, 10–12, 16–25]

## 2. Background and Related Work — 원문이 구성한 비교 구도

원문 §2는 **2.1 Tactile pose-and-shear estimation**, **2.2 Tactile servoing and object pushing**으로 구성된다. 아래 내용은 저자들이 해당 선행연구들을 소개한 범위다. 인용된 논문을 별도로 모두 정독하여 재평가한 결과는 아니다.

### 2.1 Local contact pose와 global object pose

| 구분 | 원문이 설명하는 특징 |
| --- | --- |
| Local contact pose estimation | 한 번의 접촉에서도 얻을 수 있는 국소 접촉 정보를 사용. 관측 sequence를 결합하면 정확도를 높일 수 있음 |
| Global object pose estimation | 여러 접촉에서 얻은 정보를 물체 모델 등과 결합하여 물체 전체의 pose를 추정하므로 더 어려움 |

Global pose 계열의 사례로 Bimbo et al., Suresh et al.의 tactile SLAM, Villalonga et al., Bauza et al.의 Tac2Pose, Kelestemur et al., Caddeo et al. 등이 소개된다. 이 논문의 출력은 그 계열의 전역 물체 pose가 아니라 **국소 표면과 센서 사이의 접촉 상태**다. [원문 §2.1, PDF p. 3]

Bicchi et al. (1993)은 접촉 위치·접촉력·법선 방향 모멘트의 추정을 이론적으로 다룬 초기 사례로 소개된다. GelSight에 관한 Yuan et al. (2017)은 normal contact pose를 추정하지만 비교적 평평한 센서 형상 때문에 접촉 각도 범위가 제한된다고 설명한다. TacTip 관련 선행연구는 2D에서 3D contact pose 추정으로 발전한 흐름으로 정리한다. **이 선행연구 소개에 힘·모멘트가 등장한다는 사실을 본 논문 GDN의 출력 사양으로 옮겨서는 안 된다.** [원문 §2.1, PDF p. 3]

### 2.2 Shear를 제거하는 접근과 활용하는 접근

Yuan et al. (2015)은 GelSight 표면 marker를 통해 post-contact shear를 측정했고, Cramphorn et al. (2018)은 TacTip의 marker-tipped pin 변형을 사용한 사례다. Aquilina et al. (2019)의 PCA 및 Gupta et al. (2022)의 CNN latent feature 접근은 접촉 기하와 motion-induced shear의 혼동을 줄이는 방법으로 소개된다. [원문 §2.1, PDF p. 3]

이 논문은 shear를 제거해 pose만 남기는 것이 아니라, **pose 성분과 shear 성분을 동시에 예측하고 둘 다 servoing에 사용**한다는 쪽으로 위치를 잡는다.

### 2.3 IBTS와 PBTS

**Image-based tactile servoing, IBTS**는 센서 신호나 영상 feature 공간의 오차를 제어한다. **Pose-based tactile servoing, PBTS**는 표면 feature에 대한 reference pose 등의 task-space 오차를 제어한다. 이 논문은 접촉 자세와 shear를 하나의 surface contact pose로 통합하여 feedback에 사용하므로 PBTS/task-space 계열이지만, shear의 중요성을 강조하기 위해 pose-and-shear-based tactile servoing이라고 부른다. [원문 §2.2, PDF p. 3]

| 원문이 언급한 연구 흐름 | 소개된 내용 |
| --- | --- |
| Berger & Khosla; Chen et al. | 촉각 edge 위치·orientation 또는 inverse tactile model을 이용한 2D edge tracking |
| Zhang & Chen | tactile Jacobian으로 영상 feature 오차를 task-space 오차에 연결; 2D edge와 3D 곡면 추종 |
| Sikka et al. | taxel image 기반 로봇 운동 제어와 원통 pin 굴리기 |
| Li et al.; Kappassov et al. | 3D tracking·surface-following·edge following·co-manipulation |
| Lepora et al.; Martinez-Hernandez et al. | active touch, contour following, TacTip·iCub fingertip 기반 탐색 |
| Sutanto et al. | 시연에서 학습한 tactile servoing dynamics와 3D contact-point tracking |
| Lepora & Lloyd의 이전 연구 | tactile image → contact pose의 deep model을 이용한 2D·3D pose-based servoing |

[원문 §2.2, PDF pp. 3–4]

### 2.4 Object pushing: 분석적 모델과 데이터 기반 모델

분석적 방법은 Mason의 voting theorem, Goyal et al.의 limit surface, Lee & Cutkosky의 ellipsoid approximation, Lynch et al.의 sticking/sliding 해석, Howe & Cutkosky의 다른 limit-surface 표현, Lynch & Mason의 stable pushing planning으로 이어지는 흐름이다. [원문 §2.2, PDF p. 4]

데이터 기반 방법은 Kopicki et al.의 물체 운동 예측, Bauza et al.의 학습 모델 기반 MPC, Zhou et al.의 분석·학습 혼합 limit-surface 모델, Agrawal et al.·Byravan & Fox·Li et al.의 dynamics 학습, Clavera et al.·Dengler et al.의 정책 학습으로 구분한다. 저자들은 분석적 방법이 계산 효율·투명성에 장점이 있지만, 그 가정과 근사가 맞지 않으면 성능이 떨어질 수 있다고 설명한다. [원문 §2.2, PDF p. 4]

**본 논문의 학습 대상은 물체별 pushing dynamics나 RL 정책이 아니라 tactile pose-and-shear의 확률적 추정 모델**이다. 그 출력은 설계된 필터와 feedback controller에 연결된다. [원문 §3, PDF pp. 4–12]

### 2.5 촉각 pushing과 가장 가까운 제어 비교군

Lynch et al. (1992)의 conveyor 위 물체 촉각 조작, Jia & Erdmann (1999)의 알려진 geometry에 대한 pose·motion 관측 가능성 분석, Meier et al. (2016)의 물체 상부 마찰 접촉 pushing을 소개한다. 제어 관점에서는 Hermans et al. (2013), Krivic & Piater (2019)가 가장 가깝지만, 그들은 물체 상태를 vision으로 추적하고 본 방법은 tactile sensing과 proprioception을 사용한다는 차이를 강조한다. [원문 §2.2, PDF p. 4]

## 3. 실험 환경·플랫폼·센서의 상세 사양

### 3.1 로봇 플랫폼

| 항목 | 원문에 명시된 내용 | 근거 |
| --- | --- | --- |
| 로봇 | Franka Emika Panda 2대 | §4.1, PDF p. 12 |
| 자유도 | 팔당 7 DoF | §4.1 |
| 설치 | Custom aluminium trolley와 base plate; 두 구조물을 볼트로 연결 | §4.1 |
| 베이스 간 거리 | **1.0 m** | §4.1 |
| 말단 구성 | 과업에 따라 TacTip 또는 stimulus adaptor | §4.1, Figure 6–7 |
| 센서 장착 | 기본 하향 장착 또는 right-angle adaptor를 이용한 직각 장착 | §4.1, Figure 6 |
| 사용 제어 기능 | Cartesian position/velocity control 및 로봇 상태 조회 | §4.4, PDF p. 13 |
| 저수준 실시간 루프 | libfranka callback **1 kHz** | §4.4 |
| 가반하중·도달거리·반복정밀도 | 수치 미명시 | §4의 확인 범위 |
| 로봇 최대 속도·가속도·jerk | 제한을 만족하는 trajectory generation을 사용한다고 설명하지만 각 한계값은 미명시 | §4.4 |

두 로봇이 trolley 위에 설치되었다는 사실을 이동 베이스를 제어하는 실험으로 해석하지 않는다. 논문의 조작은 설치된 두 팔의 말단 운동으로 수행한다.

### 3.2 TacTip의 원리와 구성

TacTip은 검은색의 부드러운 외피 내부에 gel을 채우고, 안쪽 pin 끝의 흰 marker를 USB 카메라와 LED 조명으로 촬영하는 **광학식 촉각 센서**다. Pin은 작은 표면 접촉을 더 큰 marker shear 패턴으로 확대하는 lever 역할을 한다. 저자들은 이를 사람 피부의 epidermal papillae 구조를 모사한 설계로 설명한다. [원문 §4.2, PDF pp. 12–13]

| 항목 | 원문 명시값·설명 | 구분 |
| --- | --- | --- |
| 사용 센서 수 | 과업에 따라 1개 또는 2개 | 실험 구성 |
| 팁 형상·크기 | **직경 40 mm의 반구형 tip** | 센서 geometry |
| Marker-tipped pin 수 | **331개**, 원형 배열 | 공간적인 sensing 구조 |
| 외피 | 3D-printed Agilus 30, Stratesys로 표기 | 재료 |
| 내부 gel | Techsil, **Shore A hardness 15** | 재료 사양 |
| 내부 영상 장치 | 표준 USB 카메라 + LED lighting | 모델명은 미명시 |
| 촬영 해상도 | **640 × 480 pixel**, 8-bit grayscale로 변환 | 실험 영상 수집 |
| Crop | **430 × 430 pixel** | 전처리 |
| 모델 입력 | **128 × 128 pixel**, 1 channel, intensity [0,1] | 학습·추론 입력 |
| 학습 출력 상태 | normal contact의 깊이·기울기와 post-contact 병진·회전 shear를 통합한 6성분 | 학습된 표현 |
| GDN 출력 | 6개 평균 + 6개 inverse standard deviation | 불확실성 표현 |

[원문 §3.1.3, §3.1.5, §4.2, Figure 3·6, PDF pp. 6–8, 12–13]

### 3.3 해상도·범위·정확도에서 명시값과 미명시값의 구분

| 성능 항목 | 원문에서 확인할 수 있는 수준 |
| --- | --- |
| 영상 해상도 | 촬영 640 × 480, 모델 입력 128 × 128 pixel |
| 공간 sensing 구성 | 331개 marker-tipped pin. Pin pitch의 mm 단위값·접촉 위치 공간 분해능은 미명시 |
| 시각화용 marker 간격 | §5.1에서 평균 인접 marker 거리에 해당하는 **15 pixel**을 Gaussian kernel width로 사용. 영상 시각화 설정이지 mm 단위 센서 분해능이 아님 |
| 최대 측정 힘·토크·압력 | N, N·m, Pa 등의 정격 범위 미명시 |
| 힘 분해능·최소 감지 힘·정확도 | 수치 미명시. 본 모델의 학습 label도 힘이 아님 |
| 카메라 frame rate·촉각 sampling rate | 수치 미명시 |
| 촉각 bandwidth·지연·high-level servo 주파수 | 수치 미명시. 저수준 1 kHz와 동일하다고 볼 수 없음 |
| 상태 추정 정확도 | Table 1–2의 MAE로 평가. 센서 하드웨어의 고유 분해능과 구분 |
| Contact pose/shear 범위 | 아래의 데이터 수집 범위가 보고됨. 하드웨어의 최대 안전 범위 또는 보증 측정 범위가 아님 |

[원문 §3.1, §4.2–4.4, §5.1–5.3, PDF pp. 5–10, 12–17]

**데이터 수집 범위:** translational shear는 반경 5 mm 원판, 깊이는 0.5–6 mm, 접촉 orientation은 중심축 기준 25° spherical cap, rotational shear는 −5°–5°다. 깊이 범위는 충분한 변화를 주되 센서를 손상시키지 않기 위해, 회전 shear 범위는 변화를 주되 slip을 제한하기 위해 선택했다고 설명한다. 이를 `최대 전단력`, `최대 압력`, `최소 검출 깊이`로 바꾸어 기록하지 않는다. [원문 §3.1.2, PDF pp. 5–6]

### 3.4 실험 물체와 지지면

| 실험 | 물체·환경 |
| --- | --- |
| 학습·검증·시험 데이터 | **VeroWhite 3D-printed flat surface**에 수직 장착 TacTip으로 접촉 |
| Object tracking | Flat surface; Rubik’s cube; mustard bottle; soft foam ball. Flat mount의 non-slip foam pad와 concave curved mount를 사용 |
| Surface-following | 3D-printed curved ramp, hemispherical dome. Base plate에 고정 |
| Single-arm pushing | 네 종류의 짧은 plastic geometric prism. MDF 및 soft foam 지지면 |
| Dual-arm pushing | 같은 짧은 물체, double-height geometric objects, 다섯 종류의 tall everyday objects |

[원문 §3.1.2, §4.3, Figure 6–10, PDF pp. 6, 13–15]

**Figure 9–10에 기재된 질량**

| 물체 | 짧은 geometric object | Double-height geometric object |
| --- | --- | --- |
| Large blue square prism | 479 g | 566 g |
| Blue circular prism | 363 g | 436 g |
| Small red square prism | 264 g | 324 g |
| Yellow hexagonal prism | 310 g | 373 g |

| Tall everyday object | 질량 |
| --- | --- |
| Mustard bottle | 237 g |
| Cream cleaner bottle | 161 g |
| Windex window cleaner spray bottle | 339 g |
| Glass bottle | 641 g |
| Large coffee tin | 214 g |

[원문 Figure 9–10 captions, PDF pp. 14–15]

원문은 이 물체들의 상세 폭·높이·지름, 관성·질량중심, MDF·foam의 마찰계수 수치를 표로 제공하지 않는다. `double-height`를 `질량 두 배`로 해석하거나 그림 크기로 치수를 추정하지 않는다. 일부 물체가 YCB set에 속한다는 설명은 있지만 외부 YCB 사양으로 빈 항목을 채우지 않았다.

### 3.5 소프트웨어와 실행 구성

| 구성 | 원문 명시값·역할 |
| --- | --- |
| libfranka | **0.8.0**, Franka Control Interface; 1 kHz real-time callback |
| pyfranka | 자체 라이브러리; smooth position/velocity trajectory, 속도·가속도·jerk 제한, background thread, pybind11 wrapper |
| CRI | Common Robot Interface Python library |
| OpenCV | **4.5.2**, 영상 수집·처리 |
| TensorFlow/Keras | **2.4**, 신경망 개발 |
| 좌표 변환 | transforms3d, Modern Robotics 제공 소프트웨어 |
| 프로세스 통신 | Pyro5 distributed object environment |
| 운영체제 | **Ubuntu 18.04** desktop PC |
| 실행 분담 | 한 PC에서 양팔 저수준 loop·영상 수집·NN inference·high-level control 수행. Training은 이 동시 실행 설명에서 제외 |
| CPU·GPU·RAM, inference latency | 미명시 |

[원문 §4.4, PDF p. 13]

## 4. Contact pose-and-shear의 정의와 학습 데이터

### 4.1 기존 3성분 contact pose에서 통합 6성분 상태로

기존 모델은 이상적인 평면 접촉을 다음과 같이 표현했다.

$$
(0,0,z,\alpha,\beta,0).
$$

깊이 $z$와 법선에 대한 두 기울기 $\alpha,\beta$는 접촉 기하를 바꾸지만, 평면과 평행한 $x,y$ 이동 및 법선 주위 $\gamma$ 회전은 이상적인 평면 geometry를 바꾸지 않는다. 이 논문은 그 세 성분을 버리는 대신 **post-contact shear**를 나타내는 데 사용한다. [원문 §3.1.1, PDF pp. 4–5]

| 성분 | 논문에서 부여한 의미 |
| --- | --- |
| $z$ | Normal contact depth |
| $\alpha,\beta$ | 접촉면 법선에 대한 센서 기울기 |
| $x,y$ | Normal contact 이후 표면 접선 방향으로 가한 translational shear motion |
| $\gamma$ | Normal contact 이후 접촉 법선축 주위로 가한 rotational shear motion |

이것은 global object pose를 여섯 축으로 완전히 측정한다는 뜻이 아니다. 또한 $x,y$는 slip이 전혀 없는 상태에서의 탄성 변형만을 정답으로 측정한 값이 아니다. **로봇으로 가한 post-contact motion을 label로 사용하므로 slip이 발생하면 영상과 motion label 사이에 모호성이 생긴다.** [원문 §3.1.1–3.1.2, §6.1]

### 4.2 두 가지 모델링 가정

첫째, 모든 접촉 표면은 **국소적으로 평면으로 근사**할 수 있다고 가정한다. 둘째, 센서 출력을 만드는 접촉을 **normal contact motion 후 tangential post-contact shear motion**으로 분해한 등가 운동으로 근사할 수 있다고 가정한다. 실제 과업에서는 normal·shear가 섞인 시간 이력이 생기지만, 학습 표본은 이 두 단계 절차로 생성한다. [원문 §3.1.1, PDF p. 5]

센서 frame $\{s\}$는 반구형 tip 중심에 부착하고 $z$축을 tip 바깥쪽으로 향하게 둔다. Surface feature frame $\{f\}$의 $z$축은 표면 법선 방향으로 표면 안쪽을 향한다. 초기 비접촉 위치에서 두 frame은 정렬되도록 설정한다.

Normal motion의 변환을 $\mathbf X_\perp$, tangential shear motion의 변환을 $\mathbf X_\parallel$로 쓰면 다음과 같다.

$$
\mathbf X_{fs}=\mathbf X_\parallel\mathbf X_\perp.
$$

$\mathbf X_\perp$는 extrinsic-xyz Euler convention의 $\alpha,\beta$ 회전과 깊이 $z$의 접촉을, $\mathbf X_\parallel$은 $x,y$ 병진과 $\gamma$ 회전을 나타낸다. 이 순서로 생성한 SE(3) 변환의 Euler 표현을 $(x,y,z,\alpha,\beta,\gamma)$로 사용한다. 두 종류의 상태를 하나로 구성하므로 별도의 pose filter와 shear filter를 각각 운용할 필요가 없어진다. [원문 §3.1.1, Figure 2, PDF p. 5]

### 4.3 데이터 수집 — Algorithm 1

각 sampled contact pose에 대해 센서를 표면 위 시작점으로 이동시키고, 기울기 $\alpha,\beta$로 회전한다. 이후 법선 방향으로 깊이 $z$만큼 접촉한 다음, 접선 방향 $x,y$와 회전 $\gamma$의 shear를 가하고 마지막 tactile image를 취득한다. **이미지 한 장과 그에 대응하는 로봇 운동 label**이 한 표본이다. [원문 Algorithm 1, PDF p. 6]

**원문 식 (1): 원판에서의 translational shear sampling**

$$
x=r\cos\theta,\qquad y=r\sin\theta,\qquad
r=r_{\max}\sqrt{r'},
$$

$$
r'\sim\mathcal U(0,1),\qquad
\theta\sim\mathcal U(0,360^\circ),\qquad r_{\max}=5\ \mathrm{mm}.
$$

제곱근을 사용하는 것은 원판 면적에 대해 균일하게 표본을 배치하기 위한 식이다. $x,y$를 각각 −5–5 mm의 독립 uniform으로 뽑는 사각형 분포와 다르다.

**원문 식 (2): spherical cap의 orientation sampling**

$$
\begin{aligned}
\alpha&=-\arcsin q, &\beta&=-\mathrm{atan2}(p,r),\\
p&=\sin\phi\cos\theta, &q&=\sin\phi\sin\theta, &r&=\cos\phi,\\
\phi&=\arccos\!\left(1-(1-\cos\phi_{\max})\phi'\right),
\end{aligned}
$$

$$
\phi'\sim\mathcal U(0,1),\qquad
\theta\sim\mathcal U(0,360^\circ),\qquad \phi_{\max}=25^\circ.
$$

깊이는 $z\sim\mathcal U(0.5,6)$ mm, 회전 shear는 $\gamma\sim\mathcal U(-5^\circ,5^\circ)$다. 식 (1)의 반지름 $r$와 식 (2)의 구면 성분 $r$는 같은 기호가 다른 문맥에서 사용된 것이다. [원문 §3.1.2, 식 (1)–(2), PDF pp. 5–6]

| Dataset | 표본 수 | 용도 |
| --- | --- | --- |
| Training | 6000 | 모델 학습 |
| Validation | 2000 | 모델 선택·hyperparameter tuning |
| Test | 2000 | 학습 후 독립적인 성능 확인 |

세 dataset 모두 VeroWhite flat surface에서 수집했다. 여러 과업에 등장하는 모든 물체의 형상·마찰별 pushing 데이터를 수집해 정책을 학습한 것은 아니다.

### 4.4 영상 전처리

```text
USB camera image: 640×480
  → 8-bit grayscale
  → marker 영역을 포함하는 430×430 crop
  → 5×5 median blur
  → adaptive threshold로 이진화
  → 128×128 resize
  → floating point 변환 및 [0,1] 정규화
  → CNN 또는 GDN
```

이 절차는 training·validation·test뿐 아니라 배포 후 추론에도 적용된다. Adaptive threshold의 구체적인 window·상수, resize interpolation 방식 등은 원문에 기재되어 있지 않다. [원문 §3.1.3, PDF p. 6]

**Marker density map은 이 추론 pipeline의 필수 전처리가 아니다.** §5.1에서 Gaussian kernel을 marker centroid에 놓아 density를 시각화한 것은 영상 안에 pose·shear 정보가 존재함을 살펴보기 위한 분석이다. 실제 neural network에는 위의 전처리 영상이 들어간다. [원문 §3.1.3, §4.2, §5.1, Figure 11, PDF pp. 6, 13–15]

### 4.5 Label 변환 — Euler pose를 그대로 회귀하지 않는다

원문의 label 전처리는 다음과 같다.

$$
(x,y,z,\alpha,\beta,\gamma)
\longrightarrow \mathbf X_{fs}
\longrightarrow \mathbf X_{sf}=\mathbf X_{fs}^{-1}
\longrightarrow \boldsymbol\xi_{sf}=\ln(\mathbf X_{sf})^\vee.
$$

따라서 model output은 **feature frame에서 본 sensor pose의 Euler 6-vector**가 아니라, **sensor frame에서 본 feature pose를 SE(3) logarithm으로 바꾼 exponential coordinates**다. 이후 mean을 다시 변환할 때는 $\mathbf X=\exp(\boldsymbol\xi^\wedge)$를 사용한다. [원문 §3.1.3–3.1.4, PDF p. 6]

이 차이는 부호와 좌표계, rotation 표현을 읽는 데 중요하다. 데이터 수집 범위의 $\alpha,\beta,\gamma$와 GDN output의 마지막 세 exponential-coordinate 성분을 아무 변환 없이 같은 숫자로 취급하지 않는다.

## 5. CNN과 Gaussian-density network

### 5.1 공통 convolutional base와 baseline CNN

Convolutional block은 **3×3 Conv2D → batch normalization → ReLU → 2×2 max pooling**으로 구성한다. Pooling에 따라 공간 해상도가 절반으로 줄어드는 대신 다음 block에서 feature 수를 두 배로 늘린다. Figure 3에는 다음 shape가 표시된다. [원문 §3.1.4, Figure 3, PDF pp. 6–7]

```text
128×128×1
 → 64×64×16
 → 32×32×32
 → …
 → 2×2×512
 → 1×1×1024
```

Baseline regression head는 flatten, dropout probability 0.1, linear activation의 fully connected output으로 구성하며, 6성분 상태를 출력한다.

**원문 식 (3): weighted MSE**

$$
\mathrm{MSE}=\frac{1}{N}\sum_{i=1}^{N}\sum_{j=1}^{6}
\alpha_j\left(\xi_{ij}^{\mathrm{label}}-\xi_{ij}\right)^2.
$$

Loss weight는 $(1,1,1,100,100,100)$이다. 여기의 $\alpha_j$는 앞의 Euler angle $\alpha$와 다른 loss weight다. 저자들은 출력 scale 차이와 일부 출력의 큰 오차를 고려하기 위해 이 값을 시행착오로 정했다. [원문 §3.1.4, PDF p. 6]

### 5.2 GDN이 추가하는 것은 상태별·표본별 불확실성

GDN은 각 영상에서 6개 평균 $\mu_j$와 6개 inverse standard deviation $\sigma_j^{-1}$을 출력한다. 한 영상에 대응하는 상태 분포는 diagonal covariance를 갖는 **단일 multivariate Gaussian**으로 표현한다. 이전 연구에서 사용한 Gaussian mixture와 달리, 여기서는 후속 Bayesian filter 가정과 맞추기 위해 한 개 Gaussian을 선택한다. [원문 §3.1.5, PDF pp. 7–8]

**원문 식 (4)**

$$
p(\boldsymbol\xi_i)=\prod_{j=1}^{6}
\frac{\sigma_{ij}^{-1}}{\sqrt{2\pi}}
\exp\left[-\frac12
\left(\sigma_{ij}^{-1}(\xi_{ij}-\mu_{ij})\right)^2\right].
$$

출력된 inverse standard deviation으로 각 variance를 계산한다.

$$
\sigma_{ij}^{2}=\frac{1}{(\sigma_{ij}^{-1})^2}.
$$

**원문 식 (5): 평균 negative log-likelihood**

$$
\overline{\mathrm{NLL}}=
\frac{1}{N}\sum_{i=1}^{N}\sum_{j=1}^{6}
\left[
\frac12\left(\sigma_{ij}^{-1}
(\xi_{ij}^{\mathrm{label}}-\mu_{ij})\right)^2
-\ln\sigma_{ij}^{-1}
\right]+c,
\qquad c=\frac{6}{2}\ln(2\pi).
$$

불확실성이 낮아 inverse standard deviation이 큰 출력은 mean 오차에 더 큰 weight를 준다. 반대로 불확실한 출력의 오차는 더 작은 weight를 받는다. 다만 $-\ln\sigma^{-1}$ 항이 있으므로 uncertainty를 무한히 키우는 것만으로 loss를 줄이는 구조는 아니다. **이는 식 (5)의 항별 역할을 풀어 쓴 해설**이다.

모든 표본에서 $\sigma_{ij}^{-1}$을 동일한 값으로 고정하면 weighted MSE 계열의 학습과 연결되지만, GDN에서는 표본마다 uncertainty를 예측한다. 표본·성분별 신뢰도 차이를 후속 필터가 사용할 수 있다는 것이 핵심이다. [원문 §3.1.5, §5.2, PDF pp. 7, 14]

### 5.3 학습 안정화를 위한 세 가지 변경

**첫째, 표준편차 대신 inverse standard deviation을 직접 출력한다.** Mean과 standard deviation을 동시에 학습하면 NLL 안의 quotient 때문에 불안정하거나 학습이 느려지는 문제가 있었다고 설명한다. Inverse standard deviation을 출력하면 그 항이 product가 된다. [원문 §3.1.5, PDF p. 7]

**둘째, softbound activation으로 그 값을 제한한다.**

**원문 식 (6)**

$$
\mathrm{softbound}(x)=x_{\min}
+\mathrm{softplus}(x-x_{\min})
-\mathrm{softplus}(x-x_{\max}),
$$

$$
\mathrm{softplus}(x)=\ln(1+\exp x).
$$

여기서는 $\sigma_j^{-1}$의 범위를 $[10^{-6},10^{6}]$으로 둔다. 이는 **NN 출력의 수치 안정화 범위**이며 센서의 물리적인 측정 범위가 아니다. [원문 §3.1.5, PDF p. 8]

**셋째, 출력마다 다른 multi-dropout을 사용한다.** Flatten된 1024차원 feature를 12개 branch로 복제하고, 각 branch에 별도 dropout과 하나의 linear output을 둔다. 여섯 inverse-standard-deviation output에는 softbound를 추가한다. Shared CNN base는 유지되므로 12개 완전히 독립된 신경망을 학습하는 것은 아니다. [원문 Figure 3(d), §3.1.5, PDF pp. 7–8]

| 출력 branch | 순서대로 적용하는 dropout probability |
| --- | --- |
| Mean, $p_\mu$ | $(0.7,0.7,0.1,0,0,0.4)$ |
| Inverse standard deviation, $p_{\sigma^{-1}}$ | $(0.1,0.1,0,0,0,0.05)$ |

Mean의 translational shear 및 rotational shear 관련 output에 더 강한 regularization을 적용하는 구성이다. 원문은 이 값들을 manual tuning으로 찾았다고 설명한다. **Inference에서 dropout을 여러 번 적용해 uncertainty를 계산하는 MC-dropout 방법이 아니라, 별도 uncertainty output을 학습하는 GDN이다.** [원문 §3.1.5, PDF p. 8]

### 5.4 공통 학습 설정

| 항목 | 원문 설정 |
| --- | --- |
| Optimizer | Adam |
| Batch size | 16 |
| Learning rate schedule | Linear rise, polynomial decay, LRPD |
| 초기 learning rate | $10^{-5}$ |
| 상승 | 3 epochs 동안 $10^{-3}$까지 선형 증가 |
| 유지 | 추가 1 epoch |
| 감소 | $e_{\max}=50$ epochs에 걸쳐 $10^{-7}$까지 감소; $\sqrt{1-e/e_{\max}}$ weighting 사용 |
| Early stopping | Validation loss, patience 25 epochs |
| 반복 학습 | CNN 10개, GDN 10개; 서로 다른 random weight initialization |

[원문 §3.1.4–3.1.5, §5.2, PDF pp. 6–8, 14]

저자들은 learning-rate schedule이 특정 learning rate 선택에 대한 민감도를 낮추고 성능을 개선했다고 설명한다. 원문에 없는 Adam 세부 계수나 전체 training wall-clock time은 추가하지 않는다.

## 6. SE(3) discriminative Bayesian filtering

### 6.1 왜 단순한 시계열 평균이 아닌가

GDN 한 장의 출력에도 shear 오차가 남는다. 필터는 이전 상태를 로봇 운동으로 전파한 **belief**와 현재 영상이 주는 **observation**을 uncertainty에 따라 결합한다. 따라서 고정 계수 low-pass filter와 달리, 현재 추정이 얼마나 모호한지에 따라 정보의 영향이 달라진다. [원문 §3.2, §5.3, PDF pp. 8–10, 14–15]

원문에서 사용하는 state dynamics model은 물체의 질량·마찰로 pushing 운동을 예측하는 물리 모델이 아니다. **측정된 sensor pose 변화로 국소 feature의 상대 pose 변화를 근사**하고, 그 근사가 설명하지 못하는 물체 운동 등을 process noise로 둔다.

### 6.2 Generative observation model을 discriminative model로 바꾸는 이유

일반 Bayesian filter에서는 상태 $x_k$가 주어졌을 때 관측 $y_k$가 나올 분포 $p(y_k\mid x_k)$를 사용한다. 하지만 이 논문의 GDN은 tactile image $y_k$에서 state의 분포 $p(x_k\mid y_k)$를 직접 예측한다. 이 방향 차이를 Bayes’ rule로 처리한다. [원문 §3.2.1, PDF pp. 8–9]

**원문 식 (7)–(9): prediction과 correction**

$$
p(x_k\mid y_{1:k-1})=
\int p(x_k\mid x_{k-1})p(x_{k-1}\mid y_{1:k-1})\,dx_{k-1},
$$

$$
p(x_k\mid y_{1:k})=
\frac{1}{Z_k}p(y_k\mid x_k)p(x_k\mid y_{1:k-1}),
$$

$$
Z_k=\int p(y_k\mid x_k)p(x_k\mid y_{1:k-1})\,dx_k.
$$

**원문 식 (10): GDN과 맞는 discriminative correction**

$$
p(x_k\mid y_{1:k})=
\frac{1}{Z'_k}
\frac{p(x_k\mid y_k)p(x_k\mid y_{1:k-1})}{p(x_k)}.
$$

여기서 추가로 $p(x_k)$가 constant라고 가정하면 다음으로 단순화된다.

**원문 식 (11)**

$$
p(x_k\mid y_{1:k})=
\frac{1}{Z''_k}p(x_k\mid y_k)p(x_k\mid y_{1:k-1}).
$$

즉 이 단순화에는 **constant prior 가정**이 들어 있다. 임의의 discriminative model을 어떤 prior 보정도 없이 항상 같은 방식으로 결합할 수 있다는 일반적인 주장으로 확대하지 않는다. 원문 식 (12)–(13)은 이 관계를 $x^{\mathrm{bel}},x^{\mathrm{obs}},x^{\mathrm{fil}}$로 다시 쓴 것이다. [원문 §3.2.1, PDF p. 9]

### 6.3 SE(3) 상태의 uncertainty 표현

원문은 SE(3) 평균에 작은 Gaussian perturbation을 **왼쪽에서 곱하는 방식**을 사용한다.

$$
\mathbf X=\exp(\boldsymbol\epsilon^\wedge)\bar{\mathbf X},
\qquad \boldsymbol\epsilon\sim\mathcal N(\mathbf0,\boldsymbol\Sigma).
$$

Gaussian인 것은 tangent-space perturbation $\boldsymbol\epsilon$이지, 곡면인 SE(3) 위의 $\mathbf X$를 그대로 Euclidean Gaussian으로 둔 것이 아니다. 이 구분 때문에 GDN output covariance도 변환해야 한다. [원문 Appendix B, 식 (35)–(38), PDF pp. 29–30]

**원문 식 (14): GDN output → SE(3) observation**

$$
\bar{\mathbf X}^{\mathrm{obs}}_k=
\exp(\boldsymbol\mu_k^\wedge),
\qquad
\boldsymbol\Sigma^{\mathrm{obs}}_k=
\mathcal J(\boldsymbol\mu_k)
\mathrm{diag}(\boldsymbol\sigma_k^2)
\mathcal J(\boldsymbol\mu_k)^T.
$$

$\mathcal J$는 **SE(3)의 left Jacobian**이다. 로봇 관절 속도를 말단 속도로 바꾸는 manipulator Jacobian과 다른 대상이다. NN은 diagonal covariance를 출력하지만 이 좌표 변환 후 covariance가 계속 diagonal이라고 전제할 수는 없다. [원문 §3.2.2, Appendix A–B, PDF pp. 9–10, 28–30]

### 6.4 Prediction: 자기 운동으로 상대 접촉 상태를 전파

현재·이전 sensor pose를 로봇 운동학에서 얻어 다음 변환을 계산한다.

**원문 식 (15)**

$$
\bar{\mathbf T}_k=
(\mathbf X^{\mathrm{sens}}_k)^{-1}\mathbf X^{\mathrm{sens}}_{k-1}.
$$

이 변환으로 이전 filtered mean과 covariance를 전파한다.

**Algorithm 2 / 원문 식 (41)에 해당하는 prediction**

$$
\bar{\mathbf X}^{\mathrm{bel}}_k=
\bar{\mathbf T}_k\bar{\mathbf X}^{\mathrm{fil}}_{k-1},
$$

$$
\boldsymbol\Sigma^{\mathrm{bel}}_k=
\mathrm{Ad}(\bar{\mathbf T}_k)
\boldsymbol\Sigma^{\mathrm{fil}}_{k-1}
\mathrm{Ad}(\bar{\mathbf T}_k)^T+
\boldsymbol\Sigma_\phi.
$$

Mean뿐 아니라 covariance도 adjoint로 이동시킨 후 process noise를 추가한다. $\mathbf X^{\mathrm{sens}}$가 바뀌면서 같은 표면을 다른 sensor frame에서 보게 되는 관계가 prediction에 반영된다. 상대적인 물체 운동 등 이 근사에서 벗어난 변화는 $\boldsymbol\Sigma_\phi$로 허용한다. [원문 §3.2.2, Algorithm 2, Appendix B, PDF pp. 8–10, 29–30]

**원문 식 (16): 기본 process noise 설정**

$$
\boldsymbol\Sigma_\phi=\sigma_\phi^2\mathbf I_{6\times6},
\qquad \sigma_\phi=0.5.
$$

원문은 이 값을 병진 0.5 mm/s, 회전 0.5 deg/s의 uncertainty로 설명한다. 다만 상태를 pose exponential coordinates로 정의한 부분과 시간 단위 표기가 완전히 명료하게 연결되어 있지는 않다. 본 문서는 원문의 값을 보존하고, 보고되지 않은 timestep scaling을 만들어 추가하지 않는다. 해당 주의점은 14.2절에 다시 모았다.

### 6.5 Correction: 두 SE(3) 분포를 어떻게 결합하는가

수정 단계는 현재 observation과 prediction belief의 정규화된 곱을 근사한다.

$$
p(x_k^{\mathrm{fil}})=
\frac{1}{Z}p(x_k^{\mathrm{obs}})p(x_k^{\mathrm{bel}}).
$$

SE(3)에서는 이 곱이 일반적으로 같은 형태의 분포가 아니므로, 두 분포가 평균 주변에 충분히 집중되어 있다는 **concentrated Gaussian on a Lie group** 근사와 iterative fusion을 사용한다. 이 방법의 전개는 Appendix C에 있다. [원문 §3.2.2, Appendix C, 식 (43)–(54), PDF pp. 9–10, 30–31]

**Algorithm 3의 계산**

두 입력을 $(\bar{\mathbf X}_1,\boldsymbol\Sigma_1)$, $(\bar{\mathbf X}_2,\boldsymbol\Sigma_2)$로 두고 operating point를 $\bar{\mathbf X}\leftarrow\bar{\mathbf X}_1$로 시작한다. 각 반복에서 residual을 계산한다.

$$
\boldsymbol\xi_i=\ln(\bar{\mathbf X}\bar{\mathbf X}_i^{-1})^\vee,
\qquad \mathcal J_i^{-1}=\mathcal J(\boldsymbol\xi_i)^{-1},
\qquad i\in\{1,2\}.
$$

Inverse left Jacobian은 2차까지 근사한다.

$$
\mathcal J(\boldsymbol\xi)^{-1}\approx
\mathbf I-\frac12\mathrm{ad}(\boldsymbol\xi^\wedge)
+\frac1{12}\left[\mathrm{ad}(\boldsymbol\xi^\wedge)\right]^2.
$$

이후 combined covariance와 mean perturbation을 구한다.

$$
\boldsymbol\Sigma=
\left(
\mathcal J_1^{-T}\boldsymbol\Sigma_1^{-1}\mathcal J_1^{-1}
+\mathcal J_2^{-T}\boldsymbol\Sigma_2^{-1}\mathcal J_2^{-1}
\right)^{-1},
$$

$$
\boldsymbol\mu=-\boldsymbol\Sigma
\left(
\mathcal J_1^{-T}\boldsymbol\Sigma_1^{-1}\boldsymbol\xi_1
+\mathcal J_2^{-T}\boldsymbol\Sigma_2^{-1}\boldsymbol\xi_2
\right).
$$

Operating point를 갱신한다.

$$
\bar{\mathbf X}\leftarrow
\exp(\boldsymbol\mu^\wedge)\bar{\mathbf X}.
$$

여기서 $^{-T}$는 inverse transpose다. Residual 정의에 대응하는 **$\boldsymbol\mu$ 앞의 음수 부호**가 중요하다. 알고리즘은 두 covariance의 inverse를 사용하므로 uncertainty가 작은 정보를 더 강하게 반영하지만, 이는 SE(3) 좌표 변환과 함께 이루어지는 결합이지 여섯 Euler angle을 단순 평균하는 것이 아니다. [원문 Algorithm 3, PDF p. 9]

Appendix C에 따르면 보통 3–4회에 수렴했지만, real-time 실행시간을 예측 가능하게 만들기 위해 **5회 고정 반복**을 사용한다. 필터 초기 상태는 최초 observation의 mean·covariance와 같게 설정한다. [원문 Algorithm 2, Appendix C 마지막 부분, PDF pp. 8, 31]

### 6.6 필터의 의미와 한계

필터는 GDN의 불확실성을 없다고 가정하는 것이 아니라 **상태의 시간적 변화에 관한 추가 정보를 사용하여 줄이는 것**이다. State dynamics가 정확하고 noise를 적절히 설정하면 효과가 커지고, prediction noise가 커지면 결과가 단일 영상의 GDN 추정에 가까워진다. 저자들은 실제 제어 과업에서는 $\sigma_\phi=0.5$를 사용하여 정밀성과 환경 변화에 대한 반응성 사이를 절충했다고 설명한다. [원문 §5.3, PDF pp. 14–15]

다만 이 필터가 slip의 원인, 접촉력, 마찰계수, global object pose를 자동으로 식별하는 것은 아니다. 그 상태들은 본 필터의 명시적 state에 포함되지 않는다.

## 7. Feedforward-feedback tactile servo control

### 7.1 SE(3) 오차를 제어 가능한 6차원 벡터로 바꾸기

일반적인 관측 pose $\mathbf X$와 reference pose $\mathbf X_{\mathrm{ref}}$에 대해 원문은 다음 오차를 사용한다.

**원문 식 (17)–(18)**

$$
\mathbf E_X=\mathbf X^{-1}\mathbf X_{\mathrm{ref}},
\qquad
\mathbf e_X=\ln(\mathbf X^{-1}\mathbf X_{\mathrm{ref}})^\vee.
$$

이는 $\mathbf X_{\mathrm{ref}}=\mathbf X\mathbf E_X$를 만족하는 **right-multiplying error**다. 그 로그를 취한 $\mathbf e_X\in\mathbb R^6$에 기존 vector-space PID를 적용한다. GDN uncertainty 표현에서 사용하는 left perturbation과 이 제어 오차의 right perturbation을 혼동하지 않는다. [원문 §3.3.1, PDF p. 10]

**원문 식 (19)**

$$
\mathbf u(t)=\mathbf v(t)
+\mathbf K_p\mathbf e_X(t)
+\mathbf K_i\int_0^t\mathbf e_X(t')\,dt'
+\mathbf K_d\frac{d\mathbf e_X}{dt}(t).
$$

$\mathbf K_p,\mathbf K_i,\mathbf K_d$는 diagonal 6×6 gain matrix다. Feedforward $\mathbf v$는 error가 0이어도 surface-following이나 pushing 운동을 지속시키는 성분이다. **출력은 velocity control signal이며, 원하는 힘·토크가 아니다.**

Discrete-time 구현에서는 integral·derivative를 backward-Euler 방식으로 근사한다. Derivative 계산 전 error를 decay coefficient 0.5의 exponentially weighted moving average로 평활화한다. 필요에 따라 integral clipping으로 wind-up을 줄이고 output도 제한한다. 구체적인 gain과 clipping은 Appendix D의 과업별 표를 따른다. [원문 §3.3.1, PDF pp. 10–11]

### 7.2 실제 tactile controller의 frame 관계

GDN과 필터가 내는 값은 **현재 sensor frame에서 본 feature pose** $\mathbf X_{sf}$다. 목표 sensor frame을 $\{s'\}$라 하면 실제 servo error는 다음과 같다.

**원문 식 (20)**

$$
\mathbf E_X=\mathbf X_{ss'}=
\mathbf X_{fs}^{-1}\mathbf X_{s'f}^{-1}
=\mathbf X_{sf}\mathbf X_{s'f}^{-1}.
$$

오차 $\mathbf X_{ss'}$를 logarithm으로 바꾸어 PID 1에 보내고, 목표 sensor frame에서 정한 feedforward velocity $\mathbf u_{s'2}$는 현재 sensor frame으로 변환하여 더한다.

$$
\mathbf u_{s2}=\mathrm{Ad}(\mathbf X_{ss'})\mathbf u_{s'2}.
$$

따라서 접촉면이 기울어져 reference와 현재 sensor frame이 달라도, reference에서 정한 접선/법선 방향의 운동을 현재 frame의 feedback velocity와 결합할 수 있다. [원문 §3.3.2, Figure 5(a), PDF p. 11]

### 7.3 Tracking과 surface-following의 설정 차이

Object tracking에서는 **reference contact depth 6 mm**, feedforward 0으로 두고 움직이는 표면에 대한 접촉 오차를 줄인다. Surface-following에서는 **reference depth 3 mm**, 표면 접선 방향의 feedforward **10 mm/s**를 사용한다. 센서를 표면 법선으로 정렬하고 정해진 깊이를 유지하면서 이동하도록 구성한다. [원문 §5.4–5.5, Tables 6–7, PDF pp. 16–18, 32]

Surface-following의 shear 관련 feedback gain은 0이다. 표면을 따라 미끄러지는 과정에서 접선 변형을 모두 0으로 되돌리는 것이 이 과업의 목표가 아니기 때문이다. 다만 저자들은 pose·shear 성분이 SE(3) filter 안에서 결합되므로 shear 추정이 간접적으로도 사용된다고 설명한다. [원문 §6.2, PDF p. 25]

## 8. Pushing controller와 양팔 협조

### 8.1 왜 target alignment controller를 추가하는가

Tactile servo만으로 접촉면을 추종하는 것과 물체를 정해진 목표점으로 보내는 것은 다르다. Pushing에서는 **PID 1의 접촉 상태 feedback + 물체 안쪽 법선 방향 feedforward + PID 2의 target alignment**를 합성한다. [원문 §3.3.3, Figure 5, PDF pp. 11–12]

Target alignment controller는 sensor–object 마찰 접촉을 유지하면서 **접선 방향 횡이동**으로 물체의 진행을 목표 쪽으로 바꾸려 한다. 이전 연구의 접촉을 반복적으로 끊고 위치를 바꾸는 방식 대신 연속적인 tangential motion을 사용한다. [원문 §3.3.3, §6.2, PDF pp. 11–12, 24]

### 8.2 목표를 reference sensor frame으로 변환

목표 pose는 work frame $\{w\}$의 $\mathbf X_{wt}$로 주어진다. 로봇의 proprioception으로 얻는 현재 sensor pose $\mathbf X_{ws}$와 tactile error $\mathbf X_{ss'}$를 사용한다.

**원문 식 (21)**

$$
\mathbf X_{s't}=\mathbf X_{ss'}^{-1}\mathbf X_{ws}^{-1}\mathbf X_{wt}.
$$

이렇게 목표를 reference sensor frame에서 표현한 다음, 그 translation의 $y,z$ 성분으로 bearing과 distance를 구한다.

**원문 식 (22)**

$$
\theta_{s'}=\mathrm{atan2}(y,z),
\qquad r_{s'}=\sqrt{y^2+z^2}.
$$

**여기서는 $\mathrm{atan2}(y,z)$다.** 평면 navigation에서 흔히 쓰는 $\mathrm{atan2}(y,x)$로 바꾸면 안 된다. Pushing의 전진은 reference sensor frame의 $z$, 횡이동은 $y$ 방향으로 설정된다. [원문 §3.3.3, Figure 5(b), PDF pp. 11–12]

### 8.3 Bearing error를 횡방향 속도로 변환

Reference bearing은 $\theta_{s'r}=0$이므로 다음 오차를 사용한다.

$$
e_{s'3}=\theta_{s'r}-\theta_{s'}.
$$

SISO PID 2가 내는 scalar output을 $y$축 성분에만 놓는다.

$$
\mathbf u_{s'3}=(0,u_{s'3},0,0,0,0)^T,
\qquad
\mathbf u_{s3}=\mathrm{Ad}(\mathbf X_{ss'})\mathbf u_{s'3}.
$$

최종적으로 Figure 5의 속도 합성은 다음과 같다.

$$
\mathbf u_s=
\mathbf u_{s1}
+\mathrm{Ad}(\mathbf X_{ss'})\mathbf u_{s'2}
+\mathrm{Ad}(\mathbf X_{ss'})\mathbf u_{s'3}.
$$

여기서 $\mathbf u_{s1}$은 tactile PID 1 output, $\mathbf u_{s'2}$는 feedforward, $\mathbf u_{s'3}$는 target alignment다. 이 합성은 **관절 torque를 합치는 것**이 아니라 **같은 frame으로 맞춘 Cartesian velocity twist를 더하는 것**이다. [원문 §3.3.3, Figure 5, PDF pp. 11–12]

### 8.4 목표 부근의 전환과 종료

목표에서 **120 mm 이내**가 되면 target alignment output을 0으로 둔다. 이는 목표 근처에서 조향을 계속할 때의 불안정성을 줄이기 위해 manual tuning한 거리다. 이후 tactile servoing controller만 active하게 남는다. Pushing sequence는 **sensor tip 중심과 target의 거리가 sensor radius 20 mm보다 작아지면 종료**한다. [원문 §3.3.3, PDF p. 12]

이 종료 기준의 대상은 **물체 중심의 pose error가 아니라 sensor tip 중심의 거리**다. 저자들은 이를 통해 sensor–object contact point가 목표점 가까이 가고 overshoot를 줄이려 한다. 실험에서 보고하는 final target error의 정의는 이 종료 threshold와도 다르며 12.3절에서 구분한다.

### 8.5 Single-arm과 dual-arm

Single-arm에서는 한 팔이 위 pushing controller를 실행한다. Dual-arm에서는 동일한 pushing controller를 사용하는 **active/leader**와 object-tracking controller를 사용하는 **passive/follower**를 물체 반대편에 둔다. Follower는 feedforward 없이 접촉 상태 변화를 따라가며 물체가 넘어지지 않도록 지지한다. [원문 §3.3.4, §5.7, PDF pp. 12, 19–21]

이는 중앙에서 두 팔의 힘을 최적 분배하는 force-allocation 방법이 아니다. 저자들은 자신의 leader–follower 방식을 **decentralised configuration**이라고 설명한다. 각 팔이 자기 접촉의 reference를 만족하려고 움직이고, 물체와의 상호작용으로 협조가 이루어진다. Leader의 목표와 follower의 역할은 다르다.

## 9. Appendix D — 실제 과업별 제어 파라미터

아래 값은 **원문 Tables 6–9의 실험 설정**이다. 모든 reference pose는 표에 제시된 **앞 3성분 position, 뒤 3성분 extrinsic-xyz Euler rotation** 순서로 적는다. 이 pose vector와 모델의 exponential coordinates는 같은 표현이 아니다. Gain의 활성 축은 MIMO error/control channel 순서의 병진 3개·회전 3개에 대응한다. 원문 표에 없는 하드웨어 최대 성능이나 N 단위 힘 설정값을 추가하지 않는다. [원문 Appendix D, PDF p. 32]

### 9.1 Object tracking — Table 6

| 항목 | 값 |
| --- | --- |
| $\mathbf K_p$ | $\mathrm{diag}(5,5,5,2,2,0)$ |
| $\mathbf K_i$ | $\mathrm{diag}(0.5,0.5,0.5,0.2,0.2,0.2)$ |
| $\mathbf K_d$ | $\mathrm{diag}(0.5,0.5,0.5,0.2,0.2,0.2)$ |
| Integral clipping | 사용하지 않음 |
| Feedback reference pose | $(0,0,6,0,0,0)$ |
| Feedforward reference velocity | $(0,0,0,0,0,0)$ |

마지막 회전축의 proportional gain은 0이지만 integral·derivative gain은 0이 아니다. 따라서 `마지막 회전축을 전혀 제어하지 않는다`고 해석하면 틀린다.

### 9.2 Surface-following — Table 7

| 항목 | 값 |
| --- | --- |
| $\mathbf K_p$ | $\mathrm{diag}(0,0,2,2,2,0)$ |
| $\mathbf K_i$ | $\mathrm{diag}(0,0,0.1,0.1,0.1,0)$ |
| $\mathbf K_d$ | $\mathrm{diag}(0,0,0.05,0.05,0.05,0)$ |
| Integral clipping | 모든 성분 $[-25,25]$ |
| Feedback reference pose | $(0,0,3,0,0,0)$ |
| Feedforward reference velocity | 과업에 따라 설정; 접선 방향 10 mm/s |

Feedback의 활성 성분은 깊이와 두 기울기다. Shear 관련 세 성분의 feedback gain은 0으로 설정한다. Ramp에서는 $(0,10,0,0,0,0)$, dome에서는 방향 $\theta_i$에 따라 $(10\cos\theta_i,10\sin\theta_i,0,0,0,0)$를 사용한다. [원문 §5.5, PDF pp. 17–18]

### 9.3 Pushing의 leader — Table 8

**PID 1: tactile MIMO feedback**

| 항목 | 값 |
| --- | --- |
| $\mathbf K_p$ | $\mathrm{diag}(1,0,0,1,0,0)$ |
| $\mathbf K_i$ | $\mathrm{diag}(0.1,0,0,0.1,0,0)$ |
| $\mathbf K_d$ | $\mathrm{diag}(0.1,0,0,0.1,0,0)$ |
| Integral clipping | 모든 성분 $[-25,25]$ |
| Feedback reference pose | $(0,0,0,0,0,0)$ |
| Feedforward reference velocity | $(0,0,10,0,0,0)$ |

**PID 2: target alignment SISO feedback**

| 항목 | 값 |
| --- | --- |
| $K_p$ | 0.9 |
| $K_i$ | **Single-arm 0.3 / dual-arm 0.5** |
| $K_d$ | 0.9 |
| Integral clipping | $[-10,10]$ |
| Output clipping | $[-15,15]$ |
| Reference bearing | 0 |

여기서 중요한 것은 PID 1의 **첫 번째 병진과 첫 번째 회전 channel만 활성**이라는 점이다. 전진 방향인 $z$의 접촉 depth feedback gain은 0이고, 전진은 $+z$의 **10 mm/s feedforward**로 생성한다. $y$ 횡이동은 목표 bearing에 대한 별도 PID 2가 생성한다. 따라서 이 pushing 설정을 `6축 pose 전체를 0으로 만드는 PID` 또는 `leader가 일정 접촉 깊이를 feedback으로 유지하는 force controller`라고 설명하면 안 된다. [원문 Table 8, Figure 5, PDF pp. 11, 32]

§5.7의 일반 설명은 leader에 같은 controller와 parameter를 사용한다고 서술하지만, **Table 8에는 PID 2의 integral gain이 single-arm과 dual-arm에서 다르게 기재**되어 있다. 본 정리는 그 차이를 보존한다.

### 9.4 Dual-arm follower — Table 9

| 항목 | 값 |
| --- | --- |
| $\mathbf K_p$ | $\mathrm{diag}(5,0,5,1,0,0)$ |
| $\mathbf K_i$ | $\mathrm{diag}(0.5,0,0.5,0.1,0,0)$ |
| $\mathbf K_d$ | $\mathrm{diag}(0.5,0,0.5,0.1,0,0)$ |
| Integral clipping | 모든 성분 $[-200,200]$ |
| Feedback reference pose | $(0,0,3,0,0,0)$ |
| Feedforward reference velocity | $(0,0,0,0,0,0)$ |

Follower는 첫 번째 병진, normal depth, 첫 번째 회전 channel을 제어한다. Leader와 달리 normal depth feedback이 활성이고 reference depth는 3 mm다. 목표점에 독자적으로 전진하는 feedforward는 없다. [원문 Table 9, §3.3.4, PDF pp. 12, 32]

### 9.5 Tall object를 위한 reference shear 변경

Tall object 실험에서는 기본값에서 첫 번째 성분만 다음처럼 바꾼다.

$$
\text{Leader reference pose}=(0.5,0,0,0,0,0),
$$

$$
\text{Follower reference pose}=(-0.5,0,3,0,0,0).
$$

저자들은 그 결과 **미는 쪽에는 약한 downward force, 지지하는 쪽에는 약한 upward force**가 생겨 선행 edge가 바닥에 걸리는 것을 줄였다고 설명한다. **설정값은 ±0.5 mm의 접촉 상태 offset이지 ±0.5 N의 힘 명령이 아니다.** 이를 N으로 바꾸는 stiffness·force calibration이나 실제 양팔 force 분배 수치는 제공되지 않는다. [원문 §5.7.2, PDF p. 21]

이 변경 뒤에도 tall objects를 foam 위에서 밀면 선행 edge가 걸렸고, 그 실험은 MDF 위에서만 수행할 수 있었다.

## 10. 힘·접촉 정보 처리의 전체 연결

### 10.1 센서 입력에서 행동까지

```text
접촉에 의한 TacTip 피부·pin 변형
    ↓ 내부 USB 카메라
Marker image
    ↓ crop / median blur / adaptive threshold / resize / normalization
128×128 tactile image
    ↓ GDN
6D contact pose-and-shear mean + uncertainty
    ↓ SE(3) mean / covariance 변환
현재 촉각 observation
    + 로봇 sensor pose 변화로 전파한 이전 belief
    ↓ discriminative Bayesian filter
Filtered local contact pose-and-shear
    ↓ reference와의 SE(3) error → log map
과업별 gain의 MIMO PID
    + frame 변환된 feedforward velocity
    + pushing인 경우 target-bearing SISO PID의 횡속도
    ↓
Cartesian end-effector velocity → robot arm
```

[원문 Figure 1·3–5, §3, PDF pp. 2, 4–12]

### 10.2 어떤 접촉 정보를 왜 사용하는가

| 정보 | 처리 | 행동에서의 역할 |
| --- | --- | --- |
| 깊이·기울기에 따른 marker pattern | GDN의 contact pose 성분 추정 | Tracking·surface-following·follower의 활성 channel에서 접촉 reference 유지 |
| 접선 변위·비틀림에 따른 marker pattern | GDN의 shear 성분 추정 | 물체의 tangential/rotational motion에 반응; 과업별 shear feedback |
| 영상별 추정 uncertainty | 관측 covariance 구성 및 Bayesian fusion | 모호한 single-frame 추정이 곧바로 큰 제어 오차로 전달되는 것을 줄임 |
| 로봇 자신의 pose 변화 | SE(3) prediction | 영상 추정에 시간적인 기하 관계를 추가 |
| 목표 bearing | Reference frame에서 SISO PID | Pushing 방향을 목표 쪽으로 바꾸는 횡이동 생성 |
| Reference shear offset | Tall object의 leader/follower reference 변경 | 정성적으로 설명된 아래·위 방향 지지 효과 생성 |

### 10.3 이 논문이 수행하지 않는 힘 처리

원문에는 별도 손목 F/T를 이 제어 loop에 결합하거나, marker 영상을 N·N·m 단위 wrench로 변환하는 과정이 없다. Normal contact depth와 shear reference를 통해 접촉을 조절하지만, **목표 normal force 추종, friction coefficient estimation, force-threshold-based collision detection, pressure distribution reconstruction**을 이 논문의 구현 메소드로 추가해서는 안 된다. [원문 §3–4, §5.7.2의 확인 범위]

또한 uncertainty output은 `slip probability`가 아니다. Slip은 모호성의 원인으로 논의되며, 명시적 slip label이나 detector를 사용하여 dataset을 정제하는 것은 §6.1의 후속 가능성으로 남는다. Sensor hardware가 slip 검출에 사용된 적 있다는 선행연구 소개와 본 논문의 구현을 구분한다.

## 11. Perception과 filter의 평가

### 11.1 Figure 11 — 영상에 어떤 상태 정보가 보이는가

Marker centroid에 Gaussian kernel을 놓아 **미변형 영상 대비 marker density 변화**를 시각화한다. Kernel width는 평균 marker 간격에 해당하는 15 pixel로 고정한다. 저자들은 중심의 낮은 density 영역 크기가 contact depth에, 위치가 sensor orientation에, 주변부 density가 translational shear에, 접촉 영역의 더 미세한 변화가 rotational shear에 관련된다고 설명한다. [원문 §5.1, Figure 11, PDF pp. 13–15]

이는 학습 가능성을 뒷받침하는 관찰이지, 각 pixel에서 힘을 계산한 calibration 결과가 아니다. Rotational shear에 해당하는 변화가 상대적으로 미세하다는 설명은 이후 그 성분의 추정 오차가 큰 결과와 함께 읽어야 한다.

### 11.2 Table 1 — CNN과 GDN의 single-image 추정

각 모델을 서로 다른 random initialization으로 10개씩 학습하고, 동일한 2000 test sample에서 성능을 비교했다. 아래 수치는 **모델 10개의 평균 ± 표준편차**다. 표의 성분명·단위는 원문 표기를 그대로 유지한다. [원문 §5.2, Table 1, PDF pp. 14, 16]

| 지표 | CNN regression | GDN |
| --- | --- | --- |
| MSE / mean NLL | 1.43 ± 0.02 | **−7.20 ± 0.25** |
| MAE $v_x$ (mm/s) | 0.448 ± 0.005 | 0.426 ± 0.005 |
| MAE $v_y$ (mm/s) | 0.451 ± 0.004 | 0.422 ± 0.005 |
| MAE $v_z$ (mm/s) | 0.164 ± 0.002 | 0.123 ± 0.002 |
| MAE $\omega_x$ (deg/s) | 0.88 ± 0.03 | 0.45 ± 0.01 |
| MAE $\omega_y$ (deg/s) | 1.04 ± 0.02 | 0.64 ± 0.01 |
| MAE $\omega_z$ (deg/s) | 1.44 ± 0.02 | 1.16 ± 0.02 |

Loss는 CNN의 weighted MSE와 GDN의 NLL이므로 두 수의 크기를 직접 비교해 improvement ratio를 계산하면 안 된다. GDN의 NLL 값에서 음수 부호도 보존해야 한다. 성분별 MAE에서는 모두 GDN의 평균값이 낮다.

Figure 12는 best-performing model의 prediction과 ground truth를 비교한다. GDN 점의 색은 **precision, 즉 inverse variance**다. 저자들은 높은 precision의 점이 ground-truth line 가까이에 나타나는 경향을 관찰했다. 다만 calibration curve나 명목 confidence interval coverage를 별도로 제시한 것은 아니다. [원문 Figure 12, §5.2, PDF pp. 14, 17]

**주의:** Method에서는 pose label을 exponential coordinates로 변환하지만, Tables 1–2와 해당 그림은 $v,\omega$ 및 mm/s·deg/s를 쓴다. 이 단위 문제는 14.2절에 기록했다. 본 표를 센서의 `힘 분해능` 또는 `mm 단위 접촉 위치 정확도`로 곧바로 재명명하지 않는다.

### 11.3 필터 평가에서 사용한 state dynamics — 실제 제어 실험과 구분

§5.3은 독립된 test contacts를 순서가 있는 sequence로 보고, **test label의 상대 pose 변화에 인위적인 Gaussian noise를 추가**하여 prediction transform을 만든다. [원문 §5.3, PDF pp. 14–15]

**원문 식 (23)–(24)**

$$
\bar{\mathbf T}_k=
\exp(\boldsymbol\psi_k^\wedge)\mathbf X_k\mathbf X_{k-1}^{-1},
\qquad
\boldsymbol\psi_k\sim\mathcal N(\mathbf0,\boldsymbol\Sigma_\psi),
$$

$$
\boldsymbol\Sigma_\psi=\sigma_\psi^2\mathbf I_{6\times6},
\qquad \boldsymbol\Sigma_\phi=\boldsymbol\Sigma_\psi.
$$

여기서는 실제로 가한 noise와 filter에 알려 준 covariance를 같게 설정한다. 따라서 이 결과를 **실물 pushing 도중 모든 시점의 ground-truth state와 비교한 filtering 성능**으로 해석해서는 안 된다. 온라인 과업의 prediction은 앞의 식 (15)처럼 robot sensor pose를 이용하고, 기본 noise는 $\sigma_\phi=0.5$다.

### 11.4 Table 2 — prediction이 정확할수록 filtering 효과가 커짐

각 GDN 모델 10개에 대해 네 noise level에서 반복했고, $\sigma_\psi=\infty$는 filter를 쓰지 않은 single-step GDN 결과로 표시한다. [원문 Table 2, PDF p. 17]

| MAE, 원문 단위 | $\infty$ | 10.0 | 1.0 | 0.1 | 0.01 |
| --- | --- | --- | --- | --- | --- |
| $v_x$, mm/s | 0.426 ± 0.005 | 0.422 ± 0.006 | 0.360 ± 0.007 | 0.160 ± 0.004 | 0.062 ± 0.004 |
| $v_y$, mm/s | 0.422 ± 0.005 | 0.421 ± 0.006 | 0.352 ± 0.006 | 0.161 ± 0.005 | 0.065 ± 0.005 |
| $v_z$, mm/s | 0.123 ± 0.002 | 0.123 ± 0.002 | 0.121 ± 0.002 | 0.098 ± 0.001 | 0.069 ± 0.003 |
| $\omega_x$, deg/s | 0.50 ± 0.01 | 0.49 ± 0.01 | 0.40 ± 0.01 | 0.18 ± 0.01 | 0.08 ± 0.01 |
| $\omega_y$, deg/s | 0.64 ± 0.01 | 0.62 ± 0.01 | 0.42 ± 0.02 | 0.18 ± 0.01 | 0.07 ± 0.01 |
| $\omega_z$, deg/s | 1.16 ± 0.01 | 1.15 ± 0.02 | 0.82 ± 0.02 | 0.30 ± 0.02 | 0.11 ± 0.02 |

Figure 13에서도 noise가 작을수록 prediction이 ground-truth line에 가까워지고 uncertainty가 줄어드는 경향을 보인다. Noise가 크면 single-image GDN에 가까워진다. **가장 좋은 열은 $\sigma_\psi=0.01$이라는 평가 조건의 결과**이며, 모든 실물 과정에서 같은 정확도를 달성했다는 의미가 아니다. [원문 §5.3, Figure 13, PDF pp. 15, 18]

## 12. 네 가지 로봇 과업의 실험

### 12.1 Task 1 — Object pose tracking

Leader arm이 표면·물체를 움직이고 TacTip을 장착한 follower가 접촉을 유지하며 따라간다. Follower reference depth는 6 mm, feedforward는 0이다. 두 종류의 실험을 수행한다. [원문 §5.4, PDF pp. 16–17]

**개별 성분 추종.** Flat surface를 work frame의 −x, y, z 방향으로 각각 200 mm 이동시키고, 이후 각 축 주위로 60° 회전시킨다. Figure 14에서는 축별 추종을 보기 쉽도록 translation 그림에서 rotation 변화를, rotation 그림에서 translation 변화를 제거했다. 따라서 전체 자유도의 raw trajectory를 그대로 겹친 그림은 아니다. [원문 §5.4.1, Figure 14, PDF pp. 16, 19]

**모든 성분을 동시에 변화시키는 추종.** Leader velocity를 주기 함수로 준다.

**원문 식 (25)**

$$
v_j(t)=\frac{2\pi b_j}{T}
\cos\left(\frac{2\pi t}{T}+\phi_j\right).
$$

Amplitude는 $(75,75,75,25,25,25)^T$로 병진은 mm, 회전은 degree다. Phase는 $(\pi/2,0,0,0,0,0)^T$, period는 30 s이고, 3주기인 90 s를 실행한다. Flat surface와의 직접 접촉 외에도 Rubik’s cube, mustard bottle, soft foam ball을 두 팔 사이에 유지하면서 추종한다. [원문 §5.4.2, Figure 15, PDF pp. 16–17, 20]

두 팔의 pose와 timestamp를 기록하여 사후에 대응시킨 결과가 제시된다. 개별 성분과 복잡한 동시 운동을 추종하는 시연이지만, tracking RMSE나 성공률을 통계표로 제시한 실험은 아니다.

### 12.2 Task 2 — Surface-following

Curved ramp에서는 reference depth 3 mm, reference sensor frame의 y방향 10 mm/s feedforward를 사용한다. Hemisphere에서는 정상부에서 45° 간격의 8방향으로, 접선 속도 10 mm/s로 이동한다. [원문 §5.5, Figure 16–17, PDF pp. 17–18, 21–22]

자세 궤적은 센서가 법선 정렬 상태로 곡면을 따라가는 것을 보여 준다. Ramp에서는 작은 횡방향 drift가 나타나고, 저자들은 표면의 약간의 기울기가 원인일 것으로 추측한다. Shear feedback은 비활성이지만 filter 내부에서는 해당 정보가 사용된다. 일정한 힘 추종이나 곡면 형상의 완전한 복원을 평가한 실험은 아니다.

### 12.3 Task 3 — Single-arm pushing

Right-angle adaptor를 사용하고, sensor end-effector를 지지면에서 45 mm 위에 둔다. 원문의 시작 위치는 work frame의 지지면에 평행한 yz평면에서 **$(y,z)=(-250,100)$ mm**, target은 **$(0,375)$ mm**다. 물체는 sensor 중앙 앞에 놓고 접촉면이 sensor 축에 대략 수직이 되도록 준비한다. [원문 §5.6, PDF pp. 18–19]

이 배치는 target까지 방향을 바꿔야 하므로 단순 직진 밀기가 아니다. 네 geometric object를 MDF·foam 위에서 밀고, 각 조건에 대해 5회 반복한다. 이전 연구의 triangular prism은 이후 dual-arm에서 두 팔이 flat surface에 접촉하는 조건으로 사용하기 어려워 제외했다.

**Final target error의 정의**

종료 시 **target에서 sensor–object contact normal까지의 수직 거리**다. 물체 중심의 도달 오차, 최종 orientation 오차, tip 중심과 target의 Euclidean distance와 다르다. 종료 판정의 20 mm도 이 표의 error threshold가 아니다. [원문 §5.6, Table 3, PDF pp. 19, 22]

**Table 3: 독립된 5회 시험, 평균 ± 표준편차**

| 물체 | Foam, mm | MDF, mm |
| --- | --- | --- |
| Blue square | 0.50 ± 0.56 | 4.45 ± 0.78 |
| Blue circle | 6.93 ± 0.06 | 9.45 ± 0.13 |
| Red square | 1.88 ± 0.71 | 4.38 ± 0.77 |
| Yellow hexagon | 0.33 ± 1.32 | 2.87 ± 0.68 |

Figure 18에는 EEF trajectory와 시작·종료의 대략적인 object pose가 표시된다. 원형 물체의 평균 error가 다른 물체보다 크다. 저자들은 원형은 10 mm 이내, 다른 물체는 5 mm 이내로 접근했다고 설명하지만, 표는 평균과 표준편차이며 모든 trial의 최댓값은 아니다. [원문 §5.6, Figure 18, PDF pp. 19, 23]

### 12.4 Task 4 전반 — 짧은 물체의 dual-arm pushing

동일한 시작점·목표에 대해 follower를 leader의 대략 반대편에 놓고, 반대쪽 접촉면의 법선에 정렬한다. Leader는 pushing controller, follower는 tracking/stabilising controller를 실행한다. MDF와 foam에서 같은 네 물체를 각각 5회 밀었다. [원문 §5.7–5.7.1, Figure 19, PDF pp. 19–20, 24]

**Table 4: 독립된 5회 시험, 평균 ± 표준편차**

| 물체 | Foam, mm | MDF, mm |
| --- | --- | --- |
| Blue square | 4.43 ± 0.25 | **5.24 ± 0.24** |
| Blue circle | 4.46 ± 3.35 | 3.58 ± 2.04 |
| Red square | 4.97 ± 0.18 | 4.28 ± 0.15 |
| Yellow hexagon | 4.43 ± 0.31 | 4.44 ± 0.62 |

Circular prism은 single-arm보다 평균 error가 작아졌다. 하지만 표를 비교하면 **모든 물체·지지면에서 dual-arm의 error가 개선된 것은 아니다.** 예를 들어 foam 위 blue square는 single-arm 0.50 mm, dual-arm 4.43 mm다. 이는 원문의 두 표를 비교한 해설이지 추가 실험 결과가 아니다.

원문 §5.7.1의 ‘모든 물체에서 5 mm 미만’이라는 문장과 Table 4의 blue square/MDF **5.24 mm**는 일치하지 않는다. 이 정리에서는 수치를 고치지 않고 남긴다.

### 12.5 Task 4 후반 — Tall object 안정화

Double-height geometric objects 4종과 everyday objects 5종을 dual-arm으로 민다. 저자들은 이 tall object들이 single-arm에서 넘어지기 쉬워 follower의 안정화가 필요하다고 설명한다. Reference pose에는 앞에서 설명한 ±0.5 mm shear offset을 적용했다. [원문 §5.7.2, PDF pp. 20–21]

**Foam에서는 선행 edge가 걸려 성공하지 못했으므로, 보고된 결과는 MDF 조건뿐**이다. [원문 §5.7.2, §6.2, PDF pp. 21, 25]

**Table 5: MDF, 독립된 5회 시험, 평균 ± 표준편차**

| 물체 | Final target error, mm |
| --- | --- |
| Tall blue square | 3.62 ± 0.31 |
| Tall blue circle | 7.11 ± 2.18 |
| Tall red square | 4.94 ± 0.19 |
| Tall yellow hexagon | 4.73 ± 0.38 |
| Mustard bottle | 6.24 ± 2.33 |
| Cleaner bottle | 7.02 ± 0.95 |
| Windex spray | 4.59 ± 1.36 |
| Glass bottle | 6.42 ± 0.39 |
| Coffee tin | 4.81 ± 2.09 |

[원문 Table 5, Figure 20, PDF p. 25]

평균 error는 모든 물체에서 7.5 mm 미만이지만, 이를 각 trial의 최대 error 보장으로 바꾸지 않는다. 결과가 보여 주는 것은 해당 제어·접촉·지지면 조건에서의 안정화와 target 접근이며, 임의의 tall object나 부드러운 지지면에서의 전도 방지 보장은 아니다.

## 13. Appendix A–C — 필터·제어를 뒷받침하는 수학

부록은 별도 기능이 아니라 앞의 uncertainty 변환, state prediction, fusion, velocity 합성을 정의하는 근거다. 아래에서는 각 부록이 계산 pipeline의 어디에 사용되는지와 핵심 식을 연결한다. [원문 Appendix A–C, PDF pp. 28–31]

### 13.1 Appendix A: pose, twist, adjoint, left Jacobian

**원문 식 (26)–(29)**

$$
\mathbf X=
\begin{bmatrix}
\mathbf C&\mathbf r\\
\mathbf0^T&1
\end{bmatrix}\in\mathrm{SE}(3),
\qquad
\mathbf C\in\mathrm{SO}(3),\quad\mathbf r\in\mathbb R^3.
$$

$$
\boldsymbol\xi=
\begin{bmatrix}\boldsymbol\rho\\\boldsymbol\phi\end{bmatrix},
\qquad
\boldsymbol\xi^\wedge=
\begin{bmatrix}
\boldsymbol\phi^\wedge&\boldsymbol\rho\\
\mathbf0^T&0
\end{bmatrix},
\qquad
\mathbf X=\exp(\boldsymbol\xi^\wedge).
$$

$\wedge$는 vector를 Lie algebra matrix로, $\vee$는 그 역으로 변환한다. 본 논문의 순서는 **병진 먼저, 회전 나중**이다. 원문은 Modern Robotics의 순서와 반대임을 명시한다. [원문 Appendix A, PDF pp. 28–29]

**원문 식 (30)–(31): adjoint**

$$
\mathrm{Ad}(\mathbf X)=
\begin{bmatrix}
\mathbf C&\mathbf r^\wedge\mathbf C\\
\mathbf0&\mathbf C
\end{bmatrix},
\qquad
\mathrm{ad}(\boldsymbol\xi^\wedge)=
\begin{bmatrix}
\boldsymbol\phi^\wedge&\boldsymbol\rho^\wedge\\
\mathbf0&\boldsymbol\phi^\wedge
\end{bmatrix}.
$$

Group adjoint는 서로 다른 frame의 velocity twist 및 uncertainty를 옮기는 데 사용한다. $\mathbf r^\wedge\mathbf C$ 항이 포함되므로 단순히 앞·뒤 3-vector를 각각 같은 rotation으로 돌리는 것만으로 항상 충분한 것은 아니다. 이는 위 행렬의 구조에 대한 해설이다.

BCH 근사는 두 작은 pose 변환의 합성과 logarithm 사이를 연결한다. Left Jacobian과 그 inverse는 급수로 표현한다. [원문 식 (32)–(34), PDF p. 29]

$$
\mathcal J(\boldsymbol\xi)=
\sum_{n=0}^{\infty}
\frac{[\mathrm{ad}(\boldsymbol\xi^\wedge)]^n}{(n+1)!},
\qquad
\mathcal J(\boldsymbol\xi)^{-1}=
\sum_{n=0}^{\infty}\frac{B_n}{n!}
[\mathrm{ad}(\boldsymbol\xi^\wedge)]^n.
$$

$B_0=1$, $B_1=-1/2$, $B_2=1/6$ 등의 Bernoulli number를 사용한다. 논문에서는 필요한 Jacobian과 inverse를 보통 **2차 항까지 잘라 계산**하며, 그 근사로 충분했다고 보고한다. 로봇 manipulator Jacobian을 학습했다는 뜻이 아니다.

### 13.2 Appendix B: SE(3) uncertainty와 prediction

Mean을 left perturbation으로 표현한 경우, SE(3) PDF에는 Jacobian determinant에 따른 정규화 인자가 들어간다.

**원문 식 (35)–(36)**

$$
p(\mathbf X)=\beta(\boldsymbol\epsilon)
\exp\left(-\frac12\boldsymbol\epsilon^T
\boldsymbol\Sigma^{-1}\boldsymbol\epsilon\right),
\qquad
\beta(\boldsymbol\epsilon)=
\frac{\eta}{\lvert\det\mathcal J(\boldsymbol\epsilon)\rvert},
$$

$$
\boldsymbol\epsilon=\ln(\mathbf X\bar{\mathbf X}^{-1})^\vee.
$$

$\beta$가 일반적으로 constant가 아니므로 SE(3) 위 PDF는 원래 perturbation의 Gaussian 형태와 같지 않다.

**원문 식 (37)–(38)**

$$
\boldsymbol\xi=\ln(\mathbf X)^\vee
\approx\boldsymbol\mu+\mathcal J(\boldsymbol\mu)^{-1}\boldsymbol\epsilon,
$$

$$
\boldsymbol\xi\sim\mathcal N\!\left(
\boldsymbol\mu,
\mathcal J(\boldsymbol\mu)^{-1}
\boldsymbol\Sigma
\mathcal J(\boldsymbol\mu)^{-T}
\right).
$$

이 관계를 역으로 사용한 것이 식 (14)의 **GDN covariance → SE(3) perturbation covariance** 변환이다.

이어 식 (39)–(42)는 sensor motion과 noise를 갖는 SE(3) 변환을 곱하면, mean은 $\bar{\mathbf T}\bar{\mathbf X}$로, covariance는 $\mathrm{Ad}(\bar{\mathbf T})\boldsymbol\Sigma\mathrm{Ad}(\bar{\mathbf T})^T+\boldsymbol\Sigma_\phi$로 전파됨을 작은 perturbation 근사 아래 유도한다. 이것이 Algorithm 2 prediction의 근거다. [원문 Appendix B, PDF pp. 29–30]

### 13.3 Appendix C: 왜 iterative fusion이 필요한가

Euclidean Gaussian 두 개의 정규화된 곱은 다시 Gaussian이지만, SE(3) PDF의 곱은 일반적으로 같은 family에 속하지 않는다. Appendix C는 perturbation이 충분히 작으면 $\mathcal J(\boldsymbol\epsilon)\approx\mathbf I$로 두어 정규화 인자를 근사하고, 한 operating point 주변의 tangent-space에서 두 분포를 결합한다. [원문 식 (43)–(45), PDF p. 30]

**원문 식 (46)–(47): 같은 operating point의 좌표로 변환**

$$
\boldsymbol\mu'_i=-\mathcal J(\boldsymbol\xi_i)\boldsymbol\xi_i,
\qquad
\boldsymbol\Sigma'_i=
\mathcal J(\boldsymbol\xi_i)\boldsymbol\Sigma_i
\mathcal J(\boldsymbol\xi_i)^T,
\qquad i\in\{1,2\}.
$$

여기서 $\boldsymbol\xi_i=\ln(\bar{\mathbf X}\bar{\mathbf X}_i^{-1})^\vee$다. **$\boldsymbol\mu'_i$의 음수 부호**는 PDF의 실제 수식에 있으며, extraction 과정에서 탈락하기 쉬운 부분이다.

**원문 식 (49): tangent-space Gaussian의 곱**

$$
\boldsymbol\Sigma'_*= 
\left((\boldsymbol\Sigma'_1)^{-1}
+(\boldsymbol\Sigma'_2)^{-1}\right)^{-1},
$$

$$
\boldsymbol\mu'_*= 
\boldsymbol\Sigma'_*
\left((\boldsymbol\Sigma'_1)^{-1}\boldsymbol\mu'_1
+(\boldsymbol\Sigma'_2)^{-1}\boldsymbol\mu'_2\right).
$$

식 (50)–(52)는 이 nonzero-mean perturbation을 새로운 SE(3) mean 주변의 zero-mean perturbation으로 다시 표현한다. 그 변환은 일반적으로 닫힌 형태로 mean을 구하기 어려워 operating point를 반복 갱신한다.

**원문 식 (53)–(54)**

$$
\bar{\mathbf X}_*\approx
\exp((\boldsymbol\mu'_*)^\wedge)\bar{\mathbf X},
\qquad
\boldsymbol\Sigma_*\approx\boldsymbol\Sigma'_*,
$$

$$
\bar{\mathbf X}\leftarrow
\exp((\boldsymbol\mu'_*)^\wedge)\bar{\mathbf X}.
$$

이를 원래 mean·covariance와 inverse Jacobian으로 전개한 구현이 앞의 Algorithm 3다. 원문은 일반적인 수렴이 3–4회이고 실제로는 5회 고정한다고 설명한다. [원문 Appendix C, PDF p. 31]

**기여의 범위도 구분해야 한다.** 저자들은 fusion algorithm 자체가 Barfoot & Furgale (2014)의 방법과 본질적으로 같음을 인정한다. 차이는 기존 Gauss–Newton/Mahalanobis minimisation 방식 대신, **SE(3) PDF의 정규화된 곱과 비선형 방정식의 반복 근사라는 대수적 유도**를 제시한다는 점이다. 이를 완전히 새로운 fusion algorithm을 처음 제안한 것으로 설명하지 않는다.

## 14. 한계, 미명시 사항, 원문 내부의 주의점

### 14.1 저자들이 명시한 한계와 후속 과제

**Shear 추정 오차.** Slip이 tactile aliasing을 만들며 single-image CNN·GDN의 shear 오차가 여전히 크다. Slip이 없는 표본만 수집하면 단순화할 여지가 있지만, 실제로 제한하기 어렵고 큰 접촉 깊이만 허용하게 되어 적용 범위를 줄일 수 있다. Slip detector로 occurrence label을 추가하거나 수집 중 slip을 줄이는 것은 후속 가능성이다. [원문 §6.1, PDF pp. 22–23]

**Training trajectory의 제한.** 학습은 normal-contact 후 parallel shear의 두 단계다. 실제 과업처럼 normal과 parallel motion이 동시에 변하고 궤적 형태가 다른 데이터를 포함하면 일반화가 나아질 수 있다고 저자들이 제안한다. 현재 논문에서 그 확장 실험을 완료한 것은 아니다. [원문 §6.1, PDF p. 23]

**표면 feature의 제한.** Flat 또는 완만한 곡면을 중심으로 다룬다. Edge에 대해서는 contact pose 자체가 5성분일 수 있어, 그 위에 3성분 shear를 더해 현재처럼 하나의 6D pose로 합치는 것이 간단하지 않다. 별도 pose/shear controller 출력을 적절하게 결합하는 방법은 후속 문제로 남는다. [원문 §6.1]

**지지면과 tall object.** Tall objects는 foam에서 edge가 걸렸다. 일부를 들어 올려 이동하는 전략은 가능성으로 언급하지만 본 실험의 구현 범위 밖이다. [원문 §6.2, PDF p. 25]

**Planning 부재.** 팔 사이 충돌, joint limit, singularity 접근 등을 미리 피하는 planner가 없다. Local control objective만으로 global task objective를 달성하지 못하는 경우나 목표 position과 orientation을 함께 맞추는 조작도 후속 과제다. [원문 §6.2]

**양팔 구성의 범위.** 현재는 leader–follower이며, 두 팔이 모두 능동적으로 역할을 분담하는 구성과 tactile gripper·다지 손으로의 확장은 향후 가능성이다. 이를 본 논문에서 실험한 dexterous hand manipulation 결과로 포함하지 않는다. [원문 §6.2, PDF pp. 25–26]

### 14.2 원문 내부의 불일치·불명확성

아래는 외부 자료로 고친 내용이 아니라 **첨부 원문 안에서 서로 다른 표기가 있는 지점**이다. 잘못된 extraction과 원문 자체의 불일치를 구분하여 기록했다.

| 항목 | 원문의 표기 | 이 정리에서의 처리 |
| --- | --- | --- |
| Tip 크기 | §4.2: 직경 40 mm. §3.3.3: 반지름 20 mm. §5.4.1: `sensor tip radius of 40 mm` | 주 사양은 직경 40 mm와 반지름 20 mm로 기록하되, tracking 해설의 radius 40 mm 표현은 다른 두 곳과 충돌한다고 명시 |
| 상태 label과 평가 단위 | §3.1.3: pose를 logarithm으로 변환한 exponential coordinates. Tables 1–2·그림: $v,\omega$와 mm/s·deg/s. §3.2.2 process noise도 속도 단위로 설명 | 원문 성분명·단위를 보존. 논문에 없는 시간 정규화·단위 환산을 보충하지 않음 |
| GDN unfiltered 수치 | Table 1 $\omega_x$: 0.45 ± 0.01. Table 2 $\sigma_\psi=\infty$: 0.50 ± 0.01 | 두 값을 각각 보존. Table 2를 Table 1과 동일하다고 설명하면서 수치를 고치지 않음 |
| GDN $\omega_z$ 표준편차 | Table 1: 1.16 ± 0.02. Table 2의 unfiltered: 1.16 ± 0.01 | 각 표의 원래 수치 유지 |
| Dual-arm short-object 성능 | §5.7.1: 모든 물체에서 5 mm 미만이라고 서술. Table 4 blue square/MDF: 5.24 ± 0.24 mm | 표 수치와 문장의 차이를 명시. 5 mm 이하로 수치를 수정하지 않음 |
| Leader 제어 파라미터 | §5.7: single-arm과 같은 parameter라고 설명. Table 8: target PID $K_i$가 single 0.3, dual 0.5 | Table 8의 구체적인 설정 차이를 기록 |
| 식 참조 | §3.2.1에서 correction step을 설명하며 식 (7)을 가리키는 문구가 있지만, 앞에서 correction으로 정의한 것은 식 (8) | Prediction 식 (7), correction 식 (8), discriminative correction 식 (10)–(11)로 내용을 구분 |

[원문 §3.1.3, §3.2.1–3.2.2, §3.3.3, §4.2, §5.4.1, §5.7, Tables 1–2·4·8, PDF pp. 6, 9–10, 12–13, 16–17, 20, 24, 32]

특히 Appendix C 식 (46)–(47)의 mean 변환, 식 (51)–(52)의 부호, γ sampling 범위, NLL 값의 음수는 실제 PDF 이미지를 기준으로 확인했다. 텍스트 추출 결과에서 음수가 빠진 것을 논문 오기로 취급하지 않았다.

### 14.3 원문만으로 확정할 수 없는 구현·성능 사양

| 항목 | 확인 범위 |
| --- | --- |
| Tactile camera·high-level control 주파수 | 미명시. libfranka 1 kHz만 명시 |
| Force/torque calibration | Newton 또는 N·m 변환 모델·측정 오차 미제시 |
| Sensor 최소·최대 힘 성능 | 최대 측정 범위, 최소 감지 힘, 힘 분해능·정확도 미명시 |
| Perception latency·동기화 | 두 팔의 pose·timestamp를 기록하고 대응시킨다고 설명하나 정량 latency·동기화 오차는 미명시 |
| 촉각 입력 전처리 세부 | Adaptive threshold의 window/상수, resize interpolation 등 미명시 |
| 모델별 training time·CPU/GPU | 미명시 |
| Process noise의 timestep 변환 | Pose 표현과 속도 단위 사이의 구체적인 시간 scaling 미명시 |
| Filter covariance의 calibration | Precision과 error의 시각적 상관 및 MAE를 제시. Coverage·calibration error 지표는 미제시 |
| 물체·지지면 dynamics | 질량 일부는 제시. 마찰계수·CoM·inertia·surface stiffness의 정량표는 미제시 |
| Non-contact와 contact loss 처리 | 일반적인 재접촉 탐색·복구 state machine은 제시하지 않음 |
| 실험 초기 접촉 | 센서가 물체·표면에 준비된 상태의 실험을 설명. 임의 접근·최초 접촉 실패에 대한 평가로 확대하지 않음 |
| Safety·motion planning | Smooth trajectory가 속도·가속도·jerk 제한을 만족한다고 설명. Planner 부재는 명시된 한계 |
| 기여별 전체 과업 ablation | CNN/GDN·filter noise 비교는 있음. 네 로봇 과업 전체에 대한 모든 모듈 제거 비교는 제시하지 않음 |
| 전도·힘·시간의 정량 비교 | Tall object 안정화 시연은 있으나 force history·전도 확률·모든 과업의 완료시간 통계가 제공된 것은 아님 |

이 표의 ‘미명시’는 저자 코드에도 해당 처리가 없다는 단정이 아니다. 이번 정리에서 확인한 근거가 **첨부 출판본**이라는 의미다.

## 15. 원문을 다시 읽을 때의 위치 색인

### 15.1 핵심 메소드·환경·실험

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 문제의식, aliasing, 네 가지 기여 | §1, Figure 1, PDF pp. 1–2 / 인쇄 pp. 1024–1025 |
| Local/global pose, shear 및 tactile servoing 관련 연구 | §2, PDF pp. 3–4 / 인쇄 pp. 1026–1027 |
| 통합 pose/shear 정의와 모델링 가정 | §3.1.1, Figure 2, PDF pp. 4–5 |
| Sampling·학습 데이터·전처리 | §3.1.2–3.1.3, Algorithm 1, 식 (1)–(2), PDF pp. 5–6 |
| CNN regression·GDN·NLL·softbound·multi-dropout | §3.1.4–3.1.5, Figure 3, 식 (3)–(6), PDF pp. 6–8 |
| Discriminative filtering의 확률식 | §3.2.1, Figure 4, 식 (7)–(13), PDF pp. 8–9 |
| SE(3) prediction·observation 변환·fusion | §3.2.2, Algorithm 2–3, 식 (14)–(16), PDF pp. 8–10 |
| Pose error·PID·frame 변환 | §3.3.1–3.3.2, 식 (17)–(20), Figure 5(a), PDF pp. 10–11 |
| Target alignment·종료·leader–follower | §3.3.3–3.3.4, 식 (21)–(22), Figure 5(b), PDF pp. 11–12 |
| 로봇·TacTip·software | §4, Figure 6–10, PDF pp. 12–15 |
| Marker density와 pose/shear 관측 | §5.1, Figure 11, PDF pp. 13–15 |
| 모델·필터 정확도 | §5.2–5.3, Table 1–2, Figure 12–13, 식 (23)–(24), PDF pp. 14–18 |
| Object tracking | §5.4, 식 (25), Figure 14–15, PDF pp. 16–17, 19–20 |
| Surface-following | §5.5, Figure 16–17, PDF pp. 17–18, 21–22 |
| Single-arm pushing | §5.6, Table 3, Figure 18, PDF pp. 18–19, 22–23 |
| Dual-arm pushing | §5.7, Table 4–5, Figure 19–20, PDF pp. 19–21, 24–25 |
| 한계·후속 과제 | §6, PDF pp. 21–26 |
| 참고문헌 | References, PDF pp. 26–28 |

### 15.2 부록 수식과 실제 제어 설정

| 원문 범위 | 역할 |
| --- | --- |
| Appendix A, 식 (26)–(34), PDF pp. 28–29 | SE(3), exponential/log map, wedge/vee, adjoint, BCH, left Jacobian |
| Appendix B, 식 (35)–(38), PDF p. 29 | Left perturbation PDF와 exponential-coordinate Gaussian의 관계 |
| Appendix B, 식 (39)–(42), PDF p. 30 | Probabilistic transform과 prediction mean·covariance |
| Appendix C, 식 (43)–(47), PDF p. 30 | Concentrated Gaussian 근사와 공통 operating point로의 좌표 변환 |
| Appendix C, 식 (48)–(54), PDF p. 31 | Gaussian product·SE(3) mean 복원·fixed-point iteration |
| Appendix D, Table 6–9, PDF p. 32 / 인쇄 p. 1055 | Tracking, surface-following, pushing leader와 follower의 gain·clipping·reference |

**논문 전체의 연결:** 접촉 기하와 post-contact shear를 하나의 local SE(3) 상태로 표현하고, GDN으로 그 상태와 uncertainty를 추정한다. Sensor kinematics를 이용한 Bayesian filtering으로 추정을 개선한 뒤, 과업별로 선택한 contact-state feedback과 feedforward·target alignment를 합성하여 부드러운 속도 제어를 수행한다. 핵심은 **힘의 직접 복원**이 아니라 **접촉 변형 상태의 표현·불확실성 처리·운동 제어의 결합**이다.
