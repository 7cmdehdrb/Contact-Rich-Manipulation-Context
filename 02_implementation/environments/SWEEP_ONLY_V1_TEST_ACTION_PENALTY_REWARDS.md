# Sweep Only v1 Test ActionPenalty 보상과 페널티

2026-11-20 현재 코드 기준. 로그 이름 `inspire_sweep_only_v1_test_action_penalty`에 대응하는 Gym 환경은 **`Inspire-Sweep-Only-v1-Test-ActionPenalty`**다. 설정 클래스는 `SweepOnlyV1TestActionPenaltyEnvCfg`, runtime은 `SweepOnlyEnv`이며, `SweepOnlyV1TestEnvCfg`의 보상에 팔·손 행동 범위 초과 비용을 추가한다.

이 문서는 **step $t$에서 받는 보상 $r_t$**를 항별로 정의한다. 사용자 요청에 따라 **보상식에서 $\Delta t$를 의도적으로 제외**한다. 거리 증분·실패 사건 항의 구현 내부 시간 간격 나눗셈과 RewardManager의 시간 간격 곱셈도 식에 쓰지 않는다. 연속형 보상·비용에는 시간 간격을 추가하거나 숫자로 흡수하지 않고 설정 weight를 그대로 사용한다. 따라서 아래 총합은 요청한 시간 간격 생략 표기이며, 시뮬레이터가 반환하는 원시 step reward의 수치와 모든 항에서 그대로 일치하는 식이라는 뜻은 아니다. Episode 길이 $T=10$초는 Reach의 크기를 정하는 별도 파라미터이므로 유지한다.

[계열 안내](SWEEP_ONLY_FAMILY.md) · [공통 환경 설명](SWEEP_ONLY.md) · [문서 작성·검증 기록](../logs/2026-11-20_sweep_only_v1_test_action_penalty_rewards_documentation.md)

## 1. Step과 공통 기호

행동 $\mathbf{a}_t$를 실행한 뒤, 해당 제어 구간의 마지막 물리 상태로 보상 $r_t$를 계산한다. $t=0$은 reset 직후이며 첫 행동은 $t=1$이다. 한 제어 구간에는 물리 샘플이 2개 있다. 접촉력은 이 2개를 누적하지만, 관절 속도·물체 자세·거리 등의 항은 별도 설명이 없는 한 구간 마지막 값을 사용한다.

| 기호 | 정의 |
| --- | --- |
| $[x]_+$ | $\max(x,0)$ |
| $\mathrm{clip}(x,l,u)$ | $\min(\max(x,l),u)$; 벡터에는 성분별 적용 |
| $\mathbf{1}[E]$ | 조건 $E$가 참이면 1, 아니면 0 |
| $\mathbf{p}_t$ | 실제 현재 타겟의 기하 중심. 로컬 bounds 중앙을 현재 물체 pose로 변환한 값이며 질량중심 COM·초기 관측 대표점과 구분 |
| $\mathbf{g}_t$ | 현재 목표 위치 |
| $\mathbf{e}_t$ | 현재 EEF 위치 |
| $d_t$ | $\lVert\mathbf{g}_{t,xy}-\mathbf{p}_{t,xy}\rVert_2$; 타겟–목표 XY 거리, 단위 m |
| $\mathcal{A}$ | reset 시 실제 배치된 활성 물체 전체. 타겟 포함 |
| $\mathcal{O}$ | $\mathcal{A}$에서 타겟을 제외한 활성 장애물 |
| $\mathbf{a}_t^A,\mathbf{a}_t^H$ | 정책의 클리핑 전 팔 6D·손 6D 행동 |
| $\mathcal{J}_A,\mathcal{J}_H$ | 팔 6개 관절, 손의 mimic follower를 포함한 물리 관절 12개 |
| $k_t$ | 해당 step에 적용되는 학습 iteration |

모든 위치·힘은 별도 언급이 없으면 월드 좌표계 기준이다. $\mathcal{A}$와 $\mathcal{O}$는 **시각적으로 관측되는 장애물 슬롯과 다른 집합**이다. 가려져 장애물 인코더에 들어가지 않는 활성 물체도 기울기·이동·접촉 비용의 대상이다.

## 2. Step t의 총 보상

