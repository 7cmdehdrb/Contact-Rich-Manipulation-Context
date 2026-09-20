# Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B066`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Jiahe Pan; Stelian Coros; Jitendra Malik; Toru Lin
- Year: 2026
- Venue: arXiv preprint
- DOI / arXiv: Not stated / 2605.28812v1
- PDF version: arXiv v1 (27 May 2026)
- Page count: 18
- SHA-256: `f022d8c38412db7bbb55839a936b1a11caa9af4fbf4c3b0ffd701da60731e508`
- PDF filename: Pan 등 - 2026 - Beyond Binary Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation.pdf
- 확인 범위: PDF pp.1–18 전체(본문, Limitations, Appendices A–F); Tables 1–6와 Figures 1/11–13 렌더 확인.

## 2. Relevance to This Review

`Relevant`

Binary tactile가 힘 크기와 접촉 위치를 버리는 문제를 직접 비교하고, 3D force와 3D contact position을 보존하는 CoP 표현이 blind manipulation을 어떻게 개선하는지 실험한다. Actor의 proprioception·previous action·recurrent history와 critic/reward의 simulator GT를 분리할 수 있어 본 Review 질문에 직접적인 근거를 제공한다.

## 3. Task

16-DOF Allegro hand로 (1) 이미 파지한 peg를 고정 hole에 삽입하고 (2) 네 fingertip 위의 plate에서 ball을 중심에 유지한다. 두 과제 모두 실행 vision 없이 proprioception과 contact sensing만 쓰며, object–environment secondary contact를 fingertip의 primary contact로 간접 추론해야 한다. [§4, pp.5–7]

## 4. Method

### 4.1. Overall Pipeline

XELA uSkin 3-axis taxel forces → calibrated differentiable taxel-to-CoP mapping → sensor별 3D resultant force + 3D contact position(실험에서는 normal force만) → current joint angles + previous action과 결합 → GRU actor(PPO) → 16 joint-position increments → EMA → PD joint control. [§3.1–3.4 pp.2–5; Appendix D–E pp.15–17]

### 4.2. Observation

Actor는 현재 16 joint angles, previous action, 선택한 contact representation(base/bin/mag/vec/pos/taxel/CoP)을 받는다. CoP/taxel은 flatten한다. GRU hidden state가 시간 문맥을 유지한다. Critic은 actor observation 외에 peg/plate/ball state와 goal 관련 GT를 추가로 받는다. [§4 p.5; Appendix E.1 p.16]

### 4.3. Action

16차원 target joint-position increment. [-1,1] clipping, task별 scale(0.03/0.05), EMA 0.5를 적용해 commanded joint target에 누적한다. [Appendix E.2, p.16]

### 4.4. Controller

각 joint target을 PD가 추종한다. Insertion은 P=3.0, D=0.1, balancing은 P=6.0, D=0.15를 사용한다. [Appendix E.2, p.16]

### 4.5. Learning / Optimization Method

IsaacLab에서 asymmetric actor–critic PPO와 domain randomization을 사용한다. Actor와 critic은 동일한 recurrent architecture를 쓰되 critic만 privileged task state를 추가로 받는다. 별도 teacher–student distillation 없이 aligned CoP를 zero-shot transfer한다. [§4 p.5; Appendix E pp.16–18]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Actor에는 current object position vector가 없음 | 해당 없음 | Peg/plate/ball position은 critic·reward·probe용 simulator GT이며 actor 입력이 아니다. [§3.4–4 and Appendix E, PDF pp.5–8,16–18] |
| Orientation | 미제공 | Actor에는 current object orientation vector가 없음 | 해당 없음 | Peg/plate rotation은 critic·reward에서만 사용한다. [§3.4–4 and Appendix E, PDF pp.5–8,16–18] |
| Shape / Geometry | 미제공 | Actor에 mesh/CAD/category/dimension을 제공하지 않음 | 해당 없음 | Hole은 환경에 고정되고 여러 peg shape로 평가하지만 shape ID는 actor 입력이 아니다. [§4.1 pp.5–6; Appendix F p.18] |
| Physical Parameters | 미제공 | Actor에 mass/friction을 제공하지 않음 | 해당 없음 | Mass/friction은 domain randomization 및 latent probing에만 사용한다. [§4.2 pp.7–8; Appendix E.4 p.17] |

