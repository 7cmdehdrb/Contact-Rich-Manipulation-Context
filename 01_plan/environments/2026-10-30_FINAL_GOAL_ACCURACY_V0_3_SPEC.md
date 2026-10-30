# Final GoalAccuracy v0_3 개발 명세

[현재 인계](../00_HANDOFF_BRIEF.md) · [부모 계열 계약](../../02_implementation/environments/FINAL_GOAL_ACCURACY_V0_1_ENVIRONMENT.md) · [작성·검증 기록](../../02_implementation/logs/2026-10-30_final_goal_accuracy_v0_3_spec.md)

2026-10-30 작성 후 사용자 수락. 같은 날 이 명세대로 구현했다. [구현 계약과 검증 범위](../../02_implementation/environments/FINAL_GOAL_ACCURACY_V0_3_ENVIRONMENT.md)를 따른다. 아래 설계·수치는 수락된 계약으로 보존하며 학습 성능 개선을 입증한 문서는 아니다.

## 1. 기준 환경과 변경 계약

직접 부모는 현재 코드의 `FinalGoalAccuracyV0_2EnvCfg`로 정한다. v0_2는 v0_1을 상속하고 timeout 보너스를 추가한 환경이다. v0·v0_1·v0_2·v1의 기존 동작을 보존한다.

| 항목 | 현재 v0_2 | v0_3 |
| --- | --- | --- |
| `target_contact` | 타겟–손 접촉 OR 유효한 목표 점유, weight 1.45 | 조건 유지, weight **0.3625** |
| `target_goal_distance` | `exp(-d/0.05)`, weight 3.7 | `DexPlanarGoalProgress`, `position_tolerance=0.0`, weight **100.0** |
| `target_goal_timeout_bonus` | 성공 timeout 중 `d < 0.02`이면 +30 | 성공 timeout인 `d <= 0.03`이면 **+100** |
| 목표 인정 반경 | 0.02m | **0.03m 고정**, 경계 포함 |
| `target_goal_hold` | 내부 0.02m, 외곽 0.06m | 내부 **0.03m**, 외곽 0.06m |

거리 감소형의 weight 100은 기존 `FinalRewardsCfg.goal_distance`와 GoalAccuracy v0의 감소형 설정을 복원하는 설계 선택이며, 사용자가 본 명세를 수락하여 구현 기준으로 확정했다. 지수형 weight 3.7은 초당 점수의 계수이고, 감소형 weight 100은 감소 거리(m)의 계수다.

## 2. target_contact 검증과 후속 결정

[보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/final.py)의 `target_contact_or_goal`은 접촉과 목표 점유의 논리합이다. 따라서 **현재 보상 전체가 실제 타겟 접촉에만 반응한다는 가정은 틀리다.** 이를 확인한 뒤 사용자는 “현재 ‘접촉 또는 목표 도달’ 조건을 유지하고 weight만 1/4로 감소”를 선택했다. 이 후속 지시를 최종 계약으로 적용한다.

실제 접촉 분기 자체는 타겟–손 전용이다. [Scene](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/final.py)은 물체별 센서의 filter를 손 body들로 설정한다. [접촉 집계](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/contact_sweep_clutter_fusion_contacts.py)의 `target_hand_contact_force_w`는 물체별 `force_matrix_w` 벡터를 합한 뒤 환경별 `target_id`를 선택한다. 손–비타겟 장애물과 손–선반 접촉력은 이 분기의 입력이 아니다.

| 상태 | 원값 |
| --- | --- |
| fresh·finite 타겟–손 법선 합력 크기 ≥ 0.01N | 1 |
| 실제 접촉 없이 유효한 타겟이 `d <= 0.03m` | 1 |
| 두 조건 모두 충족 | 1, 중복 합산 없음 |
| 두 조건 모두 불충족 | 0 |

