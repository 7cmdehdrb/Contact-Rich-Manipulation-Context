# Omni Arm 비용을 Baseline 수준으로 복원

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [Omni 구성](../environments/OMNI_ENVIRONMENT.md) · [원인 대조](2026-10-14_omni_immediate_termination.md)

기록일: 2026-10-14. 사용자가 Arm 속도 비용과 Arm action 변화 비용을 기존 환경 수준으로 강화하도록 요청했다.

## 기준과 변경

Workspace 기준 commit은 `e54ae15bca563cd602b85dbf61f9c594a59a438f`다. 이전 v1 등록·테스트·문서 변경, `.aws` 삭제와 사용자 작업을 보존했다. 사용자 수정으로 v1 threshold가 100.0인 상태를 유지하고 docstring·현행 안내·경계 테스트를 그 값에 맞췄다. 2.0으로 생성했던 이력은 기존 로그에 보존한다.

적용 task는 `Isaac-Inspire-Sweep-Omni-v0`와 이를 상속하는 `Isaac-Inspire-Sweep-Omni-v1`이다. Runtime은 `InspireSweepEnv → ManagerBasedRLEnv`, Cfg는 `InspireSweepOmniV1EnvCfg → InspireSweepOmniEnvCfg → InspireSweepEnvCfg → ManagerBasedRLEnvCfg`다. 공통 `OmniRewardsCfg`를 변경해 두 버전에 적용한다.

| 비용 | 이전 Omni | 변경 후 | 배율 |
| --- | --- | --- | ---: |
| Arm action 변화 | −0.03 × mean(Δaction_arm²) | −0.03 × sum(Δaction_arm²) | 6배 |
| Arm 관절 속도 | −0.01 × mean(qdot_arm²) | −0.03 × sum(qdot_arm²) | 18배 |

[goal_rewards.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/goal_rewards.py)의 두 함수에 `reduction="mean"` 기본 인자를 추가하고 `sum`도 지원한다. [omni_env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/omni_env_cfg.py)는 Arm 두 항만 `sum`을 지정하며 속도 weight를 −0.03으로 변경한다. 정규화 기준은 1.0이다. Hand 두 항의 평균 방식·가중치는 유지한다. Baseline 코드도 유지한다.

Baseline action 비용은 8개 전체 합이므로 이번 변경은 그 중 Arm 6개의 기여와 일치한다. Hand 비용까지 Baseline 방식으로 바꾼 것은 아니다. RewardManager의 `step_dt` 곱셈도 유지한다. 관측 41D, Action 8D, 스폰·목표·물성·PPO·나머지 보상은 변경하지 않았다.

## 검증

Workspace 루트에서 실제 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_task_contract.py \
  src/inspire_sweep_baseline/tests/test_configuration_contract.py
```

결과: **36 passed**.새 CPU 검사에서 실제 구성된 v0/v1 reward 함수의 weighted 결과가 Baseline Arm 비용과 일치함을 확인했다. 서로 다른 부호·크기의 속도와 action, 비연속 Arm 인덱스를 사용했다. 빠른 손가락·큰 Hand 명령이 Arm 비용을 바꾸지 않음도 확인했다. 기존 Hand 평균·clip 및 정규화 함수 검사도 통과했다. v1의 사용자 지정 100.0 경계 및 v0 설정 격리 검사를 갱신해 통과했다.

문서 검증 결과: 변경 문서 수식 검사 5개 파일 통과, `check_document_links.py --check-external` errors 0, workspace와 문서 submodule의 `git diff --check` 통과.

## 실행과 미검증 범위

학습·재생 task ID와 명령은 [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)를 따른다. 새 학습은 예를 들어 다음처럼 보상 변경 run을 구분한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Sweep-Omni-v1 --num_envs 2048 \
  --experiment_name inspire_sweep_omni_v1 \
  --run_name baseline_arm_costs --headless
```

이 명령은 안내이며 이번 작업에서 실행하지 않았다. 현재 머신에서 GPU 실행이 불가능해 새 학습·재생·1스텝 종료 해소를 확인하지 않았다. 기존 checkpoint의 정책 가중치는 보상 설정 변경으로 갱신되지 않는다.
