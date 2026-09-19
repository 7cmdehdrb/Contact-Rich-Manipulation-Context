# ICRA 2025 후보 논문 선별 — 축약 촉각 보완 구조와 F/T·촉각 역할 분담

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](README.md) · [Research Motivation](../../presentation/01_Research_Motivation.md)

## 1. 조사 목적

사용자 제공 ICRA 2025 CSV의 **238개 레코드**를 대상으로 제목과 초록을 확인하여, 다음 두 문헌조사 질문과 연결될 가능성이 있는 논문을 넓게 선별했다.

- **물체 정보의 제공 조건과 축약 촉각의 보완 구조**
  - Object Pose·Shape가 Tracking / Initial / 미제공 중 어떤 형태로 주어지는가?
  - 갱신되지 않거나 제공되지 않는 정보를 tactile, F/T, proprioception, history, state estimation, privileged information 등으로 어떻게 보완하는가?
  - 촉각을 Binary 또는 저차원으로 축약할 때 어떤 정보가 남고 사라지는가?

- **F/T 단독 사용의 한계와 촉각의 필요성**
  - F/T만으로 어떤 접촉 정보를 얻을 수 있는가?
  - F/T 기반 방법이 contact point, geometry, single-contact assumption 등의 추가 조건에 의존하는가?
  - tactile과 F/T를 함께 사용할 때 두 센서가 어떤 정보를 분담하는가?

이 문서는 **제목·초록 단계의 1차 선별 결과**다. 본문을 정독하지 않은 논문에 대해서는 policy observation, reward, critic input, sensor preprocessing 등을 확정하지 않는다. 관련 가능성이 조금이라도 있으면 남기는 방향으로 선별했다.

---

# 2. 최우선 정독 후보

## 2.1. Learning In-Hand Translation Using Tactile Skin with Shear and Normal Force Sensing

**저자:** J. Yin; H. Qi; J. Malik; J. Pikul; M. Yim; T. Hellebrekers

**선별 이유:** tactile simulation과 real-world gap 때문에 단순화된 tactile signal이 사용된다는 문제를 직접 언급한다. 저자들은 ternary shear와 binary normal force를 사용하고, 3-axis tactile policy를 shear-only, normal-only, proprioception-only baseline과 비교한다. 현재 연구의 **Binary contact + 추가적인 연속 하중/방향 정보**라는 역할 분담 논리를 검토하는 데 가장 직접적인 후보 중 하나다.

**원문에서 확인할 핵심:** binary normal과 ternary shear의 encoding, object pose·shape 제공 조건, actor/critic의 privileged information, 각 ablation의 정확한 observation 구성.

<a id="icra25-zhang-tactile-role"></a>

## 2.2. The Role of Tactile Sensing for Learning Reach and Grasp

**저자:** B. Zhang; I. Andrussow; A. Zell; G. Martius

**상세 원문 정독:** [2025 · Zhang et al. — The Role of Tactile Sensing for Learning Reach and Grasp](../papers/2025-zhang-role-of-tactile-sensing.md)

**선별 이유:** force-based tactile sensing의 complexity가 RL 학습에 미치는 영향을 체계적으로 비교한다. 초록에서는 imperfect visual perception 아래에서 tactile feature가 학습을 개선하지만, 지나치게 복잡한 tactile input은 학습을 어렵게 만들 수 있다고 보고한다. **촉각 표현을 얼마나 단순화할 것인가**라는 현재 연구 질문과 직접 맞닿아 있다.

**원문 정독 결과:** tactile을 overall binary(B), overall magnitude(M), overall 3D force vector(V), region-wise binary(BK), magnitude(MK), 3D force vector(VK)로 분해하여 비교한다. Perfect vision에서는 tactile의 추가 이점이 거의 없지만, noisy vision에서는 tactile이 성능을 개선하고 특히 **V와 VK가 반복적으로 강한 결과**를 보인다. Sensor-area 실험에서는 local VK에 **concise global force vector V를 추가한 조건이 local-only보다 좋아졌고**, 저자들은 sensing quantity가 단순한 area 증가보다 중요하다고 결론낸다. Binary tactile은 contact를 알려주지만 **internal/external touch ambiguity**가 남는다고 분석한다. 다만 V는 fingertip당 3D overall force vector이며 wrist 6-axis F/T와 동일하지 않다.

