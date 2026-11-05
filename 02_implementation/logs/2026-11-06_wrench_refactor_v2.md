# Refactor-v2: 시작점 기준 변위 코사인

2026-11-06 후속 정정: 아래는 당시 v1 기반 v2 기록이다. 현재 v2는 v0 기반으로 교체되었으며 [정정·v3 기록](2026-11-06_wrench_refactor_v2_fix_v3.md)이 최신이다.

2026-11-06. [환경 계약](../environments/WRENCH_REFACTOR_V2_ENVIRONMENT.md).

## 요청·결정

v1 직접 상속한 v2의 거리 보상에 signed cosine을 추가한다. 순간 속도 방향으로 구현하려던 해석은 사용자의 후속 지시로 폐기했다. 최종 벡터는 월드 XY에서 시작점→목표점과 시작점→현재 타겟점이다. 누적 변위 방식은 순간 접촉 진동에 덜 민감하지만 시작점 근처 진동에는 민감하고 후퇴·overshoot를 직접 음수화하지 않는다는 점을 설명했다.

기준 root commit은 a173240d80bdcd5f7567e36cab814480472a2d26. 시작 시 코드 작업트리는 깨끗했고 문서 submodule에 기존 변경이 있었다. 사용자 변경·학습 로그는 보존했다.

## 변경 전후·전체 대조

| 대상 | v1 | v2 |
| --- | --- | --- |
| EnvCfg 직접 부모 | v0 | v1 |
| target_goal_distance 함수 | contact_gated_goal_distance | displacement_cosine_goal_distance |
| 거리 weight/params | 25 / scale0.05, threshold0.01 | 동일 |
| target_contact | None | 동일 |
| 나머지 보상11개·Scene·Action·Observation·Command·Event·Termination·Curriculum·sim | v1 구성 | 동일 |
| runtime | WrenchRefactorEnv | 동일 |
| PPO | v1 | experiment_name만 inspire_wrench_refactor_v2 |

기존 역할별 파일에 v2 클래스·함수·Gym 등록을 추가했다. 기존11개 클래스/함수 정의를 HEAD AST와 대조하여 모두 불변임을 확인했다. 실제 Isaac Lab에서 전체 EnvCfg.to_dict 비교는 거리 callable 한 개만 차이임을, PPO 전체 비교는 experiment_name만 차이임을 검증했다. 부모 인스턴스가 자식 구성으로 바뀌지 않음을 확인했다. 새 함수는 runtime의 부분 reset별 초기 위치 버퍼를 읽으며 별도 상태나 reset 로직을 추가하지 않는다.

## 검증

CPU 회귀180개 통과(28.52초). Refactor와 Wrench/v0_1/v0_2/v0_3/v1, tactile projection, clutter wrench 테스트를 실행했다. 새 검사는 ±정방향,45/90/135도,0변위,0목표벡터,overshoot,NaN/Inf,접촉 상실·높이 제한과 v1 최종 보상 구성 보존을 확인한다.

첫 실행에서6개 실패했다. 테스트 fixture의 get_command가 호출마다 새0텐서를 반환하는데 지역 텐서만 수정한 문제, 그리고 to_dict가 callable을 문자열로 직렬화하는데 기대값에는 함수 객체를 넣은 문제였다. 테스트 goal을 고정 반환하도록 수정하고 직렬화끼리 비교한 뒤180개 통과했다. 실제 Sim 첫 실행의 설정 비교도 같은 직렬화 문제로 중단되어 수정 후 재실행했다. 환경 보상 로직 수정으로 실패를 우회하지 않았다.

재현 명령은 workspace 루트 기준이다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench.py src/inspire_sweep_baseline/tests/test_wrench_v0_1.py src/inspire_sweep_baseline/tests/test_wrench_v0_2.py src/inspire_sweep_baseline/tests/test_wrench_v0_3.py src/inspire_sweep_baseline/tests/test_wrench_v1.py src/inspire_sweep_baseline/tests/test_tactile_projection.py src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B src/inspire_sweep_baseline/tests/_wrench_refactor_probe.py --task Inspire-Wrench-Refactor-v2 --num_envs 32 --output outputs/wrench_refactor_validation/v2_gpu
```

GPU는 sandbox 밖에서 승인된 실제 CUDA 접근으로 수행하며 GUI32환경,seed42다. 최종 결과는 후술한다. 학습·정책 성능·v2 룰 기반 좌우 밀기 완료율은 검증하지 않았다. 상속된 reset의 이전 물리 검증과 새 보상으로 학습 성공을 구분한다.

최종 GUI32환경 검증 통과: 전체 설정/PPO 비교, 선반30kg·Hand790g readback, 관측74/74/64/64,17물체, 부분 reset 시 다른 환경 보존, 커리큘럼8지점에서 reset 및 각36step(총288step) 유한 관측/보상, 물성·크기 불변을 확인했다. 실행 측정61.24초, reset98–182ms. 산출물은 workspace의 `outputs/wrench_refactor_validation/v2_gpu/probe_32.json`, `v2_gpu_launch.log`, `v2_cpu_tests.log`다. Kit에서 다른 프로세스의 kvdb lock, Fabric 시각화 prototype/path 경고가 있었으나 검사 assertion은 통과했다. GUI 성공은 새 코사인의 학습 효과를 입증하지 않는다.

문서 수식5파일 및 양쪽 저장소 diff 공백 검사 통과. 링크 검사253개 중 새 링크 오류는 없고, 기존 패키지 README의 FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md 링크 한 개가 누락된 상태임을 확인했다. 이번 범위 밖의 기존 링크는 수정하지 않았다.
