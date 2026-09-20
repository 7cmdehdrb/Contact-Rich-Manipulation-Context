# FACTR 2: Learning External Force Sensing for Commodity Robot Arms Improves Policy Learning

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B061
- Authors: Steven Oh; Jason Jingzhou Liu; Tony Tao; Philip Han; Kenneth Shaw; Satoshi Funabashi; Ruslan Salakhutdinov; Deepak Pathak
- Year: 2026
- Venue: Not stated
- DOI / arXiv: Not stated / 2606.12406v1
- PDF version: arXiv v1, 10 June 2026; Appendix A–D
- Page count: 22
- SHA-256: e289338c5cd2be42e02c41d700e499d6e6bb625c877660812b570031d678e295
- PDF filename: Oh 등 - 2026 - FACTR 2 Learning External Force Sensing for Commodity Robot Arms Improves Policy Learning.pdf
- 읽은 범위: PDF pp.1–22 본문 및 포함된 부록을 새로 확인; 핵심 표·그림 렌더링 확인

근거는 이번 배치의 PDF 원문이며 기존 상세 노트는 사용하지 않았다. 페이지는 PDF의 1-based page이다.

## 2. Relevance to This Review

**Relevant**. Motor current와 proprioceptive history에서 external joint torque를 추정하고, 이를 policy input 및 training sample selection에 각각 사용하는 근거를 제공한다. Dedicated wrist F/T나 distributed tactile 없이 contact 정보가 어떤 모델·보정 가정에 의해 얻어지는지 분석할 수 있다.

## 3. Task

NEXT force-feedback teleoperation 및 FIRST imitation policy로 LEGO assembly, NIST belt/insertion, tool cleanup, cap screwing을 수행한다. Bimanual Piper에서 task당 250 demonstrations, 20 rollouts; primary metric은 completed stages의 task progress이며 cap over-turn당 0.02 penalty다. (§6 p.6; Appendix C pp.16–18)

## 4. Method

### 4.1. Overall Pipeline

Motor current×torque constant→measured joint torque; q/qdot/target-error의 50-step history→LSTM free-space torque; 차이→NEXT external joint torque. RGB+joint/gripper state+current NEXT torque→flow-matching DiT/ACT→30-step joint/gripper target chunk→robot controller. Offline NEXT torque→contact phase labels→FIRST resampling은 별도 학습 경로다. (§4–5 pp.4–5; Appendix A–B pp.13–17)

### 4.2. Observation

Estimator: q, qdot, desired-current q error의 50-step/100 Hz history. Main policy: 가장 최근 4개 RGB views(2 wrist + 2 overhead), joint positions/gripper widths, estimated external joint torques. Policy에 50-frame history가 들어가는 것은 아니다. Dedicated object 6D pose, shape, material parameters는 입력하지 않는다. (§6 p.6; Appendix A.1–2 pp.13–14; B p.16)

### 4.3. Action

Absolute joint angles+gripper width의 horizon 30 action chunk. Flow matching 또는 ACT에서 동일 input/action 사용. (Appendix B pp.16–17)

### 4.4. Controller

Policy low-level joint tracking details는 미명시. Teleoperation은 follower external joint torque를 gain-scaled leader torque로 반영하며 gravity/friction compensation/null-space regulation을 사용한다. Estimator는 실제 100 Hz. (§6.1 p.6; Appendix A.1/A.5 pp.13,15)

### 4.5. Learning / Optimization Method

NEXT는 10 min contact-free motion의 measured motor torque를 MSE로 1 min 학습한다. FIRST는 torque L1 norm의 hysteresis로 contact를 식별하고 onset 전 1 초를 pre-contact로 지정해 weighted random sampling 한다. 기본 flow matching BC, ACT에도 적용. 실물 센서 GT는 NEXT training target이 아니라 Franka validation reference다. (§4–6 pp.4–6)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Live RGB image tokens; explicit object position 없음 | RGB 매 observation | Camera image를 numerical object pose tracking으로 세지 않음 (§5 p.5; Appendix B p.16) |
| Orientation | 기타 | Live RGB; explicit object orientation 없음 | RGB 갱신 | Joint targets는 robot state (§5 p.5; Appendix B p.16) |
| Shape / Geometry | 기타 | RGB appearance와 demonstration prior | 영상 갱신 | CAD/mesh/explicit dimensions 제공은 미명시 (§5–6 pp.5–6) |
| Physical Parameters | 미제공 | Object physical parameter input 없음 | 없음 | Robot-specific inverse dynamics와 motor constant K 필요 (§4 p.4; §9 p.9) |

## 6. Missing Object Information and Compensation

접촉/하중이 영상과 instantaneous current만으로 분리되기 어려움 → proprioceptive 50-step history 기반 free-space dynamics subtraction → compact external joint torque를 policy에 제공한다. 별도로 short pre-contact/contact segment가 training에서 희소함 → torque-derived phase resampling → alignment/recovery와 contact action 학습 빈도를 높인다. 두 효과는 Appendix D.5에서 분리 비교한다. (pp.19–22)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. (§4–6 pp.4–6; Appendix B p.16)

### 7.2. Preprocessing

사용하지 않음. (§4–6 pp.4–6; Appendix B p.16)

### 7.3. Policy Representation

사용하지 않음. (§4–6 pp.4–6; Appendix B p.16)

### 7.4. Retained Information

사용하지 않음. (§4–6 pp.4–6; Appendix B p.16)

### 7.5. Removed / Unavailable Information

