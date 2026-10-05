# Task Definition and Overall Framework

[발표 문서 안내](README.md) · [전체 개요](00_Presentation_Overview_and_Design_Status.md) · [연구 동기와 선행연구](01_Research_Motivation_and_Related_Works.md) · [접촉 표현과 정책](03_Contact_Representation_and_Policy.md)

**기준일: 2026-10-05. 근거: `중간발표_최종.pdf`의 실제 PDF 14–16쪽 / 전체 34쪽.** 실제 PDF 15–16쪽의 슬라이드 인쇄 번호는 각각 16–17이다. 아래 쪽수는 인쇄 번호가 아닌 PDF 순서다.

> **문서 상태:** 최종 발표의 과업 범위, 상위–하위 역할과 학습·실행의 정보 흐름을 설명한다. 57D Observation, 8D Action, 센서 대응 및 PPO 학습은 설계 명세이며 구현과 실물 전이의 완료 보고가 아니다. 수치 범위, 접근 허용 오차와 실제 종료 판단 등 최종 PDF에 없는 사항은 미정으로 남긴다.

## 1. 과업: 지정된 방향과 거리로 물체를 밀기

본 연구의 하위 정책은 **초기 물체 Position과 이동 방향·거리 명령을 받아, Binary Tactile과 손목 F/T 피드백으로 대상 물체를 이동시키는 Sweeping**을 수행한다. 대상은 이번 Sweep으로 밀 물체이며, 상위 탐색 시스템이 궁극적으로 찾으려는 물체와는 구분한다. 초기 대상 선택, 목표 판단과 물체 근처까지의 접근을 모두 강화학습 정책에 맡기는 문제로 확장하지 않는다. [PDF 14–16쪽]

시각은 처음 대상 위치를 정할 때 사용한다. 실제 정책 실행 중에는 대상의 현재 Position·Orientation을 시각으로 계속 갱신하지 않는다. 대신 로봇·Hand 상태와 접촉 관측을 받아 다음 행동을 결정한다. 따라서 “Blind”는 로봇 자신의 상태나 초기 대상 정보를 모르거나, 조작 시작부터 아무 정보도 없는 상황을 뜻하지 않는다.

목표는 대상 물체의 이동이다. Hand의 이동량은 정책의 행동 결과와 접촉 상태를 해석하는 데 쓰이지만, 물체 이동을 대신하는 성공 기준이 아니다. 성공의 위치 오차와 종료 조건은 [성공과 종료](05_Success_and_Termination.md)에서 별도로 설명한다.

### 1.1. 명령과 위치 목표의 관계

최종 PDF의 명령은 초기 물체 Position 3차원과 방향·거리 2개 값으로 이루어진다. 방향은 선반 작업 평면의 방향각, 거리는 해당 방향으로 이동할 길이로 해석한다. 아래는 이 관계를 설명하는 기하학적 표기이며, 최종 PDF에 없는 좌표 변환 구현을 추가 확정한 식은 아니다.

```math
\mathbf{g}=[\widehat{\mathbf{p}}_0,d,\theta]\in\mathbb{R}^{5},\qquad
\widehat{\mathbf{s}}(\theta)=\cos\theta\,\mathbf{e}_1+\sin\theta\,\mathbf{e}_2,\qquad
\mathbf{p}_g=\widehat{\mathbf{p}}_0+d\,\widehat{\mathbf{s}}(\theta).
```

여기서 $\widehat{\mathbf{p}}_0$는 최초 시각으로 얻은 물체 위치, $d$는 명령 거리, $\theta$는 명령 방향이다. $\mathbf{e}_1,\mathbf{e}_2$는 선반 작업 평면의 두 기준축이며, $\widehat{\mathbf{s}}$는 단위 이동 방향을 뜻한다. 처음 관측한 위치에는 Noise가 포함될 수 있다. [PDF 15–16쪽]

**좌표계의 축, 각도의 기준·단위·정규화, 명령 거리의 유효 범위는 최종 PDF에 수치로 명시되지 않는다.** 또한 보상·평가의 목표 위치를 Noise가 있는 초기 추정값으로 정의할지, 시뮬레이션 초기 정답에서 정의할지는 구체 구현에서 명확히 해야 한다. 초기 인식 오차가 존재하는 Actor와 목표 오차의 의미를 일치시키기 위해 필요한 구분이며, 이번 문서에서 임의로 한쪽을 확정하지 않는다.

