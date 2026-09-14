# 구현·평가 설계 메모

기준일: 2026-09-14. **이 문서는 PROPOSED 설계 메모다. 구현 사양 승인서나 실행 결과가 아니다.** 연구 근거는 S-0910·S-0911·S-TASK1·S-0914이며, 아래 검사·인터페이스·실험 분해는 인계 작성자의 실행 제안이다. 출처는 [출처 목록](06_SOURCE_REGISTER.md)을 따른다.

## 1. 설계 전에 고정할 네 경계

| 정보 흐름 | 허용·구분 원칙 |
| --- | --- |
| 배포 actor 입력 | 실제 로봇에서 해당 시점에 얻을 수 있는 초기 정보·센서·선택한 고유감각 |
| 학습용 정보 | reward/reset 및 선택한 critic 설계에서 쓰는 정답. actor와 분리 |
| 평가용 정답 | 물체 pose·접촉 위치·종료 성공 등 채점에 필요한 정보. actor로 돌려보내지 않음 |
| 안전 감독 | 정책 출력과 별개로 실행을 제한하는 장치·절차. 학습된 간섭 분류와 구분 |

GT initial pose를 이용해 perception 오차를 제거하는 실험과, 현재 object GT pose를 매 step 관측하는 oracle 실험은 다르다. 전자는 초기정보 가정이고 후자는 실행 정보 조건의 변경이다. S-0911의 GT-first 전략을 최종 Blind actor의 실시간 GT 허용으로 확대하지 않는다.

## 2. 좌표계·시간·목표 표현

### 2.1 저장해야 할 시점과 기준

선반 기준 좌표계 `S`, EEF 기준 `E`, F/T 센서 기준 `W`를 구분하는 안을 사용한다. 실제 TF 이름·축 부호는 코드와 실물에서 확인하여 정한다. ‘오른쪽’을 임의로 +x 또는 +y에 고정하지 않는다.

`initial_observation_time`과 `skill_start_time`을 별도로 기록한다. 접근 과정에서 물체가 움직였다면 초기 관측값은 오래된 정보다. 초기 물체 pose를 현재 물체 pose로 덮어써서 안 된다. 고유감각으로 EEF frame을 바꾸어 표현하는 것과 최신 물체 pose를 다시 관측하는 것도 구분한다.

### 2.2 목표 표현 후보

초기 추정 위치 `p_hat_0`, 단위 방향 `d`, 목표 거리 `L`이 같은 좌표계에 있다면 명령 목표를 `p_goal_cmd = p_hat_0 + L*d`로 정의할 수 있다. 이는 S-TASK1의 방향·거리 개념을 적은 것이며 입력 인코딩은 미정이다.

평가에서는 두 값을 분리해 기록할 것을 제안한다.

```text
명령 목표 오차: ||p_object(t) - p_goal_cmd||
실제 방향 이동: dᵀ [p_object(t) - p_object(0)]
```

초기 추정 오차가 있으면 이 둘은 같은 의미가 아니다. 어떤 값을 성공 판정에 쓸지 명시해야 한다. `EEF displacement == object displacement`로 가정하지 않는다.

## 3. 관측 계약 초안

| 항목 | 출처와 갱신 | 현재 상태·주의 |
| --- | --- | --- |
| 초기 대상 pose | 초기 시각/초기 GT proxy | 실행 중 현재 pose로 갱신하지 않음 |
| 방향·거리 | 상위 명령 | 한 번의 skill 동안 유지하는 구상 |
| 초기 주변 정보 | 초기 관측 | 9/14 활용 허용. 하위 입력 범위·표현은 OPEN |
| Geometry | 초기 perception 또는 별도 정보 | 9/13안은 사용하지 않음. 현재 추가 여부 OPEN |
| wrist wrench | 실시간 F/T | raw/보정, 단위·frame·timestamp를 명시 |
| tactile | 영역별 원시 신호→전처리 | 17차원 축약은 후보. raw Grid와 구분 |
| q, q_dot, EEF state | robot proprioception | 선택할 항목과 frame OPEN |
| 이전 action/history | 정책·센서 기록 | 길이·간격·reset 규칙 OPEN |
| validity/sample age | 센서 상태 | 누락·지연 처리를 위한 제안. 실제 획득 가능성 확인 |

개념적으로 `o_t = [initial_info, goal, wrench_t, tactile_t, selected_proprioception_t, selected_history_t]`로 볼 수 있다. 이 표현은 네트워크 입력 차원이나 tensor 순서를 확정하지 않는다.

### 관측 누출 검사

매 step GT object pose·velocity, 정확한 주변 물체 pose, 물체 질량·마찰의 정답, 접촉 대상 ID, 센서가 덮지 않는 영역의 완전 접촉 정보가 actor에 들어오는지 확인한다. 센서 simulation 내부에서 정답을 이용해 물리 신호를 만들 수는 있지만, 그 식별자·정답 상태를 그대로 출력하면 실제 센서 조건과 달라진다.

