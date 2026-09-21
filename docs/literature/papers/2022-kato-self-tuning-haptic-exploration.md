# A Self-Tuning Impedance-Based Interaction Planner for Robotic Haptic Exploration

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](../reviews/README.md) · [전체 논문](README.md) · [Wrist Wrench 조사 — C1](../reviews/2026-09-21_wrist-wrench-manipulation-survey.md#c1)

## 1. 논문 정보와 확인 범위

- **저자:** Yasuhiro Kato, Pietro Balatti, Juan M. Gandarias, Mattia Leonori, Toshiaki Tsuji, Arash Ajoudani
- **게재:** IEEE Robotics and Automation Letters, 7(4), pp. 9461–9468, 2022. [IEEE 출판 기록](https://ieeexplore.ieee.org/document/9829927/) · [DOI: 10.1109/LRA.2022.3190806](https://doi.org/10.1109/LRA.2022.3190806)
- **확인 원문:** 사용자 제공 PDF 8쪽 전체. 표지에 `arXiv:2203.05413v2`, 2022-09-02, `PREPRINT VERSION. ACCEPTED JUNE, 2022`로 표기된 저자 공개본이다. IEEE 최종 편집본을 읽은 것으로 표시하지 않는다. [공개 버전 기록](https://arxiv.org/abs/2203.05413v2)
- **원문 PDF SHA-256:** `2740208f97c67cfc820c7a5f880ab8ec679c1335702fe4c22f2adeda2ad6e7a5`
- **원문이 안내한 보충 자료:** [실험 영상](https://youtu.be/DDqosdN2274). 이번 정독에서 영상은 재생·검증하지 않았다.
- **확인하지 않은 범위:** 저자 구현 코드, 원시 실험 로그, 하드웨어 재현, 인용 논문 27편의 전체 본문. 원문에 코드 공개 주소는 명시되어 있지 않으며, 코드가 어디에도 없다고 단정하지 않는다.
- **정리일·등록:** 2026-09-21. 기존 Wrist Wrench 조사 `C1`의 후속 정독이며 신규 발굴 후보나 RL 사례로 중복 등록하지 않는다.

텍스트 추출과 전 페이지 렌더링으로 본문, Fig. 1–9, 식 (1)–(9), Algorithm 1–2와 참고문헌을 대조했다. 아래 페이지는 첨부 PDF 첫 페이지를 p.1로 센다. 실험 수치는 원문 본문·그림을 구분해 기록하며, 별도 결과 Table은 없다.

**핵심:** 로봇이 미지의 평면 미로에서 벽과 접촉할 때, 두 힘 임계값 사이의 실제 이동으로 다음 진행 방향을 정한다. 막히면 과거 운동 방향과 현재 외력 방향을 이용한 Bouncing으로 전환한다. 동시에 원하는 진행 방향에는 큰 강성을, 횡방향에는 작은 강성을 배치하여 접촉 중에도 전진과 순응성을 양립시킨다. **신경망이나 RL을 학습하는 논문이 아니라, 온라인 피드백 기반 trajectory planner와 self-tuning impedance의 결합**이다. [원문 §I–III, §V]

## 2. 문제 설정과 전제

미로의 지도나 경로를 알고 충돌을 피하는 대신, 환경과의 접촉을 이용해 움직일 수 있는 방향을 찾아간다. 유연한 막대를 관 안으로 밀면 주변 형상을 따라 휘어지는 현상이 동기다. 카메라·깊이 센서 없이도 로봇의 순응성을 활용해 경로를 생성할 수 있는지가 질문이다. [원문 §I, PDF pp.1–2]

| 구분 | 원문에서 사용하는 정보·범위 |
| --- | --- |
| 사용 가능한 정보 | 로봇의 현재 pose·운동 이력, 내부 관절 토크로 추정한 외력, 이전 desired pose, 수동 설정된 임계값·속도·임피던스 파라미터 |
| 주어지지 않는 정보 | 미로의 사전 지도·상세 환경 모델, 실행 중 영상·깊이 관측 |
| 시작 | 로봇을 시작 위치로 보낸 뒤 Exploration 실행. 시작 위치 선정·초기 진행 벡터 설정 절차의 상세는 미명시 |
| 실험 과업 | 말단에 부착한 peg를 평면 미로의 통로를 따라 이동. 나사가 추가된 통로에서는 이를 밀면서 통과 |
| 범위 밖 | 자유 물체 pose 추정, 물체 grasp 학습, 일반적인 3D 미로 탐색, 전역 최단 경로 최적화 |
| 완료·중단 | 실험은 미로 통과와 과도한 힘에 의한 Error 중단을 구분. 성공 종료 검출기의 구현은 미명시 |

`Haptic information only`는 외력 외의 모든 정보를 배제한다는 뜻이 아니다. 두 알고리즘 모두 로봇의 위치·운동 정보를 이용한다. 또한 환경을 모른다는 조건과 로봇 동역학·Jacobian을 제어에 사용하는 것은 서로 다르다. [원문 §II–IV]

## 3. Related Work와 새 기여의 위치

독립된 Related Work 절은 없으며 §I에서 선행연구를 비교한다. 아래는 저자들의 비교 구도이고 인용 논문을 별도로 정독한 결과는 아니다.

| 계열 | 저자들이 설명하는 장점·제약 | 이 논문의 위치 |
| --- | --- | --- |
| RRT·PRM 기반 경로 계획, Ref. [4]–[5] | 환경 모델이 필요하고 복잡한 미지 환경의 모델링이 어려움 | 사전 지도 없이 접촉 중 경로 생성 |
| Contact-based planning, Ref. [6]–[7] | 접촉으로 불확실성을 줄이지만 지도·계산 비용 부담 | 로컬 외력·변위 기반의 반응적 planning |
| Trajectory scaling·admittance, Ref. [8]–[9], [23] | 외부 환경에 빠르게 반응하지만 탐색·경로 찾기에 추가 설계가 필요 | 속도 scaling을 부호 포함 범위로 확장한 Bouncing |
| Variable impedance, Ref. [10]–[19] | 정확한 추종·힘 생성과 부드러운 접촉 사이를 조절 | 모든 축을 같은 강성으로 만들지 않고 진행 방향에 정렬 |
| 저자들의 선행 self-tuning impedance, Ref. [20] | 운동 방향에 강성·감쇠 타원체의 주축을 정렬 | 기존 임피던스 unit을 새 interaction planner·FSM과 결합 |

따라서 **self-tuning impedance 자체를 이 논문에서 처음 제안한 것처럼 서술하면 안 된다.** 새 기여의 중심은 Exploration·Bouncing의 interaction planner, 상태 전환, 그 경로에 맞춘 기존 impedance unit의 결합과 미로 실험이다. [원문 §I, §II-B, §III]

## 4. 실물 환경·센서·입출력 경계

| 항목 | 확인 내용 |
| --- | --- |
| 로봇·구동 | Franka Emika Panda, torque-controlled arm. 제어식은 일반적인 관절 수 $n$으로 기술하며 제조사 상세 사양을 별도 보완하지 않음 |
| 도구·환경 | 말단 고정 peg: 직경 30 mm, 길이 55 mm. Peg와 미로는 rigid PLA 3D print. 직선·곡선·L형 부품으로 3개 미로 구성 |
| 외력 신호 출처 | 로봇 **내부 관절 토크 sensing으로 추정한 외부 interaction force**. 별도 손목 6축 F/T를 추가 장착한 실험이 아님 |
| 실제 사용량 | 알고리즘은 pose·force와 운동 이력을 사용. Bouncing 명령은 $x,y$ 성분으로 명시. Fig. 6–7은 힘 $x,y,z$를 표시하지만 모멘트 사용 효과는 검증하지 않음 |
| 센서 세부 성능 | 관절 토크 센서 모델·측정 범위·분해능·정확도·감도·샘플링률, 말단 외력 추정 오차·대역폭은 미명시 |
| 전처리 | 외력 추정기의 식, bias·중력 보상·필터 구현은 미명시. 잡음 영향을 줄이기 위해 힘 임계값을 비교적 높게 설정했다고 설명 |
| 좌표계 | Cartesian 공간에서 계획하고 실험 운동은 $xy$ 평면. 센서/도구/base 간 변환식과 frame 명칭의 상세는 미명시 |
| 외부 관측 | 카메라·depth 등의 외부 센서를 planner 입력에 사용하지 않음. 논문 사진·RViz 시각화는 policy vision 입력이 아님 |
| 소프트웨어·주기 | ROS, C++. 제어 루프 간격 $\Delta T$는 식에 등장하지만 수치·명령 주파수는 미명시 |

근거: §II–IV, Fig. 2, Fig. 5–9, PDF pp.2–7. 힘 임계값 5·7·60 N은 알고리즘 설정이지 센서 검출 한계나 최대 측정 범위가 아니다.

### 정보가 소비되는 위치

| 소비 구성요소 | 입력 → 내부 사용 → 출력 |
| --- | --- |
| Exploration | 현재 외력으로 pose 저장 시점을 결정 → 두 실제 위치의 차이 → 새 desired pose |
| Bouncing | 외력 방향 + 과거 실제 이동 방향 → 축별 signed velocity scaling → 새 desired pose |
| FSM·안전 중단 | 최근 실제 변위와 외력 → 탐색/반동 전환 또는 Error |
| Self-tuning impedance | desired pose 변화 방향 → 강성·감쇠 주축 정렬 → $\mathbf{K}_c,\mathbf{D}_c$ |
| Cartesian impedance controller | desired/actual pose·velocity와 임피던스 → Cartesian 제어 힘 → 관절 토크 명령 |

학습 actor·critic·teacher·reward·privileged training input은 **해당 없음**이다. Planner가 출력하는 것은 학습된 policy action이 아니라 제어기의 desired pose이며, 추정 외력과 controller가 생성하는 제어 힘은 같은 변수가 아니다. [원문 Fig. 2, §II–III, §V]

## 5. Main Method — 전체 폐루프

Fig. 2의 신호 흐름을 계산 의존 관계로 재구성하면 다음과 같다. 코드의 callback 실행 순서까지 공개된 것은 아니다.

1. 로봇에서 actual pose와 추정 외력을 받아 최근 actual motion을 계산한다.
2. FSM 상태에 따라 Exploration 또는 Bouncing이 desired pose를 갱신한다. 큰 외력은 Error 중단 조건으로 사용한다.
3. Desired pose의 진행 방향으로 self-tuning unit의 강성·감쇠 주축을 맞춘다.
4. Desired/actual pose·velocity 오차에 임피던스를 적용하여 Cartesian 제어 힘과 관절 토크를 생성한다.
5. 실제 접촉으로 로봇이 변위·외력 피드백을 만들고, 이것이 다시 다음 방향 결정의 입력이 된다.

여기서 순응성은 단순한 충격 완화 기능이 아니다. 벽에 의해 실제 운동이 통로 방향으로 편향되는 현상을 허용하며, **Exploration은 바로 그 실제 변위를 다음 경로의 단서로 사용한다.** 그래서 planner와 impedance를 독립적인 장식 요소로 분리하면 방법의 핵심을 놓치게 된다. [원문 §III-A1, Fig. 3, §IV-B]

## 6. Exploration — 두 접촉 시점의 실제 변위로 방향 갱신

### 6.1. 무엇을 저장하는가

기본 상태는 Exploration이다. 자유 공간 또는 접촉 중에도 전진할 수 있는 경우에 사용한다. 힘이 첫 임계값 $F_{\mathrm{th,low}}$에 도달하면 **실제 pose**를 $\mathbf{r}_{\mathrm{low}}$로 저장한다. 이어 두 번째 임계값 $F_{\mathrm{th,high}}$에 도달하면 $\mathbf{r}_{\mathrm{high}}$를 저장한다. 두 threshold는 별도의 RL reward나 분류기 출력이 아니다. [원문 §III-A1, Algorithm 1, PDF p.3]

### 6.2. 저장한 변위를 명령으로 바꾸는 과정

Algorithm 1의 lines 11–14는 다음과 같다. 여기서는 실험의 병진 경로 갱신을 설명한다.

```math
\begin{aligned}
\mathbf{r}_{\mathrm{nd}} &= \mathbf{r}_{\mathrm{high}}-\mathbf{r}_{\mathrm{low}},\\
\hat{\mathbf{r}}_{\mathrm{nd}} &= \frac{\mathbf{r}_{\mathrm{nd}}}{\lVert\mathbf{r}_{\mathrm{nd}}\rVert_2},\\
\Delta\mathbf{r}_d &= \hat{\mathbf{r}}_{\mathrm{nd}}\,v_{\mathrm{constE}}\,\Delta T,\\
\mathbf{x}_{d,t} &= \mathbf{x}_{d,t-1}+\Delta\mathbf{r}_d.
\end{aligned}
```

- 위치 차이는 벽 접촉 이후 **실제로 이동한 방향**을 담는다. 환경 법선이나 접촉점 좌표를 명시적으로 추정하는 단계는 없다.
- 정규화는 두 threshold 사이에 이동한 거리를 그대로 명령 크기로 쓰지 않고 방향만 사용하기 위한 것이다.
- 다음 desired pose는 현재 actual pose가 아니라 **이전 desired pose에 증분을 누적**해 만든다. 따라서 실제 운동이 지연되면 추종 오차가 커질 수 있다.
- 실험에서는 $F_{\mathrm{th,low}}=5$ N, $F_{\mathrm{th,high}}=7$ N, $v_{\mathrm{constE}}=0.04$ m/s다. 잡음 영향을 줄이려는 threshold 선택이 저강성 조건에서 큰 오차가 쌓이는 원인으로도 논의된다. [원문 §IV-B, PDF p.5]

Fig. 3은 벽을 따라 변형된 실제 이동으로 새 방향을 얻는 상황을 보여준다. 반면 벽을 정면으로 밀어 이동이 거의 없거나 L형 코너에 갇히면 두 위치 차이만으로 유효한 탈출 방향을 정하기 어렵다. 이 경우를 처리하는 것이 Bouncing이다.

**재현 주의:** Algorithm 1은 검출 flag의 재설정, 최초 threshold 검출 전 진행 벡터, 영변위 정규화 예외를 완전히 명시하지 않는다. Fig. 8에서 반복적인 방향 갱신은 관찰되지만, 그 사실로 누락된 reset 코드를 보완해 쓰지는 않는다.

## 7. Bouncing — 힘 방향과 과거 진행 방향으로 탈출 명령 생성

### 7.1. 두 벡터의 역할

로봇이 막힌 순간에는 현재 actual displacement만으로 이동 가능한 방향을 얻기 어렵다. 대신 과거 $m$ step의 운동 추세와 현재 외력 방향을 사용한다. [원문 §III-A2, Fig. 4, Algorithm 2, PDF pp.3–4]

```math
\mathbf{r}_{\mathrm{trend}}=\mathbf{x}_t-\mathbf{x}_{t-m},\qquad
\hat{\mathbf{r}}_{\mathrm{trend}}=\frac{\mathbf{r}_{\mathrm{trend}}}{\lVert\mathbf{r}_{\mathrm{trend}}\rVert_2},\qquad
\hat{\mathbf{F}}_{\mathrm{ext}}=\frac{\mathbf{F}_{\mathrm{ext}}}{\lVert\mathbf{F}_{\mathrm{ext}}\rVert_2}.
```

운동 추세는 직전에 어느 방향으로 진행해 막혔는지 나타내고, 외력 방향은 현재 접촉에서 받는 반작용의 방향을 제공한다. Algorithm 2는 이를 초기화 부분에서 정규화하고 축별 angle·scaling을 계산한 다음, control loop에서 desired pose를 적분하는 구조다. 지속적으로 매 주기 angle을 다시 계산한다고 단정하지 않는다.

### 7.2. 각도 → 축별 속도 scaling

원문 식 (8)은 두 벡터의 내적을 이용한 각도 계산이다.

```math
\phi=\arccos\left(
\frac{\langle\hat{\mathbf{F}}_{\mathrm{ext}},\hat{\mathbf{r}}_{\mathrm{trend}}\rangle}
{\lVert\hat{\mathbf{F}}_{\mathrm{ext}}\rVert\,\lVert\hat{\mathbf{r}}_{\mathrm{trend}}\rVert}
\right).
```

Algorithm 2는 $x,y$ 방향에 대응하는 $\phi(x),\phi(y)$를 사용한다. 다음 식은 원문 lines 5–11의 부호 분기를 한 식으로 다시 쓴 것이다.

```math
\begin{aligned}
\alpha & = \begin{cases}
-(1-\lvert\cos\phi(x)\rvert), & \hat F_{\mathrm{ext}}(x)<0,\\
1-\lvert\cos\phi(x)\rvert, & \hat F_{\mathrm{ext}}(x)\geq0,
\end{cases}\\
\beta & = \begin{cases}
-(1-\lvert\cos\phi(y)\rvert), & \hat F_{\mathrm{ext}}(y)<0,\\
1-\lvert\cos\phi(y)\rvert, & \hat F_{\mathrm{ext}}(y)\geq0.
\end{cases}
\end{aligned}
```

두 방향이 수직이면 scaling 크기가 커지고, 같은 축으로 평행·반평행이면 작아진다. 외력 성분의 부호를 반영하므로 $\alpha,\beta\in[-1,1]$이며 양의 전진뿐 아니라 반대 방향 명령도 가능하다. Fig. 4에서는 기존 전진 방향과 같은 축의 힘 성분에 의한 이동을 억제하고 횡방향으로 움직여 코너를 빠져나가는 개념을 보여준다.

```math
\Delta r_d(x)=\alpha v_{\mathrm{constB}}\Delta T,\qquad
\Delta r_d(y)=\beta v_{\mathrm{constB}}\Delta T,\qquad
\mathbf{x}_{d,t}=\mathbf{x}_{d,t-1}+\Delta\mathbf{r}_d.
```

실험의 $v_{\mathrm{constB}}=0.05$ m/s, $m=2000$ steps다. 이 출력은 힘 명령이 아닌 **위치 증분**이다. Exploration과 달리 전체 2D 증분을 다시 unit vector로 정규화하는 단계가 없으므로 0.05 m/s를 모든 순간의 Cartesian 속력으로 해석하지 않는다. 이는 원문 update 식의 해설이다.

**표기 주의:** 본문은 $\hat{\mathbf{F}}_{\mathrm{ext}}\in\mathbb R^6$와 $\hat{\mathbf{r}}_{\mathrm{trend}}\in\mathbb R^3$를 함께 쓰고, Algorithm 2의 `getAngleBetween`에는 force의 축 성분을 넣는다. 실제 계산에서 3D force를 선택하는 방식·축 방향 벡터 구성은 완결된 형태로 명시하지 않는다. 식 (8)의 차원을 임의로 맞추거나, 6D Wrench 전체를 혼합해 각도를 계산했다고 단정하지 않는다.

## 8. FSM — 모드 전환과 안전 중단

식 (9)는 일정 시간 동안의 actual displacement로 갇힘을 판단한다.

```math
\Delta d=\lVert\mathbf{x}_t-\mathbf{x}_{t-h}\rVert_2.
```

| 상태·전환 | 조건과 후속 처리 |
| --- | --- |
| 시작 → Exploration | 시작 위치로 이동한 뒤 기본 탐색 실행 |
| Exploration → Bouncing | $\Delta d<R_{\mathrm{th}}$. 실험에서 $R_{\mathrm{th}}=1$ mm, $h=500$ ms. 순간 속도 하나가 아니라 구간 실제 변위로 판단 |
| Bouncing → Exploration | Interaction force가 감소하면 복귀. 구체적인 복귀 threshold·hysteresis·dwell time은 미명시 |
| 큰 외력 → Error | 실험의 최대 힘 threshold는 60 N. 이를 넘는 큰 힘으로 task execution 중단 |

근거: §III-B, 식 (9), §IV-B, PDF pp.4–5. FSM 전환과 Bouncing의 운동 추세는 서로 다른 이력을 사용한다. **500 ms의 갇힘 판단 창과 2000-step 추세 창을 같은 값으로 합치면 안 된다.** 제어 주파수가 없어 2000 steps를 임의로 2초로 환산하지 않는다.

Error는 학습 safety critic이나 최적화 constraint가 아니다. 또 60 N 중단을 모든 순간 접촉력이 60 N 이하임을 보장하는 제어법으로 표현할 수 없다. Fig. 7의 중단 장면에는 65 N 표시도 있다.

## 9. Self-Tuning Impedance와 관절 토크 실행

### 9.1. 진행 방향에 임피던스 주축을 맞춘다

원문 식 (4)–(7)은 직교 기저 $\mathbf{U}$로 diagonal stiffness·damping을 회전시키는 구조다. 첫 기저 방향은 **desired motion** $\mathbf{x}_{d,t}-\mathbf{x}_{d,t-1}$에 정렬하고 나머지 기저는 직교하도록 만든다. Actual motion을 쓰는 Exploration의 방향 추출과 구분해야 한다. [원문 §II-B, PDF p.2]

```math
\begin{aligned}
\mathbf{K}_c &= \mathbf{U}\boldsymbol{\Sigma}_k\mathbf{U}^T, &
\boldsymbol{\Sigma}_k &= \mathrm{diag}(k_{\max},k_{\min},k_{\min}),\\
\mathbf{D}_c &= \mathbf{U}\boldsymbol{\Sigma}_d\mathbf{U}^T, &
\boldsymbol{\Sigma}_d &= \mathrm{diag}(d_{\max},d_{\min},d_{\min}).
\end{aligned}
```

큰 강성은 진행을 유지하고, 작은 횡방향 강성은 벽을 만났을 때 경로에 맞춰 actual motion이 변하도록 허용한다. 방향이 바뀌면 고정된 세계 좌표의 한 축을 계속 단단하게 만드는 대신 주축도 함께 회전한다. 실험은 $k_{\max}=1000$ N/m, $k_{\min}=300$ N/m를 사용한다.

원문은 $d_{\max}=2\zeta\sqrt{k_{\max}}$와 대응하는 최소 damping 개념을 제시하지만 실험의 $\zeta$ 수치·damping 세부 설정은 명시하지 않는다. 따라서 임의로 critical damping이나 특정 damping gain을 확정하지 않는다.

**범위 주의:** 일반 controller 설명은 6×6 임피던스지만 위 기저·diagonal 식은 3개 방향으로 제시된다. 실험 설명은 $xy$ 방향 tuning에 초점을 두며, Fig. 6–7의 self-tuning 패널에서 $K_c(z)$는 약 1000 N/m로 일정하다. 그러므로 모든 비진행 3D 축이 실제 실험 내내 300 N/m였다고 단정하지 않는다. 6D 행렬로의 확장·회전 stiffness·$z$축 처리의 상세는 미명시 사항으로 남긴다.

### 9.2. Desired pose와 임피던스가 토크 명령이 되는 과정

원문 식 (1)–(3)을 묶으면 다음과 같다.

```math
\begin{aligned}
\mathbf{F}_c &= \mathbf{K}_c(\mathbf{x}_d-\mathbf{x})
 +\mathbf{D}_c(\dot{\mathbf{x}}_d-\dot{\mathbf{x}}),\\
\boldsymbol{\tau}_{\mathrm{ext}} &= \mathbf{J}(\mathbf{q})^T\mathbf{F}_c+\boldsymbol{\tau}_{\mathrm{st}},\\
\boldsymbol{\tau} &= \mathbf{M}(\mathbf{q})\ddot{\mathbf{q}}
 +\mathbf{C}(\mathbf{q},\dot{\mathbf{q}})\dot{\mathbf{q}}
 +\mathbf{g}(\mathbf{q})+\boldsymbol{\tau}_{\mathrm{ext}}.
\end{aligned}
```

$\mathbf{F}_c$는 pose·velocity 오차에서 만든 Cartesian 제어 힘이며, planner 입력인 추정 외력 $\mathbf{F}_{\mathrm{ext}}$와 다르다. $\mathbf{J}^T$가 이를 joint torque로 연결하고 $\boldsymbol{\tau}_{\mathrm{st}}$는 Jacobian null space의 secondary task 항이다. $\mathbf{M},\mathbf{C},\mathbf{g}$는 로봇 동역학 항이다. Null-space 목적·gain, torque clipping·rate limit, acceleration 구현의 상세는 미명시다.

원문은 식 (2)의 $\boldsymbol{\tau}_{\mathrm{ext}}$를 external torque라고 부르면서 위 제어 관계를 제시한다. 이 표기를 근거로 센서 토크에서 외력을 복원하는 observer 알고리즘까지 공개되었다고 해석하지 않는다.

### 9.3. 학습·최적화가 있는가

**없다.** Self-tuning은 피드백으로 경로와 임피던스 방향을 온라인 조정한다는 뜻이다. Actor/critic, loss·reward, replay, demonstration, curriculum, domain randomization, sim-to-real 학습 절차는 없다. 힘 threshold는 preliminary trial로 수동 조정한다. 저자도 planner와 impedance unit이 learning technique에 의존하지 않는다고 명시한다. [원문 §V, PDF pp.7–8]

## 10. 실험 구성과 정량 결과

### 10.1. 무엇을 고정하고 무엇을 비교하는가

세 조건은 **같은 Exploration·Bouncing 로직**을 사용하고 impedance profile을 바꾼다. High는 Cartesian 세 축의 고정 강성 1000 N/m, Low는 300 N/m, Self-tuning은 진행 방향 1000·횡방향 300 N/m의 방향성 tuning이다. 따라서 비교의 중심은 planner 유무가 아니라 **동일 planner 아래 임피던스 설계의 영향**이다. [원문 §I, §IV-B]

### 10.2. 실험 1 — 나사 없는 기본 미로

아래 수치는 §IV-B 본문이 보고한 값이며, Fig. 6의 특정 snapshot 힘과 구분한다.

| 조건 | 완료 여부 | 평균 interaction force | 최대 추종 오차 | Completion time (CT) | Exploration distance (ED) |
| --- | --- | --- | --- | --- | --- |
| High impedance | 완료 | 약 23 N | 약 0.04 m | 31 s | 1.16 m |
| Low impedance | 완료 | 약 18 N | 약 0.10 m | 36 s | 1.13 m |
| Self-tuning | 완료 | 약 11 N | 약 0.04 m | 32 s | 1.13 m |
| 가정한 최적 collision-free 경로 | 비교 기준 | — | — | 26.0 s | 1.06 m |

근거: PDF p.5, Fig. 6 (p.6). 최적값은 같은 관측 조건에서 실행한 다른 planner의 실측 baseline이 아니라 저자들이 정의한 기대 경로·시간이다. Self-tuning의 CT·ED는 이 기준보다 각각 약 23%·7% 크다고 보고한다.

Low가 Self-tuning보다 평균 힘이 큰 이유에 대한 **저자 설명**은 다음과 같다. 강성이 낮으면 threshold에 도달하기까지 더 큰 desired–actual 오차가 허용되고, 낮은 추종 능력으로 그 오차를 회복하기 어렵다. Self-tuning은 전진 방향의 오차를 억제하면서 불필요한 방향의 접촉 강성을 낮춘다. 단순히 모든 강성을 낮추면 항상 힘이 가장 작아진다는 결과가 아니다.

Fig. 6의 33·24·13 N은 선택한 순간의 표시값으로 위 평균 23·18·11 N을 대체하지 않는다. 반복 trial 수, 평균의 집계 방식·표준편차·신뢰구간은 명시하지 않으므로 세 조건의 통계적 성공률로 변환하지 않는다.

### 10.3. 실험 2 — 나사로 저항을 추가한 미로

기본 통로에 screws를 넣어 추가 저항을 만든다. 새로운 물체 pose goal이나 독립적인 object rearrangement 평가가 아니라 탐색 경로의 disturbance 실험이다. [원문 §IV-B, Fig. 5·7]

| 조건 | 관찰 결과 | 원문이 설명하는 실패·성공 경로 |
| --- | --- | --- |
| High | Error로 중단 | 큰 impedance 상태로 접촉하며 힘이 증가해 60 N threshold 도달 |
| Low | Error로 중단 | 나사에 의해 실제 운동이 지연되고 최대 오차 약 0.07 m. 약 8 s에 Bouncing으로 전환한 뒤 큰 힘으로 중단 |
| Self-tuning | 통과 | 진행 방향의 교란 저항성을 유지하면서 횡방향 순응성으로 큰 힘 억제 |

Fig. 7 snapshot의 65·60·6 N은 장면별 값이다. 특히 6 N을 Self-tuning trial의 평균 또는 최대 힘으로 옮겨 적지 않는다. 논문은 이 조건의 반복 실험 성공률 표나 모든 수치 지표를 별도로 제공하지 않는다.

### 10.4. 실험 3 — 다른 두 미로

- **Maze 2:** 곡선 위주 형상에서 방향을 반복적으로 갱신하고 끝부분에서 Bouncing. 최대 추종 오차 약 0.04 m. [Fig. 8]
- **Maze 3:** U형 구간으로 큰 방향 변화가 필요한 경로를 통과. 최대 추종 오차 약 0.06 m. [Fig. 9]

두 경우 모두 사전 환경 모델 없이 통과하는 예를 제시한다. 학습 train/test split이 있는 일반화 실험은 아니며, 임의 topology·분기·막다른 길을 모두 해결한다는 보장으로 확대하지 않는다. [원문 §IV-C, PDF pp.6–7]

## 11. 검증이 메소드의 어떤 부분을 뒷받침하는가

| 비교·관찰 | 대응하는 메소드 요소 | 해석할 수 있는 범위와 남는 공백 |
| --- | --- | --- |
| High / Low / Self-tuning | 방향별 impedance 설계 | 동일 planner에서 tracking·힘·통과 결과가 달라짐. Pure F/T 관측 제거 비교는 아님 |
| 빈 통로 / 나사 추가 | 진행 방향 추종과 횡방향 순응성 | 추가 저항에서 고정 high·low의 실패와 self-tuning 성공을 보임 |
| L형 코너의 Bouncing 구간 | 갇힘 감지·탈출 방향 생성 | 실제 상태 전환을 확인. Bouncing을 제거한 별도 정량 ablation은 없음 |
| Maze 2·3 | 접촉 기반 경로 적응 | 다른 형상에서도 동작하는 실물 사례. 전역 탐색의 completeness 검증은 아님 |

Force 입력 제거, pose history 제거, threshold sweep, $m/h$ 민감도, 동적 장애물, deformable environment, RL baseline과의 체계적 비교는 이 원문에 없다. 이는 **이번 정독에서 확인한 검증 범위**이며 저자들이 명시한 Limitation 목록과는 구분한다.

## 12. Limitation — 저자들이 밝힌 한계·범위

1. **Exploration만으로 처리하기 어려운 접촉이 있다.** 벽에 수직으로 부딪히거나 L형 제약에 막히면 두 접촉 시점의 변위로 movable direction을 찾기 어렵다. Bouncing을 도입한 직접적인 이유다. [§III-A2, PDF p.3]
2. **힘 threshold 선택은 자동화되지 않았다.** 합리적인 값을 preliminary trial로 설정해야 한다고 명시한다. [§V, PDF p.7]
3. **현재 연구는 rigid environment를 대상으로 한다.** 저자들은 이 조건에서 threshold 설정의 주된 관심이 signal noise였다고 설명한다. 임의 재질에 대한 자동 threshold 적응을 검증하지 않았다. [§V, PDF p.7]

독립된 Limitation 절은 없다. 위 항목과 별도로, 안정성을 tank-based passivity observer로 분석할 수 있다고 Ref. [26]을 언급하지만 **이 논문에서 해당 observer를 구현하거나 전체 전환 시스템의 passivity를 증명한 결과는 제시하지 않는다.** 이는 검증 수준에 관한 정독상의 구분이다. [§V, PDF p.8]

## 13. Future Work — 저자들이 제시한 향후 연구

- **3D maze로 확장:** 현재 평면 미로를 넘어서는 탐색으로 방법을 확장할 계획이다.
- **Bio-inspired haptic navigation:** 시각이 제한된 곤충과 worms·moles 등 동물의 행동에 기반한 촉각 탐색 방식으로의 적용을 연구할 계획이다.

근거: §V 마지막 문단, PDF p.8. Threshold 자동화나 RL 통합을 이번 논문의 명시적 Future Work로 추가하지 않는다. 위 두 계획 역시 이미 검증된 성과가 아니다.

## 14. 재현에 필요한 미명시 정보와 표기 주의사항

| 항목 | 확인 범위·주의 |
| --- | --- |
| 센서→외력 추정 | Observer·보상·필터·frame transform과 calibration의 상세 미명시 |
| 힘의 scalar threshold | Vector force와 scalar threshold를 비교하는 표기. Norm·성분별 비교·합산의 정확한 구현 미명시. 6D force/torque를 단위 구분 없이 합친다고 가정하지 않음 |
| 각도 표기 | 본문은 $\phi(x),\phi(y)\in[-\pi,\pi]$라 쓰지만 식 (8)은 arccos. 부호는 Algorithm 2에서 force 성분으로 따로 결정하므로 부호 있는 각도 구현을 임의 보충하지 않음 |
| 차원·행렬 구성 | 6D pose/force 표기, 3D motion basis, 2D bouncing update 사이의 구체적 projection과 rotational control 미명시 |
| Exploration bookkeeping | Threshold flag reset·초기 direction·영벡터 처리·반복 접촉 이벤트 처리 미명시 |
| Bouncing 갱신 | Algorithm 2의 initialization 재실행 시점, 영외력·영운동 이력 처리 미명시 |
| FSM | Force 감소 시 복귀의 수치 조건·hysteresis, 안전 조건 우선순위 미명시 |
| 제어 설정 | $\Delta T$, sensing/control frequency, damping 실험값, null-space·torque 제한 미명시 |
| 성능 집계 | Trial 수·분산·성공 판정 코드·평균 힘 집계식 미명시. 순간 힘·평균 힘·최대 힘을 혼용하지 않음 |

## 15. 원문 위치 빠른 찾아보기

| 확인할 내용 | 원문 위치 |
| --- | --- |
| 문제·선행연구·기여와 기존 impedance unit의 구분 | §I, PDF pp.1–2; Ref. [20] |
| 제어 힘→관절 토크, 임피던스 회전 | §II, 식 (1)–(7), PDF p.2 |
| 전체 신호 흐름·Exploration | Fig. 2–3, Algorithm 1, PDF p.3 |
| Bouncing 계산·FSM | §III-A2/B, 식 (8)–(9), Fig. 4, Algorithm 2, PDF pp.3–4 |
| 하드웨어·파라미터·기본/나사 실험 | §IV-A/B, Fig. 5–7, PDF pp.4–6 |
| 다른 미로 | §IV-C, Fig. 8–9, PDF pp.6–7 |
| 수동 threshold·비학습 방법·한계·향후 연구 | §V, PDF pp.7–8 |

이 논문의 근거는 **추정 외력과 실제 운동을 이용한 비학습 planning, 방향성 impedance, 실물 미로 통과**다. 외장 손목 F/T 장착, 6D Wrench 전체의 RL observation, 학습된 history representation, 일반적인 3D 탐색 성공의 근거로 사용하지 않는다.
