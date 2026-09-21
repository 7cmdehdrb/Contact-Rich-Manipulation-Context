# Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 조사 C1](../reviews/2026-09-16_binary-tactile-wrench-rl.md#c1) · [별도 확인 CHECK-A15](../reviews/2026-09-20_separate-review-paper-list.md)

## 1. 논문 정보와 확인 범위

- **저자:** Jiahe Pan, Stelian Coros, Jitendra Malik, Toru Lin
- **연도 / 버전:** 2026, arXiv:2605.28812v1, 2026-05-27
- **게재 상태:** 제공 원문에서는 arXiv preprint로 확인되며 DOI·정식 학회/저널 게재 정보는 명시되지 않는다.
- **기관:** ETH Zurich, UC Berkeley
- **확인 원문:** 사용자 제공 PDF 18쪽 전체
- **원문 SHA-256:** f022d8c38412db7bbb55839a936b1a11caa9af4fbf4c3b0ffd701da60731e508
- **공개 원문:** [arXiv:2605.28812v1](https://arxiv.org/abs/2605.28812v1)
- **프로젝트 페이지:** [Beyond Binary project page](https://mpan31415.github.io/tactile_rep/)
- **기존 독립 Review 분석:** [260918 Review Dataset · B066](../review_dataset/260918/batch_003/papers/2026-pan-beyond-binary-cop-tactile.md)

이번 노트는 제공된 v1 PDF의 본문, Limitations, Appendices A–F와 Tables 1–6, Figures 1–14를 기준으로 정리한다. 코드 실행, 정책 재학습, 보충 영상 재현은 범위가 아니다.

## 2. 논문이 제시하는 문제

저자들은 contact-rich manipulation의 sim-to-real RL에서 촉각 표현이 병목이라고 본다. Raw tactile은 접촉 정보를 풍부하게 담지만 센서 고유의 응답과 복잡한 변형을 시뮬레이션에서 정확히 재현하기 어렵다. 반대로 binary·ternary처럼 강하게 축약한 표현은 전이가 쉬운 대신 정밀 조작에 필요한 하중과 공간 정보를 버린다.

이 논문의 핵심 질문은 **“Binary보다 풍부하지만 raw taxel보다 sim-to-real 정합이 쉬운 물리 기반 중간 표현을 만들 수 있는가?”**이다. 이를 위해 저자들은 각 tactile array의 접촉을 **Center-of-Pressure(CoP)** 로 표현한다.

이 논문에서 CoP는 임의의 다중 접촉 압력 분포 전체를 표현하는 것이 아니라, 한 sensor array의 접촉을 **resultant contact force와 centroidal contact point로 축약한 local descriptor**다.

## 3. Related Works의 비교 구도

원문은 기존 접근을 크게 세 가지로 구분한다.

- **저차원·단순 접촉 표현:** binary 또는 discretized tactile은 sim-to-real에 강하지만 고해상도 접촉 정보를 버린다.
- **Raw tactile / learned latent:** 더 풍부한 정보를 보존하지만 sensor-specific이고 simulator contact quantity와 정합하기 어렵다.
- **물리 기반 중간 표현:** force와 contact position 같은 물리량을 사용해 정보량과 전이성의 균형을 노린다.

저자들은 CoP를 **전이 가능성과 정보량 사이의 중간 지점**으로 제시한다.

## 4. 하드웨어와 과업

### 4.1. 로봇·촉각 센서

- **Hand:** 16-DOF Allegro Hand
- **Tactile:** XELA uSkin 3-axis taxel arrays
- **배치:** fingertips, phalanges, palm
- **Taxel 출력:** 각 taxel의 3축 force
- **정책 실행 시 외부 Vision:** 사용하지 않음
- **별도 Wrist 6-axis F/T:** 사용하지 않음

따라서 이 논문의 force 정보는 **손목 F/T가 아니라 tactile array에서 복원한 local contact force**다.

### 4.2. 두 Blind Manipulation Task

**Peg-in-hole insertion:** 이미 peg를 파지한 hand가 고정된 hole에 삽입한다. Circle, diamond, ellipse, hexagon, square, triangle의 6개 insertion head를 사용하고 초기 yaw를 전 범위에서 랜덤화한다.

**Ball balancing:** 네 fingertip이 50 g plate를 지지하고 그 위의 ball을 중심에 유지한다. Simulation에서는 smooth sphere로 학습하고, 실물에서는 질량·크기·마찰·표면이 다른 tennis/baseball/moon/hockey ball로 평가한다.

두 과업 모두 hand–object의 primary contact 변화로 **object–environment의 secondary contact**를 간접 추론해야 한다.

## 5. Physics-Grounded CoP 표현

각 tactile sensor array의 CoP는 **3D resultant contact force**와 **3D Cartesian contact position**으로 구성되며 둘 다 sensor frame에서 표현한다.

단순 taxel 합·평균은 compliant silicone layer 내부의 힘 분포를 반영하지 못할 수 있다. 저자들은 contact force를 normal/shear로 분해하고, contact point에서 taxel까지의 거리와 표면 법선 변화를 포함하는 differentiable stress-distribution model을 사용한다.

CoP position은 활성 taxel의 force magnitude 가중 평균으로 구한다. CoP force는 taxel force를 모은 regularized least-squares 문제로 복원한다. 이 mapping은 양방향이어서 실물 taxel→CoP와 simulator CoP→예상 taxel force를 같은 모델로 연결할 수 있다.

## 6. Differentiable Dynamics 기반 Sensor Calibration

Taxel 위치는 sensor specification에서 얻을 수 있지만 curved fingertip의 taxel frame orientation은 수동 보정이 어렵다. 저자들은 별도의 ground-truth force sensor 없이 taxel orientation을 학습한다.

1. Stiff PD로 finger joint nominal position을 유지한다.
2. Fingertip의 다양한 위치·방향에 외부 접촉을 가한다.
3. Raw taxel force, joint torque, joint angle을 기록한다.
4. 현재 orientation 추정치로 CoP force·position을 계산한다.
5. Forward kinematics와 CoP Jacobian으로 외력이 만들 joint torque를 예측한다.
6. 예측 torque와 기록 torque의 MSE를 back-propagation하여 orientation을 갱신한다.

Rotation은 R9+SVD 방식으로 parameterize한다. Appendix A의 설정은 **2400 samples, 2분 @ 20 Hz, Adam learning rate 0.1, batch gradient descent 100 steps**이다.

## 7. Sim-to-Real Alignment

Simulation은 IsaacLab ContactSensor를 사용한다. 그러나 fingertip geometry에서 simulated shear component가 신뢰하기 어려웠기 때문에 **실제 sim-to-real 실험에서는 surface-normal CoP force만 사용**한다. 개념적 CoP는 3D force vector이지만 실험 구현은 shear를 의도적으로 포기한다.

Actuator stiffness·damping·joint friction은 step, slow ramp, chirp 입력과 Bayesian optimization으로 system identification한다. Tactile sensor delay는 vision-based measurement로 측정하여 simulation에 넣고, domain randomization에서는 contact observation delay를 0.05–0.1 s로 둔다.

## 8. RL Policy

### 8.1. Actor / Critic

Actor는 current joint angles, previous action, 선택한 contact representation과 recurrent hidden state를 사용한다. **Current object pose, shape, mass, friction은 actor input이 아니다.**

Critic은 simulator privileged information을 추가로 사용한다. Peg/plate/ball의 position, rotation, velocity, goal vector·distance 등이 task에 따라 포함된다. Reward 역시 simulator task state를 사용한다.

### 8.2. Recurrent Architecture

현재 observation을 GRU에 넣고 256D latent를 FC [256, 128]에 전달한다. 3/5/10/20 step history를 flatten한 MLP와 비교했을 때 recurrent policy가 두 과업에서 sample efficiency와 convergence quality가 더 좋았다.

### 8.3. Action / Controller

- Action: 16D target joint-position increment
- Clip: [-1, 1]
- Scale: insertion 0.03, balancing 0.05
- EMA: alpha 0.5
- PD: insertion P=3.0, D=0.1 / balancing P=6.0, D=0.15

### 8.4. PPO 주요 설정

- IsaacLab + asymmetric actor-critic PPO
- initial learning rate: 5e-4, adaptive schedule
- target KL: 0.016
- rollout: insertion 64 steps/env, balancing 16 steps/env
- epochs: 5
- minibatches: 4
- gamma: 0.99
- GAE lambda: 0.95
- clip: 0.2
- entropy coefficient: 0.005

## 9. Reward와 Domain Randomization

Insertion reward는 goal distance, terminal success, good contact를 보상하고 peg rotation deviation과 hand DOF deviation을 penalize한다.

Ball balancing은 ball–plate goal distance와 plate contact를 보상하고 relative velocity, plate position/yaw deviation, action difference를 penalize하며 ball fall에 큰 penalty를 준다.

Domain randomization은 object mass·friction, initial pose, hand friction/initial state, PD gain, joint observation noise, contact force·position noise와 observation delay를 포함한다.

## 10. 실험 결과

### 10.1. Peg-in-Hole

6개 shape × 각 조건 10회 실물 평가의 overall success rate:

| 표현 | Overall success |
| --- | ---: |
| Proprioception only | 0.43 |
| Binary contact | 0.53 |
| Force magnitude | 0.55 |
| Force vector only | 0.67 |
| Contact position only | 0.50 |
| Raw taxel | 0.48 |
| **CoP** | **0.78** |
| Human | 1.00 |

OOD initialization에서는 CoP 0.63, binary 0.20, raw taxel 0.27이었다. Force-vector only 0.67, position-only 0.50, CoP 0.78의 비교는 insertion에서 **하중 정보와 접촉 위치가 상보적**임을 보여준다.

Raw taxel은 대부분의 compact representation보다 낮았다. 저자들은 imperfect tactile simulation, high dimensionality, sensor-specific mismatch를 가능한 원인으로 설명한다.

### 10.2. Taxel Masking

실물 raw taxel의 40%를 매 timestep masking하면 CoP overall success는 0.78→0.62, binary는 0.53→0.52였다. 세밀한 표현은 성능 이점과 함께 **개별 taxel 정확도에 대한 민감도**도 가질 수 있다.

### 10.3. Ball Balancing

| 표현 | Overall TTF (s) |
| --- | ---: |
| Proprioception only | 1.38 |
| Binary | 1.99 |
| Magnitude | 2.40 |
| **Force vector only** | **4.52** |
| Contact position only | 1.55 |
| Raw taxel | 1.49 |
| **CoP** | **4.60** |
| Human | 9.37 |

이 과업에서는 force vector only와 CoP가 거의 비슷하다. 따라서 **contact location의 추가 이득은 task-dependent**하다.

## 11. Policy Latent 분석

GRU의 256D latent를 linear probing하여 ball의 xy position·velocity를 예측했다. Position R²는 x 0.76, y 0.62였지만 velocity R²는 x 0.23, y 0.15였다.

50/150/250 g ball trajectory latent를 PCA로 시각화하면 시간이 지나면서 mass별 cluster가 분리된다. 저자들은 이를 명시적 supervision 없이 task-relevant physical property인 mass가 recurrent state에 emergent하게 조직되는 현상으로 해석한다.

## 12. 저자들이 밝힌 Limitation

### 12.1. Fidelity vs. Transferability

CoP는 raw taxel을 force+location으로 축약하므로 sensor-specific detail과 복잡한 distributed contact를 버린다. 정확한 sensor model이 있다면 richer raw representation이 더 높은 성능을 낼 가능성을 저자들도 인정한다.

### 12.2. Sim–Real Contact Discrepancy

실험은 unreliable simulated shear 때문에 normal component만 사용한다. Simulator는 task-object contact만 보고하지만 실제 tactile sensor는 self-collision과 environment contact에도 반응한다.

### 12.3. Scope

평가는 fixed-base dexterous hand와 XELA uSkin에 한정된다.

## 13. Future Work

저자들은 arm–hand system, full-hand tactile coverage, 다른 tactile sensor type, imitation learning, sample-efficient real-world RL로 확장하는 방향을 제시한다.

## 14. 원문을 읽을 때의 주의사항

- 이 논문은 **Wrist F/T + tactile fusion 연구가 아니다.**
- CoP force는 tactile taxel에서 복원한 local force다.
- 실제 sim-to-real 실험에서는 shear를 제거해 normal 성분만 사용한다.
- Actor는 object pose·shape를 받지 않지만 critic과 reward는 simulator GT를 사용한다.
- CoP는 full pressure distribution이 아니라 resultant force + centroidal contact point approximation이다.
- Binary보다 CoP가 우수했던 것은 특히 insertion에서 강하게 나타났고, ball balancing에서는 force-only와 CoP가 거의 같아 필요한 촉각 정보가 과업에 따라 달라진다.
- Raw taxel의 낮은 성능은 raw tactile이 원리적으로 나쁘다는 결론이 아니라 해당 simulation fidelity·dimension·sensor mismatch 조건에서의 결과다.

## 15. 저장소 내 연결

이 논문은 이미 [Binary Tactile·F/T 조사 C1](../reviews/2026-09-16_binary-tactile-wrench-rl.md#c1)에서 **Binary의 정보 손실을 보여주는 반대 근거**로 등록되어 있으며, [260918 Review Dataset B066](../review_dataset/260918/batch_003/papers/2026-pan-beyond-binary-cop-tactile.md)에서는 공통 schema로 재분석되어 있다.

이 문서는 그 기록을 대체하지 않고 저장소의 일반 papers 형식으로 원문 자체의 문제·센서·메소드·실험·한계·Future Work를 상세 정리한 canonical note다.

## 16. 주요 원문 위치

| 내용 | 원문 위치 |
| --- | --- |
| Motivation / contribution | §1, PDF pp.1–2 |
| CoP definition | §3.1, PDF p.2 |
| Taxel–CoP mapping | §3.2, PDF pp.2–4 |
| Differentiable calibration | §3.3, PDF p.4; Appendix A, p.13 |
| Sim–real alignment | §3.4, PDF p.5 |
| Policy / baselines | §4, PDF p.5 |
| Peg insertion results | §4.1, Table 1, PDF p.6 |
| Ball balancing | §4.2, Table 2, PDF p.7 |
| Latent probing / mass | §4.2, Table 3 / Fig.7, PDF pp.7–8 |
| Limitations / Future Work | §6, PDF p.8 |
| Recurrent vs MLP | Appendix D, Fig.12, PDF p.15 |
| Actor / critic / action / reward | Appendix E, Tables 4–6, PDF pp.16–17 |
