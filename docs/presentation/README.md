# 발표 문서 안내

[연구 문서 안내](../README.md) · [결정·미정 목록](../03_DECISIONS_AND_OPEN_QUESTIONS.md)

발표 자료를 논문의 Motivation·Related Works·Method 역할에 맞춰 다음 세 문서로 나눈다.

| 문서 | 다루는 내용 |
| --- | --- |
| [01. Research Motivation and Contributions](01_Research_Motivation.md) | 문제의식, Binary Tactile–Wrench 역할 분담, 제안하는 Contribution |
| [02. Related Works](02_Related_Works.md) | F/T·Wrench 선행연구, Tactile 선행연구, RL Reward Formulation, 항목별 DR 비교 |
| [03. Method](03_Method.md) | MoveIt 접근 Process, MDP 하위의 Event·Observation·Action·Reward, DR·센서 불확실성 |

## 현재 작업 범위

Method는 360도 Sweep Command, MoveIt 접근 후 초기화, Observation 57차원과 Action 8차원, Manipulator OSC와 Hand Joint Position Controller를 현재 설계로 정리한다. 관측에는 **직전 Action 8차원**을 포함하지만, Observation Stack·Sliding Window·이력 기반 물성 적응은 추가하지 않는다. 선행연구가 실제로 사용한 이력에 대한 설명과 기존 문헌조사 자료는 보존한다.

Related Works의 F/T·Wrench 절은 지정한 6편의 규칙 기반 제어·행동 전환·학습 정책을 정리한다. RL은 지정한 7편의 Reward Formulation과 접촉·촉각 보상 조건을 정리하며, 별도의 정책 학습 개요는 두지 않는다. Method의 보상은 목표 도달을 주항으로 하는 설계 초안이며, 세부 수식·가중치는 실험을 통해 구체화한다.

## 문서 이동과 이미지

기존 [Tactile Representation and Policy Design 경로](02_Tactile_Representation_and_Policy_Design.md)는 기존 문헌조사의 링크가 끊기지 않도록 이동 안내만 남긴다. 본문은 위 세 문서에서 관리하고 이 경로에 중복 작성하지 않는다.

「기존 Tactile 활용 방식과 우리의 선택」 이미지는 Motivation에 배치했다. 기존 MDP 개요도는 Method의 접힌 참고 자료로 보존했으며, 현재 차원·입출력은 Method 본문을 기준으로 한다. 이미지 원본은 변경하지 않았다.
