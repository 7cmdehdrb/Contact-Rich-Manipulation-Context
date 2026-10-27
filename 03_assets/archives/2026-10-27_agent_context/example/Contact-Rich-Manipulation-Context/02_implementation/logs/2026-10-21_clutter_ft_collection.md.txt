# Curriculum v1 정책의 원본·v2 보정 F/T 동시 수집

> 2026-10-21 로그 정리 후 참조 run의 현재 위치는 `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Curriculum-v1/2026-10-20_22-49-30`다. 아래 당시 경로·실행 명령은 수행 이력으로 보존한다. [정리 기록](2026-10-21_temp_training_log_cleanup.md).

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md#clutter-ft-테스트--2026-10-21) · [실행·CSV 계약](../../../../src/inspire_sweep_baseline/README.md#clutter-ft-테스트--curriculum-v1-정책과-v2-하중-보정)

기준일: 2026-10-21. 테스트 환경 구축과 실제 GPU 재생·CSV 수집 완료. 새 F/T 보상 계수 선택·학습은 수행하지 않았다.

## 요청과 기준 상태

사용자는 Curriculum v1과 v2의 융합을 위해, 지정 Curriculum 정책을 기존 관측으로 실행하면서 v1 미보정 F/T와 v2 보정 F/T를 동시에 취득하고 보상 설계용 CSV를 만들도록 요청했다.

Workspace HEAD는 `0e314e9`, 문서 저장소 HEAD는 `a953e0a`다. 시작 시 문서 submodule에 이전 보상 분석·학습 로그 정리 관련 변경과 로그 색인의 기존 충돌 표식이 있었으며 모두 보존했다. `src/Universal_Robots_ROS2_Description/`의 기존 untracked 파일도 변경하지 않았다. commit·push·학습 로그 정리는 수행하지 않았다.

입력 run은 `logs/inspire_contact_sweep_clutter_v1_curriculum/2026-10-20_22-49-30`이며, 최신 숫자 checkpoint인 `model_12800.pt`를 선택했다. SHA-256은 `fffb3fa70a94ccd998034b04427641822cf6a8194e625f63f92fc6742e87cf3d`다. 수집 뒤 원본 checkpoint 해시가 같은 것도 확인했다.

## 환경 계약과 구현

| 항목 | 적용 |
| --- | --- |
| Gym ID | `Isaac-Inspire-Contact-Sweep-Clutter-FT-Test-v0` |
| Runtime | `contact_sweep_clutter_ft_test.env:ContactSweepClutterFTTestEnv` → Curriculum v1 runtime |
| Cfg | `ContactSweepClutterFTTestEnvCfg` → Curriculum v1 Cfg |
| Runner | 기존 `ContactSweepClutterV1CurriculumPPORunnerCfg`와 `CurriculumOnPolicyRunner` |
| Actor/Critic | policy 57D + obstacles 40D / policy 57D + privileged 3D + obstacles 40D |
| 기존 F/T | 학습과 동일한 v1 미보정 F/T, 정책 입력 유지 |
| 추가 취득 | v2의 실제 `PureWrenchReader`를 재사용하여 raw/support/pure, EEF·월드 축 동시 기록 |
| 보상 | 기존 15항·curriculum 그대로, `wrench_change` 신규 비용 없음 |
| Action·물리 | 기존 Arm 6D + Hand 2D, physics 0.01초·control 0.02초·episode 최대 10초 |
| 샘플 | 매 제어 step 마지막 physics substep, terminal도 부모 reset 전에 취득 |

환경 클래스는 최소 lifecycle 연결만 맡고 `WrenchTelemetry`가 데이터 구성·episode별 차분 이력을, `WrenchCSVWriter`가 스트리밍 저장을 맡는다. 종료 환경은 `_reset_idx`에서 부모를 호출하기 전에 읽고, 나머지는 부모 `step` 직후 읽는다. 모든 환경이 정확히 한 번 수집되지 않으면 실패한다. 별도 noisy observation 계산이나 reward term 재평가는 하지 않는다.

