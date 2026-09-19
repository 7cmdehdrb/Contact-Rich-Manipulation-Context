# Learning Visuotactile Estimation and Control for Non-prehensile Manipulation under Occlusions

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B020
- Authors: Juan Del Aguila Ferrandis; João Moura; Sethu Vijayakumar
- Year: 2024
- Venue: 8th Conference on Robot Learning (CoRL 2024)
- DOI / arXiv: 미명시 / 2412.13157v1
- PDF version: arXiv v1; 17 December 2024; CoRL manuscript with appendix
- Page count: 15
- SHA-256: `ecfad6c9a5839c38964246df185782ba7dae9b5de6ab8ab8c1ac30dbf5b0baae`
- PDF filename: `Ferrandis 등 - 2024 - Learning Visuotactile Estimation and Control for Non-prehensile Manipulation under Occlusions.pdf`
- 분석 근거: 선택 PDF 원문을 새로 읽었다. 기존 논문 상세 노트를 근거로 사용하지 않았다. 본문 pp.1–8, Appendix A–B pp.12–15를 읽고 Table 2 및 Fig.2–4를 렌더 확인했다.

## 2. Relevance to This Review

**Relevant**. 가려진 물체의 pose를 force·EEF pose·과거 시각 정보로 추정하고 불확실성까지 RL 정책에 제공한다. Privileged policy를 이용한 데이터 생성과 실제 배포 정책 입력이 명확히 다르다. 제목의 tactile은 여기서 wrist F/T 기반 force feedback이며 별도 촉각 배열과 혼동하지 않아야 한다.

## 3. Task

고정 크기 cuboid를 평면에서 밀어 목표 위치 1 cm, 목표 orientation 15° 이내로 이동한다. Workspace 이탈과 최대300step(20초) 미완료는 실패이다. 시각 가림이 시작되면 관측 object pose는 마지막 값에 고정되지만 state estimator는 계속 pose를 갱신한다. (§3–4, pp.3–6)

## 4. Method

### 4.1. Overall Pipeline

Occlusion-free simulator GT → 여러 학습 단계의 privileged PPO policy → 다양한 interaction trajectory → 가림/센서 noise 합성 → Bayesian recurrent pose estimator → 추정 pose·uncertainty를 포함해 PPO 재학습 → hardware 실행. (§3–4, pp.3–6)

### 4.2. Observation

Estimator 입력은 object pose 관측, EEF pose, EEF force, binary occlusion indicator이다. 가림 동안 object pose 관측은 마지막 검출값을 유지한다. 실행 actor는 관측에서 object pose를 estimator 출력으로 치환한 state와 uncertainty를 받는다. Goal은 과업 target이며 current pose와 구별한다. Target를 독립 policy channel로 제공하는 방식은 입력 정의에서 미명시이다. (§3.2–3.3, pp.4–5)

### 4.3. Action

x/y pusher velocity를 각11개 bin으로 선택하고 최대0.05 m/s, 15 Hz로 실행한다. (§4, p.5; Appendix B.1, pp.12–13)

### 4.4. Controller

KUKA iiwa + wrist F/T + spherical pusher. Pusher 위 camera에서 AprilTag pose를 얻는다. OpTaS로 EEF velocity를 joint configuration으로 변환한다. (§6, p.8)

### 4.5. Learning / Optimization Method

PPO actor/value는 LSTM recurrent architecture이다. Estimator는 1024-unit LSTM과 MLP로 planar pose (x,y,sinθ,cosθ) 및 diagonal aleatoric covariance를 예측한다. Likelihood loss와 test-time 50 MC dropout samples로 aleatoric/epistemic uncertainty를 합친다. 300 privileged checkpoints로 750,000 train trajectories를 수집하며 simulator mass/friction/restitution을 randomize한다. (§3–4; Appendix A–B, pp.12–15)

## 5. Object Information

