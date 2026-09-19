# Force Policy: Learning Hybrid Force-Position Control Policy under Interaction Frame for Contact-Rich Manipulation

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B019
- Authors: Hongjie Fang; Shirun Tang; Mingyu Mei; Haoxiang Qin; Zihao He; Jingjing Chen; Ying Feng; Chenxi Wang; Wanxi Liu; Zaixing He; Cewu Lu; Shiquan Wang
- Year: 2026
- Venue: Not stated (arXiv preprint)
- DOI / arXiv: 미명시 / 2602.22088v2
- PDF version: arXiv v2; 9 May 2026
- Page count: 24
- SHA-256: `32f6abdeacef110e29c8239bb80afc1b997dce84937a765b55260e00c7b82034`
- PDF filename: `Fang 등 - 2026 - Force Policy Learning Hybrid Force-Position Control Policy under Interaction Frame for Contact-Rich.pdf`
- 분석 근거: 선택 PDF 원문을 새로 읽었다. 기존 논문 상세 노트를 근거로 사용하지 않았다. 본문 pp.1–9 및 포함된 Supplement pp.13–24를 읽었다. 핵심 Table II–VI 및 Fig.5–9를 PDF 렌더로 확인했다.

## 2. Relevance to This Review

**Relevant**. 손목/플랜지 F/T와 운동 이력으로 접촉 제어 좌표계와 힘·위치 제어 축을 구성한다. 동일한 힘·운동 신호만으로 마찰과 탄성 변형을 구별하기 어려워 시각·과업 의미 정보를 학습 라벨 생성에 추가한다. F/T의 정보적 한계와 추가 가정, 시각과 힘의 실행 역할을 직접 비교할 수 있다.

## 3. Task

상자를 무거운 장애물에 밀어 뒤집기, EV charger 삽입, 스티커 부착/압착을 수행한다. Sticker는 easy/hard 두 조건이다. Flip 20회, 나머지 조건별 10회 평가하며 flip·plugging은 중간 단계 완료에 0.5점을 주므로 표의 success rate가 모두 이진 성공 횟수는 아니다. (§V-A–B, PDF pp.6–7; Supplement V, pp.19–22)

## 4. Method

### 4.1. Overall Pipeline

전역 RGB-D point cloud → 5 Hz RISE-2의 전역 행동/latent feature → 손목 RGB·EEF pose/wrench history와 결합한 50 Hz local Force Policy → interaction frame(IF), relative pose, reference wrench, force/position selection mask → hybrid controller. Contact-aware scheduler가 두 정책 사이 전환 및 궤적 지연 정렬을 담당한다. (§IV-B–C, pp.5–6; Supplement III–IV, pp.17–19)

### 4.2. Observation

전역 정책은 현재 3D point cloud를 사용한다. 지역 정책은 손목 RGB, 9D EEF pose 표현 및 6D wrench의 이력, cached 512D 전역 feature를 입력받는다. Eq.(5)의 간략 표현만으로 wrist vision을 누락하면 안 된다. GRU는 pose/wrench 이력을, ResNet-18은 wrist image를 인코딩한다. 명시적 current object pose vector는 입력 목록에서 확인되지 않는다. 이력 길이의 수치는 미명시이다. (§IV-B, p.5; Supplement III, pp.17–18)

### 4.3. Action

IF-relative pose(9D 회전 연속 표현 포함), 6D reference wrench, 6축 binary selection mask를 예측한다. Mask의 1은 force-controlled axis이며 tactile binary representation이 아니다. Local action chunk에서 첫 행동만 실행하고 나머지는 버린다. (§IV-B–C; Supplement III, p.18)

### 4.4. Controller

힘 제어와 위치 제어를 IF 축별로 선택한다. 글로벌 trajectory chunk와 실행 궤적을 DTW로 정렬하고 연속 가속도 smoothing을 적용한다. Flexiv Rizon 4, GN02 gripper, flange 6-axis F/T, global/wrist D415를 사용한다. Local policy의 직접 출력이 joint torque라는 근거는 없다. (§IV-C–V-A, pp.5–6; Supplement IV, pp.18–19)

### 4.5. Learning / Optimization Method

모방학습이다. 과업별 고품질 arm-to-arm force-feedback teleoperation demonstration 50개를 수집하고, global policy 학습 후 고정하여 local policy를 훈련한다. MIP action loss와 frame/wrench regression, mask classification을 사용한다. Gemini 3 Pro에 초기 영상과 과업 설명을 주어 friction/stiffness 주도 상황을 판정하고 demonstration IF label을 만든다. 이는 offline label 생성이며 매 timestep 온라인 LLM 입력이 아니다. (§IV-A–B, pp.4–5; Supplement II–III/V-B, pp.15–18/20)

