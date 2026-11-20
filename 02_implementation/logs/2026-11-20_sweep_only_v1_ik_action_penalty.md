# 물체 옆 IK 시작의 Sweep Only v1 ActionPenalty

## 요청·기준·의도

사용자는 `Inspire-Sweep-Only-v0`를 직접 상속하여 Sweep 보상을 v1과 같게 하고 ActionPenalty를 적용하도록 요청했다. v1-Test 계열의 보상과 액션 비용을 물체 옆 IK 초기화에서 비교하는 것이 목적이다. 새 Task ID는 `Inspire-Sweep-Only-v1-ActionPenalty`, experiment name은 `inspire_sweep_only_v1_action_penalty`다.

기준 root commit은 `bab3f855df95702909b7e5e0815bdc67a24cfcce`. 시작 시 root 코드 작업트리는 깨끗했고 문서 submodule의 기존 변경만 있었다. 이를 보존했다. 기존 ID를 수정하거나 학습 로그를 변경하지 않았다. 서버별 학습 현황도 바꾸지 않았다.

## 최종 구성과 부모 대조

- EnvCfg: `SweepOnlyV1ActionPenaltyEnvCfg(SweepOnlyEnvCfg)` 직접 상속.
- Runner: `SweepOnlyV1ActionPenaltyPPORunnerCfg(SweepOnlyPPORunnerCfg)` 직접 상속.
- Runtime: 기존 `SweepOnlyEnv`.
- Sweep progress: 30 → **50**; retreat: −20 → **−10**; contact count/20은 그대로.
- 기존 공통 `_configure_action_penalty` 재사용: 팔 ±π/2 실행 제한, 손 URDF 한계 유지, 팔/손 범위 초과 비용 각−0.03, 기존 Action 변화 L2의 원본 이력 사용.
- Runner clip_actions: π/2 → None. 원본 출력을 Manager에 전달하고 실제 제한은 Action term에서 수행한다. Last Action 관측은 기존 ±π/2 값을 보존한다.
- 물체 옆 IK·초기 로봇 점유 공간 제외·RED·충돌 검사·초기화 실패 복구는 v0와 동일하다. Reach 없음, Deadzone30°, 대표점 GUI 마커 기본 비활성도 유지한다.
- Scene·Command·나머지 Observation/Reward·Termination·Curriculum·모델·학습률·entropy·수치 검사 등은 부모와 동일하다. IsaacLab이나 모델 코드는 수정하지 않았다.

실제 `to_dict()` 전체 대조에서 v0 대비 위 액션 설정·관측 함수·두 추가 비용·두 Sweep weight와 runner clip/log 이름 이외의 차이는 없었다. 자식 생성 후 부모 및 새로 생성한 부모 설정도 변하지 않았다.

`Inspire-Sweep-Only-v1-Test-ActionPenalty`와 비교하면 **초기화 Event 구성, Reach 없음, debug_surface_points=False**만 다르다. “IK만 바꾼 느낌”을 물체 옆 시작에는 Reach를 사용하지 않는 기존 합의와 함께 적용했다. 초기화만 다르고 모든 설정이 문자 그대로 동일하다고 설명하지 않는다. 독립적인 `Inspire-Sweep-Only-v1` ID는 추가하지 않았다.

## 코드와 사용

기존 역할별 파일에 EnvCfg·PPO 자식을 추가하고 패키지 등록 루프에 새 ID를 연결했다. `scripts/check_sweep_only_action_penalty.py`에 신규 v0/자식 전체 대조와 v1-Test-ActionPenalty 차이 검사를 추가했다. 실행 명령과 계열 표는 [계열 안내](../environments/SWEEP_ONLY_FAMILY.md#물체-옆-ik와-v1-보상-v1-actionpenalty)에 기록했다.

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Only-v1-ActionPenalty --num_envs 2048 --headless
```

## 검증 결과

workspace 루트에서 실행했다. 실행 전 GPU compute process가 없는 것을 확인했다.

```bash
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_sweep_only_action_penalty.py src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_sweep_only_action_penalty.py --headless --task Inspire-Sweep-Only-v1-ActionPenalty --output /tmp/sweep_only_v1_action_penalty_ik.json
```

- CPU **100 passed / 6.96초**.
- 실제 Isaac Sim·RTX3090·seed42·2환경: IK 초기화, wrapper 3step, 원본 현재/이전 액션 이력, 팔/손 실행 제한, 신규 비용, 부분 reset 통과.
- 실제7쌍의 부모/ActionPenalty EnvCfg·runner 전체 대조 통과. 추가로 v1-Test-ActionPenalty와의 위3종 차이만 허용한 대조도 통과했다.
- 원본 ±200은 처리·비용만 검사하고 물리 step에는 적용하지 않았다. 실제 step 입력은 팔0·손 상한1.1배였으며 손 목표는 실제 상한에 제한됐다.
- 임시 결과: `/tmp/sweep_only_v1_action_penalty_ik.json`, `/tmp/check_sweep_only_v1_action_penalty_ik.log`, `/tmp/sweep_only_v1_ik_pytest.log`.

장기 학습,2048환경 collection time,성공률,범위 초과 비용의 장기 수치 안정성은 미검증이다. 기존 v0 초기화 경로를 재사용했다는 사실을 신규 환경의2048 성능 실측으로 해석하지 않는다.
