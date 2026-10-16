# Renewal OSC 환경 추가

[개발 로그 목록](README.md) · [환경 계약과 실행](../08_ACTIVE_ENVIRONMENTS.md#renewal-osc-환경)

기준 workspace commit `b2ece799a8717f44b95bb58a32cccea206a75519`. 문서 submodule의 기존 변경은 보존했다. 사용자 요청은 Renewal 상속, EEF 기준 relative/fixed OSC, stiffness 200, damping ratio 1이다.

`omni_renewal_osc_env_cfg.py`에서 부모 post-init 이후 Arm action만 교체하고 Arm implicit PD를 0으로 설정했다. EEF body와 pose offset은 기존 sensor 설정에서 읽는다. 위치/회전 scale 0.05m/0.1rad, 관성 보정·중력 보상을 사용한다. Hand·보상·종료·관측·이벤트·PPO는 유지한다. 새 Gym ID를 등록했다. 상속·action 의미·실행 명령은 활성 환경 안내에 기록했다.

## 실제 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_omni_configuration.py src/inspire_sweep_baseline/tests/test_goal_rewards.py src/inspire_sweep_baseline/tests/test_configuration_contract.py -k 'not test_renewal_composes_complete_v4_behavior_without_v4_inheritance and not test_dex_renewal_changes_exactly_the_two_dex_reward_terms'
```

63 passed, 2 deselected (2.80s). 제외한 두 테스트는 이전 작업에서 확인한 Renewal 속도 파라미터와 예전 V4 동일성 가정의 불일치다. 새 OSC 테스트는 실제 Isaac Lab controller/action config 정의와 configclass를 사용하되 simulator 자산은 CPU stand-in으로 검증했다. EEF offset, gains, relative/fixed, 등록, 부모와의 전체 설정 비교 및 부모 instance 격리를 확인했다. 초기 테스트 fixture의 action class 이름 누락을 수정한 뒤 통과했다.

실제 Isaac Sim 환경 생성·rollout·학습은 실행하지 않았다. 토크 응답·접촉 안정성·성능을 CPU 설정 검사로 입증하지 않는다.
