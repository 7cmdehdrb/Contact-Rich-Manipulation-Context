# 전체 환경 Action 변화 비용 상한 제거

2026-11-11. [현재 Simple 계약](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md) · [전체 활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)

## 요청과 범위

사용자가 모든 환경에서 Action 변화 페널티의 최대 한도를 삭제하도록 요청했다. 활성 패키지 `src/inspire_sweep_baseline` 전체를 대상으로 실행되는 모든 action-rate 함수와 등록을 조사했다. Simple15개 환경에 한정하지 않고, 공유 함수를 사용하는 Omni·Fusion·Holding·Final·Wrench·Refactor·Relative-IK 계열도 적용했다. 참고 저장소·보관 패키지·학습 로그는 수정하지 않았다.

## 변경 전후

공통8D `action_rate_l2`, Finger12D `finger_action_rate_l2`에서 변화 제곱합에 적용되던 `clamp_max(100)`과 `max_cost` 인자를 제거했다. 합산 함수 `combined_action_rate`와 Final/Wrench wrapper의 cap 전달도 제거했다. Refactor의 `policy_action_rate_penalty`에서 선택적 Arm/Hand cap과 관련 인자를 제거하고, Relative EnvCfg의 cap 설정을 비웠다. 토크 이력 기반 WrenchV0_3/Refactor 및 desired-wrench 변화 비용의 출력 cap도 제거했다. 디버그용 가상 cap100 비교 필드도 삭제했다.

각 Reward Cfg에서 Action 변화 항의 max_cost만 제거했다. Joint Velocity·가속도·물체/장애물·접촉력 비용의 max_cost는 유지한다. 총 reward에 새 상한을 추가하지 않았다. 기존 가중치와 RewardManager의 dt 적용도 유지한다.

예를 들어 한 축에서 Raw 변화20이면 원시 비용은 기존100에서400으로 바뀐다. weight−0.03·dt0.02인 환경에서 해당 항의 step 보상은−0.06에서−0.24가 된다. 큰 변화가 계속 커질 때 비용도 계속 증가한다. 부동소수점 overflow/NaN을 임의 cap으로 숨기지 않으며 기존 학습 수치 검사 경로는 유지한다.

## 보존 계약과 최종 대조

Action 변화 비용의 입력 기준은 바꾸지 않았다. Simple Finger-v1/v2·Semi-Prof는 Clip된 ActionManager 이력, Finger-v0/Test/Wrench 및 Raw는 원본 ActionManager 이력을 사용한다. 과거 정규화 torque/wrench 비용이나 clamped Hand 비용은 기존 입력 변환을 유지한다. 따라서 입력 범위 때문에 자연스럽게 유한한 최대값을 갖는 항은 있을 수 있으나, 비용 출력에 별도 상한을 씌우지는 않는다.

액션 실행 Clip·Last Action tanh/Clip·URDF 목표 제한·OSC effort 한계는 이번 요청의 대상이 아니며 유지한다. 속도 종료·커리큘럼·정책 분포·다른 보상도 변경하지 않았다. 파일 구조를 변경하거나 새 환경 ID를 생성하지 않았다. 저장된 외부 설정에서 삭제된 max_cost 인자를 수동 주입하면 새 함수 signature와 맞지 않으므로 현재 등록된 환경 설정을 사용해야 한다.

활성 패키지 전체 AST에서 action-rate 호출/등록40곳을 조사하여 max_cost/arm_max_cost/hand_max_cost cap 설정이 남지 않았음을 확인했다. 변경 diff에서 다른 비용의 상한 유지도 확인했다. 과거 문서의 action-rate cap100 설명은 이번 계약으로 대체하며, 역사 로그는 보존하고 현재 설명서·인계·활성 안내에 최신 변경을 표시한다.

## 검증

8D 양 그룹·12D 손6축·합산 비용·Relative 변형에서100을 초과하는 제곱합과 그룹 분리, 입력 불변성, 기존 가중치/dt를 검사한다. 큰 값의 기존 cap 기대를 실제 uncapped 기대값으로 수정했다. 기존 joint-speed cap 검사는 유지한다. PPO 통합 검사도 unclipped/clip 실행 경로별 비용 기대값을 갱신했다.

전체 CPU 회귀 검사와 후속 결과는 아래에 기록한다. GPU/PhysX 실제 학습 및 성능 변화는 미검증이다.


전체 검사 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests -q -p no:cacheprovider --tb=short
```

첫 전체 실행은1240 passed·5 failed·10 skipped였다. 이 중3건은 삭제된 cap 인자/기댓값을 사용한 검사로 갱신했고,2건은 이번 변경과 무관한 기존 실패다. 중간 재실행에서 발견한 남은−6 고정 비용 기대값 및 테스트 들여쓰기 오류도 수정한 뒤 전체 검사를 다시 실행했다.

기존 실패 근거:

- `test_final_versions.py::test_shelf_termination_is_union`: 테스트가 `shelf_termination(None)`을 호출하지만 구현은 `env.cfg`를 읽는다. 해당 테스트 함수와 종료 함수의 AST가 HEAD와 동일함을 확인했다.
- `test_termination_debug.py::test_tasks_use_their_registered_runtime_family`: 오래된 runtime 목록에 없는 환경을 기본 Sweep runtime으로 간주해 Wrench 등록과 불일치한다. 테스트 함수가 HEAD와 동일하고 HEAD에도 Wrench runtime 등록이 존재함을 확인했다.

이 두 문제는 이번 Action 비용 변경 범위 밖이므로 수정하지 않았다. 문서 링크·수식·diff 공백 검사는 통과했다.


최종 전체 재실행은 **1241 passed·3 failed·10 skipped**였다. 위 기존2건 외1건은 큰 Raw Action PPO 통합 테스트의 모의 reward가 실제 RewardManager의 dt0.02 곱을 생략하여 비용을50배 크게 전달하던 문제였다. cap 제거 후 value loss3242718로 기존 NumericalPPO 보호가 작동했다. 테스트에 실제 dt 적용을 반영했으며, 제품의 비용 함수·가중치·수치 보호 한도는 완화하지 않았다.

이후 변경 관련6개 테스트 파일을 다시 실행하여 **100 passed in15.82s**를 확인했다. 대상은 `test_bounded_ppo_failure.py`, `test_goal_rewards.py`, `test_wrench_v0_3.py`, `test_sweep_simple_finger.py`, `test_clutter_fusion_rewards.py`, `test_wrench_refactor_relative.py`다. Clip/Raw 양 경로에서 실제 PPO 업데이트와 dt 반영 uncapped 비용 대조가 통과했다. 이 마지막 테스트 보정 후 전체 suite를 다시 실행한 것은 아니며, 기존2건 실패는 남아 있다.
