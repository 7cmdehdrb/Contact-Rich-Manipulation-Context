# Prof Revision Hard v0_3 구현·검증

[환경 계약](../environments/PROF_REVISION_V0.md#prof-revision-hard-v0_3) · [계통](../environments/PROF_REVISION_FAMILY.md)

## 요청·범위

2026-11-25 사용자 요청으로 `Inspire-Sweep-Prof-Revision-v0_3`를 직접 상속하는 `Inspire-Sweep-Prof-Revision-Hard-v0_3`를 추가한다. 목표 거리 하한5cm·인위적 상한 제거, 장애물0–10개와 저비용 배치, 기존8종 모두 타겟 사용이 범위다. 부모 reward·termination·관측·제어·물성·PPO는 보존한다. 기존 Play 분석의 F/T 이상 원인과 보상 설계는 이번 변경 범위에 포함하지 않았다.

## 변경 전후·의도

| 항목 | 부모 v0_3 | Hard v0_3 |
| --- | --- | --- |
| EnvCfg | `ProfRevisionV0_3EnvCfg` | 이를 직접 상속하는 `ProfRevisionHardV0_3EnvCfg` |
| 목표 | 6–12cm, 원통 footprint | 최소5cm, 추가 상한 없음. 형상·scale·reset yaw·비대칭 local bounds를 고려한 선반 내부 root XY |
| 장애물 수 | 균등 정수0–6 | 균등 정수0–10. 요청 수·물체 집합·목표를 줄이거나 다시 뽑지 않음 |
| 배치 | 외접 원·16,000셀·6회 삽입 | 실제 box·4,000셀·최대10회 삽입. 큰 면적 우선, 임의 방향 경계 채움, 셀 내부 jitter |
| 장애물 yaw | 연속 임의 각도 | 0/90/180/270도. 밀집 배치 시 외접 원의 과도한 면적 손실을 없애는 Hard 전용 선택 |
| 최소 여유 | 외접 원별1cm 확장 | 실제 XY box 사이1cm, 벽1cm, jitter 여유 별도. 타겟 목표 벽 여유2cm |
| 타겟 | cylinder 고정 | 환경 생성 때8종 중 선택, scale0.9–1.1. episode reset 때 형상 재선택·recooking 없음 |
| 가시성 | 최대7개 활성 원본 | 최대11개.16슬롯 초과 시 가장 넓은16조각 유지, 물리 장애물 제거 없음 |
| 물리 풀 | 타겟1 + 후보16 | 동일17개, 타겟 slot0·후보는 종별2개 유지 |

원 기반 무작위/경계 배치 시 긴 경로·10개 조합에서 빈 셀이 고갈되는 실제 사례를 확인했다. 목표·개수 축소 없이 해결하기 위해 Hard 전용 box 배치로 최종 변경했다. 접근·밀기 경로는 부모와 같은 선분의 선반 +X 방향 압출 영역을 타겟 footprint만큼 확장한 영역으로 보존하며, 후보 box와의 교차를 분리축으로 검사한다. 원통·곡면·손잡이도 실제 local bounds의 box로 보수적으로 처리한다.

GPU는 환경당128 threads가4,000셀의 유효성·점수를 병렬 계산한다. 반복1회는 최대10개 삽입이며, 실패 행만 최대8회 다른 경계 방향을 시도한다. 목표·개수·선택 자산·pose jitter는 유지한다. 여전히 배치 불가하면 상세 오류로 종료하며, 조용한 장애물 감소나 목표 편향은 없다. 이는 균일 Poisson Disk 분포를 주장하는 알고리즘이 아니라 box 간격을 보장하는 유한 격자 밀집 배치다.

## 파일·영향

- 기존 역할 파일의 EnvCfg·SceneCfg·EventsCfg·PPOCfg에 자식을 추가하고 Gym ID를 등록했다. 별도 버전 디렉토리는 만들지 않았다.
- 새 공통 helper는 [prof_revision_layout.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/prof_revision_layout.py)다. reset/관측에서 사용하는 배치 기하와 Warp selector를 담당한다.
- 부모의6개 고정 capacity 검사를 보호 메서드로 분리했다. 부모는6개만 허용하고 Hard만10개를 허용한다. 기존 원 기반 sampler 파일은 원본 내용과 동일하다.
- runtime reset/step·접촉 reduction·target slot0·보상 상태·초기 snapshot attachment를 재사용한다. Hard만11-source 관측 경로와 개수 보존 진단을 선택한다.
- `max_goal_distance=None`은 Hard sampler에서만 해석하며 부모의 finite 상한 검사는 유지한다.
- [live checker](../../../../src/inspire_sweep_baseline/scripts/check_prof_revision_hard.py), [테스트](../../../../src/inspire_sweep_baseline/tests/test_prof_revision_hard.py)를 추가했다.

## 최종 구성 대조

`check_prof_revision_hard.py`는 변경 전 HEAD의 EnvCfg 소스를 별도 모듈에서 실제 생성하여 현재 부모 전체 `to_dict()`와 비교한다. Hard와 현재 부모의 전체 구성 차이는 target `kind_override`, geometry layout class, reset 함수, 목표 min/max, `max_obstacles`, `layout_cell_size`만 허용한다. PPO 전체 비교에서는 `experiment_name=inspire_sweep_prof_revision_hard_v0_3`만 다르다.

| 구성 | 결과 |
| --- | --- |
| Reward 함수·순서·params·weight | v0_3 전체 상속 |
| Termination 함수·params·time_out | v0_3 전체 상속, `wrist_3_link` 선속도4m/s 포함 |
| Observation·Action·Command | policy108D·obstacles176D·12D action, 초기 시각 snapshot/촉각/F/T 계약 보존 |
| Physics·robot·shelf·actuator·sensor | 보존, 물리 풀17개 |
| Curriculum·episode·dt | 빈 curriculum·10s·physics0.01/policy0.02s 보존 |
| PPO·encoder·optimizer | experiment name 외 동일 |

## 실행 증거·한계

Windows11·RTX4070 12GB·`env_isaaclab` Python·Isaac Sim5.1 D3D12 headless에서 실행했다. 산출물은 [검증 폴더](../../../../outputs/prof_revision_hard_v0_3_validation), 최종 수치와 전체 설정 차이는 [live.json](../../../../outputs/prof_revision_hard_v0_3_validation/live.json)에 저장한다.

- 부모/Hard 관련 자동 검사36개 통과. 비대칭·비정사각형 target의 회전된 안전 목표 경계·5cm 하한·12cm 상한 제거,256환경 밀집 배치 간격·0–10개·재현성,독립 convex-hull SAT의 접근·밀기 경로 비침범,11-source CUDA 가시 OBB와 독립 CPU polygon 기준 비교·16슬롯 초과 시 가장 넓은 조각 보존, 기존 reward/관측/PPO gradient/checkpoint/ONNX 검사를 포함한다.
- `train.py`로16환경 PPO1회 업데이트와 checkpoint 저장을 통과했다. 검증용 결과는 `outputs/prof_revision_hard_v0_3_validation/ppo_smoke`에 저장했고, 모든 checkpoint tensor의 유한성을 [별도 검사](../../../../outputs/prof_revision_hard_v0_3_validation/ppo_checkpoint_check.json)했다. 기존 `logs/rsl_rl`에는 쓰지 않았다.
- 부모 기존 live checker4환경·12step 통과: [parent_smoke.json](../../../../outputs/prof_revision_hard_v0_3_validation/parent_smoke.json).
- Hard64환경·20회 전량 reset·부분 reset·510 policy step 통과. Zero action으로64회 episode 종료를 확인했다. 성공률·학습 성능 평가가 아니다.
- sampler1,280개 표본에서 장애물0–10개 모두 출현, 목표 거리0.0500088–0.470686m. 타겟 종별 출현 수는 `[7,13,6,12,8,8,6,4]`다.
- 실제 자산 bounds64행을 반복한2048행×100배치=204,800개 sampler stress 통과. geometry 재생성·물리 실행은 포함하지 않는다. [stress.log](../../../../outputs/prof_revision_hard_v0_3_validation/stress.log).
- 2048행 sampler warmup 후10회·CUDA synchronize 기준 중앙값 부모16.36ms, Hard2.46ms. 동일 실제 bounds를 사용하되 각 환경의 정상 목표·개수 분포로 비교한다. 전체 collection·센서·OBB·PPO 처리 시간과 구분하며, 모든 하드웨어에서 같은 시간이나 장기 학습 시간을 보장하는 값은 아니다.

초기 CPU native observer 검사는 Windows Warp의 기존 `fmin/fmax` 선언 문제로 컴파일되지 않았다. 새 observer의 검증은 CUDA 실행 결과를 독립 CPU polygon 구현과 대조하는 방식으로 수행했다. 초기 실행 중 검사 코드의 argsort 호출 및 configclass의 staticmethod 직렬화 문제를 수정했고, 최종 부모 전체 구성 대조에서는 capacity helper를 일반 instance 메서드로 유지한다.

장기 학습 성공률·새 checkpoint의 행동 품질·2048개 실제 물리 환경 collection 성능은 이 로그의 sampler 검증으로 대체하지 않는다. 기존 `logs/rsl_rl`과 사용자 변경·서브모듈 커밋은 보존한다.

## 후속 장애물 분산 배치 수정

2026-11-25 후속 사용자 요청: Hard-v0_3가 바둑판/일렬 배치처럼 보이며 Poisson Disk 언급의 의도는 배치 가속이었다. 기존 환경 ID를 직접 수정해 물체를 유효 빈 영역에 흩뿌리되 **밀기 최소 공간 확보 로직은 유지**한다. 위 초기 구현의 경계 방향 밀집 채움 설명은 이 절의 수정 전 동작이다.

시작 workspace HEAD는 `faed7d7ec2003c7445be80f68bd1a04136f69b24`, 문서 HEAD는 `36bf0bb5abde92460b669c0a898a831d1c8f5a75`였다. 앞선 장애물 비용 분석의 신규 scripts·실험 문서·인계/계통 문서 변경 및 기존 IsaacLab untracked 상태를 보존했다. 이 작업은 배치 분포 수정이며 비용 분석에서 제안한 보상 변경을 적용하지 않는다.

### 재현·원인

`diagnosing-bugs` 절차에 따라 실제 sampler를 호출하는 회귀 검사를 먼저 추가했다. 넉넉한 내부 공간을 가진 장애물1개 장면에서도 내부 배치 비율이0%인 것을 재현했다.

```powershell
python -m pytest src/inspire_sweep_baseline/tests/test_prof_revision_hard.py::test_sparse_layouts_use_free_area_instead_of_packing_into_corners -q
```

수정 전 결과는 `AssertionError: Only 0.0% of sparse scenes use the free interior`였다. 회귀 검사는 장애물 표면과 가장 가까운 벽 사이 여유가4cm를 넘는 배치 비율을 검사하며, 다중 장애물의 최근접 이웃이 같은 X/Y축 줄에 몰리는지도 검사한다.

가설은 방향 점수에 의한 코너 채움, 작은 셀 jitter에 의한 격자 흔적, 밀기 공간에 따른 가용 영역 축소 순으로 확인했다. 기존 점수 `ux*x+uy*y`를 최소화하면 매 삽입이 같은 방향의 극값을 선택해 코너·외곽부터 줄을 채운다. **충돌 검사·공간 제외·jitter를 고정하고 점수만 바꾼 대조**에서 분포가 개선됐으므로, 주된 원인은 경계 채움 점수였다.

### 수정 전후·전체 계약 대조

| 항목 | 이전 | 이후 |
| --- | --- | --- |
| 셀 선택 점수 | 장면별 한 방향의 선형 투영 극값 | 객체별 난수와 cell ID의 정수 hash로 공간 방향과 무관한 우선순위 |
| 위치 분포 | 코너·외곽부터 순차 채움 | 유효한 빈 셀에 무작위 분산·기존 셀 전체 범위 연속 jitter |
| 목표·요청 개수·물체·yaw | 기존 Hard 규칙 | 변경 없음. 동일 RNG draw 수, 같은 seed 입력의 목표·개수·자산/yaw 일치 확인 |
| 최소 밀기 공간 | 타겟 footprint를 포함한 target→goal 선분의 선반 +X 방향 전체 압출 영역 제외 | native kernel의 같은 SAT 유효성 조건 유지. 접근측과 이동 중 전 구간 검사 |
| 기타 여유 | 장애물 box 상호·벽1cm, 셀 jitter margin, 목표 벽2cm | 변경 없음 |
| 계산·실패 처리 | 4,000캐시 셀·큰 box 우선·128threads·실패 행 최대8재시도 | 변경 없음. 조용한 개수 감소·목표 재추출·경계 채움 fallback 없음 |
| 등록·EnvCfg·Scene·runtime·Command/Event·관측·Action·Reward·Termination·Curriculum·PPO | 기존 Hard 및 부모 구성 | 구성 파일 변경0. actual live에서 기존 부모 대비7개 허용 차이만 재확인, 부모 HEAD 대조·PPO 동등성 통과 |

활성 패키지 실행 코드 수정은 `mdp/common/prof_revision_layout.py`의 설명과 native 선택 점수에 한정했다. `sample`·`sample_commands`·geometry SAT·wall/pair clearance·재시도·yaw/jitter·타겟 형상 수명은 그대로다. 이 helper의 운영 호출자는 Hard Events의 `layout_class`뿐이므로 부모 v0_3·v0_3_1·기타 환경의 sampler는 변경하지 않았다. 기존 디렉토리·상속·Gym ID를 유지했다.

### 분포·안전 공간·속도 검증

자산 bounds64행을2048행으로 반복하고 seed987에서 수정 전·후 각각101배치=206,848장면을 생성했다. 첫 배치를 저장하고 나머지100배치에서 CUDA synchronize 후 시간을 측정했다. 두 버전 모두 요청한0–10개를 그대로 배치했고 실패0, 최대 재시도는 이전0/수정1이었다. 아래 분포 수치는 저장된 같은 목표·개수·자산·yaw의2,048장면 대조다.

| 측정 | 이전 | 수정 |
| --- | ---: | ---: |
| 장애물1개 장면의 내부 배치 비율(벽과 표면 사이>4cm,185건) | 0.00% | 77.84% |
| 장애물≥3개 장면의 최근접 이웃 축 정렬 비율(X 또는 Y 차이<1cm) | 51.75% | 13.29% |
| 장애물 표면의 가장 가까운 벽 여유 평균 | 4.04cm | 7.17cm |
| 2048행 helper 중앙값 | 2.716ms | 2.741ms |
| 2048행 helper P95 | 3.023ms | 3.066ms |

모든 장면이 수학적으로 균일한 완성 배치 분포라는 주장은 하지 않는다. 형상·남은 공간·개수·큰 물체 우선 삽입에 따른 제약은 유지한다.0–10개의 개별 위치를 검증하는 sampler 시간이며 전체 학습 속도나 성공률이 아니다.

독립 NumPy/SciPy ConvexHull/SAT로 수정 전·후 각2048장면의 **타겟 전체 압출 접근·밀기 영역과 각 장애물 사이≥1cm**, 장애물끼리·벽≥1cm를 확인했다. 타겟·목표 끝점만 확인한 검사가 아니다. [전후 배치 그림](../../../../outputs/prof_revision_hard_scatter_20261125/before_after.png)을 실제로 열어 코너/줄 편향 감소와 밀기 공간을 확인했다.

```powershell
python -m pytest src/inspire_sweep_baseline/tests/test_prof_revision_hard.py src/inspire_sweep_baseline/tests/test_prof_revision.py -q
python src/inspire_sweep_baseline/scripts/check_prof_revision_hard.py --headless --num-envs 64 --resets 20 --steps 100 --output outputs/prof_revision_hard_scatter_20261125/live.json
```

RTX4070·Windows11·Isaac Sim5.1·env_isaaclab에서 **37개 검사 통과**, actual64환경20회 전체 reset·부분 reset 비대상 rigid state 보존·100step 통과했다. 관측108/176D·보상·모든 관측 유한,8종 타겟 출현, 목표5.0009–47.0686cm를 확인했다. zero action100step에서 완료 episode0으로 성공률이나 장기 동작 개선을 평가한 실행은 아니다. ONNX 기존 API 폐기 예정 경고1건이 있었고 검사 실패는 없다. 새로운 학습·checkpoint 변경·로그 정리는 하지 않았다.

근거는 [benchmark.json](../../../../outputs/prof_revision_hard_scatter_20261125/benchmark.json), [분포·기하 검사](../../../../outputs/prof_revision_hard_scatter_20261125/distribution.json), [live.json](../../../../outputs/prof_revision_hard_scatter_20261125/live.json), [pytest.log](../../../../outputs/prof_revision_hard_scatter_20261125/pytest.log)다. 같은 폴더에 수정 전 source·원시 before/after NPZ·재현 helper를 검증 자료로 보존했으며 실행 경로에는 연결하지 않았다.

추가 [계약 소스 대조](../../../../outputs/prof_revision_hard_scatter_20261125/contract_comparison.json)에서 `sample`·`sample_commands`·초기화·selector wrapper의 Python AST와 native 기하·여유 검사 텍스트가 수정 전과 같음을 확인했다. 활성 패키지의 Git 변경 파일도 Hard layout1개뿐이다.

완료 검사: 변경 Markdown6개 수식 검사와 workspace/문서 저장소 `git diff --check` 통과. 변경 문서의 새 링크는 유효하다. 전체 README 링크 검사에서는 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1건이 나왔으며 HEAD에도 같은 경로가 있어 이번 수정과 구분해 보존했다. 나머지 변경 문서5개의 링크 검사는 별도로 확인했다. 기존 checkpoint의 바뀐 배치 분포에 대한 정책 성능·장기 재학습·2048개 실제 물리 환경 collection 성능은 이번 범위에서 미검증이다.
