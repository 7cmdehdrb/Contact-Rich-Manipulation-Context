# MAT: Multi-Fingered Adaptive Tactile Grasping via Deep Reinforcement Learning

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [260918 Review Dataset B086](../review_dataset/260918/batch_003/papers/2019-wu-mat-adaptive-tactile-grasping.md) · [별도 확인 CHECK-B02](../reviews/2026-09-20_separate-review-paper-list.md)

> **사용자 확인 상태:** **미확인** — 상세 리뷰는 작성되었지만, 사용자가 아직 직접 확인하지 않은 논문이다. (2026-09-22)

## 1. 논문 정보와 확인 범위

- **제목:** MAT: Multi-Fingered Adaptive Tactile Grasping via Deep Reinforcement Learning
- **저자:** Bohan Wu, Iretiayo Akinola, Jacob Varley, Peter K. Allen
- **게재:** 3rd Conference on Robot Learning (CoRL 2019), Osaka, Japan
- **원문 버전:** arXiv:1909.04787v2, 2019-10-10
- **DOI:** 제공 원문에 명시되지 않음
- **확인 원문:** 사용자 제공 PDF 20쪽 전체
- **파일 SHA-256:** e73a3bfccf9ed4491e98f206e05b0bda76f007b04a4a7148bde9ea140c534a2e
- **확인 범위:** 본문 §1–6과 Appendix A.1–A.15, Fig. 1–12, Table 1–5, 식 (1)–(9)
- **확인하지 않은 자료:** 프로젝트 웹사이트의 영상, 코드, 별도 실험 로그는 이번 정독에서 검증하지 않음

이 PDF는 저장소의 260918 Review Dataset에 이미 포함된 B086 원문과 SHA-256이 동일하다. 이번 문서는 해당 데이터셋의 표준화 비교 레코드와 별도로, **논문 자체의 문제 설정·센서 처리·관측·행동·학습·실험·Appendix 구현 세부를 한 문서에서 읽을 수 있도록 정리한 정식 상세 노트**다.

## 2. 초록과 핵심 주장

MAT는 vision 기반 grasp planner가 제공한 **대략적인 초기 grasp pose**에서 시작한 뒤, grasp execution 동안 vision을 사용하지 않고 tactile과 proprioception으로 손가락과 손목을 계속 수정하는 closed-loop grasping 방법이다.

저자들이 문제 삼는 대표적인 실패는 camera–robot calibration error, object slip, low friction, adversarial shape 등이다. Vision-based open-loop grasping에서는 initial grasp가 조금만 틀려도 실패할 수 있고, 재시도 시에는 hand 자체가 camera view를 가려 current grasp state를 다시 정확히 보기 어렵다.

MAT는 다음 행동을 closed loop에서 선택한다.

1. 각 finger를 작은 increment만큼 추가로 닫기
2. 현재 grasp가 좋지 않다고 판단되면 모든 finger를 다시 열기
3. reopen 이후 tactile contact 위치를 이용해 hand 위치를 재조정하고 wrist orientation을 수정하기
4. grasp가 충분하다고 판단하면 lift하여 pick-up을 시도하기

정책은 **simulation에서만 학습**하고, binary tactile contact·joint angle·tactile-cell Cartesian location처럼 sim-to-real gap이 작도록 설계한 observation/action을 사용하여 추가 실물 학습 없이 실제 Barrett Hand로 전이한다.

## 3. 연구가 해결하려는 문제

### 3.1. Open-loop vision grasping의 남은 실패

저자들은 당시 vision 기반 multi-finger grasping이 이미 높은 성공률을 보이지만, 남은 실패 몇 퍼센트를 줄이기 위해서는 grasp execution 중 현재 접촉 상태에 반응하는 closed-loop correction이 필요하다고 본다.

Vision을 실행 중 feedback으로 계속 사용하기 어려운 이유는 다음과 같다.

- arm과 palm/finger가 object를 가림
- end-effector가 object에 가까워질수록 camera observation이 악화됨
- initial calibration error가 grasp execution 동안 그대로 남을 수 있음

따라서 MAT의 목표는 vision을 전체 시스템에서 제거하는 것이 아니라,

**초기 vision grasp pose → contact-rich execution에서는 tactile/proprioception으로 correction**

이라는 역할 분리를 만드는 것이다.

### 3.2. POMDP 관점

저자들은 실제 문제를 POMDP로 본다. 실행 중 visual information이 없고, tactile만으로 object의 완전한 3D geometry나 scene 전체를 관측할 수 없기 때문이다.

다만 실제 학습 formulation은 finite-horizon MDP 형태로 기술하며, 20-step tactile/proprioceptive history를 observation에 넣어 partial observability를 완화한다.

## 4. Related Works에서의 위치

원문 §2는 tactile grasping 연구를 다음과 같이 나눈다.

### 4.1. Vision-based closed-loop grasping

Vision으로 grasp를 지속 보정하는 연구는 존재하지만, hand가 object에 접근하면서 occlusion이 증가한다는 문제가 있다.

### 4.2. Tactile-only blind grasping

Tactile scanning으로 object location/geometry를 추정한 뒤 grasp하는 방법들이 있다. 저자들은 tactile coverage가 제한적이어서 scanning 도중 물체가 움직이면 scene state를 놓칠 수 있다고 지적한다.

