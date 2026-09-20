# Sim-to-Real Transfer for Robotic Manipulation with Tactile Sensory — 원문 상세 정리

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [사용자 별도 발굴 · USER-P003](../reviews/user-found-papers.md#user-p003)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Sim-to-Real Transfer for Robotic Manipulation with Tactile Sensory** |
| 저자 | Zihan Ding, Ya-Yen Tsai, Wang Wei Lee, Bidan Huang |
| 출판 | 2021 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), Prague, Czech Republic, Sep. 27–Oct. 1, 2021, pp. 6778–6785 |
| DOI | [10.1109/IROS51168.2021.9636259](https://doi.org/10.1109/IROS51168.2021.9636259) |
| 관리 ID | USER-P003 |
| 정리일 | 2026-09-20 |
| 확인한 원문 | 사용자 제공 IEEE 출판본 PDF 8쪽 전체. 본문 §I–VI, 식 (1)–(10), Fig. 1–7, Table I–III, References [1]–[37] |
| 확인하지 않은 자료 | 코드·체크포인트·원시 실험 로그, 인용된 선행논문의 개별 원문, tactile sensor 제조·회로의 별도 기술 문서, 저자 보충 영상 |
| 원문 PDF SHA-256 | 5f2946bf566fcec7e189ec0bfd3ce45b07a555d8e819955978ddd3a255a29c0c |

이 문서는 첨부 출판본 자체의 tactile sensor design, simulation approximation, binary contact representation, TD3 observation/action/reward, domain randomization, tactile signal randomization, zero-shot sim-to-real door-opening experiment, 저자 명시 한계와 Future Work를 정리한다. 프로젝트 적용안은 포함하지 않는다.

**핵심:** 저자들은 tactile이 vision·joint-based force/torque와 다른 **local and direct contact information**을 제공한다고 본다. 특히 force/torque sensing은 kinematic chain과 multiple contact force가 얽히기 때문에 contact area를 직접 제공하기 어렵다고 설명한다. 제안 시스템은 gripper 양 finger pad에 총 30개의 resistive tactile element를 배치하고, simulation과 reality의 연속 signal을 모두 **binary contact**로 축약해 TD3 observation에 넣는다. Tactile 사용 정책은 실물에서 평균 door-opening angle을 21.5°에서 31.2°로 높였고, 평균 275.6 step에서 176.3 step으로 줄였다. [원문 §I, §IV–V, Table III, PDF pp. 1, 4–7]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 정의·기여와 Related Work |
| 3 | 실물 resistive tactile array 설계 |
| 4 | MuJoCo tactile approximation과 binary reduction |
| 5 | Door-opening RL observation/action/reward |
| 6 | TD3 training과 sim-to-real randomization |
| 7 | Tactile calibration·binary threshold |
| 8 | 실물 robot·vision·control setup |
| 9 | w/ tactile vs. w/o tactile 실험 |
| 10–12 | F/T·vision·tactile 역할 해석, Limitation, Future Work |
| 13 | 미명시 사항 |
| 14 | 원문 위치 안내 |
| 15 | 핵심 메커니즘 요약 |

## 1. 제시하는 문제 상황

### 1.1 Contact-rich manipulation에서 tactile의 역할

원문은 tactile feedback이 contact-rich task에서 local environment의 kinematics와 mechanical property에 대한 supplementary information을 제공한다고 설명한다. Object와 직접 접촉하면 in-hand pose, surface texture, geometry 등 handling에 필요한 추가 정보를 얻을 수 있다고 서술한다. [원문 §I, PDF p. 1]

Vision은 spatial distance, shape, color 등 global·local feature를 contact 없이 제공할 수 있지만 occlusion이 생기면 충분하지 않을 수 있다. Force/torque sensing은 compliance와 safe interaction에 널리 사용되지만, 저자들은 **kinematic chain을 거친 측정과 multiple contact forces의 entanglement 때문에 contact area에 대한 direct information을 제공하기 어렵다**고 설명한다. Tactile은 이 부족함을 local/direct contact detail로 보완할 수 있다는 것이 논문의 출발점이다. [원문 §I, PDF p. 1]

### 1.2 Tactile RL에서 simulation이 필요한 이유

실물 tactile sensor는 반복 접촉으로 손상될 수 있고, RL은 많은 interaction data를 요구한다. 반면 tactile simulation은 일반 simulator에서 기본 제공되지 않거나 현실과 signal discrepancy가 크다. 저자들은 다음 두 문제를 동시에 해결하려 한다.

1. tactile array를 simulation에서 모델링할 것
2. simulated tactile observation을 사용하는 policy를 real robot으로 transfer할 것

[원문 §I, PDF pp. 1–2]

### 1.3 실제 검증 과업은 door opening

Door opening은 non-contact → contact → grasp 유지 → articulated object motion으로 이어지는 contact-rich task다. 저자들은 **door knob grasp quality가 이후 opening 성능을 좌우하고, bad grasp는 slip을 유발**하기 때문에 tactile의 효과를 검증하기 적합하다고 본다. [원문 §IV-C, PDF p. 4]

## 2. Related Work — 원문이 구성한 비교 구도

### 2.1 Tactile perception과 manipulation

원문은 tactile 연구를 크게 두 부류로 정리한다.

- tactile에서 robot/object state를 추론하는 perception
  - object recognition
  - slip detection
  - shape reconstruction
  - pose estimation
- tactile을 manipulation control에 추가하는 방식
  - grasping
  - stabilization
  - edge following
  - action selection

본 연구는 두 번째 범주에 속하며 **tactile information 자체를 policy observation에 넣어 manipulation performance를 높이는 것**을 목표로 한다. [원문 §II, PDF p. 2]

### 2.2 기존 tactile simulation과 본 연구의 차이

기존 tactile simulation 연구는 있었지만, 저자들은 **simulation에서 학습된 tactile-based manipulation policy의 sim-to-real transfer**가 충분히 검증되지 않았다고 설명한다. Wu et al.의 tactile grasping RL과 유사하게 simulation에서 tactile observation을 사용하지만, 이 논문은 door opening manipulation과 zero-shot transfer를 중심으로 한다. [원문 §II, PDF pp. 2–3]

## 3. 실물 Tactile Sensor Array

### 3.1 구조

In-house resistive tactile sensor array는 다음 구조다.

- flexible PCB의 inter-digitated electrode
- carbon-impregnated polymer sheet, Velostat
- 각 electrode 위 EVA foam bump
- gripper 양 finger pad에 sensor array 부착
- 전체 **30 sensing element**
- 두 pad에 균등 분배되어 **finger당 15 element**
- 배열 전체는 **6×5 matrix**

[원문 §IV-A, Fig. 1, PDF p. 3]

Pressure가 증가하면 element resistance가 감소한다. Column을 순차적으로 5 V로 구동하고 row ADC를 읽은 뒤 cross-talk compensation을 수행한다. ATmega32u4 microcontroller를 사용하며 PC로 약 **200 frames/s**로 전송한다. [원문 §IV-A, Fig. 3, PDF p. 3]

### 3.2 원문에 명시되지 않은 sensor 사양

원문에는 다음이 수치로 제시되지 않는다.

- force range
- force resolution
- minimum detectable force
- force accuracy
- spatial pitch
- element 실제 면적
- hysteresis
- sensor-to-sensor sensitivity variation의 정량 통계

이번 노트에서는 외부 데이터시트나 Velostat 일반 사양으로 보완하지 않는다.

## 4. Simulation Tactile Model과 Binary Reduction

### 4.1 MuJoCo approximation

Real sensor의 electrical response는 nonlinear하고 deformation도 존재하므로, 저자들은 electrical behavior 자체를 정확히 모델링하는 것은 현실적이지 않다고 판단한다. 대신 MuJoCo에서 각 tactile unit을 independent cylinder body로 만들고 그 아래 force sensor를 둔다. [원문 §IV-B, PDF p. 4]

MuJoCo force sensor는 3D continuous force를 줄 수 있지만, real tactile element가 perpendicular pressing에 반응하는 점을 모사하기 위해 **normal/perpendicular force만 사용**한다. Simulation force와 real electrical response의 scale을 맞추기 위한 scaling도 적용한다. [원문 §IV-B, PDF p. 4]

### 4.2 Continuous signal을 binary로 축약

Reality gap을 줄이기 위해 simulation force와 real electrical response를 모두 binary contact로 변환한다.

$$
\hat{c}_i=\begin{cases}1,&c_i>\kappa\\0,&\text{otherwise}\end{cases},\quad i=1,\ldots,30.
$$

(원문 식 (3))

Threshold $\kappa$는 heuristic하게 정한다. Binary representation을 사용하는 이유는 real electrical response의 nonlinear deformation과 simulation force model 사이의 정확한 magnitude correspondence를 요구하지 않기 위해서다. [원문 §IV-B–C, PDF p. 4]

저자들은 MuJoCo의 built-in touch sensor는 empirical comparison에서 sensitivity가 낮았기 때문에 사용하지 않았다고 명시한다. [원문 §IV-B, PDF p. 4]

## 5. RL Observation, Action, Reward

### 5.1 Observation

Tactile이 없는 baseline actor observation은 **25차원**이다.

Robot proprioception:
- end-effector position
- end-effector velocity
- joint positions
- joint velocities
- gripper width

Environment information:
- end-effector 기준 door-knob position
- door hinge angle

Tactile policy는 여기에 30개 binary tactile value를 추가하여 **총 55차원** observation을 사용한다. [원문 §IV-C-a, PDF p. 4]

저자들은 primary test에서 single-step observation만으로 approach, grasp, door opening을 학습할 수 있었기 때문에 **history를 policy input에 추가하지 않았다.** [원문 §IV-C-a, PDF p. 4]

### 5.2 이 정책은 blind manipulation이 아니다

Actor는 door-knob relative position과 hinge angle을 매 step observation으로 받는다. 실물에서는 ZED Mini stereo camera와 AprilTag marker를 이용해 cabinet/door pose를 측정한다. 따라서 이 논문은 **continuous environment-state observation + binary tactile** 구조이며, initial-only vision 또는 blind execution으로 분류하지 않는다. [원문 §IV-C-a, §V-B, PDF pp. 4, 6]

### 5.3 Action

Action은 8 DoF다.

- 7 DoF robot desired joint velocity
- 1 DoF gripper command

Training에서는 action 값을 normalize한다. [원문 §IV-C-b, PDF p. 4]

### 5.4 Reward

전체 shaped reward는 다음 다섯 항으로 구성된다.

$$
R=\omega_{\mathrm{door}}r_{\mathrm{door}}+\omega_{\mathrm{dist}}r_{\mathrm{dist}}+\omega_{\mathrm{ori}}r_{\mathrm{ori}}+\omega_{\mathrm{grasp}}r_{\mathrm{grasp}}+\omega_{\mathrm{tactile}}r_{\mathrm{tactile}}.
$$

(원문 식 (4))

원문 weight는 다음과 같다.

| Reward term | Weight |
| --- | ---: |
| Door angle | 5.0 |
| Distance | 0.4 |
| Orientation | 0.05 |
| Grasp | 0.1 |
| Tactile | 0.01 |

[원문 §IV-C-c, PDF p. 4]

각 reward의 역할은 다음과 같다.

- $r_{\mathrm{door}}$: grasp가 유지될 때 door hinge angle 자체를 보상
- $r_{\mathrm{dist}}$: gripper와 knob-center 거리 감소
- $r_{\mathrm{ori}}$: gripper orientation과 target orientation alignment
- $r_{\mathrm{grasp}}$: 양 finger가 knob와 contact한 grasp state
- $r_{\mathrm{tactile}}$: door opening이 시작되고 grasp state일 때 activated binary tactile unit 수

Tactile reward는

$$
r_{\mathrm{tactile}}=\|\hat{\mathbf c}\|_1
$$

을 사용하며, 조건은 hinge angle $\alpha>\alpha_0$와 grasp state다. 원문은 $\alpha_0=1.15^\circ$를 사용한다. [원문 식 (5)–(9), §IV-C-c, PDF p. 4]

### 5.5 Training-only information과 실행 관측을 구분해야 한다

$r_{\mathrm{grasp}}$와 $r_{\mathrm{tactile}}$의 조건에는 **양쪽 finger가 knob에 contact했는지 나타내는 $1_{\mathrm{grasp}}$**가 사용된다. 이는 simulation reward 계산에 필요한 contact-state information이다. 원문은 이 값을 actor observation의 별도 차원으로 제시하지 않는다. [원문 §IV-C-c, PDF p. 4]

따라서 deployment actor input과 simulation reward의 GT/contact state를 구분해야 한다.

## 6. TD3 Training과 Sim-to-Real Transfer

### 6.1 RL algorithm

Policy는 continuous action을 위한 **TD3**로 학습한다. Distributed training scheme으로 multiple GPU/CPU process를 사용하고, exploration action noise를 시간에 따라 decay한다. [원문 §III-B, §IV-C-d, PDF pp. 3, 5]

Actor/critic MLP layer 구성, learning rate, replay buffer size, discount factor, target-update rate 등 TD3 hyperparameter는 본문에 수치로 제시되지 않는다.

### 6.2 Dynamics randomization

Door environment의 다음 parameter를 uniform randomization한다.

| Parameter | Range |
| --- | --- |
| Knob friction | [0.8, 1.0] |
| Door hinge stiffness | [0.1, 0.8] |
| Door hinge damping | [0.1, 0.3] |
| Door hinge friction loss | [0.0, 1.0] |
| Door mass | [50.0, 150.0] |
| Knob mass | [2.0, 10.0] |

[원문 Table I, §IV-D-a, PDF p. 5]

Table I에는 mass 등의 단위를 별도로 적지 않으므로 임의로 kg 등으로 보완하지 않는다.

Robot parameter는 randomize하지 않고, link mass·joint damping·joint-control proportional gain 등을 **simulation/real joint-position trajectory alignment로 식별하여 고정**한다. [원문 §IV-D-a, PDF p. 5]

### 6.3 Observation/action noise와 delay

| 항목 | 범위 | 적용 대상 | Scale |
| --- | --- | --- | --- |
| Observation noise | [-0.002, 0.002] | tactile 제외 모든 observation | timestep |
| Observation delay | {0, 1} | 모든 observation | timestep |
| Action noise | [-0.01, 0.01] | gripper 제외 action | timestep |
| Table X offset | [-0.05, 0.05] | table position X | episode |
| Table Y offset | [-0.05, 0.05] | table position Y | episode |

[원문 Table II, §IV-D-b, PDF p. 5]

흥미롭게도 30차원 binary tactile은 일반 observation noise를 추가하지 않는다. 대신 별도의 tactile randomization을 둔다.

### 6.4 Binary flipping

각 binary tactile bit는 training 중 매 timestep 확률

$$
p_{\mathrm{flip}}=0.005
$$

로 0↔1 flipping한다. 이는 tactile sim-to-real gap을 완화하기 위한 별도 sensor randomization이다. [원문 §IV-D-c, PDF p. 5]

## 7. Tactile Calibration

### 7.1 Calibration 장치

Simulation과 reality의 tactile activation pattern을 맞추기 위해 별도 pressing experiment를 수행한다.

- press position: 128 mm, 256 mm, 350 mm
- weight: 50 g, 100 g, 200 g, 500 g
- 한 array의 15 unit activation을 simulation/real에서 비교

[원문 §V-A, Fig. 4–5, PDF pp. 6–7]

Real과 simulated continuous magnitude는 단순한 linear correlation을 보이지 않지만, 대부분의 경우 **어떤 unit이 활성화되는지의 pattern은 비슷**했다고 설명한다. 이 결과를 바탕으로 unit별 threshold를 정해 binary contact observation을 구성한다. [원문 §V-A, Fig. 5, PDF pp. 6–7]

Fig. 5 caption은 네 weight condition에 대해 red dashed threshold $\kappa$를 0.25, 0.5, 0.75, 1.25로 표시한다. 이 값을 sensor minimum detection force로 해석하면 안 된다. [원문 Fig. 5, PDF p. 7]

## 8. Real Robot Setup

| 항목 | 설정 |
| --- | --- |
| Robot | 7 DoF Franka Emika Panda |
| Gripper | two-finger gripper |
| Tactile | in-house resistive array 2개, 총 30 element |
| Vision | ZED Mini stereo camera |
| Pose marker | AprilTag |
| High-level policy command | 20 Hz |
| Robot control | 1 kHz |
| Command smoothing | consecutive command 사이 polynomial interpolation |
| Simulation | MuJoCo |
| Policy transfer | simulation → real, policy fine-tuning 없음 |

[원문 §V-B, PDF p. 6]

Real robot의 cabinet/door pose는 AprilTag marker로 얻는다. Simulation에서는 object relative pose와 door hinge angle을 simulator에서 직접 얻는다. [원문 §V-B, PDF p. 6]

## 9. w/ Tactile vs. w/o Tactile 실험

### 9.1 Training·evaluation protocol

Tactile 조건과 no-tactile 조건 각각에 대해

- random seed 3개
- policy당 25,000 training episodes
- distributed training 5 process
- episode 최대 1,000 step
- simulation과 reality에서 policy당 10회 평가

를 수행한다. 즉 조건당 real evaluation은 총 **30 trial**이다. [원문 §V-C, Fig. 7, PDF pp. 6–7]

### 9.2 Learned grasp strategy

Tactile policy는 knob의 양 측면을 잡으면서 많은 tactile unit을 활성화하는 pose를 보였다. 저자들은 이것을 **larger contact region**으로 해석하며, contact area가 커지면서 slip 가능성이 줄고 grasp stability가 증가했다고 설명한다. [원문 §V-C, Fig. 6, PDF pp. 6–7]

### 9.3 Table III 결과

| Setting | Door angle | Min / Max | Steps | Episode reward |
| --- | ---: | ---: | ---: | ---: |
| Sim w/ tactile | 41.8 ± 15.7° | 0.6 / 90.0° | 720.5 ± 234.4 | 2435.6 ± 1024.6 |
| Sim w/o tactile | 34.6 ± 20.3° | 1.3 / 90.0° | 584.4 ± 273.4 | 1881.8 ± 1363.3 |
| Real w/ tactile | **31.2 ± 14.0°** | **14.2 / 70.8°** | **176.3 ± 25.8** | — |
| Real w/o tactile | 21.5 ± 18.9° | 3.3 / 68.2° | 275.6 ± 167.2 | — |

[원문 Table III, §V-C, PDF p. 7]

실물 평균 door angle은 tactile 사용 시 21.5° → 31.2°로 증가한다. 논문 Abstract의 **45% improvement**는 이 평균값의 상대적 증가를 가리킨다. [원문 Abstract, Table III, PDF pp. 1, 7]

실물에서는 평균 step이 275.6 → 176.3으로 감소했고, door angle의 standard deviation도 18.9 → 14.0으로 줄어 저자들은 더 빠르고 consistent한 control로 해석한다. [원문 §V-C, Table III, PDF pp. 6–7]

Simulation에서는 tactile policy의 평균 step이 더 많다. 따라서 “tactile이 simulation과 reality 모두에서 항상 step 수를 줄였다”고 일반화하면 안 된다. 원문이 명시적으로 step 감소를 강조한 수치는 real experiment의 275.6 → 176.3이다.

### 9.4 Reward 비교 주의

No-tactile policy에는 tactile reward term 자체가 없으므로 episode reward를 직접 비교하는 것은 공정하지 않을 수 있다. 저자들은 no-tactile reward에 theoretical maximum tactile reward 300을 더한 경우까지 고려했지만 tactile policy가 여전히 높다고 설명한다. [원문 §V-C, PDF p. 7]

## 10. Vision·F/T·Tactile 역할에 대한 원문 해석

### 10.1 Vision

Vision은 global environmental information과 object spatial relation을 제공한다. 실제 실험에서도 ZED Mini + AprilTag를 통해 door/cabinet pose를 계속 사용한다. 따라서 tactile이 vision을 대체하는 연구가 아니다. [원문 §I, §V-B, PDF pp. 1, 6]

### 10.2 Force/Torque

저자들은 force/torque sensing을 compliance와 safe interaction에 유용한 global interaction sensing으로 설명한다. 그러나 **sensor와 contact 사이에 kinematic chain이 있고 multiple contact force가 섞이기 때문에 contact area를 직접 제공하기 어렵다**고 명시한다. [원문 §I, PDF p. 1]

이 문장은 이 논문이 wrist F/T-only observability를 수학적으로 분석했다는 뜻은 아니다. 또한 제안 policy가 wrist 6-axis F/T와 tactile을 직접 비교하는 ablation도 아니다. 저자의 motivation-level sensor-role 설명으로 구분한다.

### 10.3 Tactile

Tactile은 contact location/area에 대해 더 **local and direct**한 signal을 제공한다. 이 논문의 binary array는 pressure magnitude를 버리지만 **어떤 taxel이 활성화되었는지의 spatial pattern**은 유지한다. Policy는 이를 통해 grasp region을 넓히는 행동을 학습한 것으로 해석된다. [원문 §I, §IV-B–C, §V-C, PDF pp. 1, 4, 6–7]

## 11. Limitation — 저자들이 밝힌 한계

논문에는 독립된 “Limitations” 절은 없지만 본문에서 다음 제약을 명시한다.

### 11.1 Real tactile response의 정확한 modeling은 어렵다

Real tactile feedback은 nonlinear하고 material deformation이 있으며 simulator에도 한계가 있어 **electrical response를 explicit하게 정확히 모델링하는 것은 현재 unrealistic**하다고 서술한다. 그래서 normal force approximation + binary thresholding을 사용한다. [원문 §IV-B, PDF p. 4]

### 11.2 Tactile 정보 자체도 해석이 단순하지 않다

Introduction에서 tactile은 spatially local information이기 때문에 **environment state를 tactile perception만으로 reasoning하는 것이 straightforward하지 않다**고 명시한다. [원문 §I, PDF p. 1]

### 11.3 검증 범위

Conclusion은 framework가 low-granularity·small-deformation tactile sensor와 contact-rich task에 적용될 가능성을 주장하지만, **다른 sensor와 task에 대한 추가 검증은 future work**로 남긴다. 따라서 본 논문 실험은 in-house resistive array + door opening에 한정된 직접 검증이다. [원문 §VI, PDF pp. 7–8]

## 12. Future Work — 저자들이 제시한 향후 연구

Conclusion에서 두 방향을 명시한다.

1. **다른 tactile sensor와 다른 contact-rich task에서 framework 추가 검증**
2. **더 나은 tactile simulation model을 만들고 continuous readout을 직접 policy에 활용**

[원문 §VI, PDF p. 8]

두 번째 항목은 binary representation이 최종 목표라기보다 **현 시점의 sim-to-real 안정성을 위해 선택한 단순화**임을 보여준다.

## 13. 미명시 사항·원문 주의사항

| 항목 | 확인 결과·주의 |
| --- | --- |
| Tactile binary threshold의 최종 unit별 수치 | Calibration figure 일부 threshold는 제시되나 deployment용 30개 threshold 전체는 미명시 |
| Sensor force range·resolution·accuracy | 미명시 |
| Taxel pitch·개별 element area | 미명시 |
| Continuous real electrical signal의 정규화 방법 | Fig. 5 scaling 외 전체 pipeline 수치 미명시 |
| TD3 network architecture | 미명시 |
| TD3 learning rate·batch·buffer·$\gamma$·target update | 미명시 |
| Robot parameter identification의 최종 값 | trajectory alignment 방법만 설명, 식별값 미명시 |
| Door/knob mass table의 단위 | Table I에서 별도 단위 미명시 |
| Actor history | 사용하지 않음. single-step observation |
| Object pose | 매 step environment observation에 포함. blind/initial-only 아님 |
| F/T input | 제안 actor observation에는 별도 F/T 입력 없음 |
| Tactile vs. F/T ablation | 없음 |
| Tactile raw continuous policy | future work이며 현재 실험에는 없음 |
| Code·실험 재현 | 이번 작업에서는 수행하지 않음 |

## 14. 다시 읽을 때의 원문 위치

| 내용 | 위치 |
| --- | --- |
| Vision·F/T·tactile 역할과 contact-area 논리 | §I, PDF p. 1 / 인쇄 p. 6778 |
| 기여·zero-shot transfer 개요 | §I, Fig. 2, PDF pp. 1–2 |
| Related Work | §II, PDF pp. 2–3 |
| TD3 formulation | §III, 식 (1)–(2), PDF p. 3 |
| Resistive tactile array hardware | §IV-A, Fig. 1·3, PDF p. 3 / 인쇄 p. 6780 |
| MuJoCo tactile approximation | §IV-B, PDF p. 4 |
| Binary threshold 식 | 식 (3), §IV-B–C, PDF p. 4 / 인쇄 p. 6781 |
| Actor observation 25D+30D | §IV-C-a, PDF p. 4 |
| Action 8 DoF | §IV-C-b, PDF p. 4 |
| Reward와 tactile term | 식 (4)–(9), §IV-C-c, PDF p. 4 |
| Domain randomization | §IV-D-a, Table I, PDF p. 5 / 인쇄 p. 6782 |
| Noise·delay | §IV-D-b, Table II, PDF p. 5 |
| Binary flipping | §IV-D-c, PDF p. 5 |
| Calibration experiment | §V-A, Fig. 4–5, PDF pp. 6–7 |
| Panda·ZED Mini·AprilTag·20/1000 Hz | §V-B, PDF p. 6 / 인쇄 p. 6783 |
| Training·evaluation protocol | §V-C, PDF p. 6 |
| Real grasp pose comparison | Fig. 6, §V-C, PDF pp. 6–7 |
| Door-opening angle distribution | Fig. 7, PDF p. 7 |
| Quantitative performance | Table III, §V-C, PDF p. 7 / 인쇄 p. 6784 |
| Conclusion·Future Work | §VI, PDF pp. 7–8 |

## 15. 핵심 메커니즘 요약

이 논문은 **continuous tactile magnitude를 정확히 simulation하는 대신 spatial binary contact pattern을 transfer target으로 삼는** 접근이다. Real resistive array와 MuJoCo force approximation의 absolute magnitude가 맞지 않아도, contact/no-contact pattern을 threshold로 정규화하면 같은 policy representation을 simulation과 reality에서 사용할 수 있다.

Policy는 tactile 없는 25차원 observation에 30개 binary taxel을 추가한다. 이 30개 bit는 단순 “grasped/not grasped” 하나가 아니라 **두 finger pad의 spatial contact pattern**을 유지한다. Reward에서도 activated taxel 수를 이용해 larger contact region을 유도한다. 결과적으로 real robot에서 tactile policy는 더 넓은 grasp contact를 형성하고 slip을 줄여 평균 door-opening angle과 consistency를 개선한다.

Sensor-role 측면에서 논문은 vision을 global spatial sensing, joint-based F/T를 compliance/global interaction sensing, tactile을 local/direct contact-area sensing으로 구분한다. 다만 proposed actor가 F/T와 tactile을 동시에 사용하는 것은 아니므로, 이 논문은 **“F/T + binary tactile fusion”의 직접 사례가 아니라, 왜 distributed tactile contact locality가 별도 가치가 있는지 설명하는 근거**로 읽는 것이 정확하다.
