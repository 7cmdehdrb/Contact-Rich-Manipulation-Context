# 260918 첫 15개 PDF — Review 질문별 종합 비교

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [Master CSV](../tables/paper_comparison.csv) · [Excel workbook](../tables/paper_comparison.xlsx)

분석 범위는 `260918/`의 PDF를 파일명 알파벳순으로 정렬한 **첫 15개 파일**이다. 중복은 없으며, 고유 학술 논문 14편과 기술문서 1개로 구성된다. Relevant 5편·Partially Relevant 3편을 정독했고, PASS 7개(논문 6편·기술문서 1개)는 Manifest에만 남겼다. 아래 비교의 모집단은 포함된 **8편**이다. 나머지 91개 PDF, 검증용 `test_pdfs` 3편, 외부 코드·영상·별도 supplement는 이 종합의 근거 집합에 포함하지 않았다.

각 표의 링크는 이번에 새로 작성한 분석이며, 함께 적은 페이지는 실제 제공 PDF의 1-based 페이지 번호다. 원문 명시, 표현 구조에서 확인되는 사실, 저자 설명, 실험 결과를 구분한다. 이 표본은 알파벳순 일부이므로 연구 분야 전체의 분포나 문헌 부재를 추정하는 데 쓰지 않는다.

## 1. Object information은 언제, 어느 모듈에 제공되는가?

### 1.1. Current position / orientation

`Tracking`은 수치 current object pose가 실행 중 갱신되는 경우다. 영상 feature의 갱신은 별도로 `기타`에 기록한다. `Initial`에는 초기 기능 영역·grasp 단서도 포함되므로 full 6D object pose가 제공된다는 뜻은 아니다.

| 입력 조건 | 해당 근거 | 실제로 제공되는 것 | 이후 함께 쓰는 정보 |
| --- | --- | --- | --- |
| Tracking | [B015 Dadiotis](../papers/2025-dadiotis-dynamic-object-goal-pushing.md) §5·11; PDF p.3 Table I, p.4 §III-E | Actor에 object–EEF relative position 및 object rotation. 학습은 noise를 더한 sim state, 실물은 external motion capture | Robot proprioception, goal-relative 정보, previous action. Contact/질량/형상 등 추가 정보는 Critic에 별도 제공 |
| Initial: 부분적 위치·방향 | [B001 Agarwal](../papers/2023-agarwal-dexterous-functional-grasping.md) §5; PDF pp.3–4·15 | 초기 RGB-D affordance 중심과 mask 축에서 pre-grasp를 계산. Grasp Actor에는 current object pose가 없음 | 손 관절각, target EEF pose, GRU state, 별도 팔 궤적 |
| Position Initial / Orientation 미제공 | [B014 Cui](../papers/2026-cui-vi-tacman.md) §5–6; PDF pp.2–5 | 초기 holdable-region centroid와 RGB-D geometry로 grasp·coarse interaction direction을 정함. Grasp 방향을 current object orientation으로 세지 않음 | Tactile marker 위치 변화와 contact-preserving pose update |
| 미제공: 명시적 current object pose 없음 | [B007 Beltran-Hernandez](../papers/2020-beltran-hernandez-learning-force-control.md) §5; PDF p.3 §III-B | 주어지는 것은 goal EEF pose와 현재 EEF error/velocity. 이를 물체의 current pose로 집계하지 않음 | Wrist F/T, force controller, nominal goal-directed motion, 학습한 motion/gain 조절 |
| 미제공: workpiece pose 관측 없음 | [B013 Cramer](../papers/2025-cramer-cheq-safe-variable-impedance.md) §5; PDF pp.3–4 §3–4 | 7개 via-point로 만든 reference path와 EEF–path error. 이것은 known path이지 current workpiece pose가 아님 | EEF contact force, robot state, nominal controller, adaptive impedance |
| 기타: 연속 영상의 latent object state | [B008 Bergmann](../papers/2025-bergmann-precision-focused-pushing.md) §5; PDF pp.2–3 §IV-A–B | Current/goal binary **vision** image의 각 6D latent. 수치 object pose GT는 Actor에 없음 | EEF planar position, episode history를 압축한 GRU |
| 기타: 연속 RGB scene 관측 | [B011 Brouwer](../papers/2026-brouwer-gentle-object-retraction.md) §5; PDF p.3 §III-B | Eye-in-hand RGB를 계속 사용하지만 명시적 object pose estimator 출력은 없음 | TCP pose, tactile force image, joint-torque estimated wrench, suction acquisition, observation history |
| 기타: image-space anatomical landmark | [B012 Chen](../papers/2025-chen-ultradp-force-aware-scanning.md) §5; PDF pp.3–4 §III | Ultrasound에서 artery의 영상 내 x 위치를 추정. Neck/artery의 full 3D pose tracking은 아님. Probe pose는 robot EEF 정보 | RGB-D, ultrasound, probe pose, wrist wrench, receding-horizon history, force/impedance controller |

