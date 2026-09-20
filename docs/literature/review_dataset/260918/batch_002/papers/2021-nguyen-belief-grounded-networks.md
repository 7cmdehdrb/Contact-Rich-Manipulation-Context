# Belief-Grounded Networks for Accelerated Robot Learning under Partial Observability

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B060
- Authors: Hai Nguyen; Brett Daley; Xinchao Song; Christopher Amato; Robert Platt
- Year: 2021 (PDF version); CoRL 2020
- Venue: CoRL 2020
- DOI / arXiv: Not stated / 2010.09170v5
- PDF version: arXiv v5, 21 October 2021; CoRL 2020 header; Appendix A–E
- Page count: 14
- SHA-256: 8e3be2a708c8895163badb862df69b46c9be7eba05a5b575744368219a51f9f9
- PDF filename: Nguyen 등 - 2021 - Belief-Grounded Networks for Accelerated Robot Learning under Partial Observability.pdf
- 읽은 범위: PDF pp.1–14 본문 및 포함된 부록을 새로 확인; 핵심 표·그림 렌더링 확인

근거는 이번 배치의 PDF 원문이며 기존 상세 노트는 사용하지 않았다. 페이지는 PDF의 1-based page이다.

## 2. Relevance to This Review

**Relevant**. Object position을 보지 못하는 contact manipulation에서 observation-action history를 belief supervision으로 학습한다. 논문이 force-feedback이라 부르는 신호는 finger coordinate/angle이며 별도 wrist F/T와 혼동하지 않아야 한다. 학습 전용 privileged belief와 실행 관측을 명확히 비교할 수 있다.

## 3. Task

UR5e+2DoF compliant gripper로 stack의 top plate 찾기/잡기, 두 bump 중 오른쪽만 밀기(1D), 두 bump를 접촉 탐색한 뒤 큰 것을 잡기(2D)를 수행한다. TopPlate/2D는 grasp action으로 끝나며, 1D는 어느 bump든 움직이면 종료한다. (§5.2–5.3 pp.5–7)

## 4. Method

### 4.1. Overall Pipeline

Finger coordinate/angle + previous action → GRU history features → A2C action distribution → discrete direction/compliance or grasp → impedance-controlled finger/robot motion. 별도 belief reconstruction head는 학습용이다. (Fig. 1 p.4; Table 3 p.12)

### 4.2. Observation

Main Ah-Ch+BGN actor와 critic 모두 normalized observation-action history를 받으며 finger coordinate/angle은 관측 가능, object locations는 보이지 않는다. True belief는 input이 아니라 actor/critic representation의 auxiliary target이다. 비교 Ah-Cs는 critic state, Ah-Cb는 critic belief, Ab-Cb는 actor/critic belief를 직접 받는다. (§3 pp.3–4; §5 p.4; Appendix B p.12)

### 4.3. Action

TopPlate: up/down/grasp 3개. TwoBumps1D: left/right × compliant/stiff 4개. TwoBumps2D: cardinal 4방향+grasp 5개. (§5.2 pp.5–6; Table 5 p.13)

### 4.4. Controller

Finger impedance controller가 compliant/stiff mode를 바꾼다. 실제 arm trajectory tracking/controller gain은 미명시. 원문은 force-feedback task라 부르지만 관측 목록에 numerical wrench를 제시하지 않는다. (§5.2–5.3 pp.5–6)

### 4.5. Learning / Optimization Method

A2C+true/reconstructed belief cross-entropy, actor·critic에 각각 적용. GRU 256→FC 256. Belief는 discretized simulation transition/observation model로 계산한다. Simulation 10 seeds; sparse success+1 외 0. 실물 finetuning 없이 100% 보고하나 실물 trial 분모는 본문/부록에서 확인되지 않는다. (§3 p.3; §5 pp.5–8; Appendix A–C pp.11–13)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Main policy에는 current object position 없음 | 없음 | Actor history에서 object belief 관련 feature 학습; exact belief input과 다름 (§5.2 pp.5–6) |
| Orientation | 미제공 | Object orientation 입력 없음 | 없음 | Finger angle은 robot contact deflection cue (§5.2 pp.5–6) |
| Shape / Geometry | 기타 | Discrete task geometry: fixed motion plane/line, plate range, 2D grid, ordered bumps | 고정 | Full unknown geometry manipulation이 아니라 constrained MOMDP (§5.2 pp.5–6; Appendix C/E pp.13–14) |
| Physical Parameters | 미명시 | Object physical parameter explicit input은 없음 | 미명시 | Belief transition/observation model에 대한 simulator knowledge를 학습에 사용 (§2–3 pp.2–3) |

## 6. Missing Object Information and Compensation

Object locations 미관측 → compliant finger position/angle + action/observation history + GRU + training-only true-belief reconstruction → 접촉으로 얻은 여러 단서를 history representation에 축적한다. 저자들은 실제 belief tracker를 실행 때 계산할 필요 없이 POMDP policy를 수행하는 이점을 주장하고 baseline 비교로 검증한다. 단, known task geometry와 simulator belief model에 의존하는 학습 조건이 있다. (§3 p.3; §5 pp.5–8)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. (§5.2–5.3 pp.5–6: 별도 tactile array/image 미사용; proprioceptive contact feedback)

### 7.2. Preprocessing

사용하지 않음. (§5.2–5.3 pp.5–6: 별도 tactile array/image 미사용; proprioceptive contact feedback)

### 7.3. Policy Representation

