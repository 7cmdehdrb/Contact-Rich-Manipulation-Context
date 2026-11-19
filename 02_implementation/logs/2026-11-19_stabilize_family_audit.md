# Stabilize / Sweep Only 네 환경 검토와 공통 코드 정리

2026-11-19. 대상은 `Inspire-Stabilize-Sweep-v0`, `Inspire-Sweep-Only-v0` 및 각 `-Test`다. 사용자가 제시한 구성·Action·Observation·Reward·Curriculum·Termination 항목을 실제 등록과 실행 코드까지 추적했다. 물체 옆 IK·Stabilize 없음 환경의 별도 설명은 [Sweep Only 상세 문서](../environments/SWEEP_ONLY.md)에 둔다.

## 요청 해석과 비교 기준

사용자는 후속 답변으로 Action 제한이 정책 분포 변경이 아니라 기존 **`clip_actions` 필드**를 뜻한다고 확인했고, 14cm 설정을 12cm로 변경하도록 지시했다. 네 runner의 `clip_actions=π/2`를 유지한다. 정책의 Gaussian 샘플과 PPO 저장값은 무제한이며 환경 실행 직전에 wrapper가 잘라 준다는 사실은 별도로 명시한다.

높이는 최초 설정 조회에서 14cm를 발견했으나, 실제 Sweep 상태 계산을 추적하면 이미 12cm를 사용했다. 미사용 14cm 설정 두 개를 없애고 `sweep_contact_height_limit=0.12` 하나를 실제 계산에 연결했다. 기본 보상 결과는 유지하면서 설정과 실행의 불일치를 제거한 변경이다.

기준 commit은 `913c2846fc81b8cf1d281d34af3c1aaf1b1252c8`이며, 이번 작업 시작 시 이전 IK 성능 개선 변경이 작업트리에 있었다. 그 상태를 `/tmp/stabilize_family_task_before`에 별도 보존해 이번 수정만 대조했다. 기존 성능 개선·문서 변경, 별도 작업 중인 `docs/plan/PLAN18.md`와 학습 로그를 보존했다. 파일 이동·새 task ID·기존 부모 계열 변경은 없다.

## 네 환경의 실제 차이

| 환경 | 초기화 | Stabilize / Gate | Reach |
| --- | --- | --- | --- |
| Stabilize 일반 | 타겟 옆 자세 후보 IK + 로봇 충돌 검사 | 있음 | 없음 |
| Sweep Only 일반 | 같은 타겟 옆 IK | 없음, 처음부터 Sweep | 없음 |
| Stabilize Test | Finger 원형 배치 + 고정 방향 단일 Warp IK | 있음 | 있음 |
| Sweep Only Test | 같은 Finger 초기화 | 없음, 처음부터 Sweep | 있음 |

Test도 IK를 사용한다. 일반 환경의 타겟 옆 후보 탐색과 로봇 충돌 검증을 사용하지 않는다는 차이다. Scene·Action·Observation·보조 비용·Termination·Curriculum·PPO 계산은 네 환경이 공통으로 사용한다. Test 두 환경은 대표점 빨간 표시도 켜져 있다.

## 조건별 검토 결과

