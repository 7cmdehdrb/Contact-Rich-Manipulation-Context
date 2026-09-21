# FoAR: Force-Aware Reactive Policy for Contact-Rich Robotic Manipulation

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [원래 Wrist Wrench 조사 W1](../reviews/2026-09-21_wrist-wrench-manipulation-survey.md#w1-foar--외장-손목-센서와-wrench-이력)

## 1. 논문 정보와 확인 범위

- **제목:** FoAR: Force-Aware Reactive Policy for Contact-Rich Robotic Manipulation
- **저자:** Zihao He, Hongjie Fang, Jingjing Chen, Hao-Shu Fang, Cewu Lu
- **게재:** IEEE Robotics and Automation Letters, Vol. 10, No. 6, pp. 5625-5632, 2025; IROS 2025 발표
- **DOI:** [10.1109/LRA.2025.3560871](https://doi.org/10.1109/LRA.2025.3560871)
- **출판 확인:** [저자 공식 저장소의 IEEE 서지](https://github.com/Alan-Heoooh/FoAR#citation) · [IEEE 문서 번호 10964857](https://ieeexplore.ieee.org/document/10964857/)
- **확인 원문:** 사용자 제공 arXiv:2411.15753v2, 2025-05-02, PDF 9쪽 전체
- **원문 PDF SHA-256:** `bc6061404a8d41d1cf23288385bb6604b87494d329c7a572074d37e6516c53fd`
- **원문이 안내한 자료:** [프로젝트 페이지](https://tonyfang.net/FoAR/) · [저자 코드·데이터 저장소](https://github.com/Alan-Heoooh/FoAR)
- **이번 정독에서 확인하지 않은 자료:** 코드 실행 결과, 공개 데이터 원본, 보충 영상, 원문이 인용한 54편의 전체 본문

원문 PDF를 텍스트 추출하고 9개 전 페이지를 PNG로 렌더링하여 본문, Algorithm 1, Table I-V, Fig. 1-5, Appendix A-B와 표의 check mark 배치를 대조했다. 아래의 `[원문 §…, PDF p.…]`는 이 첨부 PDF의 페이지 기준이다.

**핵심:** FoAR는 현재 RGB-D point cloud와 과거 약 2초의 외장 6축 F/T 이력을 함께 사용하여 미래 end-effector action chunk를 생성하는 imitation-learning policy다. 별도의 future contact predictor가 F/T feature의 반영 비율을 조절하고, 배포 시에는 예측된 접촉 구간에서 현재 힘·모멘트가 부족할 때 action을 예측 진행 방향으로 6 mm 보정한다. 실제 wiping·peeling·chopping에서 vision-only 및 단순 F/T fusion 기준선보다 높은 품질 점수와 action success rate를 보고한다. [원문 Abstract, §III-IV, Appendix A]

다음 경계를 먼저 유지해야 한다.

- 손목에 **OptoForce F/T 센서를 별도로 장착**한 사례다. 관절 토크 기반 외력 추정이 아니다.
- F/T는 6축 전체가 정책 입력에 들어가지만, reactive correction의 조건은 힘·모멘트 threshold다. 보정 방향은 측정 Wrench 방향이 아니라 예측 action chunk에서 계산한다.
- 정책은 실행 중 전면 RGB-D 카메라의 point cloud를 계속 사용한다. Blind manipulation 검증이 아니다.
- FoAR는 RL이 아니라 실물 expert demonstration을 이용한 imitation learning이다.
- tactile sensor는 사용하지 않는다.

---

## 2. 문제 설정과 연구 동기

### 2.1. Vision-only 정책이 놓치는 정보

접촉 전후의 RGB 또는 point cloud 차이는 작을 수 있다. 반면 접촉 자체는 힘과 모멘트를 발생시키므로 F/T는 접촉 상태와 물리적 상호작용을 직접 반영한다. 저자들은 assembly, wiping, peeling처럼 접촉을 오래 유지하거나 정밀하게 조절해야 하는 과업에서 vision-only policy가 이 정보를 갖지 못한다고 본다. [원문 §I, Fig. 1, PDF pp. 1-2]

### 2.2. 단순한 전체 구간 fusion의 문제

Wiping 같은 긴 과업에는 도구 집기, 접근, 표면 접촉, 도구 내려놓기가 함께 있다. F/T가 주로 유용한 구간은 접촉 중이지만, 실제 센서는 비접촉 구간에도 잡음을 출력한다. F/T를 항상 같은 비중으로 결합하면 비접촉 단계의 행동을 방해할 수 있다는 것이 FoAR의 출발점이다. [원문 §I-II, PDF pp. 1-2]

### 2.3. 연구 질문

원문 §IV는 네 질문을 둔다.

1. F/T 통합이 contact-rich 과업의 성능과 조작 정밀도를 높이는가?
2. Future contact 기반 fusion이 token 추가나 단순 feature concatenation보다 효과적인가?
3. Contact predictor, reactive correction, 높은 F/T 주파수가 성능에 기여하는가?
4. 실행 중 환경 교란에도 성능을 유지하는가?

---

## 3. Related Work의 비교 구도

이 절은 원문 §II가 선행연구를 분류한 방식이다. 인용 논문 각각을 이번 정독에서 다시 검증했다는 뜻은 아니다.

| 범주 | 원문이 인정하는 역할 | FoAR가 구분하는 지점 |
| --- | --- | --- |
| 고전 force control | 저수준 접촉 제어와 정밀한 상호작용 | 정확한 모델·사전 전략·추가 제어 파라미터에 의존할 수 있음 |
| 학습 정책의 F/T 입력 | Vision policy에 F/T와 compliance/stiffness 출력을 추가 | 이미 물체를 잡았거나 도구가 고정된 접촉 구간을 중심으로 평가하는 경우가 많음 |
| Force trajectory 출력 | Diffusion policy로 wrench·feedforward force·desired force 예측 | Hybrid/admittance/impedance controller가 별도로 필요할 수 있음 |
| Audio·tactile·force multimodal imitation learning | 접촉 관련 보조 정보를 제공 | 각 modality를 어느 단계에서 얼마나 반영할지가 남음 |
| RISE | Single-view point cloud 기반 실물 imitation-learning 기준선 | F/T 이력, contact-aware fusion, reactive correction이 없음 |

FoAR는 force control law 자체나 새로운 F/T 센서를 제안하지 않는다. **기존 RISE backbone에 F/T 시계열 인코더와 future-contact-gated fusion을 붙이고, 같은 contact probability를 간단한 배포 보정에도 사용하는 것**이 핵심이다. [원문 §II-III]

---

## 4. 실험 플랫폼과 센서

| 항목 | 원문에 명시된 내용 | 확인 위치 |
| --- | --- | --- |
| 로봇 | Flexiv Rizon | §IV-A, PDF p. 4 |
| 그리퍼 | Dahuan AG-95 | §IV-A |
| 손목 F/T | OptoForce sensor, robot flange와 gripper 사이 장착 | §IV-A |
| 시각 | 작업 공간 앞의 Intel RealSense D435 RGB-D camera | §IV-A |
| 작업 공간 | 45 cm × 60 cm × 40 cm | §IV-A |
| 계산 장치 | Intel Core i9-10900K, NVIDIA RTX 3090 | §IV-A |
| F/T 입력 | 시간당 6성분, 약 100 Hz | §III-A, §IV-A, Appendix A |
| 시각 입력 | 현재 RGB-D에서 만든 single-view point cloud; predictor에는 현재 RGB도 사용 | §III, Appendix A |
| Demonstration | Haptic teleoperation | §IV-A, Protocols |

센서 모델명이 OptoForce라고만 적혀 있으며 구체 제품 번호, force·torque range, resolution, accuracy, overload, 센서 좌표계, TCP로의 변환, zeroing, bias 제거와 filtering은 원문에 명시되지 않는다. 100 Hz는 이 논문이 사용하는 F/T sampling rate이며 센서의 제조사 최대 주파수라고 해석하지 않는다.

---

## 5. 과업과 데이터

### 5.1. Wiping

로봇이 eraser를 집고, 임의의 그림이 있는 whiteboard 위로 이동하여 지운 뒤, eraser를 용기에 내려놓는다. 기본 Wiping은 whiteboard 방향이 고정되고 Wiping (General)은 임의 방향을 허용한다. 접촉 단계에서는 표면 접촉을 지속해야 하지만 집기·접근·내려놓기는 비접촉 또는 다른 접촉 조건이다. [원문 Fig. 3, §IV-A]

### 5.2. Peeling

Peeler를 집고 cucumber 위로 정렬한 다음 껍질을 벗기고 도구를 용기에 내려놓는다. Grasp 위치가 위·아래·중앙·비대칭일 수 있어, 도구와 표면 사이 접촉을 유지하는 동작이 grasp 변화에 적응해야 한다. [원문 Fig. 3, §IV-B]

### 5.3. Chopping

Knife를 집고 pepper 위로 이동하여 자른 뒤 foam pad에 내려놓는다. 지속적인 표면 하중보다 순간 충격, 절단 깊이와 힘·모멘트 조절을 평가한다. [원문 Fig. 3, §IV-C]

### 5.4. 데이터와 평가 횟수

| 과업 | Expert demonstrations | 평가 |
| --- | ---: | ---: |
| Wiping | 50 | 방법당 20회 |
| Peeling | 50 | 방법당 20회 |
| Chopping | 40 | FoAR·RISE 각각 10회 |

평가 시 물체 위치를 randomize하되 방법 간에는 유사한 위치를 사용한다. Randomization 범위, demonstrator 수, 각 demonstration 길이, sensor synchronization error는 원문에 없다. [원문 §IV-A, Protocols]

---

## 6. 입력·특징·출력의 전체 흐름

실행 시 정보 흐름은 다음과 같다. [원문 Fig. 2, §III]

1. 현재 RGB-D에서 $N_t$개의 6차원 point로 구성된 point cloud $p_t$를 만든다.
2. 최근 $T_o$개 6D F/T 표본 $f_{t-T_o:t}$를 모은다.
3. Point cloud encoder가 scene feature $h_t^s$를, F/T encoder가 force feature $h_t^f$를 만든다.
4. 현재 RGB와 같은 F/T 이력으로 future contact probability $\phi(t)$를 계산한다.
5. $\phi(t)$로 F/T feature와 중립 embedding의 비율을 조절해 scene feature와 결합한다.
6. Diffusion action head가 미래 $T_a$ step의 end-effector action chunk를 출력한다.
7. 배포 시 contact probability와 현재 F/T threshold에 따라 action position을 소폭 수정하고, contact/non-contact별 temporal ensemble buffer에서 실행 action을 선택한다.

Algorithm 1에서 current EE pose $q_t$는 FoAR neural policy 호출 인자가 아니라 reactive correction의 진행 방향 계산에 사용된다. 원문은 출력 action의 전체 차원과 orientation 표현을 명시하지 않는다. Appendix는 output action과 point cloud를 camera coordinate에 정렬하고 gripper width도 정규화한다고 설명한다.

---

## 7. Point Cloud Encoder

RISE를 따라 5 mm voxel의 MinkowskiEngine sparse 3D encoder를 사용한다. Sparse encoder는 각 512차원인 point tokens를 출력하고, 4개 encoding block과 1개 decoding block의 Transformer가 이를 512차원 scene feature $h_t^s$로 만든다. Transformer의 $d_{model}=512$, $d_{ff}=2048$이고 readout token도 512차원이다. [원문 §III-B, Appendix A, PDF pp. 3, 9]

Point cloud는 사전에 정의한 작업 공간으로 crop하지만 tabletop point는 남긴다. 좌표는 robot workspace에 따라 $[-1,1]$로 정규화한다. 현재 한 시점의 scene observation이며, 원문은 visual history를 policy 입력으로 설명하지 않는다.

---

## 8. F/T 이력 인코더

한 시점의 $f_t\in\mathbb{R}^{6}$를 3-layer MLP `(64, 128, 512)`로 512차원 force token $F_t$에 투영한다. 최근 $T_o=200$ token, 즉 100 Hz에서 약 2초를 sinusoidal temporal positional encoding이 있는 Transformer로 처리해 512차원 force feature $h_t^f$를 만든다. Point cloud branch와 같은 Transformer 구성을 사용한다. [원문 §III-B, §IV-A, Appendix A]

이 구조는 F/T를 현재 threshold 하나로만 사용하지 않고, **6축 신호의 약 2초 시간 패턴**을 action 생성에 제공한다. 다만 학습된 feature가 접촉 위치, 물체 pose, 마찰 또는 slip을 명시적으로 복원하도록 감독되지는 않는다.

---

## 9. Future Contact Predictor와 feature fusion

### 9.1. Predictor 입력과 출력

별도의 ResNet18이 현재 RGB image $I_t$를 처리하고, 2-layer MLP `(128, 512)`가 F/T 이력을 처리한다. 두 출력을 연결한 linear layer가 미래 접촉 확률 $\phi(t)\in[0,1]$을 출력한다. Point cloud policy encoder를 predictor와 공유한 FoAR (3D-cls)가 크게 악화되어, 저자들은 contact 판별과 조작 행동이 요구하는 visual feature가 다르다고 해석한다. [원문 §III-B, §IV-B, Appendix A]

### 9.2. 접촉 label 생성

Demonstration에서 현재 시점을 중심으로 한 $[t-2\text{s},t+2\text{s}]$ 구간의 F/T가 사전 threshold를 넘는지 검사해 future contact label을 자동 생성하고 binary cross-entropy로 학습한다. 이는 학습 label 생성에 미래 표본을 쓰는 것이며, 배포 predictor가 미래 센서값을 입력받는다는 뜻은 아니다. Label 생성 threshold $\delta_{demo}$의 수치와 task별 값은 미명시다. [원문 §III-B, Appendix A]

### 9.3. Contact-gated fusion

Learnable neutral embedding을 $h^*$라 할 때 fused feature는 다음과 같다. 원문은 이 식에 번호를 붙이지 않았다. [원문 §III-B Feature Fusion, PDF p. 3]

$$
h_t=\left[h_t^s;\,\phi(t)h_t^f+\left(1-\phi(t)\right)h^*\right].
$$

$\phi(t)$가 크면 force feature를 강조하고, 작으면 force branch를 중립 embedding 쪽으로 보낸다. 실제로 F/T 입력을 제거하는 hard switch가 아니라 연속적인 feature weighting이다.

---

## 10. Diffusion action head와 학습 목적

Fused feature $h_t$를 조건으로 CNN diffusion head가 noisy action trajectory를 점진적으로 denoise한다. $T_a=20$ step을 예측하며 학습 100회, 추론 20회의 DDIM denoising iteration을 사용한다. [원문 §III-B, Appendix A]

Demonstration action에 대한 diffusion $L_2$ loss와 contact predictor의 binary cross-entropy를 결합한다. 원문은 이 식에도 번호를 붙이지 않았다. [원문 §III-B Supervision, PDF p. 3]

$$
\mathcal{L}=\mathcal{L}_{action}+\alpha\mathcal{L}_{predictor},\qquad \alpha=0.1.
$$

Training은 NVIDIA A100 2개, batch size 240, 초기 learning rate $3\times10^{-4}$, warmup 2,000 step, cosine decay를 사용한다. RISE와 같은 point-cloud augmentation 및 color jitter를 적용한다. Epoch 수, 총 gradient step, wall-clock 학습시간과 random seed 수는 원문에 없다. [원문 Appendix A]

---

## 11. 배포 시 Reactive Control

### 11.1. 상태 구분과 두 buffer

Future contact probability가 $\delta_{\phi}=0.9$보다 작으면 non-contact buffer, 이상이면 contact buffer에 예측 action chunk를 넣는다. 두 구간이 서로의 temporal ensemble에 간섭하지 않도록 buffer를 분리한다. [원문 Algorithm 1, Appendix A]

### 11.2. 부족한 하중에서의 위치 보정

Contact 구간에서 현재 force가 $\delta_f=8$ N보다 작고 torque가 $\delta_t=5$ N·m보다 작을 때 insufficient force/torque로 판단한다. 미래 $T_f=5$개 action position의 평균과 현재 EE position의 차이로 진행 방향을 만들고, 예측 action position을 $\epsilon=0.006$ m만큼 그 방향으로 이동한다. 개념식은 Algorithm 1의 12-14행을 다음처럼 읽을 수 있다.

$$
d=\mathrm{avg}\!\left(a_{t:t+T_f}^{pos}\right)-q_t^{pos},\qquad a_{t:t+T_a}^{pos}\leftarrow a_{t:t+T_a}^{pos}+\epsilon\frac{d}{\lVert d\rVert_2}.
$$

여기서 측정 Wrench의 방향으로 action을 움직이는 것은 아니다. Wrench는 부족 여부를 gate하고, 방향은 정책의 예측 trajectory가 제공한다. 또한 threshold 이상일 때 별도의 retreat, force limiting 또는 safety stop을 수행한다고 명시하지 않는다.

### 11.3. 저수준 제어

수정한 action을 단순 end-effector position controller로 보낸다. 원문은 compliance, admittance, hybrid force/position control을 사용하지 않았다고 명시한다. 따라서 결과는 학습 정책과 reactive action refinement의 결합 성능이며, 별도 force controller의 성능이 아니다. [원문 §III-C, Appendix A]

---

## 12. 평가 지표와 비교군

| 구분 | 정의 |
| --- | --- |
| ASR | 특정 action의 기본 수행 여부. 수행 품질과 무관한 action success rate |
| Wiping score | 완전히 지움 1, 부분 지움 0.5, 지우지 못함 0 |
| Peeling score | 벗긴 길이 비율을 demonstration 평균 0.778로 정규화 |
| Chopping | segment 수, segment 길이 비율의 평균과 표준편차, grasp/place ASR |

비교군은 ACT, Diffusion Policy, vision-only RISE와 다음 세 변형이다.

- **RISE (force-token):** F/T encoding을 RISE Transformer의 추가 token으로 입력
- **RISE (force-concat):** Force feature와 visual feature를 직접 concatenate
- **FoAR (3D-cls):** 별도 RGB predictor 대신 scene feature를 contact predictor와 공유

Score와 ASR을 혼용하면 안 된다. 예를 들어 wiping score 0.875와 wipe ASR 100%는 같은 지표가 아니다. [원문 §IV-A, Table I-II]

---

## 13. Wiping·Peeling 결과

Table I의 20회 평가 결과다. [원문 Table I, PDF p. 5]

| 방법 | Wiping score | Wipe ASR | Wiping General score | Wipe ASR | Peeling score | Peel ASR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ACT | 0.275 | 50% | 0.250 | 50% | 0.120 | 25% |
| Diffusion Policy | 0.400 | 60% | 0.350 | 50% | 0.386 | 70% |
| RISE | 0.500 | 75% | 0.500 | 80% | 0.377 | 50% |
| RISE (force-token) | 0.575 | 80% | 0.600 | 80% | 0.487 | 75% |
| RISE (force-concat) | 0.475 | 65% | 0.675 | 95% | 0.524 | 80% |
| FoAR (3D-cls) | 0.175 | 35% | 0.200 | 40% | 0.270 | 40% |
| **FoAR** | **0.875** | **100%** | **0.850** | **100%** | **0.756** | **100%** |

FoAR가 가장 높지만, vision-only RISE와의 차이에는 F/T 추가뿐 아니라 temporal encoder, contact-gated fusion, predictor와 reactive correction이 함께 들어간다. RISE force-token/concat은 F/T를 단순히 추가한 것만으로도 일부 조건에서 나아지지만 일관되지는 않는다. 예를 들어 기본 Wiping에서 force-concat score 0.475는 RISE 0.500보다 낮다.

---

## 14. Chopping 결과

FoAR와 RISE를 각각 10회 평가하고 demonstration을 oracle reference로 제시한다. [원문 Table II, PDF p. 6]

| 방법 | Segment 수 | 정규화 길이 평균 | 정규화 길이 표준편차 | Grasp ASR | Place ASR |
| --- | ---: | ---: | ---: | ---: | ---: |
| RISE | 1.8 ± 0.6 | 0.727 | 0.411 | 100% | 30% |
| **FoAR** | **3.9 ± 0.9** | **0.353** | **0.094** | **100%** | **70%** |
| Demonstration oracle | 5.0 ± 0.0 | 0.200 | 0.056 | 100% | 100% |

작은 평균 segment 길이와 표준편차는 더 많이, 더 균일하게 자른 결과를 뜻한다. 표본은 방법당 10회이며 RISE 외 다른 기준선은 Chopping에서 평가하지 않았다.

---

## 15. 설계 Ablation

### 15.1. Predictor·reactive correction·F/T 주파수

Wiping Table III의 결과다. Check mark는 첨부 PDF 표를 시각적으로 대조했다. [원문 §IV-D, Table III, PDF p. 6]

| F/T 주파수 | Future predictor | Reactive correction | Score | Grasp ASR | Wipe ASR |
| ---: | :---: | :---: | ---: | ---: | ---: |
| 100 Hz |  | ✓ | 0.650 | 100% | 85% |
| 100 Hz | ✓ |  | 0.650 | 100% | 80% |
| 2 Hz | ✓ | ✓ | 0.625 | 100% | 85% |
| 10 Hz | ✓ | ✓ | 0.800 | 100% | 100% |
| **100 Hz** | **✓** | **✓** | **0.875** | **100%** | **100%** |

100 Hz full configuration이 가장 높다. 그러나 F/T sampling frequency와 전체 policy inference·robot servo 주파수는 다르며, 이 표는 센서 제조사 대역폭 비교가 아니다.

### 15.2. Transformer와 MLP F/T encoder

Appendix Table V의 Peeling 결과다. [원문 Appendix B, PDF p. 9]

| 방법 | Score | Grasp ASR | Peel ASR |
| --- | ---: | ---: | ---: |
| RISE | 0.293 | 100% | 50% |
| FoAR (MLP) | 0.426 | 100% | 75% |
| **FoAR Transformer** | **0.588** | **100%** | **100%** |

저자들은 Transformer가 F/T의 temporal feature를 더 잘 처리한다고 해석한다. Table V의 FoAR score 0.588은 Table I의 0.756과 다르며, 원문은 두 표의 trial set 차이를 설명하지 않는다. 동일 숫자로 합치거나 직접 비교하지 않는다.

---

## 16. 실행 중 교란에 대한 결과

Wiping (General) 도중 이미 지운 곳에 새 그림을 쓰는 Rewrite, whiteboard를 옮기는 Move, 두 교란을 합친 Rewrite + Move를 평가한다. [원문 §IV-E, Table IV, PDF p. 7]

| 방법 | Original score | Rewrite score | Move score | Rewrite + Move score |
| --- | ---: | ---: | ---: | ---: |
| RISE | 0.500 | 0.500 | 0.600 | 0.500 |
| RISE (force-token) | 0.600 | 0.450 | 0.500 | 0.600 |
| **FoAR** | **0.850** | **0.800** | **0.850** | **0.800** |

FoAR의 grasp·wipe ASR은 네 조건 모두 100%였다. 저자들은 force-token 방식이 접촉과 비접촉을 오갈 때 F/T 잡음 때문에 불리하다고 해석한다. 각 disturbance condition의 trial 수는 해당 절에 별도로 명시되지 않는다.

---

## 17. 저자들이 밝힌 Limitation

### 17.1. Static F/T threshold

Future contact label과 reactive control이 task별 또는 고정 threshold에 의존한다. 평가한 과업에서는 작동했지만 복잡한 환경에서는 어려울 수 있다고 저자들이 명시한다. [원문 §V Conclusion, PDF p. 7; Appendix A]

### 17.2. 단순한 end-effector position control

현재 정책은 단순 EE position controller에 의존하므로 적응성에 한계가 있다고 밝힌다. [원문 §V, PDF p. 7]

독립적인 Limitation 절은 없지만 Conclusion에 위 두 항목이 명시되어 있다. 아래 §19의 실험 범위·ablation 해석은 정리자의 검토이며 저자 명시 한계와 구분한다.

---

## 18. 저자들이 제시한 Future Work

1. **고급 접촉 제어:** Compliance control 및 hybrid force/position control을 결합하여 성능을 높이는 방향. [원문 §V]
2. **로봇 형태 확장:** Dual-arm robot, humanoid robot, dexterous hand로 확장하여 더 복잡한 contact-rich manipulation을 수행하는 방향. [원문 §V]

이는 계획이며 현재 논문에서 구현·검증된 결과가 아니다.

---

## 19. 원문 근거에서 추가로 구분해야 할 범위

### 19.1. F/T 추가만의 독립 효과는 분리되지 않음

FoAR와 vision-only RISE의 비교에는 F/T 관측, temporal encoder, future contact predictor, gated fusion, reactive correction이 함께 달라진다. RISE force-token/concat이 단순 fusion 비교를 제공하지만, **같은 FoAR 구조에서 F/T만 제거한 ablation은 없다.**

### 19.2. Contact probability는 contact state의 유일한 복원이 아님

Predictor는 threshold로 만든 binary label을 학습하며, 접촉 위치·접촉 물체·마찰·slip·물체 pose를 출력하지 않는다. F/T가 그러한 상태를 유일하게 식별한다는 증거가 아니다.

### 19.3. 과업과 장비 범위

실물 한 로봇 setup에서 wiping·peeling·chopping을 평가했다. 자유 물체 pushing/sweeping, shelf clutter, 물체 pose가 보이지 않는 조건, 다양한 F/T 센서 교체, sim-to-real은 검증하지 않았다.

### 19.4. Reactive correction은 excessive-load control이 아님

Algorithm 1은 contact가 예상되는데 힘과 모멘트가 둘 다 threshold보다 작을 때만 예측 진행 방향으로 더 움직인다. 과도한 하중에 대한 retreat·stop·별도 force cap은 제시하지 않는다.

### 19.5. 통계 범위

Wiping·Peeling은 방법당 20회, Chopping은 FoAR·RISE 각각 10회다. Confidence interval, significance test, 여러 학습 seed의 분산은 보고하지 않는다.

---

## 20. 원문에 명시되지 않은 구현·계측 정보

| 항목 | 확인 결과 |
| --- | --- |
| OptoForce 정확한 모델·정량 사양 | 미명시 |
| F/T 좌표계·bias 제거·filter·calibration | 미명시 |
| Robot servo rate와 정확한 policy inference rate | 미명시. 본문은 action horizon의 낮은 주파수를 예시로 약 10 Hz라고 표현 |
| Action vector 차원·rotation 표현 | 미명시 |
| 전체 학습 step·epoch·시간·seed | 미명시 |
| 각 demonstration 길이와 demonstrator 수 | 미명시 |
| Predictor의 task별 label threshold 수치 | 미명시 |
| Table V와 Table I의 Peeling score 차이 원인 | 미명시 |
| 공개 코드와 논문 수치의 일치 여부 | 이번 작업에서 실행 검증하지 않음 |

---

## 21. 원문 위치 빠른 색인

| 주제 | 원문 위치 |
| --- | --- |
| 동기·기여 | Abstract, §I, Fig. 1, PDF pp. 1-2 |
| Related Work | §II, PDF p. 2 |
| 입력·RISE 대비 표기 | §III-A, PDF pp. 2-3 |
| Point cloud·F/T encoder와 fusion | §III-B, Fig. 2, 번호 없는 feature-fusion·loss 식, PDF p. 3 |
| Reactive correction | §III-C, Algorithm 1, PDF pp. 3-4 |
| 과업 | Fig. 3, PDF p. 4 |
| 장비·비교군·지표·protocol | §IV-A, PDF pp. 4-5 |
| Wiping·Peeling | §IV-B, Table I, Fig. 4, PDF pp. 5-6 |
| Chopping | §IV-C, Table II, Fig. 5, PDF p. 6 |
| Predictor·reactive·주파수 ablation | §IV-D, Table III, PDF p. 6 |
| Dynamic disturbance | §IV-E, Table IV, PDF p. 7 |
| Limitation·Future Work | §V, PDF p. 7 |
| 구현 세부·encoder ablation | Appendix A-B, Table V, PDF p. 9 |

---

## 22. 한 문장 요약

**FoAR는 외장 손목 6축 F/T의 약 2초 이력을 current RGB-D point cloud와 결합하되 future contact probability로 F/T feature를 조절하고, 접촉 예정 구간의 부족한 하중을 간단한 action 보정으로 보완하여 실제 wiping·peeling·chopping 성능을 높인 imitation-learning system이다.**