### 4.3. Vision grasp를 tactile로 보완하는 접근

Tactile은 grasp 전 geometry 보완, grasp 성공 예측, regrasp 계획, finger closing feedback 등에 사용되어 왔다.

MAT가 강조하는 차이는 별도 grasp-success critic이 reopen을 trigger하는 구조가 아니라, **finger closing부터 reopen·reorientation·lift까지 하나의 end-to-end RL policy 안에서 선택**한다는 점이다.

### 4.4. RL tactile grasping

기존 RL tactile grasping은 simulation-only이거나 단순 object/linear policy에 제한된 사례가 있었다고 설명한다. MAT는 다양한 object와 clutter에서 deep policy를 simulation-only로 학습하고 real robot으로 직접 전이한다.

## 5. 하드웨어와 센서

### 5.1. Robot

- **Arm:** Staubli TX60
- **Hand:** Barrett Hand BH-282
- **Finger joint range:** 0 rad(open) ~ 2.44 rad(close)

### 5.2. Tactile sensor 구성

Barrett Hand에는 총 **96 capacitive tactile cells**가 있다.

- Finger 1: 24 cells
- Finger 2: 24 cells
- Finger 3: 24 cells
- Palm: 24 cells

실물 tactile stream은 **246 Hz**이며 각 cell은 0–20 범위의 force-like magnitude를 출력한다. 원문은 이 값의 물리 단위를 별도로 명시하지 않는다.

따라서 0–20을 N으로 해석하면 안 된다.

## 6. 실물 Tactile 전처리

Appendix A.13은 sim-to-real을 위해 tactile raw signal을 어떻게 binary contact로 만드는지 구체적으로 설명한다.

### 6.1. Running mean

실물 raw tactile은 noise가 있으므로 cell별 최근 **50 samples**의 running mean을 사용한다.

246 Hz 기준으로 50 sample window는 약 0.20 s에 해당하지만, 이 시간값은 원문에 직접 적힌 값이 아니라 sampling rate와 window 길이에서 계산한 값이다.

Simulation tactile은 안정적이라고 보고 별도 averaging을 하지 않는다.

### 6.2. Binary threshold

Running mean tactile value에 대해 threshold 0.8을 적용한다.

```math
T_{m,c}=\mathbf{1}[x_{m,c}>0.8].
```

Simulation과 real 모두 같은 0.8 threshold를 사용한다.

따라서 정책은 continuous tactile magnitude를 직접 받지 않고 **contact / no-contact의 binary state**를 받는다.

### 6.3. Real tactile에 proprioceptive effort를 더하는 보정

PyBullet의 contact는 collision resolution 과정에서 약한 interpenetration을 허용하는 soft contact 특성이 있는 반면, 실제 object contact는 더 hard하다고 저자들은 설명한다.

이 sim-to-real gap을 줄이기 위해 real robot에서는 해당 tactile finger가 느끼는 **proprioceptive effort를 그 finger의 raw tactile readings에 더한 뒤** binary thresholding한다.

즉 MAT의 real-world binary tactile은 단순히 raw sensor만 threshold한 값이 아니라, simulation contact 특성과 맞추기 위한 추가 보정이 포함된다.

## 7. Observation Space

Policy observation은 여섯 종류의 tensor로 구성된다.

```math
s_t=\{s_t^{\mathrm{contacts\ binary}},s_t^{\Delta\mathrm{contacts\ binary}},s_t^{\mathrm{joint\ angles}},s_t^{\Delta\mathrm{joint\ angles}},s_t^{\mathrm{contacts\ xyz}},s_t^{\Delta\mathrm{contacts\ xyz}}\}.
```

### 7.1. Binary tactile history

최근 20 timesteps의 96 tactile cell binary contact:

```math
s_t^{\mathrm{contacts\ binary}}\in\{0,1\}^{20\times96}.
```

Adjacent timestep의 contact 변화:

```math
s_t^{\Delta\mathrm{contacts\ binary}}\in\{-1,0,1\}^{19\times96}.
```

이 정보는 단순 현재 contact뿐 아니라 어느 cell이 새로 접촉했거나 contact를 잃었는지를 남긴다.

### 7.2. Finger joint history

Barrett Hand의 8 joint angle을 20 timesteps 저장한다.

```math
s_t^{\mathrm{joint\ angles}}\in\mathbb{R}^{20\times8}.
```

Adjacent joint change가 0.05 rad threshold를 넘었는지를 binary로 저장한다.

```math
s_t^{\Delta\mathrm{joint\ angles}}\in\{0,1\}^{19\times8}.
```

### 7.3. Tactile cell Cartesian position history

Active tactile cell의 Cartesian position을 forward kinematics로 계산하고 **end-effector frame**에서 표현한다.

```math
s_t^{\mathrm{contacts\ xyz}}\in\mathbb{R}^{20\times96\times3}.
```

Adjacent difference:

```math
s_t^{\Delta\mathrm{contacts\ xyz}}\in\mathbb{R}^{19\times96\times3}.
```

해당 tactile cell이 active가 아니면 position은 [0,0,0]으로 둔다.

### 7.4. Binary지만 저차원 관측은 아니다

위 tensor를 단순 scalar count로 펼치면