사용하지 않음. (§5.2–5.3 pp.5–6: 별도 tactile array/image 미사용; proprioceptive contact feedback)

### 7.4. Retained Information

사용하지 않음. (§5.2–5.3 pp.5–6: 별도 tactile array/image 미사용; proprioceptive contact feedback)

### 7.5. Removed / Unavailable Information

사용하지 않음. (§5.2–5.3 pp.5–6: 별도 tactile array/image 미사용; proprioceptive contact feedback)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

별도 wrist 6D F/T/force sensor 출력은 명시되지 않는다. Force-feedback이라는 명칭은 compliant finger coordinate/angle의 접촉 반응을 가리킨다. (§5.2–5.3 pp.5–6)

### 8.2. Representation

관측은 robot finger coordinate/angle; net wrench vector 아님. (§5.2 pp.5–6)

### 8.3. Role

Finger deflection으로 contact/relative size를 추론; stiffness를 전환해 접촉탐색과 pushing/grasping을 구분. (§5.2–5.3 pp.5–7)

### 8.4. Required Assumptions

F/T-only localization은 해당 없음. 손가락이 bump를 놓치지 않는 1D motion, known bump order/size task, discrete model 및 관측 가능한 finger state를 가정. (§5.2 pp.5–6; Appendix E p.14)

### 8.5. Reported Limitation / Ambiguity

한 번의 observation으로 object state를 구분할 수 없는 partial observability를 다룸. Net wrench locality/multi-contact ambiguity의 분석은 아님. (§1 p.1; §5.2 pp.5–6)

## 9. Other Observations

Proprioception의 contact-induced finger angle이 핵심이다. Vision, object pose, tactile image는 사용하지 않는다. Previous action과 GRU recurrent hidden state를 사용하며 finite fixed-history 길이로 대체하지 않는다. Auxiliary reconstructed belief를 정책 입력으로 되먹이는 runtime estimator도 아니다. (Table 3 p.12)

## 10. Tactile–Other Modality Relationship

별도 tactile modality와 F/T 병용 관계는 해당 없음. Proprioception-only contact observation이 action history 및 privileged belief supervision과 어떻게 결합되는지 비교하는 사례다. (§3–5 pp.3–8)

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부·비고 |
| --- | --- | --- | --- |
| Actor | No input; Yes training supervision | History input; GT belief reconstruction target | 실행 때 belief/GT 없이 sensor/action history 필요 (§3 p.3; Table 3 p.12) |
| Critic | No input; Yes training supervision | Main BGN history input+true-belief loss; Ah-Cs baseline만 GT state input | Critic-only privileged input으로 main method를 오기하지 않음 (§5 p.4; Table 3 p.12) |
| Reward | Yes | Success+1: target plate/bump identity, correct move/grasp | Simulator hidden task state로 학습; 실제 policy 입력 아님 (§5.2 pp.5–6) |
| Termination | Yes / action-based | 1D bump movement; plate/2D grasp action; timeout | Object movement와 action-trigger를 구분 (§5.2 pp.5–6; Table 5 p.13) |
| Curriculum | Yes (data/reset/supervision) | Random hidden object initial states; exact belief computation | 별도 curriculum 미명시; simulator model을 auxiliary target 생성에 사용 (§3 p.3; §5.2 pp.5–6; Appendix E p.14) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Belief supervision 효용 | Controlled comparison | Ah-Ch+BGN vs Ah-Ch/Ah-Cs/Ah-Cb/Ab-Cb | 10-seed 평균에서 BGN만 세 robot task 모두 perfect success 도달 | Fig. 4 p.6 |
| Representation 역할 | Controlled comparison | Ab-Cb vs Ab-Cb+BGN; reconstructed vs true belief | Auxiliary loss가 belief-input baseline도 개선; main history-based BGN에는 못 미침 | §5.4 pp.7–8; Figs. 6–7 p.8 |
| 실물 전이 | Controlled comparison | Simulation-trained main policy를 UR5e에 finetuning 없이 실행 | 세 task에서 100% 보고, 평가 trial 수 미명시; simulator baseline 통계와 실물 통계를 동일시하지 않음 | §5.3 pp.6–7 |

## 13. Author-stated Limitations

검증 범위는 discrete-state environments이며 online belief tracking의 계산 부담과 unstructured belief representation의 학습 어려움을 논의한다. 별도 Limitations 절은 없다. (§3 p.3; §6 p.8)

## 14. Author-stated Future Work

Continuous-state task로 확장하고 Gaussian-mixture 등의 parametric belief 또는 particle filter의 approximate belief update를 사용하자는 방향을 제시한다. (§6 p.8)

## 15. Review-relevant Findings

- 실행 policy는 object pose나 true belief 없이 contact-induced proprioception/action history를 쓴다.
- Actor와 critic 모두 GT belief auxiliary supervision을 받는다.
- Force-feedback task 명칭만으로 wrist F/T 입력이라고 기록하면 안 된다.
- Task geometry와 discrete belief model은 강한 사전 조건이다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation/Object pose | §5.2 pp.5–6; Table 3 p.12 |
| Tactile/F/T | §5.2–5.3 pp.5–6: finger feedback |
| Reward/Termination | §5.2 pp.5–6; Table 5 p.13 |
| Critic/Belief GT | §3 p.3; §5 p.4; Appendix B p.12 |
| Ablation | Figs. 4, 6, 7 pp.6,8 |
| Limitation/Future | §6 p.8 |
