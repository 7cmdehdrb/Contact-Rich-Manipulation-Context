# Towards Safe and Efficient Learning in the Wild: Guiding RL With Constrained Uncertainty-Aware Movement Primitives

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B065
- Authors: Abhishek Padalkar; Freek Stulp; Gerhard Neumann; João Silvério
- Year: 2025
- Venue: IEEE Robotics and Automation Letters 10(7), 6880–6887
- DOI / arXiv: 10.1109/LRA.2025.3566599 / Not stated
- PDF version: IEEE publisher PDF, July 2025 issue
- Page count: 8
- SHA-256: 72065fa915de2044072efd34ffd63af79d3c1372160b70079179a6bf16c03da2
- PDF filename: Padalkar 등 - 2025 - Towards Safe and Efficient Learning in the Wild Guiding RL With Constrained Uncertainty-Aware Movem.pdf
- 읽은 범위: PDF pp.1–8 본문 및 포함된 부록을 새로 확인; 핵심 표·그림 렌더링 확인

근거는 이번 배치의 PDF 원문이며 기존 상세 노트는 사용하지 않았다. 페이지는 PDF의 1-based page다.

## 2. Relevance to This Review

**Relevant**. 실물 BNC insertion/locking에서 6D wrench와 EEF pose를 RL actor에 제공한다. Demonstration에서 얻은 nominal trajectory·covariance와 수작업 linear constraints가 함께 사용되므로 force-feedback 조작의 추가 정보와 prior를 분석할 수 있다. Force 입력 자체의 ablation은 보고하지 않는다.

## 3. Task

DLR SARA가 BNC connector를 align, insert, rotate/lock한다. Real experiment는 task success와 episode length/interaction force를 평가하지만 success를 검출하는 구체적인 센서·threshold는 미명시다. 별도의 simulation은 좁은 passage를 통과하는 2D navigation으로, manipulation 결과와 구분한다. (§IV pp.5–7)

## 4. Method

### 4.1. Overall Pipeline

Five kinesthetic demonstrations → GMM/GMR reference trajectory/covariance → LC-NS-KMP nominal trajectory and null-space projector; time+EEF pose+wrench → TQC policy → null-space action → constrained KMP desired 6D pose → robot. (§III pp.2–5; §IV.B pp.6–7)

### 4.2. Observation

실물 actor q_t = [t, p_tᵀ, f_tᵀ]ᵀ: time, target frame의 6D EEF pose(position+Euler angles), center of compliance에서 측정한 6D wrench로 총 13 scalar다. KMP 자체의 input은 time이다. Target frame은 successful demonstration의 마지막 EEF frame으로 정의한다. Current connector pose를 독립 측정한 입력은 없다. (§IV.B p.7)

### 4.3. Action

Policy가 KMP mean trajectory를 수정하는 null-space action ξ를 출력하며, resultant robot command는 6D EEF pose다. ξ를 EEF velocity로 기록하지 않는다. Linear inequality constraints는 XY 이동을 각 ±0.002 m로 제한한다. (Eqs.17,21 pp.5,7)

### 4.4. Controller

Torque-controlled 7-DoF SARA를 사용하며 KMP output은 desired EEF pose다. 본 논문은 low-level tracking controller의 구체적인 식·주파수와 wrench sensor hardware를 명시하지 않는다. Joint torque anomaly를 이용한 collision signal은 reward용으로 별도 사용한다. (Abstract p.1; §IV.B p.7)

### 4.5. Learning / Optimization Method

TQC, 2 × 256 MLP. Five demonstrations each 400 samples로 time-based KMP를 학습한다. RL exploration은 demonstration covariance에 의해 state-dependent하게 변하며 linear constraints를 적용한다. Simulation residual RL/safe residual RL/KGRL 비교와 real BNC learning curve를 보고한다. 별도 critic observation은 미명시다. (§III–IV pp.2–7)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Current connector position을 독립 추정한 actor input 없음 | 해당 없음 | EEF pose는 target frame에서 갱신되며 held-object motion의 proxy다. Object tracking이라고 바꾸어 쓰지 않는다 (§IV.B p.7) |
| Orientation | 미제공 | Current connector orientation input 없음 | 해당 없음 | EEF Euler angles와 object orientation을 구분 (§IV.B p.7) |
| Shape / Geometry | 기타 | Demonstration trajectory/covariance, target frame, hand-designed XY constraints | 고정 demonstrations/constraints | Full mesh/CAD 입력 없음; 접촉 task에 대한 motion/geometry prior는 존재 (§III; §IV.B Eq.21 p.7) |
| Physical Parameters | 미제공 | Object mass/friction explicit input 없음 | 없음 | Real contact dynamics를 RL로 적응 (§I p.1; §IV.B p.7) |

## 6. Missing Object Information and Compensation

Demonstration-only trajectory가 처리하지 못하는 kinematic/dynamic uncertainty 및 contact dynamics → current EEF pose + measured wrench + RL corrections → nominal motion을 반응적으로 수정한다. Demonstration covariance는 탐색 크기/방향을, 수작업 constraints는 허용 영역을 제공한다. 이 역할은 저자 설명과 whole-method comparison에 근거하며 wrench-only ablation으로 분리 검증되지는 않았다. (§I pp.1–2; §IV.B–V pp.7–8)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. (§III–IV pp.2–7)

### 7.2. Preprocessing

사용하지 않음. (§III–IV pp.2–7)

### 7.3. Policy Representation

사용하지 않음. (§III–IV pp.2–7)

### 7.4. Retained Information

사용하지 않음. (§III–IV pp.2–7)

### 7.5. Removed / Unavailable Information

