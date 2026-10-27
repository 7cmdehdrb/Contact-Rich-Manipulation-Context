# V4에 정상 V3 run의 공통 파라미터 적용

[로그 안내](README.md) · [원인 비교 기록](2026-10-15_omni_v4_early_termination.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md#omni-v4-종료-기준-완화와-pushing-속도-비용)

기록일: 2026-10-15. 사용자가 제공한 `2026-10-15_16-53-58_height_gated_xy_reach` run에서 적용할 수 있는 파라미터를 `InspireSweepOmniV4EnvCfg`에 코드 수준으로 반영했다. Workspace 기준 commit `4e860134b6def3ec569892e1ce353142b82d1608` 및 기존 미커밋 V4 구현·사용자 변경을 기준으로 작업했다. 제공 run·checkpoint와 기존 작업트리는 보존했다.

## 적용 범위

대상 Gym ID는 `Isaac-Inspire-Sweep-Omni-v4`, 설정은 `InspireSweepOmniV4EnvCfg(InspireSweepOmniV3EnvCfg)`다. Runtime `InspireSweepEnv`, runner `InspireSweepPPORunnerCfg`는 그대로다.

| 항목 | 적용 결과 |
| --- | --- |
| `terminations.hand_velocity.params.threshold` | 작업 시작 시 코드의 1.5를 **5.0 rad/s**로 변경. 제공한 V3의 저장 YAML 값과 일치 |
| Arm 제어 | 기본 관절각 + `0.5 × action`, 같은 6개 Arm 관절·actuator를 유지 |
| 관측 | Actor/Critic 41D·8D action, 기존 noise와 센서 입력 유지 |
| 기본 주기·reset | sim dt 0.01 s, decimation 2, episode 10 s, 스폰·물성·명령 상속 유지 |
| 접근·목표 보상 | 높이 조건부 XY reaching +30, 목표 진행 +40과 기존 보조 비용 유지 |
| V4 전용 조건 | `push_fast=0.5`, 외곽·성공 종료 비활성, pushing 속도 비용 weight −0.05 유지 |

제공 V3와 로컬 V4의 저장 설정 전체 비교에서 유효 공통 파라미터 차이는 Arm 속도 threshold 5.0 대 3.0이었다. 머신별 로그·USD 절대경로는 이식하지 않는다. 물체 속도 종료·선반 외곽·추가 비용은 사용자가 앞서 요청한 V4 고유 동작이므로 원격 V3 값으로 되돌리지 않았다. 현재 V4 소스의 Arm 값은 사용자가 후속 변경한 1.5였으며, 이번 요청에 따라 명시적으로 5.0으로 override했다. V1·V2·V3의 기본값은 변경하지 않았다.

기존 Arm/Hand raw action 변화량·실제 관절속도 제곱합 네 비용과 −0.03/−0.03/−0.03/−0.01 계수는 유지한다. 이번 작업은 환경 파라미터 적용이며 pretrained weight·optimizer·학습 iteration을 기본 설정에 넣는 작업이 아니다.

## 코드와 문서 변경

`omni_env_cfg.py`의 V4 threshold 및 출처 주석, `test_omni_configuration.py`의 기대값과 경계 검사를 수정했다. 패키지 README와 활성 환경의 V4 값·적용 출처·실행 안내도 갱신했다. 실행 명령은 기존 V4와 같으며 새로 시작한 프로세스부터 5.0이 적용된다. 이미 실행 중인 학습 프로세스나 저장된 과거 run 설정은 변경하지 않는다.

## 실제 검사

Workspace 루트에서 실행:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py \
  src/inspire_sweep_baseline/tests/test_dex_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_events.py
```

결과: **94 passed in 3.33s**. 실제 Arm 속도 4.0·5.0은 허용하고 5.001은 종료하며, Hand 고속 관절은 이 Arm 종료 판정에 포함되지 않는지 검사한다. 기존 V3와 설정 격리, V4 물체 속도 비용·0.5 종료 경계와 공통 비용도 회귀 검사한다.

문서 submodule 루트에서 실행:

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-15_omni_v4_saved_parameters.md \
  ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external \
  02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-15_omni_v4_saved_parameters.md \
  ../../src/inspire_sweep_baseline/README.md
git diff --check
```

Workspace에서도 `git diff --check`를 수행한다. 새 학습·checkpoint 재생·GPU 물리 비교는 수행하지 않았으며, 변경으로 실제 학습이 개선됐다는 결과는 아직 없다.

문서 검증 결과: 변경 Markdown 4개 수식 검사 통과, 해당 파일 링크 검사 errors=0. Workspace와 문서 submodule의 `git diff --check` 모두 통과했다.
