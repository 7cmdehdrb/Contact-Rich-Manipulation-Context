# Fusion v1_1_2 — 큰 가속도 허용치 고정 실험

[로그 목록](README.md) · [환경 구성](../environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_1_2_ENVIRONMENT.md) · [등록·실행](../08_ACTIVE_ENVIRONMENTS.md)

2026-10-22 사용자 요청. 기준 HEAD `397399c415b999b256df100ab85a2cb09aad802c`. 기존 v1_1_1 작업과 문서 변경을 보존했다. v1_1을 직접 상속한 별도 분기이며 v1_1_1의 힘 허용치를 상속하지 않는다.

Goal hold1cm 고정·fade0·장애물 무료 힘100→50N(10000)·wrench 무료 변화량500→5N/50→0.5Nm(20000)는 v1_1 그대로다. 가속도 무료 기준만1,000,000m/s² 고정으로 변경하고 가속도 커리큘럼을 제거했다. 큰 값은 사용자에게 선택 근거와 함께 알렸다. 비용 자체를 제거하지 않아 NaN/Inf·초과값의 상한 처리는 유지한다. PhysX COM 가속도 norm 계산은 변경하지 않았다.

Task `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1_2`, 공용 runtime `ContactSweepClutterFusionV1_0Env`, 독립 RewardsCfg/CurriculumCfg를 사용한다. EnvCfg/PPORunnerCfg는 v1_1을 상속한다. PPO는 experiment 이름만 다르다. 보상17·커리큘럼8·종료6항이다. 자동 복구 launcher는 그대로 재사용한다.

## 실행

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train_resilient.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1_2 \
  --num_envs 2048 --headless --max_iterations 90000
```

## 검증

- `env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_variants.py src/inspire_sweep_baseline/tests/test_termination_debug.py` —18 passed (1.24s).
- 설정 AST로 v1_1 대비 가속도 무료 기준과 해당 커리큘럼 제거 외에는 동일함을 확인한다. 등록·EnvCfg/PPO 상속, 커리큘럼 덮어쓰기 부재를 확인한다. 큰 가속도 기준에서 임계값까지0, 초과량의 지수 비용, NaN의 유한 상한을 확인하는 보상 테스트를 추가했다.
- 사용자가 필요시 Sim 실행을 허용했으나 이번 변경은 파라미터·설정만이므로 CPU 검증으로 마쳤다. IsaacLab·Sim 애플리케이션·학습·play는 실행하지 않았다. 접촉 회피 개선과 실제 물리 동작은 미검증이다.
- 전체 검사: `env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests` — **572 passed, 3 warnings (23.73s)**. 기존 ONNX deprecation 경고3개다.
