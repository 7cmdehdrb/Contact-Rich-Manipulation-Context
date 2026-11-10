# Sweep 정책 결과 수집·추출·플롯

2026-11-10 추가. 학습·play 환경을 수정하지 않고 checkpoint의 병렬 평가 결과를 저장한다. [개발·검증 기록](../logs/2026-11-10_sweep_evaluation.md) · [Simple 환경 설명](SWEEP_SIMPLE_ENVIRONMENTS.md).

## 실행

Workspace 루트 `C:\python\Contact-Rich-Manipulation`, Isaac Lab Python 환경에서 실행한다. 매 수집은 비어 있는 새 출력 경로를 사용한다. `--real-time` 지연은 사용하지 않는다.

```powershell
# 1. 병렬 수집: 128환경 × 환경당20개 완료 에피소드 = 2,560개
.\IsaacLab\isaaclab.bat -p .\src\inspire_sweep_baseline\scripts\collect_sweep_results.py --checkpoint "C:\python\Contact-Rich-Manipulation\logs\TEMP\inspire_sweep_simple_finger_v0\2026-11-10_14-30-35\model_1200.pt" --task Inspire-Sweep-Simple-Finger-v0 --num_envs 128 --episodes-per-env 20 --headless --output-dir .\outputs\sweep_evaluation\finger_1200_seed42

# 2. 원시 로그 → 에피소드별 CSV·방향별 통계
.\IsaacLab\isaaclab.bat -p .\src\inspire_sweep_baseline\scripts\extract_sweep_results.py --input-dir .\outputs\sweep_evaluation\finger_1200_seed42

# 3. 추출 결과 → GT 사분면 플롯과 오차 통계 Bar Plot
.\IsaacLab\isaaclab.bat -p .\src\inspire_sweep_baseline\scripts\plot_sweep_results.py --input-dir .\outputs\sweep_evaluation\finger_1200_seed42\analysis
```

GPU 여유에 맞게 `--num_envs`를 조정한다. `--episodes-per-env`는 **timeout 개수나 방향별 개수가 아니라 조기 종료를 포함한 전체 완료 에피소드 수**다. 각 환경의 처음 N개 에피소드만 기록해, 빨리 실패하는 환경이 전역 에피소드 한도를 먼저 소진하는 편향을 피한다. 할당량에 도달한 환경은 다른 환경이 끝날 때까지 계속 시뮬레이션되지만 추가 데이터는 기록하지 않는다. DeadZone·기하 경계·현재 checkpoint의 curriculum을 유지하며 방향 재추출·샘플 수 균등화는 하지 않는다.

`--checkpoint`, `--task`, `--output-dir`를 바꾸면 같은 수집/추출/플롯 코드를 재사용한다. 현재 Contact 어댑터는 Simple/Finger의 타겟2-of-3 이력과 Prof의 순간 접촉을 지원한다. 그 callable을 사용하는 다른 환경에서도 같은 어댑터를 사용한다. 다른 Contact 정의를 가진 task는 명시적 어댑터 추가가 필요하며 임의의 보상 양수 여부로 추정하지 않고 오류를 낸다. checkpoint와 task의 모델 입력·출력 차원은 일치해야 한다.

추출·플롯은 Isaac Sim을 import하지 않으며 NumPy·Matplotlib이 있는 일반 Python에서도 실행 가능하다. 수집만 Isaac Lab/Sim·PyTorch·RSL-RL이 필요하다. 수집은 등록된 EnvCfg/runner를 그대로 사용하고 checkpoint iteration을 로드한 뒤 첫 기록 reset을 수행한다. 학습·정책 export·checkpoint 저장은 하지 않는다. `logs/rsl_rl`이나 원본 checkpoint 폴더에 평가 결과를 쓰지 않는다.

큰 오차 때문에 중심 분포가 작게 보이면 플롯에 `--scatter-limit-cm 5`를 추가한다. 사용자 선택에 따라 현재 확대 범위는±5cm다. 전체 범위 그림을 유지하고 같은 모집단의 `timeout_scatter_zoom.png`를 추가한다. 창 밖 수와 모집단 정의는 이미지 caption 대신 `plot_metadata.json`에 기록한다. [실제128환경×20에피소드 결과](../experiments/2026-11-10_finger_model1200_evaluation.md).

