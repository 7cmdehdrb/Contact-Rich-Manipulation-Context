# Guiding real-world reinforcement learning for in-contact manipulation tasks with Shared Control Templates

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B064
- Authors: Abhishek Padalkar; Gabriel Quere; Antonin Raffin; João Silvério; Freek Stulp
- Year: 2024
- Venue: Autonomous Robots 48, Article 12
- DOI / arXiv: 10.1007/s10514-024-10164-6 / Not stated
- PDF version: Publisher PDF, published 4 June 2024; Appendix A included
- Page count: 17
- SHA-256: 7aab5f995fd6a7c3c8eef488842e21defbd86d330b9657c73076755862cc5482
- PDF filename: Padalkar - Guiding real-world reinforcement learning for in-contact manipulation tasks with Shared Control Temp.pdf
- 읽은 범위: PDF pp.1–17 본문 및 포함된 부록을 새로 확인; 핵심 표·그림 렌더링 확인

근거는 이번 배치의 PDF 원문이며 기존 상세 노트는 사용하지 않았다. 페이지는 PDF의 1-based page다.

## 2. Relevance to This Review

**Relevant**. 실물 grid-clamp insertion에서 FK로 얻은 clamp 위치와 3D force를 actor에 제공한다. 알려진 hole frame, orientation constraint, 좁은 탐색 영역이 접촉 학습을 성립시키므로 F/T 기반 방법의 추가 정보와 가정을 비교하는 데 직접 관련된다. Force cost 비교는 존재하지만 force 입력 제거 실험과는 구분해야 한다.

## 3. Task

Pouring은 thermos 안의 두 ping-pong ball을 mug에 넣으며 실물 성공은 사람이 판정한다. Grid-clamp assembly는 다섯 peg를 동시에 삽입하고 고정하는 작업으로, 실험의 성공 판정은 EEF z가 정한 threshold 아래에 도달하는 조건이다. 독립적인 peg 상태 측정으로 성공을 확인했다고 확장하지 않는다. (§5.1 pp.8–11; §5.2 pp.11–13)

## 4. Method

### 4.1. Overall Pipeline

Actor observation → SAC/TQC policy의 3D action → SCT phase별 Input Mapping → Active Constraints로 허용 영역에 projection → desired Cartesian pose → robot position controller. SCT의 phase/transition과 policy의 action을 구분한다. (§3–4 pp.3–8)

### 4.2. Observation

Pouring actor는 thermos tip의 6D pose를 mug-tip frame에서 받는다. 실물 thermos pose는 robot FK로 추정하며 mug pose는 사전에 알려져 있다. Grid-clamp actor는 hole frame의 clamp 3D position과 clamp frame의 3D force를 받는다. Policy에 RGB, tactile, previous action, history를 제공한다는 명시는 없다. (§5.1 pp.8–9; §5.2.2 p.12)

### 4.3. Action

RL-SCT의 3D action은 phase별 6D EEF pose increment로 변환된다. Pouring의 SCT 없는 baseline은 6D EEF velocity를 제어한다. Grid-clamp는 orientation을 제약하고 translation을 0.8 cm × 0.8 cm × 10 cm cuboid 안에서 탐색한다. (§4 pp.6–8; §5.2.1 p.12)

### 4.4. Controller

Cartesian position control. Simulation KUKA iiwa 100 Hz, real DLR SARA 8 kHz controller가 기술되어 있다. Grasp 및 insertion 부근으로의 접근은 사전 동작이며 policy 학습 범위와 분리된다. (§5 pp.8–12)

### 4.5. Learning / Optimization Method

