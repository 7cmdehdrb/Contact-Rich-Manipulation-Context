# Rotating without Seeing: Towards In-hand Dexterity through Touch

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B092`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Zhao-Heng Yin; Binghao Huang; Yuzhe Qin; Qifeng Chen; Xiaolong Wang
- Year: 2023
- Venue: arXiv preprint
- DOI / arXiv: Not stated / 2303.10880v4
- PDF version: arXiv v4 (27 March 2023)
- Page count: 15
- SHA-256: `7be48b3f9573efaf8d53b2abf94f23ae16532d6afa2408bc803bc14d4286a5ba`
- PDF filename: Yin 등 - 2023 - Rotating without Seeing Towards In-hand Dexterity through Touch.pdf
- 확인 범위: PDF pp.1–15 전체(본문, conclusion, appendices); hardware/thresholding, actor/value observations, reward/domain randomization, simulation/real ablations, shape probe와 failure/future를 확인하고 Figures 3/6/9 및 Tables I–V 렌더 검토.

## 2. Relevance to This Review

`Relevant`

Vision 없이 16개 FSR를 binary contact로 축약하고 proprioception, previous target, 4-frame history와 결합해 in-hand rotation을 수행한다. Binary/continuous/no-sensor, palm/fingertip sensor ablation과 asymmetric critic/object-GT reward 구조를 모두 제공하여 축약 tactile 보완과 training privileged information을 직접 비교할 수 있다.

## 3. Task

16-DoF Allegro hand가 palm에 놓인 object를 vision 없이 지정된 x/y/z rotation axis 둘레로 계속 회전하면서 떨어뜨리지 않는다. Training에서 보지 않은 real objects에도 zero-shot transfer하고, tactile contact pattern만으로 object position/interaction과 shape-related information을 얻을 수 있는지 평가한다. [§III-C/§V, PDF pp.3,5–10]

## 4. Method

### 4.1. Overall Pipeline

16 FSR analog voltages → thresholded 16-bit contact vector; simulation은 sensor-link net contact force norm을 0.01 N threshold → joint positions + previous target + goal rotation axis와 결합 → current+3 historical states stack → PPO actor → 16-D relative joint target increment → EMA → 10 Hz joint PD controller. Training value network은 contact forces, GT object pose와 physical properties를 추가로 받는다. [§III-A–B/§IV-A, pp.3–5]

### 4.2. Observation

Actor state는 Allegro joint positions $q_t ∈ R^{16}$, binary tactile $o_t ∈ {0,1}^{16}$, previous joint position target q-tilde_t ∈ R^{16}, desired rotation axis $k ∈ S^2$이며 current state와 세 historical states를 stack한다. Current object position/orientation/shape는 actor에 없다. [§IV-A, p.4]

### 4.3. Action

Actor가 16-D relative joint target command $a_t$를 출력하고 previous target에 더한다. Target을 EMA로 smoothing해 next joint target을 만든다. [§IV-A/Fig.3, p.4]

### 4.4. Controller

EMA-smoothed target joint positions을 10 Hz PD controller가 추종한다. Object는 episode 시작 전에 palm에 배치되지만 pose vector를 actor에 제공하지 않는다. [§IV-A, pp.4–5]

### 4.5. Learning / Optimization Method

IsaacGym에서 PPO와 domain randomization으로 학습한다. Actor는 4-frame sensor/proprioception stack만 받고, asymmetric value network은 per-link continuous contact forces, object GT pose 및 physical parameters를 privileged input으로 받는다. Reward는 GT object rotation, velocity, fall state, controller work/torque와 fingertip-object distance로 계산한다. [§IV-A, pp.4–5; Appendix A–C, pp.14–15]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Actor에 current object position vector가 없음 | 해당 없음 | Palm/hand contact pattern이 approximate in-hand position을 암시한다고 저자가 설명한다. [§III-D p.3; §IV-A p.4] |
| Orientation | 미제공 | Actor에 current object orientation이 없음 | 해당 없음 | Desired rotation axis는 goal/task information이며 current object orientation과 구분한다. [§IV-A p.4] |
| Shape / Geometry | 미제공 | Actor에 mesh/CAD/dimension/category를 제공하지 않음 | 해당 없음 | Separate temporal-CNN probe는 tactile rollout이 shape reconstruction을 개선함을 보이지만 actor에 shape estimate를 넣지는 않는다. [§V-H pp.8–9] |
| Physical Parameters | 미제공 | Actor에 mass/friction/scale을 제공하지 않음 | 해당 없음 | Physical parameters는 value network과 simulator randomization에만 사용한다. [§IV-A p.5; Appendix B p.14] |

## 6. Missing Object Information and Compensation

Current object pose/shape/physical parameters 미제공 → 16-region binary contact pattern + hand joint/previous-target state + four-frame history → approximate in-hand position, critical finger contact와 motion-dependent object state를 policy가 간접적으로 반영한다.

Continuous FSR magnitude의 nonlinear/noisy sim-to-real mismatch → thresholded binary contact → force magnitude는 제거하지만 contact presence와 hand-wide locality를 안정적으로 보존한다. Continuous sensor baseline과 real-robot 비교에서 binary가 더 높은 generalization을 보인다. [§III-A/D pp.3–4; §V-E pp.7–8]

## 7. Tactile

### 7.1. Raw Sensor

Palm, finger links, fingertips에 부착한 16 Force-Sensing Resistors. STM32F가 analog voltage를 읽어 host에 전달한다. Simulation은 각 sensor link의 net contact force vector를 사용한다. [§III-A–B, p.3]

### 7.2. Preprocessing

Real FSR voltage를 selected threshold theta_th로 binarize한다. Simulation은 net force norm |F|을 threshold 0.01 N으로 binarize하고 real activation behavior와 맞게 조정한다. [§III-A–B, p.3]

### 7.3. Policy Representation

16-D binary contact vector를 joint position, previous target, rotation-axis goal과 결합하고 current+3 prior steps, 즉 약 0.4 s window로 stack한다. [§IV-A p.4; §V-F p.8]

### 7.4. Retained Information

Sensor-region별 contact presence, hand-wide spatial contact pattern, approximate object position/critical contact, 4-step temporal activation sequence를 남긴다. [§III-D pp.3–4; §V-F/H pp.8–9]

### 7.5. Removed / Unavailable Information

Continuous force magnitude, force direction, shear, pressure distribution/local deformation, exact contact point/normal과 explicit object pose/shape는 제거되거나 제공되지 않는다. [§III-A–B p.3]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Policy tactile는 local FSR regions이며 wrist 6-axis F/T나 joint-torque estimated wrench를 사용하지 않는다. Simulation value network만 continuous per-link contact forces를 privileged state로 받는다. [§III-A–B/§IV-A, pp.3,5]

### 8.2. Representation

Actor에는 force norm threshold 결과인 16-bit contact만 있다. Value network에는 per-link continuous contact forces가 추가된다. [§III-B/§IV-A, pp.3,5]

### 8.3. Role

Actor에서는 contact presence/locality와 critical interaction을 제공한다. Training value network의 continuous forces는 value estimation을 쉽게 하는 privileged input이다. [§III-D p.3; §IV-A p.5]

### 8.4. Required Assumptions

Known sensor placement/hand kinematics, threshold calibration과 hand/object contact가 sensor-covered surface에 나타나는 것이 필요하다. Side-link coverage가 부족한 축에서는 failure가 증가한다. [§III-A–D pp.3–4; §V-I p.10]

### 8.5. Reported Limitation / Ambiguity

Binary contact는 load magnitude/direction을 잃고 sparse layout 밖 contact를 보지 못한다. x/y rotations에서 side-link critical contacts coverage 부족이 failure 원인으로 보고된다. [§V-I, p.10]

## 9. Other Observations

Proprioception은 current 16 joint positions와 previous joint-position target이다. Desired rotation axis는 goal이고 current object pose가 아니다. Current+3 historical states가 explicit sensor/action history를 제공한다. Vision, F/T, explicit object-state estimator는 실행에 없다. [§IV-A, p.4]

## 10. Tactile–Other Modality Relationship

Binary tactile는 local contact presence/pattern을, proprioception과 previous target은 hand configuration/control context를, history는 object-contact evolution을 제공한다. 이 조합이 current pose 없이 adaptive rotation을 가능하게 한다. No-sensor baseline은 current-vs-target joint mismatch에서 contact를 간접 추론하지만 성능이 낮다. Wrist F/T와 tactile의 결합은 평가하지 않는다. [§V-B–E, pp.6–8]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | Joint positions; binary tactile; previous joint target; desired rotation axis; 4-frame stack | Current object GT pose/shape/physical parameters가 없다. [§IV-A, p.4] |
| Critic | Yes | Per-link contact forces; object GT pose; physical parameters | Asymmetric value network의 simulation-only privileged observation. [§IV-A, p.5] |
| Reward | Yes | GT object rotation increment/pose, velocity, fall, torque/work and fingertip-object distance | Simulator state/contact quantities로 계산한다. [§IV-A/Eqs.1–2, pp.4–5; Appendix C p.15] |
| Termination | Yes | Object major-axis deviation/fall and episode horizon | Object state 기반 reset/termination을 사용한다. [§IV-A, p.5] |
| Curriculum | Yes | Randomized object shape/size/mass/friction/initial position; PD gains; observation/action noise | Simulation domain/data generation용이며 execution actor input은 아니다. [§IV-A p.5; Appendix B p.14] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Binary tactile improves in-hand rotation and generalization | Sensor ablation | Full sensor vs No-Sensor vs DS-Sensor/disabled tactile in simulation and real | Full sensor has substantially higher rotation and time-to-fall on seen/unseen objects; disabling tactile causes large drops. | §V-C–E; PDF pp.6–8 ; Tables I–III ; Fig.6 |
| Binary representation transfers better than continuous force | Representation ablation | CT-Sensor continuous input vs thresholded binary FSR input on real objects | Continuous sensor can work on some objects but has poorer generalization and high variance; authors attribute this to sim–real force mismatch. | §V-E; PDF pp.7–8 ; Table I |
| Both fingertip and palm tactile regions matter | Sensor ablation | Full vs no-fingertip vs no-palm vs disabled-all tactile | No-fingertip and no-palm performance falls near disabled-sensor baseline; both groups are needed. | §V-G; PDF pp.8–9 ; Table IV |
| Tactile history carries shape-related information | Controlled probe comparison | Temporal-CNN shape reconstruction with full rollout vs tactile channels zeroed | Test shape reconstruction MSE is 0.22 with touch versus 0.45 without touch. | §V-H; PDF p.9 ; Fig.9 |
| Sparse coverage limits rotations requiring side-link contacts | Failure analysis | x/y-axis versus z-axis rotations | x/y performance is lower for some objects; authors link failures to missing side-of-finger-link coverage. | §V-I; PDF p.10 ; Table V |

## 13. Author-stated Limitations

x/y rotation often requires critical side-of-finger-link contacts that the current sparse sensor layout does not cover, causing failures on some objects. Continuous FSR readings are noisy/nonlinear and difficult to align across simulation and real, motivating binary thresholding. Binary representation cannot retain contact-force magnitude/direction. [§III-A p.3; §V-E/I pp.7–10]

## 14. Author-stated Future Work

저자들은 denser contact sensor arrays, 특히 finger-link coverage 확대와 더 다양한 dexterous manipulation tasks로 system을 scale up하는 방향을 명시한다. [§V-I/§VI, p.10]

## 15. Review-relevant Findings

- Actor는 current object pose/shape/physical parameters 없이 binary touch와 proprioception/history를 사용한다.
- 16 FSR continuous readings은 thresholded binary contact로 축약되어 magnitude/direction을 잃는다.
- Palm/finger/fingertip의 spatial contact pattern과 4-frame history가 approximate position과 interaction 변화를 보완한다.
- Desired rotation axis는 goal이며 current object orientation tracking이 아니다.
- Asymmetric critic은 GT object pose, physical parameters와 continuous contact forces를 사용한다.
- Reward/termination도 simulator object state를 사용하며 real deployment actor와 분리된다.
- No-sensor, continuous-vs-binary, sensor-region, shape-probe ablations이 tactile 역할을 뒷받침한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Hardware / raw tactile / threshold | §III-A–B p.3 |
| Tactile information interpretation | §III-D pp.3–4 |
| Actor observation / action / controller | §IV-A/Fig.3 p.4 |
| Reward / privileged critic / randomization | §IV-A pp.4–5; Appendix B–C pp.14–15 |
| Sensor and representation baselines | §V-B–E pp.6–8 |
| Sensor-layout / shape ablations | §V-G–H pp.8–9 |
| Failure / limitation / future | §V-I/§VI p.10 |
