# Learning a High-quality Robotic Wiping Policy Using Systematic Reward Analysis and Visual-Language Model Based Curriculum

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B050`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Yihong Liu; Dongyeop Kang; Sehoon Ha
- Year: 2025
- Venue: Not stated
- DOI / arXiv: Not stated / 2502.12599v1
- PDF version: arXiv v1, 18 February 2025
- Page count: 7
- SHA-256: `dbe9a465f98a1ac28aa8dc70e8796626df1a2e3bf6aa1b360ec84aab1ec99ec9`
- PDF filename: Liu 등 - 2025 - Learning a High-quality Robotic Wiping Policy Using Systematic Reward Analysis and Visual-Language M.pdf
- 확인 범위: PDF pp.1–7 전체(본문 pp.1–6, 참고문헌 p.7); Table I 및 Fig.4 렌더 확인. 별도 부록 없음.

## 2. Relevance to This Review

`Relevant`

Blind surface wiping에서 curvature/friction을 관측하지 않고 F/T와 robot state 및 주어진 waypoint로 접촉 힘과 이동을 제어한다. 실행 시 센서 정보와 학습 중 contact/collision·waypoint 보상, VLM 영상 피드백을 구분할 수 있다. Tactile 비교가 아니라 force 기반 partial-observation manipulation 및 training-only 정보 사례로 포함한다.

## 3. Task

7-DoF Panda가 곡률·마찰이 다른 tabletop에서 두 waypoint를 닦으면서 목표 수직 힘 60 N을 유지한다. Navigation 완료율, completion steps, force Integral Absolute Error를 평가한다. MuJoCo/robosuite simulation만 검증했으며 실물 성공을 보고하지 않는다. [§V-A–B/Table I, p.5]

## 4. Method

### 4.1. Overall Pipeline

46차원 waypoint·joint·EEF·F/T observation → deep RL policy → 6차원 pose command → 20 Hz robosuite OSC_POSE → robot actuation. 학습 중 별도 LLM/VLM이 rollout metric/영상으로 reward weight를 갱신한다. [§III-A p.3; §IV pp.4–5; §V-A p.5]

### 4.2. Observation

46차원: waypoint information, sine/cosine으로 encode한 joint positions/velocities(원문의 표현), EEF position/orientation, F/T sensor values. Table curvature와 smoothness는 관측 불가다. 수치별 dimension 분해, history, previous action, recurrent state는 미명시다. VLM에 주는 failure scene은 실행 policy의 vision observation이 아니다. [§III-A, pp.2–3; §IV, p.4]

### 4.3. Action

6차원 EEF position/orientation 조정. Force는 별도 policy action이 아니라 pose 변경으로 간접 조절한다. [§III-A, p.3]

### 4.4. Controller

robosuite OSC_POSE를 20 Hz에서 제어한다. 상세 stiffness/gain 및 inner-loop frequency는 미명시다. [§V-A, p.5]

### 4.5. Learning / Optimization Method

Deep RL 알고리즘명(PPO/SAC 등), actor/critic architecture는 원문에서 확인되지 않는다. Contact/force 품질 reward를 waypoint 주변 concentric checkpoint마다 제한하여 끝없이 닦는 reward exploitation을 방지한다. 300k step부터 매 100k step에 50 episode 평가; GPT-4와 GPT-4-vision-preview가 필요 시 reward weight를 조정한다. 각 방법 5 seed, 800k step 결과를 비교한다. [§III-B–C/§IV/§V, pp.3–6]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Current tabletop pose를 별도 입력한다는 명시 없음; waypoint와 EEF pose는 제공 | 해당 없음 | Waypoints는 목표 위치이며 object pose가 아니다. [§III-A, PDF pp.2–3] |
| Orientation | 미제공 | Current surface orientation 입력 없음 | 해당 없음 | EEF orientation은 표면 orientation이 아니다. [§III-A, PDF pp.2–3] |
| Shape / Geometry | 미제공 | Curvature는 hidden; 6개 tabletop shape를 simulation에서 randomize | 해당 없음 | Known waypoints만으로 full shape 제공이라고 기록하지 않는다. [§III-A pp.2–3; §V-A p.5] |
| Physical Parameters | 미제공 | Sliding/torsional/rolling friction은 환경에서 randomize; actor에 미제공 | 해당 없음 | Curriculum에는 이 randomization parameter를 포함하지 않는다고 명시한다. [§V-A p.5] |

## 6. Missing Object Information and Compensation

관측하지 않는 tabletop curvature와 smoothness → F/T, EEF·joint state, 미리 주어진 waypoint → pose command를 조절하면서 접촉 힘과 이동을 함께 달성한다. 이 관측 구조와 POMDP 동기는 명시되지만 F/T 제거 ablation은 없다. 목표 위치 제공과 현재 object pose tracking은 구분한다. [§III-A, pp.2–3; §V, pp.5–6]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§III-A, PDF pp.2–3]

### 7.2. Preprocessing

사용하지 않음. [§III-A, PDF pp.2–3]

### 7.3. Policy Representation

사용하지 않음. [§III-A, PDF pp.2–3]

### 7.4. Retained Information

사용하지 않음. [§III-A, PDF pp.2–3]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§III-A, PDF pp.2–3]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Simulation EEF의 force/torque sensor. 실물 sensor model, wrist 장착, joint-torque wrench 추정 여부는 미명시다. [§III-A, PDF pp.2–3]

### 8.2. Representation

Observation은 F/T sensor values로만 기술하여 축별 차원은 미명시. Reward는 EEF sensor의 upward/downward force $f_z$와 목표 60 N을 사용한다. [Eq.2] [§III-A, PDF pp.2–3]

### 8.3. Role

Policy observation, force-quality reward 및 학습 평가/LLM curriculum metric. 접촉 detection은 별도 binary flag reward로 서술하여 F/T threshold로 계산했다고 단정할 수 없다. [§III-A, PDF pp.2–3; §IV p.4]

### 8.4. Required Assumptions

사전에 제공되는 waypoint, obstacle 없는 wiping 시나리오, robot kinematics/state와 training surface distribution. Force-only contact localization은 수행하지 않는다. [§I p.1; §III-A p.3; §V-A p.5]

### 8.5. Reported Limitation / Ambiguity

Net wrench locality, multiple-contact, noise/bias/drift 한계는 원문에서 직접 논의하지 않는다. [§III–VI pp.2–6]

## 9. Other Observations

Proprioception: joint/EEF state. Goal: 두 waypoint. Vision: actor에는 없고 training-only VLM failure-scene 분석에 사용. Curriculum은 success, landing/navigation force, 이전 평가 기록을 유지하지만 이것을 actor sensor history라고 기록하지 않는다. State estimator 및 previous action 입력은 미명시다. [§III-A p.3; §IV p.4]

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않는다. F/T와 proprioception/waypoint가 함께 입력되지만 각 sensor의 필요성을 분리하는 ablation은 없다. VLM과 bounded reward 비교는 학습 설계 검증이며 modality complementarity 실험이 아니다. [§V, pp.5–6]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No object GT stated | 46D sensor-like robot/F/T and waypoint inputs | Simulator에서 획득하지만 hidden curvature/friction/object full state를 actor에 제공하지 않음. 실행 센서 재현은 아직 실물 미검증. [§III-A, PDF pp.2–3] |
| Critic | Not stated | Critic input 및 asymmetric critic 여부 미명시 | Actor와 같다고 추정하지 않는다. [§III-A, PDF pp.2–3; §V-A p.5] |
| Reward | Yes | Simulation collision/contact flags, waypoint/checkpoint completion; EEF force/direction/acceleration | 학습에서 사용. Sensor force와 geometric success flags를 구분. [Eqs.1–2,6] [§III-A/C pp.3–4] |
| Termination | Yes | Collision 시 즉시 종료, 마지막 waypoint 완료 시 종료; horizon 200 | Simulation task event에 의존. 실물 종료 구현 없음. [§III-A–B p.3] |
| Curriculum | Yes; simulation evaluation/visual feedback | Success metrics, force statistics, failure-scene image; shape/friction randomization | VLM은 training-only. Randomized shape/friction parameter는 curriculum 입력에서 제외한다고 명시. [§IV p.4; §V-A p.5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Bounded reward가 완료를 회피하는 행동을 줄임 | Controlled comparison | Non-bounded vs bounded; 5 seeds | Success 58%→92%; steps 38→29; IAE 267→333. 품질 저하와 completion 개선을 함께 기록. | §V-B; PDF p.5 ; Table I |
| VLM curriculum 추가 효과 | Controlled comparison | Bounded vs bounded+VLM | Success 92%→98%; steps 29→25; IAE 333→243. Force plots는 미완료 perpetual-wiping episode를 제외한다. | §V-B; PDF pp.5–6 ; Table I ; Fig.4 |
| F/T/proprioception 입력 자체의 필요성 | Author explanation only | F/T 또는 proprioception 제거 실험 없음 | Hidden curvature/smoothness에서 sensor policy를 구성하지만 modality별 기여는 분리 검증하지 않음. | §III-A/§V; PDF pp.2–3,5–6 |
| 나쁜 초기 reward weight에서 curriculum 회복 | Controlled comparison | Navigation reward가 품질 reward의 10%인 설정 | Bounded는 600k 후에도 success 근처 0; VLM curriculum은 500k에 40%. | §V-C; PDF p.6 |

## 13. Author-stated Limitations

VLM의 복잡한 시나리오 일반화, simulation 결과의 hardware 검증, waypoint 사전 제공 가정이 현재 한계로 명시된다. [§VI, p.6]

## 14. Author-stated Future Work

Wiping 이외 복잡한 상황으로 확장, hardware deployment, observation에서 waypoint를 자율 생성하여 waypoint 제공 가정을 없애는 것이 후속 과제다. [§VI, p.6]

## 15. Review-relevant Findings

- Actor에는 vision/표면 geometry 입력 없이 F/T와 robot state 및 waypoint가 들어간다.
- VLM failure-scene feedback은 학습용이며 actor의 연속 시각 추적이 아니다.
- Algorithm명과 critic GT 구성은 원문에 미명시다.
- 접촉/충돌·waypoint reward와 termination에는 simulator task information이 사용된다.
- 보상/커리큘럼 비교는 있으나 sensor ablation은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / object information | §III-A pp.2–3 |
| Tactile | §III-A: 사용하지 않음 |
| F/T / Reward / termination | §III-A–C pp.3–4 |
| Critic | 미명시; §III–V |
| Controller | §V-A p.5 |
| Curriculum | §IV p.4 |
| Evidence | Table I p.5; Figs.4–6 p.6 |
| Limitation / Future | §VI p.6 |
