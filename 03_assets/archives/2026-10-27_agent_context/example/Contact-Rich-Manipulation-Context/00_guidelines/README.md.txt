# 지침과 문서 관리 도구

[전체 안내](../README.md) · [연구·계획](../01_plan/README.md) · [구현 기록](../02_implementation/README.md) · [정적 자산](../03_assets/README.md)

이 폴더는 다른 에이전트가 같은 기준으로 연구 맥락을 읽고 문서·코드 기록을 관리하기 위한 지침을 모은다. 기준일: 2026-10-14.

| 작업 | 기준 문서 |
| --- | --- |
| 모든 프로젝트 작업의 연구 범위·근거·상태 판단 | [에이전트 운영 지침](AGENT_RULES.md) |
| 문서 분류·작성·읽기·이동·참조 검증 | [문서 구조 규칙](DOCUMENT_STRUCTURE.md) |
| Markdown과 수식 작성·검사 | [문서 형식 규칙](rules/document-formatting.md) |
| 활성 코드 변경·환경 계약·재현 가능한 로그 | [개발 지침](09_DEVELOPMENT_GUIDE.md) |
| Inspire Sweep 환경의 역할별 파일 배치·버전 통합·이관 검증·복구 | [환경 파일 구조](12_ENVIRONMENT_FILE_STRUCTURE.md) |
| 문서 submodule과 코드 workspace의 역할·외부 링크 | [Workspace 안내](10_WORKSPACE_GUIDE.md) |
| 실험 조건·결과·실패·인계 기록 | [연구 로그 템플릿](templates/RESEARCH_LOG.md) |

루트 [AGENTS.md](../AGENTS.md)는 필수 지침으로 들어가는 진입점이다. 각 지침의 본문은 위 문서를 기준으로 유지하고, 연구 설계·실험 결과는 해당 영역에 작성한다.

## 문서 관리 도구

| 도구 | 용도 |
| --- | --- |
| [check_document_links.py](scripts/check_document_links.py) | 파일·anchor·정적 자산·데이터셋 참조 검사 |
| [check_markdown_math.py](scripts/check_markdown_math.py) | 변경 Markdown의 수식 구문·GitHub 호환성 검사 |
| [copy_bib_attachments.py](scripts/copy_bib_attachments.py) | BibTeX의 attachment 필드로 연결된 파일 복사 |
| [plot_reward_individual.py](scripts/plot_reward_individual.py) | 제안 보상 항을 개별 그래프로 표시하는 문서용 도구 |
| [tests/](tests/) | 문서 관리 Python 도구의 테스트 |

그림 생성 도구의 예시 파라미터는 연구의 확정값이나 실행 실험값과 구분한다. 검사 실행 명령과 완료 기준은 [문서 구조 규칙](DOCUMENT_STRUCTURE.md#검증과-완료-기준)에 모아 관리한다.
