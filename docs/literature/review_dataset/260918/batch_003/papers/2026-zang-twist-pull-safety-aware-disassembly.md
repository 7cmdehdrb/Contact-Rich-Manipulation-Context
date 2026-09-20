# Twist-pull as an execution skill primitive for robotic disassembly: Safety-aware skill augmentation under contact uncertainty

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B096`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Yue Zang; Xiazhen Xu; Yongquan Zhang; Fan Zhang; Wupeng Deng; Amir M. Hajiyavand; Yongjing Wang
- Year: 2026
- Venue: Journal of Manufacturing Systems 86, 22–37
- DOI / arXiv: 10.1016/j.jmsy.2026.02.020 / Not stated
- PDF version: Publisher PDF
- Page count: 16
- SHA-256: `7aa98be63d0d9e20ec58b0c39b370e14e55620e3fea46435e41e2878296a69ce`
- PDF filename: Zang 등 - 2026 - Twist-pull as an execution skill primitive for robotic disassembly Safety-aware skill augmentation.pdf
- 확인 범위: PDF pp.1–16 전체: abstract, introduction, formulation, controller, observation/action/reward, architecture, experiments, ablations, discussion, conclusion, appendix. Key pages 5, 8, 11, 14 rendered.

## 2. Relevance to This Review

`Relevant`

Hidden internal contacts and missing explicit contact state are handled with a 6D wrench, vision-derived object progress, history, compliant control and structured RL. It directly shows what information is needed when end-effector pose alone is insufficient and documents wrench distortion under misalignment.

## 3. Task

Twist–pull disassembly of cap–shaft, spanner-like, and real product assemblies under grasp misalignment and hidden contact resistance.

## 4. Method

### 4.1. Overall Pipeline

6D wrench + vision-derived Δd → structured DDPG branches → [dx, dy, k_c]; rule-based safety policy maps Δd history to pull velocity → Cartesian impedance/TP primitive → robot.

### 4.2. Observation

Actor observes [f_x, f_y, f_z, t_x, t_y, t_z, Δd]. Motion branch receives f_x, f_y, t_z; compliance branch receives f_z, t_x, t_y, Δd. Safety policy additionally uses Δd and previous pull velocities.

### 4.3. Action

Planar end-effector displacements dx, dy; rotational compensation gain k_c; safety policy separately modulates upward velocity

### 4.4. Controller

Cartesian impedance controller plus force-triggered twist–pull compensation and rule-based vertical-velocity safety policy

### 4.5. Learning / Optimization Method

DDPG. Actor and critic share the physically separated motion/compliance representation. Curriculum advances when recent success exceeds a threshold.

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Vision-derived relative object–gripper height Δd | Each timestep | Only axial relative progress is exposed, not full pose. [§4.1 and Fig.4, PDF p.5] |
| Orientation | Initial | Manually assigned/randomized initial orientation | No continuous update stated | Current orientation is not in actor observation. [§5.1 and Fig.8, PDF p.8] |
| Shape / Geometry | Initial | Known part dimensions and predefined structure cases | No | Used for action bounds/curriculum, not actor observation. [§5.1, PDF pp.8–9] |
| Physical Parameters | 미제공 | Not provided to actor | No | Friction, stiffness and interference remain hidden. [§1 and §6, PDF pp.1–2,14–15] |

## 6. Missing Object Information and Compensation

Full current object pose and hidden internal contact/friction are not modeled
→ 6D wrench + vision-derived Δd + history + compliant TP prior
→ wrench regulates motion/compliance, while Δd reports actual object progress/slip that gripper pose alone cannot reveal.

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§4–§6, PDF pp.5–15]

### 7.2. Preprocessing

사용하지 않음. [§4–§6, PDF pp.5–15]

### 7.3. Policy Representation

사용하지 않음. [§4–§6, PDF pp.5–15]

### 7.4. Retained Information

사용하지 않음. [§4–§6, PDF pp.5–15]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§4–§6, PDF pp.5–15]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Franka high-resolution joint torque sensors are stated; the policy uses a six-dimensional end-effector wrench. A separate wrist F/T transducer is not reported. [§4.1 and §5.1, PDF pp.5,7]

### 8.2. Representation

[f_x, f_y, f_z, t_x, t_y, t_z]; branch-specific subsets. Force/torque thresholds also terminate overload. [Eq.9 and §4.2, PDF pp.5–7]

### 8.3. Role

Interaction resistance observation, planar correction, compliance-gain modulation, and safety termination. [§4.1–§5.1, PDF pp.5–9]

### 8.4. Required Assumptions

Quasi-static rigid-body rotation-centre analysis, fixed estimated disassembly axis, low-speed execution, known kinematics and calibrated wrench. [§3 and §6, PDF pp.3–5,14]

### 8.5. Reported Limitation / Ambiguity

Grasp offset creates spurious wrench coupling; slip/deformation/hysteresis add variability; net wrench does not itself encode a contact location. [§3.1 and §6, PDF pp.3–4,14]

## 9. Other Observations

- Proprioception: end-effector/gripper pose is used by the impedance controller and Δd computation.
- Vision: segmentation or ArUco yields object–gripper relative height.
- History / previous action: the safety policy uses current/prior Δd and prior pull velocities.
- State estimator: no explicit hidden-contact estimator.

## 10. Tactile–Other Modality Relationship

Tactile is not used. The paper explicitly divides information between global end-effector wrench and vision-derived object progress: pose alone can diverge from actual object motion under compliant slip/deformation, so Δd supplements the wrench and gripper state.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | Sensor-derived wrench + Δd | No execution-time simulator GT identified. [§4.1–4.2, PDF pp.5–7] |
| Critic | No | Same structured observation/action representation | No asymmetric state is stated. [§4.2 and Fig.5, PDF p.7] |
| Reward | No | Object lift and Δd mismatch from the visual execution signal | No simulator-only state is identified. [Eqs.14–16, PDF p.6] |
| Termination | No | Extraction height, force/torque limits, grasp/vision failure, time limit | Execution monitors are described. [§5.1, PDF pp.8–9] |
| Curriculum | No | Predefined environments and recent success rate | No extra actor state; environment selection is training-only. [Algorithm 2 and §5.1, PDF pp.9–10] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Safety policy and structured observation/action improve training | Architecture/safety ablation | Structured+SP vs unstructured+SP vs no-SP and other RL/controller baselines | Structured+SP reaches about 99–100% final success in all five cases and converges more consistently | §5.2; PDF pp.10–11 ; Table 2 ; Fig.10 |
| Augmented skill transfers across contact structures | Controlled comparison | Policies trained on individual structures, curriculum policy, and no-RL baseline | Curriculum C0 achieves 10/10 on all five structures; no-RL is markedly lower on constrained structures | §5.2; PDF pp.11–12 ; Table 3 |
| Extreme uncertainty remains a failure mode | Failure analysis | Large radial offsets/internal interference | Force saturation or unstable interaction is reported; spanner cases do not stabilize within 80 episodes | §5.2–5.3; PDF pp.12–13 ; Table 4 |

## 13. Author-stated Limitations

저자 명시: TP는 axial separation과 rotational modulation이 지배적인 작업에 한정된다. 분석은 quasi-static rigid-body 가정이며 동역학·진동·히스테리시스를 명시적으로 모델링하지 않는다. 축 추정 편향, 극단적 misalignment/internal interference, slip은 실패를 유발한다. [§6, PDF pp.14–15]

## 14. Author-stated Future Work

저자 명시: 동적·히스테리시스 효과 모델링, stiffness adaptation과 k_c의 물리적 근거화, 더 넓은 execution-skill library와 multi-skill coordination, tactile/multimodal sensing 통합. [§6–7, PDF pp.14–15]

## 15. Review-relevant Findings

- Actor는 6D end-effector wrench와 vision-derived Δd만 받으며 full current object pose나 hidden contact state를 받지 않는다.
- Δd는 compliant interaction에서 gripper pose와 actual object displacement가 어긋나는 문제를 보완한다.
- F/T는 contact locality가 아니라 global resistance와 motion/compliance modulation에 사용된다.
- Misalignment가 wrench 성분을 결합해 해석을 왜곡한다는 한계를 직접 분석한다.
- 구조화 branch와 safety policy의 효과는 ablation으로 검증하지만 센서 modality 자체의 제거 ablation은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §4.1–4.2, PDF pp.5–7 |
| Object pose | Fig.4 and §5.1, PDF pp.5,8 |
| Tactile | 미사용; future work, PDF p.15 |
| F/T | §3.1 and Eq.9, PDF pp.3–5 |
| Reward | Eqs.14–16, PDF p.6 |
| Critic | Fig.5 and §4.2, PDF p.7 |
| Ablation | Fig.10 and Tables 2–3, PDF pp.10–12 |
| Limitation | §6, PDF pp.14–15 |
