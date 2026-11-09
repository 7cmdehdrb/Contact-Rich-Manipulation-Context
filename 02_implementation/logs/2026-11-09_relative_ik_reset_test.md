# Relative-IK-v0_2_1-Reset-Test 구현

## 요청·결정

사용자는 다양한 환경을 유지하면서 비싼 크기 구성·배치·IK 생성 비용을 공유하고, 질량·마찰 등 물성은 reset마다 갱신하는 파생 환경을 요청했다. 중간 논의의 영구 단일 배치나 환경별 독립8개 캐시를 그대로 구현하지 않았다. 최종 요청은 그룹별 초기 조건 공유·재사용·교체와 물성 독립 초기화다.

[전체 초기화 계약·설정값·실행](../environments/WRENCH_REFACTOR_RELATIVE_IK_V0_2_TEST_ENVIRONMENT.md#v0_2_1-reset-test-그룹별-초기-조건-공유물성-재추첨)

기준 commit은 `ed7572c95d57cb3871149e2fc17c78ead23978a5`이며 기존 v0_2_1-Test/Metrics 구현이 미커밋 상태였다. 그 변경과 문서 submodule 포인터를 보존했다. `logs/rsl_rl`은 수정하지 않았다. 이번 비교용 그룹16/목록8/교체32는 사용자 지정 숫자가 아니라 조절 가능한 구현 기본값이며 최적값이라고 주장하지 않는다.

## 구현·변경 전후

- Gym: `Inspire-Wrench-Refactor-Relative-IK-v0_2_1-Reset-Test`.
- EnvCfg: `WrenchRefactorRelativeIKV0_2_1ResetTestEnvCfg(WrenchRefactorRelativeIKV0_2_1TestEnvCfg)`.
- runtime: `WrenchRefactorRelativeIKV0_2_1ResetTestEnv(WrenchRefactorRelativeIKV0_2TestEnv)`. 부모 v0_2_1-Test가 사용하던 runtime의 직접 파생이다. explicit seed reset에 추가 난수 스트림/목록만 초기화한다.
- PPO: `WrenchRefactorRelativeIKV0_2_1ResetTestPPORunnerCfg`가 부모 runner를 직접 상속하며 experiment_name만 변경한다.
- Scene 스포너: 기존 구조를 유지하고 Reset 전용 spawner 설정에만 `reset_scale_groups`를 추가했다. 공통 spawner는 이 속성이 있을 때만 숫자 env_id 기준으로 같은 그룹의 크기를 공유한다. 속성이 없는 부모의 기존 추첨·형상 생성 경로는 그대로다.
- Event: startup 기하/물성 버퍼 초기화는 유지한다. reset은 `reset_all → object_spawn(공유 배치+IK) → reset_physics` 순서다. 기존 별도 robot_initial_pose term은 통합 event 안에서 필요한 대표 환경에만 원래 함수를 호출한다. 원래 IK 수치/후보1회/오류 판정은 유지한다.
- 같은 그룹의 동시 reset 대상은 한 초기 조건을 공유한다. 빈 목록을 채운 뒤에는 저장된 조건을 균등 선택하고32회마다 한 항목을 순환 교체한다. 목표 방향/배치/IK 파라미터 변경 시 전 그룹 목록을 무효화한다. 그룹별 크기가 같아 배치와 생성Z·IK 복사가 호환된다. world 좌표는 env origin을 뺀 상태로 저장하고 적용 시 더한다.
- 물성: 대상 환경의 모든17개 물체 질량을 독립 추첨하고 원래 물체별 관성에서 비례 갱신한다. 선반·물체·손 마찰은 기존 균등 bucket에서 독립 선택한다. 정적/동적 마찰의 분포, mass_scale1.5, 원래 고정 선반/로봇 질량을 보존한다. 다른 환경의 PhysX 행에는 쓰지 않는다.
- 관측 스냅샷 노이즈·가시성·초기 타겟 관측은 재사용하지 않는다. 모든 에피소드 속도·액션/보상 누적·Metrics 초기화는 유지한다. IK 표시도 복사된 초기 상태에 맞게 갱신한다.

전체 EnvCfg 대조는 부모 대비 **events, spawner의 그룹 필드, 그룹/목록/교체 설정3개**만 차이임을 확인했다. 보상15개·커리큘럼10개·종료4개·관측58+64D·행동8D·OSC·센서·타겟/목표 생성 수치·10초 제한은 유지한다. 부모 EnvCfg를 다시 만들어 작업 전 스냅샷과 일치함을 확인했다. 분포 수식은 유지하나 그룹 내 초기 조건 상관과 유한 목록 재사용으로 에피소드별 독립성은 달라진다.

## 검증

- CPU109개 통과(9.53s): 기존 Refactor/Test 회귀와 새 pool의 채우기/재사용/순환 교체, stage 변경 및 rewind 무효화, seed 재현, 미참여 그룹 보존.
- 실제 Isaac Sim GPU8환경·크기2그룹·목록2개·교체3회 설정으로 여러 부분 reset 및31step 실행 통과. 작은 설정으로 모든 분기를 빠르게 검증했으며 기본 설정16/8/32는 전체 설정 대조로 확인했다.
- 실제 크기 metadata에서 같은 그룹의 모든17슬롯 크기 일치·그룹 간 차이를 확인했다.
- 캐시 hit에서 원래 layout/IK 함수를 호출하면 실패하도록 바꾼 검사를 통과했다. 실제 물체의 env-local 배치와 로봇 관절각이 같은 그룹 내에서 일치했다.
- 선택 환경의 질량·마찰 재추첨, 관성이 최초 형상별 관성에서 계산됨을 PhysX readback으로 확인했다. 비선택 환경의 물체 상태·로봇 관절각·질량·관성·마찰은 그대로였다.
- 일정 변경10000 및 rewind0에서 목록이 초기화되고, 주기적 교체가 새 조건을 생성하는 것을 확인했다.
- 실제 timeout을 강제해 통합 reset과8개 Metrics 출력, 유한 관측·보상을 확인했다.
- 최초 GPU 실행은 EventManager가 `**scene_params`를 필수 파라미터로 해석해 생성 단계에서 실패했다. 실제 term signature를 명시적 인자로 변경하고 재실행해 통과했다.

이번 작업에서는 PPO 학습·2048환경 Collection Time·장기 다양성/성능을 측정하지 않았다. 사용자가 직접 비교할 예정이며 개선율을 주장하지 않는다. 기존 부모는 물성이 startup 고정이고 새 환경은 매 reset 물성이 달라지므로, 순수한 처리 시간 외 학습 분포 차이도 존재한다. 초기 각 그룹의8회 생성 및 커리큘럼 변경 직후는 캐시 충전 구간이다.

## 재현·산출물

workspace 루트에서 실행한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_grouped_reset_pool.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor.py -q -p no:cacheprovider

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_wrench_refactor_reset_probe.py --headless

python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-Refactor-Relative-IK-v0_2_1-Reset-Test \
  --num_envs 2048 --headless
```

GPU 결과: `outputs/relative_ik_reset_test_validation/result.json`. stdout: `/tmp/ik_reset_probe.log`. Collection 비교는 같은 환경 수·seed·학습 조건에서 수행한다.

최종 정적/문서 검사: 작업트리 변경 Python AST 통과, 변경 문서4개 math 검사 통과, 내부 링크193개 오류0, 코드/문서 저장소 `git diff --check` 통과.

## 사용자 평가 후 잠정 보류

2026-11-09 사용자는 Reset-Test 방식의 효과가 크지 않다고 평가해 잠정 보류했다. 구현·등록·학습 로그는 보존하며, 다음 v0_2_2 접촉 유지 실험은 Reset-Test가 아닌 일반 v0_2_1-Test를 부모로 사용한다. 이는 사용자 실험 평가이며 별도의 새 성능 측정을 수행한 것은 아니다.
