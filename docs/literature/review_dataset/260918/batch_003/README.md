# 260918 Review Dataset — Batch 003

[문헌 색인](../../../README.md) · [260918 데이터셋 안내](../README.md) · [Research Motivation](../../../../presentation/01_Research_Motivation.md)

최초 분석일은 2026-09-18이며, 중단된 작업을 2026-09-20에 재개해 완성했다. Schema version은 **1.0**이다. `test_pdfs` 검증본과 Batch 001의 16절 분석·54열 Master·7개 Excel 시트 형식을 유지했다.

## 범위와 처리 결과

`260918/`에서 재귀적으로 발견한 PDF **106개**를 파일명 기준으로 대소문자 구분 없이 알파벳순 정렬했다. 이번 범위는 Batch 001·002 다음인 **66–106번 41개 PDF**다. PASS나 중복을 다른 파일로 대체하지 않았다. 첫 파일은 *Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation*, 마지막은 *Framework for Robot Door Opening Based on Visual, Force, and Tactile Integration*다.

| 구분 | 수 |
| --- | ---: |
| 검토한 PDF 파일 | 41 |
| 중복 제거 후 고유 논문·자료 | 39 |
| 중복 파일 / 동일 논문의 추가 버전 | 2 |
| Relevant | 27 |
| Partially Relevant | 5 |
| PASS | 7 |
| 신규 논문 분석 Markdown | 32 |
| Batch 001·002와 합산한 검토 PDF | 106 |
| 아직 검토하지 않은 PDF | 0 |

Manifest는 이번 41개 PDF 각각의 SHA-256, 서지, 상대경로, screening 결과, 중복 관계, 읽은 범위를 기록한다. 중복 PDF는 대표 버전의 분석 파일을 가리키며 별도 Markdown을 만들지 않았다. PASS는 상세 Markdown, Master CSV, Excel 상세 시트에서 제외했다.

## 결과물

| 결과물 | 범위와 구조 |
| --- | --- |
| [Manifest](manifest.csv) | 이번 41개 PDF 전체. PASS와 duplicate 포함 |
| [Master CSV](tables/paper_comparison.csv) | Relevant/Partially Relevant 고유 논문 32행 × 54열. UTF-8 |
| [Excel workbook](tables/paper_comparison.xlsx) | Master, Object_Info, Tactile, Force_Wrench, Privileged_Info, Evidence, Manifest |
| [Review 종합](synthesis/literature-synthesis.md) | Object 정보, 축약 tactile, pose 보완, F/T 조건, F/T+tactile, privileged information, evidence, 부족한 근거를 질문별 비교 |

## 논문별 신규 분석