```math
\begin{aligned}
r_t={}&r_{\mathrm{sweep},t}+r_{\mathrm{retreat},t}+r_{\mathrm{reach},t}\\
&+r_{\mathrm{arm\ action\ rate},t}+r_{\mathrm{hand\ action\ rate},t}\\
&+r_{\mathrm{arm\ velocity},t}+r_{\mathrm{hand\ velocity},t}\\
&+r_{\mathrm{shelf\ collision},t}+r_{\mathrm{shelf\ failure},t}\\
&+r_{\mathrm{obstacle\ contact},t}+r_{\mathrm{wrench\ change},t}\\
&+r_{\mathrm{tilt},t}+r_{\mathrm{obstacle\ displacement},t}\\
&+r_{\mathrm{arm\ limit},t}+r_{\mathrm{hand\ limit},t}.
\end{aligned}
```

| 구현 term | Weight | 의미 |
| --- | --- | --- |
| `sweep_progress` | $+50$ | 접촉 이력·힘 정렬로 가중한 목표 방향 거리 감소 |
| `sweep_retreat` | $-10$ | 목표 거리 증가 |
| `reaching` | $+30$ | 현재 EEF–타겟 중심의 연속 근접 보상 |
| `arm_action_rate` | $-0.03$ | 원본 팔 행동의 연속 step 차이 제곱합 |
| `hand_action_rate` | $-0.03$ | 원본 손 행동의 연속 step 차이 제곱합 |
| `arm_joint_velocity` | $-0.03$ | 팔 관절 속도 제곱합, 합산 후 100으로 제한 |
| `hand_joint_velocity` | $-0.01$ | 손 물리 12관절 속도 제곱합, 합산 후 100으로 제한 |
| `shelf_collision` | $-0.5$ | 선반 이동·속도와 가상 손가락·손목의 근접 비용 |
| `shelf_failure` | $-3$ | 선반 속도 또는 손목 높이 실패 사건 |
| `obstacle_contact` | $w_O(k_t)$ | 장애물이 손에 가하는 합성 법선 접촉력의 초과 비용 |
| `wrench_change` | $w_W(k_t)$ | 보상된 손목 힘·모멘트의 크기 변화 비용 |
| `object_tilt` | $-30$ | 활성 타겟·장애물의 선반 법선 대비 기울기 |
| `obstacle_displacement` | $-150$ | 활성 장애물의 초기 위치 대비 3D 이동 제곱합 |
| `arm_action_limit` | $-0.03$ | 팔 원본 행동의 허용 범위 초과량 제곱평균 |
| `hand_action_limit` | $-0.03$ | 손 원본 행동의 허용 범위 초과량 제곱평균 |

총 15개 term이 구성된다. 초기 weight가 0인 `obstacle_contact`, `wrench_change`도 커리큘럼으로 활성화된다. 양의 보상은 Sweep과 Reach이며, 나머지는 0 또는 음의 기여다.

## 3. 목표 방향 Sweep 보상

### 3.1 제어 구간의 실제 타겟 접촉

물리 샘플 $j=1,2$마다 **타겟과 손 사이 접촉만** 사용한다. 각 법선 접촉력 $\mathbf{f}^{N}_{t,j,\ell}$와 접선 마찰력 $\mathbf{f}^{T}_{t,j,m}$으로 다음을 구한다.

```math
\mathbf{F}_{t,j}
=\sum_{\ell}\mathbf{f}^{N}_{t,j,\ell}
+\sum_m\mathbf{f}^{T}_{t,j,m},
\qquad
L_{t,j}=\sum_{\ell}\lVert\mathbf{f}^{N}_{t,j,\ell}\rVert_2,
\qquad
\overline{\mathbf{F}}_t=\frac{\mathbf{F}_{t,1}+\mathbf{F}_{t,2}}{2}.
```

$L_{t,j}$는 법선 하중의 합이며 **합력의 크기가 아니다**. 반대 방향의 접촉력이 상쇄돼도 하중은 남는다. 샘플 유효성 $V_{t,j}$에는 법선·마찰 데이터의 유한성, 버퍼 범위와 완전성 검사가 포함된다. 무효 샘플의 합력은 0으로 처리한다.

```math
P_t=\mathbf{1}[\exists j:\ V_{t,j}=1\ \land\ L_{t,j}\geq0.01\,\mathrm{N}],
\qquad
V_t=\mathbf{1}[V_{t,1}=1\ \land\ V_{t,2}=1],
\qquad
C_t=P_tV_t.
```

