# ICRA 2023 후보 논문 선별 — 축약 촉각 보완 구조와 F/T·촉각 역할 분담

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](README.md) · [Research Motivation](../../presentation/01_Research_Motivation.md)

## 1. 조사 목적

사용자 제공 ICRA 2023 CSV의 **190개 레코드**를 대상으로 제목과 초록을 확인하여, 현재 연구의 다음 두 문헌조사 질문과 연결될 가능성이 있는 논문을 넓게 선별했다.

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

## 2.1. Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture

**저자:** J. Pitz; L. Röstel; L. Sievers; B. Bäuml

**선별 이유:** external sensor 없이 in-hand reorientation을 수행하면서 object state를 계속 알아야 한다는 문제를 명시하고, policy가 사용할 cube state를 **별도의 deep differentiable particle filter로 추정**한다. 현재 연구의 Initial-only object state 조건에서 tactile·proprioception·history가 object-state 변화를 어떻게 보완할 수 있는지 검토할 때 매우 직접적인 사례다.

**원문에서 확인할 핵심:** particle filter 입력이 tactile, joint state, action history 중 무엇으로 구성되는지, cube state가 policy에 어떤 형태로 제공되는지, state estimator와 policy 학습이 어떻게 분리되는지.

## 2.2. Toward Fine Contact Interactions: Learning to Control Normal Contact Force with Limited Information

**저자:** J. Cui; J. Xu; D. Saldana; J. Trinkle

**선별 이유:** 기존 fine contact control이 object model과 contact location/force 정보를 얻기 위한 expensive sensor에 크게 의존한다고 지적하고, **low-cost information-poor tactile sensor**만으로 normal contact force controller를 학습한다. 현재 연구의 **저차원 tactile 표현으로 어느 수준의 force/contact control까지 가능한가**라는 질문과 직접 연결된다.

**원문에서 확인할 핵심:** information-poor tactile sensor의 실제 출력 형식, force target과 tactile signal의 관계, contact location 정보가 별도로 주어지는지, motion controller와 force controller의 역할 분담.

## 2.3. Seq2Seq Imitation Learning for Tactile Feedback-based Manipulation

**저자:** W. Yang; A. Angleraud; R. S. Pieters; J. Pajarinen; J. -K. Kämäräinen

**선별 이유:** contact modeling, **partial observability**, perception/control noise를 tactile manipulation의 핵심 문제로 정의한다. Seq2Seq model이 먼저 robot-environment interaction sequence를 이용해 partially observable environment state variable을 추정하고, 그 sequence를 다시 control sequence로 변환한다. 현재 연구의 **sensor/action history로 단일 시점 contact observation의 부족함을 보완**하는 논리에 매우 직접적이다.

**원문에서 확인할 핵심:** tactile feedback의 표현, sequence 길이, 추정하는 hidden state, object pose/shape가 실행 시 제공되는지, expert demonstration에만 존재하는 privileged state가 있는지.

## 2.4. Safe Self-Supervised Learning in Real of Visuo-Tactile Feedback Policies for Industrial Insertion

**저자:** L. Fu; H. Huang; L. Berscheid; H. Li; K. Goldberg; S. Chitta

**선별 이유:** insertion을 두 단계로 분리하여, align 단계에서는 **tactile-based grasp pose estimation**, insert 단계에서는 vision-based policy를 사용하고, 별도로 **force-torque sensing을 safe self-supervised data collection에 사용**한다. tactile과 F/T가 같은 역할을 하지 않고 각각 pose estimation과 안전한 interaction 관리에 배치되는 실제 사례이므로 현재 역할 분담 논리와 강하게 연결된다.

**원문에서 확인할 핵심:** tactile signal과 F/T signal의 실제 센서 구성, F/T가 policy observation인지 safety pipeline에만 쓰이는지, tactile pose estimator의 출력과 정책 입력, 각 modality 제거 시 성능 변화.

## 2.5. Demonstration-guided Optimal Control for Long-term Non-prehensile Planar Manipulation

**저자:** T. Xue; H. Girgin; T. S. Lembono; S. Calinon

**선별 이유:** non-prehensile planar manipulation에서 핵심 난점 중 하나로 **continuous/discrete contact configuration, contact point, contact mode를 결정하는 문제**를 명시한다. F/T 논문은 아니지만, contact-rich pushing에서 단순한 전체 하중 외에도 contact configuration 자체가 중요한 상태 변수임을 확인하는 비교 사례다.