## 2.3. LEMMo-Plan: LLM-Enhanced Learning from Multi-Modal Demonstration for Planning Sequential Contact-Rich Manipulation Tasks

**저자:** K. Chen; Z. Shen; Y. Zhang; L. Chen; F. Wu; Z. Bing; S. Haddadin; A. Knoll

**선별 이유:** visual data만으로는 force-related parameter와 condition을 충분히 제공하기 어렵다고 명시하고, human demonstration의 tactile과 force-torque information을 함께 사용한다. Low-level sweeping과 과업 수준은 다르지만, **visual / tactile / F/T가 서로 다른 정보를 제공한다는 역할 분담**을 확인하기 좋은 사례다.

**원문에서 확인할 핵심:** tactile과 F/T의 feature 구성, modality별 ablation, tactile의 spatial information과 F/T의 load information이 실제로 어떻게 사용되는지.

## 2.4. Learning Active Tactile Perception Through Belief-Space Control

**저자:** J.-F. Tremblay; D. Meger; F. R. Hogan; G. Dudek

**선별 이유:** mass, friction, size와 같은 unknown physical property를 interaction을 통해 파악하는 문제를 다룬다. generative world model과 Bayesian filtering으로 physical parameter를 추정한다. **물체 정보를 직접 제공하지 않을 때 interaction과 history로 부족한 정보를 보완하는 구조**를 조사하는 데 적합하다.

**원문에서 확인할 핵심:** observation과 action history, tactile/contact signal의 형태, explicit state estimation과 downstream policy의 연결.

## 2.5. UpViTaL: Unpaired Visual-Tactile Self-Supervised Representation Learning for Dexterous Robotic Manipulation

**저자:** G. Han; Q. Liu; Y. Cui; A. Chen; J. Chen; Q. Ye

**선별 이유:** time-series tactile data에서 temporal tactile representation을 학습한다. 실제 deployment에서는 tactile sensor input을 요구하지 않는 구조이므로 본 연구의 직접적인 sensor fusion 사례는 아니지만, **tactile history가 어떤 representation을 형성할 수 있는지** 확인할 가치가 있다.

<a id="icra25-dadiotis-pushing"></a>

## 2.6. Dynamic Object Goal Pushing with Mobile Manipulators Through Model-Free Constrained Reinforcement Learning

**저자:** I. Dadiotis; M. Mittal; N. Tsagarakis; M. Hutter

**상세 원문 정독:** [2025 · Dadiotis et al. — Dynamic Object Goal Pushing](../papers/2025-dadiotis-dynamic-object-goal-pushing.md)

**선별 이유:** 다양한 mass, material, size, shape를 가진 unknown object를 실제로 pushing하지만 초록에서는 policy가 **object pose를 계속 관측**한다고 명시한다. 따라서 “unknown physical property를 다루는 pushing”이라는 점보다, **continuous pose tracking이 어떤 정보를 대신 제공하는가**를 비교하기 좋은 사례다.

**원문 정독 결과:** actor는 current object pose에서 계산한 EE–object·object–goal 관계, robot proprioception, previous action을 사용한다. **EE–object contact state, object CoM, mass, dimensions, inertia, linear/angular velocity, shape는 critic의 simulation-only privileged information**이다. Reward도 OBB keypoint, object surface reach target, object velocity 등 actor보다 많은 GT state를 사용한다. Hardware에서는 external motion-capture system으로 object와 robot base의 6D pose를 계속 측정한다. F/T·tactile sensor는 제안 actor observation에 사용하지 않는다. Toppling 회피는 object dimensions를 직접 추정한 결과라기보다 **관측되는 object inclination에 반응하여 더 낮은 접촉 위치를 선택하는 행동**으로 설명된다.

