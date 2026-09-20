# ICRA 2024 후보 논문 선별 — 축약 촉각 보완 구조와 F/T·촉각 역할 분담

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](README.md) · [Research Motivation](../../presentation/01_Research_Motivation.md)

## 1. 조사 목적

사용자 제공 ICRA 2024 CSV의 **263개 레코드**를 대상으로 제목과 초록을 확인하여, 현재 연구의 다음 두 문헌조사 질문과 연결될 가능성이 있는 논문을 넓게 선별했다.

- **물체 정보의 제공 조건과 축약 촉각의 보완 구조**
  - Object Pose·Shape가 Tracking / Initial / 미제공 중 어떤 형태로 주어지는가?
  - 갱신되지 않거나 제공되지 않는 정보를 tactile, F/T, proprioception, observation/action history, 별도 state estimation, privileged information 등으로 어떻게 보완하는가?
  - tactile을 Binary 또는 저차원 표현으로 축약할 때 어떤 정보가 남고 어떤 정보가 제거되는가?

- **F/T 단독 사용의 한계와 촉각의 필요성**
  - force 또는 wrench 정보가 실제 manipulation에서 어떤 상태를 제공하는가?
  - force 기반 방법이 contact state, geometry, pose, physical property 등의 추가 정보에 의존하는가?
  - tactile과 force sensing을 함께 사용할 때 두 modality가 어떤 역할을 분담하는가?

이 문서는 **제목·초록 단계의 1차 선별 결과**다. 관련 가능성이 조금이라도 있으면 남기는 방향으로 선별했다. 초록이 policy observation, reward, critic input, sensor preprocessing 또는 실제 force sensor 구성을 설명하지 않는 경우에는 이를 추정하지 않는다.

---

# 2. 최우선 정독 후보

## 2.1. Touch-Based Manipulation with Multi-Fingered Robot using Off-policy RL and Temporal Contrastive Learning

**저자:** N. Morihira; P. Deo; M. Bhadu; A. Hayashi; T. Hasegawa; S. Otsubo; T. Osa

**선별 이유:** tactile manipulation에서 contact와 non-contact가 반복되기 때문에 **partial observability를 명시적으로 문제로 정의**하고, observation/action history를 고려해야 한다고 설명한다. temporal contrastive model을 이용해 history에서 task-related latent representation을 학습한다. 현재 연구에서 단일 시점 Binary tactile + F/T가 충분하지 않을 경우 **sensor/action history로 부족한 상태 정보를 보완하는 근거**로 가장 직접적인 후보 중 하나다.

**원문에서 확인할 핵심:** tactile signal의 표현, history window 또는 recurrent structure, proprioception 포함 여부, object pose·shape 제공 조건, critic의 privileged input 여부.

## 2.2. Symmetry-aware Reinforcement Learning for Robotic Assembly under Partial Observability with a Soft Wrist

**저자:** H. Nguyen; T. Kozuno; C. C. Beltran-Hernandez; M. Hamaya

**선별 이유:** 기존 peg-in-hole 연구가 peg-to-hole pose를 외부 setup이나 estimator로 제공하는 fully observable formulation에 의존한다고 지적하고, 본 연구는 **haptic + proprioceptive signal만 사용하는 memory-based agent**를 학습한다. 현재 연구의 Initial-only vision 이후 contact sensing으로 조작을 이어가는 구조와 매우 가깝다.

**원문에서 확인할 핵심:** haptic signal의 실제 구성, soft wrist에서 측정하는 값, memory 구조, reward/critic에서 GT relative pose 사용 여부, state-based agent와의 정확한 비교 조건.

## 2.3. Masked Visual-Tactile Pre-training for Robot Manipulation

**저자:** Q. Liu; Q. Ye; Z. Sun; Y. Cui; G. Li; J. Chen

**선별 이유:** tactile glove에서 얻은 **20개의 sparse binary tactile signal**을 touch state token으로 사용한다. visual token과 binary tactile token을 fusion하며 downstream manipulation RL에 적용한다. 현재 연구의 **영역별 Binary tactile 표현**과 가장 직접적으로 비교 가능한 ICRA 2024 사례다.