| 사용자 항목 | 실제 구현과 판정 |
| --- | --- |
| UR5e + Axia80 + RH56E2 오른손 | 확인. 오른손 URDF 기반 USD 자산, 센서 질량 0.28kg, 손 질량 0.790kg. 이름의 `inspire_left_*`는 호환용 식별자이며 오른손 형상이다. |
| 손 articulation | URDF joint origin·axis·limit·inertia를 반영한다. 12개 물리 손 관절 중 6개 drive를 정책이 제어하고 나머지는 소프트웨어 mimic으로 연결한다. 질량·구동기 제한은 환경에서 조정된다. |
| F/T 캔슬링 | 측정 고정 관절의 wrench에서 손·패드 전체의 중력 및 관성 지지 wrench를 제거한다. COM·관성·각속도·가속도와 EEF 원점 모멘트 이동을 반영한다. |
| F/T clipping | 정책의 최종 EEF wrench에 힘 축별 ±150N, 모멘트 축별 ±8N·m를 적용한다. 보상은 잡음·clip 전 보상된 값을 읽는다. Axia 원시 센서 축의 포화·대역폭까지 구현한 센서 전자 모델은 아니다. |
| Tactile 34 → 17 | 손바닥 17 패드와 투영된 손등 17 영역을 17개 상태로 합친다. 없음 0 / 손바닥 1 / 손등 −1 / 양쪽 2. 각 원시 bit에 독립 1% flip 후 다시 인코딩한다. 손등 가상 영역의 접촉 필터에는 물체만 들어가므로 손등–선반 접촉은 이 경로에 포함되지 않는다. |
| 마찰·질량·크기 랜덤화 | 확인. 물체 질량 U(0.345, 0.750)kg, 크기 배율 U(0.9, 1.1), 손·선반·물체별 마찰 범위. 모두 startup 때 배정하고 reset 간 유지한다. |
| 선반 내 최소 밀기 공간 제외 | 네 환경 모두 선반 경계·RED·물체 간 간격을 적용한다. 타겟은 선반 중앙 반경 2cm 원판, 장애물은 남은 보수적 격자에서 무작위 배치한다. 선반 전체의 균일 분포는 아니다. |
| 초기 로봇 점유 공간 제외 | **일반 두 환경은 적용, Test 두 환경은 미적용.** 일반은 초기 로봇 OBB를 1cm 확장한 높이별 영역을 제외한다. Test는 배치 이후 단일 IK를 풀며 로봇 형상 충돌 검사가 없다. |
| PPO `clip_actions` | 네 환경 모두 π/2. 사용자 후속 설명의 필드 조건을 충족한다. 실행 명령을 제한하며 Gaussian 출력·PPO 저장 샘플 자체를 제한하는 설정은 아니다. |
| Arm OSC / Hand Joint Position | 확인. Arm 6D 상대 EEF pose OSC, Hand 6D 절대 rad 목표를 URDF 범위로 잘라 Position Target에 전달한다. |
| 관절 Pos/Vel 및 손 6축 Absolute | 확인. 실제 signed q·qdot이며 default-relative나 정규화 값이 아니다. 손은 실제 drive 6축 위치다. |
| 물체 관측 EEF Frame | 타겟·장애물·목표 XYZ는 현재 EEF frame. 현재 EEF pose 자체는 로봇 root frame이다. |
| 2D Bounding Box 대표점 | **중앙점을 뜻한다면 동일하지 않음.** 실제 선택은 정면 가시 연결 성분의 마스크 면적 중심에 가장 가까운 유효 표면점이다. 2D bbox 중앙·물체 전체 centroid와 구분해야 한다. |
| Initial Position 유지 | 확인. reset 때 저장한 표면점의 world 좌표는 에피소드 내 고정이며, 현재 EEF가 이동할 때만 좌표 변환 결과가 달라진다. |
| 가시 장애물만 `[Mask,XYZ]×16` + MLP | 확인. 64D를 32→16 MLP로 인코딩한다. 연결 성분별 슬롯이며 타겟은 최대 성분 하나만 사용한다. 선반·물체 가림을 반영하지만 로봇 가림은 포함하지 않는다. 노출 너비 2cm 이상 및 전체 투영 너비 20% 이상 조건이다. |
| Reach | 일반 두 환경 없음. Test는 현재 타겟–EEF 3D 거리 10cm 이하에서 근접 계수가 최대. 초기 거리 예산에 비례하는 기존 Finger 식이다. |
| Sweeping | 줄어든 현재 centroid–goal XY 거리 × 접촉 누적값/20 × 힘 방향 정렬도, weight 30. 최근 3구간 중 2회 접촉, 현재 접촉·유효 측정·수평 힘 1N 이상, EEF 12cm 미만이 필요하다. |
| Inverse Sweeping | 늘어난 거리 × −38.91. Sweep 단계에서 적용하며 접촉·높이 gate는 없다. |
| 기타 비용 | 압착·Action 변화·관절 속도·선반·기울기·장애물 이동·Wrench 변화·장애물 접촉 비용 유지. 관절 속도 비용은 최대값이 아니라 qdot² 합이다. Wrench 변화는 벡터 차가 아닌 힘/모멘트 크기의 변화다. |
| 고정 30도 DeadZone | 확인. 방향 커리큘럼은 없고 선반 ±X 축 주변 각각 ±30도를 항상 제외한다. |
| Joint Vel > 1.0 종료 | **팔 6축의 절댓값만 검사.** 손에는 속도 제한 1rad/s가 있으나 별도 손 속도 종료는 없다. 정확히 1.0은 종료하지 않는다. |
| 넘어짐·떨어짐·선반 종료 | 활성 물체 바닥이 상판보다 1cm 이상 낮거나 기울기 0.9rad 이상이면 실패. 선반 속도·변위·손목 여유 조건도 유지한다. |
| Timeout Fail & Success | 10초 deadline에서 모두 timeout, 성공은 거리 3cm 미만·Sweep 활성·물리 실패 없음인 부분집합이다. timeout과 success가 상호배타적인 두 term은 아니며 실패는 timeout AND NOT success로 구분한다. |

