# Stabilize / Sweep Only Test 2048환경 성능 개선

2026-11-19 최종 결과: 두 Test 모두 실제2048환경·headless 학습32회를 완료했고, 첫 iteration을 포함한 전 회차가10초 미만이었다. 두 프로세스와 전체 iteration 검사기가 모두 exit0으로 종료됐다.

| 환경 | 완료한 iteration | 최소 | 중앙값 | 최대 |
| --- | --- | --- | --- | --- |
| `Inspire-Stabilize-Sweep-v0-Test` | 32/32 | 5.07초 | 8.81초 | 9.44초 |
| `Inspire-Sweep-Only-v0-Test` | 32/32 | 4.98초 | 8.69초 | 9.18초 |

RTX3090에서 seed42, horizon36, PPO8epochs×4minibatches와 기존 보상·관측 규칙을 유지했다. 프로파일러와 별도 CPU thread 제한 없이 원본 `train.py`로 각각 순차 실행했다. 수치는 RSL-RL의 collection+learning 시간이며 시뮬레이터 생성·최초 reset·로그/checkpoint 저장은 제외한다. 아래10초 초과 중간 결과는 개선 과정의 실패 기록으로 보존하며 최종 합격과 구분한다. [최종 원시 검증·전32회 시간·소스 대조](../../03_assets/validation/2026-11-18_stabilize_sweep_performance.json).

## 요청과 기준

사용자가 두 `-Test` 환경의 iteration time이 여전히 과도하다고 보고하며, 실제 `--headless --num_envs 2048` 학습으로10초 미만 달성을 요청했다. 질문 없이 필요한 개선·검증을 수행하도록 승인했다. 대상은 `Inspire-Stabilize-Sweep-v0-Test`와 `Inspire-Sweep-Only-v0-Test`이며 기존 학습 로그는 보존한다.

기준 root commit은 `ae94e0ab96316b6d4340d747e42fa6315b41e874`다. 작업 시작 시 root 코드는 clean이며 문서 submodule 포인터 차이가 있었다. 진단 실행·checkpoint는 `/tmp/stabilize_perf` 아래에 분리한다. 실제 학습 엔트리는 기존 `scripts/train.py`를 사용한다.

성능 합격 기준은2048환경, horizon36, PPO8epochs×4minibatches를 유지한 실제 학습에서 보고되는 collection+learning iteration time이10초 미만인 것이다. 시작 시 scene/PhysX 초기화, 첫 전체 reset, checkpoint/log 저장 비용은 RSL-RL iteration 지표에서 제외되므로 별도로 구분한다. 목표를 맞추기 위해 rollout 길이·PPO 횟수·환경 수를 줄이지 않는다.

## 진단 실행

```bash
PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m cProfile -o /tmp/stabilize_perf_baseline.prof src/inspire_sweep_baseline/scripts/train.py --task Inspire-Stabilize-Sweep-v0-Test --num_envs 2048 --headless --seed 42 --max_iterations 3 agent.experiment_name=/tmp/stabilize_perf/baseline_stabilize
```

검사기는 `/tmp/stabilize_perf_check.py`이며 stdout에서 collection/learning/iteration time과 전체 iteration 수를 함께 검사한다. 첫 iteration도 포함하고 출력 반올림 허용오차를 보수적으로 적용한다.

## 원인과 중간 측정

원본 경로는 각 reset 환경의 실제 시각 메쉬를 합쳐 다시 업로드하고 BVH를 구성한 뒤, 전체 ray mask를 CPU로 회수해 연결 성분과 대표점을 찾았다. 최초2048환경 진단은 scene/PhysX 초기화와 첫 reset 이후에도 첫 rollout이 수분 내 완료되지 않았다. 이 진단 프로세스만 SIGINT로 종료했다. Kit의 native 종료 처리 때문에 `-m cProfile` 종료 시 저장 파일이 생성되지 않았으며, 이 실행의 정확한 iteration 시간을 확보했다고 주장하지 않는다.

BVH 공유·배치 raycast·CPU mask crop까지만 적용한 중간 구현은 실제2048환경에서3iterations를 완료했지만30.13/25.69/32.51초였다. step 범위 cProfile로 정상상태16step을 비교하면 전체10.994초 중 reset8.480초, 대표점 snapshot7.607초, Finger 배치/IK0.651초였다. 대표점 생성이 주 병목임을 확인했다. 로봇/물체의 불변 로컬 COM을 CPU PhysX getter에서 반복 회수하는 비용도 약0.344초/16step이었다. step 범위만 측정하는 임시 profiler를 사용했고 최종 plain 학습 전에 제거했다.

## 변경과 의도


표면점 생성의 환경별 메쉬 업로드·BVH 구성·동기화·readback을 배치 처리로 바꿨다. 실제8종 시각 메쉬와 환경별 고정 scale·reset yaw/translation을 그대로 사용하며1mm 격자,4연결 mask,2cm/20% 노출 조건, 실제 surface hit 대표점, 최대 타겟조각/장애물별조각/순서, target-only fallback을 보존한다. 원본 두 환경은 reference 관측 경로를 유지하고 Test reset만 빠른 backend를 호출한다.

