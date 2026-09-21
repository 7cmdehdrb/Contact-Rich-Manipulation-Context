# Rotating without Seeing: Towards In-hand Dexterity through Touch

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 조사 · B3](../reviews/2026-09-16_binary-tactile-wrench-rl.md#b3)

최초 정리일: **2026-09-17**. **2026-09-21 재검증:** 사용자가 다시 제공한 PDF 15쪽 전체를 원문과 대조했으며 SHA-256이 기존 기록과 동일한 `7be48b3f9573efaf8d53b2abf94f23ae16532d6afa2408bc803bc14d4286a5ba`임을 확인했다. 이번 재검증에서는 특히 (1) actor가 16-bit tactile만 쓰는 것이 아니라 관절 위치·이전 target·회전축과 4-frame history를 함께 사용한다는 점, (2) 실물 Table I에서 Rubber Duck은 continuous tactile의 평균 CRA가 binary보다 소폭 높다는 예외, (3) Table IV의 실물 회전 열이 본문 정의와 달리 CRR로 인쇄된 표기 불일치, (4) shape reconstruction이 회전 actor 내부 모듈이 아니라 별도 temporal-CNN 사후 분석이라는 점을 다시 확인했다. 기존 Binary Tactile·F/T 조사에 포함된 **B3**의 동일 상세 노트를 보완하며, 새 논문으로 중복 등록하지 않는다.

[읽은 판본 v4](https://arxiv.org/abs/2303.10880v4) · [v4 PDF](https://arxiv.org/pdf/2303.10880v4) · [RSS 공식 서지](https://www.roboticsproceedings.org/rss19/p036.html) · [DOI](https://doi.org/10.15607/RSS.2023.XIX.036) · [저자 프로젝트](https://touchdexterity.github.io/)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | Rotating without Seeing: Towards In-hand Dexterity through Touch |
| 시스템 이름 | Touch Dexterity |
| 저자 | Zhao-Heng Yin, Binghao Huang, Yuzhe Qin, Qifeng Chen, Xiaolong Wang |
| 소속 | HKUST, UC San Diego. Yin과 Huang은 공동 제1저자이며, Yin의 UC San Diego 인턴십 중 수행을 표기 |
| 게재 | Robotics: Science and Systems XIX, 2023. 공식 proceedings는 July 2023, Daegu, Republic of Korea로 표기 |
| DOI | 10.15607/RSS.2023.XIX.036 |
| 실제 읽은 판본 | 첨부 `2303.10880v4.pdf`. 첫 페이지 표기는 **27 Mar 2023**, arXiv:2303.10880v4 [cs.RO] |
| 읽은 범위 | Abstract, §I–VI, References, Appendix A–E; 식 (1)–(9), Table I–VI, Fig. 1–11 |
| 파일 SHA-256 | `7be48b3f9573efaf8d53b2abf94f23ae16532d6afa2408bc803bc14d4286a5ba` |
| 추가 확인 | RSS 공식 페이지에서 게재 정보·DOI, 저자 프로젝트에서 자료 링크 확인 |
| 이번 작업에서 수행하지 않은 것 | 출판본과 v4의 버전 차이 대조, 공개 코드 정적 분석·실행, 정책 재학습, 실물 재현, 보충 영상 전체 분석, 제조사 데이터시트 검증 |

게재 정보와 읽은 판본을 구분한다. 이 문서의 **PDF 페이지는 첨부 파일의 1부터 시작하는 물리적 페이지 번호**다. 본문·결론은 pp. 1–10, 참고문헌은 pp. 10–13, 부록은 pp. 14–15에 있다. 아래의 선행연구 설명은 저자들의 관련 연구 서술을 정리한 것이며, 인용 논문 전부를 이번에 별도 정독한 것은 아니다.

**읽는 핵심:** 이 연구는 손 안의 물체를 시각 없이 회전시키기 위해, 16개 FSR의 부위별 접촉 여부와 고유감각·명령 이력을 결합한다. 이진 촉각의 유용성을 실물에서 확인했지만, **촉각 bit만 받는 정책도 아니고 모든 물체에서 연속 촉각보다 우수한 결과도 아니다.** 손목 6축 F/T를 이용하는 방법이나 그 비교 실험은 제시하지 않는다. [§III–V]

## 1. 연구가 해결하려는 문제

### 1.1 가려지거나 보이지 않는 손 안 물체의 회전

사람은 손 안의 물체를 눈으로 계속 확인하지 않아도 피부 접촉과 손의 움직임을 통해 조작한다. 로봇에서도 손가락과 물체 사이의 가림이 심하면 시각 추적이 어렵다. 저자들은 이 문제를 **시각 입력 없는 다지손 in-hand rotation**으로 다룬다. 물체를 손바닥에 놓고 주어진 축 주위로 계속 회전시키면서 떨어뜨리지 않는 것이 과업이다. [Abstract, §I, III-C, PDF pp. 1–3]

손끝에서만 작게 회전시키는 상황과 달리, 이 과업에서는 물체가 손바닥 위에서 미끄러지거나 구르며 손가락도 크게 움직인다. 따라서 손가락 명령과 관절 위치의 차이만으로 모든 중요한 접촉을 파악하기 어렵다고 저자들은 설명한다. [§II, III-C]

### 1.2 문제 정의와 범위

| 구분 | 논문이 수행한 것 | 확대해서 해석하면 안 되는 것 |
| --- | --- | --- |
| 시작 상태 | 물체가 손바닥 안에 초기 배치됨 | 환경에서 물체를 찾아 접근·파지하는 전 과정을 학습했다고 해석 |
| 목표 | 주어진 x·y·z축에 대한 회전 | 임의 목표 pose까지 자동 계획하고 종료하는 일반적 reorientation과 동일시 |
| Blind | 실행 actor에 물체 영상·실시간 GT pose를 주지 않음 | 시뮬레이션 보상과 critic도 물체 정답을 쓰지 않는다고 해석 |
| Unseen | 시각으로 보지 않는다는 의미와 학습에 없던 물체라는 의미를 함께 사용 | 모든 실물 평가 물체가 전부 미학습 형상이라고 해석 |
| 제어 대상 | Allegro Hand의 16개 관절 | 팔과 손의 전체 관절을 함께 제어하는 정책이라고 해석 |
| 일반화 | 단순 기하 형상으로 학습해 다양한 실물 물체에 전이 | 임의의 형상·재질·크기에 보장되는 성능으로 해석 |

저자들도 축별 회전 과업을 일반적인 in-hand reorientation의 단순화된 형태라고 설명한다. 축별 primitive를 사람이 키보드로 선택하는 shared control은 시연하지만, 목표 자세를 스스로 판단하는 상위 정책의 성능은 평가하지 않는다. [§I, V-I, Fig. 8, PDF pp. 2, 9–10]

### 1.3 접근의 핵심

고해상도 센서 몇 개로 국소적인 촉각 이미지를 정밀하게 모사하는 대신, 손가락·손바닥의 여러 위치에 저렴한 FSR을 배치한다. 각 출력을 0/1로 줄이고, 시뮬레이터의 접촉 힘도 0/1로 바꾸어 같은 종류의 관측을 만든다. 여기에 대규모 병렬 PPO, 관측 이력, 물성·센서 randomization, PD controller의 system identification을 결합한다. [§I, III–IV, Appendix C]

저자들은 16개 bit가 조합상 최대 $2^{16}$개의 패턴을 표현할 수 있다고 설명한다. 이는 이진 벡터의 조합 수이며, 실제로 모든 패턴이 발생한다거나 물체 pose를 유일하게 복원할 수 있다는 증명은 아니다. [§I, PDF p. 2; 후반 문장은 해설]

## 2. Related Work — 저자들이 설정한 비교 구도

| 관련 연구 갈래 | 원문에서 인정하는 성과 | 이 논문이 구분하는 지점 |
| --- | --- | --- |
| 분석적 in-hand manipulation | 모델과 접촉 조건에 기반한 조작 계획·제어 | 물체·controller에 대한 가정 때문에 복잡한 과업으로 확장하기 어려울 수 있음 |
| Deep RL·시연 기반 다지 조작 | 시뮬레이션 학습, 시연을 통한 sample efficiency와 자연스러운 행동 향상 | 기존 연구 다수가 시각에 크게 의존한다고 설명 |
| 시각 없는 proprioception 기반 회전 | 관절 상태·제어 오차에서 암묵적인 접촉 정보를 얻음. 원문 [50], [51], [61] | 비교 대상이 손끝의 작은 움직임이나 제한된 물체 집합을 다루는 데 비해, 본 연구는 손바닥 위의 복잡한 운동과 명시적 접촉 관측을 강조 |
| 촉각을 이용한 조작·인식 | 국소 형상, 힘·토크, 접촉 사건, 재질 등의 정보 활용 | 가장 단순한 접촉 유무도 다자유도 조작에 기여할 수 있는지 검증 |
| Binary contact 기반 위치 추정·탐색 | 원문 [22], [36], [49]에서도 이진 접촉의 유용성 제시 | 저자들은 낮은 자유도 조작기 중심의 연구와 다지손 회전을 구분 |
| 넓은 면적의 tactile skin | 원문 [11]의 Shadow Hand 피부는 유사하면서 더 조밀한 배치 | 해당 센싱 구성을 본 논문과 같은 회전 제어에 사용하는 방법이 명확하지 않았다고 설명 |
| 정교한 tactile simulation | 접촉면의 normal/shear field, 촉각 영상 등을 모사 | 본 연구는 IsaacGym의 기본 접촉 힘으로 binary 관측을 생성하며 별도의 촉각 이미지 합성 모델을 쓰지 않음 |

근거: 원문 §II, PDF pp. 2–3. 여기서 인용한 기존 연구의 제약은 **이 논문 저자들의 비교 서술**이다. 모든 tactile manipulation 연구에 대한 독립적인 최신 문헌 평가로 읽지 않는다.

실험에서는 시각 기반 방법들과 직접 성능을 비교하지 않는다. 저자들은 많은 visual simulation data를 수집하는 데 상당한 시간이 필요하다는 이유를 든다. 따라서 이 결과만으로 시각 정책 대비 성능 우위를 주장할 수 없다. [§V-B, PDF p. 6]

## 3. 하드웨어·센서·커버리지

### 3.1 시스템 구성과 센서 배치

| 항목 | 첨부 v4에서 확인한 내용 | 근거 |
| --- | --- | --- |
| 로봇 팔 | XArm. 정확한 모델·자유도는 미명시 | §III-A, p. 3 |
| 손 | 16-DOF Allegro Hand | §III-A |
| 촉각 | Force-Sensing Resistor, FSR 16개 | §III-A |
| 배치 | 손가락 4개에 각각 3개, 손바닥에 4개. 한쪽 면의 fingertips·finger links·palm에 분포 | Fig. 1, Fig. 10, pp. 1, 14 |
| 신호 취득 | STM32F microcontroller가 아날로그 전압을 취득하고 디지털 신호를 host에 전달 | §III-A |
| 접촉면 | 마찰을 높이기 위한 finger cot 사용. FSR은 cot 안쪽에 위치 | Fig. 2 설명, p. 3 |
| 센서 비용 | 원문 작성 당시 개당 약 12달러로 설명 | §I, p. 2. 현재 구매 가격이나 시스템 전체 비용이 아님 |
| 물리 시뮬레이터 | IsaacGym | §III-B, IV-C |
| 정책 출력 | 16차원 상대 관절 위치 명령 | §IV-A.2 |
| 논문에 명시된 제어 주파수 | 시뮬레이션·실물 10 Hz | §IV-A.2, IV-C |

Fig. 10의 사진에서는 손가락의 센서가 **0–11**, 손바닥의 센서가 **12–15**로 번호 붙어 있다. 그림상 손가락별 묶음은 0–2, 3–5, 6–8, 엄지의 9–11이다. 각 손가락을 따라 proximal link에서 fingertip 쪽으로 번호가 증가한다. 이는 그림의 위치 대응을 설명한 것이며, 별도로 공개 코드를 읽어 배열 순서를 검증한 것은 아니다. [Fig. 10, PDF p. 14]

센서는 손 전체 표면을 끊김 없이 덮는 피부가 아니다. 특히 손가락 **측면**의 접촉은 현재 배열로 충분히 관측하지 못하며, 저자들은 이를 x·y축 회전 실패와 연결한다. 따라서 논문이 강조하는 넓은 분포와 모든 접촉의 완전한 검출을 구분해야 한다. [§V-I, p. 10]

### 3.2 원문에 없는 사양

| 항목 | 확인 결과 |
| --- | --- |
| FSR 제조사·모델·감지 면적·치수 | 미명시 |
| 최대 측정 하중·정확도·분해능·반복성 | 미명시 |
| 검출 가능한 최소 실물 힘 | 미명시. Simulation threshold 0.01 N을 제품 검출 성능으로 사용할 수 없음 |
| MCU 세부 제품 번호·ADC bit 수·회로 저항 | 미명시. STM32F보다 구체적인 모델명으로 확장하지 않음 |
| 전압–힘 변환식·센서별 보정 계수 | 미명시 |
| 센서 취득률·통신률·최대 지연 | 미명시. 제어 주파수 10 Hz와 구분 |
| 센서 좌표·간격·커버리지 비율 | 번호가 붙은 사진은 있으나 수치 미명시 |
| 실물 LPF 차수·cutoff·hysteresis·debounce | 미명시 |
| XArm 세부 사양, Allegro의 관절별 torque limit·속도 limit | 미명시 |

## 4. Binary tactile의 생성과 효용

### 4.1 실제 센서: 전압에서 접촉 여부로

원문의 처리 경로는 **외력에 따른 FSR 저항 변화 → 아날로그 전압 → MCU 취득·디지털 전달 → 선택한 threshold에 대한 이진화 → 16개 접촉 bit**다. 전압/힘 관계가 비선형이고 잡음이 있어 정밀한 연속 force 값의 sim-to-real 정합이 어렵다는 것이 이진화의 동기다. [§III-A, PDF p. 3]

해설용으로 접촉할수록 커지는 대표 측정값을 $s_{i,t}$라 놓으면, 이진화의 의미는 다음처럼 표현할 수 있다.

$$
o_{i,t}=\mathbb{1}[s_{i,t}>\theta_{\mathrm{th}}], \qquad \mathbf{o}_t\in\{0,1\}^{16}.
$$

이 식은 **원문 설명의 개념적 재표현**이다. 실제 전압 극성, equality 처리, 센서별 threshold 사용 여부, firmware의 정확한 비교 연산은 원문에서 정하지 않는다. 실물 threshold의 전압 수치도 제공하지 않는다. [§III-A]

저자들은 연속 force 값을 맞추는 것보다 threshold를 조절해 접촉 사건을 맞추는 편이 쉽다고 설명한다. 이는 정밀한 힘 크기 보정을 생략하거나 완화하는 전략이다. 다만 설치 상태·감도·접촉면의 차이까지 자동으로 사라진다는 의미는 아니다. [§III-A; 마지막 문장은 해설]

**실물 신호에 LPF나 hysteresis를 적용했다고 이 논문에 없는 단계를 추가하지 않는다.** 본문에 등장하는 EMA는 뒤에서 설명할 **action의 평활화**다. 센서 dropout과 lag probability는 학습 중 센서 불확실성을 모사하는 randomization이다. 세 가지는 서로 다른 위치에서 작동한다.

### 4.2 시뮬레이션: 센서 링크의 접촉 힘을 이진화

각 센서를 손가락·손바닥 링크에 고정된 별도 링크로 모델링한다. 해당 센서 링크에 대한 net contact force를 가져와 norm을 계산하고 threshold를 적용한다. [§III-B, PDF p. 3]

$$
\mathbf{F}_{i,t}= \begin{bmatrix}F_{x,i,t}&F_{y,i,t}&F_{z,i,t}\end{bmatrix}^{\mathsf T}, \qquad \tilde{o}_{i,t}=\mathbb{1} \left[\lVert\mathbf{F}_{i,t}\rVert>\tilde{\theta}_{\mathrm{th}}\right], \qquad \tilde{\theta}_{\mathrm{th}}=0.01\;\mathrm{N}.
$$

위 식 역시 원문 서술을 모은 해설식이다. **부모 링크에 가해진 force는 센서 링크의 net contact force에 포함하지 않는다.** 이는 센서가 부착된 영역의 접촉과 비센서 영역 접촉을 구분하는 데 중요하다. 벡터의 세 성분을 actor에 전달하는 것도 아니며, normal force 한 성분만 threshold한다고 적혀 있지도 않다. [§III-B]

실물 threshold와 simulation threshold는 서로 다른 측정 공간에서 조절한다. 논문은 두 센서의 반응이 비슷해지도록 simulation threshold를 맞췄다고 설명하며 0.01 N을 제시한다. 실물 전압 threshold와 이 값 사이의 수치적 변환 관계는 제공하지 않는다.

### 4.3 16bit가 보존하는 정보와 잃는 정보

| 구분 | 유지되는 정보 | 유지되지 않는 정보 |
| --- | --- | --- |
| 공간 | 어떤 센서 부위들이 접촉했는지 | 한 센서 내부의 정밀한 접촉점·접촉 중심 |
| 힘 | 정한 threshold를 넘는 접촉 여부 | 연속적인 힘 크기·3축 방향·전단 분포 |
| 시간 | 관측 이력을 통해 어느 부위의 bit가 변했는지 | 원시 센서의 모든 고주파 파형 |
| 물체 상태 | 고유감각·명령·접촉 패턴을 함께 이용한 암묵적인 정보 | bit 한 프레임만으로 유일하게 정해지는 GT pose나 물성 |

이 표의 보존·손실 구분은 방법에 대한 해설이다. 저자들이 설명하는 두 가지 주요 기능은 다음과 같다. [§III-D, Fig. 2, PDF pp. 3–4]

1. **손 안 위치에 대한 정보:** 손끝과 접촉하지 않는 물체라도 손바닥의 센서가 활성화되면 어느 부근에 놓였는지 추론할 단서를 얻는다. 예시에서는 손바닥 중앙의 cuboid를 향해 엄지를 이동시킨다.
2. **조작 중 중요한 접촉의 확인:** 회전을 담당할 손끝이 실제로 물체에 닿았는지 확인한다. 접촉이 없는 상태에서 같은 손가락 동작을 실행하면 회전이 시작되지 않거나 물체가 불안정한 곳으로 이동할 수 있다.

여기서 위치 추론은 별도 pose estimator가 수치 pose를 출력한다는 뜻이 아니다. 실제 회전 actor는 아래의 MLP이며, 명시적인 물체 pose 추정 모듈은 제시하지 않는다.

## 5. RL 관측과 actor–critic의 정보 경계

### 5.1 한 시점의 관측

저자들은 문제를 MDP로 서술한다. 다만 actor가 받는 관측 한 시점만으로 충분하지 않을 수 있어 과거 상태를 함께 넣는다. [§IV-A.1, IV-C, PDF pp. 4–5]

| 성분 | 원문 기호·차원 | 의미 |
| --- | --- | --- |
| 관절 위치 | $\mathbf{q}_t\in\mathbb{R}^{16}$ | Allegro의 현재 관절 위치 |
| 촉각 | $\mathbf{o}_t\in\{0,1\}^{16}$ | 부위별 binary contact |
| 이전 위치 목표 | $\tilde{\mathbf{q}}_t\in\mathbb{R}^{16}$ | 이전 단계까지 누적된 관절 위치 target |
| 회전축 | $\mathbf{k}\in\mathbb{S}^{2}$ | 3차원 공간의 단위 축 벡터 |

원문 성분을 단순 연결하면 다음과 같이 표현할 수 있다.

$$
\mathbf{s}_t= [\mathbf{q}_t,\mathbf{o}_t,\tilde{\mathbf{q}}_t,\mathbf{k}], \qquad 16+16+16+3=51.
$$

여기서 $\mathbb{S}^{2}$는 3차원 공간의 단위구다. 자유도가 2라는 이유로 입력 성분을 2개로 합산하지 않는다. 관절 속도는 이 actor state 목록에 없다. Reward에서 관절 속도를 사용한다는 사실도 actor 입력에 있다는 뜻은 아니다.

### 5.2 현재와 과거 세 시점: 총 네 프레임

$$
\mathbf{h}_t= [\mathbf{s}_t,\mathbf{s}_{t-1},\mathbf{s}_{t-2},\mathbf{s}_{t-3}].
$$

원문은 **현재 상태와 다른 세 개의 historical state**를 stack한다고 명시한다. 위 성분 전체를 프레임마다 연결한다면 **$51\times4=204$차원**이다. 204라는 숫자는 원문에 직접 기재된 네트워크 입력 사양이 아니라 **명시된 구성에서 계산한 차원**이며, 공개 코드의 tensor shape까지 확인한 값은 아니다. [§IV-A.1, IV-C]

저자들은 이 이력을 §V-F에서 **0.4초의 local window**로 설명한다. 10 Hz의 네 sample을 뜻하며, 엄밀히 첫 sample과 마지막 sample의 timestamp 간격은 0.3초다. Episode 시작 시 history를 어떻게 채우는지는 미명시다. MLP에 유한 이력을 연결하며 LSTM·GRU를 쓴다고 설명하지 않는다.

### 5.3 학습용 privileged critic

| 정보 | Actor 실행 입력 | Critic 학습 입력 또는 보상 |
| --- | --- | --- |
| 관절 위치·binary tactile·이전 target·회전축 | 사용 | 기본 상태와 관련 |
| 링크별 contact force | 연속 force를 직접 주지 않음 | Value network에 추가 privileged information으로 사용 |
| 물체 GT pose | 사용하지 않음 | Value network에 추가; 회전 보상 계산에도 물체 상태 필요 |
| 물체 physical parameters | 사용하지 않음 | Value network에 추가 |
| 물체 속도·손끝과 물체 거리·PD torque·관절 속도 | 위 actor state 목록에 없음 | 보상 계산에 사용되는 수량들. 전부가 critic 입력이라고 명시된 것은 아님 |

근거: §IV-A.3, IV-C. Critic의 추가 정보는 본문에서 예시적으로 설명하므로 전체 차원과 정확한 feature 목록을 임의로 완성하지 않는다. 시뮬레이션에서 관측 가능한 정답을 활용해 학습하지만, 최종 actor의 실물 실행에는 그 정답을 공급하지 않는 구조다.

## 6. 정책 출력부터 관절 제어까지

### 6.1 상대 행동과 누적 target

정책의 출력은 16차원 상대 관절 명령 $\mathbf{a}_t$다. 원문은 먼저 다음의 직접 누적 형태를 소개한다. [§IV-A.2, PDF p. 4]

$$
\tilde{\mathbf{q}}_{t+1} =\tilde{\mathbf{q}}_t+\mathbf{a}_t.
$$

기준이 현재 측정 관절 위치 $\mathbf{q}_t$가 아니라 **이전 target $\tilde{\mathbf{q}}_t$**라는 점을 구분한다. 연속 timestep에서 행동이 충돌하면 손가락 운동이 매끄럽지 않을 수 있어 실제로는 행동을 평활화한다.

### 6.2 EMA가 적용되는 위치

$$
\tilde{\mathbf{a}}_t =\eta\mathbf{a}_t+(1-\eta)\tilde{\mathbf{a}}_{t-1}, \qquad \eta=0.8, \qquad t\geq1, \qquad \tilde{\mathbf{a}}_0=\mathbf{0}.
$$

$$
\tilde{\mathbf{q}}_{t+1} =\tilde{\mathbf{q}}_t+\tilde{\mathbf{a}}_t.
$$

즉 현재 행동에 0.8, 이전의 평활화된 행동에 0.2를 부여한다. 이 EMA의 목적은 손가락 motion을 매끄럽게 만드는 것이며 **FSR 전압 필터나 bit의 hysteresis가 아니다.** 새 위치 target은 PD controller로 전달된다. [§IV-A.2, Fig. 3]

### 6.3 시간 간격과 미명시 제어 설정

IsaacGym의 simulation step은 **0.01667초**, substep은 **2개**다. 정책이 출력한 control target을 **6 simulation step 동안 실행**하여 실물의 **10 Hz** 제어에 대응시킨다. 원문은 PD controller가 simulation과 real에서 10 Hz로 동작한다고 서술한다. 더 빠른 제조사 내부 servo loop의 주파수는 이 논문에서 확정하지 않는다. [§IV-C, p. 5]

관절별 action scale·clipping, target의 joint-limit 처리, 최종 PD gain, torque saturation, 실물에서 Gaussian policy의 mean만 사용하는지 여부는 미명시다. PD controller라는 명칭만으로 이 값을 임의 지정하지 않는다.

## 7. 보상 함수 — 식 (1)–(9)

### 7.1 전체 구성

본문 식 (1)과 Appendix D 식 (9)는 같은 여섯 항의 가중합을 제시한다. [PDF pp. 4, 14]

$$
r_t=w_1r_{\mathrm{rot}}+w_2r_{\mathrm{vel}} +w_3r_{\mathrm{fall}}+w_4r_{\mathrm{work}} +w_5r_{\mathrm{torque}}+w_6r_{\mathrm{dist}}.
$$

| 항 | 가중치 | 유도하려는 행동 |
| --- | --- | --- |
| 회전 $r_{\mathrm{rot}}$ | $w_1=20.0$ | 지정 축 방향으로 물체 회전 |
| 속도 $r_{\mathrm{vel}}$ | $w_2=0.1$ | 물체의 불안정한 이동 억제 |
| 낙하 $r_{\mathrm{fall}}$ | $w_3=1.0$ | 손바닥 밖 낙하 억제 |
| Work $r_{\mathrm{work}}$ | $w_4=0.0003$ | 과도한 관절 구동 억제·운동 평활화 |
| Torque $r_{\mathrm{torque}}$ | $w_5=0.0003$ | 큰 제어 torque 억제 |
| 거리 $r_{\mathrm{dist}}$ | $w_6=0.1$ | 손끝이 물체 가까이 와서 상호작용하도록 유도 |

가중치는 Appendix D의 값이다. 단위·스케일이 서로 다른 항의 수치 크기만으로 어느 항이 실제 학습을 지배했는지 단정할 수 없다.

### 7.2 회전 보상: simulator 각속도 대신 자세 변화에서 각도 계산

본문 식 (2)는 clipping 상수를 $c_1$로 표현하며, Appendix 식 (3)은 다음 값을 준다.

$$
r_{\mathrm{rot}}= \mathrm{clip}(\Delta\theta,-0.157,0.157).
$$

$\Delta\theta$는 축 $\mathbf{k}$에 수직인 평면 $\Pi$에서 측정한 signed rotation angle이다. Fig. 4와 §IV-A.3의 계산 설명은 다음과 같다.

1. $\Pi$ 위에서 단위 벡터 $\mathbf{v}$를 무작위로 고른다.
2. 이 벡터가 물체에 붙어 있다고 생각하고, 물체가 다음 상태로 움직인 뒤의 대응 벡터 $\mathbf{v}'$를 구한다.
3. $\mathbf{v}'$를 같은 평면에 투영하여 $\mathbf{v}'_p=\mathrm{Proj}(\mathbf{v}',\Pi)$를 얻는다.
4. 축 $\mathbf{k}$를 기준으로 $\mathbf{v}$와 $\mathbf{v}'_p$ 사이의 부호 있는 각도 $\Delta\theta\in[-\pi,\pi)$를 사용한다.

저자들은 simulator가 반환하는 각속도 $\boldsymbol{\omega}$에 대해 $\langle\boldsymbol{\omega},\mathbf{k}\rangle$를 보상으로 쓰면, 복잡한 물체 운동에서 잡음의 영향으로 특정 pose 주변에서 진동하는 등 바람직하지 않은 행동이 발생했다고 설명한다. 반면 위와 같이 자세 변화에서 계산한 유한 차분은 반복 학습에서 더 일관된 회전을 만들었다고 보고한다. [§IV-A.3, p. 4]

원문이 사용하는 $\Delta\theta$는 **각도 변화**이며, 이를 임의로 timestep으로 나누어 각속도 보상으로 바꾸지 않는다. 벡터를 다시 sampling하는 주기나 투영 벡터가 거의 0인 경우의 수치 처리도 원문에 없다.

### 7.3 속도·낙하·구동 페널티

Appendix 식 (4):

$$
r_{\mathrm{vel}}=-\lVert\mathbf{v}_t\rVert.
$$

본문은 $\mathbf{v}_t$를 물체의 velocity로 설명한다. 회전하는 물체가 안정적으로 손 안에 머무르고 전이 가능성을 높이도록 하는 항이다. Actor에 이 속도를 직접 제공한다는 뜻은 아니다.

Appendix 식 (5):

$$
r_{\mathrm{fall}}=-50.0.
$$

이 값은 **물체가 손바닥 밖으로 떨어질 때의 페널티**다. 매 timestep에 무조건 -50을 더하는 상수 보상으로 읽지 않는다. 낙하의 수치적 판정 경계는 미명시다. [§IV-A.3, Appendix D]

Appendix 식 (6):

$$
r_{\mathrm{work}} =-\left\langle|\boldsymbol{\tau}|,|\dot{\mathbf{q}}_t|\right\rangle.
$$

$\boldsymbol{\tau}$는 PD controller가 출력한 torque이고, 절댓값은 성분별로 적용된다. 서로 다른 관절의 부호가 상쇄되지 않게 구동 크기를 벌점으로 준다. 원문은 이를 work penalty라고 부르지만, 식에 시간 적분이나 $\Delta t$ 곱이 명시되어 있지는 않다. 따라서 총 에너지 측정값으로 바꾸어 설명하지 않는다. [해설]

Appendix 식 (7):

$$
r_{\mathrm{torque}}=-\lVert\boldsymbol{\tau}\rVert.
$$

위 두 항은 외부 손목 F/T 측정값을 이용한 wrench 보상이 아니다. 논문이 정의한 관절 controller torque에 대한 페널티다.

### 7.4 손끝–물체 거리 보상

본문은 clipped inverse-distance 형태를 설명하며, Appendix 식 (8)은 구체적인 상수와 네 손끝의 평균을 준다.

$$
r_{\mathrm{dist}} =\mathrm{mean}_{i=0,1,2,3} \left[ \mathrm{clip}\left( \frac{0.1}{0.02+4d(\mathbf{x}_{\mathrm{tip}}^{i},\mathbf{x}_{\mathrm{obj}})}, 0,1 \right) \right].
$$

$\mathbf{x}_{\mathrm{tip}}^{i}$는 각 손끝 위치, $\mathbf{x}_{\mathrm{obj}}$는 물체 위치를 나타낸다. 손끝이 물체에 가까워지도록 유도하는 shaping이다. $d$를 실제 표면까지의 signed distance나 mesh의 최단 거리라고 구체화한 정의는 원문에서 확인되지 않는다. 이 보상 역시 시뮬레이션의 위치 정보에 의존하며 actor에 물체 위치를 넣는 경로와 구분한다.

### 7.5 Reset으로 불필요한 탐색 줄이기

원문은 물체가 초기 위치, 즉 손바닥 중심에서 너무 멀어지면 episode를 reset한다. 물체의 major axis가 회전축에서 지나치게 벗어난 경우도 reset하여 원하지 않는 방향의 탐색을 줄인다. 정확한 거리·각도 threshold, 축을 정의하기 어려운 형상의 처리, 일반 simulation episode의 최대 길이는 미명시다. [§IV-A.4, PDF pp. 4–5]

이 reset은 학습을 쉽게 하는 과업 제약이다. 실물 실행 시 동일한 GT 기반 reset 판정을 수행했다고 옮겨 적지 않는다.

## 8. PPO 학습 설정

### 8.1 네트워크와 최적화

| 항목 | 원문 설정 |
| --- | --- |
| 알고리즘 | PPO, actor와 critic의 비대칭 관측 |
| Actor | MLP, hidden layers **[512, 256, 256]**, ELU |
| Critic | MLP, hidden layers **[512, 512, 256, 256]**, ELU |
| 정책 분포 | Gaussian. 학습 가능한 **state-independent standard deviation** |
| Actor learning rate | $10^{-4}$ |
| Critic learning rate | $5\times10^{-4}$ |
| Actor adaptive KL threshold | 0.02 |
| Critic adaptive KL threshold | 0.016 |
| PPO clipping coefficient | 0.2. 원문은 advantage clipping이라는 표현 사용 |
| Horizon length | 16 |
| Discount factor | $\gamma=0.99$ |
| GAE coefficient | 0.95. 부록 기호는 $\tau$이며, 보상식의 torque 기호와 의미가 다름 |
| Normalization | State input, value, advantage |
| Gradient norm | 1.0 |
| Minibatch size | 16384 |
| 병렬 환경 | 8192 |
| Simulation timestep·substeps | 0.01667 s, 2 substeps |
| Action 유지 | 6 simulation steps |

근거: §IV-C, Appendix B, PDF pp. 5, 14. 본문은 KL threshold 0.02로 간략히 설명하고, 부록은 policy/value 설정을 나누어 제시하므로 여기서는 부록의 구체 값을 보존했다.

입력 204차원이나 고정된 물체 상태 estimator를 원문 네트워크 표에 있는 수치처럼 기록하지 않는다. 전체 학습 update 수, wall-clock 시간, GPU 모델, epoch 수, entropy coefficient 등은 이 판본에서 확정하지 않는다. Fig. 6의 training-step 축을 environment transition 총수로 곧바로 변환하지도 않는다.

### 8.2 MLP가 사용하는 정보

이 actor는 촉각 이미지를 CNN이나 GAN으로 변환한 latent를 받는 구조가 아니다. Binary contact와 관절·target·축의 시간 stack이 MLP의 입력이다. 뒤에 등장하는 **temporal-CNN은 별도의 형상 이해 분석 실험**에 사용하며, 회전 제어 actor와 동일한 네트워크가 아니다. [§IV-C, V-H]

## 9. Sim-to-real: randomization과 system identification

### 9.1 Table VI 전체 설정

| 대상 | 원문 값 | 해석과 주의 |
| --- | --- | --- |
| Object mass | [0.2, 0.6] kg | 학습 물성 범위. 실물 평가 물체별 실측 질량 목록은 아님 |
| Object friction | [0.3, 3.0] | 마찰 계수 범위 |
| Object shape | $\times\mathcal{U}(0.95,1.05)$ | 형상에 대한 배율 randomization. 축별 적용 방식은 미명시 |
| Object initial position | **행 제목: (cm)**, 값: $+\mathcal{U}(-0.015,0.015)$ | 원문 단위와 수치를 그대로 보존. 아래 주의 참조 |
| Hand friction | [0.3, 3.0] | 손의 마찰 계수 범위 |
| PD P gain | $\times\mathcal{U}(0.66,1.33)$ | Nominal gain에 대한 배율; nominal 수치는 미명시 |
| PD D gain | $\times\mathcal{U}(0.80,1.20)$ | 위와 같음 |
| Sensor lag probability | 0.25 | 정확한 sampling·hold 재귀식은 미명시 |
| Sensor drop rate | 0.1 | 활성 contact bit를 1에서 0으로 뒤집음 |
| Random force scale | 0.2 | 힘의 단위·배율 기준·분포 정의는 미명시 |
| Random force probability | [0.2, 0.25] | 표의 범위 그대로. 적용 조건의 세부 알고리즘은 미명시 |
| Random force decay | 0.1 s마다 0.99 | 시간 간격과 계수 |
| Joint observation noise | $+\mathcal{U}(-0.05,0.05)$ | 관절 관측 잡음; 표에 별도 단위 설명 없음 |
| Action noise | $+\mathcal{U}(-0.06,0.06)$ | 출력 행동 잡음; scaling 전후 적용 순서는 미명시 |

근거: §IV-B, Appendix C, Table VI, PDF pp. 5, 14. $\mathcal{U}$는 uniform 분포 표기를 뜻한다. 대괄호만 제시된 항의 분포까지 모두 uniform이라고 임의 확정하지 않는다.

**단위 주의:** Table VI의 initial position 행에는 `(cm)`가 인쇄되어 있는데, 값은 $\pm0.015$다. 코드의 실제 길이 단위를 검증하지 않은 상태에서 이것을 **±1.5 cm로 고쳐 쓰지 않는다.** 표기 오류인지 실제 범위인지 첨부 원문만으로 확정할 수 없다.

### 9.2 센서 오류의 의미

§IV-B.1은 **활성화된 센서의 1을 확률 $p$로 0으로 바꾸는 dropout**을 설명한다. Table VI의 $p=0.1$을 대입하면 false negative를 모사하는 것이다. 0을 1로 바꾸는 false positive까지 대칭적으로 섞는 bit-flip noise라고 설명하지 않는다.

지연은 원문 [28]을 따르는 exponential delay라고 설명하고, Table VI에 lag probability 0.25를 제시한다. 그러나 이 판본에는 정확한 지연 분포·최대 길이·센서별 독립성·지난 값을 유지하는 식이 없다. **0.25초 지연이라는 뜻도 아니며, 센서 EMA 계수라는 뜻도 아니다.**

### 9.3 PD controller의 system identification

저자들은 시뮬레이션과 실물의 PD controller에 **impulse 입력과 sinusoidal 입력**을 주고 응답이 맞도록 계수를 조정했다고 설명한다. 이 과정이 성공적인 전이에 중요했다고 명시한다. [Appendix C, PDF p. 14]

최종 gain, 입력의 진폭·주파수, 동정 목적함수, fitting 오차는 제공하지 않는다. 따라서 전이의 근거를 이진화 하나로 축약하기보다, **접촉 표현 정합 + 물성/센서 randomization + 제어 응답 정합 + 행동 평활화**가 함께 사용된 시스템으로 읽어야 한다. 각 요소를 완전히 분리한 sim-to-real 기여도 실험은 이 판본에 없다.

## 10. 실험 구성과 지표

### 10.1 물체 집합·학습·평가의 구분

| 설정 | 학습·평가 구성 | 근거 |
| --- | --- | --- |
| Simulation 단일 물체 | Cuboid로 학습. 같은 물체에서 physics distribution shift를 평가 | §V-C/D, Table II |
| Simulation 다중 물체 | Set A로 학습하고 A와 Set B에서 평가 | §V-C/D, Table III |
| Object Set A | Irregular cubes | Fig. 5, p. 5 |
| Object Set B | Irregular cylinders 및 aspect ratio가 큰 물체 | Fig. 5 |
| 실물 다중 물체 | A와 B에서 학습한 정책을 Set C에 평가 | §V-E |
| 실물 seen 그룹 | Object C1–C5. 저자는 학습에서 본 인공 물체로 설명 | Table I, §V-E |
| 실물 unseen 그룹 | Tomato, Apple, Orange, Soupcan, Rubber Duck | Table I |
| 형상 재구성 분석 | 별도로 125개 irregular column-shaped object 사용 | §V-H. A/B/C의 개수로 혼용하지 않음 |

Set A/B의 전체 물체 수, 각 물체의 수치 치수·질량, C1–C5 전체의 고유 이름은 이 판본에서 명확히 제시하지 않는다. Fig. 5는 예시 이미지다. 본문에 등장하는 lego box 같은 예시를 임의로 특정 C 번호와 연결하지 않는다.

### 10.2 지표와 통계

| 지표 | 정의 | 평가 영역·해석 |
| --- | --- | --- |
| CRR | Cumulative Rotation Reward | 시뮬레이션의 누적 회전 보상. 회전 횟수와 동일한 수치가 아님 |
| CRA | Cumulative Rotation Angle | 실물에서 사람이 센 누적 회전 횟수, 단위 rounds |
| TTF / Duration | Time-to-Fall | 손 안에 머문 시간, 단위 초. Simulation과 real 모두 사용 |

근거: §V-A.2, PDF p. 5. Table I은 **3 seeds로 학습한 3개 정책의 평균**, **각 trial 30초**라고 명시한다. 따라서 TTF=30초는 그 관측 구간 동안 유지했다는 뜻이지, 무제한 시간 동안 낙하하지 않는다는 뜻이 아니다. 각 seed마다 시행한 추가 반복 수는 명시하지 않는다.

Table II–V는 3 seeds의 평균이라고 설명한다. 아래는 **원문의 평균±값을 그대로 옮겼으며**, 표의 ±가 어떤 집계 단위의 표준편차인지 모든 표에서 명확히 정의되지는 않는다. Fig. 6은 예외적으로 음영이 standard deviation이라고 명시한다. 따라서 모든 ±를 일률적으로 ‘3회 실물 시행의 표준편차’라고 이름 붙이지 않는다. 특히 Table V는 물체 집합에 대한 평균도 함께 설명한다.

### 10.3 비교군: 같은 이름처럼 보이는 조건의 차이

| 방법 | 학습·평가 조건 | 검증하려는 질문 |
| --- | --- | --- |
| Sensor / Ours | 기본 binary contact를 사용해 학습·평가 | 제안한 전체 방법 |
| No-Sensor | 촉각 없이 PPO 학습. 관절 상태와 target 등으로 암묵적 접촉 정보 활용 | 촉각 없이도 학습 가능한가 |
| LS-Sensor | 활성 threshold를 **0.2 N**으로 높여 별도로 학습 | 약한 접촉을 놓치는 낮은 감도의 영향 |
| DS-Sensor | 기본 촉각 정책에서 **평가할 때** tactile input을 비활성화 | 이미 학습한 정책이 촉각을 실제로 이용하는가 |
| OL / Openloop | 시뮬레이션에서 성공한 회전 궤적을 실물에서 실행 | 단순한 동작 재생으로도 가능한가 |
| CT-Sensor | Binary 대신 continuous-valued sensor input을 받도록 학습 | 연속 신호의 sim-to-real 전달과 비교 |
| No-Fingertip / No-Palm | 해당 센서 그룹을 제외하고 각각 재학습 | 센서 위치별 기여 |

근거: §V-B/G, PDF pp. 6, 8–9. No-Sensor와 DS-Sensor는 학습 조건이 다르다. DS-Sensor의 성능 저하는 학습한 입력을 평가에서 제거했을 때의 결과이므로, 촉각 없는 정책을 다시 학습한 성능과 같은 의미로 읽지 않는다.

LS-Sensor의 0.2 N은 기본 0.01 N의 20배 threshold다. 이는 값의 산술적 비교이며, 센서 제조사의 감도가 정확히 20배 낮다는 뜻은 아니다. CT-Sensor의 실물 전압–힘 calibration과 scaling·전처리의 세부 사양은 미명시다.

## 11. Simulation 결과

### 11.1 학습 곡선 — Fig. 6

Fig. 6은 단일 물체와 다중 물체에서 sensor 유무 및 감도를 비교한다. 3 seeds 평균과 표준편차 음영을 제시한다. [§V-C, PDF p. 6]

단일 cuboid에서는 No-Sensor와 LS-Sensor의 회전 보상이 전체 방법보다 낮지만, LS-Sensor의 TTF는 전체 방법 수준에 도달할 수 있었다고 설명한다. 즉 약한 접촉 일부를 놓쳐도 **단일 물체를 떨어뜨리지 않는 안정성**에는 이점이 있었다.

반면 Set A를 이용한 다중 물체 학습에서는 No-Sensor와 LS-Sensor가 실패하고 기본 촉각 정책은 학습에 성공했다고 보고한다. 저자들은 이를 작은 접촉도 감지하는 높은 감도가 다중 물체 rotation에서 중요하다는 근거로 해석한다. **단순히 binary인가보다, 어느 부위의 어느 약한 접촉까지 관측하는가가 중요하다.** 후반 문장은 이 비교에 대한 해설이다.

그래프의 곡선을 임의 digitization하여 최종 성공률이나 정확한 수렴 step을 만들어내지는 않았다. 이 논문의 주된 지표는 회전 보상과 유지 시간이며, Fig. 6의 TTF를 성공률로 바꾸지 않는다.

### 11.2 단일 물체의 물성 변화 — Table II 전체

| 방법 | Seen physics CRR | Seen TTF (s) | Unseen physics CRR | Unseen TTF (s) |
| --- | --- | --- | --- | --- |
| No-Sensor | 689.3±141.5 | 33.3±4.7 | 369.0±129.1 | 23.5±6.1 |
| Sensor | 963.8±377.8 | 42.2±4.1 | 919.3±338.0 | 40.0±4.3 |
| DS-Sensor | 904.2±408.6 | 39.1±6.3 | 615.5±293.2 | 31.2±8.0 |
| LS-Sensor | 860.0±348.7 | 38.8±6.9 | 796.5±366.7 | 37.4±8.4 |

원문 §V-D, Table II, PDF p. 7. 저자들은 학습과 다른 마찰·질량 범위에서 평가하며, 물체가 손 안에서 더 미끄러지기 쉬운 조건이라고 설명한다. 정확한 held-out 범위는 제공하지 않으므로 Table VI의 학습 범위를 시험 범위로 대신 쓰지 않는다.

Sensor는 두 physics 조건에서 상대적으로 작은 성능 감소를 보였고, No-Sensor·DS-Sensor는 더 크게 감소했다. LS-Sensor도 unseen physics에서 좋은 성능을 유지한다. 이는 **단일 물체의 물성 변화**에 대한 결과이며, 앞의 다중 물체 학습 실패와 모순되는 것이 아니다. 물체 형상 일반화와 물성 robustness를 분리해서 봐야 한다.

### 11.3 다중 물체의 형상 일반화 — Table III 전체

| 방법 | Seen object CRR | Seen TTF (s) | Unseen object CRR | Unseen TTF (s) |
| --- | --- | --- | --- | --- |
| Sensor | 976.1±86.5 | 42.1±0.6 | 594.4±63.2 | 28.2±2.7 |
| DS-Sensor | 351.5±28.0 | 18.6±0.7 | 186.5±16.1 | 10.7±1.4 |

원문 §V-D, Table III, PDF p. 7. A에서 학습하고 B에서 평가한 결과다. No-Sensor·LS-Sensor는 다중 물체 학습에서 작동하지 않았다는 이유로 이 표에서 제외되었다. 두 방법이 없다는 사실을 숨기거나 임의의 0점 행으로 추가하지 않는다.

이미 촉각을 사용하도록 학습된 정책에서 센서를 꺼버리면 seen과 unseen 모두 성능이 감소한다. 동시에 전체 Sensor 방법 역시 unseen 물체에서 CRR·TTF가 감소한다. 일반화가 확인되었다는 사실과 seen 성능을 그대로 유지했다는 주장은 다르다.

## 12. 실물 결과 — Table I 전체

아래 두 표는 원문 Table I을 읽기 쉬운 행 구조로 옮긴 것이다. **각 조건 30초**, **3 seeds로 학습한 3개 정책 평균**, **CRA는 rounds, TTF는 seconds**다. 소수 자릿수는 원문의 값을 보존하고, 불필요한 trailing zero 일부만 통일했다. [§V-E, PDF p. 7]

### 12.1 Seen objects C1–C5

| 물체 | 방법 | CRA (rounds) | TTF (s) |
| --- | --- | --- | --- |
| C1 | OL | 0.58±0.14 | 13.30±7.77 |
| C1 | No-Sensor | 0.25±0.25 | 7.67±6.80 |
| C1 | CT-Sensor | 2.50±3.25 | 20.00±8.66 |
| C1 | Ours | 4.91±0.52 | 30.00±0.00 |
| C2 | OL | 0.08±0.14 | 4.67±8.08 |
| C2 | No-Sensor | 0.33±0.28 | 14.7±15.01 |
| C2 | CT-Sensor | 0.75±0.66 | 17.67±10.79 |
| C2 | Ours | 2.83±1.26 | 28.67±2.31 |
| C3 | OL | 0.75±0.66 | 18.67±16.29 |
| C3 | No-Sensor | 0.08±0.144 | 3.67±6.35 |
| C3 | CT-Sensor | 2.42±2.10 | 15.33±15.01 |
| C3 | Ours | 2.92±1.38 | 30.00±0.00 |
| C4 | OL | 0.50±0.00 | 24.00±5.29 |
| C4 | No-Sensor | 0.42±0.14 | 16.00±12.17 |
| C4 | CT-Sensor | 1.92±1.46 | 23.00±12.12 |
| C4 | Ours | 4.50±1.73 | 30.00±0.00 |
| C5 | OL | 0.83±1.04 | 13.67±15.18 |
| C5 | No-Sensor | 0.25±0.25 | 12.67±15.53 |
| C5 | CT-Sensor | 1.00±0.87 | 17.00±15.39 |
| C5 | Ours | 2.00±0.00 | 26.67±5.77 |

### 12.2 Unseen objects

| 물체 | 방법 | CRA (rounds) | TTF (s) |
| --- | --- | --- | --- |
| Tomato | OL | 0.25±0.25 | 20.00±17.32 |
| Tomato | No-Sensor | 0.00±0.00 | 0.00±0.00 |
| Tomato | CT-Sensor | 0.33±0.29 | 12.33±15.70 |
| Tomato | Ours | 1.08±0.14 | 27.33±4.62 |
| Apple | OL | 0.67±0.76 | 20.00±17.32 |
| Apple | No-Sensor | 0.33±0.58 | 10.00±17.32 |
| Apple | CT-Sensor | 0.42±0.52 | 15.33±15.01 |
| Apple | Ours | 2.67±1.04 | 30.00±0.00 |
| Orange | OL | 0.50±0.87 | 10.00±17.32 |
| Orange | No-Sensor | 0.75±1.09 | 12.33±15.70 |
| Orange | CT-Sensor | 2.08±2.10 | 24.33±4.93 |
| Orange | Ours | 3.00±1.32 | 30.00±0.00 |
| Soupcan | OL | 1.50±1.32 | 20.00±17.32 |
| Soupcan | No-Sensor | 0.08±0.14 | 2.00±3.46 |
| Soupcan | CT-Sensor | 2.08±2.79 | 19.33±16.77 |
| Soupcan | Ours | 4.25±1.56 | 27.33±4.62 |
| Rubber Duck | OL | 0.33±0.29 | 20.00±17.32 |
| Rubber Duck | No-Sensor | 0.33±0.29 | 20.00±17.32 |
| Rubber Duck | CT-Sensor | 1.50±0.75 | 30.00±0.00 |
| Rubber Duck | Ours | 1.42±0.38 | 29.00±1.73 |

### 12.3 Binary 대 continuous의 직접 근거와 해석 경계

C1에서 binary의 CRA는 **4.91±0.52**, continuous는 **2.50±3.25**다. Apple은 각각 **2.67±1.04**, **0.42±0.52**다. 이 결과는 이 시스템에서 binary 입력으로도 실물 회전이 가능하며, 일부 물체에서는 continuous보다 높은 회전량과 더 작은 보고 편차를 얻었음을 보여준다.

그러나 Rubber Duck에서는 continuous가 **CRA 1.50±0.75, TTF 30.00±0.00**, binary가 **1.42±0.38, 29.00±1.73**으로, 평균값은 continuous 쪽이 조금 더 높다. Table I의 열 평균을 비교하면 binary가 CRA·TTF 모두 높은 것은 **10개 중 9개 물체**다. 이는 표에서 계산한 비교이며, 통계적 유의성 검정이나 일반적인 우월성 보장은 아니다.

저자들은 continuous 신호 정책의 일반화 부족과 큰 편차가 simulation과 real의 force measurement 차이 때문일 수 있다고 해석한다. 이는 **저자의 원인 가설**이며, force calibration 오차만을 독립적으로 조작해 인과관계를 분리한 실험은 제시하지 않는다. CT-Sensor의 calibration 세부도 부족하므로, 이 표로 모든 continuous tactile 방식이 binary보다 불리하다고 일반화할 수 없다. [§V-E]

또한 접촉 bit 16개만으로 위 결과를 얻은 것이 아니다. 관절 위치, 이전 target, 회전축, 시간 이력, 학습 물체 다양성, randomization, system identification이 함께 사용되었다.

### 12.4 본문 표현과 표 수치의 불일치

§V-E는 No-Sensor와 Openloop가 평가 물체를 최대 180도 정도 회전시킨 후 막히거나 떨어뜨린다고 서술한다. 그러나 Table I에는 OL의 Soupcan **1.50회**, C5 **0.83회**, No-Sensor의 Orange **0.75회**처럼 0.5회를 넘는 평균값이 있다. 따라서 ‘모든 물체에서 최대 반 회전’이라는 정량 상한으로 재사용하지 않는다. 관측한 전형적 실패 행동에 대한 본문 설명과 표 전체의 수치를 구분해 보존한다.

## 13. 촉각이 어떻게 기여했는가

### 13.1 Simulation과 real의 센서 반응 — Fig. 7, Fig. 11

Cuboid 회전에서 각각 **400 control steps, 40초**의 센서 활성 궤적을 비교한다. Simulation의 접촉 패턴은 시간 방향으로 더 촘촘하고, 센서별 활성도도 더 다양하다. 특히 센서 1·10이 simulation에서 더 자주 활성화된다고 설명한다. 그럼에도 전체적인 패턴은 비슷하다는 것이 저자의 관찰이다. [§V-F, Fig. 7, PDF p. 8]

저자들은 정책의 0.4초 local window에서 다양한 활성 패턴을 경험하는 것이 실물 관측 분포로의 전이에 도움이 될 수 있다고 **가설**을 제시한다. 정량적인 sim-real 분포 거리나 센서별 precision/recall을 보고한 것은 아니다. Fig. 11은 서로 다른 실물 물체·실행에서 다양한 활성 패턴이 나타나는 추가 사례다. [Appendix E, pp. 14–15]

이 40초 시각화와 Table I의 30초 성능 평가를 같은 trial 길이로 합치지 않는다. 또한 두 궤적이 일대일로 시간 동기화된 동일 접촉을 재현했다는 검증으로 읽지 않는다.

### 13.2 센서 위치 ablation — Table IV 전체

§V-G는 실물 로봇에서 센서를 Fingertip과 Palm 그룹으로 나누고, 각각 제거한 정책을 재학습해 전체 정책과 비교한다. 다만 각 그룹이 정확히 어떤 sensor ID를 포함하는지 정의하지 않으므로, **No-Fingertip이 4개 tip만 제거했는지 손가락 전체 12개를 제거했는지 추정하지 않는다.** [PDF pp. 8–9]

| 방법 | Cuboid 회전 열* | Cuboid TTF (s) | Rubber Duck 회전 열* | Rubber Duck TTF (s) |
| --- | --- | --- | --- | --- |
| Sensor | 4.91±0.52 | 30.00±0.00 | 1.42±0.38 | 29.00±1.73 |
| DS-Sensor | 0.25±0.25 | 7.67±6.80 | 0.33±0.29 | 20.00±17.32 |
| No-Fingertip | 0.17±0.29 | 3.33±5.77 | 0.42±0.14 | 17.00±2.64 |
| No-Palm | 0.42±0.38 | 17.00±14.73 | 0.42±0.14 | 16.67±11.72 |

**표기 주의:** 원문 Table IV는 회전 열을 **CRR**라고 인쇄한다. 그러나 §V-A는 CRR을 simulation-only로 정의하고, 여기서는 실물 평가를 설명한다. Sensor 행도 Table I의 CRA 값과 같다. 따라서 이 문서에서는 회전 열이라고 표시하고 원문의 불일치를 남겼다. 실물 회전수 CRA를 가리키는 것으로 해석할 근거는 있지만, 원문이 CRR이라고 표기했다는 사실을 삭제하지 않는다.

두 센서 제거 조건 모두 전체 방법보다 낮다. 저자들은 손끝과 손바닥 센서가 모두 성공적인 회전에 기여한다고 결론낸다. 이것을 모든 센서가 같은 정도로 중요하다거나 어떤 배치에서도 동일한 결과가 난다는 주장으로 확대하지 않는다.

또한 Table IV의 DS-Sensor 수치는 Table I의 No-Sensor C1·Rubber Duck 수치와 동일하다. **원문의 방법 정의는 다르므로 두 방법을 합치지 않는다.** 수치가 일치하는 이유는 설명되지 않았으며, 오기인지 우연인지 원문만으로 확정하지 않는다.

### 13.3 촉각 이력에서 형상을 예측할 수 있는가 — Fig. 9

저자들은 binary tactile이 물체의 형상 이해에 유용한 정보를 제공하는지 별도 분석한다. [§V-H, PDF pp. 8–9]

| 단계 | 실험 내용 |
| --- | --- |
| 회전 정책 학습 | 125개 irregular column-shaped object의 z축 회전 |
| 데이터 수집 | 총 55,000개 policy rollout |
| Rollout 길이 | 각 200 control steps, 20초 |
| 분할 | Shape-prediction용 train/test로 분할하며 test 물체는 해당 training dataset에 없음 |
| 예측 모델 | 전체 rollout trajectory를 입력으로 받는 temporal-CNN |
| 대조 조건 | 예측 과정에서 rollout의 tactile observation을 0으로 제거하는 ablated model |
| 결과 | Tactile 포함 shape reconstruction MSE **0.22**, 제거 시 **0.45** |

Fig. 9의 qualitative mesh에서도 tactile을 포함한 모델이 형상을 더 잘 재구성하는 예시를 제시한다. 이 분석은 **이력에 형상 예측에 유용한 정보가 들어 있다는 근거**다. 그러나 별도 temporal-CNN의 결과를 근거로 회전 actor 내부가 실제로 같은 mesh를 복원한다고 단정할 수 없다.

전체 20초 rollout을 보는 reconstruction model과 최근 네 프레임을 보는 제어 MLP의 입력 범위도 다르다. MSE의 shape representation·normalization·단위, train/test 물체 수와 rollout 수, temporal-CNN의 상세 구조는 미명시다. ‘Test 물체가 training dataset에 없다’는 설명을 회전 정책의 125개 학습 물체와도 완전히 분리되었다는 의미로 확대하지 않는다.

## 14. 다른 축의 회전과 human-shared control

### 14.1 Table V 전체

| 회전축 | Seen object 회전 열* | Seen TTF (s) | Unseen object 회전 열* | Unseen TTF (s) |
| --- | --- | --- | --- | --- |
| x | 1.68±0.78 | 24.13±6.04 | 2.71±1.37 | 18.2±9.19 |
| y | 1.88±0.38 | 22.46±4.81 | 1.05±0.56 | 23.13±3.01 |
| z | 3.43±1.22 | 29.06±1.45 | 2.48±1.27 | 28.73±1.34 |

근거: §V-I, Table V, PDF pp. 9–10. A·B로 학습하며 각 축의 물체 집합에 대한 평균과 3 seeds를 설명한다. 원문은 이 표의 회전 열도 **CRR**로 인쇄하지만, 본문에서는 낮은 **CRA**를 논의한다. Table IV와 같은 지표 표기 주의를 적용한다. ±가 seed 변동과 물체 간 변동을 어떻게 집계한 값인지 임의 확정하지 않는다.

저자들은 대부분의 물체를 회전시킬 수 있었지만, 특정 물체는 x·y축 회전이 어렵다고 설명한다. 이 두 축에서는 **손가락 링크 측면의 중요한 접촉**이 많이 생기는데 현재 sensor layout이 이를 지원하지 않는다는 것이 설명이다. [§V-I]

표에서 x축 unseen 회전 평균은 z축보다 높지만 TTF는 낮다. 따라서 z축이 모든 열에서 가장 우수하다거나, x·y축의 모든 물체가 실패했다고 요약하지 않는다. 축에 따라 회전량과 유지 시간이 다르게 변한다.

### 14.2 사람이 축 primitive를 선택하는 예시

Fig. 8은 사람이 키보드로 **x → y → z → y** 회전 명령을 차례로 보내고 손이 실행하는 **600 steps, 60초** 예시를 보여준다. 이는 학습한 primitive를 조합해 물체를 재배향할 수 있음을 보여주는 shared-control 시연이다. [§V-I, Fig. 8, PDF pp. 9–10]

상위 명령은 사람이 정한다. 임의의 목표 pose에 대한 자동 sequence planning, 정확한 도달 오차, 자동 완료 판정의 성능을 제시한 것은 아니다. 60초 시연을 Table I의 30초 trial 통계에 추가하여 시행 수를 늘리지 않는다.

## 15. Limitation — 저자들이 밝힌 한계와 실패 조건

독립된 Limitation 절은 없다. 아래는 본문에 **저자들이 실제로 명시한 제약·실패 조건**을 모은 것이다. 원문 미명시 정보나 정리자의 비판은 다음 별도 절로 구분한다.

| 저자 명시 내용 | 조건·이유 | 원문 위치 |
| --- | --- | --- |
| 축별 회전은 일반적인 in-hand reorientation의 단순화된 과업 | 주어진 축으로 회전시키는 문제에 초점 | §I, PDF p. 2 |
| 실제 연속 센서 출력은 비선형·잡음과 보정 오차가 있음 | 정확한 force measurement의 simulation–real 정합이 어려워 binary 사용 | §III-A, p. 3 |
| 단일 시점 state만으로 제어에 충분하지 않을 수 있음 | 현재와 과거 세 state를 함께 사용 | §IV-A.1, p. 4 |
| Simulator 각속도 기반 reward에서 불필요한 진동 행동이 나타남 | 복잡한 물체 운동에서 각속도 신호가 noisy하다고 설명 | §IV-A.3, p. 4 |
| 낮은 감도 센서는 다중 물체 학습에 부족함 | LS-Sensor가 약한 접촉을 놓치며 multi-object training 실패 | §V-C, Fig. 6, p. 6 |
| Continuous tactile 정책의 물체별 일반화·편차 문제가 있음 | Force measurement sim-real gap 때문일 수 있다는 저자 해석 | §V-E, Table I, p. 7 |
| Simulation과 real의 접촉 활성 패턴이 완전히 같지는 않음 | Simulation이 더 조밀·다양하고 특정 센서가 더 자주 활성화 | §V-F, Fig. 7, p. 8 |
| 특정 물체의 x·y축 회전이 어려움 | 중요한 손가락 측면 접촉을 현재 sensor layout이 관측하지 못함 | §V-I, Table V, p. 10 |

낮은 감도 조건의 실패를 제안한 기본 고감도 정책 전체의 실패라고 기록하지 않는다. 반대로 높은 감도 이진 센서를 썼다는 사실만으로 손의 모든 비센서 부위 접촉까지 알아낸다고 해석하지 않는다.

## 16. Future Work — 저자들이 제시한 향후 연구

| 저자 제안 | 해결하려는 문제·확장 | 원문 위치 |
| --- | --- | --- |
| 각 finger link에 더 조밀한 contact sensor array 배치 | x·y축 회전에서 필요한 측면 접촉 관측을 보완할 수 있다는 가설 | §V-I, PDF p. 10 |
| 더 dense한 contact sensor array 탐구 | 현재 접촉 센싱 구성의 확장 | §VI Conclusion, p. 10 |
| 더 다양한 과업으로 시스템 확대 | 축별 회전을 넘어 다양한 조작 기술로 확장 | §VI, p. 10; §I에도 더 복잡한 과업 확장 가능성 언급 |

더 조밀한 센서가 실제로 문제를 해결했다고 검증한 결과는 이 판본에 없다. 또한 3축 tactile, 손목 F/T 결합, 특정 시각 센서와의 fusion을 이 논문의 명시적인 Future Work로 추가하지 않는다.

## 17. 원문에서 확정할 수 없는 구현 정보와 표기 주의

이 절은 **정리자의 재현성·해석 점검**이다. 저자의 명시적 한계·향후 계획과 구분한다.

| 확인이 필요한 항목 | 첨부 v4에서 확인 가능한 범위 |
| --- | --- |
| 실물 FSR 전처리 | Threshold 이진화는 명시. 실제 threshold·LPF·hysteresis·debounce·취득률은 미명시 |
| 정확한 binary 비교 연산 | 개념은 명시되지만 전압 극성·equality·센서별 값은 미명시 |
| 센서 simulation | 독립 fixed sensor link, force norm, 부모 링크 force 제외, 0.01 N 명시. 세부 접촉 형상은 미명시 |
| Observation tensor shape | 성분과 네 프레임 명시. 204는 합산 해설, code shape 미확인 |
| 관측 normalization | 사용은 명시. 통계 갱신·클리핑·실물 이식 방식은 미명시 |
| Sensor lag | Exponential delay와 probability 0.25만 명시. 정확한 구현식 없음 |
| PD system identification | Impulse/sine 응답 정합 명시. 최종 gain과 fit protocol 미명시 |
| Action 처리 | Relative target 누적과 EMA 0.8 명시. action scale·한계·noise 순서 미명시 |
| Reset | 초기 위치 이탈·major-axis 이탈 조건 명시. 수치 threshold·time limit 미명시 |
| Table VI initial position | `(cm)`와 ±0.015를 그대로 보존. ±1.5 cm로 임의 교정하지 않음 |
| Table IV·V 회전 열 | 원문 CRR 표기와 실물 CRA 문맥이 불일치 |
| Table IV DS-Sensor | 일부 값이 Table I No-Sensor와 일치. 이유 미명시, 방법 정의는 구분 |
| Table I과 본문 | ‘최대 180도’ 표현과 0.5회 초과 표 값이 불일치 |
| 평균±값 | Fig. 6은 std 명시. 표 전체의 ± 집계 정의를 동일하다고 확정하지 않음 |
| CT-Sensor 비교 | 결과는 있으나 연속 force calibration·정규화 상세 부족 |
| No-Fingertip mask | 그룹 명칭은 있으나 제거한 정확한 ID·개수는 미명시 |
| Object A/B/C | 구분과 예시는 있으나 전체 mesh·치수·실물 물성 목록은 본문만으로 완성 불가 |
| Shape reconstruction | 125 objects·55,000 rollouts·200 steps·MSE는 명시. 출력 표현·MSE 단위·정확한 분할은 미명시 |
| 축별 정책 구성 | 축 입력과 회전 primitive는 명시. 모든 축을 하나의 checkpoint로 동시에 학습했는지 세부 구성은 이 판본에서 충분히 설명하지 않음 |
| ‘Touch-only’ 해석 | Proprioception·이전 target·회전축·history를 함께 사용. 학습 critic/reward는 simulator 정답 사용 |

Appendix B는 actor와 critic 모두 **ELU**라고 명시한다. 한편 §IV-C의 ELU 뒤 인용 [43]은 참고문헌에서 *Rectified linear units improve restricted Boltzmann machines*로 적혀 있다. 활성함수를 ReLU로 고쳐 적지 않고, 본문·부록의 ELU 명시를 따르며 인용 대응 문제는 별도로 남긴다. [PDF pp. 5, 12, 14]

## 18. 원문 위치 안내와 자료 링크

### 18.1 다시 찾아볼 위치

| 알고 싶은 내용 | 원문 위치 |
| --- | --- |
| 동기·binary array 설계 취지·‘unseen’ 의미 | Abstract, §I, pp. 1–2 |
| 관련 연구와 차이 | §II, pp. 2–3 |
| FSR 취득·threshold·simulation sensor link | §III-A/B, p. 3 |
| 위치·중요 접촉의 두 기능 | §III-D, Fig. 2, pp. 3–4 |
| Actor state·4-frame stack·action EMA | §IV-A.1/2, Fig. 3, p. 4 |
| 회전각 계산·보상 구성·reset | §IV-A.3/4, Fig. 4, pp. 4–5 |
| 비대칭 critic·8192환경·simulation timing | §IV-C, p. 5 |
| 물체 집합 | §V-A, Fig. 5, p. 5 |
| 지표·baseline·학습 곡선 | §V-A/B/C, Fig. 6, pp. 5–6 |
| 실물 전체 결과·단일/다중 sim 결과 | Table I–III, §V-D/E, p. 7 |
| 센서 반응과 배치 ablation | §V-F/G, Fig. 7, Table IV, pp. 8–9 |
| Shape-understanding 분석 | §V-H, Fig. 9, pp. 8–9 |
| 다른 축·shared control | §V-I, Fig. 8, Table V, pp. 9–10 |
| 명시적인 향후 연구 | §VI, p. 10 |
| PPO 상세 | Appendix B, p. 14 |
| DR 모든 값·PD system identification | Appendix C, Table VI, p. 14 |
| 보상 상수와 가중치 | Appendix D, 식 (3)–(9), p. 14 |
| 센서 ID 지도·추가 실물 활성 궤적 | Fig. 10–11, Appendix E, pp. 14–15 |

### 18.2 1차 자료

- **주 분석 원문:** 사용자가 첨부한 [arXiv 2303.10880v4](https://arxiv.org/abs/2303.10880v4), [동일 버전 PDF](https://arxiv.org/pdf/2303.10880v4). 본문의 방법·수치·표기 주의는 이 판본 기준이다.
- **공식 서지:** [RSS XIX proceedings 논문 페이지](https://www.roboticsproceedings.org/rss19/p036.html), [DOI](https://doi.org/10.15607/RSS.2023.XIX.036). 게재 정보 확인에 사용했다.
- **저자 프로젝트:** [Touch Dexterity](https://touchdexterity.github.io/). 논문·영상·코드 링크가 있다.
- **프로젝트가 연결하는 코드:** [YingYuan0414/in-hand-rotation](https://github.com/YingYuan0414/in-hand-rotation). 링크 존재만 확인했으며, 이번 정리에서 code commit을 고정해 분석하거나 실행하지 않았다.

### 18.3 이번 정리의 검증 범위

첨부 PDF의 텍스트와 핵심 수식·도표 렌더를 대조했다. 식 (1)–(9), Table I–VI의 수치와 의미, 원문에 있는 표기 불일치를 점검했다. Table I–V의 평균±값 132개 셀을 독립 검토 기록과 대조했으며, Table VI와 보상식은 PDF 렌더와 대조했다. 문서의 수식 구분자·Markdown 표 구조와 저장소 내부 링크 373개·anchor 참조 88개·14편의 조사–논문 양방향 연결을 검사했고 오류가 없었다. 이러한 정적 검사는 정책 재현이나 실제 GitHub 웹페이지의 수식 렌더를 직접 확인한 것과 다르다.
