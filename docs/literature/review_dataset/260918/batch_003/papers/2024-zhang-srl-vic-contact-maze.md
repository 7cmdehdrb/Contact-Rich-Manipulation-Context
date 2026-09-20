# SRL-VIC: A Variable Stiffness-based Safe Reinforcement Learning for Contact-rich Robotic Tasks

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B101`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Heng Zhang; Gokhan Solak; Gustavo J. G. Lahr; Arash Ajoudani
- Year: 2024
- Venue: IEEE Robotics and Automation Letters (accepted preprint)
- DOI / arXiv: Not stated / 2406.13744v1
- PDF version: Accepted preprint / arXiv v1
- Page count: 8
- SHA-256: `3c2dfc6bb3b833492ad46883b956ed75a2a0b51c5e4bf54c38b2f5e26ef3933d`
- PDF filename: Zhang 등 - 2024 - SRL-VIC A Variable Stiffness-Based Safe Reinforcement Learning for Contact-Rich Robotic Tasks.pdf
- 확인 범위: PDF pp.1–8 전체: introduction, related work, VIC, CMDP state/action/reward, offline/online training, simulation/real experiments, conclusion. Key pages 3, 4, 6, 8 rendered.

## 2. Relevance to This Review

`Relevant`

This blind contact task removes vision and combines net F/T, proprioceptive position, learned safety risk and impedance modulation. It directly shows that F/T alone does not supply environment geometry or contact locality, and uses controlled component ablations to test how force feedback and controller priors compensate.

## 3. Task

Blind, contact-rich maze exploration with collision safety and obstacle pushing

## 4. Method

### 4.1. Overall Pipeline

F/T (+ EE position for task policy) → task action candidate → safety critic; if risky, recovery action → [ΔP,K] → variable impedance controller → contact-rich maze motion.

### 4.2. Observation

Safety critic and recovery policy observe only 6D F/T. Task policy observes the same wrench plus 3D end-effector position. No camera, maze map or object pose is provided.

### 4.3. Action

Relative planar displacement [ΔP_x,ΔP_y] and stiffness [K_x,K_y]

### 4.4. Controller

Task-space variable impedance controller

### 4.5. Learning / Optimization Method

Safety critic and DDPG recovery policy are pretrained on scripted collision data, then updated online. SAC learns the task policy while the risk threshold selects task or recovery actions.

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 해당 없음 | No manipulated object; end-effector position is proprioceptive | Each step | Known goal is distinct from current object pose. [§III-B, PDF pp.3–4] |
| Orientation | 해당 없음 | Not applicable | Not applicable | Planar maze exploration. [§III-B, PDF pp.3–4] |
| Shape / Geometry | 미제공 | Maze map is not an observation | No | Fixed layout can be memorized indirectly through EE position. [§I and §III-B, PDF pp.1,3–4] |
| Physical Parameters | 미제공 | Not provided | No | Obstacle movability/stiffness is inferred only through interaction. [§IV, PDF pp.4–7] |

## 6. Missing Object Information and Compensation

Maze geometry, obstacle state and contact location are not observed
→ 6D F/T + end-effector position + safety-risk model + variable stiffness
→ wrench signals interaction, position supports goal-directed progress, and the learned risk/recovery mechanism avoids or exits unsafe contact.

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

Six force/torque values are said to come from an F/T sensor; real sensor model/source is not specified. [§III-B, PDF p.3]

### 8.2. Representation

[F_x,F_y,F_z,T_x,T_y,T_z] for all policies/critics; magnitude threshold defines constraint violation. [§III-B, PDF pp.3–4]

### 8.3. Role

Task observation, predictive safety state, recovery input, collision constraint and VIC feedback. [§III-B and Fig.2, PDF pp.3–4]

### 8.4. Required Assumptions

Calibrated F/T and threshold, known goal, task-space controller, and a training layout where absolute EE position is informative. [§III-B–IV, PDF pp.3–5]

### 8.5. Reported Limitation / Ambiguity

No contact location or map is recovered. Simulated F/T imprecision/dynamics mismatch caused poor initial transfer; one-maze training did not generalize to another shape. [§IV-C and conclusion, PDF pp.7–8]

## 9. Other Observations

- Proprioception: task policy gets absolute/current EE position.
- Vision: explicitly unavailable.
- History/recurrent state: not stated.
- State estimator: learned safety critic estimates risk, not environment geometry.
- Offline data: simulator-known collision samples from six predefined points.

## 10. Tactile–Other Modality Relationship

Tactile is not used. F/T provides a global interaction/risk signal and proprioceptive position supplies spatial progress. Their combination still does not identify wall/contact locality; successful navigation partly depends on a fixed learned layout.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | 6D F/T + 3D EE position | Available on the real robot. [§III-B, PDF pp.3–4] |
| Critic | No | Safety critic uses 6D F/T and candidate action | No map/GT pose input. [Eqs.4–6, PDF pp.3–4] |
| Reward | No | Distance from EE to known goal; collision/entrance/goal events | Uses robot state and monitorable events, not object GT. [§III-B, PDF p.4] |
| Termination | No | Constraint violation, leaving entrance, reaching goal, 500-step horizon | All are execution monitors. [§III-B4, PDF p.4] |
| Curriculum | Yes | Six known simulator points and scripted random collisions generate offline constraint labels | Training-data generation only, not runtime input. [§IV-B1, PDF p.5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| VIC and recovery jointly improve safety/task trade-off | Component ablation | SRL-VIC vs VIC without recovery vs recovery with K=300 or 1000 | SRL-VIC has best successes/violations and cumulative task success with low violations | §IV-B3; PDF pp.5–6 ; Fig.4 |
| Variable stiffness is needed around obstacles | Controlled controller comparison | SRL-VIC vs constant K=300/K=1000 | Low stiffness gets stuck; learned stiffness increases along obstacle motion while staying compliant laterally | §IV-B3; PDF p.6 ; Fig.5 |
| Safety critic uses more than instantaneous force | Risk analysis | Random move/stiffness samples and measured force | Risk correlates with ΔP, K and force spikes but is not a force copy | §IV-B4; PDF p.6 ; Fig.6 |
| Simulation sensing mismatch affects transfer | Failure analysis | Initial policy vs policy retrained with observation noise | Real success rises from 4/5 to 6/6 after OU-noise training | §IV-C; PDF p.7 |

## 13. Author-stated Limitations

저자 명시: one maze shape로 학습한 task policy는 다른 maze shape에서 exit를 찾지 못했다. Simulation과 real의 physical dynamics 및 F/T sensing 차이로 초기 정책이 충분히 robust하지 않았다. [§IV-C, PDF pp.7–8]

## 14. Author-stated Future Work

저자 명시: 더 일반화된 task scenario에서 평가하고 model-based RL을 도입해 unknown environment에서 safety와 robustness를 높인다. [§V, PDF p.8]

## 15. Review-relevant Findings

- Vision과 environment map 없이 6D F/T와 EE position으로 blind maze를 탐색한다.
- F/T는 net interaction과 collision risk를 제공하지만 contact point나 wall geometry를 복원하지 않는다.
- Task policy는 position을 함께 받아 fixed maze에서 진행 위치를 기억한다.
- Offline safety data는 simulator의 predefined points와 collision label을 사용하지만 runtime actor에는 제공되지 않는다.
- VIC/recovery component ablation으로 추가 정보와 controller prior의 효과가 검증된다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §III-B, PDF pp.3–4 |
| Object pose | 해당 없음; EE position only, PDF p.3 |
| Tactile | 사용하지 않음 |
| F/T | §III-B, PDF pp.3–4 |
| Reward | §III-B, PDF p.4 |
| Critic | Eqs.4–6, PDF pp.3–4 |
| Ablation | Fig.4–6, PDF pp.5–6 |
| Limitation | §IV-C–V, PDF pp.7–8 |