- `mdp/common/stabilize_sweep_surface.py`: 실제 USD에서8종 물체와 선반의 시각 메쉬 BVH를 공유한다. Test는256환경 단위의 가변 크기1mm 격자를 처리한다. 모든 실제 삼각형을 YZ 격자에 투영하여 후보 pixel만 선택하고, 원래 Warp BVH가 사용하는 native Woop ray/triangle 판정으로 깊이를 계산한다. 환경별 scale/yaw/translation 역변환은 유지한다. 양수 깊이의 float bits와 source를 단일 uint64 atomic_min key로 선택해 경합과 동률 순서를 처리한다. 선반의 가림은 기존 BVH 질의를 사용한다. 일반 helper의 기본값은 기존 BVH/CPU/64경로다. GPU에서4연결 성분·노출 폭·최대 타겟 조각·대표픽셀을 계산하고 최종 좌표만 회수한다. 대표픽셀의 수학적 동률에서 기존 NumPy float64 반올림까지 재현한다. 장애물은 source/row-major 순서로 정렬하고16조각 초과 시 전체 결과를 CPU reference 방식으로 복원해 기존 fallback을 유발한다.
- `mdp/event_functions/stabilize_sweep.py`: 두 Test만 GPU backend를 사용한다. 실패 환경을 모아 장애물 제거·타겟 단독 관측을 한 번에 재시도하고 선택 행만 갱신한다. 원본 `reset_scene`과 기본 `snapshot` 경로는 보존한다.
- `mdp/common/stabilize_sweep_contact.py`: Test startup의 질량·관성 설정이 끝난 뒤 로봇/물체의 고정 로컬 COM을1회 저장한다. joint reset이 cache timestamp를 무효화하면 다시 연결한다. world COM·속도·힘·모멘트는 계속 현재 물리 상태를 사용한다. PhysX API와 Isaac 소스는 교체하지 않는다.
- `scripts/check_stabilize_sweep.py`: fallback 전 동일 입력을 reference/GPU 경로에 주어 좌표·valid mask·장애물 제거 여부를 비교한다. 실제 PhysX COM을 reset·부분 reset·physics step·접촉 이후 캐시와 대조한다. 느린 reference 검사는 reset 타이머 밖에서 실행한다.

## 최종 대조

| 항목 | 변경 전후 |
| --- | --- |
| Gym 등록·상속·Runtime·Scene·PPO | 동일.2048환경·rollout36·PPO8epochs×4minibatches 유지 |
| Command·활성 물체 초기 배치·IK·물성 | 분포·수치·실패 처리는 동일. 고정 로컬 COM의 조회만 캐시 |
| Test 비활성 물체 보관 위치 | shelf-local z52–82m에서 env-relative x3.0–4.35m, y−0.675–0.675m의4×4 grid와 각 slot의 활성 초기 Z로 변경. 관측 제외·중력off·환경 간 충돌 필터 유지 |
| Observation |67D policy·64D obstacles·XYZ 대표 표면점·EEF 변환·episode별 고정 snapshot 유지 |
| Action·제어·시뮬레이션 |12D·physics0.01초·decimation2 유지 |
| Reward·Gate·Termination·Curriculum | 함수·계수·순서·일정 동일. Reach30·Stabilize Gate·Sweep Only Gate 없음 유지 |
| 원본 두 환경/Finger | 기존 코드 경로 보존. 새 observer·COM 캐시는 두 Test만 선택 |
| 학습 로그 | 기존 `logs/rsl_rl` 변경 없음. 진단 학습 산출물은 `/tmp/stabilize_perf`에 분리 |

AST 대조에서 기존 surface/contact 함수와 클래스는 변경되지 않았다. event 함수 중 변경된 기존 정의는 `snapshot`의 opt-in 분기와 `reset_scene_finger_test`뿐이다.

## 검증 중

최종 실제 학습 iteration 수치와 검증 산출물은 실행 완료 후 기록한다. GPU 합성2048장면·5,061만 ray는0.139/0.136초였고, GPU16장면 차등 검사에서 좌표·조각 수·순서·ray 수가 reference와 일치했다. 이는 실제 학습 iteration 시간과 별개다. bundled Warp1.8.2 CPU72개(기존 reset·관측·보상·Gate, 배치/연결 성분 차등, COM cache)가 통과했다. 실제 Isaac 통합에서 bundled Warp1.8.2와 standalone Warp1.15의 차이가 발견됐다.1.8은 kernel decorator의 module_options를 지원하지 않아 독립 kernel module의 fuse_fp 옵션을 compile 전에 설정한다. 또한 정수/실수 literal의32bit 중간 변환과 and 조건의 eager 평가 때문에 typed 상수와 음수 index guard를 명시적으로 구성한다.20px 노출 폭 임계값의 실제 반례도 회귀 검사에 추가한다. bundled Warp의 `native/builtin.h:1294`에서 signed int64 atomic_add가 min으로 구현된 라이브러리 결함도 확인했다. 비음수 픽셀 좌표 합은 정상 구현된 uint64 atomic_add로 누적하고 거리 차를 계산할 때 int64로 변환한다. 설치 라이브러리는 수정하지 않았다. 이 호환 수정 후 bundled1.8.2 CPU67개와 CUDA16장면 차등 검사가 통과했고, 합성2048장면은0.1298/0.1303초였다.


실제 통합 검사의 추가 확인: 동일 physics timestamp에서 연속 reset하면 설치된 Isaac의 `write_object_link_pose_to_sim`은 link pose와 COM state만 갱신하고 별도 world COM pose cache는 무효화하지 않는다. 초기 reset 직후 world COM을 검사한 다음 다시 reset하는 검사에서 기존 cache가 남았다. 로컬 COM 캐시 값은 fresh PhysX 값과 정확히 일치했다. 기존 동작을 바꾸지 않고 로컬 COM은 모든 reset에서, world COM은 실제 physics step 이후에 대조하도록 검사를 분리한다.

