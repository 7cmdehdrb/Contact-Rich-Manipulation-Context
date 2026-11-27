# Prof Revision v0_3_3-IK-v1 구현·검증

2026-11-27. 사용자는 선반 안쪽을 의미했던 EEF 시작 영역을 기존 손 시작위치까지로 제한하고 좌우도 줄인 그림을 승인했다. 최종 요구는 **X−0.20~+0.30m, Y−0.25~+0.25m**, 높이/손방향 유지, 기존환경 보존용 새 이름033-IK-v1, reset 외에는 일반 `inspire_sweep_prof_revision_v0_3_3`의 전체 설계 유지다. 새 환경을 추가했으며 기존033-IK를 직접 수정하지 않았다.

## 기준과 최종 계약

코드 HEAD `7f4460c489fbc7694a0ea438f2a482cc15517890`, 문서 HEAD `272cd98d3025cb1852f0404d67f59cbfbe19cc15`. 시작 시 코드/문서 작업트리는 clean이고 IsaacLab에 기존 untracked 상태가 있었다. 이를 보존하고 `logs/rsl_rl`은 건드리지 않았다. 수정 전 역할별8개 소스와 CLI/train/play3개는 `outputs/prof_revision_v0_3_3_ik_v1_validation/before`, `before_scripts`에 저장했다. 제안 그림/JSON은 `outputs/prof_revision_v0_3_3_ik_v1_area_proposal/proposal_lateral25.json`이다.

| 항목 | 부모 v0_3_3 | 새 IK-v1 |
| --- | --- | --- |
| EnvCfg | `ProfRevisionV0_3_3EnvCfg` | 직접 자식 `ProfRevisionV0_3_3IKV1EnvCfg` |
| Events | `ProfRevisionEventsCfg` | 직접 자식 `ProfRevisionV0_3_3IKV1EventsCfg` |
| reset 추가 params | 없음 | mode=`shelf_area_v1`, Xbounds=(-0.2,0.3), Ybounds=(-0.25,0.25) |
| 보상 | v0_3_3 전체 | callable/params/weight/순서 전부 동일 |
| Runtime/정밀 상태/물리step | `ProfRevisionV0_3_2Env` | 동일 클래스 재사용 |
| PPO | `ProfRevisionV0_3_3PPORunnerCfg` | 직접 자식, experiment name만 `inspire_sweep_prof_revision_v0_3_3_ik_v1` |

Scene·Command·Event의 다른항목·Observation·Action·모든16개Reward·Termination·빈Curriculum·physics·PPO 수치가 부모와 동일하다. 보상은 진행100/역방향−120/Reach9.8/Formation0.1715/장애물변위−300 cap0.04와 기존11항이다. 성공은현재XY거리<=3cm, TCP wrist_3_link 선속도>=4m/s 실패를 그대로 사용한다. v0_3_3 및 기존033-IK 전체Cfg/PPO·Gym등록의 보존도 비교했다.

## reset 구현과 안전 경계

`mdp/common/prof_revision_initial_pose.py`에 `shelf_candidates`를 추가했다. 승인된 고정사각창에서24개 연속 후보를 GPU로 뽑고, 물체→목표 경로의 EEF 예비 제외폭을 적용한4개를 기존 외부2개와 함께 batch solve한다. 기존 cache된 USD실제collision형상·전체링크FK·Warp IK·접촉없는 초기화/부분reset 경로를 재사용한다. 초기 손가락 관절과 손 방향 및 높이 분포는 부모 그대로다. 고정 창은 후보 범위이며 도달 불가/팔·손 충돌/선반 간섭/물체 경로 침범은 탈락시킨다.

IK 위치허용0.5mm에 대해1mm 안쪽 여유를 둔다. 기본 외부2개와 예산8모서리 복구 후보도 이 여유범위로 clamp해 범위 밖 대체가 발생하지 않게 했다. 선택된 실제 센서좌표의 범위는 live검사에서 따로 확인한다. 폭2mm 이하/역순/비유한값은 config validation에서 거절한다. 기존033-IK는 `bounded=False`의 원래 계산/RNG 경로 그대로이며 수치비교로 보존을 검사한다.

기본6후보/실패행8모서리1회로 계산량을 제한한다. 무한 재시도·목표/장애물 재추첨·reset 중 USD 재탐색/recooking·추가물리step은 없다. 새 파라미터는reset에만 쓰며 policy입력/보상에 넣지 않았다.

