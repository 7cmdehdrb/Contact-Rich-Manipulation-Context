# 접근·목표 진행 보상 4종의 수식

[구현 문서 안내](../README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [작성·검증 로그](../logs/2026-10-16_reward_formulas.md)

기준일: 2026-10-16. 활성 패키지 `src/inspire_sweep_baseline`의 현재 구현을 수식으로 정리한다. 보상 설계 제안이나 학습 성능 평가가 아니라 **코드에서 실제 계산하는 값**의 설명이다. 기준 workspace commit은 `301099db55cea61b7a715fcd8bf0b46d357214b2`다.

## 1. 공통 기호와 보상 적용 방식

환경 하나를 기준으로 쓰며, 실제 구현은 환경별로 독립적인 상태를 저장해 벡터 연산한다. $t=0$은 scene reset 직후, $t\geq1$은 이후 보상 호출 시점이다.

| 기호 | 의미 | 코드 대응 |
| --- | --- | --- |
| $\mathbf{e}_t\in\mathbb{R}^3$ | 월드 좌표계 EEF 위치 | `scene[frame_name].data.target_pos_w[:, 0]` |
| $\mathbf{o}_t\in\mathbb{R}^3$ | 현재 선택된 대상 물체의 link 원점 위치 | `_target_state(env)[:, :3]` |
| $\mathbf{g}_t\in\mathbb{R}^2$ | 현재 목표 command의 월드 XY 위치 | `command_manager.get_command(command_name)[:, :2]` |
| $\mathbf{v}^{xy}, v^z$ | 벡터의 XY 성분, Z 성분 | `:2`, `2` |
| $\rho$ | 접근 거리의 동등 영역 반경 | `near_radius`, 기본 0.10 m |
| $\tau$ | 목표 위치 허용 오차 | `position_tolerance`, 기본 0.01 m |
| $\varepsilon$ | 나눗셈 안정화 상수 | `epsilon`, 기본 $10^{-6}$ |
| $\Delta t$ | 정책 제어 스텝의 시간 간격 | `env.step_dt` |
| $w$ | 해당 보상 항의 설정 가중치 | `RewardTermCfg.weight` |

보조 표기를 다음과 같이 정의한다.

```math
[x]_+=\max(x,0),\qquad \mathrm{clip}_{[0,1]}(x)=\min(1,\max(0,x)).
```

네 클래스는 모두 스텝별 계산값 $q_t$를 시간 간격으로 나눈 $f_t$를 반환한다. Isaac Lab `RewardManager`가 여기에 가중치와 시간 간격을 곱하므로, 최종 스텝 보상 기여량 $R_t$는 다음과 같다.

```math
f_t=\frac{q_t}{\Delta t},\qquad R_t=w\,\Delta t\,f_t=wq_t.
```

이하 식의 $q_t$는 **시간 간격 보정과 가중치 적용 전의 스텝별 값**이다. `RewardManager`의 스텝 통계 `_step_reward`에는 $R_t/\Delta t$가 저장되므로, 통계값과 실제 스텝 보상 기여량을 구분한다.

물체 위치는 질량중심이 아닌 `object_link_state_w`의 link 원점이다. 현재 원기둥 자산에서는 바닥 원점에 해당한다. EEF는 기본 `ee_frame`의 첫 번째 target이며 손목 조립체에 고정되어 있어 손가락만 굽히는 것으로 이동하지 않는다. 접근 거리에는 현재 물체 위치가 사용되므로 물체가 EEF 쪽으로 움직여도 접근으로 계산될 수 있다.

## 2. goal_rewards.HeightGatedPlanarReachProgress

현재 물체에 대한 **XY 접근 기록 개선**을 초기 거리로 정규화하고, 높이 조건을 만족할 때 양의 보상을 준다. 최고 접근 기록에서 멀어지면 높이와 무관하게 매 스텝 음의 보상을 준다.

### 거리·초기화·높이 조건

반경 안의 모든 XY 위치는 남은 거리 0으로 처리한다.

```math
d_t=\left[\left\|\mathbf{e}_t^{xy}-\mathbf{o}_t^{xy}\right\|_2-\rho\right]_+,
\qquad b_0=d_0.
```

$b_{t-1}$은 현재 호출 전까지 저장한 최소 남은 거리다. 정규화 분모 $s$는 reset에서 정한 고정값이다.

```math
s=\begin{cases}
d_0, & d_0>\varepsilon,\\
\max(\rho,\varepsilon), & d_0\leq\varepsilon.
\end{cases}
```

높이 판정은 현재 물체의 Z 위치에 상대적으로 적용한다.

```math
h_t=\begin{cases}
1, & \left|e_t^z-(o_t^z+z_{\mathrm{offset}})\right|\leq z_{\mathrm{tol}},\\
0, & \text{그 외}.
\end{cases}
```

기본값은 `z_offset=0.09` m, `z_tolerance=0.02` m다. 따라서 허용 EEF 높이는 현재 물체 바닥 기준 0.07–0.11 m이며, 높이 0.10 m 원기둥의 기하 중심보다 0.04 m 높은 곳을 중심으로 ±0.02 m다.

### 스텝 보상과 기록 갱신

**기록을 갱신하기 전**의 $b_{t-1}$로 부호 있는 차이 $u_t$를 계산한다.

```math
u_t=\frac{b_{t-1}-d_t}{s},\qquad
q_t=\begin{cases}
u_t, & h_t=1\ \text{또는}\ u_t<0,\\
0, & \text{그 외},
\end{cases}
\qquad b_t=\min(b_{t-1},d_t).
```

- 새 기록인 $d_t<b_{t-1}$에서는 높이 조건을 만족해야 양의 보상을 받는다.
- 높이 조건 밖에서 접근해도 최소 거리 기록은 갱신된다. 이후 Z만 맞추어 같은 XY 기록의 보상을 다시 받을 수 없다.
- $d_t>b_{t-1}$이면 최고 기록 대비 이탈량만큼 매 스텝 감점된다. 직전 스텝보다 가까워졌더라도 최고 기록보다 멀면 음수다.
- 최고 기록으로 돌아오거나 그 위치에 머무르면 0이다. 반경 안에서는 모두 $d_t=0$이므로 추가 접근 보상이 없다.
- 양의 보상 누적은 최대 $d_0/s\leq1$이다. 음의 보상은 반복되며, 단일 스텝 하한 clamp도 없다. 따라서 전체 누적값은 0–1로 제한되지 않는다.

$\Delta t$로 나누므로 이탈 감점은 초당 비용이 아닌 스텝당 비용이다. 같은 이탈 상태를 같은 실제 시간 유지하더라도 제어 스텝 수가 많아지면 누적 감점이 커진다.

## 3. goal_rewards.PlanarGoalProgress

물체가 XY 목표에 가까워진 비율을 초기 목표 거리로 정규화하고, **에피소드 최고 진행률의 증가분만** 보상한다. 높이 조건과 후퇴 페널티는 없다.

### 거리와 진행률

Reset에서 물체의 초기 XY 위치 $\mathbf{o}_0^{xy}$를 저장하고 최고 진행률을 0으로 초기화한다. 목표는 reset에서 저장하지 않고 보상 호출 시 현재 command를 읽는다.

```math
D_{0,t}=\left\|\mathbf{o}_0^{xy}-\mathbf{g}_t\right\|_2,\qquad
D_t=\left\|\mathbf{o}_t^{xy}-\mathbf{g}_t\right\|_2,\qquad
A_t=[D_{0,t}-\tau]_+.
```

```math
p_t=\begin{cases}
\mathrm{clip}_{[0,1]}\left(\dfrac{D_{0,t}-D_t}{\max(A_t,\varepsilon)}\right), & A_t>\varepsilon,\\
0, & A_t\leq\varepsilon.
\end{cases}
```

### 스텝 보상과 기록 갱신

```math
B_0=0,\qquad B_t=\max(B_{t-1},p_t),\qquad q_t=B_t-B_{t-1}.
```

목표가 에피소드 동안 고정되고 초기 거리가 충분하면, 초기 위치에서 $p=0$, 목표 허용 오차 안에서 $p=1$이다. 대기·후퇴·이전 최고 위치 복귀는 0이고, 새로운 최고 진행률만 양수다. 가중치 적용 전 에피소드 누적 보상은 망원합으로 $B_T\leq1$이다. 처음부터 $A_t\leq\varepsilon$이면 0을 반환한다.

현재 command를 사용하는 이유는 reward reset 이후 command reset이 이루어지기 때문이다. Reset에서는 물체 위치만 저장하고 첫 호출에서 새 목표를 읽으므로, 이전 에피소드 목표가 섞이지 않으며 첫 행동의 진행도 포함된다. 다만 목표를 에피소드 중 변경하면 $D_{0,t}$도 재계산되며, 누적값을 단일 고정 목표에 대한 진행률로 해석할 수 없다.

## 4. dex_rewards.DexReachProgress

현재 물체에 대한 **3차원 접근 거리 기록의 개선량을 m 단위로** 보상한다. 초기 거리 정규화, 높이 gate, 후퇴 페널티는 없다.

`ReachProgress.reset`을 상속해 reset 시 3차원 남은 거리와 최소 기록을 초기화한다.

```math
d_t^{3D}=\left[\left\|\mathbf{e}_t-\mathbf{o}_t\right\|_2-\rho\right]_+,
\qquad b_0^{3D}=d_0^{3D}.
```

```math
b_t^{3D}=\min(b_{t-1}^{3D},d_t^{3D}),\qquad
q_t=b_{t-1}^{3D}-b_t^{3D}=[b_{t-1}^{3D}-d_t^{3D}]_+.
```

초기 남은 거리가 클수록 획득 가능한 총 개선량도 크다. 가중치 적용 전 누적 보상은 다음과 같다.

```math
\sum_{t=1}^{T}q_t=d_0^{3D}-b_T^{3D}\leq d_0^{3D}.
```

반경 안에 들어오면 남은 거리가 0이 되어 보상 예산을 모두 사용한다. 대기·후퇴·이전 최고 거리 복귀는 모두 0이다. 처음부터 반경 안에서 시작하면 예산이 0이므로 이후 멀어졌다 돌아와도 보상이 없다. 높이 차이가 3차원 거리에 포함되지만 별도의 목표 높이 조건은 아니다.

## 5. dex_rewards.DexPlanarGoalProgress

목표 허용 오차를 제외한 XY 남은 거리에서 **에피소드 최고 개선량의 증가분을 m 단위로** 보상한다. 정규화, 높이 gate, 후퇴 페널티는 없다.

`PlanarGoalProgress.reset`을 상속해 초기 물체 XY 위치를 저장하지만, `_best_progress`에는 비율 대신 개선 거리(m)를 저장한다. $D_{0,t}$와 $D_t$는 3절과 동일하다.

```math
A_t=[D_{0,t}-\tau]_+,\qquad L_t=[D_t-\tau]_+,\qquad p_t^{m}=[A_t-L_t]_+.
```

```math
M_0=0,\qquad M_t=\max(M_{t-1},p_t^{m}),\qquad q_t=M_t-M_{t-1}.
```

목표가 에피소드 동안 고정되면 $0\leq p_t^{m}\leq A$, 누적 보상은 $M_T\leq A=[D_0-\tau]_+$다. 목표 허용 오차 안에서는 $L_t=0$이 되어 남은 예산을 모두 사용한다. 대기·후퇴·이전 최고 위치 복귀는 0이다. 초기부터 허용 오차 안이면 예산도 0이다.

이 항은 `epsilon` 분기를 사용하지 않으므로 초기 남은 거리가 아주 작더라도 양수이면 그 거리만큼 보상할 수 있다. 목표 command의 reset 순서와 에피소드 중 변경에 대한 주의점은 3절과 같다. 목표가 변경되면 거리 예산 $A_t$도 바뀐다.

## 6. 네 항의 차이와 현재 가중치

| 클래스 | 거리 | 스텝별 값의 단위 | 높이 조건 | 최고 기록보다 후퇴 | 가중치 전 누적 상한: 고정 목표·정상 reset |
| --- | --- | --- | --- | --- | --- |
| `HeightGatedPlanarReachProgress` | EEF–현재 물체 XY, 반경 제외 | 무차원 | 양의 값에만 적용 | 이탈 중 매 스텝 음수 | 양의 값 합 최대 1, 전체 합 하한 보장 없음 |
| `PlanarGoalProgress` | 물체–목표 XY | 무차원 | 없음 | 0 | 1 |
| `DexReachProgress` | EEF–현재 물체 3D, 반경 제외 | m | 없음 | 0 | 초기 3D 남은 거리 |
| `DexPlanarGoalProgress` | 물체–목표 XY, 허용 오차 제외 | m | 없음 | 0 | 초기 XY 거리 − 허용 오차의 양수부 |

현재 Renewal 설정의 가중치는 다음과 같다. 클래스 자체가 가중치를 내장하는 것은 아니며, 다른 설정에서는 해당 `RewTerm`을 확인해야 한다.

| 설정 | 접근 항 $w$ | 목표 항 $w$ | 최종 스텝 보상 기여량 |
| --- | --- | --- | --- |
| `OmniRenewalRewardsCfg` | 30 | 40 | 각각 $30q_t$, $40q_t$ |
| `DexOmniRenewalRewardsCfg` | 30 | 300 | 각각 $30q_t$, $300q_t$ |

예를 들어 새 기록이 0.01 m 개선되었을 때 Dex 접근 보상은 $30\times0.01=0.3$, Dex 목표 보상은 $300\times0.01=3.0$이다. 정규화 보상의 경우 같은 0.01 m도 초기 거리 분모에 따라 값이 달라진다.

### 계산 예시: 높이 조건부 접근과 Dex 접근

$\rho=0.10$ m, 초기 XY 거리 0.60 m이면 높이 조건부 접근의 $d_0=s=0.50$ m다. 높이 조건을 만족하면서 XY 거리가 0.40 m가 되면 $q=(0.50-0.30)/0.50=0.4$이고, 가중치 30에서 실제 기여량은 12다. 이후 XY 거리가 0.45 m라면 최고 기록은 여전히 0.30 m이므로 $q=(0.30-0.35)/0.50=-0.1$, 매 스텝 기여량은 −3이다. XY 거리 0.40 m로 돌아오면 0이다.

Dex 접근에서는 별도로 3차원 거리가 0.60 m에서 0.40 m로 줄었다고 하면 개선량 0.20 m에 대해 $q=0.20$, 가중치 30에서 6을 얻는다. 이후 0.45 m로 멀어지거나 0.40 m로 복귀해도 0이다. 두 항은 거리 차원도 다르므로 같은 XY 이동만으로 개선량이 같다고 가정할 수 없다.

### 계산 예시: 두 목표 진행 항

초기 목표 거리 0.21 m, $\tau=0.01$ m이면 남은 예산은 0.20 m다. 현재 목표 거리가 0.11 m가 되는 첫 기록 개선에서 `PlanarGoalProgress`는 $q=0.10/0.20=0.5$, 가중치 40에서 20을 준다. `DexPlanarGoalProgress`는 $q=0.10$ m, 가중치 300에서 30을 준다. 이후 목표 허용 오차까지 도달하면 각각 나머지 0.5와 0.10 m를 지급하고, 그 뒤 대기하거나 후퇴 후 돌아와도 추가 지급하지 않는다.

## 7. 구현 근거와 검증 범위

- [goal_rewards.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_rewards.py): `_target_state`, `ReachProgress.reset`, `HeightGatedPlanarReachProgress`, `PlanarGoalProgress`.
- [dex_rewards.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/dex_rewards.py): `DexReachProgress`, `DexPlanarGoalProgress`.
- [Omni Renewal 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_renewal_envs.py), [Dex Renewal 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_renewal_envs.py): 적용 가중치·파라미터.
- [RewardManager](../../../../IsaacLab/source/isaaclab/isaaclab/managers/reward_manager.py): `compute(dt)`의 가중치·시간 간격 곱셈과 스텝 통계.
- [goal 보상 테스트](../../../../src/inspire_sweep_baseline/tests/test_goal_rewards.py), [Dex 보상 테스트](../../../../src/inspire_sweep_baseline/tests/test_dex_rewards.py): 기록 갱신, 반복 지급 방지, 부분 reset, 높이 조건, 반복 이탈과 서로 다른 시간 간격의 CPU 검증.

이번 작업에서 위 두 테스트 파일을 실행해 **51 passed**를 확인했다. Markdown 수식·링크 검사와 정확한 실행 명령은 [개발 로그](../logs/2026-10-16_reward_formulas.md)에 기록한다. Isaac Sim 학습·재생, 실물 검증과 GitHub 웹 수식 렌더링은 실행하지 않았다. 외부 코드 링크는 통합 workspace checkout에서 연결되며, 문서 저장소만 별도로 clone하면 해당 코드가 필요하다.