측정 하드웨어는 NVIDIA GeForce RTX3090 24GiB, driver560.35.03이다. IsaacSim5.1.0.0, IsaacLab commit `929f0fe1e9c1699efebf31b2ad0ab723a7d6e7e9`, PyTorch2.7.0, RSL-RL5.0.1을 사용한다. 일반 Python Warp 패키지는1.15.0이지만 시뮬레이터 실행은 bundled1.8.2를 사용하므로 최종 CUDA/통합 검증은1.8.2 기준이다. 최종 학습에는 profiler나 BLAS/OMP thread 제한을 사용하지 않는다.

유효 조건: COM 캐시는 현재 IsaacLab의 TimestampedBuffer/lazy property 규약과 Test의 고정 물성 수명에 의존한다. 향후 reset/interval COM·질량·관성 randomization을 추가하면 캐시를 해제하거나 해당 setter 이후 다시 생성해야 한다. IsaacLab 업그레이드 시 fresh PhysX COM 대조와 부분 reset 회귀 검사를 재실행한다. 단기 처리량 검증을 장기 정책 성능·모든 seed·후반 커리큘럼 처리량 보장으로 확대하지 않는다.

## 실제 메쉬를 이용한 추가 최적화

첫 plain2048환경 학습은16iterations를 요청했지만0–5가13.96/11.37/13.39/16.62/19.57/24.73초였다. 평균 episode 길이가2.85step까지 줄어 reset 횟수가 늘어났으며, 목표를 충족하지 못해 해당 진단 프로세스만 종료했다. 이 결과는 성공 측정에서 제외하는 warmup이 아니라 명시적인 실패 실행이다. 로그는 `/tmp/stabilize_perf_final_stabilize.log`다.

실제64환경의 시각 메쉬와 fallback 전 초기 장면을 캡처했다. YCB4종은 각각 약16,384triangles로12triangles의 합성 box fixture보다 복잡하며, 각 장면 격자는7,469–158,918ray였다. 실제 장면을2048행으로 반복하면167.6M ray이고 기존 batch observer는약0.77초였다. SAH BVH는약0.99초로 더 느려 채택하지 않는다. 배경 선반 질의 생략·전방 깊이 경계·활성 물체 목록은 관측을 유지하며 소폭 개선했다.

물체 배치에서는 `CircleResetLayout.sample_batch_size` 기본64를 유지하고 Test 인스턴스만512를 선택한다. 난수 생성은 chunk loop 이전에 끝나므로 결과와 후속 RNG가 동일하다.5seed×128/512/1024/2048행에서 이를 GPU exact 비교했다.2048행 sample 중앙값은214.89→56.53ms로 감소했고 Test scratch는약238MB다. 원본 sample의 계산은 그대로이며 기존64상수를 인스턴스 속성 참조로만 바꿨다.

64환경 실제 통합 검사는 seed0–2 reset, 기존 관측과 동일 입력 차등, 같은 seed의 Finger 초기화, 부분/자동 reset, 실제 물리 접촉, local/world COM 대조를 통과했다. 최종 성능 개선을 모두 연결한 후 통합 검사와2048환경 학습을 재실행한다.

실제 메쉬 최종 observer 벤치: 매 chunk의 큰 pixel/연결성분 workspace를 재사용하고 CUDA events로 단계 시간을 측정해 중간 전체 동기화를 제거했다. 실제 입력2048행에서256chunk의 전체 관측은0.2266/0.2211초, ray약102ms·연결성분약61ms·upload약2.3ms였다. 큰 GPU workspace는1,424,185,472bytes다. 원본8장면 및 기존 batch64장면과 좌표·component 결과가 일치했다. CPU 전체92개가 통과했고 변경 production5파일 mypy도 통과했다. 이 값은 대표점 추출만의 벤치이며 실제 PPO iteration 기준을 대체하지 않는다.

## 잦은 reset의 물리 계산 대기

raster256/COM/layout512 연결 후 실제2048환경6iterations는9.75/7.84/9.06/10.25/11.90/13.96초였다. 임시 step profiler가 포함된 진단이며 아직 목표 미달이다. 후반104step의36step 환산은 env11.665초 = reset4.355 + PhysX fetch5.590 + 나머지1.720초였다. physics fetch는 첫112step의48.6ms/substep에서 마지막24step의92.1ms까지 증가했다. 기존 fast reset이17개 고정 풀의 주차 물체까지 모두 깨우는 경로를 추가 병목 후보로 확인했다.

작은 실제GPU probe에서 중력off·속도0·원격 주차된 inactive에만 PhysX simulation interface put_to_sleep를 적용했다.55물체 호출은0.0569ms였으며 즉시 pose/velocity/gravity/simulation flags가 exact 동일했다. 다음 physics에서도 잠든 상태를 유지했고, pose 차이는 quaternion 정규화 수준 최대2.38e-7이었다. 기존 Tensor wake_up으로 즉시/다음physics 재활성화를 확인했다. API 실패로 오인한 초기 probe 정체는 과도한 atol=0 검사 예외 뒤 app.close가 멈춘 현상이며, API 자체는 정상 실행됐다.

대표점 bounds는 yaw-only reset에 맞춰 XY hull과 원래 Z극값 vertex만 extrema 후보로 선택한다. mesh/triangles·float64 연산 순서는 유지하며 실제20,480행 bounds가 이전3D hull과 비트 일치했다. bounds 처리시간은44.4→16.9ms/2048행이다.512/1024ray chunk는 전체 처리 이득이 작고 workspace가2.85/5.70GB로 증가하므로256을 유지한다.

