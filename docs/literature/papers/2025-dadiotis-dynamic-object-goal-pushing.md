# Dynamic Object Goal Pushing with Mobile Manipulators Through Model-Free Constrained Reinforcement Learning — 원문 상세 정리

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 조사 · ICRA 2025 후보 선별](../reviews/2026-09-19_icra-2025-contact-sensing-screening.md#icra25-dadiotis-pushing)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Dynamic Object Goal Pushing with Mobile Manipulators Through Model-Free Constrained Reinforcement Learning** |
| 저자 | Ioannis Dadiotis, Mayank Mittal, Nikos Tsagarakis, Marco Hutter |
| 출판 | 2025 IEEE International Conference on Robotics and Automation (ICRA), Atlanta, USA, May 19–23, 2025, pp. 13363–13369 |
| DOI | [10.1109/ICRA55743.2025.11128166](https://doi.org/10.1109/ICRA55743.2025.11128166) |
| 원래 조사 | [ICRA 2025 후보 선별](../reviews/2026-09-19_icra-2025-contact-sensing-screening.md#icra25-dadiotis-pushing)의 후속 원문 정독 |
| 정리일 | 2026-09-19 |
| 확인한 원문 | 사용자 제공 IEEE 출판본 PDF 7쪽 전체. 본문 §I–V, Fig. 1–7, Table I–V, References [1]–[28] |
| 확인하지 않은 자료 | 보충 영상, 저자 코드·설정·체크포인트·원시 데이터, 인용된 선행논문의 개별 원문, arXiv 버전과 출판본 사이의 변경점, 장비 제조사 데이터시트 |
| 원문 PDF SHA-256 | 38a067e36aec3323d2e04d94bee7f202357963f46a7a4001b00f08bf5a0c3682 |

이 문서는 첨부 출판본 자체의 문제 정의, Related Work, 환경과 관측, constrained RL, reward와 constraint, domain randomization, simulation·hardware 결과, 저자 명시 Future Work를 정리한다. 다른 연구 주제에 대한 적용안은 포함하지 않는다. [원문 §I–V, PDF pp. 1–6 / 인쇄 pp. 13363–13368]

**핵심:** 제안 정책은 F/T나 tactile feedback을 사용하지 않는다. 배포 시에도 **현재 object pose를 외부 motion-capture system으로 계속 갱신**하며, actor는 이 object pose에서 계산한 EE–object·object–goal 관계, robot proprioception, 이전 action을 입력받는다. 반대로 object mass·dimensions·inertia·shape·velocity와 EE–object contact state는 actor에 주지 않고 **simulation critic의 privileged information**으로만 제공한다. 이 구조에서 정책은 contact를 끊고 다시 만드는 online contact switching, goal pose tracking, toppling 회피를 학습한다. [원문 §III-C·E, Table I, PDF pp. 3–4]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 정의, contact switching, 기여와 Related Work |
| 3 | mobile manipulator, locomotion policy, RL environment |
| 4 | actor/critic 관측과 privileged information |
| 5 | action space와 controller 연결 |
| 6 | reward, constraint, constrained PPO |
| 7 | domain randomization과 zero-shot deployment |
| 8–10 | simulation ablation, constraint satisfaction, hardware success |
| 11 | contact switching, reactive behavior, object-size adaptation |
| 12–14 | 저자 명시 Limitation·Future Work·미명시 사항 |
| 15–16 | 원문 위치 안내와 핵심 메커니즘 요약 |

## 1. 제시하는 문제 상황과 실제 과업

### 1.1 미지 물체를 목표 위치와 yaw로 이동시키는 mobile pushing

논문의 목표는 quadrupedal mobile manipulator가 **잡지 않고 밀어서** 미지 물체를 원하는 평면 위치와 yaw orientation으로 옮기는 것이다. 대상 물체는 실제 환경에서 mass, size, material, friction coefficient가 미지일 수 있으며, pushing 중 contact sliding이나 상대 회전이 발생할 수 있다. [원문 Abstract·§I, PDF p. 1]

저자들이 문제로 보는 핵심은 단순히 한 접촉점을 계속 유지하는 것이 아니다. 상대 운동 때문에 기존 접촉점이 더 이상 적절하지 않을 수 있으므로, robot은 contact를 끊고 다른 위치에서 다시 접촉해야 한다. 논문은 이 **동적으로 접촉 위치를 바꾸는 행동을 contact switching**이라고 정의한다. [원문 §I, PDF p. 1]

### 1.2 목표는 position뿐 아니라 yaw와 object balance를 포함한다

과업 성공 조건은 object frame과 goal frame의 위치 오차가 **10 cm 이하**, yaw orientation 오차가 **10 deg 이하**인 것이다. Object goal position은 반경 2 m의 영역에서, object·goal·robot base yaw는 전체 $[-\pi,\pi]$ 범위에서 무작위화한다. [원문 §III-B, Fig. 3, PDF p. 3]

얇은 물체나 높은 마찰 바닥에서는 잘못된 높이에서 밀면 toppling이 발생할 수 있으므로, 저자들은 **object balance를 별도 constraint**로 넣는다. 이 때문에 policy는 base의 높이·roll·pitch와 arm contact height를 함께 조절할 수 있다. [원문 §I, §III-D, Fig. 7, PDF pp. 1, 4, 6]

### 1.3 “unknown object”의 정확한 의미

Actor에는 object의 mass, dimensions, inertia, shape class, CoM 위치가 제공되지 않는다. 그러나 **현재 object pose는 계속 제공**된다. 배포 시에는 external motion-capture system으로 object와 robot base의 6D pose를 측정하여 actor observation을 계산한다. [원문 §III-C·E, Table I, PDF pp. 3–4]

따라서 이 연구에서 “unknown object”는 **object pose까지 알 수 없다는 뜻이 아니다.** 정확한 구분은 다음과 같다.

- Object pose: **Tracking**
- Object dimensions·shape: actor에는 **미제공**
- Mass·inertia·CoM: actor에는 **미제공**
- Object velocity: actor에는 **미제공**
- Contact state: actor에는 **미제공**
- 위 정보 중 상당수는 simulation critic에는 **privileged information으로 제공**

[원문 Table I, §III-C, PDF p. 3]

## 2. Related Work — 원문이 구성한 비교 구도

아래는 이 논문 §II가 선행연구를 설명하는 방식의 정리다. 인용된 선행논문의 원문을 이번 작업에서 별도로 재검증했다는 뜻은 아니다.

### 2.1 Model-based mobile manipulation

저자들은 trajectory optimization과 MPC가 dynamic mobile manipulator에 널리 쓰이지만, online contact switching을 위해서는 **동역학적으로 가능한 contact schedule을 미리 정해야 하고 환경·robot model에 의존**하는 문제가 있다고 설명한다. [원문 §II-A, PDF p. 2]

반대로 model-free RL은 simulation domain randomization으로 uncertainty에 강인한 controller를 학습할 수 있지만, 기존 mobile-manipulator RL 연구는 주로 free-space tracking과 lightweight grasping을 다루므로 heavy contact-rich pushing으로의 확장이 충분히 검증되지 않았다고 정리한다. [원문 §II-A, PDF p. 2]

### 2.2 Force·tactile 기반 static pushing과 contact switching의 차이

§II-B에서 저자들은 force-feedback 기반 pushing [3]과 tactile-feedback 기반 pushing [4]을 **static pushing** 계열로 묶는다. 저자들의 설명에 따르면 이 방식들은 contact가 끊기면 feedback signal도 사라지므로 online contact switching을 수행하지 않고, 목표 orientation보다는 goal position 이동을 다룬다. [원문 §II-B, PDF p. 2]

이 비교 구도는 본 논문의 관측 설계와 직접 연결된다. 제안 actor는 contact state를 센서로 관측하지 않지만 **contact가 끊어진 동안에도 object pose와 EE–object relative position을 계속 계산할 수 있으므로** 새 접촉점을 찾는 행동을 이어갈 수 있다. [원문 §III-C·E, Table I, PDF pp. 3–4]

### 2.3 기존 RL pushing과의 차이

저자들은 Ferrandis et al. [5]의 RL contact switching이 fixed-base manipulator와 작고 가벼운 물체에 제한되고, Jeon et al. [6]의 quadrupedal pushing은 base의 2D planar action을 사용하며 object toppling을 고려하지 않는다고 설명한다. 본 논문은 arm의 3D 접촉 위치와 6D base command를 함께 사용하여 object surface의 다양한 높이·면에서 상호작용하는 방향으로 확장한다. [원문 §I, §II-B, PDF pp. 1–2]

## 3. 환경·로봇·센서

### 3.1 Robot과 controller 계층

| 항목 | 원문 설정 |
| --- | --- |
| Mobile platform | ANYmal quadruped |
| Mounted arm | 6-DoF robotic arm. 제조사·모델명은 본문 미명시 |
| Push policy가 직접 제어하는 arm DOF | 첫 5개 joint. 6번째 joint는 gripper 사용 시 필요하다는 이유로 고정 |
| Base command | $v_x$, $v_y$, yaw rate $\omega_z$, roll $\zeta$, pitch $\theta$, base height $h$ |
| Locomotion controller | 사전 학습된 student locomotion policy. Push-policy 학습 중 frozen |
| Push policy 주기 | 50 Hz |
| Locomotion policy 주기 | 50 Hz |
| Arm 저수준 제어 | joint impedance controller |
| Gripper | 본 과업에서는 사용하지 않음 |

[원문 §III, §III-A, Fig. 2, PDF p. 2]

Push policy가 생성한 6D base command는 사전 학습 locomotion policy가 leg joint target으로 변환한다. Locomotion policy는 randomized arm motion으로 학습되어 arm configuration 변화에 강인하도록 설계되었으며, push-policy 학습 중에는 업데이트하지 않는다. [원문 §III-A, PDF p. 2]

### 3.2 실물에서 실제로 사용하는 sensing

제안 push policy에 **wrist F/T sensor나 tactile sensor는 없다.** 실물에서 필요한 주요 외부 정보는 object와 robot base의 6D pose이며, 이는 external motion-capture system으로 얻는다. [원문 §III-E, PDF p. 4]

Actor observation에는 arm joint position·velocity, base linear/angular velocity, projected gravity도 포함된다. 하지만 이 값들을 어떤 IMU·encoder·state estimator로 구성하는지, 센서 모델·주파수·정확도는 본문에 별도로 명시하지 않는다. 따라서 일반적인 ANYmal 사양으로 보완하지 않는다. [원문 Table I, PDF p. 3]

Simulation의 EE–object contact state $\lambda_e$는 **critic privileged input**이다. 이를 실물 tactile/contact sensor 측정으로 해석하면 안 된다. [원문 Table I, §III-C, PDF p. 3]

## 4. Actor Observation, Critic Privileged Information, Training-only State

### 4.1 Actor observation

Actor observation은 $\mathbf{o}_t\in\mathbb{R}^{54}$이다. Table I의 구성은 다음과 같다.

| 입력 | 차원 | actor noise |
| --- | ---: | --- |
| EE–object relative position, base frame | 3 | $\mathcal U(\pm0.02)$ |
| Object rotation matrix w.r.t. base | 9 | $\mathcal U(\pm0.01)$ |
| Arm joint position relative to default | 5 | $\mathcal U(\pm0.01)$ |
| Robot base linear velocity | 3 | $\mathcal U(\pm0.01)$ |
| Robot base angular velocity | 3 | $\mathcal U(\pm0.20)$ |
| Arm joint velocity | 5 | $\mathcal U(\pm0.50)$ |
| Projected gravity unit vector | 3 | $\mathcal U(\pm0.05)$ |
| Object–goal relative position w.r.t. base | 3 | $\mathcal U(\pm0.02)$ |
| Goal orientation w.r.t. object | 9 | $\mathcal U(\pm0.01)$ |
| Previous action $\mathbf a_{t-1}$ | 11 | noise 없음 |

[원문 Table I, §III-C, PDF p. 3]

여기서 “policy only observes the object pose”라는 원문 표현은 **전체 actor input이 object pose 하나라는 뜻이 아니다.** 정확히는 actor가 object에 대해 직접 받는 intrinsic information이 pose뿐이라는 뜻이다. Robot proprioception, goal-relative state, previous action도 actor에 들어간다. [원문 Abstract, §III-C, Table I, PDF pp. 1, 3]

### 4.2 Critic privileged information

Critic은 actor observation에 다음 privileged information $\mathbf{o}^{pr}_t$를 더 받아 총 $\mathbb{R}^{73}$ 입력을 사용한다.

| Privileged input | 차원 |
| --- | ---: |
| EE–object contact state $\lambda_e$ | 1 |
| Object CoM position w.r.t. robot base | 3 |
| Object mass | 1 |
| Object dimensions | 3 |
| Object principal moments of inertia | 3 |
| Object linear velocity w.r.t. robot | 3 |
| Object angular velocity w.r.t. robot | 3 |
| Object shape one-hot vector | 2 |

Critic은 actor와 달리 **noiseless observation**을 받는다. [원문 Table I, §III-C, PDF p. 3]

### 4.3 Reward도 actor보다 더 많은 정답 정보를 사용한다

Actor에 dimensions·velocity가 없더라도 training reward는 simulation의 정답 object state를 이용한다.

- Task reward $r_1$: object와 goal의 **oriented bounding box 8개 keypoint** 거리
- Reach reward $r_2$: object vertical surface에서 sampled reach target과 EE 거리
- Direction reward $r_3$: object linear velocity 방향과 object-goal 방향의 정렬
- Smoothness reward $r_4$: 연속 action 변화량

따라서 actor observation만 보고 “학습에도 object geometry나 velocity가 전혀 사용되지 않는다”고 정리하면 잘못이다. **Actor에는 숨기지만 critic과 reward에는 simulation GT geometry·dynamics가 사용된다.** [원문 §III-B–D, Table I–II, PDF pp. 3–4]

## 5. Action Space와 Contact Switching

### 5.1 Action

Push policy action은

$$
\mathbf a_t=
\left(
\Delta\mathbf u^{\mathrm{cmd}}_{\mathrm{base}},
\Delta\mathbf q^{\mathrm{cmd}}_j
\right)
\in\mathbb R^{11}
$$

이다.

Base command는 6차원이고 arm joint target은 첫 5개 joint에 대한 5차원이다. Action은 default base state와 default arm configuration에 대한 deviation으로 출력된 뒤 absolute command로 변환되어 locomotion policy와 joint impedance controller에 전달된다. [원문 §III·III-A·III-C, PDF pp. 2–3]

### 5.2 Contact switching은 별도 discrete action이 아니다

Actor action에는 “contact 유지 / contact 해제 / face switch” 같은 명시적 mode가 없다. 정책이 mobile base와 arm을 연속적으로 움직이면서 결과적으로 contact를 끊고, robot이 object 주위를 돌아 다른 면이나 높이에서 다시 접촉한다. [원문 §I, §III-C, Fig. 4, §IV-C, PDF pp. 1, 3, 5]

이때 actor는 contact state $\lambda_e$를 직접 보지 않는다. Contact가 끊겨도 object pose와 EE–object relative position은 계속 관측되므로, contact-only feedback 방식과 달리 observation 자체가 사라지지 않는다. [원문 §II-B, Table I, §III-E, PDF pp. 2–4]

## 6. RL Environment와 Constrained PPO

### 6.1 기본 학습 설정

| 항목 | 설정 |
| --- | --- |
| Simulator | NVIDIA Isaac Lab |
| Parallel environments | 4096 |
| Training iterations | 20000 |
| Base algorithm | PPO 구현 [25]에 CAT [7]의 constrained RL 변경 적용 |
| Episode timeout | 20 s |
| 조기 종료 | unrecoverable object fall 또는 robot fall |
| Object initial position | environment origin |
| Robot base initial position | object-centered annulus, radius 1.2–2.5 m |
| Goal position | object-centered circular area, radius 2 m |
| Object·goal·base yaw | 각각 $[-\pi,\pi]$ 전체 범위 random |
| Success | position error $\le 10$ cm, orientation error $\le 10$ deg |

[원문 §III-B, Fig. 3, PDF p. 3]

저자들은 “model-free”를 controller 구조에서 model과 derivative가 필요하지 않는다는 뜻으로 사용하며, simulation training에 model을 사용하는 것 자체는 허용한다고 각주에서 명시한다. [원문 §II-A 각주 1, PDF p. 2]

### 6.2 Surface reach target을 이용한 exploration shaping

각 reset마다 object의 vertical surface에서 reach target $\mathbf p_r$를 무작위로 샘플링하고, $r_2$로 EE를 그쪽으로 유도한다. 목적은 특정 centroid만 밀도록 고정하는 것이 아니라 **object surface의 여러 위치를 경험하게 하는 것**이다. [원문 §III-B·D, Fig. 3B, PDF pp. 3–4]

이 reach target은 actor observation으로 주어지는 task goal이 아니라 reward shaping용 training signal이다. 저자들은 정확히 그 sampled point를 맞히게 할 의도는 없으며, $r_2$ weight를 1500 iteration 뒤 1/4로 줄인다. [원문 §III-D, PDF p. 4]

## 7. Reward와 Constraint

### 7.1 Reward

Total reward는 네 항의 가중합이다.

$$
r^{mathrm{tot}}_t
=
\sum_{i=1}^{4} w_i r_{i,t}
$$

원문 weight는

$$
w_1=2.5,\quad
w_2=1.25,\quad
w_3=0.156,\quad
w_4=0.3
$$

이다. [원문 §III-D, Table II, PDF p. 4]

각 항의 의미는 다음과 같다.

- $r_1$: object와 goal의 8개 OBB keypoint 차이를 줄이는 main task reward
- $r_2$: EE와 sampled surface reach target 사이 거리 감소
- $r_3$: object linear velocity의 **방향**이 object-goal 방향과 맞도록 유도
- $r_4$: base·arm command의 step-to-step 변화량을 줄이는 action-rate regularization

$r_3$에는 object velocity magnitude를 직접 보상하지 않는다. 저자들은 이를 통해 robot이 object를 지나치게 공격적으로 밀지 않도록 한다고 설명한다. [원문 §III-D, Table II, PDF p. 4]

성공하면 $r_1$을 2로 올리고, 이후에는 object velocity나 EE interaction을 더 유도하지 않도록 $r_3=0$으로 두며 reach reward도 직전 값에 유지한다. 원문에 reward scale $\sigma_1,\sigma_2,\sigma_3,\sigma_{4,a},\sigma_{4,b}$의 수치는 제시되지 않는다. [원문 §III-D, Table II, PDF p. 4]

### 7.2 Constraint

Constrained PPO는 다음 task·actuation constraint를 사용한다.

| Constraint | 차원 | CAT의 $p_i^{\max}$ |
| --- | ---: | --- |
| Base command limit | 6 | 0.01 → 0.2 |
| Arm command limit | 5 | 0.05 → 0.9 |
| Arm action-rate limit | 5 | 0 → 0.05 |
| Arm joint-position limit | 5 | 0.05 → 0.9 |
| Arm joint-velocity limit | 5 | 0.05 → 0.9 |
| Arm joint-torque limit | 5 | 0 → 0.015 |
| Leg joint-torque limit | 12 | 0 → 0.01 |
| Undesired robot-object & self-collision | 18 | 1.0, curriculum 없음 |
| Object balance | 1 | 0.25, curriculum 없음 |

대부분의 constraint는 첫 12000 iteration 동안 $p_i^{\max}$를 증가시키는 curriculum을 사용한다. 초반에는 constraint violation이 reward termination probability에 미치는 영향을 낮춰 exploration을 허용하고, 뒤로 갈수록 constraint satisfaction을 강화한다. [원문 §III-D, Table II, PDF p. 4]

Object balance constraint는 robot base가 움직이는 동안 object inclination이 $\theta^{\mathrm{lim}}=10^\circ$를 넘지 않도록 구성한다. 저자들은 undesired collision, arm joint position, velocity limits는 특히 strict하게 만족시키려 한다고 설명한다. [원문 §III-D, Table II, PDF p. 4]

CAT 알고리즘에서 violation이 실제 termination probability로 변환되는 세부식은 본 논문이 아니라 [7]을 참조하도록 되어 있으므로 여기서 재구성하지 않는다.

## 8. Domain Randomization과 Deployment

### 8.1 Simulation randomization

Zero-shot hardware transfer를 위해 다음을 randomize한다.

| 항목 | 범위 |
| --- | --- |
| Object–floor static/dynamic friction의 combined coefficient | 0.4–1.25 |
| Object mass | 1–10 kg |
| Object CoM x/y | centroid 기준 각 dimension의 ±25% |
| Object CoM z | centroid 기준 $[-0.6d_z,\;0.25d_z]$ |
| Object x/y dimensions | 각각 0.25–0.75 m |
| Object z dimension | 0.4–1.0 m |
| Object shape | cuboid, cylinder |
| Robot base mass | ±5 kg |
| External disturbance | robot base에 7–10 s마다 random push |
| Arm initial joint positions | default configuration 주변 randomization |
| Actor observation | Table I의 additive uniform noise |

[원문 §III-E, PDF p. 4]

### 8.2 Real deployment

Hardware에서는 **external motion capture가 object와 robot base의 6D pose를 제공**한다. 이 값으로 Table I의 actor observation을 계산한다. Goal에 성공하면 locomotion controller의 base command를 zero로 만들어 제자리 stepping을 방지한다. [원문 §III-E, PDF p. 4]

따라서 본 논문의 zero-shot transfer는 “실물에서 perception 없이 동작한다”는 의미가 아니다. Object pose perception을 외부 motion capture에 의존한 채 policy parameter를 추가 학습 없이 옮겼다는 의미다.

## 9. Simulation 결과

### 9.1 Table III — surface sampling과 balance constraint ablation

4096 simulation run 결과는 다음과 같다.

| 설정 | Success rate | Toppled object rate |
| --- | ---: | ---: |
| Surface sampling 없음 | 49.80% | 4.50% |
| Surface sampling 없음 + balance constraint 없음 | 88.70% | 7.73% |
| Balance constraint 없음 | 90.00% | 6.93% |
| Full method | **91.35%** | **3.46%** |

[원문 Table III, §IV-A, PDF p. 5]

여기서 balance constraint만 추가하면 항상 성능이 좋아진다고 읽으면 안 된다. Surface target을 object centroid로 바꾼 상태에서 balance constraint를 유지하면 **49.80%**로 크게 떨어진다. 저자들은 centroid 방향으로만 접근하면 학습 초기에 balance violation이 증가해 task reward를 발견하기 어려워진다고 설명한다. 반대로 surface의 여러 위치를 경험하게 하면 balance constraint와 함께 높은 성공률과 낮은 toppling rate를 얻는다. [원문 §IV-A, Table III, PDF p. 5]

### 9.2 Constraint violation

4096 run에서 각 constraint가 violation 상태였던 시간 비율은 모두 1% 미만이다.

| Constraint | 평균 violation time |
| --- | ---: |
| Base command | 0.059% |
| Arm command | 0.014% |
| Arm action rate | 0.032% |
| Arm joint position | 0.011% |
| Arm joint velocity | 0.007% |
| Arm joint torque | 0.189% |
| Leg joint torque | 0.473% |
| Undesired collision | 0.01% |
| Object balance | 0.298% |

[원문 Table IV, §IV-B, PDF p. 5]

이 수치는 episode failure probability나 constraint satisfaction probability가 아니라 **simulated time에서 violation이 발생한 비율**이다.

저자들은 leg torque violation이 상대적으로 큰 이유 중 하나로, 사전 학습 locomotion policy를 학습할 때 arm EE에 simulated force가 없었다는 점을 든다. [원문 §IV-B, PDF p. 5]

## 10. Hardware 결과

### 10.1 다양한 물체의 goal-pose pushing

실험 바닥은 protective mat로 높은 마찰과 seam이 존재한다. 정책은 별도의 manual repositioning 없이 successive goal을 받아 object 주위를 돌아 적절한 면에서 다시 밀 수 있다. [원문 §IV-C, Fig. 4, PDF p. 5]

Table V의 결과는 다음과 같다.

| 재질·형상 | Mass | Size | Goal yaw 차이 | 평균 face switch / goal | Success |
| --- | ---: | --- | ---: | ---: | ---: |
| Plastic cuboid | 6.43 kg | 60×34×40 cm | 180° | 0.90 | 91.6% |
| Cardboard cuboid | 5.30 kg | 50×50×53 cm | 0° | 0.23 | 92.9% |
| Cardboard cuboid | 8.32 kg | 50×50×53 cm | 90° | 0.75 | 83.3% |
| Cardboard cuboid | 4.5 kg | 100×50×53 cm | 0° | 0.14 | 80.0% |
| Wood cuboid | 6.30 kg | 40×40×60 cm | 180° | 1.00 | 91.6% |
| Cardboard cuboid on caster wheels | 13.30 kg | 50×50×60 cm | 0° | 4.80 | 83.3% |
| Cardboard cylinder | 2.45 kg | $\Phi 30\times 40\,\mathrm{cm}$ | 0° | — | 83.3% |

[원문 Table V, §IV-C, PDF p. 5]

높은 yaw 변화에서는 다른 face로 contact를 바꾸는 횟수가 증가한다. Cylinder는 face ID를 정의할 수 없으므로 face-switch metric을 제시하지 않는다. [원문 §IV-C, PDF pp. 5–6]

13.3 kg caster-wheel cuboid는 training에서 wheeled kinematics를 본 적이 없다. 저자들은 이 경우 motion overshoot가 생겨 더 많은 contact face switch와 시간이 필요하지만 최종적으로 성공했다고 보고한다. [원문 §IV-C, PDF p. 6]

### 10.2 Reactive behavior

Goal을 고정하고 사람이 object를 여러 차례 goal에서 밀어내는 동안 policy를 계속 실행한다. Fig. 5에서 policy는 object를 다시 10 cm / 10 deg tolerance 안으로 되돌린다. [원문 §IV-C, Fig. 5, PDF p. 6]

저자들이 보고한 대표적 failure pattern은 **goal margin에 매우 가까워진 뒤 pushing을 멈추는 것**이다. 저자들은 이를 method 자체의 limitation이라기보다 추가 policy tuning으로 완화할 수 있다고 해석한다. [원문 §IV-C, PDF p. 6]

## 11. Object-size adaptation과 toppling avoidance

### 11.1 Size는 actor input이 아니다

저자들은 training range 안에서 6개의 rectangular-base size를 선택하고, size마다 1000 successful episode를 분석한다. Object height·mass·CoM·friction을 고정하고 observation noise를 끈 뒤 base footprint의 영향만 본다. [원문 §IV-D, Fig. 6, PDF p. 6]

Footprint가 작을수록 policy의 contact EE height가 낮아진다. 그러나 actor는 dimensions를 직접 입력받지 않는다. 저자들은 이 adaptive behavior가 **object pose observation에 기반한다**고 설명한다. [원문 §IV-D, PDF p. 6]

### 11.2 “숨은 size를 식별했다”는 결과는 아니다

Fig. 7에서 thin cylinder가 기울기 시작하면 actor가 보는 full object rotation matrix에 inclination이 나타난다. Robot은 arm EE를 낮추고 base height·pitch·roll까지 조절하여 더 낮은 위치에서 밀고 toppling을 회피한다. [원문 Fig. 7, §IV-D, PDF p. 6]

따라서 결과를 “policy가 contact feedback으로 object size를 추정했다”고 해석하면 안 된다. 저자들의 설명은 **size 자체를 관측하지 않더라도, size가 작은 물체가 기울면서 나타나는 current object pose 변화에 반응하여 낮은 contact를 선택한다**는 쪽에 가깝다. [원문 §IV-D, PDF p. 6]

## 12. Limitation — 저자들이 밝힌 한계

논문에는 독립된 Limitation 절이 없다.

저자들이 명시적으로 언급한 실패 현상은 hardware에서 goal tolerance에 거의 도달한 뒤 pushing을 멈추는 경우다. 그러나 저자들은 이를 **method의 본질적 limitation이라고 보지 않고 policy tuning으로 완화 가능**하다고 적는다. 따라서 본 정리에서도 저자 명시 limitation으로 재분류하지 않는다. [원문 §IV-C, PDF p. 6]

현재 system이 external motion-capture를 사용한다는 사실과 memoryless policy라는 사실은 원문에 명시되어 있으나, 저자들은 이를 별도의 “Limitation” 목록으로 제시하지 않는다. 두 항목은 다음 Future Work와 연결해서 기록한다. [원문 §III-E, §V, PDF pp. 4, 6]

## 13. Future Work — 저자들이 제시한 향후 연구

Conclusion에서 두 가지 future direction을 명시한다.

1. **Policy architecture에 memory 추가**
2. **Object perception을 external motion capture가 아닌 onboard solution으로 전환**

[원문 §V, PDF p. 6]

첫 번째는 현재 actor가 previous action은 받지만 recurrent memory를 사용하지 않는 구조를 확장하려는 계획이다. 두 번째는 hardware deployment에서 외부 motion capture가 object/base pose를 제공하는 현재 setup을 onboard perception으로 대체하려는 방향이다. [원문 Table I, §III-E, §V, PDF pp. 3–4, 6]

## 14. 미명시 사항·원문 주의사항

| 항목 | 확인 결과·주의 |
| --- | --- |
| Actor/critic neural-network architecture | 미명시 |
| PPO learning rate, batch/minibatch, epoch, entropy, clip, gamma, lambda | 본문 미명시. [25], [7]의 설정을 그대로 사용했다고 단정하지 않음 |
| Reward scale $\sigma_1,\sigma_2,\sigma_3,\sigma_{4,a},\sigma_{4,b}$ | Table II에 기호는 있으나 수치 미명시 |
| External motion-capture 제조사·주파수·정확도·latency | 미명시 |
| Arm 모델명·payload·reach | 미명시 |
| Joint impedance gain·저수준 주기 | 미명시 |
| Robot base velocity·gravity·joint state의 실제 sensor/state-estimator 구성 | 미명시 |
| Wrist F/T sensor | 제안 actor input에 없음 |
| Tactile sensor | 제안 actor input에 없음 |
| EE–object contact detector | Simulation critic privileged state만 명시. 실물 sensor로 사용하지 않음 |
| Hardware trial 횟수 | Table V는 성공률을 제공하지만 각 row의 전체 trial 수는 본문 미명시. 퍼센트에서 역산하지 않음 |
| Table V Size 열의 단위 | 표에는 cm³로 적혀 있지만 값은 60×34×40과 같은 3축 dimension 형태. 원문의 표기를 그대로 기록하고 volume으로 재계산하지 않음 |
| Caster-wheel object | 13.3 kg row는 training에 없던 wheeled kinematics. 일반적인 모든 비훈련 dynamics에 대한 보장으로 확대하지 않음 |
| “only observes object pose” | actor 전체 observation이 pose 하나뿐이라는 뜻이 아님. Object intrinsic property에 대해 pose만 제공된다는 의미로 읽어야 함 |
| Code·supplementary video 재현 | 이번 작업에서는 확인·실행하지 않음 |

## 15. 다시 읽을 때의 원문 위치

| 내용 | 위치 |
| --- | --- |
| 문제 정의·unknown physical properties·contact switching | Abstract·§I, PDF p. 1 / 인쇄 p. 13363 |
| 기여·toppling 문제·3D contact location | §I, PDF pp. 1–2 |
| Model-based와 force/tactile pushing 비교 | §II-A–B, PDF p. 2 / 인쇄 p. 13364 |
| 전체 control pipeline | Fig. 2, §III, PDF p. 2 |
| ANYmal·6-DoF arm·locomotion policy | §III-A, PDF p. 2 |
| Isaac Lab, 4096 env, 20000 iterations | §III-B, PDF p. 2 |
| Initial/goal sampling과 success tolerance | §III-B, Fig. 3, PDF p. 3 |
| Actor·critic observation 전체 | Table I, §III-C, PDF p. 3 / 인쇄 p. 13365 |
| Actor 54D / critic 73D 정보 비대칭 | §III-C, Table I, PDF p. 3 |
| Action 11D와 low-level controller 연결 | §III-C, PDF p. 3 |
| Reward와 weight | §III-D, Table II, PDF p. 4 / 인쇄 p. 13366 |
| Constraint·CAT curriculum | §III-D, Table II, PDF p. 4 |
| Domain randomization | §III-E, PDF p. 4 |
| External motion capture deployment | §III-E, PDF p. 4 |
| Simulation ablation | Table III, §IV-A, PDF p. 5 / 인쇄 p. 13367 |
| Constraint violation rate | Table IV, §IV-B, PDF p. 5 |
| Hardware object별 success와 face switch | Table V, §IV-C, PDF p. 5 |
| Reactive perturbation recovery | Fig. 5, §IV-C, PDF p. 6 |
| Object footprint와 EE height | Fig. 6, §IV-D, PDF p. 6 |
| Thin cylinder toppling 회피 | Fig. 7, §IV-D, PDF p. 6 |
| Failure pattern·Future Work | §IV-C·§V, PDF p. 6 / 인쇄 p. 13368 |

PDF 7쪽은 참고문헌이며 인쇄 p. 13369에 해당한다.

## 16. 핵심 메커니즘 요약

이 논문은 **unknown dynamics를 contact sensor로 직접 식별하는 방법이 아니다.** Actor는 지속적으로 갱신되는 object pose와 robot state, goal relation을 보고 mobile base와 arm을 동시에 제어한다. Object mass·geometry·inertia·shape·velocity와 contact state는 actor에서 숨기되, simulation critic에는 privileged information으로 제공하고 reward에는 GT geometry·velocity를 사용한다. [원문 Table I–II, §III-C–D, PDF pp. 3–4]

Policy는 contact mode를 명시적으로 선택하지 않는다. Object pose tracking이 contact break 동안에도 계속 살아 있으므로 robot이 object 주위를 돌아 새 contact를 만들 수 있고, surface-target shaping으로 다양한 접촉 위치를 경험하면서 contact switching을 학습한다. Object balance constraint와 full object orientation 관측을 통해 기울어진 얇은 물체에는 더 낮은 위치에서 미는 행동이 나타난다. [원문 §III-B–D, §IV-A·C·D, Fig. 4·6·7, PDF pp. 3–6]

따라서 이 논문의 핵심은 **“물성은 모르지만 object pose는 계속 안다”는 조건에서, asymmetric actor-critic과 domain randomization으로 mobile contact switching을 학습**한 것이다. 실물 zero-shot 결과는 다양한 material·mass·shape와 high-friction floor에서 최소 80% success를 보였지만, 현재 perception은 external motion capture에 의존하며 저자들은 memory와 onboard perception을 Future Work로 제시한다. [원문 §III-E, Table V, §V, PDF pp. 4–6]
