# Attention for Robot Touch: Tactile Saliency Prediction for Robust Sim-to-Real Tactile Control

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B044`
- Authors: Yijiong Lin; Mauro Comi; Alex Church; Dandan Zhang; Nathan F. Lepora
- Year: 2023
- Venue: 2023 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 10806–10812
- DOI / arXiv: 10.1109/IROS55552.2023.10341888 / Not stated
- PDF version: IEEE conference publisher PDF
- Version note: 선택 범위 내 다른 버전 없음
- Page count: 7
- SHA-256: `806a84c298a9045f891ef497c4605430841524753a285b7f65dcad9ca5405690`
- PDF filename: `Lin 등 - 2023 - Attention for Robot Touch Tactile Saliency Prediction for Robust Sim-to-Real Tactile Control.pdf`
- 읽은 범위: PDF pp.1–7 전체(방법 수식, Tables I–II, Figs.1–6, discussion/future, 참고문헌). pp.5–6의 pose/control 비교표와 pipeline을 렌더 확인. Project page와 supplement는 확인하지 않음.
- 근거: 이번 배치의 PDF 원문에서 새로 분석했다. 기존 상세 노트는 재사용하지 않았다. 아래 페이지는 PDF 1-based page다.

## 2. Relevance to This Review

**Relevant**. 단일 TacTip image에 target edge와 distractor contacts가 함께 나타날 때 contact-depth map과 saliency map으로 target contact만 분리하고, tactile pose PID와 image-based deep-RL controller 모두의 실물 edge-following failure를 복구한다. Net F/T가 아니라 spatial tactile image를 사용해 multi-contact ambiguity를 줄이는 직접 사례이며, current global object pose·scene vision 없이 local target-contact pose/shape를 보완한다.

Screening 위치: Abstract/§I, PDF p.1; §III, pp.2–4; §IV-C–V, pp.5–7.

## 3. Task

TacTip으로 target object edge를 따라가되 bolt 등 여러 distractor contacts가 동시에 sensor에 닿는 cluttered edge-following을 수행한다. 보조 실험은 static local edge pose y/Rz 추정이다. (§IV-C–D, PDF pp.5–7)

## 4. Method

### 4.1. Overall Pipeline

Real tactile image → ConDepNet contact-depth map → TacSalNet target saliency map → either tactile PoseNet+PID or direct image-based deep-RL controller. TacNGen VAE supplies diverse synthetic noise for training. (§III/Fig.2; §IV-D/Fig.5, pp.2–6)

### 4.2. Observation

Runtime sensing is a single TacTip image and derived contact-depth/saliency map. PID branch additionally receives local y/Rz pose estimate; no global object pose or scene vision. (§III-A–C/§IV-C–D, pp.2–6)

### 4.3. Action

Pose controller follows target y/Rz; image-based deep-RL policy outputs TCP x/y actions. (§IV-D/Fig.5, p.6)

### 4.4. Controller

Two reused controllers are compared: pose-based PID and image-based deep RL. Their detailed gains/rates are not stated in this PDF. (§IV-D, p.6)

### 4.5. Learning / Optimization Method

ConDepNet/TacSalNet use pix2pixGAN objectives; TacNGen is a VAE. 7000 paired edge contacts train perception. No new RL policy, reward or critic is trained/described here. (§III-B–D/§IV-A, pp.2–4)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Tactile PoseNet predicts local target-edge lateral position y; direct image-RL branch does not output pose | Each tactile frame | No global object center/current pose. Controller target pose is separate. 근거: §IV-C–D/Fig.5, PDF pp.5–6 |
| Orientation | 기타 | Tactile PoseNet predicts local edge orientation Rz for PID branch | Each tactile frame | Image-RL branch outputs x/y and does not use an explicit Rz estimate. 근거: §IV-C–D/Fig.5, pp.5–6 |
| Shape / Geometry | 기타 | Local target contact shape in a saliency map; global contours/CAD used as labels/evaluation | Each tactile frame | TacSalNet is trained on straight edges but tested on unseen corners/contours. 근거: §III-B–C/§IV-B–D, pp.2–6 |
| Physical Parameters | 미제공 | No mass/friction/stiffness vector | No | Distractor distance affects ambiguity but is not an actor parameter. 근거: §IV-C–D, pp.5–6 |

## 6. Missing Object Information and Compensation

Global object/scene pose가 없음 → raw tactile의 target+noise deformation을 contact-depth map으로 바꾸고 target saliency만 분리 → PID에는 local y/Rz를, image-RL에는 saliency image를 제공한다. 이는 net F/T보다 spatial contact source를 구분하지만 target feature class와 simulation-labelled saliency를 요구한다. (§III–IV, pp.2–6)

## 7. Tactile

### 7.1. Raw Sensor

Single real grayscale TacTip marker image showing deformation from the target edge and any distractors. (§III-A/§IV-A, PDF pp.2,4)

### 7.2. Preprocessing

ConDepNet maps the real marker image to a contact-depth map; TacSalNet maps depth to per-pixel target saliency. TacNGen VAE supplies simulated distractor shapes during training. (§III-B–D/Fig.2, pp.2–4)

### 7.3. Policy Representation

Pose PID uses PoseNet-estimated y/Rz from the saliency-filtered image; direct deep-RL uses the saliency/contact-depth image and outputs x/y. (§IV-C–D/Fig.5, pp.5–6)

### 7.4. Retained Information

Pixelwise target-contact probability, local deformation geometry and target-edge local pose/shape while preserving unseen contour variations. (§III-A–C/§IV-C–D, pp.2–6)

### 7.5. Removed / Unavailable Information

Distractor contact features are intentionally suppressed. No calibrated force magnitude/shear, global object pose or full scene geometry remains. (§III-C/§IV-C, pp.3,5)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. TacTip optical image is not converted to a force/wrench vector. (§III–IV, pp.2–6)

### 8.2. Representation

해당 없음. (§III–IV, pp.2–6)

### 8.3. Role

해당 없음. Spatial target-contact separation is achieved from tactile images. (§III–IV, pp.2–6)

### 8.4. Required Assumptions

해당 없음 to F/T. Saliency assumes a defined target feature class and transferable simulated contact-depth labels. (§III-A–D, pp.2–4)

### 8.5. Reported Limitation / Ambiguity

No net-wrench/contact inversion is evaluated. Close overlapping contacts can be misclassified as target. (§IV-C, p.5)

## 9. Other Observations

External camera나 global geometry는 controller input이 아니다. CAD contour와 paired simulation depths는 training/evaluation에 쓰인다. Robot proprioception/history와 reused RL goal/reward 세부는 미명시다.

## 10. Tactile–Other Modality Relationship

Independent F/T는 없다. Tactile saliency는 한 sensor image 안의 target/distractor contacts를 spatially 분리해 local ambiguity를 줄인다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Actor | No object GT reported | Deep-RL controller receives contact-depth/saliency tactile image and outputs x/y | Pretrained controller details are not restated; no global object pose | §IV-D/Fig.5, p.6 |
| Critic | Not stated | Reused image-based deep-RL policy critic is not described | No asymmetric GT inference | §IV-D, p.6 |
| Reward | Not stated | No new RL training/reward in this paper | Control comparison uses frozen prior methods | §IV-D, p.6 |
| Termination | Not stated | Evaluation marks distractor trapping within 50 steps as failure; contour completion is measured | Exact policy termination logic absent | Fig.6 caption, p.7 |
| Curriculum | Supervised simulation labels | Known target contact-depth maps, synthetic overlay and noise maps label ConDepNet/TacSalNet | Training-only perception labels; not runtime object GT | §III-B–D, pp.2–4 |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Learned tactile-noise prior improves saliency | Representation ablation | TacNGen-trained TacSalNet-1 vs Gaussian-noise TacSalNet-2; 1000 real samples | AUC-J both 0.995; SIM 0.984 vs 0.972, CC 0.957 vs 0.936, NSS 4.629 vs 4.288. | §IV-B/Table I/Fig.3, PDF pp.4–5 |
| Saliency restores local contact-pose accuracy | Input augmentation comparison | PoseNet with vs without TacSalNet under bolt/comb/clip and other distractors | Without: y 1.84–2.41 mm, Rz 14.0–30.0°. With: y 0.26–0.40 mm, Rz 4.44–5.06°; near y≈−2.5 mm still degrades. | §IV-C/Fig.4, PDF p.5 |
| Saliency enables robust closed-loop control | Input augmentation comparison; Failure analysis | PID and image-deep-RL, each without vs with TacSalNet; 4 objects × 10 trials × 2 methods = 80 tests | Both methods fail without saliency. With it PID error 0.53–0.91 mm and RL error 0.94–1.21 mm over 300–520 mm contours. | §IV-D/Table II/Figs.5–6, PDF pp.5–7 |

## 13. Author-stated Limitations

Edge target, marker-based TacTip와 Tactile Gym depth simulation에만 실증했다. Distractor가 y≈−2.5 mm로 매우 가까우면 이를 target 일부로 예측해 pose accuracy가 낮아진다. Reused deep-RL actor/critic/reward/termination 세부는 이 PDF에 미명시다. (§IV-C/V, pp.5–6)

## 14. Author-stated Future Work

다른 tactile sensor types로의 적용과 unexpected tactile distractors가 있는 다양한 exploration/manipulation task로의 확장을 제시한다. (§V, pp.6–7)

## 15. Review-relevant Findings

- Current global object pose 대신 local target-edge y/Rz 또는 saliency image를 사용한다.
- Raw image의 target+noise를 모두 contact-depth map에 보존한 뒤 target만 saliency로 선택한다.
- TacSalNet training labels는 simulation GT이며 runtime에는 필요 없다.
- PID와 image-RL 모두 saliency 없이는 distractor에서 실패했다.
- F/T modality, critic input, RL reward/termination은 미명시 또는 해당 없음이다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Tactile representation pipeline | §III-A–D/Fig.2, PDF pp.2–4 |
| Training data | §IV-A, p.4 |
| Saliency ablation | §IV-B/Table I/Fig.3, pp.4–5 |
| Local pose evidence | §IV-C/Fig.4, p.5 |
| Control comparison | §IV-D/Table II/Figs.5–6, pp.5–7 |
| Limitations / future | §IV-C/§V, pp.5–7 |