최종 후보에서는 `_sleep_inactive_test_objects`를 Test reset 마지막에 연결했다. 학습 경로에서 is_sleeping readback은 하지 않고 stage ID·encoded prim path만 최초1회 저장한다. 기존 Finger 및 non-Test에는 연결하지 않는다. CPU 단위 검사는 부분reset object-major 인덱스·target/활성물체 제외·cache 재사용을 검사하며 실제GPU checker에서도 inactive sleep와 활성물체 awake를 확인한다.


### 철회한 inactive 물리 최적화

XY bounds와 inactive sleep까지 연결한 plain2048환경 학습은0–6iteration에서9.91/7.56/9.06/10.57/12.84/14.56/16.31초였다. 평균 episode 길이가2.41step까지 줄어 reset이 증가했다. sleep은 처리량 문제를 해결하지 못했으므로 helper·호출·검사 모두 철회했다. `/tmp/stabilize_perf_accepted_stabilize.log`의 accepted는 실행 당시 붙인 이름일 뿐 합격 결과가 아니다.

후속으로 inactive에만 Tensor `set_disable_simulations`를 적용하고 reset 전에 복원하는 probe를 실행했다. flag=enabled·gravity on·awake를 회수했지만 재활성화 장애물은6physics step 동안 pose와 속도가 고정됐다. 한 번도 disabled되지 않은 타겟은 같은 장면에서 정상 낙하했다. 원인은 미확정이며 물리 동작을 보존하지 못하므로 이 후보도 전부 철회했다. 최종 생산 경로에는 sleep나 simulation-off가 없다. CPU55개·문법·diff 검사를 다시 통과했다.


### 삼각형·연결 성분의 추가 병렬화

실제64장면 raw pixel owner/depth의 uint32 비트 일치 검사를14개 병렬화 구성에서 통과했다. 각 삼각형에4lane을 배정해 후보 픽셀을 나눠 검사하는 구성을 채택한다. 모든 lane이 같은 native Woop 판정과 uint64 최소 key를 사용하며 픽셀·깊이·source의 결과는 유지한다. sm80 이상에서는 warp 안에서 같은 component root의 정수 count/row sum/column sum/min/max를 먼저 집계하고 대표 lane만 atomic을 수행한다. CPU와 구형 GPU는 기존 scalar atomic 경로다.

최종 실제2048행 observer 벤치는0.158/0.158/0.156초(ray67–69ms, 연결 성분50–52ms)였다. 같은 세션의 변경 전0.202초에 비해 약22% 감소했다. 원본 observer8행 차등, 실제64행 raw pixel 차등 및 bundled Warp CPU89개 검사가 통과했다. 이 역시 실제 PPO iteration의 성공 판정을 대체하지 않는다.

### GPU profiler의 제약

로컬 Nsight2022.4로2048환경의 policy180–195를 캡처했지만, importer가 현재 CUDA의 driver API683(cuKernelGetFunction)를 알지 못해 부분 자료만 남겼다. 학습 프로세스 exit0만으로 유효한 GPU trace라고 판단하지 않는다. 남은 policy180/181에서 reset 직후 첫 physics가154.0/148.9ms, 둘째가19.7/19.9ms였으나, 전체 kernel 비중·CPU idle·원인은 이 불완전 자료로 확정하지 않는다. 새 도구는 시스템 설치나 드라이버 변경 없이 /tmp에서 준비한다.


### 유효한 GPU trace로 확인한 주 병목

Nsight2025.1.3을 NVIDIA 공식 패키지에서 `/tmp`로 풀어 사용했다. 시스템 설치·CUDA·드라이버 교체는 없다. 기존2022자료는 버전 호환 때문에 재변환할 수 없어 새2048 학습을 캡처했다. CUDA event tracing과 CPU sampling은 끄고 policy180–195만 계측했다. 이 trace는16policy/32physics/100,348kernel을 모두 포함하며 유효하다.

16policy wall5.990초 중 GPU busy union4.092초이며, PhysX `performIncrementalSAP`가2.369초를 차지했다. 첫 physics의 SAP는16회 합2368.537ms(회당123.932–182.587ms), 둘째는16회 합0.206ms(회당0.011–0.014ms)였다. 첫 physics 평균169.10ms 중 GPU합164.48ms여서 CPU scheduling 지연으로 해석하지 않는다. raw contact fetch224회1.139ms와 friction32회0.180ms는 주병목이 아니다. reset 텔레포트 뒤 충돌 후보 broadphase의 endpoint 순서 갱신이 핵심 비용이다. 기존 inactive z52–82m와 상판 약1.05m 사이 왕복은 구체적 원인 후보로 조사한다.

이 실행은 surface4lane/warp집계와 native 수치가 같은 reset state의 중복 setter 생략 후보를 포함했다. 첫5iteration은9.72/7.72/8.72/9.77/11.43초로 여전히 기준 미달이다. 후반 iteration은 profiler 수집 비용이 포함되므로 최종 plain 학습 증거로 사용하지 않는다.


### 채택한 비활성 물체 보관 위치 변경

높은 보관 위치와 상판 사이의 반복 텔레포트를 줄이기 위해 두 Test의 비활성16slot만 로봇 뒤(+X)의45cm 간격4×4 grid로 옮긴다. env-relative XY는 x3.0–4.35m, y−0.675–0.675m다. 최초 후보는 z1.1m였으며 최종 후보는 각 slot의 `_refactor_spawn_z`와 shelf-frame Z를 정확히 맞춘다(현재 수평 선반에서 world z약1.05m). `fast_reset_scene`의 선택 인자 `inactive_positions=None`은 기존 Finger/다른 환경의 동작을 보존한다. Test만 shelf-frame 위치 배열을 전달하며 sample의 난수 생성 뒤 inactive 행만 교체한다. 대표점 fallback으로 제거한 장애물도 native write 전에 같은 grid에 둔다. 활성 물체 배치·IK·목표·중력 설정·충돌 필터·simulation enable 설정은 유지한다.

