# Proprioceptive Sensor-Based Simultaneous Multi-Contact Point Localization and Force Identification for Robotic Arms

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B023
- Authors: Seo Wook Han; Min Jun Kim
- Year: 2023
- Venue: Not stated (arXiv preprint)
- DOI / arXiv: 미명시 / 2303.03903v1
- PDF version: arXiv v1; 7 March 2023
- Page count: 7
- SHA-256: `bd15b5edddee5ad6286c6e43e39c089ba0ceae9072a3d27effa9c78ad08cb9b0`
- PDF filename: `Han 및 Kim - 2023 - Proprioceptive Sensor-Based Simultaneous Multi-Contact Point Localization and Force Identification f.pdf`
- 분석 근거: 선택 PDF 원문을 새로 읽었다. 기존 논문 상세 노트를 근거로 사용하지 않았다. 본문 pp.1–6을 읽고 Table I–III와 Fig.5–6를 렌더 확인했다. p.7은 참고문헌; 관련 appendix 없음.

## 2. Relevance to This Review

**Relevant**. 조작 정책은 아니지만 joint torque와 base F/T를 이용한 접촉점·접촉력 추정의 성립 조건과 모호성을 직접 분석한다. Robot surface mesh, dynamics, 순차적 점 접촉 등의 추가 제약을 요구하며 base F/T를 더해도 singularity가 남는 실패 사례를 제시한다.

## 3. Task

로봇 팔 표면의 단일·이중·삼중 접촉 위치와 각3D force를 동시에 추정한다. Manipulation action 성공이 아니라 localization error≤2.25cm가 성공 기준이다. MuJoCo의7DOF Franka Panda에 각각10,000회, 임의 configuration/표면에서20N force를 가하며 한 link당 최대1접촉이다. (§IV, p.5)

## 4. Method

### 4.1. Overall Pipeline

JTS와 q/qdot → momentum observer의 external joint torque; base6-axis F/T → dynamics compensation한 external base wrench → candidate robot-mesh points에서 friction-constrained QP → particle weight/resampling/exploration → contact locations와 forces. (§II–III, pp.2–5)

### 4.2. Observation

Estimator 입력은 joint torque, joint position/velocity, base F/T 및 robot kinematic/dynamic model과 surface mesh이다. 물체 영상·물체 pose·tactile은 쓰지 않는다. Actor/controller 입력은 해당 없음. (§II, p.2)

### 4.3. Action

Policy action 없음. 출력은 contact count를 반영하는 particle sets, 각 contact point와3D force이다. (§III-D–E, p.5)

### 4.4. Controller

조작/접촉 제어기는 제안하지 않는다. 외부 force를 인가한 simulation estimation 평가이다. (§IV, pp.5–6)

### 4.5. Learning / Optimization Method

MCP-EP(Multi-Contact Particle Filter with Exploration Particles), QP(qpSWIFT), offline mesh preprocessing. 불가능한 접촉면을 제거하고 isotropic remesh, link내 surface geodesic 거리를 계산한다. Particle는(link,face)이며 이웃 link exploration이 잘못된 link 수렴에서 탈출하게 한다. 학습/RL은 아니다. (§III, pp.3–5)

## 5. Object Information

대상은 외부 물체 조작이 아닌 robot contact estimation이다. 표의 geometry/physics는 물체 GT와 구별하여 robot model을 명시한다.

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 해당 없음 | 대상 object pose를 추정하지 않음 | 해당 없음 | 대신 robot surface상의 contact point를 추적 |
| Orientation | 해당 없음 | Object orientation 해당 없음 | 해당 없음 | q/qdot로 robot configuration 사용 |
| Shape / Geometry | 기타 | Known robot-link mesh, contactable surfaces, face normals, precomputed geodesic distances | mesh고정; robot configuration 갱신 | 접촉하는 외부 object geometry가 아니라 robot contact surface model |
| Physical Parameters | 기타 | Robot inertia/Coriolis/gravity model; friction-cone constraint | 동역학 보정 갱신 | 외부 object 물성 없음; friction coefficient 수치는 미명시 |

## 6. Missing Object Information and Compensation

Contact location/force가 직접 측정되지 않음 → joint external torque + base wrench + known robot surface/Jacobian/dynamics + unilateral friction cone → sensor residual을 설명하는 위치·힘 후보를 추정한다.

JTS만으로 proximal link에서 sensing DOF가 부족함 → base F/T의6개 독립 측정 성분 추가 → singularity를 완화한다. 그러나 여전히 서로 다른 위치·힘이 같은 측정을 만들 수 있으며 완전한 해 유일성을 보장하지 않는다. (§II-C/IV, pp.3/6)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음.

### 7.2. Preprocessing

사용하지 않음.

### 7.3. Policy Representation

사용하지 않음.

### 7.4. Retained Information

사용하지 않음.

### 7.5. Removed / Unavailable Information

사용하지 않음.

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Robot base의6-axis F/T + 각 joint torque sensor. Wrist F/T가 아니다. (§II-A–B, p.2)

### 8.2. Representation

