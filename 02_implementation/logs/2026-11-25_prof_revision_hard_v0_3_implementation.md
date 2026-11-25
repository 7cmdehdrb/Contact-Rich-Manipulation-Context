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