| ID | 논문 | 판정 | Task |
| --- | --- | --- | --- |
| B066 | [Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation](papers/2026-pan-beyond-binary-cop-tactile.md) | Relevant | Blind peg-in-hole insertion; blind ball balancing |
| B067 | [Identifying External Contacts from Joint Torque Measurements on Serial Robotic Arms and Its Limitations](papers/2021-pang-external-contact-joint-torque-limitations.md) | Partially Relevant | External contact detection/localization on serial robot arms |
| B069 | [Learning Force Control for Legged Manipulation](papers/2024-portela-learning-force-control-legged-manipulation.md) | Partially Relevant | Whole-body locomotion, EEF position and commanded force control |
| B071 | [CONTACT: CONtact-aware TACTile Learning for Robotic Disassembly](papers/2026-saka-contact-tactile-disassembly.md) | Relevant | Rigid and deformable robotic disassembly |
| B072 | [A Contact-Driven Framework for Manipulating in the Blind](papers/2025-saleem-contact-driven-manipulating-blind.md) | Relevant | Blind valve reaching/manipulation and cluttered-shelf object retrieval |
| B073 | [The Power of the Senses: Generalizable Manipulation from Vision and Touch through Masked Multimodal Learning](papers/2024-sferrazza-m3l-vision-touch.md) | Relevant | Peg insertion; door opening; in-hand cube rotation |
| B074 | [Proactive Action Visual Residual Reinforcement Learning for Contact-Rich Tasks Using a Torque-Controlled Robot](papers/2021-shi-proactive-visual-residual-rl.md) | Relevant | RAM insertion under target pose/contact uncertainty |
| B075 | [Learning Non-Prehensile Manipulation With Force and Vision Feedback Using Optimization-Based Demonstrations](papers/2026-shirai-non-prehensile-force-vision-demonstrations.md) | Relevant | Planar non-prehensile pivoting and pushing |
| B076 | [Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing](papers/2023-yang-tactile-pushing.md) | Relevant | Goal-conditioned planar pushing of unknown objects |
| B078 | [Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning](papers/2024-su-sim2real-unknown-objects-tactile-rl.md) | Relevant | In-hand pivoting to a target relative angle |
| B079 | [Going In Blind: Object Motion Classification using Distributed Tactile Sensing for Safe Reaching in Clutter](papers/2022-thomasson-going-in-blind.md) | Partially Relevant | Incidental-contact object-motion classification for safe reaching in clutter |
| B080 | [Multi-Fingered Dragging of Unknown Objects and Orientations Using Distributed Tactile Information Through Vision-Transformer and LSTM](papers/2024-ueno-multifingered-dragging.md) | Relevant | Multi-fingered dragging, reorientation and grasping of unknown objects |
| B081 | [Learning Robotic Manipulation Skills Using an Adaptive Force-Impedance Action Space](papers/2021-ulmer-adaptive-force-impedance.md) | Relevant | Contact-rich wiping; simulated door opening, lifting and wiping |
| B083 | [Reinforcement Learning with Parameterized Manipulation Primitives for Robotic Assembly](papers/2023-vuong-parameterized-primitives-assembly.md) | Relevant | High-precision peg-in-hole assembly |
| B085 | [Contact SLAM: An Active Tactile Exploration Policy Based on Physical Reasoning Utilized in Robotic Fine Blind Manipulation Tasks](papers/2026-wang-contact-slam.md) | Relevant | Blind socket assembly and obstacle-aware block pushing |
| B086 | [MAT: Multi-Fingered Adaptive Tactile Grasping via Deep Reinforcement Learning](papers/2019-wu-mat-adaptive-tactile-grasping.md) | Relevant | Vision-initialized, tactile closed-loop multi-finger grasp adaptation and lift |
| B087 | [ViTacGen: Robotic Pushing With Vision-to-Touch Generation](papers/2025-wu-vitacgen-vision-to-touch-pushing.md) | Relevant | Goal-conditioned planar robotic pushing along desired trajectories |
| B088 | [Robotized Unplugging of a Cylindrical Peg Press-Fitted into a Cylindrical Hole](papers/2024-xu-robotized-unplugging-press-fit.md) | Partially Relevant | Robotized removal of a cylindrical press-fit peg by direct pull or twist-and-pull |
| B089 | [Reactive Diffusion Policy: Slow-Fast Visual-Tactile Policy Learning for Contact-Rich Manipulation](papers/2025-xue-reactive-diffusion-policy.md) | Relevant | Peeling; curved-surface wiping; bimanual paper-cup lifting under perturbations |
| B090 | [Disambiguate Gripper State in Grasp-Based Tasks: Pseudo-Tactile as Feedback Enables Pure Simulation Learning](papers/2025-yang-pseudo-tactile-gripper-state.md) | Relevant | Pick-and-lift; drawer opening; oven opening with forced premature-gripper disturbances |
| B092 | [Rotating without Seeing: Towards In-hand Dexterity through Touch](papers/2023-yin-rotating-without-seeing-touch-dexterity.md) | Relevant | Vision-free in-hand object rotation about commanded x/y/z axes |
| B093 | [SAVR: Scooping Adaptation for Variable Food Properties via Reinforcement Learning](papers/2025-yow-savr-variable-food-scooping.md) | Relevant | Goal-conditioned food scooping to a target portion across variable food properties |
| B094 | [ForceVLA: Enhancing VLA Models with a Force-aware MoE for Contact-rich Manipulation](papers/2025-yu-forcevla-force-aware-moe.md) | Relevant | Bottle pumping; plug insertion; USB insertion; whiteboard wiping; cucumber peeling |
| B095 | [Augmenting Robotic Disassembly Skill: Combining Compliance Control Strategy with Reinforcement Learning for Twist-Pulling Disassembly](papers/2025-zang-compliance-rl-twist-pulling-disassembly.md) | Relevant | Twist-and-pull cap–shaft robotic disassembly under hidden geometry and rotation-center misalignment |
| B096 | [Twist-pull as an execution skill primitive for robotic disassembly: Safety-aware skill augmentation under contact uncertainty](papers/2026-zang-twist-pull-safety-aware-disassembly.md) | Relevant | Twist–pull disassembly of cap–shaft, spanner-like, and real product assemblies under grasp misalignment and hidden contact resistance. |
| B098 | [Learning Insertion Primitives with Discrete-Continuous Hybrid Action Space for Robotic Assembly Tasks](papers/2021-zhang-parameterized-insertion-primitives.md) | Relevant | Peg-in-hole and connector insertion under uncertain hole pose using learned motion primitives |
| B099 | [Learning Variable Impedance Control via Inverse Reinforcement Learning for Force-Related Tasks](papers/2021-zhang-variable-impedance-airl.md) | Partially Relevant | Peg-in-hole and cup-on-plate variable-impedance manipulation learned from expert demonstrations |
| B100 | [A residual reinforcement learning method for robotic assembly using visual and force information](papers/2024-zhang-residual-rl-visual-force-assembly.md) | Relevant | Vision-guided peg-in-hole assembly with force-controlled reaching, search and insertion stages |
| B101 | [SRL-VIC: A Variable Stiffness-based Safe Reinforcement Learning for Contact-rich Robotic Tasks](papers/2024-zhang-srl-vic-contact-maze.md) | Relevant | Blind, contact-rich maze exploration with collision safety and obstacle pushing |
| B102 | [The Role of Tactile Sensing for Learning Reach and Grasp](papers/2025-zhang-role-tactile-reach-grasp.md) | Relevant | Two-finger reach-and-grasp with systematic comparison of tactile sensing representations |
| B105 | [ARMCL: ARM Contact point Localization via Monte Carlo Localization](papers/2019-zwiener-armcl-contact-localization.md) | Relevant | External contact point and force localization on a robot arm without tactile skin |
| B106 | [Framework for Robot Door Opening Based on Visual, Force, and Tactile Integration](papers/2026-simundic-visual-force-tactile-door-opening.md) | Relevant | Autonomous opening of handleless cabinet doors with failure-driven camera/environment-model correction |

