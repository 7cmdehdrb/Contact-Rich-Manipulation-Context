# Framework for Robot Door Opening Based on Visual, Force, and Tactile Integration

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B106`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Valentin Šimundić; Luka Petrović; Matej Džijan; Robert Cupec
- Year: 2026
- Venue: IEEE Access 14, 11110–11128
- DOI / arXiv: 10.1109/ACCESS.2026.3655617 / Not stated
- PDF version: IEEE Access publisher PDF
- Page count: 19
- SHA-256: `bd087fc82028a8d1b677ef51dcaaecc814c89d493347214d020002ff04e8f227`
- PDF filename: Šimundić 등 - 2026 - Framework for Robot Door Opening Based on Visual, Force, and Tactile Integration.pdf
- 확인 범위: PDF pp.1–19 전체: introduction/related work, sensor-state machine, camera/contact correction, planning, implementation, simulation/real experiments, comparison, limitations/future work, appendices. Key pages 4, 12, 14, 17 rendered.

## 2. Relevance to This Review

`Relevant`

This paper gives an explicit F/T–tactile division: wrist F/T detects unexpected collisions globally, while a fingertip tactile sensor verifies local door-leaf contact and contact loss. Failure events and pose/history then correct an initially vision-derived object model, while the authors directly state that exact contact locality is still unknown.

## 3. Task

Autonomous opening of handleless cabinet doors with failure-driven camera/environment-model correction

## 4. Method

### 4.1. Overall Pipeline

RGB-D initial door/cabinet model → geometric planner → approach/insertion monitored by wrist F/T → opening monitored by fingertip tactile → failure pose/path/history → camera/model optimization → replan; contact loss also triggers RGB-D recapture.

### 4.2. Observation

There is no learned actor. The finite-state executor separately consumes wrist F/T threshold events, fingertip contact events, robot tool pose, RGB-D door state and accumulated failed-action traces.

### 4.3. Action

Planned joint-space approach, insertion and door-opening trajectories; retry after correction

### 4.4. Controller

Trajectory execution with sensor-threshold state transitions and replanning

### 4.5. Learning / Optimization Method

No policy learning. Camera intrinsics/extrinsics and environment vertices/planes are corrected by sampled contact-hypothesis optimization and Levenberg–Marquardt.

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Initial / event-triggered update | RGB-D model, optimized correction and recapture | At initial capture and after specified failures | Not continuously tracked every timestep. [§III-A/B/E, PDF pp.4–5] |
| Orientation | Initial / event-triggered update | Door hinge-axis pose and recaptured door angle | At capture/recapture | Opening path propagates a known hinge model between updates. [§III-A/E and §V-A, PDF pp.4–5,9] |
| Shape / Geometry | Initial | RGB-D polyhedral cabinet/door model: size, axis, leaf offset and planes | Updated after correction | Full known geometry is essential to candidate contacts and planning. [§III-A–C and §V-A, PDF pp.4,9] |
| Physical Parameters | 기타 | Rigid-body and fixed-hinge assumptions | No online estimation | Friction/compliance are not estimated. [§IV-C and §VIII, PDF pp.6–7,17] |

## 6. Missing Object Information and Compensation

Initial camera/cabinet model may be biased and exact contact correspondence is unknown
→ wrist F/T collision + fingertip contact/miss/loss + tool pose + failure trace + known polyhedral geometry
→ failures become geometric constraints that correct camera/environment parameters and trigger replanning.

## 7. Tactile

### 7.1. Raw Sensor

One XELA uSPa 44 sensor on a gripper fingertip; raw channels/units are not described. [§VI-B, PDF p.12]

### 7.2. Preprocessing

Significant tactile feedback is thresholded into contact; missing signal and later loss are detected. Exact preprocessing/threshold is not stated. [§III-D, PDF p.5]

### 7.3. Policy Representation

Discrete contact-established, missed-contact, and contact-loss events in the finite-state machine. [§III-D/E and Fig.2, PDF pp.4–5]

### 7.4. Retained Information

Local fingertip contact presence and continuity with the door leaf. [§III-D, PDF p.5]

### 7.5. Removed / Unavailable Information

Exact contact coordinate, patch distribution, force vector/magnitude and contacts outside the single covered fingertip remain unavailable. [§VIII, PDF p.17]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Robotiq FT300-S six-axis wrist F/T sensor. [§VI-B, PDF p.12]

### 8.2. Representation

External wrench threshold event; robot tool pose at collision is recorded. Component vector is not used by the correction method. [§III-D, PDF p.5]

### 8.3. Role

Detect unexpected collision during approach/insertion and trigger model correction and replanning. [§III-D, PDF p.5]

### 8.4. Required Assumptions

Calibrated tool/sensor transforms and threshold; known rigid polyhedral geometry/kinematics; calibration bias is the dominant model error. [§IV and §V, PDF pp.5–10]

### 8.5. Reported Limitation / Ambiguity

The precise contacting feature is unknown, so all candidate tool–environment feature pairs must be considered; force direction is left unused. [§IV-D and §VIII, PDF pp.7–8,17]

## 9. Other Observations

- Vision: initial door size/axis/offset and event-triggered door-state recapture.
- Proprioception: tool pose and known kinematics/frames.
- History: failed collisions, misses and scenes accumulate recursively.
- State estimator: RGB-D door-state method plus camera/environment optimization.
- Goal: desired door angle and planned contact pose.

## 10. Tactile–Other Modality Relationship

F/T and tactile are assigned different event semantics. Wrist F/T detects a collision anywhere relevant during free-space approach/insertion but cannot identify the contacting features. The single fingertip tactile sensor confirms contact with the intended door leaf and detects miss/loss during opening. This adds local task-specific contact identity/continuity, although exact locality still remains absent. The division is architecturally explicit but not sensor-ablated.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | Rule-based planning/optimization; simulation ground truth is used only to generate perturbations and evaluate error. [§III–VIII, PDF pp.3–17] |
| Critic | Not applicable | 비-RL | Rule-based planning/optimization; simulation ground truth is used only to generate perturbations and evaluate error. [§III–VIII, PDF pp.3–17] |
| Reward | Not applicable | 비-RL | Rule-based planning/optimization; simulation ground truth is used only to generate perturbations and evaluate error. [§III–VIII, PDF pp.3–17] |
| Termination | Not applicable | 비-RL | Rule-based planning/optimization; simulation ground truth is used only to generate perturbations and evaluate error. [§III–VIII, PDF pp.3–17] |
| Curriculum | Not applicable | 비-RL | Rule-based planning/optimization; simulation ground truth is used only to generate perturbations and evaluate error. [§III–VIII, PDF pp.3–17] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Failure-driven correction improves repeated operation | Correction ablation | Camera noise and optimization α/N_best settings across 1000 cabinets | Most settings exceed 99% and over 90% succeed within two actions; N_best=0 degrades performance | §VII-A; PDF pp.12–14 ; Table 4 ; Fig.8–10 |
| Offline contact calibration reduces retries | Controlled real comparison | Ten cabinet poses with vs without three-scene offline calibration | Both reach 100%; first-attempt success is 9/10 with calibration vs 6/10 without | §VII-B; PDF pp.14–15 ; Fig.11 |
| F/T–tactile role division | Author explanation only | No sensor-removal ablation | F/T triggers collision correction; tactile detects intended contact/miss/loss and recapture | §III-D–E; PDF p.5 |
| Exact locality remains unresolved | Failure/complexity analysis | All possible contact feature combinations vs sampled optimization | Runtime scales approximately linearly after fixed sampling; average 67.91 ms per failed action | §VII-C and §VIII; PDF pp.15–17 ; Fig.14 |

## 13. Author-stated Limitations

저자 명시: precise contact location/correspondence를 알 수 없어 모든 possible contact candidate를 고려해야 하며 계산 비용이 든다. 현재 구현은 segmentation error를 다루지 않고 rigid polyhedral tool/target을 가정한다. [§I and §VIII, PDF pp.2,17]

## 14. Author-stated Future Work

저자 명시: F/T force direction과 surface normal 일치도를 이용해 후보를 제거하고, 전체 gripper를 덮으며 precise contact localization을 제공하는 tactile sensor를 사용한다. 다른 rigid-polyhedral manipulation task로 확장한다. [§VIII, PDF p.17]

## 15. Review-relevant Findings

- Current door model은 RGB-D로 초기 제공되고 실패/접촉 손실 때만 갱신되며 연속 pose tracking은 아니다.
- Wrist F/T는 approach/insertion collision을 감지하지만 contact feature/locality를 제공하지 않는다.
- Single fingertip tactile은 intended door contact의 presence와 continuity를 추가해 miss/loss를 구분한다.
- Tactile을 써도 exact contact point는 알 수 없어 known polyhedral geometry와 후보 enumeration이 필요하다.
- Correction ablation은 강하지만 F/T-only 대 F/T+tactile sensor ablation은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §III and Fig.2, PDF pp.3–5 |
| Object pose | §III-A/E and §V-A, PDF pp.4–5,9 |
| Tactile | §III-D and §VI-B, PDF pp.5,12 |
| F/T | §III-D and §VI-B, PDF pp.5,12 |
| Reward | 비-RL |
| Critic | 비-RL |
| Ablation | Table 4 and Fig.8–12, PDF pp.12–15 |
| Limitation | §VIII, PDF p.17 |