- binary contacts: 1,920
- binary contact deltas: 1,824
- joint angles: 160
- joint deltas: 152
- tactile xyz: 5,760
- tactile xyz deltas: 5,472

으로 총 **15,288 scalar entries**가 된다.

이는 이 문서에서 원문 tensor shape을 단순 합산한 값이다. 따라서 MAT의 tactile 표현은 **force magnitude를 binary로 축약**하지만, 96-cell 공간 분포와 20-step history를 그대로 유지하므로 정보 차원 자체는 크다.

## 8. Object Information과 Vision의 경계

### 8.1. Vision이 제공하는 것

Episode 시작 전 외부 grasp planner가 **initial 6-DoF grasp pose**를 제공한다.

MAT는 해당 pose 근처에서 grasp execution을 시작한다.

### 8.2. MAT 실행 중 제공되지 않는 것

정책 observation에는 다음이 없다.

- current RGB/RGB-D image
- current object pose
- object geometry / mesh
- object category
- object mass / friction
- wrist 6-axis F/T wrench

즉 object current state를 별도 estimator로 복원해서 policy에 넣는 구조가 아니다.

### 8.3. Sparse tactile의 한계를 저자들이 인정하는 부분

Appendix A.1.3에서 저자들은 sparse tactile information이 object가 어디에 있는지에 대한 단서를 주지만 **object pose에 대해서는 충분한 정보를 주지 못한다**고 명시한다.

이 때문에 reopen 후 wrist correction에서 pitch/yaw까지 자유롭게 바꾸지 않는다.

## 9. Action Space

MAT는 finger-level discrete action과 high-level regrasp/lift action을 함께 사용한다.

개념적으로 action은 다음과 같다.

```math
a_t=\{a_t^{\mathrm{finger1}},\ldots,a_t^{\mathrm{finger}n},a_t^{\mathrm{reopen}},a_t^{\mathrm{wrist\ rotation}},a_t^{\mathrm{lift}}\}.
```

Barrett Hand에서는 $n=3$이다.

## 10. Finger Closing Action

각 finger마다 독립적으로 close 여부를 binary로 선택한다.

```math
a_t^{\mathrm{finger}i}\in\{0,1\}.
```

Policy는 sigmoid output으로 Bernoulli probability를 만들고 action을 sample한다.

```math
a_t^{\mathrm{finger}i}\sim\mathrm{Bernoulli}(\mathrm{sigmoid}(f_{\mathrm{finger}i}(s_t))).
```

1이면 finger joint를 $\delta_{\mathrm{finger\ angle}}$만큼 닫는다.

이 increment는 curriculum의 핵심 변수다.

## 11. Reopen Action

정책은 모든 finger를 다시 열지 여부를 선택한다.

```math
a_t^{\mathrm{reopen}}\in\{0,1\}.
```

```math
a_t^{\mathrm{reopen}}\sim\mathrm{Bernoulli}(\mathrm{sigmoid}(f_{\mathrm{reopen}}(s_t))).
```

하지만 reopen은 policy sample만으로 결정되는 것은 아니다.

**최근 5 timesteps 동안 어떤 joint도 0.05 rad 이상 움직이지 않았으면 reopen이 강제로 1이 된다.**

따라서 MAT는 완전한 end-to-end learned action만으로 구성된 것이 아니라 일부 deterministic recovery condition을 포함한다.

Reopen timestep에서는 normal finger-close action을 실행하지 않는다.

## 12. Reopen 이후 Position Adjustment

모든 finger를 pre-grasp joint angle까지 연 뒤, 최근 tactile contact를 이용해 palm 위치를 재설정한다.

각 tactile link $m$의 active cell 집합을 $\bar C_m$, active tactile link 집합을 $\bar M$이라 할 때 새 palm x/y는 active link별 tactile center의 평균으로 계산한다.

```math
x_{\mathrm{new}}=\frac{1}{|\bar M|}\sum_{m\in\bar M}\frac{1}{|\bar C_m|}\sum_{c\in\bar C_m}x_{m,c}.
```

```math
y_{\mathrm{new}}=\frac{1}{|\bar M|}\sum_{m\in\bar M}\frac{1}{|\bar C_m|}\sum_{c\in\bar C_m}y_{m,c}.
```

z는 유지한다.

```math
z_{\mathrm{new}}=z_{\mathrm{old}}.
```

따라서 hand translation 전체를 RL이 직접 회귀하는 것이 아니다.

**Position correction은 tactile geometry를 이용한 rule-based planning이다.**

Appendix A.1.1에서는 저자들이 초기에는 wrist repositioning 자체를 학습하려 했지만, tactile center로 이동하는 간단한 planning이 경험적으로 더 잘 동작했다고 설명한다.

## 13. Wrist Orientation Adjustment

Reopen 시 wrist roll angle은 policy가 continuous하게 출력한다.

```math
a_t^{\mathrm{wrist\ rotation}}\in[-\pi,\pi].
```

Policy는 learned Gaussian에서 sample하고 $\pi$를 곱한다.

```math
a_t^{\mathrm{wrist\ rotation}}\sim\mathcal{N}(\tanh(f_{\mathrm{wrist\ rotation}}(s_t)),\sigma_{\mathrm{rotation}})\times\pi.
```

