# Prof Revision Hard v0_3_3 구현·검증

2026-11-26. 사용자 요청은 직전 일반 v0_3_3 상속, 보상 구조 그대로 유지, 기존 Hard v0_3처럼 타겟 다양화·목표 거리 등 Scene 조건만 변경이다. 일반 v0_3_3은 이미 있으므로 새 ID를 `Inspire-Sweep-Prof-Revision-Hard-v0_3_3`, 실험명을 `inspire_sweep_prof_revision_hard_v0_3_3`으로 정했다.

## 기준과 변경 의도

코드 HEAD `cf70cd4bea328b8e2121d896c49bc87e05f14ce8`, 문서 HEAD `391e87be79363e0db3e265125759539dcab84712`. 이전 작업의 일반 v0_3_3 변경, README·사진 스크립트·IsaacLab 및 문서 작업트리를 보존했다. 변경 전5개 역할별 소스를 `outputs/prof_revision_hard_v0_3_3_validation/before`에 저장했다. `logs/rsl_rl`은 사용하지 않았다.

| 구성 | 일반 v0_3_3 | Hard v0_3_3 |
| --- | --- | --- |
| EnvCfg | `ProfRevisionV0_3_3EnvCfg` | 직접 자식 `ProfRevisionHardV0_3_3EnvCfg` |
| Scene | `ProfRevisionSceneCfg` 원통 | 기존 `ProfRevisionHardSceneCfg` 타겟8종 |
| Events | 기본 reset/geometry | 기존 `ProfRevisionHardEventsCfg`와 Hard layout/reset |
| 목표 거리 | 6–12cm | 최소5cm·상한 없음·선반 내부 유효 영역 |
| max_obstacles | 6 | 10 |
| layout_cell_size | 0.005m | 0.01m |
| layout capacity | 6 | 10 |
| PPO | 일반 v0_3_3 | 직접 자식, experiment name만 변경 |

Scene 분포 구현은 SceneCfg뿐 아니라 reset/geometry 이벤트와 배치 capacity/격자에도 걸쳐 있다. 기존 Hard의 이 구성만 재사용하며 새 샘플러/보상 함수를 만들지 않았다. 부모의 사후검증이 `_layout_capacity()`를 사용하므로 자식에서10을 반환한다. 기존17개 바디·자산8종·선택 규칙을 보존한다.

전체 보상 callable·params·weight·순서(진행100/역방향−120/Reach9.8/Formation0.1715/장애물변위−300 cap0.04 포함), Command·Observation·Action·Termination·Curriculum·물리·runtime·정밀 상태·telemetry는 일반 v0_3_3과 동일하다. 보상 클래스는 새로 만들지 않고 상속한다. 성공 XY3cm·TCP4m/s도 그대로다. runtime 등록은 `ProfRevisionV0_3_2Env` 재사용이다.

## 검사 명령과 범위

사용 Python은 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`다. 실제 검사 산출물은 `outputs/prof_revision_hard_v0_3_3_validation`에 둔다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/prof_revision_hard_v0_3_3_validation/check_contract.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_prof_revision_precision.py src/inspire_sweep_baseline/tests/test_prof_revision.py src/inspire_sweep_baseline/tests/test_prof_revision_hard.py -q -p no:cacheprovider --basetemp outputs/prof_revision_hard_v0_3_3_validation/pytest_tmp
```

전체 `to_dict()` 대조는 부모 일반 v0_3_3과 Scene/Events/max_obstacles/layout_cell_size만 차이나며, 이4개 값은 기존 Hard v0_3과 전체 동일함을 검사한다. 보상 전체와 순서는 일치해야 한다. PPO는 실험명만 차이, 기존 모든 ProfRevision Cfg/PPO의 작업 전후 설정 및 기존 소스 AST/등록 보존을 검사한다. 실제2환경 reset/3step·reward finite·역방향−120 wiring 확인을 수행한다. Isaac Sim은 로컬 설정·캐시 쓰기 필요에 따라 sandbox 밖에서 실행했다.

## 실행

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-Hard-v0_3_3 --num_envs 2048 --headless
```

학습은 시작하지 않았다. 장기 성공률·난도 변화에 따른 학습 안정성·정착/흔들림 개선은 미검증이며 기존 Hard 배치 스트레스 실험 결과를 이번 정책 성능으로 해석하지 않는다. [환경 계약](../environments/PROF_REVISION_V0.md#prof-revision-hard-v0_3_3).

## 완료 결과

- CPU60개 통과, 기존 ONNX deprecated 경고1개. Hard 목표/장애물/형상 회귀와 정밀 보상 경계·dt·부분reset 검사를 포함한다.
- `contract.json`: 전체 부모 대조·Hard 분포4개 설정 일치·보상 전체 동일·PPO 실험명만 변경·기존 Cfg/PPO 및 소스 AST 보존 모두 통과.
- `contract_live.log`: `CONTRACT_PASS`, `LIVE_PASS` 확인. 실제2환경 reset 및3step 완료, reward finite 및 RewardManager 역방향−120 확인. 기존 visual instancer 경고는 있었으며 검사 실패는 없었다.
- 변경 Python3개 compile 통과. 변경 Markdown5개 수식 검사 통과, 문서4개 내부457/외부2 링크 검사 오류0. 루트/문서 저장소 `git diff --check` 통과.

부모 및 기존 Hard는 수정하지 않았고 기존 사용자 변경을 보존했다. README·활성 안내·인계·환경 계약·개발 로그를 갱신했다. 학습/PPO 업데이트·commit·원격전송은 실행하지 않았다.
