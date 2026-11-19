# 일반 Sweep Only 물체 옆 초기화 성능 개선

최종 결과: `Inspire-Sweep-Only-v0`의2048환경·headless·seed42·32회 전부 collection10초 미만(collection 중앙값8.322초·최대9.579초). CPU143개와 실제 GPU64환경·8seed의 배치·IK·부분 reset 검증을 통과했다. 아래 중간 후보의 실패 수치와 최종 결과를 구분한다.

## 요청·범위·기준

사용자는 `Inspire-Sweep-Only-v0`의 2048환경 collection time을 10초 미만으로 줄이되 손이 밀기 반대편에 있고, 밀기 최소 공간(RED) 및 현재 로봇 점유 공간에 물체가 겹쳐 스폰되지 않도록 요청했다. Stabilize 보상의 해결은 이번 범위가 아니다. 직접 수정이며 새 환경이나 등록 ID를 만들지 않는다.

기준 HEAD는 `913c2846fc81b8cf1d281d34af3c1aaf1b1252c8`. 시작 시 코드 작업트리는 깨끗했고 문서 서브모듈의 기존 변경은 보존했다. 코드 스냅샷은 `/tmp/sweep_ik_task_before`에 보관했다. 기존 `logs/rsl_rl`은 건드리지 않고 실행 결과와 checkpoint를 `/tmp/stabilize_perf`에 저장한다.

## 원인과 개선

일반 초기화는 목표별 손 자세 IK 외에 실제 손/팔의 자기충돌을 검사한다. OBB가 겹치는 후보마다 SciPy LP로 실제 convex hull의 교집합 내부 반경을 계산하던 것이 주 병목이었다. 초기 2048배치 fixture에서 target/shelf 충돌을 제외한 자기충돌 후보 2,587개가 실제로는 분리돼 있었다.

중간 학습 실행의 첫 collection은38.068초, 다음33.304초였다. 이 실행은 시작 중 동적 import로 장애물 배치의 새 GPU 경로를 이미 사용했으며, 충돌 검사만 기존 경로다. 따라서 변경 전 전체 코드의 벤치로 취급하지 않는다. 세 번째 iteration의16policy step cProfile에서 총20.530초 중 convex_overlap2,018회17.308초, valid17.714초, physics0.823초, 새 배치0.044초였다. IK solve21회 호출의 누적 host 시간은0.011초이며 독립적인 CUDA kernel 측정은 아니다. 프로파일러가 들어간 세 번째 collection46.098초는 최종 성능 판정에 쓰지 않는다. `/tmp/sweep_collection_check.py`는 이3회 모두10초 초과로 실패했다.

| 수정 | 이전 | 이후 | 보존한 조건 |
| --- | --- | --- | --- |
| 자기충돌 | 모든 OBB 후보에 CPU LP | 원본 hull face로 GPU에서 분리를 증명하고 미확정 후보만 CPU 전처리·동일 LP | 실제 hull, LP interior 임계1µm, 기존 손 내부 겹침 예외, target/shelf OBB |
| 채택 자세 FK | 충돌 검사 때 계산한 뒤 최종 배치용으로 다시 계산 | 채택 후보의 FK를 재사용하고 거절 행만 default FK | 관절·손 목표·판정에 사용한 실제 형상 |
| host 전송 | 후보별 GPU bad[row] 읽기 | CPU 배열로 한 번 읽고 최종 반영 | 후보 순서의 충돌 결과 |
| 장애물 선택 | 격자×로봇 대형 텐서 및 후보별 Torch 반복 | 로봇 영역 검사 커널과6후보 협력 선택 커널 | RED·높이 겹침·로봇1cm 확장·물체 반경·cell margin·난수·실패시 후보 감소 |

