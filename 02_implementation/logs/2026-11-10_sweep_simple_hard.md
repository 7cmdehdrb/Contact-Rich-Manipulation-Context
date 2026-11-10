# 2026-11-10 Simple Hard 목표 샘플링

[환경 계약](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#hard-v0-공통-변경) · [현재 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)

## 요청과 해석

Simple-v1와 Simple-Prof-v1를 각각 계승한 Simple-Hard-v0, Simple-Prof-Hard-v0를 만든다. 변경은 목표 이동거리7–15cm와 DeadZone curriculum 삭제/0도 고정뿐이다.

방향별 최대 가능 거리 `L`이15cm 미만이면 사용자가 요청한 “가능한 최대 위치”를 그대로 선택한다. 따라서7–15cm 구간의 짧은 ray도7cm부터 `L` 사이를 무작위 선택하지 않고 `L`을 사용한다. `L<7cm` 역시 방향을 고정한 채 `L`을 사용한다. `L≥15cm`일 때만7–15cm 균등분포다.

## 변경 전후와 영향

- `SweepSimpleHardEnvCfg(SweepSimpleV1EnvCfg)`와 `SweepSimpleProfHardEnvCfg(SweepSimpleProfV1EnvCfg)`를 기존 `envs/sweep_simple_envs.py`에 추가했다. 부모 EnvCfg 정의는 유지했다.
- 두 자식은 같은 `SweepSimpleHardEventsCfg`, `SweepSimpleHardCurriculumCfg`를 사용한다. 목표6–12cm→7–15cm, DeadZone30도 시작 일정→0도 고정, 해당 curriculum term→None이다. startup geometry 함수만 Hard용 캐시 초기화로 교체하며 reset 함수는 그대로 `fast_reset_scene`이다.
- 보상·관측·제어·Scene·물리·종료·메트릭·나머지 curriculum은 부모와 같다. Simple-Hard는 접촉 유지 보상이 있는 Simple-v1 계약, Prof-Hard는 접촉 조건부 접근/방향 이탈이 있는 Prof-v1 계약이다. 두 환경 모두 이미 v1 Reach를 상속한다.
- PPO는 각 부모 runner를 직접 상속하고 experiment_name만 `inspire_sweep_simple_hard_v0`, `inspire_sweep_simple_prof_hard_v0`로 구분했다.
- Gym ID는 `Inspire-Sweep-Simple-Hard-v0`, `Inspire-Sweep-Simple-Prof-Hard-v0`다. runtime은 기존 `SweepSimpleEnv`를 재사용한다.

## 구조적 거리 산출

`mdp/common/sweep_simple.py`의 `HardCircleResetLayout`은 기존 CircleResetLayout의 목표 추출만 override한다. 타겟 BBOX에 이미 반영된 물체 스케일과 고정 yaw −pi/2를 적용해,2cm 선반 가장자리 여유를 만족하는 root 위치 하한·상한을 startup에서 계산한다. 중앙 spawn 반경2cm가 이 사각형 안에 있는지는 startup에서 한 번 확인한다. 최소7cm가 모든 방향에서 가능한지는 강제하지 않는다.

reset에서는 기존과 같이 난수4개로 초기 위치·방향·거리 난수를 생성한다. 방향의 부호에 따라 해당 X/Y 경계까지 거리를 나누고, 작은 교점 거리를 `L`로 사용한다. 임의의 연속 방향·초기 위치는 매 reset 새로 정해지므로 `L` 자체를 상수로 캐시하지 않는다. 대신 불변 geometry·footprint·safe domain을 캐시하고, `L`은 후보 생성 전에 직접 구한다. 목표가 유효할 때까지 재시도하는 구조가 아니다.

목표 sampler에는 Tensor bool/item/cpu readback이나 기하 재스캔이 없다. Python scalar 설정 비교는 잘못된 캐시 재사용을 막기 위해 남긴다. 기존 장애물 배치·IK의 성공 검사까지 제거한 것은 아니다. 변경된 목표가 RED와 장애물 배치, IK 방향, 최종 command에 동일하게 사용된다.

공유 코드의 최소 변경은 다음 두 가지다.

1. `CircleResetLayout.sample`에서 기존 free function을 호출하던 곳을 `self.sample_commands` 호출로 연결했다. 기본 메서드는 기존 free function을 그대로 호출한다. 기존 입력과 RNG에 대해 결과·RNG state가 bitwise 일치한다.
2. `initialize_fast_geometry`에 선택적 `layout_class`를 추가했다. 기본값은 기존 CircleResetLayout이므로 기존 환경은 그대로다. Hard startup wrapper만 HardCircleResetLayout을 전달하고 목표 설정으로 cache를 구성한다.

파일 이동이나 기존 알고리즘 복제는 없으며, 사용자 작업과 학습 로그는 보존했다.

## 최종 대조와 실행한 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_hard.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  src/inspire_sweep_baseline/tests/test_fast_reset.py -q -p no:cacheprovider
```

**78 passed, 2 skipped**, 11.67초.

- 두 자식의 전체 config를 부모와 대조했다. 차이는 startup 함수·거리/방향 params3개·DeadZone term 제거뿐이다. 직접 부모 관계·mutable 설정 격리·등록·PPO도 확인했다.
- cardinal Pull/Push/좌우, 최대13cm, 최소에도 못 미치는4cm,15cm 이상 가능 사례를 명시적 기대값으로 검사했다.
- 합성 target geometry4,096개 중 순서를 섞은3,072개에서 방향 보존·회전된 실제 BBOX 네 꼭짓점의 안전 경계·짧은 ray의 경계 도달을 독립 검사했다. 목표 sampler의 Tensor bool을 금지한 상태에서도 실행을 통과했다.
- 128개 전체 Fast 배치에서 장애물0–6 개수 보존·겹침 없음·선반 포함·변경 목표 RED 제외·같은 seed 재현성을 확인했다.
- startup cache 연결, 부분 env ID 선택, 설정 변경 시 stale cache 차단, 부모의 동일 난수 결과를 검사했다.
- 기존 Simple-v0/Prof-v0/v1 동등성, 접촉·Reach·종료·Fast reset/Warp CPU 회귀가 함께 통과했다.

초기 테스트는 config `to_dict()`가 callable을 문자열로 직렬화하는 것을 놓쳐 실패했다. live config의 callable identity를 검사하도록 테스트를 수정했고 최종 결과는 위와 같다. 생산 동작의 실패는 없었다.

skip은 opt-in 대규모 기하 stress와 native library path가 필요한 실제 USD IK 검사다. NVIDIA 드라이버 통신 불가(`nvidia-smi`)로 실제 PhysX/GPU reset-step·렌더·학습·Collection Time은 미검증이다. 캐시와 직접 계산 구조를 구현했지만 속도 개선 수치를 측정한 것은 아니다.

변경 관련 Python17개 파일 구문 compile, root/문서 저장소 `git diff --check`, 변경 Markdown4개 수식 검사 및 문서 링크 검사(errors0)를 통과했다.