## Gym 이름 충돌과 실행 호환

처음 요청대로 일반 `Inspire-Sweep-Prof-Revision-v0_3_3-IK-v1`을 추가했으나 Gym은 같은family의 미버전 `...-IK`와 버전 `...-IK-v1` 공존을 금지해 package import가 실패했다. 기존 이름을 덮어쓰거나 강제 registry 삽입하면 기존 gym.make가 최신버전으로 치환될 수 있으므로 하지 않았다. 새 task만 namespace를 사용해 이름과 기존동작을 함께 보존했다.

**최종 task ID: `inspire_sweep_baseline/Inspire-Sweep-Prof-Revision-v0_3_3-IK-v1`.**

추가로 설치된 Isaac Lab의 `hydra_task_config`는 slash가 있는 ID를 root config name으로만 저장해 Hydra가 group 경로를 찾지 못했다. `scripts/cli_args.py`에 공통 wrapper를 추가하고 train/play의 import만 해당 wrapper로 바꿨다. namespace일 때만 동일 env/agent 설정을 적절한 group과global package로 한 번 추가등록하고 원래 Isaac Lab decorator에 위임한다. 기존 namespace 없는 task는 원래decorator를 그대로 반환한다. 이 변경은 새환경 실행경로 호환 처리이며 보상/학습 알고리즘 변경이 아니다. IsaacLab 서브모듈이나 설치파일은 수정하지 않았다.

## 검사 명령

Python은 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`, 산출물은 `outputs/prof_revision_v0_3_3_ik_v1_validation`에 격리했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_prof_revision_initial_pose.py src/inspire_sweep_baseline/tests/test_prof_revision_precision.py src/inspire_sweep_baseline/tests/test_prof_revision.py src/inspire_sweep_baseline/tests/test_prof_revision_hard.py -q -p no:cacheprovider --basetemp outputs/prof_revision_v0_3_3_ik_v1_validation/pytest_tmp
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/prof_revision_v0_3_3_ik_v1_validation/check.py
```

- CPU68개 통과·기존 ONNXdeprecated 경고1개. 승인된 창 내부1mm 여유/사각창 각부위 coverage/난수재현/목표구간 제외의 새 검사 및 기존reward·상태·부분reset·Hard 회귀를 포함한다.
- 실제128환경 reset/3step 및22회 반복 reset에서 actual ee_frame 센서값이 X−0.20~0.30/Y−0.25~0.25 범위 안임을 매회 검사했다. reward finite·역방향weight−120도 확인했다. 부모22회 reset과 비교했고16행 부분reset의 나머지112행 joint/선택buffer 보존을 통과했다. 실제링크FK 최대오차4.396μm.
- 수정 전 모든 기존Cfg/PPO 전체to_dict 일치. 새환경은 부모전체에서 reset params3개만 차이, PPO는실험명만차이. 기존등록/정의AST 보존 확인. 공통mode 분기를기존문자열로복원한AST도동일하다.
- 기존033-IK와 수정전selector를2048행 동일입력·동일RNGstate로 비교해4개반환tensor와선택metrics가비트단위로동일함을 확인했다. `original_ik_selection_bitwise_preserved=true`.
- Gym `_find_spec`으로 기존033-IK가원래ID그대로조회되고 namespace추가가이를최신환경으로치환하지않는것을검사했다. 새환경의 namespace로Hydra compose를실행해 reset범위와PPO실험명전달을확인했다.

성능: 동일세션 RTX4070·GPU동기화·warm-up2회제외20회 기준 전체 `env.reset()` 중앙값 부모72.05860ms→IK-v1 115.29675ms(+43.23815ms,1.6000배), p95 79.00360→143.91520ms. 선반내부후보가더많이탈락하는비용이있으며 기존빠른리셋과같은시간이라고주장하지않는다. 실제128행 geometry를16번확장한2048행 선택계산은 중앙값56.67870ms/6회중최대69.07120ms였다. 이는2048 PhysX전체reset이나PPO iteration측정이아니다.

검증 도구의 중간실패: 기존source module loader `previous`와joint snapshot변수명이겹쳐TypeError가발생했다. 도구변수명을수정하고전체검사를재실행해성공했다. Gym/Hydra 이름충돌은위와같이제품실행경로에서해결했다. 최종 `live.log`의 `HYDRA_AND_OLD_GYM_PASS`, `CONTRACT_PASS`, `BATCH_2048_PASS`, `LIVE_PASS` 및 `benchmark.json`을확인했다.

