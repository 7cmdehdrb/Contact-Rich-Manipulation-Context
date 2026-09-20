# ARMCL: ARM Contact point Localization via Monte Carlo Localization

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B105`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Adrian Zwiener; Richard Hanten; Cornelia Schulz; Andreas Zell
- Year: 2019
- Venue: IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)
- DOI / arXiv: Not stated / Not stated
- PDF version: IEEE Xplore publisher PDF
- Page count: 7
- SHA-256: `be0a61b1a1e88864e0be0a6900d0afe4e282dd9c9e7695c85cf10471e157cd36`
- PDF filename: Zwiener 등 - 2019 - ARMCL ARM Contact point Localization via Monte Carlo Localization.pdf
- 확인 범위: PDF pp.1–7 전체: introduction/related work, residual observer, mesh and particle models, assumptions, multi-contact discussion, simulation/real comparisons, discussion/conclusion. Key pages 3, 5, 7 rendered.

## 2. Relevance to This Review

`Relevant`

This paper directly answers how far joint-torque-derived wrench information can recover contact locality and which extra constraints make that possible. It explicitly analyzes non-uniqueness, multiple contacts, tangential forces, known geometry and model-error limitations.

## 3. Task

External contact point and force localization on a robot arm without tactile skin

## 4. Method

### 4.1. Overall Pipeline

q, q_dot, joint torques → momentum residual r → normalized torque likelihood on particles over robot mesh → resampling/density estimation → contact location distribution + SVD force amplitude.

### 4.2. Observation

Estimator inputs are proprioceptive joint positions, velocities and one-dimensional joint torques. Robot dynamics and surface geometry supply the contact Jacobian and normals.

### 4.3. Action

해당 없음. Estimated surface point(s), normals and force amplitude are outputs.

### 4.4. Controller

해당 없음. The method is an estimator that may support later collision recovery/manipulation.

### 4.5. Learning / Optimization Method

No learning is required for ARMCL; Monte Carlo localization and analytic likelihood are used. RF/MLP are comparison baselines.

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 해당 없음 | External object state is not estimated | Not applicable | Estimator localizes contact on robot surface. [§III, PDF pp.2–4] |
| Orientation | 해당 없음 | Not applicable | Not applicable | Not applicable. [§III, PDF pp.2–4] |
| Shape / Geometry | 기타 | Known triangular mesh of the robot, not external object | Static model | This prior is essential to restrict contact hypotheses. [§III-B–D, PDF pp.2–3] |
| Physical Parameters | 기타 | Known robot dynamics/model gains | Model based | External friction/tangent force is not identified. [§III-A/D, PDF pp.2–3] |

## 6. Missing Object Information and Compensation

Joint torque residual alone has non-unique contact solutions and no external-object geometry
→ known robot mesh/kinematics/dynamics + normal/single-contact assumptions + temporal particle belief
→ feasible surface locations are ranked and force amplitude is recovered after selecting location.

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§I–VI, PDF pp.1–7]

### 7.2. Preprocessing

사용하지 않음. [§I–VI, PDF pp.1–7]

### 7.3. Policy Representation

사용하지 않음. [§I–VI, PDF pp.1–7]

### 7.4. Retained Information

사용하지 않음. [§I–VI, PDF pp.1–7]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§I–VI, PDF pp.1–7]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Kinova Jaco2 one-dimensional joint torque sensors; momentum observer estimates external joint torque residual. This is not wrist F/T. [§I and §III-A, PDF pp.1–2]

### 8.2. Representation

Normalized residual r/||r||, predicted joint torque from each mesh point/normal, particle likelihood; contact force amplitude recovered afterward by SVD/norm ratio. [Eqs.1–9, PDF pp.2–4]

### 8.3. Role

Detect no-contact/contact, localize a probability distribution on the robot surface, and estimate normal-force amplitude. [§III, PDF pp.2–4]

### 8.4. Required Assumptions

Known surface mesh, kinematics and dynamics; contact force normal to surface; predominantly single contact; calibrated torque residual and detection threshold. [§III-D–F, PDF pp.3–4]

### 8.5. Reported Limitation / Ambiguity

1D joint torques cannot uniquely identify location; multiple contacts can collapse to a single equivalent one; tangent forces yield infinite solutions; geometry/model/acceleration affect accuracy. [§II, §III-F and §V, PDF pp.1,4,6–7]

## 9. Other Observations

- Proprioception: q, q_dot and motor torque.
- History: residual observer integrates dynamics and particle filter propagates belief.
- Vision: not used, but future RGB-D prior is proposed.
- Known geometry: complete robot surface mesh and normals.

## 10. Tactile–Other Modality Relationship

No tactile sensor is used. Spatial locality is reconstructed only by combining joint-torque residuals with a strong robot-geometry prior and a normal/single-contact model. Thus the result is not evidence that raw F/T alone uniquely identifies arbitrary contact.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | Estimator, not RL; simulation GT is used only for evaluation. [§III–VI, PDF pp.2–7] |
| Critic | Not applicable | 비-RL | Estimator, not RL; simulation GT is used only for evaluation. [§III–VI, PDF pp.2–7] |
| Reward | Not applicable | 비-RL | Estimator, not RL; simulation GT is used only for evaluation. [§III–VI, PDF pp.2–7] |
| Termination | Not applicable | 비-RL | Estimator, not RL; simulation GT is used only for evaluation. [§III–VI, PDF pp.2–7] |
| Curriculum | Not applicable | 비-RL | Estimator, not RL; simulation GT is used only for evaluation. [§III–VI, PDF pp.2–7] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| ARMCL improves over direct optimization without training | Controlled estimator comparison | ARMCL clustering variants vs direct optimizer, RF, MLP and friction-cone PF | ARMCL reaches up to 53% exact discrete class, ~0.11–0.12 m mean distance error and up to 159 Hz; different methods dominate different links | §IV-A; PDF p.5 ; Table I ; Fig.7 |
| Estimator converges on force/location | Controlled simulation test | Ten locations, two configurations and box-force inputs | Mean convergence 0.38±0.13 s; force error 1.1±0.6 N | §IV-B; PDF p.6 |
| Real torque sensing remains model limited | Real validation / failure analysis | Three manually applied real contacts with force-sensor ground truth | Location/angle errors depend on point; response delay ≈0.2 s and convergence ≈0.65–0.68 s | §IV-C; PDF p.6 ; Table II ; Fig.9 |

## 13. Author-stated Limitations

저자 명시: contact localization은 ambiguous하고 일부 link 위치가 동일하게 유력할 수 있다. 정확도는 dynamic model과 torque sensor에 제한되며 crosstalk와 high acceleration이 악화시킨다. 방법은 normal, 주로 single contact에 초점을 둔다. [§III-F and §V, PDF pp.4,6–7]

## 14. Author-stated Future Work

저자 명시: multiple contacts, 3D environmental sensor와 particle prior의 결합, tangential contact force의 영향을 조사한다. [§VI, PDF p.7]

## 15. Review-relevant Findings

- Wrist F/T가 아니라 1D joint torque와 momentum residual을 사용한다.
- F/T-only처럼 보이는 contact localization은 known robot mesh/kinematics/dynamics와 normal/single-contact assumption에 의존한다.
- Multiple contacts는 하나의 다른 contact와 동일한 residual을 만들 수 있어 무한한 해가 존재한다.
- Particle cloud는 단일 점보다 가능한 contact distribution을 보존한다.
- Real/simulation 비교와 estimator baseline이 있지만 tactile modality와 직접 비교하지는 않는다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §I and §III-A, PDF pp.1–2 |
| Object pose | 해당 없음 |
| Tactile | 사용하지 않음 |
| F/T | §III-A/D–F, PDF pp.2–4 |
| Reward | 비-RL |
| Critic | 비-RL |
| Ablation | Table I and Fig.7, PDF p.5 |
| Limitation | §V–VI, PDF pp.6–7 |
