# 결정·변경·미정 목록

2026-10-24 사용자 후속 지정: ObjectRandom-v2의7/7 반복 배치가 통과하면7/7, 실패하면6/6으로 제한한다. 실제7/7·seed0의 첫 reset 배치에서200회 실패하여 현재 커리큘럼 상한은6/6이다. 관측과 물리 슬롯 용량은 보존한다. [검증과 한계](../02_implementation/logs/2026-10-24_object_random_v2_population_cap.md).

2026-10-24 사용자 요청: Holding-v3 → OSC-v3 → ObjectRandom-v2를 직접 상속 체인으로 추가한다. goal hold 지급 시간을 에피소드 누적3초로 제한하고OSC-v2 제어를 재사용한다. ObjectRandom 개수는3000부터1000간격 교대 증가, Gray 내측 확장은6000~12000·250간격·최대15%다. 15%는 기존Red 제외 반경10.3cm를 기준으로 최대1.545cm 안쪽을 허용하는 구현 해석이다. [계약](../02_implementation/environments/FUSION_HOLDING_V3_FAMILY.md) · [검증](../02_implementation/logs/2026-10-24_fusion_holding_v3.md). 학습 행동 개선은 미검증이다.

> **2026-10-23 사용자 지정 — Holding 계열 운영:** Holding은 목표 유지·성공 종료 개선, OSC는 제어 설정 변경을 통한 Holding 결과 재현, OSC-Random은 물체 다양화·실제 물체 형상 확장을 담당한다. 각 계열의 버전은 독립적으로 증가하고 기준 부모를 명시한다. 현재 Random 등록명은 OSC-ObjectRandom이다. [계열 설명과 현재 상속 관계](../02_implementation/environments/FUSION_HOLDING_FAMILY.md). 이는 개발 방향의 확정이며 성능 검증 완료를 뜻하지 않는다.
> **2026-10-23 사용자 요청 — 스폰 규칙 고도화 계획:** 영역별 스폰 개수를 쉽게 조정하고, 밀도가 높아져도 RED Zone 금지와 물체 간 최소 거리를 유지한다. 가능한 한 기존 배치 알고리즘을 따르며 물리적으로 수용할 수 없으면 개수 감소를 허용한다. 이번 범위는 [reset Event 개발 계획](environments/CLUTTER_SPAWN_EVENT_PLAN.md) 작성이며 코드 구현은 하지 않는다. 유한 탐색의 실패는 물리적 불가능 증명과 구분한다. 탐색 예산 소진 시 유효 부분 배치를 반환하는 운용 방식은 계획상의 제안이며 전역 최대 개수 보장이 아니다.

> **2026-10-20 사용자 요청 — Clutter v2 F/T 보정:** v1을 계승하고 기존 F/T 관측을 보정한 6축 Wrench로 대체한다. 급격한 힘·모멘트 변화의 제곱 비용에는 상한을 두어 밀기 회피를 과도하게 유도하지 않도록 한다. 구현은 정적 tare를 참조하되 움직이는 Hand의 중력·관성 하중을 매 physics step 계산해 제거한다. 변화 허용폭 0.5 N·0.01 N·m, 스케일 5 N·0.1 N·m와 −0.1/초는 구현자가 정한 초기 실험값이다. 5%의 분모는 v1 비중 계산과 동일한 양의 보상 합이며, 실제 에피소드 누적값을 이용해 제한한다. [구현·검증·미검증 범위](../02_implementation/logs/2026-10-20_contact_sweep_clutter_v2.md).

> **2026-10-20 사용자 확인 — Contact Sweep Clutter:** 독립 Contact Sweep을 상속해 장애물 환경을 만든다. 부모 타겟·목표 분포와 로봇 초기 관절 자세를 유지하고, 목표 확정 후 참고 Scene 생성기의 장애물 배치 규칙만 적용한다. 장애물 3개·10개 관측 슬롯(최초 6개에서 후속 요청으로 감소), 모든 물체의 tilt 합·하나라도 낙하/전도 시 종료, 모든 물체의 촉각 접촉, reset 때 한 번 ±1 cm 노이즈를 적용한 초기 장애물 위치를 채택한다. 후속 확인으로 뒤쪽 GRAY 1개·WHITE 2개와 RED 반경 10.3 cm(기존 8.3 cm)를 선택했으며 v0 ID를 유지한다. [변경 검증](../02_implementation/logs/2026-10-20_clutter_red_expansion.md). MLP 구조는 구현 재량으로 `40 → 32(ReLU) → 16`을 사용한다. 장기 학습·실물 성과는 미확인이다. [구현·검증](../02_implementation/logs/2026-10-20_contact_sweep_clutter.md).

