# Blind Sweeping 관련 연구 — 33편 원문 비교와 근거

[문헌 색인](../README.md) · [조사 그룹](README.md) · [전체 논문](../papers/README.md)

작성일: 2026-09-22 · [타임라인·통합 비교표·Contribution 본문](../../presentation/04_Related_Work_Timeline_and_Contributions.md)

## 확인 범위와 읽는 방법

저장소 `docs/literature/papers`의 **33편 모두에 대해 실제 논문 PDF 또는 전체 HTML에서 비교에 필요한 방법·실험·결론 부분을 확인**했다. 기존 Markdown 요약만을 다시 분류한 결과가 아니다. 코드 실행·실험 재현과 각 판본 전체의 문장 단위 비교는 수행하지 않았다.

- 비교축은 **실행 Observation → Sensor → Method → 강건성 → Sim-to-Real**이다. 과업은 제목·관측·방법을 읽는 전제다.
- `미명시`는 확인한 원문이 세부를 제공하지 않는다는 뜻이며, 해당 기능이 불가능하거나 실제로 없었다는 단정이 아니다.
- 초기 정보, Actor의 실행 입력, 학습용 Teacher/Critic/Reward 정보, 평가용 정답을 구분한다. 로봇 제어기가 사용하는 정보와 정책 입력도 구분한다.
- `정책 추가학습 없음`에도 센서 Calibration·Domain Translation 학습·시스템 식별이 있을 수 있다. 실물 직접 학습과 비학습 실물 제어는 전이 실패가 아니다.
- `미학습 물체`, `미지 물성`, `새로운 배치`, `OOD 초기조건`, `센서 손상`을 서로 다른 검증으로 기록한다.
- 저자 한계·Future와 이 비교를 위한 해석을 분리했다. 공개본 기준인 경우 출판본 전체와 동일하다고 주장하지 않는다.

**원문 판본:** 각 항목에 읽은 원문 URL을 남겼다. Liu와 Door Opening은 보유한 출판본 PDF를 직접 확인했고, Lloyd는 출판사 전체 HTML을 우선했다. 다른 연구는 공개 저자 PDF 또는 arXiv 본문을 사용했다. MAT는 CoRL 2019 / PMLR 2020, Gentle Retraction은 RA-L 정규 권호 2026, Beyond Binary는 2026 arXiv 사전공개본으로 구분한다.

## 전체 목록과 비교에서의 역할

아래 번호는 이 자료 안의 식별자이며 저장소의 기존 R1·B1 등의 번호와 별개다. 제목을 누르면 원문 검토 내용, 기존 노트를 누르면 검토 당시 저장소 문서가 열린다.

