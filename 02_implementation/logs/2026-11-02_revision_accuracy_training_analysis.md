# Revision v0 / GoalAccuracy v0_2 저장 로그 분석

## 요청·범위

- 요청: 두 학습 로그의 성공률·XY 거리 차이, 정밀 위치 실패, 보상 우회 가능성, 커리큘럼 영향을 분석한다.
- 입력: `logs/TEMP/2026-11-01_19-14-32`, `logs/rsl_rl/inspire_final_goal_accuracy_v0_2/2026-10-30_16-53-03`.
- `play`, simulator, rollout, 학습 및 GPU 실행 없이 TensorBoard scalar, 저장 YAML, Git snapshot, CPU checkpoint 읽기만 수행했다.
- 코드·환경·보상·학습 로그 변경 없음. 분석 문서 및 `outputs/log_analysis_2026-11-02`의 집계·그림만 추가했다. 기존 사용자 변경과 submodule commit을 보존했다.
- 분석 cutoff: Revision iteration 11740, Accuracy 25627. 진행 중인 원본의 이후 기록은 분석에 포함하지 않는다.
- Revision snapshot commit `408d3d9ce947a62f094d6f8c8693be2c07e2e32d`; Accuracy `eaf1e5dc2fb0a8d3e75374110c65d93e65c7c71a`. 현재 HEAD는 Revision snapshot과 같다. 두 snapshot의 IsaacLab gitlink는 모두 `929f0fe1e9c1699efebf31b2ad0ab723a7d6e7e9`다.
- Accuracy 당시 YAML을 우선했다. 현재 v0_2_1 이상 계약을 소급 적용하지 않았다. 현재 `final.py`의 해당 보상 함수는 당시 snapshot과 같고 이후 추가된 contact-only 함수를 v0_2에 적용하지 않았다.

## 지표 해석과 비교 제한

- `Episode_Termination/target_goal_success_at_timeout`: 10초 timeout 순간 XY 반경 이내. Accuracy 2cm, Revision 3cm. 속도나 연속 hold 시간 조건은 없다.
- 로컬 IsaacLab TerminationManager는 2048 환경 각각의 마지막 종료 원인을 저장한 배열의 평균을 기록한다. 따라서 이것은 모든 종료 에피소드를 누적한 정확한 성공 횟수/시도 횟수가 아니다. 아래 성공률은 기록된 성공 지표의 iteration 산술평균이다. 여러 종료 원인은 동시에 참일 수 있다.
- `Metrics/target_goal_distance_xy_mean`: 종료된 에피소드의 전체 스텝 평균 거리. 최종 오차·최소 오차·실패 에피소드만의 거리가 아니다. reset batch 평균을 runner가 다시 평균하므로 개별 에피소드 가중 평균과도 다를 수 있다.
- `Episode_Reward/*`: 에피소드 누적 기여를 최대 에피소드 시간 10초로 나눈 값이다. 아래 값에 10을 곱하면 같은 집계 방식의 에피소드 보상 기여가 된다. `Train/mean_reward`와는 averaging window/weighting이 다르다.
- 두 run 모두 2048 env × 36 step/iteration, dt=0.02초, seed=42. 그러나 형상·배치·관측·보상·성공 반경이 동시에 달라 동일 seed의 통제 실험은 아니다.

## 핵심 수치

| 구간 | Revision 성공 지표 | Accuracy 성공 지표 | Revision 평균 XY | Accuracy 평균 XY |
| --- | ---: | ---: | ---: | ---: |
| 2000–2999 | 20.99% | 10.00% | 16.36cm | 11.97cm |
| 4000–4999 | 17.79% | 27.11% | 15.78cm | 7.96cm |
| 6000–7999 | 12.83% | 30.29% | 15.77cm | 7.34cm |
| 10741–11740 (공통 학습량) | 14.84% | 26.93% | 15.47cm | 7.72cm |
| 각 run 마지막 1000 iteration | 14.84% | 20.62% | 15.47cm | 8.53cm |

