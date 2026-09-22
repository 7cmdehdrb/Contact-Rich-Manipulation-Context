# Differentiable Compliant Contact Primitives for Estimation and Model Predictive Control

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [원래 물리 파라미터 적응 조사 A2](../reviews/2026-09-21_sweeping-physical-parameter-adaptation.md#a2)

> **사용자 확인 상태:** **미확인** — 상세 리뷰는 작성되었지만, 사용자가 아직 직접 확인하지 않은 논문이다. (2026-09-22)

## 1. 논문 정보와 확인 범위

- **제목:** Differentiable Compliant Contact Primitives for Estimation and Model Predictive Control
- **저자:** Kevin Haninger, Kangwagye Samuel, Filippo Rozzi, Sehoon Oh, Loris Roveda
- **게재:** 2024 IEEE International Conference on Robotics and Automation (ICRA 2024), Yokohama, Japan, May 13–17, 2024, pp. 17146–17152
- **DOI:** [10.1109/ICRA57147.2024.10611406](https://doi.org/10.1109/ICRA57147.2024.10611406)
- **확인 원문:** 사용자 제공 IEEE 출판본 PDF 7쪽 전체
- **파일 SHA-256:** 6a1af804a3e883ac46cc50337542ea9cd5702ccbf6e51647ebfdb307b30e0c13
- **원문이 안내한 코드/데이터:** Fraunhofer GitLab의 contact MPC 저장소
- **이번 정독에서 별도 확인하지 않은 자료:** 저자 제공 동영상, 공개 코드 실행 결과, GitLab 구현 세부, 원문 인용 논문의 전체 본문

이 논문은 contact-rich manipulation에서 필요한 접촉 기하와 동역학을 CAD 등 사전 모델에만 의존하지 않고, **로봇의 위치·토크 측정으로 compliant contact model의 파라미터를 추정하여 제어에 다시 사용하는 통합 프레임워크**를 제안한다. 같은 contact primitive를 오프라인 파라미터 fitting, 온라인 EKF 추정, gradient-based MPC에 공통으로 사용한다. [원문 Abstract, §I]

중요한 구분은 다음과 같다.

- 논문은 **마찰계수 추정**을 제안하거나 검증한 연구가 아니다.
- 온라인으로 추정 가능한 파라미터에는 stiffness vector, contact point, rest position 등이 포함되지만, **MPC 실험에서 실제로 온라인 갱신한 핵심 값은 contact rest position**이다.
- sensorless 실험에서는 flange F/T sensor를 **검증용 ground truth**로 사용하고, 추정기는 joint position과 motor current 기반 torque를 사용한다.
- sensored 실험에서는 joint torque까지 관측하여 stiffness와 contact geometry 관련 파라미터를 추정한다.
- contact model의 예측 오차가 작더라도 개별 파라미터가 실제 기하와 일치한다고 보장되지 않는 경우가 보고된다.

따라서 이 논문은 “모든 숨은 물성을 정확히 식별한다”기보다, **물리적 의미가 있는 저차원 접촉 모델을 추정하고 그 모델을 MPC에 연결하는 명시적 모델 기반 적응의 사례**로 읽는 것이 정확하다.

---

## 2. 문제 설정과 연구 동기

### 2.1. Contact-rich manipulation에서 왜 모델 파라미터가 중요한가

저자들은 문 열기, 병뚜껑 돌리기, 플러그 삽입과 같은 접촉 과업에서 contact normal, object inertia, contact stiffness 등 task parameter 변화에 대한 강인성이 필요하다고 설명한다. 이러한 값이 알려지거나 추정되면 interaction control이 개선될 수 있다. [원문 §I]

### 2.2. 기존 모델 기반 접근의 제약

기존 contact-aware planning은 contact geometry를 미리 알고 있다고 가정하는 경우가 많고, 실제로 CAD에서 contact geometry를 가져오는 경우가 있다. 이는 새로운 물체·환경마다 사전 모델 준비가 필요하고, 자연물이나 CAD가 없는 대상에 적용하기 어렵게 만든다. 저자들의 목표는 이 사전 모델 의존성을 줄이는 것이다.

### 2.3. 왜 compliant contact model인가

접촉을 완전한 rigid kinematic constraint로 두는 대신 compliance를 가진 spring-like contact primitive를 사용한다. 실제 robot/tool/environment compliance를 표현할 수 있고, force control·MPC·impact control·task monitoring과 연결할 수 있으며, 파라미터화된 모델을 자동미분 가능한 형태로 만들 수 있다는 점이 핵심이다.

---

## 3. 논문의 핵심 기여

### 3.1. 핵심 접촉 파라미터에 대해 미분 가능한 compliant contact primitive

단일 접촉을 다음 파라미터로 표현한다.

- stiffness vector $\mathbf{K}_i$
- TCP 좌표계의 contact location $\mathbf{x}_i$
- world 좌표계의 rest position $\mathbf{x}_i^o$

이 파라미터들이 robot dynamics에 들어간 상태에서 자동미분을 사용할 수 있도록 구성한다.

### 3.2. Multi-point contact를 parallel primitive로 표현

여러 contact primitive의 joint torque contribution을 합산하여 point, line, hinge와 같은 higher-order constraint를 표현한다.

### 3.3. 같은 모델을 세 가지 목적으로 사용

1. **Offline fitting:** gradient-based parameter fitting
2. **Online estimation:** EKF로 state와 contact parameter 공동 추정
3. **Online control:** 추정된 contact parameter로 MPC model 갱신

### 3.4. 공간 방향까지 포함하는 stiffness 추정

기존 1-DOF stiffness estimator의 fixed direction 가정을 확장해 stiffness magnitude뿐 아니라 **spatial direction**까지 모델에 포함한다.

---

## 4. Robot Dynamics

표준 serial manipulator dynamics는 다음과 같다. [원문 식 (1)]

$$
\mathbf{M}(\mathbf{q})\ddot{\mathbf{q}}+\mathbf{C}(\mathbf{q},\dot{\mathbf{q}})+\mathbf{B}\dot{\mathbf{q}}+\mathbf{G}(\mathbf{q})=\boldsymbol{\tau}_m+\mathbf{J}^{T}(\mathbf{q})\mathbf{F}_e.
$$

여기서 $\mathbf{q}$는 joint position, $\mathbf{M}$은 inertia matrix, $\mathbf{C}$는 Coriolis term, $\mathbf{B}$는 viscous damping, $\mathbf{G}$는 gravity torque, $\boldsymbol{\tau}_m$은 motor torque, $\mathbf{F}_e$는 TCP에 작용하는 external force다.

forward kinematics는 [원문 식 (2)]

$$
\mathbf{x}=\ell(\mathbf{q}),\qquad \dot{\mathbf{x}}=\mathbf{J}(\mathbf{q})\dot{\mathbf{q}},\qquad \ddot{\mathbf{x}}=\mathbf{J}(\mathbf{q})\ddot{\mathbf{q}}+\dot{\mathbf{J}}(\mathbf{q})\dot{\mathbf{q}}.
$$

토크 오차를 [원문 식 (3)]

$$
\tilde{\boldsymbol{\tau}}=\boldsymbol{\tau}_m-\mathbf{C}(\mathbf{q},\dot{\mathbf{q}})-\mathbf{G}(\mathbf{q})
$$

로 두어 이후 contact torque와 결합한다.

---

## 5. Differentiable Compliant Contact Model

### 5.1. 단일 contact force

$i$번째 접촉의 force는 다음과 같이 표현된다. [원문 식 (4)]

$$
\mathbf{F}_i=\mathrm{diag}(\mathbf{K}_i)\left(\mathbf{x}_i^o-\mathbf{x}_i^w\right).
$$

$\mathbf{K}_i\in\mathbb{R}^{3}$는 방향 성분을 포함한 stiffness vector, $\mathbf{x}_i^o$는 contact spring의 rest position, $\mathbf{x}_i^w$는 현재 world-frame contact point다.

### 5.2. Contact location

TCP frame에서 고정된 contact location $\mathbf{x}_i$를 두고 world 좌표에서

$$
\mathbf{x}_i^w(\mathbf{q})=\mathbf{p}(\mathbf{q})+\mathbf{R}(\mathbf{q})\mathbf{x}_i
$$

로 표현한다.

### 5.3. Stiffness magnitude와 normal direction의 결합 표현

저자들은

$$
\mathbf{n}_i=\frac{\mathbf{K}_i}{\|\mathbf{K}_i\|}
$$

로 contact normal을 정의하고 stiffness magnitude를 $\|\mathbf{K}_i\|$로 표현한다. 즉 $\mathbf{K}_i$ 하나가 **강성 크기와 공간 방향을 동시에 표현**한다.

### 5.4. Contact torque

contact Jacobian은

$$
\mathbf{J}_i=D_{\mathbf{q}}\mathbf{x}_i^w=D_{\mathbf{q}}(\mathbf{p}+\mathbf{R}\mathbf{x}_i)
$$

이며 joint-space contact torque는 [원문 식 (5)]

$$
\boldsymbol{\tau}_i=\mathbf{J}_i^{T}\mathbf{F}_i
$$

로 주어진다.

원문 식 (6)을 풀어 쓰면

$$
\boldsymbol{\tau}_i=\left(\mathbf{J}_p^{T}+D_{\mathbf{q}}^{T}(\mathbf{R}\mathbf{x}_i)\right)\mathrm{diag}(\mathbf{K}_i)\left(\mathbf{x}_i^o-\mathbf{p}-\mathbf{R}\mathbf{x}_i\right).
$$

즉 torque response에는 TCP 위치·회전, contact location, rest position, contact stiffness vector가 함께 반영된다.

---

## 6. Multi-point Contact Primitive

$N_c$개의 compliant contact를 병렬로 연결하면 총 contact torque는 [원문 식 (7)]

$$
\boldsymbol{\tau}_e=\sum_{i=1}^{N_c}\mathbf{J}_i^{T}\mathbf{F}_i.
$$

이를 분해하면

$$
\boldsymbol{\tau}_e=\mathbf{J}_p^{T}\sum_{i=1}^{N_c}\mathbf{F}_i+\sum_{i=1}^{N_c}D_{\mathbf{q}}^{T}(\mathbf{R}\mathbf{x}_i)\mathbf{F}_i.
$$

Fig. 3은 primitive 수를 늘려 point, line, hinge constraint를 표현할 수 있음을 보여준다. 복잡한 접촉을 하나의 거대한 모델로 직접 쓰기보다 **미분 가능한 compliant primitive의 조합**으로 만든다는 것이 핵심이다.

---

## 7. Discretized Dynamics와 Automatic Differentiation

stiff contact dynamics를 다루기 위해 semi-implicit integration을 사용한다. [원문 식 (8)–(12)]

$$
\mathbf{q}^{+}=\mathbf{q}+h\dot{\mathbf{q}}^{+}
$$

$$
\dot{\mathbf{q}}^{+}=\dot{\mathbf{q}}+h\boldsymbol{\delta}
$$

이며 정리하면

$$
\mathbf{q}^{+}=\mathbf{q}+h\dot{\mathbf{q}}+h^{2}\boldsymbol{\delta}.
$$

$\mathbf{B}=0$이면

$$
\boldsymbol{\delta}=\mathbf{M}^{-1}\left(\tilde{\boldsymbol{\tau}}+\boldsymbol{\tau}_e\right).
$$

contact parameter를 $\boldsymbol{\phi}$라 두면

$$
\begin{bmatrix}\mathbf{q}^{+}\\\dot{\mathbf{q}}^{+}\end{bmatrix}=f\left(\begin{bmatrix}\mathbf{q}\\\dot{\mathbf{q}}\end{bmatrix},\tilde{\boldsymbol{\tau}},\boldsymbol{\phi}\right).
$$

이 형태 덕분에 $\boldsymbol{\phi}$에 대한 parameter fitting gradient, EKF Jacobian, MPC dynamics derivative를 같은 모델에서 자동미분으로 계산할 수 있다.

---

## 8. Online Estimation State와 Linearization

온라인 추정할 contact parameter를 $\boldsymbol{\phi}_{est}$라 하면 augmented state는 [원문 식 (13)]

$$
\boldsymbol{\xi}=\begin{bmatrix}\mathbf{q}\\\dot{\mathbf{q}}\\\boldsymbol{\phi}_{est}\end{bmatrix}.
$$

EKF를 위해 dynamics를 이 state에 대해 linearize하여

$$
\boldsymbol{\xi}^{+}\approx \mathbf{A}\boldsymbol{\xi}+\mathbf{b}+\mathbf{w}
$$

형태로 만든다. [원문 식 (14)]

$D_{\mathbf{q}}\boldsymbol{\delta}$와 $D_{\boldsymbol{\phi}_{est}}\boldsymbol{\delta}$ 같은 derivative는 AD framework가 계산한다.

---

## 9. Offline Parameter Fitting

offline fitting은 robot measurement만 가지고 runtime에서 고정할 contact model parameter $\boldsymbol{\phi}_{fit}$을 찾는 과정이다. 저자들은 simplified expectation-maximization 형태로

1. Kalman filter로 full state trajectory의 mean/covariance 추정
2. 추정된 state trajectory를 고정하고 contact parameter를 gradient optimization

하는 과정을 반복한다.

원문 식 (15)의 핵심은 prediction error와 regularization을 최소화하는 것이다.

$$
\boldsymbol{\phi}_{fit}=\arg\min_{\boldsymbol{\phi}}\sum_{t=1}^{T}\left\|\boldsymbol{\mu}_{t+1}-f(\boldsymbol{\mu}_{t},\boldsymbol{\tau}_{m,t},\boldsymbol{\phi})\right\|+\text{regularization}.
$$

원문에 제시된 regularization coefficient는 $\beta_{K_i}=10^{-9}$, $\beta_{x_i}=5$다.

---

## 10. Online EKF

EKF는 joint position을 필수적으로 사용하고, joint torque가 제공되면 이를 추가로 관측할 수 있다.

joint position 관측은 [원문 식 (17)]

$$
\mathbf{q}^{m}=\mathbf{C}_{q}\boldsymbol{\xi}+\mathbf{v}_{q}
$$

이고 torque 관측은 [원문 식 (18)–(19)]

$$
\boldsymbol{\tau}^{m}\approx \mathbf{C}_{\tau}\boldsymbol{\xi}+\mathbf{v}_{m}
$$

로 linearize한다.

- **Joint position only:** torque는 input으로 취급
- **Joint position + joint torque:** 두 측정값을 observation으로 결합

따라서 외부 F/T sensor가 없어도 robot-side measurement를 이용한 contact estimation을 구성할 수 있다.

---

## 11. Observability 분석

contact parameter를 EKF state에 넣는 것만으로 추정 가능성이 자동 보장되는 것은 아니다. 논문은 linearized observability matrix를 구성하고, 충분조건으로

$$
\mathrm{rank}\left(D_{\boldsymbol{\phi}}\boldsymbol{\delta}\right)=3N_e
$$

에 해당하는 조건을 제시한다. [원문 §IV-C, 식 (23)–(25)]

예를 들어 여러 rest position을 동시에 추정할 때 contact들이 동일한 방향·동일한 torque sensitivity만 만들면 분리하기 어렵다. 특정 estimation problem의 observability condition은 AD framework를 이용해 점검할 수 있다.

이 절은 본 논문을 “EKF에 파라미터를 넣으면 자동으로 추정된다”는 식으로 해석하면 안 되는 직접적인 근거다.

---

## 12. MPC with Compliant Contact

### 12.1. Cartesian impedance controller

robot은 Cartesian impedance controller를 사용하며 [원문 식 (26)]

$$
\boldsymbol{\tau}_m=-\mathbf{J}_p^{T}\left(\mathbf{K}_{imp}(\mathbf{p}-\mathbf{x}^{d})+\mathbf{D}_{imp}\mathbf{J}_p\dot{\mathbf{q}}\right).
$$

control variable은 virtual rest position $\mathbf{x}^{d}$다.

### 12.2. Multiple-shooting MPC

horizon $H$ 동안의 $\mathbf{x}^{d}_{t:t+H}$를 최적화한다. [원문 식 (27)–(29)]

$$
\mathbf{x}^{d}_{t:t+H}=\arg\min_{\mathbf{x}^{d}_{t:t+H}}\sum_{i=t}^{t+H}c\left(\mathbf{q}_{i},\dot{\mathbf{q}}_{i},\mathbf{x}^{d}_{i},\hat{\boldsymbol{\phi}}_{est,t}\right).
$$

현재 추정된 contact parameter $\hat{\boldsymbol{\phi}}_{est,t}$가 MPC prediction model에 직접 들어간다.

### 12.3. Cost와 force constraint

원문 식 (30)은 position, velocity, force tracking을 함께 고려한다.

$$
c=\|\mathbf{p}-\mathbf{p}^{d}\|+Q_v\|\mathbf{J}\dot{\mathbf{q}}\|+\sum_i Q_f\|\mathbf{F}^{d}-\mathbf{F}_i\|.
$$

impedance controller가 만드는 effective force를 제한하기 위해 [원문 식 (31)]

$$
g(\mathbf{q},\mathbf{x}^{d})=F_{imp}-\|\mathbf{K}_{imp}(\mathbf{p}-\mathbf{x}^{d})\|_2
$$

를 사용한다.

---

## 13. 구현

원문 §VI의 구현은 다음과 같다.

- **Automatic differentiation / symbolic framework:** CasADi
- **Optimization:** IPOPT
- **Robot dynamics / kinematics:** Pinocchio with CasADi support
- **Robot inertial model:** manufacturer model 기반
- **수정:** motor inertia를 inertia matrix diagonal에 추가

controller loop 전체의 wall-clock timing, solver iteration 수, CPU 사양, 최악 실행시간은 본문에 정량적으로 제시되지 않는다.

---

## 14. 실험 1 — Sensorless External Force / Stiffness Estimation

### 14.1. Hardware와 조건

- **Robot:** Universal Robots UR16e
- **Task:** vertical contact
- **측정:** motor position + motor current, 500 Hz
- **F/T sensor:** flange F/T sensor는 validation reference로 사용
- **접촉력:** 약 105 N vertical contact

motor current를 torque로 변환하기 위해 gearbox ratio와 motor torque constant를 사용한다.

### 14.2. 비교한 observer

1. EKF + offline fitted stiffness
2. EKF + online stiffness estimation
3. momentum observer

### 14.3. Force estimate 결과

Momentum observer는 high-frequency electrical noise, gravity model의 low-frequency error, motion stop 시 discontinuity를 보인다. 장점은 단순하고 environment dynamics에 덜 의존한다는 점이다.

EKF observer는 high-frequency noise와 low-frequency error가 감소한다. offline fitted stiffness를 사용하는 EKF는 Z-force estimate가 안정적이었고, online stiffness EKF는 접촉 후 force estimate 수렴까지 약 **2.6 s lag**가 있었다. 저자들은 noise parameter나 initial covariance tuning으로 이를 해결하지 못했다.

### 14.4. Stiffness estimate 결과

직접 F/T measurement와 TCP pose로 least-squares fitting한 reference는 약 **25.8 N/mm**, proposed offline fitting은 약 **28.3 N/mm**이다.

online stiffness estimate는 약 2.6 s의 수렴 시간과 움직임 방향에 따른 magnitude variation을 보였다. Momentum-observer 기반 stiffness estimate는 noisy하며 motor current discontinuity에 따라 큰 jump가 나타났다.

---

## 15. 실험 2 — Joint Torque를 이용한 Sensored Estimation

joint torque measurement가 available한 경우 single contact point에 대해 다음 파라미터의 online estimation을 시험한다.

- $\mathbf{K}_i$
- $\mathbf{x}_i^o$
- $\mathbf{x}_i$

주요 결과는 다음과 같다.

- stiffness estimate는 서로 다른 contact material을 구분할 수 있었다.
- contact normal direction 변화도 감지할 수 있었다.
- force prediction error가 낮은 경우에도 **rest position과 contact location을 동시에 추정하면 parameter estimate가 실제 TCP geometry에서 멀어지는 현상**이 있었다.

즉 모델 출력 force가 잘 맞는 것과 hidden physical parameter가 유일하게 식별되는 것은 다른 문제다.

---

## 16. 실험 3 — Online MPC

### 16.1. Plane-following task

목표는 불확실한 높이의 plane을 따라 이동하면서 Z 방향 contact force를 **3 N**으로 유지하는 것이다.

설정:

- single contact model
- $\mathbf{K}_1=[0,0,2570]$
- horizon $H=13$
- $h=0.03$
- $F^d=3$ N
- $F_{imp}=15$ N

비교 결과 online rest-position estimation을 사용하지 않으면 plane height 오차 때문에 Z-force variation이 더 컸고, online estimation은 plane rest position 변화를 추정하여 이를 보상했다.

### 16.2. Pivoting task

두 개의 compliant contact로 hinge-like constraint를 표현한다.

- $H=13$
- $h=0.03$
- $F^d=15$ N
- $F_{imp}=30$ N
- $\mathbf{K}_1=[0,0,2570]$
- $\mathbf{K}_2=[3300,0,0]$

online으로 두 rest position $\mathbf{x}_1^o$, $\mathbf{x}_2^o$를 추정한다. Online estimation 사용 시 X/Z desired force의 steady-state tracking이 개선되었고, 몇 cm 수준의 rest-position 오차가 남는 no-estimation case에서는 tracking이 악화됐다.

### 16.3. 해석 제한

이 MPC 실험은 모든 contact parameter를 동시에 온라인 식별한 실험이 아니다. **MPC demonstration에서 online adaptation의 중심은 rest position estimation**이며 stiffness는 설정값으로 사용한다.

---

## 17. 무엇을 실제로 추정했는가

| 항목 | 모델 파라미터에 포함 | 오프라인/온라인 추정 실험 | MPC에서 온라인 갱신 |
| --- | --- | --- | --- |
| contact stiffness magnitude/direction $\mathbf{K}_i$ | O | O | 실험에서는 고정값 사용 |
| contact rest position $\mathbf{x}_i^o$ | O | O | **O** |
| TCP-frame contact location $\mathbf{x}_i$ | O | O | 주된 MPC adaptation 값 아님 |
| friction coefficient | **X** | **X** | **X** |
| object mass/inertia | robot dynamics에는 관성 모델 존재 | contact primitive 추정 대상으로 검증하지 않음 | X |
| rigid object pose | 직접적인 object-state estimator가 아님 | X | X |

따라서 이 논문은 **명시적 접촉 모델 추정 → MPC**의 근거로 사용하는 것이 적절하며, “마찰·질량을 추정하는 연구”로 확장해 설명하면 안 된다.

---

## 18. 논문 결과가 뒷받침하는 것과 그렇지 않은 것

직접 뒷받침되는 범위:

1. compliant contact primitive parameter를 robot measurement에서 offline/online으로 fit할 수 있다.
2. sensorless setup에서도 external force와 stiffness의 유용한 estimate를 얻을 수 있다.
3. joint torque가 있으면 stiffness와 contact geometry 관련 추정을 수행할 수 있다.
4. online rest-position estimation을 MPC model에 반영하면 uncertain surface height와 hinge geometry에서 force tracking을 개선할 수 있다.
5. multi-point compliant primitive로 hinge-like constraint를 표현할 수 있다.

이 논문만으로 입증되지 않는 범위:

- arbitrary clutter에서의 general manipulation
- friction coefficient identification
- mass/CoM identification
- visual occlusion 아래의 object pose tracking
- binary tactile + wrist F/T 기반 blind sweeping
- learned policy의 end-to-end physical adaptation
- contact parameter를 항상 고유하게 식별할 수 있다는 주장

---

## 19. 저자들이 밝힌 Limitation

논문에는 독립된 Limitations 절이 없지만 본문과 실험에서 다음 제약이 명시된다.

### 19.1. Observability 조건이 필요

contact parameter estimation은 local observability를 만족해야 한다. 원하는 parameter를 state에 추가하는 것만으로 추정 가능성이 보장되지 않는다. [원문 §IV-C]

### 19.2. Online stiffness estimation의 수렴 지연

sensorless vertical-contact 실험에서 online stiffness EKF는 약 2.6 s lag를 보였고, noise/covariance tuning만으로 이를 제거하지 못했다. [원문 §VI-A]

### 19.3. Parameter non-uniqueness / divergence 가능성

rest position과 contact location을 동시에 추정할 때 force prediction error는 낮지만 parameter estimate가 실제 geometry와 달라지는 현상이 보고된다. [원문 §VI-B]

### 19.4. Environment-specific model information에 의존

Momentum observer와 달리 EKF는 environment-specific compliant contact model 정보를 더 사용한다. 새로운 환경에 적용하려면 fitting 또는 estimation이 필요하다. [원문 §VI-A]

---

## 20. Future Work

원문 Conclusion에는 별도의 구체적인 Future Work 목록이 없다.

따라서 **원문에 명시된 독립적인 Future Work는 확인되지 않았다.**

저자들이 본문에서 가능성을 설명한 내용이나 정리자의 제안을 Future Work로 재분류하지 않는다.

---

## 21. 미명시 사항과 읽을 때 주의할 점

### 21.1. F/T sensor 제품과 사양

UR16e sensorless validation에서 flange F/T sensor를 사용했다고만 되어 있으며 모델명·range·resolution·accuracy는 본문에 명시되지 않는다.

### 21.2. Online MPC 계산 시간

CasADi + IPOPT를 사용한다고 명시하지만 solver의 평균/최악 계산시간, CPU 사양, real-time margin은 정량적으로 제시하지 않는다.

### 21.3. 접촉 마찰 모델

제안 primitive는 normal-direction compliance를 중심으로 설명되며 Coulomb friction coefficient를 online parameter로 추정하는 formulation이나 실험은 없다.

### 21.4. 모든 파라미터의 동시 추정 성공을 주장하지 않음

stiffness, rest position, contact location이 모두 differentiable parameter라는 사실과, 이들을 한 실험에서 모두 안정적으로 동시에 식별했다는 것은 다르다.

### 21.5. Sensorless의 의미

sensorless는 외부 F/T sensor가 추정기에 없다는 의미이지 robot motor current나 joint position까지 사용하지 않는다는 뜻이 아니다.

### 21.6. CAD-free의 범위

contact geometry를 CAD에서 직접 읽지 않고 추정할 수 있지만 robot model 자체는 Pinocchio 기반 dynamics/kinematics와 manufacturer inertial model을 사용한다. 전체 시스템이 model-free인 것은 아니다.

---

## 22. 프로젝트 관점에서의 직접 연결

이 절은 논문 자체의 주장과 구분한 **프로젝트 적용 해석**이다.

본 프로젝트는 sweeping 중 shape·질량·마찰·지지 조건 등 숨은 환경 조건에 대응하는 방법을 검토하고 있다. 이 논문은 그중 **명시적인 물성·접촉 모델을 별도 추정해 계획·제어에 제공하는 방향**의 대표적인 사례다.

| Haninger et al. | 본 프로젝트 |
| --- | --- |
| differentiable compliant contact model을 명시적으로 둠 | 최종 actor에서 별도 접촉 모델 추정기를 우선 두지 않는 방향 검토 |
| joint position/torque 기반 EKF | binary tactile + wrist wrench + proprioception/history |
| rest position/stiffness/contact location 추정 | 물성 자체 복원보다 적절한 sweeping action 선택이 우선 목표 |
| gradient-based MPC | RL policy |
| plane sliding / pivoting | shelf object sweeping |
| contact model observability가 핵심 | 부분 관측 contact state와 history 활용이 핵심 |

직접 얻을 수 있는 설계상 시사점은 다음과 같다.

1. **명시적 추정은 별도의 observability 문제가 있다.** 제한된 sensor가 있다고 해서 원하는 stiffness/contact geometry를 모두 분리할 수 있는 것은 아니다.
2. **행동에 필요한 모델과 정확한 물성 복원은 구분해야 한다.** force prediction이 맞더라도 개별 geometry parameter가 실제값과 달라질 수 있다.
3. **추정값을 제어에 쓰려면 추정 오차와 지연이 제어 성능에 직접 연결된다.** sensorless online stiffness에서 약 2.6 s lag가 나타난 사례가 이를 보여준다.
4. 본 프로젝트가 명시적 parameter estimator 대신 history-based policy를 우선 검토하는 것은 가능한 설계 선택이다. 다만 이 논문은 history-based policy가 더 우월하다는 근거가 아니며 두 접근의 우열을 직접 비교하지 않는다.

이 논문의 위치와 다른 대응 구조와의 비교는 [Sweeping의 숨은 물리 조건에 대한 명시적 추정과 이력 기반 대응](../reviews/2026-09-21_sweeping-physical-parameter-adaptation.md#a2)에서 함께 정리한다.

---

## 23. 원문 위치 빠른 색인

| 주제 | 원문 위치 |
| --- | --- |
| 연구 동기, CAD/contact geometry 문제 | §I, pp. 17146–17147 |
| 기여 요약 | §I, p. 17147 |
| robot dynamics | §II-A, 식 (1)–(3) |
| compliant contact primitive | §II-B, 식 (4)–(6), Fig. 3 |
| multi-point contact | §II-C, 식 (7) |
| semi-implicit integration | §III-A, 식 (8)–(12) |
| augmented state / linearization | §III-B, 식 (13)–(14) |
| offline fitting | §IV-A, 식 (15) |
| EKF | §IV-B, 식 (16)–(22) |
| observability | §IV-C, 식 (23)–(25) |
| impedance + MPC | §V, 식 (26)–(31) |
| sensorless experiment | §VI-A, Fig. 4–6 |
| sensored estimation | §VI-B |
| plane MPC | §VI-C.1, Fig. 7 |
| pivot MPC | §VI-C.2, Fig. 8 |
| conclusion | §VII |

---

## 24. 한 문장 요약

**미분 가능한 compliant contact primitive로 접촉 강성·방향·위치·rest position을 파라미터화하고, 이를 robot measurement에서 fitting/EKF로 추정하여 같은 모델을 gradient-based MPC에 갱신하는 명시적 contact-model adaptation 프레임워크이며, 실제 MPC에서 online rest-position adaptation이 uncertain plane·hinge contact의 force tracking을 개선했다.**
