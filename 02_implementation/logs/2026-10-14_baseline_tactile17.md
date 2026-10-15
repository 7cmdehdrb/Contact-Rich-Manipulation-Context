# Baseline을 상속한 17채널 Tactile 환경

[로그 목록](README.md) · [환경 구성](../environments/TACTILE_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [기존 센서 조사](2026-10-14_contact_sensor_contract.md)

기록일: 2026-10-14. 사용자 요구는 기존 환경을 유지하면서 Hand의 센서 영역별 독립 Binary 입력을 구현하고, mesh 증가·큰 형상 변형으로 physics 비용이나 접촉 양상을 크게 바꾸지 않는 것이다.

## 기준과 구현

Workspace 시작 commit은 `f240c64f706a9911ea143528f54001211058f11b`다. 작업 시작 시 문서 submodule의 이전 로그·문서 변경을 보존했다. Submodule commit은 별도이며 새 commit·push는 수행하지 않았다.

Task는 `Isaac-Inspire-Sweep-Baseline-Tactile-v0`, 환경은 기존 `InspireSweepEnv → ManagerBasedRLEnv`, Cfg는 `InspireSweepTactileEnvCfg → InspireSweepEnvCfg → ManagerBasedRLEnvCfg`다. PPO는 `InspireSweepTactilePPORunnerCfg → InspireSweepPPORunnerCfg`로 로그 이름만 변경한다. 입력 policy는 57D(기존 41D의 tactile 1D를 17D로 교체), Actor/Critic 동일하며 Action은 8D다. Baseline의 로봇·제어·관측의 나머지 항·reset·물체 질량·스폰·보상·종료를 상속한다.

변경 파일은 새 `tactile_env_cfg.py`, `mdp/tactile_observations.py`, `assets/tactile_regions.py`, 관측용 JSON, PPO subclass, metadata 생성·검사 도구 및 테스트다. 기존 `__init__.py`에 task 등록을 추가하고 `pyproject.toml`에 새 JSON package data를 포함했다. 기존 환경 설정과 원본 USD·URDF·mesh는 수정하지 않았다.

17개 raw pad를 연결하는 것만으로는 buried pad 접촉을 놓칠 수 있어 원본 collision hull을 추가 조사했다. Palm의 얕은 lip은 미세 이동으로 노출되지만 중심을 비롯한 대부분의 면은 가려져 있다. 작은 오프셋만 적용하는 방법으로 사용자의 전체 센서 영역 목적을 만족한다고 주장하지 않았다. Collider를 바꾸는 대신 부모의 실제 접촉점을 기존 pad footprint에 분류하는 관측 전용 방법을 추가했다.

17개 pad의 직접 normal contact force와 부모 12개의 원시 contact point를 사용한다. 원본 mesh의 2D polygon·유한 outward depth 범위·법선 방향 조건을 적용하고 다른 영역 사이에 부모 전체 힘을 broadcast하지 않는다. Body 순서를 이름으로 고정하고 reset 행을 먼저 마스킹한다. 직접·분류 Binary는 OR하며 기본 threshold는 0.05 N다. 필터와 세부 의미는 [환경 설명](../environments/TACTILE_ENVIRONMENT.md)에 기록했다.

## 실제 실행한 검증

Workspace 루트에서 다음 CPU 검증을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_tactile_configuration.py \
  src/inspire_sweep_baseline/tests/test_tactile_observations.py \
  src/inspire_sweep_baseline/tests/test_tactile_projection.py \
  src/inspire_sweep_baseline/tests/test_tactile_geometry.py

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider

/home/min/miniconda3/envs/newton/bin/python -B \
  src/inspire_sweep_baseline/scripts/build_tactile_regions.py --check

git diff -- src/inspire_sweep_baseline/inspire_sweep_baseline/env_cfg.py \
  src/inspire_sweep_baseline/inspire_sweep_baseline/assets/robot.py \
  src/inspire_sweep_baseline/inspire_sweep_baseline/assets/data/ur5e_inspire_usd

nvidia-smi
```

실제 실행 결과: 새 기능 관련 **57 passed**. 전체 CPU 테스트는 **173 passed, 17 subtests passed**(11.95초)였다. 변경 Markdown 수식 검사 8개 파일 통과, 내부·workspace 링크 검사 errors 0, workspace와 문서 submodule의 `git diff --check`도 통과했다. Metadata 검사에서는 17개 영역·12개 부모·원본 USD 5개 layer 해시가 일치했다. Baseline 설정·로봇 코드·원본 USD 경로의 diff는 비어 있다. `nvidia-smi`는 NVIDIA driver 통신 실패(exit 9)였다.

검증 항목:

- 17개 pad의 one-hot 활성화, body discovery 순서가 바뀌어도 동일 policy index.
- 동일 부모의 서로 다른 센서 영역에 동시 접촉이 있을 때 별도 bit 유지, 영역 밖·뒤쪽·접선 방향의 접촉은 배정하지 않음.
- 실제 원본 USD의 모든 17개 sensor frame과 인접 센서 배치를 사용해 부모 hull 표면의 개별 검증점이 정확히 자기 채널만 활성화함. 모든 채널의 동시 접촉도 독립 출력.
- Reset 행의 stale NaN force·point·pose 차단, 다른 env/filter slice 보존, 유효하지 않은 contact buffer 오류.
- 57D policy 및 실제 설치된 RSL MLP의 57D→8D 출력, 기존 Baseline 41D·PPO 수치·physics 설정 유지와 인스턴스 격리.
- 원본 USD 5개 해시의 실행 전후 동일성, metadata의 source hash 일치.

개발 중 빈 CPU contact fixture의 shape 처리와 packed buffer의 empty 조건 실패를 수정해 관련 검사를 통과시켰다. Runtime은 실제 접촉이 있는 부모의 포인트만 처리하고 부모 count를 한 번에 읽는다. Read-only review의 합성 CPU 측정(4 threads, backend 취득 제외)에서는 4,096 env의 빈 접촉 분류 약 0.70 ms, 두 부모에 env당 두 접촉점인 경우 약 6.03 ms였다. GPU나 simulator의 전체 FPS 수치가 아니다.

## 미검증 범위와 실행

현재 머신에서 GPU simulator 생성·PhysX contact/filter 실제 응답·각 영역의 물리 접촉·학습·정책 재생·end-to-end 속도는 실행하지 못했다. 원본 physics geometry 유지와 CPU 영역 분류 검증을 실제 simulation 성공으로 해석하지 않는다. 실행 명령·자산 설정·checkpoint 입력 차원은 [환경 설명](../environments/TACTILE_ENVIRONMENT.md)을 따른다.

새 task를 등록·검증했으며 train/play 또는 checkpoint를 생성하지 않았다. 기존 41D checkpoint는 새 57D 입력에 그대로 사용할 수 없다. GPU에서 첫 생성과 영역별 접촉·속도를 확인하는 후속 검증이 필요하다.
