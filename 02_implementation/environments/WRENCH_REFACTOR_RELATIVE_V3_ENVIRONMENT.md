# Inspire-Wrench-Refactor-Relative-v3

2026-11-06. Relative-v0를 직접 상속하여 별도 접촉 유지 보상을 없애고, 기존 cosine 거리 보상을 현재 step 접촉 조건으로 제한하는 실험이다. 거리 weight는 Refactor-v1을 참고하여5에서25로 올린다.

## 등록과 공통 구성

| 항목 | 설정 |
| --- | --- |
| Gym ID | `Inspire-Wrench-Refactor-Relative-v3` |
| EnvCfg | `WrenchRefactorRelativeV3EnvCfg(WrenchRefactorRelativeEnvCfg)` |
| runtime | `runtime.wrench_refactor:WrenchRefactorEnv` |
| PPO | `WrenchRefactorRelativeV3PPORunnerCfg` |
| experiment_name | `inspire_wrench_refactor_relative_v3` |
| Actor / Critic | 동일한 `policy`58D + `obstacles`64D |
| encoder / 본체 입력 | 장애물64→32→16, 직접58+16=74D |
| 타겟 / 장애물 | 초기 snapshot을 현재 EEF 기준으로 변환 |
| Axia / 손 질량 | 0.280kg / 0.790kg |

[Relative-v0 전체 명세](WRENCH_REFACTOR_RELATIVE_V0_ENVIRONMENT.md)의 초기화·물체 및 목표 생성·액션·관측·종료·커리큘럼을 그대로 상속한다. 목표와 보정 F/T도 EEF 기준이며 EEF pose만 base 기준이다. v2의 비대칭 Critic 관측은 사용하지 않는다.

## 보상 변경

| 항목 | v0 | v3 |
| --- | --- | --- |
| `target_contact` | 별도 접촉 유지 보상 | 삭제 (`None`) |
| `target_goal_distance` | cosine 거리, weight5 | 현재 접촉 조건부 cosine 거리, weight25 |

기존 `displacement_cosine_goal_distance` 출력에 현재 step의 `target_contact_below_height` 조건을 적용한다. 실제 타겟-손 접촉력0.01N 이상, fresh 센서 값, EEF 높이가 초기 선반면보다14cm 미만인 경우만 지급한다. 과거 접촉 횟수·2/3 step 유지 상태를 이 gate에 사용하지 않으며, 목표 내부라는 이유로 접촉 조건을 우회하지 않는다. 접촉이 끊긴 step에는 거리 보상이0이다.

초기→현재 타겟 변위와 초기→목표 벡터의 XY signed cosine은 그대로다. 역방향 변위의 음수 cosine, 변위0에서 보상0, 기존 거리 scale0.05 및 유효성 조건을 보존한다. 조건 충족 시 거리 함수×cosine×25×step_dt로 최종 보상에 반영된다. 기본 step_dt0.02초에서 양의 상한은 step당0.5다. 최초 진입 보너스10과 나머지 보상은 변경하지 않는다.

## 제어·종료·커리큘럼

현재 EEF frame OSC와 raw 정책 action-rate를 유지한다. Arm6관절 물리 속도 한도3.14rad/s, effort150/150/150/28/28/28Nm이다. 속도 종료 임계값은10,000iteration까지4.0rad/s,10,250부터250iteration마다0.05씩 감소하고20,000부터2.0을 유지한다. 기존 목표 방향 커리큘럼 및 다른 종료 조건은 같다.

## 실행과 검증

Workspace 루트의 Isaac Lab Python에서 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-v3 --num_envs 2048 --headless
```

GPU 스모크는2환경180step 및 부분 reset으로 수행했다. 보상 수식과 현재 접촉 gate는 CPU 시험으로 추가 검증했다. 실제 관측 좌표와 물리 질량·한계, 설정 전체 차이는 GPU에서 대조했다. 대규모 학습 성능은 미검증이다. [개발·검증 기록](../logs/2026-11-06_relative_family_280g_v3.md).
