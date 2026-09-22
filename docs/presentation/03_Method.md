# 3. Method

[발표 문서 안내](README.md) · [Research Motivation and Contributions](01_Research_Motivation.md) · [Related Works](02_Related_Works.md)

> **문서 상태: Method 초안.** 기존 문서의 MDP와 본 연구의 DR 설계 후보를 이관했다. 관측·행동 이력의 설계는 현재 다루지 않으며, 구체적인 정책 구성과 보상식은 이후 보강한다.

## 3.1. Markov Decision Process

### 3.1.1. State / Observation

| 구성 | Actor 입력 후보 |
| --- | --- |
| 초기 과업 정보 | 목표 방향·거리(Required), 초기 대상 Pose(Required), 제공 가능한 초기 크기·형상 정보(Optional) |
| Arm 고유감각 | 관절 위치·속도, EEF Pose·Twist |
| Hand 고유감각 | 관절 위치·속도 |
| 접촉 관측 | 한 면당 영역별 Binary 촉각 17차원과 보정된 6축 Wrench. 양면 구성의 접촉면 선택·18D 표현은 [3.3절의 후보](#surface-conditioned-tactile) |

#### 3.1.1.1. Privileged Information

시뮬레이션에서만 얻을 수 있는 일부 정보는, 최종 Blind Actor 입력에 포함하지 않는 대신에, Reward Formulation에서 활용 가능한 Privileged Information으로 사용할 수 있다.

- 현재 물체의 Ground-Truth Pose 및 속도
- 접촉 물체 ID(혹은, Shape이나 Size)
- 접촉력 벡터
- 정확한 질량·마찰·형상 파라미터 등

### 3.1.2. Action 설계

#### 3.1.2.1. Arm Action은 Cartesian Space로 표현한다

정책의 Arm Action은 **EEF 기준 Cartesian Space의 운동 명령**으로 표현한다. 이는 정책 출력의 표현에 관한 결정이며, 실제 명령 변환 및 제어기 선택을 확정한 것은 아니다.

> **추가 조사 필요:** Joint-space Action 대비 Cartesian Action을 선택할 근거와, 현재 구현에서 실제 적용되는 Controller 경로를 확인한다.

#### 3.1.2.2. Arm Action: Cartesian 증분을 생성한다

Arm의 기본 행동 후보는 EEF의 위치·회전 증분이다.

```math
a_t^{\mathrm{arm}}=(\Delta p_x,\Delta p_y,\Delta p_z,\Delta\theta_x,\Delta\theta_y,\Delta\theta_z).
```

각 성분에는 물리 단위의 크기 제한을 적용하고 EEF 기준 좌표계를 일관되게 사용한다.

#### 3.1.2.3. Hand Action (미정)

Hand의 행동 표현은 아직 확정하지 않는다. 현재 비교할 후보는 6개 구동 입력을 직접 제어하는 방식과, 엄지와 나머지 손가락을 분리한 2차원 근사다. 여기서 6차원은 **Cartesian 6-DoF가 아니라 Hand의 구동 입력 차원**이다.

| 후보 | 행동 표현 | 표현 구조상 차이 |
| --- | --- | --- |
| **A. 6차원 직접 제어** | 각 구동부의 목표 또는 목표 증분 | 부위별 접촉 조절 자유도를 유지하지만 탐색할 행동 공간이 커짐 |
| **B. 2차원 근사** | $u_{\mathrm{fingers}},u_{\mathrm{thumb}}\in[0,1]$ | 나머지 손가락과 엄지의 자세 변화를 분리. 혹은 1차원 근사도 가능. |

> **추가 조사 필요:** Sweeping·비파지 조작에서 직접 관절 제어와 저차원 Hand Synergy를 비교한 연구.

### 3.1.3. Reward Formulation 설계 — TODO

> **TODO:** 본 연구의 Reward Formulation은 추후 구체화한다. 현재는 MDP 하위의 항목만 유지한다.

## 3.2. Domain Randomization 설계

선행연구의 Randomization 대상은 [Related Works](02_Related_Works.md#24-선행연구의-domain-randomization)에 정리하고, 여기서는 본 연구의 설계 후보를 다룬다.

### 3.2.1. Randomization 대상 (후보)

| 구분 | Randomization 후보 |
| --- | --- |
| **환경 파라미터** | Object–Shelf 마찰, 선반 접촉 특성 등 |
| **물체 파라미터** | 종류·형상·크기·질량·질량 중심·초기 Pose 등 |
| **로봇 파라미터** | 시작 관절 상태·Hand 자세·제어 Gain(Stiffness & Damping) 등 |
| **Base 파라미터** | 선반에 대한 Base의 XY 평면 위치 |

### 3.2.2. 센서 불확실성

[3.2.1절](#321-randomization-대상-후보)의 환경·물체·로봇·Base 파라미터와 **별도로 센서 관측 오차를 모델링하고, 학습 중 해당 오차를 무작위화한다.** 물리 파라미터의 변화가 실제 접촉·운동을 바꾼다면, 센서 불확실성은 그 상태가 정책에 어떻게 측정·전달되는지를 바꾼다.

[Related Works의 DR 비교](02_Related_Works.md#24-선행연구의-domain-randomization)에 정리한 Binary 반전·Dropout·지연 및 연속 접촉력 잡음 사례를 근거로, 본 연구에서는 다음 관측 오차 모델을 검토한다. **아래는 본 과업에 대한 설계 후보이며, 선행연구가 손목 F/T까지 동일하게 적용했다는 뜻은 아니다.**

| 대상 | 센서 불확실성 모델 후보 |
| --- | --- |
| **영역별 Binary 촉각** | 오검출(0→1), 접촉 누락(1→0), 감지 임계값의 변동, 관측 지연. 대칭 Bit Flip과 접촉 누락만 주는 Dropout을 구분 |
| **손목 6축 F/T** | 영점 Bias, 힘·모멘트 측정 잡음, 측정값 Scale 오차, 보정 후 남는 부하 오차, 관측 지연 |
| **Arm·Hand 고유감각** | 관절 위치·속도 등 실제 사용하는 관측의 잡음과 지연, 센서 간 시간 정렬 오차 |

Binary 촉각은 [**Sim-to-Real Transfer for Robotic Manipulation with Tactile Sensory**](../literature/papers/2021-ding-sim-to-real-tactile-manipulation.md)의 **매 Bit·매 Timestep 반전**을 구현 후보로 삼는다.

<a id="surface-conditioned-tactile"></a>

## 3.3. 동작별 접촉면 선택을 통한 Tactile 관측 축약

> **상태: PROPOSED.** 손바닥 쪽 17개 영역과 손등 쪽 17개 영역을 구성한다는 계획에 대한 관측 설계 후보다. 센서 부착·영역 대응·학습 효과가 검증되었거나 전체 Observation이 확정되었다는 의미는 아니다.

### 3.3.1. 모든 센서 채널을 항상 독립 입력할 필요가 있는가?

**센서의 물리적 개수와 특정 동작의 정책에 필요한 관측 채널 수를 반드시 같게 둘 필요는 없다.** [Wei et al.](02_Related_Works.md#tactile-reduction-wei)은 과업별로 센서의 위치·종류·미설치를 선택하여, 전체 배치보다 적은 센서로 유효한 인식 성능을 얻었다. 이는 **과업에 필요한 센서 부분집합을 선택하는 설계 자체의 직접적인 근거**다. 다만 지도학습 인식 과업의 결과이므로, 같은 선택이 Sweeping 제어에서도 충분한지는 별도로 확인해야 한다. (Wei, §IV–V, PDF pp. 3–6)

[Melnik et al.](02_Related_Works.md#tactile-reduction-melnik)은 92개 채널을 16개 접촉 영역으로 묶어도 무촉각 대비 학습 효율의 이득을 유지했고, [Zhang et al.](02_Related_Works.md#tactile-reduction-zhang)은 전체 분포보다 간결한 합력 표현도 과업에 유효할 수 있음을 보였다. 이 결과들은 **원시 촉각을 모두 독립적으로 전달하기보다, 행동 조절에 필요한 정보를 남기도록 표현을 설계할 근거**다. 차원 축소가 항상 더 좋은 성능을 보장한다는 근거는 아니다. (Melnik, §2.2, Tables 4–5, PDF pp. 5·9; Zhang, §IV-C, Fig. 8, PDF p. 5)

**본 연구의 적용 논리:** Sweeping 동작이 사용할 접촉면을 먼저 지정하고, 그 동작의 정상 접촉이 해당 면에 한정되는 조건에서는 **그 면에서 접촉의 발생·유지·소실을 관측할 17개 영역을 선택**한다. 반대 면의 채널이 해당 조건에서 계속 0이라면 이를 별도 입력으로 반복하는 대신, **선택한 면의 접촉 지도와 접촉면 ID**로 표현할 수 있다. 여기서 선택은 **현재 값이 1인 센서만 남기는 것**이 아니다. 선택한 면의 17개 인덱스를 고정하고 0도 그대로 전달하여, 비접촉과 접촉 소실의 정보를 유지한다.

### 3.3.2. 접촉면 ID와 공통 17개 영역의 결합

손바닥 쪽과 손등 쪽의 센서 영역을 1:1 대응시켜 각각 Binary 벡터로 둔다.

```math
\mathbf{p}_t,\mathbf{d}_t\in\{0,1\}^{17},\qquad
m_t=\begin{cases}
0,&\text{palm-side sweep},\\
1,&\text{dorsal-side sweep}.
\end{cases}
```

$m_t$는 **현재 동작에서 사용하도록 지정한 접촉면**이다. 접촉 Bit의 크기나 개수로 매 순간 추정하는 값이 아니므로, 접촉 전이나 접촉이 끊긴 순간에도 의미가 유지된다. 선택·정렬한 촉각 입력은 다음과 같다.

```math
\mathbf{c}_t=(1-m_t)\mathbf{p}_t+m_t\mathbf{d}_t,\qquad
\mathbf{z}_t=[m_t,\mathbf{c}_t]\in\{0,1\}^{18}.
```

즉 **손바닥 17 + 손등 17의 34개 채널** 대신 **접촉면 Header 1 + 선택한 면의 17개 접촉 Bit**를 사용한다. 손목의 보정된 **6축 Wrench는 별도 입력으로 유지**한다. 따라서 이 후보의 접촉 관련 입력은 24D이지만, 초기 정보·고유감각 등을 포함한 전체 정책 입력 차원은 아니다.

[Wu et al.](02_Related_Works.md#tactile-reduction-wu)의 Canonical Representation은 서로 다른 센서의 내부 좌표를 정렬하면서 센서의 위치 정보도 보존한다. 본 설계에서는 그 **대응 관계를 일관된 표현으로 정리한다는 원칙**을 참고하여 17개 영역의 인덱스를 맞추고, 어느 면의 값인지 Header로 유지한다. 이는 Wu의 3D 좌표·힘 표현이나 GNN을 그대로 적용한 것이 아니다. 또한 손바닥과 손등의 형상·접촉 동역학이 동일하다고 가정하지 않으며, 실제 부착 영역의 대응과 센서별 Binary 판정 조건을 확인해야 한다. (Wu, §IV-A, Fig. 3, PDF pp. 3–4)

### 3.3.3. 정보 보존 조건과 제외하면 안 되는 접촉

다음 조건이 성립하는 관측에서는 위 표현으로 원래 두 Binary 벡터를 복원할 수 있다.

```math
m_t=0\Rightarrow\mathbf{d}_t=\mathbf{0},\qquad
m_t=1\Rightarrow\mathbf{p}_t=\mathbf{0}.
```

```math
\mathbf{p}_t=(1-m_t)\mathbf{c}_t,\qquad
\mathbf{d}_t=m_t\mathbf{c}_t.
```

이것은 **지정한 면과 실제 접촉면이 일치하고 비선택 면의 관측이 모두 0인 조건에서, 이미 이진화한 34개 채널을 보존한다는 대수적 결과**다. 원래의 압력 분포·힘 크기를 복원하거나, 모든 물체 상태를 식별한다는 뜻은 아니다. 또한 실제 센서의 오검출이 있으면 물리적 비접촉과 관측값 0이 일치하지 않을 수 있다.

손바닥으로 밀면서 손등이 선반·주변 물체와 접촉하거나, Hand 자세가 바뀌어 비선택 면에 유효한 접촉이 생기면 위 조건은 깨진다. [Yin et al.](02_Related_Works.md#tactile-reduction-yin)은 동작에 필요한 손바닥·손끝 센서군을 제거했을 때 성능이 낮아졌고, [Melnik et al.](02_Related_Works.md#tactile-reduction-melnik)은 센서의 활성 빈도와 Bit 제거에 따른 Q-value 변화가 일치하지 않을 수 있음을 보였다. 따라서 **드물게 활성화된다는 이유만으로 중요한 접촉 영역을 제외하지 않는다.** (Yin, §V-G, Table IV, PDF pp. 8–9; Melnik, §4, Table 8·Fig. 7, PDF pp. 14–15)

본 후보는 **정책에 전달할 주 접촉 지도의 선택**이며 물리적으로 반대편 센서를 제거하거나 읽지 않는 설계가 아니다. 전체 34채널의 취득·기록과 별도 안전 감독은 유지하는 방향으로 검토한다. 비선택 면의 접촉이 과업 수행에 필요한 조건에서는 입력을 유지하거나 표현을 확장해야 하며, 손목 F/T가 제외한 국소 접촉 정보를 항상 복원한다고 가정하지 않는다. 이를 근거 없이 별도의 간섭 원인 분류 기능으로 확대하지 않는다.

### 3.3.4. 비교 검증

| 조건 | 촉각 표현 | 검증 목적 |
| --- | --- | --- |
| **전체 채널 기준선** | Palm 17 + Dorsal 17, 동일한 접촉면 ID도 제공 | 선택 전의 정보와 비교. ID까지 포함하면 35D |
| **접촉면 선택 후보** | 접촉면 ID 1 + 선택한 면 17 = 18D | 비선택 면의 채널 생략이 성능·학습 효율에 미치는 영향 |

두 조건의 F/T·초기 정보·고유감각, Action·Controller, Reward, 네트워크 구조와 학습 예산은 동일하게 맞춘다. **정상적인 단면 접촉 조건**과 **비선택 면 접촉이 발생하는 조건**을 나누고, 실제 물체 목표 변위 성공률·이동 오차·접촉 소실·학습 진행과 비선택 면 활성 빈도를 비교한다. 안전 감독의 개입도 따로 기록하여, 외부 감독의 효과를 18D 정책의 능력으로 해석하지 않는다.

**주장의 범위는 “34D가 너무 커서 줄여야 한다”가 아니라, “지정된 Sweeping 동작에서 필요한 접촉 영역과 그 면의 정체성을 유지하면서 불필요한 채널을 생략할 수 있는지 검증한다”이다.** 접촉면 선택의 타당성과 허용 범위는 위 비교로 판단하며, 관측·행동 이력 설계는 이 절에서 추가하지 않는다.

<details>
<summary>기존 정책 개요도 — 수정 전 참고 자료</summary>

아래 이미지는 재구성 이전의 개요도다. 이미지에 포함된 이력 입력은 현재 Method 설계에서 제외하며, 현재 입력·출력 후보는 위 본문을 기준으로 한다.

![기존 강화학습 정책 설계 개요도](../../img/tactile_representation_fig2.png)

</details>
