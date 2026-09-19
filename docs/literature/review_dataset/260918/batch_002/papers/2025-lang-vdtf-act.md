# VDTF-ACT: ACT-based Multimodal Space Fine Manipulation Method with Visual Depth Tactile Fusion

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B037`
- Authors: Siyi Lang; Jihang Chen; Bo Zhang; Hanlin Dong; Panfeng Huang; Zhiqiang Ma
- Year: 2025
- Venue: IEEE/RSJ IROS 2025, 1511–1517
- DOI / arXiv: 10.1109/IROS60139.2025.11246342 / Not stated
- PDF version: Publisher PDF
- Version note: 선택 범위 내 다른 버전 없음
- Page count: 7
- SHA-256: `b2a853f00e404205c401f93f4c9f1a9948347d90e12dc6a214feb309cbf88f1d`
- PDF filename: `Lang 등 - 2025 - VDTF-ACT ACT-based Multimodal Space Fine Manipulation Method with Visual Depth Tactile Fusion.pdf`
- 읽은 범위: PDF pp.1–7 전체(본문·알고리즘·실험·결론·참고문헌), Fig.5 p.6 렌더 확인. 별도 부록 없음.
- 근거: 이번 배치의 PDF 원문에서 새로 분석했다. 기존 상세 노트는 재사용하지 않았다. 아래 페이지는 PDF 1-based page다.

## 2. Relevance to This Review

**Relevant**. Low-gravity insertion에서 vision/depth와 distributed force tactile을 결합하며 tactile encoder를 비교한다. Tactile가 object–gripper relative motion에 대한 feedback을 제공한다는 저자 설명과 실제 비교 범위를 분리해 정리할 수 있다. Depth와 tactile을 함께 추가한 비교이므로 각 modality의 독립적 기여를 과장하지 않는다.

Screening 위치: Abstract p.1; §IV pp.3–5; §V-D p.6.

## 3. Task

Low-gravity simulation에서 left arm이 peg, right arm이 socket을 잡아 정렬·삽입한다. Evaluation은 contact=1, dual grasp=2, peg/socket contact=3, fully seated insertion=4의 단계 score다. 이 score를 RL reward로 오인하지 않는다. (§V-A/B, p.5)

## 4. Method

### 4.1. Overall Pipeline

4 RGB + 2 depth + 14 joint angles + tactile16 → image/tactile encoders → Transformer ACT decoder with z=0 → k-step joint action chunk → temporal fusion → controller. (§IV, pp.3–5)

### 4.2. Observation

Sensor observations at 50 Hz. Explicit object pose/shape parameter vector 없이 images/depth와 tactile matrix/joint angles를 사용한다. Training-only style encoder는 expert action chunk를 추가로 받는다. (§IV-B, pp.4–5)

### 4.3. Action

k×14 future action sequence. Joint data/action dimension은 명시되지만 velocity/position semantics와 chunk k의 수치는 미명시. (§IV-B, p.4)

### 4.4. Controller

Algorithm 2는 controller가 predicted sequence를 실행한다고만 쓰며 low-level dynamics/gains는 미명시. Exponential temporal weighting으로 overlapping predicted actions를 결합한다. (§III-B/IV-B, pp.3–5)

### 4.5. Learning / Optimization Method

Non-RL imitation learning: scripted 50 successful insertion demonstrations, 2000 epochs; CVAE reconstruction (Fig.6 L1) + KL objective. Training style latent sampled, deployment style z=0. (§IV-B/§V-B–D, pp.4–6)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | RGB/depth feature streams, no numeric position estimate input | Repeated observations; chunk interval k unspecified | Camera coverage must not be reclassified as numeric GT Tracking. 근거: §IV/Algorithm 2, pp.3–5 |
| Orientation | 기타 | RGB/depth latent spatial features | Repeated observations | Current and goal numeric object orientation input absent. 근거: Fig.2/Algorithm 2, pp.4–5 |
| Shape / Geometry | 기타 | Depth/image geometry and fixed task model; no mesh vector input | Images update; object design fixed | §V-A reports peg 1 cm/socket 0.9 cm with positive clearance; internally inconsistent dimensions are not resolved by inference. 근거: §V-A, p.5 |
| Physical Parameters | 미제공 | No parameter vector in deployment input | No | Simulation environment parameters are not observed object physics. 근거: §IV/V-A, pp.3–5 |

## 6. Missing Object Information and Compensation

Explicit pose input 없이 floating-object interaction → RGB/depth + force-array tactile + joint state → learned action sequence. 저자는 depth를 전반적 정렬/안정성, tactile를 마지막 insertion precision에 연결하지만 두 modality를 독립적으로 제거하지 않았다. (§V-D, p.6)

## 7. Tactile

### 7.1. Raw Sensor

Gripper-pad 2×4 force matrix를 설명하며 network 입력은 total 16 values의 4×4 tactile matrix다. 실제 hardware sensor principle/force axes는 미명시; 검증은 simulation이다. (§IV-A/B, pp.3–4)

### 7.2. Preprocessing

Tactile encoder 세 종류: linear, CNN+MLP, CNN+linear. 512D embedding으로 modality fusion; threshold/binarization은 없다. (§IV-B/§V-C, pp.4–5)

### 7.3. Policy Representation

Tactile feature를 image/depth, joint-angle, style feature와 함께 Transformer에 넣어 future action chunk를 예측한다. Deployment style z=0. (Fig.2/Algorithm 2, pp.4–5)

### 7.4. Retained Information

Raw matrix에는 contact-force values와 sensor 배열 위치가 있다. CNN representation이 정확히 어떤 force/locality 성분을 보존하는지는 직접 분석하지 않는다. (§IV-B, p.4)

### 7.5. Removed / Unavailable Information

Force amplitude를 binary로 줄이지 않는다. Encoded feature의 정보 소실, force axis, shear·contact pose 복원 가능성은 미명시. (§IV, pp.3–5)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Gripper pad의 distributed force array로 tactile와 같은 신호다. Wrist 6-axis sensor는 본 방법에 없다. Related-work의 F/T 센서를 현재 방법으로 옮겨 쓰지 않는다. (§II-B p.2; §IV-A p.3)

### 8.2. Representation

4×4 tactile matrix (16 values) → learned feature. Force components/moments는 미명시. (§IV-B, p.4)

### 8.3. Role

Floating object와 gripper의 불확실한 relative motion sensing 및 precision insertion feedback이라고 저자가 설명한다. (Fig.2 p.4; §V-D p.6)

### 8.4. Required Assumptions

Fixed simulated assembly geometry, gripper sensor placement 및 multiview camera coverage. F/T-only inverse localization 방법은 아니다. (§IV-A/§V-A, pp.3,5)

### 8.5. Reported Limitation / Ambiguity

Force-array noise, net-wrench ambiguity, multi-contact localization의 한계를 직접 논의하지 않는다. (§V–VI, pp.5–6)

## 9. Other Observations

Joint14는 proprioception이다. Four RGB/two depth stream은 feature로 처리되며 object-pose estimator output과 구분한다. Temporal action fusion은 sensor history stack이 아니다. Training expert action/style latent는 runtime observation이 아니다. (§III-B/IV-B, pp.3–5)

## 10. Tactile–Other Modality Relationship

Tactile와 independent wrist F/T의 병용은 없다. Vision/depth+distributed-force tactile 결합과 tactile encoder 차이만 비교한다. Depth와 tactile 각 정보의 필요성은 저자 설명을 넘어 개별 ablation으로 분리되지 않았다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Actor | 해당 없음 | 비-RL 방법 | 해당 없음 | §III–V, pp.3–6; IL/CVAE objective, training-only expert action and evaluation score explained in §4/§9 |
| Critic | 해당 없음 | 비-RL 방법 | 해당 없음 | §III–V, pp.3–6; IL/CVAE objective, training-only expert action and evaluation score explained in §4/§9 |
| Reward | 해당 없음 | 비-RL 방법 | 해당 없음 | §III–V, pp.3–6; IL/CVAE objective, training-only expert action and evaluation score explained in §4/§9 |
| Termination | 해당 없음 | 비-RL 방법 | 해당 없음 | §III–V, pp.3–6; IL/CVAE objective, training-only expert action and evaluation score explained in §4/§9 |
| Curriculum | 해당 없음 | 비-RL 방법 | 해당 없음 | §III–V, pp.3–6; IL/CVAE objective, training-only expert action and evaluation score explained in §4/§9 |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Tactile encoder 선택 | Representation ablation | All multimodal inputs held; linear vs CNN+MLP vs CNN+linear | Insertion success 60%/70%/82%. Trial count/seed/uncertainty 미명시. | §V-C/D pp.5–6; Fig.5 p.6 |
| Depth+tactile 추가의 효과 | Sensor combination comparison | Standard visual ACT vs variants with both depth and tactile | 45% baseline vs best 82%; ≥3-point milestone 약80% vs >95%. Depth-only/tactile-only arms가 없어 기여를 따로 입증하지 못함. | §V-D/Fig.5, p.6 |
| Depth/global stability와 tactile/final insertion 역할 | Author explanation only | Milestone curves and encoder comparison에 근거한 저자 해석 | Depth는 stability/accuracy, tactile는 final insertion에 중요하다고 설명; independent removal comparison 미제시. | §V-D, p.6 |

## 13. Author-stated Limitations

독립 Limitation 또는 저자 명시의 후속 한계 목록은 없다. 보고된 평가는 MuJoCo simulated task이며 실물 정량 검증은 원문에서 확인되지 않는다. Force sensor 정보 손실과 독립 modality contribution에 대한 한계 설명도 미명시다. (§V–VI, pp.5–6)

## 14. Author-stated Future Work

Sensor encoding/fusion strategies를 최적화하여 space fine manipulation 성능을 높이는 방향을 명시한다. (§VI, p.6)

## 15. Review-relevant Findings

- Tactile input은 binary가 아닌 16 distributed force values다.
- Explicit numeric current object pose는 입력 목록에 없다.
- Depth와 tactile를 함께 추가한 비교다.
- 82%/70%/60%는 tactile encoder variants, 45%는 visual baseline이다.
- Wrist F/T+tactile의 상보성 실험은 아니다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / force source | §IV-A/B, pp.3–4; Fig.2 |
| Runtime / training distinction | Algorithms 1–2, pp.4–5 |
| Object setup / score | §V-A/B, p.5 |
| Ablation | §V-C/D, pp.5–6; Fig.5 |
| Limitations / future | §VI, p.6 |
