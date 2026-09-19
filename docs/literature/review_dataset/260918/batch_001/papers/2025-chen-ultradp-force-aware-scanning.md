# UltraDP: Generalizable Carotid Ultrasound Scanning with Force-Aware Diffusion Policy

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B012`
- Authors: Ruoqu Chen; Xiangjie Yan; Kangchen Lv; Gao Huang; Zheng Li; Xiang Li
- Year: 2025
- Venue: 2025 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 20074–20080
- DOI / arXiv: 10.1109/IROS60139.2025.11246769 / 미명시
- PDF version: Publisher version. PDF 첫 페이지의 conference/DOI 및 본문을 기준으로 확인. 선택된 배치 안에서 동일 논문의 다른 파일은 확인되지 않았다.
- Page count: 7
- SHA-256: `28eed2e8fedd40d6a82fbd461e8dfa9d6a79f52bcd46f7dafa04a0ba6066ad0a`
- PDF filename: `Chen 등 - 2025 - UltraDP Generalizable Carotid Ultrasound Scanning with Force-Aware Diffusion Policy.pdf`
- 읽은 범위: PDF pp.1–7 전체: 관련 연구·방법·실험·결론·참고문헌. 별도 Appendix 없음. Fig.3의 네트워크와 Table II–III를 렌더링으로 확인.
- 근거 원칙: 이번 배치의 해당 PDF에서 새로 추출했다. 기존 상세 노트와 외부 보충자료는 사실 근거로 사용하지 않았다. 아래 페이지는 PDF의 1-based page다.

## 2. Relevance to This Review

**Partially Relevant**. Task는 경동맥 ultrasound scanning으로 일반 물체 manipulation과 다르지만, 접촉을 유지하는 로봇 정책이 wrist F/T와 probe pose를 어떻게 함께 쓰는지 직접 조사할 수 있다. Wrench 관측과 pose 관측을 각각 제거한 ablation 및 실패 분석이 있다. Tactile와 Binary representation 연구는 아니므로 force/proprioception/영상의 역할과 low-level controller 분리에 한정해 포함한다.

Screening 근거: Title/Abstract/§I, PDF pp.1–2; §III-A–D, PDF pp.3–4; Table III, p.6.

## 3. Task

목 아래에서 시작해 경동맥을 transverse ultrasound image로 관찰하면서 위쪽 bifurcation까지 scan한다. 로봇은 probe와 neck의 접촉을 유지하고 artery를 영상의 가로 중심에 두어야 한다. 온라인 평가 성공 조건은 scanning period의 60% 이상에서 clear/centered transverse artery image를 얻고 bifurcation에서 scan을 멈추는 것이다. Task는 deformable tissue와의 연속 접촉이며 물체 grasp/retraction은 아니다. (§I, pp.1–2; §IV-B, p.6)

## 4. Method

### 4.1. Overall Pipeline

현재 ultrasound image + wrist RGBD + probe pose + measured contact wrench → observation sequence encoder → landmark-guided DDPM Diffusion Policy → relative probe pose + desired wrench → hybrid force-impedance controller → joint torques. Ultrasound landmark network는 diffusion encoder 초기화와 실행 중 image-centering guidance의 두 경로에 쓰인다. Guidance network는 frozen으로 표시된다. (Fig.3; §III-A–D, pp.3–4)

### 4.2. Observation

$O_t=(U_t,I_t,x_t,w_t)$이며 $U$는 ultrasound, $I$는 wrist RGBD 4채널, $x$는 probe pose, $w\in\mathbb{R}^{6}$는 contact wrench다. RGBD에는 depth로 만든 mask를 적용하여 background를 제거한다. Probe pose는 Cartesian position 3D + rotation representation 6D로 인코딩한다. 이 pose는 robot end effector이며 current anatomy pose가 아니다. Observation/action sequence와 receding horizon을 사용하지만 정확한 history 길이는 미명시다. (§III-A Eq.(1)–(3), p.3)

Controller는 measured wrench $F_e$, robot joint state, Jacobian/dynamics, desired pose/wrench를 별도로 사용한다. Image guidance는 현재 ultrasound에서 추정한 artery의 horizontal pixel coordinate를 사용한다. Goal인 image center와 관측 artery coordinate를 구분한다. (§III-B–D, p.4)

### 4.3. Action

시연에서 $A_t=(\operatorname{diff}(x_{t+1},x_t),w_t)$를 구성하고 desired relative pose와 wrench를 학습한다. Navigation이 예측한 명령은 약 10 Hz, low-level 제어는 1 kHz이며 command에 low-pass filter를 적용한다. Filter cutoff는 본문 미명시다. (§III-A Eq.(3), p.3; §III-D, p.4)

### 4.4. Controller

Franka 7-DoF dynamics에 기반하여 main task torque, null-space torque, gravity 및 Coriolis/centrifugal compensation을 합친다. Probe-frame z 방향은 force control, 나머지 5개 방향은 impedance control이며 selection matrix를 base frame으로 변환한다. Force feedback은 navigation에 입력되는 wrench와 별개 경로다. (§III-D Eq.(7)–(10), p.4)

### 4.5. Learning / Optimization Method

전문가 demonstration으로 DDPM diffusion policy를 학습한다. 21명의 210개 scan에서 약 460k observation-action pairs를 수집하며 unseen-subject validation에 약 54k pairs를 사용한다. 각 demonstration에 Cartesian random transformation augmentation을 적용한다. Ultrasound encoder는 expert-labelled 약 6k image/label pairs에서 artery presence classification 및 horizontal-position regression으로 사전학습한다. 학습 후 FC를 제거해 encoder를 초기화하고 별도의 frozen landmark prediction 경로도 사용한다. (§I, p.2; §III-A–B, pp.3–4)

시연에서 artery가 거의 항상 중심에 있어 centering correction을 DP가 스스로 학습하기 어렵다는 이유로 guidance를 추가했다. Linear-array probe의 straight scan에서 $\Delta y=a\Delta u$라는 알려진 probe parameter를 사용한다. 이 geometry-informed correction은 F/T-only 위치추정이 아니다. (§III-A, p.3; §III-C Eq.(5)–(6), p.4)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | Ultrasound image의 artery horizontal landmark 추정; 현재 probe pose는 별도 robot proprioception | 현재 영상에서 landmark 갱신 | 3D neck/artery current position tracking을 제공하지 않는다. 2D image coordinate를 3D object pose로 확장하지 않는다. 근거: §III-A–C, pp.3–4; Fig.3 |
| Orientation | 미제공 | Anatomy의 명시적 current orientation 입력 없음 | 없음 | 3D position+6D rotation representation은 probe pose이다. Scan 목표 transverse image나 probe orientation을 anatomy orientation으로 기록하지 않는다. 근거: §III-A, p.3; §III-C–D, p.4 |
| Shape / Geometry | 기타 | Online ultrasound/RGBD appearance; 알려진 linear-array probe mapping parameter | 영상 갱신; probe geometry parameter는 고정 | Anatomical full mesh/CAD/dimensions는 정책에 제공하지 않는다. Probe geometry와 anatomy geometry는 별개다. 근거: §III-A–C, pp.3–4; Eq.(6) |
| Physical Parameters | 미제공 | Actor의 tissue stiffness/friction/물성 수치 입력 없음 | 없음 | Controller의 robot dynamics와 gains는 사용하지만 tissue physical parameter를 관측하는 것은 아니다. 근거: §III-A, p.3; §III-D, p.4 |

Probe position/orientation은 계속 제공하지만 이것을 current neck/artery pose Tracking으로 세지 않는다. Anatomy의 horizontal image landmark만 별도 estimator로 갱신한다. Goal image center 역시 current pose가 아니다.

## 6. Missing Object Information and Compensation

명시적 3D anatomy pose/shape/물성 미제공 → 현재 ultrasound/RGBD + probe pose + measured wrench → 영상 목표에 맞춘 motion과 contact force를 함께 예측한다. 원문은 숫자 anatomy pose를 복원했다고 주장하지 않는다.

시연에서 부족한 off-center recovery 정보 → expert-labelled landmark network + known probe geometry guidance → diffusion samples를 image center 방향으로 유도한다. 이 보완은 저자가 명시한 설계 이유다. (§III-A–C, pp.3–4)

개인마다 다른 contact force/action range → contact wrench observation → 적절한 desired force 예측과 접촉 유지. Wrench 제거의 실패로 이 역할을 검증한다. Probe pose 제거 비교는 단순 force sensing만으로 image-centering을 유지하기 어렵다는 해당 task의 결과를 준다. (§III 도입, p.3; §IV-C Table III, p.6)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음. Ultrasound와 wrist RGBD는 영상 modality이고, ATI mini40은 F/T sensor다.

### 7.2. Preprocessing

해당 없음.

### 7.3. Policy Representation

해당 없음.

### 7.4. Retained Information

해당 없음.

### 7.5. Removed / Unavailable Information

해당 없음. Ultrasound 이미지 처리 결과를 tactile representation으로 재분류하지 않는다. (§III-A–D, pp.3–4)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Arm flange와 ultrasound probe 사이의 ATI mini40 F/T sensor. 원문에서 wrist-mounted라고 명시한다. Joint torque estimated wrench가 아니다. (§III-D, p.4; Fig.4)

### 8.2. Representation

Measured 6D contact wrench가 policy observation이며 navigation이 desired 6D wrench를 출력한다. Controller는 probe-frame z-force를 선택하여 규제한다. Raw sensor filtering/calibration 세부는 미명시이며, 상위 action smoothing용 filter와 혼동하지 않는다. (§III-A Eq.(2)–(3), p.3; §III-D, p.4)

### 8.3. Role

Policy의 desired force 예측, low-level contact force feedback, smooth force evaluation에 쓰인다. Table III의 wrench ablation은 policy observation에서 wrench를 제거한 것이며 저수준 F/T feedback을 제거한 실험이 아니다. (§III-D, p.4; §IV-C, p.6)

### 8.4. Required Assumptions

Probe의 contact direction을 z-axis로 두고 force/impedance selection matrix를 frame transform한다. Robot kinematics/dynamics와 controller gains가 알려져 있다. Artery landmark guidance에는 known linear-array probe parameter와 straight-line image mapping이 필요하다. 이 조건에서 F/T가 anatomy location을 추정하는 것은 아니다. (§III-C–D Eq.(6)–(10), p.4)

### 8.5. Reported Limitation / Ambiguity

Net-wrench multi-contact ambiguity, contact patch/localization ambiguity는 원문에서 직접 논의하지 않는다. Wrench observation이 없는 policy가 잘못된 force 명령으로 접촉을 유지하지 못하는 실패는 보고한다. (§IV-C, p.6)

## 9. Other Observations

- Proprioception: 현재 probe position 및 orientation representation. Low-level controller의 joint state와 구분한다.
- Vision: wrist RGBD와 ultrasound를 실행 중 계속 사용한다. Depth-derived mask는 불필요한 background를 제거한다.
- History: receding-horizon sequence 사용. Observation horizon, recurrent state 및 previous action 입력의 세부는 미명시.
- State Estimator: artery presence/horizontal position을 예측하는 pretrained network. Full 3D anatomy pose estimator가 아니다.
- Goal / geometry: image center와 scan objective, known probe mapping parameter. Fixed goal과 current image landmark를 구분한다.

근거: §III-A–D, pp.3–4; Fig.3.

## 10. Tactile–Other Modality Relationship

Tactile를 사용하지 않아 tactile–F/T 상보성의 직접 근거가 아니다. 비교 가능한 관계는 **contact wrench–probe proprioception–영상**이다.

| 추가 정보 | 제공 정보 | 부족한 정보 / 역할 구분 | 원문 근거 |
| --- | --- | --- | --- |
| Measured wrench | 현재 접촉 하중 | Desired force 예측과 접촉 유지; anatomical landmark는 제공하지 않음 | §III-D, p.4; Table III, p.6 |
| Probe pose | 로봇 probe의 현재 위치/자세 | Wrench와 함께 경로 및 centering에 기여; anatomy pose 아님 | §III-A, p.3; Table III, p.6 |
| Ultrasound / landmark | Artery image appearance 및 horizontal coordinate | 영상 중심 목표를 위한 정보 | §III-B–C, p.4 |
| Wrist RGBD | 주변 영상/깊이 | Learned visuomotor context; 독립 RGBD ablation은 없음 | §III-A, p.3 |

Wrench와 probe pose 제거는 실험했지만 각각의 modality가 가진 모든 정보적 역할을 완전히 분해한 연구는 아니다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 | 비고 |
| --- | --- | --- | --- | --- |
| Actor | 해당 없음 | 비-RL imitation learning | 해당 없음 | 실측 pose/wrench와 expert-labelled ultrasound landmark를 supervised training에 사용. Simulator privileged-state 접근이 아니다. 근거: §III-A–C, pp.3–4 |
| Critic | 해당 없음 | 비-RL imitation learning | 해당 없음 | 실측 pose/wrench와 expert-labelled ultrasound landmark를 supervised training에 사용. Simulator privileged-state 접근이 아니다. 근거: §III-A–C, pp.3–4 |
| Reward | 해당 없음 | 비-RL imitation learning | 해당 없음 | 실측 pose/wrench와 expert-labelled ultrasound landmark를 supervised training에 사용. Simulator privileged-state 접근이 아니다. 근거: §III-A–C, pp.3–4 |
| Termination | 해당 없음 | 비-RL imitation learning | 해당 없음 | 실측 pose/wrench와 expert-labelled ultrasound landmark를 supervised training에 사용. Simulator privileged-state 접근이 아니다. 근거: §III-A–C, pp.3–4 |
| Curriculum | 해당 없음 | 비-RL imitation learning | 해당 없음 | 실측 pose/wrench와 expert-labelled ultrasound landmark를 supervised training에 사용. Simulator privileged-state 접근이 아니다. 근거: §III-A–C, pp.3–4 |

RL이 아니므로 다섯 RL 항목은 해당 없음이다. Expert-labelled artery landmark는 supervised ground truth로 분명히 기록하지만 simulator privileged information과 동일시하지 않는다. §IV-A가 simulation이라고 부르는 평가는 기록된 실제 demonstration 관측을 사용하며 simulator object GT API는 제시되지 않는다. 운영상 bifurcation stopping의 구체 detector 구현도 미명시다.

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Policy wrench observation의 필요성 | Input ablation; Failure analysis | UltraDP full vs without wrench observation; 동일 low-level hybrid force-impedance controller | Success 19/20→0/20. Wrench 없는 정책은 부적절한 desired force를 예측하여 neck contact를 유지하지 못함. Controller F/T 제거 비교가 아니다. | §IV-C, PDF p.6, Table III |
| Policy probe pose observation의 필요성 | Input ablation; Failure analysis | Full vs without pose observation | Success 19/20→8/20. Pose 제거 시 접촉은 가능하나 artery의 image-center 유지가 어려움. Wrench와 pose 모두 제거한 모델은 수렴하지 않아 human trial을 수행하지 않음. | §IV-C, PDF p.6, Table III |
| Complete UltraDP system과 baseline의 비교 | Controlled comparison | UltraDP vs visual servoing (VS) vs behavior cloning (BC); 4 unseen volunteers × 5 trials; BC에는 동일 hybrid controller 적용 | Success 19/20 vs 17/20 vs 6/20. Mean landmark distance 5.71/6.52/25.44 px; SSIM 76.83/71.24/62.19%; expert score 7.11/6.76/6.14; dFz/dt 0.187/0.329/0.189 N/s. | §IV-B, PDF p.6, Table II |
| Unseen subject observation trajectory에 대한 일반화 | Controlled comparison | Recorded demonstration observations의 known vs unknown volunteer evaluation; online human scan trial과 구분 | Mean tracking error unknown 0.0135 m, known 0.0104 m. 논문은 simulation으로 부르지만 실측 demonstration 관측을 입력한 평가이며 simulator object GT 접근은 명시하지 않음. | §IV-A, PDF p.5; Table I, p.4 |

Table III의 두 관측을 모두 제거한 조건은 수렴하지 않아 시험하지 않았으며 0/20으로 채우지 않는다. Table II는 complete-system comparison이므로 개별 modality의 독립적 효과로 해석하지 않는다.

## 13. Author-stated Limitations

전문가 시연은 artery가 이미 중심에 있어 DP가 recentering을 자동 학습하기 어렵다고 명시한다. Guidance는 이 data-coverage 문제에 대한 저자들의 대응이다. (§III-A, p.3)

Known/unknown subjects를 비교한 offline 결과에서 unknown 조건의 tracking error가 더 높다. 다만 독립된 exhaustive limitation section은 없으며, 다른 연구의 한계를 자기 방법의 한계로 옮기지 않는다. (§IV-A, p.5; Table I, p.4)

## 14. Author-stated Future Work

Conclusion은 더 큰 규모의 validation을 향후 방향으로 제시한다. Dataset의 처리 후 공개 계획도 서술한다. 검증 확대 및 공개 계획을 이미 완료된 결과로 기록하지 않는다. (§I, p.2; §V, p.7)

## 15. Review-relevant Findings

- Policy는 current ultrasound/RGBD, probe pose, 6D contact wrench를 입력받는다.
- Current probe pose와 3D anatomy pose는 다르다. 수치 anatomy pose tracking은 제공하지 않는다.
- Artery horizontal coordinate를 영상에서 추정하며 known probe geometry로 guidance를 구성한다.
- Wrist F/T는 policy와 low-level controller 양쪽에서 사용된다.
- Wrench 관측 제거 0/20, probe pose 제거 8/20, 전체 모델 19/20으로 비교한다.
- Policy ablation에서도 force controller는 유지된다.
- Tactile와 RL privileged critic/reward를 다루지 않으므로 이 두 주제의 직접 근거로 확장하지 않는다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / object vs probe pose | §III-A Eq.(1)–(3), PDF p.3 |
| Shape / landmark guidance | §III-B–C Eq.(5)–(6), PDF pp.3–4 |
| F/T source / controller | §III-D Eq.(7)–(10), PDF p.4; Fig.4 |
| Training / labels / history | §I, PDF p.2; §III-A–C, pp.3–4; Fig.3 |
| Ablation / failure | §IV-C, PDF p.6; Table III; Fig.7 |
| Controlled comparisons | §IV-A–B, PDF pp.5–6; Table I–II |
| Reward / Critic | 해당 없음: 비-RL imitation learning |
| Limitations | §III-A, PDF p.3; §IV-A, p.5 |
| Future work | §I, PDF p.2; §V, p.7 |
