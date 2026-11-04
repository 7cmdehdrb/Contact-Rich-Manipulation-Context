# 2026-11-04 Wrench-v0 독립 환경 구현

## 요청과 기준

사용자는 `inspire_revision_test_v2`를 의미론적으로 계승하되 실제 환경 상속은 완전히 끊고 함수를 재사용하는 새 환경을 요청했다. 높이 제한120mm,3cm/0.005m/s 연속3초 성공 종료와 기존 수준 보상, RED 확장, 초기화/reset 랜덤화 분리와 collection1~2초 목표, Dead Zone10k 시작/3k 간격 −5°가 요구사항이다.

후속 답변으로 이름은 **`Inspire-Wrench-v0`**, 확장 폭은 제안한20mm를 사용했다. 손 진입 후방 사각형 전체를 RED로 바꾸는 해석은 사용자가 명시적으로 정정했다. 최종 구현은 **Gray 사각형을 유지하고 RED 확장에 맞춰20mm 후퇴**하는 것이다. 임시 해석대로 RED 사각형을 구현한 코드는 없다.

Workspace `main` HEAD는 `ba1aa88bf462c5263531379b0a67248ad2439552`, 문서 submodule `main` HEAD는 `c2deba2f5672450920c5e0377b2e1655752aeab6`다. 기존 작업트리의 Test-v2 TEMP 출력3개 파일, 문서 수정·미추적 기록을 보존했다. 시작 시21개 기준 코드 파일의 SHA256을 `outputs/wrench_validation/baseline.json`에 저장했고 종료 시 전부 동일함을 확인했다. 커밋·브랜치 이동·학습 로그 정리는 수행하지 않았다.

[최종 환경 계약](../environments/WRENCH_V0_ENVIRONMENT.md)에 등록, 상속, 모든 Manager와 보존 설정, 실행법을 정리했다.

## 구현과 영향

- `envs/wrench_envs.py`, `runtime/wrench.py`, `assets/scenes/wrench.py`, `agent/wrench_ppo_cfg.py`, 각 `mdp/<role>/wrench.py`에 독립 Cfg/runtime를 작성했다. 이전 환경 Cfg/runtime/Scene/PPO 상속 없음. 기존 자산 spawner·계산 함수·상태 term·모델·제어는 재사용한다.
- `__init__.py`에 정확히 `Inspire-Wrench-v0`를 등록하고 실험명을 `inspire_wrench_v0`로 분리했다. 기존 Gym 등록을 유지했다.
- `goal_reward_height_limit=0.12`, 초기 선반 작업면 기준 strict EEF gate를 유지했다. runtime에서 Hydra override 이후 contact limit을 동기화한다. 기존 Test-v2의 공통 높이 override 불일치가 새 환경으로 복제되지 않게 한 조치다.
- `SettledGoalSuccess`는 env별 정수 step counter와 동일 step cache를 가진다. dt0.02s에서150회 연속 valid이면 성공한다. d≤0.03, world3D 선속력≤0.005, 유한 위치/속도를 검사한다. 이탈/비유한은0, 부분 reset은 선택 행만0. 실패 term을 먼저 계산하고 실패 동시 발생 시 성공을 억제한다.
- `target_goal_success`는 실제 termination이다. 10초 도달만으로 보상을 받지 않는다. 성공+timeout 동시 표본은 성공으로 처리하고 truncation은 억제한다. +75는 `target_goal_success_bonus`에서 dt로 나눈 raw를 반환하여 실제 지급75를 유지한다. 기존 최초 진입 최대25를 유지한다.
- RED margin3→23mm. Gray 외곽은 새 RED 바깥65mm, 후방160×220mm Gray 사각형은 타겟→목표의 반대 방향20mm 이동한다. 공용 `LayoutConfig` 끝에 `rear_offset=0.0`을 추가하고 중심 계산에 반영했으며 기존 positional parameter 순서도 보존했다. 기존 기본값으로32장면의 전체 생성 결과를 HEAD 원본과 bitwise 대조했다.
- `WrenchLayoutBank`는 startup에서9개 일정 조합×환경별16개 후보를 생성한다. reset은 후보 tensor indexing만 하며 OBB 검색을 호출하지 않는다. 후보는 각 환경의 실제 scaled bounds에 종속적이다. 16개 후보를 복원추출하므로 이전의 매 reset 신규 난수 배치와 통계적 시간 상관이 다르다.
- 질량/마찰/관성 함수는 동일하되 mode reset→startup으로 옮겼다. 형상·크기·재질 buffer 준비는 원래도 초기화 시점이었다. 기존 환경은 매 reset USD topology를 다시 생성하는 구조가 아니었다.
- 중력 flag 적용은 전체 mask GPU→CPU 복사 대신 reset 행만 전송하고 CPU object-major buffer를 재사용한다. 물리 topology·body 수·park/활성 규칙은 유지한다.
- Dead Zone은 9999까지30°,10000에25°,13000에20°,16000에15°,19000에10°,22000에5°,25000부터0°. 기존 장애물3/3→10k3/4→12k4/4→14k4/5와 target speed schedule은 유지한다.