빠른 convex 검사에서 원본 hull의26방향 대표 face를 고르고 상대 형상 쪽2face를 먼저 확인한다. 분리가 입증되지 않으면 나머지 선택 face 및 원래 LP로 이어진다. 선택 face 수를 줄이는 것은 빠른 기각 기회를 줄일 뿐, 충돌 후보를 임의로 통과시키지 않는다. float32 회전행렬의 비직교 오차를 고려해 double 역행렬로 LP plane와 동등한 상대 좌표 검사를 하고 양의 분리 여유1e-8을 요구한다. GPU 커널은 후보별 상대 변환과 내적만 계산해 CPU의 큰 정점 배열·einsum을 없앤다. 최초 hull 캐시를 올린 Warp stream을 Torch 현재 stream에서 기다린 뒤 같은 Torch stream에 커널을 실행한다. GPU가 아닌 경우에는 NumPy 전처리와 원래 LP를 사용한다.

장애물 GPU 경로는256행 단위로 처리하며 CPU·지원 외 dtype/격자는 기존 구현을 유지한다. 큰 후보를 배치하지 못해도 뒤의 작은 후보를 계속 시도한다. Test 초기화는 이 일반 장애물 함수나 RobotResetGeometry.valid를 호출하지 않는다.

## 계약 대조

변경한 production 파일은 `mdp/common/stabilize_sweep_geometry.py`, `mdp/common/stabilize_sweep_layout.py`, `mdp/event_functions/stabilize_sweep.py`다. Event 파일은 `choose_initial_pose`의 FK 재사용과 IK 실패 행의 불필요한 기하 검사 생략만 변경했다. 일반 Stabilize와 Sweep Only가 이 초기화를 공유하므로 둘 다 계산 가속을 받는다. 주 성능 검증 대상은 요청한 일반 Sweep Only다.

등록·EnvCfg·Scene·Command·reset 순서와 재시도 흐름·손 위치/방향/높이·IK solver·4후보와 실패 행8회 재추출·초기 대표점 관측·Action·Reward/Gate·Termination·Curriculum·PPO는 유지한다. Test 초기화·대표점 빨간 시각화도 유지한다. 충돌 검사 삭제, 장애물 수 상한 축소, 물리 step 또는 rollout 길이 감소로 시간을 줄이지 않는다.

검증 스크립트는 후보 계산 결과만 믿지 않고 native body pose로 손이 타겟 뒤에 있는지, 최종 활성 물체와 로봇 OBB가 겹치지 않는지, RED와 로봇 높이별 확장 영역이 비어 있는지 검사하도록 보강했다. 일반 환경의 부분 reset도 모든 비대상 물리 상태·명령·관측·mask 보존을 검사한다.

## 검증 기록

장애물 커널: Isaac Sim Warp1.8.2 / RTX3090에서17행 및2048행×16000cells×30로봇 형상의 최종local/yaw/active/RNG가 reference와 정확히 일치했다. 합성 전체 배치 중앙값447.24ms→22.75ms. 이는 실제 학습 collection과 별개다. `/tmp/stabilize_robot_layout_gpu_result.json`.

GPU 통합 실행:

```bash
PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 WARP_CACHE_PATH=/tmp/stabilize_warp_cache /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 64 --task Inspire-Sweep-Only-v0 --audit-resets 8 --output /tmp/sweep_ik_optimized_gpu64.json
```

실제 학습 결과는 아래 성능 측정에 기록한다. 초기 시뮬레이터 생성·최초 reset·logger/checkpoint 저장은 RSL collection time 바깥이다. 장기 행동 성공률이나 모든 seed/하드웨어에 대한10초 보장은 이번 단기 성능 검사로 입증하지 않는다.

추가 검증 결과:

