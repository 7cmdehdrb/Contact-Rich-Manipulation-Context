# 아이디어·연구 설계·계획 안내

[전체 문서 안내](../README.md) · [지침](../00_guidelines/README.md) · [구현 기록](../02_implementation/README.md) · [정적 자산](../03_assets/README.md) · [문헌조사](literature/README.md)

이 폴더는 연구 방향·아이디어·설계·계획과 그 문헌 근거를 담당한다. 연구의 현재 방향은 인계·결정 문서에서, 선행연구의 근거는 문헌조사에서 확인한다. 아래 표는 계획 문서와 관련 구현 기록을 함께 찾는 출발점이다. 실제 코드 계약·개발 로그·수행한 실험은 `02_implementation/`에 둔다.

**구조 기준일: 2026-10-14.** 이 submodule은 전체 프로젝트 flow·연구·계획·결정·상태·로그의 문서 저장소다. 참고 환경 내부 설명은 workspace의 `example/Sweep-Policy/docs`, 두 프로젝트와 무관한 일반 지식은 루트 `docs`에서 관리한다. code-local API·자산·실행 참고서는 각 코드 README에서 연결한다. [전체 구조와 연결](../00_guidelines/10_WORKSPACE_GUIDE.md)을 먼저 보면 각 문서의 역할을 찾을 수 있다.

## 목적별로 찾기

| 확인할 내용 | 시작 문서 | 함께 볼 문서 |
| --- | --- | --- |
| 연구를 처음 이해하거나 다른 에이전트에게 인계 | [연구 요약](00_HANDOFF_BRIEF.md) | [프로젝트 개요](01_PROJECT_OVERVIEW.md) |
| Workspace 구조·패키지 역할·문서 위치 | [Workspace와 문서 지도](../00_guidelines/10_WORKSPACE_GUIDE.md) | [개발 지침](../00_guidelines/09_DEVELOPMENT_GUIDE.md) |
| 현재 활성 환경의 상속·관측·제어·명령 | [활성 환경 안내](../02_implementation/08_ACTIVE_ENVIRONMENTS.md) | [코드·장비 현황](../02_implementation/07_CODE_AND_HARDWARE_STATUS.md) |
| Omni 환경의 실제 구성과 보상 변경 계획 | [Omni 환경](../02_implementation/environments/OMNI_ENVIRONMENT.md) | [Omni 보상 계획](environments/OMNI_REWARD_PLAN.md): 적용 코드와 계획 구분 |
| 개발 방식·새 환경의 기록 항목·검증 | [개발 지침](../00_guidelines/09_DEVELOPMENT_GUIDE.md) | [연구 로그 템플릿](../00_guidelines/templates/RESEARCH_LOG.md) |
| 개발·재생 실패 관찰과 이관 내역 | [개발 로그 목록](../02_implementation/logs/README.md) | [과거 설계와 요청](history/README.md) |
| 단일 물체 Blind 환경의 과거 구현 명세 | [2026-09-26 구현 계획](experiments/2026-09-26_blind_sweeping_build_plan.md) | 57D/8D·OSC 계획이며 현 활성 코드와 구분 |
| 상위 탐색·전체 시스템의 배경과 후보 로드맵 | [Global Task 안내](global_task/README.md) | [Roadmap 안내](global_task/roadmap/README.md): 하위 연구 필수 구현 목록이 아님 |
| 현재 결정·미정 사항과 다음 작업 | [결정 목록](03_DECISIONS_AND_OPEN_QUESTIONS.md) | [다음 작업](04_NEXT_ACTIONS.md) |
| 방향이 바뀐 이유와 교수 피드백 | [미팅 이력](02_MEETING_HISTORY.md) | [출처와 확인 범위](06_SOURCE_REGISTER.md) |
| 구현·실험 설계와 실제 준비 상태 | [구현·평가 설계](05_IMPLEMENTATION_AND_EVALUATION.md) | [코드·장비 현황](../02_implementation/07_CODE_AND_HARDWARE_STATUS.md) |
| Axia80 simulation 구현과 재현 | [구현 가이드](../02_implementation/experiments/2026-09-22_axia80_ft_sensor_implementation.md) | [실험 결과](../02_implementation/experiments/2026-09-22_axia80_ft_sensor_feasibility.md) |
| 최종 중간발표의 연구 동기·방법·평가 계획 | [발표 문서 안내](presentation/README.md) | [발표 구성과 설계 현황](presentation/00_Presentation_Overview_and_Design_Status.md) · [보상 설계](presentation/04_Reward_Formulation.md) · [평가와 일정](presentation/06_Evaluation_and_Schedule.md) |
| 과거 발표 구상과 연구 메모 | [1차 중간발표 초안](presentation/1st_draft/00_Mid_Presentation.md) | [연구 논리 메모](memo/pres1.md): 당시 제안과 현행 결정을 구분 |
| Research Motivation의 물체 정보·축약 촉각 근거 | [2.1 신규 문헌 조사: 4편 비교](literature/reviews/2026-09-18_reduced-tactile-compensation-survey.md) | [당시 Research Motivation 초안](presentation/1st_draft/01_Research_Motivation.md) |
| 동일 schema의 Review용 PDF 재분석 | [260918 Review Dataset: 106개 전체 검토본](literature/review_dataset/260918/README.md) | [전체 질문별 횡단 비교](literature/review_dataset/260918/synthesis/literature-synthesis.md) |
| 특정 조사에서 선정한 논문 | [조사 그룹 안내](literature/reviews/README.md) | [문헌조사 전체 색인](literature/README.md) |
| 선행연구를 바탕으로 논의할 적용 후보 | [9월 18일 미팅 검토 자료](literature/reviews/2026-09-17_force-tactile-sweeping-meeting.md) | 촉각·F/T·RL 결합·보상별 검토안과 근거 |
| 제목을 아는 논문의 상세 정리 | [전체 논문 색인](literature/papers/README.md) | 각 노트 상단의 원래 조사 링크 |
| 직접 제공한 논문의 등록·정독 상태 | [사용자 발굴 논문](literature/reviews/user-found-papers.md) | [전체 논문 색인](literature/papers/README.md) |
| Inspire Hand Sweeping의 단계별 학습 결과와 후속 검증 | [학습 기록](../02_implementation/logs/2026-10-12_inspire_hand_training.md) | [최종 정책 구현·검증 TODO](TODO.md) · [구현·평가 설계](05_IMPLEMENTATION_AND_EVALUATION.md) |
| 새 실험 기록 작성 | [연구 로그 템플릿](../00_guidelines/templates/RESEARCH_LOG.md) | [다음 작업의 완료 기준](04_NEXT_ACTIONS.md) |

## 문헌을 읽는 경로

조사별로 읽을 때는 **[조사 그룹](literature/reviews/README.md) → 보고서의 논문 바로가기 → 상세 노트** 순서로 이동한다. 상세 노트의 상단에는 원래 조사 항목으로 돌아가는 링크가 있다. 제목만 알고 있으면 **[전체 논문 색인](literature/papers/README.md)**에서 찾는다.

`literature/reviews/`는 주제별 조사·선별·사용자 발굴 목록과 그 조사에서 나온 설계 제안을 모은다. `literature/papers/`는 논문별 상세 정리를 보관한다. 상세 노트가 아직 없는 항목은 보고서의 요약·서지만 연결하고, 정독 완료로 표시하지 않는다.

문헌의 제안은 프로젝트의 확정 사양과 구분한다. 연구 내용의 상태는 각 문서의 기준일과 근거를 따르며, 탐색 링크를 갱신한 날짜가 연구 결정을 바꾸지는 않는다.
