# 고밀도 스폰 규칙 고도화와 reset Event 개발 계획

[계획 안내](../README.md) · [요청 TODO](../../../../docs/TODO.md) · [현행 환경](../../02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_0_ENVIRONMENT.md) · [계획 작성·검증 로그](../../02_implementation/logs/2026-10-23_clutter_spawn_event_plan.md)

기준일: 2026-10-23. 상태: **개발 계획(PROPOSED), 미구현**. 사용자 요구인 영역별 개수 조정, RED Zone 스폰 금지, 물체 간 최소 거리 유지, 배치 불가능 시 개수 감소를 구체화한다. `docs/TODO.md`의 2번 고밀도 스폰 과제를 대상으로 하며, OSC·실물 에셋 제작·보상 개편은 이번 구현 범위에 포함하지 않는다.

목표는 **요청 개수를 우선 시도하되, 제약을 위반한 물체를 추가하거나 무한 재시도하지 않고 검증된 유효 배치를 반환하는 것**이다. 20개를 요청한 장면에서 19개까지만 유효하게 배치할 수 있다면 19개를 사용한다. 다만 유한 탐색으로 19개를 찾았다는 사실만으로 20개가 물리적으로 불가능하다고 단정하지 않는다.

## 1. 현재 구현과 실제 변경 범위

검토 기준은 workspace `703ac8864fa8c0e4606fbf67fd5629fb367e96c4`, 문서 저장소 `7fd20636009427d2960f1194b84353c71adfced3`다. 아래는 소스 대조 결과이며 새 기능의 실행 검증 결과가 아니다.

| 항목 | 확인한 현재 동작 | 필요한 변경 |
| --- | --- | --- |
| 영역별 개수 | [population.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/contact_sweep_clutter_fusion_population.py)의 GRAY/WHITE 일정과 EnvCfg의 최대 슬롯 수가 분리되어 있다. 기본 요청은 각 1→3개다. | 고정 개수/커리큘럼의 단일 설정 경로와 요청·실제 개수 분리 |
| 뒤쪽 GRAY | [population layout](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/contact_sweep_clutter_fusion_layout.py)은 `rear_obstacles=min(1, gray_obstacles)`를 사용한다. | 뒤쪽 배정 개수도 명시적 파라미터로 노출 |
| 배치 생성 | [ClutterLayoutGenerator](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/contact_sweep_clutter_layout.py)는 타겟·목표를 고정한 채 장애물을 순차 배치한다. 정해진 재시도 후 한 행이라도 미완성이면 `GenerationError`를 낸다. | 환경별 최선의 유효 부분 배치 보관, 부족한 영역을 건너뛰는 탐색, 실제 개수 반환 |
| 기하 제약 | [참고 생성기](../../../../src/scene_randomization/generator.py)의 RED/GRAY/rear, 최소 거리, 셀 점유, 이웃 수, 접근 경로를 사용한다. | 불변 제약과 분포 규칙을 명시하고 모든 반환 경로에서 재검사 |
| Event | [events_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/events/contact_sweep_clutter_fusion.py)에 이미 `object_spawn`, `mode="reset"`이 있다. | 기존 Event를 확장 가능한 배치 서비스의 어댑터로 구성 |
| 활성 물체 | [events.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/contact_sweep_clutter_fusion.py)는 배치 전 공통 요청 개수로 mask를 만든다. | 배치 결과를 받은 뒤 환경마다 다른 mask 생성 |
| 최대 개수 | 기본 7개는 타겟 1+장애물 6개다. `validate_capacity`와 생성기는 장애물 10개를 제한한다. | 타겟 포함 20개에는 최소 장애물 19슬롯 및 관련 경로 확장 필요 |
| 관측·모델 | 초기 장애물은 10×4=40D이며 [Fusion 모델](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/contact_sweep_clutter_fusion_models.py)과 export에도 40이 고정되어 있다. | Event만 고쳐서는 20개 운용 불가. 슬롯·관측·encoder·export를 함께 확장 |