**원문에서 확인할 핵심:** 20개 binary signal의 sensor placement와 threshold, tactile-only/vision-only ablation, binary tactile이 제공하는 locality, downstream policy에서 object pose나 geometry를 별도로 주는지.

## 2.4. See to Touch: Learning Tactile Dexterity through Visual Incentives

**저자:** I. Guzey; Y. Dai; B. Evans; S. Chintala; L. Pinto

**선별 이유:** 저자들은 **tactile sensing alone으로는 object spatial configuration을 충분히 reasoning하기 어렵다**고 명시한다. tactile-based policy를 사용하되 visual representation으로 reward를 구성하여 학습한다. 현재 조사 질문인 **축약 또는 tactile-only observation에서 무엇이 부족하고 다른 정보가 무엇을 보완하는가**를 직접 검토할 수 있다.

**원문에서 확인할 핵심:** execution policy의 실제 observation, vision이 reward에만 사용되는지, tactile representation, spatial configuration 정보가 부족하다는 근거와 ablation.

## 2.5. Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation

**저자:** L. Tao; J. Zhang; Q. Zheng; X. Zhang

**선별 이유:** asymmetric actor-critic에서 simulation의 rich feature를 real-world에서 접근 가능한 feature로 줄이는 문제를 정면으로 다룬다. actor가 critic과 동일한 rich feature에서 시작한 뒤 **hard-to-extract feature를 단계적으로 제거**하며, 실제 in-hand manipulation에서는 selected tactile feature를 줄인 상태에서도 task를 수행한다.

현재 연구의 **어떤 정보를 actor에 남기고 어떤 정보를 training-only로 둘 것인가**, 그리고 sensor information 축약이 학습 난도와 성능에 어떤 영향을 미치는가를 확인하는 데 매우 중요하다.

## 2.6. TEXterity: Tactile Extrinsic deXterity

**저자:** A. Bronars; S. Kim; P. Patre; A. Rodriguez

**선별 이유:** robot kinematics와 image-based tactile sensor를 결합하여 **object pose를 추정하고 추적하면서 동시에 조작**한다. visual occlusion 상황에서 tactile 정보를 단순 reactive signal이 아니라 명시적 pose estimation에 사용하는 사례다.

현재 연구가 explicit object pose estimator를 사용하지 않는 방향이라면, 이 논문은 **tactile로 pose를 복원하는 접근과 pose를 직접 출력하지 않고 policy 내부에서 처리하는 접근**을 비교하는 기준이 된다.

## 2.7. Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning

**저자:** E. Su; C. Jia; Y. Qin; W. Zhou; A. Macaluso; B. Huang; X. Wang

**기존 상세 노트:** [Sim2Real Tactile Manipulation](../papers/2024-su-sim2real-tactile-manipulation.md)

**선별 이유:** unknown object manipulation을 tactile-based RL로 수행하며, 서로 다른 tactile representation이 real-robot transfer에 어떤 영향을 주는지 비교한다. 기존 상세 정독에서 RGB·Diff·Binary representation과 Binary contact pattern의 Sim-to-Real 특성을 이미 확인한 논문으로, 현재 **Binary tactile 선택의 직접 근거**에 해당한다.

<a id="icra24-zhao-unknown-object-retrieval"></a>

## 2.8. Unknown Object Retrieval in Confined Space through Reinforcement Learning with Tactile Exploration

**저자:** X. Zhao; W. Liang; X. Zhang; C. M. Chew; Y. Wu

**상세 노트:** [2024 · Zhao et al.](../papers/2024-zhao-unknown-object-retrieval.md)

**선별 이유:** conventional vision이 적합하지 않은 confined space에서 tactile-sensorized tool의 **multi-point contact sensing**을 이용한다. 물체의 physical property에 대한 prior knowledge 없이 RL로 manipulation을 학습한다. 현재 연구의 **물체 물성이 미제공인 경우 tactile interaction으로 행동을 적응시키는 구조**와 연결된다.

