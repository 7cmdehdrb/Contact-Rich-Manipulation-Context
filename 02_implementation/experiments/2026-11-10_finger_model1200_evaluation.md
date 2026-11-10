# 2026-11-10 Finger model1200 병렬 평가 결과

`Inspire-Sweep-Simple-Finger-v0`의 `model_1200.pt`를128환경×환경당20개 완료 에피소드로 평가했다. **Timeout 목표3cm 이내 비율은69.05%, 최종 XY 오차 중앙값2.20cm, 움직임 중 Contact 인정 비율84.42%**였다. 7–9시 방향은 목표3cm 이내 비율58.39%, Contact74.17%로 측정된4방향 중 두 지표 모두 가장 낮았다.

[실행·지표 정의](../environments/SWEEP_EVALUATION.md) · [개발·검증 기록](../logs/2026-11-10_sweep_evaluation.md) · [원시 실행 metadata](../../../../outputs/sweep_evaluation/finger_1200_seed42/metadata.json) · [전체 추출 통계](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/summary.json).

현재 그림은 후속 사용자 선택에 따라 **선반 원점 GT 사분면(Q1–Q4), 가로X/세로Y, ±5cm 확대, 최소 라벨**로 갱신했다. 아래 기존 시계방향 표는 초기 타겟→목표 기준의 최초 분석 기록이며, GT 사분면 표와 동일 분류로 해석하지 않는다. 원시/추출 자료는 그대로다.

## 실행 조건과 수량

| 항목 | 실제 값 |
| --- | --- |
| Task | `Inspire-Sweep-Simple-Finger-v0` |
| Checkpoint | `logs/TEMP/inspire_sweep_simple_finger_v0/2026-11-10_14-30-35/model_1200.pt` |
| Checkpoint iteration / seed | 1200 / 42 |
| 병렬 환경·완료 quota | 128환경 × 각20에피소드 = 2,560에피소드 |
| 수집 시각 | 2026-11-10 18:03:31–18:17:12 KST, 약13분41초 |
| Physics / policy dt | 0.01 / 0.02초 |
| 완료 에피소드 | 2,560 / 2,560, 모든 환경의 quota20 충족 |
| Timeout / 조기 종료 | 2,443 / 117, 동시 timeout+실패0 |
| 원시 자료 | 1,224,661 policy-step rows,79개 NPZ chunk |
| 누락·부분 에피소드 / 비정상 속력 | 0 / 0 |
| GPU·라이브러리 | RTX4070, PyTorch2.7.0+cu128, RSL-RL5.0.1, Isaac Sim5.1/D3D12 headless |
| 출력 폴더 | `outputs/sweep_evaluation/finger_1200_seed42` |

Checkpoint SHA256는 `57a67fdf50b67eca41d92cd72bdb31a53cd9200daae329431ca62671c4cb9419`이며 수집 전후 일치했다. 학습·정책 export·원본 checkpoint 쓰기를 수행하지 않았다. 평가 로그는 `outputs/`에 저장했다.

## Timeout 최종 위치 정확도

분모는 timeout으로10초까지 진행한2,443에피소드다. 오차는 목표 command와 같은 타겟 root의 `final_shelf - goal_shelf` XY 노름이다.

| 지표 | 결과 |
| --- | --- |
| 목표3cm 이내 | 1,687 / 2,443 = **69.05%** |
| 오차 중앙값 | **2.20cm** |
| 평균 오차 | 2.79cm |
| P90 / P95 오차 | 4.89 / 6.86cm |
| RMSE | 3.73cm |
| 최대 오차 | 31.58cm |

조기 종료를 포함한 전체2,560에피소드 기준으로 환경의 실제 timeout success term은1,687개, **65.90%**다. Timeout 모집단의69.05%와 분모가 다르다.

## 방향별 결과

방향은 초기 타겟→생성 목표이며12시=선반−X, 3시=선반+Y다. 위치 통계는 timeout 에피소드, Contact 통계는 조기 종료를 포함한 전체 완료 에피소드의 moving step을 사용한다.

