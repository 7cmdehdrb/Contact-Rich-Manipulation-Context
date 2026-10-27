# Final GoalAccuacy v1 환경

[활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [부모 Accuracy v0 명세](FINAL_GOAL_ACCUACY_V0_ENVIRONMENT.md) · [개발·검증 기록](../logs/2026-10-27_final_goal_accuracy_v1.md)

2026-10-27. Accuracy v0를 직접 상속하여 Final v1의 목표 외곽 보상과 체류 속도 커리큘럼을 복원한다. 사용자가 단위를 확인했으며 목표 인정 반경은 **0.01 m = 1 cm**다. 기존 v0와 Final v1은 수정하지 않았다. 현재 코드 계약이며 학습 성능 비교 결과가 아니다.

## 등록과 부모

| 항목 | 값 |
| --- | --- |
| Gym ID | `Isaac-Inspire-Final-GoalAccuacy-v1` |
| EnvCfg | `FinalGoalAccuracyV1EnvCfg(FinalGoalAccuracyEnvCfg)` |
| Runtime | 기존 `FinalGoalAccuracyEnv(FinalV1Env)` 재사용 |
| Reward | `FinalGoalAccuracyV1RewardsCfg(FinalGoalAccuracyRewardsCfg)` |
| Curriculum | `FinalGoalAccuracyV1CurriculumCfg(FinalGoalAccuracyCurriculumCfg)` |
| PPO | `FinalGoalAccuracyV1PPORunnerCfg(FinalGoalAccuracyPPORunnerCfg)` |
| Experiment | `inspire_final_goal_accuracy_v1` |

등록 ID는 기존 계열과 동일하게 `GoalAccuacy` 철자를 사용한다. 코드: [등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py), [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/final_envs.py), [Reward](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/final.py), [Curriculum](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/final.py), [PPO](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/final_ppo_cfg.py).

## Accuracy v0 대비 요청 반영

| 요청 | v0 | v1 |
| --- | --- | --- |
| `goal_speed_scale` 복원 | 비활성, .05 m/s 고정 | Final v1 일정 재사용: `(0, .05), (6000, .05), (10000, .02)`, 간격 250 iteration |
| `object_free_speed` 복원 | 이미 활성 | 그대로 상속. `target_speed_penalty.free_speed`에 적용 |
| `goal_hold` 외곽 구간 복원 | 유효 타겟의 `d <= r`에만 지급 | Final v1의 `goal_settling_centered` 재사용, `d <= 2r`에 지급 |
| 목표 반경 고정 | .01 m | 유지, `goal_position_tolerance=None` |

`object_free_speed`는 `(0, .1), (499, .1), (500, .09), (1900, .02)`, 간격 250 iteration이며 Final v1과 수치가 동일하다. 대상은 타겟의 3D 선속도이고 페널티 weight는 -5다. 새 term을 중복 활성화하지 않는다.

`goal_hold` weight 8과 중심 보너스는 v0 값을 유지한다. 원문의 `r < d < 2r` 복원은 Final v1 함수를 그대로 재사용하여 **정확히 `d=2r`도 지급**하는 의미로 구현했다. 목표 도달 인정은 계속 **`d <= r`**이며 접촉 간주·Reaching의 반경 완화·시간 만료 성공 반경을 2r로 넓히지 않는다.

`d`는 타겟–목표 XY 거리, `v`는 타겟 3D 속력, `r=.01`, `s`는 현재 `speed_scale`, `V`는 부모의 타겟 유효성 조건이다. 제어 스텝 보상:

```math
R=8\Delta t\,\mathbf{1}_{V\land d\le2r}
\exp\left[-\ln2\left((d/r)^2+(v/s)^2\right)\right]
\left[1+\mathrm{clip}(1-d/r,0,1)^2\right].
```

기본 `dt=.02`에서 중심 정지 보상은 스텝당 .32, r 경계 정지는 .08, 2r 경계 정지는 .01이다. 지급 시간 상한은 없다. `speed_scale`은 hard cutoff가 아니라 속도 감쇠 척도다.

## Final v1과 최종 전체 대조

| 범위 | Final v1 | Accuracy v1 |
| --- | --- | --- |
| 등록·설정·experiment | Final v1 계열 | 위의 신규 Accuracy v1 계열 |
| Runtime·종료 callable | `FinalV1Env`, 직접 timeout 함수 | Accuracy v0 런타임·계측 래퍼 상속 |
| `goal_hold` 함수·외곽 조건 | `goal_settling_centered`, `d <= 2r` | 동일 |
| `goal_hold` weight | 4 | **8**, Accuracy v0 유지 |
| 목표 반경 | 4000까지 .02 m, 4000→10000 매 iteration 선형 감소, 이후 .01 m | **처음부터 .01 m 고정** |
| `goal_speed_scale` | 6000까지 .05 m/s, 10000까지 250 iteration 계단 감소, 이후 .02 | 동일 |
| 목표 연동 판정 | 현재 r를 사용하는 접촉 간주·Reaching 전환·timeout 성공 | 같은 함수가 고정 r=.01을 사용 |
| 타겟 속도 페널티 이름 | `object_speed_penalty` | `target_speed_penalty`; 함수·weight·params 동일 |
| `object_free_speed` | `object_speed_penalty.free_speed` 갱신 | `target_speed_penalty.free_speed` 갱신; 함수·points·interval 동일 |
| 장애물 개수 일정 | Gray 3000, White 2000 시작, 간격 2000 | **Gray 2500, White 2000 시작, 간격 1000**, Accuracy v0 유지 |
| 장애물 초기·최종 요청 / 용량 | 1+1 → 8+8 / 10+10 | 동일; 실제 배치는 공통 fallback 결과 사용 |
| 나머지 Reward·Curriculum | Final v1 설정 | 동일; 속도 항 이름 변경에 따른 활성 순서는 v0 상속 |
| 실패 종료·timeout 의미 | 실패 4항, 성공/미성공 모두 truncation, 목표 조기 종료 없음 | 동일; 성공 반경만 위 차이 |
| Scene·Command·Event·reset 배치 | Final v1 | 동일 구성; 개수 일정에 따른 배치 밀도 차이 있음 |
| Observation·Action·물리 | policy 57D, obstacles 80D, privileged 3D; Action 8D; dt .01, decimation 2; 최대 10초 | 동일 |
| PPO·모델 | Final v1 | experiment 이름 외 동일 |
| Metric | 실제 개수 `Curriculum/obstacle_actual_*` | v0의 `Metrics/obstacle_actual_*` 및 거리·EEF 속도·타겟 속도·가속도 평균, force/moment 최대 계측 유지 |

계측 통계와 reset 시점은 [부모 명세](FINAL_GOAL_ACCUACY_V0_ENVIRONMENT.md)의 7절과 같다. 부모와 같은 로그 키 이동이며 실험 로그를 분석한 결과가 아니다. `goal_distance`도 여전히 `DexPlanarGoalProgress`, weight 100이다.

Final v1과의 차이가 목표 반경 하나만 남은 환경은 아니다. 요청 밖의 **goal_hold weight 8, 빠른 장애물 증가, 이름 변경과 계측**을 유지했다. 또한 wrench 페널티는 누적 양의 보상 5% 예산을 공유하므로 목표 보상·목표 연동 보상의 변화가 실제 페널티 제한에 간접 영향을 줄 수 있다. iteration 10000 이후 목표 반경과 속도 척도가 같아져도 weight 차이는 남는다.

## 실행과 검증 범위

Isaac Lab 환경이 설치된 workspace 루트에서 실행한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Final-GoalAccuacy-v1 --num_envs 256 --headless
```

기본 출력 경로는 `logs/rsl_rl/inspire_final_goal_accuracy_v1`이다. 이 작업에서 학습은 실행하지 않았다.

CPU 관련 검사 **48개 통과**: 신규 4개 검사로 전체 보상·커리큘럼 차이, 등록·EnvCfg·PPO 상속, 경계 r와 2r 및 그 전후, live schedule 전환·최종·rewind, 부모 설정 격리를 확인했다. 기존 44개 검사도 통과했다. 패키지 174개 Python 소스의 작업 전 스냅샷과 비교하여 기존 AST 구문·클래스·함수 불변을 확인했다. Isaac Sim 전체 환경 import/reset/step, GPU 물리, 실제 학습·수렴·정확도 향상은 미검증이다.
