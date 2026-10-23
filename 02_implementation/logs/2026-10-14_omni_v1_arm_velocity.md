# Omni v1의 Arm 속도 종료 기준 변경

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [이전 run 진단](2026-10-14_omni_immediate_termination.md)

기록일: 2026-10-14. 사용자 요청에 따라 Arm 속도 종료 기준을 1.0에서 2.0 rad/s로 올린 별도 v1 환경을 추가했다.

## 구현과 계약

Workspace 기준 commit은 `e54ae15bca563cd602b85dbf61f9c594a59a438f`다. 기존 `.aws` 삭제, 미추적 run 폴더 및 이전 진단 문서 변경을 보존했다.

- Gym ID: `Isaac-Inspire-Sweep-Omni-v1`.
- Runtime: `InspireSweepEnv → ManagerBasedRLEnv`.
- Cfg: `InspireSweepOmniV1EnvCfg → InspireSweepOmniEnvCfg → InspireSweepEnvCfg → ManagerBasedRLEnvCfg`.
- [omni_env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_envs.py)의 v1 `__post_init__`에서 부모 초기화를 수행하고 `terminations.hand_velocity.params["threshold"] = 2.0`을 적용한다.
- [등록 코드](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py)는 Baseline과 같은 `InspireSweepPPORunnerCfg`를 사용한다. 학습 시 CLI로 `inspire_sweep_omni_v1` 폴더를 지정한다.
- v0 기준은 1.0 rad/s를 유지한다. 이름이 `hand_velocity`인 term은 Arm 6개를 검사하며 경계값 2.0 rad/s는 허용하고 초과할 때 종료한다.
- Actor/Critic 41D(현재 물체 GT 포함), Arm Joint Position 6D + Hand 2D, 50 Hz/10초, 중앙 스폰 반경 2 cm/전방향 목표 최대 15 cm, 물성·보상·나머지 종료 조건을 상속한다. 속도 보상의 정규화 기준 1.0 rad/s와 물리 actuator 속도 제한은 변경하지 않았다.

학습·기존 checkpoint 재생 명령은 [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)에 기록했다. 새 등록만으로 별도 PPO 폴더 기본값이 생성되는 것은 아니다.

## 실제 실행한 검증

Workspace 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_task_contract.py \
  src/inspire_sweep_baseline/tests/test_configuration_contract.py
```

결과: **20 passed**.실제 Isaac Lab `configclass` 의미를 사용하는 CPU 구성 검사로 v1 생성 후에도 기존·새 v0 인스턴스의 기준이 1.0임을 확인했다. 구성된 production callable에서 1.5/2.0 rad/s는 v1에서 통과하고 ±2.001 rad/s는 종료하며, 빠른 손가락은 Arm 검사에 포함되지 않음을 확인했다. Gym 등록·Cfg entry point·PPO 연결과 기존 계약도 검사했다.

문서 submodule에서 변경 문서의 `check_markdown_math.py`(3개 파일 통과), `check_document_links.py --check-external`(errors 0), `git diff --check`(통과)를 실행했다. Workspace `git diff --check`도 통과했다.

## 미검증 범위

현재 머신은 앞선 진단에서 NVIDIA 드라이버 통신 실패가 확인됐다. Isaac Sim 생성·GPU train/play·새 정책 학습은 실행하지 않았다. 2.0 rad/s로 변경했다는 사실이 첫 스텝 종료 해소 또는 기존 `model_4100.pt`의 성공을 입증하지 않는다.