기존 환경의 기준선 재현성을 위해 v1_0을 기반으로 별도 파생 설정에 새 스폰 규칙을 연결하는 방식을 제안한다. 기존 task를 일괄 변경하지 않는다. 새 task ID·패키지 이름은 구현 시 중복을 확인하여 정하고, 그때 [활성 환경 안내](../../02_implementation/08_ACTIVE_ENVIRONMENTS.md)에 부모·등록·실행 명령을 추가한다. 참고 `scene_randomization`은 읽기 전용으로 유지하고 새 배치 제어와 결과 자료형은 활성 패키지에 둔다.

## 2. 지켜야 할 계약

### 2.1. RED Zone과 거리의 의미

RED 금지는 **추가 장애물**에 적용한다. RED가 타겟의 시작점과 이동 경로를 기준으로 만들어지므로 타겟까지 RED 밖으로 옮기면 기존 과제 자체가 달라진다. 최소 거리 검사는 타겟–장애물과 장애물–장애물의 모든 활성 쌍에 적용한다.

현재 RED는 단순 원이 아니다. 타겟→목표 구간을 생성기 좌표의 −Y 방향으로 확장한 Tool/Wrist 점유와 그 주변 여유 영역이다. `zone_masks`는 이미 물체 반경을 반영한 **장애물 중심 금지 영역**을 반환한다. 이를 시각화용 원 또는 원래 경로와 혼동하거나 반경을 중복 가산하지 않는다.

| 조건 | 현재 실린더 기준 | 새 Event의 계약 |
| --- | --- | --- |
| RED 제외 | `2 × radius + red_margin = 10.3 cm` | 고밀도·재시도·감소 경로에서도 유지 |
| 물체 표면 간격 | `gap_factor × finger_thickness = 1.6 cm` | 기본값 유지. 명시적 설정 외 자동 감소 금지 |
| 중심 간 최소 거리 | 반경 4 cm 두 개이므로 9.6 cm | 모든 활성 쌍에서 만족 |
| 선반 경계 | 장애물 중심 bounds는 반경+wall margin을 반영 | 선반 밖·관통 위치를 대체 스폰 위치로 사용 금지 |
| 타겟·목표 | 기존 sampler로 한 번 결정 | 장애물 배치 실패를 이유로 재추출·거리 축소 금지 |

앞의 10.3 cm는 RED의 경로 팽창 반경이고 9.6 cm는 물체 쌍의 최소 중심 거리다. 서로 대체하지 않는다. 현재 타겟/goal의 `edge_clearance=2 cm`와 장애물 생성기의 `wall_margin=0.5 cm`도 별도 값이며 이 계획에서 묵시적으로 통합하지 않는다.

기하 계산은 생성기 frame의 cm, Event·simulator는 shelf/world frame의 m를 사용한다. 기존 좌표 변환을 한 경계에서 수행한다. 최종 simulator에 전달할 dtype으로 변환한 위치를 다시 검사하며, 수치 오차 대응은 작은 보수적 여유를 추가하는 방향으로 한다. tolerance를 이용해 최소 거리 미달을 허용하지 않는다.

보장 시점은 **reset 배치 완료 시점**이다. 이후 물리 운동으로 물체가 접근·접촉하거나 RED로 이동하는 것은 스폰 검증과 별개다. 안정화 step을 도입하면 안정화 후에도 다시 검사해야 하며, 새로 생긴 관통을 유효 스폰으로 보고하지 않는다. 이 기하 검사는 로봇 IK·실물 접근 가능성의 증명이 아니다.

### 2.2. 기존 알고리즘을 보존할 범위

기본 프로필은 GRAY/WHITE 소속, 뒤쪽 배정, 셀 점유, 이웃 수, 접근 경로 여유를 유지한다. 후보 분포와 낮은 셀 점유를 선호하는 기존 선택 방식도 가능한 범위에서 재사용한다. RED·거리·경계는 어떤 프로필에서도 완화하지 않는다.

셀이 가득 찼다는 이유와 물리 공간이 없다는 이유는 다르다. 기본 분포 규칙 때문에 요청 수를 채우지 못한 경우에는 `rule_limited`로 구분한다. 고밀도 실험에서 셀 점유·이웃 수의 상한을 바꾸려면 별도 명시적 프로필을 정의하고 기준선과 비교한다. 실패 시 상한을 몰래 올리거나 접근 경로를 제거하는 자동 fallback은 도입하지 않는다.

## 3. 영역별 개수 파라미터

다음 이름은 제안 인터페이스다. 구현 전 확정할 수 있으나 의미와 책임은 유지한다.

