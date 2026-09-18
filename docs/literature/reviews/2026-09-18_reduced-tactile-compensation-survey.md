# Research Motivation 보강 — 신규 문헌에서 본 축약 촉각의 보완 구조

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](README.md) · [Research Motivation](../../presentation/01_Research_Motivation.md)

**조사 기준일: 2026-09-18.** Research Motivation 보강 계획 중 **2.1. 물체 정보의 제공 조건과 축약 촉각의 보완 구조**만 다룬다. F/T 단독 사용의 한계와 Reward Formulation은 이번 조사 범위에서 제외한다.

이번 조사는 기존 저장소에 이미 정리된 논문을 재분류하는 방식이 아니라, **Sider Scholar로 새 후보를 발굴한 뒤 저장소에서 논문 제목을 재검색하여 기존 조사에 등장하지 않은 연구만 남기는 방식**으로 수행했다. 최종 핵심 비교 대상은 4편이며, 모두 조사 시점의 저장소 제목 검색에서 일치 항목이 없었다.

## 2.1.1. 조사 질문

축약된 촉각을 사용하는 연구에서 다음을 한 세트로 확인한다.

1. 물체 Pose와 Shape가 실행 중 Tracking / Initial / 미제공 중 어느 조건인가?
2. Initial 또는 미제공이라면, 부족한 정보를 어떤 센서·상태·이력·추정 구조로 보완하는가?
3. 촉각 축약으로 남는 정보와 제외되는 정보가 무엇이며, 추가 입력이 어떤 역할을 하는가?
4. Actor에는 없지만 Critic·Reward·Representation Learning 등에만 제공되는 Privileged Information이 있는가?
5. 추가 정보가 실제로 도움이 된다는 저자 설명, modality ablation, history ablation 또는 실패 분석이 있는가?

## 2.1.2. 신규 문헌 비교

| ID | 연구 | 축약 촉각 표현 | 물체 Pose | 물체 Shape | 실행 시 보완 정보·구조 | 학습 전용 정보 | 보완 근거 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **N1** | **Melnik et al., 2021 — Using Tactile Sensing to Improve the Sample Efficiency and Performance of DDPG for Simulated In-Hand Manipulation** | 92개 센서를 16개 손 영역으로 pooling한 **16차원 Boolean 접촉**. 각 영역에서 하나라도 접촉하면 1 | **Tracking**. 정책 상태에 현재 물체 위치·자세와 선/각속도를 매 step 제공 | 명시적 Geometry/CAD는 **미제공** | 24개 관절각·24개 관절속도, 현재 물체 상태, 목표 Pose를 함께 제공 | 비대칭 Critic은 명시되지 않음. DDPG/HER의 Actor·Critic이 같은 상태 구조를 사용 | 저해상도 16-Binary에서도 촉각 추가 이득이 유지됨. 반면 proprioception 제거 실험은 큰 성능 저하를 보임. 즉 **저차원 Binary 촉각을 사용하지만 현재 물체 상태와 고유감각을 계속 함께 제공**하는 구조 |
| **N2** | **Liang et al., 2022 — Multifingered Grasping Based on Multimodal Reinforcement Learning** | 손끝 **Binary contact** + 연속 torque 대신 **6단계로 양자화한 joint torque** | **Initial**. Vision/Point Cloud는 초기 grasp pose 생성에 사용하고, 접촉 조작 단계에서는 현재 물체 Pose를 정책에 제공하지 않음 | 실행 정책에는 **미제공** | 관절각, 이전 Action, Binary fingertip contact, level-based joint torque, **3-step observation history**. 실험에서 GRU 사용 | 일반 PPO. 별도의 privileged Critic은 명시되지 않음. Reward는 grasp 성공 및 hand-closing 항으로 구성 | 논문은 contact 단계에 **Vision/Object Model이 없다고 명시**. Joint angle only → +tactile → +tactile+torque를 비교했고, 3-modal 정책이 가장 안정적. GRU가 MLP보다 우수했으며 저자들은 history가 상호작용과 표면 형상 단서를 담는다고 해석 |
| **N3** | **Luo et al., 2026 — Blind Dexterous Grasping via Real2Sim2Real Tactile Policy Learning** | TwinTac+FSR의 **44개 Binary tactile channel**. Raw bit만으로는 taxel 위치가 명시되지 않음 | 최종 실물 정책에는 **미제공** | 최종 실물 정책에는 **미제공** | 각 Binary bit에 **Forward Kinematics로 계산한 3D taxel 위치**를 결합, **16-frame tactile history**, proprioception을 사용 | 매우 강함. PPO expert의 **Critic과 Reward는 privileged simulator state 사용**. 별도 tactile encoder pretraining에서는 object point cloud, object pose, hand point cloud, robot configuration, contact label을 supervision으로 사용. 배포 시 제거 | 저자들이 “sparse binary contacts로 직접 policy를 학습하기 어렵다”고 명시. FK spatial grounding + history + privileged geometric pretraining을 도입. 실패 분석에서도 sparse/partial tactile observation이 unsafe configuration과 empty grasp에 기여한다고 보고 |
| **N4** | **Ahn et al., 2026 — KineFuse: Kinematic-Aware Haptic Fusion for In-Hand Occluded-Object Pose Tracking** | 손끝 **Binary contact**, 일부 관절의 3-axis proximal F/T, 전 관절 proprioception으로 구성된 sparse haptic | **Tracking (estimated)**. RGB-D + FoundationPose 기반으로 매 step 6D Pose를 갱신 | **Initial / Known prior**. Known object CAD model을 가정 | RGB-D, binary contact, sparse proximal F/T, q/qdot, **4-step history**, URDF 기반 finger graph 구조를 결합 | RL Critic/Reward는 해당 없음. Pose tracker 학습 문제 | 논문 자체가 **sparse haptic은 accessible하지만 단순 flat fusion은 공간·기구학 관계를 잃는다**고 문제를 설정. encoder 구조 ablation과 tracking/manipulation 평가를 수행. 단, 후속 ablation에서는 성능 이득 일부가 haptic 값 자체보다 구조적 inductive bias에서 온다는 결과도 보고 |

