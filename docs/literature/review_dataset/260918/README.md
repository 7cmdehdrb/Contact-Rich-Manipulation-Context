# 260918 Review Dataset

[문헌 색인](../../README.md)

공통 Review 질문에 맞추어 PDF 원문을 새로 읽고 비교하는 독립 데이터셋이다. 기존 `docs/literature/papers/`의 지식베이스와 별개이며 같은 논문도 이번 분석용 Markdown을 새로 만든다.

| 데이터셋 | 범위 | 결과 |
| --- | --- | --- |
| [Batch 001](batch_001/README.md) | `260918/`의 알파벳순 첫 15개 PDF | Relevant 5편, Partially Relevant 3편, PASS 7개. 신규 분석 8개 |
| [test_pdfs 검증본](test_pdfs/README.md) | 별도 `test_pdfs/`의 3개 PDF | 승인된 형식 검증본. Batch 001에 합산하지 않음 |

`260918/`에서 발견한 전체 PDF는 106개다. 이번에 검토하지 않은 91개는 후속 진행 결정을 기다리는 범위이며 내용·관련성을 판정하지 않았다. 각 dataset의 Manifest가 해당 범위의 PDF 파일 수, 고유 논문, PASS, 읽은 범위를 관리한다. 전체 폴더의 분석 완료를 뜻하지 않는다.

현재 결과는 [Batch 001 종합 비교](batch_001/synthesis/literature-synthesis.md), [CSV](batch_001/tables/paper_comparison.csv), [Excel](batch_001/tables/paper_comparison.xlsx)에서 확인할 수 있다. Commit/Push는 수행하지 않았다.
