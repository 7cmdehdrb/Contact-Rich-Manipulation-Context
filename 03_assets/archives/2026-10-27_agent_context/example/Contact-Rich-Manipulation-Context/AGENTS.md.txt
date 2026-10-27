# Agent Operating Instructions

기준일: 2026-10-14. 이 저장소는 석사생 1의 초기 시각 이후 힘·촉각 기반 Blind Sweeping 연구를 인계하는 문서 저장소다.

작업 전에 다음을 순서대로 읽는다.

1. [프로젝트 작업 지침](00_guidelines/AGENT_RULES.md): 연구 범위, 근거와 상태의 구분, 코드·논문·결과 기록 원칙.
2. [문서 구조와 생산 규칙](00_guidelines/DOCUMENT_STRUCTURE.md): 네 폴더의 책임, 작업별 읽기 경로, 작성·이동·검증 절차.
3. [인계 요약](01_plan/00_HANDOFF_BRIEF.md), [결정·미정 목록](01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md), [다음 작업](01_plan/04_NEXT_ACTIONS.md).

Markdown을 작성하거나 수정할 때는 [문서 형식 규칙](00_guidelines/rules/document-formatting.md)을 함께 읽는다. 코드 작업은 [코드·장비 상태](02_implementation/07_CODE_AND_HARDWARE_STATUS.md), [활성 환경](02_implementation/08_ACTIVE_ENVIRONMENTS.md), [개발 지침](00_guidelines/09_DEVELOPMENT_GUIDE.md)과 실제 활성 코드를 읽는다. 문서 이동·workspace 작업은 [Workspace 안내](00_guidelines/10_WORKSPACE_GUIDE.md)를 읽는다.

루트의 네 콘텐츠 폴더는 `00_guidelines/`, `01_plan/`, `02_implementation/`, `03_assets/`다. 루트 `README.md`는 전체 탐색 입구이며, 이 파일은 에이전트 자동 발견을 위한 진입점이다. 구체적인 규칙은 위 문서에서 관리한다.

학습 실행·명령 안내 시 [개발 지침의 학습 실행 정책](00_guidelines/09_DEVELOPMENT_GUIDE.md#학습-실행-정책)을 따른다. 현재 실행기는 `train.py`이며 자동 복구 실행기는 사용 중단·코드 보존 상태다.