$\sigma_{\mathrm{rotation}}$도 학습된다.

### 13.1. 왜 pitch/yaw는 바꾸지 않는가

저자들은 두 이유를 든다.

1. Sparse tactile만으로 target object pose를 정확히 알기 어려움
2. Clutter에서 pitch/yaw를 바꾸면 finger 일부가 아래쪽으로 움직여 collision과 손상 위험이 커짐

따라서 MAT는 orientation correction을 wrist roll로 제한한다.

Appendix에서는 이를 “4-DOF as opposed to 6-DOF grasp pose adjustments”라고 표현한다. 다만 실제 position update 식에서는 z를 유지하고 x/y만 바꾸며, orientation은 roll만 학습하므로 본문 구현 설명과 “4-DOF” 용어 사이에는 해석상 주의가 필요하다.

## 14. Lift Action과 종료

Policy는 lift 여부도 binary로 선택한다.

```math
a_t^{\mathrm{lift}}\in\{0,1\}.
```

```math
a_t^{\mathrm{lift}}\sim\mathrm{Bernoulli}(\mathrm{sigmoid}(f_{\mathrm{lift}}(s_t))).
```

Lift가 선택되면 arm을 **25 cm 수직 상승**시키고 episode를 종료한다.

Reopen과 lift가 동시에 true이면 **reopen이 우선**한다.

Finite horizon의 마지막 timestep에 도달하면 policy 결정과 무관하게 자동으로 lift한다.

## 15. Reward Structure

Reward는 매우 sparse하다.

### 15.1. Terminal reward

Lift가 수행된 마지막 timestep에서 object pick-up 성공이면 1, 실패면 0이다.

```math
r_{t_{\mathrm{final}}}=\mathbf{1}\{\mathrm{pick\text{-}up\ is\ successful}\}.
```

### 15.2. Reopen penalty

Terminal 이전에는 기본적으로 reward가 0이다.

다만 충분히 finger를 닫아 보지도 않고 너무 일찍 reopen하는 행동을 억제하기 위해 penalty를 둔다.

```math
r_t=-0.05\,a_t^{\mathrm{reopen}}\left(1-\mathbf{1}\left\{\max_{i\in\mathrm{grip\ joints}}[s_t^{\mathrm{joint\ angles}}]_i>0.2\ \mathrm{rad}\right\}\right).
```

즉 reopen 자체가 항상 -0.05가 아니라, max grip joint angle이 0.2 rad를 넘기 전에 reopen할 때 penalty가 적용된다.

## 16. Soft Proximal Policy Optimization

MAT는 clipped PPO에 maximum-entropy term을 추가한 **Soft Proximal Policy Optimization**을 사용한다.

### 16.1. Policy objective

원문 식 (1)은 다음 형태로 시작한다.

```math
\max_\theta L^{\mathrm{SP}}=\mathbb{E}_{\rho_0,\pi_\theta}[\pi_\theta(a_t|s_t)Q^{\pi_\theta}(s_t,a_t)].
```

Advantage estimator를 사용하면 식 (2)는 다음과 같다.

```math
\max_\theta L^{\mathrm{PG}}=\mathbb{E}_{\rho_0,\pi_\theta}[\pi_\theta(a_t|s_t)\hat A_t].
```

### 16.2. Baseline / value network

State-value baseline $V_\psi$는 variance reduction에 사용한다.

```math
\min_\psi L^{\mathrm{BL}}=\mathbb{E}\left[\|V_\psi-V^{\pi_\theta}\|^2\right].
```

### 16.3. Clipped surrogate + soft advantage

원문 식 (4)은 다음과 같다.

```math
\max_\theta L^{\mathrm{PG}}=\mathbb{E}_{\rho_0,\pi_\theta}\left[\min(\lambda_t(\theta),\mathrm{clip}(\lambda_t(\theta),1-\epsilon,1+\epsilon))(\hat A_t-\alpha\log\pi_\theta(a_t|s_t))\right].
```

여기서

```math
\lambda_t(\theta)=\frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{\mathrm{old}}}(a_t|s_t)}.
```

즉 PPO clipping과 entropy/maximum-entropy 성격의 $\alpha\log\pi$ 항을 함께 사용한다.

## 17. Hierarchical Action Probability의 주의점

Reopen이 false일 때만 lift를 고려하고, reopen과 lift가 모두 false일 때 finger action을 고려한다.

원문 식 (5)은 이 hierarchical action flow를 log probability에 반영한다.

```math
\log\pi_\theta(a_t|s_t)=\left[\log\pi_\theta(a_t^{\mathrm{reopen}}|s_t)+(1-a_t^{\mathrm{reopen}})\log\pi_\theta(a_t^{\mathrm{lift}}|s_t)+(1-a_t^{\mathrm{reopen}})(1-a_t^{\mathrm{lift}})\sum_{i=1}^{n}\log\pi_\theta(a_t^{\mathrm{finger}i}|s_t)\right]\mathbf{1}\{t_{\mathrm{final}}<H\}.
```

**원문 식 (5)에는 reopen 시 함께 sample되는 continuous wrist rotation probability가 명시적으로 포함되어 있지 않다.**