현재 플롯 기본 분류는 `--group-by goal-quadrant`다. **선반 원점 기준 목표 GT의 X/Y 부호로 Q1(+,+), Q2(−,+), Q3(−,−), Q4(+,−)**를 나눈다. 가로축은 선반X, 세로축은 선반Y다. 입력에 없는 그룹은 생략하며, 에피소드는 있지만 moving step이0이면 N/A로 유지한다. 원점/비정상 GT는 undefined다. 축 위는 Q1: X>=0,Y>=0, Q2: X<0,Y>=0, Q4: X>=0,Y<0의 규칙으로 유일하게 배정한다. 기존 시계방향 기준을 보고 싶으면 `--group-by direction`을 지정한다. 수집/추출 CSV와 기존 통계는 수정하지 않고 플롯 단계에서 재분류한다.

`--individual`을 추가하면 종합 그림을 유지하면서 `plots/individual/<그림종류>/all.png`, `Q1.png` 등 사분면별 독립 PNG도 저장한다. 개별 scatter와 오차 통계 Bar Plot은 각 종합 그림과 같은 축 범위·단위·반경을 사용한다. 그림에는 축/단위·그룹/샘플 수·필수 범례만 남기며 task/checkpoint/seed/설명 caption은 metadata에 둔다. 다음 명령은 수집·추출을 실행하지 않는다.

오차 박스 플롯은 현재 기본적으로 전체 timeout 오차의 **상위 fence=Q3+1.5×IQR**를 넘는 값만 제외한다. 낮은 오차는 보존하며, 하나의 공통 cutoff를 Q1–Q4와 전체에 적용해 모집단 합이 일치한다. 제외 후 분포에서 사분위수·평균·중앙값·최소/최대를 다시 계산한다. `error_outliers.csv`와 metadata에 제외 표본/기준/수를 기록하며 원시/추출 및 Contact/scatter 모집단은 바꾸지 않는다. `--error-outlier-iqr`로 계수를 지정할 수 있다.

박스 플롯 기본 주축은 **0–10cm**다(`--error-axis-max-cm 10`). 제외 후에도10cm 초과 값이 있으면 상단의 별도 범위와 물결 모양 break를 추가한다. 생략 구간은 실제 잔존 표본이 없는10cm~최초 초과값 사이에서만 잡는다. 이번 데이터는144개 제외 후 최대6.183cm이므로 break 없이0–10cm를 표시한다.

기존 오차 박스 그림만 서식을 바꾸려면 `--error-only`를 사용한다. 기존 `error_boxplot.csv`를 읽어 종합 `error_boxplot.png`/`error_statistics.png`만 갱신하며 다른 그림·CSV·원시자료를 다시 만들지 않는다. 해당 모드는 Times New Roman(실제 설치 폰트 확인), all 항목 생략, 박스 중심 간격0.72/폭0.5, 기본Y축0–7cm다. 각 사분면의 평균 마커는 유지한다. 실제 결과 폴더가 `plots2`로 옮겨져 있으므로 다음처럼 지정한다.

```powershell
python src/inspire_sweep_baseline/scripts/plot_sweep_results.py --input-dir outputs/sweep_evaluation/finger_1200_seed42/analysis --output-dir outputs/sweep_evaluation/finger_1200_seed42/analysis/plots2 --error-only --error-axis-max-cm 7
```

```powershell
python src/inspire_sweep_baseline/scripts/plot_sweep_results.py --input-dir outputs/sweep_evaluation/finger_1200_seed42/analysis --group-by goal-quadrant --scatter-limit-cm 5 --individual
```

## 평가 기준

### Timeout 위치와 생성 목표

- 물체 위치는 타겟 **root**이며 목표 command `target_goal_pos`와 같은 기준점이다. BBOX 중심이나 COM 위치로 치환하지 않는다.
- 각 에피소드 시작 때 선반 pose를 저장하고 그 고정 선반 좌표계로 초기 물체·목표·현재 물체 좌표를 변환한다. 선반이 움직여도 프레임 자체가 흔들리며 오차를 가리지 않는다. 좌표 단위는 m, 플롯은 cm이다.
- 최종 오차는 `final_shelf - goal_shelf`다. 플롯 원점은 목표이고 모든 패널은 같은 축 범위와 종횡비를 사용한다. 점선은 task의 `goal_success_radius`다.
- **로그/추출의 시계방향 sector**는 생성 목표−초기 물체 위치를 사용한다. 12시=선반−X(Push), 3시=+Y, 6시=+X(Pull), 9시=−Y다. 60도 구간의 시작 경계 포함·끝 경계 제외이며 정확히1시는1–3에 속한다. 영변위/비정상 방향은 undefined로 별도 집계한다.
- **현재 플롯의 GT 사분면**은 위 sector와 다르다. 초기 물체가 선반 원점에서±2cm 범위로 달라지므로 절대 GT 좌표를 sector로 색칠하면 경계를 넘어 보일 수 있다. 따라서 절대 목표 GT를 그리는 이미지와 결과/Contact/통계의 그룹은 모두 동일한 GT 사분면을 사용한다. `goal_directions.png`는 선반 원점→GT를 단위벡터로 정규화한 방향이며 초기→목표 변위와 구분한다.
- Timeout scatter는 `horizon_reached AND time_out`인 완료 에피소드만 포함한다. 조기 실패는 포함하지 않고 별도 계수한다. timeout과 실패가 같은 step에 발생한 경우는 기본 포함하며 `terminated`, `clean_timeout`, 개별 term을 CSV에 남긴다. 플롯의 `--clean-timeouts-only` 옵션으로 동시 실패를 제외할 수 있다.
- `within_goal_radius`는 순수 기하 지표 `XY 오차 <= goal_success_radius`다. 환경 고유 성공 term의 strict 비교나 실패 조건을 바꾸지 않으며 환경의 실제 판정은 `termination_terms`로 보존한다.

