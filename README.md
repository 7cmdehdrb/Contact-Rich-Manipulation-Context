# Contact-Rich Manipulation — Research Handoff

**기준일: 2026-10-14 · 대상: Contact-Rich Manipulation 전체 흐름과 석사생 1의 Blind Sweeping 연구 · 문서 언어: 한국어**

초기 시각 정보와 상위 계획으로 준비된 시작 조건에서, 조작 중 지속적인 시각 추적 없이 손목 힘·토크와 손의 촉각 피드백을 이용해 물체를 미는 하위 정책을 연구한다. 지금의 우선순위는 복잡한 회피·간섭 판별 기능을 늘리는 것이 아니라, **제한된 센싱과 불확실한 접촉 조건에서 Blind Sweeping이 어디까지 가능한지 검증하는 것**이다.

이 저장소는 연구·개발 맥락을 인계하는 문서 전용 submodule이다. 코드 없이도 전체 연구 흐름과 현재 상태를 이해하도록 프로젝트 수준 설명·계획·결정·로그를 모은다. 구현 코드는 상위 workspace의 `src/inspire_sweep_baseline`, `src/axia80_feasibility`에서 관리한다. 참고 환경 설명은 `example/Sweep-Policy/docs`, 두 프로젝트와 무관한 일반 지식은 workspace 루트 `docs`에 둔다.

현재 baseline은 Joint Position action을 사용하는 구현 기준선이며, 발표의 57D/8D·OSC 설계 및 최종 Blind 정책과 구분한다. [현재 활성 환경](02_implementation/08_ACTIVE_ENVIRONMENTS.md) · [Workspace·문서 지도](00_guidelines/10_WORKSPACE_GUIDE.md) · [개발 원칙](00_guidelines/09_DEVELOPMENT_GUIDE.md)에서 역할·상속·실행 경로를 확인한다.

[지침](00_guidelines/README.md) · [연구·계획](01_plan/README.md) · [구현 기록](02_implementation/README.md) · [정적 자산](03_assets/README.md)

## 저장소 구조

```text
Contact-Rich-Manipulation-Context/
├── AGENTS.md                 에이전트 필수 읽기 진입점
├── README.md                 전체 문서 지도
├── 00_guidelines/            지침·템플릿·문서 관리 도구와 테스트
├── 01_plan/                  아이디어·연구 설계·계획·문헌·발표
├── 02_implementation/        실제 코드 설명·상태·개발 로그·수행한 실험
└── 03_assets/                이미지·CSV·XLSX·PDF·영상·서지·원시 결과
```

문서의 분류·작성 위치·읽기 순서·이동과 검증 절차는 [문서 구조 규칙](00_guidelines/DOCUMENT_STRUCTURE.md)에 정의한다. 계획과 적용 코드는 서로 연결하며, 정적 자료는 자산 폴더에 두고 문서에서 상대 링크로 참조한다. Git·편집기 등 숨김 설정은 도구가 요구하는 위치를 유지한다.

## 처음 읽는 사람과 에이전트

1. [AGENTS.md](AGENTS.md) → [프로젝트 작업 지침](00_guidelines/AGENT_RULES.md)과 [문서 구조 규칙](00_guidelines/DOCUMENT_STRUCTURE.md): 필수 읽기 순서, 작업 원칙, 문서 관리 기준.
2. [00_HANDOFF_BRIEF.md](01_plan/00_HANDOFF_BRIEF.md): 다른 대화에 한 파일만 전달할 때 사용할 자립형 요약.
3. [10_WORKSPACE_GUIDE.md](00_guidelines/10_WORKSPACE_GUIDE.md): 전체 구조, 문서의 관리 위치와 프로젝트 흐름.
4. [01_PROJECT_OVERVIEW.md](01_plan/01_PROJECT_OVERVIEW.md) → [03_DECISIONS_AND_OPEN_QUESTIONS.md](01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md) → [04_NEXT_ACTIONS.md](01_plan/04_NEXT_ACTIONS.md): 현재 연구와 다음 작업.

이전 논의의 이유가 필요하면 미팅 이력을, 구현 작업을 시작한다면 활성 환경·개발 지침·코드 현황과 실제 코드를 추가로 읽는다. 현재 방향만 필요한 에이전트에게 과거 자료부터 읽혀 구안을 최신 사양으로 오해하게 만들지 않는다.

