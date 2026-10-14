# Omni 보상 설계 제안 초안

[활성 환경 현황](../../02_implementation/08_ACTIVE_ENVIRONMENTS.md) · [현재 Omni 구성](../../02_implementation/environments/OMNI_ENVIRONMENT.md) · [문서 안내](../README.md)

2026-10-14 문서 위치 정리: 기존 `src/inspire_sweep_baseline/REWARD_PLAN.md`의 제안 내용과 수치를 보존하고 수식 표기를 문서 형식 규칙에 맞췄다. 아래 내용은 제안 초안이며, 현재 구현과 비교할 때는 [Omni 구성](../../02_implementation/environments/OMNI_ENVIRONMENT.md)과 코드를 우선 확인한다.

이번에는 **Initial Joint에서 출발해 접근까지 수행한다는 조건**을 반영해야 합니다. 기존 보상에서 가장 크게 바꿀 부분은 다음 세 가지입니다.

- `reaching`은 **가까이 머물면서 계속 받는 보상 → 접근한 만큼만 받는 보상**으로 변경.
- `sweeping_object`는 **목표 위치 기반으로 통일하고, 기존 물체 Y축 속도 보상은 제거**.
- `homing_after_sweep`는 **성공 시 한 번 지급하는 큰 보상**으로 교체. (Homing을 수행하지 않음)

아래는 구현을 위한 제안 초안입니다. 수치들은 확정값이 아닙니다.

---

**전체 구성은 다음과 같이 잡겠습니다.**

```math
\begin{aligned}
r_t={}&
w_{\mathrm{reach}}r_{\mathrm{reach},t}
+R_{\mathrm{success}}S_t
-R_{\mathrm{failure}}F_t\\
&+\frac{\Delta t}{T_{\mathrm{ref}}}
\Big[
w_g r_{\mathrm{goal},t}
-w_{\Delta a}c_{\Delta a,t}
-w_{\Delta h}c_{\Delta h,t}\\
&\qquad
-w_{va}c_{va,t}
-w_{vh}c_{vh,t}
-w_{\mathrm{tilt}}c_{\mathrm{tilt},t}
-w_{\mathrm{shelf}}c_{\mathrm{shelf},t}
-w_{\mathrm{time}}
\Big].
\end{aligned}
```

여기서 $T_{\mathrm{ref}}=1\mathrm{s}$입니다. 접근 진척과 성공·실패는 이벤트 또는 변화량이고, 나머지는 시간에 따라 누적되는 항으로 구분합니다.

| 항목 | 역할 |
|---|---|
| $r_{\mathrm{goal}}$ | 물체를 목표 위치로 이동 |
| $r_{\mathrm{reach}}$ | Initial Joint에서 물체 근처까지 접근 유도 |
| $S_t$ | 성공 시 큰 보상, 한 번 지급 |
| $c_{\Delta a},c_{\Delta h}$ | Arm·Hand 명령 급변을 독립적으로 억제 |
| $c_{va},c_{vh}$ | Arm·Hand 관절 속도를 독립적으로 억제 |
| $c_{\mathrm{tilt}}$ | 허용 범위를 넘는 물체 기울기 억제 |
| $c_{\mathrm{shelf}}$ | 선반의 교란 또는 과도한 접촉 억제 |
| 시간 비용 | 아무것도 하지 않고 대기하는 행동에 비용 부여 |
| $F_t$ | 전도 등 실패 시 페널티와 종료 |

**1. 목표 위치 보상은 방향에 무관한 거리 함수로 통일합니다.**

```math
d_t=
\left\|
\mathbf{p}^{xy}_{\mathrm{object},t}
-\mathbf{p}^{xy}_{\mathrm{goal}}
\right\|_2
```

```math
r_{\mathrm{goal},t}
=
\exp\left(-\frac{d_t}{\sigma_g}\right)-1,
\qquad
\sigma_g=0.10\,\mathrm{m}
```

목표에 가까워질수록 값이 커지고, 목표에 도달하면 0입니다. 도달하지 않은 상태에서는 비용이 계속 발생합니다.

기존의 양의 지수 보상을 그대로 쓰면 물체를 목표 근처에 두고 머무는 행동에서도 보상이 누적됩니다. 이번에는 그 유인을 줄이기 위해 음의 거리 비용으로 구성하고, **실제 성공의 가치는 별도 성공 보상으로 크게 부여**합니다.

**기존 Y축 속도 보상은 제거합니다.** Omni-Directional 조건에서 특정 축의 속도를 보상하면 방향 편향이 생깁니다. 목표 방향으로 투영한 속도 항도 첫 버전에는 넣지 않겠습니다. 우선 위치 목표만으로 밀기와 감속을 학습시키는 편이 원인 분석에 유리합니다.

**2. Reaching은 “새롭게 가까워진 거리”에만 보상합니다.**

기존의 $3\exp(-10d)$를 매 Step 지급하면, 물체 근처에서 멈추는 것만으로 계속 보상을 받을 수 있습니다.

이를 막기 위해 **에피소드 내 최단 접근 거리 기록**을 사용합니다.

