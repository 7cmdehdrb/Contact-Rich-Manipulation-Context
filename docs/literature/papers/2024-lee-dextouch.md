# DexTouch: Learning to Seek and Manipulate Objects With Tactile Dexterity

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 조사 · B1](../reviews/2026-09-16_binary-tactile-wrench-rl.md#b1)

정리일: **2026-09-17**. 사용자가 제공한 **IEEE Robotics and Automation Letters 출판본 PDF 8쪽 전체**를 기준으로 작성한 개별 논문 정독 노트다. 기존 [Binary Tactile·F/T 신규 조사](../reviews/2026-09-16_binary-tactile-wrench-rl.md#b1)의 **B1**에 해당한다. 해당 조사에서 사용한 arXiv 판본의 내용을 출판본에 자동 합치지 않았다.

[DOI](https://doi.org/10.1109/LRA.2024.3478571) · [저자 프로젝트](https://lee-kangwon.github.io/dextouch/) · [공개 원문 식별자](https://arxiv.org/abs/2401.12496)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | DexTouch: Learning to Seek and Manipulate Objects With Tactile Dexterity |
| 저자 | Kang-Won Lee, Yuzhe Qin, Xiaolong Wang, Soo-Chul Lim |
| 게재 | IEEE Robotics and Automation Letters, Vol. 9, No. 12, pp. 10772–10779, December 2024 |
| DOI | 10.1109/LRA.2024.3478571 |
| 출판 이력 | Received 2024-05-29; accepted 2024-09-29; publication 2024-10-11; current version 2024-10-21. 출판본 첫 페이지 표기 기준 |
| 읽은 자료 | 첨부된 IEEE 출판본 8쪽. Abstract, §I–VI, 식 (1)–(4), Fig. 1–6, Table I–III, References |
| 첨부 파일 | `Lee 등 - 2024 - DexTouch Learning to Seek and Manipulate Objects With Tactile Dexterity.pdf` |
| 파일 SHA-256 | `1acdf1b6ca87db993050706032e60df71836c4675e02151219acff3a6fdb863a` |
| 이번 정독의 범위 밖 | 공개 코드 실행·정적 구현 검증, 정책 재학습, 실물 재현, 저자 보충 영상 전체 확인, 센서 제조사 데이터시트 검증 |

이 문서의 **PDF p. 1–8은 인쇄 페이지 10772–10779에 대응**한다. 본문에서 처음 위치를 지정할 때 두 페이지를 함께 적고, 이후에는 절·식·표 번호와 PDF 페이지로 추적할 수 있게 했다. 원문에 없는 수식의 전개·차원 합산은 **해설**로 표시한다. 독립적인 프로젝트 적용안은 이 개별 노트에 포함하지 않는다.

## 1. 연구가 해결하려는 문제

### 1.1 정확한 위치를 볼 수 없지만 대략적인 존재 영역은 아는 조작

저자들은 높은 선반 안의 물건 꺼내기, 어두운 곳에서 스위치 찾기, 시각적으로 손잡이를 확인하지 못한 상태에서 문 열기를 동기로 제시한다. 이런 상황에서 사람은 물체의 정확한 위치를 보지 못해도 **대략 어디에 있을지에 대한 사전정보와 접촉을 통해 얻는 정보**를 결합한다. DexTouch의 목적도 이 정보 공백을 촉각으로 보완하여 로봇 팔과 다지손이 물체를 찾고 조작하게 하는 것이다. [원문 Abstract, §I, PDF p. 1 / 10772]

따라서 이 논문의 blind는 모든 사전정보의 부재를 뜻하지 않는다. 물체가 나타나는 영역과 과업이 주어지며, 파지 과업에는 운반 목표점도 주어진다. 정책 실행 중 현재 물체의 정확한 pose를 시각으로 계속 관측하지 않는다는 것이 핵심이다. 반면 학습에서는 시뮬레이터의 물체 상태를 critic과 보상 계산에 사용한다. [§IV-A, IV-C, V-A, PDF pp. 3–5]

### 1.2 저자가 제시하는 접근

| 문제 | DexTouch의 접근 |
| --- | --- |
| 물체의 실제 위치를 모르므로 접근 이후 상호작용을 조절하기 어려움 | 손가락·손바닥의 접촉 분포를 관측하고 팔과 손가락을 함께 제어 |
| 다자유도 팔·손의 동작을 일일이 모델링하기 어려움 | IsaacGym에서 PPO로 과업별 정책 학습 |
| 시뮬레이션 힘과 실제 센서 출력이 정밀하게 일치하지 않음 | FSR 신호를 부위별 binary contact로 변환 |
| 물체 탐색과 조작 성공 사이의 학습 보상 부족 | 접근 보상과 과업 실행 보상으로 분해 |
| 실행 때 얻을 수 있는 정보만으로 학습하기 어려움 | Actor와 critic의 관측을 다르게 하는 asymmetric training |

세 과업은 **물체 찾아 파지·운반하기, 문손잡이 찾아 문 열기, 밸브 찾아 회전시키기**다. 단순한 손 안 물체 회전에 한정하지 않고 팔의 탐색·이동과 손가락 조작을 함께 학습하는 것이 저자들이 강조하는 확장이다. 여러 과업을 하나의 범용 정책으로 동시에 수행했다고 설명하지는 않는다. [§I–III, IV-C]

### 1.3 이 논문의 결과를 읽는 핵심

실행 정책은 16개 접촉 bit만으로 구성되지 않는다. **관절 위치·속도, 손바닥 pose·속도, 손끝 상대 위치, 과업 사전정보와 binary tactile을 함께 받는 MLP**다. 또한 전이가 성공했다는 사실과 binary가 continuous tactile보다 우수하다는 주장은 다르다. 이 출판본은 tactile 유무·감도·배치와 손목 F/T를 비교하지만, 동일 조건의 binary 대 continuous tactile 비교는 제시하지 않는다. [§IV-A–C, §V, Table II–III]

## 2. Related Work — 원문이 설정한 비교 구도

아래는 **DexTouch의 §II가 선행연구를 설명한 내용**이다. 표에 나온 인용 논문들을 이번 작업에서 별도로 정독했다는 뜻이 아니다. [원문 §II, PDF pp. 1–2 / 10772–10773]

| 범주 | 원문 인용 | 인정하는 성과 | DexTouch가 구분하는 지점 |
| --- | --- | --- | --- |
| 모델 기반 dexterous manipulation | [10], [11] | 로봇·접촉의 동역학 모델에 기반한 다지 조작 | 더 복잡한 과업으로 확장할 때 모델링의 제약이 있음 |
| Deep RL 기반 dexterous manipulation | [12]–[16] | 병렬 시뮬레이션을 활용한 효과적 학습과 높은 성공률 | 많은 연구가 시각과 작은 범위의 in-hand manipulation에 집중했다고 설명 |
| 촉각 기반 안정 파지 | [17]–[24] | 물체 특성 보완, 미지·큰 물체 파지, 움직이는 물체의 적응적 파지, blind grasping | 모델이나 설계된 촉각 feedback loop의 복잡한 과업 확장에 한계가 있다고 설명 |
| 촉각 탐색·물체 인식 | [25]–[29] | 반복 파지로 물체 확인, 지속 접촉을 이용한 환경 모델링, 투명 물체 인식, clutter에서 pose 추정 | 저자들은 주로 낮은 자유도 gripper에서 구현된 인식 연구와 다지손 blind manipulation을 구분 |

Binary tactile을 이용해 sim-to-real 차이를 줄이는 선택은 선행연구 [6], *Rotating without Seeing: Towards In-hand Dexterity through Touch*를 따른다. DexTouch가 이진화를 처음 제안했다고 읽으면 안 된다. 이 논문의 비교 초점은 이 구성을 이용한 **팔·손 통합 blind manipulation과 촉각의 역할**이다. [§I, III-A, References [6], PDF pp. 1–2, 8]

## 3. 로봇 플랫폼과 센서 사양

### 3.1 플랫폼 구성

| 항목 | 출판본에 명시된 내용 | 구분·근거 |
| --- | --- | --- |
| 로봇 팔 | UR5e, 6 DoF | §III-A, PDF p. 2 |
| 로봇 손 | AllegroHand, 16 DoF | §III-A |
| 제어 관절 수 | 팔 6개 + 손 16개 = 22개 | 로봇 기구학적 자유도이며 관측 전체 차원과 다름 |
| 촉각 센서 | Force Sensing Resistor, FSR 총 16개 | 저항식 센서. 모델명·제품 번호는 미명시 |
| 배치 | 손가락마다 3개씩 총 12개, 손바닥 4개 | 손의 한쪽 면, fingertips·finger links·palm을 덮는 배치. Fig. 1–2 |
| 신호 취득 MCU | STM32F103 | §III-A |
| 실제 취득 신호 | 각 FSR의 전압 | 뉴턴 단위 force로 보정한 값을 actor에 넣는 방식으로 설명하지 않음 |
| 전압 sampling rate | 125 Hz | 이 시스템의 취득 설정. 제조사 최대 sampling rate가 아님 |
| 시뮬레이터 | IsaacGym | 물리 시뮬레이션과 대규모 병렬 RL 학습 |
| 정책·제어 주파수 | Simulation과 real 모두 10 Hz | 센서 취득 125 Hz, simulation step 약 60 Hz와 구분 |
| 저수준 제어 | 팔과 손 모두 joint-position target에 대한 PD controller | §IV-A, PDF p. 4 |

Fig. 2는 16개 센서가 손의 어느 부분에 있는지를 보여준다. 이 구성은 손 전체를 연속적으로 덮는 고해상도 촉각 피부가 아니다. **센서 ID가 접촉의 부위를 구분하고, 센서별 출력은 접촉 여부 하나로 축약된다.** 한 센서 내부의 접촉 중심, 전단력 방향, 접촉 면적은 정책 입력으로 제시하지 않는다. [§I, III-A, IV-A, Fig. 2]

### 3.2 원문에서 확인할 수 없는 장비 사양

| 사양 | 확인 결과 |
| --- | --- |
| FSR 제조사·정확한 모델·개별 센서 크기 | 미명시 |
| 최대 측정 하중·force range | 미명시 |
| 힘 분해능·정확도·반복성·히스테리시스 | 미명시 |
| 센서 부착 위치의 수치 좌표·센서 간격·손 표면 커버리지 비율 | 그림과 배치 개수는 있으나 수치 미명시 |
| ADC 분해능·회로 저항·전압-힘 보정식 | 미명시 |
| 저역통과 필터의 종류·차수·cutoff | 미명시 |
| 실물 접촉 전압 threshold | 기호 $\theta_{\mathrm{th}}$만 제시, 수치 미명시 |
| UR5e·Allegro의 하중 한계·속도 제한·PD gains | 이 논문에 구체 수치 미명시 |

뒤에서 나오는 **0.01 N과 0.3 N은 시뮬레이션 접촉 판정 설정**이다. FSR 제품의 최소 검출력·분해능·최대 측정 범위로 해석하면 안 된다. 논문에서 말하는 sensor sensitivity 비교는 우선 threshold 변경 실험의 의미다. [§III-A, V-A–C]

## 4. 원시 접촉 신호가 정책 입력으로 바뀌는 과정

### 4.1 실물: 전압 → 저역통과 필터 → threshold → 16bit

원문에 명시된 처리 순서는 다음과 같다. [원문 §III-A, PDF p. 2 / 10773]

1. 16개 FSR의 전압을 STM32F103에서 **125 Hz**로 읽는다.
2. 전압을 **low-pass filter**에 통과시켜 noise를 제거한다.
3. 처리된 신호를 main controller로 전송한다.
4. 선택한 전압 threshold $\theta_{\mathrm{th}}$에 따라 접촉/무접촉으로 변환한다.
5. 16개의 결과를 $o_t\in\{0,1\}^{16}$으로 정책의 다른 상태값과 함께 사용한다.

이 절의 설명을 기호로 옮기면 다음과 같다. **아래는 흐름을 설명하기 위한 표기이며 논문의 번호가 붙은 수식은 아니다.**

$$
\bar v_i[k]=\operatorname{LPF}(v_i)[k],
\qquad
o_{t,i}=\operatorname{Threshold}_{\theta_{\mathrm{th}}}
\bigl(\bar v_i[k(t)]\bigr),
\qquad i=1,\ldots,16.
$$

$v_i$는 센서 $i$의 전압, $\bar v_i$는 필터 출력, $o_{t,i}$는 정책 시점 $t$의 접촉 bit다. $k(t)$는 125 Hz 센서 sample을 10 Hz 정책 시점에 대응시키는 설명용 인덱스다. **원문은 이 대응에서 마지막 sample을 쓰는지, 여러 sample을 집계하는지 설명하지 않는다.** 회로의 접촉 시 전압 증감 방향과 threshold 경계의 부등호도 명시하지 않으므로 특정 회로식이나 비교 방향을 확정하지 않았다.

논문이 명시한 후처리는 **LPF와 threshold**까지다. Zero-offset 보정, baseline 적응, 센서별 threshold calibration, on/off 이중 임계값, debounce, moving majority vote, 통신 validity bit는 출판본에 기재되어 있지 않다. 이것들이 구현되지 않았다고 단정할 수는 없지만, DexTouch에서 사용했다고 기록할 근거도 없다.

### 4.2 Simulation: 센서별 net contact force의 크기 → binary

시뮬레이션에는 16개 virtual contact sensor를 둔다. 각 simulation step에서 센서별 net contact force $\mathbf F=[F_x,F_y,F_z]$의 크기 $\|\mathbf F\|$를 계산하고, **$\tilde\theta_{\mathrm{th}}=0.01\ \mathrm{N}$**을 사용해 접촉을 이진화한다. [§III-A, PDF p. 3 / 10774]

**해설용 표현:**

$$
f_{t,i}=\sqrt{F_{x,t,i}^{2}+F_{y,t,i}^{2}+F_{z,t,i}^{2}},
\qquad
o_{t,i}=\operatorname{Threshold}_{\tilde\theta_{\mathrm{th}}}(f_{t,i}).
$$

Simulation에서는 **힘의 크기**, real에서는 **필터링한 전압**을 threshold한다. 두 threshold는 기호도 다르며 물리 단위도 같다고 볼 수 없다. 이진화 뒤 두 환경의 actor가 받는 자료형과 부위별 접촉 표현을 맞추는 구조다. 힘 벡터의 방향 성분을 actor가 그대로 받는 방식은 아니다.

출판본은 virtual sensor의 위치를 Fig. 2로 보여주지만, **센서 전용 link의 생성 방식, 부모 link와의 접촉력 분리, self-contact 제외, collision mask, contact-force API**를 구체적으로 설명하지 않는다. 선행연구나 다른 판본의 구현 설명을 이번 출판본의 명시 사항으로 덧붙이지 않았다.

### 4.3 Binary 표현이 보존하는 정보와 버리는 정보

| 정보 | 이 표현에서의 상태 |
| --- | --- |
| 어느 센서 부위에 접촉이 검출되었는가 | 16개 bit의 위치를 통해 유지 |
| 여러 부위가 동시에 접촉하는가 | 다중 bit 활성으로 유지 |
| 접촉력이 얼마나 큰가 | Threshold 이후 연속 크기는 제거 |
| 힘이 어느 방향으로 작용하는가 | Sim에서도 norm 이후 성분 방향을 제거 |
| 한 센서 영역 안에서 정확히 어디를 누르는가 | Actor 입력에 명시된 공간 좌표·접촉 중심 없음 |
| 무엇과 접촉했는가 | 물체 ID를 제공하는 입력으로 설명하지 않음 |
| 접촉이 검출되지 않은 이유 | Bit만으로 실제 무접촉·약한 접촉·센서 미포착을 따로 표현하지 않음 |

이 표의 정보 해석은 **원문 관측 정의에 대한 해설**이다. 논문이 모든 종류의 오검출과 정보 손실을 직접 측정했다는 뜻이 아니다. Binary의 목적은 힘의 연속값을 정확히 일치시키는 부담을 줄이는 데 있지만, 실제 접촉을 놓치지 않을 감도와 적절한 배치는 여전히 필요하다. 해당 필요성은 뒤의 threshold·coverage ablation과 연결된다.

## 5. 과업·환경·사전정보

### 5.1 Grasping Object

테이블 위의 무작위 위치에서 물체를 찾고, 다지손으로 잡아 들어 올린 다음, **놓치지 않고 지정된 목표점까지 운반**한다. 단순히 물체를 만지거나 테이블에서 띄우는 것만으로 과업 설명 전체를 충족하는 것은 아니다. [원문 §III-B, PDF p. 3]

저자는 YCB dataset에서 15개 물체를 선택했다고 설명하고 Fig. 3에 시뮬레이션 object set을 제시한다. 실물 평가는 7개 물체로 수행하며 이 중 **3개가 unseen**이다. Fig. 3은 실물 seen 4개와 unseen 3개를 구분해 보여준다. 여러 형태의 물체에 대한 조작 능력을 평가하지만, 동시에 여러 물체를 치우는 clutter 과업으로 정의하지는 않는다.

Actor의 과업 정보에는 목표 위치 3개와 물체 spawn 영역의 크기 2개가 포함된다. 현재 물체 pose는 이 과업 정보에 포함하지 않는다. [§IV-A]

### 5.2 Door Opening

위치가 바뀐 문손잡이를 접촉으로 찾고, 손잡이를 회전시킨 뒤 문을 당겨 연다. **손잡이 회전과 문 자체의 회전은 서로 다른 상태·보상 성분**이다. 무작위 배치에서 손잡이에 도달하는 탐색뿐 아니라 두 운동을 연결하는 조작을 요구한다. Actor의 과업 정보는 spawn 영역 크기 2개다. [§III-B, IV-A–B]

### 5.3 Valve Rotating

평면에서 위치가 바뀐 밸브를 찾고 시계방향으로 회전시킨다. 저자는 다른 과업의 물체보다 밸브가 작아 더 정교한 탐색이 필요하다고 설명한다. Actor의 과업 정보는 spawn 영역 크기 2개다. 밸브 회전의 성공 bonus는 **135° 초과**에서 부여한다. [§III-B, IV-B, 식 (4)]

### 5.4 사전정보의 의미와 좌표계 주의

원문에서 $\mathrm{range}_x,\mathrm{range}_y$는 물체가 무작위 생성되는 영역의 크기다. 이는 매 시점 정확한 물체 위치가 아니다. 저자는 사전정보가 초기 접근의 출발점이며, 실제 위치의 부족한 정보는 촉각으로 보완해야 한다고 설명한다. [§IV-A, V-A, V-E]

좌표 설명에는 주의가 필요하다. §IV-A는 x를 손의 horizontal, y를 vertical 방향이라고 쓰지만, §V-A는 가구·문의 높이는 일정하게 유지하며 로봇에 대한 vertical·horizontal distance를 무작위화한다고 설명한다. Fig. 2와 Table I은 배치 영역을 제시하나 **각 task의 world/base/palm frame transform이나 축 대응을 수치로 정의하지 않는다.** 따라서 $\mathrm{range}_y$를 모든 과업의 세계 좌표계 높이 변화로 단정하거나 축을 임의로 재해석하지 않는다.

## 6. RL 문제와 Actor–Critic 관측

### 6.1 원문의 문제 정의

저자는 과업을 $\mathcal M=(\mathcal S,\mathcal A,\mathcal R,\mathcal P)$의 MDP로 기술한다. Agent는 상태 $s_t$에서 $a_t=\pi(s_t)$를 선택하고 $r_t=R(s_t,a_t,s_{t+1})$를 받으며 discounted return을 최대화한다. [원문 §IV-A, PDF pp. 3–4]

$$
\max_{\pi}\;\mathbb E_{\pi}\left[
\sum_{t=0}^{T}\gamma^t r_t
\right].
$$

위 기대값 표현은 목적을 설명한 해설이다. 원문이 MDP라는 이름을 사용해도 **Actor에 물체 상태가 완전 관측된다는 뜻은 아니다.** Fig. 2와 §IV-C의 asymmetric observation이 그 차이를 명확히 보여준다. 이 출판본에는 별도의 belief filter나 물체 pose estimator를 학습하는 절이 없다.

### 6.2 실행 Actor의 입력

| 관측 항목 | 차원 | 의미·확인 범위 |
| --- | --- | --- |
| $q_t$ | 22 | UR5e 6개 + Allegro 16개 관절 위치 |
| $\dot q_t$ | 22 | 동일 관절들의 속도 |
| $o_t$ | 16 | 센서별 binary contact |
| Palm pose와 속도 | 13 | Pose 7개 + 선속도 3개 + 각속도 3개 |
| $p_{\mathrm{tips}}$ | 12 | 손끝 4개의 **palm에 대한 상대 위치**, 각각 3개 |
| $I$, Grasping Object | 5 | 목표 위치 $(\mathrm{goal}_x,\mathrm{goal}_y,\mathrm{goal}_z)$와 spawn range 2개 |
| $I$, Door/Valve | 2 | Spawn range 2개 |

[원문 §IV-A.1, PDF p. 4 / 10775]

원문의 열거를 벡터로 묶어 설명하면 다음과 같다. **순서는 설명용이며 코드 tensor ordering을 확인한 것이 아니다.**

$$
x_t=\left[q_t,\dot q_t,o_t,p_{\mathrm{palm},t},p_{\mathrm{tips},t},I\right].
$$

열거된 항목을 합산하면 파지는 **90차원**, 문·밸브는 **87차원**이다. 이는 $22+22+16+13+12+5$ 또는 마지막 항이 2인 경우의 **정리자 합산**이며, 원문이 전체 tensor dimension을 별도로 검증해 제시한 숫자는 아니다.

Palm의 7-component pose를 로봇에 추가된 7개의 제어 자유도로 해석하면 안 된다. 이 pose의 세부 parameterization과 성분 순서, palm pose·속도의 기준 좌표계, 목표 좌표의 기준 frame, 관측 정규화와 clipping 범위는 출판본에 구체적으로 명시하지 않는다.

명시된 입력 목록에는 현재 물체의 정확한 pose·속도·질량·마찰계수가 없다. 별도의 tactile image encoder나 ResNet도 없다. 또한 frame stacking, 이전 action, RNN/LSTM 등의 history 구성은 이 출판본에 기재되어 있지 않다. 이 노트에서 다른 연구의 history 설정을 추가하지 않는다.

### 6.3 학습 Critic의 privileged information

Fig. 2에서는 robot proprioception·touch·task information이 actor와 critic으로 들어가고, privileged information은 critic에 추가된다. §IV-C는 다음 항목을 열거한다. [원문 §IV-C, PDF p. 5 / 10776]

| 학습용 정보 | 용도·경계 |
| --- | --- |
| 대상 물체의 정확한 pose | Value estimation에 사용하는 시뮬레이션 정보 |
| 물체의 선속도·각속도 | Actor의 입력 목록과 구분 |
| 로봇 손과 대상 물체 사이 거리 | Value network의 추가 정보 |
| Physical parameters | 세부 항목·차원·분포는 미명시 |
| Task별 indicator 등 reward 계산 관련 정보 | Picked·rotated 같은 진행 상태를 포함하는 설명. 전체 목록 미명시 |

**실행 때 actor가 물체를 보지 못하는 것과, 학습 reward/critic이 물체 정답 상태를 쓰는 것은 양립한다.** 이 논문은 보상까지 실제 binary tactile만으로 계산하는 학습을 제안하지 않는다. Critic의 정확한 총차원과 모든 privileged tensor는 출판본만으로 확정할 수 없다.

## 7. Action과 제어 경로

Policy는 매 제어 시점에 **정규화된 22차원 벡터** $a_t\in\mathbb R^{22}$를 출력한다. 앞 6개는 팔 관절의 position command, 나머지 16개는 손가락 관절의 position target에 사용한다. 팔과 손은 모두 PD controller로 제어한다. [원문 §IV-A.2, PDF p. 4]

| 단계 | 논문에 명시된 연결 |
| --- | --- |
| Actor | 관측에서 22D normalized action 산출 |
| 팔 명령 | 6개 관절별 position command |
| 손 명령 | 16개 finger joint position target |
| Controller | 팔·손 PD controller |
| 실행 주기 | 10 Hz, simulation에서는 action을 6개 simulation step에 걸쳐 실행 |

Cartesian delta pose, 직접 joint torque, desired wrench, stiffness를 policy가 출력한다고 설명하지 않는다. 정규화 action의 범위, joint-limit scaling, absolute target인지 이전 목표에 더하는 offset인지, action smoothing, PD gain·saturation의 수치는 미명시다. 따라서 일반적인 joint PD 식을 이 논문의 실제 구현 수식처럼 추가하지 않았다.

## 8. Reward — 접근과 목적 조작을 어떻게 연결하는가

### 8.1 전체 설계 의도

보상은 물체에 도달하는 **$r_{\mathrm{reach}}$**와 목적 조작을 수행하는 **$r_{\mathrm{execute}}$**로 구성한다. Fig. 4는 손끝–물체 사이의 접근과 과업별 물체 운동을 따로 보여준다. 추가로 joint velocity의 L1 norm을 포함하는 penalty를 넣어 jerky movement를 억제한다. [원문 §IV-B, Fig. 4, PDF p. 4 / 10775]

**해설용 전체 구조:**

$$
r_t=r_{\mathrm{reach},t}+r_{\mathrm{execute},t}
-\lambda_v\|\dot q_t\|_1.
$$

원문은 전체 보상을 이 형태의 번호 식으로 쓰거나 $\lambda_v$라는 기호·수치를 주지 않는다. 위 식은 접근+실행+속도 penalty라는 서술을 설명한 것이다. 논문에 번호가 붙은 수식은 아래의 **(1)–(4)**다.

‘두 단계’는 보상 설계의 구분이다. 접근 정책과 조작 정책을 각각 학습한 뒤 별도 switch로 연결하는 구조, 혹은 접촉 bit가 1이 되면 정책을 강제로 바꾸는 state machine으로 설명하지 않는다.

### 8.2 공통 접근 보상 — 원문 식 (1)

$$
r_{\mathrm{reach}}
=\sum_{\mathrm{finger}}\alpha_{\mathrm{reach}}
\max(d_{\mathrm{closest}}-d,0).
$$

| 기호 | 원문 의미 |
| --- | --- |
| $d$ | 해당 손끝과 목표 물체 사이의 현재 거리 |
| $d_{\mathrm{closest}}$ | 에피소드에서 지금까지 달성한 가장 가까운 거리. 시작 시 $d_{\mathrm{closest}}=d$ |
| $\alpha_{\mathrm{reach}}$ | 접근 보상의 상대 가중치. 수치 미명시 |
| 합산 | 각 finger에 대한 항의 합 |

파지에서는 테이블의 대상 물체, 문에서는 door handle, 밸브에서는 **valve center**를 향한 거리다. 물체 geometry의 최근접 표면 거리인지 특정 원점의 거리인지는 모든 과업에 대해 세부 정의되어 있지 않다. [§IV-B, 식 (1)]

**식의 해설:** 현재 거리가 이전 최고 근접 기록보다 작아질 때만 양의 접근 보상을 준다. 예를 들어 이전 최소 거리가 0.20 m일 때 0.18 m까지 접근하면 $0.02\alpha_{\mathrm{reach}}$를 받는다. 이후 0.22 m로 물러났다가 다시 0.18 m에 돌아오는 것만으로는 새 보상이 생기지 않는다. 이는 식을 설명하기 위한 가상의 수치 예시이며 논문의 실험값이 아니다.

따라서 이전 step보다 가까워질 때마다 보상하는 단순 차분과 다르다. 구현에서는 보상 계산과 최소거리 기록 갱신의 순서가 중요하지만, 출판본은 코드 수준의 갱신 순서를 제공하지 않는다. Actor는 이 물체 거리를 직접 관측하지 않아도 시뮬레이터가 학습용 reward로 계산할 수 있다.

### 8.3 물체 파지·운반 보상 — 원문 식 (2)

$$
\begin{aligned}
r_{\mathrm{execute}}
={}&(1-\mathbf 1_{\mathrm{picked}})\alpha_{\mathrm{pick}}h_{\mathrm{obj}}
+r_{\mathrm{picked}}\\
&+\mathbf 1_{\mathrm{picked}}\alpha_{\mathrm{goal}}
\max(\tilde d_{\mathrm{closest}}-\tilde d,0).
\end{aligned}
$$

| 기호·조건 | 의미 |
| --- | --- |
| $h_{\mathrm{obj}}$ | 테이블을 기준으로 한 물체 높이 |
| $\mathbf 1_{\mathrm{picked}}$ | 물체가 기준 높이 **10 cm**를 넘었을 때 1이 되는 indicator |
| $\alpha_{\mathrm{pick}}$ | 들어 올리기 항의 가중치 |
| $r_{\mathrm{picked}}$ | Picked 조건에 도달하는 순간의 추가 bonus |
| $\tilde d$ | 현재 물체–운반 목표점 거리 |
| $\tilde d_{\mathrm{closest}}$ | 시도 중 달성한 가장 가까운 물체–목표점 거리 |
| $\alpha_{\mathrm{goal}}$ | 목표점 운반 진행 항의 가중치 |

들어 올리기 전에는 물체 높이에 비례하는 보상을 제공하고, picked 조건을 만족한 이후에는 목표점까지의 **최고 근접 기록 갱신량**으로 운반을 보상한다. 높이 항 자체는 식 (1)처럼 기록 경신량을 쓰는 항이 아니다. 논문의 ‘목표 방향으로만 보상’이라는 설계 의도를 모든 항이 같은 차분 형태라고 바꾸어 설명하면 안 된다.

원문은 bonus 수치, 목표 도달 거리 tolerance, 운반 성공의 유지 시간, 물체를 다시 내렸을 때 picked flag를 유지하는지, 낙하 reset 조건을 구체적으로 제시하지 않는다. ‘10 cm를 들면 파지·운반 과업 전체 성공’으로 읽지 않는다. [§III-B, IV-B, 식 (2)]

### 8.4 문손잡이 회전·문 열기 보상 — 원문 식 (3)

$$
\begin{aligned}
r_{\mathrm{execute}}
={}&(1-\mathbf 1_{\mathrm{rotated}})\alpha_{\mathrm{rot}}
\max(\phi-\phi_{\max},0)\\
&+\mathbf 1_{\mathrm{rotated}}\alpha_{\mathrm{open}}
\max(\psi-\psi_{\max},0)\\
&+r_{\mathrm{rotated}}+r_{\mathrm{opened}}.
\end{aligned}
$$

| 기호·조건 | 의미 |
| --- | --- |
| $\phi$ | 현재 문손잡이 회전각 |
| $\phi_{\max}$ | 시도 중 최대 문손잡이 회전각 |
| $\mathbf 1_{\mathrm{rotated}}$ | 손잡이 회전이 **1.047 rad, 약 60°**를 넘으면 활성 |
| $\psi$ | 문 자체의 현재 회전각 |
| $\psi_{\max}$ | 시도 중 최대 문 열림 각도 |
| $r_{\mathrm{rotated}}$ | 손잡이 회전 threshold 도달 bonus |
| $r_{\mathrm{opened}}$ | 문이 **0.873 rad, 약 50°**를 넘게 열렸을 때 bonus |
| $\alpha_{\mathrm{rot}},\alpha_{\mathrm{open}}$ | 상대 보상 가중치. 수치 미명시 |

손잡이를 충분히 돌리기 전에는 손잡이 각도의 새 기록을 보상하고, 이후에는 문 열림 각도의 새 기록을 보상한다. 문을 조금 열었다 닫은 뒤 이전 최대 각도까지 다시 여는 것만으로는 그 각도 항의 새 보상이 생기지 않는 구조다. Bonus 항은 원문 설명상 조건 도달에 연결되며, 조건과 무관한 매 step 상수 보상으로 읽지 않는다.

**출판본 오기:** 식 (3)은 $\mathbf 1_{\mathrm{rotated}}$를 사용하지만 직후 설명 문장은 $\mathbf 1_{\mathrm{picked}}$라고 표기한다. 문장 내용은 손잡이 60° 회전을 설명하므로 이 노트에서는 식의 rotated를 따라 해설하되, 원문의 불일치를 숨기지 않는다. Flag의 latch 여부와 bonus 중복 방지 구현은 미명시다.

### 8.5 밸브 회전 보상 — 원문 식 (4)

$$
r_{\mathrm{execute}}
=\alpha_{\mathrm{rot}}\max(\theta-\theta_{\max},0)
+r_{\mathrm{success}}.
$$

$\theta$는 밸브의 현재 회전각, $\theta_{\max}$는 지금까지 달성한 최대 회전각으로 해석되는 항이다. 문손잡이 회전과 유사하게 회전의 새 진행량을 보상하며, 밸브를 **135°보다 많이 회전**하면 success bonus를 받는다. 밸브의 시계방향을 양의 $\theta$로 놓는 실제 joint-axis convention은 출판본에 수치 정의되어 있지 않다. [§III-B, IV-B, 식 (4)]

### 8.6 종료와 보상을 구분해서 읽기

§IV-A는 최대 step 수 $T$ 초과, 과업 목표 달성, reset condition 만족 시 episode를 종료한다고 설명한다. 그러나 **$T$의 수치, 과업별 전체 termination/reset 논리, 실제 로봇의 종료 판정 방법**을 제공하지 않는다. 보상에 등장하는 물체 높이·각도 threshold를 모든 실행 종료 코드의 완전한 정의로 취급하지 않는다.

## 9. 학습 설정과 Sim-to-Real

### 9.1 출판본에서 확인되는 학습 설정

| 항목 | 설정 |
| --- | --- |
| 알고리즘 | Proximal Policy Optimization, PPO |
| Actor network | Hidden layer 폭 512, 256, 128의 MLP |
| Value network | Hidden layer 폭 512, 256, 128의 MLP |
| Activation | **ELU**, 원문 §IV-C 표기 기준 |
| PPO clipping | $\epsilon=0.2$ |
| Discount factor | $\gamma=0.99$ |
| KL threshold | 0.016 |
| 학습 정보 구조 | Asymmetric observation: critic에 privileged information 추가 |
| Parallel environments | 4,096 |
| Simulation time step | $dt=0.01667\ \mathrm{s}$ |
| Simulation substeps | 2 |
| Action 유지 | 6 simulation steps |
| 정책·제어 주파수 | 10 Hz |
| 비교 결과의 training seed | 3개. Fig. 5, Table II–III의 설명 |

[원문 §IV-C, PDF p. 5; Fig. 5, Table II–III, PDF p. 6]

Action 유지 시간은 $6\times0.01667\simeq0.10002$ s이며 10 Hz와 대응한다. Substep 2개는 한 simulation step 내부의 물리 계산 설정이다. 정책을 120 Hz로 실행했다는 뜻이 아니다. 실물 센서의 125 Hz 취득도 정책의 10 Hz 실행과 따로 읽어야 한다.

Actor가 binary를 전용 encoder에 먼저 넣고 별도 tactile latent를 만드는 구조는 제시하지 않는다. Fig. 2와 §IV의 설명은 **접촉 bits와 로봇 상태·과업 정보를 MLP 정책에 입력**하는 구조다. 이 출판본만으로 actor output distribution, log-standard-deviation 설정, normalization layer 등 구현 세부를 확정할 수는 없다.

### 9.2 전이에서 실제로 확인한 것

저자는 시뮬레이션에서 학습한 정책을 **실물에서 fine-tuning 없이** 적용한다. Binary contact를 이용해 신호 표현을 단순화하고, 팔·손 플랫폼 및 10 Hz control 설정을 대응시키며, simulation과 real에 같은 물체 위치 무작위화 영역을 적용한다. [Fig. 1, §III-A, V-A, V-E]

반면 질량·마찰·센서 noise·지연·PD gain의 구체적인 domain-randomization 분포, system identification 방법, contact dropout, tactile history, action EMA는 출판본에 명시하지 않는다. **물체 초기 위치 randomization이 있다는 사실을 모든 물리·센서 파라미터를 randomize했다는 설명으로 확대하지 않는다.**

실물 전이 성공은 Table III에서 확인할 수 있다. 하지만 binary 이외의 구성요소를 고정한 continuous tactile 대조군이 없으므로, 관측된 전이 성과 전부를 이진화 하나의 효과로 분해할 수는 없다. 이는 실험 설계의 해석 범위이며 저자 명시 Limitation과는 별도로 구분한다.

## 10. 실험 설계·초기 분포·비교군

### 10.1 초기 배치 — 원문 Table I

아래 위치 값은 영역의 중심에 더하는 **균등분포 offset**이다. Table I의 축 이름을 유지했다. [원문 Table I, §V-A, PDF p. 5 / 10776]

| 과업 | Range x, m | Range y, m | Z-Pose, rad |
| --- | --- | --- | --- |
| Grasping Object | $+\mathcal U(-0.30,0.30)$ | $+\mathcal U(-0.15,0.15)$ | $[-\pi,\pi]$ |
| Door Opening | $+\mathcal U(-0.55,0.55)$ | $+\mathcal U(-0.20,0.20)$ | — |
| Valve Rotating | $+\mathcal U(-0.30,0.30)$ | $+\mathcal U(-0.30,0.30)$ | $[-\pi,\pi]$ |

예를 들어 $\pm0.30$ m는 전체 폭 0.30 m가 아니라 중심에서 양쪽으로 0.30 m인 범위다. 전체 폭 0.60 m는 이 구간에서 계산한 값이다. 이 표의 offset 반폭과 actor에 입력되는 ‘range length’의 정확한 숫자 대응은 코드 없이 확정하지 않는다. Z-Pose 열은 회전 범위를 제시하지만, 위치와 같은 확률분포를 회전에도 사용했다고 명시하는 식은 없다.

저자는 고정된 로봇 팔의 작동 범위와 가구·문의 일정한 높이를 고려해 이 분포를 정했으며, simulation과 real에 동일한 randomness를 적용했다고 설명한다. 표에 없는 중심 위치·초기 관절 자세·매 reset의 손 자세 분포는 이 노트에서 임의로 채우지 않는다.

### 10.2 비교군의 차이

| 조건 | 바뀐 내용 | 비교 목적·시점 |
| --- | --- | --- |
| **Ours** | 센서 16개, sim threshold 0.01 N, asymmetric PPO | 기본 방법 |
| **WO-Sensor** | Tactile 없이 PPO를 처음부터 학습 | Proprioception 중심 정보만으로 조작을 배울 수 있는지 |
| **LQ-Sensor** | 접촉 threshold를 0.3 N으로 높여 학습 | 접촉 검출 감도 저하의 영향 |
| **WO-PInfo** | 학습에서 privileged information을 제외 | Asymmetric value learning의 효과 |
| **DA-Sensor** | Ours와 같은 방식으로 학습하고 **평가에서 tactile을 비활성화** | 이미 학습한 정책이 실제로 tactile을 사용하는지 |
| **Fingertips** | 손끝 센서 4개만 활성화, sim threshold 0.01 N | 같은 simulation에서 센서 배치를 바꾸어 학습 |
| **Palm** | 손바닥 센서 4개만 활성화, sim threshold 0.01 N | Fingertips와 센서 수를 맞춘 위치 비교 |
| **F/Tsensor** | 손목의 3축 force·3축 torque를 학습에 사용 | 같은 simulation의 다른 센서 유형 비교 |

[원문 §V-A–D, PDF pp. 5–6]

**WO-Sensor와 DA-Sensor는 다른 실험이다.** 앞의 정책은 촉각 없이 학습에 적응할 기회가 있고, 뒤의 정책은 학습 때 사용하던 정보를 평가 때 잃는다. 두 조건의 결과를 같은 ‘무센서 baseline’으로 합치지 않는다.

WO-PInfo는 actor에 원래 들어가던 object GT를 제거한 실험이 아니다. Ours도 그 정보는 critic에만 사용한다. 또한 WO-PInfo가 물체 GT 없이 reward까지 계산하도록 바꾸었다는 설명은 없다.

### 10.3 Seed·반복 수·오차 표시

| 항목 | 원문 보고 | 해석의 경계 |
| --- | --- | --- |
| 학습 곡선 | 3 seeds 평균, 음영은 standard deviation | Fig. 5 caption에 명시 |
| Table II·III | 3 seeds로 학습한 3 policies의 평균 | 두 표 모두 해당 각주를 가짐 |
| 실물 파지 | 물체마다 30 trials | §V 도입부 |
| 실물 문·밸브 | 각 55 experiments | §V 도입부 |
| 시뮬레이션 평가 episode 수 | 미명시 | 4,096 병렬 환경 수를 평가 분모로 대체하지 않음 |
| Table II·III의 ± | 원문 값을 그대로 유지 | 각주는 평균 조건만 설명. 표의 ±가 무엇인지 별도 정의하지 않아 95% CI·표준오차로 이름 붙이지 않음 |

실물 30/55회가 policy seed별 횟수인지, 여러 정책을 합친 횟수인지는 본문과 각주를 연결해 명확히 확인할 수 없다. 따라서 **30×3, 55×3을 실제 총 시행 수라고 확정하지 않으며**, 평균 성공률로 성공 횟수를 역산하지 않는다. 원시 trial 로그나 seed별 결과도 제공되지 않는다.

## 11. 시뮬레이션 결과 — 원문 Table II와 Fig. 5

### 11.1 성공률 전체 수치

아래 값은 **0–1 비율**이며 원문의 평균±표시를 유지했다. [원문 Table II, PDF p. 6 / 10777]

| Method | Grasping Object | Door Opening | Valve Rotation |
| --- | --- | --- | --- |
| LQ-Sensor | 0.37 ± 0.14 | 0.37 ± 0.17 | 0.58 ± 0.13 |
| WO-Sensor | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.02 ± 0.01 |
| WO-PInfo | 0.15 ± 0.10 | 0.15 ± 0.09 | 0.31 ± 0.12 |
| Fingertips | 0.49 ± 0.10 | 0.48 ± 0.22 | 0.69 ± 0.07 |
| Palm | 0.36 ± 0.09 | 0.38 ± 0.23 | 0.53 ± 0.14 |
| F/Tsensor | 0.26 ± 0.11 | 0.29 ± 0.15 | 0.50 ± 0.08 |
| **Ours** | **0.72 ± 0.07** | **0.69 ± 0.12** | **0.82 ± 0.06** |

### 11.2 Reward 전체 수치

가로폭을 줄이기 위해 원문 Table II의 Reward 열을 따로 옮겼다. 성공률 표와 같은 결과이며, 과업마다 reward 구조와 scale이 다르므로 **과업 간 절댓값을 조작 능력의 순위로 비교하지 않는다.**

| Method | Grasping Object reward | Door Opening reward | Valve Rotation reward |
| --- | --- | --- | --- |
| LQ-Sensor | 587.75 ± 172.96 | 644.11 ± 179.13 | 1400.99 ± 284.58 |
| WO-Sensor | 232.80 ± 11.28 | 142.57 ± 10.03 | 389.01 ± 59.45 |
| WO-PInfo | 320.37 ± 134.71 | 411.89 ± 123.49 | 771.19 ± 168.35 |
| Fingertips | 693.12 ± 89.73 | 792.18 ± 258.47 | 1677.22 ± 169.42 |
| Palm | 520.74 ± 82.42 | 599.27 ± 228.23 | 1273.58 ± 320.24 |
| F/Tsensor | 440.17 ± 142.98 | 516.06 ± 164.20 | 1243.43 ± 162.25 |
| **Ours** | **893.28 ± 65.94** | **953.99 ± 66.65** | **2001.71 ± 66.57** |

### 11.3 저자의 해석과 수치가 보여주는 범위

**촉각 유무:** WO-Sensor는 파지·문에서 성공률 0%, 밸브에서 2%다. 저자는 이 정책이 초기에는 테이블 위치 같은 알려진 정보를 이용해 접근을 배우지만, 이후 대상과의 상호작용을 통해 성공하는 행동을 배우기 어렵다고 해석한다. Reward가 0이 아니므로 ‘아무 행동도 학습하지 못했다’는 설명은 부정확하다. [§V-B(i)]

**Threshold와 감도:** Ours의 0.01 N 대비 LQ의 0.3 N은 더 큰 접촉력이 있어야 검출되게 만든다. Ours의 성공률은 LQ보다 파지 **35 percentage points**, 문 **32 points**, 밸브 **24 points** 높다. 이 차이는 Table II 평균에서 계산한 값이다. 저자는 감도 저하 조건에서 물체가 떨어지거나 튕겨 나가는 현상을 관찰했다고 보고한다. 다만 이는 두 threshold 설정의 과업 비교이지 물리 센서의 force resolution을 측정한 결과는 아니다. [§V-B(ii)]

**Privileged critic:** WO-PInfo는 파지·문 15%, 밸브 31%로 Ours보다 낮다. 저자는 actor가 직접 볼 수 없는 privileged information도 critic을 통해 학습 효율과 안정성에 기여한다고 해석한다. [§V-B(iii)]

**센서 배치:** 같은 4개 센서를 사용하는 Fingertips가 Palm보다 세 과업 모두 높다. 반면 16개를 사용하는 Ours는 4개 조건보다 높다. **Fingertips–Palm은 같은 수에서 배치가 다른 비교**, Ours–4개 조건은 **수와 커버리지가 함께 바뀌는 비교**다. 이를 순수 공간 해상도 하나의 효과로 해석하지 않는다. [§V-C]

저자는 밸브에서 Fingertips가 Ours와 비슷한 성공률을 보인다고 설명하며, 주로 손끝으로 밸브를 조작해 다른 부위 센서의 비활성화 영향이 작다고 해석한다. 실제 값은 **0.69와 0.82**다. 이 표현을 통계적 동등성이 검증되었다는 주장으로 바꾸지 않는다.

### 11.4 학습 곡선의 읽는 법

Fig. 5(a)는 Ours·LQ-Sensor·WO-Sensor·WO-PInfo, Fig. 5(b)는 Ours·Fingertips·Palm·F/Tsensor를 비교한다. 각 그룹에서 열은 파지·문·밸브이며 위 행은 success rate, 아래 행은 episodic return이다. **음영은 3 seeds의 표준편차**다. [Fig. 5 caption]

그림의 x축 이름은 `Training steps`이고 표시된 끝은 파지 **20k**, 문 **30k**, 밸브 **15k**다. 출판본은 이 값의 PPO iteration·전체 environment transition 수와의 정확한 대응을 설명하지 않는다. 4,096을 곱해 총 sample 수로 바꾸거나 10 Hz로 나누어 학습 시간을 계산하지 않았다. Wall-clock training time도 미명시다.

## 12. 손목 F/T 비교가 구체적으로 의미하는 것

### 12.1 F/T를 학습에 사용한 방식

§V-D는 wrist-mounted F/T sensor에서 **3축 힘과 3축 토크**를 측정하여 학습에 사용한 `F/Tsensor` 그룹을 구성했다고 설명한다. 이 그룹은 다른 센서 조건과 같은 시뮬레이션 환경에서 학습·비교한다. [원문 §V-D, PDF p. 6 / 10777]

| 확인할 질문 | 출판본에서 확인되는 답 |
| --- | --- |
| 3D force만인가, torque도 포함하는가? | 3축 force와 3축 torque 모두 언급 |
| 센서 위치는 어디인가? | Robot wrist |
| 기본 방법의 16bit에 F/T를 추가한 결합인가? | 다른 sensor type을 사용하는 별도 대조군으로 제시. 병용 성능을 보고하지 않음 |
| RL과 연결되는가? | 측정값을 이용해 policy를 학습하는 비교군으로 설명 |
| F/T observation 전체 벡터가 제시되는가? | 별도의 전체 목록·총차원·tensor ordering은 미명시 |
| 전처리는 무엇인가? | Bias·gravity compensation, 좌표 변환, LPF, force/torque 정규화, clipping, history가 미명시 |
| 목표 wrench를 action으로 내는가? | 그렇게 설명하지 않음. 주방법 action은 joint-position command |
| F/T 전용 reward·force controller가 있는가? | 별도 변경식이나 세부 controller를 제시하지 않음 |
| 실물 F/T 성능인가? | **아니다. Table II의 simulation 결과이며 Table III에는 F/T 그룹이 없다** |

따라서 이 논문은 F/T를 학습 입력으로 이용하는 센서 대조의 근거는 제공하지만, **F/T 신호를 보정·정규화하고 시간 이력까지 처리하는 재현 가능한 전체 파이프라인**을 제공하지는 않는다. 원문에 없는 force-control 구조를 덧붙여 ‘DexTouch의 F/T 기반 RL 구현’으로 설명하지 않는다.

### 12.2 결과의 해석 범위

F/Tsensor의 성공률은 파지 **26%**, 문 **29%**, 밸브 **50%**이며 Ours의 **72%, 69%, 82%**보다 낮다. 저자는 이를 근거로 시각 없는 탐색·조작에서 손에 부착된 touch sensor가 더 중요하다고 해석한다. [§V-D]

이 결과는 **해당 세 과업과 해당 simulation baseline**에 대한 비교다. 손목 F/T가 모든 blind manipulation에서 열등하거나 불필요하다는 일반 결론, 혹은 실제 F/T 하드웨어보다 실제 FSR이 항상 우수하다는 실측 결론으로 확장할 수 없다. 센서 정보의 차원·공간 분포·전처리를 통제하며 원인을 분리하는 추가 실험도 이 출판본에는 없다. 이 문단은 비교 설계에 대한 정리자의 해석이며 저자의 Limitation 진술과 구분한다.

## 13. 실물 평가 — 원문 Table III와 Fig. 6

### 13.1 Fine-tuning 없는 이전 결과

아래 값은 Table III의 성공률이며 0–1 비율이다. 표 각주는 3 seeds로 학습한 3 policies의 평균이라고 설명한다. [원문 §V-E, Table III, PDF p. 6 / 10777]

| Method | Grasping Object | Door Opening | Valve Rotation |
| --- | --- | --- | --- |
| LQ-Sensor | 0.27 ± 0.12 | 0.35 ± 0.13 | 0.32 ± 0.18 |
| DA-Sensor | 0.09 ± 0.04 | 0.11 ± 0.03 | 0.12 ± 0.05 |
| **Ours** | **Seen: 0.64 ± 0.17 / Unseen: 0.47 ± 0.24** | **0.60 ± 0.17** | **0.67 ± 0.17** |

파지 Ours는 seen과 unseen을 나누지만 **LQ-Sensor와 DA-Sensor의 파지 열은 단일 값**이다. 이 두 값이 seen에만 해당하는지, unseen을 포함한 어떤 가중 평균인지는 표에서 분명히 복원할 수 없다. 따라서 Ours의 seen 64%에서 LQ 27%를 빼 동일 물체 집합의 개선량이라고 단정하지 않는다.

이 실물 표에는 **WO-Sensor, WO-PInfo, Fingertips, Palm, F/Tsensor가 없다.** Simulation의 전체 ablation이 실물에서도 모두 반복되었다는 설명은 부정확하다. DA-Sensor를 WO-Sensor로 대체해 기록하지 않는다.

### 13.2 초기 접근과 접촉 이후 행동

Fig. 6은 각 과업에서 두 개의 서로 다른 대상 배치 `Position 1/2`와 **Initial → Reaching → Touching → Manipulating**의 장면을 보여준다. 빨간 화살표는 target 위치 차이를 나타낸다. 이 탑뷰 영상은 실험 결과의 시각화이며 actor의 관측 이미지로 제시된 것이 아니다. [Fig. 6, PDF p. 7 / 10778]

저자의 정성 관찰은 다음과 같다. [§V-E, PDF pp. 6–8]

| 관찰 | 저자의 설명 |
| --- | --- |
| 초기 reaching 경로가 유사함 | 접촉 정보가 부족한 초기에는 prior를 이용하여 접근 |
| Ours의 조작 시도 시점이 달라짐 | 실제 접촉이 생긴 시점에 따라 후속 조작을 시도 |
| LQ에서 과도한 조작·낙하 | 낮은 감도로 인해 검출에 더 큰 접촉력이 필요 |
| DA의 초기 동작은 Ours와 유사하지만 후속 조작이 어려움 | 촉각 없이 물체를 찾기 어려워짐 |

접촉에 따라 행동이 달라졌다는 관찰은 촉각이 실행 정책에 기여한다는 증거다. 그러나 그림은 contact-detection latency, 접촉력 peak, 정확한 반응시간을 측정한 정량 실험은 아니다. 특정 bit와 특정 grasp primitive 사이의 수작업 규칙이 있다는 뜻도 아니다.

### 13.3 미지 물체와 물성의 영향

실물 Ours의 파지는 seen 평균 **64%**, unseen 평균 **47%**다. Seen과 unseen은 서로 다른 물체 집합이므로 이 차이를 단일 물성 또는 형상 효과의 통제 실험으로 해석하지 않는다.

저자는 unseen 3개 중 **tumbler의 성공률이 가장 낮았고**, 그 이유를 무거운 무게와 미끄러운 표면으로 설명한다. 이를 통해 학습 중 만나지 못한 물성도 성공률에 영향을 줄 수 있다고 해석한다. **Tumbler 개별 성공률과 질량·마찰 수치는 제시하지 않았다.** 질량과 표면 마찰을 각각 바꾼 요인 실험도 보고하지 않는다. [§V-E 마지막 부분, PDF p. 8 / 10779]

## 14. Limitation — 저자들이 밝힌 한계와 적용 조건

출판본에 독립적인 `Limitations` 절은 없다. 아래는 본문의 **저자 관찰·가정·실패 설명**을 모은 것이다. 정리자가 추가한 재현 공백과 비판은 §16에 따로 기록한다.

### 14.1 낮은 접촉 감도에서의 실패

저자는 threshold가 높아지면 접촉을 알아차리기 위해 더 큰 힘이 필요하고, 이 과정에서 물체가 떨어지거나 튕겨 나간다고 보고한다. 실물 LQ-Sensor에서도 과도한 조작과 낙하를 관찰했다. **이는 감도가 낮은 비교 조건의 실패 설명**이며 Ours가 동일 빈도로 실패했다는 보고로 바꾸지 않는다. [원문 §V-B(ii), PDF p. 5 / 10776; §V-E, PDF p. 7 / 10778]

### 14.2 사전정보와 실험 공간의 조건

대상의 정확한 위치를 모르더라도 **어느 범위에 있을지에 대한 prior를 가정**한다. 고정된 팔의 workspace를 고려하고 높이를 유지한 배치 무작위화를 사용했다. 저자는 prior만으로는 물체의 정확한 위치를 결정할 수 없으므로 촉각으로 정보 손실을 보완해야 한다고 설명한다. 이는 연구가 명시한 조건이며, 임의의 미지 환경에서 사전정보 없이 무제약 탐색을 검증한 결과는 아니다. [§V-A, Table I, PDF p. 5 / 10776; §V-E, PDF p. 7 / 10778]

### 14.3 학습에서 경험하지 못한 물성

무겁고 미끄러운 unseen tumbler에서의 낮은 성공률은 저자가 직접 지적한 일반화 문제다. 학습에서 경험하는 물체 특성도 prior의 일부가 될 수 있으며, 학습 밖 특성이 과업 성공을 제한할 수 있다고 설명한다. 물성별 원인을 완전히 분리해 검증한 결과로 표현하지 않는다. [§V-E, PDF p. 8 / 10779]

### 14.4 부위별 촉각의 역할이 과업에 따라 다름

저자는 Fingertips가 Palm보다 높은 결과와 밸브에서 손끝의 주된 역할을 설명한다. 이는 어떤 부위의 접촉을 감지하는지가 중요하다는 실험 관찰이다. 손바닥 센서가 모든 과업에서 불필요하다거나 손끝 4개가 전체 16개와 동등하다는 한계 진술은 아니다. [§V-C, PDF p. 6 / 10777]

## 15. Future Work — 저자들이 제시한 향후 연구

원문 §VI Conclusion은 두 방향을 명시한다. [원문 PDF p. 8 / 10779]

| 저자 제안 | 정확한 의미와 현재 결과와의 구분 |
| --- | --- |
| **3축 force sensor처럼 다양한 tactile 정보를 제공하는 센서 적용** | 현재 16bit 접촉보다 다양한 촉각 정보의 활용 방향. 이 논문에서 해당 시스템을 이미 구현·검증한 것은 아님 |
| **시스템을 확장해 generalizability 연구** | 현재 조건 밖에서의 일반화를 후속 연구로 제시. 구체적인 task 집합·학습 알고리즘·평가 프로토콜은 미명시 |

‘3축 force sensor’라는 향후 방향을 이미 수행한 손목 6축 F/T 대조군의 성공으로 바꾸지 않는다. RNN·Transformer 도입, 특정 새 태스크 수행, 센서 개수·threshold의 확정 변경은 저자가 제시한 구체 계획이 아니다.

## 16. 미명시 정보·표기 주의·주장의 경계

### 16.1 재현을 위해 추가 자료가 필요한 부분

| 범주 | 첨부 출판본만으로 확정할 수 없는 사항 |
| --- | --- |
| 실물 센싱 | FSR 모델·측정 사양, 회로·ADC, LPF 설정, 전압 threshold, 보정법, 이중 threshold·debounce 여부 |
| 시간 대응 | 125 Hz sample의 10 Hz 입력 집계법, timestamp·지연·누락 처리 |
| Sim contact | 센서 link 구현, 부모 link와의 분리, collision/self-contact 처리, force API |
| Actor | 전체 tensor 순서, palm pose 표현·frame, 관측 scaling·clipping, range length의 폭/반폭 대응 |
| Critic | Physical parameters의 구체 목록, privileged tensor 총차원 |
| Action·controller | 정규화 범위, target scaling, absolute/delta 관계, PD gains·limit·saturation·보간 |
| PPO | Learning rate, batch/minibatch, rollout horizon, epochs, entropy/value coefficient, GAE 설정, optimizer 등 |
| Training | 센서·물성 domain-randomization 분포, system identification, training steps의 집계 단위, wall-clock time |
| Reward | 모든 상대 가중치·bonus의 수치, flag latch·bonus 중복 지급·best-record 갱신 순서 |
| Termination | 최대 episode 길이, 최종 파지 목표 tolerance, 낙하 reset, 실제 로봇 종료 판정 |
| F/T baseline | Sensor model, bias/gravity 보정·좌표계·filter·정규화·history, 전체 observation 구성 |
| Evaluation | Seed별 실물 시행 수와 전체 분모의 대응, raw trial 결과, 표 ±의 별도 정의, 물체별 성공률 |

이 목록은 해당 처리가 없다는 증명이 아니라 **출판본을 읽은 것만으로 구현을 확정할 수 없다는 뜻**이다. PPO·IsaacGym의 보편적 기본값이나 선행연구 설정으로 빈칸을 채우지 않았다.

### 16.2 출판본의 표기 불일치

| 위치 | 원문 상태 | 이 노트의 처리 |
| --- | --- | --- |
| §IV-B 식 (3) 직후, PDF p. 4 | 식은 rotated indicator, 설명문은 picked indicator | 문맥상 손잡이 회전 flag로 해설하고 오기를 명시 |
| §IV-A.1, PDF p. 4 | Palm 변수 철자가 `plam` | 해설에서는 `palm`으로 표기 정리. 새로운 관측을 추가한 것이 아님 |
| §IV-C와 References [32], PDF pp. 5, 8 | Activation 본문은 **ELU**, [32]는 Nair & Hinton의 ReLU 논문 | 본문을 따라 ELU로 기록. 실제 코드 확인 없이 ReLU로 교정하지 않음 |
| §IV-A와 V-A, PDF pp. 4–5 | Horizontal/vertical 축 설명과 높이 고정 조건의 frame 대응이 불명확 | 원문 축 이름·범위 유지, 세계 좌표계로 임의 변환하지 않음 |

### 16.3 자주 혼동하기 쉬운 주장

| 잘못 읽기 쉬운 표현 | 이 출판본에서 확인되는 내용 |
| --- | --- |
| ‘접촉 여부 하나만으로 조작’ | 부위별 16bit와 많은 proprioception·task 정보 사용 |
| ‘Binary라 신경망 encoding이 없다’ | 별도 tactile image encoder는 없지만 MLP 정책으로 상태를 처리 |
| ‘0.01 N은 FSR의 감도 사양’ | Simulation threshold이며 real 전압 threshold 수치는 없음 |
| ‘125 Hz 정책’ | 센서 취득 125 Hz, 정책·제어 10 Hz |
| ‘Actor가 정확한 물체 pose로 학습·실행’ | Exact pose는 privileged critic·reward용, actor 입력 목록에 없음 |
| ‘90/87차원은 원문에 총차원으로 명시’ | 원문 항목에서 합산한 값 |
| ‘팔 action 6개는 Cartesian command’ | 팔 6개 관절의 position command |
| ‘두 단계 보상은 두 정책을 전환하는 구조’ | 한 과업 정책 안에서 reach·execute 보상을 설계 |
| ‘모든 보상은 최고 기록 개선량’ | 파지의 lift 항은 현재 높이 자체 |
| ‘10 cm lift가 전체 과업 성공’ | 이후 물체를 목표점까지 운반해야 함 |
| ‘문을 60° 열면 성공’ | 60°는 손잡이 회전, 문 열림 bonus 기준은 50° |
| ‘Binary가 continuous보다 우수함을 검증’ | Continuous tactile 대조군 없음 |
| ‘손목 F/T가 실제 실험에서 실패’ | F/T 결과는 simulation-only |
| ‘실물 무촉각 9%는 무촉각으로 학습한 정책’ | 학습 후 평가에서 끈 DA-Sensor의 파지 결과 |
| ‘모든 실물 파지 baseline에 seen/unseen 결과가 있음’ | Table III에서 Ours만 분리 |
| ‘세 seed와 시행 수를 곱하면 전체 실물 trials’ | Seed별/전체 반복 수의 대응이 미명시 |
| ‘미지 물체 모두에 강한 일반화’ | Unseen 평균 47%, 물성에 따른 실패를 저자가 논의 |

## 17. 원문 위치 안내와 검증 범위

| 다시 확인할 내용 | 원문 위치 |
| --- | --- |
| 문제·동기·binary 선택의 출처 | Abstract, §I, PDF p. 1 / 10772 |
| Related Work | §II, PDF pp. 1–2 / 10772–10773 |
| UR5e·Allegro·FSR·125 Hz·LPF | §III-A, PDF p. 2 / 10773 |
| Sim force norm·threshold·센서 배치 | §III-A, Fig. 2, PDF p. 3 / 10774 |
| 과업과 seen/unseen object set | §III-B, Fig. 3, PDF p. 3 / 10774 |
| Actor observation·action | §IV-A, PDF pp. 3–4 / 10774–10775 |
| Reach·grasp·door·valve reward | §IV-B, 식 (1)–(4), Fig. 4, PDF p. 4 / 10775 |
| MLP·PPO·privileged critic·simulation 시간 설정 | §IV-C, PDF p. 5 / 10776 |
| 초기 분포·실물 시행 수·기본 ablation | Table I, §V 도입부·V-A, PDF p. 5 / 10776 |
| 무촉각·감도·privileged 정보의 저자 해석 | §V-B, PDF p. 5 / 10776 |
| 학습 곡선·simulation 결과 | Fig. 5, Table II, PDF p. 6 / 10777 |
| 센서 위치·F/T 비교 | §V-C–D, PDF p. 6 / 10777 |
| 실물 성공률·대표 접촉 행동 | Table III, Fig. 6, §V-E, PDF pp. 6–7 / 10777–10778 |
| Unseen tumbler 실패 | §V-E 끝, PDF p. 8 / 10779 |
| 저자 결론·Future Work | §VI, PDF p. 8 / 10779 |
| 인용 자료 | References [1]–[33], PDF p. 8 / 10779 |

첨부 출판본의 본문 8쪽을 확인하고, 핵심 그림·Table I–III·식 (1)–(4)를 PDF의 실제 표시와 대조했다. 표의 평균·±값과 보상 변수·조건을 독립 검토했다. 해설용 수식은 원문 번호식과 구분하고 저장소의 블록·인라인 수식 규칙을 적용했다.

문서의 수식 구문·표 구조·내부 링크 검사와 GitHub 원격 소스 확인은 실제 GitHub 웹페이지 표시 확인과 다르다. 후자의 완료, 코드 실행, 정책 재학습, 실물 재현 또는 보충 영상 전체 확인을 주장하지 않는다.