$P_t$는 구간 내 한 번이라도 정상 접촉이 있었는지, $V_t$는 구간의 모든 샘플이 유효한지를 나타낸다. 접촉 이력에는 $C_t$가 들어가며, reset 직전 이력은 모두 0이다. 촉각 관측의 17개 bit나 손목 wrench로 이 접촉을 대신하지 않는다.

### 3.2 접촉 인식과 유지 카운트

$z_S^0$를 reset 기준 선반 root 높이라 하고, 접촉 판정용 상판 높이를 $H_S=z_S^0+1.05$로 둔다. 접촉 인식 $G_t$와 카운트 $n_t$는 다음과 같다.

```math
G_t=\mathbf{1}[C_t+C_{t-1}+C_{t-2}\geq2]
\mathbf{1}[e_{t,z}<H_S+0.12]
\mathbf{1}[e_{t,z},H_S\text{가 유한함}],
```

```math
n_0=0,\qquad
n_t=\mathrm{clip}\left(
n_{t-1}+\begin{cases}1,&G_t=1,\\-2,&G_t=0,\end{cases}
0,20\right),
\qquad
h_t=G_t\frac{n_t}{20}.
```

높이 경계는 **엄격한 미만**이다. 최근 3개 중 2개 접촉이 있어도 EEF 높이 조건이 깨지면 카운트가 감소하고 $h_t=0$이다. 반대로 과거 접촉 때문에 $G_t=1$이어도 아래 현재 접촉 조건이 깨지면 Sweep 보상은 0이다. reset부터 Sweep phase가 활성화되므로 안정화 Gate 대기는 없다.

### 3.3 힘 방향 정렬 계수

$\epsilon=10^{-12}$로 두고, 현재 타겟에서 목표를 향하는 XY 단위 방향을 정의한다.

```math
\widehat{\mathbf{u}}_t
=\frac{\mathbf{g}_{t,xy}-\mathbf{p}_{t,xy}}{\max(d_t,\epsilon)}.
```

정렬 계수 $\alpha_t$는 다음과 같다.

```math
\alpha_t=
\begin{cases}
\displaystyle\mathrm{clip}\left(
\frac{\overline{\mathbf{F}}_{t,xy}\cdot\widehat{\mathbf{u}}_t}
{\max(\lVert\overline{\mathbf{F}}_t\rVert_2,\epsilon)},0,1\right),
&C_t=1,\ \lVert\overline{\mathbf{F}}_{t,xy}\rVert_2\geq1\,\mathrm{N},\ d_t>\epsilon,\\
0,&\text{그 외}.
\end{cases}
```

분자는 수평 힘의 목표 방향 성분, 분모는 **수직 성분을 포함한 3D 평균 합력의 크기**다. 따라서 수직 힘이 커져도 수평 목표 방향 성분이 그대로라면 정렬 계수는 작아진다. 목표 반대 방향 힘은 0으로 제한한다.

### 3.4 Step t에 지급되는 식

```math
r_{\mathrm{sweep},t}=50[d_{t-1}-d_t]_+h_t\alpha_t.
```

직전 step보다 목표에 가까워진 거리만 사용한다. Episode 최고 접근 기록을 갱신하는 방식은 아니므로 후퇴 후 재접근해도 조건을 만족하면 다시 보상한다. 목표 반경 3cm 안에서 자동으로 끄는 조건은 없다. $d_0$는 reset 시 실제 타겟 중심과 목표 사이 거리다.

예를 들어 $n_t=20$, $G_t=1$, $\alpha_t=1$이고 목표 거리가 1cm 줄면 이 항은 $+0.5$다. 같은 이동에서 $n_t=10$이면 $+0.25$다. 접촉 카운트는 단독 양의 보상이 아니라 거리 감소량의 배율이다.

## 4. 목표 반대 방향 이동 페널티

```math
r_{\mathrm{retreat},t}=-10[d_t-d_{t-1}]_+.
```

목표에서 멀어진 XY 거리만 사용한다. 접촉 여부·접촉 카운트·EEF 높이·힘 크기·힘 방향 조건은 요구하지 않는다. 손이 떨어진 뒤 물체가 미끄러져 멀어져도 발생한다. 1cm 후퇴의 기여는 $-0.1$이다.

## 5. EEF–타겟 근접 보상

