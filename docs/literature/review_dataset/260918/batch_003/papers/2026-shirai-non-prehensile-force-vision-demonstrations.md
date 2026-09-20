# Learning Non-Prehensile Manipulation With Force and Vision Feedback Using Optimization-Based Demonstrations

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B075`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Yuki Shirai; Kei Ota; Devesh K. Jha; Diego Romeres
- Year: 2026
- Venue: IEEE Robotics and Automation Letters 11(3), 2905–2912
- DOI / arXiv: 10.1109/LRA.2026.3655262 / Not stated
- PDF version: IEEE publisher version
- Page count: 8
- SHA-256: `651ac6aeab0d8601364a378bae7e00462f48f8562604762d2c6c602bc4b92d2e`
- PDF filename: Shirai 등 - 2026 - Learning Non-Prehensile Manipulation With Force and Vision Feedback Using Optimization-Based Demonst.pdf
- 확인 범위: PDF pp.1–8 전체(Conclusion/Limitations/Appendix 포함); Figures 2–8와 Tables I–VI 렌더 확인.

## 2. Relevance to This Review

`Relevant`

Runtime current object GT 없이 wrist F/T, object segmentation, proprioception history로 object pose/size/mass/friction/contact state를 추정해 non-prehensile manipulation policy를 실행한다. Training privileged information, force/vision 역할, F/T-only 성립 가정과 sim-to-real 한계를 모두 직접 분석할 수 있다.

## 3. Task

한 대 또는 두 대의 MELFA robot로 planar pivoting with wall, pivoting without wall, pushing을 수행한다. Relative EEF translation으로 object를 goal pose/orientation에 옮기며 unseen real objects에 zero-shot transfer한다. [§IV–V, pp.4–6]

## 4. Method

### 4.1. Overall Pipeline

CITO가 robot/object/contact-force/contact-location demonstrations 생성 → privileged object/contact state+sensor observation으로 SAC base policy 학습 → rollouts에서 GT privileged labels 수집 → RGB segmentation CNN + 5-step force/proprioception history TCN이 privileged state 추정 → deployment에서 estimator output+runtime EEF/wrist force를 base policy에 입력 → relative EEF command → OSC/stiffness controller. [Fig.2/§III–IV, pp.2–5]

### 4.2. Observation

Base policy state는 privileged object pose, mass/size, object/environment friction, predefined surface별 extrinsic contact bits와 non-privileged robot EEF position, binary robot-contact signal, wrist 2D force다. 실물에서는 privileged part를 FastSAM object segmentation과 5-step EEF/contact-force history를 쓰는 CNN+TCN estimator가 대체한다. [§III-B–C, pp.3–4]

### 4.3. Action

각 robot의 planar 2D linear relative EEF position command. Operational Space Control이 joint torque로 변환한다. EEF orientation은 고정한다. [§III-A–B, pp.2–3]

### 4.4. Controller

Simulation은 robosuite OSC, 실물 MELFA는 stiffness controller를 사용한다. Policy는 10 Hz, simulation은 500 Hz다. [§III-B/§IV, pp.3–5]

### 4.5. Learning / Optimization Method

MuJoCo에서 MLP actor/critic SAC를 사용한다. Vanilla, kinematics-conditioned, dynamics-conditioned rewards를 비교하고 CITO contact-force/contact-state demonstrations로 reward를 shape한다. 이후 CNN+TCN estimator를 simulator GT privileged state에 supervised MSE로 학습한다. [§III/§IV, pp.2–5]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Deployment estimator가 segmentation+force/proprioception history에서 SE(2) object position 추정 | Policy 10 Hz에서 갱신 | Base training에는 GT object pose, real execution에는 estimated pose. [§III–V, PDF pp.2–6] |
| Orientation | Tracking | Estimator가 SE(2) object orientation 추정 | Policy 10 Hz에서 갱신 | Goal orientation은 별도이며 current orientation estimate와 비교한다. [§III–V, PDF pp.2–6] |
| Shape / Geometry | 기타 | Estimator가 object size와 environment/contact-face relation을 추정 | Runtime estimator output 갱신; shape 자체는 static | Full mesh/CAD/category는 없고 cuboid size 및 predefined surfaces를 사용한다. [§III-B–C/§IV pp.3–5] |
| Physical Parameters | 기타 | Estimator가 mass, object/environment friction constants를 예측 | Runtime history에서 반복 추정 | Training actor/critic은 GT, deployment는 estimate. [§III-B–C pp.3–4] |

## 6. Missing Object Information and Compensation

Deployment의 GT object pose/size/mass/friction/extrinsic contact state 미제공 → object segmentation history + wrist-force/EEF/contact history → CNN+TCN privileged-information estimator → unchanged privileged base policy의 input으로 제공한다.

Force history만으로 object size uncertainty에서 reliability가 낮음 → vision segmentation을 추가 → geometry-related privileged variables를 보완한다. F/T 단독 contact localization을 주장하지 않으며 predefined surface contact bit는 multimodal estimator가 추정한다. [§III-C, p.4]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§III–VI, pp.2–6]

### 7.2. Preprocessing

사용하지 않음. [§III–VI, pp.2–6]

### 7.3. Policy Representation

사용하지 않음. [§III–VI, pp.2–6]

### 7.4. Retained Information

사용하지 않음. [§III–VI, pp.2–6]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§III–VI, pp.2–6]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

각 MELFA robot wrist의 6-axis force/torque sensor. Policy/estimator에는 planar 2D robot contact force가 사용된다. [§III-B/§IV, pp.3–5]

### 8.2. Representation

Current 2D contact force $\lambda_t^r$, binary robot-contact signal, 그리고 5-step(0.5 s) temporal history. Demonstration reward는 reference force direction을 사용한다. [§III-B–C/§IV, pp.3–5]

### 8.3. Role

Base policy non-privileged observation, object/contact/physical-property estimator input, dynamics-conditioned reward에서 force direction imitation. [§III-B–C, pp.3–4]

### 8.4. Required Assumptions

Rigid objects, quasi-static planar SE(2), EEF pose/camera/wrist force available, high-friction/repeatable contact, predefined extrinsic environment surfaces/contact faces, training distribution의 geometry/property coverage. [§III opening/§III-B/§IV, pp.2–4]

### 8.5. Reported Limitation / Ambiguity

Force history alone은 object size uncertainty에 취약해 segmentation이 필요하다. Sliding contact는 sim-to-real discrepancy가 크며 low friction의 incipient slip은 contact loss 없이 감지하기 어렵다. Net wrist force만으로 arbitrary contact locality를 복원하지 않는다. [§III-C/§V–VI, pp.4,6]

## 9. Other Observations

Proprioception은 robot EEF position과 action/control state다. Vision은 raw RGB 대신 FastSAM segmentation mask를 CNN으로 encode한다. 5-step history는 TCN이 사용한다. State estimator는 object pose, mass/size/friction, extrinsic contact bits를 명시적으로 출력한다. Goal pose는 reward/task specification이고 current pose estimate와 구분된다. [§III–IV, pp.2–5]

## 10. Tactile–Other Modality Relationship

Wrist F/T는 global contact load/direction과 temporal interaction dynamics를 제공하고, vision segmentation은 object extent/pose와 size uncertainty를 보완한다. 둘은 tactile와 결합되지 않는다. 저자는 sensor-only force가 in-distribution geometry에서는 충분해 보였지만 size uncertainty에서 reliability가 떨어져 vision을 추가했다고 직접 명시한다. [§III-C, p.4]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Yes in base training; No GT at deployment | GT object pose, mass/size/friction, extrinsic contact bits + sensor observations; real deployment substitutes estimator output | Privileged base policy는 unchanged이며 estimator가 GT를 대체. [§III-B–C/Fig.2, pp.3–4] |
| Critic | Yes | SAC MLP critic trained on same privileged/non-privileged state formulation | Actor/critic 모두 base-policy simulation state를 사용한 것으로 기술되며 asymmetric split은 없음. [§III-B/§IV, pp.3–4] |
| Reward | Yes | GT current/goal object pose, demonstration robot/object pose, reference contact force direction, extrinsic contact bits | Simulation-only reward shaping. [§III-B Eqs.2–4, pp.3–4] |
| Termination | Yes | Goal-set indicator/current object pose threshold; 300-step limit | Training/evaluation success uses GT object state. [§III-B/§IV, pp.3–4] |
| Curriculum | Not stated | Not stated | Domain randomization of mass/size/friction/controller gains and sensor noise is used, not formal curriculum. [§IV/Appendix, pp.4,6–7] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Dynamics/contact demonstrations improve sample efficiency | Controlled comparison | Vanilla RL vs kinematics-conditioned vs dynamics-conditioned SAC | Dynamics-conditioned learns fastest; pivoting without wall is learned only by dynamics-conditioned variant. | §V; PDF p.5 ; Figs.3,8 |
| Force-reference demonstrations improve robustness | Controlled comparison | Kinematics- vs dynamics-conditioned policy with varied mass input | Dynamics-conditioned consistently more successful and less sensitive to object-property variation. | §V; PDF p.5 ; Table I |
| RL tolerates model/privileged mismatch better than MPC | Controlled comparison | MPC vs dynamics-conditioned RL with object-length input offsets | At -5 mm MPC fails while RL succeeds; both fail at -10 mm. | §V; PDF p.6 ; Table III |
| Multimodal privileged estimator enables sensor-only real deployment | Controlled evaluation | Estimator predictions vs simulator GT; unseen real objects | Fig.4 shows predictions with small width bias; all three hardware tasks 5/5 without GT privileged information. | §V; PDF pp.5–6 ; Figs.1,4 |
| Contact dynamics cause sim-to-real gap | Failure analysis | Pivoting with wall vs without wall, 3 trajectories | Wall task has larger gap due to object-wall/table sliding contacts. | §V; PDF p.6 ; Fig.6 |

## 13. Author-stated Limitations

Rigid-object, quasi-static SE(2) assumptions limit deformable/3D manipulation. Long horizons increase demonstration difficulty and estimator error accumulation. High-friction surfaces are required for repeatability; low-friction incipient slip is difficult to detect without contact loss. CITO/simulator contact mismatch remains, and real wall sliding shows larger sim-to-real gap. [§III/§V–VI, pp.2,6]

## 14. Author-stated Future Work

Slip-aware estimation 또는 faster sensing/control로 low-friction trade-off와 task speed를 개선하고, deformable/3D 및 longer-horizon manipulation으로 확장해야 한다고 제시한다. [§VI, p.6]

## 15. Review-relevant Findings

- Base training actor/critic은 object pose/size/mass/friction/contact GT를 privileged input으로 사용한다.
- Real deployment에서는 segmentation과 five-step wrist-force/proprioception history가 이 GT를 explicit estimator로 대체한다.
- Object current pose는 deployment에서 estimator output으로 매 step Tracking된다.
- Wrist F/T만으로 locality를 복원하지 않고 predefined extrinsic contact bits를 multimodal하게 추정한다.
- Dynamics-conditioned reward는 force magnitude가 아니라 demonstration force direction을 사용한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / privileged state | §III-B pp.3–4 |
| Object estimator | §III-C p.4 |
| Force/F/T | §III-B/§IV pp.3–5 |
| Action/controller | §III-B/§IV pp.3–5 |
| Reward | §III-B Eqs.2–4 pp.3–4 |
| Evidence | §V/Figs.3–6/Tables I–III pp.5–6 |
| Limitation / Future | §VI p.6 |
| Domain randomization | §IV/Appendix pp.4,6–7 |
