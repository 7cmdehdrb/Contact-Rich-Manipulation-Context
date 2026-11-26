# Prof Revision v0_3_3-IK 구현·검증

2026-11-26. 사용자 요청: 일반 `inspire_sweep_prof_revision_v0_3_3`을 직접 상속하고 시작 Joint State만 수정한다. 기존 IK 위치들과, 물체/장애물에 충돌하지 않으며 시작점→목표 구간을 피하는 RED 내부를 사용한다. reset iteration time 증가를 억제하고 기존 IK 처리를 참조한다. 후속 이름 지시 “033-IK”를 반영해 task ID는 `Inspire-Sweep-Prof-Revision-v0_3_3-IK`, 실험명은 `inspire_sweep_prof_revision_v0_3_3_ik`다.

## 작업 전 기준과 의도

코드 HEAD `35bfcc2e273cc919c5f6b0abb8b62bea1d7a5f22`, 문서 HEAD `ee66dcb7ace621f4a991ca0a07af2f97cca01164`. 시작 시 코드 변경은 없고 IsaacLab에 기존 사용자 untracked 상태가 있었다. 사용자 상태와 학습 로그를 보존했다. `logs/rsl_rl`은 건드리지 않았다. 역할별 변경 전 소스는 `outputs/prof_revision_v0_3_3_ik_validation/before`에 보관했다. 초안 이름v0_3_4는 구현 중 사용자 정정으로 폐기했고 실제 등록은033-IK만 추가한다.

선택 비율은 사용자 지정이 없어50:50 우선 선택을 기본으로 적용했다. 충돌/IK/경로 검사에 따라 유효한 다른 위치로 대체되며 실제 비율을 별도 기록한다. 기존 외부 위치는 shelf-local X=0.28–0.30m, Y=타겟 반대편0.10–0.18m, 기본높이+0.01m±0.02m이다. EEF 방향과 손가락 초기 상태는 부모 그대로다.

## 최종 계약과 구현

| 항목 | 일반 v0_3_3 | v0_3_3-IK |
| --- | --- | --- |
| EnvCfg | `ProfRevisionV0_3_3EnvCfg` | 직접 자식 `ProfRevisionV0_3_3IKEnvCfg` |
| EventCfg | `ProfRevisionEventsCfg` | 직접 자식 `ProfRevisionV0_3_3IKEventsCfg` |
| reset params | 기존 IK 범위 | 동일 범위+`initial_pose_mode=red_mix`, `red_probability=0.5` |
| 초기 팔 Joint State | 외부 IK | 충돌 검사된 외부/RED 혼합 |
| runtime | `ProfRevisionV0_3_2Env` | 동일 클래스 |
| PPO | 일반 v0_3_3 | 직접 자식, 실험명만 변경 |

새 `mdp/common/prof_revision_initial_pose.py`가 후보·FK·충돌 계산을 담당한다. USD 관절 프레임과 실제 enabled collision shape 상자를 최초 한번 읽고 GPU에 cache한다. reset 중 USD 조회·mesh recooking·환경별 Python loop·물리 step·수렴할 때까지 무제한 재시도는 없다. FK는6개 팔 관절 후보와 부모 손가락 default_joint_pos를 사용해 전체 링크를 계산한다. 보수적인 shelf-frame AABB끼리3mm 간격 검사를 적용해 팔/손과 타겟·활성 장애물·선반의 겹침을 거절한다. AABB라 유효한 일부 자세도 탈락할 수 있으나 충돌 자세 허용으로 보완하지 않는다. 로봇 self-collision 검사는 별도 추가하지 않았다.

RED 후보는 기존 시작/목표의 target bound center를 기준으로 +X extruded segment polygon에서24개를 병렬 생성하고 경로 여유 폭/선반 범위를 통과하는4개까지 IK에 보낸다. 외부 후보2개와 함께 최대6후보를 한 번의 Warp IK로 계산한다. EEF 경로 제외 예비 폭은 타겟 XY 외접반경+10cm이며, IK 이후에는 손/F/T의 실제 충돌 상자 중심과 XY 외접반경으로 시작→목표 전체 구간(양끝 포함)을 다시 검사한다. RED의 높이/방향은 기존 외부 샘플과 같다.

