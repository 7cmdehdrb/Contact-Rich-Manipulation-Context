# Bi-Touch: Bimanual Tactile Manipulation With Sim-to-Real Deep Reinforcement Learning

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B045`
- Authors: Yijiong Lin; Alex Church; Max Yang; Haoran Li; John Lloyd; Dandan Zhang; Nathan F. Lepora
- Year: 2023
- Venue: IEEE Robotics and Automation Letters 8(9), 5472–5479
- DOI / arXiv: 10.1109/LRA.2023.3295991 / Not stated
- PDF version: IEEE publisher PDF; current version 24 July 2023
- Version note: 선택 범위 내 다른 버전 없음
- Page count: 8
- SHA-256: `74151c1505e6d62d406005739cb859791a5e63f9a120ec254aa0a183a6e47f99`
- PDF filename: `Lin 등 - 2023 - Bi-Touch Bimanual Tactile Manipulation With Sim-to-Real Deep Reinforcement Learning.pdf`
- 읽은 범위: PDF pp.1–8 전체(본문, Eqs.1–4, Tables I–III, Figs.1–7, discussion/future work, 참고문헌). pp.5–7의 학습 곡선·정량표·ArUco 설명을 렌더 확인. Supplementary video는 확인하지 않음.
- 근거: 이번 배치의 PDF 원문에서 새로 분석했다. 기존 상세 노트는 재사용하지 않았다. 아래 페이지는 PDF 1-based page다.

## 2. Relevance to This Review

**Relevant**. 두 TacTip optical tactile image와 proprioception만으로 bi-pushing·bi-reorienting·bi-gathering PPO policies를 학습·실물 전이한다. Simulator object pose와 goals는 reward·curriculum에 쓰지만 실물 actor에는 object pose가 없고, ArUco는 정량 평가에만 쓴다고 명시한다. F/T 입력은 없으며 random force는 disturbance다.

Screening 위치: Abstract/§III-B–C, PDF pp.1,3–5; §IV–V, pp.5–8; Fig.7 caption, p.7.

## 3. Task

두 robot arm과 두 TacTip으로 큰 물체를 경로 따라 push하고, 물체를 목표 yaw로 reorient하며, 두 물체를 서로 gather한다. Gathering은 불시 random force perturbation에 대한 robustness까지 평가한다. (§III-C, PDF pp.3–5)

## 4. Method

### 4.1. Overall Pipeline

Train three task-specific PPO policies in Tactile Gym with two simulated tactile images and proprioception, learn a paired real-to-sim translator, then translate each real TacTip image and concatenate them for zero-shot policy execution. (§III-B–C/Fig.1, pp.3–5)

### 4.2. Observation

Actor observation is described as two tactile images plus proprioceptive feedback. Fig.2 identifies TCP quantities as proprioception; current object pose is used in rewards but unavailable in the real setting. Exact goal/subgoal encoding and critic input are not enumerated. (§III-B–C, pp.3–5)

### 4.3. Action

Task-specific Cartesian increments in each TCP frame: pushing x/Rz per arm, reorienting x/y/Rz per arm, gathering y/Rz per arm. (§III-C, p.3)

### 4.4. Controller

Two Dobot MG400 arms execute Cartesian TCP actions with table support. Low-level rate/gains and safety supervisor are not stated. (§III-A/C, pp.2–3)

### 4.5. Learning / Optimization Method

PPO via Stable-Baselines3. Reward Eqs.1–4 use simulator object/TCP states. Reorienting uses ten angle subgoals; gathering uses GUM plus a two-stage object-centre-to-TCP curriculum and randomized 1–5 N perturbations. (§III-C/§IV-A, pp.3–5)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Simulation engine supplies current object centres to reward/GUM; real ArUco supplies trajectory/success evaluation only | Simulator reward updates each step; real actor gets no object position | Current object pose and goal/subgoal are distinct quantities. ArUco is excluded from execution observation. 근거: §III-C/Eqs.1–4, PDF pp.3–5; §IV-B/Fig.7, pp.6–7 |
| Orientation | 미제공 | Simulation engine supplies current/goal orientation to pushing/reorientation rewards; real ArUco evaluates final errors | Simulator reward updates each step; no real actor orientation tracker | Goal angle is not evidence of a measured current angle input. Separate policies are trained for real reorientation directions. 근거: §III-C/Eqs.1–4, pp.3–5; §IV-B2, p.6 |
| Shape / Geometry | 기타 | Cuboid/cube simulation prior and local tactile images; unseen real objects vary shape | Local tactile image updates; global shape does not | No mesh or shape vector enters the reported actor; prism/round-object failures show limits of the training prior. 근거: §IV-A2/B2–3, pp.5–7; Fig.4 |
| Physical Parameters | 미제공 | No mass/friction/stiffness input; real objects span varied weight/stiffness and perturbations | No | Applied 1–5 N simulation perturbations are environment interventions, not policy force measurements. 근거: §III-C3/§IV-A3–B3, pp.4–7 |

## 6. Missing Object Information and Compensation

실물 actor에 current object pose가 없음 → 양쪽 local tactile deformation + TCP proprioception으로 접촉을 유지한다. Gathering GUM은 simulation에서 object-centre GT target line으로 먼저 학습한 뒤, 실물에서 계산 가능한 TCP target line으로 전환한다. ArUco current pose·goal error는 평가에만 쓰며 actor 보상 정보와 분리한다. (§III-C3/§IV-B, pp.4–7)

## 7. Tactile

### 7.1. Raw Sensor

Each TacTip internal camera observes motion of biomimetic markers/pins caused by soft-skin deformation. Two simultaneous images form the bimanual contact input. (§III-A2/B, PDF pp.2–3; Fig.1)

### 7.2. Preprocessing

A real-to-sim image-to-image GAN is trained from 5000 paired training and 2000 validation contacts over 0.5–8 mm depth and −30°–30° rotation. Real images are translated separately then concatenated. (§III-B, p.3)

### 7.3. Policy Representation

The concatenated two simulated-style tactile images are combined with proprioceptive feedback as the PPO observation. Exact image resolution and full vector ordering are not stated. (§III-B/Fig.1, p.3)

### 7.4. Retained Information

Spatial contact-surface deformation and contact-depth cues for maintaining bilateral contact and reacting to objects of different shape, weight and stiffness. (§III-A–C/§IV-B, pp.2–7)

### 7.5. Removed / Unavailable Information

No calibrated normal/shear force vector, net wrench, explicit contact point, object identity or global pose is produced. Simulation omits shear deformation. (§III-B/§V, pp.3,8)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. The robot has optical TacTips but no independent wrist F/T input. Random applied forces are disturbances. (Abstract/§III-C3, pp.1,4–5)

### 8.2. Representation

해당 없음. Perturbation magnitude/time belong to simulator/test setup and are not actor observations. (§III-C3/§IV-A3, pp.4–5)

### 8.3. Role

해당 없음. Robustness to force perturbations is evaluated through behavior, without measuring or feeding those forces to the policy. (§IV-A3/B3, pp.5–7)

### 8.4. Required Assumptions

해당 없음 to F/T. Tactile control instead assumes paired image translation and usable bilateral contacts within robot workspace. (§III-B/§IV-B, pp.3,6–7)

### 8.5. Reported Limitation / Ambiguity

No F/T ambiguity analysis. Contact deformation must not be restated as a measured wrench; shear is specifically absent from simulation. (§V, p.8)

## 9. Other Observations

TCP position/orientation은 proprioception이다. Goal/subgoal은 reward equations에 명시되지만 actor input encoding은 별도로 열거되지 않는다. Random forces는 disturbance이고, ArUco markers는 trajectories와 success의 quantitative evaluation용이다. (§III-C/Fig.2, pp.3–5; Fig.7 caption, p.7)

## 10. Tactile–Other Modality Relationship

두 TacTip tactile images와 proprioception을 결합하며 external vision이나 independent F/T를 actor에 넣지 않는다. 따라서 spatial deformation은 얻지만 calibrated wrench나 명시적 global pose는 얻지 않는다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Actor | No object GT reported | Two tactile images plus proprioceptive feedback; exact goal encoding not enumerated | Current object pose used by reward/GUM and ArUco evaluation is not an actor input | §III-B–C/Fig.1–2, pp.3–5; Fig.7 caption, p.7 |
| Critic | Not stated | PPO critic observation is not specified | Do not infer asymmetric object-state access | §IV-A, p.5 |
| Reward | Yes | Current object position/orientation, target pose or angle, TCP pose/orientation, desired contact points and GUM subgoals | Simulation training only; goals and current state are separate variables in Eqs.1–4 | §III-C/Eqs.1–4, pp.3–5 |
| Termination | Yes / partially stated | Gathering d<90 mm in simulation; reorientation target held 10 steps. Real evaluation uses ArUco d<7 cm within 300 steps or angle stability | Real ArUco logic is evaluation, not actor vision; other horizon/failure terms are not fully stated | §III-C2–3, pp.4–5; §IV-A3/B2–3, pp.5–7 |
| Curriculum | Yes | Ten reorientation angle subgoals; gathering target line first from object centres then TCPs; perturbation probability/magnitude increase | Object-centre GT is training-only and removed before real transfer | §III-C2–3/§IV-A2, pp.4–5 |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| GUM and curriculum enable perturbed gathering | Mechanism ablation | With vs without GUM, with vs without perturbations in simulation | Without GUM, perturbed gathering does not learn; GUM reduces completion steps and reaches similar curves with/without perturbations. Exact curve values are not tabulated. | §IV-A3/Fig.3c, PDF p.5 |
| Real bi-pushing transfers across unseen objects | Real-world evaluation | Three unseen objects; 20 trials each (10 linear, 10 sinusoidal) | Simulation error 12.3±4.8 mm; real tripod box 14.2±6.4, shuttle tube 16.6±7.7 and loudspeaker 17.4±8.1 mm over 300–420 mm travel. | §IV-A1/B1, Table I/Fig.5, PDF pp.5–6 |
| Reorientation exposes dynamics/geometry failures | Failure analysis; Author-reported ablation | Simulated skin/goal-hold/squeeze-penalty/goal-distribution changes; unseen real shapes | Skin stiffness/damping change is reported as the largest contributor, without numeric ablation table. Real errors are 12.5±5.3–19.5±7.0 mm and 7.5±3.9–13.4±6.5°; sharp prism fails by slip. | §III-C2/§IV-B2, Table II/Fig.6, PDF pp.4,6–7 |
| Gathering robustness degrades with harder disturbances | Real-world evaluation; Failure analysis | Four real object pairs, 10 trials per pair and 1–6 random perturbations; simulated cube baseline | All real pairs are 100% at 1–2 perturbations. At 6: cube/cube 90%, apple/can 70%, mug/prism 10%, foam/spam 10%; failures arise from large turnaround and workspace exhaustion. | §IV-A3/B3, Table III/Fig.7, PDF pp.5–7 |
| No tactile or F/T necessity isolation | No sensor ablation | All learned policies use dual tactile images plus proprioception | The experiments compare mechanisms/tasks/objects, not tactile vs no-tactile or tactile vs F/T. Performance cannot quantify tactile's independent causal contribution. | §III–V, PDF pp.3–8 |

## 13. Author-stated Limitations

Simulation은 tactile shear deformation을 모델링하지 않는다. Cuboid-only training 때문에 round/large objects의 reorientation error가 커지고, sharp triangular prism contact는 slip 후 회복하지 못했다. Gathering에서 무겁거나 irregular한 perturbed objects는 큰 우회 동작으로 workspace를 소진한다. No-tactile/F/T ablation과 critic input은 미명시다. (§III-C2/§IV-B2–3/§V, pp.4,6–8)

## 14. Author-stated Future Work

Shear effect를 simulation에 신뢰성 있게 근사하고, supporting table 없이 held object를 fine-manipulate하도록 확장한다. Bi-lifting은 supplementary video의 preliminary demonstration일 뿐 정량 본실험 성과로 다루지 않는다. (§V, p.8)

## 15. Review-relevant Findings

- Runtime actor의 current object pose는 미제공이며 ArUco는 평가 전용이다.
- Current pose와 goal/subgoal은 reward에서 별도 변수다.
- Reward·termination·curriculum은 simulator GT를 쓰지만 critic GT 여부는 미명시다.
- Random external force는 disturbance이며 F/T observation이 아니다.
- Dual tactile image는 marker deformation을 보존하지만 shear/wrench/global pose를 직접 제공하지 않는다.
- GUM은 object-centre GT에서 TCP 기반 line으로 전환하는 training curriculum이다.
- No-tactile 또는 F/T baseline은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Platform / tactile source | §III-A–B/Fig.1, PDF pp.2–3 |
| Task / action / rewards | §III-C/Eqs.1–4/Fig.2, pp.3–5 |
| GUM / curriculum / perturbations | §III-C3/§IV-A3, pp.4–5; Fig.3 |
| Pushing / reorientation results | §IV-A1–2/B1–2, pp.5–7; Tables I–II/Figs.5–6 |
| Gathering robustness / evaluation vision | §IV-A3/B3, pp.5–7; Table III/Fig.7 |
| Limitations / future | §V, pp.7–8 |