**원문 정독 보완:** XELA uSPa44의 4×4×3축 force array를 그대로 입력하지 않고, column별 normal-force max 4D + x-shear 대표값 4D + 30 Hz 초과 FFT feature 1D의 **9D tactile-only actor observation**으로 축약한다. 실물 SAC 학습에서 object progress reward는 OptiTrack으로 계산하지만 evaluation policy는 tactile만 사용한다. continuous planar displacement와 contact recovery용 parameterized backward primitive를 결합하며, 12개 unseen test object에서 90% success를 보고한다.

## 2.9. Few-Shot Learning of Force-Based Motions From Demonstration Through Pre-training of Haptic Representation

**저자:** M. Y. Aoyama; J. Moura; N. Saito; S. Vijayakumar

**선별 이유:** 저자들은 contact-rich task에서 **force sensing이 manipulated object의 physical property에 맞게 motion을 적응시키는 데 필수적인 역할**을 한다고 명시한다. haptic representation encoder를 pre-train하고, 서로 다른 stiffness와 surface friction을 가진 sponge wiping에 적용한다.

현재 연구에서 F/T를 단순 contact detector가 아니라 **load response와 hidden physical property 차이를 반영하는 연속 정보**로 사용하는 논리를 보강할 수 있다.

**주의:** 초록만으로 wrist 6-axis F/T인지 다른 force sensing인지 확정하지 않는다.

<a id="icra24-wu-1khz-tactile-insertion"></a>

## 2.10. 1 kHz Behavior Tree for Self-adaptable Tactile Insertion

**저자:** Y. Wu; F. Wu; L. Chen; K. Chen; S. Schneider; L. Johannsmeier; Z. Bing; F. J. Abu-Dakka; A. Knoll; S. Haddadin

**상세 노트:** [2024 · Wu et al.](../papers/2024-wu-1khz-tactile-insertion.md)

**선별 이유:** 기존 force-domain wiggle motion이 **변화하는 contact state에 따라 behavior를 바꾸지 못하는 한계**를 지적하고, high-frequency tactile data로 contact state를 추정하여 behavior-tree primitive를 전환한다. 단순 force-domain 제어에 tactile contact-state estimation을 추가하는 구조이므로 **force와 tactile의 역할 차이**를 확인할 가치가 높다.

**원문 정독 보완:** 제공된 7쪽 원문에서 별도 taxel/tactile array의 모델·배치·해상도는 제시되지 않는다. 실제 online estimator는 EE z-position·velocity와 joint-torque 기반 force/residual force를 이용해 Searching / Stuck / Unstuck / Aligned를 판정하고, 1 kHz BT가 Wiggle/Push를 전환한다. 따라서 제목의 tactile을 분포형 tactile skin 사용으로 단정하지 않는다.

## 2.11. Robot Synesthesia: In-Hand Manipulation with Visuotactile Sensing

**저자:** Y. Yuan; H. Che; Y. Qin; B. Huang; Z. -H. Yin; K. -W. Lee; Y. Wu; S. -C. Lim; X. Wang

**선별 이유:** contact-rich manipulation에서 visual과 tactile feedback의 fusion을 핵심 문제로 두고, tactile을 point-cloud representation으로 변환하여 vision과 결합한다. vision/touch integration에 대한 comprehensive ablation을 수행한다고 초록에 명시되어 있어 **modality별 역할과 상보성**을 확인하기 좋다.

## 2.12. Generalize by Touching: Tactile Ensemble Skill Transfer for Robotic Furniture Assembly

**저자:** H. Lin; R. Corcodel; D. Zhao

**선별 이유:** robot state, visual indicator, tactile signal을 포함한 trajectory를 사용하여 offline RL을 학습하고, tactile feedback을 control loop에 포함한다. visual disturbance에 대한 robustness와 tactile ensemble policy의 ablation을 제공하므로 **vision이 불안정한 상황에서 tactile feedback이 어떤 역할을 추가하는지** 확인할 수 있다.

