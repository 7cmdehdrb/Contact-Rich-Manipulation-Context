# Final v1-Test — object_penalty 세 항 분리

[개발 로그 목록](README.md) · [환경 계약·재개 명령](../environments/FINAL_V1_V2_ENVIRONMENTS.md#final-v1-test--object_penalty-세-항-분리) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

2026-10-27 사용자 요청: Final v1과 같은 보상 총합을 유지하면서 병합된 `object_penalty`를 세 RewardManager term으로 나누고, 기존 v1 checkpoint에서 재개한 학습 로그로 어느 비용이 큰지 확인할 수 있게 한다.

## 기준과 변경

작업 시작 시 코드 workspace HEAD는 `efc09658ca8b9cbf7b1fbeda54da364c47460029`, 문서 submodule HEAD는 `7059478e2711df434b50704370a402acdcddda59`였다. 두 저장소에는 이전 작업의 미커밋 변경이 있었으며 보존했다. 원본 학습 run은 `logs/TEMP/2026-10-26_17-11-27`, 사용 가능한 최신 checkpoint는 `model_9500.pt`다.

`Isaac-Inspire-Final-Test-v1`은 `FinalV1TestEnvCfg → FinalV1EnvCfg → FinalEnvCfg`를 사용하고 runtime은 `FinalV1Env`다. `FinalV1TestRewardsCfg`는 v1의 `object_penalty`를 제거하고 `object_tilt_penalty`(−30), `object_displacement_penalty`(−150), `object_acceleration_penalty`(초기0, v1의 가속도 일정)를 추가한다. `FinalV1TestCurriculumCfg`는 가속도 무료 기준·가중치의 대상 이름만 새 term으로 바꾼다. 가속도 비용 함수는 v1의 `ObjectAccelerationPenalty`를 그대로 사용한다. `combined_active_object_cost`가 같은 기울기·변위 계산 함수를 합성하도록 정리하여 부모 환경과 분리 환경이 수식을 공유한다.

PPO 모델·하이퍼파라미터·관측은 v1을 상속하고 experiment 이름은 `inspire_final_v1_test`로 분리했다. 원본 run이 `logs/TEMP`에 있으므로 `train.py --resume --checkpoint <실제 파일 경로>`가 정규식 검색 대신 해당 파일을 직접 읽도록 했다. 기존 `--load_run`·checkpoint 이름 검색 동작은 경로가 파일이 아닐 때 유지된다. 코드·학습 명령은 `train.py`만 사용한다.

## 실제 검증

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_final_versions.py src/inspire_sweep_baseline/tests/test_termination_debug.py -q`: **31 passed, 10.98s**. 비활성 물체·타깃 변위 제외·장애물 변위 상한·가속도 활성화에서 v1 병합 비용과 세 항의 합을 비교했고, v1 모델 가중치를 Test PPO에 로드했다. 최초 실행은 fixture의 `step_dt` 누락으로 1실패였고 fixture를 보완한 뒤 재실행했다. 그 전의 일반 pytest 호출은 ROS pytest plugin의 `lark` 누락으로 수집 전에 중단되어 plugin autoload를 비활성화했다.
- `env_isaaclab`과 GPU에서 실제 Gym 등록의 EnvCfg·PPO Cfg를 로드했다. `FinalV1TestEnvCfg`의 부모, 세 보상 term, 가속도 커리큘럼 대상, Actor/Critic 설정 일치를 확인했다. 명령은 작업 공간에서 `AppLauncher({'headless': True, 'device': 'cuda:0'})`, `load_cfg_from_registry`를 사용한 단발 Python 검사이며 exit0이었다.
- 같은 GPU에서 Final v1-Test **1환경, seed42, stage9500, reset 및2 step**을 실행했다. 관측 차원57/80/3, 세 term 존재·원래 병합 term 부재, 음의 가속도 weight, 매 step RewardManager 항의 합과 전체 reward 일치, 유한 reward를 확인했다. 실행 출력은 `/tmp/final_v1_test_gpu_smoke.log`, exit0이다.
- 기존 `logs/TEMP/2026-10-26_17-11-27/model_9500.pt`를 새 `CurriculumOnPolicyRunner`에 로드했다. `current_learning_iteration`과 환경 커리큘럼이 모두9500이고, checkpoint 정책의 한 step이 유한 보상을 반환했다. 실행 출력은 `/tmp/final_v1_test_checkpoint_load.log`, exit0이다. 이 검사는 checkpoint를 읽기 전용으로 사용했다.

## 해석과 남은 범위

실제 재개 학습은 수행하지 않았다. 위 검사는 두 step과 checkpoint 로드까지이며, 장기 학습 안정성이나 어느 항이 지배적인지는 입증하지 않는다. 재개 후 같은 iteration 구간의 `Episode_Reward/object_tilt_penalty`, `Episode_Reward/object_displacement_penalty`, `Episode_Reward/object_acceleration_penalty`를 비교한다. 세 항의 절댓값 합에 대한 비중을 계산할 수 있지만, 정책 행동이 재학습으로 바뀌므로 과거 v1 run의 내부 비중을 소급 확정하는 수치는 아니다.

원본 `logs/TEMP` checkpoint·event의 이동·수정·삭제, `logs/rsl_rl` 정리, 새 학습은 수행하지 않았다.
