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
| 접촉 관측 | 영역별 Binary 촉각 후보 17차원, 보정된 6축 Wrench |

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

<details>
<summary>기존 정책 개요도 — 수정 전 참고 자료</summary>

아래 이미지는 재구성 이전의 개요도다. 이미지에 포함된 이력 입력은 현재 Method 설계에서 제외하며, 현재 입력·출력 후보는 위 본문을 기준으로 한다.

![기존 강화학습 정책 설계 개요도](../../img/tactile_representation_fig2.png)

</details>
