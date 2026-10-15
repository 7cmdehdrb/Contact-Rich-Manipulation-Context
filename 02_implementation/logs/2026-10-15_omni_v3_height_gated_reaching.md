# 2026-10-15 — Omni v3 높이 조건부 XY Reaching

[문서 안내](../README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md)

## 요청·근거·범위

사용자는 v2를 약 1400 iteration 학습한 뒤 물체 접근은 생겼으나 선반에 충돌하며 종료된다고 보고했다. 이번 작업에서 그 run을 직접 재생하거나 원인을 계측한 것은 아니다. 요청에 따라 v2에서 Reaching만 바꾼 `Isaac-Inspire-Sweep-Omni-v3`를 추가했다.

기준 Workspace commit은 `32076d7`이다. 현재 v2의 weight는 Reaching 30, Goal 40이며 이를 보존했다. Action Rate·Joint Velocity 등 다른 비용, 종료, 관측, 제어, PPO와 v0/v1/v2는 변경하지 않았다. 참고 서브모듈은 읽기 전용으로 확인했다. 기존의 루트 지침이 가리키는 Workspace/개발 지침 경로는 여전히 없으며, 앞선 작업에서 읽은 인계·문서 저장소 지침과 기존 Manager 구성 방식을 따른다.

참고: [기본 Reaching 구현](../../../Sweep-Policy/sweeping_policy/mdp/reward_random_sweep.py)의 `reward_for_hand_reaching`은 물체 바닥 Z에 0.09m를 더한 목표에 대한 3D 지수 보상이다. [Mass variant](../../../Sweep-Policy/sweeping_policy/mdp/inspire_mass_rewards.py)는 별도로 0.04m 기본값을 사용한다. 참고 코드에 ±2cm hard gate가 이미 있는 것으로 해석하지 않았다. v3에는 기본 Reaching의 +9cm 높이와 이번 요청을 결합해 ±2cm 허용 오차를 추가했다. 허용 오차는 실험 설정이며 실측 안전 한계가 아니다.

## 구현 동작

- `InspireSweepOmniV3EnvCfg(InspireSweepOmniV2EnvCfg)`에서 Reaching callable과 `z_offset=0.09`, `z_tolerance=0.02`만 변경한다. 상속으로 현재 weight 30을 유지한다.
- `HeightGatedPlanarReachProgress`는 reset 시 `max(norm(EEF_xy − object_xy) − near_radius, 0)`를 초기 거리와 최소 기록에 저장한다. `near_radius=0.10`은 v2에서 상속한다.
- 매 step 현재 물체 XY까지의 거리로 최소 기록을 갱신한다. `abs(EEF_z − (object_z + 0.09)) <= 0.02`일 때만 `(이전 최소 거리 − 새 최소 거리) / 초기 거리`를 지급한다. `step_dt` 상쇄와 수치 epsilon은 기존 진전 보상 방식이다.
- 높이 밖의 접근도 최소 기록은 갱신하지만 지급하지 않는다. 이때 소진한 접근 진전은 높이를 나중에 맞춰도 회수할 수 없다. 높이만 개선하는 행동·대기·왕복·Z 범위 반복 출입에는 중복 보상이 없다.
- 물체 좌표는 현재 GT다. 물체가 EEF 쪽으로 움직이면 상대 XY 접근으로 계산될 수 있다는 기존 특성은 유지한다.

## 실제 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py \
  src/inspire_sweep_baseline/tests/test_goal_events.py \
  src/inspire_sweep_baseline/tests/test_task_contract.py \
  src/inspire_sweep_baseline/tests/test_configuration_contract.py
```

결과: **83 passed in 1.87s**. 높이 위·아래 gate, 현재 물체 Z/XY 반영, 높이만 변경한 보상 방지, 부분 reset, XY 정규화, dt 독립성, 초기 근접, v3 등록과 manager 인자 바인딩을 확인했다. v3 Reaching 항만 v2 항으로 치환하면 전체 config가 v2와 같음을 검사했다.

기존 v2 테스트에 남아 있던 200/400 상수는 현재 사용자가 조정한 weight를 되돌리는 대신, 실제 설정의 weight에 비례한 보상 기대값으로 변경했다. 이는 v2 실행 설정 변경이 아니다.

추가로 다음 검증을 실행했다. 결과는 `Markdown math check passed: 4 file(s)`와 양쪽 저장소 whitespace 오류 없음이다.

```bash
python -B example/Contact-Rich-Manipulation-Context/scripts/check_markdown_math.py \
  src/inspire_sweep_baseline/README.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  example/Contact-Rich-Manipulation-Context/docs/logs/2026-10-15_omni_v3_height_gated_reaching.md \
  example/Contact-Rich-Manipulation-Context/docs/README.md
git diff --check
git -C example/Contact-Rich-Manipulation-Context diff --check
```

Isaac Sim 환경 생성·GPU 학습·재생은 실행하지 않았다. EEF 높이 gate만으로 손 전체의 충돌을 방지한다고 보장할 수 없으며, 실제 선반 종료 감소와 학습 성능은 다음 run에서 확인해야 한다.


## 원격 main 병합과 publish 검증

사용자의 commit/push 요청에 따라 루트 원격 `7094a55`의 Dex Omni 추가와 문서 원격 `f4b65dc`의 네 폴더 개편을 병합했다. v2·v3 개발 로그를 `02_implementation/logs/`로 이동하고 관련 색인·링크를 갱신했다. 원격의 Dex Omni·센서 문서·Sweep-Policy 참조를 유지했으며 v3 등록·Reaching·회귀 테스트도 함께 보존했다.

위 CPU 검증 명령에 `src/inspire_sweep_baseline/tests/test_dex_rewards.py`를 추가해 병합 결과를 검사했다. 결과는 **101 passed in 1.97s**다. `check_document_links.py --check-external`로 병합한 문서 5개와 패키지 README의 내부·Workspace 링크를 확인한 결과 **errors: 0 (6 files)**였다. Markdown 수식 검사와 양쪽 `git diff --check`도 통과했다. 학습·재생은 이번 병합에서 실행하지 않았다.

기존 미추적 `src/Universal_Robots_ROS2_Description/`는 작업과 무관하여 커밋에 포함하지 않았다. 문서 main을 먼저 push한 뒤 해당 commit을 가리키는 루트 main을 push하는 순서로 게시한다.
