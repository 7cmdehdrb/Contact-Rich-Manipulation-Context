# OSC 선반 종료와 목표 시각화

[개발 로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

사용자 요청에 따라 OSC 환경의 shelf_collision에서 손가락 조건만 제거했다. 공유 함수에 check_fingers=True를 추가하고 OSC에서만 False로 설정했다. 선반 움직임 및 손목 임계값, 다른 환경, 선반 보상은 유지한다. SweepGoalCommand에 debug visualization callback을 구현하고 OSC에서 활성화했다. 현재 목표 월드 위치에 녹색 반지름 0.025m sphere marker를 표시한다. 기존 사용자 수정인 OSC action scale 1.0/1.0과 workspace 변경을 보존했다.

## 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_goal_terminations.py src/inspire_sweep_baseline/tests/test_omni_configuration.py -k 'not test_renewal_composes_complete_v4_behavior_without_v4_inheritance and not test_dex_renewal_changes_exactly_the_two_dex_reward_terms'
```

40 passed, 2 deselected (3.13s). 기존 Renewal/V4 속도 설정 동일성 테스트 2개는 이전 작업과 같이 제외했다. 손가락 제외, 선속도/각속도/손목 종료 유지, 부모 설정 격리, 목표 시각화 활성화를 검증했다. 실제 Isaac Sim 렌더링·재생은 실행하지 않았다.

## 사용자 정정: Renewal 부모에 적용

적용 범위를 OSC 전용에서 Renewal 부모로 정정했다. `OmniRenewalTerminationsCfg`에서 check_fingers=False, `InspireSweepOmniRenewalEnvCfg.__post_init__`에서 goal debug_vis=True를 설정하고 OSC의 중복 override를 제거했다. Renewal·Dex Renewal·OSC가 모두 상속하며 Renewal 외 환경의 기존 설정은 유지한다. 사용자 변경인 push_fast=0.8 및 OSC scale은 보존했다.

위 명령을 다시 실행한 결과 41 passed, 2 deselected (2.74s). Renewal·Dex Renewal·OSC의 최종 설정과 baseline 격리를 검증했다. 실제 시뮬레이션은 미실행이다.