실제 자산에서 max-scale1.1을 포함한 충돌 bbox의 원점 반경 상한은0.185664m다. grid 물체 사이 간격은 최소약0.07867m다. 로봇의 모든 관절 경로 길이와 충돌 bbox 반경, F/T mount를 합한 보수적 reach는1.478993m이며 가장 가까운 주차 표면까지1.33534m 이상의 간격이 있다. 선반 최대x−0.4965m와도3.31m 이상 떨어진다. 환경끼리는 기존 CollisionGroup 필터를 유지한다. 이 근거는 정상 작업 공간과 로봇의 도달 범위를 격리하는 것이며, 극단적인 속도로 작업 공간 밖에 발사된 물체의 모든 경로를 보장하지는 않는다.

4환경 실제 PhysX probe에서 같은 seed의 active native pose/velocity·IK·표면점·후속 RNG·gravity/simulation flags가 정확히 일치했다. 강제 fallback의 동일 grid, 비연속 부분 reset 격리, sensor roster 보존도 통과했다. 비활성 물체는101physics step 동안 정지하고 접촉0N이었다. slot16을 다시 활성화하면 첫 z속도−0.09810m/s로 낙하하고 실제접촉119.60N을 생성했다. 이번 probe의 실제 bbox 반경 최대는0.17864m였다. 이 결과는 `/tmp/stabilize_near_parking_probe.json`에 저장했으며, 이어 실제2048 학습으로 처리량을 확인한다.

### CCL 초기화와 연결 간선 최적화

연결 성분의 parent/area 초기화를 통합하고 배경 pixel의 불필요한 통계 쓰기를 생략했다. 같은 source가2×2 block을 채울 때 이미 다른 경로로 연결되는 수직 간선만 생략한다. 4연결성과 최소 row-major root는 그대로다. 실제2048장면 observer 중앙값은148.6→130.5ms, CCL은50.0→32.0ms였다. CPU91개와 CUDA에서4×4 binary mask65,536개 및3×3 background/두source mask19,683개를 SciPy 기준으로 대조했다. canonical root·area·row/column 정수합·min/max열이 모두 일치했다.

### 적용하지 않은 환경 ID 설정

설치된 PhysX의 heterogeneous scene(`replicate_physics=False`)에는 공개된 개별 actor environment-ID setter가 없다.4환경에서 zero-replica `replicate(stage,path,0,useEnvIds=True)`를 호출했으나 모두 False였고 native state/roster는 변하지 않았다. 기존 환경을 복제 가능한 단일 자산으로 바꾸거나, 유효 ID 없이 양수 `envIdInBoundsBitCount`를 지정하는 우회는 적용하지 않는다. `envIdInBoundsBitCount=0` 정밀도 설정도 아직 적용하지 않았다.


### 원래 활성 높이와 일치시키는 후속 변경

z1.1m 주차 후보의 plain2048 학습은0–8iteration에서8.27/5.78/6.27/6.74/7.47/8.31/9.28/9.99/10.85초였다. 초반만 기준을 통과하고 후반 reset 증가 때 실패했으므로 해당 진단 실행만 SIGINT로 종료했다. 전체32회 요청을 완료하지 못한 실패 결과로 기록한다. 파일은 `/tmp/stabilize_perf_near_parking_stabilize_result.json`이다.

고정5cm Z이동도 제거하기 위해 각 비활성 slot의 shelf-frame Z를 그 slot의 `_refactor_spawn_z`와 일치시킨다. kind/scale은 startup 고정이고 초기화가 yaw-only여서 활성 전환 전후 Z extents를 유지할 수 있다. 물리 도중 기울거나 떨어진 활성 물체를 복귀시키는 이동은 계속 필요하다. XY격자·로봇/선반 분리·활성 위치·난수·관측 규칙은 그대로다. 실제64환경1088개 원점 spawnZ는 약1.05m였다. CPU fixture에는 서로 다른 환경/slot의 Z를 넣어 상수 높이로 잘못 치환하지 않는지 확인했다.

### 중복 native reset 기록 생략

Test의 fixed-base root가 요청된 pose/velocity와 현재 native PhysX 값이 수치적으로 정확히 같으면 중복 root setter를 생략한다. object는 inactive→inactive이면서 native pose/velocity가 정확히 같은 행만 생략한다. 첫 reset·모든 active·활성 상태 전환·native 불일치 행은 계속 기록한다. wake-up도 실제 기록한 행에만 적용한다. +0/−0은 같으므로 이것을 비트 동일 판정이라고 부르지 않는다.

Isaac의 공개 writer가 갱신하는 link/state/COM/velocity/acceleration cache와 timestamp를 같은 규칙으로 갱신한다. native object-major 인덱스와 full-size setter 입력을 사용한다. 요청 속도는0이라는 Test 계약을 검사하며 gravity/collision/simulation-enable/sleep 설정은 변경하지 않는다. 설치된 Isaac writer와의 CPU 차등 및 실제4환경 probe에서 최초/부분 reset·상태 전환·native 작은 차이·lazy cache·다음timestamp·RNG 보존을 확인했다. 후속 활성화 slot의 중력과 실제 접촉도 통과했다. 이 경로는 `reuse_unchanged_states=False` 기본값으로 다른 환경에서는 사용하지 않는다.

이 최적화는 설치된 Isaac 내부 buffer/timestamp 규약에 의존한다. Isaac 업그레이드, reset 시 질량/COM 변경, 비영속 물체·비고정 base·0이 아닌 reset velocity를 도입할 때 현재 차등 검사를 다시 수행해야 한다. 현재는 고정 물성 Test만 사용한다.

