# Bi-Touch — 원문 상세 정리

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Bi-Touch: Bimanual Tactile Manipulation With Sim-to-Real Deep Reinforcement Learning** |
| 저자 | Yijiong Lin, Alex Church, Max Yang, Haoran Li, John Lloyd, Dandan Zhang, Nathan F. Lepora |
| 출판 | IEEE Robotics and Automation Letters, 8(9), 5472–5479, September 2023 |
| DOI | [10.1109/LRA.2023.3295991](https://doi.org/10.1109/LRA.2023.3295991) |
| 기존 조사본 식별자 | [2026-09-14 문헌조사](../reviews/2026-09-14_blind-sweep-force-torque-tactile.md)의 **R6** |
| 정리일 | 2026-09-16 |
| 확인한 원문 | 제공된 출판본 PDF 8쪽 전체. 본문 §I–V, 식 (1)–(4), Fig. 1–7, Table I–III, References [1]–[28] |
| 확인하지 않은 자료 | 인용된 선행논문의 개별 원문, 저자 코드·설정·체크포인트·데이터, 보충 영상, 제조사 데이터시트 |
| 원문 PDF SHA-256 | `fb86020254380573343786b260ca7dd8849ef0ad1fde7a2c306aef4bff0be953` |

[개별 논문 색인](README.md) · [문헌조사 자료](../README.md)

이 문서는 논문 자체의 문제 상황, 관련 연구, 장비·센서, 촉각 처리, 학습·제어 방법, 실험, 저자들이 밝힌 Limitation과 Future Work를 정리한다. 다른 연구 주제에 대한 적용안은 포함하지 않는다. `[원문 §…, PDF p.…]`는 첨부 출판본의 위치이며, **PDF 1–8쪽은 인쇄 페이지 5472–5479**에 대응한다. `[7]` 등은 원문의 참고문헌 번호다. 그림·표·수식은 PDF의 실제 표시와 대조했다. 설명을 위해 재구성한 흐름과 원문에 명시되지 않은 세부사항을 구분한다.

**핵심:** 두 TacTip의 접촉 변형 영상을 real-to-sim GAN으로 각각 변환한 뒤, 두 영상과 고유감각·목표 정보를 함께 받는 PPO 정책으로 양팔을 조작한다. 단순히 촉각을 입력하는 것에 더해, **물체의 목표 달성·접촉면 정렬·접촉 위치 유지를 reward로 구성**하고, 회전 과업의 과도한 압착을 줄이도록 **시뮬레이션 센서 동역학과 학습 조건을 수정**하며, 모으기 과업에는 **GUM과 물체 중심→TCP 기준 curriculum**을 도입한다. 별도 손목 F/T의 wrench나 뉴턴 단위의 추정 접촉력을 사용하는 제어기는 제시하지 않는다. [원문 §III–V, PDF pp. 2–8]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 상황·기여와 Related Work |
| 3–4 | 로봇·센서 상세 사양, 관측·정답의 구분, GAN과 sim-to-real |
| 5 | PPO 학습과 세 과업의 행동 공간·공통 기호 |
| 6 | Bi-pushing의 reward와 학습 환경 |
| 7 | Bi-reorienting의 reward, 과도한 압착, 학습 수정 |
| 8 | Bi-gathering의 reward, GUM, curriculum, 외란 |
| 9 | 힘·접촉 정보가 실제 운동으로 연결되는 방식 |
| 10 | 실험 조건, 표의 수치, 일반화와 실패 사례 |
| 11–12 | 저자들이 밝힌 Limitation과 Future Work |
| 13–15 | 미명시 사항·표기 주의, 원문 위치, 핵심 요약 |

## 1. 제시하는 문제 상황

### 1.1 양팔 촉각 조작의 필요성과 어려움

저자들은 크거나 다루기 어렵고 서로 결합된 물체를 조작할 때 양팔이 단일 팔보다 높은 기동성과 유연성, 넓은 작업 영역을 제공할 수 있다고 설명한다. 그러나 양팔은 상태·행동 공간이 커지고 시스템 통합과 제어기 설계가 복잡하며, 기존 장비의 높은 비용도 연구 접근성을 제한한다. 시각만으로는 가림과 국소 접촉 상태의 관측 한계가 있으므로, 접촉 변형을 직접 반영하는 촉각을 활용할 필요가 있다는 것이 출발점이다. [원문 §I, PDF p. 1]

실물에서 처음부터 RL을 학습하는 데에는 초기 정책의 팔 간 충돌 위험, 빈번한 수동 reset, 대량 접촉 실험에 따른 센서 손상 위험이 있다. 이에 저자들은 저가 양팔 플랫폼과 시뮬레이션 학습·실물 이전을 결합한다. 이러한 위험을 연구 동기로 제시한 것이지, 본문에서 별도의 충돌 방지 알고리즘이나 자동 실물 reset 시스템까지 개발한 것은 아니다. [원문 §I, PDF p. 1]

### 1.2 세 과업은 서로 다른 문제를 검증한다

| 과업 | 조작 대상과 목표 | 주된 어려움 |
| --- | --- | --- |
| **Bi-pushing** | 두 팔이 큰 물체 하나를 경로상의 위치·방향 목표들로 이동 | 두 접촉을 협조시켜 목표 경로와 접촉 정렬을 유지 |
| **Bi-reorienting** | 물체 중심의 이동을 억제하면서 지정된 각도로 회전 | 양쪽 접촉 유지와 과도한 압착 방지, 긴 물체의 협조 조작 |
| **Bi-gathering** | 각 팔이 별도 물체를 밀어 두 물체를 서로 모음 | 서로 움직이는 목표, 외란, 실물에서 알 수 없는 물체 중심 |

[원문 §III-C, Fig. 2, PDF pp. 3–4]

논문은 과업별 정책을 학습한다. 세 과업을 선택·전환하는 하나의 범용 정책이나 고수준 task planner를 제시하지 않는다. 회전에서는 방향별로 다른 정책을 학습했다고 명시한다. [원문 §IV-A, §IV-B-2, PDF pp. 5–6]

### 1.3 저자들이 내세운 기여

기여는 **Tactile Gym 2.0을 양팔 플랫폼과 세 접촉 과업으로 확장**, **과업별 reward 및 sim-to-real 개선·GUM 설계**, **미지 물체와 외란에서의 실물 검증**이다. Introduction에서 힘 조절의 중요성을 강조하지만, 실제 방법의 표현은 힘 단위가 아니라 촉각 영상, 접촉 기하, 위치·각도 행동이다. [원문 §I, §III, PDF pp. 1–4]

## 2. Related Work — 원문이 구성한 비교 구도

원문 §II는 **양팔 로봇과 deep RL**, **양팔 로봇과 tactile sensing**의 두 부분이다. 아래는 해당 논문의 선행연구 설명을 정리한 것으로, 인용 논문 자체를 새로 정독해 검증한 결과가 아니다.

### 2.1 Bimanual robot system with deep RL

| 원문 인용 | 저자들이 설명하는 기존 접근 | 이 논문이 구분하는 점 |
| --- | --- | --- |
| Kataoka 등 [13] | 시뮬레이션에서 학습해 실물 양팔로 자석 연결 | Marker 기반 시각 추적에 의존하고 미지 물체 일반화는 제시하지 않았다고 설명 |
| Grannen 등 [14] | 음식 획득을 위한 양팔 scooping 정책과 미지 음식 일반화 | 양팔 RL의 가능성을 보여 주는 사례 |
| Fan 등 [15], SURREAL | 분산 RL과 양팔 조작 benchmark | 아래 두 benchmark와 함께 촉각을 고려하지 않은 것으로 소개 |
| Zhu 등 [16], robosuite | MuJoCo 기반 단일·양팔 조작 환경 | 국소 접촉을 상세히 관측해야 하는 과업에 촉각 부재가 제약 |
| Chen 등 [17] | 양손 dexterous manipulation benchmark와 RL 비교 | 고차원 조작 학습 기반과 촉각 기반 실물 조작을 구분 |

[원문 §II-A, PDF p. 2]

저자들의 문제의식은 기존 양팔 RL이 전혀 없다는 것이 아니라, **고해상도 촉각을 활용하는 양팔 실물 조작을 위한 접근 가능한 통합 환경이 부족하다**는 것이다. [원문 §I–II, PDF pp. 1–2]

### 2.2 Bimanual robot system with tactile sensing

Sommer 등 [18]은 Gaussian Process 기반 필터와 Gaussian mixture model을 사용한 탐색·파지 자세 선택 사례로 소개된다. 저자들은 특정 물체의 사람 시연이 필요하고 한쪽 팔에만 촉각이 있다는 점을 구분한다. Hogan 등 [19]의 tactile palm 기반 pusher–slider 조작은 물체 궤적을 명시적으로 제어하지만, 미리 설계한 motion skill과 환경에 대한 충분한 지식을 요구한다는 한계를 지적한다. [원문 §II-B, PDF p. 2]

Bi-Touch는 이러한 비교에서, 양쪽 모두의 촉각을 사용하는 정책을 학습하고 미지 물체·예측하지 못한 외란에서 평가하는 benchmark를 제안한다. 기존 연구에 대한 평가는 이 논문 저자들의 서술 범위다. [원문 §II-B, PDF p. 2]

### 2.3 방법의 기반과 GUM의 위치

시뮬레이션·영상 이전의 기반은 Church 등 [7]의 **Tactile sim-to-real policy transfer via real-to-sim image translation**과 Lin 등 [8]의 **Tactile Gym 2.0**이다. GAN은 Isola 등 [23]의 image-to-image translation을 참조한다. 이 논문은 그 전체 최적화 절차를 다시 제시하지 않고, 양팔에 맞춘 관측 결합과 넓어진 데이터 수집 범위를 설명한다. [원문 §III-B, References, PDF pp. 3, 8]

Discussion에서는 GUM을 Hierarchical Visual Foresight [26]와 비교한다. 촉각 영상만으로는 목표 상태 정보가 제한되어 해당 방법을 그대로 적용하기 어렵기 때문에, 물체 중심 또는 TCP 위치로 생성한 선 위의 subgoal로 단순화했다는 설명이다. 저자들은 초기 환경 상태의 분포를 유지하면서 더 달성하기 쉬운 목표를 제공한다는 의미에서 이를 **implicit curriculum**으로 해석하고, PPO 같은 on-policy 학습에 사용할 수 있다는 점을 HER [27]와 대비한다. 이 비교는 원문 저자들의 설명이며, HER 계열 전체에 대한 별도의 문헌 검증은 하지 않았다. [원문 §V, PDF p. 8]

## 3. 환경과 로봇·센서 상세 사양

### 3.1 로봇 플랫폼과 배치

| 항목 | 원문에 명시된 내용 | 확인 범위·주의 |
| --- | --- | --- |
| 로봇 | **Dobot MG400 2대** | Industry-capable desktop robot arm으로 설명 |
| 각 팔의 자유도 | **4 DoF** | Cartesian x·y·z 위치와 말단 z축 회전 |
| 지지 테이블 높이 | **120 mm** | 두 팔 사이에 물체를 지지하는 보드 배치 |
| 베이스 간 거리 | **700 mm** | 보드 아래 중앙에 두 로봇 베이스를 배치 |
| 배치의 목적 | 세 과업에 공통으로 사용할 고정 배치에서 작업 영역 활용 | 과업별 베이스 재배치 전략을 학습하지 않음 |
| 말단 | 각 팔에 TacTip 1개 | 센서를 접촉 도구로 사용 |
| 실제 과업 action 차원 | Bi-pushing 4, bi-reorienting 6, bi-gathering 4 | 하드웨어 자유도 수와 정책 출력 차원을 구분 |
| 위치 정확도·반복정밀도 | UR5 같은 큰 산업용 팔과 같은 정확도라는 정성적 설명 | **이 논문에 수치 미명시** |
| 가반하중·reach·자중·footprint·가격 | 수치 미명시 | 이전 MG400 논문이나 제조사 사양으로 채우지 않음 |
| 관절 한계·속도·가속도·명령 주기 | 미명시 | 과업의 time step을 Hz로 환산하지 않음 |
| 보드 재료·마찰계수·전체 가로세로 치수 | 수치 미명시 | 사진의 외형에서 수치를 추정하지 않음 |

[원문 §III-A, §III-C, Fig. 1, PDF pp. 2–3]

### 3.2 TacTip의 감지 원리와 명시·미명시 사양

TacTip의 부드러운 피부 안에는 끝에 marker가 있는 돌출 pin들이 있다. 외부 자극에 의한 피부 변형을 pin의 움직임으로 증폭하고, 내부 광학 영상에서 이 움직임을 관측한다. 본 연구에서는 이 영상 자체를 학습·제어 경로에 사용한다. 별도 손목 F/T 센서나 힘 단위의 센서 출력은 실험 구성에 제시하지 않는다. [원문 §III-A-2, §III-B, PDF pp. 2–3]

| 사양 항목 | 원문 확인 결과 |
| --- | --- |
| 촉각 센서 수 | **2개**, 각 팔의 말단에 1개 |
| 센서 종류 | 저가 고해상도 biomimetic optical tactile sensor **TacTip** |
| 원신호 | 접촉에 따라 움직이는 내부 marker의 영상 |
| Marker·pin 개수 및 pitch | 수치 미명시 |
| Tip 직경·접촉 면적·피부 두께·재료 경도 | 수치 미명시 |
| 영상 촬영 해상도·정책 입력 해상도 | 수치 미명시 |
| Frame rate·센서 대역폭·전체 제어 주기 | 수치 미명시 |
| 최대 힘·토크·압력 측정 범위 | 미명시 |
| 힘 분해능·최소 검출 힘·감도·정확도 | 미명시 |
| 공간 해상도·위치 추정 정확도 | 정량 사양 미명시 |
| 데이터 수집의 접촉 깊이 | **[0.5, 8] mm** |
| 데이터 수집의 회전각 | **[−30°, 30°]** |
| Shear의 시뮬레이션 | **고려하지 않았다고 명시** |

[원문 §III-A–B, §V, PDF pp. 2–3, 8]

**[0.5, 8] mm와 ±30°는 GAN 학습용 접촉 pose의 수집 범위다. 센서의 최대 허용 변형·측정 범위·분해능이 아니다.** 또한 같은 TacTip 이름을 사용하더라도, 다른 논문에서 확인한 pin 수·해상도·치수를 이 논문의 보고값으로 옮기지 않았다.

### 3.3 관측, reward 정답, 목표 생성, 실물 평가를 구분

| 정보 | 논문에서의 사용 위치 | 혼동하면 안 되는 점 |
| --- | --- | --- |
| 두 촉각 영상 | 정책의 실행 관측 | 물체 전체 pose를 명시적으로 출력하는 별도 추정기는 제시하지 않음 |
| 각 팔의 pose·고유감각 | Fig. 1의 feature vector와 정책 입력 | 전체 scalar 목록·차원·좌표 변환은 미명시 |
| 목표·subgoal | 정책을 목표로 조건화하고 reward 계산에 사용 | 물체의 현재 pose와 명령 목표는 다름 |
| 시뮬레이션 물체 위치·방향 | 식 (1)–(4)의 reward, gathering 초기 curriculum의 target line | Reward에 등장한다고 동일한 값이 actor에 직접 들어간다는 뜻은 아님 |
| 실물의 두 TCP 위치 | Gathering의 target line 구성 | 실제 물체 중심을 정확히 관측한 값이 아님 |
| ArUco로 측정한 물체 위치·각도 | 실물 궤적·오차·완료 조건 확인 | Fig. 7은 policy가 visual feedback을 쓰지 않는다고 명시 |

[원문 Fig. 1–2, §III-B–C, §IV-B, Fig. 7 caption, PDF pp. 2–7]

특히 bi-gathering 실물 성공은 ArUco로 확인한 물체 중심 간 거리로 판정한다. 따라서 **정책의 시각 미사용**과 **실험 전체가 카메라 없이 종료·평가까지 수행됨**은 다른 주장이다. 본문만으로 독립적인 촉각 기반 물체 pose 추정기나 무시각 성공 판정기가 있다고 추가하지 않는다. [원문 §IV-B-3, Fig. 7 caption, PDF pp. 6–7]

## 4. Sim-to-real와 GAN — 무엇을 학습하고 어떻게 연결하는가

### 4.1 세 단계의 분리

시뮬레이션에서는 CAD로 만든 두 TacTip 내부의 synthetic camera가 접촉 영상을 생성한다. 두 영상을 결합한 관측과 고유감각으로 과업별 PPO 정책을 학습한다. 별도로 실제·시뮬레이션 접촉 영상 쌍으로 real-to-sim 변환 모델을 학습한다. 실물에서는 각 실제 영상을 변환한 후 정책에 전달한다. [원문 §III-B, Fig. 1, PDF pp. 2–3]

```text
정책 학습
  시뮬레이션 양팔·물체 상호작용
    → 두 synthetic tactile images + 로봇 상태·목표
    → 과업 reward → PPO 정책 학습

관측 변환 학습
  동일한 상대 접촉 pose에 대응하는 실제·시뮬레이션 영상 쌍
    → Image-to-image GAN 학습

실물 실행
  왼쪽 TacTip 영상 → Generator → 시뮬레이션형 영상 ┐
                                                   ├→ 결합 + 로봇 상태·목표
  오른쪽 TacTip 영상 → Generator → 시뮬레이션형 영상 ┘
    → 학습된 PPO 정책 → 양팔 TCP 명령 → 새로운 접촉 영상
```

이 흐름은 원문을 재구성한 것이다. PPO와 GAN을 동시에 하나의 end-to-end loss로 학습하는 구조가 아니다. 실물 실행에는 생성기가 사용되며 discriminator를 로봇 제어기로 사용하는 것이 아니다. [원문 Fig. 1, §III-B, PDF pp. 2–3]

### 4.2 영상 변환 데이터 수집

세 과업이 공통으로 요구하는 contact feature는 **평평하거나 상대적으로 평평한 표면**이다. 알려진 평면에 센서를 여러 상대 pose로 접촉시키고, 시뮬레이션과 실물에서 대응하는 random contact를 수집한다. 표면과 센서 사이의 상대 pose가 label로 기록되며, GAN의 변환 목표는 pose 자체가 아니라 대응하는 simulated tactile image다. [원문 §III-B, Fig. 1(b), PDF pp. 2–3]

| 항목 | 원문 명시 내용 |
| --- | --- |
| Contact feature | Flat / relatively flat surface |
| 접촉 깊이 | **0.5–8 mm** |
| 회전 범위 | **−30°–30°** |
| Training dataset | **5,000 tactile images** |
| Validation dataset | **2,000 tactile images** |
| 실제·시뮬레이션 대응 | 양쪽에서 paired random contacts 수집 |
| Label | 알려진 평면에 대한 센서의 relative pose |
| 넓어진 범위의 이유 | 단일 팔보다 어려운 제어를 요구하는 양팔 과업에서 더 넓은 sensing space 필요 |
| GAN 방식 | Image-to-image translation GAN [23], Fig. 1(b)에 **Pix2Pix GAN**으로 표기 |
| 학습 hyperparameter | **이전 연구 [7]의 값을 사용한다고 명시** |

[원문 §III-B, Fig. 1(b), PDF pp. 2–3]

이 숫자는 원문이 제시한 training/validation 데이터셋의 규모다. 본문은 센서별 데이터셋 분할·가중치 공유 여부를 완전히 기술하지 않으므로, ‘각 TacTip에 5,000장씩 별도 학습’ 또는 ‘두 센서 전체를 합쳐 정확히 5,000장’ 중 하나를 확정해 추가하지 않는다. 그림은 한 변환 블록에 두 센서의 영상이 들어가는 구성을 나타내지만, 센서 간 calibration·모델 관리의 구현 명세는 아니다.

### 4.3 실물에서는 변환을 먼저 하고 두 영상을 결합

두 실제 TacTip 영상을 **각각** 시뮬레이션 영상으로 변환하고, 그 결과를 concatenation하여 정책 입력으로 사용한다. Fig. 1(a), (c)는 두 접촉 패턴이 나란히 들어가고, 그 아래에 `{Pose¹, Pose², Goal}` feature vector가 연결되는 구조를 보여 준다. 단, tensor의 실제 배치 축, encoder의 공유 여부, 채널 수, feature vector의 세부 성분은 본문에 없다. [원문 §III-B, Fig. 1, PDF pp. 2–3]

정책이 양쪽 영상을 함께 받는 것과 ‘두 접촉점의 힘을 수치로 합성하거나 평형을 계산한다’는 것은 다르다. 이 논문에는 영상에서 힘·토크 벡터를 추정한 후 이를 합산하는 별도 처리 단계가 제시되지 않는다.

### 4.4 GAN 학습 설명의 한계

원문은 **입력·출력의 종류, paired data, 수집 범위·표본 수, Pix2Pix 계열 방법, 이전 연구의 hyperparameter 사용**을 알려 준다. 그러나 adversarial loss·reconstruction loss의 구체식과 계수, optimizer, learning rate, batch size, epoch 수, network 층별 크기, crop·resize·normalization, stopping criterion은 이 논문 자체에 수치로 전개하지 않는다. 이를 확인하려면 저자들이 지정한 [7]과 해당 실험 구현을 별도로 읽어야 한다. 본 정리에서는 일반적인 Pix2Pix 기본 설정을 실제 실험값으로 채우지 않았다. [원문 §III-B의 확인 범위, PDF p. 3]

실물 촉각 데이터는 GAN 학습에 사용된다. 따라서 sim-to-real을 **실제 데이터가 전혀 필요 없는 학습**으로 표현해서는 안 된다. 또한 이 연구는 실물에서 발견한 압착 문제를 바탕으로 시뮬레이션 학습을 수정한다. 시뮬레이션 정책을 실물 PPO로 계속 미세조정하는 절차는 제시하지 않지만, 실물 시험 피드백 없이 한 번에 모든 이전이 완료된 것으로도 설명하지 않는다. [원문 §III-B–C-2, PDF pp. 3–4]

## 5. PPO 학습과 행동 공간의 공통 정의

### 5.1 사용 알고리즘과 확인되지 않은 설정

세 과업 모두 **on-policy, model-free PPO**로 학습하며 Stable-Baselines3 구현을 사용한다. 원문은 과업별 reward, 일부 환경 sampling, curriculum과 외란 조건을 구체적으로 제시한다. 반면 PPO actor·critic 구조, learning rate, rollout length, batch·epoch, gamma·GAE, clip·entropy 계수, seed와 병렬 환경 수는 본문에 없다. [원문 §IV-A, PDF p. 5]

따라서 이 논문은 reward조차 이름만 언급하는 자료는 아니다. **식 (1)–(4)는 직접 주어진다.** 다만 reward의 정확한 가중치, 학습 configuration 전체, GAN 최적화 recipe까지 이 PDF 하나로 완결되지는 않는다.

### 5.2 TCP 기준의 과업별 action

| 과업 | 팔 하나가 선택하는 성분 | 양팔 전체 차원 |
| --- | --- | --- |
| Bi-pushing | **x-position, Rz-rotation** | **4** |
| Bi-reorienting | **x-position, y-position, Rz-rotation** | **6** |
| Bi-gathering | **y-position, Rz-rotation** | **4** |

모든 말단은 **자신의 TCP frame**에서 제어·이동한다. 위 축 이름을 전역 좌표계의 좌우·전후와 그대로 동일시하지 않는다. 원문은 각 action의 허용 크기, absolute target과 increment의 구현 구분, 각도 단위 변환, 비선택 축의 feedforward·고정 명령을 완전히 정의하지 않는다. 다른 pushing 논문에서 사용한 ‘1 mm 고정 전진’ 같은 설정을 가져오지 않았다. [원문 §III-C, PDF p. 3]

### 5.3 Reward 기호의 공통 의미

| 기호 | 의미 |
| --- | --- |
| $p_t^o,\theta_t^o$ | 물체의 현재 위치·방향 |
| $p_0^o$ | 물체의 초기 위치 |
| $p_t^g,\theta_t^g$ | 현재 목표의 위치·방향 |
| $p_t^{e_i},\theta_t^{e_i}$ | i번째 팔 TCP의 위치·방향 |
| $p_{\mathrm{ctrl}_i}^{o}$ | 물체 양쪽에 지정한 원하는 접촉 위치 |
| $o_i$ | Gathering에서 i번째 물체 |
| $w_j>0$ | Reward 가중치. **실제 값 미명시** |
| $\lVert\cdot\rVert_2$ | 위치 차이의 Euclidean norm. **제곱 norm이 아님** |

원문이 정의한 각도 차이 함수는 다음과 같다.

$$
S(\phi,\psi)=1-\cos(\phi-\psi).
$$

[원문 식 (1)–(4), Fig. 2, PDF pp. 3–4]

Fig. 2에서 빨간색은 goal/subgoal, 주황색은 observation에 포함되는 proprioceptive information, 검은색은 object centre, 초록색은 desired contact point, 파란색은 subgoal candidate와 target line이다. **Desired contact point는 센서가 측정한 압력 중심이 아니라 reward를 위한 기하학적 기준점**이다. 이 구분은 접촉 깊이와 힘 처리의 해석에 중요하다. [원문 Fig. 2 및 §III-C, PDF pp. 3–4]

서로 다른 과업에서 같은 $w_j$ 표기를 재사용하지만, 가중치 값이 과업 간 같다는 설명은 없다. 목표·접촉 방향각의 좌표 convention도 식과 Fig. 2의 범위에서만 제시되므로, 원문의 부호를 임의로 ‘물리적으로 자연스러운 식’으로 교체하지 않는다.

## 6. Bi-pushing — 큰 물체의 경로·방향 추종

### 6.1 과업과 reward

두 팔이 큰 물체 하나를 함께 밀어, 주어진 경로상의 위치와 방향 목표를 순서대로 달성한다. 이 과업의 목표는 단순 접촉점 도달이 아니라 **물체 위치·방향의 경로 추종**으로 정의된다. [원문 §III-C-1, PDF p. 3]

**원문 식 (1)**

$$
\begin{aligned}
R_t^{\mathrm{BP}}={}&-w_1\lVert p_t^g-p_t^o\rVert_2
-w_2S(\theta_t^g,\theta_t^o)\\
&-w_3\sum_{i=1}^{2}S(\theta_t^{e_i},\theta_t^o).
\end{aligned}
$$

| 항 | 감소시키는 오차 | 저자들이 설명하는 기능 |
| --- | --- | --- |
| 첫째 | 현재 목표와 물체의 위치 차이 | 물체를 경로의 현재 목표 위치로 이동 |
| 둘째 | 목표와 물체의 방향 차이 | 경로에서 요구하는 방향으로 물체 정렬 |
| 셋째 | 각 TCP와 물체의 방향 차이 | 두 TacTip을 접촉면에 수직으로 유지하여 stable pushing 유도 |

[원문 식 (1), Fig. 2(a), PDF p. 3]

세 번째 항은 각 팔의 정렬을 공동 reward에 반영한다. ‘양팔 힘을 동일하게 맞추는 항’이나 ‘두 팔 사이의 내부 힘을 최소화하는 항’은 아니다. 원문은 reward의 목적을 contact-normality로 설명하지만, 실행 중 이 각도를 촉각에서 회귀해 직접 gain 제어하는 모듈은 제시하지 않는다. 촉각 영상에 반응하는 행동은 PPO가 학습한다.

### 6.2 학습 경로와 환경

각 episode에서 직선 또는 정현파 경로를 샘플링하고, 그 위의 goal sequence를 물체 목표 궤적으로 사용한다. [원문 §IV-A-1, PDF p. 5]

$$
y=kx\quad\text{또는}\quad y=a\sin(x/50),
$$

$$
k\in[-0.28,0.28],\qquad a\in[-20,20],\qquad
x\in[-280,50]\ \mathrm{mm}.
$$

위 수식과 범위는 원문 표기를 따른다. Table I의 시뮬레이션 물체는 **400 mm cuboid**로 표시된다. Goal의 전체 개수, waypoint 전환 tolerance, 목표 방향을 경로에서 계산하는 구체식, 물체 초기 pose 분포, 접촉 높이·초기 penetration, 시뮬레이션 질량·마찰은 본문에 없다. [원문 §IV-A-1, Table I, PDF p. 5]

## 7. Bi-reorienting — 중심 유지, 회전, 과도한 압착의 해소

### 7.1 과업과 reward

양팔이 물체 양쪽에서 접촉하여 목표 각도까지 회전시키되, 물체 중심은 시작 위치에서 크게 움직이지 않게 한다. 접촉면에 대한 말단의 정렬과 원하는 접촉 위치 유지도 함께 요구한다. [원문 §III-C-2, Fig. 2(b), PDF pp. 3–4]

**원문 식 (2)**

$$
\begin{aligned}
R_t^{\mathrm{BR}}={}&-w_1\lVert p_0^o-p_t^o\rVert_2
-w_2S(\theta^g,\theta_t^o)\\
&-w_3\sum_{i=1}^{2}
S\left(\theta_t^{e_i},(-1)^i(\pi/2+\theta_t^o)\right)\\
&-w_4\sum_{i=1}^{2}
\lVert p_{\mathrm{ctrl}_i}^{o}-p_t^{e_i}\rVert_2.
\end{aligned}
$$

| 항 | 기능 | 해석의 경계 |
| --- | --- | --- |
| 중심 위치 항 | 초기 물체 중심과 현재 중심의 차이를 억제 | 물체 중심을 hard constraint로 고정하는 것은 아님 |
| 목표 각도 항 | 지정된 각도에 접근하도록 유도 | 성공 조건의 ‘각도 변화 1°’와 구분 |
| TCP 방향 항 | 양쪽 TCP를 접촉면에 수직으로 정렬 | 원문의 좌우 부호 convention 유지 |
| 접촉 위치 항 | TCP를 양쪽 desired contact point에 가깝게 유지 | 접촉 깊이·접촉 소실을 다루는 기하학적 shaping이지 뉴턴 단위 force tracking이 아님 |

[원문 식 (2)와 직후 설명, PDF pp. 3–4]

Fig. 2(b)의 초록색 $p_{\mathrm{ctrl}_i}^{o}$는 물체 양쪽의 원하는 TCP 접촉 위치다. 이 항은 너무 멀어져 접촉을 잃는 행동을 줄이는 데 사용된다. 그러나 기준점의 정확한 생성식, 물체 표면으로부터의 offset, 이 값이 물체 크기에 따라 변하는 방식은 본문에 수치로 설명되지 않는다. 원문 식의 위치 차이 항을 별도의 측정 접촉력 오차식으로 바꾸지 않는다.

### 7.2 최초 실물 이전에서 나타난 squeezing

원래 simulated TacTip의 stiffness·damping을 사용해 식 (2)로 학습한 정책은 실물에서 **큰 목표 각도일수록 물체를 강하게 압착하며 회전**시키는 경향이 있었고, 물체가 길수록 심해졌다. 저자들은 정책이 reward를 빠르게 얻기 위해 시뮬레이션에서 압착을 이용한 회전을 학습한 것으로 해석한다. 실제에서는 TacTip의 과변형에 의한 파손과 낮은 강성 물체의 문제가 있어 적합하지 않은 정책이었다. [원문 §III-C-2, PDF p. 4]

이는 힘센서의 과부하 경보를 추가해 해결한 사례가 아니다. **시뮬레이션에서 유리했던 접촉 전략이 실제 피부·물체 조건에서는 부적절한 행동으로 나타난 sim-to-real 문제**로 분석하고, 정책을 학습시키는 조건을 변경했다.

### 7.3 저자들이 시행한 네 가지 학습 수정

| 수정 | 원문에 적힌 내용 | 확인되지 않은 세부 |
| --- | --- | --- |
| **센서 동역학 수정** | TacTip 피부 stiffness·damping 조정. 뒤의 설명에서 **높은 stiffness·낮은 damping**을 명시 | 변경 전·후 계수와 단위 |
| **목표 유지 조건** | 목표 방향 달성을 위해 물체 pose를 **10 time steps** 유지 | 학습 코드의 pose 허용 오차·검사 구현 |
| **과도한 압착 penalty 강화** | **큰 contact depth**로 판단되는 over-squeezing의 penalty coefficient 증가 | 깊이 threshold, 강화된 penalty의 정확한 식·값 |
| **큰 목표 각도에 더 높은 학습 비중** | 큰 goal angle이 더 높은 확률로 나오도록 학습 | 최종 sampling distribution·변경 시점 |

[원문 §III-C-2, PDF p. 4]

원문은 네 수정에 대한 ablation을 수행했고 **첫 번째 변경이 성공적인 실물 이전에 가장 크게 기여했다**고 보고한다. 다만 조합별 성공률·정량 수치가 있는 별도의 ablation 표는 본문에 없다. 따라서 기여의 순서에 관한 저자 보고는 기록하되, 효과 크기를 임의로 수치화하지 않는다.

### 7.4 Stiffness 수정의 의미를 바꾸어 설명하지 않기

저자들은 높은 stiffness와 낮은 damping이 피부를 외부 접촉에 더 ‘elastic’하게 만들고, 시뮬레이션 촉각 이미지가 contact depth에 더 잘 반응하여 정책이 깊이에 민감해진다고 설명한다. **이를 ‘피부 강성을 낮춰 더 부드럽게 만들었다’로 번역하면 원문과 반대가 된다.** Elastic과 soft를 같은 의미로 치환하지 않았다. [원문 §III-C-2, PDF p. 4]

원문에 근거한 정보–학습 연결은 **센서 접촉 동역학 변경 → 깊이에 따른 관측·상호작용 변화 → 정책이 학습하는 접촉 전략의 변화 → 과도한 압착이 있는 실물 이전 문제의 완화**다. 정확한 물리계수, 영상 변화량, 최대 접촉력의 전후 비교가 없으므로 이보다 정량적인 설명은 할 수 없다.

### 7.5 크기·목표 sampling과 angle curriculum

기본 학습 설정은 물체 길이 $l$을 **[50, 200] mm**, 목표 각도 $\theta^g$를 **[30°, 90°]**에서 균일 샘플링하는 것이다. 목표 각도는 **10개 subgoals**로 균등하게 나누어 curriculum으로 사용한다. [원문 §IV-A-2, PDF p. 5]

여기서 **10개 각도 subgoals**와 **10 steps의 pose 유지**는 별개의 설정이다. 또한 §III-C-2의 큰 각도 확률 증가와 §IV-A-2의 균일 sampling 서술은 함께 존재한다. 원문은 수정 전·후의 완전한 분포와 시행 순서를 제공하지 않으므로, 두 내용을 하나의 확정 sampling 함수로 통일하지 않는다.

실물에서는 **방향별로 서로 다른 정책**을 학습했다고 명시한다. 한 정책이 모든 회전 방향을 처리한다는 주장과 구분해야 한다. [원문 §IV-B-2, PDF p. 6]

## 8. Bi-gathering — 움직이는 목표, GUM, curriculum

### 8.1 서로가 움직이는 목표가 되는 문제

각 팔은 물체 하나를 밀고, 두 물체가 가까워져야 한다. 상대 물체의 현재 위치를 직접 목표로 사용하면 그 목표도 계속 움직인다. 저자들은 이 점이 static goal을 따르는 pushing보다 어려운 탐색 문제를 만든다고 설명한다. [원문 §III-C-3, PDF p. 4]

**원문 식 (3)**

$$
\begin{aligned}
R_t^{\mathrm{BG}}={}&-w_1\lVert p_t^{o_1}-p_t^{o_2}\rVert_2\\
&-w_2\sum_{i=1}^{2}S(\theta_t^{e_i},\theta_t^{o_i})\\
&-w_3\sum_{i=1}^{2}\lVert p_{\mathrm{ctrl}}^{o_i}-p_t^{e_i}\rVert_2.
\end{aligned}
$$

첫째 항은 두 물체 사이의 거리를 줄이고, 둘째 항은 각 TCP의 접촉면 정렬을 유도하며, 셋째 항은 TCP가 desired contact point를 유지하여 접촉을 잃지 않게 한다. $p_{\mathrm{ctrl}}^{o_i}$는 원문 설명에서 TCP의 contact depth를 조절하기 위한 원하는 접촉 위치다. [원문 식 (3), Fig. 2(c), PDF p. 4]

저자들은 이 단순한 목표 구성으로는 외란 유무와 관계없이 성능이 좋지 않았다고 설명하며 ‘moving sparse goal’이라고 부른다. 다만 **식 (3) 자체는 거리·각도 차이의 연속 penalty를 이미 포함**한다. 따라서 저자들의 표현을 ‘보상이 성공 순간에만 발생하는 완전 sparse reward였다’로 바꾸어 설명하지 않는다. 보강한 것은 목표의 중간 구조와 auxiliary reward다.

### 8.2 Goal-update mechanism: 선 위의 subgoal

GUM은 두 물체를 향한 이동을 한 번에 해결하는 대신, **target line 위의 여러 후보 점 중 subgoal을 정하고 일정 시간 동안 해당 목표로 유도**한다. Fig. 2(c)는 두 물체, 이를 연결하는 target line, 파란 subgoal 후보, 선택된 빨간 subgoal을 보여 준다. [원문 §III-C-3, Fig. 2(c), PDF pp. 3–4]

| 요소 | 원문 설명·설정 |
| --- | --- |
| Target line | 초기 학습은 두 물체 중심, 이후 학습·실물 적용은 두 TCP를 기준으로 구성 |
| 후보 점 | 선 위에 같은 간격으로 배치한 **n개 static points** |
| n 후보 | **5, 10, 20** 비교 |
| 채택 n | **10**, 다른 값보다 약간 더 좋았다고 보고 |
| Subgoal 선택 | 각 팔에 더 가까운 물체를 기준으로, 생성된 점 중 그 물체에 가장 가까운 점 선택 |
| Target line 갱신 | **h time steps마다** |
| h 후보 | **25, 50, 75, 100** 비교 |
| 채택 h | **75**, 가장 좋았다고 보고 |

[원문 §III-C-3, §IV-A-3, PDF pp. 4–5]

갱신이 지나치게 드물면 원하는 방향으로 충분히 안내하지 못하고, 지나치게 빠르면 subgoal에 도달할 시간이 부족하다는 것이 저자들의 설명이다. **75는 step 수이지 Hz가 아니다.** Action 실행 주기가 없으므로 초 단위 갱신 간격도 확정할 수 없다.

원문에는 target line의 끝점 포함 여부, 최근접점 동률 처리, 목표 도달 후 즉시 다음 점을 고르는지 여부를 모두 결정하는 의사코드가 없다. 특히 후보 점 개수와 선택 규칙만으로 완전한 구현이 유일하게 정해지는 것은 아니다. 이 세부를 자동으로 채운 ‘원문 알고리즘’은 제시하지 않는다.

### 8.3 GUM의 auxiliary reward

**원문 식 (4)**

$$
\begin{aligned}
R_t^{\mathrm{BG\text{-}GUM}}={}&R_t^{\mathrm{BG}}
-w_4\sum_{i=1}^{N}\lVert p_t^{g_i}-p_t^{o_i}\rVert_2\\
&-w_5\sum_{i=1}^{N}S(\theta_t^{o_i},(-1)^i\theta_t^c).
\end{aligned}
$$

추가한 첫 항은 물체가 선택된 subgoal에 가까워지게 하고, 마지막 항은 target line 방향으로 밀리도록 물체 방향을 유도한다. 기존 식 (3)의 물체 간 거리 감소·접촉 정렬·접촉 유지 항은 그대로 포함된다. **GUM은 접촉 유지 reward를 대체하지 않고, 그 위에 방향·중간 목표 안내를 추가한다.** [원문 식 (4) 및 직후 설명, PDF p. 4]

식 (4)의 $N$은 원문이 실제로 사용하는 대문자 표기다. 문맥상 두 물체에 대한 합을 나타내지만, 그 문장에서 $N$의 정의는 별도로 주어지지 않는다. **후보 subgoal 수인 소문자 $n=10$과 혼동해서 합을 10개 물체에 대한 것으로 바꾸지 않는다.** $\theta_t^c$의 문장 정의는 불완전하지만, 직후의 ‘target line direction’ 설명과 Fig. 2(c)에서 target line 방향을 나타내는 각도로 해석된다. 정확한 각도 성분식·부호 convention은 미명시다.

### 8.4 실물에서 물체 pose를 몰라도 target line을 만드는 방법

실물에서는 물체 pose를 모르므로 target line을 **두 TCP 위치**로 만든다. 그러나 처음부터 이 선을 사용하는 시뮬레이션 학습은 실패했다. 초기 random policy가 물체와의 접촉을 유지하지 못하므로, 두 TCP를 잇는 선이 물체를 모으는 데 유용한 정보를 제공하지 못했다는 설명이다. [원문 §III-C-3, PDF p. 4]

이를 위해 도입한 2단계 curriculum은 다음과 같다.

```text
1단계: 물체 중심을 사용해 target line 생성
  → GUM subgoal과 reward로 정책을 처음부터 학습

2단계: TCP 위치로 target line의 구성 기준 변경
  → 같은 정책을 추가 학습하여 실제 관측 조건에 맞춤
  → Curriculum 동안 외란 확률·크기도 증가

실물: 현재 TCP 위치로 target line을 구성하여 실행
```

[원문 §III-C-3, PDF pp. 4–5]

이 연결의 핵심은 **물체 중심을 촉각에서 정확히 복원하는 모듈을 추가한 것이 아니라, 목표를 구성하는 데 사용하는 정보원을 학습 단계에 따라 바꾼 것**이다. 첫 단계에서 simulation object centres를 사용한다는 사실, 둘째 단계와 실물에서 TCP를 사용한다는 사실을 분리해야 한다. 변경 시점·학습량·성공률에 따른 전환 조건은 원문에 없다.

또한 target line을 TCP 기반으로 바꾼다고 해서 식 (3)–(4)의 training reward에 들어가는 object state까지 없어진다는 뜻은 아니다. **목표 생성용 정보, reward 평가용 simulator state, actor observation은 서로 다른 역할**이다. 정확한 전체 observation·critic 구성은 본문만으로 확정할 수 없다.

### 8.5 초기 물체 위치와 외란 학습

원문은 각 물체의 초기 위치 $p_0^{o_i}=(x^i,y^i)$를 다음 범위에서 균일 샘플링한다고 명시한다.

$$
x^i\in(-1)^i[50,200]\ \mathrm{mm},\qquad
 y^i\in(-1)^i[0,100]\ \mathrm{mm},\qquad i\in\{1,2\}.
$$

원문 부호 범위를 풀어 읽으면, 첫 물체는 음의 x·y 구역, 두 번째 물체는 양의 x·y 구역에서 시작한다. 이는 제시된 부호식의 해설이며, 초기 orientation이나 TCP reset 분포까지 정해 주는 식은 아니다. [원문 §IV-A-3, PDF p. 5]

외란 학습에서는 임의 시점에 물체 질량중심에 random force를 가하고, 보고한 force 크기의 샘플링 범위는 **[1, 5] N**이다. Curriculum 동안 적용 확률과 크기를 증가시켰다는 설명도 있다. 힘의 방향 분포·지속시간·빈도 스케줄·증가 단계별 범위는 미명시다. [원문 §III-C-3, §IV-A-3, PDF pp. 4–5]

**1–5 N은 시뮬레이션에서 가한 외란의 크기다. 센서의 측정 범위나 검출 threshold, 실제 외란 측정값이 아니다.** 실물에서도 random force perturbation을 가했다고 서술하지만, 그 힘을 계측·제어한 방법과 수치는 본문에 없다.

### 8.6 종료 조건은 시뮬레이션과 실물이 다르다

시뮬레이션에서는 두 물체 사이 거리 $d$가 threshold보다 작아지면 완료로 정의하며, $\epsilon=90$ mm를 사용한다. 실물에서는 약 6 cm 길이의 물체들을 사용하고, **300 time steps 이내에 ArUco로 확인한 물체 중심 사이 거리가 7 cm 미만**일 때 성공으로 판정한다. [원문 §III-C-3, §IV-A-3, §IV-B-3, PDF pp. 4–6]

따라서 실물 성공률을 시뮬레이션의 90 mm 기준과 동일한 조건으로 비교하면 안 된다. 또한 거리 기반 성공이 모든 형상에서 실제 물체 간 안정된 접촉이나 파지를 보장하는 정의는 아니다.

## 9. 힘·접촉 정보가 미는 행동까지 연결되는 방식

### 9.1 직접 사용한 것은 wrench가 아니라 변형 영상이다

전체 처리 경로를 정보의 단위와 기능에 따라 구분하면 다음과 같다.

| 단계 | 데이터·처리 | 원문이 뒷받침하는 역할 |
| --- | --- | --- |
| 물리 접촉 | 피부 변형과 내부 marker 이동 | 현재 국소 접촉의 촉각 영상 생성 |
| 관측 이전 | 실제 영상 → GAN → simulation-like tactile image | 실제·학습 관측 외형의 차이 완화 |
| 관측 결합 | 두 영상 + 각 팔의 고유감각 + 목표 | 양쪽 접촉을 함께 반영하는 정책 입력 |
| 학습 목표 | 물체 목표·접촉 정렬·desired contact point penalty | 어떤 조작과 접촉을 선호할지 reward로 규정 |
| 행동 | 과업별 4차원 또는 6차원 TCP 위치·회전 성분 | 두 팔의 운동을 함께 결정 |
| 폐루프 | 새로운 접촉 이후 새 영상을 다시 입력 | 접촉 변화에 따른 행동 수정 |

[원문 Fig. 1–2, §III, PDF pp. 2–4]

위의 영상→행동 연결은 원문의 시스템 구조다. 반면 **policy 내부에 특정 force estimate, friction coefficient, contact-mode classifier가 형성됐다는 것은 본문으로 확인할 수 없다.** 최종 행동의 일반화만으로 내부 계산의 물리량을 확정하지 않는다.

### 9.2 접촉 깊이는 세 군데에서 다른 역할로 등장한다

첫째, **GAN 학습 데이터의 0.5–8 mm**는 대응 영상을 수집하는 pose 범위다. 둘째, **desired contact point와 TCP의 거리 penalty**는 유지해야 할 접촉 기하를 정의한다. 셋째, **reorienting의 over-squeezing penalty와 센서 동역학 수정**은 과도한 penetration을 활용하는 정책이 학습되지 않도록 조건을 바꾸는 조치다. [원문 §III-B–C, PDF pp. 3–4]

이들을 합쳐 ‘GAN이 깊이를 scalar로 출력하고, 이를 F/T처럼 힘 제어했다’고 설명하면 안 된다. 원문에서 GAN의 출력은 영상이고, 깊이·힘을 직접 회귀하는 별도 네트워크나 명시적인 force feedback control law는 없다.

### 9.3 접촉 정렬과 두 접촉의 협조

Bi-pushing에서는 두 TCP 방향이 물체 접촉면에 맞도록 reward를 준다. Bi-reorienting에서는 서로 다른 양쪽 접촉면 방향을 고려하고, TCP가 원하는 접촉 위치를 유지하도록 한다. Bi-gathering에서는 각 물체에 대한 접촉 정렬·유지를 유지하면서, 두 물체가 목표 선의 subgoal을 향하도록 유도한다. [원문 식 (1)–(4), Fig. 2, PDF pp. 3–4]

즉, 양팔의 협조는 **공유된 과업 목표와 양쪽 접촉을 평가하는 reward, 두 촉각 영상을 함께 받는 정책**을 통해 학습된다. 두 개의 독립 단일팔 정책을 아무 조건 없이 병렬 실행한 것으로 설명하지 않으며, 반대로 별도의 wrench allocation 최적화가 있다고 추가하지도 않는다.

### 9.4 실제 힘·물성 차이가 나타난 사례와 증거 수준

Bi-pushing에서 879 g loudspeaker는 244 g box와 127 g tube와 다른 말단 궤적을 보였다. 저자들은 더 큰 마찰력에 대응하여 말단이 loudspeaker의 끝쪽으로 이동하면서 물체 중심을 목표 경로에 유지한 것으로 설명한다. **접촉 변화에 대한 행동 적응의 사례**로 볼 수 있지만, 마찰력을 직접 측정해 수치로 feedback한 실험은 아니다. [원문 §IV-B-1, Fig. 5, PDF p. 6]

Bi-gathering의 가벼운 foam toy는 실제 TacTip을 시뮬레이션 cube보다 훨씬 약하게 변형시키며, mug handle은 학습과 다른 접촉 형상을 만든다. 이러한 조건에서도 성공 사례가 나타났다는 것이 저자들의 일반화 근거다. 그러나 외란이 많아질수록 실패율이 올라가므로, 약한 신호와 임의 접촉 형상을 항상 해결한다는 결론으로 확대하지 않는다. [원문 §IV-B-3, Table III, Fig. 7, PDF pp. 6–7]

### 9.5 힘 사용에 관한 명확한 경계

원문에는 목표 접촉력 추종, 손목 모멘트 제어, 힘 평형 계산, force threshold 기반 종료, admittance·impedance gain의 온라인 조절이 제시되지 않는다. 실물의 과도한 압착 문제는 접촉 깊이·센서 동역학·학습 조건의 문제로 다뤄진다. **힘의 중요성을 동기로 언급하는 것과 실제로 힘을 측정·복원·제어하는 것은 구분해야 한다.** [원문 §I, §III, §V, PDF pp. 1–4, 8]

## 10. 실험 조건과 결과

### 10.1 학습 곡선의 축과 평가 지표

Fig. 3은 세 과업의 **episode당 완료 step 수**를 학습 진행에 따라 보여 주며, caption은 10 trials 평균이라고 설명한다. 적은 step으로 끝낼수록 좋은 결과다. 그래프의 가로축은 **Episodes**, 세로축은 **Episode Steps**로 표시되어 있다. Reward curve나 wall-clock time, environment transition 총수로 바꾸어 읽지 않는다. [원문 Fig. 3, §IV-A, PDF p. 5]

Bi-pushing은 비교적 매끄럽고 일찍 수렴한다. Reorienting은 학습 중 변동이 더 크다. Gathering에서는 **GUM 없음/있음 × 외란 없음/있음**의 네 조건을 비교한다. GUM을 사용한 두 조건이 더 짧은 episode로 수렴하고, 외란이 있어도 없는 경우와 비슷한 수준에 도달했다고 보고한다. Exact seed 수·오차대 정의·모든 run configuration은 본문에 없다. [원문 §IV-A, Fig. 3, PDF p. 5]

### 10.2 Bi-pushing의 물체, 치수, 질량, 경로 오차

시뮬레이션은 직선·정현파 각각 10회, 총 20회 평가한다. 실물도 세 물체 각각에 대해 같은 두 경로 유형의 20회 시험 결과를 보고한다. Table I의 accuracy는 물체 궤적의 ground-truth 궤적 대비 평균 오차와 표준편차이며, 각도 오차나 최대 힘이 아니다. [원문 §IV-A-1, §IV-B-1, Table I, PDF pp. 5–6]

**Table I 및 §IV-B-1**

| 물체 | 환경 | 궤적 오차 | 원문 Size | 질량 |
| --- | --- | --- | --- | --- |
| Cuboid | Simulation | **12.3 ± 4.8 mm** | **400 mm** | 미명시 |
| Tripod box | Real | **14.2 ± 6.4 mm** | **351 mm** | **244 g** |
| Shuttle tube | Real | **16.6 ± 7.7 mm** | **386 mm** | **127 g** |
| Loudspeaker | Real | **17.4 ± 8.1 mm** | **377 mm** | **879 g** |

Table I의 `Size`는 한 개 길이만 제공한다. 가로·세로·높이 전체 치수로 확대하지 않는다. 실물 이동 거리는 **300–420 mm**이며, 세 물체는 flat·curved·sloping 등 다른 접촉면을 갖는다. [원문 Table I, §IV-B-1, Fig. 4–5, PDF pp. 5–6]

Fig. 5에서 물체 궤적은 빨간색, TacTip 궤적은 초록색 화살표다. 말단 궤적의 변화와 물체 중심 궤적을 구분해야 한다. 더 무거운 loudspeaker에서의 행동 차이는 §9.4에 정리한 저자들의 마찰 설명과 연결된다. [원문 Fig. 5 및 §IV-B-1, PDF p. 6]

### 10.3 Bi-reorienting의 정량 결과

시뮬레이션은 10회 시험 결과를 보고한다. Translation error는 시작 위치와 최종 물체 위치의 차이로 정의한다. 실물에서는 ArUco가 부착된 **물체 상단 중심 위치**를 object position으로 삼고, 목표 방향의 최종 subgoal에서 **10 steps 동안 물체 각도가 1°보다 크게 변하지 않을 때** 과업 달성으로 간주한다고 설명한다. [원문 §IV-A-2, §IV-B-2, PDF pp. 5–6]

**이는 ‘목표 각도 오차가 1° 이하’라는 정의가 아니다.** 아래 실제 orientation error가 7.5–13.4° 수준인 것과 모순되게 새 성공 기준을 만들지 않는다.

**Table II — 원문 값**

| 물체 | Translation error | Orientation error | Size |
| --- | --- | --- | --- |
| Cube (Simulation) | **10.2 ± 4.8 mm** | **3.4 ± 1.8°** | **100 mm** |
| Plastic cube | **12.5 ± 5.3 mm** | **7.5 ± 3.9°** | **100 mm** |
| Shoe box | **16.2 ± 6.8 mm** | **11.5 ± 5.2°** | **193 mm** |
| Cracker box | **13.9 ± 5.6 mm** | **8.4 ± 4.7°** | **172 mm** |
| Cubes box | **15.5 ± 5.5 mm** | **9.2 ± 5.6°** | **186 mm** |
| Mustard bottle | **13.6 ± 5.4 mm** | **7.6 ± 4.1°** | **122 mm** |
| Goblet | **18.1 ± 6.1 mm** | **12.2 ± 5.8°** | **113 mm** |
| Soft brain toy | **17.2 ± 6.7 mm** | **9.7 ± 5.3°** | **85 mm** |
| Red ball | **19.5 ± 7.0 mm** | **13.4 ± 6.5°** | **70 mm** |
| Triangular prism | **—** | **—** | **57 mm** |

[원문 Table II, PDF p. 5 / 인쇄 p. 5476]

저자들은 cube 계열에서 학습했기 때문에 round object에서 정확도가 떨어지며, 큰 물체는 말단 이동이 길고 양팔 협조가 어려워 오차가 증가한다고 설명한다. 이는 경향에 대한 저자 해석이며, 표의 모든 물체에서 size와 error가 단조 관계를 보인다는 뜻은 아니다. [원문 §IV-B-2, PDF p. 6]

Triangular prism은 날카로운 모서리에서 불안정한 접촉과 slippage가 발생하고, 학습에서 경험하지 않은 복구 불가능한 상태로 빠졌다고 보고한다. 표의 대시는 0 오차가 아니라 유효한 완료 오차를 제시하지 않은 실패 사례다. Fig. 6의 마지막 패널은 이 거동을 포함한다. [원문 §IV-B-2, Fig. 6, PDF pp. 6–7]

### 10.4 Bricks의 추가 조작

느슨하게 놓은 여러 bricks를 접촉 중인 양끝에서 밀고 회전시켜 함께 모으는 추가 실험도 수행했다. 회전 도중 가운데 brick을 제거하는 외란에도 대응하는 장면을 보고하며, **20회 시험에서 95% 성공률**을 제시한다. 저자들은 학습에서 경험하지 않은 emergent behaviour로 해석한다. [원문 §IV-B-2, PDF p. 6]

이 결과는 별도의 bricks 전용 학습을 완료했다는 뜻이 아니다. 본문에는 brick별 질량·치수·마찰, 각 시험에서의 제거 조건을 모두 나누는 표가 없고, 세부 동작은 보충 영상으로 넘긴다. 이번 정독에서는 그 영상을 확인하지 않았으므로 본문에 보고된 범위만 기록한다.

### 10.5 Bi-gathering의 시험 조건

실물에서는 외란을 포함해 GUM으로 학습한 정책을 사용하며, 물체 쌍마다 10회 시험한다. 무외란에서는 각 물체 쌍의 10회 모두 성공했다고 보고한다. 외란이 있을 때는 임의 시점에 random force를 적용하고 적용 횟수를 변화시킨다. 시뮬레이션의 Table III 상단은 외란 조건에서의 5회 시험에 대한 보고다. [원문 §IV-A-3, §IV-B-3, PDF pp. 5–6]

**Table III — 외란 적용 횟수별 성공률**

| 물체 쌍 | 1회 | 2회 | 3회 | 4회 | 5회 | 6회 |
| --- | --- | --- | --- | --- | --- | --- |
| Cube & Cube (Simulation) | **100%** | **100%** | **100%** | **100%** | **100%** | **100%** |
| Cube & Cube (Real) | **100%** | **100%** | **100%** | **100%** | **90%** | **90%** |
| Apple & Can | **100%** | **100%** | **100%** | **100%** | **90%** | **70%** |
| Mug & Triangular Prism | **100%** | **100%** | **80%** | **70%** | **40%** | **10%** |
| Foam Toy & Spam Can | **100%** | **100%** | **70%** | **50%** | **20%** | **10%** |

[원문 Table III, PDF p. 6 / 인쇄 p. 5477]

실물에서 외란 2회까지는 모든 쌍이 100%지만, 더 많아지면 특히 불규칙 물체 쌍에서 크게 저하된다. 저자들은 perturbation 이후 큰 방향 전환으로 다시 모으려다 로봇이 workspace를 벗어나는 것이 실패 원인이라고 보고한다. 무거운 spam can과 mug에서 더 자주 나타난다고 설명하지만, 이 물체들의 구체 질량 수치는 본문에 없다. [원문 §IV-B-3, PDF pp. 6–7]

### 10.6 Figure 7의 촉각·궤적 해석

Fig. 7은 한 시뮬레이션 쌍과 네 실물 쌍의 초기 구성, 실제·생성 촉각 영상, 무외란·외란 궤적을 함께 보여 준다. 초록색 화살표는 말단 궤적이고, 아래 행의 빨간 화살표는 가한 외란이다. Foam toy의 약한 변형과 mug handle의 다른 접촉 형태를 예시로 제시한다. [원문 Fig. 7, §IV-B-3, PDF p. 7]

그림은 성공 사례 중심의 궤적이므로, Table III의 낮아지는 성공률도 함께 읽어야 한다. 또한 ArUco는 정량 평가용이며 정책 입력에는 visual feedback이 없다고 caption에서 명시한다. 이 조건은 ‘카메라가 실험에 전혀 사용되지 않는다’와 다르다.

## 11. Limitation — 저자들이 밝힌 한계

다음은 정리자의 일반적인 비판을 보탠 것이 아니라, 저자들이 본문·Discussion에서 명시한 한계와 관찰된 실패를 모은 것이다. 미기재 사양·구현 정보는 §13에 따로 둔다.

### 11.1 시뮬레이션에 shear deformation이 없음

가장 명시적인 한계는 **촉각 센서의 shear deformation을 시뮬레이션에서 고려하지 않았다는 것**이다. 저자들은 마찰력을 제어해야 하는 더 복잡한 과업에 이 효과가 필요할 수 있다고 설명한다. 따라서 깊이·접촉 형상의 영상 이전이 성공한 결과를 전단 변형이나 마찰력 제어의 sim-to-real까지 검증한 것으로 확대하면 안 된다. [원문 §V, PDF p. 8]

이는 실물 TacTip에 전단 변형이 물리적으로 발생하지 않는다거나, 모든 실제 영상에서 shear 정보가 완전히 제거된다는 뜻은 아니다. 원문이 제한하는 것은 **시뮬레이션 모델의 고려 범위**다.

### 11.2 원래 정책의 과도한 압착과 안전한 접촉의 이전 문제

Bi-reorienting의 최초 정책은 큰 각도·긴 물체에서 압착을 활용하여 실제 센서 손상 위험을 만들었다. 저자들은 이를 실물 이전의 문제로 명시하고 센서 동역학과 학습 조건을 수정했다. 이는 **해결을 시도한 초기 실패**와 **수정 후 평가 결과**를 나누어 읽어야 하는 항목이다. 수정 후에도 항상 같은 압착 실패가 지속됐다는 주장이나, 수정으로 모든 힘 제한이 보장됐다는 주장 모두 원문에 없다. [원문 §III-C-2, PDF p. 4]

### 11.3 형상·크기에 따른 회전 성능 저하

Cube 형태로 학습하여 round object에서 정확도가 낮아지고, 큰 물체에서는 더 긴 말단 경로와 양팔 협조가 어려워진다고 설명한다. 날카로운 triangular prism은 접촉 불안정과 slip으로 복구 불가능한 상태가 되어 실패했다. 이러한 결과는 미지 물체 일반화가 존재하지만 형상과 접촉 조건에 따라 성능 차이·실패가 남는다는 범위를 보여 준다. [원문 §IV-B-2, PDF p. 6]

### 11.4 반복 외란과 workspace의 한계

Gathering에서 외란을 여러 번 가하면 불규칙 물체 쌍의 성공률이 저하된다. 저자들은 크게 돌아서 물체를 다시 모으려는 운동 중 작업 영역을 벗어나는 실패를 관찰했고, 무거운 물체에서 어려움이 더 컸다고 설명한다. 따라서 시뮬레이션에서 100%였다는 결과를 실물의 모든 외란 횟수·물체 조합에 적용할 수 없다. [원문 §IV-B-3, Table III, PDF pp. 6–7]

### 11.5 TCP 기반 목표를 처음부터 사용한 학습의 실패

실물에서는 물체 중심을 모르므로 TCP로 target line을 만들지만, random policy가 접촉을 유지하지 못하는 초기 학습부터 이를 사용하면 유용한 목표 안내가 되지 않았다. 저자들은 물체 중심에서 시작해 TCP로 바꾸는 curriculum이 성공적인 학습과 이전에 핵심이었다고 명시한다. 즉, **실제 관측 조건의 목표 표현으로 처음부터 학습하는 것과, 해당 조건에서 최종 정책을 실행하는 것은 다르다.** [원문 §III-C-3, PDF pp. 4–5]

## 12. Future Work — 저자들이 제시한 향후 연구

### 12.1 Shear의 신뢰할 수 있는 시뮬레이션 근사

저자들이 명시한 방향은 shear effect를 신뢰할 수 있는 방법으로 시뮬레이션에 근사해 sim-to-real gap을 더 줄이는 것이다. 위의 shear 미고려 한계와 직접 연결된다. 구체적인 근사 모델·학습법·완성된 전단 제어 결과는 제시하지 않는다. [원문 §V, PDF p. 8]

### 12.2 다른 센서·더 많은 로봇 자유도로의 확장

현재는 4-DoF MG400과 TacTip으로 feasibility를 보였지만, Tactile Gym의 기존 확장성을 근거로 GelSight 같은 다른 optical tactile sensor와 더 많은 DoF의 로봇에도 framework가 적용될 수 있다고 기대한다. 이는 **본 논문의 양팔 실험으로 이미 비교 검증한 센서·로봇 조합이 아니라 확장 가능성에 관한 주장**이다. [원문 §V, PDF p. 8]

### 12.3 지지 테이블 없는 held-object 조작과 bi-lifting

또 다른 방향은 지지 테이블 없이 양팔이 지지한 물체를 정밀 조작하는 것이다. 저자들은 이를 보여 주기 위해 **bi-lifting 과업과 reward를 추가 개발하고 시뮬레이션·실물에서 예비 실험을 수행**했다고 보고한다. [원문 §V, PDF p. 8]

본문이 설명하는 reward의 원칙은 **촉각으로 물체를 목표 상태에 도달시키면서 안정된 접촉을 유지**하는 것이다. 그러나 정확한 reward 식·weight·lifting 성공률·물체 조건 표는 이 PDF에 없다. 결과는 보충 영상에 포함했다고 안내한다. 따라서 bi-lifting은 ‘전혀 수행하지 않은 미래 계획’으로만 쓰지도 않고, 본문 세 과업과 같은 수준의 정량 검증이 끝난 네 번째 benchmark로 쓰지도 않는다. **향후 확장 방향에 대한 예비 실험 보고**로 구분한다.

## 13. 미명시 사항과 원문 해석상의 주의

### 13.1 재현에 필요한 정보의 제공 범위

| 분야 | 이 논문에서 확인 가능한 것 | 본문에 없는 핵심 세부 |
| --- | --- | --- |
| RL 알고리즘 | PPO, Stable-Baselines3 | 버전·network·optimizer 설정·learning rate·rollout·batch·epoch·gamma·GAE·clip·entropy·seed |
| 과업 reward | **식 (1)–(4)**, 각 항의 목적, cosine distance 정의 | **모든 weight의 수치**, 단위 scaling·normalization, 추가 과압착 penalty의 완전한 식 |
| Observation | 두 촉각 영상의 결합, 고유감각·goal | 전체 scalar 목록·차원, history, image shape·stacking 축, critic 입력과 encoder 구현 |
| Action | 과업별 축과 **4/6/4차원**, 각자의 TCP frame | scaling·한계·주기·absolute/increment 구분, 비선택 축의 움직임·하위 제어 방식 |
| 학습 환경 | 양팔 배치, 일부 물체 크기·초기 위치·목표 범위, 외란 | physics timestep·solver·마찰·물체 질량·TCP reset·초기 접촉 조건의 완전한 명세 |
| GAN | Paired image collection, 5,000/2,000 samples, depth·angle 범위, Pix2Pix와 [7] 참조 | Loss와 계수, optimizer·학습률·epoch·batch, 세부 layers·전처리·augmentation, 센서별 weight 관리 |
| Contact-depth 제어 | Desired contact point penalty, 큰 깊이의 penalty 강화 | 기준점 생성식·offset, depth threshold, maximum force·피부 파손 한계 |
| 센서 동역학 조정 | **Stiffness 증가·damping 감소**, 가장 기여했다고 보고 | 전후 계수·단위, 실제 피부 파라미터 identification, 정량 ablation 수치 |
| Curriculum | 회전 각도 10분할, gathering의 object-centre→TCP 전환, 외란 증가 | 단계별 학습량·전환 기준·큰 각도의 최종 확률분포·외란 schedule |
| GUM | n=10, h=75와 비교 후보, nearest subgoal 개념 | Target line 끝점·후보 생성의 완전한 식, tie-break·subgoal 도달 처리·각도 convention |
| 종료·평가 | Gathering sim 90 mm/real 70 mm, real 300 steps, reorienting 10 steps 각도 안정 | 모든 과업의 timeout·실패 조건·센서-only 완료 판단, 정확한 실물 반복 구조 일부 |
| 하드웨어 | MG400 2대·각 4 DoF, 테이블 120 mm·베이스 간격 700 mm | 가반하중·reach·정밀도 수치, TacTip pin 수·영상 해상도·fps·힘 range·resolution |

이 표의 ‘미명시’는 실제 구현에 해당 항목이 없다는 뜻이 아니라, **첨부 논문 본문만으로 확인되지 않는다는 뜻**이다. 이전 연구 [7], 하드웨어 관련 [8], [20]–[22], 공개 코드·보충자료가 상세정보의 다음 출처가 될 수 있지만, 이번 정독에서 확인한 사실과 섞지 않았다.

### 13.2 논문에 없는 loss나 controller를 추가하지 않기

PPO의 일반적인 objective나 Pix2Pix의 흔한 adversarial·L1 loss를 알고 있더라도, 본 논문이 해당 loss와 수치를 그대로 썼다고 확정할 수 없다. 이 정리는 원문에 있는 과업 reward와 관측·학습 절차를 설명하며, 누락된 training recipe를 일반 지식으로 재구성한 별도 재현안을 제공하지 않는다.

특히 **reward의 접촉 위치 penalty와 실시간 힘 제어 law**, **GAN 입력 pose label과 runtime pose estimator 출력**, **GUM의 geometry-based goal generation과 학습된 고수준 planner**를 서로 치환하지 않는다. [원문 §III–IV의 방법 구성, PDF pp. 2–6]

### 13.3 원문 내부 표기와 조건의 차이

| 항목 | 원문에서 확인한 주의사항 | 이 정리의 처리 |
| --- | --- | --- |
| 식 (1)–(4)의 거리 | 위치 차이의 2-norm | 제곱거리로 바꾸지 않음 |
| 식 (2)의 normal 방향 | $(-1)^i(\pi/2+\theta_t^o)$ 표기 | 좌표 convention을 추정하여 다른 부호식으로 수정하지 않음 |
| 식 (4)의 합 | 대문자 N을 사용하지만 별도 정의가 없음 | 두 물체 문맥을 설명하고 소문자 n=10과 구분 |
| 식 (4)의 $\theta_t^c$ | 직후 정의 문장이 각도 설명을 완결하지 못함 | 마지막 항의 target-line direction 설명과 Fig. 2에 근거한 해석임을 명시 |
| Gathering의 ‘sparse goal’ | 저자들의 표현이나 식 (3)은 이미 연속 penalty를 포함 | Sparse binary reward였다고 재정의하지 않음 |
| Reorienting 목표 분포 | §IV-A-2의 균일 sampling과 §III-C-2의 큰 각도 확률 증가가 함께 있음 | 두 설명과 최종 분포 미명시를 함께 보존 |
| Reorienting 1° 조건 | 마지막 subgoal에서 10 steps 동안의 각도 변화 | 목표 각도 오차 1° 이하로 바꾸지 않음 |
| Gathering 거리 기준 | Simulation 90 mm, real 70 mm | 동일 threshold의 실험으로 합치지 않음 |
| Fig. 4(b) caption | 물체 목록 끝을 bi-gathering으로 적으나 패널·본문은 bi-reorienting | 본문 §IV-B-2·패널 제목과 대조해 구분 |
| Fig. 6 패널 문자 | Caption은 마지막 prism을 (j), 실제 패널은 (f) | 실제 패널과 함께 위치를 안내 |
| Fig. 7 패널 문자 | 본문·caption의 일부 문자와 실제 5개 패널 표시가 불일치 | Simulation→cubes→apple/can→mug/prism→foam/spam 순서로 식별 |
| Fig. 3 학습 축 | Caption·그림은 Episodes와 Episode Steps, 본문은 학습 진행을 time step으로도 표현 | Epoch·환경 transition 총수·실행 초로 임의 환산하지 않음 |

[원문 Fig. 2–7, 식 (1)–(4), §III-C–IV-B, PDF pp. 3–7]

### 13.4 검증의 범위

이번 작업은 첨부 출판본에 대한 정독·설명이다. 저자 코드 실행, PPO 재학습, GAN 학습 재현, 센서 계측, 보충 영상 분석을 수행하지 않았다. 따라서 원문에 보고된 ablation·성공률을 별도로 재현한 성과처럼 표현하지 않으며, 정리본의 수식 렌더링 검사는 알고리즘의 정확성·재현성 검증과 구분한다.

## 14. 원문을 다시 확인할 때의 위치 안내

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 양팔 촉각 조작의 동기와 세 기여 | §I, PDF pp. 1–2 / 인쇄 pp. 5472–5473 |
| RL·촉각 기반 양팔 선행연구 | §II-A–B, PDF p. 2 |
| MG400 2대, 테이블·베이스 거리, 센서 원리 | §III-A, Fig. 1, PDF p. 2 |
| 관측 결합과 세 단계 sim-to-real | §III-B, Fig. 1, PDF pp. 2–3 |
| GAN 데이터·수집 범위·이전 연구 설정 참조 | §III-B, PDF p. 3 |
| 세 과업의 action 축·차원·TCP frame | §III-C 시작, PDF p. 3 |
| Bi-pushing reward와 normality | §III-C-1, 식 (1), Fig. 2(a), PDF p. 3 |
| Bi-reorienting reward·contact-depth 개념 | §III-C-2, 식 (2), Fig. 2(b), PDF pp. 3–4 |
| 압착 실패와 네 가지 학습 수정 | §III-C-2, PDF p. 4 |
| Bi-gathering 기본 reward | §III-C-3, 식 (3), Fig. 2(c), PDF p. 4 |
| GUM과 auxiliary reward | §III-C-3, 식 (4), PDF p. 4 |
| 물체 중심→TCP curriculum | §III-C-3, PDF pp. 4–5 |
| PPO, 과업별 초기·목표 분포, n·h·외란 범위 | §IV-A, PDF p. 5 |
| 학습 곡선 및 Table I–II | Fig. 3, Table I–II, PDF p. 5 |
| 물체별 외란 성공률 | Table III, PDF p. 6 |
| 큰 물체 pushing과 질량·마찰 해석 | §IV-B-1, Fig. 4–5, PDF pp. 5–6 |
| 실제 회전 종료 기준·모서리 실패·bricks | §IV-B-2, Fig. 6, PDF pp. 6–7 |
| 실제 gathering 종료·약한 변형·workspace 실패 | §IV-B-3, Fig. 7, PDF pp. 6–7 |
| GUM의 implicit curriculum 해석, shear 한계, 향후 확장·lifting | §V, PDF pp. 7–8 |
| 인용한 방법·플랫폼의 서지 | References [1]–[28], PDF p. 8 |

## 15. 핵심 메커니즘 요약

Bi-Touch는 **양쪽의 변형 영상을 시뮬레이션 관측으로 바꾸고, 이를 함께 받는 PPO에 접촉 기하와 과업 목표를 반영한 reward를 제공하여 양팔 운동을 학습**한다. Bi-reorienting에서는 시뮬레이션 센서 응답과 학습 조건을 수정해 압착 전략의 실물 이전 문제를 다루며, bi-gathering에서는 움직이는 목표를 주기적으로 갱신하는 subgoal로 분해하고 물체 중심→TCP curriculum으로 실제 정보 조건에 맞춘다. [원문 §III–IV, PDF pp. 2–7]

따라서 논문의 힘·접촉 활용은 **명시적인 wrench 추정·제어**보다 **촉각 영상 표현, 접촉-depth·normality 기반 reward, 센서 동역학의 학습 영향, 정보원 전환 curriculum**에서 구체화된다. 저자들은 여러 미지 물체와 외란에서의 일반화를 보이지만, 날카로운 접촉의 slip, 반복 외란에 따른 workspace 한계, shear 미모델링을 남긴다. 지지면 없는 lifting은 향후 방향을 뒷받침하는 예비 실험으로 구분해야 한다. [원문 §III-C, §IV-B, §V, PDF pp. 4–8]