- GPU face 전처리·FK 재사용 단계의 CPU 기하/관측/COM 회귀136개 통과(21.74초, `/tmp/sweep_ik_final_cpu.log`). 작은 관통·정확 접촉·분리 경계, 비직교 float32 회전, 무작위128hull쌍에서 기존 LP와 동등성을 검사했다.
- 실제2048 초기 후보의 valid 결과2048개가 원본과 정확히 일치했다(2038valid,10invalid). OBB를 동일하게 캐시한 CPU narrow-phase 비교에서21.270초/LP2587회→0.482초/LP0회. 이 fixture에서는 모두 빠른 분리 증명이 가능했으며, 다른 배치에서 LP가0회라는 보장은 아니다.
- Sweep Only GPU64환경·8seed·부분reset·실제물리·접촉검사 exit0. 실제 손–타겟 밀기축 최소간격26.14mm, RED 최소여유2.03mm, 로봇 확장영역 최소여유2.37mm. 목표가 양쪽으로 변해도 손바닥 왼쪽·손등 오른쪽 조건 유지.
- HEAD 대비 production3개 외 등록/config/manager/hand_pose/IK/관측/runtime/PPO/train은 byte 단위 동일. layout의 기존 Test 관련8개 정의와 event의 `choose_initial_pose` 외 정의는 AST 동일. 검사 기록 `/tmp/sweep_ik_contract.json`.

CPU 전처리 중간 후보의 성능 실행 명령(아래 실패 기록에 해당):

```bash
PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Only-v0 --headless --num_envs 2048 --seed 42 --max_iterations 32 agent.experiment_name=/tmp/stabilize_perf/sweep_ik_optimized
python /tmp/sweep_collection_check.py /tmp/sweep_ik_optimized_train.log --expected-iterations 32 --output /tmp/sweep_ik_optimized_train_result.json
```

검사기는 연속32회 전체 로그의 collection time을 검사하며 반올림 상한0.0005초를 더해도10초 미만이어야 통과한다. iteration0도 제외하지 않는다. 원본 RSL 로그의 collection/learning/iteration 수치 일관성과 누락 여부도 검사한다.

### CPU face 전처리 후보의 실제 학습 실패

첫 plain2048환경 실행은 collection8.757,6.764,7.669,8.781,9.679초로 시작했지만 이후10.910,12.180,13.365,14.553,14.599,15.557초로 증가했다. 11회 기록 후 자체 프로세스를 SIGINT로 종료했다. 이는 목표 미달 실행이며 최종 통과로 취급하지 않는다. 원시 로그 `/tmp/sweep_ik_optimized_train.log`. reset 빈도가 늘어도 비용을 낮추기 위해 face 분리 증명의 GPU 처리와 채택 후보의 FK 재사용을 추가한다. 실패한 실행의 결과·명령을 보존한다.

### 잔여 병목과 GPU face 검사

CPU face 전처리 후보의 후반16policy step은5.527초였고, valid1.794초·NumPy einsum1.208초·FK boxes1.030초·physics0.896초였다. `/tmp/sweep_ik_cpu_faces_late.prof`와 보고서에 보관했다. 이 단계는 최종 GPU face 검사 및 FK 재사용 전 코드다.

GPU face kernel은 bundled Warp1.8.2 / RTX3090에서 실제2,587후보를 모두 분리했고, 전체2,048행의 valid가 기존 LP와 정확히 일치했다(2038/10). GPU kernel+동기화 중앙값0.989ms(block64); full valid 첫 실행0.209초(OBB 포함·cold 비용)였다. 커널 시간은 학습 collection과 구분한다. `/tmp/sweep_geom_kernel_cuda0.json`.

FK 단일 커널 적용 전 GPU64환경·8seed 검사는 `/tmp/sweep_ik_check_fk_reuse.py`로 표준 검사 스크립트를 실행하면서 기존 `choose_initial_pose`와 같은 RNG 상태로 비교했다. 결과 `/tmp/sweep_ik_final_gpu64.json`, exit0. 관절·손 목표·IK오차·시도수·valid·진단·난수 상태는 정확히 일치했다. FK boxes는 batch/stride가 다른 FP32 계산의 최대2.384e-7 차이가 있어 절대오차1e-6 내 수치동등으로 검증했다. 전체 배치가 bit-exact라고 주장하지 않으며 최종 물리 상태의 RED/로봇 비겹침을 별도로 검사했다. 손–타겟 최소간격26.14mm·RED 최소여유2.03mm·로봇 확장영역 최소여유2.37mm. 부분 reset 비대상 상태·관측·mask, 표면 관측 reference, 실제 접촉, timeout·Gate 없음, 비활성 물체 주차 검사도 통과했다.

