# Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B076`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Max Yang; Yijiong Lin; Alex Church; John Lloyd; Dandan Zhang; David A. W. Barton; Nathan F. Lepora
- Year: 2023
- Venue: IEEE Robotics and Automation Letters, 8(9), 5480-5487
- DOI / arXiv: 10.1109/LRA.2023.3295236 / Not stated
- PDF version: Publisher version
- Page count: 8
- SHA-256: `65960baceadcd4dff611a934c57407099bd0917338a93f8bdbbf14b407228a47`
- PDF filename: Sim-to-Real_Model-Based_and_Model-Free_Deep_Reinforcement_Learning_for_Tactile_Pushing.pdf
- 확인 범위: 전체 본문 PDF pp.1-8; 방법, 보상, sim-to-real 관측 모델, 실험, Discussion/Future Work 및 참고문헌 확인

## 2. Relevance to This Review

`Relevant`

실행 중 외부 시각 없이 TacTip과 목표 정보만으로 미지 물체를 밀며, 원시 tactile image와 tactile-derived contact-surface pose를 직접 비교한다. current object center pose와 shape를 제공하지 않은 채 국소 접촉 자세와 목표 상대 관계로 폐루프 조작을 수행하므로, 축약 tactile 표현이 어떤 정보를 유지하고 무엇을 대신하는지에 직접 근거를 제공한다.

## 3. Task

초기 안정 접촉에서 시작하여 미지 물체를 작업공간 내 임의 목표 위치까지 평면 pushing한다. 접촉 위치가 목표의 25 mm 안에 들어오면 성공으로 판정하며, 접촉 유지와 안정적인 법선 방향 밀기를 함께 추구한다.

## 4. Method

### 4.1. Overall Pipeline

TacTip 영상 → (Real-to-Sim GAN 또는 PoseNet) tactile image/국소 접촉면 pose → goal-conditioned SAC 정책 또는 PETS 동역학 모델+CEM MPC → pusher의 횡이동·회전 증분 → Dobot 위치 제어. 모델 기반 방법은 매 step 재계획한다. [Sec. III-A-C, PDF pp.2-5; Fig. 2]

### 4.2. Observation

S1은 tactile image와 pusher-to-goal 상대 pose, S2는 pusher 대비 접촉면 pose와 접촉면 대비 goal pose, S3는 접촉면 상대/절대 pose이다. S1/S2는 model-free 정책, S3는 model-based 동역학 모델에 사용한다. object center pose, mesh, 질량, 마찰은 실행 actor 입력으로 명시되지 않는다. [Eq. (3), PDF p.3]

### 4.3. Action

정책이 pusher frame의 Δy∈[-1,1] mm와 Δθ∈[-1°,1°]를 출력한다. 전진 Δx는 매 step 1 mm로 고정한다. [Sec. III-B.2, PDF p.3]

### 4.4. Controller

Dobot MG400의 Cartesian position control로 pusher 증분을 실행한다. 모델 기반 경우 CEM-MPC가 action sequence를 최적화하고 첫 action만 적용한 뒤 재계획한다. [Sec. III-A.2, III-D, PDF pp.3,5]

### 4.5. Learning / Optimization Method

Model-free는 goal-conditioned Soft Actor-Critic, model-based는 probabilistic ensemble dynamics를 학습하는 PETS와 CEM 기반 MPC이다. 두 방법 모두 Tactile Gym/PyBullet에서 cube 하나로 학습하고 real 정책은 추가 RL 학습 없이 이전한다. [Sec. III-A,C, PDF pp.2-5]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | TacTip tactile image 또는 PoseNet이 추정한 pusher 대비 국소 contact-surface position; goal은 별도 제공 | Yes | 국소 접촉면 pose이지 current object center pose tracking은 아니다. [Eq. (3), PDF p.3] |
| Orientation | 기타 | TacTip에서 추정한 pusher 대비 국소 contact-surface angle | Yes | 전체 물체 orientation은 제공하지 않는다. [Eq. (3)-(4), PDF pp.3-4] |
| Shape / Geometry | 미제공 | 실행 정책에 mesh/CAD/category 입력 없음 | No | 학습은 cube 하나, 평가는 다양한 미지 물체이다. [Sec. III-B,C and IV, PDF pp.3-7] |
| Physical Parameters | 미제공 | 질량·마찰·무게중심 입력 없음 | No | 기본 simulator physics를 사용하며 domain randomization하지 않았다. [Sec. III-C.1, PDF p.4] |