## 2. 문제를 성립시키는 가정

최종 PDF의 Problem Definition은 다음 세 가정을 명시한다. 이 가정은 시각 부족에 따른 접촉 조작을 따로 검증하기 위한 조건이다. [PDF 16쪽]

| 가정 | 뜻 | 이 가정으로 보장하지 않는 것 |
| --- | --- | --- |
| 최초 Object Position 관측 가능 | Noise가 포함된 초기 위치를 상위 계층 또는 인간에게서 받음 | 초기 GT Position·Orientation·Shape·Size를 모두 정확히 안다는 보장 |
| Goal Command는 외부에서 결정 | Human Operator 또는 High-Level Task Planner가 방향·거리를 선택 | 하위 정책이 전체 탐색 목표나 작업 순서를 계획한다는 주장 |
| 다른 물체의 간섭 없음 | 상위 계획이 명령 Sweep의 실행 가능성을 판단하고 간섭 없는 조건을 제공 | 접촉점·마찰·하중이 일정하거나, 선반 접촉·전도가 생기지 않는다는 보장 |

환경에는 물체가 무작위로 배치될 수 있지만, **명령된 Sweeping이 가능한 범위의 배치**라는 제한이 있다. 무작위 배치와 무제약 Clutter 조작은 같은 문제가 아니다. 주변 물체가 있더라도 이번 실험의 Sweep 구간에서 다른 물체의 간섭을 허용하는 정책으로 자동 확장하지 않는다.

이 조건 아래에서도 불확실성은 남는다. 초기 위치가 조금 다르면 Hand가 예상한 부위에 접촉하지 않을 수 있다. 물체의 질량·마찰·형상에 따라 동일한 행동의 이동 결과가 달라질 수 있으며, 촉각 활성 패턴과 손목 하중도 변한다. 연구의 중심은 이 상호작용 변화에 제한된 관측으로 어떻게 대응하는지다.

상위가 물체 근처까지 접근시켜 준다는 사실도 정확한 센서 부위 접촉을 보장하지 않는다. 실제 접촉과 센서가 감지한 접촉, 정상 무접촉과 신호 누락을 구분해야 한다. 센서 표현의 구체적 가정은 [접촉 표현과 정책](03_Contact_Representation_and_Policy.md)에 정리한다.

## 3. 전체 시스템에서의 상위–하위 역할

PDF 14쪽은 RGB-D 카메라, 로봇 상태, Object Pose Estimator, VLM 기반 High-Level Task Planner와 Low-Level Action Policy의 관계를 보여 준다. 상위에는 Success Detector, Interruption Handler, Policy Selector, 접근용 Fine-Tuned VLA Model도 그려져 있다. 이는 접촉 정책이 더 큰 작업 시스템에서 호출될 위치를 설명하는 구성이다. **각 상위 모듈의 구현·검증이 본 발표에서 완료되었다는 의미는 아니다.**

| 계층·단계 | 받는 정보 | 책임 | 이번 연구에서의 위치 |
| --- | --- | --- | --- |
| 초기 인식 | RGB-D 영상, 로봇 상태 | 이번에 밀 대상의 초기 위치와 장면 조건 파악 | 초기 입력을 제공하는 외부 단계 |
| 상위 판단 | 초기 장면과 작업 목적 | 대상·방향·거리 선택, 실행 가능성 판단, 정책 선택 | 하위 정책의 호출 조건을 제공 |
| 접근 | 초기 물체 위치, 명령 방향, 로봇 도달 조건 | Sweep 시작에 적합한 Hand 위치·자세로 이동 | 최종 PDF의 실행 Pipeline은 MoveIt 사용 |
| Sweeping 정책 | 고유감각, Binary Tactile, Wrench, 초기 명령, 직전 Action | 접촉 변화에 따라 Arm·Hand 행동을 반복 결정 | 연구의 직접 대상 |
| 종료·결과 처리 | 성공·실패·시간 제한의 판정 | Episode 종료 및 상위로의 결과 전달 | 시뮬레이션 판정과 실제 Blind 종료를 구분해 설계 |

