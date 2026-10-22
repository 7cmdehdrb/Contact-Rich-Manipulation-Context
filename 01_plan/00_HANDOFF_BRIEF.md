# Blind Sweeping — 단일 파일 인계 요약

**2026-10-22 Fusion v1.0 후속 수정:** 같은 task에 Gray1/White1→3/3 개수 curriculum, Goal hold tolerance와 동기화한 접촉 alpha, 비활성 물체 mask를 적용했다. 가속·감속에는 같은 기존 지수 비용을 사용한다. 재사용 가능한 `train_resilient.py`는 조기 중단 시 최신 checkpoint−500에서 커리큘럼을 복원한 뒤 재개한다. [현재 계약·실행·실제 검증](../02_implementation/logs/2026-10-22_clutter_fusion_v1_0_population_recovery.md)을 따른다.

**2026-10-22 Fusion v1.0 추가:** v3을 직접 상속한 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0`을 추가했다. 보상·종료·커리큘럼 CFG는 독립 선언이며, 손 전체 접촉 유지·비타겟 접촉 힘·EEF wrench 크기 변화량·물체별 가속도 비용과 새 Goal 일정을 사용한다. 이후 v1_1의 상속 기준이다. [계수·계약·실제 검증](../02_implementation/logs/2026-10-22_clutter_fusion_v1_0.md)을 따르며 장시간 학습 성과와 구분한다.

**2026-10-21 Fusion 상속 재구성:** 현재 체인은 Fusion v0 → v2 → v3이다. v2는 EEF orientation 보상만 제거하며 push_fast=0.8을 유지한다. v3은 v2에서 커리큘럼만 변경하며 push_fast는 모든 버전에서 0.8로 고정한다. 기존 Fusion v1은 v3으로 재작명했으며 사용자 수정 일정은 보존했다. [현재 계약·검증](../02_implementation/logs/2026-10-21_clutter_fusion_v3.md)을 따른다.

**2026-10-21 Clutter Fusion:** 사용자 확인에 따라 Curriculum v1과 v2 보정 F/T를 결합한 독립 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v0`를 추가했다. 초기 가림·1% flip, policy 55D, 보상 통합·Contact/object 강화, EEF 자세·속도 및 유한 F/T 변화율 비용, 보상·Goal deadzone 커리큘럼을 사용한다. 기존 환경 Cfg를 상속하지 않으며 [계약·계수 근거·검증](../02_implementation/logs/2026-10-21_clutter_fusion.md)을 따른다. 새 학습 성과와는 구분한다.

**2026-10-21 F/T 수집 완료:** Curriculum v1 정책의 기존 입력을 유지하는 테스트 환경에서 v2 보정 F/T를 동시 수집했다. `model_12800.pt`, 16환경·5000 제어 step의 CSV 80000행·125열과 전체 검증을 완료했다. 새 F/T 보상 계수·정책 입력 변경은 후속 작업이며 [수집·재현 기록](../02_implementation/logs/2026-10-21_clutter_ft_collection.md)을 따른다.

**2026-10-20 Clutter v1 Curriculum 추가:** 현재 v1을 상속한 `Isaac-Inspire-Contact-Sweep-Clutter-Curriculum-v1`에 Learning iteration 기반 네 보상 일정을 추가했다. 물체 free speed 0.1→0.05, Arm free speed 1.0→0.8, Arm action-rate·joint-velocity 가중치 각각 −0.03→−0.06이며 사용자 명시 요청에 따른 변형이다. [일정·runner 재개 의미·실제 검증 범위](../02_implementation/logs/2026-10-20_clutter_v1_curriculum.md)를 확인한다. 정책 성능 향상은 미검증이다.

**2026-10-20 Clutter v2 추가:** v1을 상속한 `Isaac-Inspire-Contact-Sweep-Clutter-v2`에서 F/T 관측을 Hand 중력·관성 하중을 제거한 6축 외력 반력 추정값으로 교체했다. 힘·모멘트 변화 제곱 비용은 작은 변화의 허용 구간, 최대 −0.1/초, 실제 누적 양의 보상 대비 5% 예산 제한을 갖는다. 관측 차원·Action·나머지 보상·종료는 v1을 유지한다. 모델 기반 시뮬레이션 보정과 실물 캔슬레이션 성능은 구분하며 [구현·검증 기록](../02_implementation/logs/2026-10-20_contact_sweep_clutter_v2.md)을 확인한다.

