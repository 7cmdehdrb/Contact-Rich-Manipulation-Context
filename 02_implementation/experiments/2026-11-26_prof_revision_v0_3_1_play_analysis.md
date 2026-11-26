# Prof Revision v0_3_1: 방향별 Play와 보상 의도 검증

작성일: 2026-11-26 KST · `Inspire-Sweep-Prof-Revision-v0_3_1` · 최신 보관 checkpoint `model_15550.pt`.

## 핵심 결과 (Executive Summary)

실제 headless Play **512episode에서 334성공(65.2%)**이었다. seed·환경 단위 cluster bootstrap95% 구간은 60.5%–69.9%다. 로봇 반대 −X 78/93(83.9%)와 로봇 쪽 +X 46/90(51.1%) 사이 차이가 크다. 목표 방향과 실제 순이동 방향은 대체로 맞지만, 목표 반경 안에 최종적으로 정착하는 문제를 별도로 보아야 한다. [1]

**최초 도달보다 도달 후 유지가 주요 약점이다.** 491/512건(95.9%)이 목표 반경에 들어갔지만 157건은 최종 실패했다. 특히 −Y 측면은165/166건이 진입하고도74건이 최종 실패했다. 아래 최종 위치 분포에는 목표를 지나친 방향의 편향이 보인다.

목표 밖에서 물체가 움직이는 동안 실제 접촉은 **96.3%**였다. 물체 root의 처음→마지막 순이동 각도 오차는 평균 **8.12°**, 이동 중 접촉합력 각도 오차는 평균 **66.68°**다. 두 지표는 endpoint 이동과 순간 힘을 측정하므로 같지 않다.

손가락 거리×각도 결합은 독립 재계산과 일치했다. 하지만 Formation은 평균 **+6.853**, 전체 양의 보상의 **46.2%**를 차지하며, 그중 **22.3%**가 타겟과 실제 접촉이 없는 step에 지급됐다. 자세 proxy가 실제 손가락별 접촉과 일치하는지 아래에서 확인했다. 식 구현 일치와 좋은 조작 자세의 달성은 구분한다. [1][2]

환경·보상·종료·PPO를 수정하지 않았다. 여기서의 판단은 해당 checkpoint·두 seed의 관찰이며, 부모 v0_3보다 향상됐다는 인과 비교는 하지 않는다.

## 방향 정의와 평가 분모

각 seed42·43에서64환경의 처음4개 **완료** episode, seed당256건을 포함했다. 조기 실패도 포함하며 자동 reset 전 terminal 상태를 수집했다. 추론 행동은 deterministic, 원래 observation noise는 유지했다. 초기 장면 분포를 그대로 사용했으므로 방향별 표본 수는 다르다. 성공은10초 timeout에서 **추적 중인 초기 가시 OBB 중심의 목표 XY 오차≤30mm**이고 물리 실패가 없어야 한다. 실제 root와 추적점의 차이는 별도 기록했다. [1][2]

각도 θ=`atan2(초기 방향Y, −초기 방향X)`로 로봇 반대 −X를0°로 둔다. −30°≤θ≤30°는 로봇 반대, |θ|≥150°는 로봇 쪽, 나머지 양의 각도는+Y·음의 각도는−Y 측면이다. 표본 영역 폭은 각각60°/120°/60°/120°이므로 건수가 같아야 하는 설계가 아니다.12개30° 세부 구간은 [전체 방향 집계](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/direction_summary.json)에 있다.

| 방향 | 성공/전체 | 성공률 | 95% cluster 구간 | 최종 오차 중앙값/P90 | 진입했으나 최종 실패 |
| --- | --- | --- | --- | --- | --- |
| 로봇 반대 −X | 78/93 | 83.9% | 75.3%–91.3% | 18.44/41.28mm | 14 |
| +Y 측면 | 119/163 | 73.0% | 65.3%–80.4% | 20.18/50.17mm | 38 |
| 로봇 쪽 +X | 46/90 | 51.1% | 40.5%–61.8% | 29.88/64.91mm | 31 |
| −Y 측면 | 91/166 | 54.8% | 47.0%–62.6% | 28.81/48.98mm | 74 |