실행 입력과 학습·평가용 정답을 구분한다.

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Onboard AprilTag vision; occlusion 중 recurrent force/pose estimator | 매 step 추정; 시각 관측은 가림 중 마지막 값 유지 | 배포 actor는 GT가 아닌 estimated x/y |
| Orientation | Tracking | 동일 estimator의 planar sinθ/cosθ | 매 step 추정 | 전체6D orientation이 아닌 planar yaw |
| Shape / Geometry | 기타 | 고정 cuboid 0.12×0.10×0.07 m; pusher radius0.013 m | 고정 prior; 갱신 없음 | 별도 geometry input channel은 없고 고정 geometry로 학습 |
| Physical Parameters | 미제공 | Simulator mass/friction/restitution randomization | actor에 정답 파라미터 제공 미확인 | LSTM이 hidden dynamics를 포착하도록 설계 |

## 6. Missing Object Information and Compensation

가림으로 current visual pose가 갱신되지 않음 → 마지막 visual pose + occlusion flag + EEF force/pose의 recurrent history → current object pose와 uncertainty를 추정한다.

추정 pose의 오차/불확실성 → estimator를 RL 학습 loop에 포함하고 uncertainty를 actor에 추가 → estimator 오차에 적응하며 접촉면을 바꾸는 행동이 관찰된다. 이는 저자의 설계와 실험 해석이다. Explicit uncertainty 유무 차이는94% 대92%이며 센서 자체의 제거 ablation으로 해석하지 않는다. (§3/5, pp.3–7)

## 7. Tactile

### 7.1. Raw Sensor

별도 피부/taxel/광학 촉각 센서 사용은 확인되지 않음. 저자의 tactile은 EEF force feedback을 가리키며 hardware source는 wrist F/T이다.

### 7.2. Preprocessing

Force observation은 각 성분을 ±10 N으로 clipping 후 10으로 나눈다. Tactile image threshold/binarization은 없다. (Appendix B.1, p.12)

### 7.3. Policy Representation

EEF force와 EEF pose·visual pose/occlusion flag의 recurrent representation. Binary 값은 occlusion indicator이며 contact tactile이 아니다.

### 7.4. Retained Information

Continuous force feedback 및 시간적 interaction 정보가 남는다.

### 7.5. Removed / Unavailable Information

공간적으로 분포된 contact patch/taxel 정보는 입력 목록에 없다. Binary tactile의 정보 소실 비교는 해당 없음.

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Wrist F/T sensor on KUKA iiwa. (§6, p.8)

### 8.2. Representation

논문은 EEF force fᵉ를 사용하고 성분별 ±10 N clipping/normalization을 명시한다. 정확한 축 수 및 moment 채널 사용 여부는 미명시이므로 6D wrench 입력으로 단정하지 않는다.

### 8.3. Role

Occlusion 중 pose estimation과 policy observation. Force control action이 아니라 velocity control이다.

### 8.4. Required Assumptions

고정 object/pusher geometry와 simulator dynamics 범위에서 수집한 충분한 interaction data, 이용 가능한 EEF pose 및 이전 시각 pose가 필요하다. F/T만으로 접촉점의 해석해를 구하는 방법은 아니다.

### 8.5. Reported Limitation / Ambiguity

실물 pusher dynamics 때문에 비접촉에서도 큰 force readings가 발생한다. Simulation은 이를 생략하고 noise randomization으로 대응했다. Net wrench multi-contact ambiguity는 직접 논의하지 않음.

## 9. Other Observations

Proprioception은 occlusion 없는 EEF pose/force이다. Vision은 onboard AprilTag current pose를 제공하되 가림 중 stale observation이 된다. Estimator와 actor/value 모두 recurrent state를 사용한다. Previous action 입력은 미명시이다. Fixed object geometry와 randomized dynamics가 학습 prior를 이룬다. (§3–4; Appendix A–B)

## 10. Tactile–Other Modality Relationship

별도 tactile + wrist F/T 병용 연구가 아니다. Force와 proprioception은 과거 시각 pose를 바탕으로 가림 중 pose를 추정하는 데 함께 쓰인다. Table 2의 vision baseline은 무처리 시각 pose이므로 force 제거만 통제한 sensor ablation은 아니다.

## 11. Training-only / Privileged Information