**2026-10-20 Clutter v1 추가:** 사용자 요청으로 `Isaac-Inspire-Contact-Sweep-Clutter-v1`을 v0에서 상속했다. Actor는 타겟 시작 위치, Critic만 추가 현재 XYZ를 사용한다. 월드 XY 1 cm 목표 체류·촉각 접촉 두 항·상한 있는 장애물 이동 비용을 추가하고, 지정 v0 로그로 양의 보상 비중 약 35/35/20/10의 초기 계수를 산정했다. [구현·계수 근거·실제 검증](../02_implementation/logs/2026-10-20_contact_sweep_clutter_v1.md)을 확인한다. 이 비중은 체류 5초·접촉 7초 가정이며 학습된 v1 성과가 아니다.

**2026-10-20 장애물 확장:** 사용자 확인에 따라 Contact Sweep을 상속하는 `Isaac-Inspire-Contact-Sweep-Clutter-v0`를 추가했다. 부모 타겟·목표 분포와 고정 로봇 초기 자세를 유지하고, 목표를 확정한 뒤 `scene_randomization` 규칙으로 장애물 3개(뒤쪽 GRAY 1개·WHITE 2개)를 배치한다. 같은 날 후속 요청으로 v0의 RED 제외 반경을 8.3→10.3 cm로 확대했다. 모든 물체의 tilt·낙하·촉각을 반영하며, 초기 장애물 40D를 MLP 16D로 압축한다. [환경 계약·실행](../02_implementation/08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-v0--2026-10-20)과 [검증 로그](../02_implementation/logs/2026-10-20_contact_sweep_clutter.md)를 따른다. 연구·실물 성과와 구분한다.

**2026-10-20 구현 추가:** 사용자 요청으로 Renewal v3를 보존하면서 독립 기준 task `Isaac-Inspire-Contact-Sweep-v0`를 구성했다. 기존 환경 Cfg를 상속하지 않는 별도 Env·Scene·Manager·PPO 클래스를 사용한다. v3와의 설정·짧은 GPU 실행 동등성 검사 범위는 [활성 환경](../02_implementation/08_ACTIVE_ENVIRONMENTS.md)과 [검증 로그](../02_implementation/logs/2026-10-20_contact_sweep_reference.md)를 따른다. 아래 연구 범위와 실물 성과 구분은 유지한다.

[문서 안내](README.md) · [문헌조사](literature/README.md) · [조사 그룹](literature/reviews/README.md)

**기준일: 2026-10-14.** 아래 연구 범위는 9월 14일 피드백에서 출발하며, 이후 발표 설계·코드·로그를 연결해 현재 인계 상태를 정리한다. 연구 방향, 계획, 적용 코드, 실험 성과는 각각 구분한다.

## 문서 저장 위치

이 문서 저장소는 `00_guidelines/`(지침), `01_plan/`(연구·계획), `02_implementation/`(실제 코드·개발·실험 기록), `03_assets/`(정적 자료)의 네 영역으로 구성된다. [전체 문서 안내](../README.md)에서 탐색하고 [문서 구조 규칙](../00_guidelines/DOCUMENT_STRUCTURE.md)에 따라 작성·이동·참조를 검사한다. 루트 `AGENTS.md`는 필수 지침 진입점이다. 계획과 구현의 확인 수준은 기존 기준을 유지한다.

## 현재 Workspace와 먼저 확인할 상태

활성 패키지는 사용자 결정으로 `src/inspire_sweep_baseline`, `src/axia80_feasibility` 두 개다. 나머지 `src` 패키지는 `src/trash`에 보존하며 `COLCON_IGNORE`로 ROS2/colcon 검색에서 제외한다. Isaac Lab의 Python/Gym 등록은 ROS2 빌드와 별개다.

