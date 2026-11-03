# Revision-v1 → Revision-v2 개발 명세

작성일: 2026-11-03. 상태: **v2 / Test-v2 구현 완료, 실행 검증 결과는 [개발 로그](../../02_implementation/logs/2026-11-03_revision_v2_implementation.md) 참조**.

[v1 환경 계약](../../02_implementation/environments/REVISION_V1_ENVIRONMENT.md) · [활성 환경 안내](../../02_implementation/08_ACTIVE_ENVIRONMENTS.md)

## 1. 변경 목적과 요약

Revision-v1을 직접 상속한 v2와, v2를 직접 상속한 Test-v2를 구축한다. 낮은 EEF 자세로 물체를 이동·유지하고, 목표 진입 시 감속하며, 에피소드 종료 시 정확한 목표 배치에 성공하도록 유도한다.

| 대상 | v1 | v2 | 변경 의도 |
| --- | --- | --- | --- |
| `target_goal_distance` | 높이 조건 없음, weight 3.7 | 현재 EEF 높이 < 95mm에서 지급. 곡선·weight 유지 | 낮은 손 자세로 물체를 목표에 접근시키도록 유도 |
| `target_goal_hold` | 3cm 미만 Gaussian 위치 보상·속도 감쇠, weight 8 | 2.5~3.5cm Smoothstep, 속도 감쇠 없음, weight 10. EEF 높이 < 95mm | 중심 정밀도 요구와 경계 불연속을 줄이고 목표 주변 체류 유도 |
| `target_contact` | 실제 접촉 AND EEF 높이 < 120mm, weight 1.45 | 실제 접촉 AND EEF 높이 < 95mm. weight 유지 | 낮은 손 자세에서 발생한 타겟 접촉을 보상 |
| `target_goal_first_entry_bonus` | 최초 진입 +30 | 최초 진입 +25 × 속도 감쇠 계수. 높이 조건 없음 | 빠른 통과보다 감속하며 목표에 진입하는 행동 유도 |
| `target_goal_timeout_bonus` | 성공 timeout +40 | 동일 성공 조건에서 +75 | 에피소드 종료 시 목표 배치 성공의 중요도 강화 |
| `object_acceleration_penalty` | free_acceleration 20m/s², weight −0.05 | free_acceleration 15m/s². weight 유지 | 물체의 급격한 가속·감속에 더 일찍 비용 부과 |

변경 대상은 위 6개 보상 항이다. v1의 나머지 환경·학습 설정은 상속하여 유지한다. 각 변경의 학습 효과는 구현 후 같은 조건의 학습 비교로 평가한다.

## 2. 환경 상속과 Test 구성

| 구성 | v2 | Test-v2 |
| --- | --- | --- |
| Gym ID | `Isaac-Inspire-Revision-v2` | `Isaac-Inspire-Revision-Test-v2` |
| EnvCfg | `RevisionV2EnvCfg(RevisionV1EnvCfg)` | `RevisionV2TestEnvCfg(RevisionV2EnvCfg)` |
| runtime | 기존 `RevisionEnv` | v2와 동일 |
| Scene | 기존 `RevisionSceneCfg` | `RevisionV2TestSceneCfg(RevisionSceneCfg)` |
| Reward CFG | `RevisionV2RewardsCfg(RevisionV1RewardsCfg)` | v2 그대로 상속 |
| Curriculum CFG | 기존 `RevisionV1CurriculumCfg` | v2와 동일 |
| PPO CFG | `RevisionV2PPORunnerCfg(RevisionV1PPORunnerCfg)` | `RevisionV2TestPPORunnerCfg(RevisionV2PPORunnerCfg)` |
| experiment_name | `inspire_revision_v2` | `inspire_revision_test_v2` |

Test-v2는 **타겟 슬롯 하나의 형상만 cylinder로 고정**한다. 타겟 1개와 장애물 후보 9개인 물리 객체 10개 구성, 크기 랜덤화, 장애물 배치·활성 일정은 v2와 같다. 타겟 spawner의 `kind_override = "cylinder"`를 사용하여 scale·장애물 난수열을 보존한다. v2 계열의 임시 높이 출력·시각화 면은 기본 비활성이다.

## 3. 거리·접촉·Hold 보상

### 3.1 EEF 높이 기준

기준점은 offset을 포함한 현재 `ee_frame`의 `end_effector`다. 환경별 초기 선반 작업면에서 EEF까지의 수직 높이를 계산한다.

```text
surface_z = env._revision_initial_shelf_pos[:, 2] + SHELF_SURFACE_HEIGHT
eef_z = env.scene["ee_frame"].data.target_pos_w[:, 0, 2]
h = eef_z - surface_z
```