최종 후보의 CPU 세 파일 통합103개 및 production6파일 mypy가 통과했다. mypy는 `--follow-imports=skip --ignore-missing-imports`이며 타입을 선언하지 않은 함수 본문 전체를 엄격 검사한 것은 아니다. 최종 GPU 통합 및 실제 학습 측정은 별도로 기록한다.


### 후반 reset 집중 구간과 추가 layout 최적화

slot별 활성 초기 Z와 일치시킨 plain2048 후보도25iterations를 기록하는 동안5.56–11.36초였고32회 기준은 미달했다. 평균 episode 길이가약1.4step인 후반에 reset이 거의 매 step 발생했다. `/tmp/stabilize_perf_spawn_height_stabilize_result.json`은 실패로 보존한다. 앞선 z1.1m 후보는 종료 신호 처리 중 추가 iteration까지 총11개가 기록됐으며 최댓값11.67초다. 이 추가 구간도 성공 집계에서 숨기지 않는다.

최신 slot별 Z 후보의 두 Test는 각각64환경/seed0–7 GPU 통합 검사를 통과했다. 원본 관측 차등, active native pose/velocity·IK·모든 RNG 일치, 부분 reset 격리, Gate/타임아웃 또는 Sweep Only 우회, 실제 접촉 수식, 비활성 정지·접촉0N, CollisionGroup 보존을 확인했다. 첫 parking 검사에서는 물리 후 이동한 live shelf를 고정 주차 기준으로 잘못 사용해2.42mm 차이가 났다. 검사 기대값만 default shelf+env origin으로 고쳤고 production은 바꾸지 않았다.

같은 검증에서 Shelf가 disableGravity=false, kinematic=false, 내부 fixed joint 없음인 동적 물체임을 확인했다. 전역 Z=0 ground가 지지하므로 환경 origins만 여러 Z층으로 분산하는 후보는 물리 동작을 보존하지 못해 채택하지 않았다.

RED ZONE까지의 거리 계산은 큰 중간 Torch 텐서와 다수의 CUDA 연산을 생성했다. 두 Test의 float32 CUDA layout 인스턴스만 네 변의 거리/inside 판정을 하나의 Warp kernel로 계산한다. 기본 `CircleResetLayout.red_distance`와 CPU/다른 dtype 경로는 그대로다. 원래 eager Torch의 덧셈·곱셈·나눗셈·clamp·sqrt·퇴화조건 순서를 유지하고 별도 kernel module에서 FMA를 끈다. Torch current stream을 사용하여 입력·출력 수명과 의존성을 보존한다.

생산 helper를 별도 Torch CUDA stream에서 검사한 거리8,304,000개가 bit-exact였고 valid grid와128/512/2048행 sample 출력·후속 RNG도 일치했다. full2048 layout 중앙값은57.907→29.272ms였다. CPU 전체3파일106개와 production6파일 mypy가 통과했다. `/tmp/stabilize_red_distance_production_gpu.json`, `/tmp/stabilize_latest_cpu.log`, `/tmp/stabilize_latest_mypy.log`에 근거를 남겼다. 이 변경을 포함한 실제 후반 GPU/CPU profile과 최종 plain 학습을 이어서 수행한다.

## 후반부 재측정: 비활성 물체 위치 변경 이후

실제2048환경의 policy step324–339를 Nsight Systems2025.1.3와 step 범위 cProfile로 함께 측정했다.16 policy/32 physics marker가 완전하고107,057 CUDA kernel, importer 오류0을 확인했다. 프로파일 구간 wall4.797초 중 GPU activity union2.288초였다. SAP는 이전16step의2,368.743ms에서282.327ms로 약88.1% 감소했다. 첫 substep의 SAP14.64–19.99ms, 둘째0.013–0.040ms이며, 초기/활성화 시 대형 Z 이동이 주요 broadphase 비용이었다는 진단을 뒷받침한다.

이후 남은 GPU 비용은 observer1,018.166ms(삼각형 투영/raster decode/init703.838ms, CCL313.493ms), PhysX union827.996ms(SAP 포함), app stream403.163ms였다. RED fused kernel47회는4.805ms, IK16회는1.627ms로 IK 자체는 여전히 병목이 아니다. 일반 Torch kernel에는 별도 layout NVTX가 없어 app stream의 전체를 layout 비용이라고 해석하지 않는다.

cProfile의 같은16step은 전체4.726초, reset2.743초, observer1.449초, fast reset0.835초(그중 circle sample0.509초), physics0.962초였다. 프로파일러가 실행 시간을 늘리므로 이 수치는 원인 분해용이며10초 합격 판정에는 사용하지 않는다. 최종 판정은 profiler 없는 원본 train.py 실행으로 수행한다. 원시 분석은 `/tmp/stabilize_nsys_spawn_height_late_analysis.json`, 세부 분류는 `/tmp/stabilize_nsys_spawn_height_late_breakdown.json`이다.

## 추가 배치·미사용 관측 계산 개선

RED 거리 fusion만 적용한 plain 학습은17/32 iterations에서최대10.19초로 실패했다. iteration12/14/15/16이10초 이상이었으며, 완료되지 않은32회를 성공으로 집계하지 않는다. 검사 결과 `/tmp/stabilize_perf_fused_red_stabilize_result.json`.