### GPU face 검사·FK 재사용 후보의 2048환경 측정

프로파일러나 thread 제한을 넣지 않은 실제 학습 명령이다. RSL rollout36step·PPO8epochs×4minibatches·seed42와 환경 설정을 유지했다.

```bash
PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Only-v0 --headless --num_envs 2048 --seed 42 --max_iterations 32 agent.experiment_name=/tmp/stabilize_perf/sweep_ik_final
python /tmp/sweep_collection_check.py /tmp/sweep_ik_final_train.log --expected-iterations 32 --output /tmp/sweep_ik_final_train_result.json
```

이 후보도 목표 미달이었다. iteration0–18 총19회가 기록됐고 collection 최소5.624초·중앙값9.243초·최대11.570초였다. iteration10부터10초를 초과했으므로32회 완료 전 자체 프로세스를 SIGINT로 종료했다. `/tmp/sweep_ik_final_train_result.json`의 검사 결과는 실패이며 최종 통과로 사용하지 않는다. 후반 Reset/batch_ms는197.6ms였다. 채택 FK 재사용만으로는 부족해, 기존 joint-frame FK 수식과 USD 체인을 유지하는 GPU 단일 커널을 추가 검증한다.

### GPU face 검사 이후 재프로파일

`/tmp/sweep_ik_gpu_faces_profile.py`로16policy step을 재측정한 결과 총3.912초, FK boxes53회0.822초(자체0.762초), valid51회0.342초, 표면 관측 snapshot0.472초, physics0.890초였다. IK solve51회 host 누적0.025초·tolist271회0.009초·place_obstacles16회0.071초로, 다음 개선 대상은 FK였다. 이 구간은 이전과 같은 iteration6의16step이며 초기 fixture 저장은 profiling 구간 이전에 끝난다. 원시 통계 `/tmp/sweep_ik_gpu_faces_late.prof`·보고서 `/tmp/sweep_ik_gpu_faces_late_report.txt`.

반복 candidate FK는 collision owner별로 USD root부터 해당 body까지의 joint chain을 단일 Warp 커널에서 계산한다. 기존 IsaacLab quaternion 곱·적용·회전행렬 공식을 직접 옮기고 FMA를 끈다. GPU가 아닌 경우 기존 Torch FK를 사용한다. 최초 손 표면 정점과 기존 손 내부 겹침 제외는 계속 Torch 기준을 사용해 초기 목표와 IK 입력을 유지한다. 채택 후보 FK 재사용도 유지한다. 최종 수치 동등성과 실제 배치·성능 검사는 아래에 기록한다.

GPU FK 도입 단계의 회귀는 기하/reset80개(7.32초, bundled Warp1.8.2)와 표면관측/COM57개(6.63초), 합계137개가 통과했다. 이전136개 결과와 구분한다. 새 FK 검사는 분기 트리·고정/가동 손 관절·동일 owner의 복수 메쉬·비정렬 부분 행을 포함한다.

GPU FK 도입 단계의 실제 GPU64환경·8seed 통합 결과는 `/tmp/sweep_ik_fused_fk_gpu64.json`(exit0)이다. `/tmp/sweep_ik_check_fused_fk.py`는 원본 `choose_initial_pose`를 실행할 때 실제 `boxes_reference`로 교체해 전체 이전 계산과 비교한다. 관절·손 목표·IK오차·valid·재시도·진단·난수는 정확히 일치했고 boxes의 최대절대오차는1.384731e-6(허용3e-6)였다. FP32 삼각함수·합산·batch/stride 차이를 허용하되 최종 native 물리 상태의 손/RED/로봇 비겹침을 별도로 검사해 모두 통과했다. 손–타겟 최소간격26.14mm·RED 최소여유2.03mm·로봇 확장영역 최소여유2.37mm로 앞선 검사와 같았다.

