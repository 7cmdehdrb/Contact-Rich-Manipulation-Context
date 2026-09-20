# MAT: Multi-Fingered Adaptive Tactile Grasping via Deep Reinforcement Learning

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md) · [정식 상세 노트](../../../../papers/2019-wu-mat-adaptive-tactile-grasping.md)

분석 ID: `B086`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Bohan Wu; Iretiayo Akinola; Jacob Varley; Peter K. Allen
- Year: 2019
- Venue: Conference on Robot Learning (CoRL 2019)
- DOI / arXiv: Not stated / 1909.04787v2
- PDF version: arXiv v2 (10 October 2019; CoRL 2019 paper with appendix)
- Page count: 20
- SHA-256: `e73a3bfccf9ed4491e98f206e05b0bda76f007b04a4a7148bde9ea140c534a2e`
- PDF filename: Wu 등 - 2019 - MAT Multi-Fingered Adaptive Tactile Grasping via Deep Reinforcement Learning.pdf
- 확인 범위: PDF pp.1–20 전체(본문, conclusion, Appendix A–D); observation/action/reward, ablation, real-robot results, limitations-relevant discussion을 확인하고 Figures 2/5 및 Tables 1–4 렌더 검토.

## 2. Relevance to This Review

`Relevant`

초기 vision grasp 이후 실행 vision 없이 binary tactile, tactile-cell 위치, finger proprioception과 20-step history로 grasp를 수정한다. Binary 변환이 연속 force magnitude를 제거한 뒤 어떤 spatial/temporal 정보를 남기며 current object pose 부재를 어떻게 보완하는지, 그리고 simulator reward·termination과 runtime observation을 어떻게 분리하는지 직접 분석할 수 있다.

## 3. Task

외부 vision 시스템이 제안한 coarse grasp pose에서 Barrett hand를 접근시킨 뒤 vision을 끄고, 촉각 접촉에 따라 손가락을 닫거나 다시 열고 손목을 재정렬하여 물체를 파지한다. 마지막에 물체를 25 cm 들어 올려 성공 여부를 판정하며, position/orientation calibration error가 있는 초기 grasp에서도 적응하는 것이 목표다. [§III-A/§IV, PDF pp.3,6–8]

## 4. Method

### 4.1. Overall Pipeline

96개 tactile cell의 연속 force → 최근 50 samples running mean → 0.8 threshold binary contact → forward kinematics로 active cell의 end-effector-frame Cartesian position 계산 → binary contact·cell position·8 finger joint angle의 20-step history와 temporal differences → shared tactile/finger encoders와 policy network → finger별 close/reopen 또는 lift decision; reopen이면 learned wrist roll과 rule-based XY translation으로 재접근한다. [§III-B–D, pp.3–6; Appendix A.1, p.11; Appendix D, p.19]

### 4.2. Observation

정책은 tactile state 20×96과 19-step difference, 8 finger joint angles 20×8과 thresholded difference, 96 tactile-cell Cartesian positions 20×96×3과 differences를 받는다. 입력은 현재 물체 pose, shape, force magnitude 또는 vision image를 포함하지 않는다. [§III-B–C, pp.3–4]

### 4.3. Action

각 time step에 각 finger를 닫는 binary action, 모든 finger를 다시 여는 regrasp action, 또는 lift action을 선택한다. Regrasp 시 정책은 wrist roll angle을 출력하고 XY translation은 최근 active tactile-cell 위치의 평균을 향하도록 규칙으로 계산한다. [§III-D, pp.4–5; Appendix A.1, p.11]

### 4.4. Controller

Finger-close action은 joint-space position command로 손가락을 정해진 increment만큼 닫고, reopen은 손을 열고 Cartesian wrist translation/roll을 수행한 뒤 다시 닫는다. Lift action은 현재 grasp를 유지하며 end effector를 25 cm 들어 올린다. 구체적인 low-level servo gain은 원문에서 확인되지 않는다. [§III-D/§IV-B, pp.4–6]

### 4.5. Learning / Optimization Method

PyBullet에서 sparse terminal pickup reward와 reopen penalty로 SoftPPO를 학습한다. 초기 grasp noise와 물체를 randomize하고, 학습 초기에 finger-closing magnitude를 크게 두었다가 줄이는 curriculum을 사용한다. Policy와 value function을 함께 학습하지만 value network에 object-state privileged observation을 넣는 asymmetric 구조는 원문에 명시되지 않는다. [§III-E/§IV-A, pp.5–6; Appendix B–C, pp.14–18]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Initial | 외부 vision이 계산한 grasp pose로 hand를 물체 근처에 배치 | No | Initial grasp translation에 calibration noise를 주지만 실행 중 current object position은 관측하지 않는다. [§III–V and Appendix, PDF pp.3–14,18–20] |
| Orientation | Initial | 외부 vision의 initial grasp orientation | No | 실행 중 object orientation을 추적하지 않으며 safety 때문에 regrasp는 wrist roll만 학습하고 pitch/yaw는 조절하지 않는다. [§III-A/D pp.3–5; Appendix A.1 p.11] |
| Shape / Geometry | 미제공 | 정책에 mesh/CAD/point cloud/dimension/category를 제공하지 않음 | 해당 없음 | Training/test objects는 다양하지만 object identity나 geometry vector는 observation이 아니다. [§IV-A/E pp.5,8] |
| Physical Parameters | 미제공 | 정책에 mass/friction/compliance를 제공하지 않음 | 해당 없음 | Simulation에서 physical parameters를 randomize하지만 actor input은 아니다. [§IV-A p.5; Appendix B p.14] |