## 최종 위치: 목표 축을 따라 멈춘 곳과 옆으로 벗어난 곳

전체 최종 목표 오차 중앙값은 **23.80mm**, P90은 **49.93mm**였다. 목표 반경에 한 번이라도 들어간 491건 중 최종 실패는 157건이다. 따라서 ‘한 번 도달’과 최종 성공을 구분해야 한다. 마지막1초 전부 반경 안에 있던 성공은 333/334건이다. [1]

그림의 원점은 목표, 세로축은 초기 목표 방향(양수=목표를 지나침, 음수=덜 이동), 가로축은 그 방향의 XY+90° 횡방향 오차다. 점선 원은30mm 성공 경계다. 물리 실패는 경계 안에 있어도 실패 색으로 표시한다.

![방향별 최종 목표 상대 위치 분포](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/figures/direction_final_positions.png)

| 방향 | 목표방향 평균 오차 | 횡방향 평균 오차 | 순이동 각도 오차 평균 | 각도 유효 episode |
| --- | --- | --- | --- | --- |
| 로봇 반대 −X | 12.33mm | 0.71mm | 7.72° | 92 |
| +Y 측면 | 18.80mm | 6.61mm | 5.02° | 162 |
| 로봇 쪽 +X | 0.47mm | 8.77mm | 18.28° | 88 |
| −Y 측면 | 25.80mm | 3.75mm | 5.98° | 166 |

−Y 측면의 평균 목표방향 오차는 **+25.80mm**로 목표를 지나친 쪽이다. 반면 로봇 쪽은 순이동 각도 오차 평균18.28°·목표에 한 번도 진입하지 못한13건도 있어, 모든 방향 실패를 같은 원인으로 묶지 않는다. 이 분포는 관찰이며 제동·접촉·제어 중 어느 원인이 주도했는지는 대조 실험 없이 확정하지 않는다.

순이동 각도는 실제 root의 reset→최종 XY 변위와 초기 목표 방향의0–180° 오차다. 순이동5mm 미만은 각도에서 제외하고 위치·성공 통계에는 남겼다. 중간 궤적의 흔들림은 endpoint 각도만으로 평가하지 않는다. world 좌표·목표 상대 좌표·실제 heading은 [episode별 CSV](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/direction_episodes.csv)에 있다.

## 접촉 유지와 힘·이동 방향

이동 frame은 목표 오차>30mm·타겟 XY 속도≥5mm/s다. 힘 각도는 이 중 유효한 실제 접촉·수평 합력≥1N인 frame만 사용한다. 접촉 유지는 이동 frame 수를 합쳐 비율을 계산하며 episode별 퍼센트의 단순 평균과 다르다. both-substeps는 두10ms 물리 substep 모두 normal load≥0.01N인 경우다. [1]

전체254,165개 유효 step의 접촉률은 74.0%다. 최초 접촉부터 최초 목표 진입까지(미진입이면 종료까지)의 접촉률은 유효511episode 평균95.9%, 이 구간의 가장 긴 접촉 공백 P95는0.14초였다. 초기 접근·도달 후 대기를 포함한 전체 접촉률과 아래 이동 중 접촉률은 분모가 다르다.

| 방향 | 이동 frame | 실제 접촉 | 2/3 접촉 인정 | 양 substep 접촉 | 순간 힘 오차 평균 | 속도 방향 오차 평균 |
| --- | --- | --- | --- | --- | --- | --- |
| 로봇 반대 −X | 2372 | 98.2% | 93.9% | 93.1% | 60.81° | 65.27° |
| +Y 측면 | 4982 | 98.6% | 95.2% | 96.6% | 66.72° | 76.07° |
| 로봇 쪽 +X | 3723 | 96.6% | 92.8% | 89.9% | 83.73° | 86.78° |
| −Y 측면 | 6556 | 93.6% | 88.9% | 82.9% | 58.85° | 60.79° |