앞 절에서는 wrist rotation이 learned Gaussian action이라고 분명히 설명하므로, 제공된 원문만으로는 식 (5)와 continuous rotation action의 policy-gradient log-probability 연결을 완전히 복원할 수 없다. 이 점은 저자가 Limitation으로 지적한 내용이 아니라 **원문 수식 표기의 미명시/주의사항**이다.

## 18. Policy Network Architecture

Fig. 4에서는 여섯 observation component를 각각 별도 network branch로 처리한다.

- binary tactile history
- binary tactile delta
- joint-angle history
- joint delta
- tactile xyz history
- tactile xyz delta

각 branch에서 feature를 추출하고 tanh로 범위를 제한한 뒤 embedding을 concatenate한다.

이 latent embedding이 shared fully connected layers로 전달되어 finger close, reopen, lift, wrist rotation 관련 output을 생성한다.

Appendix Table 5의 hyperparameter는 다음과 같다.

### 18.1. Baseline network

- hidden layers: 3
- hidden dimension: 128
- base learning rate: $1\times10^{-4}$
- minibatch size: 200

### 18.2. Subpolicy network

- hidden layers: 3
- hidden dimension: 128
- base learning rate: $1\times10^{-4}$
- minibatch size: 350

### 18.3. Optimization

- actors: 10
- episodes per batch / actor: 30
- horizon: 250
- epochs per batch: 10
- discount $\gamma$: 0.999
- temperature $\alpha$: $5\times10^{-4}$
- GAE $\lambda$: 0.95
- PPO clipping $\epsilon$: 0.2
- gradient clipping: 200
- value-function coefficient $c_1$: 1.0
- optimizer: Adam

## 19. Finger-Motion Curriculum

Finger action increment $\delta_{\mathrm{finger\ angle}}$가 작으면 fine control이 가능하지만 terminal lift reward가 너무 sparse해져 초기 학습이 어렵다.

저자들은 Barrett Hand에서 $\delta_{\mathrm{finger\ angle}}<0.4$ rad이면 학습이 경험적으로 어려워졌다고 설명한다.

반대로 큰 increment는 open-loop에 가까워 fine correction이 어렵다.

따라서 처음에는

```math
\delta_{\mathrm{finger\ angle}}=0.4\ \mathrm{rad}
```

에서 시작한다.

이후 최고 success rate에 따라 다음 식으로 줄인다.

```math
\delta_{\mathrm{finger\ angle}}=0.1+(0.4-0.1)(1-\mathrm{current\ max\ success\ rate}).
```

성공률이 높아질수록 0.1 rad에 가까운 작은 finger increment를 사용하게 된다.

이 curriculum의 목적은 초기에는 짧은 horizon으로 reward를 쉽게 얻고, 학습이 진행되면 더 세밀한 closed-loop finger control로 이동하는 것이다.

## 20. Simulation Training Setup

MAT는 **전부 simulation에서 학습**한다.

- simulator: PyBullet
- single-object scene와 cluttered scene을 50:50 확률로 sampling
- single-object: 1 object
- simulated clutter: 2–30 objects
- real-world clutter evaluation: 10 objects per scene 구성
- seen training objects: YCB + KIT에서 200개 이상
- novel simulation objects: BigBIRD에서 100개 이상
- simulation experiment당 500 grasp attempts

Initial grasp pose는 vision grasp planner의 pose를 바탕으로 사용하며, calibration noise를 추가한 robustness 실험도 수행한다.

## 21. Real-World Evaluation Setup

실물에서는 15 seen objects와 15 novel objects를 사용한다.

Single-object evaluation은 object당 10 trials를 수행한다.

Cluttered evaluation에서도 seen/novel scene을 구성하며 Appendix Fig. 11은 각 범주의 실제 scene별 pick-up 수를 제시한다.

실물 policy는 simulation 학습 후 **추가 learning 없이 직접 transfer**한다.

## 22. Main Result — Vision Open-loop Baseline 대비

Table 1의 grasp success rate는 다음과 같다.

| 조건 | MAT | Open-loop vision baseline |
| --- | ---: | ---: |
| Simulation · Single · Seen | 98.2 ± 2.1% | 93.8 ± 2.6% |
| Simulation · Single · Novel | 97.4 ± 1.6% | 94.9 ± 1.4% |
| Simulation · Clutter · Seen | 97.7 ± 2.9% | 92.5 ± 1.8% |
| Simulation · Clutter · Novel | 95.9 ± 3.9% | 91.1 ± 3.7% |
| Real · Single · Seen | 98.7 ± 3.5% | 96.7 ± 6.2% |
| Real · Single · Novel | 98.0 ± 4.1% | 93.3 ± 8.1% |
| Real · Clutter · Seen | 96.4 ± 4.6% | 92.9 ± 5.8% |
| Real · Clutter · Novel | 95.8 ± 4.7% | 91.9 ± 6.7% |

저자들은 simulation에서 네 조건 모두 baseline보다 유의하게 개선되었다고 설명한다.

Real에서는 평균 성공률도 높지만 sample 수가 작아 standard deviation이 커 통계적 구분이 simulation보다 약하다고 Appendix A.3에서 설명한다.

## 23. 저자들의 “Statistical Significance” 정의에 대한 주의

Appendix A.2에서 저자들은 두 결과의 mean 차이가 **적어도 한쪽 결과의 standard deviation 이상**이면 statistically significant하다고 간주한다.