기본6후보가 모두 탈락한 행에만 기존 외부 IK 범위의8개 모서리를 한 번 더 batch 계산한다. 물체·목표를 재배치하지 않는다. 한정 예산을 소진한 경우 명시적으로 실패하며 안전하지 않은 자세를 쓰지 않는다. 별도 seed+4319 generator로 새 후보를 뽑아 부모 layout/IK RNG 추첨 순서를 바꾸지 않는다. 부분 reset은 선택된 환경의 관절/선택 buffer만 갱신한다.

공통 `fast_reset_scene`에는 `ik_params.initial_pose_mode == red_mix` 분기만 추가했다. 기존 모든 환경은 원래 solve/error 경로 그대로다. `prof_revision.reset_scene`에는 자식의 새 선택 metrics를 최종 reset 진단에 합치는 조건부 분기만 추가했다. 보상 callable·params·weight·순서(역방향−120 포함), Scene·목표/장애물 분포·Command·Observation·Action·Termination·Curriculum·physics·PPO 수치를 유지했다. 기존 성공 XY3cm·TCP4m/s 종료는 그대로다.

## 검증 경로

Python `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`. 검증 산출물은 `outputs/prof_revision_v0_3_3_ik_validation`이다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/prof_revision_v0_3_3_ik_validation/check_contract.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/prof_revision_v0_3_3_ik_validation/check_reset.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_prof_revision_initial_pose.py src/inspire_sweep_baseline/tests/test_prof_revision_precision.py src/inspire_sweep_baseline/tests/test_prof_revision.py src/inspire_sweep_baseline/tests/test_prof_revision_hard.py -q -p no:cacheprovider --basetemp outputs/prof_revision_v0_3_3_ik_validation/pytest_tmp
```

최초 CPU64개 통과. 초기 live checker는 허용한 공통 IK 분기를 AST audit에서 거절하여 부모 분기를 복원한 AST 동등성 검사를 추가했다. 후보 정렬의Torch API 인자 오류도 수정했다. 실제16환경 reset/3step 통과 후128환경 반복 reset에서 기존 두 외부 후보의 충돌 탈락을 발견해 제한8모서리 recovery를 추가했다. 최종 검사/성능 수치는 아래 완료 기록에 추가한다.

## 실행과 미검증

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3_3-IK --num_envs 2048 --headless
```

