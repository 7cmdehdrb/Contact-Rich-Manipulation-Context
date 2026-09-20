# Reactive Diffusion Policy: Slow-Fast Visual-Tactile Policy Learning for Contact-Rich Manipulation

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B089`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Han Xue; Jieji Ren; Wendi Chen; Gu Zhang; Yuan Fang; Guoying Gu; Huazhe Xu; Cewu Lu
- Year: 2025
- Venue: arXiv preprint
- DOI / arXiv: Not stated / 2503.02881v3
- PDF version: arXiv v3 (23 April 2025)
- Page count: 18
- SHA-256: `98e20028e85124b7bffe2dee9775ae4cc8bdee94f65a73841d1ea910ab5cb0ad`
- PDF filename: Xue 등 - 2025 - Reactive Diffusion Policy Slow-Fast Visual-Tactile Policy Learning for Contact-Rich Manipulation.pdf
- 확인 범위: PDF pp.1–18 전체(본문, limitations/future, Appendices A–I); sensor hardware, PCA representation, inference timing, modality/architecture ablations, failure cases와 user study를 확인하고 Figures 6/8/17–18 및 Tables II–VI 렌더 검토.

## 2. Relevance to This Review

`Relevant`

Optical tactile PCA feature와 joint-torque-derived 6-D TCP wrench를 동일 slow-fast imitation framework의 대체 sensory variants로 비교하며, vision-only/open-loop baselines와 contact perturbation 실험을 제공한다. Tactile이 spatial deformation modes를 남기는 방식, estimated wrench가 global force/torque를 제공하는 방식, high-frequency feedback의 역할과 evidence를 직접 비교할 수 있다.

## 3. Task

Peeling에서는 tool로 사람이 든 cucumber를 벗기고, wiping에서는 curved vase 표면을 닦으며, bimanual lifting에서는 두 arms가 paper cup을 찌그러뜨리거나 놓치지 않고 함께 들어 올린다. 인간이 object를 움직여 contact 전후 perturbation을 가하는 조건에서 빠르게 contact를 회복하고 force를 조절하는 것이 핵심이다. [§V-A, PDF pp.7–8]

## 4. Method

### 4.1. Overall Pipeline

TactAR demonstrations: VR end-effector teleoperation + real-time tactile/force AR feedback → synchronized RGB, proprioception, action, optical tactile deformation 또는 estimated wrench. RDP: low-frequency visual/tactile/force/proprio observation → latent diffusion slow policy가 action chunk 생성 → high-frequency tactile PCA feature 또는 6-D wrench → asymmetric-tokenizer GRU fast policy가 latent chunk를 autoregressive 수정 → decoded relative trajectory를 interpolation해 Flexiv controller에 >500 Hz로 전송한다. [§III–IV, pp.4–7; Appendix F/I, pp.17–18]

### 4.2. Observation

Slow LDP는 observation horizon 2의 RGB, proprioception, tactile/force input을 1–2 Hz로 사용한다. Fast policy는 optical tactile의 15-D PCA feature 또는 estimated 6-D TCP wrench를 24 FPS로 받고, 이전 fast hidden state/action context와 함께 current latent action chunk를 수정한다. 물체 numeric pose/shape는 observation으로 명시되지 않는다. [§IV-A–B pp.5–7; Appendix F/I pp.17–18]

### 4.3. Action

Slow policy는 relative end-effector action chunk를 latent space에서 생성하고 fast policy가 각 high-frequency step에 corrective action을 autoregressively 갱신한다. Peeling/wiping은 relative proprioception/action, bimanual lifting은 absolute action을 사용한다. [§IV-B, pp.5–7; Appendix I/Table VII, p.18]

### 4.4. Controller

Decoded action predictions를 시간 보간하여 Flexiv RDK에 500 Hz 이상으로 전송하는 TCP pose control을 사용한다. Slow policy는 1–2 Hz, fast policy는 tactile/force frame 제한에 맞춘 24 FPS로 갱신한다. [§V-A p.9; Appendix F p.17]

### 4.5. Learning / Optimization Method

Real demonstrations로 학습하는 imitation-learning diffusion policy다. Stage 1 asymmetric tokenizer는 action chunk를 tactile/force sequence와 함께 encode하되 decoder는 action만 복원하게 학습하여 latent action을 만든다. Stage 2 latent diffusion slow policy가 low-frequency observation에서 latent chunk를 생성하고 GRU fast policy가 high-frequency tactile/force로 closed-loop correction을 학습한다. RL reward/critic은 없다. [§IV-B, pp.5–7]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Wrist/external RGB images에 implicit하게 나타나며 numeric object pose는 미제공 | Yes | Test object pose를 수동 randomize하지만 policy에 pose vector를 주지 않는다. [§V-A pp.7–9] |
| Orientation | 기타 | RGB appearance에 implicit; numeric orientation 미제공 | Yes | Cucumber/vase perturbations는 image와 contact signal로만 관측된다. [§V-A–B pp.7–10] |
| Shape / Geometry | 기타 | RGB and tactile deformation에 implicit | Yes | Mesh/CAD/dimensions/category vector는 policy input이 아니다. [§IV–V pp.5–10] |
| Physical Parameters | 미제공 | Mass/compliance/friction을 policy에 명시적으로 제공하지 않음 | 해당 없음 | Paper-cup stiffness와 contact conditions은 sensor response를 통해서만 드러난다. [§V-A–B pp.7–10] |

## 6. Missing Object Information and Compensation

Numeric current object pose/shape/physical parameters 미제공 → RGB scene context + proprioception + high-frequency tactile deformation 또는 estimated wrench + fast recurrent state → contact loss, force spike, surface-following 상태에 맞추어 action chunk를 즉시 수정한다.

Open-loop visual action chunk의 contact-state 변화 반영 부족 → 24 FPS tactile/force feedback과 GRU fast policy → sub-millimeter corrective action으로 contact를 회복하거나 excessive force를 줄인다. Tactile와 force는 실험에서 주로 대체 variants이며, 같은 policy에 동시에 결합한 complementary fusion evidence는 제시하지 않는다. [§IV-B/§V-B, pp.5–10]

## 7. Tactile

### 7.1. Raw Sensor

GelSight Mini(8 MP, 25 FPS, 7×9 marker array)와 improved MCTac(2 MP, 30 FPS, 5×7 marker array)의 optical images/marker motions. Bimanual setup은 서로 다른 fingertips에 두 sensor를 장착한다. [§V-A p.7; Appendix A p.16]

### 7.2. Preprocessing

Reference frame 대비 marker optical flow로 n×2 deformation field를 만든다. 20 objects에 대한 random interactions로 PCA basis를 학습하고 각 frame을 15-D feature로 투영한다. [§III-B/§IV-A pp.4–5; Appendix C–D pp.16–17]

### 7.3. Policy Representation

15-D PCA embedding of 2-D marker deformation field. Slow policy와 24-FPS fast policy가 동일 contact feature를 서로 다른 rates로 사용한다. [§IV-A–B pp.5–7; Appendix C p.17]

### 7.4. Retained Information

주요 components가 tangential force, torsional torque, normal force와 대응하며 contact deformation의 방향/크기와 빠른 temporal change를 보존한다. [Appendix C/Figs.17–18, p.17]

### 7.5. Removed / Unavailable Information

Raw tactile image의 pixel texture, full marker-level spatial detail와 고차 components를 15-D PCA로 축약한다. Representation이 explicit contact location/pose 또는 global object pose를 출력하지 않는다. [§IV-A p.5; Appendix C p.17]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Flexiv Rizon 4의 built-in joint torque sensors에서 Flexiv RDK가 계산한 estimated TCP force/torque. Wrist-mounted physical 6-axis F/T가 아니다. [§V-A, p.7]

### 8.2. Representation

World/TCP convention의 정확한 frame은 미명시이며, $F_x,F_y,F_z,M_x,M_y,M_z$ 6-D wrench를 concatenate해 observation vector로 사용한다. Raw 120 Hz signals를 24 FPS로 downsample한다. [§IV-A p.5; §V-A p.7]

### 8.3. Role

Slow/fast policy observation으로 global interaction load와 torque 변화를 제공하고 force spike/contact loss에 즉시 trajectory correction을 만든다. Peeling, wiping, bimanual lifting에서 가장 높은 overall scores를 보고한다. [§V-B, pp.9–10]

### 8.4. Required Assumptions

Robot dynamics model 기반 external TCP wrench estimation, synchronized robot/sensor timestamps, known TCP transforms, demonstration distribution과 24-FPS sampling이 필요하다. [§V-A p.7; Appendix F p.17]

### 8.5. Reported Limitation / Ambiguity

Dynamics-model error 때문에 end-effector-mounted F/T보다 noise가 크다. Net wrench에서 contact locality/patch 또는 multiple contacts를 복원하지 않으며 해당 ambiguity를 직접 분석하지 않는다. [§V-A p.7]

## 9. Other Observations

Vision은 single-arm에서 wrist D435, bimanual에서 two wrist D435와 fixed D415를 사용한다. Proprioception은 relative TCP/action context(peeling/wiping) 또는 absolute state(lifting)이며 observation horizon 2다. Fast GRU hidden state와 autoregressive previous correction이 high-frequency history를 유지한다. Language, current object GT, explicit state estimator는 없다. [§V-A pp.7–9; Appendix I p.18]

## 10. Tactile–Other Modality Relationship

Vision은 scene/tool/object configuration과 long-horizon multimodality를 slow diffusion policy에 제공하고, tactile 또는 estimated wrench는 fast contact feedback으로 latent action chunk를 수정한다. Optical tactile PCA는 local gel deformation modes를, joint-torque wrench는 low-dimensional global load를 제공한다. Table II–IV에서 Force variant가 tactile variants보다 높지만 sensor latency/dimensionality도 함께 다르므로 locality와 load의 독립 효과를 분리한 ablation은 아니다. Tactile+F/T를 동시에 한 policy에 넣은 sensor-fusion comparison도 없다. [§V-B, pp.9–10]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | 비-RL imitation learning. Demonstration action/tactile/force labels는 supervised training data이며 simulator object GT나 asymmetric critic과 구분한다. [§IV–VI, PDF pp.5–14] |
| Critic | Not applicable | 비-RL | 비-RL imitation learning. Demonstration action/tactile/force labels는 supervised training data이며 simulator object GT나 asymmetric critic과 구분한다. [§IV–VI, PDF pp.5–14] |
| Reward | Not applicable | 비-RL | 비-RL imitation learning. Demonstration action/tactile/force labels는 supervised training data이며 simulator object GT나 asymmetric critic과 구분한다. [§IV–VI, PDF pp.5–14] |
| Termination | Not applicable | 비-RL | 비-RL imitation learning. Demonstration action/tactile/force labels는 supervised training data이며 simulator object GT나 asymmetric critic과 구분한다. [§IV–VI, PDF pp.5–14] |
| Curriculum | Not applicable | 비-RL | 비-RL imitation learning. Demonstration action/tactile/force labels는 supervised training data이며 simulator object GT나 asymmetric critic과 구분한다. [§IV–VI, PDF pp.5–14] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| High-frequency reactive feedback improves contact-rich performance | Controlled comparison | Visual-only DP; DP+tactile image/embedding; RDP tactile; RDP force | Overall scores: peeling DP 0.44 vs RDP tactile 0.88–0.90 and force 0.95; wiping 0.57 vs 0.77/0.87; bimanual 0.00 vs 0.48/0.70. | §V-B; PDF pp.9–10 ; Tables II–IV |
| Fast feedback improves recovery after contact perturbation | Controlled comparison / Failure analysis | Perturbation after contact, open-loop DP vs RDP | Peeling after-contact score is 0.19 for DP, 0.15 for DP+tactile embedding, 0.80 GelSight RDP, 0.88 force RDP; failure cases show lost contact/large force. | §V-B; PDF pp.9–10 ; Table II ; Fig.8 |
| Shear/torsional wrench components matter | Input ablation | Full 6-D force/torque vs normal-force-only in peeling | Overall score drops from 0.95 to 0.48 when only normal force is retained. | Appendix G; PDF pp.17–18 ; Table VI |
| Asymmetric tokenizer matters | Architecture ablation | Default asymmetric tokenizer vs symmetric action+sensor encoder | Peeling overall score drops from 0.95 to 0.58 with symmetric tokenizer. | Appendix G; PDF p.18 ; Table VI |
| Tactile feedback improves demonstration quality | User study | Traditional VR teleoperation vs TactAR over 200 peeling trials | Stable-force ratio increases from 0.58 to 0.87 and normalized peel length from 0.72 to 0.91. | §V-C; Appendix H; PDF pp.11,18 |

## 13. Author-stated Limitations

저자들은 TactAR feedback이 direct human-hand operation만큼 intuitive/efficient하지 않고 latency가 남는다고 밝힌다. 현재 gripper는 two-finger, fast policy는 high-frequency images를 처리하지 못하며, RDP는 single-task 학습에 한정된다. Estimated wrench는 dynamics-model error로 physical endpoint F/T보다 noisy하다. [§V-A p.7; §VI p.14]

## 14. Author-stated Future Work

Sensor/system latency 감소, tactile dexterous hand로 확장, fast network에 high-frequency visual input 추가, asymmetric tokenizer를 VLA와 결합하여 multi-task reactive control로 확장하는 방향을 제시한다. [§VI, p.14]

## 15. Review-relevant Findings

- Current object numeric pose/shape는 제공하지 않고 RGB, robot state와 contact feedback을 사용한다.
- Optical tactile는 marker deformation field를 15-D PCA로 축약하여 normal/tangential/torsional modes를 남긴다.
- Force variant는 built-in joint torques에서 추정한 6-D TCP wrench이며 physical wrist F/T가 아니다.
- Tactile와 wrench는 주로 대체 variants로 비교되어 simultaneous F/T+tactile role division은 검증하지 않는다.
- High-frequency feedback와 normal-only ablation이 contact reaction과 non-normal load components의 효용을 뒷받침한다.
- 비-RL imitation learning이므로 actor/critic/reward privileged GT 구분은 해당 없음이다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Sensors / hardware | §III-B pp.4–5; §V-A p.7 |
| Representation / policy | §IV-A–B pp.5–7 |
| Tasks / observation frequency | §V-A pp.7–9 |
| Sensor comparisons | §V-B/Tables II–IV pp.9–10 |
| Failure analysis / timing ablation | §V-B pp.9–11 |
| PCA details | Appendix C–D p.17 |
| Normal-force/tokenizer ablation | Appendix G/Table VI pp.17–18 |
| Limitation / Future | §VI p.14 |
