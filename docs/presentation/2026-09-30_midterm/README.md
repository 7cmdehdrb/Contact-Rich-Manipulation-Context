# 이진 촉각과 손목 힘·토크 피드백을 활용한 목표 지향형 물체 스위핑 연구

*A Study on Goal-Conditioned Object Sweeping without Online Visual Feedback Using Binary Tactile and Wrist Force/Torque Sensing*

[발표 문서 안내](../README.md) · [기존 Motivation](../01_Research_Motivation.md) · [Related Works](../02_Related_Works.md) · [기존 Method](../03_Method.md)

| 항목 | 내용 |
| --- | --- |
| 발표 | 졸업 주제 중간발표, 2026-09-30 예정 |
| 발표자 | 민동규, 숭실대학교 기계공학과 지능로봇시스템연구실(IROL) |
| 기준 자료 | `졸업발표_ver1(6).pdf` 및 해당 발표를 다듬으며 정리한 대화 |
| 문서 상태 | 연구 설계와 평가 계획. 구현 완료 또는 성능 검증 결과를 의미하지 않음 |
| 정리 범위 | 연구 동기 → 선행연구의 설계 선택 → 제안 방향 → 과업·방법 → 학습 조건 → 센서 기여 검증 |

이 문서는 발표의 논리 전개를 Markdown 본문으로 재구성한 정리본이다. 슬라이드 번호, 반복되는 연표, 단계별 강조 화면과 동일 수식의 반복은 통합했다. 발표본에 없는 세부 설계는 확정 내용으로 추가하지 않으며, 대화에서 보완한 설명과 아직 남은 확인 사항을 구분한다. 기존 발표 문서의 원본은 변경하지 않는다.

## 목차

