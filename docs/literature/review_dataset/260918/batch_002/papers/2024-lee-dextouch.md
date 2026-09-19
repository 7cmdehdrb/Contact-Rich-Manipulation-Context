# DexTouch: Learning to Seek and Manipulate Objects With Tactile Dexterity

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B038`
- Authors: Kang-Won Lee; Yuzhe Qin; Xiaolong Wang; Soo-Chul Lim
- Year: 2024
- Venue: IEEE Robotics and Automation Letters 9(12), 10772–10779
- DOI / arXiv: 10.1109/LRA.2024.3478571 / Not stated
- PDF version: Publisher PDF; current version 21 October 2024
- Version note: B038/B039는 SHA가 다르지만 동일 DOI/본문/표를 가진 publisher copies. 다운로드 footer를 제거한 text가 완전히 일치. B038 대표, B039 duplicate.
- Page count: 8
- SHA-256: `cf9edbb075ea6bbdf55845cf692642ea9dc39f9747589b16683ea087058a117d`
- PDF filename: `Lee 등 - 2024 - DexTouch Learning to Seek and Manipulate Objects With Tactile Dexterity (2).pdf`
- 읽은 범위: B038 PDF pp.1–8 전체(related work, methods, rewards, training, all experiments/conclusion/references). Fig.5 및 Table II–III를 확대 렌더로 확인. B039는 전 페이지 text를 footer 제외 비교하여 동일 본문 확인.
- 근거: 이번 배치의 PDF 원문에서 새로 분석했다. 기존 상세 노트는 재사용하지 않았다. 아래 페이지는 PDF 1-based page다.

## 2. Relevance to This Review

**Relevant**. 16-channel Binary tactile로 vision 없는 grasp/door/valve manipulation을 수행하며 current object pose가 없는 actor와 object GT를 받는 critic을 명시적으로 분리한다. Sensor 제거·민감도·배치·wrist F/T 대체 비교가 있어 reduced tactile 및 F/T의 실제 역할을 비교하는 직접 근거다. Binary tactile와 F/T를 함께 넣은 실험은 아니다.

Screening 위치: Abstract/§I, p.1; §III–IV, pp.2–5; §V-C–D, p.6.

## 3. Task

Tactile로 무작위 배치 물체를 seek/grasp하여 goal로 옮기기, handle를 찾아 60° 회전 후 door를 50° 열기, valve를 찾아 135° 회전하기. Grasp는 10 cm lifting indicator와 goal-distance progress를 사용한다. 각 task의 성공/학습 판정에는 object 상태가 쓰이나 actor 관측과 구분한다. (§III-B–IV-B, pp.3–4)

## 4. Method

### 4.1. Overall Pipeline

Binary tactile + proprioception + task/spawn prior → PPO actor → arm/hand joint targets → PD controllers. Simulation asymmetric critic uses additional object GT only for training. (§III–IV, pp.2–5)

### 4.2. Observation

Actor: q22, qdot22, tactile16, palm pose7+linear/angular velocity6, four fingertips relative to palm12, task information I. Grasp I=goal xyz+spawn range xy; door/valve I=spawn range xy. Exact object pose/physical state absent. (§IV-A, p.4)

### 4.3. Action

Normalized 22D action: 6 arm joint position commands + 16 hand joint targets. (§IV-A, p.4)

### 4.4. Controller

Both arm and hand use PD controllers at 10 Hz policy/control. Sensor voltage sampling 125 Hz와 구분한다. (§III-A–IV-A, pp.2–4)

### 4.5. Learning / Optimization Method

IsaacGym 4096 environments; PPO; policy/value MLP layers 512/256/128 with ELU. Critic asymmetric GT explicit. Reward is reaching progress plus task execution progress and joint-velocity L1 penalty. No progressive curriculum stated. (§IV-B–C, pp.4–5)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Exact initial/current object position is absent from actor; spawn range dimensions are known | No object pose update | Prior is region size/existence, not exact Initial pose. Goal point in grasping is not current position. 근거: §IV-A, p.4; §V-A/E, pp.5,7 |
| Orientation | 미제공 | Object orientation absent from actor state | 없음 | Door/valve angle is in reward/privileged information, not actor observation. 근거: §IV-A–C, pp.4–5 |
| Shape / Geometry | 기타 | Implicit task/object-set prior; no explicit shape vector in actor state | Not applicable | YCB meshes exist in simulation; not provided as actor input. 15 objects trained/tested, real seven including three unseen. 근거: §III-B, p.3; §IV-A, p.4; §V-E, pp.7–8 |
| Physical Parameters | 미제공 | Actor no physical parameters; critic privileged physical parameters | Actor 없음 | Physical properties of encountered training objects form implicit prior; unseen heavy/slippery tumbler hurts success. 근거: §IV-C, p.5; §V-E, p.8 |

## 6. Missing Object Information and Compensation

Exact object pose/vision 없음 → Binary tactile + robot proprioception + known spawn range → 알려진 영역으로 접근한 뒤 contact timing/pattern에 따라 manipulation한다. 저자가 이 compensation을 명시하고 sensor ablation으로 뒷받침한다. Shape/physical variation은 learned prior로 남으며 unseen tumbler에서 성능이 감소한다. Asymmetric critic GT는 실행 sensing의 대체 입력이 아니라 학습 보조 정보다. (§IV-A–C, pp.4–5; §V-E, pp.7–8)

## 7. Tactile

### 7.1. Raw Sensor

16 FSR: 각 finger 3개, palm 4개. Real voltage 125 Hz. Sim 16 virtual contact sensors의 net force [Fx,Fy,Fz] norm. (§III-A, pp.2–3)

### 7.2. Preprocessing

Real voltage low-pass filtering 후 selected threshold로 binary. Real voltage threshold의 수치/force calibration은 미명시. Sim threshold 0.01 N; LQ baseline 0.3 N. (§III-A, pp.2–3; §V-A, p.5)

### 7.3. Policy Representation

16개의 0/1 contact bits를 proprioception 및 task information과 결합. (§IV-A, p.4)

### 7.4. Retained Information

해당 sensor region의 contact presence와 여러 영역에 걸친 coarse contact pattern. 구조상 직접 확인 가능. (§IV-A, p.4; Fig.2)

### 7.5. Removed / Unavailable Information

Binary화는 threshold 초과 force magnitude와 방향을 제공하지 않는다. Region 내부 contact position/patch는 표현하지 않는다. 이는 representation 구조 해석이며 continuous-vs-binary 실험은 없음. (§III-A–IV-A, pp.2–4)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

F/Tsensor baseline은 robot wrist의 3-axis force와 3-axis torque. 주 제안 policy는 FSR binary이며 F/T 병용 아님. (§V-D, p.6)

### 8.2. Representation

6D force/torque baseline. Frame/filter/normalization 세부 미명시. (§V-D, p.6)

### 8.3. Role

Blind manipulation을 위한 tactile 대체 observation으로 simulation에서 비교. (§V-D; Table II, p.6)

### 8.4. Required Assumptions

동일 simulator/task 및 proprioception/prior 맥락에서 비교한다. Known object position 없이도 spawn range와 task prior가 존재. (§IV-A, p.4; §V-A/D, pp.5–6)

### 8.5. Reported Limitation / Ambiguity

F/T-only success가 tactile보다 낮다고 보고하지만 net wrench의 contact-location ambiguity를 직접 분석하지는 않는다. (§V-D, p.6)

## 9. Other Observations

Vision 없음. History/previous action/recurrent state는 explicit actor 목록에 없다. Goal은 grasping target 위치만 제공하며 current object pose가 아니다. Palm/fingertip pose는 robot proprioception이다. (§IV-A, p.4)

## 10. Tactile–Other Modality Relationship

Tactile는 contact presence와 sensor-region pattern을, proprioception은 손/팔 configuration을, spawn range는 탐색할 영역을 제공한다. Critic GT는 학습의 효율과 안정성을 지원한다. Wrist F/T는 별도 baseline으로 교체되며 결합 실험은 없다. Region Binary+tactile/FT 결합의 우월성이나 global/local 역할 분담을 이 논문에서 직접 검증했다고 쓰지 않는다. (§IV–V, pp.4–8)

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Actor | No object GT | Proprioception + 16 binary bits + task goal/range prior | 실행 시 필요. Current/initial exact object pose 없음. | §IV-A, p.4 |
| Critic | Yes | Exact target pose; linear/angular velocity; distance from hand; physical parameters; task reward indicators | 학습 전용 value inputs. Actor에는 미제공. | §IV-C, p.5 |
| Reward | Yes | Fingertip-target distances; object height and goal distance; handle/door/valve angles; progress maxima | Simulator state로 학습; actor input으로 혼합하지 않음. | §IV-B Eq.(1)–(4), p.4 |
| Termination | Yes / partly unspecified | Task goal attainment, reset conditions and step limit | Sim goal conditions use object/task state. Detailed reset rules and real autonomous stopping input are not fully specified. | §IV-A–B, pp.3–4 |
| Curriculum | Randomized state generation | Object position uniformly sampled from known area; no progressive curriculum stated | Actor receives range dimensions, not sampled true pose. | §V-A; Table I, p.5 |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Binary tactile의 기여 | Sensor ablation | Ours vs WO-Sensor; grasp/door/valve; 3 seeds | Success Ours 0.72±0.07/0.69±0.12/0.82±0.06 vs WO 0/0/0.02±0.01. | §V-B, pp.5–6; Table II/Fig.5a, p.6 |
| Sensitivity의 기여 | Representation ablation (threshold); Failure analysis | 0.01 N vs LQ 0.3 N binary threshold | LQ success 0.37/0.37/0.58; 낮은 민감도에서 과도한 접촉과 object drop/throwing 관찰. Continuous tactile 비교가 아님. | §V, pp.5–8; Table II–III, p.6 |
| Region coverage/location | Sensor ablation | 전체 16 vs fingertip 4 vs palm 4 | Fingertip success 0.49/0.48/0.69, palm 0.36/0.38/0.53; task-dependent location effect. | §V-C, p.6; Table II/Fig.5b |
| Tactile와 wrist F/T의 대체 비교 | Controlled comparison | Ours Binary16 vs F/Tsensor baseline; no combined arm | F/T success 0.26±0.11/0.29±0.15/0.50±0.08 vs Ours 0.72/0.69/0.82. 역할의 causal decomposition이나 combination superiority는 검증하지 않음. | §V-D, p.6; Table II/Fig.5b |
| Privileged critic의 학습 기여 | Input ablation | Ours vs WO-PInfo | WO-PInfo success 0.15/0.15/0.31. Privileged value inputs의 효율/안정성에 대한 비교이며 actor GT 필요성을 보여 주는 결과가 아님. | §V-A/B, pp.5–6; Table II |
| Real-world tactile 사용 확인 | Sensor ablation; Failure analysis | Ours vs LQ vs DA (evaluation sensor off) | Ours grasp seen 0.64±0.17/unseen 0.47±0.24, door 0.60±0.17, valve 0.67±0.17. DA 0.09/0.11/0.12. Grasp 30 trials/object; door/valve 55 trials, 3 policies averaged. | §V evaluation protocol p.5; Table III p.6; §V-E pp.6–8 |

## 13. Author-stated Limitations

Known prior region이 있어야 initial reaching을 시작할 수 있으며 정확한 location은 touch로 보완한다. 학습에서 접하지 못한 무게/미끄러운 표면의 tumbler는 낮은 성공률을 보인다. 낮은 민감도는 과도한 force와 drop을 유발한다. (§V-A/E, pp.5,7–8)

## 14. Author-stated Future Work

3-axis force처럼 다양한 tactile information을 제공하는 sensor 적용과 system generalizability 확대를 명시한다. 현재 Binary policy에서 이미 continuous/shear 정보를 썼다는 뜻이 아니다. (§VI, p.8)

## 15. Review-relevant Findings

- Current object pose는 actor에 없고 spawn-range prior는 있다.
- Binary16 + proprioception을 사용한다.
- Critic/reward에는 object GT가 있다.
- Wrist F/T-only 대체 baseline과 직접 비교한다.
- Binary tactile+F/T 결합은 평가하지 않았다.
- 민감도, sensor 위치/범위, privileged critic, 실물 sensor deactivation을 각각 비교한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / prior | §IV-A, p.4 |
| Tactile preprocessing | §III-A, pp.2–3 |
| Reward / termination | §IV-A–B, pp.3–4 |
| Critic | §IV-C, p.5 |
| F/T comparator | §V-D, p.6 |
| Ablation / numbers | Fig.5 and Table II–III, p.6 |
| Limitations | §V-E, pp.7–8 |
| Future | §VI, p.8 |
