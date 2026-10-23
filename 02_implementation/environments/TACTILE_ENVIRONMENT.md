# Baseline Tactile: 17개 독립 Binary 영역

[구현 안내](../README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [구현·검증 로그](../logs/2026-10-14_baseline_tactile17.md)

기준일: 2026-10-14. `Isaac-Inspire-Sweep-Baseline-Tactile-v0`는 Baseline을 상속하는 별도 task다. 기존 환경과 원본 자산을 보존하면서 Hand의 실제 센서 영역 17개를 독립 Binary 관측으로 제공한다. CPU·USD 검증과 실제 GPU 접촉 검증을 구분한다.

## 상속과 보존 범위

`InspireSweepTactileEnvCfg → InspireSweepEnvCfg → ManagerBasedRLEnvCfg`. Runtime은 기존 `InspireSweepEnv → ManagerBasedRLEnv`다. [tactile_env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_envs.py)의 Scene·Observation subclass만 다르다. PPO는 `InspireSweepTactilePPORunnerCfg → InspireSweepPPORunnerCfg`로 수치를 그대로 상속하고 로그 폴더 이름만 바꾼다.

로봇·선반·실린더의 형상, mesh·rigid body·collider 수, 원본 USD·URDF, mass/inertia, articulation·joint·actuator, friction/contact offset, reset·스폰·좌우 18 cm 목표, 보상·종료 조건은 Baseline과 같다. Arm Joint Position 6D + Hand 2D, 50 Hz 제어, 10초 제한과 현재 물체 위치 관측도 유지한다. 기존 Baseline은 41D이며 새 환경은 57D다. 이 57D는 발표의 Cartesian/OSC 설계와 별개이고 최종 Blind 관측 계약으로 해석하지 않는다.

원본 `envs/sweep_envs.py`, `assets/robot.py`, USD layer와 mesh 파일은 수정하지 않았다. 추가 데이터인 `assets/data/tactile_regions.json`은 관측 영역을 설명하는 metadata이며 physics geometry로 사용하지 않는다.

## 센서 영역과 출력 순서

`PALM_SENSOR_BODY_NAMES`의 순서를 policy 계약으로 사용한다. PhysX가 반환하는 body 순서가 달라도 이름으로 한 번 정렬해 동일한 채널을 유지한다. 실제 자산의 수는 17개이며 각 링크에 독립 collider가 있다.

| 인덱스 | 센서 body | 개수 |
| --- | --- | ---: |
| 0 | `inspire_palm_force_sensor` | 1 |
| 1–4 | `inspire_thumb_force_sensor_1` … `_4` | 4 |
| 5–7 | `inspire_index_force_sensor_1` … `_3` | 3 |
| 8–10 | `inspire_middle_force_sensor_1` … `_3` | 3 |
| 11–13 | `inspire_ring_force_sensor_1` … `_3` | 3 |
| 14–16 | `inspire_little_force_sensor_1` … `_3` | 3 |

출력은 shape `(num_envs, 17)`, dtype float32, 값은 0/1이다. 전체 policy의 앞 34D는 Baseline과 같고, 다음 17D가 tactile, 마지막 6D가 EEF F/T다. Actor/Critic 모두 같은 57D를 받으며 Action은 8D다. 기존 41D checkpoint를 그대로 로드하는 계약이 아니므로 새 학습 결과를 사용한다.

## 직접 패드 힘과 부모 접촉점 분류

기존 USD의 부모 손 mesh는 convexHull collider다. 이 hull이 패드 일부를 덮는다. 예를 들어 palm 중심은 원래 패드 최상단보다 부모 접촉면이 약 5.16 mm 밖에 있고, 일부 손가락 2번 패드는 약 1.18–1.53 mm 안에 묻혀 있다. 1.5 mm 정도 이동만으로 palm의 원래 영역 전체를 노출할 수 없어, 자산 이동·새 collider 추가를 선택하지 않았다.

새 환경의 `hand_tactile` ContactSensor는 정확히 17개 패드 body를 선택해 개별 `net_forces_w`를 읽는다. 이 힘은 서로 다른 패드 사이에서 합치지 않는다. 가려진 영역의 판정을 보완하기 위해 부모 body 12개에 관측용 단일-body ContactSensor view를 각각 만든다. **2026-10-15 수정 후 필터는 `{ENV_REGEX_NS}/mass_cylinder` 하나만 사용한다.** 사용자 실행에서 선반 필터가 `GPU contact filter ... is not supported` 경고를 발생시켜 선반·바닥의 미지원 상세 접촉 필터를 제거했다. 경고 로그를 숨기거나 pad 센서를 끈 변경이 아니다. [수정·검증 로그](../logs/2026-10-15_tactile_gpu_filter_fix.md)를 참고한다.

[ProjectedTactileContactBits](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/tactile_observations.py)는 각 부모의 **원시 개별 접촉점**을 읽는다. 평균 접촉점이나 부모 전체의 힘을 모든 센서에 복제하지 않는다. 접촉점을 현재 센서 body 좌표로 변환하고, 다음 조건을 충족한 원래 패드 영역에만 배정한다.

- 원본 pad collision mesh를 sensor-local XY에 투영한 convex polygon 안에 있을 것. 경계 여유는 0.5 mm다.
- 원래 pad의 outward 면부터 부모 collider의 바깥면까지의 유한 +Z 범위 안에 있을 것. 깊이 범위도 원본 geometry에서 계산한다.
- 접촉 법선이 해당 센서의 표면에 거의 접선 방향이 아닐 것(`abs(local_normal_z) >= 0.2`). 앞/뒤 면 구분은 Z 범위로 처리한다.

경계가 겹치는 경우 정규화된 XY 중심 거리로 하나의 영역에만 배정한다. 같은 부모에 서로 다른 영역의 접촉점이 여러 개 있으면 각각의 채널을 활성화할 수 있다. 영역 밖의 접촉점은 어떤 채널에도 배정하지 않는다. 이는 원래 sensor 영역을 기존 실제 접촉면에 대응시키는 가상 tactile 모델이며 압력 분포·패드 변형·하중 전달 모델은 아니다.

영역별 분류된 법선 힘을 합산한 norm과 직접 pad의 법선 힘 norm을 각각 임계값과 비교하고 Binary를 OR한다. 서로 반대인 직접·분류 힘이 이미 활성인 센서를 꺼버리지 않도록 두 신호를 벡터로 상쇄하지 않는다. 기본 임계값은 0.05 N다. 따라서 아주 약한 접촉은 0일 수 있으며, 기하학적 접촉 자체의 Boolean과 구분한다. 직접 pad 읽기는 unfiltered이고, 부모 영역 분류는 위 필터에 포함된 상대 물체에 한정된다.

현재 보장하는 모델 범위는 17개 직접 pad의 모든 상대 물체 접촉과, 실린더에 대한 17개 부모 영역 분류다. 부모 링크에만 발생한 선반·바닥 접촉을 가려진 pad에 배정하지 않는다. 이 경로의 완전한 선반·바닥 커버리지에는 GPU에서 지원되는 별도 접촉점 수집 방식이 필요하며, 부모 net force를 모든 pad에 복제하거나 근거 없는 접촉점을 만들어 대체하지 않는다.

실제 Binary 임계값은 `observations.policy.tactile.params["threshold_n"]`다. `ContactSensorCfg.force_threshold`는 air/contact time tracking에 쓰이는 설정으로, 이 환경의 Binary 임계값을 자동 변경하지 않는다.

Reset 직후에는 기존 `sensor_data_fresh` 규칙으로 해당 행의 직접 힘과 원시 접촉점을 모두 차단한다. 다른 환경의 접촉 상태는 유지한다. NaN·잘못된 body 구성·잘못된 contact buffer는 명시적인 오류로 처리한다.

## 연산과 성능 확인 범위

Physics collider·triangle·joint 수는 늘리지 않았다. 관측용 view와 접촉점 분류 연산은 추가된다. 영역 polygon과 body index는 초기화 때 캐시한다. 환경별 Python/NumPy 반복을 사용하지 않고 Torch로 접촉점과 영역을 배치 처리하며, 실제 접촉이 있는 부모만 분류한다. 부모별 contact count를 한 번에 읽어 GPU host 동기화를 부모 수만큼 반복하지 않는다.

Tactile 환경의 `scene.ee_frame.debug_vis=False`로 EEF 좌표축용 PointInstancer 생성을 피한다. 원본 Baseline의 표시 설정은 유지하며 `target_frames`와 frame 데이터·관측 계산은 동일하다. 이는 첨부 경고 중 `FabricManager::initializePointInstancer mismatched prototypes`를 일으킨 선택적 디버그 표시 경로를 끄는 조치다.

원시 접촉점 buffer 설정은 부모당 `max_contact_data_count_per_prim=16`이며 실제 global capacity는 이 값에 환경 수를 곱한 크기다. Buffer가 가득 찼거나 범위를 벗어나면 조용히 접촉을 버리지 않고 오류를 발생시킨다. 더 접촉이 많은 장면에서는 별도 설정과 성능 확인이 필요하다.

현재 GPU simulator에서 센서 생성·필터 일치·각 영역 실제 응답·end-to-end FPS를 측정하지 못했다. 따라서 물리 형상 보존과 CPU 관측 검증은 확인했지만 실행 속도 변화의 크기까지 확정하지 않는다. 실물 tactile 영역·해상도·센서 특성의 검증도 별도다.

## 실행과 검증 도구

Workspace 루트의 Isaac Lab 환경에서 실행한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Sweep-Baseline-Tactile-v0 \
  --num_envs 2048 --sweep-direction both --run_name tactile17 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Sweep-Baseline-Tactile-v0 \
  --num_envs 1 --checkpoint "<57D_tactile_checkpoint.pt>" --real-time
```

로그는 `logs/rsl_rl/inspire_sweep_tactile/<timestamp>_tactile17`에 저장한다. 선반 USD 경로는 기존 `INSPIRE_SWEEP_SHELF_USD_PATH` 설정을 따른다.

관측용 metadata를 원본 USD와 대조하는 읽기 전용 검사는 다음과 같다. 이 도구는 pxr·NumPy·SciPy가 있는 CPU Python을 사용하며 Isaac Sim을 시작하거나 원본 자산을 수정하지 않는다.

```bash
/home/min/miniconda3/envs/newton/bin/python -B \
  src/inspire_sweep_baseline/scripts/build_tactile_regions.py --check
```

구체적인 CPU 테스트·원본 USD 해시 검사·미실행 항목은 [개발 로그](../logs/2026-10-14_baseline_tactile17.md)를 따른다.