| 구성 | 현재 역할과 확인 범위 |
| --- | --- |
| `inspire_sweep_baseline` | 독립 Manager-based Sweep RL 기준선, Realistic Physics, Initial Privileged, Omni v0/v1, Baseline Tactile의 6개 task. Arm은 Joint Position command를 사용한다. 기본 baseline은 현재 물체 위치를 받는 41D/8D이며, 새 Tactile은 17개 bit를 포함한 57D/8D다. 둘 다 최종 Blind actor와 구분한다. |
| `axia80_feasibility` | 정하중·cantilever·각도별 6축 반력과 frame·raw/tare를 검증하는 simulation 실험. Hand 기반 RL 패키지와 구분한다. |
| `example/Sweep-Policy` | 이전 Sweeping RL 프로젝트를 참고하고 내부 환경 변형을 비교하는 submodule. 전체 프로젝트의 현재 코드 기준은 활성 패키지 안내를 따른다. |
| `scene_randomization` | NumPy 장면·분포·접근 경로의 기하 검증 도구. 로봇 IK·접촉 물리·마찰·전도나 활성 RL reset 연결을 증명하지 않는다. |

실제 상속·입출력·실행 명령은 [활성 환경 안내](../02_implementation/08_ACTIVE_ENVIRONMENTS.md), 구조와 문서 경계는 [Workspace 안내](../00_guidelines/10_WORKSPACE_GUIDE.md), 개발 원칙과 로그는 [개발 지침](../00_guidelines/09_DEVELOPMENT_GUIDE.md)을 따른다. Manager-based RL의 OOP 원칙을 지키고, 환경의 상속 구조·task ID·실행 명령·기준 commit·검증·미실행 항목을 기록한다.

전체 flow·연구·계획·결정·상태·개발 로그는 이 문서 전용 submodule에 저장한다. `example/Sweep-Policy/docs`는 해당 참고 환경의 설명에, workspace 루트 `docs`는 두 프로젝트와 관계없는 일반 지식에 사용한다. 문서 저장소만 전달받은 에이전트도 전체 흐름을 이해하도록 핵심 설명은 내부 문서에 담는다.

[최종 중간발표 설명](presentation/README.md)은 2026-10-05 문서화한 연구 설계다. 57D 관측, Arm Cartesian 증분 6D + Hand 2D 행동, OSC와 Hand Joint Position, CoP 회전 Sub-Goal·센서/보상 비교 계획을 설명하며 구현·학습·실물 성공과 구분한다. 일반 Observation Stack·Sliding Window·이력 기반 물성 적응은 보류다. 현재 baseline의 Joint Position 제어와 발표의 OSC 설계를 같은 계약으로 읽지 않는다. Omni의 [현행 환경](../02_implementation/environments/OMNI_ENVIRONMENT.md)과 [보상 계획](environments/OMNI_REWARD_PLAN.md)도 적용 코드·계획을 나누어 확인한다.

## 연구가 무엇인가

선반에서 물체를 치워 공간과 시야를 확보하는 상위 시스템의 하위 조작 기술을 연구한다. 대상은 석사생 1의 담당 영역이며, 초기 시각 정보와 상위 계획으로 주어진 조건에서 **실행 중 시각 관측을 갱신하지 않고 손목 F/T와 Hand 촉각으로 지정된 물체를 미는 정책**이다. 초기 시각 정보까지 제거하는 연구가 아니다.

‘대상 물체’는 **이번에 밀 물체**다. 선반 뒤에서 궁극적으로 찾으려는 물체와 구분한다. 상위 판단기의 선택, 전체 탐색 계획, 물체 근처까지의 접근은 직접 구현 범위에서 분리한다. 하위 정책은 접근 완료 후의 불확실한 근접 상태에서 시작한다.

## 지금 무엇에 집중해야 하나

9월 14일 교수 피드백은 **복잡한 랜덤 배치 회피·추가 간섭 판별을 먼저 붙이지 말고, 시각 없이 제한된 힘·촉각 정보로 기본 Sweeping을 수행할 때의 문제를 깊이 검증하라**는 것이다.

핵심 질문은 접촉 위치가 달라도 동작하는지, 센서가 없는 손 부위에 접촉하면 어떻게 되는지, 가벼운 물체에서 F/T 신호가 충분한지, F/T와 촉각이 각각 어떤 정보를 제공하는지, 커버리지·해상도가 성능을 어떻게 제한하는지다. 이들은 **예정된 Hand·F/T 장비에서 이미 검증된 결함이 아니라 확인할 연구 질문**이다.

