# logs/TEMP 학습 결과 정리 — 2026-10-21

[정리 지침](../../00_guidelines/11_TRAINING_LOG_CLEANUP.md) · [로그 색인](README.md)

## 요청과 당시 결과

사용자의 명시적 요청으로 `logs/TEMP`만 정리했다. 당시 기준 루트 커밋은 `e33c134`, Context 커밋은 `e133c09`다. 활성 패키지의 Gym 등록 24개를 AST로 확인하고 저장 YAML 및 패키지 실행 안내의 experiment_name 대응을 대조했다. 코드·환경 설정은 변경하지 않았다.

42개 run 중 35개를 `logs/backup/<환경 ID 또는 Unregistered>/<원래 run 이름>`으로 이동하고, 500 iteration 미만 7개를 삭제했다. 등록 환경 8종에 16개, Unregistered에 19개가 들어갔다. 삭제 파일 크기 합계는 48,840,457바이트다. 정리 완료 당시 `logs/TEMP`는 빈 폴더였다.

`inspire_sweep_omni`와 `inspire_sweep_omni_v0`는 Omni v0로, `inspire_sweep_omni_renewal`과 사용자 지정 이름 `inspire_sweep_omni_renewal_shelf`는 Renewal v0로 분류했다. 저장 YAML의 MDP 함수·보상 구성과 README의 실행 이름을 대조한 식별이며 과거 학습 설정이 현재와 완전히 같다는 의미는 아니다. 이전 Sweep-Policy와 hand_manipulation 실행은 활성 패키지에 등록되지 않아 Unregistered로 분류했다.

## 당시 실행 명령과 검증

- `/home/irol/miniconda3/envs/env_isaaclab/bin/python /tmp/crm_temp_cleanup.py`: 42개 run, Gym ID, checkpoint 번호 확인. 삭제 후보 7개는 TensorBoard RawEventFileLoader로 Loss 태그의 최대 iteration도 확인했다.
- `python /tmp/crm_temp_apply.py`: 사전 목록 검증 후 `Path.rename`으로 35개 run을 이동하고 `shutil.rmtree`로 확정한 7개만 삭제했다. 빈 experiment 폴더만 제거했다.
- 이동 전후 파일·디렉터리의 inode, 크기, mtime_ns, mode, 심볼릭 링크 대상을 대조하여 모두 일치했다. 동명 목적지 충돌은 없었다.
- `logs/rsl_rl`의 210개 항목은 전후 metadata 대조에서 동일했다. 해당 경로에 쓰기·이동·삭제 작업은 하지 않았다.
- 계획·실행 스크립트, manifest.json, rsl_rl_before.json은 로컬 `.git/temp-cleanup-2026-10-21/`에 보관했다. 스크립트는 감사 자료이며 자동 실행 대상으로 등록하지 않았다.

내용 전체의 해시 검사, 체크포인트 로딩·재학습·재생, CPU pytest 및 Isaac Sim 실행은 수행하지 않았다. 당시 검증은 디렉터리 정리와 보존 여부에 한정한다.

## 문서 복원

같은 날 사용자 요청으로 삭제된 지침과 이 기록을 대화 이력 및 남아 있는 `.git/temp-cleanup-2026-10-21/manifest.json`에서 복원했다. 이번 작업은 문서 재생성만 수행하며 위 정리 명령을 다시 실행하지 않았다. 학습 데이터와 `logs/rsl_rl`은 수정하지 않았다.

복원 문서에는 Markdown 수식 검사기와 상대 링크 대상 존재 검사를 실행한다. Workspace 안내에는 `git diff --check`를 적용한다. 로그 색인에는 작업 시작 전부터 Git 충돌 표식이 있었으며, 그 부분과 Git index는 변경하지 않고 복원 기록 링크만 끝에 추가한다. 시뮬레이션·학습 테스트는 문서 복원 범위 밖이다.

## 실행별 대응과 삭제 근거

TensorBoard 열의 `미조회`는 checkpoint 자체가 이미 500 이상이어서 삭제 검토가 필요 없었던 경우다. iteration은 0부터 시작하는 기록 인덱스다.