먼저 접근 거리는 다음과 같이 정의합니다.

```math
d^{\mathrm{reach}}_t=
\max\left(
\left\|\mathbf{p}_{\mathrm{ref},t}
-\mathbf{p}_{\mathrm{object},0}\right\|_2
-\rho_{\mathrm{near}},
0
\right)
```

- $\mathbf{p}_{\mathrm{ref}}$: 손목 또는 손바닥에 고정된 기준점.
- $\mathbf{p}_{\mathrm{object},0}$: 초기 물체 위치.
- $\rho_{\mathrm{near}}$: 손의 크기를 고려한 근접 영역 반경.

**기준점은 손가락 굽힘으로 위치가 달라지는 Fingertip에 두지 않습니다.** 그래야 Arm을 접근시키는 대신 손가락만 굽혀 Reaching 보상을 얻는 문제를 줄일 수 있습니다.

그다음 최단 거리 기록을 갱신합니다.

```math
b_0=d^{\mathrm{reach}}_0,
\qquad
b_t=\min(b_{t-1},d^{\mathrm{reach}}_t)
```

```math
r_{\mathrm{reach},t}
=
\frac{b_{t-1}-b_t}
{\max(d^{\mathrm{reach}}_0,\epsilon)}
```

이 구성에서는 다음이 성립합니다.

| 행동 | 접근 보상 |
|---|---:|
| 이전보다 더 가까이 접근 | 양수 |
| 물체 근처에서 정지 | 0 |
| 멀어졌다가 같은 위치로 복귀 | 0 |
| 근접 영역 도달 이후 | 0 |

에피소드 전체에서 받을 수 있는 접근 보상의 비할인 합은 최대 $w_{\mathrm{reach}}$입니다. **접근 보상을 반복해서 얻는 행동에 상한을 두는 방식**입니다.

이는 임시 학습 보조 항입니다. 성공이 안정적으로 나오면 가중치를 줄여도 되는 항이며, 접근 위치나 손 자세를 정확히 지정하지 않습니다.

**3. Arm과 Hand의 Action Rate·Joint Velocity는 각각 분리합니다.**

그룹 $G\in\lbrace\mathrm{arm},\mathrm{hand}\rbrace$에 대해:

```math
c_{\Delta G,t}
=
\frac{1}{n_G}
\sum_{j=1}^{n_G}
\left(
\frac{u^G_{t,j}-u^G_{t-1,j}}
{s^G_j}
\right)^2
```

$s^G_j$는 해당 Action의 정규화 스케일입니다. Arm과 Hand는 명령 범위와 의미가 다르므로 독립적으로 설정합니다.

실제 관절 속도는 다음처럼 평가합니다.

```math
c_{vG,t}
=
\frac{1}{|J_G|}
\sum_{j\in J_G}
\left(
\frac{\dot q_{t,j}}
{\dot q^{\mathrm{ref}}_j}
\right)^2
```

- Arm은 Arm 관절 집합을 사용합니다.
- Hand는 실제 구동 관절의 속도를 사용합니다.
- Mimic Joint를 중복 계산할지는 관절 구성에 맞춰 정합니다.
- 관절별 기준 속도로 정규화해 단위와 범위 차이를 줄입니다.

**Hand의 절대 Action이나 특정 기준 자세와의 차이는 벌점으로 주지 않겠습니다.** Hand가 절대 위치 명령을 받는다면 $u_h^2$는 0에 해당하는 자세를 선호하게 만들기 때문입니다.

단, Action Rate와 Joint Velocity도 현재 자세를 유지하려는 경향은 만듭니다. 따라서 초기 손 자세가 굽혀져 있다면, 펼칠 이득이 없는 동안 굽힌 자세가 유지될 수 있습니다. 이것은 별도로 확인해야 합니다.

**4. 물체 기울기는 Dead Zone을 둔 연속 페널티로 처리합니다.**

물체의 위쪽 축과 상판 법선 사이 각도를 $\theta_t$로 정의합니다.

```math
\theta_t=
\cos^{-1}
\left(
\mathrm{clip}
\left(
\mathbf{z}_{\mathrm{object},t}^{\mathsf T}
\mathbf{n}_{\mathrm{table}},
-1,1
\right)
\right)
```

```math
c_{\mathrm{tilt},t}
=
\left[
\mathrm{clip}
\left(
\frac{\theta_t-\theta_{\mathrm{free}}}
{\theta_{\mathrm{fail}}-\theta_{\mathrm{free}}},
0,1
\right)
\right]^2
```

| 기울기 | 처리 |
|---|---|
| $\theta\leq\theta_{\mathrm{free}}$ | 페널티 없음 |
| $\theta_{\mathrm{free}}<\theta<\theta_{\mathrm{fail}}$ | 기울어질수록 페널티 증가 |
| $\theta\geq\theta_{\mathrm{fail}}$ | 전도 실패 판정 및 종료 |

$\theta_{\mathrm{free}}$는 우선 **5° 정도를 시험값**으로 사용할 수 있습니다. $\theta_{\mathrm{fail}}$은 해당 실린더가 실제로 넘어지는 상태와 시뮬레이션 로그를 대조해 정해야 합니다.

