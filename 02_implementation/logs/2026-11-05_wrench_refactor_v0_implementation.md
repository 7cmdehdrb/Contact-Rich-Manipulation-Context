# 2026-11-05 Wrench Refactor v0 구현·검증

[최종 환경 계약과 전체 대조표](../environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md).

## 요청·기준·작업트리 보존

사용자 요청은 `Inspire-Wrench-v0_2` 문제를 개선한 독립 CFG 환경이다. workspace commit `c57087aa629ec0d7205a37f44dc3a595ea7974ec`, 문서 submodule commit `c81a0bfc082686c75a2be2c984a229bc6498322c` 기준으로 작업했다. 시작부터 패키지 README, 문서 인계·안내·기존 Wrench 문서6개가 수정되어 있었고 `docs/plan/PLAN12.md`, family 문서/로그가 미추적 상태였다. 이를 보존하고 새 환경 파일과 필요한 색인 문단만 추가했다. submodule commit, branch, 사용자 변경, 학습 로그를 변경/정리하지 않았다.

사용자 확인:

1. 오타 `Insire` 대신 `Inspire-Wrench-Refactor-v0` 등록.
2. 12시/6시=선반 local ±X, 방향 균등 + 방향별 유효 거리 균등.
3. 오른손은 ZIP 원본 사용. 활성 패키지 안에서만 찾았던 초기 탐색 누락을 정정하고 `/tmp/inspire_urdf_right_with_force_sensor.zip` 확인.
4. OSC 명령 정규화 요청을 다시 정정한 **최종 지시: 출력 토크 사용**.
5. 목표3cm 내부 접촉 보상도 EEF14cm 미만에서만 지급.

## 확인한 문제와 구현 선택

`envs/wrench_envs.py`의 v0/v0_1/v0_2/v0_3/v0_4/v1/v2 및 역할별 Wrench 파일 전부와 실제 호출되는 이전 계산 함수만 확인했다. 전체 과거 환경 문서를 연쇄적으로 읽지 않았다. 모든 ‘유지’ 주장에는 최종 환경 문서의 계열 근거를 기재했다.

- v0_2의 실제 물체는 타겟+9장애물=10개였다.16개는 관측 슬롯이었다. 새 환경은8종×2장애물+원통타겟=17개다.
- v0_2의 크기/물성은 이미 startup 고정이었다. 새 환경은 타입 roster까지 고정하고, 질량/마찰을 물체별 균등 분포로 명시한다.
- 기존 `sample_revision_commands`를 CPU에서 직접 실행했다. seed42, 중앙반경0, 원통10,000개에서 좌우4909/5091, 거리 min/max≈0.15m, 표준편차6.1e−9였다. `assert distance.std()>0.02`는 실패하여 거리 균등 결여를 재현했다. ±X deadzone의 좌우 비대칭 금지 조건은 없었다. 학습된 정책이 왼쪽으로 덜 미는 원인은 재현/확정하지 못했다.
- 기존의 거대 stage bank 대신 reset 때 목표/거리·개수·후보를 추첨한다. 최초 spawn에서 저장된 bounds와 bottom z를 재사용한다. OBB는 선택된 최대6후보만 대상으로 한다. 재시도는 목표/개수를 유지하고 실패 시 명시적으로 예외를 낸다. GPU reset 성능 보장은 하지 않는다.
- 새 raw74D, 두 모델 모두 encoder후90D. Critic은 target 슬롯을 교체한다. 기존 Critic obstacle swap10%도 요청된 무변조 조건에 맞춰0으로 변경한다.
- 오른손 모델의 실제 형상·joint axis·관성을 이식한다. 공유 제어/센서 식의 내부 이름 계약을 유지하려고 `inspire_left_*` 호환 슬롯에 오른손 데이터를 넣었으며 이를 자산 customData와 계약에 명시했다. 모델을 왼손 그대로 두거나 음수 scale로 반사하지 않았다.
- 손등은 원본 pad footprint와 parent convex hull의 반대쪽 실제 표면으로 정의했다. 같은 pair의 개별 접촉점을 모두 분류하고 force magnitude를 누적한다. 새 collider/질량은 없다. 물체17개가 projection filter이며 선반/지면 투영은 미지원이다.
- contact 목표 내부 높이 예외를 제거하고 목표 경계는 inclusive3cm로 맞췄다. 기존 v0_2 함수는 보존하고 새 전용 term에 적용했다.

## 변경 전후·영향·최종 대조

새 역할별 `wrench_refactor.py`, EnvCfg·runtime·model·PPO·USD/metadata·builder·검증 파일을 추가하고 패키지 등록을 추가했다. 기존 Wrench 파일에는 변경이 없다. [전체 계약](../environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md)의 등록/Scene/reset/관측/제어/PPO/보상15행/종료6행/커리큘럼을 요청과 대조했다.

보존 항은 Reaching, Hold 수식, 관절속도 비용, tilt, obstacle displacement, shelf, success bonus, wrench-change 식·수치이며 높이 gate만 요청대로 바뀐다. 지수 거리식은 v0/v1/v2에서 재사용하고 weight5로 변경한다. v0_2 cosine은 가져오지 않는다. Arm rate는 v0_3/v0_4 출력 토크 정규화다. Hand는 실제0–1 clamp 명령 차이로 변경한다. 최초진입+15 무감쇠, obstacle free30N, speed/acceleration 비용·speed 종료 제거, arm velocity1, unconditional timeout, 방향 외 커리큘럼 제거를 확인했다.

미요청 구조 재편·기존 함수 변경은 없으며 기존 사용자 README/문서 변경을 되돌리지 않았다. 환경문서·개발로그·현재 인계·활성 환경 안내·패키지 README 링크를 추가한다.

