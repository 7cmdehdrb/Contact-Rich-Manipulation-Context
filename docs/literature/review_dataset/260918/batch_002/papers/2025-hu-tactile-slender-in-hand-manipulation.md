# Dexterous in-hand manipulation of slender cylindrical objects through deep reinforcement learning with tactile sensing

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B028
- Authors: Wenbin Hu; Bidan Huang; Wang Wei Lee; Sicheng Yang; Yu Zheng; Zhibin Li
- Year: 2025
- Venue: Robotics and Autonomous Systems 186 (2025) 104904
- DOI / arXiv: 10.1016/j.robot.2024.104904 / 미명시
- PDF version: Elsevier published article; available online 30 December 2024
- Page count: 9
- SHA-256: `7c246d3600450a13c5244e4e95412e864b5e3f7ea4173b40d4d9334e587b3e0c`
- PDF filename: `Hu 등 - 2025 - Dexterous in-hand manipulation of slender cylindrical objects through deep reinforcement learning wi.pdf`
- 분석 근거: 선택 PDF 원문을 새로 읽었다. 기존 논문 상세 노트를 근거로 사용하지 않았다. PDF 9쪽 전체를 읽었다. Fig. 2–3의 hand·taxel 배치, Table 1과 Fig. 7–9의 simulation 결과, Fig. 10–12의 tactile sim-to-real·실물 시연, 결론의 Future Work를 렌더링해 확인했다.

## 2. Relevance to This Review

**Relevant**. 세 손가락의 384개 piezoresistive taxel을 Boolean contact로 바꾼 뒤 손가락별 3D contact-center, 즉 9차원으로 축약하여 PPO actor에 제공한다. Contact center, 3-bit finger contact, raw tactile, GT object pose 조합을 같은 network 규모에서 비교하므로 축약 tactile의 정보 보존·손실, proprioception 보완, training-only GT 경계를 직접 분석할 수 있다.

## 3. Task

고정된 wrist의 custom TRX hand가 이미 세 손가락으로 잡은 가늘고 긴 stick을 떨어뜨리지 않고 미끄러뜨리며, stick 끝점으로 line, circle, spiral, figure-eight 궤적을 그리도록 pose를 연속 추종한다. 네 궤적별로 별도 policy를 학습하며, 실물에서는 서로 다른 굵기·형상·무게·표면의 stick으로 정성적 전이를 확인한다. (§3.2/§4.2/§6, PDF pp.3–8)

## 4. Method

### 4.1. Overall Pipeline

세 fingertip의 tactile array를 per-trial offset 보정하고 고정 threshold로 Boolean화한다. 활성 taxel 좌표의 평균을 finger-local 3D contact center로 계산해 6개 finger-joint position, desired stick major-axis unit vector와 결합한다. PPO가 6개 joint displacement를 출력하며, 50 Hz high-level target을 1 kHz low-level position controller에 보낸다. Simulation에서는 joint dynamics·backlash를 calibration하고 object·dynamics·initial grasp를 randomize해 실물로 직접 전이한다. (§3–5/§6.3, PDF pp.3–7)

### 4.2. Observation

주 policy observation은 (a) 측정한 6개 controlled finger-joint position, (b) desired stick major-axis 3D unit vector, (c) 각 fingertip의 local 3D contact-center position 세 개다. Current stick pose·endpoint와 axial rotation은 주 actor 입력에 없다. 비교군에 GT object pose, GT pose+contact center, raw 128×3 tactile, GT pose+finger별 contact Boolean을 사용한다. (§4.4/§6.2, PDF pp.4/6–7)

### 4.3. Action

출력은 6개 controlled finger joint의 desired displacement다. TRX hand는 8개 actuated joint를 갖지만 J2·J5는 0에 고정한다. (§3.2/§4.4, PDF pp.3–4)

### 4.4. Controller

실물에서 high-level policy는 50 Hz로 target joint position을 보내고 low-level controller는 1 kHz로 실행한다. Simulation은 calibrated PD joint control과 modeled backlash/self-lock를 사용한다. 실제 low-level gain과 target displacement를 target position으로 누적·제한하는 세부식은 미명시이다. (§5.1/§6.3, PDF pp.4–5/7)

