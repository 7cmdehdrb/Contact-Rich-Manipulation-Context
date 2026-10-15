# 2026-10-15 — Omni v2 접근·목표 진전 보상 구성

[문서 안내](../README.md) · [활성 환경 안내](../../02_implementation/08_ACTIVE_ENVIRONMENTS.md) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md)

## 요청과 상태

- 작업 ID: `2026-10-15_omni_v2_rewards`.
- 사용자 요청: v1을 보존하고 v2를 추가한다. 현재 물체 위치 기준으로 episode 최소 접근 거리를 갱신할 때만 Reaching을 지급한다. time/success/failure 보상은 임시 제거한다. 접근을 우선 학습하고 이후 목표 이동에도 충분한 보상을 부여한다.
- 상태: 보상·환경 등록 구현과 CPU 검증 완료. Isaac Sim 학습·재생 및 보상 계수의 학습 효과는 미검증이다.
- 구현 기준: Workspace `/home/ssu/Desktop/Contact-Rich-Manipulation`, 시작 commit `0135cad`. 기존 문서·참고 코드 서브모듈의 commit 차이와 사용자 산출물은 보존했다. 커밋·push는 하지 않았다.

## 읽은 근거와 지침의 확인 범위

루트 `AGENTS.md`·`README.md`, 문서 저장소 `AGENTS.md`, `docs/00_HANDOFF_BRIEF.md`, 결정·next-actions 문서, 구현·평가 문서, 코드·장비 현황, `.agents/rules/document-formatting.md` 및 활성 Baseline의 등록·보상·종료·테스트를 확인했다.

루트 지침의 `01_plan/00_HANDOFF_BRIEF.md`, `00_guidelines/10_WORKSPACE_GUIDE.md`, `00_guidelines/09_DEVELOPMENT_GUIDE.md`와 `02_implementation/08_ACTIVE_ENVIRONMENTS.md`는 작업 시작 시 현재 문서 서브모듈에 없었다. 인계는 존재하는 `docs/00_HANDOFF_BRIEF.md`를 읽었다. 확인할 수 없는 개발 지침을 추정하여 복원하지 않고 기존 ManagerTermBase·configclass·설정 상속 구조를 따랐다. 이번 변경의 상속·등록·실행 안내를 지정 경로 `02_implementation/08_ACTIVE_ENVIRONMENTS.md`에 추가하고 문서 색인에서 연결했다.

## 구현 내용과 실험 기본값

아래 최초 구현의 성공 종료 유지와 운동 패널티 축소는 문서 끝의 후속 요청으로 변경되었다. 현재 v2는 성공 보상과 성공 DoneTerm 모두 사용하지 않는다. 운동 패널티는 v1 값을 유지하며 Reaching·Sweeping 누적 상한은 +200·+400이다.

1. `CurrentObjectReachProgress`는 기존 `ReachProgress`의 reset과 초기 거리 정규화를 상속한다. 매 step에는 현재 물체 바닥 중심과 EEF의 XYZ 거리를 사용하며 반경 10cm 구까지의 최소 거리를 갱신한 만큼만 지급한다. 기존 `ReachProgress`의 초기 위치 기반 동작은 유지한다.
2. `PlanarGoalProgress`는 초기 XY 목표 거리에서 허용 오차 1cm까지 줄여야 하는 거리를 기준으로, 새 episode 최고 진전만 보상한다. 초기에 이미 목표 안이면 budget은 0이다. 정지·후퇴·기존 기록으로 복귀에는 추가 보상이 없다.
3. `OmniV2RewardsCfg`의 Reaching 누적 상한은 +20, Sweeping 누적 상한은 +40이다. 두 함수의 `/step_dt`가 RewardManager의 시간 곱셈을 상쇄한다. 기존의 음의 목표 거리 비용은 v2에서 사용하지 않는다. 음의 상시 목표 비용만 누적되는 상황에서 조기 종료가 비용을 줄이는 유인을 피하기 위한 선택이다.
4. Arm action rate·joint velocity는 −0.003, Hand action rate는 −0.003, Hand joint velocity는 −0.001이다. 운동 비용을 기존의 1/10로 낮추고 object tilt −2, shelf collision −0.5는 유지한다.
5. `time`, `success`, `failure` 보상을 `None`으로 제거한다. 10초 제한·성공 hold·실패 종료와 3 rad/s Arm 속도 임계값은 유지한다. 실제 성공 판정과 종료 보상은 별개다.
6. Gym ID `Isaac-Inspire-Sweep-Omni-v2`를 등록하고 `InspireSweepOmniV2EnvCfg`가 v1을 상속한다. Scene, reset, 41D 관측, 8D action, 물성, controller, timing과 PPO는 유지한다. 로그 분리를 위해 `--experiment_name inspire_sweep_omni_v2`를 사용한다.