Test 환경에는 `InverseDistanceReach`가 활성화돼 있다. 현재 3D EEF–타겟 기하 중심 거리를 $\rho_t$라 하고, 10cm 바깥 간격을 $b_t$로 정의한다.

```math
\rho_t=\lVert\mathbf{e}_t-\mathbf{p}_t\rVert_2,
\qquad
b_t=[\rho_t-0.10]_+,
\qquad
\phi_t=\frac{0.10}{0.10+b_t}.
```

크기 조절에 쓰는 초기 간격 $b_0^{\mathrm{root}}$는 reset 시 **물체 link/root 원점**까지의 거리에서 계산한다. 현재 근접도에 쓰는 기하 중심과 기준점이 다르다. $\mathbf{x}_0^{\mathrm{root}}$가 reset 시 타겟 원점이면 다음과 같다.

```math
b_0^{\mathrm{root}}
=[\lVert\mathbf{e}_0-\mathbf{x}_0^{\mathrm{root}}\rVert_2-0.10]_+,
\qquad
r_{\mathrm{reach},t}
=30\frac{b_0^{\mathrm{root}}}{10}\phi_t.
```

분모 10은 최대 episode 길이 $T=10$초다. $\rho_t\leq0.10\mathrm{m}$이면 $\phi_t=1$이며, 20cm이면 $1/2$, 30cm이면 $1/3$이다. 초기 간격이 0이면 episode 전체에서 이 항은 0이다.

접촉이나 목표 도달 여부를 요구하지 않으며, 근접 상태를 유지하면 매 step 지급한다. 접근량·최고 접근 기록·남은 보상 budget을 차감하는 항이 아니다. 초기 거리와 episode 길이는 지급 크기를 정하는 고정 배율로 사용한다.

## 6. 원본 행동 변화 페널티

클리핑 전 원본 행동의 연속 step 차이를 팔과 손 각각 **제곱합**한다.

```math
r_{\mathrm{arm\ action\ rate},t}
=-0.03\sum_{i=1}^{6}(a^A_{t,i}-a^A_{t-1,i})^2,
\qquad
r_{\mathrm{hand\ action\ rate},t}
=-0.03\sum_{i=1}^{6}(a^H_{t,i}-a^H_{t-1,i})^2.
```

시간 미분이나 채널 평균으로 바꾸지 않는다. 두 항 모두 cap이 없다. reset 시 이전 행동은 0이므로 첫 행동도 0과의 차이로 비용을 받는다. 실행 제한에 걸려 실제 명령이 같아도 원본 출력이 달라지면 비용이 발생한다.

## 7. 관절 속도 페널티

```math
r_{\mathrm{arm\ velocity},t}
=-0.03\min\left(\sum_{j\in\mathcal{J}_A}\dot q_{t,j}^{\,2},100\right),
\qquad
r_{\mathrm{hand\ velocity},t}
=-0.01\min\left(\sum_{j\in\mathcal{J}_H}\dot q_{t,j}^{\,2},100\right).
```

관절 속도의 단위는 rad/s다. 팔은 6관절, 손은 주 구동 6개와 follower를 합친 **물리 관절 12개**다. 각각 합산 후 cap을 적용하므로 항의 범위는 팔 $[-3,0]$, 손 $[-1,0]$이다. 허용 속도 구간 없이 0이 아닌 속도부터 비용이 생긴다. 팔 속도에 의한 조기 종료 기준은 별도다.

## 8. 선반 충돌·근접 페널티

선반 root 위치 $\mathbf{s}_t$, 초기 root 위치 $\mathbf{s}_0$, 선반 root의 선속도·각속도를 합친 6D 벡터 $\mathbf{v}_t^S$를 사용한다.

```math
M_t=\mathbf{1}[\lVert\mathbf{s}_t-\mathbf{s}_0\rVert_2
+\lVert\mathbf{v}_t^S\rVert_2>0.005].
```

위 조건은 코드의 위치 norm과 6D 속도 norm을 더하는 판정 그대로다. 각속도를 제외하거나 거리만 검사하는 식으로 바꾸지 않는다.

이 term의 근접 기준점은 $\mathbf{b}_t=\mathbf{s}_t+(0,0,1.06)$이다. 가상 손가락 프레임 앞의 2개와 손목 프레임의 기준 높이를 다음과 같이 둔다.

