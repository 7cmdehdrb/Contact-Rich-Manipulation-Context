# Dexterous Functional Grasping

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B001
- Authors: Ananye Agarwal; Shagun Uppal; Kenneth Shaw; Deepak Pathak
- Year: 2023
- Venue: 7th Conference on Robot Learning (CoRL 2023), Atlanta, USA. PDF p.1에 명시.
- DOI / arXiv: DOI 미명시; [arXiv:2312.02975](https://arxiv.org/abs/2312.02975).
- PDF version: arXiv v1, 2023-12-05.
- Page count: 15. 본문 pp.1–8, 참고문헌 pp.9–12, Appendix A–E pp.13–15.
- SHA-256: `c12f68a582bc9f3d1113f38610b62a3a337054583da3e89945e4d10c719903b9`
- PDF filename: `Agarwal 등 - 2023 - Dexterous Functional Grasping.pdf`
- 근거 범위: 이번 PDF의 본문·관련 부록을 새로 읽었다. 표·수식·관측 설명의 핵심 페이지 5·6·15는 PDF 렌더링으로도 확인했다. 기존 상세 노트를 분석 근거로 사용하지 않았다.

## 2. Relevance to This Review

**Relevant.** 초기 시각 affordance로 접근한 뒤에는 물체의 현재 pose나 시각 영상을 받지 않는 blind grasping policy를 실행한다. 손 관절각과 recurrent state가 접촉 이후 반응을 만드는 사례이며, 시각의 역할과 실행 중 피드백의 역할을 분리하여 비교할 수 있다. Tactile 또는 F/T를 사용하는 논문은 아니므로 축약 tactile의 성능 근거로 사용하지 않는다. 특히 recurrence 비교와 학습용 물체 위치의 사용을 구분할 수 있다 (§1–2·4.1, Appendix D; PDF pp.2–6·15).

## 3. Task

다지 손으로 물체를 집어 올리고 도구 사용에 적합한 단단한 grasp를 만든다. Pre-grasp 위치·방향을 정하고, 손가락으로 물체를 잡아 손바닥 가까이 옮긴 뒤, 팔의 post-grasp 궤적 중에도 파지를 유지한다. Simulation 성공은 팔이 회전하는 동안 한 번도 물체를 떨어뜨리지 않는 경우다. 실물은 7종 물체·중량 조건에서 각 방법당 10회 시험하며 saucepan은 들어 올리기만 하고 나머지는 들어 올린 뒤 흔드는 궤적으로 유지 여부를 평가한다 (§2–4.2, Table 1–2; PDF pp.3–6).

## 4. Method

### 4.1. Overall Pipeline

초기 RGB-D + category exemplar affordance mask → DINO feature 대응과 DETIC mask 교집합 → affordance 중심의 3D 점 및 mask 주축 기반 pre-grasp → 팔 접근 → 관절각·target EEF pose → recurrent PPO policy → 9D eigengrasp 계수 → 16개 손 관절각 → 손 실행. 팔의 post-grasp 동작은 mocap trajectory 또는 keypoint 보간으로 제공한다 (§2.1–2.3, Fig.2, Appendix C–D; PDF pp.3–5·14–15).

### 4.2. Observation

| 수신 모듈 | 입력 | 실행 조건 및 구분 | 원문 위치 |
| --- | --- | --- | --- |
| 초기 affordance/pre-grasp 모듈 | 세 D435의 RGB-D; 범주별 exemplar affordance annotation; DETIC object mask; camera calibration | 가장 높은 대응 점수의 접근 축을 선택. Grasp policy에 연속 영상을 전달하는 구조가 아님 | §2.1, pp.3–4; Appendix A·C, pp.13–14 |
| Grasp Actor | 손의 16개 관절 위치; EEF의 7D target pose(position, quaternion) | Appendix D의 명시적 목록. Current object pose, tactile, force는 열거되지 않음 | Appendix D, p.15 |
| Actor 내부 | 256D GRU hidden state | 관측 이력의 압축 상태. 물체 pose estimator 출력으로 정의되지 않음 | Appendix D, p.15 |
| 팔/손 실행 경로 | pre-grasp pose, post-grasp trajectory, 손 관절각 명령 | 물체 현재 pose와 구분. 상세 low-level feedback 목록은 미명시 | §2.1–2.3, pp.4–5 |

**원문 내부 불일치:** Appendix D는 관측을 $o_t\in\mathbb{R}^{16}$이라고 쓰면서 같은 문단에서 7D target EEF pose와 16개 손 관절각을 열거한다. 따라서 전체 observation dimension은 원문만으로 확정하지 않는다. §4.3의 “end-effector pose”보다 더 구체적인 Appendix D의 “target pose”를 따라 기록하며, 이를 측정된 current EEF pose나 current object pose로 바꾸지 않는다. 관절 속도는 하드웨어가 출력하지 않는다고 저자가 설명한다 (§4.1, p.6).

### 4.3. Action

9D policy 출력은 human mocap 손 자세에 PCA를 적용해 얻은 9개 eigengrasp의 선형 결합 계수다. 이를 16D 손 관절각으로 변환한다. PCA 대상은 tactile 표현이 아니라 **action 공간**이다. 별도의 팔 경로와 손 grasp policy의 action을 혼합하지 않는다 (§2.2, pp.4–5).

### 4.4. Controller

실물은 xArm6에 16관절 LEAP Hand를 장착하고 팔·손을 30 Hz로 실행한다. 관절각 명령 생성은 명시되지만 PD gain, torque loop, impedance controller의 구체적 설정은 원문에서 확인되지 않는다. 팔 궤적은 학습 policy의 9D 출력이 아닌 별도 지정 궤적이다 (Appendix C, p.14; §2.3, p.5).

### 4.5. Learning / Optimization Method

IsaacGym/IsaacGymEnvs와 rl_games에서 PPO를 사용한다. Layer-normalized GRU hidden size 256 뒤에 512·256·128 MLP를 두며 32 timesteps에서 BPTT를 절단한다. 8,192개 병렬 환경, 400 epochs로 학습한다. Human hand-pose data는 16D→9D action subspace를 만드는 데 쓰인다. Hammer의 크기·질량·마찰과 제어 stiffness/damping을 randomize한다 (Appendix D–E, Table 4; p.15).

Reward는 object 높이에 대한 binary 항과 hand–object 거리 항으로 구성된다. 높이 임계값은 PDF p.5에 `0.04cm`로 인쇄되어 있으며, 통상적인 단위로 임의 수정하지 않는다. Object 위치 기반 reward와 Actor 입력은 별개다 (§2.2, p.5).

## 5. Object Information

분류는 전체 실행 pipeline을 기준으로 하되, 초기 접근용 정보와 grasp Actor 입력을 구분한다.

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Initial | Affordance mask 중심의 RGB-D 투영으로 robot-frame 3D pre-grasp 점 | 초기 접근에서 계산; blind grasp 중 물체 위치 갱신 없음 | 물체 중심 GT나 full pose가 아니라 물체의 기능 영역 위치. Actor에 current object position 미제공 (§2.1, pp.3–4; Appendix D, p.15) |
| Orientation | Initial | DETIC object mask의 가장 큰 주축에 수직인 hand 방향과 선택된 camera 접근 축 | 초기 pre-grasp 계산; grasp 중 물체 orientation 갱신 없음 | 물체의 완전한 3D orientation estimator가 아님. Actor의 EEF target quaternion과 구분 (§2.1, p.4) |
| Shape / Geometry | Initial | 초기 object mask·local geometry·category exemplar 대응 | 초기 접근에서 사용; grasp Actor에 mesh/CAD/dimensions 입력 없음 | 제한적 형상 단서. 학습 hammer geometry prior는 존재하나 실제 물체 full shape 입력과 다름 (§2.1–2.2, pp.3–5) |
| Physical Parameters | 미제공 | Actor에 질량·마찰 등 물성 입력 없음 | 없음 | Simulator에서 object scale/mass/friction 등을 randomize함. 실행 중 물성 estimator는 미명시 (Appendix D–E, p.15) |

## 6. Missing Object Information and Compensation

- Grasp 중 current object position/orientation·시각 갱신 미제공 → 손 관절각 + target EEF pose + GRU recurrent state → 손 동작을 반응적으로 수정한다. 저자는 proprioception으로 엄지 끼임을 감지해 회복한 사례와 팔 자세 변화에 맞춘 재파지를 설명한다. 물체 pose를 수치 복원했다는 주장은 아니다 (§4.3, Figs.5–6, p.7).
- 관절 속도 직접 관측 미제공 → recurrent hidden state → 저자는 hidden state가 관절 속도를 암묵적으로 포착한다고 설명한다. RNN/feed-forward 비교는 있으나 hidden state의 velocity estimation error를 직접 측정하지는 않는다 (§4.1, Table 1, p.6).
- 정확한 pre-grasp와 물성 미확보 → 초기 visual affordance + recurrent policy + domain-randomized training → 작은 초기 오차와 dynamics 변화에 대응하도록 학습한다. 큰 초기 오차에는 회복하지 못한다고 저자가 한계를 명시한다 (§6, p.8; Appendix D–E, p.15).

따라서 이 논문의 “보완”은 reactive grasp 성공과 recurrence 성능 차이에 근거한다. Contact localization이나 전체 object state reconstruction이 검증되었다고 해석하지 않는다.

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. Grasp feedback으로 기술된 것은 관절 위치 기반 proprioception이다.

### 7.2. Preprocessing

해당 없음.

### 7.3. Policy Representation

해당 없음. 9D eigengrasp는 tactile compression이 아닌 action compression이다.

### 7.4. Retained Information

해당 없음.

### 7.5. Removed / Unavailable Information

Tactile 측정에 의한 접촉 위치·분포·압력 정보는 제공하지 않는다. Tactile 입력 자체가 없으므로 특정 tactile 전처리에서 제거된 정보라고 기록하지 않는다 (Appendix D, p.15).

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. Wrist F/T, fingertip force, joint torque estimated wrench를 policy 관측으로 기술하지 않는다.

### 8.2. Representation

해당 없음.

### 8.3. Role

해당 없음. 강한 파지나 힘을 가하는 동작은 force measurement 사용의 근거가 아니다.

### 8.4. Required Assumptions

F/T 기반 추정에 해당 없음.

### 8.5. Reported Limitation / Ambiguity

원문에서 F/T의 contact locality 또는 net-wrench ambiguity를 직접 논의하지 않음.

## 9. Other Observations

- **Proprioception:** 손 관절 위치를 grasp Actor에 제공. 관절 속도는 제공되지 않는다고 명시한다 (§4.1, p.6; Appendix D, p.15).
- **Vision:** 초기 affordance 영역과 접근 방향을 정한다. Grasp phase는 blind다 (§1–2.1, pp.2–4).
- **History / recurrent state:** GRU hidden state를 사용. 32-step BPTT는 학습 절단 길이이며 고정 32-frame 실행 입력 window로 해석하지 않는다 (Appendix D, p.15).
- **Previous Action:** Actor 입력 목록에 미명시. GRU를 쓴다는 이유로 별도 previous-action 입력을 추정하지 않는다.
- **EEF state / Goal:** 명시된 입력은 7D target EEF pose다. 물체의 current pose나 object goal pose가 아니다 (Appendix D, p.15).
- **State Estimator:** 물체 pose/force 추정 모듈 없음. Recurrent state에 명시적 estimator supervision을 제공하는지는 원문에서 확인되지 않음.
- **기타 prior:** Category별 한 장의 affordance annotation과 human hand poses로 얻은 eigengrasp action prior가 사용된다 (§2.1–2.2, pp.3–4).

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않으므로 tactile–F/T 상보성 분석은 해당 없음. 비교 가능한 역할 분담은 초기 vision이 접근 위치·방향을 정하고 proprioception+recurrence가 그 이후 grasp를 조정한다는 점이다. Recurrence 비교는 있으나 “tactile 제거” 또는 “F/T 추가” 실험은 없다. 이 결과를 binary tactile+F/T의 유용성으로 확대하지 않는다 (§1–2·4.1–4.3; pp.2–7).

| 추가 정보 | Tactile이 제공하는 정보 | Tactile에서 부족한 정보 | 추가 정보의 역할 | 역할에 대한 원문 근거 |
| --- | --- | --- | --- | --- |
| 초기 vision | 해당 없음 | 해당 없음 | Functional region과 pre-grasp 방향 제공 | §2.1, pp.3–4 |
| 관절각 + GRU | 해당 없음 | 해당 없음 | Blind grasp 반응, 관절 속도 미관측의 암묵적 보완 | §4.1·4.3, pp.6–7; Table 1 |

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | No: object GT 미제공 | 손 관절 위치 + target EEF pose + recurrent state | 실행 시 필요한 입력. Simulator 관절 상태로 학습하지만 실행 불가능한 object GT를 Actor에 주는 구조는 아님. 전체 차원은 원문 불일치 (§4.1, p.6; Appendix D, p.15) |
| Critic | 미명시 | Critic 입력 목록·asymmetric architecture는 원문에서 확인되지 않음 | PPO 사용만으로 Actor와 동일하거나 privileged라고 추정하지 않음. 실행 시 Critic 필요 여부도 별도 명시 없음 (Appendix D, p.15) |
| Reward | Yes | Simulator object 높이, hand–object 거리 | Training reward에 사용. 실제 grasp Actor 실행 입력이 아님 (§2.2, p.5) |
| Termination | Yes: simulation | Hand–object 거리 20 cm 초과 | Simulator 종료 조건. 실물 온라인 종료 센서/판정 구현은 미명시이며 sim 조건이 실물에도 필요하다고 단정하지 않음 (§2.2, p.5) |
| Curriculum / Data Generation | Yes: simulator 설정; curriculum은 미명시 | Procedural hammer 생성, object 물성/geometry randomization, 초기 hand–object 배치 | 실행 Actor 입력이 아님. 시간에 따른 curriculum schedule은 미명시. Human mocap는 action basis 생성용 data (§2.2, pp.4–5; Appendix E, p.15) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Recurrence가 grasp 성능·안정성에 기여 | Controlled comparison | 동일 eigengrasp 방법의 feed-forward vs recurrent; 5 seeds, 400 epochs | Success rate hammer 0.60±0.54→1.00±0.00; drill 0.21±0.19→0.23±0.16; screwdriver 0.56±0.52→0.95±0.10. 모든 물체에서 큰 이득으로 일반화하지 않음 | §3·4.1, Table 1; PDF pp.5–6 |
| 관절 속도 미관측을 hidden state가 보완 | Author explanation only | RNN/feed-forward 성능 차이 해석 | 속도 정보를 암묵 포착한다는 저자 설명. 속도 복원 자체에 대한 직접 오차 측정은 없음 | §4.1; PDF p.6 |
| Proprioception으로 초기 grasp 오류에 반응 | Author explanation only | 엄지가 끼인 개별 실행 사례 | 저자는 proprioception 기반으로 엄지를 물체 주위로 옮겨 회복한다고 설명. 해당 입력 제거 ablation은 없음 | §4.3, Fig.5; PDF p.7 |
| EEF pose와 grasp 조정 관계 | Author explanation only | Heavy drill 방향 변화 사례 | 엄지를 움직여 안정화하는 동작 제시. Target EEF pose 제거 실험은 없음 | §4.3, Fig.6; PDF p.7 |
| 초기 affordance 추정의 역할 | Controlled comparison | CLIPort·CLIPSeg·ours; 각 category 10회, simulated CLIPort dataset | Hammer pick 2/10·1/10·9/10; spatula 6/10·2/10·8/10; frying pan 7/10·1/10·7/10. Tactile 보완 실험이 아님 | §4.4, Table 3; PDF pp.7–8 |
| 큰 pre-grasp 오류에 대한 blind policy 한계 | Author explanation only | 정량 error sweep 미명시 | 큰 오류에서 회복할 수 없다고 명시 | §6; PDF p.8 |

입력 종류별 제거 실험은 없어 proprioception, target EEF pose, action prior 각각의 독립적 필요성을 이 결과만으로 확정하지 않는다.

## 13. Author-stated Limitations

- 작은 pre-grasp 오차에는 대응하지만 큰 오차에는 blind policy가 회복하지 못한다 (§6, PDF p.8).
- 현재 affordance model의 joint-pose 정보를 이용하지 않는다. 저자는 동전·신용카드 같은 얇은 물체의 더 세밀한 조작에는 도움이 될 수 있다고 설명한다 (§6, PDF p.8).
- Heavy drill은 좁은 grip과 불균형한 무게 분포로 어렵다고 설명하며 실물 성공률은 0.5다. 이를 일반적인 F/T ambiguity나 tactile 부재의 인과 효과로 해석하지 않는다 (§4.2, Table 2, PDF p.6).

## 14. Author-stated Future Work

큰 affordance/pre-grasp 오류를 보정하기 위해 손목 주변의 local field of view를 제공하는 방향을 제시한다. 더 세밀한 얇은 물체 조작에서 affordance model의 joint-pose 정보를 활용할 가능성도 언급한다. 둘 다 현재 구현·검증 성과가 아니다 (§6, PDF p.8). Post-grasp 경로를 internet video 또는 third-person imitation에서 얻을 수 있다는 언급도 있으나, 이 논문에서 실제 사용한 경로는 mocap 또는 keypoint 보간이다 (§2.3, PDF p.5).

## 15. Review-relevant Findings

- 초기 RGB-D가 functional region과 접근 방향을 정하고 grasp policy는 시각 갱신 없이 동작한다.
- Actor 입력에 current object pose, tactile, F/T는 없다. 손 관절각과 target EEF pose, GRU hidden state를 사용한다.
- Recurrence 비교가 존재하며 저자는 관절 속도 미관측과 dynamics 변화 적응을 설명한다.
- Actor가 object GT를 받지 않아도 reward와 simulation termination은 물체 위치를 이용한다. Critic GT 여부는 미명시다.
- “Initial” 물체 정보는 pre-grasp용 부분적 위치·방향 단서이며 완전한 object pose 추적이 아니다.
- 9D 축약은 tactile이 아니라 action 공간에 적용된다. 이 논문은 binary tactile/F/T 결합 효과를 검증하지 않는다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | Appendix D, PDF p.15; 관절 속도 부재 §4.1, p.6 |
| Object pose | §2.1, PDF pp.3–4; 초기 단서와 blind phase §1, p.2 |
| Shape / geometry | §2.1–2.2, PDF pp.3–5; Appendix E, p.15 |
| Tactile | 입력 목록 Appendix D, PDF p.15; 별도 tactile 사용 없음 |
| F/T | 입력 목록 Appendix D, PDF p.15; 별도 F/T 사용 없음 |
| Action / Controller | §2.2–2.3, PDF pp.4–5; Appendix C, p.14 |
| Reward / Termination | §2.2, PDF p.5 |
| Critic | Appendix D, PDF p.15 검토; Critic 입력은 미명시 |
| Ablation / comparison | §3–4.1, Table 1, PDF pp.5–6; Table 3, p.7 |
| Limitation | §6, PDF p.8 |
| Future Work | §6, PDF p.8; §2.3, p.5 |