![방향별 성공·접촉·순이동·힘 방향](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/figures/direction_performance.png)

이동 중 접촉합력이 목표 대비30° 이내인 비율은 47.2%,90° 초과는 36.1%였다. 초기1초 평균은 18.47°, 남은 거리>60mm는 28.30°,30–60mm는 86.54°다. 힘에는 제동·되돌림·미끄러짐에 대한 반력이 포함되므로90° 초과를 모두 잘못된 행동으로 단정하지 않는다. Sweep은 양의 거리 감소×최근3step 중2step 접촉×정렬 계수이며, 역방향 힘은 정렬0으로 진행 보상을 차단한다. [2]

## 16개 보상·페널티의 크기와 timeline

episode 평균 양의 기여 합은 **+14.833**, 음의 기여 합은 **−2.355**, 순보상은 **+12.477**다. 양/음 비중은 각 step·각 term의 부호를 분리한 합계 기준으로 각각100%가 된다. Reach처럼 양·음 양쪽이 있는 항은 두 예산에 모두 나타난다. 순보상 대비 비율은0 근처에서 불안정해 사용하지 않았다. [1]

| term | 평균 누적 기여 | 양의 예산 비중 | 음의 예산 비중 |
| --- | --- | --- | --- |
| sweep_progress | +6.7340 | 45.4% | 0.0% |
| sweep_retreat | -0.3753 | 0.0% | 15.9% |
| reaching | +1.1751 | 8.4% | 3.0% |
| arm_action_rate | -0.0732 | 0.0% | 3.1% |
| hand_action_rate | -0.0128 | 0.0% | 0.5% |
| arm_joint_velocity | -0.2547 | 0.0% | 10.8% |
| hand_joint_velocity | -0.8780 | 0.0% | 37.3% |
| shelf_collision | -0.1155 | 0.0% | 4.9% |
| shelf_failure | +0.0000 | 0.0% | 0.0% |
| obstacle_contact | -0.0006 | 0.0% | 0.0265% |
| wrench_change | -2.62e-05 | 0.0% | 0.00111% |
| object_tilt | -0.0354 | 0.0% | 1.5% |
| obstacle_displacement | -0.1390 | 0.0% | 5.9% |
| arm_action_limit | -0.1253 | 0.0% | 5.3% |
| hand_action_limit | -0.2744 | 0.0% | 11.7% |
| contact_formation | +6.8526 | 46.2% | 0.0% |

![16개 항목 보상 timeline](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/figures/01_reward_timelines.png)

위 그림은 해당 시각까지 살아 있는 episode의 평균·P10–P90이며, 아래 방향별 그림은 최초 cohort를 고정하고 조기 종료 뒤 기여를0으로 둔다. 두 분모를 혼동하지 않는다. 시간별 실제 step 기여와 구간 누적값도 [timeline CSV](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/reward_timelines.csv)·[phase CSV](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/reward_phases.csv)에 남겼다.

![방향별16항 보상 timeline](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/figures/direction_reward_timelines.png)

Sweep 누적 보상의 99.7%가 첫2초에 집중됐다. 반경 안에서 발생한 Sweep 비중은 26.2%다. Formation의 7.7%는 목표 밖·물체 속도<1mm/s인 구간에서 발생했다. 이 지표는 로봇까지 정지했다는 뜻은 아니다. 로봇 EEF도<5mm/s인 별도 정체6262frame에서 순보상>0인 비율은 94.4%였고, timeout 실패 중 마지막2초의 절반 이상을 이 상태로 보낸 것은 0건이었다.

**실제 목표 이탈 사례:** seed43·env41·episode1는 목표 안에 진입한 뒤 최종 오차41.00mm로 실패했다. 그런데 순보상은 **+13.773**, Formation은 **+6.208**였다. 아래 그림에서 목표 밖 정지 상태 이후에도 Formation이 누적된다. 이 사례는 최종 오차 중간값에 가까운 이탈 사례로 선택했으며 전체 발생 빈도를 대신하는 표본은 아니다.

