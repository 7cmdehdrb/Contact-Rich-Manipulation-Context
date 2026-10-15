# 개발 원칙과 기록 방법

[문서 안내](../01_plan/README.md) · [Workspace 구성](10_WORKSPACE_GUIDE.md) · [활성 환경](../02_implementation/08_ACTIVE_ENVIRONMENTS.md) · [작업 지침](AGENT_RULES.md)

기준일: 2026-10-14. 이 문서는 사용자가 요청한 최소 개발 지침을 정리한다. 모든 개발 원칙이나 최종 연구 설계를 이번 정리에서 확정하는 문서는 아니다.

## Manager-based RL과 객체 지향 설계

Isaac Lab의 Manager-based Reinforcement Learning 구조와 OOP 원칙을 지킨다. 환경 설정은 Scene, Observation, Action, Event, Reward, Termination, Curriculum 및 학습 설정의 책임을 나누고, MDP 함수와 Action term은 해당 책임 안에서 동작하도록 구성한다. 환경 전체를 하나의 거대한 클래스에 덧붙이는 방식으로 변형을 쌓지 않는다.

공통 동작은 기반 설정과 재사용 가능한 구성요소에 두고, 파생 환경은 바꾸려는 조건을 명시한다. 상속으로 환경을 만들 때는 부모의 관측·보상·종료·reset이 최종 설정에 어떻게 남는지 확인한다. 부모와의 차이는 클래스 이름만으로 설명하지 않고 최종 활성 term과 실제 동작을 기록한다. 구성요소 조합이 더 명확한 경우에는 조합을 사용한다.

활성 패키지 `inspire_sweep_baseline`은 Isaac Lab 기반 클래스를 상속하지만, 보관된 프로젝트 패키지를 import하거나 상속하지 않는 독립 패키지다. 참고 구현에서 코드를 가져온 이력과 실행 중 Python 상속 관계를 구분한다. 아카이브 패키지를 다시 의존성으로 연결하려면 활성 범위 변경을 먼저 문서에 남긴다.

## Omni 운동 페널티 필수 규칙 — 2026-10-15 사용자 지시

Omni 베이스와 모든 파생 환경(v0/v1/v2/v3 및 Dex Omni, 향후 파생 포함)은 아래 네 항을 반드시 사용한다. 공통 `OmniRewardsCfg`에서 상속하며 임의로 제거·대체하지 않는다.

| 항 | 로컬 함수와 대상 | 가중치 |
| --- | --- | --- |
| Arm Action Rate | `goal_rewards.action_rate_l2`, raw Arm 6D 변화량 제곱합 | −0.03 |
| Hand Action Rate | `goal_rewards.action_rate_l2`, raw Hand 2D 변화량 제곱합 | −0.03 |
| Arm Joint Velocity | `goal_rewards.joint_vel_l2`, 이름으로 선택한 Arm 6개 실제 관절 속도 제곱합 | −0.03 |
| Hand Joint Velocity | `goal_rewards.joint_vel_l2`, 이름으로 선택한 Hand 12개 실제 관절 속도 제곱합 | −0.01 |

참고 Inspire 환경의 raw 제곱합 계산을 따르되 활성 패키지의 `mdp/goal_rewards.py`에 정의한 함수를 사용한다. `example/Sweep-Policy`의 함수를 import하지 않는다. Arm/Hand 항을 합치거나 mean, 기준값 정규화, 보상 내부 Hand 입력 clamp를 적용하지 않는다. Action 자체의 처리에서 수행하는 Hand clamp와 보상 계산은 구분한다. 함수에서 dt로 나누거나 곱하지 않고 RewardManager가 weight와 step_dt를 한 번 적용한다.

이전 정규화 함수는 과거 설정의 참조를 위해 남아 있지만 Omni 설정에서 사용하지 않는다. 구조·계수 변경은 사용자 명시 지시가 있을 때만 수행한다. 다른 보상의 상대 크기를 이유로 이 페널티를 임의로 낮추지 않는다. 모든 파생 환경에 대한 callable·계수·그룹 분리 검증을 유지한다. [적용·검증 로그](../02_implementation/logs/2026-10-15_omni_penalty_contract.md).

## 환경마다 남길 계약

환경 추가·변경 시 아래 표의 항목을 코드 위치와 함께 기록한다. 현재 환경의 공통 탐색 문서는 [활성 환경 안내](../02_implementation/08_ACTIVE_ENVIRONMENTS.md)이며, 세부 계약은 해당 패키지 README와 설정 파일에 연결한다.

