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

근거는 이번 배치의 PDF 원문이며 기존 상세 노트는 사용하지 않았다. 페이지는 PDF의 1-based page이다.

## 2. Relevance to This Review

**Partially Relevant**. Demonstration trajectory가 explicit surface model을 대신하는 geometry prior이며 force trajectory를 예측해 variable stiffness를 조정한다. Online tactile compensation 연구는 아니지만 object geometry 없이 force-based contact task를 성립시키는 추가 정보와 force의 학습·평가 역할을 분석하는 데 유용하다.

## 3. Task

Franka Panda로 curved surface wiping에서 demonstration contact-force trajectory를 재현하면서 stiffness 합을 낮춘다. Success rate 대신 force RMSE와 compliance objective의 Pareto hypervolume을 평가한다. (§III–V pp.2–7)

## 4. Method

### 4.1. Overall Pipeline

Demonstrated EEF path+demonstrated force+candidate stiffness→attractor path 계산; demonstrated path/attractor/stiffness→DCM predicted force sequence→multiobjective Bayesian optimization→selected stiffness trajectory→impedance controller. (§III–IV pp.2–4)

### 4.2. Observation

DCM은 전체 demonstration EEF trajectory, attractor/reference trajectory, stiffness 및 diffusion noisy force sequence/step을 받는다. 실제 object pose, mesh, tactile, vision을 입력하지 않는다. Force observation은 data collection·objective evaluation의 target으로 사용되며 online reactive policy observation으로 명시되지 않는다. (Fig. 3–4 p.4)

### 4.3. Action

Trajectory phases별 constant stiffness를 optimization 변수로 사용. Damping과 attractor는 demonstrated position/derivatives/forces와 stiffness로 계산한다. Phase segmentation은 선행 method를 따르며 세부 미명시. (§III.B pp.2–3)

### 4.4. Controller

Cartesian impedance model은 6D EEF pose와 external force/torque, desired inertia/damping/stiffness로 정의한다. 실제 joint-command 변환 및 force 센서 mount/source는 미명시. (§III.A p.2)

### 4.5. Learning / Optimization Method

RL이 아닌 supervised denoising diffusion model+multiobjective Bayesian optimization. RetNet score network, inputs/outputs [-1, 1]로 정규화. Sim spiral 1,600 train/30 test; real spiral 80 train/20 test; simulation pretraining 후 real fine-tuning. Diffusion 30 steps 비교, robot-free optimization 1,000 virtual trials. (§IV–V pp.3–6; Appendix A p.8)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | Current workpiece pose 입력 없음 | 없음 | Demonstrated robot path는 current object pose가 아님 (§IV.A p.3) |
| Orientation | 미제공 | Workpiece orientation input 없음 | 없음 | EEF reference orientation과 구분 (Fig. 3 p.4) |
| Shape / Geometry | 기타 | Demonstration EEF trajectory에 surface geometry가 implicit하게 제공됨 | 고정 demonstration | 저자가 geometry prior 역할을 직접 명시 (§IV.A.1 p.3) |
| Physical Parameters | 미제공 | Explicit object physical parameter input 없음 | 없음 | Learned contact model/data에 내재 (§I p.1; §IV.A p.3) |

## 6. Missing Object Information and Compensation

Explicit environment geometry/friction/elastic model의 구축 어려움 → demonstrated robot trajectory + force trajectories + learned contact model → reference/stiffness에 대한 하중 변화를 예측한다. Demonstrated trajectory가 surface geometry를 implicit하게 제공한다는 저자 명시가 있다. 이것은 arbitrary unknown surface의 online localization 검증이 아니다. (§I p.1; §IV.A p.3)

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

End-effector external force/torque를 observed/demonstrated 값으로 정의. 실제 sensor model·mount·joint-torque 추정 여부는 미명시; Panda라는 명칭만으로 추정하지 않음. (§III.A–B p.2; §V.A p.5)

### 8.2. Representation

Model F는 6D force/torque로 정의; 결과 그림은 Fx/Fy(tangential), Fz(normal)를 표시. 전체 force trajectory를 예측하며 moment 실험 분석 범위는 미명시. (§III.A p.2; Figs. 9/11 p.6)

### 8.3. Role

Demonstration target; supervised prediction target; force-RMSE objective; predicted force를 사용한 offline stiffness search. (§III.B–IV pp.2–4)

### 8.4. Required Assumptions

F/T-only localization은 수행하지 않음. Demonstration path/forces, phase-based stiffness, robot impedance model 및 task-specific data가 필요. (§III–IV pp.2–4)

### 8.5. Reported Limitation / Ambiguity

Net-wrench contact ambiguity를 직접 논의하지 않음. Real force prediction 정확도 부족으로 task-objective 쪽 Pareto 해를 찾지 못하는 한계를 보고. (§V.D p.6)

## 9. Other Observations

EEF demonstration position/orientation 및 그 velocity/acceleration은 reference 계산에 사용한다. RetNet recurrent state는 trajectory prediction model의 내부이며 online policy history로 기록하지 않는다. Previous action/vision/object state estimator는 미명시 또는 해당 없음. (§III.B p.3; Fig. 4 p.4)

## 10. Tactile–Other Modality Relationship

Tactile 병용은 없다. Force 정보의 부족분을 tactile로 보완한 실험이 아니라 known demonstration geometry와 learned dynamics를 활용한 force prediction/stiffness optimization이다.

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
| Iterative diffusion의 효과 | Representation ablation | Single forward RetNet T1 vs iterative DCM | Simulation T30에서 force MSE/목적 상관 개선; data 감소 시 baseline 성능 저하가 더 큼 | Figs. 7–8 p.5 |
| 실물 finetuning | Controlled comparison | Pretrain only vs real fine-tuning, baseline vs DCM | Fine-tuned DCM의 objective correlation 약 0.5, baseline 약 0 | Fig. 10 p.6; FT는 fine-tuning의 약자 |
| Model-based optimization의 효율 | Controlled comparison | 20 robot trials vs 1,000 virtual trials + 5 validation trials | 약 80 min vs 25 min; training data 수집 비용을 포함한 전체 비용 비교는 아님 | Table I p.7; §V.D p.6 |

## 13. Author-stated Limitations

Black-box model의 explainability를 분석하지 않았다. Real DCM은 compliance-oriented 해는 찾지만 높은 task-accuracy 해를 놓쳐 prediction 개선이 필요하다. (§V.D p.6; §VI p.7)

## 14. Author-stated Future Work

Explainability/analytical contact inductive bias를 반영한 gray-box화, real prediction 개선, 대규모 contact-rich dataset을 이용한 force control foundation model을 제안한다. (§VI p.7)

## 15. Review-relevant Findings

- Demonstration path가 implicit surface geometry를 제공한다.
- Force는 모델 학습 target/optimization objective이며 live actor F/T input 연구가 아니다.
- Tactile 없음, RL actor/critic 없음.
- Fig. 10의 FT는 force/torque가 아닌 fine-tuning이다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation/Geometry | §IV.A p.3; Fig. 3 p.4 |
| Force/Controller | §III pp.2–3 |
| Tactile | 사용 없음, §III–V |
| Learning/GT | §IV.A.2 p.3; §V pp.4–7 |
| Reward/Critic | 비-RL, 해당 없음 |
| Ablation | Figs. 7–10 pp.5–6; Appendix A p.8 |
| Limitation/Future | §V.D p.6; §VI p.7 |
