# 2026-11-10 병렬 정책 결과 수집 파이프라인

[사용·지표·데이터 계약](../environments/SWEEP_EVALUATION.md) · [현재 인계](../../01_plan/00_HANDOFF_BRIEF.md).

## 요청과 기준

사용자는 `Inspire-Sweep-Simple-Finger-v0`의 `model_1200.pt`를 play하는 대신, 병렬 환경에서 반복 가능한 원시 로그 생성·데이터 추출·플롯 코드를 각각 요청했다. Timeout 최종 물체 분포를 선반 좌표/목표 중심으로 전체 및11–1/1–3/3–5/5–7/7–9/9–11 방향별로 보고, 실제 생성 목표도 보존한다. 움직임 속력>=0.001m/s인 구간에서 Contact 인정 비율을 계산하며 DeadZone으로 적거나 없는 방향은 그대로 둔다.

- Workspace HEAD: `f75b3b09b402a0ecfdf3a378b5678fc6165e9a9e`.
- 시작 작업트리: `IsaacLab`의 기존 untracked 변경 표시를 보존. 문서 submodule의 기존 사용자 변경 `02_implementation/environments/SWEEP_SIMPLE_ENVIRONMENTS.md`를 보존하고 그 파일은 수정하지 않았다.
- 기존 버전 수정/새 환경 생성이 아닌 **독립 평가 실행기 추가**다. Gym task ID·EnvCfg·runtime 상속·PPO·MDP term은 변경하지 않는다.
- 실제 대상은 `SweepSimpleFingerEnv`/`SweepSimpleFingerEnvCfg`/`SweepSimpleFingerPPORunnerCfg`. 부모 Simple-v1의 Contact·종료·curriculum 계약을 확인했다.

## 변경 전후와 의도

| 대상 | 이전 | 이후·이유 |
| --- | --- | --- |
| 수집 실행 | play 중심, 평가2개 지표에 대한 재사용 출력 없음 | `scripts/collect_sweep_results.py`: task/checkpoint별 새 출력, 환경당 완료 quota, 원본 checkpoint 읽기만 수행 |
| 실행 중 관찰 | 표준 step 안에서 terminal 직후 자동 reset | `runtime/sweep_evaluation.py`: 기존 reward compute 결과 직후·reset 전 상태를 복사하는 평가 전용 probe |
| Contact 판독 | 목표 안에서는 reward20 우회가 있음 | reward>0으로 추정하지 않고 기존 term history/현재 높이 또는 Prof의 순간 접촉을 사용, reward credit도 별도 보존 |
| 원시 자료 | 평가 목적의 지속 저장 없음 | chunk NPZ·metadata·적용 env/agent YAML, 식별자/목표/초기/최종 위치·속도·접촉·종료 term 저장 |
| 추출 | 없음 | `scripts/extract_sweep_results.py`: episode CSV·timeout CSV·방향 요약·결측/부분 수집 표시, 임계값 재설정 가능 |
| 그림 | 없음 | `scripts/plot_sweep_results.py`: 전체+6방향 최종 scatter·생성 목표·목표 변위·Contact 비율4종 |

샘플링은 policy step 끝의 physics 상태다. Simple에서는50Hz이며100Hz physics 지속시간을 복원하지 않는다. 속도는3D COM linear speed, 오차 위치는 목표와 같은 root 기준이다. 선반 frame은 에피소드 시작 pose로 고정한다. 방향은 목표−초기 물체이며12시=−X, 3시=+Y이다.

Timeout cohort는 horizon 도달 AND time_out이며 동시 실패를 기본 포함하고 별도 flag/플롯 필터를 제공한다. Contact cohort는 조기 실패를 포함한 완료 에피소드다. 완료되지 않은 에피소드는 row를 보존하지만 통계에서 제외한다. 모든 비율은 pooled numerator/denominator이며 분모0을0%로 바꾸지 않는다.

## 최종 전체 대조