Stabilize 두 환경은 Gate 전 Sweep/Inverse Sweep을 지급하지 않는다. Gate를 통과한 다음 policy step부터 Sweep을 계산한다. Sweep Only는 이 조건이 처음부터 열린 상태다. 초기 1000 iteration까지 Wrench 변화·장애물 접촉 비용 weight는 0이며 이후 기존 커리큘럼으로 증가한다. 항이 존재한다는 사실과 처음부터 비용을 지급한다는 의미를 구분한다.

위 차이는 검토 결과로 기록했다. Test의 초기화, 가시 마스크 대표점, 센서 모델 범위, 팔 전용 종료를 임의로 바꾸지 않았다. 특히 Test 로봇 비겹침 조건을 만족한다고 보고하지 않는다.

## 공통 코드 정리

| 수정 위치 | 변경 전 → 후 | 보존 범위 |
| --- | --- | --- |
| `envs/stabilize_sweep_envs.py`, `mdp/common/stabilize_sweep_state.py` | 미사용 14cm 필드 2개 + 실제 식의 12cm literal → `sweep_contact_height_limit=0.12`를 실제 finish에 전달 | 기본 높이 경계·접촉 카운트·Sweep/retreat 식 |
| `runtime/stabilize_sweep.py` | Sweep Only가 부모 Stabilize 상태를 만들고 다시 교체 → `_state_type`으로 올바른 상태를 한 번 생성 | 공통 lifecycle·phase alias·부분 reset. Manager 초기 관측부터 Sweep Only phase=1 |
| `mdp/event_functions/stabilize_sweep.py` | 일반/Test의 표면점 저장·관측 계측 중복 → `_commit_surface_snapshot` 공통 처리 | snapshot 시점·물리 기록 순서·fallback·난수·대상 행·로그 키와 순서 |
| Observation / Reward Cfg | 사용하지 않는 import 제거 | 활성 term·callable·순서·weight·params 동일 |
| PPO Cfg | `clip_actions`의 실행 wrapper 의미를 주석으로 명시 | 값 π/2 및 Gaussian/PPO/encoder 동일 |

기존 네 EnvCfg의 직접 상속 관계와 역할별 파일 배치를 유지했다. 독립적인 보상·센서·인코더 스택을 추가하지 않았다. 다른 Finger/Final/Refactor 환경은 수정하지 않았다.

설정 호환성: 제거한 `goal_reward_height_limit`·`contact_height_limit`를 외부 Hydra 명령에서 override했다면 `env.sweep_contact_height_limit`로 변경해야 한다. 기본 동작의 엄격한 12cm 경계는 유지한다.

## 검증

실제 Isaac Sim App 안에서 네 등록 ID의 EnvCfg·PPO 전체를 변경 전후 직렬화했다. 차이는 미사용 높이 필드 두 개 제거와 새 0.12 필드뿐이며, 전체 Manager term·callable·params·weight·일정·순서와 PPO 설정은 일치한다. `/tmp/stabilize_family_before_cfg.json`, `/tmp/stabilize_family_after_cfg.json`.

CPU 센서 회귀 60개를 통과했다. 정적 중력·동적 관성·gyro·COM/EEF 모멘트 이동·외력 보존·촉각 투영·17상태와 flip 등을 기존 실제 계산 함수로 검사한다. 이 검사는 실물 센서 보정·대역폭을 검증하는 실험은 아니다. `/tmp/stabilize_family_sensors_cpu.log`.

상태·기하·대표점 배치·COM cache CPU 회귀 151개를 추가로 통과해 합계 **211개 통과**다. 새 8개 검사는 실제 runtime 정의를 사용해 상태를 한 번 생성하는지, phase alias가 유지되는지, 높이 인자가 전달되는지와 12cm 미만/동일/초과 경계를 확인한다. 기존 테스트가 센서 계산·관측 encoder·정책 export·보상 수식 경계를 함께 검사한다. `/tmp/stabilize_family_core_cpu.log`.