따라서 “Actor에 숫자 object pose가 없다”와 “실행 중 vision을 쓰지 않는다”는 서로 다른 조건이다. B008·B011·B012는 전자에 해당하는 부분이 있어도 지속적인 영상 피드백이 존재한다. B001·B014의 초기 vision 이후 접촉 실행 구조와 합쳐 하나의 blind 범주로 세지 않는다.

### 1.2. Shape / geometry

이 8편의 명시된 실행 Actor/정책 입력에서 물체 full mesh/CAD를 직접 받는 사례는 확인되지 않았다. 그러나 이것이 기하 정보나 기하 prior가 전혀 없다는 뜻은 아니다.

| 제공 수준 | 확인된 경로 | 해석의 한계 |
| --- | --- | --- |
| 제한적 초기 형상 | B001의 mask/local RGB-D geometry, B014의 point cloud·normal·movable/holdable mask | Full object mesh 입력과 구분. B014는 normal 입력의 유용성을 direction-error 비교로 검증함 |
| 제한적 실행 중 형상 단서 | B008의 silhouette latent, B011의 RGB scene, B012의 RGB-D/ultrasound | 영상 단서와 명시적인 dimensions/mesh/state-estimator 출력을 구분 |
| Known task geometry | B013의 reference path와 tool/surface 조건 | 표면 전체를 online reconstruction한 결과가 아님. Path가 고정이라고 `Tracking`으로 기록하지 않음 |
| Actor에 명시적 shape 미제공 | B007은 environment geometry를 가정하지 않는다고 설명; B015는 actor에 size/dynamics를 주지 않는다고 명시 | B007에도 goal EEF pose가 필요하고, B015의 Critic·reward·randomization은 shape/dimensions를 사용 |

근거: [B001](../papers/2023-agarwal-dexterous-functional-grasping.md) §5–6; [B007](../papers/2020-beltran-hernandez-learning-force-control.md) §4–6; [B008](../papers/2025-bergmann-precision-focused-pushing.md) §5–6; [B011](../papers/2026-brouwer-gentle-object-retraction.md) §5; [B012](../papers/2025-chen-ultradp-force-aware-scanning.md) §5; [B013](../papers/2025-cramer-cheq-safe-variable-impedance.md) §5·8; [B014](../papers/2026-cui-vi-tacman.md) §5·12; [B015](../papers/2025-dadiotis-dynamic-object-goal-pushing.md) §5·11. 각 노트는 실행 입력과 학습용 기하 정보를 따로 기록한다.

## 2. 축약 tactile은 무엇을 남기고 무엇과 결합되는가?

이번 포함 논문에서 tactile을 사용하는 것은 B011과 B014다. **영역별 0/1 접촉 tactile**을 입력으로 쓰고 그 축약 효과를 비교한 사례는 이 두 편에서 확인되지 않았다.

