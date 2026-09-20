# 260918 Review Dataset — Batch 002

[문헌 색인](../../../README.md) · [260918 데이터셋 안내](../README.md) · [Research Motivation](../../../../presentation/01_Research_Motivation.md)

최초 분석일은 2026-09-18이며, 중단된 작업을 2026-09-20에 재개해 완성했다. Schema version은 **1.0**이다. `test_pdfs` 검증본과 Batch 001의 16절 분석·54열 Master·7개 Excel 시트 형식을 유지했다.

## 범위와 처리 결과

`260918/`에서 재귀적으로 발견한 PDF **106개**를 파일명 기준으로 대소문자 구분 없이 알파벳순 정렬했다. 이번 범위는 Batch 001 다음인 **16–65번 50개 PDF**다. PASS나 중복을 다음 파일로 대체하지 않았다. 첫 파일은 *Coarse-to-Fine Robotic Pushing Using Touch, Vision and Proprioception*, 마지막은 *Towards Safe and Efficient Learning in the Wild*다.

| 구분 | 수 |
| --- | ---: |
| 검토한 PDF 파일 | 50 |
| 중복 제거 후 고유 논문·자료 | 47 |
| 중복 파일 / 동일 논문의 추가 버전 | 3 |
| Relevant | 33 |
| Partially Relevant | 5 |
| PASS | 9 |
| 신규 논문 분석 Markdown | 38 |
| Batch 001과 합산한 검토 PDF | 65 |
| 아직 검토하지 않은 PDF | 41 |

Manifest는 이번 50개 PDF 각각의 SHA-256, 서지, 상대경로, screening 결과, 중복 관계, 읽은 범위를 기록한다. 중복 PDF는 대표 버전의 분석 파일을 가리키며 별도 Markdown을 만들지 않았다. PASS는 상세 Markdown, Master CSV, Excel 상세 시트에서 제외했다.

## 결과물

| 결과물 | 범위와 구조 |
| --- | --- |
| [Manifest](manifest.csv) | 이번 50개 PDF 전체. PASS와 duplicate 포함 |
| [Master CSV](tables/paper_comparison.csv) | Relevant/Partially Relevant 고유 논문 38행 × 54열. UTF-8 |
| [Excel workbook](tables/paper_comparison.xlsx) | Master, Object_Info, Tactile, Force_Wrench, Privileged_Info, Evidence, Manifest |
| [Review 종합](synthesis/literature-synthesis.md) | Object 정보, 축약 tactile, pose 보완, F/T 조건, F/T+tactile, privileged information, evidence, 부족한 근거를 질문별 비교 |

## 논문별 신규 분석

