# Fusion v1_0 종료 원인 출력 — 2026-10-23

[활성 환경](../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md.txt) · [로그 목록](README.md)

## 요청과 변경

사용자가 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0` 재생 중 실제 종료 원인을 확인하도록 모든 종료 항목의 print 출력을 요청했다. 기준 workspace commit은 `16a2a3e`이며 시작 시 문서 submodule 포인터 차이가 있었다. 기존 학습 로그와 체크포인트는 수정하지 않았다.

`ContactSweepClutterFusionV1_0Env.step()`에서 부모 실행 결과의 terminated/truncated 환경을 선택하고 `TerminationManager.active_terms`와 `get_term()`으로 실제 발생 항목을 출력한다. 현재 Isaac Lab의 TerminationManager는 자동 reset에서 term mask를 지우지 않으므로 reset 이후 상태로 종료 조건을 재평가하지 않는다. 반환값과 판정 함수·임계값은 그대로 유지한다.

활성 항목은 `time_out`, `object_drop`, `push_fast`, `shelf_collision`, `hand_velocity`, `shelf_displacement`다. `hand_velocity`는 기존 로그 키를 보존하며 실제 Arm 관절 속도라는 설명을 덧붙인다. 같은 step에 여러 조건이 발생하면 각 항목을 모두 출력한다. 종료가 없는 step이나 수동 reset에서는 출력하지 않는다. 비활성 `object_outside_shelf`와 성공 종료는 추가하지 않는다.

```text
[Termination][ContactSweepClutterFusionV1_0Env] step=123 term=object_drop env_ids=[0]
[Termination][ContactSweepClutterFusionV1_0Env] step=123 term=hand_velocity (arm joint velocity) env_ids=[0]
```

Train/play 모두 기본 출력하며 같은 실행 클래스를 상속하는 파생 환경도 자신의 활성 항목을 출력한다. 다수 환경 학습에서는 출력량과 CPU 전송 비용이 증가할 수 있다. 등록·상속·runner·기존 play 명령은 유지한다.

## 실제 검증

Workspace 루트에서 다음을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_cfg.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_object_state.py
```

결과: **11 passed in 1.72s**. 기존 설정과 활성 물체 종료 계산 검사가 통과했다.

별도로 `/home/min/miniconda3/envs/env_isaaclab/bin/python -B -`의 inline Python probe에서 실제 소스의 `step()`을 AST로 추출하고 Torch CPU mask와 부모 step 대역으로 실행했다. 여섯 항목 출력, 동일 환경의 동시 원인, 환경 ID 분리, Arm 설명, 원본 반환값 보존, 종료 없는 step에서 이전 mask가 남아도 무출력을 확인했다. 결과는 `PASS: six terms, simultaneous causes, environment IDs, arm label, unchanged return, no-done silence`였다. 이는 실제 Isaac Sim 실행 검증과 구분한다.

Isaac Sim GUI/play 및 해당 학습 checkpoint 재생은 실행하지 않았다. 기존 play 명령을 새 프로세스에서 실행하면 출력이 적용된다.

## 후속 요청: 실시간 속도 모니터링

사용자가 종료 시점만이 아니라 속도를 계속 관측하도록 명시했다. 공용 `mdp/terminations.py::push_fast()`에 기본 False인 `print_velocity` 옵션을 추가하고 v1_0의 `TerminationsCfg.push_fast.params`에서 True로 활성화했다. 매 함수 호출(제어 step)마다 모든 환경의 타겟 물체 `object_lin_vel_w`의 월드 XYZ 성분, 3차원 norm 속력, 임계값, 엄격한 초과 여부와 step·환경 ID·타겟 ID를 출력한다. 자동 reset 전에 판정에 사용한 표본을 직접 출력한다. False·True와 관계없이 원래 `speed > speed_condition` 결과를 반환한다.

```text
[push_fast] step=42 env_id=0 target_id=1 velocity_world=(0.300000, 0.400000, 0.000000) m/s speed=0.500000 m/s threshold=0.800000 m/s exceeded=False
```

출력은 play/train 모두 적용되며 종료 설정을 상속하는 파생 환경에도 적용된다. 사용자 목적은 기존 `--real-time` play의 연속 모니터링이다. 임계값은 0.8m/s로 유지하며 다른 환경의 기본 함수 호출은 출력하지 않는다.

실행한 inline 검증 명령은 `/home/min/miniconda3/envs/env_isaaclab/bin/python -B -`다. 실제 `push_fast` AST를 추출한 Torch CPU probe에서 타겟 인덱스 선택, 매 step·모든 환경 출력, XYZ와 norm, 임계값과 같은 속도에서 미종료, 초과 시 종료, 출력 옵션 기본 False와 반환값 보존을 확인했다. Isaac Sim 실시간 실행은 미검증이다.

추가 회귀 검증은 위 pytest 실행 환경에서 `test_clutter_fusion_v1_0_cfg.py`와 `test_omni_configuration.py`를 지정해 실행했으며 **33 passed in 2.70s**였다. Markdown 수식 검사와 두 저장소의 `git diff --check`도 통과했다.


## 후속 요청: 모니터링 전체 주석 처리

사용자 요청으로 v1_0 실행 클래스의 모니터링용 `step()` override 전체, 공용 `push_fast()`의 속도 출력 블록과 진단용 함수 시그니처, 종료 설정의 출력 옵션을 주석으로 보존하고 비활성화했다. 활성 `push_fast()`는 기존 시그니처와 `vector_norm(velocity) > speed_condition` 반환식으로 복원했다. 종료 조건·0.8m/s 임계값은 유지한다. 기존 프로세스에는 코드 변경이 반영되지 않으므로 다음 실행부터 모니터링이 출력되지 않는다.

검증은 앞서 기록한 CPU pytest 환경에서 `test_clutter_fusion_v1_0_cfg.py`, `test_omni_configuration.py`를 실행했다. 출력 비활성화는 실제 소스 AST에서 v1_0의 `step()` override와 `push_fast()`의 활성 print 호출·출력 옵션이 없는지 확인했다. 실제 GUI 재생은 미실행이다.

결과: **33 passed in 2.80s**, AST 출력 비활성 검사 PASS, 변경 Markdown 3개 수식 검사와 두 저장소의 `git diff --check` 통과.