Accuracy는 30%를 넘지 못한 것이 아니다. 최고 1000-iteration 구간 7570–8569는 **31.30%**, 단일 iteration 최고는 37.27%였다. Revision 최고 1000-iteration 구간 1628–2627은 21.18%였다. Accuracy의 핵심 현상은 30% 부근 정체 이후의 퇴행이다.

Accuracy가 더 오래 학습한 것만으로 차이를 설명할 수 없다. 공통 구간에서도 격차가 있다. 반대로 초기 2000–2999 성공률은 Revision이 더 높았으므로 항상 Accuracy가 우세했던 것도 아니다.

## 1. Accuracy의 우세를 설명하는 구조 차이

확인된 차이이며, 각 요소의 인과 기여량은 현재 두 run만으로 분리할 수 없다.

1. **타겟 분포**: Accuracy는 cylinder/cube/random 범주에 각각 1/3 생성 확률을 준다. random은 YCB 단계 크기 및 mug/bottle 후보다. Revision은 8종을 균등 추출하여 cylinder+cube 확률이 1/4이다. 크기 기준, 스케일 적용, target yaw와 배치 알고리즘도 바뀐다. 정형 타겟 비중이 높은 Accuracy가 더 쉬울 가능성이 있다. 종류별 성능 로그가 없어 이를 성공률 원인으로 확정하지 않는다.
2. **접촉 보상의 성공 후 조건**: Accuracy는 실제 접촉 OR 유효한 목표 점유에 1.45/s를 준다. Revision은 실제 접촉 AND EEF 높이 120mm 미만만 보상한다. Accuracy는 성공 후 손을 떼도 contact 항을 유지할 수 있고, Revision은 그 항을 잃는다. Revision에는 목표 밖 접촉을 유지하는 유인이 남으며, 목표 안에서 재접촉하면 정밀 위치를 깨뜨릴 가능성이 있다.
3. **Hold 범위**: Accuracy 2–6cm, Revision 3–8cm의 외곽 tail. Revision은 성공 영역을 넓혔지만 목표 밖에 머무는 보상도 커졌다. 4cm 정지 시 distance+hold가 Accuracy 2.6625/s, Revision 4.2225/s이다. 접촉 보상이 참이면 각각 1.45/s가 더해진다.
4. **관측·학습 차이**: Revision은 실제 arm joint 값과 실시간 critic obstacle encoder를 사용한다. Accuracy와 입력 분포 및 critic 정보가 다르므로 보상만 바뀐 실험이 아니다. 개선 의도로 추가한 정보가 이번 run의 성능 향상을 보장하지는 않는다.
5. **배치**: Revision은 고정 65mm padding의 OBB 배치, Accuracy는 별도 source layout과 padding-fraction schedule이다. `0.15`는 15cm가 아니라 분율이다. 각 숫자를 직접 빼서 난이도를 비교하면 안 된다. 마지막 실제 장애물 수는 각각 약 4/5, 3.97/4.96으로 단순 개수 부족은 큰 차이가 아니다.

## 2. 정밀 성공의 공통 병목 후보

### 현재 타겟을 추적할 Actor 정보와 기억

두 Actor는 noisy initial target position, initial goal, 현재 robot/EEF, tactile/wrench, 이전 action을 받는다. 현재 타겟 좌표는 critic용이다. `history_length=0`, MLP 모델이므로 명시적인 관측 이력이나 recurrent memory가 없다. 이전 action을 통해 간접적으로 상태가 전달될 수는 있으나, 현재 타겟의 미끄러짐·회전·접촉 상실을 추정하는 전용 기억은 없다.

이 설계는 초기 시각 이후 촉각/F/T 연구 조건에 부합한다. 하지만 형상·크기·접촉면이 달라지면 같은 손 위치와 현재 센서값이 서로 다른 타겟 오차를 뜻할 수 있다. 특히 접촉이 끊겼을 때 재접근 방향을 정하기 어렵다. 현재 GT를 Actor에 넣는 변경을 기본 해법으로 제안하지 않는다. 조건을 유지하는 history/recurrent state-estimation ablation이 적절하다.

### 탐색 잡음과 정밀 제어의 스케일