사용하지 않음. (§4–6 pp.4–6; Appendix B p.16)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Motor current 기반 measured motor torque에서 learned free-space torque를 뺀 external joint torque. Wrist 6D F/T 또는 end-effector 6D wrench 추정이 아니다. Franka built-in torque estimate는 평가용 reference. (§3–4 pp.3–4; §6.1 p.6)

### 8.2. Representation

Joint별 continuous external torque; FIRST segmentation은 L1 norm→hysteresis binary contact→free/pre-contact/contact label. Policy는 continuous estimate를 받는다. (§4–5 pp.4–5)

### 8.3. Role

Teleoperation haptic feedback; policy observation; offline demonstration phase labeling/resampling. Contact location 추정 알고리즘은 제공하지 않는다. (§5–6 pp.5–6)

### 8.4. Required Assumptions

Known/accurate motor torque constant K; free-motion dataset은 contact 없어야 함; robot-specific training과 joint/current/target measurements. Model residual을 external torque로 해석한다. (§3–4 pp.3–4; §9 p.9)

### 8.5. Reported Limitation / Ambiguity

Current residual에 friction/stiction/backlash/hysteresis/temperature/noise 등이 섞일 수 있음. K가 틀리면 absolute scale에 외부 force calibration 필요, arm variation에 retraining 가능성. Net-wrench multi-contact localization ambiguity는 직접 논의하지 않음. (§3 p.3; §9 p.9)

## 9. Other Observations

Estimator의 50-step LSTM은 sliding-window마다 hidden state를 reset한다. Policy는 current observation만 사용한다. Command error는 estimator input이며 policy previous-action input으로 동일시하지 않는다. Vision은 continuous 4-camera, goal은 task-specific demonstrations에 내재; explicit goal pose input 미명시. (Appendix A.1 p.13; B p.16)

## 10. Tactile–Other Modality Relationship

Distributed tactile은 없다. Estimated torque는 RGB/proprioception에 contact-sensitive signal을 추가하고 raw current보다 나은 조건을 보인다. Torque의 진폭·시간 변화가 알려주는 contact와 spatial locality 복원은 서로 다르며 후자는 본 논문의 검증 대상이 아니다. (Appendix D.5–6 pp.19–22)

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부·비고 |
| --- | --- | --- | --- |
| Actor | 해당 없음 | 비-RL | 해당 없음 (§4–6 pp.4–6: supervised estimator/behavior cloning) |
| Critic | 해당 없음 | 비-RL | 해당 없음 (§4–6 pp.4–6: supervised estimator/behavior cloning) |
| Reward | 해당 없음 | 비-RL | 해당 없음 (§4–6 pp.4–6: supervised estimator/behavior cloning) |
| Termination | 해당 없음 | 비-RL | 해당 없음 (§4–6 pp.4–6: supervised estimator/behavior cloning) |
| Curriculum | 해당 없음 | 비-RL | 해당 없음 (§4–6 pp.4–6: supervised estimator/behavior cloning) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| NEXT estimation | Controlled comparison | Franka contact: NEXT vs FILIC vs disturbance observer | Average joint L1 error 0.547±0.348 vs 4.395±1.531 vs 1.471±0.761 Nm; reference는 Franka estimate | Table 1 p.7 |
| History/model | Input ablation; Representation ablation | MLP/GRU/LSTM; q/qdot/tracking error; 10/25/50 steps | 최종 LSTM H50 q/qdot/error 선택; 모든 cell에서 일률 우위는 아님 | Table 4 p.14 |
| Torque input과 resampling 분리 | Input ablation; Controlled comparison | w/wo torque × None/PC/PC+C sampling | Flow Belt PC: 0.213(no torque) vs 0.767(torque); torque 기본 0.431. Table 9는 success rates라 명명하나 main metric task progress와 혼용에 주의 | Table 9 p.20 |
| Raw current vs estimated torque | Representation ablation | ACT; ACT+current; ACT+external torque | NIST insertion 0.220/0.431/0.567; cap 0.440/0.440/0.525 | Table 10 p.22 |
| Phase별 학습 효과 | Controlled comparison | Contact-only; pre-contact; both | 평균 task progress 0.670/0.818/0.811; task별 차이 있음 | Table 2 p.8 |

## 13. Author-stated Limitations

Absolute torque scale은 motor constant K에 의존하며 오차가 있으면 external force sensor calibration이 필요하다. Robot-specific이어서 hardware variation에 retraining이 필요할 수 있다. 과도한 resampling은 training coverage를 줄여 성능을 낮출 수 있고 Piper의 contact torque 정량 GT 평가는 센서 부재로 수행하지 못했다. (§9 p.9; §6.1 p.6; Appendix D.4 pp.18–20)

## 14. Author-stated Future Work

독립적인 구체적 future-work 계획은 미명시. §9의 retraining/calibration은 한계 및 적용 조건이며, 이미 검증된 보편적 전이로 기록하지 않는다. (pp.8–9)

## 15. Review-relevant Findings

- External joint torque 추정은 50-step proprioceptive history를 사용하지만 policy는 current observation만 받는다.
- Torque는 runtime input과 offline phase label의 두 역할을 하며 각 효과를 비교했다.
- Binary contact label은 학습 sample selection용이며 regional tactile 표현이 아니다.
- NEXT training에는 dedicated force GT가 없고 Franka 평가 때 reference로만 사용한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation/Object pose | §5 p.5; Appendix B p.16 |
| Tactile/F/T | §3–5 pp.3–5 |
| History | Appendix A.1–2 pp.13–14 |
| GT/Training | §4 p.4; §6.1 p.6 |
| Ablation | Tables 2/4/9/10 pp.8/14/20/22 |
| Reward/Critic | 비-RL, 해당 없음 |
| Limitation/Future | §9 p.9 |