- [1. 연구 동기](#motivation)
- [2. 선행연구와 설계 과제](#related-works)
- [3. 제안하는 연구 방향과 기여](#contributions)
- [4. 과업 정의와 실행 구조](#task)
- [5. Binary Tactile과 Wrench 표현](#sensing)
- [6. 정책 관측과 행동·제어](#policy)
- [7. 강화학습과 보상 설계](#reward)
- [8. 성공·실패·에피소드 종료](#episode)
- [9. 학습 조건과 Domain Randomization](#randomization)
- [10. 센서 기여 검증 계획](#evaluation)
- [11. 현재 범위와 확인 사항](#open-items)
- [부록. 자료 정리 기준과 후속 제안](#provenance)

<a id="motivation"></a>

## 1. 연구 동기

### 1.1. 시각 피드백과 가림의 한계

Sweeping과 같은 Contact-rich Manipulation에서 시각 정보는 물체의 위치·자세를 파악하고 조작 결과에 따라 행동을 보정하는 데 중요하다. 그러나 조작 중 Hand, Manipulator 또는 주변 구조물에 의해 가림(Occlusion)이 발생하면 대상 물체의 상태를 지속적으로 관측하기 어렵다.

본 연구는 시각 자체를 제거하는 것이 아니라, **초기 관측으로 물체와 목표를 정한 뒤 실행 중에는 시각적 상태 갱신에 의존하지 않는 Sweeping**을 대상으로 한다. 초기 시각과 접촉 이후의 피드백은 서로 다른 역할을 맡는다.

| 단계 | 사용하는 정보 | 역할 |
| --- | --- | --- |
| 초기 관측 | 대상 물체의 초기 위치, 상위 계획 또는 사용자 명령 | 조작 대상과 이동 목표 결정 |
| Sweeping 실행 | 로봇·Hand 상태, Binary Tactile, 손목 Wrench | 현재 상호작용을 반영한 행동 조절 |

### 1.2. 접촉 피드백을 활용하는 정책

시각 관측의 한계를 보완하기 위해 힘/토크·촉각을 활용한 멀티모달 정책이 연구되고 있다. 발표에서는 [FoAR](../../literature/papers/2025-he-foar.md)와 [Tactile Gym 2.0](../../literature/papers/2022-lin-tactile-gym-2-0.md)을 관련 사례로 제시한다. 여기서 멀티모달은 모든 연구가 F/T와 Tactile을 동시에 사용하는 것을 뜻하지 않는다. 시각·힘 또는 촉각·로봇 상태 등 각 연구의 관측 조합을 구분한다.

### 1.3. 촉각 표현의 상세도와 정보 손실

세밀한 촉각 분포와 변형을 활용하면 접촉 정보를 풍부하게 유지할 수 있지만, 시뮬레이션과 실제 센서 응답을 대응시키는 부담이 있다. 반대로 접촉 여부 중심으로 표현을 단순화하면 세부 응답에 대한 의존도를 줄일 수 있으나, 하중과 영역 내부의 접촉 정보가 축약된다.

[영역별 Binary 촉각을 사용하는 Ding 등의 연구](../../literature/papers/2021-ding-sim-to-real-tactile-manipulation.md)는 이러한 표현 선택의 사례다. 이 사례를 인용하는 것과, Binary 표현이 모든 조작 변화에 대응하지 못한다고 입증하는 것은 구분한다.

**연구의 출발점은 실물 전이를 고려하면서도, 시각 갱신이 없는 조작에서 행동 결정에 필요한 접촉 정보를 남기는 것이다.**

<a id="related-works"></a>

## 2. 선행연구와 설계 과제

### 2.1. 비교의 관점

발표에서 검토한 연구들은 필요한 정보를 서로 다른 방식으로 확보한다. 물체·목표 상태를 입력하거나, 시각·촉각 영상을 인코딩하거나, 영역별 접촉 여부와 로봇 상태를 결합한다. 다음 구분을 유지한다.

| 비교 항목 | 구분할 내용 |
| --- | --- |
| 관측 조건 | 초기 정보, 목표 명령, 실행 중 시각, 현재 대상 상태 |
| 촉각 표현 | 연속 촉각 영상, Binary 영상, 접촉면 Pose, 영역별 접촉 Bit |
| 정책·제어 | 규칙 기반 제어, 강화학습(RL), 모방학습(IL) |
| 학습·전이 | 시뮬레이션 정책 학습, 관측 변환, 센서 보정, 실물 직접 학습·시연 |
| 적용 범위 | 각 연구에서 다룬 과업과 접촉 가정 |

**Binary 영상과 영역별 Binary 벡터는 같은 표현이 아니다.** 또한 접촉력의 직접 측정이 없다는 사실만으로, 정책이 미끄러짐에 전혀 대응하지 못한다고 결론 내리지 않는다. 작업의 정교함을 입력 차원만으로 순위화하지 않는다는 것이 발표 검토 과정에서 정리한 해석 범위다.

### 2.2. 힘 피드백을 행동 조절에 연결하는 접근

| 연구 | 발표에서 다룬 방법과 과업 | 비교에서 남길 조건 |
| --- | --- | --- |
| [Learning Force Control](../../literature/papers/2020-beltran-hernandez-learning-force-control.md) | F/T 피드백을 이용한 RL 기반 정밀 삽입. 운동 보정과 힘 제어 파라미터를 함께 학습 | 시뮬레이션 비교와 실물 직접 RL 학습. 실물 학습을 Sim-to-Real 정책 전이와 동일시하지 않음 |
| [Force Push](../../literature/papers/2024-heins-force-push.md) | 로봇 위치·Force·Goal에 따라 단일점 밀기 방향을 조절. 물체의 현재 위치와 물체 모델 없이 수행하며 접촉 복구와 Admittance 보정 포함 | 준정적·평면·단일점 접촉 가정 |
| [FORGE](../../literature/papers/2025-noseworthy-forge.md) | 3축 Force 정보를 활용하는 조립 RL. 허용 힘 조건과 초과 힘 페널티로 힘 사용을 조절 | 동역학 파라미터 무작위화에 의한 전이. 본 연구의 6축 Wrench 입력과 구분 |

### 2.3. 촉각 영상 또는 국소 상태를 활용하는 접근

| 연구 | 발표에서 다룬 방법과 과업 | 표현·전이의 특징 |
| --- | --- | --- |
| [Tactile Gym 2.0](../../literature/papers/2022-lin-tactile-gym-2-0.md) | 촉각 영상으로 Pushing을 포함한 조작 수행 | Real-to-Sim GAN을 학습하여 실물 입력을 변환. 센서별 실데이터 수집과 조정 필요 |
| [Sim-to-Real Tactile Pushing — Yang 등](../../literature/papers/2023-yang-sim-to-real-tactile-pushing.md) | 촉각 영상과 접촉면 Pose를 사용하는 밀기 방법 비교 | GAN 또는 접촉면 상태 추정 모델을 통한 관측 전이 |
| [Bi-Touch](../../literature/papers/2023-lin-bi-touch.md) | Tactile·로봇·목표 정보를 사용하는 PPO 양팔 조작. Bi-pushing·Bi-reorienting·Bi-gathering 수행 | 센서별 Real-to-Sim GAN 사용. 발표에서 전단 변형의 시뮬레이션 제한을 비교 조건으로 제시 |
| [Sim2Real Manipulation — Su 등](../../literature/papers/2024-su-sim2real-tactile-manipulation.md) | 촉각 영상·로봇 상태·목표 각도로 Pivoting 수행. RGB·Diff·Binary 표현 비교 | Binary도 공간적 접촉 패턴을 유지하는 영상. 영역당 1 Bit로 축약하는 방식과 구분 |

### 2.4. 영역별 Binary 접촉을 사용하는 접근

| 연구 | 발표에서 다룬 방법과 과업 | 비교에서 남길 조건 |
| --- | --- | --- |
| [Sim-to-Real Transfer with Tactile Sensory — Ding 등](../../literature/papers/2021-ding-sim-to-real-tactile-manipulation.md) | Binary 촉각을 이용한 TD3 문 열기. 이진화와 Domain Randomization을 이용한 전이 | 문 상태 입력이 포함되며 촉각 센서 Calibration 필요 |
| [Rotating without Seeing](../../literature/papers/2023-yin-rotating-without-seeing.md) | FSR의 Binary 접촉으로 시각 없는 In-hand Manipulation 수행 | 영역별 접촉 표현과 실물 센서 대응. 힘 크기·전단력을 직접 입력하지 않는 조건 |
| [DexTouch](../../literature/papers/2024-lee-dextouch.md) | FSR 기반 Binary 접촉으로 탐색·파지·운반, 문 열기, 밸브 회전 수행 | 과업 사전정보를 사용하는 Blind Manipulation. 정확한 물체 상태는 학습에 활용 |

### 2.5. 실물 시연을 활용하는 멀티모달 정책

| 연구 | 발표에서 다룬 방법과 과업 | 학습·관측 조건 |
| --- | --- | --- |
| [Gentle Object Retraction](../../literature/papers/2026-brouwer-gentle-object-retraction.md) | Tactile·Wrench를 활용하며 주변 물체와 접촉을 허용하는 대상 확보·인출 | 실행 중 시각과 실물 시연을 사용하는 모방학습 |
| [FoAR](../../literature/papers/2025-he-foar.md) | PCD·Force 관측 기반 조작 모방학습. 미래 접촉 예측에 따라 힘 특징 반영 정도 조절 | 실행 중 시각 사용, 실물 시연 기반 학습 |

**발표 문구에 남은 확인 사항:** Gentle Object Retraction은 발표본에서 데이터 수집 시 임계점 이상의 데이터를 `Drop`한다고 요약되어 있다. 앞선 검토에서는 이를 **Impulse 한계를 초과한 시연의 종료·재수집**으로 구분했다. 개별 측정값만 삭제하는 것으로 해석하지 않으며, 상세 내용은 연결된 논문 노트를 기준으로 확인한다. 이 구분은 발표 문구의 의미를 명확히 한 대화 보완이다.

실물 학습 또는 IL을 사용한다는 사실만으로 환경 다양성이 부족하다고 결론 내리지 않는다. 본 발표에서 비교할 것은 학습 조건을 확대할 때 필요한 데이터 수집과 전이 절차의 차이다.

### 2.6. 선행연구의 종합

발표의 최종 종합은 연도별 우열이 아니라 다음 두 설계 선택이다.

**풍부한 접촉 정보의 활용:** 촉각 영상이나 그에 기반한 상태 추정으로 정보를 확보하고, 관측 데이터의 Real-to-Sim 변환 또는 실물 데이터 기반 학습을 활용한다.

**접촉 표현의 단순화:** 영역별 접촉 여부로 센서 응답을 단순화하되, 하중과 영역 내부의 세부 정보는 축약한다.

이에 따라 본 연구의 설계 과제는 **세밀한 촉각 재현에 대한 의존도를 낮추면서 Blind Sweeping에 필요한 접촉·하중 정보를 확보하는 것**으로 정리한다. 발표 검토 과정에서 정리한 대로, 이를 모든 실물 학습 연구가 공유하는 Sim-to-Real 목표로 일반화하지 않는다.

<a id="contributions"></a>

## 3. 제안하는 연구 방향과 기여

### 3.1. Binary Tactile–Wrench 결합을 통한 관측 보완

영역별 Binary Tactile은 Hand의 어느 센서 영역에서 접촉이 감지되는지를 제공한다. 손목 Wrench는 Hand를 통해 전달되는 전체 힘·모멘트를 제공한다. 두 관측을 함께 사용하여, Binary 패턴에 나타나지 않는 하중 차이를 행동 결정에 반영하려 한다.

목표는 세밀한 촉각 영상이나 모든 접촉 상태를 복원하는 것이 아니다. **접촉 영역은 단순한 표현으로 유지하고, 연속 하중 단서는 손목 F/T로 보완**하는 것이 제안 방향이다. 결합이 각 단독 관측보다 유효한지는 센서 제거 비교로 확인한다.

### 3.2. 목표 달성과 접촉 유지를 고려한 보상 설계

대상 물체가 지정된 목표로 이동하는 것을 주목적으로 두고, 접촉 방향 정렬과 필요한 접촉의 유지, 불필요한 행동 변화와 시간 비용을 보조 항으로 구성한다.

시뮬레이션에서는 현재 물체 위치와 접촉 정답으로 행동 결과를 평가할 수 있다. 그러나 그 정답을 실제 실행의 Actor 관측으로 제공하지 않는다.

> **Wrench는 실행 관측을 보완하고, Privileged Information은 학습 중 행동의 결과를 평가한다.**

두 항목은 검증된 성과가 아니라 제안하는 기여다. 특히 Reward가 손실된 관측 정보를 복원한다거나, Wrench만으로 모든 접촉 원인이 식별된다고 가정하지 않는다.

<a id="task"></a>

## 4. 과업 정의와 실행 구조

### 4.1. 과업과 범위

초기 관측과 Tactile·Wrench 피드백을 이용하여 대상 물체를 지정된 방향과 거리만큼 미는 **Goal-conditioned Blind Sweeping**을 수행한다.

| 항목 | 현재 발표의 정의 |
| --- | --- |
| 목표 조건 | Human Operator 또는 High-level Planner가 결정 |
| 초기 물체 정보 | 초기 Position 3D |
| 이동 명령 | Sweep 방향 1D + 거리 1D |
| 실행 중 시각 | 현재 물체 상태의 시각 갱신을 사용하지 않음 |
| 주변 물체 | Sweeping 과정에서 다른 물체의 간섭이 발생하지 않는 조건 |
| 물체 배치 | 작업 공간 내 위치와 종류를 무작위화 |
| 이동 방식 | 발표에서는 작업 공간·물체 제약으로 파지 이동을 사용하지 않는 조건을 설정 |
| 대상 물체 | Cube·Cylinder 등의 Primitive와 직접 스캔한 비정형 물체 |
| 변화 조건 | 물체 크기·질량·마찰 계수 등을 Scene별로 무작위화 |

마지막 파지 제한은 본 연구의 과업 가정이다. 실제로 모든 대상이 파지 불가능함을 검증한 결과로 확대하지 않는다.

### 4.2. 접근과 접촉 조작의 분리

```text
초기 RGB-D 관측 + 사용자/상위 목표 명령
  → MoveIt으로 대상 물체 근처까지 접근
  → 로봇·Hand 상태 + Binary Tactile + Wrench + 초기 목표 정보
  → RL Policy
  → Arm Cartesian 증분 + Hand 관절 목표
  → OSC / Hand Joint Position Controller
  → Sweeping
```

접근 단계는 Sweep 방향의 반대쪽으로 Offset된 위치와, Sweep 방향에 평행한 Hand Normal을 기준으로 한다. 발표의 접근 그림에는 Dead Zone이 포함되어 있다. 접근 Planner 자체나 Home에서 물체까지의 전체 이동을 RL의 학습 과업으로 확장하지 않는다.

**기존 Method의 상세 설정:** Sweep Command의 360도 방향 범위와 접근 Pose의 Dead Zone은 별개로 정리되어 있다. 구체적인 Offset·도달 허용 오차·좌표축 설정은 [기존 Method](../03_Method.md)를 참고하되, 발표본에 없는 수치를 이 문서에서 새로 확정하지 않는다.

### 4.3. 플랫폼과 시뮬레이션

| 구성 | 현재 계획 |
| --- | --- |
| Manipulator | UR5e |
| Hand | Inspire Robot Hand RH56E2 |
| 손바닥 촉각 | 저항식 Tactile 17개 영역 |
| 손등 촉각 | 위치별 대응을 고려하여 부착할 FSR 17개 |
| 손목 F/T | ATI Axia80 계열, 기존 설계의 Axia80-M8 |
| 초기 관측 | RGB-D Camera |
| 시뮬레이션·학습 | Isaac Lab, RSL-RL / PPO |

장비와 센서 구성은 계획이며, 본 문서는 실물 장착·Calibration·성능 검증이 완료되었다고 보고하지 않는다.

<a id="sensing"></a>

## 5. Binary Tactile과 Wrench 표현

### 5.1. 영역별 촉각 이진화

손바닥의 17개 Tactile 영역과 손등에 부착할 17개 FSR을 위치별 동일 인덱스로 매핑한다. 한 번의 관측에는 **작업 면 Header 1D와 선택 면의 접촉 여부 17D**, 총 18D를 사용한다.

손바닥 영역 안의 Cell 중 하나라도 임계값 이상이면 해당 영역을 접촉으로 처리한다. 발표 수식의 표기를 영역 인덱스 $i$, 영역 내 Cell 인덱스 $j$로 풀면 다음과 같다.

```math
b^{\mathrm{palm}}_{t,i}
=
\mathbf{1}_{\{\max_{1\leq j\leq N_i}f_{t,i,j}\geq 0.05\,\mathrm{N}\}}.
```

손등 FSR에 제시된 식은 다음과 같다.

```math
b^{\mathrm{dorsal}}_{t,i}
=
\mathbf{1}_{\{f_{t,i}>0.05\,\mathrm{N}\}}.
```

0.05 N은 현재 발표 수식에 적힌 설정값이다. 실물 센서별 감지 성능을 검증하여 확정한 값으로 해석하지 않는다. 손바닥 식의 `이상`과 손등 식의 `초과`는 원문을 보존했으며, 경계값 처리 통일은 확인 사항이다.

선택한 작업 면의 Binary 벡터를 $\mathbf{c}_t$, 작업 면 Header를 $m_t$로 두면 다음과 같다.

```math
\mathbf{z}_t=[m_t,\mathbf{c}_t],\qquad
\mathbf{c}_t\in\{0,1\}^{17},\qquad
\mathbf{z}_t\in\{0,1\}^{18}.
```

Header는 접촉 개수가 아니라 작업 면을 나타낸다. [기존 Method](../03_Method.md)는 손바닥과 손등의 단면 접촉 조건 아래 비선택 면을 생략하는 설계를 설명한다. 양면 동시 접촉이나 작업 면 전환의 상세 처리는 이번 발표에서 별도로 정의하지 않았다.

### 5.2. 시뮬레이션과 실물의 표현 대응

시뮬레이션에서는 Isaac Lab Contact Sensor의 접촉력을 영역별 임계값으로 이진화한다. 실물에서도 관측을 Binary 형태로 변환하여, 세부 센서 응답의 정밀한 일치에 대한 의존도를 줄이려 한다.

이진화로 입력 형식을 통일하는 것과 동일한 물리 접촉에서 항상 같은 신호가 발생하는 것은 구분한다. 임계값, 접촉 누락과 오검출, 영역 매핑 및 지연은 후속 확인 대상으로 남는다.

### 5.3. 손목 Wrench

```math
\mathbf{w}_t
=[F_x,F_y,F_z,M_x,M_y,M_z]_t
\in\mathbb{R}^{6}.
```

Binary 접촉은 하중 크기와 영역 내부의 세부 접촉 변화를 직접 표현하지 않는다. 손목의 전체 힘·모멘트를 함께 사용하여, Binary 패턴에 나타나지 않는 하중 차이에 대한 단서를 추가한다.

시뮬레이션에서는 손목 F/T 장착 위치에 **측정용 Fixed Joint**를 두고, Tool rigid body를 통해 전달되는 6축 Joint Reaction Wrench를 가상 센서 관측으로 사용한다.

현재 문서는 작은 접촉점 이동이나 Slip의 검출 해상도를 수치 성능으로 주장하지 않는다. 가상 Joint에서 얻는 전체 하중과 대상 물체만의 개별 접촉력은 구분하며, 필요한 보정의 적용 범위는 구현 시 확인한다.

<a id="policy"></a>

## 6. 정책 관측과 행동·제어

### 6.1. Actor Observation: 57D

| 구성 | 세부 내용 | 차원 |
| --- | --- | ---: |
| Robot 상태 | Arm Joint Position 6 + Joint Velocity 6 | 12 |
| Hand 상태 | Hand/EEF Pose 6 + 저차원 Hand Joint 상태 2 | 8 |
| Binary Tactile | 작업 면 Header 1 + 선택 면 접촉 여부 17 | 18 |
| Wrench | 힘 3 + 모멘트 3 | 6 |
| Goal Condition | Initial Target Position 3 + 방향 1 + 거리 1 | 5 |
| Last Action | Arm Action 6 + Hand Action 2 | 8 |
| **합계** | 로봇·Hand 상태 20 + 센서 24 + 목표 5 + 직전 행동 8 | **57** |

```math
o_t=[\mathbf{x}^{\mathrm{robot}}_t,
\mathbf{x}^{\mathrm{hand}}_t,
\mathbf{z}_t,\mathbf{w}_t,
\mathbf{g},a_{t-1}].
```

여기서 $\mathbf{g}$는 초기 대상 위치와 방향·거리 명령을 묶은 Goal Condition이다. 현재 대상 물체의 Pose를 실행 중 지속적으로 넣는 항이 아니다.

Hand는 6자유도 전체를 독립적으로 표현·제어하는 대신, 공통 굽힘과 엄지의 별도 관절로 이루어진 2D 표현을 사용한다. 발표는 이를 Sweeping 접촉 자세에 집중하고 학습을 단순화하기 위한 선택으로 설명한다. 2D가 충분하다는 실험 결과가 있는 것은 아니다.

**기존 Method에 명시된 좌표계:** 현재 EEF Pose와 초기 목표 정보는 Sweep 시작 EEF Frame에 대한 상대량으로, Wrench와 Arm 증분 Action은 현재 EEF Frame 기준으로 정리되어 있다. 자세의 3성분 표현과 정규화 세부는 미정이다. 센서 이력 Stack이나 RNN을 현재 관측에 추가하지 않으며, 명시된 이력은 Last Action 8D다.

### 6.2. 학습 정보와 실행 정보의 구분

발표 프레임워크는 현재 물체 Pose와 시뮬레이션 접촉 정보를 Privileged Information으로 분리한다. 현재 물체 위치는 목표 보상 계산에, 접촉 정답은 접촉 관련 평가에 사용할 수 있다.

이 정보는 최종 Blind Actor의 온라인 관측과 구분한다. 현재 발표만으로 Critic 또는 Teacher의 별도 입력 구조를 확정할 수 없으므로, 새로운 비대칭 학습 구조를 임의로 추가하지 않는다.

프레임워크의 `Contact Force`에는 6D 표기가 있으나, 이 값이 힘 3D와 모멘트 3D를 합친 것인지 등 세부 정의는 명시되지 않았다. 아래 보상에서 사용하는 접촉 Normal과 손목 Wrench를 같은 값으로 간주하지 않는다.

### 6.3. Arm Action과 OSC

```math
\mathbf{a}_{r,t}
=[\Delta p_x,\Delta p_y,\Delta p_z,
\Delta\theta_x,\Delta\theta_y,\Delta\theta_z]_t
\in\mathbb{R}^{6}.
```

정책은 Cartesian 위치·회전 증분을 출력하고, Operational Space Controller(OSC)가 로봇 명령으로 변환한다. 정책이 F/T 관측을 받아 다음 증분을 조절함으로써 물체를 미는 상호작용을 조정하도록 학습한다.

OSC의 Gain, Action Scale, 제어 주기 및 실물 제어 인터페이스의 구체적인 값은 이번 발표에서 확정하지 않았다.

### 6.4. Hand Action과 Joint Position Control

Hand Action은 공통 굽힘 $u_f$와 별도 엄지 관절 $u_{\mathrm{thumb}}$의 두 성분이며, 각각 0~1 범위의 입력을 관절 목표에 선형 매핑한다.

```math
q_j^*=(1-u_f)q_j^{\mathrm{closed}}+u_fq_j^{\mathrm{open}},
\qquad u_f\in[0,1].
```

```math
q_{\mathrm{thumb}}^*
=(1-u_{\mathrm{thumb}})q_{\mathrm{thumb}}^{0}
+u_{\mathrm{thumb}}q_{\mathrm{thumb}}^{1},
\qquad u_{\mathrm{thumb}}\in[0,1].
```

```math
\mathbf{a}_{h,t}=[u_f,u_{\mathrm{thumb}}]_t,\qquad
a_t=[\mathbf{a}_{r,t},\mathbf{a}_{h,t}]\in\mathbb{R}^{8}.
```

첫 번째 식은 $u_f=0$에서 Closed, $u_f=1$에서 Open을 뜻한다. 엄지의 두 끝점이 대응하는 실제 관절값은 후속 구현에서 정한다. 각 관절 목표는 Hand의 Joint Position Controller로 실행한다.

<a id="reward"></a>

## 7. 강화학습과 보상 설계

Isaac Lab 환경에서 RSL-RL / PPO를 이용해 정책을 학습하는 구성을 제안한다. 목표 위치에 도달하도록 하는 보상을 주항으로 두고, 접촉 방향·접촉 유지·행동 변화량·시간 비용을 보조 항으로 둔다.

아래는 **최신 발표본의 식을 옮긴 것**이다. 이전 대화의 다른 보상 후보나 계수를 섞지 않으며, 부호·가중치 등 확인이 필요한 부분은 별도로 표시한다.

```math
r_t=r_{\mathrm{goal},t}+r_{\mathrm{normal},t}
+r_{\mathrm{contact},t}+r_{\mathrm{action},t}+r_{\mathrm{time},t}.
```

### 7.1. 목표 도달 보상

```math
r_{\mathrm{goal},t}
=\exp\left(-\frac{\|\mathbf{p}_t-\mathbf{p}_g\|_2}{\sigma_p}\right).
```

$\mathbf{p}_t$는 현재 대상 물체의 위치이며 Privileged Information이다. $\mathbf{p}_g$는 사용자 명령에 따른 목표 위치, $\sigma_p$는 거리 오차에 대한 보상 계수다. 물체가 목표에 가까워질수록 높은 보상을 부여한다.

### 7.2. 접촉 Normal 정렬 보상

```math
r_{\mathrm{normal},t}
=-\frac{1-\hat{\mathbf{n}}_t^{\mathsf{T}}\hat{\mathbf{d}}}{2}.
```

$\hat{\mathbf{n}}_t$는 Hand–대상 물체 접촉의 Normal, $\hat{\mathbf{d}}$는 명령된 Sweep 방향의 단위벡터다. 두 방향이 정렬되도록 유도한다.

과거 대화에서 분모 2를 제거하는 안도 있었지만, 최신 PDF에는 분모 2가 있으므로 이 문서는 해당 식을 보존한다. 무접촉 또는 다중 접촉에서 대표 Normal을 정하는 방법은 아직 명시되지 않았다.

### 7.3. 접촉 상태 유지 보상

접촉 유무 $C_t$와 활성 영역의 가중 비율 $N_t$를 구분한다.

```math
C_t=\mathbf{1}_{\{\sum_{i=1}^{17}c_{t,i}>0\}},
\qquad
N_t=\frac{\sum_{i=1}^{17}\alpha_i c_{t,i}}
{\sum_{i=1}^{17}\alpha_i}.
```

```math
r_{\mathrm{contact},t}
=\beta C_t+(1-\beta)N_t-1.
```

$c_{t,i}$는 선택 면의 $i$번째 영역의 Binary 접촉값, $\alpha_i$는 영역별 중요도 가중치, $\beta$는 접촉 유무와 활성 비율의 배분 계수다. 작업 면 Header는 접촉 개수에 포함하지 않는다.

발표에서는 이를 접촉 유지와 접촉 면적 확대를 유도하는 보조 보상으로 설명한다. **식에서 직접 계산하는 것은 실제 면적이 아니라 활성 촉각 영역의 가중 비율**이라는 점은 대화에서 구분한 내용이다. 가중치와 배분 계수의 수치는 아직 정해지지 않았다.

### 7.4. Action 변화량 항

```math
r_{\mathrm{action},t}
=\lambda_r\|\mathbf{a}_{r,t}-\mathbf{a}_{r,t-1}\|_2^2
+\lambda_h\|\mathbf{a}_{h,t}-\mathbf{a}_{h,t-1}\|_2^2.
```

Arm과 Hand의 직전 명령 대비 변화를 억제하려는 항이다. $\lambda_r$, $\lambda_h$는 두 명령 변화량의 상대 계수다.

**원문 확인 필요:** 발표에서는 페널티라고 부르지만 식은 위처럼 양의 합으로 쓰여 있다. 계수 자체를 음수로 둘지, 식 앞에 음수를 둘지는 명시되지 않았다. 이 문서는 임의로 부호를 수정하지 않는다.

### 7.5. 시간 비용

```math
r_{\mathrm{time},t}=-\frac{\Delta t}{T_{\mathrm{ref}}}.
```

$\Delta t$는 한 정책 제어 Step의 시간 간격이며, $T_{\mathrm{ref}}$는 정규화에 사용하는 기준 수행 시간이다.

### 7.6. 보상과 기여의 연결

접촉 보조 항은 물체를 목표로 이동시키는 주목적을 지원하도록 설계한다. 센서 활성이나 자세 정렬 자체가 목표 이동을 대신하는 것은 아니다.

현재 합산식에는 Wrench 크기를 직접 벌점으로 주는 항이나 전도 전 기울기 페널티가 들어 있지 않다. 이 항들은 대화에서 검토한 후보와 구분하며, 이미 적용된 하중·전도 억제 보상으로 설명하지 않는다. 학습 계수의 최종값과 실제 보상 기여는 후속 검증 대상으로 남는다.

<a id="episode"></a>

## 8. 성공·실패·에피소드 종료

### 8.1. 대상 물체의 목표 도달

```math
\|\mathbf{p}_t-\mathbf{p}_g\|_2<\epsilon_{p,g}.
```

$\epsilon_{p,g}$는 대상 물체의 허용 위치 오차다. 최신 PDF는 기호로 표현하며, 대화에서 정한 성공 기준은 **1 cm 미만**, 즉 0.01 m다. 성공의 대상은 EEF가 아니라 대상 물체다.

시뮬레이션의 현재 물체 위치는 성공 판정에 사용할 수 있으나, 이를 최종 Actor의 실시간 물체 위치 관측으로 전달하지 않는다.

### 8.2. 물체 전도

최신 발표본은 Yaw를 제외한 Roll $\phi_t$와 Pitch $\theta_t$의 크기로 전도 종료 조건을 표현한다.

```math
T_{\mathrm{topple},t}
=\mathbf{1}_{\{\sqrt{\phi_t^2+\theta_t^2}>\epsilon_{\mathrm{topple}}\}}.
```

$\epsilon_{\mathrm{topple}}$은 허용 기울기의 임계값이다. Roll·Pitch의 기준 좌표계, 초기 지지 자세 기준과 물체별 임계값은 아직 명시되지 않았다. 이 식은 발표에서 채택한 판정 지표이며, 모든 형상의 물리적 전도 한계를 유도한 식은 아니다.

대화에서 물체 수직축과 선반 법선 사이의 각도를 사용하는 대안과 점진적 기울기 페널티도 검토했다. 최신 PDF의 판정식을 그 대안으로 교체하거나, 해당 페널티를 현재 보상 합에 임의로 추가하지 않는다.

### 8.3. 선반 이동과 금지 접촉

최신 발표본의 수식은 선반의 위치 또는 자세 변화가 임계값을 초과하는 조건이다.

```math
\Delta p_{\mathrm{shelf}}>\epsilon_{p,\mathrm{shelf}}
\quad\lor\quad
\Delta\theta_{\mathrm{shelf}}>\epsilon_{R,\mathrm{shelf}}.
```

| 기호 | 의미 |
| --- | --- |
| $\Delta p_{\mathrm{shelf}}$ | 선반 초기 위치 대비 현재 위치의 이동량 |
| $\Delta\theta_{\mathrm{shelf}}$ | 선반 초기 자세 대비 현재 자세의 회전량 |
| $\epsilon_{p,\mathrm{shelf}}$ | 선반의 허용 위치 이동량 |
| $\epsilon_{R,\mathrm{shelf}}$ | 선반의 허용 자세 변화량 |

발표 본문은 Hand 또는 Manipulator의 선반 충돌을 실패 조건으로 설명하지만, 위 수식에는 직접적인 접촉 항이 없다. **대화에서 보완한 논리**는 선반 이동과 금지 접촉을 OR로 묶는 것이다.

```math
T_{\mathrm{shelf},t}
=\mathbf{1}_{\{c_{\mathrm{shelf},t}=1
\ \lor\ \Delta p_{\mathrm{shelf}}>\epsilon_{p,\mathrm{shelf}}
\ \lor\ \Delta\theta_{\mathrm{shelf}}>\epsilon_{R,\mathrm{shelf}}\}}.
```

$c_{\mathrm{shelf},t}$는 Hand·Arm과 금지된 선반 구조물 사이의 접촉 여부다. 대상 물체와 선반 바닥의 정상 지지 접촉은 포함하지 않는다. 감지 임계값 또는 힘 기준의 상세 설정은 미정이다.

**고정 선반과의 구분:** Fixed shelf 또는 고정 작업판에서는 선반 이동 조건이 의미를 갖지 않으므로, 금지 접촉 조건을 사용한다. 고정 작업판을 쓰는 단순화 시험과 최신 PDF의 이동 가능한 선반 수식을 하나의 확정 설정으로 혼합하지 않는다. 이번 문서는 선반 모델을 새로 결정하지 않는다.

### 8.4. 시간 제한

```math
t\geq T_{\max}.
```

제한 시간까지 목표 도달이나 실패가 발생하지 않으면 에피소드를 중단한다. PDF에서는 이를 `Termination 3`에 묶어 적었으나, 대화에서는 성공·실패 Termination과 시간 제한 Truncation을 구분했다. 이 문서는 그 구분을 표시하며 구체적인 API 구현을 확정하지 않는다.

### 8.5. 실제 실행 종료와의 경계

학습·평가용 정답으로 성공을 판정하는 것과 실제 로봇이 종료 시점을 결정하는 것은 별개의 문제다. Blind 실행에서 사용할 종료 판단은 아직 정해지지 않았으며, EEF 이동거리를 물체의 목표 도달로 자동 대체하지 않는다.

<a id="randomization"></a>

## 9. 학습 조건과 Domain Randomization

**유효한 Sweeping 조건을 유지하면서 물체·접촉·제어·센서 조건을 변화시켜, 특정 상황에 대한 의존도를 줄이는 것**이 목적이다. 강건성 향상이 검증되었다는 뜻은 아니다.

### 9.1. 발표본에 포함된 무작위화

| 대상 | 현재 발표에서 제시한 항목 |
| --- | --- |
| Robot | MoveIt 접근 완료에 대응하는 물체 근처 위치의 변동, Initial Joint State, Controller Parameter |
| Hand | Initial Joint State, Controller Parameter |
| Environment / Object | 마찰 계수, 물체 형상·크기·질량·위치 |
| Sensor Uncertainty | Binary Tactile과 F/T 센서의 Bias·Noise |

학습은 물체 옆의 도달 가능한 상태에서 시작하도록 구성한다. 실물에서 매 에피소드마다 MoveIt을 실행하며 학습한다는 의미가 아니라, 접근 완료 상태에 대응하는 시뮬레이션 초기조건을 정한다는 의미다.

### 9.2. 대화에서 구체화한 초기조건과 센서 오차 후보

| 구분 | 논의한 상세 내용 | 상태 |
| --- | --- | --- |
| 접근 초기조건 | Sweep 반대편의 Hand 배치, Nominal EEF Pose 주변의 위치·자세 변화, 초기 접촉 미보장 | 설계 설명 |
| 물체 조건 | Center of Mass, Initial Orientation 등 | 추가 후보, 범위 미정 |
| Robot·Hand 조건 | OSC Stiffness·Damping, 공통 굽힘·엄지 초기값, Hand–물체 상대 자세 | 상세 범위 미정 |
| Binary Tactile | 접촉 누락, 오검출, 임계값 변화, 지연 | 적용 후보 |
| Wrench | Zero Bias, 힘·모멘트 Noise, Scale Error, Payload 보정 잔여 오차, 지연 | 적용 후보 |

Binary 관측의 `Bias·Noise`를 연속값의 가산 오차로 처리할지, 이진화 전 오차·임계값·Bit 오류로 모델링할지는 발표에서 명시되지 않았다. 기존 논의의 후보를 실제 적용 완료 항목처럼 쓰지 않는다.

### 9.3. 유효한 Reset 조건

명령된 방향으로 물체를 미는 것이 가능한 상태, 로봇과 선반의 초기 금지 충돌이 없는 상태, Hand와 물체가 비정상적으로 관통하지 않는 상태를 사용한다. 현재 과업 가정에 따라 다른 물체의 간섭이 없는 Sweeping 조건을 유지한다.

대화에서는 Randomization 범위를 추후 실제 접근 오차와 센서 특성 측정을 바탕으로 갱신하는 방향을 정리했다. 현재 자료에는 분포·범위·측정 결과가 제시되지 않는다.

<a id="evaluation"></a>

## 10. 센서 기여 검증 계획

### 10.1. 비교 목적

센서 외의 조건을 고정하고 Actor의 접촉·F/T 관측만 변경하여, Binary Tactile과 Wrench의 개별·결합 효과를 비교한다. **주된 비교는 결합 정책에서 센서 하나를 제거했을 때 무엇이 달라지는가**다.

물리적인 Hand–물체 접촉을 없애는 실험이 아니다. `No Contact Sensing`은 접촉 관측을 제공하지 않는 조건이다. 최신 발표의 Case 1에 있는 “접촉 없이 수행”은 대화의 정의에 따라 “접촉 센싱 없이 수행”으로 구분한다.

### 10.2. 공통 관측과 네 가지 조건

```math
o_t^{\mathrm{base}}
=[\mathrm{Robot\ and\ Hand\ State},
\mathrm{Goal\ Condition},\mathrm{Last\ Action}].
```

```math
\begin{aligned}
o_t^{(1)}&=o_t^{\mathrm{base}},\\
o_t^{(2)}&=[o_t^{\mathrm{base}},\mathbf{z}_t],\\
o_t^{(3)}&=[o_t^{\mathrm{base}},\mathbf{w}_t],\\
o_t^{(4)}&=[o_t^{\mathrm{base}},\mathbf{z}_t,\mathbf{w}_t].
\end{aligned}
```

| Case | 접촉 관측 | 결합 정책을 기준으로 한 해석 |
| --- | --- | --- |
| **1. No Contact Sensing** | Tactile·F/T 모두 없음 | 접촉 피드백 없는 기준 성능. Case 4와 비교해 전체 효과 확인 |
| **2. Binary Tactile Only** | Binary Tactile만 사용 | **F/T 제거 조건. Case 4 대비 F/T의 추가 기여 확인** |
| **3. Wrist Wrench Only** | 3축 힘·3축 모멘트만 사용 | **Tactile 제거 조건. Case 4 대비 Tactile의 추가 기여 확인** |
| **4. Binary Tactile + Wrench** | 두 접촉 관측 모두 사용 | 제안 방식. 각 단독 관측과 비교해 결합 효과 평가 |

Case 2 또는 Case 3의 성능 하나만으로 빠진 센서의 기여가 증명되는 것은 아니다. **Case 4와의 차이**가 해당 센서의 추가 기여를 보여주는 비교다.

### 10.3. 비교 차이의 의미

성공률처럼 클수록 좋은 동일한 평가 지표를 $J_k$라 두면, 대화에서 정리한 비교 의미는 다음과 같다. 이는 실측값이 아니라 비교 관계를 나타내는 표기다.

```math
\Delta_{\mathrm{F/T}\mid\mathrm{Tactile}}=J_4-J_2,
\qquad
\Delta_{\mathrm{Tactile}\mid\mathrm{F/T}}=J_4-J_3.
```

| 비교 | 확인할 효과 |
| --- | --- |
| **Case 4 − Case 2** | Tactile이 있는 상태에서 F/T를 추가한 효과 |
| **Case 4 − Case 3** | F/T가 있는 상태에서 Tactile을 추가한 효과 |
| Case 2 − Case 1 | Tactile 단독 추가 효과 |
| Case 3 − Case 1 | F/T 단독 추가 효과 |
| Case 4 − Case 1 | 접촉 센서 결합의 전체 효과 |

설계의 기대는 Case 4가 두 단독 조건보다 유리한 것이다. **현재는 검증할 가설이며, Case 4가 반드시 가장 좋다는 결과를 전제하지 않는다.** 결합의 효과가 없거나 일부 조건에서만 나타나는 경우도 구분하여 해석해야 한다.

### 10.4. 공통으로 유지할 조건

대화에서 비교 원칙으로 정리한 조건은 초기 상태 분포, Goal Command, Action Space, OSC·Hand Controller, Reward·종료 기준, Network 설계, 학습량과 Seed 조건이다. 수치와 반복 횟수는 미정이다.

각 관측 조건의 정책을 별도로 학습한다. 결합 정책에서 실행 시 입력만 갑자기 지우는 시험과는 구분한다. 관측을 제거하더라도 Reward·종료 계산에는 동일한 시뮬레이션 정답을 사용하여, 보상 차이와 관측 차이가 섞이지 않게 한다.

**세부 미정:** Tactile 18D에는 작업 면 Header가 포함된다. 제거 실험에서 Header도 함께 제거할지, 공통 작업 조건으로 남길지는 최신 발표에 명시되지 않았다. Network 역시 입력 차원이 달라지는 만큼, “동일 구조”의 구체적인 통제 범위는 추가 정의가 필요하다.

### 10.5. 연구 질문과 평가 대상

| 연구 질문 | 우선 연결되는 비교 | 대화에서 제안한 평가 대상 |
| --- | --- | --- |
| **RQ1. Binary Tactile은 접촉 상실을 줄이는 데 유효한가?** | Case 4 vs. Case 3. 보조적으로 Case 2 vs. Case 1 | 실제 Hand–물체 접촉 상실 횟수·시간, 접촉 유지 |
| **RQ2. Wrist Wrench는 물체·접촉 조건 변화에 따른 하중 조절에 유효한가?** | Case 4 vs. Case 2. 보조적으로 Case 3 vs. Case 1 | 힘·모멘트 변화, 과도한 하중, 접촉 조건별 행동 |
| **RQ3. 결합 정책이 단독 정책보다 목표 도달과 접촉 안정성을 개선하는가?** | Case 4 vs. Case 2·3 | 성공률, 최종 물체 위치 오차, 접촉 상실·전도·금지 충돌 |

이 세 RQ는 최신 발표본에 포함되어 있다. 표의 세부 지표는 앞선 대화에서 논의한 평가 후보이며, 산식·집계 구간·시험 횟수까지 확정한 실험 프로토콜은 아니다.

접촉 안정성을 평가할 때는 각 정책에 제공한 센서값과 평가용 실제 접촉 정답을 구분한다. 총 Reward 자체를 비교의 유일한 성능 지표로 삼지 않으며, Wrench 추가로 성능이 달라졌다는 결과를 별도의 Slip 상태 추정 정확도로 바꾸어 주장하지 않는다.

<a id="open-items"></a>

## 11. 현재 범위와 확인 사항

현재 발표는 Motivation, 선행연구 비교, 제안 기여, 센서·정책·제어·보상 설계, 종료 조건, Domain Randomization과 센서 Ablation 계획까지 구성되어 있다. **실제 실험 결과, 성능 수치, 실물 정책 전이 성공은 아직 제시되지 않았다.**

| 항목 | 현재 남은 확인 사항 |
| --- | --- |
| 보상식 | Action 변화량 항의 부호·계수, 총 보상의 가중치. 최신 PDF의 Normal 항 분모 2 유지 여부 |
| 접촉 정의 | 무접촉·다중 접촉에서 Normal을 정하는 방식, 실제 접촉과 활성 영역 비율의 구분 |
| 촉각 관측 | 0.05 N의 실물 적용성, 경계값 처리, 양면 매핑·동시 접촉 처리 |
| Privileged Contact Force | 프레임워크의 6D 표기가 의미하는 측정량과 좌표계 |
| 전도 판정 | Roll·Pitch 기준 자세·좌표계와 물체별 임계값, 기울기 페널티의 채택 여부 |
| 선반 조건 | 고정·비고정 모델별 종료 조건, 직접 접촉 검출 항과 이동량 조건의 적용 범위 |
| 실제 종료 | 물체 정답 없이 사용할 실행 종료 판단 |
| Randomization | 물체·접촉·제어·센서별 분포와 범위 |
| 센서 Ablation | 작업 면 Header의 처리, Network 통제 범위, 학습·평가 예산과 반복 조건 |
| 평가 프로토콜 | 지표의 계산 방식, 학습·평가 물체 분리, 실물 평가 시 정답 측정 방식 |

위 항목은 오류를 임의로 정정하거나 새 알고리즘으로 채운 내용이 아니라, 발표본과 대화 사이에서 확정되지 않은 사항을 보존한 목록이다.

**요약:** 초기 시각 이후 Binary Tactile과 손목 Wrench로 Sweeping을 수행하는 정책을 설계한다. 단순한 접촉 표현과 연속 하중 정보를 결합하고, 시뮬레이션 정답을 이용해 목표 이동과 접촉 유지 행동을 학습한다. 센서 제거 비교를 통해 F/T와 Tactile의 추가 기여 및 결합의 유효성을 검증한다.

<a id="provenance"></a>

## 부록. 자료 정리 기준과 후속 제안

### A. 정리 근거

| 자료 | 사용 범위 |
| --- | --- |
| `졸업발표_ver1(6).pdf` | 제목, Motivation, 발표 대상 12편의 비교, Contribution, 과업·센서·정책·보상·종료·Randomization·센서 평가 계획의 기준 |
| 발표 검토 대화 | 관측과 학습용 정답의 역할 분리, 선행연구 해석 범위, 종료 조건의 구분, Case 4–2 및 Case 4–3의 Ablation 해석 |
| [기존 Motivation](../01_Research_Motivation.md) | 접촉 영역과 하중 정보의 역할 분담에 관한 기존 설명 |
| [기존 Related Works](../02_Related_Works.md) | 발표에 등장한 논문들의 상세 설명과 개별 노트 연결 |
| [기존 Method](../03_Method.md) | EEF 기준 관측·Action, 양면 촉각 Header 등 발표에서 축약된 기존 설계 설명 |

원자료 식별을 위한 PDF SHA-256: `5a7d2af915ba58b60f13fe7fde6296099c14744290b6c3c46150e7b5c38cb1d4`.

원본 PDF는 이 폴더에 포함하지 않는다. 문헌 링크는 저장소에 존재하는 개별 논문 노트로 연결한다. 이번 작업은 새로운 원문 문헌조사가 아니라 발표·대화·기존 정리의 문서화이며, 논문 전체를 새로 검증했다는 의미가 아니다.

### B. 발표에 포함된 문헌조사 집계

다음은 발표의 **사전 문헌조사에서 검토한 논문 수**를 중복 없이 옮긴 것이다. 열 제목과 수치는 원자료를 유지한다.

| 발간 연도 | 데이터 근사, Feature 추출 | Image, Tactile 기반 물리 정보 추출 | Image, PCD, Tactile 임베딩 |
| --- | ---: | ---: | ---: |
| ~2021 | 3 | 0 | 1 |
| 2022 | 1 | 0 | 1 |
| 2023 | 2 | 0 | 1 |
| 2024 | 7 | 1 | 2 |
| 2025 | 3 | 0 | 5 |
| 2026 | 2 | 0 | 1 |

개별 12편의 발표 요약과 사전 조사 전체의 집계는 범위가 다르다. 집계의 선정 기준과 중복 분류 여부는 PDF만으로 확정할 수 없으며, 분야 전체의 연도별 점유율 또는 성능 발전을 입증하는 통계로 해석하지 않는다.

### C. 최신 발표본에 아직 없는 후속 제안

대화에서는 **Reward Ablation**과 **실물 검증 단계**도 제안했다. 그러나 최신 PDF의 끝은 Sensor Contribution과 세 RQ이며, 아래 내용을 완료된 발표 구성이나 확정 실험으로 편입하지 않는다.

| 후속 제안 | 논의한 내용 | 현재 취급 |
| --- | --- | --- |
| Reward Ablation | 관측·제어를 고정하고 Contact·Normal 보상 항의 유무 비교 | 후보 조합이 논의되었으나 최종 실험 구성 미확정 |
| 실물 검증 | 센서·제어 대응 확인 후 정책 실행과 목표·접촉 결과 평가 | 장비 확보 후 수행할 계획 후보 |
| 평가 조건 분리 | 학습에 사용하지 않은 물체·초기조건 및 물성 범위 평가 | 데이터 분할과 범위 미확정 |

새 결과가 나오기 전까지는 제안한 센서 결합과 보상 설계를 연구 가설·계획으로 유지한다.