두 run은 `position_scale=0.03`, `orientation_scale=0.15`, Gaussian learned std, `entropy_coef=0.005`, action clip 없음이다. CPU checkpoint에서 첫 세 action std에 position scale을 곱한 결과:

| 체크포인트 | XYZ raw std | 위치 명령 std (축별) |
| --- | --- | --- |
| Revision 11650 | 1.0174 / 0.9646 / 1.0056 | 3.05 / 2.89 / 3.02cm |
| Accuracy 7000 | 1.3042 / 0.8221 / 0.8732 | 3.91 / 2.47 / 2.62cm |
| Accuracy 25550 | 1.5859 / 1.5409 / 1.4923 | 4.76 / 4.62 / 4.48cm |

これは **OSC 목표 명령의 분산이며 실제 EEF/물체 이동량이 아니다**. 동역학과 제어기가 필터링한다. 그러나 목표 2–3cm와 비슷하거나 더 큰 명령 잡음은 정착을 깨뜨리는 강한 후보다. 학습 scalar는 stochastic policy 성능이며 deterministic play 성능과 동일하지 않다.

Accuracy의 평균 action std는 6000–7999의 1.1226에서 마지막 1000의 1.5202로 증가했다. action-rate penalty는 -0.9474에서 -1.4250, hold는 2.5720에서 1.8029로 나빠졌다. 학습률은 후기 1e-5에 머문다. 일부 회전축 std는 0.0116까지 작아져 전체 entropy가 감소하면서도 위치 잡음은 커지는 상황이다. 평균 entropy 하나만으로 탐색이 충분히 줄었다고 판단하면 안 된다. 상관관계이며 entropy 계수나 학습률이 단독 원인임을 증명하지는 않는다.

### 종료 보상의 짧은 할인 시야

gamma=0.98은 20ms마다 적용된다. 할인 시간 척도는 약 1초이고, 10초 전체의 성공 보상에 긴 시야를 주는 설정은 아니다. 성공 +30의 직접 할인값은 1초 전 10.93, 3초 전 1.45, 5초 전 0.192다. Critic bootstrap이 미래 보상을 전달하지만 할인 자체를 없애지는 않는다.

따라서 즉시 받는 contact/outer-hold와 나중에 받는 timeout bonus 사이의 시간 불균형이 있다. 무조건 bonus만 크게 만드는 것보다, 매 step의 근접·정착 목표와 장기 성공을 일치시키는 실험이 필요하다.

## 3. 보상 우회인가?

**목표 밖에서도 접촉·근접·정지로 양의 보상을 얻는 구조는 확실하지만, 이번 정책이 의도적으로 그 전략을 사용했다고 확정할 trajectory는 없다.**

- Revision의 4cm 정지+유효 접촉은 약 5.6725/s이다. 성공 반경 3cm 밖이어도 보상을 얻는다.
- 하지만 정확한 중심 정지는 distance+hold만 19.7/s로 더 높다. 보상식이 “정확히 맞추면 손해”가 되도록 뒤집힌 것은 아니다. 부분 관측·잡음·교정 비용 때문에 실제로 도달 가능한 행동 중 안전한 차선책이 고착될 가능성이다.
- 목표 밖에서 속도 0.05m/s로 교정할 때 hold speed factor는 0.5가 된다. Revision 4cm에서는 distance+hold가 정지 4.2225/s에서 2.9425/s로 일시 감소한다. 반면 명시적 speed penalty는 free_speed=0.02일 때 약 -0.1546/s라서, 속도 제약의 영향은 별도 speed penalty 숫자만으로 평가하면 안 된다.
- reaching은 new-best 거리 개선량 보상이다. 후퇴 후 같은 지점으로 재접근하는 진동으로 반복 수확하는 항이 아니다.
- ObjectPenalty의 displacement 부분은 non-target만 대상으로 한다. 타겟을 목표로 이동시킨 거리 자체를 벌하는 오류는 확인되지 않았다. 타겟 tilt는 벌한다. 가속도 weight의 음수 부호도 최종 reward에서 비용이 되는 구조다.

