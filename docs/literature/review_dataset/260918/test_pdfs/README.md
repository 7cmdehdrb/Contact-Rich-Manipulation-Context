# 260918 Review Dataset — test_pdfs 검증본

[문헌 색인](../../../README.md) · [260918 데이터셋 안내](../README.md) · [Research Motivation](../../../../presentation/01_Research_Motivation.md)

작성일: 2026-09-18. Schema version: **1.0-pilot**.

`test_pdfs/`의 PDF 3개를 대상으로, 공통 Review 질문과 동일 schema로 원문부터 새로 분석한 검증본이다. 이번 단계는 결과 형식·분류·근거 추적 가능성을 검토하기 위한 표본 작업이며, `260918/` 전체 PDF 분석을 완료한 결과가 아니다.

## 결과물

| 결과물 | 내용 |
| --- | --- |
| [Manifest](manifest.csv) | 전체 3개 PDF의 파일명·상대경로·SHA-256·서지·screening·처리 상태 |
| [Master CSV](tables/paper_comparison.csv) | 관련 고유 논문당 1행. 사용자 지정 공통 열 전체 포함 |
| [Excel workbook](tables/paper_comparison.xlsx) | Master, Object_Info, Tactile, Force_Wrench, Privileged_Info, Evidence, Manifest의 7개 시트 |
| [Review용 종합 비교](synthesis/literature-synthesis.md) | Object 정보, tactile 축약, F/T 조건, 학습 GT, evidence를 질문별 비교 |

## 논문별 신규 분석

| ID | 논문 | 판정 | 원문 범위 | 상태 |
| --- | --- | --- | --- | --- |
| T01 | [A residual reinforcement learning method for robotic assembly using visual and force information](papers/2024-zhang-residual-rl-visual-force-assembly.md) | Relevant | 18쪽 | completed |
| T02 | [SRL-VIC: A Variable Stiffness-based Safe Reinforcement Learning for Contact-rich Robotic Tasks](papers/2024-zhang-srl-vic.md) | Partially Relevant | 8쪽 | completed |
| T03 | [The Role of Tactile Sensing for Learning Reach and Grasp](papers/2025-zhang-tactile-reach-grasp.md) | Relevant | 8쪽 | completed |

PDF **3개**, 고유 논문 **3편**, 중복 **0개**, PASS **0편**, Relevant **2편**, Partially Relevant **1편**, 신규 논문 분석 Markdown **3개**다. 각 PDF를 먼저 screening하고 T01 → T02 → T03 순서로 정독·구조화했으며 주요 입력 경계와 수치는 원문으로 교차 검증했다. PASS와 중복 사례가 없으므로 그 분기의 실제 사례 처리는 이번 검증본에서 시험되지 않았다.

## 분석 기준과 출처 경계

분석 시작 시 GitHub `main`과 로컬 HEAD의 일치를 확인했다. Context 기준 커밋은 `189cb2cdae62eee3454dea3d2316452af1aaea35`다. `AGENTS.md`, 문서 형식 규칙, handoff·결정·next-actions, [Research Motivation](../../../../presentation/01_Research_Motivation.md), [문헌 안내](../../../README.md), [9월 18일 조사본](../../../reviews/2026-09-18_reduced-tactile-compensation-survey.md)을 조사 질문의 배경으로 읽었다.

논문 사실은 이번 제공 PDF에서 새로 추출했다. 기존 `docs/literature/papers/`의 상세 노트를 열어 재사용하거나 수정하지 않았다. 별도의 인터넷 논문 버전·코드·영상·외부 supplement의 정보를 이번 PDF 사실로 추가하지 않았다. 외부 DOI 링크는 PDF 안의 식별자에 기반한 서지 안내다.

핵심 질문은 다음 세 가지다.

1. 축약 tactile에 없는 정보를 object pose·shape·proprioception·history·force·state estimation·training information 중 무엇으로 보완하는가?
2. F/T 또는 wrench로 어떤 접촉 정보를 얻으며 이를 가능하게 하는 제어·기하·학습 조건은 무엇인가?
3. F/T와 tactile의 역할 분담을 실제 ablation 또는 비교가 뒷받침하는가?

## 공통 schema와 읽는 규칙

논문 Markdown은 Paper Information부터 Important Source Locations까지 사용자가 지정한 **16개 절**을 동일하게 사용한다. Tactile/F/T를 쓰지 않는 경우에도 해당 절을 유지하고 `사용하지 않음`·`해당 없음`으로 표시한다. 실제 사용이 확인되지 않은 것을 `No`로 확정하지 않고 `미명시`·`Not stated`로 남긴다.