## 전체 최종 대조

| 분류 | 확인 결과 |
| --- | --- |
| 기존 환경 보존 | 기준21파일 SHA256 동일. Test-v2 TEMP 사용자 변경 포함 |
| 등록/상속 | 신규 ID·독립 EnvCfg/runtime/Scene/Manager/PPO. AST에서 이전 환경 ancestor/인스턴스 없음 |
| Scene/제어 | Test-v2 cylinder target·9 obstacle 후보·센서/스포너·기본 물리·OSC8D 보존. Scene 선언 복제와 target override 확인 |
| 관측/명령 | Action·Command·Observation 정의를 이름 정규화 후 전체 AST 동일성 확인. Actor121D/Critic124D·GT 경계 보존 |
| EnvCfg | 실제 configclass와 실제 EnvCfg post-init 실행 대조. Sim asset·별도 검증 그룹은 CPU double이며 실제 시뮬레이션 구성 비교로 해석하지 않음 |
| Reward | 실제 Manager Cfg에서 기존15항 순서·callable·params·weight 대조. 성공 항의 이름/함수만 교체,75 유지 |
| Termination | 기존4실패 동일, timeout success를 연속 settled success의 실제 termination으로 변경. miss timeout은 새 success 제외 |
| Curriculum | population·target_free_speed callable/params 보존, deadzone만10000/3000 첫 업데이트 포함 규칙으로 변경 |
| Event/reset | geometry/reset_all/material 함수 보존. bank startup 추가·reset spawn 변경·physics startup 이동·중력 전송 최적화 |
| Runtime | 기존 reset snapshot/센서 freshness/telemetry/iteration 유지. TEMP print 미포함, 공통 높이 생성 시 동기화 추가 |
| PPO | 기반 PPO 선언의 AST 동일성, experiment_name만 변경. RevisionModel 함수 구현 재사용 |
| 로그 | 성공 termination/reward 이름 변경. Metrics 이름·장애물 실제 수·layout_complete 유지 |

새 환경 함수와 설정의 요청 밖 보상 재조정은 없다. 물성 고정·유한 배치 후보·reset seed가 bank를 재생성하지 않는 점은 초기화/reset 분리로 생긴 의도적 동작 차이다. 이 최적화가 장기 학습 품질을 유지한다는 주장은 하지 않는다.

## 실제 검증

### CPU 회귀

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OMP_NUM_THREADS=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q \
  src/inspire_sweep_baseline/tests/test_wrench.py \
  src/inspire_sweep_baseline/tests/test_revision_cfg.py \
  src/inspire_sweep_baseline/tests/test_revision_v1.py \
  src/inspire_sweep_baseline/tests/test_revision_v2.py \
  src/inspire_sweep_baseline/tests/test_revision_layout.py \
  src/inspire_sweep_baseline/tests/test_bbox_scene_layout.py \
  src/inspire_sweep_baseline/tests/test_final_obb_layout.py \
  src/inspire_sweep_baseline/tests/test_revision_observations.py