## 5. Object Information

실행 입력과 학습·평가용 정답을 구분한다.

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | 실행 중 global point cloud·wrist RGB; 명시적 object position vector 미확인 | 시각 입력은 계속 갱신 | EEF pose history는 물체 pose가 아님 |
| Orientation | 기타 | 시각 latent 및 접촉 제어 IF | 시각/IF 갱신 | IF orientation은 current object orientation 정답과 다름 |
| Shape / Geometry | 기타 | 현재 장면 point cloud와 wrist image의 부분적 기하 | 전역 5 Hz; 지역 50 Hz 정책 | 개별 물체 full mesh/CAD 입력은 미명시 |
| Physical Parameters | 미제공 | 수치 물성 입력 미확인; offline 시각·언어로 지배적 접촉 regime 분류 | 수치 물성 업데이트 해당 없음 | 마찰·탄성 의미 prior와 수치 friction/stiffness GT를 구분 |

## 6. Missing Object Information and Compensation

명시적 contact point 및 완전한 접촉 구조 미추정 → wrench + EEF motion history + 학습용 visual/semantic regime prior → IF orientation과 force/position 제어 subspace를 구성한다.

마찰 소산과 탄성 변형은 같은 force–motion power 패턴을 만들 수 있음 → 초기 image/task semantics로 offline label의 지배적인 regime을 구별한다. 실행 시에는 계속 갱신하는 visual policy feature와 wrist RGB가 함께 사용된다. 따라서 force-only contact localization이나 초기 시각 이후의 blind control로 분류하지 않는다. (§IV-A–B; Supplement II, pp.4–5/15–17)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. Binary mask는 제어 축 선택이다.

### 7.2. Preprocessing

사용하지 않음. Binary mask는 제어 축 선택이다.

### 7.3. Policy Representation

사용하지 않음. Binary mask는 제어 축 선택이다.

### 7.4. Retained Information

사용하지 않음. Binary mask는 제어 축 선택이다.

### 7.5. Removed / Unavailable Information

사용하지 않음. Binary mask는 제어 축 선택이다.

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

로봇 flange의 6-axis F/T sensor. Joint-torque estimated wrench와 구분한다. (§V-A, p.6)

### 8.2. Representation

Gravity-compensated 6D wrench와 EEF twist/pose history. Force/moment를 IF로 변환하며 reference wrench도 학습한다. Human demonstration의 부드러운 운동에서는 inertial effect를 무시한다. (§IV-A, p.4; Supplement III, p.18)

### 8.3. Role

Policy observation, IF 라벨 생성, 원하는 force/moment의 axis별 regulation, contact-aware policy routing. 정확한 접촉점 추정은 수행하지 않는다. (§IV, pp.4–6; §VI, p.9)

### 8.4. Required Assumptions

이론은 국소적으로 conservative한 elastic response와 접촉 topology 불변성, symmetric stiffness 및 전문가 행동의 principal-axis 정렬을 사용한다. Supplement의 Hertzian ellipse/contact patch, Winkler foundation, stiffness-centroid·반사 대칭 가정과 isotropic dissipation이 축 정렬 근거다. 다중점/면 접촉 일반화도 macroscopic reflectional symmetry를 요구하므로 임의의 multi-contact 복원은 아니다. 실제 IF 원점은 EEF로 둔다. (§III–IV, pp.3–4; Supplement I, pp.13–15)

### 8.5. Reported Limitation / Ambiguity

동일 wrench/twist power에서 friction과 stiffness의 원인을 판별하기 어렵다. Friction으로 wrench-only IF 축이 틀어질 수 있다. Contact point는 추정하지 않으며 nonsmooth/nonconservative fracture 상황은 이론 범위 밖이다. (§IV-A/§VI, pp.4/8–9; Supplement II, pp.15–17)

## 9. Other Observations

- Proprioception: EEF pose/twist history를 GRU로 인코딩해 접촉 운동과 wrench를 함께 해석한다.
- Vision: global point cloud와 wrist RGB가 실행 중 제공된다. Offline initial image/task description은 IF supervision용이다.
- History: local pose/wrench history와 scheduler의 실행 궤적 이력은 서로 다른 용도다.
- Previous Action: 독립적인 previous-action policy input은 미명시이다. Scheduler는 과거 실행 궤적을 사용한다.
- State Estimator: 완전한 object/contact state estimator가 아니라 IF orientation 및 제어 subspace를 예측한다. (§IV; Supplement III–IV)

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않으므로 tactile이 F/T에 추가하는 정보는 검증하지 않는다. 실제 결합은 vision + F/T + robot motion history이다. Vision/semantics의 offline regime label 역할과 online scene/goal guidance를 분리해야 한다.

