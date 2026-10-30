# GoalAccuracy 계열의 5000 iteration 물체 수 상한

[Accuracy v0 계약](../environments/FINAL_GOAL_ACCURACY_V0_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [실제 전체 설정 변경 대조](../../03_assets/artifacts/2026-10-30_goal_accuracy_population_cap/config_delta.json)

## 요청·근거·범위

2026-10-30 사용자는 스폰 관련 성능 진단을 중단시킨 뒤, Accuracy 최상위 환경과 모든 하위 환경의 물체 수를 5000 iteration 수준으로 제한하라고 요청했다. 이번 변경은 별도의 성능 최적화가 아니라 **기존 환경들의 장애물 수 커리큘럼 상한 수정**이다.

기준 workspace HEAD: `dc452fdc323a70eaaddffb164c785f75deef1a60`. 작업 시작 시 코드 작업트리는 clean이고 문서 submodule 포인터 차이가 있었다. 문서 저장소 HEAD는 `ed7ad400d38313bf01a46664e038f50f00d03b5f`, 내부 작업트리는 clean이었다. 두 저장소 HEAD와 사용자 기존 상태를 보존했다.

대상 Gym ID는 `Isaac-Inspire-Final-GoalAccuracy-` 접두사의 `v0`, `v1`, `v0_1`, `v0_2`, `v0_3`이다. 실제 등록은 `Accuracy` 표기다. 공통 부모 `FinalGoalAccuracyEnvCfg`는 `FinalGoalAccuracyCurriculumCfg`를 사용하고, v1/v0_1 커리큘럼은 이를 상속하며 v0_2/v0_3은 v0_1의 커리큘럼을 그대로 상속한다.

## 구현과 변경 전후

수정 소스: `src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/final.py`의 `FinalGoalAccuracyCurriculumCfg.obstacle_population.params`.

| 파라미터 | 이전 | 이후 |
| --- | --- | --- |
| `final_gray` | 8 | **4** |
| `final_white` | 8 | **5** |
| `initial_gray`, `initial_white` | 1, 1 | 동일 |
| Gray/White 증가 시작 | 2500 / 2000 | 동일 |
| 각 색 증가 간격 | 1000 | 동일 |

실제 `obstacle_population_schedule`은 시작 iteration에서 첫 증가를 적용하므로 5000에서 Gray 4, White 5다. 기존 5500의 Gray 증가를 새 상한으로 차단한다.

| iteration | 새 요청 Gray | 새 요청 White |
| --- | --- | --- |
| 0–1999 | 1 | 1 |
| 2000–2499 | 1 | 2 |
| 2500–2999 | 2 | 2 |
| 3000–3499 | 2 | 3 |
| 3500–3999 | 3 | 3 |
| 4000–4499 | 3 | 4 |
| 4500–4999 | 4 | 4 |
| **5000 이후** | **4** | **5** |

최대 장애물은 9개이고 타겟 1개를 포함하면 10개다. 이는 요청 수 상한이며 배치 실패 fallback 때문에 실제 활성 수는 더 적을 수 있다. Scene 저장 용량 Gray/White 10/10 및 장애물 관측 20슬롯은 유지하여 모델·checkpoint 차원을 보존한다. Gray padding, 목표 방향, 모든 보상·종료·다른 커리큘럼, 배치 시도 횟수와 기하 검사는 변경하지 않았다.

스케줄은 절대 learning_iteration에서 다시 계산하므로 후반 checkpoint를 읽어도 새 코드의 상한 4/5를 사용한다. 업데이트 대상은 이후 reset의 스폰 요청이며 진행 중 에피소드의 마스크를 직접 바꾸지 않는다. 이미 실행 중인 Python 프로세스에는 자동 반영되지 않으므로 새 코드로 재시작/재개해야 한다. 학습 프로세스 제어·재개 실행 및 기존 학습 로그 수정은 수행하지 않았다.

## 검증

workspace 루트에서 실행:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_final_versions.py \
  src/inspire_sweep_baseline/tests/test_final_accuracy_v0_1.py \
  src/inspire_sweep_baseline/tests/test_final_configuration.py
```

결과: **81 passed**. 상속되는 커리큘럼 3종 모두 4999/5000/5001/5499/5500, 증가 시작 경계, 후반 7549/8342 재개, 90000, 0으로 rewind를 확인했다. Event의 실제 스폰 요청 파라미터 갱신과 기존 활성 마스크 보존도 검사했다. Accuracy 밖 Final v1은 최종 8/8을 유지한다.

실제 Isaac Sim AppLauncher를 이용한 임시 검사기로 변경 전후 전체 EnvCfg/PPO를 각각 저장했다.

```bash
timeout 90s /home/min/miniconda3/envs/env_isaaclab/bin/python \
  /tmp/check_goal_population_configs.py --headless --device cpu \
  --output /tmp/goal_population_before.json > /tmp/goal_population_before.log 2>&1
```

위 명령은 소스 수정 전에 실행했다. 수정 후 같은 검사기에 `--output /tmp/goal_population_after.json`을 전달하고 `/tmp/goal_population_after.log`로 출력했다. 두 실행 모두 **exit 0**. 검사기는 5개 Accuracy 및 Final v1의 등록에서 실제 EnvCfg/PPO를 로드하여 `to_dict()`를 JSON으로 저장한다. 임시 전체 스냅샷은 `/tmp`에 두고, 중첩 dict 순서·list 길이·모든 값을 재귀 대조한 차이만 위 산출물에 보존했다.

최종 대조 결과:

- Accuracy 5종: 각 환경의 `curriculum.obstacle_population.params.final_gray`와 `final_white`만 8/8 → 4/5. 다른 모든 EnvCfg·PPO 값과 순서 동일.
- Final v1: 전체 EnvCfg·PPO 변경 없음.
- 실행 코드 diff: 공통 부모의 두 숫자와 의도 주석만 변경. 새 task·runtime·함수·관측·reward 변경 없음.
- 환경 문서, 활성 안내, 인계, 패키지 README에 공통 상한과 실행 중 프로세스 적용 조건을 기록했다. 이전 v0_3 명세의 보상 계약은 보존하며 별도 후속 지시임을 표시했다.

문서 검증: 변경 Markdown 8개 수식 검사 통과, 문서 저장소 7개 파일의 링크 검사 오류 0(내부 56, 외부 workspace 21), 두 저장소 `git diff --check` 통과. 패키지 README에 추가한 링크는 같은 개발 로그를 가리킨다.

GPU 물리 reset/step, 실제 후반 checkpoint 재개, 변경 후 collection time·성공률은 미검증이다. 커리큘럼 상한과 설정의 검증을 실제 학습 속도 개선 수치로 주장하지 않는다.
