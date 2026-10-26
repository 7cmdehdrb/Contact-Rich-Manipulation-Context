# ObjectRandom-v3 로그 마지막 500 iteration 보상 비중

[개발 로그 목록](README.md)

기준일: 2026-10-26. 사용자 지정 원본 `logs/TEMP/2026-10-25_16-55-56`의 TensorBoard event를 읽기 전용으로 분석했다. 기존 코드·문서 작업트리 변경과 학습 로그를 보존했다.

## 구간·계산

TensorBoard step 11500~11999(양 끝 포함), 500 iteration, Episode_Reward 17항이다. 모든 항목이 같은 연속 step 500개를 가지며 누락·중복·비유한값이 없음을 assert했다. iteration별 scalar의 산술평균을 먼저 구하고 그 평균의 비율을 계산했다. iteration별 비율의 평균이나 TensorBoard smoothing 결과는 아니다.

`RewardManager.compute`는 함수 출력에 weight와 dt를 곱해 episode sum에 누적하며 `reset`은 누적값을 최대 episode 시간10초로 나누어 Episode_Reward로 기록한다. 따라서 보상 가중치를 다시 곱하지 않는다. 아래 환산값은 평균 로그값×10이며, 개별 에피소드 원시 표본을 재집계한 값은 아니다. 집계 가중 방식이 다른 Train/mean_reward와 정확히 일치할 필요는 없다.

그룹 내 비중은 양의 보상끼리 또는 페널티 절댓값끼리 각각100%다. 전체 절댓값 비중은 각 항목 평균 절댓값 / 전체 평균 절댓값 합이며 합계100%다. 순보상 기준 signed 비중도 CSV에 보존했다.

## 결과

양의 보상 합 40.944647, 페널티 합 -17.144895, 순합 23.799752(로그 평균×10 환산). 페널티는 양의 보상 총량의 41.8733%를 차감한다. Train/mean_reward의 같은500 iteration 평균은 23.780463다.

| 항목 | 평균 로그값×10 | 그룹 내 비중 | 전체 절댓값 비중 |
| --- | ---: | ---: | ---: |
| `reaching` | 7.646782 | 18.6759% | 13.1638% |
| `goal_distance` | 12.416413 | 30.3249% | 21.3746% |
| `goal_hold` | 9.477518 | 23.1471% | 16.3154% |
| `hand_contact` | 11.403934 | 27.8521% | 19.6316% |
| `arm_action_rate` | -2.634894 | 15.3684% | 4.5359% |
| `hand_action_rate` | -1.476555 | 8.6122% | 2.5419% |
| `arm_joint_velocity` | -0.224511 | 1.3095% | 0.3865% |
| `hand_joint_velocity` | -0.104831 | 0.6114% | 0.1805% |
| `object` | -7.944977 | 46.3402% | 13.6771% |
| `shelf_collision` | -0.697232 | 4.0667% | 1.2003% |
| `pushing_speed` | -1.024035 | 5.9728% | 1.7629% |
| `arm_speed_excess` | -2.722602 | 15.8800% | 4.6869% |
| `shelf_failure` | -0.015872 | 0.0926% | 0.0273% |
| `eef_linear_speed` | -0.252891 | 1.4750% | 0.4353% |
| `obstacle_contact` | -0.008155 | 0.0476% | 0.0140% |
| `object_acceleration` | -0.038185 | 0.2227% | 0.0657% |
| `wrench_change` | -0.000156 | 0.0009% | 0.0003% |

## 재현·검증

Workspace 루트에서 실행한 명령:

```bash
TF_CPP_MIN_LOG_LEVEL=3 /home/min/miniconda3/envs/env_isaaclab/bin/python outputs/reward_share_2026-10-25_16-55-56/analyze.py
```

exit0. 두 비중 합계100%, 항목 평균 합과 iteration별 총합 평균의 일치를 확인했다. 결과와 SHA-256·원본 크기·집계 정의는 [summary.json](../../../../outputs/reward_share_2026-10-25_16-55-56/summary.json), [CSV](../../../../outputs/reward_share_2026-10-25_16-55-56/reward_shares.csv), [재현 스크립트](../../../../outputs/reward_share_2026-10-25_16-55-56/analyze.py)에 저장했다. 새 학습·simulator·체크포인트 재생은 수행하지 않았다. 이 분석은 보상 기여의 측정이며 정책의 성공 원인이나 특정 보상 계수의 적절성을 입증하지 않는다.