마지막 1000 iteration의 기여 (에피소드 보상/10초):

| 항 | Revision | Accuracy |
| --- | ---: | ---: |
| reaching | 0.7727 | 0.7580 |
| goal distance | 0.6492 | 1.2026 |
| goal hold | 1.3172 | 1.8029 |
| contact | 0.6309 | 0.3887 |
| timeout bonus | 0.4437 | 0.6022 |
| action rate | -0.9197 | -1.4250 |
| joint velocity | -0.1457 | -0.1975 |
| object | -0.6471 | -0.5450 |
| target speed | -0.0651 | -0.0982 |
| obstacle contact | -0.00055 | -0.00172 |
| wrench change | -0.00127 | -0.00044 |

평균에서 큰 비용은 action-rate/object이고 wrench/obstacle-contact는 매우 작다. 희귀한 실패에 미치는 영향은 평균만으로 배제할 수 없지만, 평균 보상을 지배하는 항이라는 설명은 지지되지 않는다. Revision contact는 높고 goal reward는 낮은 패턴이지만, contact 보상이 목표 밖에서 발생했는지는 분리 기록이 없어 확인할 수 없다.

또한 Revision 전체 평균 XY가 15.47cm라는 것은 “모든 에피소드가 근처까지 갔는데 마지막 1cm만 실패”한다는 해석과 맞지 않는다. 초기 목표 이동은 최대 15cm다. 오래 접근하지 못한 경우, 반대 방향 이동, 후반 도달, 일부 성공이 섞일 수 있으므로 종료 거리 히스토그램이 필요하다.

## 4. 커리큘럼 영향

- 두 run 모두 target free speed가 0.10에서 0.02m/s로 초반에 축소되고, 장애물은 White 2000/3000/4000/5000, Gray 2500/3500/4500에서 늘어 4/5가 된다.
- goal direction exclusion은 3500부터 5도씩 줄어 6000에 0도다. object acceleration 및 wrench/obstacle 비용도 동시에 강화된다. 성공률 기준이 아니라 iteration 기준이다.
- Revision은 2000–2999 성공 20.99% → 5000–5999 13.74%로 하락했다. object-fall/tilt 지표도 약 10.17% → 21.97%로 증가했다. 이 구간의 장면 난이도 상승과 성능 악화는 일치한다. 여러 일정이 겹쳐 어떤 일정의 인과 효과인지는 분리할 수 없다.
- 이후 Revision 마지막 1000에서 fall/tilt는 6.79%로 회복했으나 성공 14.84%, miss 76.35%다. 현재 주된 실패는 즉각적 파괴보다 timeout miss 쪽이다. 이 비율은 위에서 설명한 last-episode 지표다.
- Accuracy는 동일 개수 일정 중에도 30%까지 개선했다. 더 중요하게 모든 일정이 고정된 12000 이후에도 12000–14999 25.24% → 마지막 1000 20.62%로 계속 나빠졌다. **계속 난도가 증가하기 때문이라는 설명만으로 후기 퇴행을 설명할 수 없다.**
- Revision layout-complete 평균은 99.52%, 실제 장애물은 거의 4/5다. 배치 실패로 대다수 학습이 잘못됐다는 증거는 없다. 기하적 배치 완료가 제어 가능성을 보증하지는 않는다.

## 다음 실험 우선순위 (실행하지 않음)

