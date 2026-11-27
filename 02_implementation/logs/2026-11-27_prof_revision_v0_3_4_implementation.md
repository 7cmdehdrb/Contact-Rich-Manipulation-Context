# Prof Revision v0_3_4 구현·검증

## 요청과 기준

2026-11-27 사용자 요청: 일반 v0_3_3을 상속한 새 v0_3_4에 retreat−100, 팔/손 비용 통합 검토, 접촉과 힘 방향 gate 일치, 장애물 접촉 허용5N, 손목 힘 변화5N 및 모멘트 변화0.3Nm를 적용한다. 기존 환경 직접 수정이 아닌 새 파생 환경 생성이다.

기준 workspace HEAD는 `26312351bce566527e805b2f71f2caf18bcd756f`, 문서 submodule HEAD는 `9ed8eafc2bda9e1ca30035acbf1d962ba1ca581f`다. 시작 시 IsaacLab untracked 상태, 이전 Play 계측·분석 script 변경, 문서 인계 변경 및 impact 보고서·로그가 있었으며 보존했다. 학습 로그를 수정하거나 정리하지 않았다.

활성 Python 패키지327개 파일을 `outputs/prof_revision_v0_3_4_validation/before/`에 저장하고 SHA256 목록도 남긴 뒤 비교했다. 이 디렉터리는 로컬 검증 산출물이며 Git 추적 대상이 아니다.

## 최종 변경 표

| 요청 | v0_3_3 | v0_3_4 | 의도·영향 |
| --- | --- | --- | --- |
| Retreat weight | −120 | −100 | 동일 가중 거리H의 이탈 비용만 조정 |
| Action-rate term | arm·hand 각각−0.03 | `action_rate` 하나,−0.03 | 각 그룹 raw cap100 적용 후 합산하여 기존 총 비용 보존 |
| Joint-velocity term | arm·hand 각각−0.03 | `joint_velocity` 하나,−0.03 | 기존 이름으로 선택한 팔6·손12관절 및 그룹 cap100 보존 후 합산 |
| 힘 방향 gate | 현재 접촉·유효성과 평균 수평 합력≥1N | 현재 접촉·유효성 | 별도 합력 문턱을 제거하여 약한 접촉에서도 방향 계산 |
| 장애물 허용 힘 | 50N | 5N | 기존 함수·weight−0.04·raw cap100 유지 |
| 손목 힘 크기 변화 허용 | 30N | 5N | 정책 스텝20ms 기준; 기존 weight−0.1 유지 |
| 손목 모멘트 크기 변화 허용 | 3Nm | 0.3Nm | 기존 최대 severity·지수 함수·raw cap1 유지 |

Action rate는 명령 변화량 제곱합, joint velocity는 실제 관절 각속도 제곱합이다. 서로 다른 물리량이므로 두 종류를 하나의 보상으로 합치지는 않는다. 같은 종류의 팔·손만 합쳐 활성 reward16개를14개로 줄였다. 새 term raw 최대는 각각200이다. 합친 뒤100으로 자르면 부모와 총 비용이 달라지므로 사용하지 않는다. Action-limit 팔/손 term은 이번 요청 범위 밖이므로 유지한다. 부동소수점에서 weight 곱셈·덧셈 순서는 달라질 수 있지만 수학적 총 비용은 동일하다.

접촉은 기존 `ContactSamples`가 physics substep 중 하나라도 유효한 타겟 법선 하중 합≥0.01N이면 현재 스텝 접촉으로 판정한다. 모든 substep의 유효성과 최근3스텝 중2회 조건도 유지한다. 하중 합과 평균 수평 합력은 서로 달라 평균 합력에0.01N을 다시 적용해도 의도한 일치를 보장하지 못한다. 따라서 새 상태는 기존 접촉 마스크를 그대로 사용한다. 합력0 또는 목표 방향이 정의되지 않는 거리≤1e−12m에서는 정렬값0이고, 반대 힘도 정렬값0이다. 접촉ON이 모든 상황에서 정렬 보상1을 뜻하지는 않는다. 기존3–6cm force fade·거리 민감도H는 유지한다.