## 실제 검증

작업 디렉터리는 workspace 루트다. CPU 테스트용 Python은 `/home/min/miniconda3/envs/env_isaaclab/bin/python`, USD-only Python은 `/home/min/miniconda3/envs/newton/bin/python`이다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_wrench_refactor.py \
  src/inspire_sweep_baseline/tests/test_wrench.py \
  src/inspire_sweep_baseline/tests/test_wrench_v0_1.py \
  src/inspire_sweep_baseline/tests/test_wrench_v0_2.py \
  src/inspire_sweep_baseline/tests/test_wrench_v0_3.py \
  src/inspire_sweep_baseline/tests/test_wrench_v1.py \
  src/inspire_sweep_baseline/tests/test_tactile_projection.py \
  src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py

/home/min/miniconda3/envs/newton/bin/python \
  src/inspire_sweep_baseline/tests/_wrench_refactor_asset_probe.py

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_wrench_refactor_probe.py \
  --num_envs 4 --headless --device cpu --config-only
```

- 새 CPU20개 통과:7개 deadzone 각50,000표본 각도/조건부 거리 검증, exact counts/OBB/bottom/parking, partial/empty reset, 균등 startup 물성·초기화 중복 방지, 보상 경계/부분reset/dt, 독립 CFG 및 실제 post-init 구성, 실제 오른손17쌍 표면, 동일 물체 복수접촉·반대 힘 상쇄 방지, RSL-RL PPO의 두 encoder update·JIT·Actor 비특권 분리.
- 기존 Wrench 전체103개 통과. 새20개와 tactile/F/T 회귀를 합친 **최종156개 통과(20.77초)**. 결과는 `outputs/wrench_refactor_validation/tests.txt`에 저장했다.
- USD-only: 오른손30강체/29관절 frame 정합, 각 물체 positive mass/inertia, 활성 collider가 오른손 mesh 하나임을 확인. 실제 assembly 함수의 F/T child identity frame 확인.
- 실제 Isaac Lab/Sim import 및 EnvCfg·PPO 인스턴스 생성 성공.17개 물체/관측 routing/목표반경0.03 확인. `outputs/wrench_refactor_validation/config_import.log`.
- 보수적8종 footprint 범위와0.9–1.1 scale을 사용한 CPU2048장면 stress: Gray3/White3 모두 요청, α0° 및30°에서 요청 수 전부 배치. CPU2thread 약3.52초/3.48초. 실제 YCB USD/PhysX2048환경 검증이나 GPU 성능 수치가 아니다.
- 첫 새 테스트 실행에서 CPU harness의 `isaaclab.utils.noise` 미연결을 확인하여 실제 noise 모듈 연결로 수정했다. USD probe의 AST harness annotation 누락도 수정했다. 제품 코드 오류와 test harness 오류를 구분했다.

실제 물리 시도 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_wrench_refactor_probe.py --num_envs 4 --headless
```

`nvidia-smi`는 driver 연결 실패, Isaac Sim은 `NVML_ERROR_DRIVER_NOT_LOADED`, `cudaErrorNoDevice`, `Unable to create PxCudaContextManager`를 출력했다. Kit 종료 과정도 segmentation fault(exit139)가 났다. 환경 rollout 성공 산출물은 없다. 로그는 `outputs/wrench_refactor_validation/isaac_probe.log`다. config-only 검사는 시뮬레이션 생성 없이 실제 설정 import를 끝낸 뒤 종료하여 driverless Kit shutdown 오류를 피한다.

## 미검증 범위·후속 확인

GPU 호스트에서 실제4/64환경 초기화·부분reset·rollout, 오른손 무접촉 동작의 중력/관성 wrench residual, 물체 동일 pair의 앞/뒤/복수점 실제 접촉, PhysX contact buffer 용량, scale 양끝의 바닥 정렬을 검사해야 한다. 이어2048환경 처리량과 `train.py` 짧은 PPO checkpoint를 확인한다. 장기 성공률·왼쪽 행동 빈도는 훈련/정책 평가가 필요하다.

범위 밖 데이터/코드/로그 삭제, 드라이버 설정 변경, 학습 실행은 하지 않았다. PhysX 실행 불가를 CPU 정적/수학 검사로 대체하여 검증 완료라고 표기하지 않는다.

## 최종 문서·보존 검사

변경 문서4개의 Markdown math/상대 링크 검사 통과(내부104, 외부1, 오류0), workspace와 문서 저장소의 `git diff --check` 통과. 신규 Python20파일 AST 파싱 통과. 기존 활성 패키지의 추적 코드 변경은 등록용 `__init__.py`뿐이고 나머지 구현은 새 파일이다. 기존 Wrench CFG·runtime·함수·왼손 USD는 작업 전후 동일하다. README와 인계/안내의 사용자 선행 변경은 유지한 채 Refactor 안내만 앞에 추가했다.

최종 확대 검사: README까지5파일 math 검사 통과. 링크 검사에서 README의 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 참조1건이 누락 경로로 보고됐다. 이 링크는 workspace HEAD에도 존재하며 이번 신규 링크가 아니므로 요청 밖의 기존 문서를 수정하지 않았다. 신규 문서/인계/안내4파일 링크 오류는0이다. 기존 Wrench19개 코드 파일은 `git show HEAD:<path>`의 bytes와 전부 동일함을 별도로 확인했다.


## 후속 질량·EEF·촉각·재구성 명세

동일 환경에 대한 사용자 추가 요청은 [후속 수정 기록](2026-11-05_wrench_refactor_mass_eef_spec.md)을 따른다. 선반30kg/손790g/EEF OSC/촉각.05N 및159개CPU검증을 반영했으며 위 최초 작업 시점의156개 기록은 당시 결과로 보존한다.
