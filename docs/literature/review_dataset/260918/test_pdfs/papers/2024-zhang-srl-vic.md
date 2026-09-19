# SRL-VIC: A Variable Stiffness-based Safe Reinforcement Learning for Contact-rich Robotic Tasks

[검증 데이터셋](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `T02`
- Authors: Heng Zhang; Gokhan Solak; Gustavo J. G. Lahr; Arash Ajoudani
- Year: 2024
- Venue: IEEE Robotics and Automation Letters. 권·호·최종 출판 쪽수는 제공 PDF에서 미명시.
- DOI / arXiv: 제공 PDF에서 식별자 확인되지 않음. p.1의 DOI 안내 문구에는 실제 번호가 없음.
- PDF version: accepted preprint, accepted April 24, 2024. arXiv vN은 미명시.
- Page count: 8. PDF 페이지와 본문 쪽수 1–8이 일치.
- SHA-256: `3c2dfc6bb3b833492ad46883b956ed75a2a0b51c5e4bf54c38b2f5e26ef3933d`
- 원문 범위: 제공 PDF pp.1–8의 본문·그림·수식·참고문헌. 별도 Appendix 없음. 외부 코드·동영상은 미검토.

## 2. Relevance to This Review

**Partially Relevant.** 태스크는 물체의 목표 Pose 조작보다 blind maze exploration에 가깝다. 그러나 시각 없이 접촉 F/T를 사용하며 task policy와 safety/recovery policy의 입력을 구분하므로 제한 관측의 역할을 분석하는 데 유용하다. 가변 강성과 안전 회복 구조의 비교 실험도 제공한다. Tactile representation이나 F/T contact-localization 알고리즘을 검증한 논문은 아니다. [§I·III–IV, pp.1–7]

## 3. Task

Franka Panda의 peg-shaped flange를 maze 입구에서 출구까지 이동시키되 과도한 contact force를 피한다. 중간의 이동 가능한 장애물은 밀어 통과해야 하므로 접촉을 모두 피하는 정책으로는 해결할 수 없다. 성공은 constraint violation 없이 출구 도달이다. EEF 이동이 이 논문 자체의 목표이며, 특정 물체의 이동 성공을 대신 측정하는 사례로 기록하지 않는다. [§IV-A, pp.4–5]

## 4. Method

### 4.1. Overall Pipeline

```text
EEF position + 6D F/T → SAC task policy → ΔPx, ΔPy, Kx, Ky 후보
6D F/T + 후보 action → safety critic → risk
risk가 기준 이내: task action 선택
risk가 기준 초과: 6D F/T → recovery policy → recovery action 선택
선택 action → Cartesian variable impedance controller → robot actuation
```

안전 정책은 offline collision data로 먼저 학습하고 task policy는 online RL로 학습한다. Online 단계에서는 안전 모델도 갱신한다. [Fig.2, p.3; §III-B, pp.3–4]

### 4.2. Observation

| 수신부 | 입력 | 역할·경계 |
| --- | --- | --- |
| Task actor | 6축 F/T + EEF position $[P_x,P_y,P_z]$, 총 9차원 | 접촉과 현재 EEF 위치를 함께 이용해 maze 이동 |
| Recovery actor | 6축 F/T, 총 6차원 state | 위치를 암기하지 않는 접촉 안전 action 생성 |
| Safety critic | 6축 F/T state와 평가할 action | 미래 constraint risk 추정. 6차원은 state 차원이며 action까지 합친 전체 입력 차원이 아님 |
| Task value critic | SAC 사용은 명시. 별도 입력 벡터 상세는 미명시 | Privileged asymmetric critic을 제시하지 않음 |
| VIC | 목표/현재 Cartesian pose·velocity 관계, 선택 stiffness; robot dynamics/kinematics | 제어식에서 사용하는 상태. Actor에 q/qdot가 들어간다는 뜻은 아님 |

Vision, 현재 물체 Pose·속도·mesh, 명시적 goal 좌표, previous action, history stack 또는 recurrent hidden state는 정의된 Actor state에 포함되지 않는다. [§III-A–B, pp.3–4]

### 4.3. Action

4차원 $[\Delta P_x,\Delta P_y,K_x,K_y]$. 변위는 현재 EEF 위치에 대한 상대 변화다. 학습 action을 정규화하고 제어 전에 복원한다. Stiffness는 이동 방향에 맞추어 변환한다. 2D action이 9D state의 EEF z 좌표까지 제어한다는 뜻은 아니다. [§III-B, Eq.(3), pp.3–4; §IV-A, p.5]

### 4.4. Controller

Cartesian variable impedance control. 원하는 stiffness diagonal과 damping을 구성하며, 회전 stiffness 일부를 선형 stiffness에 연동하고 z축 회전 stiffness는 0으로 둔다. Robot joint dynamics, Jacobian과 Coriolis/gravity compensation을 제시한다. 최종 hardware command API와 센서/제어 주기는 제공 PDF에서 미명시. [§III-A, Eqs.(1)–(2), p.3]

### 4.5. Learning / Optimization Method

Recovery RL + VIC의 hybrid 구조다. Task policy는 SAC, recovery policy는 DDPG 방식으로 safety critic의 risk를 줄이도록 학습한다. Safety critic은 constraint label의 discounted risk를 MSE로 학습한다. Offline scripted collision data 40,018 transitions 중 185 violation transitions로 pretraining하고, online 비교는 각 조건 3 runs × 1,500 episodes이다. MuJoCo 2.3.3과 7-DoF Franka Panda 사용. [§III-B·IV-A–B, pp.4–6]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | 장애물/maze current position은 Actor state에 없음 | 없음 | EEF position은 계속 제공. Object position과 구분 |
| Orientation | 미제공 | 장애물/maze orientation은 Actor state에 없음 | 없음 | Controller의 EEF orientation과 구분 |
| Shape / Geometry | 미제공 | Maze mesh·물체 shape는 Actor에 미제공 | 없음 | 시뮬레이터 환경 mesh·flange geometry는 존재. 한 maze에서 학습한 task prior도 존재 |
| Physical Parameters | 미제공 | Actor에는 물체 mass/friction 입력 없음 | 없음 | VIC의 robot dynamics·제어 gain과 장애물·flange 실험 설정은 별도 정보 |

Goal position은 distance reward와 종료 판단에 사용한다. 정의된 task state 9차원에는 goal 좌표가 별도 입력으로 없으며, 목표 물체 Pose tracking으로 집계하지 않는다. [§III–IV, pp.3–5·8]

## 6. Missing Object Information and Compensation

```text
Vision·maze/obstacle pose·shape 직접 입력 없음
→ F/T + 현재 EEF position + 학습된 task policy + variable impedance
→ 접촉하면서 진행 방향·강성을 조정 (저자 설명·실험)

Safety model에 wall position 미제공
→ F/T와 action의 관계를 offline/online으로 학습
→ 위험 action 판정과 recovery, 위치 암기 방지 (저자 명시)
```

이 구조는 명시적인 maze map, contact point 또는 object pose 복원을 수행하지 않는다. Task policy가 한 maze shape로 학습되었다는 제약은 유지된다. [§III-B, p.3; §IV-B–C, pp.5–8]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. 6축 F/T를 분포 tactile로 분류하지 않는다.

### 7.2. Preprocessing

해당 없음.

### 7.3. Policy Representation

해당 없음.

### 7.4. Retained Information

해당 없음.

### 7.5. Removed / Unavailable Information

해당 없음.

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

원문은 F/T sensor에서 측정한 6축 값을 명시한다. 제공 PDF에는 실물 센서 모델·정확한 장착 위치·joint torque로부터 추정하는지에 대한 구현 명세가 없다. 따라서 **6-axis F/T sensor; wrist 여부 미명시**로 기록하고 특정 손목 센서 또는 estimated wrench로 추정하지 않는다. [§III-B, p.3; §IV-C, pp.6–7]

### 8.2. Representation

$[F_x,F_y,F_z,T_x,T_y,T_z]$의 연속 6차원 state. Force magnitude는 safety constraint와 분석에 사용한다. 필터·좌표계·정규화·중력/bias 보정 상세는 미명시. 실물 전이 개선을 위해 simulation state observation에 OU noise를 추가한 재학습을 보고한다. [§III-B·IV-C, pp.3–4·7]

### 8.3. Role

Task actor의 관측, recovery actor의 관측, safety critic의 risk 평가, force constraint, 고하중 penalty와 violation termination에 사용된다. Learned risk는 contact location이나 object state 출력이 아니다. [§III-B, Eqs.(4)–(6), pp.3–4]

### 8.4. Required Assumptions

F/T-only contact localization을 제안하지 않으므로 해당 역문제의 single-contact·known-surface 가정 목록은 해당 없음. 전체 task는 EEF position, robot kinematics/dynamics와 VIC, 제한된 2D action, 목표/종료 조건, collision pretraining 및 maze 경험을 함께 사용한다. Safety/recovery의 state가 F/T-only라고 전체 task가 F/T-only인 것은 아니다. [§III–IV, pp.3–5]

### 8.5. Reported Limitation / Ambiguity

실물 초기 실패를 simulator의 F/T sensing 부정확성과 dynamics 차이로 설명한다. OU observation noise로 전이를 개선한다. Net wrench로 여러 contact·contact patch를 분리하는 문제, low force·bias·drift는 직접 논의하지 않는다. Multi-contact simulator를 사용했다는 사실은 multiple contact의 관측 가능성을 입증하지 않는다. [§IV-A·C, pp.5·7]

## 9. Other Observations

- Proprioception: Task actor는 EEF position 3개를 받는다. Joint position/velocity의 Actor 입력은 없다. VIC 제어식의 robot state와 구분. [§III-A–B, p.3]
- Vision: 사용하지 않음. [Fig.1·§III-B, pp.1·3]
- History: Actor sensor history/sequence model 미명시. Replay buffer는 training data이며 실행 history가 아니다. [§III-B, pp.3–4]
- Previous Action: Actor observation에 없음. Safety critic에는 평가 대상의 현재 후보 action이 입력된다. [Eqs.(4)–(6)]
- State Estimator: Contact/object state estimator 없음. Safety critic은 risk estimator. [§III-B]
- Goal: Reward에 current EEF–goal distance 사용; Actor goal input 없음. [§III-B, p.4]

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않으므로 해당 없음.

| 추가 정보 | Tactile이 제공하는 정보 | Tactile에서 부족한 정보 | 추가 정보의 역할 | 역할에 대한 원문 근거 |
| --- | --- | --- | --- | --- |
| EEF position + F/T | 해당 없음 | 해당 없음 | Task policy에 위치 정보, safety/recovery에는 접촉 하중과 위험 관계 | §III-B, p.3. Position 제거 sensor ablation은 없음 |

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | Object GT: No | Task=F/T+EEF position; recovery=F/T | 실물에서 관측 가능한 입력. Sim state 추출 API는 미명시 |
| Critic | Safety critic: object GT 없음; task critic 상세 미명시 | Safety critic=F/T+action; SAC task critic의 입력 전체 미명시 | Safety critic은 실행 때도 action 선택에 필요. 일반 training-only critic과 다름 |
| Reward | Object GT 불필요; simulator 취득 경로 미명시 | EEF–goal distance, collision-force penalty, entrance exit penalty, goal bonus | Object pose가 아님. 학습용 goal/구역 판단은 존재 |
| Termination | Object GT 사용 확인되지 않음 | Force constraint violation; entrance departure; goal success; 500-step horizon | Goal/entrance 판정의 정확한 tolerance·좌표 계산 구현 미명시 |
| Curriculum | 명시적 curriculum 없음; offline data generation에 공간 설정 사용 | Maze 내부 사전 지정 6개 지점, 좌표 noise, random direction/action, force violation label | 위치를 safety actor에서 제거해도 data generation의 maze 공간 지식까지 없어지는 것은 아님 |

[§III-B·IV-B1, pp.3–5]

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| VIC와 recovery의 결합은 안전·성공 균형에 기여 | Controlled comparison | SRL-VIC vs Std_RL-VIC vs SRL-K300 vs SRL-K1000; 각 3 runs×1,500 episodes | Success/violation ratio와 cumulative successes에서 우수한 결과. K300은 violation이 적지만 장애물에서 진행하지 못함. 순수 F/T 제거 실험은 아님 | §IV-B2–3, pp.5–6; Figs.4–5 |
| 고정 저강성은 장애물 통과에 불충분 | Failure analysis | K300 vs variable stiffness | K300 정체, SRL-VIC는 강성을 높여 장애물 통과 | Fig.5·§IV-B3, p.6 |
| Risk는 force와 action의 관계를 반영 | Controlled comparison | Random state/action 200회 offline probe | 큰 displacement/stiffness 및 force spike와 risk의 관계 관찰. Contact locality 정답 평가는 없음 | §IV-B4, Fig.6, p.6 |
| Observation noise가 실물 전이에 기여 | Controlled comparison | 최초 simulation-trained policy vs OU observation noise로 재학습 | 실물 4/5→6/6 성공. 소규모 보고이며 동일 대규모 반복통계는 아님 | §IV-C, p.7 |
| 한 maze의 학습이 모든 maze로 일반화되지 않음 | Failure analysis | Maze shape-3 | Constraint를 위반하지 않았으나 출구를 찾지 못함 | Fig.7h·§IV-C, pp.7–8 |

## 13. Author-stated Limitations

- Dynamics와 F/T sensing의 sim-to-real 차이 때문에 최초 실물 평가에서 turning point에 걸림. [§IV-C, p.7]
- Task policy를 단일 maze shape에서 학습해 새로운 shape-3에는 일반화하지 못함. 안전 모델의 wall-position 일반화와 task 일반화를 구분한다. [§IV-C, p.8]
- 위험 상태에서 보수적으로 행동하므로 일부 baseline보다 task 완료가 다소 느림. [§IV-B3, p.6]

## 14. Author-stated Future Work

더 일반적인 task scenario 평가와 model-based RL 도입을 통한 미지 환경의 안전성·강건성 개선. [§V, p.8]

## 15. Review-relevant Findings

- Task actor에는 F/T와 EEF position, recovery actor에는 F/T가 제공된다.
- Safety critic은 실행 중 사용하는 risk 평가기이며 object-pose privileged critic과 다르다.
- Object pose·maze geometry를 Actor에서 제거해도 제어 모델·학습 환경·pretraining 위치 정보는 존재한다.
- 비교는 VIC/recovery 구조의 효과를 보여 주며 tactile 추가 효과나 F/T-only contact locality를 검증하지 않는다.
- 안전한 접촉 조절에 성공해도 새로운 maze에서 task 완료에 실패할 수 있다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §III-B state definition, p.3 |
| Object pose | §III-B state definition, p.3; §IV-C, p.8 |
| Tactile | 사용하지 않음. §III-B state·§IV setup, pp.3–5 |
| F/T | §III-B, pp.3–4; §IV-C, p.7 |
| Reward | §III-B Reward Function, p.4 |
| Critic | §III-B1–3, Eqs.(4)–(6), p.4 |
| Ablation | §IV-B, Figs.4–6, pp.5–6 |
| Limitation | §IV-B3·IV-C, pp.6–8 |
| Future Work | §V, p.8 |