힘은 개별 크기의 합이 아니라 **법선 벡터 합력의 크기**이므로 반대 방향 힘이 상쇄될 수 있다. 물리적으로 닿은 모든 상태를 반드시 검출한다는 의미는 아니다. stale·비유한 힘은 접촉 분기를 통과하지 못해도 유효한 목표 점유로 보상을 받을 수 있다.

목표 점유는 기존 `target_measurements`의 유효성 V를 유지한다. 위치·속도·목표 XY·자세 값의 유한성, 선반 로컬 XY 영역, 높이 1.04–1.07m, 기울기 0.9rad 이하 조건이다. 실제 접촉 분기에는 V를 추가하지 않는다.

RewardManager 적용 후 보상은 `0.3625 * dt * (contact OR valid_in_goal)`이다. 기존 50Hz 제어에서는 해당 step당 0.00725다. weight는 초당 보상률이며 순간 이벤트 +0.3625가 아니다.

## 3. target_goal_distance: 최단 거리 기록 갱신량

기존 [DexPlanarGoalProgress](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/dex_rewards.py)를 사용한다. 거리는 타겟 위치와 목표점 사이의 world XY 유클리드 거리(m)이며 EEF 거리·표면 거리·높이를 사용하지 않는다.

초기 거리 `d0`, 현재 거리 `d_t`, 최대 접근량 `b_t`에 대해 다음과 같이 지급한다.

```math
p_t=\max(d_0-d_t,0),\quad b_0=0,\quad b_t=\max(b_{t-1},p_t)
```

```math
R_t^{\mathrm{distance}}=100(b_t-b_{t-1})
```

함수는 `(b_t-b_{t-1}) / dt`를 반환하고 RewardManager가 weight와 dt를 곱한다. `position_tolerance=0.0`을 명시하여 **0보다 큰 거리에서 포화되는 구간을 없앤다.** 성공 반경 0.03m를 이 파라미터에 넣지 않는다.

매 step 양의 거리 감소를 모두 다시 보상하는 방식이 아니라, 에피소드 최단 거리 기록 갱신량에만 지급한다. 대기·후퇴·이전 최단 거리로 복귀는 0이고 이전 기록보다 더 접근한 부분만 보상한다. 별도 후퇴 음수 보상은 추가하지 않는다.

| 거리 변화 | 해당 이동의 보상 |
| --- | --- |
| 초기 0.15m → 0.03m | +12 |
| 이어서 0.03m → 0.02m | +1 |
| 이어서 0.02m → 0m | +2 |
| 중심에서 정지 | 0 |
| 이후 후퇴했다가 중심 복귀 | 0 |

같은 초기 거리에서 중심까지 접근할 때 이 항의 **비할인 누적 보상**이 최대 `100*d0`다. “거리 0에서 최대”는 중심에 매 step 최대 보상을 주는 뜻이 아니다. 중심 유지의 지속 보상은 Hold가 담당한다. PPO 할인은 유지하므로 도달 시점에 따라 할인 수익은 달라질 수 있다.

기존 reset 계약을 유지한다. reset 시 초기 타겟 위치와 기록을 초기화하고 첫 호출에서 새 command와 초기 위치로 계산한다. 첫 action의 접근량을 누락하지 않으며 부분 reset은 해당 환경의 기록만 지운다.

## 4. 목표 인정 반경의 적용 범위

`target_goal_hold.params.position_tolerance=0.03`을 단일 기준으로 사용한다. 기존 `goal_radius(env, 'target_goal_hold')` 경로를 재사용하며 도달은 **`d <= r`**다.

| 소비 지점 | v0_3 동작 |
| --- | --- |
| Hold 내부 구간·거리 정규화 | r=0.03m |
| Contact 목표 점유 분기 | 기존 유효성 AND `d <= 0.03m` |
| `target_goal_success_at_timeout` | timeout AND `d <= 0.03m` |
| `target_goal_miss_at_timeout` | timeout AND NOT 목표 도달 |
| timeout 보너스 | 위 성공 term 사용, +100 |
| 성공·미달 로그 | 기존 이름 유지, 3cm로 집계 |
| `Metrics/target_goal_distance_xy_mean` | 원시 XY 거리 평균 유지, 임계값으로 자르지 않음 |
| 목표 반경 커리큘럼 | 기존 비활성 유지, 학습 내내 3cm |

