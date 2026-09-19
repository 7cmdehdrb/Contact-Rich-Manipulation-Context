# A Contact Model based on Denoising Diffusion to Learn Variable Impedance Control for Contact-rich Manipulation

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B062
- Authors: Masashi Okada; Mayumi Komatsu; Tadahiro Taniguchi
- Year: 2024
- Venue: IEEE/RSJ IROS 2024
- DOI / arXiv: 10.1109/IROS58592.2024.10801976 / Not stated
- PDF version: IEEE publisher PDF, pp.7286–7293; Appendix A
- Page count: 8
- SHA-256: d11c40991f1903fb8ff57243099de87f180bd3d5e74f2c8b225bc075c6068c8e
- PDF filename: Okada 등 - 2024 - A Contact Model based on Denoising Diffusion to Learn Variable Impedance Control for Contact-rich Ma.pdf
- 읽은 범위: PDF pp.1–8 본문 및 포함된 부록을 새로 확인; 핵심 표·그림 렌더링 확인

근거는 이번 배치의 PDF 원문이며 기존 상세 노트는 사용하지 않았다. 페이지는 PDF의 1-based page다.

## 2. Relevance to This Review

**Partially Relevant**. Demonstration trajectory가 explicit surface model을 대신하는 geometry prior이며 force trajectory를 예측해 variable stiffness를 조정한다. Online tactile compensation 연구는 아니지만 object geometry 없이 force-based contact task를 성립시키는 추가 정보와 force의 학습·평가 역할을 분석하는 데 유용하다.

## 3. Task

Franka Panda로 curved surface wiping에서 demonstration contact-force trajectory를 재현하면서 stiffness합을 낮춘다. Success rate 대신 force RMSE와 compliance objective의Pareto hypervolume을평가한다. (§III–V pp.2–7)

## 4. Method

### 4.1. Overall Pipeline

Demonstrated EEF path+demonstrated force+candidate stiffness→attractor path 계산; demonstrated path/attractor/stiffness→DCM predicted force sequence→multiobjective Bayesian optimization→selected stiffness trajectory→impedance controller. (§III–IV pp.2–4)

### 4.2. Observation

DCM은 전체 demonstration EEF trajectory, attractor/reference trajectory, stiffness 및 diffusion noisy force sequence/step을 받는다. 실제 object pose, mesh, tactile, vision을입력하지 않는다. Force observation은 data collection·objective evaluation의 target으로 사용되며 online reactive policy observation으로 명시되지 않는다. (Fig.3–4 p.4)

### 4.3. Action

Trajectory phases별constant stiffness를optimization변수로사용. Damping과attractor는demonstrated position/derivatives/forces와stiffness로계산한다. Phase segmentation은선행method를따르며세부미명시. (§III.B pp.2–3)

### 4.4. Controller

Cartesian impedance model은6D EEF pose와 externalforce/torque, desired inertia/damping/stiffness로 정의한다. 실제 joint-command 변환 및force센서mount/source는미명시. (§III.A p.2)

### 4.5. Learning / Optimization Method

RL이아닌supervised denoising diffusion model+multiobjective Bayesian optimization. RetNet score network, inputs/outputs[-1,1]정규화. Sim spiral1600train/30test; realspiral80train/20test; simpretrain후realfinetuning. Diffusion30steps비교, robot-free optimization1000virtualtrials. (§IV–V pp.3–6; Appendix A p.8)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Current workpiece pose 입력 없음 | 없음 | Demonstrated robot path는 current object pose가 아님 (§IV.A p.3) |
| Orientation | 미제공 | Workpiece orientation input 없음 | 없음 | EEF reference orientation과 구분 (Fig.3 p.4) |
| Shape / Geometry | 기타 | Demonstration EEF trajectory에 surface geometry가implicit하게제공됨 | 고정 demonstration | 저자가 geometry prior 역할을직접명시 (§IV.A.1 p.3) |
| Physical Parameters | 미제공 | Explicit object physical parameter input 없음 | 없음 | Learned contact model/data에내재 (§I p.1; §IV.A p.3) |

## 6. Missing Object Information and Compensation

Explicit environment geometry/friction/elastic model의구축어려움 → demonstrated robot trajectory + force trajectories + learned contact model → reference/stiffness에대한하중변화를예측한다. Demonstrated trajectory가surface geometry를implicit하게제공한다는저자명시가있다. 이것은 arbitrary unknown surface의online localization 검증이아니다. (§I p.1; §IV.A p.3)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. (§III–V pp.2–7)

