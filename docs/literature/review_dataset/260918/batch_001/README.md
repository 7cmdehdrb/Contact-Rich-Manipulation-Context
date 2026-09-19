# 260918 Review Dataset — Batch 001

[문헌 색인](../../../README.md) · [260918 데이터셋 안내](../README.md) · [Research Motivation](../../../../presentation/01_Research_Motivation.md)

작성일: 2026-09-18. Schema version: **1.0**. `test_pdfs` 검증본에서 확인한 16절 분석·54열 Master·7개 Excel 시트 형식을 유지했다.

## 범위와 처리 결과

`260918/`에서 재귀적으로 발견한 PDF는 **106개**다. 사용자가 지정한 이번 범위는 파일명을 대소문자 구분 없이 알파벳순으로 정렬한 **1–15번**이며, 같은 이름이면 상대경로로 순서를 정한다. 첫 파일은 Agarwal의 *Dexterous Functional Grasping*, 마지막은 Dadiotis의 *Dynamic object goal pushing…*다. PASS를 다음 파일로 대체하지 않고 원래 선택한 15개를 유지했다.

| 구분 | 수 |
| --- | ---: |
| 검토한 PDF 파일 | 15 |
| 중복 제거 후 고유 자료 | 15 |
| 고유 학술 논문 | 14 |
| 비논문 기술문서 | 1 |
| 중복 파일 / 동일 논문의 추가 버전 | 0 |
| Relevant | 5 |
| Partially Relevant | 3 |
| PASS | 7 (논문 6편 + 기술문서 1개) |
| 신규 논문 분석 Markdown | 8 |
| 이번에 검토하지 않은 PDF | 91 |

Manifest는 **이번에 선택한 15개**의 검토 상태를 관리한다. 나머지 91개의 내용·관련성·논문 중복 여부는 판정하지 않았다. 다음 파일은 `Deng 등 - 2025 - Coarse-to-Fine Robotic Pushing Using Touch, Vision and Proprioception.pdf`지만 후속 분석은 수행하지 않았다. 검증용 `test_pdfs` 3편도 이번 15개 결과에 합산하지 않는다.

## 결과물

| 결과물 | 범위와 구조 |
| --- | --- |
| [Manifest](manifest.csv) | 15개 PDF 전체. SHA-256·원래 파일명·상대경로·서지·screening 근거·읽은 범위·status. PASS 포함 |
| [Master CSV](tables/paper_comparison.csv) | Relevant/Partially Relevant 고유 논문 8행 × 공통 54열. UTF-8 |
| [Excel workbook](tables/paper_comparison.xlsx) | Master, Object_Info, Tactile, Force_Wrench, Privileged_Info, Evidence, Manifest |
| [Review 종합](synthesis/literature-synthesis.md) | Object 정보, tactile 축약, 보완 구조, F/T 조건, modality 역할, GT, evidence, 부족한 근거의 8개 질문별 비교 |

## 논문별 신규 분석

| ID | 논문 | 판정 | 제공 PDF |
| --- | --- | --- | --- |
| B001 | [Dexterous Functional Grasping](papers/2023-agarwal-dexterous-functional-grasping.md) | Relevant | 15쪽 |
| B007 | [Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots](papers/2020-beltran-hernandez-learning-force-control.md) | Relevant | 8쪽 |
| B008 | [Precision-Focused Reinforcement Learning Model for Robotic Object Pushing](papers/2025-bergmann-precision-focused-pushing.md) | Partially Relevant | 8쪽 |
| B011 | [Gentle Object Retraction in Dense Clutter Using Multimodal Force Sensing and Imitation Learning](papers/2026-brouwer-gentle-object-retraction.md) | Relevant | 8쪽 |
| B012 | [UltraDP: Generalizable Carotid Ultrasound Scanning with Force-Aware Diffusion Policy](papers/2025-chen-ultradp-force-aware-scanning.md) | Partially Relevant | 7쪽 |
| B013 | [CHEQ-ing the Box: Safe Variable Impedance Learning for Robotic Polishing](papers/2025-cramer-cheq-safe-variable-impedance.md) | Relevant | 12쪽 |
| B014 | [Vi-TacMan: Articulated Object Manipulation via Vision and Touch](papers/2026-cui-vi-tacman.md) | Relevant | 8쪽 |
| B015 | [Dynamic object goal pushing with mobile manipulators through model-free constrained reinforcement learning](papers/2025-dadiotis-dynamic-object-goal-pushing.md) | Partially Relevant | 7쪽 |