### 4.5. Learning / Optimization Method

PPO, tanh MLP 2×256, 8 million time steps를 사용한다. 각 궤적별 policy를 따로 학습한다. Simulation PD/backlash parameter는 trajectory matching과 CMA-ES로 식별하며, PD gains·passive stiffness/damping·stick weight/radius/friction·initial joint/object pose를 randomize한다. (§4.3/§5, PDF pp.4–6)

## 5. Object Information

실행 입력과 학습·평가용 정답을 구분한다.

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | 주 actor에 current stick position·endpoint를 제공하지 않음; simulation reward와 평가에는 GT endpoints 사용 | 실행 중 독립 object tracking 없음 | Desired endpoint trajectory가 actor 입력으로 명시되지 않고 궤적별 별도 policy를 학습한다. |
| Orientation | 기타 | Desired major-axis unit vector만 actor 입력; current axis와 axial rotation은 미제공 | Desired direction은 실시간 갱신; current orientation tracking 없음 | Major axis 주위 회전은 과업 정의에서 무시한다. |
| Shape / Geometry | 미제공 | 주 actor에 stick mesh·radius·length 입력 없음; training은 single simulated stick | 명시적 갱신 없음 | Local contact center와 joint state가 finger–object 관계를 간접 반영한다. |
| Physical Parameters | 미제공 | Mass·radius·friction은 training domain randomization 값이며 actor 입력이 아님 | 실행 중 추정값 없음 | 실물 novel stick 전이는 정성 시연만 보고한다. |

## 6. Missing Object Information and Compensation

Current object pose·endpoint·axial rotation과 물성은 actor에 직접 주어지지 않는다. 그 대신 finger joint position과 세 finger-local contact center가 현재 grasp/contact configuration을 나타내며, desired major-axis vector가 목표 orientation을 제공한다. Training에서는 mass·radius·friction 및 initial grasp를 randomize해 미제공 물성·초기 오차에 대한 robustness를 유도한다. 다만 object position 목표가 observation에 포함되는 방식은 원문에 명시되지 않았고, contact history나 recurrent state도 없다. (§4.4/§5.3/§6.2, PDF pp.4–6)

## 7. Tactile

### 7.1. Raw Sensor

각 fingertip에 128개 piezoresistive taxel, 총 384개. Taxel은 applied normal force에 비례하는 0–2 N 값을 100 Hz로 반환하며 initial touch sensitivity는 0.1 N이다. Curved array 위에 약 1 mm silicone compliance layer가 있다. Simulation taxel은 target-object contact Boolean을 반환한다. (§3.1–3.2, PDF p.3)

### 7.2. Preprocessing

실물 trial 전 no-contact 구간의 taxel 평균 $s'$를 offset으로 구해 $s(t)=\max(s^*(t)-s',0)$로 보정한다. 그 뒤 empirical fixed threshold보다 큰 taxel만 contact로 Boolean화한다. Threshold 선택에는 small tip이 달린 별도 F/T sensor로 taxel을 하나씩 눌러 얻은 sensitivity data를 쓴다. (§5.2/§6.3, PDF pp.5/7)

### 7.3. Policy Representation

각 fingertip에서 활성 taxel의 알려진 finger-local 3D position을 평균한다. 세 contact center를 합친 3×3=9D vector가 주 actor의 tactile representation이다. 비교군은 raw 128×3 Boolean tactile와 finger별 contact/no-contact 1×3 Boolean이다. (§4.4/§6.2, PDF pp.4/6)

### 7.4. Retained Information

손가락마다 접촉 영역의 중심 위치와 curved fingertip 위 sliding trajectory를 유지한다. 3-bit contact보다 공간 위치가 있고, 384D raw Boolean보다 압축된 표현이다. (§4.4/§6.2–6.3, PDF pp.4/6–7)

### 7.5. Removed / Unavailable Information

