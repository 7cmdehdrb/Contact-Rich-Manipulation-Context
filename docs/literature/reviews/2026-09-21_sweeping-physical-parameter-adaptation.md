# Sweeping의 숨은 물리 조건에 대한 명시적 추정과 이력 기반 대응 — 신규 문헌 조사

[문헌 색인](../README.md) · [조사 그룹](README.md) · [발표 설계 2.4절](../../presentation/02_Tactile_Representation_and_Policy_Design.md#24-sweeping에서-중요하게-다뤄야-할-것은-무엇인가)

조사일: 2026-09-21  
대상: `docs/presentation/02_Tactile_Representation_and_Policy_Design.md`의 2.4절  
상태: **문헌 근거 조사 및 반영 제안. 프로젝트의 구현·성능 검증 결과가 아님.**

## 1. 조사 범위와 선정 결과

프로젝트의 대상은 접근 완료 후 시작하여, 초기 시각 정보 이후 **실행 중 물체 시각 추적을 갱신하지 않고 Binary 촉각·손목 Wrench·고유감각으로 수행하는 Sweeping 하위 정책**이다. 상위 계획·접근 정책과 물성 자체의 정확한 복원은 현재 연구 목표와 구분했다.

[저장소](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context)의 `AGENTS.md`, 문서 형식 규칙, 인계 요약, 결정·미정 목록, 다음 작업, 대상 발표 문서, `docs/literature/papers/README.md` 및 실제 폴더 목록을 확인했다. 기존 상세 리뷰 **27편을 제외**했고, 제목 선별 목록에만 있는 논문은 배제하지 않았다.

연도는 보수적으로 **2022년 이후 정식 출판**을 적용했다. SCIE 저널인 T-RO·IJRR와, 사용자가 허용한 주요 정규 학회 논문인 ICRA·IROS·CoRL을 구분하여 선정했다. 학회 논문 자체를 SCIE 등재 논문이라고 부르지는 않는다. arXiv 등록연도와 정식 출판연도가 다르면 아래에 분리했다.

**주요 결과는 명시적 추정 3편, 정책 내부 이력·DR 3편, 별도 잠재변수 적응 모듈 1편이다.** 방법·관측·실험·한계 관련 원문을 검토한 비교 조사이며, 저장소의 개별 논문 정독 노트나 재현 실험을 새로 완료했다는 의미는 아니다.

| ID | 논문 | 정식 게재 | 이 조사에서의 위치 |
| --- | --- | --- | --- |
| A1 | Dutta, Burdet & Kaboli, **Predictive Visuo-Tactile Interactive Perception Framework for Object Properties Inference** | T-RO 41:1386–1403, **2025** | 물성 추정 → 목표 지향 pushing의 직접 사례 |
| A2 | Haninger et al., **Differentiable Compliant Contact Primitives for Estimation and Model Predictive Control** | ICRA **2024**, 17146–17152 | 접촉·지지 모델 추정 → MPC |
| A3 | Xue et al., **Robust Contact-rich Manipulation through Implicit Motor Adaptation** | IJRR, **2025 온라인 출판**, DOI 아래 참조 | 물성 확률 추정 → 조건부 정책 검색 |
| B1 | Del Aguila Ferrandis, Moura & Vijayakumar, **Nonprehensile Planar Manipulation through Reinforcement Learning with Multimodal Categorical Exploration** | IROS **2023**, 5606–5613 | 물성 추정기 없는 pushing: 이력 + DR |
| B2 | Sievers, Pitz & Bäuml, **Learning Purely Tactile In-Hand Manipulation with a Torque-Controlled Hand** | ICRA **2022** | 시각 없는 조작: 관측 stack + DR |
| B3 | Handa et al., **DeXtreme: Transfer of Agile In-Hand Manipulation from Simulation to Reality** | ICRA **2023**, 5977–5984 | Recurrent policy + 물리 DR/ADR |
| C1 | Qi et al., **In-Hand Object Rotation via Rapid Motor Adaptation** | CoRL **2022**, PMLR 205:1722–1732 **2023 출판** | 이력 → 별도 latent 추정 → 정책인 경계 사례 |

출판 근거: [A1 IEEE/DOI](https://doi.org/10.1109/TRO.2025.3531816), [A2 소속기관 기록](https://vbn.aau.dk/en/publications/differentiable-compliant-contact-primitives-for-estimation-and-mo/), [A3 출판사 기록](https://journals.sagepub.com/doi/abs/10.1177/02783649251344638), [B1 소속기관 기록](https://www.research.ed.ac.uk/en/publications/nonprehensile-planar-manipulation-through-reinforcement-learning-/), [B2 IEEE](https://ieeexplore.ieee.org/document/9812093/), [B3 IEEE](https://ieeexplore.ieee.org/document/10160216), [C1 PMLR](https://proceedings.mlr.press/v205/qi23a.html).

## 2. 분류 기준: 이력 사용과 물성 추정은 서로 배타적이지 않다

아래 식은 논문별 원식을 복제한 것이 아니라, **비교를 위한 본 보고서의 공통 표기**다. $H_t$는 관측·행동 이력, $\theta$는 물성·접촉 조건, $z_t$는 잠재표현이다.

| 구조 | 실행 중 정보 흐름 | 판단 기준 |
| --- | --- | --- |
| **A. 명시적 파라미터·모델 추정** | $H_t\rightarrow\hat\theta_t\rightarrow\pi$ 또는 MPC | 질량·마찰·강성·접촉 위치 등의 의미가 정해진 추정값이나 그 분포를 제어기가 사용 |
| **B. 정책 내부 이력 처리** | $(o_t,H_t)\rightarrow\pi\rightarrow a_t$ | Stack·RNN 등이 정책 안에서 관측 부족을 보완. 별도의 실행 중 물성 회귀 출력은 없음 |
| **C. 별도 잠재변수 적응** | $H_t\rightarrow\hat z_t\rightarrow\pi$ | 물성값 자체를 출력하지 않지만 별도 적응 모듈·학습 단계가 존재 |
| **DR: 학습 조건의 구성** | $\theta\sim p_{\mathrm{train}}(\theta)$ | 위 구조들과 함께 적용할 수 있는 학습 방법. 실행 중 적응 기구 자체는 아님 |

따라서 두 가지를 별도로 확인해야 한다. **무엇을 복원하는가**와 **복원·기억 처리가 정책 안에 있는가, 별도 모듈에 있는가**다. 이력을 입력받는 명시적 추정기도 있고, 물성을 출력하지 않는 외부 적응기도 있다. 또한 DR 성공만으로 정책이 물성 차이를 내부적으로 식별했다고 결론낼 수 없다.

## 3. A — 외부 추정값을 계획·정책에 제공하는 연구

<a id="a1"></a>

### A1. Dutta et al. — 가장 직접적인 마찰·물성 추정 → Pushing 사례

**연결:** RGB-D·손끝 접촉력·push/pull 행동 → GNN을 포함한 dual differentiable filter → 물체 Pose/Twist와 질량·CoM·마찰 관련 파라미터 → 학습 동역학을 사용하는 **iCEM MPC**. 로봇–물체 마찰은 센서 특성으로 대략 알려져 있다고 가정하므로, 모든 접촉면의 마찰을 동시에 추정한다고 설명하면 안 된다.

**검증:** 실제 목표 지향 pushing에서 8개 물체를 각각 3회씩 시험하고, 추정 물성 사용 여부에 따른 최종 Pose MSE를 비교했다. 실행 중 시각을 사용하므로 Blind 실증은 아니다.

**저자 Limitation:** 물성 간 혼동으로 유사한 관측이 생길 수 있고, 필터 최대 약 5 Hz이며 단일 물체를 대상으로 한다. Pushing SOTA 제어기 비교가 목적은 아니다. **Future Work:** 계산량 감소, 변화하는 CoM·변형체·clutter 확장.

**근거:** 공개 저자본 arXiv:2411.09020v1, §III-A/F, §IV-B5, §IV-C. [원문](https://arxiv.org/html/2411.09020v1) · [DOI](https://doi.org/10.1109/TRO.2025.3531816)

<a id="a2"></a>

### A2. Haninger et al. — 접촉·지지 조건 모델 → MPC

**연결:** 관절 위치·토크/모터 입력 → compliant contact primitive의 offline fitting 및 online EKF → 갱신된 접촉 모델 → MPC. 강성·접촉 위치 등의 추정을 별도로 평가했고, **MPC 실험에서는 강성을 고정하고 접촉 기준 위치를 온라인 갱신**했다.

**검증:** 실제 로봇 2대로 추정·제어를 평가했다. 불확실한 높이의 표면을 따라 sliding하면서 접촉력을 유지하고, pivoting을 수행했다. Online 기준 위치 추정이 힘 추종에 도움을 주었다. **마찰계수 추정 사례는 아니다.**

**저자 Limitation:** 관측가능성 조건이 있으며, 두 위치 파라미터를 함께 추정할 때 힘 예측이 맞아도 위치 추정이 잘못될 수 있다. **Future Work:** 확인한 원문에서 별도 명시적 진술을 찾지 못했다.

**근거:** 공개 저자본 arXiv:2303.17476v3, §4.3, §5 식 (27)–(29), §6.2–6.3. [원문](https://arxiv.org/html/2303.17476v3) · [DOI](https://doi.org/10.1109/ICRA57147.2024.10611406)

<a id="a3"></a>

### A3. Xue et al. — 제목의 ‘Implicit’과 외부 추정기 존재를 구분

**연결:** 상태·행동 이력 → MLP 물성 추정값 및 주변 분포 → Tensor Train으로 표현한 advantage를 분포에 대해 결합 → 행동 최적화. Push 모델은 질량·반경·물체–테이블 마찰을 포함한다. **이 논문에서 implicit은 행동 정책의 표현·검색 방식이며, 물성 추정 모듈을 제거했다는 뜻이 아니다.**

**검증:** Hit·Push·Reorientation을 평가하고, Franka와 카메라로 재질이 다른 지지면 위의 실제 pushing을 수행한다. 상태에 현재 물체 Pose가 포함되어 Blind 조건과 다르다.

**저자 명시 범위/한계:** 구현은 단순 MLP와 지정한 폭의 균등분포를 사용한다(§5.2). 독립적인 한계 목록은 확인하지 못했다. **Future Work:** 더 풍부한 분포 모델 및 다른 정책 학습·behavior cloning 계열과 결합.

**근거:** 기술 검토는 arXiv:2412.11829v1 §5.2–5.3, §6.1/6.5, §7 기준. 저널 최종본과의 전면 대조는 하지 않았다. [원문](https://arxiv.org/html/2412.11829v1) · [2025-06-12 온라인 출판/DOI](https://doi.org/10.1177/02783649251344638)

## 4. B — 별도 물성 추정기 없이 정책 이력과 DR로 대응한 연구

여기서 ‘별도 모듈 없음’은 **실행 중 물리 파라미터 추정기가 없음**을 뜻한다. 카메라 Pose 추정, 저수준 제어기, 사전 시뮬레이터 보정까지 없다는 의미는 아니다.

<a id="b1"></a>

### B1. Del Aguila Ferrandis et al. — Sweeping과 가장 가까운 직접 근거

**연결:** 물체 Pose·pusher 위치·목표 → **10시점 stack+MLP 또는 LSTM 정책** → 평면 pusher 속도. §III-A는 현재 관측에서 빠진 마찰 접촉력·물체 속도를 이력으로 보완한다고 설명한다. 과거 행동을 별도 입력한다고 명시하지는 않는다.

**DR:** 마찰·반발계수, 상자 질량, 상자·pusher 크기, 행동 지속시간을 바꾸고 관측 잡음·외력을 추가한다.

**검증:** 실제 KUKA에서 75회 중 97.3% 성공(위치 0.75 cm·방향 약 9.7° 이내). **현재 물체 Pose는 Vicon으로 계속 관측**한다. LSTM과 stack을 비교했지만, 무이력 대비 효과나 마찰값 복원은 입증하지 않았다.

**저자 명시 범위/한계:** 목표 지향 planar pushing이며 미관측 형상·onboard perception은 확장 대상이다. **Future Work:** 연속 행동의 multimodal exploration, implicit policy, 형상·지각 확장.

**근거:** arXiv:2308.02459v1 §III-A/C, §IV·Table II, §V–VII. [원문](https://arxiv.org/html/2308.02459v1) · [DOI](https://doi.org/10.1109/IROS55552.2023.10341629)

<a id="b2"></a>

### B2. Sievers et al. — Blind 조건을 보완하는 조작 사례

**연결:** 측정 관절각·PD 제어오차의 **5시점 stack** → SAC MLP → 관절 제어 목표. 현재 물체 Pose나 물성값은 actor에 제공하지 않는다. 논문은 tactile이라 부르지만, 이 프로젝트의 Binary skin과 달리 관절 토크 제어와 제어오차로 하중 반응을 활용한다.

**DR:** 로봇 geometry·dynamics/contact 파라미터, 물체 질량·크기·초기 Pose, 센서 잡음·sticky action. **사전 simulator system identification은 수행했다.** 실행 중 대상별 추정기가 없다는 사실과 구분한다.

**검증:** 최대 40초 평가에서 최고 시행 회전량(15 rad)의 80% 이상에 도달한 시행이 10회 중 8회였다. 별도 장시간 실행에서 46회전을 보였다. 다른 논문의 성공률과 직접 비교할 지표는 아니다.

**저자 명시 범위/한계:** 주된 대상은 cube의 주축 회전이다. **Future Work:** x/y축 회전과 임의의 알려진 형상으로 확장(§V). Sweeping 일반화는 본 보고서에서도 미검증으로 둔다.

**근거:** arXiv:2204.03698v2 §II-D/E, §III-B2/E, §IV–V. [원문](https://arxiv.org/html/2204.03698v2) · [DOI](https://doi.org/10.1109/ICRA46639.2022.9812093)

<a id="b3"></a>

### B3. DeXtreme — Recurrent policy와 물리 DR의 추가 사례

**연결:** 시각으로 추정한 물체 Pose·목표·관절각·이전 행동 → LSTM 정책 → 손 관절 명령. 질량·마찰 등 정답 정보는 critic 측에 두며 실행 actor의 물성 입력으로 사용하지 않는다.

**DR:** 질량·마찰·반발계수·크기, 구동 강성·감쇠·지연, 잡음·외력 등을 변화시키며 ADR로 범위를 조절한다. 실제 Allegro Hand에서 연속 재배향과 sim-to-real을 검증했다.

**분류:** 물성 추정기 없는 recurrent+DR 사례지만, **시각 Pose 추정 모듈은 존재**한다. ADR은 학습 분포 조절이며 실행 중 물성 식별과 다르다.

**저자 Limitation:** sim-to-real 및 Pose 추정 차이, 실행·seed별 성능 편차가 남는다. **Future Work/후속 방향:** Pose 추정의 신뢰성·학습 데이터 다양성·하드웨어 문제 개선.

**근거:** 공개 확장 저자본 arXiv:2210.13702v2(2024) §2.3, §2.5–2.7, §3, §5. 학회 게재연도 2023과 읽은 버전을 구분한다. [원문](https://arxiv.org/html/2210.13702v2) · [DOI](https://doi.org/10.1109/ICRA48891.2023.10160216)

<a id="c1"></a>

## 5. C — HORA: 물성을 직접 출력하지 않아도 별도 적응 모듈이 존재

**연결:** 관절·행동 **30시점 이력** → 별도로 학습한 adaptation module → 8차원 latent → 기본 정책. 시뮬레이션의 물체 위치·크기·질량·마찰·CoM을 인코딩한 latent를 학습 목표로 사용하며, 실행 중에는 정답 물성이나 시각을 받지 않는다.

**검증 의미:** 실제 다양한 물체의 회전에서 DR·명시적 SysID·latent 고정 조건과 비교한다. 따라서 정확한 물성값 대신 과업 관련 잠재표현을 활용할 근거가 된다. 그러나 **‘별도 모듈 없는 end-to-end 이력 정책’의 근거는 아니다.**

**저자 Limitation:** 정확한 접촉 위치를 모르므로 force closure가 깨지며, 작은 물체·복잡한 형상에서 어려움이 남는다. **Future Work:** 다축 회전, 추가 센싱, 실물 데이터 활용.

**근거:** §3.1–3.2, §4–6 및 공개 부록 C. [출판본](https://proceedings.mlr.press/v205/qi23a/qi23a.pdf) · [부록 포함 공개 원문](https://arxiv.org/html/2210.04887v1) · [CoRL/PMLR 출판 정보](https://proceedings.mlr.press/v205/qi23a.html)

## 6. 2.4절에서 사용할 수 있는 주장과 피해야 할 주장

| 판단 | 사용 가능한 서술 | 근거 또는 이유 |
| --- | --- | --- |
| 근거 확보 | 물성·접촉 모델을 별도 추정하여 planning/control에 제공하는 접근이 존재한다 | A1–A3 |
| 근거 확보 | Pushing에서도 물성 추정기 없이 이력·DR을 결합한 정책이 실물로 전이되었다 | B1. 현재 Pose는 계속 제공됨 |
| 근거 확보 | 시각으로 현재 물체 상태를 주지 않고 관절·하중 반응 이력으로 조작한 사례가 있다 | B2. 센서·태스크는 본 연구와 다름 |
| 과장 금지 | 이력이 있으므로 마찰·질량을 정확히 알아낸다 | 행동 성공과 물성 식별은 다른 검증 문제 |
| 과장 금지 | DR 성공은 실행 중 적응을 입증한다 | 이력·DR·현재 피드백의 효과를 분리하지 않은 결과로는 부족 |
| 논리 수정 | Blind이므로 명시적 추정이 불가능하다 | 정답을 받지 않아도 센서에서 추정값을 만들 수 있음 |
| 논리 수정 | 명시적 추정은 이력 방식보다 열등하다 | 관측·과업이 다른 논문 간 결과로 보편적 우열을 정할 수 없음 |
| 용어 수정 | 모든 연구가 명시 모델 또는 모듈 없는 이력 정책으로 양분된다 | C1 같은 별도 latent 적응 구조가 존재 |

**우선 읽을 순서:** A1 → B1 → B2 → C1. 각각 물성 추정의 직접 사례, 같은 pushing 과업의 이력 사례, Blind 조작 사례, 명시값 복원과 latent 적응의 비교를 제공한다. A2·A3·B3은 분류와 적용 범위를 보완한다.

## 7. 2.4절 반영 문안 — 제안

### 2.4.1. 명시적 물성·접촉 모델을 추정하는 방향

관측된 운동과 접촉 반응으로 물성 또는 접촉 모델을 추정하고, 추정값이나 그 불확실성을 계획·제어에 제공한다. [Dutta et al.](https://doi.org/10.1109/TRO.2025.3531816)은 물성 추정을 목표 지향 pushing의 MPC에 연결하며, [Haninger et al.](https://doi.org/10.1109/ICRA57147.2024.10611406)은 접촉 모델 추정을 MPC에 반영한다. 이 접근에서도 시간 이력을 사용할 수 있다.

본 연구에 적용하려면 제한된 F/T·촉각에서 필요한 파라미터가 얼마나 구분되는지, 추정 오차가 행동 선택에 어떤 영향을 주는지 검증해야 한다. 이는 명시적 모델 전체가 부적합하다는 결론이 아니라, 별도 검증이 필요한 설계 선택이다.

### 2.4.2. 물성 추정값을 요구하지 않는 이력 기반 정책

관측·행동·반응의 이력을 정책의 입력 또는 내부 기억에 반영하여, 물성의 명시적 복원 없이 행동을 선택할 수 있다. [Del Aguila Ferrandis et al.](https://doi.org/10.1109/IROS55552.2023.10341629)은 pushing에서 관측 stack 또는 LSTM을 활용하고, [Sievers et al.](https://doi.org/10.1109/ICRA46639.2022.9812093)은 시각 없는 손 안 조작에서 관절 상태·제어오차 stack을 활용한다. 두 사례의 센싱·과업 차이를 고려하면, 이 결과가 곧바로 본 연구의 Blind Sweeping 성공을 보장하지는 않는다.

별도 latent 적응 모듈을 사용하는 [Qi et al.](https://proceedings.mlr.press/v205/qi23a.html)은 관련 접근으로 구분한다. 물성값을 출력하지 않는다는 사실만으로 모듈 없는 정책이라고 분류하지 않는다.

### 2.4.3. 본 연구의 선택과 검증 범위

본 연구는 현재 물체 Pose와 정답 물성치를 최종 Blind Actor에 제공하지 않는다. 물성 자체의 정확한 복원보다 제한된 센싱으로 적절한 Sweeping 행동을 선택하는 것이 목표이므로, **Binary 촉각·Wrench·고유감각·적용 행동의 이력을 정책에 통합하는 방향을 우선 검토한다.** 이는 관측 조건과 연구 목적에 따른 설계 선택이며, 명시적 추정의 불가능성이나 이력 방식의 보편적 우월성을 뜻하지 않는다.

Domain Randomization은 정책이 경험할 물체·환경·로봇 조건의 분포를 제공한다. 이력은 실행 중 반응을 누적할 수 있게 하고, DR은 학습 중 조건의 다양성을 제공하므로 역할을 구분한다. 두 요소의 실제 기여와 결합 센싱의 충분성은 본 연구에서 검증해야 한다.

## 8. 남은 검증 질문 — 연구 제안

문헌은 방법 선택의 근거를 제공하지만, 현재 센서 구성의 관측가능성을 대신 입증하지 않는다. 최소한 다음을 구분해 확인할 필요가 있다.

1. **이력 효과:** 같은 DR·센싱·학습 예산 아래 현재 관측만 사용하는 정책과 이력 정책 비교.
2. **DR 효과:** 같은 정책 구조에서 학습 물리 조건의 변동 유무·범위에 따른 성능 비교.
3. **일반화:** 학습 중 본 조건과 새로운 물체·마찰·지지 조건을 구분해 평가. 분포 밖 성공을 당연시하지 않음.
4. **물리 결과:** GT는 평가용으로 분리하고, EEF 이동과 실제 대상 물체 이동을 구분. 성공률과 함께 회전·접촉 손실·과도 하중을 확인.

이 실험들은 제안이며 확정된 구현 범위·수치·일정이 아니다. 모든 조합을 즉시 학습할 필요는 없으며, 현재 관측 부족과 실패 원인을 구분하는 비교부터 수행한다.

## 부록. 기존 상세 리뷰 제외 목록

아래 27개 파일에 해당하는 논문은 이번 신규 조사 후보에서 제외했다. `README.md`는 논문 수에 포함하지 않는다. PDF 보유나 후보 목록 등록만으로 제외한 것이 아니다.

```text
2019-wu-mat-adaptive-tactile-grasping.md
2020-beltran-hernandez-learning-force-control.md
2021-ding-sim-to-real-tactile-manipulation.md
2022-lin-tactile-gym-2-0.md
2023-lin-attention-for-robot-touch.md
2023-lin-bi-touch.md
2023-yang-sim-to-real-tactile-pushing.md
2023-yin-rotating-without-seeing.md
2024-heins-force-push.md
2024-lee-dextouch.md
2024-liu-tactile-active-inference-rl.md
2024-lloyd-pose-and-shear-based-tactile-servoing.md
2024-ozdamar-pushing-in-the-dark.md
2024-su-sim2real-tactile-manipulation.md
2024-wu-1khz-tactile-insertion.md
2024-yuan-robot-synesthesia-visuotactile.md
2024-zhao-unknown-object-retrieval.md
2025-bergmann-precision-focused-pushing.md
2025-chen-vividex.md
2025-dadiotis-dynamic-object-goal-pushing.md
2025-dengler-location-based-attention-pushing.md
2025-miller-enhancing-tactile-rl.md
2025-yang-pseudo-tactile-gripper-state.md
2025-zhang-role-of-tactile-sensing.md
2026-brouwer-gentle-object-retraction.md
2026-pan-beyond-binary-cop-tactile.md
2026-simundic-visuo-force-tactile-door-opening.md
```

추가 후보 중 Ueno et al.의 IROS 2024 multi-fingered dragging은 [출판·초록](https://waseda.elsevierpure.com/ja/publications/multi-fingered-dragging-of-unknown-objects-and-orientations-using/)에서 ViT–LSTM 구조를 확인했으나 원문 세부 검증이 부족하여 주요 7편에 포함하지 않았다. Phys2Real은 [저자 프로젝트](https://phys2real.github.io/)에서 ICRA 2026을 확인했지만 이번 목록에서는 정식 출판 기록 검증을 완료한 기존 연도 후보들을 우선했다. 두 후보를 상세 리뷰 완료로 처리하지 않는다.
