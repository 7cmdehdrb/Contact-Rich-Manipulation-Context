# 현행 ContactSensor와 17개 Binary 입력 의도의 대조

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기록일: 2026-10-14. 사용자 의도는 Hand의 17개 센서 mesh 영역별 접촉 여부를 Binary로 취득하는 것이다. 이번 작업은 현행 코드와 USD 조사이며 센서 구현·관측 차원을 변경하지 않았다. Workspace 기준 commit은 `f240c64f706a9911ea143528f54001211058f11b`이며 기존 문서 submodule 변경을 보존했다.

## 확인한 계약

- [env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_envs.py)의 `palm_tactile`은 `{ENV_REGEX_NS}/Robot/inspire_palm_force_sensor` 한 rigid body만 선택한다. `update_period=0.0`, `history_length=1`, `force_threshold=0.05`다.
- `ObservationsCfg.PolicyCfg.tactile`은 [palm_contact_bit](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/sweep.py)를 호출한다. 해당 함수는 body_names가 정확히 `("inspire_palm_force_sensor",)`인지 검사하며 여러 body가 들어오면 예외를 발생시킨다.
- 반환값은 `net_forces_w`의 벡터 norm이 0.05 N 이상인지 나타내는 float32 0/1, shape `(num_envs, 1)`이다. Reset 직후 stale sensor 행은 0으로 마스킹한다. 임계값 미만의 약한 접촉은 0이다. 사용 데이터는 합산된 법선 접촉력으로 기하학적 교차 여부 자체와 구분한다.
- Baseline, Realistic Physics, Initial-Privileged, Omni v0/v1 모두 이 Scene 센서와 tactile 관측을 상속한다. Actor의 tactile은 모두 1D다. Initial-Privileged는 물체 초기 위치·critic 관측을 변경하며 tactile 구성은 변경하지 않는다.
- [robot.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/robot.py)의 `PALM_SENSOR_BODY_NAMES`에는 17개가 있다: palm 1, thumb 4, index/middle/ring/little 각 3. 명칭과 달리 17개 전부가 palm 단일 부위에 있지는 않다. 이 목록은 물성·접촉 body 목록에도 사용되지만 17D 관측을 만드는 코드가 아니다.
- Robot spawn의 `activate_contact_sensors=True`는 접촉 리포팅 활성화이며 17개 관측의 자동 생성을 뜻하지 않는다.

## USD 확인과 실행한 검사

`/home/min/miniconda3/envs/newton/bin/python -`로 `pxr.Usd.Stage.Open`을 호출해 패키지 `assets/data/ur5e_inspire_usd/ur5e_inspire.usd`를 열었다. `force_sensor` 이름의 `UsdPhysics.RigidBodyAPI` prim 17개를 찾았으며, 각 body에서 instance proxy를 포함해 `UsdPhysics.CollisionAPI`를 탐색했다. 각 body에 collider 1개, collision_enabled=True임을 확인했다(exit 0). 이것은 정적 자산 검사이며 실제 GPU 접촉 응답을 입증하지 않는다.

Workspace 루트에서 다음 명령을 실제 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_observations_and_sensors.py
```

결과: **5 passed**. 현재 41D 관측·단일 palm bit·reset masking·multi-pad 거부·F/T 변환 동작을 검사한 결과다. 17D 수집의 성공을 검증한 결과가 아니다.

## 의도와의 차이 및 구현 시 고려

현재는 17개를 통합한 bit가 아니라 palm 영역 1개만 읽는다. 의도를 구현하려면 17개 sensor body를 선택해 `(num_envs, 17, 3)` 힘을 읽고, 정해진 body 이름 순서로 정렬한 뒤 각 채널을 개별 threshold하여 `(num_envs, 17)`을 반환해야 한다. 여러 mesh가 같은 rigid body에 붙으면 body 수준 ContactSensor로 mesh별 분리가 어려울 수 있으나, 조사한 USD는 17개가 각각 rigid body이므로 그 구분 단위가 존재한다.

관측은 tactile 1D를 17D로 교체하면 기존 policy 41D에서 57D로 늘어난다. Initial-Privileged critic은 policy와 privileged 13D를 함께 받으므로 54D에서 70D로 늘어난다. 기존 41D checkpoint를 새 입력에 그대로 로드할 수 없으며, 이를 구현할 때 등록·문서·테스트·새 학습 계약을 함께 갱신해야 한다. 이번 사용자 요청은 확인·설명이므로 이 변경을 실행하지 않았다.

GPU simulator 접촉 및 17개 채널의 실측 출력은 미실행이다. 문서 검사 결과는 수식 검사 2개 파일 통과, `check_document_links.py --check-external` errors 0, 문서 submodule `git diff --check` 통과다.
