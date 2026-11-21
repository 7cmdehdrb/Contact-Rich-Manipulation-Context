# Single Contact 보상 timeline과 교수님 지시 대조

## 판단

[교수님 지시](../../../../docs/instruction.md)에 비추어 현재 체계는 **실제 목표 방향 이동은 구분하지만, 목표 밖 정지와 최종 성공을 구분하는 보상은 충분하지 않다**. 접근·접촉·이동·주변 물체 보호·안정화의 역할을 나눠 볼 수 있는 구조는 갖추었다. 실제로 진행한 경우의 Sweep 보상도 확인했다. 다만 Reach는 목표 달성 여부와 무관하게 매 스텝 지급되며, 성공 자체에 주는 항은 없다. 목표 밖에서 멈춘 실패 사례에서도 보상이 지속되는 것이 실제 timeline에서 확인되었다.

이번에는 보상·가중치·환경을 변경하거나 재학습하지 않았다. 현상과 원인 가설을 구분하고, 다음 조정 실험의 기준 데이터를 확보하는 단계다. 누적 보상의 구성 비중을 정책 gradient나 학습 영향력 비중으로 해석하지 않는다.

## 실제 행동·보상 timeline

![목표 밖 정지 실패의 실제 보상 timeline](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/15800_scene020_timeout_never_entered_R3.png)

15,800 iteration, 공통 초기 장면20, 구역3 사례다. 타겟은 초기 목표 거리 약9.9cm에서4.57cm까지 이동했지만 성공 반경3cm 안으로 들어가지 못했다. 약3초 이후 타겟 이동과 Sweep 보상이 거의 사라지고 Reach가 누적 보상을 계속 올린다. episode 총 보상은8.960, Reach7.457, Sweep 진행2.224였다. 마지막2초에 목표 밖에서 거의 정지한 상태의 순보상만1.513이었다. EEF–타겟 거리는10cm 부근이며, 이것은 타겟–목표 거리가 아니다.

목표 이탈 사례인 장면9는 마지막 거리3.42cm로 실패했지만 총 보상11.315를 받았다. 같은 체크포인트의 성공 episode 보상 중앙값10.579보다 크다. 이런 실패는5회였다. 성공 episode의 평균 보상10.665는 실패 평균7.544보다 높으므로 보상이 성능과 완전히 무관하다는 뜻은 아니다. 최종 성공과 누적 보상의 순위가 항상 일치하지 않는다는 근거다.

- [목표 진입 후 이탈 timeline](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/15800_scene009_timeout_left_goal_R2.png)
- [성공 timeline](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/15800_scene039_success_R4.png)
- [팔 속도 종료 timeline](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/15800_scene045_arm_velocity_R1.png)
- [초기 정책의 타겟 접촉 실패 timeline](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/00000_scene098_no_contact.png)
- [15개 항의 원값과 적용값 전체 timeline 예시](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/15800_scene020_timeout_never_entered_R3_all_terms.png)

그림은 거리·속도·타겟 접촉력·스텝 보상·누적 보상·접촉 이력/힘/표면/목표 조건을 같은 시간축에 표시한다. 검은 조건 band는 해당 조건이 참인 구간이다. overview에서 생략한 작은 항도 `_all_terms.png`의15개 패널과 원시 데이터에 보존했다.

## 항 정의와 의도하지 않은 보상 경로

정책 주기는0.02초다. 모든 항의 적용 기여도는 원래 callable 값 × weight ×0.02다. Sweep 두 항과 shelf_failure는 callable 내부에서0.02로 나누므로 결과적으로 거리 또는 사건 단위의 보상이 된다. 아래 수치는 dt 적용 후 기준이다.