FK owner 커널의 실제 입력 벤치에서2048행 중앙값15.473ms→0.152ms,172행12.946ms→0.148ms였다. 원본172행의 valid170/invalid2 결과도 정확히 일치했다. 이 커널을 production `boxes_kernel`로 연결한 뒤 위 통합 검사를 수행했다. `/tmp/sweep_fk_fixture_cuda0.json`은 커널 비교 자료이며 전체 collection 시간과 구분한다.

### FK 단일 커널만으로 부족했던 실제 학습과 최종 추가 변경

`/tmp/sweep_ik_fused_fk_train.log`의32회 학습은 정상 종료했지만 collection 최소5.080초·중앙값9.439초·최대11.495초였다. iteration19–31은10초를 초과했다. 이것도 목표 미달로 기록하고 최종 통과로 사용하지 않는다.

추가로 두 비용을 제거했다. 첫째, IK가 이미 실패한 행은 FK·충돌 검사 대상에서 제외한다. 채택은 기존에도 `IK 성공 AND 충돌 없음`이므로 결과를 바꾸지 않는다. 모든 시도 행의 난수·목표 자세·오차·시도수는 그대로 갱신하고 최종 거절 행의 반환 geometry는 기본 자세 FK를 유지한다. 미검사 행의 진단 `collision_free`는 기존 bool 대신 `None`으로 표시한다. 비정렬 환경 ID의 혼합 성공/충돌거절/모든 IK 실패/부분 실패와 RNG·최종 FK 일치를 CPU3개 검사로 확인했다.

둘째, target·shelf·관련 self pair의 OBB SAT를 GPU 커널로 합쳐 환경×모든 body쌍×15축의 대형 중간 텐서를 만들지 않는다. 기존의 touching1e-6·축 길이1e-7 판정은 유지한다. 접촉/축 길이 경계와 거의 평행한 축은 오차 여유로 표시해 원래 Torch SAT로 재검사한다. 길이2e-6 이하인 축은 불확정이며, 정규화 오차를 고려해 `(distance+reach+1)*1e-5/max(axis_length,1e-7)`을 guard로 사용한다. 신뢰할 수 있는 길이와 충분한 간격을 가진 분리축만 불확정을 해제한다. 초기 단순 커널의 접촉 경계1/256 불일치는 이 fallback으로 해결했으며, 단순 커널은 채택하지 않았다. shape·self_pairs·device 별 메타데이터를 캐시하고 inference tensor의 version 접근도 처리한다. CPU는 기존 Torch SAT를 유지한다.

강화 guard 적용 후 실제 fixture에서 bad·self 후보·최종 valid가 원본과 정확히 일치했다. 전체 valid 중앙값은172환경7.928ms→2.373ms,2048환경74.088ms→4.160ms였다. 이는 초기 분리 증명 이후 남았던 대규모 OBB 비교 비용을 측정한 결과이며, 전체 학습 collection과는 별도다. `/tmp/sweep_sat_production_cuda0.json`.

### 최종 코드의 기하·상태 보존 검증

IK 실패 행 생략과 보수적 SAT fallback까지 포함한 CPU 기하/reset 회귀86개(9.21초, `/tmp/sweep_sat_production_cpu.log`), 표면 관측/COM 회귀57개(10.44초, `/tmp/sweep_ik_complete_surface_com_cpu.log`)를 통과했다. 합계143개다. SAT 테스트는 무작위·정확 접촉·거의 평행한 축·비정렬 부분 행·self-pair mask 캐시 갱신·inference-mode mask를 포함한다.

