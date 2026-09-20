# ViTacGen: Robotic Pushing With Vision-to-Touch Generation

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B087`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Zhiyuan Wu; Yijiong Lin; Yongqiang Zhao; Xuyang Zhang; Zhuo Chen; Nathan F. Lepora; Shan Luo
- Year: 2025
- Venue: IEEE Robotics and Automation Letters, Vol. 10, No. 11
- DOI / arXiv: 10.1109/LRA.2025.3621941 / Not stated
- PDF version: IEEE publisher version (November 2025)
- Page count: 8
- SHA-256: `f7a763f3654902bd13b66490914f812dab728f12000145c16cdd56c984560782`
- PDF filename: Wu 등 - 2025 - ViTacGen Robotic Pushing With Vision-to-Touch Generation.pdf
- 확인 범위: PDF pp.1–8 전체; architecture, observations, reward/success, modality baselines, ablations, real-robot tests, conclusion/limitations를 확인하고 Figures 2/5와 Tables II–VI 렌더 검토.

## 2. Relevance to This Review

`Relevant`

실제 tactile sensor 없이 RGB sequence에서 contact-depth representation을 생성해 pushing policy에 넣고 visual-only, tactile-only, visual+tactile 조건을 비교한다. 생성 tactile이 contact geometry를 보완하지만 local force와 fine geometry를 포함하지 않는다고 저자가 명시하여, tactile representation의 retained/removed information과 modality evidence를 직접 제공한다.

## 3. Task

UR5e end effector가 tabletop object를 시작점에서 연속 goal points를 따라 밀어 원하는 2-D trajectory를 추종한다. Policy는 최대 350 steps 동안 visual observation과 생성된 tactile contact depth, TCP coordinates를 이용해 pushing action을 갱신하며 final goal 도달률과 trajectory error로 평가한다. [§III/§IV, PDF pp.3–5]

## 4. Method

### 4.1. Overall Pipeline

Phase 1: expert visual+tactile SAC policy가 만든 simulation trajectories에서 3-frame RGB sequence와 virtual optical tactile contact depth를 수집 → ViTac-Gen encoder-decoder가 current contact-depth image를 예측. Phase 2: generator를 freeze → generated tactile feature와 visual feature를 cross-attention 및 MoCo contrastive alignment → TCP coordinates와 결합한 ViTac-Con SAC policy → robot pushing action. 실물 실행에는 RGB camera만 필요하다. [§III-A–C, pp.3–4]

### 4.2. Observation

Control policy는 current RGB image, ViTac-Gen이 최근 3 RGB frames에서 생성한 contact-depth image, end-effector/TCP coordinates, goal information을 사용한다. 물체의 numeric current pose·orientation·mesh는 actor observation으로 명시되지 않는다. [§III-B–C, pp.3–4]

### 4.3. Action

SAC의 continuous robot action으로 end effector를 밀어 trajectory goal로 이동한다. Action vector의 정확한 축 구성, scale, reference frame은 원문에서 명시되지 않는다. [§III-C/§IV-A, pp.4–5]

### 4.4. Controller

Policy action을 UR5e에 적용하지만 low-level Cartesian/joint controller와 gain은 원문에서 명시되지 않는다. Simulation control frequency는 500 Hz이며 episode는 최대 350 control steps이다. [§IV-A, p.5]

### 4.5. Learning / Optimization Method

VT-Gen은 paired RGB-sequence/contact-depth samples로 supervised training하고, VT-Con은 visual/tactile features의 MoCo contrastive objective를 포함한 SAC로 학습한다. Expert rollout과 reward/success 계산에는 simulator object-center state가 사용되지만 실물 deployment actor에는 real tactile sensor나 numeric object pose가 필요하지 않다. [§III/§IV-A, pp.3–5]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Current RGB image에 implicit하게 나타나며 numeric object-position vector는 제공되지 않음 | Yes | Reward/success의 simulator object center는 학습·평가용 GT이며 runtime actor input과 구분한다. [§III-B–C pp.3–4; §IV-A p.5] |
| Orientation | 기타 | Current RGB appearance에 implicit; numeric orientation 미제공 | Yes | 2-D pushing이며 explicit quaternion/angle input은 확인되지 않는다. [§III-C pp.3–4] |
| Shape / Geometry | 기타 | RGB appearance와 generated contact-depth image에 implicit | Yes | Full mesh/CAD/point cloud/dimensions/category vector는 policy input으로 명시되지 않는다. [§III-B–C pp.3–4] |
| Physical Parameters | 미제공 | Mass/friction/compliance를 actor에 제공하지 않음 | 해당 없음 | Domain randomization은 사용하지만 runtime physical-parameter vector는 없다. [§IV-A p.5] |

## 6. Missing Object Information and Compensation

Real tactile sensor measurement 미제공 → 최근 3 RGB frames에서 generated contact-depth image → 예상 contact geometry와 penetration structure를 control policy에 제공한다.

Numeric current object pose/shape/physical parameters 미제공 → RGB appearance + TCP coordinates + generated tactile feature → goal-directed pushing을 조절한다. 다만 이 representation이 local force distribution, shear, fine geometry를 복원하지 못한다는 한계를 저자들이 명시한다. [§III-B–C pp.3–4; §V p.8]

## 7. Tactile

### 7.1. Raw Sensor

Training label은 Tactile Gym 2의 virtual optical tactile sensor가 계산한 contact-depth image이며, reference depth와 current penetration depth의 차이로 정의된다. 실물 deployment에는 physical tactile sensor가 없다. [§III-A–B, p.3]

### 7.2. Preprocessing

Expert visual+tactile rollout에서 RGB/tactile pairs를 수집한다. ViTac-Gen이 연속 3 RGB frames를 encode하고 skip-connected decoder로 current contact-depth image를 생성하며, control training에서는 generator를 freeze한다. [§III-A–B, pp.3–4]

### 7.3. Policy Representation

생성된 2-D optical contact-depth image를 tactile encoder로 feature화하고 visual feature와 cross-attention/contrastive alignment 후 SAC observation에 넣는다. [§III-B–C, p.4]

### 7.4. Retained Information

저자가 말하는 high-level contact geometry와 penetration/contact pattern을 보존하며, visual-only signal에 contact-specific latent cue를 추가한다. [§V, p.8]

### 7.5. Removed / Unavailable Information

Detailed physical properties, local force distribution, shear force, fine surface geometry를 제공하지 못한다. 생성값이므로 실제 contact force measurement도 아니다. [§V, p.8]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Wrist F/T, joint-torque wrench, fingertip force를 사용하지 않는다. Contact depth는 virtual optical tactile geometry이며 force sensor output이 아니다. [§III-A–C, pp.3–4]

### 8.2. Representation

별도 force/wrench representation 없음. [§III–V, pp.3–8]

### 8.3. Role

사용하지 않음. Contact interaction은 generated tactile depth와 visual motion으로 표현한다. [§III-B–C, pp.3–4]

### 8.4. Required Assumptions

해당 없음. 대신 simulation-generated paired RGB/tactile data와 visual-to-touch generalization이 필요하다. [§III-A–B, pp.3–4]

### 8.5. Reported Limitation / Ambiguity

F/T ambiguity는 논의하지 않는다. 저자는 generated tactile가 local force/shear를 포함하지 않는다고 명시한다. [§V, p.8]

## 9. Other Observations

Vision은 RealSense D435 RGB의 current/recent 3 frames이며 실물의 유일한 exteroceptive sensor다. TCP coordinates와 goal point가 policy에 들어간다. Temporal information은 VT-Gen의 3-frame input에 한정되고 recurrent hidden state나 previous action input은 원문에서 확인되지 않는다. [§III-B–C/§IV-A, pp.3–5]

## 10. Tactile–Other Modality Relationship

Generated tactile는 vision을 대체하는 독립 sensor가 아니라 visual motion에서 추론한 contact-depth feature다. RGB는 global scene/object appearance와 motion을, generated contact depth는 예상 local contact geometry를, TCP coordinates는 robot configuration을 제공한다. Table II의 visual-only/tactile-only/visual+tactile comparison은 modality 조합의 성능 차이를 보이지만, 실물 tactile measurement와 generated tactile의 동등성을 뜻하지 않는다. F/T는 사용하지 않는다. [§IV-C, p.6]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | RGB; generated contact-depth; TCP coordinates; goal | 실물 actor에는 real tactile나 object GT pose가 필요하지 않다. [§III-B–C, pp.3–4] |
| Critic | Not stated | SAC critic input details not separately specified | Asymmetric object-GT critic 여부를 원문에서 확인할 수 없다. [§III-C, p.4] |
| Reward | Yes | Simulator object-center to target distance and TCP-to-object distance | Dense reward가 simulator positions를 사용한다. [§IV-A, p.5] |
| Termination | Yes | Object center within 2.5 cm of goal; maximum 350 steps | Success/episode condition은 simulator object center를 사용한다. [§IV-A, p.5] |
| Curriculum | Yes | Paired simulated tactile labels; expert trajectories; domain randomization | Data generation과 sim training용 정보이며 real runtime input이 아니다. [§III-A; §IV-A, pp.3,5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Visual and tactile/contact-depth information are complementary for pushing | Sensor combination ablation | Visual-only; tactile-only; visual+tactile observations under multiple shapes/trajectories | Table II에서 visual+tactile 계열이 단일 modality baselines보다 대체로 높은 success와 낮은 trajectory error를 보인다. | §IV-C; PDF p.6 ; Table II |
| Generated tactile improves over the visual-only baseline | Controlled comparison | ViTacGen visual-only hardware input vs visual-only policy; seen and unseen objects | 실물 50-trial tests와 unseen-object tests에서 ViTacGen이 visual-only baseline보다 더 높은 success/lower error를 보고한다. | §IV-D–E; PDF pp.6–7 ; Tables III–IV ; Fig.5 |
| Cross-attention fusion matters | Representation ablation | Cross-attention vs addition vs concatenation | Reported success is 95% for cross-attention, 77% addition, 90% concatenation. | §IV-F; PDF p.7 ; Table V |
| MoCo contrastive alignment matters | Representation ablation | MoCo vs SimCLR vs no contrastive alignment | MoCo reports 95% success versus 89% SimCLR and lower without contrastive alignment. | §IV-F; PDF p.7 ; Table VI |

## 13. Author-stated Limitations

저자들은 contact-depth가 high-level contact geometry만 나타내고 detailed physical properties, local force distributions, fine surface geometry를 포착하지 못한다고 명시한다. Visual-to-touch quality는 paired simulated data와 visual domain randomization에 의존하며, 실물 센서 force를 직접 측정하지 않는다. [§V, p.8]

## 14. Author-stated Future Work

저자들은 visual motion에서 material/physical properties와 shear-force cues까지 예측하도록 representation을 확장하겠다고 제안한다. [§V, p.8]

## 15. Review-relevant Findings

- 실물 실행은 RGB camera만 사용하며 physical tactile sensor와 F/T sensor를 사용하지 않는다.
- Tactile-like input은 최근 3 RGB frames에서 생성한 optical contact-depth image다.
- Current object pose는 numeric state로 주어지지 않고 RGB에 implicit하게 나타난다.
- Generated contact depth는 contact geometry를 남기지만 local force distribution, shear, fine geometry를 제공하지 못한다.
- Modality comparison은 visual+tactile 조합의 이득을 보이지만 generated cue와 real tactile measurement의 동일성을 검증하지 않는다.
- Reward와 termination은 simulator object-center GT를 사용한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Task / pipeline | §III pp.3–4 |
| Observation / tactile generation | §III-A–C pp.3–4 |
| Reward / success / episode | §IV-A p.5 |
| Modality comparison | §IV-C/Table II p.6 |
| Real / unseen objects | §IV-D–E pp.6–7 |
| Fusion / contrastive ablations | §IV-F/Tables V–VI p.7 |
| Limitation / Future | §V p.8 |
