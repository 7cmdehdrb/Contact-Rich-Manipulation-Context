# 2026-11-04 TEMP 학습 로그 분류

## 요청과 적용 기준

- 사용자 요청: `logs/TEMP`를 로그 정리 기준으로 분류하고 동일 학습은 더 긴 로그를 사용한다.
- [로그 정리 지침](../../00_guidelines/11_TRAINING_LOG_CLEANUP.md)에 따라 500회 이상 보존, 미등록·식별 불확실은 `Unregistered`, 기존 목적지 충돌은 접두사로 보존했다.
- 현재 실제 `__init__.py` 등록 70개를 경량 Gym registry 대역으로 수집했다. 시뮬레이션 환경은 실행하지 않았다. agent의 experiment_name, env.yaml의 함수·보상 구성, 등록 cfg, 기존 분류 및 resilient job.json의 task를 대조했다.
- 코드 HEAD `ba1aa88bf462c5263531379b0a67248ad2439552`, 문서 HEAD `c2deba2f5672450920c5e0377b2e1655752aeab6`. 기존 사용자 변경·커밋은 보존했다.

## 결과와 판단

- 원본 51개 leaf run(설정 있는 실행 50개, 설정 없는 부분 사본 1개). 재시작 12개 attempt는 job.json과 함께 3개 원래 job 디렉터리로 보존했다.
- 이동 39개 디렉터리 / 보존 leaf run 48개. 중복 삭제 3개, 500회 미만 삭제 0개.
- 이동 보존 파일 24,560개, 중복 사본 제거 파일 2,668개 / 3,699,012,402 bytes.
- 등록 환경 19개 디렉터리, Unregistered 20개 디렉터리로 이동했다. 기존 backup의 짧은 5개는 지침상 덮어쓰거나 삭제하지 않고, 더 긴 신규 사본을 B1__/Server__ 접두사로 구분해 사용 대상으로 지정했다.
- 중복 판정은 공통 checkpoint·설정·기타 파일의 바이트 전체 일치와 동일 TensorBoard 파일의 prefix 일치로 확인했다. 동일 환경·seed만으로는 중복 처리하지 않았다.
- 2026-10-19_12-15-47: B1 Loss step 41027(41028회), Server step 39036(39037회). B1 전체를 보존하고 Server 짧은 사본을 삭제했다. Server에만 있는 exported 모델 2개도 해당 짧은 사본의 산출물로 함께 제거했다.
- Realistic Physics 부분 사본은 env/agent 설정·TensorBoard가 없고 기존 보관본과 132개 파일이 같지만 model_6750.pt 및 exported 2개가 달라 중복 삭제하지 않았다. Unregistered에 원형 보존했다.
- Unregistered의 2026-08-14_22-50-21은 event header, 2026-08-25_00-58-46은 마지막 event가 잘려 있다. 각각 checkpoint 4450/13300이 있어 보존했다. 2026-08-13_21-41-17은 TensorBoard가 없지만 checkpoint 89999로 보존했다.

## 원래 경로 → 최종 경로

모든 경로는 workspace 기준이다. `B1__`·`Server__` 접두사가 붙은 5개는 기존 동명 run보다 긴 사용 대상이다. 기존 디렉터리는 그대로 유지했다.

