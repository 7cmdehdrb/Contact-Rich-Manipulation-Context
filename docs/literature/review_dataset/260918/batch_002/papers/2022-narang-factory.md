# Factory: Fast Contact for Robotic Assembly

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B058
- Authors: Yashraj Narang; Kier Storey; Iretiayo Akinola; Miles Macklin; Philipp Reist; Lukasz Wawrzyniak; Yunrong Guo; Adam Moravanszky; Gavriel State; Michelle Lu; Ankur Handa; Dieter Fox
- Year: 2022
- Venue: Not stated
- DOI / arXiv: Not stated / 2205.03532v1
- PDF version: arXiv v1, 7 May 2022; Appendix 포함
- Page count: 21
- SHA-256: 3ed5068251c0eaef46fc394cbf8d0482a027dc22ee0dfa1067929ca90b9ff8b6
- PDF filename: Narang 등 - 2022 - Factory Fast Contact for Robotic Assembly.pdf
- 읽은 범위: PDF pp.1–21 본문 및 포함된 부록을 새로 확인; 핵심 표·그림 렌더링 확인

근거는 이번 배치의 PDF 원문이며 기존 상세 노트는 사용하지 않았다. 페이지는 PDF의 1-based page다.

## 2. Relevance to This Review

**Partially Relevant**. 주요 기여는 접촉 시뮬레이션이지만 Screw task에서 pose/velocity에 force와 action을 추가하는 observation ablation을 제공한다. GT pose를 계속 제공하는 조건에서 force의 유용성이 자동으로 보장되지 않는 비교 근거이며, sensor-free 또는 tactile 정책의 실물 검증 사례는 아니다.

## 3. Task

Simulated Franka의 nut-and-bolt Pick→Place→Screw. Pick은 파지 후 lift 유지, Place는 nut/bolt keypoint 평균 거리 0.8 mm 미만, Screw는 bolt base에서 한 thread 미만 거리에 도달하면 성공이다. Screw는 wrist joint limit을 제거해 regrasp를 생략한다. (§V pp.8–10)

## 4. Method

### 4.1. Overall Pipeline

Simulator state → PPO subpolicy → controller target → IK/OSC 또는 비교용 hybrid controller → joint torques. SDF collision/contact reduction은 simulator 내부 물리 계산이며 tactile representation이 아니다. (§III–V pp.4–10)

### 4.2. Observation

Pick: hand/nut pose와 hand linear/angular velocity. Place: 여기에 bolt pose. Screw 최종 정책: gripper/nut pose와 velocity. Table IV는 Pose→+velocity→+force→+action을 비교하지만 추가 force/action의 정확한 차원·센서좌표·시간지연은 미명시다. Shared-trunk actor/critic은 이 simulation observation을 사용한다. (§V pp.8–10; Table IV p.11; Table IX p.20)

### 4.3. Action

Pick/Place는 현재 상태에 대한 6D pose 변화(axis-angle 포함)를 IK target으로 사용. Screw 최종 action은 Z translation+yaw 2D이며 다른 axis에 task-space wrench를 능동 생성하지 않는다. 비교용 force controller target은 3D force, hybrid는 pose6+force3=9D. (§V.A p.8; Table XI p.21)

### 4.4. Controller

Damped-least-squares IK 및 낮은 proportional gain의 OSC를 최종 선택했다. Closed-loop force controller는 target-current force error를, hybrid는 selection matrix를 쓴다. Robot Jacobian/inertia/gravity 모델과 낮은 joint velocity에서 Coriolis항 생략 가정이 명시된다. (Appendix D.4 p.18)

### 4.5. Learning / Optimization Method

PPO, actor/critic shared-trunk MLP. Controller/gain→observation→action→reward를 순차 비교하며 각 셀은 3 seeds 평균. 최종 Screw 4096 updates 후 1024 episodes에서85.6%, chain74.2%. Object keypoint reward는 GT를 사용하고 force reward는 사용하지 않았다고 명시한다. (§V pp.8–10; Tables IX–XII pp.20–21)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Simulator hand/nut, Place의 bolt state | 매 step | GT object pose actor 입력 (§V.B–D pp.8–10) |
| Orientation | Tracking | Simulator quaternion/pose | 매 step | Goal quaternion과 별개 current object state (§V.B–D pp.8–10) |
| Shape / Geometry | 기타 | Known part CAD/mesh/SDF는 simulation 및 keypoint 정의에 사용 | 고정 model | 정적 object mesh를 policy input으로 직접 넣는다고 명시하지 않음 (§IV.A p.6; §V pp.8–9) |
| Physical Parameters | 미제공 | Actor observation에 object 물성 없음 | 없음 | Simulator material model과 controller robot dynamics는 별개 (§IV.A p.6; §V pp.8–10) |

## 6. Missing Object Information and Compensation

현재 object pose를 상실한 blind policy가 아니라 GT pose/velocity를 계속 받는 policy다. 부족한 contact dynamics를 force input으로 보완할 수 있는지를 observation comparison으로 살펴보지만 이 설정에서는 추가 force가 성공률을 높이지 않았다. 실물 object-gripper pose estimation/slip detection을 위한 tactile 및 GT→image distillation은 향후 계획이다. (§V.D pp.9–10; Table IV/§VII.A p.11)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. (§V pp.8–10; §VII.A p.11)

### 7.2. Preprocessing

사용하지 않음. (§V pp.8–10; §VII.A p.11)