예를 들어 98.2 ± 2.1과 93.8 ± 2.6의 차이 4.4가 두 표준편차보다 크므로 significant하다고 설명한다.

이는 원문에서 사용하는 자체 판정 규칙이다. 제공 원문에는 p-value, confidence interval 기반 hypothesis test, t-test 등의 일반적인 통계 검정 절차가 제시되지 않는다.

따라서 문서에서는 저자들의 표현을 보존하되, 이를 별도의 정식 유의성 검정 결과로 확대하지 않는다.

## 24. Calibration Noise Robustness

MAT의 핵심 실험 중 하나는 initial vision grasp pose에 position calibration noise를 넣는 것이다.

### 24.1. Simulation

X-Y plane random direction으로 noise를 넣는다.

| Noise | MAT Single Seen | MAT Single Novel | MAT Clutter Seen | MAT Clutter Novel |
| --- | ---: | ---: | ---: | ---: |
| 2.5 cm | 92.5 ± 8.1 | 93.3 ± 7.2 | 94.6 ± 5.8 | 93.7 ± 4.2 |
| 5.0 cm | 91.4 ± 11.0 | 92.5 ± 10.2 | 93.3 ± 7.8 | 92.7 ± 8.0 |
| 7.5 cm | 82.5 ± 9.5 | 80.8 ± 12.3 | 85.4 ± 9.5 | 81.3 ± 9.0 |

Open-loop vision baseline은 같은 noise 증가에 따라 크게 저하된다.

7.5 cm에서 baseline은 각각 18.8%, 10.4%, 12.5%, 4.2%까지 떨어진다.

### 24.2. Real robot

Real robot에서는 novel-object initial grasp에 **5 cm Y-axis calibration noise**를 넣는다.

| 조건 | MAT | Vision baseline |
| --- | ---: | ---: |
| Single object | 92.5 ± 10.4% | 20.0 ± 15.1% |
| Cluttered scene | 92.4 ± 5.9% | 25.6 ± 19.2% |

저자들은 static calibration error가 반복 open-loop retry로 사라지지 않으므로 baseline에서 object/scene당 3회 연속 실패하면 run을 종료한다.

## 25. Calibration Noise가 대표하는 더 넓은 실패 유형

Appendix A.5는 calibration noise 실험이 단순 camera calibration 하나만을 의미하지 않는다고 설명한다.

비슷한 symptom을 만드는 예로 다음을 든다.

- learned/planned grasp pose 자체의 suboptimality
- monocular camera에서 partial 3D point cloud
- object pose estimation error
- transparent / reflective object perception difficulty
- low-fidelity sim-to-real transfer
- 예상치 못한 object pose disturbance

즉 initial grasp pose가 현실에서 어긋나는 다양한 원인에 대한 proxy 실험으로 calibration offset을 사용한다.

## 26. Tactile Baseline

Appendix A.4에서는 [38]의 non-compliant version을 tactile baseline으로 재구현한다.

Baseline 동작은 다음과 같다.

1. 각 finger가 initial contact를 감지하면 해당 finger를 멈춤
2. 모든 finger가 contact하면 전체 finger를 함께 닫음
3. 일정 시간이 지나면 lift

MAT와 달리 adaptive regrasp·wrist repositioning·granular per-finger policy가 없다.

### 26.1. 0 cm calibration noise

| 조건 | MAT | Tactile baseline |
| --- | ---: | ---: |
| Single Seen | 98.2 | 94.4 |
| Single Novel | 97.4 | 95.0 |
| Clutter Seen | 97.7 | 93.3 |
| Clutter Novel | 95.9 | 91.3 |

### 26.2. 2.5 cm calibration noise

| 조건 | MAT | Tactile baseline |
| --- | ---: | ---: |
| Single Seen | 92.5 | 64.1 |
| Single Novel | 93.3 | 68.2 |
| Clutter Seen | 94.6 | 66.1 |
| Clutter Novel | 93.7 | 66.8 |

초기 grasp가 정확할 때도 MAT가 높지만, calibration error가 있을 때 차이가 훨씬 커진다.

## 27. Component Ablation

Appendix A.4.3은 MAT의 주요 기능을 제거한 ablation을 수행한다.

### 27.1. 0 cm noise

| Variant | Single Seen | Single Novel | Clutter Seen | Clutter Novel |
| --- | ---: | ---: | ---: | ---: |
| Full MAT | 98.2 | 97.4 | 97.7 | 95.9 |
| Finger-Closing Only | 96.6 | 96.2 | 95.3 | 94.7 |
| Regrasping Only | 96.2 | 96.0 | 94.4 | 93.5 |
| Position Adjustment Only | 96.9 | 96.4 | 96.2 | 94.8 |
| Orientation Adjustment Only | 96.7 | 96.4 | 95.7 | 94.8 |

Initial pose가 정확하면 모든 variant도 비교적 높은 성능을 유지한다.

### 27.2. 2.5 cm noise