| 항 | 입력·활성 조건·적용식 요약 | 의도 | 점검 결과 |
| --- | --- | --- | --- |
| sweep_progress | 거리 감소 ×50 ×접촉 인정1/0 ×양의 힘 정렬 ×접촉면 계수 | 실제 목표 방향 밀기 | 현재 접촉·유효 데이터·XY 합력1N·높이·이력이 필요하다. 잘못된 면도0.7, 미분류는1.0으로 보상 가능 |
| sweep_retreat | 목표 거리 증가 ×−10 | 역방향 이동 억제 | 현재 접촉 여부와 무관하다. 접촉을 끊어 역방향 비용을 피하는 구조는 아님 |
| reaching | EEF–타겟3D 거리10cm 이내0.016/step,45cm에서0 | 접근 유도 | 접근 이후 움직이지 않아도 지속 지급.10초 내내 최대면8.0 |
| arm_action_rate | 원시 팔 action 변화6채널 제곱합 ×−0.0006 | 명령 안정화 | 접촉 변화나 실제 속도와 구분되는 제어 입력 비용. 명시적 포화 없음 |
| hand_action_rate | 원시 손 action 변화6채널 제곱합 ×−0.0006 | 손 명령 안정화 | 실제 clipping 이전 원값을 비용에 사용 |
| arm_joint_velocity | 팔 관절속도 제곱합, cap100 ×−0.0006 | 실제 팔 움직임 완화 | action 변화 비용과 연관되나 입력·책임은 다름. 종료는 별도로 관절1개라도1rad/s 초과 |
| hand_joint_velocity | 손12관절 속도 제곱합, cap100 ×−0.0002 | 실제 손 움직임 완화 | 명령6채널과 실제12관절의 차이 존재 |
| shelf_collision | 선반 움직임 또는 EEF가 선반 중심20cm 안일 때 손가락/손목 높이 비용 ×−0.01 | 선반 간섭 완화 | 조건부 높이 비용과 선반 실제 움직임이 한 항에 들어 있음 |
| shelf_failure | 선반 속도/손목 clearance 실패 시−3 | 위험한 선반 간섭 억제 | 선반 변위 종료만 발생한 경우와는 다른 predicate |
| obstacle_contact | 타겟 제외 장애물 접촉 합력50N 초과의 지수 비용, cap100 ×−0.0008 | 주변 물체에 큰 힘 방지 |50N까지 무반응,52.65N에서포화. 여러 힘의 벡터 합이므로 방향 상쇄 가능 |
| wrench_change | 보상용 실제 wrench의 힘/모멘트 크기 변화,30N/3Nm부터 지수 증가,75N/7.5Nm에서 cap1 ×−0.002 | 충격 완화 | 힘 방향만 바뀌고 크기가 같으면0. 관측 noise·정규화와 분리 |
| object_tilt | 활성 타겟/장애물의5° 이후 기울기 정규화 제곱합 ×−0.6 | 전도 방지 | 약51.57°에서 각 물체별포화. 그 부근은 별도 실패 종료도 존재 |
| obstacle_displacement | 활성 장애물3D 변위 제곱합, 전체cap0.04m² ×−3 | 주변 물체 위치 보존 | free band 없이 작은 변위에도 지속 비용. 접촉력 비용과 달리 접촉 종료 후에도 남음 |
| arm_action_limit | 팔±π/2 밖 원시 action 초과량/허용폭의 평균 제곱 ×−0.0006 | 범위 초과 명령 억제 | 실제 실행 clipping과 별도 |
| hand_action_limit | 손0–URDF 한계 밖 원시 action 초과량/허용폭의 평균 제곱 ×−0.0006 | 손 범위 초과 억제 | 최소1채널 clipping이 거의 항상 존재해 실효성을 추가 점검할 필요 |

접촉 유지 자체의 독립 양의 보상, goal_hold, goal_distance, 최종 성공 bonus는 활성 항에 없다. 접촉 유지는 Sweep의 인정 gate다. 따라서 접촉만으로 별도 보상을 지급하는 문제는 없지만, 접촉 여부와 관계없는 Reach의 지속 지급은 남아 있다.

![함수의 문턱·포화·크기 비교](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/reward_function_shapes.png)

### 중복·상충과 함수 특성

Reach는 가까이 있는 상태를, Sweep은 목표 거리 감소를 평가한다. 목표 밖 정지 시 Sweep은0이지만 Reach는 거의 최대값을 유지할 수 있다. 목표에 진입해도 Reach의 역할은 바뀌지 않는다. 이 때문에 성공과 정지를 분리하는 신호가 약하다.

정방향과 역방향 항은 동시에 활성화되지 않지만, 계수가 다르므로 전체가 거리 potential 차이는 아니다. 다른 비용을 제외하고 접촉 인정·정렬1이라면1cm 멀어진 뒤1cm 다시 가까워지는 왕복은 선호 면0.75−0.10=0.65, 중립0.50−0.10=0.40, 반대 면0.35−0.10=0.25의 양의 보상이 가능하다. 실제 정책이 의도적으로 이를 악용했다고 확정하지 않는다. 장면9에서는 거리 감소 총9.82cm·증가 총2.57cm가 관측되었지만, overshoot와 복구도 같은 수치를 만들 수 있다.