장기학습·성공률·새 초기분포의 흔들림/정착 효과는 미검증이다. 물체/선반 충돌 상자 검사는 기하학적 초기 간섭 검사이며 초기 물리 안정성이나 모든 미래 관절 움직임의 무충돌을 입증하지 않는다. [환경 설명](../environments/PROF_REVISION_V0.md#prof-revision-v0_3_3-ik).

## 최종 검증·성능 결과

- 새 후보/경로/회전 상자/관절 프레임 단위 검사4개와 기존 회귀를 포함해80개 통과.2개는 기존 opt-in 대규모 layout stress 및 standalone USD native library 조건으로 skip했다. 첫 회귀 실행의 Warp CPU2개는 hardcoded `C:/tmp` cache 쓰기 제한으로 실패했으며 캐시 쓰기를 허용한 재실행에서8개(해당2개 포함) 모두 통과했다. `pytest_final.log`와 `pytest_warp.log` 참조. 실제 Isaac Sim에서는 USD가 로드되어 링크/충돌형상 검사를 별도로 수행했다.
- 전체 계약: `contract.json`에서 부모와 새 환경은 reset ik_params2개만 차이, 보상 전체 동일, PPO는 실험명만 차이. 기존 모든 ProfRevision Cfg/PPO 작업 전후 동등성 통과. fast reset의 자식 분기를 제거해 원래 solve 분기로 복원한 AST가 baseline과 동일함을 확인했다. 공통 Prof reset의 자식 metrics 분기를 제거한 전체 AST도 baseline과 동일하다. 새 클래스/import/등록 외 기존 정의는 보존했다.
- 실제128환경에서 reset/3step 통과. 부모모드22회+자식22회 반복 reset(각2회 warm-up 제외20회 시간측정) 완료. 자식2816개 초기화에서 RED609개(21.6264%) 선택, 유효 RED가 없는 행은 외부 후보로 대체했다. 부분16환경 reset의 나머지112개 joint state와 선택 buffer 완전 보존 통과.
- 캐시한 전체 링크 FK를 실제 PhysX body_link_pos_w와 대조한 최대 오차0.000003993m(약4μm). joint limit/위치/방향 수렴 검사와 실제 링크 충돌 상자 검사로 선택했다. RED 진입만으로 물체/장애물 충돌을 허용하지 않는다.
- RTX4070/Windows, GPU synchronize한 전체 `env.reset()` 중앙값은 부모68.7714ms, 자식90.9045ms(+22.1331ms,1.3218배). p95는75.7093→112.8256ms. 최초 USD cache/JIT 준비시간은 warm-up에서 제외했다. 보상·물리step 루프에 새 충돌 검사를 넣지 않았다.
- 실제128행 geometry를16번 확장한2048행 GPU 후보/전체링크 충돌/Warp IK 선택 계산은 중앙값26.6634ms,6회 중 최대30.2014ms. 이것은2048개의 실제 PhysX reset이나 PPO iteration 시간 측정이 아니다. 전체2048환경 physics/collection/PPO 처리시간은 미검증이다.
- `benchmark.json`, `reset_large.log`의 `BENCHMARK`, `BATCH_2048_PASS`, `LIVE_PASS`로 완료 확인. 관절 쓰기 전만 계산하고 추가 simulation step 없이 완료했다. 큰 배치에서도 원래 layout/goal을 재추첨하지 않았다.

최종 진단의 `pose_candidates`와 `ik_attempts`는 recovery 행의 추가8후보/두번째 solve를 평균에 반영한다. 단위 검사 후 진단 수치 표현만 이와 같이 보완했고8개 변경 Python compile 및 기존 Prof reset AST 동등성을 확인했다. 장기학습/PPO 업데이트/commit/원격전송은 실행하지 않았다.

문서 최종 검사: 변경 Markdown5개 수식 검사 통과, 문서4개 내부462/외부2 링크 검사 오류0, 루트 및 문서 저장소 `git diff --check` 통과. 최초 수식검사 명령의 README 상대경로를 한 단계 깊게 지정해 파일을 찾지 못한 것은 검사 명령에서 수정 후 통과했다. 인계·활성 안내·환경 설명·README·개발 로그를 갱신했다. 기존 디렉토리/함수 위치·사용자 작업·학습 로그를 보존했다.

## 후속: EEF 시작 위치 그림

2026-11-26 사용자 요청으로 실제 reset 장면을 pyplot 그림으로 만들었다. 환경/보상 코드는 수정하지 않았다. seed42·128환경·8회 reset, 총1024개를 `outputs/prof_revision_v0_3_3_ik_visualization/samples.json`에 저장했다. EEF는 IK desired target 대신 실제 `ee_frame.data.target_pos_w[:,0]`를 선반 frame으로 변환해 표시한다. 타겟/목표/활성 장애물과 실제 손 관절의 충돌상자도 같은 reset에서 수집했다. RED 선택238/1024(23.24%)이며 기존 성능검사의21.63%와는 다른 표본이다.

`eef_start_examples.png`와 같은 이름SVG는 위쪽2개 RED·아래쪽2개 외부IK의 서로 다른 실제 장면이다. 방향별 구분이 잘 보이도록 목표 Y 양방향의 RED 사례와 X 양방향의 외부 사례를 골랐다. 좌우축은 shelf Y, 세로축은 shelf X를 뒤집어 아래가 로봇쪽(+X)이 되게 했다. EEF 다이아몬드·RED 후보 polygon·EEF 예비 경로 제외폭·기존 외부IK 영역·손/F/T 보수적 충돌상자 투영을 구분했다. 목표 위치/장애물은 각 장면마다 다르다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/prof_revision_v0_3_3_ik_visualization/sample.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/prof_revision_v0_3_3_ik_visualization/plot.py
```

그림을 직접 열어 축 방향·범례·한글·손 범위·겹침을 확인했다. 초기 범례/각주 겹침과 손 투영 잘림을 수정했다. Shapely가 없어 별도 설치 없이 Matplotlib polygon clip으로 제외폭을 그렸다. 이는3D mesh 렌더가 아닌 실제 상태의2D 투영이다. 학습/환경 설정/`logs/rsl_rl` 변경 없음.

## 후속: 전면 안팎의 연속 영역으로 직접 확대

2026-11-26 사용자: 이전 그림의 지점을 포함해 앞 영역에서 EEF가 있을 법한 위치를 모두 포함하고 싶다고 요청했다. 후속 확인에서 “전면 안팎을 연속 영역으로, 높이·손 방향 유지”를 명시적으로 선택했다. 새 버전을 추가하지 않고 기존 v0_3_3-IK를 직접 수정했다. 위의50:50 RED/외부 혼합 및 초기 그림은 변경 전 이력이다.

수정 전 역할별8개 소스는 `outputs/prof_revision_v0_3_3_ik_front_validation/before`에 추가 보관했다. 시작 시 이전 IK 구현/문서/시각화 작업의 사용자 작업트리와 IsaacLab 상태를 그대로 보존했다. 부모 v0_3_3·Hard·기존 Gym 등록·PPO·Reward 파일은 수정 전후 byte 동일하다.

| 항목 | 수정 전033-IK | 수정 후033-IK |
| --- | --- | --- |
| 후보 XY | 좁은 RED polygon/기존 외부 band | Y전체선반폭±0.5m, X시작/목표최소부터로봇베이스까지(기본0.7m) |
| IK mode params | `red_mix`, `red_probability=0.5` | `front_area`, `front_y_bounds=(-0.5,0.5)` |
| 선택 우선순위 | RED/외부50:50 시도 | 넓힌 연속 영역 우선, 외부는 안전 대체 |
| 경로 검사 | RED 후보 손·타겟 sweep | 기본/대체 모든 후보의 손·타겟 sweep |
| 기본 계산 예산 | 외부2+RED4,1batch | 외부2+전면4,1batch |
| recovery | 실패행만기존범위8모서리 | 동일예산,손경로검사도적용 |
| 보상·물체/목표 분포·관측·행동·종료·높이·방향 | v0_3_3 | 동일 |

후보 영역을 robot base까지 넓혀 기존 두 영역과 사이 공간, 좌우 양쪽을 포함한다. `front_candidates`로 연속 샘플링하고, 기존 전체링크 collision model/Warp IK를 그대로 재사용한다. 이전 지점을 반드시 일정 비율로 유지하는 요구가 아니므로50:50은 없앴다. 허용 영역 전체의 수학적/3D 도달가능성을 열거한 것은 아니며 고정 높이/방향의 이 전면 영역에서 충돌/IK/경로를 통과한 후보만 사용한다. 기존 RED helper는 참조/회귀용으로 보존했다.

기존 `_initial_pose_red_selected` 및 `red_selected_fraction`은 이제 후보카테고리 대신 실제 기존 RED polygon 내부 여부로 계산한다. `_initial_pose_front_selected`와 전면 선택/외부 대체 진단을 추가했다. 공통 reset의 분기 mode 문자열만 바꿨으며 이 분기를 이전 문자열로 복원하면 수정 전 AST와 동일하다. 다른 환경의 원래 solve 경로는 유지된다.

### 검증과 성능

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/prof_revision_v0_3_3_ik_front_validation/check.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_prof_revision_initial_pose.py src/inspire_sweep_baseline/tests/test_prof_revision_precision.py src/inspire_sweep_baseline/tests/test_prof_revision.py src/inspire_sweep_baseline/tests/test_prof_revision_hard.py -q -p no:cacheprovider --basetemp outputs/prof_revision_v0_3_3_ik_front_validation/pytest_tmp
```

- CPU회귀66개 통과. 이후 손의 경로/목표 끝점 검사1개를 추가하고 geometry7개 모두 통과(고유 합계67개). 새 검사를 끼워 넣는 중 퇴화polygon 검사의 block이 다른 test 안에 남아 tensor행수 불일치가 발생했으며 test배치를 바로잡아 통과했다. 제품 코드 오류는 아니었다. `pytest.log`, `pytest_geometry.log` 참조.
- 전체 계약: 부모 일반 v0_3_3 대비 변화는 reset IK params2개, Reward/PPO/Scene·나머지전체 설정 동일. 수정 전 대비 변경은 명시된 IK params와 관련 검증/선택 계산뿐이다. 모든 비대상 ProfRevision Cfg/PPO 전체to_dict 보존, 등록/Reward/PPO byte 보존, 공통 reset의 비대상 경로 AST 보존 통과.
- 실제128환경 reset/3step 및 부모22회+수정환경22회 반복 reset 완료. 실제 FK 최대오차3.987μm. 선택16행의 부분reset에서 나머지112행 joint와 기존RED 선택 buffer 보존 통과.
- 동일 세션/RTX4070/GPU synchronize, warm-up2회 제외20회 `env.reset()` 중앙값 부모65.34695ms→수정환경83.56715ms(+18.22020ms,1.2788배). p95 74.14830→94.90230ms. 기존 좁은033-IK의 과거측정90.90450ms와는 다른 실행세션이므로 직접 속도개선으로 단정하지 않는다. 기본 후보 수/IK batch 수는 늘리지 않았다.
- 실제128행 geometry를16배한2048행 선택 계산 중앙값28.13850ms,6회중최대31.95030ms. 실제2048 PhysX 전체reset/PPO iteration 측정이 아니며 그 처리시간은 미검증이다. `benchmark.json`, `live.log`의 완료marker 확인.

### 갱신한 그림과 실제 분포

`outputs/prof_revision_v0_3_3_ik_front_visualization/sample.py`로 seed42/128환경8회, 실제 EEF 센서1024개를 수집하고 `plot.py`로 `eef_front_area.png`/SVG를 만들었다. 기존 그림의 두 RED 시작점을 별로 표시해 새 영역에 포함됨을 보여준다. 나머지는 넓힌 실제 시작점 분포와 최소X/좌우 전면의 실제 예시다. 회색 상자는 장애물, 보라색은 실제손 충돌상자의2D 투영이다. 차트에는 각reset의 물체/목표/장애물이 다름을 표시했다.

- 전면 후보 선택1022/1024, 기존외부대체2/1024. 선반안쪽X<=0.2m인EEF147개, 기존RED내부1개다. 기존RED지점은 계속 허용되지만 더넓은분포에서 선택빈도가낮아진것이다.
- 실제EEF 범위: X−0.08919–0.69992m, Y−0.49852–0.49880m, Z1.19164–1.23136m. 목표가뒤쪽일때후보X하한도그목표깊이까지확장되어기존RED영역을포함한다.
- `summary.json`, `samples.json`, `selected_examples.json`에 수치/장면을 보관했다. 후보/충돌/IK 유효성은 코드와live검증으로 확인하며 그림의색칠전체가항상유효하다는뜻은아니다.

학습/PPO 업데이트는 시작하지 않았다. 장기 성공률·수렴·멀어진 초기위치의학습효과는미검증이다. 기존학습로그/사용자변경/서브모듈커밋을보존했고환경명은그대로다.

전면 확대 최종 확인: 변경 Python6개 compile, Markdown5개 수식 검사, 문서4개 내부462/외부2 링크 검사 오류0, 루트/문서 `git diff --check` 통과. 갱신 PNG를 직접 열어 후보영역·실제표본·이전위치 참조·축·범례·손 범위를 확인했다. 첫 그림의 rectangle clip을 patch추가 후 적용하도록 고치고, aggregate 후보영역 하한을1024장면의합집합까지 표시했다. 양쪽 손 투영이 잘리지 않도록 그림의 좌우 표시 범위를 넓혔다.