| 처리 | 원래 경로 | 최종 경로 또는 사용할 사본 |
| --- | --- | --- |
| 이동 | `logs/TEMP/B1/logs/backup/Isaac-Inspire-Contact-Sweep-v0/2026-10-20_14-05-34` | `logs/backup/Isaac-Inspire-Contact-Sweep-v0/2026-10-20_14-05-34` |
| 이동 | `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Omni-v0/2026-10-15_15-14-04_dex_best_distance` | `logs/backup/Isaac-Inspire-Dex-Omni-v0/2026-10-15_15-14-04_dex_best_distance` |
| 이동 | `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Omni-v0/2026-10-15_16-53-45_dex_best_distance` | `logs/backup/Isaac-Inspire-Dex-Omni-v0/B1__2026-10-15_16-53-45_dex_best_distance` |
| 이동 | `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2/2026-10-18_23-23-59` | `logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2/2026-10-18_23-23-59` |
| 이동 | `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-16_20-35-21` | `logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-16_20-35-21` |
| 이동 | `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-18_23-47-33` | `logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/B1__2026-10-18_23-47-33` |
| 이동 | `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-19_12-15-47` | `logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-19_12-15-47` |
| 이동 | `logs/TEMP/B1/logs/backup/Isaac-Inspire-Sweep-Baseline-v0/2026-10-13_17-00-33_baseline_mass_z9cm_1rad` | `logs/backup/Isaac-Inspire-Sweep-Baseline-v0/B1__2026-10-13_17-00-33_baseline_mass_z9cm_1rad` |
| 이동 | `logs/TEMP/B1/logs/backup/Isaac-Inspire-Sweep-Omni-v0/2026-10-14_16-16-28_centered_spawn_goal15cm` | `logs/backup/Isaac-Inspire-Sweep-Omni-v0/B1__2026-10-14_16-16-28_centered_spawn_goal15cm` |
| 중복 삭제 | `logs/TEMP/B1/logs/backup/Isaac-Inspire-Sweep-Omni-v0/2026-10-14_22-34-42_centered_spawn_goal15cm_arm2rad` | `logs/backup/Isaac-Inspire-Sweep-Omni-v0/2026-10-14_22-34-42_centered_spawn_goal15cm_arm2rad` |
| 이동 | `logs/TEMP/B1/logs/backup/Isaac-Inspire-Sweep-Omni-v1/2026-10-15_11-37-21_centered_spawn_goal15cm_arm2rad` | `logs/backup/Isaac-Inspire-Sweep-Omni-v1/2026-10-15_11-37-21_centered_spawn_goal15cm_arm2rad` |
| 이동 | `logs/TEMP/B1/logs/backup/Unregistered/2026-08-13_21-41-17` | `logs/backup/Unregistered/2026-08-13_21-41-17` |
| 이동 | `logs/TEMP/B1/logs/backup/Unregistered/2026-08-25_01-19-13` | `logs/backup/Unregistered/2026-08-25_01-19-13` |
| 이동 | `logs/TEMP/B1/logs/backup/Unregistered/2026-10-06_13-18-48` | `logs/backup/Unregistered/2026-10-06_13-18-48` |
| 이동 | `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0/2026-10-22_06-35-02_bc8551cf` | `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0/2026-10-22_06-35-02_bc8551cf` |
| 이동 | `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1/2026-10-22_08-57-45_21191bc6` | `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1/2026-10-22_08-57-45_21191bc6` |
| 이동 | `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65` | `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65` |
| 이동 | `logs/TEMP/Server/logs/backup/Isaac-Inspire-Contact-Sweep-v0/2026-10-20_13-30-06` | `logs/backup/Isaac-Inspire-Contact-Sweep-v0/2026-10-20_13-30-06` |
| 이동 | `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-15_21-12-26_dex_renewal_v0` | `logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-15_21-12-26_dex_renewal_v0` |
| 이동 | `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-15_22-04-26_dex_renewal_v0` | `logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/Server__2026-10-15_22-04-26_dex_renewal_v0` |
| 이동 | `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_12-41-16_dex_renewal_v0` | `logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_12-41-16_dex_renewal_v0` |
| 이동 | `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_15-26-16` | `logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_15-26-16` |
| 중복 삭제 | `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_19-13-47` | `logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_19-13-47` |
| 중복 삭제 | `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-19_12-15-47` | `logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-19_12-15-47` |
| 이동 | `logs/TEMP/Server/logs/backup/Isaac-Inspire-Sweep-Omni-v2/2026-10-15_13-50-41_live_reach200_sweep400` | `logs/backup/Isaac-Inspire-Sweep-Omni-v2/2026-10-15_13-50-41_live_reach200_sweep400` |
| 이동 | `logs/TEMP/Server/logs/backup/Isaac-Inspire-Sweep-Realistic-Physics-v0/2026-10-13_17-39-41_realistic_mass_friction` | `logs/backup/Unregistered/2026-10-13_17-39-41_realistic_mass_friction` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-10_22-01-08` | `logs/backup/Unregistered/2026-08-10_22-01-08` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-10_22-32-40` | `logs/backup/Unregistered/2026-08-10_22-32-40` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-11_11-21-29` | `logs/backup/Unregistered/2026-08-11_11-21-29` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-11_21-01-27` | `logs/backup/Unregistered/2026-08-11_21-01-27` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-12_20-20-09` | `logs/backup/Unregistered/2026-08-12_20-20-09` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-14_22-50-21` | `logs/backup/Unregistered/2026-08-14_22-50-21` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-17_14-30-47` | `logs/backup/Unregistered/2026-08-17_14-30-47` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-21_18-18-18` | `logs/backup/Unregistered/2026-08-21_18-18-18` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-25_00-58-46` | `logs/backup/Unregistered/2026-08-25_00-58-46` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-25_22-44-28` | `logs/backup/Unregistered/2026-08-25_22-44-28` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-26_23-25-47` | `logs/backup/Unregistered/2026-08-26_23-25-47` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-27_11-14-32` | `logs/backup/Unregistered/2026-08-27_11-14-32` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-08-28_22-56-51` | `logs/backup/Unregistered/2026-08-28_22-56-51` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-09-01_22-39-00` | `logs/backup/Unregistered/2026-09-01_22-39-00` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-09-04_21-33-15` | `logs/backup/Unregistered/2026-09-04_21-33-15` |
| 이동 | `logs/TEMP/Server/logs/backup/Unregistered/2026-09-07_21-58-38` | `logs/backup/Unregistered/2026-09-07_21-58-38` |

## 실행별 진행 근거

Loss step은 0-based iteration이다. checkpoint 번호와 Loss step 중 큰 값으로 진행의 하한을 확인했다. 재시작 attempt의 step은 이전 학습을 포함한 누적 iteration이며 독립된 중복 학습으로 취급하지 않는다.

| 원래 실행 | 환경 ID | 최대 checkpoint | 최대 Loss step |
| --- | --- | ---: | ---: |
| `logs/TEMP/B1/logs/backup/Isaac-Inspire-Contact-Sweep-v0/2026-10-20_14-05-34` | `Isaac-Inspire-Contact-Sweep-v0` | 10800 | 10814 |
| `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Omni-v0/2026-10-15_15-14-04_dex_best_distance` | `Isaac-Inspire-Dex-Omni-v0` | 2450 | 2465 |
| `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Omni-v0/2026-10-15_16-53-45_dex_best_distance` | `Isaac-Inspire-Dex-Omni-v0` | 6950 | 6951 |
| `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2/2026-10-18_23-23-59` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2` | 650 | 695 |
| `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-16_20-35-21` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1` | 48400 | 48425 |
| `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-18_23-47-33` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1` | 12300 | 12303 |
| `logs/TEMP/B1/logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-19_12-15-47` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1` | 41000 | 41027 |
| `logs/TEMP/B1/logs/backup/Isaac-Inspire-Sweep-Baseline-v0/2026-10-13_17-00-33_baseline_mass_z9cm_1rad` | `Isaac-Inspire-Sweep-Baseline-v0` | 46550 | 46573 |
| `logs/TEMP/B1/logs/backup/Isaac-Inspire-Sweep-Omni-v0/2026-10-14_16-16-28_centered_spawn_goal15cm` | `Isaac-Inspire-Sweep-Omni-v0` | 4500 | 4539 |
| `logs/TEMP/B1/logs/backup/Isaac-Inspire-Sweep-Omni-v0/2026-10-14_22-34-42_centered_spawn_goal15cm_arm2rad` | `Isaac-Inspire-Sweep-Omni-v0` | 3550 | 3555 |
| `logs/TEMP/B1/logs/backup/Isaac-Inspire-Sweep-Omni-v1/2026-10-15_11-37-21_centered_spawn_goal15cm_arm2rad` | `Isaac-Inspire-Sweep-Omni-v1` | 5900 | 5949 |
| `logs/TEMP/B1/logs/backup/Unregistered/2026-08-13_21-41-17` | `Unregistered` | 89999 | -1 |
| `logs/TEMP/B1/logs/backup/Unregistered/2026-08-25_01-19-13` | `Unregistered` | 25600 | 25645 |
| `logs/TEMP/B1/logs/backup/Unregistered/2026-10-06_13-18-48` | `Unregistered` | 21450 | 21483 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0/2026-10-22_06-35-02_bc8551cf/attempt_000` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0` | 2900 | 2929 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1/2026-10-22_08-57-45_21191bc6/attempt_000` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1` | 1850 | 1878 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65/attempt_000` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3` | 11500 | 11525 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65/attempt_001` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3` | 11350 | 11358 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65/attempt_002` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3` | 11050 | 11093 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65/attempt_003` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3` | 10700 | 10748 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65/attempt_004` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3` | 11600 | 11607 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65/attempt_005` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3` | 11100 | 11125 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65/attempt_006` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3` | 15100 | 15101 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65/attempt_007` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3` | 15100 | 15139 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65/attempt_008` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3` | 14700 | 14714 |
| `logs/TEMP/B1/logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3/2026-10-22_10-17-25_512d0a65/attempt_009` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3` | 16950 | 16953 |
| `logs/TEMP/Server/logs/backup/Isaac-Inspire-Contact-Sweep-v0/2026-10-20_13-30-06` | `Isaac-Inspire-Contact-Sweep-v0` | 600 | 621 |
| `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-15_21-12-26_dex_renewal_v0` | `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0` | 1600 | 1629 |
| `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-15_22-04-26_dex_renewal_v0` | `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0` | 33750 | 33750 |
| `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_12-41-16_dex_renewal_v0` | `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0` | 6050 | 6074 |
| `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_15-26-16` | `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0` | 5950 | 5956 |
| `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0/2026-10-16_19-13-47` | `Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0` | 95199 | 95199 |
| `logs/TEMP/Server/logs/backup/Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1/2026-10-19_12-15-47` | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1` | 39000 | 39036 |
| `logs/TEMP/Server/logs/backup/Isaac-Inspire-Sweep-Omni-v2/2026-10-15_13-50-41_live_reach200_sweep400` | `Isaac-Inspire-Sweep-Omni-v2` | 2100 | 2146 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-10_22-01-08` | `Unregistered` | 1550 | 1560 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-10_22-32-40` | `Unregistered` | 45200 | 45242 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-11_11-21-29` | `Unregistered` | 5300 | 5305 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-11_21-01-27` | `Unregistered` | 43400 | 43413 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-12_20-20-09` | `Unregistered` | 89999 | 89999 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-14_22-50-21` | `Unregistered` | 4450 | 4448 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-17_14-30-47` | `Unregistered` | 89999 | 89999 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-21_18-18-18` | `Unregistered` | 89999 | 89999 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-25_00-58-46` | `Unregistered` | 13300 | 13299 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-25_22-44-28` | `Unregistered` | 46500 | 46538 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-26_23-25-47` | `Unregistered` | 16000 | 16025 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-27_11-14-32` | `Unregistered` | 66850 | 66869 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-08-28_22-56-51` | `Unregistered` | 89999 | 89999 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-09-01_22-39-00` | `Unregistered` | 89999 | 89999 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-09-04_21-33-15` | `Unregistered` | 89999 | 89999 |
| `logs/TEMP/Server/logs/backup/Unregistered/2026-09-07_21-58-38` | `Unregistered` | 84450 | 84475 |