### 7.2. Preprocessing

사용하지 않음. (§III–V pp.2–7)

### 7.3. Policy Representation

사용하지 않음. (§III–V pp.2–7)

### 7.4. Retained Information

사용하지 않음. (§III–V pp.2–7)

### 7.5. Removed / Unavailable Information

사용하지 않음. (§III–V pp.2–7)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

End-effector external force/torque를observed/demonstrated값으로정의. 실제sensor model·mount·joint-torque추정여부는미명시; Panda라는명칭만으로추정하지않음. (§III.A–B p.2; §V.A p.5)

### 8.2. Representation

Model F는6D force/torque로정의; 결과그림은Fx/Fy(tangential),Fz(normal)를표시. 전체force trajectory를예측하며moment실험분석범위는미명시. (§III.A p.2; Figs.9/11 p.6)

### 8.3. Role

Demonstration target; supervised prediction target; force-RMSE objective; predictedforce를사용한offline stiffness search. (§III.B–IV pp.2–4)

### 8.4. Required Assumptions

F/T-only localization하지않음. Demonstration path/forces, phase-basedstiffness, robotimpedance model 및task-specificdata가필요. (§III–IV pp.2–4)

### 8.5. Reported Limitation / Ambiguity

Net-wrench contact ambiguity를직접논의하지않음. Real forceprediction정확도부족으로task-objective쪽Pareto해를찾지못하는한계를보고. (§V.D p.6)

## 9. Other Observations

EEF demonstration position/orientation 및그velocity/acceleration은reference계산에사용한다. RetNet recurrentstate는trajectory prediction model의내부이며onlinepolicyhistory로기록하지않는다. Previousaction/vision/objectstate estimator는미명시또는해당없음. (§III.B p.3; Fig.4 p.4)

## 10. Tactile–Other Modality Relationship

Tactile 병용은없다. Force정보의부족분을tactile로보완한실험이아니라known demonstration geometry와learned dynamics를활용한forceprediction/stiffness optimization이다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부·비고 |
| --- | --- | --- | --- |
| Actor | 해당 없음 | 비-RL | 해당 없음 (§III–IV pp.2–4) |
| Critic | 해당 없음 | 비-RL | 해당 없음 (§III–IV pp.2–4) |
| Reward | 해당 없음 | 비-RL | 해당 없음 (§III–IV pp.2–4) |
| Termination | 해당 없음 | 비-RL | 해당 없음 (§III–IV pp.2–4) |
| Curriculum | 해당 없음 | 비-RL | 해당 없음 (§III–IV pp.2–4) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Iterative diffusion의효과 | Representation ablation | Single forward RetNet T1 vs iterative DCM | Simulation T30에서forceMSE/목적상관개선; data감소시baseline성능저하가더큼 | Figs.7–8 p.5 |
| 실물 finetuning | Controlled comparison | Pretrain only vs realfinetune, baseline vsDCM | FinetunedDCM의objective correlation 약0.5,baseline약0 | Fig.10 p.6; FT는fine-tuning의약자 |
| Model-based optimization의효율 | Controlled comparison | 20robottrials vs1000virtual+5validation | 약80min vs25min; trainingdata수집비용포함한전체비용비교는아님 | Table I p.7; §V.D p.6 |

## 13. Author-stated Limitations

Black-box model의explainability를분석하지않았다. RealDCM은compliance-oriented해는찾지만높은task-accuracy해를놓쳐prediction개선이필요하다. (§V.D p.6; §VI p.7)

## 14. Author-stated Future Work

Explainability/analyticalcontact inductivebias를반영한gray-box화, realprediction개선, 대규모contact-richdataset을이용한forcecontrol foundationmodel을제안한다. (§VI p.7)

## 15. Review-relevant Findings

- Demonstration path가implicit surface geometry를제공한다.
- Force는모델학습target/optimizationobjective이며liveactor F/Tinput연구가아니다.
- Tactile없음, RLactor/critic없음.
- Fig.10의FT는force/torque가아닌fine-tuning이다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation/Geometry | §IV.A p.3; Fig.3 p.4 |
| Force/Controller | §III pp.2–3 |
| Tactile | 사용없음, §III–V |
| Learning/GT | §IV.A.2 p.3; §V pp.4–7 |
| Reward/Critic | 비-RL, 해당없음 |
| Ablation | Figs.7–10 pp.5–6; Appendix A p.8 |
| Limitation/Future | §V.D p.6; §VI p.7 |