| Tactile 표현 | 남는 정보 | 함께 제공되는 입력 | 이 표본으로 확인되지 않는 것 |
| --- | --- | --- | --- |
| B011: 2×49 triaxial taxel → 두 array에 각 1개 zero padding → 20×5 RGB force image → ResNet-18 | Taxel별 공간 배열과 normal/shear 세 force 성분. 범위 매핑 후 색상값으로 표현 | 연속 RGB, TCP pose, joint-torque estimated wrench, binary suction acquisition, history | Region binary로 줄여도 성능이 유지되는지, force magnitude와 spatial pattern 각각의 독립 기여 |
| B014: GelSight-style marker 영상 → normal deformation threshold로 활성 marker 선택 → marker별 위치 변화 → point registration | 선택된 접촉 marker의 위치와 변형에 따른 상대 변화, contact configuration 변화 | 초기 RGB-D·surface normal·part mask·grasp·interaction direction | Threshold 이후 marker 좌표까지 버리고 binary bit만 남긴 controller의 성능 |

근거: [B011](../papers/2026-brouwer-gentle-object-retraction.md) §7·9–10, PDF p.3 Fig.3/§III-B; [B014](../papers/2026-cui-vi-tacman.md) §7·10, PDF p.5 §III-E.

B011의 suction pressure threshold는 **grasp acquisition bit**이며 distributed tactile의 binary 축약이 아니다. B014의 threshold는 **marker 선택**이며 controller representation 전체가 binary가 되는 것도 아니다. B008의 binary image는 optical vision, B001의 9D eigengrasp는 action 표현이므로 둘 다 binary tactile 사례에서 제외한다. 이 구분 없이 “축약 tactile + history” 사례 수를 집계하면 서로 다른 종류의 축약이 섞인다.

## 3. Object 정보가 없거나 충분하지 않을 때 무엇으로 보완하는가?

반복되는 것은 단일 대체 센서가 아니라 **초기 정보·로봇 상태·시간 정보·학습 조건의 조합**이다. 다음은 각 논문이 실제 사용하는 경로이며, 다른 태스크에도 동일하게 충분하다는 결론은 아니다.

| 부족한 정보 → 추가 정보 → 역할 | 근거의 종류와 범위 |
| --- | --- |
| B001: grasp 중 current object pose·joint velocity 미제공 → 관절각·target EEF pose·GRU → reactive grasp 및 dynamics 적응 | RNN/feed-forward controlled comparison은 있음. Hidden state가 속도를 포착한다는 설명 자체는 저자 해석이며 velocity 복원 오차 실험은 없음 (Table 1, PDF p.6) |
| B008: binary 영상에 mass/friction이 보이지 않음 → episode observation history/GRU → 과거 object motion을 이용해 pushing dynamics에 대응 | 저자가 보완 목적을 직접 설명하며 history 방식 비교가 있음. 실제 mass/friction 추정값을 출력하거나 정확도를 검증한 것은 아님 (§IV-B, p.3; §IX, pp.4–6) |
| B007: environment geometry 미지 → known goal EEF pose·F/T·EEF feedback → goal 쪽 nominal motion에 접촉 대응 및 gain 조절 | Force controller/action 비교. Object geometry reconstruction이나 F/T localization은 아님 (§III-B–C, pp.3–4) |
| B013: workpiece current pose 입력 없음 → predefined path·proprioception·force → path/force tracking과 compliant control | 알려진 경로를 포함한 조건에서의 VIC·hybrid RL 비교. 임의 물체·미지 surface에 대한 충분성 실험이 아님 (§3–5, pp.3–5) |
| B014: 시각 기반 초기 방향의 불확실성·이후 visual update 없음 → tactile marker feedback → contact 유지하며 진행 방향/pose update | Normal 및 direction model 비교는 있음. Tactile 제거 또는 binary 표현 비교는 없음 (§III-E–IV, pp.5–7) |
| B011: 일부 접촉의 시각적 occlusion → local tactile·net wrench·TCP/history → gentle retraction | Force modality 제거 비교가 있음. 현재 object pose를 복원하는 estimator는 아님 (§III–VI, pp.2–7) |
| B012: 개인별 anatomy와 접촉 상태 차이 → ultrasound·RGB-D·wrench·probe pose → artery centering과 접촉 하중 제어 | Policy input ablation이 있음. Probe pose를 환자/artery pose로 바꾸어 해석하지 않음 (§III–IV, pp.3–6) |
| B015: actor에 object size/dynamics 미제공 → current pose tracking·proprioception·previous action·training privilege/randomization | 실행 중 current pose는 계속 제공됨. Shape GT critic의 독립 기여를 제거 비교로 입증한 것은 아님 (Table I, p.3; §III-E, p.4) |

