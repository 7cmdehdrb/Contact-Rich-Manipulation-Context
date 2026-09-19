# FILIC: Dual-Loop Force-Guided Imitation Learning with Impedance Torque Control for Contact-Rich Manipulation Tasks

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B021
- Authors: Haizhou Ge; Yufei Jia; Zheng Li; Yue Li; Zhixing Chen; Lu Shi; Lei Han; Ruqi Huang; Guyue Zhou
- Year: 2026
- Venue: Not stated (arXiv preprint)
- DOI / arXiv: 미명시 / 2509.17053v2
- PDF version: arXiv v2; 19 June 2026
- Page count: 8
- SHA-256: `71230e32ceafefd1ed30f08ad61e855ca4a27e35e6efa12c053f8c555ae070bf`
- PDF filename: `Ge 등 - 2026 - FILIC Dual-Loop Force-Guided Imitation Learning with Impedance Torque Control for Contact-Rich Mani.pdf`
- 분석 근거: 선택 PDF 원문을 새로 읽었다. 기존 논문 상세 노트를 근거로 사용하지 않았다. 본문 pp.1–7을 전부 읽고 Fig.3–4와 Table I–III를 PDF 렌더 확인했다. p.8은 참고문헌이며 별도 appendix는 없다.

## 2. Relevance to This Review

**Relevant**. 관절 토크를 digital twin과 Jacobian으로 보정·변환한 EEF wrench의 역할을 조사한다. 동일 시각·EEF position 입력에서 raw joint torque와 estimated force를 비교하므로 접촉 정보 표현의 유용성에 직접적인 근거를 제공한다. 독립 wrist F/T를 사용한 방법과 명확히 구별할 수 있다.

## 3. Task

Simulation peg-in-hole 및 실물 adapter insertion, emergency-stop button 조작, C-clamp 고정, bottle-cap tightening. 실물 button은 초기 ON/OFF와 최종 상태가 같아야 성공하며 clamp/cap은 확실하게 조여져 loose하지 않아야 한다. 일반 pressing 예시와 실제 button 평가 프로토콜이 다르다. (§V-C, pp.5–7)

## 4. Method

### 4.1. Overall Pipeline

Joint position/velocity/torque → synchronized MuJoCo twin의 예상 dynamics torque → residual torque와 Jacobian으로 estimated 6D wrench → RGB·EEF pose와 ACT-style Transformer에 입력 → Cartesian pose chunk → IK → fixed-impedance joint torque controller. (§IV, pp.4–5)

### 4.2. Observation

Policy는 두 RGB image stream, FK 기반 EEF pose, estimated external force/moment를 사용한다. Joint position/velocity/torque는 estimator/controller의 입력이다. CVAE style latent Z는 학습 시 pose/action sequence에서 생성되며 inference에서 생략한다. Explicit current object pose는 입력 목록에 없다. (§IV-A, p.4)

### 4.3. Action

25 Hz의 6D EEF target-pose sequence; chunk size25와 temporal ensembling. Simulation insertion은 orientation을 고정하고 xyz만 제어한다. Torque는 low-level controller 출력이며 policy가 직접 예측하는 값이 아니다. (§IV-A/§V-C, pp.4–5; Table I, p.7)

### 4.4. Controller

IK target joint angle, measured q/v, preset K/B, feedforward gravity/Coriolis compensation으로 MIT-mode torque를 생성한다. 정책25Hz, compensation250Hz, impedance2kHz. Quasi-static task 가정으로 inertial term을 제외한다. AIRBOT Play 6DOF를 force-estimator 검증에 사용한다. (§IV-A/§V-A, pp.4–5)

### 4.5. Learning / Optimization Method

ACT 계열 Transformer 모방학습. Simulation150 demos(무접촉50, corrective100), 실물 task별30 successful demos. Haptic handheld controller는 estimated force 크기를 진동으로 사람에게 전달한다. 이 진동은 robot tactile observation이 아니다. Architecture/hyperparameter를 고정하고 추가 contact cue만 바꾸는 ablation이다. 상세 loss는 ACT를 따른다고 하며 독립 수식은 미명시이다. (§IV-C/§V, pp.5–7)

## 5. Object Information

실행 입력과 학습·평가용 정답을 구분한다.

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | 두 current RGB image의 implicit visual features | 25Hz visual-policy stream | Explicit object position vector 없음 |
| Orientation | 기타 | 두 RGB image의 implicit visual features | 25Hz | EEF orientation은 object orientation과 다름 |
| Shape / Geometry | 기타 | RGB image 및 task별 demonstrations; simulation fixed peg/hole | 시각 갱신; task geometry 고정 | Policy CAD/mesh input 없음. Estimator에는 robot model 필요 |
| Physical Parameters | 미제공 | Object numeric parameter 입력 미확인 | 해당 없음 | Robot dynamics model과 fixed controller gains는 별개 |

## 6. Missing Object Information and Compensation

Vision·position만으로 잘 드러나지 않는 접촉/체결 상태 → estimated EEF wrench → 삽입 오정렬 교정, 버튼 전환, 조임 진행을 구별하는 contact cue를 제공한다. 동일 RGB/position baseline과 raw joint-torque baseline을 비교했다. Object pose를 전혀 관측하지 않는 blind policy가 아니라 RGB를 지속 사용하는 정책이다. (§V-D, p.7)

## 7. Tactile

### 7.1. Raw Sensor

로봇 tactile sensor 사용하지 않음. Demonstrator에게 주는 vibrotactile feedback은 입력 센서가 아님.

### 7.2. Preprocessing

로봇 tactile sensor 사용하지 않음. Demonstrator에게 주는 vibrotactile feedback은 입력 센서가 아님.