## 실행과 미검증

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task inspire_sweep_baseline/Inspire-Sweep-Prof-Revision-v0_3_3-IK-v1 --num_envs 2048 --headless
```

학습/PPO업데이트는시작하지않았다.2048개실제환경처리시간·장기학습안정성·초기분포변경의성공률/정착효과는미검증이다. 후보창전체가도달가능하다는뜻도아니다. 로봇self-collision검사는이번변경에추가하지않았으며기존robot설정을따른다. [최종환경계약](../environments/PROF_REVISION_V0.md#prof-revision-v0_3_3-ik-v1).

## 완료: 실제 학습설정 전달과 분포 그림

`outputs/prof_revision_v0_3_3_ik_v1_visualization/sample.py`에서 train/play와 같은 CLI wrapper 및 실제 Hydra decorator를 실행하되 callback에서보상−120/EEF범위/PPO실험명만 검사하고 학습/runner를만들지않았다. `HYDRA_DECORATOR_PASS` 통과. 단순 ConfigStore compose뿐 아니라decorator의설정변환과전달까지확인했다. 기존train/play는import한줄을원복하면수정전파일과동일하고,기존CLI함수/정의AST도동일함을검사했다.

같은스크립트에서seed42/128환경8회reset의actualEEF1024개를수집했다. 모두승인창안이며X범위−0.1986494~+0.2988648m,Y−0.2483320~+0.2482891m,Z1.1912864~1.2313657m였다. 창내부후보선택1001개/기존위치대체23개,선반안쪽X<=0.2인시작588개(57.42%)다. 기존RED polygon에속하는점은7개이며새범위와다른지표다. `samples.json`/`summary.json`/`selected_examples.json`과PNG/SVG `eef_shelf_v1`에저장했다.기존그림의RED위치를참고별로함께표시했다.

`sample.log`의 `HYDRA_DECORATOR_PASS` 및 `SAMPLES_SAVED 1024 7`을확인했다. 변경Python11개compile통과,기존train/play본문과CLI정의보존통과. 문서/그림 최종검사결과는아래에추가한다. 학습/PPO업데이트/commit/원격전송은실행하지않았다.

최종 완료검사: Markdown5개 수식 검사 통과, 문서4개 내부467/외부2 링크 검사 오류0, 루트/문서 저장소 `git diff --check` 통과. 갱신한실제EEF분포PNG를직접열어축/후보범위/범례/손투영/한글을확인했고그림의이전제목/눈금자동확장/행간겹침을수정했다. 환경안내·README·인계·개발로그를갱신했다. 기존환경과사용자변경을보존했으며학습/PPO업데이트/commit/원격전송없음.


## 후속: 1438 iter reset 후보 소진 수정

요청은 새 버전 생성이 아닌 현 IK-v1 덮어쓰기다. 사용자 원격 Linux 학습이 `select_initial_pose`의 `Collision-free initial pose budget exhausted: [1352]`로 중단됐다. 코드 기준 HEAD `cdeecf6cce8a0a3c3bd29c89d43cac120e1114d0`, 문서 HEAD `f35a3c28b8d7fa7794590bb68a078e783f81b165`. 시작 작업트리는 기존 IsaacLab untracked 상태만 있었고 이를 보존했다. 전달된 `logs/TEMP/2026-11-27/inspire_sweep_prof_revision_v0_3_3_ik_v1/2026-11-27_13-49-28`은 읽기만 했으며 `logs/rsl_rl`도 변경하지 않았다.

### 근거와 진단

전달된 params에서 seed42·2048환경·`shelf_area_v1` 및 승인된 범위를 확인했다. TensorBoard에는1439개 scalar sample, step0–1438이 있다. 기록된 `pose_recovery_fraction` scalar의 단순 평균은0.0002102023, 최대0.0148148155다. 이는 reset 행 전체를 합친 가중 비율이 아니다. 별도 실패 장면 tensor나 체크포인트는 전달된 파일에 없어서 원격1352번의 정확한 물리 상태를 복원한 것은 아니다.

`diagnosing-bugs` 절차에 따라 실제 CircleResetLayout·Warp IK·FK 충돌 검사를 호출하는 재현 도구를 먼저 만들었다. 로컬 seed42·64개 실제 asset 환경에서1024행씩 독립 배치를 검사했고40번째 index, 누적41,984장면에서 같은 예외 `[23]`를 얻었다. 실패 입력과 RNG를 저장해 정확한1024행 replay를 확인하고 실패535번째 행 하나로 줄였다. 이 최소 장면과 실제 USD 관절 frame·충돌 상자를 텍스트 fixture `tests/fixtures/prof_revision_ik_v1_budget.json`으로 저장했다. 원격 로그의 물리 상태와 동일하다는 주장은 하지 않는다.

가설은 후보 위치 부족, IK 수렴 실패, 승인 영역 전체의 실제 충돌 순으로 구분해 검사했다. 실패 행의 기본6개·기존 모서리8개는 모두 IK 위치 오차0.5mm 미만이며 경로 검사도 통과했으나 충돌 검사에서 전부 탈락했다. 같은 장면에서 XY만 재추첨하면1024회 중866회 기본 후보에 유효 자세가 있었고, 동일 범위의9×9×3 격자243개 중85개가 유효했다. 따라서 안전한 자세가 없어서가 아니라 좁은 영역에 대해 기존의 한쪽 외부 구간 모서리만 복구하던 탐색 부족이 원인이다. 종료 뒤 PhysX 경고는 최초 reset 예외와 구분한다.

### 변경 전후와 영향

| 항목 | 수정 전 | 수정 후 |
| --- | --- | --- |
| 일반 선택 | 기본6개, 필요 행8모서리 | 그대로 |
| 14개 모두 실패 | 즉시 RuntimeError | IK-v1만 동일 XY창 양측 격자 복구 |
| 추가 후보 | 없음 | X9×Y9×Z3, 최대243개/실패 행 |
| 추가 실행 | 없음 | 81개씩 최대3batch, 성공 행 제외 |
| 높이·방향 | 부모 높이 범위·기본 손 방향 | 동일, 복구Z는 중심과기존±jitter |
| 안전 검사 | IK·전체링크/선반/활성물체·경로 | 전 단계 동일 기준, 최종 실패는 계속 오류 |
| Scene/난수 | 기존 목표·장애물 추첨 | 재추첨 없음, 격자에 RNG 사용 없음 |
| 로그 | 기존7개 선택 지표 | IK-v1에 `pose_grid_recovery_fraction` 추가, 후보/시도 지표에 추가 계산 포함 |

제품 변경은 `mdp/common/prof_revision_initial_pose.py`의 선택 함수에 한정했다. 격자 회복은 `bounded`인 `shelf_area_v1`에서만 실행한다. 양측 격자에서 선택한 EEF는 `front_selected`에 포함하고 기존 외부 위치 fallback과 구분한다. 실제 충돌 모델·허용 오차·사각창1mm 여유·손가락 default joint는 바꾸지 않았다. 격자 전체도 불가능한 장면은 안전하지 않은 상태를 사용하거나 배치를 몰래 바꾸지 않고 기존 오류를 낸다.

최종 전체 계약 대조: Gym ID·EnvCfg 직접 상속·runtime·PPO experiment 및 모든 수치, Scene/Command/Event params/관측/Action/16개 Reward의 callable·params·weight·순서/Termination/빈 Curriculum/물리 및 train/play 코드의 변경은0이다. 일반 v0_3_3의 역방향−120 보상 설계를 전부 유지한다. 새 버전·새 task는 만들지 않았다. 기존033-IK(`front_area`)의 동일입력·동일RNG 반환4개 tensor와기존 지표가 비트 단위로 같고, 정상적으로 선택되는 IK-v1도 수정 직전 selector와 같은 결과임을 확인했다.

### 검증 명령과 결과

산출물은 `outputs/ik_v1_budget_debug`에 격리했다. 임시 도구는 이 명시적 debug 디렉터리에만 남기며 제품 소스에 debug logging을 넣지 않았다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_prof_revision_initial_pose.py -k real_budget -q -p no:cacheprovider --basetemp outputs/ik_v1_budget_debug/red_tmp
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_prof_revision_initial_pose.py src/inspire_sweep_baseline/tests/test_prof_revision_precision.py src/inspire_sweep_baseline/tests/test_prof_revision.py src/inspire_sweep_baseline/tests/test_prof_revision_hard.py -q -p no:cacheprovider --basetemp outputs/ik_v1_budget_debug/pytest_tmp
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/ik_v1_budget_debug/reproduce.py --replay
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/ik_v1_budget_debug/reproduce.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/ik_v1_budget_debug/live_check.py
```

