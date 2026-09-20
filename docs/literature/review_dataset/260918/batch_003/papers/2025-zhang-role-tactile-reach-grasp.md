# The Role of Tactile Sensing for Learning Reach and Grasp

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B102`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Boya Zhang; Iris Andrussow; Andreas Zell; Georg Martius
- Year: 2025
- Venue: IEEE International Conference on Robotics and Automation (ICRA)
- DOI / arXiv: 10.1109/ICRA55743.2025.11127409 / Not stated
- PDF version: IEEE Xplore publisher PDF
- Page count: 8
- SHA-256: `1ef0c13a3811f5228d4ca839620271751947f84d4bdbf5d5a33df7f443f3535c`
- PDF filename: Zhang 등 - 2025 - The Role of Tactile Sensing for Learning Reach and Grasp.pdf
- 확인 범위: PDF pp.1–8 전체: introduction, related work, RL/state/reward, tactile approximation, all representation/history/area/generalization/sim-to-real experiments, discussion/limitations. Key pages 3, 5, 6, 7 rendered.

## 2. Relevance to This Review

`Relevant`

This is a direct representation-ablation study of binary, magnitude, vector and regional tactile signals with vision, proprioception and history. It provides unusually strong evidence about what reduced tactile removes and what remains useful when visual object pose is imperfect.

## 3. Task

Two-finger reach-and-grasp with systematic comparison of tactile sensing representations

## 4. Method

### 4.1. Overall Pipeline

Vision/object state + proprioception + time + tactile history → SAC/MPO → arm joint positions + gripper width → joint impedance control → stability-tested grasp.

### 4.2. Observation

State is [TCP pose, gripper opening, visual object pose/type or image feature, tactile representation, remaining-step scalar], typically stacked for five steps. Simulation variants deliberately corrupt visual pose.

### 4.3. Action

Seven arm joint positions plus gripper opening width

### 4.4. Controller

Joint impedance controller interpolates 20-Hz policy output to 1 kHz on hardware

### 4.5. Learning / Optimization Method

Off-policy SAC and MPO with demo injection. Visual encoder can be pretrained for 10/100-object experiments; real policies use extensive domain/controller randomization.

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Simulation object pose with controlled noise; wrist vision/FoundationPose | Each step | GT in core simulation; estimated on hardware. [§III-A and §IV-B/E, PDF pp.2,4,6] |
| Orientation | Tracking | Same as position | Each step | OU/offset noise includes orientation. [§IV-B, PDF pp.4–5] |
| Shape / Geometry | 기타 | Object identity one-hot or implicit RGB | Each observation | Full mesh is not a policy input. [§III-A and §IV-D, PDF pp.2,5] |
| Physical Parameters | 미제공 | Not actor input | No | Friction/controller parameters are randomized only for training. [§IV-E, PDF p.6] |

## 6. Missing Object Information and Compensation

Visual object pose is noisy/biased and reduced tactile discards force or locality
→ tactile contact/force representation + proprioception + five-step history
→ tactile corrects local grasp behavior when vision is imperfect; history helps tracking noise but not fixed calibration bias by itself.

## 7. Tactile

### 7.1. Raw Sensor

Simulation: 50 independent 3D contact-force vectors per fingertip from 45 cuboids + 5 spheres. Hardware: two Minsight vision-based fingertips. [§III-B–C, PDF p.3]

### 7.2. Preprocessing

Whole-finger sum, contact threshold, vector magnitude, K=5/9/12 region selection, and optional global-vector concatenation. [§III-C and Table III, PDF pp.3,5]

### 7.3. Policy Representation

B (2 binary), M (2 magnitudes), V (two 3D vectors), BK/MK/VK regional signals; usually five-frame history. [Table II–III, PDF p.5]

### 7.4. Retained Information

B: presence; M: presence+magnitude; V: magnitude+direction but no locality; K variants add coarse spatial distribution. [§III-C, PDF p.3]

### 7.5. Removed / Unavailable Information

Binary removes magnitude/direction; magnitude removes direction; global aggregation removes contact locality; regional maps quantize and omit full-resolution deformation. [§III-C and §IV-C, PDF pp.3,5]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. V is aggregated fingertip tactile force, not wrist F/T. [§III-C, PDF p.3]

### 8.2. Representation

Not applicable [§III-C, PDF p.3]

### 8.3. Role

Not applicable [§III-C, PDF p.3]

### 8.4. Required Assumptions

Not applicable [§III-C, PDF p.3]

### 8.5. Reported Limitation / Ambiguity

Not applicable [§III-C, PDF p.3]

## 9. Other Observations

- Proprioception: TCP pose and gripper opening.
- Vision: exact/noised pose+type, or wrist RGB; FoundationPose on hardware.
- History: five frames is standard; 1/5/10 compared.
- Goal/time: remaining-step scalar.
- Demo injection: precomputed stable object/grasp poses seed replay.

## 10. Tactile–Other Modality Relationship

Tactile supplements visual object state specifically under perception imperfection. With perfect pose, all tactile variants are similar to no tactile. Under offset noise, global force vectors V/VK improve and stabilize performance; dense spatial detail is not always useful for this low-DoF gripper. This is directly tested rather than inferred.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Yes (simulation variants) | Exact object pose/type before controlled noise; real actor uses FoundationPose/RGB | The paper intentionally varies this oracle-like visual state. [§III-A and §IV-A/B, PDF pp.2,4–5] |
| Critic | No extra GT stated | Same multimodal state | No asymmetric critic is described. [§III–IV, PDF pp.2–6] |
| Reward | Yes | Simulation contact distances/forces and post-grasp stability under applied random forces | Not required by real execution after training. [§III-A and Table I, PDF p.2] |
| Termination | No | Fixed episode duration T | Stability check follows rollout. [§III-A, PDF p.2] |
| Curriculum | Yes | Precomputed stable placing and robust grasp poses for demo injection/object sampling | Simulator geometry and homogeneous-mass assumption are used. [§III-B, PDF p.3] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Tactile helps mainly when visual perception is imperfect | Sensor ablation | No tactile vs B/M/V/BK/MK/VK under perfect, OU and offset vision | Little change with perfect vision; V/VK improve low-variance performance under offset noise | §IV-A–B; PDF pp.4–5 ; Table II–III ; Fig.4,7 |
| Force direction is more valuable than dense magnitude maps | Representation/area ablation | V vs MK/VK at K=5/9/12, with/without global V | V and regional+V outperform magnitude-only maps; dense local input alone can be harder | §IV-C; PDF p.5 ; Fig.8 |
| Tactile improves object generalization | Sensor ablation | No tactile E vs global V for 10/100 seen and 63 unseen objects | V maintains higher performance as object diversity grows | §IV-D; PDF pp.5–6 ; Fig.9–10 |
| Tactile policies transfer to hardware | Sim-to-real comparison | Six tactile representations across three objects with/without disturbance | M/V generally exceed no-tactile policy; no-tactile policy-controlled closing is near zero | §IV-E; PDF p.6 ; Table V |

## 13. Author-stated Limitations

저자 명시: controlled simplified environment, rigid-body collision-based sensor approximation, deformation 미모델링, SAC/MPO 및 hyperparameter에 따른 결과 변화, sim-to-real 변수, computational limit로 online visual-tactile learning을 사용하지 못했다. [§V, PDF p.7]

## 14. Author-stated Future Work

저자 명시: active search와 information accumulation이 필요한 blind grasping, multi-finger in-hand manipulation, online visual-tactile feature learning. [§V, PDF p.7]

## 15. Review-relevant Findings

- Binary tactile은 접촉 presence만 남기고 magnitude/direction/local fine structure를 제거한다.
- Global V는 force magnitude와 direction을 남기지만 contact locality는 제거한다.
- Perfect object pose에서는 tactile 이득이 작지만 visual offset noise에서는 V/VK가 성능과 안정성을 높인다.
- Fine spatial resolution보다 global force direction이 2-finger grasping에서 더 유용할 수 있음을 ablation이 보인다.
- Actor는 simulation에서 GT object pose/type을 받을 수 있고 reward/demo injection은 추가 simulator GT를 사용하므로 runtime sensing과 분리해야 한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §III-A and Table II, PDF pp.2,5 |
| Object pose | §III-A/IV-B/E, PDF pp.2,4,6 |
| Tactile | §III-C and Table III, PDF pp.3,5 |
| F/T | 사용하지 않음; fingertip tactile force와 구분 |
| Reward | §III-A and Table I, PDF p.2 |
| Critic | §III–IV, PDF pp.2–6 |
| Ablation | Fig.4–10 and Table V, PDF pp.4–6 |
| Limitation | §V, PDF p.7 |