성공/미달은 기존처럼 10초 만료 시 분할하고 모두 `time_out=True`를 유지한다. 3cm 진입 즉시 종료하지 않는다. 성공에는 속도·체류시간·Hold 유효성 조건을 추가하지 않는다. 기존 실패 종료와 timeout의 동시 발생 처리도 보존한다.

목표 관련 모든 **성공 반경 소비자**에 적용하며, 의미가 다른 거리를 일괄 치환하지 않는다.

- Hold 외곽 지급 반경은 0.06m다. 3cm 밖 6cm 안에서 Hold를 받아도 성공은 아니다.
- 거리 감소형 tolerance는 사용자 요구에 따라 **0.0m**다.
- `target_reaching`의 EEF–타겟 near radius는 현재 코드의 **0.10m**를 유지한다. 기존 v0_1 문서에는 0.20m라고 쓰여 있지만 현재 코드는 0.10m다. 이번 요청은 Reaching 변경이 아니므로 과거 문서 값으로 복원하지 않는다.
- 목표 방향 deadzone, 목표 생성·배치 영역, 속도 스케일, 물체 크기를 유지한다.
- `SweepGoalCommand`의 반지름 0.025m 구는 목표점 표시용이며 성공 영역 표시가 아니다. 표시 크기를 성공 반경으로 취급하거나 변경하지 않는다.

## 5. Hold와 timeout 보너스

`goal_accuracy_outer_settling` 함수, weight 8, speed_scale 0.05m/s, 유효성 V를 유지한다. 내부 반경만 0.03m로 바꾸므로 외곽 곡선 분모도 `0.06-0.03`으로 바뀐다.

```math
H(d)=\begin{cases}
\exp[-\ln 2(d/0.03)^2]\,[1+\max(1-d/0.03,0)^2], & d\leq0.03 \\
0.5\,[\max(\min((0.06-d)/0.03,1),0)]^2, & d>0.03
\end{cases}
```

```math
R_t^{\mathrm{hold}}=8\,dt\,V\,H(d)\exp[-\ln 2(v/0.05)^2]
```

v는 기존 타겟 3D 속력이다. 유효하고 정지한 경우 초당 보상은 중심 16, 3cm 경계 4, 6cm 경계 0이다. 3cm에서 내부·외곽 함수값은 연속이다.

현재 v0_2 보너스에는 성공 term 외에 `d < 0.02` 검사가 있어 정확히 2cm에서 성공으로 집계되어도 +30이 없다. v0_3에서는 이중 판정을 제거한다.

구현안은 기존 [success_event](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_rewards.py)를 보너스 callable로 재사용하는 것이다. `termination_name='target_goal_success_at_timeout'`, weight 100을 설정한다. 함수는 `success.float()/dt`를 반환하므로 최종 지급이 정확히 +100이고 독립 반경 파라미터가 필요 없다. v0_2가 사용하는 기존 보너스 함수는 수정하지 않는다.

이미 계산된 성공 term에 따라 자동 reset 이전 마지막 transition에 한 번 지급한다. 만료 전 목표 점유에는 0, reset 이후 새 에피소드에 중복 지급하지 않는다. 실패와 timeout 동시 발생 시에도 성공 term이 참이면 지급하는 기존 의미를 유지한다.

## 6. 구현 위치·상속·보존 범위

아래는 수락된 구현 위치와 이름이며 2026-10-30 등록·구현했다. 기존 역할별 파일을 유지하고 새 버전 디렉터리는 만들지 않는다.