부모 EnvCfg의 `__post_init__`가 임계값50/30/3을 강제로 재지정하므로 새 EnvCfg는 `super().__post_init__()` 이후5/5/0.3을 다시 적용한다. RewardCfg 선언만 변경해 실제 초기화에서 되돌아가는 오류를 방지한다.

## 등록·파일·전체 계약 대조

전체 task ID는 `Inspire-Sweep-Prof-Revision-v0_3_4`다. EnvCfg는 `ProfRevisionV0_3_4EnvCfg(ProfRevisionV0_3_3EnvCfg)`, RewardCfg는 `ProfRevisionV0_3_4RewardsCfg(ProfRevisionV0_3_3RewardsCfg)`다. Runtime은 부모 v0_3_3이 사용하던 `ProfRevisionV0_3_2Env`를 상속한 `ProfRevisionV0_3_4Env`이며, 상태 생성만 `ProfRevisionContactAlignedState(ProfRevisionPrecisionState)`로 교체한다. PPO는 `ProfRevisionV0_3_4PPORunnerCfg(ProfRevisionV0_3_3PPORunnerCfg)`이고 실험명은 `inspire_sweep_prof_revision_v0_3_4`다.

변경 코드는 기존 역할별 파일7개에만 추가했다: 패키지 `__init__.py`, `envs/prof_revision_envs.py`, `runtime/prof_revision.py`, `mdp/rewards/prof_revision.py`, `mdp/reward_functions/prof_revision.py`, `mdp/common/prof_revision_state.py`, `agent/prof_revision_ppo_cfg.py`. 기존 함수를 이동하지 않았다. 상태 부모의 기존 방향 gate 식만 메서드로 추출하여 부모 식을 그대로 유지하고 자식에서 재정의한다. 기존 테스트 파일 `tests/test_prof_revision_precision.py`에 약한 힘·0합력·반대 힘·접촉OFF·무효 접촉 회귀를 추가했다.

| 계약 | 최종 차이 |
| --- | --- |
| Gym 등록·상속 | 새 ID 하나, EnvCfg·RewardCfg 직접v0_3_3 상속; 기존 등록 보존 |
| Runtime·reset lifecycle | 부모 step/reset 그대로, 자식 상태 factory만 교체 |
| Scene·자산·물성·배치·Command·Event | 부모 전체 보존; 일반 v0_3_3 초기화 사용, IK/Hard 조건 도입 없음 |
| Observation·Action | 순서·함수·params·108/176D·12D·scale·clip·noise·제어 모두 보존 |
| Reward | 위 변경 표 외 이름·callable·params·weight 보존; 활성14개 |
| Termination | 전부 보존, 목표XY 거리≤3cm·TCP4m/s 등 변경 없음 |
| Curriculum | 빈 구성 보존, 변경된 term을 가리키는 일정 없음 |
| PPO·모델 | 실험명 외 모든 설정 보존 |
| 로그 | 팔/손4개 reward 키를 `Episode_Reward/action_rate`·`Episode_Reward/joint_velocity` 2개로 통합; 나머지 유지 |
| 장애물 이동 비용 | −300·reset 대비3D 제곱변위·raw cap0.04 유지; 이전 제안의 최대 이탈 증분 비용 미도입 |

## 검증 명령·산출물

