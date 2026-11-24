# Prof Revision v0_1 추가·검증

작성일: 2026-11-24. 상태: **환경 구현·등록 및 4환경 GPU smoke 완료. 학습 미실행.**

## 요청·기준·의도

사용자는 `inspire_sweep_prof_revision_v0`의 직접 자식 `inspire_sweep_prof_revision_v0_1`을 만들고 기존 Single Contact v1의 `arm_joint_failure` 페널티만 추가하도록 요청했다. 팔 속도 종료 사건당−3.0을 재사용하며 v1의 Formation 변경은 적용하지 않는다.

작업 시작 workspace commit `c2341545a7cf99b54b0ae0b70faac6f8e5bd9dfb`, 문서 저장소 commit `10ff0cd3ac2a3b7388d0daaf89dafa2a22bec623`. 양쪽 작업트리는 시작 시 clean이었다. 서브모듈 commit을 변경하지 않았고 기존 학습 로그·checkpoint도 수정하지 않았다. 기준 SHA256은 [before.json](../../../../outputs/prof_revision_v0_1_validation/before.json)에 기록했다.

## 구현과 변경 전후

| 역할 | 구현 |
| --- | --- |
| Gym ID | `Inspire-Sweep-Prof-Revision-v0_1` |
| EnvCfg | `ProfRevisionV0_1EnvCfg(ProfRevisionEnvCfg)` |
| Rewards Cfg | `ProfRevisionV0_1RewardsCfg(ProfRevisionRewardsCfg)` |
| 추가 term | `arm_joint_failure`, 기존 callable 재사용, weight−3.0 |
| Runtime | 부모 `ProfRevisionEnv` 재사용 |
| PPO | `ProfRevisionV0_1PPORunnerCfg(ProfRevisionPPORunnerCfg)` |
| PPO 변경 | `experiment_name=inspire_sweep_prof_revision_v0_1`만 변경 |

기존 역할별 `envs/prof_revision_envs.py`, `mdp/rewards/prof_revision.py`, `agent/prof_revision_ppo_cfg.py`에 자식을 추가하고 패키지 `__init__.py`에 등록했다. 기존 클래스 선언·등록은 보존했다. 검증 스크립트 `scripts/check_prof_revision.py`는 v0_1 선택과 부모 Formation 검사를 추가했다. 패키지 README·환경 계약·현재 인계·활성 환경 안내를 갱신했다.

실제 보상은 기존 함수가 계산하는 `termination_manager.get_term('arm_joint_velocity').float()/step_dt`에 weight−3.0과 RewardManager dt를 곱해 **실제 속도 종료 step당−3.0**이다. 다른 실패만 발생하면 이 항은0, 속도 종료와 다른 실패가 동시 발생하면 각각의 비용을 합산한다. 팔 속도 종료 조건1.0rad/s 초과와 기존 연속 속도 비용은 그대로다.

## 전체 대조·검증 결과

실제 `EnvCfg.to_dict()` 전체 비교에서 추가 `arm_joint_failure` term을 제거하면 부모 v0와 정확히 동일했다. Formation callable·params·weight0.245도 동일하고, `formation_mode` 필드가 없음을 확인했다. 따라서 **유일한 환경 동작 차이는 사건 비용 추가**다. 최종 보상17개이며 기존16개 상대 순서를 유지하고 사건 비용을 마지막에 추가한다.

Formation은 `0.05/(0.05+sum(d_i))`이고 Reach 허용 반경0.10m·관측108/176D·물리·Scene/reset·Command·Action·나머지 Reward·Termination·빈 Curriculum 설정은 부모와 같다. PPO 전체 비교는 experiment_name만 제외하고 동일했다. Reach5cm의 단일 반경 차이도 기존대로 확인했다.

[audit.json](../../../../outputs/prof_revision_v0_1_validation/audit.json)의 AST 대조는 변경된 production 파일의 기존 정의9개와 기존 Gym 등록을 모두 보존했음을 확인했다. 변경 Python5개 외 나머지 Python 파일은 작업 전 SHA256과 동일했다. 특히 runtime·기하·보상 함수·관측·종료 함수는 변경하지 않았다. 부모 v0·Reach5cm v0·기존 v1에도 동작 변경을 전파하지 않는다. 변경 Python5개 `py_compile` 통과.

실제 GPU 검증 명령:

```bash
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/check_prof_revision.py \
  --task Inspire-Sweep-Prof-Revision-v0_1 --num-envs 4 --headless \
  --checkpoint logs/TEMP/2026-11-24/inspire_sweep_prof_revision_v0/2026-11-24_00-27-46/model_6100.pt \
  --output outputs/prof_revision_v0_1_validation/smoke.json
```

RTX3090·원래 자산·seed42에서 exit0으로 완료했다. [결과 JSON](../../../../outputs/prof_revision_v0_1_validation/smoke.json) · [원본 로그](../../../../outputs/prof_revision_v0_1_validation/smoke.log).

- 12step zero-action 구간의 보상·관측 유한성과 부모 Formation raw·weight0.245의 실제 Manager 기여를 검증했다.
- 관측108/176D·잠재124D·export284D, 부분 reset·자동 timeout/reset·frozen Actor OBB·현재 OBB 병진/회전 추적·JIT export를 확인했다.
- 기존 v0 고정 정책으로 실제 팔 속도 종료4건을 관측했다. 모든 transition에서 실제 팔 최대 절댓값 속도>1.0과 종료 boolean이 일치하고, auto reset 전 사건 비용이 정확히−3.0 또는0이며 전체 반환 보상이 term 합계와 일치함을 assert했다. 종료 조건을 강제로 바꾸지 않았다.

이 검증은 구성·종료 비용 배선 확인이며 새 정책의 성능 실험이 아니다. 새 정책의 학습·PPO 업데이트·장기 종료율·성공률·2048환경 collection 성능은 이번 작업에서 검증하지 않았다.

## 문서 검증·실행

변경 Markdown5개 수식 검사, 문서 저장소 변경4개 링크 검사(오류0개), workspace/문서 저장소 `git diff --check`를 통과했다. README의 기존 역사 링크 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락은 앞선 작업에서 확인한 기존 오류이며 이번 범위에서 수정하지 않았다. 새 README 링크2개는 기존 누락 링크와 구분해 대상·anchor를 확인했다. Markdown 실제 렌더링은 수행하지 않았다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Prof-Revision-v0_1 --num_envs 2048 --headless
```
