# Prof Revision v1 구현·검증

작성일: 2026-11-24. **구현·Gym 등록·CPU 검사·GPU smoke·PPO1회 업데이트 완료. 장기 행동 개선은 미검증.**

## 요청·기준·의도

사용자는 [확정 개발 명세](../../01_plan/environments/2026-11-24_PROF_REVISION_V1_SPEC.md)에 따른 새 환경 구현을 요청했다. Prof Revision v0를 직접 상속하고, 누락된 팔 속도 종료 사건 비용을 복원하며 손가락 거리만 줄이는 자세를 방향 점수와 함께 평가한다. 기존 부모 직접 수정 요청으로 해석하지 않았다.

기준 workspace commit `19cac187345419cc08be097d7148052ddf3e383b`, 문서 저장소 commit `33858ea1086f22f1154eb799d934475af5de589f`. 시작 시 소스 변경은 없었고 사용자 변경 `docs/SSH.md`, 문서 submodule 상태 및 앞선 진단·명세 문서를 보존했다. 소스 변경 전 SHA256은 [before_hashes.json](../../../../outputs/prof_revision_v1_validation/before_hashes.json)에 저장했다. 기존 `logs/rsl_rl`을 변경·정리하지 않았고 검증 학습 산출물도 `outputs/`에 저장했다.

## 구현과 최종 대조

| 역할 | 실제 구현 |
| --- | --- |
| Gym ID | `Inspire-Sweep-Prof-Revision-v1` |
| EnvCfg | `ProfRevisionV1EnvCfg(ProfRevisionEnvCfg)` |
| Runtime | 기존 `ProfRevisionEnv` 재사용 |
| Rewards Cfg | `ProfRevisionV1RewardsCfg(ProfRevisionRewardsCfg)` |
| PPO | `ProfRevisionV1PPORunnerCfg(ProfRevisionPPORunnerCfg)` |
| PPO 유일한 차이 | `experiment_name=inspire_sweep_prof_revision_v1` |

파일은 현재 역할별 위치를 유지했다. `envs/prof_revision_envs.py`, `mdp/rewards/prof_revision.py`, `agent/prof_revision_ppo_cfg.py`에 자식을 추가하고 패키지 `__init__.py`에 등록했다. `mdp/common/prof_revision_geometry.py`에 순수 배치 helper `distance_angle_formation`과 v1 선택 분기를 추가했다. 기존 runtime/state/model·관측·Action·Termination 파일은 변경하지 않았다. `scripts/check_prof_revision.py`에 v1 검증 선택지를 추가하고 기존 계열 테스트 파일을 확장했다.

| 변경 항목 | 부모 v0 | v1 |
| --- | --- | --- |
| 팔 종료 사건 비용 | 없음 | 기존 `arm_joint_failure` callable, weight−3.0, 실제 사건당−3.0 |
| Formation raw | `0.05/(0.05+sum(d_i))` | `sum(0.05/(0.05+d_i) * cos(theta_i)^2)` |
| Formation weight | 0.245 | 0.3675 |
| Formation 범위/최대 step 기여 | 0–1 / 0.0049 | 0–5 / 0.03675 |
| 전용 선택 field | 없음 | `formation_mode='distance_angle_sum'` |
| reward term 수 | 16 | 17, 기존 상대 순서 유지·새 사건 비용 마지막 |

거리와 방향은 같은 손가락끼리 먼저 곱한다. Normal은 기존 패드 local +Z를 현재 패드→EEF 회전으로 변환하고, 방향은 각 패드에서 현재 추적 가시 OBB 중심으로 향하는 벡터를 EEF 좌표계로 변환한다. EEF 원점 방향·고정 Actor OBB·물체 COM을 사용하지 않는다. full3D 코사인을 [-1,1]로 clip 후 제곱하여 지문/손등을 동일하게 인정한다. Normal 또는 방향 norm이1e−8 이하이면 각도 점수0으로 처리한다. helper는 raw 합과 개별 거리·각도·곱을 반환하므로 진단에서 각 성분을 확인할 수 있다.