- 기존 패키지의 Gym 등록·EnvCfg·runtime·Scene·Command·reset·Observation·Action·Reward·Termination·Curriculum·PPO 파일을 수정하지 않았다. 디렉터리 이동·상속 변경·학습 설정 변경 없음.
- 추가 runtime 파일은 기존 환경이 import하지 않는다. 수집 실행기만 원래 등록 환경을 생성한 뒤 그 instance의 reward compute에 관찰 wrapper를 설치한다. 원래 compute는 step당1회이고 return을 그대로 반환한다. probe close 시 원래 bound method를 복원한다.
- 추가 관측 계산·보상 재호출·난수 추첨·물리 timestep 변경 없음. 초기 frame/목표/접촉 history를 reset 전에 복사한다. checkpoint iteration load 뒤 첫 기록 reset을 실행해 생성 목표도 같은 curriculum 단계를 따른다.
- 기존 `play.py`, `train.py`와 `logs/rsl_rl` 수정 없음. checkpoint export·checkpoint 쓰기 없음. 출력은 `outputs/`만 사용한다.

## 실제 검증

### CPU와 경계 검사

Isaac Lab conda Python `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe` 사용.

```powershell
python -m pytest src/inspire_sweep_baseline/tests/test_sweep_evaluation.py src/inspire_sweep_baseline/tests/test_sweep_simple.py src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py src/inspire_sweep_baseline/tests/test_sweep_simple_hard.py -q
```

최종44개 통과. 추가14개는 시계 방향/정확한60도 경계·속력 임계값 inclusive·3D/XY 재분석·pooled 비율·빈 방향·분모0·미완료 제외·누락 chunk 거부·terminal 복사·회전된 선반 좌표 변환·비동기 종료/환경당 quota·보상20과 Contact 구분·원래 compute1회/복원·플롯 파일 생성을 검사했다. CPU 검사는 실제 quaternion math를 사용하지만 PhysX를 대체하는 fake scene을 포함한다.

초기 검사에서 NumPy bool 합산 결과의 JSON int32 직렬화 오류를 발견해 scalar bool로 변환했고, 완료 후 추출을 다시 통과했다. chunk 압축 배열은 key 접근마다 재압축 해제되지 않도록 한 번 materialize한다. 그림 육안 검사에서 Contact 플롯 하단 주석과 E 라벨 겹침을 발견해 별도 하단 공간을 확보했다.

### GPU/PhysX 실제 수집

```powershell
python src/inspire_sweep_baseline/scripts/collect_sweep_results.py --checkpoint logs/TEMP/inspire_sweep_simple_finger_v0/2026-11-10_14-30-35/model_1200.pt --task Inspire-Sweep-Simple-Finger-v0 --num_envs 2 --episodes-per-env 1 --max-steps 550 --headless --output-dir outputs/sweep_evaluation_validation/finger_model1200_smoke
python src/inspire_sweep_baseline/scripts/extract_sweep_results.py --input-dir outputs/sweep_evaluation_validation/finger_model1200_smoke
python src/inspire_sweep_baseline/scripts/plot_sweep_results.py --input-dir outputs/sweep_evaluation_validation/finger_model1200_smoke/analysis
```

- RTX4070·PyTorch2.7.0+cu128·RSL-RL5.0.1·Isaac Sim5.1/D3D12 headless. 프로세스 exit0.
- metadata `status=complete`, checkpoint iteration1200,500 policy steps×2환경=1,000 raw samples,4chunk, 완료 quota `[1,1]`.
- checkpoint SHA256: `57a67fdf50b67eca41d92cd72bdb31a53cd9200daae329431ca62671c4cb9419`, 실행 전후 일치.
- 두 에피소드 모두500step timeout, 동시 실패0. 방향은9–11과3–5, 나머지4방향은0샘플로 보존.
- 전체 moving825step·Contact 인정721step, 비율721/825≈87.394%. 비정상 속력0step.
- 최종 XY 오차는 약2.1226cm와1.2155cm. 두 개 모두3cm 반경 내부. 이 수치는 **파이프라인 검증용 작은 표본**이며 정책 성능을 입증하지 않는다.
- 추출 CSV/JSON과4종 PNG 생성 완료. timeout scatter·Contact ratio·생성 목표·목표 변위 PNG를 모두 실제 렌더링해 확인했다. Contact 하단 라벨 겹침을 수정한 뒤 재생성/육안 확인했고, 목표 변위 그림의 원점 주석을 초기 타겟으로 명시했다.
- 실행 console: `outputs/sweep_evaluation_validation/finger_model1200_smoke_console.txt`. 원시 결과는 위 출력 폴더에 보존한다.