## 6. Missing Object Information and Compensation

Current object pose/shape/physical parameters 미제공 → CoP의 local contact force·location + joint state + previous action + recurrent hidden state → primary contact 변화에서 secondary contact와 object dynamics를 간접 추론해 행동을 조정한다.

Binary contact가 버리는 force magnitude와 spatial contact location → CoP가 두 성분을 함께 보존 → insertion recovery와 OOD initialization 성능이 향상된다. 이 역할은 Table 1의 binary/vec/pos/CoP 비교로 직접 검증된다. [§4.1, pp.5–6]

## 7. Tactile

### 7.1. Raw Sensor

Allegro hand의 fingertips, phalanges, palm에 XELA uSkin arrays를 배치한다. 각 taxel은 3-axis force를 출력하며 sensor array는 grid 형상이다. [§3.2/§4, pp.2,5]

### 7.2. Preprocessing

Taxel origin/rotation을 calibration하고 stress-distribution model로 normal/shear 분해와 spreading을 모델링한 뒤, 최적화로 resultant CoP force를 복원한다. Idle taxel threshold와 sim–real mapping calibration, observation noise/delay randomization을 사용한다. [§3.2–3.4, pp.2–5; Appendix E.4 p.17]

### 7.3. Policy Representation

Sensor별 3D resultant contact force vector와 3D Cartesian contact position. 다만 실험의 sim–real observation은 unreliable simulated shear 때문에 surface-normal force component로 제한한다. 비교 표현은 array별 binary contact, magnitude, force vector only, position only, raw taxel이다. [§3.1/§3.4, pp.2,5]

### 7.4. Retained Information

Binary보다 force magnitude/direction과 sensor-frame spatial contact location을 보존한다. GRU는 이 순간 표현의 시간 변화를 내부 state에 축적한다. [§1 p.1; §4 pp.5–8]

### 7.5. Removed / Unavailable Information

CoP는 distributed pressure/multi-contact patch를 한 resultant force와 centroidal point로 축약하고 sensor-specific detail을 버린다. 구현은 shear를 제거한다. Global object pose/shape는 포함하지 않는다. [§3.1 footnote p.2; §3.4 p.5; §6 p.8]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

XELA uSkin taxel에서 복원한 local fingertip force이다. Wrist 6-axis F/T나 joint-torque estimated wrench는 사용하지 않는다. [§3.2/§4, pp.2,5]

### 8.2. Representation

CoP의 3D resultant force vector; sim–real 실험에서는 surface-normal component만 사용. Baselines는 magnitude-only와 vector-only를 포함한다. [§3.1/§3.4, pp.2,5]

### 8.3. Role

Actor contact observation으로 접촉 하중과 위치를 함께 제공한다. Insertion recovery와 ball balancing의 즉각적인 load regulation에 사용된다. [§4.1–4.2, pp.6–7]

### 8.4. Required Assumptions

각 sensor array의 calibrated taxel geometry/orientation, compliant-layer stress distribution model, resultant single-force/centroid approximation, sim–real contact alignment이 필요하다. [§3.1–3.4, pp.2–5]

### 8.5. Reported Limitation / Ambiguity

Distributed/multiple contact pressure를 완전히 나타내지 못하고 shear simulation이 불안정하다. Simulator는 task-object contact만 보고하지만 실물 sensor는 self/environment contact에도 반응한다. [§6, p.8]

## 9. Other Observations

Proprioception은 current/commanded joint angles이며 actor 입력이다. Previous action도 actor 입력이다. GRU hidden state가 명시적 frame stack 대신 history를 유지한다. Vision은 sensor-delay 측정 및 연구 분석에는 사용되지만 실행 policy observation에는 없다. Goal/current object state는 actor에 제공되지 않는다. [§3.4–4 p.5; Appendix D–E pp.15–16]

## 10. Tactile–Other Modality Relationship

