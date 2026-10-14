# 정적 자산과 원시 근거

[전체 안내](../README.md) · [지침](../00_guidelines/README.md) · [연구·계획](../01_plan/README.md) · [구현 기록](../02_implementation/README.md)

기준일: 2026-10-14. 이 폴더는 문서가 참조하는 이미지·표·영상·서지 파일과 실험 원시 근거를 저장한다. 자료를 설명하는 연구·계획 문서는 `01_plan/`, 구현·실험 문서는 `02_implementation/`에서 읽는다.

| 위치 | 저장 자료 | 설명 문서 |
| --- | --- | --- |
| [학습 실행 UML](inspire-sweep-training.html), [환경 상속 UML](inspire-sweep-inheritance.html) | Baseline의 Isaac Lab·RSL-RL 연결, 네 환경의 설정 상속과 callable 연결을 보여주는 자체 포함 HTML | [활성 환경](../02_implementation/08_ACTIVE_ENVIRONMENTS.md), [작성·검증 기록](../02_implementation/logs/2026-10-14_inspire_sweep_uml.md) |
| [img/](img/) | 연구·발표·실험 그림과 이미지 | [발표 안내](../01_plan/presentation/README.md), [실험 기록](../02_implementation/README.md#수행한-실험과-재현) |
| [csv/](csv/) | 학회별 논문 제목 목록 | [문헌조사 안내](../01_plan/literature/README.md) |
| [pdf/](pdf/) | 보관된 발표 PDF | [발표 안내](../01_plan/presentation/README.md) |
| [video/](video/) | 보관된 영상 | 영상 조건·확인 범위는 해당 참조 문서에서 확인 |
| [artifacts/](artifacts/) | 실험 CSV·metadata·run.log 등 원시 산출물 | [Axia80 실험 결과](../02_implementation/experiments/2026-09-22_axia80_ft_sensor_feasibility.md) |
| [global_task/roadmap/images/](global_task/roadmap/images/) | roadmap의 그림 | [Roadmap 안내](../01_plan/global_task/roadmap/README.md) |
| [literature/review_dataset/](literature/review_dataset/) | 문헌 데이터셋의 Manifest·비교 CSV·XLSX | [Review Dataset 안내](../01_plan/literature/review_dataset/260918/README.md) |
| [repository/document-path-map.csv](repository/document-path-map.csv) | 폴더 재구성 전후 경로 대응(저장소 루트 기준) | [재구성 로그](../02_implementation/logs/2026-10-14_document_reorganization.md) |
| [bibliography/ref.bib](bibliography/ref.bib), [literature/papers/reference.bib](literature/papers/reference.bib) | 서지 레코드 | [문헌조사 안내](../01_plan/literature/README.md) |

## 추가·참조 규칙

같은 원시 근거를 여러 폴더에 복제하기보다 기준 파일 하나를 유지하고 관련 문서에서 상대 링크로 연결한다. 새 자료는 용도에 맞는 위 하위 영역에 저장한다. 실험 자산은 날짜·실험 ID·run 조건을 설명 문서와 연결하고, 기존 결과를 덮어쓰는 대신 새 run의 경로를 구분한다.

자료의 단위·좌표계·생성 조건·출처·해석 한계는 관련 Markdown에 기록한다. 파일만 존재한다는 이유로 원문 정독·정량 검증·학습 성공·실물 성능을 확인했다고 쓰지 않는다. 원문 PDF의 저장·복제 정책은 [개별 논문 지침](../01_plan/literature/papers/README.md)을 따른다.

Review Dataset의 `analysis_file`, `analysis_note_path`는 **각 CSV 파일의 부모 폴더 기준**으로 `01_plan/literature/`의 분석 Markdown을 가리킨다. XLSX의 같은 경로 열도 workbook의 부모 폴더 기준으로 유지한다. 원본 PDF의 `local_path`·파일명·SHA-256은 출처 추적 정보이며 현재 저장소에서 열 수 있는 분석 노트 링크와 구분한다.

이미지·영상·PDF 경로를 옮길 때 이를 참조하는 Markdown·HTML·스크립트와 Git LFS 패턴도 확인한다. 분류·이동·참조 갱신과 검사 절차는 [문서 구조 규칙](../00_guidelines/DOCUMENT_STRUCTURE.md)을 따른다.

현재 보관된 PDF는 발표 자료다. Review Dataset의 `local_path`에 등장하는 논문 원문과 BibTeX `file`의 Windows Zotero 경로는 외부 제공 원본의 출처 기록이며, 해당 원문을 이번 이동으로 저장소에 새로 추가하지 않았다. Axia80 metadata·run.log의 실행 위치도 당시 provenance로 보존한다. 현재 산출물은 위 `artifacts/`에서 찾는다.
