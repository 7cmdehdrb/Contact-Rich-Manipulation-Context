# Deep Functional Predictive Control (deep-FPC): Robot Pushing 3-D Cluster using Tactile Prediction

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B059
- Authors: Kiyanoush Nazari; Gabriele Gandolfi; Zeynab Talebpour; Vishnu Rajendran; Willow Mandil; Paolo Rocco; Amir Ghalamzan-E.
- Year: 2023
- Venue: IEEE/RSJ IROS 2023
- DOI / arXiv: 10.1109/IROS55552.2023.10342410 / Not stated
- PDF version: IEEE publisher PDF, pp.10771–10776
- Page count: 6
- SHA-256: 01c9bb150cad65d334b1acdaa95755a6a8ef33e47f5792294e1151594171b3c3
- PDF filename: Nazari 등 - 2023 - Deep Functional Predictive Control (deep-FPC) Robot Pushing 3-D Cluster Using Tactile Prediction.pdf
- 읽은 범위: PDF pp.1–6 본문 및 포함된 부록을 새로 확인; 핵심 표·그림 렌더링 확인

근거는 이번 배치의 PDF 원문이며 기존 상세 노트는 사용하지 않았다. 페이지는 PDF의 1-based page다.

## 2. Relevance to This Review

**Relevant**. 시각 대신 tactile image와 robot trajectory/history로 flexible stem contact를 예측하며 접촉 유지 pushing을 수행한다. Tactile image를 1D contact location으로 축약하는 controller와 원시 영상의 dynamics model을 구분하여 분석할 수 있다.

## 3. Task

Franka의 tactile finger로 단일 plastic strawberry 또는 cluster를 3D로 밀면서 줄기 접촉이 센서 끝/기부로 미끄러지는 것을 줄인다. 평가는 contact 최대변위, slip instance 수, displacement/action integral이며 전체 strawberry GT 이동거리 성공판정과 다르다. 총100 test pushes, 각 case5회. (§IV–V pp.3–5)

## 4. Method

### 4.1. Overall Pipeline

Tactile image history+past/planned EEF pose → TFM(ConvLSTM) future images → CLM(CNN) 1D stem contact → future error의 PD sum → reference trajectory에 residual rotation velocity 추가 → Cartesian velocity control. 현재 image도 CLM으로 들어가 reference contact를 만든다. (Fig.2 p.3)

### 4.2. Observation

TFM은 64×64×3 tactile images, 과거와 계획된 robot6D EEF position/Euler orientation을 받는다. CLM은 current/predicted tactile image에서 sensor conic axis상의 contact distance를 출력한다. Controller는 현재 contact와 future contact difference, reference motion을 사용한다. 외부 scene vision이나 strawberry center pose는 입력하지 않는다. History/context/horizon의 정확한 수치는 미명시. (§III pp.2–3)

### 4.3. Action

Reference trajectory 위에 contact line axis에 대한 residual rotational velocity를 더한다. 단순test는 Y push+rotation, 3DOF test는 Y/Z translation 및 Wx rotation reference를 사용한다. (§III.d p.3; §V pp.4–5)

### 4.4. Controller

Franka Cartesian velocity controller. Prediction horizon의 contact error와 derivative에 PD gains를 곱해 합한다. Low-level joint command 변환 상세는 미명시다. (§III.d p.3; §V p.4)

### 4.5. Learning / Optimization Method

Supervised TFM/CLM과 model-based d-FPC이며 RL이 아니다. CLM은 fixed sensor에 robot rod를 5mm 간격 위치/1mm penetration으로 밀어10위치150samples로 학습. TFM은430 linear/circular pushes의60Hz tactile 및1000Hz robot state를 ROS synchronization해 학습한다. Explicit training loss 식·hyperparameter 전체는 미명시. (§III.b–c pp.2–3; §IV p.4)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Tactile CNN의 1D sensor-relative contact location | 매 feedback | Object center/world3D position이 아닌 국소 stem contact coordinate (§III.b p.2) |
| Orientation | 미제공 | Object orientation tracking 없음 | 없음 | Robot Euler orientation 입력과 contact-line rotation control을 물체 pose로 해석하지 않음 (§III pp.2–3) |
| Shape / Geometry | 미제공 | 개별 strawberry/stem model 입력 없음 | 없음 | Known half-conic sensor geometry와 학습용 stem/rod prior는 존재 (§II–IV pp.2–4) |
| Physical Parameters | 미제공 | Actor/controller에 mass/friction/stiffness 수치 없음 | 없음 | Plastic strawberry20–30g, flexible wire 환경으로 학습 (§IV p.4) |

## 6. Missing Object Information and Compensation

Global object pose/개별 analytical dynamics 미제공 → tactile current/predicted contact location + robot pose/action sequence + learned tactile dynamics → 접촉 위치 변화를 예측하고 slip 이전에 rotation을 보정한다. 논문이 검증한 것은 sensor-relative contact 유지이며 3D object pose 복원이 아니다. (§II–III pp.2–3; Tables I–III p.5)

## 7. Tactile

