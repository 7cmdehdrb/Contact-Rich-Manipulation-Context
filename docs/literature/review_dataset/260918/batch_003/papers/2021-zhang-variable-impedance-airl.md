# Learning Variable Impedance Control via Inverse Reinforcement Learning for Force-Related Tasks

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B099`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Xiang Zhang; Liting Sun; Zhian Kuang; Masayoshi Tomizuka
- Year: 2021
- Venue: IEEE Robotics and Automation Letters 6(2), 2225–2232
- DOI / arXiv: 10.1109/LRA.2021.3061374 / Not stated
- PDF version: IEEE Xplore publisher PDF
- Page count: 8
- SHA-256: `5b553563ff093de1450944b05f5f324759a69ea4b6751a13306ed3a54dca4cf2`
- PDF filename: Zhang 등 - 2021 - Learning Variable Impedance Control via Inverse Reinforcement Learning for Force-Related Tasks.pdf
- 확인 범위: PDF pp.1–8 전체: introduction, related work, controller, AIRL, observations/actions, simulation and real experiments, conclusion/limitations. Key pages 3, 4, 7, 8 rendered.

## 2. Relevance to This Review

`Partially Relevant`

The paper does not use tactile and does not infer contact locality, but it separates wrist F/T used for demonstration collection from execution observations, and compares force-action versus impedance-gain representations and short history. This is useful evidence about when force information is training-only and about force-action transfer limitations.

## 3. Task

Peg-in-hole and cup-on-plate variable-impedance manipulation learned from expert demonstrations

## 4. Method

### 4.1. Overall Pipeline

Expert F/T + tracking state → sliding-window gain labels/demonstrations → AIRL learns reward and variable-impedance policy; at execution [e,e_dot,(history)] → gain/force policy → impedance controller → robot.

### 4.2. Observation

Execution policy observes tracking error e and tracking velocity e_dot; an evaluated variant stacks the last five pairs. The wrist F/T signal is collected for expert demonstrations and used to estimate expert gains, not fed to the learned gain policy at execution.

### 4.3. Action

Diagonal Cartesian stiffness/damping gains or Cartesian feedback force, depending on experimental variant

### 4.4. Controller

Cartesian impedance controller; simplified law does not measure external force during policy execution

### 4.5. Learning / Optimization Method

AIRL alternates discriminator/reward learning and TRPO policy optimization. Learned reward is reoptimized for transfer settings; BC, force-action and constant-gain baselines are tested.

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Robot kinematics relative to fixed waypoint/trajectory | Each timestep | Attached peg/cup is represented through end-effector tracking error. [§III-B and §IV-A2, PDF pp.3–4] |
| Orientation | Tracking | Tracking error where task uses rotational components | Each timestep | Exact active components are task dependent. [§III-A–B, PDF p.3] |
| Shape / Geometry | 미제공 | Not in policy observation | No | Task fixtures define dynamics but are not encoded. [§IV, PDF pp.4–6] |
| Physical Parameters | 미제공 | Object properties not observed | No | Robot dynamics model is known to the controller. [§III-A, PDF p.3] |

## 6. Missing Object Information and Compensation

Object geometry/contact state is not observed and waypoints are fixed
→ tracking error/velocity + impedance feedback law + optional history
→ policy adapts gains along a known desired trajectory; expert F/T supplies training demonstrations only.

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§III–V, PDF pp.3–8]

### 7.2. Preprocessing

사용하지 않음. [§III–V, PDF pp.3–8]

### 7.3. Policy Representation

사용하지 않음. [§III–V, PDF pp.3–8]

### 7.4. Retained Information

사용하지 않음. [§III–V, PDF pp.3–8]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§III–V, PDF pp.3–8]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

A wrist F/T sensor measures human-applied six-dimensional force/torque during real demonstration collection. [§IV-B2, PDF p.7]

### 8.2. Representation

6D Cartesian force/torque demonstration; a ten-sample sliding window estimates diagonal stiffness/damping. Execution variants output either gain or feedback force. [§III and §IV-B2–3, PDF pp.3,7]

### 8.3. Role

Expert-data acquisition and expert gain estimation. The final gain policy does not observe the F/T signal. [§IV-B, PDF p.7]

### 8.4. Required Assumptions

Known fixed waypoints, robot dynamics model, diagonal positive gains and end-effector-attached object; controller uses a simplified impedance equation. [§III-A and §IV-A, PDF pp.3–4]

### 8.5. Reported Limitation / Ambiguity

The simplified law omits measured external force and leaves Cartesian dynamics coupled; force-action policy shows a large sim-to-real gap. No contact location is estimated. [Fig.7 and §V, PDF pp.7–8]

## 9. Other Observations

- Proprioception: e and e_dot are the core runtime inputs.
- History: a five-step stack is evaluated; it does not consistently improve results.
- Vision: absent; proposed as future workspace input.
- State estimator: sliding-window least squares estimates demonstration gains, not object state.

## 10. Tactile–Other Modality Relationship

Tactile is not used. A critical distinction is that F/T is a training-data modality here: execution relies on proprioceptive tracking error and a learned gain policy. Therefore the paper does not support a claim that wrist F/T continuously compensates missing object pose at deployment.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | Tracking error and velocity; optional five-step history | Robot-measurable signals. [§III-B and §IV-A2, PDF pp.3–4] |
| Critic | Not stated | TRPO value function details not separated | No asymmetric GT input is reported. [§III-B, PDF p.3] |
| Reward | No | AIRL reward r_theta(o,a) learned from demonstrations | Performance score used for evaluation is separate. [Eq.6–7 and §IV-A5, PDF pp.3,5] |
| Termination | Not stated | Trajectory horizon/task completion details | No privileged termination signal is specified. [§IV, PDF pp.4–7] |
| Curriculum | Not applicable | No curriculum | Not applicable. [§IV, PDF pp.4–7] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Gain-space reward transfers better than force-space reward | Controlled action-space comparison | Gain-AIRL vs force-AIRL, BC and constant gain under changed tilt/mesh/initial pose | Gain-AIRL is most robust; force policy can push in the wrong direction after dynamics change | §IV-A7; PDF pp.5–6 ; Tables I–III ; Fig.4–5 |
| Short history is not necessarily beneficial | Representation ablation | Single e/e_dot pair vs five-step history | History does not improve gain policy and can make force-AIRL harder to train | §IV-A2/A7; PDF pp.4–6 ; Tables I–III |
| Direct force actions transfer poorly to hardware | Failure analysis | Same force/gain policies in simulation and real robot | Force-AIRL exits the feasible workspace; gain policy has a smaller response gap | §IV-B4; PDF pp.7–8 ; Tables IV–V ; Fig.7 |

## 13. Author-stated Limitations

저자 명시: simplified impedance control law가 external force를 측정하지 않아 Cartesian dynamics가 coupled된다. 또한 waypoints를 fixed and given으로 가정한다. [§V, PDF p.8]

## 14. Author-stated Future Work

저자 명시: external force를 control law에 추가해 dynamics를 decouple하고, expert trajectory waypoints를 policy output에 포함하며 workspace image를 입력으로 사용한다. [§V, PDF p.8]

## 15. Review-relevant Findings

- 실행 actor는 tracking error/velocity를 사용하며 wrist F/T는 human demonstration 수집과 gain estimation에만 사용된다.
- F/T를 사용했다고 해서 실행 시 contact feedback policy라고 분류하면 안 되는 사례다.
- Five-step history는 평가되었지만 일관된 이득을 보이지 않았다.
- Gain action은 force action보다 dynamics 변화와 sim-to-real에 강했으며 이는 controller prior의 효과로 설명된다.
- Object geometry와 contact locality는 제공되거나 복원되지 않는다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §III-B and §IV-A2, PDF pp.3–4 |
| Object pose | §III-B, PDF p.3 |
| Tactile | 사용하지 않음 |
| F/T | §IV-B2–3, PDF p.7 |
| Reward | Eq.6–7, PDF p.3 |
| Critic | §III-B, PDF p.3 |
| Ablation | Tables I–III and Fig.7, PDF pp.4–8 |
| Limitation | §V, PDF p.8 |