## 실제 명령·검증과 미검증 범위

```bash
python /tmp/grad_log_inventory.py
python /tmp/grad_log_compare.py
python /tmp/grad_log_apply.py
python /tmp/grad_log_apply.py --apply
python /tmp/grad_log_document.py
```

- 이동·삭제 목록을 `/tmp/grad_log_plan.json`에 먼저 확정했다. 이동은 Path.rename으로 수행했으며 복사·병합·덮어쓰기는 하지 않았다. 재시작 job의 내부 attempt와 job.json은 그대로 유지했다.
- 전체 입력 파일을 정확히 하나의 작업에 대응시켰다. 이동 전후 모든 보존 파일의 상대경로·크기·mtime_ns·inode가 일치함을 확인한 뒤 중복 사본만 제거했다. 삭제된 중복을 제외한 누락 0개, TEMP 잔여 항목 0개다.
- 기존 backup의 전체 파일 메타데이터 보존 및 logs/rsl_rl의 전체 파일 목록·크기·mtime_ns·inode 동일을 확인했다. 이 두 경로의 기존 파일은 수정하지 않았다.
- 입력 snapshot이 판정 전후 동일하고 입력 symlink가 없음을 확인했다. 현재 프로세스 namespace에서는 train.py 학습을 발견하지 않았다. 다른 호스트의 프로세스 상태까지 확인한 것은 아니다.
- TensorBoard는 TFRecord framing과 Event protobuf를 직접 읽어 Loss/* step을 집계했다. CRC 전수 검사·checkpoint 역직렬화·학습 성능·GPU 재실행은 수행하지 않았다. 모든 run은 checkpoint만으로도 보존 임계 이상이므로 손상 로그를 0으로 간주한 삭제는 없다.
- 파일 전체 바이트 비교와 일부 SHA-256 검사는 중복 판정에만 수행하고 일반 이동 보존은 동일 inode와 메타데이터로 검증했다.
- 상세 등록 목록·진행 값·중복 비교·최종 대응·검증 수치는 [기계 판독 기록](2026-11-04_temp_log_classification.json)에 보존했다. 임시 실행 스크립트는 /tmp에 있으며 장기 보존 산출물은 이 문서와 JSON이다.

문서 검증: 변경 Markdown math 검사 1개 통과, 저장소 전체 링크 검사 errors=0, git diff --check 통과. 실제 Markdown 렌더링 검사는 수행하지 않았다.
