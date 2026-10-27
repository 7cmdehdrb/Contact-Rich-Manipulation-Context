# V4 최대 Arm 속도 추가 페널티

[로그 안내](README.md) · [활성 환경](../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md.txt) · [기존 V4 설정 적용](2026-10-15_omni_v4_saved_parameters.md)

기록일: 2026-10-15. 사용자가 V4의 기존 페널티를 유지하면서 `hand_velocity` 종료와 같은 관절 선택·절대속도 판정에 기초한 연속 비용을 요청했다. 1.0 rad/s부터 증가하고 2.0에서 weighted −0.03이 되도록 추가했다.

## 구현과 계약

기준은 workspace commit `4e860134b6def3ec569892e1ce353142b82d1608`과 진행 중인 V4·문서 변경이다. 사용자 제공 run 디렉터리와 기존 작업트리를 보존했다. 대상은 `Isaac-Inspire-Sweep-Omni-v4`이며 runtime `InspireSweepEnv`, 설정 `InspireSweepOmniV4EnvCfg(InspireSweepOmniV3EnvCfg)`, runner `InspireSweepPPORunnerCfg`를 유지한다.

- 함수: `mdp/goal_rewards.py`의 `joint_speed_cost`.
- 새 항목: `OmniV4RewardsCfg.arm_speed_excess`.
- 대상: `_arm()`으로 이름과 순서를 명시한 Arm 6개 관절. `terminations.hand_velocity`와 같은 선택이다.
- 속도: 각 관절 실제 속도의 절댓값 중 최댓값. `any(abs(qdot)>threshold)`와 같은 최대속도 기준을 연속 비용으로 확장했다. 관절별 비용을 합산하거나 벡터 norm을 사용하지 않는다.
- 반환값: `max(v_max−1.0, 0)² / (2.0−1.0)²`.
- Weight: −0.03. 2.0 rad/s에서 weighted −0.03, 기본 0.02 s 시간 곱셈 후 −0.0006이다. `pushing_speed_cost`와 동일하게 `/step_dt` 상쇄는 하지 않는다.
- 1.0 이하는 0, 음수 속도도 동일한 크기로 계산, 2.0 이후에도 제곱 증가한다. 별도 상한 clamp는 없다.
- 기존 네 action/velocity 비용의 로컬 함수·raw 입력·실제 관절속도 제곱합 및 계수 −0.03/−0.03/−0.03/−0.01은 그대로다. 물체 속도·기울기·선반 비용과 reaching·goal도 유지한다.
- Arm 속도 종료 5.0, 물체 속도 종료 0.5, 외곽·성공 종료 비활성, 41D 관측·8D action·스폰·물성·PPO도 그대로다.

이번 변경은 `goal_rewards.py`, `omni_env_cfg.py`, 관련 기존 테스트 두 파일, 패키지 README, 활성 환경 안내와 이 로그에 반영했다. 실행 명령은 기존 V4 train/play와 같고 새 프로세스부터 적용된다.

## 실제 CPU 검증

Workspace 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py \
  src/inspire_sweep_baseline/tests/test_dex_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_events.py
```

결과: **95 passed in 3.43s**. 비연속 Arm 인덱스·Hand 제외·양/음 속도·1.0 dead zone·2.0 보정·상한 없는 제곱 증가·최대값 집계·실제 시간 기여를 검증했다. V4의 선택 관절이 종료 term과 같은지, 기존 V3 설정과 네 필수 비용이 보존되는지도 확인했다.

## 문서 검증과 미실행 범위

문서 submodule 루트에서 실행했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-15_omni_v4_arm_speed_excess.md \
  ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external \
  02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-15_omni_v4_arm_speed_excess.md \
  ../../src/inspire_sweep_baseline/README.md
git diff --check
```

결과: 변경 Markdown 4개 수식 검사 통과, 해당 파일 링크 검사 errors=0, 문서 submodule과 Workspace의 `git diff --check` 모두 통과했다. 새 시뮬레이터 실행·학습·checkpoint 재생은 수행하지 않았고, 학습 안정화·속도 억제 효과는 아직 검증하지 않았다.
