# 힘·촉각 기반 Sweeping: 선행연구 검토와 적용 방향

**교수 미팅 자료 · 2026.09.18**

[문헌 색인](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/README.md) · [논문 상세 정리](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/README.md)

논문명 링크는 상세 정리 문서로 연결한다. `(확인 필요)`는 상세 정리 문서가 없는 논문을 뜻한다.

**연구 주제:** 초기 시각 관측으로 대상과 목표를 지정한 뒤, 조작 중 시각 추적 없이 Force/Torque와 Tactile 피드백으로 물체를 목표 방향·거리만큼 이동시키는 Sweeping 정책.

현재까지 검토한 연구를 기준으로, **[DexTouch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-lee-dextouch.md)의 영역별 Binary 촉각 표현, SRL-VIC(확인 필요)의 Wrench 관측, Miller 등(확인 필요)의 접촉 이력 표현학습, [Bi-Touch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2023-lin-bi-touch.md)·High-quality Wiping(확인 필요)의 보상 구성**을 적용 후보로 검토한다. 각 연구의 접근과 적용 검토 이유는 다음과 같다.

## 1. Tactile — 영역별 Binary 표현 검토

### 선행연구에서는 어떻게 사용하는가?

| 접근 | 대표 연구 | 확인한 방법 |
| --- | --- | --- |
| **광학 촉각 영상 활용** | [Tactile Gym 2.0](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2022-lin-tactile-gym-2-0.md), 2022 · [Bi-Touch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2023-lin-bi-touch.md), 2023 · [Tactile Pushing (Yang et al., 2023)](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2023-yang-sim-to-real-tactile-pushing.md) | 촉각 영상을 학습 정책에 연결하거나, CNN으로 접촉 깊이·방향을 추정한다. 일부 영상 기반 경로에서는 GAN으로 실물 영상을 Simulation 표현에 맞춘다. |
| **분포형 힘의 영상 표현** | [Gentle Object Retraction](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2026-brouwer-gentle-object-retraction.md), 2026 | 분포형 3축 힘을 RGB 영상으로 변환해 ResNet-18로 인코딩하고, Diffusion Policy 기반 모방학습에 활용한다. 광학 촉각 영상과는 구분한다. |
| **영역별 Binary 접촉 활용** | [DexTouch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-lee-dextouch.md), 2024, [Rotating without Seeing](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2023-yin-rotating-without-seeing.md), 2023 | FSR 출력을 필터·Threshold로 처리하여 영역별 접촉 여부를 만들고, 고유감각과 함께 PPO에 입력한다. 후자는 관측 이력과 Binary/연속값의 실물 비교도 다룬다. |
| **힘·접촉 위치를 보존하는 표현** | Beyond Binary(확인 필요), 2026 | 촉각을 힘과 접촉 위치의 CoP 표현으로 정리한다. 삽입·균형 과업에서 Binary보다 풍부한 정보가 유리한 결과를 보고한다. |

검토한 연구에는 **영상 자체를 학습하는 방식과, 접촉에 필요한 물리 정보로 축약하는 방식이 함께 존재한다.** 센서가 제공하는 정보와 과업에 필요한 정보를 기준으로 표현을 선택하며, 축약한 저차원 입력에도 학습 Encoder를 사용할 수 있다.

### 적용 검토안과 근거

**검토안: [DexTouch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-lee-dextouch.md)를 참고해, 17개 Grid 영역을 각각 하나의 접촉 여부로 축약.** 전체 손을 하나의 bit로 합치지 않고 **17bit의 접촉 분포를 유지하는 구성**.

- **장비와의 대응:** 현재 계획한 Hand의 영역별 촉각을 활용할 수 있으며, 광학 촉각 영상 생성·변환을 전제로 하지 않는다.
- **F/T와의 역할 분담:** 촉각에서는 ‘어느 센서 영역이 닿았는가’를, 손목 Wrench에서는 ‘전체 하중이 얼마나·어느 방향으로 작용하는가’를 활용하는 역할 분담안.
- **전이의 단순화:** 정밀한 접촉력 크기를 맞추는 부담을 줄일 수 있다. 다만 영역 내부 위치·힘 크기를 버리므로, **같은 17개 영역의 연속 Scalar 표현과 비교**하여 충분성 확인 필요.

