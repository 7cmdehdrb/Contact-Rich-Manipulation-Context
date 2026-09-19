# Enhancing Tactile-based Reinforcement Learning for Robotic Control

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B057
- Authors: Elle Miller; Trevor McInroe; David Abel; Oisin Mac Aodha; Sethu Vijayakumar
- Year: 2025
- Venue: NeurIPS 2025
- DOI / arXiv: Not stated / 2510.21609v1
- PDF version: arXiv v1, 24 October 2025; NeurIPS 2025 header; Appendix A–H 포함
- Page count: 28
- SHA-256: e51421f53cd0d4b333b05f64adf74fc0f7a52e8ee48c4bbc1c07276a1d0573b2
- PDF filename: Miller 등 - 2025 - Enhancing Tactile-based Reinforcement Learning for Robotic Control.pdf
- 읽은 범위: PDF pp.1–28 본문 및 포함된 부록을 새로 확인; 핵심 표·그림 렌더링 확인

근거는 이번 배치의 PDF 원문이며 기존 상세 노트는 사용하지 않았다. 페이지는 PDF의 1-based page다.

## 2. Relevance to This Review

**Relevant**. Sparse binary contact와 proprioception/history를 결합하고 tactile 제거 및 자기지도 표현학습을 비교한다. Object pose 없는 actor·critic과 GT를 쓰는 reward/reset을 분리하여 검토할 수 있다. 모든 로봇 실험은 simulation이며 실물 전이 성과로 해석하지 않는다.

## 3. Task

RoTO의 Find는 고정 구를 20×20 cm 영역에서 찾고, Bounce는 10초 동안 구를 반복해서 튀기며, Baoding은 손 안의 두 구를 서로 회전시킨다. Find 300 step, 나머지 600 step이다. Bounce는 5 step 이상 비접촉 뒤의 접촉을 bounce로 센다. (§4 p.6; Appendix E pp.22–23)

## 4. Method

### 4.1. Overall Pipeline

Binary contacts + joint state + previous action의 k-frame history → shared MLP encoder → PPO policy/value → joint-position targets → joint position control. SSL decoder/forward model은 학습 때만 사용한다. (§3 pp.4–5)

### 4.2. Observation

Actor와 critic 모두 동일 latent z를 사용한다. Find: 2 contact bits, 이전 action 9, joint angle 9, velocity 9, EEF position 3, quaternion 4, gripper width 1로 한 프레임 37D 및 k=16. Bounce/Baoding: 17 bits, previous action 20, joint angle 24, velocity 24로 85D 및 k=4. Current object state와 vision은 입력하지 않는다. (Table A1 p.22; §3.1 p.4)

### 4.3. Action

Franka 9D, Shadow Hand 20D joint position action. Shadow의 24 joint 중 distal/proximal coupling 때문에 actuation은 20D다. (§4 p.6; Appendix E.2 p.22)

### 4.4. Controller

Physics 120 Hz, policy 60 Hz; joint position control. PD gain 등 세부는 미명시. (§4 p.6)

### 4.5. Learning / Optimization Method

PPO-clip에 TR(binary tactile reconstruction), FR(full reconstruction), FD(latent forward dynamics), TFD(FD+tactile reconstruction)를 비교한다. SSL은 sensor readings와 action으로 학습하고 auxiliary network는 배포 때 제거한다. FD에는 EMA target encoder를 사용한다. 별도 SSL memory를 최근 여러 rollout로 늘리는 실험도 있다. 5 seeds; no-last-action baseline만 1 seed다. (§3–5 pp.4–7; Appendix F–G pp.23–25)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Actor/critic에는 object position 없음 | 없음 | EEF position은 Find에서 제공하지만 물체 위치와 다름 (Table A1 p.22; §3.1 p.4) |
| Orientation | 미제공 | Object orientation 입력 없음 | 없음 | EEF quaternion은 Find의 robot proprioception (Table A1 p.22) |
| Shape / Geometry | 미제공 | Actor/critic에는 sphere radius/mesh 입력 없음 | 없음 | 실험은 정해진 sphere 형태이며 simulator의 크기·환경 설계는 prior (§4 p.6; Appendix E p.23) |
| Physical Parameters | 미제공 | Object mass/friction 수치 입력 없음 | 없음 | 실험용 공 물성은 simulator에 설정 (§4 p.6) |

