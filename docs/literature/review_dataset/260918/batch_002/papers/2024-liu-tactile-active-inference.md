# Tactile Active Inference Reinforcement Learning for Efficient Robotic Manipulation Skill Acquisition

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B046`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Zihao Liu; Xing Liu; Yizhai Zhang; Zhengxiong Liu; Panfeng Huang
- Year: 2024
- Venue: 2024 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 10884–10889
- DOI / arXiv: 10.1109/IROS58592.2024.10802750 / Not stated
- PDF version: Publisher
- Page count: 6
- SHA-256: `3fbd7187e4c38f2304ea421fe7979f896e82a815fee4f5cd11a811e3f4f7d8fc`
- PDF filename: Liu 등 - 2024 - Tactile Active Inference Reinforcement Learning for Efficient Robotic Manipulation Skill Acquisition.pdf
- 확인 범위: PDF pp.1–6 전체(참고문헌 포함), 별도 Appendix 없음; pp.4–5 그림·수식·결과 그래프 렌더 확인. 외부 코드/영상은 확인하지 않음.

## 2. Relevance to This Review

`Relevant`

고해상도 tactile image를 접촉 중심·강도·optical-flow entropy로 축약하고 로봇/물체 상태와 결합하는 연구다. Sim pushing과 real screwing에서 object 정보 조건이 크게 달라 이를 분리해야 한다. 특히 tactile 없는 AIRL 비교와, nut angle GT 대신 tactile entropy를 reward로 쓰는 구조가 조사 질문에 직접 대응한다.

## 3. Task

시뮬레이션은 UR5가 ball/box를 경사면 아래에서 위의 red goal region으로 미는 task다. 실물은 KUKA iiwa7·BackYard gripper·GelSight mini로 nylon nut를 screw에 회전시키며 하향 shear proxy를 최소화한다. Sim 성공은 물체가 goal region 안에 들어오는 조건이고 real 정량 목표는 optical-flow entropy 감소다. Real nut의 실제 회전각·체결 성공률을 계측한 결과로 해석하지 않는다. [§IV-A–B, Figs.3–4, PDF pp.4–5]

## 4. Method

### 4.1. Overall Pipeline

로봇/물체 상태와 handcrafted tactile feature → state-transition ensemble 및 reward model → 예상 reward + ensemble information gain으로 미래 action sequence 평가 → CEM sampling/planning → 첫 action 실행 → 관측으로 model 갱신. 외재 reward와 내재 curiosity를 결합하는 model-based AIRL이다. [Fig.1; §III-A, PDF pp.2–3]

### 4.2. Observation

Sim의 $o_p$는 manipulator와 object 각각의 position, velocity, posture, angular velocity를 포함한다. Tactile $o_t$는 depth centroid 2성분과 pixel sum 1성분이다. Sim에서 optical flow를 얻지 못하므로 dynamic feature를 제외한다. Real의 $o_p$는 descent height와 rotation angle이며 nut의 GT angle이 아니다. 일반 tactile 정의는 $mu,Sigma,H(x),H(y)$이나 real task에서 policy에 쓰는 전체 feature subset/차원은 별도 미명시다. Reward에는 downward optical-flow entropy가 확실히 쓰인다. [§III-B–IV-B, PDF pp.3–5]

### 4.3. Action

Sim은 forward, left/right, rotation의 3-DoF incremental motion. Real은 EEF를 일정 속도로 하강시키면서 rotation increment만 선택한다. Action bound와 실제 control frequency는 미명시다. [§IV-B, PDF p.5]

### 4.4. Controller

Robot motion command 아래의 IK/servo/impedance 상세, gripper force control law는 미명시다. 고정 하강 속도와 허용 motion axes는 사전 제약이다. CEM은 action distribution을 갱신하고 최적 sequence의 첫 action을 실행한다. [§III-A3/IV-B, PDF pp.3,5]

### 4.5. Learning / Optimization Method

AIRL의 transition ensemble과 reward model을 실제 interaction data로 학습하며 CEM으로 계획한다. 비교 baseline은 SAC와 tactile 없는 origin AIRL이다. Sim은 서로 다른 3 seeds로 평균·분산을 표시한다. Dense reward는 goal 도달 indicator minus object-goal distance, sparse reward는 도달 indicator다. Real은 negative downward optical-flow entropy를 사용한다. Reward curve smoothing은 sim 10 episodes, real 5 episodes이며 actor sensor history 길이가 아니다. [§III-A; §IV-B–C, Eq.(11), PDF pp.2–3,5–6]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Sim: current object position; Real: nut current position 입력 없음 | Sim state 매 step; Real 미제공 | 하나의 pose 조건으로 합치지 않음 [§IV-B, PDF p.5] |
| Orientation | Tracking | Sim: current object posture; Real: nut GT angle 미제공 | Sim state 매 step; Real 미제공 | Real robot rotation angle과 nut GT angle을 구분 [§IV-B, PDF p.5] |
| Shape / Geometry | 미제공 | 별도 mesh/CAD/shape feature 입력 없음 | 없음 | Ball/box와 fixed contact-shape 설정; real screw pitch는 unknown [§III-B/IV-A–B, PDF pp.3–5] |
| Physical Parameters | 미제공 | 정밀 물성 및 real screw pitch 입력 없음 | 없음 | 모델의 명시적 물성 추정 정확도는 평가하지 않음 [§IV-A–B, PDF pp.4–5] |

## 6. Missing Object Information and Compensation

Sim의 global object state만으로 부족한 local contact 정보 → tactile centroid/intensity → contact 변화에 대한 model learning을 보완한다는 저자 설명과 AIRL 대비 안정성 비교가 있다. Real에서 unknown screw pitch와 nut angle GT 부재 → robot height/rotation + tactile dynamic entropy → 하강 중 불일치로 생기는 gel deformation을 줄이는 회전 action과 reward를 구성한다. 정확한 screw pitch/실제 shear force를 추정했다고 주장하지 않는다. [§IV-A–C, PDF pp.4–6]

## 7. Tactile

### 7.1. Raw Sensor

GelSight 계열 optical tactile RGB/gel deformation. Real GelSight mini는 gripper에 장착하며 정확한 sensor 수·해상도는 미명시. Sim PyBullet+TACTO RGB/depth. [§II-A/IV-A, Figs.3–4, PDF pp.1–2,4]

### 7.2. Preprocessing

RGB surface gradient의 Poisson integration으로 depth를 얻고 raw moments에서 centroid와 pixel sum 계산. Lucas–Kanade optical flow의 두 방향 histogram entropy를 dynamic feature로 사용. Sim은 flow 없이 depth feature만 사용. [§III-B/IV-B, Eqs.(7)–(10), PDF pp.3–5]

### 7.3. Policy Representation

Static: centroid 2D + depth sum. General dynamic: H(x), H(y) 두 entropy. Real reward는 −H(y). CNN image reconstruction 대신 handcrafted features 채택. [§III-B/IV-B, PDF pp.3–5]

### 7.4. Retained Information

접촉 중심 위치, deformation intensity proxy, 방향별 flow dispersion/slip tendency. 저자는 entropy를 shear/motion-trend proxy로 해석한다. [§III-B, PDF pp.3–4]

### 7.5. Removed / Unavailable Information

Moments·entropy만 남기므로 상세 contact patch shape와 개별 flow vectors는 policy summary에서 복원되지 않음(표현 구조상 확인). Signed shear force·calibrated force magnitude·full object geometry를 직접 제공하지 않는다. [§III-B, Eqs.(7)–(10), PDF pp.3–4]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [§III-B/IV-A–B, PDF pp.3–5]

### 8.2. Representation

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [§III-B/IV-A–B, PDF pp.3–5]

### 8.3. Role

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [§III-B/IV-A–B, PDF pp.3–5]

### 8.4. Required Assumptions

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [§III-B/IV-A–B, PDF pp.3–5]

### 8.5. Reported Limitation / Ambiguity

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [§III-B/IV-A–B, PDF pp.3–5]

## 9. Other Observations

Proprioception: sim manipulator state; real EEF descent height/rotation. Vision: 외부 scene RGB policy 입력 미명시; sensor 내부 camera는 tactile이다. Goal: sim goal region과 reward distance, 별도 goal observation 여부는 미명시. History: optical flow는 시간 변화 정보를 사용하지만 frame 간격·stack/RNN·previous action 입력은 미명시. Ensemble은 learned state-transition/reward model이며 explicit object pose estimator는 아니다. [§III–IV-B, PDF pp.2–5]

## 10. Tactile–Other Modality Relationship

Tactile 이외에 sim에서는 current object state와 robot state, real에서는 robot motion coordinates가 제공된다. Tactile은 global pose를 대체하기보다 local contact 정보를 추가하며, real reward에서 관측하기 어려운 nut angle 대신 deformation proxy를 쓴다. F/T sensor 병용은 없고 optical-flow entropy를 F/T 측정치와 동일시하지 않는다. [§IV-B–C, PDF p.5]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Sim Yes; real nut GT No | Sim current object position/posture/velocities + robot state + tactile; real robot height/angle + tactile | 본 방법은 CEM planner이며 feed-forward actor가 아님. Sim observation을 실물 센서-only 계약으로 오인하지 않음 [Fig.1; §IV-B, PDF pp.3,5] |
| Critic | Not applicable to proposed planner | Transition ensemble/reward model; 별도 asymmetric critic 없음 | Baseline SAC의 critic input 상세는 미명시 [§III-A/IV-C, PDF pp.2–3,5] |
| Reward | Sim Yes; real No nut angle GT | Goal region membership/object-goal distance; real −H(y) | 배포에는 reward 불필요. Real tactile reward는 shear proxy이며 GT force가 아님 [Eq.(11), PDF p.5] |
| Termination | Not stated | Episode horizon/실패 종료 상세 미명시 | Goal-region reward와 자동 termination을 동일시하지 않음 [§IV, PDF pp.4–6] |
| Curriculum | Not stated | 명시적 curriculum/privileged reset sampling 없음 | Real unknown screw pitch는 task 설정이지 GT 입력이 아님 [§IV-A–C, PDF pp.4–6] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Tactile이 global state의 local-contact 부족을 보완 | Sensor ablation; Author explanation only | Tactile-AIRL vs origin AIRL, dense pushing | Tactile 제거 시 variance가 크고 smoothed reward가 낮다고 설명. Exact final success table 없음 | §IV-C1; PDF p.5 ; Fig.5 |
| Model-based active inference가 sample efficiency를 개선 | Controlled comparison | Tactile-AIRL/origin AIRL vs SAC; dense/sparse rewards | Dense에서 AIRL 계열 약100 episodes, SAC 약1000 episodes. Sparse에서 SAC는 수천 episodes 후에도 학습 실패; 알고리즘 효과와 tactile 효과 분리 필요 | §IV-C1; PDF pp.5–6 ; Figs.5–6 |
| Real entropy reward로 nut 회전 조절을 학습 | Author explanation only | 제안 방법의 real learning curve; 비교군 없음 | 약15 episodes에 수렴한다고 보고. Sampling cost 때문에 real baseline을 실행하지 않음; actual shear force/angle 정량 검증 아님 | §IV-C2; PDF pp.5–6 ; Fig.7 |

## 13. Author-stated Limitations

§III-B는 fixed/regular contact shape 및 single connected depth region의 단순한 경우에 집중한다고 명시한다. Sim optical flow를 얻지 못해 dynamic tactile feature를 쓰지 못한다. Real nut angle GT 취득이 어렵고 sampling cost 때문에 real 비교군을 실행하지 못한다. 별도 Limitation 절은 없다. [§III-B/IV-B–C, PDF pp.3–5]

## 14. Author-stated Future Work

구체적인 후속 연구 항목은 원문에서 확인되지 않음. Conclusion은 broader application의 잠재력을 일반적으로 언급한다. [§V, PDF p.6]

## 15. Review-relevant Findings

- Sim은 current object pose/velocity를 지속 제공하며 tactile-only pushing이 아니다.
- Sim tactile은 centroid와 depth sum이며 real dynamic reward는 flow entropy다.
- Unknown pitch/angle 문제를 calibrated wrench가 아닌 tactile deformation proxy로 다룬다.
- F/T sensor·force–tactile combination ablation은 없다.
- CEM planner의 learned reward model과 RL asymmetric critic을 혼동하지 않는다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / Object pose | §IV-B, PDF p.5 |
| Tactile representation | §III-B, Eqs.(7)–(10), PDF pp.3–4 |
| F/T | 사용하지 않음; §IV-A–B, PDF pp.4–5 |
| Reward | Eq.(11), PDF p.5 |
| Critic/planner | §III-A, Fig.1, PDF pp.2–3 |
| Ablation | §IV-C, Figs.5–7, PDF pp.5–6 |
| Limitations / Future Work | §III-B/IV-B–C/§V, PDF pp.3–6 |
