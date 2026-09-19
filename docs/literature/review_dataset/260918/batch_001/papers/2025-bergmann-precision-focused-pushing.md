# Precision-Focused Reinforcement Learning Model for Robotic Object Pushing

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B008`. 이번 batch의 제공 PDF를 새로 읽은 분석이다. 페이지 표시는 별도 언급이 없으면 PDF의 1-based page다. 기존 상세 논문 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Lara Bergmann; David Leins; Robert Haschke; Klaus Neumann
- Year: 2025
- Venue: 2025 International Conference on Advanced Robotics and Mechatronics (ICARM), 758–765
- DOI: 10.1109/ICARM65671.2025.11293485
- arXiv: Not stated
- PDF version: publisher
- Page count: 8
- SHA-256: `6f34f73c0f3f8c541e626664cbffa907574b4fd15d289314665edca514483d38`
- PDF filename: Bergmann 등 - 2025 - Precision-Focused Reinforcement Learning Model for Robotic Object Pushing.pdf
- 확인 범위: 제공 PDF 전체(참고문헌 포함); 별도 Appendix 없음. 외부 code/video/supplement는 확인하지 않음.

## 2. Relevance to This Review

`Partially Relevant`

Tactile/F/T를 사용하지 않는 vision–proprioception pushing 연구다. 다만 binary visual representation에 없는 mass/friction 정보를 episode history로 보완한다는 명시적 논리와 memory 비교가 있으므로, 미관측 물성의 history 보완 구조에 한정하여 포함한다. 시각이 없는 실행 또는 tactile 정보손실 보완의 직접 증거로 사용하지 않는다.

## 3. Task

Franka Emika Panda의 push rod로 물체를 평면 목표 위치에 정밀하게 민다. 시뮬레이션은 마지막(50번째) step의 물체 중심–goal 중심 거리가 1 cm 미만일 때 성공이다. Orientation은 reward/성공 조건에 들어가지 않는다. 실물은 물체 위치 GT가 없어 성공을 육안 판정하므로 1 cm 오차를 계측 검증했다고 읽으면 안 된다. [§IV-D–E; §IX-B, PDF pp.3,6]

## 4. Method

### 4.1. Overall Pipeline

Glass table 아래 RGB camera → color filtering → 64×64 binary object/goal masks → 사전학습 autoencoder의 6D object latent와 6D goal latent + EEF planar position 2D → episode observation sequence → 별도 actor/critic GRU → SAC action $[\Delta x,\Delta y,\mathrm{control\ duration}]$ → custom velocity controller → 수직 push rod를 유지하는 robot motion. [Fig.2; §III–VI, PDF pp.2–4]

### 4.2. Observation

각 관측 $s\in\mathbb{R}^{14}$는 EEF base-frame $(x,y)$ 2D, 현재 object mask latent $z_o\in\mathbb{R}^{6}$, goal mask latent $z_g\in\mathbb{R}^{6}$를 연결한다. Goal mask는 episode 시작 때 물체를 target에 배치하여 생성하고 고정한다. Current object mask는 매 environment step camera observation에서 생성한다. Actor와 critic은 같은 관측 history를 받지만 별도 GRU/MLP weight를 쓴다. Full episode sequence를 재처리하고 마지막 hidden state를 사용하며 초기 hidden state는 zero다. Mass/friction, 명시적 object center/angle GT는 관측에 없다. [§IV-A–B, PDF pp.2–3; §V, PDF pp.3–4]

### 4.3. Action

Action 3D $=[a_x,a_y,a_s]$. $a_x,a_y$는 base-frame desired EEF position offset이며 $[-1,1]$ m 범위다. $a_s\in[10,600]$는 1 ms robot/MuJoCo control cycle을 같은 target으로 실행할 횟수로서 다음 관측까지의 시간을 바꾼다. 50 environment steps는 고정된 물리 실행 시간과 같지 않다. [§IV-C, PDF p.3]

### 4.4. Controller

Custom velocity controller가 desired EEF $(x,y,z)$를 따르면서 push rod가 table에 수직인 제약을 유지한다. 이 기하학적 제약은 RL이 학습하지 않는다. Low-level joint mapping/gain/impedance의 추가 상세는 원문에서 확인되지 않는다. [§VI, PDF p.4]

### 4.5. Learning / Optimization Method

Stable-Baselines3 SAC+HER. Binary mask autoencoder를 먼저 학습하고 GRU는 actor/critic과 함께 학습한다. HER goal relabeling은 관측 밖의 GT goal position도 다시 지정하여 reward를 계산하며, 바뀐 goal encoding에 맞춰 전체 GRU hidden state를 재계산한다. Reward는 GT planar object/goal distance가 1 cm 이상이면 −1, 아니면 0이다. Shape/size/pose/dynamics를 randomize하며 eGRU는 mass와 friction의 곱 분포를 경계 쪽에 더 자주 sampling하도록 바꾼다. 학습 seed 수·총 training steps는 제공 PDF에 미명시다. [§IV-D–V; §VII–VIII, PDF pp.3–4]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | 매 step RGB-derived binary silhouette의 6D latent | 매 environment step | GT center는 reward/evaluation에만 사용 [§IV-A–D, PDF pp.2–3] |
| Orientation | 기타 | Silhouette에 포함되는 현재 방향의 latent cue | 매 environment step | Goal mask에 방향이 포함되지만 orientation reward/goal success 없음 [§IV-A–E; §IX-B, PDF pp.2–3,6] |
| Shape / Geometry | 기타 | Binary object silhouette가 형태·크기 정보를 보존 | 현재 mask 입력 | Full mesh/CAD/dimension 수치 actor 입력 없음 [§IV-A; §VII, PDF pp.2–4] |
| Physical Parameters | 미제공 | Mass/friction coefficient가 binary image에서 관측되지 않음 | 없음 | 명시적 friction estimator output 없음 [§IV-B; §VII–VIII, PDF pp.3–4] |

## 6. Missing Object Information and Compensation

Binary visual image에 mass·friction 정보가 없음 → current/past object visual latent와 EEF position의 전체 episode history → 힘을 가했을 때 물체가 이동한 양을 통해 거동 관련 정보를 hidden state에 담을 수 있도록 한다. 저자가 제시한 보완 논리이며 명시적 마찰계수/힘 estimator를 출력하거나 정확한 parameter identification을 검증한 것은 아니다. GRU는 접촉이 끊긴 corrective motion 중에도 정보를 유지하도록 설계했다. 이 binary representation은 tactile이 아니라 vision이다. [§IV-B, PDF p.3]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. Binary는 RGB에서 만든 visual mask를 가리킨다. [§IV-A–B, PDF pp.2–3]

### 7.2. Preprocessing

사용하지 않음. Binary는 RGB에서 만든 visual mask를 가리킨다. [§IV-A–B, PDF pp.2–3]

### 7.3. Policy Representation

사용하지 않음. Binary는 RGB에서 만든 visual mask를 가리킨다. [§IV-A–B, PDF pp.2–3]

### 7.4. Retained Information

사용하지 않음. Binary는 RGB에서 만든 visual mask를 가리킨다. [§IV-A–B, PDF pp.2–3]

### 7.5. Removed / Unavailable Information

사용하지 않음. Binary는 RGB에서 만든 visual mask를 가리킨다. [§IV-A–B, PDF pp.2–3]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. 논문의 sliding friction force는 simulation 물성으로 정의하는 양이며 측정 F/T 입력이 아니다. [§IV-A–B; §VIII, PDF pp.2–4]

### 8.2. Representation

해당 없음. Actor force/wrench observation 없음. [§IV-A–B, PDF pp.2–3]

### 8.3. Role

해당 없음. Friction-force distribution은 training sampling 설계와 evaluation 조건에 사용한다. [§VIII–IX, PDF pp.4–5]

### 8.4. Required Assumptions

F/T-only 방법에 해당 없음. Visual setup은 아래 camera+glass table로 occlusion을 피하며 controller가 rod orientation을 유지한다. [§III/VI/X, PDF pp.2,4,6]

### 8.5. Reported Limitation / Ambiguity

해당 없음. F/T 한계를 직접 분석하지 않는다. [§IV; §X, PDF pp.2–3,6]

## 9. Other Observations

Proprioception: current EEF planar position을 vision latent에 연결한다. Vision: 현재 object silhouette와 초기 goal mask. History: 전체 episode 관측을 GRU로 처리하며 비교군은 no-history VPM와 최근 5개 Stacked다. Previous action: 별도 actor 입력으로 없음. Recurrent state: actor/critic 각각의 GRU final hidden state. State estimator: 6D visual latent 및 GRU context이며 명시적 pose/force/물성 추정 출력은 없다. [§IV–V/IX-A, PDF pp.2–5]

## 10. Tactile–Other Modality Relationship

Tactile이 없어 tactile–other 관계는 해당 없음. 실제 분석 가능한 관계는 binary vision+proprioception+history다. History ablation의 효과를 tactile history의 효과로 전환하여 인용하면 안 된다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | Object pose GT: No | Current/goal image latent + EEF planar position; GRU history | 실행에는 camera와 EEF state가 필요. 수치 object GT는 관측에서 명시적으로 제외 [§IV-A–D, PDF pp.2–3] |
| Critic | No extra object GT declared | Actor와 같은 history의 별도 GRU/MLP | 추가 privileged critic가 아니라 별도 parameter의 recurrent feature extractor [Fig.2; §IV-B, PDF pp.2–3] |
| Reward | Yes | GT object center and GT goal position | Simulator reward에 필요. 실물 GT 부재로 reward를 계산하지 않음 [§IV-D; §IX-B, PDF pp.3,6] |
| Termination | Episode 종료 GT: No; 평가 GT: Yes | 50-step fixed horizon; 마지막 GT object-goal distance로 sim 성공 평가 | 실물도 50 steps이나 성공은 visual inspection [§IV-E; §IX-B, PDF pp.3,6] |
| Curriculum | Yes for training data generation | HER GT goal relabeling/reward recomputation; geometry·mass/friction·initial pose sampling | 명시적 curriculum schedule은 없음. Dynamics sampling 변경을 실행 입력으로 기록하지 않음 [§V/VII–VIII, PDF p.4] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| History는 visual observation에 없는 물성 정보의 보완을 목적으로 함 | Author explanation only | Current frame only vs episode memory라는 설계 논리 | Object displacement에서 friction-force 정보를 유추하도록 설계; 실제 parameter 추정 정확도는 측정하지 않음 | §IV-B; PDF p.3; Not applicable; Not applicable |
| Recurrent history와 dynamics sampling은 pushing 성능에 영향을 줌 | Input ablation; Controlled comparison | VPM(no history), Stacked 5, uGRU, eGRU; 평가 100 episodes | All shapes 성공률 eGRU 81% / uGRU 73% / Stacked 76% / VPM 67%. eGRU는 sampling도 다르므로 81% vs 67%을 순수 memory 효과로 읽지 않음. Square cuboid는 91/92/89/93%로 모든 조건 개선 아님 | §IX-A; PDF p.5; Not applicable; Fig.5 |
| 실물 eGRU가 비교군보다 높은 성공률을 보임 | Controlled comparison; Failure analysis | 4개 polystyrene objects × 2 episodes = 8/agent | eGRU 87.5%, uGRU 50%, Stacked 25%, VPM 37.5%. 실물 성공은 육안판정; Stacked가 이미 도달한 물체를 불필요하게 다시 밀어 실패 | §IX-B; PDF p.6; Table II; Figs.6–7 |

## 13. Author-stated Limitations

저자는 평가 shape가 단순한 cylinder/cuboid에 제한되고 rectangular-base cuboid가 어렵다고 설명한다. Occlusion을 피하기 위한 glass table 아래 camera의 완전 가시성 가정은 비현실적이며, position-offset action은 smooth motion을 보장하지 않고 안전 보장도 없다. [§X, PDF p.6] 실물은 위치 GT가 없어 reward 계산 및 정량 성공 판정 대신 육안을 사용한다. [§IX-B, PDF p.6]

## 14. Author-stated Future Work

Imitation learning으로 복잡한 shape와 어려운 pushing 사례를 학습하는 방향, occlusion을 포함한 partial observation, $C^2$-continuous control policy, 사람 근처에서의 safety-constrained manipulation을 제안한다. [§X, PDF p.6]

## 15. Review-relevant Findings

- Binary observation은 tactile이 아니라 RGB-derived silhouette다.
- Current vision을 계속 갱신하면서 mass/friction의 미관측성을 GRU history로 보완한다.
- Actor/critic에는 object pose GT가 없지만 reward와 HER에는 GT object/goal position이 필요하다.
- Goal mask는 초기 생성·고정이며 current object mask와 구분된다.
- 실물 결과는 8 episodes/agent와 육안 성공판정으로 제한된다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §IV-A–B, Fig.2, PDF pp.2–3 |
| Object pose / shape | §IV-A/D; §VII, PDF pp.2–4 |
| Tactile / F/T | 사용하지 않음; §IV-A–B, PDF pp.2–3 |
| Reward | §IV-D, Eq.(2), PDF p.3 |
| Critic / HER | §IV-B/V, PDF pp.3–4 |
| Ablation | §IX, Figs.5/7, PDF pp.5–6 |
| Limitation / Future Work | §IX-B/X, PDF p.6 |
