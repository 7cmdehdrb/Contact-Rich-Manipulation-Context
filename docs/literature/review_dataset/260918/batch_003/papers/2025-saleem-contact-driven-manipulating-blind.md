# A Contact-Driven Framework for Manipulating in the Blind

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B072`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Muhammad Suhail Saleem; Lai Yuan; Maxim Likhachev
- Year: 2025
- Venue: arXiv preprint
- DOI / arXiv: Not stated / 2510.20177v1
- PDF version: arXiv v1 (23 October 2025)
- Page count: 9
- SHA-256: `51f7500372c556c46f7e669226f264d551573e97939198e54ef0c9153841499c`
- PDF filename: Saleem 등 - 2025 - A Contact-Driven Framework for Manipulating in the Blind.pdf
- 확인 범위: PDF pp.1–9 전체; contact estimator, occupancy prediction/planning, simulation/real ablations, future work 및 Figures 1/3와 Tables I–II 렌더 확인.

## 2. Relevance to This Review

`Relevant`

Vision 없이 joint-torque contact sensing, contact history, learned structural priors와 planning을 결합해 unknown clutter에서 조작한다. Joint-torque localization의 ambiguity와 추가 geometry/kinematic assumptions, sparse contact를 occupancy/history로 보완하는 구조를 직접 분석할 수 있다.

## 3. Task

UR10e가 camera 없이 (1) sink cabinet 내부 pipes를 피해 back-wall valve에 도달하고 (2) cluttered shelf 깊숙한 target object에 도달해 retrieval한다. Unknown obstacle와 접촉하면 즉시 멈춰 retract하고 occupancy map을 update/replan한다. [§III/V, pp.2–7]

## 4. Method

### 4.1. Overall Pipeline

Joint positions/velocities/currents → momentum observer의 binary collision/residual torque → contact particle filter + known robot surface/normal/learned link estimator → partial occupancy map(history of contact/free sweeps) → CNN 또는 diffusion structural completion → CHS/CMAX weighted-A* planner → joint motion primitives; contact 시 retract/update/replan. [§IV, pp.3–6]

### 4.2. Observation

실행 관측은 joint configuration/velocity/torque current이다. Binary contact detection은 reliable로 취급하고 contact location 및 predicted voxel occupancy는 noisy estimate다. Planner는 start/goal configurations, robot geometry, contact history에서 만든 probabilistic occupancy를 받는다. Vision은 없다. [§III–IV, pp.2–6]

### 4.3. Action

Configuration lattice의 각 joint dimension을 따라 linearly interpolated unit motion primitive. Planned edge를 실행하고 contact가 발생하면 previous configuration으로 retract한다. [§III, pp.2–3]

### 4.4. Controller

Weighted A*가 CHS/CMAX 및 occupancy cost를 사용해 joint-space path를 계획한다. Low-level joint controller 세부는 원문에서 확인되지 않음. [§III/IV-C/V, pp.2–6]

### 4.5. Learning / Optimization Method

Contact/predictor/planner hybrid. Momentum observer와 CPF는 model-based state estimation, occupancy predictor는 3D U-Net style CNN 또는 RePaint diffusion을 supervised data로 학습, planner는 CHS/CMAX search다. RL은 아니다. [§IV–V, pp.3–7]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Obstacle/target object current pose는 제공하지 않음 | 해당 없음 | Known start/goal robot configurations는 current object pose가 아니다. [§III–V, PDF pp.2–8] |
| Orientation | 미제공 | Obstacle/object orientation vector 없음 | 해당 없음 | No object orientation tracking. [§III–V, PDF pp.2–8] |
| Shape / Geometry | 기타 | Partial/probabilistic voxel occupancy and learned structural prior | 접촉/비접촉 sweep마다 map 갱신 | Full mesh/CAD는 없으나 domain-specific pipe/shelf structural prior를 학습한다. [§IV-B/V pp.4–7] |
| Physical Parameters | 미제공 | Object mass/friction/compliance input 없음 | 해당 없음 | Environment는 static으로 취급한다. [§III/IV-C pp.2–6] |

## 6. Missing Object Information and Compensation

Unknown obstacle pose/shape → reliable binary contact + noisy contact location + contact-free swept volume history → partial occupancy map을 만든다. Partial map의 unexplored region → learned pipe/shelf structural prior → likely occupancy를 예측해 충돌 횟수를 줄인다.

Joint torque의 locality ambiguity → known robot surface/normal·motion-consistency·unexplored-space constraint·temporal link classifier + particle filter → contact location cluster를 추정한다. Prediction/localization error는 CHS가 binary contact fallback으로 흡수한다. [§IV-A–C, pp.3–6]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§I–VI, pp.1–8]

### 7.2. Preprocessing

사용하지 않음. [§I–VI, pp.1–8]

### 7.3. Policy Representation

사용하지 않음. [§I–VI, pp.1–8]

### 7.4. Retained Information

사용하지 않음. [§I–VI, pp.1–8]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§I–VI, pp.1–8]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

UR10e joint currents(토크에 선형 비례)와 commanded torque/robot model로 momentum observer residual external joint torque를 계산한다. Wrist F/T가 아니다. [§IV-A/V-B, pp.3,7]

### 8.2. Representation

Low-pass external torque residual $r(t)\approx\tau_{ext}$, thresholded binary collision flag, CPF particle별 candidate 3D contact force QP likelihood. [§IV-A, pp.3–4]

### 8.3. Role

Whole-arm contact detection 및 robot-surface contact location estimate; occupied voxel marking과 replanning trigger. [§IV-A–B, pp.3–5]

### 8.4. Required Assumptions

Known robot dynamics/Jacobians/surface points/normals/friction cones; 한 시점의 contact를 candidate point-force로 설명; environment static; binary detection reliable; contact candidate가 motion into surface 및 unexplored region에 있어야 함. [§III–IV-A, pp.2–4]

### 8.5. Reported Limitation / Ambiguity

Multiple contact point/force pairs가 같은 residual을 설명하며 noise/model error에 민감하다. 실물 4 cm 기준 localization accuracy는 73%에 그치지만 CHS가 binary detection으로 fallback한다. [§II/§IV-A/§V-B, pp.2,4,8]

## 9. Other Observations

Proprioception은 $q,\dot q,\tau$이다. Contact/non-contact execution history는 voxel map과 planner memory를 구성한다. State estimator는 momentum observer, CPF, temporal external-torque link MLP, CNN/diffusion occupancy predictor다. Goal은 robot goal configuration으로 주어지며 current object pose와 다르다. [§III–IV, pp.2–6]

## 10. Tactile–Other Modality Relationship

Tactile skin 없이 joint torque가 whole-arm contact event를 제공하지만 locality는 noisy하다. 이를 contact history, known robot geometry, structural occupancy prediction, binary-contact-aware planning으로 보완한다. 따라서 force만으로 object shape를 복원하지 않고, sparse interaction과 learned prior를 합쳐 partial environment model을 만든다. [§I–V, pp.1–8]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | 비-RL planning/estimation 연구. Simulation에서는 true collision point에 3 cm Gaussian noise를 더해 localization을 모델링하지만 실물 실행은 raw proprioception+CPF를 사용한다. [§III–V, pp.2–8] |
| Critic | Not applicable | 비-RL | 비-RL planning/estimation 연구. Simulation에서는 true collision point에 3 cm Gaussian noise를 더해 localization을 모델링하지만 실물 실행은 raw proprioception+CPF를 사용한다. [§III–V, pp.2–8] |
| Reward | Not applicable | 비-RL | 비-RL planning/estimation 연구. Simulation에서는 true collision point에 3 cm Gaussian noise를 더해 localization을 모델링하지만 실물 실행은 raw proprioception+CPF를 사용한다. [§III–V, pp.2–8] |
| Termination | Not applicable | 비-RL | 비-RL planning/estimation 연구. Simulation에서는 true collision point에 3 cm Gaussian noise를 더해 localization을 모델링하지만 실물 실행은 raw proprioception+CPF를 사용한다. [§III–V, pp.2–8] |
| Curriculum | Not applicable | 비-RL | 비-RL planning/estimation 연구. Simulation에서는 true collision point에 3 cm Gaussian noise를 더해 localization을 모델링하지만 실물 실행은 raw proprioception+CPF를 사용한다. [§III–V, pp.2–8] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Structural occupancy prediction이 contact-only planning을 가속 | Input/module ablation | CHS/CMAX alone vs +CNN/+Diffusion, 200 simulated problems/domain | CHS+CNN success 1.00 pipes/0.94 shelf; total time 200.22/148.34s vs CHS 347.14/322.02s. | §V-A; PDF p.7 ; Table I |
| Prediction benefit가 real robot로 전이 | Controlled comparison | CHS vs CHS+CNN, 20 runs/domain | Total time pipes 360.4→175.9s, shelf 407.5→138.0s. | §V-B; PDF p.7 ; Table II ; Fig.3 |
| CPF robustification의 contribution | Input ablation | Baseline CPF vs motion/workspace/link-estimator refinements | 4 cm 기준 localization 73%; refinements가 held-out accuracy +20 percentage points. | §V-B; PDF p.8 |
| Noisy map을 hard exclusion하면 completeness/성능 저하 | Controlled comparison | Occupancy-only planners vs CHS-integrated variants | False occupancy가 feasible path를 제거해 lower success; CHS는 reliable binary detection으로 fallback. | §V-A; PDF pp.6–7 ; Table I |

## 13. Author-stated Limitations

Contact localization은 inherently ambiguous/noisy하며 실물 4 cm accuracy 73%다. Structural predictor는 domain-specific training에 의존하고 diffusion은 update당 약 20 s로 느리다. Binary detections를 reliable로 가정하고 environment가 static이어야 하며, simulation contact estimator는 real CPF가 아니라 true collision point+3 cm noise로 모델링했다. [§II–V, pp.2,6–8]

## 14. Author-stated Future Work

Partial occupancy와 함께 “kitchen sink with pipes” 같은 natural-language prompt를 conditioning하는 CLIP/FiLM textual prior를 후속 방향으로 제시하며 extended version에서 상세화할 예정이다. [§VI, p.8]

## 15. Review-relevant Findings

- 실행 vision과 current obstacle/object pose는 제공되지 않는다.
- Joint torque는 reliable binary contact와 noisy contact location으로 분리해 취급한다.
- Contact-free sweep/contact history가 partial occupancy를 만들고 learned structural prior가 unexplored space를 보완한다.
- Known robot geometry/kinematics/friction와 static-scene 가정이 torque localization을 성립시킨다.
- CHS가 noisy localization/prediction을 hard truth로 쓰지 않고 binary contact fallback을 유지한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / problem | §III pp.2–3 |
| Contact detection/localization | §IV-A pp.3–4 |
| Object information / occupancy | §IV-B pp.4–5 |
| Planner / action | §IV-C pp.5–6 |
| Tactile | 사용하지 않음; §I p.1 |
| Evidence | Tables I–II p.7; §V-B p.8 |
| Limitation | §II/V pp.2,6–8 |
| Future | §VI p.8 |
