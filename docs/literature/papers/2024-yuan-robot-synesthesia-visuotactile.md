# Robot Synesthesia: In-Hand Manipulation with Visuotactile Sensing

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 ICRA 2024 선별 항목](../reviews/2026-09-19_icra-2024-contact-sensing-screening.md#icra24-yuan-robot-synesthesia)

## 1. 논문 정보와 확인 범위

- **저자:** Ying Yuan, Haichuan Che, Yuzhe Qin, Binghao Huang, Zhao-Heng Yin, Kang-Won Lee, Yi Wu, Soo-Chul Lim, Xiaolong Wang
- **게재:** 2024 IEEE International Conference on Robotics and Automation (ICRA), pp. 6558–6565
- **DOI:** [10.1109/ICRA57147.2024.10610532](https://doi.org/10.1109/ICRA57147.2024.10610532)
- **확인 원문:** 사용자 제공 IEEE 출판본 PDF 8쪽 전체
- **확인 파일 SHA-256:** 305de92e13d7e2e095c6f14a5dfdd1d0c07cc2b96a6c466b6b4ddad825b5ef8e
- **프로젝트 페이지:** [Robot Synesthesia](https://yingyuan0414.github.io/visuotactile/)
- **코드·보충자료 확인:** 이번 정독에서는 별도로 확인하지 않음

논문은 visuotactile in-hand rotation을 대상으로 하며, simulation에서 teacher를 강화학습으로 학습한 뒤 point-cloud 기반 student에 distillation하여 실물에 추가 fine-tuning 없이 이전한다.

## 2. 문제 상황과 핵심 주장

저자들이 지적하는 문제는 두 가지다.

첫째, tactile과 vision은 표현 성격이 크게 다르다. Tactile은 센서 위치별로 희소하고 저차원이며, vision은 dense하고 고차원이다. 각 modality를 별도 encoder로 처리한 뒤 feature 단계에서 단순히 합치는 방식은 두 신호의 공간적 관계를 직접 표현하기 어렵다.

둘째, sim-to-real에서는 vision과 touch 각각에 domain gap이 존재하고, 두 modality를 함께 사용할 때 두 gap을 동시에 맞춰야 한다.

저자들은 이를 해결하기 위해 **binary tactile contact를 활성 센서의 3D 위치에 point cloud로 투영하고, camera point cloud 및 robot kinematics로 생성한 augmented point cloud와 처음부터 하나의 3D point set으로 합치는 Robot Synesthesia 표현**을 제안한다.

중요한 점은 이 tactile point cloud가 연속 force magnitude를 복원하는 표현이 아니라는 것이다. 실제 FSR 값은 threshold로 binary contact가 된 뒤, **어느 sensor가 활성화되었는지를 그 sensor mesh의 3D 위치로 spatialize**한다.

## 3. Related Works에서의 비교 구도

### 3.1. Dexterous Manipulation

원문은 classical model-based control에서 deep model-free RL, demonstration/imitative learning으로 발전한 흐름을 정리한다. Generalization을 위해 proprioceptive history, binary tactile, depth, vision+touch 등이 사용되어 왔다고 설명한다.

특히 저자들은 다음 선행연구의 한계를 대비한다.

- proprioceptive history만으로 object state를 추론한 접근은 z-axis rotation에 제한적이라고 설명한다.
- binary tactile + proprioception 접근은 tactile이 너무 sparse하여 복잡한 object geometry를 충분히 포착하기 어렵다고 설명한다.
- optical tactile image + depth 접근은 continuous fingertip contact를 요구하여 작은 물체 위주로 제한될 수 있다고 설명한다.

### 3.2. Visuotactile Manipulation

기존 방식은 vision과 tactile을 각자 encoder로 처리한 뒤 feature를 concatenate하거나, optical tactile처럼 두 입력이 모두 image일 때 input-level fusion을 수행한다.

Robot Synesthesia는 tactile을 3D point cloud로 바꾸어 camera point cloud와 **input level에서 같은 좌표 공간에 결합**한다는 차이를 둔다.

## 4. 하드웨어와 Simulation

| 구성 | 내용 |
| --- | --- |
| Robot arm | XArm6 |
| Hand | 16-DOF Allegro Hand |
| Tactile | 16개 Force-Sensing Resistor(FSR) |
| FSR 배치 | palm과 finger links |
| Vision | Microsoft Azure Kinect depth camera |
| Simulator | Isaac Gym |
| Policy / control frequency | simulation·real 모두 10 Hz |
| 별도 wrist F/T | 사용하지 않음 |

FSR의 제조사·모델, 측정 범위, resolution, sample rate, 실제 threshold 값은 원문에 명시되지 않는다.

## 5. Tactile 처리와 Robot Synesthesia 표현

### 5.1. Raw FSR → Binary Contact

각 FSR의 contact signal을 읽은 뒤 predetermined threshold로 binarize하여 16D contact vector를 만든다. 저자들은 이를 tactile sim-to-real gap을 줄이기 위한 처리로 설명한다.

원문은 threshold 기호를 정의하지만 실물 threshold 수치, filtering, hysteresis, debounce 등의 세부는 제공하지 않는다.

### 5.2. Tactile Point Cloud

활성 tactile sensor마다 해당 sensor mesh 위에서 점을 샘플링해 tactile point cloud를 만든다.

- camera point cloud: 512 points
- robot augmented point cloud: hand link당 8 points, hand link 수 21
- tactile point cloud: 활성 tactile sensor당 8 points
- active sensor 수: 0–16

따라서 tactile point cloud 크기는 접촉된 센서 수에 따라 변한다.

### 5.3. Augmented Point Cloud

Robot proprioception에서 현재 hand pose를 계산하고 robot mesh 위에서 point를 샘플링한다. 이는 camera observation만으로는 명확하지 않은 hand geometry와 현재 configuration을 3D spatial context로 제공한다.

### 5.4. 공통 좌표계와 modality tag

Camera point cloud, augmented robot point cloud, tactile point cloud를 모두 **hand palm frame**으로 변환한다.

각 point에는 one-hot modality label을 붙인 뒤 하나의 point set으로 concatenate한다. PointNet이 이 통합 point cloud를 encoding한다.

## 6. Benchmark Task

### 6.1. Four-Way Wheel-Wrench Rotation

다중 handle을 가진 wheel wrench를 z-axis로 회전한다. 다음에 사용할 수 있는 handle을 visual로 찾고, touch로 object interaction을 감지해야 하는 과업이다.

### 6.2. Double-Ball Rotation

두 개의 동일한 ball을 손 안에서 서로 회전시킨다. 저자들은 tactile alone으로는 두 ball을 구분하기 어렵기 때문에 visual location information이 중요하다고 설명한다.

### 6.3. Three-Axis Rotation

다양한 shape의 물체를 x, y, z axis로 회전한다. Simulation에서는 cuboid, cylinder, polygon 등을 포함한 artificial object set을 학습·평가하고, 실물에서는 크기와 shape가 다른 daily object로 generalization을 시험한다.

## 7. State, Action, Reward

### 7.1. State

문제 정의에서 상태에는 다음이 포함된다.

- Allegro joint position 16D
- binary tactile 16D
- rotation axis
- previous joint-position target
- camera point cloud
- augmented robot point cloud
- tactile point cloud

Teacher와 student가 실제로 사용하는 observation은 이후 training pipeline에서 다시 구분된다.

### 7.2. Action

Policy는 16D relative joint-position command를 출력한다. 이전 target에 relative increment를 더하고 PD controller가 추종한다.

Action에는 EMA를 적용하며 원문의 설정은 eta=0.8이다. 이 EMA는 tactile filtering이 아니라 **action smoothing**이다.

### 7.3. Reward

Reward는 다음 항목의 weighted sum으로 구성된다.

- object rotation angle reward
- object linear velocity penalty
- object–fingertip distance term
- joint torque penalty
- controller work penalty
- command–actual control error penalty
- object drop 시 큰 추가 penalty

정확한 coefficient 값은 원문 본문에 제시되지 않는다.

## 8. Teacher–Student 학습 구조

### 8.1. Stage I — PPO Teacher

Teacher는 low-dimensional privileged state로 PPO 학습한다.

입력은 다음을 포함한다.

- hand joint position
- binary tactile
- target rotation axis
- previous joint-position target
- object position
- object linear velocity
- object angular velocity
- 32D object shape feature

Shape feature는 multi-object generalization이 필요한 task에서 pretrained PointNet으로 encoding한다. Current state에 과거 3개 state를 stack하여 temporal information을 제공한다.

**원문 표기 주의:** Figure 3은 teacher input을 “Object Pose”라고 요약하지만, 본문 §IV-C의 구체적 열거에는 object position, linear velocity, angular velocity가 명시되고 orientation 변수는 별도로 열거되지 않는다. 상세 노트에서는 본문 열거를 우선해 기록한다.

### 8.2. Stage II — Visuotactile Student

Student의 low-dimensional 입력은 다음과 같다.

- joint position
- binary tactile
- rotation axis
- previous joint-position target
- 현재 + 과거 3개 state history

추가로 camera point cloud, augmented robot point cloud, tactile point cloud를 하나로 합쳐 PointNet에 넣는다.

학습은 두 단계다.

1. teacher rollout에서 **5.12 million transitions**를 수집해 Behavior Cloning으로 pre-train
2. DAgger로 fine-tune

즉, deployable policy를 point-cloud input으로 처음부터 RL 학습한 것이 아니라, **privileged-state RL teacher → visuotactile student distillation** 구조다.

## 9. Simulation 실험

### 9.1. Stage I RL 비교

Table I에서 Visual RL, partially observable non-visual RL(PS), privileged teacher(Ours)를 500 episode씩 평가한다.

Teacher가 모든 benchmark에서 더 높은 CRR/TTF를 보였으며, Visual RL은 같은 training epoch 내에 높은 reward 행동을 학습하기 어려웠다.

이 결과는 **high-dimensional visual input을 직접 PPO로 학습하는 것이 sample-inefficient**하다는 저자들의 teacher-student 선택 근거다. 동시에 deployable student 자체의 real-world 성능을 의미하는 표는 아니다.

### 9.2. Student Sensor Ablation

Table II는 다음 student 입력을 비교한다.

- Touch
- Cam + Aug
- Touch + Cam + Aug
- Touch + Cam + Aug + Syn

복잡한 wheel-wrench와 double-ball에서는 Syn을 포함한 전체 입력이 가장 높은 CRR/TTF를 보인다. 그러나 multi-object axis별 결과에서는 모든 축에서 항상 최고인 것은 아니다. 따라서 표는 “모든 과업에서 tactile point cloud가 단조롭게 우월하다”는 근거라기보다, **복잡한 spatial reasoning에서 input-level tactile spatialization이 유용한 경우가 있음**을 보여준다.

## 10. Real-World Zero-Shot Transfer

Student policy를 실물에 **fine-tuning 없이** 이전한다. 각 policy는 task별 5 episode, episode 최대 60초로 평가한다.

Table III의 주요 결과:

| Task | Touch | Cam+Aug | Touch+Cam+Aug | Touch+Cam+Aug+Syn |
| --- | --- | --- | --- | --- |
| 4-way Wrench CRA/TTF | 0.25 / 60.0 | 0.25 / 60.0 | 0.25 / 60.0 | **1.5 / 43.0** |
| Double Balls | 15.6 / 26.7 | 10.1 / 20.8 | 18.8 / 32.7 | **22.9 / 36.6** |
| Multi-Object x-axis | 0.7 / 60.0 | 0.25 / 60.0 | 0.5 / 60.0 | **2.1 / 26.6** |
| Multi-Object y-axis | 0.2 / 60.0 | 1.0 / 33.3 | **1.4 / 28.3** | 0.9 / 29.3 |
| Multi-Object z-axis | 7.4 / 60.0 | 5.1 / 60.0 | 5.1 / 57.1 | **10.2 / 60.0** |

Syn이 4-way wrench, double-ball, x-axis, z-axis에서 높은 CRA를 보이지만 **y-axis에서는 Touch+Cam+Aug가 더 높은 CRA**다.

또한 CRA와 TTF는 서로 다른 지표다. 더 많이 회전한 정책이 반드시 60초 동안 object를 유지한 것은 아니므로 하나의 숫자로 합쳐 우열을 해석하면 안 된다.

## 11. PointNet 중간표현 분석

저자들은 PointNet max pooling에서 선택되는 critical points를 시각화한다.

Robot Synesthesia policy에서 선택된 point 중 평균 **42.7%가 tactile-based points**였고, 나머지는 주로 fingertip·finger edge·palm에서 선택되었다.

이는 tactile point가 단순히 입력에 존재할 뿐 아니라 PointNet의 action representation에서 실제로 많이 선택됨을 보여주는 qualitative/representation-level 근거다.

## 12. Object Information과 정보 경계

| 구분 | Object 정보 |
| --- | --- |
| PPO teacher | object position, linear/angular velocity, shape embedding 등 privileged state 사용 |
| Student training | teacher action을 BC/DAgger로 distillation |
| Student deployment | privileged object state 대신 continuous depth-camera point cloud + robot/tactile point cloud 사용 |
| Binary tactile 단독 | object geometry나 동일한 두 object의 identity를 직접 제공하지 않음 |

따라서 이 논문은 **binary tactile-only blind policy가 object state를 내부적으로 모두 해결하는 구조가 아니다.** 실행 student는 지속적인 visual point cloud를 사용한다.

## 13. 저자들이 밝힌 Limitation

원문에는 독립된 Limitation 절이나, Conclusion에서 방법의 한계를 항목별로 명시한 내용이 없다.

따라서 아래 §15의 sensor specification 누락, continuous vision 의존, 실물 평가 trial 수 등의 사항을 저자 명시 Limitation으로 바꾸어 기록하지 않는다.

## 14. Future Work

Conclusion에서 다음을 향후 연구로 제시한다.

- **goal-conditioned object rotation**
- **optical tactile sensor integration**
- simulation environment와 training pipeline의 code release 계획

Code release는 향후 공개 의사이며, 이번 정독에서 실제 공개·재현 여부를 확인한 것은 아니다.

## 15. 미명시 사항과 원문 주의사항

- FSR 제조사·모델, force range, resolution, sampling rate가 미명시다.
- 실물 FSR threshold 값과 filtering/hysteresis/debounce가 미명시다.
- Binary tactile은 force magnitude를 버리며, tactile point cloud는 이를 복원하지 않는다. 활성 sensor의 **3D 위치**를 추가하는 표현이다.
- 별도 wrist F/T sensor는 사용하지 않는다.
- Student는 **continuous camera point cloud**를 실행 중 사용하므로 non-visual / initial-vision-only manipulation으로 분류하지 않는다.
- Figure 4의 RGB보다 point cloud가 sim-real에서 더 유사하다는 주장은 시각화로 제시되며, 해당 그림 자체에는 정량 domain-gap metric이 없다.
- Real-world Table III는 각 policy/task당 5 episode의 소규모 평가다.
- Teacher의 privileged state와 deployable student의 observation을 구분해야 한다.
- 저자들이 “vision and touch input으로 simulator에서 trained policy”라고 요약하는 문장은 전체 pipeline을 지칭하며, 실제 student는 PPO로 처음부터 학습된 것이 아니라 teacher policy를 BC+DAgger로 distillation한다.

## 16. 주요 원문 위치

| 내용 | 원문 위치 |
| --- | --- |
| Motivation / contribution | §I, PDF pp.1–2 |
| Related Works | §II, PDF pp.2–3 |
| Hardware / binary tactile / point cloud | §III-A, PDF p.3 |
| Benchmark tasks | §III-B, PDF p.3 |
| State / action / reward | §IV-A, PDF pp.3–4 |
| Tactile point cloud | §IV-B, PDF p.4 |
| Teacher / student pipeline | §IV-C, PDF pp.4–5 |
| Object sets / metrics | §V-A, PDF p.5 |
| Teacher comparison | §V-B, Table I, PDF pp.5–6 |
| Student ablation | §V-C, Table II, PDF pp.5–6 |
| Real-world transfer | §V-D, Table III, PDF p.6 |
| PointNet critical points | §V-E, Fig.7, PDF p.6 |
| Future Work | §VI, PDF p.6 |
