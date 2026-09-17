# 힘·촉각 기반 Sweeping: 선행연구 검토와 적용 방향

**미팅 자료 · 2026.09.18**

[문헌 색인](../README.md) · [논문 상세 정리](../papers/README.md)


**연구 주제:** 초기 시각 관측으로 대상과 목표를 지정한 뒤, 조작 중 시각 추적 없이 Force/Torque와 Tactile 피드백으로 물체를 목표 방향·거리만큼 이동시키는 Sweeping 정책.

## 1. Tactile 표현 검토

### 선행연구에서는 어떻게 사용하는가?

| 접근                   | 대표 연구                                                                                                             | 확인한 방법                                                                                            |
| -------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **광학 촉각 영상 활용**      | [Bi-Touch](../papers/2023-lin-bi-touch.md), [Tactile Pushing](../papers/2023-yang-sim-to-real-tactile-pushing.md) | 촉각 영상을 학습 정책에 연결하거나, CNN으로 접촉 깊이·방향을 추정한다. 일부 영상 기반 경로에서는 GAN으로 실물 영상을 Simulation 표현에 맞춘다.        |
| **분포형 힘의 영상 표현**     | [Gentle Object Retraction](../papers/2026-brouwer-gentle-object-retraction.md)                                    | 분포형 3축 힘을 RGB 영상으로 변환해 ResNet-18로 인코딩하고, Diffusion Policy 기반 모방학습에 활용한다. 광학 촉각 영상과는 구분한다.         |
| **영역별 Binary 접촉 활용** | [DexTouch](../papers/2024-lee-dextouch.md)                                                                        | FSR 출력을 필터·Threshold로 처리하여 영역별 접촉 여부를 만들고, 고유감각과 함께 PPO에 입력한다. |

요약하면, 조사한 선행 연구들에서는 다음과 같은 방법이 주로 사용된다.

- **영상 자체를 학습하는 방식 (Encoding)**
- **접촉에 필요한 물리 정보로 축약하는 방식 (Binary)**  

### 1.1. [Bi-Touch](../papers/2023-lin-bi-touch.md) — 실물 촉각 영상을 Simulation 영상으로 변환

- **후처리:** 동일한 접촉 Pose에서 얻은 실물·Simulation 영상 쌍으로 Pix2Pix GAN을 학습하여, 실물 TacTip 영상을 Simulation의 촉각 영상으로 변환.
- **정책 입력:** 양쪽 센서 영상을 각각 변환한 뒤 연결하고, 고유감각·목표 정보와 함께 PPO에 입력.
- **역할 분담:** GAN은 영상 도메인 차이를 줄이고, 제어에 필요한 촉각 특징과 행동의 관계는 RL 정책에서 학습. 

![[../../../img/bi-touch_fig1.png]]

### 1.2. [Tactile Pushing](../papers/2023-yang-sim-to-real-tactile-pushing.md) — Image 입력과 Pose 입력 비교

- **Image:** 실물 촉각 영상 → Real-to-Sim GAN → Simulation 촉각 영상 → SAC.
- **Pose:** 실물 촉각 영상 → PoseNet(CNN)으로 **접촉 깊이·각도** 추정 → 접촉면 Pose와 목표 정보 구성 → SAC 또는 PETS/MPC. 물체 중심 Pose를 추정하는 방식과는 구분.

| 구성 | 학습 샘플 수* | 최고 Reward |
| --- | ---: | ---: |
| Image + SAC | 320만 | −124.86 |
| Pose + SAC | 280만 | **−122.85** |
| Pose + PETS/MPC | **2.5만** | −144.70 |

*각 방법의 최고 Reward에서 10% 이내 성능에 도달하기까지의 샘플 수. Reward는 높을수록 좋음.*

**Pose 입력이 샘플 효율과 최고 Reward에서 소폭 우세했다.** Pose 기반 Model-based 방식은 약 100배 적은 샘플을 사용했지만, 충분히 학습한 SAC보다 최고 Reward는 낮았다. 

![[../../../img/tactile_pushing_fig1.png]]

### 1.3. [Gentle Object Retraction](../papers/2026-brouwer-gentle-object-retraction.md) — 3축 힘을 영상으로 표현하고 인코딩

