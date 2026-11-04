# Revision-Test-v2 학습 성공률 저하 진단

2026-11-04. 요청: `logs/TEMP/2026-11-03_19-32-13`에서 5000 iteration 이후 성공률 저하와 shelf 종료 증가가 패널티 회피성 조기 종료 때문인지 분석한다. 분석만 수행했으며 환경·학습 설정은 변경하지 않았다. 기존 임시 print와 사용자 작업트리·학습 로그를 보존했다.

## 자료·방법

- 원본: 해당 run의 TensorBoard event, `params/env.yaml`, `params/agent.yaml`, `git/Contact-Rich-Manipulation.diff`, model checkpoint.
- 기록된 학습 commit: `6183ab3492f037eaaeb847f1ec9a71a996a1c054`. 현재 보상·커리큘럼·agent와 비교했으며 해당 범위 차이는 Test-v1 EEF print 주석 처리뿐이다. Test-v2 계산식 변경은 없다. 당시 외부 라이브러리 전체를 복원한 검증은 아니다.
- 저장 설정: Test-v2, seed42, 2048 env, episode10s, step0.02s, rollout36step, gamma0.98, entropy coefficient0.005, adaptive PPO, action clip 없음. Curriculum runner는 실제로 NumericalPPO를 사용한다.
- iteration 축 scalar는0~17247까지 연속이며 태그별 중복·누락·비유한 값 없음을 검사했다. `/time` 태그는 별도 시간축이므로 제외했다.
- 종료 지표는 현재 Isaac Lab `TerminationManager`의 각 환경 최근 종료 결과 평균이며, 모든 완료 episode를 합산한 사건 비율은 아니다. 아래 %는 TensorBoard 지표의 구간 산술평균이다. 조건이 동시에 발동할 수 있어 종료 항 합은 반드시100%가 아니다.
- `Episode_Reward`는 reset batch의 episode 누적 보상을 실제 길이가 아닌 고정10s로 나눈 값이다. 표의 보상은 이를10배한 로그 환산값이며 전체 episode 개수 가중 평균과는 다를 수 있다. `Train/mean_reward`와 평균 방식이 달라 정확히 일치한다고 가정하지 않는다. 짧은 episode에서는 누적 비용도 줄어드는 점을 고려했다.

재현 가능한 분석 코드와 산출물은 workspace `outputs/revision_training_diagnosis/`에 보존했다.

```bash
conda run --no-capture-output -n env_isaaclab python outputs/revision_training_diagnosis/analyze.py
conda run --no-capture-output -n env_isaaclab python outputs/revision_training_diagnosis/checkpoints.py
conda run --no-capture-output -n env_isaaclab python outputs/revision_training_diagnosis/diagnose.py
```

`scalars.csv`, `audit.json`, `window_means.csv`, `means_100_iterations.csv`, `checkpoint_std.json`, `checkpoint_std_detail.csv`, `reward_changes.csv`, `diagnosis_summary.json`이 계산 근거다. checkpoint는 CPU에서 읽기만 했다. 원본 로그 수정·재학습은 수행하지 않았다.

## 발생 시점: 최초 급변은 약2900

| iteration 구간 | 성공 지표 % | shelf 지표 % | 평균 episode step | 평균 action std | action-rate 보상 환산 | reaching 보상 환산 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2400–2499 | 10.481 | 11.703 | 440.30 | 2.138 | −20.706 | +7.672 |
| 2800–2899 | 9.278 | 22.655 | 403.52 | 2.467 | −22.352 | +7.683 |
| 2900–2999 | 6.387 | 59.963 | 246.18 | 2.716 | −15.286 | +7.658 |
| 3000–3099 | 5.238 | 79.232 | 145.79 | 3.058 | −10.594 | +7.656 |
| 4000–4499 | 9.880 | 74.920 | 135.20 | 3.721 | −10.692 | +7.588 |
| 5000–5499 | 7.196 | 78.802 | 114.52 | 3.796 | −9.459 | +7.568 |
| 6000–6499 | 5.970 | 80.030 | 100.83 | 3.877 | −8.446 | +7.518 |
| 16748–17247 | 1.752 | 86.363 | 53.90 | 4.571 | −4.668 | +7.319 |

성공의100iteration 이동평균 최대는3440~3539의12.338%다. 약2900에서 조기 종료로 큰 전환이 있었고 이후 성공 지표가 일시 회복했다. 따라서5000 이후만 보면 최초 전환을 놓친다. 4000–4499→6000–6499는 성공−3.909pt, shelf+5.110pt, episode135.20→100.83step이다.

## 패널티 일정 가설과 대조

저장env.yaml과 실제Curriculum scalar가 일치한다.

- 물체 가속도·장애물 접촉·wrist wrench 관련7개 schedule은null이다. 5000 시점에 계수·임계값이 강화되지 않는다.
- target free speed는1900에서0.02m/s에 도달한 뒤 고정된다.
- 장애물은10000 미만까지Gray/White=3/3이다. 실제 배치 수도3/3, layout_complete=1이다.
- 방향deadzone만3500:25도,4000:20도,4500:15도,5000:10도,5500:5도,6000:0도로 바뀐다. 목표 방향에서±X축 근처를 제외하는 각도를 줄이는 처리이며 보상 계수 변경이 아니다.

따라서 “5000에서 패널티 커리큘럼이 강화되어 시작됐다”는 가설은 지지되지 않는다. 다만 고정 계수에서도 행동이 변하면 실제 발생 비용은 증가한다.

## 유력한 설명: 초기 접근 보상과 지속 비용의 불균형

`DexReachProgress`는EEF–물체의 최단 거리 갱신량×30을 지급한다. 초기 접근에서 보상을 얻고 reset마다 기준이 새로 설정된다. `ShelfPenalty`는 손목 높이/선반 속도 조건 발동에 일회−3을 지급하고 추가 연속 비용도 갖는다.