## 6. Missing Object Information and Compensation

Current object center pose·전체 orientation·shape·physical parameters 미제공
→ tactile image 또는 tactile-derived contact-surface pose + pusher/goal 상대 관계
→ 국소 접촉 정렬과 접촉 위치의 목표 접근을 매 step 보정한다. 저자는 이를 object-centric 정보의 대체로 설계했다. [Sec. III-B, PDF p.3]

접촉 동역학과 물성 미제공
→ model-based online replanning 또는 model-free tactile feedback
→ 미지 물체와 disturbance에서 실행 궤적을 갱신한다. [Sec. IV-B-C, PDF pp.6-7]

## 7. Tactile

### 7.1. Raw Sensor

수평 장착된 331-pin TacTip의 optical tactile image. simulation에서는 접촉 depth rendering으로 영상을 만든다. [Sec. III-C-D, PDF pp.4-5]

### 7.2. Preprocessing

S1은 real image를 pix2pix Real-to-Sim GAN으로 simulated tactile image domain에 변환한다. S2/S3은 PoseNet CNN이 tactile image에서 접촉 depth와 angle을 추정하고 Cartesian contact pose로 변환한다. [Sec. III-C.2, PDF p.5]

### 7.3. Policy Representation

64차원 등의 축약 수치는 원문에 명시되지 않는다. 비교 표현은 (a) translated tactile image와 (b) 3-DoF 국소 contact-surface pose (x,y,θ)이다. [Eq. (3); Sec. III-B.1, PDF p.3]

### 7.4. Retained Information

image 표현은 접촉 변형 pattern을 보존한다. pose 표현은 pushing에 직접 필요한 국소 접촉 위치·깊이/각도·surface normal 관계를 보존한다. [Sec. I and III-B, PDF pp.2-3]

### 7.5. Removed / Unavailable Information

pose 변환은 상세 pin-level deformation과 contact pattern을 제거한다는 점이 표현 구조상 직접 확인된다. object center, 전체 geometry, 물성은 두 표현 모두 제공하지 않는다. 저자가 정보손실 항목을 별도 열거하지는 않았다. [Eq. (3); Sec. III-B, PDF p.3]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8]

### 8.2. Representation

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8]

### 8.3. Role

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8]

### 8.4. Required Assumptions

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8]

### 8.5. Reported Limitation / Ambiguity

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [전체 PDF pp.1-8]

## 9. Other Observations

- Proprioception: pusher pose/goal-relative pose가 observation에 포함된다.
- Vision: 실행 정책은 사용하지 않는다. 상단 ArUco tracking은 real 실험 궤적 검증용이며 actor 입력이 아니다. [Sec. III-D, PDF p.5]
- Goal: 매 episode 고정된 임의 goal이 정책/계획기에 제공된다.
- History / Previous Action / Recurrent State: actor 입력으로 명시되지 않는다.
- State estimator: real tactile pose 조건에서는 PoseNet이 접촉면 pose를 추정한다.

## 10. Tactile–Other Modality Relationship