## 11. Training-only / Privileged Information

비-RL 모방학습이므로 Actor/Critic/Reward/Termination의 RL GT 분류는 해당 없음이다. 물리·의미적 supervision이 전혀 없다는 뜻은 아니다.

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV-A–B; Supplement II–III/V-B, pp.4–5/15–18/20) |
| Critic | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV-A–B; Supplement II–III/V-B, pp.4–5/15–18/20) |
| Reward | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV-A–B; Supplement II–III/V-B, pp.4–5/15–18/20) |
| Termination | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV-A–B; Supplement II–III/V-B, pp.4–5/15–18/20) |
| Curriculum | 해당 없음: 비-RL | 해당 없음 | Teleoperation pose/wrench/vision 및 offline Gemini semantic regime label과 analytic IF label. Simulator object-pose GT를 쓰는 RL curriculum이 아님. (§IV-A–B; Supplement II–III/V-B, pp.4–5/15–18/20) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Force Policy 전체 시스템의 과업 성능 | Controlled comparison | RISE-2, pi0.5, RDP, FoAR, ForceVLA, TA-VLA | Force Policy flip95%, EV65%, easy100%, hard90%. Controller·scheduler·architecture가 함께 달라 순수 F/T ablation은 아님. Flip/EV는 partial credit 포함. | §V-B; PDF p.7 ; Table II |
| Semantic/kinematic IF label이 wrench-only label보다 유용 | Representation ablation; Controlled comparison | Wrench-only IF label로 학습 vs 제안 IF label | Hard sticker success 50% vs90%; IF >20° error 비율 4.9% vs3.6%. | §V-C; PDF p.8 ; Fig.6 |
| Scheduler 자체도 성능에 기여 | Controlled comparison | Vision-only policy에 제안 scheduler 추가 | Flip RISE-2 42.5→62.5%, pi0.5 52.5→77.5%. Force 정보의 단독 효과로 전체 차이를 설명할 수 없음. | Supplement IV; PDF p.19 ; Table V |
| Force tracking과 motion smoothness | Controlled comparison | 제안 scheduler 적용 전후; demonstration force profile와 비교 | SPARC linear -4.515→-2.640, angular -3.935→-2.967; force profile 정성 비교. | §V-B–C; PDF pp.7–8 ; Fig.5; Fig.7 |
| 고하중에서 실패 원인 | Failure analysis | EV charger; 약160 N 요구 | 작은 motion/IF 오차도 로봇 torque-limit 보호를 일으켜 제안 방법에도 실패가 남음. | Supplement V-E; PDF p.20 |

## 13. Author-stated Limitations

이론은 접촉 topology가 유지되는 국소 conservative response를 전제로 하며 fracture 등 급격한 비보존 전이는 다루지 않는다. 검증 범위는 주로 surface contact와 insertion이다. 정확한 contact point/완전한 contact structure는 추정하지 않는다. EV charger의 약160 N 삽입은 로봇 torque limit 근처여서 작은 예측 오차에도 보호 정지가 발생한다. (§VI, pp.8–9; Supplement V-E, p.20)

## 14. Author-stated Future Work

더 복잡한 접촉 과업, contact structure를 모델링한 torque control, connector를 당겨 체결을 확인하는 것과 같은 high-level force-driven decision을 향후 방향으로 명시한다. Saturation 근처 force control의 정밀화도 남아 있다. (§VI, p.9; Supplement V-E, p.20)

## 15. Review-relevant Findings

- 실행 시 F/T·EEF 이력 외에 현재 global point cloud와 wrist RGB를 사용한다.
- Semantic prior는 힘·운동만으로 모호한 friction/stiffness label을 만드는 offline 단계에 쓰인다.
- IF 추정은 contact point localization 또는 full object-pose tracking과 같지 않다.
- Wrench-only IF와 비교한 실험은 존재하지만 tactile과의 비교는 없다.
- 전체 시스템 비교에는 scheduler 차이가 포함되며 binary selection mask는 tactile이 아니다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / Object pose | §IV-B, p.5; Supplement III, pp.17–18 |
| Tactile | 미사용; 제어 mask 설명 §IV-B |
| F/T / Assumptions | §III–IV, pp.3–6; Supplement I–II, pp.13–17 |
| Reward / Critic | 해당 없음: 모방학습 |
| Ablation | §V-C, p.8, Fig.6–7; Supplement IV, p.19, Table V |
| Limitation / Future | §VI, pp.8–9; Supplement V-E, p.20 |