CPU 실행은 `env_isaaclab` Python, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`을 사용했다. 외부 ROS pytest 플러그인의 누락 의존성으로 인한 수집 실패를 피한 설정이며 테스트를 생략한 것이 아니다. 대표점 검사에는 Isaac Sim에 포함된 Warp 1.8.2 경로를 사용했다.

```bash
python -m pytest src/inspire_sweep_baseline/tests/test_stabilize_sweep.py \
  src/inspire_sweep_baseline/tests/test_stabilize_sweep_surface_batch.py \
  src/inspire_sweep_baseline/tests/test_stabilize_sweep_com_cache.py -q
python -m pytest src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative.py \
  src/inspire_sweep_baseline/tests/test_tactile_observations.py \
  src/inspire_sweep_baseline/tests/test_tactile_geometry.py \
  src/inspire_sweep_baseline/tests/test_tactile_configuration.py -q
```

네 등록 ID 각각 `check_stabilize_sweep.py --headless --num-envs 4 --audit-resets 2`로 실행했고 모두 exit 0이다. 실제 reset seed 0–1, 학습 wrapper 초기 reset, 실제 물리 step·접촉 계측, 초기 표면점 고정/현재 EEF 변환, 부분 reset의 미대상 관측·명령·물리 상태 보존, timeout을 확인했다. 일반 두 환경은 채택 자세의 밀기 반대편·RED·로봇 비겹침을 검사하고, Test 두 환경은 기존 Finger 초기화와의 동등성을 검사한다. Test 통과가 초기 로봇 공간 제외 조건의 충족을 뜻하지 않는다.

| 등록 ID | 실행 결과 | 원시 결과 |
| --- | --- | --- |
| `Inspire-Stabilize-Sweep-v0` | 통과 | `/tmp/stabilize_family_stabilize_gpu.json` |
| `Inspire-Sweep-Only-v0` | 통과 | `/tmp/stabilize_family_sweep_only_gpu.json` |
| `Inspire-Stabilize-Sweep-v0-Test` | 통과 | `/tmp/stabilize_family_stabilize_test_gpu.json` |
| `Inspire-Sweep-Only-v0-Test` | 통과 | `/tmp/stabilize_family_sweep_only_test_gpu.json` |

Gate와 timeout의 같은 step 처리 검사는 통제된 접촉 sample replay를 포함한다. 실제 접촉 계측 smoke와 구분하며, 학습된 정책이 물리적으로 Gate를 안정적으로 달성한다는 결과로 해석하지 않는다. 장기 학습 성공률·실물 센서 정확도·모든 seed의 IK 성공은 미검증이다. 이전 성능 작업의 2048환경 32회 수치는 [이전 측정 기록](2026-11-19_sweep_only_ik_performance.md)을 참조하며, 이번 정리 후 새 학습 성능 측정으로 간주하지 않는다.

최종 독립 대조에서 이번 작업의 운영 Python 변경은 7파일이고 292파일은 byte 단위로 동일했다. 새 운영 파일·파일 삭제는 없다. 공유 helper의 난수 소비·부분 reset 대상·물리 기록/fallback 순서·로그 항목 값을 보존했다. 새 상태 생성의 유일한 초기화 차이는 Sweep Only phase가 Manager의 초기 shape 확인 때부터 1이라는 점이며 실제 reset 이후 관측 계약은 동일하다. 검토에서 추가 회귀 문제는 발견하지 않았다.

전체 실제 GPU 결과·CPU 실행 요약·설정 전후 차이·코드 hash를 [검증 자료](../../03_assets/validation/2026-11-19_stabilize_family_audit.json)에 보존했다. [일반 Sweep Only 상세 설명](../environments/SWEEP_ONLY.md)에는 물리 자산, 무작위 분포, 초기화 실패 한도, 센서 계산, 관측 차원, 보상 수식·가중치·일정, 종료와 실행 명령을 정리했다.

문서 6개의 수식 검사와 root·문서 저장소의 `git diff --check`를 통과했다. 링크 검사에서 이번 추가 링크 오류는 없고, 기존 README의 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 링크 1개가 이미 삭제된 경로를 가리킨다. HEAD에도 존재하는 기존 오류임을 확인했고 이번 환경 검토 범위 밖이므로 수정하지 않았다. 최종 문서 기록 후 운영 코드 hash를 다시 대조해 검증한 코드와 동일함을 확인했다.

## Sweep Only Phase 관측·압착 페널티 삭제

사용자 후속 요청으로 `Inspire-Sweep-Only-v0`(물체 옆 시작)와 `Inspire-Sweep-Only-v0-Test`(Finger 방식 시작)를 직접 수정했다. Stabilize 일반·Test는 이번 요청 대상이 아니므로 그대로 유지했다. 앞 절의 네 환경 공통 Phase·압착 설명은 이 후속 변경 이전의 검토 기록이다.

| 항목 | 변경 전 | 변경 후 |
| --- | --- | --- |
| Sweep Only Actor·Critic 직접 관측 | Phase 포함 67D | Phase term 없음, 66D |
| 장애물 관측 / encoder | 64D → 16D | 동일 |
| 본체 MLP 입력 / export 입력 | 83D / 131D | 82D / 130D |
| `squeeze` reward | weight −1 활성 | term `None`, RewardManager와 보상 로그에서 제외 |
| 내부 phase / 접촉 계측 | Sweep 시작 상태·법선 하중·접촉 카운트 | 동일, 관측으로 노출하지 않음 |
| Stabilize 일반·Test | Phase·압착 활성, 67D | 동일 |

관측은 기존 파일에 `SweepOnlyObservationsCfg`를 추가해 부모 PolicyCfg에서 Phase term만 제외했다. 일반 Sweep Only에 연결하면 Test는 직접 상속으로 같은 변경을 받는다. `SweepOnlyRewardsCfg.squeeze=None`으로 제거하므로 단순히 weight 0을 설정한 것이 아니다. 공유 접촉 계측기의 압착 통계 누적 코드는 Stabilize 호환을 위해 유지하지만 Sweep Only 보상에는 사용되지 않는다.

기존 모델의 장애물 encoder·PPO 알고리즘을 그대로 사용하는 `SweepOnlyModel`(직접 입력 66D)과 해당 model cfg를 같은 역할별 파일에 추가했다. Actor와 Critic 모두 이 모델을 사용한다. 기존 67D 체크포인트는 첫 layer 입력 shape가 달라 그대로 resume할 수 없으며, 이번 범위에서는 자동 변환을 구현하지 않았다. 기존 학습 로그·체크포인트는 건드리지 않았다.

작업 시작 시 기존 성능·공통 코드 정리 변경과 별도 작업 중인 파일을 보존했다. 이번 기준 Python 복사본은 `/tmp/sweep_no_phase_before`, 문서 복사본은 `/tmp/sweep_no_phase_docs_before`다. 실제 등록 설정을 Isaac Sim에서 전후 직렬화한 결과 Stabilize 두 환경은 전체 설정이 동일했다. Sweep Only 두 환경의 차이는 `observations.policy.phase=None`, `rewards.squeeze=None`, Actor·Critic model class 선택뿐이었다. Scene·reset·Action·나머지 Observation/Reward·Termination·Curriculum·PPO 하이퍼파라미터·등록·runtime·로그 이름은 동일하다. `/tmp/sweep_no_phase_before_cfg.json`, `/tmp/sweep_no_phase_after_cfg.json`, `/tmp/sweep_no_phase_cfg_comparison.json`.

CPU 검사 `test_stabilize_sweep.py` **95개 통과**(11.88초). 기존 모델 검사에 66D Sweep Only 모델을 함께 실행하도록 하여 Actor·Critic forward, encoder gradient, TorchScript export 수치 일치, ONNX adapter 입력 130D를 확인했다. ONNX 파일 변환·런타임 실행은 수행하지 않았다. 최초 실행의 pytest import 위치 오류를 수정한 뒤 전체 파일을 재실행했다.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
PYTHONPATH=/home/min/miniconda3/envs/env_isaaclab/lib/python3.11/site-packages/isaacsim/extscache/omni.warp.core-1.8.2+lx64 \
WARP_CACHE_PATH=/tmp/stabilize_warp_cache \
/home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest \
  src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q
```