| Variant | Single Seen | Single Novel | Clutter Seen | Clutter Novel |
| --- | ---: | ---: | ---: | ---: |
| Full MAT | 92.5 | 93.3 | 94.6 | 93.7 |
| Finger-Closing Only | 75.2 | 73.1 | 73.6 | 73.9 |
| Regrasping Only | 75.9 | 78.5 | 76.0 | 74.4 |
| Position Adjustment Only | 76.9 | 78.5 | 80.4 | 75.8 |
| Orientation Adjustment Only | 81.2 | 81.6 | 83.1 | 77.8 |

Calibration noise가 존재하면 full closed-loop combination의 이점이 크게 나타난다.

저자들은 각 제거 variant의 성능 감소량도 별도로 계산하여 보고한다.

## 28. Collision Safety와 Action 제한

### 28.1. Collision detection

Appendix A.1.3에서 다음 조건으로 collision을 감지한다.

- Barrett Hand lateral spread가 의도하지 않게 변함
- tactile cell 또는 finger가 unusually significant force를 경험

Collision이 감지되면 finger-reopen / pose-adjustment 단계에서 end-effector를 **0.1 cm씩 위로 이동**시켜 collision에서 벗어나게 한다.

이 protection mechanism은 finger closing과 lift 단계에서는 비활성화된다.

### 28.2. Side grasp

Initial side grasp처럼 palm 방향이 수평에 가까운 경우에는 horizontal position adjustment가 hand damage 위험을 높일 수 있어 **position adjustment를 비활성화하고 orientation adjustment만 허용**한다.

따라서 MAT의 action availability는 grasp configuration과 safety condition에 따라 제한된다.

## 29. Sim-to-Real을 위해 학습하지 않기로 선택한 것

Appendix A.1은 MAT가 무엇을 학습하지 않았는지도 중요하게 설명한다.

### 29.1. Wrist translation

Sparse tactile center를 이용한 deterministic relocation이 learned wrist translation보다 경험적으로 더 잘 동작하여 planning을 사용한다.

### 29.2. Continuous finger motor control

Continuous motor control은 simulation-real dynamics gap이 컸다고 설명한다.

따라서 discrete finger increment를 사용하고 curriculum으로 increment를 줄여 continuous-like fine control에 접근한다.

### 29.3. Full 6-DoF reorientation

Sparse tactile로 object pose를 알기 어렵고 clutter collision 위험이 커 pitch/yaw adjustment를 제거한다.

즉 MAT의 sim-to-real 성능은 단순히 “simulation이 정확했다”기보다, **sim-real 차이가 작은 observation과 action을 의도적으로 선택한 설계 결과**로 보는 것이 정확하다.

## 30. 이 논문에서 Binary Tactile이 실제로 남기는 정보

Binary threshold는 force magnitude를 제거하지만 다음 정보는 유지한다.

- 어느 tactile cell이 닿았는가
- finger/palm 중 어느 영역이 닿았는가
- contact가 최근 20 steps 동안 얼마나 지속되었는가
- contact가 새로 생겼는가 / 사라졌는가
- active tactile cell이 end-effector frame에서 어디에 위치하는가
- 그 위치가 시간에 따라 어떻게 변했는가

따라서 MAT는 “96-bit 현재 contact만 사용”하는 방식이 아니다.

**Binary contact + dense spatial indexing + kinematic contact position + temporal history + proprioception**의 조합이다.

## 31. Force / F/T 사용 여부

MAT는 wrist 6-axis F/T sensor를 사용하지 않는다.

Tactile cell의 raw force-like magnitude는 binary contact를 만들기 전 preprocessing에만 사용한다.

Policy 실행 입력에는 global force, torque, wrench가 없다.

Appendix A.4.1에서 저자들은 related tactile methods 일부가 force-torque sensor나 compliance를 요구하는 것과 MAT를 구분하며, MAT를 multi-fingered·F/T-free·non-compliant tactile method로 설명한다.

## 32. Training-only / Privileged Information

MAT actor에 current object GT pose나 geometry가 들어간다는 설명은 없다.

Simulation reward에서 pick-up 성공 여부는 environment state로 판정해야 하지만, 이것은 runtime actor observation과 구분된다.

| 구분 | 정보 |
| --- | --- |
| Actor execution | binary tactile history, tactile xyz history, finger joint history |
| Initial condition | 외부 vision planner의 6-DoF grasp pose |
| Reward | lift 후 pick-up success, early reopen penalty |
| Curriculum | current maximum success rate로 finger increment 조절 |
| Evaluation | actual pick-up result로 success 측정 |

Asymmetric critic에 object GT를 제공했다는 설명은 없다.

## 33. Limitation — 저자들이 직접 밝힌 제약

원문에는 독립된 Limitations 절이 없다. 저자들이 직접 설명한 적용 범위와 제약은 다음과 같다.

| 제약 | 내용 | 원문 위치 |
| --- | --- | --- |
| Sparse tactile의 object-pose ambiguity | tactile contact location은 object 위치 단서를 주지만 object pose를 충분히 알려주지 못함 | Appendix A.1.3 |
| Pitch/yaw adjustment 안전 문제 | clutter에서 pitch/yaw 변화가 finger collision과 hand damage를 만들 수 있어 roll만 조절 | Appendix A.1.3 |
| Continuous motor sim-to-real gap | continuous finger control은 dynamics gap이 커 discrete increment를 채택 | Appendix A.1.2 |
| Real-world 통계 분산 | 실물 object/scene 수가 simulation보다 적어 standard deviation이 높고 통계적 구분이 약함 | Appendix A.3 |
| Coarse initial grasp dependency | MAT는 외부 grasp planner가 initial grasp pose를 제공하는 구조 | §1, §4 |
| Position correction의 configuration restriction | initial side grasp에서는 safety 때문에 horizontal position adjustment를 비활성화 | Appendix A.15 |

