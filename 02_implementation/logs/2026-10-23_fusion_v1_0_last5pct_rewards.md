# Fusion v1_0 학습 후반 5% 보상 구성

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-fusion-v10--2026-10-22)

기준일: 2026-10-23. 사용자 지정 run의 TensorBoard 원본을 읽기 전용으로 분석했다. 현재 소스의 계수로 보상을 다시 계산하거나 학습 로그를 수정하지 않았다.

## 원본과 정의

원본 run: `logs/TEMP/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0/2026-10-22_08-34-18_4833cc00/attempt_000`.

`Episode_Reward/*` 17개 항의 기록은 iteration 0~16433, 총 16434개다. 마지막 5%는 기록 수의 0.05배를 올림한 **822개**, iteration **15612~16433** 양끝 포함으로 선택했다. 마지막 checkpoint 16400이나 계획한 90000 iteration이 아닌 실제 기록 끝을 기준으로 한다. iteration별 동일 가중 평균이며 TensorBoard smoothing은 적용하지 않았다.

RewardManager는 가중치·dt가 이미 적용된 episode 누적 보상을 최대 episode 길이 10초로 나누어 기록한다. rollout 동안 reset별 summary의 평균을 Logger가 기록하며 이번 평균은 그 iteration scalar들의 산술평균이다. 개별 episode 수 가중 평균이나 제어 step 평균으로 해석하지 않는다. 표의 평균에 10을 곱하면 동일 집계 방식에서 episode 누적 보상 단위로 환산된다. 현재 환경 소스와 학습 당시 저장 설정이 다를 수 있으므로 비중 계산에 현재 가중치를 재적용하지 않는다.

전체 비중은 `abs(mean_i) / sum(abs(mean_j)) * 100`이다. 군내 비중은 양수 보상끼리 또는 음수 페널티끼리 절댓값을 합한 분모다. 각 iteration의 비중을 계산한 뒤 평균한 값과는 다르다. 이 구간에서 항목별 부호가 양수와 음수 사이를 바꾸지 않았다.

## 결과

| 보상 항목 | 평균 로그 값 | 전체 절댓값 비중 (%) | 양수/음수 군내 비중 (%) |
| --- | ---: | ---: | ---: |
| reaching | +0.788080675 | 30.246681 | 37.015986 |
| goal_distance | +1.32986677 | 51.040531 | 62.463567 |
| goal_hold | +0.00466615618 | 0.17908793 | 0.21916839 |
| hand_contact | +0.00641428763 | 0.24618154 | 0.30127776 |
| arm_action_rate | -0.000789339991 | 0.030295014 | 0.16565952 |
| hand_action_rate | -0.00975120198 | 0.37425292 | 2.0464938 |
| arm_joint_velocity | -0.0148801712 | 0.57110371 | 3.1229153 |
| hand_joint_velocity | -0.00502460294 | 0.19284518 | 1.0545181 |
| object | -0.0316583337 | 1.2150527 | 6.6441638 |
| shelf_collision | -0.0177823201 | 0.68248872 | 3.731992 |
| pushing_speed | -0.14237188 | 5.4642589 | 29.879718 |
| arm_speed_excess | -0.194904551 | 7.4804725 | 40.904799 |
| shelf_failure | -0.000376032526 | 0.014432197 | 0.078918295 |
| eef_linear_speed | -0.0582272729 | 2.2347734 | 12.220212 |
| obstacle_contact | -1.50987375e-06 | 5.7949232e-05 | 0.0003168786 |
| object_acceleration | -0.000716122877 | 0.027484928 | 0.15029337 |
| wrench_change | -1.57803797e-09 | 6.0565387e-08 | 3.3118429e-07 |

양수 보상 합 **2.129027888**, 페널티 합 **-0.476483340**, 순합 **1.652544548**, 절댓값 합 **2.605511228**다. 페널티 크기는 양수 보상 합의 **22.38032%**다.

양수 보상의 reaching+goal_distance 비중은 **99.47955%**다. goal_hold와 hand_contact는 양수 합의 각각 **0.21917%**, **0.30128%**다. 페널티는 arm_speed_excess **40.90480%**, pushing_speed **29.87972%**, eef_linear_speed **12.22021%** 순이다. 이는 로그의 평균 기여도이며 해당 항목의 유용성이나 계수 변경 효과를 입증하지 않는다.

## 재현과 검증

실제 실행 명령:

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  outputs/fusion_reward_analysis/2026-10-23_v1_0_last5pct/analyze.py
```

스크립트는 CSV를 새 파일로 생성하므로 재실행 시 새 출력 폴더에 복사해서 실행한다.

- [재현 스크립트](../../../../outputs/fusion_reward_analysis/2026-10-23_v1_0_last5pct/analyze.py)
- [보상별 평균·비중 CSV](../../../../outputs/fusion_reward_analysis/2026-10-23_v1_0_last5pct/reward_summary.csv)
- [Iteration별 추출 CSV](../../../../outputs/fusion_reward_analysis/2026-10-23_v1_0_last5pct/rewards_by_iteration.csv)
- [원본 해시·분석 JSON](../../../../outputs/fusion_reward_analysis/2026-10-23_v1_0_last5pct/analysis.json)
- [저장된 초기 보상 설정 발췌](../../../../outputs/fusion_reward_analysis/2026-10-23_v1_0_last5pct/source_rewards_config.txt)

17개 scalar의 연속성·중복 부재·구간 일치·유한값 검증을 통과했다. 추출 CSV에서 독립 재집계한 평균과 일치하고 전체·군내 비중 합은 각각 100%였다. 원본 이벤트 파일의 분석 전후 크기와 SHA-256이 동일했다. 이벤트는 47959376 bytes, SHA-256은 `8bde3bb27d24cd2675d56cec63e1dbbc9f9d59ff755d46da7cf08f9a058c1181`다. 학습 상태 JSON의 running 표시는 분석 구간 선택에 사용하지 않았다.

새 시뮬레이션·학습·보상 코드 수정은 없으며 Isaac Sim 재생이나 CPU 회귀 테스트는 이번 분석에서 실행하지 않았다. 기존 사용자 변경은 보존했다.
