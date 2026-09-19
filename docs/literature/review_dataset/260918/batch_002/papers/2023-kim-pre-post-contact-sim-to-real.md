# Pre- and Post-Contact Policy Decomposition for Non-Prehensile Manipulation with Zero-Shot Sim-To-Real Transfer

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B033`
- Authors: Minchan Kim; Junhyek Han; Jaehyung Kim; Beomjoon Kim
- Year: 2023
- Venue: IEEE/RSJ IROS 2023, 10644–10651
- DOI / arXiv: 10.1109/IROS55552.2023.10341657 / Not stated
- PDF version: Publisher PDF
- Version note: 선택 범위 내 다른 버전 없음
- Page count: 8
- SHA-256: `5143c8df90534fe6e6f15feb357bbff8e1a90988e5a737a345d71f5b178e7da7`
- PDF filename: `Kim 등 - 2023 - Pre-and Post-Contact Policy Decomposition for Non-Prehensile Manipulation with Zero-Shot Sim-To-Real.pdf`
- 읽은 범위: PDF pp.1–8 전체(본문·실험·한계·참고문헌), Fig.5/Table III p.7 렌더 확인. 별도 부록 없음.
- 근거: 이번 배치의 PDF 원문에서 새로 분석했다. 기존 상세 노트는 재사용하지 않았다. 아래 페이지는 PDF 1-based page다.

## 2. Relevance to This Review

**Partially Relevant**. Tactile/F/T 연구는 아니지만 접촉 조작에서 simulator 3D pose/shape를 쓰는 teacher와 실행 시 RGB keypoint를 쓰는 student의 정보 차이를 명시한다. 지속적인 시각 pose 정보가 있는 방법과 blind contact feedback을 비교하고 training-only object information을 분리하는 데 유용하다. Sensor compensation의 촉각 근거로 사용하지 않는다.

Screening 위치: §I/III, pp.2–5; Fig.3 p.5.

## 3. Task

Card relocation, bump를 넘는 pushing/reorientation, wall 위로 object 이동의 세 non-prehensile task. 성공은 goal position/orientation 기준이며 wall task는 orientation matching을 요구하지 않는다. (§IV-A, p.6)

## 4. Method

### 4.1. Overall Pipeline

RGB → 2D keypoint detector → pre-contact student EEF pose/width → RRT* approach → post-contact PPO with visual keypoints/proprioception → IK → joint position controller. Training teacher uses privileged 3D geometry. (§III–IV, pp.4–6)

### 4.2. Observation

Post actor q9, qdot9, current keypoints2×8, goal keypoints2×8, EEF pose, previous action. Pre teacher and real student use different inputs. No tactile or force observation. (Table I p.4; Fig.3 p.5)

### 4.3. Action

Post action contains EEF residual pose, joint stiffness and damping ratio; damping gain is derived from stiffness and ratio. Pre student outputs contact EEF pose and gripper width. (§III, pp.4–5)

### 4.4. Controller

Inverse differential kinematics followed by joint position control; controller gains predicted by policy. Real 10 Hz policy and 500 Hz controller; simulation controller 100 Hz. (§III–IV, pp.4–6)

### 4.5. Learning / Optimization Method

Jointly train pre/post PPO in simulation, supervise student from teacher trajectories, and train keypoint detector with synthetic heatmaps/KL plus InfoNCE. System identification, action residual curriculum and domain randomization support transfer. (§III-B, pp.5–6)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Eight current image-plane object keypoints; GT projection in sim, RGB detector in real | Each policy step | Goal keypoints are separate; no direct runtime 3D GT pose. 근거: Table I p.4; Fig.3/§III-B p.5 |
| Orientation | Tracking | Object orientation encoded by current keypoint arrangement | Each policy step | Not an explicit estimated quaternion input at deployment. 근거: §III-A/B, pp.4–5 |
| Shape / Geometry | 기타 | Fixed-task object prior; bbox keypoints; exact surface mesh in training teacher | Keypoints update; model shape fixed | Student does not receive teacher mesh/contact surface inputs; shape generalization remains future work. 근거: §III-A/B pp.4–5; §V pp.7–8 |
| Physical Parameters | 미제공 | No object parameter vector in actor | No | Fixed simulation density and DR are training settings. 근거: §III-B/IV-A, pp.5–6 |

## 6. Missing Object Information and Compensation

Exact simulator 3D pose/shape가 실물에서 없음 → teacher-student + RGB 2D keypoints → initial contact choice와 online manipulation을 실행한다. Object physical parameters를 직접 추출하지 않고 sensory representation에서 policy를 학습한다는 저자 설명이 있다. Current object vision이 없는 blind task의 compensation 사례는 아니다. (§I/III, pp.2–5)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음 / 해당 없음 (Table I/§III, pp.4–5)

### 7.2. Preprocessing

사용하지 않음 / 해당 없음 (Table I/§III, pp.4–5)

### 7.3. Policy Representation

사용하지 않음 / 해당 없음 (Table I/§III, pp.4–5)

### 7.4. Retained Information

사용하지 않음 / 해당 없음 (Table I/§III, pp.4–5)

### 7.5. Removed / Unavailable Information

사용하지 않음 / 해당 없음 (Table I/§III, pp.4–5)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음 / 해당 없음 (Table I/§III, pp.4–5)

### 8.2. Representation

사용하지 않음 / 해당 없음 (Table I/§III, pp.4–5)

### 8.3. Role

사용하지 않음 / 해당 없음 (Table I/§III, pp.4–5)

### 8.4. Required Assumptions

사용하지 않음 / 해당 없음 (Table I/§III, pp.4–5)

### 8.5. Reported Limitation / Ambiguity

사용하지 않음 / 해당 없음 (Table I/§III, pp.4–5)

## 9. Other Observations

Robot joint/EEF state와 previous action, current/goal keypoints를 사용한다. Goal은 initial pose에 대한 relative transform으로 정의되지만 current keypoints는 매 step 관측한다. Torque noise는 DR이며 torque observation이 아니다. (§III, pp.4–6)

## 10. Tactile–Other Modality Relationship

Tactile/F/T 없음. Review에서의 역할은 continuous vision 및 privileged teacher 데이터의 비교군이다. Sensor 없이 contact interaction을 수행하지만 이를 tactile compensation의 실증으로 확장하지 않는다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Actor | Yes during simulation; No exact GT at real deployment | Pre teacher initial/goal 3D poses; post sim projected GT keypoints; real pre-student/post use RGB keypoints | Teacher is not deployed; visual feedback remains online | §III-A/B, pp.4–5; Fig.3 |
| Critic | 미명시 | PPO used; separate critic observations unlisted | Asymmetric GT cannot be inferred | §III-A, p.4 |
| Reward | Yes | 3D current/goal keypoint distances, orientation/position success, mesh COM-to-finger distance; gain regularization | Training quantities; not all are actor observations | Eq.(1), p.4 |
| Termination | Yes | Collision/IK infeasibility for pre; drop/success/horizon for post | Simulation training termination; real evaluation success also pose-task dependent | §III-A, p.4 |
| Curriculum | Yes | 80% success trigger reduces action magnitude; teacher mesh samples; GT segmentation/keypoint labels | Training-only data and scheduling, not runtime true state | §III-B, pp.5–6 |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Controller reduces transfer gap | Controlled comparison | Same policy architecture/scheduling, joint-position controller vs OSC; default object, 15 real trials/domain | Proposed 0.87/0.87/0.87 vs OSC 0.13/0.07/0.00 for card/bump/wall. No force-sensor contribution comparison. | §IV-B/Table III, p.7 |
| Residual curriculum enables contact learning | Controlled comparison | Scheduled vs fixed safe residual limit | Bump/wall fixed version fails to learn; real card success 0.73 fixed vs 0.87 scheduled. | §IV-B, pp.6–7; Fig.5/Table III |
| Pre/post decomposition helps exploration | Architecture ablation | Pre/post versus single post policy from EE-ABOVE or EE-AT-RIGHT | Decomposition learns more efficiently; baseline curves stay below proposed. Exact curve values are not treated as tabulated statistics. | §IV-B, pp.6–7; Fig.5a |
| Privileged information distilled to real observation | Author explanation only; Controlled comparison (whole system) | Teacher 3D pose/mesh to student 2D keypoints; no student-input ablation | Real whole-system results establish execution with visual keypoints, not the necessity of each privileged input. | Fig.3/§III-B p.5; Table III p.7 |

## 13. Author-stated Limitations

Fixed environments와 objects에 한정되며 변경되면 새로운 policy를 학습해야 한다고 명시한다. Real generalization 평가 object는 training과 visual appearance가 같도록 칠했다. Highly non-rigid water tissue box가 가장 낮은 성공률을 보였다. (§IV-B/§V, p.7)

## 14. Author-stated Future Work

Shape information을 포함하여 다른 object shapes로 일반화하는 방향. (§V, pp.7–8)

## 15. Review-relevant Findings

- 실행 중 current object 2D keypoints가 갱신된다.
- Training teacher의 3D pose/mesh와 real student 입력은 다르다.
- Reward는 3D simulator object state를 쓴다.
- Critic privileged input은 미명시다.
- Tactile/F/T의 독립적 evidence는 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / current pose | Table I p.4; Fig.3 p.5 |
| Teacher / student | §III-A/B, pp.4–5 |
| Reward / termination | §III-A Eq.(1), p.4 |
| Curriculum / data generation | §III-B, pp.5–6 |
| Controller / ablation | §IV, pp.6–7; Table III |
| Limitation / future | §V, pp.7–8 |
