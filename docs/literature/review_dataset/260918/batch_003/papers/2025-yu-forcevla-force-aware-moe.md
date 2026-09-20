# ForceVLA: Enhancing VLA Models with a Force-aware MoE for Contact-rich Manipulation

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B094`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Jiawen Yu; Hairuo Liu; Qiaojun Yu; Jieji Ren; Ce Hao; Haitong Ding; Guangyu Huang; Guofan Huang; Yan Song; Panpan Cai; Wenqiang Zhang; Cewu Lu
- Year: 2025
- Venue: 39th Conference on Neural Information Processing Systems (NeurIPS 2025)
- DOI / arXiv: Not stated / Not stated
- PDF version: NeurIPS 2025 paper with supplementary material and checklist
- Page count: 31
- SHA-256: `ccc9f854bd3d158f6f892b91294c7b1b16d48e79d69d27edb722b730452f1181`
- PDF filename: Yu 등 - ForceVLA Enhancing VLA Models with a Force-aware MoE for Contact-rich Manipulation.pdf
- 확인 범위: PDF pp.1–31 전체(본문, limitations, supplementary experiments/failure analyses/checklist); observation/action, sensor/dataset, main/generalization/fusion/masking ablations과 failure cases를 확인하고 Figures 3/5/7 및 Tables 1–3/5–6 렌더 검토.

## 2. Relevance to This Review

`Relevant`

Vision-language-action policy에 single-step 6-axis estimated TCP wrench를 명시적으로 통합하고 force/no-force, naive fusion, MoE fusion ablations과 visual occlusion/failure analysis를 제공한다. F/T가 current numeric object pose 없이 contact dynamics를 보완하는 역할과 global wrench의 source/precision 한계를 직접 분석할 수 있다.

## 3. Task

Flexiv arm이 language instruction에 따라 bottle pump 누르기, plug insertion, USB insertion, whiteboard wiping, cucumber peeling의 다섯 contact-rich tasks를 수행한다. Object/height/visual-occlusion/unstable-socket variations에서 contact force에 따라 reorient, retry, pressure/trajectory를 조절해 task-specific success criterion을 만족하는 것이 목표다. [§5.1–5.5, PDF pp.6–10]

## 4. Method

### 4.1. Overall Pipeline

Base/wrist RGB + language → pretrained SigLIP/PaliGemma VLM features; current TCP pose/gripper width → state token; world-frame estimated 6-axis TCP wrench → linear force token → post-VLM self-attention + 4-expert top-1 FVLMoE fusion → fused guidance를 π0 conditional flow-matching action head에 주입 → target TCP-pose/gripper-width action chunk → robot execution → 다음 sensor observation으로 closed-loop replanning. [§3–4, pp.4–6]

### 4.2. Observation

At timestep $t$, policy observation은 base RGB $V_t^b$, wrist RGB $V_t^h$, 7-D proprioception $s_t$ (TCP Cartesian position, Euler orientation, gripper width), single-timestep world-frame estimated wrench $f_t ∈ R^6$, language instruction이다. Numeric object pose/shape/physical parameter는 입력이 아니다. [§3, p.4]

### 4.3. Action

$H$-step low-level executable action chunk이며 dataset action은 target TCP pose와 gripper width로 표현한다. Conditional flow matching head가 noisy action trajectory를 denoise해 예측한다. [§3/§4.2–4.3, pp.4–6]

### 4.4. Controller

Target TCP pose/gripper width를 Flexiv Rizon에 실행하지만 servo/control mode, gains, action horizon/frequency는 원문에서 충분히 명시되지 않는다. Policy는 action chunk 후 새 visual/force observation을 받아 갱신한다. [§3–4, pp.4–6]

### 4.5. Learning / Optimization Method

244 real teleoperation trajectories, 약 140k synchronized timesteps와 task당 약 50 expert demonstrations로 π0-based VLA를 supervised fine-tuning한다. Force token, post-VLM 4-expert top-1 MoE, flow-matching action decoder를 end-to-end 학습한다. RL critic/reward는 없다. [§4.3/§5.1, pp.6–7]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Base/wrist RGB에 implicit; numeric object position 미제공 | Yes | Demonstrations에서 object position을 다양화하지만 current GT pose vector는 actor input이 아니다. [§3/§4.3 pp.4,6] |
| Orientation | 기타 | RGB appearance에 implicit; numeric object orientation 미제공 | Yes | Demonstrations에서 orientation을 variation하지만 policy input은 images다. [§4.3 p.6] |
| Shape / Geometry | 기타 | RGB에 implicit; language/object appearance prior | Yes | Full mesh/CAD/dimensions/point cloud는 제공하지 않는다. [§3–4 pp.4–6] |
| Physical Parameters | 미제공 | Mass/friction/compliance를 explicit input으로 제공하지 않음 | 해당 없음 | Physical uncertainty는 object/height/socket variations로 평가된다. [§5.3 pp.8–9] |

## 6. Missing Object Information and Compensation

Numeric current object pose/shape/physical parameters 미제공 → two-view RGB + pretrained vision-language context + TCP/gripper proprioception → scene/object/task configuration을 implicit하게 표현한다.

Vision만으로 contact occurrence/load/occluded interaction state 부족 → single-step estimated 6-axis world-frame TCP wrench → MoE가 task phase에 맞는 force-conditioned action chunk를 생성하고 insertion retry, pressure correction, stop behavior를 조절한다. Contact location/patch를 직접 추정하지는 않는다. [§3–5, pp.4–10; Appendix E–F pp.24–25]

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. [§1–6 and Appendix, PDF pp.1–31]

### 7.2. Preprocessing

사용하지 않음. [§1–6 and Appendix, PDF pp.1–31]

### 7.3. Policy Representation

사용하지 않음. [§1–6 and Appendix, PDF pp.1–31]

### 7.4. Retained Information

사용하지 않음. [§1–6 and Appendix, PDF pp.1–31]

### 7.5. Removed / Unavailable Information

사용하지 않음. [§1–6 and Appendix, PDF pp.1–31]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Flexiv Rizon platform에서 얻는 estimated external wrench applied at TCP. 원문은 integrated/high-cost force-torque sensing을 언급하지만 physical wrist F/T인지 joint-torque estimator인지 정확한 hardware/estimator source는 명시하지 않으므로 둘 중 하나로 단정할 수 없다. [§3 p.4; §6 p.10]

### 8.2. Representation

한 timestep의 world-frame $f_t={f_{tx},f_{ty},f_{tz},m_{tx},m_{ty},m_{tz}} ∈ R^6$. Linear projection으로 force token을 만든다. History, derivative, filtering은 명시되지 않는다. [§3 p.4; §4.2 p.5]

### 8.3. Role

Actor observation이자 MoE fusion cue로 contact occurrence/load direction, phase-dependent interaction dynamics를 action decoder에 제공한다. Insertion retry/angle adjustment, pumping pressure, wiping contact, peeling force regulation에 사용된다. [§4.1–5.5 pp.4–10; Appendix E–F pp.24–25]

### 8.4. Required Assumptions

Estimated TCP wrench calibration/precision, known world/TCP transform, timestamp-synchronized demonstration streams, contact dynamics가 expert data distribution에서 학습 가능하다는 조건이 필요하다. [§3/§4.3 pp.4,6; §6 p.10]

### 8.5. Reported Limitation / Ambiguity

Estimated wrench가 high-fidelity direct measurement의 precision을 모두 포착하지 못할 수 있다. Global wrench에서 contact point/patch와 multiple contacts를 분리하지 않으며 그 locality ambiguity를 직접 실험하지 않는다. Integrated/high-cost sensing은 접근성을 제한한다. [§6, p.10]

## 9. Other Observations

Vision은 static RealSense D435(1280×720, 30 FPS)와 wrist RealSense D415(640×480, 30 FPS), language는 task instruction이다. Proprioception은 current TCP x/y/z, Euler angles와 gripper width다. Wrench history/previous action/recurrent hidden state/explicit state estimator는 observation formulation에 없다. [§3 p.4; §4.3 p.6]

## 10. Tactile–Other Modality Relationship

Vision/language는 semantic scene and goal context를, proprioception은 robot configuration을, 6-D wrench는 immediate global contact dynamics를 제공한다. FVLMoE가 force token을 VLM 뒤에서 융합해 action을 조절한다. Force/no-force and force-masking ablations은 wrench의 역할을 직접 검증한다. Tactile spatial sensor는 없으므로 F/T에 local contact distribution을 추가하는 역할 분담은 검증하지 않는다. [§5.2–5.5 pp.7–10; Appendix F pp.24–25]

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | 비-RL real-world imitation/VLA fine-tuning. Expert actions are supervised labels; actor observation과 별도의 simulator GT critic/reward/termination은 없다. [§3–6, PDF pp.4–10] |
| Critic | Not applicable | 비-RL | 비-RL real-world imitation/VLA fine-tuning. Expert actions are supervised labels; actor observation과 별도의 simulator GT critic/reward/termination은 없다. [§3–6, PDF pp.4–10] |
| Reward | Not applicable | 비-RL | 비-RL real-world imitation/VLA fine-tuning. Expert actions are supervised labels; actor observation과 별도의 simulator GT critic/reward/termination은 없다. [§3–6, PDF pp.4–10] |
| Termination | Not applicable | 비-RL | 비-RL real-world imitation/VLA fine-tuning. Expert actions are supervised labels; actor observation과 별도의 simulator GT critic/reward/termination은 없다. [§3–6, PDF pp.4–10] |
| Curriculum | Not applicable | 비-RL | 비-RL real-world imitation/VLA fine-tuning. Expert actions are supervised labels; actor observation과 별도의 simulator GT critic/reward/termination은 없다. [§3–6, PDF pp.4–10] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Force feedback improves contact-rich task performance when fused effectively | Sensor combination / controlled comparison | π0-base without force; direct-force baseline; ForceVLA MoE fusion | Average success is 37.3% without force, 40.2% with direct force, and 60.5% with ForceVLA. | §5.2; PDF pp.7–8 ; Fig.5 |
| Post-VLM MoE fusion is better than naive/early fusion | Representation/architecture ablation | Baseline; linear/MoE before VLM; concatenate after VLM; FVLMoE | Reported success: 45%, 55%, 0%, 60%, 80%, respectively. | §5.4; PDF p.9 ; Table 3 |
| Force improves robustness under visual occlusion and physical variation | Controlled generalization comparison | Object/height/occlusion/unstable-socket variations across force/no-force models | ForceVLA averages 63.78% and reaches 90% under visual occlusion; authors report force-conditioned depth/pose adjustment and fewer torque-limit failures. | §5.3; PDF p.8 ; Table 2 |
| The trained ForceVLA depends on force at inference | Input masking ablation | Full ForceVLA vs same model with force input masked | Plug 80→20%, USB 25→0%, pump 67→30%, wipe 27→26.7%. | Appendix F; PDF pp.24–25 ; Table 6 |
| Force helps but does not solve vision-limited alignment | Failure analysis | With-force and without-force failures across tasks | USB remains low due insufficient visual clarity; no-force variants repeat stereotyped paths, over-force, wipe in air, or fail to stop. | Appendix E–F; PDF pp.24–25 ; Table 6 |

## 13. Author-stated Limitations

저자들은 estimated external wrench가 direct high-fidelity sensor만큼 precise하지 않을 수 있고 extreme haptic sensitivity tasks에서 제한될 수 있다고 명시한다. Integrated/high-cost force sensing platform은 accessibility를 낮춘다. Real-world-only dataset은 sim-to-real gap을 피하지만 diverse contact-rich tasks의 large-scale training을 위한 high-fidelity simulation을 구축하지 못했다. USB alignment처럼 fine visual clarity가 부족한 failure도 보고한다. [§6 p.10; Appendix E p.24]

## 14. Author-stated Future Work

Superior force sensors 또는 advanced calibration, lower-cost platform의 external/retrofitted force sensors에 대한 적응 평가, high-fidelity simulation과 large-scale simulated training으로 task 범위를 확장하는 방향을 제시한다. [§6, p.10]

## 15. Review-relevant Findings

- Actor는 two-view RGB, language, 7-D TCP/gripper state와 single-step world-frame 6-D estimated TCP wrench를 사용한다.
- Current numeric object pose/shape/physical parameters는 제공되지 않는다.
- Wrench source는 estimated external TCP wrench로 명시되지만 physical wrist sensor와 joint-torque estimator 중 어느 것인지는 명시되지 않는다.
- Global wrench는 contact dynamics/load를 보완하지만 contact locality/patch/multi-contact separation을 제공하지 않는다.
- Direct-force, fusion, generalization, force-masking ablations이 modality의 유용성과 integration 방식의 중요성을 검증한다.
- Tactile spatial sensing은 사용하지 않아 tactile이 F/T locality를 보완하는 직접 evidence는 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / wrench representation | §3 p.4 |
| Force fusion / action pipeline | §4.1–4.2 pp.4–6 |
| Dataset / action / hardware | §4.3 p.6 |
| Main and force baseline results | §5.1–5.2 pp.6–8; Fig.5 |
| Generalization | §5.3/Table 2 p.8 |
| Fusion ablation / case studies | §5.4–5.5 pp.9–10 |
| Force masking / failures | Appendix E–F pp.24–25 |
| Limitation / Future | §6 p.10 |
