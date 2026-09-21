# Unknown Object Retrieval in Confined Space through Reinforcement Learning with Tactile Exploration

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [원래 ICRA 2024 선별 항목](../reviews/2026-09-19_icra-2024-contact-sensing-screening.md#icra24-zhao-unknown-object-retrieval)

## 1. 논문 정보와 확인 범위

- **제목:** Unknown Object Retrieval in Confined Space through Reinforcement Learning with Tactile Exploration
- **저자:** Xinyuan Zhao, Wenyu Liang, Xiaoshi Zhang, Chee Meng Chew, Yan Wu
- **게재:** 2024 IEEE International Conference on Robotics and Automation (ICRA 2024), Yokohama, Japan, May 13–17, 2024, pp. 10881–10887
- **DOI:** [10.1109/ICRA57147.2024.10611541](https://doi.org/10.1109/ICRA57147.2024.10611541)
- **확인 원문:** 사용자 제공 IEEE 출판본 PDF 7쪽 전체
- **파일 SHA-256:** 31da048fe529c15b8a4887eecac4bb35bf7820aa853f1290f230515962f47ca8
- **확인하지 않은 자료:** supplementary video, 저자 코드, 실제 학습 로그·replay buffer, Stable-Baselines3 실행 설정 전체는 이번 정독에서 별도 확인하지 않음

이 논문은 시각이 가려지는 좁은 공간에서 **tactile-sensorized tool stick**으로 미지 물체를 밖으로 밀어내는 실물 강화학습 방법을 제안한다. 핵심은 물체 형상·질량·마찰계수 등의 사전 정보를 입력하거나 상호작용 동역학을 명시적으로 추정하지 않고, **저차원으로 축약한 tactile force feature만을 정책 observation으로 사용**해 물체 retrieval 행동을 학습하는 것이다. [원문 Abstract, §I, §III-B]

다만 “tactile-only”라는 표현은 **실행 정책의 observation**에 관한 것이다. 학습 중에는 OptiTrack으로 측정한 물체의 전진 변위를 reward 계산에 사용한다. 평가 단계에서는 OptiTrack 없이 tactile input만으로 실행한다. 따라서 실행 관측과 학습용 supervision/reward signal을 구분해야 한다. [원문 §III-B.3, §IV-A]

## 2. 초록과 연구 목표

저자들이 대상으로 삼는 문제는 지갑이 좁은 틈에 빠진 상황처럼, RGB-D camera나 motion capture로 물체를 안정적으로 관측하기 어렵고 일반 gripper가 들어가기에도 공간이 부족한 **confined-space object retrieval**이다.

이를 위해 20 cm 길이의 얇은 tool stick 끝에 tactile sensor를 부착하고, 실시간 multi-point contact measurement를 이용한다. RL agent는 물체의 기하·재질·질량·마찰 등 physical property를 사전에 알지 못한 상태에서 retrieval policy를 학습한다.

실제 tactile sensor와 변형 가능한 일상 물체를 정확히 simulation하는 것이 어렵다는 이유로 학습을 실물 로봇에서 직접 수행한다. 이 때문에 sample efficiency와 hardware wear가 큰 문제가 되고, 이를 줄이기 위해 다음 세 요소를 제안한다. [원문 §I]

1. **Focused training:** cuboid와 cylinder 두 대표 형상군만 실물에서 학습하고 다른 일상 물체로 일반화
2. **Hybrid action space:** 일반 Cartesian displacement와 parameterized backward-adjustment primitive를 결합
3. **Terminal-goal curriculum:** 처음에는 짧은 retrieval 거리부터 시작하고 성공할 때마다 목표 거리를 증가

## 3. 제시하는 문제 상황과 가정

### 3.1. 왜 vision이 아니라 tactile인가

저자들은 confined space에서 unavoidable occlusion 때문에 conventional visual perception이 불안정하다고 설명한다. 또한 공간 제약 때문에 gripper 자체가 들어가기 어려울 수 있다. 따라서 사람처럼 막대형 도구를 이용해 접촉하면서 물체를 이동시키는 설정을 선택한다. [원문 §I]

이 논문은 vision 전체를 부정하는 연구가 아니다. **조작 실행 중 정책 observation을 tactile로 제한**하는 문제를 다룬다. 학습 reward에는 OptiTrack을 사용하며, searching phase는 범위 밖이다.

### 3.2. 물체 사전정보에 대한 가정

저자들은 기존 tactile manipulation 연구의 일부가 object geometry, friction coefficient 등의 사전 지식을 가정한다고 지적한다. 본 연구는 retrieval 과정에서 다음 정보를 policy에 직접 제공하지 않는다.

- object geometry
- weight
- material
- friction coefficient
- explicit interaction dynamics model
- object pose

대신 tactile interaction pattern과 reward의 관계를 RL이 암묵적으로 학습하도록 한다.

### 3.3. 범위 밖의 문제

원문은 **물체가 이미 성공적으로 위치 파악된 상태라고 가정**하며, 별도의 searching phase 구현은 연구 범위 밖이라고 명시한다. 즉 미지 물체를 어디서 찾을지까지 tactile exploration으로 해결하는 연구가 아니다. [원문 §III-B]

## 4. Related Works의 비교 구도

원문 §II는 다음 네 축으로 선행연구를 비교한다.

### 4.1. Tactile state estimation 기반 manipulation

- Cable manipulation에서는 tactile image로 cable pose와 frictional force를 추정해 sliding/re-grasping controller를 구동
- Tactile tool manipulation에서는 tool/object pose를 추정하지만 friction coefficient의 완전한 사전 지식을 가정
- Planar pushing에서는 tactile high-frequency component로 sliding/slipping을 구분
- Goal-driven pushing에서는 tactile로 relative pose를 추정하여 unknown object pushing을 수행

이 계열과 달리 본 논문은 **interaction dynamics나 object state를 명시적으로 추정하지 않고**, 저차원 tactile feature에서 직접 action policy를 학습한다.

### 4.2. Fixed motion primitive 기반 tactile manoeuvre

밀집 clutter에서 고정 방향 primitive를 사용하는 tactile-reactive manoeuvre는 효과적이지만, 저자들은 parameterized primitive가 없으면 다양한 상황에 적응하기 어렵다고 본다.

### 4.3. Primitive-only hierarchical policy의 한계

행동 primitive repertoire만 탐색하도록 제한하면 human-engineered primitive의 bias 때문에 sub-optimal solution에 머물 수 있다고 설명한다. 그래서 본 논문은 **continuous displacement action + parameterized primitive**를 함께 사용한다.

### 4.4. Curriculum RL

Unknown-geometry peg insertion 등에서 task difficulty curriculum이 학습을 빠르게 할 수 있다는 선행 결과를 바탕으로, 본 논문은 **terminal retrieval distance 자체를 curriculum 변수로 사용**한다.

## 5. 하드웨어와 실험 시스템

### 5.1. Robot과 Tool

- **Robot:** 7-DoF KUKA iiwa LBR 14 R820
- **Tool:** 3D-printed tool stick, 길이 20 cm
- **용도:** 좁은 공간 안으로 들어가 물체를 접촉·이동
- **제어:** robot의 positional servo control 사용

원문은 iiwa의 high-performance positional servo control이 섬세한 tactile-reactive interaction에 적합하다고 설명한다.

### 5.2. Tactile Sensor

- **제품:** XELA Robotics uSPa44
- **원리:** magnetic-based tactile sensor
- **배열:** 4 × 4 taxel
- **taxel당 channel:** 3축
  - normal force 1축
  - shear force 2축
- **sampling / processing rate:** 100 Hz
- **특징:** impact와 반복 wear에 강하다고 설명

즉 한 시점의 raw tactile force는 구조적으로 16 taxel × 3축에 해당하지만, policy가 이를 그대로 사용하는 것은 아니다.

원문은 제조사 force range, force resolution, accuracy, taxel pitch, sensor 면적을 제시하지 않는다. 100 Hz를 제외한 이러한 사양은 이번 원문만으로 확정하지 않는다.

## 6. Raw Tactile → 9D Observation으로의 축약

### 6.1. Observation 정의

정책 observation은 다음과 같이 정의된다. [원문 §III-B.1]

```math
s=[f_n,f_x,\mu_{\mathrm{FFT}}]\in\mathbb{R}^{9}.
```

여기서

```math
f_n=[f_{n,1},\ldots,f_{n,4}]\in\mathbb{R}^{4}
```

이고,

```math
f_x=[f_{x,1},\ldots,f_{x,4}]\in\mathbb{R}^{4}.
```

따라서 observation은 4 + 4 + 1 = 9차원이다.

### 6.2. Normal-force feature

$f_{n,i}$는 tactile array의 **i번째 column에 존재하는 normal-force measurement 중 최댓값**이다.

즉 4×4 전체 normal-force distribution을 그대로 보존하지 않고, 각 column별 max pooling에 가까운 축약을 수행한다. 이 결과 세로 방향 세부 contact location은 제거되고, column 단위의 횡방향 접촉 분포와 force magnitude가 남는다.

### 6.3. x-shear feature

$f_{x,i}$는 i번째 column의 x-axis shear force 중 **절댓값이 가장 큰 taxel의 shear value**다.

따라서 x-shear 역시 column별 대표값 4개로 축약된다.

### 6.4. y-shear는 observation에 명시적으로 포함되지 않는다

uSPa44는 두 shear axis를 측정하지만, 원문 observation에는 normal force와 **x-axis shear**만 들어간다. y-axis shear를 별도 feature로 사용하는 내용은 없다.

### 6.5. High-frequency slip-related feature

slippage detection 선행연구에서 영감을 받아, x-axis shear force의 high-frequency component를 observation에 추가한다.

$\mu_{\mathrm{FFT}}$는 **32-sample window**에서 FFT를 계산하고, **30 Hz를 초과하는 frequency component들의 평균**으로 정의된다. 원문은 이를 potential slippage event를 자동으로 포착하기 위한 feature로 설명한다.

FFT window의 overlap, window function, spectrum magnitude/energy의 정확한 정의, 여러 taxel의 shear를 어떻게 하나의 $\mu_{\mathrm{FFT}}$로 합치는지의 구현 세부는 원문에 충분히 명시되지 않는다.

## 7. Observation에서 명시적으로 제외된 정보

실행 중 SAC policy observation은 tactile feature 9차원으로 정의된다. 다음 정보가 actor observation에 포함된다는 설명은 없다.

- robot joint position / velocity
- EEF position
- object pose
- object velocity
- geometry class
- weight / material
- friction coefficient
- OptiTrack measurement

따라서 이 논문의 policy는 **proprioception까지 포함한 multimodal policy가 아니라 tactile feature only policy**로 읽는 것이 맞다.

다만 저수준 robot controller는 action을 실제 EEF displacement로 실행하기 위해 robot state를 내부적으로 사용할 수밖에 없으며, 이것과 RL observation을 구분한다.

## 8. Hybrid Action Space

정책 action은 다음 3차원으로 정의된다. [원문 §III-B.2]

```math
a=[a_x,a_y,a_p]\in\mathbb{R}^{3}.
```

### 8.1. Continuous displacement

- $a_x$: intended retrieval direction의 horizontal EE displacement
- $a_y$: retrieval direction에 수직한 horizontal EE displacement

즉 일반적인 평면 이동은 두 continuous action이 담당한다.

### 8.2. Parameterized backward-adjustment primitive

$a_p$는 backward adjustment primitive의 parameter다.

- $a_p\leq 0$: primitive를 사용하지 않고 $a_x,a_y$에 따른 displacement 실행
- $a_p>0$: $a_x,a_y$를 무시하고 predefined backward-adjustment sequence 실행
- backward step의 거리는 $a_p$에 따라 결정

이 primitive는 cylindrical/rolling object를 조작하다 contact를 잃었을 때 **도구를 뒤로 움직여 contact location을 다시 구성하고 재접촉**하는 데 사용된다.

즉 action space는 순수 continuous Cartesian action도 아니고, discrete primitive-only space도 아니다.

## 9. Action Scaling

SAC가 출력하는 세 action component는 모두 $[-1,1]$로 normalize된다.

실행 전 다음 scaling을 적용한다.

```math
\alpha_a=[\alpha_{a,x},\alpha_{a,y},\alpha_{a,p}]=[0.5,0.2,30]\ \mathrm{mm}.
```

따라서 최대 scale은

- x displacement: 0.5 mm
- y displacement: 0.2 mm
- backward-adjustment primitive parameter: 30 mm

이다.

원문에는 RL action command frequency와 각 action이 완료될 때까지 걸리는 실제 시간의 명확한 수치가 없다. 따라서 mm 단위 scaling을 별도 근거 없이 velocity 단위로 변환하지 않는다.

## 10. Reward Function

전체 reward는 다음 다섯 항의 합이다. [원문 식 (1)]

```math
r=r_t+r_o+r_f+r_g+r_p.
```

## 10.1. Time penalty $r_t$

매 timestep마다 task completion을 빠르게 하기 위한 negative reward를 준다.

Table I의 값은

```math
r_t=-0.1.
```

Backward primitive를 사용할 때에는 primitive 전체를 단일 timestep으로 싸게 처리하지 않고, 같은 이동을 $a_x,a_y$만으로 수행했을 때 필요한 equivalent timestep 수에 따라 time penalty를 계산한다.

## 10.2. Object forward progress reward $r_o$

```math
r_o=\alpha_{r,o}d_o.
```

- $d_o$: 현재 timestep에서 object가 intended retrieval direction으로 이동한 거리
- $\alpha_{r,o}=5.0$

여기서 **$d_o$는 OptiTrack으로 측정**한다.

이 값은 policy observation에는 들어가지 않고 **학습 중 reward 계산에만 사용**된다. 평가에서는 OptiTrack을 제거하고 tactile observation만 사용한다.

## 10.3. Force-regulation reward $r_f$

원문 식 (3)은 maximum normal tactile force $f_n^{\max}$에 대해 세 구간을 정의한다.

```math
r_f=\begin{cases}0,&f_n^{\max}<f_n^{l}\\r_f^{h},&f_n^{\max}>f_n^{h}\\(f_n^{\max}-f_n^{l})^2,&\text{otherwise}\end{cases}
```

Table I의 parameter는 다음과 같다.

- $f_n^{l}=0.2$ N
- $f_n^{h}=1.5$ N
- $r_f^{h}=-10.0$

저자들의 설명은 다음과 같다.

- 너무 작은 contact force에서는 reward를 주지 않는다.
- $f_n^l>0$를 두어 agent가 interaction을 포기하는 local minimum으로 가는 것을 방지한다.
- $f_n^{\max}>f_n^h$이면 modest penalty를 부여하고 robot이 press를 release하여 $f_n^{\max}$를 $f_n^l$까지 낮춘다.
- 중간 범위에서는 $(f_n^{\max}-f_n^l)^2$이 reward가 된다.

즉 contact를 완전히 줄이는 방향이 아니라, 일정 contact force를 유지하되 upper threshold를 넘는 과도한 press는 별도 release logic으로 완화한다.

## 10.4. Terminal goal reward $r_g$

```math
r_g=\alpha_{r,g}d_g.
```

- $\alpha_{r,g}=2.0$
- $d_g$: episode 성공으로 인정하기 위해 object가 초기 위치에서 전진해야 하는 terminal distance

이 reward는 goal을 달성했을 때만 큰 positive reward로 발행된다.

## 10.5. Primitive-failure penalty $r_p$

Backward adjustment primitive를 실행한 뒤 일정 시간 안에 object와 contact를 다시 만들지 못하면 primitive failure로 보고 penalty를 준다.

Table I:

```math
r_p=-10.0.
```

재접촉 판정에 사용하는 정확한 time window와 contact threshold의 구현 세부는 원문에 명시되지 않는다.

## 11. Terminal-goal Curriculum

초기 terminal goal은

```math
d_g^l=20\ \mathrm{mm}
```

이고, 최대 goal은

```math
d_g^h=50\ \mathrm{mm}.
```

Agent가 현재 goal을 달성할 때마다 $d_g$를 **1 mm씩 증가**시키며 최종적으로 $d_g^h$까지 올린다.

저자들의 의도는 처음부터 긴 retrieval을 요구하지 않고, 짧은 성공 경험에서 시작하여 점차 더 큰 displacement를 학습하도록 하는 것이다.

이 curriculum은 training reward의 terminal condition을 바꾸는 것이며, evaluation의 최종 성공 조건 100 mm와는 별개다.

## 12. SAC 구현

Motion planner는 **Soft Actor-Critic (SAC)**으로 구현한다.

- library: Stable-Baselines3
- actor: fully connected, hidden layer 2개
- critic: fully connected, hidden layer 2개
- 각 hidden layer: 256 units
- activation: ReLU
- agent implementation: Python
- environment: MATLAB
- robot/environment–agent communication: ROS topics/services

원문은 optimizer, learning rate, batch size, discount factor, replay-buffer size, target-update coefficient, entropy coefficient 등의 SAC hyperparameter를 Table I에 제시하지 않는다.

## 13. 실물 On-Hardware Training

저자들은 tactile sensor와 다양한 rigid/non-rigid daily object를 현실적으로 simulation하기 어렵다는 이유로 **실물 iiwa에서 직접 RL을 학습**한다.

### 13.1. Training object

총 8개를 사용한다.

- Obj-1–Obj-4: standard cuboid representative, 서로 다른 weight/material
- Obj-5–Obj-8: standard cylinder representative, 서로 다른 physical properties

세부 geometry, weight, material은 supplementary video로 안내하며 논문 본문 표에는 수치가 없다.

### 13.2. Focused training

하나의 policy를 처음부터 8개 object에 online 학습시키는 것이 아니라 다음 순서를 사용한다.

1. Cuboid Obj-1–4로 첫 SAC model을 실물 학습
   - 약 **125 episodes**에 convergence
2. Cylinder Obj-5–8로 두 번째 SAC model을 scratch부터 별도 학습
   - 약 **300 episodes**에 convergence
3. 두 model의 replay buffer를 merge
4. merged replay buffer로 integrated model을 **offline training**
5. integrated model을 evaluation에 그대로 사용

저자들은 이 방식으로 실물 hardware training을 **약 5시간**으로 제한했다고 보고한다.

새 test object에 대해 additional online refinement나 pre-training은 하지 않는다.

## 14. Training-time Privileged Signal과 Evaluation-time Input의 경계

이 논문의 정보 경계는 매우 명확하다.

| 단계 | Policy observation | Reward / 외부 측정 |
| --- | --- | --- |
| 실물 RL training | 9D tactile feature | OptiTrack으로 object displacement $d_o$ 측정 |
| Offline replay merge 학습 | 저장된 transition의 tactile/action/reward | 앞서 수집된 reward 사용 |
| Evaluation | tactile feature만 사용 | OptiTrack은 policy 실행에 사용하지 않음 |

따라서 다음 두 표현을 구분해야 한다.

- **맞음:** evaluation policy는 tactile input alone으로 실행된다.
- **부정확함:** training 전체가 외부 object-state measurement 없이 tactile만으로 수행된다.

OptiTrack은 actor input이 아니라 reward를 만들기 위한 training-only measurement다.

## 15. Heuristic Baseline

Baseline은 학습 기반이 아닌 rule-based planner다.

### 15.1. Force regulation

Maximum normal force $f_n^{\max}$를

```math
[f_n^l,f_n^h]
```

범위에 유지한다.

### 15.2. Forward motion

정상 contact가 형성되면 intended retrieval direction으로

```math
0.8\alpha_{a,x}
```

의 일정 command로 이동한다고 설명한다.

원문은 이를 constant speed라고 표현하지만 $\alpha_{a,x}$ 자체는 mm 단위 displacement scale로 표기되어 있다. command period가 명시되지 않으므로 이를 별도 시간 단위의 velocity로 환산하지 않는다.

### 15.3. Backward adjustment rule

다음 조건을 만족하면 backward adjustment를 실행한다.

- first column: $f_{n,1}>f_n^l$
- 나머지 column: $f_{n,i}\leq f_n^l$, $i=2,3,4$

이는 contact가 한쪽 column으로 치우친 상태를 이용한 rule이다.

RL의 parameterized primitive와 달리 baseline의 backward distance는 **10.0 mm 고정**이다.

## 16. Comparative Evaluation

### 16.1. Success definition

평가에서 task success는

- object가 **100.0 mm** 전진
- **60 s 이내**

두 조건을 만족하는 것이다.

### 16.2. 평가 object

총 20개 object/scenario를 사용한다.

- Obj-1–8: training에서 사용한 representative objects
- Obj-9–20: 완전히 새로운 test objects
- Obj-20: 다른 경우와 달리 corrugated paper 위에서 manipulation

각 object를 **5 trials**씩 평가한다.

두 planner 모두 test object의 weight, material, geometry, friction coefficient를 제공받지 않는다.

### 16.3. Success rate

Table II의 결과는 다음과 같다.

| 조건 | Proposed RL | Heuristic |
| --- | ---: | ---: |
| Test set only, Obj-9–20 | **90%** | **55%** |
| Overall, Obj-1–20 | **93%** | **58%** |

Test set만 보면 12 objects × 5 trials = 60 trials이며, proposed method가 평균적으로 훨씬 높은 성공률을 보였다.

### 16.4. Object별 결과

| Object | Ours | Heuristic |
| --- | ---: | ---: |
| Obj-1 | 5/5 | 5/5 |
| Obj-2 | 5/5 | 5/5 |
| Obj-3 | 5/5 | 0/5 |
| Obj-4 | 5/5 | 0/5 |
| Obj-5 | 5/5 | 5/5 |
| Obj-6 | 5/5 | 5/5 |
| Obj-7 | 4/5 | 5/5 |
| Obj-8 | 5/5 | 0/5 |
| Obj-9 | 5/5 | 5/5 |
| Obj-10 | 5/5 | 0/5 |
| Obj-11 | 5/5 | 5/5 |
| Obj-12 | 5/5 | 5/5 |
| Obj-13 | 4/5 | 5/5 |
| Obj-14 | 5/5 | 5/5 |
| Obj-15 | 4/5 | 1/5 |
| Obj-16 | 5/5 | 2/5 |
| Obj-17 | 3/5 | 2/5 |
| Obj-18 | 5/5 | 0/5 |
| Obj-19 | 3/5 | 1/5 |
| Obj-20 | 5/5 | 2/5 |

### 16.5. Mug 사례 Obj-18

저자들은 mug가 wall과 접촉하는 방식에 따라 movement modality가 바뀌는 사례를 강조한다.

- body만 wall과 contact: 회전
- handle까지 wall에 걸림: forward sliding, 더 높은 friction

RL planner는 contact force pattern과 reward 사이의 관계를 암묵적으로 학습하여 이 변화에 적응했다고 설명한다.

Obj-18 대표 trial:

- RL: **15 s에 성공**
- heuristic: **60 s timeout으로 실패**

이 결과는 저자들의 해석상 fixed force/contact rule보다 learned tactile policy가 interaction mode 변화에 더 잘 대응했음을 보여 주는 사례다.

## 17. Ablation — Parameterized Action Primitive

Backward primitive를 제거하고 cylinder Obj-5–8에 대해 다시 학습한다.

원문은 primitive가 없는 model이 proposed RL보다 현저히 낮은 reward를 보이며, **backward movement로 contact location을 재구성하는 행동을 스스로 획득하지 못했다**고 설명한다.

그 결과 policy가 오히려 object interaction을 최소화하는 쪽으로 수렴했고, cylinder training objects를 대상으로 한 evaluation trial에서 모두 실패했다.

즉 저자들의 결과에서 continuous $a_x,a_y$만으로 충분한 exploration이 일어나지 않았으며, task-specific primitive가 contact recovery에 강한 inductive bias를 제공했다.

## 18. Ablation — Terminal-goal Curriculum

Curriculum을 제거한 model은 처음부터

```math
d_g=d_g^h=50\ \mathrm{mm}
```

로 학습한다.

첫 terminal success까지 필요한 timestep은 다음과 같다.

- Proposed curriculum: 약 **17,000 timesteps**
- Without curriculum: 약 **50,000 timesteps**

또한 no-curriculum policy는 네 cylinder training object 전반에 대한 generalization이 좋지 않아 학습 후반에 reward가 다시 감소했다고 저자들은 설명한다.

Fig. 8은 proposed model, without primitive, without curriculum의 reward training curve를 비교한다. 원문은 curve smoothing 방식, seed 반복 수, variance/error band를 제공하지 않는다.

## 19. 이 논문에서 tactile이 행동으로 연결되는 방식

이 논문의 sensing-to-action 구조를 요약하면 다음과 같다.

| Tactile 정보 | 축약 | 정책에 주는 의미 | Action과의 연결 |
| --- | --- | --- | --- |
| Normal force 4×4 | column별 max 4D | contact 위치의 거친 횡방향 분포 + load magnitude | forward/lateral displacement, force-reward와 간접 연결 |
| x-shear 4×4 | column별 max-absolute shear 4D | tangential interaction pattern | SAC policy의 displacement 선택 |
| x-shear time window | >30 Hz FFT component 평균 1D | slip 가능성과 관련된 high-frequency contact 변화 | SAC policy가 학습을 통해 반응 |
| contact pattern 전체 | 9D state | object geometry/물성의 직접 추정 없이 interaction mode의 proxy | continuous motion 또는 backward primitive 선택 |

중요한 점은 force feature가 object mass, friction, pose 같은 명시적 latent variable로 변환되지 않는다는 것이다. **SAC가 tactile pattern과 reward 결과의 관계를 직접 근사**한다.

## 20. Limitation — 저자들이 직접 밝힌 한계와 범위

원문에는 독립된 Limitations 절이 없다. 아래는 저자들이 본문에서 직접 설명한 적용 범위·문제 설정상의 제한이다.

| 항목 | 저자들이 밝힌 내용 | 원문 위치 |
| --- | --- | --- |
| Searching 제외 | object가 이미 successfully located되었다고 가정하며 searching phase는 범위 밖 | §III-B |
| Simulation 대신 hardware training | tactile sensor와 object의 복잡한 physical property, non-rigid object 때문에 realistic simulation modeling이 어렵다고 설명 | §I |
| Representative-shape hypothesis | cuboid와 cylinder 두 대표 shape로 학습하면 다양한 everyday object로 일반화할 수 있다는 가정을 채택 | §I, §IV-A |
| Confined horizontal setup 중심 | 본 실험은 현재 confined-space retrieval setting에 집중하며 slope/vertical은 후속 과제로 남음 | §V |
| Hardware cost | 직접 실물 RL은 시간이 많이 들고 hardware wear가 심할 수 있어 focused training/curriculum이 필요하다고 설명 | §I |

이 표는 저자들이 명시한 문제 설정과 동기를 정리한 것이며, 논문에 없는 약점을 새로 만들어 Limitation으로 넣은 것이 아니다.

## 21. Future Work — 저자들이 제시한 향후 연구

Conclusion에서 저자들은 **sloped 또는 vertical space와 같이 gravity가 추가 복잡성을 만드는 더 복잡한 환경에서 unknown object manipulation을 연구**하겠다고 명시한다. [원문 §V]

그 외 다음 항목은 원문 Future Work로 명시되지 않는다.

- proprioception 추가
- wrist F/T 추가
- recurrent policy
- simulation pretraining
- tactile sensor 변경
- vision과 tactile fusion
- multi-object clutter 확장

이러한 방향을 저자들의 계획으로 임의 추가하지 않는다.

## 22. 미명시 사항과 해석 주의점

### 22.1. Tactile-only의 범위

Policy observation은 tactile-only지만 training reward에는 OptiTrack이 사용된다. 따라서 “외부 perception 없이 전체 학습”이라고 쓰면 부정확하다.

### 22.2. 9D tactile은 raw sensor가 아니다

uSPa44의 4×4×3-axis raw measurement 전체를 policy에 넣지 않는다. column pooling과 FFT feature extraction을 거친 9D feature다.

### 22.3. y-shear의 사용 여부

Sensor는 두 shear axis를 측정하지만 observation 정의에는 x-shear만 명시된다. y-shear가 별도 hidden preprocessing이나 controller에 사용된다는 근거는 없다.

### 22.4. FFT 구현 세부

32-sample window, 30 Hz 초과 성분 평균은 명시되지만 FFT normalization, window function, overlap, taxel/column aggregation의 구체 구현은 미명시다.

### 22.5. Force upper-limit 처리

$f_n^{\max}>f_n^h$일 때 reward penalty뿐 아니라 robot이 press를 release해 force를 $f_n^l$까지 낮춘다고 설명한다. 이 release가 SAC action을 override하는 별도 safety/control routine인지, 정확히 어떤 trajectory로 수행되는지는 원문에 충분히 정의되지 않는다.

### 22.6. Episode와 termination

Training episode의 timeout, success 이후 termination timing, reset procedure, object initial pose distribution은 원문에 수치로 정리되어 있지 않다.

### 22.7. SAC 재현성

Network topology는 제시되지만 learning rate, batch size, gamma, tau, entropy tuning, replay size 등 주요 hyperparameter가 빠져 있어 제공된 7쪽만으로 학습을 완전히 재현하기는 어렵다.

### 22.8. Training curve의 통계

Fig. 8에는 단일 curve처럼 보이는 세 reward trajectory가 제시되며, seed 반복·분산·confidence interval은 설명되지 않는다. 따라서 training speed 차이를 다중 seed 통계 검정 결과로 확대 해석하지 않는다.

### 22.9. Generalization의 범위

Generalization은 8개 representative training object에서 만든 integrated model을 12개 unseen everyday object/scenario에 적용한 결과다. 임의 geometry·material에 대한 보편적 성능 보장은 아니다.

## 23. 원문 위치 안내

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 문제 정의·기여 | Abstract, §I, PDF pp. 1–2 |
| Tactile vs F/T 설명 | §I, PDF p. 1 |
| Related Works | §II, PDF p. 2 |
| Robot·tool·uSPa44 sensor | §III-A, PDF pp. 2–3 |
| 4×4×3축·100 Hz | §III-A, PDF p. 3 |
| 9D observation | §III-B.1, Fig. 3, PDF p. 3 |
| 30 Hz FFT feature | §III-B.1, PDF p. 3 |
| Hybrid action | §III-B.2, Fig. 4, PDF p. 3 |
| Reward 식 (1)–(4) | §III-B.3, PDF pp. 3–4 |
| OptiTrack training reward | §III-B.3, PDF p. 4 |
| Force thresholds·goal curriculum | §III-B.3, Table I, PDF p. 4 |
| SAC·action scaling·network | §III-C, Table I, PDF p. 4 |
| Focused hardware training | §IV-A, Fig. 5, PDF pp. 4–5 |
| Tactile-only evaluation | §IV-A, PDF p. 5 |
| Heuristic baseline | §IV-B, PDF p. 5 |
| Success criterion·test objects | §IV-B, PDF p. 5 |
| Success rate | Table II, PDF p. 6 |
| Mug Obj-18 사례 | §IV-B, Fig. 7, PDF pp. 5–6 |
| Primitive ablation | §IV-C, Fig. 8, PDF pp. 5–6 |
| Curriculum ablation | §IV-D, Fig. 8, PDF p. 6 |
| Conclusion·Future Work | §V, PDF p. 6 |

## 24. 문서 검증 범위

사용자 제공 IEEE 출판본 PDF 7쪽 전체를 텍스트와 페이지 렌더링으로 확인하고, Fig. 2–8, Table I–II, 식 (1)–(4)을 대조했다.

코드 실행, SAC 재학습, iiwa 실험 재현, supplementary video의 object property 확인은 수행하지 않았다. 원문 PDF와 페이지 이미지는 저장소에 복제하지 않으며 DOI와 파일 해시로 출처를 관리한다.
