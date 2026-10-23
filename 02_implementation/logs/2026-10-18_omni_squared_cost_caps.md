# Omni 운동 제곱합 비용의 출력 상한

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [개발 지침](../../00_guidelines/09_DEVELOPMENT_GUIDE.md)

기준일: 2026-10-18. Workspace 기준 commit `dbea2940bb458b8171408bf04c61ce57e8bec1e7`, 문서 저장소 기준 commit `f9550a515586d2c49f2b405b243561511eb8d3da`. 시작 시 상위 저장소의 문서 submodule 참조 차이를 보존했으며 문서 내부 작업트리는 깨끗했다. commit·push는 수행하지 않았다.

## 사용자 요청과 적용 범위

사용자는 `action_rate_l2`와 `joint_vel_l2`의 함수 반환 범위를 초기 −100~100으로 지정하되, 부호가 한쪽으로 제한되는 구조라면 필요한 쪽의 경계만 설정하도록 요청했다. 현재 Omni 계열의 두 함수는 음의 reward가 아니라 **비음수인 제곱합 비용**을 반환한다. 따라서 [goal_rewards.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/goal_rewards.py)의 두 함수에 `max_cost=100.0`을 추가하고 최종 제곱합에 `clamp_max(max_cost)`를 적용했다. 기본 범위는 [0,100]이다.

| 함수 | 계산 및 제한 |
| --- | --- |
| `action_rate_l2(env, action_group="arm", max_cost=100.0)` | 지정 Arm 6D 또는 Hand 2D raw action 변화량의 제곱합을 계산한 뒤 상한 적용 |
| `joint_vel_l2(env, asset_cfg=..., max_cost=100.0)` | 지정한 실제 관절 속도의 제곱합을 계산한 뒤 상한 적용 |

`max_cost`는 유한하고 0 이상이어야 한다. 0은 비용 출력 0으로 허용하고 음수·NaN·무한대 상한은 거부한다. 입력 clamp·평균·정규화·dt 나눗셈은 추가하지 않는다. 입력 tensor도 변경하지 않는다. 음의 weight 및 step_dt는 기존 RewardManager가 이후 적용한다. 따라서 −100을 최종 weighted reward 하한으로 만든 변경이 아니다.

Arm/Hand 네 항의 가중치 −0.03/−0.03/−0.03/−0.01은 유지한다. 상한에서 시간 곱셈 전 기여는 앞 세 항이 각각 −3, Hand velocity가 −1이고 0.02초 스텝 기여는 각각 −0.06·−0.02다. 실제 액션·관절 속도나 종료 기준을 제한한 것은 아니다.

함수 기본값을 바꿨으므로 해당 로컬 함수를 사용하는 Omni·Dex·Renewal·Tactile·v2·OSC 파생에 자동 적용된다. 환경 ID·실행 명령·PPO·관측·제어·성공/실패 조건은 변경하지 않았다. `mdp/rewards.py`의 별도 Baseline 동명 함수와 보관 코드는 이번 변경 범위가 아니다.

## 실제 검증

Workspace 루트에서 다음을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py \
  src/inspire_sweep_baseline/tests/test_bounded_osc.py
```

결과: **86 passed in 5.29s**. 두 그룹의 0·상한 아래·100 경계·상한 초과·음의 입력, custom cap 25·0, 잘못된 상한 거부, 원본 입력 불변 및 미선택 관절/다른 action 그룹 독립성을 검증했다. 큰 유한 float32 입력을 제곱하면서 생기는 무한대도 최종 출력이 100으로 포화되는 것을 확인했다. 기존 config 계약 검사에서 함수 참조·그룹·가중치와 v2/OSC 상속도 통과했다.

순수 tensor 출력 제한과 관련 configuration 계약을 CPU에서 검증한 변경이다. 새 GPU 실행·장시간 학습·정책 성능 개선·실물 동작은 검증하지 않았다. NaN 상태를 복구하는 변경도 아니다.

변경 Markdown 5개에 `check_markdown_math.py`와 `check_document_links.py --check-external`을 실행했다. 수식 검사 통과, 내부 링크 127개·workspace 링크 40개에서 오류 0건. Workspace와 문서 저장소의 `git diff --check`도 통과했다.
