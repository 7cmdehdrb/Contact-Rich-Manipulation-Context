# Coarse-to-Fine Robotic Pushing Using Touch, Vision and Proprioception

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B016
- Authors: Bowen Deng; Yijiong Lin; Max Yang; Nathan F. Lepora
- Year: 2025
- Venue: IEEE Robotics and Automation Letters 10(2):1545–1552
- DOI / arXiv: 10.1109/LRA.2024.3511378 / 미명시
- PDF version: Publisher version; issue February 2025; online publication 2024-12-04
- Page count: 8
- SHA-256: `a1b55c26c1ec3b0e73fd3ae75e29a4b11fe4e5d42210a94ed35a84da696ab9ec`
- PDF filename: `Deng 등 - 2025 - Coarse-to-Fine Robotic Pushing Using Touch, Vision and Proprioception.pdf`
- 분석 근거: 선택 PDF 원문을 새로 읽었다. 기존 논문 상세 노트를 근거로 사용하지 않았다. 본문·Related Work·Method·실험·Discussion·References pp.1–8을 확인했다. Table III/IV가 있는 PDF p.6을 렌더링 검수했다. 외부에서 인용한 controller/GAN 논문은 이번 PDF의 상세 명세로 채워 넣지 않았다.

## 2. Relevance to This Review

**Relevant**. 물체 local contact pose를 3개 성분으로 축약한 tactile estimator와 proprioception을 결합해 pushing한다. 이 표현에서 없는 물체 전체 위치·방향 및 초기 접근 정보는 vision의 단계별 재위치 추정과 bounding rectangle로 보완한다. Multi-stage와 single-stage 비교가 있지만 tactile-only/vision-only 센서 제거 실험과는 다르다.

## 3. Task

알 수 없는 물체를 평면상 목표 position과 orientation으로 pushing한다. 초기 접근 후 goal-driven push, 목표 부근에서 방향을 맞추는 push, 재접촉 후 최종 병진 push를 수행한다. 실물 5종·simulation 3종에서 위치/방향 오차를 평가하고 세 물체를 좁은 상자 안에 순차 배치하는 예를 제시한다. 성공의 보편적인 binary threshold 대신 최종 object pose 오차를 보고한다 (§III-C–IV, PDF pp.4–7).

## 4. Method

### 4.1. Overall Pipeline

RGB 영상 이진화·bounding rectangle → coarse/last-inch visual localization → 초기 push pose → tactile image의 local contact pose → tactile servo + EEF/goal alignment → 3단계 pushing → stage 3에서 visual localization을 다시 사용한다. 초기 vision을 한 번만 쓰는 구조로 분류하지 않는다 (§III, Figs.2–5, PDF pp.3–4).

### 4.2. Observation

| 수신 모듈 | 입력 | 역할/경계 | 근거 |
| --- | --- | --- | --- |
| Visual estimator | EEF-mounted image; camera/robot 상대 pose label로 학습 | Bottleneck에 대한 planar position/orientation 예측; coarse phase에서 연속 갱신 | §III-A1/B, pp.2–4 |
| Tactile PoseNet | Real TacTip 영상→GAN simulated image 또는 sim tactile depth map | Normal depth와 normal에 대한 두 각도; full object pose 아님 | §III-A2/3, p.3 |
| Fine controller | Contact pose 3성분; proprioceptive EEF pose; target position/bearing; stage; 시각으로 얻은 rectangle dimensions | 접촉면 수직 유지와 목표 정렬; target pose는 current object pose와 구분 | §III-A2/C, pp.3–4 |
| 평가 경로 | 물체 윗면 ArUco pose | 실물 궤적 및 최종 object error 측정용으로 기술; 실행 fine-policy 입력으로 명시하지 않음 | §IV-A, p.5 |

### 4.3. Action

EEF pose를 갱신하는 이산 position command로 pushing한다. Fine phase는 접촉면에 수직을 유지하는 성분과 target 방향 정렬을 결합한다. 전체 action vector 차원·gain 수치는 이 PDF에서 미명시이며 인용 논문의 내용으로 채우지 않는다 (§III-A2/C, pp.3–4; §V, p.7).

### 4.4. Controller

Dobot MG400 4-DoF position control. Stage 1은 목표 지향, stage 2는 목표 부근에서 고정 target bearing을 따르는 direction-driven control, stage 3은 반대 면으로 재접근해 최종 pose 보정. 이전 tactile pushing controller의 자세한 기술은 [6]으로 넘긴다 (§III-C, p.4).

### 4.5. Learning / Optimization Method

RL이 아니다. Coarse 모델 f와 last-inch 모델 g는 robot을 자동 이동하며 얻은 영상과 상대 bottleneck pose로 supervised/self-supervised 학습한다. Vision 영상은 이진화 후 minimum bounding rectangle를 fit한다. PoseNet은 simulation contact image/pose로 학습하고 real-to-sim GAN은 paired images로 학습한다. 구체적인 loss/층 구성/학습량은 인용 문헌으로 넘겨 이 PDF에서 확인되지 않는다 (§III-A3/B, pp.3–4).

