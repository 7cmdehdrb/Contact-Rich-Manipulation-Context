# 2026-10-23 Fusion Holding v2 — 목표 반경·접촉 보상·상속 변경

[개발 로그](README.md) · [환경 계약과 실행](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V2_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

## 요청과 기준 상태

사용자는 Holding-v1 기반 v2 추가, 목표 위치 허용 반경2cm→1cm→0.5cm, 목표 유지 계수2배, fade 없는 새 손 접촉 함수와 목표 영역 내 접촉 간주를 요청했다. 추가 확인에서 성공·목표 유지 보상·접촉 간주의 반경을 통일하는 것으로 확정했다. 기존 반경3배까지 주는 보상 cutoff는 v2에서 사용하지 않는다.

Workspace 기준 commit은 `635beb42988084555c2484fbbd0a3549631b4e44`, 문서 submodule은 `fdad45709030783e3d1d57cb8e869174f1a660f5`다. 작업 시작 시 상위 저장소는 문서 submodule 포인터 차이만 있었으며 submodule 내부 작업트리는 깨끗했다. 기존 commit과 사용자 작업을 보존하고 commit/push는 수행하지 않았다.

## 구현

- 등록: `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v2`, `FusionHoldingV2EnvCfg`→`FusionHoldingV1EnvCfg`, runtime `ContactSweepClutterFusionV1_0Env`, PPO `FusionHoldingV2PPORunnerCfg`→`FusionHoldingV1PPORunnerCfg`.
- 공통 반경:0~5,000은0.02m,5,000~10,000은0.02→0.01m,10,000~20,000은0.01→0.005m, 이후0.005m. 절대 iteration 기반이며 매 iteration 선형 갱신한다.
- `goal_hold`는 반경 안에서만 거리·속도 Gaussian을 반환하고 weight4를 사용한다. Gaussian 위치 척도도 공통 반경이다. 부모의 위치 척도 일정은 비활성화하고 속도 척도 일정은 유지한다.
- 새 `hand_contact_or_goal`: 최신·유한 whole-hand 합력≥0.01N 또는 유효한 목표 반경 안이면1, 아니면0. weight1.45, 시간당 계산·RewardManager의dt 적용은 유지한다. 두 조건의OR이므로 중복 보상은 없다. fade 인수·감쇠는 없고 촉각 관측은 변경하지 않는다.
- `ScheduledHoldingSuccess`는 reward manager의 현재 반경을 읽는다. 기존0.01m/s·3초·선반 유효성·실패 제외·부분 reset을 유지한다.
- OSC-v2의EnvCfg/PPO를 Holding-v2로 변경했다. UR10 Reach 제어 설정은 유지한다.
- ObjectRandom-v1의EnvCfg/PPO를OSC-v2로 변경하고, 전용 커리큘럼을Holding-v2 기반으로 바꾸었다. 개수 일정만 끄고Gray7/White7·기존 자산/물성/reset·16슬롯을 유지한다.
- 기존Holding-v0/v1·OSC-v0/v1의 동작과 로컬raw 운동 페널티 네 계수는 변경하지 않았다. 학습 로그는 변경하지 않았다.

## 실제 검증

Workspace 루트에서 다음 명령을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v2.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v0.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_osc.py
```

초기 집중 검증: **23 passed**. 이후OSC-v2 manager/Arm 상속 검사1개를 추가한 최종 코드로 다음 전체 활성 패키지 검증을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests
```

결과: **650 passed, 3 failed, 4 warnings**,29.15초. 새Holding-v2와 변경된OSC 상속 검사는 모두 통과했다. 검증 범위는 각 커리큘럼 경계·선형 중간값·checkpoint iteration 되감기·XY 원 경계 포함·3초 타이머·반경 축소 시 초기화·속도/실패 제외·부분 reset·접촉 임계값·stale/NaN 센서·목표 내 무접촉·중복 지급 방지·weight/dt·등록·부모 보존·ObjectRandom 일정 전달이다. 기존PPO/인코더/export 테스트도 통과했다.

실패3건은 변경 전HEAD를 `/tmp/holding_v2_baseline_635beb4`에 `git archive`로 추출한 별도 복사본에서도 같은 오류로 재현했다. 작업트리의 실패와 분리하여 확인했으며 이번 변경에서 수정하지 않았다.

| 기존 실패 | 원인 |
| --- | --- |
| `test_contact_sweep_clutter_mdp.py::test_physics_reset_uses_object_major_rows_and_preserves_other_environments` | 테스트용env에cfg가 없어물리 초기화의env.cfg 접근 실패 |
| `test_contact_sweep_clutter_mdp.py::test_clutter_physics_preserves_parent_sampling_and_exact_object_properties` | 같은env.cfg 누락 |
| `test_termination_debug.py::test_tasks_use_their_registered_runtime_family` | 기존Fusion/Holding 등록에 비해 기대runtime 목록이 누락됨 |

변경 전 재현 명령:

```bash
mkdir -p /tmp/holding_v2_baseline_635beb4
git archive HEAD src/inspire_sweep_baseline src/scene_randomization pytest.ini | tar -x -C /tmp/holding_v2_baseline_635beb4
ln -s /home/min/7cmdehdrb/grad/IsaacLab /tmp/holding_v2_baseline_635beb4/IsaacLab
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  /tmp/holding_v2_baseline_635beb4/src/inspire_sweep_baseline/tests/test_contact_sweep_clutter_mdp.py::test_physics_reset_uses_object_major_rows_and_preserves_other_environments \
  /tmp/holding_v2_baseline_635beb4/src/inspire_sweep_baseline/tests/test_contact_sweep_clutter_mdp.py::test_clutter_physics_preserves_parent_sampling_and_exact_object_properties \
  /tmp/holding_v2_baseline_635beb4/src/inspire_sweep_baseline/tests/test_termination_debug.py::test_tasks_use_their_registered_runtime_family
```

결과는3 failed,1.40초로 같은 기존 오류를 재현했다.

추가 정적 검사: 변경·추가 Python16개를 `ast.parse`로 검사하여 통과했다. 변경 Markdown10개에 `00_guidelines/scripts/check_markdown_math.py`를 실행하여 통과했고 상대 파일 링크 누락은0건이었다. 상위 저장소와 문서 submodule 각각의 `git diff --check`도 통과했다. GPU probe는 구문 검사만 수행했다.

## 미검증과 다음 확인

`nvidia-smi -L`을 실행했지만 NVIDIA driver와 통신하지 못했다. 이 세션에서는 GPU Scene 생성·step·PPO 학습·play를 실행하지 않았다. 갱신한 `_fusion_holding_v1_probe.py`와 `_fusion_holding_osc_v2_probe.py`도 GPU 실행은 미검증이다. CPU 검증을 접촉 물리나 학습 성공의 근거로 해석하지 않는다.

GPU 환경에서 Holding-v2→OSC-v2→ObjectRandom-v1 순으로 짧은 reset/step과 학습을 확인한다. 기존 OSC-v1 기반 ObjectRandom-v1 checkpoint는 제어 의미가 변경되어 같은 동작을 보장하지 않는다. 장기 성공률·물체 안정성·실물 성능은 미검증이다.
