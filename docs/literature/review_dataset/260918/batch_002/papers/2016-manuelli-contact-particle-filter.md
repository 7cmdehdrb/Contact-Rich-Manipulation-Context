# Localizing External Contact Using Proprioceptive Sensors: The Contact Particle Filter

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B054`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Lucas Manuelli; Russ Tedrake
- Year: 2016
- Venue: IEEE/RSJ IROS 2016, pp.5062–5069
- DOI / arXiv: Not stated / Not stated
- PDF version: Publisher version
- Page count: 8
- SHA-256: `d7330c53000689c6109986b637cf330e0ba72cc7df78e879548df861c84de453`
- PDF filename: Manuelli 및 Tedrake - 2016 - Localizing external contact using proprioceptive sensors The Contact Particle Filter.pdf
- 확인 범위: PDF pp.1–8 전체; Fig.3–4 및 Table I/§VI를 렌더 확인. 별도 부록 없음.

## 2. Relevance to This Review

`Relevant`

Wrist F/T 단독 연구는 아니지만 joint-torque residual로 접촉 위치를 복원할 때 필요한 geometry·dynamics·friction 조건과 multi-contact 비식별성을 직접 다룬다. 따라서 force 정보의 locality 복원 범위와 추가 가정을 판단하는 핵심 근거로 포함한다. 조작 policy 학습 성능을 제시하는 논문으로 취급하지 않는다.

## 3. Task

Rigid-body robot 표면의 미측정 외부 접촉을 검출하고 접촉점 위치/힘을 추정한다. Simulated Atlas(36 DoF, 30 actuated joints)에서 1–3개 접촉을 추적하며 위치 오차와 처리 시간을 평가한다. Manipulation action policy는 아니다. [§V, p.5]

## 4. Method

### 4.1. Overall Pipeline

Joint position/velocity/torque + dynamics model + known foot wrenches → generalized momentum residual → robot surface의 candidate contact particles → friction-constrained QP likelihood → particle update/resampling 및 contact set 증감 → estimated contact locations. [§III–IV, pp.1–5]

### 4.2. Observation

Momentum observer 입력은 robot $q,v,\tau$ 및 dynamics, known contact wrench다. CPF 자체 realtime 입력은 $q$와 residual $\gamma$이며 초기 complete robot surface mesh가 필요하다. 알려진 foot contacts를 residual에서 빼기 위해 simulation에서 실제 Atlas의 3축을 넘어서는 full 6-axis foot F/T를 제공한다. 외부 object pose/vision/tactile 입력은 없다. [§III-A p.2; §V p.5]

### 4.3. Action

해당 없음. 출력은 particle-set 기반 contact location과 해당 QP의 contact force이며 robot action이 아니다.

### 4.4. Controller

해당 없음. Localization estimator를 평가하며 접촉 반응 controller를 구현해 비교하지 않는다. [§V–VII, pp.5–8]

### 4.5. Learning / Optimization Method

학습 없음. Contact Particle Filter(CPF), 각 particle 위치를 고정한 convex QP의 residual fit를 likelihood로 사용한다. Contact count는 residual이 충분히 설명되는지로 particle set을 추가/제거한다. 각 set 50 particles, Gaussian motion prior를 robot 표면에 재투영한다. [§IV–V, pp.2–5]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | 외부 contact object pose 입력 없음 | 해당 없음 | 추정 출력은 robot 표면 contact location이다. [§III–IV, PDF pp.1–5] |
| Orientation | 미제공 | 외부 object orientation 없음 | 해당 없음 | Robot q와 object orientation을 구분. [§III–IV, PDF pp.1–5] |
| Shape / Geometry | 미제공 | 외부 object geometry 없음; 대신 robot complete surface mesh를 초기 제공 | Robot mesh 자체 고정; q에 따라 위치 변환 | Object geometry 미제공이지만 known robot geometry에 강하게 의존. [§IV pp.2–4; §V p.5] |
| Physical Parameters | 미제공 | 외부 object parameter 없음; 대신 robot inertia/mass/dynamics와 friction cone 사용 | Robot model 고정 | 시뮬레이션은 정확한 inertial parameter 및 joint friction 없음. [§V-A p.5; §VI-A p.7] |

## 6. Missing Object Information and Compensation

미지의 contact location과 contact count → joint-torque residual + complete robot surface + kinematic Jacobian + friction cone + temporal particle prior → 관측 torque를 설명하는 가능한 접촉점을 추정한다. 힘만으로 유일해지는 것이 아니며 서로 다른 접촉 조합이 같은 residual을 만들면 비식별적이다. [§IV pp.2–5; §VI-B p.7]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§III–IV, PDF pp.1–5]

### 7.2. Preprocessing

사용하지 않음. [§III–IV, PDF pp.1–5]

### 7.3. Policy Representation

사용하지 않음. [§III–IV, PDF pp.1–5]

### 7.4. Retained Information

사용하지 않음. [§III–IV, PDF pp.1–5]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§III–IV, PDF pp.1–5]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Actuated joint torque measurements와 momentum observer가 estimated external joint torque를 생성한다. 알려진 발 지지 하중을 빼기 위해 simulated 6-axis foot F/T가 별도로 필요하다. Wrist 6-axis wrench 단독 입력이 아니다. [§III-A p.2; §V p.5]

### 8.2. Representation

외부 generalized joint torque residual $\gamma\approx\tau_{ext}$; contact force는 3D point force로 모델링하고 contact torque는 0으로 둔다. 여러 접촉은 Jacobian-transposed force 합으로 나타낸다. [Eqs.2–6,15] [§III–IV pp.2–4]

### 8.3. Role

Collision/contact detection, number-of-contact management, contact localization 및 force estimation. 별도 tactile sensor 입력 또는 reward는 없다. [§III–IV, PDF pp.1–5]

### 8.4. Required Assumptions

Rigid robot, 정확한 dynamic/torque model, known complete link surfaces/Jacobians, contact friction cones(4-edge polyhedral approximation), no contact moment point-force model, Gaussian residual noise, link-frame zero-velocity motion prior. Multi-contact update는 다른 접촉 위치를 고정하는 근사를 사용하며 새로운 contacts가 순차적으로 도착한다고 가정한다. 알려진 foot wrenches는 제거해야 한다. [§III–IV pp.1–5; §VI pp.7–8]

### 8.5. Reported Limitation / Ambiguity

Model/friction error와 외부 접촉을 proprioception만으로 구분할 수 없는 사례를 든다. 동일 residual을 만드는 서로 다른 contact sets는 비식별적; patch/continuous contact는 point-force 근사 시 weighted location으로 합쳐질 수 있다. 동시 접촉이나 다른 set의 잘못된 추정이 divergence를 유발할 수 있다. [§VI-A–E, pp.7–8]

## 9. Other Observations

Robot joint position/velocity/torque와 known foot support wrench, static robot mesh/dynamic prior, 이전 particle distributions를 사용한다. Vision, goal, previous policy action은 없다. Motion prior는 applied control input에 의존하지 않는다고 명시한다. [§III–V, pp.1–5]

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않는다. 알려진 robot geometry와 friction feasibility가 torque residual의 공간적 모호성을 줄인다. §VI-F는 wrist/shoulder F/T를 추가하면 generalized torque 공간의 정보가 증가할 수 있다고 제안하지만 별도 sensor-combination 실험은 하지 않는다. [pp.6–8]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | 비학습 estimator. Simulator contact 위치는 평가 기준이며 CPF 실행 입력이 아니다. 비교 two-step 방법에는 contact link identity를 추가 제공했다고 footnote에 명시(p.6). [§V, p.5] |
| Critic | Not applicable | 비-RL | 비학습 estimator. Simulator contact 위치는 평가 기준이며 CPF 실행 입력이 아니다. 비교 two-step 방법에는 contact link identity를 추가 제공했다고 footnote에 명시(p.6). [§V, p.5] |
| Reward | Not applicable | 비-RL | 비학습 estimator. Simulator contact 위치는 평가 기준이며 CPF 실행 입력이 아니다. 비교 two-step 방법에는 contact link identity를 추가 제공했다고 footnote에 명시(p.6). [§V, p.5] |
| Termination | Not applicable | 비-RL | 비학습 estimator. Simulator contact 위치는 평가 기준이며 CPF 실행 입력이 아니다. 비교 two-step 방법에는 contact link identity를 추가 제공했다고 footnote에 명시(p.6). [§V, p.5] |
| Curriculum | Not applicable | 비-RL | 비학습 estimator. Simulator contact 위치는 평가 기준이며 CPF 실행 입력이 아니다. 비교 two-step 방법에는 contact link identity를 추가 제공했다고 footnote에 명시(p.6). [§V, p.5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Geometry/friction-constrained estimation의 localization | Controlled comparison | CPF vs two-step line-of-force method; 후자에 contact link identity 추가 제공 | 두 contact 예에서 CPF는 추정하지만 two-step은 허용되지 않는 wrench를 선택하여 surface intersection을 잃음. | §V-B; PDF p.6 ; Fig.4 |
| Noise와 multi-contact 조건의 localization | Controlled comparison | 1/2/3 contacts, 각 10 N, residual noise 0/0.1/0.2 | 대부분 3 cm 이내라고 본문 보고; noise 증가 시 저하. 정확한 dynamics 및 joint friction 없는 simulation 조건이다. | §V-A; PDF pp.5–6 ; Fig.3 |
| 추가 wrist/shoulder F/T 가능성 | Author explanation only | 실제 sensor-addition ablation 없음 | 추가 measured wrench가 identifiability를 높일 수 있는 수학적 설명; 실험 검증 아님. | §VI-F; PDF p.8 |
| 비식별성과 model-error ambiguity | Failure analysis | 동일 residual을 만드는 contact sets; friction과 wall contact 예 | CPF가 항상 유일한 실제 contact configuration을 복원하는 것은 아님. | §VI-A–B; PDF p.7 |

## 13. Author-stated Limitations

정확한 robot model/torque 측정 의존, non-identifiable contact sets, point-contact restriction, approximate multi-contact update의 divergence, 순차 contact arrival 가정을 명시한다. 실제 hardware가 아닌 정확한 관성 및 friction-free simulation이다. 구현 시간은 1/2/3 contacts에서 161/244/395 ms이며 42회 simulation에서는 divergence가 없었다. [§V/Table I/§VI, pp.5–8]

## 14. Author-stated Future Work

Surface sampling/projection 계산 최적화로 속도를 개선할 수 있다고 설명한다. Wrist/shoulder F/T 등의 추가 proprioceptive sensor를 확장된 generalized-coordinate measurement에 통합하는 extension을 제안한다. 명시적인 hardware deployment 계획은 확인되지 않는다. [§V-C pp.6–7; §VI-F p.8]

## 15. Review-relevant Findings

- 관측은 단일 net wrist wrench가 아니라 joint-wise external torque residual이다.
- Known robot surface mesh, dynamics 및 friction cone이 contact locality 복원에 필요하다.
- Multi-contact도 항상 식별 가능하지 않으며 temporal initialization이 수렴에 영향을 준다.
- Patch contact의 분포를 직접 복원하는 방법은 아니다.
- Simulated full foot F/T를 사용하여 known support wrench를 제거한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / residual | §III-A p.2; §V p.5 |
| Object / robot geometry | §IV p.2; §V p.5 |
| Tactile | §I–II p.1: 사용하지 않음 |
| F/T / assumptions | §III–IV pp.1–5 |
| Reward / critic | 비학습 estimator |
| Comparison | §V-B/Fig.4 p.6 |
| Limitations | §VI pp.7–8 |
| Future / extensions | §V-C/§VI-F pp.6–8 |
