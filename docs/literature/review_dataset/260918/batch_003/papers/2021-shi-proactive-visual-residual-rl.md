# Proactive Action Visual Residual Reinforcement Learning for Contact-Rich Tasks Using a Torque-Controlled Robot

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B074`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Yunlei Shi; Zhaopeng Chen; Hongxu Liu; Sebastian Riedel; Chunhui Gao; Qian Feng; Jun Deng; Jianwei Zhang
- Year: 2021
- Venue: 2021 IEEE International Conference on Robotics and Automation (ICRA)
- DOI / arXiv: 10.1109/ICRA48506.2021.9561162 / Not stated
- PDF version: IEEE publisher version
- Page count: 7
- SHA-256: `238ead5a79df6f75a2c9f563e98891ce47d8af2d1b3f772b31b2efc28a73129f`
- PDF filename: Shi 등 - 2021 - Proactive Action Visual Residual Reinforcement Learning for Contact-Rich Tasks Using a Torque-Contro.pdf
- 확인 범위: PDF pp.1–7 전체; policy/controller, state/action/reward, Tables I–II, Conclusion/Future Work 렌더 확인.

## 2. Relevance to This Review

`Relevant`

Eye-in-hand vision과 joint-torque-derived 6D force/moment를 역할 분담해 RAM insertion을 수행하고, force를 ternary contact state로 축약한다. Vision/force/active probing ablation이 있어 reduced contact information을 pose tracking과 investigative action이 어떻게 보완하는지 직접 분석할 수 있다.

## 3. Task

Franka가 이미 gripper로 잡은 RAM을 eye-in-hand camera로 slot에 정렬하고 tight slot에 삽입한다. 목표는 object와 goal pose의 거리, 특히 z 방향을 줄여 완전 삽입하는 것이다. Contact state가 ambiguous하면 짧은 25 N probing action으로 contact를 드러낸다. [§III–V, pp.2–5]

## 4. Method

### 4.1. Overall Pipeline

RGB-D target/current features → ICP-based relative 6D pose error → hand-designed PBVS/P controller; joint-torque controller가 추정한 6D external force/moment → threshold/ternary contact state → tabular Q-learning residual action; 두 action을 weighted sum → trajectory generator → Cartesian impedance control → joint torque. [Figs.3–4/§IV–V, pp.3–5]

### 4.2. Observation

Visual fixed policy는 target/current image feature의 translation+angle-axis error를 받는다. RL policy state는 Franka controller가 추정한 EE-frame $F_x,F_y,F_z,M_x,M_y,M_z$를 threshold해 -1/0/+1로 축약한 contact state다. Belief가 불명확하면 investigative force action 후 state를 다시 읽는다. [§IV/§V-A.3, pp.3–5]

### 4.3. Action

RL은 ±Cartesian movement 후보 중 실제로 positional discrete movements를 사용하고, visual fixed action과 weight $\alpha$로 합친다. Investigative action은 EE z 방향 25 N을 1 s 적용하며 25 N 또는 3 mm에서 stop한다. [§V-A.1, p.5]

### 4.4. Controller

Agent 0.5–2 Hz → Cartesian trajectory generator/interpolator → 1000 Hz Cartesian impedance control → joint torque. Translational stiffness 3000 N/m, rotational 300 Nm/rad. [Fig.3/§IV-B/§V-B, pp.3–5]

### 4.5. Learning / Optimization Method

실물에서 tabular Q-learning contact residual policy를 500 episodes 학습한다. Visual PBVS/P-controller는 fixed policy이고, residual action과 0.5 weight로 결합한다. Actor–critic 구조는 아니다. [§IV-A/§V–VI, pp.4–6]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Eye-in-hand RGB-D target/current feature registration의 relative translation | 0.5–2 Hz visual policy update | Goal/reference image와 current image feature를 ICP로 비교한다. [§III–VI, PDF pp.3–6] |
| Orientation | Tracking | ICP rotation에서 angle-axis error $\theta u$ | 0.5–2 Hz 갱신 | Goal orientation과 current relative orientation을 분리한다. [§III–VI, PDF pp.3–6] |
| Shape / Geometry | 기타 | Teach-mode target image/features의 implicit local geometry | Reference는 episode 전 고정; current features 갱신 | Explicit CAD/mesh/dimensions/category input은 없다. [§III-B/§IV-A, pp.3–4] |
| Physical Parameters | 미제공 | RAM/slot friction, stiffness parameter input 없음 | 해당 없음 | Controller stiffness는 robot parameter이고 object property가 아니다. [§III–V pp.2–5] |

## 6. Missing Object Information and Compensation

Object physical parameters/precise contact state 미제공 → joint-torque-derived force/moment threshold states → stuck/contact direction을 구별해 residual action을 선택한다.

Thresholded contact state가 noise/model error로 불명확 → 25 N investigative action → larger force/moment response로 state observability를 높인다.

Vision은 global/relative pose error를 계속 갱신하고 force state는 occlusion/contact에서 local correction을 제공한다. [§III-B/§IV–V, pp.3–5]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§III–V, pp.3–5]

### 7.2. Preprocessing

사용하지 않음. [§III–V, pp.3–5]

### 7.3. Policy Representation

사용하지 않음. [§III–V, pp.3–5]

### 7.4. Retained Information

사용하지 않음. [§III–V, pp.3–5]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§III–V, pp.3–5]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Franka joint torque/proprioceptive controller가 EE-frame external force와 moment를 추정한다. Dedicated wrist F/T sensor는 아니다. [Fig.3/§V-A.3, pp.3,5]

### 8.2. Representation

Raw estimated 6D $[F_x,F_y,F_z,M_x,M_y,M_z]$를 $|F|>4$ N 또는 $|M|>0.4$ Nm threshold로 componentwise -1/0/+1 contact state로 축약한다. [§V-A.3, p.5]

### 8.3. Role

Tabular Q-learning state, contact/stuck detection, residual Cartesian correction. Investigative force action은 ambiguous state를 더 observable하게 만든다. [§IV-A.2/§V-A, pp.4–5]

### 8.4. Required Assumptions

Joint-torque dynamics model이 external wrench를 추정할 수 있고, RAM–slot contact가 EE wrench에 충분히 나타나며 fixed thresholds가 contact sign/state를 구별한다. [§III-A/§V-A.3, pp.2–5]

### 8.5. Reported Limitation / Ambiguity

Noise/model error 때문에 작은 contact moment는 불명확해 POMDP가 된다. Ternary threshold는 continuous magnitude와 contact locality/patch를 버리고, active 25 N probing이 추가로 필요하다. [§III-A.2/§IV-A.2, pp.3–4]

## 9. Other Observations

Vision은 eye-in-hand RGB-D PBVS로 current-to-goal transform을 갱신한다. Robot proprioception은 joint torque/pose와 impedance control에 사용된다. History/recurrent state는 없고 tabular current state/action loop다. Goal image와 current object pose는 구분된다. [§III-B/§IV–V, pp.3–5]

## 10. Tactile–Other Modality Relationship

Vision은 free-space/rough and accurate pose alignment를, force/moment는 contact/stuck state와 last-mile recovery를 담당한다. No-vision와 no-RL ablation이 각각 46%와 56%인 반면 full method 89.5%여서 두 branch의 역할을 비교한다. 다만 haptic representation은 spatial tactile가 아니라 joint-wrench ternary state다. [§VI/Table I, p.6]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | Tabular Q policy uses runtime ternary external force/moment state | Actor network 없음; real sensing만 사용. [§IV-A/§V-A, pp.4–5] |
| Critic | Not applicable | Tabular Q-learning | Asymmetric critic 없음. [§IV-A, p.4] |
| Reward | No simulator GT | Current/target image pose error, step penalty, success/failure | 실물 visual/task condition으로 계산; simulator GT 사용 없음. [§V-A.2, p.5] |
| Termination | No simulator GT | Success, failure, step limit | 실물 task 판정. [§V-A–B/§VI, pp.5–6] |
| Curriculum | No | No curriculum | Formal curriculum 없음. [§V–VI, pp.5–6] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Vision과 force residual의 결합 필요 | Sensor/component ablation | No vision; no RL policy; random RL; no investigative action; full | Success: 46%, 56%, 38.5%, 33%, full 89.5% (200 trials each). | §V-B/§VI; PDF p.6 ; Table I |
| Investigative force action이 ambiguous contact state를 보완 | Input/action ablation | No investigative action vs full | 33% vs 89.5%; probing은 25 N/1 s로 detectable moment를 만든다. | §IV-A.2/§VI; PDF pp.4,6 ; Table I ; Fig.5 |
| Vision이 moved-target variation에 기여 | Controlled comparison | Fixed vs moved motherboard; teaching/spiral/vision baselines | Non-vision baselines moved motherboard 0/20, vision baselines 81/100·88/100, full 100/100. | §V-B/§VI; PDF p.6 ; Table II |
| Force policy가 visual last-mile error/sticking을 보완 | Failure analysis | No RL/vision-only branch vs full | No-RL policy는 short side에 걸려 56%; 저자는 visual alone이 friction/accuracy 때문에 마지막 거리 극복에 실패한다고 관찰. | §VI; PDF p.6 ; Table I |

## 13. Author-stated Limitations

Traditional controller parameters 때문에 setup이 느리고 end-to-end가 아니다. Generalized test가 제한적이며 discrete actions, action execution error, maximum-step dependence 때문에 성공을 보장하지 않는다. Contact state는 torque model error/noise로 partially observable하다. [§III-A/§VI–VII, pp.3,6]

## 14. Author-stated Future Work

End-to-end training, 다른 parts/robot manipulators로 generalization, skill-as-a-service의 짧은 setup, discrete와 continuous action-space learning 비교를 제시한다. [§VII, p.6]

## 15. Review-relevant Findings

- Vision은 numeric relative current-to-goal pose를 실행 중 계속 갱신한다.
- Haptic state는 dedicated tactile/F/T가 아니라 joint-torque-derived 6D wrench를 ternary threshold한 표현이다.
- 축약 wrench는 contact magnitude/locality를 버리며 25 N proactive probe로 observability를 높인다.
- No-vision/no-force-policy/no-probing ablation이 각 추가 정보의 필요성을 직접 비교한다.
- Training과 execution이 실물이며 asymmetric critic/simulator GT는 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / pipeline | Fig.3/§IV pp.3–4 |
| Object pose / vision | §III-B/§IV-A pp.3–4 |
| Force state | §V-A.3 p.5 |
| Action / controller | §IV-B/§V-A p.5 |
| Reward | §V-A.2 p.5 |
| Evidence | Tables I–II p.6 |
| Limitations / Future | §VII p.6 |
| Tactile | Dedicated tactile 사용 안 함 |
