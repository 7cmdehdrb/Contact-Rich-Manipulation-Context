# FORGE: Force-Guided Exploration for Robust Contact-Rich Manipulation under Uncertainty

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [원래 Wrist Wrench 조사 W7](../reviews/2026-09-21_wrist-wrench-manipulation-survey.md#w7)

## 1. 논문 정보와 확인 범위

- **제목:** FORGE: Force-Guided Exploration for Robust Contact-Rich Manipulation under Uncertainty
- **저자:** Michael Noseworthy, Bingjie Tang, Bowen Wen, Ankur Handa, Chad Kessens, Nicholas Roy, Dieter Fox, Fabio Ramos, Yashraj Narang, Iretiayo Akinola
- **게재:** IEEE Robotics and Automation Letters, 2025
- **출판 확인:** [IEEE 문서 번호 10925874](https://ieeexplore.ieee.org/document/10925874/) · [NVIDIA Research 출판 기록](https://research.nvidia.com/labs/srl/publication/noseworthy-2025-forge/)
- **확인 원문:** 사용자 제공 arXiv:2408.04587v2, 2025-01-02, PDF 13쪽 전체
- **원문 PDF SHA-256:** `ec7dc0cb6eda93b0e95dc025b1835ea98531996a76b094b375c5e7a45495b5e6`
- **원문이 안내한 자료:** [프로젝트 페이지](https://noseworm.github.io/forge/)
- **이번 정독에서 확인하지 않은 자료:** 코드 실행·실험 재현, 프로젝트 영상, 향후 공개 예정 코드, 원문이 인용한 65편의 전체 본문

원문 PDF를 텍스트 추출하고 13개 전 페이지를 PNG로 렌더링하여 식 (1)-(8), Table I-II, Fig. 1-10과 Appendix A-G를 대조했다. 아래의 `[원문 §…, PDF p.…]`는 첨부 PDF 기준이다.

**핵심:** FORGE는 pose 추정 오차가 있는 조립에서, 관절 토크로 추정한 말단 3축 힘과 사용자가 지정한 최대 허용 힘을 recurrent PPO 정책에 입력한다. 학습 중 controller·part·robot dynamics와 허용 힘을 무작위화하고, threshold 초과량을 보상에서 벌점으로 주어 정책이 controller gain 변화에도 힘을 조절하도록 한다. 같은 정책이 성공 여부도 출력하여 조기 종료와 force-threshold 자동 증분에 사용된다. Peg insertion, gear meshing, M16 nut threading, snap-fit과 planetary gearbox 조립을 sim-to-real로 평가한다. [원문 Abstract, §I, §III-V]

다음 경계를 먼저 유지해야 한다.

- 실제 정책 입력은 **6D Wrench가 아니라 EE 좌표계의 3D force**다. 원문은 torque sensing을 Future Work로 남긴다.
- 힘은 Franka Panda의 관절 토크에서 추정한다. 외장 손목 F/T 센서를 장착한 실험이 아니다.
- 정책은 noisy fixed-part pose를 계속 입력받는다. 현재 pose를 보지 않는 Blind manipulation 검증이 아니다.
- 정책이 물성값을 명시적으로 추정하지는 않는다. 이전 action과 recurrent memory, dynamics randomization으로 미관측 dynamics에 대응한다.
- 과도한 힘에 대한 학습 벌점은 simulation의 ground-truth force를 사용하고, actor에는 noisy force를 제공한다.

---

## 2. 문제 설정과 과업

### 2.1. 해결하려는 문제

저자들은 낮은 clearance와 pose uncertainty가 있는 조립에서 접촉 기반 탐색이 필요하지만, 공격적인 탐색은 부품 slip·손상을 일으킬 수 있다고 본다. 기존 sim-to-real 조립 정책은 접촉력을 직접 관측하지 않거나 controller gain 조정에 힘의 크기를 의존하는 경우가 있다. FORGE의 목표는 정책이 배포 시 지정된 허용 힘에 맞춰 행동을 바꾸고, 별도의 gain 재조정 없이 pose 오차를 탐색하도록 만드는 것이다. [원문 §I, PDF pp. 1-2]

### 2.2. 주요 과업

| 과업 | 기하·성공 조건의 핵심 | 별도 주의 |
| --- | --- | --- |
| 8 mm Peg Insertion | Socket과 diametrical clearance 0.5 mm; 바닥에서 1 mm 이내 | 위치 오차에서 탐색 필요 |
| Medium Gear Meshing | Peg와 clearance 0.5 mm; 인접 gear teeth 정렬 | 단순 삽입보다 회전 정렬 필요 |
| M16 Nut Threading | Nut를 최소 quarter-thread, 2.5 mm 낮춰 빠지지 않게 체결 | 초기 thread orientation을 한 wrist 회전으로 성공 가능한 범위에 둠 |
| Snap-fit | 실제 부품은 약 15 N이 필요한 변형 삽입 | 필요한 힘을 모른다는 가정에서 threshold 자동 조정 |
| Planetary Gearbox | Ring 1개, small gear 3개, large gear 1개, M16 nut 3개의 8개 primitive | 조립 순서는 사전에 알려짐 |

원문은 완전히 미지인 thread orientation은 다루지 않고 Future Work로 남긴다. Gearbox 실험에서도 grasp 위치와 조립 순서는 사전에 정한다. [원문 §II-A, §V-D/E, Appendix F]

---

## 3. POMDP와 정책 입출력

### 3.1. 상태와 미관측 dynamics

시뮬레이션 상태는 EE·고정부품·파지부품의 pose와 velocity, EE contact force, 그리고 robot·controller·part dynamics parameter $\Psi$를 포함한다. 그러나 actor는 전체 상태와 $\Psi$를 받지 않는다. [원문 §II-B]

### 3.2. Actor observation

모든 정책의 실행 관측은 다음과 같다.

- noisy EE pose $\hat{p}^{ee}\in SE(3)$와 velocity $\hat{v}^{ee}\in\mathbb{R}^{6}$
- EE frame의 estimated contact force $\hat{F}^{ee}\in\mathbb{R}^{3}$
- fixed part의 noisy pose estimate $\hat{p}^{fixed}\in SE(3)$
- previous action $a_{t-1}$
- FORGE에서는 deployment parameter인 scalar force threshold $F_{th}$

Held part pose·velocity와 dynamics parameter $\Psi$는 actor에 제공하지 않는다. Previous action과 recurrent network가 dynamics 차이를 간접적으로 구분하는 단서를 제공한다. [원문 §II-B, §III, §IV-B]

### 3.3. Action과 controller

정책 action은 fixed-part tip 기준의 $(x,y,z,yaw)$ 4D 상대 transform이다. Absolute target은 fixed-part pose estimate와 action을 결합하고 action scale $\lambda$로 clip한다. Task-space impedance controller는 다음 형태로 힘을 계산한다. [원문 식 (5)-(6), §II-B, §III-B]

```math
p_t^{targ}=\mathrm{clip}\!\left(\mathrm{combine}(a_t,\hat{p}^{fixed}),\lambda\right),\qquad F^{targ}=k_p\left(p_t^{targ}-p_t^{ee}\right)-k_dv_t^{ee}.
```

정책은 15 Hz로 target을 보내고, Franka impedance controller는 1 kHz로 동작한다. Roll·pitch action은 정책이 출력하지 않으며, upright part를 가정한다. [원문 §II-B, §IV-A, Appendix F]

### 3.4. Recurrent PPO와 asymmetric critic

Partial observability를 처리하기 위해 recurrent PPO와 asymmetric actor-critic을 사용한다. Simulation에서는 critic과 reward·success 판정에 privileged state를 사용할 수 있지만, real deployment actor에는 위 noisy observation만 제공한다. 각 task·방법마다 seed 3개를 학습하고, 실물 결과는 세 policy에 걸쳐 평균한다. [원문 §IV-B]

---

## 4. Force Threshold와 보상

### 4.1. Threshold-conditioned policy

정책을 $\pi(a\mid o,F_{th})$로 조건화한다. 학습 중 $F_{th}$를 무작위화하므로, 배포 시 task에 맞는 허용 힘을 바꿔도 정책을 다시 학습하지 않는 것을 목표로 한다. 기본 세 과업의 학습 범위는 5-10 N이고, 실험 배포의 대표 threshold는 7.5 N이다. [원문 §III-A, Appendix A Table II]

### 4.2. Excessive-force penalty

측정 힘의 norm이 threshold를 초과한 만큼 선형 벌점을 준다. [원문 식 (3), §III-A]

```math
R_{contact\,pen}(F_t^{ee})=-\beta\max\!\left(0,\lVert F_t^{ee}\rVert_2-F_{th}\right).
```

Peg의 $\beta$는 0.2, gear와 nut는 0.05다. Simulation actor 입력에는 1 N noise가 있는 force를 사용하지만, 이 penalty 계산에는 ground-truth force를 사용한다. 따라서 실물에서 동일 보상을 계산해 online RL을 수행한 것이 아니다. [원문 §IV-B, Appendix A-B Table II]

### 4.3. Task reward

기본 task reward는 held part keypoint와 target keypoint 거리의 logistic kernel, placement bonus, success bonus로 구성된다. Nut threading은 sub-millimeter 단계까지 구분해야 하므로 coarse·fine kernel을 합친다. [원문 식 (2), 식 (8), Appendix B]

```math
K_{a,b}(d)=\left(e^{-ad}+b+e^{ad}\right)^{-1},\qquad R_{kp}=K_{a_c,b_c}(d_t^{kp})+K_{a_f,b_f}(d_t^{kp}).
```

여기에 excessive-force penalty와 아래 success-prediction penalty가 결합된다. 원문은 전체 reward를 하나의 최종 합산식으로 다시 쓰거나 각 bonus의 수치 가중치를 모두 명시하지 않는다.

---

## 5. Dynamics Randomization

### 5.1. Controller randomization

Controller proportional gain $k_p$와 action scale $\lambda$를 함께 무작위화한다. 기본 과업의 범위는 $k_p\in[400,800]$, $\lambda\in[1.6,2.5]$ cm이며, 최대 명령 가능 힘의 범위는 6.4-20.0 N이다. 이 값들은 actor observation에 직접 넣지 않으므로, 정책은 force feedback으로 gain 차이에 대응해야 한다. [원문 §III-B, Appendix A Table II]

### 5.2. Part와 robot dynamics

- Part mass와 friction을 무작위화한다. Friction 범위는 peg 0.5-1.0, gear 0.38-0.75, nut 0.1-0.38이다.
- Robot joint friction 등의 차이를 근사하기 위해 각 force dimension에 0-5 N의 random dead zone을 둔다.
- Fixed-part pose, hand-relative pose, held-part 위치를 초기화할 때 무작위화한다.
- Fixed-part pose estimate에는 episode 단위 오차를, force와 EE pose에는 timestep 단위 Gaussian noise를 준다.

이 설계는 friction이나 mass를 실시간 추정하여 actor에 넣는 방식이 아니다. 여러 조건에서 나타나는 force·motion response를 recurrent policy가 처리하도록 학습 분포를 구성하는 방식이다. [원문 식 (4), §III-B, Appendix A]

---

## 6. Success Prediction과 자동 Threshold 조정

### 6.1. Early-termination action

Policy network가 motion action과 함께 $a_t^{ET}\in[0,1]$을 출력한다. Simulation의 true success label $y_t$와의 차이를 벌점으로 둔다. [원문 식 (7), §III-C]

```math
R_t^{ET}=-\left|a_t^{ET}-y_t\right|.
```

배포 시 $a_t^{ET}>p_{term}$이면 episode를 종료한다. Nut가 실제로 체결되었는지 확인하기 위해 위로 당기는 행동처럼, 성공 여부를 드러내는 행동이 정책에서 나타날 수 있다고 저자들은 설명한다.

### 6.2. Force-threshold tuning

Snap-fit처럼 필요한 힘을 모르면 7.5 N에서 시작해, timeout까지 성공이 예측되지 않을 때 다음 실행에서 5 N씩 threshold를 올린다. 이 과정은 한 episode 안에서 연속적으로 threshold를 바꾸는 online adaptation이 아니라, 실행 결과에 따라 다음 trial의 scalar conditioning 값을 변경하는 절차다. [원문 §III-C, §V-D]

---

## 7. 실험 장비와 평가 설계

| 항목 | 원문 내용 |
| --- | --- |
| 로봇 | Franka Panda |
| 힘 정보 | Panda joint-torque sensing을 EE-frame 3D force로 projection |
| 외장 F/T | 사용하지 않음; 외장 센서도 가능하다고만 언급 |
| 제어 | FrankaPy task-space impedance, policy 15 Hz, controller 1 kHz |
| Simulation | Isaac Gym Factory |
| Pose 오차 | 실물에서 calibrated pose에 0-5 mm artificial error 추가; gearbox만 perception system 사용 |
| 주요 비교 | IndustReal, No Force·No DR·No Force Penalty ablation, force·DR·penalty 없는 Baseline |
| 기본 실물 평가 | Table I 총 855 trials; 각 row 45 trials, fixed-part 위치 5개와 pose-error level 3개 |

No Force는 force observation만 제거한다. No FP는 force observation과 DR을 유지하고 excessive-force penalty를 제거한다. Baseline은 force observation·DR·force penalty가 없지만 success prediction은 유지한다. 따라서 각 비교의 차이를 혼합하면 안 된다. [원문 §IV-C, §V-A]

---

## 8. 기본 실물 결과

Table I의 핵심 결과다. 괄호는 standard error이며, success rate와 힘은 각 row 45회에서 계산했다. [원문 Table I, PDF p. 5]

| 과업 | 방법 | Success | Duration (s) | $F_{mean}$ (N) | $F_{max}$ (N) |
| --- | --- | ---: | ---: | ---: | ---: |
| 8 mm Peg | FORGE | 0.84 (0.05) | 2.82 (0.20) | 5.51 (0.24) | 12.84 (0.37) |
| 8 mm Peg | No Force | 0.82 (0.06) | 3.18 (0.36) | 7.09 (0.35) | 14.16 (0.39) |
| 8 mm Peg | IndustReal | 0.82 (0.06) | 3.41 (0.24) | 9.45 (0.14) | 21.15 (0.26) |
| Medium Gear | FORGE | 0.98 (0.02) | 3.14 (0.39) | 7.95 (0.11) | 15.10 (0.45) |
| Medium Gear | No Force | 0.93 (0.04) | 3.06 (0.29) | 8.49 (0.23) | 14.68 (0.39) |
| Medium Gear | IndustReal | 0.87 (0.05) | 8.44 (0.61) | 9.80 (0.16) | 20.48 (0.26) |
| M16 Nut | FORGE | 0.69 (0.07) | 11.38 (0.47) | 7.82 (0.13) | 14.52 (0.22) |
| M16 Nut | No Force | 0.40 (0.07) | 14.09 (1.11) | 8.34 (0.15) | 15.04 (0.17) |
| M16 Nut | IndustReal | 0.36 (0.07) | 22.27 (0.64) | 12.63 (0.31) | 22.34 (0.33) |

Force observation의 성공률 효과는 peg에서 0.84 대 0.82로 작고, nut에서 0.69 대 0.40으로 크다. 따라서 force가 모든 과업에서 같은 폭으로 성공률을 높였다고 쓰면 안 된다. 다만 FORGE는 두 baseline보다 대체로 평균·최대 힘이 낮고, nut처럼 slip에 취약한 과업에서 차이가 컸다.

No FP는 gain이 커질수록 평균 힘이 증가했고, nut에서는 항상 part가 gripper에서 빠져 결과를 보고하지 못했다. Gain sweep 180회에서는 FORGE가 여러 controller gain에서도 7.5 N threshold 부근의 낮은 힘과 높은 성공률을 유지했지만, No Force와 No DR은 일관성이 낮았다. [원문 §V-A-C, Fig. 5]

---

## 9. Pose uncertainty와 실패 양상

실물 평가의 pose error를 Low 0-1 mm, Medium 1-2.5 mm, High 2.5-5 mm로 나눴다. FORGE는 gear와 nut에서 모든 error level의 IndustReal보다 높았지만, 2.5 mm를 넘으면 전반적으로 성능이 저하됐다. 주요 실패는 peg·part가 서로 걸리거나, nut가 bolt에 정렬되기 전에 회전하여 thread가 맞지 않는 경우였다. [원문 §V-A-B, Fig. 3-4]

학습 noise를 $\sigma=2.5$ mm보다 크게 하면 학습이 불안정했다고 저자들이 보고한다. Curriculum이나 tactile sensor·wrist camera 추가가 도움이 될 수 있다고 논의하지만, 이 논문에서 검증하지는 않았다.

---

## 10. Success Prediction 결과

Table I에서 force observation이 있을 때 early-termination precision·recall과 delay가 전반적으로 좋아졌다. 예를 들어 M16 Nut의 FORGE precision/recall은 0.74/0.74, delay는 6.54 s이고, No Force는 0.33/0.33, 11.48 s다. Peg의 FORGE는 precision/recall 1.00/1.00이었다. [원문 Table I, §V-D]

Simulation의 fixed-time termination과 predicted termination 비교에서는 같은 success-rate 수준에서 predicted termination의 delay가 더 짧았다. 이는 force observation만의 효과가 아니라 learned success action과 termination rule의 결합 결과다. [원문 Appendix D, Fig. 8]

---

## 11. Snap-fit과 Threshold 자동 조정

실제 snap-fit은 성공에 약 15 N이 필요했다. 7.5 N에서 시작해 5 N씩 높이는 전체 tuning 절차를 10회 수행한 결과는 다음과 같다. [원문 §V-D, Fig. 6]

- 물리적 insertion은 10/10 발생했다.
- 성공 예측까지 포함한 tuning 절차 성공은 8/10이었다.
- 29회의 개별 policy execution 중 success prediction은 27회 정확했다.
- 대체로 threshold가 17.5 N이 되는 세 번째 실행에서 성공했다.

큰 초기 분포에서 높은 threshold를 처음부터 사용하면 성공률은 6/10으로 떨어졌다. 정렬 전에 큰 힘을 쓰면 grasp가 불안정해지고 part slip이 발생했기 때문이다. 저자들은 **한 개의 episode-wide scalar threshold가 task phase별 요구를 표현하지 못한다**는 한계를 명시한다.

---

## 12. Planetary Gearbox와 Geometry Generalization

### 12.1. Multi-stage assembly

전체 gearbox 조립 5회에서 primitive별 결과는 Ring 5/5, Small Gear 15/15, Large Gear 3/5, M16 Nut 15/15였고, 전체 조립은 3/5 성공했다. Large gear는 학습 때 한 개 gear와 맞물렸지만 실제로는 이미 삽입한 세 gear와 동시에 맞물려야 해 distribution shift가 컸다. Early termination은 fixed duration 대비 한 전체 trial에서 평균 65 s를 줄였다. [원문 §V-E, Appendix F]

### 12.2. Part geometry

Peg 8/12/16 mm, gear small/medium/large, nut M12/M16/M20에 대해 size별 specialist를 각각 학습하고 다른 size에 평가했다. 각 cell은 seed 3개 policy를 128회씩 평가한 값이다. 대체로 교차 size에서도 성능이 유지됐지만, medium/large gear에서 학습한 policy는 작은 gear의 작은 base에서 일반화가 가장 약했다. 한 policy가 geometry 전반을 일반화하도록 geometry randomization하는 것은 Future Work다. [원문 Appendix G, Fig. 10]

---

## 13. Related Work의 비교 구도

이 절은 원문 §VI가 선행연구를 분류한 방식이며, 인용 논문 전체를 이번 정독에서 다시 검증했다는 뜻은 아니다.

| 범주 | 원문이 보는 역할 | FORGE의 구분점 |
| --- | --- | --- |
| 고전 insertion·spiral search | Pose 오차에서 정해진 접촉 탐색 | Task-specific하며 큰 오차·다양한 과업에 제한 |
| Real-world RL | 실제 contact distribution에서 학습 | 안전한 접촉과 data efficiency 문제가 있음 |
| Sim-to-real assembly | Parallel simulation·privileged state 활용 | Force observation과 threshold-conditioned behavior를 추가 |
| Gain·compliance tuning | 힘의 크기를 controller에서 조정 | Gain 대신 해석 가능한 scalar threshold로 배포 조정을 단순화 |
| Success verification | 고정 시간, 센서 rule, 별도 verification policy | 주 정책이 실행 중 성공 확률과 행동을 함께 출력 |

FORGE는 새로운 impedance controller나 force estimator를 제안하지 않는다. 핵심은 force-conditioned recurrent RL, force penalty, dynamics randomization, success prediction을 하나의 sim-to-real 학습 구조로 묶은 것이다.

---

## 14. 저자들이 밝힌 Limitation

### 14.1. 큰 pose error와 학습 불안정

2.5-5 mm의 큰 error에서 성능이 낮아지고, training noise를 $\sigma=2.5$ mm 이상으로 키우면 학습이 불안정했다. Curriculum이나 추가 sensing이 필요할 수 있다. [원문 §V-A-B, PDF pp. 5-6]

### 14.2. 단일 force threshold

Snap-fit에서 정렬 전에는 낮은 힘, 체결 단계에서는 높은 힘이 필요했다. Episode 전체에 하나의 threshold를 사용하는 구조는 이러한 phase-dependent force requirement를 표현하지 못한다. [원문 §V-D, PDF p. 7]

### 14.3. 제한된 관측과 recovery

저자들은 작은 slip은 wrist camera나 tactile로 회복할 수 있을 가능성을 언급하지만, FORGE는 slip 자체를 피하는 방향이며 해당 recovery sensor·policy를 구현하지 않았다. [원문 §III-A]

### 14.4. 과업 가정

Nut thread orientation, upright part, 알려진 assembly sequence, 사전 grasp location 등 task-specific 가정이 남아 있다. 이 중 완전히 미지인 thread orientation은 저자가 명시적으로 Future Work로 남겼다. [원문 §II-A, Appendix F]

---

## 15. 저자들이 제시한 Future Work

1. **Torque sensing:** Force뿐 아니라 torque를 관측하여 더 효율적인 search strategy를 학습한다. [원문 §VII]
2. **Real-to-sim:** 실제 상호작용을 이용해 simulation model을 자동 조정하고 더 적응적인 행동을 만든다. [원문 §VII]
3. **Thread orientation:** 완전히 관측되지 않은 thread orientation에서도 nut threading을 수행한다. [원문 §II-A 각주]
4. **Geometry randomization:** 한 task policy가 여러 part geometry에 일반화하도록 geometry를 simulation에서 무작위화한다. [원문 Appendix G]

이 항목들은 제안이며 현재 논문에서 구현·검증된 결과가 아니다.

---

## 16. 원문 근거에서 추가로 구분해야 할 범위

### 16.1. Force sensing과 전체 FORGE 효과

No Force ablation은 직접 비교를 제공하지만, FORGE의 전체 성능에는 force penalty·DR·success prediction도 함께 작용한다. Peg에서 success 차이는 작고 nut에서 크므로, sensor 기여를 하나의 수치로 일반화하면 안 된다.

### 16.2. Estimated force와 F/T 센서

Franka joint torque를 EE 3D force로 projection한 값이다. 모멘트를 관측하지 않고 외장 F/T의 resolution·bandwidth·bias 특성을 검증하지 않는다. Wrist 6D Wrench 사례로 인용하면 부정확하다.

### 16.3. Blind manipulation과의 차이

고정부품 pose estimate를 모든 timestep에 관측한다. Pose에 noise는 있지만, 초기 시각 이후 물체 pose를 갱신하지 않는 현재 프로젝트의 Blind 조건과 동일하지 않다.

### 16.4. 안전 보장의 범위

Threshold 초과 벌점은 learned behavior를 유도하지만 hard constraint나 독립적인 safety supervisor는 아니다. Table I에서도 $F_{max}$가 7.5 N deployment threshold보다 크다. 따라서 threshold를 절대적인 force cap으로 해석하지 않는다.

### 16.5. 성공 판정의 학습용 정답

Success label은 simulation privileged state로 만든다. 실물에서는 이를 직접 관측하지 않고 predictor 출력으로 종료한다. 실물 Blind success 판정을 해결했다는 일반적 결론보다, simulation label로 학습한 success predictor가 특정 조립 과업에 전이됐다는 결과로 읽어야 한다.

### 16.6. 통계와 실험 범위

Table I은 총 855회로 규모가 크고 seed 3개를 사용하지만, task·robot·force estimation 방식은 제한되어 있다. Gearbox 전체 조립은 5회, snap-fit tuning은 10회다. 다른 robot, 자유 물체 pushing/sweeping, clutter, tactile 결합은 검증하지 않았다.