| 설정 | 의미·제약 |
| --- | --- |
| `gray_count` / `white_count` | 해당 영역의 요청 장애물 수. 0 이상의 정수이며 타겟 제외 |
| `rear_count` | GRAY 요청 중 뒤쪽 영역에 우선 배정할 수. `0 ≤ rear_count ≤ gray_count` |
| `max_gray_obstacles` / `max_white_obstacles` | simulator 시작 전에 만드는 고정 슬롯 용량. episode 도중 변경 금지 |
| `population_mode` | `fixed` 또는 `curriculum`. fixed에서는 개수 커리큘럼이 Event 값을 덮어쓰지 않음 |
| `population_schedule` | iteration별 영역 요청 수. 실제 배치 실패로 일정 자체를 낮추지 않음 |
| `min_surface_gap` | 물체 표면 사이의 최소 간격. 초기 기본값 0.016 m |
| `search_budget` | 후보 수, 재시작 수, 제한적 재배치 횟수의 상한. 값은 benchmark 후 결정 |
| `distribution_profile` | 셀 점유·이웃 수·접근 경로 및 후보 선택 규칙의 버전 |

총 요청 물체 수는 **1 + gray_count + white_count**다. rear_count는 중복 가산하지 않는다. 예를 들어 총 20개를 요청하려면 GRAY 7개·WHITE 12개 등으로 설정한다. 이 예시는 설정법이며 실제 배치 가능 개수의 주장이나 추천 비율이 아니다. 장애물 자체를 20개 요청하면 타겟 포함 21개다.

rear는 GRAY의 부분집합이다. `rear_count`는 뒤쪽에 배정할 슬롯의 quota이며 일반 GRAY 후보가 rear에 놓이는 것을 금지하는 값은 아니다. 따라서 **역할별 배정 개수**와 **공간적으로 rear에 들어온 총개수**를 구분해 기록한다.

영역 요청을 다른 영역으로 자동 이전하지 않는다. GRAY가 부족하다고 WHITE를 요청 이상으로 늘리면 사용자가 지정한 분포가 달라진다. 어느 영역을 줄였는지 결과에 남긴다. 요청이 슬롯 용량을 초과하거나 음수·실수·NaN이면 시작 시 설정 오류로 처리한다. 현재 `min(requested, capacity)` 방식처럼 조용히 자르지 않으며, 용량 부족을 물리적 한계로 보고하지 않는다.

향후 임의 다각형 영역은 별도 확장으로 남긴다. 첫 구현은 현재 존재하는 GRAY·WHITE·rear를 명확하게 파라미터화하여 검증 범위를 제한한다.

## 4. 유한 탐색과 개수 감소

### 4.1. 탐색 순서

1. 설정과 고정 타겟·목표를 검증하고 역할별 후보 영역을 계산한다. 슬롯 한도는 시작 전에 검사한다.
2. 기존 순서인 rear → 나머지 GRAY → WHITE로 요청 수 전체 배치를 먼저 시도한다. 후보는 채택 전에 RED·거리·경계와 활성 프로필 규칙을 통과해야 한다.
3. 한 역할을 채우지 못해도 이후 역할의 배치 시도를 계속한다. GRAY 실패 때문에 충분한 WHITE 공간까지 버리지 않는다. 채워진 슬롯과 미배치 슬롯은 별도 mask로 관리하며 미초기화 좌표를 검사에 넣지 않는다.
4. 현재 유효 부분 배치를 최선 후보로 저장한다. 다시 시작한 시도가 더 적은 수를 만들었다고 기존 최선 결과를 잃지 않는다.
5. 요청 수를 채우지 못한 환경만 추가 탐색한다. 동일 타겟·목표에서 후보 순서를 다양화하고, 막힌 슬롯 주변의 소수 물체를 되돌려 재배치한다. 기존 물체를 잘못 놓아 생긴 국소 포화를 전체 공간 부족으로 취급하지 않는다.
6. 잔여 공간을 층화하여 후보를 보충하고 부족한 영역부터 다시 삽입한다. 격자/층화 후보는 탐색 보완 수단이며 격자에 없다는 이유로 연속 공간의 불가능을 선언하지 않는다.
7. 정해진 예산 안에서 최선의 유효 결과를 선택하고 독립 검증기에 통과시킨다. 요청을 충족한 환경은 종료하며 다른 환경의 실패 때문에 다시 생성하지 않는다.

