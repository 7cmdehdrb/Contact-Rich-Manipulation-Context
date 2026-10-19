# 공통 환경의 종료 이벤트 출력

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md)

기준일: 2026-10-19. Workspace 기준 commit `fb195f7739a12cdc22f4e2f70962d6bfe7dd5e53`, 문서 기준 commit `b97791af609a30219a6c169596324160daa7999b`. 시작 시 문서 submodule 참조 차이 및 사용자 체크포인트 폴더 `2026-10-18_23-47-33/`, `2026-10-18_23-47-52/`가 있었다. 모두 보존했다. commit·push는 수행하지 않았다.

## 요청과 구현

사용자는 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1` 재생 직후 종료되는 현상의 원인을 확인할 수 있도록 모든 종료 이벤트의 print를 요청했다. 이번 변경은 원인 추적용 출력이며, 종료 원인의 확정이나 조건 수정은 수행하지 않았다.

[InspireSweepEnv](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/env.py)의 `_reset_idx`에서 기존 termination manager의 active term과 해당 환경의 판정 결과를 읽어 print한 뒤 원래 reset을 실행한다. 사용자의 후속 지시에 따라 v1 전용 처리는 만들지 않고 공통 환경에 직접 print를 추가했다. 개별 판정 함수를 다시 평가하지 않으며 상태가 지워지기 전에 모든 True 항목을 출력한다.

v1의 항목은 `time_out`, `object_drop`, `push_fast`, `shelf_collision`, `hand_velocity`, `shelf_displacement`다. 비활성 항목은 제외하며 다른 환경에서는 그 환경의 활성 항목 전부를 순회한다. 동시 발생 시 각각 한 줄씩 출력하고 원래 episode step과 env ID를 유지한다. v2·OSC 등 모든 파생 환경에도 적용된다. observation·action·reward·termination 조건·PPO·task 등록·checkpoint 호환성은 바꾸지 않는다.

출력 형식 예시(실측 원인을 뜻하지 않음):

```text
[TERMINATION] term=hand_velocity function=arm_velocity timeout=False env_ids=[0] episode_steps=[1]
```

`hand_velocity`는 과거 term 이름이며 실제로는 Arm 관절 속도 판정이다. `shelf_collision`에는 선반 속도와 손목 높이 조건이 함께 있으므로 해당 이름만으로 두 하위 조건 중 어느 쪽인지 확정할 수는 없다. 이번 요청은 종료 이벤트 식별 범위로 구현했다.

## 검증

Workspace 루트에서 다음을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_termination_debug.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py
```

결과: **13 passed in 2.39s**. 변경한 Markdown 4개에 대한 수식 검사와 링크 검사도 통과했다(링크 오류 0). 루트 및 문서 저장소의 `git diff --check`도 통과했다.

CPU harness에서 실제 공통 환경 메서드를 실행해 여섯 항목 동시 발생 출력, reset 전 episode step 보존, timeout 표시, 발생하지 않은 항목 무출력, 부모 reset 실행과 모든 task의 공통 등록을 확인한다. 실제 Isaac Sim play 및 사용자가 보고한 최초 종료 원인은 아직 확인하지 않았다. 기존 명령으로 프로세스를 다시 실행하면 출력이 활성화된다.

## 후속 요청: print 주석 처리

2026-10-19 사용자 요청으로 공통 `env.py`의 종료 진단 블록 전체를 주석 처리했다. v1·v2·OSC를 포함한 모든 task에서 출력과 진단 순회를 비활성화하며 기존 reset은 실행한다. 위 출력 설명은 활성화 당시 기록이다.

검증 명령은 위 CPU pytest 명령에서 `test_termination_debug.py`만 지정했다. 결과 **2 passed in 1.17s**. 모든 종료 flag가 True여도 출력 없이 부모 reset이 실행되는 것을 확인했다. 실제 Isaac Sim 재생은 수행하지 않았다. 문서 수식·링크 및 diff 검사를 함께 수행했다.