```

**82 passed,4 skipped,7.08s**. skip은 CUDA가 없는 경우의 GPU 검사다. `outputs/wrench_validation/tests_final.txt`에 결과를 보관했다. 새 검사는 다음을 실제 production 함수/설정으로 확인한다.

- 거리/속도 정확한 경계·바깥1e−9·NaN/Inf, dt0.01/0.02/0.07/0.1의 필요한 연속 표본 수, 동일step 중복 호출, 부분reset, 이탈 시 counter0.
- 실패 동시 발생 시 성공 억제·+75 실제 지급·성공시 timeout 억제·비성공시 timeout 유지.
- 높이119.999/120/120.001mm에서 distance/Hold/contact 공통 strict gate.
- 10k/12k/13k/14k/16k/19k/22k/25k 전후 일정과 startup bank의 모든 조합 커버리지.
- RED 확대와 Gray 사각형 후퇴 및 Gray 보존. 9개 단계의 OBB RED 제외·Gray/White 분류·물체 간20mm 간격·보드 경계·목표 방향 범위.
- bank에서 환경별 bounds·바닥 정렬 유지, seed 재현, 부분reset의 다른 행 상태 보존, reset 중 검색 호출 시 테스트 실패, 중력 object-major 매핑, 관측 noise 재생성.
- 실제 Cfg term 순서/함수/수치 보존·독립 MRO·기존 설정 격리, 기존 Revision/Final 회귀.

첫 실행은 ROS pytest plugin의 `lark` 누락으로 수집 전에 실패했다. `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`로 해당 외부 plugin을 제외했다. 다음 실행의 CPU observation config import는 harness에 noise module이 없어 실패하여, 관측 전체 선언을 원본과 AST 동일성 대조하는 방식으로 검증했다. 생산 코드 오류를 숨기도록 noise 구현을 대체하지 않았다.

신규 소스/검증20파일의 Python compile 통과. 기준21파일 보존 결과는 `outputs/wrench_validation/source_audit.json`, 공용 OBB 원본 대조는 `outputs/wrench_validation/obb_default_audit.txt`다.

### 배치 비용 측정

```bash
OMP_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/tests/_wrench_layout_benchmark.py --num-envs 2048
OMP_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/tests/_wrench_layout_benchmark.py \
  --num-envs 64 --bank-size 16 --all-stages \
  --output outputs/wrench_validation/layout_all_stages_64.json
