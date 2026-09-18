# Research Motivation 보강 — 물체 정보 제공 조건과 축약 촉각의 보완 구조

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](README.md) · [전체 논문](../papers/README.md) · [Research Motivation](../../presentation/01_Research_Motivation.md)

**조사·문서화 기준일: 2026-09-18.** Research Motivation 보강 계획 중 **2.1. 물체 정보의 제공 조건과 축약 촉각의 보완 구조**만 다룬다. 2.2의 F/T 단독 한계 조사와 Reward Formulation 설계는 포함하지 않는다.

Sider Scholar에서 검색한 후보와 기존 확보 문헌을 대상으로 정리한 **7편의 비교 결과**를 문서화했다. 직접적인 Pushing 연구 2편과, 촉각 표현·정보 보완 구조를 비교하기 위한 조작 연구 5편이다. 이 문서 등록 작업에서는 조사 대상을 추가하거나 논문 코드·실험을 재현하지 않았다. 아래 원문 링크와 기존 상세 노트를 유지하며, 미명시·미확인 사항은 확정 정보로 바꾸지 않는다.

**조사 결과, 보완 방식은 Pose·Shape 제공 하나로 수렴하지 않았다.** 초기 존재 범위, 고유감각·이력, 지속적인 시각 정보, 학습용 정답, 연속적인 접촉 특징을 서로 다르게 활용한다. **실행 중 제공되는 정보와 학습에만 사용하는 정보를 분리해야** 각 연구의 성립 조건을 정확히 설명할 수 있다. [T1][src-t1] · [T2][src-t2] · [T3][src-t3] · [T4][src-t4]

## 논문 바로가기와 기존 상세 노트

T1–T7은 **이 보고서 안에서만 사용하는 비교 식별자**다. 기존 R·B·USER-P 식별자와 정독 상태를 변경하지 않는다. 기존 상세 노트를 재사용하며, 비교표를 작성했다는 이유로 새 원문 정독 노트를 만들거나 정독 편수를 늘리지 않는다.