## 미검증 범위

아래는 최초 소규모 smoke 당시의 범위다. 이후128환경×20에피소드 실행은 이 문서의 후속 절과 연결된 실험 결과에서 별도로 검증했다.

- 128환경×20에피소드 등 대규모 throughput/GPU 메모리, 여러 seed의 성능 통계는 실행하지 않았다.
- Prof 및 다른 task/checkpoint의 실제 GPU 수집, 강제 kill·디스크 오류·손상 로그 복구는 실행하지 않았다. 지원하지 않는 Contact callable은 명시적 어댑터가 필요하다.
- raw/NPZ는 재분석 가능한 자료이며, 실행 상태가 partial/failed이면 완료 모집단과 제외 수를 함께 해석해야 한다.
- 인접한 기존 사용자 문서 변경과 IsaacLab 내부 untracked 파일은 검토·정리 범위에 포함하지 않았다.

## 문서·소스 최종 검사

- 변경 Markdown5개 수식 검사 통과. workspace와 문서 저장소 각각 `git diff --check` 통과.
- 변경 문서의 외부 workspace 링크 포함391개 링크를 검사했다. 새 문서/새 링크는 정상이며, 패키지 README의 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 참조1개가 현재 없는 파일을 가리킨다. 이번 평가 추가와 무관한 기존 누락이므로 수정하지 않았다.
- 기존 환경 코드의 tracked diff는 없고 추가 runtime·실행기·테스트와 README/인계/안내/신규 문서만 변경했다. 문서 submodule의 Simple 환경 설명에 있던 사용자 변경은 그대로 남아 있다.

## 후속: 사용자 요청으로1회 전체 수집·추출·정리

사용자가 순차 실행과 결과 정리를 요청해, 위에서 제시한128환경×각20에피소드를 seed42·동일 task/checkpoint로 실행했다. [실험 결과](../experiments/2026-11-10_finger_model1200_evaluation.md)에 전체 조건·정량값·그림·CSV/검증 코드를 연결했다.

- KST18:03:31–18:17:12 수집 완료, 모든 환경 quota20,2,560에피소드/1,224,661raw rows/79chunk. 수집→추출→플롯→원시 독립 대조 모두 exit0.
- Timeout2,443개·조기 종료117개·동시 timeout 실패0·부분 에피소드0. Timeout 목표3cm 이내69.05%, median2.20cm/P90 4.89cm, moving Contact878,484/1,040,635=84.42%. 단일 seed/checkpoint의 결과로 한정한다.
- 전체 row에서 원시 힘 threshold/height/freshness와3-step Contact 이력을 별도로 재계산했다. 순간/이력 인정 모두 저장값과 불일치0. 모든 episode CSV와 방향 요약을 원시 배열에 대조했다.
- 원래 수집/추출/환경 코드는 변경하지 않았다. 전체 범위 scatter의 최대 오차31.58cm 때문에 중심 정확도를 읽기 어려워 **플롯 실행기에 선택 옵션 `--scatter-limit-cm`만 추가**했다. 기존4종 그림/모집단/축 의미를 유지하고, 옵션을 주면 확대 그림1종을 추가한다. 창 밖43/2,443점을 각 패널/metadata에 표시하며 전체 원본과 CSV에는 모두 남긴다.
- 플롯 확대 옵션 회귀 검사 포함 `test_sweep_evaluation.py`:15개 통과. full-range/zoom5종 그림을 실제 렌더링해 확인했다. 앞선44개 환경 포함 검사와 이번15개 검사 수를 합산하지 않는다.
- 수집 당시4개 평가 소스 snapshot과 zoom 후속 버전 snapshot을 구분해 해시와 보존했다. checkpoint 전후 해시 일치. 기존 사용자 문서·IsaacLab 변경과 `logs/rsl_rl` 보존.
- 문서 안내의 대규모 미실행 표기를 이번 실제 실행 결과로 갱신했다. 다른 seed/task/checkpoint·실물 성능은 여전히 미검증이다.
- 후속 변경 Markdown5개 수식 검사 및 외부 산출물 포함252개 링크 검사 통과. workspace/문서 저장소 `git diff --check`와 플롯/검증 코드 `py_compile`도 통과했다.

