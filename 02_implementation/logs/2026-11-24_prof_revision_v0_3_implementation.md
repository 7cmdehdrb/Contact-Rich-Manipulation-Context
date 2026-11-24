# Prof Revision v0_3 구현 기록

2026-11-24. [환경 계약](../environments/PROF_REVISION_V0.md#prof-revision-v0_3).

## 요청·기준

사용자 요청은 v0을 직접 상속하는 다른 분기 v0_3이다. 손등/손바닥 선호 삭제, 기존 Joint Termination 삭제, UR5e 마지막 마디 TCP 선속도4m/s 이상 종료를 요구했다. TCP를 EEF와 구분하라는 명시적 지시에 따라 로봇의 `WRIST_BODY_NAME`과 마지막 arm body인 `wrist_3_link`의 링크 원점을 사용한다.

root HEAD `7572d9df73b9bc413c9abe1e1d58def3198add65`에서 기존 사용자 `docs/SSH.md` 및 앞선 v0_2 구현/문서 미커밋 변경을 보존했다. 시작 시 전체 Python 내용 snapshot을 `outputs/prof_revision_v0_3_validation/before.json`에 기록했다. 이 snapshot을 기준으로 기존 미커밋 구현까지 보존을 비교했다. 문서 저장소는 독립 submodule이며 기존 변경/HEAD를 유지한다.

## 구현과 최종 차이

| 항목 | 부모 → v0_3 |
| --- | --- |
| EnvCfg | ProfRevisionV0_3EnvCfg가 ProfRevisionEnvCfg 직접 상속 |
| Sweep | 면 선호 wrapper1.5/0.7 → 순수 진행 함수, weight100·면 계수1 |
| 팔 관절 속도 종료 | abs(qdot)>1.0 term → None으로 비활성 |
| TCP 속도 종료 | 없음 → wrist_3_link 원점 월드3D 선속도 norm>=4.0, time_out=False |
| 성공 판정 | 기존 실패 제외 목록에서 관절 종료를 TCP 현재 predicate로 교체 |
| 기타 보상 | 부모15개·Formation0.245·관절 L2 비용 보존, 활성16개 |
| 나머지 Manager/물리/runtime | 부모 상속·보존 |
| PPO | 모든 수치 보존, 로그 inspire_sweep_prof_revision_v0_3만 변경 |

새 termination 함수는 선택된 link-origin 속도를 읽는다. 로컬 Isaac Lab `articulation_data.py:body_link_vel_w`의 COM→link 속도 보정 구현을 확인했다. 손 쪽 offset이나 COM 위치를 TCP로 오인하지 않는다. 3D norm으로 방향에 대칭이고 정확히4에서 종료한다. physics substep peak가 아닌 기존 policy step 끝의 상태를 검사한다.

v0_3 성공 함수는 설정된 TCP term callable/params를 직접 평가한다. 상속 config의 success가 추가 term보다 먼저 계산될 수 있기 때문에 오래된 flag를 읽지 않게 하기 위함이다. 기존 부모 성공 함수는 수정하지 않았다. 기존 runtime의 종료·timeout 집계는 이름 동적 조회/성공 flag 기반이므로 그대로 재사용한다.

새 사건 비용·margin 비용은 요청 범위에 없어 추가하지 않았다. 기존 v0_1/v0_2/v1은 그대로 보존한다.

## 검증

산출물 경로: workspace `outputs/prof_revision_v0_3_validation/`.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q src/inspire_sweep_baseline/tests/test_prof_revision.py src/inspire_sweep_baseline/tests/test_sweep_single_contact_v1.py
```

CPU62개 통과(3.69초), 기존 ONNX deprecation warning1건. 새 테스트는4 바로 아래/정확히/위·음수·3D norm·빠른 EEF와 관절 속도 제외·동시 실패/timeout·성공3cm 경계·비정상 threshold를 검증했다.

현재 작업 시작 snapshot과의 AST 대조에서 기존 생산 정의17개와 기존 등록 호출 모두 보존했다. Python 변경은 생산6개·기존 validator1개·기존 test1개로8개, 나머지 Python 내용은 동일하다(`audit.json`). 이전 v0_2 변경까지 포함한 보존 검사다.

GPU·학습·문서 검증 결과는 아래에 후속 기록한다.

## 미검증 범위

장기 학습 성공률·동작 안정성·실제로 TCP가4m/s에 도달하는 물리 궤적·2048환경 성능은 별도 실험이 필요하다. 속도 샘플 주입 검증은 실제 물리 운동으로 그 속도를 만든 검증과 구분한다. 기존 학습 로그는 수정하지 않는다.

## GPU·PPO 완료 결과

실제 RTX3090·4환경·seed42 실행:

```bash
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_prof_revision.py --task Inspire-Sweep-Prof-Revision-v0_3 --num-envs 4 --output outputs/prof_revision_v0_3_validation/smoke.json --headless
```

`PROF_REVISION_SMOKE_PASSED`와 결과 JSON을 확인했다. 부모 전체 EnvCfg는 Sweep 함수와 종료 교체/성공 실패 제외 조건 외 동일, PPO는 실험명 외 동일이다. 실제 body ID가 wrist_3_link 하나로 resolve됨을 확인했다. 활성 reward16개, arm_joint_velocity 종료 없음, tcp_linear_velocity 존재. 12개 zero-action step·관측108/176D 유한·Formation 부모 식/weight·보상 총합·부분 reset·자동 timeout·고정/추적 OBB·JIT export 통과.

실제 termination manager compute 직전 TCP 링크 속도 buffer에 환경별3.999/4.0/−4.001/벡터(3,4,0)m/s를 주입하고 원본을 복원했다. 일반 step에서 flags=[false,true,true,true], 뒤3개만 종료·자동 reset. 모든 환경을 timeout 직전 및 목표 위치로 두었을 때 success=[true,false,false,false]로 실패 우선순위를 확인했다. 이 검증은 속도 buffer fixture이며 물리적4m/s 동작 실험이 아니다. API가 반환하는 목표 command가7D인 점을 fixture에서 처음 놓쳐3D center 대입에 실패했으며 `[:, :3]`으로 수정 후 재검증했다. 생산 코드 오류는 아니었고 초기 로그는 `smoke_initial_fixture.log`로 보존했다.

짧은 PPO:

```bash
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3 --num_envs 16 --max_iterations 1 --resilient-attempt-dir outputs/prof_revision_v0_3_validation/ppo_smoke --resilient-target-iterations 1 --logger tensorboard --headless
```

16환경×36step=576transition·PPO1회 완료. collection3.762초/learning0.506초, value loss0.1655·surrogate−0.0574·entropy17.0155. `model_0.pt`의 모델/optimizer132개 Tensor 모두 유한, optimizer step32, TensorBoard75개 scalar tag 모두 유한(`ppo_check.json`). 장기 정책 성능이나2048환경 처리량을 입증하지 않는다.

문서 검사: 변경5개 Markdown math 통과, 문서 저장소4파일 links internal401/external1 오류0, README 신규 링크2개 파일·anchor 확인. 두 저장소 `git diff --check` 통과. 최종 변경 Python8개 컴파일 및 이전 정의/등록 보존 대조 통과. 사용자 변경·기존 학습 로그를 보존했고 커밋은 만들지 않았다.
