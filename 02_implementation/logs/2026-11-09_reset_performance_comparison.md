# Relative-IK Test와 contact_manipulation_symmetric 리셋 성능 검토

## 요청·범위·근거 수준

사용자가 지정한 `envs/wrench_refactor_relative_ik_test_envs.py`와 비교 저장소의 `src/contact_manipulation_symmetric` 실제 호출 경로를 분석했다. 사용자 기반 commit은 `3501ffb`, 비교 저장소는 `8a38b58`이다. 일반 v0_2-Test, v0_2_1-Test, v0_2_2-Test, v0_2_2_1-Test, v0_2_2_2-Test는 같은 reset event/runtime을 사용한다. 별도 v0_2_1-Reset-Test는 구분한다.

이번 요청은 수정 방안 검토다. 실행 코드·설정·학습 로그는 변경하지 않았다. 신규 GPU/PPO 성능 측정을 하지 않았으며, 기존 문서의 측정과 현재 코드에서 확인한 구조적 차이를 구분한다. 현재 장비에서 양쪽 Collection Time 차이를 재현하거나 개선율을 검증한 결과가 아니다.

기존 근거는 [2026-11-08 Collection 프로파일](2026-11-08_collection_profile.md), [Reset-Test 구현 및 보류 기록](2026-11-09_relative_ik_reset_test.md), 비교 저장소 `docs/TRAINING_LOG.md`의 10465–10515행이다. 기존 프로파일이 가리키는 `outputs/collection_profile` 원자료는 현재 workspace에 없어 재분석하지 못했다. 이 때문에 현재 Test의 병목 비율을 과거 Relative-IK-v0 수치와 동일시하지 않는다.

## 실제 리셋 경로 비교

| 항목 | 사용자 일반 Relative-IK Test | 비교 symmetric |
| --- | --- | --- |
| 물리/정책/rollout | 100Hz/50Hz/36step | 100Hz/50Hz/36step |
| 에피소드 | 독립 10초, 실패 시 부분 reset | 8초 및 공유 장면 만료 시 전체 truncation |
| 물체 구성 | 17개 pool, 타겟1+장애물0–6 활성 | 기본 요청15–25개, 공유 활성 mask |
| 크기 | 환경별 생성 시 고정, 독립 크기 | 공유 geometry와 replicate_physics=True |
| 배치 | 부분 reset마다 각 환경 새 목표·배치 | 새 장면은 env0에서 한 번 생성, 전체 broadcast |
| 부분 reset | OBB search→상태 기록→가시성→IK | 저장 배치·비전 복원→새 연속 초기 자세 IK |
| IK | Torch FK/DLS, 작은 배치 CPU 이동 | FP32 CUDA에서 Warp fused IK 및 CUDA Graph 탐색 |
| 비활성 물체 | 높은 위치 주차, gravity off, reset마다 flags 설정·wake | 주차+kinematic, 동일 mask의 부분 reset은 flag 변경 생략 |
| 물성 | 일반 Test는 startup 고정 | 여기서는 초기 자세/배치 경로를 중심으로 비교 |

따라서 화면에 보이는 물체 수만으로 Collection 비용을 설명할 수 없다. 특히 양쪽은 리셋 시 매번 생성하는 정보량이 다르다. 비교 환경도 매번 새 로봇 자세를 샘플링한다. ‘IK도 모두 캐시에서 복사’한다고 해석하면 틀린다.

### 사용자 경로

- `mdp/events/wrench_refactor_relative_ik_test.py:9`: prestartup geometry, startup physics. reset은 `reset_scene_to_default → reset_scene → reset_robot_from_goal_ik` 순서다.
- `mdp/event_functions/wrench_refactor.py:80`: 개수 추첨, layout 생성, 17개 pose/velocity 기록, gravity flags, 초기 관측/가시성 계산.
- `mdp/common/wrench_refactor_layout.py:70`: 16개 중6개 후보를 선택해 OBB search. 후보64·restart4·pass2·최대3회 추가 실패 재시도. 목표/개수를 낮추는 fallback은 없다.
- `mdp/common/bbox_scene_layout.py:139`: search는 tensor 계산이나 Python의 2×6 반복이 있다. batch≤8은 CUDA 난수 생성 후 CPU search, 결과 GPU 복귀. 입력 검사와 결과 분기에는 host 동기화가 있다.
- `mdp/common/wrench_refactor_ik.py:130`: batch≤128은 CPU chain으로 이동한다. 최대80회 FK/Jacobian/DLS, 허용 오차 위치0.5mm·회전0.003rad. CUDA 경로의 `bool(done.all())`는 반복마다 동기화 가능성이 있다. 현재 일반 Test는 pose 후보1회이고 SVD 품질 검사는 꺼져 있다.
- `runtime/wrench_refactor_relative_ik_test.py:158`: native reset 전후 episode metrics·초기 관측 상태를 정리한다.