이 표현을 적용할 전제는 실제 미는 부위에 촉각 센서가 반응한다는 것이다. 비센서 부위 접촉과 약한 신호에서는 Binary가 0이어도 무접촉이라고 단정할 수 없다. [DexTouch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-lee-dextouch.md)의 Binary 성공과 Beyond Binary(확인 필요)의 반대 결과를 함께 고려하면, **Binary는 우선 검토 후보이며 최종적으로 가장 좋은 표현인지는 비교 대상**이다.

## 2. F/T — 6축 관측과 방향·크기 활용 검토

### 선행연구에서는 어떻게 사용하는가?

| 연구 | F/T 활용 | 참고할 점 |
| --- | --- | --- |
| [Force Push](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-heins-force-push.md), 2024, §IV | 힘 **방향**으로 미는 방향을 보정하고, **크기**로 접촉 손실·회복과 과부하 대응을 수행하는 비학습 제어 | Force를 단순한 충돌 감지값이 아니라 연속적인 조작 Feedback으로 사용한다. |
| SRL-VIC(확인 필요), 2024, §III-B | EEF 위치와 **6D Wrench**를 정책에 입력하고 이동·Stiffness를 선택한다. Wrench는 위험 평가·회복 정책에도 사용한다. | 6축 관측이 행동 조정으로 연결되는 RL 사례다. 과업은 자유 물체 Sweep이 아닌 Maze 통과다. |
| CHEQ-ing the Box(확인 필요), 2025, §4.2 | **Force 3D**를 관측에 넣고 Motion·Stiffness·Damping을 학습한다. 목표 힘 오차와 한계 초과를 보상·종료에도 반영한다. | 힘의 활용이 관측 추가뿐 아니라 순응성 제어와 보상 설계로 이어진다. 과업은 Polishing이다. |

### 적용 검토안과 근거

**검토안: SRL-VIC(확인 필요)의 6축 Wrench 관측과 [Force Push](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-heins-force-push.md)의 방향·크기 활용을 참고.** 영점·장착 하중·좌표계를 정리한 연속값을 정책에 제공하는 구성.

촉각이 접촉 영역을 알려 주더라도 저항의 크기는 알기 어렵다. 반대로 손목 Wrench만으로는 같은 하중이 어느 부위의 접촉에서 발생했는지 모호할 수 있다. **두 센서가 제공하는 정보의 차이를 조작에 활용하는 것이 결합의 이유**다.

보상에서는 진행·횡방향·선반 법선 성분을 구분해 분석하고, **과도한 힘·모멘트 억제**에 연결하는 안을 검토한다. 물체를 밀기 위해 필요한 힘까지 줄이거나, 손목 Torque를 물체 회전 오차로 취급하지 않는다. Stiffness Action의 추가는 센서 결합 효과를 확인한 뒤 검토할 항목이다.

**F/T 관련 추가 조사는 필요하다.** 현재 RL 근거는 Maze·Polishing·Wiping에 치우쳐 있다. 자유 물체 Pushing에서 **Wrench로 접촉 손실·미끄러짐·물체 진행을 어떻게 판단하는지**, 그리고 **미지 질량·마찰에 어떻게 적응하는지**를 우선 보완해야 한다.

## 3. RL 결합 — 접촉 이력과 동역학 보조학습 검토

### 선행연구에서는 어떻게 학습에 반영하는가?

