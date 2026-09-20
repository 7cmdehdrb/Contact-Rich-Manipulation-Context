# 260918 Review Dataset

[문헌 색인](../../README.md) · [Research Motivation](../../../presentation/01_Research_Motivation.md)

공통 Review 질문에 맞추어 `260918/`의 PDF 원문을 처음부터 다시 읽고 비교한 독립 데이터셋이다. 기존 `docs/literature/papers/`의 지식베이스와 목적이 다르며, 동일 논문이 있어도 이번 분석용 Markdown을 별도로 유지한다.

## 전체 범위와 처리 결과

파일명을 대소문자 구분 없이 알파벳순으로 정렬한 **106개 PDF 전체**를 검토했다. 동일 파일·동일 논문의 추가 버전은 대표본에 통합했다. PASS와 duplicate는 상세 분석표에서 제외하고 Manifest에 남겼다.

| 구분 | 수 |
| --- | ---: |
| 발견하고 검토한 PDF 파일 | 106 |
| 중복 제거 후 고유 논문·자료 | 101 |
| 중복 파일 / 동일 논문의 추가 버전 | 5 |
| Relevant | 65 |
| Partially Relevant | 13 |
| PASS | 23 |
| 신규 Review 분석 Markdown | 78 |
| 미검토 PDF | 0 |

## Batch 구성

| 데이터셋 | 알파벳순 범위 | 결과 |
| --- | --- | --- |
| [Batch 001](batch_001/README.md) | 1–15번, 15개 PDF | Relevant 5편, Partially Relevant 3편, PASS 7개, duplicate 0개, 분석 Markdown 8개 |
| [Batch 002](batch_002/README.md) | 16–65번, 50개 PDF | Relevant 33편, Partially Relevant 5편, PASS 9개, duplicate 3개, 분석 Markdown 38개 |
| [Batch 003](batch_003/README.md) | 66–106번, 41개 PDF | Relevant 27편, Partially Relevant 5편, PASS 7개, duplicate 2개, 분석 Markdown 32개 |

별도 [test_pdfs 검증본](test_pdfs/README.md)은 schema와 형식을 먼저 검증한 3개 PDF이며 위 106개 통계와 Master에 합산하지 않는다.

## 전체 결과물

| 결과물 | 범위와 구조 |
| --- | --- |
| [Manifest](manifest.csv) | 106개 PDF 전체의 SHA-256, 상대경로, 서지, screening, 중복 관계와 읽은 범위 |
| [Master CSV](tables/paper_comparison.csv) | Relevant/Partially Relevant 고유 논문 78행 × 54열. UTF-8 |
| [Excel workbook](tables/paper_comparison.xlsx) | Master, Object_Info, Tactile, Force_Wrench, Privileged_Info, Evidence, Manifest |
| [Review 종합](synthesis/literature-synthesis.md) | Object 정보, 축약 tactile, pose 보완, F/T 성립 조건, F/T+tactile 역할, privileged information, evidence를 질문별로 횡단 비교 |

각 Batch README에서 그 범위의 논문별 분석, PASS 근거, 주요 미확인 정보와 세부 검증 범위를 확인할 수 있다. 전체 Manifest와 Master는 Batch별 CSV를 공통 schema로 병합하고 원본 PDF의 파일명·정렬 순서·SHA-256을 다시 대조한 결과다.

## 중복 처리

| PDF ID | 논문 | 대표 ID | 판정 근거 |
| --- | --- | --- | --- |
| B018 | Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention | B017 | B017/B018의 DOI·제목·7쪽 본문 일치. 전체 추출문에서 다운로드 권한 footer 행을 제외하면 동일하며 Method/실험 변경 없음. SHA-256은 다르므로 동일 파일 해시가 아닌 같은 출판본 복사본으로 판정. |
| B031 | A Unified Approach for Motion and Force Control of Robot Manipulators: The Operational Space Formulation | B032 | Same title/author/year, §I–IX structure and references as B032; 17p Korean translation/reformat. Publisher original B032 selected; no independent method/result version identified. |
| B039 | DexTouch: Learning to Seek and Manipulate Objects With Tactile Dexterity | B038 | Same DOI/publisher version as B038. Entire extracted body identical after removing download footer; SHA differs. No method/result changes. |
| B077 | Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning | B078 | Earlier arXiv version of the same paper analyzed from the more complete ICRA publisher version B078; pagination and wording differ. |
| B103 | A Unified Approach for Motion and Force Control of Robot Manipulators: The Operational Space Formulation | B032 | Exact SHA-256 duplicate of B032; filename incorrectly suggests an unrelated 2026 segmentation paper. |

`status=duplicate`인 행의 대표본은 `duplicate_of`로 추적한다. 중복본에는 별도 Markdown을 만들지 않았다. `analysis_file`이 있는 중복 행은 대표본의 분석을 가리키며, 없는 행도 대표 ID를 통해 분석 파일을 찾을 수 있다.

## 공통 coding 기준

- Goal pose와 current object pose를 분리했다. `Tracking`은 실행 중 current position/orientation 수치가 갱신될 때만 사용했다.
- Shape가 고정되어 있다는 이유로 `Tracking`으로 기록하지 않았다. Mesh/CAD, point cloud, image latent, known task geometry와 demonstration prior를 분리했다.
- Actor, critic, estimator, controller, reward, termination, curriculum/data generation의 입력을 분리했다.
- Wrist 6-axis F/T, joint-torque/current 기반 estimate, end-effector force, fingertip force를 `ft_source`에서 구분했다.
- 센서 병용과 상보적 역할의 실험적 입증을 구분했다. Input/Sensor/Representation/Sensor combination ablation, controlled comparison, failure analysis와 저자 설명만 있는 경우를 별도로 기록했다.
- 제공 PDF에서 확인되지 않은 정보는 `Not stated`, `미명시`, `판단 불가`, `해당 없음`으로 남겼다. 기존 상세 노트나 일반 지식으로 빈칸을 채우지 않았다.

## 해석 범위

이 데이터셋은 제공된 106개 PDF의 원문에 근거한다. 외부 코드·영상·별도 supplement에서만 확인되는 정보는 PDF의 사실로 보충하지 않았다. 실험 재현이나 프로젝트 사양 확정은 이 문헌 데이터셋의 범위가 아니다. 개별 사실과 미명시는 각 분석 Markdown §11–16, Batch README, Master의 evidence 필드에서 추적할 수 있다.
