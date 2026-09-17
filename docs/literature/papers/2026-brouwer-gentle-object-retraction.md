# Gentle Object Retraction in Dense Clutter — 원문 상세 정리

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 조사 · USER-P001](../reviews/user-found-papers.md#user-p001)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Gentle Object Retraction in Dense Clutter Using Multimodal Force Sensing and Imitation Learning** |
| 저자 | Dane Brouwer, Joshua Citron, Heather Nolte, Jeannette Bohg, Mark Cutkosky |
| 출판 | IEEE Robotics and Automation Letters, Vol. 11, No. 2, February 2026, pp. 1578–1585 |
| DOI | [10.1109/LRA.2025.3643332](https://doi.org/10.1109/LRA.2025.3643332) |
| 출판 이력 | 접수 2025-06-17, 승인 2025-11-28, 온라인 출판 2025-12-11, current version 2025-12-19. 권·호의 게재연도 2026과 온라인 출판연도 2025를 구분한다. |
| 문헌 관리 ID | [사용자 별도 발굴 논문 목록](../reviews/user-found-papers.md#user-p001)의 **USER-P001**. 기존 조사본의 R1–R7 및 IROS-S01–S05에 추가한 항목이 아니다. |
| 정리일 | 2026-09-16 |
| 확인한 원문 | 첨부 출판본 PDF 8쪽 전체. 본문 §I–VII, 식 (1)–(3), Fig. 1–7, References [1]–[46]. 번호가 부여된 표와 부록은 없다. |
| 확인하지 않은 자료 | 보충 영상·다운로드 자료, 코드·설정·체크포인트·원시 로그, 인용된 선행논문의 개별 원문, 제조사 데이터시트 |
| 원문 PDF SHA-256 | `aea8d5dca5fa450d5ca5385d33cfde6963921726202723eee2fd916b24ff093d` |

이 문서는 해당 논문 자체의 문제, Related Work, 환경·센서, 힘 처리, 모방학습, 실험, 저자 명시 Limitation 및 Future Work를 정리한다. 다른 연구에 대한 적용안은 포함하지 않는다. `[원문 §…, PDF p.…]`는 첨부 출판본의 위치이며, **PDF 1–8쪽은 인쇄 페이지 1578–1585**에 대응한다. `[35]` 같은 번호는 원문의 참고문헌 번호다. 수식 해설과 비율 계산은 원문에서 출발한 재구성이며 새로운 실험 결과가 아니다.

**핵심:** 벽과 천장이 있는 고밀도 선반에서, 로봇이 주변 물체와 접촉하면서 빨간 목표를 찾아 흡착하고 밖으로 꺼낸다. **두 측면의 분포형 3축 촉각을 RGB 형태로 표현하고, 관절 토크에서 추정한 TCP wrench를 별도 저차원 입력으로 제공하여 Diffusion Policy를 학습**한다. 동시에 두 힘 정보를 이용한 impulse 기준으로 시연과 평가의 과도한 접촉을 제한한다. 주된 검증은 센서 입력 ablation이며, 새로운 RL 알고리즘·GAN·sim-to-real 방법이나 수작업 힘 추종 제어기를 제안하는 연구가 아니다. [원문 §I, §III–V, PDF pp. 1–6]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 정의·기여와 Related Work |
| 3–4 | 로봇·센서 상세 사양, 선반·물체·과업 조건 |
| 5–6 | 분포형 촉각의 영상화, wrench 추정, 흡착 상태 처리 |
| 7–9 | Diffusion Policy, impulse 기준, 원격조작 시연과 학습 |
| 10–12 | 센서 ablation, 성공·실패·시간, 힘 이후 운동 반응 분석 |
| 13–15 | Discussion의 해석, 저자 명시 Limitation, Future Work |
| 16–17 | 미명시 정보·해석 주의사항, 원문 위치와 검증 범위 |

## 1. 제시하는 문제 상황과 연구의 목적

### 1.1 시각적 혼잡뿐 아니라 물리적으로 걸리는 환경

가정의 캐비닛이나 창고 선반에는 여러 이동 가능한 물체가 밀집되어 있다. 목표를 꺼내려면 다른 물체를 건드리지 않는 경로가 거의 없으므로, 기존의 충돌 회피만으로는 과업을 수행하기 어렵다. 로봇이 접촉을 활용하면서도 과도한 힘으로 물체나 환경을 손상시키지 않아야 한다. [원문 Abstract, §I, PDF p. 1]

이 논문에서 강조하는 환경은 **lateral access**, 즉 선반의 앞쪽에서 들어가는 조건이다. 위에서 내려다보거나 위로 접근할 수 있는 열린 탁상 환경과 달리, 로봇 자체와 물체에 의해 시야가 가려지고, 주변 물체를 밀면 벽 또는 다른 물체에 걸릴 수 있다. 처음에는 잘 움직이던 물체도 군집이 벽에 끼면 갑자기 움직이기 어려워진다. 고정 장애물만을 다루는 문제와 구분되는 이유다. [원문 §I–II, PDF pp. 1–2]

Fig. 1(c)는 이를 보여 준다. 초기 자세에서 밀면 물체들이 왼쪽 벽에 걸려 큰 접촉력이 생긴다. 로봇은 그 접촉에서 벗어나는 다른 자세로 이동하면서 목표에 대한 접근을 이어 간다. 그림의 overhead view는 독자 설명용이며 **로봇이 사용하는 관측이 아니다.** [원문 Fig. 1, PDF p. 1]

### 1.2 Non-prehensile tactile의 의미

저자들은 비파지 조작 중 생기는 상호작용을 감지하는 분포형 접촉력 센서를 **non-prehensile tactile sensor**로 정의한다. 이 시스템에서는 물체를 흡착하는 컵 자체가 아니라, 좁은 말단 도구의 좌우 측면에서 주변 물체를 밀고 스치는 힘을 측정한다. 목표 획득 여부는 별도의 진공관 압력으로 판단한다. [원문 §II–III-A, Fig. 1–2, PDF pp. 2–3]

즉, `촉각 = 물체를 잡았는지 확인하는 손끝 신호`로만 다루지 않는다. 주변 물체를 헤치고 들어가거나 빠져나오는 동안의 접촉도 정책이 알아야 할 정보로 취급한다.

### 1.3 연구 질문과 기여의 실제 범위

저자들의 질문은 **접촉이 불가피한 고밀도 선반 인출에서 wrench와 분포형 tactile이 각각, 그리고 함께 얼마나 도움이 되는가**다. 이를 위해 같은 모방학습 구조와 시연 데이터에서 두 감각 입력의 제공 여부를 바꾼 네 정책을 비교한다. [원문 §I Contributions, §V-A, PDF pp. 2, 5]

보고한 기여는 다음 세 축으로 정리할 수 있다. 이는 원문 Contributions의 재구성이다.

| 축 | 논문에서 검증하는 내용 |
| --- | --- |
| 센서의 역할 비교 | Wrench-only, tactile-only, 병용 조건의 과업 성능을 비접촉력 기준선과 비교 |
| 물리적 밀집 환경의 인출 | 점유 면적 45–55%의 lateral-access 장면에서 접근·탐색·흡착·인출 수행 |
| Gentle manipulation의 평가 | 최종 성공뿐 아니라 과도한 힘 실패, timeout, 성공 시간, 큰 힘 이후 운동 반응 평가 |

다만 형상 다양성, 변형 가능성, 광학·분광 특성의 영향을 독립적인 요인으로 조사한 것은 아니라고 명시한다. 장면 배치가 달라진다는 사실과 미지 물체 종류에 대한 일반화 검증을 구분한다. [원문 §I Contributions, PDF p. 2]

## 2. Related Work — 원문이 설정한 비교 구도

아래 내용은 **이 논문의 §II가 선행연구를 설명한 방식**이다. 인용 논문들을 이번 작업에서 별도로 정독했다는 의미는 아니다. [원문 §II, PDF p. 2]

| 선행연구 범주 | 원문 참고문헌 | 인정하는 내용 | 이 논문이 구분하는 문제 |
| --- | --- | --- | --- |
| 접촉력이 포함된 다중감각 학습 | [4]–[12] | Wrench·tactile 표현 학습, kinesthetic 또는 robot-free 시연, 양손 visuotactile 조작 | 고밀도 환경에서 비파지 표면에 생기는 접촉을 중심으로 조사하지 않음 |
| 탁상 decluttering·인출·packing | [13]–[20] | 비파지 재배치·인출 및 일부 force-sensing 활용 | 위에서 장면을 볼 수 있고 개방되어 있어, lateral access의 가림·군집 jamming과 다름 |
| 선반의 mechanical search·인출 | [21]–[25] | 가려진 목표를 찾고 접근 가능하도록 고립시킴 | 상대적으로 낮은 밀도와 non-prehensile tactile의 부재를 지적 |
| 촉각 기반 움직임 분류 | [26] | 제한된 clutter에서 물체의 운동 종류를 분류 | 분류 결과를 실제 motion planning에 연결하는 일이 자명하지 않음 |
| 고정 장애물 사이의 촉각 reaching | [27]–[30] | 시각 없이 접촉을 줄이면서 목표 위치로 접근 | 움직이는 물체 군집의 갑작스러운 impedance 변화·jamming을 회피한 설정 |
| 촉각 반응 primitive | [31] | 제한된 lateral access에서 접촉에 반응하며 reaching | 목표 위치를 미리 알고 있으며, 목표 물체 인출까지 수행하지 않음 |
| Blind recognition·retrieval | [32]–[33] | 촉각만으로 물체를 인식·인출 | 시각과 힘 센싱의 상호작용을 조사하지 않음 |

직접적인 전작인 [31]은 *Tactile-informed action primitives mitigate jamming in dense clutter*다. 본 논문은 그 primitive 제어를 그대로 사용한다고 설명하지 않는다. **본 논문의 실행 정책은 실제 시연을 이용한 Diffusion Policy**이며, 다중 힘 센싱의 유용성을 ablation으로 비교한다. [원문 §II–III, References [31], PDF pp. 2–3, 8]

## 3. 로봇 플랫폼과 상세 센서 사양

### 3.1 플랫폼·제어 구성

| 항목 | 원문에 명시된 내용 | 구분·확인 위치 |
| --- | --- | --- |
| 로봇 팔 | Flexiv Rizon 4 | §III-A, PDF p. 2 |
| 말단 도구 | 좁은 형태의 3D-printed custom end-effector | Fig. 1(a), §III-A |
| 물체 획득 장치 | Suction cup, vacuum pump, 3-way solenoid valve | §III-A, §IV-C, PDF pp. 2, 5 |
| 소프트웨어 구성 | ROS가 Flexiv 소프트웨어와 센서들을 연결 | §III-A. ROS 배포판·구체 controller API는 미명시 |
| 원격조작 장치 | 3Dconnexion SpaceMouse Compact | §IV-C, PDF p. 5 |
| 시연에서 조작하는 운동 성분 | TCP의 x·y·z 위치와 yaw. Roll·pitch는 캐비닛 정렬을 유지하도록 고정 | §IV-C. 로봇의 전체 기구학적 자유도와 구분 |
| 정책 행동 형식 | Cartesian position 3개 + quaternion 4개 + suction command 1개 | 원문 식 (1), PDF p. 3 |
| 시스템 sampling rate | 10 Hz | §IV-B, PDF p. 4. 각 센서의 제조사 최대 주파수가 아님 |
| 실행 action chunk | 8 action steps | §IV-B. 총 prediction horizon이나 diffusion denoising 횟수와 다름 |

원문에는 로봇의 관절 수, 최대 가반하중, reach, 반복정밀도, 최대 속도·토크, 세부 servo 주파수의 수치가 없다. **모델명 ‘Rizon 4’의 숫자를 자유도라고 해석하지 않는다.**

### 3.2 센서별 실제 측정·추정 정보

| 감각 | 위치·생성 방식 | 출력·성능 | 원문 위치 |
| --- | --- | --- | --- |
| Eye-in-hand vision | 말단에 부착된 monocular fisheye camera | 정책 영상 128×128×3. 카메라 모델·native 해상도·FOV·frame rate 미명시 | §III-A–B, Fig. 1·3, PDF pp. 2–3 |
| 분포형 tactile | 도구의 왼쪽·오른쪽에 각각 soft triaxial array | 센서당 49 elements, 총 98 taxels. 각 taxel은 x·y·z 힘을 제공 | §III-A, Fig. 2, PDF p. 2 |
| Tactile의 실효 신호 구별 수준 | 실제 환경을 이동할 때의 잡음 기준 | 잡음과 구분할 수 있는 최소 신호 변화 약 0.5 N | §III-A. 축별 분해능·정확도로 보고된 값은 아님 |
| Wrench | 내장 joint-torque sensing을 활용하는 Flexiv 명령 | Dynamics-compensated 6D wrench, suction cup에 둔 TCP frame 표현 | §III-A, Fig. 3, PDF p. 3 |
| Wrench의 실효 신호 구별 수준 | 팔의 움직임으로 발생하는 잡음 기준 | 힘 성분에서 약 3.3 N의 변화가 안정적으로 검출 가능. 컵 위치의 moment는 작다고 서술 | §III-A. 토크 분해능이나 6축 공통 정확도가 아님 |
| Proprioception | 로봇 joint encoder로 TCP pose 구성 | 위치 3성분 + quaternion 4성분. 모든 관절각을 정책에 직접 넣는다고 명시하지 않음 | §III-A, Fig. 3 |
| 흡착 압력 | Suction line 압력 측정 | Gauge pressure가 −6.9 kPa, 약 −0.07 bar보다 낮으면 acquisition bit가 1 | §III-A. 압력 센서 모델·분해능 미명시 |

**별도의 손목 장착형 F/T 센서를 사용한다고 분류하지 않는다.** 원문이 `force-torque`, `wrench sensing`이라고 부르는 정보의 하드웨어 원천은 팔의 관절 토크 센싱과 내장 추정 기능이다. 분포형 tactile은 별도의 실제 센서다. [원문 Abstract, §III-A, PDF pp. 1–3]

### 3.3 원문에서 확인되지 않는 계측 사양

| 항목 | 확인 결과 |
| --- | --- |
| Tactile 축별 최대 측정 범위·과부하 한계 | 미명시 |
| Tactile taxel 간격·감지 면적·위치 정확도 | 미명시. 98개라는 개수만으로 mm 단위 공간 해상도를 계산할 수 없음 |
| Tactile 정확도·선형성·히스테리시스·대역폭 | 미명시 |
| Tactile의 물리적 변환 원리·재료 세부 | 본문은 soft triaxial array로 설명하고 [35]를 인용. 상세 구조를 다른 자료에서 가져오지 않음 |
| Wrench 최대 측정 범위·moment 검출 성능 | 미명시 |
| Wrench 내부 dynamics compensation 모델·gain·filter | 미명시 |
| 카메라·압력 센서의 정량 성능 | 입력 영상 크기와 acquisition threshold 외 미명시 |
| 각 감각의 timestamp 동기화·지연·dropout 처리 | 미명시 |

뒤에서 나오는 **전단력 ±1 N·법선력 0→−5 N은 영상 변환 범위**, **26 N·6 N은 과업 판정 기준**이다. 둘 다 하드웨어 최대 측정 범위가 아니다. [원문 §III-B, §IV-B, PDF pp. 3–4]

## 4. 과업 환경과 성공 조건

### 4.1 선반 배치 생성

| 항목 | 원문 설정 |
| --- | --- |
| 선반 크기 | 38 cm × 53 cm, 높이 32 cm |
| 배치 후보 | 5×7 grid |
| 목표 물체 | 장면에서 유일한 빨간 물체. 세 종류 중 하나를 선택 |
| 목표 위치 | 캐비닛 맨 뒤의 가운데 세 grid cells 중 하나 |
| 주변 장애물 | 네 종류로 25–28개를 배치. 빈 cell도 가능 |
| Sampling | 선택에 uniform random sampler 사용 |
| 점유율 | 바닥 면적의 45–55% |
| 조합 수 | 저자들은 약 10의 20제곱에 해당하는 가능한 이산 배치를 제시. 실제 학습·평가 장면 수가 아님 |

원문은 뒤쪽 모서리에 목표를 두면 주변 장애물을 여러 차례 흡착해 옮기는 등의 다른 전략이 필요할 수 있다고 설명한다. **실제 평가 목표 위치는 뒤쪽 가운데 세 칸으로 제한**되어 있다. [원문 §IV-A, Fig. 4, PDF p. 4]

### 4.2 물체 종류와 footprint

| 역할 | 원문 구분 | 바닥 투영 면적 |
| --- | --- | ---: |
| 빨간 목표 | Cardboard tea box | 55.87 cm² |
| 빨간 목표 | Aluminum can, 첫 번째 형상 | 34.25 cm² |
| 빨간 목표 | Aluminum can, 두 번째 형상 | 25.87 cm² |
| 장애물 | Blue type | 34.26 cm² |
| 장애물 | Green type | 26.32 cm² |
| 장애물 | Black type | 40.97 cm² |
| 장애물 | Yellow type | 57.03 cm² |

모든 물체의 높이·질량·마찰계수·정량 강성은 보고하지 않는다. Fig. 4(a)는 배치용 schematic이고, 그 배치를 실제 물체로 구성한 것이 Fig. 4(b)다. **이 도식은 정책의 occupancy-grid 관측이나 시뮬레이션 학습 환경이 아니다.** [원문 §IV-A, Fig. 4, PDF p. 4]

### 4.3 과업의 시작과 완료

로봇은 선반 앞의 home position에서 시작한다. 빨간 목표를 찾고, 주변 물체와 접촉하며 접근하고, suction cup으로 획득한 뒤 home으로 가져와 검은 선으로 표시한 영역에 내려놓아야 한다. 제한 시간은 **120초**다. 10 Hz이므로 timeout episode는 약 1,200 action steps가 된다. [원문 §IV-B, Fig. 4(c)–(d), PDF p. 4]

따라서 성공은 단순히 접근하거나 흡착 신호가 발생하는 것이 아니다. **목표를 실제로 꺼내 지정 영역에 내려놓는 전체 과업**이다. 과도한 impulse 실패 조건도 함께 적용된다.

정책은 실행 중 eye-in-hand 영상을 계속 관측한다. 목표가 처음부터 보이지 않는 장면도 있지만, 이를 초기 관측만으로 실행하는 blind policy로 해석하지 않는다. 목표의 정확한 pose를 별도의 입력으로 받는 구성도 제시되지 않는다. [원문 §III-B, §IV-C, PDF pp. 3, 5]

## 5. 힘 처리 I — 분포형 3축 촉각을 이미지로 바꾸는 방법

### 5.1 실제 촉각 데이터와 입력 크기

두 센서의 **49 taxels × 2 × 3축 = 294개 힘 성분**을 사용한다. 각 센서에 zero-force taxel 하나씩을 padding하여 센서당 50개로 만든 뒤, 전체를 **20×5 pixels의 3채널 이미지**로 표현한다. 실측 taxel 98개와 padded pixels 100개를 구분한다. [원문 §III-A–B, Fig. 2–3, PDF pp. 2–3; 성분 수는 원문 개수에서 계산]

이 영상은 피부 내부 카메라로 촬영한 optical tactile image가 아니다. **뉴턴 단위로 얻은 분포형 힘을 색상으로 인코딩한 합성 표현**이다. 촉각 feature가 유지되도록 각 pixel을 taxel 하나와 대응시킨다.

### 5.2 채널·부호·변환 범위

| 입력 성분 | RGB에서의 채널 | 힘에서 pixel intensity로의 대응 | 의미 |
| --- | --- | --- | --- |
| x shear | B, blue | −1 N→0, +1 N→255 | 전단력 방향과 크기 |
| 왼쪽 y shear | G, green | −1 N→0, +1 N→255 | 왼쪽 센서의 y 전단 |
| 오른쪽 y shear | G, green | 왼쪽과 force range를 뒤집음 | 도구의 위쪽 방향이 양쪽 모두 intensity 증가에 대응하도록 정렬 |
| z normal | R, red | 0 N→0, −5 N→255 | 원문의 법선 부호에서 압축이 커질수록 red intensity 증가 |

즉 **x·y·z→B·G·R**이며 x·y·z→R·G·B가 아니다. Fig. 2(a)의 양쪽 센서 좌표계와 Fig. 2(c)의 이미지 대응을 함께 보아야 한다. [원문 §III-B, Fig. 2, PDF pp. 2–3]

오른쪽 y축 반전은 서로 다른 쪽에 붙은 센서의 방향 표현을 맞추는 전처리다. 이 과정을 거쳐 비슷한 물리 방향의 전단 변화가 양쪽 영상에서 일관된 색 변화로 표현된다. 다만 전체 taxel ordering·reshape·좌우 결합 코드까지 공개한 것은 아니다.

### 5.3 Zero force, padding, ablation mask는 다르다

원문에 따르면 **전단력 0 N은 B와 G에서 intensity 127**에 대응한다. 법선력 0 N은 R=0이다. 따라서 무접촉을 나타내는 물리적 zero-force 값이 반드시 검은 pixel인 것은 아니다. 원문의 값과 채널 순서를 따르면 RGB의 기준색은 대략 (0, 127, 127)이다. [원문 §III-B, Fig. 2(c), PDF pp. 2–3]

논문은 ablation에서 감각 정보를 zero values로 masking한다고 설명하지만, 이것이 정규화 전 raw force, 입력 영상, encoder feature 중 어느 tensor에 적용되는지까지 밝히지는 않는다. **무접촉의 색상 기준과 입력 모달리티를 제거하는 zero mask를 동일한 것으로 단정하지 않는다.** [원문 §V-A, PDF p. 5]

### 5.4 영상화로 보존하는 정보와 미명시 처리

이 표현은 힘을 하나의 Boolean contact flag 또는 하나의 peak 값으로 줄이지 않고, **어느 taxel에서 어느 방향으로 얼마나 힘이 변하는지**를 이미지 encoder에 전달한다. 다만 ResNet이 그로부터 계산하는 feature의 물리적 의미나 jam·slip 분류 결과를 명시적으로 감독하는 모듈은 없다. [원문 §III-B, Fig. 2–3, PDF pp. 2–3]

다음은 원문이 설명하지 않는 부분이다.

| 세부 처리 | 확인 결과 |
| --- | --- |
| 범위를 벗어난 전단·법선력의 clipping·saturation·다른 처리 | 미명시 |
| Integer rounding 방식 | 미명시. 원문의 0 N→127을 그대로 기록 |
| Raw tactile의 영점 조정·필터·cross-axis compensation | 미명시 |
| 20×5 이미지를 ResNet에 넣기 위한 resize·crop·channel normalization | 미명시 |
| Taxel의 정확한 pixel index와 padding 위치 | 본문은 sensor당 하나의 padding 및 Fig. 2 대응만 제시 |
| Tactile history에 대한 별도 temporal encoder | 미명시. 다중감각 observation history는 Diffusion Policy에 전달 |

**영상 변환 범위가 ±1 N 또는 −5 N이라고 해서 그 힘을 넘는 접촉을 센서가 측정하지 못한다고 판단할 수 없다.** 후술하는 6 N threshold는 3축 힘의 norm이며, 영상 채널 범위와 다른 양이다.

## 6. 힘 처리 II — TCP wrench와 흡착 상태

### 6.1 Wrench 생성과 정책 입력

Flexiv의 joint-torque sensing 기반 내장 기능으로 **dynamics-compensated wrench**를 얻고 suction cup의 TCP frame으로 표현한다. Fig. 3의 입력은 다음 6성분이다. [원문 §III-A, Fig. 3, PDF p. 3]

**원문 관측 구성의 재표기**

$$
\mathbf{w}_t=[f_x,f_y,f_z,\tau_x,\tau_y,\tau_z]_t.
$$

이 값은 normalization 후 proprioception·pressure와 함께 저차원 feature로 연결된다. 정책에는 wrench 전체가 들어가지만, 과도한 힘을 판정하는 net-force 지표는 **앞의 힘 3성분만** 사용한다. 토크 성분에 별도 failure threshold를 두었다는 설명은 없다. [원문 §III-B, §IV-B, PDF pp. 3–4]

원문은 내장 compensation을 사용한다고만 밝힌다. 관절 토크에서 외력으로 변환하는 Jacobian 계산, 센서 바이어스·중력·부하 보상의 개별 식이나 filter 계수를 새로 만들어 보충하지 않는다.

### 6.2 왜 tactile과 같은 정보가 아닌가

저자들은 두 힘 감각이 상보적이라고 설명한다. 여러 접촉이 동시에 생기면 wrench는 개별 접촉의 크기를 분리하지 못한다. 반면 tactile은 측면의 특정 taxel에서 큰 국소 접촉을 볼 수 있지만, 로봇 팔 전체를 덮지 않으므로 일부 접촉을 놓친다. 따라서 net-force 기준과 peak-tactile 기준을 둘 다 둔다. [원문 §IV-B, PDF p. 4]

이는 **합력 관측의 국소 정보 부족과 부분 tactile coverage**의 차이다. 본문은 두 센서로 모든 접촉 위치를 역산하거나 개별 물체 ID를 복원하는 estimator를 제시하지 않는다.

### 6.3 흡착 획득 상태

정책의 pressure 입력은 raw pressure history 자체가 아니라 **binary grasp acquisition value**로 설명된다. Gauge pressure가 −6.9 kPa보다 낮으면 1이 된다. [원문 §III-A, PDF p. 3]

**원문 규칙의 해설용 재표기**

$$
b_t=\begin{cases}
1,&p_{\mathrm{gauge},t}<-6.9\ \mathrm{kPa},\\
0,&\text{그 외}.
\end{cases}
$$

이 값은 suction을 켜라는 행동 명령과 구분한다. $g_i$는 밸브를 제어하는 명령이고, acquisition bit는 압력으로부터 얻는 관측이다. 압력 센서의 정확한 모델·범위·필터·hysteresis·debouncing과 target 종류 판정 능력은 보고하지 않는다.

## 7. 상세 핵심 메소드 — 다중감각 Diffusion Policy

### 7.1 네트워크 구조

Fig. 3의 연결은 다음과 같다. [원문 §III-B, Fig. 3, PDF p. 3]

```text
Eye-in-hand camera image (128×128×3)
  → 영상 전용 pretrained ResNet-18 ─────┐
                                      │
Tactile force image (20×5×3)            │
  → 촉각 전용 pretrained ResNet-18 ────┤
                                      ├→ observation feature
TCP pose (7), wrench (6), pressure (1) │       + 과거 observations
  → normalization ────────────────────┘
                                              ↓
                                        Diffusion head
                                              ↓
                               TCP position + quaternion + suction
                                              ↓
                                         Robot controller
```

카메라와 tactile은 **각각 별도의 ResNet-18 encoder**를 거친다. 저자들은 [5]의 결과에 근거해 raw 고차원 tactile을 직접 처리하는 대신 시각적 embedding을 사용하고, ResNet 선택의 근거로 [5], [37]을 인용한다. 이 논문 자체에서 모든 tactile encoder 후보를 비교한 것은 아니다.

### 7.2 Observation의 구성과 정보 경계

| 입력 | 차원·표현 | 들어가지 않는 것으로 구분할 정보 |
| --- | --- | --- |
| Visual feature | 128×128 RGB를 별도 encoder로 처리 | Overhead view, scene schematic의 grid가 아님 |
| Tactile feature | 20×5×3 힘 영상을 별도 encoder로 처리 | 안전용 peak 하나만을 입력하는 구조가 아님 |
| Wrench | 6차원 | 외장 손목 F/T 센서의 raw 출력을 가정하지 않음 |
| TCP pose | 7차원 | 7개의 로봇 관절각이라는 뜻이 아님 |
| Grasp acquisition | 1차원 binary | Suction command 자체나 목표 물체 ID가 아님 |

저차원 입력은 합계 14성분이다. **전체 observation dimension은 두 encoder의 출력 차원과 history 길이를 더 알아야 계산 가능**하므로 확정하지 않는다. Fig. 3는 현재와 이전 observations의 사용을 보여 주지만, 정확한 observation horizon을 본문 수치로 제시하지 않는다.

### 7.3 행동의 정확한 형태

**원문 식 (1)**

$$
A_i=[x_i,y_i,z_i,q_{x,i},q_{y,i},q_{z,i},q_{w,i},g_i].
$$

앞의 3개는 명령 Cartesian 위치, 다음 4개는 명령 quaternion, 마지막은 흡착을 제어하는 binary command다. 따라서 **힘 목표값·임피던스·stiffness를 직접 출력하는 정책이 아니다.** [원문 §III-B, 식 (1), PDF p. 3]

8차원 형식과 실제 자유도도 구분해야 한다. Quaternion 4개는 독립적인 회전 자유도 4개가 아니다. 시연에서는 x·y·z·yaw를 조작하고 roll·pitch를 고정하지만, 학습 행동의 저장 형식은 위 8성분이다. 실행 시 roll·pitch를 강제로 제한하는 별도 코드가 있는지는 본문에 설명되지 않는다. [원문 §IV-C, PDF p. 5]

### 7.4 힘이 행동까지 연결되는 방식

본 연구의 정책 경로는 **측정 힘→학습된 observation feature→시연에서 학습한 action sequence**다. 예를 들어 힘 증가를 보고 시연자가 군집에서 물러나거나 방향을 바꾸는 장면을 학습에 포함한다. 이때 힘 관측이 제거된 정책과 유지된 정책의 실제 반응을 비교한다. [원문 §IV-C, §V-B, PDF pp. 5–6]

본문은 다음 중간 모듈을 제안하지 않는다: 명시적 jam classifier, slip estimator, 물체 pose 추정기, 접촉별 힘 분배 optimizer, force PID, admittance law. 시연자가 사용한 동작 전략이 있다고 해서 이를 실행 정책의 hand-coded state machine으로 해석해서도 안 된다.

따라서 논문의 설명력은 학습 정책 내부의 물리 상태를 완전히 해석한 데 있지 않다. **동일한 데이터·학습 구조에서 관측 감각을 바꾸고, 성능과 힘 이후 운동이 어떻게 달라졌는지 실제 실험으로 보인 것**이 근거다.

### 7.5 RL·GAN·시뮬레이션 여부와 공개 수준

| 질문 | 원문에서 확인한 답 |
| --- | --- |
| RL인가? Reward가 있는가? | 현재 방법은 실제 시연 기반 imitation learning. RL reward는 제시하지 않음 |
| GAN 또는 real-to-sim translation을 쓰는가? | 제시하지 않음. Force image는 측정값의 채널 인코딩 |
| 시뮬레이션 학습 환경인가? | 실제 캐비닛에 생성한 배치를 구성해 실제 로봇 시연·평가. 시뮬레이션 policy training을 제시하지 않음 |
| 학습 구조 | Diffusion Policy [34], 두 pretrained ResNet-18, normalized 저차원 입력 |
| 학습 데이터와 반복 | 100개 시연, 각 정책 200 epochs |
| 실행 시간 구성 | 10 Hz sampling, 8 action steps를 기준으로 0.8초 반응 구간 설정 |
| 상세 diffusion 학습식 | 본문에 optimizer loss·noise schedule·denoising 식을 전개하지 않음 |
| 기타 hyperparameter | Learning rate, batch size, optimizer, prediction/observation horizon, denoising 횟수·scheduler, checkpoint 선택 등 미명시 |
| Encoder 학습 여부 | Pretrained라고 명시하지만 freeze/fine-tune·사전학습 데이터·최종 feature 차원은 미명시 |

[원문 §III-B, §IV-B, §V-A, PDF pp. 3–5]

## 8. 힘 처리 III — Gentleness를 정의하는 impulse 기준

### 8.1 왜 순간 힘뿐 아니라 시간창을 사용하는가

로봇과 시연자에게 접촉에 반응할 시간을 주기 위해, 최근 반응 구간에서 평균한 힘에 반응 시간을 곱한 **scalar impulse 지표**를 사용한다. 목표는 물체를 건드리지 않는 것이 아니라, 접촉에 반응하지 못한 채 큰 힘을 유지하는 행동을 제한하는 것이다. [원문 §IV-B, PDF p. 4]

### 8.2 Net force와 peak tactile force의 계산

**원문 식 (2)**

$$
I_{\mathrm{net}}=F_{\mathrm{net}}\delta t_{\mathrm{react}}.
$$

여기서 측정값으로서의 net force는 wrench의 힘 3성분에 대한 L2 norm을 구한 뒤, 직전 반응 시간 동안 평균한 값이다. **3축 벡터를 시간 평균한 뒤 norm을 취한다고 쓰지 않는다.**

**원문 식 (3)**

$$
I_{\mathrm{peak}}=F_{\mathrm{peak}}\delta t_{\mathrm{react}}.
$$

Peak force는 모든 taxel 각각의 3축 힘 norm 중 최댓값을 구하고, 그 최댓값을 직전 반응 시간 동안 평균한 값이다. 즉 **공간상 max→시간 평균**의 순서다. Taxel 전체 힘의 합이나 평균, 법선 성분만의 최대가 아니다. [원문 §IV-B, 식 (2)–(3), PDF p. 4]

원문은 측정값과 threshold에 비슷한 F 표기를 사용한다. 아래는 순서를 설명하기 위해 측정 norm을 $u$, $v$로 새로 표기한 해설이다.

$$
u_t=\lVert\mathbf{w}_{t,1:3}\rVert_2,\qquad
v_t=\max_j\lVert\mathbf{f}_{j,t}\rVert_2.
$$

10 Hz에서 충분한 8-sample 창이 확보되었다고 해석하면, 동일한 평균×시간 관계는 다음 이산 합으로 쓸 수 있다. 이는 **원문 정의의 대수적 설명이며 실제 코드 확인 결과가 아니다.**

$$
I_{\mathrm{net},t}=\frac{1}{f_s}\sum_{k=0}^{7}u_{t-k},\qquad
I_{\mathrm{peak},t}=\frac{1}{f_s}\sum_{k=0}^{7}v_{t-k}.
$$

초기 미충족 window, sample 누락, 보간 등은 원문에 미명시다. 또한 시간에 따라 최대 taxel이 바뀔 수 있으므로, peak 지표를 특정 한 접촉점의 누적 impulse로 단정하지 않는다.

### 8.3 왜 두 종류의 제한이 필요한가

저자들이 제시한 이유는 다음과 같다. [원문 §IV-B, PDF p. 4]

| 기준 | 필요성 | 단독 사용의 한계 |
| --- | --- | --- |
| Peak tactile impulse | 특정 물체를 손상시킬 가능성이 큰 국소 최대 접촉을 감시 | Tactile이 덮지 않은 팔·도구 접촉을 감지하지 못할 수 있음 |
| Net wrench impulse | Tactile coverage 밖의 접촉까지 고려할 전역 부하 기준 | 동시 다중 접촉의 개별 크기를 분리하지 못함 |

정책 입력으로 두 센서를 주는 선택과, **실험 안전·종료 판단에 두 센서 측정을 사용하는 선택은 별개**다. 정책에서 masking했다고 실제 센서까지 제거하는 실험은 아니다.

### 8.4 Threshold의 실험적 설정

저자들은 plastic cup과 장면에 쓰는 yellow cardboard tea box를 대상으로 손상이 발생하는 접촉 시험을 수행한다. Tea box는 cardboard의 buckling 또는 tearing, cup은 cracking이 발생할 때 멈춘다. 각 물체에 세 번씩 반복해 시험별 최대 net force와 peak tactile force를 얻고, 전체 시험에서 평균한 뒤 정수로 올림하여 기준을 정한다. [원문 §IV-B, PDF p. 4]

| 양 | 사용한 값 | 성격 |
| --- | ---: | --- |
| Net-force magnitude threshold | 26 N | 해당 물체·환경에 맞춘 기준 |
| Peak-tactile magnitude threshold | 6 N | Taxel별 3축 norm의 peak에 대한 기준 |
| Action steps | 8 | 반응 구간 설정의 근거 |
| Sampling rate | 10 Hz | 시스템 설정 |
| 반응 시간 | 0.8 s | 8/10으로 설정 |
| Net impulse 제한 | 20.8 N·s 미만 | 26×0.8 |
| Peak impulse 제한 | 4.8 N·s 미만 | 6×0.8 |

이 값들은 **센서 최대 측정 범위나 보편적 안전 한계가 아니다.** 저자들도 다른 과업 전체에 적용할 수 있는 힘이 아니라고 명시한다. 이 정리는 원문의 실험 설정을 설명하는 것이며, 다른 장비·물체에서 같은 한계를 사용하라는 권고가 아니다.

### 8.5 반응 시간·정지 기준을 읽을 때 주의할 점

**0.8초는 action chunk와 sampling rate로 정한 반응 구간이지, 신경망 순전파에 0.8초가 걸린다는 측정값이 아니다.** 또한 26 N 또는 6 N을 한 sample에서 넘으면 즉시 failure라고 정의한 것이 아니라, 위 시간창의 impulse가 기준을 넘는지를 사용한다. [원문 §IV-B, PDF p. 4]

원문의 impulse는 힘 norm에 기반한 비음수 scalar다. 이를 방향까지 포함한 실제 물체의 운동량 변화 또는 모든 순간 접촉력이 안전하다는 수학적 보증과 동일시하지 않는다. 원문은 이 지표를 해당 과업에서 gentleness를 평가하는 실용적 제한으로 사용한다.

## 9. 시연 수집과 학습 데이터

### 9.1 시연자가 조작·관측하는 것

SpaceMouse의 x·y·z·yaw 신호를 TCP 명령의 증분으로 매핑하고 roll·pitch는 고정한다. 왼쪽 버튼은 solenoid를 vacuum pump 쪽으로 연결해 suction을 켜고, 오른쪽 버튼은 대기압으로 연결해 물체를 빠르게 해제한다. [원문 §IV-C, PDF p. 5]

시연자는 실제 장면을 밖에서 직접 보는 대신 다음 화면을 사용한다: eye-in-hand 영상, tactile image, pressure 정보, excessive-force warning image. Fig. 5에서 카메라에 보이지 않는 오른쪽 측면 접촉이 빨간 경고로 표시된다. [원문 Fig. 5, §IV-C, PDF p. 5]

경고 영상은 좌·중·우로 나뉜다. 좌우는 각 측면의 peak tactile force, 가운데는 joint-torque 기반 net force다. 각 기준의 0–80%에서는 검정→흰색으로 표시하고 **80%를 넘으면 해당 부분을 빨갛게 표시**한다. 시연자가 반응할 시간을 확보하되 필요한 접촉에서 과도한 false positive를 피하도록 경험적으로 조정했다. [원문 §IV-C]

이 경고 영상은 **시연용 인터페이스**다. Fig. 3의 정책 입력에 별도 warning-image encoder가 추가되어 있지는 않다. Kinesthetic force reflection이나 haptic sleeve로 힘을 전달한 시스템도 아니다. 그 장치는 Future Work다.

### 9.2 일관된 시연을 위한 행동 기준

다음은 저자들이 시연자에게 적용한 전략이며, **실행 정책의 명시적 상태기계가 아니다.** [원문 §IV-C, PDF p. 5]

| 관측 상황 | 시연 전략 |
| --- | --- |
| 시작부터 빨간 목표가 보임 | 목표를 향해 직접 전진 |
| 처음에는 목표가 가려짐 | 장면마다 전방-왼쪽 또는 전방-오른쪽 접근을 번갈아 선택 |
| 이동 중 목표가 보이기 시작함 | 목표 방향으로 진행 재개 |
| 방해 물체가 진로를 차지함 | 주변 물체를 밀어 공간을 내며 대략 sinusoidal한 snaking motion 수행 |
| 군집이 벽에 걸려 큰 힘 경고 발생 | 군집에서 멀어지며 목표를 향하도록 재정렬 |
| Jamming이 지속되어 진로가 없음 | 입구까지 후퇴한 뒤 다른 위치로 재진입 |
| 목표가 분리·접근 가능한 상태가 됨 | 흡착 획득 후 최종 위치까지 인출 |

이 과정 때문에 시연자의 행동을 설명하려면 시각뿐 아니라 힘 정보도 중요할 수 있다. 저자들은 후술한 Discussion에서 이를 causal confusion 가설로 연결한다.

### 9.3 데이터 수집·학습 조건

무작위 장면에서 **100개 시연**을 수집한다. 두 impulse 중 하나라도 한계를 넘으면 시연을 자동 종료하고 해당 장면을 다시 수집한다. 과도한 힘 사례를 그대로 성공 시연으로 사용하는 것이 아니다. [원문 §V-A, PDF p. 5]

네 정책은 이 시연들과 같은 architecture·hyperparameter를 사용하며, **각각 200 epochs** 학습한다. 차이는 제공하는 wrench·tactile 정보의 mask다. 시연 전체를 모으는 시간, 폐기·재시도 수, train/validation 분할, 전체 frame 수, 학습 seed 수와 여러 seed에 걸친 평균은 미명시다.

이 실험에서는 기준선용 시연자가 힘 없이 별도로 시연하지 않는다. **힘 정보를 보고 만들어진 동일 시연에서, 학습 정책에게 주는 감각 정보만 다르게 한다.** 이 조건은 결과와 Discussion을 해석할 때 유지해야 한다. [원문 §IV-C–V-A, PDF p. 5]

## 10. Force ablation의 설계

### 10.1 네 정책의 입력 차이

| 정책 | Eye-in-hand vision | TCP pose | Acquisition pressure bit | Wrench | Tactile |
| --- | --- | --- | --- | --- | --- |
| Baseline | 유지 | 유지 | 유지 | 0으로 mask | 0으로 mask |
| Wrench-informed | 유지 | 유지 | 유지 | 유지 | 0으로 mask |
| Tactile-informed | 유지 | 유지 | 유지 | 0으로 mask | 유지 |
| Wrench + tactile | 유지 | 유지 | 유지 | 유지 | 유지 |

학습 때와 평가 때 같은 masking을 적용한다. 네트워크 모듈을 삭제해 parameter 수까지 줄인 실험이 아니라, 동일 architecture에 대한 감각 정보 masking으로 설명한다. **Baseline은 vision-only가 아니며, suction pressure까지 제거한 조건도 아니다.** [원문 §V-A, PDF p. 5]

### 10.2 평가 절차와 supervisor

새 무작위 장면 하나를 만들면 네 정책을 같은 장면에서 평가한다. 이를 **40개의 unseen environment configurations**에 대해 반복하므로, 정책별 40회·전체 160회의 평가다. 성공·timeout·과도한 힘 실패 조건은 공통이다. [원문 Abstract, §V-A–B, PDF pp. 1, 5–6; 총합은 계산]

Masking은 policy input에 적용된다. **평가용 impulse 계산과 Fig. 7의 분석에는 실제 측정 힘이 필요하므로, ‘힘 관측이 없는 정책’과 ‘실험 시스템에 힘 센서가 없는 상태’를 구분한다.** 논문은 baseline에서도 excessive-force failures와 wrench·tactile 반응을 평가한다.

Unseen은 새 배치의 장면을 뜻한다. 장애물·목표의 OOD 종류까지 검증했다는 뜻은 아니다. 정확한 실물 재배치 오차, 평가 순서 randomization, seed별 반복 학습은 보고하지 않는다.

## 11. 실험 결과 — 성공, 실패 유형, 시간

### 11.1 Fig. 6(a)의 전체 결과

아래 횟수는 **PDF p. 6의 Fig. 6(a)에 직접 적힌 값**이다. 괄호의 백분율은 각 값을 40으로 나눈 계산이다. [원문 §V-B, Fig. 6(a), PDF pp. 5–6]

| 정책 | 성공 | Timeout 실패 | Excessive-force 실패 |
| --- | ---: | ---: | ---: |
| Baseline | 15/40 (37.5%) | 10/40 (25.0%) | 15/40 (37.5%) |
| Wrench-informed | 24/40 (60.0%) | 9/40 (22.5%) | 7/40 (17.5%) |
| Tactile-informed | 24/40 (60.0%) | 9/40 (22.5%) | 7/40 (17.5%) |
| Wrench + tactile | 27/40 (67.5%) | 2/40 (5.0%) | 11/40 (27.5%) |

저자들이 말하는 **80% improvement는 성공률 자체가 80%라는 뜻이 아니라 baseline 대비 상대 증가율**이다.

**Fig. 6(a) 값으로 계산한 해설**

$$
\frac{27-15}{15}\times100=80\%.
$$

절대 성공률은 37.5%→67.5%, 즉 **30 percentage points 증가**다. 두 단일 감각 정책은 각각 상대 60% 증가다.

### 11.2 ‘병용이 가장 좋다’의 정확한 뜻

병용 정책은 전체 성공이 가장 많고 timeout이 가장 적다. 그러나 **과도한 힘 실패는 단일 감각 정책의 7회보다 많은 11회**다. Baseline의 15회보다는 적지만, 모든 지표에서 병용이 최선은 아니다. [원문 Fig. 6(a), §VI, PDF pp. 6–7]

저자들은 이 과도한 힘 실패 차이가 통계적으로 유의하지 않으며 우연일 수 있다고 설명한다. 추가 가설로, 모달리티가 늘면 데이터 효율이 떨어질 수 있고 100개 시연이 병용 정책에 부족했을 가능성을 제시한다. **‘두 센서를 결합하면 힘 안전성이 더 나빠진다’거나 ‘데이터 부족이 원인으로 입증됐다’고 결론 내리지는 않는다.**

### 11.3 통계 표기

Fig. 6(a)의 별표는 baseline과의 양측 pairwise z-test에서 p<0.05임을 나타낸다. 단검 표시는 wrench+tactile 정책과의 양측 pairwise z-test에서 p<0.05라는 뜻이다. 성공 막대에는 force-informed 세 정책의 별표가 있고, timeout 막대에는 병용 이외 정책의 단검이 표시된다. [원문 Fig. 6 caption, PDF p. 6]

그러나 **27/40과 24/40 사이의 성공률 차이가 통계적으로 유의하다고 따로 보고하지 않는다.** 원문에 없는 정확한 p-value, confidence interval, 다중비교 보정이나 다른 검정 결과를 덧붙이지 않는다.

### 11.4 Timeout을 일으킨 행동

병용 이외 정책들에서 다음 행동을 관찰했다고 보고한다: 큰 접촉력이 없는데도 물체에서 물러남, 목표를 고립시킨 뒤에도 목표에 집중하지 못함, 목표 없이 후퇴함. Baseline에서 timeout이 가장 많았다. 구체 영상은 보충자료에 있다고 안내하지만, 이번에는 영상을 직접 확인하지 않았다. [원문 §V-B, PDF p. 6]

### 11.5 성공 시간

Fig. 6(b)는 **성공한 trial의 완료 시간**과 standard error를 보여 준다. Force-informed 세 정책은 모두 baseline보다 빠르며, **wrench-informed가 가장 빠르다.** 병용이 가장 빠른 것은 아니다. [원문 §V-B, Fig. 6(b), PDF p. 6]

막대에 정확한 시간 수치가 인쇄되어 있지 않고 본문에도 평균값을 나열하지 않으므로, 초 단위 정밀 수치를 표로 전사하지 않는다. 또한 실패·120초 timeout까지 포함한 전체 평가 평균 시간과 성공 시간은 다르다.

## 12. 힘에 실제로 반응했는가 — 후속 운동 분석

### 12.1 성공률에서 더 나아간 분석

저자들은 모든 정책의 모든 평가 timestep에서 측정한 힘과 **그 뒤 0.8초 동안의 말단 변위**를 연결한다. 한 번의 inference cycle에 해당하는 반응 시간을 주고 큰 힘을 본 뒤 움직이는지 확인하기 위한 분석이다. [원문 §V-B, Fig. 7, PDF p. 6]

Fig. 7은 net force와 peak tactile force 각각에 대한 heatmap이다. 가로축은 측정 힘, 세로축은 이후 운동 크기이며, 오른쪽 아래는 **큰 힘에도 거의 움직이지 않은 sample**이다. 기준 힘은 검은 점선으로 표시된다.

Baseline에서는 이런 sample이 많고, force-informed 정책은 힘이 커졌을 때 작은 운동에 머무르는 sample이 줄어든다. Tactile-only에서는 큰 peak force에 비해 운동이 작은 sample이 wrench-only·병용보다 더 남는다. 저자들은 이를 큰 힘 대응에서 wrench sensing이 특히 효과적이라는 관찰로 설명한다.

### 12.2 Failed reaction의 정의와 횟수

Net force가 26 N 기준을 넘거나 peak tactile force가 6 N 기준을 넘었는데, 후속 변위가 **0.5 cm 미만**이면 failed reaction으로 집계한다. [원문 §V-B, PDF p. 6]

| 정책 | Failed reaction instances |
| --- | ---: |
| Baseline | 412 |
| Wrench-informed | 17 |
| Tactile-informed | 72 |
| Wrench + tactile | 22 |

이 결과는 **‘센서를 넣었더니 성공했다’뿐 아니라, 큰 힘 이후 움직이지 않는 반응 실패가 줄었다**는 행동 수준의 증거를 제공한다. 다만 wrench-only가 이 집계에서 가장 작고, 전체 과업 성공은 병용이 가장 높다. 하나의 지표로 모든 성능을 대신할 수 없다.

### 12.3 이 지표가 보여 주지 않는 것

다음은 저자들의 한계 목록과 별개로, 보고된 지표의 정의에서 따라오는 해석 범위다.

**412는 실패 episode 수가 아니다.** 전체 timestep에 대한 instance 집계이며, 같은 접촉에서 시간상 연속된 sample이 포함될 수 있다. 정책별 총 sample 수·episode 길이로 정규화한 독립 접촉 사건의 실패 확률로 바꾸지 않는다.

또한 후속 변위의 크기는 힘을 낮추는 방향으로 움직였는지, 힘이 얼마나 감소했는지, 실제 물체 손상이 방지됐는지를 직접 측정하지 않는다. **Fig. 7은 force–motion 관계의 분석이지 명시적 causal mechanism·접촉 해소 방향 제어의 증명은 아니다.** 원문은 이 결과와 최종 성능을 함께 사용해 반응성 개선을 논의한다.

## 13. Discussion — 저자들의 해석과 가설

### 13.1 Causal confusion의 가능성

시연자는 힘 경고를 보고 물러나거나 방향을 바꾼다. 그런데 학습 정책에서 그 힘 모달리티를 가리면, 정책은 시연자의 행동을 유발한 관측 일부를 보지 못한다. 저자들은 실제 원인이 되는 힘 정보를 제공함으로써, 관련 없는 시각적 distractor와 행동 사이의 우연한 상관에 의존하는 **causal confusion**이 줄어들 수 있다고 해석한다. [원문 §VI, PDF pp. 6–7]

[38]은 nuisance factor를 제거하는 관점으로 인용되고, 본 논문은 반대로 **행동의 진짜 원인일 수 있는 관측을 추가하는 것**을 대안으로 제안한다. 다만 저자들은 이 상관을 검증할 **추가 실험이 필요하다**고 명시한다. 이번 ablation으로 인과적 원인이 완전히 식별되었다고 주장하지 않는다.

### 13.2 병용의 이득과 데이터 요구량

병용 정책의 timeout 감소와 전체 성공 개선은 감각 정보를 충분히 제공하는 이점으로 설명하지만, excessive-force 실패 증가에는 작은 데이터셋과 다중모달 학습의 데이터 효율 문제가 관여했을 가능성을 제시한다. 이는 [39], [40]을 참고한 설명이며, demonstration 수를 바꾼 추가 실험으로 입증한 결론이 아니다. [원문 §VI, PDF p. 7]

### 13.3 Whole-body sensing의 필요성

저자들은 비구조화 환경에서 파지 표면뿐 아니라 다른 로봇 표면의 예상치 못한 접촉에도 반응해야 한다고 강조한다. 이 논문의 장비가 이미 전신 tactile을 구현했다는 뜻은 아니다. 실제 tactile은 두 측면에 있고, 다른 부위 접촉에 대한 보완 경로는 joint-torque 기반 wrench다. [원문 §VI, PDF p. 7]

## 14. Limitation — 저자들이 밝힌 한계와 적용 범위

독립된 Limitation 절은 없지만 §I Contributions, §IV, §VI, §VII에서 범위와 제약을 밝힌다. 아래는 그 내용을 정리한 것이다. 미기재 hyperparameter 등 정리자의 확인 한계는 다음 절들과 구분한다.

| 저자 명시 한계·범위 | 내용과 결과 해석 | 원문 위치 |
| --- | --- | --- |
| 물체 특성의 독립적인 분석 부족 | 형상 다양성·변형 가능성·광학/분광 변화의 영향을 별도로 조사하지 않음 | §I Contributions, PDF p. 2 |
| 부분 tactile coverage | 두 센서가 팔 전체를 덮지 않아 일부 접촉을 놓침. Net wrench 기준을 함께 두는 이유 | §IV-B, PDF p. 4 |
| 과업별 gentleness threshold | 두 취약 물체 시험으로 얻은 힘 기준은 모든 과업에 적용할 수 없음 | §IV-B, §VII, PDF pp. 4, 7 |
| 목표 종류·배치의 제한 | 빨간 목표 세 종류, 뒤쪽 가운데 세 칸. 모서리 목표는 다른 전략이 필요할 수 있음 | §IV-A, §VII, PDF pp. 4, 7 |
| 적은 시연과 병용의 잔여 힘 실패 | 100개 시연에서 병용의 힘 실패가 단일 모달리티보다 많음. 데이터 효율 또는 우연이라는 가능성을 구분 | §VI, PDF p. 7 |
| Causal confusion 설명의 검증 부족 | 힘 정보를 제공하는 것이 원인-행동 이해를 개선한다는 해석은 추가 실험 필요 | §VI, PDF pp. 6–7 |
| OOD 물체에 대한 별도 검증 미완료 | 새 배치 평가와 달리, 미지 장애물·목표 종류의 robustness 연구를 후속 과제로 제시 | §VII, PDF p. 7 |

## 15. Future Work — 저자들이 제시한 향후 연구

아래는 §VII 및 §VI의 후속 검증 언급을 정리한 것으로, **현 논문에서 이미 구현·검증한 방법이 아니다.** [원문 §VI–VII, PDF p. 7]

| 방향 | 구체적으로 제시한 내용 | 현 상태와 구분 |
| --- | --- | --- |
| 시연자의 haptic feedback | Kinesthetic teleoperation 장치로 wrench를, haptic sleeve [41]로 tactile을 전달 | 현재는 화면 기반 힘 경고·촉각 영상 |
| 촉각에 반응할 자유도 확대 | 하드웨어의 운동 자유도를 늘려 non-prehensile tactile의 가능성 확대 | 현재 시연은 x·y·z·yaw, roll·pitch 고정 |
| Multifingered manipulator | 말단을 다지 손으로 대체 | 더 복잡한 tactile geometry와 새로운 acquisition metric 필요 |
| OOD robustness | 장애물과 목표의 분포 밖 물체를 이용한 추가 검증 | 현재는 고정 물체군의 새로운 배치 평가 |
| 임의 목표 인식 | 빨간 목표만이 아니라 임의 물체를 찾도록 pretrained segmentation network 활용 가능성 | 현 정책에 segmentation network를 넣었다는 뜻이 아님 |
| Adaptive gentleness | 과업별 고정 threshold 한계를 완화하며 control barrier function [42], [43] 검토 | 현재는 고정 impulse threshold이며 CBF 보증 없음 |
| RL fine-tuning | [44]처럼 모방학습 정책을 RL로 추가 개선 | 현재 정책은 RL로 학습하지 않음 |
| 더 반응적인 diffusion architecture | Reactive diffusion policy [45] 같은 구조 검토 | 현재 모델을 해당 구조로 부르지 않음 |
| Custom tactile encoder | [5]처럼 robotic play data로 tactile encoder 학습 | 현재는 pretrained ResNet-18 활용 |
| 다른 control architecture와 비교 | [46]의 model-based low-level force-informed controller와 vision/proprioception 기반 learned planning의 결합과 비교 | 현재 force ablation은 같은 Diffusion Policy 구조 안의 비교 |
| 인과 설명 검증 | 힘 정보 추가가 causal confusion을 줄인다는 관계에 대한 추가 실험 | Discussion의 가설이지 확정 원인 아님 |

## 16. 미명시 정보와 원문 해석 주의사항

### 16.1 재현에 필요한데 본문에 없는 정보

| 구분 | 미명시 항목 |
| --- | --- |
| 센서·도구 | Taxel pitch·면적·장착 치수·coverage 비율·sensor range·정확도·주파수·필터 |
| 입력 전처리 | 힘 영상 clipping·resize·normalization의 상세 값, wrench normalization, masking tensor 위치 |
| 로봇 실행 | Cartesian target의 기준 좌표계 세부, action interpolation·saturation, quaternion 정규화, low-level compliance 설정 |
| Diffusion 학습 | Loss의 실제 구현, noise scheduler, denoising 횟수, optimizer·learning rate·batch size, horizon, encoder freeze 여부 |
| 시연·평가 | 전체 수집 시간·폐기 시연 수·validation split, 독립 학습 seed 수, 장면 재구성 오차·평가 순서 |
| 정량 결과 | 성공 시간의 정확한 숫자, Fig. 7 bin 설정·정규화, 실패 반응의 분모·독립 event 수 |
| 안전 구현 | 초기 rolling window·sample 누락 처리, 정확한 stop command와 정지 지연 |

이 항목들은 해당 기능이 없다는 주장이 아니라 **첨부 논문만으로 구현을 확정할 수 없다는 뜻**이다. 선행 Diffusion Policy나 Flexiv 제품의 일반적인 설정으로 빈칸을 채우지 않는다.

### 16.2 Quaternion 순서

Fig. 3의 proprioception 표시에는 위치 뒤 quaternion이 **qw, qx, qy, qz** 순서로 그려져 있다. 반면 행동을 정의하는 식 (1)은 **qx, qy, qz, qw**다. 관측과 행동의 component ordering이 같다고 임의로 통일하지 않는다. 실제 tensor ordering은 구현을 추가 확인해야 한다. [원문 Fig. 3, 식 (1), PDF p. 3]

### 16.3 자주 혼동하기 쉬운 수치와 주장

| 잘못 읽기 쉬운 표현 | 이 논문에서의 정확한 범위 |
| --- | --- |
| ‘80% 성공’ | 병용의 실제 성공률은 67.5%. 80%는 baseline 대비 상대 개선 |
| ‘병용이 항상 가장 안전하고 빠름’ | 전체 성공은 최고지만 힘 실패는 단일 감각보다 많고, 완료 시간은 wrench-only가 가장 짧음 |
| ‘힘 정보 없는 baseline = vision-only’ | Proprioception·binary pressure는 유지 |
| ‘Tactile 100개’ | 실제 98개, padding 후 100 pixels |
| ‘Tactile은 카메라 영상’ | 3축 힘을 RGB로 매핑한 영상 표현 |
| ‘F/T 센서를 손목에 추가’ | Joint-torque 기반 built-in wrench 추정 |
| ‘0.5 N/3.3 N은 데이터시트 분해능’ | 실제 움직임 중 noise와 구분되는 최소 신호 변화로 보고 |
| ‘26 N/6 N을 넘는 순간 실패’ | 0.8초 창의 평균 힘×시간으로 정의한 impulse 실패 |
| ‘시뮬레이션 10의 20제곱 장면 학습’ | 가능한 배치 조합의 규모. 실제 시연은 100개 |
| ‘40종 미지 물체 평가’ | 40개의 새로운 환경 배치. OOD 물체는 향후 연구 |
| ‘412번 task 실패’ | 후속 변위 기준의 timestep-level failed reaction instances |
| ‘Causal confusion을 해결했음을 증명’ | 저자들이 가능성을 제시하고 추가 검증 필요성을 명시 |

## 17. 원문 위치 안내와 문서 검증 범위

| 다시 확인할 내용 | 원문 위치 |
| --- | --- |
| 문제·기여·물체 특성 분석 범위 | Abstract, §I, PDF pp. 1–2 |
| Related Work | §II, PDF p. 2 |
| 로봇과 tactile 최소 구별 신호 | §III-A, Fig. 1–2, PDF pp. 1–2 |
| Wrench·pressure·영상 변환·network | §III-A–B, Fig. 3, 식 (1), PDF p. 3 |
| 환경 크기·물체 footprint·목표 위치 | §IV-A, Fig. 4, PDF p. 4 |
| 성공·timeout·impulse·threshold 시험 | §IV-B, 식 (2)–(3), PDF p. 4 |
| 시연 조작·화면·행동 전략 | §IV-C, Fig. 5, PDF p. 5 |
| 100 demonstrations·200 epochs·masking | §V-A, PDF p. 5 |
| 40회 평가의 성공·실패·시간 | §V-B, Fig. 6, PDF pp. 5–6 |
| 큰 힘 이후 0.8초 변위·실패 반응 수 | §V-B, Fig. 7, PDF p. 6 |
| Causal confusion·데이터 효율 가설 | §VI, PDF pp. 6–7 |
| 향후 장치·물체·정책·제어 구조 | §VII, PDF p. 7 |
| 인용 자료 | References [1]–[46], PDF pp. 7–8 |

본문의 수식·표·그림은 첨부 PDF의 실제 표시와 대조했다. 새 수식은 별도 줄의 `$$`와 표준 인라인 `$…$`를 사용한다. 원문 식 번호와 해설용 수식을 구분했다. 로컬 수식 구문·표 구조·렌더링 확인과 GitHub 원격 저장 소스 확인은 실제 GitHub 웹페이지 표시 확인과 다르며, 후자의 완료를 주장하지 않는다. 코드 실행, 정책 재학습, 실험 재현 및 보충 영상 확인은 수행하지 않았다.
