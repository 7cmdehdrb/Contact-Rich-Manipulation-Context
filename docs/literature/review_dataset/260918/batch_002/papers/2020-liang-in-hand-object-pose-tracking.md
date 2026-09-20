# In-Hand Object Pose Tracking via Contact Feedback and GPU-Accelerated Robotic Simulation

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B041`
- Authors: Jacky Liang; Ankur Handa; Karl Van Wyk; Viktor Makoviychuk; Oliver Kroemer; Dieter Fox
- Year: 2020
- Venue: 2020 IEEE International Conference on Robotics and Automation (ICRA), 6203–6209
- DOI / arXiv: Not stated / Not stated
- PDF version: IEEE conference publisher PDF
- Version note: 선택 범위 내 다른 버전 없음; PDF에 DOI는 명시되지 않음
- Page count: 7
- SHA-256: `52e13e7a78ceab0d86ebd0b7b5f4b0b7137c52cd79f9330d774df98dc96b4313`
- PDF filename: `Liang 등 - 2020 - In-Hand Object Pose Tracking via Contact Feedback and GPU-Accelerated Robotic Simulation.pdf`
- 읽은 범위: PDF pp.1–7 전체(본문, Algorithm 1, Fig.2–4, 결론, 참고문헌). Fig.3–4의 contact ablation과 real failure를 렌더 확인. 별도 supplement 없음.
- 근거: 이번 배치의 PDF 원문에서 새로 분석했다. 기존 상세 노트는 재사용하지 않았다. 아래 페이지는 PDF 1-based page다.

## 2. Relevance to This Review

**Relevant**. 초기 vision pose 이후 조작 중 vision 없이 fingertip BioTac에서 추정한 3D contact-force vectors와 robot state/history를 physics simulations에 대조해 6D in-hand object pose를 30 Hz로 추적한다. Wrist wrench가 아니라 tactile-derived force이며, known sensor pose·object mesh·initial visual belief·forward dynamics 가정을 요구하고 banana slippage에서 모든 hypotheses가 발산하면 회복하지 못하는 한계를 직접 보여 준다.

Screening 위치: Abstract/§I, PDF pp.1–2; §III, pp.2–5; §IV–V, pp.5–6.

## 3. Task

Vision으로 초기 object pose distribution을 만들고, 조작 중 contact feedback과 robot controls를 parallel simulations에 맞추어 6D in-hand pose를 추적한다. 평가 trajectory에는 pick/place, in-hand rotation, finger gaiting과 inertial/table-contact slip이 포함된다. (§I/§IV, PDF pp.1,5)

## 4. Method

### 4.1. Overall Pipeline

Initialize K physics simulations from an initial visual pose distribution, replay the real robot controls, compare simulated and real contact/kinematic observations, then resample and perturb pose/physics hypotheses. The lowest-cost simulation supplies the current pose. (§I/§III-B, pp.1–3)

### 4.2. Observation

Estimator observation contains joint positions, fingertip sensor poses/orientations, per-finger 3D contact-force vectors and optional translational/rotational slip; it uses the full observation/control history through a rolling cost window. (§III-A–C, pp.2–3)

### 4.3. Action

The estimator does not output manipulation actions. Desired joint-position controls from teleoperated trajectories are copied to every simulation. (§III-A/§IV, pp.2,5)

### 4.4. Controller

Real and simulated hand use joint-angle PD control; gains are tuned so step responses match. (§IV-A, p.6)

### 4.5. Learning / Optimization Method

Non-RL sample-based optimization: WRS, REPS and PBO update simulation state/object pose/physics parameters every T steps; GT pose is used only for simulation ablation and endpoint evaluation. (§III-D–E/§IV, pp.3–6)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Initial visual distribution then position of minimum-cost simulation hypothesis | Approximately 30 Hz | Real PoseRBPF first/last poses initialize/evaluate; they are not continuous execution input. 근거: §I/§III-B, pp.1–3; §IV-B, pp.5–6 |
| Orientation | Tracking | SE(3) pose hypothesis selected by observation cost | Approximately 30 Hz | ADD penalizes symmetric orientation differences; current real GT is not available throughout. 근거: §III-A–D, pp.2–4; §IV, pp.5–6 |
| Shape / Geometry | 기타 | Known simplified object collision mesh; YCB model/point cloud for evaluation | Fixed | Method does not infer novel object geometry. 근거: §I/§IV-A, pp.1,5 |
| Physical Parameters | 기타 | Mass, friction and other simulation parameters θ sampled and optimized | Optimizer update every T steps | Best θ need not equal true physical values; it is optimized for observation cost. 근거: §III-D–E, pp.3–4 |

## 6. Missing Object Information and Compensation

Continuous visual pose가 가려짐 → initial visual belief + BioTac-derived fingertip forces + robot kinematics/control history + known mesh/dynamics hypotheses → 최저 observation-cost simulation의 SE(3) pose를 현재 추정으로 선택한다. 이는 물체 pose를 actor에 직접 넣는 정책이 아니라 별도 estimator이며, pose가 전혀 필요 없는 blind control과도 다르다. (§III, pp.2–5)

## 7. Tactile

### 7.1. Raw Sensor

Real robot has one BioTac on each of four fingertips. The raw electrode vector is not passed directly to this estimator. (§IV, PDF p.5)

### 7.2. Preprocessing

A previously trained model estimates a 3D contact-force vector from BioTac electrodes. Force magnitude threshold defines contact. Real translational/rotational slip is not estimated. (§III-C/§IV, pp.3,5)

### 7.3. Policy Representation

No policy. Estimator cost compares per-finger force magnitude/direction and binary contact over a time window, together with joint/sensor pose; simulated ablation optionally includes slip terms. (§III-A–C, Eqs.(1)–(3), pp.2–3)

### 7.4. Retained Information

Sensor/fingertip identity, 3D force magnitude and direction, contact presence; simulated slip direction/status when enabled. (§III-A–C, pp.2–3)

### 7.5. Removed / Unavailable Information

Raw electrodes, dense contact patch/local geometry and exact within-skin contact point are absent; real experiments omit slip terms. (§III-A–C/§IV, pp.2–5)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Each BioTac's electrodes are mapped by a pretrained model to a 3D contact-force vector; this is fingertip tactile-derived force, not wrist F/T. (§IV, p.5)

### 8.2. Representation

For each fingertip, force magnitude and vector-direction difference plus thresholded contact agreement enter the cost. (§III-C, Eq.(3), p.3)

### 8.3. Role

Real/sim force agreement ranks parallel pose/dynamics hypotheses and periodically updates their states/parameters. (§III-B–D, pp.2–4)

### 8.4. Required Assumptions

Known fingertip sensor pose and object mesh, calibrated force estimator, synchronized robot actions, credible simulator/contact model and initial visual belief. (§III-A–E, pp.2–4)

### 8.5. Reported Limitation / Ambiguity

Contact forces do not uniquely determine pose; optimization maintains multiple physics hypotheses. Large slip can make all simulations diverge, after which later updates cannot recover. (§III-E/§IV-B, pp.4,6)

## 9. Other Observations

Joint positions와 각 fingertip sensor pose/orientation, replayed controls, initial visual pose distribution을 사용한다. Sim에서는 slip direction/state도 비교하지만 real cost에는 slip term이 없다. (§III-A–C/§IV, pp.2–5)

## 10. Tactile–Other Modality Relationship

Tactile raw signal을 별도 wrist F/T와 결합하지 않는다. BioTac를 learned 3D force vectors로 축약하여 physics-based pose hypotheses의 observation cost에 사용한다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Actor | 해당 없음 | Estimator only; no learned control actor | Robot controls are recorded/exogenous | §III-A/§IV, pp.2,5 |
| Critic | 해당 없음 | No RL critic | Observation cost ranks hypotheses | §III-B–D, pp.2–4 |
| Reward | 해당 없음 | Cost uses q, sensor pose, contact force and optional slip agreement | Not an RL reward; real object pose is not in the cost | §III-C, Eq.(3), p.3 |
| Termination | 해당 없음 | Algorithm loop is written as while TRUE; trajectory endpoint is evaluation protocol | No GT success termination | Algorithm 1/§IV, pp.5–6 |
| Curriculum | 해당 없음 | No curriculum; initial pose/parameter distributions and perturbation widths are estimator hyperparameters | Simulation GT only supports evaluation/ablation | §III-D–E/§IV-A, pp.3–6 |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Contact feedback improves pose tracking | Input ablation | With vs without contact cost across low/medium/high initial pose noise | Contact lowers mean/variance ADD, especially as initial noise increases; exact bars rather than a single summary number. | §IV-A/Fig.3, PDF p.6 |
| Adaptive optimizers improve tracking | Controlled comparison | WRS/REPS/PBO vs open-loop and identity baselines | At medium noise REPS and PBO mean ADD are 5.8 mm and 5.9 mm; adaptive methods generally reduce variance/max error. | §IV-A/Fig.2, PDF pp.5–6 |
| Real object dependence and unrecoverable divergence | Real-world evaluation; Failure analysis | Foam, Spam and banana trajectories | Best final ADD 14.1 mm (Foam, PBO) and 12.2 mm (Spam, REPS); no optimizer tracks banana due unstable low-friction rotational slip and divergence. | §IV-B/Fig.4, PDF p.6 |
| Slip observation has conditional value | Input ablation | With vs without simulated slip detection | Helps at low/medium initial pose noise but advantage disappears at high noise; no real slip experiment because BioTac slip is not estimated. | §IV-A/Fig.3, PDF p.6 |

## 13. Author-stated Limitations

Initial vision과 known object mesh/robot model에 의존하고 real slip을 추정하지 않는다. Real trajectory 전체의 GT pose가 없어 final visual pose만 평가 기준으로 쓴다. Banana의 large moment arm/low friction에서 모든 simulation이 잘못된 slip 방향 또는 낙하로 발산하면 optimizer가 후속 update로 회복하지 못한다. (§IV-B, p.6)

## 14. Author-stated Future Work

Contact sensing을 vision-based pose tracking과 in-the-loop로 통합할 계획을 명시한다. (§V, p.6)

## 15. Review-relevant Findings

- 실행 중 current object pose는 physics hypotheses가 30 Hz로 추정한다.
- 초기와 최종 real pose는 PoseRBPF이며, 최종값은 평가용 기준으로만 사용한다.
- 힘은 wrist 6축 F/T가 아니라 BioTac electrode에서 학습된 fingertip 3D vectors다.
- Finger identity/pose는 알지만 within-sensor contact location은 제공하지 않는다.
- Real slip 정보는 사용하지 않는다.
- RL actor/critic/reward/termination은 해당 없음.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Problem / observation | §III-A, PDF p.2 |
| Cost and contact terms | §III-B–C, pp.2–3; Eq.(3) |
| Pose/parameter optimization assumptions | §III-D–E, pp.3–4 |
| Real tactile force source | §IV, p.5 |
| Contact ablation | §IV-A/Fig.3, p.6 |
| Real failure / future | §IV-B–V/Fig.4, p.6 |
