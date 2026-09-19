# Dynamic object goal pushing with mobile manipulators through model-free constrained reinforcement learning

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B015`. 이번 batch의 제공 PDF를 새로 읽은 분석이다. 페이지 표시는 별도 언급이 없으면 PDF의 1-based page다. 기존 상세 논문 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Ioannis Dadiotis; Mayank Mittal; Nikos Tsagarakis; Marco Hutter
- Year: 2025
- Venue: 2025 IEEE International Conference on Robotics and Automation (ICRA), 13363–13369
- DOI: 10.1109/ICRA55743.2025.11128166
- arXiv: Not stated
- PDF version: publisher
- Page count: 7
- SHA-256: `3e2c43e804a6430d7501034a50bef6de747e7a52bf95805a1750ecbca073c173`
- PDF filename: Dadiotis 등 - 2025 - Dynamic Object Goal Pushing with Mobile Manipulators Through Model-Free Constrained Reinforcement Le.pdf
- 확인 범위: 제공 PDF 전체(참고문헌 포함); 별도 Appendix 없음. 외부 code/video/supplement는 확인하지 않음.

## 2. Relevance to This Review

`Partially Relevant`

Tactile/F/T를 정책 입력으로 쓰지 않는 contact-rich pushing 연구지만, 실행 actor의 pose-only object 정보와 학습 critic·reward·constraint의 추가 물체 GT를 명확하게 분리한다. 따라서 shape/dynamics가 실행에서 빠진 조작의 training-time information 조건을 비교하는 한정 근거로 포함한다. 시각/pose가 없는 실행이나 tactile·F/T 상보성의 직접 근거는 아니다.

## 3. Task

ANYmal mobile base와 6DoF arm으로 물체를 목표 평면 위치와 yaw orientation으로 밀고 다시 접촉 위치를 바꾼다. Object toppling을 억제하며 이동·재배향을 수행한다. 성공 허용치는 object–goal 거리 $\leq 10\,\mathrm{cm}$와 orientation error $\leq 10^{\circ}$다. Sim episode는 20초 timeout 또는 회복 불가능한 robot/object fall에서 reset하며, 실물은 success까지 실행하고 이후 base command를 zero로 둔다. [§III-B/E, PDF pp.3–4]

## 4. Method

### 4.1. Overall Pipeline

Current object/base pose와 proprioception·previous action → 54D asymmetric actor → 11D push action(base 6D + arm 5D) → frozen pretrained locomotion policy(base command를 leg joint targets로 변환) + arm joint impedance controller → robot. Push/locomotion policy는 모두 50 Hz다. Arm의 6번째 joint는 고정한다. [Fig.2; §III-A–C, PDF pp.2–3]

### 4.2. Observation

Actor는 54D(Table I): base-frame EEF–object relative position 3D; object rotation matrix 9D; arm joint position deviation 5D; base linear velocity 3D와 angular velocity 3D; arm joint velocity 5D; projected gravity 3D; base-frame object–goal relative position 3D; object-frame goal rotation 9D; previous action 11D를 받는다. Current object pose와 goal-related terms를 모두 포함한다. Actor에는 object mass/size/shape/contact state/velocity가 직접 들어가지 않는다. 실물의 object/base 6D pose는 external motion capture에서 받으며 simulation actor에는 표의 uniform noise를 넣는다. Critic은 noiseless actor features + 19D privileged state로 73D다. [§III-C/E; Table I, PDF pp.3–4]

### 4.3. Action

11D deviation action: base linear velocity $v_x,v_y$; yaw rate; roll, pitch; height의 6성분과 arm joint position 5성분. 기본 base state(속도/방향 0, 높이 0.5 m) 및 default arm configuration에 대한 차이를 absolute command로 변환한다. 이는 EEF의 6D Cartesian action과 다르다. [§III-A/C, PDF pp.2–3]

### 4.4. Controller

Pretrained student locomotion policy가 base 6D command와 로봇 상태를 받아 leg joint position targets를 만든다. Push training 중 locomotion policy weight를 freeze한다. Arm command는 low-level joint impedance controller로 보낸다. Locomotion policy 전체 입력 vector와 torque estimation을 위한 상세 경로는 원문에 미명시다. [§III-A/C, PDF pp.2–3]

### 4.5. Learning / Optimization Method

Isaac Lab의 4,096 parallel environments에서 20,000 iterations의 asymmetric constrained PPO를 학습한다. CaT(Constraints as Terminations)를 적용하며 reward는 object/goal bounding box의 8개 keypoint distance, EEF–surface reach target distance, goal 방향 object velocity, action-rate regularization이다. Mass/CoM/dimensions/friction/shape/robot mass 및 외란을 randomize한다. 특정 reach target은 episode마다 object vertical surface에서 sampling하여 학습 초기에 접촉 위치 탐색을 유도한다. 해당 reward weight는 1,500 iterations 뒤 1/4로 낮추며 constraint reward-termination probability를 curriculum으로 바꾼다. [§III-B–E; Table II, PDF pp.2–4]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Sim GT+noise; real external motion capture의 object/base pose | 각 50 Hz policy inference에 사용 | EEF-object relative position 3D와 object-goal relative position 3D를 구분 [Table I; §III-C/E, PDF pp.3–4] |
| Orientation | Tracking | Object rotation matrix; real external motion capture | 실행 중 갱신 | Current object rotation과 goal relative rotation은 별도 9D inputs [Table I; §III-C/E; §IV-D, PDF pp.3–4,6] |
| Shape / Geometry | 미제공 | Actor에 dimensions/shape label 없음 | 없음 | Critic의 dimensions 3D/shape one-hot 2D와 reward의 bbox keypoints/surface target은 별도 제공 [Table I; §III-D/E, PDF pp.3–4] |
| Physical Parameters | 미제공 | Actor에 mass/CoM/inertia/friction 없음 | 없음 | Critic은 mass/CoM/inertia/velocities를 받고 friction은 randomization 설정 [Table I; §III-C–E, PDF pp.3–4] |

## 6. Missing Object Information and Compensation

실행 actor에 object size·shape·dynamics와 contact state가 없음 → current object pose tracking + robot proprioception + previous action + domain-randomized training/privileged critic → pose 반응, 특히 object inclination에 따라 contact location과 pushing height를 바꾼다. 저자는 작은 base의 물체를 더 낮게 미는 행동이 object pose observation에 기반한다고 설명한다. 그러나 pose/previous-action/privileged-critic 제거 ablation을 수행하지 않았으므로 각 정보의 독립적인 필요성은 입증하지 않았다. [§III-C–E; §IV-D, PDF pp.3–4,6]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. Simulator EE-object contact state는 critic 전용이며 tactile sensor observation이 아니다. [Table I; §III-C, PDF p.3]

### 7.2. Preprocessing

사용하지 않음. Simulator EE-object contact state는 critic 전용이며 tactile sensor observation이 아니다. [Table I; §III-C, PDF p.3]

### 7.3. Policy Representation

사용하지 않음. Simulator EE-object contact state는 critic 전용이며 tactile sensor observation이 아니다. [Table I; §III-C, PDF p.3]

### 7.4. Retained Information

사용하지 않음. Simulator EE-object contact state는 critic 전용이며 tactile sensor observation이 아니다. [Table I; §III-C, PDF p.3]

### 7.5. Removed / Unavailable Information

사용하지 않음. Simulator EE-object contact state는 critic 전용이며 tactile sensor observation이 아니다. [Table I; §III-C, PDF p.3]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

실행 push actor에는 tactile/F/T/wrench 또는 joint torque가 없다. Arm/leg joint torque는 Table II의 학습 constraint에 쓰이며 wrist F/T sensing이 아니다. [Tables I–II, PDF pp.3–4]

### 8.2. Representation

Force/wrench policy representation 해당 없음. Constraint는 absolute joint torque와 nominal torque limit의 차이를 사용한다. [Table II, PDF p.4]

### 8.3. Role

Joint torque는 actuation-limit constraint이며 actor observation이나 contact localization 입력이 아니다. Critic의 contact state $\lambda_e$ 역시 force measurement가 아니다. [Tables I–II, PDF pp.3–4]

### 8.4. Required Assumptions

F/T-only 방법 해당 없음. Current object/base pose tracking, frozen locomotion policy, known robot joint/control limits를 사용한다. [§III, PDF pp.2–4]

### 8.5. Reported Limitation / Ambiguity

원문이 선행 force/tactile-only pushing의 contact break 후 feedback 상실을 설명하지만, 본 연구의 F/T-only ambiguity 실험은 없다. Net-wrench locality/multi-contact ambiguity는 직접 검증하지 않는다. [§I/II-B, PDF pp.1–2]

## 9. Other Observations

Proprioception은 arm joint position/velocity, base velocity/angular velocity/projected gravity이며 locomotion controller에도 robot state를 제공한다. Vision/pose acquisition은 실물 external motion capture이며 onboard RGB input은 없다. Previous action 11D를 actor에 포함한다. Frame history/RNN은 현 구조에 없고 memory는 향후 계획이다. Goal은 current object에 대한 relative position/orientation으로 actor에 들어간다. State estimator는 external object/base tracking 외 explicit object dynamics/contact estimator가 없다. [Table I; §III-A/C/E; §V, PDF pp.2–4,6]

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않으므로 tactile–F/T/proprioception 상보성은 해당 없음. 이 논문에서 비교 가능한 사실은 object pose만을 object 관측으로 제한한 실행 actor와 shape/dynamics/contact GT를 가진 학습 계층의 차이다. Joint torque constraint를 F/T sensor 병용으로 기록하지 않는다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | Yes: noisy simulator current object pose; hidden object properties No | Object-relative EEF position; current object rotation; goal-relative terms; robot state; previous action | 실물에는 external motion capture가 계속 필요. 학습 actor에 object pose가 없다는 분류는 틀림 [Table I; §III-C/E, PDF pp.3–4] |
| Critic | Yes | Noiseless actor observation + EE-object contact 1D, object CoM 3D, mass 1D, dimensions 3D, inertia 3D, linear velocity 3D, angular velocity 3D, shape one-hot 2D = 19 privileged dimensions | 총 73D. 실행 actor에는 이 19D가 필요하지 않음 [Table I; §III-C, PDF p.3] |
| Reward | Yes | Object/goal GT bbox의 8개 keypoints; surface reach target; object velocity; goal success; action rates | 배포에는 reward를 계산하지 않음. Bounding box와 surface GT는 actor shape input이 아님 [§III-D; Table II, PDF pp.3–4] |
| Termination | Yes for training constraints/state outcomes | CaT reward-termination probability는 joint/torque/collision/object-tilt constraints에 의존. Environment reset은 20 s timeout 또는 unrecoverable robot/object fall. 실물 stop은 tracked object-goal success 후 base command를 zero로 설정 | 세 종류를 구분한다. 모든 constraint violation이 즉시 환경 hard-reset을 일으킨다는 뜻은 아님. Object tilt/collision 등은 학습 GT; 실물 성공은 mocap pose로 판정 [§III-B/D/E; Table II, PDF pp.3–4] |
| Curriculum | Yes | GT object surface reach sampling; reach reward weight schedule; CaT probability schedule; mass/CoM/size/friction/shape reset randomization | 실행 actor에 object dimensions/physics를 추가하지 않는다 [§III-B/D/E; Table II, PDF pp.3–4] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| 학습용 surface target과 balance constraint가 성공/전도율에 영향 | Controlled comparison | 4조건: surface sampling과 balance constraint의 유무; 4,096 sim runs | Full success 91.35% / toppled 3.46%; without balance 90.00% / 6.93%; without surface 49.80% / 4.50%; without both 88.70% / 7.73%. Sensor/critic-input ablation 아님 | §IV-A; PDF pp.4–5; Table III; Not applicable |
| Size가 실행 입력에 없어도 push height가 object footprint에 적응 | Controlled comparison; Author explanation only | 6 footprint sizes; size별 1,000 successful episodes; height/mass/CoM/friction 고정, noise off | Small base에서 더 낮은 EEF contact height. 저자는 object pose feedback 기반이라고 설명; pose 제거 실험은 없고 성공 episode에 조건부인 통계 | §IV-D; PDF p.6; Not applicable; Fig.6 |
| 실물에서 unknown object를 goal pose로 pushing | Controlled comparison | 7 object 조건(material/shape/mass/goal-yaw 변경) | Table V success 80.0–92.9%; current pose는 mocap으로 지속 제공. Trial denominator 미명시 | §IV-C; PDF p.5; Table V; Fig.4 |
| Object tilt에 따라 낮은 contact로 이동 | Author explanation only | Thin cylinder의 실물 time trace | Arm EEF height와 base height/pitch/roll이 tilt 후 바뀜; memory/pose/force 센서의 독립 기여 비교 아님 | §IV-D; PDF p.6; Not applicable; Fig.7 |
| 성공 허용치 직전에 정지하는 실패 | Failure analysis | 실물 실패 사례 설명 | 대부분 물체를 success margin 가까이 민 뒤 정지. 저자는 method의 근본 한계보다 추가 policy tuning 문제로 해석 | §IV-C; PDF p.6; Not applicable; Not applicable |

## 13. Author-stated Limitations

별도 Limitations 절은 없다. 저자는 low reaching에서 shoulder joint limit에 근접해야 하는 구현상의 어려움을 설명한다. 실물 실패의 상당수는 success margin 직전에서 멈추는 경우이며, 저자는 이를 방법의 근본 한계라기보다 추가 tuning으로 개선할 수 있는 문제로 해석한다. [§IV-B/C, PDF pp.5–6] 외부 motion capture에 의존한다는 사실은 §III-E에 명시되지만 이를 촉각/F/T의 한계라고 바꾸어 쓰지 않는다.

## 14. Author-stated Future Work

Policy architecture에 memory를 추가하고 object perception을 onboard solution으로 바꾸는 방향을 제안한다. [§V, PDF p.6]

## 15. Review-relevant Findings

- 실물 실행에도 current object/base pose tracking이 필요하다.
- Object shape/dynamics와 EE-object contact는 actor가 아닌 critic 전용 GT다.
- Bounding-box keypoints와 surface sampling이 reward/training에 사용된다.
- Joint torque는 학습 constraint용이며 force/wrench actor 입력이 아니다.
- CaT reward termination, environment reset, 실물 success stop은 서로 다르다.
- Tactile/force 센서 제거 또는 privileged-critic 제거 ablation은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / Current pose | Table I; §III-C/E, PDF pp.3–4 |
| Shape / Physical parameters | Table I; §III-D/E, PDF pp.3–4 |
| Tactile / F/T | Actor에 없음; Tables I–II, PDF pp.3–4 |
| Reward / Termination / Curriculum | §III-B/D/E; Table II, PDF pp.3–4 |
| Critic | Table I, PDF p.3 |
| Ablation | Table III, PDF p.5; Fig.6, PDF p.6 |
| Limitation / Future Work | §IV-B–D/§V, PDF pp.5–6 |
