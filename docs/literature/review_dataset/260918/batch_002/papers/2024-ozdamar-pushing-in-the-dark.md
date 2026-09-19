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

근거는 이번 배치의 PDF 원문이며 기존 상세 노트는 사용하지 않았다. 페이지는 PDF의 1-based page다.

## 2. Relevance to This Review

**Relevant**. 42개capacitive sensing area를threshold하고접촉위치로축약해currentobjectpose/shape없이pushing한다. Binary/contact-location representation과robot pose/knownbasegeometry의보완관계를직접검토할수있다. 손목F/T나force magnitude를사용하는방법은아니다.

## 3. Task

Omnidirectional rectangular mobilebase로bulky box/cylinder를목표주변으로민다. 성공/stop은objectcenter가아닌현재contactpoint–goal distance<0.05m이며simulation은300s및150s이상contactloss조건도적용한다. Objectorientation은제어하지않는다. (§II.C pp.3–4; §III.B p.5)

## 4. Method

### 4.1. Overall Pipeline

42taxel capacitance→low-pass/threshold→active taxel positions→point/line contact와representative2Dcontactpoint→robotworldpose+worldgoal→reactivevelocity/state machine→mobilebase(vx,vy,omega). (Fig.3/Algorithm1 p.4)

### 4.2. Observation

Controller입력은worldgoal2D,robotworldposition/rotation,robot-relative contactpoint2D이다. Contactpoint는1taxel일때그좌표,복수taxel일때contactboundary 양끝taxel좌표평균. Currentobjectcenter/orientation/shape/mass/friction은없다. Robotlocalization은odometry로서술한다. (§II.B–C p.3; Algorithm1 p.4; §III.B p.6)

### 4.3. Action

Base planarvx,vy,yawrate. Lateral velocity로contact를중앙으로돌리고edgecriticalregion에서는realignment state를사용한다. Linear0.05m/s/angular0.15rad/s로saturation해quasi-static을지향한다. (§II.C pp.3–4; §III.A p.5)

### 4.4. Controller

Rule-basedreactivecontroller:contact-goal거리와headingerror,bicycle-model형yaw계산,contactlateraloffsetlogisticgain,realignmenthysteresis. UR16e와Softhand는플랫폼에있지만task에는base만사용한다. Algorithm1마지막벡터의vx중복인쇄는본문Eq.(1)의vx/vy정의와구별한다. (§II.A p.2; II.C pp.3–4)

### 4.5. Learning / Optimization Method

학습/RL/optimization없음. Heuristicallytunedgains를sim/real동일사용. RPS를lateral/realignment를제거한NPS및vision-basedAPS와비교. (§III pp.5–7)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Thresholdedtaxels로robot-relative2Dcontactpoint추정 | 매contactupdate | Objectcenterposition은미제공;contactpoint를world로변환해goal거리계산 (§II.B–C p.3) |
| Orientation | 미제공 | Currentobjectorientation없음 | 없음 | Robotheading과goalbearing은존재 (§II.C pp.3–4) |
| Shape / Geometry | 미제공 | Objectshape/size입력없음 | 없음 | Knownrectangularbasegeometry/taxellocations필요;objectgeometry와구분 (§II.B–C pp.2–3) |
| Physical Parameters | 미제공 | Mass/friction/inertia없음 | 없음 | Quasi-staticpushing가정 (§II.C p.3) |

## 6. Missing Object Information and Compensation

Currentobjectpose/shape/physicalmodel미제공 → reducedtactilecontactlocation + robotodometry/worldgoal + knownsensor/basegeometry + reactiverule → 접촉이edge로이동할때base를재정렬한다. Objectpose를복원하는대신contactpoint를taskfeedback변수로선택한다. 따라서contact-goal성공을objectcenter/6Dpose정확도로바꾸면안된다. (§II–III pp.3–6)

## 7. Tactile

### 7.1. Raw Sensor

14PCB×3electrodes=42taxels,각4.3cm. Front/left/rightbase를conductiveink-coatedfoam이덮고compression에따른capacitance를측정한다. (§II.B pp.2–3)

### 7.2. Preprocessing

Taxel별low-passfilter→threshold→timestampedcontacttransmission. Threshold수치는미명시. (§II.B p.3)

### 7.3. Policy Representation

