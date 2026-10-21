# Clutter Curriculum v1 — 12000 iteration 이후 보상 비중

[개발 로그](README.md)

기준일: 2026-10-21. 환경·보상 설정·학습 로그는 변경하지 않았다.

## 대상과 방법

- Task: `Isaac-Inspire-Contact-Sweep-Clutter-Curriculum-v1`.
- Run: `logs/inspire_contact_sweep_clutter_v1_curriculum/2026-10-20_22-49-30`.
- Workspace HEAD `0e314e9`, 문서 HEAD `a953e0a`. 기존 사용자 수정 문서 2개와 색인의 기존 충돌 표식은 보존했다.
- 전체 0–12823 중 12000–12823 inclusive, 824 iteration. 15개 보상 시계열의 정렬·연속성·중복 없음·유한값을 확인했다.
- 각 iteration을 동일 가중 평균한다. 개별 episode 동일 가중 평균은 아니다.
- RewardManager는 함수 × weight × dt를 누적하고 reset 시 최대 episode 길이 10초로 나눈다. 저장값에 가중치를 다시 곱하지 않는다.
- 절댓값 비중 = abs(항별 평균) / 모든 항별 평균 절댓값 합계. 양의 보상 내 비중 = 항별 평균 / 양의 평균 합계.

## 결과

양의 합계 2.060421459, 비용 합계 −0.341351160, 순합계 1.719070299, 절댓값 합계 2.401772620. 비용은 양의 합계의 16.567%다.

| 항목 | 저장값 평균 | 전체 절댓값 비중 | 양의 보상 내 비중 | 순합계 대비 부호 있는 비율 |
| --- | ---: | ---: | ---: | ---: |
| `goal_distance` | +1.273574160 | 53.02643% | 61.81134% | +74.08505% |
| `reaching` | +0.779307196 | 32.44717% | 37.82271% | +45.33306% |
| `arm_speed_excess` | -0.195785116 | 8.15169% | — | -11.38901% |
| `pushing_speed` | -0.057151574 | 2.37956% | — | -3.32456% |
| `arm_joint_velocity` | -0.032398008 | 1.34892% | — | -1.88462% |
| `hand_action_rate` | -0.027201767 | 1.13257% | — | -1.58235% |
| `shelf_collision` | -0.013617667 | 0.56698% | — | -0.79215% |
| `goal_hold` | +0.007124041 | 0.29662% | 0.34576% | +0.41441% |
| `obstacle_displacement` | -0.005532869 | 0.23037% | — | -0.32185% |
| `arm_action_rate` | -0.005085716 | 0.21175% | — | -0.29584% |
| `hand_joint_velocity` | -0.003025420 | 0.12597% | — | -0.17599% |
| `object_tilt` | -0.001313536 | 0.05469% | — | -0.07641% |
| `contact_any` | +0.000345799 | 0.01440% | 0.01678% | +0.02012% |
| `shelf_failure` | -0.000239488 | 0.00997% | — | -0.01393% |
| `contact_count` | +0.000070264 | 0.00293% | 0.00341% | +0.00409% |

양의 보상 중 reaching 37.823%, goal_distance 61.811%, goal_hold 0.346%, 촉각 두 항 합계 0.0202%다. 기존 35/35/20/10 시나리오는 목표 체류 5초·접촉 7초를 가정한 것이며 실측과 다르다. 로그만으로 촉각 보상이 작은 원인이나 정책 성공률은 확정할 수 없다.

비용 중 arm_speed_excess 57.356%, pushing_speed 16.743%, arm_joint_velocity 9.491%, hand_action_rate 7.969%다.

12000–12399 / 12400–12823에서 양의 구성은 goal_distance 61.959/61.671%, reaching 37.651/37.986%, goal_hold 0.368/0.324%, 촉각 합계 약 0.022/0.019%다. 두 하위 구간에서도 비슷한 구성이다.

Curriculum 실측값은 pushing free speed 0.06 m/s, Arm free speed 0.9 rad/s, Arm action-rate·joint-velocity weight 각각 −0.05이며 분석 구간에서 일정했다.

## 재현과 검증

[분석 코드](../../03_assets/artifacts/clutter_v1_curriculum_reward_shares/analyze.py) · [정량 결과·원본 해시](../../03_assets/artifacts/clutter_v1_curriculum_reward_shares/summary.json) · [전체 항별 CSV](../../03_assets/artifacts/clutter_v1_curriculum_reward_shares/reward_shares.csv)

Workspace 루트에서 실제 실행:

```bash
/home/ssu/miniconda3/envs/newton/bin/python -B example/Contact-Rich-Manipulation-Context/03_assets/artifacts/clutter_v1_curriculum_reward_shares/analyze.py --log-dir logs/inspire_contact_sweep_clutter_v1_curriculum/2026-10-20_22-49-30 --output-dir example/Contact-Rich-Manipulation-Context/03_assets/artifacts/clutter_v1_curriculum_reward_shares
/home/ssu/miniconda3/envs/newton/bin/python -B src/inspire_sweep_baseline/scripts/analyze_clutter_rewards.py --log-dir logs/inspire_contact_sweep_clutter_v1_curriculum/2026-10-20_22-49-30 --last-n 824 --output /tmp/clutter_existing_analysis.json
```

- 별도 계산과 기존 분석기의 15항 평균을 절대 오차 1e-12로 대조: 일치. 절댓값 비중 합계와 부호 있는 순비중 합계 각각 100% 확인.
- 기본 Python은 tensorboard 미설치, env_isaaclab은 numpy 미설치로 읽기 실패하여 기존 newton 환경을 사용했다. 패키지 설치·환경 수정 없음.
- Train/mean_reward 평균 17.201704는 별도 episode 집계 버퍼를 사용한다. Episode_Reward 합계 × 10초 = 17.190703과 정확히 같을 필요는 없다. 비중은 일관된 Episode_Reward 항 사이에서 계산했다.
- 실제 play·새 학습·성공률 측정·원인 진단은 실행하지 않았다.
- 네이티브 인라인 시각화 도구가 제공되지 않아 표와 CSV로 전달한다.

문서 검증도 실제 실행했다. Workspace 루트에서 `python example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_markdown_math.py example/Contact-Rich-Manipulation-Context/02_implementation/logs/2026-10-21_clutter_curriculum_reward_shares.md example/Contact-Rich-Manipulation-Context/02_implementation/logs/README.md`: 2파일 통과. 문서 저장소 루트에서 `python 00_guidelines/scripts/check_document_links.py --check-external 02_implementation/logs/2026-10-21_clutter_curriculum_reward_shares.md`: 1파일·내부 링크 4개·오류 0. `git diff --check -- 02_implementation/logs/README.md`: 통과. 색인의 기존 충돌 표식 해결은 이번 범위 밖이다.
