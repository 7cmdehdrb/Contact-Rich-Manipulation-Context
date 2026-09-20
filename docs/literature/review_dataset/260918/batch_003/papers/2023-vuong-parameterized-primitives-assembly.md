# Reinforcement Learning with Parameterized Manipulation Primitives for Robotic Assembly

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B083`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Nghia Vuong; Quang-Cuong Pham
- Year: 2023
- Venue: arXiv preprint
- DOI / arXiv: Not stated / 2306.06679v1
- PDF version: arXiv v1 (2306.06679v1, 11 Jun 2023)
- Page count: 8
- SHA-256: `352344faf4bc2709eac1d040a5706c6d17f1abd49fad44ecc58994a50720ce0b`
- PDF filename: Vuong 및 Pham - 2023 - Reinforcement Learning with Parameterized Manipulation Primitives for Robotic Assembly.pdf
- 확인 범위: 전체 arXiv PDF pp.1-8; state/action/reward, F/T hardware, assumptions, sim-real experiments, failure modes, conclusion/future work 확인

## 2. Relevance to This Review

`Relevant`

peg-hole relative pose와 6-axis F/T를 관측하거나 action feasibility/primitive termination에 사용해 contact-rich insertion을 수행한다. 특히 저자 스스로 force를 접촉 상태 분리에는 쓰지만 policy는 주로 kinematics에 의존하여 sim-to-real 실패가 생긴다고 분석하고 tactile 통합을 future work로 제시하므로, F/T가 제공하는 범위와 부족한 local contact state를 직접 보여준다.

## 3. Task

round/square/triangle peg을 작은 clearance의 hole에 삽입한다. RL이 parameterized manipulation primitives의 종류와 속도·거리·force threshold·desired force 등을 online 선택한다.

## 4. Method

### 4.1. Overall Pipeline

초기 hole pose estimate와 robot kinematics로 peg-hole relative pose 계산 + flange Gamma IP60 6-axis F/T → PPO discrete MP policy와 parameter subpolicy → free/in-contact primitive 선택 및 parameter → hybrid motion/force operational-space controller → EEF command. [Secs. III-A and IV, PDF pp.3-5]

### 4.2. Observation

state는 peg relative to hole pose p_t와 external force/torque f_ext,t로 정의한다. 다만 conclusion은 policy가 주로 kinematics에 의존하고 force는 free/in-contact action subspace 분리에만 쓰였다고 해석한다. hole/task frame은 초기 pose estimate로 설정한다. [Sec. IV, PDF p.4; Sec. VI, p.7]

### 4.3. Action

13개 MP 중 하나와 continuous parameters를 고르는 hybrid discrete-continuous action이다. primitives는 translate/rotate until contact, fixed distance/angle, insert이며 speed, displacement, threshold, desired force, timeout 등을 parameterize한다. [Secs. III-A, IV; Table I, PDF pp.3-5]

### 4.4. Controller

operational-space inverse-dynamics position loop와 feedforward force loop의 hybrid motion/force control. Real controller는 1000 Hz이고 F/T는 insertion torque regulation과 primitive stopping에 사용한다. [Sec. III-A and V-A, PDF pp.3,5]

### 4.5. Learning / Optimization Method

PPO로 categorical discrete-action policy와 각 MP의 Gaussian action-parameter policy를 학습한다. MuJoCo simulation에서 perception error를 randomize한 뒤 six physical peg-hole tasks로 zero-shot transfer한다. [Secs. IV-V, PDF pp.4-6]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | 초기에 추정한 hole/task frame과 robot FK로 peg-relative-to-hole position p_t 계산 | Yes | 초기 hole estimate 오차는 <1 mm 가정; simulation에서 ±1 mm randomize. [Sec. IV and V-A, PDF pp.3-5] |
| Orientation | Tracking | 초기 hole axis/task frame과 EEF orientation으로 relative orientation 계산 | Yes | 초기 error <1° 가정; simulation에서 ±1° randomize. [Sec. IV and V-A, PDF pp.3-5] |
| Shape / Geometry | Initial | peg/hole profile와 insertion axis; peg는 EEF에 rigidly attached | No | precise geometry/clearance는 task setup에 알려져 있다. [Assumptions and Table II, PDF pp.3,5] |
| Physical Parameters | 기타 | material/clearance는 task setup에 정의되나 actor의 별도 parameter input은 아님 | No | geometry/material variants로 real transfer를 평가한다. [Table II and Sec. V-C, PDF pp.5-7] |

## 6. Missing Object Information and Compensation

Exact contact configuration/locality 미제공
→ flange 6-axis F/T + relative peg-hole kinematics + parameterized contact primitives
→ contact 유무, overload, desired insertion force와 search/align sequence를 제어한다. [Secs. III-A, IV, PDF pp.3-5]

F/T가 제공하지 못한 stable contact-state semantics
→ 현재 방법은 pose 중심 의사결정과 hand-designed MP constraints에 의존
→ 저자는 contact-model sim-real gap과 반복적 wrong MP 선택을 실패 원인으로 보고, force를 RL observation에 더 직접 통합하고 tactile을 추가하는 것을 향후 과제로 제시한다. [Secs. V-C and VI, PDF p.7]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [전체 PDF pp.1-8; tactile integration은 future work]

### 7.2. Preprocessing

사용하지 않음. [전체 PDF pp.1-8; tactile integration은 future work]

### 7.3. Policy Representation

사용하지 않음. [전체 PDF pp.1-8; tactile integration은 future work]

### 7.4. Retained Information

사용하지 않음. [전체 PDF pp.1-8; tactile integration은 future work]

### 7.5. Removed / Unavailable Information

사용하지 않음. [전체 PDF pp.1-8; tactile integration은 future work]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Franka Panda flange에 장착한 ATI Gamma IP60 6-axis force/torque sensor. libfranka torque estimate는 insert motion에 충분히 정밀하지 않아 별도 sensor를 쓴다. [Sec. V-A, PDF p.5]

### 8.2. Representation

external wrench f_ext,t; component-wise zero/nonzero contact mask; direction projection f_ext^T u; force/torque thresholds; desired wrench [0,0,-f_d,0,0,0]. [Secs. III-A and IV, PDF pp.3-5]

### 8.3. Role

free/in-contact MP family 선택, contact detection, primitive success/failure, overload termination, insertion force/torque regulation, policy state. [Secs. III-A and IV, PDF pp.3-5]

### 8.4. Required Assumptions

single rigidly grasped peg, known task frame/insertion axis, initial hole pose error <1 mm/<1°, external wrench near zero in free space, calibrated flange F/T, operational-space dynamics. [Sec. IV assumptions, PDF p.3]

### 8.5. Reported Limitation / Ambiguity

F/T로 exact contact location/configuration을 복원하지 않는다. 저자는 force가 주로 free/in-contact action subspace를 나눌 뿐 pose 중심 policy의 contact-model sim-real gap을 해결하지 못했다고 명시한다. [Secs. V-C and VI, PDF p.7]

## 9. Other Observations

- Proprioception: EEF pose/robot kinematics로 relative peg-hole pose를 매 step 갱신한다.
- Vision: initial hole pose를 <1 mm/<1°로 estimate한다고 가정하며 visual servoing은 가능한 예시다. 실행 중 continuous vision tracking을 명시하지 않는다.
- Goal: hole task frame과 insertion goal.
- History / previous action / recurrent state: actor input으로 명시되지 않는다.
- State estimator: 초기 hole pose estimator는 외부 모듈로 가정하며 구체 구현은 미명시이다.

## 10. Tactile–Other Modality Relationship

Tactile은 사용하지 않는다. F/T는 global wrench와 contact event/force regulation을 제공하고, relative pose는 search progress와 geometric error를 제공한다. 이 결합은 contact location을 직접 추정하지 않으며 known geometry·accurate initial task frame·rigid grasp가 방법을 성립시킨다. 저자는 force/tactile 부족을 failure analysis와 future work에서 직접 인정한다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | noisy estimated relative pose + external F/T | simulation에서도 actual hole pose가 아니라 randomized perception-error task frame으로 observation을 만든다. [Sec. V-A, PDF p.5] |
| Critic | Not stated | PPO critic input 미명시 | asymmetric privileged critic은 보고하지 않는다. [Sec. V-A, PDF p.5] |
| Reward | No | same noisy estimated relative pose and MP success signal | estimated hole pose로 task frame, observation, reward를 계산한다고 명시한다. [Sec. V-A, PDF p.5] |
| Termination | No | MP thresholds/timeouts and estimated goal position | real에서도 F/T와 kinematic estimate로 구현 가능하다. [Secs. III-A and IV, PDF pp.3-4] |
| Curriculum | No | episode마다 perception error sampling | GT curriculum은 없다. [Sec. V-A, PDF p.5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| parameterized MP action space가 학습 효율/성공률을 높인다. | Controlled comparison | hybrid vs discrete MP vs continuous ee-pose | 60% success까지 simulation samples가 discrete의 약 절반이며 최종 success도 높다. | Sec. V-B; PDF PDF p.6 ; Fig. 4-5 |
| F/T/kinematic primitive 정책이 real insertion에 transfer된다. | Controlled comparison | hybrid vs discrete vs fixed-sequence over six peg-hole pairs | hybrid가 대체로 discrete보다 높은 success와 짧은 time; ee-pose는 큰 contact force로 항상 실패. | Sec. V-C; PDF PDF pp.6-7 ; Fig. 6 |
| pose 중심 상태가 contact sim-real gap에 취약하다. | Failure analysis | physical rollout failures | 이미 접촉 후 move-until-contact 반복, fit/align failure; 저자는 contact force를 RL observation에 더 직접 포함할 것을 제안한다. | Sec. V-C; PDF PDF p.7 |

## 13. Author-stated Limitations

action primitives가 허용하는 motion으로 행동 다양성이 제한된다. policy가 주로 kinematics에 의존하고 force는 free/in-contact 분리에만 쓰여 contact modeling sim-real gap과 object-size 차이에 취약하다. low-level primitive controller가 complex dynamics의 성능 상한을 정한다. [Secs. V-B-C and VI, PDF pp.6-7]

## 14. Author-stated Future Work

dummy free-motion primitive를 추가하고, contact force를 RL observation에 더 직접 포함하며, tactile information과 advanced robust low-level control laws를 통합할 것을 제시한다. [Secs. V-B-C and VI, PDF pp.6-7]

## 15. Review-relevant Findings

- actor state는 peg-hole relative pose와 external 6D F/T로 정의된다.
- Gamma IP60 flange F/T를 사용하며 joint-torque estimate와 구분된다.
- F/T는 contact detection, MP feasibility/termination, desired force regulation을 담당한다.
- contact locality는 추정하지 않으며 accurate initial hole pose, known geometry, rigid grasp를 가정한다.
- simulation reward도 randomized estimated hole frame을 사용하므로 actual pose oracle로 기록하지 않는다.
- 저자는 tactile 통합을 명시적 future work로 제시한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | Sec. IV, PDF p.4 |
| Object pose | Assumptions and Sec. V-A, PDF pp.3,5 |
| Tactile | 사용하지 않음; future work Sec. VI, p.7 |
| F/T | Secs. III-A, IV and V-A, PDF pp.3-5 |
| Reward | Eq. (3), PDF p.4; noisy estimate Sec. V-A, p.5 |
| Critic | Sec. V-A, PDF p.5; input 미명시 |
| Ablation | Figs. 4-6, PDF pp.6-7 |
| Limitation | Secs. V-C and VI, PDF p.7 |
