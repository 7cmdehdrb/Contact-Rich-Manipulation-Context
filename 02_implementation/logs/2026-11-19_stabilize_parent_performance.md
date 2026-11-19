# 일반 IK 환경에 공통 성능 개선 적용

## 요청과 변경 기준

사용자가 두 Test에 적용한 최적화를 부모인 일반 IK 환경에도 적용하도록 요청했다. 대상은 `Inspire-Stabilize-Sweep-v0`와 이를 상속한 `Inspire-Sweep-Only-v0`다. 새 환경을 만들지 않고 공통 `reset_scene`·`commit_scene`을 직접 수정했다. Test는 부모 EnvCfg를 상속하지만 reset event를 교체하므로, Test 전용 adapter에 넣었던 최적화가 부모로 역전파되지 않았던 것이다.

작업 시작 시 이전 Test 최적화가 미커밋 상태였다. 이를 포함한 Python 파일을 `/tmp/stabilize_parent_before`에 보관하고 이번 변경의 비교 기준으로 사용했다. 기존 수정과 문서 submodule 상태를 보존했다. [이전 Test 최적화와32회 측정](2026-11-18_stabilize_sweep_performance.md)은 당시 범위와 결과이며, 이번 일반 IK 환경의 성능으로 해석하지 않는다.

## 적용과 보존 범위

| 항목 | 변경 전 | 변경 후 |
| --- | --- | --- |
| 대표점 추출 | 환경별 메쉬 구성·광선 질의·CPU 연결 성분 | Test와 같은 공유 메쉬·256환경 GPU raster/연결 성분·CPU bounds kernel |
| 비활성 물체 | 높은 Z52–82m | 환경 기준 +X3m부터45cm 간격4×4 격자, slot별 활성 초기 Z 유지 |
| 로컬 COM | physics timestamp마다 getter | startup 물성 확정 후 cache, joint reset 무효화 뒤 재연결 |
| native reset | root/object 전체 기록·gravity 전체 설정·전체 wake | 고정 base와 계속 비활성인 물체의 동일 상태 기록 생략, 변경 gravity 설정, 기록한 물체 wake |
| 장애물 배치 |8행씩 Torch RED 계산 |32행씩 fused RED 계산, 기존 로봇 점유 공간 검사 유지 |

1mm 격자·실제 시각 메쉬·노출 기준·4연결 조각·타겟 최대 조각·장애물 순서·EEF 기준 XYZ·장애물0개 fallback을 유지한다. fallback까지 기존 좌표로 계획하고 관측한 뒤, 물리에 commit할 때 비활성 행만 새 주차 위치로 바꾼다. 활성 pose/quaternion과 난수 추출은 그대로다.

일반 IK의 손바닥 왼쪽 방향, 실제 손 하단5mm, 손목 고도각0°/2°의 최대4후보, 충돌 메쉬 검사, 실패 행만 최대8회 배치 재추출, 최종 실패 오류를 유지한다. Test용 협력 셀 선택기는 로봇 점유 공간 조건을 포함하지 않으므로 일반 배치에 이식하지 않는다. 일반 `place_obstacles`의 로봇 OBB XY 여유·Z overlap·최소 간격·큰 물체 실패 뒤 작은 물체 배치 규칙을 그대로 사용한다. 난수는 배치 loop 전에 추출하므로8→32행 묶음 변경으로 난수 진행이 달라지지 않는다.

일반 환경에는 원래 미사용 centroid 관측 생성이 없으므로 삭제할 항목이 없다. 일반 환경에 Reach를 추가하거나 Test의 단일 IK로 교체하지 않는다. Test reset 실행 경로와 Finger의 기본 경로는 이번 변경에서 보존한다.

## 검증

