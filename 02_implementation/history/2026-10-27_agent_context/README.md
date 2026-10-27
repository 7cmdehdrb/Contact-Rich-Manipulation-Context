# 에이전트 컨텍스트 정리 전 백업

2026-10-27 작업 시작 당시의 원문을 보존한다. 커밋뿐 아니라 당시 작업트리 수정도 포함한다. 기본 작업 컨텍스트가 아니며 과거 환경·지침 조사 요청 시에만 읽는다. 개별 과거 환경 설명·개발 로그는 원래 위치에 보존하되 삭제된 절을 가리키던 링크는 백업 원문으로 연결하고, 현재 진입 문서에서 이전 계열 목록을 제거했다.

원본은 workspace 상대 경로를 유지한 `.md.txt` 파일이다. 내용은 원본 바이트 그대로이며 확장자는 과거 상대 링크가 현재 문서 검사에 섞이지 않도록 붙였다. [SHA-256 manifest](../../../03_assets/archives/2026-10-27_agent_context/manifest.json)에 원래 경로·해시·크기·줄 수를 기록한다.

| 원본 | 보존본 |
| --- | --- |
| `AGENTS.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/AGENTS.md.txt) |
| `example/Contact-Rich-Manipulation-Context/AGENTS.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/AGENTS.md.txt) |
| `example/Contact-Rich-Manipulation-Context/README.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/README.md.txt) |
| `example/Contact-Rich-Manipulation-Context/00_guidelines/AGENT_RULES.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/00_guidelines/AGENT_RULES.md.txt) |
| `example/Contact-Rich-Manipulation-Context/00_guidelines/DOCUMENT_STRUCTURE.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/00_guidelines/DOCUMENT_STRUCTURE.md.txt) |
| `example/Contact-Rich-Manipulation-Context/00_guidelines/09_DEVELOPMENT_GUIDE.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/00_guidelines/09_DEVELOPMENT_GUIDE.md.txt) |
| `example/Contact-Rich-Manipulation-Context/00_guidelines/10_WORKSPACE_GUIDE.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/00_guidelines/10_WORKSPACE_GUIDE.md.txt) |
| `example/Contact-Rich-Manipulation-Context/00_guidelines/11_TRAINING_LOG_CLEANUP.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/00_guidelines/11_TRAINING_LOG_CLEANUP.md.txt) |
| `example/Contact-Rich-Manipulation-Context/00_guidelines/12_ENVIRONMENT_FILE_STRUCTURE.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/00_guidelines/12_ENVIRONMENT_FILE_STRUCTURE.md.txt) |
| `example/Contact-Rich-Manipulation-Context/00_guidelines/README.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/00_guidelines/README.md.txt) |
| `example/Contact-Rich-Manipulation-Context/00_guidelines/rules/document-formatting.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/00_guidelines/rules/document-formatting.md.txt) |
| `example/Contact-Rich-Manipulation-Context/01_plan/00_HANDOFF_BRIEF.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/01_plan/00_HANDOFF_BRIEF.md.txt) |
| `example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md.txt) |
| `example/Contact-Rich-Manipulation-Context/02_implementation/logs/README.md` | [원문](../../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/02_implementation/logs/README.md.txt) |

복구가 필요하면 현재 작업트리와 해당 원문을 먼저 비교한 뒤 필요한 파일·부분만 복사한다. 전체 덮어쓰기나 `reset --hard`로 사용자 변경을 지우지 않는다. 이 백업은 환경 실행 코드나 학습 로그의 백업이 아니다.

과거 문서의 링크만 변경한 파일도 manifest에 원문을 보존했다. 해당 파일 목록과 해시는 manifest를 확인한다.