참조: [B001](../papers/2023-agarwal-dexterous-functional-grasping.md), [B007](../papers/2020-beltran-hernandez-learning-force-control.md), [B008](../papers/2025-bergmann-precision-focused-pushing.md), [B011](../papers/2026-brouwer-gentle-object-retraction.md), [B012](../papers/2025-chen-ultradp-force-aware-scanning.md), [B013](../papers/2025-cramer-cheq-safe-variable-impedance.md), [B014](../papers/2026-cui-vi-tacman.md), [B015](../papers/2025-dadiotis-dynamic-object-goal-pushing.md)의 §6·12. 특히 B008의 결과는 **시각 표현에 없는 물성 정보의 history 보완**에 한정된 Partially Relevant 근거이며 tactile 축약의 보완 효과를 직접 검증한 것은 아니다.

## 4. F/T 중심 접근은 어떤 조건에서 성립하는가?

이 표본에는 net wrench로 contact point/patch를 직접 복원하는 F/T-only localization 연구가 없다. F/T를 쓰는 제어 연구 역시 goal·robot state·path 또는 vision을 함께 사용한다. 따라서 이 결과들을 “F/T만 있으면 contact configuration을 알 수 있다”는 근거로 사용할 수 없다.

| 접근 | 실제 복원/제어 대상 | 추가 정보·조건 | Locality / multi-contact에 대해 말할 수 있는 범위 |
| --- | --- | --- | --- |
| B007 wrist F/T | Contact response와 trajectory/controller gain 조절 | Goal EEF pose, EEF error/velocity, robot IK, controller baseline/range | Contact location 추정 출력 없음. Net-wrench multi-contact ambiguity를 직접 분석하지 않음 |
| B013 F/T sensor의 3D force 입력 | Polishing force·velocity·path tracking | 7 via-point reference, robot kinematics/dynamics, nominal prior, tool/workpiece 조건. Material-removal 논리는 constant contact area 가정 | Contact patch를 온라인 추정하지 않음. 원문의 task 조건을 일반 contact localization 가정으로 바꾸지 않음 |
| B012 wrist 6D wrench | Normal force regulation 및 learned desired pose/wrench | Probe-frame 선택 행렬, 알려진 linear probe mapping, RGB-D/ultrasound, probe pose, hybrid controller | Artery 위치는 ultrasound 기반. F/T-only 위치 추정이 아님 |
| B011 joint-torque estimated wrench | TCP-frame net load, policy input, excessive net impulse 판정 | Dynamics compensation, robot sensor transform, 다른 입력을 유지한 diffusion policy | Multi-contact의 개별 contact magnitude를 net wrench가 알지 못한다고 저자가 명시함. Tactile도 arm 전체 coverage가 없다고 설명 |

근거: [B007](../papers/2020-beltran-hernandez-learning-force-control.md) §8, PDF pp.3–5; [B013](../papers/2025-cramer-cheq-safe-variable-impedance.md) §8, PDF pp.3–4; [B012](../papers/2025-chen-ultradp-force-aware-scanning.md) §8, PDF p.4 Eq.(8)–(10); [B011](../papers/2026-brouwer-gentle-object-retraction.md) §8, PDF pp.3–4. B011의 moment가 suction cup에서 작다는 설명은 policy가 torque 성분을 버렸다는 명시가 아니다. Force 검출 한계와 실제 policy wrench representation을 분리한다.