수치 +20/+40과 운동 비용 변경은 사용자 요구를 구체화하기 위해 에이전트가 선택한 실험 기본값이다. 성능이 검증된 최적값이나 교수의 확정 사양을 의미하지 않는다. Reaching이 전역 최적 정책을 보장한다는 주장도 하지 않는다. 정확한 식은 [환경 안내](../../02_implementation/08_ACTIVE_ENVIRONMENTS.md#v2-보상-계약)에 있다.

현재 물체 GT는 reward에서 사용하며 actor·critic은 v1과 같은 live-object 41D 관측이다. 최종 Blind 정책 성능을 주장하지 않는다. Reaching은 물체가 EEF 쪽으로 움직인 상대 접근도 보상할 수 있다. 목표 진전 항 단독으로 접촉·직립을 검증하지 않으며, 기존 물리 비용·종료 조건을 함께 사용한다. Reaching budget 소진 후 유지 접촉만으로 추가 접근 보상을 지급하지 않는다.

## 실제 실행한 검증

시뮬레이터를 시작하지 않는 CPU harness에서 실제 MDP 함수, Isaac Lab tensor math, 공식 configclass와 manager term 설정을 검사했다. `env_isaaclab`에는 앞선 점검에서 NumPy가 없어, CPU 의존성이 설치된 `jd_isaaclab` Python을 사용했다.

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

최종 결과: **76 passed**. 최초 두 파일 검증은 35 passed, 회귀 범위 확대 후 75 passed였으며, 접근 +20 → 대기 0 → 목표 이동 +40의 통합 시나리오를 추가한 뒤 위 최종 명령을 실행했다.

검증 내용:

- 현재 물체 위치 반영, v0/v1 초기 위치 보상 유지, 정지·동일 상대 거리에서 이동·왕복 중복 지급 방지.
- 0.01/0.02/0.05초 제어 주기에서 budget 동일, 목표 XY 방향 대칭, 이미 가까운 reset에서 보상 0.
- 개별 환경 reset 시 다른 환경 기록 보존, command reset 이전 scene snapshot 사용과 첫 transition 진전 반영.
- v2 등록, manager 인자 바인딩, 세 terminal/time 보상의 제거, v1 scene·관측·action·종료 조건 유지와 인스턴스 격리.
- 기존 goal termination·spawn 및 configuration/task 계약 회귀 검사.

추가 검증은 Workspace 루트에서 다음 명령으로 수행했고 모두 통과했다.

```bash
python -B example/Contact-Rich-Manipulation-Context/scripts/check_markdown_math.py \
  src/inspire_sweep_baseline/README.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  example/Contact-Rich-Manipulation-Context/docs/logs/2026-10-15_omni_v2_rewards.md \
  example/Contact-Rich-Manipulation-Context/docs/README.md \
  example/Contact-Rich-Manipulation-Context/docs/03_DECISIONS_AND_OPEN_QUESTIONS.md
git diff --check
git -C example/Contact-Rich-Manipulation-Context diff --check
```

결과: `Markdown math check passed: 5 file(s)`, 양쪽 `git diff --check` 오류 없음.

## 미검증 범위와 다음 확인

- Isaac Sim 환경 생성, GPU 물리, 실제 reward manager·센서와 통합한 학습·재생은 실행하지 않았다. 이번 작업은 학습 실행 요청이 아니라 환경 구성 요청이다.
- 새로운 학습 run·checkpoint·성공률은 없다. 기존 체크포인트 재개보다 새 v2 run으로 비교할 것을 권한다.
- Hand 분포 표준편차·entropy·clamp 문제와 action/controller 문제는 변경하지 않았다.
- 다음 run에서 접근 거리 최소값·물체 목표 거리·진전 보상 누적량·팔 속도 종료·Hand 표준편차를 확인한다. 접근 우선 학습과 물체 이동은 실제 실험으로 검증해야 한다.

## 후속 요청 — v2 success DoneTerm 제거

2026-10-15 후속 사용자 요청에 따라 `InspireSweepOmniV2EnvCfg.__post_init__`에서 `self.terminations.success = None`을 설정했다. 목표 도달과 기존 성공 hold 조건으로는 종료하지 않는다. 시간 초과·실패 종료는 유지하며 v0/v1의 성공 종료와 보상은 변경하지 않았다. 활성 환경 안내·패키지 README·결정 기록도 현재 동작에 맞췄다.

아래 명령을 실제 실행했고 **28 passed in 1.34s**였다. v2의 성공 항 제거, 다른 종료 조건 보존, v1 인스턴스 격리와 기존 종료 계산을 CPU에서 검증했다. Isaac Sim 학습·재생은 실행하지 않았다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py
```

변경 Markdown 4개(패키지 README, 활성 환경 안내, 결정 목록, 본 로그)에 기존 수식 검사기를 실행하고 양쪽 저장소 `git diff --check`를 재실행했다. 모두 통과했다.

## 후속 정정 — 운동 패널티 원복과 진전 보상 강화

사용자는 네 운동 패널티를 변경하면 안 되며 다른 보상이 약하면 해당 보상 weight를 높이라고 지시했다. 최초 구현에서 접근을 우선하도록 패널티를 낮춘 것은 이 기준에 맞지 않아 v2의 네 weight override를 삭제했다. v1의 Arm action rate −0.03, Hand action rate −0.03, Arm joint velocity −0.03, Hand joint velocity −0.01을 그대로 상속한다. 앞으로 이 요청 범위에서는 해당 패널티를 변경하지 않는다.

Reaching weight는 20 → 200, 목표 진전 weight는 40 → 400으로 변경했다. 네 운동 패널티 대비 진전 보상의 비율을 앞선 설정과 같게 맞추는 10배 조정이다. Tilt·선반 비용은 그대로이므로 전체 보상식의 일괄 배율 조정과는 다르다. 보상 계산식과 성공 DoneTerm 제거는 유지했다. 이는 학습 성능을 검증한 계수가 아니다.

회귀 테스트에서 네 운동 항목의 전체 설정이 v1과 같은지 검사하도록 변경했고, 접근 +200 → 대기 0 → 목표 이동 +400을 검증했다. 위 '실제 실행한 검증'에 기재한 6개 테스트 파일의 명령을 다시 실행한 결과 **76 passed in 1.59s**였다. Isaac Sim 학습·재생은 실행하지 않았다. 변경 Markdown 4개의 수식 검사와 양쪽 저장소 `git diff --check`도 통과했다.
