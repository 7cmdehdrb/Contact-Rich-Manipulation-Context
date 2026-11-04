# Revision-v2 / Test-v2 구현·검증

2026-11-03. [최종 개발 명세](../../01_plan/environments/2026-11-03_REVISION_V2_SPEC.md) · [구현 계약·실행](../environments/REVISION_V2_ENVIRONMENT.md)

## 요청과 기준

사용자가 최종 명세의 실제 개발과 GPU smoke를 승인했다. v1 직접 파생 v2, v2 직접 파생 Test-v2를 추가한다. 낮은 EEF에서 접근·체류·접촉하도록 보상을 제한하고, 감속한 최초 진입·최종 배치 성공을 강화하는 변경이다.

기준 workspace HEAD는 `e27edb571cb4d22c8ceacbd1f6e829c9dd5a023b`, 문서 submodule HEAD는 `5e6fb3f23f153452c4605a98672d59c4047b8e2d`다. 작업 시작 시 Test-v1 임시 높이 출력·90/95/100mm 시각화와 문서 변경이 있었으며 보존했다. 구현 전 6개 소스 파일 내용을 `/tmp/revision_v2_before.json`에 저장하고 AST를 비교했다. 기존 함수·클래스 19개와 등록 구문은 동일하다.

## 최종 변경 대조

| 구성 | v1 → v2 | 구현·영향 |
| --- | --- | --- |
| 등록·EnvCfg | 새 v2/Test-v2 ID, 직접 상속 | 기존 RevisionEnv 재사용. 부모 ID·runtime 보존 |
| 거리 | 높이 제한 없음 → EEF < 95mm | `goal_distance_v2`, 기존 거리 곡선·weight 3.7 유지 |
| Hold | Gaussian·속도 감쇠·weight 8 → Smoothstep·감쇠 없음·weight 10·EEF < 95mm | `goal_hold_v2`, 2.5~3.5cm, 기존 물리 유효성·finite velocity 유지 |
| 접촉 | EEF < 120mm → < 95mm | 기존 callable 재사용, `contact_height_limit`을 공통 `goal_reward_height_limit`에 동기화 |
| 최초 진입 | +30 → +25 × Gaussian speed damping | `FirstGoalEntryBonusV2`; free 0.01 / scale 0.02m/s, world 3D 속력, 높이 무관, latch·cache·부분 reset 상속 |
| timeout | +40 → +75 | 기존 callable·inclusive 3cm 성공 유지 |
| 가속도 | free 20 → 15m/s² | 기존 callable·weight −0.05·물체별 cap 100 유지 |
| Test Scene | 타겟 형상만 cylinder | 타겟 1·장애물 후보 9·scale·장애물 난수열 보존, 임시 디버그 기능 미포함 |
| PPO | experiment 이름만 분리 | gamma 0.98·lam 0.95 포함 나머지 동일 |

15개 보상 이름·평가 순서를 보존했다. 나머지 9개 보상의 callable·params·weight, Scene(일반 v2), Command·Event·Observation·Action·Termination·Curriculum·runtime·물리 dt는 부모와 같다. 부모 post-init이 Hold params를 Gaussian용으로 다시 지정하는 문제는 v2 post-init의 최종 교체로 처리했다. 거리·Hold 높이 비교는 기존 접촉과 동일한 world-Z ceiling 비교를 사용하여 부동소수점 뺄셈 때문에 정확한 경계의 결과가 달라지지 않게 했다.

구현 위치는 기존 역할별 6개 소스 파일이다. 신규 CPU 검사 `tests/test_revision_v2.py`, GPU 검사 `tests/_revision_v2_probe.py`를 추가하고 기존 접촉 검사에 `--revision-v2` 선택지를 추가했다. 기존 접촉 검사의 기본 v0 실행 경로는 유지한다.

## 실행한 검증

GPU는 RTX 3090 / driver 560.35.03이다. 샌드박스 내부 NVML 접근은 실패했으나 권한 있는 실행에서 장치 정상 확인 후 GPU 검증을 실행했다. 테스트는 원래 자산과 실제 CUDA/PhysX를 사용한다.

### CPU·설정·부모 보존

