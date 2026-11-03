# Test-v2-GT 구현·검증

2026-11-03. [관측 계약·실행 명령](../environments/REVISION_V2_ENVIRONMENT.md#test-v2-gt-실시간-타겟-위치-대조-실험) · [부모 v2 구현](2026-11-03_revision_v2_implementation.md)

## 요청·목적·기준

사용자는 Test-v2 직접 파생인 Test-v2-GT를 요청했다. 유일한 기능 차이는 Actor에 Critic의 현재 타겟 Position을 추가하는 것이다. 초기 장애물 관측을 유지하여, 낮은 성공률에 실시간 타겟 위치 정보의 부재가 기여하는지 보상 변경 없이 비교한다.

기준 workspace HEAD는 `e27edb571cb4d22c8ceacbd1f6e829c9dd5a023b`이며 직전 Revision-v2 구현은 미커밋 상태였다. 기존 사용자 변경과 v1 임시 계측, 별도 `docs/plan/PLAN9.md`, 기존 학습 로그를 보존했다. 변경 대상4개 소스의 시작 스냅샷은 `/tmp/revision_v2_gt_before.json`에 기록했다. 기존 최상위 AST 구문은 전부 보존됐다. 결과는 `outputs/revision_v2_gt_validation/parent_ast.json`이다.

## 최종 변경 대조

| 대상 | 변경·보존 |
| --- | --- |
| Gym 등록 | `Isaac-Inspire-Revision-Test-v2-GT` 추가 |
| EnvCfg | `RevisionV2TestGTEnvCfg(RevisionV2TestEnvCfg)`, 전체 to_dict 결과는 부모와 동일 |
| Runtime·Scene | 기존 RevisionEnv·Test-v2 원통 타겟 Scene 재사용 |
| Actor 관측 그룹 | `[policy, obstacles]` → `[policy, privileged, obstacles]` |
| 실시간 정보 | 기존 `privileged.target_position`의 robot-root XYZ(m), 매 관측 갱신·noise 없음 |
| 기존 Actor 정보 | policy57D의 초기 타겟·센서 등과 초기 장애물64D 모두 유지 |
| Critic | `[policy, privileged, critic_obstacles]`, 모델·현재 장애물 관측 유지 |
| Actor 모델 | `RevisionGTModel(RevisionModel)`, 직접입력57→60D·MLP 입력73→76D |
| 네트워크 나머지 | hidden256/128/64, 장애물encoder64→32→16, activation·분포·정규화 설정 동일 |
| Runner | `RevisionV2TestGTPPORunnerCfg(RevisionV2TestPPORunnerCfg)` |
| PPO | gamma0.98·lam0.95 포함 알고리즘·학습 일정 동일 |
| 실험 식별 | experiment_name=`inspire_revision_test_v2_gt` |
| 나머지 환경 | 보상·95mm 조건·종료·reset·OSC·물리·커리큘럼·자산 전부 동일 |

`agent/revision_models.py`의 기존 RevisionModel은 Actor 관측 그룹을 엄격하게 제한한다. 이를 부모 전체에 완화하지 않고 GT 전용 파생 모델의 관측 차원 해석만 확장했다. 기존 Critic 그룹을 재사용하므로 새 관측 함수·중복 타겟 계산·Actor 속도/자세 입력·Critic 중복 위치 입력은 추가하지 않았다. 기존 장애물 encoder 및 export 경로는 차원에 따라 동작하여 그대로 재사용한다.

신규 동작은 `__init__.py`, `envs/revision_envs.py`, `agent/revision_ppo_cfg.py`, `agent/revision_models.py`에 추가했다. 기존 보상 및 관측 생성 파일은 변경하지 않았다. 직전 리뷰의 CLI 높이 override 동기화 지적도 이번 관측 대조 실험에 섞어 수정하지 않았다.

## CPU 검증

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest \
  src/inspire_sweep_baseline/tests/test_revision_v2_gt.py \
  src/inspire_sweep_baseline/tests/test_revision_observations.py \
  src/inspire_sweep_baseline/tests/test_revision_v2.py \
  src/inspire_sweep_baseline/tests/test_revision_v1.py -q
```

**33 passed (2.57s)**. `/tmp/revision_v2_gt_pytest.log`에 결과를 보존했다.

- 실제 Actor 출력의 gradient가 policy·현재 타겟XYZ·초기 장애물에 전달되고 현재 장애물에는 전달되지 않음을 검사했다.
- 현재 타겟XYZ 변경은 GT Actor 출력에 반영되며 부모 Actor 출력은 동일하다.
- 부모 Actor MLP73D, GT Actor 및 기존 Critic MLP76D를 확인했다.
- GT의124D JIT 출력과 원래 모델 출력이 같고 checkpoint save/load 후 출력이 동일하다.
- GT의 누락된 타겟 그룹·잘못된 타겟 차원·현재 장애물 오연결·잘못된 policy 차원을 거부한다.
- 기존 Revision Actor 정보 분리·Critic·보상·커리큘럼 회귀 검사를 함께 통과했다.

## 실제 GPU 환경 검증

RTX3090 / driver560.35.03, seed42, 원래 자산으로 실행했다. 시작 전 GPU 학습 프로세스가 없음을 확인했다.

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/tests/_revision_v2_gt_probe.py \
  --num_envs 64 --headless
```

**64 env·32 step·부분 reset·실제 모델 추론·JIT 비교 통과**. stdout은 `/tmp/revision_v2_gt_probe.log`, 결과는 `outputs/revision_v2_gt_validation/probe.json`이다.

실제 configclass로 부모/GT EnvCfg 전체 값이 같은 것을 확인했다. Runner 차이는 experiment_name·obs_groups.actor·actor.class_name뿐이며 Critic와 나머지 PPO 값은 같다. 부모 재생성 결과도 보존됐다.

PhysX target root를 world X로0.01m 이동시킨 후 실제 ObservationManager를 갱신했다. privileged XYZ가 즉시 바뀌고 실제 `object_position_in_root` 결과와 같았다. 초기 타겟 관측 policy[21:24] 및 초기 장애물은 그대로였다. Actor latent[57:60]이 같은 최신XYZ이며, rollout·부분 reset 이후에도 현재 상태와 일치했다. 32 step의 관측·보상·Actor/Critic 출력은 모두 유한했다. 실제GPU에서도124D JIT 결과가 원래 Actor와 일치했다.

검사 도구 초기 실행에서는 runner dict 키 순서에 의존한 비교와 RSL-RL 구형 설정 필드의 직접 전달을 보완했다. 최종 검사는 키 집합을 비교하고 train.py와 같은 `handle_deprecated_rsl_rl_cfg`를 적용한다. 이 문제를 해결하기 위해 제품 환경·모델 동작을 바꾸지는 않았다.

## PPO 학습·저장 검증

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Revision-Test-v2-GT --num_envs 64 --headless \
  --max_iterations 2 \
  --experiment_name /home/min/7cmdehdrb/grad/outputs/revision_v2_gt_training \
  --run_name smoke
```

**64 env PPO2 iterations·checkpoint 저장 통과**. run은 `outputs/revision_v2_gt_training/2026-11-03_19-28-27_smoke`이며 model_0.pt·model_1.pt를 저장했다. stdout은 `/tmp/revision_v2_gt_training.log`다. value loss0.7043→0.7449가 유한했고, 모든 모델·optimizer 저장 tensor가 유한하다.

Actor·Critic의 첫 linear weight shape는 모두256×76이다. Actor의 추가 GT 입력 열[57:60]의 weight가 iteration 사이 실제로 갱신됐다(max absolute change0.0593377). 두 장애물 encoder도 각각4개 weight/bias tensor가 갱신됐다. 저장된 agent.yaml에서 Actor 그룹 확장·Critic 그룹 보존·gamma0.98·lam0.95를 확인했다. 결과는 `outputs/revision_v2_gt_validation/checkpoints.json`이다. 기존 `logs/rsl_rl` 대신 별도 outputs 경로를 사용했다.

## 적용 범위·비교 해석

Actor 입력 차원이 달라 기존 Test-v2 체크포인트를 그대로 resume하는 경로는 지원하지 않는다. GT task로 새 학습을 시작하고 동일 seed·환경 수·학습 budget의 Test-v2와 비교한다. Critic·보상은 같지만 새로운 Actor의 입력 차원 증가에 따른 첫 linear layer의 파라미터 증가는 발생한다.

장기 성공률·최종 XY오차·정책 안정성 비교와 GUI play는 수행하지 않았다. GT 전용2048 env 실행은 이번에는 반복하지 않았으며, 동일한 부모 환경의2048 env 검증은 부모 개발 로그를 따른다. GT의 결과 개선은 관측 정보 부족이 기여했음을 뒷받침하고, 개선이 없으면 보상 외에도 최적화·제어·학습 시간 등의 원인이 남는다.


## 문서·최종 검사

변경 문서4개의 math·외부 경로 포함 링크 검사, 전체 문서455개 및 dataset 링크 검사는 오류0이다. Workspace와 문서 submodule의 diff whitespace 검사도 통과했다. README의 외부 링크 검사에는 직전 작업에서도 확인한 기존 Final-v0_2 환경 문서 누락1건이 남아 있으며, 새 GT 링크와 anchor는 정상이다. Markdown 시각 렌더링은 별도 수행하지 않았다.
