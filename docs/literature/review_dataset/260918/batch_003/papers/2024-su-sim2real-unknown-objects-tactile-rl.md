# Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B078`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Entong Su; Chengzhe Jia; Yuzhe Qin; Wenxuan Zhou; Annabella Macaluso; Binghao Huang; Xiaolong Wang
- Year: 2024
- Venue: 2024 IEEE International Conference on Robotics and Automation (ICRA), 9234-9241
- DOI / arXiv: 10.1109/ICRA57147.2024.10611113 / 2403.12170
- PDF version: IEEE publisher version
- Page count: 8
- SHA-256: `f6810b19801ee51016999b40337b7d5be497adacb3c075a7a9eedefbd2dd1070`
- PDF filename: Su 등 - 2024 - Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning.pdf
- 확인 범위: 전체 publisher PDF pp.1-8; observation, reward, actor/critic, representation 및 sensor ablation, failure cases, conclusion/future work 확인

## 2. Relevance to This Review

`Relevant`

두 DIGIT의 RGB, difference, binary tactile representation을 같은 pivoting 정책에서 직접 비교하며, tactile 제거·object-angle oracle·point-cloud vision까지 통제 비교한다. 실행 actor는 current object pose를 받지 않고 tactile, joint proprioception, target angle로 동작하므로 reduced tactile이 어떤 정보를 남기며 object state 부족을 어떻게 보완하는지에 직접 답한다.

## 3. Task

그리퍼로 물체를 잡은 상태에서 지지면을 이용해 물체를 목표 상대 각도로 pivoting한다. 성공은 최종 angle deviation이 15% 미만인 경우이며, 외부 센서로 current object pose를 추정하지 않는다.

## 4. Method

### 4.1. Overall Pipeline

두 DIGIT tactile image → RGB/Diff/Binary 전처리와 shared image encoder → joint proprioception MLP 및 target angle과 결합 → PPO actor → EEF x-z translation/y rotation → robot controller. simulation에서 여러 object category로 학습한 뒤 real robot에 zero-shot transfer한다. [Figs. 1-2; Sec. III-IV, PDF pp.1-4]

### 4.2. Observation

64×64 tactile image 두 장, robot joint proprioceptive state, target relative angle을 actor/critic에 제공한다. 세 tactile 표현을 대체 입력으로 비교한다. current object position/orientation/shape의 수치 상태는 실행 actor에 제공하지 않는다. [Sec. IV, PDF p.3]

### 4.3. Action

EEF translation을 x-z plane으로 제한하고 rotation은 y axis로 제한한 연속 action이다. gripper width는 고정 grasp command이므로 action에 포함되지 않는다. [Sec. IV, PDF p.3]

### 4.4. Controller

policy action을 로봇 EEF motion으로 실행하며 gripper는 물체를 secure grasp하도록 고정한다. 구체적인 low-level controller 종류와 gain은 원문에서 확인되지 않는다. [Sec. IV, PDF p.3]

### 4.5. Learning / Optimization Method

Stable-Baselines3 기본 hyperparameter의 PPO를 사용한다. 두 tactile image는 shared encoder, proprioception은 MLP로 encode하며 actor와 critic이 같은 feature를 사용한다. 22개 simulation objects와 domain randomization으로 학습하고 real data/fine-tuning 없이 이전한다. [Sec. IV, PDF p.3]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | current object position 수치 입력 없음 | No | reward 계산에는 simulation object position이 쓰이지만 actor 입력과 구분한다. [Sec. IV, PDF p.3] |
| Orientation | 미제공 | current object angle 수치 입력 없음; target angle만 제공 | No | Oracle Angle은 비교용 privileged baseline일 뿐 제안 actor가 아니다. [Sec. IV-V.A, PDF pp.3-5] |
| Shape / Geometry | 미제공 | mesh/category/point cloud를 actor에 제공하지 않음 | No | Point Cloud는 별도 baseline이다. [Sec. IV-V, PDF pp.3-6] |
| Physical Parameters | 미제공 | friction, stiffness, mass 입력 없음 | No | support height/object size/initial pose를 학습 때 randomize한다. [Sec. IV, PDF p.3] |

## 6. Missing Object Information and Compensation

Current object position·orientation·shape·물성 미제공
→ 두 fingertip의 tactile representation + joint proprioception + target angle
→ grasp 내 contact pattern과 robot motion 관계를 이용해 목표 회전을 직접 결정한다. 저자는 explicit object pose estimation의 partial-observation error를 피하기 위해 end-to-end 정책을 택했다. [Sec. I, IV, PDF pp.1,3]

세밀한 intensity/색 정보(Binary에서 제거)
→ spatial binary contact mask + diverse-object training
→ sim-real에서 공통인 contact pattern에 집중하고 domain gap을 낮춘다. [Sec. III-B and V-B, PDF pp.3,6]

## 7. Tactile

### 7.1. Raw Sensor

gripper 양 fingertip에 장착된 두 DIGIT vision-based tactile sensors의 RGB image. [Fig. 2; Sec. III, PDF pp.2-3]

### 7.2. Preprocessing

RGB 그대로, force-free canonical image와 현재 image의 pixel difference를 grayscale 평균한 Diff, Diff에 sensor별 grid-searched threshold φ를 적용한 Binary를 비교한다. right image는 horizontal flip하고 Diff/Binary는 0-1 random scaling; 일부 조건은 scale/erase 및 RGB brightness/contrast/hue augmentation을 추가한다. [Sec. III-B and Baselines, PDF pp.3-4]

### 7.3. Policy Representation

각 sensor의 64×64 RGB, grayscale Diff, 또는 binary contact mask를 shared encoder로 encode한다. [Sec. III-B/IV, PDF p.3]

