# Tactile Active Inference Reinforcement Learning — 원문 상세 정리

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 조사 · IROS-S05](../reviews/2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md#iros-s05)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Tactile Active Inference Reinforcement Learning for Efficient Robotic Manipulation Skill Acquisition** |
| 저자 | Zihao Liu, Xing Liu, Yizhai Zhang, Zhengxiong Liu, Panfeng Huang |
| 출판 | 2024 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), Abu Dhabi, UAE, October 14–18, 2024, pp. 10884–10889 |
| DOI | [10.1109/IROS58592.2024.10802750](https://doi.org/10.1109/IROS58592.2024.10802750) |
| 문헌 관리 식별자 | [IROS 제목 선별 보고서](../reviews/2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md#iros-s05)의 **IROS-S05**. 기존 선정 논문이며 사용자 별도 발굴 목록의 새 항목이 아니다. |
| 정리일 | 2026-09-16 |
| 확인한 원문 | 첨부 출판본 PDF 6쪽 전체. 본문 §I–V, 식 (1)–(11), Fig. 1–7, References [1]–[22]. 번호가 부여된 표·알고리즘·부록은 없다. |
| 확인하지 않은 자료 | 저자 코드·설정·원시 데이터·보충자료, 인용된 선행논문의 개별 원문, 제조사 데이터시트. 다른 논문이나 일반적인 구현 관행으로 미기재 내용을 채우지 않았다. |
| 원문 PDF SHA-256 | `3fbd7187e4c38f2304ea421fe7979f896e82a815fee4f5cd11a811e3f4f7d8fc` |

이 문서는 해당 논문 자체의 문제 상황, Related Work, 환경·센서, 촉각 처리, 학습·계획 방법, 실험, 저자 명시 한계와 향후 연구를 정리한다. 별도 연구 주제에 대한 적용안은 포함하지 않는다. `[원문 §…, PDF p.…]`는 첨부 출판본의 위치이며, **PDF 1–6쪽은 인쇄 페이지 10884–10889**에 대응한다. `[18]` 같은 표기는 원문 참고문헌 번호다. 수식과 그림은 PDF의 실제 표시를 확인했으며, 원문 식의 해설과 원문이 제시하지 않은 구현 정보를 구분한다.

**핵심:** 광학 촉각 영상을 접촉 중심·깊이 합·optical-flow entropy로 축약하고, 이 특징을 로봇·물체 상태와 결합한다. 상태전이 모델 앙상블과 reward model로 후보 행동의 미래를 예측하고, **예상 보상과 state information gain을 함께 평가하는 CEM 계획**으로 다음 행동을 정한다. 시뮬레이션에서는 공·상자를 경사면 위로 밀고, 실물에서는 일정 속도로 하강하면서 너트를 돌릴 회전 증분을 학습한다. **뉴턴 단위 힘을 복원하거나 목표 힘을 추종하는 제어기, SAC에 촉각을 추가한 정책, 시뮬레이션 pushing 정책의 실물 이전으로 설명하면 안 된다.** [원문 §III–IV, Fig. 1·3–7, PDF pp. 2–6]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 상황·기여와 Related Work의 비교 구도 |
| 3–4 | 시뮬레이션/실물 플랫폼·센서 사양, 관측·행동·정보의 역할 |
| 5 | 촉각 정적·동적 특징의 계산과 힘·미끄러짐 해석 범위 |
| 6–7 | FEEF 식 (1)–(6), 상태전이·reward model, CEM 계획 |
| 8 | 과업별 reward 식 (11), 학습 환경과 실제 학습 정보 공개 수준 |
| 9–10 | Fig. 5–7의 결과·비교 조건, 촉각에서 행동까지의 과업별 연결 |
| 11–13 | 저자 명시 Limitation, Future Work, 미명시·수식 주의사항 |
| 14 | 원문 위치 안내와 문서 검증 범위 |

## 1. 제시하는 문제 상황과 기여

### 1.1 사전 프로그램과 일반 RL의 서로 다른 한계

저자들은 사전 프로그램 기반 조작의 문제를 두 가지로 설명한다. 비정형 실제 환경을 정형화된 형상·절차로 표현하기 어렵고, 개발자가 로봇이 마주칠 모든 상태를 예상하여 정책에 넣기도 어렵다는 것이다. 여기서 촉각은 pose만으로 부족한 국소 접촉 정보를 제공하고, RL은 탐색으로 다양한 상태에서의 행동을 학습하는 대안으로 제시된다. 그러나 기존 촉각의 정보 부족과 RL의 낮은 데이터 효율이 실제 적용을 어렵게 한다. [원문 §I, PDF p. 1]

시각 기반 촉각 센서는 젤의 접촉 변형을 영상으로 얻을 수 있지만, 고차원 영상을 그대로 미래 예측에 사용할지는 별도 문제다. 저자들은 **수작업 영상 특징으로 계산 부담을 줄이면서 접촉에 필요한 정보를 상태에 포함**시키려 한다. 동시에 model-based 방식의 데이터 재사용과 intrinsic curiosity를 결합하여, 희소 보상에서도 탐색과 목표 수행을 함께 개선하려 한다. [원문 §I·III-B, PDF pp. 1, 3–4]

### 1.2 무엇을 제안했고 무엇을 검증했는가

원문이 제시한 기여는 광학 촉각 정보를 RL에 통합하는 특징 설계, 조작 기술 획득에 Active Inference RL을 도입하는 것, 그리고 Tactile-AIRL을 시뮬레이션과 실물에서 검증하는 것이다. 검증은 **경사면 pushing의 학습 효율**과 **너트 회전 중 하강 방향 변형을 줄이는 실물 학습**으로 구성된다. [원문 §I, PDF p. 1]

AIRL이라는 개념 자체를 이 논문에서 처음 만든 것은 아니다. §II-B와 §III-A는 Tschantz et al.의 기존 AIRL/FEEF 연구 [18]을 기반으로 삼는다. 본 논문의 핵심 구성은 **그 학습·계획 구조에 조작용 촉각 특징을 결합하고, 서로 다른 두 과업에서 평가하는 것**이다. [원문 §II-B·III-A, PDF pp. 2–3]

### 1.3 과업의 실제 범위

시뮬레이션은 경사면 아래쪽의 공 또는 상자를 위쪽 목표 영역으로 미는 과업이다. 실물은 이미 그리퍼가 잡은 nylon nut를 나사에 따라 회전시키는 과업이다. 실물에서 목표는 미지의 나사 pitch에 대해 적절한 회전을 찾아, 고정된 하강 운동과의 불일치로 발생하는 접촉면 변형을 줄이는 것이다. 두 실험은 플랫폼·행동 공간·촉각 특징이 다르다. [원문 §IV-A–B, Fig. 3–4, PDF pp. 4–5]

## 2. Related Work — 원문이 설정한 비교 구도

이 절은 원문 §II의 두 하위 절과 §I의 동기를 정리한 것이다. 아래 선행연구의 원문을 각각 추가 정독했다는 의미는 아니다.

### 2.1 Vision-based Tactile Sensor

| 비교 축 | 원문이 언급한 연구와 역할 | 본 논문의 선택 |
| --- | --- | --- |
| 광학 촉각의 활용 | GelSight 계열의 국소 변형 관측과 절단 [5], 식기 조작 [6], 케이블 조작 [7] | 광학 접촉 정보를 조작 학습의 상태에 포함한다. |
| 접촉면 복원 | Poisson reconstruction [8], 접촉 기하·힘 평가 [7] | 깊이 영상에서 중심과 pixel sum을 계산한다. 구체적인 RGB→gradient 변환은 [20]을 참조한다. |
| 학습형 특징 | 복잡한 접촉의 특징 추출 [9], 물체 표면 복원 [10] | 본 연구에서는 이미지 재구성 기반 다단계 예측이 RL 성능을 저해했다는 관찰에 따라 handcrafted features를 선택한다. |
| Shear/slip 정보 | GelSight의 shear·slip 측정 연구 [21] | Lucas–Kanade optical flow의 축별 분포 entropy를 동적 특징으로 사용한다. |

저자들이 말하는 높은 해상도는 이 센서 유형의 동기다. **해당 실험 센서의 영상 해상도나 힘 분해능 수치를 본문이 제공한다는 뜻은 아니다.** [원문 §II-A·III-B, PDF pp. 1–4]

### 2.2 Reinforcement Learning and Active Inference

| 비교 축 | 원문의 설명 | 본 연구와의 관계 |
| --- | --- | --- |
| Model-based RL | 학습한 전이 모델로 미래를 예측하여 실제 표본을 효율적으로 이용한다. 오차 누적과 희소 보상의 어려움이 남는다. [4] | 상태전이 모델을 쓰되 정보 획득 목적을 함께 고려한다. |
| Sim-to-real·사전학습 | 시뮬레이션에서 대량 학습 후 이전 [11], 시뮬레이션을 사전학습으로 사용하는 half sim2real [12] | 본 실험은 pushing의 시뮬레이션 비교와 screwing의 직접 실물 학습이다. 이 선행연구 설명을 본 논문의 이전 절차로 옮기지 않는다. |
| 탐색 공간 축소 | VPG [13]는 사전 정의된 기술과 영상 위치 선택을 이용한다. | 효율 개선의 관련 접근이며, 본 논문은 CEM으로 연속 운동 증분의 시퀀스를 계획한다. |
| 데이터 활용·희소 보상 | RHER [14]는 계층적 구성과 HER을 이용한다. | 본 논문은 HER이나 해당 계층 구조를 채택했다고 하지 않는다. |
| Active inference | Free-energy principle [15]–[16], active-inference adaptive control [17] | 현재와 미래 free energy를 줄이는 행동 선택의 배경이다. |
| AIRL | [18]은 active inference를 RL의 모델링·보상 관점으로 해석한다. | 본 논문의 FEEF, 예상 정보 획득, CEM 기반 계획을 설명하는 직접적 기반이다. |

따라서 SAC는 제안 알고리즘의 내부 학습기가 아니라 **실험의 model-free RL 비교군**이다. 또한 이 논문의 `AIRL`은 Active Inference Reinforcement Learning의 약어이며, inverse reinforcement learning이나 모방학습을 가리키지 않는다. [원문 §II-B·III-A·IV-C, PDF pp. 2–3, 5]

## 3. 환경·로봇 플랫폼·센서 상세 사양

### 3.1 시뮬레이션과 실물 환경

| 항목 | 시뮬레이션 pushing | 실물 screwing | 근거 |
| --- | --- | --- | --- |
| 로봇 | 본문은 UR robot, Fig. 3 caption은 **UR5** | **KUKA iiwa7** | §IV-A, PDF p. 4 |
| 도구·센서 | 말단의 광학 촉각을 TACTO로 모사. Fig. 3에 GelSight 표시 | **BackYard gripper**, **GelSight mini** | §IV-A, Fig. 3–4, PDF p. 4 |
| 환경 | 경사면, 공 또는 상자, 위쪽 빨간 목표 영역 | 나사와 nylon nut, 접촉 상태에서 회전 | §IV-A, Fig. 3–4 |
| 시뮬레이터 | **PyBullet + TACTO** | 실물에서 표본 수집·학습 | §IV-A–C |
| 환경 인터페이스 | Gym wrapper로 관측·행동·reward 구성 | 같은 데이터 흐름 개념 적용 | §IV-B, PDF p. 5 |
| 학습 행동 | 전진·좌우·회전의 3개 운동 증분 | 회전 증분 1개. 하강은 고정 속도 | §IV-B |
| 촉각 특징 | 중심과 깊이 합만 사용 | Optical-flow entropy를 사용하며, reward는 하강 방향 entropy의 음수 | §IV-B |
| 검증 초점 | Dense/sparse reward의 학습 곡선 | 하강 방향 shear 대리 지표의 개선·빠른 학습 | §IV-C, Fig. 5–7 |

Fig. 3의 작은 tactile image와 Fig. 4의 marker image는 장면을 보는 외부 카메라 영상이 아니라 **센서 접촉 변형을 관측하는 내부 촉각 영상**이다. Fig. 4는 그리퍼·센서·나사와 너트의 배치를 보여 주지만, 장착 치수나 센서 채널 결합 명세를 제공하지는 않는다. [원문 Fig. 3–4, PDF p. 4]

### 3.2 원문 명시·미명시 사양

| 사양 항목 | 원문 확인 결과 | 해석 시 주의 |
| --- | --- | --- |
| 로봇 모델 | UR5(시뮬레이션), KUKA iiwa7(실물) | 모델명이 확인된 것이며 제조사 세부 사양을 별도 검증한 것은 아니다. |
| 물리 로봇의 총 관절 자유도·가반하중·reach·반복정밀도 | **정량 사양 미명시** | iiwa7의 이름에서 자유도나 가반하중을 추출해 적지 않는다. |
| 실험에서 허용한 운동 | 시뮬레이션은 전진·좌우·회전, 실물은 하강·회전 | 허용 운동과 실제 학습 action 차원은 다르다. 실물 하강은 정책 action이 아니다. |
| 그리퍼 | BackYard라는 명칭 | 상세 모델, stroke, 구동 방식, 파지력 설정·제어값 미명시 |
| 광학 촉각 모델 | GelSight mini(실물) | 시뮬레이션 센서와 실물 센서의 완전한 사양 일치를 주장하지 않는다. |
| 측정 원리 | 접촉에 따른 젤 변형을 RGB 영상으로 관측 | 정전용량/압력 taxel을 직접 읽는 구조가 아니다. |
| 영상 해상도·crop·처리 영상 크기 | **미명시** | 그림 크기에서 입력 해상도를 추정하지 않는다. |
| 감지 면적·marker 수·간격·공간 해상도 | **미명시** | Fig. 2의 점 개수를 제품 사양으로 사용하지 않는다. |
| 최대 힘·압력·토크 측정 범위 | **미명시** | 아래의 접촉 intensity와 flow entropy는 N 또는 N·m 단위 측정값이 아니다. |
| 힘 분해능·정확도·최소 검출 힘·감도 | **미명시** | 별도의 힘 정답 대비 calibration/정확도 결과도 제시하지 않는다. |
| 카메라 frame rate·센서 갱신률·제어 주파수·대역폭 | **미명시** | Episode 수나 CEM 반복을 Hz로 바꾸어 해석하지 않는다. |
| 실물 센서 수·양쪽 손가락 신호 결합 방식 | **입력 명세 미명시** | 사진의 장착 모습과 실제 모델 입력 채널 수를 구분한다. |
| 전용 F/T 센서 | 측정 장치·입력 경로로 **제시하지 않음** | 로봇에 있을 수 있는 내장 센싱을 본 논문이 사용했다고 추정하지 않는다. |
| 경사각·경사면 치수·물체 질량·마찰계수·나사 pitch | **정량값 미명시** | 미지의 pitch는 실물 과업의 동기이며 식별 결과를 보고한 것은 아니다. |
| Action 크기·회전 범위·하강 속도·안전 threshold | **정량값 미명시** | 고정 하강 속도라는 설명만 있다. |

이 논문은 센서 계측 성능보다 학습 효율을 평가한다. 따라서 장비명이 있고 촉각을 이용한다는 사실과, 센서 성능 명세가 충분히 공개되었다는 판단은 분리해야 한다. [원문 §III-B·IV-A–B, PDF pp. 3–5]

## 4. 관측·행동·보상의 역할 분리

### 4.1 전체 관측

원문은 로봇·물체 상태 벡터를 $o_p$, 촉각 특징을 $o_t$로 부르고, 둘의 concatenation을 $o$로 정의한다. 여기서 $o_t$의 아래첨자 t는 **tactile의 구분자**이고, $o_\tau$ 같은 표기의 아래첨자는 시간이다. 원문은 두 표기 방식을 함께 사용한다. [원문 §III-A, Fig. 1, PDF pp. 2–3]

| 정보 | 시뮬레이션에서의 내용 | 실물에서의 내용 |
| --- | --- | --- |
| $o_p$ | 로봇과 조작 물체의 위치·속도·자세·각속도 | 하강 높이와 회전각 |
| $o_t$ | 깊이 영상 중심 $\mu$와 pixel sum $\Sigma$ | 일반 특징 집합은 §III-B에 제시. 실물 reward에 $H(y)$를 쓰는 것은 명확하지만 실물 observation에 넣은 최종 세부 목록은 별도 열거하지 않음 |
| Action | 전진·좌우·회전의 incremental motion | 하강축 주위 회전의 incremental motion |
| 외부에서 고정하는 운동 | 별도 고정 전진 속도는 설명하지 않음 | EEF가 고정 속도로 하강 |
| Reward 계산 정보 | 물체의 목표 영역 진입 여부와 목표 중심까지의 거리 | 촉각 optical flow의 하강 방향 분포 entropy |

**시뮬레이션에서는 현재 물체의 상태가 observation에 포함된다.** 물체 pose를 모르는 tactile-only pushing으로 정리할 수 없다. 또한 실물에서는 로봇의 회전각이 관측되더라도 **너트 자체의 실제 회전각 정답은 얻기 어렵다**고 저자들이 설명한다. 이 둘은 같은 값으로 취급되지 않는다. [원문 §IV-B, PDF p. 5]

### 4.2 촉각이 기여하는 서로 다른 경로

첫 번째 경로는 **상태 표현**이다. 중심·intensity·변형 추세가 로봇 상태와 결합되어 전이 모델의 입력이자 예측 대상이 된다. 두 번째 경로는 **실물 보상**이다. 하강 방향 optical-flow entropy가 회전 행동의 좋고 나쁨을 평가한다. 세 번째인 **state information gain**은 촉각 센서가 직접 출력하는 값이 아니라, 상태전이 모델들의 미래 예측 분포에서 얻는 계획용 점수다. [원문 Fig. 1, 식 (6)–(11), PDF pp. 3–5]

이 세 역할을 모두 ‘촉각 값을 reward에 넣었다’ 또는 ‘촉각을 actor에 넣었다’로 축약하면 실제 구조가 사라진다. 제안 방법에서는 학습된 모델을 통한 **행동 시퀀스 평가·재계획**이 핵심이며, 단일 actor network의 입력→출력 설명으로 대체할 수 없다.

## 5. 힘·접촉 정보 처리 — 영상에서 저차원 특징까지

### 5.1 왜 handcrafted features를 선택하는가

저자들은 촉각 영상 재구성 loss를 이용한 다단계 예측이 RL을 저해했다는 실험 관찰을 설명하고, 원인을 영상 형식의 정보 한계로 추정한다. 그래서 촉각 영상을 그대로 미래 예측하지 않고 수작업 특징을 사용한다. 다만 해당 비교의 architecture, loss 설정, 성능 표나 별도 ablation 곡선은 본문에 없다. **특징 선택의 이유는 제시하지만 이미지 기반 방법 전반의 열등함을 정량 입증한 것은 아니다.** [원문 §III-B, PDF p. 3]

특징은 접촉 위치·intensity·shape와 관련된 정적 특징, sliding과 같은 운동 추세를 나타내는 동적 특징으로 나눈다. 다만 실제 정적 특징 계산은 **접촉 형상이 고정되어 있고 깊이 영상이 하나의 연결 영역인 단순한 경우**에 초점을 맞춘다. Shape라는 동기 표현을 별도의 shape encoder가 있다는 뜻으로 해석하지 않는다. [원문 §III-B, PDF pp. 3–4]

### 5.2 정적 특징: RGB → 접촉 깊이 → 중심·깊이 합

광학 촉각 RGB 영상에서 표면 gradient를 얻고 Poisson 적분을 이용하여 접촉 깊이를 복원한다. 원문은 이 단계에 [20]을 인용하지만, RGB→gradient calibration, 경계 조건, solver, 단위 변환은 전개하지 않는다. 시뮬레이션은 TACTO가 RGB와 depth를 제공한다. [원문 §III-B·IV-A, PDF pp. 3–4]

원문의 $m_{ij}$는 계산 대상 깊이 영상 영역의 raw moment다. 정적 특징의 정의는 다음과 같다.

**원문 식 (7) — 접촉 중심**

```math
\mu=\left(\frac{m_{10}}{m_{00}},\frac{m_{01}}{m_{00}}\right).
```

**원문 식 (8) — 접촉 intensity**

```math
\Sigma=m_{00}.
```

중심은 깊이 영상의 접촉 분포가 센서 영상의 어느 위치에 놓이는지 나타낸다. Pixel sum은 전체 깊이 값의 합으로, 저자들은 이를 contact intensity로 사용한다. 본문은 raw moment를 계산하는 이산 합을 별도 식으로 제시하지 않으므로, 위 두 식과 설명을 중심으로 해설한다. [원문 §III-B, PDF p. 4]

여기서 중요한 구분은 다음과 같다. **$\Sigma$는 covariance matrix가 아니며, N 단위 접촉력도 아니다.** 또한 $\mu$는 영상상의 접촉 중심이지 로봇 좌표계에서 복원한 물체 중심이나 전역 pose가 아니다. 원문은 이를 물리 좌표계나 실제 힘으로 변환하는 calibration을 제시하지 않는다. 접촉이 없어 $m_{00}=0$일 때의 처리, 여러 접촉 영역의 분리·병합 규칙도 미명시다. [원문 식 (7)–(8)의 정의와 §III-B]

### 5.3 동적 특징: Lucas–Kanade optical flow

접촉면에 shear/sliding 경향이 생기면 젤의 변형 패턴이 바뀐다. 저자들은 이를 영상 내 점들의 displacement field로 관측하고, **Lucas–Kanade optical flow**로 계산한다. Fig. 2는 정지 상태와 오른쪽으로 움직이려는 상태의 흐름 벡터를 비교한다. 이 그림은 현상 예시이며 알려진 힘을 가한 calibration 결과는 아니다. [원문 §III-B, Fig. 2, PDF p. 4]

**원문 식 (9) — 샘플 점의 optical-flow field**

```math
F=\begin{bmatrix}
\{P(x_1,y_1),P(x_2,y_2),\ldots,P(x_n,y_n)\}\\
\{Q(x_1,y_1),Q(x_2,y_2),\ldots,Q(x_n,y_n)\}
\end{bmatrix}.
```

$P$와 $Q$는 각 샘플 위치의 optical-flow 두 성분이다. 이 $F$는 **영상 변위 집합**이며 물리적 force vector가 아니다. 샘플 점 선정, tracking window, frame 간격, 기준 영상 갱신, outlier 제거 등의 세부 설정은 제시되지 않는다. [원문 식 (9), PDF p. 4]

### 5.4 축별 histogram → entropy

샘플 점들의 $P$ 값과 $Q$ 값을 각각 histogram으로 모아 이산 분포를 추정한다. 그 후 각 방향의 entropy를 계산한다.

**원문 식 (10) — 동적 접촉 특징**

```math
\begin{aligned}
H(x)&=-\sum p(P)\log p(P),\\
H(y)&=-\sum p(Q)\log p(Q).
\end{aligned}
```

원문 설명에서 entropy가 높다는 것은 flow 값의 분포가 더 퍼져 있다는 뜻이며, 이를 **더 큰 물체 운동 추세와 젤 변형, shear의 대리 지표**로 해석한다. 따라서 단일 접촉 bit보다 접촉면의 시간적 변화를 표현할 수 있다. [원문 §III-B, 식 (10), PDF p. 4]

다만 출력은 축마다 scalar entropy다. **미끄러짐의 signed velocity, 접선력 벡터, 마찰계수, 실제 slip 발생 여부를 직접 출력하는 estimator는 아니다.** 특히 $H(x)$·$H(y)$의 x·y는 flow를 나눈 축이지, entropy의 부호로 운동 방향을 표현한다는 뜻이 아니다. N 단위 전단력과의 대응식·측정 오차·slip threshold도 제시되지 않는다. Histogram bin 수·범위와 log의 밑이 없으므로 동일 수치의 재현에는 추가 정보가 필요하다. [원문 식 (9)–(10)의 해설; §III-B]

### 5.5 일반 특징 집합과 실제 사용 집합

원문이 일반적으로 제안한 tactile features는 $\mu$, $\Sigma$, $H(x)$, $H(y)$다. 중심이 두 성분이므로 **모두 사용하면 센서당 5개 scalar에 해당한다는 것은 식으로부터의 차원 해석**이다. 원문이 모든 실험의 최종 observation dimension을 5로 선언한 것은 아니다. [원문 §III-B, PDF p. 4]

시뮬레이션에서는 저자들이 사용한 환경에서 optical flow를 얻지 못했기 때문에 **$\mu$와 $\Sigma$만 사용**한다. 즉 정적 촉각 특징은 3개 scalar로 해석할 수 있지만, 로봇·물체 상태가 더해진 전체 observation 차원은 별도다. 이 설명을 TACTO 또는 모든 촉각 시뮬레이션이 원천적으로 optical flow를 만들 수 없다는 일반 주장으로 확대하지 않는다. [원문 §IV-B, PDF p. 5]

실물은 $H(y)$ 기반 reward를 명시한다. 그러나 최종 실물 $o_t$가 일반 특징 5개 전부인지, 그 일부인지, 여러 센서에서 어떻게 합치는지는 본문에 별도 명세가 없다. 사용이 확실한 동적 보상 경로와 미명시 observation 목록을 구분해야 한다.

### 5.6 이름이 비슷하지만 다른 두 entropy

| 구분 | Optical-flow entropy | State information gain의 entropy |
| --- | --- | --- |
| 출처 | 실제 촉각 영상의 점별 flow 값 분포 | 학습된 전이 모델들의 미래 상태 예측 분포 |
| 원문 | 식 (10) | 식 (6) |
| 의미 | 접촉면 변형·운동 추세의 대리 특징 | 행동을 통해 모델의 불확실성을 줄일 수 있는 정도를 평가하는 항 |
| 사용 | 촉각 특징, 실물의 $r_3=-H(y)$ | CEM 후보 행동의 탐색 가치 |
| 큰 값의 역할 | 실물에서는 줄이도록 reward 설계 | 예상 정보 획득은 키우도록 계획 |

따라서 **‘entropy를 줄이는 방법’과 ‘curiosity로 정보 획득을 키우는 방법’은 모순이 아니다.** 서로 다른 확률분포에서 계산한 서로 다른 값이다. [원문 식 (6), (10)–(11), PDF pp. 3–5]

## 6. Active Inference RL — FEEF에서 행동 점수까지

### 6.1 원문의 기호와 목적

원문은 **Free Energy of the Expected Future(FEEF)**를 사용한다. 실제 PDF의 기호는 $\widetilde{\mathcal F}$이며, 정책에 조건화한 값을 $\widetilde{\mathcal F}_\pi$로 쓴다. Reward도 부분 관측으로 취급한다. 여기서 free energy는 로봇의 기계적 에너지나 힘의 일을 뜻하는 것이 아니라, **확률모형 사이의 차이로 정의한 목적함수**다. [원문 §III-A, PDF p. 2]

| 기호 | 원문의 의미 |
| --- | --- |
| $x_{t:T}$ | 시간 t부터 T까지의 변수 시퀀스 |
| $o$ | 로봇·물체 상태와 tactile features의 결합 |
| $r$ | 환경 reward 또는 reward 시퀀스 |
| $\theta$ | 신경망 모델의 파라미터 |
| $\pi$, $q(\pi)$ | 정책, 정책에 대한 분포. 실제 실행은 CEM의 행동 시퀀스 계획으로 구현 |
| $q$ | 미래 변수에 대한 로봇의 belief |
| $p^\Phi$ | 로봇의 선호가 반영된 biased generative model |
| $D_{\mathrm{KL}}$ | KL divergence |
| $\mathcal H$ | 예측 확률분포의 entropy. 촉각 flow의 $H(x)$·$H(y)$와 구분 |

### 6.2 FEEF와 정책 분포 — 식 (1)–(3)

**원문 식 (1)**

```math
\widetilde{\mathcal F}
=D_{\mathrm{KL}}\!\left(
q(r_{0:T},o_{0:T},\theta,\pi)
\,\Vert\,
p^\Phi(r_{0:T},o_{0:T},\theta)
\right).
```

**원문 식 (2)**

```math
\widetilde{\mathcal F}=0
\;\Rightarrow\;
D_{\mathrm{KL}}\!\left(q(\pi)\,\Vert\,e^{-\widetilde{\mathcal F}_\pi}\right)=0.
```

**원문 식 (3)**

```math
\widetilde{\mathcal F}_\pi
=D_{\mathrm{KL}}\!\left(
q(r_{0:T},o_{0:T},\theta\mid\pi)
\,\Vert\,
p^\Phi(r_{0:T},o_{0:T},\theta)
\right).
```

저자들의 설명은 $q(\pi)$가 free energy가 작은 정책을 선호하도록 만들어, 미래의 free energy를 줄이는 계획 문제로 연결하는 것이다. 위 식은 **원문 표기를 보존한 것**이며, 원문에 없는 정규화 상수나 상세 유도를 추가하여 완결된 증명으로 제시하지 않는다. 식 (1)의 비교 분포에 등장하는 변수 범위와 식 (2)의 지수 표현은 §13에서 별도로 주의한다. [원문 §III-A, PDF p. 2]

### 6.3 정보 획득과 목표 수행의 분리 — 식 (4)

원문은 시퀀스 표기를 줄인 후, 음의 FEEF를 정보 획득 항과 extrinsic 항으로 나눈다.

**원문 식 (4)**

```math
\begin{aligned}
-\widetilde{\mathcal F}_\pi
&\approx
\mathbb E_{q(o,\theta\mid r,\pi)q(r\mid\pi)}
\left[\ln p(o,\theta\mid r,\pi)-\ln q(o,\theta\mid\pi)\right]\\
&\quad-
\mathbb E_{q(r\mid o,\theta,\pi)q(o,\theta\mid\pi)}
\left[\ln q(r\mid o,\theta,\pi)-\ln p^\Phi(r)\right]\\
&=
\mathbb E_{q(r\mid\pi)}
\left[D_{\mathrm{KL}}\!\left(q(o,\theta\mid r,\pi)\,\Vert\,q(o,\theta\mid\pi)\right)\right]\\
&\quad-
\mathbb E_{q(o,\theta\mid\pi)}
\left[D_{\mathrm{KL}}\!\left(q(r\mid o,\theta,\pi)\,\Vert\,p^\Phi(r)\right)\right].
\end{aligned}
```

첫 번째 KL 기대값은 원문에서 **expected information gain, c**로 표시한다. 미래 관측이 로봇의 이해를 얼마나 바꾸는지에 해당하는 탐색 동기다. 두 번째 KL 기대값은 **extrinsic term**이며, 미래 reward가 선호하는 분포에 가까워지도록 하는 목표 수행 동기다. 식에서는 두 번째 항 앞에 마이너스가 있으므로, 낮은 FEEF를 선택하는 것은 정보 획득을 크게 하고 선호와의 차이를 줄이는 방향이다. [원문 식 (4), PDF p. 2]

저자들은 RL 문맥에서 선호를 expected reward로 구현한다고 설명한다. 다만 $p^\Phi(r)$의 구체적인 분포, reward scale과의 대응, 두 항의 수치적 균형을 정하는 설정은 제공하지 않는다. 이 문서도 이를 임의의 curiosity weight로 보충하지 않는다.

### 6.4 미래 상태와 reward의 분포 예측 — 식 (5)

현재 관측에서 행동을 가정하고, 학습한 전이 모델로 미래 관측 시퀀스를 전개한다. 해당 미래 상태에 reward model을 적용하여 예상 reward도 구한다. [원문 §III-A.1, Fig. 1, PDF p. 3]

**원문 식 (5) — 줄바꿈용 연결 화살표를 제외한 표기**

```math
\begin{aligned}
q(o_{t:T},r_{t:T},\theta\mid\pi)
&=p(\theta)\prod_{\tau=t}^{T}
q(r_\tau\mid o_\tau,\theta,\pi)
q(o_\tau\mid o_{\tau-1},\theta,\pi),\\
q(r_\tau\mid o_\tau,\theta,\pi)
&=\mathbb E_{q(o_\tau\mid\theta,\pi)}
\left[p(r_\tau\mid o_\tau)\right],\\
q(o_\tau\mid o_{\tau-1},\theta,\pi)
&=\mathbb E_{q(o_{\tau-1}\mid\theta,\pi)}
\left[p(o_\tau\mid o_{\tau-1},\theta,\pi)\right].
\end{aligned}
```

Fig. 1은 **Model Ensemble(ME)**과 **Reward Model(RM)**을 학습 대상 신경망으로 표시한다. 실제 환경이 주는 reward와 계획 중 모델이 예측하는 reward를 구분하며, 모델 앙상블 블록에는 Gaussian fitting과 평균·분산 기호가 있다. 하지만 그림에 그려진 신경망 아이콘 개수를 ensemble size로 확정하거나, 그 그림만으로 개별 모델의 출력 분포·loss·학습 절차를 복원할 수는 없다.

원문은 미래 상태 분포를 필요로 한다는 원리를 제시하지만, particle 수, rollout에서 앙상블 구성원을 고르는 방식, 평균·분산 추정법, 모델별 학습 데이터 분할은 설명하지 않는다. [원문 §III-A.1, Fig. 1, PDF p. 3]

### 6.5 한 시점의 정보 획득 점수 — 식 (6)

**원문 식 (6)**

```math
\begin{aligned}
-\widetilde{\mathcal F}_{\pi\tau}
&\approx
-\mathbb E_{q(o_\tau,\theta\mid\pi)}
\left[D_{\mathrm{KL}}\!\left(
q(r_\tau\mid o_\tau,\theta,\pi)\,\Vert\,p^\Phi(r_\tau)
\right)\right]\\
&\quad+
\mathcal H\!\left[
\mathbb E_{q(\theta)}
\left[q(o_\tau\mid o_{\tau-1},\theta,\pi)\right]
\right]\\
&\quad-
\mathbb E_{q(\theta)}
\left[\mathcal H\!\left[q(o_\tau\mid o_{\tau-1},\pi,\theta)\right]\right].
\end{aligned}
```

뒤의 두 항은 원문이 **state information gain, c**로 묶은 부분이다. ‘앙상블의 예측을 합친 분포의 entropy’에서 ‘각 모델 예측 분포 entropy의 평균’을 뺀다. 이는 단순히 다음 상태의 분산이 크면 보상을 주는 설명보다 구체적이다. **모델들이 같은 불확실한 분포를 예측하는 경우와 서로 다른 예측을 하는 경우를 구분하는 형태**이기 때문이다. 이 문장은 식 (6)의 구조 해설이며, 본문이 별도의 모델 불확실성 검증 실험을 보고했다는 뜻은 아니다.

예상 reward가 거의 없는 탐색 초기에도, 다른 접촉·운동을 경험하여 모델을 개선할 것으로 예상되는 행동은 정보 획득 점수로 선택될 수 있다. 목표와 연결되는 상태를 발견한 후에는 reward 예측도 행동 선택에 기여한다. 이것이 저자들이 희소 보상 성능을 설명하는 핵심 논리다. 단, 원문은 curiosity를 제거한 동일 모델 기반 비교군을 별도로 제시하지 않으므로 성능 향상의 각 원인을 완전히 분리한 ablation으로 보지는 않는다. [원문 §III-A.2·IV-C.1, PDF pp. 3, 5]

## 7. CEM으로 다음 행동을 정하는 실제 구조

### 7.1 ‘Learning Policy’는 행동 시퀀스 분포의 반복 갱신이다

원문 §III-A.3은 특정 후보 행동 시퀀스의 점수를 계산할 수 있다는 조건에서 **sampling-based Cross-Entropy Method(CEM)**를 선택한다. 매 행동 실행 시 Gaussian 행동 시퀀스 분포를 초기화하고, 샘플의 미래 상태·free energy를 평가하며 분포 파라미터를 갱신한다. 분포가 안정되면 계획된 시퀀스의 **첫 번째 행동만 실제 실행**한다. [원문 §III-A.3, PDF p. 3]

따라서 원문의 policy라는 용어를 PPO/SAC처럼 한 번의 actor forward pass로 행동을 내는 구조로 바꾸지 않는다. 학습된 모델을 사용하지만, 현재 상태에서 어떤 운동을 할지는 후보 행동 시퀀스를 다시 평가하는 절차를 거친다.

### 7.2 실제 상호작용과 모델 내부 예측의 분리

아래는 Fig. 1과 §III-A를 읽기 쉽게 재구성한 흐름이며, 원문에 없는 실행 코드나 새 알고리즘이 아니다.

```text
현재 로봇·물체 관측과 촉각 특징을 결합
  → Gaussian 행동 시퀀스 분포에서 후보를 샘플링
  → 각 후보에 대해:
       상태전이 모델 앙상블로 미래 관측을 전개
       reward model로 미래 reward를 예측
       앙상블 예측 분포로 state information gain을 계산
       계획 horizon 동안의 점수를 합산
  → 평가 결과로 행동 시퀀스 분포를 갱신하고 다시 샘플링
  → 분포가 안정되면 선택한 시퀀스의 첫 행동 실행
  → 실제 환경에서 다음 관측·reward 획득
  → 상호작용 자료를 모델 학습에 사용하고 다음 행동 계획
```

Fig. 1의 계획 블록은 **예측된 curiosity와 reward의 합을 시간에 따라 더한 값**으로 action을 선택한다고 표시한다. 본문은 반복 목표를 음의 FEEF라고 설명하면서 수치 표현으로 지수값을 언급한다. 본문만으로 elite 선택 비율, importance weighting, 실제 점수 변환이 어느 단계에 적용되는지까지 확인할 수는 없다. [원문 Fig. 1, §III-A.3, PDF p. 3]

### 7.3 제공되지 않은 학습·계획 세부

CEM population, elite 수·비율, horizon의 실제 값, 반복 횟수, 분포 초기 평균·분산, action clipping, 종료 tolerance는 미명시다. 전이·reward model의 layer 구성, optimizer, learning rate, loss, batch size, bootstrap 방법, 업데이트 주기와 최초 random exploration량도 없다. 그림에서 모델 학습과 데이터 흐름을 확인할 수 있지만, **그림만으로 재현 가능한 training recipe를 확보한 것은 아니다.** [원문 §III-A 및 Fig. 1의 확인 범위]

## 8. 과업별 reward와 학습 환경 구성

### 8.1 시뮬레이션 dense/sparse reward

시뮬레이션에서 공 또는 상자가 목표 영역에 들어가면 indicator가 1이고, 그렇지 않으면 0이다. Dense reward는 여기에 물체와 목표 중심 사이의 거리의 음수를 더한다. [원문 §IV-B, PDF p. 5]

**원문 식 (11) — 세 과업 보상**

```math
\begin{aligned}
r_1&=\mathrm{sgn}(\mathrm{get\_target})
-\mathrm{dis}(\mathrm{object},\mathrm{target}),\\
r_2&=\mathrm{sgn}(\mathrm{get\_target}),\\
r_3&=-H(y).
\end{aligned}
```

원문의 `sgn(get_target)`은 여기서 **0/1 목표 진입 판정 함수**로 설명된다. 일반적인 수학 sign 함수의 음수 출력을 사용하는 것이 아니다. `dis`는 물체와 목표 영역 중심의 거리다. 거리의 단위·정규화, 영역 크기, step reward의 누적 방식, 목표 도달 즉시 episode를 종료하는지는 미명시다. 따라서 식의 간결함과 환경 구현의 완전성을 구분한다.

Dense reward에서는 목표에 아직 도달하지 않아도 거리 변화가 행동 평가에 영향을 준다. Sparse reward에서는 도달 전 외적 reward가 같을 수 있으므로 정보 획득 목적이 탐색에 도움을 준다는 것이 저자의 설명이다. **촉각 intensity에 대한 별도 penalty나 접촉 유지 reward는 식 (11)에 없다.** [원문 §IV-B–C, PDF p. 5]

### 8.2 실물 screwing의 reward는 실제 힘이 아닌 대리 지표다

실물은 EEF를 일정 속도로 내리면서 **회전 증분만 조절**한다. 나사 pitch를 알지 못하므로 하강에 적합한 회전을 탐색해야 하고, 적절하지 않은 회전은 젤과 너트 사이의 하강 방향 변형으로 드러난다. 하지만 너트의 실제 각도 정답을 얻기 어려워, 저자들은 하강 방향 optical-flow entropy를 음수 reward로 사용한다. [원문 §IV-A–B, PDF pp. 4–5]

따라서 학습의 연결은 **회전 증분 변경 → 접촉면 flow 변화 → $H(y)$ 변화 → reward 변화 → 이후 계획 개선**이다. 나사 pitch를 수치로 추정하거나, 정확한 너트 회전량을 추종하거나, 목표 전단력에 대한 오차를 최소화하는 controller가 아니다. 하강이 외부에서 고정되므로, 정책이 하강 속도와 회전 속도를 모두 자유롭게 최적화했다고 쓰면 안 된다.

원문은 이 결과를 shear force 감소로 설명한다. 다만 직접 계산·기록한 objective는 **음의 flow entropy**이며, 실제 전단력의 N 단위 측정이나 정답 회전각 대비 오차는 보고하지 않는다. [원문 §IV-B–C.2, Fig. 7, PDF pp. 5–6]

### 8.3 무엇이 공개되었고 무엇이 없는가

| 재현 항목 | 원문에 명시된 내용 | 미명시 내용 |
| --- | --- | --- |
| 학습 알고리즘 | AIRL, 전이 모델 앙상블, reward model, CEM | 구현체·버전·학습 코드 경로 |
| 시뮬레이션 | PyBullet, TACTO, Gym wrapper, UR5, 경사면 pushing | 버전, timestep, 물성·경사각·물체 크기, 초기 상태 분포 |
| Observation | 로봇·물체 상태와 tactile feature 결합 | 전체 벡터 차원, 좌표계·스케일링, 실제 센서별 결합 |
| Action | 시뮬레이션 3개 증분, 실물 회전 증분 | 단위·범위·실행 주기, 저수준 제어 및 IK |
| Reward | 식 (11)의 세 함수 | 거리 정규화, flow histogram 설정, reward-model 학습 loss |
| 반복 실험 | 제안 방법을 서로 다른 random seed로 3회 실행했다고 설명 | 모든 비교군의 동일 seed 반복 여부·seed 값 |
| 표시·평활화 | 시뮬레이션 10 episodes, 실물 5 episodes의 sliding window | 음영이 통계적으로 무엇을 나타내는지의 상세 정의 |
| 실물 학습 종료 | 최근 5 episodes reward가 비교적 안정될 때 종료 | 안정화의 정량 tolerance, 별도 성공 판정·시험 횟수 |
| 모델 학습 | 신경망 ME·RM을 상호작용에서 학습 | architecture·loss·optimizer·LR·batch·업데이트 횟수 |
| CEM | Gaussian sequence sampling·갱신·첫 action 실행 | 후보 수·elite 규칙·horizon 값·반복 제한·수치 설정 |
| Sim-to-real | 해당 학습 프레임워크를 별도 실물 screwing에 적용 | Pushing policy의 실물 이전, domain randomization·GAN 전이 절차는 제시하지 않음 |

**이 논문에는 reward와 관측·행동의 개념적 정의, AIRL 계획 목적의 수식이 있다. 반면 신경망과 CEM의 구체적 최적화 설정은 상당 부분 없다.** 따라서 ‘방법을 전혀 설명하지 않는다’와 ‘그대로 재현 가능한 학습 명세가 있다’ 중 어느 쪽으로도 과장하지 않는다. [원문 §III–IV 전체]

## 9. 실험 결과와 비교 조건

### 9.1 공통 평가 방식

시뮬레이션에서는 SAC와 비교하고, dense reward에서는 origin AIRL도 함께 표시한다. 제안 방법은 서로 다른 random seed로 3회 수행하여 평균과 분산을 그렸다고 설명한다. 곡선 변동을 줄이기 위해 시뮬레이션은 10 episodes, 실물은 5 episodes의 sliding window를 사용한다. **이 window는 결과의 reward 평활화이며 센서 신호 전처리나 정책 입력 history 길이가 아니다.** [원문 §IV-C, PDF p. 5]

실물은 표본 수집 비용 때문에 **제안 방법만 실행**했다. 실물 SAC·AIRL ablation이나 같은 예산에서의 다른 방법 비교는 없다. Episode 수 기반의 data efficiency와 wall-clock 계산 시간·모델 rollout 수는 별개이며, 후자의 수치는 제시하지 않는다.

### 9.2 Dense reward — Fig. 5

Fig. 5에는 공/상자 각각에 대해 Tactile-AIRL, origin AIRL, SAC의 여섯 곡선이 있다. 전체 그래프는 느리게 학습하는 SAC를 포함하고, 작은 inset은 약 200 episodes까지의 초기 학습 차이를 확대한다. [원문 Fig. 5, PDF p. 5]

저자들은 **Tactile-AIRL과 origin AIRL 모두 약 100 episodes에서 거의 최대 누적 reward에 도달하고, SAC는 약 1,000 episodes가 필요**했다고 설명한다. 이를 model-based 방식의 데이터 효율 개선으로 해석한다. 즉 **약 한 자릿수 규모의 학습량 차이를 촉각 추가만의 효과로 설명하면 안 된다.** AIRL 자체의 모델 기반 성격도 비교에 포함되어 있다. [원문 §IV-C.1]

촉각의 추가 효과에 대해서는, 촉각이 없으면 학습 곡선 분산이 커지고 평활화된 reward가 상대적으로 낮아진다고 설명한다. 접촉의 국소 정보가 $o_p$만으로 얻기 어렵기 때문이라는 해석이다. 다만 origin AIRL의 정확한 입력 벡터와 모든 공통 hyperparameter는 별도로 공개하지 않으므로, 제안 방법과의 차이를 코드 수준에서 검증했다고 쓰지는 않는다.

### 9.3 Sparse reward — Fig. 6

Fig. 6의 legend는 **Tactile-AIRL의 ball, Tactile-AIRL의 box, SAC** 세 항목이다. Tactile-AIRL의 두 곡선은 학습과 함께 상승하지만 SAC는 거의 0에 머문다. 제안 방법의 곡선에도 변동이 남아 있어, 희소 보상에서 항상 실패 없이 목표에 도달한다고 읽을 수는 없다. [원문 Fig. 6, PDF p. 6]

저자들은 SAC가 수천 episodes를 탐색해도 학습하지 못했다고 설명한다. **그러나 Fig. 6에 보이는 가로축은 약 0–300 episodes다.** 수천 episodes라는 수치는 본문 보고이고, 그 전체 구간을 이 그림이 직접 보여 주지는 않는다. Dense 실험과 달리 이 그림에는 별도의 origin AIRL 곡선이 없으며, SAC 선 하나가 공·상자 각각을 어떻게 대표하는지는 명시하지 않는다. [원문 §IV-C.1, PDF p. 5; Fig. 6, PDF p. 6]

세로축은 reward이며 성공률이 아니다. Sparse step reward가 0/1이라고 해서 그림의 30–40 수준 값을 30–40% 성공률로 바꾸지 않는다. 목표 도달 후 종료·보상 지속·episode 길이 설정이 없어 누적 값의 세부 구성도 확정할 수 없다.

### 9.4 실물 screwing — Fig. 7

Fig. 7은 제안 방법의 실물 학습 reward가 증가하고 후반부에 안정되는 한 곡선을 보여 준다. 원문은 **약 15 episodes에 수렴**했다고 보고하며, 최근 5 episodes의 reward가 비교적 안정될 때 학습을 종료했다고 설명한다. [원문 §IV-C.2, PDF pp. 5–6]

이 결과는 정해진 하강 운동에서 더 적절한 회전을 찾으며 하강 방향 optical-flow entropy를 줄였다는 증거다. **15번의 모든 나사 조립이 성공했다거나, 15 episodes로 임의 pitch의 나사에 일반화했다는 결과는 아니다.** 실물 비교군, 다중 pitch·물체·시작 조건 평가, 너트 각도 정답, 전단력 실측 감소량, 최종 체결 토크·완료율은 보고하지 않는다.

### 9.5 결과 수치의 수준을 구분한 요약

| 조건 | 원문이 보고한 결과 | 해석 범위 |
| --- | --- | --- |
| Dense pushing | Tactile-AIRL·AIRL 약 100 episodes, SAC 약 1,000 episodes | 거의 최대 누적 reward에 도달하는 상호작용량의 본문 보고. 성공률 표나 wall-clock speedup은 아님 |
| 촉각 추가 효과 | 촉각이 없을 때 더 큰 분산·상대적으로 낮은 평활 reward | Fig. 5와 저자 해석. 특징별 ablation은 없음 |
| Sparse pushing | Tactile-AIRL 학습, SAC 학습 실패 | Fig. 6은 약 300 episodes 구간, ‘수천 episodes’는 본문 보고 |
| 실물 screwing | 약 15 episodes에 reward 수렴 | 제안 방법만 시험. 직접 전단력 정확도·다양한 나사 성공률 검증은 아님 |

## 10. 촉각 특징이 실제 행동에 연결되는 방식

### 10.1 Pushing: 접촉 표현이 다음 상태 예측을 바꾼다

Pushing에서는 $\mu$와 $\Sigma$로 센서 표면에서의 접촉 중심·변형 intensity를 표현한다. 로봇과 물체 상태가 같거나 비슷하더라도 국소 접촉 정보가 추가되므로 모델이 다음 상태를 예측할 때 이용할 수 있다. 각 전진·횡이동·회전 후보를 모델로 전개하고, 예상 목표 reward와 정보 획득 점수가 높은 시퀀스를 선택하여 첫 운동을 실행한다. [원문 Fig. 1, §III-B·IV-B]

다만 논문은 **‘접촉 중심이 왼쪽으로 이동하면 회전을 얼마만큼 수정한다’와 같은 명시적 mapping이나 force-to-motion 제어식**을 제시하지 않는다. 그 연결은 학습한 전이·reward model과 CEM의 후보 평가에 들어 있다. 접촉을 직접 유지하는 PID나 force threshold 기반 mode switch로 바꾸어 설명해서는 안 된다.

### 10.2 Screwing: 접촉 변형이 행동 평가 기준을 제공한다

실물에서는 고정 하강과 잘 맞지 않는 회전이 접촉면 변형을 만든다. 영상 flow의 하강 방향 분포가 넓어지면 저자들이 정의한 $H(y)$가 증가하고 환경 reward가 낮아진다. 모델은 이런 상호작용 결과를 학습하여 후보 회전의 미래를 평가하고, CEM은 목표 수행과 정보 획득을 고려한 회전 증분을 선택한다. [원문 §III-A–B·IV-B]

이때 ‘좋은 회전’의 학습 신호를 너트의 정답 각도에서 만들지 않아도 된다는 점이 촉각의 중요한 역할이다. 그러나 이는 **광학 변형의 통계량으로 유용한 objective를 만든 것**이지, 그 통계량이 모든 접촉에서 정확한 전단력 측정이라는 보장은 아니다.

## 11. Limitation — 저자들이 직접 밝힌 제약

원문에 독립된 Limitation 절은 없다. 아래는 본문에서 저자들이 직접 인정하거나 실험 범위로 명시한 사항이다. 별도로 발견한 구현 누락·수식 주의사항은 §13으로 분리했다.

| 저자 명시 제약 | 내용 | 원문 위치 |
| --- | --- | --- |
| 단순한 정적 접촉 형상 | 고정된 접촉 형상, regular-shaped surface, 단일 연결 영역의 깊이 영상에 초점을 맞춘다. | §III-B, PDF pp. 3–4 |
| 영상 재구성 기반 예측의 어려움 | 촉각 이미지 reconstruction loss를 이용한 다단계 예측이 RL을 저해했다는 관찰을 설명하며 원인을 추정한다. | §III-B, PDF p. 3 |
| 시뮬레이션 동적 촉각 특징 부재 | 사용한 환경에서 optical flow를 얻지 못하여 $\mu$·$\Sigma$만 사용했다. | §IV-B, PDF p. 5 |
| 실제 너트 회전각 정답 획득의 어려움 | 정확한 너트 각도를 얻기 어려워 optical-flow entropy를 reward의 대리 지표로 사용한다. | §IV-B, PDF p. 5 |
| 실물 비교 실험의 비용 | Sampling cost 때문에 실물에서는 제안 방법만 구현했다. | §IV-C, PDF p. 5 |
| 실물 제어 공간의 제한 | 하강·회전만 허용하고 하강 속도는 고정했다. 학습 action은 회전 증분이다. | §IV-B, PDF p. 5 |

‘많은 과업에 충분하다’는 특징의 일반성 주장과 실제 검증 범위는 구분한다. 실험은 공·상자 pushing과 하나의 screwing 구성에 관한 것이며, 저자들이 주장한 모든 조작으로의 확장성이 각기 실험된 것은 아니다. [원문 §III-B·IV–V]

## 12. Future Work — 원문 확인 결과

**원문에 구체적으로 명시된 Future Work 계획 없음.** §V는 tactile features와 AIRL의 탐색·활용 및 학습 효율을 정리하는 Conclusion이다. §IV-C.2에서는 더 넓은 실제 적용 가능성을 언급하지만, 특정 센서·과업·알고리즘 변경을 후속 연구 계획으로 제시하지는 않는다. [원문 §IV-C.2·V, PDF p. 6]

따라서 여러 접촉 영역 처리, 실물 비교군 확장, 힘 calibration, 빠진 optical flow의 시뮬레이션 구현 등을 저자의 Future Work라고 임의로 추가하지 않는다. 이러한 사항의 미검증 여부는 아래 확인 범위에 기록한다.

## 13. 미명시 사항·원문 수식과 해석의 주의점

### 13.1 FEEF 수식의 생략·표기

이 논문은 [18]을 인용하여 FEEF를 설명하지만 모든 유도를 전개하지 않는다. 다음은 **정리자가 원문 표기에서 확인한 주의점**이며, 저자의 Limitation으로 바꾸어 서술하지 않는다.

| 위치 | 원문 상태 | 이 문서의 처리 |
| --- | --- | --- |
| 식 (1) | q의 인자에 policy가 있지만 비교하는 biased generative model의 인자에는 policy가 표시되지 않는다. | 정책 차원의 기준 측도·확장된 분포 정의를 임의로 추가하지 않는다. |
| 식 (2) | 지수값을 policy distribution과 KL 비교하는 형태로 쓰지만 정규화 상수를 표시하지 않는다. | 원문 식을 보존하고, 이 식만으로 완전한 확률밀도 정의·증명이 주어졌다고 하지 않는다. |
| 식 (4) 직전 | 시퀀스를 r와 s로 줄인다고 쓰지만 실제 식은 o를 사용한다. | 계산식의 o를 유지한다. |
| 식 (4) | 첫 전개에는 `ln p`, 다음 KL 표현에는 q가 등장하며 변환 과정이 생략된다. Extrinsic KL에는 r라는 표식도 사용한다. | 원문 그대로 기록하되 환경 reward scalar와 KL 비용을 완전히 동일한 것으로 놓지 않는다. |
| 식 (5) | 조건부 분포와 그 변수에 대한 expectation이 함께 나타나는 압축된 표기다. | 미래 모델 rollout의 의도로 해설하며 상세 적분·수치 구현을 복원했다고 하지 않는다. |
| 식 (6), Fig. 1, §III-A.3 | 식은 extrinsic KL와 정보 획득, 그림은 예측 c+r의 합, 본문은 음의 FEEF와 지수 표현을 사용한다. | 공통된 계획 방향은 설명하되 실제 점수 scaling·정규화·CEM 가중치 구현은 미확인으로 남긴다. |

식 (5)에 인쇄된 꺾인 연결 화살표는 긴 식의 줄바꿈 표시로 처리하여 Markdown 식에서 제외했다. 의미를 바꾸는 연산을 추가한 것이 아니다. 원문의 식 번호는 모두 수식 블록 밖에 표시했다.

### 13.2 힘·슬립·확률적 불확실성을 혼동하지 않는 기준

$\Sigma$는 깊이 합, $F$는 optical flow, $H(y)$는 flow histogram entropy다. **이름이나 저자의 해석만으로 물리 단위가 있는 힘·압력·전단력으로 변환하지 않는다.** 식 (6)의 정보 획득 역시 sensor entropy가 아니라 모델 예측의 불확실성에 관한 값이다. [원문 §III]

실물에서 너트와 그리퍼 사이의 변형을 줄였다는 설명과, 실제 나사 pitch·체결 토크·slip 없는 완전 조립을 정량 검증했다는 주장은 다르다. 본문이 제시한 것은 reward curve 중심의 결과다. 모델의 높은 curiosity가 항상 안전한 접촉으로 이어진다는 안전 보장이나 강제 힘 제한도 본문에 제시되지 않는다. [원문 §IV]

### 13.3 학습량과 비교의 범위

약 100·1,000·15 episodes는 원문의 보고 수치다. 그러나 episode당 step 수·실물 수행 시간·planning 계산량이 없어 총 환경 step 수나 시간 절약률을 계산할 수 없다. 또한 sparse 실험에 curiosity 제거 비교군, 실물에 다른 알고리즘 비교군, 특징별 제거 실험이 없어 **촉각·모델 기반 예측·정보 획득의 효과를 모두 독립적으로 정량 분해한 결과는 아니다.** [원문 §IV-C, Fig. 5–7]

### 13.4 원문만으로 재현하기 어려운 세부사항

접촉 깊이 복원 calibration과 무접촉 예외 처리, optical-flow 추적·histogram 설정, 모델 network·loss·학습 설정, CEM 상세 설정, action 실행 주기·제어기, reset·termination, 센서 성능 사양, raw learning curve와 통계 설정이 충분히 명시되지 않는다. 이 사실은 제시된 방법의 개념과 실제 실험 결과가 없다는 뜻이 아니라, **제공된 6쪽만으로 동일 구현·수치를 재현할 수 있는 범위에 한계가 있다는 뜻**이다.

## 14. 원문 위치 안내와 문서 검증 범위

### 14.1 원문 위치

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 연구 문제·기여 | §I, PDF p. 1 |
| 광학 촉각 관련 연구 | §II-A, PDF pp. 1–2 |
| RL·active inference 관련 연구, 원전 [18] | §II-B 및 References, PDF pp. 2, 6 |
| FEEF 정의·정책 분포·탐색/활용 분리 | §III-A, 식 (1)–(4), PDF p. 2 |
| 전체 ME·RM·CEM 데이터 흐름 | Fig. 1, PDF p. 3 |
| 미래 상태·reward 평가, 정보 획득 | §III-A.1–2, 식 (5)–(6), PDF p. 3 |
| Gaussian 행동 시퀀스·CEM·첫 action 실행 | §III-A.3, PDF p. 3 |
| 특징 선택 동기·Poisson 접촉 깊이 | §III-B, PDF pp. 3–4 |
| 접촉 중심·intensity | 식 (7)–(8), PDF p. 4 |
| Optical flow와 축별 entropy | Fig. 2, 식 (9)–(10), PDF p. 4 |
| UR5 pushing·KUKA iiwa7 screwing 장비 | §IV-A, Fig. 3–4, PDF p. 4 |
| 관측·행동 차이, 세 reward | §IV-B, 식 (11), PDF p. 5 |
| 비교군·seed·reward window·dense 결과 | §IV-C, Fig. 5, PDF p. 5 |
| Sparse 결과·실물 학습·결론 | §IV-C.1–2·V, Fig. 6–7, PDF pp. 5–6 |

### 14.2 문서 검증

첨부 출판본 6쪽을 텍스트와 렌더링으로 확인하고, 식 (1)–(11) 및 Fig. 1–7을 대조했다. 수식 67개(블록 11개·인라인 56개)의 로컬 MathJax 구문 검사에서 오류가 없었으며, 블록 수식 전체와 주요 본문의 로컬 브라우저 렌더링, 표 14개의 열 구조를 확인했다. 실제 GitHub 웹페이지 자체의 최종 렌더링은 확인하지 않았다.

코드 실행·모델 재학습·실물 재현은 수행하지 않았다. 원문 PDF와 페이지 이미지는 저장소에 복제하지 않으며, DOI·원문 위치·파일 해시로 출처를 관리한다. 로컬 수식 검사와 GitHub 웹페이지 자체의 최종 렌더링 확인은 별개의 검증 범위다.
