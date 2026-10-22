# Fusion v1_1_1 — 가속도 실험 분기

[로그 목록](README.md) · [환경 구성](../environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_1_1_ENVIRONMENT.md) · [등록·실행](../08_ACTIVE_ENVIRONMENTS.md)

2026-10-22 사용자 요청. 기준 HEAD `397399c415b999b256df100ab85a2cb09aad802c`. 기존 문서 변경을 보존했다. v1_1에서 Goal1cm·fade0·가속도100→5(1000~20000, 주기250)를 유지하고 장애물 힘과 wrench 허용치만 매우 크게 고정한 실험 분기다. 사용자 표현의 큰 v1 수치는 현재 v1_0의2000N 및5000N/500Nm로 해석했다. 이 값은 고정하며 해당 커리큘럼은 제거했다.

EnvCfg/PPORunnerCfg는 v1_1을 상속하고 보상·커리큘럼은 독립 클래스로 선언했다. Runtime은 공용 v1_0, task는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1_1`이다. 보상17·커리큘럼6·종료6항. PPO는 experiment 이름만 변경한다. 다른 속도·변위·기울기 비용·종료 조건은 유지한다. 부모 코드와 기존 task는 변경하지 않았다.

가속도 일정은 시작1000에서 첫 감소하며20000에서 정확히5가 된다. 절대 iteration 기반 함수로 checkpoint 복원·되감기가 가능하다. 이 조건에서 실패해도 가속도100의 인과관계가 입증되지는 않는다. 특히1000 이후에는 기준이100보다 낮아지고 다른 비용도 활성화되어 있다. 가속도 비용을 제외한 대조군과 비교하는 것이 더 직접적이나, 요청하지 않은 대조 환경은 추가하지 않았다.

## 실행

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train_resilient.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1_1 \
  --num_envs 2048 --headless --max_iterations 90000
```

## 검증

- `env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_variants.py src/inspire_sweep_baseline/tests/test_termination_debug.py` —16 passed (1.23s).
- 실제 설정 AST를 비교하여 변경한 두 보상 외의 항이 동일하고, 해당3개 커리큘럼만 제거됐으며 고정 힘 값을 다른 커리큘럼이 덮어쓰지 않는지 확인했다. 가속도 시작/첫 감소/종료 직전/최종/복원 경계와 등록·부모·PPO 구성도 검증했다.
- IsaacLab·Sim 애플리케이션, GPU probe, 학습·play는 실행하지 않았다. 학습 성능·접촉 회피 개선은 미검증이다.
- 전체 검사: `env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests` — **569 passed, 3 warnings (25.15s)**. 기존 ONNX deprecation 경고3개다.
- 변경 문서8파일 math 검사 통과, 링크 검사 오류0, 루트·문서 저장소 `git diff --check` 통과.