## 2.6. Learning Generalizable Pivoting Skills

**저자:** X. Zhang; S. Jain; B. Huang; M. Tomizuka; D. Romeres

**선별 이유:** 다양한 object로 pivoting을 일반화하기 위해 object의 **kinematic feature space를 별도로 학습**하고 그 feature로 policy의 state/action space를 조정한다. 실행 시 한 장의 depth image를 사용한다. 현재 연구에서 Shape를 제공하지 않을 경우 어떤 정보가 사라지는지, 반대로 Shape feature를 직접 주면 어떤 adaptation이 가능한지 비교하기 좋다.

## 2.7. RLAfford: End-to-End Affordance Learning for Robotic Manipulation

**저자:** Y. Geng; B. An; H. Geng; Y. Chen; Y. Yang; H. Dong

**선별 이유:** RL training 과정에서 생성되는 **contact information을 unified representation**으로 사용하여 contact map을 예측한다. 현재 연구의 tactile sensor contact-region 정보와 동일한 표현은 아니지만, contact location을 manipulation representation으로 사용하는 연구로서 참고할 가치가 있다.

**원문에서 확인할 핵심:** contact information이 simulation ground truth인지 실제 sensor-derived signal인지, contact map이 training-only인지 execution policy에도 제공되는지.

## 2.8. Online augmentation of learned grasp sequence policies for more adaptable and data-efficient in-hand manipulation

**저자:** E. K. Gordon; R. S. Zarrin

**선별 이유:** test time에 tool property, desired trajectory, desired application force가 training과 달라질 수 있다는 문제를 명시하고, domain knowledge와 online lookahead로 RL policy를 보완한다. **물체/도구 physical property와 요구 force가 바뀌는 상황에서 policy가 무엇을 알아야 하는가**를 검토하는 데 유용하다.

## 2.9. H-SAUR: Hypothesize, Simulate, Act, Update, and Repeat for Understanding Object Articulations from Interactions

**저자:** K. Ota; H. -Y. Tung; K. A. Smith; A. Cherian; T. K. Marks; A. Sullivan; A. Kanezaki; J. B. Tenenbaum

**선별 이유:** vision만으로 object articulation을 확정하기 어려운 상황에서 action을 수행하고, 결과를 관측하여 hypothesis를 업데이트한다. tactile/F/T 연구는 아니지만 **초기 정보만으로 알 수 없는 object property를 interaction history로 줄여 나가는 구조**가 현재 문제와 유사하다.

## 2.10. Feature Extraction for Effective and Efficient Deep Reinforcement Learning on Real Robotic Platforms

**저자:** P. Böhm; P. Pounds; A. C. Chapman

**선별 이유:** real-world sensor measurement의 single snapshot은 dynamics 때문에 **partial state observability만 제공하므로 observation history가 필요하다**고 명시한다. 이전 observation을 GRU encoding하고 current raw observation과 결합한다. manipulation 전용 논문은 아니지만, F/T/tactile history를 observation에 추가하는 설계 근거로 참고할 수 있다.

## 2.11. Variable Admittance Interaction Control of UAVs via Deep Reinforcement Learning

**저자:** Y. Feng; C. Shi; J. Du; Y. Yu; F. Sun; Y. Song

**선별 이유:** external interaction force가 존재하는 unknown environment에서 RL로 admittance parameter를 조정한다. manipulation 과업은 아니지만, **연속 force feedback을 controller adaptation에 연결하는 구조**를 확인할 수 있다.

**주의:** 초록만으로 실제 force sensing 방식이나 observation 구성을 확정할 수 없다.

## 2.12. Immersive Demonstrations are the Key to Imitation Learning

**저자:** K. Li; D. Chappell; N. Rojas

**선별 이유:** fingertip-level과 palm-level force feedback을 human demonstrator에게 제공했을 때 demonstration force와 trajectory quality가 어떻게 달라지는지 비교한다. 실행 policy에는 force data가 직접 들어가지 않지만, **interaction force 정보가 manipulation quality에 실질적인 영향을 준다**는 간접 근거로 확인할 가치가 있다.

## 2.13. Force control for Robust Quadruped Locomotion: A Linear Policy Approach