이렇게 하면 약한 흔들림은 허용하면서도, 지속적으로 물체를 기울여 미는 행동에는 비용을 줄 수 있습니다. 실린더의 수평 Yaw 회전은 이 항에 포함되지 않습니다.

**5. 선반 페널티는 선반의 물리 설정에 맞춰 정의해야 합니다.**

선반 페널티는 기존 상태를 유지

**6. 성공 보상은 충분히 크게, 한 번만 지급합니다.**

성공은 다음 조건을 일정 시간 유지하는 것으로 제안합니다.

- 목표 평면 오차 1 cm 미만.
- 물체 평면 속도 2 cm/s 미만.
- 물체가 거의 직립한 상태.
- 상판 위에 지지되어 있고 실패 조건이 없음.
- 위 조건을 우선 0.3초 유지.

직립 허용각은 초기 시험값으로 10° 정도를 검토할 수 있습니다. 이는 손 자세에 대한 요구가 아니라 **최종 물체 상태에 대한 요구**입니다.

성공이 확정되면 큰 보상을 한 번 지급하고 종료합니다. Homing은 요구하지 않습니다. 목표점을 지나가거나, 넘어지는 순간 목표에 들어온 경우에는 성공 보상을 지급하지 않습니다.

---

초기 가중치는 아래처럼 시작할 수 있습니다.

| 항목 | 시작값 제안 | 해석 |
|---|---:|---|
| 목표 거리 $w_g$ | 6.0 | 기존 주보상 비중 유지 |
| 접근 $w_{\mathrm{reach}}$ | 1.0 | 에피소드 전체 최대 +1 |
| Arm Action Rate | 0.03 | 정규화된 그룹 평균에 적용 |
| Hand Action Rate | 0.03 | Arm과 별도 조정 |
| Arm Joint Velocity | 0.01 | 초기에는 약하게 적용 |
| Hand Joint Velocity | 0.01 | 초기에는 약하게 적용 |
| 물체 기울기 | 2.0 | Dead Zone 이후 증가 |
| 선반 교란·접촉 | 0.5 | 위 정규화 정의를 전제로 함 |
| 시간 비용 | 0.1 | 초당 비용 |
| 성공 이벤트 | +30 | 한 번 지급 |
| 전도 등 실패 이벤트 | −80 | 한 번 지급 |

실패 −80은 **예를 들어 최대 10초인 초기 실험을 가정한 값**입니다. 제한 시간과 실제 누적 비용에 맞춰 조정해야 합니다. 실패 페널티가 너무 작으면 빨리 실패해서 이후 비용을 피하는 행동이 유리해질 수 있습니다.

또한 기존 `−0.03 × 제곱합`과 이번 `−0.03 × 정규화 평균`은 실제 세기가 다릅니다. 숫자만 그대로 비교하면 안 됩니다.

**Hand가 자꾸 굽혀지는 원인은 현재 표만으로 확정할 수 없습니다.** 다만 우선 확인할 항목은 명확합니다.

| 확인 항목 | 가능한 원인 |
|---|---|
| Action 0이 어떤 손 자세인가 | 초기 정책 출력이 이미 굽힘 자세에 대응 |
| 정책 출력 → Clip → Joint Target 변환 | 중립 출력과 실제 중립 자세가 불일치 |
| Reaching 거리 기준점 | 손가락 굽힘으로 거리가 감소 |
| 가상 finger 프레임 높이 | 굽힘으로 선반 페널티 감소 |
| 초기 Hand 자세 | 변화량·속도 페널티 때문에 초기 굽힘 유지 |
| Hand Action 변화와 물체 이동 | 실제로 굽힌 상태가 현재 환경에서 유리할 가능성 |

가장 직접적인 점검은 **동일한 Arm 자세에서 Hand 명령만 변화시키며 보상 항별 값과 실제 Joint Target을 기록하는 것**입니다. 특정 자세를 선호하지 않도록 보상을 설계하는 것과, 학습 결과가 특정 자세를 선택하는 것은 구분해야 합니다.

이 초안은 정지 상태에서 반복해서 받을 수 있는 양의 보상을 제거하고, 접근 보상에는 총량 제한을 두며, 최종 성공에 가장 큰 이득을 줍니다. 다만 이것만으로 학습 성공이 보장되지는 않습니다. Initial Joint에서 출발하면 성공까지 시간이 길어지므로, **제어 주기와 할인율이 성공 보상을 지나치게 약화시키지 않는지**도 함께 확인해야 합니다.


---

추가적으로, 터미네이션 조건은 크게 변경하지 않습니다. 변경된 리워드에 맞추어 조건 자체는 다소 변경될 수 있습니다.

- 물체를 완전히 넘어트리거나, 선반 영역 밖으로 떨어트리면 터미네이션
- 물체를 지나치게 빠르게 밀 경우 터미네이션
- 선반과 크게 충돌해 선반의 좌표를 크게 이탈하였을 경우에 터미네이션

