# Making Sense of Vision and Touch: Self-Supervised Learning of Multimodal Representations for Contact-Rich Tasks

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [Wrist Wrench 조사 연결 문헌 — W5 Ref. [19]](../reviews/2026-09-21_wrist-wrench-manipulation-survey.md#ref-w5-19-lee-2019)

> **사용자 확인 상태:** **미확인** — 상세 리뷰는 작성되었지만, 사용자가 아직 직접 확인하지 않은 논문이다. (2026-09-22)

## 1. 논문 정보와 확인 범위

- **제목:** Making Sense of Vision and Touch: Self-Supervised Learning of Multimodal Representations for Contact-Rich Tasks
- **저자:** Michelle A. Lee, Yuke Zhu, Krishnan Srinivasan, Parth Shah, Silvio Savarese, Li Fei-Fei, Animesh Garg, Jeannette Bohg
- **게재:** 2019 International Conference on Robotics and Automation (ICRA), pp. 8943–8950
- **DOI:** [10.1109/ICRA.2019.8793485](https://doi.org/10.1109/ICRA.2019.8793485)
- **공개 원문:** [arXiv:1810.10191v2](https://arxiv.org/abs/1810.10191)
- **확인 원문:** 사용자 제공 IEEE ICRA 2019 출판본 PDF 8쪽 전체
- **원문 PDF SHA-256:** `04e06023bab7013215bb1b09ecb5398bddb39591d106a161476bdbfe2d0e0371`
- **원문이 안내한 자료:** [프로젝트 페이지·보충 영상](https://sites.google.com/view/visionandtouch)
- **이번 정독에서 확인하지 않은 자료:** 보충 영상, 코드 실행, 수집 데이터 원본, 원문이 인용한 58편의 전체 본문, 2020년 IEEE T-RO 확장판

원문 PDF를 텍스트 추출하고 8개 전 페이지를 PNG로 렌더링하여 본문, Fig. 1–6, 식 (1), staged reward 식과 참고문헌을 대조했다. 아래의 `[원문 §…, PDF p.…]`는 첨부 PDF의 첫 페이지를 p.1로 센 기준이다.

**핵심:** 이 논문은 고정 RGB 카메라, 손목 장착 6축 F/T 센서의 최근 32 ms 이력, end-effector proprioception을 각각 인코딩해 128차원 multimodal representation으로 융합한다. 이 표현은 action-conditional optical flow, 다음 control cycle의 contact, 세 센서 stream의 temporal alignment를 맞히는 self-supervised loss로 먼저 학습한다. 이후 표현망을 고정하고, TRPO가 이 128차원 표현에서 3D Cartesian displacement를 출력하도록 별도로 학습한다. 실물 KUKA LBR IIWA peg insertion에서 각 형상 전용 정책과 새로운 형상으로의 transfer를 평가한다. [원문 Abstract, §III–VII]

다음 경계를 먼저 유지해야 한다.

- 논문이 `touch` 또는 `haptic`이라고 부르는 주된 접촉 신호는 **손목 장착 6축 F/T 센서의 전역 Wrench**다. 분포형 tactile array나 접촉 위치 영상이 아니다.
- 정책은 F/T만 사용하지 않는다. RGB와 proprioception을 계속 함께 사용한다.
- Self-supervised representation과 RL policy를 동시에 end-to-end로 학습하지 않는다. 표현을 먼저 학습한 뒤 **고정**하고 TRPO policy를 학습한다.
- RL actor의 action은 위치와 자세를 모두 제어하는 6-DoF 명령이 아니라 **3D end-effector 위치 변위**다.
- 이 논문은 2019년 출판물이므로 [2026-09-21 Wrist Wrench 조사](../reviews/2026-09-21_wrist-wrench-manipulation-survey.md)의 2022년 이후 선별 조건에는 포함되지 않는다. W5의 참고문헌 [19]에서 거슬러 올라간 연결 선행문헌으로 별도 등록한다.

---

## 2. 문제 설정과 연구 동기

### 2.1. 왜 vision과 F/T를 함께 쓰는가

Peg insertion의 reaching 단계에서는 카메라가 box와 hole의 대략적 위치를 제공한다. Contact 이후에는 peg가 box 표면에 닿고 미끄러지거나 hole edge에 걸리므로, 영상만으로는 잘 보이지 않는 접촉 변화가 force profile에 나타난다. 저자들은 두 modality가 상보적이지만 차원, sampling frequency와 신호 성격이 달라 수작업 feature와 controller 설계만으로 결합하기 어렵다고 본다. [원문 §I, Fig. 1, PDF p.1]

### 2.2. 왜 표현 학습과 정책 학습을 분리하는가

고차원 RGB와 고주파 F/T를 곧바로 real-robot deep RL에 넣으면 sample complexity가 커진다. 논문은 먼저 별도 trajectory dataset에서 compact state representation을 self-supervision으로 학습한 뒤, RL에서는 그 표현을 고정해 학습 파라미터를 줄이는 방식을 택한다. 정책 학습 시 trainable parameter는 전체 모델의 약 3%라고 보고한다. [원문 §III–V, PDF pp.2–4]

### 2.3. 연구 질문

원문 §VI는 실험 질문을 세 가지로 정리한다.

1. 모든 modality를 사용할 때 일부 modality만 쓸 때보다 contact-rich manipulation 성능이 좋은가?
2. 학습된 표현을 사용하면 실물 로봇에서 RL policy 학습이 실용적인 sample 수로 가능한가?
3. 학습한 표현은 peg geometry 변화에 전이되고 sensor noise·외부 교란에서 회복하는가?

---

## 3. Related Work의 비교 구도

이 절은 원문 §II가 선행연구를 배치한 방식이다. 각 인용 논문의 원문을 이번 작업에서 다시 검증했다는 뜻은 아니다.

| 범주 | 원문이 인정하는 역할 | 이 논문이 구분하는 지점 |
| --- | --- | --- |
| 고전 contact-rich manipulation | Force control과 접촉 형상 지식을 이용해 정밀 삽입 수행 | 새로운 geometry마다 contact configuration·controller 재설계가 필요할 수 있음 |
| Vision 기반 deep policy | RGB와 proprioception에서 다양한 조작을 학습 | Tight-clearance contact 단계에서는 haptic 정보가 빠질 수 있음 |
| Haptic-only RL | Raw F/T 또는 tactile latent에서 조작 정책 학습 | Vision과 touch의 상보성을 동시에 사용하지 않음 |
| Simulation-to-real contact policy | 실물 sample 사용을 줄임 | 당시 contact simulation의 fidelity 제약 때문에 haptic feedback 활용이 제한적 |
| Autoencoder·prediction 기반 state representation | 고차원 관측을 compact latent로 변환 | Raw reconstruction 대신 action-relevant optical flow·contact와 cross-modal alignment를 예측 |
| Multimodal classification | Vision·haptic·audio 등을 물체·재질 분류에 결합 | 분류가 아니라 contact-rich control의 state 표현을 목표로 함 |

논문의 신규성은 새로운 F/T 센서나 새로운 RL algorithm이 아니다. **서로 다른 세 modality를 self-supervised predictive tasks로 묶은 표현, 그 표현을 고정한 TRPO policy, 그리고 compliant torque controller를 하나의 실물 insertion pipeline으로 연결한 것**이다. [원문 §II–V]

---

## 4. 로봇, 센서와 과업 환경

| 항목 | 원문에 명시된 내용 | 확인 위치 |
| --- | --- | --- |
| 로봇 | KUKA LBR IIWA, 7-DoF torque-controlled robot | §VI, PDF p.4 |
| 실물 시각 | 고정 Kinect v2, robot을 바라보도록 배치 | §VI |
| 시뮬레이션 시각 | CHAI3D rendering | §VI |
| RGB policy 입력 | 128×128×3 | §IV-A, §VI |
| 실물 F/T | OptoForce, 마지막 관절과 peg 사이에 장착 | §VI |
| F/T raw rate | 1 kHz | §II-B, Fig. 3 |
| F/T network 입력 | 최근 32개 6축 reading, 32×6 time series | §IV-A, Fig. 2 |
| Proprioception | End-effector 위치·속도; 실험 설정은 pose와 linear/angular velocity로 서술 | §IV-A, §VI |
| Policy rate | 20 Hz | §V, Fig. 3 |
| Trajectory/controller rate | 200 Hz | §V, Fig. 3 |
| 시뮬레이션 contact | SAI 2.0 rigid-body contact simulation | §VI |

실물 F/T가 1 kHz로 들어오고 policy는 20 Hz로 갱신되므로, 각 policy step의 F/T branch는 **직전 32 ms**의 짧은 waveform을 본다. 32개 reading을 policy step 32개 이력으로 해석하면 안 된다.

센서의 정량 range, resolution, accuracy, overload, F/T 좌표계, gravity·payload compensation, bias 제거와 filtering은 원문에 명시되지 않는다. `OptoForce`의 정확한 제품 모델도 적지 않았다.

### 4.1. Peg insertion task

과업은 reaching → box surface contact → sliding search·alignment → insertion → hole bottom 도달의 순서다. Peg와 hole은 round, square, triangular, semicircular, hexagonal의 다섯 형상을 3D print했다. Fig. 5가 제시한 clearance는 각각 round 2.15 mm, square 2.24 mm, triangular 2.13 mm, semicircular 1.85 mm, hexagonal 2.50 mm다. [원문 §VI, Fig. 1·5, PDF pp.1, 6]

Policy action은 3D Cartesian displacement이므로 peg orientation은 policy가 바꾸지 않는다. Full 6-DoF insertion을 해결한 결과로 확대하면 안 된다.

---

## 5. 전체 메소드: 학습과 실행의 end-to-end 흐름

논문의 전체 절차는 두 개의 학습 단계와 한 개의 실행 controller로 나뉜다.

### 5.1. Stage A — Multimodal trajectory 수집

1. Random policy와 peg가 box에 접촉하도록 유도하는 heuristic policy를 실행한다.
2. 각 state에서 RGB, 최근 32개 F/T reading, proprioception과 다음 action을 기록한다.
3. Robot kinematics·geometry에서 optical-flow label을 만들고, F/T heuristic에서 다음 contact label을 만든다.
4. 시간 정렬된 세 modality와 임의로 shift한 modality 조합을 만들어 alignment label을 만든다.

수집된 dataset은 100,000 states다. Policy가 20 Hz로 실행되며 수집에는 90–120분이 걸린다. Heuristic policy는 **표현 학습용 data collector**이지 TRPO를 지도하는 teacher policy가 아니다. [원문 §IV-B, §VI Implementation Details, PDF pp.3, 5]

### 5.2. Stage B — Self-supervised representation pretraining

1. Image, F/T, proprioception을 modality별 encoder로 처리한다.
2. 세 feature를 concatenate하고 fusion MLP로 128차원 multimodal representation을 만든다.
3. 다음 action을 조건으로 optical flow와 다음-step contact를 예측한다.
4. Multimodal representation만으로 세 sensor stream이 같은 시각의 관측인지 판별한다.
5. 세 prediction loss의 합으로 encoder·fusion·prediction head를 end-to-end 학습한다.

Representation model은 Titan V에서 20 epochs 학습한다. 이 단계에는 task reward나 TRPO gradient가 들어가지 않는다. [원문 §IV, §VI]

### 5.3. Stage C — Frozen representation 위의 RL policy

1. Representation encoder와 fusion parameter를 고정한다.
2. 매 20 Hz step에서 현재 multimodal observation을 128차원 vector로 바꾼다.
3. 2-layer MLP TRPO policy가 3D end-effector displacement를 출력한다.
4. Staged insertion reward로 policy를 학습한다.

Optical-flow·contact·alignment prediction head는 policy action을 직접 출력하지 않는다. 또한 RL 학습 중 representation을 fine-tune하지 않는다. [원문 §V]

### 5.4. Stage D — Compliant torque execution

1. 현재 end-effector 위치에 policy displacement를 더해 목표 위치를 만든다.
2. Trajectory generator가 20 Hz 목표를 200 Hz position·velocity·acceleration trajectory로 보간한다.
3. PD impedance controller가 task-space acceleration command를 계산한다.
4. Operational-space dynamics가 Cartesian acceleration을 end-effector force와 joint torque로 변환한다.
5. KUKA IIWA가 torque command를 실행하고 다음 sensor observation이 policy loop로 돌아온다.

따라서 성능은 learned representation·TRPO policy만의 결과가 아니라, **고정 orientation·Cartesian displacement action·trajectory interpolation·PD impedance·operational-space torque control**을 함께 사용한 시스템 결과다. [원문 §V, Fig. 3, PDF p.4]

---

## 6. Modality encoder와 128차원 fusion

### 6.1. RGB image branch

고정 카메라의 128×128×3 RGB image를 FlowNet과 유사한 6-layer CNN으로 인코딩한다. 마지막 activation map에 fully connected layer를 적용해 **128차원 visual feature**를 만든다. [원문 §IV-A]

### 6.2. F/T history branch

최근 32개의 6축 force·torque reading을 32×6 time series로 구성한다. 5-layer causal convolution과 stride 2를 사용해 **64차원 haptic feature**를 만든다. Causal convolution이므로 현재 표현에 미래 F/T가 들어가지는 않는다. [원문 §IV-A]

이 branch가 보는 정보는 개별 contact patch의 분포가 아니라 wrist에서 합성된 3축 force와 3축 moment의 짧은 시간 변화다.

### 6.3. Proprioception branch

현재 end-effector 위치와 속도를 2-layer MLP로 인코딩해 **32차원 proprioceptive feature**를 만든다. 실험 설정 절은 pose 및 linear/angular velocity라고도 표현하지만, 정확한 input vector 차원과 orientation 표현은 열거하지 않는다. [원문 §IV-A, §VI]

### 6.4. Fusion

세 feature 128+64+32차원을 concatenate한 뒤 2-layer MLP를 통과시켜 최종 **128차원 multimodal representation**을 만든다. Modality encoder 전체에는 약 50만 개의 learnable parameter가 있다고 설명한다. [원문 §IV-A–B, Fig. 2]

이 fusion은 attention이나 recurrent memory가 아니다. F/T의 32 ms 이력은 causal convolution에서만 처리되고, 최종 policy도 2-layer feed-forward MLP다.

---

## 7. 세 가지 self-supervised objective

### 7.1. Action-conditional optical flow prediction

현재 multimodal representation과 **다음 end-effector action**을 입력받아 action 이후의 128×128×2 optical-flow map을 예측한다. Action은 2-layer MLP로 인코딩한다. Flow decoder는 upsampling이 있는 6-layer convolutional network이며 image encoder에서 네 개의 skip connection을 받는다. Ground truth는 알려진 robot kinematics와 geometry로 자동 생성한다. [원문 §IV-B, Fig. 2]

Loss는 모든 pixel의 endpoint error(EPE) 평균이다. 이 objective는 visual branch가 scene appearance만 압축하는 대신, action에 따라 로봇 영상이 어떻게 변할지를 보존하도록 유도한다.

### 7.2. Action-conditional next-contact prediction

같은 representation과 다음 action을 2-layer MLP contact predictor에 넣어 다음 control cycle에 contact가 생길지를 binary classification한다. Label은 F/T reading에 간단한 heuristic을 적용해 자동 생성한다. Cross-entropy loss를 사용한다. [원문 §IV-B]

여기서 다음 contact label은 representation pretraining의 supervision이다. TRPO reward나 policy termination signal로 직접 사용된다고 적혀 있지 않다.

### 7.3. Cross-modal temporal alignment prediction

RGB·F/T·proprioception이 같은 시각에 정렬되었는지 판별한다. 학습 시 실제로 time-aligned된 sample과 sensor stream을 임의로 shift한 sample을 섞고, 2-layer MLP가 multimodal representation에서 aligned/not-aligned를 이진 분류한다. Cross-entropy loss를 사용한다. [원문 §IV-B]

이 objective의 목적은 `peg를 본다`, `box를 만진다`, `force를 느낀다`처럼 동시에 발생하는 cross-modal redundancy를 latent에 담는 것이다. Sensor timestamp를 online으로 보정하는 synchronization algorithm은 아니다.

### 7.4. 결합 loss와 학습 범위

원문은 세 loss를 합해 stochastic gradient descent로 end-to-end 최소화한다고 설명한다.

```math
\mathcal{L}_{repr}=\mathcal{L}_{flow}+\mathcal{L}_{contact}+\mathcal{L}_{align}.
```

각 항의 가중치, optimizer의 구체 종류, learning rate, batch size와 train/validation split은 ICRA 원문에 명시되지 않는다. 세 objective 각각을 제거한 ablation도 이 출판본에는 없다.

---

## 8. RL policy, 정보 경계와 reward

### 8.1. MDP와 policy

논문은 유한 horizon discounted MDP를 두고 다음 목적을 제시한다. [원문 §III, 식 (1), PDF p.2]

```math
J(\pi)=\mathbb{E}_{\pi}\left[\sum_{t=0}^{T-1}\gamma^t r(s_t,a_t)\right].
```

구현에서는 model-free TRPO를 사용한다. Policy network는 frozen 128차원 representation을 입력받는 2-layer MLP이고, 연속 3D Cartesian displacement $\Delta x$를 출력한다. TRPO의 KL constraint는 update가 이전 policy에서 지나치게 멀어지는 것을 막는다. [원문 §V]

### 8.2. Actor·value function·teacher의 구분

| 구성요소 | 입력·역할 | 원문 확인 상태 |
| --- | --- | --- |
| Actor policy | Frozen multimodal representation → 3D $\Delta x$ | 2-layer MLP로 명시 |
| Value/baseline | TRPO 학습에 통상 필요 | Architecture·입력·학습 설정 미명시 |
| Representation network | RGB + F/T history + proprioception → 128D | RL 중 고정 |
| Random/heuristic policy | Representation dataset 수집 | Teacher demonstration이나 policy distillation이 아님 |
| Privileged task state | Peg의 목표 대비 위치로 reward 계산 | Actor observation에는 포함되지 않음 |

Actor가 raw F/T를 직접 받는다고만 요약할 수는 있지만, 정확한 경로는 `32×6 F/T → causal CNN → fusion latent → actor`다. 반대로 reward에 쓰는 peg state를 actor가 입력받는다고 쓰면 안 된다.

### 8.3. Staged reward

Peg의 현재 위치를 $s=(s_x,s_y,s_z)$, 평면 성분을 $s_{xy}=(s_x,s_y)$, hole 깊이를 $h_d$로 두고 reaching·alignment·insertion·completion 단계의 reward를 순차적으로 사용한다. 원문 식은 다음과 같다. [원문 §VI Reward Design, PDF p.5]

```math
r(s)=
\begin{cases}
c_r-\dfrac{c_r}{2}\left(\tanh(\lambda\lVert s\rVert)+\tanh(\lambda\lVert s_{xy}\rVert)\right), & \text{reaching},\\
2-c_a\lVert s_{xy}\rVert_2, & \lVert s_{xy}\rVert_2\leq\epsilon_1 \quad \text{alignment},\\
4-2\dfrac{s_z}{h_d-\epsilon_2}, & s_z<0 \quad \text{insertion},\\
10, & h_d-\lvert s_z\rvert\leq\epsilon_2 \quad \text{completion}.
\end{cases}
```

이 reward는 F/T 자체에 대한 보상이나 force penalty가 아니다. Ground-truth에 가까운 peg position과 hole-relative task coordinate가 학습 reward에 필요하다. 실물에서 이 위치를 어떻게 계측·등록했는지, actor와 분리된 reward-only 센서가 무엇인지는 원문에 구체적으로 적혀 있지 않다.

---

## 9. Low-level controller

Policy가 현재 end-effector 위치 $x_t$에서 displacement $\Delta x$를 내면 목표 $x_{des}$를 정한다. Trajectory generator는 이를 200 Hz trajectory로 보간한다.

```math
\xi_t=\{x_k,v_k,a_k\}_{k=t}^{t+T}.
```

PD impedance controller는 desired acceleration과 현재 상태의 오차로 task-space acceleration command를 계산한다. [원문 §V, PDF p.4]

```math
a_u=a_{des}-k_p(x-x_{des})-k_v(v-v_{des}).
```

Operational-space inertial matrix $\Lambda$와 Jacobian $J(q)$를 이용해 Cartesian force와 joint torque로 변환한다.

```math
F=\Lambda a_u,\qquad \tau_u=J^T(q)F.
```

이 controller는 접촉 중 compliance와 실시간 반응성을 제공한다. 다만 robot dynamics model을 이용하므로, 논문이 policy를 `model-free RL`이라고 부르는 것은 **policy optimization에서 contact transition model을 학습·계획하지 않는다**는 의미다. 전체 실행 stack이 robot model을 전혀 사용하지 않는다는 뜻은 아니다.

---

## 10. Representation data와 policy 학습 절차

| 단계 | 데이터·횟수 | 고정·학습 대상 |
| --- | --- | --- |
| Representation 수집 | Random + contact-seeking heuristic rollout, 100k states, 90–120분 | Dataset 생성 |
| Representation 학습 | 20 epochs, Titan V | 세 encoder·fusion·세 prediction head 학습 |
| Simulation policy | 1,200 episodes, episode당 500 steps | Representation 고정, TRPO policy 학습 |
| Simulation 중간 평가 | 10 training episodes마다 stochastic policy 10 trials | 평균·표준편차 episode reward |
| Real policy | 300 episodes, episode당 1,000 steps, 약 5시간 | Representation 고정, shallow TRPO policy 학습 |
| Real 최종 평가 | Policy당 100 episodes | Task stage·success 집계 |

실물에서는 round, triangular, semicircular peg 각각에 representation model과 policy를 학습한 조건을 평가한다. Transfer 실험에서는 triangular peg에서 학습한 model을 재사용한다. [원문 §VII-B]

---

## 11. Simulation modality ablation

Square peg insertion에서 box 위치와 arm 초기 위치를 episode마다 randomize한다. 비교군은 표현 학습과 policy 학습에서 해당 modality를 제거한 다음 네 구성이다. [원문 §VII-A, Fig. 4]

| 구성 | 사용 modality | 원문 결과의 핵심 |
| --- | --- | --- |
| Full | Vision + F/T + proprioception | 약 76%가 hole bottom까지 complete; 약 22%가 hole 안까지 진입 |
| No haptics | Vision + proprioception | 약 절반이 hole 안까지 들어가지만 complete는 5% 미만 |
| No vision | F/T + proprioception | 대다수가 box에 touch하는 단계에 머묾 |
| No vision, No haptics | Proprioception only | Box contact 또는 실패가 대부분 |

Fig. 4의 training curve에서도 Full이 최종 normalized return이 가장 높다. No haptics가 다른 두 baseline보다 높은 이유로, 저자들은 vision이 contact 전 reaching·hole localization에 유용하고 F/T는 contact 이후에 주로 informative하다고 해석한다.

이 비교는 실행 때 sensor 하나만 masking한 민감도 실험이 아니다. **서로 다른 modality 조합으로 representation을 학습하고, 그 representation 위에서 별도 TRPO policy를 학습한 pipeline-level ablation**이다.

---

## 12. 실물 삽입 결과

### 12.1. 형상별 별도 학습

각 peg용 representation과 policy를 각각 학습했을 때 100회 평가의 complete-insertion 비율은 다음과 같다. [원문 §VII-B, Fig. 6, PDF p.6]

| Peg | Complete insertion |
| --- | ---: |
| Round | 92% |
| Triangular | 73% |
| Semicircular | 71% |

정책이 관찰상 학습한 전략은 box에 접근하고, surface를 따라 slide하며 hole을 찾고, peg를 정렬한 다음 삽입하는 순서다. 이는 별도 symbolic phase controller가 명시적으로 전환한 결과가 아니라 learned behavior에 대한 저자들의 서술이다.

### 12.2. 새로운 형상으로의 transfer

Triangular peg에서 학습한 모델을 hexagonal·square peg에 옮긴다. [원문 §VII-B, Fig. 6]

| Transfer 조건 | Hexagonal | Square |
| --- | ---: | ---: |
| Representation + policy 모두 그대로 | 62% | 62% |
| Representation 고정, 새 형상 policy 재학습 | 81% | 92% |

앞 조건은 새로운 형상에서 policy도 추가 학습하지 않은 transfer다. 뒤 조건은 representation만 재사용하고 policy는 새로 학습한다. 따라서 81/92%를 policy zero-shot transfer 성능으로 쓰면 안 된다.

### 12.3. 교란·가림

Rollout 중 카메라를 주기적으로 가리고 robot arm을 사람이 밀었을 때 policy가 회복했다고 보고한다. 그러나 본문에는 이 robustness 실험의 trial 수, 성공률, 교란 크기와 지속 시간이 없다. 정량 근거가 아니라 qualitative supplementary-video 관찰로 취급해야 한다. [원문 §VII-B, PDF p.6]

---

## 13. Ablation이 각 메소드 주장에 주는 근거

| 메소드 주장 | 대응 실험 | 말할 수 있는 범위 | 분리되지 않은 요소 |
| --- | --- | --- | --- |
| Vision과 F/T가 상보적 | Simulation Full / No haptics / No vision / proprio-only | 전체 pipeline에서 두 modality가 함께 있을 때 insertion completion이 높음 | Encoder capacity·representation quality·policy가 함께 바뀜 |
| Compact representation이 real RL을 가능하게 함 | Frozen representation + 300 episodes, 약 5시간 | 한 실물 setup에서 shallow policy 학습 가능 | Raw-input end-to-end RL과 같은 budget 직접 비교 없음 |
| Representation이 shape 변화에 전이 | Triangular representation을 hexagonal·square에 재사용 | Latent를 고정하고 policy를 재학습해 높은 성능 | 새 policy 학습 비용은 남음 |
| Policy도 shape 변화에 전이 | Triangular representation+policy 그대로 62/62% | 두 unseen peg에서 추가 policy 학습 없이 일부 성공 | 형상·clearance 범위가 다섯 3D-printed peg로 제한 |
| 세 self-supervised objective가 각각 필요 | 직접 대응 실험 없음 | 결합 objective로 pipeline이 작동함 | Flow/contact/alignment loss 제거 ablation 없음 |
| Robustness | Camera occlusion·manual push의 qualitative recovery | 교란 후 회복 사례 존재 | 정량 protocol·baseline·통계 없음 |

---

## 14. 저자들이 밝힌 Limitation

원문에는 독립적인 `Limitations` 절이 없고, Conclusion도 제한 사항을 명시적인 목록으로 제시하지 않는다. 다만 다음 범위는 원문 자체에서 확인된다.

- 실물 구현 절은 sensor synchronization, sensing-to-control delay와 복잡한 real-world dynamics가 추가적인 도전이라고 명시한다. [원문 §VII-B, PDF p.6]
- Conclusion의 향후 계획은 현재 controller가 position 3-DoF에 한정되어 있고 평가 과업이 peg insertion 계열임을 드러내지만, 저자들은 이를 `limitation`이라는 표현으로 따로 선언하지 않았다. [원문 §VIII]

아래 §16의 정보 부족과 해석 한계는 정리자의 검토이며, 저자 명시 limitation과 구분한다.

---

## 15. 저자들이 제시한 Future Work

원문 §VIII는 다음 세 방향을 명시한다.

1. **다른 contact-rich task로 확장**
2. **위치와 자세를 함께 다루는 full 6-DoF controller로 확장**
3. **Depth·sound 같은 더 풍부한 modality와 새로운 self-supervision source 탐색**

이는 향후 계획이며 현재 논문의 실험 결과가 아니다.

---

## 16. 원문 근거에서 추가로 구분해야 할 범위

### 16.1. F/T가 정책에 들어가지만 F/T-only policy는 아님

Full model은 RGB·F/T·proprioception을 모두 사용한다. 실물에서도 카메라를 계속 사용하므로 blind manipulation 근거로 확대하지 않는다.

### 16.2. `Touch`는 분포형 tactile이 아님

이 논문에서 haptic branch는 wrist OptoForce의 6D Wrench다. 접촉 위치, pressure image, taxel별 force를 직접 측정하지 않는다.

### 16.3. F/T의 독립 효과는 pipeline 수준으로만 분리됨

No haptics는 F/T input을 뺀 representation을 다시 학습하고 그 위에서 policy도 다시 학습한다. 같은 policy의 inference 중 F/T만 제거한 실험과는 다르다. 그래도 vision+proprioception과 full multimodal pipeline의 직접 비교라는 점에서는 센서 조합 근거가 된다.

### 16.4. Sample efficiency claim의 기준선

저자들은 frozen representation 덕분에 policy trainable parameter가 전체의 3%이고 실물 policy를 약 5시간에 학습했다고 보고한다. 그러나 raw multimodal end-to-end TRPO, random frozen encoder, autoencoder pretraining과 동일 budget 비교는 없다.

### 16.5. Reward의 privileged state

Actor는 multimodal latent를 보지만 reward는 hole-relative peg position을 사용한다. 이는 training-only task state이며 실행 actor observation과 분리해야 한다. 실물 reward state의 계측 방법이 불명확하므로 blind self-supervision만으로 전체 학습이 끝났다고 표현하지 않는다.

### 16.6. Generalization 범위

형상·clearance transfer는 의미가 있지만 동일 robot, camera, controller, peg-in-hole family와 3D-printed parts 안에서 평가했다. 전혀 다른 contact-rich task로 전이한 결과는 없다.

---

## 17. 원문에 명시되지 않은 구현·계측 정보

| 항목 | 확인 결과 |
| --- | --- |
| OptoForce 정확한 모델과 force/torque 사양 | 미명시 |
| F/T calibration·bias·gravity/payload compensation·filter | 미명시 |
| Camera–robot extrinsic calibration과 sensor synchronization 오차 | 미명시 |
| Proprioception의 정확한 vector 차원·orientation 표현 | 미명시 |
| 각 MLP hidden width·activation | 미명시 |
| Representation loss별 weight | 미명시; 단순 합으로 설명 |
| Representation optimizer·learning rate·batch size·split | 미명시 |
| TRPO KL bound·discount·GAE·value network·seed | 미명시 |
| Reward의 $c_r,c_a,\lambda,\epsilon_1,\epsilon_2$ 수치 | 미명시 |
| 실물 reward용 peg/hole position 계측 방법 | 미명시 |
| 교란·camera occlusion 실험의 정량 protocol | 미명시 |

---

## 18. 원문 위치 빠른 색인

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 문제 설정·기여·Fig. 1 force profile | Abstract, §I, PDF p.1 |
| Contact-rich manipulation·representation 선행연구 | §II, PDF pp.1–2 |
| MDP·representation→policy 개요 | §III, 식 (1), PDF p.2 |
| Modality encoder·fusion·Fig. 2 | §IV-A, PDF p.3 |
| Flow/contact/alignment self-supervision | §IV-B, PDF p.3 |
| TRPO policy·controller·Fig. 3 | §V, PDF pp.3–4 |
| Robot·sensor·reward·dataset 설정 | §VI, PDF pp.4–5 |
| Simulation modality ablation | §VII-A, Fig. 4, PDF pp.5–6 |
| Real insertion·shape transfer·교란 | §VII-B, Fig. 5–6, PDF p.6 |
| Conclusion·Future Work | §VIII, PDF p.6 |

---

## 19. 한 문장 요약

**Lee et al.은 32 ms의 손목 6축 F/T 이력, RGB와 proprioception을 action-conditional flow/contact 및 temporal-alignment self-supervision으로 128차원 표현에 압축하고, 그 표현을 고정한 TRPO policy와 compliant torque controller로 실물 peg insertion을 학습했지만, 3-DoF·연속 시각·privileged position reward·단일 task family의 범위는 유지해야 한다.**
