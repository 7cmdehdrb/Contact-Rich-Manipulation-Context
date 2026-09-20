# Pushing in the Dark: A Reactive Pushing Strategy for Mobile Robots Using Tactile Feedback

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B063
- Authors: Idil Ozdamar; Doganay Sirintuna; Robin Arbaud; Arash Ajoudani
- Year: 2024
- Venue: IEEE Robotics and Automation Letters 9(8),6824–6831
- DOI / arXiv: 10.1109/LRA.2024.3414279 / Not stated
- PDF version: IEEE publisher PDF
- Page count: 8
- SHA-256: d42a4eca50357a08a1a86bffb30ccc018149062627dd0ddd46fabdd495b4e76f
- PDF filename: Ozdamar 등 - 2024 - Pushing in the Dark A Reactive Pushing Strategy for Mobile Robots Using Tactile Feedback.pdf
- 읽은 범위: PDF pp.1–8 본문 및 포함된 부록을 새로 확인; 핵심 표·그림 렌더링 확인

근거는 이번 배치의 PDF 원문이며 기존 상세 노트는 사용하지 않았다. 페이지는 PDF의 1-based page이다.

## 2. Relevance to This Review

**Relevant**. 42개 capacitive sensing area를 threshold하고 접촉 위치로 축약해 current object pose/shape 없이 pushing한다. Binary/contact-location representation과 robot pose/known base geometry의 보완 관계를 직접 검토할 수 있다. 손목 F/T나 force magnitude를 사용하는 방법은 아니다.

## 3. Task

Omnidirectional rectangular mobile base로 bulky box/cylinder를 목표 주변으로 민다. 성공/stop은 object center가 아닌 현재 contact point–goal distance < 0.05 m이며 simulation은 300 s 및 150 s 이상 contact loss 조건도 적용한다. Object orientation은 제어하지 않는다. (§II.C pp.3–4; §III.B p.5)

## 4. Method

### 4.1. Overall Pipeline

42-taxel capacitance→low-pass/threshold→active taxel positions→point/line contact와 representative 2D contact point→robot world pose+world goal→reactive velocity/state machine→mobile base(vx, vy, omega). (Fig. 3/Algorithm 1 p.4)

### 4.2. Observation

Controller 입력은 world goal 2D, robot world position/rotation, robot-relative contact point이다. Contact point는 1개 taxel일 때 그 좌표, 복수 taxel일 때 contact boundary 양 끝 taxel 좌표 평균. Current object center/orientation/shape/mass/friction은 없다. Robot localization은 odometry로 서술한다. (§II.B–C p.3; Algorithm 1 p.4; §III.B p.6)

### 4.3. Action

Base planar vx, vy, yaw rate. Lateral velocity로 contact를 중앙으로 돌리고 edge critical region에서는 realignment state를 사용한다. Linear 0.05 m/s, angular 0.15 rad/s로 saturation을 적용해 quasi-static을 지향한다. (§II.C pp.3–4; §III.A p.5)

### 4.4. Controller

Rule-based reactive controller: contact-goal 거리와 heading error, bicycle-model 형 yaw 계산, contact lateral-offset logistic gain, realignment hysteresis. UR16e와 Softhand는 플랫폼에 있지만 task에는 base만 사용한다. Algorithm 1 마지막 벡터의 vx 중복 인쇄는 본문 Eq.(1)의 vx/vy 정의와 구별한다. (§II.A p.2; II.C pp.3–4)

### 4.5. Learning / Optimization Method

학습/RL/optimization 없음. Heuristically tuned gains를 sim/real 동일 사용. RPS를 lateral/realignment를 제거한 NPS 및 vision-based APS와 비교. (§III pp.5–7)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Thresholded taxels로 robot-relative 2D contact point 추정 | 매 contact update | Object center position은 미제공; contact point를 world로 변환해 goal 거리 계산 (§II.B–C p.3) |
| Orientation | 미제공 | Current object orientation 없음 | 없음 | Robot heading과 goal bearing은 존재 (§II.C pp.3–4) |
| Shape / Geometry | 미제공 | Object shape/size 입력 없음 | 없음 | Known rectangular base geometry/taxel locations 필요; object geometry와 구분 (§II.B–C pp.2–3) |
| Physical Parameters | 미제공 | Mass/friction/inertia 없음 | 없음 | Quasi-static pushing 가정 (§II.C p.3) |

## 6. Missing Object Information and Compensation

Current object pose/shape/physical model 미제공 → reduced tactile contact location + robot odometry/world goal + known sensor/base geometry + reactive rule → 접촉이 edge로 이동할 때 base를 재정렬한다. Object pose를 복원하는 대신 contact point를 task feedback 변수로 선택한다. 따라서 contact-goal 성공을 object center/6D pose 정확도로 바꾸면 안 된다. (§II–III pp.3–6)

## 7. Tactile

### 7.1. Raw Sensor

14 PCBs × 3 electrodes = 42 taxels, 각 4.3 cm. Front/left/right base를 conductive-ink-coated foam이 덮고 compression에 따른 capacitance를 측정한다. (§II.B pp.2–3)

### 7.2. Preprocessing

Taxel별 low-pass filter→threshold→timestamped contact transmission. Threshold 수치는 미명시. (§II.B p.3)

