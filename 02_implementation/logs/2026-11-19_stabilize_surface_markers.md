# Test 대표 표면점 시각화와 비활성 물체 간섭 검토

## 요청과 변경 범위

사용자 요청: `Inspire-Stabilize-Sweep-v0-Test`, `Inspire-Sweep-Only-v0-Test`에서 정책에 주는 물체 대표점을 물리 상호작용 없는 빨간 점으로 표시하고 비활성 물체의 다른 환경 간섭을 검토한다. 기준 코드 HEAD는 `53006da77bc89e284abda04c04dfc11b866582e7`이며 문서 서브모듈의 기존 변경을 보존했다.

기존에는 대표점 표시가 없었다. 이제 Test 두 설정만 `debug_surface_points=True`이며 일반 부모는 False다. runtime은 reset 완료 후 `/Visuals/StabilizeSweep/surface_points`에 반지름 6mm 빨간 구형 마커를 갱신한다. 강체·충돌 속성이 없는 VisualizationMarkers를 사용한다. GUI 또는 `rgb_array` 렌더 모드에서만 생성하며 일반 headless 학습에서는 생성하지 않는다. 끄려면 실행 시 `env.debug_surface_points=False`를 지정한다.

타겟 `_surface_target_w`와 유효 mask가 참인 `_surface_obstacles_w`를 그대로 표시한다. reset이 완료되지 않은 환경, padding과 비활성 대기 물체는 제외한다. 정책 입력은 이 세계 좌표를 현재 EEF 좌표로 변환한다. 대표점은 초기 관측이므로 물체가 움직여도 점은 세계 좌표에서 고정되고 다음 reset 때 바뀐다. 부분 reset에서도 전체 최신 캐시를 표시한다. 대표점 재추출이나 물체 중심 추적을 추가하지 않았다.

## 간섭 검토

- Scene의 `filter_collisions=True`, `replicate_physics=False`에 따라 InteractiveScene이 환경별 CollisionGroup을 생성한다. GPU 환경 ID 기능만 가정하지 않고 실제 USD의 invert filter와 환경별 include/self-group 관계를 검사했다. 각 환경 밖으로 대기 물체를 옮겨도 prim의 소속 환경은 유지되므로 다른 환경의 로봇·선반·물체와 물리 충돌하지 않는다.
- 대기 위치는 로봇 작업 영역 밖 45cm 격자이며 최대 물체 반경 및 로봇 도달 거리 guard가 있다. 중력을 끄고 속도를 0으로 초기화한다. 물리 실행 검사에서 대기 위치 유지·속도 0·net contact force 0을 확인한다.
- 비활성 물체의 collider와 simulation 자체는 켜져 있다. 같은 환경에서 작업 물체가 대기 구역까지 날아가는 비정상 궤적에 대한 절대 무접촉을 보장하지 않는다. 공통 ground도 환경 간 차단 대상과 다르다. 대기 물체의 렌더링은 그대로 남으므로 다른 환경과 시각적으로 겹쳐 보일 수 있다.
- 현재 정책 관측은 카메라 RGB가 아닌 활성 물체 메쉬 기반 대표점이다. 다른 환경이나 대기 물체를 관측 후보로 추가하지 않았다. 향후 실제 카메라를 도입하면 시각적 가림은 별도로 검토해야 한다.

## 계약 대조와 검증

변경한 실행 코드는 EnvCfg의 시각화 플래그와 runtime의 reset 후 시각화뿐이다. 등록·상속·Scene·Command·Event/reset 배치·관측 계산·Action·Reward·Termination·Curriculum·PPO는 기준과 동일하다. GPU checker의 부모/Test 전체 설정 대조는 기존 reset·Reach 차이 외에 이번 시각화 플래그만 허용한다.

CPU 명령:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 WARP_CACHE_PATH=/tmp/stabilize_warp_cache /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q
```

결과: 75 passed. 최초 실행은 Warp cache 경로를 지정하지 않아 읽기 전용 홈 cache 생성에 실패했으며, `/tmp`로 지정한 위 재실행이 통과했다. Python compileall과 diff 공백 검사도 통과했다.

GPU 명령(각 TASK에 두 요청 환경 ID 사용):

```bash
PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 WARP_CACHE_PATH=/tmp/stabilize_warp_cache /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 4 --task TASK --audit-resets 2 --output /tmp/stabilize_markers_RESULT.json
```

검증은 headless에서 렌더 모드 플래그를 일시적으로 `rgb_array`로 설정해 동일 마커 생성 경로를 실행하고 원상 복원한다. USD PointInstancer 좌표가 관측 캐시와 일치하며 마커 subtree에 CollisionAPI/RigidBodyAPI가 없고 충돌 그룹이 그대로임을 검사한다. 일반 headless에서는 마커가 없거나 숨겨지는 것도 검사한다. 이 검사는 GUI 캡처의 육안 검토를 대신하지 않는다. 생성 시 Fabric의 PointInstancer prototype 경고가 기록되었으며 아래 검증 결과와 구분한다.

두 GPU 실행 모두 exit 0으로 통과했다. 각 4환경, 초기 seed42 및 reset seed0·1, 부분 reset·실제 물리·접촉 검사다. `/tmp/stabilize_markers_stabilize.json`과 `/tmp/stabilize_markers_sweep.json`의 주요 결과는 다음과 같다. 장기 학습·2048 성능 재측정·의도적 환경 간 관통 실험·GUI 렌더 이미지 검토는 이번에 수행하지 않았다. `logs/rsl_rl`은 변경하지 않았다.

| 검사 | Stabilize-Test | Sweep-Only-Test |
| --- | --- | --- |
| `surface_markers_match_policy_snapshot_and_have_no_physics` | 통과 | 통과 |
| `test_inactive_parking_grid_and_unchanged_collision_groups` | 통과 | 통과 |
| `test_inactive_bodies_stationary_and_contact_free_after_physics` | 통과 | 통과 |
| `partial_reset_isolation` | 통과 | 통과 |
| `real_physics_smoke` | 통과 | 통과 |
