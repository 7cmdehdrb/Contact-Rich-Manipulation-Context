# 1 kHz Behavior Tree for Self-adaptable Tactile Insertion

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [원래 ICRA 2024 선별 항목](../reviews/2026-09-19_icra-2024-contact-sensing-screening.md#icra24-wu-1khz-tactile-insertion)

## 1. 논문 정보와 확인 범위

- **제목:** 1 kHz Behavior Tree for Self-adaptable Tactile Insertion
- **저자:** Yansong Wu, Fan Wu, Lingyun Chen, Kejia Chen, Samuel Schneider, Lars Johannsmeier, Zhenshan Bing, Fares J. Abu-Dakka, Alois Knoll, Sami Haddadin
- **게재:** 2024 IEEE International Conference on Robotics and Automation (ICRA 2024), Yokohama, Japan, May 13–17, 2024, pp. 16002–16008
- **DOI:** [10.1109/ICRA57147.2024.10610835](https://doi.org/10.1109/ICRA57147.2024.10610835)
- **확인 원문:** 사용자 제공 IEEE 출판본 PDF 7쪽 전체
- **파일 SHA-256:** 85c3686c951e9b7508c0e2fd3a897d1d3b4a9e3c0c2ddce49101a550c659298e
- **확인하지 않은 자료:** 저자 코드, supplementary material, 영상, 선행 연구 [8], [19]의 원문 구현 세부사항은 이번 정독에서 별도 검증하지 않음

이 논문은 기존의 **force-domain wiggle 기반 insertion skill**을 그대로 반복 실행하는 대신, 접촉 상태를 실시간으로 추정하여 **Wiggle과 Push primitive를 1 kHz Behavior Tree(BT)에서 전환**하도록 확장한다. 핵심은 새로운 end-to-end policy를 학습하는 것이 아니라, 기존의 adaptive impedance + feed-forward force primitive 위에 **상태 추정과 reactive primitive switching**을 얹어 불필요한 wiggle을 줄이고 stuck 상태에서 다시 wiggle로 복귀하도록 만든 것이다. [원문 §I–II, PDF pp. 1–4]

## 2. 초록 내용

삽입은 제조와 서비스 로봇에서 중요한 contact-rich skill이다. 저자들의 이전 연구는 force-domain wiggle motion을 기반으로 insertion skill을 구성했지만, 상호작용 중 접촉 상태가 바뀌어도 행동을 그 변화에 맞추어 조절하지 못한다는 한계가 있었다.

본 논문은 이를 해결하기 위해 **고주파 contact/tactile information으로 접촉 상태를 추정하고, 그 결과에 따라 behavior primitive를 전환하는 Behavior Tree 기반 skill formalism**을 제안한다. tight-clearance peg-in-hole 실험에서 기존 방법보다 실행 시간, robustness, 새로운 과업에 대한 adaptability가 개선되었다고 보고하며, zero-shot transfer와 fine-tuning에서도 transferability가 개선되었다고 설명한다. [원문 Abstract, PDF p. 1]

## 3. 제시하는 문제 상황

### 3.1. 기존 insertion 접근의 초점

저자들은 insertion 연구를 크게 다음과 같이 정리한다. [원문 §I, PDF pp. 1–2]

- End-to-end deep RL: force 또는 visuo-tactile sensing을 model input으로 사용하는 접근
- Imitation Learning / Learning from Demonstration
- Parameterized skill learning
- 산업 현장에서 널리 쓰이는 인간 설계 기반 force spiral search와 multi-phase primitive

저자들은 deep RL이 versatile skill을 학습하는 데 유망하지만, **sample efficiency, safety guarantee, interpretability**가 real-world deployment의 문제라고 본다. 반대로 force spiral search나 parameterized skill은 human knowledge를 이용하여 더 작은 parameter space에서 학습할 수 있다.

### 3.2. 저자들이 강조하는 미해결 문제

기존 연구는 hole을 찾는 과정에 집중하는 경우가 많지만, 저자들이 본 문제는 그 이후의 **실제 삽입 과정에서 physical interaction에 맞추어 행동을 바꾸는 능력**이다. 특히 tight-clearance assembly에서는 삽입 중 작은 misalignment가 stuck 상태를 만들 수 있고, 이미 정렬된 상태에서 계속 wiggle하면 오히려 삽입을 방해할 수 있다. [원문 §I, PDF p. 2]

저자들의 이전 방식은 사람의 wiggle motion을 feed-forward force로 모사했지만, 새로운 접촉 조건에서도 정해진 방식으로 wiggle을 지속한다. 사람은 필요한 순간에만 wiggle을 사용하고 정렬이 이루어지면 바로 push로 전환하는데, 이전 skill에는 이러한 실시간 self-adaptation이 없다.

따라서 이 논문의 직접적인 질문은 다음에 가깝다.

> **삽입 중 접촉 상태 변화를 실시간으로 판별하여, 이미 학습된/설계된 motion primitive 사이를 필요한 순간에 전환할 수 있는가?**

## 4. Related Works의 비교 구도

원문에는 독립된 Related Works 절이 없으며 Introduction에서 선행연구를 비교한다. [원문 §I, PDF pp. 1–2]

| 접근 | 원문에서의 위치 | 저자 관점의 특징 |
| --- | --- | --- |
| End-to-end deep RL | [5], [7], [16] 및 visuo-tactile [9], [15] | 높은 표현력과 generalization 가능성이 있으나 sample efficiency·safety·interpretability 문제가 남음 |
| Meta-RL | [14], [18], [20], [21] | transferable insertion skill에 유망하지만 실물 적용 부담이 큼 |
| Imitation Learning / LfD | [3], [4], [6], [17] | sample-efficient하며 산업 적용 가능성이 높음 |
| Parameterized skill learning | [8], [10] | 인간 지식을 primitive와 parameter space에 넣어 학습 차원을 줄임 |
| Force spiral / handcrafted assembly | [11]–[13], [22] | 실제 제조 현장에서 널리 쓰이며 정밀 조립에서 강한 성능을 보일 수 있음 |
| 저자들의 이전 wiggle skill | [8], [19] | Lissajous 형태의 feed-forward force로 search/alignment와 stuck recovery 수행. 단, contact state 변화에 따른 실시간 primitive 전환이 없음 |

본 논문은 이 가운데 **parameterized skill + human-designed reactive structure** 쪽에 위치한다. 즉, neural network가 raw tactile sequence에서 action을 직접 출력하는 구조가 아니라, 해석 가능한 contact state estimator와 BT를 통해 이미 정의된 primitive를 switching한다.

## 5. 실험 환경과 하드웨어

### 5.1. 로봇과 과업

실험은 **7-DoF Franka robot**으로 수행한다. 네 종류의 tight-clearance insertion object를 사용한다. [원문 Fig. 1, §III, PDF pp. 1, 4]

| Object | 형상·크기 | Clearance |
| --- | --- | --- |
| A | Cuboid, 35 mm × 25 mm × 60 mm | 각 dimension 0.1 mm |
| B | Cylinder, length 50 mm, diameter 40 mm | 0.05 mm |
| C | Cylinder, length 50 mm, diameter 30 mm | 0.025 mm |
| D | 37 mm long key | 원문 Fig. 1 caption에 clearance 수치 미명시 |

주요 실험은 (1) 동일 skill parameter에서 BT+state estimation이 없는 baseline과의 실행 성능 비교, (2) evolution strategy를 사용한 learning performance, (3) Object A에서 학습한 skill의 B/C/D transferability로 구성된다. [원문 §III, PDF pp. 4–6]

### 5.2. 센서와 “tactile” 용어의 주의점

논문은 제목과 본문에서 **tactile information / tactile skill**이라는 표현을 사용하지만, 제공된 7쪽 원문에는 DIGIT, GelSight, FSR, taxel array 같은 **별도 tactile sensor의 종류·배치·해상도**가 제시되지 않는다.

실제 contact-state estimator에 명시적으로 들어가는 신호는 다음이다. [원문 §II-C, 식 (7)–(9), PDF pp. 3–4]

- End-Effector의 insertion-axis 위치 $x_z$
- End-Effector의 insertion-axis 속도 $v$
- robot dynamics와 joint torque에서 얻는 robot force/torque 추정치
- joint torque 기반 external force estimate를 제거한 residual force $F_{res}$

특히 alignment 판정에는 residual force의 z 성분 $f_{res,z}$를 사용한다. 즉 이 논문에서 “tactile”은 **공간적으로 분포된 피부형 tactile sensing만을 뜻하는 표현으로 읽으면 안 된다.** 원문이 실제 online estimator에 제시하는 핵심 sensing은 robot state와 interaction force/wrench 계열이다.

또한 원문에는 force/torque sensor의 별도 모델명, 측정 range, resolution, sampling hardware 사양이 없다. 1 kHz는 **Behavior Tree tick frequency**로 명시되며, 이것을 별도 tactile sensor의 제조사 sampling rate로 바꾸어 기록하지 않는다.

## 6. 전체 Skill 구조

논문의 전체 흐름은 다음과 같다. [원문 Fig. 2, §II-B, PDF pp. 2–3]

1. **Approach:** initial position에서 hole 방향으로 이동한다.
2. **Contact:** 접촉을 형성한다.
3. **Contact state estimation:** 삽입 상태를 Searching / Stuck / Unstuck / Aligned 중 하나로 갱신한다.
4. **Wiggle 또는 Push 선택:** Aligned가 아니면 Wiggle, Aligned이면 Push를 실행한다.
5. **Reactive recovery:** Push 중 속도가 reference 이하로 떨어지면 다시 Stuck으로 판정되어 Wiggle로 복귀할 수 있다.
6. **Finish:** task completion condition이 만족되면 종료한다.

기존 방법은 Approach → Contact → Smart Wiggle을 sequential FSM으로 수행한다. 제안 방법은 depth 5의 Behavior Tree로 바꾸고, root를 **1 kHz**, 즉 매 1 ms마다 tick한다. tick은 depth-first search 방식으로 condition/action node를 순회하고, leaf node의 return status에 따라 action이 실행되거나 중단된다. [원문 §II-B, PDF pp. 2–3]

## 7. Adaptive Impedance Control + Feed-forward Force

### 7.1. 로봇 동역학

원문의 torque-controlled robot dynamics는 다음과 같다. [원문 식 (1), PDF p. 2]

$$
M(q)\ddot q+C(q,\dot q)\dot q+g(q)=\tau_m+\tau_{ext}.
$$

- $q\in\mathbb{R}^n$: joint position
- $M(q)$: mass matrix
- $C(q,\dot q)$: Coriolis matrix
- $g(q)$: gravity vector
- $\tau_m$: motor torque / control input
- $\tau_{ext}$: external torque

### 7.2. 공통 primitive 제어법

모든 motion primitive는 adaptive impedance control with feed-forward force를 사용한다. [원문 식 (2), PDF p. 2]

$$
\tau_m(t)=J(q)^T\left[F_{ff}(t)+K(t)e+D\dot e+M(q)\ddot x_d+C(q,\dot q)\dot x_d\right]+g(q).
$$

여기서 $e=x_d-x$, $\dot e=\dot x_d-\dot x$이며, $K(t)$와 $D$는 Cartesian stiffness와 damping이다. $F_{ff}(t)$가 feed-forward wrench 역할을 한다.

Pre-insertion의 Approach와 Contact에서는 $F_{ff}(t)=0$으로 desired trajectory를 따라간다. 접촉 이후 Wiggle과 Push는 동일한 control law를 사용하지만 $F_{ff}$의 생성 방식이 달라진다. [원문 §II-B, PDF p. 3]

## 8. Wiggle과 Push primitive

### 8.1. Wiggle

Wiggle은 저자들의 이전 연구 [8], [19]에서 사용한 **Lissajous curve-shaped feed-forward force**를 사용한다. 각 방향 $i$의 desired force는 다음과 같다. [원문 식 (3), PDF p. 3]

$$
F_{ff,i}(t)=a_i\sin(2\pi f_i t+\phi_i).
$$

$i$는 End-Effector frame의 $x,y,r_x,r_y,r_z$ 방향이고, $a_i$, $f_i$, $\phi_i$는 각각 amplitude, frequency, phase다. main insertion direction인 z축 force는 상수 $a_z$를 유지한다.

이 wiggle의 기능은 두 가지로 설명된다.

- hole을 search하고 peg를 alignment하는 것
- insertion 중 peg가 stuck된 상태에서 빠져나오도록 하는 것

### 8.2. Push

Aligned state가 검출되면 Wiggle을 중단하고 Push primitive를 실행한다. Push에서는 $F_{ff}(t)$를 **마지막으로 갱신된 값으로 유지**한다. 따라서 제안법의 핵심은 새로운 Push controller를 만드는 것이 아니라, **정렬된 순간을 찾아 wiggle을 멈추고 일정 feed-forward force 기반 push로 전환하는 것**이다. [원문 §II-B, PDF p. 3]

## 9. Real-time Contact State Estimation

Contact state estimator는 이 논문의 핵심 구성이다. 원문의 Algorithm 1과 §II-C를 기준으로 보면, 네 상태가 있다. [원문 Algorithm 1, §II-C, PDF pp. 3–4]

| 상태 | 원문 의미 |
| --- | --- |
| Searching | hole을 찾는 중 |
| Stuck | insertion object가 막혀 움직이지 못하는 상태 |
| Unstuck | object가 insertion direction으로 이동하는 상태 |
| Aligned | peg가 hole과 정렬되었다고 판단된 상태 |

### 9.1. High-frequency noise filtering

robot state time series $X$는 길이 $N=50$의 Blackman window로 convolution하여 filtering한다. [원문 식 (4)–(6), PDF p. 3]

$$
w[n]=0.42-0.5\cos\left(\frac{2\pi n}{N}\right)+0.08\cos\left(\frac{4\pi n}{N}\right).
$$

$$
\bar w[n]=\frac{w[n]}{\sum_{i=1}^{N}w[i]}.
$$

$$
\tilde X=X*\bar w.
$$

원문은 이 filtering을 high-frequency noise의 영향을 줄이기 위해 사용한다고 설명한다. 이후 Fig. 3에 제시된 측정값도 이 전처리를 거친 값이다.

### 9.2. Moving z-score로 Stuck → Unstuck 검출

Unstuck 검출은 End-Effector의 task-frame z-position $x_z$에 대해 moving z-score를 계산한다. [원문 식 (7), PDF p. 3]

$$
z=\frac{x_z-\mu}{\sigma}.
$$

$\mu$와 $\sigma$는 이전 관측으로 계산하고, 원문 footnote는 **직전 1초의 measurement를 reference**로 사용한다고 명시한다. 저자들은 새로운 sample의 z-score가 3을 넘으면 anomaly로 판단한다.

물체가 stuck되어 있을 때 z-position은 거의 수평으로 유지되지만, hole을 찾아 unstuck되면 insertion direction으로 빠르게 이동한다. 따라서 $z>3$을 stuck 상태가 풀리는 turning point의 검출에 사용한다. [원문 §II-C.2, PDF pp. 3–4]

### 9.3. Residual force로 Aligned 검출

robot이 object에 가하는 force/torque는 joint torque와 robot dynamics를 이용해 다음과 같이 추정한다. [원문 식 (8), PDF p. 4]

$$
[F_r^T,\tau_r^T]^T=J_{body}^{-T}\left(\tau_m-C(q,\dot q)\dot q-g(q)\right).
$$

그다음 joint torque 기반 external force estimate $F_{ext}$를 빼 residual force를 만든다. [원문 식 (9), PDF p. 4]

$$
F_{res}=F_r-F_{ext}.
$$

저자들의 논리는 다음과 같다.

- clearance 때문에 misaligned 상태에서도 pressing force가 있으면 insertion direction으로 일부 이동할 수 있다.
- wiggle을 반복하면 더 잘 정렬된 pose로 접근한다.
- 더 잘 정렬되면 같은 조건에서 저항이 작아져 insertion direction의 net force가 커진다.
- 따라서 $f_{res,z}$의 **local maximum**을 alignment moment로 본다.

Aligned가 검출되면 그때의 z-direction velocity에 discount factor $\alpha=0.1$을 곱해 reference speed를 만든다.

$$
v_{ref}=\alpha v,\qquad \alpha=0.1.
$$

그 뒤 object velocity가 $v_{ref}$ 아래로 떨어지면 다시 Stuck으로 판정한다. 즉, Push로 전환한 뒤에도 다시 막히면 BT가 Wiggle로 복귀할 수 있다. [원문 §II-C.3, Algorithm 1, PDF pp. 3–4]

### 9.4. Algorithm 1의 상태 전환을 순서대로 풀어 쓰면

원문 pseudo-code는 다음과 같이 해석할 수 있다.

1. 초기 상태는 Searching이고 현재 $x_z$를 $x_{z0}$로 기록한다.
2. Searching 중 $x_z-x_{z0}>\epsilon$이 되면 Searching이 성공한 것으로 보고 Stuck으로 상태를 바꾼다.
3. Stuck에서 moving z-score가 3보다 커지면 Unstuck으로 바꾼다.
4. Unstuck 이후 $f_{res,z}$가 local maximum이면 Aligned로 바꾸고 $v_{ref}=\alpha v$를 기록한다.
5. Stuck이 아닌 상태에서 velocity가 $v_{ref}$보다 작아지면 다시 Stuck으로 바꾼다.
6. BT는 Aligned condition이 true이면 Push, false이면 Wiggle을 실행한다.

여기서 $\epsilon$의 실제 수치, local maximum 판정 window와 prominence, velocity의 정확한 계산 방식은 제공된 원문에 명시되지 않는다.

## 10. Behavior Tree의 역할

BT 자체가 contact state를 학습하는 것은 아니다. contact state estimator가 condition을 제공하고 BT는 그 결과를 **1 ms마다 재평가하여 action node를 enable/abort**한다. [원문 §II-B–C, Fig. 2]

이 구조의 의미는 다음과 같다.

- FSM처럼 한 번 다음 phase로 넘어가면 고정되는 것이 아니라 현재 상태를 계속 재검사한다.
- Aligned가 검출되면 즉시 Wiggle을 멈추고 Push로 전환할 수 있다.
- Push 중 다시 stuck되면 Wiggle을 재개할 수 있다.
- primitive 자체는 해석 가능한 impedance + feed-forward force controller로 유지된다.

따라서 논문의 “self-adaptable”은 **continuous action을 end-to-end로 매 step 재생성하는 적응**이라기보다, 물리 상태 추정에 따라 **기존 primitive의 사용 시점과 switching을 reactive하게 바꾸는 적응**에 가깝다.

## 11. Evolution Strategy 기반 Skill Parameter Learning

### 11.1. 무엇을 학습하는가

논문은 BT switching과 별도로 기존 skill의 parameter를 evolution strategy로 학습한다. 학습 대상은 neural policy의 weight가 아니라 **stiffness, force amplitude/frequency/phase 등 skill parameter vector $\xi$**다. [원문 §II-D, Table I, PDF p. 4]

$K$개의 rollout을 위해 parameter perturbation을 multivariate Gaussian에서 샘플링한다.

$$
\tilde\xi_k\sim\mathcal N(\xi,\Sigma_\epsilon),\qquad k=1,2,\ldots,K.
$$

box constraint를 적용한다. [원문 식 (10)]

$$
\xi_k=\min(\max(\tilde\xi_k,\xi_{min}),\xi_{max}).
$$

### 11.2. Cost function

각 rollout의 성능은 다음 cost로 평가한다. [원문 식 (11), PDF p. 4]

$$
J=\frac{t_{exe}}{t_{max}}+\Phi e^d.
$$

- $t_{exe}$: execution time
- $t_{max}$: time limit
- $\Phi$: insertion 성공이면 0, 실패면 1
- $d$: End-Effector와 insertion hole 사이 average distance

성공하면 두 번째 항이 0이므로 실행 시간이 주요 cost가 되고, 실패하면 hole에서 멀수록 더 큰 penalty를 받는다.

### 11.3. PIBB 기반 update

원문은 [29]의 PIBB algorithm을 이용해 parameter distribution을 갱신한다. 먼저 cost를 min-max normalization한다. [원문 식 (12)]

$$
\tilde J_k=\frac{J_k-\min(\{J_k\})}{\max(\{J_k\})-\min(\{J_k\})}.
$$

normalized cost에 따라 rollout weight를 계산한다. [원문 식 (13)]

$$
P_k=\frac{\exp(-c\tilde J_k)}{\sum_{i=1}^{K}\exp(-c\tilde J_i)}.
$$

parameter center와 covariance는 weighted average로 갱신한다. [원문 식 (14)–(16)]

$$
\xi\leftarrow\sum_{k=1}^{K}P_k\xi_k.
$$

$$
\Sigma_\epsilon^{temp}=\sum_{k=1}^{K}P_k(\xi_k-\xi)(\xi_k-\xi)^T.
$$

$$
\Sigma_\epsilon\leftarrow\Sigma_\epsilon+\gamma(\Sigma_\epsilon^{temp}-\Sigma_\epsilon).
$$

원문은 $c=10$, $\gamma=0.9$를 사용한다. 따라서 이 논문의 “learning performance”는 **BT를 학습하는 것이 아니라, BT가 포함된 skill framework의 parameter optimization이 얼마나 빠르고 안정적으로 진행되는지**를 비교하는 실험이다.

## 12. Table I의 예시 Skill Parameter

Skill performance 비교에 사용한 Object A parameter는 다음과 같다. [원문 Table I, PDF p. 4]

| Parameter | Value |
| --- | --- |
| $K_{xyz}$ | 523.907 N/m |
| $K_r$ | 24.984 N/rad |
| $[a_x,a_y,a_z]$ | [1.792, 2.360, 4.931] N |
| $[a_{rx},a_{ry},a_{rz}]$ | [0.766, 0.906, 3.228] N/rad로 표기 |
| $[\phi_x,\phi_y]$ | [-0.078, 0.776] |
| $[\phi_{rx},\phi_{ry},\phi_{rz}]$ | [-1.562, 0.610, -0.119] |
| $[f_x,f_y]$ | [2.179, 1.561] |
| $[f_{rx},f_{ry},f_{rz}]$ | [0.718, 0.720, 0.143] |

회전 방향 amplitude의 단위가 Table I에서 N/rad로 적혀 있으나, 이것을 torque amplitude의 일반적인 SI unit으로 임의 수정하지 않고 원문 표기를 그대로 기록한다.

## 13. 실험 결과

### 13.1. Skill performance: 동일 parameter에서 BT의 효과

Object A에서 baseline으로 성공했던 parameter distribution을 바탕으로 Gaussian sampling한 서로 다른 parameter를 사용하여 **100회** 실행한다. [원문 §III-A, PDF pp. 4–5]

- Proposed method success rate: **30%**
- Baseline success rate: **21%**
- 완료된 trial 기준 전체 execution time: **8.9% 감소**

Fig. 3의 대표 실행에서는 T1에서 Stuck → Unstuck이 검출되고, T2에서 $f_{res,z}$ local maximum으로 Aligned가 검출된다. Proposed method는 이 시점에 wiggle을 멈추고 Push로 전환하여 T3에서 완료하지만, baseline은 이미 얻은 alignment 이후에도 wiggle을 계속하여 정렬된 위치를 놓치고 실행 시간이 길어진다. [원문 Fig. 3, §III-A, PDF pp. 5–6]

이 비교는 **동일한 primitive parameter에서 switching logic의 차이**를 보여 주는 실험이라는 점이 중요하다.

### 13.2. Learning performance

Object A와 C에서 evolution strategy 학습을 각각 **10회 반복**한다. 전체 cost curve에서는 proposed method가 더 낮은 cost와 variance를 보이지만, Pre-Insertion은 두 방법이 동일하고 차이는 Insertion phase에서만 발생한다. [원문 §III-B, Fig. 4, PDF pp. 5–6]

저자들은 Insertion phase의 평균 execution speed가 다음과 같이 개선되었다고 보고한다.

- Object A: **52.9% improvement**
- Object C: **45.6% improvement**

Fig. 4(b), (d)에 표시된 최종 결과 수치는 다음과 같다.

| Object | 지표 | Baseline | Proposed |
| --- | --- | ---: | ---: |
| A | External force | 6.2 N | 5.91 N |
| A | External torque | 0.77 Nm | 0.64 Nm |
| A | Time | 2.94 s | 1.92 s |
| C | External force | 4.17 N | 4.38 N |
| C | External torque | 0.55 Nm | 0.55 Nm |
| C | Time | 1.15 s | 0.79 s |

따라서 proposed method가 항상 force magnitude 자체를 감소시켰다고 일반화하면 안 된다. Object C의 표시값에서는 external force가 오히려 약간 높고 torque는 동일하다. 원문의 핵심 주장은 **contact force를 과도하게 키우지 않으면서 execution speed를 개선**했다는 것이다.

### 13.3. Zero-shot transfer

Object A에서 학습한 optimal parameter policy를 B, C, D에 그대로 적용하고 각 object에 대해 **100회** 실행한다. [원문 §III-C.1, Fig. 5, PDF p. 6]

| Transfer target | Baseline success | Proposed success |
| --- | ---: | ---: |
| Object B | 49% | 62% |
| Object C | 38% | 48% |
| Object D | 36% | 41% |

저자들은 세 object를 종합하여 success rate가 **22.7% 향상**되었다고 보고한다. 이 수치는 percentage point 증가가 아니라 저자들이 계산한 overall enhancement 표현이다.

### 13.4. Fine-tuning transfer

Object A skill을 pretrained model로 두고 B/C/D에 fine-tuning한다. [원문 §III-C.2, Fig. 6, PDF p. 6]

- Object B: baseline보다 **33.3% faster convergence**, performance variance **49.4% 감소**
- Object C: 학습 전반에서 baseline보다 낮은 cost를 보였다고 서술
- Object D: baseline보다 **1.7 times quicker convergence**, outcome variance **66.2% 감소**

Fig. 6 fine-tuning experiment는 각 조건을 **5회** 반복하고 solid line은 mean, shaded area는 variance를 나타낸다.

## 14. 이 논문에서 “학습”과 “실시간 적응”을 구분해야 하는 이유

논문에는 서로 다른 두 시간척도의 adaptation이 섞여 있다.

### Offline / episodic parameter learning

Evolution strategy + PIBB가 여러 rollout의 cost를 사용하여 $\xi$와 $\Sigma_\epsilon$을 갱신한다. 이는 stiffness, wiggle force profile 등의 **skill parameter 학습**이다.

### Online / 1 kHz reactive adaptation

실행 중에는 moving z-score, residual force local maximum, velocity threshold로 contact state를 갱신하고 BT가 Wiggle/Push를 전환한다. 이것은 **학습된 neural policy의 online update가 아니라 rule-based state estimation + reactive switching**이다.

따라서 “1 kHz로 학습한다”, “1 kHz RL policy가 tactile input을 받아 action을 출력한다”, “BT가 end-to-end로 학습된다”는 식으로 요약하면 원문과 다르다.

## 15. 이 논문에서 확인되는 sensing → state → action 연결

이 논문의 contact information은 다음과 같이 행동으로 연결된다.

| 입력 / 파생값 | 전처리·판정 | 추정 상태 | 행동 영향 |
| --- | --- | --- | --- |
| EE z-position $x_z$ | Blackman filtering + moving z-score | Stuck → Unstuck | hole을 찾은 뒤 insertion이 진행되기 시작했음을 검출 |
| Residual force $f_{res,z}$ | local maximum 검출 | Unstuck → Aligned | Wiggle 중단, Push로 전환 |
| z-direction velocity $v$ | $v<v_{ref}$ | non-Stuck → Stuck | Push 중 다시 막히면 Wiggle로 복귀 |
| BT condition | 1 kHz tick | Aligned true/false | Push / Wiggle primitive 선택 |

즉, raw force를 action amplitude에 직접 비례시켜 연속적으로 바꾸는 force controller가 아니라, **filtered motion/force에서 discrete contact state를 추출한 뒤 primitive switching에 사용**한다.

## 16. Limitation — 저자들이 직접 밝힌 제약

원문에는 독립된 Limitations 절이 없다. Conclusion에서도 명시적인 한계 목록을 제시하지 않는다. 아래는 저자들이 본문에서 문제 범위 또는 실험 범위로 직접 설명한 내용만 분리한 것이다.

| 저자 서술에서 확인되는 범위 제약 | 내용 | 원문 위치 |
| --- | --- | --- |
| tight-clearance insertion 중심 | 연구 문제와 실험은 peg-in-hole 및 key insertion 계열의 tight-clearance assembly에 집중 | §I, §III, Fig. 1 |
| contact state estimator가 task-specific signal에 의존 | Unstuck은 insertion-axis z-position anomaly, Aligned는 z residual force local maximum, re-stuck은 z velocity 기준으로 판정 | §II-C, Algorithm 1 |
| baseline과 동일한 Pre-Insertion | 학습 성능 차이는 Insertion phase에서 발생하며 Pre-Insertion은 두 방법이 동일 | §III-B |
| transfer 평가 object 수가 제한됨 | Object A에서 학습 후 B/C/D 세 object에 대해 zero-shot/fine-tuning 평가 | §III-C |

위 항목 중 일부는 “저자들이 실패 원인으로 명시한 limitation”이 아니라 **원문이 정의한 적용·평가 범위**다. 이를 저자들이 방법의 약점이라고 직접 인정했다고 확대 해석하지 않는다.

## 17. Future Work — 저자들이 제시한 향후 연구

Conclusion에서 저자들은 향후 **더 넓은 범위의 object를 포함하는 skill transfer learning에 대해 extensive empirical research를 수행하겠다**고 명시한다. [원문 §IV Conclusion, PDF p. 6]

그 외에 다음을 Future Work로 명시하지는 않는다.

- 별도 tactile array 추가
- end-to-end RL로 BT 대체
- vision integration
- contact-state estimator의 neuralization
- insertion 이외 sweeping/pushing으로 확장

이러한 방향을 저자들의 계획으로 임의 추가하지 않는다.

## 18. 미명시 사항과 원문 해석 주의점

### 18.1. 별도 tactile sensor 사양이 없다

제공된 원문에는 별도 tactile sensor 모델, taxel 수, spatial resolution, force range, threshold, calibration이 없다. 따라서 제목의 “Tactile Insertion”을 **distributed tactile skin 기반 방법**으로 분류하면 안 된다. 실제 online state estimation은 EE motion과 force/wrench 추정에 기반한다.

### 18.2. 1 kHz의 대상

1 kHz는 BT root tick frequency로 명시된다. Blackman filtering과 contact state estimation이 동일하게 hardware sensor에서 정확히 1 kHz로 acquisition되었다는 독립적 sensor specification은 제공되지 않는다.

### 18.3. 일부 detector parameter가 빠져 있다

다음 값은 원문만으로 재현하기 어렵다.

- Searching → Stuck의 $\epsilon$
- $f_{res,z}$ local maximum 판정 window/조건
- velocity 계산·filter의 구체 구현
- Finish condition
- task timeout $t_{max}$의 실제 값
- $K$ rollout 수
- parameter bounds $\xi_{min},\xi_{max}$
- 초기 covariance $\Sigma_\epsilon$

### 18.4. Force / external force / residual force 용어를 구분해야 한다

원문은 robot이 object에 가하는 $F_r$와 joint torque 기반 external force estimate $F_{ext}$를 구분하고, 둘의 차이를 $F_{res}$로 정의한다. alignment detector는 일반 raw contact force가 아니라 **$f_{res,z}$의 local maximum**을 사용한다.

### 18.5. Transferability의 의미

여기서 transferability는 Object A에서 얻은 **parameterized skill**을 다른 insertion geometry에 적용했을 때의 zero-shot success와 fine-tuning convergence에 관한 것이다. 범용 object manipulation policy나 unseen task family 전반에 대한 transfer를 검증한 것은 아니다.

## 19. 원문 위치 안내

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 연구 동기·기여 | Abstract, §I, PDF pp. 1–2 |
| 기존 RL/LfD/parameterized skill 비교 | §I, PDF pp. 1–2 |
| 실험 object 크기·clearance | Fig. 1 caption, PDF p. 1 |
| Adaptive impedance control | §II-A, 식 (1)–(2), PDF p. 2 |
| FSM → 1 kHz BT | Fig. 2, §II-B, PDF pp. 2–3 |
| Wiggle feed-forward force | 식 (3), §II-B, PDF p. 3 |
| Contact state algorithm | Algorithm 1, §II-C, PDF pp. 3–4 |
| Blackman filtering·moving z-score | 식 (4)–(7), PDF p. 3 |
| Residual force·Aligned 판정 | 식 (8)–(9), §II-C.3, PDF p. 4 |
| Evolution Strategy / PIBB | §II-D, 식 (10)–(16), PDF p. 4 |
| 예시 skill parameter | Table I, PDF p. 4 |
| 동일 parameter skill 성능 | §III-A, Fig. 3, PDF pp. 4–6 |
| Learning performance | §III-B, Fig. 4, PDF pp. 5–6 |
| Zero-shot transfer | §III-C.1, Fig. 5, PDF p. 6 |
| Fine-tuning | §III-C.2, Fig. 6, PDF p. 6 |
| Conclusion·Future Work | §IV, PDF p. 6 |

## 20. 문서 검증 범위

사용자 제공 IEEE 출판본 PDF 7쪽 전체를 텍스트와 페이지 렌더링으로 확인했다. Fig. 1–6, Algorithm 1, Table I, 식 (1)–(16)을 대조하여 정리했다.

코드 실행, robot experiment 재현, 선행 연구 [8], [19]의 parameter 의미 전체 검증은 수행하지 않았다. 원문 PDF와 페이지 이미지는 저장소에 복제하지 않으며 DOI와 파일 해시로 출처를 관리한다.