## 중복 처리

| PDF ID | 논문 | 대표 ID | 판정 근거 |
| --- | --- | --- | --- |
| B077 | Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning | B078 | Earlier arXiv version of the same paper analyzed from the more complete ICRA publisher version B078; pagination and wording differ. |
| B103 | A Unified Approach for Motion and Force Control of Robot Manipulators: The Operational Space Formulation | B032 | Exact SHA-256 duplicate of B032; filename incorrectly suggests an unrelated 2026 segmentation paper. |

## Context와 사실 근거

재개 시점의 local `main`과 `origin/main`이 일치하는 것을 확인했다. 조사 질문은 `AGENTS.md`, 문서 형식 규칙, Research Motivation, 문헌 안내, 2026-09-18 reduced-tactile compensation 조사본을 기준으로 유지했다.

논문 사실은 이번 범위의 PDF 원문에서 title, abstract, introduction, method overview와 observation을 먼저 screening하고, 포함 논문은 method, training, experiments, discussion, conclusion과 관련 appendix를 새로 읽어 추출했다. 핵심 표와 그림은 렌더링으로 확인했다. 기존 `docs/literature/papers/`의 상세 노트는 결과의 사실 근거로 사용하거나 수정하지 않았다. 외부 코드·영상·별도 supplement에만 있는 정보를 PDF 사실처럼 채우지 않았다.

## 공통 coding 기준

- Goal pose와 current object pose를 구분했다. `Tracking`은 실행 중 current position/orientation이 수치로 갱신되는 경우에만 사용했다.
- Shape가 시간에 따라 고정된다는 이유로 `Tracking`으로 기록하지 않았다. Mesh/CAD, image/point-cloud 단서, known task geometry, demonstration prior를 분리했다.
- Actor, critic, state estimator, controller, reward, termination, curriculum 입력을 분리했다.
- Wrist 6-axis F/T, joint-torque/current 기반 estimate, fingertip 또는 gripper-pad force, base F/T를 `ft_source`에서 구분했다.
- 센서를 함께 사용했다는 사실과 역할 상보성이 ablation으로 입증됐다는 주장을 구분했다.
- 원문에서 확인되지 않은 값은 `Not stated`, `미명시`, `판단 불가`, `해당 없음`으로 남겼다.
- 각 source location의 `PDF p.`는 제공 PDF 첫 장부터 세는 1-based 페이지다.

## 주요 미확인 정보

Critic 입력이 `Not stated` 또는 `미명시`인 논문: B076, B081, B083, B087, B093, B095, B099.

F/T 하드웨어 출처 또는 장착 위치가 명확하지 않은 논문: B081, B090, B094, B095, B101.

이 밖의 task별 미명시, 원문 표기 불일치, 성공 판정 proxy, 실물 trial denominator는 각 분석 파일 §1·§11–16에 보존했다. 미확인 항목을 기존 노트나 일반 지식으로 보충하지 않았다.

## 검증과 다음 범위

41개 원본 SHA-256과 정렬 범위, 모든 Manifest 행의 최종 상태, 중복 대표 관계, 16절 Markdown schema, 54열 Master, PASS/duplicate 제외, 상세 시트 ID, CSV와 Excel 값, 공개 파일의 절대경로 부재를 검사했다. Excel은 7개 시트의 표·filter·고정 행/열과 렌더링을 검수했다. 코드 실행이나 논문 실험 재현은 범위가 아니다.

이번 배치로 `260918/`에서 발견한 106개 PDF의 screening과 관련 논문 재분석이 완료됐다. 이번 결과는 프로젝트 확정 사양을 변경하지 않는다. Git commit/push 여부는 데이터셋 전체 검증 결과와 함께 최종 기록한다.