최선 후보의 비교 기준은 **필수 제약 만족 → 활성 장애물 수 최대 → 뒤쪽 배정·영역별 충족률 → 기존 분포 점수** 순으로 제안한다. 서로 다른 개수를 동일한 좌표 배열의 앞부분으로만 표현하지 않고 역할/slot ID를 함께 보관한다. 같은 seed에서 동률 선택도 결정적으로 수행한다.

20개 요청에 유효한 19개 결과가 있으면 불완전한 20개 좌표를 반환하지 않는다. 마지막 한 개를 겹쳐 놓거나 RED에 넣지 않으며, 가짜 좌표·중복 물체로 관측을 채우지 않는다. 모든 장애물 배치가 막히면 타겟만 남는 결과까지 표현할 수 있어야 한다. 단, 타겟 자체가 유효하지 않으면 설정/입력 오류이며 개수 감소로 숨기지 않는다.

### 4.2. “물리적으로 불가능”의 판정 한계

유한 후보 탐색은 **유효한 19개 배치가 존재함**을 보일 수 있지만, 임의의 연속 영역에서 **20개 배치가 전혀 없음**까지 일반적으로 보장하지 못한다. 따라서 다음 정보를 분리한다.

| 결과 | 판정 근거 | 처리 |
| --- | --- | --- |
| `fulfilled` | 요청 개수를 만족한 유효 배치 발견 | 그대로 반환 |
| `reduced_proven` | 적용한 기하 모델에서 타당한 상한/불가능 증명 확보 | 유효 부분 배치 반환, 증명 범위·상한 기록 |
| `reduced_search_budget` | 충분한 재배치 시도 후 예산 소진, 불가능 증명 없음 | 최선의 유효 부분 배치 반환, 최대 개수는 미확정으로 기록 |
| `invalid_input` / `validation_error` | 잘못된 설정·타겟·좌표 또는 최종 검증 실패 | 스폰 성공으로 처리하지 않고 명시적 오류 |

`rule_limited`는 별도 원인 필드다. 규칙을 포함한 상한으로 감소가 입증되어도 RED·거리만 적용한 물리적 수용량의 증명이라고 쓰지 않는다. 반대로 후보가 RED에서 자주 탈락했다는 통계만으로 그 영역이 공집합이라고 판단하지 않는다.

**실시간 Event에서는 `reduced_search_budget` 반환을 실용적 기본안으로 제안한다.** 이는 사용자의 무리한 배치·무한 탐색 방지 의도를 반영한 운용 방식이며, “물리적 불가능이 증명된 경우에만 감소”라는 엄밀한 계약을 완전히 만족하는 것은 아니다. 증명이 필요한 평가에서는 미확정 표본을 별도 오프라인 검증으로 넘긴다. 이 한계를 숨긴 채 “항상 전역 최댓값을 스폰한다”고 약속하지 않는다.

오프라인 검증에서는 작은 문제의 전수 탐색, 타당한 영역/거리 상한 또는 보수적 공간 분할을 사용한다. 제한된 후보 집합을 완전 탐색해 19개가 최대여도 결론은 그 후보 집합에 한정된다. 19개 하한과 타당한 19개 상한이 일치할 때만 해당 모델의 최대값을 확정한다. 면적비를 단순히 반올림한 값은 최대 개수의 증명이 아니다.

## 5. Manager 기반 Event 설계

### 5.1. 책임과 반환 자료

| 구성요소 | 책임 |
| --- | --- |
| Scene/EnvCfg | 고정 슬롯·센서·버퍼 용량 구성, geometry/config 검증 |
| Curriculum | 다음 reset의 요청 수 결정. 진행 중 episode의 mask 변경 금지 |
| 배치 생성 서비스 | simulator와 독립적으로 후보 생성·재배치·최선 결과 선택 |
| 독립 검증기 | 최종 활성 위치와 역할의 RED·거리·영역·경계·프로필 검사 |
| reset Event | `env_ids` 입력, 배치 서비스 호출, 상태·mask·초기 관측 갱신 |
| 관측·보상·종료 | 실제 활성 mask 소비. 스폰 탐색 로직은 포함하지 않음 |

