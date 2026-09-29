# 발표 문서 안내

[연구 문서 안내](../README.md) · [결정·미정 목록](../03_DECISIONS_AND_OPEN_QUESTIONS.md)

발표 자료를 논문의 Motivation·Related Works·Method 역할에 맞춰 다음 세 본문으로 나누며, 별도의 타임라인·비교 발표 초안을 함께 관리한다.

| 문서 | 다루는 내용 |
| --- | --- |
| [01. Research Motivation and Contributions](01_Research_Motivation.md) | 문제의식, Binary Tactile–Wrench 역할 분담, 제안하는 Contribution |
| [02. Related Works](02_Related_Works.md) | F/T·Wrench 선행연구, Tactile 선행연구, RL Reward Formulation, 항목별 DR 비교 |
| [03. Method](03_Method.md) | MoveIt 접근 Process, MDP 하위의 Event·Observation·Action·Reward, DR·센서 불확실성 |

## 2026-09-30 최종 슬라이드 발표 대본

[15분 이내 발표 대본](05_Midterm_Presentation_Script_15min.md)은 `졸업발표_ver2_최종.pdf`의 1–35쪽에 맞춘 실제 발화용 원고다. [페이지별 발표 흐름 메모](HELP.md)를 바탕으로 완결된 문장과 화면 전환을 구성하고, 페이지별 시간과 누적 체크포인트를 제공한다.

센서의 상보성, CoP 기반 회전 Sub-Goal의 학습용 보상 역할, 센서·보상 Ablation을 중심으로 설명한다. DR은 학습 설정으로만 다루며 별도 평가 실험은 포함하지 않는다. 시간은 발화 분량과 전환을 바탕으로 산정한 편집 예산이며, 실제 리허설 측정값과 구분한다.

## 2026-09-30 중간발표 정리본

[이진 촉각과 손목 힘·토크 기반 목표 지향형 Sweeping — 중간발표 본문](2026-09-30_midterm/README.md)은 `졸업발표_ver1(6).pdf`와 발표 검토 대화를 기준으로 정리한 독립 문서다. 슬라이드 순서가 아니라 **연구 동기 → 선행연구의 설계 선택 → 제안 방향 → 과업·센서·정책·보상 → 종료·학습 조건 → 센서 기여 검증**의 논리로 구성한다.

센서 Ablation은 **Case 4–Case 2: F/T의 추가 기여**, **Case 4–Case 3: Tactile의 추가 기여**로 정리한다. 발표본의 수식·조건과 대화 보완을 구분하며, 남은 확인 사항과 발표본에 없는 후속 제안은 별도로 표시한다. 기존 세 본문과 문헌 노트는 변경하지 않는다.

## 관련 연구 비교 발표 초안

[04. Related Work Timeline and Contributions](04_Related_Work_Timeline_and_Contributions.md)는 8장 발표 흐름, 연도별 연구지도, Observation·Sensor·Method·강건성·Sim-to-Real 비교표와 검증 전 Contribution 후보를 정리한다. [33편 원문 근거](../literature/reviews/2026-09-22_related-work-five-axis-evidence.md)로 연결하며, 기존 세 본문의 확정 설계를 변경하는 문서는 아니다.

## 현재 작업 범위

Method는 360도 Sweep Command, MoveIt 접근 후 초기화, Observation 57차원과 Action 8차원, Manipulator OSC와 Hand Joint Position Controller를 현재 설계로 정리한다. 관측에는 **직전 Action 8차원**을 포함하지만, Observation Stack·Sliding Window·이력 기반 물성 적응은 추가하지 않는다. 선행연구가 실제로 사용한 이력에 대한 설명과 기존 문헌조사 자료는 보존한다.

Related Works의 F/T·Wrench 절은 지정한 6편의 규칙 기반 제어·행동 전환·학습 정책을 정리한다. RL은 지정한 7편의 Reward Formulation과 접촉·촉각 보상 조건을 정리하며, 별도의 정책 학습 개요는 두지 않는다. Method의 보상은 목표 도달을 주항으로 하는 설계 초안이며, 세부 수식·가중치는 실험을 통해 구체화한다.

## 문서 이동과 이미지

기존 [Tactile Representation and Policy Design 경로](02_Tactile_Representation_and_Policy_Design.md)는 기존 문헌조사의 링크가 끊기지 않도록 이동 안내만 남긴다. 본문은 위 세 문서에서 관리하고 이 경로에 중복 작성하지 않는다.

「기존 Tactile 활용 방식과 우리의 선택」 이미지는 Motivation에 배치했다. 기존 MDP 개요도는 Method의 접힌 참고 자료로 보존했으며, 현재 차원·입출력은 Method 본문을 기준으로 한다. 이미지 원본은 변경하지 않았다.