## 2.13. ArrayBot: Reinforcement Learning for Generalizable Distributed Manipulation through Touch

**저자:** Z. Xue; H. Zhang; J. Cheng; Z. He; Y. Ju; C. Lin; G. Zhang; H. Xu

**선별 이유:** 16×16 tactile array를 이용해 **tactile observation만으로 다양한 물체를 이동**시키고, unseen object shape와 physical robot으로 일반화한다. sensor 구조는 본 연구와 다르지만, object pose/vision 없이 spatially distributed touch information만으로 manipulation이 가능한 범위를 확인하는 비교 사례다.

## 2.14. AcTExplore: Active Tactile Exploration on Unknown Objects

**저자:** A. -H. Shahidzadeh; S. J. Yoo; P. Mantripragada; C. D. Singh; C. Fermüller; Y. Aloimonos

**선별 이유:** tactile sensor의 **limited sensing coverage**를 핵심 문제로 명시하고, active exploration으로 tactile data를 누적하여 unknown object의 3D shape를 reconstruct한다. 현재 연구에서도 sensor placement 때문에 일부 접촉이 관측되지 않을 수 있으므로, **불완전한 tactile coverage를 어떻게 다루는가**를 확인하는 데 가치가 있다.

## 2.15. Augmenting Tactile Simulators with Real-like and Zero-Shot Capabilities

**저자:** O. Azulay; A. Mizrahi; N. Curtis; A. Sintov

**선별 이유:** high-resolution tactile sensor의 simulation-to-real gap을 직접 다루며, GAN으로 real-like tactile image를 생성하고 contact positioning을 유지한다. 현재 연구가 Binary tactile을 택하는 Motivation 중 하나가 **고해상도 tactile image의 Sim-to-Real 부담**이므로 직접적인 비교 근거가 된다.

## 2.16. Learning Force Control for Legged Manipulation

**저자:** T. Portela; G. B. Margolis; Y. Ji; P. Agrawal

**선별 이유:** 기존 RL manipulation이 forceful interaction을 암묵적으로 사용하면서도 contact force를 명시적으로 regulate하지 않는 문제를 지적하고, **desired contact force level을 직접 추종하는 RL task formulation**을 제안한다. 현재 sweeping reward에서 excessive load를 억제하면서 필요한 접촉 하중을 유지하려는 설계와 연결된다.

**주의:** 본문에서 실제 force observation과 measurement mechanism을 확인하기 전에는 wrist F/T 기반 연구로 분류하지 않는다.

---

# 3. Object State·History·Privileged Information 조사에 강하게 관련된 후보

## 3.1. Gaussian Mixture Likelihood-based Adaptive MPC for Interactive Mobile Manipulators

**저자:** D. Rakovitis; D. Mronga

**선별 이유:** pushing, carrying, door opening에서 uncertain contact dynamics와 multiple unknown environmental parameters를 다룬다. GMM/GMR이 **proprioceptive measurement를 기반으로 dynamic model parameter를 예측**한다. 물체 물성을 직접 제공하지 않고 interaction response에서 controller parameter를 적응시키는 사례로 볼 수 있다.

## 3.2. GAMMA: Graspability-Aware Mobile MAnipulation Policy Learning based on Online Grasping Pose Fusion

**저자:** J. Zhang; N. Gireesh; J. Wang; X. Fang; C. Xu; W. Chen; L. Dai; H. Wang

**선별 이유:** 여러 시점에서 얻은 grasp pose를 online fusion하여 **temporally consistent grasping observation state**를 RL에 제공한다. 현재 연구에서 Initial object information 이후 갱신이 없을 때와 대비하여, continuous state fusion이 manipulation policy에 어떤 이점을 주는지 확인할 수 있다.

## 3.3. Learning for Deformable Linear Object Insertion Leveraging Flexibility Estimation from Visual Cues

**저자:** M. Li; C. Choi

