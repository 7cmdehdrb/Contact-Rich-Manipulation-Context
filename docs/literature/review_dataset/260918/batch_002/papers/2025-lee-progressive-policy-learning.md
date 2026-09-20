# Progressive Policy Learning: A Hierarchical Framework for Dexterous Bimanual Manipulation

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B040`
- Authors: Kang-Won Lee; Jung-Woo Lee; Seongyong Kim; Soo-Chul Lim
- Year: 2025
- Venue: Mathematics 13(22), 3585
- DOI / arXiv: 10.3390/math13223585 / Not stated
- PDF version: Publisher open-access PDF; published 8 November 2025
- Version note: 선택 범위 내 다른 버전 없음
- Page count: 18
- SHA-256: `40965d06e240b0cc50077cf2deebae06c09164a6b7fd7a320b23bab14f23294a`
- PDF filename: `Lee 등 - 2025 - Progressive Policy Learning A Hierarchical Framework for Dexterous Bimanual Manipulation.pdf`
- 읽은 범위: PDF pp.1–18 전체(본문, 수식, 표·그림, 결론, 참고문헌). Fig.5/Table 2의 비교 수치를 렌더 확인. 별도 Video S1은 확인하지 않음.
- 근거: 이번 배치의 PDF 원문에서 새로 분석했다. 기존 상세 노트는 재사용하지 않았다. 아래 페이지는 PDF 1-based page다.

## 2. Relevance to This Review

**Partially Relevant**. 두 손의 cube grasp-and-rotate RL을 실행 중 RGB-D/ArUco로 갱신되는 cube body/layer pose와 keypoint에 의존해 수행하며 tactile/F/T observation은 없다. 다만 measured wrench가 아닌 외력 disturbance와 접촉 sensing을 분리하고, 저자가 vision-centric state estimation의 physical-interaction 정보 부재를 실물 실패 원인으로 명시해 tactile-vision fusion을 후속 과제로 제시한다. 따라서 제한 sensing 정책의 직접 근거가 아니라 current-pose vision 및 미관측 접촉의 비교군으로 포함한다.

Screening 위치: Abstract/§3.1–3.2, PDF pp.1,4–8; §4.4–5, pp.13–16.

## 3. Task

왼손이 cube를 안정적으로 잡고 오른손이 지정 layer를 CW/CCW 90° 회전한다. Holding과 rotating을 별도 MDP로 학습하되 실행 시 동시에 동작한다. (§3.1–3.3, PDF pp.4–8)

## 4. Method

### 4.1. Overall Pipeline

Train a left-hand holding PPO policy under random wrenches, freeze it, then train the right-hand rotation PPO on states induced by the executing holder; deploy both concurrently with visual object tracking. (§3, pp.4–11)

### 4.2. Observation

Shared state contains hand joints, cube body/layer pose, object keypoints, layer joint, holding goal, fingertip positions and previous actions. Policies use task-specific subsets; joint/action have 3-step history. (§3.1, pp.4–6)

### 4.3. Action

Normalized relative joint-position targets: 16D left and 17D right including wrist; scaled, accumulated, clipped and EMA filtered. (§3.1, Eq.(5), pp.6–7)

### 4.4. Controller

EMA-smoothed desired joints are tracked by low-level PD torque control at 60 Hz in simulation and reality. (§3.1–3.2, pp.6–8)

### 4.5. Learning / Optimization Method

PPO with separate holding/rotation rewards, 2048 parallel IsaacLab environments and staged progressive training; MAPPO and naive chaining are baselines. (§3.4–4.3, pp.9–13)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Cube body/layer 3D pose from simulator; real ArUco markers via RGB-D | 60 Hz during execution | Current pose and holding goal pose are separate; the goal is not a current-object observation. 근거: §3.1–3.2, Fig.3, PDF pp.4–8; §4.4, pp.13–14 |
| Orientation | Tracking | Cube body/layer quaternion and layer joint angle; real marker-derived pose | 60 Hz during execution | Current orientation, desired holding pose and target layer angle are distinct quantities. 근거: §3.1–3.4, pp.4–10; §4.4, pp.13–14 |
| Shape / Geometry | 기타 | Fixed cube/layer digital twin and predefined local keypoints transformed by current pose | Keypoint world positions update with pose | No general shape vector; diverse-object transfer was not tested. 근거: §3.1–3.3, pp.4–8; §5, pp.15–16 |
| Physical Parameters | 미제공 | Object mass randomized in simulation; no actor parameter input listed | Actor 없음 | Friction variation is proposed future work rather than current observation. 근거: §3.5/Table 1, p.11; §4.4–5, pp.14–16 |

## 6. Missing Object Information and Compensation

Current object pose는 미제공이 아니라 vision으로 계속 Tracking된다. 반면 contact/slip/force는 관측하지 않아 joint/action history, domain randomization과 visual pose/keypoint로 정책을 구성한다. 저자는 이 한계를 tactile-vision fusion의 필요성으로 연결하지만 tactile 보완 효과를 실험하지 않았다. (§3.1–3.5, pp.4–11; §4.4–5, pp.14–16)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. 실물 시스템은 RGB-D/ArUco와 robot proprioception을 사용하고 tactile-equipped hand는 future work다. (§3.2/§4.4–5, pp.7–8,13–16)

### 7.2. Preprocessing

해당 없음. (§3.2/§4.4–5, pp.7–8,13–16)

### 7.3. Policy Representation

해당 없음. Contact state, slip, deformation image가 actor에 제공되지 않는다. (§3.1–3.2, pp.4–8)

### 7.4. Retained Information

해당 없음. (§3.1–3.2, pp.4–8)

### 7.5. Removed / Unavailable Information

Vision-centric state가 physical interaction information을 제공하지 않는다는 저자 한계를 유지한다. (§4.4–5, pp.14–16)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

측정 F/T 센서는 없다. Simulation의 random external wrench와 실물의 human taps/pulls는 입력이 아니라 disturbance다. (§3.1/§4.4, pp.5,14)

### 8.2. Representation

Actor에 wrench representation 없음. Training disturbance만 6D force/torque bounds로 정의된다. (§3.1, Eq.(2), p.5)

### 8.3. Role

Left holding policy의 disturbance robustness를 훈련·정성 평가한다. Contact 또는 object state를 추정하지 않는다. (§3.1/§4.4, pp.5,14)

### 8.4. Required Assumptions

Measured wrench 기반 localization에 해당 없음. 외력 분포와 hardware-limit bounds가 training assumption이다. (§3.1, p.5)

### 8.5. Reported Limitation / Ambiguity

Wrench가 관측되지 않으므로 force source/contact location ambiguity를 푸는 방법이 아니다. 저자는 tactile-vision fusion을 후속 과제로 둔다. (§4.4–5, pp.14–16)

## 9. Other Observations

Robot proprioception과 previous-action history가 있다. Goal pose/target layer angle은 current object pose와 분리했다. Training external wrench는 observation이 아니다. (§3.1–3.5, pp.4–11)

## 10. Tactile–Other Modality Relationship

Tactile/F/T modality 관계를 실험하지 않았다. Visual pose와 proprioception이 현재 시스템의 실행 입력이며 tactile는 저자 제안 future work다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Actor | Simulation Yes; real estimated | Current cube body/layer pose, keypoints, layer state, robot state/history and goals | Sim object state is noisy GT-like observation; real deployment requires 60 Hz ArUco estimates | §3.1–3.2, pp.4–8; §4.4, pp.13–14 |
| Critic | Not stated | Value network has same stated MLP sizes; separate critic observation list absent | Asymmetric/full-state critic must not be inferred | §3.5, p.11 |
| Reward | Yes | Object-goal position/z-axis error, layer angle/velocity, transformed object keypoints, grasp indicator, action penalty | Simulation training only; these quantities are not all independent sensor measurements | §3.4, Eqs.(6)–(11), pp.9–10 |
| Termination | Yes | Drop, pose-alignment tolerance, inability to align/rotate by time limit; 5-degree real success | Real success uses visual layer angle and observed failure modes | §3.3, p.8; §4.4, p.14 |
| Curriculum | Yes | Successful holding-state distribution initializes rotating policy; mass/pose/keypoint/action noise DR | Training-only state construction; not a runtime tactile signal | §3.1 Eq.(4), pp.5–6; §3.5/Table 1, p.11 |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Progressive state-distribution conditioning의 효과 | Architecture comparison | HPPL vs naive chaining vs MAPPO; same rewards/observations/environment; 12 seeds | Simulation success 0.821±0.029 vs 0.225±0.031 and 0.433±0.034; normalized reward 0.962±0.021 vs 0.459±0.071 and 0.640±0.043. | §4.1–4.3; Table 2/Fig.5, PDF pp.11–13 |
| Zero-shot real execution feasibility | Real-world feasibility | Best HPPL only; CW/CCW, 65 trials | 41/65 successes, 63.08%. No baseline or tactile comparison on hardware. | §4.4, PDF pp.13–15 |
| 미관측 접촉 정보와 visual failure | Failure analysis; Author explanation only | Real failures under contact and marker occlusion | Excessive contact causes cube displacement; marker occlusion increases pose error. Authors attribute limitations partly to absent physical interaction information. | §4.4–5, PDF pp.14–16 |

## 13. Author-stated Limitations

Hand-crafted reward 의존, marker occlusion/pose error 및 sim-to-real mismatch로 인한 실물 성능 저하, vision-centric state의 physical interaction 정보 부재, 다양한 task/platform으로의 generalization 미검증을 명시한다. (§4.4–5, pp.14–16)

## 14. Author-stated Future Work

Tactile-vision fusion과 tactile/friction randomization, contact-aware rewards; IRL/IL을 통한 reward-design 부담 완화; task와 platform 확대 평가를 제시한다. (§4.4–5, pp.15–16)

## 15. Review-relevant Findings

- Actor는 current cube/layer pose와 keypoints를 simulation state 또는 실물 ArUco 추정으로 계속 받는다.
- Goal pose/angle과 current pose를 구분해야 한다.
- External wrench는 disturbance이지 F/T observation이 아니다.
- Reward와 termination은 object/layer GT-like state를 사용한다.
- Value-network input은 별도로 명시되지 않았다.
- Tactile의 효과는 future proposal이며 현재 성과가 아니다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| State / actor observations | §3.1, PDF pp.4–6 |
| Controller / visual tracking | §3.1–3.2, pp.6–8 |
| Reward / termination | §3.3–3.4, pp.8–10 |
| Training GT / randomization | §3.5, p.11 |
| Baseline results | §4.1–4.3, pp.11–13; Table 2/Fig.5 |
| Real failure / limitations / future | §4.4–5, pp.14–16 |