마지막 두 항목은 저자들이 직접 “limitation”이라는 제목으로 쓰지는 않았지만 방법의 명시적 전제·제한으로 기술한 내용이다.

## 34. Future Work — 저자들이 제시한 향후 연구

Conclusion에서 저자들이 명시한 Future Work는 간결하다.

**MAT를 grasping에서 더 일반적인 dexterous tactile-based object manipulation으로 확장하는 것**이다.

다음 항목은 원문 Future Work로 명시되지 않는다.

- wrist F/T 추가
- tactile force magnitude를 policy에 직접 입력
- recurrent neural network 추가
- online vision fusion
- full 6-DoF regrasp
- real-world fine-tuning

이들을 저자 계획으로 임의 추가하지 않는다.

## 35. 미명시 사항과 원문 해석 주의점

### 35.1. Binary tactile sensor 값의 물리 단위

Raw tactile output range 0–20은 제시하지만 unit이 없다. Threshold 0.8을 N 단위 contact threshold로 기록하지 않는다.

### 35.2. Real tactile의 effort 보정

실물 tactile threshold 입력에는 proprioceptive effort가 더해진다. 따라서 “raw tactile 0.8 threshold만으로 binary를 만든다”라고 요약하면 불완전하다.

### 35.3. 20-step history의 실제 시간 길이

Tactile hardware는 246 Hz지만 policy timestep rate가 tactile stream rate와 동일하다고 명시되지 않는다. 따라서 20 steps를 20/246초로 직접 환산하지 않는다.

### 35.4. Action log-probability와 wrist rotation

식 (5)에 continuous wrist rotation probability가 나타나지 않는다. 실제 optimization 구현에서 이를 어떻게 포함했는지는 제공 원문만으로 확정할 수 없다.

### 35.5. “4-DOF adjustment” 용어

Appendix는 4-DOF grasp pose adjustment라고 표현하지만 position update 식은 x/y만 변경하고 z를 유지하며 orientation은 roll만 학습한다. 이 용어가 정확히 어떤 DOF count를 지칭하는지 원문 설명만으로 완전히 해소되지 않는다.

### 35.6. Statistical significance

저자들이 사용하는 mean-difference-vs-standard-deviation criterion을 일반적인 hypothesis test로 바꾸어 서술하지 않는다.

### 35.7. Tactile magnitude의 필요성

MAT는 binary tactile을 사용하지만 continuous force magnitude와 binary representation을 직접 비교하는 ablation은 없다. 따라서 이 논문만으로 “binary가 continuous보다 우수하다”고 결론 내릴 수 없다.

## 36. 원문 위치 안내

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 연구 동기·기여 | Abstract, §1, PDF pp. 1–2 |
| Related Works | §2, PDF pp. 2–3 |
| POMDP/MDP formulation, hardware | §3, PDF pp. 3–4 |
| 96 tactile cells·joint range | §3, PDF p. 4 |
| Observation | §4.1, PDF pp. 4–5 |
| Action | §4.2, PDF p. 5 |
| Reward | §4.3, PDF p. 5 |
| Soft PPO | §4.4, Fig. 4, PDF pp. 5–7 |
| Curriculum | §4.5, PDF p. 7 |
| Main experiments | §5, Table 1, PDF pp. 7–8 |
| Calibration noise | §5.2, Fig. 5–6, PDF p. 8 |
| Future Work | §6, PDF p. 8 |
| Design rationale | Appendix A.1, PDF p. 11 |
| Statistical rule | Appendix A.2–A.3, PDF pp. 11–12 |
| Tactile baseline/ablation | Appendix A.4, Table 2, PDF pp. 12–13 |
| Noise 의미 | Appendix A.5, PDF p. 13 |
| Simulation noise results | Appendix A.6, Table 3, PDF pp. 13–14 |
| Real noise results | Appendix A.7, Table 4, PDF p. 14 |
| Real objects/scenes | Appendix A.8–A.12, PDF pp. 14–18 |
| SoftPPO hyperparameters | Appendix A.10, Table 5, PDF p. 16 |
| Binary tactile preprocessing | Appendix A.13, PDF p. 19 |
| Reopen position adjustment | Appendix A.14, 식 (6)–(9), PDF p. 19 |
| Side-grasp safety | Appendix A.15, PDF pp. 19–20 |

## 37. 문서 검증 범위

사용자 제공 arXiv v2 PDF 20쪽 전체를 읽고 본문과 Appendix A.1–A.15를 확인했다. Fig. 4, Table 1–5, calibration-noise 실험, tactile preprocessing, position-adjustment 식을 대조했다.

코드 실행, PyBullet training 재현, 실제 Staubli/Barrett 실험 재현, 저자 영상 확인은 수행하지 않았다. PDF와 페이지 이미지는 저장소에 복제하지 않으며 arXiv 식별자와 SHA-256으로 원문을 식별한다.
