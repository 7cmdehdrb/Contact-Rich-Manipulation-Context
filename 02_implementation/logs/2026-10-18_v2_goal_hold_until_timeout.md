# v2와 OSC v2: 성공 후 timeout까지 목표 유지

[개발 로그](README.md) · [활성 환경 계약](../08_ACTIVE_ENVIRONMENTS.md) · [사용자 결정](../../01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md)

기준일: 2026-10-18. Workspace `main`, 기준 commit `78ceff42d0c873eb1177d0b564bf83dcf68d6588`, 문서 저장소 기준 commit `f751e5af429846cdbe08900e40661a8797668971`. 작업 시작 시 상위 저장소에는 문서 submodule 참조 차이가 있었고 문서 내부 작업트리는 깨끗했다. 참조 차이는 보존했으며 commit·push는 수행하지 않았다.

## 요청과 적용

사용자가 원한 동작은 목표 위치에 물체가 계속 머무는 상태로 timeout까지 기다리는 것이다. 최초 구현의 성공 종료는 이 의도와 달랐으므로 제거했다. 적용 대상은 기존 task ID 두 개다.

- `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2`.
- 위 환경을 상속한 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2`.

공통 v2의 `DexTactileOmniRenewalV2TerminationsCfg.success=None`으로 설정했다. 기존 실패 조건 5개와 timeout만 활성이다. OSC Cfg는 이 termination/reward를 그대로 상속하므로 OSC 파일에 중복 설정을 추가하지 않았다. 두 task 모두 관측·행동·제어·물성·reset·기존 비용·PPO·등록 ID는 바꾸지 않았다. 특히 OSC stiffness 100과 명령 상한 5 mm/0.025 rad도 유지한다.

## 보상과 상태의 수명

[새 reward term](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_hold_rewards.py)의 `StableGoalAchievement`가 기존 `StableGoalSuccess`의 자격 판정·연속 타이머를 재사용한다. reward manager가 이 term을 먼저 계산하고 `goal_hold`는 같은 인스턴스의 시간을 읽는다. termination manager의 가짜 성공 항을 계산하거나 False를 반환하도록 둔 구조가 아니다.

자격 조건은 기존과 같다: 목표 XY 오차 <1 cm, 물체 XY 속도 <0.02 m/s, 선반 법선 기준 기울기 ≤10°, 바닥 지지 오차 ≤1 cm, 물체 반경을 고려한 선반 내부 지지, 활성 실패 없음. 0.5초 연속 만족 시 최초 달성이다.

| 상태 | +100 보너스 | 유지 보상 |
| --- | --- | --- |
| 최초 0.5초 연속 유지 | dt 상쇄 후 한 번 지급 | 0→최대 +20/초로 증가 |
| 성공 후 계속 유지 | 추가 지급 없음 | +20/초 계속 지급 |
| 목표 이탈·자격 상실 | 지급 이력 유지 | 0, 연속 시간 초기화 |
| 목표 재진입 | 같은 episode에서는 재지급 없음 | 0부터 다시 증가 |
| timeout·기존 실패로 reset | 해당 환경의 지급 이력 초기화 | 해당 환경의 연속 시간 초기화 |

`_awarded`는 환경별 Boolean latch다. 성공 판정 후 이탈해도 latch를 해제하지 않아 재진입을 통한 보너스 반복 획득을 막는다. 부분 reset은 해당 row의 타이머와 latch만 초기화한다. `StableGoalAchievement`의 반환값은 최초 달성 지표를 step_dt로 나눈 값이며 reward weight +100을 한 번 지급한다. `goal_hold` weight +20은 dt를 RewardManager에서 한 번 곱한다.

50 Hz에서는 체류 보상이 +0.016, +0.032, …, +0.4/스텝으로 증가하고, 25스텝 이후에도 +0.4/스텝이 계속 지급된다. episode 시작부터 500스텝·10초 동안 자격을 유지하면 체류 보상 +195.2, 보너스 +100이다. 실제 물체 도착이 늦으면 도착 후 남은 시간만 지급한다. 기존 실패 조건이 발생하면 timeout 전에 종료할 수 있다.

기존 `success_event`와 다른 Omni 환경의 `StableGoalSuccess` 종료 동작은 유지했다. v2만 새 비종료 reward term을 사용한다. `stable_goal_hold`는 이제 termination manager 대신 reward manager의 success 인스턴스를 조회한다. 새 속도·위치 오차 비용은 추가하지 않았다.

## 실행한 CPU 검증

관련 테스트:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_goal_hold_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py \
  src/inspire_sweep_baseline/tests/test_bounded_osc.py
```