| 생성 목표 방향 | 전체 N | Timeout N | 조기 종료 N | 오차 중앙값 cm | P90 cm | 목표3cm 이내 | Moving Contact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 전체 | 2,560 | 2,443 | 117 | 2.20 | 4.89 | 69.05% | 84.42% |
| 11–1시 | 0 | 0 | 0 | — | — | — | — |
| 1–3시 | 644 | 613 | 31 | 2.01 | 4.71 | 72.92% | 90.56% |
| 3–5시 | 615 | 580 | 35 | 1.97 | 4.27 | 75.00% | 93.70% |
| 5–7시 | 0 | 0 | 0 | — | — | — | — |
| 7–9시 | 659 | 632 | 27 | 2.67 | 5.41 | 58.39% | 74.17% |
| 9–11시 | 642 | 618 | 24 | 2.20 | 5.32 | 70.55% | 80.08% |

Iteration1200에서는 목표 방향의 선반±X 주변30도 DeadZone이 유지된다. 11–1시와5–7시의0샘플은 해당 분포를 유지한 결과이며 성능0%를 의미하지 않는다. 방향별 quota나 재샘플링은 적용하지 않았다. 나머지4방향은 각각615–659개 생성 목표가 기록됐다.

3–5시는 관측된4방향 중 목표 반경 내 비율과 Contact 비율이 가장 높았고, 7–9시는 가장 낮았다. 두 지표의 동반 차이는 이번 결과에서 관측되지만, Contact 차이가 위치 오차를 유발했다는 인과 결론은 이 평가만으로 내릴 수 없다. 단일 checkpoint·seed와 현재 목표 분포의 결과다.

## 움직임 중 Contact 인정

물체3D 속력>=0.001m/s인 policy step은1,040,635개다. 그중 실제2-of-3 이력과 현재 EEF 높이 조건으로 Contact가 인정된 step은878,484개여서 **878,484 / 1,040,635 = 84.42%**다. 목표 내부 reward20을 실제 접촉으로 치환하지 않았다.

| 방향 | Moving step | Contact 인정 step | 비율 |
| --- | ---: | ---: | ---: |
| 전체 | 1,040,635 | 878,484 | 84.42% |
| 1–3시 | 259,351 | 234,856 | 90.56% |
| 3–5시 | 249,031 | 233,333 | 93.70% |
| 7–9시 | 269,594 | 199,953 | 74.17% |
| 9–11시 | 262,659 | 210,342 | 80.08% |

비율은 방향/에피소드별 비율을 평균하지 않고 분자·분모를 합쳐 계산했다. dt0.02초의 표본 시간 합계로 moving20,812.70초, 인정17,569.68초이며 여러 환경·에피소드를 합한 값이다. 실행 wall time이나 physics100Hz 연속 접촉시간과 구분한다.

조기 종료117개는 순수 object fall/tilt94개, 순수 shelf failure20개, 순수 arm joint velocity2개, object fall/tilt+shelf failure 동시1개다. 개별 term 계수는95·21·2이며 중복이 있으므로 단순 합118을 에피소드 수로 해석하지 않는다.

## 그림

초기 물체 위치가 변하는데 절대 선반 GT 좌표를 초기→목표 방향 sector로 구분해115/2,560개 목표가 다른 사분면으로 넘어 보였다. GT를 보정하거나 이동시키지 않고, 동일 좌표 부호로 분류를 통일했다. Q1(+,+)615개, Q2(−,+)644개, Q3(−,−)645개, Q4(+,−)656개이며 배정 불일치0이다. [GT 재플롯 검증](../../../../outputs/sweep_evaluation/finger_1200_seed42/gt_replot_validation.json).

수집·추출 없이 그림만 갱신했고 원시/추출85개 입력의 SHA256이 모두 동일하다. 종합6장·개별30장과 통계CSV를 저장했다. 이전 그림은 `analysis/plot_history/before_gt_quadrants/`에 보존했다. [개별 이미지 목록](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/plots/individual/index.md).

### GT 사분면별 최종 오차 통계

후속 사용자 요청으로 오차 박스 플롯에서 큰 아웃라이어를 제외했다. 전체 timeout 분포의 공통 상위 fence **Q3+1.5×IQR=6.198785cm**를 넘는144개를 제외해2,299개를 사용한다. 원시/추출·기존 전체 성능지표와 Contact/scatter는 유지하며, 여기의 표/박스 통계만 필터 후 모집단이다. 상자는25–75%, 선은중앙값, 마름모는평균, 수염은잔존최소–최대다. 필터 후 사분위수와 평균도 다시 계산했다. 주축0–10cm, 잔존최대6.183cm이므로 이번 그림에는 축 생략이 없다. 향후10cm 초과 잔존값은 상단 범위+물결 break로 표시한다.