| 파일 | 목적 |
| --- | --- |
| [프로젝트 개요](01_plan/01_PROJECT_OVERVIEW.md) | 문제 정의, 시스템 경계, 센싱, 목표와 비목표, 용어 |
| [시간순 미팅·논의 이력](01_plan/02_MEETING_HISTORY.md) | 9월 8일 이전 배경부터 9월 14일까지의 변화, 교수 피드백과 학생 제안의 구분 |
| [결정·미정·보류 목록](01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md) | 현재 기준, 변경된 가정, 아직 결정하면 안 되는 사양 |
| [다음 작업과 완료 기준](01_plan/04_NEXT_ACTIONS.md) | 우선순위, 의존관계, 산출물, 다음 미팅 준비 |
| [구현·평가 설계 메모](01_plan/05_IMPLEMENTATION_AND_EVALUATION.md) | 관측 경계, 시뮬레이션 센서 모델, 실험·평가·종료 판정의 설계 초안 |
| [출처와 확인 범위](01_plan/06_SOURCE_REGISTER.md) | 첨부 문서·대화 기반 정보·추가 확인 자료와 주장별 근거 |
| [코드·장비 현황](02_implementation/07_CODE_AND_HARDWARE_STATUS.md) | 현재 활성 코드·과거 구현/센서 보고·실물 미확인, 과거 PPO와 실행 확인 항목 |
| [활성 환경](02_implementation/08_ACTIVE_ENVIRONMENTS.md) | 두 활성 패키지의 역할, 환경 상속, 적용 설정과 실행 명령 |
| [개발 지침](00_guidelines/09_DEVELOPMENT_GUIDE.md) | Manager-based RL의 OOP 원칙, 계약·로그·검증·문서 갱신 |
| [Workspace와 문서 지도](00_guidelines/10_WORKSPACE_GUIDE.md) | 전체 구조, 세 문서 영역, 패키지·도구의 연결 |
| [개발 로그](02_implementation/logs/README.md) | 10월 진행·재생 기록과 Workspace 정리 |
| [과거 설계](01_plan/history/README.md) | 이전 README와 7월 TODO, 과거 설정 요청 기록 |
| [문헌조사 색인](01_plan/literature/README.md) | 주제별 조사 보고서, 센서 정보에서 행동까지의 연결, 논문 근거와 프로젝트 제안의 구분 |
| [연구 로그 템플릿](00_guidelines/templates/RESEARCH_LOG.md) | 실험, 실패, 센서 확인, 미팅 결정, 에이전트 인계 기록 |

## 문헌조사 자료

주제별 비교 보고서는 `01_plan/literature/reviews/`에 **조사 기준일 + 주제명**으로 저장한다. 목록과 관리 규칙은 [문헌조사 색인](01_plan/literature/README.md)에 정리한다. 기존 번호 문서는 역할에 따라 계획·구현·지침 폴더에 나누어 보관한다. 문헌조사 보고서의 제안을 자동으로 확정 사양에 반영하지 않는다.

각 그룹의 논문별 바로가기는 [조사 그룹 안내](01_plan/literature/reviews/README.md), 전체 상세 노트는 [논문 색인](01_plan/literature/papers/README.md)에서 찾는다. 현재 등록된 보고서·목록은 다음과 같다.

- [2026-09-14 — Blind Sweep을 위한 F/T·촉각 기반 Pushing 문헌 조사](01_plan/literature/reviews/2026-09-14_blind-sweep-force-torque-tactile.md)
- [2026-09-15 — IROS 2023–2025 Tactile·F/T 기반 RL 관련 논문 제목 선별](01_plan/literature/reviews/2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md)
- [2026-09-16 — Binary Tactile·F/T 기반 RL 신규 문헌 조사](01_plan/literature/reviews/2026-09-16_binary-tactile-wrench-rl.md)
- [2026-09-16 — Binary Tactile·Wrench 입력 처리 및 비교 실험 제안](01_plan/literature/reviews/2026-09-16_binary-tactile-wrench-design-notes.md)
- [2026-09-18 미팅 검토 자료 — 힘·촉각 기반 Sweeping의 선행연구와 적용 후보](01_plan/literature/reviews/2026-09-17_force-tactile-sweeping-meeting.md) — 2026-09-17까지의 문헌을 바탕으로 한 논의 자료이며 확정 사양·미팅 결과가 아님.
- [2026-09-21 — Sweeping의 숨은 물리 조건에 대한 명시적 추정과 이력 기반 대응](01_plan/literature/reviews/2026-09-21_sweeping-physical-parameter-adaptation.md)
- [2026-09-21 — Wrist Wrench를 관측·피드백으로 사용하는 Manipulation 연구](01_plan/literature/reviews/2026-09-21_wrist-wrench-manipulation-survey.md) — 후속 정독: [FoAR](01_plan/literature/papers/2025-he-foar.md)
- [사용자 발굴 논문 — 누적 목록](01_plan/literature/reviews/user-found-papers.md)

