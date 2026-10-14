# 최종 Sweeping 정책 구현·검증 TODO

[학습 기록](../02_implementation/logs/2026-10-12_inspire_hand_training.md) · [발표 문서](presentation/README.md) · [문서 안내](README.md)

**기준일: 2026-10-12.** 아래는 현재 학습 기록과 구현을 기준으로 정리한 후속 작업 제안이다.

## 1. 현재 어디까지 확인했는가

초기 Sweeping 실패의 주요 문제는 **Hand 접촉으로 물체가 반복적으로 전도되는 것**이었다. 전도에 덜 민감한 물체에서는 기존 보상으로 기본 Sweeping을 학습했다. 따라서 먼저 물리·제어 이슈를 정리하고, 확보한 동작을 바탕으로 발표의 최종 목표에 필요한 보상으로 전환한다.

| 항목 | 현재 상태 | 남은 확인 |
| --- | --- | --- |
| Inspire Hand와 손가락 제어 | **기본 동작 검증:** `v1-mass`에서 정상 학습 | 일반 물체에서도 전도 없이 수행 가능한지 |
| Tactile·F/T 추가 | **센서 포함 학습 검증:** `v2-mass`에서 정상 학습 | 손바닥 접촉 1D + F/T 6D를 넣은 결과이며, 공간 촉각과 센서별 기여는 미검증 |
| 현재 물체 위치 관측 제거 | **진행 중:** `v3`, Actor·Critic 41D | 초기 위치와 로봇·접촉 관측만으로 Sweeping을 유지하는지 |
| Privileged Critic | **학습 대기:** `v4`, Actor 41D / Critic 54D | Actor 관측을 유지하면서 학습에 도움이 되는지 |
| 최종 관측·보상 구성 | **일부 구현, 통합 검증 필요:** 코드 2에 17영역 촉각·목표·법선·접촉·위험 보상 초안 존재 | 최신 발표와의 차이 조정, CoP 회전 Sub-Goal 구현 및 효과 확인 |

학습 성공 여부는 [최신 학습 기록](../02_implementation/logs/2026-10-12_inspire_hand_training.md)을 따른다. [환경 목록](../02_implementation/logs/1012_src_robot_hand_environments.md)과 [체크포인트 목록](../02_implementation/logs/1012_latest_checkpoints_play.md)은 구현·파일 확인 자료이며 성공률 검증 결과는 아니다. 또한 mass 실험은 [실린더 형상과 낮은 무게중심](../02_implementation/logs/1010.md)으로 안정성을 높인 조건이다.

## 2. 도달할 최종 목표

**접근이 완료된 상태에서, 초기 물체 위치와 명령 방향·거리를 받아 Tactile·F/T 피드백으로 물체를 목표까지 이동시키는 Blind Sweeping**을 구현한다. 실행 중 현재 물체 위치·자세는 Actor에 제공하지 않는다. 성공은 Hand 이동량이 아니라 **물체의 목표 위치 오차 1 cm 미만**으로 평가한다.

과업 범위는 발표의 **명령된 Sweep 구간에 다른 물체의 간섭이 없는 조건**을 따른다. 목표·관측·종료의 상세 정의는 [과업](presentation/02_Task_Definition_and_Framework.md), [정책 입력](presentation/03_Contact_Representation_and_Policy.md), [성공·종료](presentation/05_Success_and_Termination.md)를 기준으로 한다.

## 3. 진행 순서

### 1단계 — 물리·제어 병목을 정리하고 기준 환경 고정

- [ ] **Arm 속도·진동 원인 확인:** `hand_velocity` 종료 임계치 완화 이후의 진동과 속도 초과 원인을 확인한다. 이미 추가된 `v1-mass-limit`을 이용해 **3.0 → 1.0 rad/s 복원** 시 동작과 종료 양상을 비교한다. 비교 환경은 구현되어 있으나 학습 결과는 아직 확인되지 않았다.
- [ ] **실측 마찰 적용:** Friction Test의 물체–선반 마찰과 Randomization을 적용하고, Hand–물체 마찰도 정한다. 실제에 맞는 형상·질량·무게중심과 접촉 높이에서 **미끄러짐과 전도 중 무엇이 발생하는지** 확인한다.
- [ ] **성공 기준 환경 보존:** 정상 학습한 설정·체크포인트를 남기고, 위 조건을 정리한 뒤 기존 보상으로 기본 Sweeping이 유지되는지 확인한다.

### 2단계 — Blind 관측과 최종 환경 구성 연결

- [ ] **`v3`·`v4` 결과 확인:** 초기 위치만 사용하는 조건의 학습 가능성과 Critic 특권 정보의 효과를 보고 최종 Critic 구성을 정한다. 현재 물체 GT는 보상·평가 및 선택한 Critic에만 사용한다.
- [ ] **최종 센서·관측으로 확장:** 손바닥 한 영역에서 **선택 작업면 Header + 17영역 Tactile(18D)**로 확장하고 최종 Actor **57D**의 항목을 맞춘다. 손바닥·손등 영역 매핑, F/T 좌표·모멘트 기준점·자중 영향을 확인한다. 기존 손등 센서는 부모 링크 접촉을 재사용한 근사이므로 공간 접촉의 신뢰성을 따로 확인한다.
- [ ] **환경 구성을 고정한 후 기존 제어·초기화 적용:** 사전 검증한 **OSC, Relative Observation, Object Pose Dependent Initial Joint State**를 통합한다. Relative Observation과 EEF 기준 Action 사이의 좌표 변환을 맞추고, 이때 학습이 실패하면 해당 요소를 Ablation한다. 접근 후 시작하는 `v3-mass` 구현은 초기 위치 관측을 고정하는 `v3`와 별개로 활용한다.