GPU 통합 검사는 기존 실행기를 갱신하여 활성 관측 목록에 Phase가 없고 활성 보상 목록에 squeeze가 없는지, reset·step 출력이 66D인지 검사한다. 내부 phase와 접촉 계산은 별도로 확인한다. Stabilize 검사에서는 기존 Phase·squeeze 활성과 67D를 계속 요구한다.

네 ID 각각 GPU 4환경·reset seed 0–1 통합 검사를 통과했다(exit 0). Sweep Only 두 환경의 reset·step·부분 reset에서 66D 관측과 Phase/squeeze term 부재를 확인했고, Stabilize 두 환경은 기존 67D·Phase·squeeze를 확인했다. 최초 Sweep Only 검사에서 마지막 관측을 Phase로 가정하던 두 검사 위치가 실패해 해당 검사를 내부 상태와 실제 관측 shape 확인으로 수정한 뒤 재실행했다. 운영 환경 코드의 추가 수정은 필요하지 않았다. 실행 명령·최종 원시 결과·코드 hash는 기존 [검증 자료](../../03_assets/validation/2026-11-19_stabilize_family_audit.json)의 `followup_sweep_only_remove_phase_and_squeeze`에 보존했다.

문서 6개 수식 검사, 수정 패키지 `git diff --check -- src/inspire_sweep_baseline`, 문서 저장소 diff 검사를 통과했다. 새 링크 오류는 없으며 README의 기존 누락 링크 1개는 유지했다. 전체 root diff 검사에는 별도 사용자 작업 `docs/plan/PLAN18.md:284`의 trailing whitespace가 있어 해당 파일을 변경하지 않았다. 이번 후속 변경의 장기 학습·2048환경 시간은 측정하지 않았다.

