# 문서 저장소 작업 지침

현재 활성 기반은 `src/inspire_sweep_baseline`, 최신 중점 환경은 **Holding → Final**이다. `src/axia80_feasibility`는 사용하지 않는다. 이 저장소는 코드 설명·지침·변경 의도를 기록하는 문서 submodule이다.

- 모든 작업: [에이전트 운영 규칙](00_guidelines/AGENT_RULES.md)을 읽는다.
- 환경 작업: [현재 인계](01_plan/00_HANDOFF_BRIEF.md), [개발 지침](00_guidelines/09_DEVELOPMENT_GUIDE.md), [Holding·Final 안내](02_implementation/08_ACTIVE_ENVIRONMENTS.md) 중 아직 읽지 않은 해당 문서를 확인한다. 이어서 요청된 환경의 상세 문서와 실제 코드만 읽는다.
- 논문 작성·번역·첨삭: [논문 컨텍스트](04_article/README.md)와 [용어집 및 표기 기준](04_article/TERMINOLOGY.md)을 먼저 읽는다. 최신 사용자 지시를 우선하며, 논문 관련 문서의 갱신·업로드는 사용자 지시에 따라 수행한다.
- 문서 작성·수정: [문서 구조](00_guidelines/DOCUMENT_STRUCTURE.md)와 [형식 규칙](00_guidelines/rules/document-formatting.md)을 따른다.
- 경로·저장소 작업: [Workspace 안내](00_guidelines/10_WORKSPACE_GUIDE.md)를 읽는다.
- 과거 연구·이전 환경 조사: 명시적으로 필요한 경우에만 [정리 전 백업](02_implementation/history/2026-10-27_agent_context/README.md) 및 해당 역사 자료를 읽는다.

기존 버전 직접 수정과 새 파생 환경 생성을 구분하고 부모를 보존한다. 매 수정의 의도·전체 대조·검증을 개발 로그에 남긴다. 학습은 `train.py`를 사용하며 학습 로그 정리는 별도 명시적 요청에만 수행한다.
