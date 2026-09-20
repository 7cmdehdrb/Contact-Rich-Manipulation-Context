# ManiFeel: Benchmarking and Understanding Visuotactile Manipulation Policy Learning

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B052`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Quan Khanh Luu; Pokuang Zhou; Zhengtong Xu; Zhiyuan Zhang; Qiang Qiu; Yu She
- Year: 2026
- Venue: Not stated
- DOI / arXiv: Not stated / 2505.18472v2
- PDF version: arXiv v2, 12 January 2026
- Page count: 19
- SHA-256: `f9bbb98529baf333276c989b912a5f887a3ec4ba6156d6debd2601882664cc12`
- PDF filename: Luu 등 - 2026 - ManiFeel Benchmarking and Understanding Visuotactile Manipulation Policy Learning.pdf
- 확인 범위: PDF pp.1–19 전체(본문 pp.1–14, Appendices A–D pp.14–17, 참고문헌 pp.17–19); Figs.5/11 및 Tables II/IV를 렌더 확인. 별도 supplement는 확인하지 않음.

## 2. Relevance to This Review

`Relevant`

Vision-only, vision+TacRGB, vision+distributed tactile force field를 같은 proprioception·imitation-policy 조건에서 비교하여 tactile 정보의 과업별 역할과 추가 입력의 역효과를 직접 보여 준다. 다만 실행 중 vision을 계속 사용하며 tactile-only 조건은 없고, TacFF는 wrist 6축 F/T가 아니라 접촉면의 normal/shear grid다.

## 3. Task

ManiFeel은 insertion 4종, screwing 2종, exploration 3종의 simulation task와 gear assembly, bulb installation, ball sorting(normal/dim)의 real task를 이용해 supervised visuotactile policy를 비교한다. 일부 task는 occluded view 또는 dim light지만 모든 정책은 현재 vision과 proprioception을 받고, tactile은 vision에 추가된다. [§III-A pp.3–6; §IV pp.7–13; Appendix A pp.14–15]

## 4. Method

### 4.1. Overall Pipeline

현재·직전 vision, TacRGB 또는 TacFF, 7D EEF proprioception → modality별 encoder → latent concatenation → Diffusion Policy/Equivariant Diffusion Policy/Flow Matching → relative-pose action chunk → robot. Human demonstrations를 supervised imitation으로 학습하며 simulation과 real policy는 각 환경 데이터로 별도 학습한다. [§III-B/Fig.5 pp.6–7; §IV-D p.11; Appendices B–D pp.15–17]

### 4.2. Observation

세 configuration은 vision-only, vision+TacRGB, vision+TacFF이며 모두 7D EEF position+quaternion을 포함한다. 각 encoder는 현재와 직전 두 frame $(\cdot)_{t-1:t}$을 받는다. TacRGB와 TacFF를 동시에 쓰거나 tactile-only로 비교하지 않는다. 실험에는 task별 camera 1대와 right-finger tactile 1개만 사용하며, object-search의 agent view는 시각화 전용이다. [Eq.1–3/Fig.5 pp.6–7; Fig.4 p.6; Appendix D p.16]

### 4.3. Action

Policy가 relative-pose action chunk를 생성한다. Simulation task는 6D 또는 gripper를 포함한 7D이며, 일부 task는 roll/pitch 또는 roll/pitch/yaw를 고정한다. Real task는 position+yaw와 gripper에 해당하는 5D다. [Appendix B Table V p.15; Appendix D Tables VI–VII pp.16–17]

### 4.4. Controller

Simulation은 relative-pose control을 사용하지만 세부 low-level tracking controller는 미명시다. Real robot은 EEF position과 yaw를 조절하고 roll/pitch를 고정하는 OSC-yaw controller를 사용한다. [Appendix D, p.16]

### 4.5. Learning / Optimization Method

Human demonstrations를 이용한 supervised imitation이다. DP는 DDPM(sim) 또는 DDIM(real), EquiDP는 SO(2)-equivariant encoder와 DDIM, FM은 one-step flow field를 쓴다. 보상·critic은 없다. Simulation success는 3 seeds × 50 initializations × 마지막 10 epochs의 1500 evaluations 평균이며 real은 15 rollouts다. [§III-B/§IV pp.7–8; Appendix C–D pp.16–17]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | 현재 RGB scene의 latent로 암묵적으로 갱신; 수치 object position vector는 actor input으로 열거되지 않음 | 현재·직전 image frame마다 갱신 | Object-search에서는 내부 object가 camera에 가려져 tactile exploration으로 찾는다. Simulation GT randomization/evaluation state를 actor pose 입력으로 세지 않는다. [§III-A–B, PDF pp.4–7; Appendix A p.14] |
| Orientation | 기타 | 현재 RGB/TacRGB contact pattern으로 암묵적으로 관측; 명시적 object orientation vector 없음 | image/tactile frame마다 갱신 | Peg reorientation 초기 in-hand orientation은 randomize하지만 해당 simulator angle을 actor에 직접 제공한다고 명시하지 않는다. [§III-A–B, PDF pp.4–7; Appendix A p.14] |
| Shape / Geometry | 기타 | RGB 및 TacRGB deformation/texture 또는 TacFF contact field; explicit mesh/CAD/dimensions 없음 | 센서 영상은 갱신; task geometry 자체는 고정/학습됨 | Socket/object geometry의 명시적 수치 입력과 sensor feature를 구분한다. [§III-A–B, PDF pp.4–7] |
| Physical Parameters | 미제공 | Mass, friction, stiffness를 actor parameter로 제공한다는 명시 없음 | 해당 없음 | Normal/shear field가 접촉 결과를 반영하지만 물성 parameter 자체를 제공하지 않는다. [§III–IV, PDF pp.3–14] |

## 6. Missing Object Information and Compensation

명시적 current object pose·full shape·물성 parameter는 제공하지 않는다. Pre-contact/global localization은 계속 갱신되는 vision과 EEF pose가 담당하고, 접촉 후 local geometry/texture 또는 force distribution은 TacRGB/TacFF가 보완한다. Fully occluded object search에서는 tactile exploration으로 위치를 찾지만, benchmark 전체가 blind 또는 tactile-only인 것은 아니다. [§III-A–B pp.4–7; §IV-A pp.7–9]

## 7. Tactile

### 7.1. Raw Sensor

Simulation은 TacSL이 모사한 GelSight R1.5 기반 TacRGB와 TacFF를 제공한다. Real은 right-finger GelSight R1.5 한 개를 사용한다. Dataset은 simulation에서 두 tactile sensor를 기록하지만 본 실험 policy에는 right sensor 하나만 쓴다. [§III-A pp.4–5; §IV-D p.11; Appendix B/D pp.15–16]

### 7.2. Preprocessing

모든 modality를 $[-1,1]$로 normalize한다. TacRGB 원본은 simulation 240×320, real 160×240이고 ResNet18/UniT에는 256×256, T3/AnyTouch에는 224×224로 resize한다. TacFF는 10×14이며 current·previous 두 frame을 encoder에 넣는다. [§III-B p.6; Appendix D Table VII, p.17]

### 7.3. Policy Representation

TacRGB는 contact elastomer deformation의 3-channel image를 CNN/ViT latent로 축약한다. TacFF는 각 10×14 contact point의 normal 1축과 tangential shear 2축을 담은 3-channel spatial field이며 별도 encoder latent로 축약한다. 둘은 같은 policy에 함께 넣지 않는다. [§III-A–B, pp.4–7; Appendix D p.17]

### 7.4. Retained Information

TacRGB는 local surface texture·geometry·deformation을, TacFF는 distributed contact pressure와 directional shear를 유지한다. 두 표현의 task별 효용을 vision-only와 비교한다. [§III-A p.5; §IV-A pp.8–9]

### 7.5. Removed / Unavailable Information

Latent encoding은 raw spatial detail을 축약한다. TacRGB는 calibrated force를 직접 제공하지 않고 TacFF는 high-resolution appearance/texture를 보존하지 않는다. 어느 쪽도 global object pose/full shape가 아니며 binary contact 표현 실험은 없다. [§III-B pp.6–7; §IV-A/C pp.8–11]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

TacFF는 wrist 6-axis F/T가 아니라 fingertip contact-area force field다. Simulation은 TacSL에서 생성하고, real은 GelSight marker optical flow의 tangential displacement와 reconstructed depth의 normal indentation으로 추정한다. [§III-A pp.4–5; §IV-D p.11]

### 8.2. Representation

10×14×3 grid: 각 contact point의 normal 성분 1개와 2D shear 성분. $[-1,1]$ normalize 후 force-field encoder에 current·previous frame을 전달한다. Force 단위·calibration·net 6D wrench 변환은 미명시다. [Eq.1–3, PDF pp.6–7; Appendix D Table VII p.17]

### 8.3. Role

Contact alignment, stable contact, tightening/force regulation을 위한 policy observation이다. Table II에서 insertion/screwing에는 대체로 TacFF가 유리하지만 exploration의 texture/shape 판별에는 TacRGB가 더 유리하다. [§IV-A, PDF pp.7–9; Table II]

### 8.4. Required Assumptions

접촉이 right-finger sensing area에 들어오고 field estimate가 interaction을 충분히 반영해야 한다. Global approach/pre-contact localization은 vision에 의존하며, simulation TacSL과 real marker/depth reconstruction의 대응을 가정한다. [§III-A–B pp.4–7; §IV-D pp.11–13]

### 8.5. Reported Limitation / Ambiguity

Sensor force range, physical unit, calibration error, sampling rate와 6축 resultant wrench는 미명시다. 저자들은 simulated tactile fidelity, elastomer deformation·friction/contact dynamics 차이와 camera sensitivity가 sim-real absolute gap을 만든다고 밝힌다. [§V-B, PDF pp.13–14]

## 9. Other Observations

Vision은 실행 중 계속 갱신된다. Insertion/screwing은 wrist camera, exploration은 occluded front camera 또는 dim-light front camera를 사용한다. 모든 configuration은 7D EEF pose를 받고 current·previous frame의 짧은 history를 사용한다. Numerical object-state estimator, recurrent hidden state, previous action input은 명시되지 않는다. [§III-A–B pp.4–7; Appendix D p.16]

## 10. Tactile–Other Modality Relationship

Vision은 global scene/localization과 pre-contact alignment를, TacRGB는 texture·local deformation/geometry를, TacFF는 distributed normal/shear interaction을 제공한다. Table II/III의 controlled modality comparison은 역할이 task-dependent임을 보이고 TacRGB 추가가 gear/bulb에서 성능을 낮추는 경우도 확인한다. 그러나 tactile-only와 TacRGB+TacFF 결합은 시험하지 않아 vision 없는 실행 가능성이나 두 tactile channel의 상보성을 판정할 수 없다. [§III-B p.6; §IV-A–B pp.7–10]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No simulator object GT stated | Current/previous camera+tactile observations and 7D EEF pose | Simulation source라는 이유만으로 hidden object pose/shape를 actor input으로 세지 않는다. Real도 같은 sensor classes가 필요하다. [§III-B pp.6–7; Appendix D p.16] |
| Critic | Not applicable | Supervised imitation; critic 없음 | Actor–critic 또는 asymmetric critic이 아니다. [§III-B p.7; Appendix C p.16] |
| Supervised labels | Yes; demonstration actions | Future relative-pose/gripper action chunks | Training target이며 inference에는 정답 action이 없다. [§III-A/B pp.5–7; Appendix B/C pp.15–16] |
| Reward | Not applicable | Reward learning 없음; simulation task success는 evaluation metric | 평가용 simulator success를 policy observation/reward로 바꾸어 기록하지 않는다. [§IV p.7] |
| Termination | Not stated | Task success와 rollout completion을 평가하지만 policy termination rule은 상세 미명시 | Success metric의 정확한 GT criterion/horizon을 제공 PDF에서 확인할 수 없다. [§IV pp.7–13; Appendices A/D pp.14–17] |
| Curriculum | No curriculum stated | Randomized starts and task-specific demonstration sets | Environment randomization과 curriculum을 구분한다. [Appendix A/D pp.14–17] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Tactile modality의 task별 추가 효과 | Input/Sensor ablation | Vision-only vs Vision+TacRGB vs Vision+TacFF; 동일 DP·proprioception, 3 seeds | Peg insertion 0.14/0.21/0.40, object search 0.52/0.69/0.52, dim ball sorting 0.57/0.72/0.60. Gear는 TacRGB가 0.63→0.57로 저하해 추가 sensor가 항상 이득은 아니다. | §IV-A; PDF p.8 ; Table II ; Fig.6 |
| Real에서 modality trend 재현 | Controlled comparison | 각 sensing configuration을 real data로 별도 학습; task당 15 rollouts | Real gear 0.33/0.27/0.47, bulb 0.40/0.40/0.73, normal-light ball 0.33/0.80/0.33, dim ball 0.13/0.33/0.13 (Vision/TacRGB/TacFF). Direct sim-to-real policy transfer 결과는 아니다. | §IV-D; PDF p.12 ; Fig.11 |
| TacRGB encoder 선택의 성능 차이 | Representation ablation | ResNet18 scratch vs UniT/T3/AnyTouch; 3 simulation tasks, 3 seeds | Task별 최고는 gear UniT 0.61, object search T3 0.71, ball UniT 0.80. Table 값상 UniT/T3가 scratch를 일관되게 능가하지는 않아 본문의 “consistently outperform” 일반화는 지지되지 않는다. | §IV-C; PDF p.11 ; Table IV ; Fig.9 |
| Simulated/real tactile distribution similarity | Controlled comparison | TacRGB/TacFF의 ball/bulb/gear simulation vs real; ResNet-feature FID/KID | FID는 2.91–6.57, KID는 2.54–7.44×10^-2. Distribution metric이며 force calibration 또는 contact-dynamics 정확도를 직접 검증하지 않는다. | §III-A; PDF p.5 ; Table I ; Fig.2 |

## 13. Author-stated Limitations

저자들은 (1) tactile representation이 task 전반에 일관되게 일반화되지 않음, (2) vision과 tactile 한 종류만 pairwise로 쓰고 단순 concatenation fusion만 평가함, (3) policy/representation/real 비교가 대표 task subset에 제한됨, (4) simulated tactile fidelity·camera sensitivity·미모델 contact dynamics와 real setup 차이 때문에 absolute sim-real gap이 남는다고 밝힌다. Real policy는 simulation에서 직접 전이한 것이 아니다. [§V-B, PDF pp.13–14]

## 14. Author-stated Future Work

더 universal한 tactile representation과 Sparsh 등 추가 encoder 평가, TacRGB+TacFF 및 adaptive/task-aware cross-modal fusion, hierarchical fusion, 개선된 tactile sensor modeling, domain adaptation과 randomization을 제안한다. Code/dataset/log/checkpoint 공개도 예정형으로 서술하므로 제공 PDF만으로 실제 공개 완료를 확인하지 않는다. [Abstract/§I pp.1–2; §V-B/§VI pp.13–14]

## 15. Review-relevant Findings

- 실행 관측은 vision을 계속 포함하므로 occluded task가 있어도 blind policy benchmark로 해석하지 않는다.
- TacFF는 wrist F/T가 아니라 10×14×3 fingertip normal/shear field다.
- Force-like TacFF와 image-like TacRGB의 이점이 task에 따라 바뀌며, 추가 modality가 성능을 낮춘 사례도 있다.
- No-tactile 대비 비교는 강하지만 tactile-only 및 TacRGB+TacFF 결합 evidence는 없다.
- Table IV 수치는 pretrained encoder가 scratch를 항상 능가한다는 본문 표현과 일치하지 않는다.
- Real 정책은 real demonstrations로 새로 학습했으므로 zero-shot sim-to-real 성과가 아니다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / fusion | §III-B/Fig.5, PDF pp.6–7 |
| Object pose / task conditions | §III-A pp.3–6; Appendix A pp.14–15 |
| Tactile / TacFF source | §III-A pp.4–5; §IV-D p.11 |
| Action / controller | Appendices B/D, pp.15–17 |
| Sensor modality evidence | Table II/Fig.6, p.8; Fig.11, p.12 |
| Representation evidence | Table IV/Fig.9, p.11 |
| Privileged / labels | §III-B p.7; Appendices B–C pp.15–16 |
| Limitations / Future Work | §V-B/§VI, pp.13–14 |
