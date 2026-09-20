# Augmenting Robotic Disassembly Skill: Combining Compliance Control Strategy with Reinforcement Learning for Twist-Pulling Disassembly

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B095`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Yue Zang; Xiazhen Xu; Yongquan Zhang; Amir M. Hajiyavand; Jiaqi Ye; Yongjing Wang
- Year: 2025
- Venue: 2025 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)
- DOI / arXiv: 10.1109/IROS60139.2025.11246037 / Not stated
- PDF version: IEEE publisher version
- Page count: 6
- SHA-256: `fbb924fa91256d304cd67637795042a5e7724e7232a5d95c8b36b25b81dcaba1`
- PDF filename: Zang 등 - 2025 - Augmenting robotic disassembly skill combining compliance control strategy with reinforcement learn.pdf
- 확인 범위: PDF pp.1–6 전체; mechanical assumptions, impedance equations, RL state/action/reward, robot sensor, safety/termination, strategy/transfer/compliance/action-space comparisons, limitations/future를 확인하고 Figures 4–6와 Tables I–IV 렌더 검토.

## 2. Relevance to This Review

`Relevant`

Hidden cap–shaft geometry와 misalignment 상황에서 flange force/torque와 TCP pose만으로 rotation center를 탐색하고 impedance twist-pull을 수행한다. Object pose/geometry 없이 wrench가 policy observation·reward·compliance에 쓰이는 범위, 이를 성립시키는 known axis/grasp/controller assumptions와 controlled strategy comparisons를 제공한다.

## 3. Task

Franka robot이 internal connection geometry가 보이지 않는 cap–shaft assembly를 grasp한 뒤 z-axis로 twist하면서 5 mm씩 들어 올려 cap/shaft를 분리한다. RL은 misaligned grasp에서 effective rotation center (x + Δx, y + Δy)를 탐색하고, compliance controller는 axial load가 threshold를 넘으면 rotation을 보상한다. Cap이 specified height에 도달하면 성공이다. [§III–V, PDF pp.2–5]

## 4. Method

### 4.1. Overall Pipeline

Franka internal torque sensing에서 flange force/torque detection + TCP pose → DDPG actor가 rotation-center offset (Δx, Δy) → Cartesian impedance controller가 target pose tracking force를 joint torques로 mapping; rule ΔR_z = k_r(F_z - F_s)가 axial force를 twist compensation으로 변환 → fixed 5 mm lift steps → force/torque monitoring and safety limits → success height 또는 re-execution. [§III-B/§IV/§V, pp.2–5]

### 4.2. Observation

RL state는 robotic flange에서 detected forces/torques와 tool-center-point poses다. Full component list/history/frame/filtering은 미명시이며 transfer ablation은 simplified {F_x, F_y, τ_z} observation을 사용한다. Current object pose, connection geometry, shape 또는 vision은 input이 아니다. [§IV-B/§V-A, pp.3–5]

### 4.3. Action

DDPG action은 (Δx, Δy) rotation-center offset이며 gripper rotation center를 조정한다. Disassembly skill은 z-axis rotation compensation과 fixed 5 mm lift step을 실행한다. [§IV-A–B/§V, pp.3–5]

### 4.4. Controller

Cartesian impedance controller가 position/orientation errors에서 desired task force를 계산하고 $J^T$로 joint torque에 mapping하며 nullspace and Coriolis terms를 더한다. Axial force $F_z$가 threshold $F_s$를 넘으면 $k_r$ gain으로 z-rotation correction을 만든다. Collision limit은 30 N/10 Nm, main experiment $F_s=2$ N다. [§III-B/§V, pp.2–5]

### 4.5. Learning / Optimization Method

Real robot interaction에서 off-policy DDPG를 사용하고 매 step policy를 update한다. Reward는 $r=-0.5(F_n+T_z)$, $F_n=(F_x^2+F_y^2)^{1/2}$로 lateral load와 torsional load를 줄이는 rotation-center search를 유도한다. Hyperparameters는 trial and error로 선택했으며 alternatives를 비교하지 않는다. [§IV-B, pp.3–4]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Actor에 cap/shaft current position이 없음 | 해당 없음 | Grasp point $(x,y)$와 TCP pose는 robot/tool state이고 object pose tracking과 구분한다. [§IV-A–B p.3] |
| Orientation | 미제공 | Actor에 cap/shaft current orientation이 없음 | 해당 없음 | Z-axis twist is a controller/task assumption, not measured current object orientation. [§III–IV pp.2–3] |
| Shape / Geometry | 미제공 | Internal cap–shaft connection geometry를 unknown zone으로 취급; actor geometry input 없음 | 해당 없음 | Transfer results show size/geometry similarity matters despite no explicit geometry input. [§III-A p.2; §V-A p.5] |
| Physical Parameters | 미제공 | Friction/locking parameters를 actor에 제공하지 않음 | 해당 없음 | Hidden friction/geometric resistance is encountered online. [§III-A–B pp.2–3] |

## 6. Missing Object Information and Compensation

Current object pose와 hidden connection geometry/physical parameters 미제공 → flange force/torque + TCP pose → DDPG가 low-load rotation center를 탐색한다.

Contact geometry와 exact path 미제공 → known axial twist/pull structure + Cartesian impedance + force-threshold rotation rule → mechanical resistance에 compliant하게 반응한다. F/T만으로 contact location을 추정하는 것이 아니라 action-constrained path search가 ambiguity를 줄인다. [§III–IV, pp.2–4]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§I–VI, PDF pp.1–6]

### 7.2. Preprocessing

사용하지 않음. [§I–VI, PDF pp.1–6]

### 7.3. Policy Representation

사용하지 않음. [§I–VI, PDF pp.1–6]

### 7.4. Retained Information

사용하지 않음. [§I–VI, PDF pp.1–6]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§I–VI, PDF pp.1–6]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Franka Emika robot의 internal torque sensor를 이용해 robotic flange에서 force and torque를 detect한다. Joint torque에서 flange wrench를 계산하는 exact estimator/filter는 원문에서 명시되지 않으며 physical wrist F/T로 기록해서는 안 된다. [§IV-B/§V, pp.3–5]

### 8.2. Representation

RL state는 flange force/torque와 TCP pose; reward는 $F_n=(F_x^2+F_y^2)^{1/2}$와 $T_z$; compliance rule은 $F_z$와 threshold $F_s$를 사용한다. Transfer simplification은 {F_x, F_y, τ_z}. [§III-B/§IV-B/§V-A, pp.3–5]

### 8.3. Role

Policy observation, low-load reward, axial-force-triggered rotation compensation, overload monitoring/collision safety, rotation-center path search에 사용한다. [§III-B/§IV-B/§V, pp.3–5]

### 8.4. Required Assumptions

Maintained rigid grasp of cap/tool, known z twist/pull axis and fixed lift direction, single structured cap–shaft interface, TCP/flange transform, calibrated internal torque-to-wrench sensing, chosen impedance gains/force threshold, geometry similarity for transfer가 필요하다. [§III–V, pp.2–5]

### 8.5. Reported Limitation / Ambiguity

Net flange wrench는 contact patch/location 또는 internal lock type을 직접 식별하지 않는다. Large center offset and geometry dissimilarity reduce performance; excessive initial torque can cause grasp failure. Authors do not analyze multi-contact wrench ambiguity or sensor bias/noise. [§V-A/Table II–IV, pp.5–6]

## 9. Other Observations

Proprioception은 TCP pose와 impedance position/orientation errors이다. Known task prior는 twist/pull z-axis, fixed 5 mm lift and success height다. Vision, object pose/shape input, tactile, sensor history, recurrent hidden state, previous action은 원문에서 명시되지 않는다. [§III–V, pp.2–5]

## 10. Tactile–Other Modality Relationship

Global flange wrench는 resistance magnitude/direction을, TCP pose는 robot configuration과 rotation-center geometry를, impedance controller는 measured load에 대한 compliant action을 제공한다. Tactile spatial sensing은 없으므로 local contact location/patch는 관측하지 않는다. Table I의 combined/without-RL/RL-only 비교는 force sensor 자체가 아니라 compliance prior와 RL 결합의 효과를 검증한다. [§V-A, pp.5–6]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | Detected flange forces/torques and TCP poses | Object GT pose/geometry/physical parameters가 없다. [§IV-B, p.3] |
| Critic | Not stated | DDPG critic input not explicitly enumerated | DDPG를 사용하지만 privileged object GT critic 여부는 원문에서 확인되지 않는다. [§IV-B, pp.3–4] |
| Reward | No | Sensor-derived $F_n$ and $T_z$ | Simulator/object GT가 아니라 runtime-measurable force/torque로 계산한다. [§IV-B/Eq.4, p.3] |
| Termination | No | Specified lift height and force/torque safety conditions based on robot/tool state | Object GT pose tracking을 사용한다고 명시하지 않는다. [§V, p.5] |
| Curriculum | No / Not stated | Real-world training; no simulator curriculum or privileged data generation described | Transfer uses frozen actor from different structures, not privileged curriculum. [§V-A, p.5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Compliance prior plus RL improves disassembly acquisition | Controlled comparison | Combined method vs without RL vs RL-only across five structures | Combined succeeds 10/10, 9/10, 7/10, 8/10, 8/10; baselines are substantially lower, including threaded 3/10 and 0/10. | §V-A; PDF pp.5–6 ; Table I |
| Learned wrench/TCP policy transfers when geometry is similar | Controlled transfer comparison | Own, similar, simplified, and non-similar training environments | Own/similar/simplified agents generally transfer well; non-similar agent drops to 3/10 on threaded and interference cases. | §V-A; PDF p.5 ; Table II |
| Compliance stiffness affects disassembly success | Controller ablation | Low, medium, high translational/torsional impedance settings | Medium is best or tied across tested structures; low fails friction-locked cases and excessive stiffness is not always better. | §V-A; PDF pp.5–6 ; Table III |
| Rotation-center distance and force threshold constrain performance | Controlled comparison | Three action-space distance ranges and three $F_s$ thresholds | Rotation achieved per minute decreases as grip point moves farther from axis; threshold effect is smaller near the center. | §V-A; PDF p.6 ; Table IV |
| Flange wrench uniquely localizes hidden contacts | No supporting evidence | No localization/tactile comparison | The method searches a rotation center under known twist-pull structure; it does not estimate local contact point or patch. | §III–V; PDF pp.2–6 |

## 13. Author-stated Limitations

저자들은 alternative RL training strategies를 비교하지 않았고, evaluation이 success에만 집중하여 speed/operational efficiency를 평가하지 않았다고 명시한다. 실험한 limited structures 밖의 generalisability가 추가 검증되어야 한다. Transfer section은 geometry/size similarity와 fixture design이 중요하며 excessive initial torque가 grasp failure를 일으킬 수 있음을 보고한다. [§V-A/§VI, pp.5–6]

## 14. Author-stated Future Work

RL training process와 sample efficiency를 개선하고 더 complex disassembly scenarios와 diverse structural forms로 framework를 확장해 generalisability와 industrial applicability를 검증할 계획이다. [§VI, p.6]

## 15. Review-relevant Findings

- Actor state는 flange force/torque와 TCP pose이며 current object pose/geometry는 제공되지 않는다.
- Force source는 Franka internal torque sensing 기반 flange detection이고 physical wrist F/T로 명시되지 않는다.
- Reward는 runtime-measurable lateral force magnitude와 z torque로 계산해 simulator GT가 필요 없다.
- Wrench는 rotation-center search와 compliance/overload control에 사용하지만 contact locality를 직접 복원하지 않는다.
- 방법은 known twist/pull axis, maintained grasp, structured cap–shaft interface와 tuned impedance/threshold에 의존한다.
- Strategy/transfer/compliance/action-space comparisons은 controller prior와 geometry dependence를 뒷받침하지만 sensor ablation은 아니다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Mechanical assumptions / hidden geometry | §III-A p.2 |
| Impedance / force-threshold rule | §III-B pp.2–3 |
| RL state / action / reward | §IV-A–B pp.3–4 |
| Robot sensor / safety / success | §V pp.4–5 |
| Method / transfer evidence | §V-A/Tables I–II p.5 |
| Compliance / action-space evidence | Tables III–IV pp.5–6 |
| Limitation / Future | §VI p.6 |