`SHELF_SURFACE_HEIGHT`는 1.05m다. physics 진행 후·자동 reset 전의 현재 EEF 높이를 사용한다. 각 높이 한계는 strict `<`로 비교하여 정확히 한계에 있거나 높이값이 비유한이면 미지급한다. 높이 하한·과거 높이·물체 윗면 높이 조건은 추가하지 않는다.

| 보상 | 작업면 기준 EEF 높이 한계 | 설정 |
| --- | --- | --- |
| 거리·Hold·접촉 | 0.095m | `goal_reward_height_limit = 0.095`를 공통 기준으로 사용. 기존 접촉 함수의 `contact_height_limit`을 같은 값으로 동기화 |

거리와 Hold는 같은 `goal_reward_height_limit`을 읽고, 접촉 높이도 이 값으로 동기화한다. Hold 전용 높이 설정을 별도로 두지 않는다. v2와 Test-v2에 동일하게 적용하며 높이 커리큘럼은 없다. 높이 조건은 보상 지급 기준이며 제어 목표나 실제 EEF 이동 범위를 강제로 제한하지 않는다.

### 3.2 거리·접촉

- **거리:** 기존 `exp(-d / 0.05)`에 `isfinite(h) AND h < 0.095` 조건만 적용한다. weight 3.7을 유지하며, `d`는 target root와 goal 사이의 XY 거리다.
- **접촉:** 실제 타겟–손 접촉 AND `h < 0.095`를 요구한다. 최신·유한 접촉 force, norm ≥ 0.01N, weight 1.45를 유지한다.

거리 raw는 `torch.where(height_valid, raw_v1, 0.0)`, 접촉 raw는 `float(contact_valid AND height_valid)`다. 높이가 유효해지면 현재 상태로 다시 평가한다.

### 3.3 Smoothstep Hold

보상 이름 `target_goal_hold`는 유지한다. v1의 Gaussian 위치 함수와 타겟 속도 감쇠를 제거하고, weight를 8→10으로 변경한다. 목표 중심에서 2.5cm까지 동일한 최대 위치 보상을 주고 2.5~3.5cm 구간에서 부드럽게 0으로 감소시킨다. 목표 성공 반경은 3cm로 유지한다.

```math
r_{\mathrm{hold},t}=10 V_t H(d_t)\Delta t,
\qquad
V_t=V_{\mathrm{physical},t}\,\mathbf{1}[z_{\mathrm{EEF},t}<z_{\mathrm{limit}}].
```

```math
H(d)=\begin{cases}
1,&d\leq0.025,\\
1-3u^2+2u^3,&0.025<d<0.035,\\
0,&d\geq0.035,
\end{cases}
\qquad u=\frac{d-0.025}{0.01}.
```

| 파라미터 | v2 값 |
| --- | --- |
| Reward weight | 10 |
| `full_reward_radius` | 0.025m |
| `outer_radius` | 0.035m |
| Target success radius | 0.030m |
| Velocity attenuation | 없음 |
| EEF height limit | 초기 작업면 + 0.095m |

`z_limit = surface_z + goal_reward_height_limit`이다. 위치 반경은 유한하고 `0 < full_reward_radius < outer_radius`여야 한다. 성공 반경과 Hold 두 반경을 독립적으로 관리한다. **기존의 `d < 0.03` Hold 마스크를 유지하면 안 된다.** 3~3.5cm에서도 위치 보상이 남지만 timeout 성공은 여전히 `d <= 0.03`으로 판정한다.

`V_physical`은 기존 `target_measurements`의 물리적 유효성 결과를 재사용한다. 위치·속도·goal XY·물체 최저점·정렬값의 유한성, 활성 타겟, 선반 좌표의 `abs(x) <= 0.16`·`abs(y) <= 0.46`, 물체 최저점의 작업면 대비 −0.01~+0.02m, `alignment >= cos(0.9)`를 유지한다. **속도 감쇠 제거 후에도 속도의 유한성 검사는 유지**하며, 유한한 속력의 크기로 Hold 값을 줄이지 않는다. EEF와 작업면 기준의 유한성도 별도로 검사한다.

```text
u = clamp((d - full_reward_radius) / (outer_radius - full_reward_radius), 0, 1)
position_reward = 1 - 3*u*u + 2*u*u*u
hold_valid = physical_valid AND isfinite(h) AND h < goal_reward_height_limit
raw_reward = where(hold_valid, position_reward, 0)
step_reward = 10 * raw_reward * step_dt
```