다음으로 Test의 셀 선택을 환경당128 CUDA threads의 협력 계산으로 합쳤다. 각 thread는 연속된 셀 구간을 세어 원래 row-major prefix/searchsorted 선택을 재현한다. 셀 경계·RED 거리·앞서 배치한 물체와의 거리·요청 수·최초 실패 slot·partial 배치를 보존한다. FMA를 끄고 Torch current stream에서 실행한다. 기존 command/물체 선택/난수 추출 코드는 공유하며, 선택된6개 물체의 좌표·yaw 조립만 한 번에 벡터화한다. default `cell_selector=None`의 기존 Torch loop는 그대로 남는다. Test의 float32 CUDA,16,000셀 이하 입력만 새 selector를 선택하고 다른 환경·CPU·다른 dtype/셀 수에는 기존 경로를 유지한다. 대형 prefix/distance scratch도 새 selector에서는 만들지 않는다.

실제 CUDA nondefault stream에서128/512/2048행의 raw index/enabled/complete/failed_slot, 전체 sample 출력·RNG, 실패 payload를 원본과 대조했다. 2048행 median은 RED fusion 이후29.241ms에서 협력 셀 선택+벡터 조립11.244ms로 감소했다. 이는 배치 함수 단독 측정이며 최종 iteration 합격 근거와 구분한다. `/tmp/stabilize_circle_vectorized_gpu.json`에 기록했다.

Test 정책이 사용하지 않는 기존 centroid visibility/packing도 `populate_legacy_observation=False`에서 생략한다. 기본값True는 Finger 경로를 보존한다. 기존 난수3회(shape·device·generator·순서와 swap0 예외)를 그대로 소비하고 미사용 legacy buffer의 선택 행만0으로 둔다. 비유효 파라미터의 예외와 그 시점의 RNG 진행도 대조했다. Test의 실제 관측은 기존 대표 표면점 buffer를 계속 읽는다.

최종 소스 기준 CPU3파일126개/13.27초 및 변경6파일 mypy가 통과했다. 실제 GPU checker의 Finger 기준 호출에서는 Test의 `red_distance`/`cell_selector` instance override를 임시 제거하고 batch64/default옵션을 사용한 뒤 finally에서 복원한다. 비교 대상은 실제 Test 옵션 전체이며 native 활성 pose/quaternion/velocity/관절/IK/RNG·legacy buffer 미사용·부분 reset을 추가 대조한다. 이 시점에 최종GPU64 재검사와 두 환경의 plain2048 학습 합격은 아직 진행 전/진행 중이다.

## 32회 중간 합격과 CPU 기하 준비 비용

협력 셀 선택+legacy 관측 생략 적용 후 Stabilize-Test의 실제2048환경 headless 학습32회가 모두10초 미만으로 통과했다. 최소5.23초·중앙값9.295초·최대9.89초이며, 첫 iteration을 포함하고 누락한 iteration은 없다. `/tmp/stabilize_perf_cooperative_stabilize_result.json`에 전32회 collection/learning/iteration 수치를 보존했다. 이 시점의 두 번째 환경과 후속 CPU bounds 변경은 아직 검증하지 않았으므로 최종 두 환경 합격과 구분한다.

최대값의 여유를 확보하기 위해 대표점 투영 bounds의 CPU NumPy 임시 배열 계산도 합쳤다. 기존 yaw-only support/all_support 정점과 double 산술 순서·float32 변환을 유지하는 Warp CPU kernel을 추가하며, generic helper의 기본 `bounds_backend='numpy'`는 보존한다. 두 Test만 명시적으로 `cpu_kernel`을 선택한다. immutable 정점/prefix 캐시와 shelf_max_x만 저장하고 geometry 객체 순환 참조는 만들지 않는다. GPU 관측 해상도·ray/triangle 판정·연결 성분·대표점 규칙은 그대로다.

실제 fixture와 무작위 yaw20,480장면에서 lower/upper/origin_x의 uint32 bit가 모두 일치했다. 미참조 정점의 최대X, XY hull 내부 정점의 Z 극값, inactive zero도 별도 검사했다. bundled Warp1.8.2의 CPU 단독 측정에서256행 median2.218→0.442ms,2048행19.761→2.804ms였다. `/tmp/stabilize_surface_bounds_cpu_bench.json`에 전체 반복 값을 보존한다. 이 변경을 포함한 최종 실제 observer와 두 환경 학습 검증은 후속 절에 기록한다.

## 최종 소스의 기능 검증

CPU bounds까지 반영한 생산 코드를 고정한 뒤 CPU3파일131개가16.40초에 통과했다. 변경한 생산6파일 mypy도 오류 없이 통과했다. CPU 통합 검사는 설치된 pip Warp1.15.0을 사용했고, 실제 시뮬레이터·추가 CUDA 차등 검사는 Isaac 번들의 Warp1.8.2를 사용했다. 타입 검사 옵션은 앞서 기록한 제한을 유지한다.

최종 생산 bounds를 실제8종 메쉬로 다시 검사했다. CPU20,480장면의 bounds와 CUDA64장면의 raw pixel image·2048장면의 전체 표면점 관측이 NumPy bounds 경로와 bit-exact였다.2048행 준비 계산 중앙값19.011→2.701ms, 전체 observer 중앙값129.914→114.707ms였다. CPU 조건별8회·전체 observer backend별5회 원시 시간은 `/tmp/stabilize_surface_bounds_production_cpu.json`과 `/tmp/stabilize_surface_bounds_production_gpu.json`에 보존했다.

두 Test 모두 최종 코드로 GPU64환경·seed0–7 통합 검사를 완료했고 exit0이었다. 최적화 override를 제거한 Finger 기준 호출과 실제 Test 호출을 대조했다. 활성 native pose/quaternion/velocity·관절·IK·RNG, 대표 표면점·fallback, legacy centroid buffer 미사용/선택 행0, 부분 reset 격리, 실제 COM·접촉 모멘트, Gate/타임아웃과 Sweep Only 우회를 통과했다. 비활성 정지·접촉0N, 재활성화 후 물리 반응과 기존 collision group도 검사했다.