Tactile CoP는 local contact force와 location을 제공하고 proprioception/previous action/GRU는 hand motion과 temporal context를 제공한다. F/T는 병용하지 않는다. Binary representation과 CoP를 동일 과제에서 직접 비교하여, insertion에서는 force와 position이 서로 보완적임을 vec-only/pos-only ablation으로 보인다. Ball balancing에서는 force-only와 CoP가 비슷해 location의 추가 이득은 task-dependent하다. [Tables 1–2, pp.6–7]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | Current joint angles; previous action; contact representation; GRU state | 실행에서 object GT 불필요. [Appendix E.1, p.16] |
| Critic | Yes | Peg/plate/ball position, rotation, velocity, goal vector/distance, goal reached | Asymmetric critic의 simulation-only input. [Appendix E.1/Table 4, p.16] |
| Reward | Yes | Goal distance/reached, object rotation, plate/ball state and contact indicators | Simulator task state로 계산. [Appendix E.3/Table 5, p.16] |
| Termination | Yes | Goal reached 또는 ball fallen/task resets | 명시된 success/fall indicator가 episode 판정에 사용된다. [Appendix E.3, p.16] |
| Curriculum | Not stated | Not stated | Curriculum 사용은 원문에서 확인되지 않음; domain randomization은 사용. [Appendix E.4, p.17] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| CoP가 binary/raw taxel보다 insertion에 유용 | Representation ablation | base; binary; magnitude; vector; position; raw taxel; CoP | Overall success: binary 0.53, raw taxel 0.48, CoP 0.78; OOD init에서 CoP 0.63으로 최고. | §4.1; PDF p.6 ; Table 1 ; Fig.4 |
| CoP force와 contact position의 상보성 | Representation ablation | force-vector only vs position-only vs CoP | Insertion overall 0.67/0.50/0.78로 결합 CoP가 높다. | §4.1; PDF p.6 ; Table 1 |
| 필요한 tactile 정보는 task-dependent | Representation ablation | base/bin/mag/vec/pos/taxel/CoP | Ball balancing TTF는 vec 4.52s, CoP 4.60s로 유사하고 binary 1.99s; 저자는 force alone이 충분할 수 있다고 설명한다. | §4.2; PDF p.7 ; Table 2 ; Fig.5 |
| Temporal recurrent state의 효용 | Controlled comparison | GRU recurrent policy vs MLP with 3/5/10/20 stacked observations | 두 과제에서 recurrent policy가 sample efficiency와 convergence quality를 개선한다. | Appendix D; PDF p.15 ; Fig.12 |

## 13. Author-stated Limitations

CoP는 sensor-specific detail과 arbitrary distributed contact를 버린다. 실험 구현은 simulated shear의 불안정 때문에 normal force만 사용하며 simulation은 self/environment contact를 누락한다. 고정-base hand와 XELA uSkin 범위에 한정된다. [§6, p.8]

## 14. Author-stated Future Work

Arm–hand systems, full-hand tactile coverage, 다른 tactile sensor type으로 확장하고, CoP를 imitation learning과 sample-efficient real-world RL에 통합하는 방향을 제시한다. [§6(C), p.8]

## 15. Review-relevant Findings

- 실행 actor에는 current object pose, shape, mass/friction GT가 없다.
- Binary tactile는 array별 contact presence만 남기지만 CoP는 resultant force와 contact location을 남긴다.
- Insertion ablation은 force와 location의 상보성을 보이지만 ball balancing에서는 force-only가 거의 같은 성능이다.
- Critic과 reward/termination은 simulator object state를 사용한다.
- Wrist F/T 없이 tactile force와 proprioception, recurrent state로 blind tasks를 수행한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / pipeline | §3.4–4 p.5; Appendix E.1 p.16 |
| Object pose / privileged state | Appendix E.1/Table 4 p.16 |
| Tactile / force | §3.1–3.4 pp.2–5 |
| Action / controller | Appendix E.2 p.16 |
| Reward / termination | Appendix E.3/Table 5 p.16 |
| Ablation | Tables 1–2 pp.6–7; Fig.12 p.15 |
| Limitation / Future | §6 p.8 |
| Domain randomization | Appendix E.4 p.17 |