- CPU3파일132개 통과(11.70초). 추가 차등 검사는 부분 순서의35환경·서로 다른 물체 크기·로봇 높이·0–6개 요청에서 batch8/1/32/64의 local/yaw/active 및 후속 RNG가 정확히 같은지 확인한다.
- 변경 생산3파일 mypy 통과(`--follow-imports=skip --ignore-missing-imports`). 엄격한 전체 의존성 타입 검사는 아니다.
- 일반 Stabilize GPU4환경, seed0–1, 실패 주입 검사 통과. 최초 IK 실패·부분 reset 충돌 실패·자동 reset IK 실패 복구, 실제 손 방향/높이, Gate/timeout, 대표점 reference 대조, 고정 COM와 실제 접촉 모멘트를 확인했다.
- 일반 Sweep Only GPU64환경, seed0–7 통과. Gate 우회와 부모 보상 차이, 대표점 reference 대조, 부분 reset·정지한 비활성 물체·충돌 필터·실제 접촉 검사를 확인했다.
- 변경 전 Python snapshot과 대조해 등록·모든 EnvCfg/MDP Cfg·runtime·PPO·train.py·IK/충돌 기하 모듈이 byte-identical임을 확인했다. `choose_initial_pose`, `plan_initial_layout`, Test reset adapter, 원본/배치 관측 helper와 native writer의 실행 AST도 동일하다(설명 docstring 제외).

검증기의 표면점 reference·COM·비활성 주차 검사를 일반 환경까지 확장했다. 초기 reset에서 재추출이 실제로 필요할 수 있으므로 `len(sampled)==1` 대신 전체 표집 행 수가 최초 환경 수+복구 행 수와 일치하는지 검사한다. 생산 복구 조건을 완화한 변경이 아니다.

GPU 검사는 다음 명령으로 실행했고 둘 다 exit0이었다. 결과는 `/tmp/stabilize_parent_gpu4.json`과 `/tmp/stabilize_parent_sweep_gpu64.json`이다.

```bash
PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 WARP_CACHE_PATH=/tmp/stabilize_warp_cache /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 4 --task Inspire-Stabilize-Sweep-v0 --audit-resets 2 --inject-reset-failures --output /tmp/stabilize_parent_gpu4.json > /tmp/stabilize_parent_gpu4.log 2>&1
PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 WARP_CACHE_PATH=/tmp/stabilize_warp_cache /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 64 --task Inspire-Sweep-Only-v0 --audit-resets 8 --output /tmp/stabilize_parent_sweep_gpu64.json > /tmp/stabilize_parent_sweep_gpu64.log 2>&1
```

Test의32회10초 미만 결과를 일반 환경에 전용하지 않는다. 보관 위치 변경과 COM/native cache의 물성·Isaac 버전 의존성은 이전 최적화와 같다.

## 실제2048환경 학습 결과

일반 `Inspire-Stabilize-Sweep-v0`를 RTX3090·headless·2048환경·seed42로3iterations 실행해 exit0으로 완료했다. 원본 `train.py`와 horizon36·PPO8epochs×4minibatches를 유지했고 profiler·별도 thread 제한은 사용하지 않았다. 기록과 checkpoint는 `/tmp`에 분리했으며 기존 `logs/rsl_rl`은 수정하지 않았다.

```bash
PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Stabilize-Sweep-v0 --headless --num_envs 2048 --seed 42 --max_iterations 3 agent.experiment_name=/tmp/stabilize_perf/parent_stabilize > /tmp/stabilize_parent_train.log 2>&1
```

iteration 시간은 순서대로 **41.06/35.06/43.24초**였다. 정상 학습 실행과 최적화 연결은 확인했지만, 일반 IK 환경의10초 미만은 달성하지 않았다. 시뮬레이터 생성·첫 reset·로그/checkpoint I/O는 RSL-RL iteration 시간에서 제외된다. 첫 iteration의 `Reset/observation_ms`는 환경당0.0786ms, `Reset/batch_ms`는 배치당973.82ms였다. 이 값들은 단위와 집계 대상이 다르므로 직접 빼서 IK 시간을 추정하지 않는다. 남은 일반 경로의 비용을 이번에 세부 프로파일링하지 않았으며 특정 함수가 병목이라고 확정하지 않는다.

일반 Sweep Only는64환경 통합 검사까지 완료했고2048 PPO 시간은 별도로 측정하지 않았다. 장기 학습 행동과 모든 seed에서의 성능은 미검증이다. [CPU·GPU 결과·수정 전후 계약·소스 해시·학습 시간 원시값](../../03_assets/validation/2026-11-19_stabilize_parent_performance.json)을 보존한다.

변경 Markdown5개 수식 검사, 문서4파일의 링크 검사와 root·문서 저장소의 `git diff --check`가 통과했다. 패키지 README의 이번 새 링크는 존재하며, 이전 작업에서 확인한 기존 GoalAccuracy 누락 링크는 이번 범위 밖으로 보존했다. 별도 Markdown 렌더링은 수행하지 않았다.
