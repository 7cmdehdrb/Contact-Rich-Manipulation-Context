# Zero-Shot Transfer of a Tactile-based Continuous Force Control Policy from Simulation to Robot

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B036`
- Authors: Luca Lach; Robert Haschke; Davide Tateo; Jan Peters; Helge Ritter; Júlia Borràs; Carme Torras
- Year: 2024
- Venue: IEEE/RSJ IROS 2024, 725–732
- DOI / arXiv: 10.1109/IROS58592.2024.10802386 / Not stated
- PDF version: Publisher PDF
- Version note: 선택 범위 내 다른 버전 없음
- Page count: 8
- SHA-256: `0a6faf3649135e59037c359ec6c4e82f0869da075c10d0b895f26920c18f5854`
- PDF filename: `Lach 등 - 2024 - Zero-Shot Transfer of a Tactile-based Continuous Force Control Policy from Simulation to Robot.pdf`
- 읽은 범위: PDF pp.1–8 전체(본문·실험·결론·참고문헌), Fig.6/7 및 Table II p.6 렌더 확인. 별도 부록 없음.
- 근거: 이번 배치의 PDF 원문에서 새로 분석했다. 기존 상세 노트는 재사용하지 않았다. 아래 페이지는 PDF 1-based page다.

## 2. Relevance to This Review

**Relevant**. 두 손가락의 연속 normal-force와 position/history만으로 unknown object compliance 및 offset에 대응하는 force-control policy다. 힘의 크기를 보존하는 scalar tactile, binary contact-memory, proprioception의 역할을 구분할 수 있다. Reward의 object velocity와 실행 입력도 명확히 분리된다.

Screening 위치: Abstract, p.1; §IV-A–C, pp.4–5.

## 3. Task

Parallel-jaw grasp의 두 normal force를 goal에 맞추면서 물체의 lateral displacement를 줄인다. Object를 처음부터 두 finger 사이에 놓으며 자유로운 object seeking/pose tracking task는 아니다. 10개 실물 object에서 6초 force-control trials를 평가한다. (§III, pp.2–3; §V, pp.5–7)

## 4. Method

### 4.1. Overall Pipeline

Finger force + q + goal error + previous action/contact memory (3 steps) → PPO → contact-state inductive bias → finger position targets → position controllers. (§IV, pp.4–5)

### 4.2. Observation

Actor는 두 손가락의 local force/position 관측을 받는다. Object velocity는 reward에만 사용한다. Critic 입력은 별도 명시가 없다. (§IV-A/C, pp.4–5)

### 4.3. Action

각 finger의 normalized action을 ±0.003 m의 position increment로 변환한다. 먼저 접촉한 finger를 느리게 하는 inductive-bias scaling을 거친 command와 actor action을 구분한다. (§III-A/IV-B, pp.2,4)

### 4.4. Controller

TIAGo parallel-jaw position control, 25 Hz. 한 finger만 접촉한 상태의 action scale은 0.1이며 양쪽 contact 후에는 force error에 따라 조절한다. (§III/IV-B, pp.2–4)

### 4.5. Learning / Optimization Method

MuJoCo에서 PPO 4M steps, MLP 2×50 ReLU. Force tracking, object movement penalty, action smoothness를 조합한다. Object width/offset/contact softness, actuator and force scaling randomization 및 curriculum을 사용한다. (§III-C–V, pp.3–5)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | No object pose measurement in actor | No | Initial placement between fingers is experimental condition; q is finger position. 근거: §III–IV, pp.2–5 |
| Orientation | 미제공 | No object orientation input | No | No orientation estimator. 근거: §IV-A, p.4 |
| Shape / Geometry | 미제공 | No geometry feature input; width randomized in simulator | No runtime update | Training width is not actor observation. 근거: §III-C/IV-D, pp.3–5 |
| Physical Parameters | 미제공 | Actor does not receive stiffness or object parameters | No | Identified gripper parameters and simulated stiffness/force scaling are controller/training settings. 근거: §III-C, pp.3–4; §IV-A/D, pp.4–5 |

## 6. Missing Object Information and Compensation

Unknown object stiffness → short force/position history → compliance에 맞춘 force-control action(저자 설명). Unknown lateral offset → had-contact flag와 contact-conditioned scaling → 먼저 닿은 finger가 물체를 밀지 않도록 감속. Object velocity GT → training penalty → 실행 시 velocity sensing 없이 object movement를 억제하도록 학습. (§IV, pp.4–5)

## 7. Tactile

### 7.1. Raw Sensor

각 손가락에 하나의 load-cell 기반 normal-force sensor. 두 scalar force를 25 Hz policy에 사용한다. (§III, pp.2–3; §IV-A, p.4)

### 7.2. Preprocessing

Force error와 noise를 포함하고, force threshold로 contact c를 구해 persistent had-contact h=c∨h_previous를 만든다. k=3 observation stack. Threshold 수치는 미명시. (§IV-A, p.4)

### 7.3. Policy Representation

손가락별 position q, force f, goal-minus-measured force Δf, previous action, had-contact flag를 함께 입력한다. (§IV-A, p.4)

### 7.4. Retained Information

Finger별 연속 normal-force 크기, goal error, contact 발생 기억을 남긴다. Binary flag가 추가되더라도 force amplitude 자체는 제거하지 않는다. (§IV-A, p.4)

### 7.5. Removed / Unavailable Information

Contact locality/patch/shear는 이 scalar normal-force sensor 입력에 없다. 이는 연속 force를 binary로 바꾸어 소실시킨 정보가 아니라 원래 측정하지 않는 정보다. (§III/IV-A, pp.2–4)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Tactile로 명명한 두 finger load-cell normal force와 동일하다. 손목 6축 F/T는 사용하지 않는다. (§III, pp.2–3)

### 8.2. Representation

각 손가락의 scalar normal force, goal error 및 thresholded contact memory. (§IV-A, p.4)

### 8.3. Role

Policy feedback, contact-conditioned action scaling, force-error reward. Object contact location 추정용 wrench가 아니다. (§IV-A–C, pp.4–5)

### 8.4. Required Assumptions

물체가 두 손가락 사이에서 시작한다. Finger force와 position을 측정하며 simulation-to-real에는 actuator identification 및 contact/randomization 모델을 이용한다. (§III–IV, pp.2–5)

### 8.5. Reported Limitation / Ambiguity

Light sponge의 첫 접촉을 sensor가 놓쳐 object가 이동할 수 있다. Sensor hysteresis가 simulator에 없음을 논의한다. Multiple-contact net-wrench ambiguity는 직접 다루지 않는다. (§V, p.7)

## 9. Other Observations

Vision/object state estimator는 없다. Finger q는 robot state이며 object pose가 아니다. Previous action, force goal, persistent contact flag, 3-frame observation history를 이용한다. (§IV-A, p.4)

## 10. Tactile–Other Modality Relationship

Tactile force와 proprioception/history를 함께 사용한다. Wrist F/T와 tactile의 독립 modality 조합이 아니라 finger-force 자체가 tactile다. History의 stiffness 역할은 저자 설명이며 별도 history ablation은 없다. Contact-state inductive bias와 training randomization은 비교 실험이 있다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Actor | No object GT | Finger q, normal force/error, previous action, had-contact flag; 3-step stack | 실행에 센서 관측과 force goal 필요 | §IV-A, p.4 |
| Critic | 미명시 | PPO 사용은 명시; critic-specific observation/privilege는 미명시 | PPO library 사용만으로 symmetric/asymmetric를 단정하지 않음 | §V, p.5 |
| Reward | Yes | Force-error reward + simulator object lateral velocity penalty + action smoothness | Object velocity는 학습 reward에 사용; actor에는 없음 | §IV-C Eq.(4)–(7), pp.4–5 |
| Termination | 미명시 (object GT); fixed horizon | Episode 150 steps | Success GT termination은 보고하지 않음 | §V, p.5 |
| Curriculum | Yes: simulator settings | Object width/offset sampling range, object velocity penalty weight/threshold annealing | 학습 전용; runtime true stiffness/pose 입력이 아님 | §IV-D, p.5 |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Inductive bias 및 randomization의 실물 기여 | Controlled comparison; Input/action architecture ablation | Proposed vs baseline vs NoIB vs NoRAND; 10 objects ×20 trials ×4 methods | Mean force rewards 104±13/97±12/88±20/64±25; movement 1.6±0.9/1.6±0.9/2.6±0.9/2.5±1.0 mm. Mug movement는 누락이며 0이 아님. | §V, pp.6–7; Table II/Fig.7, p.6 |
| Object velocity penalty와 curriculum | Controlled comparison | NoPEN, NoCURR, NoIB, NoRAND simulation variants | NoPEN은 force tracking은 좋지만 object movement 증가; NoCURR는 접촉하지 않는 해에 머뭄. Fig.6 caption은 200 trials/policy, 본문은 2000으로 수가 불일치한다. | §V, pp.5–6; Fig.6 |
| 3-step history의 stiffness 정보 역할 | Author explanation only | History를 포함한 policy; history 제거 비교 없음 | 저자가 short history로 stiffness를 추정하도록 한다고 명시. 독립 ablation으로 필요성을 입증하지 않음. | §IV-A, p.4 |
| 작은 force와 compliance 대응 | Controlled comparison; Failure analysis | Mug/plush target 0.2/0.5/0.7 N; light sponge behavior | Soft/small-force 조건에서 baseline 대비 이점을 보고하나 very light sponge는 first contact miss와 hysteresis 영향이 남음. | §V, pp.6–7; Fig.7/Table II |

## 13. Author-stated Limitations

Very light sponge에서 첫 접촉을 감지하기 전에 이동할 수 있고 sensor hysteresis가 simulator에서 모델링되지 않았다. 실물 displacement는 millimeter paper로 읽어 simulation보다 정밀하지 않다. Force reward는 contact duration/width/compliance 영향을 받아 object 사이 직접 비교에 한계가 있다고 설명한다. (§V, pp.6–7)

## 14. Author-stated Future Work

Continuous grasp force control을 더 복잡한 DRL task의 일부로 통합하는 방향을 제시한다. (§VI, p.7)

## 15. Review-relevant Findings

- Force amplitude를 보존하는 두 scalar tactile와 binary contact-memory를 함께 쓴다.
- Current object pose/shape/stiffness는 actor에 없다.
- 3-step history의 stiffness 추정 역할을 명시한다.
- Object velocity는 reward에만 사용한다.
- Tactile+손목 F/T 결합 실험은 아니다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / history | §IV-A, p.4 |
| Object conditions / sim parameters | §III, pp.2–4 |
| Action / controller | §IV-B, p.4 |
| Reward / curriculum | §IV-C/D, pp.4–5 |
| Critic | §V p.5: explicit input 미명시 |
| Ablation / real trials | §V, pp.5–7; Table II/Fig.6–7 |
| Limitations / future | §V–VI, pp.6–7 |
