# Revision-v1 / Revision-Test-v1 구현·리뷰·검증

[최종 구현 계약](../environments/REVISION_V1_ENVIRONMENT.md) · [개발 명세](../../01_plan/environments/2026-11-02_REVISION_V1_SPEC.md) · [명세 작성 기록](2026-11-02_revision_v1_spec.md)

## 요청과 기준 상태

- 사용자는 작성한 명세를 실제 구현하고 코드 리뷰로 의도한 변경만 적용했는지 검증하도록 요청했다. 기존 학습을 종료했으므로 GPU smoke를 허용했다. `play.py`는 실행하지 않았다.
- 기준 root HEAD: `408d3d9ce947a62f094d6f8c8693be2c07e2e32d`. docs HEAD: `1c5de3ad0a1a525c6d79bd083af6e58c9d51aa43`. IsaacLab gitlink: `929f0fe1e9c1699efebf31b2ad0ab723a7d6e7e9`.
- 시작 시 root에는 docs submodule 변경과 사용자 `docs/plan/PLAN8.md`가 있었고, docs에는 이전 분석·명세·그림 및 handoff 변경이 있었다. 이 작업을 보존했고 commit/submodule pointer 변경 명령을 실행하지 않았다.
- 구현은 기존 역할별 Revision 파일에 파생 클래스/함수를 추가하는 방식이다. runtime·기존 Final·v0 계산 함수·제어·관측을 수정하지 않았다. 공유 spawner에만 기본값 None의 선택적 kind override를 추가했다.

## 요청과 최종 차이 대조

| 요청 | 최종 적용 | 보존 확인 |
| --- | --- | --- |
| Object 비용 3분리 | tilt −30, obstacle displacement −150, acceleration −0.05/free 20 | 기존 순수 계산·mask·cap·history 그대로, 같은 값에서 composite 합과 일치 |
| 다른 보상의 5% 연동 제거 | 실제 대상인 wrist를 독립 callable로 분리, raw cap 1·weight −0.1 유지 | v0의 budget 구현은 그대로; obstacle contact 수식도 그대로 |
| 7개 커리큘럼 삭제 | None 비활성화, 정확한 10k 값 고정 | obstacle contact free 50N/−0.05, 12k 값 미사용 |
| 장애물 교대 증가 | 3/3 → 10k 3/4 → 12k 4/4 → 14k 4/5 | 기존 reset 시 적용·배치 fallback·실제 개수 계측 유지 |
| Hold 변경 | strict 3cm Gaussian, center raw2, 0.05m/s까지 감쇠 없음 | weight8, 기존 물리 유효성; parent outer tail 보존 |
| Entry/timeout 분리 | 최초 strict entry +30, timeout inclusive 성공 +40 | 기존 종료 조건·실패 동시 발생 처리 유지, 새 종료 없음 |
| Test 단일 차이 | 타겟 spawn kind만 cylinder | 크기·장애물 난수 소비·물성·관측·모든 보상/커리큘럼 유지 |
| 부모 직접 상속 | V1→v0, Test→V1, PPO도 동일 관계 | 기존 등록·PPO 수치 유지; 새 experiment_name만 추가 |

실제 EnvCfg의 v0→v1 diff는 rewards, curriculum, 초기 spawn의 Gray/White, 미사용 `goal_hold_outer_radius`뿐이다. v1→Test의 diff는 타겟 kind override 하나다. 각 PPO 차이는 experiment_name 하나다. 전체 차이 경로·active terms·fixed params는 probe JSON에 저장했다.

`RevisionV1RewardsCfg.__post_init__`에서 분리된 3개 term을 원래 object 위치에, entry를 timeout 직전에 삽입했다. 기존 나머지 term 상대 순서를 유지했다. 최종 보상 15개, 커리큘럼 3개다.

## CPU와 부모 보존