Privileged critic이나 auxiliary estimation head는 선택 가능한 설계일 뿐 현재 채택된 구조가 아니다. 채택하면 별도 결정과 배포 시 필요한 정보 범위를 명시한다.

## 4. 촉각 전처리와 F/T 대응

### 4.1 촉각

S-TASK1은 영역별 gram-force Grid를 scalar/Boolean으로 축약하는 안을 제시했다. 실제 센서 출력은 매뉴얼과 원시 sample로 다시 확인한다. 센서 17개, 각 센서 내부 taxel 수, 최종 policy dimension은 서로 다른 수다.

각 영역의 위치, 면적, 방향, raw shape, 단위, 유효 범위, 결측 표현을 먼저 기록한다. 합계·평균·최댓값은 서로 다른 정보를 보존하므로 임의로 동등하게 취급하지 않는다. Boolean은 force magnitude를 제거하므로 scalar와 같은 17차원이어도 정보량이 같지 않다.

센서별 대응 관계를 유지하고 raw 데이터를 따로 저장한다. 전처리 함수를 바꿔도 비교 실험을 재구성할 수 있어야 한다. threshold와 filtering 값은 측정 또는 명시적인 시험 가정에 근거해 설정한다.

### 4.2 F/T

정의할 것은 센서 frame, 힘·모멘트 단위, 측정 기준점, 영점, Hand 부하, 자세·운동 변화의 영향, raw/compensated 채널, filtering·지연이다. simulator의 특정 contact force를 바로 실물 wrist F/T와 같다고 단정하지 않는다.

F/T 증가만으로 ‘다른 물체와 간섭했다’고 결론 내리지 않는다. 접촉 위치·물체/선반 특성·운동 상태 등의 차이로 신호가 달라질 수 있다는 점이 S-0914의 문제 제기다. 원인 구분은 별도 검증 대상이다.

## 5. 시뮬레이션 센서 모델의 단계

| 단계 | 목적 | 기록할 한계 |
| --- | --- | --- |
| 이상 정보 디버그 | controller·reward·물체 동역학이 작동하는지 확인 | 실제 sensing 성능이 아님 |
| 기하학적 센서 영역 모델 | 실제 부착 영역에서만 tactile을 생성 | 영역·해상도 가정 |
| 제한 신호 모델 | noise·양자화·지연·누락·약한 감지 조건의 영향 확인 | 수치는 실측 또는 가정 여부 명시 |
| 실물 대응 모델 | 실제 위치·단위·수신 주기·신호 특성으로 갱신 | 여전히 재현하지 못한 요소 기록 |

실물이 준비되지 않았다고 이상적인 전손 접촉을 실제 tactile처럼 다루지 않는다. 비센서 부위 접촉에서는 평가 정답상 접촉이 있어도 tactile 출력이 없을 수 있는 모델이 필요하다. Hand contact sum을 어떤 방식으로 wrist wrench로 대응시킬지도 별도로 정의해야 한다.

`no_contact`, `sensor_missing`, `below_effective_detection`, `uncovered_contact`를 분석상 구분한다. 이 라벨은 평가·로그용이며 실제 구분 불가능한 원인을 actor의 정답 입력으로 주면 안 된다.

## 6. reset과 접근 오차

기본 reset은 물체 근처의 접근 완료 상태다. 현재 코드의 넓은 초기 joint randomization을 그대로 최종 조건으로 채택하지 않는다. 초기 접촉 여부, 위치 오차, orientation 오차, 유효 joint configuration을 명시한다. [S-0910]

실측 전에는 임시 분포를 `assumed`로 표시한다. 실측 후에는 접근 반복에서 얻은 상대 pose 오차 분포와 simulation reset을 비교한다. 같은 perception error를 물체 pose randomization·EEF 오차·관측 noise에 독립적으로 여러 번 넣어 과장하지 않도록 생성 모델을 남긴다.

다양한 물체와 접촉 위치를 도입할 때 sensor coverage와 contact geometry가 함께 바뀌는 효과를 구분한다. 모든 randomization을 한 번에 추가하기보다 원인을 분리할 수 있는 단계적 실험이 적절하다.

## 7. 행동·controller·Hand 구성

9/10 보고 코드는 Cartesian/OSC였고 이후 연구안에는 Diff-IK 등의 관절 명령 변환이 등장한다. 먼저 실제 코드를 읽고 아래 표를 채운다. 근거 없이 controller를 교체하지 않는다.

| 항목 | 현재 값 |
| --- | --- |
| action semantics: position increment / velocity / wrench 등 | OPEN |
| action dimension와 각 축 | OPEN |
| action의 기준 frame | OPEN |
| scaling·clipping·명령 주기 | OPEN |
| controller 종류와 설정 | OPEN; OSC 사용 보고 이력 있음 |
| 손 자세 고정 / mode selection / 연속 hand control | OPEN; predefined posture 제안 있음 |
| policy rate와 실제 sensor/control rate | OPEN |
| 안전 제한과 감독 방식 | 실물 구성 확인 후 결정 |

RNN, hybrid action, stiffness action, 엄격한 무회전 제약은 자동 추가하지 않는다. 기본 센싱과 제어가 불확실한 상태에서 복잡한 action space로 실패 원인을 늘리지 않는다.