다음 명령은 86 passed (14.18s)다.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest \
  src/inspire_sweep_baseline/tests/test_revision_v2.py \
  src/inspire_sweep_baseline/tests/test_revision_v1.py \
  src/inspire_sweep_baseline/tests/test_revision_cfg.py \
  src/inspire_sweep_baseline/tests/test_revision_layout.py \
  src/inspire_sweep_baseline/tests/test_revision_observations.py \
  src/inspire_sweep_baseline/tests/test_final_configuration.py \
  src/inspire_sweep_baseline/tests/test_final_versions.py -q
```

- 거리·Hold·접촉 모두 94.9/95/95.1mm, NaN/Inf, 환경별 원점 차이, 접촉 없음·stale·NaN force를 검사했다.
- Hold의 2.5/3/3.5cm 값과 연결점 기울기, 물리 mask, 속력 크기 독립성을 검사했다. 실제 `target_measurements`를 호출하여 finite speed5m/s에서는 감쇠 없음, NaN/Inf 속도·비활성 타겟·선반 XY 이탈·바닥 높이 이탈·기울기·비유한 목표에서는0을 확인했다.
- 최초 진입의 3D 속력·Gaussian 값·strict 3cm 경계·cache·재진입·비유한 속도·전체/부분 reset을 검사했다. dt 0.01/0.02/0.1에서 지급액이 같다.
- 가속도 15m/s² 경계·cap·활성 물체 합산·초기화 후 첫 표본 억제를 검사했다. 초기 검사에서 경계 근처 float32 fixture의 허용오차가 너무 엄격하여 실패했고, 수학적 기대값 검사 입력을 float64로 고쳐 통과했다. 제품 코드 변경 사유는 아니었다.
- 실제 Isaac configclass로 전체 CFG를 비교했다. v1→v2 차이는 공통 높이 설정·위 5개 Reward CFG override이며 접촉은 높이 설정 차이로 적용된다. v2→Test 차이는 타겟 kind_override 하나다. PPO 차이는 experiment_name 하나다.
- 기존 정의 AST 보존 결과는 `outputs/revision_v2_validation/parent_ast_preservation.json`에 저장했다. 회귀 검사와 실제 부모 CFG 재생성 결과도 동일하다.

### GPU 환경·리셋·이벤트

아래 명령은 Workspace 루트에서 실행한다. 로그는 `/tmp/revision_v2_probe64.log`, `/tmp/revision_v2_test_probe64.log`, `/tmp/revision_v2_probe2048.log`에 기록한다.

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/tests/_revision_v2_probe.py --num_envs 64 --headless

env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/tests/_revision_v2_probe.py --test-variant --num_envs 64 --headless

env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/tests/_revision_v2_probe.py --num_envs 2048 --headless
```

64 env v2/Test-v2 통과. 각 환경에서 sparse/dense 32 step씩 유한 관측·보상, 전체/부분 reset, 장애물 일정 경계·rewind, 고정 패널티 수치를 확인했다. 같은 seed42에서 Test의 scale·장애물 종류가 일반 v2와 정확히 같았다. 실제 env.step의 자동 reset 직전 이벤트는 최초 진입 `[25,0,0]`, timeout `[75,75,0]`이며 고속 실패·종료 시 latch reset을 확인했다. 이벤트 fixture는 physics 이후 목표를 현재 타겟에 정렬하여 보상·종료 순서를 검사하는 통제 조건이다.

2,048 env에서도 같은 초기화·sparse/dense 총64 step·일정 전환·부분 reset·이벤트 lifecycle 검사가 통과했다. 관측·보상은 모두 유한했으며 PhysX capacity 오류가 없었다. 결과 JSON·spawn NPZ는 `outputs/revision_v2_validation`에 저장했다.

### 실제 EEF·접촉·Hold 지급액

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/tests/_revision_contact_probe.py \
  --revision-v2 --num_envs 4 --headless \
  --output outputs/revision_v2_validation/contact_physics.json