- **영상화:** 좌우 각 49개 Taxel에 무접촉 값 1개씩을 채워 총 100픽셀로 구성. **X 힘→B, Y 힘→G, Z 힘→R**의 색상 강도로 변환하여 **20×5×3 RGB 힘 영상** 생성. 오른쪽 센서의 Y축 부호는 좌우 방향이 일치하도록 반전.
- **인코딩:** 힘 영상을 **촉각 전용 사전학습 ResNet-18**에 입력. 별도 ResNet-18의 Camera 특징과 정규화한 Wrench·TCP Pose·흡착 상태를 연결해 **Diffusion Policy 모방학습**에 사용. 

![[../../../img/gentle_object_fig1.png]]

### 1.4. [DexTouch](../papers/2024-lee-dextouch.md) — Binary 접촉과 Isaac Gym 구현

- **실물:** 손의 FSR 16개(손가락 각 3개 + 손바닥 4개) 전압 → Low-pass Filter → Threshold → **16bit 접촉 여부**.
- **Isaac Gym:** 실물 센서 위치에 대응하는 **가상 접촉 센서 16개** 구성 → 매 step 센서별 Net Contact Force $\mathbf F_i=[F_{x,i},F_{y,i},F_{z,i}]$ 취득 → 크기 $\lVert\mathbf F_i\rVert_2$를 **0.01 N 임계값**으로 Binary 변환.
- **정책 연결:** 실물과 Simulation에서 같은 형태의 접촉 벡터를 만들고, 로봇 상태·과업 정보와 함께 MLP 기반 PPO에 입력. 힘 크기를 Binary로 축약해 Sim-to-Real 차이를 줄이는 구성. 원문 §III-A, §IV-C, Fig. 2.

![[../../../img/dex_touch_fig1.png]]

### 적용 검토안

**검토안: [DexTouch](../papers/2024-lee-dextouch.md)를 참고해, 17개 Grid 영역을 각각 하나의 접촉 여부로 축약.** 전체 손을 하나의 bit로 합치지 않고 **17bit의 접촉 분포를 유지하는 구성**.

- **전이의 단순화:** 정밀한 접촉력 크기를 맞추는 부담을 줄일 수 있다. 다만 영역 내부 위치·힘 크기와 같은 정보들이 소실되지만, Sim-to-Real Transfer 까지 포함하면 더 높은 성공률을 가질 수 있을 것으로 예상된다.
- **F/T와의 역할 분담:** 촉각에서는 ‘어느 센서 영역이 닿았는가’를, 손목 Wrench에서는 ‘전체 하중이 얼마나·어느 방향으로 작용하는가’에 대한 정보를 담을 수 있기 때문에, 저차원화를 해도 정책 학습이 가능할 것으로 예상된다.

이 표현을 적용할 전제는 실제 미는 부위에 촉각 센서가 반응한다는 것이다. 비센서 부위 접촉과 약한 신호에서는 Binary가 0이어도 무접촉이라고 단정할 수 없다. 

[DexTouch](../papers/2024-lee-dextouch.md) 연구에서는 0.01N 이상의 힘이 감지될 경우 True로 취급하였으나, 구매한 Inspire Robot 사의 핸드 제품의 경우 0.05N Force Resolution을 가지기 때문에, 이 미세한 힘의 차이가 수렴 여부에 어떤 영향을 줄 것인지 알 수 없다. 하지만, [Gentle Object Retraction](../papers/2026-brouwer-gentle-object-retraction.md) 연구에서는 0.5N 수준의 Resolution을 가지는 Tactile Image를 Encoing 한 것으로 Diffusion Policy를 학습한 선례도 존재한다.

## 2. F/T — 6축 관측과 방향·크기 활용 검토 (추가 조사 필요)

### 선행연구에서는 어떻게 사용하는가?

| 연구                                                                             | F/T 활용                                                                                                                    | 참고할 점                                                                    |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| [Force Push](../papers/2024-heins-force-push.md)                               | 힘 **방향**으로 미는 방향을 보정하고, **크기**로 접촉 손실·회복과 과부하 대응을 수행하는 비학습 제어                                                             | Force를 단순한 충돌 감지값이 아니라 연속적인 조작 Feedback으로 사용한다.                          |
| [Gentle Object Retraction](../papers/2026-brouwer-gentle-object-retraction.md) | Encoded Camera Image, Tactile Image, **6-Axis Wrench** 정보를 관측에 포함하고, Imitation Learning을 통해 장애물들을 밀치는 Diffusion Policy 학습 | Wrench 정보를 활용하여 특정 방향으로 밀 수 없음으로 판단한다. (임계점 이상의 Impulse에 대하여 Failure 처리) |