**선별 이유:** 다양한 Young's modulus와 bending stiffness를 가진 DLO를 다루기 위해 **physical property를 먼저 추정하고 그 추정값에 policy를 condition**한다. simulation에서는 GT flexibility를 이용해 estimator를 학습하고, 실행 중에는 interaction 이후 visual configuration으로 flexibility를 추정한다.

현재 연구가 explicit parameter estimation 없이 F/T/tactile history로 물성 차이에 적응하려는 경우 좋은 대비 사례다.

## 3.4. Learning Extrinsic Dexterity with Parameterized Manipulation Primitives

**저자:** S. -M. Yang; M. Magnusson; J. A. Stork; T. Stoyanov

**선별 이유:** 다양한 weight, shape, friction의 box를 다루면서 object detection이나 pose estimation 없이 **depth perception data만으로 low-level manipulation policy**를 학습한다. 정확한 physical model과 contact dynamics modeling 없이도 interaction을 활용한다는 점에서, state를 직접 명시적으로 주지 않는 manipulation의 비교군이다.

## 3.5. Contact Energy Based Hindsight Experience Prioritization

**저자:** E. Sayar; Z. Bing; C. D’Eramo; O. S. Oguz; A. Knoll

**선별 이유:** touch sensor와 **object displacement**를 함께 이용해 contact-rich experience의 information value를 정의하고 replay priority에 반영한다. tactile alone이 아니라 object motion information과 함께 contact quality를 판단하는 사례이므로, 현재 2.1의 **촉각 축약 + 추가 입력 연결**을 확인하는 후보이다.

## 3.6. Grasp Anything: Combining Teacher-Augmented Policy Gradient Learning with Instance Segmentation to Grasp Arbitrary Objects

**저자:** M. Mosbach; S. Behnke

**선별 이유:** teacher policy는 **object pose information**을 이용해 motor control을 학습하고, 이후 student sensorimotor policy는 object segmentation을 기반으로 학습한다. training 단계와 execution 단계의 정보가 명확히 다르므로 **privileged object state 사용 여부를 분리해서 기록하는 사례**로 중요하다.

## 3.7. RGBManip: Monocular Image-based Robotic Manipulation through Active Object Pose Estimation

**저자:** B. An; Y. Geng; K. Chen; X. Li; Q. Dou; H. Dong

**선별 이유:** manipulation 중 camera viewpoint를 적극적으로 변경하며 **6D object pose를 지속적으로 추정**하고 RL policy가 perception과 manipulation의 trade-off를 조절한다. 현재 연구의 Initial-only object pose 조건과 정반대에 가까운 비교군으로, continuous pose tracking이 제공하는 정보량을 확인하기 좋다.

## 3.8. TWIST: Teacher-Student World Model Distillation for Efficient Sim-to-Real Transfer

**저자:** J. Yamada; M. Rigter; J. Collins; I. Posner

**선별 이유:** simulator에서 쉽게 얻을 수 있는 **state observation을 privileged information으로 teacher world model에 제공**하고, image observation만 받는 student world model로 distillation한다. actor/critic 또는 teacher/student에서 training-only GT 정보를 구분하는 현재 조사 항목과 직접 연결된다.

## 3.9. DeformNet: Latent Space Modeling and Dynamics Prediction for Deformable Object Manipulation

**저자:** C. Li; Z. Ai; T. Wu; X. Li; W. Ding; H. Xu

**선별 이유:** current visual representation만 사용하는 대신 recurrent state-space model로 **latent dynamics를 시간적으로 예측**한다. deformable manipulation이라는 차이는 있지만, current observation에 없는 future/current hidden state를 temporal model로 보완하는 구조를 참고할 수 있다.

## 3.10. DexDLO: Learning Goal-Conditioned Dexterous Policy for Dynamic Manipulation of Deformable Linear Objects

**저자:** S. Zhaole; J. Zhu; R. B. Fisher

