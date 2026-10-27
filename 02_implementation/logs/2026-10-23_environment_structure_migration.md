# 2026-10-23 Inspire Sweep 환경 파일 구조 통합

[개발 로그](README.md) · [구조 지침](../../00_guidelines/12_ENVIRONMENT_FILE_STRUCTURE.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

상태: **구조 이관 검증 완료, 기존 ObjectRandom 후기 배치 오류 확인**.45개 설정 동등성·초기 단계 GPU/PPO·대표3개 `train.py` 검사는 통과했다. 그러나 최신 ObjectRandom2개 task의16개 장애물 reset 실패가 이관 전 원본에서도 재현되어, 환경 전체의 무오류를 선언하지 않는다. 사용자의 테스트 중단 요청을 지킨 뒤, VPN 연결 및 재개 지시에 따라 검증했다. 새 환경 구현, 학습 목표·보상·제어·배치 규칙 변경은 이번 구조 정리 범위에 포함하지 않는다.

## 요청과 확정한 구조

사용자는 `src/inspire_sweep_baseline`의 환경별 디렉터리와 패키지 루트의 EnvCfg 파일이 혼재한 상태를 통합하도록 요청했다. 기존에 동작하던 학습의 보존을 최우선으로 하며 Contact Sweep Clutter Fusion·Holding 계열을 중점 검증한다.

Cfg는 `mdp/actions`, `observations`, `commands`, `events`, `rewards`, `curricula`, `terminations`에, 계산은 각 `*_functions`에 둔다. 같은 계열의 v0/v1/v2 등은 역할별 같은 파일에 모은다. EnvCfg 조합은 `envs/`, PPO Cfg·모델·runner는 `agent/`에 둔다. 사용자 추가 확인으로 runtime Env/lifecycle/telemetry는 `runtime/`, 공유 계산·상태는 `mdp/common/`, SceneCfg는 `assets/scenes/`에 둔다.

이전 module 경로를 보존하는 호환 layer는 만들지 않는다. 저장소 안의 import·등록 문자열·실행기·검사·현행 문서 참조를 새 위치로 갱신한다. Gym task ID, 환경 계약, 기존 클래스의 역할과 버전은 유지한다. 세부 배치와 향후 환경 추가 절차는 [구조 지침](../../00_guidelines/12_ENVIRONMENT_FILE_STRUCTURE.md)을 따른다.

## 기준 commit과 사용자 작업

| 항목 | 이관 전 상태 |
| --- | --- |
| 루트 HEAD | `a30d0b4d92a7bd3c50b8d03516f1ada056da85c8` |
| 문서 submodule HEAD | `4d1158538eb9e6be69a6e0c18e772696169946cd` |
| 브랜치 | 루트 `main`, 문서 submodule detached HEAD |
| 기존 미추적 파일 | `docs/plan/PLAN5.md` 보존 |
| 학습 로그 | 정리·이동·삭제하지 않음. `logs/rsl_rl` 보존 |

복구는 위 commit의 별도 worktree에서 확인한다. 현재 작업트리의 변경을 `reset`·`clean`으로 제거하지 않는다. 실제 복구 명령 예시와 submodule·미추적 파일의 경계는 [복구 안내](../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/00_guidelines/12_ENVIRONMENT_FILE_STRUCTURE.md.txt)에 기록했다. 이 작업에서 commit·push·복구 실행을 완료했다는 뜻은 아니다.

## 이관 전 CPU 검증

Windows PowerShell, workspace 루트에서 다음 명령을 실제 실행했다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONUTF8='1'
Remove-Item Env:PYTHONPATH,Env:ROS_PACKAGE_PATH,Env:AMENT_PREFIX_PATH -ErrorAction SilentlyContinue
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests
```

결과: **645 passed, 6 failed, 4 skipped, 4 warnings, 35.60초**. 소스 이동 전에 실행한 기준 결과다. 실패를 이번 이관의 회귀로 분류하지 않는다.

| 기존 실패 | 확인한 원인 |
| --- | --- |
| `test_clutter_ft_telemetry.py::test_requested_checkpoint_loads_strictly_and_runs_cpu_inference` | 지정된 과거 `logs/backup/.../model_12800.pt` 부재 |
| `test_contact_sweep_clutter_mdp.py::test_physics_reset_uses_object_major_rows_and_preserves_other_environments` | 기존 mock에 `env.cfg`가 없음 |
| `test_contact_sweep_clutter_mdp.py::test_clutter_physics_preserves_parent_sampling_and_exact_object_properties` | 같은 `env.cfg` mock 누락 |
| `test_termination_debug.py::test_tasks_use_their_registered_runtime_family` | 최신 Fusion/Holding task가 기대 runtime 표에 누락됨 |
| `test_training_recovery.py::test_ctrl_c_stops_real_coordinator_without_respawning` | Windows subprocess의 `SIGINT` 비호환 |
| `test_training_recovery.py::test_output_failure_reaps_worker` | Windows에 `os.killpg`가 없음 |

4개 skip은 `INSPIRE_SWEEP_USD_TEST_PYTHON` 미설정과 fallback Python 부재에 따른 USD·material·spawner·tactile geometry probe다. 4개 warning은 모델 export의 Torch ONNX deprecation이다. 기존 테스트 탐색에 포함된 recovery-script 단위 검사는 실행했으나 실제 학습·자동 복구 실행은 하지 않았다. 학습 실행 정책은 계속 `scripts/train.py`다.

명령·정확한 실패 node ID·집계는 workspace 로컬 `outputs/structure_migration/baseline_pytest.txt`에 저장했다. 전체 stdout을 보존한 파일은 아니다.

## 이관 전 실제 설정 스냅샷

`outputs/structure_migration/snapshot_configs.py`를 작성하고 실제 Isaac Sim headless AppLauncher에서 등록된 Inspire task **45개**의 runtime class, EnvCfg·PPO class를 import했다. 각 설정을 인스턴스화하여 등록 문자열·상속 MRO·필드 순서·수치·callable·자산 경로를 `outputs/structure_migration/baseline_config.json`에 저장했다. **Task별 오류는 0개**이며 JSON 크기는35,900,927바이트다. 환경 생성·reset/step·학습은 이 검사에 포함하지 않았다.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONUTF8='1'
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -B outputs/structure_migration/snapshot_configs.py --output outputs/structure_migration/baseline_config.json *> outputs/structure_migration/baseline_launcher.log
```

Kit가 보호된 설치 경로의 `user.config.json`을 저장하지 못해 프로세스 종료 코드는1이었다. `SNAPSHOT_RESULT tasks=45 errors=0`과 완성된 JSON을 별도로 확인했다. task import·설정 생성 실패와 Kit 사용자 설정 저장 실패를 구분한다.

| 실행 환경 | 확인값 |
| --- | --- |
| Python | 3.11.15, `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe` |
| Isaac Sim / Isaac Lab | 5.1.0.0 / 0.54.4, Lab은 workspace editable 경로 |
| Torch / RSL-RL / Gymnasium | 2.7.0+cu128 / 5.0.1 / 1.2.1 |
| GPU | NVIDIA GeForce RTX4070, CUDA 가용 |
| 기본 shelf | `omniverse://192.168.0.13/Library/Shelf/Arena/Collected_speedrack_shape/speedrack_shape.usd` |

스냅샷·이동 대응표 등 `outputs/structure_migration/`의 파일은 현재 workspace의 검증 산출물이다. 문서 submodule만 전달하면 이 파일들은 포함되지 않는다.

## 이관 중 실행한 설정·문서 검사

사용자의 테스트 중단 요청 전에 이동 후 실제 설정 스냅샷을 생성했다. 등록45개 task의 설정 생성 오류는0개였으며, 이동 대응표로 module/symbol 참조를 연결한 비교에서 기준 스냅샷과 차이는0개였다. 이후 원래 선언 순서의 복원, 이동하지 않은 자산 파일의 원본 보존, `importlib.util` import 보완이 있었으며 **그 최종 상태의 스냅샷은 다시 실행하지 않았다.** 이 중간 동등성 결과를 최종 작업트리 전체의 검증 완료로 해석하지 않는다.

workspace 루트에서 실제 실행한 명령은 다음과 같다.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONUTF8='1'
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -B outputs/structure_migration/snapshot_configs.py --output outputs/structure_migration/migrated_config.json *> outputs/structure_migration/migrated_launcher.log
python -B outputs/structure_migration/compare_configs.py
```

비교 집계는 `tasks=45`, `task_errors=0`, `differences=0`이며 `outputs/structure_migration/config_comparison.json`에 저장했다. 원본·이관본 스냅샷과 비교 도구는 같은 디렉터리에 있다. 이관본 launcher도 같은 Kit `user.config.json` 저장 실패로 종료 코드1을 반환했으며, 완성된 설정 JSON의 task 오류는0개였다. 비교 명령은 종료 코드0을 반환했다.

CPU harness의 경로·fixture를 옮기는 중간 실행은 **69 passed, 3 failed, 9 errors, 1 warning, 8.05초** 상태에서 maxfail 기준으로 중단했다. 실제 명령은 다음과 같다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONUTF8='1'
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests --maxfail=12 --tb=short
```

이때 과거 checkpoint 부재는 기준 검사에서도 확인한 실패였다. 나머지는 population curriculum fixture, contacts의 이전 폴더, 등록 문자열 예상값 등 수정 중인 test harness 참조 문제였다. 전체 stdout 파일은 보존하지 않았다. 당시 fixture 수정이 진행 중이었으며, 이후 최종 suite는 실행하지 않았다. 이 결과를 최종 코드의 통과 집계나 학습 실패 판정으로 사용하지 않는다.

문서의 현재 코드 위치를 새 구조로 연결했다. 이전 파일에서 Cfg·함수가 나뉜 경우 Scene·보상·종료·관측 등의 실제 역할로 링크를 분리했다. 과거 로그의 당시 본문·명령·inline 경로는 유지하고, 클릭 가능한 코드 링크의 target을 새 위치로 갱신했다.

사용자 중단 요청 전에 다음 문서 검사를 실행했다. 실행 Python은 위 `env_isaaclab`의 Python이며 문서 저장소를 작업 디렉터리로 사용했다.

| 실제 명령 | 결과 |
| --- | --- |
| `python -B 00_guidelines/scripts/check_document_links.py` |361개 Markdown, 내부 링크4692개, 오류0개 |
| `python -B 00_guidelines/scripts/check_document_links.py --check-external` |외부 경로 오류89개. 모두 이관 전 문서 HEAD에도 같은 링크 target이 존재하는 과거 산출물·로그·PDF 부재. Inspire source 링크 누락0개 |
| `python -B 00_guidelines/scripts/check_markdown_math.py <변경한88개 Markdown>` |88개 파일 통과 |
| `git diff --check` |문서 저장소 통과. 패키지 README도 별도 통과 |

정확한 명령 인자와 결과는 workspace의 `outputs/structure_migration/document_validation.json`, `docs_internal_links.txt`, `docs_external_links.txt`, `docs_markdown_math.txt`, `docs_diff_check.txt`에 기록했다. 외부 오류를 없애기 위해 기존 로그·산출물을 생성·정리하지 않았다. 이후 이 로그의 상태·검증 결과를 갱신했으며 사용자 요청에 따라 추가 검사는 하지 않았다.

## 최종 소스 검토

테스트 중단 요청 이후에는 코드·참조·문서를 읽어 검토하고 수정했다. 운영 코드를 import하거나 simulator·pytest를 추가 실행하지 않았다. 패키지 최상위는 `agent`, `assets`, `mdp`, `envs`, `runtime`, `__init__.py`로 정리했으며, 기존 환경별 디렉터리와 그 안의 Python cache를 제거했다. 학습 로그 정리는 수행하지 않았다.

비 Fusion 심볼301개와 Fusion/Holding 심볼166개를 이동 대응표와 원본 소스에 대조했다. 수치·제어·관측·보상·종료·lifecycle의 변경은 발견하지 못했다. 같은 이름의 서로 다른 `goal_settling`, `staged_reward_threshold` 함수는 각각의 계산을 유지하고 Cfg import 별칭으로 구분한다. `envs/`에는9개 계열 파일의45개 EnvCfg만 두며, MDP Cfg와 term 구현은 분리했다.

소스 검토에서 발견한 `import importlib.util`의 하위 module import 누락을 수정했다. 이동한 두 기하 loader의 `parents[4]` 참조는 기존 `src/scene_randomization`을 가리킨다. `apply_realistic_physics`의 EnvCfg 타입 참조는 import 순환을 피하도록 지연 annotation과 `TYPE_CHECKING` import로 분리했다. 자산 데이터와 기존 `assets/` 구현 파일은 원본을 보존했다.

등록 정보는 module 경로 변경 외 동일하다. 운영 코드의 상대 import514개와 활성 코드의 절대 import21개를 읽어 확인한 범위에서 제거된 module 참조는 발견하지 못했다. 외부 소비자 `src/inspire_tactile_validation/inspire_tactile_validation/experiment.py`의 tactile reader import·metadata 경로도 새 위치로 갱신했다. 상세 검토 기록은 workspace의 `outputs/structure_migration/source_review.txt`에 있다.

CPU 검사에는 현재 파일의 정의를 역할별로 읽는 테스트 전용 `_source_units.py`와 이름·import 대응표를 추가했다. 실행할 함수·클래스 본문을 복사해 보관하지 않으며, 운영 패키지의 이전 import 경로를 복원하는 기능도 제공하지 않는다. 기존 AST 기반 검사가 분리된 현재 정의를 읽도록 하는 보조 계층이다. 최종 테스트 코드 역시 재실행 전 상태다.

이 검토는 소스 수준의 확인이며 실제 학습·reset·step·checkpoint 재개 성공을 입증하지 않는다.

## 당시 사용자 후속 지시까지 보류한 검증

아래 검증은 사용자가 테스트를 재개하도록 요청한 뒤 실행한다.

- 최종 작업트리의 실제 import 및 전체45개 EnvCfg·PPO 스냅샷 비교: 이동한 module/symbol 경로만 대응시키고 설정값·필드 순서·MRO의 의미를 대조한다.
- CPU 계약·PPO 모델·save/load 검사: 기준645개 통과·6개 실패와 비교하고 원래 문제와 이관 중 발생한 문제를 구분한다.
- Fusion·Holding 환경 생성 및 짧은 reset/step/PPO 연결: 검증 task·환경 수·step·seed·자산 경로와 한계를 기록한다.
- 자산 경로: 이동에 취약한 `__file__` 기반 scene generator·visibility 참조, robot USD·tactile JSON·package data를 확인한다.
- 최종 문서 재검사: 지침·로그 색인, 활성 환경·패키지 README의 현재 위치, 내부·외부 링크 및 변경 Markdown 수식을 확인한다.

장기 학습 성능, 실물 동작, 누락된 과거 checkpoint의 실제 복원은 아직 검증하지 않았다. 학습 로그를 정리하거나 기존 산출물을 덮어쓰는 작업은 수행하지 않는다.

## VPN 연결 후 재검증 — 2026-10-23

사용자가 VPN 연결을 알리고 앞서 보류한 테스트의 실행을 요청했다. 샌드박스 내부에서는 외부 자산을 읽지 못했지만, 샌드박스 밖의 `Test-NetConnection 192.168.0.13 -Port 3009`는 VPN 인터페이스 `irol`, source `192.168.0.251`에서 성공했다. GPU 실행은 승인된 샌드박스 외 실행으로 전환했다. 선반 경로·자산·환경 설정을 대체하거나 변경하지 않았다.

최종 소스의45개 등록 task를 실제 Isaac launcher에서 다시 import하고 EnvCfg·PPO를 생성했다. `resumed_snapshot.log`의 결과는 `tasks=45 errors=0`이며, `compare_configs.py`는 **45개, 오류0개, 차이0개**를 보고했다. 원본 경로와 현재 경로만 이동 대응표로 연결했고 필드 값·순서·상속·callable의 의미를 보존했다. 이 snapshot 프로세스도 설치 경로의 Kit 사용자 설정 저장 권한으로 종료 코드1이었다. 이후 실제 GPU probe에는 `--kit_args=--/app/userConfigPath=C:/python/Contact-Rich-Manipulation/outputs/structure_migration/kit_user.config.json`을 지정했다.

### CPU 테스트 수정과 결과

첫 전체 재실행은633 passed·18 failed·4 skipped였다. 새 실패12개는 분리된 layout 좌표 함수의 테스트 참조, 합쳐진 runtime에서 검사할 클래스 선택, 옛 등록 경로 예상값, CPU schedule 검사에서 불필요한 simulator module까지 import한 harness 문제였다. 실제 현재 정의를 검사하도록 테스트 참조를 수정했다. 기존 실패 중 물리 mock 두 개에 실제 환경에 존재하는 `cfg.obstacle_observation_slots=10`을 추가하고, 등록 runtime 예상표에 누락되었던 v1_4·Holding9개를 추가했다. 운영 코드의 수치·함수 본문·설정은 이 재검증 과정에서 변경하지 않았다.

수정 후 전체 suite는 **648 passed·3 failed·4 skipped·4 warnings,43.91초**였다. 남은3개 실패는 모두 이관 전에도 실패했던 다음 항목이다. 테스트를 통과시키기 위해 이 assertion을 삭제하거나 완화하지 않았다.

| 테스트 | 현재 실행을 완료할 수 없는 이유 |
| --- | --- |
| `test_requested_checkpoint_loads_strictly_and_runs_cpu_inference` | `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Curriculum-v1/2026-10-20_22-49-30/model_12800.pt` 부재. 새 checkpoint로 대신 통과 처리하지 않음 |
| `test_ctrl_c_stops_real_coordinator_without_respawning` | 사용 중단된 `train_resilient.py`의 POSIX SIGINT 검사. Windows `subprocess.send_signal(SIGINT)` 미지원 |
| `test_output_failure_reaps_worker` | 같은 보관 실행기의 POSIX `os.killpg` 검사. Windows에 API가 없음 |

설치된 Isaac의 USD 라이브러리를 테스트 subprocess에만 연결하여 이전에 skip되던 USD 자산 closure·material·spawner·촉각 geometry 검사도 실행했다. `outputs/structure_migration/usd_bootstrap/sitecustomize.py`는 설치 파일이나 운영 package를 변경하지 않는다. 별도5개 검사는 모두 통과했고, 위3개를 명시적으로 deselect한 통합 실행은 **652 passed·3 deselected·0 skipped·4 warnings,43.97초**였다. 경고4개는 기존 Torch ONNX deprecation이다.

실제 최종 통합 명령은 다음과 같다. 앞선 전체 실패 기록은 `resumed_pytest_final.log`, 실행 가능한 전체 통과 기록은 `resumed_available_suite.log`, 별도 USD 결과는 `resumed_usd.log`에 보존한다.

```powershell
$env:PYTHONPATH='C:/python/Contact-Rich-Manipulation/outputs/structure_migration/usd_bootstrap'
$env:INSPIRE_SWEEP_USD_TEST_PYTHON='C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONUTF8='1'
Remove-Item Env:ROS_PACKAGE_PATH,Env:AMENT_PREFIX_PATH -ErrorAction SilentlyContinue
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests --deselect src/inspire_sweep_baseline/tests/test_clutter_ft_telemetry.py::test_requested_checkpoint_loads_strictly_and_runs_cpu_inference --deselect src/inspire_sweep_baseline/tests/test_training_recovery.py::test_ctrl_c_stops_real_coordinator_without_respawning --deselect src/inspire_sweep_baseline/tests/test_training_recovery.py::test_output_failure_reaps_worker --tb=short
```

### 실제 GPU 환경과 PPO

Holding v2의 기존 `_fusion_holding_v1_probe.py`는 실제 자산으로 환경 생성·32 step·actor/critic encoder·부분 reset 검사를 통과했다. 같은 공통 계약을 전체45개 등록 환경에 적용하는 검증은 `outputs/structure_migration/runtime_probe.py`, 순차 실행기는 `run_runtime_matrix.py`에 있다. 별도 환경 구현이나 자동 복구 실행기가 아니며, 등록된 실제 환경과 PPO runner를 그대로 실행한다. 각 task는 별도 프로세스로 실행하고 실패를 재시도로 숨기지 않는다.

공통 조건은 RTX4070·CUDA, seed42,4 environments,32 step이다. 관측·보상·관절 위치·적용 토크의 유한성, 부분 reset 시 다른 환경의 goal·initial snapshot 보존, timeout 자동 reset을 검사한다. 이어서 steps_per_env4·epoch1·minibatch1의 PPO2 iterations를 실행하고 actor parameter의 실제 갱신 및 actor/critic parameter 유한성을 확인한다. 저장 뒤 parameter를 의도적으로 변경한 후 checkpoint를 load하여 actor/critic state_dict의 정확한 복원과 재추론·물리 step을 검사한다. 이 작은 rollout 설정은 검증용이며 등록된 기본 PPO 설정은 변경하지 않는다.

task별 명령·종료 코드·결과는 `runtime_matrix.json`, task별 상세 항목·shape·checkpoint 경로는 `runtime/<task>/probe.json`, stdout·stderr는 같은 폴더의 `process.log`에 기록한다. **45/45개가 모두 통과했고 프로세스 종료 코드도 모두0**이다. 이 결과의 커리큘럼 범위는 초기 iteration0/1이다.

| EnvCfg 계열 파일 | 통과 task 수 |
| --- | --- |
| `sweep_envs.py` |4 |
| `sweep_omni_envs.py` |6 |
| `sweep_omni_renewal_envs.py` |9 |
| `contact_sweep_envs.py` |1 |
| `contact_sweep_clutter_envs.py` |5 |
| `contact_sweep_clutter_fusion_envs.py` |11 |
| `contact_sweep_clutter_fusion_holding_envs.py` |3 |
| `contact_sweep_clutter_fusion_holding_osc_envs.py` |3 |
| `contact_sweep_clutter_fusion_holding_osc_object_random_envs.py` |3 |

실제 `scripts/train.py`도 Baseline v0, Clutter Curriculum v1, Holding OSC ObjectRandom v1에서 각각4 environments·2 iterations로 실행하여 모두 종료 코드0, `training_status.json`의 `completed`, `model_1.pt` 생성을 확인했다. 명령 전체는 `train_launcher.json`에 기록했다. 기존 `logs/rsl_rl`을 건드리지 않기 위해 `train.py`의 기존 private 출력 디렉터리 인자 `--resilient-attempt-dir`와 절대 iteration 인자만 사용했다. `train_resilient.py`를 학습에 실행하거나 자동 재시작하지 않았다. 기록은 `outputs/structure_migration/train_launcher/<task>/`에만 저장했다.

```powershell
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -B outputs/structure_migration/run_runtime_matrix.py
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -B outputs/structure_migration/run_launcher_checks.py
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -B outputs/structure_migration/run_final_probes.py
```

이 helper들은 같은 GPU에서 동시에 simulator를 실행하지 않도록 앞 단계의 완료를 기다린다. 재시도·자동 복구 기능은 없다. 첫 두 명령은 종료 코드0이었다. 세 번째 명령은 아래의 오래된 probe 예상값 및 실제 후기 배치 실패로 종료 코드1이었다. 최초 실패 기록도 그대로 보존한다.

추가 상세 probe의 오래된 수치를 이관 전 스냅샷 및 원본 코드와 대조해 수정했다. Fusion v0의 `push_fast`는1.0, 비교 대상 Clutter v2는0.8이며, pushing penalty는−5, 일정 간격은300, goal hold 기간은500이었다. v1_0의 활성 curriculum은8개, 초기 wrench 허용값은5000 N·500 N·m, 가속도 허용값은100, goal tolerance는0.01 고정이었다. `hand_contact`의 fade width0은 거리 감쇠 비활성이고0.015는 선택 가능한 선형 감쇠다. 이 값들은 이관 전에 이미 존재했으며 환경 코드를 바꾸지 않고 검사 예상값·호출 인자를 원래 계약에 맞췄다. 수정 도중의 실패 report도 별도로 보존했다.

Fusion v0 상세 probe의 재실행은 `fusion_v0_detailed_corrected/probe.json`에서 통과했다. 실제 goal 극좌표·속도 계산·wrench history/budget·부분 및 timeout reset·curriculum boundary·PPO299→300을 검사했다. Holding OSC v2의 실제 base-frame·encoder·부분 reset 상세 검사도 `holding_osc_v2_frames/probe.json`에서 통과했다.

Fusion v1_0 상세 probe도 `fusion_v1_0_detailed_final2/probe.json`에서 통과하고 종료 코드0을 확인했다. 실제 Hand/obstacle 접촉과 target identity 분리, 촉각, 활성 물체 수·비활성 물체의 gravity flag·새 활성 물체의 중력 반응, native PhysX 가속도, reward history·부분/timeout reset, curriculum 경계·역방향 복원을 검사했다. PPO2499→2500 갱신 후7500으로 바꾸었다가2500 checkpoint를 복원하여 첫 reset의 인구수·보상 일정까지 확인했다. 초기 예상값 오류 및 width0을 경계 판정으로 잘못 해석한 중간 검사 실패도 보존하며, 최종 검사는 원본 함수의 명시적 계약에 따라 width0의 감쇠 비활성과 width0.015의 선형 감쇠를 각각 검증한다.

최종 snapshot은 쓰기 가능한 Kit 사용자 설정 경로로 다시 실행하여 **프로세스 종료 코드0,45개 생성 오류0, 비교 차이0**을 확인했다. `final_snapshot.log`, `final_config_comparison.log`, `config_comparison.json`에 기록했다. 이 결과가 앞의 보호된 설치 경로 저장 실패와 중간 snapshot을 대체하는 최종 설정 검증이다. 기존 자산18개는 이관 전과 바이트 단위로 동일하며 `asset_preservation.json`에 기록했다.

### 기존 오류: ObjectRandom의16개 장애물 reset

다음 두 task를 seed42·4 environments·curriculum iteration22500으로 설정하고 reset하면 실패했다.22500회 학습을 실행한 결과가 아니라, 해당 checkpoint 단계로 재개할 때와 같이 커리큘럼을 적용한 뒤 reset한 결과다.

- `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v1`
- `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-ObjectRandom-Test-v0`

최종 인구수는 gray8·white8·target1이다. 실제 크기와 yaw를 반영한 비중첩 배치를200번 제안해도 env0에서 유효한 배치를 얻지 못해 다음 오류가 발생했다.

```text
RuntimeError: No non-overlapping enlarged layout for env 0 after 200 attempts; target/goal unchanged
```

실패 지점은 [`sample_layout`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/contact_sweep_clutter_fusion_holding_osc_object_random_placement.py)이며 target·goal을 유지하면서 원래 zone generator의 proposal을 실제 oriented bounds로 거르는 단계다. 이 실패만으로 모든 seed의 배치가 불가능하다고 단정하지 않는다. 반복 횟수·물체 수·크기·목표 분포·배치 알고리즘을 바꾸지 않았다.

이관 전 전체 package를 `baseline_runtime/src/inspire_sweep_baseline/inspire_sweep_baseline`에 수정 없이 복사하고, 같은 상대 위치에 원본 `src/scene_randomization`을 두어 동일한 seed·task·GPU·자산·iteration으로 대조했다. **두 task 모두 같은 env0·200회 실패를 재현했다.** 새 파일 구조로 인한 회귀가 아니라 이관 전에도 존재하던 후기 배치 문제다. 원본 source와 재현용 copy의 바이트 동일성도 확인한다. baseline을 만들기 위해 현재 작업트리를 되돌리거나 Git reset·clean을 실행하지 않았다.

```powershell
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -B outputs/structure_migration/baseline_reset_probe.py --headless --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v1 --kit_args=--/app/userConfigPath=C:/python/Contact-Rich-Manipulation/outputs/structure_migration/kit_user.config.json
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -B outputs/structure_migration/baseline_reset_probe.py --headless --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-ObjectRandom-Test-v0 --kit_args=--/app/userConfigPath=C:/python/Contact-Rich-Manipulation/outputs/structure_migration/kit_user.config.json
```

현재 실패 report는 `full_population_Holding-OSC-ObjectRandom-v1/probe.json`, `full_population_Holding-ObjectRandom-Test-v0/probe.json`, 원본 대조 report는 `baseline_reset_<task>.json`이며 각각의 stdout·traceback도 보존했다. 운영 동작 보존을 요청한 구조 정리 범위를 넘어서는 기존 배치 오류 수정 여부를 사용자에게 별도로 확인했다. 답변 전에는 배치 로직을 변경하지 않는다.

현재 판정은 **검사한 구조 이관·초기 학습 경로에서 회귀를 발견하지 못했으나, 기존 후기 배치 오류가 남아 전체 환경의 무오류는 확정할 수 없음**이다. 누락된 과거 checkpoint, POSIX 전용 보관 실행기 검사2개, 장기 수렴·성능·실물 동작도 별도 범위다.

전체 task 집합·각 필수 runtime 검사·상세 probe·기존 실패 원본 재현·자산 보존을 다시 집계한 기록은 `outputs/structure_migration/final_validation.json`이다. 집계기는 `summarize_validation.py`이며 실패를 통과로 바꾸지 않고 기존 후기 오류를 별도 결과로 기록한다.

기록 마감2026-10-24: 집계 명령은 종료 코드0이며 재현용 원본238개 파일의 바이트 동일성을 확인했다. `validate_documents.py` 재실행에서361개 Markdown·내부 링크4693개 오류0, 변경 Markdown88개 수식 검사 통과, 문서 및 루트 `git diff --check` 통과였다. 외부 경로 오류89개는 모두 이관 전 HEAD에도 있던 과거 산출물·로그·PDF 부재이며 Inspire source 링크 누락은0개였다. 결과는 `document_validation.json`, `docs_*.txt`, `final_root_diff_check.log`에 보존했다. 기존 `logs/rsl_rl`과 사용자 작업은 정리·이동·삭제하지 않았고 commit·push도 수행하지 않았다.
