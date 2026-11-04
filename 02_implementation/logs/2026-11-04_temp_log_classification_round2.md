# 2026-11-04 TEMP 추가 로그 분류 (2차)

## 요청·범위·판정

사용자가 추가한 TEMP 로그에 [동일 정리 기준](../../00_guidelines/11_TRAINING_LOG_CLEANUP.md)을 재적용했다. [1차 기록](2026-11-04_temp_log_classification.md)은 보존했다. 현재 등록 코드의 70개 ID와 agent experiment_name, 저장 env/agent 설정을 확인했다. 환경 코드는 수정하지 않았다.

- 입력: 18개 실행, 1678개 파일, 2692120828 bytes. 입력 외 파일과 symlink는 없었다.
- 결과: 500회 이상 8개를 정확한 환경 ID 폴더로 이동하고, 500회 미만 10개를 삭제했다. 삭제 실행은 Loss step+1 기준 2, 9, 5, 5, 2, 4, 259, 29, 5, 6회다. 모든 삭제 후보를 TensorBoard LegacyEventFileLoader로 다시 읽어 iteration을 재확인했다.
- 동일 환경의 별도 실행은 중복으로 간주하지 않았다. 기존 backup과 동명 1개는 공통 학습 파일 21개 바이트 일치, TensorBoard prefix 일치로 같은 실행임을 확인했다. exported/policy.pt와 policy.onnx는 달랐다.
- 중복 run 2026-10-21_19-31-34: 기존 최대 checkpoint 1900, 신규 최대 checkpoint 20450 및 Loss step 20453. 더 긴 신규 사본을 `inspire_contact_sweep_clutter_fusion__2026-10-21_19-31-34`로 보관하여 사용할 대상으로 지정했다. 기존 짧은 backup은 덮어쓰기·삭제하지 않았다.
- inspire_final_v2는 현재 Final-v2/Test-v2가 같은 runner experiment_name을 공유하므로 환경 식별이 확정되지 않았다. 단, 해당 개별 실행의 6회 진행은 확인되어 등록 여부와 무관한 500회 미만 규칙으로 삭제했다.

## 원래 경로 → 최종 경로

| 처리 | 원래 경로 | 최종 경로 | 완료 iteration 근거 |
| --- | --- | --- | ---: |
| 이동 | `logs/TEMP/inspire_contact_sweep_clutter_fusion/2026-10-21_18-24-12` | `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v0/2026-10-21_18-24-12` | 1229 |
| 이동 | `logs/TEMP/inspire_contact_sweep_clutter_fusion/2026-10-21_19-31-34` | `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v0/inspire_contact_sweep_clutter_fusion__2026-10-21_19-31-34` | 20454 |
| 500회 미만 삭제 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_holding_object_random_test_v0/2026-10-23_22-40-18` | 삭제 | 2 |
| 이동 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_holding_object_random_test_v0/2026-10-23_22-43-35` | `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-ObjectRandom-Test-v0/2026-10-23_22-43-35` | 1453 |
| 500회 미만 삭제 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v0/2026-10-23_20-23-39` | 삭제 | 9 |
| 500회 미만 삭제 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v0/2026-10-23_20-31-42` | 삭제 | 5 |
| 500회 미만 삭제 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v0/2026-10-23_20-42-37` | 삭제 | 5 |
| 500회 미만 삭제 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v0/2026-10-23_20-51-31` | 삭제 | 2 |
| 500회 미만 삭제 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v0/2026-10-23_21-00-03` | 삭제 | 4 |
| 500회 미만 삭제 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_holding_osc_v2/2026-10-24_02-22-38` | 삭제 | 259 |
| 이동 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_holding_osc_v2/2026-10-24_02-43-09` | `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2/2026-10-24_02-43-09` | 8604 |
| 이동 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_v2/2026-10-21_20-31-32` | `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v2/2026-10-21_20-31-32` | 14557 |
| 500회 미만 삭제 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_v3/2026-10-21_21-47-29` | 삭제 | 29 |
| 이동 | `logs/TEMP/inspire_contact_sweep_clutter_fusion_v3/2026-10-21_21-55-18` | `logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v3/2026-10-21_21-55-18` | 7390 |
| 500회 미만 삭제 | `logs/TEMP/inspire_final_goal_accuracy_v0_2/2026-10-30_16-49-04` | 삭제 | 5 |
| 이동 | `logs/TEMP/inspire_final_goal_accuracy_v0_2/2026-10-30_16-53-03` | `logs/backup/Isaac-Inspire-Final-GoalAccuracy-v0_2/2026-10-30_16-53-03` | 25906 |
| 이동 | `logs/TEMP/inspire_final_v1_test/2026-10-27_17-16-27` | `logs/backup/Isaac-Inspire-Final-Test-v1/2026-10-27_17-16-27` | 9600 |
| 500회 미만 삭제 | `logs/TEMP/inspire_final_v2/2026-10-26_16-53-48` | 삭제 | 6 |

## 검증·실제 명령·미검증 범위

```bash
python /tmp/grad_log_inventory.py > /tmp/grad_log_inventory_round2.out
python /tmp/grad_log_compare.py > /tmp/grad_log_compare_round2.out
python /tmp/grad_log_round2.py
```

- 전체 입력 파일이 정확히 하나의 이동·삭제 작업에 속함을 검증했다. `/tmp/grad_log_round2_plan.json`으로 작업 목록을 먼저 확정한 뒤 실행했다. 이동은 Path.rename, 삭제는 승인된 TEMP의 짧은 실행에 한정한 shutil.rmtree를 사용했다.
- 이동된 1621개 파일은 원래 상대경로·크기·mtime_ns·inode가 모두 일치한다. 삭제된 57개 파일은 28987695 bytes다. TEMP 잔여 0개, 누락 0개다.
- 기존 backup의 모든 파일 메타데이터 보존을 확인했다. logs/rsl_rl은 전체 파일 목록·크기·mtime_ns·inode 동일을 확인했으며 수정하지 않았다.
- 작업 직전 입력 snapshot이 그대로임을 확인했다. 다른 호스트의 프로세스 상태, checkpoint 역직렬화, GPU 학습 및 학습 성능은 검증하지 않았다. 일반 이동의 전체 내용 재해싱 대신 동일 inode와 메타데이터를 확인했다.
- [상세 JSON](2026-11-04_temp_log_classification_round2.json)에 현재 등록 목록·설정 대응·Loss step·중복 바이트 비교·경로 대응·검증 결과를 저장했다. 임시 스크립트는 /tmp에 있다.

문서 검사 결과: 변경 Markdown math 1개 통과, 전체 문서 링크 errors=0, git diff --check 통과. 실제 렌더링은 확인하지 않았다.