1. 현재 run을 평가할 때 latest 하나만 쓰지 말고 peak 구간을 별도로 보존·비교한다. Accuracy 7570–8569의 로그 우세는 해당 checkpoint의 deterministic 우세를 보증하지 않으므로 평가 때 확인한다.
2. 정밀 단계의 exploration을 먼저 독립 변수로 시험한다: entropy decay, position/orientation별 std 관리, coarse/fine action scale 중 하나씩. 잡음을 줄였다는 이유만으로 초기 탐색까지 제거하지 않는다.
3. 연구 관측 조건을 유지한 tactile/wrench/action history 또는 recurrent state estimation을 시험한다. 별도의 관측 진단 없이 현재 target GT를 Actor에 추가하지 않는다.
4. 다음 보상 ablation에서는 contact의 목표 밖 보상과 목표 안 손 떼기 유인, 넓은 outer hold와 교정 중 speed attenuation을 분리한다. 목표 개선량 보상/외곽 tail 축소/성공 점유 보상은 후보이지 이번 분석에서 검증된 수정안은 아니다.
5. curriculum을 성능 기준으로 천천히 승급하거나 한 요소씩 변경하는 비교를 한다. 할인율 변경은 값 함수/return scale까지 바꾸므로 별도 실험으로 둔다.
6. 추가 telemetry: terminal XY 및 최소 XY 히스토그램, goal 진입 후 이탈률, goal 밖 contact와 안쪽 contact, 타겟 종류/크기/목표방향별 성공, 실패 에피소드 보상 분해, action 축별 std. 기존 로그에는 없어 소급 계산할 수 없다.

## 산출물·검증·미검증

- 집계: `outputs/log_analysis_2026-11-02/summary.json`, `metrics_250_iteration.csv`.
- 시각화: `outputs/log_analysis_2026-11-02/training_comparison.png`, `.svg`.
- 출처/고정 cutoff/YAML SHA256: `outputs/log_analysis_2026-11-02/source_manifest.json`.
- TensorBoard 모든 iteration scalar를 reservoir sampling 없이 읽었다. `/time` series를 제외한 iteration 중복 없음, 수치 finite를 확인했다. 구간 평균은 단일 run의 iteration 산술평균이며 독립 trial 통계나 인과 추정이 아니다.
- checkpoint는 `CUDA_VISIBLE_DEVICES=''`, `map_location='cpu'`로 2500/7000 및 각각 11650/25550을 읽었다. 모델 forward와 simulator는 실행하지 않았다.
- 미검증: deterministic 정책 성공률, 종료 오차 분포, 특정 형상별 실패, goal 진입·이탈, contact harvesting trajectory, 각 변경의 인과 효과, 물리 rollout 및 수정 후 성능. 사용자의 play 금지를 유지한다.
- 변경 전후 대조: 실행 코드와 설정은 그대로이며 기록/집계/그림만 새로 추가했다. 개발 로그 외 기존 문서와 사용자 변경은 수정하지 않았다.
- 문서 검증: Markdown math 검사 통과, 문서 저장소 링크 검사 errors=0, `git diff --check` 통과. PNG를 직접 열어 네 패널의 축·범례·시계열 렌더링을 확인했다. Markdown 자체의 별도 렌더링은 수행하지 않았다.

## 후속 질문: 총보상 피크 이후 하락의 항별 분해

사용자는 두 run의 공통적인 피크 후 하락을 어떤 reward/penalty가 만드는지 질문했다. 이전에 추출한 동일 cutoff의 scalar를 사용했다. 새 학습·play·GPU 실행 및 코드 변경은 없다. 성공률 피크가 아니라 `Train/mean_reward`의 최고 1000-iteration 이동평균을 기준으로 삼았다.

- Revision 피크: 1558–2557, Train mean reward 34.3588. 바로 다음 2558–3557은 31.6332, 마지막 10741–11740은 19.6336.
- Accuracy 피크: 7569–8568, Train mean reward 47.0071. 바로 다음 8569–9568은 42.2625, 마지막 24628–25627은 24.3380.
- 아래는 `Episode_Reward`에 10초를 곱한 항별 에피소드 기여다. runner 집계가 달라 그 합은 Train mean reward와 정확히 같지 않다. 하락 기여율은 항별 합을 분모로 사용한다.

