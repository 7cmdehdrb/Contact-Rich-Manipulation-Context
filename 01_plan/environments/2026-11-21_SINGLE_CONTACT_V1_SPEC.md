# Inspire-Sweep-Single-Contact-v1 개발 명세

작성일: 2026-11-21. 최초 상태는 명세 작성만 완료였으며, **후속 구현 요청으로 환경 구현·등록 및 CPU/GPU·PPO1회 smoke를 완료**했다. [구현·검증 기록](../../02_implementation/logs/2026-11-21_single_contact_v1_implementation.md)을 따른다. 이하 명세 작성 시점의 예정 표현과 오프라인 분석 한계는 당시 이력이다. 장기 학습·성공률 개선은 미검증이다.

이 문서는 `Inspire-Sweep-Single-Contact-v0`를 직접 상속할 `Inspire-Sweep-Single-Contact-v1`의 구현 계약이다. 사용자 후속 정정을 우선하며, [교수님 지침](../../../../docs/instruction.md)의 목적 정의 → 항 관계 → 함수 특성 → 실제 궤적 재계산 → 가중치 선정 → 향후 행동 검증 순서로 작성했다. 여기서 재계산은 기존 v0 궤적의 오프라인 평가이며 v1 정책의 성능 측정이 아니다.

## 1. 요청 확정과 변경 범위

| 항목 | 확정 계약 |
| --- | --- |
| 부모 | `Inspire-Sweep-Single-Contact-v0` 직접 상속. 기존 v0의 함수 결과·설정·등록 보존 |
| Reaching 함수 | 움직이는 접근 목표에 대한 5cm 초과 거리의 감소를 보상, 증가를 같은 계수로 벌점. 최소 거리 기록·지속 근접 보상 없음 |
| 접근 위치 | 물체의 top-down 외접 원주에서 초기 의도 밀기 방향의 반대편. 중심은 물체를 따라 이동 |
| 구역3 예외 | 구역3(당기기) 전체에서 일반 반대편 규칙을 대체하여 **12시에서 시계방향 +15°인 단일 원주점**. 구역1은 밀기 반대편 유지. 원호·±각도 범위 없음 |
| 회전 독립성 | 접근점은 물체 이동을 따라가지만 물체 회전에 따라 공전하지 않음. 반경과 선반 기준 방향 고정 |
| Reaching 가중치 | 성공 궤적 기준 약3:7의 Reaching:Sweeping 순보상을 목표로 **4.9**. 고정 계수, 실행 중 비율 제한·동적 재조정 없음 |
| 손바닥/손등 | 구역1/2 손등, 구역3/4 손바닥. 선호1.5·반대0.7·미분류1.0 및 하중 혼합 방식 유지 |
| 방향 함수 | 수평 힘과 현재 목표 방향의 각도에 $\theta_0=30^\circ$, $p=4$의 signed 지수 함수 적용 |
| 팔 종료 페널티 | 기존 팔 속도 종료가 발생한 step에 일회 **-3.0** |
| 보류 | 거리별 방향 가중, 근거리 정밀도 함수, 감속 평가, 진행/후퇴 계수 재구성 |
| 제외 | 손끝 비용, 주먹 강제·자세 보상, 실시간 타겟 Actor 관측 추가, 성공 기준 변경 |

사용자 표현 중 “Sweeping의30%”와 “Reaching:Sweeping=3:7”은 수학적으로 다르다. **뒤의 명시적인3:7 의도를 채택**한다. 따라서 Reaching 평균은 Sweeping 평균의3/7, 약42.9%에 맞추며 두 항 합에서 약30%를 차지하도록 초기 계수를 정한다. 이 비율을 매 step·매 episode·구역별로 강제하지 않는다.

최종 사용자 정정에 따라 오른쪽 접근과 손바닥 접근 기회를 늘리는 예외는 **구역3(당기기)**에 적용한다. 구역3의 기존 선호도 손바닥1.5·손등0.7이므로 그대로 유지한다. 구역1은 일반적인 밀기 반대편 접근점과 손등 선호를 유지한다. 구역3의 밀기 방향 범위 자체를+15°로 바꾸는 것이 아니라, 구역3 episode에서 손의 접근점만+15°에 두는 것이다.

기존10cm는 물체 부피를 고려한 여유였으나, 새 접근점은 물체 외접 원주에 있으므로 **접근점으로부터의 허용 거리는5cm**로 줄인다. 물체 외접 원 반경과 이5cm 허용 거리는 서로 다른 값이다.

## 2. 기준 코드·등록·상속