![목표 진입 후 이탈했지만 지속 보상을 받은 실제 사례](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/figures/case_lost_goal.png)

## 장애물 보호: 이동량과 비용을 함께 본다

장애물 이동량은 활성 비타겟의 초기 위치 대비3D root 변위다. 아래 분모는 장애물이 있는 episode만 포함한다. 비용은 전체 episode의 활성 장애물 합산이며, 원위치 이탈 제곱×시간이므로 충돌 충격·yaw·누적 경로와 같은 지표가 아니다. [1][2]

| 방향 | 장애물 있는 건수 | 최대 변위≥1cm/≥5cm | 최대 변위 P95 | 평균 비용³ | ≥1cm 이동하며 성공 |
| --- | --- | --- | --- | --- | --- |
| 로봇 반대 −X | 82 | 4/0 | 8.73mm | −0.027 | 3 |
| +Y 측면 | 137 | 13/6 | 33.86mm | −0.285 | 3 |
| 로봇 쪽 +X | 77 | 8/2 | 35.30mm | −0.204 | 2 |
| −Y 측면 | 150 | 6/0 | 0.65mm | −0.023 | 0 |

³ 비용 평균의 분모는 해당 방향 전체 episode다. 개별 물체 peak·최종 변위·50Hz 누적 경로는 [장애물 CSV](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/direction_obstacles.csv)에 있다. 접촉 비용0은 충돌0을 의미하지 않는다. 접촉 항의 손–장애물 합력50N 문턱은 타겟을 통한 간접 충돌이나 모든 팔 링크 충돌을 포괄하지 않는다.

![방향별 장애물 변위와 손가락 자세](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/figures/direction_obstacles_fingers.png)

## 손가락 자세: 각도 보상과 실제 접촉의 차이

v0_3_1 Formation은 각 손가락의 `0.05/(0.05+gap) × cos²(normal,타겟 중심 방향)`을5개 합산한다. raw0–5·weight0.245·dt0.02초여서 최대0.0245/step,10초 동안 최대+12.25다. 양방향 cos²는 지문 normal의 부호를 구분하지 않는 의도된 계약이다. 실제 접촉·정지·목표 도달을 지급 조건으로 쓰지 않는다. [2]

| 손가락 | 이동 접촉 중 pad gap 평균 | 양방향 normal 오차 평균 | gap≤5mm & 각도≤30° | 해당 손가락 타겟 접촉 | 평균 Formation 기여 |
| --- | --- | --- | --- | --- | --- |
| 엄지 | 38.28mm | 34.36° | 0.0% | 20.1% | +1.068 |
| 검지 | 19.41mm | 37.63° | 35.3% | 25.5% | +1.253 |
| 중지 | 10.75mm | 37.42° | 29.0% | 51.9% | +1.596 |
| 약지 | 19.82mm | 28.22° | 10.8% | 15.2% | +1.648 |
| 소지 | 30.14mm | 31.40° | 6.0% | 8.6% | +1.288 |

각도 오차는 `acos(|cos|)`의0–90°다. gap은 distal pad의 추적 가시 OBB까지 거리이며 실제 전체 물체 표면까지 거리와 같지 않다. 타겟 접촉률은 해당 손가락의 모든 sensor body에서 마지막 물리 substep normal load 합≥0.05N인 비율이다. 지문점이 멀어도 다른 마디가 닿을 수 있어 두 열을 구분한다. 방향별5개 손가락 원시 집계는 [손가락 CSV](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/direction_fingers.csv)에 있다.

5mm·30°는 진단용 구간이며 기존에 확정된 과업 성공 조건이 아니다. 현재 식은 문턱형이 아니라 완만한 연속 점수다. 엄지의 동시 근접·정렬 비율0%와 Formation 기여가 동시에 관측되듯이, 점수의 양수 여부만으로5개 손가락이 모두 적절히 접촉했다고 판단할 수 없다. 방향별 접촉 방식이 달라 전체 평균뿐 아니라 heatmap도 함께 본다.