Single-contact·known normal·known friction 같은 가정은 각 연구가 사용한다고 명시한 경우에만 기록한다. 본 표본에 localization 연구가 없다는 이유로 그러한 가정이 불필요하다고 결론 내리지 않는다.

## 5. F/T + tactile에서 실제 역할 분담은 검증되었는가?

직접적인 sensor combination 비교는 [B011 Brouwer](../papers/2026-brouwer-gentle-object-retraction.md)에서 확인된다. 다만 그 “wrench”는 **joint-torque estimated wrench**이므로 wrist 6-axis F/T 결과로 그대로 옮기지 않는다. 네 정책은 RGB·TCP pose·suction acquisition 등의 입력을 공통으로 유지하고 tactile/wrench 접근만 바꾼다. `wrench-informed`는 wrench 단독 전체 관측 정책을 뜻하지 않는다 (§V-A, PDF p.5).

| 역할 | 원문이 제시한 내용 | 근거의 강도 |
| --- | --- | --- |
| Wrench | Net load를 감지하고 국소 tactile coverage 밖 접촉에도 반응할 수 있음 | §IV-B의 설계 설명; Fig.7의 force-response 관찰 |
| Tactile | Taxel별 국소 triaxial force와 peak force를 직접 측정해 net wrench에 가려지는 국소 하중을 관측 | §III-B·IV-B의 representation/측정·설계 설명. Contact별 force 분해나 contact-location 정확도 실험은 없음 |
| 결합 | 두 센서를 갖는 정책의 task success 및 timeout 행동 비교 | 실제 sensor combination ablation. Spatial 정보와 force 크기를 따로 제거한 비교는 없음 |

Fig.6(PDF p.6)의 40회/정책 결과는 다음과 같다.

| Policy | 성공 | Timeout 실패 | Excessive-force 실패 |
| --- | --- | --- | --- |
| Baseline | 15/40 (37.5%) | 10/40 | 15/40 |
| Wrench-informed | 24/40 (60%) | 9/40 | 7/40 |
| Tactile-informed | 24/40 (60%) | 9/40 | 7/40 |
| Wrench + tactile | 27/40 (67.5%) | 2/40 | 11/40 |

그림의 유의성 표시는 각 force-informed 정책의 **baseline 대비 성공률**과 combined 대비 다른 정책들의 **timeout 비율**에 붙어 있다. Combined가 두 단독 정책보다 성공률에서 유의하게 우수하다는 표시는 없다. Baseline 대비 “80% 향상”은 37.5%→67.5%의 상대 향상이며 80%p 증가가 아니다. Combined의 excessive-force 실패 수 11은 단독 정책의 7보다 많고, 저자는 이 차이가 유의하지 않다고 설명한다 (§VI, PDF p.7).

또한 큰 힘에 대한 무반응 건수는 baseline 412, wrench 17, tactile 72, combined 22다. 따라서 모든 측정 지표에서 결합이 가장 좋다고 요약할 수 없다. Causal confusion 감소 설명은 저자의 해석이며 별도 인과 검증 결과와 구분한다 (Fig.7·§V-B–VI, PDF pp.6–7).

영역별 binary로 줄였을 때 남을 후보는 “어느 센서 영역에서 접촉이 감지되는가”라는 공간 패턴이다. 그러나 B011의 정책은 실제로 force magnitude와 shear를 포함한 triaxial 영상을 사용한다. **이 문장은 현재 연구 관점의 표현 구조 해석이며 해당 논문의 직접 검증 결과는 아니다.** 본 표본은 region binary + wrist F/T의 성능을 검증하지 않았다.

## 6. Training-time privileged information은 실행 입력과 어떻게 다른가?