## 2.1.3. 논문별 확인 내용

### N1. Melnik et al., 2021

- 원문: [Frontiers in Robotics and AI](https://doi.org/10.3389/frobt.2021.538773)
- 16-Binary 조건은 92개 센서를 phalanx와 palm 기준 16개 영역으로 묶은 표현이다.
- 그러나 tactile-only 정책이 아니다. 기본 68차원 state에 **현재 물체 위치·자세·속도와 로봇 고유감각**이 포함되고, Binary tactile은 여기에 추가된다.
- 따라서 **“영역별 Binary tactile로 충분했다”기보다, 축약 촉각과 현재 object state를 함께 사용하는 사례**로 분류해야 한다.
- 저자들은 정확한 object geometry가 state에 직접 표현되지는 않지만 tactile이 geometry/contact physics에 관한 latent representation 학습을 도울 수 있다고 해석한다.
- 후속 방향으로 multimodal sensor fusion을 제시한다.

### N2. Liang et al., 2022

- 원문: [IEEE RA-L, DOI 10.1109/LRA.2021.3138545](https://doi.org/10.1109/LRA.2021.3138545)
- 실물에서는 Point Cloud 기반 방법으로 **초기 grasp pose**를 만들지만, 이후 contact manipulation 단계의 RL observation은 **이전 action + Binary fingertip contact + quantized joint torque + joint angles**로 구성된다.
- 저자들은 이 단계에는 **visual perception이나 object model을 제공하지 않는다**고 명시한다.
- 3개 timestep history를 사용하며, 저자는 이 이력이 object surface shape를 특징짓는 데 도움이 될 수 있다고 설명한다.
- Modality ablation에서 joint angle only, joint angle+tactile, joint angle+tactile+torque를 비교하며 **세 modality를 모두 사용한 정책이 증가하는 task difficulty에 가장 안정적**이었다.
- GRU가 MLP보다 우수했고 저자들은 historical interaction information의 활용을 이유로 든다.
- 후속 연구로 in-hand manipulation, domain randomization 확대, 초기 grasp를 스스로 찾기 위한 vision 통합을 제시한다.

### N3. Luo et al., 2026

- 원문: [arXiv:2606.11767](https://arxiv.org/abs/2606.11767)
- 배포 시에는 **proprioception과 Binary tactile만** 사용하며 object Pose·Shape를 직접 제공하지 않는다.
- 저자들은 flat Binary activation만으로는 tactile site의 위치가 표현되지 않는다고 지적하고, 각 bit에 **현재 손 자세로부터 FK 계산한 3D sensor position**을 결합한다.
- 여기에 16-frame history를 사용한다.
- 실행 입력을 단순하게 유지하는 대신, 학습에서는 정보 사용이 강하다.
  - PPO expert: Actor는 deployable observation만, **Critic과 Reward는 privileged simulator quantities** 사용.
  - Tactile encoder pretraining: object/hand point cloud, object pose, robot configuration, contact label을 simulator-only supervision으로 사용.
- 저자들은 sparse binary contact만으로 직접 imitation policy를 학습하기 어렵다고 명시한다.
- 실물 실패 분석에서는 **불완전한 tactile coverage와 spatial ambiguity**가 empty grasp, unsafe configuration, slip에 연결될 수 있다고 분석하며, 향후 full-hand tactile, shear/slip sensing, richer tactile representation 등을 제시한다.

### N4. Ahn et al., 2026

- 원문: [arXiv:2607.14842](https://arxiv.org/abs/2607.14842)
- Binary fingertip contact만 쓰지 않고, 모든 관절의 q/qdot, 일부 관절의 proximal 3-axis F/T, 4-step history, RGB-D visual feature를 결합한다.
- 또한 **known object CAD model**과 hand-eye calibration을 가정한다.
- 즉 Sparse/Binary Haptic은 전체 object state를 독립적으로 복원하는 입력이라기보다, **visual pose tracker의 occlusion 문제를 보완하는 modality**로 사용된다.
- 저자들은 sparse haptic을 flat vector로 합치면 sensing site 간 kinematic/spatial relation이 사라진다고 지적하고, URDF-aware finger-level representation을 사용한다.
- 중요한 반대 근거도 있다. inference에서 haptic 값을 0으로 만든 ablation에서도 성능 이득 일부가 유지되어, 이 논문의 이득은 **센서 값 자체뿐 아니라 structured encoder의 inductive bias**에서도 발생했다고 저자들이 분석한다.
- 한계로 단일 pencil-shaped object 중심의 정량 평가와 tracking drift를 들며, 다양한 물체·실물 정량 평가와 temporal regularization/re-initialization을 후속 과제로 제시한다.

## 2.1.4. 이번 조사에서 확인된 보완 패턴

| 물체 정보 조건 | 확인된 보완 방식 | 해당 신규 연구 |
| --- | --- | --- |
| **Pose Tracking 제공** | Binary tactile을 독립적인 object-state source로 쓰지 않고, 현재 object kinematics 및 proprioception에 추가 | N1 |
| **Initial만 제공** | 초기 visual grasp 이후 Binary contact + quantized load + proprioception + short history로 closed-loop 조작 | N2 |
| **Pose·Shape 모두 미제공** | Binary contact를 kinematic sensor position으로 grounding하고 history를 사용. 학습 때는 privileged geometry/state supervision을 적극 활용 | N3 |
| **Pose Tracking + Known Shape** | Binary contact를 sparse F/T·proprioception·history·RGB-D와 융합하고 CAD/URDF의 구조적 prior 사용 | N4 |

## 2.1.5. Research Motivation에 반영할 수 있는 결론

이번 신규 조사에서 가장 명확한 결과는 **“저차원/Binary tactile 연구가 단순 Binary contact만으로 조작 상태를 모두 판단한다”는 구조가 일반적이지 않다**는 점이다.

확인한 연구들은 크게 다음 방식으로 부족한 정보를 보완한다.

1. **현재 물체 Pose·속도를 정책에 직접 계속 제공한다.** — N1
2. **초기 Vision으로 시작 조건만 만든 뒤, Binary tactile에 load cue·proprioception·history를 함께 사용한다.** — N2
3. **실행에서는 Object Pose/Shape를 제거하되, kinematic grounding·history와 simulator privileged supervision을 사용한다.** — N3
4. **Sparse haptic을 독립적으로 사용하지 않고 Vision tracking·known CAD·F/T·proprioception과 융합한다.** — N4

따라서 본 연구의 (2) → (2-1) 논리는 다음처럼 강화하는 것이 적절하다.

> **영역별 Binary tactile은 접촉 발생 영역을 단순하게 표현하지만, 물체 상태와 상호작용 원인을 모두 직접 제공하지 않는다. 기존의 저차원 촉각 기반 연구들도 현재 물체 상태, load-related signal, proprioception, temporal history, kinematic prior 또는 학습 시 privileged geometric information을 함께 사용한다. 따라서 초기 Pose 이후 object tracking과 geometry를 제공하지 않는 Sweeping에서는, Binary tactile에서 제외된 정보 중 실제 행동 조절에 필요한 정보를 어떤 추가 센싱으로 보완할지 별도로 설계할 필요가 있다.**

이 결과는 **F/T를 추가하면 자동으로 Sweeping 성능이 향상된다는 증거는 아니다.** 현재 조사로 뒷받침되는 것은 “축약 촉각을 사용할 때 다른 상태·센서·시간적 정보가 함께 사용되는 사례가 존재하고, 일부 연구에서는 그 추가 modality 또는 history의 효과를 ablation으로 확인했다”는 범위다. 손목 F/T가 본 연구에서 그 부족분을 얼마나 보완하는지는 별도의 센서 ablation으로 검증해야 한다.

## 참고문헌

1. Melnik, A., Lach, L., Plappert, M., Korthals, T., Haschke, R., & Ritter, H. (2021). *Using Tactile Sensing to Improve the Sample Efficiency and Performance of Deep Deterministic Policy Gradients for Simulated In-Hand Manipulation Tasks*. Frontiers in Robotics and AI, 8, 538773. https://doi.org/10.3389/frobt.2021.538773
2. Liang, H., Cong, L., Hendrich, N., Li, S., Sun, F., & Zhang, J. (2022). *Multifingered Grasping Based on Multimodal Reinforcement Learning*. IEEE Robotics and Automation Letters, 7(2), 1174–1181. https://doi.org/10.1109/LRA.2021.3138545
3. Luo, S., Huang, X., Xu, Z., Li, W., Jiao, Z., & Xiao, C. (2026). *Blind Dexterous Grasping via Real2Sim2Real Tactile Policy Learning*. arXiv:2606.11767. https://arxiv.org/abs/2606.11767
4. Ahn, C., Lee, J., Park, S., & Hwang, D. (2026). *KineFuse: Kinematic-Aware Haptic Fusion for In-Hand Occluded-Object Pose Tracking*. arXiv:2607.14842. https://arxiv.org/abs/2607.14842
