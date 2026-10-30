# Final GoalAccuracy v0_3 구현 계약

[수락된 명세](../../01_plan/environments/2026-10-30_FINAL_GOAL_ACCURACY_V0_3_SPEC.md) · [개발·검증·리뷰 로그](../logs/2026-10-30_final_goal_accuracy_v0_3_spec.md) · [전체 설정 대조 결과](../../03_assets/artifacts/2026-10-30_goal_accuracy_v0_3/config_report.json) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

2026-10-30 구현. `Isaac-Inspire-Final-GoalAccuracy-v0_3`은 **v0_2를 직접 상속**한다. 명세의 보상 네 항목만 변경하며 기존 환경의 함수와 동작을 보존했다.

## 등록과 구성

| 항목 | 실제 값 |
| --- | --- |
| EnvCfg | `FinalGoalAccuracyV0_3EnvCfg` → `FinalGoalAccuracyV0_2EnvCfg` |
| RewardsCfg | `FinalGoalAccuracyV0_3RewardsCfg` → `FinalGoalAccuracyV0_2RewardsCfg` |
| runtime | 기존 `FinalGoalAccuracyEnv` |
| PPO | `FinalGoalAccuracyV0_3PPORunnerCfg` → `FinalGoalAccuracyV0_2PPORunnerCfg` |
| experiment_name | `inspire_final_goal_accuracy_v0_3` |

구현은 기존 `envs/final_envs.py`, `mdp/rewards/final.py`, `agent/final_ppo_cfg.py`, 패키지 `__init__.py`에 있다. Scene·Command·Event·Observation·Action·Termination·Curriculum·runtime·PPO 하이퍼파라미터는 부모와 같다. 정책 입력 policy 57D/obstacles 80D/privileged 3D, 행동 8D, 물리 100Hz·정책 50Hz, 10초 에피소드 구성을 보존한다. 현재 코드의 Reaching 반경은 10cm이며 그대로 유지한다.

## 최종 변경 표

| term | v0_2 → v0_3 |
| --- | --- |
| `target_contact` | 기존 `target_contact_or_goal` 유지; weight 1.45 → **0.3625** |
| `target_goal_distance` | 지수형 weight 3.7 → **`DexPlanarGoalProgress`, tolerance 0.0, weight 100** |
| `target_goal_hold` | `position_tolerance` 0.02 → **0.03m**; 함수·weight 8·외곽 6cm·speed_scale 0.05 유지 |
| `target_goal_timeout_bonus` | strict 거리 검사 +30 → **`success_event`, 성공 timeout term에 따라 +100** |

Contact는 실제 타겟–손 접촉 OR 유효한 목표 점유다. 실제 힘은 타겟별 센서의 손 filter에서 수집하며 임계값 0.01N, fresh·finite 검사와 법선 벡터 합산을 유지한다. 두 조건을 모두 만족해도 한 번만 지급한다.

거리 보상은 에피소드 최단 XY 거리 기록을 1cm 갱신할 때 +1이다. 성공 반경 3cm 안에서도 중심까지 지급하며 대기·후퇴·기록 복귀에는 중복 지급하지 않는다. 중심에 멈췄을 때의 지속 보상은 기존 Hold가 담당한다.

Hold의 목표 반경을 읽는 기존 경로를 통해 Contact 목표 점유 및 timeout 성공/미달도 **`d <= 0.03m`**를 사용한다. timeout 보너스는 성공 term을 직접 읽으므로 정확히 3cm에서도 +100이다. 조기 성공 종료, 추가 속도·체류시간 조건은 없다. 실패와 timeout의 동시 발생 처리도 부모와 같다.

목표 반경·Hold 속도 커리큘럼은 비활성으로 유지한다. 거리 감소 tolerance 0, Hold 외곽 6cm, Reaching 반경 10cm, 목표점 표시용 구 반경 2.5cm는 서로 다른 의미다. 원시 거리 metric은 임계값으로 자르지 않는다.

보상 이름과 순서는 부모와 같으며 timeout 보너스는 Wrench 항 앞에 있다. 양의 보상량 변경에 따라 Wrench의 기존 5% 예산이 달라지는 것은 명세에 포함된 영향이다. Wrench 계수·일정은 보존한다.

## 검증과 코드 리뷰

- 관련 CPU 검사 **93개 통과**: 기존 Final·GoalAccuracy 회귀, 부모 격리, 세 가지 dt에서 거리 기록·3cm 경계·+100, partial reset, Contact 대상 선택, Wrench 예산, 공식 Manager 인자 검증 포함.
- 접촉 임계값 바로 아래/위 사례를 보강한 뒤 해당 접촉 검사만 재실행하여 **6개 통과**했다.
- 실제 Isaac Sim AppLauncher로 새 Gym ID·EnvCfg·PPO 로딩 성공. 모든 중첩 설정과 순서를 비교하여 네 보상 및 PPO experiment_name 외 차이가 없음을 확인했다. Scene 재구성 용량 3종과 기존 환경 4종의 설정 격리도 통과했다.
- 작업 전 HEAD와 기존 클래스/함수 정의 29개 및 모든 기존 등록의 AST를 대조해 변경 없음을 확인했다.
- 독립 코드 리뷰 결과: 개발 규칙 위반 **0건**, 명세 불일치 **0건**. 세부 증거·범위는 개발 로그를 따른다.

**실제 물리 reset/step, 접촉 센서의 동적 대상 분리, 성공 위치를 만든 timeout transition, 학습 수렴·성공률은 미검증이다.** 현재 호스트는 NVIDIA 드라이버와 CUDA 장치를 사용할 수 없다. 설정 probe 성공을 물리 동작 검증으로 해석하지 않는다.

## 실행

workspace 루트에서 Isaac Lab 환경을 활성화하고 실행한다. 아래 학습 명령은 안내이며 이번 작업에서 학습을 시작하지 않았다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Final-GoalAccuracy-v0_3 --num_envs 2048 --headless
```

전체 설정 대조는 다음 명령으로 재현한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/tests/_final_accuracy_v0_3_probe.py \
  --headless --device cpu
```

GPU 사용 가능 시 같은 probe에 `--device cuda:0 --smoke`를 지정하면 reset/step·커리큘럼 전환·timeout 분할 검사를 수행한다. 이 smoke는 성공 위치나 접촉 대상을 의도적으로 만들지 않으므로 실제 성공 transition 지급과 접촉 대상 분리 검사를 대체하지 않는다.