## 5. Object Information

Pose 제공은 phase마다 다르므로 `기타`로 분류한다. Fine tactile contact pose를 full current object pose tracking으로 집계하지 않는다.

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Coarse visual relative bottleneck 위치; stage 3 visual relocalization | Coarse에서 연속, stage 3에서 재사용; fine pushing 중 full object xy estimator 명시 없음 | Fine에서는 EEF pose·target·rectangle dimensions 사용. ArUco object trajectory는 평가용 (§III–IV, pp.3–5). |
| Orientation | 기타 | Visual rectangle axis/relative angle; fine tactile surface-normal 두 각도 | Coarse/relocalization 및 local contact normal 갱신 | Surface normal angle과 full planar object orientation을 동일시하지 않음. Apple rectangle orientation 한계 (§IV-B, p.6). |
| Shape / Geometry | Initial | Visual minimum bounding rectangle의 dimensions 및 접촉면 선택 | Coarse에서 획득; shape 자체를 timestep tracking한다고 명시하지 않음 | Full CAD/mesh 입력 없음; 제한적 shape prior를 실제 controller가 사용 (§III-B/C, p.4). |
| Physical Parameters | 미제공 | 질량·마찰의 controller 입력은 명시되지 않음 | 없음 | 다양한 물체 물성은 실험 조건이며 online 물성 estimator는 없음 (§IV-A, p.5). |

## 6. Missing Object Information and Compensation

- Tactile이 uniform surface 위 절대 접촉 위치를 측정하지 못함 → EEF proprioception + target position + 초기 visual rectangle dimensions → 목표 방향·정지 위치를 정한다 (§III-A2/C, pp.3–4).
- Tactile single-stage pushing만으로 object orientation 목표를 제어하지 못함 → visual localization·shape axis + multi-stage 재접촉 → 목표 position/orientation을 함께 맞춘다 (§III-C/IV-B, pp.4–6).
- 초기 object 접근 정보 부재 → coarse visual bottleneck 추정 → tactile contact가 가능한 시작 상태로 이동한다. 이는 저자가 명시한 역할 분담이며 모달리티별 독립 ablation으로 분해한 결과는 아니다 (§I, p.1).

## 7. Tactile

### 7.1. Raw Sensor

실물 TacTip biomimetic optical tactile sensor 1개를 EEF에 장착한다. Sim에서는 256×256 contact depth map을 사용한다. 실물 영상의 정확한 raw 해상도는 별도 명시 없음 (§IV-A, p.5).

### 7.2. Preprocessing

Real tactile image를 paired-image GAN으로 simulated representation으로 번역한 뒤 PoseNet에 입력한다. 이미지 이진화는 이 논문의 visual preprocessing이며 tactile binary 변환으로 기록하지 않는다 (§III-A3/B2, pp.3–4).

### 7.3. Policy Representation

PoseNet의 출력은 surface-normal 접촉 깊이 1개와 normal에 대한 orientation angle 2개다. 다른 pose 성분은 0으로 둔다 (§III-A2, p.3).

### 7.4. Retained Information

Local contact depth와 surface normal orientation. Contact image의 원시 공간 패턴 대신 이 3개 성분이 controller로 간다 (§III-A2, p.3).

### 7.5. Removed / Unavailable Information

원문 명시: 균일 표면의 접선 방향 위치는 측정할 수 없다. 표현 구조상 full global object position/shape, distributed pressure/shear map은 이 3개 출력에 포함되지 않는다. Force magnitude 추정값을 output으로 명시하지 않음 (§III-A2, p.3).

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. 별도 wrist F/T·force sensor·estimated wrench 입력이 명시되지 않는다.

### 8.2. Representation

해당 없음. Tactile contact depth를 Newton 단위 force로 환산하지 않는다.

### 8.3. Role

해당 없음.

### 8.4. Required Assumptions

F/T-only 추정 가정은 해당 없음. Tactile method는 local surface contact pose와 EEF proprioception을 사용한다.

### 8.5. Reported Limitation / Ambiguity

원문에서 F/T ambiguity를 직접 논의하지 않음.

## 9. Other Observations

- Proprioception: EEF pose로 target alignment를 계산한다.
- Vision: coarse/last-inch 및 stage 3 relocalization; fine 내 full-pose 연속 tracking으로 명시되지 않음.
- Goal: position과 orientation/bearing은 제공한다.
- History / previous action / recurrent state: 명시적 policy 입력으로 미명시.
- Estimator: visual relative bottleneck pose와 tactile local contact pose를 서로 분리한다.
- 평가용 ArUco: 물체 궤적/오차 계측용이다 (§III–IV-A, pp.3–5).