## 후속: 빈 방향 생략·개별 이미지 추가, 플롯만 실행

사용자가11–1/5–7시는 없는 데이터로 취급하고, 한 이미지의 여러 subplot을 독립 이미지로도 저장하도록 요청했다. 수집/추출 없이 기존 model1200/seed42의 추출 결과만 사용했다.

- 변경 전: 빈 방향도 scatter에 N=0, Contact에 N/A로 표시하고 종합 그림만 저장했다. 변경 후: 각 플롯 입력 모집단에 에피소드가 없는 방향은 생략한다. 이번 입력은 전체+1–3/3–5/7–9/9–11의5항목이다. 에피소드가 있으나 moving step이0인 경우는 숨기지 않고 N/A를 유지한다.
- `plot_sweep_results.py`에 `--individual` 추가. 종합 그림과 같은 그리기 함수·축 범위·방향 색상·단위·반경으로 각 항목을 독립 저장한다. Contact도 전체와 각 방향의 단독 비율 그림을 저장한다. 제목/주석 여백을 따로 확보했다.
- 실제 명령: `python src/inspire_sweep_baseline/scripts/plot_sweep_results.py --input-dir outputs/sweep_evaluation/finger_1200_seed42/analysis --scatter-limit-cm 10 --individual`. exit0, 종합5장과 `plots/individual/<그림종류>/<방향>.png`25장 생성.
- 수집 실행기·추출 실행기·환경/MDP/학습 코드는 수정/실행하지 않았다. 재플롯 전후 raw79chunk·metadata·추출 CSV/summary/validation JSON 총85개 파일의 SHA256이 모두 일치했다. `replot_input_hashes_before.json`과 `replot_validation.json`에 근거를 보존했다.
- 회귀 검사 `test_sweep_evaluation.py`:16개 통과. 빈 방향과 관측됐지만 moving0인 방향을 구분하고, 개별 이미지 생성 범위·기존 확대 창 밖 수·기존 데이터 검사를 수행했다.
- 종합 확대/Contact와 개별 확대 전체/1–3시·생성 목표3–5시·목표 변위7–9시·전체 Contact를 육안 확인했다. 모든30장의 독립 육안 검사를 수행했다고 주장하지 않는다. 나머지는 같은 렌더러/구조이며 파일 목록으로 생성 여부를 확인했다.
- 원본 수량·전체/방향별 지표는 그대로다. 향후 다른 checkpoint에서11–1/5–7시 데이터가 있으면 자동 표시되며 이번 요청을 전역 방향 삭제로 적용하지 않았다. 최초 source snapshot을 보존하고 개별 이미지 지원 버전을 별도 snapshot으로 추가했다.
- `plots/individual/index.md`에25개 개별 이미지 링크를 정리했다. 문서4개 수식·외부 링크132개 검사 및 workspace/문서 저장소 `git diff --check` 통과. 최종 주석 여백 조정 후 전체 독립 확대 그림을 다시 확인했고, 입력85개 해시 불변을 재확인했다.

## 후속: 목표 GT 사분면 정정·±5cm 확대·오차 통계 Bar Plot

사용자가 생성 목표의 사분면 겹침 원인 확인·명확한 GT 분류·확대 scale 조정·전체/사분면의 중간/평균/최소/최대 Bar Plot 및 caption 최소화를 요청했다. 짧은 확인을 통해 **선반 원점 기준 GT 사분면**, **중심±5cm 확대**, **timeout 최종 XY 오차의 중앙값/평균/최소/최대**로 확정했다. 수집·추출은 수행하지 않았다.

### 원인과 변경 전후

