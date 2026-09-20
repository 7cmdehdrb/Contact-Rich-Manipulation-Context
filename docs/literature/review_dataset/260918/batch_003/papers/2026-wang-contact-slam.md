# Contact SLAM: An Active Tactile Exploration Policy Based on Physical Reasoning Utilized in Robotic Fine Blind Manipulation Tasks

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B085`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Gaozhao Wang; Xing Liu; Zhenduo Ye; Zhengxiong Liu; Panfeng Huang
- Year: 2026
- Venue: arXiv preprint
- DOI / arXiv: Not stated / 2512.10481v2
- PDF version: arXiv v2 (2512.10481v2, 26 Jan 2026)
- Page count: 9
- SHA-256: `c8de578a2013e0ef05302ffc5560a2944f1eb1992dfa7508004b6a0a8b757f6e`
- PDF filename: Wang 등 - 2026 - Contact SLAM An Active Tactile Exploration Policy Based on Physical Reasoning Utilized in Robotic F.pdf
- 확인 범위: 전체 arXiv PDF pp.1-9; assumptions, tactile/wrench equations, factor graph, particle filter, active exploration, ablations/comparison, failures, conclusion/future work 확인

## 2. Relevance to This Review

`Relevant`

continuous vision 없이 두 Tac3D의 distributed force·resultant force/torque·marker displacement와 known geometry를 결합해 grasped object와 environment의 relative pose/contact region을 추정하고 assembly/pushing한다. Net wrench가 가능한 범위를 정확한 geometry, quasi-static/single-rigid-grasp constraints, particle filtering이 어떻게 보완하는지 명시해 두 핵심 Review 질문에 직접 답한다.

## 3. Task

시각이 가려진 상태에서 (1) 두·세 pin power-socket assembly와 (2) 장애물이 있는 block pushing을 수행한다. active contact exploration으로 상대 pose/obstacle region uncertainty를 줄인 뒤 A* trajectory를 실행하고 alignment factor로 완료를 판정한다.

## 4. Method

### 4.1. Overall Pipeline

양 fingertip Tac3D force distribution/marker displacement → resultant force/torque와 SVD relative transform → factor-graph localization + known polygon contours/contact-pair constraints + particle filter → entropy/distance-variance active exploration → A* path → robot motion until tactile change/alignment. [Fig. 3; Sec. III, PDF pp.2-5]

### 4.2. Observation

robot EEF/gripper pose, Tac3D marker-point displacement, left/right 3D force/resultant torque, tactile contact-change event, traveled distance, known object contours, particle distribution을 사용한다. scene object exact pose는 초기에 unknown이며 filter가 갱신한다. [Secs. II-III, PDF pp.2-5]

### 4.3. Action

candidate Cartesian directions 중 predicted contact outcomes의 entropy 또는 distance variance가 최대인 exploration motion을 고른다. contact signal 변화까지 움직인 뒤 particles를 갱신한다. 수렴 후 estimated pose에서 target pose까지 A* trajectory를 실행한다. [Sec. III-C-D, PDF pp.4-5]

### 4.4. Controller

구체적인 low-level Cartesian controller/gains는 원문에서 확인되지 않는다. Algorithm 2는 selected motion을 contact까지 실행하고 final A* trajectory를 alignment factor θ_ali=1까지 수행한다. [Algorithm 2, PDF p.5]

### 4.5. Learning / Optimization Method

학습 기반 RL이 아니라 physics/geometric model, factor-graph MAP, particle filtering, active information-gain planning의 hybrid state-estimation/controller이다. [Secs. III-B-D, PDF pp.3-5]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | gripper는 robot FK, grasped object는 tactile marker displacement, environment는 contact-pair particle/factor graph로 추정 | Yes | absolute/relative poses를 추정하되 task는 relative contact region이면 충분하다고 한다. [Secs. II-III, PDF pp.2-4] |
| Orientation | Tracking | Tac3D marker SVD rigid transform과 robot EEF pose; polygon/contact constraints | Yes | grasped object는 gripper에 대해 translation slip이 없다는 가정이 있다. [Secs. II and III-B, PDF pp.2-3] |
| Shape / Geometry | Initial | grasped/manipulated/obstacle의 exact polygon contours, dimensions, vertices | No | 방법을 성립시키는 강한 prior이다. [Assumption 3 and Sec. III-C, PDF pp.2,4] |
| Physical Parameters | 기타 | quasi-static, rigid/static scene 및 grasp constraint를 가정; mass/friction 값은 미명시 | No | dynamic constraints는 future work이다. [Sec. II assumptions and V, PDF pp.2,9] |

## 6. Missing Object Information and Compensation

초기 scene object/obstacle exact pose 미제공
→ Tac3D-derived object displacement + resultant force direction + robot pose + known geometry + particle/filter history
→ contact 가능한 contour pair를 줄이고 relative pose posterior를 갱신한다. [Secs. III-B-C, PDF pp.3-4]

Net force/torque만으로 contact locality/configuration이 고유하지 않음
→ exact polygon contours, opposed normals, quasi-static/rigid/static assumptions, active motion outcome
→ candidate contact regions/particles를 반복적으로 제거한다. 즉 F/T-like wrench만으로 성립하는 방법이 아니라 geometry와 exploration이 ambiguity를 해소한다. [Secs. II and III-C-D, PDF pp.2,4-5]

정확 contact configuration 미복원
→ relative contact-region distribution
→ task planning에 충분한 localization만 추정한다. 이는 저자가 명시한 설계 선택이다. [Sec. II, PDF p.2]

## 7. Tactile

### 7.1. Raw Sensor

양 gripper finger의 Tac3D sensors. sensor-frame 3D force distribution, resultant 3D force, resultant 3D torque, internal marker-point displacement를 제공한다. [Sec. III-A-B, PDF pp.2-3]

### 7.2. Preprocessing

left/right sensor 좌표의 force components를 gripper frame force로 조합하고, marker points의 before/current 대응을 SVD rigid registration해 rotation R과 translation M을 구한다. contact signal change를 event로 검출한다. [Eqs. (1),(4)-(5), PDF pp.3-4]

### 7.3. Policy Representation

grasped-object relative rigid transform T_s_l, resultant force direction/magnitude, torque, binary/contact-change event z_obs, factor-graph variables와 particle weights. [Secs. III-A-C, PDF pp.2-4]

### 7.4. Retained Information

local deformation-derived relative motion, distributed load, net force/torque direction, contact occurrence와 history를 남긴다. [Secs. III-A-C, PDF pp.2-4]

### 7.5. Removed / Unavailable Information

정확한 environment contact patch/configuration을 직접 측정하지 않고 candidate contact region으로 축약한다. 외부 접촉은 grasped object를 통해 간접 관측되며 force direction만으로는 contour pair가 고유하지 않다. [Secs. II and III-C, PDF pp.2,4]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

두 fingertip Tac3D tactile sensors가 계산한 resultant 3D forces/torques. Wrist 6-axis F/T가 아니다. [Sec. III-A, PDF p.2]

### 8.2. Representation

left/right component difference로 얻은 gripper-frame Fx,Fy,Fz; each sensor resultant torque; force direction; contact-change event; alignment thresholds. [Eq. (1), Sec. III-A-C, PDF pp.2-4]

### 8.3. Role

외부 contact direction 추정, contact pair selection, particle likelihood update, motion-until-contact termination, operation alignment/success 판단. [Secs. III-B-D, PDF pp.3-5]

### 8.4. Required Assumptions

quasi-static contact; rigid/static environment; grasped object와 gripper 사이 translation 없음; exact object geometry/dimensions; known sensor/robot transforms; opposing contour normals; all external loads transmitted to fingertip sensors. [Sec. II assumptions and III-A-C, PDF pp.2-4]

### 8.5. Reported Limitation / Ambiguity

method는 exact contact configuration을 구하지 않고 relative contact-region만 추정한다. 비슷한 hole regions는 multi-peak particle posterior와 non-convergence를 만들며, indirect block contact는 movable-block size에 따른 translation shift를 고려해야 한다. [Sec. II; IV-B-D, PDF pp.2,7-8]

## 9. Other Observations

- Proprioception: EEF/gripper pose와 commanded/traveled motion distance.
- Vision: 실행 중 사용하지 않는다. evaluation plot의 ground truth는 평가용이다.
- History: factor graph와 particle posterior가 contact events 전체를 누적한다.
- Previous action: chosen motion direction와 traveled distance가 likelihood backtracking에 사용된다.
- State estimator: factor-graph MAP + particle filter가 grasped/environment relative pose와 contact region을 추정한다.
- Goal: target region/goal contact state는 prior로 제공된다.

## 10. Tactile–Other Modality Relationship

Tac3D의 marker displacement는 grasped object의 gripper-relative pose를, distributed/resultant forces와 torques는 external contact direction/event를 제공한다. Net wrench만으로 contact locality를 결정하지 않고 known polygon contours와 active action outcomes가 spatial ambiguity를 줄인다. 따라서 여기서 tactile이 F/T-like resultant wrench에 추가하는 정보는 local marker deformation/relative transform과 distributed force이며, geometry prior와 history가 함께 필요하다. Sensor components의 독립 ablation은 없다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | 비-RL model-based estimation/planning. Ground-truth socket/obstacle pose는 evaluation RMSE에만 사용되며 실행 estimator 입력이 아니다. [전체 PDF pp.1-9] |
| Critic | Not applicable | 비-RL | 비-RL model-based estimation/planning. Ground-truth socket/obstacle pose는 evaluation RMSE에만 사용되며 실행 estimator 입력이 아니다. [전체 PDF pp.1-9] |
| Reward | Not applicable | 비-RL | 비-RL model-based estimation/planning. Ground-truth socket/obstacle pose는 evaluation RMSE에만 사용되며 실행 estimator 입력이 아니다. [전체 PDF pp.1-9] |
| Termination | Not applicable | 비-RL | 비-RL model-based estimation/planning. Ground-truth socket/obstacle pose는 evaluation RMSE에만 사용되며 실행 estimator 입력이 아니다. [전체 PDF pp.1-9] |
| Curriculum | Not applicable | 비-RL | 비-RL model-based estimation/planning. Ground-truth socket/obstacle pose는 evaluation RMSE에만 사용되며 실행 estimator 입력이 아니다. [전체 PDF pp.1-9] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| active tactile reasoning이 passive force search보다 assembly에 유리하다. | Controlled comparison | Contact SLAM active exploration vs spiral hole search | two-pin 80%, three-pin 84% success; spiral search 10%. | Sec. IV-B.2; PDF PDF p.6 ; Table I |
| distance-variance criterion과 adaptive resampling이 localization failure를 줄인다. | Input/algorithm ablation | entropy-only/fixed resampling vs each improvement | entropy가 작은 local optimum과 premature particle elimination을 각각 회복해 unimodal convergence를 만든다. | Sec. IV-B.1; PDF PDF pp.6-7 ; Figs. 5-6 |
| contact-derived localization이 environment pose를 갱신한다. | Controlled evaluation | different gripper/plug initial positions | socket estimate가 ground truth 근처로 수렴하고 error가 2 mm 이내; pushing obstacle error는 10 mm 이내. | Secs. IV-B.2 and IV-C; PDF PDF p.8 ; Figs. 8-9 |

## 13. Author-stated Limitations

exact geometry/dimensions와 quasi-static geometric constraints에 크게 의존한다. 비슷한 크기의 multiple hole regions에서는 particle posterior가 multi-modal로 남아 maximum exploration steps 후에도 수렴하지 않을 수 있다. 정확한 contact configuration 대신 task-level region만 추정하며 current work는 dynamic constraints를 다루지 않는다. [Secs. II, IV-B, V, PDF pp.2,7,9]

## 14. Author-stated Future Work

fine manipulation에서 dynamic constraints를 포함하도록 framework를 확장해 task capability를 높일 계획이다. [Sec. V, PDF p.9]

## 15. Review-relevant Findings

- 실행 중 vision 없이 Tac3D와 prior scene geometry로 relative pose/contact region을 tracking한다.
- F/T source는 wrist가 아니라 두 fingertip Tac3D가 계산한 resultant force/torque이다.
- Net wrench만으로 contact locality를 복원하지 않으며 known exact contours와 active exploration이 ambiguity를 줄인다.
- tactile marker displacement는 grasped-object relative transform을 추가한다.
- factor graph와 particle history가 contact events를 누적한다.
- sensor-modality ablation은 없지만 active exploration components 및 passive spiral-search 비교가 있다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | Secs. II-III, PDF pp.2-5 |
| Object pose | Eqs. (3)-(6), PDF pp.3-4 |
| Tactile | Sec. III-A-B, PDF pp.2-3 |
| F/T | Eq. (1) and Sec. III-C, PDF pp.2-4 |
| Reward | 해당 없음; entropy/distance information gain Eq. (8), PDF p.4 |
| Critic | 해당 없음 |
| Ablation | Sec. IV-B.1, PDF pp.6-7; Figs. 5-6 |
| Limitation | Secs. IV-B.2 and V, PDF pp.7,9 |
