# Clutter v1 선반 실패의 일회성 −3

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [v1 MDP](../environments/CONTACT_SWEEP_CLUTTER_V1_MDP.md)

## 요청과 구현

사용자는 `contact_sweep_clutter_v1`에 shelf 실패 시 일회성 −3 비용을 추가하고 종료로 인해 비용이 누락되지 않도록 요청했다. 작업 기준 workspace commit은 `fdc50dda2ea1f795348bea71d5ed60bd279e9de5`다. 시작 시 v1 rewards cfg에 사용자가 속도 free-speed 재설정을 주석 처리한 변경과 상위 저장소의 문서 submodule 참조 변경이 있었다. 이를 보존했다.

Task ID는 `Isaac-Inspire-Contact-Sweep-Clutter-v1`, runtime은 `ContactSweepClutterV1Env`, cfg는 `ContactSweepClutterV1EnvCfg`를 사용한다. 새 보상 `shelf_failure`의 weight는 −3이고 함수는 아래 값을 반환한다.

```text
shelf_collision 종료 여부(float) / env.step_dt
```

RewardManager가 weight와 dt를 곱하므로 실제 차감은 `−3 × 종료 여부`다. 일반 비용률 −3/초가 아니며 제어 주기가 달라도 이벤트당 −3이다. 기존 `shelf_collision` 연속 비용과 별도로 합산한다.

실행 순서는 **physics → 현재 상태의 종료 조건 판정 → 보상 계산(−3 포함) → 자동 reset → 관측·보상·종료 플래그 반환**이다. 조건 판정 자체를 보상보다 뒤로 옮기지 않고, 현재 step의 판정값을 읽어 에피소드 reset 전에 마지막 반환 보상에 비용을 넣는다. 이전 step에서 미래의 실패를 예측해 선차감하는 방식은 아니다.

`shelf_collision`만 트리거로 사용한다. Timeout·물체 실패·선반 변위 실패만 발생하면 이 항은 0이다. 여러 종료 조건이 동시에 발생하더라도 `shelf_collision`이 참이면 이 항으로는 한 번만 −3을 부과한다. 해당 step 뒤 자동 reset되므로 이전 실패가 다음 에피소드에 반복되지 않는다. 별도 누적 latch나 추가 종료 조건은 도입하지 않았다.

v1 상속에 따라 v2에도 새 음의 항이 적용된다. v2의 F/T 변화 비용에 대한 양의 보상 5% 예산의 분모에는 이 음의 비용이 포함되지 않는다. v0에는 추가하지 않았다.

## 검증

`test_clutter_v1_shelf_failure.py`에서 실제 checked-in `ManagerBasedRLEnv.step` 함수 본문과 `RewardManager.compute`를 실행하고 simulator 주변 객체만 CPU 대역으로 대체했다. 0.01·0.02·0.04초 주기 각각에서 다음을 확인했다.

- 실패 판정 뒤 reward가 계산되고 그 후 reset이 호출된다.
- reset 진입 시 이미 episode 누적 비용에 −3이 기록되어 있다.
- 자동 reset이 실패 flag를 지워도 호출자가 받는 마지막 보상은 −3이다.
- Timeout-only·다른 실패-only 행에는 0이다.
- 다음 정상 step에는 비용이 반복되지 않는다.
- 실제 v1 reward 선언의 callable과 weight −3을 확인한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_clutter_v1_shelf_failure.py
```

위 전용 검사 4개는 통과했다. 같은 명령에서 대상 경로를 `src/inspire_sweep_baseline/tests`로 바꾼 전체 패키지 검사도 **349개 통과**, 기존 ONNX deprecation 경고 2개였다. stdout은 workspace `outputs/clutter_v1_shelf_failure_2026-10-20/pytest.log`에 저장했다.

물리 엔진 재실행·장기 재학습은 수행하지 않았으며, 이 변경만으로 shelf 회피·밀기 성공률이 개선되었다고 주장하지 않는다. 이미 실행 중인 학습 프로세스는 Python에 로드된 이전 설정을 사용하므로, 변경 적용에는 새 프로세스 시작이 필요하다.