| 연구 | RL에 연결하는 방법 | 이번 연구와의 연결 |
| --- | --- | --- |
| **[DexTouch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-lee-dextouch.md)** | Binary Tactile과 로봇 상태를 MLP 기반 PPO에 입력 | 센서 결합 정책의 기본 비교 기준 |
| **[Rotating without Seeing](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2023-yin-rotating-without-seeing.md)** | 현재·과거의 접촉, 관절 상태, 이전 관절 목표를 함께 입력 | 순간 접촉값이 담지 못하는 시간적 변화를 활용 |
| **Enhancing Tactile-based Reinforcement Learning for Robotic Control**, Miller et al., 2025 (확인 필요), §3·§5 | 촉각·고유감각·행동 이력을 Encoder로 표현하고, **촉각 재구성 또는 행동 조건부 Forward Dynamics 보조학습**을 PPO와 함께 수행 | 센서를 관측에 추가하는 데서 나아가, 접촉 정보를 표현에 보존하고 제어에 활용하도록 학습 목적을 설계 |

Miller 등(확인 필요)의 연구에서는 Binary 촉각을 추가했을 때의 이득이 과업에 따라 달랐으며, 재구성·동역학 보조학습이 RL-only보다 유리한 결과를 보였다. 다만 **실물 검증은 수행하지 않았다**. (§5–7)

### 적용 검토안과 근거

**검토안: Miller 등(확인 필요)의 ‘관측·행동 이력 Encoder + Forward Dynamics 보조학습’ 적용.**

촉각과 Wrench의 최근 이력, 로봇 상태, 행동을 함께 표현하고, **행동 이후의 접촉 상태 변화를 예측하는 데 유용한 잠재표현**을 학습하여 Sweeping 정책에 입력하는 구성을 검토한다. 원논문의 예측 대상은 잠재표현이며, 여기에 손목 Wrench를 포함하는 것은 우리 과업에서 검토할 확장이다.

이 방법을 검토하는 이유는 **같은 순간 힘이라도 최근에 어떻게 움직였고 어느 접촉 영역이 변했는지에 따라 필요한 행동이 달라질 수 있기 때문**이다. 예를 들어 하중 증가와 함께 접촉 영역이 이동하는 경우, 하중만 증가하고 접촉 분포는 유지되는 경우를 구분할 단서가 이력에 있다. 이것이 곧 마찰·충돌 원인의 완전한 식별을 뜻하지는 않는다.

효과 확인 방법은 **동일한 센서·이력·Encoder를 사용하는 PPO에서 보조학습의 유무를 비교**하는 안이다. 이를 통해 ‘이력을 더 넣어서 좋아진 것’과 ‘같은 정보를 더 유용하게 학습한 것’을 구분한다.

**연구에서 확인할 핵심:** 제한된 촉각과 Wrench의 시간적 관계를 학습하면, 접촉 위치 변화·접촉 손실 상황에서 단순 결합 정책보다 실제 물체 이동을 개선할 수 있는가?

## 4. Reward — 물체 진행 중심의 보상 구성 검토

### 선행연구에서는 어떻게 구성하는가?

[DexTouch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-lee-dextouch.md)는 식(1–4), [Yang의 Tactile Pushing](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2023-yang-sim-to-real-tactile-pushing.md)은 식(4), [Bi-Touch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2023-lin-bi-touch.md)는 식(1–4), CHEQ(확인 필요)는 본문·부록에 보상 항을 공개한다. 이들에서 **과업 진행과 조작 품질을 구분하는 구성**을 참고할 수 있다.

| 연구 | 보상의 구성·설계 원리 | 적용 후보 |
| --- | --- | --- |
| **[DexTouch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-lee-dextouch.md) / [Yang의 Tactile Pushing](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2023-yang-sim-to-real-tactile-pushing.md)** | 과업 진행 또는 목표 방향·거리 관련 항을 사용 | **물체의 목표 이동**을 주목표로 설정 |
| **[Bi-Touch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2023-lin-bi-touch.md)**, §III-C | 목표 위치·방향과 접촉 정렬·유지 관련 항을 구분 | **목표 달성과 미는 자세·접촉의 품질을 분리**하여 보상 |
| **High-quality Wiping(확인 필요)**, 2025, §III | 접촉·힘 보상을 매 시점 지급할 때 생기는 정체 문제를 다루고, 새로운 Checkpoint에 도달할 때 제한적으로 지급 | **접촉 유지 보상이 실제 진행을 대체하지 않도록 지급 조건을 설계** |

