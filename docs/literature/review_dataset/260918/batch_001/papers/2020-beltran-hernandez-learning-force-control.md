# Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B007`. 이번 batch의 제공 PDF를 새로 읽은 분석이다. 페이지 표시는 별도 언급이 없으면 PDF의 1-based page다. 기존 상세 논문 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Cristian Camilo Beltran-Hernandez; Damien Petit; Ixchel Georgina Ramirez-Alpizar; Takayuki Nishi; Shinichi Kikuchi; Takamitsu Matsubara; Kensuke Harada
- Year: 2020
- Venue: IEEE Robotics and Automation Letters 5(4), 5709–5716
- DOI: 10.1109/LRA.2020.3010739
- arXiv: Not stated
- PDF version: publisher
- Page count: 8
- SHA-256: `b8338cd208ea74e5afc83a9159b391ef5dae2d4d61694ea452996ca9eae5d802`
- PDF filename: Beltran-Hernandez 등 - 2020 - Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots.pdf
- 확인 범위: 제공 PDF 전체(참고문헌 포함); 별도 Appendix 없음. 외부 code/video/supplement는 확인하지 않음.

## 2. Relevance to This Review

`Relevant`

F/T와 EEF 목표 pose 오차·속도를 함께 입력하여 접촉 조작을 수행하는 사례다. 물체 형상 모델 없이 동작하지만 알려진 EEF goal과 튜닝된 force controller에 의존하므로 F/T-only라는 표현의 조건을 구분하는 데 직접 유용하다. Tactile은 사용하지 않으며 F/T 센서 제거 비교도 없다.

## 3. Task

위치 제어형 UR3 e-series와 Robotiq Hand-e로 고정된 조립 대상에 peg/ring을 삽입한다. 시뮬레이션 cube peg–hole clearance는 1 mm, 실물 ring–bolt 0.2 mm와 peg–pulley 0.05 mm다. 성공은 EEF가 목표 pose에 충분히 가까워진 상태로 정의되며 최소 오차의 수치는 미명시다. 실제 물체 pose를 독립 추적한 성공 판정이라고 서술하지 않는다. [§IV-A–D, PDF pp.5–7]

## 4. Method

### 4.1. Overall Pipeline

EEF goal pose + current EEF pose/velocity + filtered F/T → SAC policy → pose command $a_x$와 controller parameter $a_p$ → parallel position/force 또는 admittance control → EEF pose command → IK → 안전 검증 → joint position command. Policy 20 Hz, force controller 500 Hz. [Fig.1; §III-B–D; Algorithm 1, PDF pp.3–5]

### 4.2. Observation

정책 관측은 $o=[x_e,\dot{x},F_{\mathrm{ext}}]$, $x_e=x_g-x$이다. Goal $x_g$는 알려진 EEF pose이며 current object pose가 아니다. $F_{\mathrm{ext}}$는 F/T 센서에서 얻고 low-pass filtering한다. Controller는 pose error와 force feedback을 받고, 미분/적분 항을 사용한다. 안전층은 IK 가능 여부, 목표 joint로 가는 속도, 접촉 하중 한계를 검사한다. Actor에 joint state 전체·물체 pose/shape·vision·previous action·stacked history를 추가로 넣는다는 명시는 없다. Critic 입력 계약은 별도로 명시하지 않는다. [§III-B–D; Algorithm 1, PDF pp.3–5]

### 4.3. Action

모든 모델에서 6개 위치·방향 제어 성분 $a_x$와 가변 gain $a_p$를 출력한다. Parallel 모델 P-9/P-14/P-19/P-24는 각각 9/14/19/24차원, admittance A-8/A-13/A-13pd/A-18은 8/13/13/18차원이다. P-14는 pose 6D + PD 1D + PI 1D + selection 6D, A-13pd는 pose 6D + PD 6D + stiffness 1D이다. 모델명은 총 action dimension을 나타낸다. [Table I, PDF p.5]

### 4.4. Controller

Parallel 제어는 position PD, force PI, 방향별 selection $S$, policy pose 보정을 합친다. Admittance는 force에 대한 inertia/damping/stiffness 응답과 PD 명목 궤적을 결합한다. 제어 가능한 gain 수를 줄이기 위해 PD derivative는 critical damping 관계, PI integral은 proportional의 1%, admittance inertia는 실험에서 고정하고 damping은 stiffness와 관계식으로 산출한다. Actor는 empirical $P_{\mathrm{base}}\pm P_{\mathrm{range}}$ 안의 gain을 선택한다. IK solver 종류와 구체적인 robot command API는 미명시다. [§III-C, Eqs.(1)–(4), PDF pp.3–4]