Clutter는 배경으로 유지할 수 있다. 다만 물체 수나 기능 수를 늘리는 것 자체를 기여로 삼지 않는다. 단일 물체로 기본 문제를 분리해 검증하는 것은 가능하지만 최종 환경이 단일 물체로 확정된 것은 아니다. 센싱 문제를 연구하는 것과 센서 하드웨어 자체 개발에 매몰되는 것도 구분한다.

## 시스템과 센싱 계획

```text
초기 시각 관측 / 상위 판단
  → 조작 대상과 목표 방향·거리 결정
  → 별도 접근 계획·실행
  → 물체 근처에서 하위 정책 시작
  → 초기정보 + 실시간 F/T·촉각 + 채택할 고유감각/이력
  → Cartesian 조작 명령
  → 종료·결과 전달 방식은 추가 설계
```

장비 계획은 UR5e → ATI Axia80-M8 6축 F/T → Inspire Dexterous Hand다. 프로젝트에서는 Hand 6자유도와 17개 촉각 영역을 전제로 논의했다. 이전 연구안은 영역별 gram-force Grid를 scalar/Boolean 하나로 축약해 17차원으로 사용하는 방안을 제시했다. 제품 원시 포맷·센서 위치·부착 범위·해상도·샘플링률의 검증된 명세와 구분한다. 9월 14일에는 센서와 Hand 실물이 아직 준비되지 않았다고 보고했다.

9월 14일에는 초기 대상 pose, 목표 방향·거리, F/T와 촉각이 입력의 중심이었으며 정확한 관측 벡터와 축약 방식은 미정이었다. 당시 23차원 표현은 전체 관측 차원이 아니었다. 이후 발표의 57D/8D 설계와 현행 환경별 차원은 상단의 발표·활성 환경 문서에서 구분하여 확인한다.

## 9월 14일 연구 경계와 이후 설계의 구분

| 항목 | 현재 해석 |
| --- | --- |
| Vision | 초기 사용 허용. 한 번의 하위 Sweep 중 지속 물체 시각 추적 없음 |
| 초기 주변 정보 | 처음부터 전혀 모른다는 강제 가정은 9/14에 수정. 하위 입력 범위는 미정 |
| 시작 조건 | 별도 접근이 완료된 물체 근처. 실제 접촉과 촉각 감지는 보장되지 않음 |
| 방향·거리 | 목표 조건의 중심. 좌우는 구체적인 출발안이며 전방향의 구현 범위는 추가 결정 |
| Geometry | 9/13안은 명시 입력 없음. 9/14에 상세 입력 사양을 다시 확정한 것은 아님 |
| Controller | 9/10 보고 구현은 OSC. 이후 안에는 Diff-IK 등의 변환이 등장. 최종 실물 경로 미확정 |
| Hand 제어 | 사전 정의 자세 구상. 손가락 전체 자유 제어를 확정하지 않음 |
| 간섭 판별·중단 | 9/13 중심 제안에서 9/14 후순위 확장으로 이동 |
| 완료·대기 | 물체 목표 도달과 EEF 이동을 구분. 실물 Blind 종료·대기 전환은 미정 |
| 안전 정지 | 연구용 간섭 판별 우선순위와 별개. 안전 기능을 제거·자동 해제하지 않음 |

위 표는 9월 14일의 범위·미정 상태를 보존한다. 이후 360도 방향·57D/8D·OSC 발표 설계와 후속 변경은 [결정 목록](03_DECISIONS_AND_OPEN_QUESTIONS.md), 실행 코드의 구체값은 [활성 환경](../02_implementation/08_ACTIVE_ENVIRONMENTS.md)을 따른다. ‘확인된 방향’은 ‘실험 완료’가 아니다. ‘미정’은 임의로 선택해도 된다는 뜻이 아니다. 필요한 제안은 제안이라고 표시하고 검증 방법을 남긴다.