**45 passed in 4.70s**. 0.01/0.02/0.05초 제어 주기에서 10초 유지, +100 한 번, 유지 보상 계속 지급을 검증했다.

또한 이탈·재진입 시 보너스 재획득 금지, 부분/전체 reset 후 재지급, 각 자격 조건의 무효화, 보상 재조회 시 시간 중복 증가 방지를 확인했다.

전체 회귀 검사:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider
```

**316 passed, 17 subtests passed in 17.48s**. 실제 Isaac Lab configclass와 MDP 함수를 실행하는 기존 CPU harness에서 v2 변경 범위·부모 격리·reward 계산 순서와 OSC의 상속 동등성을 확인했다.

## GPU manager·timeout 수명 검증

[수명 검증 스크립트](../../../../src/inspire_sweep_baseline/tests/_goal_hold_lifecycle_probe.py)를 추가하고 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_goal_hold_lifecycle_probe.py --headless \
  > /tmp/goal_hold_timeout_lifecycle.log 2>&1

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_goal_hold_lifecycle_probe.py --headless \
  --task Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2 \
  > /tmp/goal_hold_timeout_lifecycle_osc.log 2>&1
```

각 실제 Gym task를 2개 환경·seed 42로 생성하고 기본 10초 timeout을 그대로 사용한다. 각 physics substep 전에 robot joint state와 물체의 지지 상태를 고정하여, 정책 성능이나 기존 OSC 불안정성과 분리해 reward/termination/auto-reset 순서를 검증한다. 이는 물체를 정책이 목표에 밀어 넣는 성능 평가가 아니다. 장면 고정은 검증 스크립트에만 있고 실제 환경 코드는 물체나 로봇을 고정하지 않는다.

검증 항목은 성공 termination 없음, 25스텝에 +100 지급 후 무종료, 500스텝 전까지 무종료, 500스텝에서 timeout, +100 누적 한 번, 유지 보상 누적 +195.2, auto-reset 후 첫 스텝의 보너스 0·유지 보상 +0.016이다.

두 task 모두 실제 manager/step/auto-reset 경로의 assertion을 통과했다. 각 task의 2개 환경에서 결과는 같았다.

| Task | timeout | 성공 보너스 합 | 유지 보상 합 | 성공으로 reset |
| --- | --- | --- | --- | --- |
| Joint Position v2 | 500스텝·10초 | 각각 +100 | 각각 +195.19931 | 없음 |
| OSC v2 | 500스텝·10초 | 각각 +100 | 각각 +195.19931 | 없음 |

두 출력 모두 `GOAL_HOLD_LIFECYCLE`의 `passed=true`, `pinned_states=true`를 확인했다. float32 누적의 +195.2 대비 오차는 약 0.00069다. timeout 후 첫 스텝의 bonus 0·유지 보상 +0.016도 통과했다. 기존 시각화 PointInstancer 경고는 그대로다.

첫 검증 도구는 두 task를 한 프로세스에서 연속 생성하도록 되어 있었고 v2 검사 통과 후 대기가 길어 중단했다. 단일 task 선택과 hook 복원 처리를 추가해 OSC는 별도 프로세스로 실행했다. 초기 실행의 v2 통과 출력은 보존했고, OSC 개별 실행도 exit 0으로 완료했다. 이는 학습 중단이나 실제 task의 timeout 의미 변경이 아니라 검증 실행 방식의 조정이다.

## 실행 안내와 미검증 범위

task ID와 train/play 명령은 그대로다. [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)과 [패키지 안내](../../../../src/inspire_sweep_baseline/README.md)를 따른다. 기존 체크포인트의 관측/행동 차원은 바뀌지 않았지만, 이 변경으로 장시간 유지 정책이 학습됐다는 뜻은 아니다. 새 장시간 PPO 학습·재개·자연스러운 물체 정착 성능·실물 동작을 검증하지 않았다. 기존 OSC의 0 명령 이후 과속 문제도 이번 변경에서 해결하지 않았다.

변경 Markdown 9개에 `00_guidelines/scripts/check_markdown_math.py`와 `check_document_links.py --check-external`을 실행했다. 수식 검사 9개 통과, 내부 링크 187개·workspace 링크 49개에서 오류 0건. Workspace와 문서 저장소의 `git diff --check`도 통과했다.
