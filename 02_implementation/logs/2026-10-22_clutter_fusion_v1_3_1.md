# Fusion v1_3_1 — Goal 반경·접촉 fade width 선형 커리큘럼

[로그 목록](README.md) · [환경 구성](../environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_3_1_ENVIRONMENT.md) · [등록·실행](../08_ACTIVE_ENVIRONMENTS.md)

2026-10-22 사용자 요청. 기준 HEAD `7588005eb3113cb1bae1e7023e6449331412c91b`. 기존 문서 변경을 보존했다. v1_3을 직접 상속하는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3_1`을 추가했다. Runtime은 공용 v1_0, 보상·커리큘럼은 독립 CFG이며 PPO는 v1_3 상속 후 experiment 이름만 분리한다.

## 변경

Goal hold radius points: (5000,0.02),(10000,0.01),(20000,0.005)m. Hand contact fade width points: (5000,0.001),(10000,0.01)m. 첫 point까지 유지·매 iteration 선형 보간·마지막 point 이후 고정한다. 보상 초기값도 각 첫 point와 일치한다.

접촉 보상은 live Goal hold 반경과 live fade width를 사용한다. 7500에서는 반경0.015m·폭0.0055m다. checkpoint 복원·되감기는 절대 iteration에서 다시 계산한다. Goal progress 자체 tolerance는 기존1cm이며 변경 대상이 아니다. 나머지 보상·기존9개 커리큘럼·종료·물리·관측·PPO는 유지한다. 보상17·커리큘럼11·종료6항이다.

## 실행

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train_resilient.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3_1 \
  --num_envs 2048 --headless --max_iterations 90000
```

## 검증

`env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests` — **589 passed, 3 warnings (24.41s)**. 경고는 기존 ONNX deprecation이다.

실제 CFG와 선형 함수, 실제 hand_contact_any를 연결한 CPU 테스트에서5000 직전/당일/직후·7500·10000 직전/당일·15000·20000·최종 이후·7500 복원·0 되감기를 확인했다. 각 시점의 반경 안/감쇠 중간/감쇠 밖에서 alpha0/0.5/1을 검증했다. 부모 대비 다른 보상·커리큘럼이 동일한지, 등록·상속·PPO 변경 범위도 확인했다.

Sim 실행은 허용되어 있으나 파라미터와 기존 함수 조합 변경이라 CPU 검증으로 마쳤다. IsaacLab·Sim 애플리케이션·학습·play는 실행하지 않았다. 학습 성능·실제 물리 동작은 미검증이다.