- 수정 전 회귀 테스트는 `Collision-free initial pose budget exhausted: [0]`로 실패했다(`red.log`,4.21초). 수정 후 실제 Warp CPU 연산과 저장된 USD FK로 같은 행을 복구하고 범위·오차·전체링크 충돌·경로를 다시 검사해 통과했다. 모든 충돌 검사를 강제로 실패시킨 경우에도 최대257후보/5회 solve 안에서 예외가 발생하고 default joint가 보존되는 검사도 추가했다.
- 최종 관련72개 테스트 통과, 기존 ONNX deprecation warning1개(`pytest_final.log`). 최초70개 통과 뒤2·3번째 격자 batch까지 진행해야 복구되는 경우도 추가 검사했다. default joint 불변 검사는 clone한 snapshot과 비교한다(`pytest_pose_final.log`). 전체1024행 GPU 실패 입력 replay도 `REPLAY_PASS`다.
- 독립적으로 새로 뽑은2,097,152장면의 selector 검사에서 실패0(`stress_after.json`). 기존8모서리 복구419행, 새 격자 복구12행(전체의약0.000572%)이며 평균1024행 후보 수의 최댓값은6.0947265625다. 이는64개 actual asset geometry를 재사용해1024행씩 계산한 장면 배치/IK 검사이며2백만 실제 PhysX reset이나PPO 학습이 아니다. 새장면1024행 selector 중앙값19.2819ms/p95 36.9734ms/최대62.5157ms.
- 실제128환경의 reset·3step·반복22회·16행 부분 reset에서 센서XY 범위와 finite reward, 나머지112행 joint/선택 버퍼 보존, FK-PhysX 링크 위치 최대오차4.396μm를 확인했다. 전체Cfg/PPO·기존 Gym/Hydra 실행 및 기존033-IK bitwise 검증도 통과했다(`live.log`: `CONTRACT_PASS`, `IMMEDIATE_BEFORE_AFTER_PASS`, `LIVE_PASS`).
- 동일세션·동일128행 geometry를 확장한2048행 정상 선택 계산20회 중앙값은 수정 직전19.50935ms/수정 후19.66830ms, 비율1.00815다. 약0.8% 차이는 해당 측정값이며 Linux 원격 iteration 성능으로 일반화하지 않는다. 실제128환경 전체 reset 중앙값은46.89335ms다. 과거 날짜의 다른 세션 측정치와 직접 비교해 속도 개선을 주장하지 않는다.