### 7.3. Policy Representation

로봇 tactile sensor 사용하지 않음. Demonstrator에게 주는 vibrotactile feedback은 입력 센서가 아님.

### 7.4. Retained Information

로봇 tactile sensor 사용하지 않음. Demonstrator에게 주는 vibrotactile feedback은 입력 센서가 아님.

### 7.5. Removed / Unavailable Information

로봇 tactile sensor 사용하지 않음. Demonstrator에게 주는 vibrotactile feedback은 입력 센서가 아님.

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

내장 motor/joint torque 측정에서 추정한 EEF wrench. 별도 wrist F/T sensor를 쓰지 않는다.

### 8.2. Representation

Jacobian-transpose SVD pseudoinverse와 observed/expected dynamics torque의 차로 Fx,Fy,Fz,τx,τy,τz를 복원한다. MuJoCo twin을 q/v/torque와 동기화한다.

### 8.3. Role

Policy의 contact cue; teleoperation vibration feedback. Inner loop는 fixed impedance torque control이며 estimated wrench를 직접 force setpoint로 출력하지 않는다.

### 8.4. Required Assumptions

알려진 robot kinematics/Jacobian, 동기화된 dynamics model, 관절 torque 측정 및 EEF에 작용하는 외력의 mapping을 전제한다. Inner controller는 quasi-static을 가정한다. 임의 link의 다중 접촉을 모두 EEF wrench로 분리하는 방법은 아님.

### 8.5. Reported Limitation / Ambiguity

저자는 model inaccuracies, sensor noise, joint friction, mechanical compliance를 추정의 문제로 언급한다. Multi-contact location ambiguity나 contact patch 복원 한계는 직접 분석하지 않는다.

## 9. Other Observations

Proprioception q/v/torque는 digital twin과 estimator/control에 사용하고 policy에는 EEF pose와 wrench로 변환한다. 두 RGB camera는 online observation이다. Action chunk temporal ensemble을 사용하지만 별도 sensor history 길이/recurrent hidden state/previous-action input은 미명시이다. CVAE latent는 training-only action-sequence 정보이다.

## 10. Tactile–Other Modality Relationship

Tactile 병용이 없다. 이 연구가 검증하는 관계는 RGB+EEF position에 contact cue를 더할 때 raw joint torque보다 task-space estimated wrench가 유용한가이다. Contact locality를 tactile이 보완했다는 근거는 없다.

## 11. Training-only / Privileged Information

Actor·Critic·reward·termination·학습 데이터 생성을 따로 기록한다.

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV-A/C; §V-C, pp.4–6) |
| Critic | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV-A/C; §V-C, pp.4–6) |
| Reward | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV-A/C; §V-C, pp.4–6) |
| Termination | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§IV-A/C; §V-C, pp.4–6) |
| Curriculum | 해당 없음: 비-RL | 해당 없음 | 성공 teleoperation demonstration, simulator contact-force visualization, training-only CVAE action-sequence latent. Simulator GT actor/critic 사용이 아니라 imitation supervision이다. (§IV-A/C; §V-C, pp.4–6) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Estimated wrench 추가의 효과 | Input ablation; Representation ablation | RGB+EE position / +joint torque / +estimated EE force; 동일 architecture·hyperparameters | Simulation n50 success68/80/90%. | §V-D; PDF p.7 ; Table II |
| Task-space wrench가 raw joint torque보다 높은 실물 성공률 | Input ablation; Representation ablation | 각 조건/task n30; Pos / Pos+JT / Pos+EF | Plug46.7/63.3/80.0%; E-stop43.3/60.0/83.3%; Clamp30.0/63.3/76.6%; Cap26.6/70.0/80.0%. 원문 반올림 표기 유지; 유의성 검정 미명시. | §V-D; PDF p.7 ; Table III |
| 외력 추정 정확도 | Controlled comparison | Known static gravitational loads; pose별30 repeated estimates | Fig.4에 Z-axis error 평균/표준편차 제시. 모든6축·dynamic contact의 동등한 정확도 검증은 아님. | §V-A; PDF pp.5–6 ; Fig.4 |
| Force cue가 접촉 이벤트를 드러냄 | Failure analysis; Author explanation only | 4과업 traces 및 position-only 실패 | Force/torque peak와 contact stage가 대응; vision/position-only는 misalignment recovery 및 tightening/button state에서 실패. | §V-B/D; PDF pp.5–7 ; Fig.3 |

## 13. Author-stated Limitations

Force reconstruction은 modeled robot dynamics에 의존하고 fixed impedance를 사용한다. Controller는 quasi-static 근사에 따라 inertial term을 생략한다. (§IV-A–B, pp.4–5; §VI, p.7)

## 14. Author-stated Future Work

Variable impedance를 통한 dynamic compliance, modeling error에 강한 force estimation, implicit force reasoning을 제시한다. (§VI, p.7)

## 15. Review-relevant Findings

- F/T source는 wrist sensor가 아니라 joint torque 기반 estimated wrench이다.
- Vision·EEF pose가 모든 비교 조건에 공통으로 들어간다.
- Wrench와 raw joint torque를 동일 조건에서 비교했다.
- Fixed impedance torque execution과 policy pose output은 서로 다르다.
- Vibrotactile demonstrator feedback은 로봇 tactile sensing이 아니다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / Object pose | §IV-A p.4 |
| Tactile | §IV-C p.5: demonstrator feedback only |
| F/T | §III-B/§IV-B pp.3–5, Eq.2/6 |
| Reward / Critic | 해당 없음: imitation learning |
| Ablation | §V-D p.7, Tables II–III |
| Limitation / Future | §IV p.4; §VI p.7 |