| 위치 | 구현 예정 |
| --- | --- |
| `envs/final_envs.py` | `FinalGoalAccuracyV0_3EnvCfg(FinalGoalAccuracyV0_2EnvCfg)`; rewards만 교체 |
| `mdp/rewards/final.py` | `FinalGoalAccuracyV0_3RewardsCfg(FinalGoalAccuracyV0_2RewardsCfg)`; 위 네 보상 override |
| `agent/final_ppo_cfg.py` | `FinalGoalAccuracyV0_3PPORunnerCfg(FinalGoalAccuracyV0_2PPORunnerCfg)`; experiment_name만 `inspire_final_goal_accuracy_v0_3` |
| 패키지 `__init__.py` | `Isaac-Inspire-Final-GoalAccuracy-v0_3`; 기존 runtime `FinalGoalAccuracyEnv` |
| `tests/` | 보상·경계·전체 설정 대조·부모 회귀 검사 |

Scene·asset·물성·reset·Command·Event·Observation·Action·runtime·Termination Cfg·Curriculum Cfg를 상속한다. 정책 입력·모델·OSC·PPO 하이퍼파라미터·10초 에피소드·물리 100Hz/정책 50Hz를 유지한다. 목표 반경은 기존 소비자가 읽는 보상 설정으로 반영한다.

보상 순서는 부모와 동일하다: `target_reaching`, `target_goal_distance`, `target_goal_hold`, `target_contact`, `robot_action_rate_penalty`, `robot_joint_velocity_penalty`, `object_penalty`, `shelf_penalty`, `obstacle_contact_penalty`, `target_goal_timeout_bonus`, `wrist_wrench_change_penalty`, `target_speed_penalty`.

특히 timeout 보너스는 Wrench 항보다 앞에 둔다. Wrench의 양의 보상 예산이 선행 보상에 의존하므로 이번 보상 변경에 따라 실제 예산도 달라지는 것은 예상된 영향이다. 예산 비율·Wrench 계수·일정은 바꾸지 않는다. 보너스 항이 +100이며 전체 step 총보상이 반드시 +100이라는 뜻은 아니다.

## 7. 구현 완료 시 검증 기준

| 검증 | 통과 기준 |
| --- | --- |
| 접촉 대상·조건 | 목표 밖 비타겟/선반 접촉만 있으면 0; 타겟 접촉이면 1; 무접촉 유효 목표 점유이면 1; OR 중복 없음; weight 0.3625 |
| 측정 경계 | 0.01N 아래·정확히·위, stale, NaN, 벡터 상쇄, 환경별 target_id |
| 목표 경계 | 0.03m 아래·정확히·위에서 Hold·Contact·성공/미달·보너스 대조; Hold 외곽 별도 확인 |
| 거리 감소 | 최초 접근, 후퇴·재접근, 첫 step, 부분 reset, 3cm/2cm/1mm/0m 최단 기록; dt 독립 지급 |
| timeout | 만료 전 0, 성공 만료 +100, 거리 미달 만료 0, reset 뒤 중복 없음; 여러 dt 검사 |
| 순서·Wrench | 동일 step +100을 기존 양의 예산에 반영; term 순서 보존 |
| 전체 구성 | v0_2 대비 rewards 네 term과 등록/experiment만 명시한 차이; 나머지 callable·params·weight·일정·로그 이름 보존 |
| 부모 회귀 | v0·v0_1·v0_2·v1의 작업 전후 동등성, 특히 v0_2의 엄격한 보너스 경계 보존 |
| 실제 Isaac Sim | import·등록·reset/step·실제 접촉 센서 대상 분리·timeout 지급·커리큘럼 전환 확인 |

이번 작성에서 기존 접촉·timeout·거리 기록에 관한 CPU 검사 **12개 통과**를 확인했다. 현재 부모 동작에 관한 확인이며 v0_3이나 실제 물리 접촉을 검증한 결과가 아니다. 상세 실행과 미검증 범위는 개발 로그를 따른다.

구현 이후 학습에는 `src/inspire_sweep_baseline/scripts/train.py`를 사용한다. 기존 checkpoint 재개나 학습 실행은 이번 문서 작업에서 결정하지 않는다.
