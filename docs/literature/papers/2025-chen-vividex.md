# ViViDex: Learning Vision-Based Dexterous Manipulation from Human Videos — 원문 상세 정리

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 조사 · ICRA 2025 후보 선별](../reviews/2026-09-19_icra-2025-contact-sensing-screening.md#icra25-chen-vividex)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **ViViDex: Learning Vision-Based Dexterous Manipulation from Human Videos** |
| 저자 | Zerui Chen, Shizhe Chen, Etienne Arlaud, Ivan Laptev, Cordelia Schmid |
| 출판 | 2025 IEEE International Conference on Robotics and Automation (ICRA), Atlanta, USA, May 19–23, 2025, pp. 3336–3343 |
| DOI | [10.1109/ICRA55743.2025.11127358](https://doi.org/10.1109/ICRA55743.2025.11127358) |
| 원래 조사 | [ICRA 2025 후보 선별](../reviews/2026-09-19_icra-2025-contact-sensing-screening.md#icra25-chen-vividex)의 후속 원문 정독 |
| 정리일 | 2026-09-19 |
| 확인한 원문 | 사용자 제공 IEEE 출판본 PDF 8쪽 전체. 본문 §I–V, 식 (1)–(3), Fig. 1–4, Table I–VI, References [1]–[82] |
| 확인하지 않은 자료 | 프로젝트 웹사이트·코드·체크포인트·원시 실험 데이터, DexYCB/DexMV 원본 영상, 인용된 선행논문의 개별 원문, supplementary material |
| 원문 PDF SHA-256 | \`f745a7921f5601a78e3d4a7eadf2092b378d69a123b9ce0515fb75a4b8bec2c7\` |

이 문서는 첨부 출판본 자체의 human-video trajectory extraction, state-based PPO, trajectory-guided reward, privileged object-state 사용, visual-policy distillation, 3D point-cloud representation, simulation·real-robot 평가와 원문이 명시한 제약을 정리한다. 다른 연구에 대한 적용안은 포함하지 않는다.

**핵심:** ViViDex는 처음부터 privileged information 없이 RL을 학습하는 방법이 아니다. 먼저 human video에서 얻은 reference trajectory를 이용해 **robot state와 object state를 입력으로 받는 state-based PPO policy**를 video마다 학습하고, 성공 rollout을 대량 생성한다. 그 다음 rollout에서 얻은 3D scene point cloud와 robot proprioception을 사용하여 **GT object state를 입력으로 쓰지 않는 visual policy**를 BC 또는 3D Diffusion Policy로 학습한다. 따라서 최종 실행 정책의 관측과 teacher/data-generation 단계의 privileged state를 명확히 구분해야 한다. [원문 Abstract·§III-B–C, Fig. 1, PDF pp. 1–4]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 정의·기여와 Related Work |
| 3 | Human-video trajectory extraction과 retargeting |
| 4 | State-based PPO와 trajectory-guided reward |
| 5 | Trajectory augmentation |
| 6 | Visual policy와 point-cloud coordinate transform |
| 7 | Privileged information·실행 observation 경계 |
| 8 | Simulation platform·task·protocol·metric |
| 9 | State-policy ablation과 SOTA 비교 |
| 10 | Visual-policy ablation·seen/unseen generalization |
| 11 | Pour·Place-inside 결과 |
| 12 | Real-robot 데이터 수집과 결과 |
| 13–15 | Limitation·Future Work·미명시 사항 |
| 16 | 원문 위치 안내 |
| 17 | 핵심 메커니즘 요약 |

## 1. 제시하는 문제 상황

### 1.1 Human video는 풍부하지만 그대로 robot control에 쓰기 어렵다

저자들은 multi-finger dexterous manipulation을 RL로 직접 학습하면 reward engineering과 계산 자원이 많이 필요하고, reward를 높이지만 자연스럽지 않은 행동이 나타날 수 있다고 지적한다. Teleoperation demonstration은 학습 효율을 높이지만 다양한 robot demonstration을 수집하는 데 많은 사람이 필요하다. [원문 §I, PDF p. 1]

Human video는 상대적으로 풍부하지만, video에서 추정한 human hand/object trajectory는 noise가 있고 robot morphology와도 다르다. 기존 human-video 방법은 수십~수백 개 video를 필요로 하거나 **GT object CAD model·pose 같은 privileged information을 policy learning에 사용**하는 경우가 있어 real-world applicability가 제한된다고 설명한다. [원문 Abstract·§I, PDF p. 1]

### 1.2 ViViDex의 3단계 구조

ViViDex는 다음 세 단계로 구성된다.

1. **Reference trajectory extraction**
   - human video에서 hand/object trajectory 추출
   - human hand motion을 robot hand motion으로 retarget

2. **Trajectory-guided state-based RL**
   - video별로 state-based PPO policy 학습
   - robot state와 object state 사용
   - video trajectory를 reward reference로 사용해 physically plausible trajectory 생성

3. **Unified vision-based policy learning**
   - 성공한 state-policy rollout을 dataset으로 사용
   - robot proprioception + 3D scene point cloud로 action 학습
   - BC 또는 3D Diffusion Policy 사용
   - 최종 visual policy는 explicit privileged object state를 입력으로 사용하지 않음

[원문 Abstract·§I·III, Fig. 1, PDF pp. 1–4]

## 2. Related Work — 원문이 구성한 비교 구도

### 2.1 Dexterous manipulation

원문은 trajectory optimization과 data-driven learning을 큰 축으로 나눈다. Trajectory optimization은 robot/object dynamic model을 잘 정의해야 하는 반면, RL·IL은 robot data에서 직접 policy를 학습할 수 있다. [원문 §II, PDF p. 2]

RL 계열은 sample inefficiency와 reward engineering 문제가 있고, demonstration-augmented RL은 이를 완화하지만 robot demonstration 자체를 수집해야 한다. ViViDex는 human video를 trajectory/reward guidance로 사용하여 state-policy를 먼저 안정화하고 그 rollout으로 visual policy를 학습한다. [원문 §II, PDF p. 2]

### 2.2 Human video를 manipulation에 사용하는 연구

원문은 human video 활용을 크게 다음으로 구분한다.

- large-scale video에서 generic visual representation 학습
- human video에서 reward function 학습
- hand/object trajectory를 직접 추출해 dexterous policy 학습

DexMV·DexRepNet은 human video에서 demonstration을 추출하여 DAPG를 사용한다. PGDM은 human motion에서 얻은 pre-grasp를 이용해 RL을 효율화한다. ViViDex는 **trajectory-guided reward와 trajectory augmentation**으로 더 적은 video에서 복잡한 manipulation을 학습하려 한다. [원문 §II, PDF p. 2]

## 3. Reference Trajectory Extraction

### 3.1 Human hand와 object pose

Human hand pose와 shape는 MANO representation을 사용하며 hand joint의 3D location

$$
\boldsymbol{\psi}_h\in\mathbb{R}^{21\times3}
$$

로 표현한다. Human hand/object trajectory를 추출하는 전체 pose-estimation pipeline은 prior work [24]를 따른다고 설명하며, 본 논문에서 estimator architecture를 다시 상세히 제시하지 않는다. [원문 §III-A, PDF pp. 2–3]

### 3.2 Hand motion retargeting

Video length가 $T$일 때 robot joint angle $\mathbf q_r^t$를 다음 optimization으로 구한다.

$$
\min_{\mathbf q_r^t}
\sum_{t=1}^{T}
\left\|
\hat{\mathbf x}_{rj}^{t}(\mathbf q_r^t)
-
\boldsymbol{\psi}_{hj}^{t}
\right\|_2^2
+
\alpha
\left\|
\mathbf q_r^t-\mathbf q_r^{t-1}
\right\|_2^2.
$$

(원문 식 (1))

첫 항은 forward kinematics로 얻은 robot hand joint position과 human hand의 tip/middle-phalanx position을 맞추고, 두 번째 항은 joint pose의 급격한 변화를 억제한다. 원문은

$$
\alpha=4\times10^{-3}
$$

으로 설정하고 초기 robot pose $\mathbf q_r^0$를 motion limit의 mean pose로 둔다. NLopt solver로 optimization한다. [원문 §III-A, 식 (1), PDF p. 3]

이 단계에서 얻은 trajectory는 **visually plausible하지만 physically plausible하지 않을 수 있다.** 따라서 그대로 robot demonstration으로 쓰지 않고 다음 state-based RL 단계에서 물리적으로 실행 가능한 trajectory로 정제한다. [원문 §III-A, PDF p. 3]

## 4. State-based PPO Policy

### 4.1 Input과 network

State-based policy는 actor와 critic MLP로 구성되며 **robot state와 object state를 입력**으로 받고 robot control command를 출력한다. [원문 §III-B, PDF p. 3]

원문은 state-based policy의 정확한 state vector dimension이나 actor/critic별 입력 차이를 표로 제시하지 않는다. 따라서 object pose·velocity·shape 중 정확히 어떤 항목이 state vector에 포함되는지 본문 밖의 일반적인 dexterous-RL 설정으로 보완하지 않는다.

### 4.2 Reference trajectory를 reward로 사용

State policy는 human-video reference trajectory를 따라가되 simulator physics를 만족하는 motion을 찾는다. Training 중 trajectory를 **pre-grasp**와 **manipulation** 두 stage로 나누지만, test time policy execution에는 stage distinction이 없다. [원문 §III-B, PDF p. 3]

### 4.3 Pre-grasp reward

Pre-grasp에서는 physical contact 없이 human-like approach를 하도록 reference fingertip position을 따른다.

$$
R_p
=
\sum_{t=1}^{T_p}
10
\exp\left(
-10
\left\|
\mathbf x_{rt}^{t}(\mathbf q_r^t)
-
\hat{\mathbf x}_{rt}^{t}
\right\|_2^2
\right).
$$

(원문 식 (2))

$\hat{\mathbf x}_{rt}^{t}$는 reference trajectory의 robot fingertip position, $\mathbf x_{rt}^{t}$는 current fingertip position이다. [원문 §III-B, 식 (2), PDF p. 3]

### 4.4 Manipulation reward

Pre-grasp configuration에 도달하면 manipulation stage로 넘어가며 hand와 object motion을 함께 constrain한다.

$$
R_m
=
\sum_{t=T_p+1}^{T_r}
\left(
\lambda_1R_m^h
+
\lambda_2R_m^o
+
\lambda_3\mathbf 1_{\mathrm{cont}}
+
\lambda_4\mathbf 1_{\mathrm{lift}}
\right).
$$

(원문 식 (3))

구성은 다음과 같다.

- $R_m^h$: robot hand motion을 reference와 가깝게 유지
- $R_m^o$: current object pose를 reference object trajectory에 맞춤
- $\mathbf 1_{\mathrm{cont}}$: object와 contact한 fingertip 수
- $\mathbf 1_{\mathrm{lift}}$: object가 table에서 lift되면 bonus

Object-motion term은 position error와 orientation angular distance를 함께 사용한다. 원문은

$$
\lambda_1=4,\quad
\lambda_2=10,\quad
\lambda_3=0.5,\quad
\alpha_1=50,\quad
\alpha_2=0.1
$$

을 명시한다. **$\lambda_4$의 수치는 본문에 별도로 기재되지 않는다.** [원문 §III-B, 식 (3), PDF p. 3]

이 구조에서 object GT trajectory는 단순 evaluation target이 아니라 **state-policy RL reward 자체에 사용**된다.

## 5. Reference Trajectory Augmentation

한 개 video trajectory만 그대로 따라가면 initial object position·rotation과 target position 변화에 일반화하기 어렵다. 저자들은 RL training 중 다음 augmentation을 적용한다.

- initial object position randomization
- initial object rotation randomization
- 그 변화에 맞춰 entire reference trajectory transform
- final object pose와 새로운 target 사이 interpolation
- corresponding hand motion도 함께 interpolate

[원문 §III-B, PDF p. 3]

이를 통해 하나의 human demonstration에서 여러 initial/target configuration을 생성한다.

## 6. Vision-based Policy

### 6.1 입력에서 explicit object state 제거

State-based policy는 robot proprioceptive state와 object state를 요구하므로 실제 환경에서 object state를 안정적으로 추정하기 어렵다. 이를 피하기 위해 visual policy는 **robot state + 3D scene point cloud**만 입력으로 받는다. [원문 §III-C, PDF pp. 3–4]

Training data는 optimized state-based policy의 successful rollout에서 생성한다. 각 rollout에서 depth camera로

$$
\mathbf{PC}_w\in\mathbb{R}^{N\times3}
$$

의 scene point cloud를 렌더링한다. [원문 §III-C, PDF p. 3]

### 6.2 Coordinate transformation

World-frame point cloud만 사용하는 대신 동일한 point cloud를 다음 coordinate frame으로 변환한다.

- world/table frame
- desired target frame
- robot palm frame
- robot fingertip frames

이를 결합한 representation은

$$
\mathbf{PC}
\in
\mathbb{R}^{N\times3(j+3)}
$$

으로 표현되며 $j$는 fingertip 수다. [원문 §III-C, Fig. 1, PDF pp. 3–4]

Target-frame transform은 policy가 target position을 더 직접적으로 인식하도록 하고, palm/fingertip coordinate transform은 fine-grained hand-object interaction feature를 강화하기 위한 것이다.

### 6.3 PointNet + BC / Diffusion Policy

Point-cloud representation은 PointNet으로 encoding한다.

- **Behavior Cloning:** transformed point cloud + robot state → action
- **3D Diffusion Policy:** PointNet 3D feature를 denoising model의 global condition으로 사용하고 Gaussian noise에서 action 복원

두 모델 모두 predicted action과 ground-truth action 사이 $\ell_2$ loss로 학습한다. [원문 §III-C, PDF p. 4]

즉 최종 visual policy는 PPO가 아니라 **supervised imitation/distillation policy**다.

## 7. Privileged Information과 실행 Observation의 경계

### 7.1 State-based teacher

State-based PPO는 robot state와 object state를 직접 입력받으며, reward에도 current/reference object pose가 들어간다. 따라서 이 단계는 **privileged object state를 적극적으로 사용하는 training stage**다. [원문 §III-B, 식 (3), PDF p. 3]

### 7.2 Visual student

Visual policy는 explicit GT object pose나 CAD model을 policy input으로 사용하지 않고 다음을 받는다.

- robot joint/proprioceptive state
- depth-camera 3D scene point cloud
- task target에 대한 coordinate transform

따라서 explicit object Pose·Shape parameter는 최종 policy input에서 제거된다. 다만 **scene point cloud를 매 실행 step에 받으므로 object geometry와 현재 spatial configuration에 대한 online visual information은 계속 존재한다.** Initial-only vision이나 blind manipulation으로 분류하지 않는다. [원문 §III-C, §IV-E, PDF pp. 3–4, 6]

### 7.3 Visual policy 학습 데이터에도 teacher privilege가 간접적으로 남는다

Visual policy의 action label은 privileged state policy가 성공한 rollout에서 생성한다. 즉 deployment input에는 GT object state가 없지만, 학습 dataset의 action supervision은 **privileged teacher가 생성한 physically plausible behavior**를 사용한다. [원문 Abstract·§III-C, Fig. 1, PDF pp. 1, 3–4]

## 8. Experimental Setup

### 8.1 Video dataset와 object

DexYCB에서 다음 5개 object를 사용한다.

- mustard bottle
- tomato soup can
- sugar box
- large clamp
- mug

Object마다 3개 video를 선택해 총 15개 video를 visual-policy training에 사용한다. [원문 §IV-A, PDF p. 4]

10개 unseen object도 평가한다.

- master chef can
- tuna fish can
- pudding box
- gelatin box
- potted meat can
- banana
- pitcher base
- bleach cleanser
- wood block
- foam brick

[원문 §IV-A, PDF p. 4]

### 8.2 Protocol #1 / #2

**Protocol #1**
- object별 separate policy
- Figure 2 첫 번째 row의 initial pose 사용
- novel placement에서 평가

**Protocol #2**
- 5개 object를 하나의 unified policy로 학습
- object마다 3개 pose 사용
- 10개 unseen object generalization 평가

[원문 §IV-A, PDF p. 4]

### 8.3 Simulation platform

| 목적 | Robot | Simulator |
| --- | --- | --- |
| Prior-work state-policy 비교 | Adroit hand | MuJoCo |
| Visual-policy training·ablation | Allegro hand + UR5 arm | SAPIEN |
| Real robot | Allegro hand + UR5 arm | 실제 환경 |

[원문 §IV-A, PDF p. 4]

저자들은 Adroit+MuJoCo benchmark setup은 hand가 arm에 붙지 않고 free motion하므로 **less realistic**하다고 명시한다. 이를 보완하기 위해 실제 hardware와 유사한 Allegro+UR5 SAPIEN setup을 사용한다. [원문 §IV-A, PDF p. 4]

### 8.4 Tasks

- **Relocate:** object를 target position으로 이동
- **Pour:** particle이 든 mug를 grasp해 container에 붓기
- **Place inside:** banana를 grasp해 mug 안에 넣기

Pour는 container 안 particle percentage, place-inside는 mug 내부 banana mesh percentage로 success를 계산한다. [원문 §IV-A, PDF p. 4]

## 9. Evaluation Metric과 Implementation

### 9.1 Relocate metric

Relocate는 기존 연구를 따라 10 cm threshold success $SR_{10}$을 사용하고, 더 엄격한 3 cm threshold $SR_3$도 추가한다. [원문 §IV-A, PDF p. 4]

State-based policy에는 reference trajectory fidelity도 평가한다.

- $E_o$: average object-position trajectory error
- $E_h$: average fingertip-position trajectory error
- $SR_o$: $E_o<1$ cm인 timestep fraction
- $SR_h$: $E_h<5$ cm인 timestep fraction

[원문 §IV-A, PDF p. 4]

### 9.2 Training

| 항목 | 원문 설정 |
| --- | --- |
| State-based RL | PPO |
| State-policy training | video당 single A100에서 약 2 h |
| Successful rollout | video당 100 trajectory |
| Visual-policy data | 15 video에서 생성한 rollout |
| BC training | single A100에서 약 10 h |
| Diffusion training | single A100에서 약 20 h |
| Test | initial configuration을 바꿔 300 episode 평균 |
| Episode length | relocate 60, place-inside 80, pour 100 |

[원문 §IV-A, PDF pp. 4–5]

## 10. State-based Policy 결과

### 10.1 Hand reward ablation

Table I의 Allegro/Protocol #1 결과는 다음과 같다.

| Condition | Pre-grasp hand reward | Manipulation hand reward | $E_o$ | $E_h$ | $SR_o$ | $SR_h$ | $SR_3$ |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| R1 | × | ✓ | 0.048 | 0.21 | 0.35 | 0.00 | 0.00 |
| R2 | ✓ | × | 0.0033 | 0.077 | 0.95 | 0.32 | 1.00 |
| R3 | ✓ | ✓ | **0.0019** | **0.032** | **0.97** | **0.79** | **1.00** |

[원문 Table I, Fig. 3, §IV-B, PDF pp. 4–5]

저자들은 pre-grasp hand reward가 없으면 stable pre-grasp에 도달하기 어렵고, manipulation 중 hand reward가 없으면 object target은 달성해도 unnatural hand action이 나타날 수 있다고 설명한다. 두 stage 모두 human-hand trajectory guidance를 쓰는 R3가 가장 자연스럽고 안정적이다. [원문 §IV-B, Fig. 3, PDF p. 5]

### 10.2 State-of-the-art comparison

Table II에서 ViViDex state policy는 object당 **human video 1개**만 사용하고 Adroit와 Allegro 모두 5개 object의 $SR_{10}$·$SR_3$에서 1.00을 기록한다. [원문 Table II, PDF p. 5]

반면 DexMV 계열은 약 97 video/object를 사용하는 조건이 있으며, 저자들이 20 video/object로 retrain한 DAPG baseline은 일부 complex shape에서 성능이 크게 낮아진다. [원문 Table II, §IV-B, PDF p. 5]

Rotation augmentation을 제거한 Allegro S8도 평균 $SR_{10}=0.96$, $SR_3=0.94$를 유지한다. [원문 Table II, PDF p. 5]

이 결과는 simulation state-policy benchmark이고 final visual policy나 real-robot success와 구분한다.

## 11. Visual Policy 결과

### 11.1 Object별 separate visual policy

Protocol #1 relocate $SR_3$:

| Model | Point count | Average $SR_3$ |
| --- | ---: | ---: |
| BC | 512 | 0.86 |
| BC | 2048 | 0.96 |
| 3D Diffusion Policy | 2048 | **0.99** |

[원문 Table III, §IV-C, PDF p. 5]

Point density를 512→2048로 늘리면 BC 성능이 개선되고, 2048-point diffusion policy가 BC보다 더 robust한 결과를 보인다. Visual policy는 state policy보다 약간 낮지만 높은 성능을 유지한다. [원문 §IV-C, PDF p. 5]

### 11.2 Unified multi-object policy

Protocol #2 결과:

| Model | Videos | Target frame | Hand frames | Seen avg. | Unseen avg. |
| --- | --- | --- | --- | ---: | ---: |
| V4 BC | $1\times5$ | × | × | 0.34 | 0.31 |
| V5 BC | $2\times5$ | × | × | 0.54 | 0.33 |
| V6 BC | $3\times5$ | × | × | 0.81 | 0.38 |
| V7 BC | $3\times5$ | ✓ | × | 0.95 | 0.37 |
| V8 BC | $3\times5$ | ✓ | ✓ | 0.97 | 0.41 |
| V9 Diffusion | $3\times5$ | ✓ | ✓ | **0.99** | **0.50** |

[원문 Table IV, §IV-C, PDF p. 6]

Video 수를 늘리면 seen/unseen 성능이 전반적으로 개선된다. Target-coordinate transform은 seen-object performance를 크게 높이고, hand-coordinate transform은 fine-grained hand-object interaction feature를 추가해 unseen generalization도 개선한다. Diffusion Policy는 unseen success를 BC V8의 0.41에서 0.50으로 높인다. [원문 §IV-C, PDF p. 6]

## 12. Pour / Place-inside 결과

Table V에서 state policy L5와 visual diffusion policy L6는 human video를 task당 1개만 사용한다.

| Method | Training | Videos pour / place | Pour | Place inside |
| --- | --- | --- | ---: | ---: |
| DexMV best reported | DAPG | 101 / 91 | 0.27 | 0.31 |
| ViViDex state | PPO | 1 / 1 | **0.97** | **0.68** |
| ViViDex visual | Diffusion | 1 / 1 | **0.97** | **0.68** |

[원문 Table V, §IV-D, PDF p. 6]

이 결과는 Adroit-hand simulation 결과다. Real robot에서는 relocate task만 정량 평가한다.

## 13. Real-world Experiments

### 13.1 Hardware

| 항목 | 원문 설정 |
| --- | --- |
| Arm | UR5 |
| Hand | Allegro |
| Camera | RealSense D435 RGB-D 1대 |
| Training data | object당 real robot trajectory 5개 |
| Quantitative task | relocate |
| Trial | object당 10 episode |
| Seen object | 5개 |
| Unseen object | cracker box, spray bottle, bleach cleanser, water bottle, pudding box |

[원문 §IV-E, Fig. 4, Table VI, PDF p. 6]

### 13.2 Real policy는 zero-shot sim-to-real이 아니다

저자들은 real-world point cloud가 simulation보다 noisy하므로 **real environment에서 새로운 training data를 수집**한다. State-based policy를 simulator에서 특정 object location에 대해 실행하고, real robot에는 object를 동일 location에 놓아 corresponding robot execution을 수행하여 3D scene point cloud와 robot state를 수집한다. Object마다 5 trajectory를 모아 visual policy를 새로 학습한다. [원문 §IV-E, PDF p. 6]

논문은 이 절차를 “simulator-trained visual policy를 그대로 실물로 옮긴 zero-shot transfer”로 주장하지 않는다.

실물에서 state-based teacher 실행에 **real-time GT object state를 직접 입력하는지, 아니면 simulator에서 생성한 command/trajectory를 재생하는지**는 해당 문단만으로 명확히 설명되지 않는다. 이 부분을 임의로 보완하지 않는다.

### 13.3 Table VI

| Method | Unified | Seen avg. | Unseen avg. |
| --- | --- | ---: | ---: |
| R1 BC | × | **0.88** | — |
| R2 BC | ✓ | 0.72 | 0.58 |
| R3 Diffusion | ✓ | **0.80** | **0.68** |

[원문 Table VI, §IV-E, PDF p. 6]

Separate BC는 seen objects에서 가장 높은 0.88을 기록하지만 unseen generalization을 평가하지 않는다. Unified diffusion policy는 unified BC보다 seen·unseen 모두 높다. [원문 §IV-E, PDF p. 6]

## 14. Limitation — 저자들이 밝힌 범위와 제약

논문에는 독립된 “Limitations” 절이 없다. 다만 본문에서 다음 제약을 직접 언급한다.

### 14.1 State-based policy의 object-state 의존

State policy는 robot proprioception뿐 아니라 object state가 필요하며, 저자들은 **real environment에서 object state를 reliably estimating하는 것이 non-trivial**하다고 명시한다. Visual policy를 따로 만드는 직접적인 이유다. [원문 §III-C, PDF p. 3]

### 14.2 Human-video trajectory 자체는 noisy하다

Video에서 추출한 robot/object reference trajectory는 visually plausible하지만 **direct robot control에 사용할 만큼 physically plausible하지 않을 수 있다.** State-based RL refinement가 이를 보완한다. [원문 §I·III-A, PDF pp. 1, 3]

### 14.3 Benchmark simulator의 realism

Adroit+MuJoCo setup은 hand가 arm에 연결되지 않고 freely moving하므로 저자들이 **less realistic**하다고 명시한다. 이 때문에 Allegro+UR5 SAPIEN setup도 별도로 사용한다. [원문 §IV-A, PDF p. 4]

### 14.4 Real point-cloud domain gap

Real-world point cloud는 simulation보다 noisy하므로 저자들은 **simulation visual policy를 그대로 배포하지 않고 real trajectory를 추가 수집하여 visual policy를 다시 학습**한다. [원문 §IV-E, PDF p. 6]

이는 논문의 real-world demonstration이 privileged-state-free visual inference를 보여주지만, pure simulation-only training 또는 zero-shot sim-to-real을 검증한 것은 아니라는 의미다.

## 15. Future Work — 저자들이 제시한 향후 연구

Conclusion §V에는 별도의 future-work 방향이 명시되어 있지 않다. 저자들은 ViViDex의 효과와 unseen-object generalization을 요약하지만, 구체적인 후속 연구 항목을 제안하지 않는다. [원문 §V, PDF p. 6]

“향후 tactile/F/T를 추가한다”, “online object-state estimator를 개발한다”와 같은 내용은 이 논문에서 제시하지 않으므로 Future Work로 추가하지 않는다.

## 16. 미명시 사항·원문 주의사항

| 항목 | 확인 결과·주의 |
| --- | --- |
| State-based policy의 정확한 state vector | “robot and object states”라고만 명시. pose·velocity·shape 등의 전체 구성·차원은 미명시 |
| State actor/critic의 hidden layers | MLP라고만 명시. layer size 미명시 |
| PPO hyperparameter | algorithm만 명시. learning rate, batch, clip, $\gamma$, $\lambda$ 등 미명시 |
| Manipulation reward의 $\lambda_4$ | 식 (3)에 존재하지만 numerical value 미명시 |
| Human/object pose estimator 상세 | prior work [24]를 따름. 본문에서 architecture·error statistics 미명시 |
| Object CAD model의 final visual-policy 입력 | 사용하지 않음. 3D scene point cloud를 사용 |
| Visual policy의 explicit object pose 입력 | 사용하지 않음. online point cloud는 계속 사용 |
| Point cloud N | Table III relocate ablation에서는 512/2048 point를 비교하지만 generic formulation의 $N$은 variable로 정의 |
| Control-command 22 dimension | Fig. 1에 22 dim 표시가 있으나 본문에서 Allegro+UR5의 각 component를 명시적으로 풀어 설명하지 않음 |
| PointNet architecture | 세부 layer 미명시 |
| Diffusion-policy architecture/horizon | prior work [77], [78]를 따르며 본문 세부 hyperparameter 미명시 |
| Real data collection 시 teacher 실행 방식 | simulator state policy의 motion을 real robot에 어떻게 정확히 전달하는지 상세 미명시 |
| Real visual-policy training time | 미명시 |
| Real camera calibration·depth preprocessing | 미명시 |
| Real unseen object의 training exclusion 검증 | 5개 unseen object 이름과 평가 결과는 제공되나 세부 dataset split 과정은 추가 설명 없음 |
| Tactile/F/T | ViViDex policy input에 사용하지 않음 |
| 코드·프로젝트 페이지 검증 | 이번 작업에서는 확인·실행하지 않음 |

## 17. 다시 읽을 때의 원문 위치

| 내용 | 위치 |
| --- | --- |
| 연구 동기·privileged object information 문제 | Abstract·§I, PDF p. 1 / 인쇄 p. 3336 |
| 전체 3단계 ViViDex 구조 | Fig. 1·§I·III, PDF pp. 1–2 |
| Related Work | §II, PDF p. 2 / 인쇄 p. 3337 |
| Human-video pose extraction·retargeting | §III-A, 식 (1), Fig. 2, PDF pp. 2–3 |
| State policy input·PPO teacher | §III-B, PDF p. 3 / 인쇄 p. 3338 |
| Pre-grasp reward | 식 (2), §III-B, PDF p. 3 |
| Manipulation reward·contact/lift bonus | 식 (3), §III-B, PDF p. 3 |
| Reference trajectory augmentation | §III-B, PDF p. 3 |
| Visual policy input·point-cloud transforms | §III-C, PDF pp. 3–4 |
| BC / 3D Diffusion Policy | §III-C, PDF p. 4 |
| DexYCB object·Protocol #1/#2 | §IV-A, PDF p. 4 / 인쇄 p. 3339 |
| Adroit MuJoCo / Allegro+UR5 SAPIEN | §IV-A, PDF p. 4 |
| Task·metric·training time | §IV-A, PDF pp. 4–5 |
| State reward ablation | Table I, Fig. 3, §IV-B, PDF pp. 4–5 |
| State-policy SOTA comparison | Table II, §IV-B, PDF p. 5 / 인쇄 p. 3340 |
| Separate visual-policy result | Table III, §IV-C, PDF p. 5 |
| Unified visual-policy ablation | Table IV, §IV-C, PDF p. 6 / 인쇄 p. 3341 |
| Pour·place-inside | Table V, §IV-D, PDF p. 6 |
| Real robot setup·data collection | §IV-E, Fig. 4, PDF p. 6 |
| Real robot result | Table VI, §IV-E, PDF p. 6 |
| Conclusion | §V, PDF p. 6 |

PDF pp. 7–8은 References다.

## 18. 핵심 메커니즘 요약

ViViDex의 핵심은 **privileged state RL과 deployable visual policy를 한 정책에 섞지 않고 단계적으로 분리**하는 것이다.

먼저 noisy human-video trajectory를 robot morphology에 retarget한 뒤, object state를 직접 볼 수 있는 simulator에서 PPO teacher를 학습한다. Teacher는 human hand/object trajectory를 reward reference로 사용하면서 physics를 만족하는 성공 behavior를 생성한다. 다음 단계에서는 이 성공 rollout을 **action-labeled visual dataset**으로 바꾸고, robot proprioception과 3D point cloud만 받는 BC/Diffusion Policy를 학습한다.

따라서 최종 visual policy에는 GT object pose가 직접 들어가지 않지만, **매 step의 scene point cloud를 통해 object geometry·pose 변화에 해당하는 visual information을 계속 관측**한다. 또한 training data 자체는 privileged object-state teacher에서 생성된다. 이 때문에 ViViDex는 privileged information의 **training/deployment 분리**를 보여주는 좋은 사례이지만, object state가 initial-only인 blind/contact-driven policy의 사례는 아니다.

Real robot에서도 visual policy는 object당 5개의 real trajectory를 추가로 사용해 학습하므로, 논문의 real-world 결과는 **privileged-state-free visual execution**을 보여주지만 zero-shot sim-to-real을 증명하는 결과는 아니다.