| 항 | Revision 피크 → 마지막 | 변화 | Accuracy 피크 → 마지막 | 변화 |
| --- | ---: | ---: | ---: | ---: |
| goal hold | 19.9774 → 13.1724 | -6.8049 | 26.8700 → 18.0290 | -8.8410 |
| goal distance | 8.3167 → 6.4915 | -1.8252 | 14.7296 → 12.0264 | -2.7032 |
| timeout bonus | 6.2629 → 4.4373 | -1.8256 | 9.1136 → 6.0225 | -3.0911 |
| action rate penalty | -7.7807 → -9.1972 | -1.4165 | -9.5782 → -14.2495 | -4.6713 |
| object penalty | -3.7361 → -6.4707 | -2.7346 | -4.3301 → -5.4495 | -1.1194 |
| contact | 5.9718 → 6.3092 | +0.3374 | 5.7578 → 3.8873 | -1.8705 |
| target speed penalty | -0.7978 → -0.6506 | +0.1472 | -1.0505 → -0.9820 | +0.0685 |
| 전 항 합계 | 34.2432 → 19.7694 | -14.4738 | 46.7287 → 24.3887 | -22.3400 |

### 피크 직후의 차이

- Revision의 바로 다음 1000 iteration에서는 hold가 19.9774 → 20.1460으로 소폭 개선된다. object penalty는 -3.7361 → -5.9258로 악화되어 전체 항 합계 하락 2.8540 중 약 76.7%를 설명한다. 따라서 Revision 하락의 시작을 hold 붕괴로 설명하면 틀린다.
- 이때 평균 요청 장애물 수는 Gray 1.058 → 2.058, White 1.558 → 2.558이다. object penalty는 활성 물체별 기울기, 비타겟 변위, 가속도 비용을 합산하고 물체 수로 나누지 않는다. 장애물 증가가 비용을 올릴 수 있는 구조다. 가속도 비용도 3000 이후 활성화되지만 하나의 aggregate 로그만으로 세 하위 비용을 분리할 수는 없다.
- Accuracy의 다음 구간은 hold -1.5404, action rate -1.1258, timeout -0.6954가 주요 하락분이다. 이때 장애물 수는 이미 Gray4/White5로 고정이다. padding 및 가속도 관련 일정은 아직 바뀌므로 완전 고정 환경 비교는 아니다.

### 공통 구조와 인과 해석

- 피크→마지막 총 하락에서 hold 감소가 가장 크다(Revision 약 47%, Accuracy 약 40%). distance+hold+timeout 감소를 합하면 각각 약 72%, 66%다. 이는 목표 수행 악화가 총보상 감소에 드러나는 것이며, hold 항 자체가 정책 퇴행을 유발했다는 인과 증명은 아니다.
- action-rate 항의 weight나 내부 0.03 계수는 커리큘럼으로 강화되지 않는다. 악화는 raw action 차이 제곱합이 커진 결과다. Gaussian sampling의 축별 분산이 커지면 연속 action 차이 비용이 커질 수 있다. 조건부 평균과 시계열 상관도 영향을 주므로 std만으로 비용 전체를 재구성하지 않는다.
- PPO에는 환경 reward와 별개로 고정 entropy coefficient 0.005가 있다. 이는 확률분포를 넓게 유지하는 유인이고, 환경 reward의 action-rate/settling과 긴장 관계가 있다. 정확한 보상의 피크 후 퇴행을 수학적으로 강제하는 항은 아니며, entropy가 단독 원인이라는 결론에는 ablation이 필요하다.
- hold는 목표 밖에서도 정지 보상을 주고, 속도 0.05m/s에서 해당 hold 보상을 절반으로 줄인다. contact는 진척 없이도 지급될 수 있고, timeout bonus는 gamma=0.98로 먼 시점에서 할인된다. 이 조합은 교정 대신 접촉·정지에 머무는 차선책을 허용한다. 두 run의 contact 추이는 반대이므로 contact 수확 증가를 공통 하락 원인으로 단정하지 않는다.
- 명시적 target-speed penalty는 두 run 모두 마지막에 덜 부정적이다. wrench/obstacle-contact의 전체 하락 기여는 각각 합쳐 0.018 미만, 0.013 미만으로 매우 작다. 이들이 평균 총보상 하락을 주도한다는 설명은 맞지 않는다.
- 후속 분석 자료: `outputs/log_analysis_2026-11-02/reward_peak_decomposition.csv`. 전체 항별 값·피크 다음 구간·최종 구간과 차이를 저장했다. 원본 로그는 보존했다.