새 결과 자료는 batch별 좌표, slot별 역할/활성 여부, 요청·실제 영역 개수, 상태 코드, 거절 원인, 사용 예산, 최소 거리·RED 여유, 접근 경로, seed/episode ID를 포함한다. 좌표 tensor는 고정 용량으로 유지하되 유효성은 mask로 판정한다. 미사용 슬롯은 simulator에 쓰기 전에 유한한 parking 위치로 채운다.

현행 `SceneBatch`는 고정 개수 배열과 단일 Config를 가정하므로 반환값에 mask만 덧붙여 기존 검증기를 그대로 사용하는 방식은 피한다. 새 결과를 이해하는 검증 경계를 활성 패키지에 두고, 기존 exact-count API는 호환성을 유지한다. 클래스명 등은 구현 시 정하되 Event를 거대한 환경 클래스 안에 합치지 않는다.

### 5.2. reset 처리 순서

현재 [ManagerBasedRLEnv](../../../../IsaacLab/source/isaaclab/isaaclab/envs/manager_based_rl_env.py)는 curriculum 계산 → scene reset → reset Events → 각 Manager reset 순서로 동작한다. 이를 기준으로 다음 의존 순서를 고정한다.

1. 초기화 시 전체 capacity와 관측 shape를 확정한다. material 초기화는 현행 startup Event에 둔다.
2. reset 대상 `env_ids`에 대해서만 요청 개수를 snapshot한다. `None`은 전체, 빈 ID는 무동작이며 비연속 ID도 지원한다.
3. `reset_all` 이후 타겟·목표를 한 번 샘플링하고 배치 결과를 임시 버퍼에 준비한다. 이때 완료된 다른 episode의 상태는 변경하지 않는다.
4. **최종 배치 검증 후** 해당 행의 pose·zero velocity·실제 active mask를 반영한다. simulator API를 통한 쓰기는 원자적 트랜잭션이 아니므로 중간 오류 시 성공 관측을 반환하지 않는다.
5. 미배치 슬롯은 기존처럼 100 m parking·중력 비활성·속도 0으로 처리하고 재활성 슬롯은 wake-up한다. 기존 구현이 피하는 simulation-disable 토글을 다시 도입하지 않는다. 주차 물체가 다른 환경·센서에 접촉하지 않는지도 확인한다.
6. 기존 episode 물성 Event를 적용한다. geometry를 바꾸는 randomization을 향후 추가한다면 반드시 배치 계산 전으로 옮긴다.
7. 실제 mask로 초기 위치·가림·노이즈 관측을 만들고, object-state/가속도·접촉 이력과 각 Manager의 reset 순서를 맞춘다. 이전 episode의 잔여 속도·접촉으로 첫 step 비용이 발생하지 않는지 검증한다.
8. 요청/실제 개수와 감소 원인을 logging용 상태로 저장한다. Manager reset이 `extras`를 덮어쓰는 시점을 확인하여 올바른 episode에 집계한다.

Event는 계속 `mode="reset"`을 사용한다. 실시간 USD prim 추가·삭제 또는 매 step 재배치를 하지 않는다. 물체 topology는 시작 시 고정하고 episode별 활성 집합만 바꾼다. 부모의 기존 `object_spawn`과 새 Event가 동시에 실행되지 않도록 최종 활성 term 목록을 검사한다.

## 6. 7개에서 20개까지 확장할 때의 의존 작업

첫 단계는 현행 최대 장애물 10슬롯 안에서 부분 배치·mask 계약을 완성하는 것이다. 그다음 타겟 포함 10/15/20개를 시험한다. 15/20개 설정은 아래 항목 완료 후에만 실행한다.