| 항목 | 기록할 내용 |
| --- | --- |
| 등록과 상속 | 전체 Gym task ID, environment class, config class, 부모 클래스, runner entry point |
| 변형 목적 | 부모와 다른 가정·기능·물성 및 그 차이를 만든 이유 |
| 입력 | Actor/Critic 각각의 term 순서·차원·단위·frame, 초기값과 현재값, GT 경계 |
| 행동과 제어 | Action 의미·차원·scale·clip·frame, Arm/Hand mapping, controller와 정책 주기 |
| Scene와 reset | 자산 출처·경로, 물성, 초기 분포, 접촉·관통·유효성 검사 |
| 보상과 종료 | 활성 term·계수, 성공·실패·timeout의 구분, 임계값 근거 |
| 실행 | 작업 디렉터리, train/play/sensor test 명령, 필요한 환경 변수·의존성 |
| 결과 | 실제 실행한 검증, run/checkpoint/seed, 실패 사례, 미실행 항목과 이유 |

연구용 Blind 정책과 현재 물체 위치를 매 step 사용하는 기준선을 명시적으로 구분한다. 설계 문서의 57D/8D·OSC 구상, 실행 코드의 관측·제어, 저장된 checkpoint의 입력 차원은 서로 다른 확인 대상이다. 현재값은 코드로 확인하고, 성능은 해당 조건의 실행 로그로 확인한다.

## 개발 로그

개발 로그는 이 저장소의 `02_implementation/logs/YYYY-MM-DD_<topic>.md`에 남긴다. 실험 조건과 정량 결과를 길게 다루는 기록은 `02_implementation/experiments/`에 저장하고 개발 로그에서 연결한다. 기존 `1009.md`, `1010.md`, `1012_*.md`는 당시 날짜의 기록으로 보존하며, 새 기록은 연도를 포함한 이름을 사용한다.

[연구 로그 템플릿](templates/RESEARCH_LOG.md)의 실험·실패·인계 항목을 활용한다. 특히 다음 정보가 있어야 다른 사람이 이어서 실행할 수 있다.

1. 요청·검증 질문과 기준 코드의 branch/commit 및 작업트리 변경 여부.
2. 환경의 전체 ID, 환경·설정 클래스의 상속 관계, 최종 적용 설정.
3. 그대로 실행할 수 있는 명령과 필요한 checkpoint·asset·설정 경로.
4. 무엇을 바꾸었는지, 실제로 어떤 검사·실험을 수행했는지와 결과.
5. 실행하지 못한 항목, 결과가 입증하지 못하는 것, 다음 확인 사항.

체크포인트 경로가 존재하거나 학습 로그가 남아 있다는 사실과 정책이 성공한다는 결론을 구분한다. 당시 실행 경로는 로그에 남기고, 파일 이동 후 현재 위치와 활성 여부를 함께 안내한다. 코드의 이관을 새 학습·실물 성공으로 기록하지 않는다.

## 문서 위치와 갱신

| 내용 | 관리 위치 |
| --- | --- |
| 연구 흐름·아이디어·계획·결정 | 이 문서 저장소의 `01_plan/` |
| 실제 코드 설명·상태·개발 로그·수행한 실험 | 이 문서 저장소의 `02_implementation/` |
| 지침·템플릿·문서 관리 도구 / 정적 자료 | `00_guidelines/` / `03_assets/` |
| 참고 Sweeping 프로젝트 내부 환경 설명 | workspace의 `example/Sweep-Policy/docs/` |
| 위 두 프로젝트와 관계없는 일반 지식 | workspace 루트의 `docs/` |
| 함수·API·asset 등 코드를 바로 이해하는 설명 | 해당 패키지 README 또는 코드에 붙은 문서 |

전체 프로젝트 설명을 여러 위치에 복제하기보다, 한 문서를 기준으로 두고 관련 위치에서 링크한다. 환경 계약을 바꾸면 패키지 설명·활성 환경 안내·개발 로그를 같이 확인한다. 연구 방향을 바꾸면 [결정 목록](../01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md), [인계 요약](../01_plan/00_HANDOFF_BRIEF.md), [다음 작업](../01_plan/04_NEXT_ACTIONS.md)을 갱신한다. 파일을 옮기면 문서 색인과 역방향 링크도 갱신한다.

## 변경 검증

검증은 변경의 성격에 맞춘다. 순수 Python/설정 계약 검사는 실제 사용하는 term과 경계를 확인하고, 센서·물리·학습의 동작은 Isaac Sim 실행 결과로 확인한다. 정적 검사 통과를 시뮬레이션 성공으로 해석하지 않는다. 모든 기록에 실행한 검사와 실행하지 못한 검사를 나누어 적는다.

Markdown은 [문서 형식 규칙](rules/document-formatting.md)을 따르며, 변경한 파일만 `00_guidelines/scripts/check_markdown_math.py`로 검사한다. 상대 링크가 가리키는 파일과 anchor, `git diff --check`도 확인한다. 현 작업트리에서 없는 자료는 미확보로 표시하고, 읽은 자료와 코드로 설명할 수 있는 수준까지 문서를 가공한다.

폴더 분류와 새 문서·자산의 작성·읽기·이동 절차는 [문서 구조 규칙](DOCUMENT_STRUCTURE.md)을 따른다.