## 6. Missing Object Information and Compensation

Current object pose/velocity 미제공 → binary tactile + proprioception + previous action + finite history 및 SSL → 접촉과 그 시간적 변화를 이용한 control representation 학습. 저자들은 proprioceptive control error가 접촉을 암묵적으로 감지할 수 있으나 decoupled dynamics, 작은 inertia, spatial/multiple-contact ambiguity에서 tactile이 유용하다고 해석한다. 이 네 설명은 모두 독립된 controlled experiment로 검증한 결론은 아니다. (§5–6 pp.6–9)

## 7. Tactile

### 7.1. Raw Sensor

Simulation Isaac Lab ContactSensor의 link net contact force. Franka finger 위 두 plate body, Shadow Hand 17 links; 실제 FSR 하드웨어 검증은 없다. (Appendix E.1 p.22)

### 7.2. Preprocessing

Net contact force를 binary화한다. Threshold 값은 미명시. Joint angle 정규화와 joint velocity scaling은 별도 proprioception 처리다. (Appendix E.1 p.22)

### 7.3. Policy Representation

2 또는 17 binary bits/frame을 다른 관측과 history stacking 후 MLP latent 256D로 인코딩한다. (§3.1 p.4; Table A1 p.22)

### 7.4. Retained Information

Sensor/link별 접촉 유무와 여러 step의 activation 변화. 공간 해상도는 sensor/link 구획 수준이다. (Table A1 p.22; Fig.1 p.2)

### 7.5. Removed / Unavailable Information

Binary 구조상 force magnitude/direction, link 내부의 세부 contact location·pressure distribution은 표현되지 않는다. 이는 representation 구조상 확인 가능한 손실이며 저자의 별도 손실량 실험은 아니다. (Appendix E.1 p.22)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. F/T-only localization 및 그 가정은 해당 없음. (Table A1 p.22)

### 8.2. Representation

사용하지 않음. F/T-only localization 및 그 가정은 해당 없음. (Table A1 p.22)

### 8.3. Role

사용하지 않음. F/T-only localization 및 그 가정은 해당 없음. (Table A1 p.22)

### 8.4. Required Assumptions

사용하지 않음. F/T-only localization 및 그 가정은 해당 없음. (Table A1 p.22)

### 8.5. Reported Limitation / Ambiguity

원문에서 F/T의 해당 한계를 직접 논의하지 않음. (Table A1 p.22)

## 9. Other Observations

Proprioception은 joint angle/velocity 및 Find의 EEF pose·gripper width를 제공한다. Previous action은 target과 실제 joint motion의 차이를 접촉 단서로 사용할 수 있게 한다는 저자 설명이 있다. History는 16 또는 4 frame이며 recurrent hidden state가 아니라 stacked observation+MLP다. 별도 explicit object pose estimator는 없다. SSL forward model은 학습용으로 배포 관측이 아니다. (§3.1 p.4; §5 p.6; Appendix E p.22)

## 10. Tactile–Other Modality Relationship

| 추가 정보 | Tactile이 제공하는 정보 | 부족한 정보 | 추가 정보의 역할 | 근거 |
| --- | --- | --- | --- | --- |
| Proprioception/previous action | link contact bits | 연속 robot motion 및 command error | 정규화 robot state와 previous target; 일부 접촉의 implicit inference | Fig.3 p.7; §5 p.6 |
| History/SSL | 접촉 activation | object motion의 순간적 비가시성 | 과거 센서와 latent dynamics로 state-related representation 형성 | Fig.4–6 pp.7–8 |