| 대상 | 작업·검증 |
| --- | --- |
| Scene·capacity | GRAY/WHITE 슬롯 합을 공통 capacity로 사용. Hydra override 이후 simulator 생성 전 재구성 유지 |
| 배치 생성기 | 10개 제한을 새 경로에서 해소. count-dependent `Config.check`의 셀 용량 검사와 기하 설정 오류를 분리하여 과다 요청도 부분 결과를 만들 수 있게 설계 |
| 결과·mask | 환경마다 다른 실제 개수, Gray-then-White 고정 슬롯, 타겟 index 0 유지 |
| 초기 관측 | raw 장애물 관측을 `4 × capacity`로 확장. 10슬롯 reshape·padding·가림·순차 교환 경로 제거/일반화 |
| 모델·export | 40D assertion·encoder reshape·입력 metadata·export 크기를 함께 변경. latent 크기는 별도 의도 없이 변경하지 않음 |
| 접촉·물성 | tactile filter·물체별 Hand contact sensor·PhysX buffer 크기·중력 flag의 object-major indexing 확인 |
| 보상·종료 | 실제 mask만 사용. parking 물체의 낙하/전도·가속도·힘이 들어가지 않도록 검사 |
| 저장·재개 | capacity·영역 규칙·gap·profile 버전 저장. shape가 다른 checkpoint의 무검사 로드 금지 |

동일 iteration으로 커리큘럼을 복원하는 것과 RNG 상태까지 동일하게 복원하는 것은 다르다. 정확한 배치 재현이 필요하면 환경별 seed/episode counter와 생성기 상태를 저장한다. 부분 reset 순서에 영향을 받지 않도록 `(seed, env_id, episode_index)` 기반 난수 스트림을 제안한다. 현행 공통 generator 스트림에서 변경되는 점을 기록하고 타겟·목표 sampler의 분포는 유지한다.

4096환경×20물체의 PhysX·센서 비용은 이번 소스 대조만으로 보장할 수 없다. CPU 후보 계산·GPU 왕복 복사·독립 검사·reset p50/p95/p99·steps/s·GPU 메모리·contact overflow를 함께 측정한다. 실패 행만 재시도하고 chunk 단위 후보 생성 및 거리 계산을 사용한다. 최적화로 GPU 구현을 먼저 추가하기보다 기존 NumPy 경로에서 비용을 측정한다.

Omni 계열의 로컬 `goal_rewards.action_rate_l2`·`joint_vel_l2`, raw 제곱합, Arm/Hand 분리와 지정 계수(Arm −0.03/−0.03, Hand −0.03/−0.01)는 유지한다. 활성 물체 수 증가로 물체별 비용의 합이 커지는 효과는 기록하되 이 스폰 작업에서 보상 정규화나 계수 조정을 끼워 넣지 않는다.

## 7. 단계별 산출물과 완료 기준

| 단계 | 개발 내용 | 다음 단계 진입 기준 |
| --- | --- | --- |
| P0 계약 확정 | 요청/실제/capacity·rear 의미, profile, search budget과 감소 상태 정의 | 기존 기본값과 새 설정의 대응표·오류 정책 완성 |
| P1 순수 기하 | 독립 결과형·validator, 최선 부분 배치, 유한 재시도·국소 재배치 | simulator 없이 모든 반환 배치의 RED·거리 위반 0, 미충족 원인 구분 |
| P2 reset Event | 요청 snapshot→검증→mask·pose·관측 반영, fixed/curriculum 분리 | 부분 reset·혼합 개수·비활성/재활성·resume 회귀 통과 |
| P3 용량 확장 | Scene·관측·encoder/export·contact 경로를 capacity 기반으로 변경 | 19 장애물 이상의 shape·mask·export 계약 통과, 기존 설정 회귀 유지 |
| P4 실행 평가 | 7/10/15/20개 요청, 여러 영역 비율·seed·목표 방향, 소규모부터 병렬 환경 확대 | 유효성·요청 대비 실제 수·reset 비용·메모리·미확정률 보고 |

기간은 P1/P3의 실패율·성능 측정 후 산정한다. OSC 안정화나 실물 에셋 확보 없이도 현재 실린더의 P0–P2는 진행 가능하다. 비정형 물체는 향후 footprint/radius 입력을 일반화하는 별도 단계로 분리한다.

### 필수 검증 사례

