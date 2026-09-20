# Current as Touch: Proprioceptive Contact Feedback for Compliant Dexterous Manipulation

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B053`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Chenyang Ma; Yunchao Yao; Zhenyu Wei; Ruogu Li; Daniel Szafir; Mingyu Ding
- Year: 2026
- Venue: Not stated
- DOI / arXiv: Not stated / 2607.03529v1
- PDF version: arXiv v1, 3 July 2026
- Page count: 18
- SHA-256: `34aa3921204a77c9ce36aeaf5fe0b59191fa25fff206dabd38a4c5634578a88e`
- PDF filename: Ma 등 - 2026 - Current as Touch Proprioceptive Contact Feedback for Compliant Dexterous Manipulation.pdf
- 확인 범위: PDF pp.1–18 전체(본문 pp.1–9, Appendices A–C pp.9–15, 참고문헌 pp.16–18); Fig.3, Tables 1–4/7 및 Appendix C를 렌더 확인. Webpage/video는 확인하지 않음.

## 2. Relevance to This Review

`Relevant`

외부 tactile/F/T 없이 hand motor current와 joint-state history를 contact/load cue로 사용하고 current 제거 ablation을 실물에서 수행한다. Current는 calibrated force나 wrench가 아니며 contact location도 주지 않으므로, proprioceptive force proxy의 정보·가정·모호성과 object-pose 보완 조건을 직접 비교할 수 있다.

## 3. Task

LEAP Hand+Franka와 Dex3+Unitree G1에서 foam-cup stacking, whiteboard wiping을 current-conditioned teleoperation으로, dynamic bottle holding과 single-card picking을 autonomous policy로 수행한다. 목표는 force를 추정하는 것이 아니라 standard position interface에서 적절한 compliant reference position(CRP)을 예측하는 것이다. [§1/§4, PDF pp.2–9]

## 4. Method

### 4.1. Overall Pipeline

최근 robot joint state와 raw motor-current history + teleoperation intent velocity 또는 task-level object/goal pose → temporal convolution observation encoder → ACT-style action encoder(training only)와 Transformer chunk predictor → CRP sequence → 최근 prediction의 exponential aggregation → fixed-gain PD controller. Offline-smoothed current는 auxiliary training target일 뿐 deployment input은 raw current다. [§3/Fig.5 pp.4–7; Appendix A pp.9–13]

### 4.2. Observation

기본 history는 10 frames다. Teleoperation은 $\{q,I,v_{intent}\}$를, policy mode는 $\{q,I,g\}$를 사용한다. $q$는 hand와 arm joint positions 또는 arm EEF pose이고, $g$는 object/goal/pouring SE(3) pose다. Single-card는 VICON card-deck pose를 training과 inference 모두에서 계속 사용하고, bottle task는 fixed pouring-cup pose를 제공한다. Camera image는 model observation이 아니지만 teleoperator는 task outcome을 시각적으로 보며 command를 교정한다. [Eqs.3–6 pp.5–6; Appendix A.2 pp.10–11]

### 4.3. Action

10-frame CRP action chunk다. Label은 human-corrected target joint position $q_{cmd}$이며 hand-joint reference와 embodiment에 따라 arm-joint 또는 EEF-pose reference를 포함한다. 실행 때 여러 과거 prediction을 exponential average한다. Main text는 최근 2개/first two라고 쓰지만 Appendix A.5는 $M=3$을 best balance 및 사용 설정으로 서술하여 실제 기본값이 일관되지 않는다. [§3.2–3.4 pp.5–7; Appendix A.2/A.5 pp.10–13]

### 4.4. Controller

Predicted CRP를 fixed-gain PD가 추종하여 $\tau=K_p(q^c_{ref}-q)-K_d\dot q$의 position error로 interaction torque를 만든다. Direct torque command, explicit wrench estimator, contact-Jacobian inversion을 사용하지 않는다. Exact gains와 control frequency는 미명시다. [Eq.1 p.4; Appendix C.3 p.15]

### 4.5. Learning / Optimization Method

ACT-style supervised behavior cloning이다. Temporal convolution encoder와 Transformer가 action chunk를 예측하고, training-only future-action encoder/KL regularization 및 offline-smoothed-current auxiliary head를 쓴다. Loss는 CRP MSE+annealed KL+current auxiliary MSE이며 AdamW, 300 epochs다. 보상·critic은 없다. [§3.3–3.4 pp.6–7; Appendix A.3–A.4 pp.11–13]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Single-card: VICON deck SE(3)를 train/inference에 갱신. Bottle: fixed pouring-cup의 precomputed SE(3). Teleoperation model: object position 없음. | Card pose는 실행 중 tracking; fixed goal은 갱신 없음 | Task마다 조건이 다르며 current가 object pose를 복원하지 않는다. [§3.3 p.6; §4.3 p.9; Appendix A.2 pp.10–11] |
| Orientation | 기타 | Single-card: VICON rotation; bottle: fixed pouring pose; teleoperation model: object orientation 없음 | Card orientation은 실행 중 tracking; fixed pose는 갱신 없음 | Dex3/G1 pose는 position+6D rotation representation을 사용한다. [§4.3 p.9; Appendix A.2 p.11] |
| Shape / Geometry | 미제공 | Mesh/CAD/dimensions 또는 current shape estimate 없음 | 해당 없음 | Training object set의 다양성은 actor의 explicit shape input이 아니다. [§4/Appendix A.1, PDF pp.7–10] |
| Physical Parameters | 미제공 | Stiffness, mass, load, friction을 수치 input으로 제공하지 않음 | 해당 없음 | Bottle water mass는 평가 조건이며 actor input이 아니다. Current는 이를 직접 측정하는 calibrated sensor가 아니다. [§4.2–4.3 pp.8–9; Appendix C pp.14–15] |

## 6. Missing Object Information and Compensation

정확한 contact location, distributed pressure/shear, calibrated force/wrench, object stiffness/load와 대부분 task의 explicit shape는 제공되지 않는다. 반복 가능한 hardware-specific current patterns와 joint history, task pose/intent, demonstration supervision으로 CRP를 직접 예측한다. Single-card에서는 VICON pose가 별도로 필요하므로 current-only localization 성과가 아니다. [§3.3 pp.5–6; §5 p.9; Appendix C pp.14–15]

## 7. Tactile

### 7.1. Raw Sensor

외부 tactile sensor를 사용하지 않는다. 저자들이 motor current를 “tactile-like” proprioceptive contact feedback이라고 부르지만 taxel/skin/optical tactile measurement는 아니다. [Abstract/§1–2, PDF pp.1–4]

### 7.2. Preprocessing

Tactile preprocessing은 해당 없음. 별도 motor current는 inference에서 raw/zero-delay로 쓰며 min–max normalize한다. Median filter 5와 moving average 5는 auxiliary label·diagnostic용 offline smoothing이다. [§3.4 p.6; Appendix A.2 pp.10–11]

### 7.3. Policy Representation

Tactile image, pressure grid, contact Boolean은 없다. Contact 관련 실행 표현은 10-frame joint-current vector history를 temporal convolution으로 encode한 latent다. [§3.3–3.4 pp.5–7; Appendix A.3 p.12]

### 7.4. Retained Information

Motor load와 반복 가능한 contact resistance·grasp load의 상관 정보는 유지할 수 있으나 explicit tactile spatial information은 제공하지 않는다. [§1 pp.2–3; Appendix C pp.14–15]

### 7.5. Removed / Unavailable Information

Contact point, finger-surface pressure map, local normal/shear 방향, texture/geometry와 calibrated force magnitude는 직접 관측하지 않는다. [§2–3 pp.3–6; Appendix C.2–C.3 p.15]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Policy 실행 sensor는 dexterous-hand joint별 raw motor current다. Figure 3의 SRI 6-axis F/T는 motor-current/contact-force 상관을 측정하는 외부 기준으로만 사용하며 policy input이 아니다. Sensor model, mounting details, range는 미명시다. [Fig.3 p.3; Acknowledgments p.9]

### 8.2. Representation

Raw current $I_{t-H+1:t}$를 joint position history와 함께 temporal encoder에 넣는다. Explicit torque/force/wrench로 변환하지 않는다. Training-only auxiliary target은 median-5+moving-average-5 current이고 전체 input/action은 train-split min–max로 normalize한다. [§3.3–3.4 pp.5–7; Appendix A.2 pp.10–11]

### 8.3. Role

Contact resistance, grasp loading, slip/overload와 dynamic load에 상관된 cue로 CRP를 조절한다. PD position error가 최종 torque를 발생시킨다. Force estimate나 안전 threshold controller를 출력하지 않는다. [§1/§3 pp.2–7; Appendix C.3 p.15]

### 8.4. Required Assumptions

Motor current가 해당 hand/transmission/contact에 대해 충분히 informative하고, training data가 internal-motion current와 contact response를 포괄하며, fixed PD interface가 CRP error를 적절한 torque로 바꿔야 한다. 일부 task는 external pose 또는 human intent가 추가로 필요하다. [§3.1–3.3 pp.4–6; §5 p.9]

### 8.5. Reported Limitation / Ambiguity

Current에는 contact 외에 friction, inertia/Coriolis/back-EMF, cable/tendon preload, backlash, gravity, thermal drift, offsets, quantization, communication spikes가 섞인다. Unknown/multiple contact와 changing normal 때문에 current→contact wrench inverse가 ill-conditioned하며 contact locality를 복원하지 않는다. [§5 p.9; Appendix C.1–C.2 pp.14–15]

## 9. Other Observations

Hand/arm joint positions, teleoperation intent velocity 또는 task-level SE(3), 10-frame history를 쓴다. Single-card의 VICON은 continuous external tracking이며 blind actor 조건과 다르다. Future demonstrated action chunk는 training posterior에만 들어가고 inference style latent는 zero다. Previous executed action은 observation으로 명시되지 않지만 최근 action predictions는 command aggregation에 사용한다. [§3.2–3.4 pp.5–7; Appendix A.2–A.5 pp.10–13]

## 10. Tactile–Other Modality Relationship

External tactile는 없고 motor current가 tactile-like cue를 대신한다. Figure 3의 외부 F/T는 correlation 기준일 뿐 deployment sensor가 아니다. w/o Current ablation은 kinematics/intent 또는 pose만으로는 contact-conditioned CRP가 약해짐을 보여 주지만, tactile-vs-current 또는 tactile+current 조합은 비교하지 않는다. 따라서 current가 spatial tactile나 wrist F/T와 같은 정보를 준다고 결론내릴 수 없다. [Fig.3 p.3; §4/Tables 1–4 pp.7–9]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Mixed; external tracked/fixed task pose | Raw current, robot state, intent or task-level pose | Single-card의 VICON pose는 training과 inference에 모두 필요하므로 training-only GT가 아니라 deployment tracking requirement다. Teleop human vision은 model 밖에 있다. [§3.3 p.6; §4.3 p.9; Appendix A.2 p.11] |
| Training action encoder | Yes; future demonstration action chunk | ACT posterior style latent during training | Inference에는 future action이 없어 style latent를 zero로 둔다. [Appendix A.3 p.12] |
| Auxiliary target | Yes; offline-smoothed current | Median-5 + moving-average-5 current target | Training-only head이며 deployment는 raw current를 사용한다. [§3.4 pp.6–7; Appendix A.2–A.3 pp.10–12] |
| Critic / Reward | Not applicable | Supervised imitation; critic·reward 없음 | Policy gains를 RL result로 기록하지 않는다. [§3.3–3.4 pp.6–7] |
| Termination | Not stated | Operator/task trial endpoints and evaluation outcomes | Learned or sensor-based autonomous termination rule은 제공 PDF에서 확인되지 않는다. [§4 pp.7–9] |
| Curriculum | No | Task-specific demonstrations; no curriculum stated | Object set와 load evaluation을 curriculum으로 바꾸어 기록하지 않는다. [§4/Appendix A.1 pp.7–10] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Motor current와 measured normal force의 상관 | Controlled measurement | Current+joint-position regressor; external F/T labels on Dex3 and LEAP | Dex3 RMSE 10.09 g, $R^2=0.99$; LEAP RMSE 17.75 g, $R^2=0.95$. Main CRP policy는 이 regressor/force estimate를 사용하지 않는다. | §1; PDF pp.2–3 ; Fig.3 |
| Teleoperation에서 current 입력의 기여 | Input/Sensor ablation | Retargeting vs same CRP model w/o Current vs w/ Current; novice/skilled 각 15 trials | Cup w/ Current는 deformation 0%, grasp failure 6.7%/3.3%, time 16.8/16.1 s; w/o Current failure 76.7%/71.7%. Table 1에 failure가 남아 있어 본문의 “100% success” 문구와 일치하지 않는다. | §4.2; PDF pp.7–8 ; Table 1 |
| Sustained wiping에서 current 입력의 기여 | Input/Sensor ablation | 동일 세 방법; novice/skilled 각 15 trials | w/ Current success 100%/100%, time 6.9/6.5 s; w/o Current 46.7%/60.0%; direct retargeting 40.0%/100.0%. | §4.2; PDF pp.7–8 ; Table 2 |
| Dynamic load adaptation | Input/Sensor ablation | ACT-style policy w/o vs w/ Current; load별 12 trials | 250 g stable 16.7%→100%; OOD 350 g에서 baseline fell 100%, current policy는 stable 41.7%/slipped 58.3%/fell 0%. | §4.3; PDF pp.7–9 ; Table 3 |
| Thin-object retrieval의 contact regulation | Input/Sensor ablation | Single-card policy w/o vs w/ Current; VICON pose는 둘 다 사용, 52 trials | Strict success 55.8%→76.9%, tolerant 65.4%→90.4%, 2+ cards 7.7%→0%, missed 26.9%→9.6%. | §4.3; PDF pp.7–9 ; Table 4 |
| Execution aggregation의 smoothness–responsiveness trade-off | Component ablation | $M=1,2,3,4$ recent predictions; 각 10 trials | Grasp success 40/70/90/100%, hold 90/100/100/70%. Main text의 2-frame 서술과 Appendix의 $M=3$ 선택이 불일치한다. | Appendix A.5; PDF p.13 ; Table 7 |

## 13. Author-stated Limitations

저자들은 current informativeness가 hand hardware·transmission·measurement에 의존하고, ab/adduction joint가 없는 hand에서는 shear/vertical-load signal이 약할 수 있다고 밝힌다. CRP label은 analytical optimum/force label이 아니라 human-corrected empirical target이므로 demonstration quality·coverage에 의존한다. Policy task는 필요 시 object pose를 사용해 perception/localization을 해결하지 않는다. Auxiliary current loss, execution smoothing, heuristic current-threshold controller를 모두 ablate하지 않았다. Appendix C는 current에 hardware dynamics·friction·backlash·thermal drift·random spikes가 섞이고 contact-force inversion이 ill-conditioned함을 명시한다. [§5 p.9; Appendix C pp.14–15]

## 14. Author-stated Future Work

Robust perception/localization 통합과 auxiliary current loss·execution smoothing·heuristic threshold controller의 상세 component study를 future work로 명시한다. 더 넓은 hand/transmission에서의 신호 일반화나 explicit contact localization 계획은 원문에 구체적으로 제시되지 않는다. [§5 p.9]

## 15. Review-relevant Findings

- Motor current는 calibrated force/wrench가 아니라 contact-correlated proprioceptive signal이다.
- External 6-axis F/T는 Figure 3의 측정 기준이며 learned CRP policy의 실행 입력이 아니다.
- Single-card policy는 VICON object pose를 실행 중 계속 사용하므로 current-only 또는 blind localization 결과가 아니다.
- Current 제거 ablation은 실물 네 과업에서 직접 evidence를 제공하지만 external tactile와의 비교는 없다.
- Current history는 contact locality·normal/shear map을 보존하지 않으며 internal dynamics/noise와 혼합된다.
- Main text의 2-prediction smoothing과 Appendix의 $M=3$ 선택이 불일치해 exact deployment aggregation은 미명시로 남긴다.
- Table 1의 nonzero grasp failure 때문에 저자의 foam-cup “100% success” 서술을 그대로 재사용하지 않는다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / task pose | §3.2–3.4 pp.5–7; Appendix A.2 pp.10–11 |
| Motor current / external F/T | Fig.3 p.3; Appendix C pp.14–15 |
| Action / controller | §3.1–3.3 pp.4–6; Appendix A.5 p.13 |
| Tactile | §1–2 pp.1–4: external tactile 미사용 |
| Training-only information | §3.4 pp.6–7; Appendix A.2–A.4 pp.10–13 |
| Current ablations | Tables 1–4, PDF pp.7–9 |
| Aggregation ablation | Table 7, PDF p.13 |
| Limitations / Future Work | §5 p.9; Appendix C pp.14–15 |