## 6. Missing Object Information and Compensation

Current object position/orientation/shape 미제공 → binary tactile contact pattern + active-cell Cartesian locations + finger joint history → 어떤 손가락/부위가 접촉했는지와 시간에 따른 접촉 변화를 이용해 close/reopen/lift를 선택한다.

Binary threshold가 연속 tactile force magnitude를 제거 → cell identity/location과 20-step history를 별도 보존 → contact locality와 변화 방향을 정책에 제공한다. 저자들은 sparse touch가 object pose를 충분히 정하지 못한다고 명시하며, 안전을 위해 full 6-DoF reorientation 대신 XY translation과 wrist roll로 action space를 제한한다. [§III-B–D pp.3–5; Appendix A.1 p.11]

## 7. Tactile

### 7.1. Raw Sensor

Barrett BH-282 hand의 세 fingers와 palm에 총 96 capacitive tactile cells(각 finger 24, palm 24)가 있으며, 실물에서는 약 246 Hz로 0–20 범위의 force-like scalar를 출력한다. [§III-B p.3; Appendix D p.19]

### 7.2. Preprocessing

실물 raw reading은 cell별 최근 50 samples의 running mean을 계산하고 0.8 threshold로 binary contact로 바꾼다. Joint encoders와 forward kinematics로 각 cell의 end-effector-frame Cartesian position을 계산하며, 20-step histories와 adjacent-frame differences를 만든다. [§III-B–C pp.3–4; Appendix D p.19]

### 7.3. Policy Representation

20×96 binary tactile map과 19×96 difference, 20×96×3 cell-position sequence와 differences를 finger-joint histories와 함께 policy에 넣는다. Image encoder가 아니라 finger/palm group별 fully connected encoders로 처리한다. [§III-C/F, pp.4–5]

### 7.4. Retained Information

Contact presence, cell identity에 따른 local contact location/pattern, kinematics로 변환한 spatial position, 20-step temporal persistence와 transitions를 보존한다. [§III-B–C, pp.3–4]

### 7.5. Removed / Unavailable Information

Threshold 이후 continuous force magnitude와 magnitude 변화는 사라진다. Sensor는 shear vector, local deformation image, contact normal/pose 또는 full pressure distribution을 제공하지 않는다. Binary contacts만으로 exact object pose는 정해지지 않는다고 저자가 설명한다. [§III-B p.3; Appendix A.1 p.11]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Wrist F/T는 사용하지 않는다. Capacitive tactile cell의 local scalar force-like output만 threshold 전에 존재한다. [§III-B, p.3]

### 8.2. Representation

정책에는 force magnitude가 아니라 thresholded binary contact만 들어간다. 별도의 $F_x,F_y,F_z,M_x,M_y,M_z$ 또는 estimated wrench는 없다. [§III-B–C, pp.3–4]

### 8.3. Role

Raw tactile force는 contact/no-contact 판정을 만드는 데만 쓰이며, 정책은 binary contact pattern과 위치/history로 grasp state를 조절한다. [§III-B–D, pp.3–5]

### 8.4. Required Assumptions

Cell별 threshold와 running-mean calibration, known hand kinematics와 sensor placement, 물체가 hand workspace 안에 있다는 coarse initial grasp가 필요하다. [§III-A–C pp.3–4; Appendix D p.19]

### 8.5. Reported Limitation / Ambiguity

Binary contacts는 force 크기와 object pose를 충분히 제공하지 않는다. Wrist wrench 기반 contact localization이나 multi-contact force separation은 원문에서 다루지 않는다. [Appendix A.1 p.11]

## 9. Other Observations

Proprioception은 8 finger joint angles와 thresholded temporal differences이다. Tactile-cell Cartesian positions도 joint kinematics에서 계산한다. Sensor history는 20 steps이며 previous action을 별도 observation으로 제공한다고 명시하지 않는다. 외부 vision은 episode 초 initial grasp pose를 만드는 데만 사용하고 tactile policy 실행 중에는 사용하지 않는다. [§III-A–C, pp.3–4]

## 10. Tactile–Other Modality Relationship