| 연구 | Actor | Critic | Reward | Termination / data generation |
| --- | --- | --- | --- | --- |
| B001 | Object GT 미제공; 손 관절각·target EEF pose·GRU | 입력/GT 미명시 | Sim object 높이·hand–object 거리 | Sim hand–object 거리로 종료; procedural hammer/물성 randomization. 실물 온라인 종료 구현은 미명시 |
| B007 | F/T·EEF pose error·velocity | 별도 privileged state 명시 없음; 미명시 항목을 No로 확정하지 않음 | Goal error·contact/안전 관련 항목; 센서 기반 구성과 simulator 값을 구분 | Goal 도달·force/safety 조건. 독립적인 hidden object GT 필요가 입증된 구조는 아님 |
| B008 | Binary vision latent·EEF position·GRU; numeric object-position GT 미제공 | Actor와 같은 관측 계열, 별도 GRU | GT object/goal position으로 거리 reward | Episode는 고정 50 steps이며 GT success가 조기 종료 조건이 아님. HER relabeling과 물성 sampling에는 simulator 정보 사용 |
| B013 | Robot state·3D contact force·path error | State/action/λ 기반 Q ensemble; adaptive mixing을 위해 실행 중에도 사용 | Path·velocity·force error | Constraint violation truncation과 path 완료. Sim/실물 sensor 값과 reference path를 구분 |
| B015 | **학습 시 noisy object pose GT 포함**; 실물 motion capture로 대응 | Noiseless actor 정보 + contact, CoM, mass, dimensions, inertia, velocity, shape | Object/goal bounding-box keypoint, object velocity, reach target | CaT의 학습상 reward termination, timeout/fall reset, 실물 success stop을 구분. Reset/domain randomization도 simulator geometry/물성 사용 |

근거: [B001](../papers/2023-agarwal-dexterous-functional-grasping.md) §11, PDF pp.5·15; [B007](../papers/2020-beltran-hernandez-learning-force-control.md) §11, PDF pp.3–6; [B008](../papers/2025-bergmann-precision-focused-pushing.md) §11, PDF pp.3–4·6; [B013](../papers/2025-cramer-cheq-safe-variable-impedance.md) §11, PDF pp.3–4; [B015](../papers/2025-dadiotis-dynamic-object-goal-pushing.md) §11, PDF pp.3–4 Tables I–II.

B011·B012·B014는 비-RL이므로 Actor/Critic/Reward 표의 RL 항목은 해당 없음이다. 그렇다고 학습 supervision이 없는 것은 아니다. B011은 multimodal demonstration, B012는 expert demonstrations와 artery landmark labels, B014는 simulation geometry/part annotation/displacement supervision을 사용한다. 이들 supervision을 실행 Actor의 object GT 관측으로 집계하지 않는다 ([B011](../papers/2026-brouwer-gentle-object-retraction.md)·[B012](../papers/2025-chen-ultradp-force-aware-scanning.md)·[B014](../papers/2026-cui-vi-tacman.md) §4·11).

이 표본만으로도 “실행 시 object GT가 없다”와 “학습 과정에서 GT를 쓰지 않는다”는 동치가 아님을 확인할 수 있다. 특히 B015는 asymmetric critic이 있다고 해서 Actor가 pose를 받지 않는 사례로 분류하면 안 된다.

## 7. 추가 정보의 유용성은 무엇으로 뒷받침되는가?

| 근거 유형 | 이 표본의 사례 | 허용되는 결론과 제한 |
| --- | --- | --- |
| Sensor combination ablation | B011: baseline / wrench / tactile / both, Fig.6–7, PDF pp.5–6 | 해당 task·demonstration 분포에서 force modalities의 효과. Binary tactile나 wrist F/T 조합의 검증은 아님 |
| Input ablation | B012: wrench·probe pose 등 policy input 비교, §IV, PDF pp.5–6 | Wrench policy input의 유용성. 입력을 제거해도 저수준 force controller는 남으므로 force sensing 전체 제거 결과가 아님 |
| Controlled comparison: history | B001 recurrent vs feed-forward(Table 1, p.6); B008 memory 방식/물성 sampling 비교(§IX, pp.4–6) | Recurrence 효과를 비교할 수 있음. 특정 물성·velocity가 정확히 식별되었다는 직접 검증과는 다름 |
| Input/model ablation: geometry feature | B014 normal 유무 및 direction 모델 비교(Table II/Fig.7, pp.5–6) | Normal 입력이 direction estimation에 주는 이득. Tactile 필요성/축약 성능의 ablation은 아님 |
| Controller / optimization comparison | B007 controller·action parameter 설정, B013 fixed/variable impedance와 CHEQ/SAC 비교 | 해당 controller 설계의 효과. Force 센서의 독립적 필요성을 제거 비교로 보인 것은 아님 |
| Constraint / sampling ablation | B015 balance constraint와 surface reach target 비교(§IV-A, Table III, pp.4–5) | 해당 training 설계의 효과. Critic privileged state의 독립 기여는 직접 검증하지 않음 |
| Failure analysis / author explanation | B001 large pre-grasp error; B008 simple-shape·observability 한계; B011 timeout/force response | 보고된 실패와 저자 설명을 조건부 근거로 사용. 새로운 modality가 그 실패를 해결한다고 임의 연결하지 않음 |

