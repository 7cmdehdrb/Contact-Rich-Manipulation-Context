# 2026-11-10 Finger model3000 병렬 평가 결과

`Inspire-Sweep-Simple-Finger-v0`의 `model_3000.pt`로 128환경 × 각 20회, 총 2,560개 완료 에피소드를 수집했다. Seed는 이전 평가와 동일한 42다. Timeout 목표 3cm 이내 비율은 **79.84%**, 최종 XY 오차 중앙값은 **1.71cm**, 움직임 중 Contact 인정 비율은 **88.12%**다.

[지표 정의](../environments/SWEEP_EVALUATION.md) · [실행 metadata](../../../../outputs/sweep_evaluation/finger_3000_seed42/metadata.json) · [추출 통계](../../../../outputs/sweep_evaluation/finger_3000_seed42/analysis/summary.json) · [원시 로그 대조](../../../../outputs/sweep_evaluation/finger_3000_seed42/analysis/validation.json).

## 수집 및 전체 결과

| 항목 | 결과 |
| --- | --- |
| 체크포인트 | `logs/TEMP/inspire_sweep_simple_finger_v0/2026-11-10_14-30-35/model_3000.pt` |
| SHA256 | `c0ba049b72b9c34924e49748dcaec783705cfe12f0c5460e463bb47757db13ac` |
| 수집 시각 | 2026-11-10 21:36:12–21:49:19 KST, 약 13분 7초 |
| 완료 / 부분 에피소드 | 2,560 / 0, 모든 환경 quota 20 충족 |
| Timeout / 조기 종료 | 2,470 / 90, 동시 timeout+실패 0 |
| 원시 자료 | 1,238,332행, NPZ 79개 |
| 목표 3cm 이내 | 1,972 / 2,470 = 79.84% |
| 실제 환경 성공률, 전체 완료 에피소드 기준 | 1,972 / 2,560 = 77.03% |
| Timeout XY 오차 중앙값 / 평균 | 1.71 / 2.22cm |
| P90 / P95 / 최대 오차 | 4.24 / 5.92 / 28.23cm |
| 움직임 중 Contact 인정 | 894,085 / 1,014,614 step = 88.12% |

Contact는 3차원 속력 0.001m/s 이상인 구간이며 조기 종료 에피소드도 포함한다. 오차 통계는 Timeout 에피소드 기준이고, 위 표에는 이상치 제외를 적용하지 않았다. 원시 전체 행에서 순간 접촉과 2-of-3 접촉 이력을 독립적으로 재구성했으며 불일치는 각각 0건이다. 비정상 속력도 0건이다. 종료 term은 물체 낙하/기울어짐 78건, 선반 실패 12건, 팔 관절 속도 1건이며 한 에피소드에 여러 term이 겹칠 수 있다.

## 플롯

- [목표 중심 Scatter](../../../../outputs/sweep_evaluation/finger_3000_seed42/analysis/plots/timeout_scatter_zoom.png): GT 사분면별 200개 균등 무작위 비복원 추출, 총 800개, seed 42, alpha 0.65, ±5cm. 공간 밀도를 평탄화하지 않는다. 전체 패널과 개별 패널은 같은 샘플을 사용한다. 표시 범위 안의 점은 Q1 191개, Q2 191개, Q3 186개, Q4 187개다.
- [오차 박스 플롯](../../../../outputs/sweep_evaluation/finger_3000_seed42/analysis/plots/error_boxplot.png): 전체 집계 항목 없이 Q1–Q4, Y축 0–7cm, 상자 간격 축소, 중앙값 선과 평균 마름모. 공통 상위 Tukey fence 5.181260cm 초과 163개를 제외한 2,307개로 계산했다. 최대 잔존 오차 5.152949cm로 축 생략은 불필요했다. 제외 목록은 별도 CSV에 보존했다.
- [이론상 목표 생성 영역](../../../../outputs/sweep_evaluation/finger_3000_seed42/analysis/plots/goal_generation_region.png): 초기 위치 반경 2cm, 목표 변위 6–12cm, ±X 방향 Deadzone 반각 30도를 반영한 선반 원점 GT 영역. 수집 데이터로 경계를 추정하지 않았다.
- [움직임 중 Contact](../../../../outputs/sweep_evaluation/finger_3000_seed42/analysis/plots/moving_contact_ratio.png), [생성된 GT 목표](../../../../outputs/sweep_evaluation/finger_3000_seed42/analysis/plots/generated_goals.png), [개별 그림 목록](../../../../outputs/sweep_evaluation/finger_3000_seed42/analysis/plots/individual/index.md).

Times New Roman과 공통 밝은 사분면 색상을 사용했다. 이상치 제거는 오차 박스 통계에만 적용했고, Scatter·Contact·원시 로그에는 적용하지 않았다. 11–1시와 5–7시는 0개이며 임의 보충하지 않았다. 시계 방향 분류와 GT 사분면은 서로 다른 기준이다.

## 이전 체크포인트와 비교

| 이상치 제외 전 지표 | model1200 | model3000 |
| --- | --- | --- |
| Timeout 목표 3cm 이내 | 69.05% | 79.84% |
| Timeout 오차 중앙값 | 2.20cm | 1.71cm |
| 움직임 중 Contact 인정 | 84.42% | 88.12% |
| 전체 에피소드 실제 성공률 | 65.90% | 77.03% |

동일 Task·seed·환경 수·quota의 각 1회 평가 결과다. 정책별 조기 종료 시점이 달라 각 에피소드의 목표와 물리 궤적이 짝지어진 비교는 아니다. 여러 seed의 불확실성이나 학습 일반화 성능을 검증한 결과로 해석하지 않는다.