```

CPU float32·1thread·seed42·synthetic scaled bounds 조건이다. 실물8종과 PhysX 실행은 포함하지 않는다.

| 측정 | 2048환경,1단계×2후보 | 64환경,9단계×16후보 |
| --- | --- | --- |
| 기존 Revision OBB 검색1회 | 4.03684s | 0.14025s |
| 확장 Wrench OBB 검색1회 | 4.01065s | 0.12721s |
| startup bank 생성 | 7.02918s | 15.78908s |
| reset 후보 선택 평균20회 | 0.000234s | 0.0000633s |
| reset 후보 선택 최대 | 0.000311s | 0.000205s |
| bank tensor bytes | 798720 | 1797120 |

확장된 기하의 단일 검색 자체는 빨라진 것이 아니다. 초기화로 옮기고 reset에서 재사용한 효과다. 64환경 전체 단계의 실제 요청 개수 충족률은3/3·25°3/4·25°4/4에서100%,20°4/4에서99.90%,4/5 단계에서95.90~97.27%였다. 나머지는 기존 best-count/complete=False 정책으로 유지한다. 원본의 전체 simulator 병목 순위를 계측한 결과는 아니다.

2048환경 기본16후보×9단계 전체 초기화 시간은 측정하지 않았다. 저장 tensor 크기만57,507,840bytes로 산출했다. pure-layout bank 선택 수치는 reset 전체 또는 collection 시간이 아니다.

## 미검증·후속 실행

`nvidia-smi`는 드라이버와 통신할 수 없다고 반환했고, 설치된 PyTorch2.7.0+cu126의 `torch.cuda.is_available()`은False다. 따라서 **실제 Isaac Sim 초기화·부분reset·물리 rollout·PPO 학습·GPU collection1~2초 목표는 아직 미검증**이다. 사용자에게 추가 승인을 요구하지 않았으며 학습을 실행한 것처럼 기록하지 않는다. `logs/rsl_rl`은 건드리지 않았다.

`tests/_wrench_probe.py`를 준비했다. GPU 호스트에서 실제 전체 EnvCfg/PPO 비교,64/2048환경 초기화, 물성 고정·부분reset·관측 차원·각 단계36step finite rollout을 확인할 수 있다. 이 스크립트 자체는 이번 세션에서 실행하지 않았다. 실제 검증 순서는 환경 계약의64/2048 probe 이후 `scripts/train.py`의 collection 측정이다. zero-action probe 시간은 정책 inference를 포함하지 않으므로 PPO collection 목표를 대체하지 않는다.

단기 학습 검증을 수행할 때는 다음처럼 기존 학습 로그 밖에 기록한다. 아래 명령은 **미실행 예시**다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-v0 --num_envs 2048 --headless --max_iterations 2 \
  --resilient-attempt-dir outputs/wrench_training/smoke
```

단기 PPO가 통과하더라도 shelf failure 감소, 정지 성공률, 새로운 정책 행동, 후보 반복/고정 물성의 일반화 영향은 장기 대조 학습으로 확인해야 한다.

## 문서·최종 정적 검사

변경 Markdown5파일의 수식 검사와 두 저장소 `git diff --check`를 통과했다. 링크 검사에서는 기존 README의 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 링크1개가 파일 없음으로 검출됐다. 해당 링크가 작업 전 HEAD에도 있음을 확인했고 이번 요청 범위 밖이므로 보존했다. 신규 Wrench 링크와 나머지 변경 문서4개의 링크는 정상이다. 최종 기준 코드21파일 SHA256 동일성 및 공용 OBB 기본값 bitwise 비교도 통과했다.

## 2026-11-04 후속: 실제 크기 collider의 오프라인 배치 이미지

사용자가 통합 명세3.4 RED/Gray/White 영역이 의도에 맞는지 판단할2D 코드 샘플을 요청했다. [산출물·재현 안내](../../../../outputs/wrench_layout_preview/README.md)에4단계 PNG/SVG, 초기 확대, collider atlas, 생성 코드와 JSON provenance를 저장하고 통합 명세3.4에 연결했다. 환경 코드는 변경하지 않았다.

production WrenchLayoutBank·zone_masks를 직접 호출했다. 현재 절차적 collider 함수 및 기존 USD size_fraction0.9 실측 bounds로 box/can collider를 재구성하고, Test-v2 환경0의 동일 spawner 형상/scale roster를 사용했다. 과거 pose를 복사하지 않고 seed42·현재 RED23mm/후방20mm/Gray65mm로9단계×16후보 bank를 새로 생성했다.4개 단계의 후보0을 그대로 표시한다. 현재 원격 USD를 새로 검증한 것은 아니며 이 출처 한계를 안내했다.

검증:4개 샘플 complete=True, 실제3/3·3/4·4/5·4/5. 활성 OBB의 zone·wall5mm·모든139쌍의20mm 간격 검사가 통과했다. 생성 PNG 배치/확대를 열어 육안 확인했다. 실물 모양과 보수적 OBB를 구분하고 Gray의 일부 교차 허용을 설명했다. GPU/물리/학습을 실행하지 않았으며 기존 설정·학습 로그·사용자 변경은 보존했다.