| ID | 논문 | 기존 상세 노트 |
| --- | --- | --- |
| [T1](#t1) | DexTouch: Learning to Seek and Manipulate Objects with Tactile Dexterity | [Lee et al., 2024](../papers/2024-lee-dextouch.md) |
| [T2](#t2) | Rotating without Seeing: Towards In-hand Dexterity through Touch | [Yin et al., 2023](../papers/2023-yin-rotating-without-seeing.md) |
| [T3](#t3) | General In-Hand Object Rotation with Vision and Touch — RotateIt | 상세 노트 미작성. 아래 비교표·원문 참조 |
| [T4](#t4) | AnyRotate: Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch | 상세 노트 미작성. 아래 비교표·원문 참조 |
| [T5](#t5) | Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing | [Yang et al., 2023](../papers/2023-yang-sim-to-real-tactile-pushing.md) |
| [T6](#t6) | Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning | [Su et al., 2024](../papers/2024-su-sim2real-tactile-manipulation.md) |
| [T7](#t7) | Pushing in the Dark: A Reactive Pushing Strategy for Mobile Robots Using Tactile Feedback | [Özdamar et al., 2024](../papers/2024-ozdamar-pushing-in-the-dark.md) |

<a id="classification"></a>

## 2.1.1. 분류 기준

아래에서 **Pose는 물체 자체의 위치·자세**, **Shape는 물체의 형상·치수·CAD 또는 시각적 형상 관측**을 뜻한다. 목표 Pose, 로봇의 Pose, 촉각으로 추정하는 *국소 접촉면 Pose*는 별도로 표시한다.

`Tracking / Initial / 미제공`은 실행 시의 정보 제공 조건이다. `미제공`은 **실행 정책에 해당 정보를 명시적으로 제공하지 않는다**는 의미다. 시뮬레이터에 물체 Mesh가 존재하거나, 물체를 특정 자세로 놓고 시작한다는 사실만으로 Shape·Initial Pose 제공으로 분류하지 않는다. 정확한 초기 Pose와 사전 존재 범위도 구분한다.

관측이 부족한 조건과 보완 방식을 논문별로 함께 확인한다. **촉각에 남는 정보 / 제외되는 정보 → 함께 제공한 입력 → 보완하려는 문제**의 연결을 보되, 추가 입력의 존재만으로 보완 목적이나 인과적 효과를 단정하지 않는다.

<a id="execution-inputs"></a>

## 2.1.2. 물체 정보 제공 조건 → 실행 중 보완 구조

| 연구·과업 | 촉각 표현과 남는 정보 | 물체 Pose | 물체 Shape | 미제공 정보를 보완하는 실행 입력·구조 |
| --- | --- | --- | --- | --- |
| **T1. DexTouch** — Lee et al., 2024<br>탐색·파지·문 열기·밸브 회전 | **16개 영역의 Binary 접촉**. 감지 영역은 남지만 연속적인 힘 크기는 제공하지 않음 | **미제공**.<br>정확한 초기 Pose 대신 **물체가 존재하는 범위**를 사전 제공 | **미제공**.<br>실행 입력에 물체별 CAD·치수 없음 | **존재 범위 + 관절 위치·속도 + 손바닥 Pose·속도 + 손끝 위치**. 사전 범위로 접근하고 실제 접촉으로 물체를 찾음. [원문][src-t1] · [상세 노트](../papers/2024-lee-dextouch.md) |
| **T2. Rotating without Seeing** — Yin et al., 2023<br>손안 물체 회전 | **16개 영역의 Binary 접촉**. 영역별 접촉 유무 유지 | **미제공** | **미제공** | **관절 위치 + 이전 관절 목표 + 현재·과거 총 4시점의 관측**. 순간 관측의 부족을 짧은 이력으로 보완하도록 구성. 물체를 손안에 놓고 시작함. [원문][src-t2] · [상세 노트](../papers/2023-yin-rotating-without-seeing.md) |
| **T3. General In-Hand Object Rotation with Vision and Touch〈RotateIt〉** — Qi et al., 2023<br>다축 손안 회전 | 접촉 위치를 **8개 구간으로 이산화하고 손가락 ID와 결합**. 세밀한 접촉 영상 대신 위치 범주 유지 | **명시적 Pose 수치는 미제공**.<br>단, 물체 Depth는 계속 관측 | **Tracking: 부분 Depth 형상**.<br>실행 시 완전한 CAD는 미제공 | **지속적인 물체 Depth + 이산 접촉 위치 + 관절 상태·행동 이력**을 Transformer에 제공하여 물체 상태·물성을 포함하는 잠재표현을 추정. **Blind 실행 조건은 아님.** [원문][src-t3] |
| **T4. AnyRotate** — Yang et al., 2024<br>다양한 손 방향에서 손안 회전 | **Binary 접촉 + 접촉 Pose + 접촉력 크기**. 영상은 축약하지만 **연속적인 접촉 위치·힘 크기는 유지** | **미제공** | **미제공** | **관절 상태·목표 + 손끝 위치·자세 + 이전 행동 + 30시점의 촉각·고유감각 이력**. TCN이 학습용 특권정보의 잠재표현을 추정함. [원문][src-t4] |
| **T5. Sim-to-Real Model-Based and Model-Free DRL for Tactile Pushing** — Yang et al., 2023<br>목표 지향적 밀기 | 촉각 영상에서 **접촉 깊이·각도를 추정하여 접촉면 Pose로 축약**. 단순 Binary가 아니라 조작에 필요한 국소 기하 특징을 유지 | **물체 전체 Pose는 미제공**.<br>**국소 접촉면 Pose는 계속 추정** | **미제공** | **PoseNet의 접촉면 추정 + 로봇 위치·자세 + 목표 정보**. 물체 중심을 알아내는 대신 **접촉면을 목표 쪽으로 제어하는 문제로 재정의**함. [원문][src-t5] · [상세 노트](../papers/2023-yang-sim-to-real-tactile-pushing.md) |
| **T6. Sim2Real Manipulation on Unknown Objects with Tactile-based RL** — Su et al., 2024<br>지지면을 이용한 Pivoting | **두 장의 64×64 Binary 촉각 이미지**. 영상의 공간적 접촉 패턴이 남으므로 **영역별 1비트 벡터와 다름** | **미제공**.<br>목표 상대각은 제공 | **미제공** | **촉각 이미지 + 관절 고유감각 + 목표각**. 파지 폭을 고정하고 병진·회전 자유도를 제한함. 제안 정책에 별도 물체 각도 추정기를 넣지는 않음. [원문][src-t6] · [상세 노트](../papers/2024-su-sim2real-tactile-manipulation.md) |
| **T7. Pushing in the Dark** — Özdamar et al., 2024<br>이동로봇의 반응형 밀기 | 정전용량 센서에 임계값을 적용하여 **대표 접촉 좌표와 점·선 접촉을 계산**. 연속적인 접촉력은 사용하지 않음 | **미제공** | **미제공** | **로봇 자기 위치·자세 + 목표 위치 + 접촉 좌표 + 재정렬 상태기계**. 접촉점이 로봇 가장자리로 이동하면 횡방향 운동으로 재정렬. **RL이 아닌 제어 기반 비교 사례.** [원문][src-t7] · [상세 노트](../papers/2024-ozdamar-pushing-in-the-dark.md) |

**분류에서 중요한 발견:** DexTouch의 사전 정보는 *정확한 초기 Pose*가 아니라 **존재 범위**다. 반대로 RotateIt은 *명시적인 Pose 수치*를 받지 않더라도 **실행 중 물체 Depth를 계속 받으므로**, 시각 관측이 없는 연구로 분류하면 안 된다. [T1][src-t1] · [T3][src-t3]

<a id="training-information"></a>

## 2.1.3. 실행에는 없지만 학습에는 제공되는 정보

**Critic의 정답 입력, Reward 계산용 정답, Teacher의 정답 입력은 서로 다른 역할**이므로 나누어 기록한다. 아래 Reward 열은 계산에 사용되는 정보의 출처를 분류한 것이며, 새로운 보상함수의 설계·비교를 수행한 것은 아니다.

| 연구 | Critic의 추가 정보 | Reward 계산에 사용하는 물체 정보 | 그 밖의 학습 전용 정보 |
| --- | --- | --- | --- |
| **T1. DexTouch** | **GT 물체 Pose·선/각속도·손과의 거리·물성·과업 상태**. Shape/CAD의 별도 입력은 명시되지 않음 | 물체 위치·높이·목표와의 거리, 문·손잡이·밸브의 각도 등 | 별도 Teacher–Student 구조가 아니라 **비대칭 Actor–Critic**. [원문][src-t1] |
| **T2. Rotating without Seeing** | **GT 물체 Pose·물성·각 링크의 접촉력**. 실행 Actor에는 제공하지 않음 | 물체 회전량·선속도·위치 및 물체–손 관계 | **비대칭 Actor–Critic**. 형상 복원 실험은 별도 분석이며, 복원 Shape를 조작 정책에 다시 넣는 구조가 아님. [원문][src-t2] |
| **T3. RotateIt** | **Teacher의 정책·Critic이 특징을 공유**하며, GT Pose·물성·Mesh 기반 Shape 표현을 사용 | GT 물체 각속도·선속도 등. 식의 `pose penalty`는 **물체가 아니라 손 관절 자세**에 대한 항 | **GT Mesh·Pose·물성의 잠재표현과 Teacher 행동**을 Student의 학습 목표로 사용. 실행에서는 센서 이력으로 이를 추정함. [원문][src-t3] |
| **T4. AnyRotate** | **Critic만의 독립적인 추가 입력 목록은 원문에서 명확히 분리되지 않음**. Teacher의 특권정보 사용은 확인됨 | GT 물체·목표 Pose의 keypoint 관계, 물체 회전·각속도, 접촉 상태 등 | Teacher에 **GT Pose·치수·질량·질량중심·중력·보조 목표** 제공. Student는 그 잠재표현과 행동을 학습함. [원문][src-t4] |
| **T5. Tactile Pushing** | Model-free는 **SAC**이며 추가 GT를 받는 비대칭 Critic은 명시되지 않음. Model-based **PETS–MPC에는 Critic이 없음** | **접촉면 위치·방향과 목표·Pusher의 관계**. 물체 중심의 전체 Pose를 필요로 하는 식과 구분해야 함 | 접촉면 Pose 추정용 관측 모델을 별도로 학습. 시뮬레이션에서는 접촉 정보를 얻고, 실물에서는 촉각 영상으로 추정. [원문][src-t5] |
| **T6. Su et al.** | **추가 GT Pose·Shape 없음**. Actor와 Critic이 같은 촉각·고유감각 특징 사용 | 물체의 현재·초기 목표 거리와 현재 상대각 등 **실행 관측에 없는 정답** 사용 | GT 각도를 받는 Oracle과 각도 추정기 방식은 **비교군**이며, 제안 Binary 정책의 입력이 아님. [원문][src-t6] |
| **T7. Pushing in the Dark** | 해당 없음 | 해당 없음 | 학습 기반 방법이 아님. 로봇 위치·목표·접촉 좌표를 사용하는 제어 규칙. [원문][src-t7] |

**Su et al.은 “Actor에 Pose가 없으면 Critic에는 반드시 있을 것”이라는 추정을 반박하는 사례**다. 반면 **Reward 계산에는 현재 물체 상태를 사용**한다. 따라서 `Privileged Information 사용 여부: O/X` 하나로 묶기보다 위처럼 구분해야 한다. [T6][src-t6]

<a id="compensation-evidence"></a>

## 2.1.4. 추가 정보가 실제로 무엇을 보완했는가?

아래의 **해석 범위**는 원문의 구성과 실험을 바탕으로 이번 Research Motivation에 적용할 수 있는 수준을 판단한 것이다. 단순히 입력이 존재한다는 사실과, 그 입력의 효과를 제거 실험으로 검증했다는 사실을 구분한다. 마지막 열은 **조사자의 해석**이며, 저자의 설명이나 프로젝트의 검증된 성과와 동일하지 않다.

| 연구 | 저자가 설명하거나 실험으로 확인한 보완 관계 | 이번 논리에 사용할 수 있는 범위 — 조사자의 해석 |
| --- | --- | --- |
| **T1. DexTouch** | **존재 범위로 접근 → 촉각으로 실제 물체 탐색**이라는 역할을 설명함. Critic의 특권정보를 제거한 `WO-PInfo`는 성능이 저하됨. — §V-B/E, Table II. [원문][src-t1] | **사전 범위 + 실행 촉각 + 학습용 정답**의 분업 근거. 다만 존재 범위 자체의 제거 효과와 **Binary 하중 정보 손실**을 직접 입증한 실험은 아님 |
| **T2. Rotating without Seeing** | 한 시점 관측이 충분하지 않을 수 있어 **과거 3시점을 추가**한다고 명시. 별도 형상 복원 실험에서도 촉각이 포함된 이력이 유용함을 확인. — §IV-A, §V-H. [원문][src-t2] | **Binary + 고유감각 + 이력**으로 물체 관련 정보를 간접적으로 활용하는 사례. 단, 이력 길이의 독립적인 제거 비교나 정책의 정확한 Shape 복원까지 입증한 것은 아님 |
| **T3. RotateIt** | Teacher에서 **Shape를 제거하면 성능 저하**. Student에서도 고유감각에 시각·촉각을 결합하면 성능이 개선됨. — Table 1, Fig. 6, §5.1–5.2. [원문][src-t3] | **형상 정보가 학습에 유용하며, 실행에서는 여러 센서로 그 표현을 추정한다**는 근거. “실행 정책에 CAD를 직접 제공한다”는 근거는 아님 |
| **T4. AnyRotate** | **접촉력 크기는 물성이 다른 물체**, **접촉 Pose는 미지 형상**을 다루는 데 유용하다고 분석. 둘 중 하나를 제외하면 성능 저하. — §5.2. [원문][src-t4] | 이번 조사에서 **촉각 축약으로 제외되는 접촉 정보의 필요성을 가장 직접적으로 검토한 사례**. 다만 사용한 힘 특징은 **국소 접촉력의 크기**이며, 손목 6축 Wrench의 효과를 검증한 것은 아님 |
| **T5. Tactile Pushing** | 물체 중심 정보를 얻기 어려워 **접촉면 제어로 문제를 재정의**했다고 명시. 접촉면 Pose 기반 정책이 촉각 이미지 기반 정책보다 일반화·안정성에서 유리한 결과를 보임. — §III-B, §V. [원문][src-t5] | **정보를 추가하는 대신, 필요한 정보가 줄어들도록 과업을 구성하는 방식**의 근거. 저차원화가 항상 불리하다는 주장에는 맞지 않음 |
| **T6. Su et al.** | Binary 영상·고유감각으로 외부 Pose 추정 없이 Pivoting 수행. 촉각 표현과 비촉각 비교군을 평가함. — §IV–V. [원문][src-t6] | **물체 Pose·Shape가 없어도 축약 촉각으로 수행 가능한 조건**의 사례. 공간 패턴이 남는 Binary 이미지이므로 **영역별 접촉 비트의 충분성을 그대로 뒷받침하지는 않음** |
| **T7. Pushing in the Dark** | 접촉 좌표의 변화에 따라 재정렬하는 제어가 비반응형 비교군보다 효과적임. 성공은 **접촉점–목표 거리**로 판정. — Algorithm 1, §III-B. [원문][src-t7] | **접촉 위치 + 로봇 위치 + 제어 구조**로 밀기가 가능한 사례. **물체 중심의 정확한 위치·자세 제어**나 손의 Sweeping 전체와 동일시하면 안 됨 |

<a id="limitations-future-work"></a>

### 원문이 밝힌 한계·향후 연구

아래는 저자들이 밝힌 한계와 향후 방향을 분리한 표다. 향후 계획을 구현·검증 완료로 읽지 않으며, 구체적인 방향이 명시되지 않은 항목은 그대로 남긴다.

| 연구 | 저자들이 밝힌 한계 | 저자들이 제시한 향후 방향 |
| --- | --- | --- |
| **T1. DexTouch** | 학습에서 경험하지 못한 무게·미끄러운 표면이 수행에 영향을 줌 | **3축 힘 등 더 다양한 촉각 정보** 및 일반화 확장. — §V-E, §VI. [원문][src-t1] |
| **T2. Rotating without Seeing** | 손가락 측면 접촉이 중요한 회전에서는 현재 센서 배치가 부족할 수 있음 | 더 조밀한 센서 배열과 다양한 과업. — §V-I, §VI. [원문][src-t2] |
| **T3. RotateIt** | 손의 기계적 범위·물체 크기 제약. 현재 촉각 입력은 센서의 전체 정보를 활용하지 않음 | 풍부한 촉각 처리, 시각 사전학습, 실물에서의 지속학습. — §6. [원문][src-t3] |
| **T4. AnyRotate** | 날카로운 모서리·꼭짓점이 있는 물체에서 어려움 | 더 풍부한 접촉 기하 표현 또는 시각적 Shape 정보. — §6. [원문][src-t4] |
| **T5. Tactile Pushing** | 고정된 전진 행동이 가까운 목표 도달과 접촉면 탐색을 제한 | 행동 제약 완화, 실물 학습 및 자동 Reset 문제 검토. — §V. [원문][src-t5] |
| **T6. Su et al.** | 불안정한 파지와 불완전·비정상 접촉으로 촉각 패턴이 충분하지 않은 실패 | 코드·훈련 환경 공개 계획. 별도의 구체적인 센싱 확장 방향은 명시하지 않음. — §V-C, §VI. [원문][src-t6] |
| **T7. Pushing in the Dark** | 원통의 구름과 접촉 형태 차이를 낮은 성공률의 가능한 원인으로 논의 | 별도의 구체적인 후속 연구 계획은 명시하지 않음. — §IV. [원문][src-t7] |

<a id="motivation-conclusion"></a>

## 2.1.5. Research Motivation에 반영할 결론 — 해석·제안

**“축약 촉각 연구들은 부족한 정보를 물체 Pose·Shape를 추가하여 해결한다”는 문장으로 일반화하기는 어렵다.** 이번에 확인한 연구들은 실행 시 해당 정보를 직접 받지 않고도 고유감각·이력으로 조작하거나, 정보 요구량이 낮은 제어 문제로 바꾸는 경우가 있었다. [T2][src-t2] · [T5][src-t5] · [T6][src-t6] · [T7][src-t7]

연구 동기 계획의 **(2) 영역별 Binary 촉각의 정보 한계 → (2-1) 부족한 정보를 무엇으로 보완하는가**는 다음처럼 보강하는 것이 근거에 맞다.

> **촉각을 축약하면 남는 정보와 제외되는 정보가 표현 방식에 따라 달라진다. 기존 연구들은 사전 정보, 고유감각·이력, 다른 센서 또는 학습용 정답을 활용하고, 경우에 따라 필요한 상태 정보가 적도록 과업을 재구성한다. 따라서 본 연구에서도 영역별 Binary 촉각이 제공하지 않는 정보 중, Sweeping에 실제로 필요한 정보가 무엇인지 확인해야 한다.**

**AnyRotate의 접촉 Pose·접촉력 제거 비교**가 ‘제외된 접촉 정보가 행동 성능에 중요할 수 있다’는 연결에 가장 직접적이다. **RotateIt의 Shape 제거 비교**는 형상 정보의 기여를, **DexTouch의 특권정보 제거 비교**는 제한된 실행 관측을 사용하는 정책의 학습 조건을 설명하는 데 적합하다. 세 근거는 각각 **접촉 정보·형상 정보·학습 정보**를 검증한 것이므로, 같은 종류의 보완으로 묶지 않는다. [T4][src-t4] · [T3][src-t3] · [T1][src-t1]

이 결론은 **문헌에 근거한 연구 동기 보강안**이며, 본 연구의 영역별 Binary 촉각과 손목 F/T 결합이 Sweeping에서 충분하다는 검증 결과는 아니다. F/T 단독 사용의 한계는 이번 보고서의 범위 밖인 2.2에서 별도로 조사한다.

## 원문과 근거 위치

아래 링크는 앞선 조사에서 제시한 공개 원문을 유지한다. 버전이 명시된 HTML과 버전이 지정되지 않은 PDF 링크를 구분하며, 링크 등록을 새로운 출판 상태 확인이나 원문 전체 재정독으로 취급하지 않는다.

<a id="t1"></a>

### T1. DexTouch

**Lee et al. (2024). DexTouch: Learning to Seek and Manipulate Objects with Tactile Dexterity.** [공개 원문 — arXiv:2401.12496v2][src-t1] · [기존 상세 노트](../papers/2024-lee-dextouch.md).

주요 근거: 정책 관측과 비대칭 Actor–Critic 설명, §V-B/E·Table II의 특권정보 제거 비교, §V-E·VI의 한계·향후 방향.

<a id="t2"></a>

### T2. Rotating without Seeing

**Yin et al. (2023). Rotating without Seeing: Towards In-hand Dexterity through Touch.** [공개 PDF — arXiv:2303.10880, 링크에 버전 미지정][src-t2] · [기존 상세 노트 — arXiv v4](../papers/2023-yin-rotating-without-seeing.md).

주요 근거: §IV-A의 Binary 접촉·관측 이력·비대칭 Critic, §V-H의 형상 복원 분석, §V-I·VI의 한계·향후 방향.

<a id="t3"></a>

### T3. RotateIt

**Qi et al. (2023). General In-Hand Object Rotation with Vision and Touch.** [공개 PDF — arXiv:2309.09979, 링크에 버전 미지정][src-t3]. 상세 노트 미작성.

주요 근거: Teacher–Student와 시각·이산 촉각 입력 설명, Table 1·Fig. 6·§5.1–5.2의 Shape·감각 입력 비교, §6의 한계·향후 방향.

<a id="t4"></a>

### T4. AnyRotate

**Yang et al. (2024). AnyRotate: Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch.** [공개 원문 — arXiv:2405.07391v3][src-t4]. 상세 노트 미작성.

주요 근거: 접촉 Pose·접촉력·이력 및 Teacher–Student 설명, §5.2의 접촉 정보 제거 비교, §6의 한계·향후 방향. Critic만의 독립 입력 목록은 미명시로 유지한다.

<a id="t5"></a>

### T5. Tactile Pushing

**Yang et al. (2023). Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing.** [공개 PDF — arXiv:2307.14272, 링크에 버전 미지정][src-t5] · [기존 상세 노트](../papers/2023-yang-sim-to-real-tactile-pushing.md).

주요 근거: §III-B의 접촉면 기반 문제 정의, 접촉 Pose 추정·SAC·PETS/MPC 설명, §V의 비교·한계·향후 방향.

<a id="t6"></a>

### T6. Sim2Real Tactile Manipulation

**Su et al. (2024). Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning.** [공개 원문 — arXiv:2403.12170v1][src-t6] · [기존 상세 노트 — arXiv v1](../papers/2024-su-sim2real-tactile-manipulation.md).

주요 근거: §III-B의 Binary 이미지, §IV–V의 관측·보상·비교군, §V-C·VI의 실패 사례·공개 계획.

<a id="t7"></a>

### T7. Pushing in the Dark

**Özdamar et al. (2024). Pushing in the Dark: A Reactive Pushing Strategy for Mobile Robots Using Tactile Feedback.** [공개 원문 — arXiv:2403.09305v1][src-t7] · [기존 상세 노트](../papers/2024-ozdamar-pushing-in-the-dark.md).

주요 근거: Algorithm 1·§III-B의 접촉 기반 제어와 성공 판정, §IV의 평가·실패 해석. RL 기반 비교 대상과 구분한다.

[src-t1]: https://arxiv.org/html/2401.12496v2
[src-t2]: https://arxiv.org/pdf/2303.10880
[src-t3]: https://arxiv.org/pdf/2309.09979
[src-t4]: https://arxiv.org/html/2405.07391v3
[src-t5]: https://arxiv.org/pdf/2307.14272
[src-t6]: https://arxiv.org/html/2403.12170v1
[src-t7]: https://arxiv.org/html/2403.09305v1
