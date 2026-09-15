# Tactile Gym 2.0 — 원문 상세 정리

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Tactile Gym 2.0: Sim-to-Real Deep Reinforcement Learning for Comparing Low-Cost High-Resolution Robot Touch** |
| 저자 | Yijiong Lin, John Lloyd, Alex Church, Nathan F. Lepora |
| 출판 | IEEE Robotics and Automation Letters, 7(4), 10754–10761, October 2022 |
| DOI | [10.1109/LRA.2022.3195195](https://doi.org/10.1109/LRA.2022.3195195) |
| 기존 조사본 식별자 | [2026-09-14 문헌조사](../reviews/2026-09-14_blind-sweep-force-torque-tactile.md)의 **R5** |
| 정리일 | 2026-09-15 |
| 확인한 원문 | 제공된 출판본 PDF 8쪽 전체. 본문 §I–V, Fig. 1–7, Table I–VII, 본문의 궤적 수식, References [1]–[34] |
| 확인하지 않은 자료 | 인용된 선행논문의 개별 원문, 본문이 언급한 동반 하드웨어 논문, 저자 코드·설정·데이터·체크포인트, 보충 영상, 제조사 데이터시트 |
| 원문 PDF SHA-256 | `e2d99c8f078d3c46b3f3032a2fc5c1c2bb319804de050bfa13cb62fccad0761b` |

[개별 논문 색인](README.md) · [문헌조사 자료](../README.md)

이 문서는 해당 논문 자체의 문제 상황, Related Work, 환경·센서, 촉각 처리·학습 방법, 실험, 저자들이 밝힌 Limitation과 Future Work를 정리한다. 다른 연구 주제에 대한 적용안은 포함하지 않는다. `[원문 §…, PDF p.…]`는 첨부 출판본의 위치이며, **PDF 1–8쪽은 인쇄 페이지 10754–10761**에 대응한다. `[1]` 등의 번호는 원문의 참고문헌 번호다. 표와 그림은 PDF의 실제 표시를 확인했으며, 계산 과정의 재구성은 원문 설명과 구분한다.

**핵심:** 이 논문의 중심은 새로운 힘 제어기나 pushing 전용 상태 추정기의 개발이 아니라, **서로 다른 광학식 촉각 센서를 같은 sim-to-real 방법론과 저가 로봇 플랫폼에서 비교하는 것**이다. 실제 접촉으로 생긴 영상을 센서별 시뮬레이션 depth-image 표현으로 변환하고, 그 표현으로 학습한 PPO 정책을 실행한다. Pushing은 edge-following·surface-following과 함께 이 플랫폼을 평가하는 세 과업 중 하나다. [원문 Abstract, §I, §III-B–F, PDF pp. 1–5]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 상황·기여와 관련 연구의 비교 구도 |
| 3 | 로봇·센서 상세 사양, 실험 환경과 정보의 역할 |
| 4 | 접촉 시뮬레이션, GAN 영상 변환, 데이터 수집 |
| 5 | PPO와 세 과업의 관측·행동·평가 정의 |
| 6 | 힘·변형·영상·행동의 연결과 실패를 설명하는 증거 |
| 7 | 시뮬레이션·영상 변환·실물 실험의 정량 결과 |
| 8 | Limitation — 저자들이 밝힌 한계 |
| 9 | Future Work — 저자들이 제시한 향후 방향 |
| 10–12 | 미명시 사항·표기 주의, 원문 위치 안내, 핵심 요약 |

## 1. 제시하는 문제 상황

### 1.1 촉각 RL의 접근성과 센서별 연구 분리

저자들은 고해상도 촉각과 deep RL의 결합이 정교한 물리적 상호작용을 학습하는 유망한 방법이라고 본다. 그러나 촉각 로봇의 높은 비용, 전문적인 센서 제작·시뮬레이션 기술, 센서 종류가 바뀌었을 때의 이전 문제 때문에 연구 진입 장벽이 높다고 지적한다. [원문 Abstract, §I, PDF p. 1]

Introduction은 이 장벽을 세 가지로 설명한다. 접근 가능한 촉각 기술이 충분하지 않고, 센서를 제작할 수 있는 연구실도 익숙한 기술에 머무르며, 그 결과 촉각 RL 방법이 특정 연구실·플랫폼 안에 갇히기 쉽다는 것이다. 따라서 문제의 출발점은 단순히 ‘물체를 잘 밀지 못한다’가 아니라, **다른 센서와 저렴한 로봇에서도 재사용·비교할 수 있는 연구 기반이 부족하다**는 데 있다. [원문 §I, PDF p. 1]

### 1.2 TacTip에서의 성공을 GelSight 계열까지 검증할 필요

기존 Tactile Gym 연구 [1]은 시뮬레이션 촉각 영상으로 학습한 정책에 real-to-sim 영상 변환을 결합하여 여러 실물 조작을 보였다. 그러나 다른 고해상도 촉각 센서에도 적용 가능하다는 주장은 TacTip에서만 실험적으로 확인되어 있었다. [원문 §I, §III-B, PDF pp. 1, 3]

본 논문은 **marker-based TacTip 계열과 image-shading-based GelSight 계열**을 같은 프레임워크 안에 넣는다. 구체적인 비교 대상은 소형화한 TacTip, DIGIT, 그리고 DIGIT의 하우징·카메라·조명을 사용하면서 TacTip 계열 피부를 결합한 DigiTac이다. 센서 간에는 영상의 외형뿐 아니라 피부 형상·강성·접촉 거동도 다르므로, 단순한 입력 영상 형식 변경만으로 동등한 조작을 기대할 수는 없다는 점이 실험에서 드러난다. [원문 §I, §III-A–D, §IV-C, PDF pp. 1–7]

### 1.3 로봇 비용을 낮추되 과업도 실제 자유도에 맞게 변경

기존 6축 UR5 기반 환경을 그대로 실행하는 대신, 4축 Dobot MG400에 맞게 과업과 데이터 수집을 수정한다. 특히 roll·pitch를 사용할 수 없으므로 센서 장착 방향을 바꾸고, yaw로 표면 법선 방향을 맞출 수 있는 형태의 surface-following을 사용한다. 이는 저가 로봇으로 기존 6축 로봇의 모든 운동 능력을 복제했다는 주장이 아니다. [원문 §III-A–B, PDF p. 3]

### 1.4 저자들이 명시한 기여와 실제 평가 범위

| 원문의 기여 | 실제로 확인하는 내용 |
| --- | --- |
| Tactile Gym의 센서 범위 확장 | DIGIT와 TacTip 계열을 같은 플랫폼에 통합하고 각각의 촉각 관측을 사용 |
| Sim-to-real 조건의 센서 실증 비교 | Edge-following, surface-following, object-pushing의 학습·실물 성능과 실패 차이 |
| 접근성 향상 | 저렴한 4자유도 데스크톱 로봇에 과업을 맞추고 하드웨어·소프트웨어 공개를 안내 |

[원문 §I의 기여, PDF pp. 1–2]

**‘하나의 sim-to-real 접근’은 동일한 방법론을 적용한다는 뜻이다.** 본문은 센서별 관측 공간, 데이터, 영상 전처리·하이퍼파라미터 조정과 학습 정책을 설명한다. 한 개의 고정된 GAN·정책 가중치를 세 센서에 무조건 교체 적용하는 실험으로 바꾸어 읽지 않는다. [원문 §III-C–E, §IV-A, PDF pp. 3–5]

## 2. Related Work — 원문의 조직과 비교 구도

독립된 **§II. Related Work**는 `Deep Reinforcement Learning in Tactile Robotics`와 `Tactile Sim-to-Real Transfer`로 나뉜다. 아래는 이 논문이 소개한 선행연구의 역할을 정리한 것이며, 각 인용 논문을 별도로 검증한 결과는 아니다.

### 2.1 촉각과 deep RL을 결합한 연구

| 원문 인용 | 저자들이 소개한 내용 | 이 논문에서의 위치 |
| --- | --- | --- |
| [10] van Hoof 등 | 저해상도 촉각 등을 이용한 object stabilisation | 촉각 RL의 선행 사례 |
| [11] Veiga 등 | 촉각 기반 forward predictive model | 접촉 위치 제어와 예측의 배경 |
| [12] Tian 등 | GelSight 계열 촉각으로 물체를 재배치하는 deep tactile model-predictive RL | 고해상도 촉각을 이용한 학습 조작 |
| [3] Dong 등, [13] TD3 | 촉각 영상 시퀀스로 실제 환경에서 일반화 가능한 insertion policy 학습 | 실물 촉각 RL의 사례 |
| [14] Kim·Rodriguez | Extrinsic contact line 모델을 통한 접촉 위치 표현과 시뮬레이션 학습 | 원시 영상·고유감각 관측의 단순화 사례 |
| [1] Church 등 | Tactile Gym과 real-to-sim 영상 변환으로 실물 pushing·rolling 등 수행 | 본 논문이 직접 확장하는 방법 |
| [15], [4] | TacTip의 braille keyboard 입력, DIGIT의 piano 연주 학습 | 촉각 RL의 다양한 응용 |

[원문 §II-1, References, PDF pp. 2, 8]

이 논문은 TD3·model-predictive RL을 자체 실험의 대안 알고리즘으로 비교하지 않는다. 이들은 Related Work에 등장하며, **본 실험의 정책 학습은 PPO**다. [원문 §II-1, §IV-A, PDF pp. 2, 5]

### 2.2 Sim-to-real gap을 줄이는 두 계열

원문은 센서 변형 동역학을 **유한요소법(FE)**으로 모델링하는 방향 [16]–[21]과, 촉각 데이터를 **영상 렌더링**으로 재현하는 방향 [1], [5], [22], [23]을 구분한다. 본 논문은 후자의 depth-image rendering과 image translation을 따른다. 피부 변형의 정밀 FE 해석을 정책 실행 중 풀어내는 구조가 아니다. [원문 §II-2, §III-C–D, PDF pp. 2–4]

Introduction의 TACTO [5]·PyTouch [6]는 GelSight 계열의 공개 연구 도구로, TacTip·Tactile Gym은 다른 주요 연구 흐름으로 소개된다. 이 논문이 실제 확장하는 플랫폼은 Tactile Gym이며, TACTO나 PyTouch를 새 시스템의 필수 실행 구성요소로 사용했다고 본문이 밝히지는 않는다. [원문 §I–III, PDF pp. 1–4]

### 2.3 센서 구조 비교와 알고리즘 우열 비교의 차이

본 논문의 비교는 같은 PPO 기반 절차를 여러 센서에서 실행해 보는 **센서·플랫폼 실증 비교**다. 저자들은 결과의 차이를 주로 피부의 물리적 구조와 재료 특성으로 설명한다. 이를 GelSight 원리 전체와 TacTip 원리 전체의 보편적인 우열을 확정한 결과로 확대하지 않는다. [원문 §IV-C, §V, PDF pp. 6–8]

## 3. 환경과 로봇·센서 상세 사양

### 3.1 Dobot MG400 플랫폼

| 항목 | 원문에 명시된 내용 | 해석상 주의 |
| --- | --- | --- |
| 모델 | **Dobot MG400** | 데스크톱 robot arm |
| 자유도 | **4축 / 4 DoF** | 말단 x·y·z 위치와 z축 회전만 구동 |
| 베이스·제어부 footprint | **190 × 190 mm** | 전체 작업 영역의 가로·세로가 아님 |
| 가반하중 | **750 g / 0.75 kg** | 밀 수 있는 물체의 최대 질량과 구분 |
| 최대 reach | **440 mm** | 실험 궤적 길이와 구분 |
| 반복정밀도 | **±0.05 mm** | §III-A-1의 repeatability. Table I는 Accuracy (mm) 행에 0.05로 표기 |
| 로봇 무게 | **8 kg** | Table I의 Weight |
| 로봇 가격 | **2.7k 달러** | 2022년 논문 Table I의 비교값. 현재 가격이나 전체 센서 시스템 비용이 아님 |
| 말단 장비 | TacTip, DIGIT, DigiTac 중 해당 실험 센서를 장착 | 세 센서의 동시 융합이 아님 |
| Surface-following용 장착 | Custom 3D-printed flange로 센서를 말단에 수직 장착 | 사용 가능한 yaw를 표면 방향 정렬에 활용 |
| 제어·통신 주기, 최대 속도·가속도 | 미명시 | 로봇 모델명에서 값을 추정하지 않음 |
| 관절 범위·명령 보간·역기구학 구현 | 미명시 | Task action과 실제 관절 명령의 변환 세부 미제시 |

[원문 §III-A–B, Table I, Fig. 1, PDF pp. 2–3]

본문의 repeatability와 표의 Accuracy라는 이름을 그대로 구분했다. 0.05 mm를 절대 위치 정확도, 접촉 위치 추정 오차, 촉각 분해능으로 바꾸어 서술하지 않는다.

### 3.2 Table I의 비교 대상

| 항목 | 기존 [1] | 기존 [21] | 기존 [23] | 본 연구 |
| --- | --- | --- | --- | --- |
| 로봇 | UR5 | Sawyer | UR5 | MG400 |
| Accuracy (mm), 표의 이름 | 0.1 | 0.1 | 0.1 | 0.05 |
| Price (달러), 당시 표기 | 45k | 26k | 45k | 2.7k |
| Max. Reach (mm) | 850 | 1260 | 850 | 440 |
| Payload (kg) | 5 | 4 | 5 | 0.75 |
| Weight (kg) | 18.4 | 19 | 18.4 | 8 |
| DoF | 6 | 7 | 6 | 4 |
| 통합 센서 | TacTip | TacTip | DIGIT | TacTip·DIGIT·DigiTac |

[원문 Table I, PDF p. 3 / 인쇄 p. 10756]

위 값은 이 논문이 제시한 당시 플랫폼 비교를 옮긴 것이다. 다른 로봇의 제조사 사양을 이번에 독립적으로 확인한 결과가 아니며, 해당 플랫폼에 표시되지 않은 센서를 원천적으로 사용할 수 없다는 뜻도 아니다.

### 3.3 세 센서의 원리와 물리적 차이

| 구분 | TacTip | DIGIT | DigiTac |
| --- | --- | --- | --- |
| 계열 | TacTip-style | GelSight-style | TacTip-style |
| 영상에 나타나는 주된 신호 | Marker-tipped pin의 움직임 | 접촉 변형에 따른 image shading | Marker 기반 피부 변형 |
| 피부·형상 | 부드럽고 곡면인 3D-printed skin | 비교 대상 중 더 평평하고 상대적으로 뻣뻣한 elastomer | TacTip 계열의 부드러운 생체모방 피부 |
| 구성 특징 | 기존 [1]보다 compact한 버전 | 소형·저가, 로봇 손에 통합 가능한 크기로 소개 | DIGIT housing·camera·lighting에 맞춘 TacTip skin |
| 영상 차이 | Marker 크기·밀도·카메라 시점 등이 기존 버전과 다름 | 음영 변화가 marker보다 미묘해 전처리 조정이 어려움 | DIGIT와 동일한 영상 dimension이라고 설명하지만 수치는 없음 |
| 접촉·운동에서 드러난 특성 | 더 큰 접촉면이 pushing 안정성에 유리하다고 저자들이 해석 | 약한 변형·오목한 면·마찰 증가에서 문제가 발생 | 부드러운 돔형 피부로 오목한 면 추종 가능 |

[원문 §III-A–D, Fig. 1–2, §IV-C, PDF pp. 2–7]

TacTip 내부 pin은 접촉으로 인한 표면 변형을 증폭하여 marker movement로 보여 준다. DIGIT는 GelSight와 같은 영상 음영 기반 원리로 소개된다. DigiTac은 DIGIT와 TacTip의 데이터를 합치는 센서 융합기가 아니라, **구조를 결합한 하나의 광학식 촉각 센서**다. [원문 §III-A-2, PDF p. 3]

### 3.4 센서 성능 사양: 명시된 것과 없는 것

| 사양 항목 | 이번 원문에서 확인한 범위 |
| --- | --- |
| Tip 크기 | Pushing 결과 설명에 **20–40 mm** 범위를 제시. 각 센서의 개별 치수·직경 대응은 수치로 나열하지 않음 |
| 영상 크기 | DigiTac과 DIGIT의 영상 dimension이 같다고 설명. 실제 픽셀 수·채널 수·모델 입력 해상도는 미명시 |
| Pin/marker 수·간격·밀도 | 차이가 있다는 설명은 있으나 수치는 미명시 |
| 공간 해상도·접촉 위치 분해능 | 정량 수치 미명시 |
| 최대 힘·압력·모멘트 측정 범위 | 미명시 |
| 힘 분해능·최소 검출 힘·감도 | 미명시 |
| 힘 측정 정확도·선형성·히스테리시스 | 미명시 |
| 촉각 카메라 frame rate·측정 대역폭 | 미명시 |
| 피부 강성·탄성률·경도·두께 | 상대적으로 soft/stiff하다는 설명만 있으며 정량 수치는 미명시 |
| 센서별 가격·무게 | 이 논문에 수치 미명시 |
| 별도 F/T 센서 | 제시된 시스템·정책 입력에 별도 F/T 센서가 나타나지 않음 |
| 뉴턴 단위 force 또는 wrench 출력 | 이 방법의 중간 상태·제어 입력으로 제시되지 않음 |

[원문 §III-A–E, §IV-C-1, PDF pp. 3–6]

원문은 하드웨어·센서 작동의 상세 설명을 동반 논문으로 넘기고 여기서는 주요 사항만 요약한다고 밝힌다. 따라서 다른 TacTip 연구의 pin 수·영상 해상도를 가져오지 않았다. **SSIM, 데이터 수집의 접촉 깊이 범위, 실물 추종 오차는 각각 다른 지표이며 센서 자체의 해상도·측정 범위가 아니다.** [원문 §III-A, Table II–III, PDF pp. 3–5]

### 3.5 과업 물체와 평가용 정보

| 용도 | 원문 구성 | 명시된 수치·범위 |
| --- | --- | --- |
| Pushing | Cube, cylinder, triangular prism | 기본 물체 질량 범위 **185–363 g**. Triangular prism은 **185 g**으로 별도 명시 |
| Pushing 추가 실험 | DIGIT, 분동을 더한 물체 | 전체 물체 +150 g 비교 및 prism에 +50·100·150·200 g 시험 |
| Edge-following | Square, clover leaf, teardrop | CAD boundary를 정답으로 사용. Table VI의 세 번째 열은 **Foil**로 표기 |
| Surface-following | Arch, flower, disc/circle | 수직 옆면의 closed-loop 2D contour를 추종 |
| 영상 변환 데이터 수집 | 3D-printed stimulus의 직선 edge와 평면 surface | 센서에 대한 상대 pose로 label 부여 |
| Pushing 평가 | 물체 위의 ArUco marker로 실제 궤적 추적 | 카메라·보정 정확도·샘플링률 미명시 |
| Edge/surface 평가 | CAD 모델을 Blender에 가져와 경계 point cloud 추출 | 점 간격·궤적 대응 알고리즘의 세부 미명시 |

[원문 §III-E–F, Fig. 3, §IV-C, PDF pp. 4–7]

**ArUco는 물체 이동을 평가하기 위한 외부 측정으로 설명된다.** 이를 정책이 실행 중 사용하는 물체 pose 입력으로 적지 않는다. 반대로 정책의 전체 observation vector가 본문에 없으므로, 촉각 외의 고유감각·목표 정보까지 모두 없다고 단정하지도 않는다. [원문 Fig. 1, §III-F, PDF pp. 2, 5]

## 4. 상세 핵심 메소드: 시뮬레이션과 영상 변환

### 4.1 세 단계의 학습·실행 절차

| 단계 | 입력·수행 내용 | 산출물과 역할 |
| --- | --- | --- |
| 1. 시뮬레이션에서 online RL | 가상 센서의 tactile image로 각 과업 수행·학습 | 시뮬레이션 관측을 받는 정책 |
| 2. Domain adaptation | 실제·가상 접촉 영상과 대응 접촉 pose로 영상 변환 학습 | 실제 영상을 가상 센서 영상으로 바꾸는 모델 |
| 3. Zero-shot sim-to-real | 실제 촉각 영상에 변환 모델을 적용하고 학습된 정책 실행 | 실제 로봇 조작. 이전 후 정책 추가 학습·튜닝 없이 평가 |

[원문 §III-B, Fig. 1, PDF pp. 2–3]

여기서 **online learning은 첫 단계의 시뮬레이션 상호작용 학습**이다. 실제 조작 중 새 데이터로 PPO를 계속 재학습한다는 뜻이 아니다. 또한 zero-shot은 실제 촉각 데이터 없이 개발했다는 뜻이 아니라, 실제 데이터를 포함해 영상 변환 모델을 준비한 뒤 정책을 추가 튜닝하지 않고 실물에서 사용한다는 의미다. [원문 §III-B, §III-D–E, §IV-A, PDF pp. 3–5]

### 4.2 가상 센서: CAD 접촉 형상과 depth image

Tactile Gym은 **rigid-body physics로 접촉 동역학을 처리**하고, 센서 CAD 모델에 대해 depth image를 렌더링한다. 가상 센서 내부의 synthetic camera가 해당 영상을 얻는다. 실제 marker의 색·조명·음영을 모두 정밀하게 그대로 복원한 영상을 정책에 주는 방법은 아니다. [원문 §III-C, Fig. 2, PDF pp. 3–4]

저자들은 DIGIT·DigiTac의 CAD와 소형 TacTip 형상을 가상 센서에 반영하고, 센서마다 **마찰·강성·감쇠 등의 skin physics와 camera parameters**를 조정한다. 이 조정은 형상과 접촉 거동이 다른 센서를 학습 환경에서 구분하기 위한 것이다. 다만 계수·단위·카메라 파라미터값은 이 논문에 제시하지 않는다. [원문 §III-B–C, PDF pp. 3–4]

Fig. 2는 각 센서의 실물, 가상 접촉 기하, 실제 edge 접촉 영상, 시뮬레이션 관측에 대응하는 생성 depth image를 나란히 보여 준다. TacTip 계열의 marker와 DIGIT의 음영은 외관상 크게 다르지만, 정책에 전달하기 전에는 **각 가상 센서가 제공하는 접촉 depth-image 표현**으로 옮겨진다. 세 센서의 CAD·시점이 다르므로 최종 영상까지 완전히 같다는 뜻은 아니다. [원문 Fig. 2, PDF p. 4]

### 4.3 실제 영상에서 시뮬레이션 영상으로: GAN

영상 변환은 **real-to-sim 방향**이다. 실제 센서 영상을 입력으로 받아 시뮬레이션에서 정책이 보았던 종류의 영상으로 변환한다. Generator에는 **U-net**, discriminator에는 **batch normalization이 포함된 일반 convolutional network**를 사용한다. 원문 [26]의 image-to-image translation과 [27]의 U-net을 참조한다. [원문 §III-D, Fig. 1(b), PDF pp. 2, 4]

Generator의 역할은 관측 변환이고 PPO의 역할은 행동 결정이다. Discriminator는 영상 변환 학습에 등장하며, Fig. 1(d)의 실제 정책 실행 경로는 **실제 촉각 영상 → generator → RL policy → robot**로 나타난다. Discriminator가 접촉 성공·위험도를 판정하여 로봇을 제어하는 구조로 설명하지 않는다. [원문 Fig. 1, PDF p. 2]

### 4.4 센서별 전처리·보정은 필요하다

TacTip·DigiTac의 marker는 빛을 더 분명하게 반사하는 반면 DIGIT의 음영 변화는 미묘하여, 후자의 영상 처리 fine-tuning이 상대적으로 어렵다고 설명한다. 각 센서의 설계·조명이 다르므로 **image preprocessing과 관련 하이퍼파라미터를 조정**해야 한다. Discussion에서는 가상 센서 내부 camera를 보정하여 실제·가상 데이터 분포를 잘 맞췄다고 다시 강조한다. [원문 §III-D, §V, PDF pp. 4, 7]

그러나 crop·resize·threshold·normalization의 실제 연산 순서, 이미지 크기, U-net 채널 수, GAN loss와 weight, 학습률·batch size는 본문에 재기재되어 있지 않다. Fig. 2의 회색·이진처럼 보이는 예시만으로 특정 전처리 알고리즘을 확정하지 않는다. [원문 §III-C–E의 확인 범위, PDF pp. 3–4]

**정책 학습 하이퍼파라미터를 센서마다 fine-tune할 필요는 없었다는 §IV-A의 진술과, 영상 변환 전처리·하이퍼파라미터를 센서마다 조정했다는 §III-D의 진술은 대상이 다르다.** 이를 ‘센서가 달라도 아무 설정 변경이 필요 없다’로 합치면 안 된다.

### 4.5 Contact feature별 데이터와 모델

세 과업에는 두 종류의 접촉 특징을 사용한다. **Edge 데이터는 edge-following**, **surface 데이터는 surface-following과 object-pushing**에 대응한다. 센서 3개와 feature 2개를 조합하고 각각 train·validation을 수집하여 **총 12개 데이터셋**을 구성한다. 센서·feature 조합은 6개이며, ‘12개 센서’나 ‘12개 RL 과업’이라는 뜻이 아니다. [원문 §III-E, PDF p. 4]

각 training dataset에는 **5,000개**, validation dataset에는 **2,000개**의 촉각 영상이 있다. 직선 edge 또는 평면 surface에 센서를 무작위 상대 pose로 접촉시키고, 영상과 접촉 중 sensor–stimulus relative pose를 기록한다. Fig. 1(b)는 실제·시뮬레이션의 대응 접촉 영상을 사용한 학습을 보여 준다. [원문 §III-E, Fig. 1(b), PDF pp. 2, 4]

원문은 데이터 수집에 **실물 약 6시간, 시뮬레이션 1분 미만**이 걸린다고 설명한다. 이 문장의 시간 집계 단위가 개별 feature·sensor 묶음인지 전체 12개인지 세분되어 있지는 않으므로, 임의로 곱하여 총 시간이나 센서 fps를 계산하지 않는다. [원문 §III-E, PDF p. 4]

### 4.6 Table II: 상대 접촉 pose의 수집 범위

아래 축은 **training feature에 고정된 좌표계에 대한 sensor pose**다. $R_z$는 z축 주위 axial rotation을 뜻한다. 원문 표의 기호와 범위를 유지했다.

| 센서 | Edge: y (mm) | Edge: z (mm) | Edge: $R_z$ (deg) | Surface: x (mm) | Surface: $R_z$ (deg) |
| --- | --- | --- | --- | --- | --- |
| TacTip | [−6, 6] | [2, 5] | [−179, 180] | [1, 4] | [−15, 15] |
| DigiTac | [−5, 5] | [2, 4] | [−179, 180] | [1, 3] | [−15, 15] |
| DIGIT | [−5, 5] | [2, 3] | [−179, 180] | [1, 2] | [−11, 11] |

[원문 Table II, PDF p. 4 / 인쇄 p. 10757]

이 값은 **영상 변환 학습용 접촉 pose sampling 범위**다. 센서의 최대 물리적 변형·측정 범위, 힘의 포화값, 실제 policy action 범위로 대체하지 않는다. 특히 edge의 y·z와 surface의 x는 장착·feature frame이 다른 조건의 변수다.

### 4.7 비대칭 센서의 회전각 의존 수집 범위

DIGIT와 DigiTac은 한 축으로 더 넓어서 원래 TacTip과 같은 대칭성이 없다. 따라서 회전각에 따라 x·y 수집 범위를 맞추고, **edge에 직교하는 y 범위를 해당 각도의 tangent로 scaling**했다고 원문이 설명한다. [원문 §III-E, PDF p. 4]

Scaling의 구체식·부호·각도 구간·특이점 처리는 제시되어 있지 않다. 따라서 이를 임의의 식이나 실행 코드로 보완하지 않는다. 이 설명이 확인하는 것은, 센서 형상이 달라질 때 같은 고정 sampling box를 기계적으로 사용하지 않았다는 사실이다.

## 5. PPO와 세 과업의 행동 연결

### 5.1 학습 알고리즘과 공개된 세부 수준

원문은 **Stable-Baselines-3의 PPO**로 세 센서의 세 과업 정책을 학습했다고 명시한다. 세 센서에 대한 학습 결과가 Fig. 4에 있으며, 학습 후 최종 성능은 유사하고 정책을 실물로 옮긴 뒤 추가 fine-tuning을 하지 않았다고 보고한다. [원문 §IV-A, Fig. 4, PDF pp. 5–6]

이 논문은 플랫폼 확장·비교가 중심이어서 상세 학습 방법을 [1]로 넘긴다. **Reward의 항·수식·계수, 전체 observation vector, actor/critic 구조, PPO clip·entropy·learning rate·rollout 설정은 이 본문에 재현 가능한 형태로 제시되지 않는다.** 따라서 일반 PPO 식이나 다른 pushing 논문의 reward를 여기에 사용된 식처럼 넣지 않았다. [원문 §III-C, §IV-A, PDF pp. 3–5]

§IV-B는 정책이 **domain randomization을 사용해 학습되었다**고 설명하며, 영상 변환 품질의 작은 차이가 과업 성능을 크게 바꾸지 않는 이유로 든다. 어떤 항목을 어떤 범위로 randomize했는지는 본문에서 정량적으로 정의하지 않는다. 센서별 physics/camera 조정과 episode별 randomization은 같은 개념으로 합치지 않는다. [원문 §III-C, §IV-B, PDF pp. 4–5]

### 5.2 과업별 목표와 action: 원문 표기 유지

| 과업 | 조작 목표 | 원문이 명시한 2D action space |
| --- | --- | --- |
| Object pushing | 평면 위 물체를 순차 목표점으로 이동 | TCP의 **x-position과 rotation angle** |
| Edge following | 센서–edge 거리를 일정하게 유지하며 edge를 따라 sliding | TCP의 **x-position과 y-position** |
| Surface following | 접촉 깊이를 유지하고 sensor tip을 법선 방향으로 맞추며 sliding | TCP의 **y-position과 rotation angle** |

[원문 §III-F-1–3, PDF pp. 4–5]

TCP는 촉각 센서 tip에 위치한다. 위의 x·y는 원문의 표현이며, 다른 논문의 좌표계와 맞추려고 바꾸지 않았다. 출력이 절대 위치인지 증분인지, 각 성분의 범위·scaling·명령 주기, action에서 제외된 축의 자동 진행 규칙은 이 본문만으로 상세히 확정할 수 없다. 특히 고정된 ‘1 mm 전진’ 같은 별도 규칙을 덧붙이지 않는다.

### 5.3 Pushing: 열 개 목표점으로 나눈 경로 추종

각 pushing trajectory는 **동일 길이의 10개 구간**으로 나뉘며, 각 구간의 끝점이 목표가 된다. 따라서 한 궤적에 10개 goal이 있다. 로봇은 촉각 피드백으로 해당 경로를 따라 물체를 밀며, 평가 경로는 직선·곡선·정현파다. [원문 §III-F-1, §IV-C-1, PDF pp. 5–6]

**원문 본문의 궤적 표현 — 번호 없는 식**

$$
\begin{aligned}
\text{Straight:}\quad &y=kx,\\
\text{Curved:}\quad &y=0.001x^2,\\
\text{Sinusoidal:}\quad &y=0.02\sin(0.02x).
\end{aligned}
$$

$$
k\in[-0.3,0.3],\qquad x\in[0,200]\ \mathrm{mm}.
$$

[원문 §IV-C-1, PDF pp. 5–6]

정현파 계수와 단위는 위와 같이 인쇄되어 있다. 원문은 각 계수의 단위나 구현의 좌표 scaling을 따로 풀지 않으므로, 진폭을 다른 숫자로 고치거나 별도 metre–millimetre 변환을 도입하지 않았다. 이는 **원문 식의 보존**이지 실제 코드와의 일치 검증이 아니다.

Pushing episode는 **250 steps**, 이동 거리는 **200–280 mm**로 보고된다. 목표점 전환의 허용 오차, 최종 성공 threshold, 초기 접촉 오차 분포, 접촉 소실 시 종료·복구 조건은 본문에 수치로 제시하지 않는다. 250 steps와 Fig. 5의 몇 장면만으로 policy frequency를 역산하지 않는다. [원문 §III-F-1, §IV-C-1, Fig. 5, PDF pp. 5–6]

### 5.4 Edge following: edge 위치를 유지하는 sliding

센서 tip과 접촉 edge 사이의 거리를 고정한 채 경계를 따라 이동한다. Square의 직선·직각 모서리, clover의 양·음 곡률, teardrop 형태를 이용해 추종 성능을 평가한다. 영상 변환 모델을 학습시킨 자극은 **직선 edge**이며, 평가는 더 복잡한 경계로 확장한다. [원문 §III-F-2, §IV-C-2, Fig. 3·6, PDF pp. 5–7]

명시적인 edge pose 회귀기와 고정 gain controller를 사용한 것으로 설명하지 않는다. Edge 정보를 담은 변환 영상으로 학습된 PPO가 x·y 운동을 선택한다. 원하는 거리의 수치나 reward로 그 거리를 부과하는 상세식은 원문이 재기재하지 않는다.

### 5.5 Surface following: 4자유도에 맞춘 옆면 추종

고정 접촉 깊이와 normal orientation을 유지하며, arch·flower·circle의 수직 옆면을 따라 움직인다. 센서를 옆으로 장착하여 yaw를 사용하고, 한 방향으로 변하는 표면에 대해 법선 정렬을 수행한다. 이전 6축 플랫폼처럼 임의 3D 표면에서 roll·pitch를 모두 바꾸는 실험은 아니다. [원문 §III-B, §III-F-3, Fig. 1(d)·3(b), PDF pp. 2–5]

영상 변환 모델은 **평면 surface**에서 학습되지만 curved surface에서도 사용한다. 단, 이것이 오목·볼록한 모든 표면에서 세 센서가 모두 성공했다는 뜻은 아니며, DIGIT의 오목면 중단 사례를 별도로 기록한다. [원문 §IV-C-3, Fig. 7, PDF p. 7]

## 6. 힘·접촉 정보가 행동까지 연결되는 방식

### 6.1 관측에서 행동까지의 전체 연결

```text
물체와 센서 피부의 물리적 접촉
  → 피부 변형
  → marker 움직임 또는 image shading으로 나타나는 촉각 영상
  → 센서별 전처리와 real-to-sim generator
  → 해당 가상 센서의 depth-image 표현
  → 시뮬레이션에서 학습된 과업별 PPO 정책
  → TCP의 두 행동 성분
  → 접촉 상태와 물체/센서의 운동 변화
  → 다음 촉각 영상
```

이 흐름은 Fig. 1과 §III를 재구성한 것이다. **힘·압력을 물리 단위로 복원하는 중간 노드가 없다.** 센서 영상에는 접촉 기하·변형에 관한 정보가 담기지만, 모델이 force vector·마찰계수·미끄러짐 상태를 각각 추정했다고 논문이 입증하지는 않는다. [원문 Fig. 1–2, §III-A–F, PDF pp. 2–5]

### 6.2 Depth image가 하는 일과 하지 않는 일

영상 변환은 센서의 marker나 조명 차이로 표현이 달라지는 문제를 줄여, 실제 입력을 정책의 시뮬레이션 학습 관측에 대응시킨다. 따라서 **센서의 시각적 외형을 통일된 종류의 접촉 영상 표현으로 바꾸는 연결**이 핵심이다. [원문 §III-C–D, §IV-B, PDF pp. 3–5]

하지만 변환 영상의 depth가 센서 전체에서 독립적으로 교정된 물리적 indentation field라고 검증된 것은 아니며, SSIM은 그 물리량 정확도를 측정하지 않는다. 이 논문은 depth map에서 6축 wrench를 적분하거나 접촉점·법선 벡터를 명시적으로 계산하여 정책 입력으로 주는 후처리도 제시하지 않는다.

### 6.3 힘이 부족할 때의 실패: DIGIT와 가벼운 prism

저자들은 세 물체 중 가장 가벼운 **185 g triangular prism**을 DIGIT로 밀 때 모든 경로에서 실패했다고 보고한다. 가능한 원인으로 **상대적으로 뻣뻣한 elastomer가 충분히 변형되지 않아 tactile image translation이 실패한다**는 가설을 제시한다. [원문 §IV-C-1, Table IV, PDF p. 6]

이를 시험하기 위해 PPO·GAN 모델을 그대로 두고 prism에 분동만 더한다. +50·100·150·200 g 조건의 결과가 Table V이며, +150 g까지 대체로 개선되고 그 이후에는 추가 이득이 없었다고 설명한다. 저자들은 하중 증가가 실제 촉각 영상을 **GAN 학습 분포 안으로 들어오게 한다**고 해석하며, 그 범위 안에서는 병목이 GAN보다 RL 정책으로 넘어간다고 추정한다. [원문 §IV-C-1, Table V, PDF p. 6]

이 연결에서 확인된 실험 조작은 **질량 변경**, 관측된 결과는 **실패 여부와 궤적 오차 변경**이다. 접촉력·피부 변형량·분포 이탈 정도를 동시에 정량 측정한 표는 없으므로, 하중 증가가 어느 뉴턴 임계값을 넘겼다는 설명이나 병목 전환의 독립적 증명으로 확대하지 않는다. **185 g은 센서 최소 검출 힘이 아니다.**

### 6.4 더 강하게 누르면 sliding 마찰도 커진다

Edge-following에서는 DIGIT의 상대적으로 평평하고 뻣뻣한 피부가 작은 penetration 변화에 더 민감하게 반응한다고 설명한다. 충분한 변형을 확보하려면 더 강한 접촉이 필요한데, 그 결과 마찰력도 증가한다. 저자들은 센서 손상을 피하고 sliding을 쉽게 하기 위해 **물체를 wax로 코팅**했다고 명시한다. [원문 §IV-C-2, PDF p. 7]

이는 실행 중 force measurement를 보고 자동으로 목표 힘을 조절하는 제어법이 아니라, **물리적 실험 조건을 조정한 조치**다. 코팅량·마찰계수·가압력 수치는 없고, 모든 센서·과업에 동일하게 코팅했는지도 세분해 적지 않으므로 비교 조건을 임의로 동일하다고 가정하지 않는다.

### 6.5 변환이 잘되어도 형상·재료의 운동 제한은 남는다

Surface-following에서 DIGIT는 원형 물체에 대해 가장 작은 평균 오차를 보였지만, arch·flower의 오목한 구간에서는 걸리는 현상이 발생한다. 저자들은 평평하고 뻣뻣한 sensing surface 때문에 sliding이 방해된다고 설명하고, 손상을 피하기 위해 해당 실험을 진행하지 않기로 했다고 기록한다. [원문 §IV-C-3, Table VII, Fig. 7, PDF p. 7]

따라서 **영상 변환의 높은 평균 SSIM**, **완주한 경로의 낮은 위치 오차**, **특정 기하에서의 물리적 완주 가능성**은 서로 다른 결과다. 한 숫자가 좋다는 이유로 나머지까지 확보되었다고 볼 수 없다.

### 6.6 원문이 제공하는 메커니즘 설명의 경계

본 연구는 센서별 물리적 변형·영상 표현이 행동 성능에 영향을 준다는 실증 근거를 제공한다. 다만 policy 내부에서 어떤 이미지 특징이 어느 방향의 action을 만드는지 feature attribution이나 intervention으로 분해한 결과는 없다. **관측 변환과 행동 경로는 명확하지만, PPO의 내부 특징을 명시적인 힘 추정·slip 검출·법선 제어로 재해석해서는 안 된다.** [원문 §III–V, PDF pp. 3–8]

## 7. 실험 결과

### 7.1 시뮬레이션 학습

Fig. 4는 edge-following·surface-following·object-pushing에서 센서별 평균 학습 성능을 제시한다. 저자들은 초반의 작은 차이를 tip 형상에 따른 접촉 동역학 차이로 해석하지만, 최종적으로는 세 센서 모두 유사한 성능에 도달했다고 보고한다. 정확한 최종 reward, 반복 seed 수, 음영 구간의 통계 정의를 표로 제공하지는 않는다. 그래프를 보고 임의의 수렴 step이나 신뢰구간을 확정하지 않았다. [원문 §IV-A, Fig. 4, PDF pp. 5–6]

### 7.2 Table III: 영상 변환 SSIM

| Contact feature | TacTip | DigiTac | DIGIT |
| --- | --- | --- | --- |
| Edge | **0.9956** | 0.9953 | 0.9867 |
| Surface | 0.9927 | **0.9932** | 0.9818 |

[원문 Table III, PDF p. 5 / 인쇄 p. 10758]

값은 validation dataset에서의 **평균 Structural Similarity Index**이며, 1에 가까울수록 변환 이미지와 기준 이미지가 잘 맞는다는 의미다. DIGIT가 두 feature에서 조금 낮지만, 저자들은 모든 센서에서 변환 방법이 유효했다고 평가한다. 미세한 SSIM 차이의 영향이 작았던 이유는 정책의 domain randomization으로 설명한다. [원문 §IV-B, PDF p. 5]

이 validation 결과가 가벼운 prism의 모든 접촉 영상에서도 같은 품질을 보장하지는 않는다. 6.3절의 실패 가설은 학습·검증용 접촉 분포와 실제 조작 중 변형 조건이 달라질 수 있다는 설명이다.

### 7.3 Table IV: pushing 궤적 오차

수치는 실제 궤적과 ground-truth 궤적 사이의 **평균 Euclidean distance, 단위 mm**다. 아래는 읽기 편하도록 원문의 넓은 표를 경로·물체별 행으로 바꿨다. Bold는 **추가 하중 없는 세 센서 사이의 최솟값**이며, weighted 행에 해당하는 값은 별도 조건이다.

| 경로 | 물체 | TacTip | DigiTac | DIGIT | DIGIT, 물체 +150 g |
| --- | --- | --- | --- | --- | --- |
| Straight | Cube | **10.33** | 11.25 | 11.20 | 10.92 |
| Straight | Cylinder | **9.21** | 10.24 | 10.13 | 11.00 |
| Straight | Triangular prism | **11.51** | 16.09 | N/A | 16.65 |
| Curve | Cube | **12.19** | 13.01 | 12.94 | 12.28 |
| Curve | Cylinder | 11.29 | **11.20** | 12.00 | 11.51 |
| Curve | Triangular prism | **13.20** | 16.41 | N/A | 16.58 |
| Sine | Cube | **11.93** | 12.32 | 12.41 | 12.07 |
| Sine | Cylinder | **11.30** | 11.48 | 11.33 | 11.53 |
| Sine | Triangular prism | **13.89** | 15.13 | N/A | 17.06 |

[원문 Table IV, PDF p. 6 / 인쇄 p. 10759]

Table IV에서 **N/A는 failure case**다. 평균 오차 0이나 시험을 성공적으로 완주한 누락값으로 처리하지 않는다. 마지막 조건은 prism만이 아니라 **세 물체 모두에 150 g을 더한 DIGIT 실험**이다. [원문 Table IV caption]

저자들은 대략 10 mm 수준의 오차를 200–280 mm 이동 거리 및 20–40 mm tip 크기와 함께 해석한다. TacTip의 큰 접촉면이 더 안정적인 push에 도움이 된다는 설명을 제시하지만, 표에는 curved cylinder에서 DigiTac이 약간 더 작은 오차를 보이는 예외도 있다. [원문 §IV-C-1, PDF p. 6]

Fig. 5는 DigiTac–prism–curve, DIGIT–cube–straight, TacTip–cylinder–sine의 사례와 실제 물체 궤적을 보여 준다. 그림의 일부 snapshot 시각을 전체 시험 평균 수행 시간이나 제어 주파수로 바꾸지는 않는다. [원문 Fig. 5, PDF p. 6]

### 7.4 Table V: 같은 PPO·GAN을 유지한 DIGIT 추가 하중 실험

| Prism 질량 조건 | Straight 오차 (mm) | Curve 오차 (mm) | Sine 오차 (mm) |
| --- | --- | --- | --- |
| 185 g + 0 g | N/A | N/A | N/A |
| 185 g + 50 g | 18.05 | 17.73 | 17.95 |
| 185 g + 100 g | 16.93 | 17.54 | 18.12 |
| 185 g + 150 g | **16.65** | **16.58** | **17.06** |
| 185 g + 200 g | 17.17 | 16.92 | 17.26 |

[원문 Table V, §IV-C-1, PDF p. 6]

+150 g에서 세 경로의 최솟값을 얻고 +200 g에서는 추가 개선이 없다. 다만 sine은 +50 g에서 +100 g으로 갈 때 17.95 → 18.12 mm로 조금 커지므로, 모든 하중 단계에서 오차가 엄격히 단조 감소한 것은 아니다. 원문이 제시한 ‘+150 g까지의 개선’이라는 전체 경향과 개별 셀 값을 구분한다.

이 실험은 **다시 학습하지 않고 물리적 접촉 조건을 바꿔 성능을 회복한 사례**다. 새로운 강화학습 알고리즘의 효과나 명시적 online force adaptation으로 해석하지 않는다. 원문의 병목 가설은 6.3절과 같다.

### 7.5 Table VI: edge-following

| 센서 | Square (mm) | Clover (mm) | Foil (mm) |
| --- | --- | --- | --- |
| DIGIT | 0.88 | 1.71 | 1.82 |
| DigiTac | 1.04 | **0.85** | 0.86 |
| TacTip | **0.63** | 1.42 | **0.67** |

[원문 Table VI, PDF p. 7 / 인쇄 p. 10760]

세 센서 모두 경계를 끝까지 추종했다고 보고한다. Table VI의 `Foil`은 Fig. 3(a)의 세 번째 teardrop형 자극에 대응하며, 원문의 서로 다른 명칭을 함께 남겼다. Fig. 6에는 CAD ground truth, 실제 trace, 시작점·방향, 위치 오차 색상이 표시된다. [원문 §III-F-2, §IV-C-2, Fig. 3·6, PDF pp. 5–7]

평균 오차가 낮아도 국소 오차가 작은 것은 아니다. 저자들은 DIGIT에서 일부 구간의 오차가 약 5 mm까지 커졌다고 설명한다. 더 강한 접촉의 필요성과 그로 인한 마찰·wax 처리도 함께 보고되어 있으므로, 낮은 평균 오차만 떼어 센서 성능을 평가하지 않는다. [원문 §IV-C-2, PDF p. 7]

### 7.6 Table VII: surface-following

| 센서 | Arch (mm) | Flower (mm) | Circle (mm) |
| --- | --- | --- | --- |
| DIGIT | N/A | N/A | **0.47** |
| DigiTac | **0.79** | **1.04** | 0.58 |
| TacTip | 0.91 | 1.23 | 0.59 |

[원문 Table VII, PDF p. 7 / 인쇄 p. 10760]

DIGIT는 circle에서 가장 정확하지만 arch·flower의 오목면에서 문제가 발생한다. Fig. 7 caption은 red cross를 실패 지점으로 설명하고, 본문은 걸림과 손상 위험 때문에 DIGIT로 해당 과업을 수행하지 않기로 했다고 기록한다. 따라서 두 N/A를 **완주한 시험의 평균 오차**나 **일반적인 센서 성능 0점**으로 치환하지 않는다. [원문 §IV-C-3, Table VII, Fig. 7]

### 7.7 결과 전체가 뒷받침하는 결론

저자들은 센서마다 다른 감지 원리에도 불구하고 depth rendering–image translation–PPO 절차를 사용할 수 있음을 보였다고 결론짓는다. 그러나 실제 조작 범위는 피부의 강성과 형상에 영향을 받는다. 원형 표면에서 DIGIT가 가장 낮은 오차를 보인 결과와, 약한 접촉·오목한 표면에서 실패한 결과는 함께 유지되어야 한다. [원문 §IV-C, §V, PDF pp. 6–8]

이 결과들은 주로 평균 궤적 오차와 특정 실패 사례다. 반복 횟수·seed·분산·신뢰구간을 포함하는 전수 성공률 비교표가 아니므로, 모든 물체·경로 분포에 대한 통계적 우위를 주장하지 않는다.

## 8. Limitation — 저자들이 밝힌 한계

독립적인 Limitation 제목은 없지만 §III, §IV-C와 §V에 제약·실패·적용 한계가 명시되어 있다. 아래는 **저자들이 밝힌 내용**이며, 10절의 미기재 정보 목록이나 별도 연구 제안과 구분한다.

### 8.1 낮은 자유도에 따른 과업 범위 제한

MG400은 x·y·z와 yaw만 구동하므로, 기존 UR5 실험에서 쓰던 roll·pitch로 일반적인 표면 법선 정렬을 할 수 없다. 저자들은 장착 방향을 변경하고 한 방향으로 변화하는 표면으로 과업·데이터 수집을 수정했다. 저가화와 함께 과업의 운동 범위도 바뀐 것이다. [원문 §III-A–B, PDF p. 3]

### 8.2 센서가 달라질 때 필요한 영상 처리·보정

센서 설계·조명·카메라 시점이 다르므로 image preprocessing과 관련 하이퍼파라미터를 센서별로 조정해야 한다. DIGIT의 미묘한 음영은 marker 기반 센서보다 튜닝이 어렵다고 설명한다. 이는 공통 방법론의 일반성이 모든 sensor configuration에서 무보정 이전을 뜻하지 않는다는 제한이다. [원문 §III-B–D, §V, PDF pp. 3–4, 7]

### 8.3 가벼운 물체와 뻣뻣한 피부에서 충분한 촉각 변형을 얻기 어려움

DIGIT를 고려해 기존 [1]의 50–80 g 물체보다 무거운 185–363 g 물체를 사용했다. 그럼에도 가장 가벼운 prism은 기본 하중에서 실패한다. 원문은 상대적으로 뻣뻣한 피부와 부족한 변형으로 인한 영상 변환 실패를 가설로 제시하고, 추가 하중 실험을 수행한다. 센서의 재료와 과업 물체가 만드는 접촉 조건이 학습된 pipeline의 적용 범위를 제한한다. [원문 §III-F-1, §IV-C-1, PDF pp. 5–6]

### 8.4 더 강한 접촉, 마찰 및 손상 위험

Edge-following에서 DIGIT에 충분한 변형을 만들기 위해 더 forceful한 접촉이 필요하고, 그에 따라 마찰력도 증가한다. 저자들은 센서 보호를 위해 wax coating으로 sliding을 돕는다. 피부 변형 신호를 확보하는 것과 센서를 손상 없이 움직이는 것은 동시에 고려해야 하는 문제로 보고된다. [원문 §IV-C-2, PDF p. 7]

### 8.5 오목면에서의 DIGIT 걸림

더 평평하고 뻣뻣한 DIGIT 피부가 오목한 표면 위 sliding을 방해한다. Arch·flower에서 걸림이 관찰되었고 손상을 피하려고 해당 시험을 진행하지 않았다. §V에서도 이러한 구조가 concave surface following에 적합하지 않았다고 정리한다. 이는 image-shading 원리 일반의 불가능성이 아니라 **시험한 센서의 구성·재료와 특정 기하의 문제**로 설명된다. [원문 §IV-C-3, §V, PDF pp. 7–8]

### 8.6 Ball rolling은 구현하지 않음

플랫폼이 ball rolling에도 적용 가능할 것으로 기대하지만, 당시 DigiTac에는 그 과업에 적합한 flat skin이 없어서 본 연구에서는 구현하지 않았다고 명시한다. 기대한 확장 가능성과 실제 세 과업의 검증 범위는 다르다. [원문 §III-F, PDF p. 4]

## 9. Future Work — 저자들이 제시한 향후 방향

### 9.1 GelSight 계열에 더 적합한 영상 변환 구조

DIGIT의 영상 변환 SSIM이 조금 낮다는 결과에 대해, **GelSight-type sensor에 더 잘 맞는 다른 neural network architecture가 결과를 바꿀 수 있다**고 언급한다. 이것은 §IV-B의 가능성 제안이며, 본 논문에서 대체 architecture를 비교·검증한 성과는 아니다. [원문 §IV-B, PDF p. 5]

### 9.2 과업별 센서 물리 특성의 선택·맞춤화

§V는 이러한 empirical comparison이 후속 연구자에게 조작 상황에 맞는 **촉각 센서의 물리적 특성 선택·customization**을 도울 것이라고 설명한다. 감지 원리의 이름만이 아니라 실제 피부 구조·재료와 과업의 관계를 비교하는 benchmark로 발전시키려는 방향이다. 정확한 후속 센서 설계값이나 실험 계획은 제시하지 않는다. [원문 §I의 기여, §V, PDF pp. 2, 8]

### 9.3 더 복잡한 행동과 파지·dexterous manipulation으로 확장

저자들은 저가 플랫폼의 일반성이 TacTip·GelSight 계열 모두에서 복잡한 행동의 sim-to-real deep RL을 개발할 가능성을 연다고 본다. 또한 controlled scenario에서 기본 방법을 개발한 뒤, **prehensile manipulation과 dexterous robot hand의 더 어려운 응용**으로 발전시킬 수 있다고 기대한다. 이는 향후 활용 방향이며 본 논문이 다지 손 파지 정책을 실험했다는 뜻은 아니다. [원문 §V, PDF p. 8]

### 9.4 Ball rolling에 대한 기대의 수준

§III-F의 ball rolling 언급은 현재 flat skin 부재로 구현하지 않았지만 적용 가능성을 기대한다는 수준이다. 이를 ‘다음 단계에서 반드시 flat DigiTac을 제작한다’는 확정 계획으로 바꾸지 않는다. 명시된 기대와 현재 미구현 이유만 기록한다. [원문 §III-F, PDF p. 4]

## 10. 미명시 사항과 원문 해석상 주의

### 10.1 재현을 위해 추가 자료가 필요한 부분

| 분야 | 이 논문 본문에서 확인하지 못한 상세 내용 |
| --- | --- |
| 센서 사양 | 개별 tip 치수, marker 수·pitch, 영상 픽셀 수·fps, 물리적 힘 범위·분해능·정확도 |
| 시뮬레이션 | 센서별 마찰·강성·감쇠 수치, physics timestep, solver·버전, camera intrinsics/extrinsics |
| 영상 변환 | 전처리 순서·수치, generator/discriminator 층·채널, loss·optimizer·학습률·batch |
| Dataset | 각 6시간의 집계 단위, 연속 샘플 독립성, pose sampling 분포의 상세 정의, tangent scaling 구현 |
| 정책 입력 | 촉각 외 고유감각·목표 정보의 정확한 항목·좌표계, 전체 차원, history·frame stacking 여부 |
| PPO | Actor/critic 구조, clip·entropy·discount·rollout·batch·seed, 정확한 reward 구성 |
| Action·로봇 제어 | 절대 위치/증분 구분, action bounds, scaling, 자동 진행 축, update frequency·latency·IK |
| Domain randomization | 대상 변수, 분포, 범위, 갱신 시점 |
| Reset·종료·안전 | 초기 오차 분포, 접촉 실패 판정, goal 전환·최종 성공 threshold, 과부하 한계 |
| 실물 시험 | Cube·cylinder 각각의 기본 질량, 개별 물체 치수·마찰, wax의 적용 범위·량, 실제 접촉력 |
| 통계·평가 | 반복 횟수·분산, Fig. 4 음영의 정의, 궤적 점 대응과 오차 집계의 상세식 |

이 표는 **원문 자체의 상세 기술 범위**를 기록한 것이다. 구현에 해당 기능이 없다는 주장도 아니고, 저자들이 이 모든 항목을 자신의 Limitation이라고 선언했다는 뜻도 아니다. 원문은 여러 상세를 기존 연구 [1]과 공개 자료로 넘기지만, 이번에는 그 자료까지 읽은 것으로 취급하지 않았다.

### 10.2 혼동하면 안 되는 수치·주장

| 원문 항목 | 유지해야 할 구분 |
| --- | --- |
| MG400 0.05 mm | 본문은 repeatability, Table I는 Accuracy라는 행명. 촉각 해상도가 아님 |
| Table II pose ranges | 영상 변환용 sampling 범위. 힘 측정 범위나 RL action bounds가 아님 |
| SSIM 0.98–0.99대 | 이미지 유사도. 접촉력 정확도·위치 분해능·정책 성공률이 아님 |
| 185 g 및 +150 g | 시험 물체의 질량·추가 하중. 최소 검출 힘이나 접촉 임계값이 아님 |
| Table IV weighted 조건 | DIGIT에서 모든 pushing 물체에 +150 g. 무가중 세 센서의 동일 조건 비교와 구분 |
| Table V 성능 경향 | +150 g이 최적이지만 개별 단계가 모두 단조 개선되지는 않음 |
| Surface의 두 N/A | Fig. 7은 실패 위치, 본문은 걸림·파손 위험으로 시험 미진행을 설명. 완주 오차 없음 |
| Foil / teardrop, Circle / disc | 원문의 표·그림 명칭 차이. 별도의 추가 물체로 세지 않음 |
| 단일 sim-to-real approach | 공통 절차이지 모든 센서에 같은 GAN·policy weights라는 검증이 아님 |
| Zero-shot | 이전 후 policy 재학습 없음. 실제 영상 수집·센서별 calibration 없음이라는 뜻은 아님 |
| 세 과업에서 유효하다는 결론 | 개별 물체·표면의 실패·중단 예외를 제거하지 않음 |

### 10.3 이 논문만으로 밝히지 못하는 정책 내부의 물리적 추론

접촉 영상이 정책 행동을 바꾸는 폐루프와 그 실물 성능은 제시된다. 그러나 ‘PPO가 힘 크기를 추정했다’, ‘마찰계수를 식별했다’, ‘slip을 분류해 특정 보정으로 전환했다’ 같은 내부 메커니즘을 직접 확인하는 결과는 없다. 원문에서 부재한 상태 추정·force controller를 덧붙이기보다 **영상 표현의 이전, 과업별 행동, 접촉 조건별 성공·실패**를 이 연구가 실제 보여 준 수준으로 정리하는 것이 정확하다.

## 11. 원문을 다시 읽을 때의 위치 안내

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 접근성 문제와 세 가지 기여 | Abstract, §I, PDF pp. 1–2 / 인쇄 pp. 10754–10755 |
| 촉각 RL·sim-to-real Related Work | §II-1–2, PDF p. 2 |
| 세 단계 pipeline과 실물 실행 경로 | Fig. 1, §III-B, PDF pp. 2–3 |
| MG400 상세·플랫폼 비교 | §III-A-1, Table I, PDF p. 3 |
| 센서 원리·DigiTac 구성·장착 변경 | §III-A-2–B, PDF p. 3 |
| Rigid-body contact와 depth rendering | §III-C, Fig. 2, PDF pp. 3–4 |
| GAN 구조와 센서별 조정 | §III-D, §V, PDF pp. 4, 7 |
| Dataset 수·크기·시간·비대칭 보정 | §III-E, PDF p. 4 |
| 센서별 pose sampling 범위 | Table II, PDF p. 4 |
| 세 과업 목표·action·평가 정답 | §III-F, Fig. 3, PDF pp. 4–5 |
| PPO와 policy fine-tuning 여부 | §IV-A, Fig. 4, PDF pp. 5–6 |
| SSIM·domain randomization 설명 | §IV-B, Table III, PDF p. 5 |
| Pushing 경로·250 steps·궤적 오차 | §IV-C-1, Table IV, Fig. 5, PDF pp. 5–6 |
| 가벼운 prism 실패·추가 하중·분포 가설 | §IV-C-1, Table V, PDF p. 6 |
| Edge 추종·마찰·wax coating | §IV-C-2, Table VI, Fig. 6, PDF pp. 6–7 |
| Surface 추종·DIGIT concave 중단 | §IV-C-3, Table VII, Fig. 7, PDF p. 7 |
| 저자들의 종합 해석과 향후 응용 | §V, PDF pp. 7–8 |
| 미구현 ball rolling과 이유 | §III-F, PDF p. 4 |
| 인용 선행연구의 서지 | References [1]–[34], PDF p. 8 |

## 12. 핵심 메커니즘 요약

**접촉에 의한 피부 변형 → marker 또는 음영 영상 → 센서별 real-to-sim GAN → 시뮬레이션 depth-image 표현 → PPO 정책 → TCP 위치·회전 행동**이 이 논문의 정보–행동 연결이다. 힘을 물리 단위로 복원하는 대신 영상 형태의 접촉 정보를 활용한다. [원문 §III, Fig. 1–2, PDF pp. 2–5]

중요한 실증 결과는 영상 변환 방법의 센서 간 적용 가능성과, **센서 구조·재료가 충분한 변형·sliding·완주 가능성을 제한한다는 점**이다. DIGIT의 가벼운 prism 실패·분동 추가, edge-following의 wax 처리, concave surface의 중단은 이 차이를 보여 주는 구체적 사례다. 다만 피부 강성·실제 접촉력·정책 내부 특징을 정량 분해한 연구는 아니며, 파지·dexterous hand와 ball rolling 등은 검증 결과가 아니라 후속 가능성으로 남는다. [원문 §III-F, §IV-C, §V, PDF pp. 4–8]