| ID | 논문 | 판정 | Task |
| --- | --- | --- | --- |
| B016 | [Coarse-to-Fine Robotic Pushing Using Touch, Vision and Proprioception](papers/2025-deng-coarse-to-fine-robotic-pushing.md) | Relevant | Planar pushing to target position and orientation; packing objects |
| B019 | [Force Policy: Learning Hybrid Force-Position Control Policy under Interaction Frame for Contact-Rich Manipulation](papers/2026-fang-force-policy.md) | Relevant | Pushing and flipping; EV charger insertion; sticker application |
| B020 | [Learning Visuotactile Estimation and Control for Non-prehensile Manipulation under Occlusions](papers/2024-del-aguila-ferrandis-visuotactile-estimation-occlusions.md) | Relevant | Planar non-prehensile pushing under occlusions |
| B021 | [FILIC: Dual-Loop Force-Guided Imitation Learning with Impedance Torque Control for Contact-Rich Manipulation Tasks](papers/2026-ge-filic.md) | Relevant | Peg/adapter insertion; emergency-stop operation; clamp fixation; cap tightening |
| B023 | [Proprioceptive Sensor-Based Simultaneous Multi-Contact Point Localization and Force Identification for Robotic Arms](papers/2023-han-proprioceptive-multi-contact-localization.md) | Relevant | Multi-contact point localization and force identification |
| B025 | [Visuotactile-RL: Learning Multimodal Manipulation Policies with Deep Reinforcement Learning](papers/2022-hansen-visuotactile-rl.md) | Relevant | Texture contact reaching; door opening; tactile grasp/lift |
| B026 | [Force Push: Robust Single-Point Pushing With Force Feedback](papers/2024-heins-force-push.md) | Relevant | Single-point planar pushing; straight/curved path; obstacle contact |
| B027 | [Perceiving Extrinsic Contacts from Touch Improves Learning Insertion Policies](papers/2023-higuera-extrinsic-contacts-insertion.md) | Relevant | Mug-in-cupholder; bowl-in-dishrack insertion |
| B028 | [Dexterous in-hand manipulation of slender cylindrical objects through deep reinforcement learning with tactile sensing](papers/2025-hu-tactile-slender-in-hand-manipulation.md) | Relevant | Continuous three-finger in-hand pose tracking of slender cylindrical objects |
| B030 | [Robotic Compliant Object Prying Using Diffusion Policy Guided by Vision and Force Observations](papers/2025-kang-compliant-object-prying-vision-force.md) | Relevant | Compliant battery prying and extraction from spring-loaded/tight casings |
| B032 | [A Unified Approach for Motion and Force Control of Robot Manipulators: The Operational Space Formulation](papers/1987-khatib-operational-space-motion-force.md) | Partially Relevant | Constrained motion; active force control; contact/slide/insertion/compliance operations |
| B033 | [Pre- and Post-Contact Policy Decomposition for Non-Prehensile Manipulation with Zero-Shot Sim-To-Real Transfer](papers/2023-kim-pre-post-contact-sim-to-real.md) | Partially Relevant | Non-prehensile card relocation; push/reorient over bump; object transfer over wall |
| B035 | [Pre- and Post-Contact Policy Decomposition for Planar Contact Manipulation Under Uncertainty](papers/undated-koval-contact-policy-decomposition.md) | Relevant | Planar pushing into graspable hand-relative goal region under pose uncertainty |
| B036 | [Zero-Shot Transfer of a Tactile-based Continuous Force Control Policy from Simulation to Robot](papers/2024-lach-continuous-force-control.md) | Relevant | Continuous grasp normal-force regulation with minimal object displacement |
| B037 | [VDTF-ACT: ACT-based Multimodal Space Fine Manipulation Method with Visual Depth Tactile Fusion](papers/2025-lang-vdtf-act.md) | Relevant | Dual-arm peg/socket grasping, alignment and insertion in simulated low gravity |
| B038 | [DexTouch: Learning to Seek and Manipulate Objects With Tactile Dexterity](papers/2024-lee-dextouch.md) | Relevant | Blind seeking and grasping/retrieval; door opening; valve rotation |
| B040 | [Progressive Policy Learning: A Hierarchical Framework for Dexterous Bimanual Manipulation](papers/2025-lee-progressive-policy-learning.md) | Partially Relevant | Bimanual Rubik-like cube holding and 90-degree layer rotation |
| B041 | [In-Hand Object Pose Tracking via Contact Feedback and GPU-Accelerated Robotic Simulation](papers/2020-liang-in-hand-object-pose-tracking.md) | Relevant | 6D in-hand object pose tracking during pick/place, in-hand rotation and finger gaiting |
| B043 | [Tactile Gym 2.0: Sim-to-Real Deep Reinforcement Learning for Comparing Low-Cost High-Resolution Robot Touch](papers/2022-lin-tactile-gym-2.md) | Relevant | Single-arm object pushing, edge following and surface following |
| B044 | [Attention for Robot Touch: Tactile Saliency Prediction for Robust Sim-to-Real Tactile Control](papers/2023-lin-tactile-saliency.md) | Relevant | Target-edge contact pose estimation and 2D edge following amid tactile distractors |
| B045 | [Bi-Touch: Bimanual Tactile Manipulation With Sim-to-Real Deep Reinforcement Learning](papers/2023-lin-bi-touch.md) | Relevant | Bimanual planar object pushing, in-plane reorientation and object gathering under perturbations |
| B046 | [Tactile Active Inference Reinforcement Learning for Efficient Robotic Manipulation Skill Acquisition](papers/2024-liu-tactile-active-inference.md) | Relevant | Sim slope pushing; real nut screwing |
| B047 | [FACTR: Force-Attending Curriculum Training for Contact-Rich Policy Learning](papers/2025-liu-factr.md) | Relevant | Box lifting; non-prehensile pivoting; fruit pick-place; dough rolling |
| B049 | [ForceMimic: Force-Centric Imitation Learning with Force-Motion Capture System for Contact-Rich Manipulation](papers/2025-liu-forcemimic.md) | Relevant | Zucchini peeling |
| B050 | [Learning a High-quality Robotic Wiping Policy Using Systematic Reward Analysis and Visual-Language Model Based Curriculum](papers/2025-liu-high-quality-robotic-wiping.md) | Relevant | Blind curved-surface wiping with two waypoints and target force 60 N |
| B051 | [Pose-and-shear-based tactile servoing](papers/2024-lloyd-pose-and-shear-tactile-servoing.md) | Relevant | Tactile object tracking; surface following; single/dual-arm pushing |
| B052 | [ManiFeel: Benchmarking and Understanding Visuotactile Manipulation Policy Learning](papers/2026-luu-manifeel.md) | Relevant | Insertion; screwing; occluded exploration; tactile sorting |
| B053 | [Current as Touch: Proprioceptive Contact Feedback for Compliant Dexterous Manipulation](papers/2026-ma-current-as-touch.md) | Relevant | Compliant dexterous teleoperation; wiping; card picking; dynamic bottle holding |
| B054 | [Localizing External Contact Using Proprioceptive Sensors: The Contact Particle Filter](papers/2016-manuelli-contact-particle-filter.md) | Relevant | External contact detection/localization on robot surface |
| B057 | [Enhancing Tactile-based Reinforcement Learning for Robotic Control](papers/2025-miller-enhancing-tactile-rl.md) | Relevant | Object finding; Ball bouncing; Baoding rotation |
| B058 | [Factory: Fast Contact for Robotic Assembly](papers/2022-narang-factory.md) | Partially Relevant | Pick; Place; Nut-and-bolt Screw |
| B059 | [Deep Functional Predictive Control (deep-FPC): Robot Pushing 3-D Cluster using Tactile Prediction](papers/2023-nazari-deep-fpc.md) | Relevant | Flexible strawberry stem/cluster pushing; contact maintenance |
| B060 | [Belief-Grounded Networks for Accelerated Robot Learning under Partial Observability](papers/2021-nguyen-belief-grounded-networks.md) | Relevant | Top plate grasping; 1D selective bump pushing; 2D contact exploration/grasping |
| B061 | [FACTR 2: Learning External Force Sensing for Commodity Robot Arms Improves Policy Learning](papers/2026-oh-factr2.md) | Relevant | Bimanual assembly; insertion; cap screwing; force-feedback teleoperation |
| B062 | [A Contact Model based on Denoising Diffusion to Learn Variable Impedance Control for Contact-rich Manipulation](papers/2024-okada-diffusion-contact-model.md) | Partially Relevant | Curved-surface wiping; force-trajectory reproduction |
| B063 | [Pushing in the Dark: A Reactive Pushing Strategy for Mobile Robots Using Tactile Feedback](papers/2024-ozdamar-pushing-in-the-dark.md) | Relevant | Mobile base pushing bulky objects |
| B064 | [Guiding real-world reinforcement learning for in-contact manipulation tasks with Shared Control Templates](papers/2024-padalkar-shared-control-templates.md) | Relevant | Pouring; grid-clamp insertion/assembly |
| B065 | [Towards Safe and Efficient Learning in the Wild: Guiding RL With Constrained Uncertainty-Aware Movement Primitives](papers/2025-padalkar-kernelized-guided-rl.md) | Relevant | BNC connector alignment; insertion; locking |