- 기존 `generated_goals`는 절대 선반 GT를 그리지만 색상/그룹은 `goal-initial`의 시계방향 sector였다. 초기 타겟은 원점에 고정되지 않아±2cm 범위로 변한다. 실제2,560episode CSV에서 절대 GT가 원래 sector의 사분면과 다른 경우는1–3시22개,3–5시22개,7–9시37개,9–11시34개로 합115개였다. 반면 초기→목표 변위 자체는 기존 sector와 모두 일치했다. **GT 오차가 아니라 서로 다른 원점의 표시/분류 기준 혼용**이다.
- 기본 플롯 그룹을 GT X/Y 부호의 Q1(+,+), Q2(−,+), Q3(−,−), Q4(+,−)로 바꿨다. GT값을 이동/보정/재추출하지 않는다. 이전 direction 그룹이 필요하면 `--group-by direction`으로 명시한다. 전체/결과/Contact/Bar Plot이 동일한 그룹을 사용한다.
- 축은 가로 선반X·세로 선반Y로 통일했다. 이전 로봇 시점(+Y,−X) 표시와 구분한다. `goal_directions.png`는 초기→목표 변위 대신 **선반 원점→GT의 정규화 단위 방향**이다. 절대 GT 위치와 모든 그룹이 같은 경계를 사용한다.
- ±5cm 확대는 원래 전체 범위 그림과 함께 유지한다. 창 안2,257/전체2,443개, 창 밖186개는 metadata에 기록한다. GT Q1/2/3/4 timeout N은580/613/621/629다.
- `error_statistics.png`를 추가했다. 전체 및 GT 사분면별 timeout 최종 XY 오차(cm)의 median/mean/min/max를4개 bar로 표현한다. `error_statistics.csv`에 정확한 값을 저장한다. **확대 창 밖도 통계에 포함**하며 개별 Bar Plot도 같은 공통 세로축 범위를 사용한다.
- task/checkpoint/seed/진행 상태·원점 설명·caption·각종 footer를 모든 현재 그림에서 제거했다. 축/단위·그룹/샘플 수·필수 범례와 Contact 값만 남기고 설명은 metadata/문서로 옮겼다.

### 실제 실행과 검증

```powershell
python src/inspire_sweep_baseline/scripts/plot_sweep_results.py --input-dir outputs/sweep_evaluation/finger_1200_seed42/analysis --group-by goal-quadrant --scatter-limit-cm 5 --individual
python -m pytest src/inspire_sweep_baseline/tests/test_sweep_evaluation.py -q
```

- 플롯 exit0, 종합6장+개별30장. GT별 전체 N은Q1=615/Q2=644/Q3=645/Q4=656이며 원래2,560개를 중복 없이 분할한다.
- `plot_episode_groups.csv`로 원래sector·GT좌표·새group의 대응을 보존하고, `contact_statistics.csv`는 원래 episode별 분자/분모를 새GT그룹에서 pooled 재계산했다. 입력 `direction_summary.csv`의 기존 비율을 단순 재표기하지 않았다.
- 기존 원시/추출85개 파일 SHA256 불변. 새group2,560개를 X/Y 부호로 독립 대조해 불일치0. Python statistics의 median/fmean/min/max로 모든 그룹의 Bar 값을 독립 대조하고 Contact step 합도 대조했다. 근거: `gt_replot_input_hashes_before.json`, `gt_replot_validation.json`.
- 회귀27개 통과. GT 사분면과 정확한 축 경계·undefined, 기존 방향 모드, 1cm 확대 밖 timeout까지 통계에 포함됨, 서로 다른 median/mean/min/max, 기존수집/추출 동작을 확인했다.
- 새 GT 목표/단위 방향·±5cm 확대·통계 Bar·Contact·개별 통계Q1을 실제 렌더링해 확인했다. 모든36장의 개별 육안 검사를 수행했다고 주장하지 않는다. 전체/개별 생성 목록과 공통renderer를 검사했다.
- 현재 plots를 바꾸기 전 source/destination 절대 경로가 해당 analysis 안에 있는지 검사했다. 이전 그림은 `analysis/plot_history/before_gt_quadrants/`에 보존하고 검증한 새 그림을 현재 `analysis/plots/`로 교체했다. 이전 verbose/clock 파일이 현재 폴더에 섞여 보이지 않게 했다.
- 기존 환경·보상·종료·등록·학습 설정, 수집/추출 코드와 checkpoint는 변경하지 않았다. 전체 오차와 Contact 총계는 동일하고 **그룹별 결과만 GT 기준으로 재집계**됐다. 기존 시계방향 실험표는 역사적 모집단으로 명시하고 최신GT표/그림과 구분했다.

## 후속: 오차 통계 Bar를 박스 플롯으로 대체

