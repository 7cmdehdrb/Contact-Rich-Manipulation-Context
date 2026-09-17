# Contact-Rich Manipulation — Research Handoff

**기준일: 2026-09-14 · 대상: 석사생 1의 Blind Sweeping 연구 · 문서 언어: 한국어**

초기 시각 정보와 상위 계획으로 준비된 시작 조건에서, 조작 중 지속적인 시각 추적 없이 손목 힘·토크와 손의 촉각 피드백을 이용해 물체를 미는 하위 정책을 연구한다. 지금의 우선순위는 복잡한 회피·간섭 판별 기능을 늘리는 것이 아니라, **제한된 센싱과 불확실한 접촉 조건에서 Blind Sweeping이 어디까지 가능한지 검증하는 것**이다.

이 저장소는 연구 맥락을 인계하는 문서 저장소다. 로봇 제어·강화학습 구현 저장소가 아니며, 문서에 등장하는 설계안을 구현 완료로 간주해서는 안 된다.

[문서 안내](docs/README.md) · [조사 그룹](docs/literature/reviews/README.md) · [전체 논문](docs/literature/papers/README.md)

## 처음 읽는 사람과 에이전트

1. [AGENTS.md](AGENTS.md): 작업 원칙, 범위 이탈 방지, 증거 취급 방식.
2. [00_HANDOFF_BRIEF.md](docs/00_HANDOFF_BRIEF.md): 다른 대화에 한 파일만 전달할 때 사용할 자립형 요약.
3. [01_PROJECT_OVERVIEW.md](docs/01_PROJECT_OVERVIEW.md) → [03_DECISIONS_AND_OPEN_QUESTIONS.md](docs/03_DECISIONS_AND_OPEN_QUESTIONS.md) → [04_NEXT_ACTIONS.md](docs/04_NEXT_ACTIONS.md): 현재 연구와 다음 작업.

이전 논의의 이유가 필요하면 미팅 이력을, 구현 작업을 시작한다면 기술 문서와 코드 현황을 추가로 읽는다. 현재 방향만 필요한 에이전트에게 과거 자료부터 읽혀 구안을 최신 사양으로 오해하게 만들지 않는다.

| 파일 | 목적 |
| --- | --- |
| [프로젝트 개요](docs/01_PROJECT_OVERVIEW.md) | 문제 정의, 시스템 경계, 센싱, 목표와 비목표, 용어 |
| [시간순 미팅·논의 이력](docs/02_MEETING_HISTORY.md) | 9월 8일 이전 배경부터 9월 14일까지의 변화, 교수 피드백과 학생 제안의 구분 |
| [결정·미정·보류 목록](docs/03_DECISIONS_AND_OPEN_QUESTIONS.md) | 현재 기준, 변경된 가정, 아직 결정하면 안 되는 사양 |
| [다음 작업과 완료 기준](docs/04_NEXT_ACTIONS.md) | 우선순위, 의존관계, 산출물, 다음 미팅 준비 |
| [구현·평가 설계 메모](docs/05_IMPLEMENTATION_AND_EVALUATION.md) | 관측 경계, 시뮬레이션 센서 모델, 실험·평가·종료 판정의 설계 초안 |
| [출처와 확인 범위](docs/06_SOURCE_REGISTER.md) | 첨부 문서·대화 기반 정보·추가 확인 자료와 주장별 근거 |
| [코드·장비 현황](docs/07_CODE_AND_HARDWARE_STATUS.md) | 보고된 구현·센서 시험과 미검증 상태, 과거 PPO 설정, 실행 전 확인 항목 |
| [문헌조사 색인](docs/literature/README.md) | 주제별 조사 보고서, 센서 정보에서 행동까지의 연결, 논문 근거와 프로젝트 제안의 구분 |
| [연구 로그 템플릿](templates/RESEARCH_LOG.md) | 실험, 실패, 센서 확인, 미팅 결정, 에이전트 인계 기록 |

## 문헌조사 자료

주제별 비교 보고서는 `docs/literature/reviews/`에 **조사 기준일 + 주제명**으로 저장한다. 목록과 관리 규칙은 [문헌조사 색인](docs/literature/README.md)에 정리한다. 기존 `docs/00_...`부터 `docs/07_...`까지는 인계·현재 상태 문서로 유지하며, 문헌조사 보고서의 제안을 자동으로 확정 사양에 반영하지 않는다.

각 그룹의 논문별 바로가기는 [조사 그룹 안내](docs/literature/reviews/README.md), 전체 상세 노트는 [논문 색인](docs/literature/papers/README.md)에서 찾는다. 현재 등록된 보고서·목록은 다음과 같다.

- [2026-09-14 — Blind Sweep을 위한 F/T·촉각 기반 Pushing 문헌 조사](docs/literature/reviews/2026-09-14_blind-sweep-force-torque-tactile.md)
- [2026-09-15 — IROS 2023–2025 Tactile·F/T 기반 RL 관련 논문 제목 선별](docs/literature/reviews/2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md)
- [2026-09-16 — Binary Tactile·F/T 기반 RL 신규 문헌 조사](docs/literature/reviews/2026-09-16_binary-tactile-wrench-rl.md)
- [2026-09-16 — Binary Tactile·Wrench 입력 처리 및 비교 실험 제안](docs/literature/reviews/2026-09-16_binary-tactile-wrench-design-notes.md)
- [사용자 발굴 논문 — 누적 목록](docs/literature/reviews/user-found-papers.md)

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

출처 ID는 [출처 목록](docs/06_SOURCE_REGISTER.md)에 정의한다. 문서의 수정 시각보다 **해당 논의가 발생한 날짜와 적용 범위**를 우선한다. 과거 페이지의 ‘최종 제안’이라는 표현도 후속 미팅에서 변경될 수 있다. 새 에이전트의 실험·설계 제안은 교수 지시와 별도로 표시한다.

## 다른 에이전트에 전달할 시작 요청

```text
이 저장소는 Blind Sweeping 연구 인계 문서다.
AGENTS.md와 docs/00_HANDOFF_BRIEF.md를 먼저 읽고,
docs/03_DECISIONS_AND_OPEN_QUESTIONS.md와 docs/04_NEXT_ACTIONS.md를 확인하라.
현재 확정 방향, 미정 사양, 다음 우선 작업을 구분한 뒤 내가 요청한 작업을 수행하라.
과거 제안, 다른 학생의 주제, 에이전트가 만든 설계안을 현재 확정 요구사항으로 승격하지 말라.
구현 작업은 실제 코드와 실행 환경을 읽은 뒤에만 시작하라.
```

## 갱신 원칙

새 미팅이 생기면 먼저 이력과 결정 목록을 갱신하고, 현재 요약·다음 작업·관련 기술 문서를 함께 수정한다. 이전 결정을 삭제해 역사를 지우지 말고 대체된 이유를 남긴다. 실험 성과는 코드 커밋·설정·로그·평가 조건과 연결될 때에만 완료 상태로 올린다.