Thresholding은 force magnitude와 pressure 변화를 제거하고, centroid는 활성 patch의 크기·형상·다중 patch 구조를 하나의 평균점으로 축약한다. 저자는 rigid object에서는 binary가 가능하지만 continuous pressure distribution이 더 정밀한 조작에 유용할 수 있다고 밝힌다. Threshold 수치와 contact-center scale factor 수치는 미명시이다. (§4.4/§5.2/§7, PDF pp.4–5/8)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Policy execution에는 F/T를 사용하지 않는다. 별도 force–torque sensor를 tactile sensitivity·threshold calibration에만 사용하며 model, axis 수, range, sampling rate는 미명시이다. (§5.2, PDF p.5)

### 8.2. Representation

Small tip으로 taxel 하나씩 누른 F/T reference와 tactile reading의 관계를 기록하지만, calibration curve나 wrench vector를 actor representation으로 만들지 않는다. (§5.2, PDF p.5)

### 8.3. Role

실물 tactile threshold를 경험적으로 설정해 주변 deformation/noise 신호를 거르고 실제 contact signal을 통과시키는 offline 역할이다. Reward의 simulated per-taxel contact force는 이 F/T sensor measurement와 별개다. (§4.5/§5.2, PDF pp.4–5)

### 8.4. Required Assumptions

한 번에 taxel 하나를 누르는 calibration과 small tip이 해당 threshold 설정을 성립시키는 조건이다. Runtime contact localization은 tactile array geometry와 활성 taxel에서 얻는다. (§5.2, PDF p.5)

### 8.5. Reported Limitation / Ambiguity

F/T calibration sensor의 세부 사양·좌표계·numerical threshold·반복 수와 uncertainty는 미명시이다. F/T-only manipulation 또는 F/T–tactile fusion ablation은 수행하지 않는다. (§5.2/§6.2, PDF pp.5–6)

## 9. Other Observations

Measured finger joint position 6D와 desired stick major-axis unit vector 3D가 tactile contact center 9D를 보완한다. Observation history, recurrent state, previous action은 미명시이다. Real policy 50 Hz와 tactile hardware 100 Hz 사이의 sampling/holding 처리도 미명시이다. 주 실행에는 external vision이 없지만 simulation reward·termination·representation ablation에는 GT object pose가 등장한다. (§3.1/§4.4/§6.2–6.3, PDF pp.3–7)

## 10. Tactile–Other Modality Relationship

Tactile contact center는 각 손가락 표면의 공간적 접촉 위치를, joint proprioception은 finger configuration을, desired axis는 task goal orientation을 제공한다. F/T는 실행 modality가 아니라 tactile threshold calibration 도구다. Fig. 9는 contact-center, raw tactile, 3-bit contact, GT pose 조합을 비교하지만 proprioception 제거 실험은 없으므로 contact center 단독 효과가 아니라 공통 joint-state 위에 더한 표현 효과로 해석해야 한다. (§4.4/§6.2, PDF pp.4/6–7)

## 11. Training-only / Privileged Information

