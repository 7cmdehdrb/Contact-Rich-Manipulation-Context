# IROS 2023–2025 Tactile·F/T 기반 Reinforcement Learning 관련 논문 제목 선별

- **조사 기준일:** 2026년 9월 15일
- **자료 범위:** 제공된 IROS 2023·2024·2025 논문 제목 CSV 전체
- **1차 선별 당시 상태:** 제목 기반 1차 선별 완료. 초록·본문 검증 미수행
- **용도:** 원문 정독 우선순위를 정하기 위한 후보군이며, 실제 센서 구성·학습 방식·성과를 확정하지 않음

**후속 갱신 — 2026-09-16:** 사용자가 관련 논문 5편을 임시 선정했다. 선정 목록·서지·원문 정독 상태는 [§11](#11-사용자-임시-선정-및-후속-원문-정독--2026-09-16-추가)에 별도 기록한다. 1–10절은 2026-09-15 제목 기반 조사 기록이다.

[조사 그룹](README.md) · [전체 논문](../papers/README.md)

**후속 정독 바로가기**

| 선정 ID | 논문 | 상세노트 상태 |
| --- | --- | --- |
| [IROS-S01](#iros-s01) | Attention for Robot Touch | [상세노트](../papers/2023-lin-attention-for-robot-touch.md) · 완료 |
| [IROS-S02](#iros-s02) | Disambiguate Gripper State in Grasp-Based Tasks: Pseudo-Tactile as Feedback | [상세노트](../papers/2025-yang-pseudo-tactile-gripper-state.md) · 완료 |
| [IROS-S03](#iros-s03) | Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention | [상세노트](../papers/2025-dengler-location-based-attention-pushing.md) · 완료 |
| [IROS-S04](#iros-s04) | Multi-Fingered Dragging of Unknown Objects and Orientations Using Distributed Tactile Information Through Vision-Transformer and LSTM | 미작성 — 후속 정독용 원문 미제공 |
| [IROS-S05](#iros-s05) | Tactile Active Inference Reinforcement Learning | [상세노트](../papers/2024-liu-tactile-active-inference-rl.md) · 완료 |

## 1. 결론

제공된 CSV에 수록된 제목 레코드 **4,762건**을 대상으로, 초기 시각 관측 이후 손목 F/T와 손의 촉각 피드백으로 수행하는 Blind Sweeping 연구에 연결될 가능성이 있는 제목을 선별했다. 완전히 같은 제목 1건을 제외한 고유 제목은 4,761개이며, 최종 후보는 **31편**이다.

| 연도 | CSV 레코드 | 고유 제목 | 엄격 일치 | 원문 확인 후보 | 후보 합계 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2023 | 1,196 | 1,195 | 1 | 8 | 9 |
| 2024 | 1,581 | 1,581 | 1 | 9 | 10 |
| 2025 | 1,985 | 1,985 | 0 | 12 | 12 |
| **합계** | **4,762** | **4,761** | **2** | **29** | **31** |

제목에 tactile 또는 force 계열 표현과 `reinforcement learning`이 모두 직접 나타나면서 프로젝트의 제외 범위에도 해당하지 않는 **엄격한 문자상 교집합**은 2023년과 2024년에 각각 1편이다. 2025년에는 엄격 일치가 없다. 다만 센서 단서와 manipulation 또는 policy·learning 표현이 함께 나타나는 제목 4편을 최우선 원문 확인 후보로 분리했다. 이 네 편의 RL 사용 여부는 원문을 확인해야 한다.

세 연도의 제목에서 읽히는 변화는 다음과 같다.

- 2023년 후보군에서는 DQN, curriculum RL, non-prehensile manipulation, contact 전후 policy 분해처럼 **과업과 RL 구조를 직접 결합한 제목**이 확인된다.
- 2024년 후보군에서는 tactile policy의 zero-shot transfer, tactile skin의 sim-to-real, distributed tactile과 sequence model, diffusion contact model처럼 **촉각 표현·전이·학습 제어를 연결한 제목**이 나타난다.
- 2025년 후보군에서는 visuo-tactile fusion, pseudo-tactile feedback, force-aware diffusion policy, compliance와 RL의 결합처럼 **멀티모달 피드백과 policy architecture를 함께 언급한 제목**이 확인된다.
- 제공된 제목만으로는 **별도의 손목 F/T와 손 촉각을 동시에 actor 관측으로 사용하여 Blind pushing 또는 sweeping을 학습하는 논문**을 확인할 수 없다. 이는 해당 연구가 없다는 뜻이 아니라, 제목만으로 직접 식별하지 못했다는 뜻이다.

이 비교는 선별된 제목의 내용 차이를 정리한 것이며, 연도별 후보 수나 특정 방법의 정량적 증가를 뜻하지 않는다.

## 2. 자료와 선별 방법

입력 자료는 다음 세 파일이다.

- `IROS_2023_papers(1).csv`: 1,196개 레코드, 고유 제목 1,195개
- `IROS_2024_papers(1).csv`: 1,581개 레코드, 고유 제목 1,581개
- `IROS_2025_papers(1).csv`: 1,985개 레코드, 고유 제목 1,985개

2023년 CSV의 `Sensor Selection for Fine-Grained Behavior Verification that Respects Privacy.`가 914번과 1061번에 중복되어 있다. 이 제목은 후보군에 포함되지 않으므로 후보 수에는 영향이 없다.

각 연도의 전체 제목을 읽고 의미를 판정했다. 단순 문자열 교집합만으로 결과를 정하지 않았으며, 다음 두 방향을 함께 검토했다.

1. tactile, touch, force, torque, wrench, contact, compliance 등의 감각·접촉 단서가 있고, RL 또는 learned policy가 제목에 나타나는가.
2. pushing, sweeping, scooping, dragging, non-prehensile manipulation 등 프로젝트와 가까운 과업에서 센서 또는 정책 축이 제목에 생략되었을 가능성이 충분한가.

이번 단계에서는 저자, 초록, 본문, 센서 사양, 코드와 실험 결과를 확인하지 않았다. 따라서 `learning`, `policy`, `ACT`, `diffusion`을 곧바로 RL로 해석하지 않았고, `force`, `contact`, `compliance`만으로 실제 F/T 센서 사용을 확정하지 않았다.

## 3. 판정 기준

### 3.1 엄격 일치

제목에서 다음 세 요소가 모두 직접 나타나는 경우다.

- tactile, touch 또는 F/T sensor 계열 표현
- reinforcement learning 또는 deep reinforcement learning
- manipulation 과업이며 프로젝트에서 명시적으로 제외한 범위가 아님

엄격 일치도 원문 검증 전에는 해당 센서가 actor observation인지, 학습용 정답이나 보조 모듈인지 확정하지 않는다.

### 3.2 원문 확인 후보

다음 중 하나에 해당한다.

- tactile/F/T 또는 contact feedback은 명확하지만 RL·policy learning이 제목에 없다.
- RL·learned policy와 contact-rich manipulation은 명확하지만 센서 종류가 제목에 없다.
- pushing·sweeping과 매우 가까운 과업이지만 관측과 학습 방식 중 일부가 생략되어 있다.

### 3.3 제외 기준

다음 제목은 문자상 일부 조건이 맞더라도 현재 후보군에서 제외했다.

- tactile hardware, force estimation, contact detection, reconstruction 등 지각·계측만 다루는 경우
- insertion 또는 peg-in-hole 중심 과업
- dexterous in-hand manipulation 중심 과업
- imitation learning 또는 learning from demonstration만 명시된 경우
- vision-only policy가 명시된 경우
- locomotion, navigation, exoskeleton 등 현재 조작 과업과 거리가 큰 경우
- actuator 수준의 force tracking 또는 impedance tuning이 중심인 경우

## 4. IROS 2023

### 4.1 엄격 일치 — 1편

| CSV # | 논문 제목 | 제목에서 확인되는 단서 | 원문에서 확인할 사항 |
| ---: | --- | --- | --- |
| 321 | **A Grasp Pose is All You Need: Learning Multi-Fingered Grasping with Deep Reinforcement Learning from Vision and Touch.** | touch와 deep RL 기반 manipulation이 모두 명시됨 | touch가 actor에 입력되는 방식, 온라인 vision 의존성, grasping 결과의 프로젝트 전이 가능성 |

### 4.2 원문 확인 후보 — 8편

| CSV # | 논문 제목 | 제목에서 확인되는 단서 | 원문에서 확인할 사항 |
| ---: | --- | --- | --- |
| 4 | **A Multitask and Kernel Approach for Learning to Push Objects with a Target-Parameterized Deep Q-Network.** | pushing과 DQN policy가 명시됨 | tactile/F/T 관측 사용 여부, 목표 표현, 행동 공간 |
| 137 | **GOATS: Goal Sampling Adaptation for Scooping with Curriculum Reinforcement Learning.** | scooping과 curriculum RL이 명시됨 | 센서 종류, 접촉 feedback 사용 여부, 물성 변화에 대한 적응 방식 |
| 312 | **Learning Bifunctional Push-Grasping Synergistic Strategy for Goal-Agnostic and Goal-Oriented Tasks.** | pushing을 포함한 학습형 조작 전략 | RL 여부와 tactile/F/T 관측 여부 |
| 593 | **Nonprehensile Planar Manipulation through Reinforcement Learning with Multimodal Categorical Exploration.** | non-prehensile planar manipulation과 RL이 명시됨 | `multimodal`의 의미, 실제 센서 입력, pushing 과업 구성 |
| 1103 | **Contact-Aware Non-Prehensile Manipulation for Object Retrieval in Cluttered Environments.** | clutter, contact-aware, non-prehensile retrieval이 결합됨 | learned policy 여부, contact 정보의 측정 방식, 온라인 vision 사용 여부 |
| 1108 | **Pre-and Post-Contact Policy Decomposition for Non-Prehensile Manipulation with Zero-Shot Sim-To-Real Transfer.** | contact 전후 policy 분해와 non-prehensile sim-to-real이 명시됨 | policy 학습법, 접촉 관측, 전환 조건, 실물 센서 구성 |
| 1123 | **Deep Functional Predictive Control (deep-FPC): Robot Pushing 3-D Cluster Using Tactile Prediction.** | tactile prediction이 pushing control에 연결됨 | RL 여부, tactile prediction의 입력·출력, 예측에서 행동까지의 연결 |
| 1128 | **Attention for Robot Touch: Tactile Saliency Prediction for Robust Sim-to-Real Tactile Control.** [상세노트](../papers/2023-lin-attention-for-robot-touch.md) | tactile prediction, control, sim-to-real이 명시됨 | manipulation policy인지 여부, saliency가 행동 결정에 사용되는 방식 |

## 5. IROS 2024

### 5.1 엄격 일치 — 1편

| CSV # | 논문 제목 | 제목에서 확인되는 단서 | 원문에서 확인할 사항 |
| ---: | --- | --- | --- |
| 1146 | **Tactile Active Inference Reinforcement Learning for Efficient Robotic Manipulation Skill Acquisition.** [상세노트](../papers/2024-liu-tactile-active-inference-rl.md) | tactile, reinforcement learning, manipulation이 모두 명시됨 | 실제 tactile 관측, active inference와 RL의 결합, 행동 공간과 실물 검증 |

### 5.2 원문 확인 후보 — 9편

| CSV # | 논문 제목 | 제목에서 확인되는 단서 | 원문에서 확인할 사항 |
| ---: | --- | --- | --- |
| 100 | **Zero-Shot Transfer of a Tactile-based Continuous Force Control Policy from Simulation to Robot.** | tactile 기반 force-control policy와 sim-to-real이 명시됨 | policy 학습법, 저수준 force control과 manipulation policy의 경계 |
| 304 | **RTTF: Rapid Tactile Transfer Framework for Contact-Rich Manipulation Tasks.** | tactile transfer와 contact-rich manipulation이 결합됨 | 전이 대상이 policy인지 표현인지, RL 사용 여부, 실제 센서 조건 |
| 495 | **MPGNet: Learning Move-Push-Grasping Synergy for Target-Oriented Grasping in Occluded Scenes.** | occlusion에서 move–push–grasp 전략을 학습함 | tactile/F/T 사용 여부, push 단계의 policy와 vision 의존성 |
| 614 | **ProSIP: Probabilistic Surface Interaction Primitives for Learning of Robotic Cleaning of Edges.** | surface interaction과 cleaning skill learning이 명시됨 | F/T 또는 tactile feedback, primitive 학습법, sweeping과의 동역학 차이 |
| 690 | **A Contact Model based on Denoising Diffusion to Learn Variable Impedance Control for Contact-rich Manipulation.** | diffusion contact model과 variable impedance learning이 결합됨 | 실제 F/T 관측, contact model이 actor·controller에 연결되는 방식, RL 여부 |
| 711 | **Multi-Fingered Dragging of Unknown Objects and Orientations Using Distributed Tactile Information Through Vision-Transformer and LSTM.** | distributed tactile로 미지 물체를 dragging함 | RL 여부, tactile history, 온라인 외부 vision 사용 여부, 행동 출력 |
| 724 | **Learning a Pre-Grasp Manipulation Policy to Effectively Retrieve a Target in Dense Clutter.** | dense clutter의 target retrieval policy가 명시됨 | tactile/F/T 관측 여부, pre-grasp manipulation의 실제 동작과 vision 의존성 |
| 987 | **The Power of the Senses: Generalizable Manipulation from Vision and Touch through Masked Multimodal Learning.** | vision–touch multimodal learning과 generalizable manipulation이 결합됨 | 표현 학습과 행동 policy의 관계, 실행 중 vision·touch 사용 조건 |
| 1441 | **Fine Manipulation Using a Tactile Skin: Learning in Simulation and Sim-to-Real Transfer.** | tactile skin 기반 manipulation과 sim-to-real learning이 명시됨 | RL 여부, tactile 표현, 실물 전이 방법과 과업 범위 |

## 6. IROS 2025

### 6.1 최우선 원문 확인 후보 — 4편

센서·접촉 표현과 학습된 행동 또는 policy가 함께 나타나지만, 제목에 reinforcement learning이 명시되지 않아 엄격 일치로 분류하지 않았다.

| CSV # | 논문 제목 | 제목에서 확인되는 단서 | 원문에서 확인할 사항 |
| ---: | --- | --- | --- |
| 171 | **VDTF-ACT: ACT-based Multimodal Space Fine Manipulation Method with Visual Depth Tactile Fusion.** | visual-depth–tactile fusion과 ACT 기반 manipulation이 결합됨 | ACT가 imitation policy인지, tactile의 실행 중 사용, 외부 vision 의존성 |
| 728 | **Learning Gentle Grasping Using Vision, Sound, and Touch.** | touch를 포함한 multimodal 입력으로 gentle grasping을 학습함 | RL 여부, touch의 행동 기여, 힘 제한과 feedback 구조 |
| 1371 | **Disambiguate Gripper State in Grasp-Based Tasks: Pseudo-Tactile as Feedback Enables Pure Simulation Learning.** [상세노트](../papers/2025-yang-pseudo-tactile-gripper-state.md) | pseudo-tactile feedback과 simulation learning이 결합됨 | pseudo-tactile의 정의, 실물 센서 사용 여부, actor 입력과 sim-to-real 방식 |
| 1788 | **UltraDP: Generalizable Carotid Ultrasound Scanning with Force-Aware Diffusion Policy.** | force-aware 정보와 diffusion policy가 직접 결합됨 | 실제 force sensing, diffusion policy의 관측·행동, 의료 scanning과 sweeping의 공통 제어 요소 |

### 6.2 그 밖의 원문 확인 후보 — 8편

| CSV # | 논문 제목 | 제목에서 확인되는 단서 | 원문에서 확인할 사항 |
| ---: | --- | --- | --- |
| 331 | **Adaptive Visuo-Tactile Fusion with Predictive Force Attention for Dexterous Manipulation.** | visuo-tactile fusion과 predictive force attention이 명시됨 | perception module인지 policy인지, 실행 중 센서와 행동의 연결 |
| 662 | **High-dynamic Tactile Sensing for Tactile Servo Manipulation: Let Robots Swing a Hammer.** | 고속 tactile sensing과 tactile servo manipulation이 결합됨 | 학습 policy 여부, tactile update rate와 행동 제어 구조 |
| 727 | **Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention.** [상세노트](../papers/2025-dengler-location-based-attention-pushing.md) | cluttered pushing을 직접 학습함 | tactile/F/T 사용 여부, location attention의 입력, 온라인 vision 의존성 |
| 811 | **CATCH-FORM-3D: Compliance-Aware Tactile Control and Hybrid Deformation Regulation for 3D Viscoelastic Object Manipulation.** | tactile control과 compliance-aware manipulation이 명시됨 | learned policy 여부, tactile·force 표현, 저수준 제어와 행동 정책의 경계 |
| 1150 | **VibeCheck: Using Active Acoustic Tactile Sensing for Contact-Rich Manipulation.** | active acoustic tactile sensing과 contact-rich manipulation이 결합됨 | 학습 policy 여부, 센서 관측에서 행동까지의 연결 |
| 1813 | **Augmenting robotic disassembly skill: combining compliance control strategy with reinforcement learning for twist-pulling disassembly \*.** | compliance control과 reinforcement learning이 결합됨 | 실제 tactile/F/T 관측, compliance와 RL action의 역할 분담 |
| 1872 | **SAVR: Scooping Adaptation for Variable food properties via Reinforcement Learning.** | scooping adaptation과 RL이 명시됨 | tactile/F/T 관측, 물성 적응에 사용한 history와 행동 공간 |
| 1975 | **Semantic-Geometric-Physical-Driven Robot Manipulation Skill Transfer via Skill Library and Tactile Representation.** | tactile representation과 manipulation skill transfer가 결합됨 | policy transfer인지 skill retrieval인지, RL 여부, tactile의 실행 중 역할 |

## 7. 2023–2025 제목 수준의 추세

아래 내용은 제목에서 반복적으로 나타나는 표현을 정리한 **후속 검증 가설**이다. 논문 본문을 확인한 연구 동향 결론이 아니다.

| 관점 | 2023 | 2024 | 2025 | 프로젝트에서 확인할 질문 |
| --- | --- | --- | --- | --- |
| 정책·학습 표현 | DQN, curriculum RL, policy decomposition, predictive control | active inference RL, diffusion contact model, LSTM·Transformer, zero-shot transfer | ACT, diffusion policy, simulation learning, RL–compliance 결합 | PPO actor와 별도 contact model·history encoder를 어떻게 구분할 것인가 |
| 과업 | pushing, scooping, non-prehensile retrieval | dragging, cleaning, pre-grasp retrieval, contact-rich manipulation | pushing, tactile servoing, disassembly, scooping, force-aware scanning | sweeping과 가장 가까운 접촉 유지·횡방향 보정·속도 적응 요소는 무엇인가 |
| 센서·표현 | touch, tactile prediction, tactile saliency | distributed tactile, tactile skin, vision–touch learning, tactile force-control | visual-depth–tactile fusion, pseudo-tactile, force attention, acoustic tactile | 손목 wrench와 부분 tactile 영역이 각각 어떤 모호성을 줄이는가 |
| 전이 | zero-shot sim-to-real, tactile predictive control | tactile policy transfer와 sim-to-real이 반복됨 | simulation learning과 generalizable policy가 반복됨 | 실물 신호의 범위·noise·지연·coverage가 시뮬레이션 표현과 대응하는가 |

### 7.1 관측 표현이 policy architecture와 함께 다뤄진다

2023년의 tactile prediction·saliency, 2024년의 distributed tactile·masked multimodal learning, 2025년의 tactile fusion·predictive force attention처럼 접촉 표현과 manipulation 또는 control을 함께 다루는 제목이 반복된다. 해당 표현이 실제 actor 입력이며 행동 결정에 직접 연결되는지는 원문을 확인해야 한다.

프로젝트에서는 이를 `raw F/T + raw tactile`의 단일 선택으로 축약하지 말고, 보정 wrench, 활성 tactile 영역, sensor validity, history와 학습 표현을 분리해 비교할 필요가 있다. 이 문장은 제목 비교에서 도출한 검토 방향이며 확정 설계가 아니다.

### 7.2 sim-to-real과 zero-shot transfer가 반복된다

2023년의 pre/post-contact policy와 tactile control, 2024년의 tactile force-control policy·tactile skin, 2025년의 pure simulation learning에서는 sim-to-real 또는 transfer 표현이 반복된다. simulation과 실제 센서 표현의 대응이 각 논문의 핵심 문제인지는 원문을 확인해야 한다.

원문에서는 센서 영상 변환, domain randomization, feature alignment, system identification, real-world fine-tuning 중 무엇을 사용하는지 구분해야 한다. 제목의 `sim-to-real`만으로 실제 로봇 성능이나 zero-shot 성공을 일반화하지 않는다.

### 7.3 비파지 조작은 존재하지만 F/T–tactile 결합은 제목에서 드러나지 않는다

Pushing, scooping, dragging, cleaning, retrieval은 세 연도에 걸쳐 반복된다. 반면 별도의 wrist F/T와 hand tactile을 동시에 사용한다는 제목은 후보군에서 확인되지 않았다. 특히 다음 구분이 필요하다.

- tactile sensor가 force를 추정하는 경우와 별도 F/T 센서를 함께 쓰는 경우
- contact force를 reward나 simulator 정답으로만 쓰는 경우와 actor가 실시간으로 관측하는 경우
- 초기 vision만 쓰는 경우와 조작 중 외부 vision을 계속 사용하는 경우
- tactile/F/T가 상태 추정에만 쓰이는 경우와 실제 행동을 수정하는 경우

## 8. 원문 정독 우선순위

### 8.1 1순위 — 현재 과업과 정책 구조가 가까운 제목

1. **Pre-and Post-Contact Policy Decomposition for Non-Prehensile Manipulation with Zero-Shot Sim-To-Real Transfer.** — contact 전환과 policy 구조
2. **Deep Functional Predictive Control (deep-FPC): Robot Pushing 3-D Cluster Using Tactile Prediction.** — tactile prediction에서 pushing action까지의 연결
3. **Zero-Shot Transfer of a Tactile-based Continuous Force Control Policy from Simulation to Robot.** — tactile·force control과 실물 전이
4. **ProSIP: Probabilistic Surface Interaction Primitives for Learning of Robotic Cleaning of Edges.** — sweeping과 가까운 surface interaction skill
5. **A Contact Model based on Denoising Diffusion to Learn Variable Impedance Control for Contact-rich Manipulation.** — learned contact model과 compliance
6. **Multi-Fingered Dragging of Unknown Objects and Orientations Using Distributed Tactile Information Through Vision-Transformer and LSTM.** — tactile history와 미지 물체 dragging
7. **Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention.** — cluttered pushing policy와 관측 조건
8. **SAVR: Scooping Adaptation for Variable food properties via Reinforcement Learning.** — 물성 변화에 대한 contact-rich RL 적응

### 8.2 2순위 — 센서 표현과 policy 학습을 확인할 제목

1. **Attention for Robot Touch: Tactile Saliency Prediction for Robust Sim-to-Real Tactile Control.**
2. **Tactile Active Inference Reinforcement Learning for Efficient Robotic Manipulation Skill Acquisition.**
3. **The Power of the Senses: Generalizable Manipulation from Vision and Touch through Masked Multimodal Learning.**
4. **VDTF-ACT: ACT-based Multimodal Space Fine Manipulation Method with Visual Depth Tactile Fusion.**
5. **Disambiguate Gripper State in Grasp-Based Tasks: Pseudo-Tactile as Feedback Enables Pure Simulation Learning.**
6. **UltraDP: Generalizable Carotid Ultrasound Scanning with Force-Aware Diffusion Policy.**
7. **Augmenting robotic disassembly skill: combining compliance control strategy with reinforcement learning for twist-pulling disassembly \*.**

우선순위는 논문의 질이나 학술적 중요도 순위가 아니다. 현재 프로젝트의 관측→표현→행동 연결을 확인하기 위한 정독 순서다.

## 9. 대표 제외 사례

| 연도 | 논문 제목 | 제외 이유 |
| --- | --- | --- |
| 2023 | **Real-Time Model-Free Deep Reinforcement Learning for Force Control of a Series Elastic Actuator.** | RL과 force가 모두 있으나 actuator 수준 force control임 |
| 2023 | **Learning Robotic Assembly by Leveraging Physical Softness and Tactile Sensing.** | tactile learning이지만 assembly와 physical softness 중심임 |
| 2023 | **MOMA-Force: Visual-Force Imitation for Real-World Mobile Manipulation.** | force를 사용하지만 imitation learning을 명시함 |
| 2024 | **Learning When to Stop: Efficient Active Tactile Perception with Deep Reinforcement Learning.** | tactile+RL이지만 manipulation policy가 아니라 active perception임 |
| 2024 | **Exploratory Motion Guided Tactile Learning for Shape-Consistent Robotic Insertion.** | insertion 과업임 |
| 2024 | **Learning a Shape-Conditioned Agent for Purely Tactile In-Hand Manipulation of Various Objects.** | tactile learning이지만 in-hand manipulation임 |
| 2025 | **Peg-in-hole assembly method based on visual reinforcement learning and tactile pose estimation.** | tactile+RL이지만 peg-in-hole 과업임 |
| 2025 | **Q-Learning-based Optimal Force-Tracking Control of Grinding Robots in Uncertain Environments.** | Q-learning+force이나 저수준 force tracking 중심임 |
| 2025 | **Low-Fidelity Visuo-Tactile Pre-Training Improves Vision-Only Manipulation Performance.** | tactile은 사전학습에만 사용되고 실행은 vision-only로 명시됨 |
| 2025 | **AugInsert: Learning Robust Visual-Force Policies via Data Augmentation for Object Assembly Tasks.** | visual-force policy이지만 insertion·assembly 범위임 |

## 10. 확인 범위와 한계

- 제공된 CSV가 각 연도의 공식 IROS 논문을 빠짐없이 포함하는지는 별도로 검증하지 않았다. 따라서 결과는 **제공된 CSV에 수록된 전체 제목**에 대한 선별이다.
- 제목만으로 sensor placement, signal type, actor observation, reward, critic privileged information, online vision, action space와 실물 검증을 확인할 수 없다.
- `tactile`, `force`, `contact`, `compliance`는 서로 다른 정보다. 제목에 force가 있다고 F/T sensor를 사용했다고 단정하지 않는다.
- `learning`, `policy`, `ACT`, `diffusion`, `active inference`가 모두 reinforcement learning을 뜻하는 것은 아니다.
- 제목 기반 추세는 원문 정독 대상을 정하기 위한 가설이다. 논문 내용, 저자들이 밝힌 Limitation과 Future Work, 프로젝트 적용 가능성은 원문 정독 단계에서 별도로 기록한다.
- 후보가 적거나 제목에서 F/T–tactile 결합이 드러나지 않는다는 사실은 연구 공백이나 신규성을 확정하지 않는다.

## 11. 사용자 임시 선정 및 후속 원문 정독 — 2026-09-16 추가

### 11.1 선정의 의미와 기존 조사본의 관계

사용자는 아래 5편을 **현재 연구 주제와 관련 있는 논문으로 임시 선정**했다. 이 기록은 사용자가 제공한 선정 결정과 서지 정보를 반영한 것이며, 제목 기반 1차 선별을 수행한 정리자의 최종 적합성 판정이 아니다. **임시 선정, 원문 정독 완료, 실제 방법의 프로젝트 적용 가능성 확정은 서로 다른 상태**다.

1–10절의 31편 후보군, 연도별 집계, 문자상 엄격 일치와 원문 확인 후보의 구분, 당시 정독 우선순위는 최초 조사 기록으로 보존한다. 아래 5편은 그 후보군의 후속 선택 목록이며, 나머지 26편을 부적합으로 확정하거나 삭제한 것이 아니다. 향후 작업 대상은 사용자의 최신 요청을 따른다.

`IROS-S01`–`IROS-S05`는 이번 사용자 목록의 순서를 유지한 관리 식별자다. 우열 순위가 아니며, [2026-09-14 종합 조사본](2026-09-14_blind-sweep-force-torque-tactile.md)의 `R1`–`R7` 및 각 원문 내부의 참고문헌 번호와 혼용하지 않는다. 이 목록은 **IROS 학술대회 논문** 목록이며, 이전 SCIE 저널 중심 조사 범주와 구분한다.

| 관리 ID | 논문 | 기존 제목 선별 위치 | 선정 상태 | 후속 원문 정독 상태 |
| --- | --- | --- | --- | --- |
| IROS-S01 | Attention for Robot Touch: Tactile Saliency Prediction for Robust Sim-to-Real Tactile Control | 2023 CSV #1128, §4.2 | 사용자 임시 선정 | 제공된 출판본 PDF 7쪽 정독·정리 완료. [상세 노트](../papers/2023-lin-attention-for-robot-touch.md) |
| IROS-S02 | Disambiguate Gripper State in Grasp-Based Tasks: Pseudo-Tactile as Feedback Enables Pure Simulation Learning | 2025 CSV #1371, §6.1 | 사용자 임시 선정 | 제공된 출판본 PDF 8쪽 정독·정리 완료. [상세 노트](../papers/2025-yang-pseudo-tactile-gripper-state.md) |
| IROS-S03 | Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention | 2025 CSV #727, §6.2 | 사용자 임시 선정 | 제공된 출판본 PDF 7쪽 정독·정리 완료. [상세 노트](../papers/2025-dengler-location-based-attention-pushing.md) |
| <a id="iros-s04"></a>IROS-S04 | Multi-Fingered Dragging of Unknown Objects and Orientations Using Distributed Tactile Information Through Vision-Transformer and LSTM | 2024 CSV #711, §5.2 | 사용자 임시 선정 | 이번 후속 정독용 원문 미제공. 사용자 제공 서지만 기록 |
| IROS-S05 | Tactile Active Inference Reinforcement Learning for Efficient Robotic Manipulation Skill Acquisition | 2024 CSV #1146, §5.1 | 사용자 임시 선정 | 제공된 출판본 PDF 6쪽 정독·정리 완료. [상세 노트](../papers/2024-liu-tactile-active-inference-rl.md) |

### 11.2 사용자 제공 서지

다음 서지는 사용자가 제공한 내용이다. IROS-S01–S03·S05는 각각의 첨부 출판본의 제목·저자·DOI·게재 페이지와 대조했다. IROS-S04는 이번에 원문이나 출판사 자료를 별도로 검증하지 않았으며, `et al.`을 임의의 저자 목록으로 확장하지 않는다. 사용자 제공 서지의 표기는 유지하며, IROS-S02의 전체 저자 목록은 개별 정독 노트에 기록했다.

**IROS-S01 / 사용자 [1]** — Y. Lin, M. Comi, A. Church, D. Zhang, and N. F. Lepora, “Attention for Robot Touch: Tactile Saliency Prediction for Robust Sim-to-Real Tactile Control,” in *2023 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)*, Detroit, MI, USA: IEEE, Oct. 2023, pp. 10806–10812. DOI: [10.1109/IROS55552.2023.10341888](https://doi.org/10.1109/IROS55552.2023.10341888).

**IROS-S02 / 사용자 [2]** — Y. Yang et al., “Disambiguate Gripper State in Grasp-Based Tasks: Pseudo-Tactile as Feedback Enables Pure Simulation Learning,” in *2025 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)*, Hangzhou, China: IEEE, Oct. 2025, pp. 14899–14906. DOI: [10.1109/IROS60139.2025.11246513](https://doi.org/10.1109/IROS60139.2025.11246513).

**IROS-S03 / 사용자 [3]** — N. Dengler, J. D. Aguila Ferrandis, J. Moura, S. Vijayakumar, and M. Bennewitz, “Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention,” in *2025 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)*, Hangzhou, China: IEEE, Oct. 2025, pp. 7600–7606. DOI: [10.1109/IROS60139.2025.11246809](https://doi.org/10.1109/IROS60139.2025.11246809).

**IROS-S04 / 사용자 [4]** — T. Ueno et al., “Multi-Fingered Dragging of Unknown Objects and Orientations Using Distributed Tactile Information Through Vision-Transformer and LSTM,” in *2024 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)*, Abu Dhabi, United Arab Emirates: IEEE, Oct. 2024, pp. 7445–7452. DOI: [10.1109/IROS58592.2024.10802283](https://doi.org/10.1109/IROS58592.2024.10802283).

**IROS-S05 / 사용자 [5]** — Z. Liu, X. Liu, Y. Zhang, Z. Liu, and P. Huang, “Tactile Active Inference Reinforcement Learning for Efficient Robotic Manipulation Skill Acquisition,” in *2024 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)*, Abu Dhabi, United Arab Emirates: IEEE, Oct. 2024, pp. 10884–10889. DOI: [10.1109/IROS58592.2024.10802750](https://doi.org/10.1109/IROS58592.2024.10802750).

<a id="iros-s01"></a>

### 11.3 IROS-S01에서 원문으로 확인한 사항

*Attention for Robot Touch*는 **새로운 pushing 정책보다, 목표 edge와 distractor가 동시에 닿았을 때 목표 접촉 표현을 분리하는 방법**이 중심이다. ConDepNet은 real tactile image를 contact depth로 변환하고, TacSalNet은 목표 saliency를 예측하며, TacNGen은 VAE로 학습용 접촉 잡음을 생성한다. 이 표현을 PoseNet–PID 또는 image-based deep-RL edge-following에 연결한다. 별도 손목 F/T, 물리 단위 힘 추종, 물체 운반의 목표 도달을 검증한 논문으로 분류하지 않는다. [첨부 출판본 §III–IV, Fig. 2·5, PDF pp. 2–6]

GAN·VAE의 손실식과 대응/합성 데이터 생성법은 본문에 있지만, GAN/VAE의 상세 hyperparameter 및 RL reward·전체 학습 설정은 [2]나 보충자료에 의존하거나 본문에 미제시다. 정적 pose 평가에는 prediction drift calibration이 포함되며, 가까운 distractor를 target 일부로 포함하는 실패도 보고한다. 자세한 수식·사양·실험·Limitation·Future Work는 [개별 정독 노트](../papers/2023-lin-attention-for-robot-touch.md)를 따른다.

이 절의 원문 확인 결과는 IROS-S01에만 적용한다. IROS-S02·S03·S05의 확인 결과는 아래 §11.4–11.6에 별도로 기록한다. 원문 미제공인 IROS-S04의 실제 센서 구성, RL 채택 여부, 관측·행동·성과를 이름이나 임시 선정 사실만으로 확정하지 않는다.


<a id="iros-s02"></a>

### 11.4 IROS-S02에서 원문으로 확인한 사항 — 2026-09-16

*Disambiguate Gripper State in Grasp-Based Tasks*는 **RL이 아니라 Diffusion Policy 기반 모방학습** 연구다. Force-controlled Robotiq 2F-85의 힘 평형 시 관절각을 pseudo-tactile로 사용하고, 빈 파지로 최대 닫힘에 도달하면 저수준 제어기가 정책 명령을 override하여 그리퍼를 실제로 다시 연다. 정책은 RGB·EEF pose·binary gripper state를 관측한다. 따라서 전용 tactile array의 분포 관측이나 외부 시각 없는 정책으로 분류하지 않는다. [첨부 출판본 §III–IV-C, Fig. 2–3, PDF pp. 2–5]

시뮬레이터 정답 상태를 사용하는 수작업 expert로 성공 시연을 생성하고, 과업당 2,000개 시연을 이용해 학습한다. 현실적인 asset·시각 randomization과 별도로, 외력·토크에 반응하는 admittance가 EEF 궤적을 보정한다. 이 외력의 측정·추정 장치, threshold·gain·필터, DP 최적화 세부는 원문에 미명시다. GAN은 제시하지 않는다. [첨부 출판본 §IV-B–C·V-A, 식 (1), PDF pp. 4–6]

세 실물 과업의 전체 task 성공률은 90%·90%·80%이며, SR-R 100%는 재개방·파지 재시도에 대한 복구율이지 task 전체 성공률이 아니다. 원문에는 별도 Limitation 절이나 구체적인 Future Work 계획이 없으며, 본문이 인정하는 준비 비용·잔여 sim-to-real 문제와 실험 결과의 범위를 구분해 기록했다. 자세한 메소드·전체 결과·ablation·미명시 사항은 [개별 정독 노트](../papers/2025-yang-pseudo-tactile-gripper-state.md)를 따른다. [첨부 출판본 §V–VI, Table I–IV, PDF pp. 6–8]

이 원문 분류는 사용자의 임시 선정을 삭제하거나 부적합으로 확정하는 결정이 아니다. 최초 제목 선별과 후속 원문 확인을 구분하기 위한 기록이며, IROS-S03의 확인 결과는 아래 §11.5에 별도로 기록한다. IROS-S05의 확인 결과는 §11.6에 기록하며, IROS-S04의 정독 완료를 뜻하지 않는다.

<a id="iros-s03"></a>

### 11.5 IROS-S03에서 원문으로 확인한 사항 — 2026-09-16

*Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention*는 **현재 물체 pose·목표 pose·pusher 위치와 binary occupancy grid를 사용하는 PPO pushing 연구**다. F/T·tactile이 actor 관측으로 제시되지 않으며, 실물에서는 Vicon 또는 RealSense D435 3대·AprilTags·point-cloud fusion으로 실행 중 지각 정보를 얻는다. `Guidance-free`는 global path·그 경로상의 subgoal이 없다는 뜻이지 초기 관측만 사용하는 Blind 제어라는 뜻이 아니다. [첨부 출판본 §III, §IV-E, Fig. 2, PDF pp. 2–3, 6]

5 mm cell 지도를 16 × 16 patch로 처리하고, patch 기준 물체·목표 위치와 embedding에서 feature·score를 구해 64차원 attention feature를 만든다. 수치 상태 feature와 결합한 LSTM 정책은 축별 11개 속도 bin의 22 logits를 출력한다. 본문에는 reward 식·계수, PPO 설정, 물성·geometry randomization과 두 시간척도의 pose noise가 제시되어 있다. 충돌 penalty는 장애물 접촉 여부에 대한 binary 값이며, 힘 크기 추종이나 촉각 신호 처리가 아니다. [첨부 출판본 §III–IV-A, 식 (1), Table I, PDF pp. 3–4]

단일 장애물 정책의 두 장애물 직접 적용은 성공률 48.1%·충돌률 50.7%로 CNN보다 낮았고, 두 장애물 환경에서 5 × 10^8 steps 추가 학습한 뒤 91.2%·3.54%로 개선되었다. 이 결과를 모든 clutter에 대한 즉시 일반화로 확대하지 않는다. 실물 정량 결과는 MoCap의 세 장면에서 100%·100%·90%이며, dynamic·3Cam은 별도 정성 시연이다. 목표 pose도 실물에서는 고정했다. [첨부 출판본 §IV-D–E, Table II, PDF pp. 5–7]

원문에는 구체적인 Future Work 계획이 없으며, 단일→두 장애물 성능 저하·잔여 실패·실물 평가 범위 등 저자 명시 제약을 따로 정리했다. Grid100 × 140과 patch16 × 16의 가장자리 처리, Table I의 discount/GAE 기호, Table II caption의 포괄 주장과 예외도 기록했다. 자세한 내용은 [개별 정독 노트](../papers/2025-dengler-location-based-attention-pushing.md)를 따른다. 이 분류는 사용자의 임시 선정을 삭제하거나 부적합으로 확정하는 결정이 아니며, IROS-S05는 아래 §11.6에서 별도로 다룬다. IROS-S04는 아직 후속 정독용 원문 미제공 상태다.

<a id="iros-s05"></a>

### 11.6 IROS-S05에서 원문으로 확인한 사항 — 2026-09-16

*Tactile Active Inference Reinforcement Learning for Efficient Robotic Manipulation Skill Acquisition*는 **handcrafted tactile features와 모델 앙상블·reward model을 결합하고, 예상 보상과 state information gain을 평가하는 CEM으로 행동 시퀀스를 계획하는 연구**다. 이 논문의 AIRL은 Active Inference RL이며 inverse RL이나 모방학습이 아니다. SAC는 내부 학습기가 아니라 비교군이다. [첨부 출판본 §II-B·III-A, 식 (1)–(6), Fig. 1, PDF pp. 2–3]

촉각 정적 특징은 Poisson 기반 깊이 영상의 중심과 pixel sum이고, 동적 특징은 Lucas–Kanade optical flow의 축별 histogram entropy다. 이들은 접촉 위치·intensity·변형 추세의 대리 표현이지, N 단위 힘이나 signed shear vector를 복원한 값은 아니다. 시뮬레이션 pushing에서는 optical flow를 쓰지 못해 정적 특징만 사용하며, 현재 로봇·물체의 위치·속도·자세·각속도도 관측한다. 따라서 물체 상태를 모르는 tactile-only pushing으로 분류하지 않는다. [첨부 출판본 §III-B·IV-B, 식 (7)–(10), PDF pp. 3–5]

실물은 KUKA iiwa7·BackYard gripper·GelSight mini로 너트를 돌리는 별도 학습 실험이다. 고정 하강 속도에서 회전 증분만 학습하고, 하강 방향 flow entropy의 음수를 reward로 사용한다. 시뮬레이션 pushing 정책의 실물 이전이나 GAN은 제시하지 않는다. Dense/sparse/실물 reward 식은 있지만 모델 학습 loss·hyperparameter, CEM horizon·후보 수, 센서 해상도·측정 범위·주파수 등은 미명시다. [첨부 출판본 §IV-A–B, 식 (11), Fig. 3–4, PDF pp. 4–5]

Dense 조건에서 Tactile-AIRL과 origin AIRL 모두 약 100 episodes, SAC 약 1,000 episodes라는 본문 결과를 보고한다. 약 15 episodes의 실물 수렴은 제안 방법만의 reward curve이며, 실제 전단력 감소량이나 체결 성공률을 측정한 수치가 아니다. 단순 연결 접촉, 시뮬레이션 flow 부재, 너트 각도 정답·실물 비교 비용의 한계를 기록했고, 구체적 Future Work는 원문에 없다. 상세 수식·결과·미명시 사항은 [개별 정독 노트](../papers/2024-liu-tactile-active-inference-rl.md)를 따른다. [첨부 출판본 §III-B·IV-C·V, Fig. 5–7, PDF pp. 3–6]

IROS-S01–S03·S05 네 편의 첨부 원문 정독이 완료되었고 IROS-S04는 원문 미제공 상태다. 이는 코드 실행·실험 재현이나 프로젝트 적용 판단의 완료를 뜻하지 않으며, 기존 임시 선정과 1–10절의 제목 선별 기록은 유지한다.