`robot_action_rate_penalty`는Arm6D·Hand2D의raw action 차이 제곱합을 각각100으로cap하고0.03×step_dt를 곱해 매step 부과한다. 총 최대 비용은0.12/step이다. 손 실행값은[0,1]로clamp하지만 이 비용은clamp 이전raw값으로 계산한다.

2800–2899에서action-rate 비용 환산−22.352가 큰 음의 항이다. 3000–3099에는episode가403.52→145.79step으로 짧아져 비용이−10.594까지 감소하는 반면reaching은+7.683→+7.656으로 유지된다. 같은 두 구간의Train mean reward도1.566→6.761로 회복한다. 이는 “성공률을 낮춰도 지속 비용을 회피하는 조기 종료가 보상 목적상 유리해졌다”는 가설과 일치한다. 단, 종료 종류별episode return을 직접 비교한 인과 증명은 아니다.

4000–4499→6000–6499의 보상 환산 차이는Hold−3.836, timeout bonus−2.944, goal distance−1.387에 비해action-rate 비용 감소+2.246이다. shelf 비용 악화는−0.136에 그친다. 후반 보상 저하는 새 패널티 급증보다 성공 관련 보상의 소실이 주도한다. 이 분해는 수치상 기여이며Hold 소실이 근본 원인이라는 뜻은 아니다.

앞선model17200 직접play의12개 완료episode 중shelf9건은 모두손목clearance<30mm였다. 말기 정책에 실제 조기 종료 행동이 존재한다는 보조 근거다. 단일env·평균 행동play이므로 학습2048env 전체 및2900 당시 종료 세부 원인까지 같다고 단정하지 않는다.

## 행동 분포·할인율

checkpoint의 학습 가능한Gaussian std를 직접 읽었다. 5000에서는XYZ=(3.9790,0.009093,6.0304), RPY=(4.0933,4.3218,5.7973), Hand=(3.3735,2.6012)다. Y는4000의1.8396에서4500=0.1976,4750=0.0243,5000=0.0091로 축소됐고, Z는5.5663→6.0304로 커졌다. 평균std만으로는 축별 편중을 볼 수 없다.

위치command scale0.03m를 적용하면5000의Z std6.03은약0.181m의 목표 위치 증분 노이즈다. 실제1step에18cm 움직였다는 의미가 아니다. Arm command는clip하지 않으며 하위 제어에서는 토크를 제한한다. 학습은Gaussian sample, 일반play는mean을 사용하므로 둘의 성능을 동일시하지 않는다.

고정entropy coefficient0.005와std 상한 없음은 큰 분산을 허용하며raw action-rate 비용·실패 위험을 키울 수 있다. 비용cap 이후에는 극단적 행동의 추가 비용이 더 커지지 않는다. 다만Y 분산은 줄어들었고 학습 gradient를 재현하지 않았으므로entropy만을 단독 원인으로 확정할 수 없다.

gamma0.98은step0.02s에서 유효 할인 시간약1초다. 500step 마지막의timeout bonus75가 시작 시점에 기여하는 직접 할인값은 `75 * 0.98**499 = 0.00314`, 잔여450step이면0.00845다. 초기 접근 보상과 가까운 미래의 연속 비용에 비해10초 후 성공bonus의 영향이 약하다. Critic bootstrap 및 중간Hold 보상도 있으므로 성공 학습 신호가 완전히 없다는 뜻은 아니다.

## 판단·후속 검증

가장 지지되는 설명은 큰raw action 변화 비용, 초기reaching 보상, 상대적으로 작은 일회shelf 실패 비용이 결합하여 성공 추구보다 조기 종료로 편향된 정책이 형성됐다는 것이다. 행동 분포 편중과 목표 방향 난도 변화가 후반 악화를 가속했을 수 있다. 5000의패널티 계수 증가설은 부정되며, 최초 큰 전환은방향schedule 시작3500보다 이른약2900이다.

인과관계 분리를 위한 후속 실험 제안이며 이번에 실행·수정하지 않았다.

1. 전환 전checkpoint2500에서 같은seed·목표 분포 대조군을 두고std 상한 또는entropy 감소를 한 번에 하나씩 적용한다. stochastic/mean 평가를 분리한다.
2. action-rate 비용만 바꾼 대조군에서shelf 종료·episode 길이·성공·실제action 차이를 비교한다. shelf 일회 비용만 크게 만들면 다른 실패 조건으로 이동할 가능성도 있어 종료 전체를 본다.
3. reaching과실패 비용의 균형, gamma와성공 보상 시점을 별도 실험으로 비교한다. 물리 안전 종료 조건부터 완화하지 않는다.
4. 방향deadzone 고정 대조군으로3500 이후 추가 저하를 분리한다.

단일run의 상관·코드상 기전·checkpoint 파라미터에 근거한 진단이다. 원인별 인과 기여율은 미확정이며joint episode 기록 부재로 성공/실패별return 분포·전체episode 가중 성공률은 복원할 수 없다. 원본 학습 로그에shelf의세부 분기별 기록도 없다.

## 검증

분석3개 스크립트 실행, 연속iteration·유한값·중복 없음, 보상 변화 합 및checkpoint std를 확인했다. 원본을 변경하지 않고CSV/JSON을 보존했다. 보조 그래프의 수치는500iteration 집계와 대조했다. 프리뷰HTML 생성은 성공했지만 브라우저의file URL 접근이 정책상 거부되어 실제 브라우저 표시 검증은 미실시이며 우회하지 않았다. 판단 근거는 보존한CSV/JSON과 위 수치다. 개발 로그Markdown·diff 검사를 수행했다.