```

통과, `/tmp/revision_v2_contact.log`에 실행 로그를 남겼다. 로봇 base를 옮기지 않고 실제 PhysX Jacobian IK로 EEF를 이동했다. FrameTransformer 측정값 94.8998~94.9001mm에서 grounded target의 거리·Hold raw=1, 95.0996~95.1002mm에서 raw=0이었다. 정확히95mm의 strict 경계는 CPU 검사로 별도 확인했다.

실제 RewardManager에서 Hold step 보상은 d=0에서 약0.20, d=0.03m에서 약0.1000009, d=0.035m에서 0~2.4e−8이었다. 마지막 미소값은 world 좌표 float32 덧셈에 따른 거리 오차이며 허용오차1e−5 안이다.

실제 센서 force가0.01N 이상인 접촉 표본 중 EEF87.16~89.23mm의20개 표본은 raw1, EEF100.46~103.57mm의8개 표본은 raw0이었다. 잘못된 gate 표본0개, robot root 보존을 확인했다. 낮은 표본은 정상 바닥 정렬 타겟, 높은 표본은 높이 gate를 분리하기 위한 중력 해제 공중 타겟이다. 이 검사는 손과 타겟을 통제 배치한 물리 검증이다.

### PPO 학습·체크포인트

기존 `logs/rsl_rl` 대신 절대 experiment 경로를 지정했다. 실제 `train.py`로 다음 두 명령을 실행했다.

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Revision-v2 --num_envs 2048 --headless \
  --max_iterations 2 \
  --experiment_name /home/min/7cmdehdrb/grad/outputs/revision_v2_training \
  --run_name smoke

env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Revision-Test-v2 --num_envs 64 --headless \
  --max_iterations 2 \
  --experiment_name /home/min/7cmdehdrb/grad/outputs/revision_v2_test_training \
  --run_name smoke
```

v2 2048 env PPO2 iterations 통과. run은 `outputs/revision_v2_training/2026-11-03_19-16-28_smoke`이며 `model_0.pt`, `model_1.pt`를 저장했다. value loss0.4798→0.5341, surrogate loss−0.0033→−0.0045로 유한했다. actor·critic·optimizer의 저장 tensor가 모두 유한하고, 두 obstacle encoder의 weight/bias가 iteration 사이에 실제 갱신됨을 확인했다. 저장된 agent.yaml은 gamma0.98·lam0.95·seed42·36step/env이며, env.yaml은 공통높이0.095·Hold0.025/0.035·free acceleration15다.

Test-v2 64 env도 PPO2 iterations 통과. run은 `outputs/revision_v2_test_training/2026-11-03_19-18-46_smoke`이며 같은 두 checkpoint를 저장했다. value loss0.3933→0.6251, surrogate loss−0.0170→−0.0205로 유한했고 모델·optimizer 유한성, 두 encoder 갱신, gamma/lam 보존을 확인했다. 체크포인트 검사는 `outputs/revision_v2_validation/checkpoints.json`, stdout은 `/tmp/revision_v2_training.log`와 `/tmp/revision_v2_test_training.log`에 기록한다.

### 문서·최종 대조

변경 문서5개의 math 검사와 외부 경로를 포함한 링크 검사, 문서 저장소 전체454개 Markdown 및 dataset 링크 검사는 오류0이었다. package README까지 외부 링크를 검사하면 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 링크 누락1건이 검출된다. 이 링크는 작업 전에도 존재하던 별도 환경 설명이며 이번에 추가한 v2 링크는 정상이다. Workspace와 문서 submodule의 `git diff --check`도 통과했다. Markdown 렌더링은 별도 실행하지 않았다.

## 한계와 후속 평가

검증은 코드 계약·실행 가능성에 관한 것이다. 장기 학습 성공률, 물체 상부 누르기 감소, 최종 XY 정밀도 향상은 아직 평가하지 않았다. GUI play도 실행하지 않았다. 실제 접촉 검사는 IK로 손을 배치하고 타겟을 접촉 위치로 옮기는 통제 fixture이며, 정상 초기 배치에서 학습된 정책이 그 동작을 수행했다는 의미는 아니다.

기존 학습 로그를 정리하지 않았고 `logs/rsl_rl`을 변경하지 않았다. 검증 산출물은 `outputs/revision_v2_validation`과 별도 smoke 학습 폴더에 보존한다.


## 2026-11-03 구현 후 코드 리뷰

사용자의 코드 리뷰 요청에 따라 `code-review` 스킬의 Standards·Spec 두 축을 독립적으로 검토했다. 기준은 HEAD `e27edb571cb4d22c8ceacbd1f6e829c9dd5a023b`의 작업트리 차이와 신규 검사 파일이다. Test-v1의 기존 임시 계측은 `/tmp/revision_v2_before.json` 스냅샷으로 분리했다. 제품 코드 변경 없이 리뷰 결과만 기록한다.

### Standards: 지적0건