### 움직임 중 Contact 인정 비율

기본 속력은 `object_lin_vel_w`의3차원 노름이며 조건은 **속력 >= 0.001m/s**다. policy dt0.02초인 Simple 계열에서는50Hz, 각 policy step 마지막 physics substep의 속도·접촉을 같은 시점에 기록한다. physics100Hz 구간의 접촉 지속시간을 직접 측정하는 값은 아니다.

```math
R = \frac{\sum_t 1[v_t \ge 0.001]\,1[\mathrm{ContactAccepted}_t]}{\sum_t 1[v_t \ge 0.001]}
```

전체/방향별로 **분자·분모를 먼저 합친 뒤 나눈다.** 에피소드별 비율의 평균을 사용하지 않는다. dt가 일정하므로 moving step 비율과 표본 시간 비율은 같다. 분모가0이면 CSV/JSON에서는 빈 값/null, 플롯에서는 N/A로 표시한다. 비정상 속력은 분모에서 제외하고 `invalid_speed_steps`로 센다.

Contact 통계에는 조기 실패를 포함한 모든 완료 에피소드의 유효 step이 들어간다. 실행 제한 등으로 끝까지 수집하지 못한 에피소드는 `episodes.csv`에 `completed=0`으로 남지만 집계에서는 제외한다. 제외한 에피소드·step 수를 `summary.json`에 표시한다.

| 항목 | Simple/Finger | Prof |
| --- | --- | --- |
| 힘 | 기존 타겟↔손 normal force 벡터 합의 노름 | 기존 타겟↔손 contact pair별 노름의 합 |
| 순간 인정 | 센서 fresh·유한한 힘·힘>=threshold·EEF 높이 제한 | 동일한 조건, 위 힘 정의 사용 |
| 최종 Contact 인정 | 실제 reward term의3step history에서2개 이상 인정 + 현재 EEF 높이 제한 | 순간 인정 그대로 |
| 목표 내부 보상 우회 | 접촉과 무관한 count/reward20은 **Contact 인정으로 치환하지 않음** | 해당 우회 없음 |

기존 reward compute를 한 번 호출한 직후, 자동 reset 이전에 상태와 실제 이력을 복사한다. reward term을 재호출하거나 observation을 추가 계산하지 않는다. 원시 로그의 `contact_instant`, `contact_accepted`, `contact_reward_credit`를 구분한다. Prof는 접촉 유지 reward credit이 없으므로 그 열은 NaN이다.

임계값·차원을 바꿔 재분석할 수 있다. 원시 로그는 그대로 보존하며 별도 분석 폴더를 지정할 수 있다.

```powershell
python .\src\inspire_sweep_baseline\scripts\extract_sweep_results.py --input-dir .\outputs\sweep_evaluation\finger_1200_seed42 --speed-threshold 0.002 --speed-dimension xy --output-dir .\outputs\sweep_evaluation\finger_1200_seed42\analysis_xy_2mm
```

`xy` 옵션은 world XY 속력을 의미한다. 기본3D 노름은 선반 방향에 무관하다. 환경의 힘·높이 threshold는 수집 metadata에 기록된 실제 reward params를 따른다.

## 산출물