사용자가 캔들 모양의 box plot을 요청했다. 기존 최종XY오차 자료와 GT Q1–Q4 분류·±5cm scatter·최소 caption을 유지하며 통계그림만 박스 플롯으로 대체했다. 이전에 요청한 평균/최소/최대도 읽을 수 있도록 **상자25–75%·중앙값선·평균마름모·실제최소–최대 수염**으로 명시했다. 1.5IQR 밖 표본을 버리는 정의가 아니다.

- `error_box_statistics`가 실제 timeout 오차에서 사분위수와 극값을 계산하고 matplotlib bxp로 종합/각 그룹을 그린다. `error_statistics.csv`의 기존열은 유지하고 `error_boxplot.csv`에 q1/q3/med/mean/whislo/whishi를 저장했다.
- `error_boxplot.png`와 기존 링크 `error_statistics.png`는 같은 새그림이다. 개별 `individual/error_statistics/*.png`도 box로 대체했다. Contact 비율 Bar는 분포를 나타내는 자료가 아니므로 기존표현을 유지했다.
- 재수집/재추출 없이 플롯명령만 실행해 exit0. 이전 Bar6개는 `analysis/plot_history/before_boxplot/`에 복사해 보존했다. 원시/추출85개 입력 SHA256 불변, GT/timeout 모집단 및 통계 수치 동일.
- 회귀28개 통과. 표본1/2/10/20cm에서 q1=1.75,q3=12.5,median6,mean8.25,min1,max20을 검사해 사분위수/극값/평균을 구분했다. 실제5개 그룹에서도 min<=q1<=median<=q3<=max를 대조했다. 종합 PNG를 렌더링해 확인했다.
- 안내/결과/인계를 현재박스정의로 갱신하고 후속소스 snapshot을 보존했다. 환경/수집/추출 코드는 변경하지 않았다.

## 후속: 큰 오차 제외와0–10cm 주축·조건부 물결 break

사용자가 지나친 큰 오차를 제외하고, 그래도 크면 물결 처리로 기본 플롯 내부를0–10으로 요청했다. 오차박스 통계에만 전체 timeout의 **공통 상위Q3+1.5IQR**를 적용한다. 개별사분면별 서로 다른 기준이나 양호한 낮은 오차의 제거를 피하고, 전체=사분면 합을 유지했다. 원시/추출/Contact/scatter는 변경하지 않았다.

- 실제 기준: 원본q1=1.434163cm,q3=3.340012cm,upper=6.198785cm. 2,443개 중144개 제외,2,299개 유지. 필터 후 모든 박스사분위수·평균·중앙값·최소/최대 재계산. 잔존최대6.182978cm로 기본0–10cm 안에 들어가 이번 그림에는 가짜축 생략을 넣지 않았다.
- `filter_large_errors`, `box_axis_ranges` 추가. 향후 잔존값이10cm를 넘으면0–10cm 하단을 넓게, 상단은 별도압축범위로 공유축에 그리고 양쪽 물결 break를 표시한다. 생략범위는10cm와 최초 초과표본 사이의 비어 있는 구간뿐이다. `--error-outlier-iqr` 기본1.5, `--error-axis-max-cm` 기본10. 종합/개별그림은 같은 필터/축 범위.
- `error_outliers.csv`로 제외 episode ID/group/error를 보존하고 metadata에 원본/잔존/제외수·quartile/fence·축 범위를 남겼다. 원시/추출85개 SHA256 불변, 제외144개 모두 fence초과·잔존극값 모두 fence이하·개별 n 합2,299=전체n을 대조했다.
- 기존단일표본 밖확대/GT 회귀에 더해,0/1/2/3/100cm에서 상위fence6cm·낮은0cm보존·100cm제외와10cm 경계/실제break 렌더링 분기를 검사한다. 종합 실제 PNG를 확인했고, caption은 기존 최소라벨 수준을 유지했다.
- 수집·추출 실행 없이 플롯만 재실행했다. 환경/보상/종료/정책 변경 없음. 현재결과표/사용안내/인계를 필터 후 모집단으로 명시했다. 원래 전체 성능지표를 필터 후 값으로 소급 대체하지 않았다.
- 최종 회귀30개 통과. 변경 Markdown4개 수식·외부산출물 포함138개 링크 검사와 workspace/문서 저장소 `git diff --check` 통과.

