# Identifying External Contacts from Joint Torque Measurements on Serial Robotic Arms and Its Limitations

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B067`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Tao Pang; Jack Umenberger; Russ Tedrake
- Year: 2021
- Venue: 2021 IEEE International Conference on Robotics and Automation (ICRA)
- DOI / arXiv: 10.1109/ICRA48506.2021.9561761 / Not stated
- PDF version: IEEE publisher version
- Page count: 7
- SHA-256: `a46dff570a309911de96824021bbc18b705e736a47b087dd5ffc447bf12afb75`
- PDF filename: Pang 등 - 2021 - Identifying External Contacts from Joint Torque Measurements on Serial Robotic Arms and Its Limitati.pdf
- 확인 범위: PDF pp.1–7 전체; Figures 3–5/9와 implementation/conclusion 렌더 확인.

## 2. Relevance to This Review

`Partially Relevant`

Manipulation policy가 아니라 joint-torque-only contact localization의 성립 가정과 근본 ambiguity를 정량 분석한다. 본 Review의 두 번째 핵심 질문인 F/T 또는 wrench만으로 contact locality를 어디까지 복원할 수 있는지에 직접적인 제한 근거를 제공한다.

## 3. Task

Serial robot arm에서 joint angles와 residual external joint torque로 단일 외부 contact의 후보 위치와 force를 추정한다. RSGD가 residual의 local minima 집합을 찾고, 여러 후보가 있으면 작은 active robot motion으로 spurious candidate를 배제한다. [§III, V–VI, pp.2,4–6]

## 4. Method

### 4.1. Overall Pipeline

Raw joint torque → dynamics observer가 gravity/inertia를 제거한 residual torque $\tau_{ext}$ → known kinematics/surface/friction cone에서 candidate force QP residual 계산 → surface rejection sampling + Riemannian gradient descent(RSGD) → possible contact set → MILP active discrimination motion. [§II–VI, pp.2–6]

### 4.2. Observation

Estimator 입력은 current joint angles $q$, residual external joint torque $\tau_{ext}$, known robot kinematics/surface mesh이다. Contact force와 location은 출력이며, vision/tactile skin/object pose는 입력하지 않는다. [§III, p.2]

### 4.3. Action

Estimation 자체에는 action이 없다. Active discrimination은 candidate contact의 절반에서 pull-away, 나머지에서 push-into하도록 작은 joint displacement $\delta q$를 계획한다. [§VI, pp.5–6]

### 4.4. Controller

별도 manipulation controller는 제안하지 않는다. Active exploration motion은 contact normal 방향의 linearized motion constraints와 joint displacement bounds를 둔 MILP다. [§VI, pp.5–6]

### 4.5. Learning / Optimization Method

RL/학습이 아니다. Contact-force QP, rejection sampling, manifold Gauss–Newton/gradient descent, mixed-integer linear optimization을 결합한다. [§V–VII, pp.4–6]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Manipulated object current position은 입력하지 않음 | 해당 없음 | 추정 대상은 robot surface의 contact point이지 object pose가 아니다. [§III–VIII, PDF pp.2–6] |
| Orientation | 미제공 | Manipulated object orientation 입력 없음 | 해당 없음 | Object orientation/goal은 다루지 않는다. [§III–VIII, PDF pp.2–6] |
| Shape / Geometry | 기타 | Known robot surface triangle mesh and link geometry | 고정 prior | Object geometry가 아니라 robot geometry가 contact localization을 성립시킨다. [§III/VII pp.2,6] |
| Physical Parameters | 기타 | Illustrative known friction coefficient/cone; robot dynamics | 고정 prior | 분석 예는 friction coefficient 1, estimator는 friction cone constraint를 쓴다. [§III–IV pp.2–4] |

## 6. Missing Object Information and Compensation

Object pose/scene geometry 미제공 → known robot kinematics + robot surface mesh + friction cone + residual joint torque → robot body의 possible contact positions와 forces를 추정한다.

Joint torque alone의 locality ambiguity → 모든 low-residual 후보를 집합으로 유지 + small active motion → spurious 후보를 falsify한다. 단 active discrimination은 static environment contact와 새로운 contact가 생기지 않는다는 추가 가정이 필요하다. [§III–VI, pp.2–6]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§I–VIII, pp.1–6]

### 7.2. Preprocessing

사용하지 않음. [§I–VIII, pp.1–6]

### 7.3. Policy Representation

사용하지 않음. [§I–VIII, pp.1–6]

### 7.4. Retained Information

사용하지 않음. [§I–VIII, pp.1–6]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§I–VIII, pp.1–6]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

각 joint의 torque sensor raw signal에서 dynamics observer로 gravity/inertia를 제거해 residual external joint torque를 얻는다. Wrist F/T가 아니다. [§II, p.2]

### 8.2. Representation

Joint-space residual torque vector $\tau_{ext}$; candidate point마다 feasible contact force를 QP로 풀고 measured/predicted torque의 squared residual $l(p;q,\tau_{ext})$를 계산한다. [§III, p.2]

### 8.3. Role

Contact detection의 기반이며 robot surface contact location과 force 후보 집합을 추정한다. [§III–V, pp.2–5]

### 8.4. Required Assumptions

At most one external contact; negligible moment at contact point; known robot kinematics and surface; point lies on surface; force lies in known friction cone. Active discrimination은 static contact object와 motion 중 new contacts 없음도 가정한다. [§I/§III/§VI, pp.1–2,5]

### 8.5. Reported Limitation / Ambiguity

서로 다른 contact position/force가 거의 같은 joint torque를 만들 수 있고 joint-axis 부근 contact는 undetectable하다. Geometry와 configuration/singularity, noise threshold에 의존하며 multi-contact는 가정 밖이다. [§IV/§VIII, pp.3–6]

## 9. Other Observations

Joint angles와 known kinematics/surface normal이 estimator에 들어간다. Active motion 후 residual torque가 남거나 사라지는 history로 후보를 배제한다. Vision, object state, previous policy action, recurrent state는 사용하지 않는다. [§III/VI, pp.2,5–6]

## 10. Tactile–Other Modality Relationship

Tactile을 병용하지 않는다. 논문은 full-body tactile skin이 더 직접적인 대안이지만 비용/내구성 때문에 드물다고 설명한다. Joint torque는 global generalized effect만 제공하므로 동일 torque를 설명하는 spatial contacts가 여러 개 생기며, active exploration이 추가 정보로 필요하다. [§I, pp.1–2; §IV–VI, pp.3–6]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | 비-RL optimization/estimation 연구. Simulation/analysis의 true contact는 평가용이며 실행 estimator 입력이 아니다. [§III–VIII, pp.2–6] |
| Critic | Not applicable | 비-RL | 비-RL optimization/estimation 연구. Simulation/analysis의 true contact는 평가용이며 실행 estimator 입력이 아니다. [§III–VIII, pp.2–6] |
| Reward | Not applicable | 비-RL | 비-RL optimization/estimation 연구. Simulation/analysis의 true contact는 평가용이며 실행 estimator 입력이 아니다. [§III–VIII, pp.2–6] |
| Termination | Not applicable | 비-RL | 비-RL optimization/estimation 연구. Simulation/analysis의 true contact는 평가용이며 실행 estimator 입력이 아니다. [§III–VIII, pp.2–6] |
| Curriculum | Not applicable | 비-RL | 비-RL optimization/estimation 연구. Simulation/analysis의 true contact는 평가용이며 실행 estimator 입력이 아니다. [§III–VIII, pp.2–6] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Joint-torque-only contact detectability는 robot geometry에 의존 | Controlled comparison | IIWA link 6 vs UR5 forearm, surface samples | Fully detectable sample 비율이 IIWA 2.19%, UR5 32.58%로 다르며 joint-axis 주변은 빠르게 undetectable해진다. | §IV; PDF pp.3–4 ; Figs.4–5 |
| 동일 torque에 여러 contact 후보가 존재 | Failure analysis | True contact와 20,000 surface samples의 residual | 서로 다른 links/positions에 multiple global/local minima가 나타난다. | §III–IV; PDF p.3 ; Fig.3 |
| RSGD real-time feasibility | Controlled runtime analysis | 1000 samples; 184 accepted candidates | 단일 CPU thread에서 약 10 Hz; 평균 gradient run 472 μs. | §VII; PDF p.6 ; Fig.10 |
| Active motion이 후보를 구별할 수 있음 | Author demonstration only | Candidate set에 push/pull small motion MILP | 가능한 경우 residual 유지/소실로 후보를 절반씩 배제하지만 infeasible 또는 정보 없는 해도 가능하다. | §VI; PDF pp.5–6 ; Fig.9 |

## 13. Author-stated Limitations

Single-contact, negligible contact moment, known surface/friction constraints에도 joint torque는 contact locality를 고유하게 정하지 못한다. Joint-axis 인접 contact는 noise threshold 아래로 사라지고 geometry/conformation/singularity에 민감하다. RSGD는 global minima 보장을 하지 않으며 mesh normal discontinuity/proximity query에서 실패할 수 있다. Active discrimination도 항상 가능하지 않다. [§I/IV–VIII, pp.1,3–6]

## 14. Author-stated Future Work

독립된 Future Work 절은 없다. 결론은 실제 robot deployment 시 raw residual torque의 noise filtering과 bias 제거가 필요하다고 명시하고, 더 robust한 whole-body contact estimation에는 더 capable한 sensor가 필요할 수 있다고 제안한다. [Abstract/§VIII, pp.1,6]

## 15. Review-relevant Findings

- Joint torque는 wrist F/T와 구분되며 generalized residual torque를 제공한다.
- Known robot surface/kinematics, single point contact, friction cone, negligible contact moment가 필수 가정이다.
- 동일 joint torque를 설명하는 여러 spatial contact가 존재해 locality는 일반적으로 unique하지 않다.
- Active robot motion은 static-contact 가정 아래 추가 관측을 만들어 ambiguity를 줄인다.
- Multi-contact separation과 arbitrary contact moment는 분석 범위 밖이다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / formulation | §II–III p.2 |
| Object pose | 사용하지 않음; §III p.2 |
| Tactile | 사용하지 않음; §I p.1 |
| Force / assumptions | §I/III pp.1–2 |
| Ambiguity | §IV pp.3–4 |
| Estimator / action | §V–VI pp.4–6 |
| Evidence | Figs.3–5 pp.3–4; Fig.10 p.6 |
| Limitation / deployment note | §VIII p.6 |
