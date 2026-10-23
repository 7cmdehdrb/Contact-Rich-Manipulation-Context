# TEMP 전체 감사와 action 관측 피드백 발산 수정

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [이전 개별 run 조사](2026-10-24_holding_osc_resume_crash_audit.md)

## 요청과 범위

2026-10-24 사용자 요청: `logs/TEMP`의 모든 환경을 검토하고 반복되는 std 오류 중단을 막을 방법을 마련한다. 기준 Workspace commit은 `df95c75`이며 시작 시 IsaacLab 미추적 파일 표시가 있었다. 기존 사용자 작업과 이전 조사 문서 변경을 보존했다. 원본 학습 로그·checkpoint는 읽기 전용으로 검사했으며 이동·삭제·정리하지 않았다. 진단 학습은 checkpoint 복사본을 사용하고 결과를 `outputs/temp_training_audit`에 기록했다.

## 전체 감사

현재 TEMP에는4개 run이 있다. 첫 run은 Holding OSC v2의 원본, 나머지는 그 `model_2100.pt`에서 재개한 run이다. 관측·모델·PPO 수치 설정은 같은 계열이며 마지막 run만 환경 수가1024다.

| run | 환경 수 | 기록된 iteration | 최대 유한 value loss | 저장 checkpoint |
| --- | --- | --- | --- | --- |
|2026-10-23_22-20-48|2048|0~2107|4.439e29, 이후NaN|43|
|2026-10-24_01-40-57|2048|2100~2102|1.337e32|1|
|2026-10-24_01-43-17|2048|2100~2102|1.337e32|1|
|2026-10-24_01-45-06|1024|2100~2341|1.941e21|5|

총50개 checkpoint의 모델·optimizer 등 모든 tensor를 재귀 검사했다. 저장 파일에서는NaN/inf를 발견하지 않았으며 scalar std도 양수였다. 네 run 모두 value loss 급등 기록이 있다. 예외 순간 모델은 저장 주기 사이에 있어 저장 checkpoint 정상 여부만으로 학습 안전성을 판단할 수 없다.

감사 결과는 [요약 CSV](../../03_assets/artifacts/temp_stability_2026-10-24/summary.csv), [설정·지표·checkpoint JSON](../../03_assets/artifacts/temp_stability_2026-10-24/audit.json)에 보존했다. stderr/예외 원문이 모든 run에 저장된 것은 아니므로 이 표만으로 각 run의 프로세스 종료 사유를 확정하지 않는다.

## 최소 PPO 재현

설치된 RSL-RL5.0.1의 실제 PPO·MLPModel·RolloutStorage를 사용한 CPU 재현에서 관측 한 행에 유한한`1e30`을 넣었다. value 최대값6.47e28, value lossNaN, std `[NaN,NaN]`을 거쳐 다음 sampling에서 사용자와 같은 `normal expects all elements of std >= 0.0`가 발생했다. 이는 오류 전파 경로의 재현이며 실제 센서가1e30을 출력했다는 뜻은 아니다.

## 실제 실패 직전 데이터와 원인

원본 `model_2100.pt` 복사본, seed42,2048환경, 동일 task로 진단 실행했다. 새로운 수치 검사가 iteration2101에서 env366의 Actor mean1.234e6을 탐지해 중단하고 약42MB의 `numerical_failure.pt`를 저장했다. 이때 큰 입력은 F/T나 관절 속도가 아니라 이전 action 관측이었다.

- policy55D의 index12~19: 이전 raw action8D. 최대 절댓값909989.
- 같은 행의 관절 속도는 약[-3.36,4.00], F/T6D는 최대 약0.00261, pose·초기 목표·장애물 값도 보통 범위였다.
- raw action 관측을 재입력한 Actor mean 최대 절댓값1234151.75.
- Actor/Critic 파라미터의 최대 절댓값은 약7.83·8.33으로 유한했다.
- 당시 저장 rollout의 reward 최대 절댓값은13.46, value는224373이었다.

**큰 raw action → 다음 step의 raw last_action 관측 → 더 큰 Actor 출력**의 증폭 경로를 실제 모델·실제 관측으로 확인했다. MLP라도 이전 출력을 다시 넣으면 피드백 계가 된다. 물리 상태가 폭주하지 않아도 이 경로는 발산할 수 있다.

같은 모델과 관측을 사용한 원인 분리 replay:

| 조건 | Actor mean 최대 절댓값 |
| --- | --- |
|원본 관측|1234151.75|
|이전 action8D만[-1,1]로 제한|15.044|
|F/T6D만0으로 변경|1234151.75|

다른 물리 관측을 고정하고 이전 action만 반복 갱신한100회 replay에서 원본은1.638e14까지 증가했고 제한한 feedback은 약15.856에 머물렀다. [replay 결과](../../03_assets/artifacts/temp_stability_2026-10-24/action_feedback_replay.json). 이 근거는 이번 재현의 직접 원인을 지지하며 다른 모든 향후 수치 오류의 원인을 배제하지는 않는다.

## 수정

