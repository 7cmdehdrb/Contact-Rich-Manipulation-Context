# Dex Tactile Renewal v1 Arm 속도 제한

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md)

2026-10-19 사용자 요청: `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1`에서 Arm actuator의 물리 속도 제한을 낮춘다. 기준 workspace commit은 `fb195f7739a12cdc22f4e2f70962d6bfe7dd5e53`, 문서 저장소는 `b97791af609a30219a6c169596324160daa7999b`다. 기존 공통 종료 print·문서 변경과 사용자 체크포인트 디렉터리는 보존했다. commit·push는 수행하지 않았다.

[설정 클래스](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_renewal_envs.py)의 `InspireDexTactileSweepOmniRenewalV1EnvCfg.__post_init__`에서 `ARM_JOINT_NAMES`로 `scene.robot.actuators["arm"].velocity_limit_sim`을 매핑한다.

| 관절 | 기존 | 변경 |
| --- | --- | --- |
| shoulder_pan_joint, shoulder_lift_joint, elbow_joint | 3.14 rad/s | 2.0 rad/s |
| wrist_1_joint, wrist_2_joint, wrist_3_joint | 6.28 rad/s | 4.0 rad/s |

종료 함수 `arm_velocity`가 검사하는 `joint_vel`과 동일한 rad/s 단위이며 5.0 rad/s 실패 기준보다 낮다. Isaac Lab은 이 값을 articulation의 physics solver 속도 제한으로 전달한다. solver는 초과 시 감속을 시도하므로 모든 물리 상황에서 순간 초과가 없다고 보장하는 상태 clamp와는 구분한다. action·관절 위치 범위·종료 기준·보상·센서는 이번 변경에서 수정하지 않았다.

공통 robot factory와 v0는 그대로이며 상속 구조 `v0 → v1 → v2 → OSC v2`에 따라 v2와 OSC v2에도 적용된다. runtime·task ID·PPO·train/play 명령은 그대로다. 프로세스를 다시 시작하면 반영된다.

## 검증

workspace 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py \
  src/inspire_sweep_baseline/tests/test_bounded_osc.py
```

결과: **17 passed in 2.77s**. v1의 최종 설정과 v0 인스턴스 불변성, v2·OSC 상속과 기존 계약 검사를 통과했다. 실제 Isaac Sim play·학습과 물리 속도 실측은 수행하지 않았으므로 기존 두 번째 스텝 과속 종료의 해소는 아직 확인하지 않았다.

변경 Markdown 4개의 수식 검사·workspace 외부 파일 링크 검사 통과(링크 오류 0). 루트와 문서 저장소의 `git diff --check` 통과.