기준은 [현재 v0 계약](../../02_implementation/environments/SWEEP_V0.md#single-contact-파생-환경)과 다음 실제 코드다.

| 역할 | 현행 부모 | v1 예정 선언 |
| --- | --- | --- |
| Gym ID | `Inspire-Sweep-Single-Contact-v0` | `Inspire-Sweep-Single-Contact-v1` |
| [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_v0_envs.py) | `SweepSingleContactEnvCfg` | `SweepSingleContactV1EnvCfg(SweepSingleContactEnvCfg)` |
| [Runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/sweep_v0.py) | `SweepSingleContactEnv` | `SweepSingleContactV1Env(SweepSingleContactEnv)` |
| [접촉 state](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/sweep_v0_state.py) | `SingleContactSweepState` | `SingleContactV1SweepState(SingleContactSweepState)` |
| [PPO Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/sweep_v0_ppo_cfg.py) | `SweepSingleContactPPORunnerCfg` | `SweepSingleContactV1PPORunnerCfg(SweepSingleContactPPORunnerCfg)` |
| experiment name | `inspire_sweep_single_contact_v0` | `inspire_sweep_single_contact_v1` |

예정 Gym entry point는 `inspire_sweep_baseline.runtime.sweep_v0:SweepSingleContactV1Env`, EnvCfg entry point는 `inspire_sweep_baseline.envs.sweep_v0_envs:SweepSingleContactV1EnvCfg`, PPO entry point는 `inspire_sweep_baseline.agent.sweep_v0_ppo_cfg:SweepSingleContactV1PPORunnerCfg`다. **이 이름들은 이번 작업에서 등록하거나 구현하지 않았다.**

같은 계열의 기존 역할별 파일에 파생 클래스를 추가하며, 버전별 폴더 생성·부모 함수 이동·기존 runtime 재작성은 하지 않는다. 보상 계산은 `mdp/reward_functions/`, 공유 기하·상태는 `mdp/common/`, 연결만 EnvCfg/runtime에 둔다.

## 3. 접근점 기하와 좌표

### 3.1 두 목표의 구분

- 물체 최종 목표 $\mathbf{g}$: 기존 Command의 목표. Sweep 거리·성공 판정용이며 변경하지 않는다.
- 손 접근 목표 $\mathbf{a}_t$: 이번 Reaching만 평가하는 단일 점. Command나 Actor 입력을 대체하지 않는다.
- 물체 중심 $\mathbf{c}_t$: 기존 `centroid(env)`와 같은 **현재 물체 link pose로 변환한 local bounds 중심**. 질량중심과 구분한다.
- 손 위치 $\mathbf{h}_t$: 기존 `ee_frame`의 EEF 위치. 손끝·손바닥 중심으로 바꾸지 않는다.

top-down 기하는 reset 시 선반 좌표계의 XY 평면에서 정의한다. 이 기준 좌표계는 episode 동안 고정하여 선반 움직임으로 보상 기준이 바뀌지 않게 한다. 12시=-shelf X, 3시=+shelf Y, 6시=+shelf X, 9시=-shelf Y다. 아래 그림의 오른쪽은 로봇 오른쪽, 위쪽은 선반 안쪽이다. 기존 영상의 화면축(right=-Y/up=+X)과 혼동하지 않는다.

### 3.2 외접 원의 구현 근사

사용자의 “외접하는 원의 느낌, 엄격한 강제 아님”과 회전 독립성 요구에 따라 **기존 scaled local bounds의 직립 XY footprint를 감싸는 원**을 사용한다. 중심은 bounds 중심이며, 반경 $R$은 local XY 반폭 벡터의 길이다. 별도 mesh 탐색이나 최소 외접 원 solver를 추가하지 않는다. 반경 계산에도 물체 회전 quaternion을 사용하지 않는다.

```math
R=\frac{1}{2}\sqrt{(b_{\max,X}-b_{\min,X})^2+(b_{\max,Y}-b_{\min,Y})^2}.
```

반경과 기준 방향은 reset마다 계산하고 episode 중 고정한다. 중심 $\mathbf{c}_t$는 매 step 현재 물체를 따라 이동한다. **물체 회전으로 방향 벡터를 회전시키거나 반경을 다시 계산하지 않는다.** 중심 위치가 같다면 물체가 회전해도 접근점은 같다. 기울어진 물체의 실제 실루엣에 항상 밀착하는 외접 원은 아니며, 틸트·낙하 보호는 부모 비용/종료가 담당한다. 기하 중심의 실제 병진은 따라가되 회전 자체로 접근점이 공전하지 않게 하는 근사다. 물체 scale을 이미 반영한 bounds에 scale을 다시 곱하지 않는다.

이번 평가 bank의 물체 외접 원 반경은 약5.11–6.22cm였다. 접근 허용 거리는 원주점으로부터5cm이며, 물체 중심으로부터5cm가 아니다. 접근 방향을 유도하되 원주점에 정확히 손을 놓도록 강제하지 않는다.

### 3.3 일반 구역1·2·4

초기 `sweep_dir`의 선반 XY 단위 방향을 $\mathbf{u}_0$라 한다. 현재 물체→최종목표 방향으로 매 step 바꾸지 않는다. 그래야 목표를 지나친 뒤 접근점이 물체 반대편으로 갑자기 바뀌지 않는다.

```math
\mathbf{a}_{t,XY}=\mathbf{c}_{t,XY}-R\mathbf{u}_0,\qquad
a_{t,Z}=c_{t,Z}.
```

구역1에서 선반 안쪽으로 밀면 로봇 쪽 반대편 원주, 오른쪽으로 밀면 왼쪽 원주, 왼쪽으로 밀면 오른쪽 원주가 접근점이다. 방향별 추가 원호 폭이나 임의의 랜덤 접근점은 넣지 않는다. 부드러운 허용 범위는 Reaching의5cm 여유가 제공한다.

### 3.4 구역3(당기기) 예외

구역은 부모의 초기 의도 방향으로 판정한다. 구역3의 전체 범위는 기존처럼6시 중심 ±30°, 즉12시 기준 절댓값150° 이상이다. 구역3으로 분류된 모든 episode는 실제 당기기 각도가 그 안에서 무엇이든 **접근점을12시에서 시계방향+15°인 단일 원주점**으로 둔다. 구역3에서만 일반 반대편 원주 규칙을 대체하며, 구역1에는 이 예외를 적용하지 않는다.

```math
\mathbf{a}_t=\mathbf{c}_t+R(-\cos15^\circ,\sin15^\circ,0).
```

각도는 **선반 기준12시에서 시계방향으로15°**다. 손 위치에 따라 각도를 선택하지 않고, 원호 최단점·무작위 각도·1시30° 기준을 사용하지 않는다. 벡터 $(-\cos15^\circ,\sin15^\circ,0)$에 물체 quaternion을 곱하지 않는다. 손에서 이 점까지의3D 거리를 사용한다.

![접근점·허용 거리](../../../../outputs/reward_design/2026-11-21_single_contact_v1_spec/approach_geometry.png)

회색은 물체 bounds를 감싸는 원, 파란 화살표는 밀기 방향, 주황 점은 접근 목표다. 주황 옅은 영역은 동일 높이에서5cm 허용 범위를 설명한다. 실제 오차는3D 거리다.

## 4. Reaching 식·상태·가중치

### 4.1 최종 식

```math
\ell_t=\|\mathbf{h}_t-\mathbf{a}_t\|,\qquad
e_t=\max(\ell_t-0.05,0),\qquad
r_{R,t}=4.9(e_{t-1}-e_t).
```

RewardManager term `reaching`은 유지하고 callable만 파생 전용으로 교체한다. **Cfg weight=4.9, callable 반환값=$(e_{t-1}-e_t)/\Delta t$**로 하여 최종 step 기여가 위 식이 되게 한다. 기존 weight0.8·decay_distance0.35·거리45cm cutoff·상태별 지속 지급은 새 term에서 사용하지 않는다.

- 5cm 밖에서 오차가1cm 줄면 +0.049, 늘면 -0.049다.
- 5cm 내부·경계에서는 $e=0$이며 추가 접근 보상은 없다. 내부에서 외부로 나갈 때만 증가한 초과 거리만큼 비용이 생긴다.
- 접근 목표는 물체를 따라 움직인다. 물체가 멀어지면 비용, 손이 따라가며 오차를 줄이면 보상이 생긴다. 같은 간격으로 따라가는 동안에는0이다.
- 최소 오차 기록, 양수 부분만 지급, 접촉 시 초기화, episode 길이 정규화, 초기 거리 나눗셈, Reaching:Sweep 비율 cap은 사용하지 않는다.
- 같은 오차로 돌아오는 왕복의 **할인 전 합은0**이다. PPO gamma0.98에서 할인된 return까지 왕복 유인이 완전히 사라진다는 보장은 하지 않는다.
- 정상적인 밀기로 물체가 손에서 멀어지는 구간에서도 비용이 발생할 수 있다. Sweep과의 동시 기여를 검증한다.

### 4.2 reset·종료·중복 계산

reset된 환경 행만 대상으로 최종 배치·Command reset이 끝난 뒤 반경·구역·초기 방향·초기 오차 $e_0$를 저장한다. `RewardManager.reset`은 `CommandManager.reset`보다 먼저 호출되므로, 그 시점에 이전 command로 초기 오차를 확정하면 안 된다. 파생 runtime의 `super()._reset_idx(env_ids)` 완료 후 초기화하는 계약을 사용한다. 첫 policy step부터 정상적인 $e_0-e_1$을 지급한다.

정책 step당 이전 오차는 한 번만 갱신한다. 로깅이나 같은 step의 중복 조회가 보상을0으로 바꾸지 않도록 계산값과 step stamp를 보관한다. terminal step의 보상은 이전 episode의 목표·물체·오차로 계산한 뒤 자동 reset한다. reset 간 순간이동은 Reaching에 포함하지 않는다. 부모 환경의 state와 공유하지 않는 파생 전용 버퍼를 사용한다.

### 4.3 성공 사례 기반 계수 산정

데이터는 `model_15800.pt`의 기존128환경·seed1729·500step 기록이다. 환경별 첫 episode만 사용하며 v0 성공82개를 계수 산정에 사용했다. 이후 자동 reset episode와 실패 episode는 산정 분모에 넣지 않았다. 성공 판정을 보상 실행에 사용하는 것은 아니며, **오프라인 계수 선택에서만 성공 표본을 사용**한다.

새 방향 함수와 아래 접촉면 부호 처리를 먼저 적용하여 Sweeping을 재계산한다. 이 명세에서 비율 산정용 Sweeping은 **signed `sweep_progress` + 기존 음수 `sweep_retreat`의 episode 합**이다. 기타 안정화·충돌·종료 비용은 포함하지 않는다. Reaching 역시 증가 비용을 포함한 signed episode 합을 사용한다.

```math
\bar R_1=\frac{1}{N}\sum_{i\in\mathrm{success}}\sum_t(e_{i,t-1}-e_{i,t}),\qquad
\bar S=\frac{1}{N}\sum_{i\in\mathrm{success}}\sum_t(r_{P,i,t}+r_{B,i,t}),
\qquad
w_R^*=\frac{3\bar S}{7\bar R_1}.
```

| 재계산 지표 | 성공82개 평균 |
| --- | ---: |
| weight1 Reaching 순거리 변화 | 0.226437m |
| 새 Sweep 양의 기여 | 3.118533 |
| 새 방향 함수의 음의 기여 | -0.432951 |
| 기존 후퇴 비용 | -0.077133 |
| Sweeping 순합 | 2.608449 |
| 계산상 Reaching 계수 | 4.936946 |
| 채택 고정 계수 | **4.9** |
| weight4.9 Reaching 양의 기여 | 1.347163 |
| weight4.9 Reaching 음의 기여 | -0.237622 |
| weight4.9 Reaching 순합 | **1.109541** |
| 두 순합 중 Reaching 비중 | **29.84%** |
| 양의 기여만 비교한 Reaching 비중 | 30.17% |

개별 episode의 비율 평균이 아니라 **episode 합의 집단 평균 비율**이다. 두 항 중 하나가 음수인 episode의 비율은 일반적인0–100% 기여율로 해석하지 않는다. 초기 오차를 일괄 ±1mm 바꾼 민감도 시나리오에서 산정 계수는 약4.915–4.959다. 따라서4.9는 근사적인 초기값이며, 소수점 이하 정밀 조정을 성능 향상의 근거로 해석하지 않는다. 이1mm는 오차 상한의 증명이 아니라 수치 민감도 검사다.

![가중치 산정과 episode 편차](../../../../outputs/reward_design/2026-11-21_single_contact_v1_spec/reward_calibration.png)

구역별 성공 표본과 순합은 다음과 같다. 구역별로 다른 가중치를 적용하지 않는다.

| 구역 | 성공 표본 | Reaching 순합 | Sweeping 순합 |
| --- | ---: | ---: | ---: |
| 1 | 14 | 1.015 | 1.704 |
| 2 | 29 | 0.989 | 2.568 |
| 3 | 1 | 1.375 | -0.948 |
| 4 | 38 | 1.229 | 3.066 |

82개 중4개는 새 식에서 Sweeping 순합이 음수다. 특히 구역3은 표본이1개뿐이며 방향 비용이 크다. 이는 새 함수가 기존 성공 행동 일부를 부정적으로 평가한다는 **검토 근거**다. 전체30:70이 맞는다는 이유로 구역3의 학습 개선까지 검증됐다고 판단하지 않는다.

## 5. Sweep 방향 함수와 면 계수

### 5.1 유지 조건·변경 입력

현재 타겟에 손이 가한 힘을 물리 substep2개에 걸쳐 평균한 $\mathbf{F}_t$를 사용한다. 관측 noise·clip·정규화된 wrist F/T를 사용하지 않는다. 방향 각도는 수평 힘 $\mathbf{F}_{t,XY}$와 현재 물체 중심→최종목표 XY 단위 방향 $\mathbf{u}_t$ 사이의0–180° 각도다.

```math
\theta_t=\arccos\left(\mathrm{clip}\left(
\frac{\mathbf{F}_{t,XY}\cdot\mathbf{u}_t}{\|\mathbf{F}_{t,XY}\|},-1,1\right)\right),
\qquad
A_t=2\exp[-\ln(2)(\theta_t/(\pi/6))^4]-1.
```

각도 계산 단위는 rad다. 부모 정렬식의 분모는3D 힘 norm이지만 새 함수는XY norm이므로, 수직 힘이 방향 점수에 섞이지 않는 변경임을 명시한다. 별도 수직 힘 보상이나 비용은 추가하지 않는다.

부모의 최근3 policy step 중2회 유효 접촉 및 EEF 상판 위12cm 미만 조건을 만족할 때 $h_t=1$, 아니면0이다. 현재 유효 접촉·유한값·수평 힘1N 이상·목표 XY 거리 $d_t>10^{-12}$ 조건을 $v_t$라 하고 $G_t=h_tv_t$로 둔다. 거리0 또는 유효 힘이 없는 경우 각도를 억지로0도로 간주해 보상하지 말고, 계산을 안전하게 mask하여 진행항을0으로 만든다. 부모의 접촉 문턱·높이·이력·force sampling 시점을 유지한다.

### 5.2 부호와 접촉면 배율

거리 감소량을 $\Delta_t=d_{t-1}-d_t$라 하면 먼저 signed 기본 진행값을 만든다.

```math
b_t=G_t\max(\Delta_t,0)A_t,
\qquad
r_{P,t}=50\left(c_t\max(b_t,0)+\min(b_t,0)\right),
\qquad
r_{B,t}=-10\max(-\Delta_t,0).
```

Manager term `sweep_progress`는 이름을 유지하되 signed 값을 허용한다. callable 반환값은 $(c_t\max(b_t,0)+\min(b_t,0))/\Delta t$, weight는50이다. `sweep_retreat`의 callable·weight-10·무접촉 후퇴 비용은 그대로다.

면 계수 $c_t$는 부모와 동일한 분류·법선 하중 비율로 계산한다. 선호1.5·반대0.7·미분류1.0을 유지하며 **양의 보상에만 곱한다**. 새 음수 방향 비용에는 배율1을 사용한다. 이는 선호 면일수록1.5배 더 큰 벌점을 받는 역전을 막기 위한 직전 제안의 부호 처리이며, 면 선호 수치를 재조정하는 것이 아니다.

| 초기 의도 구역 | 범위 | 선호 |
| --- | --- | --- |
| 1 전방 | 절댓값30° 이하 | 손등 |
| 2 오른쪽 | +30° 초과 +150° 미만 | 손등 |
| 3 후방 | 절댓값150° 이상 | 손바닥 |
| 4 왼쪽 | -150° 초과 -30° 미만 | 손바닥 |

양면 하중이 같으면1.1이며, 분류 하중 합이 부모의 작은 수 문턱 이하이면1.0이다. 미분류를 잘못된 면으로 재분류하지 않는다. 목표를 지나쳐도 초기 구역은 유지되지만 힘 방향 평가의 $\mathbf{u}_t$는 현재 목표 방향을 따른다.

| 상황 | 최종 처리 |
| --- | --- |
| 거리 감소·각도30° 미만 | 양의 진행값에 기존 면 배율 |
| 거리 감소·각도30° | 진행항0 |
| 거리 감소·각도30° 초과 | 음의 진행항, 면 배율 적용 안 함 |
| 거리 증가 | 기존 후퇴 비용. 음수 각도와 후퇴를 곱하여 양수로 만들지 않음 |
| 거리 변화0 | 진행·후퇴 모두0. 접촉만으로 독립 방향 보상/비용을 지급하지 않음 |
| 접촉/힘/높이/이력 gate 실패 | 진행항0, 후퇴 비용은 유지 |

![고정 방향 함수와 비교 후보](../../../../outputs/reward_design/2026-11-21_direction_revision/direction_function.png)

그림의 파란30°·p4가 v1 채택 함수이며, 나머지20°/45° 곡선은 비교 설명용이다. 방향 계수는0/10/15/20/30/45/60°에서1/0.983/0.915/0.744/0/-0.940/약-1이다. 현재 거리별 blending·근거리 예외·감속 항은 추가하지 않는다. 따라서 목표 가까이에서도 같은 각도 함수를 적용하며, 그로 인한 미세 복구 억제 가능성은 검증 대상이다.

이 버전은 기존 진행50/후퇴-10을 보존하므로 **Sweep의 왕복 순이득 가능성을 해결한 버전은 아니다.** 보류된 이전5번의 계수 대칭화·거리 potential을 슬쩍 포함하지 않는다.

## 6. Joint 종료 일회 비용

새 Reward term 이름은 `arm_joint_failure`, weight=-3.0이다. 기존 `arm_joint_velocity` Reward는 실제 속도 L2 비용이므로 이름을 덮어쓰지 않는다. Termination term `arm_joint_velocity`도 이름·threshold1.0·조건을 유지한다.

```math
f_{J,t}=\frac{\mathbf{1}[\text{termination.arm\_joint\_velocity}_t]}{\Delta t},
\qquad r_{J,t}=-3.0\Delta t f_{J,t}.
```

TerminationManager가 해당 step에 계산한 실제 boolean 결과를 읽는다. 별도 근사 속도 판정을 새로 만들지 않는다. 팔 관절 하나라도 절댓값1rad/s를 **초과**해야 종료하며, 정확히1rad/s에서는 이 종료가 발생하지 않는다. 한 step에 여러 관절이 초과해도 -3은 한 번이다. 다른 종료와 동시에 발생해도 Joint 비용은 한 번 지급하고 부모의 다른 비용은 그대로 적용한다.

정상 timeout에는0이며, 마지막 policy step 계산 후 자동 reset되는 수명으로 일회성을 보장한다. 정책 dt0.02에서 raw flag/dt는50, 최종 기여는-3이다. 임계값을0.8로 바꾸거나0.8 초과 연속 비용을 추가하지 않는다. 0.8 초과율은 평가 지표로만 수집한다.

## 7. 전체 보상·나머지 계약 대조

| 활성 Reward term | v0 weight | v1 weight | callable·동작 변경 |
| --- | ---: | ---: | --- |
| sweep_progress | 50 | 50 | fixed signed 각도 함수·양수 면 배율/음수 배율1 |
| sweep_retreat | -10 | -10 | 없음 |
| reaching | 0.8 | **4.9** | 현재 접근점까지5cm 초과 거리의 대칭 증분 |
| arm_action_rate | -0.03 | -0.03 | 없음 |
| hand_action_rate | -0.03 | -0.03 | 없음 |
| arm_joint_velocity | -0.03 | -0.03 | 없음 |
| hand_joint_velocity | -0.01 | -0.01 | 없음 |
| shelf_collision | -0.5 | -0.5 | 없음 |
| shelf_failure | -3 | -3 | 없음 |
| obstacle_contact | -0.04 | -0.04 | 없음. free_force50N 유지 |
| wrench_change | -0.1 | -0.1 | 없음. free30N/3Nm·ratio2.5·sharpness3·budget없음 유지 |
| object_tilt | -30 | -30 | 없음 |
| obstacle_displacement | -150 | -150 | 없음 |
| arm_action_limit | -0.03 | -0.03 | 없음 |
| hand_action_limit | -0.03 | -0.03 | 없음 |
| arm_joint_failure | 없음 | **-3** | 신규 일회 종료 비용 |

기존15개 term 순서를 유지하고 신규 비용은 마지막에 추가한다. Reaching/Sweep 계산의 선후에 따라 같은 step 물리 상태나 면 하중이 달라지지 않아야 한다. 미활성 goal_hold·goal_distance·success bonus·hand_contact·squeeze 항을 활성화하지 않는다.

| 구성 | 부모 보존 계약 |
| --- | --- |
| Scene·물성·배치 | 같은17슬롯/최대 장애물6·자산·scale·마찰·질량·충돌·Test 초기화·단일 Warp IK |
| 초기 접근 | 보상 목표만 변경. 로봇을 새 접근점에 배치하거나 초기 IK 분포를 바꾸지 않음 |
| 관측 | policy66D+obstacles64D, 기존 초기 표면점·현재 EEF·관절·목표·촉각·정규화 wrist 유지. Actor/Critic에 접근점·현재 물체 GT를 추가하지 않음 |
| 액션 | 팔6+손6, 기존 OSC·실행 clipping·raw action 비용·Last Action 표현 유지 |
| 시간 | physics dt0.01·decimation2·policy dt0.02·episode10초 |
| 종료 | 낙하/틸트·선반·팔속도·timeout·success callable과 임계값 모두 유지 |
| 성공 | 실제 부모 코드의10초 시점 현재 중심 XY 거리 **엄격히3cm 미만** 및 실패 없음. 이번 요청은 성공 경계 변경을 포함하지 않으므로 일반 지침의 다른 표기만으로 `<=`로 바꾸지 않음 |
| 커리큘럼 | 빈 구성 유지. 보상 계수를 학습 진행에 따라 자동 조정하지 않음 |
| PPO | 모델/입력·Gaussian·36 rollout step·8epoch/4batch·gamma0.98·lam0.95·학습률·optimizer·clip 모두 부모 유지. experiment name만v1 |

## 8. 구현 담당 파일과 상태 계약

다음은 후속 구현 지침이며 이번 작업에서 실행하지 않는다.

1. `envs/sweep_v0_envs.py`에 직접 파생 Cfg를 추가하고 Reaching·Sweep callable 교체와 Joint 비용만 연결한다. mutable 부모 Cfg를 제자리 변경하지 않는다.
2. `mdp/common/sweep_v0_state.py`에 파생 state를 둔다. 부모 binary contact 이력을 재사용하고, 부모 `finish`가 previous distance를 갱신하기 전에 필요한 거리 증분을 확보한다. 기존 `positive`를 새 signed 의미로 몰래 재사용하지 말고 v1 전용 signed 진행 필드를 둔다.
3. `mdp/reward_functions/sweep_contact_preference.py`에서 기존 표면 하중 계산을 상속·재사용하는 v1 callable을 둔다. 실제 `_surface_loads`를 step당 중복 질의하지 않는다. 부모 클래스의 출력은 그대로 유지한다.
4. `mdp/reward_functions/stabilize_sweep.py`에 v1 Reaching·Joint 종료 callable을 추가하거나 기존 역할별 책임에 맞게 연결한다. 공유 기하·step cache는 v1 state에 둔다. 환경 전체 상태를 Reward callable 안에서 재초기화하지 않는다.
5. `runtime/sweep_v0.py`의 직접 파생 runtime에서 `_state_type`과 reset 후 기하·오차 초기화만 추가한다. 부모 물리 step/capture 루프는 복제하거나 교체하지 않는다.
6. `agent/sweep_v0_ppo_cfg.py`의 직접 파생 RunnerCfg와 패키지 `__init__.py`의 새 ID를 연결한다. 원본3개 등록 문자열은 수정하지 않는다.

처음 Manager가 만들어질 때 아직 reset 기하가 없을 수 있으므로 버퍼 생성과 유효 초기화를 구분한다. 부분 reset에서 다른 환경의 이전 오차·접근 방향·반경·진행 이력을 변경하지 않는다. 오류를 숨기기 위해 큰 NaN 값을0으로 치환하는 대신 원인·대상 env를 진단한다.

## 9. 교수님 지시 대조·검증 계획

### 9.1 행동 목적과 의도하지 않은 행동

| 변경 | 의도 | 반드시 함께 볼 부작용 |
| --- | --- | --- |
| 증분 Reaching | 물체를 따라 접근·회복, 정지 중 지급 제거 | 정상 밀기와 증가 비용의 충돌, 할인된 왕복 유인 |
| 반대편 접근점 | 힘 전달에 유리한 쪽으로 접근 | 5cm 허용 범위의 방향 유도 효과와 접근 가능성을 확인 |
| 구역3 +15°점 | 당기기에서 오른쪽·손바닥 접근 기회 확대 | 고정 접근점이 일부 당기기 각도·배치에서 적절한지 확인 |
| signed 방향 | 좁은 좋은 각도와 나쁜 각도를 구분 | 기존 성공도 음수 평가, 구역3 정지·접촉 회피, 근거리 복구 억제 |
| Joint -3 | 속도 위반으로 끝나는 행동 억제 | 접근 자체 위축,1rad/s 바로 아래 속도에 머무를 가능성 |

### 9.2 CPU 수식·상태 검사

- Reaching: 5cm 바로 아래/정확히/바로 위, +1cm/-1cm=+0.049/-0.049, 정지0, 동거리 추종0, 물체만 이동, 접촉 해제 후 재접근, 왕복 telescoping, 첫 step·terminal step·부분 reset·중복 조회.
- 기하: 실제 scaled bounds의 직립 footprint 외접, 구역1/2/4의 반대편 점, 구역3 전체에 동일+15°점, 구역1에 예외가 적용되지 않음, 손 위치 변화로 접근점이 변하지 않음, 중심 일치에서도 유한 거리, 물체 평행이동 동행, 중심 고정·yaw/roll/pitch 회전 시 접근점과 반경 불변, radius reset 갱신.
- 방향: 0/15/30/45/90/180°,[-1,1]·단조성, 수직 힘 추가 시XY 각도 불변, 힘0/1N 경계, 목표 거리0, NaN 방어, 현재/과거 접촉 gate 조합.
- 부호: 좋은 방향·나쁜 방향의 전진, 후퇴, 정지, 각 면/혼합/미분류, 음수에1.5가 적용되지 않음, 후퇴가 양수로 반전하지 않음.
- Joint: 1rad/s 아래/정확히/초과, 복수 관절·복수 실패 동시, 정상 timeout, 최종 정확히-3, dt를 바꿔도 일회 지급액 보존.
- 설정: 부모 작업 전후 전체 동등성, v1과 부모 차이가 요청 표와 일치, 관측·액션·성공 경계·PPO 불변, 활성16개 term·가중치·순서 확인.

### 9.3 후속 실제 실행·학습 검증

후속 개발 때 GPU 소수 환경 reset/step/부분 reset과 실제 RewardManager 적용값·총합을 검증한 뒤 짧은 학습 smoke를 수행한다. 학습 진입점은 `src/inspire_sweep_baseline/scripts/train.py`다. 아직 없는v1 ID로 이번에 실행하지 않는다.

행동 평가는 기존 공통128장면과 별도 seed를 사용한다. v0/v1 각각 성공률·구역별 성공률·밀기 시작률·목표 밖 정지 시간·목표 진입 후 이탈·최종 거리·의도 면 하중과 미분류 비율·힘 각도 분포·1rad/s 종료율·0.8 초과 시간을 비교한다. 새 보상으로 점수를 매긴 기존 성공82개를 새 정책 성공82개로 보고하지 않는다.

보상 기여는 접근/실제 이동접촉/정지/목표 안 구간으로 나누고 원값·weight·dt 적용값·양수·음수·gate를 모두 저장한다. 평균3:7은 초기 산정의 참고값이며 행동 검증의 합격 조건으로 강제하지 않는다. 누적 비율을 학습 영향력 비율로 해석하지 않는다.

실험 원인 분리가 필요하면 부모 → Reaching만 변경 → Joint 비용 추가 → signed 방향 추가의 대조를 우선한다. 최종v1 정의는 본 명세의 전체 변경이며, 대조 실험 때문에 부모 환경을 수정하거나 별도 버전을 임의로 추가하지 않는다. 독립 학습 seed와 실제 성능 비교는 후속 작업이다.

### 9.4 추가 로그 필드

`reach_target_center`, `reach_radius`, `reach_region`, `reach_reference_angle`, `reach_reference_point`, `reach_distance`, `reach_excess`, `reach_previous_excess`, `reach_delta`, `reach_positive/negative/net`, `sweep_angle_xy`, `sweep_direction_coefficient`, `sweep_gate`, `sweep_side_multiplier`, `sweep_positive`, `sweep_direction_negative`, `sweep_retreat`, `joint_failure_event`를 동일 policy 시간축에 저장한다. 초기 EEF world pose·선반 기준 pose도 명시 저장하여 이번 오프라인 자료의 초기 프레임 차이를 재발시키지 않는다.

## 10. 산출물·재현·현재 검증 한계

- [가중치 재계산 요약·해시](../../../../outputs/reward_design/2026-11-21_single_contact_v1_spec/calibration_summary.json)
- [128개 episode별 재계산](../../../../outputs/reward_design/2026-11-21_single_contact_v1_spec/episode_rescores.csv)
- [step별 재계산 NPZ](../../../../outputs/reward_design/2026-11-21_single_contact_v1_spec/rescored_trace.npz)
- [재계산·그래프 스크립트](../../../../outputs/reward_design/2026-11-21_single_contact_v1_spec/calibrate_spec.py)
- [기존 입력 데이터 manifest](../../../../outputs/reward_timeline/model15800_family/dataset_manifest.json)
- [이전 실제 보상 timeline 분석](../../02_implementation/experiments/2026-11-21_single_contact_reward_timeline.md)

workspace root에서 아래 명령은 저장 데이터 재분석만 수행한다.

```powershell
python outputs/reward_design/2026-11-21_single_contact_v1_spec/calibrate_spec.py
```

기존 trace의 현재 물체·EEF·힘·이력·면 하중과 초기 bounds/관측을 사용했다. 초기 EEF는 저장된 비노이즈 goal-in-EEF 및 EEF orientation에서 복원했고 초기 surface 관측 경로와의 대조 오차는 최대1.51e-7m였다. snapshot의 선반 pose와 trace의 이전 분석 기준 프레임을 직접 비교하면 초기 중심 좌표에 최대0.366mm 차이가 있다. 초기 접근 오차는 hand/center를 동일 snapshot 프레임에 놓아 계산했고 이후에는 trace 프레임을 사용했다. 고정 접근 방향의 미세한 프레임 차이 가능성까지 완전히 제거한 정확한 v1 replay라고 주장하지 않는다.

저장 거리 변화로 부모 Sweep을 역산한 step 기여는 원본과 최대0.002794, 목표3cm 밖에서는 최대0.000134 차이가 있었다. 과거 계측의 float32 로컬 거리·근거리 방향 정밀도 및 계산 기준 차이가 포함되며, 이번 계수는 근사 재계산에 기반한 초기 선택이다. 기존 raw 보상/trace는 수정하지 않았다. Reaching의 episode telescoping은 모든128개에서 검사했다. 실제v1 runtime과의 수치 일치는 후속 구현 후 검증해야 한다.

최초 명세 작성 때 수행한 것은 소스 확인·오프라인 재계산·그림 시각 확인·문서 검증이었다. 이후 사용자의 명시적인 구현 요청으로 환경·Gym 등록·CPU/GPU 검사·짧은 PPO smoke를 수행했으며, 최신 범위와 결과는 위 구현 기록을 따른다. 이 문서의 기존 v0 궤적 재계산 수치를 새 v1 정책의 성능으로 해석하지 않는다.