PASS 자료는 상세 Markdown·Master·상세 Excel 시트에서 제외했다. 해당 판단의 서지·이유·원문 위치는 Manifest에만 기록한다. 학술 논문이 아닌 문서도 원래 PDF 개수에는 포함하고 `source_type`으로 구분한다.

## Context와 사실 근거

최신 GitHub `main`과 로컬 HEAD가 같은 것을 확인했다. Context 기준 커밋은 `189cb2cdae62eee3454dea3d2316452af1aaea35`다. `AGENTS.md`, 문서 형식 규칙, handoff·결정·next-actions, [Research Motivation](../../../../presentation/01_Research_Motivation.md), [문헌 안내](../../../README.md), [9월 18일 조사본](../../../reviews/2026-09-18_reduced-tactile-compensation-survey.md)을 조사 질문의 배경으로 확인했다.

논문 사실은 선택한 PDF의 title/abstract/introduction/method/observation을 먼저 screening하고, 포함 논문에 한해 본문·실험·discussion·conclusion·관련 appendix를 새로 읽어 추출했다. 중요한 표·그림은 PDF 렌더링으로 확인했다. 기존 `docs/literature/papers/`의 상세 노트를 근거로 재사용하거나 수정하지 않았다. 검증본에서는 **형식과 검증 절차만** 재사용했다. 외부 논문 버전·연결 코드·영상·별도 supplement를 제공 PDF의 사실로 채우지 않았다.

파일명과 PDF의 연도/버전이 다른 경우 PDF 표기를 우선했다. 따라서 파일명 연도와 `year`가 반드시 같지는 않다. PDF에서 확인되지 않은 metadata는 인터넷 검색으로 보충하지 않고 `Not stated`로 남겼다.

## 공통 schema와 coding 기준

논문 노트는 사용자가 지정한 **1–16절**과 Method 4.1–4.5, Tactile 7.1–7.5, F/T 8.1–8.5를 공통으로 유지한다. 쓰지 않는 센서도 절을 생략하지 않는다. 각 사실은 정책·controller·estimator·안전층·학습/평가 중 어느 경로의 정보인지 구분한다.

| 필드 / 표기 | 적용 기준 |
| --- | --- |
| Tracking | Current object position/orientation의 수치 정보가 실행 중 갱신됨. GT/noisy GT/motion capture/estimate 출처는 별도로 기록 |
| Initial | 초기 object/part/functional-region의 위치 또는 방향 단서가 제공됨. Full object center/6D pose를 뜻하지 않음. B001의 affordance 점·mask 축과 B014의 초기 holdable-region 점을 설명과 함께 기록 |
| 미제공 | 명시된 실행 입력에 해당 object 정보가 없음. Goal EEF pose, reference path, grasp command와 current object pose를 구분 |
| 기타 | 연속 영상의 latent, RGB scene, image-space landmark처럼 명시적 pose tracking과 같지 않은 정보 경로. 갱신 시점·차원·수신 모듈을 별도 설명 |
| Shape / geometry | Mesh/CAD, partial point cloud, silhouette, dimensions, task/reference geometry를 구분. 고정된 shape는 그 자체로 Tracking이 아님 |
| Not stated / 미명시 | 제공 PDF에서 확인할 수 없음. 원문에 없는 내용을 일반 지식이나 다른 논문에서 가져와 채우지 않음 |
| No | 명시된 입력 또는 방법에서 사용하지 않는 것이 확인됨 |
| Not applicable / 해당 없음 | 해당 센서·방법·학습 구조를 쓰지 않아 분석 항목 자체가 적용되지 않음 |
| ft_used | Force/F/T/Wrench의 넓은 범주. `ft_source`가 필수이며 wrist sensor·joint-torque estimate·tactile force를 동일시하지 않음 |
| history_used | 센서 frame history, whole-episode sequence, recurrent state, initial contact reference를 구분. BPTT 길이를 실행 window 길이로 바꾸지 않음 |
| *_gt | Actor/Critic/Reward/Termination/Curriculum 각각의 사용 정보와 실행 필요성을 서술. Simulator에서 학습했다는 사실만으로 모든 정보를 privileged라고 집계하지 않음 |
| evidence_type | Input/Sensor/Representation/Sensor combination ablation, Controlled comparison, Failure analysis, Author explanation only, No supporting evidence. 임의 점수 없음 |
| PDF p. | 제공 PDF 첫 장부터 세는 실제 페이지 번호. 출판 인쇄 페이지와 구분 |

