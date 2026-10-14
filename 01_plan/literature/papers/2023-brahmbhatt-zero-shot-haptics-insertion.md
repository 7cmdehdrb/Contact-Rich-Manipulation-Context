# Zero-Shot Transfer of Haptics-Based Object Insertion Policies

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [원래 Wrist Wrench 조사 W4](../reviews/2026-09-21_wrist-wrench-manipulation-survey.md#w4)

## 1. 논문 정보와 확인 범위

- **제목:** Zero-Shot Transfer of Haptics-Based Object Insertion Policies
- **저자:** Samarth Brahmbhatt, Ankur Deka, Andrew Spielberg, Matthias Müller
- **게재:** IEEE International Conference on Robotics and Automation (ICRA), pp. 3940–3947, 2023
- **출판 확인:** [IEEE 문서 번호 10160346](https://ieeexplore.ieee.org/document/10160346/)
- **확인 원문:** 사용자 제공 arXiv:2301.12587v3, 2023-06-08, PDF 9쪽 전체
- **원문 PDF SHA-256:** `89a1a9fda0db4e0942b9c000200f0d34f4f1f86fbcabc18c7bcf507012a09273`
- **원문이 안내한 자료:** [프로젝트 페이지](https://sites.google.com/view/compliant-object-insertion) · [코드](https://github.com/isl-org/0shot-object-insertion)
- **이번 정독에서 확인하지 않은 자료:** 코드 실행·학습 및 실험 재현, supplementary video, 원문이 인용한 47편의 전체 본문

원문 PDF를 텍스트 추출하고 9개 전 페이지를 PNG로 렌더링하여 식, Table I–III, Fig. 1–9와 Supplementary Material A–C를 대조했다. 아래의 `[원문 §…, PDF p.…]`는 첨부 PDF 기준이다.

**핵심:** 이 논문은 이미 파지한 물체를 슬롯형 홀더에 삽입하는 접촉 구간을 대상으로, 목표 대비 말단 pose와 6D 말단 Wrench의 8시점 이력을 입력받는 SAC residual policy를 시뮬레이션에서만 학습한다. 목표 pose에 6D noise curriculum을 주고, 절반의 episode를 부분 삽입 상태에서 시작하며, 실제 정책 추론 지연을 시뮬레이션에 반영한다. 학습한 정책은 별도 실물 데이터·미세조정 없이 Franka Panda에 배포되어 regular plate 기준 `83.3±13.6%` 성공률을 보였다. [원문 Abstract, §I, §III–IV]

다음 경계를 먼저 유지해야 한다.

- **Zero-shot**은 실물 데이터·실물 사전학습·미세조정이 없다는 뜻이다. 카메라 보정, 실행 전 ArUco 목표 측정, 사람이 물체를 잡아 주는 초기화까지 없는 완전 무보정 자율 시스템은 아니다.
- 실행 중 live object tracking은 쓰지 않지만, 시작 전 shoulder camera로 목표 pose를 한 번 측정한다. 따라서 시각을 전혀 쓰지 않는 정책 시스템으로 표현하면 안 된다.
- 정책이 다루는 핵심은 MoveIt 접근 이후의 contact-rich stage다. 물체 파지와 장애물이 없다고 가정한 12 cm 상공까지의 접근은 학습 대상이 아니다.
- Wrench는 외장 F/T가 아니라 Franka의 말단 외력 추정값이며, 중력·코리올리·가속 성분을 제거해 물체 무게와 접촉 하중을 함께 반영한다.
- 이력 ablation은 있지만 Wrench 자체를 제거한 ablation은 없다. 이 논문만으로 6D Wrench의 독립 기여도를 수치화할 수 없다.

---

## 2. 문제 설정과 2단계 실행

### 2.1. 해결하려는 문제

접시를 식기 건조대·식기세척기 슬롯에 넣을 때 목표 pose가 부정확하고 목표 슬롯이 보이지 않는 물체로 막혀 있으면 충돌 회피만으로는 과업을 풀기 어렵다. 저자들은 실물 데이터 수집이나 실물 적응 없이, 충돌을 이용하여 막힌 목표에서 이웃의 빈 슬롯을 찾는 정책을 시뮬레이션에서 학습하려 한다. [원문 §I, PDF pp. 1–2]

### 2.2. 실행 단계와 가정

1. 물체는 정책 실행 전에 이미 gripper에 파지되어 있다.
2. MoveIt open-loop planner가 말단을 근사 목표 pose의 12 cm 위까지 이동한다. 저자들은 이 접근 경로에 장애물이 없다고 가정한다.
3. 학습된 controller가 접촉이 많은 삽입 구간을 수행한다. 이것이 논문의 주 기여다.

실물에서는 작업자가 물체를 gripper finger 사이에 잡고 있는 동안 gripper를 닫는다. 전체 pick-and-place나 mobile perception stack을 학습한 결과가 아니다. [원문 §III, §IV, PDF pp. 3–4]

---

## 3. 좌표계와 Actor Observation

### 3.1. Noisy target-relative pose

로봇 base, target, object, end-effector를 각각 $b,t,o,e$로 쓰고, bar는 최종 의도 상태를 뜻한다. 파지 물체를 목표에 놓는 end-effector pose는 다음과 같다. [원문 §III, PDF p. 3]

```math
{}^{b}T_{\bar e}={}^{b}T_t{}^{t}T_{\bar o}{}^{o}T_e.
```

Simulation의 정확한 target pose에 6D uniform noise $\mathcal{U}[-\epsilon,\epsilon]$를 더한 $^{b}\widetilde{T}_t$를 만들고, 이를 통해 noisy end-effector target $^{b}T_{\widetilde e}$를 계산한다. $^{t}T_{\bar o}$와 $^{o}T_e$는 episode 중 고정된 것으로 가정한다. 실제 접촉으로 in-hand object pose가 바뀌더라도 이를 추적하지 않으므로 정책이 그 오차에 견뎌야 한다.

현재 관측의 pose 성분은 noisy target에 대한 현재 end-effector 상대 pose다. Translation 3개와 axis-angle rotation 3개로 표현해 6D가 된다.

```math
{}^{\widetilde e}T_e=\left({}^{b}T_{\widetilde e}\right)^{-1}{}^{b}T_e.
```

### 3.2. End-effector Wrench

두 번째 성분은 base frame으로 표현한 6D Wrench $W$다. Force 3축과 moment 3축을 포함한다. 원문은 gravity, Coriolis, acceleration 성분을 제거하여 물체 무게와 접촉력만 남긴다고 설명한다. 따라서 object mass가 observation에 영향을 준다. [원문 §III, PDF p. 3]

실물 코드에서는 Franka state의 `O_F_ext_hat_K`를 사용한다. 이는 별도 장착 F/T 센서 측정이 아니라 관절 토크 기반 외력 추정으로 분류해야 한다. [저자 제어 코드](https://github.com/isl-org/0shot-object-insertion/blob/e916d29e815b46e2f54636d46fff8a92cc698f22/ros_controllers/src/tf_policy_controller.cpp#L241-L247) · [Franka 정의](https://github.com/frankaemika/libfranka/blob/0.9.0/include/franka/robot_state.h#L302-L310)

### 3.3. 8시점 stacking

속도, 접촉 이력, 현재 접촉 지속시간처럼 단일 frame으로 알기 어려운 상태를 간접적으로 표현하기 위해 상대 pose 6D와 Wrench 6D를 $H=8$ steps 쌓는다. 단순 차원 계산으로는 timestep당 12D, 총 96D history다. 기본 actor는 recurrent network가 아니라 이 고정 길이 stacking을 2-layer MLP로 처리한다. [원문 §III, Supplementary C Table III]

---

## 4. Action, Residual Target, Low-level Controller

### 4.1. Policy action

SAC actor는 $a_t\in[-1,1]^6$을 출력한다. 앞의 3개는 translation, 뒤의 3개는 axis-angle rotation이며 현재 end-effector pose에 대한 6-DOF residual motion target이 된다. 이 residual은 noisy target을 향해 직선으로 이동하는 base motion target과 합성된다. [원문 §III, PDF p. 3]

Main text는 translation을 45 cm, rotation을 45°로 scaling한다고 쓰지만 Supplementary Table III는 rotation을 **50°**로 기록한다. 동일 PDF 내부 표기 불일치이므로 어느 하나를 임의로 확정하지 않는다.

### 4.2. 제어 주기

- SAC high-level policy: 20 Hz
- Operational Space Controller (OSC): 1 kHz
- 새 state vector: low-level 50 steps마다 획득
- OSC proportional gain: 150
- Damping ratio: 1.0
- Translation error scaling: 0.05
- Rotation error scaling: 0.5

저자들은 OSC와 Wrench formulation이 simulated/real robot dynamics를 분리한다고 보고 robot dynamics 자체는 randomize하지 않았다. 이는 dynamics mismatch가 사라진다는 증명이 아니라 논문의 설계 선택이다. [원문 §III, Supplementary C Table III]

---

## 5. SAC와 보상

### 5.1. 학습 구조

Actor와 critic은 각각 hidden size `(256, 256)`의 2-layer MLP다. Continuous action의 unimodal Gaussian policy를 Soft Actor-Critic으로 학습한다. Horizon은 $T=128$, discount factor는 $\gamma=0.99$다. [원문 §III, Supplementary C]

### 5.2. Reward components

전체 reward는 다음 항들의 합이다.

- 매 step 시간 벌점: $R_{time}=-1/T=-1/128$
- 물체 drop 벌점과 episode 종료: $R_{drop}=-1.1$
- 성공 reward와 episode 종료: $R_{success}=+0.5$
- true target까지의 translation·rotation 거리 벌점
- 이전 action 대비 변화량에 대한 smoothness 벌점

거리 벌점은 다음 형태다. Actor observation에는 noisy target이 들어가지만, reward의 거리 계산은 simulation true target을 사용한다. [원문 §III, Supplementary C Table III]

```math
R_{dist}=-\sum_{m\in\{trans,rot\}}K_{dist}^{(m)}
\min\!\left(\lambda_{dist}^{(m)},\left\lVert{}^{\bar e}T_e\right\rVert^{(m)}\right).
```

Action 변화 벌점은 두 연속 action transform의 차이를 제한한다.

```math
R_{\Delta a}=-\sum_{m\in\{trans,rot\}}K_{\Delta a}^{(m)}
\min\!\left(\lambda_{\Delta a}^{(m)},\left\lVert{}^{a_{t-1}}T_{a_t}\right\rVert^{(m)}\right).
```

두 항 모두 translation/rotation scale은 각각 $8.59\times10^{-3}$, $8.21\times10^{-3}$이고 cutoff는 50 cm, 30°다. 저자들은 phase별 staged reward를 사용하지 않는다.

### 5.3. Simulation 성공 판정

물체가 height threshold보다 낮고 tabletop X–Y 좌표가 어느 slot center에서 $d_{success}$ 안에 있으면 success state로 본다. 삽입 뒤 진동을 줄이기 위해 이 상태를 10 policy steps 유지해야 종료하며, $d_{success}$는 slot 폭을 포함하도록 늘렸다. Supplementary Table III는 별도로 `Max. distance from target for success`를 2 cm, 10°로 기록한다. [원문 §III, Supplementary C]

---

## 6. Zero-shot Sim-to-Real을 위한 설계

### 6.1. Target-pose noise curriculum

Target pose noise가 없으면 policy가 simulation obstacle geometry와 충돌 없는 궤적을 암기하고 실물에서 실패했다. 저자들은 translation·rotation 모두에 6D uniform noise를 추가하고 $\epsilon$을 piecewise-linear curriculum으로 키웠다. 최종 범위는 5 cm, 5°다. 이로써 true target을 관측만으로 알 수 없게 하고 충돌 대응 행동을 학습하도록 유도한다. [원문 §III, Supplementary C]

### 6.2. Partial insertion initialization

큰 pose noise는 random exploration으로 성공 상태를 발견할 확률도 낮춘다. Reverse curriculum에 따라 episode의 50%를 물체가 이미 부분 삽입된 pose에서 시작한다. 이 초기화와 residual action formulation 중 하나라도 없으면 simulation 학습 자체가 완전히 실패했다고 저자들이 보고한다. [원문 §III–IV]

### 6.3. Policy inference delay

실제 로봇에서는 policy inference와 state/action 통신 중에도 시간이 흐른다. Simulation에서 low-level control 7–13 steps의 delay를 randomize하여 이를 모델링한다. 1 kHz controller 기준 약 7–13 ms에 해당한다. Delay를 제거하면 simulation 성공률은 97%지만 실물은 50%로 떨어졌다. [원문 §III, Fig. 8, Supplementary C]

### 6.4. Gripper와 geometry mismatch

Simulation은 Panda rigid gripper, 실물은 Soft Robotics mGrip을 사용한다. 저자들은 mGrip의 높은 마찰과 firmness/compliance가 얇은 plate 파지에 유리하다고 설명한다. 정확한 Wrench를 위해 mGrip을 simulation에 모델링하는 일은 범위 밖으로 남겼다. Plate, holder, blocking object의 geometry도 simulation과 실물이 크게 다르다. [원문 §III–IV, Fig. 4–5]

---

## 7. 학습 Hyperparameters

| 항목 | 값 |
| --- | ---: |
| Horizon / simulated slots / slot gap | 128 / 3 / 10 cm |
| Observation history | 8 steps |
| Batch size / discount | 256 / 0.99 |
| Actor·critic·temperature learning rate | $3\times10^{-4}$ |
| Training iterations / updates per iteration | 64 K / 50 |
| Parallel workers | 20 |
| Replay buffer | 1024 K steps |
| Initial random experience | 64 K steps; main text는 500 episodes로 설명 |
| Training hardware | Intel Xeon Platinum 8180, 112 cores, 1 TB RAM |
| 한 policy 학습 시간 | 14 hours |

Main text와 Supplementary가 초기 random data를 서로 다른 단위로 기록하므로 64 K steps와 500 episodes가 정확히 같은 수인지 원문만으로 확정하지 않는다. [원문 §III, Supplementary C]

---

## 8. 실물 장비와 평가 Protocol

| 항목 | 원문 내용 |
| --- | --- |
| 로봇 | Franka Emika Panda |
| Gripper | Soft Robotics mGrip; simulation은 Panda rigid gripper |
| 목표 측정 | Shoulder camera와 작업자가 든 ArUco marker로 시작 전에 1회 측정 |
| 시작 pose | 중앙 slot 위 `20×40×15 cm` cuboid에서 random |
| 홀더 | 실물 6 slots; plate-slot clearance 2.5 mm |
| Blocking object | 목표 slot에 cup 또는 phone charger |
| 평가 횟수 | 방법·물체별 slot당 4회, 총 24 episodes |
| 집계 | 1–4번째 trial 각각을 6개 slot에 걸쳐 success rate로 만든 뒤 네 값의 mean/std. 보고 |

실물 성공은 plate가 어느 slot에든 삽입되어 3초 유지되는 경우다. 성공을 감지하면 grasp를 풀고 arm을 올린다. Slot 밖에서 정지한 경우, high-force jam, torque limit 또는 joint-angle limit 도달은 실패다. 성공 감지에 쓰인 실물 센서와 정확한 threshold는 원문에 충분히 명시되지 않았다. [원문 §IV, PDF p. 4]

---

## 9. Baseline과 비교 조건

| 방법 | 동작·학습 조건 | 해석 주의 |
| --- | --- | --- |
| Straight-down | OSC target을 계속 아래로 이동 | Noisy target에 민감한 단순 heuristic |
| Random-search | 5 cm horizontal square에서 점을 뽑고, 3 N 접촉까지 하강한 뒤 실패 시 상승·재탐색 | Yaw error에 민감 |
| `[16] no-vision` | Proprioception/Wrench 별도 branch와 temporal convolution을 축소 재구현 | 원 논문의 full method나 pretrained representation을 그대로 비교한 것이 아님 |
| Ours | 8-step stacked pose/Wrench, SAC, noise·delay·partial insertion | 제안한 전체 조합 |

`[16] no-vision`은 원 구조가 simulation에서 `17.0±13.1%`였기 때문에 16D Wrench/proprioception feature의 작은 버전으로 바꾸고, 이 논문의 RL objective와 randomization으로 다시 학습했다. 따라서 해당 선행 논문의 원 성능을 재현한 결과로 읽으면 안 된다. [원문 §IV, PDF p. 5]

---

## 10. 주요 정량 결과

Table II의 plate insertion 결과는 다음과 같다. 각 값은 앞 절의 네 success-rate 값에 대한 mean±std.다. [원문 Table II, PDF p. 5]

| 방법 | Simulation success (%) | Real regular plate success (%) |
| --- | ---: | ---: |
| Straight-down | 40.0±15.5 | 33.3±27.2 |
| `[16] no-vision` | **89.0±13.4** | 41.7±9.62 |
| Random-search | 50.0±19.5 | 45.8±8.33 |
| Ours | 84.0±15.0 | **83.3±13.6** |

제안법은 simulation 최고값이 아니다. No-vision baseline이 simulation에서 89.0%로 더 높지만 실물에서는 41.7%다. 이 논문의 핵심 결과는 simulation 절대 성능보다 제안법의 작은 transfer gap과 실제 충돌 대응이다.

---

## 11. Geometry와 물체 Generalization

모든 policy는 330 g의 완전한 원통형 simulated plate 하나로 학습한다. 실물 평가는 서로 다른 크기·모양·무게의 plate와 cup을 사용한다. [원문 Fig. 5, Fig. 7]

| 물체 | 특성 | Ours real success (%) |
| --- | --- | ---: |
| Regular plate | 342 g, 약 `31.2×25.4 cm` | 83.3 |
| Medium plate | 266 g, 약 `21.8×16.8 cm` | 83.3 |
| Small plate | 295 g, 10.5 cm 표기 | 62.5 |
| Cup | 163 g, 학습에 없던 geometry | 66.6 |

Small plate와 cup은 높이 차이를 보정하기 위해 상대 EEF-pose observation의 Z translation에 **constant offset을 추가한 뒤** 평가했다. 따라서 네 물체 결과를 아무 조정 없는 순수 zero-shot geometry generalization으로 표현하면 안 된다.

Fig. 6의 multi-object 시연에서는 cup을 먼저 넣고 성공 뒤 grasp를 풀어 arm을 올린 다음, 사람이/시스템이 regular plate를 다시 파지해 cup으로 막힌 slot을 목표로 실행한다. 같은 insertion policy가 이웃 빈 slot로 plate를 옮기지만 object swap과 grasp 전환까지 policy가 해결한 것은 아니다.

---

## 12. Ablation: Memory와 Transfer 설계

Fig. 8의 bar 높이는 real success, bar 안 표기는 simulation success다. 모든 ablation은 regular plate로, full-scale target noise와 non-zero inference delay를 둔 같은 평가 조건에서 비교한다. [원문 Fig. 8, §IV]

| 설정 | Simulation (%) | Real (%) |
| --- | ---: | ---: |
| Full algorithm, $H=8$ stacking | 84 | **83.3** |
| Explicit stacked velocity | 96 | 66.7 |
| $H=16$ stacking | 65 | 25.0 |
| Recurrent policy | 86 | 16.7 |
| No history | 72 | 4.17 |
| PPO instead of SAC | 78 | 62.5 |
| No policy inference delay | 97 | 50.0 |
| No target-pose noise | 57 | 0.00 |

관측 stacking이 가장 잘 전이했고, 더 긴 $H=16$이나 recurrent policy가 자동으로 개선되지 않았다. 저자들은 큰 observation과 recurrent architecture가 learnable parameter를 늘리는 점을 가능한 원인으로 든다. No-history policy는 drift 후 고정 joint pose로 수렴하는 경향, no-delay policy는 충돌 반응성이 낮은 경향, no-noise policy는 slot의 위·아래 충돌을 구분하지 못하고 삽입 뒤 plate를 다시 드는 경향이 있었다.

이 표에는 **No Wrench** 조건이 없다. History 제거 결과를 Wrench의 독립 기여로 바꾸어 해석하면 안 된다.

---

## 13. Simulation Wrench 계산

MuJoCo는 equality, friction loss, contact constraint가 만든 전체 joint torque를 함께 보고한다. Supplementary A는 non-contact constraint 기여를 빼 contact torque를 구한다고 설명한다. 여기서 합의 $c$는 contact constraint를 제외한 constraint다. [원문 Supplementary A, PDF p. 7]

```math
\tau_{contact}=\tau_{constraint}-\sum_cJ_c^{T}(\theta)F_c.
```

그 뒤 end-effector frame $K$에서 로봇이 가하는 Wrench를 Jacobian transpose의 pseudoinverse로 계산한다. 음수 부호는 constraint가 로봇에 가한 torque를 로봇이 환경에 가한 값으로 바꾸기 위한 것이다.

```math
W=-J_K^{-T}(\theta)\tau_{contact}.
```

Simulation과 실물의 Wrench 생성 경로가 동일한 센서 모델은 아니다. Simulation은 constraint force/Jacobian 기반 계산이고, 실물은 Franka state estimator의 외력 추정값이다.

---

## 14. Related Work의 비교 구도

이 절은 원문 §II와 Table I이 선행연구를 분류한 방식이며, 인용 논문 전체를 이번 정독에서 다시 검증했다는 뜻은 아니다.

| 범주 | 기존 접근에 대한 원문의 관점 | 이 논문의 구분점 |
| --- | --- | --- |
| Handcrafted insertion | Impedance·force·vision-force control로 접촉을 처리 | Learned residual contact policy |
| Demonstration learning | Real expert demonstrations가 필요할 수 있음 | Expert data 없이 simulation RL |
| Real-world RL·adaptation | 실제 환경 training·fine-tuning·representation data 필요 | 실물 adaptation 없이 직접 배포 |
| Live vision insertion | 전체 상호작용을 볼 수 있는 unoccluded camera 요구 | 목표를 시작 전 한 번만 보고 실행 중 pose/Wrench 사용 |
| Tactile insertion | Rich tactile sensor와 실제 데이터가 필요할 수 있음 | Low-dimensional estimated Wrench 사용 |

저자들은 정확한 3D plate/holder model을 가정하지 않지만, simulated geometry와 목표 transform, 실물 ArUco 기반 target initialization은 사용한다.

---

## 15. 저자들이 밝힌 Limitation

### 15.1. 큰 수평 초기 오차

Stage 2 시작 EEF pose와 target pose 사이의 horizontal gap이 크면 성능이 낮다. Noise 범위를 넘어서는 전역 탐색 능력이 입증된 것은 아니다. [원문 §IV, PDF p. 6]

### 15.2. Base joint 자세

Base motor가 center에서 멀리 회전한 자세에서는 simulation training 범위에 포함했음에도 실물 성능이 낮다. 저자들은 OSC에 쓰인 inertial parameter 식별 오차를 원인으로 추정한다. 이는 검증된 원인 규명이 아니라 저자 가설이다. [원문 §IV, PDF p. 6]

### 15.3. Jam recovery

Fig. 9는 collision에 jammed된 뒤 회복하지 못하는 사례를 보여 준다. 충돌을 이용한다고 해서 모든 contact mode에서 안정적으로 탈출하는 것은 아니다.

### 15.4. 모델·시스템 범위

Soft gripper dynamics를 simulation에 정확히 모델링하지 않았고, grasp와 obstacle-free approach는 별도 전제다. 실물 success detector의 세부 구현도 재현에 충분할 만큼 명시되지 않았다.

---

## 16. Future Work와 미명시 사항

### 16.1. 저자가 명시한 Future Work

결론에서 base motion이 manipulation uncertainty의 큰 원인이 되는 mobile manipulation에 이 시스템이 유용할 수 있다고 보고, **mobile manipulator와 통합**하기를 희망한다고 명시한다. [원문 §V, PDF p. 6]

### 16.2. 원문에 명시되지 않은 항목

- Wrench 관측을 완전히 제거한 ablation과 force/moment 성분별 비교
- 외장 F/T 센서 대비 Franka 추정 Wrench의 정확도·대역폭·noise 정량화
- Real success detector의 센서, height/axis threshold, high-force jam threshold
- ArUco target 측정 오차의 실측 분포와 hand–eye calibration 오차
- Small plate/cup에 적용한 Z-offset의 정확한 수치
- 물체 파지 자동화와 막힘 물체의 pose·종류를 바꾼 체계적 robustness 평가
- Mobile manipulator 통합의 구체 architecture·실험 계획

---

## 17. 이 논문에서 직접 말할 수 있는 것과 없는 것

| 직접 근거가 있는 주장 | 이 논문만으로 말할 수 없는 주장 |
| --- | --- |
| 초기 목표 측정 후 pose·6D Wrench 8-step history로 contact-rich insertion을 수행했다 | 완전 무시각·무보정으로 작업했다 |
| 실물 데이터·fine-tuning 없이 simulation policy를 Panda로 옮겼다 | 아무 실물 setup·calibration도 필요 없다 |
| Target-pose noise, inference delay, memory representation이 sim-to-real에 중요했다 | Wrench가 성공률을 몇 %p 높였는지 분리했다 |
| Regular plate에서 `83.3±13.6%`, simulation에서 `84.0±15.0%`를 기록했다 | 모든 geometry에서 동일 성능으로 일반화한다 |
| 막힌 target slot에서 이웃 빈 slot로 이동하는 행동을 보였다 | 자유 물체 sweeping·재파지·전역 obstacle planning을 해결했다 |
| Small plate와 cup에도 전이했지만 constant Z-offset을 적용했다 | 모든 물체에 parameter adjustment 없는 zero-shot이었다 |

---

## 18. 재현 시 확인할 항목

- Actor observation의 Wrench frame, sign, bias·gravity·Coriolis·acceleration 제거 순서
- 20 Hz observation stacking에서 frame 누락·timestamp alignment·action latency 처리
- Main text 45°와 Table III 50° 중 실제 rotation action scale
- Target-noise curriculum schedule과 partial-insertion pose sampling 분포
- Simulation/real Wrench magnitude scaling과 normalization 여부
- Success detector, drop detector, torque/joint limit의 실제 threshold
- Z-offset 적용 조건과 물체별 offset 값
- Soft gripper에서 grasp slip이 Wrench history에 만드는 변화

이 노트는 논문의 원문 정독 기록이다. 코드가 공개되어 있다는 사실은 코드 실행·학습 재현이나 hardware behavior 검증을 완료했다는 뜻이 아니다.