## 2.7. Da-Vil: Adaptive Dual-Arm Manipulation with Reinforcement Learning and Variable Impedance Control

**저자:** M. F. Karim; S. Bollimuntha; M. S. Hashmi; A. Das; G. Singh; S. Sridhar; A. K. Singh; N. Govindan; K. M. Krishna

**선별 이유:** interaction force를 관리하면서 task demand에 따라 impedance를 동적으로 조절하는 문제를 다룬다. 다양한 mass와 geometry의 object를 평가하므로 force-aware adaptation과 연결될 가능성이 있다.

**주의:** 초록에는 wrist F/T sensor 또는 force observation이 policy input으로 들어간다고 명시되어 있지 않다. 본문에서 environment feedback과 force sensing 구성을 확인하기 전에는 F/T 기반 연구로 분류하지 않는다.

## 2.8. Impedance Primitive-Augmented Hierarchical Reinforcement Learning for Sequential Tasks

**저자:** A. B. Tahmaz; R. Prakash; J. Kober

**선별 이유:** object pushing, door opening, surface cleaning 등 contact task에서 variable stiffness control을 학습한다. 접촉 상태에 따라 compliance를 바꾸는 구조라면 continuous load information을 action/control에 연결하는 참고 사례가 될 수 있다.

**주의:** 초록만으로는 F/T 또는 tactile observation 사용 여부를 확인할 수 없다.

---

# 3. 물체 정보·History·Privileged Information과 관련된 후보

## 3.1. Privileged-Dreamer: Explicit Imagination of Privileged Information for Rapid Adaptation of Learned Policies

**저자:** M. Byrd; J. Crandell; M. Das; J. Inman; R. Wright; S. Ha

**선별 이유:** unobservable hidden parameter를 limited historical data에서 명시적으로 추정하고 model, actor, critic을 그 추정값에 condition한다. Manipulation 전용은 아니지만 **history를 사용해 현재 관측에 없는 물성·상태를 보완하는 구조**와 매우 가깝다.

## 3.2. Prompt-Responsive Object Retrieval with Memory-Augmented Student-Teacher Learning

**저자:** M. Mosbach; S. Behnke

**선별 이유:** cluttered manipulation에서 imperfect detection의 temporal sequence가 implicit state estimation에 유용한 정보를 제공한다고 명시한다. modality는 vision이지만, **단일 시점 관측이 불완전할 때 history로 state를 보완**하는 사례다.

## 3.3. Integrating Model-Based Control and RL for Sim2Real Transfer of Tight Insertion Policies

**저자:** I. Marougkas; D. M. Ramesh; J. H. Doerr; E. Granados; A. Sivaramakrishnan; A. Boularias; K. E. Bekris

**선별 이유:** simulation에서 plug와 socket의 SE(3) pose를 모두 입력으로 사용하고, 실제 환경에서도 visual SE(3) tracker를 사용한다. contact-rich insertion이지만 **continuous object state tracking을 유지하는 경우**이므로 Tracking / Initial / 미제공 분류의 좋은 비교군이다.

<a id="icra25-chen-vividex"></a>

## 3.4. ViViDex: Learning Vision-Based Dexterous Manipulation from Human Videos

**저자:** Z. Chen; S. Chen; E. Arlaud; I. Laptev; C. Schmid

**상세 원문 정독:** [2025 · Chen et al. — ViViDex](../papers/2025-chen-vividex.md)

**선별 이유:** 먼저 privileged object state를 사용하는 state-based RL policy를 학습하고, successful rollout으로 privileged information 없이 동작하는 visual policy를 다시 학습한다. **학습 전용 GT state와 실행 observation을 분리**하는 사례로 중요하다.