- **기본 회귀:** GRAY1/WHITE1과 GRAY3/WHITE3, 고정 타겟·목표, 현재 기본 gap·RED·접근 규칙. 단순 장면에서 요청 수를 불필요하게 줄이지 않는지 확인한다.
- **영역 설정:** 0/0, 한 영역만 요청, rear 0/GRAY와 동일, 음수·bool·실수·용량 초과. fixed 모드가 curriculum에 덮어써지지 않아야 한다.
- **고밀도:** 요청 전체를 채우는 알려진 배치, 마지막 한 개가 막히는 배치, 재배치해야 요청 수를 채우는 배치, GRAY 실패 후 WHITE는 가능한 배치를 구분한다.
- **20→19:** 19개 유효 배치와 해당 시험 모델의 19개 상한이 함께 주어진 fixture에서 19개를 반환한다. 별도로 20개 배치 witness가 있는 장면을 시험해 성급한 감소를 검출한다.
- **불가능/미확정:** 영역 공집합, 규칙 상한, 탐색 예산 부족의 상태를 구분한다. 후보 고갈을 물리 불가능으로 잘못 기록하지 않아야 한다.
- **경계:** RED 경계 안/밖, 최소 거리 바로 미만/이상, 선반 경계·frame 변환·float32 변환 후 위치, NaN/Inf와 final validator 실패를 검사한다.
- **배치 단위:** 같은 batch의 20/19/타겟만 존재하는 환경, 빈 batch, 순서가 섞인 `env_ids`, 비대상 행 불변, 실패 행만 재시도.
- **활성 mask:** parking 물체는 관측·가림·접촉 집계·보상·종료에서 제외되고 재활성화 시 pose·velocity·gravity·history가 일치해야 한다. 관측의 visible mask와 물리 active mask를 혼용하지 않는다.
- **재현·재개:** 동일 입력·seed·설정 재현, episode 중 개수 불변, iteration 복원, capacity 불일치 checkpoint 거절. 정확 RNG 재개를 지원하는지 별도로 표시한다.

CPU 테스트는 [루트 README](../../../../README.md)의 Isaac Lab Python 및 ROS 경로·pytest plugin 격리 방식으로 실행한다. 우선 기존 `test_clutter_layout.py`, `test_clutter_reset.py`, `test_clutter_fusion_v1_0_population.py`, `test_clutter_fusion_v1_0_cfg.py`, object-state/contact/model 테스트와 새 부분 배치 테스트를 대상으로 한다. 구체적인 새 테스트 파일·실행 명령은 구현 시 확정하여 실제 결과와 함께 로그에 남긴다.

Isaac Sim에서는 먼저 1환경, 이후 소규모 batch에서 reset·접촉·parking을 확인한 뒤 환경 수를 늘린다. 전체 대규모 학습을 시작하기 전에 충돌 버퍼 경고와 관통 여부를 확인한다. CPU 기하 통과를 simulator·학습 성공으로 대신하지 않는다.

## 8. 로그와 최종 인수 조건

매 reset 결과에는 요청/실제 GRAY·WHITE·rear 배정 수, 총 활성 수, 감소 상태·원인, 시도 수, 처리 시간, 최소 표면 간격·RED 여유, profile/version과 재현 seed를 기록할 수 있어야 한다. 대규모 실행에서는 집계 통계를 기본으로 하고 감소/오류 표본의 상세 좌표를 재현 자료로 저장한다. 요청 20개 실험을 실제 12개 장면만으로 채운 뒤 “20개 고밀도 검증”으로 보고하지 않는다.

완료 기준은 다음과 같다.

1. 영역별 요청 수를 설정만으로 바꿀 수 있고, 실제 수와 슬롯 용량이 구분된다.
2. 정상 반환된 모든 활성 배치에서 RED·거리·경계 위반이 없다. 검증 실패 결과는 simulator 실행 성공으로 반환하지 않는다.
3. 요청 수를 못 채우면 유효 부분 배치를 보존하고 무한 탐색하지 않는다. 20→19 사례를 재현하며 감소의 증명 여부를 정확히 기록한다.
4. Event가 실제 배치 결과를 기준으로 환경별 mask·관측·물성·이력을 일관되게 적용한다.
5. 10슬롯 초과 확장은 Scene부터 export까지 함께 검증하고, 고밀도에서의 속도·메모리 및 미확정 감소율을 공개한다.
6. 실제 구현 때 상속·등록·실행 안내와 개발 로그를 갱신한다. 학습 로그 정리는 수행하지 않는다.

이번 산출물은 이 계획서와 소스 대조·문서 검증 기록이다. 스폰 알고리즘·Event·환경·테스트 코드는 아직 변경하지 않았으며, 20개 수용 가능성·전역 최대 배치·실시간 성능·물리 안정성은 미검증이다.
