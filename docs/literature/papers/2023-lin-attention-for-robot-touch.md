# Attention for Robot Touch — 원문 상세 정리

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Attention for Robot Touch: Tactile Saliency Prediction for Robust Sim-to-Real Tactile Control** |
| 저자 | Yijiong Lin, Mauro Comi, Alex Church, Dandan Zhang, Nathan F. Lepora |
| 출판 | 2023 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), Detroit, USA, October 1–5, 2023, pp. 10806–10812 |
| DOI | [10.1109/IROS55552.2023.10341888](https://doi.org/10.1109/IROS55552.2023.10341888) |
| 문헌 관리 식별자 | [IROS 2023–2025 제목 선별 보고서](../reviews/2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md)의 **IROS-S01**. 2026-09-16 사용자 임시 선정 목록의 첫 번째 논문이며, 이전 조사본의 R1–R7과 별개다. |
| 정리일 | 2026-09-16 |
| 확인한 원문 | 제공된 출판본 PDF 7쪽 전체. 본문 §I–V, 식 (1)–(10), Fig. 1–6, Table I–II, References [1]–[24] |
| 확인하지 않은 자료 | 보충 파일·영상, 저자 코드·설정·데이터·체크포인트, 이 논문이 인용한 선행연구의 세부 구현, 제조사 데이터시트. 기존에 다른 논문을 정리한 내용으로 본문의 빈칸을 채우지 않았다. |
| 원문 PDF SHA-256 | `806a84c298a9045f891ef497c4605430841524753a285b7f65dcad9ca5405690` |

[개별 논문 색인](README.md) · [문헌조사 자료](../README.md)

이 문서는 해당 논문 자체의 문제 상황, 관련 연구, 환경·센서, 학습·제어 방법, 실험, 저자들이 밝힌 한계와 향후 연구를 정리한다. 프로젝트 적용안은 포함하지 않는다. `[원문 §…, PDF p.…]`는 첨부 출판본의 위치이며, **PDF 1–7쪽은 인쇄 페이지 10806–10812**에 대응한다. `[2]` 등의 번호는 원문 참고문헌 번호다. 수식·표·그림은 실제 PDF 표시와 대조했다.

**핵심:** 이 연구는 물체를 밀어 목표 위치로 옮기는 정책을 새로 설계한 논문이 아니다. **목표 edge와 방해 물체가 동시에 촉각 센서에 닿을 때, 목표 edge의 접촉 표현을 분리하여 기존 pose 추정기와 edge-following 제어기가 방해 접촉에 끌려가지 않게 하는 연구**다. 두 개의 pix2pix GAN과 하나의 VAE를 사용하며, 학습한 saliency map을 PoseNet–PID 또는 image-based deep-RL 경로에 넣는다. 별도의 손목 F/T나 뉴턴 단위 힘 추정·추종 제어는 제시하지 않는다. [원문 Abstract, §I, §III–IV, PDF pp. 1–6]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 제시하는 문제·기여, Related Work의 비교 구도 |
| 3 | 로봇·센서 사양, 접촉 환경과 실험 조건 |
| 4 | tactile image·contact depth·saliency의 정의와 전체 구조 |
| 5 | ConDepNet의 대응 데이터·conditional GAN·L1 학습 |
| 6 | TacSalNet의 목표/잡음 합성·자동 label·학습 목적 |
| 7 | TacNGen의 VAE·학습/생성 절차·잡음 ablation |
| 8 | 학습과 실물 실행의 분리, PID·DRL로의 연결 |
| 9 | 정량 실험·그림·표·평가 기준 |
| 10–11 | 저자들이 밝힌 Limitation과 Future Work |
| 12–14 | 재현 정보의 공백·원문 주의사항·위치 안내·요약 |

## 1. 제시하는 문제 상황과 연구 목적

### 1.1 고해상도 촉각도 여러 접촉이 섞이면 제어를 잘못 유도한다

저자들의 출발점은 기존 tactile control 연구가 이상적인 접촉 조건에 집중하여, **예상하지 못한 다른 자극이 동시에 닿는 상황**을 충분히 다루지 않았다는 것이다. 센서가 고해상도 영상을 제공하더라도, 그 영상의 변형이 전부 조작 대상에서 온 것은 아니다. 목표 edge를 따라가야 하는 센서가 옆의 물체에도 닿으면, pose 추정기나 정책이 방해 물체의 접촉을 목표 특징으로 해석할 수 있다. [원문 §I, Fig. 1(b), PDF p. 1]

Fig. 1(b)의 예는 TacTip이 흰 원통의 edge와 분홍색 장난감에 동시에 접촉하는 상황이다. 필요한 것은 센서 전체에 생긴 변형을 더 많이 수집하는 것만이 아니라, **현재 과업에서 따라가야 하는 접촉 특징과 그렇지 않은 특징을 구분하는 것**이다. 이 논문에서 noise는 단순한 카메라 전자 잡음만을 뜻하지 않는다. 다른 물체가 유발한 실제 접촉 변형도 target 기준에서는 noise/distractor feature다. [원문 §I, Fig. 1, PDF p. 1]

### 1.2 왜 raw tactile image를 사람이 직접 labeling하지 않는가

TacTip의 marker 영상은 물체 표면의 외관을 그대로 보여 주는 사진이 아니다. 접촉에 따라 내부 marker가 움직인 결과이므로, 사람이 어느 부분이 목표 물체의 접촉이고 어느 부분이 방해 접촉인지 직관적으로 표시하기 어렵다. 또한 부드럽고 손상되기 쉬운 센서로 많은 종류의 방해 물체를 직접 접촉시키며 target–noise 결합 분포를 수집하는 데에는 물리적 부담이 있다. [원문 §I, §III-A, PDF pp. 1–3]

따라서 저자들은 실물 영상에 직접 사람이 saliency label을 다는 대신, **같은 상대 접촉 pose를 실물과 시뮬레이션에서 재현하고, 시뮬레이션 접촉 depth를 중간 표현과 학습 label로 이용**한다. 여기서 자동 labeling은 정답이 없다는 뜻이 아니라, 사람이 픽셀을 분류하지 않고 시뮬레이터와 데이터 생성 과정으로 정답을 확보한다는 뜻이다. [원문 §III-B–C, PDF p. 3]

### 1.3 제안과 실제 검증 범위

| 구분 | 원문에서의 내용 |
| --- | --- |
| 제안 개념 | tactile image에서 목표 특징에 해당하는 영역을 나타내는 tactile saliency |
| 표현 학습 | ConDepNet → TacSalNet의 합성 mapping과 TacNGen 기반 학습용 잡음 생성 |
| 지각 검증 | distractor가 있는 상태에서 목표 edge의 위치·방향 추정 |
| 제어 검증 | distractor가 있는 고정 물체의 2D edge를 한 바퀴 따라가기 |
| 제어기 | pose-based PID와 image-based deep-RL 두 종류 |
| 실험의 target feature | edge. 수식에는 일반적인 feature type을 정의하지만 실제 분석은 edge로 제한 |
| 이 논문에서 직접 검증하지 않은 것 | 물체 운반/pushing의 목표 도달, 임의 물체 식별, 여러 동일 종류 edge 사이의 사용자 지정 대상 선택, 다른 촉각 센서로의 실제 전이 |

마지막 행은 본문에서 확인한 실험 범위를 정리한 것이며, 저자들이 각각 독립된 한계로 선언했다는 뜻은 아니다. [원문 §I, §IV-A.2, §IV-C–D, §V, PDF pp. 1–2, 4–7]

## 2. Related Work — 원문이 구성한 비교 구도

이 절은 해당 논문이 선행연구를 설명한 방식의 정리다. 아래 인용 논문들의 원문·코드를 이번에 별도로 검증한 것은 아니다.

### 2.1 시각적 saliency와 touch 관련 기존 saliency

| 선행연구 묶음 | 이 논문에서 소개한 내용 | 이 연구와의 구분 |
| --- | --- | --- |
| Visual saliency [9], [12]–[15] | 시각 영상에서 더 주의를 끄는 영역·물체를 예측 | 이 연구는 센서 내부의 촉각 영상에서 과업에 필요한 접촉 영역을 다룸 |
| Xu et al. [16], Ni et al. [17] | 모바일 장치의 2D 영상과 사용자의 touch behavior를 연결 | 사람이 화면의 어디를 만지는지와 로봇 촉각 영상의 특징 분리는 다른 문제 |
| Lau et al. [18] | 사람이 접촉할 가능성이 높은 3D mesh 부위를 나타내는 tactile mesh saliency | 입력과 정답이 실제 tactile sensor image가 아님 |
| Jiao et al. [19] | sketch의 tactile saliency·depth·semantic category를 함께 예측 | sketch 해석과 실물 센서에 동시에 들어온 접촉 분리는 구분됨 |
| Jain et al. [20] | 시각 3D point cloud로 object saliency를 정해 유익한 촉각 데이터 수집을 유도 | 이 연구는 어디를 탐색할지보다 이미 얻은 tactile image의 목표 접촉을 추출 |
| Cao et al. [21] | Spatio-Temporal Attention Model로 tactile texture recognition | 현재 과업의 target edge와 distracting contact를 분리하는 제어 전처리와 목적이 다름 |

원문의 핵심 대비는 **‘touch와 관련된 saliency’라는 이름을 공유해도, 입력·정답·과업이 다르다**는 것이다. 여기서의 attention을 곧바로 Transformer의 self-attention이나 별도의 attention weight policy로 해석하지 않는다. 제시된 구현은 GAN 기반 saliency prediction과 VAE 기반 noise generation이다. [원문 §II–III, PDF pp. 2–4]

### 2.2 Tactile control과 이 연구의 위치

Introduction은 기존 tactile RL [2]–[4]과 contour/exploration [5]–[8]의 이상적인 실험 조건을 문제 배경으로 둔다. 실제 실험에서는 PoseNet [7], pose-based tactile servoing [11], image-based sim-to-real RL [2]를 기반 제어 방법으로 사용한다. 이 연구의 변경 대상은 이 방법들의 목적 자체가 아니라 **실물 distractor가 섞인 tactile 입력**이다. [원문 §I, §IV-C–D, PDF pp. 1, 5–6]

방법론의 주요 의존 관계는 다음과 같다.

| 원문 참고문헌 | 현재 논문에서 맡는 역할 |
| --- | --- |
| [2] Church et al., *Tactile sim-to-real policy transfer via real-to-sim image translation* | Tactile Gym, sim-to-real image-based control, pix2pix 학습 hyperparameter의 참조 |
| [7] Lepora & Lloyd, *Optimal deep learning for robot touch* | tactile pose prediction의 기반 |
| [11] Lepora & Lloyd, *Pose-based tactile servoing* | pose-based PID control의 기반 |
| [22] Isola et al., *Image-to-image translation with conditional adversarial networks* | 두 prediction network의 pix2pix GAN 방법 |
| [8], [23] Tactile Gym 2.0·DigiTac 관련 연구 | 저가 플랫폼과 다른 센서로의 확장 가능성을 설명하는 배경 |

이 의존 관계는 **현재 논문에 실제로 기술된 학습식과, 인용 논문·보충자료를 읽어야 알 수 있는 설정을 분리해서 읽어야 한다**는 뜻이다. [원문 §III-B–D, §IV-A, §IV-C–D, §V, References, PDF pp. 3–7]

## 3. 환경·로봇·센서와 상세 사양

### 3.1 로봇 플랫폼

실험에는 Dobot MG400 desktop robot 한 대를 사용하고, TacTip을 말단에 부착한다. 원문은 저가·고정밀의 tactile robot 플랫폼으로 소개하지만, 이 논문 자체에 MG400의 정량 장비 사양을 다시 제시하지는 않는다. [원문 §IV-A.1, PDF p. 4]

| 항목 | 이 원문에 명시된 내용 | 구분 |
| --- | --- | --- |
| 로봇 모델 | Dobot MG400 | 장비명 |
| 촉각 센서 장착 | TacTip을 end-effector로 사용 | 실제 실험 구성 |
| 로봇 전체 자유도 | 숫자 미명시 | 다른 MG400 논문의 사양으로 보충하지 않음 |
| 가반하중·최대 reach·footprint | 미명시 | 장비 사양 |
| 반복정밀도·절대정확도 | 정량값 미명시 | ‘high-accuracy’라는 정성 설명만 있음 |
| DRL 행동 출력 | x와 y | Fig. 5 및 Fig. 6 caption에 명시된 과업 행동 |
| Pose-based 경로 | edge의 y·Rz 예측, Fig. 5의 target pose y·Rz | 과업의 pose 변수이며 로봇 전체 자유도와 다름 |
| 제어 주기·통신 방식·속도·행동 크기 | 미명시 | 실험/실행 설정 |

### 3.2 TacTip과 측정 정보

TacTip은 부드러운 피부 안쪽의 돌출 pin 끝에 marker를 둔 광학식 촉각 센서다. 외부 접촉이 피부를 변형시키면 pin과 marker의 움직임이 나타나며, 이를 내부 카메라 영상으로 관측한다. 원문이 설명하는 transduction의 핵심은 pin에 의한 표면 변형의 증폭이다. [원문 §IV-A.1, PDF p. 4]

| 센서 항목 | 확인 결과 |
| --- | --- |
| 종류·모델 | marker-based optical tactile sensor, TacTip |
| 수량·배치 | 단일 TacTip을 로봇 말단에 부착하여 target edge와 distractor에 접촉 |
| 원시 관측 | 내부 marker의 움직임을 담은 tactile image |
| 수학적 입력 표현 | grayscale image, 각 픽셀 값 [0, 1] |
| 이미지의 실제 촬영/모델 입력 해상도 | 구체적인 픽셀 수 미명시. 식의 w×h는 기호 정의 |
| marker·pin 개수, 밀도·간격 | 미명시 |
| 센서 직경·피부 두께·재료·경도 | 이 원문에 정량 사양 미명시 |
| 공간 해상도·접촉점 위치 분해능 | 미명시 |
| 최대 측정 힘·압력·토크, 힘 분해능·정확도·최소 검출 힘 | 미명시. 본 방법은 물리 단위 힘을 출력하는 모델을 제시하지 않음 |
| frame rate·샘플링률·대역폭·지연 | 미명시 |
| 커버리지 | Fig. 1·4–6에서 tip 접촉 영상을 보여 주지만 유효 감지 면적·각도 수치는 미명시 |
| 별도 wrist F/T | 본 실험 구성에 제시되지 않음 |

**데이터 수집 시 누른 깊이 3–6 mm는 센서의 최대 측정 범위가 아니며, PoseNet의 위치 MAE는 센서 자체의 분해능이 아니다.** 또한 이후 생성하는 contact depth map의 픽셀은 [0, 1] 수준값으로 정의된다. 이것을 뉴턴·파스칼·밀리미터로 보정된 센서 출력이라고 바꾸어 기록하지 않는다. [원문 §III-A–B, §IV-A.2, §IV-C, PDF pp. 2–5]

### 3.3 실험 환경과 대상

| 단계 | 대상·환경 | 원문 위치 |
| --- | --- | --- |
| 대응 데이터 수집 | flat edge가 있는 square stimulus와 TacTip의 무작위 상대 접촉 | §IV-A.2, Fig. 4(a), PDF p. 4–5 |
| Noise generator 학습 | 반지름·각도가 다른 simulated cone-shaped distractor | §IV-A.2, Fig. 2(c), PDF pp. 2, 4 |
| Saliency ablation | target edge 옆의 고정 distractor가 있는 실물 접촉과 없는 접촉을 대응 | §IV-B, Fig. 3(a), PDF p. 4 |
| 정적 pose 추정 | bolt, soft-tined comb, wooden clip, toy figure, spoon을 edge 옆에 고정. 간격 7–14 mm | §IV-C, PDF p. 5 |
| Edge-following | square·volute·flower·foil, 각 물체 주변에 최소 4개 bolt distractor를 7–12 mm 간격으로 고정 | §IV-D, Fig. 6(a), PDF pp. 6–7 |

정적 실험의 toy figure·spoon 결과와 더 다양한 distractor를 사용한 움직임은 보충자료로 안내되어 있다. 이번 정량 정리는 본문·그림·표에 실제로 제시된 결과를 기준으로 하며, 보충 영상을 시청한 것으로 기록하지 않는다. [원문 §IV-C–D, PDF pp. 5–6]

## 4. 핵심 표현과 전체 정보 흐름

### 4.1 I, C, S는 서로 다른 영상이다

| 기호 | 뜻 | 포함하는 정보 |
| --- | --- | --- |
| $I$ | real grayscale tactile image | target와 distractor의 접촉이 함께 만든 marker 영상 |
| $C$ | contact depth map | 접촉 부위와 깊이 수준을 단순화한 영상. target/noise를 아직 구분하지 않음 |
| $C^F$ | target feature만의 contact depth map | 학습 시 분리해서 알고 있는 목표 접촉 표현 |
| $C^N$ | noise contact depth map | 학습용 방해 접촉 표현 |
| $S^F$ | tactile saliency map | target feature 영역을 나타내는 [0, 1] 영상 |
| $F$ | target feature type | 일반 정의에서는 edge/surface 등의 종류. 실제 실험은 edge |

저자들은 saliency의 픽셀을 해당 픽셀이 feature F에 속할 확률로 정의한다. 그러나 실제 label 생성에서는 **target-only contact depth map을 min–max 정규화**한다. 이 둘은 논문의 개념 정의와 구현을 각각 기록한 것이다. 이 학습 label을 사람의 주의 분포나 확률 보정이 검증된 물리적 접촉 확률로 해석하지 않는다. [원문 §III-A–C, PDF pp. 2–3]

### 4.2 직접 mapping을 두 단계로 분해

원문 식 (1): 원하는 최종 mapping.

$$
\psi_F(I):=S^F.
$$

원문 식 (2): real tactile image를 contact depth로 바꾸는 mapping.

$$
\phi(I):=C.
$$

원문 식 (6): contact depth에서 target saliency를 얻는 mapping.

$$
\delta_F(C):=S^F.
$$

원문 식 (7): 두 mapping의 합성.

$$
\delta_F\bigl(\phi(I)\bigr)=\delta_F(C)=S^F=\psi_F(I).
$$

이 분해의 목적은 marker 영상에서 사람이 직접 target/noise 영역을 labeling하기 어려운 문제를, **시뮬레이션에서 target와 noise를 따로 만들 수 있는 depth 표현의 문제로 옮기는 것**이다. 식 (7)은 원하는 mapping의 구성식이며, 학습된 네트워크가 모든 실물 입력에서 오차 없이 같다는 보증은 아니다. [원문 §III-A–C, PDF pp. 2–3]

### 4.3 학습용 network와 실행용 network

```text
학습 준비
  실물 tactile I + 같은 pose의 simulated depth C
    → ConDepNet 학습

  simulated cone 접촉 depth
    → VAE 학습 → decoder를 TacNGen으로 사용

  target-only depth C^F + TacNGen noise
    → 오염된 입력 C
  target-only depth C^F → min–max 정규화 → label S^F
    → TacSalNet 학습

실물 실행
  TacTip I → ConDepNet → C → TacSalNet → S^F
    ├─ PoseNet → edge pose → pose-based PID → 로봇
    └─ image-based deep-RL policy → x·y action → 로봇
```

TacNGen은 **학습에 사용할 noise feature를 만드는 모델**이다. 매 제어 step에서 noise를 생성해 행동을 결정하는 모델이 아니다. Fig. 5의 실행 경로에는 ConDepNet·TacSalNet과 선택한 제어 경로가 있으며, Fig. 2(c)의 VAE/decoder는 학습 데이터 생성 쪽에 놓인다. [원문 Fig. 2, Fig. 5, §III-D, PDF pp. 2–4, 6]

## 5. ConDepNet — 실물 변형을 contact depth로 바꾸는 학습

### 5.1 입력·정답을 어떻게 짝짓는가

로봇이 real TacTip으로 target feature에 특정 상대 pose로 접촉하면 tactile image I를 저장한다. 시뮬레이션에서 **같은 상대 접촉 pose**를 재현하여 contact depth C를 얻는다. 이 I–C pair로 real-to-sim mapping을 학습한다. 시뮬레이션은 Tactile Gym의 rigid-body physics와 depth rendering을 이용한다. [원문 §III-B, Fig. 2(a), PDF pp. 2–3]

따라서 discriminator가 판별하는 ‘진짜 정답’은 이 경우 **실제 카메라처럼 생긴 영상이 아니라, 조건 I에 대응하는 시뮬레이션 contact depth C**다. 변환 방향은 실물 영상을 사실적인 실물 영상으로 재생성하는 것이 아니라 **실물 marker 영상 → 시뮬레이션형 접촉 표현**이다. [원문 식 (3)–(5), Fig. 2(a), PDF pp. 2–3]

### 5.2 Conditional GAN과 reconstruction 항

ConDepNet은 pix2pix GAN의 generator이며, 원문은 다음 min–max 목적을 제시한다.

원문 식 (3):

$$
G_C=G^{\ast}=\arg\min_G\max_D\mathcal{L}_C(G,D).
$$

원문 식 (4):

$$
\mathcal{L}_C(G,D)=\mathcal{L}_{\mathrm{cGAN}}(G,D)+\alpha\mathcal{L}_{L_1}(G).
$$

원문 식 (5), 두 번째 항의 닫는 괄호만 구문상 완결되도록 표시:

$$
\begin{aligned}
\mathcal{L}_{\mathrm{cGAN}}(G,D)
={}&\mathbb{E}_{I\in\Gamma,\,C\in\Phi}\left[\log D(I,C)\right]\\
&+\mathbb{E}_{I\in\Gamma}\left[\log\left(1-D(I,G(I))\right)\right].
\end{aligned}
$$

이때 I와 C는 임의로 서로 섞은 독립 표본이 아니라, 앞에서 정의한 paired dataset의 대응 관계를 따른다. Discriminator는 (I,C)와 (I,G(I))를 비교하고, generator는 조건 I에 맞는 contact depth를 생성하도록 학습된다. [원문 §III-B, 식 (3)–(5), PDF p. 3]

L1 항은 paired target과의 픽셀별 차이를 억제하는 reconstruction 항으로 읽는다. 아래 식은 **원문이 이름으로 정의한 Manhattan norm 항을 설명용으로 전개한 것**이며, 논문에 별도 식 번호로 제시된 학습 구현은 아니다.

$$
\mathcal{L}_{L_1}(G)=
\mathbb{E}_{(I,C)}\!\left[\lVert C-G(I)\rVert_1\right].
$$

실제 구현에서 픽셀·batch의 합/평균을 어떻게 취하는지, loss weight α를 얼마로 설정했는지는 본문에 없다. GAN 구조의 명칭은 pix2pix로 제공되지만 구체 layer 수와 channel 수도 이 원문에서 전개하지 않는다. [원문 §III-B, §IV-A.2, PDF pp. 3–4]

### 5.3 Generator에 random latent input을 넣지 않는 이유

저자들은 이 모델에는 원래 pix2pix 설명의 random vector 입력을 사용하지 않는다고 명시한다. real tactile image 하나마다 deterministic한 contact depth image가 필요하기 때문이다. **ConDepNet의 변환용 generator와 TacNGen의 확률적 noise decoder는 역할이 다르다.** [원문 §III-B, PDF p. 3]

### 5.4 실제 보고된 수집 범위

| 항목 | 원문 수치·조건 |
| --- | --- |
| Feature | flat edge를 가진 square stimulus |
| 데이터 수 | edge-feature tactile image 7,000개 수집을 보고. 실물·시뮬레이션에서 대응 접촉 수행 |
| 위치 y | −6–6 mm |
| 접촉 깊이 z | 3–6 mm |
| 회전 Rz | −180–180° |
| Train/validation 분할 | 이 본문에 수치 미명시 |
| Preprocessing | grayscale·[0, 1] 표현은 정의. 실제 crop·resize·threshold 등의 설정값은 미명시 |

7,000개를 이전 연구의 ‘학습 5,000 + 검증 2,000’으로 자동 분할하지 않는다. 원문 §IV-A.2는 총 수집량을 기술하지만 그 분할은 여기서 확정하지 않는다. [원문 §III-A, §IV-A.2, PDF pp. 2, 4]

## 6. TacSalNet — 목표 접촉만 남기는 학습

### 6.1 왜 depth map 뒤에 또 다른 network가 필요한가

ConDepNet이 잘 동작해도 C에는 target와 distractor 양쪽의 접촉 영역이 남는다. **접촉 위치를 가시화한 것과 목표 접촉을 선택한 것은 다르다.** TacSalNet은 바로 이 두 번째 문제를 풀며, 입력은 접촉이 혼합된 depth map, 출력은 목표 feature의 saliency map이다. [원문 §III-B–C, Fig. 2(a)–(b), PDF pp. 2–3]

### 6.2 오염된 입력과 깨끗한 label의 자동 생성

먼저 target-only depth map 집합과 noise depth map 집합을 분리해서 준비한다. 원문의 번호 없는 데이터 생성 관계를 정리하면 다음과 같다.

$$
C_{kl}=C_k^F+C_l^N.
$$

합성은 **pixel-by-pixel sum**이다. 학습 입력에는 두 접촉을 겹쳐 넣지만, 정답은 합성 전 target-only map으로부터 만든다.

$$
S_k^F=\mathrm{Norm}(C_k^F),\qquad
\mathcal{D}_{\Psi,F}=\left\{\left(C_{kl},S_k^F\right)\right\}.
$$

Min–max normalization을 통상적인 픽셀 표현으로 풀면 아래와 같다. 이는 원문의 ‘선형으로 [0,1]에 rescale’한다는 설명을 전개한 식이다.

$$
\left[\mathrm{Norm}(C^F)\right]_{ij}
=\frac{C^F_{ij}-\min_{a,b}C^F_{ab}}
{\max_{a,b}C^F_{ab}-\min_{a,b}C^F_{ab}}.
$$

원문은 상수 영상에서의 분모 0 처리, 합성 후 범위를 벗어나는 픽셀의 clipping, 실제로 모든 target–noise 조합을 생성했는지까지 기술하지 않는다. 집합의 수학적 정의를 실제 학습 데이터 개수로 바꾸지 않는다. [원문 §III-C, PDF p. 3]

**학습 신호의 핵심은 ‘어떤 접촉이 더 강한가’가 아니다.** Target-only map을 생성 과정에서 알고 있으므로, 같은 입력에 다른 contact가 추가되어도 출력은 기존 target를 가리켜야 한다. 이 대응 관계로 목표 접촉과 distractor의 분리를 학습한다. [원문 §III-C, Fig. 2(b), PDF pp. 2–3]

### 6.3 학습 목적과 discriminator의 역할

원문 식 (8):

$$
G_{S^F}=G^{\ast}=\arg\min_G\max_D\mathcal{L}_{S^F}(G,D).
$$

원문은 이 손실이 식 (4)–(5)와 같은 형태라고 설명한다. 여기서는 조건 입력을 C로, 정답을 S로 바꾸어 읽어야 한다. 아래는 그 **입출력 치환을 설명한 전개식**이다.

$$
\begin{aligned}
\mathcal{L}_{S^F}(G,D)
={}&\mathbb{E}_{(C,S^F)}[\log D(C,S^F)]\\
&+\mathbb{E}_{C}[\log(1-D(C,G(C)))]\\
&+\alpha\,\mathbb{E}_{(C,S^F)}[\lVert S^F-G(C)\rVert_1].
\end{aligned}
$$

Discriminator는 오염된 depth C에 대응하는 실제 학습 label S와 예측 G(C)를 구분한다. Reconstruction 항은 생성 결과가 합성 이전 target의 모양과 위치를 유지하도록 유도한다. 여기서 ‘실제 학습 label’은 **실물 사람이 그린 mask가 아니라 시뮬레이션 target-only depth를 정규화한 영상**이다. [원문 §III-C, 식 (8), Fig. 2(b), PDF pp. 2–3]

### 6.4 Feature type 선택과 object identity는 다르다

수식의 F는 edge나 surface 같은 feature type이다. 실제 학습·평가는 edge에 한정한다. 따라서 이 원문만으로 ‘임의의 물체 이름을 지시하면 그 물체의 접촉만 추출한다’거나 ‘같은 형태의 edge 둘 중 초기 지정 물체를 추적한다’는 기능을 주장할 수 없다. 실제 검증은 **학습한 target edge feature를 방해 자극에서 분리하는 것**이다. [원문 §III-A, §IV-A.2, PDF pp. 2, 4]

## 7. TacNGen — 학습용 접촉 잡음을 만드는 VAE

### 7.1 왜 noise 생성기를 따로 만드는가

시뮬레이터에 모든 종류의 방해 물체 CAD를 넣고 센서를 접촉시키는 방식은 비효율적이다. 또한 저자들은 그렇게 얻은 noise 패턴이 실물 ConDepNet 출력에서 보이는 패턴과 다를 수 있다고 설명한다. 이에 따라 다양한 noise contact depth를 생성할 모델을 도입한다. [원문 §III-D, PDF pp. 3–4]

여기서 **VAE 학습 자체는 실물 distractor 데이터가 아니라 시뮬레이션 cone 접촉 데이터**를 사용한다. 동기의 ‘실물 noise와의 차이’와, 실제 학습 데이터의 출처를 혼동하지 않는다. [원문 §IV-A.2, PDF p. 4]

### 7.2 Encoder·decoder와 손실

Encoder는 noise contact depth C로부터 K차원 latent Gaussian의 평균과 대각 covariance를 추정한다. 원문의 번호 없는 관계는 다음과 같다.

$$
f_\theta(C)=(\mu_{\theta,C},\Sigma_{\theta,C}),\qquad
\Sigma_{\theta,C}=\mathrm{diag}(\sigma_1^2,\ldots,\sigma_K^2).
$$

$$
z\sim\mathcal{N}(\mu_{\theta,C},\Sigma_{\theta,C}),\qquad
f_\lambda(z)=\widehat{C}.
$$

원문 식 (9):

$$
\mathcal{L}_{\mathrm{TN}}
=\mathbb{E}_{C\in\Phi^N}\!\left[
\alpha\,\mathrm{KL}\!\left[p_\theta(z\mid C)\,\Vert\,q(z)\right]
-\mathbb{E}_{p_\theta(z\mid C)}\log p_\lambda(C\mid z)
\right].
$$

$$
p_\theta(z\mid C)=\mathcal{N}(\mu_{\theta,C},\Sigma_{\theta,C}),\qquad
q(z)=\mathcal{N}(0,\mathbf{I}).
$$

KL 항은 추정 latent distribution이 prior와 지나치게 멀어지지 않게 하며, reconstruction log-probability 항은 원래 noise contact depth를 복원하도록 한다. α는 두 항의 상대 비중을 조절한다. 이것은 식 (9)의 역할 해설이며, reconstruction을 실제 코드에서 MSE 또는 BCE 중 무엇으로 구현했는지는 이 원문에 없다. GAN의 L1 가중치와 VAE의 KL 가중치에 같은 α 기호가 쓰이지만 두 값이 같다는 명시는 없다. [원문 §III-D, PDF p. 4]

### 7.3 학습 후 noise 생성

원문 식 (10):

$$
\tau(z)=f_{\lambda^{\ast}}(z)=\widehat{C}^{N},
\qquad z\sim\mathcal{N}(\mu,\Sigma).
$$

Encoder·decoder를 학습한 뒤, 학습된 decoder를 TacNGen으로 사용한다. Fig. 2(c)는 이를 고정하여 sampled latent vector에서 noise feature를 생성하는 흐름을 보여 준다. 생성 단계의 μ·Σ 실제 값과 K는 본문에 명시되지 않는다. Prior가 표준정규라는 사실만으로 식 (10)의 구현 설정까지 확정하지 않는다. [원문 §III-D, 식 (9)–(10), Fig. 2(c), PDF pp. 2, 4]

### 7.4 실제 학습·사용 절차의 명시 수준

| 항목 | 원문에 있는 설명 | 원문에 없는 세부사항 |
| --- | --- | --- |
| Training noise | simulated cone-shaped distractor의 contact depth | cone radius·각도의 실제 범위, 표본 수 |
| VAE 구조 | conventional VAE, convolutional layers | layer/channel, latent K, activation 등의 수치 |
| VAE 최적화 | 식 (9), θ·λ 동시 최적화 | optimizer·learning rate·batch·epoch·KL weight. 추가 정보는 보충 파일로 안내 |
| TacSalNet용 noise | TacNGen 생성 후 conventional augmentation | 증강 종류·범위·확률 |
| Epoch별 noise 생성 | 기존 생성 noise에 매 epoch 증강을 적용해도, 매 epoch 재생성하는 경우와 유사한 성능이었다고 보고 | 별도 정량 비교표·속도·학습시간 |
| Pix2pix 설정 | ConDepNet·TacSalNet 모두 [2]의 hyperparameter를 사용 | 현재 본문 안의 구체 수치 |

[원문 §IV-A.2, PDF p. 4]

## 8. 촉각 처리에서 실제 제어까지

### 8.1 세 학습 모델의 데이터 경계를 구분

| 모듈 | 학습 입력 | 정답/목적 | 실물 데이터 사용 |
| --- | --- | --- | --- |
| ConDepNet | real tactile image | 같은 접촉 pose의 simulated contact depth, cGAN+L1 | **사용** |
| TacNGen | simulated noise depth | VAE reconstruction+KL | 미사용 |
| TacSalNet | target-only depth에 noise를 합성한 입력 | 정규화된 target-only map, cGAN+L1 | 미사용 |
| PoseNet | 시뮬레이션에서 마련된 접촉 표현 | edge pose 추정. 상세 학습은 [7]과 각주 구현 참조 | 본문은 sim-to-real 버전을 사용한다고 명시 |
| Image-based DRL | simulated contact depth 기반 관측 | edge-following 정책. 상세 RL 설정은 [2] 참조 | 실물 fine-tuning 없이 사용 |

‘Real data를 쓰는 것은 ConDepNet뿐’이라는 주장은 논문의 제안 network 구성에 대한 설명이다. 전체 pipeline을 실물 데이터 없이 학습한 것으로 읽어서는 안 된다. 특히 실제 적용에는 학습된 ConDepNet이 반드시 앞단에 들어간다. [원문 §IV-A.2, §IV-C–D, Fig. 5, §V, PDF pp. 4–6]

### 8.2 PoseNet–PID 경로

Saliency map을 sim-to-real 버전의 tactile PoseNet에 입력하여 목표 edge의 위치 y와 방향 Rz를 예측한다. Fig. 5의 pose-based 경로는 이 추정 결과를 PID controller에 전달하고, 로봇에 target pose y·Rz를 보내는 구조다. Fig. 6의 붉은 화살표는 이 경로에서 TacTip의 방향 변화도 보여 준다. [원문 §IV-C–D, Fig. 5–6, PDF pp. 5–7]

정보–행동의 연결은 다음과 같다.

```text
동시 접촉으로 만들어진 marker 영상
 → 전체 접촉 depth
 → 목표 edge의 saliency
 → 목표 edge에 대한 y·Rz 추정
 → pose-based PID의 보정
 → 방해 물체가 아니라 목표 edge를 따라가는 접촉 운동
```

PID의 정확한 setpoint, gain, feedforward 항, 이동 증분·속도·제어 주기는 본문에 없다. 또한 본문의 ‘pose-based PID controller도 simulation에서 학습’이라는 요약 문장을 **PID gain을 RL로 학습했다는 뜻으로 확대하지 않는다.** 그림은 학습된 PoseNet과 PID를 구분하며, PID gain 학습 방법을 제시하지 않는다. [원문 §IV-D, Fig. 5, PDF p. 6]

### 8.3 Image-based DRL 경로

다른 경로에서는 PoseNet으로 명시적 pose를 복원하지 않고 saliency map을 image-based deep-RL policy에 제공한다. Fig. 5와 Fig. 6 caption에 따르면 이 정책은 **x·y 행동만 출력**한다. Pose-based 경로의 y·Rz와 동일한 행동 공간인 것으로 통일하면 안 된다. [원문 Fig. 5–6, PDF pp. 6–7]

기존 정책은 simulation의 contact depth를 입력으로 학습했고 실물 fine-tuning 없이 사용된다. TacSalNet을 붙이면 실물의 오염된 접촉 표현을 목표 feature 표현으로 바꾸어 공급한다. **이번 논문의 핵심은 distractor에 대응하는 새 RL reward가 아니라, 기존 정책에 들어가는 영상 표현을 바꿔 robustness를 높인다는 것**이다. [원문 §IV-D, §V, PDF p. 6]

### 8.4 실제로 기술된 RL 학습 방법과 공백

| 항목 | 현재 원문에서 확인되는 수준 |
| --- | --- |
| RL 역할 | edge-following 기반 제어기. TacSalNet 효과를 검증하는 두 control 방법 중 하나 |
| 입력 | contact-depth 기반으로 학습, 실행 시 saliency map을 공급하는 Fig. 5의 연결 |
| 행동 | x·y. 실제 증분 범위·단위·rate 미명시 |
| 학습 환경 | Tactile Gym을 이용하는 [2]의 sim-to-real tactile control 방법을 참조 |
| 알고리즘명 | 본문은 image-based deep-RL [2]로 기술. PPO·SAC 등의 구체 이름을 다시 명시하지 않음 |
| Reward function·가중치 | 현재 본문 미제시 |
| 전체 observation vector·history | 현재 본문 미제시 |
| Reset·termination·randomization | 재현 가능한 전체 설정 미제시 |
| Optimizer·학습률·batch·rollout·training steps·policy architecture | 현재 본문 미제시 |
| 실물 추가 학습 | fine-tuning 없이 적용한다고 명시 |

따라서 본 논문은 **ConDepNet·TacSalNet의 adversarial/reconstruction 손실과 TacNGen의 VAE 손실은 제공하지만, RL 정책의 학습 recipe는 제공하지 않는다.** 다른 Tactile Gym 논문에서 PPO를 사용했다는 이유만으로 이 노트에 PPO 설정을 대입하지 않는다. [원문 §III-B–D, §IV-D, PDF pp. 3–4, 6]

### 8.5 힘·접촉 정보 활용의 정확한 의미

이 연구에서 접촉이 행동으로 이어지는 중심 경로는 **힘 크기 → 힘 명령**이 아니라 **복합 접촉 변형 → 목표 접촉 표현 → pose/정책 → 운동**이다. Fig. 5는 saliency map을 후속 모델에 전달하는 흐름이며, raw marker image에 saliency를 곱하는 마스킹 연산을 제어 단계로 제시하지 않는다. Fig. 1·3–6의 overlay 영상은 표현을 시각적으로 보여 주는 자료와 구분해야 한다. [원문 §III, Fig. 1–6, PDF pp. 1–7]

또한 ‘noise를 제거한다’는 것은 방해 물체와의 물리적 접촉을 없애거나 안전성을 보장한다는 뜻이 아니다. 실제 성능 평가도 접촉력·손상·충돌 회피가 아니라 saliency 유사도, edge pose 오차, edge-following 궤적 오차다. [원문 §IV-B–D, Table I–II, PDF pp. 4–6]

## 9. 실험과 결과

### 9.1 실험 1 — TacNGen noise와 Gaussian noise 비교

비교군은 다음과 같다.

| 모델 | TacSalNet 학습에 사용한 noise |
| --- | --- |
| TacSalNet-1 | 제안 TacNGen의 생성 noise |
| TacSalNet-2 | 2차원 multivariate Gaussian distribution 기반 noise |

여기서 Gaussian noise를 ‘모든 픽셀에 독립적인 백색 잡음’이라고 바꾸어 설명하지 않는다. 원문은 2차원 Gaussian distribution과 그 시각적 패턴을 비교할 뿐, pixel-wise iid noise 구현을 명시하지 않는다. [원문 §IV-B, Fig. 3, PDF p. 4]

Fig. 3(a)의 실물 평가 reference 생성은 특히 중요하다. **동일한 target-edge 상대 pose에서 distractor가 있는 영상과 없는 영상을 얻는다.** 오염된 영상은 ConDepNet 뒤 두 TacSalNet에 넣고, distractor 없는 영상은 ConDepNet과 min–max normalization으로 target saliency reference를 만든다. 따라서 평가 reference 역시 그림상 ConDepNet을 거치며, 인간 annotation이나 직접 측정한 물리적 압력 정답은 아니다. [원문 Fig. 3(a), PDF p. 4]

원문 Table I — 실물 1,000 samples의 유사도 평가. 네 지표 모두 큰 값이 좋은 방향이다.

| 모델 | AUC-Judd | SIM | CC | NSS |
| --- | ---: | ---: | ---: | ---: |
| TacSalNet-1 | **0.995** | **0.984** | **0.957** | **4.629** |
| TacSalNet-2 | **0.995** | 0.972 | 0.936 | 4.288 |

TacNGen 기반은 AUC-Judd에서 동률이고 나머지 세 지표에서 더 높다. Fig. 3(b)의 마지막 세 행은 straight edge만으로 학습했어도 corner-edge를 처리한 예를 보여 준다. 저자들은 Gaussian 기반 모델은 noise를 남기는 경향이 있다고 설명하고, 이후 전체 framework 평가에는 TacSalNet-1만 사용한다. 이를 다른 모든 noise generator보다 우수하다는 결과로 확대하지 않는다. [원문 §IV-B, Fig. 3(b), Table I, PDF pp. 4–5]

### 9.2 실험 2 — distractor가 있는 정적 접촉의 pose 추정

목표는 edge pose의 y와 Rz를 예측하는 것이다. Distractor와 edge 사이 거리는 7–14 mm이고, 접촉 pose는 다음 범위에서 sample한다.

| 변수 | 평가 범위 |
| --- | --- |
| x | −10–10 mm |
| y | −3–3 mm |
| z | 3–6 mm |
| Rz | −45–45° |

이는 ConDepNet용 edge 데이터 수집 범위와 다르다. Training range와 정적 robustness evaluation range를 하나의 분포로 합치지 않는다. [원문 §IV-A.2, §IV-C, PDF pp. 4–5]

**아래 saliency 적용 결과에는 저자들이 distractor 때문에 생기는 prediction drift를 calibration했다고 명시한 조건이 포함된다.** Calibration의 절차·데이터·offset 계산법은 본문에 설명하지 않는다. 따라서 아래 수치를 ‘아무 보정 없이 saliency network만 추가했을 때의 효과’로 단정하지 않는다. [원문 §IV-C, PDF p. 5]

Fig. 4(c)–(d)의 개별 panel에 인쇄된 MAE를 전사하면 다음과 같다.

| 조건 | Saliency 미사용 y MAE | Saliency 미사용 Rz MAE | Saliency 사용 y MAE | Saliency 사용 Rz MAE |
| --- | ---: | ---: | ---: | ---: |
| No distractor | 0.21 mm | 3.18° | 0.22 mm | 3.20° |
| Bolt | 1.84 mm | 24.3° | 0.26 mm | 4.48° |
| Comb | 2.20 mm | 14.0° | 0.40 mm | 5.06° |
| Clip | 2.41 mm | 30.0° | 0.35 mm | 4.44° |

Distractor가 없을 때에는 거의 같은 성능을 유지하고, distractor가 있을 때에는 pose 오차가 크게 줄어든다. 다만 원문은 **y가 약 −2.5 mm인 구간에서는 saliency를 써도 추정 정확도가 나빠진다**고 보고한다. 저자들의 설명은 센서가 distractor에 너무 가까워져 TacSalNet이 이를 target 일부로 포함하기 때문이라는 것이다. [원문 §IV-C, Fig. 4, PDF p. 5]

Toy figure·spoon은 실험 대상에 포함되지만 개별 결과를 보충자료로 넘긴다. 위 표는 Fig. 4에서 확인한 네 조건만 기록한 것이며, 나머지 둘의 MAE를 만들어 넣지 않는다. [원문 §IV-C, PDF p. 5]

### 9.3 실험 3 — distractor 주변에서 edge-following

Square·foil·flower·volute의 고정 edge 주변에 bolt를 최소 4개 배치한다. Bolt와 edge의 간격은 7–12 mm다. 곡률이 바뀌는 edge에서 distraction의 영향을 보기 위해 본문 정량 비교는 bolt 한 종류를 사용한다. [원문 §IV-D, Fig. 6(a), PDF pp. 6–7]

원문 Table II — ground-truth 궤적에 대한 mean absolute error.

| 대상 | PID, saliency 미사용 | PID, saliency 사용 | DRL, saliency 미사용 | DRL, saliency 사용 |
| --- | --- | ---: | --- | ---: |
| Square | Fail | 0.77 mm | Fail | 1.04 mm |
| Foil | Fail | 0.53 mm | Fail | 0.94 mm |
| Flower | Fail | 0.76 mm | Fail | 1.03 mm |
| Volute | Fail | 0.91 mm | Fail | 1.21 mm |

Saliency가 없으면 두 control 방법 모두 bolt 접촉에 끌려가 목표 edge를 벗어나거나 distractor에서 멈춘다. Saliency가 있으면 목표의 전체 둘레를 완료한다. Fig. 6의 초록색은 target contour, 색상은 궤적 위치 오차, 파란 화살표는 시작 pose다. 보라색 cross는 TacTip이 distractor에 stuck된 위치를 표시하며 caption은 50 steps를 언급한다. 이 50을 전체 task의 공통 최대 episode 길이로 해석하지 않는다. [원문 §IV-D, Fig. 6 caption, PDF pp. 6–7]

저자들은 saliency 적용 두 방법의 결과를 **실물 80회 시험, 각 물체·방법 조합당 10회**로 보고한다. 4개 물체 × 2개 제어 경로 × 10회에 대응한다. 전체 이동 거리는 300–520 mm다. Saliency 미사용 baseline까지 각각 동일 횟수로 수행하여 총 160회였다고는 본문만으로 확정하지 않는다. [원문 §IV-D, PDF p. 6]

Table II에서는 PID의 궤적 오차가 DRL보다 작지만, 본 연구의 주된 비교는 **동일한 제어 방법에 saliency를 넣었을 때와 넣지 않았을 때의 distraction 대응**이다. 두 방법은 행동 공간도 다르므로 이 결과를 모든 tactile task에서 PID가 RL보다 우수하다는 일반 결론으로 확대하지 않는다. [원문 Fig. 5–6, Table II, PDF pp. 5–7]

### 9.4 세 실험이 각각 뒷받침하는 것

| 실험 | 관측한 결과 | 넘어가면 안 되는 해석 |
| --- | --- | --- |
| Noise generation ablation | TacNGen 기반 saliency가 Gaussian 기반보다 3개 지표에서 높고 1개 동률 | 모든 종류·모든 세기의 noise 제거 보장 |
| Static pose prediction | 보고된 보정 조건 아래 y·Rz 추정 오차 감소 | 센서의 힘 분해능 향상 또는 calibration 없는 효과 |
| Edge-following | 시험한 contour·bolt 배치에서 두 제어 경로의 완주와 낮은 궤적 오차 | 물체 이동/pushing 성능, 임의 clutter 조작 성공률 |

[원문 §IV-B–D, Table I–II, Fig. 3–6, PDF pp. 4–7]

## 10. Limitation — 저자들이 밝힌 한계와 검증 범위

이 논문에는 독립된 Limitation 절은 없다. 다음은 본문·Discussion에서 저자들이 명시한 범위와 관찰된 어려움을 구분한 것이다.

### 10.1 Distractor가 가까우면 목표 feature로 잘못 포함될 수 있다

정적 pose 평가에서 y≈−2.5 mm일 때 성능이 떨어지는 현상을 보고한다. 저자들은 가까운 distractor를 TacSalNet이 target의 일부로 예측하기 때문이라고 해석한다. 즉, 제안법이 여러 접촉의 분리를 항상 성공하는 것은 아니다. [원문 §IV-C 마지막 문단, PDF p. 5]

### 10.2 실제 target feature는 edge로 한정했다

방법의 수학적 정의는 edge·surface 등 일반 feature type을 사용하지만, 실험 분석을 간단히 하기 위해 **target를 edge로 제한**했다고 명시한다. Surface나 다양한 feature class를 동일하게 검증한 결과는 아니다. [원문 §III-A, §IV-A.2, PDF pp. 2, 4]

### 10.3 TacTip과 depth-based simulator에서 검증했다

Discussion은 본 방법을 marker-based TacTip으로 시험했으며 Tactile Gym의 depth-based tactile simulation에 의존한다고 밝힌다. DIGIT·DigiTac이 다른 연구에서 Tactile Gym에 통합되었다는 사실과, **이 saliency 방법을 그 센서에서 검증했다는 사실은 다르다.** [원문 §V, PDF p. 6]

### 10.4 Pose 평가에서 drift calibration이 필요했다

Distractor에 의해 생기는 피할 수 없는 prediction drift를 calibration했다고 저자들이 적는다. 이는 보고된 정확도를 해석할 때 필요한 실험 조건이다. 다만 독립적인 실패 분석이나 보정 ablation으로 전개하지 않았으므로, calibration의 원인·효과 크기·구현을 이 노트에서 추가로 확정하지 않는다. [원문 §IV-C, PDF p. 5]

## 11. Future Work — 저자들이 제시한 향후 방향

### 11.1 다른 종류의 촉각 센서에 적용

저자들은 DIGIT·DigiTac 등을 Tactile Gym에 통합한 이전 결과를 근거로, **다른 tactile sensor type에 saliency 접근법을 적용하는 후속 연구**를 제안한다. 현재 논문의 실제 비교 센서는 TacTip 하나다. [원문 §V, PDF p. 6]

### 11.2 다른 exploration·manipulation task로 확대

예상하지 못한 tactile distractor가 성능을 떨어뜨리는 다른 탐색·조작 과업에 활용할 수 있을 것으로 기대한다. 이는 앞으로의 적용 가능성이지, pushing·grasping 등 추가 과업을 이 논문에서 이미 구현했다는 의미가 아니다. [원문 §V 마지막 문단, PDF pp. 6–7]

### 11.3 Label normalization의 다른 선택지

방법 절에서는 개념 검증을 위해 min–max normalization을 사용했으며, standardization 같은 대안을 언급한다. 이를 확정된 개발 계획으로 부풀리지 않고 **원문에 언급된 대체 표현 가능성**으로 기록한다. 해당 대안의 성능 비교는 제시하지 않는다. [원문 §III-C, PDF p. 3]

## 12. 재현에 필요한 미명시 정보와 원문 주의사항

### 12.1 무엇을 읽어야 학습을 재현할 수 있는가

| 구분 | 이 본문에서 확보되는 것 | 추가 확인이 필요한 것 |
| --- | --- | --- |
| ConDepNet | 입출력·동일 pose pairing·7,000 image 수집·pose 범위·cGAN+L1 식 | [2]의 hyperparameter, 실제 preprocessing·split·network layer·optimizer |
| TacSalNet | target+noise 합성·target-only normalization·GAN 목적 | 실제 dataset 수·clipping·증강 종류·최종 설정·정규화 예외 처리 |
| TacNGen | cone-derived depth·convolutional VAE·KL/reconstruction 식·decoder 생성 | 보충 파일의 latent 크기·학습량·cone 범위·구현 loss·sampling 설정 |
| PoseNet | 출력 y·Rz, simulation 기반 버전 사용 | [7]·각주 코드의 학습 설정, distractor drift calibration 방법 |
| PID | PoseNet 뒤에 연결되는 제어 구조·Fig. 5의 target pose | gain·setpoint·trajectory generator·command scaling·rate |
| DRL | simulated depth input·saliency plug-in·x/y action·실물 fine-tuning 없음 | [2]의 algorithm·reward·reset·termination·observation·network·학습 설정 |
| Evaluation | Table I–II, Fig. 4 MAE, 1,000 samples 및 80 control tests | metric 구현·reference 정규화, 정적 pose 시험 표본 수, failure 반복 수, 원시 로그 |

이 목록은 재현 정보의 공개 위치를 구분한 것이며, 해당 정보가 세상 어디에도 없다는 뜻이 아니다. 원문이 보충 파일이나 [2]를 가리키는 항목은 그 자료를 확인해야 한다. 이번 정리에서는 그 내용을 검증하지 않았다. [원문 §III, §IV-A–D, PDF pp. 3–6]

### 12.2 수식·용어를 읽을 때 주의할 부분

**식 (5)의 괄호:** 출판본 두 번째 log 항에 닫는 괄호가 완결되지 않은 표기가 보인다. 위 정리에서는 log(1−D(I,G(I)))의 입출력 관계를 유지하고 괄호만 완결했다. 새로운 loss나 목적함수를 추가한 것은 아니다. [원문 식 (5), PDF p. 3]

**S의 확률 정의와 label:** S는 target에 속할 probability로 정의되지만 label은 target-only depth의 min–max 정규화다. Binary segmentation mask·사람 annotation·calibrated probability를 사용하는 것처럼 바꾸지 않는다. [원문 §III-A·C, PDF pp. 2–3]

**합성의 범위:** C의 원소를 [0,1]로 정의한 뒤 target map과 noise map을 더한다. 겹친 픽셀의 범위를 어떻게 처리하는지는 본문에서 명시하지 않는다. 이 공백을 자동 clipping이나 물리적으로 정확한 다중 접촉 시뮬레이션으로 채우지 않는다. [원문 §III-B–C, PDF p. 3]

**VAE 최적 파라미터 표기:** 식 (10) 뒤에서는 λ*를 θ·λ에 대한 argmin으로 표기한다. 문맥상 encoder·decoder를 함께 최적화한 뒤 decoder 파라미터를 사용하는 뜻으로 설명하되, 생성 latent의 μ·Σ 값을 발명하지 않는다. [원문 §III-D, PDF p. 4]

**Noise 모델의 motivation과 학습 source:** 실물 ConDepNet의 noise pattern과 단순 simulated distractor pattern의 차이를 동기로 제시하지만 TacNGen은 simulation-only로 학습한다. 실물 noise dataset으로 VAE를 학습했다고 바꾸지 않는다. [원문 §III-D, §IV-A.2, PDF pp. 3–4]

**Saliency overlay와 제어 입력:** Figure의 raw image와 map을 겹친 그림을, raw image×mask 연산이 실제 제어 입력이라고 해석하지 않는다. Fig. 5가 보이는 것은 map을 PoseNet 또는 정책으로 보내는 연결이다. [원문 Fig. 5, PDF p. 6]

**‘학습된 PID’ 표현:** 본문은 simulation에서 준비된 control 방법을 묶어 설명하지만, PID 파라미터 자체의 RL 학습을 기술하지 않는다. 학습된 perception model·학습된 정책·PID controller를 분리한다. [원문 §IV-D, Fig. 5, PDF p. 6]

**80회·50 steps:** 80회는 본문의 saliency 적용 성능 설명에 제시된 실물 시험 수다. Fig. 6 caption의 50 steps는 distractor에 stuck된 실패 묘사다. 이를 무조건 전체 실험 총수 또는 모든 episode의 timeout으로 사용하지 않는다. [원문 §IV-D, Fig. 6, PDF pp. 6–7]

### 12.3 형식·검증 범위

블록 수식은 두 개의 달러 기호를 각각 독립 줄에 두고, 인라인 수식은 한 쌍의 달러 기호로 표기한다. 원문 식 번호는 수식 밖에 두었다. 학습 손실을 설명용으로 전개한 식과 원문에 실제로 번호가 붙은 식을 구분했다. 원문 그림과 표를 확인했지만 원문 PDF·그림은 저장소에 복제하지 않는다.

수식 24개(블록 18개·인라인 6개)의 로컬 MathJax 구문 검사에서 오류가 없었고, 블록 수식 전체의 렌더링과 표 21개의 열 구조를 확인했다. 로컬 브라우저에서 본문 표시도 점검했다. 실제 GitHub 웹페이지의 최종 렌더링은 확인하지 않았다. 이 검증은 학습 코드 실행이나 실험 재현을 뜻하지 않는다.

## 13. 원문 위치 안내

| 확인할 질문 | 원문 위치 |
| --- | --- |
| Tactile saliency를 왜 도입했는가 | Abstract, §I, Fig. 1, PDF p. 1 |
| 기존 touch saliency와 무엇이 다른가 | §II, PDF p. 2 |
| I→C→S의 정의 | §III-A–C, 식 (1)–(2), (6)–(7), PDF pp. 2–3 |
| ConDepNet의 GAN loss와 대응 데이터 | §III-B, 식 (3)–(5), Fig. 2(a), PDF pp. 2–3 |
| TacSalNet의 label과 noise 합성 | §III-C, 식 (8), Fig. 2(b), PDF pp. 2–3 |
| TacNGen의 VAE loss·decoder | §III-D, 식 (9)–(10), Fig. 2(c), PDF pp. 2–4 |
| Hardware·7,000 images·pose range·hyperparameter 출처 | §IV-A, PDF p. 4 |
| TacNGen과 Gaussian noise ablation | §IV-B, Fig. 3, Table I, PDF pp. 4–5 |
| 정적 pose 평가와 drift calibration | §IV-C, Fig. 4, PDF p. 5 |
| Saliency가 PID와 DRL에 들어가는 방식 | §IV-D, Fig. 5, PDF p. 6 |
| Edge-following 오차·실패 그림 | Table II, Fig. 6, §IV-D, PDF pp. 5–7 |
| 가까운 distractor에서 실패하는 조건 | §IV-C 마지막 문단, PDF p. 5 |
| 다른 센서·과업에 대한 Future Work | §V, PDF pp. 6–7 |

## 14. 핵심 요약

이 논문은 **촉각 센서의 감도를 높이거나 새로운 미는 동작을 학습하기보다, 여러 접촉이 섞인 영상을 과업에 맞는 접촉 표현으로 바꾸는 문제**를 다룬다. ConDepNet은 실물 marker 영상을 contact depth로 옮기고, TacSalNet은 그중 target edge의 saliency를 예측한다. TacNGen은 simulation-only VAE로 학습에 필요한 noise를 생성한다. [원문 §III–IV, PDF pp. 3–6]

핵심 학습 감독은 **동일 pose의 real–sim pair**, **target-only map을 알고 있는 합성 데이터**, **noise reconstruction과 latent regularization**이다. 이 구조가 후속 PoseNet·PID·DRL의 입력을 바꾸며, 정적 edge pose 추정과 distractor가 있는 edge-following에서 개선을 보인다. [원문 Fig. 2·5, 식 (3)–(10), Table I–II, PDF pp. 2–6]

그러나 가까운 distractor의 target 혼입, drift calibration 조건, edge-only·TacTip-only 검증 범위는 남는다. GAN/VAE의 목적함수는 직접 제공하지만 상세 hyperparameter는 [2]·보충 파일에 의존하며, RL의 reward와 전체 학습 설정은 이 본문에 없다. [원문 §IV-A.2, §IV-C–D, §V, PDF pp. 4–7]