**선별 이유:** 동일 framework로 여러 DLO manipulation을 학습하고 **reduced observations에 대한 분석**을 제공한다고 초록에 명시한다. 어떤 observation을 제거해도 policy가 유지되는지 확인하면 현재 sensor input 축약 설계에 참고할 수 있다.

---

# 4. Force/Contact Control 및 비교군으로 확인할 후보

## 4.1. SliceIt! - A Dual Simulator Framework for Learning Robot Food Slicing

**저자:** C. C. Beltran-Hernandez; N. Erbetti; M. Hamaya

**선별 이유:** 서로 다른 material property에 적응하면서 contact force를 줄이는 compliant RL policy를 학습한다. **물성이 달라도 필요한 interaction을 수행하면서 과도한 force를 억제하는 reward/control 구조**를 확인할 수 있다.

**주의:** 초록만으로 force sensor 종류와 policy observation을 확정할 수 없다.

## 4.2. A Reinforcement Learning-based Control Strategy for Robust Interaction of Robotic Systems with Uncertain Environments

**저자:** D. Sacerdoti; F. Benzi; C. Secchi

**선별 이유:** unmodeled interaction에서 passivity-based control과 online DRL을 결합해 task requirement를 추정하고 controller를 적응시킨다. uncertain contact interaction을 안정적으로 다루는 방법론 후보이다.

**주의:** 초록에는 tactile 또는 wrist F/T input이 명시되지 않는다.

## 4.3. Exploring Transformers and Visual Transformers for Force Prediction in Human-Robot Collaborative Transportation Tasks

**저자:** J. E. Domínguez-Vidal; A. Sanfeliu

**선별 이유:** 여러 입력에서 향후 human force를 예측하고 입력별 ablation을 제공한다. 과업은 다르지만 **force와 motion state 사이의 temporal relationship을 학습하여 future interaction을 예측**하는 사례로 history 기반 wrench processing 관점에서 참고할 수 있다.

## 4.4. HAGrasp: Hybrid Action Grasp Control in Cluttered Scenes using Deep Reinforcement Learning

**저자:** K. -T. Song; H. -H. Chen

**선별 이유:** complete workspace point cloud를 사용해 grasp pose estimation, end-effector pose evaluation, motion planning을 하나의 closed-loop RL model에 통합한다. 현재 연구처럼 object state를 contact sensing으로 간접 처리하는 것이 아니라 **rich geometric observation을 지속적으로 제공하는 구조**의 비교군이다.

## 4.5. Dual-Critic Deep Reinforcement Learning for Push-Grasping Synergy in Cluttered Environment

**저자:** J. Zhong; Y. W. Wong; J. Jin; Y. Song; X. Yuan; X. Chen

**선별 이유:** cluttered environment에서 pushing을 수행하지만 current state는 **visual interpretation에서 생성**된다. contact sensor 없이 visual state를 기반으로 pushing action을 선택하는 비교군으로, 현재 blind/initial-only 조건과의 차이를 확인할 수 있다.

## 4.6. Mastering Stacking of Diverse Shapes with Large-Scale Iterative Reinforcement Learning on Real Robots

**저자:** T. Lampe; A. Abdolmaleki; S. Bechtle; S. H. Huang; J. Tobias Springenberg; M. Bloesch; O. Groth; R. Hafner; T. Hertweck; M. Neunert; M. Wulfmeier; J. Zhang; F. Nori; N. Heess; M. Riedmiller

**선별 이유:** simulator나 demonstration 없이 **pixels에서 end-to-end로 real-robot manipulation**을 학습한다. tactile/F/T 없이도 가능한 manipulation 범위를 확인하는 비교 사례다.

## 4.7. 6-DoF Closed-Loop Grasping with Reinforcement Learning

**저자:** S. Herland; K. Bach; E. Misimi

**선별 이유:** eye-in-hand RGB-D visual observation만으로 continuous 6-DoF grasp action을 생성하고 zero-shot sim-to-real transfer를 수행한다. tactile/F/T가 없는 vision-only closed-loop manipulation의 비교군으로 사용할 수 있다.