Simulation pouring에서 SAC/TQC를 비교하고 실제 SARA에서는 SAC를 사용한다. Policy는 2 × 256 MLP이며 real pouring 5 learning sessions, grid-clamp force-cost 유무 각각 5 learning sessions를 보고한다. Grid-clamp 초기 grasp는 6개 위치를 순환한다. Critic의 별도 state 입력은 미명시다. (§5; Appendix A pp.13–14)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Thermos/clamp pose를 robot FK로 추정; target mug/hole frame은 사전 설정 | 매 실행 state | Tracked value는 실제 물체를 독립 관측한 GT가 아니며 grasp/calibration 오차가 남는다 (§5.1 p.9; §5.2 pp.11–12) |
| Orientation | 기타 | Pouring thermos orientation은 FK estimate; grid-clamp에서는 orientation uncertainty를 무시하고 constraint로 고정 | Pouring state 갱신; clamp actor에는 orientation 없음 | Task별 입력을 분리한다 (§5.1 p.9; §5.2.1 p.12) |
| Shape / Geometry | 기타 | Known mug/hole frame, phase-specific geometric constraints, cuboid exploration bounds | 고정 task prior | Mesh/CAD를 actor에 직접 제공하지 않지만 known task geometry가 SCT 설계에 사용됨 (§3–4 pp.3–8; §5.2.1 p.12) |
| Physical Parameters | 미제공 | Actor에 object mass/friction 입력 명시 없음 | 없음 | Controller와 constraint 설계 조건은 별도 (§5 pp.8–13) |

## 6. Missing Object Information and Compensation

FK 기반 pose estimate에 남는 grasp/kinematic/table-calibration 오차 → measured 3D force + constrained local translation + 반복적인 real experience → insertion 중 반응을 학습한다. Known hole/mug frame과 phase constraints는 탐색 범위를 정하는 사전 정보다. Force만으로 object pose 또는 contact location을 복원하는 방법은 아니다. (§5.2 pp.11–13)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. (§4–5 pp.6–13)

### 7.2. Preprocessing

사용하지 않음. (§4–5 pp.6–13)

### 7.3. Policy Representation

사용하지 않음. (§4–5 pp.6–13)

### 7.4. Retained Information

사용하지 않음. (§4–5 pp.6–13)

### 7.5. Removed / Unavailable Information

사용하지 않음. (§4–5 pp.6–13)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Grid-clamp의 integrated F/T sensor. 센서의 구체적인 장착 위치·모델은 미명시이므로 wrist 6-axis F/T라고 단정하지 않는다. (§5.2.2 p.12)

### 8.2. Representation

Clamp frame에서 표현한 3D force vector. Actor에 torque components/history/derivative를 넣는다는 명시는 없다. (§5.2.2 p.12)

### 8.3. Role

Actor observation; quadratic force penalty −(1/12) fᵀf; 실험에서 interaction-force cost 비교. (§5.2.2–3 pp.12–13)

### 8.4. Required Assumptions

Known hole frame/table calibration, fixed grasp-to-EEF transform을 이용한 FK estimate, 작은 orientation uncertainty, 제한된 translation cuboid. F/T-only contact localization은 수행하지 않는다. (§5.2 pp.11–12)

### 8.5. Reported Limitation / Ambiguity

Kinematics, grasp, calibration, controller uncertainty를 task 어려움으로 명시한다. Net-wrench multi-contact ambiguity나 contact-patch 식별 한계는 직접 논의하지 않는다. (§5.2 p.11)

## 9. Other Observations