개발 지침의 역할별 파일 배치·지정 부모 직접 상속·부모 정의 보존·범위 제한을 확인했다. 기존 정의19개의 AST는 구현 전과 같고, 기존 등록도 보존됐다. 문서·검증 기록을 포함하여 수정이 필요한 규칙 위반이나 코드 냄새는 발견하지 못했다.

### Spec: P2 지적1건 — 공통 높이의 CLI override 동기화

`envs/revision_envs.py:102`의 `self.contact_height_limit = self.goal_reward_height_limit`은 post-init에서 한 번만 실행된다. 정상 train/play 경로의 `IsaacLab/source/isaaclab_tasks/isaaclab_tasks/utils/hydra.py:92`는 그 이후 `env_cfg.from_dict(...)`로 CLI 설정을 적용한다. 실제 업데이트 함수는 post-init을 재실행하지 않는다.

명세3.1절은 “거리와 Hold는 같은 goal_reward_height_limit을 읽고, 접촉 높이도 이 값으로 동기화한다”라고 정의한다. 하지만 `env.goal_reward_height_limit=0.09`만 CLI에 지정하면 거리·Hold는90mm, 접촉은95mm를 사용한다. EEF92mm의 실제 접촉은 거리·Hold와 다른 높이 기준으로 지급된다. 기본95mm 설정에는 영향이 없으며, 공통 높이 설정을 override하는 경우 발생한다.

CPU 재현에서는 실제 V2 클래스 AST와 IsaacLab의 `from_dict`/업데이트 함수를 사용하고 부모·reward 객체만 stub으로 대체했다. 아래 업데이트 전후 결과는 `(0.095, 0.095)` → `(0.09, 0.095)`다.

```python
cfg = RevisionV2EnvCfg()
cfg.from_dict({"goal_reward_height_limit": 0.09})
print(cfg.goal_reward_height_limit, cfg.contact_height_limit)
# 0.09 0.095
```

권장 수정은 Hydra override 이후 환경 생성 단계에서 두 설정을 동기화하거나 v2 접촉 항이 공통 값을 직접 읽게 하는 것이다. 기존 v1의 동작은 보존해야 한다. 리뷰 요청 범위에서는 수정하지 않았다.

### 기본 설정 대조·검증

기본95mm에서 세 항의 strict gate, Smoothstep 반경·weight10·속도 감쇠 제거·물리 유효성 보존, 최초 진입25×Gaussian·높이 독립·기회 소진·cache/reset, timeout75, 가속도 free15가 명세와 일치한다. Test 타겟 cylinder, 직접 상속, 나머지 보상·커리큘럼·PPO 보존도 확인했다. 추가 신규 결함은 발견하지 못했다.

앞서 기록한 동일 CPU 명령을 재실행하여 **86 passed (13.11s)**를 확인했다(`/tmp/revision_v2_review_pytest.log`). GPU 검증은 추가 실행 없이 기존64/2048 env·접촉 fixture·두 PPO run의 JSON 산출물을 재검토했다. 기본 설정만 검증하는 기존 검사에서는 위 CLI override 누락이 검출되지 않는다. 장기 정책 성능은 이번 리뷰의 검증 범위가 아니다.


## 2026-11-04 Test-v2 임시 종료 원인 출력

사용자는 `Isaac-Inspire-Revision-Test-v2` play 중 어떤 종료 조건이 발동하는지 확인하기 위해, 곧 주석 처리할 print를 요청했다. 기준 workspace commit은 `ba1aa88`이며 기존 문서 submodule의 수정·미추적 파일은 보존했다.

`runtime/revision.py:RevisionEnv._reset_idx` 시작 부분에 TEMP 블록을 추가했다. 변경 전에는 종료 원인 콘솔 출력이 없었고, 변경 후에는 `RevisionV2TestEnvCfg` 정확한 타입 이름에만 적용하여 reset 직전 TerminationManager의 활성 term 결과를 읽고 env ID·episode step·발동한 모든 term 이름을 flush 출력한다. 초기 reset에서 발동 조건이 없으면 출력하지 않는다. Test-v2-GT 및 부모 버전에는 출력하지 않는다. TEMP 시작부터 END 주석 사이를 주석 처리하여 제거할 수 있다.

최종 대조: runtime의 출력 블록만 추가했다. 등록·상속·PPO·Scene·Command·Event·관측·행동·보상·종료 callable/params·커리큘럼·기존 reset 및 metrics는 그대로다. 종료 조건을 다시 계산하지 않고 저장된 결과만 조회한다. Test-v2 학습에도 같은 출력이 적용되므로 다중 환경에서는 출력량과 CPU/GPU 동기화 비용이 늘 수 있다. `logs/rsl_rl` 및 checkpoint는 수정하지 않았다.