2026-10-16 사용자 지정에 따라 이후 환경 확장의 기준은 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v0`다. 실행기 기본 task는 바꾸지 않으며 상속으로 확장한다. 비용 상한·손목 높이·방향 제한을 갖춘 v1의 계약과 검증은 [활성 환경](../02_implementation/08_ACTIVE_ENVIRONMENTS.md), [개발 로그](../02_implementation/logs/2026-10-16_dex_tactile_renewal_v1.md)에서 확인한다.

2026-10-18에는 v0 직접 상속의 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2`에 안정된 목표 위치 0.5초 유지 성공·일회성 +100 보너스·연속 유지 시간에 비례하는 최대 +20/초 보상을 추가했다. 새 속도·위치 오차 비용이나 액션 제한은 추가하지 않는다. [구현·검증 로그](../02_implementation/logs/2026-10-18_dex_tactile_renewal_v2_goal_hold.md). 장시간 학습·정착 성능 개선은 미검증이다.

같은 날 사용자 의도를 명확히 반영해 **성공으로 종료하지 않고 기존 실패 또는 10초 timeout까지 유지**하도록 수정했다. +100은 episode당 최초 한 번만 지급하고 목표 유지 보상은 이후에도 최대 +20/초로 계속 지급한다. 목표 이탈/재진입 시 유지 보상은 다시 증가하지만 +100을 반복 지급하지 않는다. OSC v2도 상속으로 동일하게 적용한다. [후속 수정·검증](../02_implementation/logs/2026-10-18_v2_goal_hold_until_timeout.md).