```bash
PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 WARP_CACHE_PATH=/tmp/stabilize_warp_cache /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 64 --task Inspire-Stabilize-Sweep-v0-Test --audit-resets 8 --output /tmp/stabilize_gpu_accepted_stabilize_64.json > /tmp/stabilize_gpu_accepted_stabilize_64.log 2>&1
PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 WARP_CACHE_PATH=/tmp/stabilize_warp_cache /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 64 --task Inspire-Sweep-Only-v0-Test --audit-resets 8 --output /tmp/stabilize_gpu_accepted_sweep_only_64.json > /tmp/stabilize_gpu_accepted_sweep_only_64.log 2>&1
```

기준 commit과 package Python299파일을 대조해293파일이 byte-identical임을 확인했다. 변경6파일의 opt-in 분기를 제거한 기존 Finger/default 계산 경로는 AST가 일치했다. 모든 환경 등록·Scene/Command/Observation/Action/Reward/Gate/Termination/Curriculum/Event 설정·runtime·PPO와 `train.py`도 보존됐다. 별도 에이전트가6파일과 설치된 Isaac writer를 다시 읽고 관측·물리·난수 계약을 검토했으며 기능상 잔여 지적은 없었다.

## 최종2048환경 학습과 범위

최종 CPU bounds 변경 이후 추가 생산 코드 수정 없이 다음 두 명령을 각각 완료했다. 출력 파일·checkpoint는 `/tmp`에 분리했고 기존 `logs/rsl_rl`은 수정하지 않았다.

```bash
PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Only-v0-Test --headless --num_envs 2048 --seed 42 --max_iterations 32 agent.experiment_name=/tmp/stabilize_perf/final_bounds_sweep_only > /tmp/stabilize_perf_final_bounds_sweep_only.log 2>&1
PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Stabilize-Sweep-v0-Test --headless --num_envs 2048 --seed 42 --max_iterations 32 agent.experiment_name=/tmp/stabilize_perf/final_bounds_stabilize > /tmp/stabilize_perf_final_bounds_stabilize.log 2>&1
```

검사기는 iteration0–31의 연속성·완전성, 유한한 collection/learning/iteration 값과 합산 일치, 출력 반올림을 고려한10초 미만 상한을 검사했다. 전64회 중 제외한 회차와10초 이상인 회차는 모두0개다. 각 실행은2048×36×32=2,359,296개 transition을 수집했다. 최종 결과 파일은 `/tmp/stabilize_perf_final_bounds_sweep_only_result.json`과 `/tmp/stabilize_perf_final_bounds_stabilize_result.json`이며 원시 배열을 위 영구 검증 JSON에도 포함한다.

측정 장비는 RTX3090 24GiB·i9-9900K이며 NVIDIA driver560.35.03, Isaac Sim5.1.0.0, Isaac Lab repository2.3.2(`929f0fe`), PyTorch2.7.0, RSL-RL5.0.1, simulator Warp1.8.2를 사용했다. 최종 Stabilize의 collection 중앙값8.4385초·최대9.096초, learning 중앙값0.347초였고, Sweep Only의 collection 중앙값8.292초·최대8.836초, learning 중앙값0.357초였다. 시뮬레이터 초기 생성에는 여전히 수 분이 걸린다.

의도적으로 달라진 물리 상태는 비활성 물체의 주차 XYZ이며, 미사용 legacy centroid buffer의 선택 행은0으로 둔다. 활성 배치·IK·난수 진행·관측 규칙·보상/Gate·시간 간격·환경 수·학습량은 유지한다. 정상 작업 영역 밖의 주차 공간과 현재 충돌 필터에서 검증했으며 비정상적인 고속 발사 물체와의 모든 접촉 가능성을 증명한 것은 아니다. 고정 local COM cache와 native writer 생략은 현재 Isaac buffer 규약과 고정 물성에 의존하므로 물성 reset·자산·Isaac 버전 변경 시 재검증해야 한다.

이번 결과는 이 장비와 seed42의 유한32회 실행에 대한 성능 검증이다. 다른 장비·모든 seed·장기 학습의 매 iteration 시간과 학습 성공률을 보장하지 않는다. 일반 Stabilize/Sweep Only와 Finger의 성능을 개선했다고 주장하지 않는다. 원본의 최초 진단은 첫 iteration을 완료하지 못했으므로 사용자 보고90초를 직접 재측정한 baseline으로 사용하지 않는다.

최종 검증 JSON은 `--require-accepted` 검사기를 통해 생성했고 모든 성능·GPU 계약·현재 소스 해시·CPU/mypy/CCL·주차·유효 profile gate가 통과했다. 전체64회 시간, 양쪽 GPU64 결과, source hash, 차등 검사와 실패/기각 이력을 포함하며550,615bytes다. SHA256은 `960dbbd9ec4fe24cd758d0fbf30db3d963d8c95fd89c7fe4f029e1edbc293517`이다.

변경 Markdown5개의 수식 검사와 root·문서 저장소의 `git diff --check`가 통과했다. 문서 저장소4파일의 링크331개를 검사해 오류0개였다. 패키지 README의 링크166개 검사에서는 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1개가 남았으며, 기준 commit에도 같은 링크가 있음을 확인하고 이번 범위 밖으로 보존했다. 새 성능 링크는 유효하다. 자동 Markdown 검사 결과이며 별도 렌더링 확인은 하지 않았다.
