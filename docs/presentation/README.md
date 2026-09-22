# 발표 문서 안내

[연구 문서 안내](../README.md) · [결정·미정 목록](../03_DECISIONS_AND_OPEN_QUESTIONS.md)

발표 자료를 논문의 Motivation·Related Works·Method 역할에 맞춰 다음 세 문서로 나눈다.

| 문서 | 다루는 내용 |
| --- | --- |
| [01. Research Motivation and Contributions](01_Research_Motivation.md) | 문제의식, Binary Tactile–Wrench 역할 분담, 제안하는 Contribution |
| [02. Related Works](02_Related_Works.md) | F/T·Wrench 선행연구, Tactile 선행연구, RL Reward Formulation, 항목별 DR 비교 |
| [03. Method](03_Method.md) | MDP 하위의 State/Observation·Action·Reward, 본 연구의 DR·센서 불확실성 설계 후보 |

## 현재 작업 범위

관측·행동 이력의 설계와 이력 기반 물성 적응은 현재 다루지 않는다. 기존 「Sweeping에서 중요하게 다뤄야 할 것은 무엇인가?」 절과 Method의 이력 입력 항목은 제외했다. 선행연구가 실제로 사용한 이력에 대한 설명과 기존 문헌조사 자료는 삭제하지 않으며, 본 연구의 현재 설계로 해석하지 않는다.

Related Works의 F/T·Wrench 절은 지정한 6편의 규칙 기반 제어·행동 전환·학습 정책을 정리한다. RL은 지정한 7편의 Reward Formulation과 접촉·촉각 보상 조건을 정리하며, 별도의 정책 학습 개요는 두지 않는다. Method의 보상식은 여전히 미정이며, 사용자가 설계를 구체화한 뒤 보강한다.

## 문서 이동과 이미지

기존 [Tactile Representation and Policy Design 경로](02_Tactile_Representation_and_Policy_Design.md)는 기존 문헌조사의 링크가 끊기지 않도록 이동 안내만 남긴다. 본문은 위 세 문서에서 관리하고 이 경로에 중복 작성하지 않는다.

「기존 Tactile 활용 방식과 우리의 선택」 이미지는 Motivation에 배치했다. 기존 MDP 개요도는 Method의 접힌 참고 자료로 보존했으며, 그림에 남아 있는 이력 입력은 현재 설계에서 제외한다. 이미지 원본은 변경하지 않았다.