> **2026-10-16 사용자 지정 개발 기준:** 이후 추가 작업은 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v0`를 기반으로 상속한다. 실행기 기본 task 변경 요청은 아니다. 이번 v1에는 지수 속도 비용 상한 100, 손목 종료 0.03 m, 선반 로컬 ±X 각각 ±15° 목표 제외를 적용한다. [구현 계약·실행 안내](../02_implementation/08_ACTIVE_ENVIRONMENTS.md) · [검증 로그](../02_implementation/logs/2026-10-16_dex_tactile_renewal_v1.md).

> **2026-10-15 사용자 요청 — Omni v2 보상 실험:** v1을 유지하고 이를 상속하는 v2에서 현재 물체 위치 기준의 episode 최소 접근 기록 보상, time/success/failure 보상 제거를 구현했다. 후속 사용자 요청으로 v2의 success DoneTerm도 제거했으며 실패·시간 초과 종료는 유지한다. 추가 사용자 지시에 따라 운동 비용은 v1 원래 값으로 복원하고 Reaching·목표 이동 진전 보상만 각각 누적 +200·+400으로 강화했다. 보상 계수의 학습 효과는 미검증이다. [구현·검증 로그](../02_implementation/logs/2026-10-15_omni_v2_rewards.md) · [환경 안내](../02_implementation/08_ACTIVE_ENVIRONMENTS.md).

[문서 안내](README.md) · [문헌조사](literature/README.md) · [조사 그룹](literature/reviews/README.md)

기준일: 2026-10-14. 출처는 [출처 목록](06_SOURCE_REGISTER.md)을 따른다. 9월 14일 연구 경계와 이후 설계·workspace 결정을 함께 관리하며, 결정의 확인을 실험 검증 완료로 해석하지 않는다.

## Workspace·문서 관리 결정 — 2026-10-14

근거: S-WORKSPACE-20261014 및 S-DOC-STRUCTURE-20261014의 사용자 정리 요청. 연구 방법·수치·최종 성능을 새로 확정하는 결정과 구분한다.

| ID | 상태 | 결정 | 반영 위치 |
| --- | --- | --- | --- |
| W-01 | CONFIRMED_DIRECTION | `src/inspire_sweep_baseline`, `src/axia80_feasibility`만 활성 유지. 나머지는 `src/trash` 보관 및 colcon 제외 | [활성 환경](../02_implementation/08_ACTIVE_ENVIRONMENTS.md), [Workspace 구성](../00_guidelines/10_WORKSPACE_GUIDE.md) |
| W-02 | CONFIRMED_DIRECTION | 문서 submodule은 전체 flow·연구·계획·상태·로그, 참고 환경 docs는 내부 환경, 루트 docs는 일반 지식 담당 | [문서 지도](../00_guidelines/10_WORKSPACE_GUIDE.md) |
| W-03 | CONFIRMED_DIRECTION | Manager-based RL의 OOP 원칙을 지키고 환경의 상속·정확한 실행 명령을 개발 로그에 남김 | [개발 지침](../00_guidelines/09_DEVELOPMENT_GUIDE.md), [로그 목록](../02_implementation/logs/README.md) |
| W-04 | CONFIRMED_DIRECTION | 과거 설계·누락된 기록은 보존하되 현행 계약·성과와 구분하고 탐색 링크를 연결 | [역사 자료](history/README.md), [구현 계획](experiments/2026-09-26_blind_sweeping_build_plan.md) |
| W-05 | CONFIRMED_DIRECTION | 문서 저장소를 지침·연구/계획·실제 코드 기록·정적 자산의 네 폴더로 분류하고, 이동한 파일의 참조와 에이전트 생산·읽기 규칙을 함께 갱신 | [문서 구조 규칙](../00_guidelines/DOCUMENT_STRUCTURE.md), [재구성 로그](../02_implementation/logs/2026-10-14_document_reorganization.md) |

현재 baseline의 Arm Joint Position 제어·41D 기본 관측과 아래 발표의 57D/8D·OSC 설계는 서로 다른 검증 단계다. 환경별 적용 계약은 활성 환경 안내에 기록한다. 이번 정리에서 발표 설계를 baseline에 구현했거나 Blind 성능을 검증한 것은 아니다.

> **2026-10-05 최종 중간발표 문서화:** `중간발표_최종.pdf`의 설계와 아래 과거 기록의 차이는 [발표 구성과 설계 현황](presentation/00_Presentation_Overview_and_Design_Status.md)에 정리했다. Base 기준 관측, 갱신된 보상식, CoP 회전 Sub-Goal 및 센서·보상 비교 계획은 해당 설명 문서를 함께 확인한다. 이는 기존 발표 설계를 문서화한 것이며 새로운 구현·실험 완료 보고가 아니다.

> **발표 문서 재구성에 따른 사용자 결정:** Motivation·Contribution, Related Works, Method를 [세 문서](presentation/README.md)로 분리한다. Observation Stack·Sliding Window·이력 기반 물성 적응은 보류하며 P-09·O-11·O-17에 반영한다. 기존 brief·next-actions의 이력 검토 제안은 현재 우선 작업으로 해석하지 않는다. Related Works의 선행연구 보상 정리와 본 연구 Method의 보상 초안은 구분한다.

> **2026-09-22 Method 개편 — 사용자 지정 설계:** [Method](presentation/1st_draft/03_Method.md)를 기준으로 360도 Sweep, 간섭 없는 MoveIt 접근 후 정책 실행, Observation 57D(직전 Action 8D 포함), Action 8D(Manipulator 6D + Hand 2D), Arm OSC·Hand Joint Position Controller를 채택하는 설계를 정리했다. 목표 도달이 주보상이며 다른 보상은 안정화 보조 항이다. 이는 구현 완료 보고가 아니며, Noise·Randomization·보상식·가중치의 미정 수치는 유지한다.

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
| P-01 | PROPOSED | 현재 Method는 초기 물체 Position·방향·거리, Robot·Hand 상태, 18D 촉각·6D Wrench·직전 Action을 포함한 57D 관측 | 사용자 지정 차원의 설계. Orientation 3성분 표현과 정규화 세부는 미정 |
| P-02 | CONFIRMED_DIRECTION | 선반 평면의 Sweep 방향은 360도 전 방향 허용 | 접근 Pose의 12시·6시 Dead Zone과 구분. 상세 조건은 Method |
| P-03 | PROPOSED | 전면 17 Grid·후면 17 FSR을 Binary화하고, 접촉면 Header 1 + 선택 면 17의 18D 관측 | 부착·영역 대응·임계값 및 단면 접촉 가정 검증 필요 |
| P-04 | CONFIRMED_DIRECTION | EEF 기준 Cartesian 위치·회전 증분 6D를 OSC로 실행하는 설계 | 실제 Controller 구현·Gain·Action Scale·주기는 검증·구체화 전 |
| P-05 | PROPOSED | 초기 접촉→sweep→근처 대기 자세 | 전체 상태기계·학습 action 구조는 확정되지 않음 |
| P-06 | CONFIRMED_DIRECTION | Command는 초기 물체 Position 3D + Direction 1D + Distance 1D | 현재 Actor에는 Object Orientation·Shape·Size를 추가하지 않음 |
| P-07 | REPORTED_IMPLEMENTED | 9/10의 Cartesian/OSC sweep·일부 relative obs·초기 상태 랜덤화 | 센서 기반 최종 정책과 다름. 최신 코드 재확인 필요 |
| P-08 | HISTORICAL | 9/11 PPO config 코드 | 현재 환경·실행에 적용되는지 미확인 |
| P-09 | DEFERRED | Observation Stack·Sliding Window·이력 기반 물성 적응 | 직전 Action 8D는 이번 사용자 지정으로 포함. 일반적인 이력 설계와 구분 |
| P-10 | PROPOSED | Base Randomization은 정지 후 XY 위치 편차로 한정 | 범위는 실측 전 미정이며 Yaw·동적 이동·위치 추정 오차는 자동 포함하지 않음 |

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
| O-01 | 현재 실제 학습 코드·버전·run은 무엇인가? | 활성 패키지·등록·상속·계약은 08 문서에 정리됨. 설치 버전·적용 run·평가는 로그와 연결해 보완 | P0 |
| O-02 | 장비가 실제로 어디까지 준비됐고 어떤 데이터를 내는가? | 모델·장착·원시 sample·매뉴얼·수신 로그 확인 | P0 |
| O-03 | 각 tactile 영역은 어디이며 실제 접촉면을 덮는가? | hand–sensor 대응표, 센서/비센서 접촉 실험 | P0 |
| O-04 | F/T와 tactile의 실효 신호·noise·지연은 어느 수준인가? | 무부하/자세변화/약한 접촉/가벼운 물체의 동기 로그 | P0 |
| O-05 | 초기 정보에 주변·geometry를 어디까지 포함하는가? | 상위/하위 정보 계약과 비교 목적 정리. 완전 GT를 디폴트로 넣지 않음 | P0 |
| O-06 | 선택한 Action·Controller를 실제로 어떻게 구현하는가? | 현재 Joint Position 기준선과 발표의 Arm Cartesian 증분→OSC·Hand 2D 설계를 구분하고 연구용 구현 연결을 검증 | P0 |
| O-07 | 시뮬레이션 센서 모델이 실물에서 얻을 정보와 대응하는가? | tactile 영역 mapping, wrist wrench 정의, 물체 ID 누출 검사 | P0 |
| O-08 | Blind 실행에서 목표 도달·종료를 어떻게 판정하는가? | 물체 GT 평가와 실물 종료 로직을 분리하고 오류 측정 | P0 |
| O-09 | 초기 상태 분포의 구체적인 범위는 무엇인가? | 360도 방향·MoveIt 도달 가능 상태·Hand 0.5+Noise·큐브/실린더/비정형 물체의 유효 조건 구체화 | P1 |
| O-10 | 실제 approach error 분포는? | 반복 접근 후 EEF–물체 relative pose error 측정 | P1, 장비 의존 |
| O-11 | Observation Stack·Sliding Window·이력 기반 적응을 추가할 것인가? | 현재 검토 보류. 직전 Action 8D만 관측에 포함 | DEFERRED |
| O-12 | 보상·성공 기준·허용 force·rotation·timeout은? | 물리 목표와 실물 안전 한계 및 관측 조건에 근거해 결정 | P1 |
| O-13 | Hand의 공통 굽힘과 엄지 별도 Joint의 2D 표현을 어떻게 매핑하는가? | 관측 집계, 0~1 정규화 범위와 Joint Position 목표 매핑 구체화 | P1 |
| O-14 | 어떤 비교 실험으로 F/T·촉각의 기여를 입증하는가? | 동일 조건의 무접촉센서/F/T-only/tactile-only/결합 baseline 제안 검토 | P1 |
| O-15 | 최종 clutter 범위와 실물 검증 수준은? | 기본 feasibility·센싱 실패 조건과 연구 일정의 근거로 결정 | P2 |
| O-16 | 간섭 판별이 센서만으로 충분히 가능한가, 추가 기여가 있는가? | 기본 문제 및 문헌 결과 이후 식별 가능성과 rule-based 기준 비교 | P2/DEFERRED |
| O-17 | 명시적 물성 모델과 이력 기반 간접 적응은 기존 연구에서 어떻게 비교되는가? | 현재 발표 범위에서 제외. 기존 문헌조사 자료는 보존 | DEFERRED |

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

## 2026-10-15 Omni 운동 페널티 고정 — 사용자 지시

Omni 베이스 및 모든 파생(Dex 포함)은 참고 Inspire와 같은 raw Action 변화량·실제 관절 속도의 제곱합을 로컬 MDP 함수로 사용한다. Arm/Hand 네 항은 분리 유지하며 임의로 평균·정규화·보상 입력 clamp를 도입하거나 계수를 낮추지 않는다. [필수 개발 규칙](../00_guidelines/09_DEVELOPMENT_GUIDE.md), [적용·검증 로그](../02_implementation/logs/2026-10-15_omni_penalty_contract.md).

## 2026-10-18 Dex Tactile 목표 정착 보상 — 사용자 지시

기존 텍타일 환경을 상속하여 안정된 목표 도달의 큰 일회성 성공 보상과 목표에 연속해서 머무를수록 증가하는 양의 보상을 추가한다. 새 속도·목표 통과 후 위치 오차 비용과 액션 clipping은 추가하지 않는다. 구현은 v0를 직접 상속한 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2`다. +100 보너스·최대 +20/초 선형 체류 보상은 초기 실험 계수다. 초기 구현에서는 0.5초 연속 만족 시 성공 종료했으나, 아래 후속 사용자 명확화에 따라 성공 종료를 제거했다. 기존 v0 보상·실패 종료는 상속한다. [활성 계약](../02_implementation/08_ACTIVE_ENVIRONMENTS.md), [초기 구현 로그](../02_implementation/logs/2026-10-18_dex_tactile_renewal_v2_goal_hold.md). 장시간 학습과 오버슈트 개선 성과는 아직 미검증이다.