### 4.5. Learning / Optimization Method

Off-policy SAC(TF2RL)를 사용한다. Reward는 EEF goal error, action 크기, 접촉 하중, 시간 penalty, 성공/안전위반 항을 가중합한다(Eqs.(5)–(6)); 성공 보너스 200, 안전위반 −10이다. 시뮬레이션 action 비교는 모델별 50,000 steps×3회, 최대 150 steps/episode; 실물 P-14/A-13pd는 각 task에서 20,000 steps×2회, 최대 200 steps/episode를 학습한다. 실물 자체 학습이며 제공 원문은 sim-to-real 전이 결과를 주장하는 구조가 아니다. [§III-E–IV-D, PDF pp.5–7]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Current object position 관측 없음 | 없음 | Known EEF goal과 current EEF pose는 별도 제공 [§III-B; Algorithm 1, PDF pp.3,5] |
| Orientation | 미제공 | Current object orientation 관측 없음 | 없음 | EEF quaternion 표현과 물체 orientation GT를 구분 [§III-B1; Algorithm 1, PDF pp.3,5] |
| Shape / Geometry | 미제공 | 환경 geometry를 안다고 가정하지 않음 | 없음 | IK robot geometry와 고정 조립 setup은 별도 제약 [§III-B, Fig.2, PDF p.3] |
| Physical Parameters | 미제공 | 물체 mass/friction/stiffness의 actor 입력 없음 | 없음 | Controller inertia·gain base/range는 사전에 설정한 제어 parameter [§III-C; §V, PDF pp.4,8] |

## 6. Missing Object Information and Compensation

환경 geometry 및 상호작용의 정밀 모델 미제공 → 알려진 EEF goal에 대한 nominal PD trajectory + F/T + EEF velocity + SAC의 gain/trajectory 선택 → 접촉 후 속도·compliance를 조절하며 목표로 진행한다. 이는 저자가 설명한 설계 목적이다. F/T로 object pose나 contact location을 복원했다는 주장은 없다. Fig.9의 phase별 gain 변화는 하중 반응을 보여 주지만 F/T 입력 제거 실험은 아니다. [§III-B–C; §IV-D; §V, PDF pp.3–4,7–8]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§III-B; §IV-A, PDF pp.3,5]

### 7.2. Preprocessing

사용하지 않음. [§III-B; §IV-A, PDF pp.3,5]

### 7.3. Policy Representation

사용하지 않음. [§III-B; §IV-A, PDF pp.3,5]

### 7.4. Retained Information

사용하지 않음. [§III-B; §IV-A, PDF pp.3,5]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§III-B; §IV-A, PDF pp.3,5]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

UR3 e-series EEF에 장착된 Force/Torque sensor. 센서의 독립 모델명은 미명시. Joint-torque estimated wrench라고 쓰지 않는다. [§IV-A, PDF p.5]

### 8.2. Representation

$F_{\mathrm{ext}}$ contact-force feedback; 6방향 parallel force/position 제어와 연결. Simple low-pass filter를 명시하며 cutoff, gravity/bias compensation, filter history 길이는 미명시. Force/torque 개별 단위 및 전체 actor 차원은 미명시. [§III-B–C, PDF pp.3–4]

### 8.3. Role

Actor observation; force controller feedback; 접촉 하중 최소화 reward; force-limit collision detection과 episode 종료; 접촉 단계별 gain 조절. 별도의 contact localization/state estimator는 없다. [§III-B–E; §IV-D, PDF pp.3–7]

### 8.4. Required Assumptions

Known EEF goal; measurable EEF pose/velocity; position-controlled robot과 IK; empirical baseline gain/range 및 안전한계; 고정된 조립 task setup. F/T 이외의 정보 없이 일반 접촉 위치를 역산하는 방법이 아니다. [§III-B–D; §V, PDF pp.3–5,8]

### 8.5. Reported Limitation / Ambiguity

Force-limit 판정은 collision 발생 후의 reactive safety라는 점을 명시한다. Net wrench의 multi-contact/locality/patch ambiguity, 작은 힘·bias·drift 한계는 원문에서 직접 논의하지 않음. [§III-D, PDF p.5]

## 9. Other Observations

