# CONTACT: CONtact-aware TACTile Learning for Robotic Disassembly

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B071`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Yosuke Saka; Jyun-Chi Hu; Adeesh Desai; Zhiyuan Zhang; Bihao Zhang; Quan Khanh Luu; Md Rakibul Islam Prince; Minghui Zheng; Yu She
- Year: 2026
- Venue: arXiv preprint
- DOI / arXiv: Not stated / 2603.08560v2
- PDF version: arXiv v2 (21 July 2026)
- Page count: 8
- SHA-256: `d43d42529de365d00b9b2f5d1f80a524945461b4044184700bce27a4bd83d00d`
- PDF filename: Saka 등 - 2026 - CONTACT CONtact-aware TACTile Learning for Robotic Disassembly.pdf
- 확인 범위: PDF pp.1–8 전체; Tables I–V와 Figures 3–6 렌더 확인.

## 2. Relevance to This Review

`Relevant`

Vision-only, Vision+raw tactile RGB, Vision+structured tactile force field를 동일 diffusion-policy 조건에서 직접 비교한다. Tactile이 vision의 접촉 ambiguity를 어떤 spatial force 정보로 보완하는지와 naive sensor fusion이 항상 유리하지 않다는 근거를 rigid/deformable disassembly에서 제공한다.

## 3. Task

Rigid/deformable components를 pulling, sliding, pinching으로 분리한다. Simulation S1–S5와 real R1–R5는 loose/tight extraction, lid, barb, deformable tab/clip을 포함하며 성공은 target component가 완전히 추출되어 height threshold를 넘는 것이다. [§II-A/§III-A, pp.3,5]

## 4. Method

### 4.1. Overall Pipeline

Front RGB + wrist RGB + EEF pose + optional GelSight TacRGB/TacFF의 two-step history → modality별 ResNet-18 → feature concatenate → 1D U-Net diffusion model → DDIM action chunk(16-step horizon, 첫 8개 실행) → relative translation/yaw/gripper commands. [§II-B–C/Fig.5, pp.3–5]

### 4.2. Observation

매 control step에 front/wrist RGB, EEF 3D position+quaternion, optional TacRGB 또는 TacFF를 10 Hz로 받으며 $t-1,t$ 두 frame history를 사용한다. 정책은 Vision Only, Vision+TacRGB, Vision+TacFF로 따로 학습된다. [§II-B–C/§III-A, pp.3–5]

### 4.3. Action

5D relative command: $\Delta x,\Delta y,\Delta z$, world z-axis yaw increment $\Delta\theta_z$, gripper command. Diffusion horizon 16 중 첫 8 actions를 실행한다. [§II-C, p.5]

### 4.4. Controller

High-level diffusion policy가 relative Cartesian/gripper commands를 출력한다. Robot의 low-level controller type/gains는 원문에서 확인되지 않음. [§II-C/§III-A, p.5]

### 4.5. Learning / Optimization Method

Teleoperation demonstrations로 supervised imitation learning하는 Diffusion Policy다. Modality configuration별 동일 data/protocol로 400 epochs 학습하고 DDIM 10 denoising steps를 사용한다. RL actor/critic/reward는 없다. [§II-C/§III-A, pp.4–5]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Front/wrist RGB에 current object appearance가 implicit하게 포함 | 매 10 Hz 갱신 | Numeric current object position/pose vector는 policy input이 아니다. [§II–III, PDF pp.3–7] |
| Orientation | 기타 | Front/wrist RGB의 implicit visual orientation | 매 10 Hz 갱신 | Current orientation을 별도 수치로 제공하지 않는다. [§II–III, PDF pp.3–7] |
| Shape / Geometry | 기타 | Raw RGB/tactile appearance의 implicit geometry | 매 frame 갱신되나 static shape 정보 | Mesh/CAD/dimension/category ID는 policy input이 아니다. [§II-B–C pp.3–5] |
| Physical Parameters | 미제공 | Friction/compliance/material parameter vector 없음 | 해당 없음 | Deformability와 resistance는 sensor response에서만 나타난다. [§II-A–B pp.3–4] |

## 6. Missing Object Information and Compensation

Numeric current object pose/shape/physical parameters 미제공 → front/wrist vision + EEF pose + two-step history → global/local geometry와 motion을 implicit하게 인코딩한다.

Vision으로 보이지 않는 grasp quality/contact transition → TacRGB의 local deformation 또는 TacFF의 distributed normal/shear → centered/corner grasp, sliding/pulling resistance, deformable release를 구별한다. TacFF의 이 역할은 vision-only/TacRGB와 동일 조건 비교로 직접 검증된다. [Figs.3–4 pp.3–4; Tables I–II p.6]

## 7. Tactile

### 7.1. Raw Sensor

실물은 right fingertip의 GelSight R1.5 optical tactile sensor. TacRGB는 240×160 RGB deformation image이며, simulation은 TacSL로 real sensing setup을 mirror한다. [§II-B/§III-A, pp.3,5]

### 7.2. Preprocessing

TacRGB에서 optical flow와 depth reconstruction으로 force field를 계산한다. 모든 modalities를 10 Hz 동기화하고 [-1,1] normalize하며 ResNet-18로 encode한다. [§II-B/§III-A, pp.3,5]

### 7.3. Policy Representation

TacRGB: high-resolution surface deformation image. TacFF: 10×14 grid의 3-channel distributed shear-x, shear-y, normal force field; arrow direction/length은 shear, color는 normal force다. [§II-B/Fig.3, pp.3–4; §III-A p.5]

### 7.4. Retained Information

TacRGB는 local indentation/deformation pattern, TacFF는 spatially distributed normal/shear magnitude와 direction 및 contact redistribution을 남긴다. Two-step history가 transition 단서를 제공한다. [§II-B, pp.3–4]

### 7.5. Removed / Unavailable Information

TacFF는 raw optical appearance를 compact 10×14 force grid로 축약한다. Calibrated wrist wrench, full object pose/shape, long contact history는 포함하지 않는다. 원문은 TacFF를 compact/structured force cue로 설명하나 정량적인 information-loss 측정은 하지 않는다. [§II-B/§III-B–D, pp.3–7]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

GelSight optical tactile reconstruction의 local distributed force field이다. Wrist 6-axis F/T가 아니다. [§II-B/§III-A, pp.3,5]

### 8.2. Representation

10×14 grid에 shear-x, shear-y, normal components. [§II-B/§III-A, pp.3,5]

### 8.3. Role

Contact state transition, grasp centering, directional resistance/sliding, deformable release를 policy observation으로 제공한다. [§II-B/§III-B–D, pp.3–7]

### 8.4. Required Assumptions

Optical-flow/depth reconstruction이 local shear/normal field를 안정적으로 제공하고, GelSight가 right fingertip contact를 포착해야 한다. [§II-B/§III-A, pp.3,5]

### 8.5. Reported Limitation / Ambiguity

단순한 TacRGB+TacFF feature concatenation은 성능을 낮췄다. 저자들은 observation dimensionality와 heterogeneous signals가 task-relevant cue를 희석할 수 있다고 설명한다. [§III-D/Table V, p.7]

## 9. Other Observations

Front camera는 global context, wrist camera는 local gripper view, EEF 7D pose는 robot state를 제공한다. Two-step history를 feature dimension에 concatenate한다. Previous action, recurrent hidden state, explicit state estimator는 사용하지 않는다. [§II-B–C, pp.3–5]

## 10. Tactile–Other Modality Relationship

Vision은 global geometry/scene와 local approach를, tactile은 occluded contact quality와 normal/shear redistribution을 제공한다. TacFF는 TacRGB보다 contact-dominated tasks에서 일관되게 강했다. 그러나 TacRGB+TacFF naive fusion은 두 modality 단독보다 나빠 sensor 병용 자체가 상보성 증명이 아님을 보인다. [Tables I–V, pp.6–7]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | Supervised imitation learning. Demonstration action과 simulation success labels는 학습/evaluation 자료이며 RL privileged actor/critic/reward/curriculum은 해당 없음. [§II-C/§III-A, pp.4–5] |
| Critic | Not applicable | 비-RL | Supervised imitation learning. Demonstration action과 simulation success labels는 학습/evaluation 자료이며 RL privileged actor/critic/reward/curriculum은 해당 없음. [§II-C/§III-A, pp.4–5] |
| Reward | Not applicable | 비-RL | Supervised imitation learning. Demonstration action과 simulation success labels는 학습/evaluation 자료이며 RL privileged actor/critic/reward/curriculum은 해당 없음. [§II-C/§III-A, pp.4–5] |
| Termination | Not applicable | 비-RL | Supervised imitation learning. Demonstration action과 simulation success labels는 학습/evaluation 자료이며 RL privileged actor/critic/reward/curriculum은 해당 없음. [§II-C/§III-A, pp.4–5] |
| Curriculum | Not applicable | 비-RL | Supervised imitation learning. Demonstration action과 simulation success labels는 학습/evaluation 자료이며 RL privileged actor/critic/reward/curriculum은 해당 없음. [§II-C/§III-A, pp.4–5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| TacFF가 vision-only를 보완 | Sensor combination ablation | Vision Only vs Vision+TacRGB vs Vision+TacFF, 동일 policy/data | Simulation 모든 5 tasks에서 TacFF 최고; S2 36.9→44.3%. Real 모든 5 tasks에서 TacFF 최고; R5 15→55%. | §III-B–C; PDF p.6 ; Tables I–II |
| Structured force가 raw deformation보다 contact task에 적합 | Representation ablation | TacRGB vs TacFF | R2/R3/R4에서 TacRGB 30/15/5%, TacFF 70/45/75%; TacRGB는 task-irrelevant variability 가능성을 저자가 설명. | §III-B–C; PDF p.6 ; Table II |
| Tactile은 visual degradation에서 task-dependent stabilizer | Sensor ablation | Normal vs dim lighting, R1/R5 | R5 Vision Only 15→0%, TacFF 55→55%; R1은 모든 modality가 저하. | §III-D.1; PDF p.7 ; Table IV |
| Naive tactile fusion은 상보성을 보장하지 않음 | Sensor combination ablation | Vision+TacRGB+TacFF vs individual tactile configurations | R3 combined 0%, R5 combined 20%, 각각 TacFF 45/55%보다 낮다. | §III-D.2; PDF p.7 ; Table V |

## 13. Author-stated Limitations

독립된 Limitations 절은 없고 저자가 명시적으로 열거한 일반화 한계도 없다. 실험 결과에서 naive TacRGB+TacFF concatenation이 task-relevant force 정보를 희석하고 성능을 떨어뜨리는 한계를 직접 보고한다. [§III-D.2/§IV, p.7]

## 14. Author-stated Future Work

Heterogeneous tactile streams를 통합하려면 modality-aware attention이나 stream별 dedicated encoder 같은 structured fusion이 필요하다고 제안한다. [§III-D.2, p.7]

## 15. Review-relevant Findings

- Numeric current object pose/shape 대신 cameras, EEF pose, two-frame history를 사용한다.
- TacFF는 local distributed shear와 normal force를 남긴다.
- Contact-dominated/deformable tasks에서 TacFF가 vision-only와 TacRGB보다 일관되게 높았다.
- Geometry-dominant task에서는 tactile gain이 작거나 lighting 저하를 완전히 보완하지 못했다.
- TacRGB+TacFF의 단순 병합은 성능을 오히려 낮췄다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / tactile | §II-B–C pp.3–5 |
| Object information | §II-B–C pp.3–5 |
| Action / learning | §II-C/§III-A p.5 |
| F/T | Wrist F/T 없음; §II-B |
| Simulation evidence | Table I p.6 |
| Real evidence | Tables II–V pp.6–7 |
| Limitation / Future | §III-D.2/§IV p.7 |
| Privileged information | 비-RL; §II-C |