검증: Python compile 구문 검사 및 `git diff --check` 통과. 로컬 Isaac Lab에서 `termination_manager.compute()` 이후 `_reset_idx`가 호출되고 `active_terms`/`get_term` API가 존재함을 소스로 확인했다. 실제 Isaac Sim play·GPU 실행 및 checkpoint 재생은 실행하지 않았으며 출력 발생 장면은 미검증이다.

재현은 사용자의 기존 명령으로 프로세스를 다시 시작한다.

```bash
python src/inspire_sweep_baseline/scripts/play.py --task Isaac-Inspire-Revision-Test-v2 --checkpoint /home/min/7cmdehdrb/grad/logs/TEMP/2026-11-03_19-32-13/model_17200.pt --num_envs 1
```


### 2026-11-04 후속: 매 step 실패 상태·조건 출력

사용자가 play에서 주된 종료 원인으로 `shelf_failure`와 `object_fall_or_tilt`를 확인하여 매 step의 현재 상태와 판정 조건을 요청했다. 두 term의 실제 함수인 `mdp/termination_functions/final.py:shelf_termination`과 `revision.py:any_active_object_fall_or_tilt`에 정확히 `RevisionV2TestEnvCfg`일 때만 실행되는 TEMP 블록을 추가했다. 이전 종료 시점 요약 출력은 유지한다.

변경 전에는 종료 시 term 이름만 출력했다. 변경 후에는 매 제어 step(기본 0.02s), termination 계산 중 reset 전에 다음 값을 출력한다.

- 선반: 선형·각속도 전체 6D norm > threshold(기본0.1), 손목 world Z에서 선반 root Z+1.05m를 뺀 clearance < 0.03m, default root position+env origin 대비 이동 거리 > 0.05m. 각 실제 인자와 비교 결과·최종 OR 결과를 출력한다. `check_fingers=False`도 표시하며 True일 경우 두 손가락 clearance와 0.01m 판정을 출력한다. 6D norm은 순수 선속력이 아니므로 m/s라고 표시하지 않는다.
- 물체: 활성 slot ID·target 여부, 현재 선반 좌표계 bbox 최저점 < 1.04m(1.05−bottom_clearance), 최저점 비유한 여부, 선반 법선 기준 tilt >= 0.9rad, 개별 실패·전체 실패 결과. 비활성 물체는 실제 종료 대상이 아니므로 출력에서 제외한다.

각 출력에 env ID·episode step이 포함되며 종료 step도 reset 전에 출력한다. 기본 physics substep 0.01s마다가 아니라 termination을 평가하는 제어 step마다 출력한다. TEMP 블록을 주석 처리하면 해당 출력이 비활성화된다. 대량 콘솔 출력과 GPU 동기화로 play 속도가 느려질 수 있다.

최종 대조: 기존 종료 식·임계값·반환값·환경 설정·보상·커리큘럼·등록·상속·PPO·reset은 보존했다. Test-v2-GT 및 다른 환경은 추가 계산·출력을 수행하지 않는다. 작업트리의 선행 출력과 기존 문서 변경을 보존했고 학습 로그는 수정하지 않았다.

검증: 두 Python 파일 compile 통과. TEMP 블록을 제외한 AST가 HEAD의 원본과 동일함을 확인했다. `git diff --check` 통과. 실제 Isaac Sim play/GPU 출력·재생은 실행하지 않았으므로 물리 실행은 미검증이다. 기존 사용자 명령으로 play를 재시작하여 확인한다.


### 2026-11-04 직접 play 재현·종료 원인 진단

사용자의 요청에 따라 `env_isaaclab` conda에서 아래 명령을 직접 실행했다. 기존 임시 계측을 사용했으며 이 진단에서는 소스·종료 임계값을 추가 변경하지 않았다. 진단 스킬의 수정·회귀 단계는 요청 범위가 원인 파악이므로 수행하지 않았다. 초기 샌드박스 실행은 CUDA 장치 접근 및 Isaac Sim 캐시 쓰기 제한으로 실패했고, 권한 확장 실행은 CUDA:0·GUI·seed42로 실제 checkpoint load 및 rollout에 성공했다. headless 옵션이나 다른 seed는 추가하지 않았다.

