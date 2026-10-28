# Final GoalAccuracy v0_1 구현 계약

[활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [개발 사양](../../01_plan/environments/2026-10-28_FINAL_GOAL_ACCURACY_V0_1_REWARD_SPEC.md) · [구현·검증 로그](../logs/2026-10-28_final_goal_accuracy_v0_1.md) · [부모 v0](FINAL_GOAL_ACCURACY_V0_ENVIRONMENT.md)

2026-10-28 구현. `Isaac-Inspire-Final-GoalAccuracy-v0_1`은 Accuracy v0를 직접 상속한다. 2cm 목표 인정, 타겟 접촉, 고정 20cm Reaching, 6cm 외곽 Hold, 지수 거리 보상, 직육면체 타겟과 대상별 Manager 이름을 적용했다. 기존 v0/v1은 Gym ID의 `Accuacy` 오타만 `Accuracy`로 교정했으며 1cm 보상·종료·일정은 보존한다. 옛 ID alias는 등록하지 않는다.

## 등록과 상속

| 구분 | 값 |
| --- | --- |
| Gym ID | `Isaac-Inspire-Final-GoalAccuracy-v0_1` |
| EnvCfg | `FinalGoalAccuracyV0_1EnvCfg` → `FinalGoalAccuracyEnvCfg` |
| runtime | 기존 `FinalGoalAccuracyEnv` 재사용 |
| Scene | `FinalGoalAccuracyV0_1SceneCfg` → `FinalV1SceneCfg` |
| Reward·Curriculum·Termination | `FinalGoalAccuracyV0_1RewardsCfg`, `FinalGoalAccuracyV0_1CurriculumCfg`, `FinalGoalAccuracyV0_1TerminationsCfg`; 각각 v0 상속 |
| PPO | `FinalGoalAccuracyV0_1PPORunnerCfg` → `FinalGoalAccuracyPPORunnerCfg` |
| experiment_name | `inspire_final_goal_accuracy_v0_1` |

관측 policy 57D·obstacles 80D·privileged 3D, Actor의 초기 타겟/장애물 입력 및 Critic 현재 타겟 입력, 관측 노이즈, 8D 행동과 OSC, 50Hz 제어·100Hz 물리, 10초 에피소드, seed·reset·배치·물성·실패 조건·PPO 하이퍼파라미터는 부모와 같다. 새 학습 출력은 별도 experiment 경로를 사용한다.

## 보상·게이트

| 활성 보상 순서 | 계산 또는 변경 |
| --- | --- |
| `target_reaching` | EEF–타겟 3D 거리의 near radius 0.20m 밖 최단 gap 갱신량 ×30; 목표 점유 분기 없음 |
| `target_goal_distance` | 현재 world XY 거리 d에 대해 초당 `3.7 exp(-20d)` |
| `target_goal_hold` | r=0.02m, R=0.06m, speed_scale=0.05m/s, weight=8; 사양의 내부 centered score와 quadratic 외곽 연결 |
| `target_contact` | 타겟–손 합력 ≥0.01N이며 fresh/finite, 또는 유효한 타겟이 d≤0.02m일 때 초당 1.45 |
| `robot_action_rate_penalty` | 부모의 Arm·Hand action 변화 비용 |
| `robot_joint_velocity_penalty` | 부모의 Arm·Hand 관절 속도 비용 |
| `object_penalty` | 전체 활성 물체 기울기·가속도 + 장애물 변위 비용 |
| `shelf_penalty` | 부모 계산 유지; 종료 설정 조회 이름만 `shelf_failure` |
| `obstacle_contact_penalty` | 장애물–손 접촉 비용 유지 |
| `wrist_wrench_change_penalty` | 기존 Wrench 크기 변화·5% 예산 비용; 양의 보상 뒤 순서 보존 |
| `target_speed_penalty` | 타겟 3D 속력 비용 유지 |

모든 보상률은 RewardManager가 dt를 한 번 곱한다. Reaching은 기존처럼 함수 내부에서 dt로 나누어 거리 증가분을 지급한다. 타겟 Contact의 실제 접촉 분기에는 새로운 거리·저속·유효성 조건을 넣지 않는다. 목표 간주는 기존 타겟 유효성 V를 사용하며 촉각 관측을 강제로 켜지 않는다. 물체별 접촉 벡터를 합하고 해당 환경의 target_id를 선택하므로 선반·비타겟 장애물 힘이 타겟 접촉 보상을 만들지 않는다.

`target_goal_hold.position_tolerance`가 목표 반경의 단일 기준이다. Hold 유효성, 경계 및 식은 개발 사양 3–7절과 같다. 2cm 밖에서도 6cm까지 Hold를 받지만 성공·Contact 목표 간주 반경은 2cm다. 거리 보상의 기준 궤적 적분은 2cm 도달 13.122572, 중심 도달 18.868424이며, 학습 성공률을 뜻하지 않는다.

## 커리큘럼과 종료

활성 커리큘럼은 순서대로 `obstacle_population`, `obstacle_gray_zone_padding`, `target_free_speed`, `object_free_acceleration`, `object_acceleration_weight`, `target_goal_direction_deadzone`, `wrist_wrench_free_force_change`, `wrist_wrench_free_moment_change`, `wrist_wrench_change_weight`, `obstacle_contact_free_force`, `obstacle_contact_weight`다. 점·갱신 간격·iteration·파라미터 값은 부모와 같다. `target_goal_speed_scale`과 `target_goal_position_tolerance`는 비활성이다. 이름 변경 대응과 각 대상은 개발 사양 8.3절을 따른다.

종료는 순서대로 `object_fall_or_tilt`, `target_speed`, `shelf_failure`, `arm_joint_velocity`, `target_goal_success_at_timeout`, `target_goal_miss_at_timeout`이다. 마지막 두 항은 10초 만료의 d≤0.02 여부를 분할하며 둘 다 `time_out=True`다. 조기 성공 종료·속도·연속 유지시간 조건을 추가하지 않았다. metric 수집과 실패/만료 동시 발생 가능성은 기존과 같다.

옛 활성 term은 자식에서 None 처리하여 중복 지급·중복 호출을 막는다. Reward·Curriculum은 상속으로 새 필드가 뒤에 붙는 문제를 방지하도록 인스턴스의 Manager 순서를 부모 순서에 맞춰 명시적으로 정렬한다. 설정 조회에는 새 이름을 전달하고 공유 함수의 기본 인자는 기존 이름으로 남겨 다른 환경을 보존했다.

## 큐브와 스폰

큐브 타겟만 로컬 XYZ 기본 치수를 0.06×0.08×0.10m로 바꿨다. Scene 재구성 때 타겟 MultiAsset의 cube variant에만 `cube_size`를 적용한다. 기존 환경의 기본 cube_size는 0.08×0.08×0.08m이며, 다른 타겟·장애물·종류 확률은 동일하다.

기존 생성 시 `Uniform(0.9,1.1)` 균일 배율과 reset 시 형상·배율 보존을 유지한다. 시각·충돌 mesh가 동일 치수를 사용하며 기존 prestartup bounds와 `shelf_surface_height - bounds_min_z` 스폰 경로를 재사용한다. bottom-origin이므로 높이 증가에 맞춰 반높이를 더하지 않는다. bounds 기반 목표 여유·배치·가림·target_width 경로도 유지한다. 새 cube의 관성은 명시적 실린더 관성을 재사용하지 않고 기존 procedural mesh의 자동 질량 속성 계산 경로를 사용한다.

## 로그와 실행

Manager 로그는 새 이름을 사용한다. 예: `Episode_Reward/target_goal_hold`, `Curriculum/target_free_speed`, `Episode_Termination/target_goal_success_at_timeout`. 기존 `Metrics/*`의 이름·집계는 유지한다. 과거 로그·checkpoint·저장된 설정은 변경하지 않았다.

workspace 루트에서 GPU와 Isaac Sim 자산 접근이 가능한 환경의 명령 예시다. 이번 작업에서 학습을 실행한 명령이 아니다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Final-GoalAccuracy-v0_1 --num_envs 2048 --headless
```

## 검증 상태

- 관련 CPU 검사 139개 통과: 신규 보상 수치·경계·대상 선택·순서·커리큘럼 rewind·등록·공식 Manager 인자 검사·부모 회귀·PPO CPU 업데이트 포함.
- 추가로 Holding v0/v4 회귀 18개와 변경 전 커밋의 기존 Manager 구성 대조 3개가 통과했다.
- 실제 Isaac Sim import/등록/EnvCfg 생성 통과. 전체 top-level 설정에서 부모와 달라진 그룹이 Scene·Reward·Curriculum·Termination 네 개뿐임을 대조했다. PPO는 experiment_name만 다르다.
- 실제 Scene 재구성 4개 용량에서 타겟 cube_size 외 차이가 없음을 확인했다.
- 실제 USD 생성·prestartup scaling에서 0.9/1.0/1.1 배율의 치수·collision 존재·바닥 높이 1.05m 정렬을 확인했다. 이는 동적 접촉 검증이 아니다.
- 물리 reset/step: CUDA 장치가 없는 환경에서 초기화를 완료하지 못해 중단했다. 물리 접촉·행동·학습 수렴·성공률은 미검증이다.

[실제 설정·USD 결과](../../03_assets/artifacts/2026-10-28_goal_accuracy_v0_1_implementation/config_and_assets.json)와 상세 실행·제약은 구현 로그를 따른다.
