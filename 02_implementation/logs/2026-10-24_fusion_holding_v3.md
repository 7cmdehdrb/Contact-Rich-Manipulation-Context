# Holding v3 · OSC v3 · ObjectRandom v2 개발·검증

후속 변경: 아래8/8 상한은 초기 구현·검증 당시 조건이다. 이후7/7 반복 검사에서도 실패해 사용자 지정에 따라 현재ObjectRandom-v2의 활성 상한을6/6으로 낮췄다. [반복 검사와 현재 상한](2026-10-24_object_random_v2_population_cap.md).

[로그 안내](README.md) · [환경 계약·학습 명령](../environments/FUSION_HOLDING_V3_FAMILY.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

날짜: 2026-10-24, Asia/Seoul. 사용자 요청은 목표 근처에서 성공을 회피하며 hold 보상을 연장하는 유인을 제한하고, 같은OSC 제어로 새 과업을 비교하며, 장애물 개수와 Gray 침범 커리큘럼을 추가하는 것이다. 구현과 장기 학습 결과를 구분한다.

## 기준과 보존 범위

작업 시작 시 workspace main HEAD는 `e3fe8e33f0757254ef7b44fc296c9fcb0d5bdd01`, 문서 submodule main HEAD는 `e8af2cf0089ca1f8d4ed44e13dc2995f4085b349`였다. 기존 workspace 변경은 `scripts/record_three_views.py`와 IsaacLab 내부 미추적 상태, 문서 변경은 로그 색인과 미추적 `2026-10-24_three_view_recording_config.md`였다. 해당 내용을 보존하며 로그 색인에는 새 항목만 추가했다. 커밋·push·학습 로그 정리를 수행하지 않았다.

## 구현

- 등록은 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v3`, `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v3`, `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v2`다. EnvCfg와PPO entry point·experiment를 추가했다. 직접 상속은 Holding-v2 → Holding-v3 → OSC-v3 → ObjectRandom-v2다.
- `FusionHoldingV3RewardsCfg.goal_hold`의 `CappedGoalSettling`은 보상률을 유지하고 지급 대상 step의 시간을 최대3초 누적한다. 이탈·재진입은 잔여 예산을 유지한다. 선택 episode reset만 해당 카운트를 초기화한다. 마지막 부분 step을 처리해dt가3초의 약수가 아니어도3초를 초과하지 않는다. weight4·성공3초·속도·공통 반경·접촉 간주와 나머지 보상은 유지한다.
- 현재OSC-v2 본문을 `mdp/common/contact_sweep_clutter_fusion_holding_osc_configuration.py:configure_reach_osc`로 옮겨v2/v3가 공유한다. 위치/회전 stiffness100/50, scale0.03/0.15, 관성 분리·중력 보상true 등 실제 적용값을 그대로 보존했다. 과거 문서의80/25·false 표기와 차이가 있었으므로 새 계약에는 코드값을 기록했다.
- ObjectRandom-v2는v1의 Scene/Event를 재사용한다. White3000·Gray4000부터 각2000간격으로 한 개씩 추가해 전체1000간격 교대를 구성한다. 최종8/8은16000에서 도달한다.
- Gray 패딩은6000에서0,6250에서0.625%,9000에서7.5%,12000에서15%다. `scheduled_value`의250간격 절대 iteration 계산을 사용한다. 최대1.545cm만큼 기존Red 반경10.3cm의 안쪽을 허용하며 새Gray 제외 반경은8.755cm다. Gray/rear 후보에만 적용하고 White 판정과 외곽Gray·물체 간격·접근 certificate·OBB·선반 검사는 유지한다. 진행 중 episode는 변경하지 않는다.
- 기존 로컬 `ClutterLayoutGenerator`에 역할별 구역 판정 hook을 추가하고 ObjectRandom용 파생 generator만 확장한다. 원본 `src/scene_randomization`은 수정하지 않았다. 단계별 generator cache를 제한하고, seeded reset에서 새 cache도 비워 재현성을 유지한다.
- Actor/Critic 입력·16슬롯 encoder·8D 행동·네 로컬 운동 페널티의 callable·raw 제곱합·계수는 유지한다. 전체 계약과 코드 위치는 [환경 문서](../environments/FUSION_HOLDING_V3_FAMILY.md)에 있다.

## CPU 검증

Workspace 루트에서Isaac Lab Conda Python을 사용했다. 기본 시스템Python에는pytest가 없어 아래 환경으로 실행했다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_fusion_holding_v0.py src/inspire_sweep_baseline/tests/test_fusion_holding_v2.py src/inspire_sweep_baseline/tests/test_fusion_holding_osc.py src/inspire_sweep_baseline/tests/test_object_random_geometry.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_fusion_holding_v3.py src/inspire_sweep_baseline/tests/test_clutter_layout.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests
```

첫 묶음42개, 새 동작·배치 묶음22개가 통과했다. 누적 지급 시간·목표 이탈·재진입·부분 reset·dt 경계, 종료 판정 후150번째 보상, 개수·패딩 일정의 경계·resume·되감기, White 불변과 기존Red 내부의 실제Gray 샘플 생성·간격을 확인했다.

전체 첫 실행은678 passed /4 failed /4 skipped였다. 새 등록3개가 기존runtime 검사 목록에 없어 발생한1개는 `test_termination_debug.py`에 신규ID를 추가해 수정했다. 나머지3개는 변경하지 않은 기존 코드·자료 조건의 실패다.

| 검사 | 확인한 실패 조건 |
| --- | --- |
| `test_clutter_ft_telemetry.py::test_requested_checkpoint_loads_strictly_and_runs_cpu_inference` | 요구하는 `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Curriculum-v1/2026-10-20_22-49-30/model_12800.pt`가 없음 |
| `test_training_recovery.py::test_ctrl_c_stops_real_coordinator_without_respawning` | Windows에서subprocess `SIGINT` 전송 미지원 |
| `test_training_recovery.py::test_output_failure_reaps_worker` | Windows에 `os.killpg`가 없음 |

해당3개를 제외한 전체 재실행은 **679 passed /4 skipped /3 deselected**,44.46초였다. 실제 명령은 다음과 같다. 전체 pytest 탐색은 기존 복구 코드의 임시 fake-worker 검사도 포함했다. 실제 학습은 실행하지 않았다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests --deselect src/inspire_sweep_baseline/tests/test_clutter_ft_telemetry.py::test_requested_checkpoint_loads_strictly_and_runs_cpu_inference --deselect src/inspire_sweep_baseline/tests/test_training_recovery.py::test_ctrl_c_stops_real_coordinator_without_respawning --deselect src/inspire_sweep_baseline/tests/test_training_recovery.py::test_output_failure_reaps_worker
```

## 실제 Isaac Sim 검증

실제 설치의AppLauncher·Gym registry·EnvCfg·PPO를 사용했다. CUDA RTX4070·Isaac Sim5.1·Windows D3D12다. 초기 sandbox 실행은Kit user config/cache 쓰기 제한으로 중단되었다. 정상 설치 캐시 쓰기를 허용한 재실행은 세 환경의 실제 import·설정 비교를 통과했다. `outputs/holding_v3_launcher_probe_retry.log`와 `outputs/fusion_holding_v3_validation/probe.json`에 기록했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -u src/inspire_sweep_baseline/tests/_fusion_holding_v3_probe.py --headless
```

직접 상속, Holding-v2 대비 goal_hold 외 설정 동일, OSC-v2/v3 actions·나머지 설정 동일, ObjectRandom-v1 대비 rewards/curriculum 외 설정 동일, 신규 PPO16슬롯·experiment, 네 운동 페널티 callable·계수를 확인했다.

처음에는 한 Kit 프로세스에서 환경을 순차 생성하는 harness를 사용했다. Holding-v3의 reset/10step 뒤 두 번째 환경 초기화에서 진행이 멈춰 해당 검증 프로세스만 종료했다. probe를 각 환경마다 새 프로세스로 실행하도록 수정했다. 아래 세 명령을 순차 실행했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -u src/inspire_sweep_baseline/tests/_fusion_holding_v3_probe.py --headless --smoke --task Holding-v3
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -u src/inspire_sweep_baseline/tests/_fusion_holding_v3_probe.py --headless --smoke --task Holding-OSC-v3
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -u src/inspire_sweep_baseline/tests/_fusion_holding_v3_probe.py --headless --smoke --task Holding-OSC-ObjectRandom-v2
```

각2환경·seed42·reset·10step의 관측/보상 유한성 검사를 모두 통과했다. Holding-v3·OSC-v3 프로세스는 exit0이다. ObjectRandom-v2는 추가로 iteration6000·9000·12000에서 reset을 통과했다. 로그는 `outputs/holding_v3_smoke_Holding-v3.log`, `outputs/holding_v3_smoke_Holding-OSC-v3.log`, `outputs/holding_v3_smoke_Holding-OSC-ObjectRandom-v2.log`다.

ObjectRandom의 iteration16000·Gray8/White8 reset은 **`No non-overlapping enlarged layout for env 0 after 200 attempts; target/goal unchanged`**로 실패했다. JSON 보고서에서 failed_iteration16000과 앞선 성공 단계를 확인했다. 예외 후 Kit 종료가 완료되지 않아 해당 검증 프로세스만 종료했다. 이관 전 ObjectRandom에서도16개 장애물 reset의 동일 형태 오류가 [기록](2026-10-23_environment_structure_migration.md#기존-오류-objectrandom의16개-장애물-reset)되어 있다. 같은 seed의 동일 장면을 기준 버전과 새로 A/B 비교한 것은 아니므로 원인 동일성을 확정하지 않는다. 타겟 재추출·장애물 수 감소·겹침 허용으로 우회하지 않았다.

패딩 단계·되감기·seeded reset 검증은 최대 밀도 단계를 제외하고 다음 명령으로 추가 확인했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -u src/inspire_sweep_baseline/tests/_fusion_holding_v3_probe.py --headless --smoke --task Holding-OSC-ObjectRandom-v2 --curriculum-iterations 6000 9000 12000 0
```

최종 실행은 exit0이다. 초기 reset/10step,6000·9000·12000·0의 정확한 활성 개수, iteration9000에서 동일 seed42로 반복한 reset의 물체 위치 재현성을 통과했다. `outputs/holding_v3_smoke_object_random_rewind.log`와 `outputs/fusion_holding_v3_validation/probe_Holding-OSC-ObjectRandom-v2.json`에 기록했다. 후자는 마지막 성공 실행 결과로 갱신되었으며 앞선 최대 밀도 실패는 위 기록을 따른다. cache 초기화 수정 후 관련 CPU24개도 통과했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_fusion_holding_v3.py src/inspire_sweep_baseline/tests/test_clutter_layout.py src/inspire_sweep_baseline/tests/test_termination_debug.py
```

## 문서 검증

변경 Markdown11개에 대해 수식 검사 통과, 상대 파일·anchor·외부 workspace 참조 오류0을 확인했다. HTTP URL의 접근 성공을 검사한 것은 아니다. 두 저장소의 `git diff --check`도 통과했다. 검사 명령은 다음과 같다. 처음에 `core.autocrlf=false`를 강제한 검사는 기존CRLF를 새 trailing whitespace로 해석했으므로, 저장소의 원래 설정으로 다시 검사해 통과 여부를 판정했다. 전역Git 설정과 기존 파일의 줄바꿈은 변경하지 않았다.

```powershell
$contextRoot='C:/python/Contact-Rich-Manipulation/example/Contact-Rich-Manipulation-Context'
$changedDocs=@(
  '01_plan/00_HANDOFF_BRIEF.md', '01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md',
  '01_plan/04_NEXT_ACTIONS.md', '02_implementation/08_ACTIVE_ENVIRONMENTS.md',
  '02_implementation/environments/ENVIRONMENT_EVOLUTION.md',
  '02_implementation/environments/FUSION_HOLDING_FAMILY.md',
  '02_implementation/environments/README.md',
  '02_implementation/environments/FUSION_HOLDING_V3_FAMILY.md',
  '02_implementation/logs/README.md', '02_implementation/logs/2026-10-24_fusion_holding_v3.md'
) | ForEach-Object { Join-Path $contextRoot $_ }
$changedDocs += 'C:/python/Contact-Rich-Manipulation/src/inspire_sweep_baseline/README.md'
& python "$contextRoot/00_guidelines/scripts/check_markdown_math.py" @changedDocs
& python "$contextRoot/00_guidelines/scripts/check_document_links.py" --root $contextRoot --check-external @changedDocs
git diff --check
git -C $contextRoot diff --check
```

## 미검증과 후속

PPO update·checkpoint 저장/복원·장기 학습·성공 회피 행동 개선·실물 성능은 이번에 검증하지 않았다. 최대16개 장애물의 배치 성공을 보장하지 않으며, 원래의 고정 타겟·목표와 엄격한 비겹침 조건 아래에서 고밀도 배치 가능성은 후속 문제다. Gray 침범률과 개수별 배치 실패·접촉·성공률을 함께 평가한다. 학습·명령 안내에는 `scripts/train.py`를 사용한다.