### 7.3. Policy Representation

1 active taxel = point contact 및 해당 위치; multiple = line contact 및 양 끝 taxel 위치 평균. Controller에는 2D contact point가 전달된다. (§II.B p.3)

### 7.4. Retained Information

활성 영역 위치, point/line 분류, 대표 contact location. (§II.B p.3)

### 7.5. Removed / Unavailable Information

Threshold 후 force/pressure의 연속 크기와 방향은 controller 입력으로 유지하지 않는다. 양 끝 평균 축약은 전체 activation pattern/내부 분포를 보존하지 않음(구조상 확인). 모든 다중 접촉이 한 line으로 대표 가능하다는 일반 검증은 없다. (§II.B p.3)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. Simulation Gazebo contact sensor는 wrench도 출력하지만 저자들이 position만 사용했다고 명시한다. (§III.B p.5)

### 8.2. Representation

No force/wrench policy input; capacitive touch의 contact location만 사용. (§II.B p.3; III.B p.5)

### 8.3. Role

해당 없음. (§III.B p.5)

### 8.4. Required Assumptions

F/T-only localization 해당 없음. Tactile location + known robot geometry/odometry, holonomic base, quasi-static motion 가정. (§II.C p.3)

### 8.5. Reported Limitation / Ambiguity

원문에서 F/T의 해당 한계를 직접 논의하지 않음. (§IV pp.7–8)

## 9. Other Observations

Robot world pose/odometry와 predefined world goal은 필수다. Previous action/sensor history window/RNN은 없으며 state machine의 realignment threshold 메모리는 있다. Vision은 제안 RPS에 없고 APS baseline에만 있다. (§II.C pp.3–4; §III.B pp.5–6)

## 10. Tactile–Other Modality Relationship

| 추가 정보 | Tactile 정보 | Tactile에서 없는 정보 | 역할 | 근거 |
| --- | --- | --- | --- | --- |
| Robot odometry/world goal | 로봇 상대 contact 위치 | World goal까지 거리/heading | 접촉좌표 world 변환, 진행 방향/종료 결정 | Eq.(3) p.3 |
| Known base/taxel geometry | Active taxel index | Metric contact location | 점/line 중점 좌표와 edge 근접해석 | §II.B p.3 |
| Realignment state | Contact lateral offset | 지속적인 edge 탈출 동작 | Hysteresis로 중앙 복귀 | Algorithm 1 p.4 |

NPS는 tactile 제거가 아닌 reactive control 구조 제거 비교다. Tactile+F/T sensor combination 비교는 없다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부·비고 |
| --- | --- | --- | --- |
| Actor | 해당 없음 | 비-RL | 해당 없음 (§II–III pp.2–7) |
| Critic | 해당 없음 | 비-RL | 해당 없음 (§II–III pp.2–7) |
| Reward | 해당 없음 | 비-RL | 해당 없음 (§II–III pp.2–7) |
| Termination | 해당 없음 | 비-RL | 해당 없음 (§II–III pp.2–7) |
| Curriculum | 해당 없음 | 비-RL | 해당 없음 (§II–III pp.2–7) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Contact-reactive motion | Controlled comparison | RPS vs no-lateral/no-realignment NPS vs APS | Simulation 144 conditions: 88.19% vs 15.97% vs 5.56%; sensor 제거 실험은 아님 | §III.B pp.5–6; Table II p.6 |
| Real object/goal robustness | Controlled comparison | 2 objects × 8 targets; proposed RPS | 100% 보고; 평균 completion 89 s (box)/88 s (cylinder). Real baseline 비교 없음 | §III.C pp.6–7 |
| Cylinder failure | Failure analysis | Cylinder vs boxes | 낮은 sim 성공률 원인으로 rolling과 box line-contact 안정성 차이를 저자가 추정 | §IV pp.7–8 |

## 13. Author-stated Limitations

Simulation에서 cylinder 성공률이 더 낮고 저자들은 rolling/line contact 안정성 차이를 가능 원인으로 든다. 현재 목표는 unknown-property object의 position 운반이며 orientation control/obstacle avoidance는 향후 확장이다. Quasi-static 및 uncluttered environment 범위를 명시한다. (§II.C p.3; §I p.2; §IV pp.7–8)

## 14. Author-stated Future Work

Object pose 제어 및 주변 obstacle 회피로 확장하며 object shape/size와 vision 기반 obstacle/orientation 정보가 추가로 필요하다고 명시한다. (§IV p.8)

## 15. Review-relevant Findings

- 42 taxels를 threshold한 후 representative contact point로 축약한다.
- Current object center/orientation은 없지만 robot world pose/goal은 제공된다.
- Gazebo wrench는 명시적으로 사용하지 않는다.
- 성공의 0.05 m는 contact point–goal 거리다.
- Binary tactile와 F/T 결합 효과는 평가하지 않았다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation/Object pose | Algorithm 1 p.4; Eq.(3) p.3 |
| Tactile | §II.B pp.2–3 |
| F/T | §III.B p.5: 출력 중 position만 선택 |
| Controller | §II.C pp.3–4 |
| Reward/Critic | 비-RL, 해당 없음 |
| Comparison | §III.B–C pp.5–7; Table II p.6 |
| Limitation/Future | §IV pp.7–8 |
