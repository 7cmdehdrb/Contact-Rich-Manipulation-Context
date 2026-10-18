# Dex Tactile Renewal v2: 목표 유지와 일회성 성공 보상

후속 변경: 이 문서는 최초 구현 당시의 성공 종료를 기록한다. 사용자 명확화에 따라 v2와 OSC v2는 성공으로 종료하지 않으며 bonus를 한 번 지급한 뒤 timeout까지 유지하도록 [수정했다](2026-10-18_v2_goal_hold_until_timeout.md). 현행 계약은 해당 후속 로그와 활성 환경 안내를 따른다.

[개발 로그 목록](README.md) · [활성 환경 계약](../08_ACTIVE_ENVIRONMENTS.md) · [사용자 결정](../../01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md) · [패키지 실행 안내](../../../../src/inspire_sweep_baseline/README.md)

기준일: 2026-10-18. Workspace `main`, 기준 commit `10f4d0bbaed1832d3662e0b3695a34e84448a369`. 문서 저장소 기준 commit `8adbde54af951da10b2d881e5329282a40133a38`. 작업 시작 시 상위 저장소의 문서 submodule 참조 차이가 있었고 문서 내부 작업트리는 깨끗했다. 참조 차이는 보존했으며 commit·push는 수행하지 않았다.

## 요청과 구현 경계

사용자는 기존 텍타일 환경을 상속해 안정된 목표 도달의 큰 일회성 보상과 목표 위치에 연속해서 머물수록 증가하는 보상을 추가하도록 요청했다. 새 속도·지나간 위치 오차 비용은 추가하지 않는다. 이전 대화에서 배제한 액션 clipping도 도입하지 않았다.

새 task는 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2`, runtime은 공통 `InspireSweepEnv`, Cfg는 `InspireDexTactileSweepOmniRenewalV2EnvCfg(InspireDexTactileSweepOmniRenewalEnvCfg)`다. v0를 직접 상속하며 v1의 비용 상한·손목 높이·방향 제한을 적용하지 않는다. 파일은 [v2 Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/dex_tactile_omni_renewal_v2_env_cfg.py)다. Runner는 `InspireDexTactileSweepOmniRenewalV2PPORunnerCfg`로 기존 Dex Tactile runner를 상속하며 experiment 이름만 `inspire_dex_tactile_sweep_omni_renewal_v2`로 분리한다.

상속으로 유지되는 계약은 현재 물체 GT를 포함한 Actor/Critic 동일 57D 관측, 촉각 17채널·0.01 N, 손목 F/T, Arm Joint Position 6D+Hand 2D, 기존 action scale, 0.02초 제어 주기, 장면·물성·전방향 목표·reset·10초 timeout과 기존 보상/실패 종료다. 네 필수 raw Action·실제 관절 속도 제곱합 비용의 callable·그룹·계수를 유지한다. 새 속도 입력을 actor에 추가하지 않으며 최종 Blind actor나 실물 성공 판정을 구현한 것은 아니다.

## 성공과 체류 보상

`DexTactileOmniRenewalV2TerminationsCfg`는 `OmniRenewalTerminationsCfg`를 상속하여 마지막에 `StableGoalSuccess`를 추가한다. 다음 모든 조건을 0.5초 연속 유지해야 성공한다.

| 조건 | 적용값 |
| --- | --- |
| 목표 XY 위치 오차 | <0.01 m |
| 물체 XY 속도 norm | <0.02 m/s |
| 물체 기울기 | 선반 법선 기준 ≤10° |
| 지지 높이 | 최저 바닥 rim과 선반면 1.05 m 사이 오차 ≤0.01 m |
| 지지 영역 | 선반 로컬 반폭 (0.20, 0.50) m에서 물체 반경 0.04 m를 제외한 영역 내부 |
| 활성 실패 | `object_drop`, `push_fast`, `shelf_collision`, `hand_velocity`, `shelf_displacement` 모두 False |

비활성 `object_outside_shelf`는 참조하지 않는다. timeout은 기존 성공 구현대로 실패 목록에 넣지 않는다. 성공은 `time_out=False`인 종료이며, 성공 스텝의 보상 계산 후 자동 reset한다.

`DexTactileOmniRenewalV2RewardsCfg(DexOmniRenewalRewardsCfg)`는 다음 두 양의 항만 추가한다.

- `success`: 기존 `goal_rewards.success_event`의 weight +100. 함수가 step_dt를 상쇄하여 제어 주기와 무관하게 성공 종료 스텝에 +100을 한 번 지급한다.
- `goal_hold`: 새 `goal_rewards.stable_goal_hold`의 weight +20. 성공 term이 갱신한 공개 `hold_duration_s`를 `get_term_cfg("success").func`에서 읽는다. 연속 유지 시간 `h`에 대해 `min(h / hold_time, 1)`을 반환하고 RewardManager가 dt를 한 번 곱한다. 보상 조회는 성공 함수를 다시 호출하지 않아 타이머를 중복 증가시키지 않는다.

현재 주기에서는 25스텝의 유지 보상이 +0.016, +0.032, …, +0.4로 증가하며 합계 +5.2다. 성공 보너스와 합쳐 새 양의 항의 누적 합은 +105.2다. 기존 항들의 기여는 별도다. 조건이 하나라도 깨지면 유지 시간과 보상은 0이 되며, 재진입하면 처음부터 쌓는다. 부분 reset도 해당 환경만 초기화한다. 성공 즉시 종료하므로 성공 후 체류 시간을 추가로 쌓지는 않는다. +100과 최대 +20/초는 구현자가 고른 초기 실험값이며 성능 기반 최적값으로 검증하지 않았다.

## 실제 실행한 검증

Workspace 루트에서 관련 CPU 검사를 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py
```