사용하지 않음. (§III–IV pp.2–7)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Center of compliance에서 측정한 6D wrench. Wrist F/T인지 joint-torque-estimated wrench인지 하드웨어 출처는 미명시. Collision 판정에는 별도로 anomalous joint torques를 관찰한다. (§IV.B p.7)

### 8.2. Representation

6D wrench f_t; force/torque vector의 filtering, history, normalization은 미명시. (§IV.B p.7)

### 8.3. Role

Actor observation; −0.01 fᵀf reward cost; interaction-force learning curve. Joint torque collision signal은 terminal reward −50에 사용. (Eqs.22–23; Fig.7 p.7)

### 8.4. Required Assumptions

Successful demonstrations and covariance, known target frame from final demonstration, expert-defined linear constraints, demonstration variance가 적절한 exploration strategy를 나타낸다는 가정. F/T-only localization은 수행하지 않는다. (§IV.B p.7; §V p.8)

### 8.5. Reported Limitation / Ambiguity

Net-wrench contact locality/multi-contact ambiguity, noise/drift는 직접 논의하지 않는다. Demonstration 및 constraint design의 한계를 별도로 명시한다. (§V pp.7–8)

## 9. Other Observations

EEF pose와 time이 actor에 들어간다. Successful demonstration의 final frame이 goal/reference이며 current object pose가 아니다. History, previous action, recurrent hidden state, vision은 actor 입력으로 명시되지 않는다. Demonstration covariance와 constraints는 KMP/projector에 들어가는 조건으로 actor sensor vector와 구분한다. (§III–IV pp.2–7)

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않으며 force+tactile combination evidence는 없다. EEF pose/wrench/trajectory prior를 함께 사용하므로 F/T만으로 성공한 조작으로 분류할 수 없다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부·비고 |
| --- | --- | --- | --- |
| Actor | 실물 simulator GT 없음 | Time; measured EEF pose; measured wrench. Simulation actor는 time | Real sensors/reference frame 필요; current object GT 입력 명시 없음 (§IV pp.5–7) |
| Critic | 미명시 | TQC의 별도 critic state/privileged observation 설명 없음 | Algorithm 이름만으로 actor와 같은 입력이라고 단정하지 않음 (§IV pp.6–7) |
| Reward | Simulation state 사용; 실물 measured wrench/collision/outcome | Simulation distance-to-obstacle/displacement/goal; real action norm, wrench norm, success reward and joint-torque collision penalty | Real success label의 획득 방식 미명시 (Eqs.18–20 p.6; Eqs.22–23 p.7) |
| Termination | Simulation state 사용; 실물 success 판정 source 미명시 | Simulation goal/blocked≥20 steps/time400; real task outcome/collision | Real connector locking success의 센서·threshold 미명시 (§IV pp.6–7) |
| Curriculum | Adaptive curriculum 미명시; 실물 simulator GT 없음 | Five real kinesthetic demonstrations, nominal path/covariance, expert constraints | Demonstrations/prior는 실행 sensor observation과 별도 (Algorithm1 p.5; §IV.B p.7) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Guided exploration/constraints의 전체 효과 | Controlled comparison | Simulation residual RL vs safe residual RL vs KGRL | KGRL은 초기부터 success rate 1을 보이며 wall collision/constraint violation을 억제. Safe residual도 explicit wall filters로 collision/violation을 억제. 2D navigation 결과로 real contact-sensing ablation과 구분 | §IV.A, Figs.4–6, PDF pp.5–6 |
| Demonstration policy에 RL correction이 필요 | Failure analysis; Controlled comparison | Real BNC vanilla KMP 실패 vs KGRL learning curve | KMP-only motion은 완료하지 못했고 KGRL은 평균 약 45 episodes에서 success 1. 독립 evaluation denominator/seed 수는 본문 미명시 | §IV.B, Fig.7, PDF pp.6–7 |
| Wrench 입력의 추가 효용 | Author explanation only; No supporting evidence for modality ablation | Wrench 제거 또는 pose-only actor 비교 없음 | Contact dynamics 적응의 설명은 있지만 sensor contribution을 분리할 수 없음 | §I; §IV.B, PDF pp.1–2,7 |

## 13. Author-stated Limitations

Safety constraints는 수작업으로 정의하며 expert knowledge가 필요하다. Demonstrations가 적절한 exploration strategy를 encode한다는 가정은 항상 성립하지 않을 수 있다. Smooth exploration 자체를 주요 평가 목표로 삼지는 않았다. (§V pp.7–8)

## 14. Author-stated Future Work

Constraint extraction을 자동화하고 non-linear constraints를 포함하여 더 넓은 assembly task에 적용하는 방향을 제시한다. (§VI p.8)

## 15. Review-relevant Findings

- Real actor는 time + 6D EEF pose + 6D wrench를 사용한다.
- Wrench의 hardware source는 원문에서 확인되지 않는다.
- Goal frame은 successful demonstration의 마지막 frame이며 current object tracking과 다르다.
- Demonstration covariance와 manually defined XY constraints가 exploration을 안내한다.
- Wrench-input 제거 ablation 및 tactile combination은 없다.
- Real success label과 critic 입력은 미명시다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / object pose | §IV.B p.7 |
| Tactile / F/T | §IV.B p.7: tactile 없음; 6D wrench |
| Reward / termination | Eqs.18–20 p.6; Eqs.22–23 p.7 |
| Critic | §IV pp.6–7: 별도 입력 미명시 |
| Comparisons | Figs.4–6 pp.5–6; Fig.7 p.7 |
| Limitation / future work | §V–VI pp.7–8 |
