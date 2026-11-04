# 2026-11-04 Unregistered 등록 환경 재분류

## 요청·범위

사용자가 `logs/01. Models/Unregistered`로 옮긴 보관 로그를 현재 `src/inspire_sweep_baseline` 등록 환경과 대조하고, 등록 환경으로 확인되면 해당 폴더로 이동하도록 요청했다. 현재 등록 환경의 보관 위치인 `logs/backup/<정확한 Gym ID>`를 목적지로 사용했다. 이번 요청은 재분류이며 학습 길이에 따른 삭제·중복 삭제는 수행하지 않았다.

[1차 정리 기록](2026-11-04_temp_log_classification.md)에서 설정 누락으로 식별 불확실하게 남긴 Realistic Physics 실행 1개를 추가 근거로 식별했다. 나머지 기존 작업 기록과 사용자 변경은 보존했다. 진단 스킬의 재현·검증 방식을 데이터 위치 검사에 적용했으며 코드 변경·장기 자동화 테스트는 추가하지 않았다.

## 근거와 결과

현재 `__init__.py`를 경량 Gym registry 대역으로 실행하여 실제 등록 70개를 확인했다. Unregistered의 71개 디렉터리(70개 run, 보조 로그 1개)에 대해 저장 env.yaml의 함수 모듈과 agent.yaml의 experiment_name을 조사했다. 이름만으로 분류하지 않았다.

- Realistic Physics 1개: `2026-10-13_17-39-41_realistic_mass_friction`에는 params/TensorBoard가 없었다. 그러나 기존 `Isaac-Inspire-Sweep-Realistic-Physics-v0`의 동명 실행은 agent experiment가 `inspire_sweep_realistic_physics`이고 env 설정도 해당 패키지를 참조한다. 부분 사본의 135개 파일 중 132개가 그 실행과 SHA-256이 동일하다. 파일 이름뿐 아니라 내용까지 확인하여 같은 학습에서 나온 부분 사본으로 식별했다.
- 기존 보관본과 `model_6750.pt`, `exported/policy.pt`, `exported/policy.onnx`가 다르므로 병합·덮어쓰기·중복 삭제하지 않았다. 기존 폴더는 존재해 새 환경 폴더 생성은 필요하지 않았고, 이동할 run 이름에 `Unregistered__`를 붙였다.
- `2026-10-21_19-36-46`: experiment가 `inspire_contact_sweep_clutter_fusion_v1`이다. 현재 등록에서 Fusion-v1은 명시적으로 제거됐다. [v3 재구성 기록](2026-10-21_clutter_fusion_v3.md)은 이름뿐 아니라 부모·보상·종료 조건 변경도 명시한다. 저장 env에는 `eef_orientation` weight=-0.02가 남아 있지만 현재 v3은 이를 제거한다. 따라서 이 실행을 현행 v3 또는 v1_0에 잘못 합치지 않고 유지했다. `tests/test_clutter_fusion_v3_curriculum.py`의 v1 미등록 assertion도 코드로 확인했다.
- 나머지 설정 있는 67개 run은 `sweep_rl`, `sweeping_policy`, `single_object_sweep`, `hand_manipulation_rl`, `hand_manipulation_test`, `sweep_inspire_rl` 등 과거 별도 패키지를 참조한다. 현재 inspire_sweep_baseline 등록과 연결되는 근거가 없어 유지했다. 이름에 inspire가 있거나 비슷한 조작 과제라는 사실을 현재 환경과 동일시하지 않았다.
- `2026-08-10_03-46-24`는 env/agent 설정이 없고 git/IsaacLab.diff만으로 과제를 확정할 수 없어 유지했다. `_auxiliary`는 CPU smoke 로그 보조 디렉터리이며 학습 실행으로 분류하지 않았다.

## 이동 대응

| 원래 경로 | 최종 경로 |
| --- | --- |
| `logs/01. Models/Unregistered/2026-10-13_17-39-41_realistic_mass_friction` | `logs/backup/Isaac-Inspire-Sweep-Realistic-Physics-v0/Unregistered__2026-10-13_17-39-41_realistic_mass_friction` |

이동 1개, 삭제 0개, Unregistered 잔여 70개 디렉터리(69개 run 및 보조 디렉터리 1개)다. 더 긴 원본 보관 run은 기존 이름 그대로 유지한다.

## 재현·검증

```bash
python /tmp/grad_unregistered_audit.py
python /tmp/grad_unregistered_move.py
python /tmp/grad_unregistered_audit.py
```

최초 audit는 `confirmed registered but unclassified 1` 및 `MISCLASSIFIED` assertion으로 실패했고, 이동 후에는 0 및 `PASS: confirmed registered run is in its environment folder; 135 files retained`를 출력했다. 이 검사는 파일 분류 상태에 대한 검사이며 시뮬레이션 실행 검사가 아니다.

이동 전에 `/tmp/grad_unregistered_move_plan.json`으로 대상·목적지·근거를 확정했다. Path.rename으로 이동했고, 이동한 135개 파일 전체의 SHA-256 및 상대경로·크기·mtime_ns·inode를 전후 대조했다. 전체 `logs` 트리의 파일 목록·크기·mtime_ns·inode를 비교하여 이 1개 경로 이동 외의 변경이 없음을 확인했다. 기존 목적지, 남은 Unregistered, `logs/rsl_rl`과 다른 학습 로그 모두 보존했다. 소스 코드·환경 설정은 변경하지 않았다.

파일 내용 해시는 이동 대상과 동일 실행 비교에 사용했다. 전체 다른 로그는 메타데이터 보존을 확인했으며 전수 해싱하지 않았다. checkpoint 역직렬화·정책 실행·GPU 학습·성능은 검증하지 않았다. 등록 수집은 실제 등록 코드를 실행했지만 Isaac Lab 환경 자체를 초기화한 것은 아니다.

[상세 판정·해시·등록 목록·결과 JSON](2026-11-04_unregistered_reclassification.json)에 71개 디렉터리 전체 조사 결과와 이동 근거를 보존했다. 임시 실행 스크립트는 `/tmp`에 있다. 문서 검증: 변경 Markdown math 검사 통과, 전체 링크 errors=0, git diff --check 통과. 렌더링 검사는 수행하지 않았다.