### 적용 검토안과 근거

검토안: **6축 Wrench 관측**을 통해 **의도하는 방향·크기**를 반영하는 Reward를 정책에 제공하는 구성.

**F/T 관련 추가 조사는 필요하다.** Contact 기반 Manipulation으로 조사한 연구들에서는 대부분 Tactile 정보를 활용하는 경우가 많아, Wrench 정보를 다루는 경우를 확인하지 못했다. 
**Wrench로 접촉 손실·미끄러짐·물체 진행을 어떻게 판단하는지**, 그리고 **미지 질량·마찰에 어떻게 적응하는지**를 우선 보완할 예정이다.

## 3. RL 결합과 Reward — Task 중심의 보상 설계

### 선행연구에서는 어떻게 학습에 반영하는가?

아래 세 연구에서는 **촉각을 정책의 관측으로 제공하고, Reward는 Task의 목표 달성과 필요한 접촉 자세를 중심으로 구성**한다. 촉각 신호를 많이 발생시키거나 특정 Wrench를 만드는 것 자체가 주목적은 아니다.

| 연구 | 정책에 제공하는 정보 | Reward의 중심 |
| --- | --- | --- |
| [DexTouch](../papers/2024-lee-dextouch.md) | Binary Tactile, 로봇 상태, 초기 물체 범위·과업 목표 | 접근 → 들어 올리기·운반 / 손잡이 회전·문 열기 |
| [Bi-Touch](../papers/2023-lin-bi-touch.md) | 양쪽 Tactile Image와 고유감각·목표 정보 | 물체 위치·방향, 접촉면에 대한 TCP 정렬, 접촉 위치 |
| [Tactile Pushing](../papers/2023-yang-sim-to-real-tactile-pushing.md) | Tactile Image 또는 추정한 접촉면 Pose와 목표 정보 | 목표 방향·거리, Pusher와 접촉면의 정렬 |

**위치·방향·정렬 오차는 Reward 계산 항이며, 모두 정책 관측에 직접 들어간다는 뜻은 아니다.** 특히 영상 기반 정책에서는 촉각 특징과 행동이 Task 성과에 어떤 영향을 주는지를 RL 학습으로 연결한다.

### 3.1. [DexTouch](../papers/2024-lee-dextouch.md) — 접근 보상 + Gate를 둔 Task-specific 보상

Sweep은 아니지만, **Grasping·운반과 Door Opening에서 접근 보상과 과업별 실행 보상을 함께 사용**한다. 관절속도의 L1 Penalty도 추가한다. Gate는 보상 항의 활성 조건이며, 별도 정책으로 전환하는 규칙은 아니다. 원문 §IV-B, 식 (1)–(3).

**공통 접근 보상 — 손끝이 대상에 더 가까이 도달했을 때 보상**

$$
r_{\mathrm{reach}}
=\sum_{\mathrm{finger}}\alpha_{\mathrm{reach}}
\max(d_{\mathrm{closest}}-d,0).
$$

$d$는 손끝–대상 거리, $d_{\mathrm{closest}}$는 에피소드에서 달성한 최소거리 기록이다. **직전 step보다 가까워지는 것보다 엄격하게, 기존 최소거리 기록을 갱신할 때 보상**한다.

**Grasping·운반 — 들어 올린 뒤 목표점으로 이동**

$$
\begin{aligned}
r_{\mathrm{execute}}^{\mathrm{grasp}}
={}&(1-\mathbf{1}_{\mathrm{picked}})\alpha_{\mathrm{pick}}h_{\mathrm{obj}}
+r_{\mathrm{picked}}\\
&+\mathbf{1}_{\mathrm{picked}}\alpha_{\mathrm{goal}}
\max(\tilde d_{\mathrm{closest}}-\tilde d,0).
\end{aligned}
$$

| 항 | 의미 |
| --- | --- |
| $(1-\mathbf{1}_{\mathrm{picked}})\alpha_{\mathrm{pick}}h_{\mathrm{obj}}$ | 물체를 들어 올리기 전에는 테이블 기준 높이를 보상 |
| $\mathbf{1}_{\mathrm{picked}}$ | 물체 높이 **10 cm 초과** 시 활성화되는 Gate |
| $\mathbf{1}_{\mathrm{picked}}\alpha_{\mathrm{goal}}\max(\tilde d_{\mathrm{closest}}-\tilde d,0)$ | 들어 올린 후에는 물체–목표점 거리 $\tilde d$의 최소기록 갱신을 보상 |
| $r_{\mathrm{picked}}$ | 들어 올리기 조건 달성 Bonus |