사용 Python: `/home/min/miniconda3/envs/env_isaaclab/bin/python`. ROS 경로에서 자동 로드되는 pytest plugin이 `lark` 부재로 collection 전에 실패해, 테스트 의존성 변경 없이 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`로 실행했다.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_revision_v1.py src/inspire_sweep_baseline/tests/test_revision_cfg.py src/inspire_sweep_baseline/tests/test_revision_layout.py src/inspire_sweep_baseline/tests/test_revision_observations.py src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_rewards.py -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_final_configuration.py src/inspire_sweep_baseline/tests/test_final_versions.py -q
```

결과는 각각 **60 passed**, **51 passed**, 합계 **111 passed**다. 새 CPU 검사는 실제 생산 함수를 import하고 Isaac Lab configclass 기반 harness를 사용한다. v0용 AST helper에는 새 stateful class 정의를 읽기 위한 ManagerTermBase binding만 추가했다.

검사 범위:

- 15개 보상 순서·weight·변경하지 않은 term 동등성, 3개 커리큘럼과 남은 두 일정 불변.
- 0/9999/10000/11999/12000/13999/14000/90000/rewind의 장애물 일정.
- Hold 위치/속도 경계·invalid mask·radius 동기화. 중앙16, 1.5cm8, 경계 안쪽1, 정확히 경계0.
- entry의 최초/재진입/부분 reset/동일 step cache, XY만 판정, dt 0.01/0.02/0.1에서 30/40/70 금액 보존.
- 별도 reward manager 없이 wrist raw 값이 기존 unlimited-budget raw 경로와 일치. first sample, stale/NaN sample, 부분 reset, cap 포함.
- 기존 composite와 분리 합 동등성, 비활성·비타겟 mask, displacement 합산 cap, acceleration 첫 sample/활성 전환/부분 reset 및 물체별 cap.
- 기존 Revision와 Final 설정·함수 회귀.

초기 테스트 fixture의 shelf quaternion 누락, 매 step reset한 row의 예상값, float32 cap의 미세 반올림 오차를 수정했다. 이 수정은 테스트 입력·기댓값만 바꿨고 실제 보상식을 바꾸지 않았다.

추가로 기준 commit의 기존 클래스/함수 AST 11개를 6개 Revision 파일에서 현재와 비교해 모두 동일함을 확인했다. 기록: `outputs/revision_v1_validation/parent_ast_preservation.json`. 공유 spawner default None 분기는 기존 kind와 scale 추첨 순서를 유지하며, 새 Test와 v1의 실제 생성 메타데이터 비교도 통과했다.

## 실제 GPU 검증

RTX 3090 24GB, Isaac Sim/Isaac Lab은 설치된 환경을 사용했다. sandbox 내부에서는 드라이버 접근이 안 되었지만 승인된 외부 실행에서 GPU가 정상 확인되었다. 기존 `omniverse://192.168.0.13` 서버의 선반과 NVIDIA YCB 자산을 사용했고 대체 선반·대체 형상을 사용하지 않았다. 기존 physics 설정은 변경하지 않았다.

