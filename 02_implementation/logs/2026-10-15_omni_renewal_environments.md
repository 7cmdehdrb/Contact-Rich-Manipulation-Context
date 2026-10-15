# Omni Renewal·Dex Sweep Omni Renewal 환경 추가

[로그 안내](README.md) · [활성 환경·명령](../08_ACTIVE_ENVIRONMENTS.md#omni-renewal-환경)

기록일: 2026-10-15. 사용자가 현재 V4와 같은 기능을 기존 함수로 새 클래스에 구성하고, 이 환경을 상속해 `reaching`·`goal_distance`만 Dex 방식으로 교체한 환경을 요청했다.

기준은 workspace commit `4e860134b6def3ec569892e1ce353142b82d1608`, 문서 submodule commit `501a0936124c98921201c89ba1cd69cf706e6ce7` 및 현재 미커밋 V4 구현이다. 기존 작업트리와 사용자 제공 run·checkpoint를 보존했다. 같은 기능의 기준은 추가 Arm 최대속도 비용까지 반영한 현재 V4다.

## 구성과 코드

| Gym ID | 설정·상속 | 소스 |
| --- | --- | --- |
| `Isaac-Inspire-Sweep-Omni-Renewal-v0` | `InspireSweepOmniRenewalEnvCfg(InspireSweepEnvCfg)` | [omni_renewal_env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/omni_renewal_env_cfg.py) |
| `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0` | `InspireDexSweepOmniRenewalEnvCfg(InspireSweepOmniRenewalEnvCfg)` | [dex_omni_renewal_env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/dex_omni_renewal_env_cfg.py) |

Renewal에 이벤트·보상·종료 Cfg를 새로 명시했다. 모든 계산은 기존 로컬 MDP 함수를 재사용하며, V1–V4의 환경/보상 클래스 상속 체인을 이어 붙이지 않는다. 기하 상수와 `RealisticPhysicsEventsCfg`·물성 적용 함수를 재사용한다. 기존 V4 클래스와 기존 Dex 클래스는 변경하지 않았다.

- 두 환경의 runtime: `InspireSweepEnv(ManagerBasedRLEnv)`.
- PPO: `InspireSweepPPORunnerCfg`를 그대로 등록한다. 로그 구분은 실행 명령의 `--experiment_name`을 사용한다.
- Renewal: Actor/Critic 41D·action 8D, scene·action·command·초기 상태·센서·주기·물성·스폰과 전체 reward/termination이 V4와 동일하다.
- 보상: 높이 조건부 XY 접근 +30, 정규화한 목표 진행 +40, 네 필수 제곱합 비용, 기울기·선반·물체속도·최대 Arm 속도 비용을 유지한다. 활성 보상은 10개다.
- 종료: Arm 속도 5.0·물체 속도 0.5 초과, 낙하·전도·선반 충돌·변위·timeout 유지. 외곽·성공 종료는 비활성이다.
- Dex Renewal: `DexOmniRenewalRewardsCfg(OmniRenewalRewardsCfg)`에서 `DexReachProgress`(+30 reward/m)와 `DexPlanarGoalProgress`(+300 reward/m)만 교체한다. 두 term은 기존 `DexOmniRewardsCfg`와 함수·계수·params가 같다. 나머지는 Renewal과 동일하다.
- Dex의 reaching에는 Z gate params를 전달하지 않는다. Renewal 부모의 `__post_init__`는 보상을 수정하지 않아 Dex 보상을 덮어쓰지 않는다.

등록은 패키지 `__init__.py`에 추가했다. 패키지 README, 활성 환경의 등록 표·상속도·입출력 표·train/play 명령, 로그 색인을 갱신했다.

## 실제 검증

Workspace 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py \
  src/inspire_sweep_baseline/tests/test_dex_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_events.py \
  src/inspire_sweep_baseline/tests/test_configuration_contract.py
```

결과: **103 passed in 3.60s**. 기존 CPU harness에서 실제 configclass와 기존 MDP를 사용했다. Renewal의 전체 `to_dict()`가 V4와 일치하며 이벤트·보상·종료 term의 순서도 같음을 확인했다. Dex Renewal의 두 보상이 기존 Dex와 같고, 이 두 항을 부모 값으로 복원하면 전체 설정이 Renewal과 일치함을 확인했다.

두 새 환경의 네 필수 운동 비용 함수·계수·관절 선택, Gym ID·runtime·PPO 연결, 모든 manager params의 callable signature, 인스턴스 간·부모와 자식 간 설정 격리를 검사했다. 기존 goal·Dex·속도 비용·실패·목표 배치 회귀 검사도 통과했다. 설정 시험의 asset 노드는 CPU 대체물이므로 실제 Isaac Sim 환경 생성 검증과 구분한다.

문서 submodule 루트에서 다음 명령을 실행했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-15_omni_renewal_environments.md \
  ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external \
  02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-15_omni_renewal_environments.md \
  ../../src/inspire_sweep_baseline/README.md
git diff --check
```

결과: 변경 Markdown 4개 수식 검사 통과, 해당 파일 링크 검사 errors=0. Workspace와 문서 submodule의 `git diff --check` 모두 통과했다. 실제 GPU 환경 생성·train/play·새 성공률 평가·실물 실험은 수행하지 않았다. 실행 예시는 위 활성 환경 절에 있으며 CPU 계약 일치를 학습 성공으로 해석하지 않는다.