PDF 14쪽의 접근용 VLA 박스와 PDF 15쪽의 MoveIt Pre-Contact Process를 동일한 구현 경로로 합치지 않는다. **최종 발표에서 Sweeping 진입 절차를 구체적으로 설명한 것은 MoveIt 접근이며, VLA는 상위 시스템의 접근 모듈 구성으로 나타난다.** 두 경로를 전환하는 규칙, VLA 미세조정 데이터나 접근 정책 학습 결과는 제시되지 않았다.

## 4. 접근 완료 후 정책이 시작하는 조건

최종 PDF 15쪽의 실제 실행 Pipeline은 Environment → 초기 Observation → MoveIt Pre-Contact Process → RL Policy → Action & Control 순서다. 접근 단계는 초기 물체 위치에서 명령 방향의 반대쪽으로 Offset을 둔 위치에 Hand를 배치하고, Hand Normal을 Sweep 방향과 평행하게 정렬한다.

이 배치는 Hand가 처음부터 목표 반대편에서 물체를 밀기 위한 조건이다. 다만 계획된 위치·자세가 실제 접촉 상태와 정확히 같지는 않으므로, 정책은 접근 결과에서 시작해 촉각·F/T 변화로 이후 행동을 조절해야 한다. 접근 자체를 학습 Episode에 모두 포함해야 한다는 의미는 아니다.

| 시작 조건 | 최종 PDF에서 제시한 내용 | 남은 세부 사항 |
| --- | --- | --- |
| Hand 위치 | 대상 초기 위치에서 Sweep 방향의 반대쪽으로 Offset | Offset 거리, 기준점, 허용 위치 오차 |
| Hand 자세 | Hand Normal과 Sweep 방향이 평행 | 손바닥·손등 선택 규칙, 자세 허용 오차 |
| 도달 가능성 | 접근 도식에 Dead Zone 표시 | 기준축·각도 구간과 실제 도달 판정 |
| 정책 진입 | MoveIt의 Pre-Contact Process 뒤 RL 수행 | 진입 시 접촉 유무, 센서 유효성, 시작 시점 판정 |
| 시뮬레이션 초기 상태 | 접근 후 상태를 바탕으로 Joint Configuration 등을 변화시킴 | 실제 접근 오차를 반영하는 분포와 유효 Reset 검사 |

[1st draft Method](1st_draft/03_Method.md)는 방향을 선반 평면의 360도로 두고, 접근 자세의 12시·6시 부근 Dead Zone을 별도로 설명한다. 최종 PDF 15쪽도 Dead Zone을 표시하지만 해당 구간의 수치와 기준축을 다시 명시하지 않는다. **360도 명령 방향과 접근 자세의 도달 제한은 서로 다른 조건**이라는 설명은 유지하고, 과거 각도값을 이번 PDF에서 재확정된 수치로 승격하지 않는다.

## 5. 학습 Pipeline: 정답을 이용해 행동의 결과를 평가

시뮬레이션 학습은 환경과 센서를 구성하고, 제한된 Observation으로 행동을 결정한 뒤, 시뮬레이션 정답으로 행동 결과에 Reward를 부여하는 흐름이다. 최종 발표는 Isaac Lab, RSL-RL/PPO와 Domain Randomization을 학습 구성으로 제시한다. [PDF 15쪽]

1. **유효한 초기 환경을 구성한다.** 물체와 로봇·Hand가 접근 완료 후의 Sweep을 시작할 수 있도록 초기화한다. 환경 마찰, 물체 크기·형상·질량·Pose, Robot Joint Configuration·Gain, Hand Joint Configuration 등을 변화시키는 설계를 둔다.
2. **실물과 대응하는 접촉 관측을 생성한다.** 시뮬레이션 Contact Sensor를 Binary 촉각 표현으로 변환하고, 손목 측정 위치의 Reaction Wrench를 F/T 표현으로 사용한다. 이상적인 모든 접촉 정답을 Actor의 tactile 값으로 대체하지 않는다.
3. **Actor Observation을 조립한다.** Robot·Hand 상태, 센서, 초기 Goal Command와 직전 Action을 결합한다. 현재 물체 GT Pose는 이 벡터에 계속 넣지 않는다.
4. **정책 Action을 제어기에 전달한다.** Arm Cartesian 증분과 Hand의 두 제어 축을 각각 OSC와 Joint Controller로 실행한다.
5. **환경 변화로 Reward와 종료를 계산한다.** 현재 대상 물체의 GT Pose, 접촉력 등으로 목표 이동과 접촉 행동을 평가한다. 그 결과는 PPO 학습과 Episode 관리에 사용한다.
6. **다음 관측으로 반복한다.** 정책의 행동으로 물체·접촉·로봇 상태가 변하고, 다음 접촉 관측이 다음 행동으로 연결된다.

