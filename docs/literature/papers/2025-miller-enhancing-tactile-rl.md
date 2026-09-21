# Enhancing Tactile-based Reinforcement Learning for Robotic Control

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [Binary Tactile 조사 B4](../reviews/2026-09-16_binary-tactile-wrench-rl.md#b4) · [B057 Review 분석](../review_dataset/260918/batch_002/papers/2025-miller-enhancing-tactile-rl.md) · [CHECK-A12 목록](../reviews/2026-09-20_separate-review-paper-list.md)

## 1. 논문 정보와 확인 범위

- **제목:** Enhancing Tactile-based Reinforcement Learning for Robotic Control
- **저자:** Elle Miller, Trevor McInroe, David Abel, Oisin Mac Aodha, Sethu Vijayakumar
- **게재:** 39th Conference on Neural Information Processing Systems (NeurIPS 2025)
- **원문 버전:** arXiv:2510.21609v1, 2025-10-24
- **DOI:** 원문에 명시 없음
- **확인 원문:** 사용자 제공 PDF 28쪽 전체, Appendix A–H 포함
- **파일 SHA-256:** e51421f53cd0d4b333b05f64adf74fc0f7a52e8ee48c4bbc1c07276a1d0573b2
- **저자 프로젝트:** https://elle-miller.github.io/tactile_rl
- **확인하지 않은 자료:** 공개 코드 실행, 학습 checkpoint 재현, 별도 실물 하드웨어 실험은 이번 정독에서 수행하지 않음

이 논문은 **proprioception + sparse binary contact만 사용하는 blind manipulation RL**에서 tactile 정보가 언제 실제로 필요한지, 그리고 sparse tactile을 policy가 제대로 사용하도록 representation을 어떻게 학습할지를 연구한다. Vision, depth, runtime object pose와 teacher-student privileged-state distillation을 의도적으로 사용하지 않는다. [원문 §1, §3.1]

핵심 주장은 두 층으로 나뉜다.

1. **Sensor-level question:** binary tactile은 proprioceptive history보다 실제로 추가 정보를 주는가?
2. **Representation-level question:** tactile이 유용하더라도 PPO가 sparse/non-smooth contact를 무시할 수 있는데, self-supervised learning이 이를 개선할 수 있는가?

논문의 모든 manipulation 결과는 **Isaac Lab simulation**에서 얻은 것이며, 실물 robot 검증은 없다.

## 2. 연구 배경과 문제 정의

저자들은 tactile RL 문헌에서 촉각의 효과에 대한 결과가 일관되지 않다고 지적한다. 어떤 연구는 tactile을 추가했을 때 성능이 향상되지만, 다른 연구에서는 proprioception만으로도 유사한 성능이 나온다. 특히 binary contact가 proprioceptive history에 이미 암묵적으로 포함된다는 주장도 존재한다. [원문 §1]

저자들이 제안하는 원인은 tactile signal의 데이터 특성이다.

- contact가 있을 때만 발생하여 **sparse**
- contact/no-contact 전환 때문에 **non-smooth**
- proprioception은 거의 항상 존재하는 continuous signal
- gradient-based RL이 안정적인 proprioception에 먼저 의존하면서 tactile representation을 충분히 학습하지 못할 가능성

따라서 이 논문은 단순 tactile 추가 실험을 넘어서, **정책·value function과 동시에 학습되는 observation encoder가 tactile 정보를 실제 latent state에 보존하도록 auxiliary self-supervision을 제공**한다.

## 3. 주요 기여

저자들이 제시한 주요 기여는 다음과 같다. [원문 §1]

1. Sparse binary tactile이 proprioceptive history를 넘어서는 효과가 있음을 task별로 분석
2. Proprioception + 최대 17 binary contacts만으로 복잡한 simulated dexterity 달성
3. Tactile Reconstruction(TR), Full Reconstruction(FR), Forward Dynamics(FD), Tactile Forward Dynamics(TFD)의 네 self-supervised objective 제안·비교
4. On-policy PPO rollout과 self-supervised auxiliary memory를 분리하는 방법 분석
5. Find, Bounce, Baoding의 세 환경을 포함하는 Robot Tactile Olympiad(RoTO) benchmark 제안

저자들은 특히 **Forward Dynamics가 가장 일반적으로 강한 auxiliary objective**이며, learned latent가 object position과 velocity 관련 정보를 포함하도록 만든다고 분석한다.

## 4. Related Work의 비교 구도

### 4.1. In-hand manipulation RL

기존 연구는 privileged state teacher-student, RGB-D, explicit object pose estimator 등에 의존하는 경우가 많다고 정리한다. 본 논문은 **runtime object state 없이 tactile + proprioception에서 직접 representation을 학습**하는 방향을 택한다.

### 4.2. RL representation learning

Pixel RL에서는 reconstruction, latent forward dynamics, contrastive learning, information bottleneck 등 auxiliary representation learning이 널리 사용된다. 저자들은 이러한 접근을 tactile/proprioceptive observation으로 가져온다.

### 4.3. Tactile representation learning

기존 tactile SSL에는 tactile image augmentation, masked reconstruction, visual-tactile contrastive learning, contact prediction 등이 있다. 본 논문은 **binary contact를 대상으로 multi-step forward dynamics를 model-free RL에 결합**하는 데 초점을 둔다.

### 4.4. Tactile-tailored RL

Contact-rich episode를 더 자주 replay하거나 contact가 있을 때만 tactile encoder를 update하는 접근과 달리, 본 논문은 **on-policy RL과 auxiliary representation learning이 사용하는 데이터 memory 자체를 분리**한다.

## 5. POMDP 정의와 관측 구조

논문은 true state가 직접 보이지 않는 POMDP로 문제를 정의한다. 서로 다른 실제 state가 sensing limitation 때문에 동일 observation을 만들 수 있는 perceptual aliasing을 partial observability의 핵심으로 둔다. [원문 §3.1]

Agent observation은 단일 frame이 아니라 **최근 k timestep의 multimodal history**다.

Proprioception에는 다음이 포함된다.

- joint angles $\theta$
- joint velocities $\dot{\theta}$
- previous action $a_{t-1}$
- 환경에 따라 EEF position $x_{EE}$
- 환경에 따라 EEF orientation $q_{EE}$
- Find에서는 gripper width

Tactile observation은

```math
o_t^{tact}=b\in\{0,1\}^{N_{sensors}}
```

의 sensor/link별 binary contact다.

즉 continuous force magnitude, shear vector, pressure image, current object pose는 actor observation에 없다.

## 6. Environment별 Observation

Appendix Table A1의 observation은 다음과 같다.

| Environment | Tactile | Previous action | Joint angle | Joint velocity | 추가 proprioception | 한 frame | History |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| Find | 2 | 9 | 9 | 9 | EEF pos 3 + quat 4 + gripper width 1 | 37D | $k=16$ |
| Bounce | 17 | 20 | 24 | 24 | 없음 | 85D | $k=4$ |
| Baoding | 17 | 20 | 24 | 24 | 없음 | 85D | $k=4$ |

따라서 stacked observation 크기는 Find가 $37\times16$, Bounce/Baoding이 $85\times4$이다.

History length는 경험적으로 정했다.

## 7. Binary Tactile의 생성

### 7.1. Find

Franka parallel gripper finger 위에 **plate-like body 두 개**를 추가해 contact sensor로 사용한다. Object 또는 다른 finger와 해당 body가 collision할 때만 sensor가 반응하도록 구성하여 ground contact가 tactile로 들어오지 않게 한다.

### 7.2. Bounce / Baoding

Shadow Hand는 midair에 고정되어 있으므로 **17개 link 각각을 contact sensor로 설정**한다.

### 7.3. Raw → Binary

Isaac Lab ContactSensor의 **net contact force**를 가져온 뒤 binary contact로 변환한다.

원문은 binary threshold의 실제 수치를 명시하지 않는다.

따라서 이 논문의 17개 tactile은 실제 17-taxel hardware의 raw binary output이 아니라, **simulation에서 17 hand links에 배치한 contact regions를 이진화한 표현**이다.

## 8. Proprioception 전처리

Appendix E.1에서 다음 preprocessing을 명시한다.

- joint angle: $[-1,1]$로 normalize
- Franka joint velocity: 0.33을 곱해 scaling
- Shadow joint velocity: 0.2를 곱해 scaling
- tactile: net contact force를 binary화

Previous action 역시 observation에 포함되며, 이는 이후 proprioception-only agent가 contact를 암묵적으로 추정하는 데 중요한 역할을 한다.

## 9. Encoder, Policy, Value Network

Observation history 전체를 하나의 MLP encoder가 latent로 변환한다.

```math
o_t\rightarrow1024\rightarrow512\rightarrow256\rightarrow z_t.
```

Layer normalization과 ELU를 각 hidden layer 뒤에 사용한다.

Policy는

```math
z_t\rightarrow128\rightarrow64\rightarrow n_{actions}\rightarrow a_t
```

이고 output activation은 tanh다.

Value network는

```math
z_t\rightarrow128\rightarrow64\rightarrow1\rightarrow V(o_t)
```

이다.

Actor와 value function 모두 동일 encoder $e$의 latent representation $z_t$에 condition된다.

## 10. PPO와 Auxiliary Loss의 결합

RL algorithm은 PPO-Clip이다.

논문의 notation을 따르면 PPO 관련 loss는 encoder, policy, value parameters를 함께 update하며, 여기에 auxiliary representation loss를 추가한다.

```math
L=L_{PPO}(\theta_e,\theta_\pi,\theta_v)+c_{aux}L_{aux}(\theta_e,\theta_{aux}).
```

PPO update와 auxiliary update는 **서로 다른 optimizer**를 사용한다.

- PPO: shared learning rate $lr$, gradient clipping 1.0
- Auxiliary: learning rate $lr_{aux}$, gradient clipping 없음

Auxiliary network는 training에서만 사용하며 deployment 후에는 제거할 수 있다.

## 11. Self-Supervised Objective 1 — Tactile Reconstruction

문제는 multimodal encoder가 stable proprioception만 사용하고 sparse tactile을 무시하는 것이다.

TR은 latent $z_t$에서 원래 tactile observation을 복원하도록 강제한다.

Binary tactile이므로 BCE classification loss를 사용하며, contact class sparsity를 보정하기 위해 positive weight

```math
p_c=10
```

을 사용한다.

개념적으로 loss는 contact false negative를 non-contact error보다 더 크게 벌준다.

이 objective의 목적은 **latent representation 안에 tactile contact pattern을 반드시 남기게 하는 것**이다.

## 12. Self-Supervised Objective 2 — Full Reconstruction

FR은 tactile뿐 아니라 proprioception까지 동시에 reconstruction한다.

```math
L_{FR}=L_{TR}+\mathrm{MSE}(\hat{o}_t^{prop},o_t^{prop}).
```

이는 일반적인 multimodal autoencoder에 가까운 baseline이다.

중요하게도 결과에서는 모든 task에서 FR이 TR보다 좋은 것이 아니다. 특히 Baoding에서는 tactile-only reconstruction인 TR이 FR을 크게 앞서며, 저자들은 proprioceptive reconstruction이 tactile representation과 **negative interference**를 일으킬 가능성을 제시한다.

## 13. Self-Supervised Objective 3 — Multi-step Forward Dynamics

FD는 reconstruction이 아니라 **미래를 예측하는 데 필요한 정보**를 latent에 남기려는 objective다.

Memory에서 terminal transition을 포함하지 않는 sequence

```math
(o_t,a_t,\ldots,o_{t+n-1},a_{t+n-1})
```

를 sampling한다.

현재 latent와 action에서 다음 latent를 예측한다.

```math
\hat{z}_{t+1}=f(z_t,a_t).
```

이 prediction을 autoregressive하게 반복해 여러 timestep 미래를 예측한다.

Target latent는 실제 encoder를 직접 사용하지 않고 EMA target encoder $e_T$로 계산한다.

```math
z_{t+i}^{T}=e_T(o_{t+i}).
```

Forward prediction은 projector $p$를 거쳐 target latent와 MSE로 비교한다.

```math
L_{FD}=\sum_{i=1}^{n-1}\mathrm{MSE}\left(p(\hat{z}_{t+i}),z_{t+i}^{T}\right).
```

Target encoder update는 Appendix 식 (7)을 따른다.

```math
\theta_{e_T}\leftarrow(1-\tau)\theta_{e_T}+\tau\theta_e,\qquad\tau=0.01.
```

## 14. Self-Supervised Objective 4 — Tactile Forward Dynamics

TFD는 FD에 **future tactile reconstruction**을 추가한다.

예측된 future latent $\hat z_{t+i}$를 decoder로 binary tactile space로 다시 변환하고, 실제 미래 tactile과 BCE를 계산한다.

즉 목적은

- latent dynamics prediction
- predicted latent에서 tactile dynamics가 복원 가능하도록 보존

을 동시에 수행하는 것이다.

원문 결과에서는 이 추가 constraint가 항상 유리하지 않다. Find에서는 좋은 결과를 보이지만 Bounce에서는 가장 약한 objective 중 하나이며, 저자들은 explicit tactile reconstruction term이 forward prediction과 충돌할 가능성을 논의한다.

## 15. Separated Auxiliary Memory

일반적인 on-policy auxiliary learning은 PPO rollout과 같은 데이터에서 representation loss를 학습한 뒤 rollout을 버린다.

저자들은 rollout이 교체될 때마다 auxiliary loss에 spike가 발생하는 것을 관찰한다.

이를 완화하기 위해 SSL용 data buffer를 별도로 두어 최근 여러 rollout을 보관한다.

On-policy RL rollout shape가

```math
[B,R,\ldots]
```

이면 auxiliary memory는

```math
[N_{rollouts},B,R,\ldots]
```

로 확장된다.

기대 효과는 다음 두 가지다.

1. Auxiliary update의 data distribution 변화 완화
2. 더 넓은 experience distribution에서 representation 학습

PPO 자체를 off-policy로 바꾸는 것이 아니라, **policy는 on-policy PPO를 유지하면서 representation auxiliary loss만 과거 rollout도 활용**한다.

## 16. Robot Tactile Olympiad — Find

### 16.1. Task

Franka robot이 20 cm × 20 cm plate의 어딘가에 고정된 sphere를 찾아야 한다.

- episode: 300 timesteps
- 약 5 s
- tactile sensors: 2
- history: 16
- action: 9D joint position target

### 16.2. Reward

Object–EEF distance가 작아질수록 증가하는 dense distance reward를 사용한다.

Actor observation에 object center GT는 없지만 **reward는 simulator의 object–EEF distance를 사용**한다.

## 17. Robot Tactile Olympiad — Bounce

### 17.1. Task

Shadow Hand가 30 g, 70 mm diameter ball을 10초 동안 최대한 많이 튀긴다.

- episode: 600 timesteps
- tactile sensors: 17
- history: 4
- action: 20D joint position target
- policy frequency: 60 Hz

Bounce event는 **최소 5 timesteps, 약 83 ms 동안 contact가 없다가 다시 contact가 생긴 경우**로 정의한다.

### 17.2. Reward

Reward는 세 항으로 구성된다.

- $r_{air}$: 마지막 contact 이후 시간에 비례한 exploration reward
- $r_{bounce}$: bounce event bonus
- $r_{fall}$: ball이 허용 영역 밖으로 떨어졌을 때 penalty

## 18. Robot Tactile Olympiad — Baoding

### 18.1. Task

Shadow Hand 안에서 두 개의 1.5-inch, 55 g balls를 서로 회전시킨다.

- episode: 600 timesteps, 10 s
- tactile sensors: 17
- history: 4
- action: 20D

### 18.2. Reward 설계

초기에는 두 ball을 잇는 vector의 xy angular velocity를 maximize했지만, policy가 원래 Baoding과 다른 creative strategy를 만드는 문제가 있었다.

최종 reward는 두 virtual target positions를 사용한다.

- 각 ball center가 target center로 가까워지는 dense distance reward
- 두 ball 모두 target center의 1 cm 이내로 들어오면 target pair를 switch
- switch 시 rotation bonus
- ball distance가 15 cm를 넘으면 fall penalty

이 reward는 policy에 object position을 observation으로 제공한다는 뜻이 아니다. Simulator GT ball position은 **reward와 termination**에 사용된다.

## 19. Simulation / Control Rate

세 환경 모두

- physics: 120 Hz
- control policy: 60 Hz
- joint position control

을 사용한다.

Low-level PD gains나 실제 hardware actuator dynamics는 본문에서 상세히 제시하지 않는다.

## 20. RL-only Sensor Ablation

저자들은 다음 세 조건을 비교한다.

1. PPO(prop-tactile)
2. PPO(prop)
3. PPO(prop, no last action) — 이 조건만 1 seed

### 20.1. Find

Tactile을 추가했을 때 sample efficiency는 약간 개선되지만 **최종 performance는 proprioception-only와 유사**하다.

저자들은 proprioception-only agent가 previous action과 joint state 사이의 control error를 통해 contact를 암묵적으로 추정한다고 해석한다.

### 20.2. Bounce

Tactile을 추가하면 sample efficiency와 return이 더 높다.

다만 proprioception-only도 손을 펼친 채 반복 motion을 만드는 **state-agnostic degenerate bouncing strategy**로 상당한 성능을 얻는다.

### 20.3. Baoding

가장 큰 차이가 난다.

Proprioception-only는 사실상 task를 제대로 수행하지 못하지만 tactile을 추가하면 functional rotation behavior가 나타난다.

따라서 binary tactile의 효과는 task-independent하지 않고, interaction dynamics와 sensing ambiguity에 따라 달라진다.

## 21. 저자들이 정리한 “Tactile이 필요한 네 조건”

§6 Q1에서 저자들은 proprioception만으로 충분하지 않은 상황을 네 가지로 정리한다.

### 21.1. Decoupled object–robot dynamics

Object motion이 joint articulation direction과 분리되어 있어 object가 움직여도 joint control error에 큰 변화가 생기지 않는 경우다.

Baoding처럼 ball이 hand plane을 따라 수평으로 움직이는 상황이 대표적이다.

### 21.2. Low-inertia objects

아주 가볍거나 deformable한 물체는 contact reaction force가 작아 joint/proprioceptive signal에 충분한 변화를 만들지 못할 수 있다.

저자들은 30 g Bounce ball, paper, sponge를 예로 든다.

### 21.3. Contact spatial ambiguity

한 rigid link의 **어느 위치에서 contact가 발생했는지**가 필요한 경우다.

Joint control error는 motor에 전달되는 net effect만 보여 주므로 joint에서 접촉점까지의 거리와 정확한 위치를 구분하기 어렵다.

### 21.4. Multi-contact resolution

하나의 강한 contact인지 여러 개의 약한 simultaneous contact인지 구분해야 하는 경우다.

Proprioception은 total/net contribution을 중심으로 반영하므로 fine-grained contact source를 분리하기 어렵다.

이 네 항목은 저자들의 해석이며, 네 현상을 각각 독립적으로 하나씩 조작한 factorial experiment를 수행한 것은 아니다.

## 22. RL + Self-Supervision 결과

네 auxiliary objective를 비교한 결과:

- **TR:** 세 task 모두에서 강한 성능
- **FD:** 세 task 모두에서 강한 성능이며 전반적으로 가장 유리
- **FR:** task-dependent
- **TFD:** task-dependent

Find와 Bounce에서는 FD의 mean return이 TR보다 높다.

Baoding에서는 TR의 mean return이 더 안정적이지만, FD는 더 높은 upper-bound performance를 보인다.

따라서 단순 reconstruction보다 dynamics prediction이 control-relevant representation을 더 잘 만들 가능성이 있지만, **항상 한 objective가 모든 환경에서 절대적으로 우세한 것은 아니다.**

## 23. Auxiliary Memory 결과

FD agent에 separated auxiliary memory를 적용한다.

- Find: 효과 작음
- Bounce: 효과 작음
- Baoding: 큰 개선

저자들은 Baoding이 하나의 rotation을 이해하기 위해 더 긴 temporal horizon의 dynamics를 요구하기 때문에, 여러 rollout의 경험을 auxiliary representation learning에 사용하는 것이 유리했을 가능성을 제시한다.

## 24. Representation Analysis — Mutual Information

저자들은 self-supervision이 실제 object state 관련 정보를 latent에 더 많이 담는지 확인하기 위해

```math
I(z_t;s_t)
```

를 측정한다.

- 각 agent에서 5,000개의 $(z_t,s_t)$ sample 수집
- $z_t$는 원래 256D
- KSG estimator의 high-dimensional bias를 줄이기 위해 PCA로 13D까지 축소
- $K=4$ nearest neighbors

여기서 $s_t$는 **분석용 simulator GT state**이며 actor observation이 아니다.

### 24.1. Bounce

Base PPO가 전체 MI는 가장 높지만, 저자들은 반복적인 low-entropy trapping gait가 MI를 인위적으로 높인 결과일 수 있다고 지적한다.

Dynamics objectives는 non-zero MI를 보이며, FD는 ball vertical velocity와 x/z position을 유일하게 함께 encoding한다.

### 24.2. Baoding

MI 분포가 policy performance와 더 비슷하게 대응한다.

FD는 PPO보다 거의 3배의 MI를 보이고, marginal MI 분석에서 ball x/y/z position을 encoding한 유일한 model로 보고된다.

따라서 self-supervision이 object pose를 actor에 직접 제공한 것은 아니지만, **sensor history에서 object-state-correlated latent를 형성**할 수 있음을 분석적으로 보여 준다.

## 25. Reconstruction Objective의 Modality Interference

§6 Q3의 결과는 단순히 “더 많은 modality reconstruction이 더 좋다”는 결론을 부정한다.

- Find: FR > TR — proprioception reconstruction도 유용
- Bounce: FR ≈ TR — 주된 이득이 tactile에서 온 것으로 해석
- Baoding: TR ≫ FR — proprioception reconstruction 추가가 tactile representation에 방해가 된 가능성

특히 Baoding에서 TR만 failure run이 없었다고 저자들은 설명한다.

즉 multimodal encoder에 모든 modality를 동일한 auxiliary objective로 강제하는 것이 반드시 좋은 것은 아니다.

## 26. Forward Dynamics와 Explicit Tactile Reconstruction의 관계

FD는 combined observation latent의 future를 예측한다.

TFD는 여기에 tactile reconstruction까지 추가한다.

결과는 다음과 같다.

- Find: TFD가 일부 이점
- Bounce/Baoding: TFD가 FD보다 약함

저자들은 두 가능성을 제시한다.

1. FD만으로도 필요한 tactile information이 latent에 암묵적으로 충분히 포함됨
2. Tactile reconstruction loss와 dynamics prediction 사이에 training conflict가 발생함

정확한 mechanism은 이 논문에서 분리되지 않았고, **tactile-only forward model**이 후속 분석 방법으로 제안된다.

## 27. Physical Metric으로 본 성능

논문의 “physical metrics”는 실물 hardware가 아니라 **simulation에서 실제 task count/time으로 환산한 지표**다.

평균 기준으로 best self-supervised agent는 다음 성능을 보고한다.

| Task | 비교 | 결과 |
| --- | --- | --- |
| Find | FD vs baseline | object를 찾는 시간 약 1.4 s vs 1.9 s |
| Bounce | FD vs baseline | 10 s 동안 약 79 vs 69 bounces |
| Baoding | FD + auxiliary memory vs baseline | 10 s 동안 약 17 vs 5 rotations |

최고 seed 기준으로

- Bounce: 88 bounces / 10 s
- Baoding: 25 rotations / 10 s

를 보고한다.

저자들은 이를 인간 기록과 비교하지만 **실물 로봇 결과가 아니며 real world에 그대로 transfer될 가능성이 낮다고 직접 명시**한다.

## 28. Future Tactile Prediction 분석

Appendix D에서 TFD가 future binary tactile을 얼마나 잘 예측하는지 분석한다.

### Bounce

- tactile interaction이 점점 sparse해짐
- TPR은 약 99%에서 90% 정도로 감소
- FNR은 약 0.2% 수준으로 매우 낮게 수렴
- no-contact state에서도 다음 contact 발생을 미리 예측하는 사례가 관찰됨
- contact location은 틀릴 수 있음

### Baoding

- contact frequency가 높음
- 실제 contact detection TPR 약 99%
- FPR 약 15%
- 대부분 training에서 accuracy >96%

저자들은 $p_c=10$의 높은 positive weighting 때문에 contact를 miss하기보다 **overpredict하는 경향**이 생긴다고 해석한다.

## 29. Positive Weighting의 후속 개선안

Appendix D에서 저자들은 BCE positive weight를 fixed $p_c=10$으로 두는 것의 개선 방향을 제안한다.

- minibatch의 nonstationary contact distribution에 따라 inverse mean 기반으로 weight를 동적으로 변경
- palm과 pinky처럼 sensor region마다 activation frequency가 크게 다르므로 region별 imbalance를 따로 반영

이는 이번 논문에서 구현된 결과가 아니라 저자들이 제안한 future improvement다.

## 30. Training Protocol과 Hyperparameter Tuning

Custom PPO implementation은 SKRL 기반이다.

- training environments: 4096
- continuous evaluation environments: 100
- final evaluation: 5 seeds
- 각 environment × method combination마다 독립 hyperparameter sweep
- sweep당 Optuna TPE 20 trials, startup 5 trials
- PPO 및 SSL hyperparameter를 함께 tuning
- forward dynamics는 sequence length $n$도 tuning

고정한 주요 값:

- $\gamma=0.99$
- value loss scale $c_V=0.1$
- gradient norm clip 1.0
- value clip 0.2
- PPO ratio clip 0.2

논문은 method마다 별도 tuning하여 self-supervision을 단순히 baseline PPO hyperparameter 위에 얹는 비교를 피하려고 한다.

## 31. Compute Cost

실험 하나는 대략

- hyperparameter sweep: 약 50 GPU-hours
- final five seeds: 약 $5\times2$ hours
- 총 약 60 hours

로 설명된다.

전체 7 experiment × 3 tasks를 합쳐 약 **1,260 hours**의 compute를 보고한다.

사용 환경은

- 8× NVIDIA RTX A4500 cluster
- Isaac Lab 환경당 16 GB VRAM
- 32 GB RAM
- 8 CPU cores

이다.

## 32. Training-only / Privileged Information 경계

| 구성 | Object GT 사용 | 내용 |
| --- | --- | --- |
| Actor | No | Binary tactile + proprioception + previous action history의 learned latent |
| Value | No extra privileged state | Actor와 같은 encoder latent $z_t$ |
| PPO reward | Yes | Object/ball position, target distance, rotation/fall 상태 등 simulator state |
| Termination/reset | Yes | Ball distance, fall condition, randomized object position |
| SSL loss | No object GT | Sensor observation과 action만 사용 |
| MI representation analysis | Yes | $I(z_t;s_t)$ 계산을 위해 simulator true state 사용 |
| Deployment auxiliary network | No | Decoder/forward model은 training 후 제거 가능 |

따라서 논문의 blind agent는 **runtime policy observation이 object GT-free**라는 의미다. Training 전체가 simulator GT 없이 수행된다는 뜻은 아니다.

## 33. F/T와의 관계

이 논문은 wrist 6-axis F/T를 사용하지 않는다.

Tactile의 raw source는 simulation contact force이지만 policy에는 binary contact만 들어간다.

§6의 “net force contribution”은 proprioceptive joint control error가 contact effect를 얼마나 반영하는지를 설명하는 개념이며, **별도 F/T sensor measurement를 의미하지 않는다.**

따라서 이 논문의 결과만으로 wrist F/T와 binary tactile의 직접 비교 우열을 결론내릴 수 없다.

## 34. 저자들이 실험으로 직접 보여 준 것과 보여 주지 않은 것

### 직접 비교한 것

- proprioception vs proprioception+tactile
- tactile reconstruction / full reconstruction / forward dynamics / tactile forward dynamics
- on-policy auxiliary memory vs larger separated auxiliary memory
- latent representation과 simulator GT state의 mutual information
- 세 task에서 physical metric 변화

### 직접 비교하지 않은 것

- binary tactile vs continuous tactile magnitude
- binary tactile vs tactile image
- tactile vs wrist F/T
- real robot sim-to-real
- 17-link sensor layout vs 다른 sensor 배치
- 각 Q1 조건을 하나씩 독립적으로 조작한 factorial ablation
- tactile threshold 값에 대한 sensitivity
- sensor dropout/noise robustness

이 구분은 논문의 범위를 해석할 때 중요하다.

## 35. Limitation — 저자들이 직접 밝힌 한계

### 35.1. 실물 robot 검증 부재

§7에서 가장 큰 한계로 **physical robot hardware validation이 없음**을 명시한다.

저자들은 binary contact가 continuous tactile보다 sim-to-real complexity가 작다고 설명하지만, 실제 transfer를 검증한 것은 아니다.

### 35.2. Self-supervision의 계산 비용

RL-only에 비해 auxiliary network와 additional optimization 때문에 training compute가 증가한다.

특히 forward dynamics는 prediction sequence length $n$이 커질수록 비용이 증가한다.

### 35.3. Auxiliary memory의 메모리 비용

Separated auxiliary memory는 과거 rollout을 더 보관하므로 memory requirement를 증가시킨다.

### 35.4. 다른 domain 일반화 미검증

저자들은 locomotion 등 다른 environment에서도 유사한 결과를 기대하지만 실험하지 않았다.

### 35.5. Human comparison의 한계

§6 Q4에서 simulation agent가 human record를 넘는 결과를 제시하지만 real-world에 그대로 transfer될 가능성이 낮다고 직접 인정한다.

## 36. Future Work — 저자들이 제시한 향후 연구

원문에 독립적인 Future Work 절은 없지만 다음 구체적 후속 방향을 제안한다.

1. **Tactile-only forward model**
   - FD가 tactile을 어떻게 활용하는지 TFD와 분리하여 분석

2. **Off-policy experience의 representation learning 활용**
   - on-policy PPO를 유지하면서 auxiliary encoder가 더 다양한 과거 데이터를 사용하는 방향

3. **Adaptive BCE weighting**
   - nonstationary minibatch contact ratio에 따라 positive weight를 동적으로 설정

4. **Sensor-region별 imbalance 보정**
   - palm/finger별 contact frequency 차이를 loss weighting에 반영

실물 validation의 필요성은 limitation으로 명시되지만, 구체적인 hardware experiment plan을 별도 future-work 항목으로 제안하지는 않는다.

## 37. 미명시 사항과 원문 해석 주의점

### 37.1. Binary contact threshold

Isaac Lab net contact force를 binary로 만든다고 명시하지만 **threshold 수치는 제공되지 않는다.**

### 37.2. 17 contacts와 실제 tactile hardware를 동일시하면 안 된다

Shadow Hand의 17개 link를 simulation ContactSensor region으로 사용하는 설정이다. 실제 17-taxel hand sensor의 electrical characteristics, noise, dead zone, coverage를 검증한 것이 아니다.

### 37.3. Binary가 continuous보다 우수하다는 실험은 아니다

저자들은 computational/sim-to-real 이점을 이유로 simple tactile representation부터 시작하라고 권고하지만, 본 실험에 continuous tactile baseline이 없다.

### 37.4. PPO가 object pose 없이 학습되지만 reward는 GT를 사용한다

Blind runtime observation과 simulator reward supervision을 분리해야 한다.

### 37.5. “Superhuman”은 simulated metric

88 bounces와 25 Baoding rotations는 simulation best run이다.

### 37.6. No-last-action baseline은 한 seed

Previous action 제거 비교는 main 5-seed evaluation과 동일한 통계 수준이 아니다.

### 37.7. Tactile utility의 네 조건은 저자 해석

Decoupled dynamics, low inertia, spatial ambiguity, multi-contact resolution은 실험 결과를 바탕으로 한 설명이지만 각각을 독립적으로 격리해 검증한 것은 아니다.

## 38. 원문 위치 안내

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 연구 문제·기여 | Abstract, §1, PDF pp. 1–3 |
| Related Works | §2, PDF p. 3 |
| POMDP·observation encoder·PPO | §3.1, PDF p. 4 |
| TR / FR / FD / TFD | §3.2, Fig. 2, PDF pp. 4–5 |
| Separated auxiliary memory | §3.3, PDF p. 5 |
| RoTO task·frequency·sensor 수 | §4, PDF p. 6 |
| RL-only tactile ablation | §5, Fig. 3, PDF pp. 6–7 |
| SSL 비교 | §5, Fig. 4, PDF p. 7 |
| Auxiliary memory | §5, Fig. 5, PDF p. 7 |
| Tactile 필요 조건 4개 | §6 Q1, PDF p. 8 |
| Mutual information analysis | §6 Q2, Fig. 6, PDF p. 8 |
| Modality interference | §6 Q3, PDF p. 9 |
| Physical metrics | §6 Q4, Fig. 7, PDF p. 9 |
| Practical recommendations | §6 Q7, PDF p. 10 |
| Limitations | §7, PDF p. 10 |
| Observation 상세 | Appendix E.1, Table A1, PDF p. 22 |
| Action·reward·reset | Appendix E.2–E.4, PDF pp. 22–23 |
| Network architecture | Appendix F, PDF pp. 23–24 |
| Hyperparameter sweep | Appendix G, Tables A3–A4, PDF pp. 24–25 |
| Future tactile prediction 분석 | Appendix D, PDF pp. 18–21 |
| Latent trajectories | Appendix H, PDF pp. 25–28 |

## 39. 문서 검증 범위

사용자 제공 arXiv v1 / NeurIPS 2025 PDF 28쪽 전체를 확인했다. 본문과 Appendix A–H의 observation, reward, network, hyperparameter, representation analysis 및 tactile prediction 결과를 함께 대조했다.

특히 Fig. 1–7, Table A1–A4와 Appendix의 tactile prediction 및 latent trajectory figure를 포함하여 본문의 주장과 세부 experimental setting을 구분해 정리했다.

코드 실행, PPO 재학습, Isaac Lab environment 재현, physical robot test는 수행하지 않았다. 원문 PDF를 저장소에 복제하지 않으며 arXiv identifier와 SHA-256으로 출처를 관리한다.