Workspace 루트에서 실행한 명령:

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/tests/_revision_v1_probe.py --num_envs 64 --headless
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/tests/_revision_v1_probe.py --num_envs 64 --test-variant --headless
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/tests/_revision_v1_probe.py --num_envs 2048 --headless
```

모두 통과했다. 각 실행 seed42, 초기·최종 혼잡도 각32 control steps(합64, 물리128steps), 9개 iteration/reset 경계, 부분 reset을 검사했다. 물리 객체10·Actor121/Critic124·보상15·커리큘럼3, 유한 reward/obs, 고정값 불변, 현재 mask 유지 후 다음 reset에 수 변경을 확인했다.

- `probe_v1_64.json`: 초기 실제3/3. 12k의 1개 env에서 Gray 배치가 하나 부족해 평균3.984375를 기록했다. 요청 수4/4와 기존 best-effort OBB 배치 동작의 차이이며 임의로 배치 규칙을 바꾸지 않았다.
- `probe_test_64.json`: 타겟64개 모두 cylinder, 장애물8종 유지. `spawn_v1_64.npz`와 target 포함 전체 scale 및 장애물 kind 배열이 정확히 같음. 형상 override가 난수열을 밀지 않음을 실제 생성에서 확인했다.
- `probe_v1_2048.json`: 기본 학습 규모 초기화·rollout·부분 reset 통과. 요청과 실제 개수는 JSON에 별도 저장한다.

Test64와 v1 2048에는 실제 `env.step()` 이벤트 fixture를 추가했다. 물리 실행 후 목표 XY를 선택된 타겟 XY에 맞추고 기존 termination/reward manager를 그대로 호출한다. 세 번째 타겟은 실제 높이3m·vx2m/s 상태로 두어 고속 실패가 발생하도록 했다. 첫 두 row는 timeout 직전으로 설정했다.

| 실제 step 시나리오 | entry | timeout | 검증 |
| --- | ---: | ---: | --- |
| 최초 진입 + timeout | 30 | 40 | 같은 step 총70 |
| 기존 entry latch + timeout | 0 | 40 | 중복 최초 지급 없음 |
| 공중 고속 진입 + speed failure | 30 | 0 | 실패로 entry 차단하지 않음 |

RewardManager의 실제 dt 적용 후 금액, 자동 reset 전 latch 설정과 reset 후 해제를 확인했다. fixture는 probe에만 있으며 production의 목표·종료 동작을 바꾸지 않는다. 초기 v1 64 실행은 이 추가 fixture 이전이므로 event_lifecycle 결과는 Test64/v1 2048 JSON을 참조한다.

기존 선반 mass-properties 경고와 debug marker Fabric prototype 경고는 출력되었으나 실행은 완료되었다. 해당 경고를 이유로 물리·시각화 설정을 이번 범위 밖에서 변경하지 않았다.

## 짧은 PPO 학습

공식 `train.py`로 두 환경 모두 PPO 2 iterations를 완료했다. 모든 로그는 절대 experiment 경로로 `outputs`에 저장했다. `logs/rsl_rl`은 수정하지 않았다.

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Revision-v1 --num_envs 2048 --headless --max_iterations 2 --experiment_name /home/min/7cmdehdrb/grad/outputs/revision_v1_training --run_name smoke_2048
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Revision-Test-v1 --num_envs 64 --headless --max_iterations 2 --experiment_name /home/min/7cmdehdrb/grad/outputs/revision_v1_test_training --run_name smoke_64
```

| 환경 | run | steps | 결과 |
| --- | --- | ---: | --- |
| v1 / 2048 env | `outputs/revision_v1_training/2026-11-02_15-28-09_smoke_2048` | 147456 | 2 iterations 완료 |
| Test / 64 env | `outputs/revision_v1_test_training/2026-11-02_15-30-48_smoke_64` | 4608 | 2 iterations 완료 |

각 run의 `model_0.pt`와 `model_1.pt`를 CPU로 열어 전체 tensor(optimizer 포함)의 유한성을 확인했다. Actor 13개·Critic 12개 tensor가 갱신되었고 각 장애물 인코더의 weight/bias 4개도 모두 갱신되었다. TensorBoard에 15개 독립 `Episode_Reward/` 키가 기록되며 기존 combined object 키는 없다. 기록된 scalar도 모두 유한하다. 상세는 `outputs/revision_v1_validation/checkpoint_v1.json`, `checkpoint_test.json`, `tensorboard_v1.json`에 있다.

원본 콘솔은 `outputs/revision_v1_validation/train_v1_2048.log`, `train_test_64.log`다. 환경·학습 설정 snapshot은 각 run의 `params/`에 있다.

## 코드 리뷰

`/home/min/.agents/skills/code-review/SKILL.md`를 적용했다. 사용자가 지정한 개발 명세와 작업 시작 HEAD를 기준으로 commit 전 working-tree diff와 신규 테스트 파일을 검토했다. 새 commit이 없으므로 `git diff 408d3d9ce947a62f094d6f8c8693be2c07e2e32d -- src/inspire_sweep_baseline`의 working-tree 비교를 사용했다(3-dot HEAD 비교가 아님).

