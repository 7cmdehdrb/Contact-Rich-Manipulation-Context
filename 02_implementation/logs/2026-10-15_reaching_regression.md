# Reaching 최고 기록 이탈 페널티

[개발 로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기준 workspace commit: `4307c6b4a3acb0e9bb6974aaa467ed2ba689a366`. 작업 시작 시 패키지 README에 사용자 변경이 있어 보존했다.

## 요청과 구현

물체 중앙 +4cm 또는 바닥 +9cm의 높이, 현재 물체 기준 XY 10cm 동등 영역, 최고 접근 기록 대비 이탈 페널티를 요청받았다. 자산 `spawn_mass_cylinder`는 mesh를 높이 절반만큼 올리고 body origin을 바닥에 둔다. 보상은 `object_link_state_w`를 읽으므로 z_offset=0.09를 유지했다.

`HeightGatedPlanarReachProgress`의 남은 거리는 max(XY 거리 − 0.1, 0)이다. 이전 최소 기록에서 현재 남은 거리를 뺀 부호 있는 값을 초기 남은 거리로 나눈다. 초기부터 반경 안이면 분모는 0.1m다. 양수에는 기존 ±2cm Z gate를 적용하고, 음수에는 Z gate를 적용하지 않는다. 최소 기록은 항상 갱신한다. 반경 밖에서 최고 기록보다 먼 동안 매 step 벌점, 최고 기록 복귀는 0, 새 기록은 양수다. 함수의 dt 나눗셈과 weight=30을 유지한다. 따라서 이탈 비용은 초당 비용이 아니라 step당 비용이며, 실제 강도는 추가 학습으로 확인해야 한다.

공통 함수의 Omni v3/v4/Sweep Renewal에 적용한다. 상속·등록·실행 명령과 Dex의 별도 접근 함수, 기존 운동 페널티는 변경하지 않았다.

## 검증

실행 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_goal_rewards.py src/inspire_sweep_baseline/tests/test_omni_configuration.py -k 'not test_renewal_composes_complete_v4_behavior_without_v4_inheritance and not test_dex_renewal_changes_exactly_the_two_dex_reward_terms'
```

결과: 57 passed, 2 deselected (2.71s). 최초 실행에서 새 테스트의 float32 반경 경계 비교 3건은 수치 허용 오차로 수정했다. 제외한 설정 테스트 2건은 현재 Renewal 속도 설정이 V4와 같다는 예전 가정 및 arm_speed_excess weight=-0.03 가정 때문에 실패했다. 현행 Renewal은 별도 속도 설정 및 weight=-0.1을 사용하며 이번 작업에서는 변경하지 않았다.

물체 이동·반경 내 plateau·반복 이탈·잘못된 높이에서 이탈·복귀 무보상·초기 반경 내부·부분 reset·서로 다른 step_dt를 CPU에서 검증했다. Isaac Sim 실행과 재학습은 수행하지 않았다. 보상 변경이 정책 개선을 입증하지는 않는다.
