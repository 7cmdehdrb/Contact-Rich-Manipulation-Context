# 1. 기존 연구 대비 차별점 (Differentiation from Prior Work)

> **용어 표기 원칙**: 핵심 개념은 영어 전문 용어를 그대로 사용하며, 아래 표기를 문서 전체에서 통일한다.  
> perception · target pose estimation · contact-rich manipulation · position control · physical interaction · force/torque (F/T) feedback · action space · joint space · Cartesian space · end-effector (EEF) pose · exploration · failure mode · sample efficiency · privileged state · observation representation · translation invariance · domain randomization · out-of-distribution (OOD) · zero-shot transfer · task specification · language-conditioned manipulation · vision-language-action (VLA)

> **서술 원칙**: 각 한계는 [사실] — 기존 연구 코드·문서에서 확인된 것, [근거] — 역학적·문헌적 뒷받침, [추정] — 실험으로 검증이 필요한 가설로 구분한다.  
> 각 차별점은 [채택] — 내려진 설계 결정, [근거] — 이론적·공학적 근거, [추정] — 정량적 이득의 검증 필요 항목으로 구분한다.

---

## 목차

1. [기존 연구의 한계](#11-기존-연구의-한계)
2. [시스템 구조 개요 및 설계 원칙](#12-시스템-구조-개요-및-설계-원칙)
3. [S1 — Contact-Rich DRL 핵심 차별점](#13-s1--contact-rich-drl-핵심-차별점)
4. [S2 — VLA Sweep Goal Specification](#14-s2--vla-sweep-goal-specification)
5. [S3 — VLA in-task sensor](#15-s3--vla-in-task-sensor)
6. [S4 — VLA in-task supervisor](#16-s4--vla-in-task-supervisor)
7. [S3 vs S4 — VLA authority 핵심 구분](#17-s3-vs-s4--vla-authority-핵심-구분)
8. [2-phase 학습·배포 분리 구조](#18-2-phase-학습배포-분리-구조)
9. [차별점 종합 및 학술 기여도](#19-차별점-종합-및-학술-기여도)
10. [관련 문서](#관련-문서)

---

## 1.1 기존 연구의 한계

기존 연구의 확인된 구성: DRL 단독 제어(전 구간), stiff joint position control, observation은 시뮬레이터의 ground-truth 절대 좌표 state (privileged state), F/T sensing 부재, 접촉은 물체 속도 기반 간접 감지, target은 코드 내 ID로 지정.

- 한계 1~3: contact sensing·제어·action space의 **성능 한계**
- 한계 4: observation 표현 설계의 **구조적 한계**
- 한계 5: task specification interface의 **기능적 한계**

### 한계 1 — Perception의 vision-based target pose estimation 종속

**[사실]** 기존 시스템에는 physical interaction을 감지하는 sensing modality(F/T, tactile)가 없다. 따라서 환경 상태에 대한 perception 경로는 시각 정보 하나뿐이다. 시뮬 학습에서는 ground-truth object state가 observation으로 주어지는데, 이는 **"오차·지연·occlusion이 없는 이상적 vision perception을 가정한 것과 동등"** 하며, 실기에서 이 observation을 대체할 수단은 vision-based target pose estimation뿐이다.

**[근거]** 이 구조가 contact-rich manipulation에서 position control과 결합될 때 세 가지 성능 한계를 만든다.

1. **Pose estimation error → 접촉력 증폭**: stiff position control에서는 위치 오차가 접촉 강성(contact stiffness)을 통해 접촉력 오차로 직접 증폭된다 (F ≈ k_contact·δx). Vision 기반 pose estimation의 오차 수준은 contact 단계가 요구하는 정밀도를 상회하며, 이를 보정할 feedback channel이 없다.
2. **Self-occlusion**: 접촉 단계에서는 manipulator·gripper에 의한 self-occlusion이 기하학적으로 필연이다. Pose estimate 신뢰도가 가장 필요한 순간(접촉 직전·접촉 중)에 가장 낮아진다.
3. **Perception latency**: vision pipeline의 update rate와 latency는 contact transient의 시간 스케일보다 근본적으로 느려, 접촉 상황 변화를 제어 주기 안에서 반영할 수 없다.

### 한계 2 — Physical interaction sensing의 부재 → contact 안전성·학습 효율 저하

**[사실]** 접촉 감지는 물체 속도 기반의 간접 신호뿐이다 (reward 계산에 object velocity 사용). F/T feedback은 observation에도 제어기에도 없으며, 제어는 stiff joint position control이다.

**[근거 — 역학적]** 물체 속도는 접촉력이 이미 물체를 가속시킨 **뒤에야** 관측되는 lagging indicator다. 접촉력 상승이 속도 변화에 선행하므로, 속도 기반 감지로는 impulse가 가해진 후에만 접촉을 인지할 수 있고, stiff position control은 그 사이의 접촉 충격을 완화하지 못한다. 이 메커니즘은 시뮬레이션의 contact dynamics에서도 동일하게 작동하므로, **sweeping·pushing 시 학습 과정에서도 object toppling이 구조적으로 발생하기 쉽다.**

**[추정]** toppling failure의 빈발은 penalty 위주의 학습 신호와 episode 조기 종료를 만들어 유효한 성공 경험의 수집을 지연시키고, sample efficiency를 저하시켰을 것으로 추정된다. 단, **기존 연구가 최종적으로 선반 전체 랜덤화 sweeping 학습에 성공했음은 확인된 사실**이므로, 이 한계는 "학습 불가"가 아니라 "contact 안전성과 학습 효율의 저하"로 해석해야 한다.

### 한계 3 — Joint-space action space의 implicitness

**[사실]** 기존 action space는 joint space 변위로 정의되어 있다.

**[근거 — 기하학적]** EEF 변위는 δx ≈ J(q)·δq로 사상되고 Jacobian J(q)는 configuration-dependent다. 동일한 joint-space action이 현재 자세에 따라 전혀 다른 방향·크기의 EEF motion을 만들므로, task가 정의되는 Cartesian space 관점에서 joint-space action은 **implicit한 parameterization**이다.

**[근거 — 문헌]** contact-rich manipulation RL에서 EEF-space action이 joint-space action 대비 빠른 수렴과 높은 성공률을 보인다는 비교 실험이 반복적으로 보고되어 있다 (Martín-Martín et al., IROS 2019; Aljalbout et al., 2024).

### 한계 4 — 절대 좌표 기반 observation representation의 구조적 비불변성

**[사실]** 기존 observation은 로봇/월드 기준 **절대 좌표**로 물체·EEF 상태를 표현한다. 동시에, 기존 연구는 선반 영역 전체에 물체 위치를 randomization하여 학습했고 **임의 위치 sweeping을 달성했음이 확인**되어 있다. 따라서 이 한계를 "위치 일반화 불가"로 서술하면 사실과 충돌한다.

**[근거 — 표현론적]** sweeping 과제 자체는 물체가 선반 어디에 있든 동일한 과제, 즉 translation-invariant하다. 그러나 절대 좌표 표현에서는 EEF-물체의 상대 배치가 동일한 상황이 물체 위치마다 **서로 다른 입력 벡터**로 나타난다. Policy는 그 invariance를 데이터(domain randomization)로 근사해야 하며, OOD 위치나 다른 선반 구성에 대한 zero-shot transfer 보장이 없다.

### 한계 5 — 자연어 기반 task specification의 부재

**[사실]** target 지정은 코드 내 object ID 하드코딩으로 이루어진다. 자연어 instruction을 해석하는 경로는 시스템에 존재하지 않는다.

**[판정 — 성격 규정]** 이 항목은 앞의 네 한계와 성격이 다르다. 성능(performance) 저하가 아니라 **capability 부재**이며, 접촉 제어·학습 성능과 독립적인 축이다.

---

## 1.2 시스템 구조 개요 및 설계 원칙

신규 연구는 역할이 명확히 분리된 세 계층으로 구성된다. 시나리오 S1~S4는 계층 구조를 점진적으로 확장한다.

```
[계층 1 — VLA (10~20Hz)]
  Type A (S1/S2): 장면 이해 → sweep goal 결정 → EEF 접근 → handoff 후 종료
  Type B (S3/S4): Type A + contact 중 배경 모니터링 → goal signal 지속 갱신

  VLA 출력 형식 (주의: VLA는 robot action을 출력하지 않음):
    Type A 출력: sweep_direction (3D unit vector) + sweep_distance (float, meter)
    Type B 출력: sweep_remaining (float) + danger_level (float [0,1])
                 + termination_signal (bool) + emergency_stop (bool)

     │ handoff 조건: EEF-물체 distance < 10cm 또는 F/T > 0.3N
     ▼

[계층 2 — DRL Policy (50~100Hz) — vision-free contact reflex]
  observation (S4 기준 전체):
    · joint_pos, joint_vel                    [proprioception, 공통]
    · ee_disp_from_handoff                    [누적 이동량, object-relative frame]
    · F/T 에뮬레이션 + F/T history            [접촉 leading indicator]
    · phase_indicator                          [F/T 크기 기반]
    · [S2~S4] sweep_direction (3D)            [handoff 시 1회, S4에서 mid-task 변경 가능]
    · [S2~S4] sweep_distance (1D)             [handoff 시 1회]
    · [S3~S4] sweep_remaining (1D)            [VLA 10~20Hz, ZOH로 DRL step 사이 홀드]
    · [S3~S4] danger_level (1D)               [VLA 10~20Hz, ZOH로 DRL step 사이 홀드]
  action: EEF Cartesian 변위 [Δx, Δy, Δz, Δroll, Δpitch, Δyaw]
     │
     ▼

[계층 3 — 저수준 제어기 (500Hz)]
  시뮬 (학습): OSC → joint torque           (contact dynamics 물리 정확성)
  실기 (배포): Admittance + DiffIK → joint velocity  (UR5e RTDE 인터페이스)
  [S4 전용] 안전 override: F/T > threshold 또는 VLA emergency_stop
            → DRL bypass, zero velocity 즉각 발동
```

> **VLA 신호와 DRL 주기 불일치 처리 — ZOH (Zero-Order Hold)**:  
> VLA는 10~20Hz로 동작하고 DRL은 50~100Hz로 동작한다.  
> 두 주기 사이에 새 VLA 값이 도착하지 않으면, 마지막 값을 그대로 유지한다 (ZOH).  
> DRL이 stale 신호를 자동으로 감쇄하도록 하기 위해, ZOH 기간을 obs에 추가하는 것이 권장된다.

> **역할 분리 원칙**: VLA는 "무엇을, 어디까지, 주변은 어떤가" (scene-level semantic).  
> DRL은 "지금 어떻게 힘을 가할 것인가" (physical reflex, vision-free).

### 학습·배포 구조 개요

```
[학습 (Phase 1)]              [배포 (Phase 2)]
  1024 envs parallel             단일 로봇
  VLA 없음                       VLA 실행 (10~20Hz)
  GT proxy 신호 + noise DR       실제 VLA 추론 결과
  50Hz × 1024 = 51,200 steps/s  
  → VLA 병렬 추론 불가 (이유: §1.8)
```

---

## 1.3 S1 — Contact-Rich DRL 핵심 차별점

*한계 1~4 해결. VLA: Type A (approach + handoff만). DRL: vision-free contact reflex.*

S1의 네 가지 차별점은 하나의 설계 원칙을 구현한다:  
**"과제의 구조(contact sensing, force compliance, translation invariance)를 외부 조건(domain randomization, 대규모 데이터)이 아니라 시스템 설계에 내장한다."**

---

### 차별점 1 — Vision-free contact reflex: F/T + proprioception 기반 DRL
*(한계 1, 2 해결 — observation 레벨)*

**[채택]** Handoff 이후 DRL은 **vision-free**로 동작한다. Real-time target pose를 observation에서 제거하고, F/T sensing과 proprioception(EEF displacement 누적)으로 contact phase 전구간을 제어한다.

```
DRL observation (contact phase 전구간, vision 없음):
  · ee_disp_from_handoff:  proprioception 누적 EEF 이동량 (object-relative frame)
  · F/T 에뮬레이션:        접촉 상태 leading indicator (500Hz)
  · phase_indicator:       sigmoid(‖F_ext‖ 기반), vision 불필요

Vision 제거 논리 (contact 유지 중):
  ‖F_ext‖ > 0.5N  →  object_pos(t) ≈ initial_pos + ee_disp(t)
  → real-time target pose는 DRL에 새로운 정보를 추가하지 않음
  → vision 포함은 한계 1의 세 문제(occlusion, latency, 오차 증폭)를 구조적으로 유입
```

**[근거 — 한계 1의 세 문제 해결]**

1. **Self-occlusion 회피**: F/T 센서는 카메라 시야와 무관하게 측정된다.
2. **Contact transient 반응 속도**: F/T 센서는 500Hz로 갱신. Vision(10~20Hz)보다 두 자릿수 빠름.
3. **Pose estimation error → 접촉력 증폭 경로 차단**: Admittance control(차별점 2)과 결합 시, F/T 측정값이 admittance 입력이 되므로 오차가 force feedback 루프 안에서 자기조정된다.

**[설계 제약 — F/T observation sim-to-real]**

```
실기 F/T (중력보상 후) = F_contact + F_inertial  (F_inertial = m_gripper × a_EEF)
시뮬 ContactSensor     = F_contact only           ← 물리량 불일치

해결: 시뮬에서 손목 관절 반력 사용
     wrench_b = robot.data.body_incoming_joint_wrench_b[:, wrist_idx, :]
     + 동일 중력보상 적용
     → 시뮬·실기 obs 물리량 일치
```

---

### 차별점 2 — Admittance-based compliant control
*(한계 2 해결 — 제어 레벨; 차별점 1의 dual safety 보완)*

**[채택]** 실기 배포에서 stiff joint position control 대신 **Admittance control + Differential IK**를 저수준 제어기로 채택한다.

```
M·ẍ + D·ẋ + K·x = F_ext    (task space)

F_ext : F/T 센서 측정값 (중력보상 후) [N]
x     : EEF 위치 보정량 (명령 궤적 대비 비켜난 변위) [m]
M, D, K : 가상 질량·댐핑·강성 [kg, N·s/m, N/m]
→ x(t) → DiffIK: q̇ = J⁺·ẋ → UR5e RTDE speedJ (500Hz)
```

**[근거 — Dual safety 구조]**

| 계층 | 동작 | 역할 |
|---|---|---|
| DRL policy (50~100Hz) | F/T obs 기반 학습된 행동 결정 | "지금 어떻게 힘을 가할까" |
| Admittance control (500Hz) | F_ext에 비례하여 EEF 물리적으로 비켜줌 | Policy reaction time 이전에 작동하는 안전 버퍼 |

**[근거 — UR5e 제약]** UR5e는 사용자 레벨 joint torque 인터페이스를 제공하지 않는다. 시뮬(OSC)과 실기(Admittance+DiffIK)의 **의도적 비대칭** 구조이며, (M, D, K) 파라미터 식별로 두 제어기의 EEF step force 응답 특성을 일치시켜 sim-to-real을 달성한다.

---

### 차별점 3 — EEF Cartesian action space
*(한계 3 해결)*

**[채택]** DRL policy의 action은 **EEF Cartesian 변위 [Δx, Δy, Δz, Δroll, Δpitch, Δyaw]** 로 정의한다.

```
joint-space action (기존):  δx = J(q)·δq  →  q가 달라지면 같은 δq가 다른 δx
Cartesian action (신규):    δx 자체를 action으로 정의  →  q에 무관하게 의미 고정
```

---

### 차별점 4 — Object-relative observation representation
*(한계 4 해결)*

**[채택]** DRL policy observation에서 EEF 및 target 물체의 상태를 **물체(target object) 기준 상대 좌표계**로 표현한다.

```python
ee_pos_rel, ee_quat_rel = subtract_frame_transforms(
    target_pos_w, target_quat_w,   # 물체 위치·방향 (변환 원점·기준)
    ee_pos_w,     ee_quat_w        # EEF 위치·방향 (월드 기준 입력)
)
```

```
절대 좌표 obs (기존):    EEF–물체 상대 배치가 동일해도 물체 위치마다 obs 벡터가 다름
                          → policy가 동일 과제를 위치별로 별개 학습 (empirical 일반화)

object-relative obs (신규): 상대 배치가 같으면 obs 벡터가 동일 (물체 위치 무관)
                              → 하나의 policy 매핑이 모든 위치에 이론적으로 적용
                              → OOD 위치에서도 이론적 보장 (reachability 내)
```

---

## 1.4 S2 — VLA Sweep Goal Specification

*한계 5 해결 (capability 부재 → language-conditioned goal 가능). VLA: Type A + sweep_goal 결정·전달. DRL: goal-conditioned.*

### 차별점 5-A — Language-conditioned sweep goal via VLA
*(한계 5 해결)*

**[채택]** 자연어 instruction을 입력으로 받는 VLA를 시스템 최상위 계층으로 통합한다. S2에서 VLA는 handoff 전에 장면 전체를 이해하고 sweep goal을 결정한 뒤, handoff 시 DRL에 **1회 전달 후 종료**한다.

```
사용자: "선반 위 노란색 컵을 오른쪽으로 치워줘"
   ↓
[VLA — handoff 전]:
  이미지 + instruction → target 식별 → 주변 물체 배치 이해
  → sweep_goal { direction: 3D unit vector, distance: float [m] } 결정
  → EEF 접근 → handoff 1회 전달 후 종료

[DRL]: F/T + proprioception + sweep_goal → contact reflex 실행
  sweep_remaining_est = sweep_goal.distance - dot(ee_disp, sweep_direction)
  (proprioception 기반 자체 추산, VLA 지속 갱신 없음)
```

**[핵심 — goal-conditioned policy]** S2의 DRL은 sweep_direction과 sweep_distance를 obs로 받으므로, 동일하게 학습된 policy로 handoff 시 다른 방향/거리를 지정하면 그 목표를 따른다. 추가 학습 없이 배포 시 방향·거리를 자유롭게 지정할 수 있다.

**[역할 분리]**

| | 역할 | 입력 |
|---|---|---|
| VLA | "무엇을, 어느 방향으로, 얼마나" (semantic) | 이미지 + 자연어 |
| DRL | "지금 어떻게 힘을 가할 것인가" (physical reflex) | F/T + proprioception + sweep_goal |

---

## 1.5 S3 — VLA in-task sensor

*실행 정확도·안전성 향상. 한계 5는 S2에서 이미 해결됨 (S3의 기여와 혼동 금지).*  
*VLA: Type B — **정보 제공자(sensor)**. DRL: 제공된 obs를 보고 **자율적으로 판단·행동**.*

### 차별점 5-B — VLA scene monitoring: sweep_remaining + danger_level 실시간 공급
*(실행 정확도·안전성 향상; 한계 1·2 보완)*

**[채택]** S2에서 handoff 후 종료되던 VLA가 S3에서는 contact 중에도 배경에서 지속 동작(10~20Hz)하며, vision-corrected sweep_remaining과 danger_level을 DRL에 실시간으로 공급한다.

```
[VLA — contact 중 배경 모니터링 (10~20Hz 지속)]:
  · target 물체 위치 추적 (vision) → swept_distance_estimate 갱신
  · 주변 물체와 target의 간격 추적 → danger_level [0, 1] 계산
  · sweep_remaining = sweep_goal.distance - swept_distance_estimate

  VLA 출력 Type B:
    sweep_remaining  : float (meter)
    danger_level     : float [0, 1]  (1 = 위험, 주변 물체 충돌 임박)
    termination_signal : bool
    emergency_stop   : bool

→ ZOH로 DRL step (50~100Hz) 사이 유지
→ DRL obs: sweep_remaining + danger_level 추가 (S2 대비 +2D)
```

**[S3의 기여 명확화]**

S3가 기여하는 것은 **실행 정확도와 주변 물체 안전성**이다. 한계 5(자연어 지정 부재)는 S2에서 이미 해결되었다.

| S2 한계 (S3가 해결하는 것) | S3의 해결 방법 |
|---|---|
| sweep_remaining 추정 오차 (proprioception drift) | VLA vision-corrected 값으로 대체 |
| 주변 물체 위험 대응 지연 | danger_level obs → DRL 직접 반응 (reward 패널티보다 빠름) |
| 종료 지점 정확도 저하 | VLA가 실제 물체 변위 기반으로 termination_signal 발동 |

**[S3 작동 원리 — DRL 자율성 유지]**

S3에서 danger_level이 0.9가 되었을 때 DRL이 속도를 줄이는 것은 VLA의 명령이 아니다.  
DRL policy가 학습을 통해 `danger_level=0.9` obs에 "속도 감소"가 최적 반응임을 학습한 것이다.  
**의사결정 주체는 항상 DRL이다.**

**[S2 vs S3 비교]**

| | S2 (Type A) | S3 (Type B, sensor) |
|---|---|---|
| sweep_remaining 추정 | proprioception 누적 (contact slip → drift 가능) | VLA vision-corrected (실제 물체 변위) |
| 주변 물체 위험 대응 | reward 패널티만 (사후 반응) | danger_level obs → DRL 사전 반응 |
| 종료 정확도 | proprioception 오차 누적 | VLA 추정 정확도 한계 내 |
| sweep_direction 변경 | 불가 (handoff 후 고정) | 불가 (고정 유지) |
| 의사결정 주체 | DRL | DRL (변경 없음) |

---

## 1.6 S4 — VLA in-task supervisor

*동적 장면 변화 대응.*  
*VLA: Type B — **감독자(supervisor)**, 목표 직접 변경·action override 권한.*  
*DRL: VLA 명령에 따라 목표를 추종하거나 즉각 정지.*

### 차별점 5-C — Mid-task VLA intervention: 방향·거리 변경 및 긴급 정지
*(동적 장면 변화 대응 확장)*

**[채택]** S3에서 goal이 handoff 후 고정되던 것에서, S4에서는 VLA가 contact 중 방향·거리를 변경하거나 긴급 정지를 발동할 수 있다.

```
S4 개입 유형별 메커니즘:

[Mechanism A — Hard bypass (긴급 정지)]:
  1차: F/T > threshold (500Hz, ~2ms)   → DRL bypass, zero velocity
  2차: VLA emergency_stop (10~20Hz)    → vision 기반 위험 감지, DRL bypass

[Mechanism B — Soft intervention (목표 변경)]:
  방향 변경:
    VLA → sweep_direction obs 갱신 (10~20Hz)
    DRL → 다음 step에서 새 direction obs 수신 후 행동 조정
    Admittance compliance → 방향 전환의 급격함 물리적 완충

  거리 변경:
    VLA → sweep_remaining 조기 0 설정 또는 단축 갱신
    DRL → 목표 달성으로 인식 후 자연 종료
```

**[S4 안전 계층구조]**

| 계층 | 응답 속도 | 역할 |
|---|---|---|
| F/T threshold (500Hz) | ~2ms | 가장 빠른 물리 안전장치 |
| VLA emergency_stop (10~20Hz) | ~50~100ms | vision 기반 비접촉 위험 감지 |
| VLA danger_level → DRL obs | ~50~100ms | 사전 예방적 반응 |
| VLA goal update (10~20Hz) | ~50~100ms | 정상 범위 내 목표 재설정 |

**[S4 학습 추가 DR]** Soft intervention이 실기에서 효과적으로 작동하려면, 시뮬 학습 중에도 goal이 mid-episode에서 변하는 경험이 필요하다.

```
시뮬 S4 추가 DR (mid-episode goal change):
  · sweep_direction 변경 (일정 확률로 발생)
  · sweep_remaining 단축 (장애물 갑자기 출현 모사)
  · danger_level 급등·급감 시나리오
```

---

## 1.7 S3 vs S4 — VLA authority 핵심 구분

**S1~S4 구분의 핵심은 VLA의 역할(role)과 의사결정 권한(authority)의 차이다.**

| 관점 | S3 (Type B, in-task **sensor**) | S4 (Type B, in-task **supervisor**) |
|---|---|---|
| VLA의 역할 | **정보 제공자** — perception 신호 공급 | **감독자** — 목표 직접 변경·action override |
| 의사결정 주체 | **DRL** (obs를 보고 스스로 판단·행동) | **VLA** (방향 변경 명령, DRL은 추종·정지) |
| sweep_direction 변경 | 불가 (handoff 후 고정) | 가능 (mid-task, VLA가 직접 변경) |
| danger_level 대응 | DRL policy가 학습된 반응으로 자율 조정 | VLA가 emergency_stop 발동 → DRL bypass |
| DRL 자율성 | **완전 유지** | **제한** (VLA 명령 우선) |
| S3/S4 설계 질문 | VLA perception이 실행 정확도를 높이는가? | VLA supervision이 동적 변화에 대응하는가? |

### S1~S4 체계 요약

```
S1: 핵심 DRL 차별점 (F/T obs + Admittance + Cartesian action + object-relative obs)
    VLA: Type A 기본 (approach + handoff)
     ↓ 누적
S2: + Language-conditioned sweep goal
    VLA: Type A (handoff 시 sweep_goal 결정·전달, 이후 종료)
    기여: 한계 5 해결 (자연어 지정 + goal-conditioned policy)
     ↓ 누적
S3: + VLA in-task perception (contact 중 지속 모니터링)
    VLA: Type B, sensor — sweep_remaining + danger_level 공급
    기여: 실행 정확도·안전성 향상 (한계 5 완전 해결 아님, S2에서 이미 해결)
     ↓ 누적
S4: + VLA in-task control (mid-task goal override + hard bypass)
    VLA: Type B, supervisor — sweep_direction 변경 + emergency_stop 권한
    기여: 동적 장면 변화 대응 (예상치 못한 장애물, 목표 변경)
```

---

## 1.8 2-phase 학습·배포 분리 구조

**이 제약은 S3/S4 전체 설계의 핵심 전제다.**

### 왜 VLA를 학습 중 직접 사용할 수 없는가

S3/S4에서 VLA가 10~20Hz로 sweep_remaining·danger_level을 공급한다고 하면, 다음 의문이 생긴다:  
**"DRL 학습 시 vectorized env에서 VLA를 직접 실행하면 되지 않는가?"**

```
계산:
  vectorized env 수:  1024개 (표준 on-policy PPO 설정)
  DRL step rate:      50Hz
  필요 VLA 추론 수:   1024 × 50 = 51,200 inferences/sec

실제 VLA 처리 능력:
  Octo-Small (93M):   최대 30Hz, single sample
  Qwen2.5-VL-3B:      최대 5~10Hz, single sample

결론: 현존 최경량 VLA도 51,200 inferences/sec 불가.
      수백~수천 GPU 필요 → 비현실적.
```

### 2-phase 분리 설계

```
[Phase 1 — DRL 학습 (시뮬)]
  환경: Isaac Lab, 1024 parallel envs, 50Hz
  VLA: 없음 (실행 안 함)
  sweep_remaining 대체: GT 해석적 계산
    sweep_remaining_gt = sweep_goal.dist - dot(obj_pos_delta, sweep_dir)
  danger_level 대체: GT 해석적 계산
    danger_level_gt = max(0, 1 - (clearance - min_safe) / (max_safe - min_safe))
  Noise DR: σ_r (remaining), σ_d (danger) 추가
    → policy가 VLA 추정 오차에 robust하게 학습
  목적: contact reflex policy 학습 + VLA 신호 오차에 대한 robustness

[Phase 2 — 배포 (실기, 단일 로봇)]
  환경: 실제 UR5e
  VLA: 실행 (10~20Hz)
  DRL: Phase 1에서 학습된 policy 그대로 사용
  ZOH: VLA 값 step 사이 홀드
  목적: 학습된 policy로 실제 VLA 신호에 반응
```

### 2-phase 분리의 sim-to-real 리스크 및 완화

```
리스크: GT_proxy + Gaussian ≠ VLA structural errors
  · VLA는 Gaussian이 아닌 편향 오차 가질 수 있음 (특정 각도 추정 약점)
  · GT proxy는 물체 완전 가시성 가정 → occlusion 시 오차 패턴 다름

완화 방법:
  · σ_r, σ_d 교정: 사전 실기 VLA 실행 → 오차 분포 측정 → DR 파라미터 업데이트
  · 오차 분포 비대칭 확인 시: uniform noise, t-분포 noise 등 DR 형태 확장
  · Worst-case DR: σ_r·, σ_d 상한에서 policy 동작 확인
```

### VLA fine-tuning 파이프라인 (독립)

VLA fine-tuning은 DRL 학습과 완전히 독립적인 파이프라인이다.

```
VLA fine-tuning 파이프라인:
  데이터: Isaac Sim 시뮬레이션 (이미지 + GT 레이블)
  레이블 생성: 동일 GT 해석적 계산으로 자동 생성
  학습: 지도학습 (image → float values)
    Type A: image → (sweep_direction 3D, sweep_distance 1D)
    Type B: image → (sweep_remaining, danger_level)
  방법: LoRA fine-tuning (W = W_0 + BA, rank r=8~32)
  권장 모델: Octo-Small (93M, Type B 실시간 가능)
```

---

## 1.9 차별점 종합 및 학술 기여도

### 한계·차별점·시나리오 매핑

| §1.1 한계 | 차별점 | 활성화 시나리오 | 해결 계층 |
|---|---|---|---|
| 한계 1 — vision perception 종속 | 차별점 1 (vision-free F/T obs) | **S1** | observation |
| 한계 2 — F/T sensing 부재 | 차별점 1 (obs) + 차별점 2 (Admittance) | **S1** | observation + control |
| 한계 3 — joint-space action | 차별점 3 (EEF Cartesian action) | **S1** | action space |
| 한계 4 — 절대 좌표 obs | 차별점 4 (object-relative obs) | **S1** | observation |
| 한계 5 — 자연어 지정 부재 | 차별점 5-A (VLA sweep goal at handoff) | **S2** | 계층 추가 |
| 실행 정확도·안전성 향상 | 차별점 5-B (VLA in-task sensor) | **S3** | obs 보강 (DRL 자율 판단 유지) |
| 동적 장면 변화 대응 | 차별점 5-C (VLA in-task supervisor) | **S4** | 목표 override + hard bypass |

### Policy Network 입출력 개요

| 시나리오 | obs 차원 | 핵심 추가 obs |
|---|---|---|
| S1 | ~57D | F/T (6D), ee_disp (6D), phase_indicator |
| S2 | ~61D | + sweep_direction (3D), sweep_distance (1D) |
| S3 | ~63D | + sweep_remaining (1D), danger_level (1D) |
| S4 | ~63D | sweep_direction이 dynamic (mid-task 변경 가능) |

전체 공통 출력: EEF Cartesian 변위 [Δx, Δy, Δz, Δroll, Δpitch, Δyaw] (6D)

### 학술 포지셔닝

```
                  Force/Admittance 제어 수준
                       높음
                        │
  [S3~S4 목표] ★        │  Variable Impedance RL (단일 task, VLA 없음)
                        │
──────────────────────────────────────────────── 자연어 지시 통합 수준
낮음                    │                          높음
  [S1~S2 목표] ★        │  SayCan / RT-2 / π0  (VLA, F/T 제어 없음)
                        │
  기존 제자 연구 ☆       │
  (DRL + position ctrl)  │
  Factory/AnyPeg ☆      │
  (Contact-rich RL)    낮음
```

**미개척 공간**: F/T 기반 contact 제어 × 자연어 지시 × Admittance compliant control의 통합.  
이 영역은 현재 학술적으로 공백이며, 본 연구가 S1(F/T·Admittance 축)부터 S2~S4(언어 지시 축)를 순차적으로 채운다.

### 연구 기여 및 권장 목표

| 시나리오 | 핵심 기여 | 권장 | 근거 |
|---|---|---|---|
| S1 | F/T obs + Admittance + Cartesian action + object-relative obs | **필수** | 핵심 기여 검증. 단독 논문 성립 |
| S2 | 언어 지시 기반 임의 방향·거리 sweeping (goal-conditioned DRL) | **목표** | 한계 5 해결. S1 후 1~2개월 |
| S3 | VLA scene monitoring → 종료 정확도·주변 물체 안전성 향상 | 가능 시 | S2 후 1~2개월, 시스템 통합 난이도 도약 |
| S4 | Mid-task VLA intervention → 예상치 못한 장애물 적응 | 선택 | 후속 논문 후보 |

---

## 관련 문서

| 문서 | 내용 |
|---|---|
| [docs_r3/01-0](01-0_overview.md) | 차별점 개요 (기여도·난이도 계층, 포지셔닝 요약) |
| [docs_r3/01-1](01-1_obs_vla_design.md) | VLA Type A/B 설계 분석, obs 공간 상세, ZOH, mid-task 개입 메커니즘 |
| [docs_r3/01-2](01-2_scenario_analysis.md) | S1~S4 기술 요구사항·난이도·ablation 상세 |
| [docs_r3/01-3](01-3_drl_setup_strategy.md) | DRL 학습 전략, 2-phase 구조, DR 설계 |
| [docs_r3/01-4](01-4_reward_isaaclab_setup.md) | Reward 함수 설계, Isaac Lab 설정, F/T 에뮬레이션 코드 |
| [docs_r3/01-5](01-5_network_architecture.md) | S1~S4 policy network 아키텍처 다이어그램 |
| [docs_r3/01-6](01-6_vla_model_candidates.md) | VLA 모델 후보군, GPU 사양, HuggingFace 링크 |
| [docs_r3/01-7](01-7_vla_finetuning_basics.md) | VLA fine-tuning 기초 (초심자용), LoRA 설명 |
| [docs_r3/01-8](01-8_vla_finetuning_scenario.md) | 시나리오별 VLA fine-tuning 전략 |