## 8. 보상·성공·종료를 분리

### 8.1 보상 후보

목표 방향 진행, 목표 오차, 접촉 유지, 과도한 힘, 물체 전도, 불필요한 운동 등의 후보를 검토할 수 있다. 어떤 항목과 계수를 쓰는지는 OPEN이다. 특히 정상적인 밀기 접촉을 일괄 collision penalty로 처리하지 않는다. 관측할 수 없는 주변 상태를 벌점으로만 강요할 때 생길 학습 문제는 검증 질문으로 남긴다.

Reward에 GT를 사용하는 것과 actor에 GT를 넣는 것은 다르다. 다만 reward나 termination으로 정보가 간접 제공되는 실험 조건까지 결과에서 명확히 설명해야 한다.

### 8.2 물리적 성공과 실제 종료

평가용 GT로 목표 도달을 채점할 수 있다. 그러나 실물 Blind 실행은 그 GT를 갖지 않으므로 **정책이 언제 멈출지**가 별도 문제다. EEF 이동 거리를 성공의 대리 정답으로 바꾸지 않는다.

가능한 설계 후보에는 제한된 실행 시간/운동 budget, 센서·이력 기반 종료 판단, 상위의 재관측 후 완료 확인 등이 있다. 어느 방식도 이번에 채택하지 않는다. 각 방식이 한 번의 Blind 구간을 어떻게 정의하는지와 조기 종료·미종료 오류를 비교한 뒤 결정해야 한다.

GT 도달 시 simulator가 자동으로 episode를 끝내는 초기 실험은 가능하지만 `oracle-terminated`로 표시하고, 그 성능을 실물의 자율 종료 성능으로 주장하지 않는다. 독립 안전 감독의 개입률도 별도로 보고한다.

## 9. 제안 실험 순서와 비교 조건

| ID | 실험 | 목적 | 상태 |
| --- | --- | --- | --- |
| E-00 | 실제 코드·관측·controller 경로 audit | 현황과 GT 누출 확인 | 계획 |
| E-01 | 센서 영역·비센서 영역 contact probe | 실제 접촉과 감지의 관계 확인 | 계획 |
| E-02 | 단순 물체·제한 방향의 기본 pushing | 물리·제어·목표 정의 확인 | 계획 |
| E-03 | 공통 초기정보/고유감각 아래 무접촉센서·F/T·tactile·결합 비교 | 센서 기여 분리 | 계획 |
| E-04 | 접촉 위치·coverage·약한 신호·초기 오차 변화 | 실패 범위와 robustness | 계획 |
| E-05 | history 없음/있음 비교 | 시간 정보의 기여 확인 | 필요성 검토 |
| E-06 | 실제 접근 분포와 실물 센서 조건에서 검증 | 전이와 종료 판정 평가 | 장비 의존 |
| E-07 | 추가 간섭 판별과 규칙 기반 비교 | 후속 기여 검증 | DEFERRED |

Ablation을 할 때 제거한 센서 외의 goal·proprioception·controller·training budget·test condition을 가능한 한 맞춘다. 각 조건에서 다시 학습한 비교인지, 학습 후 입력만 제거한 robustness 검사인지 구분한다. 여러 seed 및 보지 않은 조건을 사용하되 실제 개수·훈련량은 사전에 기록하고 결과에서 공개한다.

## 10. 지표와 기록

목표 물체의 최종 오차·실제 이동 거리, 물체 회전·전도·낙하, 접촉 손실, wrench peak·누적 상호작용, 수행 시간, 종료 오류, 안전 개입, 센서 누락·지연 등을 후보로 둔다. 물체·센서·제어 조건에 맞게 최종 지표를 정하고 수치 기준을 임의 확정하지 않는다.

각 run에는 코드·설정·체크포인트·seed·물체/선반 조건·초기 분포·sensor model·actor/critic 입력·종료 방식·평가 정답의 출처를 연결한다. raw와 전처리 후 신호, robot state와 action의 timestamp를 보존한다. 분석용 GT contact label은 actor 입력과 별도 저장한다.

## 11. 구현 전후 검사 목록

- [ ] 코드 저장소·커밋과 실제 실행 설정을 확인했다.
- [ ] 초기 object pose와 현재 GT object pose의 경로를 분리했다.
- [ ] actor/critic/reward/evaluation/safety 입력을 구분했다.
- [ ] tactile 영역·raw dimension·축약 함수·유효 상태를 명시했다.
- [ ] wrist wrench frame·단위·부하·보정의 의미를 기록했다.
- [ ] 접근 완료 후 reset을 정의하고 실제/가정 분포를 구분했다.
- [ ] action→controller→robot command 경로를 확인했다.
- [ ] 물체 성공과 EEF 진행, 평가 채점과 실제 종료를 분리했다.
- [ ] 실행한 검사와 실행하지 못한 검사를 결과에 각각 표시했다.
- [ ] 기본 결과 없이 간섭·회피·Pivoting 확장을 끼워 넣지 않았다.