Wrist F/T 결합은 실험하지 않는다. Binary와 연속 tactile의 직접 representation 비교도 없다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부·비고 |
| --- | --- | --- | --- |
| Actor | No | Sensor history latent z | 배포 때 binary/proprioceptive history 필요; object GT 불필요 (§3.1 p.4; Table A1 p.22) |
| Critic | No | Actor와 동일 z; asymmetric privileged state 없음 | 학습용 value network (§3.1 p.4; Appendix F pp.23–24) |
| Reward | Yes | Find object–EEF distance; Baoding ball–target distances/rotation; Bounce contact timing와 fall distance | 학습용 simulator state. Sensor-only actor를 GT-free training으로 해석하면 안 됨 (Appendix E.3 pp.22–23) |
| Termination | Yes | Bounce/Baoding fall을 object distances로 판정; 시간제한도 적용 | Simulation episode reset용 (Appendix E.4 p.23) |
| Curriculum | Yes (reset/data generation) | Ball initial positions와 robot joints의 simulator randomization; 별도 curriculum은 미명시 | 학습 환경 생성. SSL target에는 object GT를 넣지 않음; MI 분석에만 GT state 사용 (Appendix E.4 p.23; §6 p.8) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Binary tactile의 task-dependent 효과 | Sensor ablation | PPO(prop-tactile) vs PPO(prop); no-last-action은 1 seed | Find 최종 성능 유사; Bounce 향상; Baoding은 proprio-only 실패에서 tactile로 성공. 수치 없는 곡선을 임의로 수치화하지 않음 | §5 pp.6–7; Fig.3 p.7 |
| SSL 효용 | Representation ablation | RL-only vs TR/FR/FD/TFD | TR·FD가 일관되게 개선; FR·TFD는 task-dependent | Fig.4 p.7 |
| Auxiliary memory 효용 | Controlled comparison | FD on-policy buffer vs larger separated buffer | Find/Bounce 효과 작고 Baoding 증가 | Fig.5 p.7 |
| Pose/velocity 관련 latent 정보 | Controlled comparison | 학습법별 reduced latent와 simulator state MI | FD가 일부 pose/velocity를 더 많이 인코딩; 반복 gait가 MI를 부풀릴 수 있음도 저자 명시 | §6 Q2; Fig.6 p.8 |
| 실제 물리 metric | Controlled comparison | SSL agents vs RL-only | Find 1.4 vs 1.9 s, Bounce 79 vs69회/10s, Baoding FD+memory 17 vs5회/10s 평균; 모두 simulation | §6 Q4; Fig.7 p.9 |

## 13. Author-stated Limitations

실물 하드웨어 검증 부재가 주된 한계다. SSL은 계산량을, 별도 auxiliary memory는 메모리 요구를 늘린다. 인간과 비교한 기록은 simulation 결과여서 실물에 그대로 전이되지 않을 것임을 명시한다. (§7 p.10; §6 Q4 p.9)

## 14. Author-stated Future Work

Tactile-only forward model로 FD/TFD 영향의 기전을 분리할 필요, off-policy data로 on-policy representation 학습 개선, BCE positive weighting을 nonstationary/contact-region frequency에 맞게 조정하는 방향을 제시한다. (§6 Q3 p.9, Q6 p.10; Appendix D p.18)

## 15. Review-relevant Findings

- Actor와 critic은 object GT 대신 binary tactile·proprioception·previous action history를 쓴다.
- Binary contact 제거 효과는 task마다 다르며 Baoding에서 크다.
- Reward와 fall/reset은 simulator object state를 사용한다.
- F/T 추가나 binary-vs-continuous tactile 우열을 직접 실험하지 않았다.
- 모든 로봇 조작 결과는 simulation이다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation/Object pose | §3.1 p.4; Table A1 p.22 |
| Tactile | Appendix E.1 p.22 |
| F/T | Table A1 p.22: 사용 없음 |
| Reward/Termination | Appendix E.3–E.4 pp.22–23 |
| Critic | §3.1 p.4; Appendix F pp.23–24 |
| Ablation | Fig.3–5 p.7 |
| Limitation/Future | §6–7 pp.9–10; Appendix D p.18 |