## 중복 처리

| PDF ID | 논문 | 대표 ID | 판정 근거 |
| --- | --- | --- | --- |
| B018 | Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention | B017 | B017/B018의 DOI·제목·7쪽 본문 일치. 전체 추출문에서 다운로드 권한 footer 행을 제외하면 동일하며 Method/실험 변경 없음. SHA-256은 다르므로 동일 파일 해시가 아닌 같은 출판본 복사본으로 판정. |
| B031 | A Unified Approach for Motion and Force Control of Robot Manipulators: The Operational Space Formulation | B032 | Same title/author/year, §I–IX structure and references as B032; 17p Korean translation/reformat. Publisher original B032 selected; no independent method/result version identified. |
| B039 | DexTouch: Learning to Seek and Manipulate Objects With Tactile Dexterity | B038 | Same DOI/publisher version as B038. Entire extracted body identical after removing download footer; SHA differs. No method/result changes. |

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

Critic 입력이 `Not stated` 또는 `미명시`인 논문: B020, B027, B028, B033, B036, B040, B043, B044, B045, B046, B050, B064, B065.

F/T 하드웨어 출처 또는 장착 위치가 명확하지 않은 논문: B032, B049, B050, B058, B062, B064, B065.

이 밖의 task별 미명시, 원문 표기 불일치, 성공 판정 proxy, 실물 trial denominator는 각 분석 파일 §1·§11–16에 보존했다. 미확인 항목을 기존 노트나 일반 지식으로 보충하지 않았다.

## 검증과 다음 범위

50개 원본 SHA-256과 정렬 범위, 모든 Manifest 행의 최종 상태, 중복 대표 관계, 16절 Markdown schema, 54열 Master, PASS/duplicate 제외, 상세 시트 ID, CSV와 Excel 값, 공개 파일의 절대경로 부재를 검사했다. Excel은 7개 시트의 표·filter·고정 행/열과 렌더링을 검수했다. 코드 실행이나 논문 실험 재현은 범위가 아니다.

다음 미검토 파일은 `260918/Pan 등 - 2026 - Beyond Binary Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation.pdf`다. 이번 결과는 프로젝트 확정 사양을 변경하지 않는다. Batch 002를 위한 별도 Git commit/push는 수행하지 않았으며, 남은 41개는 사용자의 다음 결정 전까지 분석하지 않는다.