action 변화·관절속도·wrench 변화는 모두 안정화 목적이지만 명령 변화, 실제 운동, 물리 충격이라는 다른 입력이다. 이들을 수학적으로 완전 독립시킬 필요는 없다. 다만 같은 동작에서 비용이 겹치는 정도를 timeline으로 확인해야 한다. 이번 결과에서는 이들 비용이 Reach·진행 보상보다 누적 기여를 압도한다는 근거는 없었다. **안정화 비용이 커서 정지했다는 인과 결론은 내릴 수 없다.**

장애물 접촉력과 변위는 힘을 가한 순간과 그 후에 남은 위치 오차를 각각 평가한다. 목적이 다르지만, 같은 밀기 사건의 비용이 두 번 누적될 수 있는 관계는 의도적으로 관리해야 한다. 접촉력 지수식은50N 기준을 조금 넘는2.65N 구간 안에서 전 범위를 소진한다. 반대로 wrench 변화는30→75N의 넓은 구간에서 증가한다. 가중치보다 먼저 문턱과 곡선의 민감도를 점검해야 한다는 교수님 지시에 해당한다.

## 동일 초기 장면의 체크포인트 비교

![체크포인트 비교](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/checkpoint_comparison.png)

| iteration | 성공/128 | 성공률 | 평균 episode 보상 | Reach 기여 | Sweep 진행 기여 | 마지막2초 목표 밖 정지 중 순보상 양수인 episode |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 0.00% | 1.987 | 2.554 | 0.000 | 128 |
| 1,000 | 38 | 29.69% | 8.479 | 7.110 | 2.126 | 83 |
| 4,000 | 64 | 50.00% | 9.365 | 7.203 | 2.835 | 59 |
| 8,000 | 57 | 44.53% | 8.767 | 6.948 | 2.697 | 65 |
| 12,000 | 65 | 50.78% | 9.599 | 7.213 | 3.136 | 58 |
| 15,800 | 82 | 64.06% | 9.543 | 7.012 | 3.251 | 38 |

모든 checkpoint는 **현재 보상과 현재 환경**으로 재평가했다. 과거 학습 당시에 발생한 reward log를 복원한 표가 아니다. 학습이 진전되며 성공과 Sweep 보상은 대체로 증가했지만 단조적이지 않다.12,000→15,800에서 성공률은 상승했으나 평균 총 보상은약0.055 감소했다. 이 작은 차이의 통계적 유의성이나 가중치의 인과 효과를 주장하지 않는다.

15,800의 성공률 Wilson95% 구간은55.45–71.85%다. 앞선 별도640회 평가의67.50%와 표본·seed·환경 수가 다르며 두 수치를 합산하지 않는다. 이번 고정 bank는 구역1/2/3/4 각각19/48/16/45개다. 구역3은12,000과15,800에서 각각1/16 성공으로 여전히 취약했다. 한 학습 run 안의 checkpoint 비교이며 독립 학습 seed 비교는 아니다.

![체크포인트별 누적 보상 시간 변화](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/checkpoint_reward_timelines.png)

집단 timeline에서는 각 초기 episode가 끝난 뒤 보상을0으로 유지했다. 뒤의 auto-reset episode 보상을 섞지 않는다. 아직 종료되지 않은 초기 episode 수를 별도 패널에 표시했다.

### 15,800에서의 실제 기여와 gate

평균 양의 기여 Reach7.012·Sweep3.251 중 Reach 비중은68.32%다.13개 비용 합계는평균−0.719였다. 이것은 누적 수치 구성이지 학습 영향력68.32%라는 뜻이 아니다.

정지 구간에서도 양의 순보상이 남았다. 목표 밖 정지 접촉의 평균 순보상은0.01499/step, 목표 밖 비접촉·EEF 정지 구간은0.01525/step이었다. 같은 구간의 Reach는각각0.01576·0.01584/step으로, 거의 최대0.016이다. 현재 체크포인트의 시간 초과 실패33회 모두 마지막 목표 밖 정지 구간에서 양의 순보상을 받았다. 목표 밖 정지가1초 이상이며 그 구간 순보상이 양수인38회에는 일부 팔 속도 종료도 포함된다. 그 구간의 순보상률 중앙값은약0.7685/초다.

Sweep 진행 항은 전체 초기 episode step의6.65%에서 양수였다. 그러나 목표 밖 실제 이동 접촉3225frame만 대상으로 하면 **81.77%에서 양수**, XY 힘1N gate 통과90.17%, 접촉 이력·높이 인정92.12%였다. 목표 안 유지·접근·정지 구간이 전체 분모에 섞인6.65%만으로 gate가 과도하게 엄격하다고 결론내리면 안 된다.

