# FACTR: Force-Attending Curriculum Training for Contact-Rich Policy Learning

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B047`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Jason Jingzhou Liu; Yulong Li; Kenneth Shaw; Tony Tao; Ruslan Salakhutdinov; Deepak Pathak
- Year: 2025
- Venue: Not stated (arXiv preprint)
- DOI / arXiv: Not stated / 2502.17432v2
- PDF version: arXiv v2, 2025-04-24
- Page count: 15
- SHA-256: `8d59e64b4e599f6cbb67096647f546b28fccca5ceaa7ef86df8500fbc3c4fcab`
- PDF filename: Liu 등 - 2025 - FACTR Force-Attending Curriculum Training for Contact-Rich Policy Learning.pdf
- 확인 범위: PDF pp.1–15 전체 및 Appendix VII–XII 확인; pp.9,14–15의 attention·ablation·task 결과표 렌더 확인. 외부 코드/영상 미확인.

## 2. Relevance to This Review

`Relevant`

Robot external joint torque를 vision과 결합하고 force 입력을 무시하는 학습 문제를 curriculum으로 완화한다. Sensor 및 curriculum 비교가 있어 접촉 정보의 실제 추가 역할을 평가할 수 있다. 측정원은 joint torque 및 gripper current이며 wrist F/T나 distributed tactile이 아니다.

## 3. Task

Franka Panda와 OpenManipulator-X gripper로 box lifting, non-prehensile pivoting, delicate fruit pick-and-place, dough rolling을 수행한다. 성공은 box를 2초 이상 균형 있게 들기, fixture에서 물체를 90° 회전시켜 세우기, fruit를 bowl에 놓기, dough를 cylinder로 8초 이상 rolling하기다. Bimanual box와 나머지 unimanual task의 action/torque source를 구분한다. [§V-A, PDF p.6]

## 4. Method

### 4.1. Overall Pipeline

실물 bilateral teleoperation으로 RGB·외부 joint torque·expert joint target 수집 → visual blur/downsampling 강도를 점차 낮추는 FACTR curriculum으로 BC → ViT visual tokens + MLP force token + Appendix의 gripper proprioception → action-chunking transformer → joint-position targets → follower control. Operator force feedback과 배포 policy observation은 별도 사용 경로다. [§III–IV; Appendix X, PDF pp.3–6,13–14]

### 4.2. Observation

본문은 현재 RGB image와 external joint torque를 입력으로 정의한다. Appendix X는 current hand joint angles를 추가하며 current arm joints는 generalization을 위해 제외한다고 명시한다. Box/pivot/dough는 arm external joint torque, fruit는 gripper torque 정보를 쓴다; gripper의 측정원은 servo current다. Object numerical pose/shape/physical parameters는 입력하지 않는다. External torque의 정확한 observation dimension 및 force token과 hand token 결합의 전체 상세는 미명시다. [§III-A/IV-A/V-A; Appendix X, PDF pp.3–6,13]

### 4.3. Action

Absolute joint-position targets의 100-step action chunk. Box는 두 arm joints, pivot/dough는 한 arm, fruit는 arm과 gripper joints를 출력한다. 전체 action dimension과 배포 policy frequency는 미명시다. [§IV-A; Appendix X/Table IV, PDF pp.4–5,13–14]

### 4.4. Controller

Leader motor torque는 follower external torque의 scaled feedback, null-space rest-pose regulation, gravity/friction compensation, joint-limit avoidance를 합한다. Gripper leader feedback은 follower current를 EMA(α=0.1)로 평활화한다. Follower bimanual system은 RMP로 joint targets를 생성하며 arm/table collision을 회피한다. Appendix의 500 Hz는 teleoperation friction compensation control-loop 주파수로 policy frequency가 아니다. [§III; Appendix IX, PDF pp.3–4,13]

### 4.5. Learning / Optimization Method

Real demonstration 기반 behavior cloning이며 RL이 아니다. Expert future joint targets에 MSE를 적용하고 AdamW로 20k–50k gradient steps 학습한다. Visual pixel 또는 latent에 Gaussian blur/downsampling을 적용하고 initial warm-up 뒤 intensity를 decay한다. 기본 task 실험은 latent Gaussian blur+linear schedule; fixed smoothing과 여러 scheduler/operator를 비교한다. 50 demonstrations를 수집했다고 하나 task별 분배는 해당 문장에 명시하지 않는다. [§IV–V; Appendix X, PDF pp.4–9,14]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | 현재 RGB appearance에서 얻는 implicit location cue | 계속 갱신 | 명시적 pose tracker 없음 [§IV-A/V-A, PDF pp.4–6] |
| Orientation | 기타 | 현재 RGB feature의 implicit orientation cue | 계속 갱신 | Task goal 90° 회전은 current numerical orientation input이 아님 [§IV-A/V-A, PDF pp.4–6] |
| Shape / Geometry | 기타 | RGB appearance의 implicit geometry | 현재 영상 입력 | Known CAD/dimensions input 없음; unseen shape/texture 평가 [§IV/V-C, PDF pp.4–8] |
| Physical Parameters | 미제공 | Object mass/friction/stiffness 명시 입력 없음 | 없음 | Robot dynamics는 teleoperation compensation용 [§III–V, PDF pp.3–8] |

## 6. Missing Object Information and Compensation

유사한 visual image에서 구분하기 어려운 contact/motion phase와 unseen object의 interaction 상태 → external joint torque/current → contact establishment, drop 후 contact loss, dough rolling 방향 전환의 단서를 제공한다. Curriculum은 early training에서 vision 의존을 줄여 그 단서를 사용하도록 유도한다. Force의 mode-switching 역할 일부는 저자 가설·attention 해석이며, contact location을 수치 추정한 결과는 아니다. [§V-C, Figs.8–9/Table I, PDF pp.7–9]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§III-A/IV-A/V-A, PDF pp.3–6]

### 7.2. Preprocessing

사용하지 않음. [§III-A/IV-A/V-A, PDF pp.3–6]

### 7.3. Policy Representation

사용하지 않음. [§III-A/IV-A/V-A, PDF pp.3–6]

### 7.4. Retained Information

사용하지 않음. [§III-A/IV-A/V-A, PDF pp.3–6]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§III-A/IV-A/V-A, PDF pp.3–6]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Franka Panda의 external joint torque readings. Fruit gripper는 external force sensor 없이 servo current를 사용. Wrist 6-axis F/T 및 estimated Cartesian wrench와 구분한다. [§III-A/V-A, PDF pp.3,6]

### 8.2. Representation

Joint torque/current vector → MLP force token. EEF 6D wrench로 변환하는 policy input은 없음. Gripper teleoperation feedback은 current EMA α=0.1; policy force preprocessing의 별도 filter는 미명시. [§III-A/IV-A, PDF pp.3–5]

### 8.3. Role

Teleoperator bilateral force feedback; policy observation; contact/mode switching과 contact-loss recovery; rolling phase 구분. [§III-A/V-C, Figs.8–9/Table I, PDF pp.3,8–9]

### 8.4. Required Assumptions

Follower에서 external joint torque sensing 사용 가능; leader/follower kinematic equivalence 및 torque scaling; leader dynamics/friction model. 별도의 F/T-only contact localizer는 없음. [§III; §VI; Appendix IX, PDF pp.3–4,9,13]

### 8.5. Reported Limitation / Ambiguity

Joint torque sensor precision/noise 때문에 subtle force adjustment가 어려울 수 있다고 명시. Net-wrench multi-contact/locality ambiguity는 직접 분석하지 않음. [§VI, PDF p.9]

## 9. Other Observations

Vision은 매 실행 단계 사용한다. Appendix X의 gripper joint angles는 proprioception이며 arm joints는 policy에서 제외한다. Low-level control은 robot state를 사용하므로 policy input과 혼동하지 않는다. 100-step action chunk는 future output horizon이며 sensor history가 아니다. Previous action·RNN·stacked observation history는 미명시다. Goal은 task demonstration에 내재하며 별도 object goal pose input은 없다. [§III–IV; Appendix X, PDF pp.3–6,13–14]

## 10. Tactile–Other Modality Relationship

Distributed tactile 사용은 없다. Vision+joint-load feedback의 결합을 vision-only 및 동일 센서의 no-curriculum과 비교한다. 따라서 force 입력 병용만으로 충분하다는 결론과, force를 실제 활용하도록 만드는 학습 방법의 효과를 구분한다. High-resolution tactile은 현재 센서가 아니라 저자의 향후 계획이다. [§V–VI, PDF pp.7–9]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | 비-RL. Human expert joint targets를 supervised label로 사용한다. Curriculum은 visual corruption schedule이며 simulator GT curriculum이 아님. [§IV; Appendix X, PDF pp.4–6,13–14] |
| Critic | Not applicable | 비-RL | 비-RL. Human expert joint targets를 supervised label로 사용한다. Curriculum은 visual corruption schedule이며 simulator GT curriculum이 아님. [§IV; Appendix X, PDF pp.4–6,13–14] |
| Reward | Not applicable | 비-RL | 비-RL. Human expert joint targets를 supervised label로 사용한다. Curriculum은 visual corruption schedule이며 simulator GT curriculum이 아님. [§IV; Appendix X, PDF pp.4–6,13–14] |
| Termination | Not applicable | 비-RL | 비-RL. Human expert joint targets를 supervised label로 사용한다. Curriculum은 visual corruption schedule이며 simulator GT curriculum이 아님. [§IV; Appendix X, PDF pp.4–6,13–14] |
| Curriculum | Not applicable | 비-RL | 비-RL. Human expert joint targets를 supervised label로 사용한다. Curriculum은 visual corruption schedule이며 simulator GT curriculum이 아님. [§IV; Appendix X, PDF pp.4–6,13–14] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Force 입력과 FACTR가 unseen-object 일반화를 개선 | Sensor ablation; Controlled comparison | ACT vision-only / vision+force / FACTR; task별 5–10 trials per object | Tables VII–X test success: box31.7/58.3/91.7%; pivot26/42/76%; fruit26.7/73.3/93.3%; dough0/70/80%. Main p.8의 평균21.3/61.2/87.5%와 단순 task-average는 일치하지 않아 임의로 통합하지 않음 | §V-C; Appendix XII; PDF pp.7–8,15 ; Tables VII–X ; Fig.6 |
| Contact loss 후 recovery | Controlled comparison; Failure analysis | Box를 첫 lift 후 떨어뜨리고 second attempt 평가 | Test objects: vision-only4/30, vision+force16/30, FACTR27/30. Force trace가 pre-lift로 돌아가 recovery한다는 설명은 저자 해석 | §V-C; PDF p.8 ; Table I |
| 고정 visual degradation보다 curriculum이 유리 | Controlled comparison | Pivot5 test objects×5trials; constant vs linear/cosine/exp/step, pixel/latent와 blur/pool | Constant15–17/25, decaying schedules17–21/25. 모든 scheduler 중 하나가 일관되게 우세하지 않음 | §V-D; PDF p.9 ; Table II |
| 유사 영상의 rolling/contact phase를 force가 구분 | Author explanation only | Torque trace 및 first-decoder-layer attention 시각화 | Rolling torque oscillation과 contact 시 force attention 증가. Attention만으로 독립적인 contact-state estimator 정확도를 증명하지 않음 | §V-C; PDF pp.8–9 ; Figs.8–9 |
| 확장된 unseen objects에서도 force-aware generalization | Controlled comparison | Vision-only / Bi-ACT / FACTR, 별도 확장 test set | Box35/120 vs68/120 vs105/120; pivot30/130 vs76/130 vs101/130; dough0/60 vs41/60 vs46/60. Original Tables VII–X와 별도 모집단 | Appendix XI; PDF p.14 ; Table VI |

## 13. Author-stated Limitations

External joint torque의 precision/noise가 미세한 force adjustment를 제한하고 해당 센서가 있는 follower를 가정한다. Curriculum operator/schedule은 task별 hyperparameter tuning에 영향을 받는다. [§VI, PDF p.9]

## 14. Author-stated Future Work

High-resolution tactile sensors 또는 haptic gloves, EEF F/T가 장착된 arm으로의 확장, adaptive/self-tuning curriculum을 제안한다. 현재 실험에서 tactile 또는 EEF F/T를 사용한 것으로 기록하지 않는다. [§VI, PDF p.9]

## 15. Review-relevant Findings

- Current RGB와 joint torque/current를 함께 사용하며 blind execution이 아니다.
- Policy hand proprioception은 포함하지만 current arm joint observation은 제외한다.
- Joint torque와 wrist F/T·Cartesian wrench·tactile taxel을 구분해야 한다.
- Force 사용 여부와 curriculum 사용 여부를 별도 baseline으로 비교한다.
- Original test table과 expanded test table, 본문 aggregate의 수치를 합치지 않는다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / Object information | §IV-A/V-A; Appendix X, PDF pp.4–6,13 |
| Tactile / F/T source | §III-A/V-A, PDF pp.3,6 |
| Controller | §III; Appendix IX, PDF pp.3–4,13 |
| Reward / Critic | 비-RL; BC loss Eq.(6), PDF p.4 |
| Ablation | Tables I–II, V–X, PDF pp.8–9,14–15 |
| Limitation / Future Work | §VI, PDF p.9 |
