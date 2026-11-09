# Relative-IK-v0_2_2-Test: 타겟 접촉 카운트 실험

## 요청·확정 조건

사용자는 v0_2-Test 대비 v0_2_1-Test에서 EEF/타겟 속도 초과 비용을 제거하니 타겟의 과도한 속도·넘어짐이 두드러진다고 보고했다. 접촉 유지 보상으로 이를 줄일 수 있는지 실험하기 위해 일반 v0_2_1-Test를 상속한 v0_2_2를 요청했다. Reset-Test 방식은 효과가 크지 않다는 사용자 판단으로 잠정 보류하며 코드·등록·학습 로그는 보존한다.

참조 계열의 원래 함수에는 EEF 높이14cm 제한·목표3cm 점유 우회와 weight0.1이 있었다. 사용자에게 차이를 확인했고 다음으로 확정했다.

- 타겟–손 실제 접촉만 인정. EEF 높이 조건 없음.
- 목표3cm 안이라는 이유로 접촉을 인정하지 않음.
- 현재 포함 최근3step 중2step 접촉이면 인정. 인정마다 카운트 증가, 상한10.
- 불인정 창에서는0 지급.5회 연속 불인정 시 카운트 초기화.
- weight0.1 적용.

[전체 환경 계약](../environments/WRENCH_REFACTOR_RELATIVE_IK_V0_2_TEST_ENVIRONMENT.md#v0_2_2-test-타겟-접촉-카운트-실험)

## 구현·부모 대조

기준 commit `6705c050349a2a89e4e161b3d96ceb26b301a144`. 시작 시 코드 저장소는 문서 submodule 포인터 외 변경이 없었다. 이전 환경·서브모듈 커밋·사용자 변경·`logs/rsl_rl`을 보존했다.

- Gym ID: `Inspire-Wrench-Refactor-Relative-IK-v0_2_2-Test`.
- 실험명: `inspire_wrench_refactor_relative_ik_v0_2_2-Test`.
- EnvCfg: `WrenchRefactorRelativeIKV0_2_2TestEnvCfg(WrenchRefactorRelativeIKV0_2_1TestEnvCfg)`.
- RewardsCfg: `WrenchRefactorRelativeIKV0_2_2TestRewardsCfg`가 v0_2_1 RewardsCfg를 상속해 `hand_contact`만 덮어쓴다.
- runtime: 일반 부모의 `WrenchRefactorRelativeIKV0_2TestEnv` 그대로 사용. Reset-Test runtime/이벤트/크기 공유를 사용하지 않는다.
- PPO: 부모 runner 직접 상속, experiment_name만 변경.

`TargetContactMaintenance`는 RefactorContactMaintenance의 상태 버퍼·선택 reset을 상속하고 평가 함수만 새로 정의했다. 현재 타겟의 object/hand force matrix를 사용하는 공통 계산 함수를 재사용하며, 목표 거리·EEF 높이를 읽지 않는다. 임계값은 기존0.01N, 최신 센서와 유한 힘 조건이다. 여러 접촉력은 벡터 합으로 판단하므로 반대 힘은 상쇄될 수 있다.

최근 창은 현재 원시 접촉이 없어도 직전 두 step이 접촉이면 한 step 인정될 수 있다.5회 불인정은 원시 접촉 부재5회가 아니라 **창 판정의 연속 불인정5회**다. 불인정 중4회까지 카운트는 보존하되 보상은0이다. 중간에 인정되면 misses는0이 된다. 같은 step 중복 호출은 캐시를 반환하고, step 평가가 누락되면 연속 이력을 초기화한다.

| 항목 | 부모 | v0_2_2-Test |
| --- | --- | --- |
| hand_contact 함수 | hand_contact_or_goal | TargetContactMaintenance |
| 접촉 범위 | 손 전체 합력 | 타겟–손 합력 |
| 목표 점유 우회 | 유효 타겟3cm 안이면 인정 | 없음 |
| 시간 구조 | step별 이진값 | 2-of-3 인정 창·상한10 카운트 |
| weight | 1.45 | 0.1 |
| step당 최대(dt0.02) | 0.029 | 0.02 |

GPU 전체 EnvCfg 사전 비교에서 위 한 RewardTerm 외 모든 항목이 부모와 같고, PPO도 실험명 외 동일했다. 부모를 다시 생성해 사전 불변을 확인했다. 나머지14개 보상·10개 커리큘럼·4개 종료·씬/센서/관측/액션/목표/관절 한계/초기 IK/일반 reset·Metrics는 보존한다. EEF/타겟/팔 초과 속도 비용은 여전히 없다. 기존 goal_hold의 속도 감쇠와 관절 속도 제곱 비용·팔 속도 종료는 그대로다.

## 검증

- CPU **111 passed, 9.33s**. 부모/자식 보상 사전 대조, 원래 Refactor 회귀, 실제 타겟 접촉 임계값, 목표 점유만으로0, EEF 센서·높이 설정 없이 동작, 장애물 힘 제외, 최근3step 창, 상한10,5회 연속 불인정 초기화, duplicate call/부분 reset/skipped step, stale/NaN 센서 차단을 검사했다.
- 실제 GPU RTX3090 **8환경·120step** 통과. 전체 설정/PPO/부모 불변 비교, 실제 PhysX 관절 한계, 유한 관측/보상, 일정 변경/rewind, 부분 reset 및 Metrics8개를 확인했다.
- 실제 목표에 타겟을 정지시켜 Holding 보상은 지급되는 상태에서 접촉 센서 freshness를 끄고 Contact 평가를 반복해0임을 확인했다. 목표 점유로 접촉 보상을 대체하지 않는다.
- Hold151회 호출 검사는 누적 지급 시간 상한이 없는지를 검사한 것이며 물리3초 유지 실험은 아니다.

## 재현·산출물

workspace 루트에서 실행한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor.py -q -p no:cacheprovider

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_wrench_refactor_relative_ik_test_probe.py \
  --headless --num-envs 8 --contact-child \
  --output outputs/relative_ik_v0_2_2_test_validation

python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-Refactor-Relative-IK-v0_2_2-Test \
  --num_envs 2048 --headless
```

GPU 결과는 `outputs/relative_ik_v0_2_2_test_validation/result.json`, stdout은 `/tmp/ik_v0_2_2_probe.log`다. 장기 학습에서 접촉 유지가 빨라진 타겟 이동·넘어짐을 줄이는지,2048환경 성능 및 수렴은 미검증이다. 사용자의 원인 판단을 입증된 인과관계로 기록하지 않는다.


추가 학습 연결 검증: `train.py`에서32환경·2iteration을 실행해 통과했다. 위 학습 명령에 `--num_envs 32 --max_iterations 2 --resilient-attempt-dir outputs/relative_ik_v0_2_2_test_validation/train --resilient-target-iterations 2`를 사용했다. TensorBoard의 hand_contact·Metrics8개 출력, 삭제한 속도 보상 부재, 모든 기록 scalar의 유한값을 확인했다. 산출물은 `train/`, `training_log_validation.json`, stdout은 `/tmp/ik_v0_2_2_train.log`다. 이는 학습/로깅 연결 확인이며 정책 성능 검증이 아니다.

최종 정적·문서 검사: 변경 Python AST 통과, 문서5개 math 검사 통과, 내부 링크197개 오류0. 등록 파일 EOF 빈 줄을 정리한 뒤 코드/문서 저장소 `git diff --check`를 통과했다.


## 후속 수정: Contact EEF 높이15cm 제한

사용자는 v0_2_2-Test의 Contact 보상에 EEF 높이 제한15cm를 추가하도록 요청했다. 위 최초 구현의 높이 제한 없음은 이 후속 수정으로 대체한다. 기존 작업트리의 v0_2_2 구현을 보존하며 해당 환경에 직접 적용했다.

`hand_contact.params.eef_height_limit=0.15`를 추가하고 초기 선반 표면 기준 `EEF_z < initial_shelf_z + SHELF_SURFACE_HEIGHT + 0.15`를 판정한다. 원래 Refactor 높이 gate와 같은 엄격한 미만 판정으로,15cm 경계·그 이상·NaN/Inf는 불인정한다. 원시 접촉뿐 아니라 현재 창 인정에도 적용하므로 이전2step의 접촉 이력으로 높이 제한을 우회하지 않는다. 높은 상태가5회 연속이면 카운트를 초기화한다. 목표 점유 우회 없음·타겟 전용·2-of-3·상한10·weight0.1은 유지한다. 일반 EnvCfg의 goal_reward_height_limit/contact_height_limit 또는 다른 보상·부모 환경은 변경하지 않았다.

CPU116개 통과(9.78s). 추가5개 사례는15cm 직전/정확히 경계/직후/NaN/Inf이며,0이 아닌 초기 선반 높이를 사용해 상대 기준과 즉시 지급 차단·5회 초기화를 검사했다. 실제 실행 명령은 위 CPU 명령과 같다.

후속 GPU4환경·120step도 통과했다. 위 probe 명령의 `--num-envs 4 --output outputs/relative_ik_v0_2_2_test_validation/height15`로 실행했으며 전체 설정 대조와 실제 센서 연결·부분 reset·유한 관측/보상을 확인했다. stdout은 `/tmp/ik_v0_2_2_height15.log`다. 이 후속 변경 뒤 PPO 학습은 재실행하지 않았고 장기 성능은 미검증이다. 문서4개 math 검사·내부 링크196개 오류0, 코드/문서 diff 공백 검사를 통과했다.