**원문 정독 결과:** state-based PPO는 **robot state + object state**를 입력으로 받고, human-video reference의 hand/object trajectory를 reward에 사용하여 physically plausible rollout을 생성한다. Final visual policy는 이 성공 rollout에서 만든 dataset으로 **robot proprioception + 3D scene point cloud**를 입력받아 BC 또는 3D Diffusion Policy로 학습되며 explicit GT object pose를 입력으로 사용하지 않는다. 다만 point cloud는 매 step 갱신되므로 object geometry·spatial configuration을 online vision으로 계속 관측한다. Real-robot 평가에서도 simulation visual policy를 zero-shot으로 옮기지 않고 object당 5개의 real trajectory를 추가 수집하여 visual policy를 학습한다.

## 3.5. Learning Coordinated Bimanual Manipulation Policies Using State Diffusion and Inverse Dynamics Models

**저자:** H. Chen; J. Xu; L. Sheng; T. Ji; S. Liu; Y. Li; K. Driggs-Campbell

**선별 이유:** historical observation을 이용해 future state를 예측하고 inverse dynamics로 action을 계산한다. explicit object pose tracking을 쓰지 않는 정책에서 **history가 object movement/state change 정보를 어떻게 전달할 수 있는가**를 생각할 때 참고할 수 있다.

## 3.6. IMRL: Integrating Visual, Physical, Temporal, and Geometric Representations for Enhanced Food Acquisition

**저자:** R. Liu; Z. Mahammad; A. Bhaskar; P. Tokekar

**선별 이유:** bounding box와 pose 같은 surface-level geometric information만으로는 다양한 physical property에 대응하기 어렵다는 문제를 제기하고 visual, physical, temporal, geometric representation을 결합한다. **Pose/Shape와 physical interaction information은 서로 다른 정보**라는 논리를 검토하는 데 유용하다.

## 3.7. One-Shot Video Imitation via Parameterized Symbolic Abstraction Graphs

**저자:** J. Wang; K. Liu; D. Guo; Z. Xian; C. G. Atkeson

**선별 이유:** video demonstration만으로는 force와 같은 invisible physical attribute를 포착하기 어렵다고 명시한다. simulation을 이용해 non-geometric, visually imperceptible attribute를 보완한다. **시각 정보만으로 interaction load를 알기 어렵다**는 motivation과 연결된다.

## 3.8. DROP: Dexterous Reorientation via Online Planning

**저자:** A. H. Li; P. Culbertson; V. Kurtz; A. D. Ames

**선별 이유:** contact-rich in-hand manipulation을 수행하지만 vision-based pose estimator를 계속 이용한다. **contact-rich task에서도 continuous visual pose tracking을 가정하는 접근**과 현재 Initial-only vision 조건을 대비하기 좋다.

## 3.9. World Model-Based Perception for Visual Legged Locomotion

**저자:** H. Lai; J. Cao; J. Xu; H. Wu; Y. Lin; T. Kong; Y. Yu; W. Zhang

**선별 이유:** locomotion 연구지만 teacher의 privileged information과 student의 visual input 사이의 information gap을 직접 문제 삼는다. actor/critic, teacher/student, privileged state 사용을 정리할 때 방법론 참고 가치가 있다.

## 3.10. Integrating Learning-Based Manipulation and Physics-Based Locomotion for Whole-Body Badminton Robot Control

**저자:** H. Wang; Z. Shi; C. Zhu; Y. Qiao; C. Zhang; F. Yang; P. Ren; L. Lu; D. Xuan

**선별 이유:** model-based strategy의 privileged information을 IL과 RL training에서 arm policy 학습에 사용한다. 현재 과업과 직접 관련성은 낮지만, **training-only information과 deployment policy의 정보 경계**를 확인하는 사례로 남긴다.

---

# 4. 직접 근거는 약하지만 원문 확인 가치가 있는 후보

## 4.1. Routing Manipulation of Deformable Linear Object Using Reinforcement Learning and Diffusion Policy

**저자:** M. Li; H. Yu; C. Choi

**선별 이유:** unknown friction과 intensive contact가 있는 DLO manipulation에서 RL agent가 rope tension을 낮추도록 학습한다. **필요한 접촉은 유지하면서 과도한 하중을 억제하는 reward formulation** 참고 후보이다.