v1 raw는 기존 `wrist_wrench_eef`의 실제 변환을 그대로 쓴다. 이 함수는 Axia 하우징 frame을 사용하며, v2는 measurement joint의 child frame을 사용한다. 따라서 두 raw 경로를 동일하다고 가정하거나 v1 raw에서 v2 support를 직접 차감하지 않는다. v2 pure는 v2 raw에서 Hand 자체 중력·관성 하중을 차감한 반력이다. 두 축 표현 모두 모멘트 원점은 EEF다. world는 축 표현만을 가리키며 N/N·m 단위, parent-on-child 부호를 유지한다.

CSV 125열에는 v1 원본, v2 원본·자체 하중·보정값, 월드 축 step 변화량, EEF 위치·wxyz quaternion, tactile 17개·접촉 수, 목표 XY 오차, 종료 사유, 실제 가중 step 보상 15개·양의 합·순합, 적용 curriculum 값이 있다. `delta_valid=0`의 변화량은 0으로 저장하며 첫 표본·reset 이후 첫 표본이므로 이후 변화량 보상 설계에서 제외한다. GT 목표 오차는 데이터 해석 context이며 정책 관측에 추가하지 않았다.

원본 학습의 `params/env.yaml`과 실제 실행의 `env.yaml`에서 observations/rewards/actions/terminations/events/commands/curriculum/sim 8개 구성을 비교해 모두 일치했다. 환경 수·출력 위치는 수집용으로 지정했다. checkpoint iteration 12800이 전체 기록에서 유지됐으며 Arm 두 일정 가중치는 −0.05, 물체 free speed 0.06 m/s, Arm free speed 0.9 rad/s다. 기존 로컬 제곱합 함수와 Arm/Hand 분리는 바꾸지 않았다.

## 실제 실행

현재 호스트의 `/home/ssu/miniconda3/envs/jd_isaaclab/bin/python`을 사용했다. Torch 2.7.0+cu128, RSL-RL 5.0.1, Isaac Sim 5.1.0.0, RTX PRO 6000 GPU다. 샌드박스에서는 `/dev/nvidia*`가 숨겨져 첫 사전 검사가 실패했으나, 승인된 샌드박스 밖 실행에서 GPU를 확인해 수집을 완료했다. CUDA 불가 초기 실패의 metadata와 stdout도 `outputs/clutter_ft`에 보존했다. 패키지 설치·드라이버 변경은 하지 않았다.

Workspace 루트에서 실행한 본 수집 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONDONTWRITEBYTECODE=1 /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B src/inspire_sweep_baseline/scripts/collect_clutter_ft.py --headless --num_envs 16 --steps 5000 --output-dir outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset

python -B src/inspire_sweep_baseline/scripts/validate_clutter_ft.py outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset
```

수집기 기본 `--checkpoint`는 지정 run이다. `--checkpoint`에 파일을 주면 해당 모델을, 디렉터리를 주면 숫자 iteration이 가장 큰 모델을 선택한다. 기본 seed는 42다. 기존 출력 폴더를 덮어쓰지 않으며 학습 로그 안의 출력 경로도 허용하지 않는다. 정책 export·새 학습은 수행하지 않는다. 기본 출력은 새 UTC timestamp 폴더다.

## 산출물과 검증

- [본 CSV](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset/wrench.csv): **80000행 ×125열**, 약 139.1 MiB. 16환경 ×5000 제어 step = 환경당 누적 시뮬레이션 100초, 전체 1600초. 여러 episode를 포함한다.
- [수집 metadata](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset/metadata.json): checkpoint·단위·좌표계·seed·실행 상태 `complete`·80000행.
- [전체 CSV 검증](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset/validation.json): **passed**, 유한값·행 정렬·누락/중복 없음·전 행 sensor fresh·751 terminal transitions 보존·reset 차분 이력 분리·보상 합계·raw/support/pure 관계 검증.
- [원본 설정 대조](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset/source_config_match.json): 8개 구성 모두 일치.
- [CSV·코드·checkpoint 해시](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset/manifest.json).
- [본 수집 stdout](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_attempt.log).
- [짧은 선행 GPU CSV](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_smoke/wrench.csv): 4환경 ×20 step =80행. [검증](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_smoke/validation.json) 통과. 이 짧은 실행에는 종료 전이가 없어 terminal 보존은 본 수집과 CPU lifecycle 검사로 확인했다.

본 수집에는 tactile ON 표본 978행, 목표 XY 1 cm 내 표본 4410행이 있다. 이는 step 수이며 episode 성공 횟수나 성공률이 아니다. 보정 힘 norm 최대 301.139 N, 모멘트 norm 최대 21.0989 N·m, step 변화량 최대 301.141 N/21.0990 N·m를 보존했다. clamp·평활화·이상치 제거를 하지 않았다. 보상 계수는 단일 최대값보다 접촉·종료·목표 상태에 따른 분포와 구간을 확인한 후 별도 선택해야 한다. 이번 작업에서 그 선택은 하지 않았다.

raw = support + pure의 최대 수치 오차는 0.0000267029다. 이는 CSV 내부 수학 일관성 검증이며 보정 추정의 물리적 정확도나 실물 성능 검증과 구분한다.

CPU 검증 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests
```

[최종 CPU stdout](../../../../outputs/clutter_ft/pytest.log): **377 passed**, 기존 ONNX deprecation 경고 2개. 추가 7개 검사는 종료 직전 표본·부분 reset·차분 경계·유한값/누락/중복 거부·CSV 가중치 및 덮어쓰기 방지·환경 lifecycle·등록/상속·지정 실제 checkpoint의 strict CPU load와 유한 추론·숫자 checkpoint 선택을 확인한다. 기존 v2 보정 수학·관측, Curriculum runner 경계 포함 집중 검사 38개도 먼저 통과했다. 전체 검사의 최초 실행은 runtime-family 고정 목록에 새 테스트 task와 기존 Curriculum task가 빠져 1개 실패했으며 목록을 보완한 뒤 위 전체 검사를 통과했다. newton Python에는 pytest가 없어 테스트는 jd_isaaclab Python으로 실행했다.

기존 정책으로 재생한 한 seed의 데이터다. 보정 F/T를 정책에 입력한 새 정책 학습, 새 보상 계수의 성능·예산 비중, 여러 seed/checkpoint 비교, 실물 센서 보정은 이 작업의 검증 범위에 포함하지 않는다.

문서 저장소에서 다음 명령을 실행해 Markdown 6파일 수식 검사 통과, 내부 링크 208개·workspace 외부 파일 링크 67개·오류 0을 확인했다. 두 저장소의 변경 대상 `git diff --check`도 통과했다. 기존 색인의 충돌 표식은 이번 범위에서 해결하지 않았다.

```bash
python 00_guidelines/scripts/check_markdown_math.py 01_plan/00_HANDOFF_BRIEF.md 01_plan/04_NEXT_ACTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-21_clutter_ft_collection.md ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external 01_plan/00_HANDOFF_BRIEF.md 01_plan/04_NEXT_ACTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-21_clutter_ft_collection.md ../../src/inspire_sweep_baseline/README.md
```

## 후속 요청 — 보정 F/T의 축별 시간 변화율

사용자 요청에 따라 기존 CSV를 후처리해 별도 파일로 저장했다. 기존 환경·수집 코드·보상·원본 CSV는 변경하지 않았다. 기준 commit과 이전 작업트리 변경은 위와 같으며, 기존 `PLAN.md` 등 사용자 파일은 보존했다. 데이터 분석 스킬의 원본·단위·grain·재현성 기준을 적용했으며, 요청 산출물은 CSV이므로 보고서·노트북·차트는 별도로 만들지 않았다.

