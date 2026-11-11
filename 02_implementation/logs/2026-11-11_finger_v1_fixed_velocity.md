# Finger-v1 팔 속도 종료 고정과 비용 복구

2026-11-11. [현재 환경 문서](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md)

## 요청·변경 전후

사용자는 Finger-v1의 팔 종료 커리큘럼 삭제·1.0rad/s 고정·팔 속도 비용−0.03 및 문서 갱신을 요청했다. 새 ID 없이 기존 환경에 직접 적용했다.

| 항목 | 이전 | 현재 |
| --- | --- | --- |
| 팔 속도 종료 임계값 | 초기2rad/s,2000–5000 iteration에1rad/s까지 감소 | 처음부터1.0rad/s 고정 |
| `arm_joint_velocity_threshold` | 250 iteration 간격 감소 | None |
| `arm_joint_velocity.weight` | −0.06 | −0.03 |

종료 함수는 변경하지 않아 팔 관절 하나라도 속도 절댓값이1.0rad/s를 초과하면 실패 종료한다. 정확히±1.0rad/s는 이 조건으로 종료하지 않고, 손 관절은 제외한다. 물리 속도 제한은 변경하지 않는다.

## 영향과 최종 대조

역할별 `mdp/rewards/sweep_simple.py`, `mdp/terminations/sweep_simple.py`, `mdp/curricula/sweep_simple.py`의 Finger-v1 설정만 변경했다. 기존 상속에 따라 Finger-v2, Semi-Prof-v0, Finger-Raw-v1/v2, Semi-Prof-Raw-v0에도 적용된다. Raw의 팔 비용은 이미−0.03이므로 동일하고 종료 일정만 고정으로 바뀐다.

Finger-v0·Finger-v0-Test·Finger-v0-Wrench는 변경하지 않는다. 다른 보상·DeadZone/보상 커리큘럼·액션 Clip·Last Action·Gaussian/PPO·후퇴 게이트·성공 조건·Scene·reset은 유지한다. 원환경/Raw의 속도 비용 차이는 이제 없지만, 실행 Clip·관측·action-rate 입력 차이는 유지한다. 과거 checkpoint를 기존 ID로 play해도 종료/비용은 이번 수정값을 사용한다.

전체 EnvCfg 대조와 부모 불변성 검사에 현재 계약을 반영했다. 기존 일정9조건 테스트를6개 영향 환경의 고정 임계값·비용·커리큘럼 비활성·속도 경계/손 제외 검사로 교체했다. 따라서 테스트 개수 감소는 검사 삭제 사고가 아닌 검증 대상 변경이다. None이 된 커리큘럼을 수정하던 두 격리 검사는 종료 임계값 변경을 통한 격리 검사로 바꿨다.

## 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_wrench.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_semi_prof.py \
  -q -p no:cacheprovider --tb=short
```

**65 passed in11.87s**. 관련 전체 구성·부모 보존·6개 영향 환경의 경계 판정·기존 제어 및 보상 회귀 통과. 문서 링크·수식·diff 공백 검사 수행. GPU/PhysX 및 실제 학습은 미검증이며 학습 로그·checkpoint는 변경하지 않았다.
