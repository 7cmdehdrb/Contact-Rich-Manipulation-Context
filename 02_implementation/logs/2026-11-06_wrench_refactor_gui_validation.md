# Wrench Refactor GUI 리셋·직선 밀기 검증

[환경 명세](../environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [재구성 소스](../environments/WRENCH_REFACTOR_V0_RECONSTRUCTION.md)

## 요청과 범위

2026-11-05부터11-06까지 실제 `Inspire-Wrench-Refactor-v0`를32환경,GUI로 검사했다. RL 학습 없이 같은 OSC·관측·보상·종료 함수를 사용했다. 왼쪽(world−Y)은 손바닥, 오른쪽(+Y)은 손등이며 두 방향의 명목 손 자세는 같다. 타겟은 선반 중앙, 목표는±Y12cm, 활성 장애물0개다. 총17개 물체 중16개는 중력을 끈 주차 상태다. 물성·크기는 seed42의 startup 랜덤값을 유지했다.

기준 workspace HEAD는 `c57087aa629ec0d7205a37f44dc3a595ea7974ec`이며 작업트리는 기존 사용자 변경과 이전 Refactor 구현이 있는 dirty 상태다. 커밋·학습·학습 로그 변경은 하지 않았다. 모든 결과는 workspace의 `outputs/wrench_refactor_validation/` 아래다.

## 실행 환경과 이전 판단 정정

실제 호스트는 RTX3090 24GB, driver560.35.03,CUDA12.6이며 DISPLAY=:1에서 Isaac Sim5.1/Isaac Lab0.54.4가 동작한다. 초기 도구 sandbox에서는 NVIDIA device 접근이 차단되어 GPU 부재로 오판했다. 허용된 장치 접근으로 실제 GUI 실행에 성공했다. 따라서 이전 로그의 “호스트 NVIDIA driver 부재”는 이 기록으로 정정한다. 다른 사용자의 기존 Isaac 프로세스는 중단하지 않았다.

## 재현된 결함과 수정

| 항목 | 변경 전 | 변경 후·검증 |
| --- | --- | --- |
| startup event signature | `env_ids=None` 때문에 EventManager가 인자 목록 검사에서 초기화 실패 | `initialize_geometry/physics`의 `env_ids`를 필수 인자로 변경. 실제GUI32환경 생성 및 CPU 회귀 통과 |
| 주차 물체 중력 | CPU readback은disable1인데 일부 물체가100ms에53.96mm 낙하, 속도−.981m/s | Refactor 전용 helper에서 flag를 바꾼 전체 row를wake_up.7168배치에서 최대drift3.82µm |
| Arm 속도 종료 | 1rad/s | 사용자 후속 지시로3rad/s. actuator 물리 한도는 기존2/4rad/s 유지 |
| 초기 Wrist3 | .785rad | 사용자 후속 지시로−π/2. 실측 palm normal≈(.000798,−.9999998,.000472). 나머지5축 고정,IK/random reset 없음 |
| 문서 EEF 회전 | identity로 오기 | 실제 quaternion(.5,−.5,−.5,−.5)로 수정. safety frame 부착 body도 실제 `inspire_base_link`로 정정 |

기존 Wrench 공통 함수는 수정하지 않았다. 새 이벤트 signature 회귀와 부분reset gravity 행·wake 대상 검사를 추가했다. CPU 기존 Wrench/촉각 및 Refactor 총160개 통과. live robot의 전체 hand mass .790kg, shelf mass30kg도 첫GPU probe에서 확인했다.

## 테스트1: 리셋·방위

`reset_final/reset.json`:32환경×32reset×7deadzone stage=7168배치. 최초 바닥정렬 최대오차0m. 일부 reset마다 첫5정책step(100ms)을 관찰하여 최대 바닥높이 오차.000243187m, 단일step 활성Z변화.000027180m, 주차물체 이동.000003815m를 기록했다. 바닥1.03m 미만 사례0. 질량·마찰·geometry buffer는 전reset에서 불변이었다. reset 중앙값.06979초, 최댓값.45822초이며32환경 일괄값이다.2048환경 성능으로 외삽하지 않는다.

실제goal방위는30/25/20/15/10/5/0° 각stage1024개씩 기록했다. 허용각을 연결한 구간에서24bin 카이제곱·KS·좌우 binomial검사를 수행했다. 금지방위0개, 카이제곱p는.2297~.8526, 좌우−Y 비율은.4746~.5049였다. 표본의 무작위 변동이 있으므로 정확히50%를 요구하지 않는다.

독립적으로 production goal sampler를 stage당200000개,총1400000개 추출했다. 모든stage 금지구간0개,−Y 비율49.8705~50.2025%.21검사 Bonferroni 보정 기준(.001/21)에서 편향 검출 없음. 이 검사는 목표 샘플러의 방위 분포에 관한 것이며, 접촉 물리·제어 난이도 때문에 학습이 한쪽으로 편향되는 가능성까지 배제하지 않는다.

## 테스트2: 시험 조건과 실패 이력

환경의 기본episode10초와 별도로, 시험은 접근·직선밀기·안정유지 관찰을 위해40초로 설정한다. 자동reset 없이 실제 production termination/reward를 매step 계산한다. 최초종료step까지의 `preterminal` mask만 유효 에피소드 보상으로 합산한다. 성공 이후 장면을 유지하며 계산한 반복success 값은 보상 검증 합산에서 제외한다. 실패(낙하·선반·관절속도)는 현재 시험 코드에서 즉시 정지한다.

- `push_audit`: 매우 작은 명령 제한 때문에 접근하지 못했다. 접촉 검증에 사용할 수 없다.
- `push_audit_v2`: EEF1.40m 경유점과 손의 추가 상단12cm를 고려하지 않아 상단 선반 접촉. 접근 중23/32관절속도 실패. 사용자 관찰과 일치하며 정상밀기 결과에서 제외한다.
- `push_audit_v3`: 기본 Isaac OSC의axis-angle만 보고 로컬 RPY wrapper를 놓친 임시 변경으로 시작했다가 중단했다. 기존RPY입력이 맞으므로 복구했다. 이 과정의 잘못된 중간 설명도 정정한다.
- `push_audit_v4`:25cm 후퇴 후 베이스 근처에서 옆 정렬할 때 EEF가.94m로 내려가고4rad/s 초과. 유효한 경로가 아니므로 폐기했다. 특이점 부근·충돌의 정확한 기여는 이 실행만으로 확정하지 않는다.
- `push_audit_v5`:새 Wrist3 초기각,후퇴 제거,EEF1.13m 수평접근.32환경 모두 실패 없이 밀었지만 일부 목표미도달/안정유지부족. 왼쪽 손바닥ch0,오른쪽 손등ch17 활성 확인.
- `push_audit_v6`:직선 이동14.5cm,hold6초. 실패0,성공19/32. 왼쪽 접촉 자세 약7° 오차와X방향 약3cm drift로 전체성공은 아님. 명령 좌표와OSC 내부목표의 최대world차이.95µm로 좌표변환을 직접 검증했다.

최종 시험 결과는 후속 절에 기록한다. v6의 거리/hold/contact/관절속도 보상은 원시 신호로 독립 재계산했으며 최대오차는 각각2.24e−8/7.16e−8/1.09e−9/2.33e−10이다. 시작history(Hand 이전action=1,Reach resetbest)를0으로 가정하면 첫step 비교가 틀리므로 분석기가 실제reset 상태를 읽거나 첫step 미확인 범위를 분리한다.

## 실행 명령

Isaac Lab Python은 `/home/min/miniconda3/envs/env_isaaclab/bin/python`을 사용했다. 아래 명령은 workspace 루트에서 실행하고 `--headless`를 붙이지 않는다. 분석용 SciPy/Matplotlib도 필요하다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python -u src/inspire_sweep_baseline/tests/_wrench_refactor_behavior_probe.py --mode reset --device cuda:0 --output outputs/wrench_refactor_validation/reset_final
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python -u src/inspire_sweep_baseline/tests/_wrench_refactor_behavior_probe.py --mode push --device cuda:0 --output outputs/wrench_refactor_validation/push_final
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/analyze_wrench_refactor_behavior.py outputs/wrench_refactor_validation/push_final
```

`push_trace.npz`는policy50Hz의모든32환경과13보상항,5종료항,EEF/물체pose·velocity,action/torque,34촉각원시bit/실제policy관측,6축보정F/T/실제policy관측,목표접촉력,손바닥법선,손mesh높이bounds,Jacobian최소singular value를 포함한다. 시간단위초,위치m,힘N,모멘트Nm다. `channels.json`이보상/종료이름과시험설정,`summary.json`이방향별phase평균및검사,`signals.png`가시계열이다.

## 최종 밀기 결과: push_audit_v7

두 방향 모두 같은 명목 palm-left 자세다. production OSC gain/보상/센서는 변경하지 않고 시험 제어에만 world 회전오차의 적분(gain1/s, norm상한.20rad)을 추가했다. EEF 증분은 최대.03m,회전 증분은 최대.25rad이며 production RPY 입력 형식을 유지한다. 이는 접촉 하중에 따른 자세 오차를 줄이는 룰 기반 외부 루프다. 손2개 action은 항상1(최대개방)이다.

Baseline2초→초기 앞쪽 위치에서낮추기4초→옆정렬4초→수평진입5초→접촉접근3초→직선밀기8초→정지6초,총32초를32환경에서 기록했다. EEF 목표 작업높이1.13m,goal은초기target±Y.12m,손경로의마지막직선이동은.145m다. XY 경로는 오른손asset에서 계산한palm-center offset과개별target radius로 결정한다.

**32/32개 모두 최종3cm 반경 내부에 도달**했다. 최종거리6.06~23.62mm,평균15.61mm다. 실패termination(낙하/선반/관절속도)은0개다. 실제최대Arm속도.96878rad/s,수평진입이후손전체mesh bbox높이1.07164~1.26120m였다. 명령한world목표와OSC내부root목표를world로복원한값의최대차이는.9537µm다.

**3초 안정 유지 성공은21/32(왼쪽15/16,오른쪽6/16)**다. 남은11개는목표안에있어도순간속도>.005m/s 때문에연속유지시계가끊겼다. 마지막2초의peak가일부.0053~.0136m/s였고,최종순간속도만작다고3초연속조건을만족한것은아니다. 손을접촉상태로유지한시험이므로미세접촉진동/밀림이포함된다. success조건을완화하거나속도를필터링하지않았다.32개모두성공했다고보고하지않는다.

### 촉각·F/T

다음은노이즈를넣기전보정F/T의벡터크기와34개원시촉각bit다. 힘은N,모멘트는Nm,활성률은해당phase의환경×step표본중비율이다.

| 방향·구간 | 평균힘 | 평균모멘트 | 앞면하나이상 활성 | 뒷면하나이상 활성 |
| --- | ---: | ---: | ---: | ---: |
| left / baseline | 1.589654e-06 | 2.805935e-06 | 0.000% | 0.000% |
| left / approach_contact | 0.01769529 | 0.0004679117 | 5.125% | 0.000% |
| left / push | 1.240918 | 0.01908782 | 99.250% | 0.000% |
| left / hold | 1.31328 | 0.01338484 | 87.792% | 0.000% |
| right / baseline | 1.596801e-06 | 2.625166e-06 | 0.000% | 0.000% |
| right / approach_contact | 1.756414e-06 | 1.710034e-06 | 0.000% | 0.000% |
| right / push | 1.193368 | 0.01250983 | 0.000% | 94.047% |
| right / hold | 1.295313 | 0.01035465 | 0.000% | 100.000% |

왼쪽push는앞면ch0,오른쪽push는대응뒷면ch17이주로활성화되며반대면은0이었다.평면중앙으로미는시험이므로나머지finger채널이활성화되지않는것은예상되는결과다.모든34채널의실제물리접촉이나같은물체두접촉의전공간coverage를이실험이증명하지는않는다.복수접촉누적은별도CPU기하회귀에서검사했다.

비접촉접근의force residual도약1.6~1.7µN수준이고push는약1.2N,모멘트는약.013~.019Nm로분리된다.이작은비접촉residual은simulator의질량/관성/운동량을직접이용하는취소기의결과이며실제하드웨어noise 성능을뜻하지않는다.실제Actor입력의1% tactile bit변조·F/T 관측noise를포함한배열도별도로저장했다.

### 보상 및 페널티

유효에피소드(최초termination step포함)내환경당누적보상의방향별평균이다.성공하지않은환경은32초시험끝까지기록되므로좌우총보상은동일길이정책성능비교가아니다.

| 항목 | 왼쪽16개평균 | 오른쪽16개평균 |
| --- | ---: | ---: |
| target_reaching | 7.9209881 | 7.6201553 |
| target_goal_distance | 30.90287 | 41.308464 |
| target_goal_hold | 55.859337 | 68.823624 |
| target_contact | 11.457573 | 12.407594 |
| robot_action_rate_penalty | -1.9784955e-05 | -1.9421514e-05 |
| robot_joint_velocity_penalty | -0.13295901 | -0.023418291 |
| object_tilt_penalty | 0 | 0 |
| obstacle_displacement_penalty | 0 | 0 |
| shelf_penalty | -8.3926411 | -8.750597 |
| obstacle_contact_penalty | 0 | 0 |
| target_goal_first_entry_bonus | 15 | 15 |
| target_goal_success_bonus | 70.3125 | 28.125 |
| wrist_wrench_change_penalty | 0 | 0 |

- 최초진입은모든환경에서정확히한번+15다.안정유지성공21개만첫종료step에+75이며나머지는0이다.
- 거리·hold·contact·joint-velocity·action-rate·reaching을기록신호로독립재계산했다.최대오차는각각2.98e−8,7.18e−8,1.09e−9,2.33e−10,5.96e−12,1.80e−6으로float32연산범위였다.보상항합과total차이최대7.63e−6이다.
- 장애물0개이므로장애물접촉/변위페널티는전구간0이다.기울기비용과wrench-change도0이었다.후자는힘변화20N·모멘트변화2Nm면제범위를넘지않았기때문이다.
- shelf penalty는0이아니다.선반실패event는없지만기존virtual finger/wrist의근접비용이발생한다.이dense항은surface1.06m,손가락2cm·손목8cm여유,EEF와선반중심거리20cm를사용한다.실제손collision만으로해석하면안된다.기존규칙을요청대로유지했으며계수를바꾸지않았다.
- timeout은40초이며시험은32초에끝냈다.따라서이번GUI밀기시험에서timeout을의도적으로발생시키지는않았다.종료CFG는표준`time_out`이고CPU구성회귀에서확인했다.

### 최종 산출물과 한계

Workspace의`outputs/wrench_refactor_validation/push_audit_v7/`에원시기록·summary·시계열그림을보존했다.그림은실제render로확인했다.재구성부록을최종소스및실제설정export로갱신했다. 문서만으로117파일을새디렉토리에복원하고별도에셋을복사하여실제Isaac Lab import와USD probe를통과했다. 에셋루트재배치와log_dir차이를제외한전체환경/PPO설정은원본과정확히같았다.7168reset/140만방위샘플/32직선밀기/CPU160개범위이며2048환경·장기RL학습·모든장애물접촉manifold·물리하드웨어전이는미검증이다.초기실패실행도삭제하지않았다.

## 후속: Hand 속도 페널티에서 미믹 제외

사용자가중복속도비용을지적하여Refactor에만적용했다. 오른손ZIP의URDF joint/mimic을직접검사해독립구동6축(thumb1/2,index1,middle1,ring1,little1)을확정했다. thumb3는thumb2의.8024배,thumb4는thumb3의.9487배,각손가락2번은1번의1.0843배이므로기존12축제곱합은구동축의운동을중복반영했다.

변경은reward CFG의hand_cfg joint_names 12→6뿐이다. 공통reward함수·다른환경·Arm비용·계수·cap·동작제어·관측·종료·커리큘럼은보존했다. 현재HandOpennessAction은12개위치목표를모두쓰기때문에“시뮬레이터에서12개중6개actuator를없앴다”는의미가아니다.

실제reward callable에미믹만5rad/s,구동축0을넣으면비용0;구동축6개각1rad/s면raw.06;Arm6개도1rad/s면raw.24를검사한다. 새GUI기록에는합산관절이름을기록하며분석기는metadata가없는이전v1~v7기록을기존12축기준으로해석한다. 과거실험값을새6축보상으로재명명하지않는다. CPU회귀161개통과(24.55초),실제Isaac Lab설정import통과. 이전export와전체환경/PPO구성을대조하여hand_cfg.joint_names외차이0개를확인했다. 새6축보상으로GUI물리를재실행하지는않았다.