## 4.2. Variable-Friction In-Hand Manipulation for Arbitrary Objects via Diffusion-Based Imitation Learning

**저자:** Q. Yan; Z. Ding; X. Zhou; A. J. Spiers

**선별 이유:** rich and subtle contact process를 직접 문제로 언급하는 in-hand manipulation 연구다. 초록에는 tactile/F/T sensor가 명시되지 않으므로 본문에서 policy observation과 contact representation을 확인할 후보이다.

## 4.3. Learning a High-Quality Robotic Wiping Policy Using Systematic Reward Analysis and Visual-Language Model Based Curriculum

**저자:** Y. Liu; D. Kang; S. Ha

**선별 이유:** 다양한 curvature와 friction에서 wiping quality와 task completion을 함께 고려하는 reward formulation을 체계적으로 분석한다. 센서 근거보다는 **contact task의 reward 설계 방법** 참고용이다.

## 4.4. Non-Prehensile Shape Manipulation of Elastoplastic Objects With Reinforcement Learning

**저자:** S. Herland; E. Misimi

**선별 이유:** gentle pushing을 수행하면서 object를 sampled boundary coordinates로 표현한다. **Object Shape를 명시적으로 제공하는 pushing 계열 정책**의 비교 사례로 사용할 수 있다.

## 4.5. Hierarchical Visual Policy Learning for Long-Horizon Robot Manipulation in Densely Cluttered Scenes

**저자:** H. Wang; L. Qi; Z. Wang; J. Ren; W. Li; Y. Sun

**선별 이유:** severe occlusion이 존재하는 cluttered scene에서 push/pick/place를 수행하지만 visual observation을 계속 사용한다. **occlusion 상황에서도 지속적 vision을 사용하는 접근**과 현재 연구를 대비하기 좋다.

## 4.6. Language-Guided Object-Centric Diffusion Policy for Generalizable and Collision-Aware Manipulation

**저자:** H. Li; Q. Feng; Z. Zheng; J. Feng; Z. Chen; A. Knoll

**선별 이유:** task-relevant object의 3D point cloud를 policy condition으로 사용한다. **Object/obstacle geometry를 명시적으로 제공하는 조작 정책**과 Initial-only object information 구조를 비교할 수 있다.

## 4.7. DemoStart: Demonstration-Led Auto-Curriculum Applied to Sim-to-Real with Multi-Fingered Robots

**저자:** M. Bauza; J. E. Chen; V. Dalibard; N. Gileadi; R. Hafner; M. F. Martins; J. Moore; R. Pevceviciute; A. Laurens; D. Rao; M. Zambelli; M. Riedmiller; J. Scholz; K. Bousmalis; F. Nori; N. Heess

**선별 이유:** multi-finger manipulation을 수행하지만 deployment policy input은 multiple camera raw pixels와 proprioception이다. **tactile 없이 수행되는 dexterous manipulation**의 비교군으로 확인할 수 있다.

## 4.8. MJPR: Multi-Modal Joint Predictive Representation in Deep Reinforcement Learning

**저자:** Z. Wang; Z. He; Z. Wang; H. He; B. Yang; H. Shi

**선별 이유:** 서로 다른 sensor modality가 complementary information을 생성하도록 joint predictive representation을 학습한다. 향후 **F/T와 tactile의 fusion architecture**를 검토할 때 간접적인 방법론 참고가 가능하다.

## 4.9. Masked Sensory-Temporal Attention for Sensor Generalization in Quadruped Locomotion

**저자:** D. Liu; T. Zhang; J. Yin; S. See

**선별 이유:** sensor-level temporal attention을 사용하여 다양한 proprioceptive sensor combination과 missing information을 처리한다. manipulation은 아니지만 **sensor history와 관측 누락**을 함께 다루는 구조로 참고할 수 있다.

## 4.10. Robust Robot Walker: Learning Agile Locomotion over Tiny Traps

**저자:** S. Zhu; R. Huang; L. Mou; H. Zhao