1active taxel=pointcontact및해당위치;multiple= linecontact및양끝taxel위치평균. Controller에는2Dcontactpoint가전달된다. (§II.B p.3)

### 7.4. Retained Information

활성영역위치,point/line분류,대표contactlocation. (§II.B p.3)

### 7.5. Removed / Unavailable Information

Threshold후force/pressure의연속크기와방향은controller입력으로유지하지않는다. 양끝평균축약은전체activation pattern/내부분포를보존하지않음(구조상확인). 모든다중접촉이한line으로대표가능하다는일반검증은없다. (§II.B p.3)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지않음. SimulationGazebocontactsensor는wrench도출력하지만저자들이position만사용했다고명시한다. (§III.B p.5)

### 8.2. Representation

Noforce/wrenchpolicyinput;capacitivetouch의contactlocation만사용. (§II.B p.3; III.B p.5)

### 8.3. Role

해당없음. (§III.B p.5)

### 8.4. Required Assumptions

F/T-onlylocalization해당없음. Tactilelocation+knownrobotgeometry/odometry,holonomicbase,quasi-staticmotion가정. (§II.C p.3)

### 8.5. Reported Limitation / Ambiguity

원문에서F/T의해당한계를직접논의하지않음. (§IV pp.7–8)

## 9. Other Observations

Robotworldpose/odometry와predefinedworldgoal은필수다. Previousaction/sensorhistorywindow/RNN은없으며state machine의realignmentthreshold메모리는있다. Vision은제안RPS에없고APSbaseline에만있다. (§II.C pp.3–4; §III.B pp.5–6)

## 10. Tactile–Other Modality Relationship

| 추가정보 | Tactile정보 | Tactile에서없는정보 | 역할 | 근거 |
| --- | --- | --- | --- | --- |
| Robotodometry/worldgoal | 로봇상대contact위치 | Worldgoal까지거리/heading | 접촉좌표world변환,진행방향/종료결정 | Eq.(3) p.3 |
| Knownbase/taxelgeometry | Activetaxelindex | Metriccontactlocation | 점/line중점좌표와edge근접해석 | §II.B p.3 |
| Realignmentstate | Contactlateraloffset | 지속적인edge탈출동작 | Hysteresis로중앙복귀 | Algorithm1 p.4 |

NPS는tactile제거가아닌reactivecontrol구조제거비교다. Tactile+F/T sensorcombination비교는없다.

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
| Contact-reactive motion | Controlled comparison | RPS vs no-lateral/no-realignmentNPS vsAPS | Simulation144conditions:88.19% vs15.97% vs5.56%;sensor제거실험은아님 | §III.B pp.5–6; TableII p.6 |
| Realobject/goalrobustness | Controlled comparison | 2objects×8targets;proposedRPS | 100%보고;평균completion89sbox/88scylinder. Realbaseline비교없음 | §III.C pp.6–7 |
| Cylinderfailure | Failure analysis | Cylinder vs boxes | 낮은sim성공률원인으로rolling과boxline-contact안정성차이를저자가추정 | §IV pp.7–8 |

## 13. Author-stated Limitations

Simulation에서cylinder성공률이더낮고저자들은rolling/linecontact안정성차이를가능원인으로든다. 현재목표는unknown-propertyobject의position운반이며orientationcontrol/obstacleavoidance는향후확장이다. Quasi-static및unclutteredenvironment범위를명시한다. (§II.C p.3; §I p.2; §IV pp.7–8)

## 14. Author-stated Future Work

Objectpose제어및주변obstacle회피로확장하며objectshape/size와vision 기반obstacle/orientation정보가추가로필요하다고명시한다. (§IV p.8)

## 15. Review-relevant Findings

- 42taxels를threshold한후representativecontactpoint로축약한다.
- Currentobjectcenter/orientation은없지만robotworldpose/goal은제공된다.
- Gazebowrench는명시적으로사용하지않는다.
- 성공의0.05m는contactpoint–goal거리다.
- Binarytactile와F/T결합효과는평가하지않았다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation/Objectpose | Algorithm1 p.4; Eq.(3) p.3 |
| Tactile | §II.B pp.2–3 |
| F/T | §III.B p.5:출력중position만선택 |
| Controller | §II.C pp.3–4 |
| Reward/Critic | 비-RL,해당없음 |
| Comparison | §III.B–C pp.5–7; TableII p.6 |
| Limitation/Future | §IV pp.7–8 |