주변 물체 접촉 합력의99분위는0.896N, 최대36.68N으로50N 미만이었다. 그래서 obstacle_contact 항은 이 평가에서0이었다. 가벼운 접촉을 과도하게 억제한다는 근거는 없으며,50N 초과 구간에서 실제 보호 성능을 검증한 것도 아니다. Wrench 힘 크기 변화의99분위는1.676N, 최대37.889N, 모멘트 변화99분위0.0661Nm·최대2.877Nm였다.30N 초과는 드물어 wrench_change도 거의 작동하지 않았다. 기울기 비용은0.01% 정도에서만 발생했다.

손 action은 최소1채널이 허용 범위를 벗어난 step이100%였다. 채널별 초과 빈도도94.37–99.91%였다. 평균 hand_action_limit 기여는−0.185로 총 양의 보상보다 작았다. 이것만으로 해당 비용을 키워야 한다고 결정하지 않는다. 원시 출력 부호·크기, 열린 손에 필요한 실행 clipping, 관측의 last-action 표현을 함께 점검할 후속 근거다. 원시 action과 이전 action을 모두 저장했다.

## 교수님 지시 항목별 점검과 후속 실험

| 지시 | 이번 점검 | 판단·다음 단계 |
| --- | --- | --- |
| 평가 목적 정의 | 접근·접촉·이동·보호·안정화와 최종 성공을 분리 | 최종 성공을 별도로 장려하는 신호가 부족한 부분을 확인 |
| 중복·상충 | Reach–Sweep–정지, 안정화3종, 힘–변위 관계 대조 | 항의 독립성보다 역할과 실제 동시 기여를 관리해야 함 |
| 함수 범위·민감도 |12패널 함수 그래프, 실제 입력 분포·문턱·포화 기록 | Reach plateau·1N gate·힘 비용50→52.65N·wrench cap을 확인 |
| 실제 step timeline | 성공·목표 미진입 정지·목표 이탈·팔 속도 실패의15개 항 원값과 적용값 저장 | 수행 완료 |
| 실제 기여에 따른 조정 |6 checkpoint·공통128장면·조건부 gate·phase 기여 분석 | 조정 근거 확보. 가중치만 일괄 변경할 근거는 부족 |
| 수정 후 성능 검증 | 보상 변경·재학습을 하지 않음 | 이번 결과를 보상 수정의 효과로 보고하지 않음 |

우선 실험은 접근 목적의 Reach를 상태 지속 지급에서 접근 진전에 대한 신호로 바꾸거나 접촉 이후 줄이는 안과, 목표 진입·유지·종료 성공의 신호를 분리하는 안이다. 목표 밖 정지의 양의 이득이 줄고 성공률·최종 거리·안정성이 같이 좋아지는지 같은 scene bank와 추가 독립 seed로 검증해야 한다. 이것은 제안이며 적용하지 않았다.

그 다음 정·역방향 보상을 potential 형태 또는 왕복 이득을 제한하는 형태로 비교하고,1N gate는 실제 이동 접촉의 미통과 구간을 보고 판단한다. 장애물·wrench 항은 이번 일반 평가에서 초과 상황이 거의 없었으므로, 더 큰 비용을 주기 전에 통제된 충격/장애물 접촉 probe로 함수의 유효 구간을 검증하는 편이 지시문의 순서에 맞는다.

## 보존 데이터와 재분석

데이터 root는 `outputs/reward_timeline/model15800_family`다.6개 trace 합계242,683,843byte, 약231.44MiB다.768개의 공통 bank episode에 대한 보상 분석을 완료했다. 각 trace에는 이후 auto-reset episode도 일부 포함되며, 비교 대상은 `episode==0`뿐이다.

- [데이터 manifest·파일 해시·shape/dtype](../../../../outputs/reward_timeline/model15800_family/dataset_manifest.json)
- [단위·좌표·보상 정의](../../../../outputs/reward_timeline/model15800_family/field_units.json)
- [전체 수치·검사 결과](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/summary.json)
- [768개 episode 표](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/episodes.csv)
- [항별 활성 빈도·분위·누적 기여](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/term_statistics.csv)
- [행동 phase별 보상](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/phase_rewards.csv)
- [전체·목표 밖·이동 접촉 조건부 gate](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/conditional_gate_statistics.csv)
- [실제 입력 분포](../../../../outputs/reward_timeline/model15800_family/reviewed_analysis/input_distributions.csv)
- [사용한 소스312개와 설정 snapshot](../../../../outputs/reward_timeline/model15800_family/source_snapshot.zip)

