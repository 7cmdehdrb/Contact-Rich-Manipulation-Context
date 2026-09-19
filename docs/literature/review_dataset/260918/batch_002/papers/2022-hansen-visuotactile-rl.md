# Visuotactile-RL: Learning Multimodal Manipulation Policies with Deep Reinforcement Learning

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B025
- Authors: Johanna Hansen; Francois Hogan; Dmitriy Rivkin; David Meger; Michael Jenkin; Gregory Dudek
- Year: 2022
- Venue: IEEE ICRA 2022, pp.8298–8304
- DOI / arXiv: 10.1109/ICRA46639.2022.9812019 / 미명시
- PDF version: IEEE publisher version
- Page count: 7
- SHA-256: `158c8174d4647386453f85cd6eb790d810331502b747cd06e078b538f95b270a`
- PDF filename: `Hansen 등 - 2022 - Visuotactile-RL Learning Multimodal Manipulation Policies with Deep Reinforcement Learning.pdf`
- 분석 근거: 선택 PDF 원문을 새로 읽었다. 기존 논문 상세 노트를 근거로 사용하지 않았다. 본문 pp.1–6을 읽고 핵심 Table I를 렌더 확인했다. p.7은 참고문헌; 관련 appendix 없음.

## 2. Relevance to This Review

**Relevant**. 시각·촉각·proprioception 조합과 tactile gate/augmentation을 비교하여 각 modality가 어떤 조건에서 유용한지 조사한다. Binary contact gate는 존재하지만 촉각 자체는 연속 depth image여서 축약 촉각과 혼동하지 않아야 한다. 시각 교란 및 물성 변화 실험이 추가 센서 역할의 근거를 제공한다.

## 3. Task

Simulation에서 TactileReach(시각에 안 보이는 목표 texture를 palm으로 정확히 접촉), Door(articulated handle을 돌려 문 열기), TactileLift(접촉 마찰이 낮은 돌기가 있는 box grasp/lift)를 수행한다. 물체 위치와 일부 geometry/physics를 episode별 변경한다. 성능 표는 누적 evaluation reward이며 success percentage가 아니다. (§V-A, p.5; Table I, p.6)

## 4. Method

### 4.1. Overall Pipeline

Current RGB, tactile depth와 joint position/velocity → modality별 encoder(MultiPath) → fused state → DrQv2 actor/Q → EEF pose action → OSC. Contact depth 기반 hard gate는 무접촉에서 tactile feedback/gradient 흐름을 차단한다. (Fig.1 p.1; §IV–VI pp.4–6)

### 4.2. Observation

Camera-proprio, camera-tactile-proprio, tactile-proprio 세 조합을 비교한다. Proprio는 joint position/velocity, pixel input은3frame history이다. RGB9×84×84, palm tactile3×84×84, dual gripper tactile6×84×84. Explicit object pose/shape GT vector는 없다. (§V-A/VI.1, pp.5–6)

### 4.3. Action

EEF pose를 통해 제어한다. 정확한 action component별 scaling 및 gripper action encoding은 원문에서 미명시이다. (§V, p.4)

### 4.4. Controller

Simulated Panda의 Operational Space Controller,20Hz. TactileReach/Door는 palm, TactileLift는 두 tactile sensor를 장착한 parallel-jaw gripper이다. Hardware 검증은 보고하지 않는다. (§V, pp.4–5)

### 4.5. Learning / Optimization Method

DrQv2(DDPG 기반 n-step critic target·decaying exploration)와 MP/SP encoder, tactile gate, random shift tactile augmentation, camera dropout/domain randomization을 비교한다. DrTD3 baseline도 포함한다. Online TD learning이며 policy와 Q는 encoder core를 공유하고 Q에 action을 추가한다. (§III/VI, pp.3/6; Fig.1)

## 5. Object Information

