# Vi-TacMan: Articulated Object Manipulation via Vision and Touch

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B014`. 이번 batch의 제공 PDF를 새로 읽은 분석이다. 페이지 표시는 별도 언급이 없으면 PDF의 1-based page다. 기존 상세 논문 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Leiyao Cui; Zihang Zhao; Sirui Xie; Wenhuan Zhang; Zhi Han; Yixin Zhu
- Year: 2026
- Venue: arXiv preprint; published venue Not stated
- DOI: Not stated
- arXiv: 2510.06339v3
- PDF version: arXiv:2510.06339v3, 2 April 2026
- Page count: 8
- SHA-256: `e4906095739291fec96f41452cbec9a752d50a53dbe50d57defb965db2647062`
- PDF filename: Cui 등 - 2026 - Vi-TacMan Articulated Object Manipulation via Vision and Touch.pdf
- 확인 범위: 제공 PDF 전체(참고문헌 포함); 별도 Appendix 없음. 외부 code/video/supplement는 확인하지 않음.

## 2. Relevance to This Review

`Relevant`

초기 vision으로 stable grasp와 coarse interaction direction을 얻고 이후 tactile contact regulation으로 articulated manipulation을 수행하므로 초기 object 정보 이후의 보완 구조를 직접 보여 준다. Tactile은 threshold로 활성 marker를 고른 뒤 marker 위치변화를 유지하는 표현이며 영역별 Binary policy가 아니다. F/T를 함께 사용하는 연구는 아니다.

## 3. Task

손잡이가 있는 articulated object의 movable part를 조작한다. 초기 안정 파지와 대략적인 진행 방향을 얻은 뒤 contact configuration을 유지하며 문/서랍류의 구속운동을 따른다. 시뮬레이션의 정량지표는 주로 unseen-category interaction direction의 angular error이며, 실물은 complete manipulation 사례를 보여 준다. 실물 task 성공의 통일된 각도/거리 threshold, 반복 trial 수와 success rate는 제공 PDF에 미명시다. [§II–IV, PDF pp.2–7]

## 4. Method

### 4.1. Overall Pipeline

초기 Femto Bolt RGB-D → depth refinement + surface normals → DINOv3 detector + SAM2 movable/holdable masks → collision-free parallel-grasp sampling → PointNet++ point-displacement prediction → Kabsch transforms → grasp-point directions의 vMF/Fréchet mean → grasp $G$와 coarse direction $d$ → GelSight-style active marker positions 변화의 point registration → 50 Hz EEF pose update. [§II–III, PDF pp.2–6]

### 4.2. Observation

Vision initializer는 camera-frame visible point position $p$, RGB $c$, surface normal $n$, movable mask $m$, holdable mask $h$를 다룬다(Eq.(2)). Displacement network에는 point coordinates, movable-region normals, movable masks를 사용한다. Grasping pose는 holdable region centroid와 sampled gripper rotations/width로 정한다. 실행 tactile controller는 initial reference contact $C_0$와 현재 contact $C_{t+1}$의 차이를 줄이는 EEF transform을 계산한다(Eq.(1)). 초기 $G,d$ 이후 all subsequent manipulation은 tactile policy로 수행한다고 명시한다. Whole-object current 6D pose 또는 articulation-axis tracking input은 정의하지 않는다. [§II-A–C; §III-C–E, PDF pp.2–6]

### 4.3. Action

상위 출력 $G\in\mathrm{SE}(3)\times\mathbb{R}$는 grasp pose+gripper width이고 $d\in\mathbb{S}^{2}$는 coarse direction이다. 하위 tactile controller는 reference contact를 복원하는 EEF transform $T_{\Delta}\in\mathrm{SE}(3)$를 출력한다. Step size, stiffness/force command, exact joint command 형식은 이 PDF에서 미명시다. [Eqs.(1),(3)–(10); §III-E, PDF pp.2–6]

### 4.4. Controller

Kinova Gen3 7-DoF의 gripper pads를 GelSight-type tactile sensors로 대체한다. Normal deformation이 threshold를 넘는 marker 위치를 추적하고 point registration으로 EEF pose update를 계산하며 50 Hz로 contact를 조절한다. TacMan/TacMan-Turbo의 전체 알고리즘을 참조하지만 이 PDF가 생략한 state machine/threshold/calibration을 그 문헌이나 상식에서 채우지 않는다. Joint-level controller/IK 구성은 미명시다. [§III-E/IV-B, PDF pp.5–7] 현재 PDF는 space constraints 때문에 controller 상세를 선행연구로 안내하므로 생략된 threshold/stop rule은 미명시로 남긴다. [§III-E, PDF p.5; 확인 범위의 한계]

### 4.5. Learning / Optimization Method

RL이 아니다. Detection과 displacement network를 supervised learning으로 학습한다. PartNet-Mobility 385개 object/8 categories의 SAPIEN render와 GAPartNet labels를 사용하며 train 39,524 / validation 9,881 / test 5,836 samples다. Test categories는 dishwasher/door/oven/table이다. Point-displacement loss는 relative L1 magnitude error와 cosine direction loss의 합(Eq.(11)); AdamW 사용. Point-flow target/part labels는 학습용 simulator/annotation 정보이며 실행 tactile 관측과 구분한다. 5만여 synthetic samples를 5만회의 로봇 조작 성공 episode로 해석하지 않는다. [§III-A/B/D; §IV-A, PDF pp.4–6]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Initial | 초기 RGB-D visible point coordinates와 holdable-region centroid | 초기 grasp 설정 이후 object position 갱신 없음 | 부분적 물체 영역 위치 단서이며 whole-object center/full pose가 아님. Gripper translation을 초기화하는 데 사용 [§II-B; §III-C, Eqs.(2)–(3), PDF pp.2–4] |
| Orientation | 미제공 | Current object orientation/kinematic joint-axis 추정 입력 없음 | 없음 | Grasp orientation과 interaction direction을 current object orientation으로 세지 않음 [§II-A–C; §III-E, PDF pp.2–3,5–6] |
| Shape / Geometry | Initial | RGB-D partial point cloud; depth-derived surface normals; movable/holdable masks | 초기 grasp/direction inference 이후 tactile execution | Full CAD/mesh와 explicit articulation model은 실행에 요구하지 않음 [§II-B; §III-A–E, PDF pp.2–6] |
| Physical Parameters | 미제공 | Mass/friction/stiffness actor input 미명시 | 없음 | Rigid-body assumption과 stable-grasp assumption은 별도 [§II-C; §V, PDF pp.3,7–8] |

## 6. Missing Object Information and Compensation

정확한 hidden articulation kinematics 및 실행 중 whole-object pose model 미제공 → 초기 vision의 grasp/coarse direction + active-marker tactile contact feedback → reference contact와 현재 contact의 차이를 줄이며 constrained motion을 따른다. 저자가 명시한 vision-global/touch-local 역할 분담이다. Tactile-only 자체가 완전한 초기 무지에서 출발하는 방식은 아니며 초기 stable grasp/direction이 필요하다. [Abstract/§II-A/§III-E/§V, PDF pp.1–2,5–7]

## 7. Tactile

### 7.1. Raw Sensor

Gripper pads의 GelSight-style optical tactile sensors. Silicone elastomer, black markers, Lambertian coating을 사용한다. 센서 image resolution, marker 수, 정확한 센서 개수와 calibrated force 단위는 미명시다. [§III-E; Figs.6/9, PDF pp.5–7]

### 7.2. Preprocessing

Normal deformation이 predefined threshold를 넘는 marker를 activated로 선택한 뒤 marker-wise position change를 tracking한다. Threshold 수치·검출/좌표변환 상세는 미명시다. [§III-E, PDF p.5]

### 7.3. Policy Representation

Activated marker positions 및 reference/current contact의 point-set difference → point registration → EEF SE(3) pose update. Binary presence vector만 사용하는 것이 아니다. [§II-A, Eq.(1); §III-E, PDF pp.2,5]

### 7.4. Retained Information

접촉한 marker의 identity/spatial arrangement와 marker-wise displacement; reference contact 대비 configuration 변화. 전체 feature dimension과 좌표계는 미명시다. [§III-E, PDF p.5]

### 7.5. Removed / Unavailable Information

Threshold 이하 marker는 active feature set에서 제외된다(표현 구조상 직접 확인 가능). Raw tactile image의 texture/intensity가 얼마나 소실되는지는 미명시. Metric force/wrench와 full-object pose를 tactile representation이 제공한다고 볼 근거 없음. [§III-E, PDF p.5]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. Independent wrist F/T 또는 joint-torque estimated wrench가 제안 입력에 없음. [§III-E/IV-B, PDF pp.5–7]

### 8.2. Representation

해당 없음. Marker deformation을 metric force/wrench로 변환한다고 명시하지 않는다. [§III-E, PDF p.5]

### 8.3. Role

해당 없음. Contact regulation은 tactile point registration 기반이다. [§II-A; §III-E, PDF pp.2,5]

### 8.4. Required Assumptions

F/T-only 방법에 해당 없음. 전체 방법의 제약은 stable grasp, coarse initial direction, Kabsch rigid-body assumption이다. [§II-A/C; §V, PDF pp.2–3,7–8]

### 8.5. Reported Limitation / Ambiguity

원문에서 F/T 한계를 직접 논의하지 않음. [§II–V, PDF pp.2–8]

## 9. Other Observations

Vision은 초기 global grasp/direction inference에 사용하며 이후 tactile execution을 명시한다. Depth refinement는 foundation-model relative depth의 scale을 sensor depth와 RANSAC linear fit으로 맞춘다. History는 initial contact $C_0$와 current contact/marker change 비교로 존재하지만 frame-stack 길이나 recurrent hidden state는 미명시다. Proprioception 및 previous-action input contract는 미명시다. State estimator는 초기 predicted displacement/transform/direction과 실행 contact-registration update이며 current object-pose estimator와 다르다. [§II–III, PDF pp.2–6]

## 10. Tactile–Other Modality Relationship

| 추가 정보 | Tactile 정보 | Tactile에서 부족한 정보 | 추가 정보의 역할 | 근거 |
| --- | --- | --- | --- | --- |
| 초기 RGB-D/normal/part masks | Local contact marker 변화 | 어디를 잡고 어느 방향으로 시작할지의 global cue | Grasp $G$와 coarse direction $d$ 제안 | §II-A–C/III, pp.2–6 |
| Initial reference contact $C_0$ | 현재 marker contact configuration | 안정 접촉의 기준 상태 | Registration 목표로 사용 | Eq.(1), p.2 |
| F/T | 해당 없음 | 해당 없음 | 사용하지 않음 | §III-E, pp.5–6 |

저자는 vision/touch의 역할 분담을 직접 설명한다. 하지만 제공 PDF의 정량 ablation은 surface normal 입력의 direction-estimation 기여이며 tactile 제거/vision-only 조작 성공률과의 통제 비교는 없다. 영역별 Binary로 marker positions를 대체하는 실험도 없다.

## 11. Training-only / Privileged Information

비-RL이므로 아래 RL 구분은 `해당 없음`이다. Supervised learning의 annotation/point-flow 정답은 §4.5에 별도로 기록했다.

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | Actor/critic/reward/termination/curriculum RL 구분은 해당 없음. Supervised point-flow GT와 GAPartNet labels는 §III에 명시 [§III-A/B/D, PDF pp.4–5] |
| Critic | Not applicable | 비-RL | Actor/critic/reward/termination/curriculum RL 구분은 해당 없음. Supervised point-flow GT와 GAPartNet labels는 §III에 명시 [§III-A/B/D, PDF pp.4–5] |
| Reward | Not applicable | 비-RL | Actor/critic/reward/termination/curriculum RL 구분은 해당 없음. Supervised point-flow GT와 GAPartNet labels는 §III에 명시 [§III-A/B/D, PDF pp.4–5] |
| Termination | Not applicable | 비-RL | Actor/critic/reward/termination/curriculum RL 구분은 해당 없음. Supervised point-flow GT와 GAPartNet labels는 §III에 명시 [§III-A/B/D, PDF pp.4–5] |
| Curriculum | Not applicable | 비-RL | Actor/critic/reward/termination/curriculum RL 구분은 해당 없음. Supervised point-flow GT와 GAPartNet labels는 §III에 명시 [§III-A/B/D, PDF pp.4–5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Surface normals가 coarse direction 정확도를 개선 | Input ablation; Controlled comparison | Ours with vs without normals; 5,836 unseen-category samples | Mean±SD angular error 8.13±6.54° vs 10.10±6.57°. FlowBot3D 13.92±9.45°, Normal-only 12.66±8.25°. 세 baseline 대비 one-sided paired tests p<0.0001 | §IV-A; PDF pp.5–6; Table II; Fig.7 |
| 초기 vision과 local tactile의 역할 분담 | Author explanation only | Coarse $G,d$ initialization then tactile registration execution | 정확한 kinematic recovery 대신 contact stability를 유지한다는 저자 설명. Tactile-removal controlled ablation 없음 | §II-A; §III-E; §V; PDF pp.2,5–7; Not applicable; Not applicable |
| 결합 시스템의 실물 articulated manipulation | Author explanation only | 실물 vision initialization + tactile controller demonstration | 4개 real examples를 5 viewpoints로 visual test; Fig.10에 manipulation 사례. 제공 PDF의 반복 trial 수/성공률/실패 통계 미명시 | §III-A; §IV-B; PDF pp.4,7; Not applicable; Figs.9–10 |

## 13. Author-stated Limitations

Kabsch displacement 추정은 strict rigid-body assumption을 사용한다. 여러 distinct valid direction을 가진 물체는 현재 vMF 표현만으로 부족할 수 있다. 초기 grasp가 조작 내내 stable하다고 가정하며 slip recovery는 현재 구현 범위 밖이다. [§V, PDF pp.7–8]

## 14. Author-stated Future Work

Non-rigid deformation 및 multi-stage articulation에 대한 displacement estimation, deformable tracking/sequential state estimation, multi-modal direction distribution 또는 high-level command conditioning, tactile slip detection과 dynamic re-grasping을 제안한다. Coarse direction/grasp를 AR 또는 언어로 사용자에게 보여 주는 HRI 확장도 향후 가능성으로 제시한다. [§V, PDF pp.7–8]

## 15. Review-relevant Findings

- 초기 RGB-D/geometry cue를 이용한 grasp·direction과 실행 tactile contact regulation을 분리한다.
- 초기 visible point coordinates와 holdable-region centroid는 부분적 Position=Initial 정보이며 whole-object current pose tracking이 아니다.
- Threshold는 active-marker 선택 단계이며 이후 marker 위치변화를 유지한다.
- Current object pose/explicit articulation model tracking 대신 reference contact를 규제한다.
- Wrist F/T 병용이나 Binary tactile 축약 실험은 없다.
- 정량 ablation은 surface-normal 입력이고 modality complementarity를 분리한 ablation은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / Object pose | §II-A–C, Eqs.(1)–(10), PDF pp.2–4 |
| Geometry / supervised GT | §III-A/B/D, PDF pp.4–5 |
| Tactile | §III-E; Figs.6/9, PDF pp.5–7 |
| F/T | 사용하지 않음; §III-E/IV-B, PDF pp.5–7 |
| Reward / Critic | 해당 없음; supervised learning §III, PDF pp.4–5 |
| Ablation | §IV-A; Table II; Fig.7, PDF pp.5–6 |
| Limitation / Future Work | §V, PDF pp.7–8 |