각 `iteration_XXXXX` 폴더에 `trace.npz`, `metadata.json`, `reward_terms.json`, `environment.yaml`, `initial_scene.npz`, 초기 scene/관측 해시, torch RNG 상태를 저장했다. 초기 물체 pose/velocity·bounds·활성 mask·로봇 관절·선반·목표·대표 표면점·관측을 보존했다. **이것은 PhysX 내부 solver/contact state까지 복원하는 완전한 simulator checkpoint는 아니다.** 현재 목적의 offline 재분석에는 checkpoint나 simulator 실행이 필요 없다.

원시 보상은 `reward_raw`, 가중치만 적용한 rate는 `reward_weighted_rate`, 실제 dt 적용 기여는 `reward_contribution`, 전체는 `reward_total`이다.15개 항의 순서는 metadata의 `reward_terms`다. 원값과 weight와 dt가 따로 있어 후속 가중치의 산술적 재계산은 가능하지만, 이를 바꾼 정책의 행동이나 성공률 변화로 해석해서는 안 된다.

```python
import json
from pathlib import Path
import numpy as np

root = Path('outputs/reward_timeline/model15800_family')
run = root / 'iteration_15800'
meta = json.loads((run / 'metadata.json').read_text())
trace = np.load(run / 'trace.npz')
env_id = 20
mask = trace['episode'][:, env_id] == 0
time_s = trace['step'][mask, env_id] * meta['dt']
term_names = meta['reward_terms']
applied_rewards = trace['reward_contribution'][mask, env_id]
raw_rewards = trace['reward_raw'][mask, env_id]
```

```powershell
python src/inspire_sweep_baseline/scripts/analyze_reward_timelines.py outputs/reward_timeline/model15800_family --output-dir outputs/reward_timeline/model15800_family/new_analysis
python outputs/reward_timeline/model15800_family/prepare_dataset.py
```

## 검증·제한

전 체크포인트의 초기 물리 상태와 첫 관측의 항목별 SHA-256 dictionary가 정확히 일치했다. 정책에 따라 이후 reset 시점과 RNG 소비가 달라지므로 이후 모든 관측 noise가 동일한 paired trajectory라는 뜻은 아니다. 정책은 deterministic inference이고 기존 관측 noise를 유지했다. 당시 GPU는RTX4070 12GB, Windows conda `env_isaaclab`,128환경·seed1729·500정책 step이었다.

모든 원시 float의 유한성, 최초 episode128개 완료, 누적 보상 합, 실제 RewardManager의 step reward를 검사했다. 최대 합계 오차5.96e-8, manager rate×dt 오차2.98e-8이었다.14개 항의 입력으로부터 독립 재구성한 적용 보상 최대 오차는5.96e-8이었다.

**shelf_collision의 움직임 gate는 별도 제한이 있다.** 저장한 `shelf_moved_proxy`는 runtime 초기 선반 pose를 기준으로 하지만 실제 callable은 default root pose+env_origins를 기준으로 삼는다.5mm 문턱 부근에서 checkpoint별51–70frame이 달랐고 독립 재구성의 스텝 오차는0.01이었다. 실제 callable 원값·적용값은 정확히 저장해 timeline과 통계에는 그 값을 사용했다. 높이 기반 부분을 제외한 잔여값은0/1 gate임을 검사했지만, 이 항 전체를 독립 검증했다고 기록하지 않는다.

최초 집계는 NumPy 정수의 JSON 직렬화에서 중단되었다. Python int로 명시 변환한 뒤 재집계했다. 물리 데이터는 재수집하거나 제외하지 않았다. 최초 `analysis`, 중간 `analysis_final` 폴더는 보존했고 최종은 `reviewed_analysis`다. 조건부 이동 접촉이0개인 초기 정책의 비율은 빈 값으로 저장하며0으로 대체하지 않았다.

관측 noise 없는 비교, 독립 학습 seed, 보상 수정 후 재학습, 충격/장애물 과부하의 통제 실험은 하지 않았다. 교수님 지시를 완전히 충족했다고 결론내리기보다, **현재 단계에서 확인된 보상–행동 불일치와 다음 조정 실험의 근거**로 사용한다.