```math
N_t=\mathbf{1}[\lVert\mathbf{b}_t-\mathbf{e}_t\rVert_2<0.20],
\qquad
\eta_{t,i}=z^{\mathrm{finger}}_{t,i}-b_{t,z},
\qquad
\eta_t^W=z_t^{\mathrm{wrist}}-b_{t,z}.
```

```math
r_{\mathrm{shelf\ collision},t}
=-0.5\left[
M_t+N_t\left(
\sum_{i=1}^{2}\mathrm{clip}\left(1-\frac{\eta_{t,i}}{0.02},0,1\right)
+\mathrm{clip}\left(1-\frac{\eta_t^W}{0.08},0,1\right)
\right)\right].
```

손가락 2cm·손목 8cm 미만부터 각각 비용이 증가하고, 기준 높이 이하에서 각 비용이 1로 포화한다. 근접 부분은 $N_t=1$일 때만 적용하며 선반 이동 부분 $M_t$는 독립적이다. 이 식의 기준 높이 **1.06m**는 Sweep 접촉·실패 판정의 **1.05m**와 다르다. 실제 접촉력만을 측정한 충돌 비용이 아니라 코드상 가상 프레임 근접 비용을 포함한다. 항의 범위는 $[-2,0]$이다.

## 9. 선반 실패 페널티

```math
D_t=\mathbf{1}\left[
\lVert\mathbf{v}_t^S\rVert_2>0.10
\ \lor\
z_t^{\mathrm{wrist}}-(s_{t,z}+1.05)<0.03
\right],
\qquad
r_{\mathrm{shelf\ failure},t}=-3D_t.
```

선반의 6D root 속도 norm이 0.1을 초과하거나 손목 높이가 상판 기준 3cm 미만일 때 $-3$을 준다. `check_fingers=False`여서 가상 손가락 높이는 이 실패 페널티의 조건이 아니다.

선반 **종료 조건**에는 초기 위치 대비 5cm 초과 이동도 포함되지만, 이 $-3$ 항에는 그 이동 조건이 없다. 따라서 선반 이동만으로 종료되면 반드시 $-3$을 받는 것은 아니다. `shelf_collision`과 이 항은 같은 step에 함께 발생할 수 있다.

## 10. 장애물 접촉력 페널티

활성 장애물과 손 사이 **법선 접촉력 벡터를 먼저 합산**하고 그 크기를 구한다. $\mathbf{f}^{O\to H}_{t,i,\ell}$는 장애물 $i$가 손에 가하는 법선 힘이다.

```math
F_t^O=\left\lVert\sum_{i\in\mathcal{O}}\sum_{\ell}
\mathbf{f}^{O\to H}_{t,i,\ell}\right\rVert_2,
\qquad
x_t=[F_t^O-F_{\mathrm{free}}(k_t)]_+,
```

```math
c_{O,t}=\min\left(\frac{e^{2x_t}-1}{2},100\right),
\qquad
r_{\mathrm{obstacle\ contact},t}=w_O(k_t)c_{O,t}.
```

구현은 overflow를 피하기 위해 지수의 입력도 사전에 제한하지만 유한값에 대해서는 위 식과 동등하다. 센서가 fresh가 아닌 step은 0, 힘의 크기가 NaN·무한대이면 raw cost는 100으로 처리한다.

타겟·선반·바닥의 접촉과 접선 마찰력은 이 항에 넣지 않는다. 물체별 힘 크기를 합한 값이 아니므로 반대 방향 힘은 상쇄될 수 있다. 구간 평균 힘을 쓰는 Sweep과 달리 이 항은 센서의 현재 force matrix를 사용한다. $F_{\mathrm{free}}$와 $w_O$의 일정은 14절에 정리한다.

## 11. 손목 wrench 크기 변화 페널티

$\mathbf{f}_t^W$, $\boldsymbol{\tau}_t^W$는 EEF 원점·EEF 축에서 읽은 **손의 중력·관성 보상 후 힘과 모멘트**다. 관측 함수의 원본 출력을 직접 읽으므로 관측 noise와 축별 clip을 적용하기 전 값이다.

```math
\delta F_t=\left|\lVert\mathbf{f}_t^W\rVert_2-\lVert\mathbf{f}_{t-1}^W\rVert_2\right|,
\qquad
\delta\tau_t=\left|\lVert\boldsymbol{\tau}_t^W\rVert_2-\lVert\boldsymbol{\tau}_{t-1}^W\rVert_2\right|.
```

