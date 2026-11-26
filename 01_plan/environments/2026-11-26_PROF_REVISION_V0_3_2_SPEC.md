# Prof Revision v0_3_2 개발명세: 거리 기반 힘 정렬 완화와 정밀 도달

작성일: 2026-11-26 KST. 상태: **새 환경 구현·등록 완료**, 검증 상세는 [구현 기록](../../02_implementation/logs/2026-11-26_prof_revision_v0_3_2_implementation.md)을 따른다. 사용자 확정: **v0_3_1을 상속하는 새 환경**, **성공 반경3cm 유지**. 제안 이름 `Inspire-Sweep-Prof-Revision-v0_3_2`를 구현 ID로 적용했다. 아래 수치·수식은 초기 실험 설정이며 장기 학습 성능이 검증된 설정은 아니다.

같은 날 후속 지시 반영: Reach×2, Formation×0.7, 이탈은 기존−20의2배인**−40**으로 변경한다. 장애물 변위는 원시 Play에서 cap 도달0회를 확인하여 **weight−300·raw cap0.04 유지**로 결정했다. 아래가 최신 명세이며 이전+100/−100 대칭안은 대체됐다.

[부모 환경](../../02_implementation/environments/PROF_REVISION_V0.md#prof-revision-v0_3_1) · [Play 근거](../../02_implementation/experiments/2026-11-26_prof_revision_v0_3_1_play_analysis.md) · [힘/이동 방향 비교](../../02_implementation/experiments/2026-11-26_prof_revision_motion_alignment.md) · [명세 작성 기록](../../02_implementation/logs/2026-11-26_prof_revision_precision_spec.md)

## 1. 목적과 근거의 구분

사용자가 제안한 거리 기반 전환과 후속 보상 배분 변경을 구현한다.

1. 목표가 가까워지면 힘 방향의 중요도를 낮춰, 목표 방향과 반대인 제동력이 양의 거리 개선 보상을 차단하지 않게 한다.
2. 목표가 가까워지면 같은 거리 개선에 더 많은 보상을 부여해, 성공 반경 안에서도 중심으로 정밀하게 접근하도록 유도한다.
3. 목표에서 멀어지는 거리 증가의 기본 비용 계수를 기존20의2배인40으로 올린다. 근거리 가중 거리H는 양쪽에 동일하게 적용하되, 기본 계수는+100/−40으로 비대칭이다.
4. Reach weight를4.9→9.8, Formation weight를0.245→0.1715로 조정한다. 각 함수·입력·거리/각도 식은 유지한다.
5. 장애물 변위 비용의 cap 작동 여부를 확인하고 사용자 조건에 따라 계수−150→−300으로 조정한다. 조사 근거는8.1절에 기록한다.

실제 Play에서491/512건이 목표에 진입했지만157건이 최종 실패했고, 현재 Sweep100/이탈−20의 비대칭은 코드로 확인했다. 그러나 **힘 방향 때문에 감속을 배우지 못했다는 설명은 설계 가설**이다. 방향만 교체한 이전 재평가의 Sweep 증가는3.0%였으므로 주원인이 확정됐다고 기록하지 않는다. 본 명세는 근거리 보상 구조의 변경 효과를 새 학습으로 검증하는 계획이다.

## 2. 환경 계약과 수정 범위

| 항목 | 계약 |
| --- | --- |
| 부모 | `ProfRevisionV0_3_1EnvCfg` 직접 상속 |
| 새 Gym ID / EnvCfg | `Inspire-Sweep-Prof-Revision-v0_3_2` / `ProfRevisionV0_3_2EnvCfg` |
| Runtime | `ProfRevisionV0_3_2Env(ProfRevisionEnv)`; 거리 보상 상태 생성·추가 telemetry만 확장 |
| Rewards | `ProfRevisionV0_3_2RewardsCfg(ProfRevisionV0_3RewardsCfg)`; 부모v0_3_1이 이 Rewards를 상속해 사용함 |
| PPO | `ProfRevisionV0_3_2PPORunnerCfg(ProfRevisionV0_3_1PPORunnerCfg)`; 로그 이름만 새 ID에 대응 |
| 로그 이름 | `inspire_sweep_prof_revision_v0_3_2` |
| 변경 term | `sweep_progress`, `sweep_retreat` 계산 및 이탈 weight; `reaching`, `contact_formation`, `obstacle_displacement` weight |
| 성공 | 현재 추적 OBB 중심과 목표의 XY 거리 `d <= 0.03m`, 기존10초 timeout 판정·실패 우선순위 유지 |
| 관측·행동 | 부모의 Actor/Critic term 순서·차원·noise·scale·action·clip·제어 주기 유지 |
| 기타 | Formation 거리×각도 합산식·Reach 함수·장애물 변위 함수와cap 유지; 위5개 term 외 모든 비용·자산·배치·reset·PPO 유지 |

현재 OBB 중심은 보상·평가에 사용한다. Actor에 현재 물체 위치·속도·남은 거리를 새 관측으로 추가하지 않는다. 성공 반경3cm와 보상 전환 반경은 서로 다른 설정값이며 자동으로 결합하지 않는다. ‘3cm 성공 인정’이 ‘3cm에서 진행 보상 중지’를 뜻하지 않는다.

손가락 보상식 재설계, Joint 종료 재도입, 새 속도 비용·정착 시간 보상·terminal bonus는 이번 구현 범위에 포함하지 않는다. 첫 실험은 거리 가중·이탈 강화와 세 term의 weight 조정을 평가한다.

## 3. 초기 계수

| 설정명 | 초기값 | 의미 |
| --- | ---: | --- |
| `sweep_force_fade_inner_m` | 0.03m | 이 거리 이하에서 힘 방향 영향0 |
| `sweep_force_fade_outer_m` | 0.06m | 이 거리 이상에서 기존 힘 정렬 전부 적용 |
| `sweep_precision_radius_m` | 0.06m | 이 거리 안에서 거리 개선·이탈의 중요도 증가 |
| `sweep_precision_max_multiplier` | 2.0 | 목표 중심에서 거리 민감도의 최대 배수 |
| `sweep_progress.weight` | +100 | 기존값 유지 |
| `sweep_retreat.weight` | −40 | 현재 환경의−20에서 크기2배; 이전 제안−100을 대체 |
| `reaching.weight` | +9.8 | 현재+4.9의2배; signed Reach의 양·음 모두2배 |
| `contact_formation.weight` | +0.1715 | 현재+0.245의0.7배; raw 식 유지 |
| `obstacle_displacement.weight` | −300 | 현재−150의2배; cap 미도달에 따른 사용자 조건 적용 |
| `obstacle_displacement.params.displacement_max_cost` | 0.04m² | 활성 장애물3D 제곱변위 합의 raw 상한 유지 |

반경은 m, Sweep/이탈의 기본 weight는 보상/m이며 가중된 거리 역시 m 단위를 갖는다. 다른 term은 각 기존 raw rate에 weight·dt를 적용한다. 모든 반경·배수는 finite, `0 <= inner < outer`, `precision_radius > 0`, `max_multiplier >= 1`을 초기화 시 검증한다. GPU step 안에서 CPU 검증·동기화를 반복하지 않는다.

## 4. 공통 정의

`p_t`는 현재 추적 가시 OBB 중심, `g`는 목표, `d_t=||g_xy−p_t,xy||`이다. 물체 root/COM과 바꾸지 않는다. `d_(t−1)`은 reset 또는 직전 policy step의 동일 점 기준 거리다. policy dt는 기존0.02초이고, 마지막 physics substep의 상태 갱신을 사용한다.

`C_t`는 **최근3step 중2step 접촉 인정 AND 현재 실제 접촉 AND 센서 유효성**이다. 기존 먼 거리 보상의 실질적인 접촉 조건을 보존한다. 양의 보상에만 적용한다. 접촉이 끊긴 동안의 목표 이탈도 비용을 받는다.

`A_t`는 기존 `state.alignment`다. 수평 목표 단위 방향 `u_t`에 대해 `clip((F_xy·u_t)/||F_3D||,0,1)`이며, 현재 접촉·센서 유효성·수평 힘≥1N·목표 방향 정의 가능 조건을 만족하지 못하면0이다. 평균힘의 물리 substep 집계·3D 정규화·임계값은 바꾸지 않는다.

## 5. 남은 거리에 따른 힘 방향 영향

포화 smoothstep `S(x)`를 정의한다. 아래 `x`는 먼저[0,1]로 clip한다.

```math
S(x)=3x^2-2x^3,\qquad
\alpha(d)=S\left(\mathrm{clip}\left(\frac{d-r_{\mathrm{inner}}}{r_{\mathrm{outer}}-r_{\mathrm{inner}}},0,1\right)\right)
```

양의 진행 보상에 곱하는 힘 계수는 다음과 같다.

```math
B_t=(1-\alpha(d_t))+\alpha(d_t)A_t
```

- `d >= 6cm`: `B=A`, 기존 힘 조건을 그대로 적용한다.
- `3cm < d < 6cm`: 힘 방향의 영향을 연속적으로 낮춘다.
- `d <= 3cm`: `B=1`, 힘 방향과 힘≥1N 조건이 진행 보상을 차단하지 않는다. 별도의 `C_t`는 유지한다.
- 목표에서 멀어지는 실제 이동은 `B`와 무관하게 이탈 비용을 받는다. ‘반대 힘’과 ‘목표에서 멀어지는 이동’을 구분한다.

`alpha`는 현재 거리 기준으로 계산한다. timestep마다 별도 phase 전환·타이머·hysteresis 없이 현재 거리로 결정한다.0과1 경계에서 값과1차 미분이 연속이다.

## 6. 목표 중심까지 강화되는 거리 민감도

남은 거리의 국소 중요도 `w(d)`를 다음과 같이 둔다. `R=0.06m`, `m=2`다.

```math
w(d)=1+(m-1)\left[1-S\left(\mathrm{clip}(d/R,0,1)\right)\right]
```

`d>=6cm`이면1,3cm에서1.5,목표 중심에서2다. 성공 반경 안에서도 중심에 가까워질수록 더 커진다.

| 남은 거리 | 힘 방향 비중 `alpha` | 거리 민감도 `w` | 반대/무효 힘일 때 양의 보상 계수 `B` |
| --- | ---: | ---: | ---: |
| 6cm 이상 | 1.000 | 1.000 | 0.000 |
| 4.5cm | 0.500 | 1.156 | 0.500 |
| 3cm | 0.000 | 1.500 | 1.000 |
| 1.5cm | 0.000 | 1.844 | 1.000 |
| 0cm | 0.000 | 2.000 | 1.000. 단, 정지하면 진행량0 |

![제안한 거리별 힘 방향·정밀도 계수](../../../../outputs/prof_revision_precision_spec_20261126/proposed_weights.png)

현재 거리 계수를 단순히 `w(d_t)*(d_(t−1)−d_t)`로 곱하지 않는다. 경계를 왕복할 때 출발·도착 방향에 따라 다른 계수가 적용될 수 있기 때문이다. **`w`의 적분으로 정의한 동일한 가중 거리 `H`의 차이**를 양·음 양쪽에 사용한다.

```math
u=\mathrm{clip}(d/R,0,1),\qquad
H(d)=d+(m-1)R\left(u-u^3+\frac{u^4}{2}\right)
```

`H(0)=0`, `H'(d)=w(d)>0`이다. `d>=R`이면 `H(d)=d+(m−1)R/2`이므로, 그 구간에서의 거리 차이는 원래 거리 차이와 같다. 기본안의 이상적인 원거리→중심 단조 접근은 기본 거리 보상 외에 최대3.0의 추가 정밀 보상을 받는다(100×0.03). 이는 강제 누적 cap이 아니라 한 번의 단조 접근에 대한 적분량이다.

## 7. 최종 보상식과 이탈 강화

```math
\Delta H_t=H(d_{t-1})-H(d_t)
```

```math
r_{\mathrm{progress},t}=100\max(\Delta H_t,0)C_t B_t,
\qquad
r_{\mathrm{retreat},t}=-40\max(-\Delta H_t,0)
```

위 식은 RewardManager dt까지 반영한 실제 step 기여다. Manager callable은 각각 `max(ΔH,0)*C*B / step_dt`, `max(−ΔH,0) / step_dt`를 반환하고 weight는+100/−40으로 둔다. dt를 두 번 곱하거나 episode 길이로 나누지 않는다.

동일한 가중 거리 구간에서 **역방향 비용은 정방향 최대 보상의40%**다. 정방향은 접촉·힘 계수로 추가 감쇠된다. 역방향 비용에는 힘·접촉 gate를 곱하지 않는다. '현재의2배'는 기본 계수−20→−40을 뜻하며, 유지한 근거리H 가중까지 포함하면 실제 누적 비용이 기존의 정확히2배가 되는 것은 아니다. 동일 저장 궤적에서 평균−0.375→−1.253(약3.34배)이었다.

정지·목표 중심 정지는 양·음 모두0이다. 목표를 통과하여 이전보다 더 멀어지면 비용이 발생한다. 한20ms 구간에서 목표를 지나쳤지만 끝점 거리는 더 짧다면 순개선으로 평가한다. substep 경로 길이·최대 이탈을 새로 평가하는 설계가 아니다.

가중 거리 차이는 분할합이 일치하지만, **이전 대칭안의 '닫힌 왕복 합≤0' 보장은 최신안에서 성립하지 않는다.** 예를 들어 양쪽 가중 거리 변화가0.01m이고접촉·힘 계수가1이면 전진+1.0,이탈−0.4로 왕복 합+0.6이다. 이는 최신 사용자 지시의+100/−40 비율에 따른 결과다. 왕복·진동 및 기존gamma0.98의 할인 수익은 실제 학습에서 평가한다. 정책 불변성을 보장하는 보조 보상으로 주장하지 않는다.

## 8. 저장된 checkpoint 궤적의 사전 예산 대조 — 실행 완료

`v0_3_1/model_15550`의 seed42·43,512완료episode·254,165step을 같은 궤적으로 재평가했다. 기존 첫step은 최근2/3접촉 조건이 거짓이므로 양의 보상0이다. 첫step 이탈은 저장된 raw retreat로 reset 이전 거리를 재구성하여 포함했다. 새 Play·학습이 아니며 성공률 개선 결과로 해석하지 않는다.

| episode 평균 | 기존 | 명세 기본안 |
| --- | ---: | ---: |
| Sweep | +6.734 | +9.703 |
| 이탈 비용 | −0.375 | −1.253 |
| Reach | +1.175 | +2.350 |
| Formation | +6.853 | +4.797 |
| 장애물 변위 비용 | −0.139 | −0.278 |
| 전체 순보상 | +12.477 | +13.549 |
| 성공334건 순보상 | +13.469 | +14.983 |
| 실패178건 순보상 | +10.616 | +10.859 |
| 진입 후 실패157건 순보상 | +11.801 | +12.215 |

최신안의 양의 기여 합은16.993,음의 기여 절댓값 합은3.443이다. 양의 예산은Sweep57.1%·Reach14.7%·Formation28.2%,음의 예산 중 이탈36.4%·장애물 변위8.1%다. Reach는양·음 양쪽에 기여하므로 net 비율과 다르다. 이전 대칭안과 달리 **실패 궤적의 평균 보상도 기존보다 증가**한다. 이를 실패 감소·성공률 향상으로 해석하지 않는다.

[최신 재평가·cap 조사](../../../../outputs/prof_revision_precision_spec_20261126/revision2/summary.json) · [episode별 값](../../../../outputs/prof_revision_precision_spec_20261126/revision2/episodes.csv) · [16개 term·비중](../../../../outputs/prof_revision_precision_spec_20261126/revision2/rewards.csv) · [재현 스크립트](../../../../outputs/prof_revision_precision_spec_20261126/revision2/check_weights.py). 이전+100/−100·다른weight 유지 조건의 [초기 민감도 조사](../../../../outputs/prof_revision_precision_spec_20261126/summary.json)는 이력으로 보존하며 최신 결과가 아니다. 근거리 최대 배수2는 유지한다.

### 8.1 장애물 변위 cap 조사와 변경 결정

현재 비용은 타겟을 제외한 활성 장애물의 **reset 위치 대비3D 제곱변위 합**을0.04m²로 자른 뒤,−150과dt0.02를 곱한다.0.04는4cm나 최종 reward 상한0.04가 아니다. 단일 장애물만 움직인다면20cm 변위에서 해당 raw 상한에 도달한다.

```math
q_t=\sum_{i\in\mathrm{active\ obstacles}}\|\mathbf{p}_{i,t}-\mathbf{p}_{i,0}\|^2,\qquad
r_{\mathrm{obstacle},t}=-150\min(q_t,0.04)\Delta t
```

| 원시 Play 조사 | seed42 | seed43 |
| --- | ---: | ---: |
| 유효step | 126,623 | 127,542 |
| cap 도달step/episode | 0 / 0 | 0 / 0 |
| 최대q, m² | 0.00839835 | 0.00620487 |
| 최대값 / cap | 21.0% | 15.5% |
| cap 때문에 잘린 누적 비용 | 0 | 0 |

최대 단일 장애물 변위는91.64mm였다. 개별 순간 이동이 커진 경우도 있지만,전체 평균−0.139는cap에 막힌 값이 아니라 이 궤적들의 실제 제곱변위·지속시간·장애물이 없는episode까지 포함한 평균이다. 예를 들어 장애물1개가1cm 이동한 상태를10초 유지할 때 기존 비용은−0.15다. 작거나 짧은 이동은 이 제곱변위×시간 구조에서 작게 계산된다.

원시 위치로 계산한 비용과 저장된 term의 최대step 오차는7.13e−9이고 값은 finite다. 관측한254,165step에서 상한 손실0이므로 사용자 조건 중 **'실제로 그 정도 발생한 경우'를 적용**한다. 새 weight−300,raw cap0.04 유지. 최신식은 `−300*min(q,0.04)*dt`이며 모든 동일 궤적에서 이 항은정확히2배다. raw cap10배(0.4)안은 적용하지 않는다. weight2배로최종step 비용 상한은0.12→0.24가 된다. 새 학습에서의 cap 도달 빈도는 별도로 기록한다.

## 9. 구현 위치와 상태 수명

현재 패키지의 역할별 파일을 유지한다. 아래 계획을 구현했으며, 검증·최종 대조는 [구현 기록](../../02_implementation/logs/2026-11-26_prof_revision_v0_3_2_implementation.md)에 남긴다.

| 파일 | 변경 계획 |
| --- | --- |
| `envs/prof_revision_envs.py` | 새 EnvCfg를v0_3_1에서 상속, 위4개 거리/배수 설정 및 새 Rewards 지정 |
| `mdp/common/prof_revision_state.py` | GPU 벡터화 순수 `alpha/w/H` helper와 `ProfRevisionPrecisionState(ProfRevisionState)` 추가 |
| `mdp/reward_functions/prof_revision.py` | 새 상태의 정밀 진행/이탈 rate를 읽는 두 함수 추가 |
| `mdp/rewards/prof_revision.py` | Sweep/이탈 두 callable 교체·이탈weight−40; Reach9.8·Formation0.1715·장애물변위−300; raw cap0.04 유지 |
| `runtime/prof_revision.py` | 기본 상태 생성 factory를 추출하고 새 runtime에서만 precision state 생성; 추가 telemetry hook은 부모 기본값 빈 사전 |
| `agent/prof_revision_ppo_cfg.py` | 부모 runner 상속, 로그 이름만 분리 |
| `__init__.py` | 새 ID의 runtime·EnvCfg·runner 등록 |

상태 생성 factory는 `(count, device, cfg)`를 받고 기존 runtime에서는 기존 `_state_type(count, device)`와 동일한 동작을 한다. 파생 runtime만 계수를 전달한 새 상태를 생성한다. 기존 생성자에서 cfg가 아직 `self.cfg`로 저장되기 전일 수 있으므로 전달 인자를 사용한다.

새 상태의 `finish`는 부모 `previous_distance`가 갱신되기 전에 이전 거리를 보존하고 부모 계산 후 `ΔH`, `alpha`, `B`, 정밀 진행·이탈을 계산한다. 원본 `positive`, `retreat`, `alignment`, Reach buffer는 의미를 바꾸지 않고 유지한다. 새 term은 별도 `precision_positive`, `precision_retreat`를 사용한다. 기존 `_m` 로그에 가중 거리를 몰래 덮어쓰지 않는다.

reset은 선택된 env_ids의 이전 거리·부모 접촉 이력·정밀 cache를 함께 초기화한다. 다른 환경의 상태는 건드리지 않는다. 기존과 동일하게 마지막 physics substep 후, 종료·reward·자동 reset 전 한 번만 계산한다. 두 reward callable은 같은 cache를 읽고 상태를 갱신하지 않아 term 호출 순서에 독립적이어야 한다.

새 계수·원본/정밀 progress·retreat·거리 구간·힘의 감쇠 계수를 terminal reset 전에 기록한다. 기존 `force_alignment`는 원본 `A`의 의미를 유지하며 `effective_alignment=B`를 별도 기록한다. step 경로에서 새 센서 생성·mesh query·CPU 복사·환경별 Python loop는 추가하지 않는다.

## 10. 검증과 학습 비교 계획

### 10.1 구현 계약 검증

- 새 환경의 전체 Manager·Scene·관측·액션·PPO를 부모와 비교한다. 허용 차이는 위5개 reward term의 명시된 callable/weight,4개 거리/배수 scalar 설정,상태/runtime 클래스,등록·로그 이름이다. 성공 반경·종료·Formation/Reach/장애물 변위 함수·장애물cap·나머지 비용은 동일해야 한다.
- 기존v0_3_1/v0_3/Hard/v1의 함수 결과·설정·등록이 바뀌지 않았음을 검사한다. 특히 공통 runtime factory 확장 전후 부모 결과를 대조한다.
- 0/3/6cm와 양옆의 경계, 완전 정지, 힘 정렬1/0/반대, 낮은 힘, 접촉 없음·invalid, 목표 통과, 목표 복귀, 부분 reset을 검사한다.
- +100/−40 부호·배율, 분할 불변성, `H` 미분/수치적분, 유한값과 왕복 예제+0.6을 검증한다. 왕복 합≤0을 요구하는 이전 검사는 폐기한다. Reach 양·음×2, Formation×0.7, 장애물변위×2·cap0.04 계약도 검증한다. 원시cap 조사는 명세 단계에서 실행했다.
- 실제 환경4–64개 headless에서 첫step·부분 reset·terminal step·보상 dt·원본 buffer·파생 cache를 확인한다.16환경 PPO1회 업데이트로 loss와 reward finite 여부를 검사한다. 이것을 장기 성능 증거로 간주하지 않는다.

### 10.2 효과 분리

1. 부모 원본.
2. 힘 전환만 적용.
3. 힘 전환 + 이탈−40, 정밀 배수1.
4. 힘 전환 + 이탈−40 + 정밀 배수2.
5. 최신 최종안:4번에 Reach×2·Formation×0.7·장애물 변위×2 추가.

각 비교는 별도 학습 로그·config snapshot으로 구분한다. 대조를 위해 여러 영구 Gym ID를 자동 생성할 필요는 없으며, 평가용 설정 override는 명시적으로 기록한다. 학습 실행기는 `src/inspire_sweep_baseline/scripts/train.py`를 사용한다. 명세 단계에서는 학습을 실행하지 않는다.

부모 checkpoint로 동일 행동 보상 대조는 가능하다. 보상이 바뀐 학습 재개에서는 기존 critic이 새 수익을 이미 학습했다고 가정하지 않는다. 새 학습을 기본 비교로 두고, actor warm start 실험을 하면 critic·optimizer 초기화/보존 정책과 실제 loader 지원 여부를 먼저 확인하여 별도 기록한다. 부모 PPO gamma 등은 이번 실험에서 변경하지 않는다.

### 10.3 행동 평가와 채택 기준

최소 동일한2개 평가 seed×64환경×4완료episode로 방향별 성공률·신뢰구간을 비교한다. 가능하면 학습 seed3개 이상을 추가하여 한 checkpoint 우연과 학습 효과를 구분한다.

- 주 지표: 목표 진입 후 최종 실패율(기준157/491), 최종 거리 중앙값/P90, 10/20/30mm 도달·최종 유지 비율.
- 감속: 최초 진입 전 남은 거리별 OBB 중심 이동 속도, 목표 도달 속도, 목표 통과 횟수, 최초 진입 후 최대 이탈, 반대 힘이 작용하는 양의 거리 개선 구간.
- 부작용: 최초 도달률·도달 시간, 접촉 유지, 장애물 최대 변위/1cm 이상 비율, 낙하·기울기·TCP 실패, 왕복 경로 길이/할인 수익.
- 보상: 방향별·구간별 정밀 진행/이탈/Formation 비중, 성공/실패 return 분포, `alpha/A/B`의 실제 적용 확인.

채택은 단순히 새 총보상이 높다는 이유로 결정하지 않는다. 진입 후 실패와 최종 거리 오차가 개선되고, 기존 최초 도달·접촉·장애물 지표가 악화되지 않는지를 같은 조건에서 확인한다. 표본 오차로 불명확하면 추가 평가하고 개선으로 단정하지 않는다.

## 11. 남는 한계와 완료 상태

이 명세는 가까워지는 작은 이동을 더 가치 있게 만들고 가까운 곳의 이탈도 강하게 부과한다. **정지 자체에 양의 보상을 주거나 낮은 종단 속도를 직접 요구하지는 않는다.** 따라서 이를 구현하면 반드시 제동·정착을 학습한다는 보장은 없다. 실제 학습에서도 재이탈이 남으면 다음 별도 실험으로 목표 근처 속도·정착 시간 보상을 검토한다.

Formation weight는낮추지만 지속 지급 구조와 미해결 힘 센서 충실도 문제는 남는다.3cm 밖에서는 여전히 기존 힘 방향에 의존한다. 최신+100/−40 비율에서는왕복 이익이 남을 수 있다. 이번 명세는 사용자 지정 새 환경·성공 반경·거리 가중·후속 보상 비율을 구체화했다.

명세 단계 완료: 실제 코드·상속·dt 확인,512episode 최신weight 재평가,원시 장애물cap 검사,수학 경계·수치적분·계수 그림. 초기 대칭안의1,000개 닫힌 경로 검산은이력이며 최신비율의 보장이 아니다. 후속 구현 요청으로v0_3_2를 구현·등록했다. CPU·실제 GPU 실행·PPO 단기 검증은 [구현 기록](../../02_implementation/logs/2026-11-26_prof_revision_v0_3_2_implementation.md)을 기준으로 한다. 장기 학습·실제 행동 성능 대조는 미완료다.