Proprioception/FK는 manipulated-object pose estimate를 제공한다. Goal mug/hole frame은 사전 정보이며 current pose 측정과 구분한다. SCT phase는 action mapping과 constraint 선택에 쓰인다. Real pouring 성공에는 human observation이 사용된다. Vision, sensor history, recurrent state, previous action의 policy 입력은 미명시다. (§3–5 pp.3–13)

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않으므로 tactile–F/T의 역할 분담에 대한 근거는 없다. Force feedback의 역할은 geometry/FK prior 아래에서 contact task를 학습하는 것이다. Force-cost ablation은 센서 입력의 필요성을 검증하는 sensor ablation이 아니다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부·비고 |
| --- | --- | --- | --- |
| Actor | 실물 simulator GT 없음; simulation source는 별도 구분 | Real FK-derived relative pose; clamp force; simulated pouring relative pose | 실행 시 FK/force와 known target frame 필요. Sim pose acquisition의 GT 여부는 원문에서 별도 명확히 설명되지 않음 (§5 pp.8–13) |
| Critic | 미명시 | 별도 critic observation 또는 asymmetric GT 입력 미명시 | Actor와 같다고 추정하지 않음 (§5; Appendix A pp.13–14) |
| Reward | Simulation environment state 사용; 실물 sensor/human 판정 | Pouring success/spillage/collision; clamp z-progress, force cost, action cost, terminal reward | 실물 pouring human outcome label; clamp robot z/force 사용. Reward용 정보를 actor 입력과 혼합하지 않음 (§5.1 pp.8–10; §5.2.2 p.12) |
| Termination | Simulation outcome state; 실물 task별 판정 | Pouring human success/failure/collision/time limit; clamp EEF z threshold | Clamp 성공은 EEF z 기반 proxy이며 독립 object state GT가 아님 (§5.1 pp.8–10; §5.2.2 p.12) |
| Curriculum | 실물 simulator GT 없음; adaptive curriculum 미명시 | Known SCT constraints; six real pickup locations for reset | Reset distribution/task prior는 실행 actor observation과 별도 (§5.2 pp.11–12) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| SCT가 task learning을 안내 | Controlled comparison | Simulation pouring SCT 유무 × sparse/shaped reward, SAC/TQC | SCT 포함 방법이 더 효율적이며 collision을 제한한다. Real에서는 unsafe baseline을 실행하지 않음 | §5.1, PDF pp.8–11 |
| Force penalty가 지속적인 높은 하중을 줄임 | Controlled comparison | Real grid-clamp force cost 유무; 두 조건 모두 force observation 사용 | 각각 약 70 episodes에서 success 1; force penalty 없는 경우 80–90 episodes 이후 탐색 중 높은 force/failure 발생. Abstract의 75 episodes와 본문의 약 70 표현은 일치하지 않음 | §5.2.3, Fig.11, PDF pp.12–13 |
| Force actor input 자체의 필요성 | No supporting evidence | Force observation 제거 조건 없음 | Force cost 실험으로 입력 modality의 인과적 필요성을 판정할 수 없음 | §5.2, PDF pp.11–13 |

## 13. Author-stated Limitations

SCT는 명시적인 task constraints를 설계할 수 있는 문제에 적합하며 juggling/locomotion처럼 복잡한 motor skill로의 적용은 쉽지 않다. SCT를 수작업으로 설계하는 부담도 남는다. (§6 p.13)

## 14. Author-stated Future Work

Demonstration으로부터 SCT constraints와 nominal policy를 추출하고 uncertainty-aware movement primitives를 결합하는 방향을 제시한다. (§6 p.13)

## 15. Review-relevant Findings

- Grid-clamp actor는 FK 기반 relative position과 3D force를 받는다.
- Known target geometry와 orientation/translation constraints가 포함되어 있다.
- Force-cost ablation의 두 조건 모두 force observation을 사용한다.
- Critic GT 입력은 미명시다. Real clamp 성공은 EEF z threshold로 판정한다.
- Tactile 및 F/T-only contact localization은 사용하지 않는다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / object pose | §5.1 p.9; §5.2.2 p.12 |
| Tactile / F/T | §5.2.2 p.12: tactile 없음, integrated F/T의 force 입력 |
| Reward / termination | §5.1 pp.8–10; §5.2.2 p.12 |
| Critic | Appendix A pp.13–14; 별도 입력 미명시 |
| Ablation | §5.1 pp.8–11; Fig.11 pp.12–13 |
| Limitation / future work | §6 p.13 |
