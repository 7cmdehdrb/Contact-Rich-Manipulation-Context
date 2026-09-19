# A residual reinforcement learning method for robotic assembly using visual and force information

[검증 데이터셋](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `T01`
- Authors: Zhuangzhuang Zhang; Yizhao Wang; Zhinan Zhang; Lihui Wang; Huang Huang; Qixin Cao
- Year: 2024
- Venue: Journal of Manufacturing Systems 72, 245–262
- DOI / arXiv: [10.1016/j.jmsy.2023.11.008](https://doi.org/10.1016/j.jmsy.2023.11.008); arXiv 미명시
- PDF version: publisher version. PDF의 저널·권·쪽·DOI로 식별.
- Page count: 18. 아래 `PDF p.`는 파일의 1부터 시작하는 페이지이며 인쇄 쪽수는 245–262.
- SHA-256: `861e2ce7fee3a3c2e59852e8e90bb9630063eaa176739dbf8398db962d1fca19`
- 원문 범위: 제공 PDF pp.1–18의 본문·그림·표·참고문헌. 별도 Appendix 없음. 연결 영상·코드는 이번 분석에 포함하지 않음.

## 2. Relevance to This Review

**Relevant.** 현재 물체의 명시적 Pose·Geometry를 실행 정책에 주지 않고 시각 특징과 손목 F/T를 서로 다른 제어 경로에 사용하는 조립 연구다. 시각은 공간 탐색을, 힘 피드백은 접촉 상호작용과 단계 판정을 담당한다. Modality 및 controller 비교가 있어 F/T의 실제 역할을 확인할 수 있다. Tactile은 사용하지 않으므로 Binary tactile의 보완이나 F/T–tactile 상보성의 직접 근거는 아니다. [§3–4, PDF pp.4–7; §5.2·6.1, pp.9·11–13]

## 3. Task

Peg-in-hole assembly를 reaching → searching/alignment → insertion으로 나눈다. 평면 위에서 다양한 peg·hole 형상, clearance, 초기 상대 위치·yaw 조건을 시험한다. Searching에서는 접촉을 유지하며 구멍을 찾고, insertion에서는 구멍 바닥과 안정적으로 접촉하면 완료로 판정한다. 성공 판정은 삽입 단계의 $F_z>F_d/2$이며, 물체 Pose 오차는 별도의 평가 지표에도 쓰인다. 임계값은 이 논문의 실험 설정이며 다른 연구의 안전 한계로 이전하지 않는다. [§3·4.1·4.5, pp.4·7–8; §5.2, p.9]

## 4. Method

### 4.1. Overall Pipeline

```text
Reaching: 현재 RGB → CNN → PPO actor → Cartesian pose increment → IK → joint position
Searching: 현재 RGB → CNN → PPO actor → pose increment
           F/T → explicit force control + admittance → increment 대체/보정
           결합 Cartesian command → IK → joint position
Insertion: F/T → force-based controller → IK → joint position
공통 단계 판정/안전 감독: F/T와 단계 이력, 명령 및 시간 제한
```

Searching의 z방향은 힘 제어로 대체하고 다른 방향의 시각 정책 출력을 admittance로 보정한다. F/T를 Actor와 연결해 end-to-end fusion한 구조가 아니다. [Fig.2–5·7; §4.1–4.4, pp.3–7]

### 4.2. Observation

| 수신부 | 실제 입력 | 역할·확인 범위 |
| --- | --- | --- |
| Actor | 현재 eye-in-hand RGB, 정규화된 3×240×320 입력을 CNN의 512차원 특징으로 변환 | 공간 탐색·상대 배치에 따른 action. 명시적 object pose, F/T, q, 이전 action, goal pose 입력 없음 |
| Critic | Actor와 공유하는 CNN의 같은 시각 특징 | 상태 가치 추정. 별도 privileged state 없음 |
| Force controller | 외력·모멘트, 목표 힘, position command와 운동 오차/내부 적분 상태 | 힘 추종·유연 반응 |
| IK/로봇 제어 | 최종 Cartesian 명령, 로봇 기구학 | 관절 위치 명령 변환. 세부 IK 초기값 전달은 미명시 |
| 단계 판정·안전 감독 | $F_z$, 전체 외력, action 크기, 속도·가속도 및 step | Actor observation과 구분 |

CNN 특징을 저자들은 peg–hole 상대 Pose 표현이라고 설명하지만, 명시적 6D pose 회귀 출력·정확도 검증은 제시하지 않는다. [§3·4.2–4.6, pp.4–8]

### 4.3. Action

PPO Actor action은 $[\Delta x,\Delta y,\Delta z,\Delta\alpha_z]$의 4차원 Cartesian increment다. 평면 실험이므로 회전은 z축 하나다. 전체 6D wrench 입력과 4D 학습 action을 혼동하지 않는다. [Eq.(2), p.4]

### 4.4. Controller

선택 행렬로 힘·위치 부분공간을 분리한 modified parallel force/position controller다. 표면 법선에는 feedforward explicit force control, 나머지 방향에는 admittance를 적용한다. TRAC-IK로 joint position을 계산하고 URScript/ROS 경로로 position-controlled UR10을 구동한다. 힘 제어 200 Hz, RL 30 Hz. Robotiq 2-finger-140 gripper와 ATI mini45가 사용된다. [§4.3, Eqs.(4)–(9), pp.5–6; §5.1, p.8]

### 4.5. Learning / Optimization Method

PPO의 공유 CNN + Actor/Critic 각각 2-layer MLP. Reaching/searching/insertion에 따라 보상과 정책 결합이 달라진다. PyBullet 학습 후 domain randomization으로 실물 이전하고 실물 fine-tuning도 별도로 평가한다. 물체·카메라 배치, 영상, action 등에 randomization을 적용한다. 미래의 multimodal Actor 학습 계획은 현재 구현과 구분한다. [§4.4–5.4, pp.6–11]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | RGB의 512차원 latent relative-pose feature | Reaching/searching에서 현재 영상 사용 | 숫자 current position은 Actor에 미제공. 시각 특징을 명시적 Tracking으로 집계하지 않음 |
| Orientation | 기타 | 같은 CNN feature | Reaching/searching에서 갱신 | yaw 조정 action이 있으나 orientation 수치 추정 출력은 없음 |
| Shape / Geometry | 기타 | RGB 외형 단서와 학습된 prior | 영상 갱신; CAD/mesh 수치 입력 없음 | 저자는 학습 후 기하 파라미터가 필요 없다고 설명. 평면과 task-frame 가정은 별도 존재 |
| Physical Parameters | 미제공 | Actor에는 물체 물성 입력 없음 | 없음 | Controller gain·목표 힘·마찰 관련 deadzone은 별도 설정. 실험 simulation friction 0.01, rigid objects를 Actor 관측으로 기록하지 않음 |

Goal: 실행 Actor의 goal-pose 입력은 없다. 학습 reward를 위한 hole/target reference와 목표 접촉력은 별도다. 실물에서는 teach pendant로 최종 target position을 얻는다. [§4.2·4.5·5.1–5.4·8, pp.5·7–9·11·17]

## 6. Missing Object Information and Compensation

```text
Actor에 명시적 current peg–hole pose와 geometric parameters 미제공
→ 연속 RGB의 object-centric feature
→ 공간 탐색과 정렬 action 생성 (저자 설명)

시각 action만으로 contact/friction을 처리하기 어려움
→ F/T 기반 해석적 force/admittance controller와 단계 구조
→ 접촉 유지, 외란 대응, 학습 action 탐색 공간 축소 (저자 설명 + controller 비교)
```

연속 시각을 제거한 Blind 정책의 사례가 아니다. 명시적 Pose 미입력과 시각 정보 부재는 다르다. 촉각 축약으로 잃은 정보를 보완했다는 주장은 해당 없음. [§4.4·7–8, pp.7·13·16–17]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. 손목 F/T를 분포형 tactile로 분류하지 않는다.

### 7.2. Preprocessing

해당 없음.

### 7.3. Policy Representation

해당 없음.

### 7.4. Retained Information

해당 없음.

### 7.5. Removed / Unavailable Information

해당 없음. Tactile 축약 실험이 없다.

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

EEF와 gripper 사이 ATI mini45 6-axis F/T. Simulation에도 6-DoF F/T를 사용한다. Joint torque estimated wrench가 아니다. [§5.1, p.8]

### 8.2. Representation

$[F_x,F_y,F_z,M_x,M_y,M_z]$. Median filter, dead zero, gripper·object gravity compensation을 거쳐 task frame에서 계산하고 robot base frame으로 변환한다. 시뮬레이션 x/y deadzone은 마찰 영향을 줄이도록 설정한다. 필터 window와 실물 bias/드리프트 정량치는 미명시. [§3·4.3·5.1, pp.4·6·8]

### 8.3. Role

표면 접촉 검출, reaching/searching/insertion 전환, 법선 힘 추종, 다른 방향의 admittance, 과부하 reset, 삽입 완료와 완료 보상에 사용한다. Actor observation에는 들어가지 않는다. 접촉점 위치를 역산하는 별도 estimator는 없다. [§4.1·4.3–4.6, pp.4–8]

### 8.4. Required Assumptions

최종 insertion의 force-only 단계는 앞선 시각 기반 탐색·정렬이 완료되었다는 조건에 의존한다. 평면 접촉면, 선택한 법선 z축, task/sensor/base 좌표 변환, 중력 보상, 미리 설정한 제어 gain·목표 힘·임계값이 사용된다. $F_z=0$을 정렬·삽입 진입 단서로, 이후 바닥 접촉을 완료로 해석하는 조립 단계 구조가 있다. 일반적인 F/T-only contact localization이나 임의 multi-contact 해법이 아니다. [§3–5.2, pp.4–9]

### 8.5. Reported Limitation / Ambiguity

Raw force의 noise·drift를 filter/dead zero로 처리한다고 명시한다. Contact force tracking 오차를 고려해 단계 임계값을 정하며, 더 섬세한 부품에는 active force precision 개선이 필요하다고 설명한다. Net wrench의 multi-contact 분리·contact patch ambiguity는 원문에서 직접 논의하지 않음. 관련 연구에서 force만으로 위치·외형을 포착하기 어렵다고 설명한 부분은 자체 localization 실험 결과와 구분한다. [§2.3·4.1·4.3·7, pp.3–4·6·17]

## 9. Other Observations

- Proprioception: Actor 입력에는 없음. Controller의 현재 pose/운동 오차와 IK/위치 제어 경로는 존재한다. 전체 joint-state input 명세는 미명시. [§4.3–4.4]
- Vision: RealSense SR305의 현재 RGB. RGB-D 장비를 쓴다고 depth가 최종 Actor 입력인 것은 아니다. [§4.2·5.1]
- History: Actor frame stack/RNN 미명시. Controller 적분 상태와 단계 상태는 존재하며 학습 sensor history와 구분한다. [§4.1·4.3–4.4]
- Previous Action: Actor 입력으로 제시되지 않음. [§4.4]
- State Estimator: CNN latent feature. 독립적인 object-pose estimator는 원문에서 확인되지 않음. [§4.2]
- Goal: Actor에는 explicit goal 없음. Controller의 desired force와 reward target은 별도. [§4.3·4.5·5.3]

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않아 해당 없음. 대신 시각과 F/T의 관계는 다음과 같다.

| 추가 정보 | Tactile이 제공하는 정보 | Tactile에서 부족한 정보 | 추가 정보의 역할 | 역할에 대한 원문 근거 |
| --- | --- | --- | --- | --- |
| RGB + F/T | 해당 없음 | 해당 없음 | RGB는 공간 탐색, F/T는 접촉 유지·상호작용 처리 | §4.4·7–8, pp.7·13·17. Controller 비교로 전체 결합 구조 평가 |

이 비교는 Binary tactile + wrist F/T 조합의 근거로 전환할 수 없다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | No | RGB → CNN feature | 실행 시 RGB 필요. Object pose GT 없음 |
| Critic | No | Actor와 공유한 RGB feature | 실행 시 Critic 불필요. 비대칭 GT critic 아님 |
| Reward | 추가 기하 상태 사용; GT 취득 경로 일부 미명시 | 단계별 relative distance·yaw·height, hole depth, force success/failure | Eq.(12)는 Actor에 없는 기하량 요구. Sim GT API와 실물 각 변수의 계산·측정 방법 전체는 미명시. 실물 target은 teach pendant로 설정. Reward는 배포 Actor에 불필요 |
| Termination | 별도 object GT 사용 확인되지 않음 | 삽입 후 force threshold; 과도한 force/action, step 한계 | 배포에도 F/T·안전 제한 필요. 위치 평가 지표와 구분 |
| Curriculum | 별도 curriculum 미명시; reset/randomization에 simulator 설정 사용 | 초기 상대 position/yaw, 형상·clearance, 카메라·동역학 설정 | 학습 환경 생성용. Actor 입력으로 전달한다고 쓰지 않음 |

[§4.4–5.4, pp.7–11; Algorithm 2, p.8]

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| 시각이 공간 탐색에 기여 | Input ablation; Failure analysis | Full Model vs RGB를 가린 No Vision | No Vision은 유효한 탐색·보상 획득에 실패했다고 보고. Table 2 성능표에서는 제외 | §5.2·6.1, pp.9·11; Fig.10, pp.12–13 |
| 분석적 접촉 제어의 구성에 따라 성능 차이 | Controlled comparison | 같은 시각 정책 계열의 Full Model / Vision+Admittance / Vision+Force Threshold. Square, 2×2×2 cm, clearance 0.1 mm, 각 20회 | 성공률 100% / 5% / 0%. 힘 입력 자체 제거만의 효과가 아니라 제어 구조 비교 | Table 2, p.13 |
| 시각과 힘의 역할 분담 | Author explanation only | spatial search와 contact/friction 처리 분리 | force policy가 action 공간 일부를 대체·수정해 탐색 공간을 줄인다고 설명. 역할별 정보량을 따로 검증한 실험은 없음 | §4.4·7–8, pp.7·13·17 |
| 실물 fine-tuning의 효과 | Controlled comparison | Square, 1 mm clearance, 각 조건 20회; Sim2Real vs retrained | 성공률 45%→95%, 성공 시간 25.6→15.5 s. 센서 조합 ablation 아님 | Table 3, p.16 |

Table 2의 높은 시뮬레이션 성공률을 실물 zero-shot 성능으로 인용하지 않는다.

## 13. Author-stated Limitations

- RGB가 밝기·색 분포에 영향을 받고 제한한 camera FOV 때문에 peg·hole 특징 추출이 불충분할 수 있음. [§7, pp.11·13]
- 수동 force gain 조정은 재질·경도가 바뀌는 조건에서 제한됨. Sim-to-real gap이 여전히 존재함. [§7, p.13]
- 평면 이외에서는 action 차원을 최대 6으로 늘려야 하며 학습 시간 증가가 예상됨. 섬세한 부품에는 더 정밀한 active force control이 필요함. [§7, p.17]

## 14. Author-stated Future Work

- Depth 영상 활용, 조립 부품을 강조하는 영상 전처리, 더 정밀한 force policy로 일반화 개선. [§7, pp.13·17]
- RL로 force control parameter를 자동 조절하고 variable-stiffness tasks를 수행. [§7–8, pp.13·17]
- 조립 시간 단축, visual·force·proprioceptive 데이터를 함께 RL observation으로 사용. 현재 Actor의 입력 구성과 구분. [§8, p.17]

## 15. Review-relevant Findings

- Explicit pose/geometry를 Actor에 주지 않아도 현재 RGB는 reaching/searching에서 계속 제공된다.
- Actor와 Critic은 시각 특징을 공유하며 F/T는 controller·단계 판정·안전 감독에 쓰인다.
- Reward에는 Actor에 없는 상대 기하량과 hole depth가 사용된다. 모든 변수의 GT 취득 경로가 명시된 것은 아니다.
- Force-only insertion은 앞선 정렬과 알려진 제어 축·단계 조건 위에서 수행된다.
- Tactile, Binary representation, F/T+tactile 조합의 검증은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §3·4.2·4.4, pp.4–7; Fig.4·7 |
| Object pose | §4.2, p.5; §4.5, pp.7–8; §5.3, p.11; §8, p.17 |
| Tactile | 사용하지 않음. §3–5.1의 입력·장비 목록, pp.4–8 |
| F/T | §4.1·4.3·5.1, pp.4–6·8; Eqs.(4)–(9) |
| Reward | §4.5, Eq.(12), pp.7–8 |
| Critic | §4.4, Fig.7·Eqs.(10)–(11), pp.6–7 |
| Ablation | §5.2·6.1, pp.9·11–13; Table 2, p.13 |
| Limitation | §7, pp.11·13·17 |
| Future Work | §7–8, pp.13·17 |