### 7.4. Retained Information

Binary는 contact presence의 pixel-level spatial pattern, 접촉 영역의 위치·모양·분포를 남긴다. Diff는 RGB absolute appearance를 제거하면서 deformation difference magnitude를 남긴다. [Sec. III-B, PDF p.3]

### 7.5. Removed / Unavailable Information

Binary threshold는 color와 continuous pixel intensity/deformation magnitude를 제거하며 threshold 때문에 일부 contact를 놓칠 수 있다. 저자가 noise-contact information trade-off를 명시한다. shear/force vector를 별도 수치로 제공하지 않는다. [Sec. III-B, PDF p.3; Fig. 5, PDF p.6]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8; DIGIT image를 사용하며 별도 F/T/wrench input은 없음]

### 8.2. Representation

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8; DIGIT image를 사용하며 별도 F/T/wrench input은 없음]

### 8.3. Role

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8; DIGIT image를 사용하며 별도 F/T/wrench input은 없음]

### 8.4. Required Assumptions

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8; DIGIT image를 사용하며 별도 F/T/wrench input은 없음]

### 8.5. Reported Limitation / Ambiguity

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8; DIGIT image를 사용하며 별도 F/T/wrench input은 없음]

## 9. Other Observations

- Proprioception: robot joint states를 MLP feature로 제공한다.
- Goal: target relative angle을 task information으로 제공한다. current object angle과 구분한다.
- Vision: external point cloud는 별도 baseline이며 제안 actor에서는 사용하지 않는다.
- History / Previous action / recurrent state: 원문에서 actor 입력으로 확인되지 않는다.
- State estimator: 제안 정책에는 명시적 estimator가 없다. Angle Estimator/PCA는 비교 baseline이다.

## 10. Tactile–Other Modality Relationship

Tactile은 current contact의 spatial pattern을 제공하고 proprioception은 손의 motion/configuration을 제공하며 target angle은 목적을 지정한다. Binary tactile은 magnitude와 appearance를 제거하지만 위치·형상 pattern을 남긴다. 저자는 w/o Tactile, point cloud, angle-estimator, oracle-angle와 통제 비교하여 단순 병용 이상의 필요성을 제시했다. F/T는 사용하지 않는다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | tactile images + joint proprioception + target angle | current object GT pose/shape는 실행 actor에 없음. [Sec. IV, PDF p.3] |
| Critic | No | actor와 같은 tactile/proprioception feature | actor와 critic이 같은 feature를 사용한다고 명시한다. [Policy Training, PDF p.3] |
| Reward | Yes | simulation contact count, current/initial/target object position and angle | real 실행에는 reward가 필요하지 않는다. [Reward Function, PDF p.3] |
| Termination | Not stated | episode termination 조건은 원문에서 확인되지 않음 | 15% angle deviation은 evaluation success metric이며 termination과 동일하다고 추론하지 않는다. [Evaluation Metric, PDF p.4] |
| Curriculum | No | 다양한 objects와 domain randomization | GT를 이용한 curriculum은 명시하지 않는다. [Domain Randomization, PDF p.3] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| tactile은 pivoting에 필요하다. | Sensor ablation | Tactile-Binary(Aug) vs w/o Tactile | real success 0.80 vs 0.33; DAgger non-tactile student 0.50. | Sec. V-A; PDF PDF pp.4-5 ; Table I ; Fig. 4 |
| Binary representation이 sim-to-real에 유리하다. | Representation ablation | RGB vs Diff vs Binary, augmentation 유무 | 비증강 real success RGB 0.50, Diff 0.60, Binary 0.80; Binary는 simulation 성능이 비슷해도 real 성능이 높다. | Sec. V-B; PDF PDF pp.5-6 ; Table I ; Fig. 5 |
| 다양한 object training이 unseen object generalization을 높인다. | Controlled comparison | single-category vs multi-category training | multi-category Binary real success 0.80; single-category policy는 0.54. | Sec. V-C; PDF PDF pp.5-6 ; Table II |

## 13. Author-stated Limitations

Binary threshold는 noise를 줄이지만 contact information 일부를 놓칠 수 있다. real failure는 unstable gripping으로 incomplete pattern이 생기거나 unusual/incomplete contact로 feedback가 약해지는 경우다. [Sec. III-B, V-C, PDF pp.3,6]

## 14. Author-stated Future Work

Conclusion은 tactile feedback를 manipulation strategy refinement에 더 통합하는 방향을 제시한다. 별도의 구체적 algorithmic future work는 원문에서 확인되지 않는다. [Sec. VI, PDF p.6]

## 15. Review-relevant Findings

- 실행 actor는 current object pose/shape를 받지 않고 두 tactile images, joint proprioception, target angle을 사용한다.
- Binary는 continuous intensity를 제거하지만 contact 영역의 spatial pattern을 남긴다.
- w/o tactile real success 0.33 대비 Binary tactile 0.80으로 sensor ablation이 있다.
- RGB, Diff, Binary를 같은 정책과 task에서 직접 비교한 representation ablation이 있다.
- actor와 critic은 같은 feature를 사용하며 asymmetric privileged critic이 아니다.
- reward는 simulation current object position/angle 등의 GT를 사용한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | Sec. IV, PDF p.3 |
| Object pose | Sec. IV, PDF p.3; Oracle baseline Sec. V-A, p.4 |
| Tactile | Sec. III-B, PDF p.3 |
| F/T | 사용하지 않음; 전체 PDF |
| Reward | Sec. IV, PDF p.3 |
| Critic | Policy Training, PDF p.3 |
| Ablation | Tables I-II, PDF p.5; Sec. V, pp.4-6 |
| Limitation | Sec. III-B and V-C, PDF pp.3,6 |