**선별 이유:** exteroceptive sensor가 tiny obstacle을 충분히 관측하지 못하는 상황에서 proprioception과 contact encoder로 implicit trap representation을 학습한다. **직접 보이지 않는 접촉 상태를 interaction response로 추론**하는 인접 사례다.

## 4.11. Learning Quiet Walking for a Small Home Robot

**저자:** R. Watanabe; T. Miki; F. Shi; Y. Kadokawa; F. Bjelonic; K. Kawaharazuka; A. Cramariuc; M. Hutter

**선별 이유:** foot contact sensor와 varying PD gain을 결합해 contact velocity와 충격을 낮춘다. 저차원 contact sensing이 controller adaptation에 연결되는 인접 사례다.

## 4.12. Physics-Aware Robotic Palletization With Online Masking Inference

**저자:** T. Zhang; Z. Wu; Y. Chen; Y. Wang; B. Liang; S. Moura; M. Tomizuka; M. Ding; W. Zhan

**선별 이유:** box size뿐 아니라 density와 rigidity 같은 intrinsic physical property가 실제 task에 중요하다고 지적한다. tactile/F/T 연구는 아니지만 **Pose/Shape만으로 physical interaction 결과를 설명하기 어렵다**는 배경 논리와 연결된다.

## 4.13. Diff-Dagger: Uncertainty Estimation With Diffusion Policy for Robotic Manipulation

**저자:** S.-W. Lee; X. Kang; Y.-L. Kuo

**선별 이유:** stacking, pushing, plugging에서 policy uncertainty를 이용해 expert intervention을 요청한다. tactile/F/T 기반 판단은 아니지만, **rollout 중 현재 상황의 불확실성을 감지하고 상위 개입을 요청하는 구조**의 대안 사례다.

---

# 5. 우선 정독 순서

현재 Research Motivation을 보강하려는 목적에서는 다음 다섯 편을 먼저 확인하는 것이 효율적이다.

1. **Learning In-Hand Translation Using Tactile Skin with Shear and Normal Force Sensing**
   - Binary normal / ternary shear / proprioception ablation이 센서 역할 분담 논리와 가장 직접적으로 연결된다.

2. **The Role of Tactile Sensing for Learning Reach and Grasp**
   - tactile input complexity와 학습 성능의 trade-off를 확인할 수 있다.

3. **Learning Active Tactile Perception Through Belief-Space Control**
   - 미제공 물성 정보를 interaction과 state estimation으로 보완하는 구조를 확인할 수 있다.

4. **LEMMo-Plan**
   - tactile과 F/T가 visual information에 없는 정보를 어떻게 추가하는지 확인할 수 있다.

5. **Dynamic Object Goal Pushing with Mobile Manipulators Through Model-Free Constrained Reinforcement Learning**
   - pushing에서 unknown physical property를 처리하지만 continuous object pose를 제공하는 비교 사례다.

---

# 6. 이번 선별에서 아직 직접 확보되지 않은 근거

이번 CSV의 제목·초록 선별만으로는 다음 질문에 직접 답하는 논문을 명확하게 확보하지 못했다.

> **Wrist F/T만으로 contact location 또는 multi-contact configuration을 추정할 때 어떤 ambiguity가 남으며, tactile contact-region 정보가 이를 어떻게 보완하는가?**

따라서 Research Motivation의 F/T 단독 한계 부분을 보강하려면 ICRA 2025 CSV에 한정하지 않고 다음 범주의 문헌을 별도로 조사해야 한다.

- wrist wrench 기반 contact point localization
- external wrench 기반 multi-contact estimation
- known tool/object geometry를 가정하는 F/T contact estimation
- tactile + wrist F/T sensor fusion
- distributed tactile과 global wrench의 observability 비교
- force/torque 기반 manipulation에서 contact location을 사전에 알고 있다고 가정하는 연구

후속 조사에서는 “F/T가 부족하다”는 결론을 먼저 두지 않고, **F/T만으로 식별 가능한 상태와 식별성이 깨지는 조건을 먼저 확인**한다.
