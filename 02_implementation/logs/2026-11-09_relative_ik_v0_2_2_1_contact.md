# Relative-IK-v0_2_2_1-Test: 접촉 불인정 즉시 카운트 초기화

## 요청과 기준

사용자는 v0_2_2-Test의 최근 3스텝 중 2스텝 접촉 인정 구조를 유지하며, 누적 카운트 초기화를 5회 연속 불인정에서 1회 불인정으로 바꾸는 새 환경을 요청했다. 기준 커밋은 `e7fcb88395da4a0db7139aa3d8a9337d946a3473`이며 시작 시 문서 서브모듈 변경이 있었다. 이를 보존했다.

## 변경 의도에 대한 사용자 보충

사용자는 “후반가서 멈춰서 추가로 밀리는 현상이 많아서” 이 변경을 수행했다고 명시했다. 따라서 v0_2_2_1-Test의 의도는 단순히 접촉 유지 요구를 강화하는 것뿐 아니라, **후반에 멈춘 뒤 물체가 추가로 밀리는 현상이 자주 관찰되어 이를 줄이려는 것**이다. 이 관찰을 배경으로 2-of-3 인정 구조는 유지하면서 1회 불인정 시 카운트를 즉시 초기화하도록 강화했다.

이는 사용자가 관찰한 현상과 실험 동기의 기록이다. 추가 이동의 물리적 원인이나 이 변경의 개선 효과가 검증되었다는 의미는 아니다. 기존의 일반적인 접촉 강화 설명에 구체적인 관찰 배경을 추가했으며 코드·수치·학습 설정은 변경하지 않았다. 인계와 활성 환경 안내에도 같은 의도를 반영했다.

## 등록과 최종 차이

- Gym ID: `Inspire-Wrench-Refactor-Relative-IK-v0_2_2_1-Test`.
- EnvCfg: `WrenchRefactorRelativeIKV0_2_2_1TestEnvCfg`, 부모 `WrenchRefactorRelativeIKV0_2_2TestEnvCfg` 직접 상속.
- runtime: 부모와 같은 `WrenchRefactorRelativeIKV0_2TestEnv`.
- PPO: `WrenchRefactorRelativeIKV0_2_2_1TestPPORunnerCfg`, 부모 PPO 직접 상속. experiment_name만 `inspire_wrench_refactor_relative_ik_v0_2_2_1-Test`로 변경.
- RewardsCfg: 부모 직접 상속. `hand_contact.params.reset_after_misses=1`만 추가한다. 공통 `TargetContactMaintenance` 함수의 기본값은 5이므로 기존 환경 동작은 유지한다.

| 항목 | 부모 | 새 환경 |
| --- | --- | --- |
| 카운트 초기화 | 5회 연속 불인정 | 1회 불인정 |
| 접촉 인정 | 최근 3스텝 중 2스텝 | 동일 |
| 접촉 대상·힘 | 손–타겟, 0.01N 이상 | 동일 |
| EEF 높이 | 초기 선반 표면 위 15cm 미만 | 동일 |
| 목표 3cm 내 접촉 간주 | 없음 | 동일 |
| 카운트 상한·weight | 10·0.1 | 동일 |

원시 접촉이 한 번 끊겨도 최근 창이 2-of-3을 만족하면 인정된다. 창 판정이 불인정되는 첫 스텝에는 보상과 누적 카운트가 모두 0이 된다. 이후 다시 인정되면 카운트 1부터 시작한다. 높이 조건 불충족도 불인정이다. Scene·Command·Event·reset·Action·Observation·다른 Reward·Termination·Curriculum·Metrics는 부모 구성을 유지한다. Distance 변경이나 속도 비용 복구는 하지 않았다.

## 실행과 검증

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-IK-v0_2_2_1-Test --num_envs 2048 --headless

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py src/inspire_sweep_baseline/tests/test_wrench_refactor.py -q -p no:cacheprovider

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python -B src/inspire_sweep_baseline/tests/_wrench_refactor_relative_ik_test_probe.py --headless --num-envs 4 --strict-contact-child --output outputs/relative_ik_v0_2_2_1_test_validation
```

CPU 118개 통과(11.10초). 부모의 기존 5회 초기화 회귀 검사, 새 1회 초기화·2-of-3 유지·재접촉 시 1부터 시작, 전체 보상 설정 대조를 포함한다. 장기 학습 및 행동 개선 효과는 미검증이며 위 학습 명령은 실행 안내다.

GPU 4환경·120step 검증 통과. 실제 등록을 통한 부모/자식 전체 EnvCfg 및 PPO 대조에서 차이는 Contact 초기화 파라미터와 experiment_name뿐이고, 부모 설정 보존을 확인했다. 실제 reset·부분 reset·유한 관측/보상·Metrics·목표 점유 접촉 우회 부재도 확인했다. 결과는 `outputs/relative_ik_v0_2_2_1_test_validation/result.json`, stdout은 `/tmp/ik_v0221_probe.log`다. PPO 학습은 실행하지 않았다.

문서 4개 수식 검사 및 코드/문서 diff 공백 검사를 통과했다. 링크 검사 346개 중 패키지 README에 기존부터 있던 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 경로 1건을 발견했다. HEAD에도 존재하는 작업 범위 밖의 링크로 보존했으며 새로 추가한 링크에는 오류가 없다.
