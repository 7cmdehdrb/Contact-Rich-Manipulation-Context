# logs/TEMP 학습 로그 정리 — 2026-10-22

[정리 지침](../../00_guidelines/11_TRAINING_LOG_CLEANUP.md) · [로그 색인](README.md)

## 요청과 결과

사용자의 명시적 요청에 따라 `logs/TEMP`의 17개 run을 정리했다. 루트 기준 커밋은 `a2fcb0b`, 문서 저장소 기준 커밋은 `f5655d0`다. 현재 소스의 Gym 등록 호출을 AST로 확인한 ID는 28개이며, 저장된 `params/agent.yaml`의 experiment_name과 `params/env.yaml`의 MDP·관측·보상 구성을 현재 등록·PPO 설정과 대조했다.

9개 run을 `logs/backup`으로 디렉터리 이동하고, 500회 미만인 8개 run을 삭제했다. 삭제된 일반 파일 크기 합계는 50,479,031바이트다. 등록 환경 6종에 8개 run, `Unregistered`에 1개 run을 보존했다. `logs/TEMP`는 비어 있으며 목적지 충돌은 없었다.

과거 Fusion v1은 현재 등록 ID가 없어 `Unregistered`에 보존했다. 이후 v3으로 재작명한 이력은 있으나 과거 run을 현재 v3 학습으로 재분류하지 않았다. TEMP 바로 아래의 두 날짜 폴더는 저장 experiment_name과 YAML에서 각각 Clutter v0 및 Fusion v0로 식별했다. 과거 설정과 현행 설정이 완전히 동일하다는 의미는 아니다.

## 실행과 검증

- `python /tmp/temp_cleanup_20261022.py`: 사전 목록·현재 등록 ID·checkpoint 및 삭제 후보의 TensorBoard `Loss/*` 최대 step을 확인하고 이동·삭제 계획을 저장했다. 후보 event 파일의 읽은 record 길이 합계와 파일 크기도 일치했다. 0 기반 step 499 이상은 보존하는 경계를 적용했다.
- `/proc`에서 확인 가능한 학습 프로세스 인자와 TEMP 파일을 연 프로세스를 검사했으며 발견하지 못했다. TEMP 내부 심볼릭 링크는 없었다. 접근 불가능하거나 다른 PID namespace의 프로세스까지 확인한 것은 아니다.
- `python /tmp/temp_cleanup_20261022.py apply`: 사전 TEMP snapshot 일치를 재확인한 뒤 `Path.rename`으로 9개 run을 이동하고 `shutil.rmtree`로 확정된 8개만 삭제했다. 빈 experiment 디렉터리만 제거했다.
- 이동 전후 모든 하위 항목의 상대 경로·inode·크기·mtime_ns·mode가 일치했다. 원래 run 이름과 내부 파일을 유지했고 입력 잔여 항목은 0개다.
- `logs/rsl_rl`의 루트 포함 165개 항목은 전후 메타데이터가 일치했다. 이 경로에는 쓰기 작업을 하지 않았다.
- 계획·메타데이터 snapshot·결과·실행 스크립트 사본은 workspace의 `outputs/temp-cleanup-2026-10-22/`에 보존했다. 일회성 감사 자료이며 자동 실행은 등록하지 않았다.

파일 내용 전체 해시 검사, checkpoint 로딩, 재학습·재생, CPU pytest와 Isaac Sim 실행은 하지 않았다. 검증 범위는 로그 분류·이동·삭제 및 파일 보존이다.

## 실행별 대응

원래 경로는 `logs/TEMP`, 목적지는 `logs/backup` 기준이다. TensorBoard 미조회는 checkpoint가 이미 기준을 충족해 삭제 후보가 아니었던 경우다. Loss step은 0 기반이므로 완료 횟수는 step + 1이다.

| 원래 경로 | 처리·목적지 | 최대 checkpoint | 최대 Loss step |
| --- | --- | ---: | ---: |
| `2026-10-20_14-04-31` | `Isaac-Inspire-Contact-Sweep-Clutter-v0/2026-10-20_14-04-31` | 9650 | 미조회 |
| `2026-10-21_19-31-34` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v0/2026-10-21_19-31-34` | 1900 | 미조회 |
| `inspire_contact_sweep_clutter_fusion_v1/2026-10-21_19-36-46` | `Unregistered/2026-10-21_19-36-46` | 900 | 미조회 |
| `inspire_contact_sweep_clutter_fusion_v2/2026-10-21_20-59-46` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v2/2026-10-21_20-59-46` | 650 | 미조회 |
| `inspire_contact_sweep_clutter_v1/2026-10-20_20-58-18` | `삭제` | 200 | 242 |
| `inspire_contact_sweep_clutter_v1/2026-10-20_21-23-37` | `삭제` | 200 | 227 |
| `inspire_contact_sweep_clutter_v1/2026-10-20_21-51-10` | `삭제` | 100 | 113 |
| `inspire_contact_sweep_clutter_v1/2026-10-20_22-10-23` | `삭제` | 50 | 88 |
| `inspire_contact_sweep_clutter_v1/2026-10-20_22-18-42` | `삭제` | 300 | 316 |
| `inspire_contact_sweep_clutter_v1_curriculum/2026-10-20_22-49-30` | `Isaac-Inspire-Contact-Sweep-Clutter-Curriculum-v1/2026-10-20_22-49-30` | 14450 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal/2026-10-16_14-15-19_dex_tactile_renewal_v0` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v0/2026-10-16_14-15-19_dex_tactile_renewal_v0` | 1350 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal/2026-10-16_15-28-03` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v0/2026-10-16_15-28-03` | 5800 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal/2026-10-16_21-40-05` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v0/2026-10-16_21-40-05` | 41900 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v2_osc/2026-10-18_23-48-27` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2/2026-10-18_23-48-27` | 6200 | 미조회 |
| `inspire_dex_tactile_sweep_omni_renewal_v2_osc/2026-10-19_11-21-13` | `삭제` | 300 | 349 |
| `inspire_dex_tactile_sweep_omni_renewal_v2_osc_smoke/2026-10-18_20-14-08_validation` | `삭제` | 0 | 0 |
| `inspire_dex_tactile_sweep_omni_renewal_v2_smoke/2026-10-18_20-02-53_validation` | `삭제` | 0 | 0 |