### 3단계 — 발표의 보상으로 순차 전환

코드 2의 보상 초안을 **정상 학습한 기준 환경에 이식·조정**한다. 접근 후 시작하는 최종 과업에 맞게 기존 Reaching·Gate 의존을 정리하고, 고정 방향 Sweep·속도 구간·Homing 중심의 보상을 **명령된 물체 목표 도달 중심**으로 바꾼다. 아래 순서는 개발 제안이며, 마지막에는 동일한 세 구성을 별도로 학습해 비교한다.

| 순서 | 적용할 보상 | 확인할 요점 |
| --- | --- | --- |
| **① Base** | **Goal + Action Rate + Time** | 현재 물체–목표 위치 오차로 이동을 유도한다. Arm·Hand 명령 급변을 억제하되 움직임을 막지 않는다. Time은 **성공 시 한 번 주는 조기 완료 보상**으로 맞춘다. |
| **② 접촉 보상 추가** | **Base + Normal + Contact** | 실제 대상 접촉 법선을 **현재 물체→목표 방향**에 정렬하고, 접촉 유무·17영역 활성 비율을 보상한다. 접촉만 유지하며 정지하는 정책이 생기는지 확인한다. |
| **③ 회전 보조 목표 추가** | **② + CoP 회전 Sub-Goal** | 촉각 접촉면과 보정 Wrench로 CoP를 추정하고, 신뢰할 수 있는 CoP 변화로 **Yaw 목표를 생성하여 추종을 보상**한다. 회전 목표가 접촉과 물체 진행을 개선하는지 확인한다. |

- [ ] **기존 구현과 최종식의 차이 반영:** 코드 2의 Step별 시간 비용과 미접촉 페널티 형태를 발표의 Time·Contact 정의로 맞춘다. Normal은 무접촉·다중 접촉 및 법선 부호를 확인한다. CoP의 유효 접촉 기준과 Yaw 목표 생성식은 추가 구현·검증한다.
- [ ] **실패 조건과 보상 균형 정리:** 전도·선반 접촉·Timeout 판정과 성공 기준을 맞춘다. 고정 선반에서 이동량 종료가 유효한지 확인하고, 기존 전도·물체 상승·판 접촉 위험 페널티의 적용 여부를 정한다. 보조 보상이나 위험 페널티 때문에 **물체 진행 없이 정지하는 행동**이 다시 생기지 않는지 확인한다.

보상 항의 상세식은 [최종 보상 설계](presentation/04_Reward_Formulation.md)를 따른다. 항별 기여와 실제 물체 진행을 함께 보고 가중치를 조정한다.

### 4단계 — 일반화와 최종 비교, 실물 연결

- [ ] **일반 물체·명령 조건으로 확장:** 안정 실린더에서 확보한 정책을 다양한 형상·크기·질량, 방향·거리, 접근 오차로 확장한다. 마찰·제어·센서 불확실성의 Randomization 범위를 정하고 실패 조건을 확인한다.
- [ ] **최종 Ablation:** 구성·가중치를 고정한 뒤 **센서 4조건(없음 / Tactile / F/T / 둘 다)**과 **보상 3조건(Base / +Normal·Contact / +Sub-Goal)**을 각각 별도 학습한다. 센서 비교에서는 Actor 관측만 바꾸고 보상용 신호는 유지하여 두 효과를 분리한다.
- [ ] **공통 지표로 평가:** 성공률·물체 위치 오차, 전도·접촉 상실·선반 접촉, 성공까지의 시간과 학습량을 비교한다. 총 Reward 크기만으로 개선을 판단하지 않는다.
- [ ] **실물 실행 연결:** MoveIt 접근 이후 센서 입력과 Arm·Hand 제어를 연결한다. 현재 물체 GT를 Actor에 주지 않는 상태에서 사용할 **종료 방식**과, 물체 성공을 측정할 **외부 평가 방식**을 정하고 확인한다.

비교 조건과 평가 기준은 [발표의 평가 계획](presentation/06_Evaluation_and_Schedule.md)을 따른다.

## 4. 확인한 자료

- **학습 경과:** [1009](../02_implementation/logs/1009.md), [1010](../02_implementation/logs/1010.md), [최신 학습 기록](../02_implementation/logs/2026-10-12_inspire_hand_training.md), [환경별 구현 현황](../02_implementation/logs/1012_src_robot_hand_environments.md), [체크포인트 현황](../02_implementation/logs/1012_latest_checkpoints_play.md).
- **학습 코드 1:** [Sweeping-Policy-DRL-Sim-Train / min](https://github.com/IROL-SSU/Sweeping-Policy-DRL-Sim-Train/tree/min), 확인 커밋 [25866dcf](https://github.com/IROL-SSU/Sweeping-Policy-DRL-Sim-Train/commit/25866dcffe940ff2c44b610a44a174819cb6671a). 기본 Sweeping, mass·센서·Blind·속도 임계치 비교 환경.
- **학습 코드 2:** [Contact-Rich-Manipulation](https://github.com/7cmdehdrb/Contact-Rich-Manipulation), 확인 커밋 [9f4a07c8](https://github.com/7cmdehdrb/Contact-Rich-Manipulation/commit/9f4a07c83c1854022f415b3a2e8008f6fceacbf8). OSC 환경과 `src/hand_manipulation_rl`의 센서·보상 초안.