Tactile은 국소 접촉면 상태를, robot/goal 상대 정보는 어디로 밀어야 하는지를 제공한다. 저자는 두 정보를 결합해 current object center와 shape 없이 pushing하도록 명시적으로 구성했다. F/T는 사용하지 않는다. image 대 pose 비교는 tactile 자체의 표현 ablation이며, pose가 더 적은 상세정보를 가지면서도 model-free 학습 효율과 real robustness가 더 좋았다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | real 실행에서는 tactile image/pose와 goal-relative 정보 | current object GT pose·shape·물성은 필요하지 않다. [Eq. (3); Sec. III-C.3, PDF pp.3,5] |
| Critic | Not stated | SAC critic의 별도 입력은 원문에서 확인되지 않음 | asymmetric critic 또는 GT 입력을 명시하지 않는다. [Sec. III-A.1, PDF pp.2-3] |
| Reward | Yes | simulation contact position/orientation, pusher orientation, goal distance | 학습 시 simulator state로 shaped reward를 계산하며 real 실행에는 reward가 필요하지 않다. [Eq. (4), PDF pp.3-4] |
| Termination | Yes | simulation contact-to-goal distance 25 mm | real에서는 tactile-derived contact 위치와 goal을 사용하지만 training termination의 simulator GT 사용은 구분한다. [Sec. III-B.4, PDF p.4] |
| Curriculum | No | cube 하나와 제한 goal space | domain randomization·다물체 curriculum 없이 학습한다. [Sec. III-C.1 and V, PDF pp.4,8] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| tactile pose가 tactile image보다 model-free 학습에 효율적이다. | Representation ablation | 동일 SAC에서 tactile image vs tactile pose | pose가 10% best reward에 2.8M samples, image는 23M; final reward도 pose가 더 높다. | Sec. IV-A; PDF PDF p.5 ; Table II ; Fig. 4 |
| pose 표현이 unseen contact와 disturbance에 더 robust하다. | Representation ablation; Failure analysis | real unseen objects/disturbances에서 tactile image vs pose | image 정책은 duck·-20° initial offset에서 contact를 잃었고 pose 기반 정책은 성공했다. | Sec. IV-C; PDF PDF pp.6-7 ; Fig. 7 |
| model-based와 model-free의 역할/표본효율 차이 | Controlled comparison | PETS+CEM vs SAC | model-based가 100× 적은 samples와 9/10 simulation objects 최고 성공률; 충분히 학습한 model-free는 real에서 더 짧은 경로. | Sec. IV-A-C; PDF PDF pp.5-7 ; Tables II-III ; Figs. 4,6-7 |

## 13. Author-stated Limitations

저자는 고정 Δx action constraint가 초기 위치에 가까운 goal의 도달 가능성과 contact surface 주변 탐색을 제한한다고 명시한다. 또한 시각 없이 real-world 학습을 수행하려면 자동 reset이 해결되지 않은 실무 문제라고 한다. [Sec. V, PDF pp.7-8]

## 14. Author-stated Future Work

action constraint를 제거해 reliability-performance trade-off를 조사하고, sample-efficient model-based RL로 real-world learning을 시도하는 방향을 제시한다. 자동 reset과 무시각 real 학습은 선결 과제로 남긴다. [Sec. V, PDF p.8]

## 15. Review-relevant Findings

- 실행 actor는 current object center pose, mesh, 물성을 받지 않는다.
- TacTip image를 직접 쓰는 표현과 국소 contact-surface pose (x,y,θ)로 축약한 표현을 비교한다.
- 축약 pose는 detailed deformation을 버리지만 pushing에 필요한 contact location/normal 관계를 남긴다.
- tactile pose + goal/proprioceptive relation이 누락된 object pose와 shape를 대신한다.
- ArUco vision은 평가 궤적 기록용이며 정책 입력이 아니다.
- reward와 training termination은 simulator contact/goal state를 사용한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | Eq. (3), PDF p.3 |
| Object pose | Sec. III-B.1, PDF p.3 |
| Tactile | Sec. III-B.1 and III-C.2, PDF pp.3,5 |
| F/T | 사용하지 않음; 전체 PDF |
| Reward | Eq. (4), PDF pp.3-4 |
| Critic | Sec. III-A.1, PDF pp.2-3; 입력 미명시 |
| Ablation | Table II, PDF p.5; Fig. 7, PDF p.7 |
| Limitation | Sec. V, PDF pp.7-8 |
