# Refactor-v2 상속 정정 및 EEF 기준 v3

2026-11-06. [v2 계약](../environments/WRENCH_REFACTOR_V2_ENVIRONMENT.md) · [v3 계약](../environments/WRENCH_REFACTOR_V3_ENVIRONMENT.md).

## 요청·기준·변경 범위

사용자는 기존 v2가 v1 기반인 것이 잘못된 설정이라고 정정했다. v0/v1은 맞으므로 보존하고, v2는 v0 직접 상속·접촉 보상 별도·거리 보상×누적변위 cosine으로 수정한다. v3는 수정된 v2를 직접 상속하고 이전 EEF task-space OSC를 복원한다. 기준 root commit은 a173240d80bdcd5f7567e36cab814480472a2d26이며, 시작 시 v2 추가 및 root OSC/최소거리5cm 변경이 있는 작업트리였다. 이번 요청 직전 소스 스냅샷을 /tmp/refactor_v2_v3_before.json에 저장하여 범위 밖 정의 불변성을 대조했다. 사용자 변경과 학습 로그는 보존했다.

| 항목 | 수정 전 v2 | 수정 후 v2 | 새 v3 |
| --- | --- | --- | --- |
| EnvCfg/RewardsCfg 부모 | v1 | v0 | EnvCfg는 v2, Rewards는 v2 그대로 |
| 거리 함수 | 현재접촉조건부 지수×cosine | v0 지수×cosine, 접촉조건 없음 | v2 그대로 |
| 거리 weight/scale | 25/0.05 | 5/0.05 | 동일 |
| 별도 target_contact | None | v0 유지(weight0.1) | 동일 |
| 활성 보상 수 | 12 | 13 | 13 |
| OSC | root 공통 | 동일 | WrenchRefactorOSCAction, EEF task frame |
| PPO | 수치 동일, v1 부모 | 수치 동일, v0 부모 | 수치 동일, v2 부모 |
| experiment_name | inspire_wrench_refactor_v2 | 동일 | inspire_wrench_refactor_v3 |

v3 EnvCfg의 post-init에서 부모를 실행한 뒤 arm_action.class_type 한 개만 바꾼다. 이전 EEF 전용 클래스의 매 정책step task-frame clone, offset Jacobian 및 link-origin 속도 보정도 함께 선택된다. 오른손 USD·Wrist3·EEF offset·촉각/F/T·Hand mapping·질량·목표 최소5cm와 모든 나머지 Manager 설정은 상속한다. 새 Gym ID는 Inspire-Wrench-Refactor-v3이며 runtime은 공통 WrenchRefactorEnv다.

## 검증

CPU 회귀181개 통과(23.69초). v2 보상 설정을 v0 전체와 비교하여 거리 callable만 다름을 확인했다. 별도 접촉 보상 유지·weight5·거리params 동일, 방향별 signed cosine, 무접촉·stale 센서에서도 거리 항 지급, 높이 제한과0변위/0목표벡터/NaN/Inf 처리를 검증했다. 기존 v1 현재접촉 조건 테스트는 그대로 통과했다. 기존 EEF task-frame freeze·offset Jacobian/속도 검사도 통과했다. 요청 직전 정의와 AST 대조 결과 수정 대상으로 지정한 v2 클래스3개·거리함수 외11개 기존 클래스/함수는 동일했다.

실제 Isaac Lab에서는 v0/v1/v2/v3를 모두 구성하여 전체 to_dict를 비교한다. v1←v0은 기존 접촉/거리 차이, v2←v0은 거리 callable만, v3←v2는 action class_type만 달라야 한다. 전체 PPO는 experiment_name만 다르며 부모 인스턴스도 변하지 않는지 검사한다. 실제 GUI32환경 v3 검증은 아래 결과를 따른다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench.py src/inspire_sweep_baseline/tests/test_wrench_v0_1.py src/inspire_sweep_baseline/tests/test_wrench_v0_2.py src/inspire_sweep_baseline/tests/test_wrench_v0_3.py src/inspire_sweep_baseline/tests/test_wrench_v1.py src/inspire_sweep_baseline/tests/test_tactile_projection.py src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B src/inspire_sweep_baseline/tests/_wrench_refactor_probe.py --task Inspire-Wrench-Refactor-v3 --num_envs 32 --output outputs/wrench_refactor_validation/v3_gpu
```

v2/v3 변경 후 RL 학습 및 룰 기반 좌우 밀기 성공률은 검증하지 않았다. 과거 v2 GUI 결과는 이전 v1 기반 보상으로 수행한 당시 결과로 보존하고 현재 v2 계약의 증거로 해석하지 않는다. v0 재구성 부록은 v0 전용 스냅샷이며 이번 요청에서 v0가 바뀌지 않아 갱신하지 않았다.

최종 GUI v3 32환경 검증 통과: 4개 버전 전체 최종 구성/PPO 차이 검사, 실제 오른손 USD·EEF offset·EEF 축 XYZ 명령 해석, 선반30kg/Hand790g, 관측74/74/64/64, 부분reset,8개 커리큘럼 지점에서 목표 최소5cm 및 각36step(총288step) 유한 관측/보상·물성불변을 확인했다. 측정38.53초,reset71.4–78.5ms. 결과는 workspace의 `outputs/wrench_refactor_validation/v3_gpu/probe_32.json`, `v3_gpu_launch.log`, `v2_fix_v3_cpu.log`다. 기존 Fabric 경고가 있으나 assertion은 통과했다. v2는 이번 검증의 전체 설정 비교 및 v3와 공유하는 보상 함수 테스트로 확인했으며 별도 GUI 실행은 추가하지 않았다.

문서 수식7파일·양쪽 저장소 공백 검사 통과. 링크269개 검사에서 새 링크 오류는 없고, 기존 README의 FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md 누락 링크 한 개만 확인했다. 기존 누락은 이번 범위에서 수정하지 않았다.
