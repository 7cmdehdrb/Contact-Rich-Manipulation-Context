# Tactile 학습 시작의 미지원 GPU 접촉 필터 경고 수정

[로그 목록](README.md) · [Tactile 환경](../environments/TACTILE_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기록일: 2026-10-15. 사용자가 `Isaac-Inspire-Sweep-Baseline-Tactile-v0` 학습 시작 시 대량 경고를 보고하고 Tactile을 유지하면서 수정하도록 요청했다. 기준 workspace commit은 `9e91d0e255981fc7a1011480656a402b6c014488`, 문서 submodule commit은 `87b1a2dab7feb7947152b6cb6e7b1b73a051ae78`다. 기존 문서 변경·사용자 run은 보존했다.

## 관찰과 원인

첨부 텍스트에는 `/World/envs/env_2009/Shelf`부터 `env_2047/Shelf`까지 `GPU contact filter for collider ... is not supported`가 반복되고, 마지막에 EEF 디버그 marker의 `FabricManager::initializePointInstancer mismatched prototypes`가 있다. 원본 첨부는 사용자 제공 파일이며 별도로 복제하지 않았다.

기존 Tactile Scene은 부모 body 12개 각각의 ContactSensor에 실린더·`Shelf.*`·ground를 filter로 등록했다. 실제 GPU backend가 해당 Shelf collider를 상세 접촉 filter로 지원하지 않아 환경별·관측 view별로 경고가 증폭된다. 17개 접촉 채널 자체의 개수 문제가 아니다. 해당 shelf USD는 외부 Nucleus 경로이므로 이 머신에서 mesh 내부 구조를 직접 확인하지 않았고 특정 collider 종류라고 단정하지 않았다.

NVIDIA의 [동일 유형의 imported USD filter 문제](https://github.com/isaac-sim/IsaacLab/issues/4108)에서는 형상 종류에 따른 GPU contact filter 지원 차이와 primitive collider 대비 차이를 설명한다. [GroundPlane 상세 접촉 문제](https://github.com/isaac-sim/IsaacLab/issues/2282)도 별도 보고돼 있다. 로컬 설치 API의 `RigidContactView.get_contact_data()`는 valid filter를 요구하므로 모든 filter를 없앤 뒤 그대로 사용하는 것도 해결책이 아니다.

## 재현 가능한 회귀 검사와 수정

GPU가 없는 현재 머신에서는 실제 tensor backend를 실행하지 못한다. 대신 실제 production Cfg를 생성하고 첨부의 미지원 collider 경로가 filter pattern에 매칭되는지 검사하는 CPU 회귀 검사를 추가했다. 이는 경고의 원인이 되는 등록 요청을 검증하는 것이며 PhysX 실행을 재현했다고 주장하지 않는다.

최초 검사는 기존 작업트리의 `omni_env_cfg.py`에 있는 `@configclass질` 오타 때문에 shared fixture가 생성되지 않았다. 정의되지 않은 decorator 이름을 원래 `@configclass`로 복구했다. 이 파일의 threshold 등 환경 값은 변경하지 않았다. 이후 회귀 검사는 미지원 filter와 디버그 표시 조건에서 **2 failed**로 실제 실패했다.

수정 내용:

1. 부모 영역 분류 filter를 GPU 지원 primitive인 `{ENV_REGEX_NS}/mass_cylinder` 하나로 제한한다. Shelf·ground filter를 등록하지 않는다.
2. 17개 직접 pad ContactSensor는 기존 unfiltered 상태를 유지한다. 실린더의 접촉점은 12개 부모에서 계속 수집해 17개 영역에 각각 분류한다. Policy 입력 57D, tactile 17D, 채널 순서·임계값·reset masking과 직접/분류 OR는 동일하다.
3. Tactile Scene의 EEF frame `debug_vis`만 False로 설정한다. Frame target과 계산·F/T 입력은 유지하고 Baseline의 debug 설정은 변경하지 않는다.

원본 USD·URDF·mesh·collider 수·접촉 파라미터·로봇 질량·관절·제어·보상·종료 조건은 바꾸지 않았다. 경고 수준을 낮추거나 로그를 필터링해 문제를 숨기지 않았다.

### 센싱 범위의 명시적 제한

직접 pad가 접촉하면 상대가 선반·바닥이어도 직접 bit를 읽는다. 부모 링크의 실린더 접촉은 기존처럼 17개 영역으로 분류한다. 다만 부모 링크에만 발생하는 선반·바닥 접촉을 가려진 pad에 배정하지는 않는다. 미지원 GPU 경로의 0/NaN 데이터를 유효한 센서 출력이라고 보장하지 않으며, 이를 대체하기 위해 부모 전체 힘을 모든 pad에 복제하거나 물리 형상을 바꾸지 않았다. 이 제한은 패키지 README·활성 환경·Tactile 설명에도 반영했다.

## 실제 검증

Workspace 루트에서 다음을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_tactile_gpu_filters.py \
  src/inspire_sweep_baseline/tests/test_tactile_configuration.py \
  src/inspire_sweep_baseline/tests/test_tactile_observations.py \
  src/inspire_sweep_baseline/tests/test_tactile_projection.py \
  src/inspire_sweep_baseline/tests/test_tactile_geometry.py
```

결과: **60 passed**. 이 중 새 one-filter 통합 검사는 17개 환경 각각에서 서로 다른 영역의 원시 실린더 접촉을 production reader에 넣어 출력이 정확히 `eye(17)`임을 확인한다. 모든 센서를 0으로 만들거나 합쳐 경고만 제거한 것이 아니다. 기존 USD 17개 센서 frame과 source hash 검사, 57D/41D 격리와 reset 처리도 통과했다.

전체 CPU suite의 최초 결과는 175 passed, 17 subtests passed, 1 failed였다. 실패는 Tactile 수정과 별개의 `test_v1_velocity_boundary_and_config_isolation`에서 현재 Omni v1 threshold 3.0을 기존 테스트가 100.0으로 기대하는 불일치였다. 사용자 threshold는 변경하지 않고, 테스트가 현재 설정의 양·음 경계값과 v0 격리를 검증하도록 고쳤다. 최종 전체 결과는 **176 passed, 17 subtests passed**(11.90초)다. 변경 Markdown 수식 검사 5개 파일 통과, 내부·workspace 링크 검사 errors 0, workspace·문서 submodule `git diff --check` 통과. `build_tactile_regions.py --check`도 17개 영역·12개 부모·원본 source hash 일치로 통과했다. `nvidia-smi`는 NVIDIA driver 통신 실패(exit 9)였다. 실제 GPU warning-free 시작·train/play·FPS는 이 머신에서 확인하지 못했다.

## 다시 실행할 명령

이미 시작한 프로세스에는 ContactSensor view와 filter가 남아 있으므로 새 프로세스로 시작한다. 다음 smoke 명령은 안내이며 이번 작업에서 실행하지 않았다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Sweep-Baseline-Tactile-v0 \
  --num_envs 16 --max_iterations 2 --run_name tactile17_filter_fix_smoke --headless
```

정상 생성 확인 후 기존 2048-env 학습 명령을 사용한다. 원본 checkpoint·run·user asset은 변경하지 않았다.
