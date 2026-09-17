# 결정·변경·미정 목록

[문서 안내](README.md) · [문헌조사](literature/README.md) · [조사 그룹](literature/reviews/README.md)

기준일: 2026-09-14. 출처는 [출처 목록](06_SOURCE_REGISTER.md)을 따른다. 이 문서는 현재 요구사항을 판별할 때의 기준이며 실험 검증 완료를 뜻하지 않는다.

## 1. 상태 정의

| 상태 | 의미 |
| --- | --- |
| CONFIRMED_DIRECTION | 회의·대화에서 확인된 현재 연구 방향 |
| REPORTED_IMPLEMENTED | 과거 구현 보고가 있음. 실제 코드·실행 검증은 별도 |
| PROPOSED | 학생·정리자·인계 작성자가 제안한 설계 또는 실험 |
| OPEN | 아직 결정되지 않았거나 확인 근거가 부족함 |
| DEFERRED | 폐기하지 않았지만 현재 우선 작업에서 제외 |
| SUPERSEDED | 뒤의 논의로 수정된 가정 |
| HISTORICAL | 현재 사양이 아닌 배경·과거 구상 |

## 2. 현재 유지할 방향

| ID | 상태 | 내용 | 근거 |
| --- | --- | --- | --- |
| D-01 | CONFIRMED_DIRECTION | 석사생 1은 초기 시각 이후 힘·촉각 중심의 하위 Blind Sweeping을 연구한다 | S-0914 |
| D-02 | CONFIRMED_DIRECTION | 상위 시각·판단·접근과 하위 접촉 조작을 분리한다 | S-0910, S-0911, S-0914 |
| D-03 | CONFIRMED_DIRECTION | 초기 주변 정보가 존재할 수 있다. 완전 초기 무지를 필수 조건으로 강제하지 않는다 | S-0914 §3 |
| D-04 | CONFIRMED_DIRECTION | 물체 근처의 접근 결과에서 시작하며 실제 접촉 위치와 감지는 불확실하다 | S-0910 §3, S-0914 §3–4 |
| D-05 | CONFIRMED_DIRECTION | 제한 센싱·접촉 불확실성과 기본 조작 가능성이 현재 연구 중심이다 | S-0914 §2, §4 |
| D-06 | CONFIRMED_DIRECTION | F/T·촉각 관련 선행연구를 센서 구성·관측 조건까지 확인한다 | S-0914 §6 |
| D-07 | CONFIRMED_DIRECTION | 실물 미준비가 시뮬레이션 검토를 미룰 이유는 아니다 | S-0914 §6 |
| D-08 | CONFIRMED_DIRECTION | 실제 검증 과정의 실패와 난도를 로그로 남기고 연구 결과로 정리한다 | S-0914 §6 |
| D-09 | CONFIRMED_DIRECTION | 두 학생의 힘·촉각 공통 기반 연구는 공유 가능하다 | S-0914 공통 피드백 |
| D-10 | CONFIRMED_DIRECTION | roadmap은 초안이다. 최신 사용자 지시·미팅 경계와 충돌하면 절대 기준으로 삼지 않는다 | C-ROADMAP |
| D-11 | CONFIRMED_DIRECTION | 성공 목표는 대상 물체 조작이다. EEF 이동과 물체 이동은 구분한다 | S-TASK1 |

## 3. 최근까지의 설계 방향 — 세부 확정과 구분

| ID | 상태 | 현재 정보 | 주의 |
| --- | --- | --- | --- |
| P-01 | PROPOSED | 초기 대상 pose+방향·거리+F/T+촉각이 입력의 중심 | 전체 observation dimension은 미정 |
| P-02 | PROPOSED | 선반 좌표계의 좌우 Sweep을 구체적인 시작안으로 사용 | 9/11의 전방향 지향을 영구 삭제하지 않음 |
| P-03 | PROPOSED | tactile 영역별 Grid를 scalar/Boolean으로 축약하여 17차원 사용 | 원시 출력·축약 함수·threshold 실측 미완료 |
| P-04 | PROPOSED | Cartesian arm command와 사전 정의 Hand posture | Δpose/velocity, 제어 DOF, controller, hand mode 미정 |
| P-05 | PROPOSED | 초기 접촉→sweep→근처 대기 자세 | 전체 상태기계·학습 action 구조는 확정되지 않음 |
| P-06 | PROPOSED | 9/13안에서는 명시 Geometry 입력 없음 | 9/14에 전체 입력 계약을 확정하지 않음. geometry 필요성을 임의 확정하지 않음 |
| P-07 | REPORTED_IMPLEMENTED | 9/10의 Cartesian/OSC sweep·일부 relative obs·초기 상태 랜덤화 | 센서 기반 최종 정책과 다름. 최신 코드 재확인 필요 |
| P-08 | HISTORICAL | 9/11 PPO config 코드 | 현재 환경·실행에 적용되는지 미확인 |

## 4. 변경되었거나 후순위가 된 내용