PDF가 이 구성을 MDP Formulation으로 부르더라도 Actor에 물체의 전체 상태가 관측되는 것은 아니다. 물리 시뮬레이션에는 완전한 상태가 존재하지만 정책은 그 일부만 입력받는다. 따라서 MDP라는 제목만으로 물체 위치의 관측 가능성이나 충분한 상태 추정을 보장하지 않는다. 별도의 Belief State, RNN 또는 Observation Stack은 최종 PDF에서 확정되어 있지 않다.

### 5.1. 57D Observation과 8D Action의 역할

| 구분 | 구성 | 차원 | 정보 역할 |
| --- | --- | ---: | --- |
| Proprioception | Manipulator 관절 위치·속도 각 6, Hand/EEF Pose 6, Hand 저차원 관절 상태 2 | 20 | 현재 로봇과 Hand의 상태 |
| Contact Sensors | Tactile 18, 손목 Wrench 6 | 24 | 접촉 영역과 전체 힘·모멘트 |
| Goal Condition | 초기 대상 Position 3, 방향·거리 2 | 5 | 이번 Episode에서 달성해야 할 이동 |
| Last Action | 직전 Arm 6, Hand 2 | 8 | 바로 이전에 내린 정책 명령 |
| **Actor 합계** | 위 네 그룹의 결합 | **57** | 현재 물체 GT Pose를 제외한 실행 입력 |
| Arm Action | Cartesian 병진·회전 증분 | 6 | OSC가 실행할 운동 보정 |
| Hand Action | 공통 굽힘·엄지 제어 | 2 | Joint Controller가 실행할 Hand 명령 |
| **Action 합계** | Arm + Hand | **8** | 정책의 한 번의 행동 출력 |

이 표는 PDF 15쪽의 전체 흐름을 설명하기 위한 요약이다. 촉각 Header, 좌표계, 정규화, Joint 매핑과 센서 보정의 자세한 설명은 [접촉 표현과 정책](03_Contact_Representation_and_Policy.md)에 둔다. EEF Twist나 초기 Object Shape·Size를 추가하면 발표의 57D 명세가 바뀌므로, 이번 문서에서는 해당 입력을 자동 추가하지 않는다.

### 5.2. 학습 정답과 실행 입력의 경계

| 정보 | Actor 실행 입력 | 학습·평가에서의 사용 | 확인해야 할 경계 |
| --- | --- | --- | --- |
| 초기 물체 Position | 포함, Noise 허용 | Goal과 초기 조건 구성 | 최초 관측값이 현재 물체 상태로 갱신되지 않음 |
| 로봇·Hand 상태 | 포함 | 제어·정규화·평가 | 실물에서 얻을 수 있는 값과 표현을 대응 |
| Binary Tactile·Wrench | 포함 | 접촉 반응 및 센서 관련 분석 | 실물 측정량과 시뮬레이션 정답을 구분 |
| 현재 대상 GT Pose | 제외 | 위치 보상·전도·성공 평가 | `Privileged Information`이 Actor로 누출되지 않음 |
| 대상 접촉력 정답 | Actor에 그대로 추가하지 않음 | 접촉 방향 보상 등의 계산 | 학습용 대상 접촉력과 손목 합성 Wrench를 구분 |
| 현재 주변 물체 GT·Contact ID | 명세에 없음 | 필요시 환경 유효성·평가 확인 | Actor 입력으로 편의상 추가하지 않음 |

PDF 15쪽은 Privileged Information을 Target Object Pose 6D와 Contact Force 3D로 표시한다. 이는 Reward·평가를 계산할 때 사용할 정답의 범주이며, 57D Actor Observation에 추가하는 성분이 아니다. Critic에 어떤 특권정보를 제공하는지와 정확한 Actor–Critic Network 구조는 이 프레임워크 그림만으로 확정되지 않는다.