## Sweep Only 역방향 계수 −20 조정

사용자가 정방향 최대 계수 30과 역방향 계수 −38.91의 비대칭을 확인한 뒤 역방향 계수를 −20으로 요청했다. `Inspire-Sweep-Only-v0`와 `Inspire-Sweep-Only-v0-Test`에 직접 적용했다. SweepOnlyRewardsCfg에서 부모 term의 callable·params를 복사하고 weight만 −20으로 변경하며 Test는 이를 상속한다. Stabilize 일반·Test는 −38.91을 유지한다. step당 식은 `−20 × max(d_t − d_previous, 0)`이며 1cm 후퇴 시 −0.2다. 정방향 보상·접촉·높이 조건·관측·PPO·reset·종료·커리큘럼은 변경하지 않았다.

기존 GPU 검사 실행기의 부모 대조에도 명시적 weight 차이를 반영했다. 단순 계수 변경이므로 새 테스트를 추가하지 않고 실제 등록 설정을 직렬화하여 직전 검증 설정과 전체 비교한다. 기존 사용자 변경·학습 로그는 보존한다.

검증: 실제 Isaac Sim 등록 설정 `/tmp/sweep_retreat_20_cfg.json`을 직전 `/tmp/sweep_no_phase_after_cfg.json`과 전체 대조했다. Sweep Only 두 ID는 해당 weight 한 항목만 변경됐고 Stabilize 두 ID는 전체 설정이 동일했다. 패키지·문서 diff 검사를 통과했다. 이번 계수 수정 후 물리 rollout·학습 성능은 재측정하지 않았다.

## Sweep Only v1 Test 추가

사용자 요청으로 `Inspire-Sweep-Only-v0-Test`의 직접 자식 `Inspire-Sweep-Only-v1-Test`를 추가했다. 기존 역할별 파일 안에 EnvCfg와 runner를 추가하고 Gym 등록을 연결했다. 새 파일·runtime·보상 함수는 만들지 않았다. EnvCfg는 부모 post-init을 호출한 뒤 정방향 계수 30→50, 역방향 계수 −20→−10만 수정한다. runner는 부모를 직접 상속하며 로그 이름만 `inspire_sweep_only_v1_test`로 분리한다. 초기 배치·IK·Reach·66D 관측·64D 장애물·Phase/압착 비활성·Action·종료·커리큘럼·PPO는 보존한다. 부모와 다른 기존 환경의 계수는 변경하지 않는다.

검증은 `/tmp/sweep_only_v1_validate.py`로 실제 등록 설정을 Isaac Sim 안에서 직렬화하고 직전 네 환경 전체 설정 `/tmp/sweep_retreat_20_cfg.json`과 비교한다. 자식과 부모 차이도 두 weight와 experiment name만 허용한다. 같은 실행에서 신규 ID의 GPU 4환경 reset·4 policy step·부분 reset, 66D/64D 관측, live RewardManager 계수와 Phase/squeeze 비활성을 확인한다. 장기 학습·2048환경 성능은 이번 단순 계수 실험 추가 범위에서 실행하지 않는다.

실행 결과: `V1_TEST_CONFIG_AND_GPU_SMOKE_PASS`, `CONFIG_SNAPSHOT_PASS`, exit 0. 기존 네 ID 설정은 직전 검증값과 전체 일치하고, 새 자식은 부모 대비 두 보상 weight와 experiment name만 달랐다. GPU 4환경 reset·step·부분 reset 검사를 통과했다. 원시 로그 `/tmp/sweep_only_v1_validate.log`, 전체 설정 `/tmp/sweep_only_v1_cfg.json`. 패키지·문서 diff 검사 통과.