최종 실제 GPU 통합 검사는64환경·seed0–7로 실행해 정상 종료했다. `/tmp/sweep_ik_check_complete.py`는 같은 RNG 상태에서 변경 전 `choose_initial_pose`, 원본 Torch FK·SAT와 원본 LP를 모두 실행해 새 경로와 비교한다. 관절·목표·IK오차·valid·시도수·난수는 정확히 일치했고 FK boxes 최대절대오차는1.384731e-6(허용3e-6)이었다. 진단의 유일한 의도된 차이는 미검사 IK 실패 행의 `collision_free=None`이다. 원본 참조 실행을 함께 포함하므로 이 검사의 reset 시간은 성능 수치로 쓰지 않는다.

최종 native body pose 감사에서 손–타겟 밀기축 최소간격26.14mm, RED 최소여유2.03mm, 로봇 확장영역 최소여유2.37mm를 확인했다. 활성 물체–로봇 비겹침·손바닥 왼쪽·비대상 부분 reset 상태 보존·대표점 관측 reference·접촉·timeout을 모두 통과했다. 결과 `/tmp/sweep_ik_complete_gpu64.json`.

독립 최종 코드 대조에서는 변경된 Python이 위 production3개와 검사 스크립트·테스트 총5개뿐이며 나머지468개는 기준 HEAD와 byte 단위 동일했다. 원본 SAT overlap·LP 함수, Test 초기화8개 정의, Event의 `choose_initial_pose` 외 정의도 AST 동일하다. 이 비교는 초기 배치 샘플링 설정·재시도·보상·관측·PPO를 바꾸지 않았음을 확인하며 모든 가능한 배치의 bit-exact 결과를 주장하지 않는다. 현재 고정 자산·미터 단위 좌표 외의 임의의 수치적으로 불안정한 기하나 런타임 중 geometry/device 변경은 검증 범위가 아니다.

강화 SAT guard의 별도 GPU 비교에서도 무작위8,960쌍·접촉/거의 평행 경계768쌍·실제 fixture68,096쌍, 합계77,824쌍에서 원본 Torch와의 판정 불일치0개였다. `/tmp/sweep_sat_fallback_cuda0.json` 및 production 전체 검사 `/tmp/sweep_sat_production_cuda0.json`을 성능 증거와 함께 보존한다.

### 최종 실행 및 판정

IK 실패 행의 불필요한 검사 제거와 GPU SAT까지 포함한 실제 학습이 정상 종료(exit0)했다. 프로파일러·thread 제한 없이 기존 `train.py`와 동일한2048환경·seed42·rollout36·PPO8×4를 사용했다.

```bash
PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Only-v0 --headless --num_envs 2048 --seed 42 --max_iterations 32 agent.experiment_name=/tmp/stabilize_perf/sweep_ik_complete
python /tmp/sweep_collection_check.py /tmp/sweep_ik_complete_train.log --expected-iterations 32 --output /tmp/sweep_ik_complete_train_result.json
```

iteration0–31 전부 통과. collection 최소4.905초·중앙값8.322초·최대9.579초다. learning을 포함한 로그 iteration time은 중앙값8.69초·최대9.98초다. 최초 시뮬레이터 생성·최초 reset은 이 지표에 포함되지 않는다. 값의 반올림 상한까지 고려해 각 collection이10초 미만임을 검사했다.

[원시32회 수치·기하 동등성·GPU audit·소스 hash·실패한 중간 후보](../../03_assets/validation/2026-11-19_sweep_only_ik_performance.json)를 보존했다. 학습 결과와 checkpoint는 `/tmp/stabilize_perf/sweep_ik_complete`에 두며 기존 `logs/rsl_rl`은 수정하지 않았다. 다른 장치·모든 seed의 시간 또는 장기 학습 성공률까지 보장하는 결과는 아니다.

문서 최종 검사: 변경 Markdown5개의 수식 검사와 root/package/docs의 `diff --check`를 통과했다. 링크 검사에서는 이번 추가 링크 오류가 없었고, 기존 README의 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1개만 보고됐다. 이 링크는 기준 HEAD에도 존재했으므로 이번 범위에서 변경하지 않았다. `/tmp/sweep_ik_complete_links.json`. 작업 중 별도로 수정된 `docs/plan/PLAN18.md`는 건드리지 않았다.