Binary tactile는 어디에 접촉했는지를, finger joint state는 hand configuration을, 20-step history는 접촉이 형성·소실되는 과정을 제공한다. Cell Cartesian positions는 cell identity를 kinematic workspace location으로 바꾸어 rule-based XY regrasp에도 직접 사용한다. F/T는 병용하지 않는다. Component ablations는 regrasp/translation/orientation/finger-closing 기능의 효과를 검증하지만, tactile magnitude와 binary를 직접 비교하지는 않는다. [§III-C–D pp.4–5; Tables 1–2, pp.7,12]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | Binary tactile/cell positions and histories; finger joint states | Current object GT pose/shape는 actor 입력이 아니다. [§III-B–C, pp.3–4] |
| Critic | No | Policy observation 기반 value network | Asymmetric critic 또는 object GT input은 원문에서 확인되지 않는다. [§III-E/F, p.5] |
| Reward | Yes | Simulation pickup success after commanded lift; reopen penalty | Pickup 성공은 simulator의 object displacement/state로 판단하며 실물 실행 sensor 입력과 구분된다. [§III-E, p.5] |
| Termination | Yes | Lift/pickup outcome and episode action limit | Simulation과 evaluation에서 25 cm lift 성공 여부로 종료/성공을 판정한다. [§III-E/§IV-B, pp.5–6] |
| Curriculum | Yes | Finger closing action magnitude schedule; randomized grasp noise/objects | 학습용 curriculum과 simulation sampling이며 실행 observation에는 없다. [§III-E/§IV-A, pp.5–6] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Adaptive tactile policy가 fixed vision grasp보다 calibration error에 강함 | Controlled comparison | MAT vs tactile baseline and open-loop vision baseline under translation/rotation noise | Simulation에서 noise가 커져도 MAT가 높은 pickup success를 유지하며, 실물 5 cm calibration error에서 MAT는 약 92%이고 vision baseline은 약 20–26%다. | §IV-C–E; PDF pp.6–8 ; Table 1; Table 3 |
| Adaptive action components가 성능에 기여 | Input/action ablation | Full MAT vs no finger-closing adaptation/no regrasp/no position/no orientation variants | Table 1과 Appendix Table 2에서 full method가 대부분의 noise 조건에서 component-removed variants보다 높다. | §IV-D; Appendix A.4; PDF pp.7,12 ; Table 1; Table 2 |
| Binary tactile와 proprioceptive history로 real grasps를 수정 가능 | Controlled real-robot comparison | MAT vs tactile heuristic baseline vs vision-only baseline across two calibration errors | MAT는 two real object sets에서 약 92% pickup success를 보고하고 baselines보다 높다. | §IV-E; Appendix C; PDF pp.8,13–14 ; Tables 3–4 |
| Tactile representation 자체의 magnitude 필요성 | No supporting evidence | Continuous tactile magnitude vs binary tactile | 논문은 thresholded binary representation만 사용하며 continuous-magnitude representation ablation은 제시하지 않는다. | §III-B; §IV; PDF pp.3,6–8 |

## 13. Author-stated Limitations

독립된 Limitations 절은 없다. 원문은 sparse touch가 object pose를 충분히 알려주지 않으며 pitch/yaw regrasp를 허용하면 unsafe grasp가 될 수 있어 roll만 조절한다고 설명한다. Binary threshold는 force magnitude를 버리고, 실물 평가 sample 수가 작아 standard deviation이 크다고 Appendix에서 밝힌다. [Appendix A.1/A.4, pp.11–14]

## 14. Author-stated Future Work

결론은 제안한 tactile grasp adaptation을 더 일반적인 dexterous tactile object manipulation으로 확장하겠다고 명시한다. 세부 sensor 또는 task 계획은 원문에서 더 제시되지 않는다. [§V, p.8]

## 15. Review-relevant Findings

- Initial grasp pose는 외부 vision에서 오지만 policy 실행 중 current object pose/shape는 제공되지 않는다.
- 96-cell continuous tactile reading은 running mean 뒤 binary로 threshold되어 force magnitude가 제거된다.
- Cell location, finger joint angles, temporal differences를 포함한 20-step history가 binary contact의 부족한 spatial/temporal 정보를 보완한다.
- Wrist F/T 또는 global wrench는 사용하지 않는다.
- Actor에는 object GT가 없지만 simulation reward와 termination은 lift/pickup state를 사용한다.
- Ablation은 adaptive action components의 효용을 보이지만 continuous tactile와 binary tactile를 직접 비교하지 않는다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Task / initial vision condition | §III-A p.3 |
| Observation / tactile processing | §III-B–C pp.3–4; Appendix D p.19 |
| Action / controller | §III-D pp.4–5; Appendix A.1 p.11 |
| Reward / curriculum | §III-E p.5 |
| Actor/value architecture | §III-F pp.5–6 |
| Ablation / simulation | §IV-C–D pp.6–7; Appendix A.4 p.12 |
| Real results | §IV-E p.8; Appendix C pp.13–14 |
| Limitation / Future | Appendix A.1/A.4 pp.11–14; §V p.8 |