- Standards 독립 리뷰: **지적 0건**. 역할별 파일 구조·직접 상속·부모 보존·과업 범위를 충족한다. Wrist raw 코드의 제한된 중복은 기존 v0 동작을 수정하지 말라는 저장소 지침을 우선한 것으로 판단했다.
- Spec 독립 리뷰: **구현 누락/오류/범위 확대 0건**, 실제 이벤트 lifecycle 검증 보완1건. 보완 probe와 Test64 실행 결과를 재리뷰하여 **해소, 남은 지적0건**을 확인했다.
- 최종 대조에서 추가한 과업 변경은 명세의 표와 일치한다. observation/runtime/termination/기존 Final 파일은 변경하지 않았다.

## 미검증과 해석 한계

짧은 초기화·rollout·PPO 검증은 장기 성공률 개선이나 정밀 정지의 실현을 입증하지 않는다. 10k~14k 실제 장기 학습은 수행하지 않았고, 해당 일정은 iteration 설정·reset 경계 검사로 검증했다. Test는64환경으로 물리·학습을 검증했으며 별도의2048환경 실행은 하지 않았다. 연속 궤적의 control sample 사이 통과 검출은 원래 명세대로 추가하지 않았다.


## 문서·작업트리 최종 점검

아래 기존 점검은 2026-11-02 구현 작업 기준이다.

구현 계약, 활성 환경 색인, 패키지 README, 현재 handoff를 갱신했다. 변경5개 Markdown 수식 검사와 root/docs의 `git diff --check`는 통과했다. 문서 저장소의 변경4개 문서 링크 검사는 통과했다. README까지 포함한 전체 파일 링크 검사에는 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1건이 남아 있다(기준 commit README1395행, 현재1397행에도 존재). 이번에 추가한 링크는 정상이며 요청 밖의 역사 문서 경로는 수정하지 않았다. 사용자 `docs/plan/PLAN8.md`, 이전 분석·명세·그림, 기존 로그는 보존했다. commit은 생성하지 않았다.

## 2026-11-03 Test-v1 EEF 높이 임시 출력

- 요청: 사용자가 play에서 실제 높이를 확인한 뒤 바로 주석 처리할 수 있도록 reward 또는 termination에서 항상 출력. 기존 Test-v1 직접 수정이며 새 환경은 추가하지 않는다.
- 기준: workspace `e27edb5`, 문서 저장소 `5e6fb3f`. 시작 시 코드 변경 없음. 문서의 기존 handoff·활성 안내·v1 상세 수정과 standalone 문서 로그는 보존했다.
- 변경 전: 접촉 reward에서 EEF world z와 초기 작업면+120mm를 비교하며 출력 없음.
- 변경 후: `RevisionV1TestEnvCfg`에 `debug_print_eef_height: bool = True` 추가. 공유 reward `target_contact_below_height`에서 플래그가 참일 때 `(eef_z - initial_shelf_z - 1.05) * 1000`을 계산하여 env별 mm를 소수 첫째 자리까지 매 호출 출력한다. 접촉 여부와 무관하게 출력하며 flush한다. 설정 한 줄 주석 처리로 비활성화된다.
- 영향: Test-v1의 play 및 train에서 매 reward 호출 출력과 GPU→CPU 동기화 비용 발생. 부모 v0/v1은 플래그 기본값 False로 출력하지 않는다. 실제 shelf 움직임에 따라 기준을 바꾸지 않는다.
- 최종 대조: 변경은 Test 플래그와 reward의 출력 분기뿐이다. 등록·상속·Scene·Command·Event/reset·Observation·Action·reward 수치/판정·Termination·Curriculum·runtime·PPO는 유지하며 높이 제한도 추가하지 않았다. `logs/rsl_rl` 등 학습 로그는 수정하지 않았다.
- 검증: `env_isaaclab/bin/python`으로 변경 파일 AST 문법 검사 및 실제 reward 함수 AST 추출 실행. 초기 shelf z가 0/2m인 두 env에서 75.0/150.0mm 출력, 플래그 부재 시 무출력, 활성/비활성 보상 결과 `[1., 0.]` 동일 확인. 지속 테스트 파일은 추가하지 않았다.
- 미검증: Isaac Sim play/GPU rollout은 실행하지 않았다. 사용자가 기존 play 명령으로 실제 궤적과 출력값을 확인한다. 이 출력 자체는 누르기 원인이나 높이 제한 효과를 입증하지 않는다.

