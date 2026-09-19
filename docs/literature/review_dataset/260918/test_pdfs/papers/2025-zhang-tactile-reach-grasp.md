# The Role of Tactile Sensing for Learning Reach and Grasp

[검증 데이터셋](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `T03`
- Authors: Boya Zhang; Iris Andrussow; Andreas Zell; Georg Martius
- Year: 2025
- Venue: IEEE International Conference on Robotics and Automation (ICRA), 11817–11824
- DOI / arXiv: [10.1109/ICRA55743.2025.11127409](https://doi.org/10.1109/ICRA55743.2025.11127409); arXiv 미명시
- PDF version: publisher version. 첫 페이지의 conference·DOI와 인쇄 쪽수로 식별.
- Page count: 8. 아래 PDF pp.1–8은 인쇄 pp.11817–11824에 대응.
- SHA-256: `1ef0c13a3811f5228d4ca839620271751947f84d4bdbf5d5a33df7f443f3535c`
- 원문 범위: 제공 PDF 전체 8쪽을 페이지 영상으로 판독. 본문 text layer가 추출되지 않아 그림·표를 포함한 원문 페이지를 직접 확인했다. 별도 Appendix 없음. 인용된 센서 논문과 외부 코드는 미검토.

## 2. Relevance to This Review

**Relevant.** Binary contact, force magnitude, 3D force vector와 공간 분해능을 바꾸어 촉각 표현을 비교한다. 불완전한 시각 Pose, proprioception, observation history와 촉각을 함께 사용해 각 표현의 이득을 평가한다. 손가락 전체 합력과 영역별 촉각을 함께 주는 비교는 축약 정보의 차이를 분석하는 직접 근거다. 다만 wrist F/T+tactile 연구가 아니며, blind grasping은 future work다. [§III–V, PDF pp.2–6]

## 3. Task

Franka Panda + 2-finger antipodal gripper의 tabletop reach-and-grasp. 물체에 접근하여 안정적으로 파지하는 것이 목표다. 학습 종료 후 들어 올리고 유지하면서 물체에 random force를 가하는 stability check를 수행하며, 물체가 손에 남는 시간 비율을 terminal grasp reward로 계산한다. Simulation의 강한 stability check와 실물 picking success는 동일한 평가 절차라고 단정하지 않는다. [§III-A, p.2; §IV-E, p.6]

## 4. Method

### 4.1. Overall Pipeline

```text
TCP pose + gripper opening + 시각 상태 + tactile representation + 남은 step
→ SAC 또는 MPO policy (MLP)
→ arm joint positions + gripper opening command
→ 실물 joint impedance controller의 보간
→ robot/gripper command

주요 시각 경로: sim current object pose + object one-hot ID
실물: FoundationPose current object pose estimate
일반화 실험: wrist RGB → pretrained image encoder → visual representation
```

실험별 시각 입력을 하나의 조건으로 합치지 않는다. [§III-A·IV-A/D/E, pp.2·4–6; Tables II·IV]

### 4.2. Observation

| 수신부/조건 | 입력 | 비고 |
| --- | --- | --- |
| Actor 공통 | TCP Cartesian pose, gripper opening, tactile state, remaining-step scalar | Joint position action과 달리 joint state 전체를 observation으로 제시하지 않음 |
| 주요 pose-input 실험 | Current object position/orientation + one-hot identity | 이상적 GT pose 또는 noise를 더한 pose. Actor가 object pose를 계속 받음 |
| 실물 pose-input 실험 | FoundationPose object pose | Object pose 추정이 실행 경로에 존재. 입력 mesh/template 구성은 본 논문에 미명시 |
| RGB 일반화 실험 | Wrist RGB의 image-encoder feature | 명시적 pose+ID 표현을 영상 표현으로 변경 |
| Critic | SAC/MPO를 사용하나 Actor 대비 상세 입력 계약은 미명시 | 별도 privileged critic을 가정하지 않음 |
| Controller | Joint-position targets 및 실행에 필요한 robot feedback | Controller 상태와 Actor observation을 구분 |

Visual history는 주요 실험 5 frames, 길이 비교 1/5/10, RGB 일반화는 Table II에 10으로 명시한다. 이를 tactile history 5 frames로 옮겨 적지 않는다. [§III-A·IV-A/B/D/E, pp.2·4–6; Tables II–IV]

### 4.3. Action

Arm의 모든 joint position과 gripper opening width. 7-DoF Panda이므로 7개 arm joint와 1개 gripper 명령에 대응한다. Delta action인지 absolute target인지 추가 구현 상세는 미명시이며, 원문의 joint-position command를 그대로 기록한다. [§III-A–B, pp.2–3]

### 4.4. Controller

실물은 policy 20 Hz 출력을 joint impedance controller로 1,000 Hz에 보간한다. Action moving-average filter와 17 ms delay를 학습에 넣어 관측·실행 지연을 모사한다. Controller parameter와 friction을 randomization한다. Simulation의 상세 low-level gain과 force reconstruction 내부 알고리즘은 미명시. [§III-B, p.3; §IV-E, p.6]

### 4.5. Learning / Optimization Method

SAC와 MPO(Maximum a Posteriori Policy Optimization)를 사용한다. MLP 설정은 Table IV에 제시한다. Precomputed grasp trajectory를 replay buffer에 채우는 demo injection으로 학습을 가속한다. Isaac Gym parallel simulation, 조건별 4–8 seeds 사용. Main reward는 episode 끝의 stability check이며, auxiliary reward는 접근·접촉·파지 힘·과도한 힘 penalty다. [§III-A–B, pp.2–3; §IV, p.4; Tables I·IV]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking; 기타(RGB variant) | 주요 sim: GT 또는 noisy GT; 실물: FoundationPose; 일반화: RGB feature | 현재값을 step별 사용; pose/visual history 추가 | Absolute/relative reference frame의 세부 정의는 미명시. Goal position이 아님 |
| Orientation | Tracking; 기타(RGB variant) | Position과 같은 current object pose 경로 | step별 갱신 | 실물 object pose estimation 명시. RGB variant의 명시적 orientation 수치는 미제공 |
| Shape / Geometry | 기타 | 주요 실험의 one-hot object identity; RGB variant의 영상 외형·학습 prior | ID는 동일 물체 동안 고정; RGB는 갱신 | Actor의 full mesh/CAD 입력 없음. FoundationPose model 제공 방식은 미명시. Object ID를 full geometry로 등치하지 않음 |
| Physical Parameters | 미제공 | Actor 물성 입력 없음 | 없음 | Simulator rigid-body·mass assumption과 friction/controller randomization은 별도. Homogeneous mass distribution은 stable/grasp-pose 사전계산에 사용 |

분류 단위는 실험 조건이다. 이 논문 전체를 `Pose 미제공`으로 분류할 수 없다. [§III-A–C·IV-A/B/D/E, pp.2–6; Table II]

## 6. Missing Object Information and Compensation

```text
Visual current pose의 offset/시간적 noise
→ tactile + TCP pose/gripper opening + visual history
→ 접촉 후 local adjustment와 파지 판단 보완
   (저자가 조사 질문으로 명시; tactile representation 비교 수행)

영역별 제한된 tactile feature의 불충분한 force 정보
→ 손가락 전체 3D force vector V를 MK/VK에 추가
→ 일부 유사 상태의 결과 구분과 학습 개선
   (개선은 Fig.8 비교; causal explanation은 저자 가설)

Binary tactile에서 force magnitude/direction 미제공
→ 현재 object pose/ID·proprioception·visual history는 모든 조건에 병용
→ 병용 사실 확인. 각각이 Binary 손실을 복원한다는 개별 ablation은 없음
```

Visual history만으로 모든 perception noise를 보완할 수 없다고 보고한다. Pose 자체를 제거한 blind grasping 실험은 없다. [§IV-B–C·V, pp.4–6]

## 7. Tactile

### 7.1. Raw Sensor

실물은 손가락마다 하나씩 장착한 vision-based Minsight 2개다. 논문은 1,740 mm²의 all-around sensing, normal/shear force, 60 Hz를 설명한다. Sensor 내부 원시 영상 해상도와 영상→힘 복원의 상세 회로·학습 방법은 본문에 미명시다. Simulation은 각 센서를 45 cuboids + 5 spheres로 근사해 primitive별 net force vector 50개를 얻는다. 이 50개를 실제 Minsight의 taxel 수라고 쓰지 않는다. [§III-C, p.3; §IV-E, p.6]

### 7.2. Preprocessing

Simulation의 contact force들을 전체 센서 또는 선택한 K개 영역으로 집계한다. 각 영역에서 contact 여부(B), gross-force magnitude(M), 3D force vector(V)를 만든다. K=5/9/12는 단순 해상도만 아니라 inner/back 등 coverage도 바꾼다. Binary의 수치 threshold, normalization, 실물 force reconstruction의 상세는 미명시. [§III-C, p.3; Fig.3; Tables II–III, p.5]

### 7.3. Policy Representation

| 기호 | 표현 | 두 손가락의 차원 | 남는 공간 구분 |
| --- | --- | --- | --- |
| E | Tactile 없음 | 0 | 없음 |
| B | 손가락별 전체 binary contact | 2 | 어느 손가락인지 |
| M | 손가락별 전체 force magnitude | 2 | 어느 손가락인지 |
| V | 손가락별 전체 3D force vector | 6 | 어느 손가락인지 |
| BK | K개 영역의 binary contact | 2K | 선택 영역별 접촉 |
| MK | K개 영역의 force magnitude | 2K | 선택 영역별 크기 |
| VK | K개 영역의 3D force vector | 6K | 선택 영역별 크기·방향 |

MK+V, VK+V는 전체 force vector를 추가한 비교다. Full-range 고해상도 force map은 sensor abstraction에서 소개하지만 Table II–III의 주요 정책 비교를 raw tactile image policy로 기록하지 않는다. [§III-C·IV-C, pp.3·5]

### 7.4. Retained Information

- B/BK: contact presence와 손가락/선택 영역 식별. [원문 명시]
- M/MK: 해당 집계 영역의 force magnitude. V/VK: 3D force magnitude와 direction. [원문 명시]
- BK/MK/VK: 선택 영역 배치에 따른 거친 spatial contact pattern. [Representation 구조상 직접 확인 가능]

### 7.5. Removed / Unavailable Information

- B/BK에는 연속 힘 크기·방향이 없다. M/MK에는 force direction이 없다. [Representation 구조상 직접 확인 가능; Table III]
- B/M/V는 센서 내부 접촉 위치·분포를 명시적으로 보존하지 않는다. BK/MK/VK도 영역 내부 세부 분포를 제공하지 않는다. [집계 구조상 직접 확인 가능]
- K개 영역이 덮지 않는 sensing surface의 상세 contact는 제한된다. Coverage와 수량을 함께 바꾼 실험임을 유지한다. [Fig.3]
- 저자는 Binary만으로 internal/external touching이 모호할 수 있다고 설명한다. [원문 명시; §IV-B, p.5]
- Raw image에 있던 texture·deformation 중 정확히 무엇이 제거되는지는 이 PDF의 sensor 변환 명세만으로 판단 불가. 다른 Minsight 논문의 정보를 채워 넣지 않는다.

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

**Fingertip tactile-derived force**다. Minsight 및 그 simulation abstraction의 force를 사용한다. 별도의 wrist 6-axis F/T 또는 joint-torque estimated wrench는 사용하지 않는다. Single-unit abstraction이 finger-base force/torque sensor를 모사한다고 설명하지만 실제 사용 표현은 3D force이며 moment는 없다. [§III-C, p.3; Table III, p.5]

### 8.2. Representation

손가락별 전체 또는 영역별 3D force, magnitude, binary로 변환한다. V의 6차원은 **3D force × 두 손가락**이며 한 센서의 force 3 + moment 3이 아니다. Force derivative/history/impulse를 Actor 입력으로 제시하지 않는다. [Table III, p.5]

### 8.3. Role

Policy observation으로 파지 접촉의 힘 크기·방향을 제공한다. Reward에도 finger force 방향·크기와 과도한 힘 penalty를 사용한다. 저자는 force vector 방향이 antipodal grasp 안정성에 유용하다고 해석한다. Force 자체를 목표로 추종하는 별도 force controller나 force-based contact localization은 제안하지 않는다. [Table I·III; §IV-B·V, pp.2·5–6]

### 8.4. Required Assumptions

F/T-only 역문제는 해당 없음. 전체 finger force로 stability를 판단할 수 있다는 저자 설명에는 **finger가 대상 object에만 접촉한다는 조건**이 붙는다. 두 손가락 antipodal grasp, 제한된 in-hand 자유도, rigid collision simulation과 사전 정의 sensor geometry가 실험 맥락이다. 이를 임의 multi-contact·전신 wrench의 충분성으로 일반화할 수 없다. [§III-C·IV-B·V, pp.3·5–6]

### 8.5. Reported Limitation / Ambiguity

Binary의 internal/external touching ambiguity, local tactile의 sim-to-real distribution shift를 논의한다. 실제 sensor deformation을 무시한 rigid-body 모델도 한계로 든다. Net wrist wrench에서 multi-contact 위치·patch를 분리하는 문제는 원문에서 직접 논의하지 않음. [§IV-B/E·V, pp.5–6]

## 9. Other Observations

- Proprioception: TCP pose와 gripper opening. 모든 tactile 조건의 공통 입력이며 제거 비교는 없다. [§III-A, p.2]
- Vision: 주요 실험의 current object pose+one-hot ID, RGB 일반화 실험의 영상 feature, 실물 FoundationPose를 구분한다. [§IV-A/D/E]
- History: Visual observation 5 steps를 주로 사용, 1/5/10 비교. RGB variant는 Table II의 10. Tactile history 및 recurrent model은 미명시. [§IV-A/B·Table II]
- Previous Action: Actor 입력으로 명시되지 않음. Action moving-average filter는 제어 처리이며 previous-action observation과 다르다. [§III-A·IV-E]
- State Estimator: 실물 FoundationPose, RGB 실험 pretrained image encoder. [§IV-D/E]
- 기타: Remaining-step scalar. 명시적 goal pose 입력 없음. [§III-A]

## 10. Tactile–Other Modality Relationship

| 추가 정보 | Tactile이 제공하는 정보 | Tactile에서 부족한 정보 | 추가 정보의 역할 | 역할에 대한 원문 근거 |
| --- | --- | --- | --- | --- |
| Current object pose / vision | 접촉 후 contact/force | 전체 물체 위치·방향을 직접 주지 않음 | 전역 공간 단서. 주요 실험은 pose를 계속 공급 | §III-A·IV-A/B, pp.2·4–5. Tactile이 imperfect vision을 보완하는 방향으로 실험 |
| TCP pose / gripper opening | Contact/force | 로봇 자세·개구 상태 | 공통 proprioception. Binary 손실을 복원하는지 개별 검증 없음 | §III-A, p.2 |
| Visual history | 현재 tactile | Visual noise의 시간 맥락 | Perception memory 비교; history만으로 충분하지 않다고 보고 | §IV-B, Fig.5, p.4 |
| Per-finger total force V | MK/VK의 선택 영역 정보 | 영역 밖/집계 force 및 방향 단서 | 전체 force를 추가할 때 성능 개선. 유사 상태를 구분한다는 설명은 가설 | §IV-C, Fig.8, p.5 |

마지막 행은 같은 tactile force의 공간 집계 표현을 결합한 것이다. 독립적인 wrist F/T+tactile의 modality ablation이 아니다. 영역별 Binary + wrist F/T로 바꾸어도 같은 효과가 유지되는지는 이 논문의 직접 검증 결과가 아니다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | Yes, 주요 simulation pose-input 조건 | Current GT object pose 또는 noisy GT pose + object ID | GT가 학습 전용인 것이 아니라 sim actor 평가에도 입력됨. 실물은 FoundationPose로 대체. RGB variant는 명시적 pose GT 입력 없음 |
| Critic | 미명시 | SAC/MPO 학습은 명시, 별도 critic observation 명세 없음 | Asymmetric privileged critic이라고도, GT-free critic이라고도 단정하지 않음 |
| Reward | Simulation 상태·접촉 정보 사용 | Finger–object distance, 접촉 여부, force 관련 항, stability check의 object-in-hand/contact 유지 시간 | Actor tactile가 E/B여도 reward에 힘·접촉 정보 사용. 각 값의 API는 미명시 |
| Termination | 고정 episode 길이 명시; 추가 GT 종료 조건 미명시 | 끝난 뒤 lift/hold/disturbance stability check | 평가/reward의 성공 판단과 rollout 종료를 구분. 실물 episode 100 steps |
| Curriculum | Curriculum 미명시; geometry 기반 data generation 있음 | Stable/grasp pose 사전계산, demo injection, 물체/초기 Pose sampling, RGB encoder용 simulation data | Homogeneous mass assumption 사용. Encoder pretraining target/loss는 미명시 |

[§III-A–B·IV-A/D/E, pp.2–6; Tables I–II]

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| 완전한 pose 정보에서는 tactile 추가 이득이 제한됨 | Sensor ablation; Representation ablation | Ideal visual GT pose+ID, SAC/MPO, E vs tactile variants | 비슷한 in-distribution 성공률. Tactile가 항상 유리하다는 결과 아님 | §IV-A, Fig.4, p.4 |
| Imperfect vision에서는 force vector 표현이 도움 | Representation ablation | OU/offset pose noise에서 B/M/V/BK/MK/VK/E | 특히 offset 조건에서 V/VK가 유리. SAC/MPO 결과가 다르며 모든 noise 조건에서 큰 차이는 아님 | §IV-B, Fig.7, p.5 |
| Visual memory는 noise를 완전히 보완하지 못함 | Input ablation | 1/5 frames, 탐색적 10-frame 비교 | 5 frames가 더 좋은 결과, 10에서는 저하 보고 | §IV-B, Fig.5, p.4 |
| 선택 영역 force에 전체 force를 더하는 효과 | Representation ablation | K=5/9/12, MK 또는 VK vs 각각 +V; noisy vision, SAC | 전체 force 추가 시 개선. 논문은 VK+V가 V 단독 이상이라고 정리. Sensor coverage/수량도 함께 변함 | §IV-C, Fig.8, p.5 |
| 실물에서 force representation별 차이 | Representation ablation; Controlled comparison | Cola can, 20회, without disturbance; E/B/M/V/BK/MK, policy-only | 성공률 0/35/45/65/20/5%. 괄호 안 programmed-close 수치는 제외. 모든 물체에서 V가 최고인 것은 아님 | §IV-E, Table V, p.6 |
| 전체 finger force의 상태 구분 기여 | Author explanation only | Fig.8 결과 해석 | 유사 관측의 인과적 차이를 구분한다는 저자 가설. Contact configuration 복원 오차를 측정하지 않음 | §IV-C, p.5 |

실물 Table V에서 일부 조건의 괄호는 rollout 후 강제로 gripper를 닫는 별도 개입이다. Policy-only와 섞지 않는다. VK 실물 시험은 계산 자원 제한으로 제외되었다. [§IV-E, p.6]

## 13. Author-stated Limitations

- 비교는 대부분 단순화한 통제 환경이며 종합적 결론을 내리기 어렵다. [§V, p.6]
- Simulator가 실제 sensor deformation을 무시하고 rigid collision으로 고해상도 sensing을 근사한다. [§V, p.6]
- Hyperparameter·algorithm에 따라 qualitative outcome이 달라질 수 있다. Sim-to-real 변경 요인이 실물 평가에 영향을 준다. [§V, p.6]
- 제한된 계산 자원으로 visual-tactile feature의 online learning을 사용하지 않았고 VK의 실물 시험도 제외했다. [§IV-E·V, p.6]
- 저자는 낮은 성공률을 antipodal point-contact gripper 조건과 연결한다. Force vector가 공간 해상도보다 유용하다는 결과를 모든 hand/task로 일반화하지 않는다. [§V, p.6]

## 14. Author-stated Future Work

Active search와 information accumulation이 필요한 blind grasping, 그리고 multi-finger in-hand manipulation에서 결과가 어떻게 달라지는지 검토하는 방향을 제시한다. 별도 Conclusion 절은 없으며 Discussion에 명시되어 있다. [§V, p.6]

## 15. Review-relevant Findings

- Binary, magnitude, vector와 영역 구성을 직접 비교하지만 주요 실험에는 current object pose·ID와 proprioception이 함께 제공된다.
- Visual history와 tactile history를 구분해야 한다. 이 논문이 명시한 history는 visual이다.
- B/BK는 연속 하중·방향을 보존하지 않고 V/VK는 3D 힘 방향을 보존한다.
- 전체 finger force와 영역별 force 결합의 simulation 비교가 있다. Wrist 6-axis F/T 결합 실험은 없다.
- Sim actor가 GT/noisy GT object pose를 사용하는 조건과 raw-RGB 일반화 조건, 실물 estimated pose 조건이 다르다.
- Tactile 입력이 없는 조건에서도 reward는 접촉·힘 정보를 사용할 수 있다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §III-A, p.2; §IV-A/B/D/E, pp.4–6; Table II, p.5 |
| Object pose | §III-A, p.2; §IV-A/B, p.4; §IV-E, p.6 |
| Tactile | §III-C, Fig.3, p.3; Table III, p.5 |
| F/T | 별도 F/T 없음. Fingertip force: §III-C, p.3; Table III·Fig.8, p.5 |
| Reward | §III-A, Table I, p.2 |
| Critic | §IV, Table IV, p.4: SAC/MPO만 확인, critic input 상세 미명시 |
| Ablation | §IV-A–E, Figs.4–10·Table V, pp.4–6 |
| Limitation | §V Limitations, p.6 |
| Future Work | §V Discussion, p.6 |