Momentum observer로 얻은 external joint torque n개와 dynamics-compensated base wrench6개를 결합해 W∈R^(n+6)를 구성한다. Base wrench에서 RNEA nominal robot dynamics contribution을 빼야 하며 raw measurement가 곧 contact wrench는 아니다. (Eq.3–6, p.2)

### 8.3. Role

Candidate contact points에서 friction-constrained QP residual을 최소화하여3D contact force를 구하고 PF로 point location을 추정한다. Contact point 수는 residual에 따라 particle set 추가/제거로 관리한다.

### 8.4. Required Assumptions

알려진 robot mesh/normal/Jacobian/dynamics, moment 없는 point contact, pulling 불가·friction cone, 한 link당 최대1contact, multi-contact가 순차적으로 생기고 이전 particle set이 다음 접촉 전에 수렴한다는 가정이다. Dual-contact 평가는0.1초 간격이다. (pp.2–4/6)

### 8.5. Reported Limitation / Ambiguity

Base F/T를 추가해도 같은 sensor measurement를 만드는 다른 point/force pair가 존재한다(Fig.5). Dual contact에서는 거의 같은 측정을 설명하는 local minimum도 실패를 일으킨다(Fig.6). Contact links가 멀수록 사이 joint sensing이 풍부해지는 경향을 보고한다.

## 9. Other Observations

Vision·history/action-conditioned policy는 없음. Momentum observer의 시간적 적분과 particle filter의 이전 belief를 사용한다. q/qdot 및 robot model은 단순 net wrench 외에 반드시 들어가는 proprioceptive/기하 정보이다.

## 10. Tactile–Other Modality Relationship

Tactile이 없으며 base F/T와 distributed joint torque의 결합이다. Contact locality는 알려진 robot geometry와 friction/point-contact 제약을 함께 써서 복원한다. 이 결과를 wrist F/T 하나로 임의의 다중 접촉 분포를 복원한 것으로 확대하면 안 된다.

## 11. Training-only / Privileged Information

Actor·Critic·reward·termination·학습 데이터 생성을 따로 기록한다.

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV, pp.5–6) |
| Critic | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV, pp.5–6) |
| Reward | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV, pp.5–6) |
| Termination | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV, pp.5–6) |
| Curriculum | 해당 없음: 비-RL | 해당 없음 | Simulation에서 접촉 위치/힘 GT를 성공률·RMSE 평가에 사용한다. Estimator 입력 GT와 평가용 GT를 구별한다. (§IV, pp.5–6) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| 접촉 수가 증가할 때 추정 성능 | Controlled comparison | Single/dual/triple, 각10,000 simulation trials | Success99.96/96.70/81.63%; position RMSE0.16/1.08/3.50cm; force RMSE0.01/2.00/4.63N. RMSE에 실패 포함. | §IV; PDF p.5 ; Table I |
| 추가 base F/T가 observability를 늘림 | Author explanation only | Link1에서 JTS-only1DOF vs base F/T 추가7DOF | 6 sensing DOF가 위치와 무관하게 추가된다는 식/설명. 본 논문에 matched sensor-removal success table은 없음. | §II-C; PDF p.3 |
| Base F/T와 JTS 조합에도 모호성 잔존 | Failure analysis | Single/dual singular configurations | Single10,000 중4실패는 singularity; dual에서는 거의 같은 measurement를 만드는 local minima가 주 원인. | §IV-A–B; PDF p.6 ; Table III ; Fig.5–6 |
| 실시간 계산 | Controlled comparison | Single/dual/triple | 평균 iteration0.45/1.66/4.50ms. Contact convergence와 iteration rate를 구별해야 함. Single 약18.25step=8.21ms 후 수렴. | §IV; PDF pp.5–6 ; Table I |

## 13. Author-stated Limitations

동일 측정으로 설명되는 다른 contact-force pair의 singularity가 남는다. Dual contact에서는 정확히 같지 않아도 유사한 측정을 설명하는 local minima가 주 실패 원인이다. Offline mesh distance는 link 내부에서만 유효하여 exploration particles가 필요하다. Point contact·한 link당1접촉·순차 발생 가정 아래 검증했다. (§II–IV, pp.2–6)

## 14. Author-stated Future Work

원문에서 명시적인 향후 연구 계획을 확인하지 못했다. (§V Conclusion, p.6)

## 15. Review-relevant Findings

- Base F/T와 JTS를 함께 사용하며 wrist F/T-only 방법이 아니다.
- Robot surface mesh와 동역학 모델이 필수이다.
- Moment 없는 unilateral point contact, 한 link당 최대1접촉 및 순차 발생을 가정한다.
- Base F/T가 singularity를 완화하지만 제거하지는 못한다.
- Simulation-only 검증이며 tactile/정책 ablation은 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / Object information | §II pp.2–3; §III-A p.3 |
| Tactile | 미사용, §I–II |
| F/T / Assumptions | §II pp.2–3; §III-B p.4 |
| Reward / Critic | 해당 없음: model-based estimator |
| Evidence / Ambiguity | Table I p.5; Table III/Fig.5–6 p.6 |
| Limitation / Future | §IV–V p.6; future 미명시 |
