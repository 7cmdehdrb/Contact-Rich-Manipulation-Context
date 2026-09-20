# Pose-and-shear-based tactile servoing

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B051`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: John Lloyd; Nathan F. Lepora
- Year: 2024
- Venue: The International Journal of Robotics Research 43(7), 1024–1055
- DOI / arXiv: 10.1177/02783649231225811 / Not stated
- PDF version: Publisher version
- Page count: 32
- SHA-256: `dbb9876a0719e4e18e36c59234ecff5ec525f253a26ef2e2590a1f68804aea66`
- PDF filename: Lloyd 및 Lepora - 2024 - Pose-and-shear-based tactile servoing.pdf
- 확인 범위: PDF pp.1–32 전체(본문 pp.1–26, 참고문헌 pp.26–28, Appendices A–D pp.28–32); Tables 2/4/6–9 렌더 확인.

## 2. Relevance to This Review

`Relevant`

외부 vision/current whole-object pose 없이 tactile의 local pose-and-shear와 proprioception으로 surface following과 pushing을 수행한다. 특히 slip-induced tactile aliasing을 uncertainty model 및 robot kinematics 기반 Bayesian filter로 보완하고 그 효과를 비교한다. Binary marker image와 영역별 contact Boolean은 다른 표현이므로 구분해서 분석한다.

## 3. Task

Object tracking, curved surface following, single/dual-arm pushing을 실물 Panda와 TacTip으로 수행한다. Pushing은 global object center pose 목표가 아니라 sensor-object contact normal이 목표에 얼마나 근접했는지 평가하며, sensor tip center가 목표에 tip radius 20 mm 이내이면 종료한다. Tall objects는 follower arm으로 넘어짐을 억제한다. [§3.3.3–4 pp.11–12; §5 pp.16–25]

## 4. Method

### 4.1. Overall Pipeline

TacTip marker image → grayscale/crop/blur/binarize/resize → Gaussian-density network의 local contact pose/shear mean+uncertainty → robot kinematic motion과 SE(3) Bayesian filter → PID tactile servo + 필요 시 target-alignment PID → Cartesian velocity → robot low-level control. [§3/Fig.5, pp.5–12]

### 4.2. Observation

Estimator는 현재 tactile image, 이전 filtered state/covariance, robot kinematics로 얻는 sensor pose 변화량을 받는다. Controller는 filtered local feature pose/shear, reference contact pose, feedforward velocity를 받으며 pushing에서는 proprioceptive EEF pose와 work-frame goal도 사용한다. 이 local surface pose는 whole-object absolute pose가 아니다. Leader robot trajectory는 tracking 시험의 stimulus/평가이며 follower에 object GT pose 입력으로 전달한다고 하지 않는다. [§3.2–3.3 pp.9–12; §5.4 pp.16–17]

### 4.3. Action

6D Cartesian velocity twist. Tracking에서는 feedforward 0, surface following에서는 surface tangential feedforward, pushing에서는 surface normal 방향 feedforward와 lateral target alignment를 합친다. [§3.3 pp.10–12]

### 4.4. Controller

SE(3) error의 MIMO PID; pushing은 SISO bearing PID 추가. Derivative 전 exponential moving average 0.5, task별 integral/output clipping을 사용한다. libfranka low-level 1 kHz, pyfranka에서 velocity/acceleration/jerk constraints를 유지한다. High-level tactile control 주기는 단일 고정 수치로 명시되지 않는다. [§3.3/§4.4 pp.10–13; Appendix D p.32]

### 4.5. Learning / Optimization Method

Supervised GDN tactile estimator를 NLL로 학습하며 CNN MSE regression과 비교한다. Flat printed surface에서 6000 train/2000 validation/2000 test, robot-controlled normal contact 후 shear의 pose label을 수집한다. Adam, batch 16, LR schedule 및 early stopping. Controller와 Bayesian filter는 RL이 아니다. [§3.1 pp.5–8]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Tactile에서 sensor-relative local surface contact depth와 shear를 추정 | 매 sensor/control cycle 갱신 | Whole-object center/current absolute position tracking 없음. Goal과 EEF pose 별도. [§3.1–3.3, PDF pp.5–12] |
| Orientation | 기타 | Local surface normal angles와 post-contact rotation shear | 매 cycle 갱신 | Global object orientation이 아니라 local contact feature orientation. [§3.1–3.3, PDF pp.5–12] |
| Shape / Geometry | 기타 | Locally flat surface prior; flat-surface training; known hemispherical sensor geometry | Full object shape는 미제공; prior 고정 | Object mesh/CAD/identity를 controller에 제공하지 않는다. 곡면으로 일반화한다. [§3.1 pp.5–6; §4.2 pp.12–13] |
| Physical Parameters | 미제공 | Object mass/friction을 controller input으로 제공하지 않음 | 해당 없음 | 실험 object mass 목록과 surface 종류는 분석 metadata이지 실행 input이 아니다. [§4.3/§5 pp.13–25] |

## 6. Missing Object Information and Compensation

Global object state/shape 미제공 → local tactile pose-and-shear + EEF pose + goal → 접촉을 유지하며 surface following/pushing을 수행한다.

Slip 때문에 tactile image 하나로 shear가 모호함 → GDN uncertainty + robot kinematics의 변화량 + Bayesian temporal state → 불확실한 관측을 prediction과 결합해 오차를 줄인다. 이 후자는 저자 명시와 Table 2 비교로 뒷받침된다. 다만 Table 2의 offline filter test는 label-derived pose 변화에 synthetic noise를 더한 것이며 실행 중 object GT를 넣은 실험은 아니다. [§3.2 pp.9–10; §5.3 pp.14–17]

## 7. Tactile

### 7.1. Raw Sensor

1개 또는 2개 TacTip; robot EEF에 장착. 지름 40 mm hemispherical soft tip 내부 331 marker-tipped pins를 USB camera+LED로 촬영한다. Normal deformation과 tangential/torsional shear에 반응한다. [§4.1–4.2, pp.12–13]

### 7.2. Preprocessing

640×480 image → 8-bit grayscale → 430×430 crop → 5×5 median blur → adaptive threshold binary image → 128×128 resize → float [0,1]. 이 Binary는 contact presence taxel이나 region Boolean이 아니라 marker image의 intensity binarization이다. [§3.1.3, p.6]

### 7.3. Policy Representation

GDN은 local contact pose의 depth/normal orientation $(z,\alpha,\beta)$와 post-contact shear $(x,y,\gamma)$를 결합한 6D mean과 6개 inverse standard deviation을 예측한다. Filter 후 mean/covariance와 local feature pose가 controller로 간다. [§3.1.1/3.1.5/3.2, pp.5,7–10]

### 7.4. Retained Information

Marker pattern의 공간 배치·변형을 통해 local depth/normal orientation 및 translational/rotational shear를 추정한다. Uncertainty도 유지한다. Force 단위로 calibration한 wrench가 아니다. [§5.1–5.3, pp.13–17]

### 7.5. Removed / Unavailable Information

Representation 구조상 raw image 세부 texture/intensity는 6D pose/shear와 uncertainty로 축약된다. Global object pose/shape, force magnitude/pressure field는 출력하지 않는다. 원문이 직접 지적한 손실/ambiguity는 slip으로 서로 다른 shear label에 비슷한 tactile image가 대응하는 tactile aliasing이다. [§3.1 p.6; §6.1 pp.22–23]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [§3–4, pp.5–13]

### 8.2. Representation

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [§3–4, pp.5–13]

### 8.3. Role

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [§3–4, pp.5–13]

### 8.4. Required Assumptions

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [§3–4, pp.5–13]

### 8.5. Reported Limitation / Ambiguity

사용하지 않음. F/T-only 방법 및 tactile–F/T 결합 분석은 해당 없음. [§3–4, pp.5–13]

## 9. Other Observations

Proprioception은 sensor pose 변화에 의한 filter prediction 및 goal bearing/distance 계산에 사용한다. History는 Bayesian state/covariance와 PID integral/derivative에 남으며 고정 frame stack이나 recurrent neural hidden state가 아니다. Goal pose와 reference contact pose, feedforward velocity는 controller command다. 외부 vision 입력은 없다. [§3.2–3.3, pp.9–12]

## 10. Tactile–Other Modality Relationship

Tactile은 local contact geometry/shear, proprioception은 연속 sensor motion 및 work-frame goal relation을 제공한다. Filter가 이 둘을 결합하는 이유는 shear aliasing의 보완으로 명시된다. F/T를 병용하지 않는다. Marker binary image를 영역별 Boolean으로 더 축약한 실험은 없으므로 그 성능을 이 결과에서 추정할 수 없다. [§3.2/§5.3/§6.1, pp.9–10,14–17,22–23]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | Robot pose로 supervised tactile labels를 생성한다. Offline filter 평가의 dynamics는 test labels+synthetic noise이며 실제 servo filter는 robot sensor kinematics를 쓴다. RL actor/critic/reward/termination/curriculum은 해당 없음. [§3.1/§5.3, pp.5–8,14–17] |
| Critic | Not applicable | 비-RL | Robot pose로 supervised tactile labels를 생성한다. Offline filter 평가의 dynamics는 test labels+synthetic noise이며 실제 servo filter는 robot sensor kinematics를 쓴다. RL actor/critic/reward/termination/curriculum은 해당 없음. [§3.1/§5.3, pp.5–8,14–17] |
| Reward | Not applicable | 비-RL | Robot pose로 supervised tactile labels를 생성한다. Offline filter 평가의 dynamics는 test labels+synthetic noise이며 실제 servo filter는 robot sensor kinematics를 쓴다. RL actor/critic/reward/termination/curriculum은 해당 없음. [§3.1/§5.3, pp.5–8,14–17] |
| Termination | Not applicable | 비-RL | Robot pose로 supervised tactile labels를 생성한다. Offline filter 평가의 dynamics는 test labels+synthetic noise이며 실제 servo filter는 robot sensor kinematics를 쓴다. RL actor/critic/reward/termination/curriculum은 해당 없음. [§3.1/§5.3, pp.5–8,14–17] |
| Curriculum | Not applicable | 비-RL | Robot pose로 supervised tactile labels를 생성한다. Offline filter 평가의 dynamics는 test labels+synthetic noise이며 실제 servo filter는 robot sensor kinematics를 쓴다. RL actor/critic/reward/termination/curriculum은 해당 없음. [§3.1/§5.3, pp.5–8,14–17] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| GDN uncertainty estimation의 정확도 | Controlled comparison | 10 CNN vs 10 GDN models, 동일 data | 모든 component MAE가 개선; 예 vz 0.164→0.123, rotational z 1.44→1.16(Table 1 표기 단위 유지). | §5.2; PDF pp.14,16 ; Table 1 ; Fig.12 |
| Kinematic/dynamics filtering의 보완 효과 | Controlled comparison | GDN 단독 vs filter; label-derived motion+synthetic noise 수준 변화 | Table 2 vx MAE 0.426→0.062(최소 noise); noise가 커지면 단독 수준으로 수렴. Offline 평가 조건을 포함해야 함. | §5.3; PDF pp.14–17 ; Table 2 ; Fig.13 |
| Shear가 manipulation에 기여하는 역할 | Author explanation only | Shear 제거 policy ablation 없음; tracking/pushing demonstrations | Tangential/rotational tracking과 follower 접촉 유지에 shear가 필요하다고 설명. Surface following의 shear gains는 0. | §6.2; PDF pp.24–25 |
| Pushing 결과와 제한 | Controlled comparison | Single/dual arm; MDF/foam; 각 object 5회 | Single circle MDF error 9.45±0.13 mm; dual 3.58±2.04 mm. Dual blue square MDF 5.24±0.24 mm이므로 본문 전체 <5 mm 주장과 표가 일치하지 않음. Tall objects는 foam에서 실패. | §5.6–5.7; PDF pp.19–25 ; Tables 3–5 |

## 13. Author-stated Limitations

Shear slip aliasing, training trajectory의 제한, flat/gently curved surface 가정, dynamics noise 설정 의존을 논의한다. Tall objects는 foam에서 leading edge가 걸려 성공하지 못했다. Planning이 없어 arm collision/joint limits/singularity 및 local objective로 달성하기 힘든 global pose tasks를 미리 처리하지 못한다. [§6.1–6.2, pp.22–25]

## 14. Author-stated Future Work

Slip detection으로 수집 data를 제한하거나 label을 추가하고, 실제 task와 유사한 trajectory 및 edge feature로 확장할 수 있다고 제안한다. Planning, 양팔의 active 협업, goal-pose guiding/insertion/assembly, tactile gripper와 multi-finger hands를 후속 방향으로 제시한다. [§6.1–6.2, pp.23–26]

## 15. Review-relevant Findings

- Contact pose/shear를 추정하지만 whole-object pose tracker는 아니다.
- Binary marker image는 contact region Boolean representation과 다르다.
- Shear ambiguity를 uncertainty와 kinematic history 기반 Bayesian filter로 보완한다.
- 실행 F/T 없이 local tactile feedback으로 real pushing을 수행한다.
- Pushing target error는 object center pose error가 아닌 contact normal 기준이다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / pose | §3.2–3.3 pp.9–12 |
| Tactile | §3.1 pp.5–8; §4.2 pp.12–13 |
| F/T | 사용하지 않음; §3–4 |
| Learning / labels | §3.1 pp.5–8 |
| Reward / Critic | 비-RL |
| Evidence | Tables 1–2 pp.16–17; Tables 3–5 pp.22,24–25 |
| Limitation / Future | §6 pp.21–26 |
| Appendix / controller | Appendices A–D pp.28–32 |