사용자의 reset IK는 `sim.step()`로 팔을 이동시키지 않는다. 따라서 settle physics step 제거를 주요 개선안으로 제시할 근거는 없다.

### 비교 경로

- `mdp/events.py:8994`: 공유 template이 없거나 deadline이 되면 `_build_episode_batch`를 env0 하나로 호출한다. 부분 reset은 기존 template/sample을 사용한다.
- `mdp/events.py:8903`: `_shared_reset_batch`는 배치·비전을 expand하고 새 robot start를 생성한다. 정상 행은 GPU tensor로 유지하며 bounded search 끝에서 실패 여부를 host로 한 번 전달한다.
- `mdp/events.py:6430`: 입력 geometry/scene cache, power-of-two batch bucket, 고정 scratch buffer, acceptance mask, CUDA Graph replay로 작은 연산 dispatch를 줄인다.
- `config/ur5e/scene.py:905,1319`: FP32 CUDA solve는 `_arm_ik_kernel`을 사용한다. 반복·FK·Jacobian 풀이를 kernel 내부에서 수행한다. Python에서 48회 반복하며 GPU 결과를 읽는 방식이 아니다.
- `mdp/events.py:8881`: 선택 환경의 상태와 metadata를 기록하고 sensor reset 및 `sim.forward()`를 수행한다. forward는 물리 시간을 진행하는 step과 구분해야 한다.
- `mdp/terminations.py:22`: 공유 scene deadline에서 최근 재시작한 환경까지 timeout 처리해 전체를 함께 교체한다. 이 정책을 가져오면 사용자 독립10초 episode 계약이 바뀐다.

현재 비교 설정은 `generation_mode="sequential"`이다. 저장소에 큰 initial catalog 자산이 있다는 이유로 현재 reset을 사전 생성 catalog lookup이라고 설명하면 안 된다. catalog 초기화는 parameterized/clutter 모드의 조건부 경로다.

## 기존 측정이 알려 주는 범위

사용자 측 11월8일 Relative-IK-v0/2048환경/RTX4070의 기록:

| 항목 | CPU fast path 적용 후 기록 |
| --- | --- |
| Collection | 워밍업 제외 평균7.310초 |
| reset 전체 | 36step당2.914초 |
| IK event / solver | 1.333초 / 0.838초 |
| scene reset / OBB search | 1.123초 / 0.816초 |
| IK 표시 박스 | 0.273초 |
| PhysX fetch_results | 1.865초 |

함수 시간은 포함 시간이며 서로 중첩된다. Collection 평균은 워밍업 제외, 함수 집계는 전체4iteration으로 기준도 다르다. cProfile은 GPU 대기를 호출 시간에 포함할 수 있다. 현재 Test의 확정 비중이나 순수 kernel 시간으로 해석하지 않는다.

당시144step에서141회 부분 reset, 평균4.49환경·최대10환경이었다. 전체2048개라도 실제 reset은 아주 작은 batch가 거의 매 step 들어왔다. 이것이 큰 GPU를 써도 작은 Torch 연산의 고정 비용이 남는 이유다. CPU 우회는 이미 적용돼 있으며 새 해결책이 아니다.

비교 저장소는 RTX3090/1024환경의 native 검사에서512행 부분 reset 54.453/85.515/44.415ms를 기록했다. 새 장면 full reset은 최초6183.280ms, 이후1482.597/1348.039ms였다. PPO Collection 측정이 아니며, GPU·환경 수·batch 크기·과업이 달라 직접 속도비를 계산하지 않는다. 공유 경로에서 부분 reset 중 layout/ray 호출이 증가하지 않았다는 검증은 코드 설명과 일치한다.

