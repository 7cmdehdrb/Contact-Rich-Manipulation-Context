# The Power of the Senses: Generalizable Manipulation from Vision and Touch through Masked Multimodal Learning

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B073`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Carmelo Sferrazza; Younggyo Seo; Hao Liu; Youngwoon Lee; Pieter Abbeel
- Year: 2024
- Venue: 2024 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)
- DOI / arXiv: 10.1109/IROS58592.2024.10802719 / Not stated
- PDF version: IEEE publisher version
- Page count: 8
- SHA-256: `9f364e8d29f6c23b2d19ca1329366e96f63f79c01c821a475cc797bc303ddd8c`
- PDF filename: Sferrazza 등 - 2024 - The Power of the Senses Generalizable Manipulation from Vision and Touch through Masked Multimodal.pdf
- 확인 범위: PDF pp.1–8 전체; task/reward/observation, Figures 2–7, Limitations/Future Work 렌더 확인. 원문이 가리키는 online appendix는 제공 PDF에 없어 확인 불가.

## 2. Relevance to This Review

`Relevant`

High-resolution tactile force maps와 vision을 joint masked-autoencoder representation으로 결합하고 modality/representation/history ablation을 수행한다. Object pose vector 없이 visual/tactile pixels로 조작하는 구조와 tactile이 vision의 occlusion/generalization 부족을 보완하는 근거를 제공한다.

## 3. Task

MuJoCo simulation에서 (1) varied-shape peg insertion, (2) locked-door handle turning/opening, (3) Shadow Hand cube in-hand reorientation을 수행한다. Generalization은 unseen peg shapes, randomized door pose/friction/damping, doubled cube mass/camera perturbation으로 평가한다. [§V–VI, pp.4–6]

## 4. Method

### 4.1. Overall Pipeline

4-frame RGB + distributed tactile force maps → modality별 early CNN → positional/modality embeddings → shared ViT masked-autoencoder encoder → multimodal embedding → transformer+pooling actor/critic heads(PPO); training은 tactile/pixel reconstruction loss와 PPO objective를 함께 optimize한다. [§IV/Fig.1, pp.3–4]

### 4.2. Observation

64×64 RGB image와 tactile maps를 4 frames channel-stack하여 actor와 critic에 공통 제공한다. Insertion/door는 fingertip 32×32×3 force maps, in-hand는 phalange/palm 3×3 maps를 padded 32×32로 사용한다. Explicit current object pose vector는 없다. [§III–V, pp.3–5; §VI-C p.6]

### 4.3. Action

Task별로 insertion floating gripper 3D position, door opening 3D delta EEF position+rotation, Shadow Hand 20D action을 출력한다. [§V-A–C, pp.4–5]

### 4.4. Controller

Learned PPO policy가 simulator control actions를 직접 출력한다. 별도 low-level controller/gains는 원문에서 task별로 명시되지 않음. [§IV-B/§V, pp.3–5]

### 4.5. Learning / Optimization Method

PPO와 multimodal MAE를 joint optimize한다. $L=L_{rep}+L_{PPO}$이며 reconstruction은 pixel/taxel MSE다. Actor와 critic은 같은 learned multimodal embeddings를 받고 별도 transformer/MLP head를 사용한다. [§III–IV, pp.2–3]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Current RGB image에 object position이 implicit하게 포함 | 매 simulator step 갱신 | Numeric current pose tracking input은 없다. Goal image/target geometry와 current state를 구분한다. [§IV–VI, PDF pp.3–6] |
| Orientation | 기타 | RGB/tactile pattern의 implicit orientation | 매 step 갱신 | In-hand target orientation overlay는 goal이고 current orientation vector는 actor에 주지 않는다. [§IV–VI, PDF pp.3–6] |
| Shape / Geometry | 기타 | RGB와 tactile spatial patterns의 implicit geometry | 매 frame 관측 | Peg shape identity/mesh/dimensions는 actor vector로 제공하지 않는다. [§V-A pp.4–5] |
| Physical Parameters | 미제공 | Mass/friction/damping parameter vector 없음 | 해당 없음 | Test에서 mass/friction을 바꾸지만 policy에 수치로 제공하지 않는다. [§V-B–C/§VI-B pp.4–5] |

## 6. Missing Object Information and Compensation

Explicit current object pose/shape/physical parameters 미제공 → camera image + distributed tactile force map + 4-frame history → object/contact state를 implicit representation으로 encode한다.

Vision occlusion과 delayed contact response → local tactile pressure/shear field → contact-rich correction을 제공한다. 반대로 touch만으로 부족한 global task geometry → vision → global reasoning을 제공한다. 저자 주장이 modality baselines와 generalization experiments로 비교된다. [§I–II pp.1–2; §VI pp.5–6]

## 7. Tactile

### 7.1. Raw Sensor

MuJoCo touch-grid plugin의 spatially distributed force maps. Insertion/door는 각 fingertip에 32×32 taxels, in-hand는 fingers/palm의 3×3 maps를 zero-pad해 32×32로 구성한다. [§III/§V, pp.3–5]

### 7.2. Preprocessing

각 taxel은 shear 2 components와 pressure 1 component의 3-channel map. Early CNN features, four-frame channel stacking, positional/modality embeddings, uniform multimodal masking, ViT MAE reconstruction을 적용한다. [§III–IV, p.3; §VI-C p.6]

### 7.3. Policy Representation

Shared ViT encoder의 joint visual–tactile embeddings. Policy inference에는 masking 없이 CNN/ViT를 통과한 multimodal tokens를 사용한다. [§IV-A–B, p.3]

### 7.4. Retained Information

Local force magnitude/pressure와 2D shear direction의 spatial distribution, vision과의 cross-modal relation, 4-frame temporal contact memory를 유지한다. [§III–IV/§VI-C, pp.3,6]

### 7.5. Removed / Unavailable Information

CNN/ViT latent는 raw taxel field를 압축하며 직접 해석 가능한 contact location/force vector나 whole-object pose를 출력하지 않는다. Force map은 simulator abstraction이며 real sensor 검증은 없다. [§IV–VII, pp.3–7]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

MuJoCo tactile touch-grid의 distributed contact forces. Wrist F/T가 아니다. [§III/§V, pp.3–5]

### 8.2. Representation

32×32×3 tactile force map: shear 2 channels + pressure 1 channel, 4-frame stacked latent. [§III–IV, p.3]

### 8.3. Role

Local contact feedback와 vision occlusion 보완; multimodal representation learning 및 PPO observation. [§I/§IV/§VI, pp.1,3,5–6]

### 8.4. Required Assumptions

Simulator touch grid가 real tactile force map에 대응하는 abstraction이라는 가정; tactile sensing coverage가 task contact를 포착해야 한다. [§III/VII, pp.3,7]

### 8.5. Reported Limitation / Ambiguity

Tactile는 non-contact 시 정보가 sparse한데도 항상 입력되어 learning을 느리게 할 수 있다. Paired vision-touch data가 부족하고 real-world transfer를 직접 검증하지 않았다. [§VII, pp.6–7]

## 9. Other Observations

Vision RGB는 global object/task scene과 goal cue를 제공한다. History는 4-frame channel stack이며 recurrent state/explicit estimator는 없다. Previous action과 proprioceptive joint/EEF vector의 포함 여부는 제공 PDF에서 명시되지 않는다. [§IV–V/§VI-C, pp.3–6]

## 10. Tactile–Other Modality Relationship

Vision은 global geometry와 contact 전 접근을, tactile은 occlusion 뒤 local pressure/shear를 제공한다. Shared attention/MAE가 두 modality의 relation을 학습한다. Vision-policy variant에서 touch를 encoder training에만 사용해도 vision-only보다 좋아 tactile의 training-time representation benefit을 보인다. Wrist F/T는 없다. [§I/VI, pp.1,5–6]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | RGB+tactile learned embeddings | Current object GT pose/parameters를 입력하지 않는다. [§IV-B, p.3] |
| Critic | No | Actor와 같은 multimodal embeddings | Asymmetric privileged critic은 명시되지 않음. [§IV-B, p.3] |
| Reward | Yes | Object position/orientation, door state 등 simulator task state | Dense/sparse rewards는 simulator state/goal distance로 계산한다. [§V-A–C, pp.4–5] |
| Termination | Yes | Insertion success, door opened/detached, orientation threshold | Simulator task outcome로 episode 성공/종료. [§V-A–C, pp.4–5] |
| Curriculum | Not stated | Not stated | Formal curriculum 사용은 확인되지 않음. [§VI, pp.5–6] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Joint vision-touch representation이 generalization 개선 | Representation ablation | M3L vs vision-only MAE, end-to-end, sequential; unseen objects/conditions | M3L이 세 task의 zero-shot generalization에서 baselines와 동등 이상이며 vision-only를 크게 상회한다. | §VI-B; PDF pp.5–6 ; Fig.5 |
| Touch는 training-only representation에도 기여 | Sensor/representation ablation | M3L vision-policy vs vision-only MAE | Touch를 encoder training에만 쓴 vision policy도 vision-only보다 상당히 향상되어 full M3L gap의 큰 부분을 줄인다. | §VI-B; PDF p.5 ; Fig.5 |
| Representation objective가 sample efficiency에 기여 | Controlled comparison | M3L/MAE variants vs same-encoder end-to-end PPO | Representation-learning methods가 대체로 end-to-end보다 sample-efficient하고 M3L은 세 task에서 best in-task performance를 일관되게 보인다. | §VI-C; PDF p.6 ; Fig.6 |
| History가 transient contact를 보존 | Representation ablation | 1 frame vs 4 stacked frames, tactile insertion | 4 frames가 약 90% success에 도달하고 1 frame은 약 55% 수준; 저자는 recent contact memory 역할로 해석한다. | §VI-C; PDF p.6 ; Fig.7 |

## 13. Author-stated Limitations

PPO의 off-policy 대비 높은 sample complexity와 difficult exploration 한계가 있다. Non-contact에서도 tactile를 항상 처리해 learning이 느려질 수 있다. Paired vision-touch datasets가 부족하며 결과는 simulation만 제시된다. [§VII, pp.6–7]

## 14. Author-stated Future Work

다른 RL algorithms와 결합하고 tactile gating을 도입하며, 대규모 image data와 적은 paired vision-touch data를 pretraining/finetuning으로 활용하는 방향을 제시한다. Real transfer는 visual domain randomization 등 가능한 경로로 논의하지만 본 논문에서 검증하지 않는다. [§VII, pp.6–7]

## 15. Review-relevant Findings

- Current object pose vector 없이 vision/tactile force maps의 learned latent를 사용한다.
- Tactile raw representation은 pressure와 shear가 분포된 high-resolution force map이다.
- Four-frame history가 한 시점 뒤 사라지는 contact 정보를 기억하는 데 중요하다.
- Actor/critic은 object GT를 받지 않지만 reward/termination은 simulator state를 사용한다.
- Touch를 representation training에만 사용해도 vision-only deployment가 개선됐다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / representation | §III–IV p.3 |
| Object info / tasks | §V pp.4–5 |
| Action / rewards | §V-A–C pp.4–5 |
| Actor / Critic | §IV-B p.3 |
| Tactile / force | §III/§V pp.3–5 |
| Ablation | Figs.5–7 pp.5–6 |
| Limitation / Future | §VII pp.6–7 |
| Appendix | Online appendix referenced but not included |
