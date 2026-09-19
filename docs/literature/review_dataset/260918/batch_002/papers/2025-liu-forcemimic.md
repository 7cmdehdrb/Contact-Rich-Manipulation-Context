# ForceMimic: Force-Centric Imitation Learning with Force-Motion Capture System for Contact-Rich Manipulation

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B049`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Wenhai Liu; Junbo Wang; Yiming Wang; Weiming Wang; Cewu Lu
- Year: 2025
- Venue: IEEE ICRA 2025, pp.1105–1112
- DOI / arXiv: 10.1109/ICRA55743.2025.11128061 / Not stated
- PDF version: Publisher version
- Page count: 8
- SHA-256: `3d03855b800a8ca9c897a37b1766436a30d55f04e3780659d59497d27ea870f2`
- PDF filename: Liu 등 - 2025 - ForceMimic Force-Centric Imitation Learning with Force-Motion Capture System for Contact-Rich Manip.pdf
- 확인 범위: PDF pp.1–8 전체(본문 pp.1–6, 참고문헌 pp.7–8); Fig.4 및 Table I/Figs.6–7을 렌더 확인. 별도 부록 없음.

## 2. Relevance to This Review

`Relevant`

시각 경로의 접촉 오차를 force control로 보완하는 모방학습 연구다. 특히 제안 정책의 force 출력과 저수준 force feedback을 구분하며, force를 정책 입력에 추가한 비교군이 오히려 실패하는 사례를 제시한다. Tactile 병용 연구는 아니지만 추가 센서 정보의 역할과 배포 시 입력 분포 문제에 직접 근거를 준다.

## 3. Task

Flexiv Rizon 4 두 팔로 zucchini를 고정하고 peeler로 껍질을 벗긴다. 왼팔은 규칙 기반 고정, 오른팔은 학습 peeling을 수행한다. 성공은 손상 없이 어떤 길이든 벗기는 motion-correct 조건과 연속 껍질 길이 10 cm 초과 조건을 각각 평가한다. [§IV-B, PDF p.5]

## 4. Method

### 4.1. Overall Pipeline

ForceCapture의 RGB-D·SLAM pose·6축 wrench demonstration → point cloud/TCP pose/중력 보정 wrench로 변환 → diffusion policy → 미래 pose와 wrench → 예측 force에 따른 primitive 선택 → Flexiv RDK IK 또는 hybrid force-position control. [Fig.2, PDF p.3; §III-B–C, pp.4–5]

### 4.2. Observation

제안 HybridIL의 policy 입력은 MLP가 인코딩한 point cloud와 robot TCP pose이며 Fig.2 caption은 history pose를 명시한다. Wrench는 예측 대상 및 controller의 force tracking에 사용되며, 제안 policy 입력에 측정 force가 포함된다고 쓰면 안 된다. Force DP와 Force+Hybrid DP 비교군에만 측정 robot force 입력을 추가한다. 현재 object pose는 별도 벡터로 입력하지 않는다. [Fig.2, p.3; §III-C, p.4; §IV-B(b), p.5]

### 4.3. Action

다음 20 timestep의 pose와 wrench parameters를 예측한다. Fig.2의 실행 인터페이스는 t:t+10 구간을 표시한다. 이는 current object pose가 아니라 robot TCP의 목표 trajectory와 interaction wrench다. [Fig.2, p.3; §III-C/Fig.4, p.4]

### 4.4. Controller

예측 force가 6 N 미만이면 IK joint-position primitive, 연속 step에서 6 N을 넘으면 hybrid force-position primitive를 선택한다. 예측 pose 전후점으로 motion direction을 구하고 force를 그 직교 평면에 투영한다. 초기 미접촉 시 force-control 방향 반대로 pressing하여 접촉을 만든다. Flexiv RDK를 사용하지만 실행 wrench의 물리 sensor/estimation source와 control loop rate는 원문에서 특정하지 않는다. [§III-C, pp.4–5]

### 4.5. Learning / Optimization Method

Diffusion Policy 기반 supervised imitation learning, pose와 wrench에 대한 MSE 학습 구조(Fig.2). 15개 zucchini에서 438 skill segment, 30,199 action sequence를 수집했고 action을 perception보다 3 timestep 앞당겼으며 모든 방법을 500 epoch 학습했다. RL이 아니다. [Fig.2, p.3; §IV-B, p.5]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | 매 시점 RGB-D에서 얻는 point cloud의 암묵적 공간 정보; 명시 object position vector 없음 | Point cloud 갱신; object pose tracker 없음 | TCP pose와 고정 초기 TCP 조건은 current object position이 아니다. [§III-B–C, PDF pp.4–5] |
| Orientation | 기타 | Point cloud에 포함되는 암묵적 외형; 수치 object orientation 없음 | 시각 입력 갱신 | SLAM은 수집 장치 pose이지 object pose가 아니다. [§III-B–C, PDF pp.4–5] |
| Shape / Geometry | Tracking | RGB-D backprojection point cloud; object와 EEF 부분 유지, 10,000으로 voxelization | 관측 point cloud 갱신 | Full mesh/CAD는 policy 입력으로 명시하지 않는다. [§III-B–C, PDF pp.4–5] |
| Physical Parameters | 미제공 | Object mass/friction 등 입력 미명시 | 해당 없음 | Tool weight/CoM은 수집 wrench 중력 보정용으로 추정하며 object parameter와 다르다. [§III-B–C, PDF pp.4–5] |

## 6. Missing Object Information and Compensation

불완전한 시각 안내 및 pose trajectory의 접촉 오차 → demonstration에서 예측한 wrench와 실행 force tracking → 껍질에 접촉하고 과도한 힘을 줄이는 제어. 이는 저자의 동기와 비교 실험에 근거한다. 반대로 측정 force를 actor에 추가하는 것만으로 보완이 성립하지 않았으며 deployment/data force 분포 불일치가 실패 원인 후보로 논의된다. [§I, pp.1–2; §IV-B, pp.5–6]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§III-B–C, PDF pp.4–5]

### 7.2. Preprocessing

사용하지 않음. [§III-B–C, PDF pp.4–5]

### 7.3. Policy Representation

사용하지 않음. [§III-B–C, PDF pp.4–5]

### 7.4. Retained Information

사용하지 않음. [§III-B–C, PDF pp.4–5]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§III-B–C, PDF pp.4–5]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

수집: handle과 tool/gripper 사이 6축 F/T sensor. 실행: Flexiv Rizon 4의 force sensing/control 기능을 사용하지만 wrist sensor인지 joint-torque estimated wrench인지 명시하지 않는다. 두 출처를 동일시하지 않는다. [§III-A–B, pp.3–4; §IV-B, p.5]

### 8.2. Representation

수집 wrench는 3축 force+3축 torque. 1000 Hz F/T, 200 Hz T265, 30 Hz L515를 L515 시간축에 정렬한다. Quasi-static 가정하에 tool 중력만 보정한다. Policy는 wrench trajectory를 출력하고 controller는 motion에 직교한 predicted force를 사용한다. [§III-B–C, PDF pp.4–5]

### 8.3. Role

학습 label/출력 목표, primitive 전환, 접촉 형성, force tracking. 제안 policy의 measured-force observation은 아니다. 비교군 Force DP/Force+Hybrid DP에서만 추가 observation이다. [§III-B–C, PDF pp.4–5; §IV-B, pp.5–6]

### 8.4. Required Assumptions

수집 시 quasi-static하여 tool 관성은 무시하고, pose–wrench 표본으로 tool weight/CoM을 least-squares 추정한다. 센서/카메라/EEF 좌표 변환을 보정한다. Force와 motion 제어축은 직교시킨다. Contact localization은 수행하지 않는다. [§III-B–C, PDF pp.4–5]

### 8.5. Reported Limitation / Ambiguity

측정 force의 dataset/deployment 분포 불일치가 sensory-input policy 실패의 원인 후보다. Net wrench의 multiple-contact/location ambiguity는 직접 논의하지 않는다. [§IV-B, p.6]

## 9. Other Observations

Vision: L515 RGB-D를 background/EEF 기준으로 필터한 point cloud. Proprioception: current/history TCP pose. History 길이 및 recurrent state는 미명시. Previous action 입력은 미명시. T265는 demonstration 수집 장치 pose tracking용이며 실행 object tracker가 아니다. Goal pose는 policy가 생성하는 EEF 미래 목표다. [Fig.2, p.3; §III-B–C, p.4]

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않는다. Vision은 위치·외형을 제공하고 wrench 출력과 controller는 접촉 하중을 조절한다. Sensor input ablation은 force 병용의 일관된 향상을 보이지 않으므로 상보성의 일반적 입증으로 해석할 수 없다. [§IV-B, pp.5–6]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | Demonstrated TCP pose와 wrench가 supervised label이다. Simulator GT 기반 actor/critic/reward/termination/curriculum은 해당 없음. [§III-C/§IV-B, pp.4–5] |
| Critic | Not applicable | 비-RL | Demonstrated TCP pose와 wrench가 supervised label이다. Simulator GT 기반 actor/critic/reward/termination/curriculum은 해당 없음. [§III-C/§IV-B, pp.4–5] |
| Reward | Not applicable | 비-RL | Demonstrated TCP pose와 wrench가 supervised label이다. Simulator GT 기반 actor/critic/reward/termination/curriculum은 해당 없음. [§III-C/§IV-B, pp.4–5] |
| Termination | Not applicable | 비-RL | Demonstrated TCP pose와 wrench가 supervised label이다. Simulator GT 기반 actor/critic/reward/termination/curriculum은 해당 없음. [§III-C/§IV-B, pp.4–5] |
| Curriculum | Not applicable | 비-RL | Demonstrated TCP pose와 wrench가 supervised label이다. Simulator GT 기반 actor/critic/reward/termination/curriculum은 해당 없음. [§III-C/§IV-B, pp.4–5] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Wrench 출력+hybrid control이 peeling을 개선 | Controlled comparison | Raw DP vs HybridIL; 각각 20회 | Motion correct 80%→100%; length>10 cm 55%→85%. 입력 force 추가가 아닌 출력/제어 방식 비교. | §IV-B; PDF pp.5–6 ; Table I ; Figs.6–7 |
| Force를 policy input에 추가하면 항상 유리하지 않음 | Input ablation | Raw DP / Force DP / Force+Hybrid DP / HybridIL; 비교군은 10회 | Length>10 cm: 55/10/20/85%. Force-input 두 방법은 contact 이후 예측에 어려움. | §IV-B; PDF pp.5–6 ; Table I |
| Force-input 실패의 분포 불일치 설명 | Failure analysis | Dataset 약 10 N; Raw DP 약 20 N, 일부 40 N 초과; HybridIL 약 9 N | 저자는 controller 차이와 남은 distribution mismatch를 원인 후보로 설명; 인과 분리 실험은 없음. | §IV-B; PDF p.6 ; Fig.7 |

## 13. Author-stated Limitations

간단한 MLP representation, 두 개 control primitive, 단일 peeling skill로만 검증했다. Force를 sensory input으로 활용하는 문제는 미해결이며, HybridIL도 예측 force-position 조기 종료에 따른 primitive 전환으로 peeling이 끊겼다. [§IV-B/§V, PDF p.6]

## 14. Author-stated Future Work

향상된 multimodal representation, 더 다양한 또는 정책이 직접 선택하는 primitive, 다른 force-oriented task로 확장, force sensing 입력과 control strategy 통합 및 data/deployment 차이 해결을 제안한다. [§IV-B/§V, PDF p.6]

## 15. Review-relevant Findings

- 제안 HybridIL은 vision point cloud와 TCP pose를 입력받고 force/wrench를 출력한다.
- Measured force 입력 비교군의 성능 저하는 추가 입력의 유용성이 분포와 제어 방식에 의존함을 보여 준다.
- 수집 6축 F/T와 실행 Flexiv force source는 별도로 기록해야 한다.
- Tactile 및 F/T contact localization 실험은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | Fig.2 p.3; §III-C p.4; §IV-B(b) p.5 |
| Object pose / geometry | §III-B–C p.4 |
| Tactile | §III–IV pp.3–5: 사용하지 않음 |
| F/T / controller | §III-A–C pp.3–5 |
| Reward / Critic | 비-RL; §III-C |
| Ablation / failures | Table I/Figs.6–7 p.6 |
| Limitation / Future | §IV-B/§V p.6 |