과거 사용자 수치의 규모만 보면 reset이 약40% 수준이다. 이를 거의 제거해도 Collection은 대략4초대 비용이 남을 수 있다. 집계 기준이 달라 이는 대략적인 사고 실험이며 현재 환경의 성능 하한은 아니다. reset만 바꿔1–2초를 보장할 수 없다.

## 권장 수정 순서

### 1. 학습 중 IK 박스 표시 중단

`envs/wrench_refactor_relative_ik_test_envs.py:34`의 `debug_initial_ik_bounds=True` 때문에 reset마다 `_update_initial_ik_bounds`가 실행된다. 해당 함수는 reset 대상만 버퍼를 고친 뒤 **전체 active 환경**을 `VisualizationMarkers.visualize`에 넘긴다. 2048환경에서24개 edge씩49,152개다. native marker는 translation/orientation/scale/index를 CPU NumPy로 변환해 USD에 쓴다. headless라는 이유만으로 이 직접 호출이 없어지지 않는다.

학습에서는 flag를 끄고 play/디버깅에서만 켜거나, 선택한 소수 환경만 표시하는 방식이 가장 간단한 첫 변경이다. 물리·관측·보상 분포는 유지할 수 있다. 과거 측정의 약0.27초 규모라 단독으로 대폭 개선을 기대하지 않는다. EEF frame 등 다른 debug 표시도 별도 계측 대상으로 둔다.

### 2. 현재 IK 수식을 유지한 fused 구현

`ResetArmIK.solve/forward`의 USD joint frame·EEF offset·DLS damping0.02·step cap0.15·80회 상한·관절 제한·수렴 조건을 보존하며 Warp kernel 또는 고정 반복 CUDA Graph로 옮긴다. 작은 batch도 GPU에 남기고, 완료된 행은 mask로 각도 갱신을 멈추며 최종 성공 판정만 host로 가져온다. 같은 목표/초기 seed에서 현재 solver와 오차·성공 여부·관절각을 비교한다.

비교 repo의 solver를 그대로 복사하면 안 된다. 회전 오차 가중, 초기 seed, 수렴 판정, TCP offset, 관절 clamp가 다르다. 실행 방식만 참고한다. 기본 FK·관절 한계 등 불변 입력도 startup에서 캐시할 수 있다. Graph capture/JIT 준비 비용은 steady-state 측정과 분리한다.

### 3. OBB search의 dispatch·동기화 축소

현재 목표·개수·선택 body·후보64·restart4·pass2·tie-break·재시도 계약을 유지한 채 고정 batch bucket과 GPU graph/fused search를 검토한다. padding 행은 RNG를 추가 소비하거나 선택 결과에 영향을 주지 않게 하고, 난수는 기존 shape/순서로 외부 생성해 입력 buffer에 복사하는 방안부터 시작한다.

불변 크기/유효 범위 검사는 startup으로 이동할 수 있으나 동적 목표/배치 검사를 무조건 삭제하지 않는다. 현재 작은 CPU 경로도 이미 최적화한 결과이므로 새 GPU 구현이 더 빠른지는 batch1/4/8/16 실측으로 판단한다. 초기부터 분포를 줄이는 후보 수 축소나 실패 시 기본 배치 반환은 권하지 않는다.

### 4. 중복 쓰기와 불변 geometry 전송 제거

- `apply_final_visibility`는 reset마다 IDs→CPU NumPy→반경 계산→GPU로 왕복한다. 크기가 고정이므로 보수적 반경을 startup에서 한 번 계산해 GPU에 저장하고 selected IDs로 gather한다.
- local layout에서 이미 아는 좌표를 가시성 입력으로 전달하면 물리 state를 읽어 shelf frame으로 되돌리는 작업도 줄일 수 있다. 실제 pose/COM 기준의 동등성 확인이 필요하다.
- 현재 native `reset_scene_to_default`는 robot 기본 관절을 기록한 후 IK event가 arm을 다시 기록한다. 최종 arm IK와 기본 hand를 합쳐 관절 상태를 한 번 쓰는 reset event를 검토한다. robot root·shelf·hand·속도·target 초기화를 빠뜨리면 안 된다.
- 현재 설치된 native 함수에는 rigid object collection default reset 루프가 없다. 따라서 ‘17개 물체를 default로 썼다가 다시 써서 두 배 느리다’는 주장은 해당 SDK에서는 맞지 않는다.
- gravity flag는 변경된 행만 setter 대상으로 삼는 방안을 측정한다. 활성 body wake-up의 물리 의미는 유지한다. 다른 repo의 공유 kinematic flag를 독립 크기/활성 mask 환경에 그대로 적용하면 안 된다.

