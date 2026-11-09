# Relative-IK-v0_2_2_3-Fast-Test 개발 기록

2026-11-09. 사용자 요청에 따라 v0_2_2_2-Fast-Test를 직접 상속한 새 환경을 추가했다. 기존 작업트리의 Fast 구현 및 사용자 변경은 보존했다. 기준 HEAD는3501ffb이며 이번 작업은 기존 함수 수정 없이 자식 정의와 등록을 추가했다.

## 등록과 최종 계약

- Gym ID: `Inspire-Wrench-Refactor-Relative-IK-v0_2_2_3-Fast-Test`.
- EnvCfg: `WrenchRefactorRelativeIKV0_2_2_3FastTestEnvCfg` → `WrenchRefactorRelativeIKV0_2_2_2FastTestEnvCfg` 직접 상속.
- runtime: 부모와 같은 `WrenchRefactorRelativeIKV0_2_2_2FastTestEnv`.
- PPO: `WrenchRefactorRelativeIKV0_2_2_3FastTestPPORunnerCfg` → 부모 Fast runner 직접 상속. experiment_name만 `inspire_wrench_refactor_relative_ik_v0_2_2_3-Fast-Test`로 변경.

| 항목 | 부모 | 새 환경 |
| --- | --- | --- |
| 접촉 카운트 상한 | 10 | 20 |
| 최종 접촉 불인정 | 카운트 즉시0 | 카운트−2, 최소0 |
| 접촉 인정 | 카운트+1 | 동일 |
| 불인정 step 보상 | 0 | 0; 감소한 카운트는 재접촉 인정 시 활용 |
| Holding 보상 | goal_hold 활성 | None |
| Holding 커리큘럼 | goal_speed_scale 활성 | None |

접촉은 타겟 손 접촉력0.01N 이상·센서 fresh/finite·초기 선반 표면 기준 EEF 높이15cm 미만, 최근3step 중2step 및 현재 높이 gate를 그대로 사용한다. 원시 접촉 미검출1회가 반드시 최종 불인정은 아니다. 카운트 감소는 최종 불인정마다 적용한다. 별도 `TargetContactDecayMaintenance`를 추가해 기존 부모 함수 결과를 보존했다. episode reset은 여전히 이력과 카운트를0으로 초기화한다. weight0.1·step_dt0.02는 유지되어 인정 step 보상 최대값은0.02에서0.04로 증가한다.

Holding 삭제는 goal_hold 및 이를 대상으로 하는 유일한 커리큘럼 goal_speed_scale에 한정한다. 이름에 holding이 들어가는 shelf_failure 계산이나 다른 보상·일정을 삭제하지 않는다. 목표3cm, 목표 거리/역방향 페널티−25.94, 접촉 높이 조건, 실패/timeout 종료는 유지한다. Scene·Command·Event/reset·Actor/Critic Observation·Action·나머지 Reward/Termination/Curriculum·Fast 기하/Warp backend 및 PPO 수치는 부모와 동일하다.

## 검증과 미검증 범위

실제 configclass를 사용하는 CPU 설정 검사에서 부모·자식 전체 EnvCfg를 비교했다. 예상 차이는 hand_contact/goal_hold/goal_speed_scale뿐이며, 자식 생성 후 부모를 재생성해 동일함을 확인했다. Scene/asset는 CPU double을 사용하므로 native Sim 검증은 아니다. 등록 코드 블록 실행으로 Gym ID와 runtime/EnvCfg/runner 연결을 확인했고 PPO AST로 부모 직접 상속 및 experiment_name 단독 변경을 확인했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  src/inspire_sweep_baseline/tests/test_fast_reset.py -q -p no:cacheprovider
```

결과: **42 passed, 2 skipped**,7.76초. 접촉 상한20,2-of-3 판정, 반복 감산과 하한0, 동일 step 중복 호출, 접촉 재개, 부분 episode reset, 높이 경계, 부모 접촉 규칙 회귀 및 Fast reset 검사를 포함한다. skip은 선택 실행하는 대량 배치/실제 USD 검사다. 문서 수식·링크·git diff 공백 검사도 수행했다.

GPU/PhysX 및 학습은 실행하지 않았다. 이전 Fast의 GPU 미검증 상태는 유지되며 이번 CPU 검사가 학습 안정성이나 성능 향상을 입증하지 않는다. 학습 로그는 변경하지 않았다.

## 실행

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-Refactor-Relative-IK-v0_2_2_3-Fast-Test \
  --num_envs 2048 --headless
```

## 후속 정정: 불인정 시 잔여 카운트 보상

사용자가 접촉 불인정이어도 높이15cm 미만이면 남은 카운트 보상을 지급해야 한다고 정정했다. 최초 구현의 불인정 보상0 처리는 의도 오해였으므로 위 최종 계약에 반영했다. v0_2_2_3-Fast-Test 전용 함수의 보상 gate만 accepted에서 height_valid로 변경했다. 접촉 인정·카운트+1/−2·상하한·부모 환경은 보존한다. 현재 높이15cm 이상이면 과거 접촉이나 잔여 카운트와 관계없이 보상0이며 카운트는2 감소한다.15cm 미만에서 불인정 시에도 감소 후 카운트×weight0.1×dt를 지급한다.

회귀 검사의 연속 불인정 기대값을18,16,…,0으로 변경했다. 중복 호출 시 감산 중복 방지, 하한0, 높이15cm 경계에서 잔여 카운트가 있어도 보상0, 부분 reset 및 부모 규칙 검사는 유지했다. GPU/학습은 실행하지 않았다.

후속 정정 후 동일 CPU 명령 결과: **42 passed, 2 skipped** (7.77초). 문서 수식·링크 및 diff 공백 검사 통과.

## 최종 사용자 결정: 카운트 −2, 불인정 보상0

앞선 잔여 보상 지급안과 비교 논의 후, 사용자가 카운트−2와 불인정 step 보상0을 최종 선택했다. 접촉 유지와 빠른 재접촉을 유도하면서 기존 누적 이력은 일부 보존하려는 의도다. 전용 함수의 보상 gate를 accepted로 변경했다. 기존2-of-3 접촉 인정·높이15cm 미만 gate·카운트0–20·Holding 제거·부모 설정은 유지한다. 위 잔여 지급 절은 중간 결정 이력이며 현재 계약은 이 절과 상단 표를 따른다.

재접촉 보상 검사를 추가했다. 상한20에서 원시 접촉 미검출 첫 step은 기존2-of-3으로20 지급, 다음 불인정은 카운트18/보상0, 접촉 재개 첫 step은 아직1-of-3이므로16/보상0, 다음 인정 step은17 지급임을 검사한다. 이는 원시 접촉 검출 즉시 보상 재개가 아니라 기존 최종 인정 기준에 따른 재개다. GPU/학습은 실행하지 않았다.

최종 변경 후 동일 CPU 회귀 명령: **43 passed, 2 skipped** (7.93초). 문서 수식·링크 및 diff 공백 검사 통과.
