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