## 후속: 종합 오차 박스 그림만 Times New Roman·0–7cm·Q1–Q4로 재렌더링

사용자가 바 플롯만 다시 그리며 Times New Roman·Y축 축소·전체 평균 제거·간격 축소를 요청했다. 직전 결과가 box plot이므로 그 종합 오차 그림에 적용한다고 명시하고 진행했다. 전체 평균 제거는 **all 집계항목 제거**로 적용하며 각 사분면의 mean 마커는 보존했다.

- 실제 결과 디렉터리가 기존 `plots`에서 `plots2`로 이동된 상태를 발견했다. 이동을 되돌리지 않고 `analysis/plots2/error_boxplot.csv`를 사용했다.
- `restyle_error_boxplot`/`--error-only` 모드 추가: 기존 집계CSV만 읽고 `error_boxplot.png` 및 같은그림의 기존 alias `error_statistics.png`2개만 다시 쓴다. 원시/추출/다른그림·개별그림을 다시 그리지 않는다.
- 실제 폰트 `C:/Windows/Fonts/times.ttf`를 fallback 없이 확인하고, rc_context로 이그림에만 Times New Roman12pt를 적용했다. Y축0–7cm는 현재최대6.183cm를 포함한다. Q1–Q4만 표시하고 중심간격1→0.72, 폭0.5유지로 박스사이 빈간격0.5→0.22로 줄였다. 최소 caption을 유지한다.
- 실행: `python src/inspire_sweep_baseline/scripts/plot_sweep_results.py --input-dir outputs/sweep_evaluation/finger_1200_seed42/analysis --output-dir outputs/sweep_evaluation/finger_1200_seed42/analysis/plots2 --error-only --error-axis-max-cm 7`, exit0. 다른42개그림/CSV SHA256불변, displayed_groups=Q1/Q2/Q3/Q4·Y범위0/7·폰트경로를 sidecar `error_boxplot_style.json`과 대조했다. `box_style_input_hashes.json`에 사전해시 보존.
- 실제 PNG를 육안 확인했고 `py_compile` 통과. 수집·추출·통계 재계산·환경/학습 변경은 없다. 저영향 서식변경은 실행/이미지/파일해시로 검증했으며 이전30개 회귀검사를 이번에 다시 실행했다고 주장하지 않는다.


## Theoretical goal support and shared pastel colors

- Request: replace sampled goal scatter with theoretical boundaries and translucent fill; match quadrant colors in the existing styled error boxplot.
- Verified Simple Finger-v0 reset uses CircleResetLayout.sample_commands: displacement distance 6-12 cm, excluded angle 30 degrees around both X axes, and initial root position in a 2 cm disk. Absolute shelf-frame goal support is the Minkowski sum of the two allowed annular sectors and this disk. It is not simply an annular sector centered at the shelf origin.
- Shelf clipping is inactive: cylinder radius 4 cm, maximum scale 1.1 and edge clearance 2 cm leave safe X >=13.6 cm; support reaches at most 12*cos(30deg)+2=12.393 cm in X.
- Added analytical distance-to-sector geometry and --goal-region-only to plot_sweep_results.py. Boundary contours use a 0.02 cm grid; no empirical rows are used. Saved goal_generation_region.png/svg/json under analysis/plots2. Quadrants use absolute shelf GT signs. This depicts command sampler support, not obstacle-layout or IK success probability.
- Shared light green/orange/teal/purple palette with --error-only. Existing Times New Roman, 0-7 cm Y axis, Q1-Q4 categories, spacing and statistics preserved. No environment/training changes, recollection or extraction.
- Validation: both render commands succeeded; both PNGs visually inspected. Analytical origin exclusion, inner/outer radius, deadzone and mathematically constructed feasible points passed. Palette metadata matched. Python compilation passed.


## Uniformly subsampled pastel timeout scatter

