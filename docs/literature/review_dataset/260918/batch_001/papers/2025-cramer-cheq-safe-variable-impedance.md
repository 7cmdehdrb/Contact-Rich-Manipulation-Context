# CHEQ-ing the Box: Safe Variable Impedance Learning for Robotic Polishing

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B013`
- Authors: Emma Cramer; Lukas Jäschke; Sebastian Trimpe
- Year: 2025
- Venue: Not stated
- DOI / arXiv: 미명시 / 2501.07985v1
- PDF version: arXiv:2501.07985v1 [cs.RO], 14 January 2025. PDF 첫 페이지에 arXiv version/date 표시. Venue/DOI는 원문에서 확인되지 않음. Appendix A–C가 같은 PDF에 포함되어 있다. 선택된 배치 안에서 동일 논문의 다른 파일은 확인되지 않았다.
- Page count: 12
- SHA-256: `c961295d97a000d866506cb4cd6c8dd0831a2bbb3e4e8c44dfa8c8e5f33be235`
- PDF filename: `Cramer 등 - 2025 - CHEQ-ing the Box Safe Variable Impedance Learning for Robotic Polishing.pdf`
- 읽은 범위: PDF pp.1–12 전체: 본문·참고문헌·Appendix A (details), B (simulation), C (hardware). State/control diagram p.3, 결과 p.5, appendix 결과 p.12를 렌더링으로 확인.
- 근거 원칙: 이번 배치의 해당 PDF에서 새로 추출했다. 기존 상세 노트와 외부 보충자료는 사실 근거로 사용하지 않았다. 아래 페이지는 PDF의 1-based page다.

## 2. Relevance to This Review

**Relevant**. 시각 없이 force와 proprioception으로 polishing을 수행하는 variable-impedance RL 연구다. 그러나 알려진 workpiece 위의 reference path와 nominal controller를 사용하므로, pose 없는 manipulation을 성립시키는 geometry/task prior를 구체적으로 분석할 수 있다. Force input, critic ensemble, runtime controller mixing, reward와 safety termination을 분리할 수 있으며 tactile 병용의 근거는 제공하지 않는다.

Screening 근거: Title/Abstract/§1, PDF pp.1–2; §3–4.2, pp.3–4; Fig.1–2.

## 3. Task

7-DoF Franka Panda에 non-rotating polishing tool을 장착하고, 3D-printed curved bridge workpiece 위의 지정 경로를 따라 polishing한다. 경로는 7개 via-points로 주어지며 normal force와 translational velocity를 일정하게 유지하는 것이 목표다. Simulation 비교의 목표는 5 N, 0.05 m/s다. 실제 material removal의 직접 측정이 아니라 force·velocity·path tracking을 평가한다. 모든 via-point를 따라 작업하고 force/pose/velocity 안전 조건을 지키는 것을 task 진행과 성공의 기준으로 사용한다. (§3, p.3; §5.1, p.4; Appendix A.3–A.4, pp.8–10)

## 4. Method

### 4.1. Overall Pipeline

Robot joint/EEF state + 3D contact force + known next-path-point errors → CHEQ/SAC policy → pose increment + impedance gains. 별도로 known path를 따르는 nominal controller가 같은 형식의 action을 만든다. Critic ensemble uncertainty가 mixing weight를 정하고 두 action을 섞는다. Mixed action → Cartesian impedance controller → joint torques. (Fig.2; §4, pp.3–4)

$a_t^{ref}=(1-\lambda_t^{RL})a_t^{prior}+\lambda_t^{RL}a_t^{RL}$이다. Nominal prior와 learned policy는 함께 실행되며 prior가 학습 때만 사용하는 보조 GT가 아니다. (§4.2, p.4)

### 4.2. Observation

명시된 base state는 $s_t^{RL}=(q_t,\cos q_t,\sin q_t,\dot q_t,\tilde p_t,\dot{\tilde p}_t,F_t,\Delta r_t^{path})\in\mathbb{R}^{74}$이다. EEF pose는 Cartesian position+quaternion, force는 $F_t\in\mathbb{R}^{3}$, path feature는 다음 5개 point에 대한 position/velocity errors $\Delta r^{path}\in\mathbb{R}^{5\times6}$다. Vision, tactile, 현재 workpiece pose는 포함하지 않는다. (§4.2, p.3)

CHEQ 설명에는 mixing weight context와 이에 조건화한 critic이 등장한다. Critic 입력은 $z=(s^{RL},a^{RL},\lambda^{RL})$로 명시된다. Base 74D state와 mixing context를 구분하며, 본문에 없는 actor concatenation 구현 세부/추가 GT state를 만들지 않는다. (§2, p.2; §4.2, p.4)

IC는 robot kinematics/dynamics, current EEF state와 mixed reference를 사용한다. Nominal controller는 known path의 다음 점 및 fixed gains를 사용한다. (§4.1–4.2, pp.3–4)

### 4.3. Action

$a_t^{RL}=(\Delta p_t^{RL},K_t,\zeta_t)$이며 6개 diagonal stiffness와 scalar damping factor로 impedance를 정한다. $D=2\zeta\sqrt K$다. Nominal controller도 pose increment, fixed $K^{prior},\zeta^{prior}$를 출력한다. Action은 joint torque를 직접 내는 것이 아니라 impedance reference와 gain을 정한다. (§4.1–4.2, pp.3–4)

### 4.4. Controller

Mass-spring-damper 형태에서 $M=0$, desired velocity=0으로 두고 pose error와 damping을 Jacobian transpose로 joint torques에 매핑한다. Null-space torque, Coriolis/centrifugal term과 gravity compensation을 더한다. Known surface path의 position은 interpolation, orientation은 SLERP로 구성한다. Current robot에서 predefined radius 안의 가장 먼 path point를 reference로 선택하며 tool indentation offset을 사용한다. (§4.1–4.2, pp.3–4; Appendix A.2, pp.7–8)

### 4.5. Learning / Optimization Method

CHEQ는 SAC와 critic ensemble로 구성된 adaptive hybrid RL이다. Ensemble uncertainty가 낮을 때 learned policy에 더 많은 control weight를 주고, 높으면 nominal prior 의존도를 높인다. Simulation은 10 runs로 safe SAC/unsafe SAC와 비교한다. Hardware는 실제 장비에서 학습하고 actor/learner를 분리한다. Simulation control frequency 50 Hz, hardware 20 Hz, hardware waiting time 0.033 s를 사용한다. (§4.2–6, pp.3–6; Appendix C, p.11)

Reward는 known reference path의 parallel/perpendicular error, movement direction, velocity, measured force와 target의 오차를 합하고 endpoint bonus/constraint violation penalty를 추가한다. No-force ablation은 없다. (§4.2, p.3; Appendix A.3, pp.8–9)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | 실행 중 workpiece current position 추정/추적 없음 | 없음 | 고정 workpiece 위의 7개 waypoint는 reference geometry이며 Initial object pose 측정 또는 current object tracking이라고 명시하지 않는다. 근거: §3–4.2, pp.3–4; Appendix A.2, pp.7–8 |
| Orientation | 미제공 | Current workpiece orientation 입력 없음 | 없음 | Controller reference orientation과 로봇 orientation을 현재 물체 orientation으로 기록하지 않는다. 근거: §4.1–4.2, pp.3–4; Appendix A.2, pp.7–8 |
| Shape / Geometry | 기타 | Surface를 따른 7개 predefined via-points 및 path directions/orientations; tool indentation offset | Reference는 고정; next-point errors는 로봇 위치에 따라 갱신 | 제한된 known path geometry. Full mesh/CAD를 actor runtime에 주는지 미명시이며 reference path 제공을 전체 형상 tracking으로 세지 않는다. 근거: §3–4.2, pp.3–4; Appendix A.2, pp.7–8 |
| Physical Parameters | 미제공 | Actor object mass/friction/stiffness 수치 입력 없음 | 없음 | Low friction, constant contact area, tool normal alignment는 물리 가정. Robot model/gain은 controller 정보이며 object 물성 관측이 아니다. 근거: §3–4.2, p.3; Appendix A.1–A.2, pp.7–8 |

이 논문은 object pose를 관측하지 않는 대신 known surface path를 제공한다. 미제공 current pose와 known task geometry를 함께 기록해야 하며, 고정 geometry를 Tracking 또는 Initial pose measurement로 바꾸어 세지 않는다.

## 6. Missing Object Information and Compensation

Current workpiece pose와 full shape의 online 관측 없음 → known surface reference path/SLERP orientation + nominal controller + indentation offset → 실행할 task geometry와 motion direction을 미리 지정한다. 이는 unknown-geometry contact exploration이 아니다. (§3–4.2, pp.3–4; Appendix A.2, pp.7–8)

고정 impedance로 curved surface에서 일정한 force/velocity 유지가 어려움 → contact force + robot state + known path errors → policy가 pose와 impedance를 조정한다. 이 역할은 variable-gain 비교로 뒷받침되지만 force input 제거 실험으로 분리하지 않았다. (§5.1, p.4; Fig.3, p.5)

Exploration 시 learned action의 불확실성 → Q ensemble uncertainty + nominal prior → control weight를 조정한다. 이것은 tactile 정보를 대체하는 modality가 아니라 execution controller 선택 구조다. (§4.2, p.4)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음.

### 7.2. Preprocessing

해당 없음.

### 7.3. Policy Representation

해당 없음.

### 7.4. Retained Information

해당 없음.

### 7.5. Removed / Unavailable Information

해당 없음. 10-step average는 critic uncertainty를 부드럽게 만드는 방법이며 tactile/sensor observation stack이 아니다. (§4.2, p.3; Appendix C, p.11)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

원문은 contact force를 force-torque sensor로 측정한다고 설명한다. Sensor model, 정확한 mount 위치, joint-torque estimation 여부는 명시하지 않으므로 wrist 6-axis F/T로 자동 분류하지 않는다. (§4.2, p.3; Appendix C, p.11)

### 8.2. Representation

Actor state는 $F_t\in\mathbb{R}^{3}$다. F/T hardware가 존재한다고 6D wrench 전체를 actor에 넣는다고 쓰지 않는다. Force norm은 reward와 safety bound에 사용하며 hardware의 drift/motion noise에 cutoff 35 Hz low-pass를 적용한다. (§4.2, p.3; Appendix A.3–A.4, pp.8–9; Appendix C, p.11)

### 8.3. Role

Force는 policy observation, force-tracking reward, safety truncation, evaluation에 쓰인다. Low-level IC는 pose error/gains를 torque로 바꾼다. 목표 force를 맞추기 위한 정책과 gain 조정 역할이며 contact location estimator는 아니다. (§4.1–4.2, p.3; Appendix A.3–A.4, pp.8–9)

### 8.4. Required Assumptions

Reference path가 workpiece surface 위에 알려져 있고 tool orientation을 정한다. Indentation offset은 tool geometry와 reference 사이의 관계를 제공한다. Non-rotating tool, 작은 force 변화로 근사한 constant contact area, low friction으로 force norm을 normal force에 대응시키는 가정을 사용한다. Robot kinematics/dynamics는 IC에 필요하다. 따라서 성공 조건을 F/T만으로 unknown geometry를 알아낸 결과로 설명하면 안 된다. (§3–4.1, p.3; Appendix A.1–A.3, pp.7–8)

### 8.5. Reported Limitation / Ambiguity

Hardware에서 drift와 motion-dependent sensor noise를 보고한다. 낮은 control frequency와 gain chattering이 force 측정/학습을 어렵게 만든다고 설명한다. Net wrench의 multi-contact/contact-patch/locality ambiguity는 원문에서 직접 논의하지 않는다. (Appendix C, p.11)

## 9. Other Observations

- Proprioception: joint positions/cosines/sines/velocities, EEF pose/velocity. Controller 모델과 policy state를 구분한다.
- Vision: 사용하지 않음.
- Goal / geometry: 7 predefined via-points의 reference path와 다음 5개 point에 대한 robot errors. Current workpiece pose가 아니다.
- History: raw force/pose history stack은 미명시. Hardware mixing uncertainty만 10 steps 평균한다.
- Previous Action / recurrent state: explicit policy input은 미명시.
- State Estimator: Q ensemble uncertainty estimator. Object pose/contact location estimator는 제시하지 않는다.

근거: §4.1–4.2, pp.3–4; Appendix C, p.11.

## 10. Tactile–Other Modality Relationship

Tactile를 사용하지 않으므로 tactile–F/T 상보성에 대한 직접 결론은 없다.

| 추가 정보 | F/T의 정보 | F/T 외 정보의 역할 | 근거 |
| --- | --- | --- | --- |
| Robot proprioception | 현재 3D contact force | EEF/joint state와 motion context | §4.2, p.3 |
| Known reference path | Force는 목표 경로나 surface geometry를 직접 주지 않음 | Desired motion과 path error 계산 | §4.2, pp.3–4; Appendix A.2, pp.7–8 |
| Nominal controller | Force 변화에 반응할 필요 | 안전한 방향의 탐색과 initial prior | §4.2–5.2, p.4 |
| Critic uncertainty | F/T 센서값과 별개 | Learned/nominal action의 mixing weight | §4.2, p.4 |

이 관계는 명시적 state/controller 구조다. Force와 geometry input을 각각 제거해 필요성을 정량 비교한 것은 아니다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 | 비고 |
| --- | --- | --- | --- | --- |
| Actor | Hidden object GT 사용은 명시되지 않음 | 74D base state: q/cosq/sinq/qdot; EEF pose/velocity; F∈R3; next-five-reference-path-point errors. CHEQ mixing weight context 별도 | Yes: robot state, measured force, known path and mixing context | 현재 object GT 대신 known goal path가 존재. Simulation에서 각 관측을 읽는 API/실측오차 모델 세부는 미명시. 근거: §2, p.2; §4.2, pp.3–4 |
| Critic | Asymmetric additional GT 미명시 | Q ensemble은 z=(sRL,aRL,λRL)에 조건화. 추가 object GT 입력은 제시하지 않음 | Yes: ensemble uncertainty가 실행 중 λ를 결정 | 단순 training-only critic으로 분류하지 않는다. Critic predictions의 불확실성으로 nominal/RL control authority를 조정한다. 근거: §4.2, p.4; Fig.2b |
| Reward | Hidden current object GT는 확인되지 않음 | Known path와 robot current position/velocity의 오차; force norm과 목표 force의 오차; terminal/truncation term | 학습 필요; hardware online training에 sensor/robot state와 reference 필요 | 시뮬레이션 reward 관측 API는 미명시. Material removal 실제 측정 GT를 reward로 쓰지 않는다. 근거: §4.2, p.3; Appendix A.3, pp.8–9 |
| Termination | Hidden current object GT는 확인되지 않음 | Robot EEF position/orientation/velocity, contact-force constraints; last-via-point completion; horizon | Yes: safety truncation와 task completion | Workpiece pose GT tracking과 다르다. Main text acceleration 제한도 언급하나 Appendix의 상세 구현에서 별도 정의는 확인되지 않음. 근거: §5.2, p.4; Appendix A.4, pp.9–10; Table A.4 |
| Curriculum | Object-GT curriculum 미명시 | Ensemble uncertainty→mixing weight λ; conservative hardware uncertainty bounds | Yes: λ 조정은 online controller 일부 | Known nominal path prior를 사용. 최초 random sampling과 λ 범위 설정이 있지만 object GT를 이용한 curriculum은 명시하지 않음. 근거: §4.2, p.4; Appendix A.5, p.10; Appendix C, p.11 |

Critic ensemble은 training 때 Q를 학습하는 동시에 runtime uncertainty/λ 계산에도 사용한다. 따라서 critic을 실행에 불필요한 privileged module로 일괄 분류하지 않는다. Reference path는 actor/controller/reward에서 공통으로 알려진 정보이며 hidden current object GT와 다르다. Simulator가 물리 상태를 내부적으로 가진다는 일반론만으로 추가 actor/critic GT를 추정하지 않는다.

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Curved-path polishing에서 variable impedance의 효과 | Controlled comparison | Untuned fixed gains vs BO-tuned fixed gains vs five-section-specific tuned gains | Section-wise gains는 steep curvature 구간에서 force/velocity error를 줄인다. F/T 센서 제거 또는 tactile 결합 ablation이 아니다. | §5.1, PDF p.4; Fig.3, p.5 |
| CHEQ가 safety-constrained exploration과 performance를 함께 개선 | Controlled comparison; Failure analysis | CHEQ vs safe SAC vs unsafe SAC; simulation 10 runs; same task, different safety/prior mixing conditions | 2.5M steps mean failures CHEQ 56.2±5.6, safe SAC 3237.4±285.3, unsafe SAC 6631.7±98.9. Unsafe SAC는 episode당 첫 violation만 집계하므로 실제 violation은 더 많다. | §5.2, PDF pp.4–5; Fig.4 |
| Hardware에서 nominal prior 위에 learned residual/VIC를 학습 | Controlled comparison; Failure analysis | Hardware training progression and nominal controller comparison; simulation-to-real direct transfer 아님 | 250k steps/8h 시점 5 failures 보고. λ 약 0.2에서도 개선. Appendix의 1M-step 추가 학습에서는 더 높은 λ에도 polishing return이 더 개선되지 않는다. | §6, PDF pp.5–6; Fig.5; Appendix C, pp.11–12, Fig.C.1 |
| Noise filter와 uncertainty smoothing의 hardware 필요성 | Author explanation only; Failure analysis | Force sensor drift/motion noise, gain chattering에 대한 관찰; 별도 removal ablation 미제공 | 35 Hz low-pass, 10-step uncertainty averaging, conservative mixing curriculum으로 안정화했다고 설명. 각 장치의 독립 성능 기여는 정량 분리하지 않음. | Appendix C, PDF p.11 |
| F/T input 자체의 필요성 및 known geometry 의존성 | No supporting evidence (sensor ablation); Author explanation only | F/T/waypoint removal 비교 없음; 모든 주요 방법에서 task-specific reference/control setup 사용 | Force/geometry의 역할은 state/reward/controller 구조에서 확인되지만 force-free policy 또는 unknown-geometry control보다 우수하다는 비교는 없다. | §3–5, PDF pp.3–5; Appendix A, pp.7–10 |

본문의 큰 자릿수 개선 표현을 일반화하지 않고 보고된 failure 수치를 기록한다. Hardware의 250k-step 보고와 Appendix C의 1M-step 추가 실행은 같은 checkpoint가 아니므로 5회 실패를 전체 장기 실험 수로 쓰지 않는다. Force sensing, smoothing, known geometry 각각의 ablation은 없다.

## 13. Author-stated Limitations

- 방법은 실험적으로 안전한 학습을 보이지만 theoretical safety guarantee가 없다고 명시한다. (§1, p.2)
- Hardware 통신·계산·관측 대기 때문에 simulation의 50 Hz 대신 20 Hz를 선택하며 반응성이 제한된다. (Appendix C, p.11)
- F/T drift/motion noise와 초기 mixing weight 변화에 따른 gain chattering이 학습을 어렵게 만든다. Low-pass filter, 10-step uncertainty averaging, conservative uncertainty bounds로 대응한다. (Appendix C, p.11)
- 보수적 mixing은 더 안정적이지만 curriculum을 느리게 한다. 추가 학습으로 λ는 커져도 polishing behavior는 더 개선되지 않았다고 보고한다. (§6, pp.5–6; Appendix C, pp.11–12)
- Material-removal model은 constant contact area/low-friction 등의 근사에 의존한다. 이는 본문의 물리 모델 가정이며 보편적 polishing 검증으로 확대하지 않는다. (§3, p.3; Appendix A.1, p.7)

## 14. Author-stated Future Work

명시적인 향후 연구 계획은 원문에서 확인되지 않음. §7 Conclusion과 Appendix C를 확인했다. 현재 hardware의 한계나 이 분석자의 제안을 저자의 future work로 바꾸어 기록하지 않는다. (§7, p.6; Appendix C, pp.11–12)

## 15. Review-relevant Findings

- Current workpiece pose와 vision은 actor에 제공하지 않지만 known surface path는 제공한다.
- 74D base state에는 robot proprioception, 3D contact force, next-five-path-point errors가 포함된다.
- F/T sensor의 torque 성분이 actor 입력이라는 근거는 없다.
- Contact locality를 wrench만으로 추정하는 방법이 아니다.
- SAC 기반 policy action은 pose increment와 impedance gains이며 nominal controller와 혼합한다.
- Critic ensemble은 추가 object GT 없이 서술되고 runtime uncertainty 기반 mixing에 사용된다.
- Reward/termination은 robot state·force·known path를 사용하며 hidden object state GT의 추가 사용은 명시하지 않는다.
- 비교 실험은 VIC/controller/exploration 방식의 효과이며 tactile 병용 또는 force input 자체의 ablation이 아니다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / actor state | §4.2, PDF p.3 |
| Object pose vs reference geometry | §3–4.2, PDF pp.3–4; Appendix A.2, pp.7–8 |
| Tactile | 사용하지 않음: §4.2, PDF p.3 |
| Force source / filtering / limitations | §4.2, PDF p.3; Appendix C, p.11 |
| Action / IC / mixing | §4.1–4.2, PDF pp.3–4; Fig.2 |
| Critic / runtime uncertainty | §4.2, PDF p.4; Appendix C, p.11 |
| Reward | §4.2, PDF p.3; Appendix A.3, pp.8–9 |
| Termination / safety | §5.2, PDF p.4; Appendix A.4, pp.9–10 |
| Comparisons | §5–6, PDF pp.4–6; Fig.3–5; Appendix B–C, pp.11–12 |
| Limitations / future check | §1, PDF p.2; §6–7, pp.5–6; Appendix C, pp.11–12 |
