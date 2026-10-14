# Blind Sweeping의 Binary Tactile·Wrench 입력 설계 및 비교 실험 제안

기준일: 2026-09-16. **상태: PROPOSED. 구현 완료·최종 관측 사양·장비 실측 결과가 아니다.**

[조사 그룹](README.md) · [전체 논문](../papers/README.md) · [신규 문헌 조사](2026-09-16_binary-tactile-wrench-rl.md) · [문헌 색인](../README.md) · [프로젝트 결정과 미정 사항](../../03_DECISIONS_AND_OPEN_QUESTIONS.md)

**이 설계안에서 인용한 근거 문헌**

ID는 [원문 조사](2026-09-16_binary-tactile-wrench-rl.md)의 논문 구분을 따른다.

| 조사 ID | 논문 | 상세노트 |
| --- | --- | --- |
| [B1](2026-09-16_binary-tactile-wrench-rl.md#b1) | DexTouch | [상세노트](../papers/2024-lee-dextouch.md) |
| [B3](2026-09-16_binary-tactile-wrench-rl.md#b3) | Rotating without Seeing | [상세노트](../papers/2023-yin-rotating-without-seeing.md) |
| [W1](2026-09-16_binary-tactile-wrench-rl.md#w1) | CHEQ-ing the Box | 미작성 |
| [W2](2026-09-16_binary-tactile-wrench-rl.md#w2) | SRL-VIC | 미작성 |
| [W3](2026-09-16_binary-tactile-wrench-rl.md#w3) | High-quality Wiping | 미작성 |
| [W4](2026-09-16_binary-tactile-wrench-rl.md#w4) | AFORCE | 미작성 |

## 1. 이번 조사에서 검증할 설계 가설

**영역별 binary tactile은 ‘어디에 접촉했는가’를, 연속 wrist wrench는 ‘전체 부하가 얼마나·어느 방향으로 작용하는가’를 제공하도록 조합한다.** 이는 문헌에서 도출한 실험 가설이다. 17개 접촉 bit와 6축 wrench를 합치면 모든 접촉 상태를 알 수 있다는 주장이 아니다.

첫 구현 비교는 복잡한 접촉 분류기를 추가하기보다 같은 Cartesian 제어 경로에서 접촉 표현만 바꾸는 방식이 적절하다. 관측 이력이 필요한지는 순간 입력 정책의 실패와 비교해 판단한다. 특정 PPO 설정이나 RNN, stiffness action의 채택을 이 문서에서 확정하지 않는다.

## 2. Binary tactile의 구체적 후처리

### 2.1 실제 출력부터 확인한다

프로젝트의 ‘17개 촉각 영역’은 17개의 원시 scalar 센서와 같은 뜻이 아니다. 영역 안에 Grid가 있다면 원시 taxel 수, 단위, 부호, 부착 위치, 갱신률을 먼저 확인한다. 제품이 주는 gram-force가 영역 합력인지, 셀별 변환값인지도 구분해야 한다.

| 단계 | 입력 → 출력 | 확인할 점 |
| --- | --- | --- |
| 샘플 유효성 | packet·timestamp → validity·sample age | 통신 누락과 무접촉을 구분 |
| 영점 보정 | 원시값 → baseline 대비 변화 | 비접촉 기준에서 보정. 접촉 중 baseline을 계속 추적하면 지속 접촉이 지워질 수 있음 |
| 저역통과 | 보정값 → 잡음이 감소한 신호 | 실제 sampling period 사용. 차단주파수는 노이즈와 허용 지연을 측정한 뒤 결정 |
| 영역 축약 | taxel vector → 영역 대표값 | max·합·활성 셀 비율은 다른 물리적 의미 |
| 이진화 | 대표값 → 영역별 접촉 bit | 영역별 threshold와 hysteresis 후보 비교 |
| 시간 정렬 | 비동기 센서 → policy tick의 observation | 오래된 값을 새 측정으로 취급하지 않음 |

DexTouch의 확인된 처리 순서는 **FSR → low-pass filter → threshold → binary vector**다. 아래 hysteresis·validity mask·시간창 통계는 본 프로젝트에 대한 추가 제안이며 그 논문의 구현이라고 쓰지 않는다. [문헌 조사 B1](2026-09-16_binary-tactile-wrench-rl.md#b1)

### 2.2 필터와 영역 축약

영역 $i$의 taxel $j$에 대해 비접촉 기준값을 $b_{ij}$라 하면, 접촉 시 증가하는 방향으로 부호를 맞춘 보정 신호를 $u_{ij,t}$로 정의한다. 이미 힘 단위로 보정된 출력이 아니라면 이 값을 N이라고 표기하지 않는다.

단순 1차 low-pass 후보는 다음과 같다.

$$
z_{ij,t}=\alpha_t z_{ij,t-1}+(1-\alpha_t)u_{ij,t}, \qquad \alpha_t=\exp(-2\pi f_c\Delta t).
$$

$f_c$는 설계할 차단주파수이고 $\Delta t$는 실제 샘플 간격이다. 급격한 접촉을 지나치게 평활화하면 충격이나 짧은 접촉을 놓칠 수 있다. 필터 사용 여부 자체도 검증 대상이다.

| 영역 대표값 후보 | 장점 | 주의 |
| --- | --- | --- |
| $s_i=\max_j z_{ij}$ | 작은 국소 접촉에 민감 | 단일 taxel 이상치에 민감 |
| $s_i=\sum_j \max(z_{ij},0)$ | 넓게 분산된 약한 접촉을 모음 | 셀 수·baseline 오차·cross-talk 영향. 셀 출력이 보정된 힘이어야 합력으로 해석 가능 |
| 활성 셀 비율 | 접촉 면적 변화의 거친 표현 | 셀별 threshold가 먼저 필요하며 공간 배치를 잃음 |
| 여러 하위 영역의 bits | 접촉 위치 정보를 더 보존 | 관측 차원과 sim mapping 비용 증가 |

‘영역별 1 bit’와 ‘손 전체 1 bit’를 혼동하지 않는다. Sweeping 중 접촉이 손가락 끝에서 손바닥 쪽으로 이동하는 정보를 쓰려면 영역 구분을 유지해야 한다. 반대로 17개 bit 안에서는 각 영역 내부의 접촉 위치가 사라진다.

### 2.3 Threshold·hysteresis·debounce

노이즈가 있는 신호에 단일 threshold를 적용하면 경계에서 0/1이 반복될 수 있다. 다음 Schmitt-trigger 형태는 이를 줄이는 **제안**이다.

$$
c_{i,t}=\begin{cases} 1,&s_{i,t}\geq\theta_{i,\mathrm{on}},\\ 0,&s_{i,t}\leq\theta_{i,\mathrm{off}},\\ c_{i,t-1},&\theta_{i,\mathrm{off}}<s_{i,t}<\theta_{i,\mathrm{on}}, \end{cases} \qquad \theta_{i,\mathrm{off}}<\theta_{i,\mathrm{on}}.
$$

연속된 일정 시간 동안 조건을 만족해야 상태를 전환하는 debounce도 비교할 수 있다. 다만 hysteresis와 debounce를 동시에 강하게 적용하면 접촉 시작·해제의 지연이 커진다. 즉시 접촉 이벤트가 필요한 정책에는 오히려 불리할 수 있다.

임계값은 다음 절차로 선정한다.

1. 손 자세·시간 경과별 비접촉 신호 분포를 수집한다.
2. 예상하는 가장 약한 접촉과 넓은 면·모서리 접촉 분포를 수집한다.
3. 오검출률과 미검출률, 접촉 시작·해제 지연을 threshold별로 비교한다.
4. 영역별 차이가 크면 동일 threshold를 강제하지 않는다.
5. 시뮬레이션에도 검출확률·threshold 오차·지연을 대응시킨 뒤 정책을 비교한다.

논문의 **시뮬레이션 threshold**를 실물의 최소 감지 힘이나 제품 분해능으로 사용하지 않는다. DexTouch와 Yin 등의 0.01 N은 해당 논문 설정의 근거이며 Inspire Hand에 그대로 복사할 값이 아니다. 검출 가능한 신호가 없으면 이진화가 해당 채널에 없던 직접 관측을 만들어 주지는 않는다. 다른 센서·이력을 이용한 접촉 추정은 별도 문제다. [문헌 조사 B1](2026-09-16_binary-tactile-wrench-rl.md#b1), [B3](2026-09-16_binary-tactile-wrench-rl.md#b3)

가상 tactile은 실제 센서가 덮는 패치의 접촉만 반영해야 한다. 센서가 없는 부모 손가락 링크 전체의 접촉으로 대체하면 실물보다 넓은 coverage를 준다. 또한 실제 저항식 센서의 normal-force 반응과 simulation의 net-force norm은 shear 포함 여부·다중접촉 상쇄 때문에 같지 않을 수 있다. 측정축과 힘을 모으는 규칙을 맞춘 뒤 threshold를 비교한다. [문헌 조사 B3](2026-09-16_binary-tactile-wrench-rl.md#b3) 및 본 프로젝트 설계 해석

### 2.4 Sensor rate와 policy rate의 차이

빠른 센서에서 가장 최근 bit 하나만 선택하면 두 policy tick 사이의 짧은 접촉이 사라질 수 있다. 다음 세 입력을 비교하되, 시뮬레이션과 실물에 같은 시간 정렬 규칙을 적용한다.

| 표현 | 의미 | 잃는 정보 |
| --- | --- | --- |
| 마지막 bit | 현재 접촉 추정 | tick 사이 접촉 이벤트 |
| 시간창 내 any-contact | 최근 구간에 접촉이 한 번이라도 있었는가 | 이미 해제된 접촉과 현재 접촉의 구분 |
| 시간창 contact duty | 구간에서 접촉으로 관측된 시간 비율 | 사건의 순서·정확한 시각 |

불규칙 샘플에서는 단순 샘플 개수 비율과 시간 비율이 다르다. duty를 사용한다면 timestamp 기준으로 정의한다. sensor dropout을 0으로 채우면서 ‘무접촉’이라고 학습시키지 않는다. 최소한 mask 또는 sample age를 함께 제공하고, reset·중단·재개 시 필터·이력 상태 처리 규칙을 고정한다.

## 3. Wrench를 RL에 넣기 전의 처리

### 3.1 무엇을 측정하는 wrench인가

손목 센서의 값에는 환경 접촉뿐 아니라 손·어댑터 중량, 질량중심 오프셋, 가속도에 따른 관성, 영점 드리프트가 포함될 수 있다. 구매 예정 장비에서 모두 보정됐다고 가정하지 않는다. 우선 무접촉 상태에서 손 자세와 로봇 운동을 바꾸어 잔차를 확인한다.

Hand articulation으로 하중 분포가 바뀌면 하나의 고정 payload 보정만으로 충분하지 않을 수 있다. 준정적 실험과 빠른 Sweep에서 같은 잔차를 기대해서도 안 된다. 필요한 보정 수준은 실제 속도·가속도와 센서 로그로 판단한다.

### 3.2 좌표계와 모멘트 기준점을 함께 고정한다

$S$를 센서 프레임, $T$를 선택한 task 프레임으로 둔다. $R_{TS}$는 $S$에서 $T$로의 회전이고, $p_{TS}$는 **$T$ 원점에서 센서 원점까지의 벡터를 $T$에서 표현한 값**이다. 같은 작용 wrench를 $T$ 원점 기준으로 옮기면 다음과 같다.

$$
F^T=R_{TS}F^S,\qquad \tau^T=R_{TS}\tau^S+p_{TS}\times(R_{TS}F^S).
$$

방향만 회전해 센서 원점 기준 모멘트를 유지하려면 위 병진 항을 넣지 않고, 그 선택을 observation 문서에 적는다. 데이터시트의 작용/반작용 부호와 시뮬레이터 센서 부호도 맞춰야 한다. 좌표계가 다른 force와 torque를 그대로 이어 붙이면 접촉 방향 학습이 불필요하게 어려워진다.

기본 비교에서는 보정된 6D wrench를 유지한다. 이후 목표 Sweep 방향·선반 법선에 대한 투영을 특징으로 추가할 수 있으나, 평면 force만 쓰거나 torque를 제거한 효과를 별도로 검증해야 한다.

### 3.3 정규화와 포화

N과 N·m를 같은 스케일로 취급하지 않는다. 축별 또는 힘/토크 그룹별 scale $d_k$를 고정해 다음 입력을 후보로 사용한다.

$$
\widetilde w_{k,t}=\mathrm{clip}\left(\frac{w_{k,t}-b_k}{d_k},-c_k,c_k\right).
$$

$b_k,d_k,c_k$는 실제 데이터와 학습 분포에서 정할 값이다. 문헌 숫자를 장비 한계로 옮기지 않는다. running normalization을 쓰면 학습·실행 시 통계 갱신 규칙을 일치시킨다. **정책 입력 clipping과 독립적인 안전 감독의 원시 하중 판단을 분리한다.**

방향만 남기는 $F/\lVert F\rVert$는 거의 무접촉일 때 잡음을 확대하고 과부하 크기를 버린다. 방향 특징을 쓴다면 연속 크기와 신뢰도/접촉 상태를 함께 보존하는 대안을 비교한다.

### 3.4 시뮬레이션 대응

손목 wrench는 손목 아래 모든 외력의 합성 결과다. 시뮬레이션에서 대상 물체와의 접촉력만 따로 추출해 actor에 주면 실제 센서보다 더 좋은 정보가 된다. 비센서 부위 접촉도 wrist에는 나타날 수 있으며, 여러 접촉의 힘·모멘트는 서로 상쇄될 수 있다.

sim sensor가 external-contact force만 주는지, 중력·관성·constraint reaction까지 포함하는지 확인하고 실물 전처리와 맞춘다. 힘의 단위와 impulse/force 차이, physics step과 sensor period 차이도 확인한다. 센서 위치에서 떨어진 contact force를 합칠 때 모멘트 팔을 누락하지 않는다.

## 4. RL 통합: 관측·학습 정답·행동을 분리한다

### 4.1 최소 관측 후보

$$
o_t=[\xi_0,\ g,\ q_t,\dot q_t,\ x_{\mathrm{EEF},t},\dot x_{\mathrm{EEF},t},\ a_{t-1},\ \widetilde w_t,\ c_t,\ m_t,\ \delta t_t].
$$

$\xi_0$는 허용된 초기 정보, $g$는 목표 방향·거리, $c_t$는 영역별 contact vector, $m_t$는 유효성 mask, $\delta t_t$는 sample age다. 로봇 상태는 중복과 실물 측정 가능성을 확인해 줄일 수 있다. **이 식은 설계 후보이며 전체 observation dimension을 확정하지 않는다.**

현재 물체 pose·속도, 접촉한 물체 ID, 주변 물체 GT는 최종 Blind actor에 자동 추가하지 않는다. Teacher·critic·보상 계산·평가에서 사용하는 GT는 별도 인터페이스로 관리한다. 특히 critic-only GT가 encoder 입력이나 history 생성 경로를 통해 actor에 새어 들어가지 않도록 한다.

### 4.2 History와 latent를 쓰는 방법

| 단계 | 구조 | 판단할 질문 |
| --- | --- | --- |
| 기준선 | 현재 wrench+bits → MLP | 순간 접촉만으로 가능한가? |
| 이력 비교 | 최근 $H$개 observation/action → MLP 또는 temporal encoder | 저항 변화·접촉 이동·재접촉을 구분하는 데 이력이 유효한가? |
| 순환 비교 | proprioception+wrench+bits → GRU/LSTM → action | 고정 창보다 긴 접촉 이력이 필요한가? |
| 추가 연구 | 이력 → dynamics/contact latent → policy | 성능 향상이 압축·추정 모듈 때문인지 충분한 비교가 가능한가? |

정확한 $H$, latent dimension, RNN 구조는 제안 단계에서 수치로 고정하지 않는다. 센서 이력과 이전 action을 함께 보아야 동일 힘이 ‘로봇이 더 밀어서 커진 것’인지 다른 변화인지 해석할 단서가 생긴다. 그렇더라도 마찰·질량·다중접촉 원인이 항상 식별되는 것은 아니다.

### 4.3 Action과 controller

첫 센서 비교에서는 이미 검증할 Cartesian action→controller 경로를 고정한다. 정책이 속도나 Δpose를 출력하고 OSC/impedance 등의 저수준 제어기가 실행하는 구성이 가능하다. 구현 저장소를 읽기 전에는 현재 controller를 확정하지 않는다.

SRL-VIC의 Δposition+stiffness, polishing 연구의 motion+impedance는 **추가 action-space 선택지**다. Binary의 효용을 검증하는 동시에 stiffness 자유도까지 바꾸면 성능 차이의 원인을 구분하기 어렵다. 초기 센서 표현 비교 후 별도 ablation으로 검토한다. AFORCE처럼 measured force가 주로 저수준 controller에 들어가는 경우도 있으므로, ‘힘을 썼다’와 ‘actor가 힘을 관측했다’를 기록에서 구분한다. [문헌 조사 W1](2026-09-16_binary-tactile-wrench-rl.md#w1), [W2](2026-09-16_binary-tactile-wrench-rl.md#w2), [W3](2026-09-16_binary-tactile-wrench-rl.md#w3), [W4](2026-09-16_binary-tactile-wrench-rl.md#w4)

### 4.4 Reward와 종료

보상 후보는 대상 물체의 목표 방향 진행, 과도한 하중, 접촉 손실, 전도, 행동 급변 등을 구분한다. 힘을 작게 만드는 보상만 강하게 주면 접촉을 피하는 정책이 유리해질 수 있다. 반대로 접촉 유지 보상만으로 물체 이동이 보장되지 않는다.

시뮬레이션에서는 물체 GT로 진행·전도·성공을 계산할 수 있다. 이 평가 신호를 실물 Blind 종료 규칙과 동일시하지 않는다. EEF가 목표 거리를 이동했어도 미끄러짐·접촉 손실로 물체가 덜 이동할 수 있다. 접촉·wrench만으로 종료를 판단할 수 있는 조건과 실패 조건을 따로 실험한다.

## 5. 센서 표현 비교 실험

아래 모든 비교는 **동일 초기 정보, action/controller, reward, 훈련 예산, 물체 분포**를 기본으로 한다. 장비 준비와 계산 자원에 따라 최종 규모는 결정하되, 실행 전에 평가 구간을 정한다.

| 조건 | 접촉 입력 | 검증하는 질문 |
| --- | --- | --- |
| P0 | 없음; 허용된 초기 정보+proprioception | 접촉 센서 자체가 기여하는가? |
| B | 영역별 binary tactile | 접촉 분포만으로 충분한 구간이 있는가? |
| C | 같은 영역의 continuous tactile | 힘 크기를 버릴 때 어떤 정보가 사라지는가? |
| W | 보정 6D wrench | 전역 하중만으로 어디까지 가능한가? |
| W+B | wrench+binary tactile | 접촉 분포와 하중의 보완성이 있는가? |
| W+C | wrench+continuous tactile | W+B의 정보 손실이 실제로 문제인가? |

접촉센서를 actor에서 제외한 P0도 독립 안전 감독은 유지한다. B와 C는 같은 부착 위치·coverage·샘플링·지연 조건을 사용한다. B의 차원 축소와 이진화 효과를 구분하려면 C도 같은 영역 축약을 거치게 하고, 원시 Grid 입력은 별도 비교로 남긴다.

우선 순간 입력으로 비교한 뒤 필요하면 history를 추가한다. 최종 B/C 및 W+B/W+C 비교에는 동일 history 길이와 네트워크 용량 조건을 적용해 기억의 효과와 표현의 효과를 분리한다. 성능이 나쁜 입력을 평가 때 갑자기 0으로 만드는 실험과, 그 입력 없이 처음부터 학습한 실험을 같은 센서 ablation으로 취급하지 않는다.

### 5.1 분리해서 흔들어 볼 조건

- **접촉 위치:** 센서 중앙, 경계, 비센서 부위. 비센서 부위에 가상 tactile을 만들지 않는다.
- **신호 크기:** 가벼운 물체, 넓은 면의 약한 압력, 마찰 차이. 조건을 실제 측정값에 연결한다.
- **센서 변화:** threshold 오차, additive noise, baseline drift, 지연, 일부 dropout.
- **초기 오차:** 접근 완료 후 EEF–물체 상대 pose 오차. 원거리 접근을 별도 학습 문제로 추가하지 않는다.
- **동역학:** 물체 질량·마찰·접촉 강성 차이. 초기에는 센서 오차와 동시에 전부 흔들지 않아 실패 원인을 분리한다.

### 5.2 보고할 지표

| 수준 | 지표 |
| --- | --- |
| 감지 | false-positive/false-negative, 접촉 시작·해제 지연, 영역별 coverage, dropout 비율 |
| 조작 | 물체 실제 목표 변위 성공률, 이동 오차, 접촉 손실, 전도, 수행 시간 |
| 하중 | 보정 wrench의 peak와 시간 누적 노출, 힘·토크 각각의 초과 횟수 |
| 전이 | sim과 real의 같은 과업·조건에서 성공률과 실패 유형 변화 |
| 행동 반응 분석 | 접촉 신호 변화와 행동 수정의 대응 로그. 인과적 기여는 통제된 비교·센서 개입 실험으로 별도 확인 |

성공률의 분모·물체별 편차·반복 횟수를 함께 기록한다. 연구 간 서로 다른 회전수·성공률·return을 한 표에서 순위처럼 비교하지 않는다. Binary가 유리하다는 주장은 적어도 C/W+C와의 비교 및 실물 전이를 확인한 범위 안에서만 한다.

## 6. 지금 내릴 수 있는 판단

**Binary tactile은 충분히 실험할 가치가 있는 관측 표현이다. 그러나 임계값 하나로 접촉 위치·하중·미끄러짐·물체 이동을 모두 대체할 수 없다.** 먼저 실제 센서가 약한 접촉을 구분하는지 확인하고, 영역별 접촉 bits와 연속 wrench를 유지한 W+B를 W, B, W+C와 비교한다.

이 제안은 프로젝트의 제한 센싱 검증을 구체화한다. 새 회피 정책, 별도 object-pose estimator, 전체 hand 제어, 상위 탐색기를 필수 구성으로 추가하지 않는다.