각 행의 상세 비교 조건·수치·source location은 해당 [Master](../tables/paper_comparison.csv)의 `evidence_*`와 Excel `Evidence` 시트, 논문 노트 §12에 대응한다. 임의 evidence score는 부여하지 않았다. B008 실물 성공은 GT 위치 계측 없이 육안 판정했으므로 simulation의 1 cm 성공 조건을 실물에서 동일하게 계측 검증했다고 쓰지 않는다 ([B008](../papers/2025-bergmann-precision-focused-pushing.md) §12–13, PDF p.6 §IX-B).

## 8. 현재 표본만으로 충분히 뒷받침되지 않는 주장

1. **영역별 binary tactile + wrist 6-axis F/T가 다른 관측 조합보다 우수하다.** 이번 8편에는 이 표현·센서 조합의 직접 비교가 없다. 가장 가까운 B011도 triaxial tactile image + joint-torque estimated wrench다.
2. **연속 tactile을 binary로 축약해도 필요한 정보가 보존된다.** B011은 magnitude/shear를 포함하며 B014는 marker 위치 변화를 쓴다. 둘 다 binary-only 대조군을 제공하지 않는다.
3. **F/T만으로 일반적인 multi-contact 위치·patch·configuration을 복원할 수 있다.** 이번 표본에는 이를 검증한 localization 논문이 없고, B011은 net wrench의 개별 contact magnitude 한계를 명시한다.
4. **History 또는 proprioception이 current object pose의 부족을 항상 대체한다.** B001은 초기 affordance 및 grasp prior가 있고 큰 pre-grasp 오류에 실패한다. B008은 vision을 계속 사용하며, B015는 current pose tracking을 유지한다.
5. **Actor가 센서 입력만 쓰면 학습에서도 GT가 필요 없다.** B001·B008의 reward, B015의 actor/critic/reward/data generation을 분리하면 성립하지 않는다. 반대로 어떤 GT가 반드시 필요한지는 해당 GT 제거 비교 없이는 단정할 수 없다.
6. **Tactile과 wrench의 국소/전역 역할이 독립적으로 완전히 분리·검증됐다.** B011은 sensor combination을 비교하지만 spatial pattern·force magnitude·coverage 각각을 별도 조작한 실험은 없다. Task 성공 차이와 정보 역할의 인과 식별을 구분해야 한다.
7. **Force 센서 제거 ablation과 policy force-input 제거 ablation은 같다.** B012의 controller force feedback은 별도로 남는다. B007·B013도 controller/gain 비교를 sensor necessity 비교로 바꿀 수 없다.

미확인 항목도 비교의 일부다. B001의 Critic 입력과 observation 차원 불일치, 일부 F/T 장착·처리 세부, B014가 다른 논문으로 넘긴 tactile controller의 세부, 비공개 코드·외부 supplement의 구현은 이번 PDF만으로 채우지 않았다. 구체적 미명시는 각 논문 §1·4·8·11·16과 [Batch 안내](../README.md)에 기록했다. 이 종합은 프로젝트의 확정 사양을 변경하지 않는다.
