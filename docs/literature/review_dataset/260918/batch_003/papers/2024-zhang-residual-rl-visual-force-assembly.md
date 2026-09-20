# A residual reinforcement learning method for robotic assembly using visual and force information

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B100`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Zhuangzhuang Zhang; Yizhao Wang; Zhinan Zhang; Lihui Wang; Huang Huang; Qixin Cao
- Year: 2024
- Venue: Journal of Manufacturing Systems 72, 245–262
- DOI / arXiv: 10.1016/j.jmsy.2023.11.008 / Not stated
- PDF version: Publisher PDF
- Page count: 18
- SHA-256: `861e2ce7fee3a3c2e59852e8e90bb9630063eaa176739dbf8398db962d1fca19`
- PDF filename: Zhang 등 - 2024 - A residual reinforcement learning method for robotic assembly using visual and force information.pdf
- 확인 범위: PDF pp.1–18 전체: abstract, related work, MDP, visual encoder, force controller, PPO, reward/safety, simulation/real setup, ablations, discussion, conclusion. Key pages 4, 7, 11, 15, 17 rendered.

## 2. Relevance to This Review

`Relevant`

The paper explicitly assigns global relative-pose search to vision and local contact handling to wrist F/T, while keeping force out of the learned actor and putting it in a controller. It includes modality/controller ablations and exposes simulation GT used in the staged reward.

## 3. Task

Vision-guided peg-in-hole assembly with force-controlled reaching, search and insertion stages

## 4. Method

### 4.1. Overall Pipeline

Eye-in-hand RGB → CNN → PPO visual action; wrist F/T → stage logic + explicit force/admittance controller; sum/replace commands → IK → UR10 position command.

### 4.2. Observation

PPO actor and critic receive the 512-D CNN feature from current RGB. Wrist F/T is processed by the separate force policy/controller and stage machine, not concatenated into the actor observation.

### 4.3. Action

3D Cartesian displacement Δx and z-axis rotation increment Δα_z from visual policy; force controller adds/replaces residual commands

### 4.4. Controller

Modified parallel explicit-force/admittance/position controller; IK to position commands

### 4.5. Learning / Optimization Method

PPO with shared CNN feature extractor and separate actor/value MLPs. Simulation domain randomization supports transfer; real policy can be fine-tuned.

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Tracking | Implicit feature from eye-in-hand RGB | Each policy step | No explicit numeric part position is given to actor. [§4.2–4.4, PDF pp.5–7] |
| Orientation | Tracking | Implicit relative z-axis pose feature from RGB | Each policy step | Action controls only z-axis rotation in the flat setup. [§3–4.2, PDF pp.4–5] |
| Shape / Geometry | 기타 | Implicit visual appearance; no explicit geometry | Each image | Claims no geometric parameter requirement after training. [Abstract and §8, PDF pp.1,17] |
| Physical Parameters | 미제공 | Not actor input | No | Force-control parameters are manually tuned rather than object-estimated. [§4.3 and §7, PDF pp.5–6,16–17] |

## 6. Missing Object Information and Compensation

Explicit part geometry and numeric current pose are not provided
→ RGB latent relative-pose features + wrist F/T + analytical hybrid controller
→ vision performs broad search/alignment while force feedback recognizes and regulates physical interaction.

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§3–8, PDF pp.4–17]

### 7.2. Preprocessing

사용하지 않음. [§3–8, PDF pp.4–17]

### 7.3. Policy Representation

사용하지 않음. [§3–8, PDF pp.4–17]

### 7.4. Retained Information

사용하지 않음. [§3–8, PDF pp.4–17]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§3–8, PDF pp.4–17]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

ATI Mini45 six-axis F/T sensor between end-effector and gripper. [§5.1, PDF p.9]

### 8.2. Representation

Median-filtered, dead-zoned, gravity-compensated 6D wrench; F_z thresholds and force error in task frame. [§4.3, PDF pp.5–6]

### 8.3. Role

Detect stage transitions/completion, track desired normal force, provide admittance response, and trigger fail-safe reset. It is controller input, not PPO actor input. [§4.1, §4.3–4.6, PDF pp.4–8]

### 8.4. Required Assumptions

Known task frame and surface normal, calibrated transform/gravity compensation, rigid objects, manually tuned force/admittance gains. [§4.3 and §5.1, PDF pp.5–6,9]

### 8.5. Reported Limitation / Ambiguity

Wrench does not supply explicit part pose/locality; manually tuned parameters may not transfer across materials and hardness. [§7, PDF pp.16–17]

## 9. Other Observations

- Vision: normalized 3×240×320 RGB, CNN to 512 features.
- Proprioception: robot pose/IK/controller state, not PPO actor input.
- History: no explicit actor stack.
- Goal: reward uses part-relative pose during training; actor infers direction visually.

## 10. Tactile–Other Modality Relationship

Tactile is not used. The claimed visual–force complement is phase and module specific: vision produces search increments, while F/T switches phases, regulates normal force and corrects disturbances. Sensor combination/controller ablations directly test parts of this division.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | No | Current RGB image features | No part GT is fed. [§3–4.4, PDF pp.4–7] |
| Critic | No | Same shared CNN features | No asymmetric critic state. [§4.4 and Fig.7, PDF p.7] |
| Reward | Yes | Exact relative position d, orientation α and insertion height z in simulation | These variables are not the stated actor observation. [Eq.12, PDF pp.7–8] |
| Termination | No | F/T completion/contact plus force/action/time safety limits | Execution-detectable monitor. [§4.1 and §4.6, PDF pp.4,8] |
| Curriculum | Not applicable | No curriculum | Domain randomization is used instead. [§5.4, PDF p.11] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Vision and modified force control are jointly needed | Sensor/controller ablation | Full model vs no vision vs vision+force threshold vs vision+admittance | Full model reaches 100% in all simulated settings; baselines often 0–35% | §5.2 and §6.1; PDF pp.9–14 ; Table 2 ; Fig.10 |
| Full model is robust across pose, clearance and shape | Controlled comparison | 3 initial ranges, 3 clearances, 3 shapes | Full model maintains 100% in reported simulation tests | §5.2–6.1; PDF pp.9–14 ; Table 2 |
| Sim-to-real and fine-tuning improve hardware performance | Controlled comparison | Direct sim-to-real vs real fine-tuning | Square 1-mm case improves from 45% to 95%; unseen shapes also improve | §6.2; PDF pp.15–16 ; Table 3 ; Fig.13 |

## 13. Author-stated Limitations

저자 명시: RGB는 brightness/color와 제한된 FOV에 민감하고, force-control parameters를 수동 조정하므로 재료·경도 변화에 제한이 있다. Simulation–hardware gap이 남고, non-flat task는 최대 6D action으로 확대되어 학습 시간이 늘어난다. [§7, PDF pp.16–17]

## 14. Author-stated Future Work

저자 명시: depth/preprocessed image, force-control parameter의 RL 자동 조정, visual+force+proprioceptive RL observation을 사용하는 variable-stiffness task를 연구한다. [§7–8, PDF pp.16–17]

## 15. Review-relevant Findings

- Actor observation은 RGB feature뿐이며 wrist F/T는 별도 controller와 stage machine 입력이다.
- Current part pose는 수치로 주어지지 않고 RGB에서 implicit relative-pose feature로 추출된다.
- Vision은 spatial search, F/T는 contact detection·force regulation·insertion completion을 담당한다.
- Reward는 simulation exact relative position/orientation/height를 사용하므로 actor observation과 분리해야 한다.
- Sensor/controller ablation이 있어 visual–force 조합의 유용성에 직접 evidence가 있다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | §3 and §4.4, PDF pp.4,7 |
| Object pose | §4.2, PDF p.5 |
| Tactile | 사용하지 않음 |
| F/T | §4.1/4.3 and §5.1, PDF pp.4–6,9 |
| Reward | Eq.12, PDF pp.7–8 |
| Critic | §4.4, PDF p.7 |
| Ablation | Fig.10 and Table 2, PDF pp.11–14 |
| Limitation | §7, PDF pp.16–17 |
