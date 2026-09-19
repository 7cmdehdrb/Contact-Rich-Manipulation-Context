# Perceiving Extrinsic Contacts from Touch Improves Learning Insertion Policies

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B027
- Authors: Carolina Higuera; Joseph Ortiz; Haozhi Qi; Luis Pineda; Byron Boots; Mustafa Mukadam
- Year: 2023
- Venue: Not stated (arXiv preprint)
- DOI / arXiv: 미명시 / 2309.16652v1
- PDF version: arXiv v1;28September2023
- Page count: 7
- SHA-256: `86e13b38ca1a51b689e4193ce0b973c33585487dc9bb0ba79ab87427dee22467`
- PDF filename: `Higuera 등 - 2023 - Perceiving Extrinsic Contacts from Touch Improves Learning Insertion Policies.pdf`
- 분석 근거: 선택 PDF 원문을 새로 읽었다. 기존 논문 상세 노트를 근거로 사용하지 않았다. 본문 pp.1–6을 읽고 Fig.5–8의 policy learning/evaluation 그래프를 렌더 확인했다. p.7은 참고문헌; 관련 appendix 없음.

## 2. Relevance to This Review

**Relevant**. 손가락–물체 tactile image를 외부 물체–환경 contact patch로 바꾸고 PPO policy에 제공한다. Proprio-only, tactile embedding, estimated patch, GT patch를 비교하므로 축약 표현의 역할과 geometry/grasp prior, training-only GT를 분석하는 데 직접 유용하다.

## 3. Task

Franka Panda gripper가 이미 잡은 mug를 handle이 cupholder slot에 맞게 삽입하고, bowl을 dishrack의 왼쪽 두 번째 slot에 넣는다. Mug/holder tolerance는1cm. Simulation training episode250steps, 실물 평가 trial최대100steps. 성공률과 완료 timestep 수를 비교한다. (§V, pp.4–6)

## 4. Method

### 4.1. Overall Pipeline

두 DIGIT image → background subtraction → VAE embeddings5frame → MLP temporal feature + EEF pose history + NDF object-shape/query-point features → NCF-v2 Transformer의 extrinsic contact probabilities → thresholded object-surface contact patch → MLP/max-pool + EEF history → PPO → relative6D EEF pose → joint-space IK. (§III/V, pp.2–4)

### 4.2. Observation

주 정책 πNCF-v2는 EEF pose(t,t−1,t−2), estimated contact patch embedding을 받는다. Estimator에는 tactile history, EEF history, object shape representation/query points가 별도로 필요하다. Direct-tactile baseline은 EEF history에 tactile-sequence embedding을 더한다. Oracle만 GT contact patch를 입력받는다. (§III/§V-A, pp.2–4)

### 4.3. Action

현재 EEF pose에 대한6DOF relative transform; rotation은 axis-angle. (§V-A, p.4)

### 4.4. Controller

Joint-space IK controller에 target transform을 전달한다. Franka Panda parallel gripper 양 finger의 DIGIT 사용. Controller frequency/gains는 원문 미명시이다. (§V-A, p.4)

### 4.5. Learning / Optimization Method

PPO로 각 policy와 downsampling MLP를 공동 최적화한다. NCF는 IsaacGym/TACTO simulated contacts로 미리 학습한다. Mugs/bottles/bowls 각5shape dataset, held-out shape 평가; pretrained NDF와 별도 trained tactile VAE를 사용한다. NCF-v2는 이전 predicted contact pt−1 recursion을 제거하고 입력의 temporal cues만 쓴다. (§III-B–V, pp.2–4)

## 5. Object Information