**저자:** A. Shirwatkar; V. K. Kurva; D. Vinoda; A. Singh; A. Sagi; H. Lodha; B. G. Goswami; S. Sood; K. Nehete; S. Kolathaya

**선별 이유:** manipulation 연구는 아니지만, **centroidal wrench와 개별 foot contact information을 분리해 사용**하고 contact information을 기반으로 wrench를 각 접촉점의 ground reaction force로 분배한다. global wrench와 local contact-state 정보가 서로 다른 역할을 가진다는 구조적 비교 사례다.

---

# 3. Object State·History·Privileged Information과 관련된 후보

## 3.1. DeXtreme: Transfer of Agile In-hand Manipulation from Simulation to Reality

**저자:** A. Handa; A. Allshire; V. Makoviychuk; A. Petrenko; R. Singh; J. Liu; D. Makoviichuk; K. Van Wyk; A. Zhurkevich; B. Sundaralingam; Y. Narang

**선별 이유:** robust dexterous policy와 별도로 **real-time object pose estimator**를 구성하고, vision-based policy를 privileged motion-capture state를 받는 policy와 비교한다. contact-rich task에서도 continuous object state tracking을 유지하는 대표적인 비교 사례다.

## 3.2. Learning on the Job: Self-Rewarding Offline-to-Online Finetuning for Industrial Insertion of Novel Connectors from Vision

**저자:** A. Nair; B. Zhu; G. Narayanan; E. Solowjow; S. Levine

**선별 이유:** 기존 insertion algorithm이 precise localization과 carefully managed setup에 의존하는 문제를 지적하고, unseen connector에 대해 visual policy를 online finetuning한다. tactile/F/T 없이 **localization과 visual representation으로 insertion uncertainty를 처리하는 접근**과 현재 연구를 비교할 수 있다.

## 3.3. Robotic Table Wiping via Reinforcement Learning and Whole-body Trajectory Optimization

**저자:** T. Lew; S. Singh; M. Prats; J. Bingham; J. Weisz; B. Holson; X. Zhang; V. Sindhwani; Y. Lu; F. Xia; P. Xu; T. Zhang; J. Tan; M. Gonzalez

**선별 이유:** crumbs와 spills의 **uncertain latent dynamics를 high-dimensional visual observation으로 reasoning**하며 wiping action을 계획한다. contact-rich wiping에서도 continuous visual state를 사용하는 비교군으로, contact feedback 없이 latent dynamics를 다루는 접근을 확인할 수 있다.

## 3.4. Learning Visual Locomotion with Cross-Modal Supervision

**저자:** A. Loquercio; A. Kumar; J. Malik

**선별 이유:** proprioception-only blind policy가 upcoming geometry를 알 수 없어 한계가 있고, vision을 추가해 이를 보완한다. 또한 time-shifted proprioception으로 vision module을 supervise한다. locomotion 연구지만 **한 modality에서 사라진 정보를 다른 modality가 보완하고, 시간차 sensor information을 학습에 사용하는 구조**를 참고할 수 있다.

## 3.5. Using Memory-Based Learning to Solve Tasks with State-Action Constraints

**저자:** M. Verghese; C. Atkeson

**선별 이유:** state에 따라 가능한 action이 불연속적으로 바뀌는 sequential task에서 memory-based learning을 사용한다. sensory partial observability를 직접 다루지는 않지만, **현재 상태 하나만으로 action을 결정하기 어려운 sequential decision problem에서 memory를 사용하는 사례**로 남긴다.

## 3.6. Learnable Tegotae-based Feedback in CPGs with Sparse Observation Produces Efficient and Adaptive Locomotion

**저자:** C. Herneth; M. Hayashibe; D. Owaki

**선별 이유:** sparse observation과 minimal feedback information만으로 adaptive locomotion을 학습한다. manipulation과 직접 관련성은 낮지만, **관측을 축약하면서도 interaction reaction을 이용해 adaptive behavior를 학습하는 사례**로 참고할 수 있다.

## 3.7. Learning Pre-Grasp Manipulation of Flat Objects in Cluttered Environments using Sliding Primitives

**저자:** J. Wu; H. Wu; S. Zhong; Q. Sun; Y. Li

**선별 이유:** cluttered environment에서 flat object를 sliding primitive로 이동시키며 novel object로 일반화한다. 초록에서는 tactile/F/T를 사용하지 않고 object-centric visual/state representation으로 action parameter를 선택한다. **cluttered sliding을 vision/state 기반으로 해결하는 비교군**으로 적합하다.