## 10. Tactile–Other Modality Relationship

Vision은 접근 가능한 물체 위치·방향·제한적 shape를 제공하고 tactile은 접촉 중 local depth/normal 변화를 제공한다. EEF proprioception과 goal은 tactile의 surface-tangential 위치 부재를 넘어 target alignment를 수행하게 한다. 이러한 모듈 역할은 method에서 확인되지만 Table III는 전체 multi-stage 설계와 single-stage를 비교하므로 vision·shape·stage switching 각각의 독립 효과는 분리하지 못한다. F/T 결합은 없다 (§III, pp.3–4; Table III, p.6).

## 11. Training-only / Privileged Information

비-RL이다. Actor/Critic/Reward/Termination의 RL 구분은 해당 없음. 학습용 robot-relative pose, simulated tactile pose, GAN paired images와 평가용 ArUco는 별도 supervision이다.

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§III-A/B, pp.2–4; §IV-A, p.5) |
| Critic | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§III-A/B, pp.2–4; §IV-A, p.5) |
| Reward | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§III-A/B, pp.2–4; §IV-A, p.5) |
| Termination | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§III-A/B, pp.2–4; §IV-A, p.5) |
| Curriculum | 해당 없음: 비-RL | 해당 없음 | Robot-relative bottleneck pose label; simulated tactile/contact pose; paired real/sim images. RL curriculum은 해당 없음. (§III-A/B, pp.2–4; §IV-A, p.5) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Multi-stage가 single-stage보다 최종 object 위치 오차를 낮춤 | Controlled comparison | 각 object/method 30 trials; 기존 single-stage tactile push vs multi-stage visual+tactile control | 실물 cuboid x 5.4±3.0→2.4±1.6 mm, y 6.9±2.5→2.9±1.4 mm; 각 p<0.0001. 센서 단독 제거가 아닌 전체 제어 전략 비교. | §IV-A/B; PDF pp.5–6 ; Table III |
| Multi-stage의 orientation 제어 | Controlled comparison | 같은 Table III의 object orientation 결과 | 실물 cuboid 2.0±0.8°, hexagon 2.5±1.1°, apple N/A. Single-stage orientation란은 N/A이므로 임의 수치 이득을 만들지 않음. | §IV-B; PDF p.6 ; Table III |
| Tactile local-pose가 주지 못하는 tangential 위치 | Author explanation only | Uniform surface의 surface pose 구성 | Surface 위치는 측정 불가라 해당 성분을 0으로 두고 proprioceptive EEF pose/goal로 정렬한다. | §III-A2; PDF p.3 ; Fig.3 |
| 제한적 shape 표현의 실패 | Failure analysis | Apple의 bounding rectangle orientation | Round object는 orientation을 항상 0 rad로 예측한다고 보고; shape preprocessing이 모든 물체에 적합하지 않음. | §IV-B1/V; PDF pp.6–8 ; Table II |

## 13. Author-stated Limitations

저자는 MG400의 position control 때문에 연속 motion 대신 discrete pushes를 사용해 속도가 느리고, 이산 push가 최종 정확도에 미치는 영향은 미확인이라고 명시한다. Image preprocessing이 모든 물체 pose를 잘 찾지는 못하며 apple의 orientation이 0으로 추정되는 사례가 있다 (§IV-B1/V, PDF pp.6–8).

## 14. Author-stated Future Work

다른 robot arm의 velocity/continuous control, discrete pushing 정확도 영향 조사, 3D point cloud로 더 정밀한 object pose와 3D pushing 확장, 다른 manipulation 및 throw-and-catch 같은 동적 과제로 확장할 가능성을 제시한다. 구현 결과가 아닌 저자의 향후 방향이다 (§V, PDF pp.7–8).

## 15. Review-relevant Findings

- Tactile representation은 binary가 아니라 contact-depth/normal-angle 3성분이다.
- Uniform surface 위 위치를 tactile만으로 측정할 수 없다고 원문이 명시한다.
- Vision은 초기 coarse phase뿐 아니라 stage 3에서도 재사용한다.
- EEF proprioception·target·visual rectangle dimensions가 함께 제공된다.
- ArUco는 object-level 평가에 사용하며 reward/Actor GT로 기록하지 않는다.
- 전체 multi-stage 비교는 있으나 tactile/vision 각각의 독립 ablation은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §III-A–C, pp.3–4 |
| Object pose / shape | §III-B/C, p.4; 평가 경로 §IV-A, p.5 |
| Tactile | §III-A2/3, p.3; §IV-A, p.5 |
| F/T | §III pp.3–4의 입력 목록; 사용 없음 |
| Reward / Critic | 비-RL; 해당 없음 |
| Ablation / comparison | §IV-A/B, pp.5–6; Table III |
| Limitation | §V, pp.7–8 |
| Future Work | §V, pp.7–8 |