벡터 차이의 norm이나 시간 미분이 아니라 **각 norm의 차이 절댓값**이다. 따라서 힘 방향만 바뀌고 크기가 같으면 그 변화만으로 비용이 발생하지 않는다. 허용 크기 변화 $F_W(k_t)$와 $\tau_W(k_t)$를 이용한다.

```math
u_{F,t}=\frac{[\delta F_t-F_W(k_t)]_+}{1.5F_W(k_t)},
\qquad
u_{\tau,t}=\frac{[\delta\tau_t-\tau_W(k_t)]_+}{1.5\tau_W(k_t)},
\qquad
u_t=\mathrm{clip}(\max(u_{F,t},u_{\tau,t}),0,1),
```

```math
c_{W,t}=\frac{e^{3u_t}-1}{e^3-1},
\qquad
r_{\mathrm{wrench\ change},t}=w_W(k_t)c_{W,t}.
```

힘과 모멘트 중 더 큰 정규화 초과 정도를 사용한다. 각 변화량이 허용값 이하면 비용 0, 허용값의 **2.5배 이상**이면 해당 severity가 1로 포화하며 raw cost의 범위는 $[0,1]$이다.

이 환경은 `max_positive_fraction=None`이므로 **양의 누적 보상에 따른 5% budget 제한이 없다**. reset 직후·새로 활성화 직후에는 이전 유효 wrench가 없으므로 첫 비용은 0이다. current sample이 fresh이고 이전 sample이 유효할 때 계산하며, 현재 비유한값으로 severity가 NaN·양의 무한대가 되면 1로 처리하고 다음 step의 이전 유효 상태를 무효화한다.

## 12. 활성 물체 기울기와 장애물 이동 페널티

### 12.1 기울기

$\widehat{\mathbf{z}}_{t,i}$는 물체 $i$의 로컬 +Z 축을 월드로 변환한 방향, $\widehat{\mathbf{z}}_t^S$는 **현재 선반 법선**이다.

```math
\theta_{t,i}=\arccos\left(\mathrm{clip}
(\widehat{\mathbf{z}}_{t,i}\cdot\widehat{\mathbf{z}}_t^S,-1,1)\right),
\qquad
\theta_{\mathrm{free}}=\frac{5\pi}{180},
```

```math
r_{\mathrm{tilt},t}
=-30\sum_{i\in\mathcal{A}}
\left[\mathrm{clip}\left(
\frac{\theta_{t,i}-\theta_{\mathrm{free}}}{0.9-\theta_{\mathrm{free}}},0,1
\right)\right]^2.
```

5° 이하는 0, 이후 제곱으로 증가하며 0.9rad 이상에서 물체 하나당 $-30$으로 포화한다. **타겟도 포함**한다. 합계에는 별도 cap이 없으며 활성 물체가 $N$개면 범위는 $[-30N,0]$이다. 초기 자세와의 회전량이나 yaw 회전 자체를 벌하는 항은 아니다.

### 12.2 장애물 이동

$\mathbf{x}_{t,i}$는 object collection이 제공하는 물체 원점의 현재 3D 위치, $\mathbf{x}_{0,i}$는 reset에서 저장한 같은 원점의 초기 위치다.

```math
r_{\mathrm{obstacle\ displacement},t}
=-150\min\left(
\sum_{i\in\mathcal{O}}\lVert\mathbf{x}_{t,i}-\mathbf{x}_{0,i}\rVert_2^2,
0.04\right).
```

XY뿐 아니라 Z 이동도 포함하며 타겟은 제외한다. 장애물별 cap이 아니라 **전체 제곱합에 0.04m² cap**을 적용하므로 범위는 $[-6,0]$이다. 0.04m는 거리 임계값이 아니다. 장애물 하나만 움직이면 20cm 변위에서 포화한다. 합산 결과가 NaN·무한대면 cap으로 처리한다.

매 step의 이동 증분이 아닌 **초기 위치에서 벗어난 상태 자체**에 대한 비용이다. 장애물이 움직인 뒤 멈춰도 계속 비용이 발생하고, 초기 위치로 돌아오면 줄어든다. 회전만으로 원점 위치가 변하지 않으면 이 항에는 비용이 없다.

## 13. 행동 허용 범위 초과 페널티

실행할 팔 명령은 6채널 모두 $[-\pi/2,\pi/2]$로 제한하고, 손 명령은 채널별 $[0,U_i]$로 제한한다. 비용은 제한 전 원본 행동과 제한 결과의 차이를 사용한다.