**Door Opening — 손잡이를 돌린 뒤 문을 열기**

$$
\begin{aligned}
r_{\mathrm{execute}}^{\mathrm{door}}
={}&(1-\mathbf{1}_{\mathrm{rotated}})\alpha_{\mathrm{rot}}
\max(\phi-\phi_{\max},0)\\
&+\mathbf{1}_{\mathrm{rotated}}\alpha_{\mathrm{open}}
\max(\psi-\psi_{\max},0)
+r_{\mathrm{rotated}}+r_{\mathrm{opened}}.
\end{aligned}
$$

$\phi$는 손잡이 각도, $\psi$는 문 열림 각도이며, 아래첨자 $\max$는 각각의 최대기록이다. 손잡이를 **약 60°** 돌리기 전에는 손잡이 회전을, 이후에는 문 열림을 보상한다. 두 Bonus는 손잡이 회전 조건과 **문 약 50° 열림**에 대응한다. $\alpha$와 Bonus의 구체적인 수치는 원문에 명시되지 않는다.

**특징은 Privileged Information의 적극적인 활용이다.** Critic에는 물체 Pose·속도·물성·거리·과업 상태를 추가하고, Reward는 물체 거리·높이·각도 등 시뮬레이션 상태로 계산한다. Actor에는 실행 가능한 로봇 상태·촉각·과업 사전정보를 제공하며, **현재 물체의 GT Pose를 계속 입력하지 않는다.** 원문 §IV-A, §IV-C.

### 3.2. [Bi-Touch](../papers/2023-lin-bi-touch.md) — 위치·방향·접촉 자세를 Task별로 조합

양쪽 촉각 영상을 함께 받는 PPO 정책에, 과업별 위치·방향·접촉 기하 보상을 제공한다. **영상 특징에서 어떤 접촉 상태가 좋은 행동으로 이어지는지는 정책이 학습**한다. 아래는 원문 §III-C, 식 (1)–(4)의 구성이다.

$p$는 위치, $\theta$는 평면 방향각, $o$는 물체, $g$는 목표, $e_i$는 $i$번째 TCP다. $S$는 Cosine Distance이며, $w_j>0$의 구체적인 수치는 원문에 명시되지 않는다.

**Bi-pushing — 목표 위치·방향으로 밀면서 접촉면에 수직 정렬**

$$
R_t^{\mathrm{BP}}
=-w_1\lVert p_t^g-p_t^o\rVert_2
-w_2S(\theta_t^g,\theta_t^o)
-w_3\sum_{i=1}^{2}S(\theta_t^{e_i},\theta_t^o).
$$

**Bi-reorienting — 중심 위치를 유지하면서 목표 방향으로 회전**

$$
\begin{aligned}
R_t^{\mathrm{BR}}
={}&-w_1\lVert p_0^o-p_t^o\rVert_2
-w_2S(\theta^g,\theta_t^o)\\
&-w_3\sum_{i=1}^{2}
S\!\left(\theta_t^{e_i},(-1)^i(\pi/2+\theta_t^o)\right)\\
&-w_4\sum_{i=1}^{2}
\lVert p_{\mathrm{ctrl}_i}^{o}-p_t^{e_i}\rVert_2.
\end{aligned}
$$

$p_{\mathrm{ctrl}_i}^{o}$는 원하는 접촉 위치다. **중심 유지 + 목표 회전 + 접촉면 정렬 + 접촉 위치 유지**로 구성한다. 여기서 수직 정렬은 세계 좌표계의 수직축이 아니라 **접촉면 법선 방향 정렬**이다. 각도의 좌우 부호는 원문 표기를 따른다.

**Bi-gathering — 두 물체 사이의 거리를 줄이면서 접촉 유지**

$$
\begin{aligned}
R_t^{\mathrm{BG}}
={}&-w_1\lVert p_t^{o_1}-p_t^{o_2}\rVert_2
-w_2\sum_{i=1}^{2}S(\theta_t^{e_i},\theta_t^{o_i})\\
&-w_3\sum_{i=1}^{2}
\lVert p_{\mathrm{ctrl}}^{o_i}-p_t^{e_i}\rVert_2.
\end{aligned}
$$

