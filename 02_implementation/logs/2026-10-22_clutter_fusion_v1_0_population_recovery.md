# Fusion v1.0 수정 — 장애물 개수·Goal 접촉 감쇠·자동 학습 복구

후속 변경: 가속도 입력은 [PhysX 직접 가속도](2026-10-22_clutter_fusion_v1_0_native_acceleration.md)로 교체했다. 아래 속도 차분 설명은 이 로그 작성 시점의 구현이다. 상한·커리큘럼은 유지한다.

[개발 로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [최초 v1.0 구현](2026-10-22_clutter_fusion_v1_0.md)

기준일: 2026-10-22. 사용자 후속 요청으로 기존 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0`을 수정했다. 새 task ID는 추가하지 않는다. Workspace 기준 HEAD `a2fcb0b77a234a14db8b6fc9c91cfef4c4229092`, 문서 submodule `f5655d0f9897708635edbe62b086994cfe5ac46d`, Isaac Lab `929f0fe1e9c1699efebf31b2ad0ab723a7d6e7e9`에서 시작했다. 앞선 v1.0 구현과 사용자 telemetry·문서·PLAN 변경은 작업트리에 보존하며, 기존 학습 로그·checkpoint를 삭제하거나 덮어쓰지 않았다.

## 가속도와 접촉 유지

사용자는 추가 질의에서 **기존 가속도 지수 비용을 유지하고 가속·감속의 대칭성을 확인**하도록 명확히 했다. 기존 `norm(v_current - v_previous) / step_dt`는 음의 속도 변화도 양의 크기로 평가한다. 같은 크기의 가속·감속 비용이 같고 방향 변화도 포함됨을 회귀 검사한다. 무료 임계값0.3→0.05 m/s² 일정과 물체별 지수 비용·cap100·weight−1을 유지한다. 비활성 슬롯의 비용·history는 제외한다.

손 접촉 보상의 raw rate는 아래와 같다. d는 타겟과 Goal의 월드 XY 거리, r은 현재 RewardManager의 `goal_hold.params.position_tolerance`다.

```text
alpha = clamp((d - r) / 0.03, 0, 1)
reward_rate = 0.29 * alpha * (whole_hand_net_force >= 0.01 N)
```

따라서 d≤r이면0, d=r+1.5cm이면0.5, d≥r+3cm이면1이다. 실제 지급에는 RewardManager가 step_dt를 한 번 곱한다. r을 복사한 별도 설정이나 접촉용 tolerance 커리큘럼을 두지 않고 매 호출에서 live Goal hold 설정을 읽는다. 1000 iteration의0.05→0.04m, 2500의0.01m 및 checkpoint rewind가 즉시 함께 적용된다. Goal progress의 별도 tolerance와 혼동하지 않는다.

기존 weight0.29는 유지하지만 이제 5초 접촉 시 +1.45는 alpha=1인 경우의 상한이다. 목표 근처에서는 그보다 작다. 최초 v1.0의 참조 로그10.04% 보정은 새 정책에서의 보상 비중을 보장하지 않는다.

## 장애물 개수와 스폰

| Learning iteration | Gray | White | 타겟 포함 실제 활성 물체 |
| --- | --- | --- | --- |
| 0~2999 | 1 | 1 | 3 |
| 3000~4499 | 1 | 2 | 4 |
| 4500~5999 | 2 | 2 | 5 |
| 6000~7499 | 2 | 3 | 6 |
| 7500 이후 | 3 | 3 | 7 |

`obstacle_population_schedule`은 현재 iteration으로 다음 reset의 Gray/White 수를 재계산한다. 진행 중 episode의 물체는 바꾸지 않는다. 부분 reset에서는 해당 환경만 새 단계로 전환한다. 7500에서2500으로 되돌리면 다음 reset은 Gray1/White1이 된다. 전체 활성 curriculum term은 기존8개에서 **9개**이며, 두 개수 일정을 하나의 population term이 관리한다.

Scene에는 최대 capacity만큼 cylinder와 센서를 미리 만든다. 기본 최대는 Gray3+White3이며, 이름 순서는 target `mass_cylinder`, Gray용 `obstacle_0..2`, White용 `obstacle_3..5`다. `_active_object_mask`가 환경별 episode의 실제 멤버십이다. 아직 쓰지 않는 물체는 선반 로컬 Z=100m에 서로 떨어뜨려 주차하고 속도를0으로 초기화하며 PhysX 중력을 끈다. 물체가 늘어나면 정해진 Gray/White 슬롯을 선반에 배치하고 중력을 켜서 깨운다. PhysX actor 자체는 제거하거나 simulation-disable하지 않는다.

비활성 슬롯은 가림 classifier의 occluder 및 관측 대상에서 모두 제외한다. 1% visibility flip도 비활성 슬롯을 켤 수 없다. 기존40D 관측은10개 `[present,x,y,z]` 슬롯이므로 최종6개 장애물을 수용하며, 나머지 슬롯은0이다. Actor policy55D·obstacles40D, Critic privileged3D, Action8D, tactile17D는 유지한다. 기존 tactile parent filter와 물체→손 역방향 ContactSensor는 최대7개 물체를 모두 포함한다.

물체 기울기·장애물 변위·가속도·비타겟 접촉 비용과 낙하/기울기 종료는 active mask를 사용한다. Target은 항상 활성 상태다. 새 슬롯 수를 기존 모든 물체 비용 함수에 그대로 넣어 주차된 물체를 낙하로 판정하지 않도록 v1.0 로컬 `object_state.py`에서 축약한다. 기존 v3와 공통 보상 함수는 변경하지 않는다.

타겟·Goal의 샘플링 함수·호출 순서·분포를 유지한다. `ClutterLayoutGenerator`에 population별 불변 Config 사본을 전달하고, 기존 source generator의 RED 여유2.3cm·물체 간격·밀도·approach 검사를 재사용한다. Gray 중 첫1개는 기존 뒤쪽 조건을 유지하고 추가 Gray는 일반 Gray 영역에 둔다. Gray3개 모두를 뒤쪽으로 제한하지 않는다. White는 RED/GRAY 밖이다. 배치 실패를 이유로 타겟·Goal을 다시 뽑거나 규칙을 완화하지 않는다.

### 개수를 조정하는 위치

[`env_cfg.py`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/contact_sweep_clutter_fusion_envs.py)의 `max_gray_obstacles`, `max_white_obstacles`로 Scene capacity를 조정한다. 합계는 기존 관측의 최대10개 이하다. [`curriculum_cfg.py`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/contact_sweep_clutter_fusion.py)의 `obstacle_population.params`에서 initial/final 개수, Gray/White 시작 iteration, interval을 조정한다. 실제 개수는 capacity 이하로 제한된다. Hydra에서 EnvCfg capacity를 덮어쓴 경우에도 runtime이 물리 초기화 전에 Scene을 다시 구성한다.

예시로 최대 White2개만 허용하려면 학습 명령 뒤에 `env.max_white_obstacles=2`를 붙인다. 시작부터 Gray2/White1을 사용하려면 `env.curriculum.obstacle_population.params.initial_gray=2`를 지정하고 Gray capacity/final도2 이상으로 유지한다. 숫자를 줄였다가 다시 늘려 인스턴스를 생성해도 이전 센서가 중복으로 남지 않는다.

### 클래스와 파일

Env Cfg/PPO Cfg는 계속 v3을 상속한다. Runtime은 `ContactSweepClutterFusionV1_0Env` → `ContactSweepClutterFusionEnv`로 확장하여 mask 초기화와 population RNG reset만 담당한다. Scene·Event·Reward·Termination·Curriculum 책임은 각 파일에 분리하고 기본 step loop를 복제하지 않는다. 등록 ID와 experiment 이름은 그대로다.

## 자동 재시작 학습

전용 진입점은 [`scripts/train_resilient.py`](../../../../src/inspire_sweep_baseline/scripts/train_resilient.py)다. Isaac Sim을 갖지 않는 supervisor가 기존 train.py를 새 프로세스로 실행한다. [`training_recovery.py`](../../../../src/inspire_sweep_baseline/scripts/training_recovery.py)는 checkpoint 검사·선택·iteration 복원 규칙을 제공한다. 기존 train.py는 내부 supervisor 옵션을 전달했을 때만 이 경로를 사용하며 일반 학습 호출은 유지한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train_resilient.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0 \
  --num_envs 2048 --headless --max_iterations 90000
```

`--task`를 바꾸면 이후 환경에도 사용할 수 있다. `--max_iterations`는 **각 시도에서 추가할 양이 아니라 전체 절대 목표**이고 기본값은90000이다. 다른 환경에서는 원하는 전체 목표를 명시한다. 재개는 명시적인 파일로 시작할 수 있다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train_resilient.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0 \
  --num_envs 2048 --headless --max_iterations 90000 \
  --resume-checkpoint /absolute/path/model_2500.pt \
  --rollback-iterations 500 --max-restarts 10
```

기본 산출물은 새 `logs/resilient/<task>/<UTC시각_uuid>/attempt_000`, `attempt_001`, … 폴더다. `--job-dir <새 경로>`로 변경할 수 있다. 기존 폴더 재사용·checkpoint 덮어쓰기·자동 로그 정리는 하지 않는다. `job.json`에 각 시도의 command, 복원 iteration, 종료코드, checkpoint 선택 이유와 상태를 남기고 시도별 console.log·params·checkpoint를 보존한다. 로그 시각은 UTC 형식이다.

자동 복구 규칙:

1. 전체 목표에 도달하기 전 오류 종료 또는 완료 표식 없는 조기 정상 종료가 발생하면 현재 작업의 checkpoint 계보를 조회한다. 다른 실험이나 임의의 최신 run은 검색하지 않는다.
2. 가장 최신의 저장 iteration을 L이라고 할 때, `max(0,L−500)` 이하에서 가장 큰 유효 checkpoint를 선택한다. 정확히500 전 파일이 없으면 그보다 앞선 파일을 사용한다. 실패한 runtime의 현재 iteration과 마지막 저장 iteration은 다를 수 있다.
3. checkpoint의 iteration·모델·optimizer tensor와 Gaussian std를 검사한다. NaN/Inf, std≤0, log-std의 지수 underflow/overflow, 깨진 파일은 제외한다. 최후의 유효 후보가 없고 목표 rollback이0이면 초기 상태부터 다시 시도한다. 그 외 복원 가능한 파일이 없으면 원인을 기록하고 종료한다.
4. 되돌리기 지점보다 늦은 이전 분기의 checkpoint는 삭제하지 않고 이번 작업의 후보에서만 제외한다. 재실패 시 폐기된 미래 분기로 돌아가지 않는다.
5. 새 프로세스에서 모델·optimizer를 load하고 checkpoint.iter로 모든 curriculum을 적용한 **뒤 환경을 reset**한다. 따라서2500에서 재개하면 첫 rollout 전부터 해당 Goal tolerance·Deadzone·force/acceleration 임계값·Gray1/White1이 적용된다.
6. 복원 iteration K에서 `target−K` 회만 실행한다. RSL-RL의 기존 관례대로 checkpoint.iter부터 루프를 시작하고 마지막 저장 index가target−1인지 확인한다. 예를 들어 target4000의 마지막 index는3999다.
7. 기본 최대 재시작은10회이며 `--max-restarts`로 조정한다.0은 재시작 없음이다. Ctrl+C/SIGTERM은 의도적 중단으로 처리하고 재시작하지 않는다. supervisor 출력 실패나 반복 중단 시에도 자식 프로세스를 정리한다.

전체 목표의 완료 표식과 최종 checkpoint가 모두 유효하면, 그 이후 Kit 종료 중 발생한 오류는 경고로 기록하고 이미 완료한 학습을 되돌리지 않는다. 명시적 Ctrl+C/SIGTERM 중단은 이 판정보다 우선한다.

PPO 수식·학습률·표준편차 parameterization·seed는 임의로 변경하지 않는다. 오류를 숨기거나 std를 clamp하는 코드가 아니며, 반복해서 재현되는 학습 발산의 원인까지 고쳤다는 의미는 아니다. 이 wrapper의 distributed 학습은 지원하지 않는다.

## 검증과 제한

### CPU 회귀 검사

Workspace 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  -q -p no:cacheprovider src/inspire_sweep_baseline/tests
```

**최종543 passed, 기존 ONNX DeprecationWarning3개, 26.00초.** 가속/감속 대칭성, alpha 경계와 live tolerance, 부분 reset·비활성 비용/종료 제외, 개수 경계/rewind, 다섯 population 단계별1024개 배치의 독립 geometry 검사를 포함한다. 기존 관측·제어·v3 회귀도 포함한다. 중간 검사에서 test fixture의 boolean indexing 오류1개를 수정한 뒤 전체를 재실행했다. Bootstrap 추가 검사 전에는542 passed/23.80초였으며, 최종 결과는 GPU에서 발견한 초기 저장 오류의 수정까지 포함한다.

자동 복구의19개 테스트에는 실제 자식 프로세스에서 요청의 std RuntimeError를 발생시키는 사례, 조기 정상 종료, 손상/nonfinite checkpoint, std0 및 log_std underflow, 연속 실패의 분기 제한, Ctrl+C, 로그 출력 실패 후 자식 정리, 최종 완료 후 오류 종료, 실제 Logger의 bootstrap 저장 수명주기가 포함된다. 실패·재개 시나리오에서0→2500→2100의 복원 iteration과4000/1500/1900의 남은 학습량을 확인한다.

### 실제 GPU 환경·PPO·복원

RTX GPU를 사용하는 sandbox 밖 실행에서 다음을 수행했다. Shelf 자산은 기존 로컬 USD를 읽었다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  INSPIRE_SWEEP_SHELF_USD_PATH=/home/min/Desktop/Shelf_USD/Arena/Collected_speedrack_shape/speedrack_shape.usd \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_clutter_fusion_v1_0_probe.py \
  --headless --device cuda:0 --num_envs 4 \
  --output outputs/fusion_v1_0_revision_validation/probe_final.json
```

결과는 **passed**다. [실제 판정 JSON](../../../../outputs/fusion_v1_0_revision_validation/probe_final.json)에17개 보상·9개 curriculum·6개 종료, 관측55/40/3D·Action8D, 30개 손 body 및 물체별 ContactSensor, 실물리12step의 유한값, 부분/timeout reset을 기록했다. Population0·2999·3000·4499·4500·5999·6000·7499·7500·20000·2500에서 정확한 활성 수·비활성 관측0·주차 pose 불변·PhysX gravity flag를 검사했다. 새 White2를20cm 높여 실제 step 후 떨어지는 것도 확인했다.

실제 palm 접촉에서 타겟 identity 제외와 기존 tactile을 확인하고, iteration0·1000·2500·7500·0의 현재 Goal tolerance마다 alpha0/0.5/1을 확인했다. 이어2499·2500의 실제 PPO update2회를 수행해 model_2500.pt를 생성했다. 환경을7500 단계로 전진시킨 뒤 이 checkpoint를 복원하여 첫 rollout 전에 iteration2500의 Goal0.01m·force43N·moment4.3N·m·acceleration0.23m/s² 및 Gray1/White1이 적용되는 것을 확인했다.

첫 GPU 시도에서는 simulation-disable actor의 pose 행이 population 변경 후 뒤섞이고 비활성 물체가 움직이는 문제가 재현됐다. reset state 쓰기 전에 actor를 다시 활성화해도 해결되지 않아, actor topology를 유지하는 현재 중력 제어·100m 주차 방식으로 수정했다. 그 후 모든 경계를 통과했다. probe fixture도 command getter가 반환하는 복사본 대신 실제 Goal buffer를 수정하고, PPO rollout 이후 동일 환경 재사용 구간은 inference_mode 안에서 실행하도록 고쳤다. 실패 기록은 probe.json·probe_diagnostic.json·probe_fixed1/2/3.json에 보존했다.

실제 supervisor의 최초 재개 검사는 iteration2500과 curriculum2500 복원 후, 학습 전 초기 snapshot 저장에서 아직 생성되지 않은 Logger.writer 접근 오류를 발견했다. bootstrap은 public `alg.save()`와 framework의 iter/infos 형식으로 로컬 파일을 원자적으로 저장하도록 수정했다. Writer는 기존 learn()에서 한 번만 초기화한다. 실패한 resume_job의 로그와 checkpoint는 그대로 보존했다. 설치된 RSL-RL의 실제 Logger·OnPolicyRunner로 오류를 재현하고 수정 후 저장 형식·writer 초기화 수명주기를 검사하는 회귀 테스트를 추가했다.

수정 후 다음 실제 supervisor 재개 명령을 실행해 **exit0·completed**를 확인했다. 기존 실패 폴더를 덮어쓰지 않고 새 폴더를 사용했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  INSPIRE_SWEEP_SHELF_USD_PATH=/home/min/Desktop/Shelf_USD/Arena/Collected_speedrack_shape/speedrack_shape.usd \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/scripts/train_resilient.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0 \
  --headless --device cuda:0 --num_envs 4 --max_iterations 2502 \
  --resume-checkpoint /home/min/7cmdehdrb/grad/outputs/fusion_v1_0_revision_validation/model_2500.pt \
  --max-restarts 0 \
  --job-dir /home/min/7cmdehdrb/grad/outputs/fusion_v1_0_revision_validation/resume_job_final \
  agent.num_steps_per_env=4 agent.algorithm.num_learning_epochs=1 \
  agent.algorithm.num_mini_batches=1
```

[실행 상태](../../../../outputs/fusion_v1_0_revision_validation/resume_job_final/job.json)와 [worker 상태](../../../../outputs/fusion_v1_0_revision_validation/resume_job_final/attempt_000/training_status.json)는 restored_iteration=2500, curriculum_iteration=2500, learning_iterations=2, last_iteration=2501, target_iterations=2502, status=completed다. 실제 학습 로그에서도 Gray1/White1·Goal0.01m·force43N·moment4.3N·m·acceleration0.23m/s²를 확인했다. 이 짧은 GPU 실행은 정상 재개 경로이며, 오류 주입과 반복 rollback 자체는 위 실제 자식 프로세스 CPU 검사로 검증했다.

문서 검사는 문서 저장소에서 `check_markdown_math.py` 및 `check_document_links.py --check-external`을 수정 문서6개에 실행했고 오류0이었다. 활성 코드와 문서 저장소의 `git diff --check`도 통과했다. 사용자 기존 PLAN·telemetry·다른 문서 변경과 기존 학습 로그는 유지했다.

장시간 학습의 안정화·성공률·실물 성능은 별도 검증 대상이다.
