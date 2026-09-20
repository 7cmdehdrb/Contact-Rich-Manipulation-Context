# Learning Force Control for Legged Manipulation

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B069`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Tifanny Portela; Gabriel B. Margolis; Yandong Ji; Pulkit Agrawal
- Year: 2024
- Venue: 2024 IEEE International Conference on Robotics and Automation (ICRA)
- DOI / arXiv: 10.1109/ICRA57147.2024.10611066 / Not stated
- PDF version: IEEE publisher version
- Page count: 7
- SHA-256: `e1f88d0516e488be20e8800153fd69bd00e0df19d89bc033b2da756f2e83fa64`
- PDF filename: Portela 등 - 2024 - Learning Force Control for Legged Manipulation.pdf
- 확인 범위: PDF pp.1–7 전체; observation/privileged architecture, simulation/real force results, Discussion 렌더 확인.

## 2. Relevance to This Review

`Partially Relevant`

Blind sweeping과 task는 다르지만, end-effector F/T 없이 proprioception history와 privileged-state estimator로 external force를 추정하고 force-control policy를 구성한다. 실행 센서와 training-only force GT/critic state를 분리해 object/contact 정보 부족을 보완하는 사례로 유용하다.

## 3. Task

Unitree B1 quadruped와 Z1 arm이 mobile reaching/locomotion과 end-effector force tracking을 하나의 policy로 수행한다. Zero-force command에서는 compliant mode, 큰 force command에서는 whole-body pulling/lifting을 구현한다. [§III–V, pp.3–6]

## 4. Method

### 4.1. Overall Pipeline

Joint encoders + body IMU + 30-step observation/command history → supervised state estimator가 body velocity, gripper position, external force를 추정 → actor가 history와 estimated privileged state를 입력 → 17 joint position targets → joint PD. Training critic은 true privileged state를 받는다. [§IV-A–B, p.3]

### 4.2. Observation

Runtime base observation은 projected gravity, feet clocks, 17 joint positions/velocities, current/previous actions이며 30-step history와 force/EEF/base commands를 concat한다. Actor는 estimator의 body velocity, gripper body-frame position, external force estimate를 추가로 받는다. End-effector F/T는 없다. [§IV-A–C, pp.3–4]

### 4.3. Action

17차원 normalized action이 B1의 12 leg joints와 Z1 arm의 앞 5 joints에 대한 joint-position target을 생성한다. [§IV-A, p.3]

### 4.4. Controller

Target은 $0.25a_t+q_{def}$로 변환되어 각 joint의 low-level PD controller가 추종한다. Arm의 마지막 roll/gripper opening joints는 teleoperation command로 직접 제어된다. [§III/§IV-A, p.3]

### 4.5. Learning / Optimization Method

4096 parallel Isaac Gym environments에서 PPO로 actor/critic을 학습하고, state estimator는 privileged state regression loss로 concurrent supervised training한다. Critic만 true body velocity, gripper position, external force를 받는다. [§IV-B, p.3]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Manipulated object current position은 policy input이 아님 | 해당 없음 | Gripper position은 object pose가 아니다. [§III–VI, PDF pp.3–6] |
| Orientation | 미제공 | Manipulated object orientation input 없음 | 해당 없음 | Body projected gravity와 arm state만 사용한다. [§III–VI, PDF pp.3–6] |
| Shape / Geometry | 미제공 | Object mesh/CAD/dimension/category input 없음 | 해당 없음 | Task objects are qualitative evaluation setups. [§III–VI, PDF pp.3–6] |
| Physical Parameters | 미제공 | Object mass/friction을 policy input으로 제공하지 않음 | 해당 없음 | Payload weight compensation은 command로 주어질 수 있으나 object parameter vector는 아니다. [§V-B p.5] |

## 6. Missing Object Information and Compensation

Current object state/geometry 미제공 → proprioception/IMU/action/command history + learned external-force/gripper-state estimator → compliant interaction과 commanded force tracking을 수행한다.

End-effector F/T 미제공 → simulation privileged external force를 supervised target으로 삼은 estimator가 30-step history에서 force를 복원 → actor force feedback으로 사용한다. 저자들은 실물에서 estimator error가 tracking error보다 크고 policy가 estimate를 일부 무시하는 것으로 보인다고 보고한다. [§IV-B p.3; §V-A p.5]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§III–VI, pp.3–6]

### 7.2. Preprocessing

사용하지 않음. [§III–VI, pp.3–6]

### 7.3. Policy Representation

사용하지 않음. [§III–VI, pp.3–6]

### 7.4. Retained Information

사용하지 않음. [§III–VI, pp.3–6]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§III–VI, pp.3–6]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

실행 입력에 wrist/end-effector F/T가 없다. 외력은 joint encoder와 body IMU를 포함한 observation history에서 neural estimator가 추정한다. Dynamometer는 평가 reference일 뿐 policy sensor가 아니다. [§III–IV p.3; §V-A p.5]

### 8.2. Representation

Estimated external gripper force vector $\hat F_e\in\mathbb{R}^3$와 desired force command $F^{cmd}\in\mathbb{R}^3$ (world frame). [§IV-B–D, pp.3–4]

### 8.3. Role

Actor state estimate와 force-tracking command/reward에 사용되어 compliance, pulling, lifting을 조절한다. [§IV-C–D pp.3–4; §V pp.4–6]

### 8.4. Required Assumptions

Simulator의 soft PD potential field로 force task를 만들고 estimator가 sim-trained privileged force를 real history에서 재구성할 수 있어야 한다. Known robot proprioception/IMU와 sim-to-real transfer가 필요하다. [§IV-B–D, pp.3–4]

### 8.5. Reported Limitation / Ambiguity

Estimator가 실제 force를 overshoot하며 moderate sim-to-real gap이 있다. Tracking이 비교적 유지되어 policy가 estimated force feedback을 일부 무시할 수 있다고 저자가 해석한다. 외력의 spatial contact location은 추정하지 않는다. [§V-A p.5; §VI p.6]

## 9. Other Observations

Proprioception은 17 joint position/velocity, projected gravity, feet clock, current/previous actions이다. 30-step observation·command history를 사용한다. Commands는 desired EEF force, EEF position, base velocity, force/position mode를 포함한다. Vision은 없다. [§IV-A–C, pp.3–4]

## 10. Tactile–Other Modality Relationship

Tactile/F/T를 사용하지 않고 proprioceptive history와 learned state estimator로 external force를 간접 복원한다. 따라서 연속 force magnitude/direction은 얻지만 contact location/patch/object state는 제공하지 않는다. 이 방법의 force estimate는 critic supervision과 simulation force GT에 의존한다. [§IV-B, p.3]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | Observation/command history + estimated body velocity, gripper position, external force | 실행에서 true privileged state를 estimator prediction으로 대체. [§IV-B, p.3] |
| Critic | Yes | True body velocity, body-frame gripper position, external gripper force | Simulation-only privileged state. [§IV-B, p.3] |
| Reward | Yes | Actual EEF position/force, locomotion/contact/safety terms | Simulator state로 tracking objective를 계산. [§IV-C–E/Table I, pp.3–4] |
| Termination | Yes | Gripper collision and body height below 0.3 m | Training failure termination. [§IV-B, p.3] |
| Curriculum | Not stated | Not stated | Task mode/commands를 episode 중 random resampling하지만 formal curriculum은 미명시. [§IV-C, p.3] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Learned force control/estimation accuracy | Controlled evaluation | 1000 simulated setpoints across workspace and 0–70 N real dynamometer trials | Simulation z-force tracking error 약 5 N at low targets, <10 N over range; real tracking 5–10 N. | §V-A; PDF pp.4–5 ; Figs.3–4 |
| Estimator는 F/T 없이 external force를 제공 | Controlled comparison | Estimated vs actual force | Estimation error가 tracking error 이상이고 hardware에서 overshoot; policy가 estimate를 일부 무시할 가능성을 저자가 언급. | §V-A; PDF p.5 ; Fig.4D |
| Whole-body coordination의 이점 | Controlled comparison | Fixed arm workspace vs whole-body policy | Workspace convex-hull volume 0.81→1.29 m³(+59%); pulling 90 N으로 arm rated payload 36 N 초과. | §V-A/C; PDF pp.5–6 ; Figs.4–5 |
| F/T 없는 force mode의 task utility | Author demonstration only | Zero-force compliance; payloads 0/2/4/6 kg | 4 kg까지 gravity compensation과 multi-axis compliance, 6 kg에서는 compliance 저하. | §V-B; PDF pp.5–6 ; Fig.4F |

## 13. Author-stated Limitations

Position tracking 약 5 cm, force tracking 약 5 N은 high-precision task에 부족할 수 있고 그 한계가 hardware/optimization/architecture 중 어디서 오는지 미확인이다. Force estimator는 real에서 overshoot하고 sim-to-real gap이 있다. [§V-A/§VI, pp.5–6]

## 14. Author-stated Future Work

Kinesthetic demonstrations에서 compliant/forceful behavior를 autonomous imitation learning으로 학습하고, kinematic/dynamic models를 policy에 통합해 더 나은 정확도를 얻는 방향을 제시한다. [§VI, p.6]

## 15. Review-relevant Findings

- Runtime wrist F/T 없이 joint/IMU/action history에서 external force를 추정한다.
- Actor는 estimated privileged state를, critic은 true external force/body/gripper state를 받는다.
- Current object pose/shape는 policy에 제공되지 않는다.
- Force magnitude/direction을 추적하지만 contact locality는 복원하지 않는다.
- 실물 force estimate의 bias에도 force tracking은 유지되어 estimate 의존성이 명확하지 않다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / action | §IV-A p.3 |
| Privileged actor/critic | §IV-B p.3 |
| Force task / reward | §IV-C–E pp.3–4 |
| Object pose | 제공하지 않음; §IV-A–C |
| Tactile / F/T | 실행 tactile/F/T 없음; §III–IV p.3 |
| Evidence | §V/Figs.3–5 pp.4–6 |
| Limitation / Future | §VI p.6 |
| Termination | §IV-B p.3 |
