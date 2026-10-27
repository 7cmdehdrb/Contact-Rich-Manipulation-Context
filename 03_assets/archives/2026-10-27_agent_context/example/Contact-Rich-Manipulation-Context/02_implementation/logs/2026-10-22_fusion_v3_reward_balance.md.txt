# Fusion v3 iteration 6000~마지막 보상 구성 분석

[개발·실험 로그](README.md) · [활성 Fusion v3](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-fusion-v3--2026-10-21)

기준일: 2026-10-22. 사용자가 지정한 `logs/rsl_rl/inspire_contact_sweep_clutter_fusion_v3/2026-10-21_21-55-18`의 실제 TensorBoard 이벤트를 읽어 보상별 평균과 비중을 계산했다. Data 분석 스킬의 원본·집계 단위·분모·재현성 기준을 적용했다. 새 학습·재생이나 보상 계수 변경은 수행하지 않았다.

## 기준과 집계 방법

Workspace HEAD `a2fcb0b`, 문서 submodule HEAD `f5655d0` 및 이전 작업트리 변경을 보존했다. 원본 학습 로그는 읽기 전용으로 취급했다. 원본은 해당 run의 `events.out.tfevents.1792587337.min-System-Product-Name.1586792.0`이며, `Episode_Reward/*` 14개 항이 iteration 0~7389까지 있다. 요청 범위는 **6000~7389 양끝 포함, 1,390 iteration**이다. 마지막 checkpoint `model_7350.pt`나 앞선 재생의 `model_7200.pt`로 분석 종료점을 제한하지 않았다.

실제 사용한 [`RewardManager.reset`](../../../../IsaacLab/source/isaaclab/isaaclab/managers/reward_manager.py)은 가중치와 dt를 적용한 episode 보상 누적값을 최대 episode 길이 10초로 나누어 기록한다. RSL-RL Logger는 rollout 중 reset step별 summary를 평균한다. 이번 표는 그 TensorBoard 값에 대한 **iteration 동일 가중 산술평균**이며 smoothing이나 weight의 재적용은 없다. 개별 episode 수로 가중한 전 구간 episode 평균은 원본 scalar만으로 복원하지 않는다. 각 평균에 10을 곱하면 같은 집계 방식의 episode 누적 보상 기여로 환산된다. `Train/mean_reward`는 별도의 episode 이동 집단을 사용하므로 보상 항 평균의 합과 동일하다고 가정하지 않는다.

비중은 구간 평균을 먼저 구한 뒤 계산한다. 전체 비중은 `abs(mean_i) / sum(abs(mean_j)) × 100`, 군내 비중은 양수 항끼리 또는 음수 항끼리 절댓값을 합한 분모를 사용한다. 이번 구간에서 각 항의 iteration별 부호가 일정하므로 부호 변화에 따른 평균 상쇄는 없다. 표에는 비활성 `eef_orientation`을 추가하거나 다른 항을 임의로 분리하지 않았다.

## 결과

| 항 | 평균 TensorBoard 값 | 전체 절댓값 비중 % | 양수/페널티 군내 비중 % |
| --- | ---: | ---: | ---: |
| reaching | +0.760964219 | 33.38419 | 42.51111 |
| goal_distance | +0.965514768 | 42.35800 | 53.93829 |
| goal_hold | +0.061984171 | 2.71930 | 3.46273 |
| contact_any | +0.001309984 | 0.05747 | 0.07318 |
| contact_count | +0.000262845 | 0.01153 | 0.01468 |
| action_rate | −0.059787416 | 2.62293 | 12.21699 |
| joint_velocity | −0.024607528 | 1.07955 | 5.02831 |
| object | −0.112646416 | 4.94190 | 23.01822 |
| shelf_collision | −0.041404550 | 1.81645 | 8.46063 |
| pushing_speed | −0.098929372 | 4.34012 | 20.21528 |
| arm_speed_excess | −0.149019989 | 6.53764 | 30.45082 |
| shelf_failure | −0.000035400 | 0.00155 | 0.00723 |
| eef_linear_speed | −0.002794758 | 0.12261 | 0.57108 |
| wrench_change | −0.000153831 | 0.00675 | 0.03143 |

양수 합은 **1.7900359865**, 페널티 합은 **−0.4893792616**, 순합은 **1.3006567249**다. episode 누적 보상 기여로 환산하면 각각 +17.900359865, −4.893792616, +13.006567249다. 페널티 크기는 양수 보상 합의 **27.3391%**다.

양수 보상에서 reaching+goal_distance가 **96.4494%**, goal_hold는 **3.4627%**, 접촉 두 항의 합은 **0.0879%**다. 페널티에서는 Arm speed excess **30.4508%**, object **23.0182%**, pushing speed **20.2153%** 순이다. F/T 변화율 항은 페널티 합의 **0.03143%**, 양수 보상 합 대비 크기는 **0.00859%**다. 이는 해당 구간의 평균 기여 비중이며, 이를 근거로 계수 증감의 학습 효과를 확인했다고 해석하지 않는다.

## 재현과 검증

실제 실행 명령은 Workspace 루트에서 다음과 같다.

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  outputs/fusion_reward_analysis/2026-10-22_iter6000_end/analyze_rewards.py \
  > outputs/fusion_reward_analysis/2026-10-22_iter6000_end/analysis_stdout.json
```

- [재현 스크립트](../../../../outputs/fusion_reward_analysis/2026-10-22_iter6000_end/analyze_rewards.py): TensorBoard scalar를 전량 읽고 요청 구간을 선택한다. CSV는 exclusive creation으로 생성하므로 재실행은 비어 있는 새 폴더에 스크립트를 복사해서 수행한다.
- [보상별 평균·비중 CSV](../../../../outputs/fusion_reward_analysis/2026-10-22_iter6000_end/reward_summary.csv): TensorBoard 평균·episode 누적 환산·전체 비중·군내 비중·양수 합 대비 부호 있는 비율·최솟값·최댓값.
- [Iteration별 원본 추출 CSV](../../../../outputs/fusion_reward_analysis/2026-10-22_iter6000_end/rewards_by_iteration.csv): 1,390행 ×15열, iteration과 14개 보상 항.
- [분석·검증 JSON](../../../../outputs/fusion_reward_analysis/2026-10-22_iter6000_end/analysis.json): 원본 파일명·SHA-256·크기·범위·계산 정의·합계·모든 항의 정밀값·검증 상태.

검증은 다음을 모두 통과했다. 원본 protobuf event를 `RawEventFileLoader`로 직접 해독한 값이 `EventAccumulator`의 값과 일치했다. 14개 항 모두 6,000~7,389의 1,390개 연속 scalar를 가지며 누락·중복·비유한값이 없었다. 추출 CSV를 NumPy로 다시 읽어 평균을 독립 집계했고 오차 허용 범위 `rtol=1e-13, atol=1e-15`에서 일치했다. 전체 비중의 합과 각 군내 비중의 합은 각각 100%였다. 분석 전후 원본 event 파일의 SHA-256·크기가 동일했다. 새 시뮬레이션 또는 패키지 코드 변경이 없으므로 Isaac Sim 재생·전체 CPU 회귀 테스트는 이번 분석에서 다시 실행하지 않았다.

변경한 문서 2파일의 Markdown 수식 검사를 통과했다. 상대 링크 검사는 내부 74개·workspace 외부 파일 5개·오류 0이었고, 수정한 색인의 `git diff --check`도 통과했다. 루트 `PLAN.md` 등 기존 사용자 변경은 유지했다.