| GT 그룹 | Timeout N | 중앙값 cm | 평균 cm | 최소 cm | 최대 cm |
| --- | ---: | ---: | ---: | ---: | ---: |
| 전체 | 2,299 | 2.110 | 2.314 | 0.049 | 6.183 |
| Q1 | 559 | 1.901 | 2.058 | 0.059 | 6.053 |
| Q2 | 572 | 1.943 | 2.160 | 0.076 | 5.903 |
| Q3 | 578 | 2.134 | 2.343 | 0.049 | 6.183 |
| Q4 | 590 | 2.483 | 2.676 | 0.215 | 6.168 |

![최종 오차 박스 플롯](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/plots/error_boxplot.png)

[통계 원본 CSV](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/plots/error_statistics.csv) · [GT 그룹 행별 대응](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/plots/plot_episode_groups.csv).

[제외한 아웃라이어144개](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/plots/error_outliers.csv). 제외 전 원본2,443개의 평균2.786cm/최대31.582cm는 원래 데이터에 남아 있으며, 필터 후 박스 통계와 구분한다.

### 목표 중심 최종 오차: ±5cm 확대

점선은 목표 반경3cm다. 전체2,443점 중2,257점이 창 안에 있고186점은 창 밖이다. 전체 범위 그림과 CSV에는 모든 점을 보존했다. 이미지 설명을 줄이라는 요청에 따라 창 밖 수·모집단 정의·실행 조건은 metadata와 이 문서에 둔다.

![Timeout 최종 오차 확대](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/plots/timeout_scatter_zoom.png)

[최종 오차 전체 범위](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/plots/timeout_scatter.png) · [선반 원점 기준 생성 목표](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/plots/generated_goals.png) · [선반 원점 기준 GT 방향](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/plots/goal_directions.png).

### 움직임 중 Contact

![움직임 중 Contact 인정 비율](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/plots/moving_contact_ratio.png)

## 실행·검증 근거

아래 순서대로 실행해 모두 exit0으로 완료했다. 수집에 사용한 Python은 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`다.

```powershell
python src/inspire_sweep_baseline/scripts/collect_sweep_results.py --checkpoint logs/TEMP/inspire_sweep_simple_finger_v0/2026-11-10_14-30-35/model_1200.pt --task Inspire-Sweep-Simple-Finger-v0 --num_envs 128 --episodes-per-env 20 --headless --output-dir outputs/sweep_evaluation/finger_1200_seed42
python src/inspire_sweep_baseline/scripts/extract_sweep_results.py --input-dir outputs/sweep_evaluation/finger_1200_seed42
python src/inspire_sweep_baseline/scripts/plot_sweep_results.py --input-dir outputs/sweep_evaluation/finger_1200_seed42/analysis --scatter-limit-cm 10
python outputs/sweep_evaluation/finger_1200_seed42/verify_results.py
```

원시 배열을 독립 재계산해1,224,661행의 순간 접촉·3-step 이력을 검증했고 모두 불일치0이었다. 모든 episode CSV row의 최종 위치·방향·분자/분모와 모든 방향 요약의 median/P90/RMSE를 원시 로그와 대조했다. 상태complete, quota20×128, row/chunk 수량, 부분 에피소드0도 확인했다. 전체/목표/방향/Contact와 확대 그림을 실제 렌더링해 확인했다.

- [검증 코드](../../../../outputs/sweep_evaluation/finger_1200_seed42/verify_results.py) · [검증 결과](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/validation.json).
- [에피소드별 CSV](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/episodes.csv) · [Timeout CSV](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/timeout_episodes.csv) · [방향 요약 CSV](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/direction_summary.csv).
- [실행 console](../../../../outputs/sweep_evaluation/finger_1200_seed42_console.txt) · [평가 코드 snapshot/해시](../../../../outputs/sweep_evaluation/finger_1200_seed42/source_snapshot/manifest.json) · [플롯 창 밖 수량](../../../../outputs/sweep_evaluation/finger_1200_seed42/analysis/plots/plot_metadata.json).

다른 seed·checkpoint·Prof task의 재현성, 없는 두 방향의 정책 성능, 실물 성능은 이번 실행에서 검증하지 않았다. 초기 소규모2에피소드 smoke와 이번 결과는 다른 모집단이며 성능 비교 기준으로 사용하지 않는다.