```math
\widetilde a^A_{t,i}=\mathrm{clip}(a^A_{t,i},-\pi/2,\pi/2),
\qquad
r_{\mathrm{arm\ limit},t}
=-\frac{0.03}{6}\sum_{i=1}^{6}
\left(\frac{a^A_{t,i}-\widetilde a^A_{t,i}}{\pi}\right)^2,
```

```math
\widetilde a^H_{t,i}=\mathrm{clip}(a^H_{t,i},0,U_i),
\qquad
r_{\mathrm{hand\ limit},t}
=-\frac{0.03}{6}\sum_{i=1}^{6}
\left(\frac{a^H_{t,i}-\widetilde a^H_{t,i}}{U_i}\right)^2.
```

손 채널 순서와 실제 상한은 다음과 같다. 단위는 rad다.

| $i$ | 손 채널 | $U_i$ |
| --- | --- | --- |
| 1 | 엄지 굽힘 `thumb_2` | 0.5864 |
| 2 | 검지 `index_1` | 1.4381 |
| 3 | 중지 `middle_1` | 1.4381 |
| 4 | 약지 `ring_1` | 1.4381 |
| 5 | 소지 `little_1` | 1.4381 |
| 6 | 엄지 대립 `thumb_1` | 1.1641 |

팔은 전체 허용 폭 $\pi$, 손은 전체 허용 폭 $U_i$로 정규화하고 **6채널 평균**을 낸다. 6절의 행동 변화 항이 제곱합인 것과 구분한다. 허용 구간 내부와 경계에서는 0이며 cap은 없다. 전 채널이 각자의 전체 허용 폭만큼 초과하면 해당 그룹의 기여는 $-0.03$, 그 두 배만큼 초과하면 $-0.12$다.

팔 비용은 OSC의 위치 scale 0.03·회전 scale 0.15를 적용하기 전 행동에서 계산한다. 팔 관절 각도 자체의 초과 비용이 아니다. 손은 follower 12개가 아니라 **정책이 출력하는 주 구동 6개**만 대상으로 한다. Last Action 관측은 별도로 $[-\pi/2,\pi/2]$에 제한되므로 이 비용 입력과 같지 않을 수 있다.

## 14. 학습 iteration에 따른 계수와 허용값

다음 5개 일정이 활성화돼 있다. 표의 값은 각 지정 iteration에서의 값이다.

| Iteration | $w_O$ | $F_{\mathrm{free}}$ [N] | $w_W$ | $F_W$ [N] | $\tau_W$ [N·m] |
| --- | --- | --- | --- | --- | --- |
| 0 | 0 | 80 | 0 | 50 | 5 |
| 1000 | 0 | 80 | 0 | 50 | 5 |
| 3000 | −0.02 | 80 | −0.03 | 50 | 5 |
| 6000 | −0.05 | 50 | −0.10 | 30 | 3 |
| 10000 | −0.05 | 50 | −0.10 | 30 | 3 |
| 12000 이후 | −0.10 | 30 | −0.10 | 20 | 2 |

표의 모든 행이 각각의 schedule에 저장된 knot라는 뜻은 아니다. 동일한 값을 유지하는 구간의 표시를 통일했다. 원본 knot는 다음과 같다.

- $w_O$: `(0,0), (1000,0), (3000,-0.02), (6000,-0.05), (10000,-0.05), (12000,-0.10)`.
- $F_{\mathrm{free}}$: `(0,80), (3000,80), (6000,50), (10000,50), (12000,30)`.
- $w_W$: `(0,0), (1000,0), (3000,-0.03), (6000,-0.10)`.
- $F_W$: `(0,50), (3000,50), (6000,30), (10000,30), (12000,20)`.
- $\tau_W$: `(0,5), (3000,5), (6000,3), (10000,3), (12000,2)`.

각 schedule에서 인접 knot $(k_a,v_a)$, $(k_b,v_b)$ 사이 값은 **250 iteration 단위로 양자화한 선형 보간**이다.

```math
v(k)=v_a+(v_b-v_a)
\frac{250\left\lfloor(k-k_a)/250\right\rfloor}{k_b-k_a},
\qquad k_a\leq k<k_b.
```

