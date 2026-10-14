# Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [B007 Review 분석](../review_dataset/260918/batch_001/papers/2020-beltran-hernandez-learning-force-control.md) · [CHECK-A01 목록](../reviews/2026-09-20_separate-review-paper-list.md)

## 1. 논문 정보와 확인 범위

- **제목:** Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots
- **저자:** Cristian Camilo Beltran-Hernandez, Damien Petit, Ixchel Georgina Ramirez-Alpizar, Takayuki Nishi, Shinichi Kikuchi, Takamitsu Matsubara, Kensuke Harada
- **게재:** IEEE Robotics and Automation Letters, Vol. 5, No. 4, pp. 5709–5716, October 2020
- **DOI:** [10.1109/LRA.2020.3010739](https://doi.org/10.1109/LRA.2020.3010739)
- **확인 원문:** 사용자 제공 IEEE 출판본 PDF 8쪽 전체
- **파일 SHA-256:** b8338cd208ea74e5afc83a9159b391ef5dae2d4d61694ea452996ca9eae5d802
- **2026-09-21 재검증:** 이번에 다시 제공된 IEEE PDF의 SHA-256이 기존 정독 원문과 동일함을 확인했다. 따라서 별도 중복 노트를 만들지 않고 이 문서를 canonical 상세 노트로 유지하며, observation·controller action space·fail-safe·reward·실물 insertion 결과·Limitation/Future Work를 원문 8쪽 기준으로 재확인했다.
- **Supplementary material:** IEEE Xplore에 저자 제공 보충자료가 있다고 원문에 명시되지만 이번 정독에서는 확인하지 않음
- **코드:** 원문은 SAC 구현으로 TF2RL을 사용했다고 밝히지만, 논문 전용 공개 코드는 이번 정독에서 확인하지 않음

이 논문은 **torque-controlled compliant robot이 아니라 rigid position-controlled industrial robot에서 contact-rich task를 RL로 학습**하는 방법을 다룬다. 핵심은 RL이 force controller를 대체하는 것이 아니라, **전통적인 force-control 구조를 유지하면서 motion trajectory와 controller gain을 동시에 조절**하도록 하는 것이다. [원문 Abstract, §I, §III]

실험은 Gazebo simulation과 실제 UR3 e-series에서 수행하며, 실물 단계에서도 policy를 직접 학습한다. 따라서 이 논문은 simulation에서 학습한 policy를 그대로 실물로 이전하는 sim-to-real 연구가 아니다.

## 2. 저자들이 제시하는 문제

저자들은 실제 산업용 robot에 RL을 적용할 때 rigid position control이 contact-rich task에서 특히 문제가 된다고 본다.

Position controller는 contact-free motion에서는 유용하지만, 환경과의 접촉을 disturbance로 취급하여 목표 pose를 계속 추종하려고 하므로 contact force가 커질 수 있다. 반면 force control은 접촉 interaction을 다룰 수 있지만 controller gain을 task와 환경에 맞게 tuning해야 한다.

기존 variable impedance RL 연구의 상당수는 joint torque control 또는 flexible joint를 가정한다. 저자들의 직접적인 질문은 다음과 같다.

> **Low-level torque access가 없는 position-controlled industrial robot에서도, RL이 motion trajectory와 force-controller parameter를 함께 학습하여 contact-rich assembly를 수행할 수 있는가?**

또 하나의 문제는 real-robot RL exploration이다. Random exploration 중 IK 불능 command, 과도한 joint velocity, 큰 contact force가 발생하면 hardware 또는 환경이 손상될 수 있고 사람이 반복적으로 emergency stop을 복구해야 한다. 이를 줄이기 위해 별도 fail-safe layer를 제안한다.

## 3. 논문의 세 가지 주요 기여

원문 §I에서 저자들은 다음 세 기여를 제시한다.

1. **RL + conventional force control framework**
   - Position-controlled robot에서 low-level force-control policy를 학습
   - Modified parallel position/force control과 admittance control 두 구조 구현

2. **Action-space empirical study**
   - RL이 조절하는 controller parameter 개수를 달리하여 learning performance 비교

3. **Fail-safe mechanism**
   - Real rigid manipulator에서 random exploration을 수행할 때 IK, joint velocity, force limit을 검사하여 사람 개입을 줄임

## 4. Related Work의 비교 구도

### 4.1. Conventional Force Control

Force control은 환경과의 interaction을 feedback으로 제어할 수 있지만 stiffness 등 parameter를 접촉 조건에 맞게 정해야 한다.

기존 접근은

- variable gain scheduling
- adaptive gain control
- demonstration으로 gain 학습

등을 사용한다.

본 논문은 predefined scheduling 대신 **interaction experience를 이용해 time-varying force-control gain을 RL로 선택**한다.

### 4.2. RL + Variable Impedance / Force Control

선행 연구에는 PI2, DDPG, VICES 등으로 impedance parameter를 학습하는 방법이 있지만 대부분 joint torque control access를 전제로 한다.

저자들은 industrial position-controlled manipulator에서도 사용할 수 있도록 **task-space force/admittance controller가 position command를 생성하고, 최종 joint command는 IK와 robot position controller가 실행**하는 구조를 사용한다.

### 4.3. Real-Robot Learning

기존 대규모 실물 RL은 grasp posture 같은 high-level output을 학습하고 low-level controller를 별도로 사용한 경우가 많다.

본 논문은 contact-rich task에서 RL이 **직접 low-level motion correction과 compliant-control gain까지 선택**한다는 차이를 강조한다.

## 5. 전체 시스템 구조

Fig. 1의 핵심 흐름은 다음과 같다.

1. Task가 목표 EEF pose $x_g$를 제공
2. 현재 EEF pose $x$로부터 pose error $x_e=x_g-x$ 계산
3. F/T sensor에서 interaction load $F_{\mathrm{ext}}$ 측정
4. EEF velocity $\dot{x}$ 측정
5. SAC policy가
   - motion correction $a_x$
   - force-controller parameter $a_p$
   를 출력
6. Conventional force controller가 $x_e$, $F_{\mathrm{ext}}$, $a_x$, $a_p$를 이용해 commanded pose $x_c$ 생성
7. IK solver가 $x_c$를 joint command $q_c$로 변환
8. Fail-safe layer가 command를 검사
9. Position-controlled robot에 $q_c$ 전달

Policy와 force controller의 주기는 다르다.

- **Policy:** 20 Hz
- **Force controller / robot control:** 최대 500 Hz

즉 RL이 20 Hz에서 매 low-level cycle의 torque를 직접 생성하는 구조가 아니다.

## 6. Policy Observation

Policy observation은 Algorithm 1과 §III-B에서 다음과 같이 정의된다.

```math
o=[x_e,\dot{x},F_{\mathrm{ext}}].
```

여기서

```math
x_e=x_g-x.
```

Observation의 세 요소는 다음 역할을 가진다.

| Observation | 의미 |
| --- | --- |
| $x_e$ | Known goal EEF pose에 대한 현재 EEF pose error |
| $\dot{x}$ | 현재 EEF velocity |
| $F_{\mathrm{ext}}$ | F/T sensor 기반 interaction feedback |

F/T signal에는 **simple low-pass filter**를 적용한다.

그러나 원문은 다음을 명시하지 않는다.

- cutoff frequency
- filter order
- gravity compensation
- payload compensation
- sensor bias/zeroing
- 각 force/torque component의 normalization
- F/T sensor의 제조사·모델

따라서 이를 임의로 보완하지 않는다.

## 7. Object Information의 범위

이 논문은 current object pose를 policy에 주지 않는다.

| 정보 | Policy 입력 여부 | 비고 |
| --- | --- | --- |
| Current object position | No | Known EEF goal과 구분 |
| Current object orientation | No | EEF quaternion과 구분 |
| Object mesh / geometry | No | 환경 geometry를 알고 있다고 가정하지 않음 |
| Object mass / friction | No | Actor 입력으로 사용하지 않음 |
| Goal EEF pose | Yes / given condition | Task마다 사전에 알려져 있다고 가정 |
| EEF pose error / velocity | Yes | Proprioceptive task-space information |
| F/T | Yes | Contact interaction feedback |

Fig. 2에서 저자들은 단순 P-controller가 goal을 향해 직선적으로 진행하면 환경 geometry를 모르기 때문에 표면을 관통하려는 command가 될 수 있다고 설명한다. RL의 trajectory correction과 force feedback이 이 nominal motion을 수정한다.

## 8. Action Space의 기본 구조

Policy action은

```math
a=[a_x,a_p]
```

로 나뉜다.

### 8.1. Motion action $a_x$

```math
a_x=[p,\phi]
```

이며 3D position과 quaternion 기반 orientation에 대응하는 **6개의 position/orientation control components**를 사용한다.

모든 비교 model에서 $a_x$는 동일하게 6차원이다.

### 8.2. Controller parameter action $a_p$

$a_p$는 force-controller type에 따라 다르다.

- Parallel position/force control: position gain, force gain, selection matrix
- Admittance control: position gain, stiffness

RL이 controller structure 자체를 생성하는 것은 아니며, 미리 정의한 controller 안의 제한된 parameter를 선택한다.

## 9. EEF Pose 표현

EEF pose는

```math
x=[p,\phi]
```

로 정의한다.

- $p\in\mathbb{R}^3$: translation
- $\phi\in\mathbb{R}^4$: unit quaternion

Quaternion은 scalar part $\eta$와 vector part $\epsilon$으로 표현한다.

Controller가 계산한 commanded pose

```math
x_c=[p_t,\phi_t]
```

는 IK를 통해 desired joint configuration $q_c$로 변환된다.

원문은 IK solver의 구체적인 algorithm을 명시하지 않는다.

## 10. Parallel Position / Force Control

Parallel controller는

- position PD
- force PI
- direction별 selection matrix $S$
- RL motion action $a_x$

을 결합한다.

원문 식 (1)의 구조는 다음과 같다.

```math
u=S(K_p^x x_e+K_d^x\dot{x}_e)+a_x+(I-S)\left(K_p^fF_{\mathrm{ext}}+K_i^f\int F_{\mathrm{ext}}dt\right).
```

Selection matrix는

```math
S=\mathrm{diag}(s_1,\ldots,s_6),\qquad s_j\in[0,1].
```

각 $s_j$는 해당 direction에서 position controller와 force controller 중 어느 쪽의 영향이 큰지를 조절한다.

## 11. Parallel Controller의 Parameter Reduction

원래 parallel controller에는 총 30개의 parameter가 있다.

- Position PD gains: 12
- Force PI gains: 12
- Selection matrix: 6

하지만 RL action dimension이 커지면 학습이 어려워지고 unstable action 가능성이 증가하므로 controllable parameter 수를 줄인다.

Position derivative gain은 proportional gain으로부터 계산한다.

```math
K_d^x=2\sqrt{K_p^x}.
```

Force integral gain은 실험적으로 proportional gain의 1%로 설정한다.

```math
K_i^f=0.01K_p^f.
```

따라서 최대 설정에서 RL이 직접 선택하는 controller parameter는

```math
a_p=[K_p^x,K_p^f,S].
```

이다.

## 12. Controller Parameter의 Action Mapping

RL output은 normalized $[-1,1]$ 범위에서 생성된다.

각 controller parameter에는 baseline value $P_{\mathrm{base}}$와 range $P_{\mathrm{range}}$를 미리 정하여

```math
[P_{\mathrm{base}}-P_{\mathrm{range}},P_{\mathrm{base}}+P_{\mathrm{range}}]
```

사이로 mapping한다.

즉 RL이 gain을 완전히 unconstrained하게 만드는 것이 아니라 **사람이 정한 baseline과 search range 안에서 fine-tuning**한다.

이 $P_{\mathrm{base}}$와 $P_{\mathrm{range}}$ 선택은 후술하는 저자 명시 limitation과 직접 연결된다.

## 13. Admittance Control

Position-controlled robot에서 desired dynamic interaction을 만들기 위해 task-space admittance model을 사용한다.

원문 식 (2):

```math
F_{\mathrm{ext}}=m_d\ddot{x}+b_d\dot{x}+k_dx.
```

- $m_d$: desired inertia
- $b_d$: desired damping
- $k_d$: desired stiffness

Damping ratio와 natural frequency 관계는

```math
\zeta=\frac{b_d}{2\sqrt{k_dm_d}},\qquad\omega_n=\sqrt{\frac{k_d}{m_d}}.
```

로 정의한다.

Admittance controller 앞에는 nominal goal trajectory를 생성하는 position PD controller가 있고, RL motion action $a_x$도 함께 사용된다.

## 14. Admittance Parameter Reduction

Admittance structure도 원래 30개의 parameter를 가진다.

- Position PD gains: 12
- Inertia / damping / stiffness: 18

저자들은 다음과 같이 줄인다.

- Position derivative gain: proportional gain에서 계산
- Desired inertia: 각 direction에서 **0.1 kg·m²**로 고정한다고 원문에 표기
- Damping ratio $\zeta$: constant
- Damping은 stiffness와 inertia로부터 계산

```math
b_d=2\zeta\sqrt{k_dm_d}.
```

따라서 RL이 직접 조절하는 것은

```math
a_p=[K_p^x,k_d]
```

이다.

## 15. Action-Space Model 8개

Table I에서는 controller parameter를 몇 축별로 독립 조절할지에 따라 8개 policy를 비교한다.

| Controller | Model | Pose | PD | PI / Stiffness | Selection $S$ | 총 Action |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Parallel | P-9 | 6 | 1 | 1 | 1 | 9 |
| Parallel | P-14 | 6 | 1 | 1 | 6 | 14 |
| Parallel | P-19 | 6 | 6 | 6 | 1 | 19 |
| Parallel | P-24 | 6 | 6 | 6 | 6 | 24 |
| Admittance | A-8 | 6 | 1 | 1 | — | 8 |
| Admittance | A-13 | 6 | 1 | 6 | — | 13 |
| Admittance | A-13pd | 6 | 6 | 1 | — | 13 |
| Admittance | A-18 | 6 | 6 | 6 | — | 18 |

여기서 model 이름의 숫자는 총 action dimension과 일치한다.

이 비교의 목적은 **controller parameter를 많이 노출할수록 dexterity는 커지지만 RL learning complexity도 증가하는 trade-off**를 확인하는 것이다.

## 16. Soft Actor-Critic

RL algorithm은 TF2RL의 Soft Actor-Critic(SAC)을 사용한다.

SAC는

- off-policy actor–critic
- replay buffer 사용
- maximum-entropy objective

를 통해 sample efficiency와 exploration을 확보한다.

원문은 policy/critic network layer size, batch size, learning rate, replay-buffer size 등 전체 SAC hyperparameter를 표 형태로 제공하지 않는다.

## 17. Fail-Safe Mechanism

Algorithm 1은 policy command와 실제 robot actuation 사이에 별도의 safety layer를 둔다.

각 step에서 다음을 검사한다.

1. Desired EEF command $x_c$에 대해 IK solution $q_c$가 존재하는가?
2. 현재 joint configuration에서 $q_c$로 가는 데 필요한 joint velocity가 $\dot{q}_{\max}$를 넘지 않는가?
3. Contact load가 $F_{\max}$를 넘지 않는가?

IK가 없거나 joint velocity limit을 넘으면 **그 action을 실행하지 않고 현재 state에 머문다.**

Force limit을 넘으면 **episode를 즉시 종료**한다.

## 18. Proactive Safety와 Reactive Safety

저자들은 safety check를 명확히 두 종류로 구분한다.

### Proactive

- IK existence
- joint velocity limit

Robot을 실제로 움직이기 전에 unsafe command를 차단한다.

### Reactive

- contact force limit

Force limit violation은 이미 collision/contact overload가 발생한 뒤 측정되기 때문에 reactive하다.

따라서 논문의 fail-safe를 “collision을 발생 전에 모두 예방하는 guarantee”로 해석하면 안 된다.

## 19. Reward Function

모든 task에 같은 reward structure를 사용한다.

```math
r(s,a)=w_1L_m\left(\left\|x_e/x_{\max}\right\|_{1,2}\right)+w_2L_m\left(\left\|a/a_{\max}\right\|_2\right)+w_3L_m\left(\left\|F_{\mathrm{ext}}/F_{\max}\right\|_2\right)+w_4\rho+w_5\kappa.
```

$L_m$은 입력을 reward range로 선형 mapping한다.

Reward가 고려하는 요소는 다음과 같다.

- Goal pose error
- Action magnitude
- Contact load magnitude
- Step/time penalty $\rho$
- Terminal / safety outcome $\kappa$

Terminal term은

```math
\kappa=\begin{cases}200,&\text{task completed}\\-10,&\text{safety violation}\\0,&\text{otherwise}\end{cases}.
```

각 term weight $w_i$, $x_{\max}$, $a_{\max}$, $F_{\max}$의 실제 수치는 원문 본문에 명시되지 않는다.

## 20. F/T 정보가 사용되는 네 위치

이 논문에서 $F_{\mathrm{ext}}$는 단순 observation 하나가 아니라 여러 계층에서 사용된다.

| 위치 | 역할 |
| --- | --- |
| SAC policy observation | 접촉 상황에 따라 motion/gain을 선택 |
| Force controller | Parallel PI 또는 admittance response 계산 |
| Reward | 낮은 interaction load를 선호하도록 shaping |
| Fail-safe / termination | $F_{\max}$ 초과 시 collision으로 보고 episode 종료 |

따라서 “force가 actor에만 들어간다”는 요약은 불완전하다.

반대로 **F/T를 제거한 ablation은 없다.** 이 연구는 force sensing의 필요성 자체보다, force feedback을 가진 framework 안에서 action/controller representation을 비교한다.

## 21. Hardware와 Sensor

실험 장비는 다음과 같다.

- **Robot:** Universal Robot 3 e-series
- **Gripper:** Robotiq Hand-e
- **Force/Torque:** end-effector mounted F/T sensor
- **Robot control frequency:** up to 500 Hz
- **Policy frequency:** 20 Hz
- **Simulation:** Gazebo 9
- **Training PC:** Intel i9-9900K, NVIDIA RTX-2080 Super로 원문 표기

F/T sensor의 별도 제조사/모델, range, resolution, accuracy, raw sampling frequency는 원문에 명시되지 않는다.

## 22. Simulation Peg-Insertion Experiment

Action-space 비교는 동일 초기조건을 보장하기 위해 simulation에서 수행한다.

Task:

- Cube-shaped peg insertion
- Hole clearance: **1 mm**
- 각 policy: **50,000 steps**
- 최대 episode length: **150 steps**
- Policy: 20 Hz → 최대 약 **7.5 s**
- 각 model training: **3회 반복**
- 전체 training session: reset 포함 약 **50 min**

Episode는 다음 중 하나에서 종료된다.

1. 최대 timestep 도달
2. Target pose에 대한 minimum error 만족
3. Collision 발생

Minimum target-error threshold의 실제 수치는 원문에 명시되지 않는다.

## 23. Action-Space 비교 결과

Fig. 5의 learning curve에서 parallel-control family가 전체적으로 높은 reward를 보인다.

### Parallel

- **P-9:** controller parameter freedom이 부족해 일관된 good policy 학습이 어려움
- **P-24:** 충분히 학습할 수 있지만 learning이 느림
- **P-14:** 가장 빠른 learning과 높은 final performance

### Admittance

- **A-8:** parameter freedom 부족으로 성능이 낮음
- **A-13pd / A-18:** 높은 성능
- **A-13pd:** P-14와 비슷한 높은 final reward

저자들은 **P-14와 A-13pd가 complexity와 learnability 사이의 가장 좋은 trade-off**라고 결론낸다.

## 24. Selection Matrix의 영향

Parallel controller 계열은 learning-curve variance가 더 크다.

저자들은 selection matrix $S$의 작은 변화가 controller behavior를 크게 바꿀 수 있기 때문이라고 설명한다.

Random exploration 과정에서 $S$가 달라지면 position-force authority가 크게 바뀌므로, 서로 다른 training run 사이의 variance가 커진다.

## 25. Safety-Penalty Ablation

저자들은 fail-safe mechanism을 단순 mechanical protection으로만 사용하지 않고, **safety violation을 reward로 policy에 알려주는 효과**를 비교한다.

비교 조건:

- proposed reward: safety violation $\kappa=-10$
- ablation: safety violation penalty 제거

Penalty를 제거하면

- overall reward 감소
- learning speed 감소
- learning curve noise 증가
- collision 증가

가 나타난다.

A-13pd 예시에서 약 +100 reward에 도달하는 시점이

- penalty 있음: 약 12k steps
- penalty 없음: 약 20k steps

로 보고된다.

## 26. Collision Count 비교

Table II의 평균 collision count는 다음과 같다.

| Model | Safety penalty 있음 | 없음 |
| --- | ---: | ---: |
| A-8 | 326 | 455 |
| A-13 | 350 | 408 |
| A-13pd | 300 | 462 |
| A-18 | 451 | 457 |
| P-9 | 187 | 369 |
| P-14 | 121 | 206 |
| P-19 | 183 | 392 |
| P-24 | 219 | 337 |

모든 model에서 safety violation을 reward에 반영했을 때 collision 수가 줄었다.

이 비교는 **F/T observation 제거 실험이 아니라 동일 force-sensing framework에서 reward feedback의 효과**를 보는 실험이다.

## 27. Real Robot Task 1 — Ring Insertion

첫 번째 실물 task는 metallic ring을 bolt에 삽입하는 것이다.

- Clearance: **0.2 mm**
- 비교 policy: P-14, A-13pd
- Training: 각 **20,000 steps**
- 반복: 2회
- 최대 episode: **200 steps**, 약 10 s

두 model 모두 빠르게 successful policy를 학습한다.

Training session당 평균 collision:

- P-14: **45**
- A-13pd: **34**

Ring을 gripper로 단단히 잡았더라도 grasp 내부에서 ring position/orientation이 조금 바뀔 수 있으며, 저자들은 이것이 training performance drop의 한 원인이라고 설명한다.

## 28. Real Robot Task 2 — Peg Insertion

두 번째 실물 task는 metallic peg를 pulley에 삽입한다.

- Clearance: **0.05 mm**
- Pulley는 다른 robot arm이 유지
- Pulley center가 약간 flexible하여 contact stiffness가 ring task보다 낮음
- 그러나 clearance가 더 작아 misalignment 시 peg가 쉽게 stuck됨

두 policy 모두 약 **13k steps** 이후 successful policy를 찾는다.

Training session당 평균 collision:

- A-13pd: **4**
- P-14: **26**

A-13pd가 더 일관된 performance를 보인다.

## 29. Fig. 9 — 학습된 Contact-Dependent Gain 변화

Fig. 9는 A-13pd의 초기 policy와 학습 후 policy를 insertion direction 기준으로 비교한다.

Task는 세 phase로 나눈다.

1. **Contact 전 search**
2. **Initial contact 후 search**
3. **Insertion**

학습 후 policy에서는 첫 contact 이후

- stiffness $k_d$ 감소
- position proportional gain $K_p^x$ 감소

가 나타난다.

저자들은 이로 인해

- motion speed 감소
- manipulator stiffness 감소
- contact force 감소

가 발생한다고 설명한다.

Peg가 정렬되어 insertion phase로 들어가면 $k_d$와 $K_p^x$를 다시 높여 insertion friction을 이기고 task를 빠르게 완료한다.

이는 **force feedback에 따라 motion/compliance를 phase-dependent하게 조절하는 행동을 학습했다는 관찰**이다.

다만 F/T가 없는 동일 policy와의 비교가 아니므로 force sensing의 인과적 기여량을 정량화한 ablation은 아니다.

## 30. Policy / Controller / Safety의 역할 분리

이 논문을 이해할 때 세 계층을 구분해야 한다.

### Policy

20 Hz에서

- trajectory correction
- force-controller gain

을 선택한다.

### Force Controller

500 Hz에서

- pose error
- F/T
- policy parameter

를 이용해 compliant task-space command를 만든다.

### Safety Layer

실제 command 직전에

- IK feasibility
- joint velocity
- force limit

을 검사한다.

따라서 learned policy 하나가 control, compliance, safety를 전부 end-to-end로 대체한 구조가 아니다.

## 31. Training-only / Privileged Information 경계

| 구성 | 정보 |
| --- | --- |
| Actor | $x_e$, $\dot{x}$, filtered $F_{\mathrm{ext}}$ |
| Critic | 별도 observation contract 미명시 |
| Force controller | $x_e$, $F_{\mathrm{ext}}$, policy action/parameter |
| Reward | EEF goal error, action, F/T, time penalty, success/safety event |
| Safety | IK solution, estimated required joint velocity, F/T limit |
| Object GT pose | Actor input으로 명시되지 않음 |
| Environment geometry | 정확한 geometry knowledge를 policy/control 가정으로 두지 않음 |
| Known task information | Goal EEF pose $x_g$ |

Simulation에서 각 measured quantity가 Gazebo API의 어떤 GT channel에서 취득되는지는 본문에 상세히 명시되지 않는다.

## 32. 이 논문이 보여 주는 것과 보여 주지 않는 것

### 직접 보여 주는 것

- Position-controlled industrial robot에서 force-controller gain을 RL action에 포함할 수 있음
- Controller parameter dimension에 따라 learning speed/variance가 달라짐
- Safety violation penalty가 collision 수와 learning speed에 영향을 줌
- Real robot에서 0.2 mm / 0.05 mm clearance insertion을 실물 학습
- Contact phase에 따라 stiffness/gain을 변화시키는 policy behavior

### 직접 보여 주지 않는 것

- F/T 없는 policy와의 비교
- Tactile vs F/T 비교
- Wrench만으로 contact location이나 object pose를 추정하는 성능
- Multi-contact source disambiguation
- Force sensor noise/bias/drift robustness
- 다른 object family에 대한 generalization
- Simulation-trained policy의 zero-shot real transfer

## 33. Limitation — 저자들이 직접 밝힌 한계

§V에서 저자들은 두 가지를 명시한다.

### 33.1. Controller hyperparameter 의존성

성능이 controller gain의 baseline과 range,

- $P_{\mathrm{base}}$
- $P_{\mathrm{range}}$

선택에 크게 의존한다.

본 실험에서는 이를 경험적으로 정했다.

즉 “RL이 controller tuning을 완전히 자동화했다”는 표현은 과도하다. RL은 사람이 설정한 parameter search region 안에서 gain을 조절한다.

### 33.2. Goal EEF pose 사전 지식

각 task의 goal EEF pose를 알고 있다고 가정한다.

현재 방법은 target perception 또는 target localization을 해결하는 연구가 아니다.

## 34. Future Work — 저자들이 제시한 향후 연구

저자들은 limitation과 연결하여 다음 두 방향을 제안한다.

1. **Human demonstration에서 controller hyperparameter 획득**
   - Demonstration으로 baseline/range를 정하고
   - 이후 RL로 force-control parameter를 refine

2. **Vision으로 rough target pose 추정**
   - Known exact goal pose 가정을 완화
   - Vision에서 low-level force control까지 end-to-end learning으로 연결

두 방향 모두 본 논문에서 구현·검증한 결과가 아니라 향후 연구 제안이다.

## 35. 미명시 사항과 해석 주의점

### 35.1. F/T sensor 모델과 성능

원문은 UR3 e-series end-effector에 F/T sensor가 있다고만 쓰며 모델명, range, resolution, accuracy를 제공하지 않는다.

### 35.2. Low-pass filter

Simple low-pass filter를 사용한다고만 명시하며 cutoff와 filter order를 제공하지 않는다.

### 35.3. $F_{\mathrm{ext}}$의 세부 표현

F/T sensor와 6방향 force/position control을 사용하지만, observation vector의 축 순서·normalization·force와 moment 단위 세부를 표로 명시하지 않는다.

### 35.4. Critic 정보

SAC를 사용하지만 critic이 actor와 정확히 같은 observation을 받는지, 별도 privileged information이 있는지 본문에서 명시하지 않는다.

### 35.5. Success error threshold

Simulation episode가 minimum target-pose error에서 끝난다고 설명하지만 그 threshold 수치는 제공하지 않는다.

### 35.6. Safety는 완전한 사전 collision avoidance가 아니다

IK/joint velocity는 proactive check지만 force limit은 overload가 측정된 이후 episode를 끝내는 reactive mechanism이다.

### 35.7. 실물 training과 sim-to-real을 구분해야 한다

Real experiments는 P-14/A-13pd를 실물에서 20k steps씩 다시 학습한다. Simulation policy를 그대로 deployment한 zero-shot transfer가 아니다.

### 35.8. Force-sensing necessity ablation 없음

좋은 결과가 F/T를 활용하는 framework 안에서 나왔지만, F/T input 자체를 제거한 baseline은 없다.

## 36. 원문 위치 안내

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 연구 문제·기여 | Abstract, §I, PDF pp. 1–2 |
| Force control / RL 관련 연구 | §II, PDF p. 2 |
| SAC | §III-A, PDF p. 3 |
| 전체 control scheme | §III-B, Fig. 1–2, PDF p. 3 |
| Observation | §III-B, Algorithm 1, PDF pp. 3, 5 |
| Parallel controller | §III-C.1, 식 (1), Fig. 3, PDF pp. 3–4 |
| Admittance controller | §III-C.2, 식 (2)–(4), Fig. 4, PDF p. 4 |
| Fail-safe | §III-D, Algorithm 1, PDF pp. 4–5 |
| Reward | §III-E, 식 (5)–(6), PDF p. 5 |
| Action-space models | Table I, PDF p. 5 |
| Simulation setup/result | §IV-B, Fig. 5, PDF pp. 5–6 |
| Safety penalty ablation | §IV-C, Fig. 6, Table II, PDF pp. 6–7 |
| Ring / peg 실물 실험 | §IV-D, Fig. 7–9, PDF p. 7 |
| Learned gain response | Fig. 9, §IV-D.2, PDF p. 7 |
| Limitation / Future Work | §V, PDF p. 8 |

## 37. 문서 검증 범위

사용자 제공 IEEE 출판본 PDF 8쪽 전체를 확인했다. 특히 Fig. 1–4의 control architecture, Algorithm 1, Table I의 action-space 구성, 식 (1)–(6), Fig. 5–9와 Table II의 simulation/real-robot 결과를 원문 페이지 렌더링과 함께 대조했다.

Supplementary material, TF2RL 실행 설정, 실제 controller source code, sensor datasheet 및 robot 실험 재현은 수행하지 않았다. PDF는 저장소에 복제하지 않으며 DOI와 SHA-256으로 출처를 관리한다.