```bash
conda run --no-capture-output -n env_isaaclab python src/inspire_sweep_baseline/scripts/play.py --task Isaac-Inspire-Revision-Test-v2 --checkpoint /home/min/7cmdehdrb/grad/logs/TEMP/2026-11-03_19-32-13/model_17200.pt --num_envs 1 > outputs/revision_termination_diagnosis/play_gpu.log 2>&1
```

Workspace 상대 경로 `outputs/revision_termination_diagnosis/play_gpu.log`에 stdout/stderr 원본을 저장했고, `summary.json`에 종료 line 번호·각 에피소드 마지막 두 step·조건별 수치·집계를 저장했다. 최초 실패 실행 로그는 같은 폴더의 `play.log`다. 에피소드12개 종료 후 다음 에피소드159step까지 수집하고 SIGINT로 실행을 중단했으므로 종료 코드는1이며 마지막 `CondaError: KeyboardInterrupt`는 의도한 중단이다. 중간 에피소드는 집계에서 제외한다.

| 관측 종료 | 횟수 | 직접 판정 원인 |
| --- | --- | --- |
| shelf_failure | 9/12 | 모두 wrist clearance < 0.03m |
| object_fall_or_tilt | 2/12 | 비타겟 장애물 tilt1건, bbox bottom 하한1건 |
| target_goal_miss_at_timeout | 1/12 | 500step/10초 도달 시 목표 미달 |

선반 종료는 모두18~20step(0.36~0.40초)에 발생했다. 종료 시 wrist clearance는21.470~29.764mm로30mm 하한을 넘었고, 선반6D 속도 norm은0.000232~0.076642로0.1 이하, 이동량은0.003~0.197mm로50mm 이하였다. 따라서 이번9건은 선반 흔들림·이동으로 종료한 것이 아니라 손목 frame 높이 보호 조건이 발동한 것이다. 첫 사례는 step18의40.824mm에서 step19의26.150mm로 내려갔다(원본 log line696/706/707). 이 wrist frame은 `assets/scenes/revision.py`의 `inspire_base_link` 로컬 offset(0,0,-0.17) 지점이며 EEF 높이와는 다른 측정점이다. 현재 shelf predicate는 XY 위치 검사나 실제 접촉력 조건 없이 해당 world Z와 shelf root Z+1.05m만 비교한다.

물체 종료 첫 사례(episode9, step56,1.12초)는 object1(target=False)의 선반 법선 기준 기울기가0.866040→1.076806rad(약61.70도)로0.9rad(약51.57도)를 넘었다. 바닥 높이는1.048450m로1.04m 이상이며 낙하 조건은 False였다. 원본 line8721/8733/8743이다.

두 번째 사례(episode11, step15,0.30초)는 object2(target=False)의 선반 좌표 bbox 최저점이1.042768→1.035490m로1.04m 미만이 됐다. tilt는0.235484→0.560678rad(약32.13도)로0.9rad 미만이었다. 선반 상판 기준 bbox 최저점이14.510mm 아래에 놓인 상태다. 원본 line9132/9144/9153이다. 두 사례 모두 타겟 object0의 실패 조건은 False였다.

해석 한계: bbox는 8개 경계점의 최저점이며 실제 collider 최저점·물체 중심 높이와 동일하지 않다. 따라서 두 번째 사례는 코드상 bottom 조건 발동을 입증하지만 실제 물체가 선반 밖으로 추락했는지, bbox와 collision 형상의 차이인지, 접촉/관통인지까지 이 로그만으로 확정할 수 없다. 정책이 손목을 낮추거나 장애물을 기울이게 된 학습 원인, 접촉한 로봇 부위, 장기 실패율은 조사하지 않았다. 단일 seed의12개 에피소드 관측 빈도를 전체 정책 성능으로 일반화하지 않는다.

검증: 원본 로그를 파싱하여 종료12건·선반9건 모두 wrist만 True·물체2건 해당 객체별 실패를 확인하고 마지막 두 step을 JSON으로 보존했다. 기존 `play.py`는 checkpoint 옆 `exported/policy.pt`와 `policy.onnx`를 자동 생성/갱신하는 경로를 포함한다. `logs/rsl_rl` 정리나 수정은 수행하지 않았다. 사용자 요청의 기존 임시 계측은 유지했다.