## 3.8. Reinforcement Learning Based Pushing and Grasping Objects from Ungraspable Poses

**저자:** H. Zhang; H. Liang; L. Cong; J. Lyu; L. Zeng; P. Feng; J. Zhang

**선별 이유:** object를 table edge까지 pushing한 뒤 grasping하는 model-free RL 연구이며, input scenario image에서 VAE feature를 추출한다. **pushing을 tactile/F/T 없이 visual observation으로 수행하는 비교 사례**다.

---

# 4. Contact-rich Manipulation의 비교군 및 간접 참고 후보

## 4.1. Dexterous Manipulation from Images: Autonomous Real-World RL via Substep Guidance

**저자:** K. Xu; Z. Hu; R. Doshi; A. Rovinsky; V. Kumar; A. Gupta; S. Levine

**선별 이유:** contact-rich dexterous manipulation을 다루지만 system은 **vision-based**이며 user가 image-based subtask example을 제공한다. tactile/F/T 없이 real-world RL로 contact-rich task를 수행하는 강한 비교군이다.

## 4.2. Dexterous Imitation Made Easy: A Learning-Based Framework for Efficient Dexterous Manipulation

**저자:** S. P. Arunachalam; S. Silwal; B. Evans; L. Pinto

**선별 이유:** single RGB camera만으로 demonstration을 수집하고 complex in-hand manipulation을 학습한다. tactile/F/T 없이 가능한 dexterous manipulation 범위를 확인하는 비교군이다.

## 4.3. Mechanical Intelligence for Prehensile In-Hand Manipulation of Spatial Trajectories

**저자:** Q. Lu; Z. Gan; X. Wang; G. Bai; Z. Zhang; N. Rojas

**선별 이유:** simple low-level non-position control과 underactuated mechanical design으로 open-loop in-hand manipulation을 수행한다. sensing을 늘리는 대신 **mechanical structure와 prior design으로 uncertainty를 흡수하는 대안 접근**으로 참고할 수 있다.

## 4.4. Linear Delta Arrays for Compliant Dexterous Distributed Manipulation

**저자:** S. Patil; T. Tao; T. Hellebrekers; O. Kroemer; F. Z. Temel

**선별 이유:** distributed compliant mechanism과 RL로 다양한 object manipulation을 수행한다. 초록에서는 tactile/F/T sensing이 명시되지 않으므로 sensor-fusion 근거는 아니지만, **compliance 자체로 contact uncertainty를 흡수하는 접근**의 비교군이다.

## 4.5. Grey-Box Learning of Adaptive Manipulation Primitives for Robotic Assembly

**저자:** M. Braun; S. Wrede

**선별 이유:** contact-rich compliant assembly에서 pure data-driven learning 대신 expert prior를 Manipulation Primitive에 넣고 policy-gradient RL을 결합한다. **부족한 sensor/state information을 사전 구조와 task prior로 보완하는 접근**을 확인할 수 있다.

## 4.6. Decoupling Skill Learning from Robotic Control for Generalizable Object Manipulation

**저자:** K. Lu; B. Yang; B. Wang; A. Markham

**선별 이유:** object manipulation에서 learned skill dynamics와 robot kinematic control을 분리한다. current research에서도 high-level goal, low-level contact policy, robot controller를 분리하고 있으므로 **policy가 직접 학습해야 할 정보와 conventional controller에 맡길 정보를 구분하는 비교 사례**다.

## 4.7. Learning Category-Level Manipulation Tasks from Point Clouds with Dynamic Graph CNNs

**저자:** J. Liang; A. Boularias

**선별 이유:** RGB-D scene에서 tool/target object와 key-pose를 추정하여 category-level manipulation을 수행한다. **object geometry와 pose를 지속적으로 시각에서 제공하는 manipulation**과 Initial-only object information 구조를 비교할 수 있다.

## 4.8. Implementation and Optimization of Grasping Learning with Dual-modal Soft Gripper

**저자:** L. Zhao; H. Liu; F. Li; X. Ding; Y. Sun; F. Sun; J. Shan; Q. Ye; L. Li; B. Fang

