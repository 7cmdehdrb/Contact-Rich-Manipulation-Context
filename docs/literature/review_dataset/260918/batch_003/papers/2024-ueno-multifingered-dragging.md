# Multi-Fingered Dragging of Unknown Objects and Orientations Using Distributed Tactile Information Through Vision-Transformer and LSTM

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B080`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: T. Ueno; S. Funabashi; H. Ito; A. Schmitz; S. Kulkarni; T. Ogata; S. Sugano
- Year: 2024
- Venue: 2024 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 7445-7452
- DOI / arXiv: 10.1109/IROS58592.2024.10802283 / Not stated
- PDF version: IEEE publisher version
- Page count: 8
- SHA-256: `801aaae0779dfe6aab0b16d7d6dde5d953e001d0c75e6cc5546b001670f10590`
- PDF filename: Ueno 등 - 2024 - Multi-Fingered Dragging of Unknown Objects and Orientations Using Distributed Tactile Information Th.pdf
- 확인 범위: 전체 본문 PDF pp.1-8; architecture, inputs/outputs, data collection, ablations, feature analysis, limitations/future work 확인

## 2. Relevance to This Review

`Relevant`

current object pose·property label을 입력하지 않고 distributed 3-axis tactile, joint state, LSTM history로 unknown object의 orientation과 softness에 맞춰 dragging/grasping한다. ViT-only, LSTM-only, open-loop 비교가 있어 spatial tactile와 temporal memory가 누락된 object information을 보완하는 효과를 직접 평가한다.

## 3. Task

Allegro Hand 앞에 놓인 물체를 먼저 touch해 orientation/property를 파악하고, 적절한 finger로 회전·drag한 뒤 palm 안에서 grasp한다. long object 성공은 최종 orientation이 palm horizontal 대비 ±15°이고 table 제거 후 떨어지지 않는 조건이다.

## 4. Method

### 4.1. Overall Pipeline

19개 uSkin patch의 3-axis taxels → patch crop/normalization/tokenization → ViT spatial attention/CLS feature → 16 joint angles와 결합 → LSTM temporal state → 다음 tactile·follower joint·leader target joint 예측 → leader joint target을 PID 위치 제어로 실행. 예측과 실측을 0.5 closed-loop ratio로 재입력한다. [Secs. III-C-E, PDF pp.3-5]

### 4.2. Observation

실행 입력은 912-dim tactile (19 patches×16 chips×3 axes)와 16 Allegro joint angles이다. ViT-LSTM의 이전 prediction과 현재 raw data를 weighted-average하여 재귀 입력하므로 time history가 hidden state에 남는다. current object pose, object label, softness label은 없다. [Secs. III-A,D; IV-B, PDF pp.3-5]

### 4.3. Action

LSTM이 예측한 16-dim leader joint angles가 target command이다. 각 object state에 맞춰 finger hooking, rotation, dragging, final grasp sequence를 생성한다. [Sec. III-D and IV-A, PDF pp.4-5]

### 4.4. Controller

CyberGlove demonstration에서 remap한 leader joint angle 형식을 실행하고, Allegro Hand PID가 target joint position에 필요한 torque를 계산한다. [Secs. III-B,D, PDF pp.3-4]

### 4.5. Learning / Optimization Method

human teleoperation 240 trials의 one-step-ahead supervised deep predictive/imitative learning이다. joint, desired joint, tactile MSE를 합산하며 AdamW로 학습한다. RL은 아니다. [Sec. III-D-E and IV, PDF pp.4-5]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | object position vector 없음 | No | 초기 left-right offset 범위는 제한된다. [Secs. I and VI, PDF pp.1,8] |
| Orientation | 미제공 | object orientation vector/label 없음 | No | PCA는 사후 internal-feature 분석이며 actor 입력이 아니다. [Secs. I, V-B,D, PDF pp.1,6-7] |
| Shape / Geometry | 미제공 | object identity/shape label 없음 | No | unknown shape experiments에서 평가한다. [Secs. V-E-F, PDF pp.7-8] |
| Physical Parameters | 미제공 | softness/friction label 없음 | No | softness에 따라 attention/drag force pattern이 달라진다. [Secs. V-C-D, PDF p.6] |

## 6. Missing Object Information and Compensation

Current object position·orientation·shape·softness label 미제공
→ distributed 3-axis tactile + joint angles + LSTM history
→ initial active touch에서 어느 finger가 어디에 닿았는지와 deformability를 implicit feature로 유지해 motion sequence를 고른다. [Secs. I, III-D, V, PDF pp.1,4,6-7]

정확한 초기 좌우 위치 미제공
→ spatial attention으로 일정 범위의 contact location 변화에 대응
→ 다만 저자는 넓은 left-right misalignment는 robot hand kinematics 때문에 아직 포함하지 못했다고 한다. [Sec. VI, PDF p.8]

## 7. Tactile

### 7.1. Raw Sensor

Allegro fingertips, phalanges, palm의 XELA uSkin 19 patches. 각 patch 16 magnetic taxels가 x/y/z force-related component를 내며 총 912 channels를 20 Hz로 기록한다. [Sec. III-A, PDF p.3]

### 7.2. Preprocessing

각 patch를 4×4×3 token으로 crop하고 taxel/joint를 0.1-0.9 normalize한다. sensor variation 때문에 patch별 linear transform weight를 공유하지 않는다. [Secs. III-C and IV-B, PDF pp.3,5]

### 7.3. Policy Representation

19 tactile tokens×48 dims를 3-layer single-head ViT가 20-dim CLS feature로 축약하고 16 joint dims와 결합해 500-dim LSTM hidden state에 입력한다. [Sec. IV-B; Table I, PDF p.5]

### 7.4. Retained Information

finger/patch별 contact 위치, 3-axis load pattern, 시간에 따른 contact progression, object orientation/softness와 연관된 implicit feature를 남긴다. [Secs. V-B-D, PDF pp.6-7]

### 7.5. Removed / Unavailable Information

CLS 20-dim 축약 뒤 raw 912-channel 세부값은 policy output 단계에 직접 노출되지 않는다. object pose·shape·softness의 명시적 수치는 제공하지 않으며 one patch는 고장으로 제외했다. [Secs. III-A,C and IV-B, PDF pp.3,5]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8; uSkin의 local 3-axis tactile channels를 쓰며 wrist F/T/wrench는 사용하지 않음]

### 8.2. Representation

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8; uSkin의 local 3-axis tactile channels를 쓰며 wrist F/T/wrench는 사용하지 않음]

### 8.3. Role

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8; uSkin의 local 3-axis tactile channels를 쓰며 wrist F/T/wrench는 사용하지 않음]

### 8.4. Required Assumptions

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8; uSkin의 local 3-axis tactile channels를 쓰며 wrist F/T/wrench는 사용하지 않음]

### 8.5. Reported Limitation / Ambiguity

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8; uSkin의 local 3-axis tactile channels를 쓰며 wrist F/T/wrench는 사용하지 않음]

## 9. Other Observations

- Proprioception: Allegro Hand 16 joint angles.
- History: LSTM hidden state와 이전 predicted tactile/joint를 current raw data와 0.5 비율로 재귀 결합한다.
- Previous action: leader target joint가 다음 observation과 함께 sequence에 간접 반영되지만 별도 previous-action vector는 없다.
- Vision: 실행 actor는 사용하지 않는다. human demonstrator는 data collection 중 visual feedback을 사용했다.
- State estimator: 명시적 pose estimator는 없고 LSTM latent가 orientation/property를 implicit하게 encode한다.

## 10. Tactile–Other Modality Relationship

Tactile spatial attention은 어떤 finger/contact region이 중요한지 나타내고, joint state는 hand configuration을 제공하며, LSTM history는 initial touch에서 얻은 orientation/softness cue를 긴 manipulation 동안 유지한다. ViT-only 0%, LSTM-only 30%, ViT-LSTM 95% 비교는 spatial tactile와 temporal memory가 함께 필요함을 보여준다. F/T는 사용하지 않는다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | 비-RL supervised imitation/deep predictive learning. Human visual feedback와 CyberGlove leader joints는 demonstration 수집/labels에만 사용되며 autonomous 실행 입력이 아니다. [Secs. III-D-E and IV, PDF pp.4-5] |
| Critic | Not applicable | 비-RL | 비-RL supervised imitation/deep predictive learning. Human visual feedback와 CyberGlove leader joints는 demonstration 수집/labels에만 사용되며 autonomous 실행 입력이 아니다. [Secs. III-D-E and IV, PDF pp.4-5] |
| Reward | Not applicable | 비-RL | 비-RL supervised imitation/deep predictive learning. Human visual feedback와 CyberGlove leader joints는 demonstration 수집/labels에만 사용되며 autonomous 실행 입력이 아니다. [Secs. III-D-E and IV, PDF pp.4-5] |
| Termination | Not applicable | 비-RL | 비-RL supervised imitation/deep predictive learning. Human visual feedback와 CyberGlove leader joints는 demonstration 수집/labels에만 사용되며 autonomous 실행 입력이 아니다. [Secs. III-D-E and IV, PDF pp.4-5] |
| Curriculum | Not applicable | 비-RL | 비-RL supervised imitation/deep predictive learning. Human visual feedback와 CyberGlove leader joints는 demonstration 수집/labels에만 사용되며 autonomous 실행 입력이 아니다. [Secs. III-D-E and IV, PDF pp.4-5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| spatial tactile attention과 temporal memory가 모두 필요하다. | Representation ablation | ViT-LSTM vs LSTM-only vs ViT-only | trained objects success 95% vs 30% vs 0%. | Sec. V-A; PDF PDF pp.5,7 ; Table II |
| closed-loop tactile policy가 object property 변화에 적응한다. | Controlled comparison | ViT-LSTM vs nearest training open-loop trajectory | untrained known-shape objects success 78% vs 53%. | Sec. V-E; PDF PDF p.7 ; Table IV |
| latent history가 unseen orientation을 encode한다. | Controlled comparison; Feature analysis | trained 45/90/135° vs untrained 68/113° | untrained 포함 box orientation success 96%; LSTM PCA clusters interpolate orientations. | Sec. V-B; PDF PDF pp.6-7 ; Table III ; Fig. 5 |

## 13. Author-stated Limitations

한 uSkin patch가 고장으로 제외되었고, training/evaluation 초기 위치 범위가 제한적이다. Allegro Hand가 모든 finger에 adduction/abduction이 없어 큰 left-right misalignment를 포함하지 못했다. tactile attention의 middle-finger high score 원인도 미해명이다. [Secs. III-A, V-C, VI, PDF pp.3,6,8]

## 14. Author-stated Future Work

초기 orientation과 position 범위를 넓히고, demonstration에 haptic feedback device를 사용해 data quality를 높이며, image/sound 등 다른 modality와 tactile을 통합할 것을 제안한다. [Sec. VI, PDF p.8]

## 15. Review-relevant Findings

- 실행 시 current object pose, shape, softness label을 제공하지 않는다.
- 912-channel distributed 3-axis tactile과 16 joint angles를 사용한다.
- ViT는 spatial tactile을 20-dim CLS로 축약하고 LSTM은 contact history를 유지한다.
- ViT-LSTM 95%, LSTM-only 30%, ViT-only 0%의 representation ablation이 있다.
- human visual feedback와 leader joints는 training demonstrations에만 사용된다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | Secs. III-D and IV-B, PDF pp.4-5 |
| Object pose | Introduction and Sec. V-B/D, PDF pp.1,6-7 |
| Tactile | Sec. III-A/C, PDF p.3 |
| F/T | 사용하지 않음; 전체 PDF |
| Reward | 해당 없음; supervised MSE Eq. (4)-(5), PDF p.4 |
| Critic | 해당 없음 |
| Ablation | Tables II-IV, PDF p.7 |
| Limitation | Sec. VI, PDF p.8 |