| ID | 논문 | 비교에서의 역할 | 기존 노트 |
| --- | --- | --- | --- |
| P01 | [Lee — Making Sense of Vision and Touch (2019)](#p01) | 다중 감각 표현의 출발 | [상세 노트](../papers/2019-lee-making-sense-vision-touch.md) |
| P02 | [Wu — MAT (CoRL 2019; proceedings 2020)](#p02) | 초기 시각·Binary·Blind 전이의 핵심 선행 | [상세 노트](../papers/2019-wu-mat-adaptive-tactile-grasping.md) |
| P03 | [Beltran-Hernandez — Learning Force Control (2020)](#p03) | 힘 제어를 RL 행동으로 조절 | [상세 노트](../papers/2020-beltran-hernandez-learning-force-control.md) |
| P04 | [Ding — Sim-to-Real Transfer with Tactile Sensory (2021)](#p04) | Binary 전이와 현재 물체 관측의 구분 | [상세 노트](../papers/2021-ding-sim-to-real-tactile-manipulation.md) |
| P05 | [Kato — Self-Tuning Impedance-Based Interaction Planner (2022)](#p05) | 비학습 미지 접촉 환경 대응 | [상세 노트](../papers/2022-kato-self-tuning-haptic-exploration.md) |
| P06 | [Lin — Tactile Gym 2.0 (2022)](#p06) | 광학 촉각의 밀기·전이 | [상세 노트](../papers/2022-lin-tactile-gym-2-0.md) |
| P07 | [Brahmbhatt — Zero-Shot Haptics-Based Object Insertion (2023)](#p07) | 초기 시각 이후 Wrench RL | [상세 노트](../papers/2023-brahmbhatt-zero-shot-haptics-insertion.md) |
| P08 | [Attention for Robot Touch — Lin, 2023](#p08) | 방해 접촉·국소 특징 추출 | [상세 노트](../papers/2023-lin-attention-for-robot-touch.md) |
| P09 | [Bi-Touch — Lin, 2023](#p09) | 촉각 기반 양팔 비파지 조작 | [상세 노트](../papers/2023-lin-bi-touch.md) |
| P10 | [Tactile Pushing — Yang, 2023](#p10) | 국소 접촉 상태 기반 밀기 | [상세 노트](../papers/2023-yang-sim-to-real-tactile-pushing.md) |
| P11 | [Rotating without Seeing — Yin, 2023](#p11) | Binary 기반 Blind RL·미학습 물체 | [상세 노트](../papers/2023-yin-rotating-without-seeing.md) |
| P12 | [Haninger et al. — Differentiable Compliant Contact Primitives (2024)](#p12) | 명시적 접촉 모델 추정·MPC | [상세 노트](../papers/2024-haninger-differentiable-compliant-contact-primitives.md) |
| P13 | [Force Push (2024)](#p13) | 비시각 Force-only 밀기 | [상세 노트](../papers/2024-heins-force-push.md) |
| P14 | [DexTouch — Lee, 2024](#p14) | Binary 기반 Hand-Arm 탐색·조작 | [상세 노트](../papers/2024-lee-dextouch.md) |
| P15 | [Tactile Active Inference Reinforcement Learning — Liu et al., 2024](#p15) | 촉각 특징·모델 기반 학습의 관측 대조 | [상세 노트](../papers/2024-liu-tactile-active-inference-rl.md) |
| P16 | [Pose-and-shear-based tactile servoing — Lloyd & Lepora, 2024](#p16) | 촉각 추정·비학습 밀기 대안 | [상세 노트](../papers/2024-lloyd-pose-and-shear-based-tactile-servoing.md) |
| P17 | [Pushing in the Dark (2024)](#p17) | 대표 접촉점 기반 비시각 밀기 | [상세 노트](../papers/2024-ozdamar-pushing-in-the-dark.md) |
| P18 | [Sim2Real Manipulation on Unknown Objects — Su, 2024](#p18) | Binary 영상과 영역 비트의 구분 | [상세 노트](../papers/2024-su-sim2real-tactile-manipulation.md) |
| P19 | [Wu et al. — 1 kHz Behavior Tree (2024)](#p19) | 행동 규칙+파라미터 학습 | [상세 노트](../papers/2024-wu-1khz-tactile-insertion.md) |
| P20 | [Robot Synesthesia — Yuan et al., 2024](#p20) | 지속 시각·Binary 융합의 대조 | [상세 노트](../papers/2024-yuan-robot-synesthesia-visuotactile.md) |
| P21 | [Unknown Object Retrieval (2024)](#p21) | 저차원 촉각-only RL·미학습 물체 | [상세 노트](../papers/2024-zhao-unknown-object-retrieval.md) |
| P22 | [Precision-Focused RL Pushing (2025)](#p22) | 현재 영상 기반 정밀 밀기 대조 | [상세 노트](../papers/2025-bergmann-precision-focused-pushing.md) |
| P23 | [ViViDex — Chen et al., 2025](#p23) | 시각 정책·실물 데이터 사용 대조 | [상세 노트](../papers/2025-chen-vividex.md) |
| P24 | [Dynamic Object Goal Pushing (2025)](#p24) | 현재 Pose를 받는 동적 밀기 대조 | [상세 노트](../papers/2025-dadiotis-dynamic-object-goal-pushing.md) |
| P25 | [Location-Based Attention Pushing (2025)](#p25) | 현재 Pose·장애물 지도를 받는 밀기 대조 | [상세 노트](../papers/2025-dengler-location-based-attention-pushing.md) |
| P26 | [He et al. — FoAR (2025)](#p26) | 접촉 예측·Wrench 기반 실물 IL | [상세 노트](../papers/2025-he-foar.md) |
| P27 | [Enhancing Tactile-based Reinforcement Learning — Miller et al., 2025](#p27) | Binary RL·실물 미검증 대조 | [상세 노트](../papers/2025-miller-enhancing-tactile-rl.md) |
| P28 | [Noseworthy et al. — FORGE (2025)](#p28) | 힘 조건부 RL·실물 전이 | [상세 노트](../papers/2025-noseworthy-forge.md) |
| P29 | [Yang et al. — Pseudo-Tactile Feedback (2025)](#p29) | Binary 그리퍼 상태·시뮬레이션 IL | [상세 노트](../papers/2025-yang-pseudo-tactile-gripper-state.md) |
| P30 | [The Role of Tactile Sensing for Learning Reach and Grasp — Zhang et al., 2025](#p30) | 촉각 측정량·해상도 직접 비교 | [상세 노트](../papers/2025-zhang-role-of-tactile-sensing.md) |
| P31 | [Gentle Object Retraction (2026)](#p31) | 촉각·Wrench·시각 결합의 근접 과업 | [상세 노트](../papers/2026-brouwer-gentle-object-retraction.md) |
| P32 | [Beyond Binary — Pan, 2026](#p32) | Binary보다 풍부한 접촉 표현 비교 | [상세 노트](../papers/2026-pan-beyond-binary-cop-tactile.md) |
| P33 | [Šimundić et al. — Visuo-Force-Tactile Door Opening (2026)](#p33) | 시각 재관측·F/T·촉각 통합 제어 | [상세 노트](../papers/2026-simundic-visuo-force-tactile-door-opening.md) |

---

<a id="p01"></a>

## P01. Lee — Making Sense of Vision and Touch (2019)

| 비교축 | 원문 근거 |
| --- | --- |
| Observation | 실시간 RGB·wrench 32시점·EEF 위치/속도. Optical flow/contact 정답은 표현학습용. |
| Sensor | 고정 RGB 카메라·손목 6축 F/T·joint encoder. 분포 촉각 없음. |
| Method | 자기지도 multimodal encoder를 고정하고 TRPO로 3D EEF 변위 학습; impedance·OSC 실행. |
| 강건성 | 미학습 hexagonal·square peg에 정책 추가학습 없이 적용. 간헐적 camera 가림·arm 외란은 정성 평가. |
| Sim-to-Real | 실물에서 TRPO 직접 학습. Simulation/real 실험을 zero-shot 전이로 분류하면 안 됨. |

**저자 한계·Future:** 한계 목록 미명시. 6DoF 조작·modality·자기지도 확대가 후속.

**비교 해석:** 연속 시각+wrench 융합의 선행. 간헐적 가림 회복은 실행 전체의 시각 갱신 제거와 다르다.

**원문:** [arXiv:1810.10191v2](https://arxiv.org/html/1810.10191v2), §IV–VIII, Fig.2–6.

---

<a id="p02"></a>

## P02. Wu — MAT (CoRL 2019; proceedings 2020)

| 비교축 | 원문 근거 |
| --- | --- |
| Observation | 초기 vision grasp pose 이후 96 binary contact·hand joints·활성 taxel FK 위치의 20시점 이력/차분. 실행 영상·물체 pose 없음. |
| Sensor | Barrett BH-282 손가락·손바닥 taxel과 고유감각. 실물 평균화·threshold·finger effort 보정 포함. |
| Method | Soft PPO+폐쇄량 curriculum. 폐쇄·재개방·회전·lift 학습, 접촉 기반 Cartesian 재배치 결합. |
| 강건성 | Seen/novel 물체, 단일/clutter, 실물 5cm calibration offset 평가. |
| Sim-to-Real | 전부 simulation 정책학습 후 실물 추가학습 없이 전이. 센서 보정은 수행. |

**저자 한계·Future:** Sparse tactile의 pose 정보 부족·충돌 위험으로 회전 조정 제한. 조작 과업 확장은 후속.

**비교 해석:** 초기시각+binary tactile+blind+미학습 물체+sim-to-real은 기존 조합이다.

**원문:** [arXiv:1909.04787v2](https://arxiv.org/html/1909.04787v2), §4–6, Table1, Appendix A.1.3/A.13–14; [PMLR 출판 연도](https://proceedings.mlr.press/v100/wu20a.html).

---

<a id="p03"></a>

## P03. Beltran-Hernandez — Learning Force Control (2020)

| 비교축 | 원문 근거 |
| --- | --- |
| Observation | 기지 goal 대비 EEF pose error·velocity·wrench. Vision 없음. Privileged critic 미명시. |
| Sensor | UR3 e-series EEF F/T·proprioception. F/T 제품 모델 미명시; 분포 촉각 없음. |
| Method | SAC가 trajectory와 controller gain 결정. Parallel position/force 또는 admittance 제어·fail-safe 결합. |
| 강건성 | Ring/peg insertion의 다른 정밀도·접촉 조건에서 학습. 고정 정책의 held-out 일반화는 미검증. |
| Sim-to-Real | 실물 과업에서 직접 훈련. Simulation 비교가 policy transfer를 뜻하지 않음. |

**저자 한계·Future:** 경험적으로 정한 controller gain 범위에 성능 의존. Demonstration 기반 설정·vision goal 추정이 후속.

**비교 해석:** 환경 geometry 불필요와 goal pose 기지는 공존한다. 힘 제어 방법론 비교에 적합하다.

**원문:** [arXiv:2003.00628v3 PDF](https://arxiv.org/pdf/2003.00628), §III-B/IV-A/IV-D/V, Algorithm1, Fig.7–9.

---

<a id="p04"></a>

## P04. Ding — Sim-to-Real Transfer with Tactile Sensory (2021)

| 비교축 | 원문 근거 |
| --- | --- |
| Observation | Robot state·gripper width·현재 손잡이 상대 위치·door hinge angle 25D에 binary tactile 30D 추가. 환경 상태는 actor 입력. |
| Sensor | 양쪽 저항식 15+15 taxel, ZED Mini+AprilTag, proprioception. Wrist F/T 결합 정책 아님. |
| Method | TD3 door opening; joint velocity+gripper action. Dynamics/noise/delay·binary flipping randomization. |
| 강건성 | 정해진 cabinet/knob의 parameter·위치 변동. 새로운 geometry의 held-out 평가는 미확인. |
| Sim-to-Real | Simulation 정책을 추가학습 없이 배포. 사전 robot trajectory alignment·tactile calibration·threshold 선정 수행. |

**저자 한계·Future:** 다른 센서·과업 검증, 촉각 모델·연속값 개선이 후속.

**비교 해석:** Binary tactile 전이 근거지만, 현재 환경 상태를 관측하므로 blind 정책과 다르다.

**원문:** [arXiv:2103.00410 PDF](https://arxiv.org/pdf/2103.00410), §IV-C–D/V-A–C/VI, Table I–III.

---

<a id="p05"></a>

## P05. Kato — Self-Tuning Impedance-Based Interaction Planner (2022)

| 비교축 | 원문 근거 |
| --- | --- |
| Observation | 환경 지도·geometry·외부 vision 없이 robot actual pose·history·추정 외력 사용. 자유 물체 조작 과업 아님. |
| Sensor | Panda 내부 torque sensing으로 외력 추정. 별도 손목 F/T·분포 촉각 없음. |
| Method | 힘 threshold 사이 실제 변위로 Exploration, 외력·과거 운동으로 Bouncing. FSM+방향성 impedance; 학습 없음. |
| 강건성 | 평면 미로 3개와 추가 screw 저항 조건에서 미지 환경 대응. 학습 데이터의 held-out 일반화와 구분. |
| Sim-to-Real | 학습 정책 전이 해당 없음. 직접 실물 알고리즘 검증. |

**저자 한계·Future:** 수동 threshold 조정·rigid 환경 한정. 3D maze·생체모사 탐색이 후속.

**비교 해석:** 미지환경의 rule-based 대응 사례. Sweeping 물체 이동과 구분한다.

**원문:** [arXiv:2203.05413v2](https://arxiv.org/html/2203.05413v2), §III–V, Algorithms1–2, Fig.5–9.

---

<a id="p06"></a>

## P06. Lin — Tactile Gym 2.0 (2022)

| 비교축 | 원문 근거 |
| --- | --- |
| Observation | Tactile-image 폐루프. 전체 actor observation·고유감각·goal/history 구성은 본문 미명시. ArUco object tracking은 평가 GT. |
| Sensor | TacTip·DIGIT·DigiTac 광학 촉각, Dobot MG400. Wrist F/T 없음. |
| Method | 실제 이미지→센서별 real-to-sim GAN→depth-image 표현→PPO→TCP action. Pushing·edge/surface following. |
| 강건성 | 미학습 실물 형상·궤적 적용. DIGIT의 가벼운 triangular prism pushing 실패를 추가 질량으로 개선. |
| Sim-to-Real | 정책 추가훈련 없이 전이하나 GAN용 실물 데이터·센서별 preprocessing/camera calibration 필요. |

**저자 한계·Future:** DIGIT의 뻣뻣하고 평평한 표면은 약한 접촉·오목 형상에 불리. 파지·다지 조작 적용 가능성 제시.

**비교 해석:** 직접 pushing 선행. 미명시 관측을 ‘전체 상태 사용’이나 ‘촉각만’으로 단정하지 않는다.

**원문:** [arXiv:2207.10763v2](https://arxiv.org/html/2207.10763v2), §III-B–F/IV/V, Table IV–VII.

---

<a id="p07"></a>

## P07. Brahmbhatt — Zero-Shot Haptics-Based Object Insertion (2023)

| 비교축 | 원문 근거 |
| --- | --- |
| Observation | 초기 noisy target 이후 상대 EEF pose+wrench의 8시점 stack. 물체 pose 추적 없음. |
| Sensor | 초기 camera+ArUco; 실행 EEF wrench·proprioception. 분포 촉각 없음; F/T 모델 미명시. |
| Method | 파지한 plate 삽입. MoveIt 접근→SAC residual+OSC; pose-noise curriculum·부분삽입 초기화·지연 반영. |
| 강건성 | 다른 실물 plate 3종·cup·방해물 평가. Small plate·cup에는 height 보상 Z offset 추가. |
| Sim-to-Real | 실물 정책 fine-tuning 없이 전이. 실제 지연 정보는 simulation 설정에 반영. |

**저자 한계·Future:** 큰 수평오차·base 회전에 취약, jam 회복 실패. Mobile manipulator 결합은 후속.

**비교 해석:** 초기시각+wrench RL 선행. Sweeping·binary tactile의 추가 가치가 차별점 후보이다.

**원문:** [arXiv:2301.12587v3 PDF](https://arxiv.org/pdf/2301.12587), §III–V, Table II, Fig.4–9, Supplement A.

---

<a id="p08"></a>

## P08. Attention for Robot Touch — Lin, 2023

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | 촉각 영상에서 목표 edge의 국소 특징 추정. 물체 전체 pose 입력 없음. |
| Sensor | TacTip 영상 → 접촉 깊이 → saliency map. 손목 F/T 없음. |
| Method | GAN·VAE 표현 학습; PoseNet–PID 또는 기존 RL에 연결. |
| 강건성 | 학습 밖 edge 형상·방해 접촉에서 실제 edge following 검증. 미지 물체 pushing은 아님. |
| Sim-to-Real | 제어 모델 fine-tuning 없이 사용; ConDepNet은 실물–sim paired data로 학습. |

**저자 한계·Future:** 가까운 distractor를 목표로 오인; 다른 광학 촉각 센서·과업으로 확장 제시.

**비교 해석:** 접촉 특징 선택의 근거이며 sweeping 직접 비교군은 아니다.

**원문:** IROS 2023; 확인 판본 [arXiv v2](https://arxiv.org/html/2307.14510v2), §III–V, Fig. 5–6, Table II.

---

<a id="p09"></a>

## P09. Bi-Touch — Lin, 2023

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | 두 촉각 영상·TCP 고유감각·목표. Gathering은 object-center에서 TCP 기준으로 curriculum 전환. |
| Sensor | 양팔 MG400·TacTip; GAN으로 실물 영상을 sim 표현으로 변환. 손목 wrench 없음. |
| Method | PPO; 접촉 안정화 reward, gathering의 goal-update mechanism. |
| 강건성 | 학습 밖 형상·중량·강성의 실물 물체와 반복 교란 시험. |
| Sim-to-Real | 정책 추가 학습 없는 전이; 영상 변환 GAN에는 실물 접촉 데이터 필요. |

**저자 한계·Future:** Shear 미모델링·교란 후 workspace 이탈; shear 근사와 지지면 없는 조작 확장.

**비교 해석:** Blind 비파지 조작 선행이지만 양팔·고해상도 영상 조건이다. 평가용 ArUco는 actor 입력과 구분한다.

**원문:** RA-L 2023; 확인 판본 [arXiv v1 PDF](https://arxiv.org/pdf/2307.06423), §III–V, Tables I–III, pp. 2–8.

---

<a id="p10"></a>

## P10. Tactile Pushing — Yang, 2023

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | 촉각 영상/추정 접촉면 pose·상대 목표. 물체 중심 pose는 모름; 목표도 접촉 위치 기준. |
| Sensor | MG400·TacTip; GAN 영상 또는 PoseNet 접촉 깊이·각도. 손목 wrench 없음. |
| Method | Image/pose SAC와 pose PETS–MPC 비교; 고정 전진+횡이동·회전. |
| 강건성 | 단일 cube·DR 없이 훈련; 미지 물체·목표·질량중심·장애물 교란 시험. 영상 정책 실패 존재. |
| Sim-to-Real | 정책/동역학 모델 추가 학습 없음; GAN/PoseNet은 실제 접촉 데이터로 사전 학습. |

**저자 한계·Future:** 고정 전진 때문에 가까운 목표·접촉면 탐색 제한; 제약 해제·실물 학습 제시.

**비교 해석:** Blind pushing 자체는 신규성이 아니다. 물체 이동량과 접촉 위치 목표를 구분한다.

**원문:** RA-L 2023; [공개 PDF](https://arxiv.org/pdf/2307.14272), §III–V, Tables I/III, Fig. 7.

---

<a id="p11"></a>

## P11. Rotating without Seeing — Yin, 2023

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | 관절 위치·이전 target·16bit 접촉·회전축의 4-frame stack. Object GT·물성은 critic 전용. |
| Sensor | Allegro 손바닥·손가락·손끝 FSR 16개. 손목 F/T 없음. |
| Method | Asymmetric PPO → 관절 증분 → EMA·PD. 물성·센서 dropout/지연 등 randomization. |
| 강건성 | Sim 물성 이동·held-out geometry 분리 평가; 실물 미지 물체 회전 검증. |
| Sim-to-Real | Sim 정책 직접 배포; threshold 정합 필요. Continuous보다 항상 우세하지는 않음. |

**저자 한계·Future:** 손가락 옆면의 감지 부족이 회전을 제한; 조밀한 센서·과업 확장.

**비교 해석:** Binary blind RL 선행. 지속 회전과 목표 pose 도달은 다르다; shape reconstruction은 사후 분석이다.

**원문:** RSS 2023; [arXiv v4 PDF](https://arxiv.org/pdf/2303.10880) 확인, §III–VI, Tables I–V, pp. 3–10.

---

<a id="p12"></a>

## P12. Haninger et al. — Differentiable Compliant Contact Primitives (2024)

| 항목 | 확인내용 |
| --- | --- |
| Observation | 관절 위치·토크로 접촉 파라미터 추정. 현재 물체 pose 추적 없음; 로봇·접촉 모델 필요 |
| Sensor | Motor current 또는 관절 토크. Sensorless 실험의 flange F/T는 검증용; tactile array 없음 |
| Method | 접촉 모델 fitting→EKF→MPC. 평면 접촉 이동·hinge pivot |
| 강건성 | 재질·법선·평면 높이·hinge 위치 변화 검증; 미학습 물체군 평가 없음 |
| Sim-to-Real | 실물 추정·제어 검증. Simulation 학습 정책의 전이 아님 |

**저자한계·Future:** 온라인 추정 지연과 공동 파라미터 추정의 발산 보고; 구체적 후속 계획 미명시.

**비교해석:** 숨은 접촉 모델을 추정하는 사례이며 자유 물체 sweeping의 검증은 아니다.

**원문:** [본문](https://arxiv.org/html/2303.17476v3), §4.2, §6.1–3, Fig.7–8, §7; [ICRA 출판](https://doi.org/10.1109/ICRA57147.2024.10611406).

---

<a id="p13"></a>

## P13. Force Push (2024)

| 비교축 | 원문 검증 내용 |
| --- | --- |
| Observation | 초기 근사 물체 위치, 실시간 로봇 pose·접촉점 위치. 현재 물체 pose·물성 없음. 벽 위치는 알려짐 |
| Sensor | FT300의 2D 힘. 촉각 없음. Vicon 물체 pose는 평가용 |
| Method | 비학습 pushing-angle 제어, 재접촉 규칙, admittance, QP IK |
| 강건성 | 형상·질량분포·마찰·초기 편차 변화. 학습셋 분리 없는 모델 미지 조건 |
| Sim-to-Real | simulation·실물 검증. 학습 전이 해당 없음. 실물 gain 조정 |

**저자 한계·Future:** 준정적 convex 단일 물체·충분한 이동 공간 가정. 안정성 증명·좁은 clutter·재접촉 개선은 향후 과제.

**비교 해석:** 비시각 force-pushing은 기존 성과다. 접촉점 경로 추종과 물체 중심의 목표 도달을 구분한다.

**원문 근거:** [공개본 v2](https://arxiv.org/html/2401.17517v2), §III–V, §VII, Table I, Fig. 10–14, §VIII.

---

<a id="p14"></a>

## P14. DexTouch — Lee, 2024

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | 로봇 고유감각·16bit 접촉·목표/탐색 영역 크기. 정확한 초기/현재 대상 pose 없음; object GT는 critic 전용. |
| Sensor | UR5e–Allegro·FSR 16개. Wrist F/T는 별도 sim 대조군이며 결합 입력이 아님. |
| Method | Asymmetric PPO·22D 관절 target·PD; grasp/door/valve별 정책. |
| 강건성 | 위치 randomization과 실물 unseen grasp 물체 시험; 무겁고 미끄러운 tumbler에서 저하. |
| Sim-to-Real | 정책 fine-tuning 없이 전이. 상세 물성·센서 DR는 미명시. |

**저자 한계·Future:** 영역 prior와 학습 밖 물성의 영향; 풍부한 촉각 정보·일반화 확장.

**비교 해석:** 접근부터 수행하는 binary blind arm-hand 선행. F/T-only 열세가 결합의 이득을 증명하지는 않는다.

**원문:** RA-L 2024; 확인 판본 [공개 v2](https://arxiv.org/html/2401.12496v2), §III–VI, Tables II/III. 출판본 전체 판본 차이 미대조.

---

<a id="p15"></a>

## P15. Tactile Active Inference Reinforcement Learning — Liu et al., 2024

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | Sim은 현재 로봇·물체 pose/velocity. Real은 로봇 하강 높이·회전각; 너트 각도 미관측. |
| Sensor | GelSight 계열 영상의 접촉 중심·깊이 합·optical-flow 특징. 실물 최종 입력목록 미명시. |
| Method | 전이모델 ensemble·reward model·information gain을 활용한 Active-Inference RL+CEM 계획. |
| 강건성 | 공·상자 pushing 및 미지 pitch screwing. Held-out 물체 일반화는 미보고. |
| Sim-to-Real | Sim pushing·real screwing을 별도 학습. Pushing policy 전이 미보고. |

**저자 한계·Future:** 단순 접촉 가정·실물 비교 비용 제약. 출판본 Future는 미명시이며 공개 초고의 향후 계획과 구분한다.

**비교 해석:** Contact-only blind pushing의 성공 근거로 분류할 수 없다.

**원문:** [IROS 출판본](https://doi.org/10.1109/IROS58592.2024.10802750), §III-B·IV-A–C·V, Figs.5–7. [공개 초고](https://arxiv.org/abs/2311.11287)는 결론 문단이 다르다.

---

<a id="p16"></a>

## P16. Pose-and-shear-based tactile servoing — Lloyd & Lepora, 2024

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | 실시간 TacTip 영상·EEF pose로 국소 contact pose/shear 추정. 전역 물체 pose 입력 없이 목표점 방향 보정. |
| Sensor | TacTip 광학 촉각 1–2개; pose/shear 평균·불확실성 표현. |
| Method | 지도학습 GDN+SE(3) Bayesian filter+feedforward/PID servo. |
| 강건성 | 기하·생활 물체, MDF/foam 표면, 단일·양팔 pushing 평가. Tall objects의 foam pushing은 실패. |
| Sim-to-Real | 실물 데이터 학습·실물 실험. Sim-to-real 해당 없음. |

**저자 한계·Future:** Slip aliasing, 평면·완만한 곡면 중심, planner 부재. 다양한 접촉 궤적·planning·다지 조작 확장을 제안한다.

**비교 해석:** 알고리즘 기반 제어도 비시각 pushing과 형상·마찰 변화에 대응한다. RL 자체를 우월성 근거로 삼기 어렵다.

**원문:** [IJRR 출판사 원문](https://journals.sagepub.com/doi/10.1177/02783649231225811), §3.1–3.3·4.2–4.3·5.4–5.7·6, Tables 3–5.

---

<a id="p17"></a>

## P17. Pushing in the Dark (2024)

| 비교축 | 원문 검증 내용 |
| --- | --- |
| Observation | 로봇 pose·접촉 위치·목표 좌표. 현재 물체 pose·orientation·물성 모델 없음 |
| Sensor | 베이스 capacitive skin 42 taxel을 thresholding해 대표 접촉점 계산. F/T 없음 |
| Method | 비학습 reactive pushing과 가장자리 접촉의 realignment 규칙 |
| 강건성 | 물체·질량분포·마찰 변화, point/line 접촉 전환, 옆·뒤 목표 시험 |
| Sim-to-Real | simulation·실물 검증. 학습 정책 전이에는 해당 없음 |

**저자 한계·Future:** 준정적 조작을 가정하며 원통의 상대적 성능 저하를 rolling 등으로 설명한다. 확인한 제출본의 구체적 future-work 제안은 미명시.

**비교 해석:** threshold 기반 접촉 정보만으로도 pushing이 가능하다. 성공 기준은 물체 중심이 아닌 접촉점과 목표 사이 거리다.

**원문 근거:** [공개 제출본 v1](https://arxiv.org/html/2403.09305v1), §II-B–C, Algorithm 1, §III-B–C, Table II, §IV.

---

<a id="p18"></a>

## P18. Sim2Real Manipulation on Unknown Objects — Su, 2024

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | 두 촉각 영상·관절 고유감각·목표각. 현재 object GT는 actor 입력이 아니며 reward/평가에 사용. |
| Sensor | DIGIT 2개; RGB/Diff/Binary **64×64 영상**. 센서당 1bit가 아님. |
| Method | 영상 encoder+PPO; 지지면 pivoting, 제한 EEF 이동·회전, gripper 폭 고정. |
| 강건성 | Multi-category 훈련; 실물 미지 물체·새 지지면 시험. |
| Sim-to-Real | 정책 fine-tuning·학습된 domain translator 없음. 무접촉 기준 영상·센서별 threshold 탐색은 필요. |

**저자 한계·Future:** 불안정 파지·불완전하거나 낯선 접촉 패턴에서 실패; 구체 신규 과업 계획 미명시.

**비교 해석:** 전이를 위한 표현 추상화 근거지만 영역별 binary와 달리 공간 패턴을 유지한다.

**원문:** [저자 프로젝트](https://tactilerl.github.io/)는 ICRA 2024 표기; 방법 확인은 [v1 원문](https://arxiv.org/html/2403.12170v1), §III–VI, Tables I–III.

---

<a id="p19"></a>

## P19. Wu et al. — 1 kHz Behavior Tree (2024)

| 항목 | 확인내용 |
| --- | --- |
| Observation | EEF z-position·속도와 관절 토크 유래 외력으로 접촉상태 추정. 명목 hole/task frame 사용 |
| Sensor | 로봇 관절 센싱·외력 추정. 표면 tactile array 아님 |
| Method | Insertion용 BT+adaptive impedance; PIBB evolution strategy로 skill parameter 학습 |
| 강건성 | 한 물체에서 학습한 skill을 다른 세 물체에 zero-shot 적용하고 별도 fine-tuning |
| Sim-to-Real | 실물 물체 간 전이. Simulation→실물 학습 전이 아님 |

**저자한계·Future:** 독립 Limitation 절 없음; 더 넓은 물체군의 skill transfer 평가 제안.

**비교해석:** 규칙과 파라미터 학습의 결합도 미학습 형상 대응을 보였다. 순수 rule-based나 end-to-end RL로 단순화하면 부정확하다.

**원문:** [저자 PDF](https://frankiewoo.github.io/publication/wu-2024-icra/wu-2024-icra.pdf), §II-B–D, Alg.1, 식8–9, §III-C, Fig.5–6, §IV, pp.2–6.

---

<a id="p20"></a>

## P20. Robot Synesthesia — Yuan et al., 2024

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | Student는 현재 depth·joint position·binary contact·직전 목표·history. Teacher는 물체 상태·shape embedding 추가. |
| Sensor | Allegro의 FSR 16개 binary+Azure Kinect depth. 활성 센서 위치를 point cloud로 표현. |
| Method | PPO teacher → PointNet student에 BC+DAgger 증류. |
| 강건성 | 단일·이중 물체 회전, 새로운 생활 물체·공 조합 평가. 우세는 조건별로 다름. |
| Sim-to-Real | 시뮬레이션 학습 후 실물 추가 fine-tuning 없이 전이. |

**저자 한계·Future:** Limitation 절 없음. Goal-conditioned rotation·optical tactile 통합을 제안한다.

**비교 해석:** 물체 일반화·무 fine-tuning 전이는 선행 성과다. Online depth는 우리 관측 조건과 다르다.

**원문:** [공개 원문](https://arxiv.org/html/2312.01853v1), §III-A–B·IV-A–C·V-D·VI, Tables III–IV. 공개는 2023, [ICRA 게재](https://yingyuan0414.github.io/visuotactile/)는 2024.

---

<a id="p21"></a>

## P21. Unknown Object Retrieval (2024)

| 비교축 | 원문 검증 내용 |
| --- | --- |
| Observation | actor는 촉각 9D만 입력. 물체 탐색 완료 가정. OptiTrack 변위는 보상용 |
| Sensor | XELA 4×4×3축 연속 힘 → 열별 normal·shear와 고주파 feature. Binary·손목 F/T 아님 |
| Method | SAC, 변위와 parameterized backward primitive, 목표 curriculum·replay 통합 |
| 강건성 | 학습과 구별되는 일상 물체 평가. 새로운 물체에서 추가 학습 없음 |
| Sim-to-Real | 실물 직접 RL 학습. simulation 전이 결과 없음 |

**저자 한계·Future:** 촉각·비강체 simulation 모델링의 어려움으로 직접 실물 학습을 선택했다. 경사·수직 환경은 향후 과제.

**비교 해석:** 저차원 촉각-only RL과 unseen 물체 조작은 기존 성과다. 우리의 binary+wrench·Hand sweeping·simulation 학습을 구분해야 한다.

**원문 근거:** [기관 공개 PDF](https://oar.a-star.edu.sg/storage/k/kro0r788qn/icra-2024-xinyuan.pdf), §III–IV, PDF pp. 3–6, Table II, §V.

---

<a id="p22"></a>

## P22. Precision-Focused RL Pushing (2025)

| 비교축 | 원문 검증 내용 |
| --- | --- |
| Observation | 매 step 물체 영상·goal latent·EEF XY·history. GT 좌표는 보상용 |
| Sensor | 가림을 피한 유리 테이블 아래 RGB·proprioception. Binary는 영상 mask이며 촉각 없음 |
| Method | 사전학습 autoencoder, SAC/HER·GRU, XY offset·유지 시간 출력 |
| 강건성 | 단순 cuboid/cylinder의 크기·질량·마찰 변화. arbitrary unseen 형상 검증 아님 |
| Sim-to-Real | simulation 정책을 실물 네 물체에 평가. 성공은 육안 판정 |

**저자 한계·Future:** 단순 형상·fully observable 환경·smoothness와 safety 보장 부재. 부분 관측·복잡 형상·안전 제어는 향후 과제.

**비교 해석:** GRU는 숨은 물성에 대응하지만 현재 시각을 대체하지 않는다. 실물 목표 정밀도를 계측으로 입증했다고 쓰면 안 된다.

**원문 근거:** [공개본 v1, 2024](https://arxiv.org/html/2411.08622v1), §III–V, §VII–VIII, §IX-B/Table II, §X.

---

<a id="p23"></a>

## P23. ViViDex — Chen et al., 2025

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | Student는 지속적인 scene point cloud+robot proprioception. PPO teacher는 robot·object state 사용. |
| Sensor | RealSense RGB-D; tactile·wrist F/T policy 입력 없음. Contact는 reward에 활용. |
| Method | Human-video trajectory → trajectory-guided PPO → BC/3D Diffusion student. |
| 강건성 | 초기 pose·목표 위치·seen/unseen object 평가. 실물 정량 과업은 relocate. |
| Sim-to-Real | 실물 trajectory로 visual policy 학습. Zero-shot 전이 아님. |

**저자 한계·Future:** 영상 trajectory·real point cloud noise와 state 추정 어려움. 인터넷 영상 활용·3D pose estimation 개선을 제안한다.

**비교 해석:** 지속적 시각 입력을 사용한다. Privileged teacher와 실행 student를 구분하는 대조 사례다.

**원문:** [공개 v3 원문](https://arxiv.org/html/2404.15709v3), §III-A–C·IV-A–E·V, Tables IV–VI. 초고는 2024, ICRA 게재는 2025.

---

<a id="p24"></a>

## P24. Dynamic Object Goal Pushing (2025)

| 비교축 | 원문 검증 내용 |
| --- | --- |
| Observation | actor: 현재 물체 pose·robot state·직전 action. Critic에 물성·접촉 등 privileged 정보 추가 |
| Sensor | 실물 MoCap으로 물체·base pose를 지속 갱신. pushing actor의 tactile·wrist wrench 없음 |
| Method | Constrained PPO·비대칭 actor–critic, base와 arm 명령, 사전학습 locomotion |
| 강건성 | 질량·크기·재료 변화와 학습하지 않은 caster-wheel dynamics 시험 |
| Sim-to-Real | 물성·관측 randomization을 거쳐 zero-shot 실물 전이 명시 |

**저자 한계·Future:** actuator 제한 부근 동작과 목표 직전 멈춤 사례. memory·onboard perception 추가는 향후 과제.

**비교 해석:** unknown object는 pose 미관측을 의미하지 않는다. 전도 대응 역시 현재 물체 pose 피드백을 유지한 결과다.

**원문 근거:** [공개본 v1](https://arxiv.org/html/2502.01546v1), §III-C/Table I, §III-D–E, §IV-C–D/Table V, §V.

---

<a id="p25"></a>

## P25. Location-Based Attention Pushing (2025)

| 비교축 | 원문 검증 내용 |
| --- | --- |
| Observation | 현재 object/goal pose, pusher XY, occupancy grid. 실물 dynamic scene에서는 grid 갱신 |
| Sensor | MoCap 또는 RGB-D 3대·AprilTags·point cloud. tactile·F/T 없음 |
| Method | PPO categorical XY velocity, location-based attention·LSTM |
| 강건성 | unseen 장애물 형상·배치·이동 시험. dual-obstacle 고성능에는 추가 simulation fine-tuning |
| Sim-to-Real | dynamics randomization·관측 noise 후 KUKA 실물 검증. 3Cam 결과는 정성 시연 |

**저자 한계·Future:** single-obstacle 정책의 dual-obstacle 직접 일반화 저하를 보고한다. 구체적 future-work 제안은 미명시.

**비교 해석:** unseen 장애물과 unseen 조작 대상 물체를 구분한다. 현재 기하 관측에 기반한 충돌 회피 과업으로, 접촉을 허용하는 blind sweep과 다르다.

**원문 근거:** [공개본 v3](https://arxiv.org/html/2403.17667v3), §III-B, §IV-A/Table I, §IV-D/Table II, §IV-E, §V.

---

<a id="p26"></a>

## P26. He et al. — FoAR (2025)

| 항목 | 확인내용 |
| --- | --- |
| Observation | 현재 RGB·RGB-D point cloud, 6D F/T 이력. EEF pose는 reactive controller 입력 |
| Sensor | RealSense D435, OptoForce wrist F/T. Tactile array 없음 |
| Method | Wiping·peeling·chopping의 실물 시연 IL: Diffusion Policy+contact predictor+reactive correction |
| 강건성 | Board 이동·새 그림 추가 등 실행 중 외란 평가; 미학습 물체 identity 평가와 구분 |
| Sim-to-Real | Real demonstration→real execution. Simulation 학습 전이 아님 |

**저자한계·Future:** 고정 F/T threshold·단순 position control의 제약; compliance/hybrid control 및 다른 로봇으로 확대 제안.

**비교해석:** 접촉에 따른 vision/force 융합의 근거다. 현재 시각을 계속 사용하므로 blind 수행으로 분류하지 않는다.

**원문:** [본문](https://arxiv.org/html/2411.15753v2), §III, Alg.1, §IV-A,E, Table IV, §V; [RA-L 출판](https://doi.org/10.1109/LRA.2025.3560871).

---

<a id="p27"></a>

## P27. Enhancing Tactile-based Reinforcement Learning — Miller et al., 2025

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | Proprioception·직전 action·binary contact history. Vision·현재 object state·privileged teacher 없음. GT는 reward/분석용. |
| Sensor | 시뮬레이션 link-level binary contact. 실물 센서 성능은 미검증. |
| Method | PPO+촉각 reconstruction/forward-dynamics SSL; 분리된 auxiliary memory. |
| 강건성 | Find·Bounce·Baoding의 접촉 패턴과 seed별 성능 비교. Held-out 형상 일반화는 미보고. |
| Sim-to-Real | 실물 미검증. Binary 채택의 전이 동기는 성공 증거와 구분. |

**저자 한계·Future:** 실물 검증 부재·SSL 계산량·memory 비용. 다른 환경 domain 적용 가능성은 기대 수준이다.

**비교 해석:** Blind+binary tactile+RL 자체는 이미 존재하며, 촉각의 추가 효용도 과업에 따라 다르다.

**원문:** [원문](https://arxiv.org/html/2510.21609v1), §3.1–3.3·4–7, Figs.3–7, Appendix E.

---

<a id="p28"></a>

## P28. Noseworthy et al. — FORGE (2025)

| 항목 | 확인내용 |
| --- | --- |
| Observation | Noisy EEF pose/velocity·fixed-part pose, 3D 힘, previous action·force threshold. Held-part pose·dynamics는 actor 비관측; GT는 학습용 |
| Sensor | Franka joint torque에서 EE force 추정. Wrist moment·tactile array 입력 없음 |
| Method | 조립용 recurrent PPO+asymmetric actor-critic, dynamics randomization, success prediction |
| 강건성 | Pose 추정 오차·workspace 위치·controller gain 평가; 미학습 형상군 일반화는 미확인 |
| Sim-to-Real | Task별 simulation RL→실물 직접 전이 |

**저자한계·Future:** 큰 pose noise와 단일 force threshold의 제약; torque sensing·real-to-sim 확대 제안.

**비교해석:** 접촉력 RL의 실물 전이는 선행 성과다. 자유 물체의 움직임·binary tactile 결합 조건으로 차별화를 검증해야 한다.

**원문:** [본문](https://arxiv.org/html/2408.04587v2), §II-B, IV-A–B, V-A–D, Table I, App.A, §VII; [2025 출판기록](https://research.nvidia.com/labs/srl/publication/noseworthy-2025-forge/).

---

<a id="p29"></a>

## P29. Yang et al. — Pseudo-Tactile Feedback (2025)

| 항목 | 확인내용 |
| --- | --- |
| Observation | 현재 RGB·EEF pose·binary gripper state. GT object pose는 demonstration expert용 |
| Sensor | RealSense D435i·Robotiq 2F-85 관절각의 pseudo-tactile. 별도 admittance의 wrench 측정 장치 미명시 |
| Method | Simulation expert 시연의 Diffusion Policy IL+빈 파지 재개방 규칙+arm admittance |
| 강건성 | Pose 변화와 강제 gripper closing 외란 평가. Recovery와 task success는 별도; held-out identity 미명시 |
| Sim-to-Real | Simulation demonstration으로 학습한 정책을 실물 파지·서랍/오븐 열기에 적용 |

**저자한계·Future:** 기구학 오차의 stress에 admittance로 대응; 구체적인 future work 미명시.

**비교해석:** Binary 상태의 의미를 저수준 제어로 유지하는 사례다. 현재 RGB를 사용하는 IL이므로 blind tactile-only RL과 구분한다.

**원문:** [본문](https://arxiv.org/html/2503.23835v1), §IV-A–C, V-A–C, Table I–IV, §VI; [IROS 출판](https://doi.org/10.1109/IROS60139.2025.11246513).

---

<a id="p30"></a>

## P30. The Role of Tactile Sensing for Learning Reach and Grasp — Zhang et al., 2025

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | TCP pose·gripper opening+tactile+현재 visual 정보. 조건별 pose/type, RGB encoder, FoundationPose 사용. |
| Sensor | Minsight fingertip 2개. Global/local binary·magnitude·3D force 비교; wrist 6D wrench가 아님. |
| Method | SAC/MPO; tactile quantity·area·vision noise·history ablation. |
| 강건성 | Sim unseen objects, real 물체 및 사람이 위치·자세를 바꾸는 외란 평가. |
| Sim-to-Real | Noise·delay·friction/controller randomization 후 실물 검증. VK는 실물 평가 제외. |

**저자 한계·Future:** 통제 환경·sensor deformation 생략·알고리즘 의존. Blind grasping·multi-finger manipulation을 후속 과제로 제시한다.

**비교 해석:** Global force와 local contact의 보완성 근거지만, wrist wrench+binary sweeping의 직접 검증은 아니다.

**원문:** [원문](https://arxiv.org/html/2502.20367v1), §III-A–C·IV-A–E·V, Figs.4–11, Tables III–V.

---

<a id="p31"></a>

## P31. Gentle Object Retraction (2026)

| 비교축 | 원문 검증 내용 |
| --- | --- |
| Observation | 실행 중 eye-in-hand 영상, TCP pose, acquisition binary, wrench·tactile image |
| Sensor | 관절 토크 추정 wrench·양측 49-taxel 3축 연속 촉각. 손목 F/T·binary tactile 아님 |
| Method | 실물 demonstration의 Diffusion IL. 영상·촉각 encoder와 저차원 관측 결합 |
| 강건성 | unseen 장면 배치 평가. 고정 target/obstacle 종류. OOD 물체는 향후 과제 |
| Sim-to-Real | 실물 demonstration 학습·평가. simulation 전이 결과 없음 |

**저자 한계·Future:** 적은 demonstration, task-specific force threshold, 형태·외관 변화 미검증. multifinger hand·OOD 물체·RL 보정은 향후 과제.

**비교 해석:** wrench+tactile 상보성은 이미 연구됐다. 계속되는 영상과 연속 촉각을 우리의 관측 제한과 구분한다.

**원문 근거:** [공개본 v2, 2025](https://arxiv.org/html/2508.19476v2), §III/Fig. 3, §IV-A–C, §V/Fig. 6, §VI–VII.

---

<a id="p32"></a>

## P32. Beyond Binary — Pan, 2026

| 비교축 | 원문 확인 내용 |
| --- | --- |
| Observation | 고유감각·이전 command/action·CoP와 GRU 상태. 현재 object GT·goal 상태는 critic 전용. |
| Sensor | Allegro–uSkin 손끝 taxel → CoP 위치·force. Sim shear 불신으로 normal 성분만 사용; wrist F/T 없음. |
| Method | 물리 기반 taxel–CoP mapping·센서 교정·GRU asymmetric PPO. |
| 강건성 | Insertion OOD 초기 자세·taxel masking, 실물 공의 rolling 변화 시험. Insertion shape의 held-out 여부 미확인. |
| Sim-to-Real | 정책 zero-shot; 실제 센서 교정·paired rollout 정합·actuator 식별·지연 측정 동반. |

**저자 한계·Future:** Shear 손실·sim/hardware 접촉 범위 불일치; arm-hand·전체 hand coverage·다른 센서로 확장.

**비교 해석:** 위치·하중 상보성의 선행. Binary+wrist wrench와 구분하되 상보성은 신규성이 아니다.

**원문:** 정식 게재 미확인; [arXiv v1](https://arxiv.org/html/2605.28812v1), 2026-05-27, §III–VI, Tables 1/2, Appendix A–E.

---

<a id="p33"></a>

## P33. Šimundić et al. — Visuo-Force-Tactile Door Opening (2026)

| 항목 | 확인내용 |
| --- | --- |
| Observation | 초기 RGB-D 문 기하·회전축 모델, tool pose·접촉 사건. Contact loss 후 RGB-D로 현재 문 상태 재추정 |
| Sensor | Wrist FT300-S·fingertip XELA uSPa44·RGB-D. 힘은 충돌, tactile은 접촉/miss/loss 검출 |
| Method | FSM+기하 계획; 실패 정보로 camera parameter 보정·재계획. RL/IL 정책 아님 |
| 강건성 | Calibration perturbation과 한 실물 cabinet의 여러 pose 평가. 성공률은 재시도 포함 |
| Sim-to-Real | Simulation·실물 알고리즘 검증. 학습 정책의 전이 아님 |

**저자한계·Future:** 정확한 접촉점 불명으로 후보 탐색 비용 발생; force direction과 전체 gripper tactile coverage 활용 제안.

**비교해석:** F/T+tactile 결합은 선행 사례가 있다. 재촬영이 존재하므로 initial-vision-only 조건과 다르다.

**원문:** [출판본](https://doi.org/10.1109/ACCESS.2026.3655617)을 직접 읽음. §III-A,D–E, VI-B, VII-B, VIII, pp.4–5,12,14–15,17.

---

현재 연구의 센서·성능·실물 전이 행은 기존 연구 결과와 같은 완료 상태가 아니다. 발표용 해석과 검증 제안은 [본문](../../presentation/04_Related_Work_Timeline_and_Contributions.md)에 있다.
