# Fusion v1_1 / v1_2 — 접촉 허용 기준과 Goal 커리큘럼 분리

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [v1_1](../environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_1_ENVIRONMENT.md) · [v1_2](../environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_2_ENVIRONMENT.md)

2026-10-22 사용자 요청으로 두 파라미터 변형을 추가했다. 기준 HEAD는 `b3b5bfdb1f1202ff47c6d21fe63583a814f21de3`다. 기존 v1_0 사용자 설정과 문서 작업을 보존했다. 접촉 회피를 완화하려는 설계이며 인과관계나 학습 개선은 입증하지 않았다.

## 구현

EnvCfg 상속은 v1_0→v1_1→v1_2다. runtime은 `ContactSweepClutterFusionV1_0Env`를 재사용한다. `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1`과 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_2`를 등록했다. 각 패키지에 EnvCfg·독립 RewardsCfg·독립 CurriculumCfg·상속 PPORunnerCfg를 둔다. 종료는 변경하지 않아 상속된 설정을 사용한다. PPO에서는 experiment 이름만 바꾼다.

v1_1: Goal hold 1cm 고정, fade width0. 장애물 무료 힘100→50N(10000), 가속도100→5m/s²(20000), wrench 힘 변화500→5N·모멘트 변화50→0.5Nm(20000). 모두1000에서 첫 감소·주기250이다. v1_2는 Goal2→1cm(5000)→0.5cm(10000), fade width1cm를 추가한다.

`staged_reward_threshold`는 각 구간의 시작·종료 iteration을 포함하는 업데이트 수로 균등 감소량을 계산한다. 장애물37회, 가속도·wrench77회, Goal첫구간17회·둘째구간20회다. 두 번째 Goal 구간은5250에서 처음 감소한다. 끝점은 정확히 최종값을 대입한다. 절대 iteration만 사용해 복원·되감기·부분 reset 호출에 일관된 설정을 제공한다.

물체 속도·장애물 변위/기울기·Arm/Hand 네 고정 비용·선반 비용과6개 종료 조건, 장애물 개수·다른 커리큘럼, 관측55+40/privileged3D·Action8D·50Hz 제어·100Hz 물리는 유지한다. 장애물 인코더와 PPO도 유지한다. Goal progress tolerance는1cm 고정이며 v1_2의0.5cm 최종 Goal hold와 별개다.

## 실행 안내

Workspace 루트에서 다음 명령을 사용한다. v1_2는 task 접미사를 바꾼다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train_resilient.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1 \
  --num_envs 2048 --headless --max_iterations 90000
```

자동 복구는 기존 launcher의 checkpoint iteration 복원·reset 순서를 사용한다. 별도 launcher 수정은 없다.

## 검증

사용자 제한에 따라 IsaacLab·Sim 애플리케이션, GPU probe, 학습·play는 실행하지 않았다. CPU pytest는 simulator 의존성을 대체하여 설정 정의와 실제 순수 Python 커리큘럼·보상 함수를 검사한다.

- 새 변형 및 보상 함수 테스트: `env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_variants.py src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_rewards.py` — 43 passed (1.54s).
- 시작 직전·첫 업데이트·구간 사이·최종 직전/당일·최종 이후·2500 복원·0 되감기·부분 환경 ID 호출을 검증했다. 등록/상속/PPO 변경 범위와 보상 변경 범위도 확인했다.
- 전체 첫 검사: 561 passed, 7 failed. 6개는 v1_0 사용자 긴급 변경 이전의 테스트 기대값, 1개는 새 ID가 빠진 runtime 목록이었다. 부모 실제 설정을 변경하지 않고 기대값/목록을 수정했다.
- 전체 최종 검사: `env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests` — **567 passed, 3 warnings (23.70s)**. 경고는 기존 ONNX export deprecation이다.
- 문서: `check_markdown_math.py` 변경10파일 통과, `check_document_links.py --check-external` 문서9파일 오류0(내부293·외부파일47 링크), 루트와 문서 저장소 `git diff --check` 통과.
- 미검증: 실제 simulator 구성·접촉 동역학·PPO 학습 성능. CPU 경계 검증은 접촉 회피 개선을 보장하지 않는다.