실행 입력과 학습·평가용 정답을 구분한다.

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | EEF history와 fixed grasp-relative pose assumption으로 object pose를 간접 추론 | EEF는 계속 갱신; 독립 object tracking 없음 | Actor의 explicit current object position vector 없음 |
| Orientation | 기타 | 동일 fixed relative grasp pose 및 EEF orientation | EEF update; grasp transform 고정 가정 | Simulation bowl grasp 변동은 실패 원인 |
| Shape / Geometry | Initial | Known object class의 reference point cloud/NDF shape feature, object-surface query points | reference shape 고정; contact probability 갱신 | Novel instance 일반화와 shape prior 없는 조건은 다름 |
| Physical Parameters | 미제공 | Runtime mass/friction 정답 입력 미명시 | 해당 없음 | Training simulation contact supervision은 별도 |

## 6. Missing Object Information and Compensation

Object–environment contact를 직접 볼 수 없음 → intrinsic DIGIT tactile history + EEF motion/pose history + object shape/reference cloud + fixed grasp relation → extrinsic contact patch를 추정해 policy에 공간 정보를 준다.

EEF pose만으로 실제 bowl grasp pose의 변동을 알 수 없음 → NCF도 EEF를 통해 object pose를 추론하므로 이 문제를 완전히 해결하지 못한다. GT contact oracle은 patch를 통해 object pose 정보를 암묵적으로 더 받을 수 있다고 저자가 설명한다. (§V-C, p.6)

## 7. Tactile

### 7.1. Raw Sensor

두 gripper finger의 DIGIT optical tactile RGB; robot–object intrinsic contact deformation image. TACTO로 simulation한다. (§III-B/V-A, pp.3–4)

### 7.2. Preprocessing

각 image에서 background subtraction;24real sensor background로 randomization; VAE encoding. 최근5embedding을 concatenate 후 MLP,30fps에서약0.17s history. NCF-v1의 autoencoder/LSTM과 recurrent contact output을 변경했다. (§III-B, pp.2–3)

### 7.3. Policy Representation

Actor에는 raw image 대신 thresholded extrinsic contact point cloud의 MLP/max-pool embedding을 제공한다. Estimator의 probabilities를 threshold해서 object surface의 contact patch를 선택한다. Threshold 수치는 미명시이다. (§V-A, p.4)

### 7.4. Retained Information

Object 위 어느 표면점이 환경과 접촉하는지, multiple patch와 contact/no-contact transition의 공간 정보를 유지한다. Fingers에 닿는 intrinsic contact와 별개인 extrinsic patch이다.

### 7.5. Removed / Unavailable Information

Thresholded patch에는 probability confidence 값 자체가 직접 전달되지 않는다(표현 구조상 확인). Raw tactile RGB/deformation 및 force magnitude/shear를 독립 policy channel로 보존하지 않는다. 모든 물리 정보의 소실 여부를 추정하지 않는다. Region-wise binary fingertip tactile 비교는 하지 않았다.

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음.

### 8.2. Representation

해당 없음.

### 8.3. Role

해당 없음.

### 8.4. Required Assumptions

해당 없음.

### 8.5. Reported Limitation / Ambiguity

원문은 F/T-only ambiguity를 직접 평가하지 않음.

## 9. Other Observations

EEF3pose history21D가 모든 정책에 공통이다. Tactile5frame history는 estimator/direct-tactile baseline에 쓰인다. External RGB vision input은 없다. NCF-v2는 recurrent predicted-contact feedback을 제거하고 window history를 사용한다. Previous action input은 미명시이다. Goal은 과업별 고정 insertion target이며 actor에 별도 goal pose가 입력된다는 근거는 없다.

## 10. Tactile–Other Modality Relationship

Tactile은 손가락 접촉 변화, proprioception은 EEF motion, reference shape는 object-surface 공간 좌표계를 제공해 extrinsic contacts를 추정한다. Sensor를 단순 병용한 것에 그치지 않고 direct tactile embedding보다 task-specific patch representation이 유용한지 비교했다. F/T 병용/비교는 없다.

## 11. Training-only / Privileged Information

