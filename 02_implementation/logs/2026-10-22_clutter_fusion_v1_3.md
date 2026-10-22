# Fusion v1_3 — point 기반 선형 커리큘럼

[로그 목록](README.md) · [환경 구성](../environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_3_ENVIRONMENT.md) · [등록·실행](../08_ACTIVE_ENVIRONMENTS.md)

2026-10-22 사용자 확인: v1_1 기반 새 v1_3. 중복된 Wrench 구간은1000까지1000N/100Nm,5000에서500N/50Nm,10000에서100N/10Nm,20000에서5N/0.5Nm로 확정했다. 기준 HEAD `397399c415b999b256df100ab85a2cb09aad802c`. 기존 v1_1_1·v1_1_2 구현과 사용자 문서 변경을 보존했다.

사용자는 v1_1_2에서 느리지만 밀기가 시작됐다고 보고했다. 이는 가속도 비용의 영향에 대한 관찰이며 이번 작업에서 인과관계나 학습 성과를 독립 검증하지 않았다.

## 구현

`Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3`: EnvCfg/PPOCfg는 v1_1을 직접 상속, runtime은 공용 v1_0. 독립 RewardsCfg/CurriculumCfg를 사용한다. Goal1cm 고정·fade0, 기타5개 커리큘럼·보상·종료·PPO는 유지하며 experiment 이름을 분리한다.

새 함수 `piecewise_linear_reward_threshold`는 `(iteration,value)` points를 입력받아 첫 점까지 유지, 점 사이 선형 보간, 마지막 점 이후 고정한다. 정렬된 비음수 정수 iteration과 유한 비음수 값을 검증한다. 절대 iteration만 사용하므로 복원·되감기·부분 reset에 일관되며250 단위 양자화는 없다. 기존 런타임 `set_learning_iteration`이 매 학습 iteration에서 CurriculumManager를 계산한다.

| 항목 | Points |
| --- | --- |
| 장애물 힘 N | (1000,200), (5000,100), (10000,50) |
| Wrench 힘 N | (1000,1000), (5000,500), (10000,100), (20000,5) |
| Wrench 모멘트 Nm | (1000,100), (5000,50), (10000,10), (20000,0.5) |
| 가속도 m/s² | (2000,100), (5000,20), (10000,10), (20000,5) |

보상 초기값은 각 첫 point와 동일하다. 1000/2000에서 아직 초기값이며 다음 iteration부터 연속 선형 감소한다. 보상17·커리큘럼9·종료6항이다.

## 실행과 검증

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train_resilient.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3 \
  --num_envs 2048 --headless --max_iterations 90000
```

- 전체 CPU 검사: `env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests` — **586 passed, 3 warnings (28.35s)**. 기존 ONNX deprecation 경고3개다.
- 네 커리큘럼의 실제 CFG를 읽어 초기값·시작 직전·각 point·구간 첫1회·중간값·끝 직전·최종 이후·역순 복원·부분 reset을 확인했다. 다른 보상/커리큘럼 유지, 환경 등록·부모·PPO 변경 범위, 잘못된 points 거부를 확인했다.
- Sim 실행은 허용되었으나 순수 설정·함수 변경이라 CPU 검증으로 마쳤다. IsaacLab·Sim 애플리케이션·GPU probe·학습·play는 실행하지 않았으며 접촉 회피 개선은 미검증이다.