장기PPO 재학습·원격1438iter 이후 학습 지속·전체2048개 PhysX clone 부하·모든 가능한 배치의 복구 성공은 미검증이다. 전달 로그는 변경하지 않았고 학습/commit/push를 실행하지 않았다. 고정 격자도 모든 배치의 수학적 가능성을 보장하지 않는다. 이번 재현 원인은 복구됐으며 충돌 조건을 완화하지 않았다.


추가 실제 reset 확인: 최소 실패 장면의 배치·XY제안을 고정하여 실제64환경 중23번의 `_reset_idx`를 호출하고 simulator forward로 센서를 갱신했다. `REAL_GRID_RESET_PASS`이며 실제 shelf-local EEF는 `[0.29903364,-0.24901295,1.19145322]`m로 승인 범위 안이다. 이 행은 기본14개가 모두 충돌했지만 추가81후보의 첫 batch에서 복구됐고, 후보95개·시도3회·격자복구 비율1로 기록됐다. 이는 별도로 기록한128환경 일반 경로 검사와 구분된다.

최종 문서 검사: 변경 Markdown5개 수식 검사 통과, 문서4개 내부469/외부2 링크 오류0, 양쪽 저장소 `git diff --check` 통과. README까지 포함한 링크 검사에서는 작업 전 HEAD에도 있던 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md`의 누락 링크1개가 남는다(현재README1665행, 이번 추가 링크 아님). 요청 밖의 과거 링크는 수정하지 않았다. 제품 공통 파일의 선택 함수 이외 모든 함수/클래스 AST가 수정 전과 같고 debug logging이 없음을 확인했다.