| 경로 | 내용 |
| --- | --- |
| `metadata.json` | schema/version·실행 상태·task·checkpoint 경로/해시·seed·코드 commit/status·dt·iteration·Contact 정의·수집 수 |
| `env.yaml`, `agent.yaml` | 평가에 적용된 환경·runner 설정 |
| `raw/steps_000000.npz` 등 | chunk별 policy step 원시 배열. 각 row는 환경1개·에피소드1개·step1개 |
| `analysis/episodes.csv` | 에피소드 ID·방향·초기/목표/최종 root·오차·종료 사유·움직임/접촉 분자/분모 |
| `analysis/timeout_episodes.csv` | timeout 위치 scatter의 원본 row, 같은 열 구조 |
| `analysis/direction_summary.csv` | 전체·6방향·undefined 통계, 샘플 수·RMSE·median/p90 오차·반경 내 비율·Contact 비율 |
| `analysis/summary.json` | 위 통계와 분석 조건·모집단·원시 자료 경로·부분 에피소드 제외 수 |
| `analysis/plots/timeout_scatter.png` | 목표 중심 최종 오차 scatter: 전체+데이터가 있는 방향 |
| `analysis/plots/generated_goals.png` | 선반 원점 기준 실제 생성 목표 scatter: 전체+데이터가 있는 방향 |
| `analysis/plots/goal_directions.png` | 선반 원점→실제 GT 목표의 정규화 방향, 단위 없음 |
| `analysis/plots/moving_contact_ratio.png` | 동일 GT 사분면별 pooled Contact 비율 |
| `analysis/plots/error_boxplot.png`, `error_statistics.png` | Timeout 최종 XY 오차 박스 플롯: 상자25–75%, 중앙값선, 평균마름모, 실제최소–최대 수염; 전체+GT 사분면 |
| `analysis/plots/error_statistics.csv`, `error_boxplot.csv` | 상위 IQR 아웃라이어 제외 후 중앙값·평균·최소·최대와 사분위수(cm); scatter 확대 창 범위와 독립 |
| `analysis/plots/error_outliers.csv` | 오차 박스 플롯에서 제외된 episode ID·GT group·원래 오차 |
| `analysis/plots/contact_statistics.csv` | 플롯 그룹별 에피소드 수·moving/accepted step·비율 |
| `analysis/plots/plot_episode_groups.csv` | 원래 sector·목표 GT 좌표·현재 플롯 그룹의 행별 대응 |
| `analysis/plots/individual/<그림종류>/<방향>.png` | `--individual` 사용 시 전체와 각 유효 방향의 독립 이미지 |
| `analysis/plots/plot_metadata.json` | 입력 분석 경로와 timeout 동시 실패 필터 |

NPZ는 `allow_pickle=False`로 읽는다. 키는 `env_id`, `episode_id`, `episode_step`, `global_step`, `target_id`, `initial_shelf`, `goal_shelf`, `object_shelf`, `velocity_w`, `shelf_pos_w`, `shelf_quat_w`, `force_resultant_n`, `force_pair_sum_n`, `sensor_fresh`, `height_valid`, `contact_instant`, `contact_accepted`, `contact_reward_credit`, `terminated`, `time_out`, `horizon_reached`, `term__<각 종료 term>`이다. 위치/속도 배열은 row×3, quaternion은 row×4이고 나머지는 row별 scalar다.

## 중단·재현·제한

`--output-dir` 미지정 시 task/checkpoint/UTC timestamp로 새 경로를 만든다. 수집 경로가 이미 있으면 덮어쓰지 않는다. `--chunk-steps` 기본128이며 chunk는 임시파일 작성 후 rename한다. 정상 종료·Ctrl+C에서는 남은 chunk를 flush한다. 강제 kill/프로세스 crash에서는 마지막 메모리 chunk를 잃을 수 있으며 metadata 상태와 실제 chunk가 다를 수 있다. 추출은 episode step 누락·중복·에피소드 내 목표 변경·완료 manifest 수량 불일치를 검사한다.

`--max-steps`로 제한할 수 있으며 quota에 못 미치면 `status=partial`이다. 이 경우 완료된 에피소드는 분석 가능하되 source 상태와 미완료 제외 수가 함께 남는다. runtime 초기화 전에 실패해 dt/원시 chunk가 없으면 분석할 수 없다. checkpoint/task가 다르면 출력 폴더도 분리한다. 서로 다른 checkpoint 결과를 자동으로 하나의 비율로 합치지 않는다.

Finger model1200의128환경×20에피소드 수집·추출·플롯·원시 대조는 [실험 결과](../experiments/2026-11-10_finger_model1200_evaluation.md)에 기록했다. 다른 GPU·병렬 규모·task 어댑터 조합은 별도 실행 검증이 필요하다. 최초 검증용2에피소드 결과는 정책 성능의 일반화 근거가 아니다.