### 적용 검토안과 근거

**검토안: [Bi-Touch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2023-lin-bi-touch.md)의 목표·접촉 보조항 구분과 High-quality Wiping(확인 필요)의 진행 연계 원리를 참고.** Sweeping에 적용할 보상 후보는 다음과 같다.

| 역할 | 우리 과업의 보상 후보 | 이유 |
| --- | --- | --- |
| **Main Reward** | 대상 물체의 목표 오차 감소·목표 도달 | Hand가 아니라 물체가 지정한 위치로 이동하는 것이 과업의 목적 |
| **정렬·경로 보조** | 미는 EEF 자세와 목표 경로의 과도한 이탈 억제 | 접촉이 유지되는 자세를 유도하면서 필요한 보정 운동은 허용 |
| **하중 제한** | 허용 범위를 넘는 힘·모멘트에 Penalty | 물체 진행을 위해 필요한 하중을 허용하면서 과도한 밀기를 억제 |
| **접촉 보조** | 필요할 경우 새로운 물체 진행 구간과 연결해 접촉 품질 보상 | 접촉만 유지하며 멈춰 있는 정책을 방지 |

정렬·경로는 EEF와 물체를 구분한다. **[Force Push](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-heins-force-push.md)의 경로 보정은 푸셔 기준점의 오차를 이용하며, 물체 중심을 추적하는 방식이 아니다.** 우리 학습에서 물체 중심 경로를 보상한다면 Simulation 정답으로 계산하는 별도 설계다. 이 정답은 Reward·평가에만 사용하고 실행 정책에는 넣지 않는다.

Clutter 충돌 회피보다 **기본 Sweeping의 진행·접촉·하중 조절을 우선 검토**한다. 상위 판단기가 조작 가능한 시작 조건을 제공한다는 전제다. 이는 전체 경로의 무충돌을 보장한다는 뜻은 아니다.

## 5. 적용 후보와 검토할 질문

| 항목 | 적용 후보 | 우리 연구에서 검토할 질문 |
| --- | --- | --- |
| **촉각 표현** | [DexTouch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-lee-dextouch.md)의 영역별 Binary | 17개 영역의 접촉 분포만으로 충분한가? Scalar를 보존해야 하는 조건은 무엇인가? |
| **F/T 활용** | SRL-VIC(확인 필요)의 Wrench6 + [Force Push](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2024-heins-force-push.md)의 방향·크기 활용 | 촉각과 전체 하중 정보가 서로의 모호성을 보완하는가? |
| **학습 방법** | Miller 등(확인 필요)의 이력 Encoder·Forward Dynamics 보조학습 | 같은 입력의 PPO보다 접촉 변화에 적응하여 물체 이동을 개선하는가? |
| **보상 구성** | [Bi-Touch](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/literature/papers/2023-lin-bi-touch.md)의 목표·정렬 분리 + High-quality Wiping(확인 필요)의 진행 연계 | 자세·접촉 점수만 얻는 정체를 막고 실제 목표 이동을 유도하는가? |

**논의할 구성안: 영역별 Binary 접촉 + 연속 Wrench + 행동·관측 이력의 표현학습.** 센서 결합 자체를 기여로 두기보다, 접촉 위치와 센싱 조건이 달라질 때 **어떤 정보가 물체의 진행·접촉 유지에 필요하며, 그 정보를 정책이 어떻게 활용하게 할 것인지**에 초점을 둔다. F/T를 이용한 자유 물체 조작의 선행연구는 추가 확인이 필요하다.

---

검토 범위: 2026.09.17까지 확보한 프로젝트 문헌과 원문 확인 내용. 위 요소의 Sweeping 적용 효과는 비교 실험으로 확인할 항목이다. 연구 범위는 [프로젝트 결정 사항](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/3fe9c881799b82c927e89983ce0709ec3f713689/docs/03_DECISIONS_AND_OPEN_QUESTIONS.md)을 따른다.