유효성 실패 시 정확히0을 반환하여 비유한 입력이 보상에 전파되지 않게 한다. 연속 보상의 step 기여는 `weight × raw × step_dt`이며 `step_dt = 0.02s`다.

| 목표 거리 | H(d) | 유효 상태의 step 보상 |
| --- | --- | --- |
| 0~2.5cm | 1 | 0.20 |
| 3.0cm | 0.5 | 0.10 |
| 3.5cm 이상 | 0 | 0 |

2.5cm·3.5cm 연결점에서 값과 1차 미분이 연속이며, 성공 경계3cm에서도 보상 불연속이 없다. 목표 중심의 과도한 정밀도 요구를 완화하고 목표 주변 체류를 유도한다. 속도 감쇠가 없으므로 정지 상태를 직접 구별하여 추가 보상하지는 않는다. 감속 유도는 최초 진입의 속도 감쇠와 기존 속도 패널티가 담당한다. v1의 목표 중심·무감쇠 최대 rate16 대비 v2 최대 rate는10이므로, weight 상승을 모든 거리에서의 보상 증가로 해석하지 않는다.

## 4. 최초 목표 진입 보너스

목표 영역을 빠르게 통과하는 진입보다 감속한 진입에 더 큰 보상을 주기 위해, v1의 고정 +30을 **최대 +25 및 진입 속도 감쇠**로 변경한다. 최초로 유한 XY 거리 `d < 0.03`m가 관측된 step에서, 타겟의 현재 world-frame 3D 선속도 norm `v`를 사용한다. EEF 높이는 지급 조건에 포함하지 않는다.

```math
g(v)=\exp\left[-\left(\frac{\max(0,v-v_{\mathrm{free}})}{v_{\mathrm{scale}}}\right)^2\right].
```

설정할 기본 후보값은 `free_speed = 0.01`m/s, `speed_scale = 0.02`m/s다. 별도 커리큘럼 없이 적용한다. 지수에 `ln(2)`를 넣지 않으므로 free + scale에서 감쇠 계수는 `exp(-1)`이다.

```text
inside = isfinite(d) AND d < 0.03
first_entry = inside AND NOT entered
entry_value = where(first_entry AND isfinite(v), g(v), 0)
entered = entered OR inside
raw_reward = entry_value / step_dt
weight = 25
```

최초 진입 순간 지급액을 확정하고 **지급액과 관계없이 기회를 소진**한다. 목표 내부에서 감속하거나 밖으로 나갔다가 재진입해도 추가 지급하지 않는다. 속도가 비유한이면 0을 지급하고 기회를 소진한다. `free_speed`는 유한·0 이상, `speed_scale`은 유한·0 초과여야 한다.

| 최초 진입 속력 | 실제 지급액, 근삿값 |
| --- | --- |
| 0~0.01m/s | +25 |
| 0.02m/s | +19.4700 |
| 0.03m/s | +9.1970 |
| 0.04m/s | +2.6350 |
| 0.05m/s | +0.4579 |
| 0.07m/s | +0.0031 |

상태는 v2 전용 reward term이 소유한다. 같은 step의 재호출에는 감쇠까지 반영한 캐시를 반환하고, 부분 reset은 해당 env의 상태만 초기화한다. v1의 최초 내부 표본 판정·실패 step 평가 동작은 유지한다.

## 5. Timeout·가속도 변경

**Timeout:** 최종 목표 배치의 중요도를 높이기 위해 weight를 40→75로 변경한다. 기존 `successful_timeout_bonus`와 성공 판정인 timeout AND 유한 XY 거리 `d <= 0.03`m를 유지한다. 높이·속도·진입 이력 조건을 추가하지 않는다. raw는 success_event/step_dt이므로 실제 지급액은 +75다. 최초 진입과 동시에 발생하면 두 이벤트 합계는 `75 + 25*g(v)`, 최대 +100이다.

**가속도:** 급격한 물체 운동에 더 일찍 비용을 부과하기 위해 `object_acceleration_penalty.params["free_acceleration"]`을 20→15m/s²로 변경한다. weight −0.05, 물체별 max_cost 100, 활성 물체별 비용 합산, reset/활성화 첫 표본 억제·캐시는 유지한다. 입력은 PhysX의 마지막 physics step `object_com_lin_acc_w`의 3D norm이다. 15m/s²까지 비용 0이며 초과분에는 기존 지수 비용을 적용한다. 높이와 무관하게 적용하고 처음부터 15로 고정한다.

## 6. 보존 범위와 구현 위치