같은 날 v2를 직접 상속한 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2`를 추가했다. Arm만 stiffness 100의 OSC로 교체하고 Cartesian 명령 norm을 5 mm/0.025 rad로 제한한다. v2 보상·종료·센서는 상속한다. 초기 응답 감소와 별개로 0 명령에서도 이후 과속이 재현되어 지속 안정성은 미해결이다. [실측과 실행 안내](../02_implementation/logs/2026-10-18_dex_tactile_renewal_v2_osc.md).

후속 사용자 지시로 v2의 부모를 v0에서 v1로 변경했다. **현재 체인은 v0 → v1 → v2 → OSC v2**다. 따라서 v2와 OSC v2에 v1의 지수 속도 비용 상한 100·손목 종료 높이 3 cm·±X 각각 ±15° 목표 방향 제외가 적용되고, +100 일회성 보너스·목표 유지 보상·성공 후 timeout까지 실행하는 동작은 유지한다. 물체 스폰 위치 분포는 바꾸지 않는다. [상속 전환·검증](../02_implementation/logs/2026-10-18_v2_inherits_v1.md).

## 실제로 어느 정도 진행됐나

9월 10일에는 기존 Sweeping 환경을 Joint action에서 Cartesian/OSC로 바꾸고, 일부 상대 관측과 EEF·물체 초기 랜덤화를 시험했다고 보고했다. 다른 초기 joint configuration에서 sweeping이 가능했다는 보고도 있다.

그러나 당시 **정책에 F/T 없음, tactile 없음, 완전한 Blind 정책 아님, Sim-to-Real 전, 실제 접근 오차 기반 초기 분포 없음**으로 명시했다. 이는 사전 feasibility이며 현재 연구의 완성 결과가 아니다. 9월 11일 대화에는 Isaac Lab/RSL-RL PPO 설정이 공유됐지만 설정만으로 센서 입력과 성능을 알 수 없다.

**별도 센서 시험은 있었다.** 9월 10일에는 시험 중인 압저항 촉각 센서가 넓은 접촉면에서 충분한 신호를 내지 못하고 좁은 면에서 상대적으로 잘 반응한다는 보고가 있다. 무게·속도 등을 바꾸어 시험했다는 내용도 있다. 이는 그 시험 센서의 관찰 보고이지 구매 예정 Inspire Hand·Axia80의 실측 성능이 아니다. 원시 로그와 정량 수치는 이번에 확인하지 못했다.

9월 14일 최초 인계에서는 실제 코드·run·checkpoint를 직접 확인하지 못했다. 이후 [9월 22일 Axia80 결과](../02_implementation/experiments/2026-09-22_axia80_ft_sensor_feasibility.md), [10월 9–12일 개발 로그](../02_implementation/logs/README.md), 현재 활성 환경의 코드 검토가 추가되었다. 10월 12일 기록은 당시 환경·저장 설정·checkpoint 조사이며 그 작업에서 학습·재생·성공률 평가를 실행한 것은 아니다. 현재 정리에서도 새 학습이나 실물 성능을 확인했다고 주장하지 않는다. Hand의 10월 중순 도착 가능성은 당시 예상이며 도착·장착·수신 완료 여부는 미확인이다.

## 다음에 해야 할 일

**첫째, 현재 사실을 고정한다.** [활성 환경 현황표](../02_implementation/08_ACTIVE_ENVIRONMENTS.md)를 사용하고 실제 적용 config·자산 가용성·설치 버전·평가 결과의 미확인 항목을 보완한다. actor observation, reset, action→controller, reward·termination의 변경은 표와 로그에 반영한다. 장비 준비 상태와 원시 센서 구조를 확인한다. 기존에 구축 중인 관련 기반을 새 방향이라는 이유로 전부 버리지 않는다.

**둘째, 선행연구와 센싱 feasibility를 병행한다.** Blind/부분 시각 관측의 F/T·촉각 조작 연구를 센서 구성·커버리지·해상도·태스크·실물 검증 기준으로 비교한다. 실물이 없으면 가정을 명시한 시뮬레이션 센서 모델로 접촉 위치·사각지대·약한 신호를 분리해 검토한다. 기존 압저항 시험은 센서 모델·조건·로그를 복원할 수 있는 범위에서 재사용한다.

**셋째, 최소 조작 실험을 만든다.** 접근 완료 후 근접 상태에서 단순 물체를 밀며 학습·평가 정답과 actor 입력을 분리한다. 대상 물체 이동과 Hand 이동을 따로 측정한다. 기본 제어·보상·센싱 확인 후 F/T-only, tactile-only, 결합 센싱, 필요시 history를 비교한다. 이 비교 구성은 인계 문서의 실행 제안이지 이미 승인된 최종 실험표가 아니다.

**넷째, 실제 접근 오차와 실물 전달을 검증한다.** 상위 접근을 반복해 EEF–물체 상대 pose 오차를 측정하고 reset 분포를 갱신한다. 실물 조건이 준비되면 신호·제어·종료의 simulation 차이와 실패를 기록한다. 간섭 판별 등 확장은 기본 결과와 문헌 검토 뒤에 필요성을 판단한다.

각 단계의 완료 기준은 상세 next-actions 문서에 있다. 교수 지시, 학생 제안, 인계 작성자의 실행 계획, 실제 결과를 섞지 않는다.

## 다른 에이전트가 하지 말아야 할 일

Pivoting·approach·장면 해석을 학생 1 필수 과업으로 합치지 않는다. 과거 structured compliance·strict rotation constraint·RNN·hybrid action을 현재 확정 요건으로 되살리지 않는다. 사용자가 초안이라고 한 roadmap을 절대 규격으로 취급하지 않는다.

실시간 object GT pose를 최종 Blind actor에 계속 넣고 Blind 성능이라고 보고하지 않는다. 실제 센서가 제공하지 않는 contact ID·비센서 영역 정보를 actor에 넘기지 않는다. F/T 증가가 곧 주변 물체 간섭이라고 단정하지 않는다. EEF 이동으로 물체 성공을 대체하지 않는다. PPO를 바꾸기 전에 실패 원인과 실제 적용 config를 확인한다.

자료가 부족하면 무엇을 확인하지 못했는지 적고 확보한 근거로 가능한 작업을 진행한다. 이미 문서·코드에서 읽을 수 있는 배경을 사용자에게 반복해서 설명하게 하지 않는다.

## 공유·갱신과 출처

9월 11일에는 팀 공용 Agent Context와 교차 검토 체계가 요청되었다. 이 저장소는 학생 1의 맥락을 전달하는 문건이며 팀 전체 자료 수집·권한 설정 완료를 뜻하지 않는다. 새 미팅·실험이 생기면 현재 요약, 결정 목록, 다음 작업을 함께 갱신하고 구안은 변경 이력으로 보존한다.

상세 문서가 함께 있다면 `AGENTS.md`, `01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md`, `01_plan/04_NEXT_ACTIONS.md`를 우선 읽는다. 코드 작업은 `02_implementation/08_ACTIVE_ENVIRONMENTS.md`, `00_guidelines/09_DEVELOPMENT_GUIDE.md`, `00_guidelines/10_WORKSPACE_GUIDE.md`와 실제 활성 코드를 읽은 뒤 수행한다.