실행 입력과 학습·평가용 정답을 구분한다.

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | RGB implicit scene observation; tactile-proprio baseline은 visual channel 없음 | RGB 사용 조건에서 매step | 명시적 current object position vector 미제공 |
| Orientation | 기타 | RGB·contact image implicit cues | image history 갱신 | Object orientation estimator 없음 |
| Shape / Geometry | 기타 | RGB 및 contact-depth geometry; task별 제한된 물체/texture prior | 매step image; box protrusions는episode별random | Explicit mesh/CAD policy input은 없음 |
| Physical Parameters | 미제공 | Weight/friction 등 domain randomization | 정답 parameter actor입력 없음 | 물성 변화는 evaluation/training 환경 설정 |

## 6. Missing Object Information and Compensation

촉각은 접촉 때만 존재하고 전체 물체 접근 정보를 주지 못함 → RGB + joint state → 물체로 접근하고 접촉을 형성한다.

시각에서 보이지 않는 texture/접촉 변화 또는 시각·물성 교란 → tactile depth + proprioception +3frame history → contact-rich 조작과 교란 대응을 돕는다. Sensor combination 비교는 존재하지만 모든 입력의 개별 필요성을 증명한 것은 아니다. (§I/IV–VI, pp.1/4–6)

## 7. Tactile

### 7.1. Raw Sensor

Simulation optical-tactile 대응 geometric contact rendering. Palm1개 또는 gripper fingertip2개. 실제 특정 GelSight/DIGIT 제품을 장착한 hardware 실험은 아님. (§V, pp.4–5)

### 7.2. Preprocessing

Fingertip perspective depth를 silicone membrane half-width에 해당하는 threshold로 clipping해 contact imprint를 만든다.3frame stack, CNN encoder, random shift augmentation을 사용한다. 별도로 depth 기반 contact hard gate를 둔다. (§IV-A/V/VI.1, pp.4–6)

### 7.3. Policy Representation

연속 contact-depth image latent. Hard gate가 binary인 것이지 image를 contact/no-contact scalar로 바꾼 것은 아니다. MP는 vision/tactile별 encoder, SP는 channel concatenation이다.

### 7.4. Retained Information

Contact location, local shape/depth pattern, temporal image 변화가 representation에 남는다. Normal/shear force를 calibration해 읽는 출력은 명시하지 않는다.

### 7.5. Removed / Unavailable Information

Clipped contact rendering에는 sensor 밖 geometry가 없으며 CNN latent가 정확히 어떤 성분을 잃는지는 판단 불가. 정량 force/shear를 직접 제공한다는 근거 없음. Random image shift는 tactile relative position을 바꾸므로 원래 state를 보존하지 않는다고 저자가 지적한다. (§III-A, p.3)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

별도 force/F/T/wrench 입력 사용하지 않음.

### 8.2. Representation

해당 없음.

### 8.3. Role

해당 없음.

### 8.4. Required Assumptions

해당 없음.

### 8.5. Reported Limitation / Ambiguity

F/T 한계는 분석하지 않음.

## 9. Other Observations

Proprioception은 joint position/velocity이다. RGB는 reaching과 전역 장면 정보를 제공한다. History는3frame stack이며 recurrent hidden state 사용은 미명시이다. Previous-action input 및 object state estimator는 명시하지 않는다. Target texture를 독립 goal input으로 encoding하는 방법도 미명시이다.

## 10. Tactile–Other Modality Relationship

센서 비교 세 조건 모두 proprioception을 유지한다. Vision은 접촉 전 접근에 유용하고 tactile은 시각에서 보이지 않는 접촉 texture 및 접촉 중 cue를 제공한다. Camera dropout/gating은 모델이 tactile을 활용하게 하는 학습 기법이다. F/T와 tactile의 global/local 역할 비교는 수행하지 않는다.

## 11. Training-only / Privileged Information