| ID | 이전 가정·제안 | 현재 상태와 이유 |
| --- | --- | --- |
| X-01 | 주변 물체는 초기부터 아무 정보도 없다 | SUPERSEDED. 9/14 초기 관측 활용 허용. 하위에 무엇을 줄지는 OPEN |
| X-02 | 간섭 감지→중단→대기가 이번 기여의 중심이다 | DEFERRED. 먼저 기본 센싱·Blind 조작과 선행연구 검증 |
| X-03 | clutter 회피 능력을 늘려 기여를 만든다 | DEFERRED. 주변 복잡도보다 접촉·센싱 문제 우선 |
| X-04 | 넓은 공간 임의 시작이면 초기조건 요구를 충족한다 | SUPERSEDED. 접근 완료 후 상대 pose 오차를 반영한 근접 분포가 필요 |
| X-05 | 상위는 방향·거리만 주고 나머지 모든 상황은 하위가 해결한다 | SUPERSEDED. 접근·시작 조건·조작 가능성의 상위 역할 인정 |
| X-06 | 무회전 Sweep과 Pivoting 두 가지를 하나의 현재 필수 패키지로 구현한다 | HISTORICAL. 연구 1/2의 최신 경계를 따른다 |
| X-07 | strict rotation constraint, SVD stiffness, RNN이 이미 확정되었다 | HISTORICAL/OPEN. 현재 사양으로 승계할 근거 없음 |
| X-08 | F/T·촉각이 있으니 접촉 상태와 간섭 원인이 충분히 식별된다 | 근거 없는 가정. S-0914가 먼저 검증하라고 요구한 대상 |

연구용 중단 기능의 `DEFERRED`는 안전 정지의 제거가 아니다. 단일 물체 검증의 허용은 최종 clutter 포기의 결정이 아니다.

## 5. 미정 사항과 해결에 필요한 근거

| ID | 질문 | 결정에 필요한 작업 | 우선도 |
| --- | --- | --- | --- |
| O-01 | 현재 실제 학습 코드·버전·run은 무엇인가? | 저장소/커밋, env 클래스, observation/action/reset/reward/termination 확인 | P0 |
| O-02 | 장비가 실제로 어디까지 준비됐고 어떤 데이터를 내는가? | 모델·장착·원시 sample·매뉴얼·수신 로그 확인 | P0 |
| O-03 | 각 tactile 영역은 어디이며 실제 접촉면을 덮는가? | hand–sensor 대응표, 센서/비센서 접촉 실험 | P0 |
| O-04 | F/T와 tactile의 실효 신호·noise·지연은 어느 수준인가? | 무부하/자세변화/약한 접촉/가벼운 물체의 동기 로그 | P0 |
| O-05 | 초기 정보에 주변·geometry를 어디까지 포함하는가? | 상위/하위 정보 계약과 비교 목적 정리. 완전 GT를 디폴트로 넣지 않음 | P0 |
| O-06 | 정책 action, control DOF, 실물 controller는 무엇인가? | 기존 OSC와 후속 Diff-IK 구상의 실제 연결 경로 확인 | P0 |
| O-07 | 시뮬레이션 센서 모델이 실물에서 얻을 정보와 대응하는가? | tactile 영역 mapping, wrist wrench 정의, 물체 ID 누출 검사 | P0 |
| O-08 | Blind 실행에서 목표 도달·종료를 어떻게 판정하는가? | 물체 GT 평가와 실물 종료 로직을 분리하고 오류 측정 | P0 |
| O-09 | 최초 학습의 방향 범위·물체 종류·초기 접촉 조건은? | 최소 실험 정의. 좌우 시작안과 전방향 확장 범위 구분 | P1 |
| O-10 | 실제 approach error 분포는? | 반복 접근 후 EEF–물체 relative pose error 측정 | P1, 장비 의존 |
| O-11 | 고유감각·action history·sensor history·RNN은 필요한가? | 관측 가능성과 baseline 실패를 보고 비교 실험 설계 | P1 |
| O-12 | 보상·성공 기준·허용 force·rotation·timeout은? | 물리 목표와 실물 안전 한계 및 관측 조건에 근거해 결정 | P1 |
| O-13 | 손 자세 고정/모드 선택/연속 손가락 제어 중 무엇을 쓰는가? | 접촉면과 tactile coverage, 기본 제어 가능성 확인 | P1 |
| O-14 | 어떤 비교 실험으로 F/T·촉각의 기여를 입증하는가? | 동일 조건의 무접촉센서/F/T-only/tactile-only/결합 baseline 제안 검토 | P1 |
| O-15 | 최종 clutter 범위와 실물 검증 수준은? | 기본 feasibility·센싱 실패 조건과 연구 일정의 근거로 결정 | P2 |
| O-16 | 간섭 판별이 센서만으로 충분히 가능한가, 추가 기여가 있는가? | 기본 문제 및 문헌 결과 이후 식별 가능성과 rule-based 기준 비교 | P2/DEFERRED |

P0/P1/P2는 이 인계에서 구성한 작업 우선순위다. 교수님이 이 번호나 정확한 순서를 승인했다는 뜻은 아니다. 장비가 없는 P0 항목은 확인 불가로 남기고 가정을 명시한 시뮬레이션·문헌 작업을 병행한다.

## 6. 결정 변경 템플릿

```text
Decision ID:
날짜:
이전 상태:
새 상태:
결정 내용:
근거 출처 또는 실험 ID:
교수 지시 / 사용자 결정 / 실험 결과 / 제안 중 구분:
변경 이유:
영향받는 문서·코드:
아직 남는 불확실성:
```

새 결정이 나면 해당 행과 미팅 이력, brief, 다음 작업을 함께 갱신한다. 미정 항목을 해결하지 못했다고 매번 같은 배경 질문을 반복하지 말고, 이미 읽을 수 있는 코드·문서를 먼저 확인한다.
