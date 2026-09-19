# A Unified Approach for Motion and Force Control of Robot Manipulators: The Operational Space Formulation

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B032`
- Authors: Oussama Khatib
- Year: 1987
- Venue: IEEE Journal of Robotics and Automation RA-3(1), 43–53
- DOI / arXiv: Not stated / Not stated
- PDF version: English publisher PDF
- Version note: B031은 같은 논문의 한국어 번역형 17p이며 번역자/공식성 미명시. 원문 publisher B032(11p)를 대표 근거로 사용; 별도 논문으로 세지 않음.
- Page count: 11
- SHA-256: `7c4f6a6918e0a1a4b9f40f27fb605410e7274609e7f38666bfa8979158dd61a4`
- PDF filename: `Khatib - 1987 - A unified approach for motion and force control of robot manipulators The operational space formula.pdf`
- 읽은 범위: 영문 PDF pp.1–11 전체(본문·수식·토론·참고문헌), Fig.3 제어 구조 렌더 확인. B031은 제목·구조·마지막 참고문헌을 비교해 번역형 중복으로 확인; 분석 근거로 사용하지 않음.
- 근거: 이번 배치의 PDF 원문에서 새로 분석했다. 기존 상세 노트는 재사용하지 않았다. 아래 페이지는 PDF 1-based page다.

## 2. Relevance to This Review

**Partially Relevant**. 운동/힘 제어를 성립시키는 known constraint direction, task frame, robot dynamics와 force feedback의 역할을 명시하는 기초 제어 연구다. F/T만으로 contact geometry를 복원하는 방법이 아니므로, force control과 contact inference를 구분하기 위한 근거로 포함한다. Tactile 축약 및 modality ablation은 다루지 않는다.

Screening 위치: Abstract/§I–II, pp.1–3; §V and Fig.3, pp.6–7.

## 3. Task

Assembly의 constrained motion과 active contact force를 통합 제어한다. 실물 구현은 contact, slide, insertion, compliance operations를 보고하며 일반 제어 정식화가 핵심이다. 객체 추적이나 unknown contact localization의 성공률 task는 아니다. (§I–II, pp.1–3; §IX, p.10)

## 4. Method

### 4.1. Overall Pipeline

Known task motion/force directions + EEF/joint state + force feedback → operational-space controller with dynamics compensation → Jacobian-transpose mapping → joint force/torque. (§II–V, pp.2–7; Fig.3)

### 4.2. Observation

Controller 입력은 current/desired EEF position, orientation, velocity, desired acceleration/force, joint q/velocity, sensed transformed force 및 task specification matrices다. Learned actor는 없다. 물체 pose/shape estimator 입력으로 바꾸어 쓰지 않는다. (Fig.3, p.7; §IV–V, pp.5–7)

### 4.3. Action

Operational force $F=F_m+F_a+F_{ccg}$를 선택하고 $Gamma=J^TF$로 joint force에 매핑한다. Motion, active force, Coriolis/centrifugal/gravity compensation을 구분한다. (§IV Eq.(28)–(34), p.5; §V Eq.(45)–(48), p.7)

### 4.4. Controller

힘 제어 방향과 직교하는 motion subspace를 task matrix로 지정한다. Impact transition은 pure energy dissipation/velocity damping을 사용한다. PUMA implementation은 low-level 200 Hz, dynamics 100 Hz. Redundant null-space damping 및 singular configuration 처리를 추가한다. (§V–IX, pp.7–10)

### 4.5. Learning / Optimization Method

비-RL model-based analytical controller. Nonlinear dynamic decoupling은 model structure/parameter knowledge에 의존한다. PUMA dynamic identification을 사용하지만 학습 actor/critic/reward는 없다. (§IV, p.5; §IX, p.10)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미명시 | Explicit current manipulated-object position input is not specified | 미명시 | EEF current/desired pose와 object pose를 구분. 근거: §II–V, pp.2–7 |
| Orientation | 미명시 | Explicit current object orientation input is not specified | 미명시 | Controller orientation error는 EEF orientation이다. 근거: §II, pp.2–3; §V, p.6 |
| Shape / Geometry | 기타 | Holonomic geometric constraints, rigid-body linkage description, allowed motion and force directions | Task matrix는 constant/configuration-/time-varying 가능 | Full mesh sensing이 아니라 제약/방향을 알고 제어하는 조건. 근거: §II, pp.2–3 |
| Physical Parameters | 미명시 | Robot dynamics model and identified PUMA parameters; object properties input unspecified | Robot dynamic coefficients updated | Robot inertia/parameters를 object physical input으로 기록하지 않음. 근거: §III–IV, pp.3–6; §IX, p.10 |

## 6. Missing Object Information and Compensation

Unknown contact geometry를 센서만으로 복원하는 구조가 제시되지 않는다. Known holonomic constraint + force/moment 방향 + task frame → 제어할 motion/force subspace를 제공한다. Robot dynamics + EEF feedback → 동적 coupling을 보상한다. 이는 F/T가 geometry 정보를 대신 추정한다는 주장이 아니다. (§II–V, pp.2–7)

## 7. Tactile

### 7.1. Raw Sensor

Wrist and finger sensing 사용을 §IX에서 언급하지만 tactile sensor 종류·raw/processing/representation 및 정보 보존/소실은 미명시다. Tactile 미사용으로 확정하지 않는다. (§IX, p.10)

### 7.2. Preprocessing

Wrist and finger sensing 사용을 §IX에서 언급하지만 tactile sensor 종류·raw/processing/representation 및 정보 보존/소실은 미명시다. Tactile 미사용으로 확정하지 않는다. (§IX, p.10)

### 7.3. Policy Representation

Wrist and finger sensing 사용을 §IX에서 언급하지만 tactile sensor 종류·raw/processing/representation 및 정보 보존/소실은 미명시다. Tactile 미사용으로 확정하지 않는다. (§IX, p.10)

### 7.4. Retained Information

Wrist and finger sensing 사용을 §IX에서 언급하지만 tactile sensor 종류·raw/processing/representation 및 정보 보존/소실은 미명시다. Tactile 미사용으로 확정하지 않는다. (§IX, p.10)

### 7.5. Removed / Unavailable Information

Wrist and finger sensing 사용을 §IX에서 언급하지만 tactile sensor 종류·raw/processing/representation 및 정보 보존/소실은 미명시다. Tactile 미사용으로 확정하지 않는다. (§IX, p.10)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

실물 PUMA 560에서 wrist and finger sensing. Fig.3의 force sensor feedback 경로는 명시되지만 sensor model·축 수는 미명시. (Fig.3, p.7; §IX, p.10)

### 8.2. Representation

Force/moment를 포함하는 generalized operational force; sensor-frame force transformation. Force-rate feedback도 사용했다고 언급한다. (§II, pp.2–3; §V, p.7)

### 8.3. Role

Active force regulation, motion/force subspace 제어, impact energy dissipation. 위치를 추정하는 force inversion은 아니다. (§V Eq.(45)–(48), p.7)

### 8.4. Required Assumptions

Known force/moment directions and geometric constraints, task reference frames, robot Jacobian/dynamics. Accurate dynamics identification이 decoupling에 기여한다. (§II, pp.2–3; §III–V, pp.3–7; §IX, p.10)

### 8.5. Reported Limitation / Ambiguity

운동으로 인한 inertial/Coriolis coupling과 torque-control 제약을 논의한다. Net wrench의 multi-contact/locality ambiguity는 직접 논의하지 않는다. (§I, p.1; §IX, p.10)

## 9. Other Observations

Proprioception과 EEF state, reference trajectory, desired force/moment, task frame 및 identified robot dynamics가 controller를 구성한다. Vision/previous action/history stack은 미명시. Force-rate feedback을 history stack과 등치하지 않는다. (Fig.3, p.7; §IX, p.10)

## 10. Tactile–Other Modality Relationship

Wrist and finger sensing을 동시에 사용했다고 보고하나 각 센서의 독립적 역할이나 ablation은 제시하지 않는다. 따라서 tactile가 wrist wrench에 locality를 추가했다고 자동 해석하지 않는다. (§IX, p.10)

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Actor | 해당 없음 | 비-RL 방법 | 해당 없음 | §II–IX, pp.2–10 |
| Critic | 해당 없음 | 비-RL 방법 | 해당 없음 | §II–IX, pp.2–10 |
| Reward | 해당 없음 | 비-RL 방법 | 해당 없음 | §II–IX, pp.2–10 |
| Termination | 해당 없음 | 비-RL 방법 | 해당 없음 | §II–IX, pp.2–10 |
| Curriculum | 해당 없음 | 비-RL 방법 | 해당 없음 | §II–IX, pp.2–10 |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Force control 성능 | Author explanation only | PUMA implementation 결과 보고; 센서 제거 비교 없음 | Impact velocity 최대 4.0 in/s에서 bounce elimination; force step rise <0.02 s, steady force error <12%. Trial 수/variance 미명시. | §IX, PDF p.10 |
| Null-space damping으로 redundant mechanism 안정화 | Controlled comparison | Simulated 3-DoF arm, damping 추가 전/후 | End-effector goal=current position, initial joint velocity 0.5 rad/s 조건의 motion을 Fig.4로 비교. 센서 역할 실험은 아님. | §VII, PDF pp.8–9; Fig.4 |
| Force control의 추가 정보 의존성 | Author explanation only | Task specification/known dynamics의 수학적 구조 | Force-regulated directions와 free-motion directions를 미리 지정. Contact location/shape 추정 성능은 제시하지 않음. | §II, PDF pp.2–3; §V, pp.6–7, Fig.3 |

## 13. Author-stated Limitations

Known robot dynamic parameters와 torque actuation의 제약, orientation representation과 applied moment specification의 compatibility를 다룬다. Joint-torque 제어 한계에도 force 성능을 얻었다고 보고한다. 센서 bias/noise 또는 multi-contact ambiguity 분석은 없다. (§V, p.6; §IX, p.10)

## 14. Author-stated Future Work

명시적 future-work 계획은 미명시. Joint constraints, collision avoidance, posture control을 framework에 자연스럽게 통합할 수 있다고 논의하지만 이 논문의 신규 실험으로 취급하지 않는다. (§IX, p.10)

## 15. Review-relevant Findings

- Force regulation은 known task geometry/direction과 robot dynamics를 이용한다.
- EEF pose는 current object pose가 아니다.
- Wrist/finger sensing의 구체 representation과 상보성은 미명시다.
- Contact locality를 F/T만으로 복원했다는 근거는 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / model | §II–V, pp.2–7; Fig.3 |
| Object geometry / assumptions | §II, pp.2–3 |
| Force / impact control | §V, pp.6–7 |
| RL / privileged | 해당 없음 |
| Evidence | §VII–IX, pp.8–10; Fig.4–5 |
| Limitations / future | §V, p.6; §IX, p.10 |
