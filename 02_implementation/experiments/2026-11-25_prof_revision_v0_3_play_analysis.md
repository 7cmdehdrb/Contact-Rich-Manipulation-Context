# Prof Revision v0_3 실제 Play 검증 보고서

2026-11-25 · `Inspire-Sweep-Prof-Revision-v0_3` · `model_7650.pt` · 실제 PhysX 재생 512개 완료 에피소드

## Executive Summary

**접촉을 유지하며 물체를 이동시키는 행동은 학습됐지만, 모든 방향에서 정밀하게 목표를 맞추고 손가락 자세를 완성하는 수준에는 도달하지 못했다.** 실제 성공은 **389/512회, 75.98%**다. 로봇 쪽으로 이동시키는 구역3은 **35/89회, 39.33%**로, 나머지 구역의 80.23–87.64%보다 낮다. 목표에 한 번 진입한 451회 중 62회가 최종 실패했다. [S1](#s1-실제-play-증거)

**접촉 유지는 강점이고, 방향 정렬과 종료 오차 수정이 약점이다.** 목표 밖에서 물체가 움직이는 frame의 접촉률은 **96.60%**다. 그러나 힘이 실제로 전달되며 물체도 움직이는 frame에서 목표와의 수평 힘 각도가 30° 이내인 비율은 **63.99%**, 90°를 넘는 반대 성분의 비율은 **17.47%**다. Sweep 진행 보상의 **99.86%가 첫 2초 안**에 발생했다. 성공군과 실패군 모두 초기 이동 이후 추가 진행 보상이 거의 없다.

**손가락 자세는 약지 중심이다.** 미는 frame에서 약지 끝–추적 OBB 간격은 평균 **8.26 mm**, 엄지는 **87.28 mm**다. 별도 실제 접촉 계측에서도 약지가 83.84%, 검지가 40.41%의 frame에서 타겟에 접촉했으며 엄지는 1.37%다. 이는 다섯 손끝이 함께 접근하는 자세가 충분히 형성됐다는 근거가 되지 않는다. 다만 v0_3의 Formation은 **거리 합만** 보상하므로 패드 각도나 다섯 손가락 실제 접촉은 원래의 강제 조건이 아니다. [S2](#s2-환경-계약과-코드)

**구현된 보상과 성공 판정은 저장된 물리 입력에 부합했다.** 16개 보상의 총합 오차는 최대 4.77e−7, 재계산한 성공·TCP 종료 불일치는 모두 0이었다. 실제 정책 성능의 위 한계와 수식 구현의 일치 여부를 구분한다. 드문 수 kN 접촉 하중의 해석은 아래 추가 대조 결과를 함께 봐야 한다.

**F/T의 물리적 충실도에는 별도 미해결 문제가 있다.** 동일 trajectory 재생에서 타겟 총 접촉력3.37 kN·전체 손 법선력3.29 kN인데 보정 F/T는 거의0인 사례가 재현됐다. 원시 mount 힘도9.73 N 수준이어서 단순 보정 제거만의 문제로 설명되지 않는다. 이 상태에서 F/T 기반 감지가 의도대로 작동했다고 판정하거나, 작은 `wrench_change`를 작은 충격의 증거로 쓰지 않는다. 원인 확정과 센서 경로 수정은 수행하지 않았다.

## 1. 무엇을 실행했는가

| 항목 | 실행 조건 |
| --- | --- |
| 체크포인트 | `logs/TEMP/2026-11-25/inspire_sweep_prof_revision_v0_3/2026-11-24_23-02-44/model_7650.pt` |
| 정책 | 저장 모델의 deterministic inference, 기존 관측 noise 유지, 학습/update 없음 |
| 표본 | seed42·43 각각 64개 병렬 환경, 각 환경의 첫 4개 완료 에피소드; 총512회 |
| 물리·정책 주기 | 물리0.01 s, 정책0.02 s, 정책당2개 물리 substep |
| 에피소드 | 최대10 s. 조기 물리 실패도 분모에 포함. 나중의 추가 reset 에피소드는 제외 |
| 실제 분석량 | 250,526개 policy transition, 환경별 시간 합5,010.52 s, substep501,052개 |
| 장비 | RTX4070, Isaac Sim5.1.0, PyTorch2.7.0+cu128, headless |
| 원래 설정 보존 | Reward·Termination·Observation·Action·Event·Command·Curriculum이 학습 저장 YAML과 모두 동일 |
| 실행용 차이 | 병렬 수·seed·산출물 경로, GPU found/lost pair buffer 2^25→2^21. 접촉 valid는 분석 frame 모두 True |

두 본 수집의 측정 loop+저장 시간은 각각215.36 s, 215.05 s다. 초기 앱/자산 기동과 후처리 시간은 여기에 포함하지 않는다. 동일 seed·4환경·20step에서 계측을 켠 경우와 끈 경우의 **정책 관측, 장애물 관측, 관절, 물체, 보상, done은 완전히 동일**했다. 마지막 손가락별 하중 계측을 포함한 버전도 재대조했다. [최종 hook 대조](../../../../outputs/prof_revision_v0_3_analysis_20261125/hook_parity_final.json)

최종 성공 기준은 **10초 종료 시 추적된 초기 가시 OBB 중심과 목표의 XY 거리 ≤30 mm**, 같은 step의 낙하/전도·선반·TCP 속도 실패 없음이다. 중간에 목표를 스치는 것만으로 성공하지 않는다. 이 표본에서 성공389회 모두 마지막1초를 계속 목표 안에 있었고, 388회는 종료 물체 수평 속도도10 mm/s 이하였다. 실제 원통 link 중심을 기준으로30 mm 밖인데 가시 OBB 때문에 성공한 사례는0회였다.

## 2. 성공은 75.98%이고 방향에 따라 차이가 크다

전체 Wilson95% 구간은 **72.09–79.47%**다. 같은 vector env의 반복4회를 하나의 묶음으로 재표집한10,000회 bootstrap 구간은 **72.27–79.49%**다. 초기 환경 수가128개라는 반복 구조를 반영한 후자를 주요 불확실성 범위로 본다. 두 seed의 결과는189/256회(73.83%)와200/256회(78.13%)다. 이 구간은 이 시뮬레이터·현재 reset 분포에서의 불확실성이고 실물 전이 성능을 포함하지 않는다.

| 목표 방향 구역 | 성공 / 완료 | 성공률 | Wilson 95% 구간 | 최종 거리 평균 |
| --- | --- | --- | --- | --- |
| 1 · 선반 안쪽 −X, ±30° | 78/89 | 87.64% | 79.21%–92.96% | 23.74 mm |
| 2 · 오른쪽 +Y, 120° | 134/157 | 85.35% | 78.98%–90.04% | 19.76 mm |
| 3 · 로봇 쪽 +X, ±30° | 35/89 | 39.33% | 29.82%–49.71% | 37.14 mm |
| 4 · 왼쪽 −Y, 120° | 142/177 | 80.23% | 73.74%–85.42% | 24.09 mm |

구역은 선반 좌표 기준이다. 구역1/3은 각각60°, 구역2/4는 각각120°라서 구역별 표본 수가 같지 않다. 전체 성공률은 episode count로 합산했으며 구역 비율을 단순 평균하지 않았다.

최종 분류는 성공389회, 목표 밖 timeout108회, 물체 낙하/전도6회, 선반 실패9회, TCP 속도 실패0회다. 물리 종료 flag가 겹칠 수 있어 표에서는 물체→선반→TCP 순서로 한 번만 분류했다. 원래의 개별 flag는 NPZ에 모두 남겼다.

전체 최종 거리의 중앙값은20.53 mm, P90은41.46 mm다. 성공군 평균17.63 mm, 목표 밖 timeout군 평균47.79 mm다. 목표에 한 번 들어간 비율은451/512회(88.09%)로 최종 성공률보다12.11%p 높다. **접근·초기 이동과 최종 유지/정밀 도달은 동일한 성과가 아니다.**

![최종 거리, 접촉률 timeline, 구역별 성공률과 최종 거리 분포](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/03_success_and_contact.png)

종료 반경만 사후 변경해서 계산한 민감도는10 mm에서11.52%,20 mm에서46.48%,30 mm에서75.98%,40 mm에서87.11%,50 mm에서91.21%다. 이는 **같은 저장된 최종 상태의 재판정**이며 환경이나 반경을 바꾸어 다시 학습·재생한 결과가 아니다. 30 mm 성공이 높은 정밀도의 중심 정렬을 뜻하지는 않는다.

| 활성 장애물 수 | 완료 에피소드 | 성공 | 성공률 |
| --- | --- | --- | --- |
| 0 | 63 | 45 | 71.43% |
| 1 | 79 | 59 | 74.68% |
| 2 | 81 | 56 | 69.14% |
| 3 | 65 | 49 | 75.38% |
| 4 | 75 | 62 | 82.67% |
| 5 | 62 | 48 | 77.42% |
| 6 | 87 | 70 | 80.46% |

장애물 수에 따른 단조로운 성공률 하락은 관측되지 않았다. 장애물 수 자체가 원인이라는 결론은 이 분할만으로 낼 수 없다. 모든 seed·episode index·장애물 수별 분모와 구간은 [groups.csv](../../../../outputs/prof_revision_v0_3_analysis_20261125/groups.csv)에 있다.

## 3. 16개 보상의 시간별 분포

아래 모든 그래프의 x축은 **에피소드 경과시간(s)**, y축은 **가중치와 dt를 적용한 policy step당 보상**이다. 선은 해당 시각에 살아 있는 에피소드의 평균, 음영은 그 분포의 P10–P90이며 신뢰구간이 아니다. 조기 종료 이후를 관측된0으로 채우지 않았다. 시각별 alive 분모와 전체 cohort 기준 종료 후0 기여 평균을 모두 [reward_timelines.csv](../../../../outputs/prof_revision_v0_3_analysis_20261125/reward_timelines.csv)에 저장했다. 드문 비용은 P10–P90이0이어도 발생할 수 있으므로 실제 step 최소·최대·발생률을 [rewards.csv](../../../../outputs/prof_revision_v0_3_analysis_20261125/rewards.csv)에서 확인할 수 있다.

![16개 모든 보상의 평균과 P10–P90 timeline](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/01_reward_timelines.png)

| 보상 항 | weight | 에피소드 평균 합 | 성공군 평균 | 실패군 평균 | 비영(非零) step 비율 |
| --- | --- | --- | --- | --- | --- |
| sweep_progress | 100 | 5.846084 | 6.430541 | 3.997680 | 4.97% |
| sweep_retreat | -20 | -0.197500 | -0.161765 | -0.310513 | 51.28% |
| reaching | 4.9 | 1.177277 | 1.186527 | 1.148023 | 41.49% |
| arm_action_rate | -0.03 | -0.068249 | -0.067452 | -0.070769 | 100.00% |
| hand_action_rate | -0.03 | -0.006197 | -0.005928 | -0.007050 | 99.95% |
| arm_joint_velocity | -0.03 | -0.211498 | -0.206846 | -0.226211 | 100.00% |
| hand_joint_velocity | -0.03 | -0.708612 | -0.719841 | -0.673098 | 100.00% |
| shelf_collision | -0.5 | -0.182101 | -0.183579 | -0.177429 | 9.43% |
| shelf_failure | -3 | -0.052734 | 0.000000 | -0.219512 | 0.00% |
| obstacle_contact | -0.04 | -0.001562 | 0.000000 | -0.006504 | 0.00% |
| wrench_change | -0.1 | -0.000033 | -0.000000 | -0.000136 | 0.01% |
| object_tilt | -30 | -0.036101 | -0.000482 | -0.148751 | 0.08% |
| obstacle_displacement | -150 | -0.493032 | -0.235266 | -1.308243 | 87.31% |
| arm_action_limit | -3 | -0.151806 | -0.149920 | -0.157772 | 14.72% |
| hand_action_limit | -3 | -0.187690 | -0.190037 | -0.180269 | 86.93% |
| contact_formation | 0.245 | 0.515341 | 0.549334 | 0.407835 | 100.00% |

에피소드 전체 보상 평균은 **5.241585**다. 성공군은6.245286, 실패군은2.067280이다.

| 에피소드 구간 | Reach | Sweep 진행 | Formation | 그 외 비용 합 | 순보상 |
| --- | --- | --- | --- | --- | --- |
| 0-1 s | 1.0166 | 2.6207 | 0.0274 | -0.6398 | 3.0249 |
| 1-3 s | 0.1553 | 3.2200 | 0.1113 | -0.7482 | 2.7384 |
| 3-6 s | 0.0049 | 0.0039 | 0.1650 | -0.4176 | -0.2438 |
| 6-10 s | 0.0005 | 0.0015 | 0.2117 | -0.4915 | -0.2779 |

구간 표는 각 에피소드가 해당 구간에 실제 받은 기여를 합친 뒤 **512회 전체로 나눈 값**이다. 조기 종료는 이후 기여가 없으므로 구간 합과 전체 에피소드 합이 일치한다.

Sweep 진행 보상95%를 벌기까지 걸린 시간의 중앙값은 **1.22 s**, P90은1.58 s다.2초 이후 기여는 전체 Sweep의 **0.142%**다. 최초 접촉 시간의 중앙값0.83 s, 첫 목표 진입 시간 중앙값1.14 s와 함께 보면 **접근→짧은 밀기→자세 유지**가 주된 행동이다. 실패한 에피소드에도 같은 시간 구조가 나타나므로 후기 정밀 수정이 충분하다고 보기 어렵다. 다만 이는 저장 trajectory의 관측이며 정책의 내부 의도나 원인을 직접 밝힌 것은 아니다.

![평균 보상 기여와 성공·실패군의 누적 총보상](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/02_reward_balance.png)

![성공·실패군을 나눈 16개 보상 timeline](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/08_reward_by_outcome.png)

Reaching은10 cm 이내에서 추가 접근 보상이0이 되며, Formation은 정지·무접촉·목표 밖에서도 양수가 될 수 있다. 실제 무접촉101,714 step에서 Formation 평균은0.000869/step이었다. 목표 밖에서 물체 속도·추적점 이동률 <1 mm/s, EEF 속도 <5 mm/s인 더 엄격한 정지 표본3,319 step 중71.65%는 순보상이 양수였지만, 그 집단의 순보상 **평균은−0.003506/step**이었다. 드문 큰 장애물 변위 비용이 평균에 영향을 주었다. 따라서 **정지 중 보상 통로는 존재하지만 정지가 평균적으로 항상 유리하다는 주장은 성립하지 않는다.**

## 4. 미는 동안의 접촉은 대부분 유지된다

접촉은 타겟–손 contact point의 법선 하중 합≥0.01 N인 물리 substep이 policy step 안에 하나라도 있으면 True다. 환경의 접촉 인정은 최근3개 policy step 중2개 이상 접촉한 경우다. 단일 frame의 물리 접촉과 이 이력 상태를 분리했다.

| 측정 집단 / 항목 | 결과 | 분모 |
| --- | --- | --- |
| 전체 에피소드 시간의 raw 접촉 | 59.40% | 250,526 step |
| 전체 시간의2-of-3 접촉 인정 | 60.26% | 250,526 step |
| 목표 밖에서 물체가5 mm/s 이상 움직일 때 raw 접촉 | **96.60%** | 11,021 step |
| 같은 이동 표본의2-of-3 접촉 인정 |90.98% |11,021 step |
| 같은 이동 표본의 두 물리 substep 모두 접촉 |91.55% |11,021 step |
| 첫 접촉부터 첫 목표 진입 또는 종료까지의 접촉률 | 에피소드 평균93.95%, 중앙값100% | 유효 운반 구간510회 |
| 운반 구간의 최대 접촉 단절 길이 | 중앙값0 s, P90 0.218 s, 최대7.44 s |512회; 구간 없는 경우0 |

2-of-3 인정률이 이동 접촉률보다 낮은 일부는 접촉 시작의1step 지연이다. 전체 인정률이 raw보다 높을 수 있는 것은 반대로 잠깐 끊겨도 이력이 남기 때문이다. 이 지표로 **접촉 유지 자체가 지배적인 실패 원인이라고 말하기는 어렵다.** 접촉은 계속되는데 방향이 나빠지거나 목표 밖에 머무는 사례도 확인했다.

## 5. 접촉 중 힘 방향에는 개선 여지가 있다

힘은 손이 **타겟에 가한 힘**, normal+friction의 substep 평균, world 축이다. 물체의 현재 추적 중심→목표의 수평 방향과 비교한다. 손목 F/T의 반력 벡터와 부호를 혼동하지 않았다.

방향 분석의 기본 분모는 **목표 밖(거리>30 mm), raw 접촉·valid, 수평 힘≥1 N**의12,145 frame이다. 그중 물체 수평 속도≥5 mm/s인9,539 frame을 ‘실제 미는 구간’으로 별도 표시했다. 방향이 정의되지 않는 무접촉·미소 힘 frame을0°로 넣지 않았다.

| 힘 방향 지표 | 접촉·1 N 이상·목표 밖 | 실제 미는 구간 |
| --- | --- | --- |
| 수평 오차 평균 |60.62° |42.01° |
| 수평 오차 중앙값 |29.26° |19.86° |
| 수평 오차 P90 |159.17° |143.09° |
|30° 이내 비율 |50.65% |63.99% |
|90° 초과 비율 |31.58% |17.47% |

30°는 분석을 위한 정확도 구간이고 v0_3의 성공 임계값은 아니다. 환경은 signed 수평 cos를 **[0,1]로 자른 뒤 전체3D 힘 크기로 정규화**한다. 반대 힘은 정렬 보상을0으로 만들지만 방향 자체의 음수 비용은 없다. 후퇴가 실제 발생하면 별도−20×후퇴 거리 비용을 받는다. 수평 각도가 같아도 수직 하중이 크면 원래 정렬 값은 작아진다. 기본 방향 표본의 수직 비중 |Fz|/|F| 중앙값은26.78%다.

![힘 방향 분포, 수직 힘 비중과 접촉 단절 길이](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/04_force_and_maintenance.png)

큰 각도가 모두 잘못된 제어 명령이라는 뜻은 아니다. 물체의 관성에 대한 제동이나 접촉 기하에 따른 반력일 수도 있다. 다만 후기 목표 오차가 남는 사례에서 큰 힘 각도와 진행 보상 소멸이 함께 관측됐으므로, 방향별 실패 trajectory를 다음 비교 실험의 우선 대상으로 삼을 근거는 있다.

## 6. 손가락 자세는 약지 중심이며 다섯 손끝의 균형은 약하다

v0_3의 실제 Formation은 다음과 같다. 다섯 손끝과 **초기 가시 조각을 따라 움직이는 OBB** 사이 외부 거리 합을 사용한다. 원통 전체 실제 표면까지의 거리가 아니다.

```math
F_t=\frac{0.05}{0.05+\sum_{i=1}^5 d_{i,t}},\qquad r_{F,t}=0.245F_t\times0.02.
```

실제 접촉·각도·힘·목표 진입 gate는 없다. 이 표본의 에피소드 평균 Formation raw는0.2140이고, 최대 에피소드 평균도0.5221로 이론상 최대1보다 낮다. 패드 +Z축과 패드→추적 중심의 **양방향** 오차를 따로 측정했으며, 아래 각도 진단이 원래 보상에 포함돼 있다고 해석하면 안 된다.

| 손가락 | 미는 동안 OBB 간격 평균 | OBB 5 mm 이내 비율 | 패드 축 각도 30° 이내 비율 |
| --- | --- | --- | --- |
| 엄지 | 87.28 mm | 1.33% | 4.67% |
| 검지 | 47.21 mm | 24.79% | 6.26% |
| 중지 | 54.98 mm | 5.37% | 37.63% |
| 약지 | 8.26 mm | 55.26% | 24.07% |
| 소지 | 45.49 mm | 6.13% | 22.65% |

![다섯 손가락의 OBB 간격과 패드 방향 진단](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/05_finger_posture.png)

실제 접촉 여부는 거리 proxy를 보완하기 위해 target-only normal force matrix에서도 확인했다. 이 추가 항목은 **seed43의256개 에피소드에만** 있으며, 아래 분모는 실제 미는 frame4,667개다. 한 frame에 여러 손가락이 닿을 수 있어 접촉 frame 비율의 합은100%가 될 필요가 없다. 접촉 기준은 그룹별 법선 resultant norm 합≥0.05 N다. 법선 하중 합 비중은 같은 길이의 frame을 더한 값으로, 전체 contact point의 스칼라 하중이나 마찰을 포함한 총하중과는 다른 지표다.

| 실제 collider 그룹 | 접촉한 frame 비율 | 전체 법선 하중 합 비중 | 상위 1% frame 제외 후 비중 |
| --- | --- | --- | --- |
| 엄지 | 1.37% | 0.33% | 0.69% |
| 검지 | 40.41% | 9.63% | 19.49% |
| 중지 | 6.81% | 16.89% | 4.79% |
| 약지 | 83.84% | 34.62% | 71.34% |
| 소지 | 3.73% | 1.91% | 2.85% |
| 손바닥 전용 센서 pad | 0.00% | 0.00% | 0.00% |
| hand base hull · 손바닥/손등 포함 | 1.74% | 36.63% | 0.83% |

약지가 가장 자주 접촉한다. 엄지·소지의 기여는 작다. `palm_pad`가0이라는 것은 **전용 pad collider가 접촉하지 않았다는 뜻**이며 손바닥 전체가 접촉하지 않았다는 뜻은 아니다. `hand_base`는 손바닥·손등·가장자리를 포함한 본체 hull이다. 이 드문 base 접촉의 큰 하중 때문에 전체 하중 합의 비중과 통상적인 접촉 빈도는 다르다. 상위1%의 전체 하중 frame을 제외하면 약지 비중은71.34%다. 제외 결과는 민감도 분석이며 원시 큰 하중을 삭제하거나 본 평가에서 제외하지 않았다.

![실제 타겟 접촉의 collider 그룹별 빈도와 법선 하중 비중](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/09_target_contact_body.png)

손바닥/손등 면 분류가 부여한 하중은 같은 시점 타겟 스칼라 법선 하중의 합에 비해4.64% 수준이었다. 그 분류된 일부 안에서만 손바닥 비중46.46%다. **대부분 미분류이므로 손바닥/손등 사용 비율 전체를 대표하는 수치로 쓰지 않는다.** v0_3는 원래 면 선호 계수를1로 통일했으므로 특정 면을 선택하지 않은 것 자체를 계약 위반으로 보지 않는다.

## 7. 속도·충돌·주변 물체 영향

TCP 종료의 대상은 `wrist_3_link` 원점의3D 선속도이며, EEF offset 속도가 아니다. 관측된 최대값은 **0.6561 m/s**, 임계값은 **4.0 m/s 이상**이다. TCP 종료0회는 현재 모델에서 조건이 작동할 상황이 없었다는 뜻이다. 저장된 속도로 predicate 일치는 확인했지만, 실제4 m/s 초과 상황에서의 보호 성능까지 이 실험으로 검증한 것은 아니다.

기존 부모의1 rad/s 팔 관절 종료는 제거돼 있다. 현재 trajectory에서 관절 최대 절대 속도>1 rad/s인 frame은9.70%, 관측 최대3.3995 rad/s였다. 이는 제거된 조건 아래의 동작을 확인한 것이고, 부모 환경의 반사실적 성공률을 계산한 결과는 아니다.

활성 물체 낙하/전도6회(1.17%), 선반 실패9회(1.76%)가 있었다. 활성 장애물 최대 변위의 에피소드별 중앙값은0.31 mm지만 P95는34.52 mm, 최대162.13 mm다. 주변 물체 영향이 항상 작다고 볼 수 없으며, 실패군의 장애물 변위 비용 평균−1.3082가 성공군−0.2353보다 컸다. 활성 물체 최대 tilt의 P95는4.27°, 최대58.86°로 드문 큰 실패가 존재한다.

팔 raw action 축6.91%, 손 raw action 축23.38%가 실행 허용범위 밖이었다. Action term이 적용한 clip 후의 물리 명령이 범위를 벗어났다는 뜻은 아니다. 원래 action-limit 비용은 이런 원본 출력을 비용화한다. 손 관절 속도 비용은 평균−0.7086/episode로 지속적인 비용 중 가장 크며, Formation+0.5153보다 컸다.

![손목·관절 속도, 장애물 변위와 성공/보상의 관계](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/06_safety_and_reward_alignment.png)

## 8. 드문 큰 접촉 하중과 F/T의 추가 대조

접촉 하중의 큰 꼬리를 삭제하지 않고 동일 seed43·64환경을1,600 step 다시 재생했다. 이 추가 실행은 본 성공률의 분모에 더하지 않았다. 계측을 추가한 trajectory의 **힘·action·물체 위치·보상은 원본 seed43의 첫1,600 step과 완전히 동일**했다. 따라서 추가 센서 조회가 새로 만든 행동이나 다른 초기 배치에서 나온 하중은 아니다. [추가 대조 JSON](../../../../outputs/prof_revision_v0_3_analysis_20261125/wrench_focus_summary.json)

[추가 원시 trace](../../../../outputs/prof_revision_v0_3_analysis_20261125/wrench_focus/trace.npz) · [실행 metadata](../../../../outputs/prof_revision_v0_3_analysis_20261125/wrench_focus/metadata.json) · [저장 trace 대조 코드](../../../../outputs/prof_revision_v0_3_analysis_20261125/analyze_wrench_focus.py).

102,020개 유효 추가 transition 중 최종 substep의 타겟 총 접촉력 norm>100 N인 frame이73개,9개 에피소드에서 나왔다. 그중62개에서 보정 F/T 힘 norm은0.1 N 미만이었다. 아래의 최대 사례는 seed43·env35·episode3·policy step73, 에피소드1.46 s다.

| 같은 시점의 물리·센서 항목 | 측정값 |
| --- | --- |
| 타겟에 손이 가한 총 힘 · normal+friction, 최종 substep |3,367.56 N |
| 타겟 법선 resultant norm |3,290.73 N |
| 전체 손 collider의 법선 resultant 합 norm |3,290.73 N |
| 원시 mount F/T의 힘 norm |9.7265 N |
| 중력·관성 support 추정의 힘 norm |9.7265 N |
| 보정 F/T의 힘 norm |6.96e−7 N |
| 해당 에피소드의 wrist_3_link 최대 속도 |0.6356 m/s |
| 해당 에피소드 최종 결과 |목표 밖 timeout, 최종 거리99.81 mm |

세 가지 가설을 구분했다.

1. **다른 손 접촉이 법선력을 상쇄했는가:** 큰 하중73개 중 전체 손 법선 resultant가 타겟 법선의5% 미만인 경우는0개였다. 최대 사례에서도 둘의 크기가 같다. 적어도 법선력의 단순 상쇄는 이 불일치를 설명하지 못했다. 전체 마찰력과 공간 모멘트의 모든 접촉별 경로까지 해소한 것은 아니다.
2. **2개 substep 평균과 최종 시점의 차이인가:** 최종 substep 자체가3.37 kN이고 직전 substep도 큰 하중이었다. 평균 시간창의 차이만으로 이 사례를 설명할 수 없다. underlying PhysX joint-force API와 lazy buffer의 시점 의미는 별도 확인 대상이다.
3. **보정기가 큰 원시 힘을 없앴는가:** 최대 사례의 raw부터9.73 N 수준이며 support 추정과 거의 같다. 큰 raw force를 보정식이 직접 제거했다는 증거는 없고, **mount의 incoming-joint-wrench 읽기 경로와 접촉 센서 반응 사이의 일관성**을 우선 확인해야 한다. 정확한 원인을 이 보고서에서 확정하지 않았다.

![동일 seed 큰 접촉 하중과 전체 손·원시·support·보정 F/T 대조](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/10_force_outlier_audit.png)

원시 contact point reduction과 별도 normal-force matrix가 큰 하중의 크기·시점을 서로 뒷받침한다. 그러나 이 값이 현실의 동일한 하중을 정량 재현한다고 인증한 것은 아니다. 중복 접촉·solver 제약·incoming-joint-force API의 의미나 캐시를 더 조사해야 한다. **시뮬레이터 접촉력과 보정 F/T의 대응이 미검증인 상태에서 ‘F/T를 통해 강한 접촉을 정상적으로 감지했다’ 또는 ‘wrench_change가 작으므로 동작이 부드럽다’고 결론 내릴 수 없다.**

보정 F/T는 본512회 전체에서 힘 norm 중앙값0.225 N, P95 2.130 N, 최대379.51 N, 모멘트 norm P95 0.0898 Nm였다. `wrench_change` 비영 frame 비율은0.00559%에 불과했다. 이는 해당 보정 신호가 임계값을 넘게 변한 경우가 드물었다는 측정이며, 강한 접촉이 없었다는 뜻은 아니다. 보상 수식 일치 검증과 **센서의 물리적 충실도 검증**을 분리해야 하는 이유다.

현재16개 보상에는 타겟 접촉력의 절대 크기를 직접 제한하는 항이 없다. `obstacle_contact`는 비타겟 물체만 대상으로 하고, `wrench_change`는 보정 F/T의 크기 변화량에 대한 비용이며 절대 타겟 힘 상한이 아니다. TCP 속도 종료도 힘 상한이 아니다. 따라서 원래 수식대로 보상·종료가 계산됐다는 사실만으로 큰 타겟 하중이 억제된다고 해석할 수 없다. 현재 정책이 F/T 입력에 얼마나 의존하는지는 별도 ablation 없이 확정하지 않았다.


## 9. 대표 에피소드에서 보이는 동작

모든 통계는512회 전체에서 계산했다. 아래 그림은 설명을 위한 개별 사례이며 표본 전체를 대체하지 않는다. 초기 EEF 위치가 멀어 finger gap이 크게 시작하는 것은 접근 단계다.

### 성공 사례

Seed 43, env 56, episode 0. 종료 `success`, 최종 거리 17.55 mm, 최소 거리 2.75 mm, 총보상 7.062. 해당 범주에서 **최종 거리의 중앙값에 가까운 실제 에피소드**를 선택했다.

![성공 사례의 보상·거리·접촉·힘·손가락 timeline](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/case_success.png)
### 목표 밖 timeout 사례

Seed 42, env 22, episode 2. 종료 `timeout_outside_goal`, 최종 거리 39.57 mm, 최소 거리 31.36 mm, 총보상 -11.228. 해당 범주에서 **최종 거리의 중앙값에 가까운 실제 에피소드**를 선택했다.

![목표 밖 timeout 사례의 보상·거리·접촉·힘·손가락 timeline](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/case_timeout.png)
### 목표 진입 후 실패 사례

Seed 43, env 50, episode 3. 종료 `timeout_outside_goal`, 최종 거리 34.05 mm, 최소 거리 25.70 mm, 총보상 2.660. 해당 범주에서 **최종 거리의 중앙값에 가까운 실제 에피소드**를 선택했다.

![목표 진입 후 실패 사례의 보상·거리·접촉·힘·손가락 timeline](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/case_lost_goal.png)
### 물리 실패 사례

Seed 43, env 46, episode 1. 종료 `shelf_failure`, 최종 거리 28.76 mm, 최소 거리 14.03 mm, 총보상 3.098. 해당 범주에서 **최종 거리의 중앙값에 가까운 실제 에피소드**를 선택했다.

![물리 실패 사례의 보상·거리·접촉·힘·손가락 timeline](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/case_physical_failure.png)

## 10. 학습 로그와 기존 영상의 보조 확인

학습 TensorBoard75개 scalar tag를 [training_scalars.csv](../../../../outputs/prof_revision_v0_3_analysis_20261125/training_scalars.csv)로 추출했다. 그림과 본문 비교는 체크포인트 iteration7650까지로 제한했다. 해당 iteration의 `Episode_Termination/success`는64.57%, `Metrics/timeout_success_rate`는71.78%였다. 전자는 학습 중 stochastic 정책의 집계, 후자는 timeout 집단의 최근 이력 집계여서 deterministic 전체 완료 에피소드 성공75.98%와 분모·집계 방식이 다르다. 서로를 동일한 성공률로 치환하지 않는다. `Episode_Reward/*`도 RewardManager가 에피소드 합을 최대10초로 나눈 로그이므로 위 에피소드 합과 직접 비교하면10배 단위 차이가 생긴다. [S3](#s3-학습-로그)

![iteration7650까지의 학습 로그 추이](../../../../outputs/prof_revision_v0_3_analysis_20261125/figures/07_training_context.png)

기존에 녹화된 동일 체크포인트의120초3시점 영상도 확인했다. 시작1·3·6·9초를 추출한 아래 시각 대조에서 접근 후 손을 유지하는 양상이 보인다. 이는 **별도1환경 녹화**여서64환경 평가의 특정 env/episode와1:1 대응한다고 주장하지 않는다. [S4](#s4-기존-3시점-영상)

![기존120초 영상의 첫 에피소드 시각 대조](../../../../outputs/prof_revision_v0_3_analysis_20261125/existing_video_contact_sheet.png)

## 11. 의도와 실제 결과의 최종 대조

| 검증 대상 | 확인 결과 | 판단 |
| --- | --- | --- |
|16개 보상·계수·dt 적용 보존 | 학습 YAML 일치, 합산 최대 오차4.77e−7 | 구현 일치 |
|면 계수1, 접촉·힘 정렬을 사용한 Sweep | 독립 거리 증분 재계산 오차≤1.87e−9 | 구현 일치 |
|10초·3 cm 성공 판정 | 저장된 물리 상태 재판정 불일치0 | 구현 일치, 성능75.98% |
|접촉을 유지하면서 이동 | 이동 frame96.60% 접촉 | 주된 강점 |
|모든 방향의 수행 | 구역3 성공39.33%, 나머지80.23–87.64% | 방향 일반화 불충분 |
|힘을 목표 방향으로 전달 | 이동 frame30° 이내63.99%, 반대 성분17.47% | 부분 달성 |
|다섯 손가락 Formation | 약지 중심 실제 접촉, 엄지·소지 약함 | 거리 shaping은 작동, 균형 잡힌 다지 자세는 입증 안 됨 |
|초기 이동 후 목표 수정 | Sweep99.86%가 첫2초, 목표 진입 후 최종 실패62회 | 후기 수정이 약한 행동 |
|TCP4 m/s 안전 종료 | 현재 predicate와 일치, 실제 발동0회 | 조건 구현 확인, 발동·보호 효과 미검증 |
|주변 물체·선반 보존 | 물리 실패15회, 장애물 변위 최대162 mm | 드문 큰 실패가 남음 |
|접촉력과 보정 F/T 대응 | 같은 시점3.37 kN 접촉·보정 F/T 거의0 재현 | 물리적 충실도 미검증, 원인 추가 확인 필요 |

우선 **접촉력–원시 mount–보정 F/T 경로의 일관성을 확인한 뒤**, 같은 초기 scene bank에서 구역3과 ‘목표 진입 후 이탈’ 사례의 후기 제어를 비교하는 것이 타당하다. 현재 정책이 목표 밖에서 정지/저속 유지할 때 촉각·F/T에 추가 수정에 필요한 신호가 남는지 확인해야 한다. 보상 수정 후보로는 후기 오차와 실제 접촉 자세를 더 직접 평가하는 기준을 검토할 수 있지만, 그 수정이 성능을 개선한다는 결과는 아직 없다. 현재 보고서는 보상·관측·제어·자산·checkpoint를 수정하지 않았다.

## 12. 측정의 범위와 한계

- 한 체크포인트, 두 seed, 현재 시뮬레이터·reset 분포의 성능이다. 학습 수렴, 다른 체크포인트의 우열, 실물 성능을 입증하지 않는다.
- 정량 평가의 policy step은50 Hz이고 contact substep은100 Hz다. 더 짧은 충격·고주파 stick-slip을 연속시간으로 복원하지 못한다.
- 힘 방향은 현재 타겟에 대한 ground-truth 접촉 데이터로 평가했다. 정책 입력에 이 ground truth를 추가하지 않았다. Actor는 기존 초기 OBB snapshot과 실제 로봇 상태·촉각·보정 F/T를 사용한다.
- Formation의 OBB 간격, 패드 축 방향, 실제 collider 접촉, 손바닥/손등 분류는 서로 다른 측정이다. 이들을 하나의 ‘자세 합격률’로 임의 합치지 않았다.
- force30°·이동5 mm/s·정지1 mm/s·pad5 mm는 해석을 위한 분석 기준이다. 환경 성공 기준·보상 계수를 변경한 것이 아니다.
- 구역·성공/실패군 비교는 관측 연관이다. 구역, 힘 방향, 장애물 영향 중 하나를 실패의 단독 원인으로 확정하지 않는다.
- 원격 선반 USD는 원래 Omniverse 경로에서 읽었으며 그 원격 서버의 자산 revision 전체를 archive하지 않았다. 현재 Python 소스 snapshot·해시, 초기 물리 상태, 최종 YAML, 모델 해시는 보관했다. PhysX solver state 전체를 저장한 simulator checkpoint는 아니다.

## 13. 원시 증거와 재현

### S1. 실제 Play 증거

[전체 요약 JSON](../../../../outputs/prof_revision_v0_3_analysis_20261125/summary.json) · [에피소드별512행 CSV](../../../../outputs/prof_revision_v0_3_analysis_20261125/episodes.csv) · [보상 총합/분포](../../../../outputs/prof_revision_v0_3_analysis_20261125/rewards.csv) · [시각별16항 분포](../../../../outputs/prof_revision_v0_3_analysis_20261125/reward_timelines.csv) · [구간별 보상 합](../../../../outputs/prof_revision_v0_3_analysis_20261125/reward_phases.csv) · [손가락 기하](../../../../outputs/prof_revision_v0_3_analysis_20261125/fingers.csv) · [실제 collider 접촉](../../../../outputs/prof_revision_v0_3_analysis_20261125/target_body_contacts.csv) · [전체 schema·단위·좌표](../../../../outputs/prof_revision_v0_3_analysis_20261125/data_dictionary.json).

[seed42 원시 trace](../../../../outputs/prof_revision_v0_3_analysis_20261125/seed42/trace.npz) · [seed43 원시 trace](../../../../outputs/prof_revision_v0_3_analysis_20261125/seed43/trace.npz) · [seed42 metadata](../../../../outputs/prof_revision_v0_3_analysis_20261125/seed42/metadata.json) · [seed43 metadata](../../../../outputs/prof_revision_v0_3_analysis_20261125/seed43/metadata.json) · [episode 시간축 정렬 배열](../../../../outputs/prof_revision_v0_3_analysis_20261125/episode_aligned.npz). NPZ의 각 배열은 원래 `[global_step,env,...]`이며, episode와step 열로 자동reset 전후를 식별한다. episode_aligned 배열은 `[episode,episode_step,...]`이고 조기 종료 이후는NaN이다.

[독립 재검산 결과](../../../../outputs/prof_revision_v0_3_analysis_20261125/validation.json)에서 완료 수·성공 수·최종 거리·보상 합·manager YAML·현재 코드 해시·원본 모델 불변을 대조했다. 모든 검사는 통과했다. 성공·TCP predicate는250,526개 eligible transition에서 재판정 불일치0이었다. 본 수집 전체 buffer를 포함한 수식 오차도 summary에 보관했다.

### S2. 환경 계약과 코드

[환경 설명](../environments/PROF_REVISION_V0.md#prof-revision-v0_3) · [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/prof_revision_envs.py) · [reward 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/prof_revision.py) · [접촉·거리 상태](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/prof_revision_state.py) · [손가락 기하](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/prof_revision_geometry.py) · [성공·TCP 종료](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/prof_revision.py).

체크포인트 SHA256은 `8fda7b805f02927fb21908582d8362701ed2f305dd0429436116debf55f23561`이다. 학습 당시 기록된 코드 commit은 `c8df111ce9c59636b2386ad7971df423a2b2b506`, 평가 시작 HEAD는 `464b01570a8f73a2b1abf1a426f5eb70e5e30f68`이며 활성 패키지의 두 commit 간 차이는0이다. 본문이 인용한 실제 실행 코드는 [source manifest](../../../../outputs/prof_revision_v0_3_analysis_20261125/seed43/source_manifest.json)와 source_snapshot에 보존했다.

계측기는 [collect_prof_revision_play.py](../../../../src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py), 통계·그래프 생성기는 [report_prof_revision_play.py](../../../../src/inspire_sweep_baseline/scripts/report_prof_revision_play.py)다. 개발 변경의 의도와 검증은 [개발 로그](../logs/2026-11-25_prof_revision_v0_3_play_analysis.md)에 남겼다.

### S3. 학습 로그

원본 `logs/TEMP/2026-11-25/inspire_sweep_prof_revision_v0_3/2026-11-24_23-02-44`의 TensorBoard와 params를 읽었다. 학습 로그를 수정하거나 정리하지 않았다. 원본 scalar와 wall time·iteration·tag는 [training_scalars.csv](../../../../outputs/prof_revision_v0_3_analysis_20261125/training_scalars.csv)에 보존했고, iteration7650보다 뒤의 scalar는 성능 비교에 사용하지 않았다.

### S4. 기존 3시점 영상

[high_angle 120초](../../../../outputs/three_view_recordings/Prof-Revision-v0_3/high_angle.mp4) · [rear_eye_level 120초](../../../../outputs/three_view_recordings/Prof-Revision-v0_3/rear_eye_level.mp4) · [inside_top_down 120초](../../../../outputs/three_view_recordings/Prof-Revision-v0_3/inside_top_down.mp4) · [녹화 metadata](../../../../outputs/three_view_recordings/Prof-Revision-v0_3/metadata.json).

### 재현 명령

프로젝트 root에서 Isaac Lab 환경을 활성화하고 원래 선반 자산에 접근할 수 있는 상태에서 실행한다. 기존 산출물을 덮어쓰지 않도록 새 출력 폴더를 사용한다.

```powershell
$out = "outputs/prof_revision_v0_3_replay_$(Get-Date -Format yyyyMMdd_HHmmss)"
foreach ($seed in 42,43) { python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --task Inspire-Sweep-Prof-Revision-v0_3 --checkpoint "logs/TEMP/2026-11-25/inspire_sweep_prof_revision_v0_3/2026-11-24_23-02-44/model_7650.pt" --output-dir "$out/seed$seed" --num_envs 64 --episodes 4 --seed $seed --headless }
python src/inspire_sweep_baseline/scripts/report_prof_revision_play.py --root $out --runs seed42 seed43 --training-run "logs/TEMP/2026-11-25/inspire_sweep_prof_revision_v0_3/2026-11-24_23-02-44"
```