v1과 Test-v1은 보존한다. v2는 변경 표의 6개 항 외에 보상 term 수·순서, 관측·행동·OSC, 자산·reset·종료 조건, 물리·제어 dt, 커리큘럼과 PPO 파라미터를 유지한다. PPO는 gamma 0.98·GAE lam 0.95를 포함한 기존 학습 설정을 유지하고 experiment_name만 환경별로 분리한다.

특히 `target_speed_penalty`의 기본 free_speed 0.1m/s와 `target_free_speed` 커리큘럼 points `((0, 0.1), (499, 0.1), (500, 0.09), (1900, 0.02))`, interval 250, 기존 보간·갱신 규칙을 유지한다. 최초 진입과 속도 패널티의 속도 파라미터는 서로 독립적이며, Hold에는 속도 감쇠 파라미터를 전달하지 않는다.

| 기존 파일 | 구현 내용 |
| --- | --- |
| `inspire_sweep_baseline/__init__.py` | v2/Test-v2 등록 |
| `envs/revision_envs.py` | 직접 상속 CFG, 거리·Hold·접촉의 공통95mm 설정 및 접촉 높이 동기화 |
| `assets/scenes/revision.py` | Test-v2의 타겟 cylinder override |
| `mdp/rewards/revision.py` | 거리·Hold·최초 진입·timeout·가속도 설정 override |
| `mdp/reward_functions/revision.py` | 거리 높이 wrapper, Smoothstep Hold 함수, 속도 감쇠 최초 진입 term |
| `agent/revision_ppo_cfg.py` | v2/Test-v2 experiment_name |
| `tests/` | 변경 조건과 부모 동작 보존 검사 |

접촉 함수는 기존 callable을 재사용하고 EnvCfg의 높이 설정으로 변경한다. 현재 디렉터리 구조를 유지하며 부모 함수·설정에 변경이 전파되지 않도록 한다. 최종 post-init 결과에서 설정값과 reward 평가 순서를 확인한다. v1의 post-init이 Hold params를 Gaussian용으로 다시 설정하므로, v2는 부모 초기화 후 Smoothstep용 params를 최종 적용한다. 기존 goal_hold_v1과 부모 설정은 수정하지 않는다.

## 7. 검증·완료 기준

- **높이:** 거리·Hold·접촉 모두94.9/95.0/95.1mm 및 비유한 높이·환경별 원점 차이를 검사한다. 정확히95mm와 그 이상에서는 세 보상 모두0이어야 한다. h94.9mm에서는 각 항의 기존 물리·접촉·거리 조건에 따라 지급하며, 최종 높이 설정이 모두0.095인지 확인한다. 접촉 유/무·stale·비유한 force도 조합한다.
- **Hold:** 2.5/3.0/3.5cm와 각 경계 직전·직후에서 H=1/0.5/0, 연결점의 값·1차 미분 연속성, 3~3.5cm의 양수 지급을 확인한다. 동일 위치·물리 유효성에서 유한 속력만 바꾸면 보상은 같아야 하고, 비유한 속도·기존 물리 유효성 실패는0이어야 한다.
- **목표 경계:** 최초 진입은 strict `d < 3cm`, timeout은 inclusive `d <= 3cm`를 유지한다. Hold 반경 변경이 두 이벤트에 전파되지 않게 한다.
- **최초 진입:** 속도 감쇠 표, free 경계, free + scale에서 exp(-1), 높이 독립성, 재진입 미지급, 비유한 속도, 동일 step 재조회, 전체/부분 reset을 확인한다.
- **실지급액:** RewardManager dt 합산 후 Hold 최대0.20·3cm에서0.10, 최초 진입 `25*g(v)`, timeout +75, 동시 이벤트 최대 +100을 확인한다.
- **가속도:** 15m/s² 경계·cap·활성 물체 합산·첫 표본 억제와 높이 독립성을 검사한다.
- **부모 보존:** v1/Test-v1의 설정·동작, v2의 나머지 보상·커리큘럼·관측·행동·PPO가 유지되는지 대조한다. 같은 seed에서 Test-v2의 타겟 형상만 달라지고 scale·장애물 난수열은 보존되어야 한다.
- **실제 실행:** v2/Test-v2의 64 env 초기화·rollout·부분 reset, v2의 2048 env 실행, 실제 EEF·접촉 센서를 이용한 높이 경계 검증을 수행한다. `scripts/train.py`로 짧은 PPO·checkpoint 저장을 검증하고 기존 학습 로그를 보존한다.

구현 로그에는 실제 검사 명령·결과와 미검증 범위를 남긴다. 장기 성능은 최종 XY 오차·timeout 성공률·최초 진입 속력·평균 지급액으로 비교한다. 실제 수행한 검증과 미검증 범위는 개발 로그에 별도로 기록한다.
