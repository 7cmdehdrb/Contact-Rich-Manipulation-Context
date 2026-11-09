# Relative-IK-v0_2_2_2-Test: 역방향 거리 페널티 추가

## 요청과 의도

v0_2_2_1-Test를 직접 상속하고 Refactor Relative 계열의 역방향 거리 페널티를 기존 weight의 2배로 추가한다. 사용자는 최초의 “감소한 거리” 표현을 **목표에서 멀어진 거리(기존 방식)**로 명시적으로 정정했다. 처음부터 역방향으로 미는 행동과 목표에 도달한 뒤 계속 밀어 벗어나는 행동을 억제하려는 실험이다. 효과는 아직 검증하지 않았다.

기준 커밋은 `e7fcb88395da4a0db7139aa3d8a9337d946a3473`이다. 작업 시작 시 v0_2_2_1 추가 코드 및 문서 서브모듈의 미커밋 변경이 있었으며 보존했다.

## 등록과 변경 계약

- Gym ID: `Inspire-Wrench-Refactor-Relative-IK-v0_2_2_2-Test`.
- EnvCfg: `WrenchRefactorRelativeIKV0_2_2_2TestEnvCfg`, `WrenchRefactorRelativeIKV0_2_2_1TestEnvCfg` 직접 상속.
- runtime: 부모와 동일한 `WrenchRefactorRelativeIKV0_2TestEnv`.
- RewardsCfg: 부모 직접 상속, `target_inverse_distance` 1개 추가.
- PPO: `WrenchRefactorRelativeIKV0_2_2_2TestPPORunnerCfg`, 부모 직접 상속. experiment_name만 `inspire_wrench_refactor_relative_ik_v0_2_2_2-Test`로 변경.

기존 `mdp/reward_functions/wrench_refactor.py`의 `RelativeInverseDistance`를 수정 없이 재사용한다. 참조 `WrenchRefactorRelativeRewardsCfg.target_inverse_distance`의 weight -12.97을 두 배인 **-25.94**로 설정한다.

현재 목표와 물체의 XY 거리에서 이전 스텝의 XY 거리를 빼고 양수 부분만 사용한다. 함수는 이를 step_dt로 나누므로 RewardManager의 dt 곱까지 적용한 실제 스텝 보상은 다음과 같다.

```text
-25.94 × max(현재 XY 목표 거리 - 이전 XY 목표 거리, 0)
```

가까워지거나 같은 거리를 유지하면 0이다. 멀어짐 1cm는 -0.2594이며 목표 3cm 반경 안에서도 적용한다. 접촉·EEF 높이 조건은 이 페널티에 없다. Z 이동은 거리 계산에 포함하지 않는다. 같은 스텝 중복 호출은 캐시하고 부분 reset은 선택 환경의 이전 위치를 갱신하여 reset 이동을 벌점으로 부과하지 않는다. 기존 코드와 동일하게 두 위치 모두 현재 목표를 기준으로 계산한다.

접촉 보상은 2-of-3, 1회 불인정 카운트 초기화, EEF 높이 15cm 미만, 상한 10, weight 0.1을 유지한다. 기존 goal_distance 및 goal_hold를 포함한 다른 보상·Scene·Command·Event·reset·관측·액션·종료·커리큘럼·Metrics는 부모와 동일하다. 역방향 항의 별도 커리큘럼은 없다.

이 페널티는 두 제어 시점 사이의 목표 거리 순증가를 측정한다. 한 스텝 사이 목표를 지나쳤더라도 이전보다 거리가 작으면 벌점은 없으며, 경로상의 모든 목표 통과를 탐지하거나 행동을 강제로 금지하는 것은 아니다.

## 실행과 검증

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-IK-v0_2_2_2-Test --num_envs 2048 --headless

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench_refactor_relative.py -q -p no:cacheprovider

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python -B src/inspire_sweep_baseline/tests/_wrench_refactor_relative_ik_test_probe.py --headless --num-envs 4 --inverse-distance-child --output outputs/relative_ik_v0_2_2_2_test_validation
```

학습 명령은 실행 안내이며 PPO 학습·장기 행동 개선은 미검증이다.

CPU 최종 140개 통과(12.18초). 최초 검사에서는 새 테스트의 기대값 float32와 fixture float64가 달라 1개 실패했고, 기대값 dtype을 fixture에 맞춘 뒤 위 전체 검사를 재실행했다. 실제 역방향 이동·목표 접근·목표 도달 후 1cm 초과 이동·Z만 변경·weight 두 배 및 부모 보존을 검사했다. 기존 함수의 중복 호출·부분 reset·dt 상쇄 회귀 검사도 포함한다.

GPU 4환경·120step 통과. 전체 EnvCfg/PPO 대조에서 부모와의 차이는 역방향 보상 추가 및 experiment_name뿐이었다. 부모 설정 보존, 실제 등록·관절 제한·reset/부분 reset·유한 관측/보상·Metrics를 확인했다. 활성 보상은 16개, 종료 4개, 커리큘럼 10개다. 결과는 `outputs/relative_ik_v0_2_2_2_test_validation/result.json`, stdout은 `/tmp/ik_v0222_probe.log`다.

문서 4개 수식 및 코드/문서 diff 공백 검사 통과. 링크 검사 349개 중 기존 README의 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 1건은 작업 범위 밖의 기존 문제로 보존했으며 새 링크 오류는 없다.