팔 종료 사건은 이미 계산된 `arm_joint_velocity` boolean을 읽으며 callable의 dt 나눗셈과 RewardManager dt가 상쇄된다. 기존 속도 판정1.0rad/s 초과·연속 관절 속도 비용−0.03/cap100은 보존한다. 새로운 힘·접촉·진행 gate나 감싸기 분산항은 넣지 않았다. 합산과 weight 증가로 전체 이론적 최대가 부모의7.5배임을 유지했다.

실제 config 인스턴스 전체 `to_dict()` 대조에서 v1 선택 field·Formation weight·추가 사건 term을 제외하면 부모와 동일했다. PPO는 experiment_name을 제외하고 동일했다. Reach5cm v0는 Reach 반경0.05를 부모0.10으로 되돌렸을 때 전체 config가 부모와 동일했다. 따라서 관측108/176D·Reach10cm·목표 성공3cm·면 선호·모든 나머지 reward/termination/curriculum·Scene/reset·제어·물리·PPO를 보존한다.

[AST/해시 audit](../../../../outputs/prof_revision_v1_validation/audit.json)은 기존 production 정의10개와 기존 Gym 등록9개를 보존했음을 확인했다. 공유 `update_geometry`는 마지막 선택 분기 이전의 기존 계산이 동일하고, else의 기존 Formation 식도 AST가 동일했다. 이 검사는 변경된5개 production 파일을 대상으로 하며 나머지 소스는 변경 전 해시와 같다. 테스트·검증 스크립트·README는 허용된 별도 변경이다. audit 재현 스크립트는 [audit.py](../../../../outputs/prof_revision_v1_validation/audit.py)다.

## CPU 검사

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q \
  src/inspire_sweep_baseline/tests/test_prof_revision.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact_v1.py
```

**58 passed**, ONNX export 기존 deprecation warning1개. [원본 출력](../../../../outputs/prof_revision_v1_validation/cpu_tests.log).

새 수식의0/45/90/135/180도 값, Normal 반전·스케일 불변성, 거리와 방향의 손가락별 결합, 퇴화 벡터·raw 최대5·step 최대0.03675를 확인했다. 실제 기하 갱신 함수를 사용해 pad 원점·현재 중심·3D/EEF frame·공통 강체 변환·부분 reset을 확인했다. 기존 부모 기하/관측·OBB·PPO/export 및 Single Contact v1 회귀 검사도 통과했다. 기존 사건 함수를 dt0.01/0.02/0.05에서 읽어−3.0 불변성을 검증했다.

최초 실행은 프로젝트와 무관한 ROS pytest plugin이 자동 로드되며 `lark` 모듈 부재로 collection 전에 중단됐다. 환경을 설치·변경하지 않고 위 명령처럼 plugin 자동 로드만 비활성화하여 실제 프로젝트 검사를 완료했다.

## GPU·Isaac Sim 검증

RTX3090, 원래 Scene 자산 사용, seed42, 4개 환경. 다음 명령이 exit0으로 완료됐다.

```bash
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/check_prof_revision.py \
  --task Inspire-Sweep-Prof-Revision-v1 --num-envs 4 --headless \
  --checkpoint logs/TEMP/2026-11-24/inspire_sweep_prof_revision_v0/2026-11-24_00-27-46/model_6100.pt \
  --output outputs/prof_revision_v1_validation/smoke.json