마지막 knot 이후에는 최종값을 유지한다. 예를 들어 iteration 2000에서 $w_O=-0.01$, $w_W=-0.015$다. iteration 2250에서는 각각 $-0.0125$, $-0.01875$다. Weight가 0일 때 RewardManager는 해당 함수를 호출하지 않으며, wrench term을 0에서 활성화할 때 이력을 초기화해 오래된 값의 차이를 벌하지 않는다.

Sweep $+50/-10$, Reach $+30$, 행동·관절·기울기·이동·선반 비용의 weight는 이 일정으로 바뀌지 않는다. 목표 방향 Deadzone 30°도 고정 배치 조건이며 보상식의 각도 허용 오차나 커리큘럼이 아니다.

## 15. 포함하지 않는 보상과 종료의 관계

다음 항은 비활성화돼 있다.

- 안정화 점수 `stage`, 초기 타겟 이동·회전 비용, 압착 `squeeze`.
- 별도 목표 거리 함수 `goal_distance`, 목표 체류 `goal_hold`, 접촉 유지 `hand_contact`.
- 별도 역거리 항 `target_inverse_distance`, 물체 가속도·밀기 속도·EEF 속도·EEF 방향 비용, 통합 `object` 비용.
- 별도의 행동 크기 $\lVert\mathbf{a}_t\rVert^2$ 비용과 목표 최초 진입·성공·timeout bonus.

목표 반경 안에 있어도 즉시 성공 종료하지 않는다. 최대 10초의 timeout에서 $d_t<0.03\mathrm{m}$이고 같은 step에 물리 실패가 없으면 성공으로 집계한다. **정확히 3cm는 성공이 아니다.** 성공 집계 자체가 추가 보상을 지급하지는 않는다.

팔 관절 중 하나라도 절대 속도 1rad/s 초과, 활성 물체의 낙하·0.9rad 이상 기울기, 선반 실패 조건은 조기 종료를 일으킨다. 이 중 팔 과속·물체 낙하에 대응하는 별도 정액 실패 페널티는 없다. 각 step의 위 15개 항과 종료 판정을 구분해 해석한다.

## 16. 코드 대조 위치

아래 링크는 이 문서의 식과 설정을 확인하는 기준이다.

| 확인 대상 | 실제 코드 |
| --- | --- |
| 환경 등록 | [패키지 등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py) |
| 정확한 버전·상속·ActionPenalty 연결 | [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/stabilize_sweep_envs.py) |
| 로그 이름·wrapper clip 해제 | [PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/stabilize_sweep_ppo_cfg.py) |
| 전체 보상 term·기본 weight | [RewardCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/stabilize_sweep.py) |
| Test Reach 상속 | [Finger RewardCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/sweep_simple.py) |
| Sweep 접촉 이력·카운트·방향·거리 | [Sweep 상태](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_state.py) |
| 타겟 접촉의 법선·마찰 샘플 집계 | [접촉 샘플](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_contact.py) |
| 물리 샘플 순서·구간 종료 계산 | [runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/stabilize_sweep.py) |
| 범위 초과 비용 | [Sweep 보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/stabilize_sweep.py) |
| Reach·선반 실패 사건 | [IK Test 보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/wrench_refactor_relative_ik_test.py) |
| Reach 초기 거리·관절 속도·지수 cap | [공통 거리·속도 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_rewards.py) |
| 원본 12D 행동 변화 비용 | [Finger 행동 비용](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/sweep_simple.py) |
| 선반 이동·가상 프레임 근접 비용 | [선반 충돌 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/sweep.py) |
| 접촉력·wrench·기울기·이동 비용 | [Fusion 비용 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/contact_sweep_clutter_fusion.py) |
| 장애물 합성 법선 접촉력 | [물체별 접촉 집계](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/contact_sweep_clutter_fusion_contacts.py) |
| 선반 법선 대비 기울기 | [기울기 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/contact_sweep_clutter.py) |
| 보상용 wrench의 noise·clip 이전 입력 | [PureWristWrench](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/contact_sweep_clutter.py) |
| 손 채널 순서·상한 | [손 기구학](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/hand_kinematics.py) |
| 학습 일정과 250-iteration 보간 | [CurriculumCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/stabilize_sweep.py), [schedule 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curriculum_functions/contact_sweep_clutter_fusion_holding.py) |
| 종료 term과 timeout 성공 | [TerminationCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations/stabilize_sweep.py), [성공 판정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/stabilize_sweep.py) |
