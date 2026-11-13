# Simple17환경 높이12cm·ForceDirection signed cosine

2026-11-13. 사용자는 직전 조사표의 모든 환경에 대해 보상 기준 높이를12cm로 고정하고, `Inspire-Sweep-Simple-Finger-ForceDirection-v0`의 힘 방향 점수를 코사인 유사도로 바꾸어 반대 방향에 음의 비용을 주도록 요청했다.

## 범위와 변경

[Simple 환경 설명서](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md)의17개 등록 ID가 범위다. 모든 활성 `eef_height_limit`를0.12로 설정했다. Prof-v2는 이미12cm라 값이 동일하다. Simple/Finger의 접촉 유지, Prof의 goal_distance/방향 이탈, Semi-Prof의 접촉 조건부 로그 거리 항을 모두 포함한다. Raw/Hard/Wrench 파생 환경도 상속으로 적용된다. 높이 관련 curriculum은 없으므로 학습 중에도 고정이다.

이는 초기 선반 표면에서 EEF까지의 수직 높이<12cm 조건이다. 정확히12cm는 인정하지 않는다. 기존 목표 내부 접촉 간주·후퇴 활성화에 따른 높이 예외는 유지한다. 일반 EnvCfg의0.14 필드는 실제 해당 보상 gate에 사용되지 않아 유지했다. 손목3/8cm·손가락2cm 충돌 조건, 후퇴 목표8cm, 목표 이동거리·OSC 회전 scale0.15는 변경하지 않았다. 과거 Relative-IK 환경에 공유되는 계산 함수의 기본15cm 인자도 유지하고 Simple cfg에서0.12를 명시했다.

ForceDirection-v0에는 별도 `cosine_force_direction` 함수를 연결했다. 물리 force sampler·평균 방식·실제 접촉 유효성·수평 최소1N·선반 평면의 현재 물체→목표 방향은 기존과 같다. 원점수는3D 합력과 XY 목표 방향의 코사인이며−1~1이다. weight0.33과 dt 적용도 유지한다.

| 각도 | 기존 ForceDirection 원점수 | 변경 후 |
| --- | --- | --- |
| 0° | 1 | 1 |
| 45° | 0.25 | 약0.707 |
| 90° | 0 | 0 |
| 135° | 0 | 약−0.707 |
| 180° | 0 | −1 |

순수 수직 힘은 수평 최소 힘 조건을 만족하지 않아0이다. 수평 성분이 있는 힘은3D 크기를 분모로 사용하므로 수직 성분이 커질수록 코사인 절댓값이 작아진다. 목표 XY<1cm에서는 기존대로 각도만 무시하고 점수1을 부여한다. 따라서 이 구간의 유효한 반대 힘도 예외 적용을 받는다. 실제 접촉·수평1N 조건은 유지한다. 성공 종료/메트릭3cm·접촉 간주1cm·raw Last Action·Runner Clip·1rad/s 종료·PPO는 변경하지 않았다.

Semi-Prof-v0와 Semi-Prof-Raw-v0의 기존 비음수 각도 제곱 점수는 유지한다. 이들의 보상 높이만12cm로 바뀐다. ForceDirection의 양의 가중치 항이 이제 음수를 반환할 수 있으므로 TensorBoard의 해당 term 누적값도 음수가 될 수 있다. 부모 Wrench 비용의 기존5% 예산 함수/설정은 유지하며 새 부호 있는 term의 누적값에 대해서도 기존 clamp_min(0) 예산 규칙을 따른다.

## 대조와 검증

수정 소스는 `mdp/rewards/sweep_simple.py`의 높이 params/ForceDirection callable 및 `mdp/reward_functions/sweep_simple.py`의 새 함수다. 기존 Semi-Prof 함수는 수정하지 않았다. Env/runtime/등록/PPO/Action/Observation/Termination/Curriculum 코드는 변경하지 않았다. 관련 테스트의 과거 환경 대비 기대값에 높이 변화만 추가하고,17개 실제 EnvCfg의 모든 높이값과 성공 반경을 검사한다.

테스트는 Simple/Finger/Finger versions/Wrench/Semi-Prof의 기존5개 파일을 아래와 같이 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_wrench.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_semi_prof.py \
  -q -p no:cacheprovider --tb=short
```

추가 검증은17환경 높이0.12·성공0.03, 접촉12cm 아래/동일/위와 목표 내부 예외, signed cosine 각도·수직힘·목표 overshoot·1cm 경계·약한 힘/NaN/비접촉이다. 기존 Semi-Prof 식과 Wrench 예산/순서 검증도 유지했다. 초기 실패는 Semi-Prof 테스트의 선반 float64·EEF float32 혼합 fixture 때문에 정확한12cm가 다르게 표현된 문제였으며, 실제 환경처럼 동일 dtype과 계산된 경계를 사용하도록 수정했다.

GPU는 RTX3090에서 아래 신규 학습 smoke를 실행했다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Simple-Finger-ForceDirection-v0 \
  --num_envs 64 --headless --max_iterations 2 --seed 42 \
  --experiment_name /home/min/7cmdehdrb/grad/outputs/finger_force_direction_v0/training \
  --run_name cosine_height12_smoke
```

실행에는 기존 env_isaaclab Python과 ROS/PYTHONPATH 해제를 사용했다.64환경·2iterations 정상 완료(exit0). [stdout](../../../../outputs/finger_force_direction_v0/train_cosine_height12_stdout.log) · [run](../../../../outputs/finger_force_direction_v0/training/2026-11-13_22-33-19_cosine_height12_smoke). 저장 YAML의 높이0.12·cosine_force_direction·방향 반경0.01·성공0.03을 확인했고 두 checkpoint의 actor/critic 가중치는 모두 유한했다.

최종 CPU79개 통과(12.74s). 변경5개 Markdown 수식·외부 경로 포함 링크·전체584개 문서 링크와 workspace/문서 저장소 git diff --check를 모두 통과했다. 별도 렌더링은 미검증이다. 모든17환경의 GPU 재학습이나 장기 수렴/정확도 개선은 미검증이다. 이미 실행 중인 프로세스에 코드/설정 변경을 실시간 적용하지는 않았다.