추가로 원래6개 drive 채널 순서의 실제 관절 각도를 기록했다. 아래는 이동·접근·대기를 모두 포함한 전체 유효 frame의 평균과 표준편차이며, 관절 각도만으로 물체 접촉 적합성을 판정하지 않는다. 원시12관절 위치·속도와6drive 위치는 trace에 보존했다.

| drive 채널 | 평균 실제 각도 | 표준편차 |
| --- | --- | --- |
| 엄지2 | 31.78° | 6.11° |
| 검지1 | 24.45° | 22.57° |
| 중지1 | 23.81° | 24.75° |
| 약지1 | 27.12° | 25.01° |
| 소지1 | 25.69° | 24.29° |
| 엄지1 | 42.04° | 8.17° |

![손가락 거리·normal·Formation timeline](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/figures/05_finger_posture.png)

## 리워드별 의도 판정

| term | 이번 자료로 확인한 의도와 한계 |
| --- | --- |
| sweep_progress | 접촉·정렬을 동반한 거리 감소 보상은 수식과 일치. 방향별 성공과 최종 정착은 별도이며 순간 역방향 힘도 관측. |
| sweep_retreat | 실제 거리 증가량에 대한 비용. 목표 이탈을 막는 hard 조건은 아니며, 진입 후 실패 수와 함께 판단. |
| reaching | EEF 접근 초과 거리의 감소/증가를 부호 있게 보상.10cm 이내 plateau에서는 미세한 최종 자세·성공을 직접 구분하지 않음. |
| arm_action_rate | 팔 action 변화 비용. 작은 변화 선호를 제공하지만 조작 품질·성공을 보장하지 않음. |
| hand_action_rate | 손 action 변화 비용. 손가락 접촉 형상이나 각도 자체의 판정은 Formation과 구분. |
| arm_joint_velocity | 팔 관절 제곱속도 연속 비용은 유지됨. Joint 속도 강제 종료를 재도입한 환경이 아님. |
| hand_joint_velocity | 손 관절 속도 비용. 자세를 유지하는 정적 상태에서는 부담이 작아 지속 Formation과 교환 가능. |
| shelf_collision | 선반 접촉 비용 발생 규모를 확인. 모든 충돌의 물리적 위험도를 단일 합력으로 대체할 수 없음. |
| shelf_failure | 선반 물리 실패 관련 항. 미발동은 안전장치의 경계 성능을 실증한 것이 아님. |
| obstacle_contact | 손–장애물 직접 합력50N 문턱. 물체를 움직이지 말라는 의미를 전부 포괄하지 않음. |
| wrench_change | 손목 F/T 변화 문턱 비용. 위치·보상 계산 검증과 센서의 물리적 충실도 검증을 구분해야 함. |
| object_tilt | 활성 물체의 기울기 비용. 수평 위치 이탈·yaw만의 회전은 장애물 변위와 다른 속성. |
| obstacle_displacement | 지속 제곱 변위 비용 적용 일치. 작은·짧은 이동에 대한 부담과 성공 판정은 별개. |
| arm_action_limit | 실행 제한 전 팔 action 초과 비용. 최종 실행 clip과 별도로 계산됨. |
| hand_action_limit | 정규화 손 action[0,1] 범위 초과 비용. 관절 물리 각도 제한과 구분. |
| contact_formation | 거리×양방향 각도 합산은 정상 적용. 큰 거리에서도 연속 점수·비접촉 지급·지속 지급으로 실제 접촉 자세와 성공의 대리 지표에 한계. |

우선 검토할 것은 손가락 보상을 더 키우는 것보다 **방향별 목표 정착과 Formation의 지급 규모·거리 민감도**다. 순수 자세 보상이라는 목적을 유지하려면 거리 scale·합산 범위·weight를 함께 비교해야 한다. 실제 다지 접촉이 필수라면 그것을 별도 지표/요건으로 정의할 수 있지만, 이번에는 어떤 수치나 지급 조건도 바꾸지 않았다. 같은 초기 상태·같은 학습 예산의 대조 학습 없이는 변경 효과를 확정할 수 없다.