| 원래 경로 (logs/TEMP 기준) | 처리·목적지 (logs/backup 기준) | 최대 checkpoint | 최대 TensorBoard iteration |
| --- | --- | ---: | ---: |
| `UR5e_shelf_sweep_inspire_right_v1/2026-10-08_19-37-04_center_reach_no_sensors` | `Unregistered/2026-10-08_19-37-04_center_reach_no_sensors` | 550 | 미조회 |
| `UR5e_shelf_sweep_inspire_right_v1/2026-10-08_20-30-33_center_reach_separate_reset` | `삭제` | 200 | 221 |
| `UR5e_shelf_sweep_inspire_right_v1/2026-10-08_20-51-46_center_reach_separate_reset` | `삭제` | 0 | 26 |
| `UR5e_shelf_sweep_inspire_right_v1/2026-10-08_20-54-43_center_reach_separate_reset` | `Unregistered/2026-10-08_20-54-43_center_reach_separate_reset` | 13200 | 미조회 |
| `UR5e_shelf_sweep_inspire_right_v2/2026-10-08_13-43-42_fixed_height_penalty` | `Unregistered/2026-10-08_13-43-42_fixed_height_penalty` | 1000 | 미조회 |
| `UR5e_shelf_sweep_inspire_right_v2/2026-10-08_15-30-43_aligned_reach_fixed_height` | `Unregistered/2026-10-08_15-30-43_aligned_reach_fixed_height` | 650 | 미조회 |
| `UR5e_shelf_sweep_inspire_right_v2/2026-10-08_16-28-21_wrist_gate_up_alignment` | `Unregistered/2026-10-08_16-28-21_wrist_gate_up_alignment` | 1900 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-11_23-06-58` | `Unregistered/2026-08-11_23-06-58` | 29400 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-12_21-24-07` | `Unregistered/2026-08-12_21-24-07` | 16100 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-13_21-41-17` | `Unregistered/2026-08-13_21-41-17` | 89999 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-16_23-43-46` | `Unregistered/2026-08-16_23-43-46` | 89999 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-20_17-17-51` | `Unregistered/2026-08-20_17-17-51` | 89999 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-25_01-19-13` | `Unregistered/2026-08-25_01-19-13` | 25600 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-28_15-12-41` | `Unregistered/2026-08-28_15-12-41` | 89999 | 미조회 |
| `UR5e_shelf_sweep_random_single_inspire_hand_v1_mass/2026-10-10_14-32-43_inspire_hand_mass_cylinder` | `Unregistered/2026-10-10_14-32-43_inspire_hand_mass_cylinder` | 11750 | 미조회 |
| `UR5e_shelf_sweep_random_single_inspire_hand_v2_mass/2026-10-10_19-19-24_inspire_mass_palm_ft` | `Unregistered/2026-10-10_19-19-24_inspire_mass_palm_ft` | 6750 | 미조회 |
| `UR5e_shelf_sweep_random_single_inspire_hand_v2_mass/2026-10-10_21-55-16_inspire_mass_z4cm_correct_alignment` | `Unregistered/2026-10-10_21-55-16_inspire_mass_z4cm_correct_alignment` | 89999 | 미조회 |
| `UR5e_shelf_sweep_random_single_inspire_initial_v3_mass/2026-10-12_15-18-40_inspire_mass_initial_object` | `Unregistered/2026-10-12_15-18-40_inspire_mass_initial_object` | 60300 | 미조회 |
| `UR5e_shelf_sweep_random_single_inspire_open/2026-10-09_17-07-34_inspire_open_joint_position` | `Unregistered/2026-10-09_17-07-34_inspire_open_joint_position` | 2350 | 미조회 |
| `UR5e_shelf_sweep_random_single_inspire_open/2026-10-09_18-09-20_inspire_open_joint_position` | `Unregistered/2026-10-09_18-09-20_inspire_open_joint_position` | 42100 | 미조회 |
| `hand_manipulation_push_v1/2026-10-06_13-18-48` | `Unregistered/2026-10-06_13-18-48` | 21450 | 미조회 |
| `inspire_contact_sweep/2026-10-20_14-05-34` | `Isaac-Inspire-Contact-Sweep-v0/2026-10-20_14-05-34` | 10800 | 미조회 |
| `inspire_dex_omni/2026-10-15_15-14-04_dex_best_distance` | `Isaac-Inspire-Dex-Omni-v0/2026-10-15_15-14-04_dex_best_distance` | 2450 | 미조회 |
| `inspire_dex_omni/2026-10-15_16-53-45_dex_best_distance` | `Isaac-Inspire-Dex-Omni-v0/2026-10-15_16-53-45_dex_best_distance` | 6950 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v1/2026-10-16_20-35-21` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-16_20-35-21` | 48400 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v1/2026-10-18_23-47-33` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-18_23-47-33` | 12300 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v1/2026-10-19_12-15-47` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-19_12-15-47` | 41000 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v2_osc/2026-10-18_20-27-56` | `삭제` | 300 | 340 |
| `inspire_dex_tactile_sweep_omni_renewal_v2_osc/2026-10-18_20-42-44` | `삭제` | 300 | 340 |
| `inspire_dex_tactile_sweep_omni_renewal_v2_osc/2026-10-18_22-51-09` | `삭제` | 300 | 340 |
| `inspire_dex_tactile_sweep_omni_renewal_v2_osc/2026-10-18_23-23-59` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2/2026-10-18_23-23-59` | 650 | 미조회 |
| `inspire_sweep_baseline/2026-10-13_17-00-33_baseline_mass_z9cm_1rad` | `Isaac-Inspire-Sweep-Baseline-v0/2026-10-13_17-00-33_baseline_mass_z9cm_1rad` | 46550 | 미조회 |
| `inspire_sweep_omni/2026-10-14_16-16-28_centered_spawn_goal15cm` | `Isaac-Inspire-Sweep-Omni-v0/2026-10-14_16-16-28_centered_spawn_goal15cm` | 4500 | 미조회 |
| `inspire_sweep_omni_renewal/2026-10-15_21-12-24_renewal_v0` | `Isaac-Inspire-Sweep-Omni-Renewal-v0/2026-10-15_21-12-24_renewal_v0` | 550 | 미조회 |
| `inspire_sweep_omni_renewal/2026-10-15_21-34-49_renewal_v0` | `Isaac-Inspire-Sweep-Omni-Renewal-v0/2026-10-15_21-34-49_renewal_v0` | 950 | 미조회 |
| `inspire_sweep_omni_renewal/2026-10-15_22-04-03_renewal_v0` | `Isaac-Inspire-Sweep-Omni-Renewal-v0/2026-10-15_22-04-03_renewal_v0` | 26450 | 미조회 |
| `inspire_sweep_omni_renewal/2026-10-16_15-26-13` | `삭제` | 150 | 194 |
| `inspire_sweep_omni_renewal/2026-10-16_15-42-56` | `Isaac-Inspire-Sweep-Omni-Renewal-v0/2026-10-16_15-42-56` | 3650 | 미조회 |
| `inspire_sweep_omni_renewal_shelf/2026-10-16_12-41-02_renewal_v0` | `Isaac-Inspire-Sweep-Omni-Renewal-v0/2026-10-16_12-41-02_renewal_v0` | 4850 | 미조회 |
| `inspire_sweep_omni_v0/2026-10-14_22-34-42_centered_spawn_goal15cm_arm2rad` | `Isaac-Inspire-Sweep-Omni-v0/2026-10-14_22-34-42_centered_spawn_goal15cm_arm2rad` | 3550 | 미조회 |
| `inspire_sweep_omni_v1/2026-10-14_22-31-30_centered_spawn_goal15cm_arm2rad` | `삭제` | 100 | 136 |
| `inspire_sweep_omni_v1/2026-10-15_11-37-21_centered_spawn_goal15cm_arm2rad` | `Isaac-Inspire-Sweep-Omni-v1/2026-10-15_11-37-21_centered_spawn_goal15cm_arm2rad` | 5900 | 미조회 |


## 같은 날 추가 요청에 따른 두 번째 정리

사용자가 다시 채운 `logs/TEMP`에 대해 명시적으로 정리를 요청하여 수행했다. 이전 42개 run 정리와 별개이며, 이번 기준 commit은 workspace `0e314e9`, Context `a953e0a`다. 시작 시 Context 내부 작업트리는 깨끗했고, 상위 submodule 참조 차이와 미추적 UR Description 폴더는 보존했다.

40개 run 중 37개를 이동하고 3개를 삭제했다. 등록 환경 11종에 21개, `Unregistered`에 16개를 보존했다. 삭제한 일반 파일 크기 합계는 4,239,366바이트다. 목적지 충돌은 없었고, 원래 run 이름과 전체 내부 파일을 유지했다. `TEMP`는 빈 폴더로 남겼다.

현재 등록 코드의 Gym ID 24개를 AST로 확인하고 `agent.yaml`의 experiment_name, `env.yaml`의 관측·보상 함수와 패키지 실행 안내를 대조했다. `inspire_dex_sweep_omni_renewal_shelf`는 Dex progress 보상과 Renewal 관측 구성을 사용하는 사용자 지정 실험 이름이므로 Dex Renewal v0로 분류했다. 과거 설정 수치가 현행 코드와 완전히 같다는 의미는 아니다. UR5e 과거 run의 함수는 `sweeping_policy`/`single_object_sweep`에 속해 Unregistered로 분류했다.

### 실행과 검증

workspace 루트에서 다음 명령을 실행했다. 스크립트와 전후 manifest는 로컬 Git 관리 영역의 감사 자료이며 자동 실행으로 등록하지 않았다.

```bash
/home/ssu/miniconda3/envs/jd_isaaclab/bin/python .git/temp-cleanup-2026-10-21-second/plan.py
/home/ssu/miniconda3/envs/jd_isaaclab/bin/python .git/temp-cleanup-2026-10-21-second/apply.py
```

- 삭제 후보는 TensorBoard RawEventFileLoader의 `Loss/*` 최대 step으로 확인했다. 각각 19, 0, 0으로, 0 기반 인덱스를 고려해도 500회 미만이다.
- `/proc`의 접근 가능한 cwd·fd를 검사해 TEMP 사용 프로세스가 없음을 확인하고, 적용 직전 모든 run의 사전 metadata가 동일함을 재검사했다. 미분류 일반 파일과 심볼릭 링크는 없었다.
- `Path.rename`으로 이동하고 확정한 3개에만 `shutil.rmtree`를 적용했다. 이동 전후 상대 경로·inode·크기·mtime_ns·mode가 모두 일치했다. 원래 경로 소멸, 목적지 존재, TEMP 잔여 0개를 확인했다.
- `logs/rsl_rl`에는 쓰기·이동·삭제를 수행하지 않았다. 전후 비교에서 실행 중인 Clutter v0 학습 PID 3898329가 파일명에 포함된 TensorBoard 이벤트 파일 하나의 크기·mtime만 증가했다. 해당 학습의 쓰기로 판단하며 다른 항목은 동일했다. 프로세스는 중단하지 않았다.
- 기본 Python 및 `env_isaaclab`에는 필요한 yaml/tensorboard 의존성이 없어 최초 조회가 실패했다. 두 모듈이 있는 `jd_isaaclab` Python으로 계획과 실행을 완료했다.

내용 전체 해시, checkpoint 역직렬화·재생·학습 성능, Isaac Sim 및 CPU pytest는 수행하지 않았다. 이번 검증 범위는 파일 이동 보존·삭제 기준·대상 경로에 한정한다.

### 두 번째 정리 경로 대응

입력은 `logs/TEMP/`, 목적지는 `logs/backup/` 기준이다. Loss step의 `미조회`는 checkpoint만으로 보존 기준을 충족했다는 뜻이다.

| 원래 경로 | 목적지 또는 처리 | 최대 checkpoint | 최대 Loss step |
| --- | --- | --- | --- |
| `2026-10-13_17-00-33_baseline_mass_z9cm_1rad` | `Isaac-Inspire-Sweep-Baseline-v0/2026-10-13_17-00-33_baseline_mass_z9cm_1rad` | 39200 | 미조회 |
| `2026-10-13_17-39-41_realistic_mass_friction` | `Isaac-Inspire-Sweep-Realistic-Physics-v0/2026-10-13_17-39-41_realistic_mass_friction` | 35250 | 미조회 |
| `2026-10-13_17-40-08_realistic_initial_privileged` | `Isaac-Inspire-Sweep-Realistic-Physics-Initial-Privileged-v0/2026-10-13_17-40-08_realistic_initial_privileged` | 26850 | 미조회 |
| `2026-10-15_11-37-21_centered_spawn_goal15cm_arm2rad` | `Isaac-Inspire-Sweep-Omni-v1/2026-10-15_11-37-21_centered_spawn_goal15cm_arm2rad` | 4600 | 미조회 |
| `2026-10-15_15-14-04_dex_best_distance` | `Isaac-Inspire-Dex-Omni-v0/2026-10-15_15-14-04_dex_best_distance` | 2350 | 미조회 |
| `2026-10-19_12-15-47` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-19_12-15-47` | 39000 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-11_21-01-27` | `Unregistered/2026-08-11_21-01-27` | 43400 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-12_20-20-09` | `Unregistered/2026-08-12_20-20-09` | 89999 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-14_22-50-21` | `Unregistered/2026-08-14_22-50-21` | 4450 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-17_14-30-47` | `Unregistered/2026-08-17_14-30-47` | 89999 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-21_18-18-18` | `Unregistered/2026-08-21_18-18-18` | 89999 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-25_00-58-46` | `Unregistered/2026-08-25_00-58-46` | 13300 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-25_22-44-28` | `Unregistered/2026-08-25_22-44-28` | 46500 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-26_23-25-47` | `Unregistered/2026-08-26_23-25-47` | 16000 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-27_11-14-32` | `Unregistered/2026-08-27_11-14-32` | 66850 | 미조회 |
| `UR5e_shelf_sweep_random/2026-08-28_22-56-51` | `Unregistered/2026-08-28_22-56-51` | 89999 | 미조회 |
| `UR5e_shelf_sweep_random/2026-09-01_22-37-56` | `삭제` | 0 | 19 |
| `UR5e_shelf_sweep_random/2026-09-01_22-39-00` | `Unregistered/2026-09-01_22-39-00` | 89999 | 미조회 |
| `UR5e_shelf_sweep_random/2026-09-04_21-33-15` | `Unregistered/2026-09-04_21-33-15` | 89999 | 미조회 |
| `UR5e_shelf_sweep_random/2026-09-07_21-58-38` | `Unregistered/2026-09-07_21-58-38` | 84450 | 미조회 |
| `UR5e_single_object_shelf_sweep_diff_ik_abs_v2/2026-08-10_22-32-40` | `Unregistered/2026-08-10_22-32-40` | 45200 | 미조회 |
| `UR5e_single_object_shelf_sweep_diff_ik_abs_v2/2026-08-11_11-21-29` | `Unregistered/2026-08-11_11-21-29` | 5300 | 미조회 |
| `UR5e_single_object_shelf_sweep_random/2026-08-10_22-01-08` | `Unregistered/2026-08-10_22-01-08` | 1550 | 미조회 |
| `inspire_contact_sweep/2026-10-20_13-19-15_smoke_contact_reference` | `삭제` | 0 | 0 |
| `inspire_contact_sweep/2026-10-20_13-30-06` | `Isaac-Inspire-Contact-Sweep-v0/2026-10-20_13-30-06` | 600 | 미조회 |
| `inspire_dex_sweep_omni_renewal/2026-10-15_21-12-26_dex_renewal_v0` | `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-15_21-12-26_dex_renewal_v0` | 1600 | 미조회 |
| `inspire_dex_sweep_omni_renewal/2026-10-15_22-04-26_dex_renewal_v0` | `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-15_22-04-26_dex_renewal_v0` | 33750 | 미조회 |
| `inspire_dex_sweep_omni_renewal/2026-10-16_15-26-16` | `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_15-26-16` | 5950 | 미조회 |
| `inspire_dex_sweep_omni_renewal/2026-10-16_19-13-47` | `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_19-13-47` | 95199 | 미조회 |
| `inspire_dex_sweep_omni_renewal_shelf/2026-10-16_12-41-16_dex_renewal_v0` | `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_12-41-16_dex_renewal_v0` | 6050 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v2/2026-10-18_20-07-29` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2/2026-10-18_20-07-29` | 1150 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v2/2026-10-18_20-42-27` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2/2026-10-18_20-42-27` | 6400 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v2/2026-10-18_23-47-52` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2/2026-10-18_23-47-52` | 12100 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v2/2026-10-19_12-16-03` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2/2026-10-19_12-16-03` | 9950 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v2/2026-10-19_17-52-20_resume_8500` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2/2026-10-19_17-52-20_resume_8500` | 11450 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v2/2026-10-19_20-37-46_resume_10300` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v2/2026-10-19_20-37-46_resume_10300` | 11750 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v3/2026-10-20_13-12-56_smoke_v3` | `삭제` | 0 | 0 |
| `inspire_sweep_omni_v2/2026-10-15_13-50-41_live_reach200_sweep400` | `Isaac-Inspire-Sweep-Omni-v2/2026-10-15_13-50-41_live_reach200_sweep400` | 2100 | 미조회 |
| `inspire_sweep_omni_v3/2026-10-15_15-32-26_height_gated_xy_reach` | `Isaac-Inspire-Sweep-Omni-v3/2026-10-15_15-32-26_height_gated_xy_reach` | 1550 | 미조회 |
| `inspire_sweep_omni_v3/2026-10-15_16-53-58_height_gated_xy_reach` | `Isaac-Inspire-Sweep-Omni-v3/2026-10-15_16-53-58_height_gated_xy_reach` | 7850 | 미조회 |

### 문서 검사 결과

이번 이동으로 달라진 10월 14일 진단 로그의 Baseline·Realistic Physics run 링크 두 개를 백업 위치로 갱신했다. `python 00_guidelines/scripts/check_markdown_math.py`에 수정 Markdown 두 파일을 전달했고 `git diff --check`를 실행했다. 내부 링크 검사도 실행했다. `check_document_links.py --check-external`은 이번 이동 링크 수정 후에도 작업 전부터 없던 Omni v0 run 폴더와 루트 DexTouch PDF 참조 두 개 때문에 실패한다. 두 자료는 이번 TEMP 입력에 없었으며 임의 대체하지 않았다.