## 2026-10-18 v2의 OSC 파생 — 사용자 지시

v2를 상속한 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2`에서 Arm 제어만 OSC로 교체한다. 기존 Renewal OSC를 참조하되 stiffness를 100으로 낮추고 작은 Cartesian 증분 상한을 적용한다. 이 요청에서는 OSC 명령 크기 제한을 명시적으로 허용했으며, 이전 Joint Position 환경의 가동 범위 제한 금지와 구분한다. 보상·실패 종료·성공 조건·Hand·센서·물성 등은 v2에서 그대로 상속한다. 1.5 rad/s는 대략적인 명령 범위 선택 목표이고 새 종료 임계값이 아니다. 구현자는 translation norm 5 mm·rotation-vector norm 0.025 rad를 초기 실험값으로 설정했다. 초기 응답은 감소했지만 0 명령에서도 이후 과속이 발생하는 대조 결과가 있어 지속 안정성은 미해결이다. [실측·검증 로그](../02_implementation/logs/2026-10-18_dex_tactile_renewal_v2_osc.md).

## 2026-10-18 성공 이후 timeout까지 유지 — 사용자 명확화

사용자의 의도는 물체를 목표에 계속 놓아 둔 채 timeout까지 유지하는 것이다. v2의 `terminations.success`는 `None`으로 바꾸고 +100은 reward term의 episode latch로 최초 한 번만 지급한다. 기존 실패 조건은 유지한다. 목표 유지 보상은 성공 후에도 계속 지급하며 이탈하면 0으로 초기화하고 재진입 시 다시 증가한다. 이탈/재진입으로 +100을 반복 획득하지 않으며, 다음 episode reset에서만 재지급 가능해진다. OSC v2에도 부모 상속으로 동일하게 적용한다. [수정·검증 로그](../02_implementation/logs/2026-10-18_v2_goal_hold_until_timeout.md).

## 2026-10-18 v2의 부모를 v1로 변경 — 사용자 지시

v2를 v0 직접 상속에서 v1 직접 상속으로 변경한다. 현재 체인은 `v0 → v1 → v2 → OSC v2`이며 runner도 같은 버전 상속을 따른다. v1의 지수 속도 비용 두 항 상한 100·손목 높이 종료 기준 0.03 m·±X 각각 ±15° 목표 방향 제외를 적용한다. v1의 스폰 관련 변경은 목표 방향 제한이며 반경 2 cm의 물체 위치 분포는 그대로다. v2의 +100 최초 달성 보너스·최대 +20/초 유지 보상·성공으로 종료하지 않는 동작은 유지한다. OSC는 수정된 v2 위에서 Arm 제어만 교체한다. 기존 task ID·실행 명령은 유지한다. [구현·검증 로그](../02_implementation/logs/2026-10-18_v2_inherits_v1.md).

## 2026-10-20 Clutter v1 초기 관측과 보상 — 사용자 지시

`Isaac-Inspire-Contact-Sweep-Clutter-v0`를 상속한 v1에서 타겟 현재 위치를 Actor의 시작 위치 관측으로 교체하고, 현재 XYZ는 Critic의 추가 관측으로만 사용한다. 목표 유지 조건은 월드 XY 반경 1 cm, Contact는 하나 이상 ON과 5개 포화 접촉 수의 두 항이며 최대값을 같게 둔다. 장애물은 타겟을 제외한 실제 초기 위치 대비 3D 이동 거리 제곱합을 비용으로 사용하고 상한을 둔다. `pushing_speed.free_speed=1.0`, `arm_speed_excess.free_speed=0.5`를 적용한다.

사용자가 지정한 `2026-10-20_14-04-31` 로그와 목표 체류 5초·5개 접촉 7초 가정으로 초기 계수 30/100/0.9/0.16/0.16, 장애물 −5 및 제곱합 상한 0.04 m²를 선택했다. 양의 보상 네 그룹 합을 비중의 분모로 사용하고 페널티는 별도로 보고한다. 목표 유지의 증가는 반경 안에 있는 동안 일정 보상률을 누적하는 것으로 구현했다. 실제 v1 비중을 목표값으로 강제하거나 수렴을 확인했다는 결정이 아니다. [구현·계산·검증 근거](../02_implementation/logs/2026-10-20_contact_sweep_clutter_v1.md).

## 2026-10-23 — 자동 복구 학습 사용 중단

사용자 결정: `train_resilient.py` 사용을 중단하고 학습 실행·안내에는 `train.py`를 사용한다. 원인 불명 중단을 checkpoint rollback 후 재학습으로 해결하려 했으나 실제로는 중단이 반복되었다는 사용자 보고가 근거다. 원인은 미확정이다. 복구 코드는 추후 재사용을 위해 보존하며 사용자 명시 재사용 요청 전까지 실행·권장하지 않는다. [현재 실행 정책](../00_guidelines/09_DEVELOPMENT_GUIDE.md#학습-실행-정책).