Proprioception: EEF pose error와 velocity는 actor, joint position/velocity feasibility는 IK·안전층에서 사용한다. Vision: 사용하지 않는다. Goal: 사전에 알려진 EEF goal. History/previous action/recurrent state: actor 입력으로 미명시이며 controller의 derivative/integral state와 혼동하지 않는다. State estimator: 별도의 object/contact estimator는 없다. [§III-B–D, PDF pp.3–5]

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않으므로 tactile–F/T 상보성은 해당 없음. F/T는 goal pose와 EEF state를 대신하는 것이 아니라 이들과 함께 접촉 응답을 조절한다. 두 센서 조합의 필요성을 입증한 결과로 사용할 수 없다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | Object GT: No | EEF goal error; EEF velocity; filtered F/T | 이 관측은 실행에도 필요. Sim state 취득 API는 미명시 [§III-B; Algorithm 1, PDF pp.3,5] |
| Critic | Not stated | SAC actor-critic 언급만 있고 별도 critic observation/privileged state 미명시 | GT critic 유무 판단 불가 [§III-A, PDF p.3] |
| Reward | 별도 object GT 사용 명시 없음 | EEF goal error; action; F/T; time; safety/success outcome | 실물에서도 측정 가능한 항으로 정의. Sim GT 취득 경로는 미명시; 배포 reward 불필요 [§III-E, Eqs.(5)–(6), PDF p.5] |
| Termination | 별도 object GT 사용 명시 없음 | EEF goal error threshold; force limit collision; episode step limit | Known goal·EEF/F/T 기반. 최소 성공 오차 수치는 미명시 [§III-D; §IV-B, PDF pp.5–6] |
| Curriculum | Not stated | 명시적 curriculum 없음; sim에서 비교용 동일 initial condition 설정 | 실물에도 초기/목표 pose 설정 필요. 물체 GT를 actor로 전달한다는 근거 없음 [§IV-B–D, PDF pp.6–7] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| 제어 gain/action 구성에 따라 학습 성능이 다름 | Controlled comparison | 8개 action spaces, 공통 F/T/EEF 관측 | P-14와 A-13pd가 복잡도·학습성 trade-off에서 우수; 센서 추가/제거 효과는 분리하지 않음 | §IV-B; PDF pp.5–6; Table I; Fig.5 |
| Safety violation 정보를 reward에 반영하면 collision 수가 줄어듦 | Controlled comparison | 동일 모델의 penalty 포함/제외 | A-13pd 300 vs 462, P-14 121 vs 206 평균 collisions/training session. F/T observation 제거 비교가 아님 | §IV-C; PDF pp.6–7; Table II; Figs.5–6 |
| 접촉 단계에 따라 controller gain을 조절함 | Author explanation only | 학습 초기와 학습 후 insertion trace | 접촉 후 stiffness/gain 감소, 정렬 후 증가를 관찰. 힘 정보의 인과 효과를 분리하는 ablation은 없음 | §IV-D2; PDF p.7; Not applicable; Fig.9 |
| 실물 precision assembly를 학습함 | Controlled comparison | P-14 vs A-13pd; ring/peg tasks | Ring collision 평균 45 vs 34; peg 26 vs 4. Clearance 0.2/0.05 mm. 성공률 table과 다른 지표임 | §IV-D; PDF p.7; Not applicable; Figs.7–8 |

## 13. Author-stated Limitations

Controller gain의 base/range 선택에 성능이 크게 의존하며 해당 hyperparameter를 경험적으로 정했다. Task마다 EEF goal pose를 안다고 가정한다. [§V, PDF p.8] 실물 ring pose가 grasp 안에서 조금 바뀌어 학습 성능이 일시 저하될 수 있다고 설명한다. [§IV-D1, PDF p.7]

## 14. Author-stated Future Work

Human demonstration으로 gain hyperparameter를 얻고 RL로 refine하는 방법, vision으로 target pose를 대략 추정하여 vision-to-low-level end-to-end learning을 수행하는 방향을 제안한다. 아직 구현·검증한 결과가 아니다. [§V, PDF p.8]

## 15. Review-relevant Findings

- Actor는 object pose/shape 대신 EEF goal error·velocity와 F/T를 받는다.
- F/T는 actor, controller, reward, safety termination에 각각 사용된다.
- Critic privileged information은 원문에서 확인되지 않는다.
- Controller hyperparameter와 EEF goal의 사전 설정이 필요하다.
- 핵심 비교는 action/controller 구성 및 safety penalty 비교이며 tactile/F/T 조합 ablation은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §III-B; Algorithm 1, PDF pp.3,5 |
| Object pose / shape | §III-B; Fig.2, PDF p.3 |
| Tactile | 사용하지 않음; §III-B/IV-A, PDF pp.3,5 |
| F/T | §III-B–D/IV-A, PDF pp.3–5 |
| Reward | §III-E, Eqs.(5)–(6), PDF p.5 |
| Critic | §III-A, PDF p.3; 별도 입력 미명시 |
| Ablation/comparison | Tables I–II, Figs.5–9, PDF pp.5–7 |
| Limitation / Future Work | §V, PDF p.8 |