**선별 이유:** visual input과 object semantic embedding을 이용해 grasping mode를 결정한다. contact sensing 연구는 아니지만, **object semantic/shape prior를 직접 주어 policy의 mode selection을 보완하는 사례**로 확인할 가치가 있다.

## 4.9. Skill-based Robot Programming in Mixed Reality with Ad-hoc Validation Using a Force-enabled Digital Twin

**저자:** J. Krieglstein; G. Held; B. A. Bálint; F. Nägele; W. Kraus

**선별 이유:** force-controlled assembly skill을 programming하고 force-enabled digital twin에서 검증한다. learning-based sensor fusion의 직접 근거는 아니지만, **force-controlled manipulation이 coordinate frame, motion mode, force-control parameter 등 많은 사전 구조를 필요로 하는 사례**로 참고할 수 있다.

---

# 5. 우선 정독 순서

현재 Research Motivation을 보강하는 목적에서는 다음 순서로 원문을 확인하는 것이 효율적이다.

1. **Toward Fine Contact Interactions: Learning to Control Normal Contact Force with Limited Information**
   - 저정보 tactile로 normal force를 제어한다는 점이 현재 Binary tactile 설계와 매우 직접적이다.

2. **Seq2Seq Imitation Learning for Tactile Feedback-based Manipulation**
   - tactile partial observability와 interaction sequence/history의 필요성을 직접 다룬다.

3. **Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture**
   - external sensor 없이 object state를 tactile 기반 estimator로 계속 추정하는 구조를 확인할 수 있다.

4. **Safe Self-Supervised Learning in Real of Visuo-Tactile Feedback Policies for Industrial Insertion**
   - tactile pose estimation과 F/T safety sensing을 서로 다른 역할로 사용하는 사례다.

5. **Demonstration-guided Optimal Control for Long-term Non-prehensile Planar Manipulation**
   - planar pushing에서 contact point와 contact mode가 별도의 중요한 상태라는 점을 확인할 수 있다.

6. **DeXtreme: Transfer of Agile In-hand Manipulation from Simulation to Reality**
   - continuous object pose estimator와 privileged state policy의 역할을 비교할 수 있다.

7. **Feature Extraction for Effective and Efficient Deep Reinforcement Learning on Real Robotic Platforms**
   - current sensor snapshot의 partial observability와 observation history 사용의 일반적 근거를 확인할 수 있다.

---

# 6. ICRA 2023 선별에서 얻은 조사 방향

ICRA 2023 후보군에서는 현재 Research Motivation의 2.1과 2.2를 보강할 수 있는 서로 다른 형태의 근거가 확인된다.

첫째, **저차원 또는 information-poor tactile도 force control에 사용할 수 있지만, 그 자체가 object state 전체를 제공하는 것은 아니다.** Toward Fine Contact Interactions는 제한된 tactile sensing으로 normal force를 제어하고, Dextrous Tactile In-Hand Manipulation은 별도의 state estimator를 둔다.

둘째, **tactile manipulation은 partial observability 문제를 갖고 history가 보완 수단이 될 수 있다.** Seq2Seq Tactile Manipulation은 interaction sequence로 hidden environment state를 추정하고, Feature Extraction 연구도 real-world sensor snapshot이 partial state만 제공한다는 점을 명시한다.

셋째, **tactile과 F/T는 같은 목적으로만 사용되지 않는다.** Safe Self-Supervised Visuo-Tactile Insertion에서는 tactile이 grasp pose estimation에, F/T는 safe self-supervised data collection에 사용된다. 원문 정독을 통해 두 sensing modality가 어떤 단계와 정보에 연결되는지 더 구체적으로 확인할 가치가 있다.

넷째, non-prehensile planar manipulation 연구에서는 contact point와 contact mode 자체가 계획에 필요한 중요한 변수로 등장한다. 이는 **global load measurement만으로 manipulation에 필요한 모든 contact configuration이 자동으로 주어지는 것은 아니라는 문제의식**과 연결될 수 있지만, 이 문헌만으로 F/T의 한계를 직접 증명할 수는 없다.

이번 CSV에서도 **wrist 6-axis F/T만으로 contact location 또는 multi-contact configuration을 추정할 때의 observability/ambiguity를 직접 분석하는 연구**는 명확하게 확인되지 않았다. 이 부분은 별도의 wrench-based contact localization 및 multi-contact estimation 문헌조사가 필요하다.