- Request: match goal-region/boxplot quadrant colors, reduce scatter opacity, and uniformly downsample the provided zoom figure.
- Added --scatter-only to plot_sweep_results.py. Uses existing completed horizon-timeout episodes, absolute shelf GT quadrants, shared pastel palette, alpha 0.35 (previously 0.65), Times New Roman, and unchanged +/-5 cm axes and 3 cm goal-radius circle.
- Sampling is uniform random without replacement within each quadrant, seed 42, 200 episodes per quadrant (800 total). Sampling occurs before viewport clipping; it does not flatten spatial density. The all panel and individual panels use the same selected IDs. Within-view counts Q1/Q2/Q3/Q4: 191/181/189/181. Minimal group titles retained; sample definitions/counts/IDs are in timeout_scatter_zoom_style.json.
- Rerendered only combined timeout_scatter_zoom.png and five corresponding individual PNGs in analysis/plots2. No recollection, extraction, outlier deletion, CSV edits or boxplot/theoretical-region edits.
- Validation: render succeeded and combined PNG visually inspected. Four sets contain exactly 200 unique episode IDs each. Hash comparison confirmed only the six intended images changed among the prior preserved files. Python compile and document checks run below.


## Restored scatter opacity with identical samples

- User requested restoring scatter alpha while keeping counts. Default alpha changed from 0.35 to 0.65; combined zoom scatter and five individual images regenerated.
- The original combined PNG could not be overwritten (Windows OSError 22), so saved under plots2/alpha_restored. Verified selected episode IDs and counts exactly match previous metadata: 200 per quadrant, 800 total. Shared pastel colors, font, axes, seed and source CSVs unchanged. No recollection. Render succeeded; combined image visually checked.


## model3000 recollection and final plot styling

- Authorized checkpoint: model_3000.pt, same Simple Finger-v0 task, seed42, 128 environments, 20 completed episodes each. New output finger_3000_seed42; existing model1200 outputs and training logs preserved.
- Collected 2,560 complete episodes, 2,470 timeouts, 90 early endings, zero partials; 1,238,332 raw rows in 79 chunks. Runtime iteration 3000 and checkpoint hash recorded in metadata.
- Initial CLI parser rejected a bare Kit renderer argument before creating a run; reran successfully with --kit_args=--/app/vulkan=false. Collection exited 0; duration about 13m7s. No environment changes.
- Extracted CSVs and generated combined/individual plots. Applied existing final styles: Times New Roman, shared pastel quadrant palette, Q1-Q4 box chart 0-7cm, pooled upper Tukey exclusion, 200 uniform random scatter samples per quadrant with alpha0.65 and +/-5cm axes. Added theoretical goal-region figure from unchanged generator parameters. Full-plot palette/font now match specialized styling; this is the only plotting code adjustment in this turn.
- Quantitative results before outlier exclusion: timeout <=3cm 79.8381%, median1.7122cm, mean2.2161cm; moving-contact894085/1014614=88.1207%. Box-only fence5.181260cm excludes163, retains2307; raw CSV/Scatter/Contact unchanged by exclusion.
- Validation: existing CPU suite30 passed; independent all-raw reconciliation passed, including reconstructed 2-of-3 contact history and instant thresholds with zero mismatches. All episode rows and all summary groups reconciled. Combined final box/scatter PNGs visually inspected. Source snapshots and hashes saved. Single seed evaluation only; no training or multi-seed inference.
- Durable result: [model3000 evaluation](../experiments/2026-11-10_finger_model3000_evaluation.md).


## model3000 scatter alpha 0.9

- User requested changing scatter images only to alpha0.9. Called existing restyle_timeout_scatter with explicit alpha=.9; no code/default changes. Saved combined zoom PNG and five individual PNGs under finger_3000_seed42/analysis/plots/alpha_09.
- Verified exact same sampled episode IDs and counts as previous model3000 scatter (200 per quadrant, 800 total), and alpha0.9 in metadata. Analysis CSV hashes unchanged. Box plots, goal figures and source logs preserved. Render succeeded; combined output visually inspected.


## Darker same-hue model3000 scatter

- User requested stronger colors in the same hue families. Rendered model3000 scatter with green #628C45, orange #D17A28, teal #318C82, purple #8060AF; alpha0.9 maintained. Applied palette to the rendering process only, leaving shared default palette and other figures unchanged.
- Saved combined and five individual PNGs under plots/alpha_09_dark. Selected episode IDs and sample/viewport counts exactly match alpha_09 (200 samples per quadrant). No data collection, extraction or CSV changes. Render succeeded and combined PNG visually inspected.
