# The Role of Tactile Sensing for Learning Reach and Grasp — 원문 상세 정리

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 조사 · ICRA 2025 후보 선별](../reviews/2026-09-19_icra-2025-contact-sensing-screening.md#icra25-zhang-tactile-role)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **The Role of Tactile Sensing for Learning Reach and Grasp** |
| 저자 | Boya Zhang, Iris Andrussow, Andreas Zell, Georg Martius |
| 출판 | 2025 IEEE International Conference on Robotics and Automation (ICRA), Atlanta, USA, May 19–23, 2025, pp. 11817–11824 |
| DOI | [10.1109/ICRA55743.2025.11127409](https://doi.org/10.1109/ICRA55743.2025.11127409) |
| 원래 조사 | [ICRA 2025 후보 선별](../reviews/2026-09-19_icra-2025-contact-sensing-screening.md#icra25-zhang-tactile-role)의 후속 원문 정독 |
| 정리일 | 2026-09-19 |
| 확인한 원문 | 사용자 제공 IEEE 출판본 PDF 8쪽 전체. 본문 §I–V, Fig. 1–11, Table I–V, References [1]–[49] |
| 확인하지 않은 자료 | 코드·체크포인트·원시 데이터·추가 실험 로그, 인용된 선행논문의 개별 원문, 제조사 데이터시트, 다른 공개 버전과의 차이 |
| 원문 PDF SHA-256 | `070ebe5e7df074ef9a601b53d48bf0b83cd29984cacac3b00c2f3d7f8ec118e9` |

이 문서는 첨부 출판본 자체의 문제 정의, tactile representation, RL 환경, vision-noise 실험, sensor area/quantity 비교, generalization, sim-to-real, Limitation과 Future Work를 정리한다. 다른 연구에 대한 적용안은 포함하지 않는다.

**핵심:** 이 논문은 2-finger antipodal grasping에서 tactile sensor의 **측정량과 공간 해상도**를 체계적으로 분리해 비교한다. Tactile representation은 global binary contact(B), global force magnitude(M), global 3D force vector(V), 그리고 K개 local region별 binary(BK), magnitude(MK), 3D force vector(VK)로 구성된다. 완벽한 vision에서는 tactile 추가 효과가 거의 없지만, visual pose가 noisy하면 tactile이 성능을 개선하며 특히 **전체 3D force vector V와 local 3D force vector VK가 consistently 강한 결과**를 보인다. Sensor-area 실험에서는 **local VK에 concise global force V를 추가한 구성이 local-only보다 좋아지고**, 저자들은 좋은 sensing quantity가 넓은 sensing area보다 중요하다고 결론짓는다. [원문 §III-C, §IV-A–C, Fig. 7–8, Table III, PDF pp. 3–5]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 정의·기여와 Related Work |
| 3 | RL state/action/reward와 stability check |
| 4 | Isaac Gym 환경·Franka Panda·Minsight 기반 sensor approximation |
| 5 | B/M/V/BK/MK/VK tactile representation |
| 6 | Perfect vision과 imperfect vision 비교 |
| 7 | Memory length와 visual noise |
| 8 | Sensing area·local/global force 비교 |
| 9 | Object generalization |
| 10 | Real hardware sim-to-real |
| 11–13 | Discussion·Limitation·Future Work·미명시 사항 |
| 14 | 원문 위치 안내 |
| 15 | 핵심 메커니즘 요약 |

## 1. 제시하는 문제 상황

### 1.1 Reactive grasping에서 visual error를 contact feedback으로 보완

저자들은 static grasp-pose prediction이 빠르고 정확하지만, 긴 planning/execution horizon 동안 perception·calibration error가 누적될 수 있고 실패에 반응하기 어렵다고 설명한다. Reactive RL policy는 visual perception, proprioception, tactile feedback을 이용하여 이러한 오차에 대응할 수 있다. [원문 Abstract·§I, PDF p. 1]

문제는 tactile sensor마다 sensing area, resolution, measured quantity가 크게 다르지만 **2-finger RL grasping에서 어떤 tactile representation이 실제로 필요한지 체계적으로 비교한 연구가 부족하다**는 점이다. 이 논문은 특정 sensor 제품의 우열을 평가하기보다, tactile sensing을 area/resolution/quantity로 추상화하여 비교한다. [원문 §I·II, PDF pp. 1–2]

### 1.2 연구 범위는 2-finger antipodal reach-and-grasp

대상은 robot arm에 부착된 **2-finger antipodal gripper**다. Gripper 내부 자유도는 사실상 opening/closing 1 DoF이므로 multi-finger hand보다 in-hand manipulation 능력이 제한적이고 form-closure grasp가 어렵다. 이 때문에 robot arm motion 자체를 policy가 함께 제어한다. [원문 §I, PDF p. 1]

저자들은 이 setup에서 vision은 global geometry를 제공하고 tactile은 local adjustment를 제공하는 구도를 강조한다. 따라서 결과를 multi-finger dexterous manipulation 전체에 일반화하지 않는다. [원문 §I, §V, PDF pp. 1, 6]

## 2. Related Work — 원문이 구성한 비교 구도

### 2.1 Vision-only reactive grasping과 tactile RL

저자들은 vision-only grasp detector가 novel object에 잘 일반화할 수 있지만 single grasp pose를 출력하고 별도 path planning이 필요해 perturbation/perception error에 반응하기 어렵다고 설명한다. RL-based reactive grasping은 이를 보완하지만 대부분 vision+proprioception 위주다. [원문 §II-a, PDF pp. 1–2]

Tactile RL 관련 사례로는 binary contact를 이용한 sim-to-real, binary tactile grid+proprioception을 이용한 grasp adjustment, tactile intrinsic reward, visual+F/T transformer 등을 언급한다. 이 논문의 차별점은 **2-finger reach-and-grasp에서 tactile sensing area와 measured quantity를 함께 체계적으로 비교**하는 것이다. [원문 §II-a·c, PDF pp. 1–2]

### 2.2 Tactile sensor를 area와 measured quantity로 분류

원문은 tactile sensor를 다음 관점으로 비교한다.

- sensing coverage / area
- sensing units / resolution
- binary contact / force magnitude / force vector

Minsight, Insight, DenseTact, BioTac, GelSight, GelSlim, uSkin, binary taxel array, F/T sensor 등을 이 축으로 배치한다. 실물 실험에는 Minsight를 사용한다. [원문 §II-b, Fig. 2, PDF p. 2]

## 3. RL State, Action, Reward

### 3.1 State

정책 state는 네 부분으로 구성된다.

$$\mathbf{s}=[\mathbf{s}_{pp},\mathbf{s}_{visual},\mathbf{s}_{tactile},s_{step}].$$

- $\mathbf{s}_{pp}$: TCP Cartesian pose와 gripper opening size를 포함한 proprioception
- $\mathbf{s}_{visual}$: object type encoding과 object Cartesian pose
- $\mathbf{s}_{tactile}$: 실험 조건에 따른 tactile representation
- $s_{step}$: remaining episode step에 비례하는 scalar

[원문 §III-A, PDF p. 2]

즉, tactile representation 비교 실험에서도 policy는 tactile만 받는 것이 아니라 **proprioception + vision + tactile + time**을 함께 받는다.

### 3.2 Action

Action은 arm의 모든 joint position과 gripper opening width다.

$$\mathbf{a}_t=[j_1,\ldots,j_{n_{\mathrm{arm}}},j_{\mathrm{gripper}}].$$

Franka Panda에서는 $n_{\mathrm{arm}}=7$이다. 저자들은 operational-space control 대신 joint-level target을 직접 policy action으로 사용한다. [원문 §III-A·B, PDF pp. 2–3]

### 3.3 Main reward와 stability check

Main success reward $r_{\mathrm{grasp}}$는 policy rollout 뒤 **grasp stability check**에서 계산한다. Robot은 arm을 들어 올리고 orientation을 유지한 채 object에 random force를 가하고 기다린다. 이 동안 양 finger contact가 유지되는 시간을 $t_{\mathrm{inhand}}$로 누적한다.

$$r_{\mathrm{grasp}}=1000\frac{t_{\mathrm{inhand}}}{t_{\mathrm{total}}}.$$

[원문 §III-A, PDF p. 2]

### 3.4 Auxiliary reward

Auxiliary reward는 매 step에 제공되며 다음 요소를 포함한다.

- 양쪽 finger contact를 유도하는 touch term
- finger와 object 사이 접근을 유도하는 approach term
- 양쪽 force relation을 반영하는 force term
- force가 설정 threshold를 초과할 때 penalize하는 force penalty

원문 Table I은 penalty에서 $f_{\max}=3f_{\mathrm{penalty}}$를 사용한다고 정의한다. 다만 $f_{\mathrm{penalty}}$의 구체적인 수치는 본문에 제시되지 않는다. [원문 Table I, §III-A, PDF p. 2]

## 4. Simulation Environment와 Sensor Approximation

### 4.1 Robot과 환경

| 항목 | 원문 설정 |
| --- | --- |
| Simulator | Isaac Gym |
| Robot | Franka Panda, arm 7 DoF |
| Gripper | 2-finger antipodal gripper |
| Tactile | 각 finger에 sensor 1개 |
| Vision | wrist-mounted RGB camera |
| Objects | YCB + Google Scanned Objects |
| Target placement | precomputed stable orientation 중 random, reachable range 내 random position |
| Collision | rigid-body collision |
| Policy rate | 20 Hz |
| Raw observation collection | 매 policy step |

[원문 §III-B, Fig. 1, PDF p. 3]

Demo injection은 precomputed grasp position 기반 trajectory로 replay buffer를 prefill하는 방식이며, training speed를 높이지만 asymptotic performance는 바꾸지 않는다고 저자들이 설명한다. [원문 §III-B, PDF p. 3]

### 4.2 Minsight의 원문 명시 사양

실물 tactile sensor는 **Minsight**다.

| 항목 | 원문 명시 |
| --- | --- |
| Sensing area | 1740 mm² |
| Coverage | all-around |
| Force | normal + shear |
| Sampling rate | 60 Hz |

[원문 §III-C, PDF p. 3]

센서 분해능·정확도·최소 검출 힘·force range는 제공된 논문 본문에 별도 수치로 기재되지 않는다. 제조사 또는 원 논문 [5]의 사양을 이번 노트에 섞지 않는다.

### 4.3 Simulation tactile model

실제 deformable skin을 FEM으로 모델링하면 대규모 RL data collection에 너무 느리고, mesh-mesh contact도 불안정하므로 저자들은 fingertip을 primitive geometry로 근사한다. Sensor approximation은 **45 cuboid + 5 sphere**, 총 50개의 독립 force-vector sensing primitive로 구성한다. [원문 §III-C, Fig. 1c, PDF p. 3]

이 high-resolution approximation을 바탕으로 area와 quantity를 축약하여 서로 다른 sensor를 모사한다.

## 5. Tactile Representation

### 5.1 Sensing area / resolution

저자들은 세 수준의 sensing coverage를 정의한다.

1. **Single-unit sensor**
   - fingertip 전체를 하나의 unit으로 취급
   - total force를 측정
   - 원문은 이를 **finger base의 force-torque sensor를 모사하는 형태**라고 설명한다.

2. **K-feature sensor**
   - fingertip을 $K$개 region으로 나눔
   - $K=5,9,12$를 사용
   - independent taxel array를 모사

3. **Full-range sensor**
   - fingertip 전 표면에서 high-resolution force map을 출력하는 개념

[원문 §III-C, Fig. 2–3, PDF p. 3]

여기서 single-unit은 **wrist 6-axis wrench sensor와 동일한 장치가 아니다.** Finger 전체에서 합쳐진 force information을 하나의 unit으로 본 추상화이며, 본문 실험의 V는 각 finger별 3D force vector이다.

### 5.2 Measured quantity

Table III의 tactile state는 다음과 같다.

| 기호 | 의미 | 두 finger 기준 차원 |
| --- | --- | ---: |
| E | tactile 없음 | 0 |
| B | overall binary touch | $1\times2$ |
| M | overall force magnitude | $1\times2$ |
| V | overall 3D force vector | $3\times2$ |
| BK | region별 binary touch | $K\times2$ |
| MK | region별 force magnitude | $K\times2$ |
| VK | region별 3D force vector | $3K\times2$ |

[원문 Table II–III, §III-C, PDF pp. 3, 5]

Binary는 contact 여부만 유지하고, M은 magnitude를 추가하며, V는 force magnitude와 orientation을 함께 유지한다. BK/MK/VK는 같은 quantity를 spatially distributed region마다 제공한다.

## 6. 실험 설계와 RL 알고리즘

저자들은 SAC와 MPO 두 off-policy model-free RL algorithm으로 같은 비교를 수행한다.

| Method | Learning rates | Network | Hidden layers | Replay buffer |
| --- | --- | --- | --- | --- |
| SAC | $10^{-3}/10^{-4}$ | MLP | [256, 256, 512] | 2M |
| MPO | $10^{-3}/10^{-3}/10^{-2}$ | MLP | [256, 256, 512] | 2M |

원문 Table IV는 learning-rate 값만 제시하며 각 값이 정확히 어떤 optimizer/component에 대응하는지는 표에서 별도 열로 나누지 않는다. [원문 Table IV, PDF p. 4]

실험별 seed는 계산 시간에 따라 4–8개다. [원문 §IV, PDF p. 4]

## 7. Perfect Vision에서 tactile 효과

첫 실험에서는 visual state로 **정확한 object pose + one-hot object type**을 사용한다. Visual state는 5 successive observation을 쌓아 short-term memory를 구성한다. [원문 §IV-A, PDF p. 4]

Precomputed grasp 자체의 평균 success는 약 15%이며, demo injection을 사용하면 policy는 약 300k step에 수렴하고 약 60% success를 달성한다. [원문 §IV-A, PDF p. 4]

### 결과

Perfect vision에서는 서로 다른 tactile representation을 추가해도 in-distribution success가 거의 비슷하다. 저자들은 이 조건에서 **tactile sensing이 성능을 개선하지 않는다**고 해석한다. [원문 §IV-A, Fig. 4, PDF p. 4]

VK는 state-space의 61.2%를 차지하지만 이 큰 차원이 perfect-vision 조건의 성능을 크게 악화시키지는 않았다고 보고한다. [원문 §IV-A, PDF p. 4]

## 8. Imperfect Vision, Memory, Tactile

### 8.1 Visual noise

두 종류의 pose noise를 사용한다.

- **Offset noise:** episode마다 하나의 calibration-like error를 뽑아 episode 내에서 유지
- **OU noise:** 매 step 변화하는 Ornstein–Uhlenbeck process로 visual tracking noise를 모사

[원문 §IV-B, Fig. 6, PDF p. 4]

### 8.2 Memory length

Single-frame, 5-frame, 10-frame visual history를 비교한다.

- memory만으로 noise effect를 제거하지는 못한다.
- 5-frame memory가 가장 좋은 결과
- 10-frame은 오히려 performance 감소

저자들은 2-finger grasping에서는 short-term memory만 필요하다는 해석을 제시한다. [원문 §IV-B, Fig. 5, PDF p. 4]

### 8.3 Tactile quantity 비교

OU noise에서는 tactile 효과가 SAC에서 뚜렷하지 않고 MPO에서 작게 나타나며, policy가 여전히 vision에 많이 의존한다고 분석한다. Offset noise에서는 tactile이 더 낮은 variance와 나은 performance를 제공한다. [원문 §IV-B, Fig. 7, PDF pp. 4–5]

특히 **V와 VK가 반복적으로 다른 tactile type보다 우수**했다. 저자들은 antipodal grasping에서 force closure가 중요한 조건이므로 전체 contact-force orientation이 유용할 수 있다고 해석한다. [원문 §IV-B, Fig. 7, PDF p. 5]

Binary tactile은 contact를 효과적으로 등록하지만, 저자들은 **internal touch와 external touch 사이의 ambiguity**가 남기 때문에 robust learning algorithm이 필요하다고 적는다. [원문 §IV-B, PDF p. 5]

## 9. Sensing Area와 Global/Local Force

### 9.1 Taxel density

Noisy vision에서 $K=5,9,12$를 비교한 결과 저자들은 다음 경향을 보고한다.

$$
\mathrm{VK}^{12}
\sim
\mathrm{VK}^{9}
\ge
\mathrm{VK}^{5}.
$$

즉 local force-vector sensing에서는 너무 적은 taxel이 불리했다. [원문 §IV-C, Fig. 8, PDF p. 5]

### 9.2 Local tactile에 global force 추가

각 local VK에 overall force vector V를 추가한 조건도 비교한다. 결과는 원문의 표현대로 대략

$$
\{\mathrm{VK}^{5},\mathrm{VK}^{9},\mathrm{VK}^{12}\}+V
\ge
V
>
\mathrm{VK}^{5},\mathrm{VK}^{9},\mathrm{VK}^{12}
$$

의 경향을 보인다. 저자들은 **concise global force를 추가하면 global-only 또는 local-only보다 더 좋은 성능**을 얻는다고 해석한다. [원문 §IV-C, Fig. 8, PDF p. 5]

또한 global force input이 서로 비슷해 보이는 local state가 실제 grasping에 미치는 causal effect를 구분하는 데 도움이 될 수 있다고 가설을 제시한다. [원문 §IV-C, PDF p. 5]

### 9.3 Magnitude만으로는 충분하지 않았다

MK 조건은 대체로 tactile 없는 E와 비슷했고, MK+V는 V 단독보다 낮았다. 저자들은 이를 바탕으로 **sensing area를 넓히는 것보다 sensing quantity를 잘 선택하는 것이 더 중요하다**고 결론낸다. 특히 force orientation을 포함한 V가 magnitude-only보다 유용했다. [원문 §IV-C, Fig. 8, PDF p. 5]

이 결과는 2-finger antipodal grasping과 본 논문의 noise/reward/controller 조건 안에서 해석해야 한다. 모든 manipulation에서 dense local tactile이 불필요하다는 일반 명제로 확장하지 않는다.

## 10. Object Generalization

Object generalization 실험에서는 object type one-hot 대신 wrist RGB image를 사용하고 visual encoder를 pretrain한다. Google Scanned Objects와 YCB에서 최대 100개 object를 사용하며 texture와 lighting을 randomize한다. [원문 §IV-D, PDF p. 5]

10개에서 100개 object로 다양성이 증가하면 tactile 없는 E baseline performance는 떨어지지만, **simple overall force vector V는 성능을 비교적 유지**한다. [원문 §IV-D, Fig. 9, PDF pp. 5–6]

100개 object로 900k step 학습한 MPO policy를 63개 unseen object에 평가하면 seen/unseen 모두 성능이 감소하지만, V를 사용하는 policy가 tactile 없는 E보다 높은 success를 유지한다. 저자들은 tactile이 novel-object grasping generalization에 도움을 준다고 해석한다. [원문 §IV-D, Fig. 10, PDF pp. 5–6]

## 11. Real Hardware Sim-to-Real

### 11.1 실물 구성

| 항목 | 설정 |
| --- | --- |
| Robot | Franka Panda |
| Gripper | self-developed antipodal gripper |
| Tactile | fingertip당 Minsight 1개, 총 2개 |
| Object pose | FoundationPose |
| Policy frequency | 20 Hz |
| Low-level interpolation | joint impedance controller, 1000 Hz |
| Episode length | 100 step |
| Training delay model | action moving-average + 17 ms delay |
| Domain randomization | friction coefficient, controller parameter 등 |
| Training length | 1.6M step |
| Vision noise | OU + offset |
| Real trials | object/condition별 20회 |
| VK hardware | limited computational power 때문에 제외 |

[원문 §IV-E, Fig. 11, Table V, PDF p. 6]

### 11.2 Table V 결과

대표 object 세 개에 대한 average success는 다음과 같다.

| Tactile | Cola sim | Cola real | Cola disturb | Box sim | Box real | Box disturb | Banana sim | Banana real | Banana disturb |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E | 0.18 | 0.00 | 0.00 | 0.46 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 |
| B | 0.33 | 0.35 | 0.25 | 0.51 | 0.35 | 0.20 | 0.30 | 0.15 | 0.30 |
| M | 0.42 | 0.45 | 0.45 | 0.66 | 0.45 | 0.50 | 0.39 | 0.65 | 0.55 |
| V | **0.53** | **0.65** | **0.55** | **0.68** | 0.45 | 0.40 | 0.35 | **0.70** | 0.50 |
| BK | 0.45 | 0.20 | 0.25 | 0.53 | 0.20 | 0.40 | **0.46** | 0.15 | 0.30 |
| MK | 0.41 | 0.05 | 0.00 | 0.63 | 0.25 | 0.40 | 0.34 | 0.20 | 0.15 |

괄호 안 hard-coded closing 결과는 원문 Table V에 별도로 제시되어 있으나 위 표에서는 policy-controlled success만 정리했다. [원문 Table V, PDF p. 6]

### 11.3 Sim-to-real에서 global force가 유리했던 이유

저자들은 **V가 다른 setup보다 강한 sim-to-real performance**를 보였다고 정리한다. 반면 BK/MK 같은 denser local tactile은 실물 robot motion error로 인해 aggressive touch가 발생하면서 simulation과의 distribution shift가 더 커질 수 있다고 가설을 제시한다. [원문 §IV-E, PDF p. 6]

Tactile 없는 E는 policy-controlled real experiment에서 거의 0 success지만, rollout 뒤 hard-coded gripper closing을 추가하면 성공률이 올라간다. 저자들은 이를 tactile이 없을 때 policy의 gripper motion과 성공 grasp 사이의 correlation이 약하다는 신호로 해석한다. [원문 §IV-E, Table V, PDF p. 6]

Banana에서 일부 real result가 simulation보다 높은 현상은 deformable Minsight sensor의 넓어진 contact area와 high-friction silicone shell로 설명한다. [원문 §IV-E, PDF p. 6]

## 12. Discussion — 저자들의 결론

저자들의 핵심 결론은 다음과 같다.

1. **Imperfect vision 아래에서는 tactile 정보가 grasp success에 중요하다.**
2. 2-finger antipodal grasping에서는 **fine spatial resolution 자체는 필수적이지 않을 수 있다.**
3. Overall contact force의 **orientation을 포함한 V가 spatially distributed binary/magnitude taxel보다 더 유용**했다.
4. Local tactile만보다 **global force V를 함께 추가한 조건이 더 좋았다.**
5. 이 결론은 antipodal gripper의 제한된 manipulation capability와 point-like contact 특성의 영향을 받는다.

[원문 §V, PDF p. 6]

저자들은 point-wise contact인 antipodal gripper가 전체 success를 낮추는 주요 이유라고 보고하고, 같은 pipeline에서 surface-contact parallel gripper를 사용한 비교에서 success가 **0.93**으로 크게 높아졌다고 언급한다. [원문 §V, PDF p. 6]

## 13. Limitation — 저자들이 밝힌 한계

원문 §V에 명시적인 Limitations paragraph가 있다.

- 비교 실험은 대부분 **simplified, controlled environment**에서 수행
- Simulation tactile model은 **real sensor deformation을 무시**
- Tactile feedback은 rigid-body collision checking으로 high-resolution sensing을 근사
- SAC와 MPO가 다른 qualitative result를 보이므로 **algorithm/hyperparameter에 따라 결론이 달라질 수 있음**
- Sim-to-real 과정의 여러 추가 요소가 real-robot evaluation에 영향을 줌
- Computational resource 제한 때문에 online visual-tactile feature learning을 사용하지 않음

[원문 §V, PDF p. 6]

따라서 V가 모든 로봇·모든 과업에서 최적이라는 일반적인 sensor-design 결론으로 확대하면 안 된다.

## 14. Future Work — 저자들이 제시한 향후 연구

저자들은 두 가지 방향을 명시한다.

1. **Blind grasping**
   - active search와 information accumulation이 필요한 문제

2. **Multi-finger in-hand manipulation**
   - 2-finger antipodal gripper에서 얻은 tactile-resolution 결론이 더 높은 dexterity에서는 어떻게 달라지는지 확인

[원문 §V, PDF p. 6]

## 15. 미명시 사항·원문 주의사항

| 항목 | 확인 결과·주의 |
| --- | --- |
| Minsight 최대 force range·분해능·정확도 | 본문 미명시 |
| Binary threshold | sensor abstraction 정의만 제시하며 numerical threshold 미명시 |
| M/MK/V/VK의 force normalization | 본문에서 상세 수치 미명시 |
| SAC/MPO learning-rate 각 값의 정확한 component 대응 | Table IV에 값만 제시 |
| $f_{\mathrm{penalty}}$ | 기호는 있으나 수치 미명시 |
| Episode length in simulation baseline | §IV-E에서 hardware transfer용으로 100 step으로 늘렸다고만 명시. 원래 값은 본문에서 직접 수치 확인되지 않음 |
| Full-range high-resolution force-map setup의 세부 policy input | sensor taxonomy에는 정의하지만 주요 Table III 비교는 B/M/V/BK/MK/VK 중심 |
| V와 wrist 6-axis F/T의 동일성 | 동일하지 않음. V는 각 finger의 3D overall force vector |
| Minsight 60 Hz와 policy 20 Hz 사이 sample handling | 상세 aggregation/synchronization 미명시 |
| FoundationPose tracking latency/accuracy | 미명시 |
| Hardware VK 제외 | computational power 제한 때문. 실물에서 VK 성능을 직접 검증한 것이 아님 |
| Generalization unseen 63개 object의 개별 목록·trial 수 | 본문 미명시 |
| 코드 실행·재현 | 이번 작업에서는 수행하지 않음 |

## 16. 다시 읽을 때의 원문 위치

| 내용 | 위치 |
| --- | --- |
| 문제 정의·기여 | Abstract·§I, PDF p. 1 / 인쇄 p. 11817 |
| Tactile grasping Related Work | §II-a·c, PDF pp. 1–2 |
| Sensor taxonomy | §II-b, Fig. 2, PDF p. 2 |
| RL state/action | §III-A, PDF p. 2 / 인쇄 p. 11818 |
| Auxiliary reward·stability check | Table I, §III-A, PDF p. 2 |
| Isaac Gym·Franka·camera·object data | §III-B, Fig. 1, PDF p. 3 |
| Minsight 1740 mm²·normal/shear·60 Hz | §III-C, PDF p. 3 / 인쇄 p. 11819 |
| 50-force-vector tactile approximation | §III-C, Fig. 1c, PDF p. 3 |
| Single/K/full-range sensor abstraction | §III-C, Fig. 3, PDF p. 3 |
| B/M/V/BK/MK/VK 정의 | Table III, PDF p. 5 / 인쇄 p. 11821 |
| SAC/MPO parameter | Table IV, PDF p. 4 / 인쇄 p. 11820 |
| Perfect-vision 결과 | §IV-A, Fig. 4, PDF p. 4 |
| Visual noise·memory | §IV-B, Fig. 5–7, PDF pp. 4–5 |
| Binary ambiguity·V/VK 우위 | §IV-B, Fig. 7, PDF p. 5 |
| Taxel area + global force result | §IV-C, Fig. 8, PDF p. 5 |
| Object generalization | §IV-D, Fig. 9–10, PDF pp. 5–6 |
| Hardware setup·FoundationPose·20/1000 Hz | §IV-E, Fig. 11, PDF p. 6 |
| Sim-to-real success | Table V, §IV-E, PDF p. 6 / 인쇄 p. 11822 |
| Discussion·Limitation·Future Work | §V, PDF p. 6 |

PDF pp. 7–8은 참고문헌이다.

## 17. 핵심 메커니즘 요약

이 논문은 tactile sensing을 단순히 “있음/없음”으로 비교하지 않고, **공간 해상도와 물리량을 분리**한다. Contact-only binary B/BK, magnitude M/MK, direction까지 포함한 3D force vector V/VK를 구분하고, noisy vision 조건에서 어떤 정보가 실제 policy 학습과 sim-to-real에 도움이 되는지 분석한다.

가장 중요한 결과는 **global 3D force vector V가 강하고, local 3D force vector VK에 V를 추가하면 local-only보다 더 좋아진다**는 점이다. 반면 binary는 contact detection에는 유효하지만 internal/external touch ambiguity가 남고, magnitude-only local taxel은 이 setup에서 큰 도움이 되지 않았다. 저자들은 이를 바탕으로 2-finger antipodal grasping에서는 **좋은 sensing quantity가 단순한 spatial resolution 증가보다 중요**하다고 해석한다. [원문 §IV-B–C, Fig. 7–8, §V, PDF pp. 5–6]

다만 이 global force는 **fingertip당 3D force vector**이며 wrist 6-axis wrench가 아니다. 또한 policy는 visual object pose·proprioception과 함께 tactile을 사용한다. 따라서 이 결과는 “wrist F/T가 tactile을 대체한다”는 결론이 아니라, 이 특정 grasping setup에서 **global continuous force information과 local contact information이 서로 다른 역할을 가질 수 있음**을 보여주는 실험으로 읽는 것이 정확하다.
