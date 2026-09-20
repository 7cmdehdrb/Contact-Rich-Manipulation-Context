# Tactile Gym 2.0: Sim-to-Real Deep Reinforcement Learning for Comparing Low-Cost High-Resolution Robot Touch

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B043`
- Authors: Yijiong Lin; John Lloyd; Alex Church; Nathan F. Lepora
- Year: 2022
- Venue: IEEE Robotics and Automation Letters 7(4), 10754–10761
- DOI / arXiv: 10.1109/LRA.2022.3195195 / Not stated
- PDF version: IEEE publisher PDF; current version 9 August 2022
- Version note: 선택 범위 내 다른 버전 없음
- Page count: 8
- SHA-256: `e2d99c8f078d3c46b3f3032a2fc5c1c2bb319804de050bfa13cb62fccad0761b`
- PDF filename: `Lin 등 - 2022 - Tactile Gym 2.0 Sim-to-Real Deep Reinforcement Learning for Comparing Low-Cost High-Resolution Robo.pdf`
- 읽은 범위: PDF pp.1–8 전체(본문, Tables I–VII, Figs.1–7, discussion, 참고문헌). p.6 Table IV–V와 pushing failure를 렌더 확인. 별도 supplement/video는 확인하지 않음.
- 근거: 이번 배치의 PDF 원문에서 새로 분석했다. 기존 상세 노트는 재사용하지 않았다. 아래 페이지는 PDF 1-based page다.

## 2. Relevance to This Review

**Relevant**. TacTip, DIGIT, DigiTac의 optical tactile image를 동일 sim-to-real PPO framework에 넣어 object pushing·edge following·surface following을 실물에서 비교한다. Current object pose는 policy 입력으로 보고되지 않고 ArUco/CAD는 평가 GT에 쓰이며, sensor 구조·stiffness·contact deformation이 약한 물체와 concave surface 실패를 좌우한다. 다만 세 sensor 모두 tactile을 사용해 no-tactile/FT baseline은 없다.

Screening 위치: Abstract/§III-B–F, PDF pp.1–5; §IV–V, pp.5–8.

## 3. Task

Optical tactile end effector로 물체를 지정 path로 push하고, object edge 또는 side surface를 따라간다. 세 task를 TacTip, DIGIT, DigiTac으로 sim-to-real 비교한다. (§III-F, PDF pp.4–5)

## 4. Method

### 4.1. Overall Pipeline

Train PPO with simulated tactile depth images, train a sensor-specific real-to-sim image translator from paired contacts, then feed translated real tactile images to the frozen simulation policy for zero-shot deployment. (§III-B–E, pp.3–5)

### 4.2. Observation

The policy receives a high-resolution simulated-style tactile image. This PDF does not restate the full actor/proprioception/goal vector from prior Tactile Gym work; no current global object pose is reported. (§III-B–C, pp.3–4)

### 4.3. Action

Task-specific 2D TCP actions: pushing x/yaw, edge following x/y, surface following y/yaw. (§III-F, pp.4–5)

### 4.4. Controller

Dobot MG400 executes Cartesian TCP actions; exact low-level gains/rate are not stated. A custom flange compensates for the arm's 4-DoF limits. (§III-A–B, pp.2–3)

### 4.5. Learning / Optimization Method

PPO via Stable-Baselines3. Real-to-sim pix2pix-style GAN uses 5000 paired training and 2000 validation images per feature/sensor; reward/critic/termination details are not restated. (§III-D–E/§IV-A, pp.4–5)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | No current object position in reported actor input; ArUco records pushing path | No actor pose update | ArUco trajectory is evaluation GT, not policy vision. 근거: §III-F1/§IV-C1, PDF pp.4–6; Fig.5 |
| Orientation | 미제공 | No current object orientation input reported | No | Pushing yaw goal/control does not establish a measured current object orientation input. 근거: §III-F/§IV, pp.4–7 |
| Shape / Geometry | 기타 | Fixed training stimulus/contact-feature prior; local tactile image; CAD contour only evaluation | Local image updates | Unseen trajectory/object shapes are tests; no mesh vector goes to actor. 근거: §III-C–F, pp.3–5; §IV-C, pp.5–7 |
| Physical Parameters | 미제공 | No mass/friction vector in policy; objects 185–363 g and added weights vary evaluation conditions | No | Weight changes sensor deformation/domain match; it is not a sensed parameter. 근거: §III-F1, pp.4–5; §IV-C1, p.6 |

## 6. Missing Object Information and Compensation

Current global object pose/geometry를 actor에 제공했다는 근거가 없음 → local optical tactile image와 task/robot context로 contact를 유지한다. Pushing ArUco trajectory와 CAD contours는 평가 GT다. Weak tactile deformation은 DIGIT translation domain을 벗어나 failure를 낳으며 object weight 추가로 신호를 키운 시험은 compensation이라기보다 sensor feasibility 조건이다. (§III-F/§IV-C, pp.4–7)

## 7. Tactile

### 7.1. Raw Sensor

Internal-camera optical images from TacTip, DIGIT or DigiTac. TacTip/DigiTac use marker/pin deformation; DIGIT uses GelSight-style image shading. (§III-A2/Fig.2, PDF pp.2–4)

### 7.2. Preprocessing

Each sensor uses tuned image preprocessing and camera calibration, then a conditional U-Net GAN maps real images to simulated contact-depth style. (§III-D–E, pp.4–5)

### 7.3. Policy Representation

The translated/simulated tactile image is the PPO observation channel. Exact image resolution, CNN architecture and full actor vector are not repeated in this PDF. (§III-B–D, pp.3–4)

### 7.4. Retained Information

Spatial local deformation/contact geometry needed to maintain object or surface contact; sensor design changes contact-area and deformation distribution. (§III-A/C, pp.2–4; §IV-C, pp.6–7)

### 7.5. Removed / Unavailable Information

No conversion to calibrated force/wrench or explicit contact pose/object pose is reported. GAN translation error can suppress weak deformations outside its training distribution. (§III-D/§IV-B–C, pp.4–7)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. Optical tactile image is the method's sensor; no wrist F/T or force-vector input. (§III-A–D, pp.2–4)

### 8.2. Representation

해당 없음. (§III-A–D, pp.2–4)

### 8.3. Role

해당 없음. Contact force is discussed physically through deformation/friction, not measured as a policy wrench. (§IV-C, pp.6–7)

### 8.4. Required Assumptions

해당 없음 to F/T. Tactile transfer assumes real deformations fall within paired-data/GAN domain. (§III-D–E/§IV-C, pp.4–7)

### 8.5. Reported Limitation / Ambiguity

No F/T analysis. Sensor stiffness/contact-area effects cannot be recast as calibrated force evidence. (§IV-C/V, pp.6–8)

## 9. Other Observations

External visual tracking은 평가에만 사용한다. Exact proprioception, goal encoding, sensor history와 previous action은 이 PDF에서 열거하지 않고 prior framework로 넘긴다. (§III-B/F, pp.3–5)

## 10. Tactile–Other Modality Relationship

Tactile-only 계열 비교이며 independent F/T는 없다. 세 sensor의 local deformation images와 physical contact mechanics를 비교했지만 modality ablation은 아니다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Actor | No object GT reported | Simulated tactile image in training; translated real tactile image in deployment; full proprioception/goal vector not restated | ArUco/CAD evaluation GT is excluded from actor | §III-B–F, pp.3–5 |
| Critic | Not stated | PPO critic input not enumerated | Do not infer asymmetric object state | §IV-A, p.5 |
| Reward | Not stated | Task reward definitions are referred to prior Tactile Gym implementation | Object trajectory GT used for evaluation must not be treated as proven reward input here | §III-B/F–IV-A, pp.3–5 |
| Termination | Not stated | Pushing evaluation reports 250-step episodes; training/reset conditions not specified | No autonomous real success detector described | §IV-C1, p.6 |
| Curriculum | Not stated | No progressive curriculum reported; paired contact-pose labels train GAN separately | Known contact pose labels are translation supervision, not actor execution input | §III-D–E, pp.4–5 |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Sensor-specific tactile dynamics in RL | Sensor comparison | TacTip vs DigiTac vs DIGIT PPO training | All reach similar accurate final simulated performance; small differences attributed to tip/contact dynamics. No no-tactile arm. | §IV-A/Fig.4, PDF pp.5–6 |
| Real pushing accuracy and weak-contact failure | Sensor comparison; Failure analysis | Three sensors × three objects/trajectories; weighted DIGIT prism follow-up | Successful paths are typically ~9–16 mm error. DIGIT fails all 185 g prism paths; adding 150 g restores 16.58–17.06 mm, supporting a deformation/GAN-domain explanation. | §IV-C1, Tables IV–V/Fig.5, PDF p.6 |
| Edge-following sensor performance | Sensor comparison | Three sensors on square/clover/teardrop contours | TacTip/DigiTac typical 0.6–1.4 mm, DIGIT 0.9–1.8 mm; authors link larger local errors to stiffer flat elastomer and contact/friction. | §IV-C2, Table VI/Fig.6, PDF pp.6–7 |
| Surface-following physical limitation | Failure analysis | Sensors on disc/flower/arch surfaces | DIGIT reaches 0.5 mm on circular surface but gets stuck on concave shapes; flower/arch tests are stopped to avoid damage. | §IV-C3, Table VII/Fig.7, PDF p.7 |

## 13. Author-stated Limitations

DIGIT의 flat/stiff skin은 작은 penetration 변화와 friction에 민감하며 충분한 deformation을 위해 강한 접촉이 필요하다. Light triangular prism에서는 GAN translation이 실패했고 concave surfaces에서는 stuck되어 sensor damage 우려로 일부 test를 중단했다. Full actor/reward/termination specification과 no-tactile comparison은 원문에 없다. (§IV-C/V, pp.6–8)

## 14. Author-stated Future Work

Sensor physical characteristics의 선택·customization에 이 benchmark를 활용하고, controlled scenario에서 출발해 prehensile/dexterous hand tasks로 확대할 가능성을 제시한다. (§V, p.8)

## 15. Review-relevant Findings

- Current object pose는 actor 입력으로 명시되지 않았다.
- ArUco와 CAD는 trajectory error 평가 GT다.
- Real optical images는 GAN으로 simulated depth-style image에 맞춘다.
- DIGIT failure는 calibrated force 부족이 아니라 stiff skin/weak deformation/domain mismatch로 설명된다.
- PPO critic/reward/termination의 세부는 이 PDF에 미명시다.
- No-tactile 및 wrist F/T 비교가 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Tactile sensors / raw signal | §III-A, PDF pp.2–3; Fig.2 |
| Sim-to-real observation | §III-B–E, pp.3–5 |
| Task / action / evaluation GT | §III-F, pp.4–5 |
| Pushing results / weak contact | §IV-C1, p.6; Tables IV–V/Fig.5 |
| Edge/surface sensor limitations | §IV-C2–3, pp.6–7; Tables VI–VII |
| Discussion / future | §V, pp.7–8 |