## 4.8. Self-supervised Learning for Joint Pushing and Grasping Policies in Highly Cluttered Environments

**저자:** Y. Wang; K. Mokhtar; C. Heemskerk; H. Kasaei

**선별 이유:** dense clutter에서 pushing과 grasping을 joint RL로 수행한다. 초록에는 tactile/F/T가 명시되지 않으므로, **cluttered pushing을 visual/state 기반으로 해결하는 접근**과 현재 contact-driven sweeping을 비교하기 위한 후보로 남긴다.

---

# 5. 우선 정독 순서

현재 Research Motivation의 논리를 보강하는 목적에서는 다음 순서로 원문을 확인하는 것이 효율적이다.

1. **Touch-Based Manipulation with Multi-Fingered Robot using Off-policy RL and Temporal Contrastive Learning**
   - tactile partial observability와 observation/action history의 필요성을 직접 다룬다.

2. **Symmetry-aware Reinforcement Learning for Robotic Assembly under Partial Observability with a Soft Wrist**
   - external pose estimator 없이 haptic + proprioception + memory로 contact-rich task를 수행한다.

3. **Masked Visual-Tactile Pre-training for Robot Manipulation**
   - 20개의 sparse binary tactile touch-state signal을 직접 사용한다.

4. **See to Touch: Learning Tactile Dexterity through Visual Incentives**
   - tactile-only observation에서 spatial configuration 정보가 부족할 수 있음을 직접 문제로 제시한다.

5. **Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation**
   - rich simulation state와 deployable sensor observation의 경계를 체계적으로 줄인다.

6. **Few-Shot Learning of Force-Based Motions From Demonstration Through Pre-training of Haptic Representation**
   - force sensing과 object physical property adaptation의 연결을 확인할 수 있다.

7. **1 kHz Behavior Tree for Self-adaptable Tactile Insertion**
   - force-domain motion에 tactile contact-state estimation을 추가하는 역할 분담을 확인할 수 있다.

8. **TEXterity: Tactile Extrinsic deXterity**
   - visual occlusion에서 tactile + kinematics로 explicit object pose를 추정하는 대안 구조를 확인할 수 있다.

---

# 6. ICRA 2024 선별에서 얻은 조사 방향

ICRA 2024 후보군에서는 현재 Research Motivation의 2.1에 필요한 근거가 상당히 직접적으로 나타난다.

첫째, **tactile observation 자체도 부분관측일 수 있으며 history가 필요하다**는 연구가 존재한다. Touch-Based Manipulation은 이를 직접 문제로 정의하고, Symmetry-aware RL은 haptic + proprioception의 memory-based policy를 사용한다.

둘째, **Binary 또는 sparse tactile representation을 실제 manipulation에 사용하는 사례**가 확인된다. Masked Visual-Tactile Pre-training은 sparse binary touch state를 사용하고, 기존에 정독한 Sim2Real Manipulation on Unknown Objects는 Binary tactile image representation의 transfer 특성을 비교한다.

셋째, **tactile만으로 모든 object state를 알 수 있다는 가정도 성립하지 않는다.** See to Touch는 tactile alone이 spatial configuration reasoning에 충분하지 않을 수 있음을 명시하고, TEXterity는 tactile + kinematics를 이용해 별도의 object pose estimator를 구성한다.

넷째, force/haptic 정보는 contact 여부를 넘어 **physical property와 interaction load에 적응하는 정보**로 사용된다. Few-Shot Force-Based Motions는 stiffness와 friction이 다른 물체에 적응하기 위한 haptic representation을 학습하며, Learning Force Control은 desired contact force level 자체를 제어 목표로 둔다.

반면 이번 CSV 선별에서도 **wrist 6-axis F/T만으로 multi-contact/contact-location을 식별할 때의 ambiguity를 직접 분석하는 논문**은 명확하게 확보되지 않았다. 따라서 F/T 단독 관측의 식별 가능성과 한계를 뒷받침하려면 별도의 contact localization / wrench observability / multi-contact estimation 문헌조사가 여전히 필요하다.
