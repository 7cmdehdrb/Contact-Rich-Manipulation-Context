# Disambiguate Gripper State in Grasp-Based Tasks: Pseudo-Tactile as Feedback Enables Pure Simulation Learning

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B090`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Yifei Yang; Lu Chen; Zherui Song; Yenan Chen; Wentao Sun; Zhongxiang Zhou; Rong Xiong; Yue Wang
- Year: 2025
- Venue: 2025 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)
- DOI / arXiv: 10.1109/IROS60139.2025.11246513 / Not stated
- PDF version: IEEE publisher version
- Page count: 8
- SHA-256: `1cfd60398be38d346147936354116d017f7fafdc026c6df0e917debdd1e49393`
- PDF filename: Yang 등 - 2025 - Disambiguate Gripper State in Grasp-Based Tasks Pseudo-Tactile as Feedback Enables Pure Simulation.pdf
- 확인 범위: PDF pp.1–8 전체; pseudo-tactile controller, privileged demonstration generation, admittance control, observation/action, three task results, ablations and conclusion을 확인하고 Figures 2–4와 Tables I–IV 렌더 검토.

## 2. Relevance to This Review

`Relevant`

Force-controlled gripper의 equilibrium joint angle을 pseudo-tactile로 사용하여 ambiguous closed command를 reliable binary grasp-state feedback으로 바꾸고, 이 축약 정보가 vision-only policy의 부족분을 어떻게 보완하는지 직접 실험한다. Privileged object pose 기반 simulation expert와 runtime RGB/binary state를 분리하며 pseudo-tactile ablation을 제공한다.

## 3. Task

UR5+Robotiq 2F-85가 pick-and-lift, drawer opening, oven opening을 수행한다. Grasp 전에 gripper를 강제로 닫는 disturbance가 발생해도 empty-close를 grasp-close로 오인하지 않고 다시 열어 regrasp한 뒤 task를 완료하는 것이 목표다. [§I/§V, PDF pp.1–2,6–8]

## 4. Method

### 4.1. Overall Pipeline

Pure simulation에서 privileged object poses로 object-centric end-effector target poses와 trajectories를 계산하고 successful rollouts만 Diffusion Policy demonstrations로 저장 → runtime actor는 third-person RGB + EEF 6-DoF pose + corrected binary gripper state → EEF pose/binary gripper action. Low-level pseudo-tactile controller는 force equilibrium의 continuous gripper joint angle을 읽어 empty-close이면 high-level close command를 override해 reopen하고, articulated tasks에서는 admittance controller가 external F/T에 따라 pose를 보정한다. [§III-A–C, pp.3–5]

### 4.2. Observation

Policy input은 320×240 third-view RGB, end-effector 6-DoF pose, binary gripper state다. Continuous joint angle은 policy input이 아니며 low-level pseudo-tactile controller만 사용한다. Corrected binary state 1은 object를 실제로 grasp한 closed state를 뜻한다. Numeric object current pose는 privileged expert/data generation에만 사용한다. [§III-A/C, pp.3–5]

### 4.3. Action

Diffusion Policy가 end-effector 6-DoF target pose와 binary gripper command를 출력한다. Low-level gripper controller는 pseudo-tactile이 empty-close를 검출하면 close를 reopen으로 override할 수 있다. [§III-A/C, pp.3–5]

### 4.4. Controller

Robotiq force-controlled gripper의 joint angle at force equilibrium을 rule-based feedback으로 사용한다. Drawer/oven에서는 Cartesian admittance의 mass–damper–spring equation을 적용해 external wrench에 따라 policy pose를 보정한다. External force/torque sensor source는 원문에서 명시되지 않는다. [§III-A–C, pp.3–5]

### 4.5. Learning / Optimization Method

DDIM noise scheduler의 Diffusion Policy를 privileged simulation expert demonstrations로 supervised imitation learning한다. Expert는 simulator object poses에서 key poses를 계산하고 task-specific post-grasp motion rules를 실행하며, object pose/joint angle로 성공 rollouts만 선별한다. Object/robot pose, lighting, texture를 randomize하며 각 task 2,000 demonstrations를 사용한다. [§III-B–C/§V-A, pp.4–6]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Runtime RGB에 implicit; numeric pose는 policy에 미제공 | Yes | Simulation expert/data generation은 GT object pose를 사용하나 runtime actor와 구분한다. [§III-B–C pp.4–5] |
| Orientation | 기타 | Runtime RGB에 implicit; numeric orientation 미제공 | Yes | Oven-door pose는 expert trajectory generation에 사용된다. [§III-B pp.4–5] |
| Shape / Geometry | 기타 | RGB appearance에 implicit; simulation assets contain geometry | Yes | Mesh/CAD/category/dimension을 runtime vector로 제공하지 않는다. [§III-B–C pp.4–5] |
| Physical Parameters | 미제공 | Runtime policy에 mass/friction/joint parameters를 제공하지 않음 | 해당 없음 | Simulation assets/physics는 training environment에만 있다. [§III-B–C pp.4–5] |

## 6. Missing Object Information and Compensation

Gripper command state만으로 grasp success/empty close 구분 불가 → force-equilibrium gripper joint angle pseudo-tactile → low-level controller가 empty-close를 reopen으로 바꾸고 policy에는 reliable binary grasp state를 제공한다.

Runtime numeric object pose 미제공 → RGB + EEF pose + binary grasp state → grasp 전/후 phase를 구분하고 task trajectory를 생성한다. Training data 생성에서는 GT object pose와 joint angle을 사용하는 privileged expert가 이 부족분을 대신하지만 실행 actor에는 들어가지 않는다. [§III-A–C, pp.3–5]

## 7. Tactile

### 7.1. Raw Sensor

별도 tactile hardware는 없다. Robotiq 2F-85 force-controlled gripper가 object와 force equilibrium에 도달했을 때의 continuous gripper joint angle을 pseudo-tactile signal로 사용한다. [§III-A, pp.3–4]

### 7.2. Preprocessing

Rule-based controller가 closed command와 equilibrium joint angle을 검사한다. Joint angle이 maximum까지 닫혀 object가 없음을 나타내면 close command를 override하여 gripper를 reopen한다. [§III-A/Fig.2, pp.3–4]

### 7.3. Policy Representation

Policy에는 continuous joint angle이 아니라 noise-free corrected binary gripper state만 들어간다: 1은 successful grasp-close, 0은 empty-open. [§III-A–C, pp.3–5]

### 7.4. Retained Information

Object containment/contact의 binary grasp success, 즉 grasp-close와 empty state의 구분을 남긴다. [§III-A, pp.3–4]

### 7.5. Removed / Unavailable Information

Force magnitude/direction, contact location/patch, pressure/shear, object pose, continuous finger deformation 정도는 policy representation에 없다. Continuous joint angle 자체도 actor input에서 제거된다. [§III-A/C, pp.3–5]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Pseudo-tactile는 force-controlled gripper의 joint angle이며 wrist F/T가 아니다. Articulated tasks의 admittance control은 external force/torque $F_{ext}$를 사용하지만 sensor hardware/source는 원문에서 명시되지 않는다. [§III-A–C, pp.3–5]

### 8.2. Representation

Pseudo-tactile controller에는 equilibrium gripper joint angle; policy에는 corrected binary gripper state. Admittance controller에는 external force/torque vector가 들어가지만 정확한 component/frame/filtering은 미명시다. [§III-A–C, pp.3–5]

### 8.3. Role

Gripper pseudo-tactile는 grasp-state disambiguation과 automatic retry에, external F/T는 articulated-object kinematic mismatch를 흡수하는 low-level compliance에 사용된다. 둘 다 actor neural observation의 continuous force channel은 아니다. [§III-A–C, pp.3–5]

### 8.4. Required Assumptions

Force-controlled parallel gripper, empty close에서 maximum joint angle까지 닫힘, object grasp 시 다른 equilibrium angle, manually designed rule/threshold가 필요하다. Admittance는 calibrated external wrench와 stable gains를 가정한다. [§III-A–C, pp.3–5]

### 8.5. Reported Limitation / Ambiguity

Pseudo-tactile binary state는 grasp presence만 구분하고 contact locality나 load를 제공하지 않는다. External F/T의 source와 contact ambiguity는 원문에서 논의하지 않는다. [§III-A–C, pp.3–5]

## 9. Other Observations

Vision은 third-person RealSense D435i RGB, proprioception은 EEF 6-DoF pose, goal/task context는 demonstration distribution에 포함된다. Previous action, sensor history, recurrent hidden state, explicit runtime object estimator는 명시되지 않는다. Low-level admittance output과 pseudo-tactile correction을 actor observation과 분리해야 한다. [§III-C/§V-A, pp.5–6]

## 10. Tactile–Other Modality Relationship

RGB는 object/handle scene와 approach context를, EEF pose는 robot configuration을, pseudo-tactile binary state는 vision으로 불확실한 actual grasp success를 제공한다. External F/T는 drawer/oven interaction에서 policy pose를 compliant하게 보정하지만 pseudo-tactile와 함께 actor에 fusion되는 modality가 아니다. Table IV는 pseudo-tactile on/off를 직접 비교해 binary feedback의 필요성을 검증한다. [§III-C p.5; §V-C pp.7–8]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | RGB; EEF 6-DoF pose; corrected binary gripper state | Runtime actor는 object GT pose나 continuous gripper joint angle을 받지 않는다. [§III-C, p.5] |
| Critic | Not applicable | 비-RL imitation learning | Actor–critic/critic이 없다. [§III-C, p.5] |
| Reward | Not applicable | 비-RL imitation learning | Learned policy reward가 없다. [§III-B–C, pp.4–5] |
| Termination | Yes | GT object pose or joint angle monitors expert rollout completion; successful rollout filtering | Training demonstration generation에만 사용되며 real actor input이 아니다. [§III-B, p.4] |
| Curriculum | Yes | Privileged object poses for key targets; object/robot pose, lighting, texture randomization; automated successful demonstrations | Training/data-generation-only simulator information. [§III-B, pp.4–5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Pseudo-tactile disambiguation improves task robustness | Sensor/controller ablation | Diffusion Policy simulation data with vs without pseudo-tactile feedback | Oven opening: success 30% without vs 80% with pseudo-tactile; disturbance resilience 30% vs 100%. | §V-C; PDF p.7 ; Table IV |
| Adding ambiguous empty-grasp data does not replace reliable feedback | Controlled comparison / Failure analysis | Gripper-randomized simulation data without pseudo-tactile vs proposed feedback | Randomized-data DP has 100% recovery but 0% task success; rollout repeatedly opens/closes because vision cannot identify grasp success. | §V-C; PDF pp.7–8 ; Table IV ; Fig.4(b) |
| Policy architecture alone does not resolve ambiguous grasp state | Architecture ablation | DP, ACT, and RDT-1B trained with gripper-randomized simulation data, no pseudo-tactile | Task success remains 0%, 40%, and 0%, respectively, while proposed DP with feedback reaches 80%. | §V-C; PDF pp.7–8 ; Table IV |
| Pure-simulation method transfers to three real tasks | Controlled comparison | Proposed method vs real-teleoperation DP/ACT/RDT-1B baselines | Proposed overall task success is 90% pick-and-lift, 90% drawer, 80% oven and 100% disturbance resilience for all tasks. | §V-B; PDF pp.6–7 ; Tables I–III |

## 13. Author-stated Limitations

독립된 Limitations 절은 없다. 원문이 드러내는 적용 조건은 force-controlled gripper의 equilibrium joint angle로 empty-close와 grasp-close를 구분할 수 있어야 하고, manually designed low-level rule이 필요하다는 점이다. Binary state는 grasp presence 외 force magnitude/location을 제공하지 않으며, 세 tasks와 한 gripper에서만 검증했다. 이는 원문 구성과 실험 범위에서 확인되는 조건이며 별도 저자 limitation 주장으로 확대하지 않는다. [§III-A/§V, pp.3–8]

## 14. Author-stated Future Work

Conclusion에는 구체적인 future-work 항목이 명시되지 않는다. [§VI, p.8]

## 15. Review-relevant Findings

- Pseudo-tactile raw signal은 force-controlled gripper의 equilibrium joint angle이며 별도 tactile sensor가 아니다.
- Actor에는 corrected binary grasp state만 들어가고 continuous joint angle, force magnitude, contact location은 들어가지 않는다.
- RGB와 EEF pose가 scene/robot state를 제공하고 binary pseudo-tactile가 vision으로 애매한 grasp success를 보완한다.
- Training expert는 GT object pose와 joint angle completion checks를 사용하지만 runtime actor에는 제공하지 않는다.
- External F/T는 admittance controller에 사용되며 sensor source는 미명시다.
- Table IV가 pseudo-tactile on/off를 직접 비교해 binary feedback의 필요성을 뒷받침한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Gripper-state ambiguity | §I/§III-A pp.1–4 |
| Pseudo-tactile controller | §III-A/Fig.2 pp.3–4 |
| Privileged data generation | §III-B/Fig.3 pp.4–5 |
| Admittance / observation / action | §III-C p.5 |
| Real task comparison | §V-A–B/Tables I–III pp.6–7 |
| Ablation / failure analysis | §V-C/Table IV pp.7–8 |
| Limitation / Future | §VI p.8; no dedicated limitation/future section |
