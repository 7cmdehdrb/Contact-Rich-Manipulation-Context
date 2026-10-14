# Precision-Focused Reinforcement Learning Model for Robotic Object Pushing

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [B008 Review 분석](../review_dataset/260918/batch_001/papers/2025-bergmann-precision-focused-pushing.md) · [CHECK-A02 목록](../reviews/2026-09-20_separate-review-paper-list.md)

## 1. 논문 정보와 확인 범위

- **제목:** Precision-Focused Reinforcement Learning Model for Robotic Object Pushing
- **저자:** Lara Bergmann, David Leins, Robert Haschke, Klaus Neumann
- **게재:** 2025 International Conference on Advanced Robotics and Mechatronics (ICARM 2025), pp. 758–765
- **DOI:** [10.1109/ICARM65671.2025.11293485](https://doi.org/10.1109/ICARM65671.2025.11293485)
- **확인 원문:** 사용자 제공 IEEE 출판본 PDF 8쪽 전체
- **파일 SHA-256:** 6f34f73c0f3f8c541e626664cbffa907574b4fd15d289314665edca514483d38
- **저자 공개 코드:** [ubi-coro/precise_pushing](https://github.com/ubi-coro/precise_pushing) — 원문에 링크가 있으나 이번 정독에서는 코드 자체를 실행·검증하지 않음
- **확인하지 않은 자료:** 외부 코드 실행 결과, 학습 checkpoint, 별도 supplementary material, YouTube 영상의 세부 행동은 이번 정독에서 검증하지 않음

이 연구는 **tactile 또는 F/T sensor를 사용하지 않는 vision–proprioception 기반 planar pushing 연구**다. 직접적인 목표는 물체를 목표 위치의 **1 cm 이내**로 정밀하게 밀면서 overshoot와 불필요한 corrective movement를 줄이는 것이다. 물체의 mass와 friction은 RGB binary silhouette만으로 관측되지 않기 때문에, 저자들은 **episode 전체 observation history를 GRU로 처리하여 과거 push에 대한 물체 반응을 기억**하게 한다. [원문 §I, §IV-B, PDF pp. 1, 3]

따라서 이 논문에서 말하는 binary는 tactile contact가 아니라 **RGB 영상을 color filtering한 binary object/goal mask**다. 또한 sliding friction force는 정책이 센서로 측정하는 wrench가 아니라 simulation의 mass와 friction coefficient로 정의한 물리량이다.

## 2. 초록과 핵심 연구 질문

저자들이 다루는 문제는 다양한 shape, size, mass, friction을 가진 물체를 목표 위치까지 **정확하게** 밀어야 하는 상황이다. 특히 mass와 friction은 직접 관측되지 않으며, 마찰이 작으면 물체가 목표를 지나치기 쉽다. 그 결과 robot은 object의 반대편으로 돌아가 다시 밀거나 방향을 바꾸는 corrective movement가 필요해진다. [원문 Abstract, §I]

기존 vision-proprioception model(VPM) [2]은 planar pushing을 RL로 수행하지만 성공 tolerance가 **5 cm**였다. 본 논문은 이를 **1 cm**로 줄이고, 다음 두 가지를 핵심 변경으로 제시한다.

1. **GRU memory:** episode 전체 관측 history에서 object response를 기억
2. **Improved sampling:** 작은 sliding friction force처럼 정밀 제어가 어려운 조건을 training에서 더 자주 샘플링

논문의 연구 질문을 정리하면 다음과 같다.

> 현재 RGB silhouette와 EEF position만으로 직접 관측되지 않는 object dynamics를, 과거 observation sequence를 이용해 암묵적으로 추론하면 1 cm 수준의 precise pushing과 corrective movement 감소에 도움이 되는가?

## 3. Related Works의 비교 구도

원문 §II는 pushing을 다음과 같이 구분한다.

### 3.1. Pushing을 보조 skill로 사용하는 연구

Pushing과 grasping을 결합하거나 clutter에서 object singulation을 수행하는 연구가 많다. 이런 경우 pushing 자체의 정밀도나 mass/friction variation이 주요 연구 대상이 아닌 경우가 많다고 설명한다.

### 3.2. RL benchmark로서의 pushing

Multi-goal RL, imitation learning, vision-touch multimodal learning 등의 benchmark로 pushing을 사용하는 연구가 있지만, object shape·size·friction variation이 제한된 단순 환경이 많다고 지적한다.

### 3.3. Pushing 자체를 주요 과업으로 다루는 연구

분석적 방법부터 data-driven/RL까지 다양한 pushing 연구가 있으며, clutter traversal이나 upright pushing처럼 다른 목표가 많다. 저자들은 본 연구가 **precise target positioning**과 **낮은 sliding friction force** 조건에 초점을 둔다는 차이를 강조한다.

### 3.4. RNN 기반 pushing

RNN은 이전 pushing 연구에서도 사용됐지만, 저자들은 **RL과 recurrent memory를 결합했을 때 작은 sliding friction force에서 precise control이 개선되는지**를 직접 비교하는 연구는 부족하다고 설명한다.

## 4. 시스템 구성

### 4.1. Robot

- **Robot:** Franka Emika Panda
- **DOF:** 7
- **End-Effector:** grasping hand 대신 push rod 사용
- **Task:** table 위 물체의 planar pushing

### 4.2. Camera

Camera는 **glass table 아래** 설치된다. object와 goal을 지속적으로 볼 수 있도록 occlusion을 의도적으로 제거한 setup이다. RGB 영상은 color filtering으로 64×64 binary image로 변환된다. [원문 §III, §IV-A]

이 setup은 실험상 observation을 안정화하지만, 저자들은 Discussion에서 **항상 fully observable한 환경은 비현실적인 가정**이라고 직접 인정한다.

### 4.3. Simulation

- Gymnasium 기반 custom environment
- MuJoCo physics engine
- simulation에서 policy를 안전하게 학습
- 이후 실물 Panda setup으로 transfer

## 5. 전체 Model Architecture

Fig. 2의 흐름은 다음과 같다.

1. camera RGB에서 current object image와 goal image 획득
2. color filtering → 64×64 binary mask
3. 사전 학습한 autoencoder encoder로 각각 6D latent 생성
4. current EEF planar position 2D와 concat → 매 step 14D observation
5. episode 시작부터 현재까지 observation을 memory buffer에 저장
6. actor용 GRU와 critic용 GRU가 각각 sequence 전체 처리
7. 가장 최근 hidden state를 feature vector로 사용
8. actor/critic MLP에 전달
9. actor가 3D action $[a_x,a_y,a_s]$ 출력

Actor와 critic은 **별도 recurrent feature extractor를 사용하며 weight를 공유하지 않는다.**

## 6. Vision Representation과 Autoencoder

### 6.1. Binary object / goal image

RGB image는 color filtering을 통해 64×64 binary image로 변환된다.

Goal mask는 episode 시작 시 **object를 target position에 배치한 이미지**로 생성한다. 따라서 goal image는 episode 동안 고정된다.

Current object image는 실제 현재 object position/orientation에 따라 매 environment step 갱신된다.

### 6.2. Autoencoder

RL agent를 학습하기 전에 autoencoder를 별도로 학습한다. Training image에는 object shape, position, orientation을 randomize한다.

Encoder는

```math
z_o,z_g\in\mathbb{R}^{6}
```

의 latent representation을 만든다.

저자들은 이전 VPM 연구 [2]의 결과를 따라 6D latent dimension을 사용한다.

### 6.3. 14D 현재 observation

Planar EE position은

```math
p_e=[x_e,y_e]^T\in\mathbb{R}^{2}
```

이고, 현재 observation은

```math
s=[p_e,z_o,z_g]\in\mathbb{R}^{14}
```

로 구성된다.

정책에는 numeric object center, mass, friction coefficient가 직접 들어가지 않는다.

## 7. 왜 Memory가 필요한가

이 논문의 핵심 논리는 §IV-B에 가장 명확하게 설명된다.

Binary object image에는 object의 **mass와 friction coefficient가 나타나지 않는다.** 따라서 현재 frame만 보는 VPM은 sliding friction force를 직접 알 수 없다.

반면 object를 한 번 밀었을 때 이동 거리는 물성과 관련된 정보를 제공한다. 같은 interaction에서도 sliding friction이 작으면 object가 더 멀리 이동한다. 따라서 저자들은

**과거 EEF position + 과거 object visual latent + 현재 결과**

의 sequence에서 object의 동적 반응을 암묵적으로 학습하도록 GRU를 도입한다.

중요한 점은 이 구조가 **mass 또는 friction coefficient estimator를 명시적으로 출력하지 않는다는 것**이다. Hidden state가 정책 성능에 유용한 과거 정보를 표현하도록 end-to-end로 학습된다.

## 8. GRU Feature Extraction

Agent는 현재 시점 $T$까지의 episode 전체 observation

```math
(s_1,s_2,\ldots,s_T)
```

을 처리한다.

저자들이 entire history를 사용하는 이유는 corrective movement 때문이다.

- object와 처음 접촉하기 전까지 interaction information이 없음
- 접촉 후에야 object response에서 friction-related information을 얻을 수 있음
- overshoot correction을 위해 pusher가 object 반대편으로 이동하면 접촉이 일시적으로 사라짐
- contact-free 구간에도 이전 interaction information을 기억해야 함
- 접근/교정 시간이 상황마다 달라 fixed history length보다 variable-length recurrence가 적합

현재 시점의 GRU hidden state가 actor/critic MLP의 feature vector가 된다. Initial hidden state는 zero다.

## 9. Action Space

Action은 다음 3차원 continuous vector다.

```math
a=[a_x,a_y,a_s]^T.
```

### 9.1. Cartesian position offset

```math
a_x,a_y\in[-1,1]
```

이며 base frame x/y 방향의 desired EE position offset이다. 원문은 단위를 m로 표시한다.

### 9.2. Action duration / control-cycle count

```math
a_s\in[10,600]
```

은 같은 target offset을 적용하는 **MuJoCo simulation step 수**다.

MuJoCo control cycle은 1 ms이므로 하나의 Gymnasium environment step 동안 action을 유지하는 시간은 $a_s$에 의해 결정된다.

따라서 $a_s$는 단순한 세 번째 spatial displacement가 아니다. 이는

- 다음 policy observation을 언제 받을지
- controller가 target position으로 수렴할 시간을 얼마나 줄지

를 agent가 선택하게 한다.

저자들은 RL에서 중요한 manual tuning parameter였던 action duration을 action space에 포함하여 delayed-reward 문제의 tuning 부담을 줄이려 한다.

## 10. Low-Level Velocity Controller

RL policy에는 push rod를 table에 수직으로 유지하는 orientation constraint를 학습시키지 않는다.

Custom velocity controller가

- desired Cartesian $(x,y,z)$ 위치 추종
- push rod가 table에 perpendicular하도록 유지

를 담당한다.

저자들은 constraint까지 RL이 학습하게 하면 pushing 자체와 동시에 추가 조건을 배워야 해 문제가 복잡해진다고 설명한다.

따라서 결과는 **RL policy 단독의 unconstrained Cartesian control**이 아니라, task-specific low-level controller 위의 learned planar decision이다.

## 11. Reward Function

Reward는 simulator의 **ground-truth object center와 goal center**를 사용한다.

Object position과 goal position을

```math
p_o=[x_o,y_o]^T,\qquad p_g=[x_g,y_g]^T
```

라고 하면 즉시 reward는 다음과 같다.

```math
r(p_o,p_g)=\begin{cases}-1,&\|p_o-p_g\|_2\ge 0.01\ \mathrm{m}\\0,&\text{otherwise}\end{cases}
```

즉 goal에서 1 cm 이상 떨어져 있으면 step reward가 -1이고, 1 cm 미만이면 0이다.

**중요:** $p_o,p_g$의 numeric GT는 policy observation이 아니다. Actor는 6D image latent와 EE position을 사용하고, GT center는 training reward 계산에만 사용된다.

## 12. Episode Success와 Termination

Episode horizon은 항상

```math
T_{\max}=50
```

environment steps다.

Goal에 일찍 도달해도 episode를 즉시 종료하지 않는다. 마지막 step에서 object가 goal에서 1 cm 미만을 유지해야 success다.

이 설계는 policy가 target에 잠깐 들어갔다가 다시 object를 밀어내는 행동을 성공으로 인정하지 않게 한다.

이 점은 real-world evaluation에서 특히 중요하다. Stacked agent는 초반에 target에 도달한 뒤 불필요한 correction을 수행하여 다시 벗어나는 사례가 관찰된다.

## 13. Goal-Conditioned RL Objective

논문은 goal-conditioned finite-horizon MDP로 task를 정의한다. Goal $g$는 episode 시작 시 sampling되고 episode 동안 고정된다.

Policy objective는 다음과 같다.

```math
\pi_{\phi,G}^{*}:=\arg\max_{\pi}\mathbb{E}_{\pi,\rho_G}\left[\sum_{k=0}^{T_{\max}}\gamma^k r_{k+1}^{g}\right].
```

현재 environment state뿐 아니라 desired goal을 함께 condition하여 action을 선택한다.

## 14. SAC + Hindsight Experience Replay

Agent는 Stable-Baselines3의

- Soft Actor-Critic(SAC)
- Hindsight Experience Replay(HER)

를 사용한다.

HER는 replay transition의 desired goal을 다른 goal로 relabel하고 reward를 재계산한다.

본 논문에서는 중요한 구현 변경이 두 가지 있다.

1. **Observation 밖의 GT goal position도 relabel**해야 한다.
2. Goal encoding이 바뀌면 recurrent input sequence 전체가 달라지므로 **$t=1,\ldots,T$의 GRU hidden state를 모두 다시 계산**해야 한다.

따라서 off-policy recurrent agent와 HER를 단순히 그대로 결합한 것이 아니라, goal relabeling과 recurrent-state recomputation을 위해 Stable-Baselines3 implementation을 확장했다.

원문에는 총 training steps, seed 수, SAC learning rate·batch size·network hidden dimension 등의 상세 hyperparameter 표는 없다.

## 15. Domain Randomization

Episode 시작 시 object와 task 조건을 randomize한다.

### 15.1. Object parameter range

| Parameter | Range / Value |
| --- | --- |
| Shape | cylinder, cuboid |
| Cylinder radius | 0.04–0.055 m |
| Cuboid length/width | 0.05–0.11 m |
| Minimum height | 0.046 m |
| Cuboid maximum height | $\min(0.08,\text{length},\text{width})$ m |
| Cylinder maximum height | 0.055 m |
| Mass | 0.001–1.0 kg |
| Sliding friction coefficient | 0.2–1.0 |
| Torsional friction coefficient | 0.001–0.01 |
| Damping | 0.01 |
| Rolling friction coefficient | 0.0001 |

Start position, goal position, object yaw도 randomize한다.

Object orientation은 reward에 포함되지 않지만, initial yaw는

```math
[-\pi,\pi]
```

에서 uniform sampling한다.

## 16. Sliding Friction Force와 Improved Sampling

### 16.1. 왜 낮은 friction force가 어려운가

저자들이 정의한 sliding friction force는

```math
F_k=\mu_k m_o\,9.81\ \mathrm{m/s^2}.
```

$\mu_k$는 sliding friction coefficient, $m_o$는 object mass다.

Mass와 friction이 모두 작으면 물체가 작은 push에도 멀리 움직여 target을 overshoot하기 쉬우므로 가장 정밀 제어가 어려운 조건으로 본다.

### 16.2. Uniform sampling의 문제

Mass와 friction coefficient를 각각 uniform하게 뽑으면 두 변수의 곱으로 결정되는 sliding-friction distribution은 uniform하지 않는다. Fig. 3(left)에서는 작은/큰 friction-force 영역이 상대적으로 적게 샘플된다.

### 16.3. Modified exponential sampling

저자들은 mass와 friction coefficient가 friction-force scale에 곱으로 들어간다는 점을 이용하여 $\mu_k=0.4$로 고정하고 mass sampling을 변경한다.

먼저 gravity를 제외한 friction product의 범위를

```math
\tilde F_k^{\min}=m_o^{\min}\mu_k^{\min},\qquad \tilde F_k^{\max}=m_o^{\max}\mu_k^{\max}
```

으로 정의한다.

$x$는 scale parameter

```math
\beta=\frac{1}{7}
```

인 exponential distribution에서 뽑아 $[0,1]$로 clip하고, $y$는

```math
y\sim\mathrm{Bernoulli}(0.5)
```

로 뽑는다.

Mass는 다음과 같이 생성한다.

```math
m_o=\left(\frac{\tilde F_k^{\max}-\tilde F_k^{\min}}{\mu_k}\right)\left((1-x)(1-y)+xy\right)+\frac{\tilde F_k^{\min}}{\mu_k}.
```

Bernoulli 변수를 이용해 exponential sample을 양쪽 boundary로 mirror함으로써 **작은 값과 큰 값 모두를 더 자주 샘플**한다.

본 논문의 목적은 특히 작은 friction-force condition을 충분히 경험시키는 것이다.

## 17. 비교 모델

Simulation에서는 네 agent를 비교한다.

| Model | History | GRU | Improved friction sampling |
| --- | --- | --- | --- |
| VPM | 현재 observation만 | No | No |
| Stacked | 최근 5 observations concat | No | No |
| uGRU | 전체 episode history | Yes | No |
| eGRU (ours) | 전체 episode history | Yes | Yes |

모든 agent는

- 1 cm success threshold
- expanded 3D action space $[a_x,a_y,a_s]$

를 동일하게 사용한다.

따라서 original VPM 논문의 5 cm 조건과 직접 비교하는 실험이 아니라, **본 논문의 stricter setting으로 재구현한 VPM baseline**과 비교한다.

## 18. Corrective Movement 정의

저자들은 correction을 두 종류로 구분한다.

### 18.1. Overshoot correction

Time $t$에서 object가 1 cm target area 안에 있었는데 $t+1$에서 밖으로 벗어나면, 다시 target으로 밀어야 하는 correction이 발생했다고 본다.

### 18.2. Distance correction

한 step에서 object-goal distance가 증가한 뒤 episode 후반에 다시 감소하면 distance correction으로 분류한다.

즉 단순 success rate뿐 아니라 **얼마나 불필요하게 목표를 지나치거나 잘못된 방향으로 밀었는지**를 correction count로 평가한다.

## 19. Simulation 평가 조건

각 model은 **100 test episodes**에서 평가한다.

정밀 제어가 가장 어려운 작은 sliding friction 조건을 의도적으로 사용한다.

- mass: 0.001–0.01 kg
- sliding friction coefficient: 0.2–0.3
- 다른 parameter는 Table I 범위에서 uniform sampling
- unstable simulation으로 object가 사라지는 문제를 피하기 위해 minimum height를 0.052 m로 조정

정책은 deterministic evaluation을 사용하고, error bar는 SEM(Standard Error of the Mean)이다.

## 20. Simulation 결과

Fig. 5에서 전체 shape를 합한 success rate는 다음과 같이 표시된다.

| Model | Overall Success |
| --- | ---: |
| **eGRU** | **84%** |
| uGRU | 73% |
| Stacked | 76% |
| VPM | 67% |

Shape별 success rate는 그림에 다음과 같이 표시된다.

| Shape group | eGRU | uGRU | Stacked | VPM |
| --- | ---: | ---: | ---: | ---: |
| Cuboids excluding square-base | 64% | 56% | 54% | 49% |
| Square-base cuboids | 91% | 92% | 89% | 93% |
| Cylinders | 84% | 67% | 74% | 69% |

중요한 해석은 두 가지다.

첫째, 전체적으로 eGRU가 VPM보다 약 15 percentage points 높은 성공률을 보이고 correction 수가 더 적다.

둘째, **모든 shape에서 eGRU가 무조건 최고인 것은 아니다.** Square-base cuboid에서는 네 agent가 모두 매우 높고 VPM이 93%로 표시된다.

따라서 “GRU가 모든 물체에서 항상 우월하다”가 아니라, **어려운 low-friction / shape condition에서 recurrent history와 sampling 개선이 전체적인 robustness를 높인다**는 범위로 해석해야 한다.

## 21. Memory 효과와 Sampling 효과를 분리해서 읽는 법

eGRU와 VPM의 차이는 두 가지가 동시에 바뀐다.

- recurrent GRU
- improved sampling

따라서 84% vs 67% 차이를 전부 memory 효과라고 볼 수 없다.

보다 직접적인 비교는 다음과 같다.

- **VPM vs Stacked:** short fixed history의 효과
- **Stacked vs uGRU:** 5-frame concat과 recurrent full history의 차이
- **uGRU vs eGRU:** 동일 GRU 구조에서 improved friction sampling의 추가 효과

논문 결과는 recurrent memory와 sampling 개선이 둘 다 기여한다는 구조지만, 각 비교에서 성능 차이는 shape에 따라 일정하지 않다.

## 22. Real-World Setup

Simulation-trained agent를 실물 Franka Panda setup으로 옮긴다.

### 22.1. Test objects

네 개의 polystyrene object를 사용한다.

| Object | Mass | Size |
| --- | ---: | --- |
| Blue cylinder | 0.006 kg | radius 0.03 m, height 0.1 m |
| Red cylinder | 0.010 kg | radius 0.04 m, height 0.1 m |
| Green cuboid | 0.017 kg | 0.1 × 0.1 × 0.08 m |
| Yellow cuboid | 0.027 kg | 0.1 × 0.15 × 0.08 m |

가볍게 만들어 작은 friction-force condition을 의도적으로 어렵게 구성했다.

### 22.2. Evaluation protocol

각 agent는 총 **8 episodes**를 평가한다.

- 4 objects
- object당 2 episodes
- start/goal position이 주로 달라짐
- 각 episode 50 steps

실물에서는 object/goal GT center가 없기 때문에 reward를 계산하지 않는다.

**Success도 1 cm GT measurement가 아니라 visual inspection으로 판정한다.**

따라서 simulation의 1 cm quantitative criterion과 실물 success를 동일한 측정 정밀도로 해석하면 안 된다.

## 23. Real-World 결과

Fig. 7에 표시된 success rate는 다음과 같다.

| Model | Real Success |
| --- | ---: |
| **eGRU** | **87.5% (7/8)** |
| uGRU | 50% (4/8) |
| Stacked | 25% (2/8) |
| VPM | 37.5% (3/8) |

eGRU는 overshoot correction과 distance correction도 가장 적다.

저자들은 original VPM과 비교해 실물에서 success rate가 약 50 percentage points 높고, corrective movement가 약 1/3 적다고 요약한다.

### 23.1. Stacked agent의 대표 실패

Stacked policy는 episode 초반 target에 object를 잘 놓고도 남은 step에서 불필요하게 object를 다시 움직여 실패하는 경우가 관찰된다.

이 사례는 fixed short history가 단순 도달 여부만이 아니라 **“이미 충분히 도달했으며 더 건드리지 않아야 한다”는 temporal context**를 유지하는 데 부족할 수 있음을 보여 주는 저자들의 실패 분석이다.

### 23.2. Orientation behavior

흥미롭게도 reward에는 object orientation 목표가 없지만, 실물 eGRU는 object를 goal orientation 쪽으로 맞추려는 행동도 관찰되었다고 저자들이 보고한다.

이는 정량 orientation objective가 학습됐다는 증명은 아니며, 관찰된 emergent behavior 수준으로 기록한다.

## 24. Actor / Critic / Reward 정보 경계

| 구분 | 사용 정보 |
| --- | --- |
| Actor | Current EEF planar position + current object 6D visual latent + fixed goal 6D visual latent + full episode history through GRU |
| Critic | Actor와 같은 observation history를 별도 GRU로 처리 |
| Actor에 없는 정보 | Numeric object center, mass, friction coefficient, sliding friction force |
| Reward | Simulation GT object center + GT goal center |
| HER | GT goal position relabel + reward recomputation |
| Simulation evaluation | GT object-goal distance |
| Real evaluation | GT position 없음; visual inspection success |

이 논문은 asymmetric privileged critic 구조가 아니다. Actor와 critic은 별도 network지만, critic에 object GT mass/friction/pose를 추가로 넣는다는 설명은 없다.

## 25. 이 연구에서 History가 보완하는 정보의 정확한 범위

저자들은 history를 통해 **sliding friction force와 관련된 object behavior**를 추출할 수 있다고 설명한다.

그러나 다음은 구분해야 한다.

- GRU가 정확한 $\mu_k$ 또는 $m_o$를 regression한다고 검증하지 않음
- hidden state를 물성 parameter와 비교하는 probing experiment 없음
- contact force sensor를 이용하지 않음
- object response는 매 step vision으로 계속 관측됨
- 물체가 occluded된 상태에서 memory만으로 dynamics를 보완하는 실험이 아님

따라서 이 논문은 **history가 미관측 latent dynamics를 보완할 수 있다는 사례**지만, tactile/F/T history의 직접적인 증거는 아니다.

## 26. Limitation — 저자들이 직접 밝힌 한계

원문 §X에서 저자들은 다음 한계를 명시한다.

### 26.1. 단순한 object shape

Cylinder와 cuboid 두 종류만 검증한다. 특히 rectangular-base cuboid가 가장 어려운 조건으로 나타난다.

### 26.2. Fully observable environment

Glass table 아래 camera로 object를 계속 볼 수 있게 구성했으며, 저자들은 실제 환경에서는 occlusion이 발생하므로 이 가정이 비현실적이라고 설명한다.

### 26.3. Smoothness 보장 없음

Policy는 position offset을 출력하며, 생성되는 motion이 smooth하다는 보장이 없다.

### 26.4. Safety guarantee 없음

사람과 가까운 곳에서 pushing이 수행될 수 있지만 제안 방법에는 explicit safety guarantee가 없다.

### 26.5. 실물 평가의 GT 부재

§IX-B에서 실물 setup에는 GT position이 없어 reward를 계산하지 못하고 success를 visual inspection으로 판정한다고 명시한다. 이는 §X의 독립 limitation 목록은 아니지만 저자들이 직접 밝힌 evaluation constraint다.

## 27. Future Work — 저자들이 제시한 향후 연구

저자들은 §X에서 다음 후속 방향을 명시한다.

1. **Imitation learning**
   - real-world demonstration을 이용한 pushing
   - rectangular cuboid 등 어려운 사례와 더 complex shape 검토

2. **Partial observability**
   - 현재의 below-glass fully observable setup에서 벗어나 occlusion이 있는 환경 연구

3. **Smooth control**
   - $C^2$-continuous control policy 연구

4. **Safety constraints**
   - 사람 근처 또는 human collaboration 환경에서 안전 제약을 고려한 manipulation

이 항목들은 제안된 future work이며 현재 논문에서 이미 구현·검증한 결과가 아니다.

## 28. 미명시 사항과 해석 주의점

### 28.1. Tactile / F/T를 사용하지 않는다

논문에 tactile 또는 force/torque policy input이 없다. sliding friction force라는 표현을 wrist F/T measurement로 바꾸어 해석하면 안 된다.

### 28.2. Binary image와 Binary tactile을 구분해야 한다

64×64 binary image는 RGB color segmentation의 결과다. Contact 여부를 threshold한 tactile map이 아니다.

### 28.3. History는 current vision을 대체하지 않는다

GRU는 current object vision을 포함한 전체 sequence를 처리한다. 실행 중 vision을 끄거나 initial-only vision으로 동작하지 않는다.

### 28.4. 실물 success는 1 cm 계측값이 아니다

Simulation에서는 GT로 1 cm threshold를 평가하지만 실물은 육안 판정이다.

### 28.5. eGRU improvement를 memory 단독 효과로 보면 안 된다

eGRU는 GRU와 improved friction sampling을 둘 다 사용한다. Memory만의 직접 비교에는 uGRU, Stacked, VPM 관계를 함께 봐야 한다.

### 28.6. Training reproducibility

원문 8쪽에는 SAC/GRU의 전체 network·optimizer hyperparameter, seed 수, 총 training step 수가 충분히 제시되지 않는다. 공개 코드가 원문에 링크되어 있지만 이번 정독에서는 별도 검증하지 않았다.

### 28.7. Action duration의 의미

$a_s$는 velocity 또는 force magnitude가 아니라 같은 desired position offset을 유지할 **1 ms controller cycle 수**다. Environment feedback period 자체를 policy가 조절한다.

## 29. 원문 위치 안내

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 연구 문제·1 cm precision·기여 | Abstract, §I, PDF p. 1 |
| Related Works | §II, PDF pp. 1–2 |
| Panda·camera·MuJoCo setup | §III, PDF p. 2 |
| Architecture overview | Fig. 2, PDF p. 2 |
| Binary image·autoencoder·14D observation | §IV-A, PDF pp. 2–3 |
| GRU memory 동기와 구조 | §IV-B, PDF p. 3 |
| 3D action·$a_s$ | §IV-C, PDF p. 3 |
| GT reward·1 cm threshold | §IV-D, 식 (2), PDF p. 3 |
| Fixed 50-step episode | §IV-E, PDF p. 3 |
| SAC+HER modification | §V, PDF pp. 3–4 |
| Velocity controller | §VI, PDF p. 4 |
| Domain randomization | §VII, Table I, PDF p. 4 |
| Sliding friction definition·sampling | §VIII, 식 (3)–(5), Fig. 3, PDF pp. 4–5 |
| Correction 정의·simulation 평가 | §IX-A, Fig. 4–5, PDF p. 5 |
| Real setup·objects·results | §IX-B, Fig. 6–7, Table II, PDF p. 6 |
| Limitation·Future Work | §X, PDF p. 6 |

## 30. 문서 검증 범위

사용자 제공 IEEE 출판본 PDF 8쪽 전체를 텍스트와 페이지 렌더링으로 확인했다. 특히 Fig. 2의 recurrent architecture, Table I 및 식 (3)–(5)의 domain randomization/sampling, Fig. 5의 simulation success/correction 결과, Fig. 6–7과 Table II의 real-world 평가를 원문 페이지 이미지와 대조했다.

이번 작업에서는 공개 코드 실행, model 재학습, real robot 재현, YouTube 영상의 추가 행동 분석은 수행하지 않았다. 원문 PDF와 페이지 이미지는 저장소에 복제하지 않으며 DOI와 SHA-256으로 출처를 관리한다.