이 단계는 주로 부가 비용 절감이다. IK/OBB보다 큰 병목이라고 확정하지 않는다.

### 5. 더 큰 개선이 필요하면 초기 상태 생성과 소비 분리

환경별 geometry를 유지하며 layout+goal+IK+active mask의 새 초기 상태를 큰 batch로 미리 생성하고, episode reset에서는 준비된 상태를 gather/write하는 queue 방식이 후보다. finite pool 재사용과 달리 소모한 상태를 새로 보충하면 초기 조건의 독립성을 더 잘 유지할 수 있다.

다만 생성 비용이 사라지지는 않는다. 실제 이득은 큰 batch 계산과 생산/소비 중첩에서 나와야 한다. 같은 GPU에서 refill하면 물리와 경합할 수 있고, queue refill 시간을 Collection 밖으로 옮기기만 하면 전체 학습시간은 개선되지 않는다. 커리큘럼/파라미터 변경 시 무효화, 환경별 크기 호환, RNG/seed 순서, queue 고갈과 메모리 비용을 설계해야 한다.

비교 repo와 동일한 ‘공유 장면+전체 주기 reset’을 채택하면 배치 생성은 더 크게 줄일 수 있다. 대신 동시에 경험하는 배치 다양성, 환경 간 상관, episode truncation 분포가 바뀐다. 단순 성능 보존 패치가 아니라 별도 연구 실험으로 취급한다.

## 기존 Reset-Test의 해석

기존 구현은16그룹·그룹당8상태·32회 선택마다 교체하며, cache hit에서도 기본 reset·state write·gravity/wake·가시성/노이즈·박스 표시·manager reset은 남는다. 작은 부분 reset batch가 여러 그룹에 흩어지면 초기 충전 중에는 계산 공유도 제한적이다.

더 중요한 차이는 **일반 Test는 startup 물성이 고정인데 Reset-Test는 매 reset마다 질량·관성·선반/물체/손 마찰을 재추첨하고 PhysX setter를 호출한다**는 점이다. 이는 사용자가 당시 요청한 의미 있는 기능이지만 순수 캐시 성능 A/B가 아니다. 효과가 작았다는 사용자 관찰은 보존하되, 물성 setter가 이득을 상쇄했다고 실측 없이 단정하지 않는다. 같은 물성 정책·같은 debug flag·충전 완료 상태에서 비교해야 한다.

## 실행 전후 검증 계획

1. 정확한 Gym ID, 장비, num_envs, checkpoint/정책 상태, seed, rollout36, dt/decimation, debug 설정을 고정한다. 양쪽1024와2048을 혼동하지 않는다.
2. 같은 초기 reset 입력을 batch1/4/8/16/64/2048로 재생해 IK·OBB·flags/state write·visibility·marker·manager 시간을 분리한다. component 계측 때의 synchronize 비용을 실제 Collection 측정에 그대로 섞지 않는다.
3. 한 번에 한 변경을 적용한다. marker off → IK → OBB → writer/cache 순으로 원인별 차이를 측정한다.
4. `src/inspire_sweep_baseline/scripts/train.py`로 실제 collection과 전체 iteration wall time을 확인한다. warm-up/JIT/cache fill/full scene refresh와 steady-state, median 및 tail latency, reset 호출 수와 batch 분포를 기록한다. 새 산출물은 outputs에 두고 `logs/rsl_rl`을 정리하지 않는다.
5. 부분 reset에서 비선택 환경 불변, 모든 속도/관측 cache/goal/hand target 초기화, OBB 수·영역·충돌 규칙, IK 허용 오차와 실패 판정, 난수 소비/분포를 검증한다.

이번 문서 수정의 전후 차이는 ‘검토 기록 없음 → 실제 호출 경로·개선 순서·미검증 범위를 기록’이다. 실행 코드/등록/상속/보상/물리/학습 설정은 그대로다. GPU 성능 개선, 학습 성과, 실제 rollout 동등성은 미검증이다.

문서 검증: Markdown math 검사1파일 통과, 저장소 링크 검사 errors=0, 양쪽 저장소 `git diff --check` 통과. 기존 루트 `.gitignore` 변경과 submodule 상태는 보존했다.