Actor·Critic·reward·termination·학습 데이터 생성을 따로 기록한다.

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | No explicit privileged state | RGB/tactile pixels와 joint state | Simulation GT object pose를 actor vector에 넣었다는 근거 없음 (Fig.1; §V-A/VI.1, pp.1/5–6) |
| Critic | No separate privileged input reported | 공유 visual/tactile/proprio encoder + action | Q/targetQ의 별도 asymmetric GT 입력은 명시하지 않음 (Fig.1 p.1; §III p.3) |
| Reward | 부분 명시 | TactileReach precise target-texture contact와 Robosuite Reach reward; Door/Lift 기준은 benchmark 참조 | Simulator task state 기반 성공/진척 기준은 확인되나 세부 GT 항목/식은 미명시 (§V-A, p.5) |
| Termination | 미명시 | Contact/door/lift 성공 조건은 기술; termination 구현 및 GT channel 미명시 | 성공 정의를 곧 episode 종료 구현으로 단정하지 않음 (§V-A, p.5) |
| Curriculum | Yes: environment generation | Random object/frame poses, protrusions, friction/weight/light/camera; contact depth rendering | Domain randomization은 training환경 조작이며 actor physicsGT입력과 다름 (§V–VI, pp.4–6) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Modality 조합의 task별 차이 | Sensor combination ablation | Vision-proprio / visuotactile-proprio / tactile-proprio MP-DrQv2 | 5seeds training evaluation reward: Reach107±9/160±79/74±45; Door340±51/369±3/210±140; Lift146±38/167±72/44±10. 성공률이 아님. | §VI; PDF p.6 ; Table I |
| Tactile gate가 tactile-critical 학습을 도움 | Representation ablation | 기본MP vs tactile gate | Reach reward160±79 vs236±126; learning speed 향상. Door training은369±3 vs277±127로 모든 과업에서 우수하지 않음. | §VI.2; PDF pp.5–6 ; Table I ; Fig.5 |
| Tactile augmentation 효과 | Representation ablation | 기본MP vs no tactile augmentation | Reach160±79 vs109±3; Door369±3 vs227±155; Lift167±72 vs167±54. 저자는 대부분 과업에 도움이라 정리. | §VI.4; PDF p.6 ; Table I |
| 시각·물성 변화 대응 | Controlled comparison | DR Visual/Dynamics evaluation, sensor combinations와 training strategies | Table I의 best-seed10episodes 평가와5seed train평가를 구별해야 함. 특정 gate/visual-degradation 기법이 모든 조건에서 최고인 것은 아님. | §V–VI; PDF pp.5–6 ; Table I ; Fig.6–7 |

## 13. Author-stated Limitations

Tactile은 간헐적이고 학습 초기에 드물어 multimodal 모델이 vision에 과도하게 의존할 수 있다고 지적한다. Tactile image shift는 원래 contact relative state를 보존하지 않는다. Visual degradation은 tactile 활용을 늘려도 전체 성능을 낮출 수 있고 tactile gating 이득은 task에 따라 다르다. (§III-A/IV/VI, pp.3–6)

## 14. Author-stated Future Work

Tactile signal 존재에 따라 조건부 camera degradation을 적용하는 방향을 추가 연구 대상으로 명시한다. 장기 목표는 multimodal contact-rich manipulation control이다. (§II p.2; §VI.3 p.6)

## 15. Review-relevant Findings

- Contact gate는 binary지만 tactile representation은 고해상도 연속 depth image이다.
- 세 modality 조합 모두 joint position/velocity를 사용한다.
-3frame history를 사용하고 object pose GT vector는 명시하지 않는다.
- 결과는 simulation reward이며 hardware success rate가 아니다.
- Tactile/vision 조합 ablation은 있으나 F/T 병용은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / Object pose | Fig.1 p.1; §V-A/VI.1 pp.5–6 |
| Tactile | §IV-A/V pp.4–5; §VI.1 p.6 |
| F/T | 미사용; §V-A p.5 |
| Reward / Termination | §V-A p.5; termination 미명시 |
| Critic | Fig.1 p.1; §III p.3 |
| Ablation | Table I p.6; Fig.5–7 p.5 |
| Limitation / Future | §III–IV pp.3–4; §VI p.6 |