Actor·Critic·reward·termination·학습 데이터 생성을 따로 기록한다.

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | 주방법 No; 비교군 Yes | 주방법은 joint position+desired axis+contact centers. 비교군 (b)(c)(e)는 GT object pose를 observation에 사용 | GT-pose 비교군을 실물 배치 가능한 주방법으로 혼동하지 않는다. (§4.4/§6.2, PDF pp.4/6) |
| Critic | 미명시 | PPO를 명시하지만 critic observation과 asymmetric GT 입력을 설명하지 않음 | PPO라는 이유로 privileged critic을 추정하지 않는다. (§4.3, PDF p.4) |
| Reward | Yes | Current·desired stick axis와 두 endpoints의 GT error, simulated per-taxel contact-force sum, alive constant | Simulation object pose와 contact force가 학습 reward에 필요하며 actor 입력과 구분한다. (§4.2/§4.5, PDF p.4) |
| Termination | Yes | Stick geometry-center height가 미명시 threshold 아래면 drop으로 episode 종료 | Simulation GT object center height를 사용한다. 실물 자동 종료 조건은 미명시이다. (§4.5, PDF p.4) |
| Curriculum | 명시적 curriculum 없음; reset GT Yes | Sampled initial finger joint/object pose, collision/contact checks, randomized mass/radius/friction and joint dynamics | Policy 입력은 아니며 simulation reset·training distribution 생성에 사용한다. (§5.3/Algorithm 1, PDF pp.5–6) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Contact-center 축약 표현의 상대 성능 | Representation ablation; Controlled comparison | Contact center / GT object pose / both / raw 384D tactile / GT pose+3-bit finger contact | 동일 network 크기와 8M steps에서 contact-center policy가 Fig. 9의 최종 reward가 가장 높고 GT pose 추가는 더 개선하지 않는다. 본문은 3 runs, caption은 5 seeds로 반복 수가 불일치한다. | §6.2; PDF pp.6–7 ; Fig. 9 |
| Trajectory tracking과 goal generalization | Controlled simulation evaluation | Line/circle/spiral/eight, 각 10 episodes; circle speed/radius four novel settings | Training position error 0.83/0.97/2.32/1.16 cm, orientation error 1.80/1.92/5.90/2.36°. Novel circle settings position 1.19/1.41/0.85/1.61 cm, orientation 2.23/3.16/1.70/2.50°. | §6.1; PDF p.6 ; Table 1 ; Fig. 7–8 |
| Tactile sim-to-real behavior | Qualitative real-world comparison | Simulated vs real contact-center trajectories and active-taxel patches | Periodic contact motion과 contact 유지가 정성적으로 유사하나 initial stick pose가 달라 trajectory 일치를 기대하지 않으며, real patch margin은 deformation·sensitivity 차이로 더 불규칙하다. | §6.3; PDF p.7 ; Fig. 10 |
| Novel stick 전이 | Qualitative demonstration only | Single simulated training stick vs different shape/weight/surface real sticks | Fig. 11–12 snapshots로 실행을 보이지만 real endpoint를 얻기 어려워 성공률·tracking error의 정량 분석은 하지 않았다. | §6.3; PDF pp.7–8 ; Fig. 11–12 |

## 13. Author-stated Limitations

저자들은 실물 stick endpoint의 real-time position을 얻기 어려워 real policy performance의 정량 분석을 수행하지 않았다고 밝힌다. Tactile material deformation은 no-contact drift와 irregular contact margins를 만들며, fixed threshold가 잘못된 contact state를 낼 수 있어 매 trial calibration이 필요하다. Binary tactile은 rigid object 조작에는 가능하지만 pressure 변화·normal-force magnitude를 쓰지 못해 더 정밀한 조작과 더 다양한 물체에는 정보가 부족할 수 있다. Data는 confidential이다. (§6.3/§7/Data availability, PDF pp.7–8)

## 14. Author-stated Future Work

Tactile reading과 surface pressure 사이의 nonlinear relation을 모델링하고 continuous full tactile signal을 사용해 pressure distribution과 normal-force magnitude를 보존함으로써 더 정밀한 in-hand manipulation과 더 다양한 object로 확장할 계획이다. (§7, PDF p.8)

## 15. Review-relevant Findings

- Main actor는 current object pose 없이 6D joint position, desired axis 3D, contact-center 9D를 사용한다.
- 384개 taxel을 threshold한 뒤 세 centroid로 축약하므로 위치는 유지하지만 force magnitude와 patch structure는 제거한다.
- 3-bit finger contact는 너무 빈약하고 raw 384D는 같은 MLP·data budget에서 spatial information을 distill하기 어렵다는 비교가 있다.
- GT object pose는 representation ablation 및 reward·termination·reset에 사용되며 주 actor 입력과 구분된다.
- F/T는 runtime policy modality가 아니라 tactile threshold calibration에만 쓰인다.
- Fig. 9 반복 수는 본문 3 runs와 caption 5 seeds가 불일치하고, 실물 결과는 정량 평가가 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Hardware / tactile specification | §3.1–3.2, PDF p.3; Fig. 2–3 |
| Observation / action / reward | §4.3–4.5, PDF p.4 |
| F/T calibration / domain randomization | §5.2–5.3, PDF p.5 |
| Simulation tracking / representation ablation | §6.1–6.2, PDF p.6; Table 1; Fig. 7–9 |
| Real transfer / sensor drift | §6.3, PDF p.7; Fig. 10–12 |
| Limitations / Future Work | §6.3–7, PDF pp.7–8 |