1. Fusion 관측의 action8D를 로컬 `bounded_last_action()`으로 읽는다. out-of-place `clamp(-1,1)` 복사본만 정책에 전달한다. raw manager action·prev_action·Action term 실행·보상 계산에는 쓰지 않는다. Fusion과 그 Holding/OSC/ObjectRandom 파생에 적용된다. 관측 차원·모델/optimizer 키는 같지만 범위 밖 action의 입력 의미는 바뀐다. 기존 정책의 동작 동등성이나 학습 성능 향상을 보장하지 않는다.
2. `CurriculumOnPolicyRunner`가 기본 PPO를 로컬 `NumericalPPO`로 구성한다. rollout 관측·Actor mean·Critic value·환경 reward·bootstrap 후 reward·returns·advantages·gradient·파라미터·optimizer의 수치 유효성을 검사한다. 관측/value/return의 절댓값 및 value loss 기본 중단 상한은1e6이다. 이 값은 진단용 ceiling이며 물리 센서 calibration이나 reward clipping이 아니다.
3. scalar std는 optimizer.step 후 최소1e-4로 투영한다. 기존`distribution.std_param` 이름과 shape를 유지해 scalar checkpoint/Adam 상태를 그대로 로드한다. NaN을 양수로 덮어쓰지 않으며 비유한 값은 별도로 거부한다.
4. optimizer state load 후 PPO의 adaptive learning_rate 변수도 복원한 param_group LR과 동기화한다. 설치된 PPO는 optimizer LR만 복원해 첫 adaptive 조정이 새 설정의 LR에서 시작하는 문제가 있었다. 이것을 action 피드백 발산의 유일 원인으로 해석하지 않는다.
5. 수치 이상 시 원인·iteration·관측·rollout·gradient·현재 상태·update 전 상태를`numerical_failure.json`/`.pt`에 남긴다. update 중 실패하면 모델/optimizer 메모리를 update 직전으로 복원한 후 예외로 중단한다. rollout이나 프로세스를 자동 재시작하거나 batch를 건너뛰지 않는다. 정상 update의 계산은 설치된 PPO를 그대로 사용한다.

네 raw 운동 페널티와 계수, reward 함수·정규화·dt 적용·물성·제어 scale는 변경하지 않았다. scalar std의 양수 제한은 학습 분포 파라미터의 제한이며 보상 내부 Hand action clamp가 아니다.

## 실제 명령과 검증

Workspace 루트에서 실행했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe src/inspire_sweep_baseline/scripts/audit_training_runs.py logs/TEMP --output outputs/temp_training_audit/full_audit
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/temp_training_audit/reproduce_ppo_failure.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/temp_training_audit/replay_action_feedback.py
```

최초 PPO 재현은 위 std RuntimeError로 실패했다. 수정 전 실제 진단 실행은 다음과 같다. checkpoint_source는 원본의 복사본이며 원본 파일을 변경하지 않았다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -u src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2 --num_envs 2048 --resume --experiment_name C:/python/Contact-Rich-Manipulation/outputs/temp_training_audit --load_run checkpoint_source --checkpoint model_2100.pt --max_iterations 5 --headless
```

수정 전 진단 결과는`outputs/temp_training_audit/2026-10-24_02-24-07/numerical_failure.pt`와`train_2100_guarded.log`다. 앞서 model2300에서 시작한60iteration 진단은 더 빠른 model2100 재현 조건을 확인한 뒤 수동 중단했다. 자동 복구나 로그 삭제는 수행하지 않았다.

수정 후에는 위 명령의`--max_iterations`만20으로 바꿔 같은2048환경에서 실행했다. `2026-10-24_02-28-21` 진단 run은2100~2119의20iteration, 총1474560개 환경 step을 학습하고 exit0으로 정상 종료했다. 학습 시간은176.74초였다. value loss는 첫2100에서5.3017, 기존 중단 지점2102에서0.7470, 마지막2119에서0.4765였으며 전체 기록의 최대도5.3017이었다. 저장된2100/2119 checkpoint의 모델·optimizer tensor도 모두 유한했다. [수정 후 감사 JSON](../../03_assets/artifacts/temp_stability_2026-10-24/fixed_audit.json). 기본 수치 검사는 켜진 상태였다. 이 결과를 장기 학습 전체의 안정성 보장으로 해석하지 않는다.

CPU 검증은 action 관측의 raw buffer 비변경·feedback 제한, 실제 PPO NaN 전파와 방어, 정상 update의 upstream과 bitwise 동등성, resume LR·checkpoint 저장/로드·JIT export, Fusion/Holding 계약과 raw reward 검사를 포함했다.62개 테스트와 추가93개 테스트가 각각 통과했다. 두 번째 실행에는 기존 ONNX deprecation warning2개가 있었다.

실제 CPU 검증 명령:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_clutter_fusion_observations.py src/inspire_sweep_baseline/tests/test_numerical_ppo.py src/inspire_sweep_baseline/tests/test_fusion_holding_osc.py src/inspire_sweep_baseline/tests/test_fusion_holding_v2.py src/inspire_sweep_baseline/tests/test_omni_configuration.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_configuration_contract.py src/inspire_sweep_baseline/tests/test_task_contract.py src/inspire_sweep_baseline/tests/test_fusion_holding_v0.py src/inspire_sweep_baseline/tests/test_fusion_holding_v1.py src/inspire_sweep_baseline/tests/test_clutter_fusion_models.py src/inspire_sweep_baseline/tests/test_goal_rewards.py src/inspire_sweep_baseline/tests/test_dex_rewards.py
```

변경 Markdown의 수식·링크 검사와 두 저장소의 `git diff --check`도 통과했다. 원본 TEMP checkpoint 수는50개 그대로이며 원본 model2100과 진단 복사본의 SHA256 일치도 확인했다.

장기 학습·전체 task의 GPU 실행·Ubuntu GPU 실행·실물 성능은 이번 검증 범위에 포함하지 않는다. 이전 action 관측의 의미가 바뀌었으므로 성능은 수정 후 조건에서 다시 평가해야 한다.