Actor·Critic·reward·termination·학습 데이터 생성을 따로 기록한다.

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | 주방법 No; oracle Yes | Main: estimated patch+EEF; oracle: GT extrinsic contact cloud | GT-contact variant를 deployment actor로 혼동하지 않음 (§V-A, p.4) |
| Critic | 미명시 | PPO는 명시하지만 critic observation/GT 비대칭 입력은 미명시 | 일반 PPO 구조로 추론하지 않음 (§V-A, p.4) |
| Reward | Yes | Mug/holder keypoint alignment와 mug orientation; bowl current position과 target distance | Simulator object pose/geometry를 reward에 사용; actor에 제공된다는 뜻 아님 (§V-A, p.4) |
| Termination | 미명시 | 250-step training;100-step real cap; insertion success metric | 성공 GT 기준의 세부 threshold/termination 구현은 미명시 (§V, pp.4–6) |
| Curriculum | Yes: data/estimator supervision | Simulation contacts의 NCF supervision; object shape dataset/NDF; randomized EEF initialization | Training-time contact labels와 runtime predicted patch를 분리 (§III-B/V-A, pp.3–4) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Contact representation이 policy에 유용 | Representation ablation; Controlled comparison | Proprio / tactile embedding / estimated NCF patch / GT patch | Real mug15trials: estimated patch60%, proprio/tactile 각각약27%; +33percentage points. 평균23steps 감소,1.36× 빠름. | §V-B; PDF p.5 ; Fig.5–6 |
| Bowl insertion 일반화 | Representation ablation; Controlled comparison | 동일4policy simulation100trials;3deployment variants real15trials | NCF-v2는 proprio보다 real success약13percentage points 높고1.27× 빠름. 실물 초기 grasp pose 통제와 simulation의 uncontrolled bowl pose를 구별. | §V-C; PDF pp.5–6 ; Fig.7–8 |
| NCF sim-to-real 개선 | Controlled comparison | NCF-v1 / v2MLP / v2Transformer | Simulation contact MSE0.048/0.042/0.039 over100test trajectories; real data는 Fig.3의 contact tracking 정성 비교. VAE/recurrence 변경 각각의 독립 ablation은 아님. | §IV; PDF pp.3–4 ; Fig.3 |
| Object-pose/grasp prior 한계 | Failure analysis; Author explanation only | Simulation bowl의 초기 pose 변동 vs real controlled grasp | GT patch oracle은 pose를 암묵 제공하지만 EEF-dependent NCF/other policies는 변동을 추론하기 어려움. | §V-C; PDF p.6 |

## 13. Author-stated Limitations

세 object class에 제한되고 grasp 중 object–gripper relative pose가 고정된다고 가정한다. 올바른 reference point cloud를 얻으려면 object class를 미리 알아야 한다. Simulation bowl의 uncontrolled grasp pose에서는 EEF만으로 실제 object pose를 알 수 없어 performance가 낮아진다. (§V-C/VI, p.6)

## 14. Author-stated Future Work

Vision으로 다양한 object shape의 implicit representation을 학습하는 시스템과 NCF를 통합해 class/reference-shape 제한을 줄이는 방향을 제시한다. (§VI, p.6)

## 15. Review-relevant Findings

- Main actor는 GT contacts가 아닌 estimated extrinsic patch를 받는다.
- Shape reference와 fixed grasp-relative pose prior가 estimator를 성립시킨다.
- Tactile5frame, EEF3pose history를 쓴다.
- Thresholded contact patch는 object surface의 공간 정보이며 binary fingertip region sensing과 다르다.
- Reward는 current object pose/keypoints를 사용하고 critic GT는 미명시이다.
- Direct tactile embedding 대비 patch representation의 실험 비교가 있다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / Object pose | §III pp.2–3; §V-A p.4; §V-C p.6 |
| Tactile / Shape | §III-B pp.2–3; §VI p.6 |
| F/T | 사용하지 않음; §V-A p.4 |
| Reward / Critic | §V-A p.4; critic 입력 미명시 |
| Ablation | Fig.5–8 p.5; §V-B–C pp.5–6 |
| Limitation / Future | §VI p.6 |