[가공 코드](../../../../src/inspire_sweep_baseline/scripts/process_clutter_ft_rates.py)는 동일 환경·episode의 인접 유효 제어 표본에 대해 `rate = (current − previous) / 0.02`를 계산한다. 시간 간격은 반올림된 float32 `sim_time_s`의 차이가 아니라 metadata의 0.02초와 연속 제어 counter를 사용하며, physics counter의 간격도 일치하는지 검사한다. 초기·reset 직후 `delta_valid=0`인 767행은 제외하고 종료 직전 유효 차분은 유지했다. 원본 80000행에서 각 축 **79233개** 변화율을 얻었다.

원본은 v2 보정값 `v2_pure_world_*`, `v2_pure_eef_*`다. `world`는 월드 축 성분의 차분이며, `eef`는 회전하는 EEF 축 성분의 차분이므로 축 회전에 의한 변화도 포함한다. 모멘트 기준점은 두 경우 모두 이동하는 EEF다. 힘 변화율 단위는 N/s, 모멘트는 N·m/s이며 시간 미분의 후진 유한차분 근사다. 정규화·평활화·clamp·이상치 제거는 하지 않았다.

출력은 `outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates`다. 각 좌표계에 Fx/Fy/Fz/Mx/My/Mz를 나눈 6개 CSV, 합계 12개를 생성했다.

| 축 | 월드 축 CSV | EEF 축 CSV |
| --- | --- | --- |
| Fx | [world/fx_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/world/fx_rate.csv) | [eef/fx_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/eef/fx_rate.csv) |
| Fy | [world/fy_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/world/fy_rate.csv) | [eef/fy_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/eef/fy_rate.csv) |
| Fz | [world/fz_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/world/fz_rate.csv) | [eef/fz_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/eef/fz_rate.csv) |
| Mx | [world/mx_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/world/mx_rate.csv) | [eef/mx_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/eef/mx_rate.csv) |
| My | [world/my_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/world/my_rate.csv) | [eef/my_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/eef/my_rate.csv) |
| Mz | [world/mz_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/world/mz_rate.csv) | [eef/mz_rate.csv](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/eef/mz_rate.csv) |

각 CSV에는 `rate_N_per_s` 또는 `rate_Nm_per_s`와 그 절댓값, 현재·이전 보정값·차이·시간 간격, 원본 data row 번호, 환경·episode·step·시각·종료·촉각 수·목표 오차를 저장했다. 부호를 보존했으며 절댓값과 구분했다. 원본 data row 번호는 header 다음 첫 데이터 행을 1로 센다. [가공 metadata](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/metadata.json)에 원본 SHA-256·계산법·단위·제외 수를 기록했다.

Workspace 루트에서 실제 실행:

```bash
python -B src/inspire_sweep_baseline/scripts/process_clutter_ft_rates.py outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset --output-dir outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_clutter_ft_rates.py

/home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/verify_rates.py
```

CPU 검사 **3 passed**: 환경이 섞인 행의 환경별 미분, terminal 표본 유지·reset 점프 제외, delta flag가 reset을 가로지르는 오류 거부, physics 간격 불일치 거부를 확인했다. 전체 377개 테스트는 이전 수집 구현의 검사이며 이번 후처리 추가 뒤 전체 재실행은 하지 않았다.

별도 [NumPy 검증 코드](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/verify_rates.py)로 원본을 `(5000 step, 16 env, 12 성분)`으로 재배열하고 episode ID로 독립 마스크를 구성해 미분을 다시 계산했다. [검증 결과](../../../../outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates/validation.json): 12파일 모두 79233행, reset 마스크·원본 행 대응·유한값·절댓값·시간 변화율 일치. 전체 변화율의 NumPy 대조 최대 오차 0이며 원본 SHA-256 불변을 확인했다. 새 시뮬레이션 실행이나 보상 계수 선택은 하지 않았다.
