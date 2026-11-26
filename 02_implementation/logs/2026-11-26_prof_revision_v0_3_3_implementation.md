# Prof Revision v0_3_3 구현·검증

2026-11-26. 사용자 요청은 v0_3_2 직접 상속 환경 추가 및 역방향 페널티 계수120 적용이다. 목표 부근 흔들기/왕복으로 보상을 누적하는 사용자 관찰이 근거다. 기존 환경 직접 수정이 아니다.

## 기준과 보존

코드 HEAD `cf70cd4bea328b8e2121d896c49bc87e05f14ce8`, 문서 HEAD `391e87be79363e0db3e265125759539dcab84712`. 시작 시 README·사진 촬영 스크립트·IsaacLab 및 문서의 인계/활성 안내/환경 설명/사진 로그 사용자 변경이 있었다. 이를 보존하고 `logs/rsl_rl`은 건드리지 않았다. 변경 전 역할별 소스는 `outputs/prof_revision_v0_3_3_validation/before`에 저장했다.

## 최종 변경 계약

| 항목 | 부모 v0_3_2 | 새 v0_3_3 |
| --- | --- | --- |
| Gym ID | `Inspire-Sweep-Prof-Revision-v0_3_2` | `Inspire-Sweep-Prof-Revision-v0_3_3` |
| EnvCfg | `ProfRevisionV0_3_2EnvCfg` | 직접 자식 `ProfRevisionV0_3_3EnvCfg` |
| RewardsCfg | `ProfRevisionV0_3_2RewardsCfg` | 직접 자식 `ProfRevisionV0_3_3RewardsCfg` |
| sweep_retreat weight | −40 | −120 |
| Runtime | `ProfRevisionV0_3_2Env` | 동일 클래스 재사용 |
| PPO | `ProfRevisionV0_3_2PPORunnerCfg` | 직접 자식, experiment name만 `inspire_sweep_prof_revision_v0_3_3` |

역방향 callable `precision_sweep_retreat`·params·정밀 상태·dt 적용·로그 키·진행+100·Reach9.8·Formation0.1715·장애물변위−300(cap0.04) 및 나머지 보상 전부 유지. Scene·자산·Command·Event/reset·Observation·Action·Termination·빈 Curriculum·성공 XY 3cm·TCP4m/s 종료·정밀 거리4개 파라미터·물리·PPO 수치도 유지했다. 보상 순서는 동일하다. 기존 모든 클래스/함수와 등록 AST를 보존하며 새 reward import와 새 선언/등록만 추가했다.

동일한 가중 거리 H 왕복에 대한 Sweep 두 항은 최대 `(100−120)×ΔH = −20×ΔH`다. 역방향 비용은 접촉/힘 gate가 없고 진행 gate는0–1이므로 해당 두 항에서 왕복 이익은 사라진다. 다른 보상과 할인·학습까지 포함한 흔들림 완전 방지는 이 수식만으로 입증되지 않는다. 보상 함수·정지 보상·다른 계수 변경은 요청 밖이므로 하지 않았다.

## 검증

사용 Python은 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`. 기본 `python`은 Isaac Lab/pytest 미설치라 실제 환경 Python으로 다시 실행했다. 검증 산출물은 `outputs/prof_revision_v0_3_3_validation`에 격리했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_prof_revision_precision.py src/inspire_sweep_baseline/tests/test_prof_revision.py src/inspire_sweep_baseline/tests/test_prof_revision_hard.py -q -p no:cacheprovider --basetemp outputs/prof_revision_v0_3_3_validation/pytest_tmp
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/prof_revision_v0_3_3_validation/check_contract.py
```

CPU60개 통과, 기존 ONNX deprecated 경고1개. 0/3/6cm·dt·접촉·왕복·부분reset·부모 회귀 검사 포함. 실제 Isaac Lab import 및 전체 `to_dict()` 대조 통과: 부모 대비 새 환경은 `rewards.sweep_retreat.weight` 한 값만 다르고 PPO는 실험명만 다르다. 모든 기존 ProfRevision Cfg/PPO의 작업 전후 전체 설정이 동일하며 기존 소스 AST 보존 확인. `contract.json`과 `pytest.log`에 결과가 있다.

검증 도구 초기 실패는 이전 모듈을 `sys.modules`에 넣지 않아 dataclass 해석이 실패한 것이며 도구를 수정해 계약 검사를 통과했다. sandbox에서는 Isaac Sim 사용자설정 쓰기 오류 후 물리 초기화가 멈춰 로컬 설정·캐시 쓰기를 허용한 실행으로 재시도했다. live 결과와 문서 검사 결과는 아래 완료 기록에 기재한다.

## 실행과 미검증 범위

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3_3 --num_envs 2048 --headless
```

학습은 시작하지 않았다. 장기 성공률·실제 흔들림 억제·정착 개선·학습 안정성은 미검증이다. 새 환경의 검증을 부모 학습 결과로 대체하지 않는다. [환경 계약](../environments/PROF_REVISION_V0.md#prof-revision-v0_3_3).

## 완료 기록

실제2환경 reset 및3step 완료, reward finite와 활성 RewardManager의 `sweep_retreat.weight == -120` 확인. `contract.json`의 `live_envs=2`, `live_steps=3` 및 `contract_live.log`의 `LIVE_PASS`로 완료를 확인했다. 기존 PhysX/visual instancer 경고가 있으나 step 검사는 통과했다. PPO 업데이트/장기학습은 실행하지 않았다.

문서4개 수식 검사 통과, 내부452·외부2개 링크 검사 오류0, 루트 및 문서 저장소 `git diff --check` 통과. README와 인계·활성 안내·환경 계약·개발 로그를 갱신했다. 파일/함수 이동·commit·원격전송 없음.