| 표기/필드 | 정의 |
| --- | --- |
| Tracking | Current position/orientation이 실행 중 계속 제공되는 조건. GT/noisy GT/estimate를 별도 설명 |
| Initial | Episode 초기에만 물체 상태가 제공됨. 이번 표본에 확인된 사례 없음 |
| 미제공 | 해당 수치/정보가 명시된 실행 입력에 없음. 로봇 상태·학습용 정보와 구분 |
| 기타 | Latent RGB representation, object identity, 실험별 다른 입력 경로 등 단일 분류로 왜곡되는 경우 |
| 미명시 / Not stated | 제공 PDF에서 확인할 수 없거나 취득 방법·조건이 명확하지 않음 |
| No | 명시된 입력/방법상 사용하지 않음이 확인됨 |
| Not applicable | 방법·센서를 쓰지 않아 적용 대상 자체가 아님 |
| ft_used | Force/F/T/Wrench 범주 전체. `Yes`만 보지 말고 반드시 `ft_source` 확인. T03은 fingertip force이며 wrist F/T가 아님 |
| *_gt | Yes/No의 이유·조건·미명시 부분을 함께 기록. Reward의 기하량 사용과 simulator API 확인 여부를 분리 |
| evidence_type | 원문의 ablation·comparison·failure·author explanation 유형. 임의 점수 없음 |
| PDF p. | 제공 파일의 첫 페이지를 1로 센 실제 페이지 번호. 인쇄 페이지와의 대응은 각 노트 §1 |

Master는 논문당 1행을 유지하므로, 같은 논문의 주요 실험·RGB variant·실물 조건을 셀 안에서 구분한다. 복수 값은 `; `로 구분한다. Excel 상세 시트는 **정보 항목 또는 주장당 1행**으로 나누어 조건·역할·원문 위치를 더 자세히 기록한다. `Evidence`는 claim·비교 조건·결과·section/page/table/figure를 분리한다. 표나 수식이 없는 원문 위치에는 가짜 번호를 만들지 않는다.

## Manifest와 중복 규칙

Manifest의 `local_path`는 **저장소 root 기준 상대경로**이고, `analysis_file` 및 Master의 `analysis_note_path`는 **이 검증 데이터셋 root 기준 상대경로**다. 이 경로는 내부 대응용 문자열이며 PDF 공개 배포 링크가 아니다. PDF는 기존 위치에서 읽었고 결과 폴더로 복제하지 않았다.

SHA-256으로 동일 파일을 검사하고 제목·저자·PDF DOI로 논문 동일성을 확인했다. 이번 세 편은 제목·저자 조합이 다르며 중복이 없다. T02 DOI는 PDF에서 미확인이나 다른 두 편과 제목이 명백히 달라 고유 논문으로 분리할 수 있다. 이후 중복이 생기면 주 분석본 한 편에만 Markdown을 만들고 `duplicate_of`·`version_note`로 연결한다.

`relevance_screening`은 Pending/Relevant/Partially Relevant/PASS, `status`는 pending/reading/completed/duplicate/passed를 사용한다. PASS는 Manifest에만 남기며 Master와 상세 시트에서 제외한다. 이번 세 파일은 모두 `completed`다.

## 주요 미확인 정보

- T01: Reward 기하량의 simulator API와 실물 변수별 취득 방법 전체. Force filter window 등 상세 처리 설정.
- T02: 제공 accepted PDF의 DOI/arXiv 식별자, 실제 F/T 모델·정확한 장착 위치·보정 처리, task critic의 전체 입력, goal/entrance 판정 tolerance.
- T03: Critic의 상세 입력, raw sensor 영상→force reconstruction 내부 설정, Binary threshold, FoundationPose의 runtime geometry 입력, 일부 reward·encoder 학습 구현 상세.
- 공통: 코드 실행·실험 재현·연결 영상 및 별도 supplement는 수행하지 않았다. 문헌의 입력 구조·보고 결과를 확인한 작업이다.

## 형식 검증에서 확인할 사항

최종 파일 검증에서 다음을 확인했다.

- Manifest의 3개 SHA-256이 원래 PDF와 일치한다.
- 신규 논문 Markdown 3개가 모두 1–16절의 공통 구조를 유지한다.
- Master CSV는 3행·54열이며 Excel Master의 모든 셀 내용과 일치한다.
- Excel은 지정한 7개 시트를 포함한다. 상세 5개 시트의 행 수는 Object_Info 12, Tactile 29, Force_Wrench 15, Privileged_Info 15, Evidence 15다.
- 시트 미리보기의 한글·줄바꿈을 검수했으며 저장 파일의 고정 행/열과 표 구조를 확인했다.
- 데이터셋 내부 Markdown 링크가 연결되고 공개 파일 및 XLSX 내부 XML에 로컬 절대경로가 없다. 결과 폴더에 PDF 사본은 없다.
- 기존 `docs/literature/papers/`는 변경되지 않았다. 기존 문서에서는 문서 안내와 문헌 색인에 진입 링크만 추가했다.

1. 수치 Pose, 연속 RGB 잠재표현, 초기 정보, 학습용 기하량의 구분이 원하는 세밀도인지.
2. 정책·controller·safety critic의 입력을 분리한 표와 원문 위치가 충분한지.
3. 논문당 Master 1행 + 상세 시트의 항목별 행 구조가 전체 문헌 확장에 적합한지.

검증 완료 기록은 파일 구조·표 간 일치·링크·공개 경로 점검을 뜻한다. 연구 결과의 독립 실험 재현 또는 전체 문헌 분석 완료를 뜻하지 않는다. Commit과 Push는 수행하지 않았다.
