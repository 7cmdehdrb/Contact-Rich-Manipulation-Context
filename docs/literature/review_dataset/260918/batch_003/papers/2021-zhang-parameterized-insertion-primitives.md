# Learning Insertion Primitives with Discrete-Continuous Hybrid Action Space for Robotic Assembly Tasks

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B098`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Xiang Zhang; Shiyu Jin; Changhao Wang; Xinghao Zhu; Masayoshi Tomizuka
- Year: 2021
- Venue: arXiv:2110.12618
- DOI / arXiv: Not stated / 2110.12618v1
- PDF version: arXiv v1, 25 Oct 2021
- Page count: 7
- SHA-256: `7f83be243717d5604186dd6daa8e92aa790631d594e2ccce7ef7a6c218cd98e1`
- PDF filename: Zhang 등 - 2021 - Learning Insertion Primitives with Discrete-Continuous Hybrid Action Space for Robotic Assembly Task.pdf
- 확인 범위: PDF pp.1–7 전체: abstract, related formulation, primitives, algorithm, state/reward, simulation, real experiments, conclusion. Key pages 3, 5, 6 rendered.

## 2. Relevance to This Review

`Relevant`

The paper exposes how current hole pose uncertainty is handled without vision: nominal relative pose and wrist wrench feed an RL policy whose force-thresholded primitives react to contact. It directly separates force-based contact detection from true contact localization and also exposes training-time pose GT in reward/termination.

## 3. Task

Peg-in-hole and connector insertion under uncertain hole pose using learned motion primitives

## 4. Method

### 4.1. Overall Pipeline

Relative peg pose/velocity + external wrench → TS-MP-DQN → primitive type and continuous parameters → velocity/impedance execution until projected force or travel limit → next primitive.

### 4.2. Observation

s=(x, x_dot, F_ext), where x is peg pose relative to the nominal hole pose, x_dot is velocity, and F_ext is the external wrench. The true hole pose is randomized around the nominal pose and is not separately observed.

### 4.3. Action

Discrete primitive type (translation/rotation/insertion) plus continuous velocity and force-limit parameters

### 4.4. Controller

Cartesian velocity commands with impedance control on the real robot; primitive terminates on projected-force or travel threshold

### 4.5. Learning / Optimization Method

Parameterized-action Q learning with an actor for continuous parameters, a main and twin Q network, clipped double Q targets and policy smoothing.

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Peg pose relative to nominal hole frame | Each policy step | Actual hole position is randomly perturbed and hidden. [§IV-A, PDF p.4] |
| Orientation | Tracking | Peg orientation relative to nominal hole frame | Each policy step | Actual hole yaw contains hidden perturbation. [§IV-A, PDF p.4] |
| Shape / Geometry | 미제공 | No geometry in policy observation | No | Peg/hole meshes define tasks and transfer sets only. [§IV, PDF pp.4–6] |
| Physical Parameters | 미제공 | Not stated | No | Impedance gains are controller settings, not observed object parameters. [§IV-C, PDF pp.5–6] |

## 6. Missing Object Information and Compensation

Actual hole pose is not observed; only a nominal frame is available
→ relative peg state + external wrench + force-terminated motion primitives
→ the policy probes contacts and changes primitive sequence to search, align and insert.

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§III–V, PDF pp.3–7]

### 7.2. Preprocessing

사용하지 않음. [§III–V, PDF pp.3–7]

### 7.3. Policy Representation

사용하지 않음. [§III–V, PDF pp.3–7]

### 7.4. Retained Information

사용하지 않음. [§III–V, PDF pp.3–7]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§III–V, PDF pp.3–7]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Simulator external wrench; real FANUC setup uses an F/T sensor. [§IV-A and §IV-C, PDF pp.4–5]

### 8.2. Representation

F_ext in the state; each primitive uses the projected force along its commanded direction and a learned threshold f_lim. [§III-A, PDF p.3]

### 8.3. Role

Contact feedback to terminate translation/rotation/insertion primitives and policy observation for reactive search. [Fig.1 and §III-A, PDF pp.1,3]

### 8.4. Required Assumptions

Known nominal hole frame, calibrated force and command direction, rigidly held peg, bounded pose uncertainty and impedance-controlled execution. [§III-A and §IV-A, PDF pp.3–4]

### 8.5. Reported Limitation / Ambiguity

The force threshold signals contact but does not identify the true hole pose or spatial contact point; the paper does not directly discuss wrench ambiguity. [§III–V, PDF pp.3–7]

## 9. Other Observations

- Proprioception: current relative peg pose and velocity.
- Vision: not used; explicitly proposed for future initial pose estimation.
- History / previous action: not included.
- State estimator: none; true hole offset remains latent.

## 10. Tactile–Other Modality Relationship

Tactile is not used. F/T supplies a contact stopping event and wrench observation, while proprioceptive relative pose provides motion progress. The actual hole offset remains latent and is handled through sequential contact-conditioned primitives.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | Relative peg pose/velocity to nominal hole + external wrench | These signals are available on the real robot; true hole perturbation is hidden. [§IV-A/C, PDF pp.4–5] |
| Critic | No | Same state and hybrid action | Twin Q networks receive no separately stated GT. [§III-B and Fig.2, PDF pp.3–4] |
| Reward | Yes | Exact simulation pose error \|\|x-x_goal\|\| | Used only to train in simulation. [Eq.10, PDF p.4] |
| Termination | Yes | Simulation goal/terminal flag; primitive force/distance thresholds | Task termination depends on simulated completion while primitive stopping is sensor based. [§II-A, §III-A, §IV-A, PDF pp.2–4] |
| Curriculum | Not applicable | No curriculum | Transfer learning is evaluated but no curriculum is described. [§III-C–IV, PDF pp.4–6] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Parameterized primitives improve learning and transfer | Controlled action-space comparison | TS-MP-DQN vs MP-DQN, discrete primitives, continuous SAC | TS-MP-DQN has the highest simulated success and faster convergence | §IV-B; PDF pp.5–6 ; Table I ; Fig.5 |
| Learned primitives transfer to real assembly | Sim-to-real controlled comparison | Four action/algorithm baselines on six real tasks | TS-MP-DQN obtains 86.7–100% across tasks and exceeds baselines | §IV-C; PDF p.6 ; Table II |
| Continuous primitive parameters matter | Representation/action ablation | Parameterized vs discretized primitive parameters | Parameterized version is substantially better on real tasks under larger hole uncertainty | §IV-C; PDF p.6 ; Table II |

## 13. Author-stated Limitations

독립 Limitation 절은 없다. 원문상 비전이 없어 nominal hole pose와 bounded perturbation에 의존하며, F/T contact threshold가 실제 hole pose나 contact locality를 복원하지는 않는다. [§IV-A and §V, PDF pp.4,6]

## 14. Author-stated Future Work

저자 명시: insertion 과정에 vision을 추가해 initial pose estimation을 제공하고, bimanual 및 deformable-object manipulation으로 확장한다. [§V, PDF p.6]

## 15. Review-relevant Findings

- Actor는 relative peg pose, velocity, external wrench를 사용하지만 실제 perturbed hole pose는 받지 않는다.
- Wrist F/T는 command direction으로 투영된 힘과 learned threshold로 primitive를 종료한다.
- F/T는 contact presence를 제공할 뿐 contact location이나 true hole pose를 직접 복원하지 않는다.
- Simulation reward와 task completion은 exact pose state를 사용하므로 execution observation과 분리해야 한다.
- Parameterized/discrete/continuous action 비교와 real sim-to-real 비교가 있다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §IV-A, PDF p.4 |
| Object pose | §IV-A, PDF p.4 |
| Tactile | 사용하지 않음 |
| F/T | Fig.1 and §III-A/IV-C, PDF pp.1,3,5 |
| Reward | Eq.10, PDF p.4 |
| Critic | §III-B and Fig.2, PDF pp.3–4 |
| Ablation | Fig.5 and Tables I–II, PDF pp.5–6 |
| Limitation | §V, PDF p.6 |
