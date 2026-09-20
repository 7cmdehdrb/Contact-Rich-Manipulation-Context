# SAVR: Scooping Adaptation for Variable Food Properties via Reinforcement Learning

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B093`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: J-Anne Yow; Wei Tech Ang
- Year: 2025
- Venue: 2025 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)
- DOI / arXiv: 10.1109/IROS60139.2025.11247626 / Not stated
- PDF version: IEEE publisher version
- Page count: 7
- SHA-256: `677cb337aa99b570f790158662d5d107780dacb45e49b4d7a87798397c8c9a18`
- PDF filename: Yow 및 Ang - 2025 - SAVR Scooping Adaptation for Variable food properties via Reinforcement Learning.pdf
- 확인 범위: PDF pp.1–7 전체; state/action/reward, F/T history, DMP/controller, simulation randomization, real perception pipeline, modality ablations, limitations/future를 확인하고 Figures 1/3와 Tables II–V 렌더 검토.

## 2. Relevance to This Review

`Relevant`

Wrist 6-axis F/T history와 segmented spoon/food image를 함께 사용해 current food properties를 직접 제공하지 않고 scooping trajectory를 조절하며 sensor-modality ablation을 제공한다. F/T가 interaction dynamics를, vision mask가 spoon/food spatial cue를 담당하는 실제 역할과 privileged simulator reward/data randomization을 구분할 수 있어 본 Review 질문에 직접 관련된다.

## 3. Task

xArm-6가 green beans, corn, mashed potatoes 등 서로 다른 texture/cohesion의 food에서 user-specified target amount를 spoon으로 scoop한다. 목표는 fixed DMP trajectory를 그대로 재생하는 대신 vision과 force history에 따라 z-direction corrective term을 조절하여 target weight percentage에 근접한 bite를 얻는 것이다. [§III/§V, PDF pp.3,5–7]

## 4. Method

### 4.1. Overall Pipeline

Initial RGB-D bowl/food center → DMP start $y_0$ 설정; SAM2가 spoon/food masks를 tracking → 최근 5 EEF poses + 최근 5 wrist 6-D F/T + cropped 200×200 mask + target amount + DMP index → PPO actor at 20 Hz → scalar z-force correction $C_f$ → demonstrated DMP at 100 Hz → position controller at 100 Hz → xArm motion. [§III-A/§IV-B/§V-A, pp.3–5]

### 4.2. Observation

State는 5-step EEF pose history(각 position+quaternion 7-D), 5-step 6-D F/T history, separate IDs의 spoon/food cropped mask 3×200×200, target amount, actual amount(episode final step에서만 갱신), DMP step index다. Food pose는 initial DMP start 설정에 사용되며 actor에 current numeric pose tracking vector로 계속 제공된다고 명시하지 않는다. [§III-A, p.3; §V-A, p.5]

### 4.3. Action

Scalar continuous $a_t ∈ [-1,1]$가 DMP external force term $C_f$에 직접 들어가 z-direction trajectory를 perturb한다. $a=0$이면 unperturbed DMP를 실행한다. [§III-A, p.3]

### 4.4. Controller

Single demonstration에서 학습한 DMP와 robot position controller가 100 Hz로 실행되고 PPO policy는 20 Hz로 $C_f$를 갱신한다. 5-step history가 frequency gap의 context를 제공한다. [§IV-B, p.4]

### 4.5. Learning / Optimization Method

Stable-Baselines3 PPO를 MuJoCo에서 sparse terminal portion reward로 학습한다. Episode마다 food/container pose, food volume, particle size/mass/damping/friction과 target amount를 randomize한다. DMP prior가 trajectory structure를 제공해 RL은 scalar force correction만 학습한다. [§III-A/§IV-A–B, pp.3–4]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Initial | RealSense D435i depth + GroundingDINO bowl/food-center detection으로 DMP start $y_0$ 계산 | No | Numeric food pose는 initial DMP alignment에 사용되고 current position tracking vector로 policy에 계속 입력되지 않는다. [§V-A p.5] |
| Orientation | 미명시 | Food/object current orientation 제공 조건이 원문에서 확인되지 않음 | 미명시 | Task는 bowl-contained particulate/deformable food이며 explicit orientation 정의가 없다. [§III/§V pp.3,5] |
| Shape / Geometry | 기타 | SAM2가 current spoon and food masks를 tracking; cropped segmented image를 actor에 제공 | Yes | Full mesh/CAD/dimension은 제공하지 않으며 mask는 appearance/area cue다. [§III-A p.3; §V-A p.5] |
| Physical Parameters | 미제공 | Texture, particle size/mass/friction/density를 runtime vector로 제공하지 않음 | 해당 없음 | Training에서 particle properties를 randomize하고 real에서는 sensor response로 간접 적응한다. [§IV-A p.3; §V-C pp.6–7] |

## 6. Missing Object Information and Compensation

Current food physical properties와 continuously updated numeric pose 미제공 → 5-step wrist F/T + spoon/food masks + EEF pose history → interaction resistance와 spoon/food area/configuration을 바탕으로 DMP z-force correction을 조절한다.

DMP가 food texture에 적응하지 못하는 부족분 → PPO scalar force term $C_f$ → trajectory 전체를 새로 학습하지 않고 vertical scoop path만 online 수정한다. Initial bowl/food center는 RGB-D로 DMP start를 맞춘다. [§III/§V-A, pp.3–5]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§I–VI, PDF pp.1–7]

### 7.2. Preprocessing

사용하지 않음. [§I–VI, PDF pp.1–7]

### 7.3. Policy Representation

사용하지 않음. [§I–VI, PDF pp.1–7]

### 7.4. Retained Information

사용하지 않음. [§I–VI, PDF pp.1–7]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§I–VI, PDF pp.1–7]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Spoon을 Sunrise Instruments M3712B 6-axis force-torque sensor에 장착하며 sensor는 robot wrist/end effector between spoon and arm에 위치한다. [§V-A, p.5]

### 8.2. Representation

최근 $k=5$ time steps의 6-D F/T sequence $s_{ft} ∈ R^{6×5}$. 개별 axes, frame, normalization/filtering은 원문에서 명시되지 않는다. [§III-A p.3; §IV-B p.4]

### 8.3. Role

PPO actor observation으로 food–spoon interaction과 hidden food properties에 반응해 DMP z-force correction을 조절한다. Segmentation-only/force-only ablation에서 force-only가 real에서 더 높아 force의 중요성이 보고된다. [§III/§V-C, pp.3,6]

### 8.4. Required Assumptions

Calibrated spoon-mounted 6-axis F/T, fixed spoon/tool transform, DMP start/goal alignment, 5-step synchronized EEF/wrench histories, contact within the scooping motion prior가 필요하다. [§III-A/§IV-B/§V-A, pp.3–5]

### 8.5. Reported Limitation / Ambiguity

Net wrist wrench에서 local food-contact location, distributed contact 또는 food identity를 복원하지 않는다. 원문은 F/T 자체 ambiguity를 직접 논의하지 않으며 real performance가 sensor/perception error의 영향을 받을 수 있다고 설명한다. [§IV-E p.4; §V-C p.6]

## 9. Other Observations

Vision은 wrist RealSense D435i RGB-D다. GroundingDINO+depth가 initial bowl/food center를 구하고, GroundingDINO bounding boxes와 SAM2가 spoon/food masks를 tracking한다. Proprioception은 5-step EEF position+quaternion, goal은 target portion amount, temporal context는 EEF/F/T 5-step histories와 DMP step index다. Previous PPO action/recurrent state는 명시되지 않는다. [§III-A p.3; §V-A p.5]

## 10. Tactile–Other Modality Relationship

F/T는 food–spoon interaction load/dynamics를, segmented vision은 spoon and food area/configuration과 sim-to-real-robust appearance cue를, EEF history와 DMP index는 motion phase를 제공한다. Full SAVR가 real 10% threshold에서 force-only와 segmentation-only보다 높고 Table V의 relaxed criterion에서도 조합이 가장 높아 modality combination의 효용을 직접 뒷받침한다. Tactile은 사용하지 않는다. [§V-C/Tables IV–V, p.6]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | 5-step EEF pose/F/T; segmented mask; target; DMP index; final amount | Current food GT properties/pose는 execution actor input이 아니다. [§III-A, p.3] |
| Critic | Not stated | PPO critic observation not separately described | Asymmetric critic 또는 simulator particle GT 사용은 원문에서 확인되지 않는다. [§III–IV, pp.3–4] |
| Reward | Yes | Actual scooped particle amount vs target at final simulation step | Simulator particle count/volume로 sparse terminal reward를 계산한다. [§III-A/Eq.3, p.3] |
| Termination | No | Fixed $T=20$ DMP timesteps | Object GT success/failure가 아니라 fixed trajectory horizon에 종료한다. [§IV-B, p.4] |
| Curriculum | Yes | Food/container poses, volume, particle size/mass/damping/friction and target amount randomization | Simulation training/data generation only; runtime explicit parameters가 아니다. [§IV-A, p.3] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| F/T and segmented vision together improve sim-to-real scooping | Sensor combination ablation | Full SAVR vs ForceOnly vs SegImageOnly on real foods | 10% criterion overall success: 36.11% full, 22.22% force-only, 2.78% segmentation-only; mean amount error 12.79%, 28.77%, 41.82%. | §V-C; PDF p.6 ; Table IV |
| Combined sensing remains strongest under practical tolerance | Sensor combination ablation | Full/force-only/segmentation-only/DMP at 20% target tolerance | Full SAVR reaches 83.33% overall success versus force-only 36.11%, segmentation-only 8.33%, DMP 30.56%. | §V-C; PDF p.6 ; Table V |
| Segmentation improves over raw RGB+force in simulation | Representation ablation | Segmented mask+force vs RGB+force | Overall simulation success is 57.33% vs 35.67%, with lower amount error 10.77% vs 18.19%. | §IV-E; PDF pp.4–5 ; Table II |
| DMP prior reduces search difficulty | Controlled comparison | SAVR vs PPO-NoPrior and fixed DMP in simulation | SAVR reports 57.33% success; PPO-NoPrior 0%; DMP 18.50%, across target levels. | §IV-D–E; PDF pp.4–5 ; Tables II–III |

## 13. Author-stated Limitations

Maximum scoopable amount를 spoon의 heaped capacity와 weight로 정의해 food type별 volumetric bite가 일관되지 않는다. 특히 mashed potatoes는 같은 target weight에서도 큰 heap을 만들 수 있다. Simulation은 discrete particles만 model하여 soft/deformable foods의 physics를 충분히 표현하지 못한다. [§VI, pp.6–7]

## 14. Author-stated Future Work

Depth-based volumetric reconstruction 또는 density-aware estimation으로 bite-size validation을 표준화하고, deformable-food physics를 simulator에 포함해 soft foods의 strategy와 sim-to-real transfer를 개선할 것을 제안한다. [§VI, p.7]

## 15. Review-relevant Findings

- Real execution은 spoon-mounted 6-axis F/T의 5-step history와 tracked spoon/food masks를 함께 사용한다.
- Numeric food position은 RGB-D로 episode initial DMP start에만 사용하고 current pose vector를 지속 제공하지 않는다.
- Food texture/particle physical parameters는 actor에 주지 않고 F/T와 visual mask로 간접 적응한다.
- F/T는 global interaction history를 제공하지만 contact location이나 distributed contact를 복원하지 않는다.
- Modality ablation은 force-only나 segmentation-only보다 combined input의 real performance가 높음을 보인다.
- Reward는 simulator actual scooped amount GT를 사용하고 particle properties는 training randomization에만 있다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| State / history / action / reward | §III-A pp.3–4 |
| Training randomization / controller | §IV-A–B pp.3–4 |
| Simulation ablations | §IV-D–E/Tables II–III pp.4–5 |
| Real sensor / initial pose / masks | §V-A p.5 |
| Real modality evidence | §V-C/Tables IV–V p.6 |
| Limitation / Future | §VI pp.6–7 |