## 현재 상태를 오해하지 않기 위한 핵심

- **Blind는 시스템 전체에서 카메라를 제거한다는 뜻이 아니다.** 초기 시각 관측은 허용하고, 한 번의 하위 조작 실행 중 물체 시각 추적을 갱신하지 않는다는 의미다.
- **상위 판단기가 접근과 시작 조건을 제공한다.** 그렇다고 실제 접촉 위치나 촉각 감지가 완벽하게 보장되는 것은 아니다.
- **9월 13일의 간섭 감지·중단 제안은 9월 14일에 후순위가 되었다.** 안전 정지까지 제거하라는 뜻은 아니다.
- **Clutter는 배경이지, 복잡도 증가 자체가 현재 기여는 아니다.** 단일 물체로 기본 문제를 분리해 검증할 수 있지만 최종 환경이 단일 물체로 확정된 것도 아니다.
- **9월 10일에 보고된 OSC 기반 Sweeping은 사전 검증이다.** 당시 정책에 F/T·촉각 관측은 없었고, 최종 Blind 정책이나 Sim-to-Real 성공을 입증하지 않는다.
- **정책의 촉각 미사용과 별도 센서 시험 부재는 다르다.** 9월 10일에는 별도로 시험하던 압저항 촉각 센서의 신호 부족이 보고되었다. 이를 구매 예정 Hand·Axia80의 실측 성능으로 옮기지 않는다.
- **17차원 촉각은 센서 영역별 축약 표현의 후보다.** 실제 원시 데이터 구조·센서 위치·해상도·샘플링률의 검증과 구분한다.

## 문서의 상태 표기

`CONFIRMED_DIRECTION`은 회의·대화에서 확인된 방향이지 실험 검증 완료가 아니다. `REPORTED_IMPLEMENTED`는 과거 구현 보고, `PROPOSED`는 설계·실험 제안, `OPEN`은 미정, `DEFERRED`는 후순위, `SUPERSEDED`는 후속 논의로 수정된 가정, `HISTORICAL`은 배경 이력을 뜻한다.

출처 ID는 [출처 목록](01_plan/06_SOURCE_REGISTER.md)에 정의한다. 문서의 수정 시각보다 **해당 논의가 발생한 날짜와 적용 범위**를 우선한다. 과거 페이지의 ‘최종 제안’이라는 표현도 후속 미팅에서 변경될 수 있다. 새 에이전트의 실험·설계 제안은 교수 지시와 별도로 표시한다.

## 다른 에이전트에 전달할 시작 요청

```text
이 저장소는 Blind Sweeping 연구 인계 문서다.
AGENTS.md와 01_plan/00_HANDOFF_BRIEF.md를 먼저 읽고,
01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md와 01_plan/04_NEXT_ACTIONS.md를 확인하라.
현재 확정 방향, 미정 사양, 다음 우선 작업을 구분한 뒤 내가 요청한 작업을 수행하라.
과거 제안, 다른 학생의 주제, 에이전트가 만든 설계안을 현재 확정 요구사항으로 승격하지 말라.
구현 작업은 02_implementation/08_ACTIVE_ENVIRONMENTS.md와 00_guidelines/09_DEVELOPMENT_GUIDE.md,
실제 활성 코드와 실행 환경을 읽은 뒤 시작하라.
```

## 갱신 원칙

새 미팅이 생기면 먼저 이력과 결정 목록을 갱신하고, 현재 요약·다음 작업·관련 기술 문서를 함께 수정한다. 이전 결정을 삭제해 역사를 지우지 말고 대체된 이유를 남긴다. 실험 성과는 코드 커밋·설정·로그·평가 조건과 연결될 때에만 완료 상태로 올린다.

---

### `reference.bib`

```bash
python 00_guidelines/scripts/copy_bib_attachments.py 03_assets/bibliography/ref.bib \
  --destination "03_assets/literature/source_pdfs/260918"
```

위 복사 도구는 서지 파일에 기록된 원본 경로를 읽는다. 현재 접근 가능한 원본과 PDF 복제 범위는 [문헌 자료 관리 규칙](01_plan/literature/README.md#자료와-출처-관리)을 확인한다. 기존 Review Dataset의 `local_path`는 당시 제공된 원문 경로 기록이며, 이번 정리에서 원문 PDF를 새로 확보한 것은 아니다.

이전 경로와 새 경로의 전체 대응은 [이관 경로표](03_assets/repository/document-path-map.csv), 수행한 검사와 확인 범위는 [재구성 로그](02_implementation/logs/2026-10-14_document_reorganization.md)에 남긴다.