```

검증 결과:

- 실제 Manager17개 활성 term·term 순서·전체 config/PPO 대조 통과.
- 12step zero-action 검증에서 유한 관측/보상, world 좌표계로 별도 재구성한 Formation과 EEF 계산의 일치, Formation 실제 가중치와 dt 기여 및 전체 reward 합계 확인.
- 관측108/176D·잠재124D·export284D, 현재 손 관절/손끝 Pose·quaternion, frozen Actor OBB·물체 병진/회전에 따른 가시 OBB 추적 확인.
- 부분 reset의 다른 환경 보존·자동 timeout/reset·접촉 이력 초기화·Actor/Critic JIT export 확인.
- v0 고정 정책을 로드하여 실제 팔 속도 종료4건을 관측했다. reward 계산을 auto reset 전에 capture하여 모든 transition에서 실제 팔 최대 절댓값 속도>1.0과 종료 boolean의 일치, 실제 사건 비용−3.0 또는0, 반환 reward와 term 합계 일치를 assert했다. 종료 조건을 완화하거나 강제 true로 바꾸지 않았다.

이 고정 정책 실험은 새 보상 배선 검증이며 v1 정책의 행동·종료율·성공률 측정이 아니다. 단기 zero-action 구간의 손가락별 `D_i`, `A_i`, `D_i A_i`도 결과 JSON에 기록했다. [결과 JSON](../../../../outputs/prof_revision_v1_validation/smoke.json) · [실행 로그](../../../../outputs/prof_revision_v1_validation/smoke.log).

## train.py PPO smoke

기존 학습 로그와 분리하기 위해 이미 제공되는 출력 경로 옵션을 사용했다. 학습 코드나 하이퍼파라미터를 수정하지 않고 새 초기값·16환경×36step·PPO1회로 제한했다.

```bash
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Prof-Revision-v1 --num_envs 16 --headless \
  --max_iterations 1 --logger tensorboard \
  --resilient-attempt-dir outputs/prof_revision_v1_validation/ppo_smoke \
  --resilient-target-iterations 1
```

exit0, status completed, checkpoint `model_0.pt` 생성. value loss3.2591·surrogate loss−0.0405·entropy17.0130, collection4.796s·learning0.494s를 기록했다. 이는 **16환경의 단일 iteration 시간**으로2048환경 성능을 뜻하지 않는다. checkpoint의 model/optimizer 등132개 tensor와 TensorBoard scalar76개 tag가 유한하며 optimizer step32를 확인했다. [PPO 검사 JSON](../../../../outputs/prof_revision_v1_validation/ppo_check.json) · [학습 상태](../../../../outputs/prof_revision_v1_validation/ppo_smoke/training_status.json) · [실행 로그](../../../../outputs/prof_revision_v1_validation/ppo_smoke.log).

## 문서·최종 검증·미검증 범위

패키지 README·부모 환경 계약의v1절·개발 명세 상태·현재 인계·활성 환경 안내·기존 명세 작성 로그의 후속 링크를 갱신했다. 순수 명세 작성 당시의 미구현 기록은 날짜별 이력으로 보존했다.

최종 검사: 변경 Markdown7개 수식 검사 통과, 문서 저장소의 변경6개 링크 오류0개. README 전체 검사에서는 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1개를 발견했으며, 기준 commit의 README에도 같은 링크가 있어 이번 작업의 새 오류와 구분했다. 새 README 링크2개의 대상·anchor는 유효하다. 기존 역사 링크는 요청 범위 밖이므로 변경하지 않았다. 변경 Python7개 `py_compile`, AST/해시 audit, workspace와 문서 저장소의 `git diff --check`도 통과했다.

장기 학습의 목표 진입/체류·방향별 손가락 자세·실제 접촉 면·속도 종료율·성공률·보상 비중과2048환경 collection32회 기준은 미검증이다. 이번 정적/단기 검증으로 감싸기 안정성이나 종료 악용 해소를 주장하지 않는다. Markdown 실제 렌더링과 실물 실험도 수행하지 않았다. 검증용 단기 checkpoint는 정상 학습 완료 모델이 아니다.

정상 학습 실행:

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Prof-Revision-v1 --num_envs 2048 --headless
```
