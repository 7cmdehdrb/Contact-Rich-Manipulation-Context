# 실제 코드와 수행 기록

[전체 안내](../README.md) · [지침](../00_guidelines/README.md) · [연구·계획](../01_plan/README.md) · [정적 자산](../03_assets/README.md)

기준일: 2026-10-14. 이 폴더는 실제 작성된 코드의 계약과 상태, 개발 과정, 수행한 실험·검증을 설명한다. 문서마다 코드 확인·구현 보고·실제 실행·미확인을 구분하며, 설계와 앞으로 수행할 검증은 [연구·계획 영역](../01_plan/README.md)에 연결한다.

## 현재 구현을 확인할 문서

| 문서 | 확인할 내용 |
| --- | --- |
| [코드·장비 상태](07_CODE_AND_HARDWARE_STATUS.md) | 코드와 하드웨어 준비 상태 및 확인 근거 |
| [활성 환경 안내](08_ACTIVE_ENVIRONMENTS.md) | 활성 패키지·환경 상속·observation/action/controller/reward/termination/reset와 실행 명령 |
| [Fusion v0 → v2 → v3 → v1_0 변경 비교](environments/CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md) | 단계별 보상·커리큘럼·장애물·wrench 변화와 상속·실행 |
| [Contact Sweep Clutter Fusion v1_0 환경 설명](environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_0_ENVIRONMENT.md) | v1_0 자체의 Scene·관측·Action·17개 보상·6개 종료·9개 curriculum·학습 복구 |
| [Contact Sweep Clutter Fusion 환경 설명](environments/CONTACT_SWEEP_CLUTTER_FUSION_ENVIRONMENT.md) | Scene 의도·Actor/Critic 관측과 노이즈/Frame·Action 범위·15개 보상 수치·종료·커리큘럼의 독립 설명 |
| [Contact Sweep Clutter v1 MDP](environments/CONTACT_SWEEP_CLUTTER_V1_MDP.md) | v1 자체의 관측·8D Action·14개 보상·상태 전이·종료를 설명하는 독립 문서 |
| [Contact Sweep와 Clutter 구성](environments/CONTACT_SWEEP_ENVIRONMENTS.md) | 두 v0 환경의 공통 제어·물성·관측·보상·종료와 장애물 배치·MLP·실행 비교 |
| [Omni 환경](environments/OMNI_ENVIRONMENT.md) | 현재 적용된 환경 구성과 확인한 동작 범위 |
| [Baseline Tactile 환경](environments/TACTILE_ENVIRONMENT.md) | 기존 물리 형상 유지·17개 Binary 접촉 영역·57D 관측과 검증 범위 |
| [Sweep Omni v3 구성](environments/SWEEP_OMNI_V3_ENVIRONMENT.md) | 관측 41D·높이 조건부 접근 진행·목표 진행·종료·이벤트의 독립 설명 |
| [Dex Omni v0 구성](environments/DEX_OMNI_V0_ENVIRONMENT.md) | 관측 41D·거리 기록 개선 보상·종료·이벤트의 독립 설명 |
| [접근·목표 진행 보상 수식](environments/REACH_AND_GOAL_REWARD_FORMULAS.md) | 높이 조건부 XY 접근·정규화 목표 진행·Dex 거리 개선 보상 4종의 수식과 차이 |
| [개발 로그](logs/README.md) | 변경·실행 조건·검사 결과·미실행 항목과 당시 관찰 |

활성 패키지는 workspace의 `src/inspire_sweep_baseline`, `src/axia80_feasibility`다. 실제 환경·등록·config·runner는 활성 환경 문서에서 코드로 이어서 확인한다. 현재 기준선의 Arm Joint Position 제어와 발표의 57D/8D·OSC 설계는 각 문서의 확인 단계에 따라 읽는다.

## 수행한 실험과 재현

| 문서 | 기록 범위 |
| --- | --- |
| [2026-09-22 Axia80 F/T feasibility 결과](experiments/2026-09-22_axia80_ft_sensor_feasibility.md) | 질량·자세별 simulation 측정과 기대 반력 비교, 근거 산출물과 해석 한계 |
| [2026-09-22 Axia80 구현·재현 가이드](experiments/2026-09-22_axia80_ft_sensor_implementation.md) | 당시 구현·시험 조건·좌표계·측정·재현 절차와 현재 코드 위치 |

실험 결과의 CSV·metadata·run.log는 [정적 실험 자산](../03_assets/artifacts/axia80_feasibility/results/)에서 관리한다. 원시 파일의 존재, 당시 실행 보고, 현재 재실행 여부는 각각 구분한다. 수행 전 계획은 [9월 26일 환경 구축 계획](../01_plan/experiments/2026-09-26_blind_sweeping_build_plan.md)과 [Omni 보상 계획](../01_plan/environments/OMNI_REWARD_PLAN.md)에서 확인한다.

## 과거 구현 상태

[2026-07-19 Sweep RL 상태](history/2026-07-19_sweep_rl_status.md)는 보관된 `sweep_rl`의 당시 구현 보고와 후속 작업이다. 현재 활성 환경의 사양·성과·TODO는 현재 문서에서 확인한다. 과거 설계와 개정 요청은 [계획 이력](../01_plan/history/README.md)에서 찾는다.

## 새 기록을 남기는 방법

코드 변경 전에 [개발 지침](../00_guidelines/09_DEVELOPMENT_GUIDE.md)과 실제 활성 코드를 읽는다. 새 개발 로그는 `logs/YYYY-MM-DD_<topic>.md`, 수행한 실험 기록은 `experiments/YYYY-MM-DD_<topic>.md`에 작성하고 [연구 로그 템플릿](../00_guidelines/templates/RESEARCH_LOG.md)을 활용한다.

기준 commit·작업트리 변경, 환경·config 상속, 정확한 명령, 실제 검증·결과와 미실행 항목을 남긴다. 새 문서·자산의 색인 등록과 링크 검사는 [문서 구조 규칙](../00_guidelines/DOCUMENT_STRUCTURE.md)을 따른다. 연구 결정의 변경은 [결정 목록](../01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md)에 기록한다.