### 7.3. Policy Representation

사용하지 않음. (§V pp.8–10; §VII.A p.11)

### 7.4. Retained Information

사용하지 않음. (§V pp.8–10; §VII.A p.11)

### 7.5. Removed / Unavailable Information

사용하지 않음. (§V pp.8–10; §VII.A p.11)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Simulation force observation/controller feedback; 물리 wrist F/T 센서가 구현된 결과는 아니다. DIM 인간 wrench-mounted F/T는 비교용 외부 dataset이다. (§V.F p.10; Table IV p.11)

### 8.2. Representation

추가 force observation의 차원/좌표계는 미명시. Controller 수식은 6D wrench이고 실험 action target은3D force; joint torque/contact force norm은 평가값. (§V.A p.8; Appendix D.4 p.18)

### 8.3. Role

Observation ablation; closed-loop/hybrid force control; simulation realism 평가. 최종 Screw policy는 force observation을 선택하지 않는다. Reward에 force는 사용하지 않는다. (§V.D–F pp.9–10)

### 8.4. Required Assumptions

F/T-only contact localization은 하지 않음. Robot dynamics/Jacobian과 known assembly assets, stable initialized grasp, constrained2D Screw action이 사용된다. (§V.D p.9; Appendix D pp.17–18)

### 8.5. Reported Limitation / Ambiguity

원문에서 net wrench의 contact location/multi-contact ambiguity를 직접 논의하지 않음. 제한된 training budget이 낮은 차원의 관측·action을 유리하게 했다고 설명한다. (§V.D p.10)

## 9. Other Observations

Vision은 정책에 사용하지 않는다. Hand pose/velocity를 robot state로 사용하고, Table IV의 action 입력은 어떤 시간의 action인지 미명시다. Memory/recurrent network는 명시되지 않고 MLP다. 별도 pose estimator는 아직 실물화를 위한 제안이다. (§V pp.8–11; Table IX p.20)

## 10. Tactile–Other Modality Relationship

Tactile은 이번 실험에 없다. Pose/velocity/force/action 비교는 force 추가의 독립된 효과를 볼 자료이지만 binary tactile+F/T의 조합 실험으로 해석할 수 없다. (§V.D; Table IV p.11)

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부·비고 |
| --- | --- | --- | --- |
| Actor | Yes | Simulator current nut pose/velocity; Place bolt pose | Simulated inference에도 GT 필요; 실물 센서 대체는 향후계획 (§V pp.8–10) |
| Critic | Yes | Shared trunk의 동일 observation; critic-only extra state 미명시 | 학습 때 GT observation (Table IX p.20) |
| Reward | Yes | Nut/bolt/EEF keypoint distance와 success bonus | 학습용 GT; force reward 없음 (§V.B–F pp.8–10) |
| Termination | Yes | Screw success/failure와 fixed episode duration | 성공은 nut/bolt geometry; failure 상세 threshold 미명시 (§V.D p.9) |
| Curriculum | Yes | Known stable grasps, randomized hand/object states, preceding subpolicy final-state range | Training/reset용 simulator state; automatic curriculum은 미명시 (Table III p.9; §V.E p.10; Appendix D.3 pp.17–18) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Force 추가 효과 | Input ablation | Pose+velocity vs +force vs +force+action | 성공률0.7760→0.5026→0.3307; 각3seeds 평균. 힘센서 일반무용성의 결론은 아님 | Table IV p.11; §V.D pp.9–10 |
| Controller 구조와 성공 | Controlled comparison | OSC vs impedance/hybrid force-motion, tested gains | Table X의 hybrid/impedance조건 성공0; OSC low gain0.797. 선택된 gain·budget 조건의 결과 | Table X p.21 |
| 2D task constraint | Controlled comparison | 2DOF Z/yaw vs6DOF pose action | Table XI 2DOF pose+velocity0.7969;6DOF0 | Table XI p.21 |

## 13. Author-stated Limitations

SDF thin shells/low-tessellation 처리, memory 및 stiff deformable 지원이 제한적이다. Screw에서 wrist limit을 제거해 regrasp를 배우지 않으며, subpolicy chaining 절차는 긴 sequence로 잘 확장되지 않는다. Contact-force realism 비교가 sim-to-real 성공을 보장하지 않는다고 명시한다. (§V.D–F pp.9–10; §VII p.11)

## 14. Author-stated Future Work

Regrasp, insertion/gear policy, 추가 assets/controllers, sim-to-real transfer, image actor/privileged critic 또는 teacher-student distillation을 제안한다. Occlusion 시 object-gripper pose/slip 추정을 위한 tactile 통합은 future work다. (§VII.A p.11)

## 15. Review-relevant Findings

- Force observation 추가가 GT pose/velocity 조건에서 성능을 낮춘 비교가 있다.
- 최종 Screw actor는 GT object pose/velocity를 사용한다.
- 시뮬레이터 contact reduction은 tactile binary화가 아니다.
- Asymmetric image actor·tactile 실물화는 미구현 향후 계획이다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation/Object pose | §V.B–D pp.8–10; Table IV p.11 |
| Tactile | §VII.A p.11: 향후 계획 |
| F/T/controller | Appendix D.4 p.18; Table X p.21 |
| Reward/Termination | §V.B–F pp.8–10 |
| Critic | Table IX p.20 |
| Ablation | Table IV p.11; Tables X–XII p.21 |
| Limitation/Future | §VII p.11 |