## 6. 실물 실행 Pipeline: 동일한 의미의 관측으로 배포

최종 PDF는 시뮬레이션에서 학습한 정책의 **Zero-Shot Deploy**를 목표로 제시한다. 이것은 학습 후 실물에서 정책을 추가 학습하지 않고 실행하려는 방향이며, 실물 전이가 완료되었다는 성과 표현은 아니다. [PDF 15쪽]

실행 과정에서는 먼저 초기 물체 위치와 명령 방향·거리를 얻고, MoveIt으로 Sweep 시작 위치에 접근한다. 그 뒤 로봇·Hand 상태와 실제 Tactile·F/T 값을 같은 의미의 Observation으로 구성해 정책에 제공한다. 정책은 Arm 6D와 Hand 2D를 출력하고, 제어기가 이를 실제 운동으로 변환한다. 접촉 관측이 다음 행동을 바꾸면서 Sweep이 이어진다.

실물에는 시뮬레이션의 현재 물체 GT와 대상 접촉력 정답이 자동으로 주어지지 않는다. 학습용 Reward를 계산할 수 있었다는 사실만으로 실물에서 성공·전도·종료를 같은 방법으로 판정할 수 있는 것은 아니다. **현재 물체 위치를 Actor에 계속 제공하지 않는 실행 조건과, 성공을 외부에서 측정하는 평가 조건은 별도로 정해야 한다.** 실제 종료의 남은 설계는 [성공과 종료](05_Success_and_Termination.md)에 연결한다.

접촉 표현과 명령 차원을 맞추는 것도 실물 동작을 보장하는 충분조건은 아니다. 촉각 영역 대응·임계값, F/T 영점과 중력·부하 보정, 좌표계, 시간 지연과 제어 경로를 확인해야 한다. 이 문서는 그 대응이 필요하다는 정보 계약을 설명하며, 확인되지 않은 Gain·Action Scale·제어 주기를 새로 확정하지 않는다.

## 7. 기존 초안과의 관계 및 남은 결정

[1st draft Method](1st_draft/03_Method.md)는 초기 물체 Position·방향·거리, MoveIt 접근, 57D Observation, 8D Action과 Arm OSC·Hand Joint Controller를 이미 제시했다. 최종 PDF는 이를 상위 시스템, 시뮬레이션 학습과 실물 Pipeline으로 확장해 설명한다. 과거 초안의 접근·상대 좌표 표현은 상세 참고자료로 사용할 수 있지만, PDF에 재명시되지 않은 수치를 최종 확정 사양으로 취급하지 않는다.

9월 30일 설명본은 같은 입력·출력과 센서 역할을 한 문서에 정리했다. 현재 문서는 과업과 정보 흐름을 독립 문서로 분리하며, 센서·보상·종료·평가의 상세 내용은 각각의 문서로 연결한다. 최종 PDF의 상위 VLA 도식이나 Domain Randomization을 이유로 본 연구 범위를 접근 정책 학습·전체 탐색·간섭 회피까지 확대하지 않는다.

| 미정 항목 | 필요한 결정 또는 확인 |
| --- | --- |
| 명령 기준 | 방향각의 기준축·단위, 작업 평면, 유효 거리·방향 범위 |
| Goal 계산 | Noise가 있는 초기 추정과 학습·평가 목표의 관계 |
| 접근 계약 | Offset, EEF 기준점, 위치·자세 허용 오차와 Dead Zone 기준 |
| 정책 진입 | 접근 완료 판정, 초기 접촉 상태와 센서 유효성 처리 |
| Reset 분포 | 접근 후 상대 오차와 물체·로봇 초기 조건의 유효 범위 |
| 학습 구조 | Critic 입력, Network, 실제 PPO 설정과 학습 예산 |
| 실물 실행 | 센서·제어 대응, 현재 물체 GT 없이 사용할 종료 로직 |

이 항목들은 프레임워크가 성립하기 위한 구현·검증 과제다. 최종 발표는 시스템 설계와 평가 계획을 제시한 상태이며, 이번 문서화에서 해당 결정이나 실험 결과를 추가로 만들어 넣지 않는다.