Master는 논문당 한 행이며 복수 값은 `; `로 구분한다. 셀의 Yes/No만 분리해서 읽으면 조건이 사라질 수 있으므로 source/role/evidence 설명을 함께 사용한다. Excel의 상세 5개 시트는 정보 항목 또는 주장당 한 행이며 `Evidence`는 Section·Page·Table·Figure를 분리한다. 비-RL의 supervised labels는 RL privilege와 분리하여 노트에서 설명한다.

B001과 B014의 초기 부분 위치 단서를 `Initial`로 기록하더라도 두 연구의 실행 controller가 whole-object pose를 계속 받는다는 뜻은 아니다. B014의 grasp orientation·interaction direction은 current object orientation이 아니므로 Orientation은 `미제공`이다. B008의 binary는 **vision**, B011의 binary pressure는 **suction acquisition**, B014의 threshold는 **marker 선택**이다.

## 경로·중복·상태 규칙

`local_path`는 저장소 root 기준 상대경로다. `analysis_file`과 `analysis_note_path`는 이 batch root 기준 상대경로이며, PDF 공개 배포 링크가 아니다. 원본 PDF를 분석 폴더로 복제하지 않았다. Source hash는 원본 파일에서 계산했다.

선택한 15개 사이의 동일 SHA-256, 제목·저자·DOI/arXiv 식별자를 확인했으며 동일 파일·동일 논문의 추가 버전은 발견하지 않았다. 이 중복 판정은 나머지 91개 및 기존 paper-note 존재 여부와 무관하다. `version_note`는 실제 제공 버전과 filename 차이를 기록하며 확인하지 않은 버전 간 method 차이를 만들지 않는다.

`relevance_screening`은 Pending/Relevant/Partially Relevant/PASS, `status`는 pending/reading/completed/duplicate/passed다. 최종 batch는 completed 8개·passed 7개이며 미완료 상태가 없다. `read_scope`는 PASS screening 범위와 포함 논문의 전체 독해 범위를 구분한다.

## 주요 미확인 정보와 해석 제한

- **B001:** Critic 입력/GT가 미명시다. Appendix D의 관측 차원 표기와 열거된 입력 차원이 일치하지 않으며 p.5 reward threshold 단위도 원문 그대로 보존했다.
- **B007:** Critic 입력, F/T 독립 모델·filter cutoff·일부 보정 설정, 최소 성공 pose tolerance가 미명시다.
- **B008:** 일부 학습량/seed 세부가 미명시다. 실물 object position GT가 없어 1 cm 정확도의 독립 계측 성공 검증은 아니다.
- **B011:** Wrench/Tactile 결합 성공률이 각 단독보다 유의하게 높다는 검증은 없다. 세부 입력 history 및 일부 wrench/센서 처리의 미명시는 노트에 유지한다.
- **B012:** Patient/artery의 full 3D pose는 제공하지 않는다. Policy wrench-input ablation과 저수준 force controller 제거는 다르다.
- **B013:** 제공 PDF가 다른 문헌으로 넘긴 reward·constraint 구현 세부를 보충하지 않았다. Critic ensemble은 실행 중 adaptive mixing에도 쓰인다.
- **B014:** Tactile threshold 수치, 전체 marker/센서 규격, 참조 controller의 일부 알고리즘과 실물 반복 성공률이 미명시다.
- **B015:** 실물은 external motion capture를 계속 사용한다. 일부 실물 trial denominator와 상세 low-level 계약이 미명시다.
- **PASS metadata:** 일부 PDF의 연도·venue·식별자가 명시되지 않아 `Not stated`다. 상세 재분석을 수행한 것으로 표시하지 않는다.

확인되지 않은 정보를 채우기 위해 기존 노트나 외부 논문·코드로 범위를 확장하지 않았다. 개별 사실의 구체적 위치와 한계는 각 노트 §12–16에서 추적할 수 있다.

## 검증과 다음 범위

원본 SHA-256, 알파벳순 15개 선택, 16절 schema, 54열 Master, PASS 제외, 시트 간 논문 ID, Markdown 링크, CSV/Excel 값의 일치, Excel 표·필터·고정 행/열, 공개 파일의 절대경로 유무를 검사했다. 7개 시트와 긴 행·가로 구간의 렌더링을 검수했다. 코드/실험 재현과 native Excel application 동작 시험은 수행하지 않았다.

이 batch는 문헌 비교 자료이며 프로젝트의 확정 사양을 변경하지 않는다. 기존 paper notes와 검증본 파일은 그대로 유지했다. Commit/Push는 수행하지 않았으며, **다음 PDF 분석은 사용자가 결정할 때까지 진행하지 않는다.**