환경은 Windows11·Isaac Sim5.1·RTX4070, Python은 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`를 사용한다. Workspace 루트에서 실행한다.

```powershell
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -m pytest src/inspire_sweep_baseline/tests/test_prof_revision.py src/inspire_sweep_baseline/tests/test_prof_revision_precision.py -q -p no:cacheprovider --basetemp outputs/prof_revision_v0_3_4_validation/pytest_regression
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -u outputs/prof_revision_v0_3_4_validation/validate.py --headless
python example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_markdown_math.py src/inspire_sweep_baseline/README.md example/Contact-Rich-Manipulation-Context/01_plan/00_HANDOFF_BRIEF.md example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md example/Contact-Rich-Manipulation-Context/02_implementation/environments/PROF_REVISION_V0.md example/Contact-Rich-Manipulation-Context/02_implementation/logs/2026-11-27_prof_revision_v0_3_4_implementation.md
git diff --check
git -C example/Contact-Rich-Manipulation-Context diff --check
```

CPU 검사65개 통과. 기존 ONNX export의 비권장 API 경고1건만 있었다.

실제 Isaac Sim 검증은 seed42·16환경에서 기존v0_3_3 `2026-11-26_21-31-25/model_8600.pt`의 결정론적 추론으로100정책step을 실행했다. 전체 결과는 workspace의 `outputs/prof_revision_v0_3_4_validation/result.json`, 전체 설정은 `contract.json`, 성공 로그는 `smoke_verified.log`에 있다.

| 검사 | 결과 |
| --- | --- |
| 기존 설정·PPO 대조 | 기존46개 설정 비교 통과, 부모 구성 보존 |
|327개 파일의 기존 정의·등록AST 대조 | 새 등록1개와 새 클래스/함수 추가; 기존 정의 동일, 부모gate 추출식 동일 |
| 기존 상태 전후 실행 |64행×30step의 무작위 접촉·힘·위치 입력에서 기존 모든tensor 완전 일치 |
| 부모와 자식 전체 구성 | 보상 차이를 제거하면 나머지EnvCfg 완전 일치; PPO는 실험명만 차이 |
| 실제 Manager |14개 reward, curriculum0개, 장애물5N·손목5N/0.3Nm 확인 |
| 팔/손 합산 | 실제 이름 해석으로 팔6·손12관절 선택; 입력scale0.01/1/10/100의32행에서 기존 두cap합과 완전 일치 |
| 실제 손목 비용 경계 |5N/0.3Nm 바로 아래·정확한 경계에서0, 바로 위에서양수,12.5N/0.75Nm에서raw1 |
| 기존 checkpoint 호환 | Actor·Critic 로드와100step 추론 통과, 입력108/176D·행동12D 보존 |
| 실제 reward 계산 |101회 계산에서 통합 비용·전체dt 합산 대조 통과 |
| 부분reset | 짝수행만reset, 홀수행 상태tensor 완전 보존 |
| 자동reset |16행 강제timeout 처리·episode 카운터 및 새 상태cache 초기화 통과 |
| 유한성 |100정책step의 모든 관측·보상finite |

초기 검증 실행에서는 검증 코드의 callable 직렬화 비교와 손 관절 수 가정(행동6D와 실제 관절12개 혼동)을 수정했다. 환경 코드를 수정한 오류는 아니며, 최종 검증은 전체를 다시 실행하여 통과했다. 첫 실행의 `app.close()`가 예외 출력을 가려 예외를 먼저 기록하도록 검증 script도 보강했다. 성공 표시와 `result.json`을 완료 근거로 사용하고 exit0만으로 성공 판정하지 않았다.

변경Markdown5개 수식 검사와 변경Python8개 `py_compile`, 두 저장소의 `git diff --check`를 통과했다. 변경 문서5개 전체 링크 검사는 internal659/external30개 중 README에 기존 누락 경로 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md`1건을 보고했다. `git show HEAD:src/inspire_sweep_baseline/README.md`에서도 존재하는 기존 링크이며 이번 요청 범위 밖이라 보존했다. 새로 추가한 링크 오류는 없다. README를 제외한 변경 문서4개는 internal478개 검사·오류0이었다.

## 검증 범위의 한계

新環境の長期再学習・成功率・衝撃低減効果は今回の実装検証では確定しない。既存v0_3_3 checkpointは入力・モデル形状が同じなので動作確認に使えるが、新報酬で学習された方策ではない。以前のPlayで確認したF/T読み取りの大接触見落とし自体を修正する要求ではなく、F/T読み取り経路も維持する。
