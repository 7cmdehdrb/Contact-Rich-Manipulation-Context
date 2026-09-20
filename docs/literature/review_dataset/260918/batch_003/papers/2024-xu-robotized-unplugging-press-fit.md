# Robotized Unplugging of a Cylindrical Peg Press-Fitted into a Cylindrical Hole

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B088`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Shuihao Xu; Duc Truong Pham; Shizhong Su
- Year: 2024
- Venue: Royal Society Open Science 11: 230872
- DOI / arXiv: 10.1098/rsos.230872 / Not stated
- PDF version: Publisher PDF
- Page count: 13
- SHA-256: `b240190d1c63da8c7da3dd85562be243a8fa4eaf35e32f534dc003371afc6572`
- PDF filename: Xu 등 - 2024 - Robotized unplugging of a cylindrical peg press-fitted into a cylindrical hole.pdf
- 확인 범위: PDF pp.1–13 전체; theoretical/FEM/robot method, force–torque curves, controlled comparison, limitations and future work를 확인하고 Figures 5–8 및 Tables 3–5 렌더 검토.

## 2. Relevance to This Review

`Partially Relevant`

Manipulation policy나 contact-localization 연구는 아니지만, wrist 6-axis F/T로 press-fit disassembly의 axial force와 torque를 측정하고 direct pull과 twist-pull을 비교한다. F/T가 global load를 정량화할 수 있으나 contact locality를 추정하지 않으며, 해석이 known cylindrical geometry·material·friction·quasi-static model에 의존하는 사례로 본 Review의 F/T-only 성립 조건에 제한적 근거를 제공한다.

## 3. Task

EVA cylindrical peg가 steel cylindrical hole에 press-fit된 assembly를 TM14 robot이 gripper로 잡고 직접 당기거나, 축 방향으로 당기면서 동시에 회전하여 분리한다. 성공은 peg가 hole에서 완전히 빠지는 것이며, 두 전략의 axial friction force와 torque를 theory, finite-element simulation, robot experiment로 비교한다. [§2–3, PDF pp.3–11]

## 4. Method

### 4.1. Overall Pipeline

Known interference-fit geometry/material/friction → theoretical and Abaqus finite-element models로 force/torque 예측 → vision으로 peg 위치를 찾아 Robotiq gripper 정렬 → fixed-speed direct-pull 또는 twist-and-pull Cartesian trajectory 실행 → wrist ATI Axia80-M20 6-axis F/T를 실시간 기록 → peak axial force/torque와 separation outcome 비교. F/T는 feedback policy가 아니라 measurement/evaluation channel이다. [§2.1–2.3/§3.1–3.3, pp.3–9]

### 4.2. Observation

Robotized experiment는 vision으로 초기 peg 위치를 찾고, wrist F/T로 axial force $F_z$와 torque $T_z$를 기록한다. Fixed motion plan의 online policy observation으로 object pose 또는 F/T를 사용해 action을 수정한다고 명시하지 않는다. [§3.1–3.2, pp.7–9]

### 4.3. Action

Direct pulling은 z-axis로 0.25 mm/s, twist-pulling은 z-axis 0.15 mm/s와 회전 속도 3π/200 rad/s를 동시에 적용하여 총 π rad 회전한다. [§3.2, pp.8–9]

### 4.4. Controller

TM14의 programmed Cartesian trajectory와 Robotiq 2F-85 grip을 사용한다. F/T는 trajectory feedback이나 force regulation에 연결되지 않고 병렬 기록된다. Low-level servo law/gain은 원문에서 명시되지 않는다. [§3.1–3.2, pp.7–9]

### 4.5. Learning / Optimization Method

학습/RL이 아니다. Elasticity/contact mechanics theory, static finite-element analysis, predefined robot motion과 repeated physical trials를 결합한다. [§2–3, pp.3–12]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Initial | Machine vision으로 peg 위치를 찾아 gripper를 중심 정렬 | No | 실행 중 peg current pose tracking은 보고하지 않는다. [§3.1 pp.7–8] |
| Orientation | Initial | Cylindrical peg/hole 축 정렬과 gripper alignment | No | 회전 command는 current object orientation observation이 아니라 predefined trajectory다. [§3.1–3.2 pp.7–9] |
| Shape / Geometry | Initial | Known cylindrical peg/hole diameters, length and interference fit | No | Method와 force prediction이 single cylindrical press-fit geometry에 의존한다. [§2.1/Table 1 pp.3–4] |
| Physical Parameters | Initial | Known/assumed EVA and steel elastic properties, friction coefficients and interference | No | Friction coefficient와 Young’s modulus 등을 model에 직접 사용한다. [§2.1–2.2/Tables 1–2 pp.3–7] |

## 6. Missing Object Information and Compensation

Runtime distributed contact state와 contact location 미제공 → known concentric cylindrical geometry + material/friction assumptions + fixed twist/pull trajectory → axial force/torque 변화를 해석한다.

Current object pose tracking 미제공 → initial vision alignment + gripper constraint + programmed motion → 분리 동작을 수행한다. F/T는 contact locality를 복원하거나 feedback action을 선택하지 않고 global load outcome을 측정한다. [§3.1–3.3, pp.7–11]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§1–4, PDF pp.1–13]

### 7.2. Preprocessing

사용하지 않음. [§1–4, PDF pp.1–13]

### 7.3. Policy Representation

사용하지 않음. [§1–4, PDF pp.1–13]

### 7.4. Retained Information

사용하지 않음. [§1–4, PDF pp.1–13]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§1–4, PDF pp.1–13]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Robot wrist와 gripper 사이의 ATI Axia80-M20 6-axis force/torque sensor. [§3.1/Fig.5, pp.7–8]

### 8.2. Representation

6-axis F/T를 기록하지만 분석은 주로 axial pulling force $F_z$와 z-axis torque $T_z$, peak/average values와 time/displacement curves에 집중한다. [§3.2–3.3, pp.8–11]

### 8.3. Role

Direct pulling과 twist-pulling의 global friction load를 측정하고 theory/FEM을 검증한다. Contact detection/regulation, policy observation, contact localization에는 사용하지 않는다. [§3.3, pp.9–11]

### 8.4. Required Assumptions

Single concentric cylindrical press-fit contact, known dimensions/interference, rigid steel hole, linearly elastic EVA pin, specified friction, maintained gripper alignment, quasi-static/static model을 가정한다. [§2.1–2.2, pp.3–7]

### 8.5. Reported Limitation / Ambiguity

작은 torque는 sensor noise/trajectory error에 민감하고 반복 실험의 EVA wear가 결과에 영향을 준다. Net wrist wrench에서 contact patch/location을 복원하거나 multiple contacts를 구분하는 문제는 다루지 않는다. [§3.3/§4, pp.10–13]

## 9. Other Observations

Vision은 initial peg localization/alignment에만 사용된다. Known geometry/material/friction과 programmed velocities가 주요 prior다. History나 recurrent state, previous policy action, explicit state estimator는 없다. [§2–3, pp.3–11]

## 10. Tactile–Other Modality Relationship

Tactile은 사용하지 않는다. Wrist F/T는 global axial load와 torque를 측정하지만 local contact distribution을 제공하지 않는다. 분리 mechanics의 해석은 cylindrical geometry와 friction/material model이 보완한다. 따라서 이 논문은 F/T-only contact localization 성능보다, global wrench를 의미 있게 해석하려면 geometry/physics constraints가 필요하다는 간접 사례다. [§2–3, pp.3–11]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | 비-RL mechanics/robot experiment. Theory/FEM의 exact geometry와 material values는 model inputs이며 runtime learned policy GT가 아니다. [§2–4, PDF pp.3–13] |
| Critic | Not applicable | 비-RL | 비-RL mechanics/robot experiment. Theory/FEM의 exact geometry와 material values는 model inputs이며 runtime learned policy GT가 아니다. [§2–4, PDF pp.3–13] |
| Reward | Not applicable | 비-RL | 비-RL mechanics/robot experiment. Theory/FEM의 exact geometry와 material values는 model inputs이며 runtime learned policy GT가 아니다. [§2–4, PDF pp.3–13] |
| Termination | Not applicable | 비-RL | 비-RL mechanics/robot experiment. Theory/FEM의 exact geometry와 material values는 model inputs이며 runtime learned policy GT가 아니다. [§2–4, PDF pp.3–13] |
| Curriculum | Not applicable | 비-RL | 비-RL mechanics/robot experiment. Theory/FEM의 exact geometry와 material values는 model inputs이며 runtime learned policy GT가 아니다. [§2–4, PDF pp.3–13] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Twist-pulling reduces axial friction load | Controlled comparison | Direct pulling vs simultaneous twist-and-pull with same press-fit specimens | Average axial friction-force reduction is 32.53% in experiment, 33.49% in simulation, and 32.72% in theory. | §3.3; PDF pp.9–12 ; Tables 3–5 ; Figs.6–8 |
| Twist-pulling can enable removal when direct pulling fails | Failure analysis | Large-interference specimen under direct vs twist-pull | For the reported 7.08 mm pin, direct pulling did not remove the pin whereas twist-pulling completed removal. | §3.3; PDF pp.10–12 ; Tables 4–5 |
| Analytical/FEM assumptions approximate measured loads | Controlled comparison | Theory; Abaqus simulation; robot experiment | The three approaches report similar percentage reduction, while absolute deviations are attributed to model simplification, material variation, and experiment error. | §3.3–4; PDF pp.9–13 ; Tables 3–5 |
| F/T provides contact locality | No supporting evidence | No localization/tactile comparison | Only global force/torque curves are evaluated; contact location or distributed patch recovery is not tested. | §3.3; PDF pp.9–11 |

## 13. Author-stated Limitations

저자들은 linear-elastic EVA model이 실제 plastic/nonlinear behavior를 단순화하고, repeated tests에서 pin wear 때문에 동일 specimen을 재사용하기 어렵다고 설명한다. Small torque는 큰 fluctuation을 보이며 pin-position/robot-trajectory error의 영향을 받을 수 있다. 검증은 single cylindrical press-fit geometry와 제한된 specimens에 한정된다. [§3.3/§4, pp.10–13]

## 14. Author-stated Future Work

저자들은 elastic–plastic material model, 다른 materials와 geometries, wear를 고려한 반복성, 여러 cylinders 또는 더 복잡한 disassembly assemblies로 확장할 필요를 제시한다. [§4, p.13]

## 15. Review-relevant Findings

- Wrist ATI 6-axis F/T를 사용하지만 fixed trajectory를 수정하는 online policy observation으로 쓰지 않는다.
- 분석은 $F_z$와 $T_z$의 global load에 집중하며 contact location/patch를 복원하지 않는다.
- Force interpretation은 known cylindrical geometry, interference, material elasticity와 friction assumption에 의존한다.
- Current pose는 초기 vision alignment 뒤 지속 추적되지 않는다.
- Direct pull과 twist-pull controlled comparison은 force reduction을 뒷받침하지만 tactile 보완 효과를 검증하지 않는다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Geometry / physical assumptions | §2.1–2.2 pp.3–7 |
| Robot / F/T setup | §3.1/Fig.5 pp.7–8 |
| Action / trajectories | §3.2 pp.8–9 |
| Force/torque results | §3.3 pp.9–12 |
| Evidence tables | Tables 3–5 pp.10–12 |
| Limitation / Future | §4 p.13 |