여기에 GUM(Goal-update Mechanism)을 적용해 **중간 목표까지의 거리와 Target Line 방향 정렬**을 추가한다.

$$
\begin{aligned}
R_t^{\mathrm{BG\text{-}GUM}}
={}&R_t^{\mathrm{BG}}
-w_4\sum_{i=1}^{N}\lVert p_t^{g_i}-p_t^{o_i}\rVert_2\\
&-w_5\sum_{i=1}^{N}S(\theta_t^{o_i},(-1)^i\theta_t^c).
\end{aligned}
$$

$p_t^{g_i}$는 중간 목표이며, $\theta_t^c$는 본문의 설명상 Target Line 방향이다. 원문의 $N$은 두 물체에 대한 합산 문맥이며, 중간 목표 후보 개수와 구분한다.

**세 과업 모두 목표 상태와 접촉 기하를 보상으로 정한다.** 다만 회전 과업에서는 실물의 과도한 압착을 줄이기 위해 큰 Contact Depth에 대한 Penalty도 강화했다. 따라서 ‘위치·방향만 사용하고 접촉을 전혀 유도하지 않는다’고 해석하는 것은 부정확하다.

### 3.3. [Tactile Pushing](../papers/2023-yang-sim-to-real-tactile-pushing.md) — 멀 때는 방향, 가까울 때는 거리

Model-free SAC와 Model-based PETS/MPC를 비교하며, 다음 보상으로 **목표 진행과 접촉면 정렬**을 평가한다. 원문 §III-B-3, 식 (4).

$$
r=
\begin{cases}
-\bigl(g(o_\theta,g_\theta)+g(p_\theta,o_\theta)\bigr),
&\lVert o_{xy}-g_{xy}\rVert>d,\\
-\bigl(f(o_{xy},g_{xy})+g(p_\theta,o_\theta)\bigr),
&\lVert o_{xy}-g_{xy}\rVert\le d.
\end{cases}
$$

| 항 | 의미 |
| --- | --- |
| $f(o_{xy},g_{xy})$ | **물체 접촉 위치**와 목표 사이의 Euclidean Distance |
| $g(o_\theta,g_\theta)$ | 접촉면 방향과 목표를 향하는 방향의 Cosine Distance |
| $g(p_\theta,o_\theta)$ | Pusher가 접촉면에 수직으로 밀도록 유도하는 정렬 오차 |
| $d=100\,\mathrm{mm}$ | 방향 보상에서 거리 보상으로 바꾸는 경계 |

먼 구간에서는 고정 전진 동작에 **목표 방향 정렬**을 결합하고, 가까운 구간에서는 **음의 목표거리**를 보상으로 사용한다. 두 구간 모두 접촉면 정렬 항을 유지한다. 힘 크기나 6축 Wrench 추종 항은 없다. 목표의 기준은 물체 중심이 아닌 접촉 위치다.

### 적용 검토안

요약하면, 조사한 세 연구는 **Task를 달성한 상태와 필요한 접촉 자세를 Reward로 정의하고, 촉각에서 행동으로 이어지는 관계를 학습**한다. 

**검토안: Sweeping의 목표 방향·거리 달성을 Main Reward로 두고, 필요한 미는 자세·접촉 정렬을 Sub Reward로 구성.**

Task 중심 Reward를 사용하더라도 **동일한 보상 조건에서 촉각·F/T의 유무를 비교**하면, 각 센서가 목표 이동과 접촉 유지에 기여하는지를 확인할 수 있다.

## 결론

**논의할 구성안: 영역별 Binary 접촉 + 연속 Wrench 관측 + Task 중심 Reward.** 같은 보상 조건에서 센서별 기여를 비교하고, F/T를 이용한 자유 물체 조작의 보상 설계를 고도화.

---

검토 범위: 2026.09.17까지 확보한 프로젝트 문헌과 원문 확인 내용. 위 요소의 Sweeping 적용 효과는 비교 실험으로 확인할 항목이다. 연구 범위는 [프로젝트 결정 사항](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/3fe9c881799b82c927e89983ce0709ec3f713689/docs/03_DECISIONS_AND_OPEN_QUESTIONS.md)을 따른다.
