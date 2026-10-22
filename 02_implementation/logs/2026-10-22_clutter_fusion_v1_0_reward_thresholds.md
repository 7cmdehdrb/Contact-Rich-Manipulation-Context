# Fusion v1_0 — 접촉 감쇠 폭·Goal 반경·가속도 무료 기준 수정

[개발 로그 목록](README.md) · [현재 환경 설명](../environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_0_ENVIRONMENT.md) · [버전 비교](../environments/CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md)

2026-10-22 사용자 요청으로 같은 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0`을 수정했다. Workspace 기준 HEAD는 `3bf14a91e5070ec987d02cf1498052a21275b48c`이며 기존 문서 변경·PLAN2.md를 보존했다. 환경 ID·상속 구조는 변경하지 않는다.

## 변경 계약

| 항목 | 이전 | 현재 |
| --- | --- | --- |
| 접촉 alpha 전이 폭 | r부터 r+3cm | r부터 r+1.5cm |
| Goal hold 시작 반경 | 0.05m | 0.03m |
| Goal hold 일정 | 1000부터500마다−0.01m, 최종0.01m | 시작·간격·감소량·최종 유지 |
| Goal 최종 도달 | 2500 | 1500 |
| 가속도 무료 기준 시작 | 0.3m/s² | 1.0m/s² |
| 가속도 첫 변경·간격 | 1000·250 | 유지 |
| 가속도 감소량·최종 | −0.01·0.05m/s² | −0.02·0.1m/s² |
| 가속도 최종 도달 | 7000 | 12000 |

Alpha는 `clamp((d-r)/0.015,0,1)`이다. d≤r에서0, r+0.75cm에서0.5, r+1.5cm 이상에서1이다. r은 계속 실제 Goal hold term에서 읽으므로 해당 curriculum과 즉시 동기화된다.

Goal 반경은0~999에서0.03m, 1000~1499에서0.02m, 1500부터0.01m다. 가속도 기준은1000에서0.98, 1250에서0.96, 2500에서0.86, 11999에서0.12, 12000부터0.1m/s²다. 최종값에서 멈추고 checkpoint iteration으로 재계산하며 rewind도 가능하다.

Reward CFG의 초기값과 Curriculum CFG의 start를 함께 수정했다. 접촉·가속도 callable의 기본값도 각각0.015와1.0으로 맞췄다. PhysX 직접 가속도·가속/감속 대칭·지수 함수·물체당 raw 상한100·weight는 유지했다. Goal progress의 고정1cm tolerance도 유지했다. 물체 배치·관측·종료는 수정하지 않았다.

## 검증

Workspace 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  -q -p no:cacheprovider src/inspire_sweep_baseline/tests
```

**551 passed, 기존 ONNX DeprecationWarning3개, 28.31초.** 관련 CFG·보상 검사34개도 별도 통과했다. 새 초기값·첫 변경·최종 직전/직후·90000 clamp·rewind, 부분 env ID 호출과 현재 Goal 반경에 따른 alpha0/0.5/1을 확인했다. 가속도 norm·가속/감속 대칭·상한 검사도 새 callable 기본값에 맞춰 통과했다.

실제 GPU probe의 기대값도 새 일정과1.5cm 감쇠로 갱신했으나 이번에는 GPU 실행·PPO 학습을 재실행하지 않았다. 변경은 기준 수치와 일정이며 CPU 검증을 실제 물리·정책 성능 검증으로 해석하지 않는다. 환경 설명·버전 비교·활성 환경·패키지 README를 현재 수치로 갱신하고 문서 수식·링크와 `git diff --check`를 검사했다.

## 후속 수정: 0 폭으로 감쇠 비활성화

사용자 요청에 따라 `hand_contact_any`는 `goal_contact_fade_width=0.0`일 때 alpha=1로 처리한다. Goal 설정·거리 조회와 나눗셈을 생략하며 접촉력 임계값, 유한 센서 값, fresh 조건은 유지한다. 양수의 기존 감쇠와 기본 인자는 유지하며 음수·NaN·Inf는 거부한다.

검증: `env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_rewards.py` — 31 passed (1.71s). 0 폭의 접촉 조건, 잘못된 폭, 기존 양수 감쇠·커리큘럼 동기화를 확인했다. IsaacLab·Sim과 학습은 실행하지 않았다.