Actor·Critic·reward·termination·학습 데이터 생성을 따로 기록한다.

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | 배포 No; 데이터 생성 Yes | 배포 πest는 estimated object pose/uncertainty; πpriv는 GT environment state | 실행 중 simulator GT 불필요. Teacher와 배포 actor를 구별 (§3.2–3.3/4, pp.4–6) |
| Critic | 미명시 | Value network의 LSTM architecture는 명시; 별도 asymmetric GT 입력은 미명시 | 동일 architecture만으로 동일 입력/GT 부재를 확정하지 않음 (Appendix B.1, p.13) |
| Reward | Yes | Simulator current pose와 target의 거리/회전오차, pusher velocity, 성공/이탈 reward | 학습용이며 배포 actor 입력이 아님 (§4, p.5) |
| Termination | Yes | Simulator object/pusher workspace 경계와 target 달성; max horizon | 실물 목표 성공 판정과 학습 종료 GT를 구별 (§4, p.5; Appendix A, p.12) |
| Curriculum | Yes: data generation | GT-state privileged checkpoints, GT pose estimator labels; physics randomization | Estimator 학습 데이터 생성에 필요; 배포 입력 아님 (§3.2/4, pp.4–5; Appendix A–B) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| 불확실성 모델링의 pose 추정 효과 | Representation ablation | Vision baseline / MSE / likelihood / likelihood+MC dropout | Mean translational L2 error49.83/7.62/6.83/4.42 mm; yaw mean abs22.56/2.51/2.46/2.10°. Force-only ablation은 아님. | §5.1; PDF p.6 ; Table 2 |
| Estimator와 uncertainty를 policy 학습에 반영 | Input ablation; Controlled comparison | 제안 / uncertainty input 제거 / MSE estimator / privileged policy에 estimator 직접 연결 | Success94/92/64/83%; end-to-end RL12%, BC38%. RL curves 3seeds. | §5.2; PDF pp.6–7 ; Fig.2 |
| Occlusion 대응 hardware | Controlled comparison | 자연 가림 / human-induced5s / full occlusion | 19/20;10/10;7/10 successful. Full occlusion은 시작 후 종료까지 가림이며 초기 관측까지 전혀 없는 조건은 아님. | §6; PDF p.8 ; Fig.1 |
| 정보 수집 행동 | Controlled comparison; Author explanation only | Privileged vs uncertainty-aware policy | 20,000 episodes에서 contact switches2.68±1.53 vs4.22±2.67; sticking이 uncertainty를 줄인다는 설명은 해석 수준. | §5.4; PDF pp.7–8 ; Fig.4 |

## 13. Author-stated Limitations

학습형 estimator는 방대한 interaction data와 충분한 상태 공간 coverage가 필요하다. Pusher/object geometry를 고정했고 다양한 기하 및 다른 non-prehensile 과업 일반화는 검증하지 않았다. Pusher dynamics가 force measurement에 주는 영향을 simulation에서 생략했다. 추정 uncertainty 자체의 정량적 calibration 평가는 하지 않았다. (§7, p.8)

## 14. Author-stated Future Work

Pusher dynamics를 학습에 포함하고 uncertainty로 실패 예측, fallback recovery, estimator 데이터 coverage 확대를 수행할 수 있다고 명시한다. (§6–7, p.8)

## 15. Review-relevant Findings

- 배포 actor에는 current object pose estimate가 매 step 제공된다. Pose 미제공 정책이 아니다.
- 시각 pose는 가림 동안 정지하지만 force/EEF history를 통한 추정이 계속된다.
- 이름의 visuotactile은 별도 tactile array와 wrist F/T의 병용을 뜻하지 않는다.
- GT는 privileged 데이터 생성, estimator label, reward/termination에 사용된다.
- 불확실성 및 학습 구조 ablation은 있으나 force 제거 단독 실험은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / Object pose | §3.2–3.3, pp.4–5 |
| Tactile / F/T | §6 p.8; Appendix B.1 p.12 |
| Reward / Termination | §4 p.5; Appendix A p.12 |
| Critic | Appendix B.1 p.13: architecture only; GT input 미명시 |
| Ablation | Table 2 p.6; Fig.2–4 p.7 |
| Limitation / Future | §6–7 p.8 |