결과: **76 passed in 3.49s**. 실제 MDP 함수와 Isaac Lab tensor math·configclass를 실행하는 기존 CPU harness를 사용했다. 0.01/0.02/0.05초 주기의 hold 시간·+100 보너스, 보상 재조회 시 비증가, 부분 reset, 이탈·속도·기울기·지지 높이·선반 경계·실패 플래그에 따른 유지 보상 0, v0 상속 전체 diff·부모 격리·실패보다 뒤인 성공 term 순서·등록 및 PPO 동일성을 검사했다.

루트 README의 전체 검증도 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider
```

결과: **309 passed, 17 subtests passed in 17.51s**.

GPU 실행은 아래 명령으로 8개 환경·PPO 1 iteration을 수행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2 \
  --num_envs 8 --max_iterations 1 --headless \
  --experiment_name inspire_dex_tactile_sweep_omni_renewal_v2_smoke \
  --run_name validation > /tmp/dex_tactile_renewal_v2_smoke.log 2>&1
```

결과: exit 0. 새 task 등록과 manager 생성, 57D 관측·8D 행동, 보상 12항·종료 7항 및 PPO 1 iteration을 완료했다.

산출물은 `logs/rsl_rl/inspire_dex_tactile_sweep_omni_renewal_v2_smoke/2026-10-18_20-02-53_validation/`의 `params/env.yaml`, `params/agent.yaml`, `model_0.pt`와 TensorBoard 이벤트다. stdout에는 `goal_hold=20`, `success=100` 및 `Episode_Termination/success`가 기록됐다. 무작위 정책의 짧은 실행에서 두 새 보상과 성공 지표는 0이므로 실제 성공을 달성한 검증으로 해석하지 않는다. 기존 시각화 PointInstancer 경고는 남아 있으며 이번 보상 변경에서 수정하지 않았다.

## 실행과 미검증 범위

일반 학습은 Workspace 루트에서 다음과 같다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2 \
  --num_envs 2048 --headless
```

재생은 같은 task와 사용자가 선택한 체크포인트를 지정한다. 기존 v0와 관측·행동·정책 크기는 같지만, 새 보상의 학습 성과는 별도 확인해야 한다. 이번 작업에서는 장시간 학습·v0 체크포인트 재개·정착 성공률·오버슈트 개선·실물 실행을 검증하지 않았다.

문서 저장소 루트에서 변경한 Markdown 7개만 검사했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py 01_plan/00_HANDOFF_BRIEF.md 01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md 01_plan/04_NEXT_ACTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-18_dex_tactile_renewal_v2_goal_hold.md ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external 01_plan/00_HANDOFF_BRIEF.md 01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md 01_plan/04_NEXT_ACTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-18_dex_tactile_renewal_v2_goal_hold.md ../../src/inspire_sweep_baseline/README.md
git diff --check
```

결과: Markdown 수식 검사 7개 통과, 내부 링크 165개·workspace 링크 37개에서 오류 0건. Workspace 루트에서도 `git diff --check` 통과. GPU run에 저장된 `params/env.yaml`에서 새 두 reward callable과 +20/+100, 성공 hold_time 0.5·위치/속도 임계값·실패 목록을 확인했다.