## 검증·센서 한계·재현 자료

| run | Formation raw 최대 오차 | 장애물 step 비용 최대 오차 | 보상 합 최대 오차 |
| --- | --- | --- | --- |
| seed42 | 2.38e-06 | 7.13e-09 | 1.79e-07 |
| seed43 | 2.38e-06 | 3.3e-09 | 1.19e-07 |

성공·TCP 종료는 물리 입력에서 독립 재판정했고, Reach·Sweep 증분·힘 정렬도 대조했다. 형성 점수는 world normal과 거리로 재계산해 EEF frame 구현과 대조했다. 모든 완료 episode의 step 연속성·유한값·초기 위치/mask 불변·checkpoint SHA256·학습 params와7개 Manager 설정 일치를 확인했다. [1]

동일 seed42·64환경·20step을 계측 hook 없는 원본 경로로 다시 실행했다. reward·done·joint/object 위치·모든 observation audit의 최대 차이는0이었다. [계측 동등성](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/hook_parity.json). 이 검사는20step의 동등성이며 전체512episode를 원본으로 별도 재생한 검사는 아니다.

원시 terminal 위치·실패 flag에서512건의 성공과 방향을 별도 재집계하고, 보상 양/음 예산·손가락별 Formation 합계를 대조했다. [독립 재검산](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/validation.json).

시뮬레이터의 이동 접촉 합력 norm 최대는 1645.43N였고, 수집된 raw wrist force 최대는 73.63N·보정 pure force 최대는 82.98N였다. 같은 물리량이 아니므로 최대값 차이만으로 원인을 확정하지 않는다. 앞선 v0_3 평가의 F/T 충실도 문제를 해결한 분석도 아니며, 힘 방향은 제공된 접촉합력 기준의 진단으로 해석한다. 위치·성공·거리/각도 보상 일치는 이 센서 한계와 별개다.

| seed | 성공 | 평균 순보상 | ≥1cm 장애물 이동 |
| --- | --- | --- | --- |
| 42 | 176/256 (68.8%) | 12.549 | 14 |
| 43 | 158/256 (61.7%) | 12.406 | 17 |

각 방향의 구간은 seed·env를 cluster로 resample한 기술통계다. 서로 다른 방향의 초기 손 위치·가림·목표 거리·장애물 구성이 함께 달라질 수 있어 방향 자체의 순수 인과 효과라고 해석하지 않는다. 다른 checkpoint·실물 전이·장기 수렴·부모 대비 개선·센서 불일치 원인 확정은 미검증이다.

[1] [방향별 집계·독립 검사](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/direction_summary.json), [전체 기존 계측 집계](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/summary.json), [episode CSV](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/direction_episodes.csv), [보상 CSV](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/direction_rewards.csv), [손가락 CSV](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/direction_fingers.csv), [필드 사전](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/data_dictionary.json). 각 seed 폴더에 terminal-inclusive `trace.npz`·초기 상태·metadata·설정 YAML·소스 snapshot이 있다.

[2] [거리·각도 자세 구현](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/prof_revision_geometry.py), [Sweep/Reach 상태](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/prof_revision_state.py), [16항 계수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/prof_revision.py), [성공/TCP 종료](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/prof_revision.py).

계측은 `collect_prof_revision_play.py --task Inspire-Sweep-Prof-Revision-v0_3_1 --checkpoint <model_15550.pt> --output-dir <seed별 폴더> --num_envs 64 --episodes 4 --seed 42 또는43 --wrench-diagnostics --headless`로 수행했다. 전체 checkpoint 경로·SHA256와 실행 명령·검사 기록은 [개발 로그](../logs/2026-11-26_prof_revision_v0_3_1_play_analysis.md)를 따른다.