### 7.1. Raw Sensor

Franka gripper의 custom camera-based half-conic deformable tactile finger 1개. 내부 white dot markers+LED+camera로 membrane deformation을 관측;60Hz. (§III.a/IV pp.2–3)

### 7.2. Preprocessing

TFM image64×64×3; convolution/ReLU/maxpool, action concatenation, ConvLSTM, upsampling/skip connection. Binary threshold는 사용하지 않는다. (§III.c pp.2–3)

### 7.3. Policy Representation

TFM은 image latent와 robot sequence; CLM은 image→sensor conic axis상의1D contact distance; d-FPC는 current/future distance error. (Fig.2 p.3)

### 7.4. Retained Information

Raw image에는 local deformation/marker pattern. Controller용1D 표현에는 sensor 축 방향 접촉 위치와 그 시간 변화가 남는다. (§III.b–d pp.2–3)

### 7.5. Removed / Unavailable Information

1D CLM output에는 force magnitude, shear vector, 전체 contact patch/여러 접촉별 위치가 명시적 성분으로 없다(구조상 확인). TFM 자체는 영상을 유지하므로 파이프라인 전체가1D만 받는 것은 아니다. (Fig.2 p.3)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음. F/T-only localization 및 그 가정은 해당 없음. (§III–IV pp.2–4)

### 8.2. Representation

사용하지 않음. F/T-only localization 및 그 가정은 해당 없음. (§III–IV pp.2–4)

### 8.3. Role

사용하지 않음. F/T-only localization 및 그 가정은 해당 없음. (§III–IV pp.2–4)

### 8.4. Required Assumptions

사용하지 않음. F/T-only localization 및 그 가정은 해당 없음. (§III–IV pp.2–4)

### 8.5. Reported Limitation / Ambiguity

원문에서 F/T의 해당 한계를 직접 논의하지 않음. (§III–IV pp.2–4)

## 9. Other Observations

Robot EEF6D state와 과거·미래 reference trajectory가 prediction의 action conditioning이다. ConvLSTM은 spatiotemporal dependency를 모델링하나 별도 object-state estimator나 scene vision은 없다. CLM training의 robot-controlled contact positions는 supervised calibration label이며 RL GT가 아니다. (§III pp.2–3)

## 10. Tactile–Other Modality Relationship

| 추가 정보 | Tactile 정보 | 부족한 정보 | 역할 | 근거 |
| --- | --- | --- | --- | --- |
| Robot EEF history/planned poses | Current deformation/contact | Motion에 따른 future contact 변화 | TFM action conditioning | §III.c pp.2–3 |
| Learned dynamics | Current contact coordinate | 미래 slip 경향 | 예측 오차에 기반한 선제 rotation 보정 | PD vs d-FPC Tables I–III p.5 |

F/T와 결합하지 않았고 robot pose 입력만의 제거실험은 없다.

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
| Prediction의 contact 유지 효과 | Controlled comparison | Open-loop; tactile CLM+PD; TFM+CLM+d-FPC | Zone1 최대변위0.80/0.65/0.20; Zone2는PD0.36가d-FPC0.43보다작음. 해당열 단위는표에미명시 | Table I p.5; §V p.4 |
| Cluster pushing에서 prediction | Controlled comparison | Open-loop/PD/d-FPC의 linear/circular push | Linear slip49.33/29.4/17.1; circular47.98/20.5/9.5. 원시촉각과F/T 비교가 아님 | Table III p.5 |
| Sensor deformation에 따른 실패 | Failure analysis | Sensor base zone vs tip/center | Base의 큰 초기변형으로 TFM future prediction 어려움; cluster 다중접촉은 성능저하 | §V pp.4–5 |

## 13. Author-stated Limitations

Sensor base의 큰 초기변형은 TFM prediction을 어렵게 하며 Zone2 최대변위에서는 PD가 더 낫다. Cluster의 추가 접촉은 prediction/control을 어렵게 하고, 두 deep model 때문에 d-FPC 계산시간은PD보다길다(약55–60ms vs19–20ms). (§V pp.4–5; Table I p.5)

## 14. Author-stated Future Work

구체적인 후속 구현/실험 계획은 미명시. Conclusion은 flexible-object tactile manipulation 연구의 토대라는 일반적 전망만 제시한다. (§VI p.6)

## 15. Review-relevant Findings

- Controller는 global object pose가 아니라1D tactile contact 위치를 유지한다.
- Tactile image history와 past/planned robot6D pose로 future image를 예측한다.
- F/T 입력과 RL actor/critic은 없다.
- 예측 제어의 이득은PD/open-loop 비교로 검증하되 zone별 예외가 있다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation/Object pose | §III pp.2–3 |
| Tactile/TFM/CLM | Fig.2 p.3; §III pp.2–3 |
| F/T | §III–IV pp.2–4: 없음 |
| Training labels | §III.b p.2; §IV p.4 |
| Reward/Critic | 비-RL, 해당 없음 |
| Ablation/comparison | Tables I–III p.5 |
| Limitation/Future | §V pp.4–5; §VI p.6 |