## 2026-11-03 Test-v1 임시 높이 시각화

- 요청·의도: 사용자가 적절한 EEF 높이 기준을 정할 수 있도록 작업면 위60/70/80/90mm에 반투명 얇은 면 추가. 곧 삭제할 순수 시각화이며 Test-v1 직접 수정이다.
- 기준: 같은 workspace `e27edb5`에서 앞선 높이 출력 변경과 기존 문서 사용자 변경을 유지했다.
- 변경 전후: `assets/scenes/revision.py`의 Test Scene에 helper 호출 한 줄 추가. 같은 파일의 임시 helper는 선반 초기 위치와 공통 작업면/크기 상수를 이용해4개 `AssetBaseCfg`를 구성한다. 면 중심 높이는60/70/80/90mm, 색은 파랑/초록/주황/자홍, 크기0.4×1.0m, 두께0.5mm, opacity0.12다. 기본 env0 world z는1.11/1.12/1.13/1.14m이며 각 환경 원점은 Scene이 적용한다.
- 물리와 수명: collision/rigid/mass props는 모두 None이고 contact sensor 활성화도 False다. 물체 collection에 넣지 않아 후보·관측·접촉 필터에 포함되지 않는다. 초기 선반 작업면 기준으로 고정하며 reset 또는 물체 이동에 따라 변하지 않는다. Test Scene의 `_add_temporary_eef_height_guides(self)` 한 줄을 주석 처리해 끄고, 최종 제거 시 helper도 삭제한다.
- 최종 대조: 이번 코드 diff는 Test Scene의 호출과 helper뿐이다. 부모 Scene, 타겟 cylinder 설정, 물리 물체10개, 등록·상속·Manager·reward·termination·제어·커리큘럼·PPO와 앞선 EEF 출력은 유지한다. 학습 로그를 수정하지 않았다.
- 검증: Python AST 문법 검사와 helper AST를 stub 생성자로 실행해4개 면의 위치·치수·opacity·물리 속성 None을 확인했다. 로컬 Isaac Lab `PreviewSurfaceCfg.opacity` 지원 및 shape spawner의 None일 때 collider/rigid/mass 미생성 분기를 확인했다. 코드 diff 공백 검사 통과. 문서3개 수식·링크와 문서 diff 공백 검사를 수행한다.
- 미검증: 실제 Isaac Sim 초기화·렌더링·GPU rollout은 실행하지 않았다. 실제 화면에서 투명도와 여러 면의 겹침 가독성은 사용자 play로 확인할 대상이다.

### 높이 면 spawn 경로 오류 수정

사용자 play에서 `Unable to find source prim path: '/World/envs/env_.*/TempEEFHeightGuides'` 오류가 발생했다. 기존 stub 검사는 실제 Isaac Lab regex spawn의 부모 존재 조건을 검사하지 못했다. `sim/utils/prims.py`의 실제 `clone` decorator를 AST로 추출하고 기존 env 부모만 있는 경로 resolver를 제공한 `/tmp/revision_height_spawn_check.py`로 수정 전 동일 RuntimeError를 재현했다. 이 검사는 USD stage 대신 단일 env 경로 resolver를 쓰며 렌더링 검사는 아니다.

중간 부모를 요구하는 `{ENV_REGEX_NS}/TempEEFHeightGuides/Height_{height_mm}mm`를 기존 환경 부모 바로 아래의 `{ENV_REGEX_NS}/TempEEFHeight_{height_mm}mm`로 변경했다. 같은 검사 명령 `python /tmp/revision_height_spawn_check.py`가 수정 후4개 경로 모두 통과했다. Scene AST 문법·workspace diff 공백 검사도 통과했다. 변경은 prim 경로와 설명 주석뿐이며 높이·색·투명도·물리 속성·Manager·이전 EEF 출력은 유지한다.

`nvidia-smi`가 NVIDIA driver 통신 실패를 반환하여 실제 Isaac Sim 초기화·렌더링·GPU rollout은 이번에도 검증하지 못했다. 경로 처리 재현 통과와 실제 화면 검증을 구분한다. 학습 로그와 사용자 변경은 보존했다.

### 시각화 높이90/95/100mm·불투명도90%로 교체

사용자 후속 요청으로 기존60/70/80/90mm 네 면 구성을90/95/100mm 세 면으로 교체했다. 색은 아래부터 파랑/초록/주황이며 opacity를0.12에서0.90으로 변경했다. 새 play 실행 시 이전 높이 면은 생성하지 않는다. 기존0.5mm 두께·0.4×1.0m 크기·초기 작업면 기준·충돌 없는 시각 자산·임시 helper 제거 방식을 유지한다. 수정은 helper의 높이/색 목록·opacity·개수 주석뿐이며 reward/종료/제어/학습 로그는 유지한다.

검증: 변경 Scene AST 문법과 높이 목록·opacity 정적 확인, 코드·문서 diff 공백, 변경 문서3개 수식·링크 검사를 통과했다. 실제 Isaac Sim 렌더링은 실행하지 않았다. 기존 실행 중인 프로세스에는 자동 반영하지 않으며 play 재실행으로 확인한다.


## 2026-11-03 임시 높이 계측 주석 처리

사용자가 Test-v1의 임시 print·높이 표시를 전부 주석 처리하고 v2 상속 여부를 점검하도록 요청했다. 활성 기준은 작업트리의 v1·v2·Test-v2-GT이며 기존 학습 로그와 다른 사용자 변경을 보존했다.

- `envs/revision_envs.py`: Test-v1의 `debug_print_eef_height: bool = True` 선언을 주석 처리했다.
- `mdp/reward_functions/revision.py`: 공통 접촉 함수의 임시 조건 분기·mm 변환·문자열 생성·print 전체를 주석 처리했다. 기존 접촉 force·높이 조건·반환값은 동일하다.
- `assets/scenes/revision.py`: Test-v1의 임시 면 생성 호출과 helper 정의 전체를 주석 처리했다. 높이90/95/100mm·색·opacity는 주석 안에 보존한다. cylinder 타겟 override는 유지한다.

변경 전3개 파일을 `/tmp/revision_debug_disable_before.json`에 저장했다. 실제 AST를 비교하여 이번 차이가 임시 설정·출력 분기·시각화 호출·helper 비활성화뿐임을 확인했다. 패키지 전체 Python AST에 활성 임시 print 문구·면 prim 경로·임시 helper 참조가 없음을 검사했다.

상속은 `RevisionV2EnvCfg → RevisionV1EnvCfg`이며 임시 설정이 있던 `RevisionV1TestEnvCfg`를 상속하지 않는다. `RevisionV2TestSceneCfg → RevisionSceneCfg`도 임시 시각화가 있던 `RevisionV1TestSceneCfg`를 상속하지 않는다. Test-v2는 v2, Test-v2-GT는 Test-v2를 상속한다. 따라서 v2 계열에는 원래도 임시 기능이 활성화되지 않았으며, 이번에는 공통 reward 함수 안의 비활성 출력 분기까지 주석 처리했다. 보상용95mm 조건은 그대로 유지한다.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest \
  src/inspire_sweep_baseline/tests/test_revision_cfg.py \
  src/inspire_sweep_baseline/tests/test_revision_v1.py \
  src/inspire_sweep_baseline/tests/test_revision_v2.py -q
```

결과: **20 passed (1.67s)**. 로그는 `/tmp/revision_debug_disable_pytest.log`다. 새 테스트 파일은 추가하지 않았다. 문법·AST·상속·보상 회귀를 확인했으며 GPU/GUI play는 재실행하지 않았다. 이미 실행 중인 프로세스에는 소스 변경이 자동 적용되지 않으므로 재실행부터 반영된다. 학습 로그는 변경하지 않았다.
