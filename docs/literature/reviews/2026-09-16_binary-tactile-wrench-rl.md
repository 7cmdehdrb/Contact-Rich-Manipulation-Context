# Blind Sweeping을 위한 Binary Tactile·F/T 기반 RL 신규 문헌 조사

조사 기준일: **2026-09-16**. 기존 저장소 문헌과 중복되는 연구를 제외한 추가 조사다.

[문헌 색인](../README.md) · [구체적인 입력 처리·실험 제안](2026-09-16_binary-tactile-wrench-design-notes.md) · [현재 연구 범위](../../00_HANDOFF_BRIEF.md)

## 1. 핵심 답변

**저항식 촉각 신호를 영역별 0/1로 바꾸어 RL에 사용하는 실물 연구는 존재한다. 가장 직접적인 구현 참고는 DexTouch와 Rotating without Seeing이다.** 두 연구는 FSR 16개의 접촉 분포를 사용한다. 전체 손의 접촉 여부를 하나의 Boolean으로 축약하는 방식과 다르다. [B1, B3]

**Binary는 force amplitude의 정밀한 sim-to-real 매칭 부담을 줄일 수 있다. 그 대가로 하중 크기·접촉 중심·영역 내부 분포를 잃는다.** 실물에서 continuous보다 유리한 비교가 있는 반면, 상세 접촉 표현이 더 나은 반대 사례도 있다. 따라서 ‘binary가 정확하다’는 표현은 접촉 검출 정확도, 과업 성공률, 전이 강인성 중 무엇을 뜻하는지 구분해야 한다. [B3, C1]

**F/T를 RL에 사용하는 방식도 하나가 아니다.** CHEQ는 측정 force 3D를 actor에 직접 넣고 motion·impedance를 학습한다. SRL-VIC는 6D wrench를 actor와 safety/recovery 모델에 넣는다. High-quality Wiping은 F/T 관측과 접촉·힘·진행 보상 설계를 결합한다. AFORCE는 목표 wrench를 action으로 내고 빠른 저수준 controller에서 힘을 다루는 참고 사례다. [W1–W4]

이번 조사에서 **기존 문헌을 제외한 ‘실물 Blind object sweeping + F/T actor + RL’의 완전 일치 사례는 확보하지 못했다.** 이것은 해당 연구의 부재나 신규성 증명이 아니다. 신규 자료를 아래처럼 구분했다.

- **주요 참고 5편:** B1의 저항식 binary 구현, B2의 실제 binary pushing, W1–W3의 지속 접촉·힘 기반 RL.
- **제한적 방법 참고 3편:** B3의 binary 대 continuous 실물 비교, B4의 sparse-contact 표현학습, W4의 wrench action/controller 분리.
- **반대 근거 1편:** C1. Binary의 정보 손실을 보여주지만 삽입 과업을 연구 범위로 추가하는 근거는 아니다.

## 2. 범위·중복·증거 기준

### 2.1 프로젝트 기준

대상은 **UR5e–손목 6축 F/T–Inspire Hand 계획에서, 접근 완료 후 초기 정보와 실시간 접촉 감각으로 수행하는 하위 Blind Sweeping**이다. 초기 시각 사용은 허용하고 실행 중 연속 object-pose 추적은 사용하지 않는 조건을 유지한다. 센서 커버리지와 약한 접촉, 기본 조작 가능성이 우선이다. 상위 탐색·접근·회전 조작을 자동 포함하지 않는다.

17개 tactile 영역을 scalar/Boolean으로 축약하는 안은 제안이며 실제 원시 출력 명세가 아니다. 본 보고서의 모델·전처리·실험 제안도 **PROPOSED**다. 기존 결정 문서나 구현 현황을 변경하지 않는다.

### 2.2 제외한 기존 자료

저장소 `main`의 조사 시작 커밋은 `427486e623200a52f3857e763c8ef20f97fd2461`이다. 다음 경로에서 제목·약칭·저자·식별자를 대조했다.

- [2026-09-14 조사](2026-09-14_blind-sweep-force-torque-tactile.md)의 R1–R7과 대조 문헌.
- [IROS 2023–2025 제목 선별](2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md)의 후보·제외표·후속 선정.
- [개별 정독 노트](../papers/README.md)와 [사용자 별도 발굴 목록](../collections/user-found-papers.md).
- 대화에서 이미 검토한 MAT 등 기존 문헌.

Force Push, Pushing in the Dark, Tactile Gym 2.0, Bi-Touch, Yang의 tactile pushing, Tactile-AIRL, Gentle Object Retraction 등은 신규에 포함하지 않았다. 제목만 선별됐던 SAVR·ProSIP·distributed tactile dragging 등도 재등록하지 않았다. preprint·학회·저널 확장판은 동일 연구 계열을 확인해 중복 계수하지 않는다.

기존 **Pseudo-Tactile gripper-state 논문은 Diffusion Policy 기반 모방학습**이며, 전용 tactile 배열의 힘을 bit로 바꾼 RL 연구가 아니다. 그 연구의 binary gripper state와 이번 조사의 영역별 binary tactile은 구분해야 한다. 기존 정독 결과를 재확인한 사항이며 신규 선정은 아니다. [기존 상세 노트](../papers/2025-yang-pseudo-tactile-gripper-state.md)

### 2.3 검색·원문 확인

요청한 **Sider Scholar의 OpenAlex 및 Scholar 검색**을 사용했다. 주요 질의는 `binary tactile reinforcement learning`, `binary tactile sim real manipulation`, `force feedback reinforcement pushing`, `robotic wiping reinforcement`, 각 후보의 정확한 제목이었다. 관련 없는 결과나 누락이 있어 저자 공개 원문·출판정보·공식 프로젝트·공개 코드로 교차 확인했다. 검색 스니펫만으로 방법·성능을 확정하지 않았다.

연도 제한은 이번 요청에 없으므로 직접 binary pushing과 실물 표현 비교에 중요한 2016·2021·2023년 자료도 포함했다. 이전 조사의 ‘2022년 이후 SCIE’ 조건을 이번 조사에 자동 적용하지 않았다. 학회·저널·preprint 상태는 논문마다 표시한다.

원문 확인은 재현 실험과 다르다. 코드는 W1의 공개 구현을 정적으로 확인했으며 학습·실물 실험을 실행하지 않았다. 하드웨어 제조사 사양을 별도로 조사한 작업도 아니다.

## 3. 신규 연구 비교표

| ID | 연구·연도 | 확인한 접촉 표현 | 정책·실행 조건 | Blind Sweeping에 가져올 것 / 경계 |
| --- | --- | --- | --- | --- |
| B1 | DexTouch, 2024 | 저항식 FSR 16bit | PPO, 실물 Blind seek/grasp/door/valve | LPF·threshold·coverage 비교. Sweeping 실험은 없음 |
| B2 | Koval et al., 2016 | strain-gauge threshold의 접촉 bits | POMDP 계획, 실물 planar pushing | 접촉 이력으로 belief 갱신. **RL 아님**, 알려진 geometry 필요 |
| B3 | Rotating without Seeing, 2023 | 저항식 FSR 16bit | PPO, 실물 in-hand rotation | Binary/continuous 직접 비교·history·dropout. 표현 참고에 한정 |
| B4 | Enhancing Tactile-based RL, 2025 | 시뮬레이션 sparse binary contact | PPO+보조 표현학습, sim-only | bits가 무시되는 조건·이력 학습. 실물 전이 근거 아님 |
| W1 | CHEQ-ing the Box, 2025 | F/T의 **힘 3D만** actor에 입력 | SAC 계열+prior 혼합, 실물 polishing | 수치 concat·필터·motion/impedance. 고정 경로/표면 전제 |
| W2 | SRL-VIC, 2024 | 6D wrench | SAC+recovery, 실물 Blind maze | wrench 기반 motion/stiffness 선택. 자유 물체 이동 목표와 다름 |
| W3 | High-quality Wiping, 2025 | F/T 포함 46D 관측 | Blind RL, sim-only | 접촉/힘과 진행의 보상 충돌 방지. 세부 RL optimizer 미명시 |
| W4 | AFORCE, 2021 | 목표 wrench action·측정/추정 wrench 제어 | SAC는 simulation; 실물은 expert | 고주파 force loop 분리. 실물 learned-RL 전이로 분류 금지 |
| C1 | Beyond Binary, 2026 | binary 대 힘+접촉 중심 | PPO, 실물 blind insertion/balancing | 정보 손실 반대 근거만 사용. Sweeping 직접 비교군 아님 |

## 4. Binary tactile: 방법과 근거

### B1. DexTouch: Learning to Seek and Manipulate Objects with Tactile Dexterity

**2026-09-17 후속 정독:** 사용자가 제공한 IEEE 출판본 8쪽을 기준으로 [상세 논문 노트](../papers/2024-lee-dextouch.md)를 추가했다. 아래 최초 조사 요약은 arXiv v2 기준이며, 상세 노트에서는 출판본의 명시 범위를 따로 확인한다. 원문 식 (1)–(4), Table I–III 전체 수치, 실물 시행 수의 해석 범위와 미명시 구현 정보를 정리했다.

**Kang-Won Lee, Yuzhe Qin, Xiaolong Wang, Soo-Chul Lim. IEEE RA-L 9(12):10772–10779, 2024.** [DOI](https://doi.org/10.1109/LRA.2024.3478571) · [확인 원문 v2](https://arxiv.org/html/2401.12496v2) · [저자 프로젝트](https://lee-kangwon.github.io/dextouch/)

**문제·센서:** 시각 없이 물체를 찾고 조작한다. UR5e+Allegro의 손가락에 각각 3개, 손바닥에 4개의 FSR을 부착한다. 실물 전압을 STM32F103에서 **125 Hz로 획득→LPF→전송→threshold→16bit**로 처리한다. Simulation은 독립 센서 영역의 net-contact-force norm을 **0.01 N**으로 이진화한다. 실물 전압 threshold·LPF 차수/cutoff·hysteresis·debounce는 미명시다. [§III-A, IV-A]

**RL 연결:** asymmetric PPO actor는 관절 위치·속도 각 22D, binary 16D, palm pose/twist 13D, fingertip 위치 12D, 과업 정보 5D 또는 2D를 사용한다. MLP는 `[512,256,128]`, 출력은 22개 관절 위치 명령이며 10 Hz 정책 아래 PD가 실행한다. Critic의 물체 pose·속도·물성과 actor 입력을 구분한다. [§IV]

**효용:** simulation 3 seeds의 grasp/door/valve 성공률은 기본 binary **.72/.69/.82**, threshold를 .3 N으로 높이면 **.37/.37/.58**, wrist-F/T 대조군은 **.26/.29/.50**다. 이는 감도·분포의 중요성을 보여주며 continuous tactile 대비 우위를 검증한 표는 아니다. F/T 비교도 **sim-only**다. Fine-tuning 없는 실물 grasp seen/unseen은 **64%/47%**, door **60%**, valve **67%**다. [§V, Tables II–III]

**저자 Limitation:** 낮은 감도의 과도접촉·낙하, 무겁고 미끄러운 미학습 물체의 성능 저하. [§V-B/E] **Future Work:** 3축 tactile과 일반화 확대. [§VI]

**프로젝트 해석:** 가장 우선해서 읽을 저항식 binary 구현 사례다. **0.01 N을 FSR 제품의 검출 성능이나 Inspire 설정으로 옮기지 않는다.** 파지와 자유 물체 Sweeping의 힘·이동 요구가 다르므로 F/T의 일반적 열세도 결론낼 수 없다.

### B2. Pre- and post-contact policy decomposition for planar contact manipulation under uncertainty

**Michael C. Koval, Nancy S. Pollard, Siddhartha S. Srinivasa. IJRR 35(1–3):244–264, 2016; online 2015.** [DOI](https://doi.org/10.1177/0278364915594474) · [저자 공개 PDF](https://personalrobotics.cs.washington.edu/publications/koval2015pomdp.pdf)

**문제·센서:** Barrett WAM+Hand로 병을 평면에서 밀어 hand-relative goal에 도달시킨다. distal-finger **strain gauge를 trial마다 재보정하고 threshold로 이진화**한다. FSR이라고 바꿔 부르면 안 된다. 실물 threshold 수치·필터·sample rate는 미명시다. [§7–8, PDF pp.11–16]

**정책 연결:** 초기 object-pose belief에서 시작하여 pre-contact particle filter, post-contact discrete Bayes filter로 접촉 이력을 누적한다. SARSOP로 POMDP 정책을 구하고 전방·좌우·대각의 5개 평면 action을 실행한다. **PPO나 딥RL이 아닌 모델 기반 belief-space planning**이다. 관측 모델은 contact/no-contact 구분을 완전하다고 가정하고 접촉 중 관측에 10% 오류를 둔다. [§7]

**효용:** 동일 30개 실물 초기 배치에서 SARSOP **27/30**, QMDP **20/30** 성공. 정보 획득의 가치를 고려한 정책 비교이며 binary 대 continuous ablation은 아니다. [§8.3–8.4]

**저자 Limitation:** 알려진 geometry·준정적 모델, 이산화 계산량, planning의 운동학 제약 미포함, 모델 밖 불확실성, grasp 실행 판단의 외부 관찰자 의존. [§8.2/8.4, §9.1–9.4] **Future Work:** 연속 공간 추론·전체 configuration 계획·grasp 실행을 포함한 목표 설계. [§9.2–9.4]

**프로젝트 해석:** Binary만으로도 폐루프 pushing이 가능하다는 가장 직접적인 과업 참고다. 그러나 명시적인 geometry/belief estimator를 현재 프로젝트의 필수 구성으로 가져오는 것은 별도 결정이다. 2014 RSS 선행판과 별도 신규 2편으로 세지 않는다.

기존 IROS 목록의 *Pre-and Post-Contact Policy Decomposition for Non-Prehensile Manipulation with Zero-Shot Sim-To-Real Transfer*는 **Minchan Kim 등, 2023, DOI 10.1109/IROS55552.2023.10341657**의 별도 연구다. B2와 제목 일부가 유사하지만 저자·DOI·방법이 다르다. [기존 후보의 원문](https://arxiv.org/abs/2309.02754)

### B3. Rotating without Seeing: Towards In-hand Dexterity through Touch

**Zhao-Heng Yin, Binghao Huang, Yuzhe Qin, Qifeng Chen, Xiaolong Wang. RSS 2023.** [DOI](https://doi.org/10.15607/RSS.2023.XIX.036) · [확인 PDF](https://arxiv.org/pdf/2303.10880) · [저자 프로젝트](https://touchdexterity.github.io/)

**사용 이유:** in-hand rotation은 직접 연구 범위 밖이지만 **binary 대 continuous의 실물 비교와 이진화 전이 방법**을 확인하기 위해 제한적으로 포함한다.

FSR 전압을 threshold해 16bit로 만든다. Simulation은 센서용 링크의 force norm **.01 N** threshold를 사용하고 부모 링크 접촉을 포함하지 않는다. Actor는 관절 위치 16D, bits 16D, 이전 관절 목표 16D, 회전축 3D의 현재+과거 3프레임을 받는다. Asymmetric PPO가 상대 관절 명령 16D를 10 Hz로 출력한다. Action EMA .8은 **센서 필터가 아니다**. 활성 bit의 dropout .1, lag probability .25, PD system identification을 사용한다. 실물 threshold 전압·tactile LPF/hysteresis는 미명시다. [§III–IV, Appendix]

**직접 비교:** Table I의 30초 실물 trial/3 seeds에서 seen C1 회전수는 binary **4.91±.52**, continuous **2.50±3.25**; unseen apple은 **2.67±1.04**, **.42±.52**다. 반면 rubber duck은 **1.42±.38**, **1.50±.75**로 모든 물체에서 binary가 앞서지는 않는다. 저자는 continuous의 큰 편차를 sim-real 힘 측정 차이와 연결한다. [§V-E, PDF p.7]

**저자 Limitation:** x/y 회전에서는 finger-side 접촉이 현재 센서로 관측되지 않아 실패한다. [§V-I, p.10] **Future Work:** 더 촘촘한 배열과 다양한 과업. [§VI]

**프로젝트 해석:** 이진화의 전이상 이점을 지지하지만 threshold·dropout 수치를 그대로 복사할 근거는 아니다. 접촉 영역을 누락하면 bit의 단순성만으로 해결되지 않는다.

### B4. Enhancing Tactile-based Reinforcement Learning for Robotic Control

**Elle Miller, Trevor McInroe, David Abel, Oisin Mac Aodha, Sethu Vijayakumar. NeurIPS 2025.** [원문 v1](https://arxiv.org/html/2510.21609v1) · [저자 프로젝트](https://elle-miller.github.io/tactile_rl/)

**문제:** Sparse binary 정보를 추가해도 RL이 자동으로 활용하지 않는다. Isaac Lab의 Find·Bounce·Baoding에서 이를 비교한다. Find는 독립 finger plate 2개, Shadow 계열은 link 17개의 simulated contact를 이진화한다. **실물 센서 실험은 없다.** [§3–4]

**RL 연결:** Find 16프레임, 나머지 4프레임의 proprioception·이전 action·binary history를 concat하여 MLP encoder `[1024,512,256]`와 PPO actor/value에 전달한다. Tactile reconstruction은 latent에서 접촉 bits를 복원하는 weighted BCE, forward-dynamics 보조학습은 action-conditioned latent 예측과 EMA target encoder를 사용한다. 과거 rollout을 별도 보조 버퍼에 저장하며 배포 시 보조 decoder는 제거할 수 있다. [§3.1–3.3, Appendix E–F]

**효용:** Find의 RL-only에서는 tactile 추가 최종 성능이 proprioception과 유사한 반면, Baoding에서는 binary가 유용하고 보조학습이 성능을 높인다. 이는 **binary 대 continuous 비교도, sim-to-real 비교도 아니다**. [§6, Appendix A]

**저자 Limitation:** 실물 미검증, 보조학습의 계산·메모리 비용. [§7] **Future Work:** 과거/off-policy 경험을 on-policy 표현학습에 사용하는 방향. [§6 Q6, §7]

**프로젝트 해석:** 17bit 입력도 PPO가 무시할 수 있다. 현재 입력/이력 기준선을 비교한 다음 representation learning의 필요성을 판단할 근거다. 논문의 17 link를 Inspire의 17개 영역과 동일시하지 않는다.

## 5. F/T·Wrench: RL에 들어가는 경로

### W1. CHEQ-ing the Box: Safe Variable Impedance Learning for Robotic Polishing

**Emma Cramer, Lukas Jäschke, Sebastian Trimpe, 2025.** 분석은 [arXiv 2501.07985v1 및 부록](https://arxiv.org/html/2501.07985v1) 기준. [저자 코드](https://github.com/Data-Science-in-Mechanical-Engineering/polishing-cheq). 출판사 최종본은 이번에 확인하지 못해 preprint 방법·설정을 기준으로 기록한다.

**정책 경로:** 고정 곡면의 주어진 경로를 따라 polishing한다. **74D observation**은 관절/EEF 상태, 다음 5개 경로점에 대한 오차, F/T 센서의 **3D force**를 concat한 것이다. Torque 3D는 actor에 포함하지 않는다. SAC 계열 CHEQ가 **Δpose 6D+stiffness diagonal 6D+damping ratio 1D**를 출력하고, critic ensemble의 불확실성에 따라 nominal controller 출력과 혼합한다. 그 결과를 Cartesian impedance controller가 실행한다. [§3–4, 식(1)–(5)]

**전처리:** 실물 F/T에는 **35 Hz low-pass**, 정책은 **20 Hz**, action 후 관측까지 **33 ms**를 둔다. 10-step 평활화는 **critic uncertainty**에 적용하며 힘 이력 encoder가 아니다. Force 좌표계·정규화·보정 상세는 충분히 명시하지 않는다. [Appendix C]

**학습·실물:** 힘은 observation 외에 목표 norm 오차 보상과 한계 초과 판단에도 쓰인다. 실물에서 약 8시간/250k steps 학습과 5회 실패를 보고한다. 알려진 경로·nominal policy를 갖춘 설정이며 독립적인 model-free RL의 무사고 보장이 아니다. [§6]

**저자 Limitation:** 이론적 안전 보장 없음, drift·운동 잡음, 낮은 제어율·혼합비 변동의 chatter와 후반 개선 정체. [§1, §6, Appendix C] **Future Work:** §7에서 구체적인 후속 계획은 미명시.

**코드 추가 확인:** 공개 commit `1a3c1fee3332848068afdb127c4fa33eee420418`의 [`sim_robot_env.py`](https://github.com/Data-Science-in-Mechanical-Engineering/polishing-cheq/blob/1a3c1fee3332848068afdb127c4fa33eee420418/environments/sim_robot_env.py)에서 `_get_observation()`의 force3 concat을 확인했다. Simulation substeps의 force vector들을 모아 **norm으로 정렬한 중앙의 원래 vector**를 선택한다. 축별 median이 아니다. 이는 공개 simulation 구현 확인이며 실물 필터 코드나 논문 각 실험의 정확한 재현을 확인한 것은 아니다.

**프로젝트 해석:** 측정 힘→수치 관측→motion/impedance 선택의 구체적 구현 참고다. 고정 표면의 경로 오차는 자유 물체의 이동 오차와 다르다. 35 Hz는 원시 센서 sampling rate가 아니라 필터 설정이며, 20 Hz 샘플열에 그대로 적용할 수치가 아니다.

### W2. SRL-VIC: A Variable Stiffness-Based Safe Reinforcement Learning for Contact-Rich Robotic Tasks

**Heng Zhang, Gokhan Solak, Gustavo J. G. Lahr, Arash Ajoudani. IEEE RA-L 9(6):5631–5638, 2024.** [DOI](https://doi.org/10.1109/LRA.2024.3396368) · [원문 v1](https://arxiv.org/html/2406.13744v1)

**문제·경로:** Franka의 flange가 시각 없이 미로를 통과하며 벽 접촉과 이동 가능한 장애물을 다룬다. 실물에서는 볼트를 밀어 통과한다. Task actor는 **EEF position 3D+wrench 6D=9D**, safety critic/recovery의 상태 입력은 **wrench 6D**다. Safety critic은 후보 action도 함께 평가한다. 위치를 safety 상태에서 제외해 벽 좌표 암기를 줄인다. SAC task policy와 DDPG recovery policy가 **ΔPx, ΔPy, Kx, Ky**를 출력하고 VIC가 실행한다. [§III-B, IV-A]

**힘 사용:** wrench는 정책 관측, 힘 한계 위반은 reward·termination·risk 학습에 사용한다. 시뮬레이션 관측에 OU noise를 넣어 재훈련한 뒤 실물 fine-tuning 없이 전이했다. 최초 실물 **4/5**, 재훈련 후 **6/6**은 소규모 해당 시험의 결과다. Sensor 모델·wrench 관측 정규화·LPF·history는 원문에서 확정하지 못했다. Action은 정규화하고 controller에 적용하기 전 역변환한다. [§IV-A/C]

**저자 Limitation:** single maze 학습은 새로운 일부 형태의 출구를 찾지 못한다. 안전 모델 일반화와 task 일반화는 다르며, sensing/dynamics 차이도 전이 실패 원인이었다. [§IV-C] **Future Work:** 더 일반적인 과업, model-based RL 통합. [§V]

**프로젝트 해석:** 저항 증가 시 감속만 하는 대신 motion과 stiffness를 함께 바꾸는 근거다. 미로 탐색은 저자가 extended peg-in-hole로도 설명하는 경계 과업이며, 지정 물체를 목표 거리만큼 Sweep하는 검증은 아니다. Safety/recovery 모델을 현 프로젝트의 필수 기여로 추가하지 않는다.

### W3. Learning a High-quality Robotic Wiping Policy Using Systematic Reward Analysis and Visual-Language Model Based Curriculum

**Yihong Liu, Dongyeop Kang, Sehoon Ha, 2025.** [확인 원문 arXiv 2502.12599v1](https://arxiv.org/html/2502.12599v1). 본 분석은 공개 원고 기준이며 실물 결과는 없다.

**관측·행동:** 미지 곡률·마찰 표면에서 힘을 유지하며 waypoint를 방문하는 **blind wiping policy**다. F/T, waypoint, 관절·EEF 상태 등을 포함한 **46D observation→6D pose action→OSC_POSE 20 Hz**를 사용한다. 본문에서 PPO/SAC 등 RL optimizer 이름, actor/critic 구조, F/T 필터·정규화·history는 확인되지 않아 미명시로 남긴다. 46D 성분별 차원도 임의 복원하지 않는다. [§III-A, V-A]

**보상 설계:** force reward는 목표 $f_z$에서의 Gaussian형 점수와 alignment 조건을 결합한다. 접촉·힘 보상을 매 timestep 누적하면 제자리 접촉이 유리해질 수 있으므로 **새 checkpoint 영역에 도달할 때 지급하는 bounded reward**로 바꾼다. 별도의 binary contact reward flag는 tactile bits가 actor에 들어갔다는 뜻이 아니다. VLM은 학습 실패 영상을 해석해 curriculum/weight 조정을 지원하며 **실행 actor에 영상이 들어가는 구조가 아니다**. [§III–IV]

**효용:** simulation 5 seeds에서 기본→bounded→bounded+VLM 성공률은 **58%→92%→98%**다. 목표 힘 60 N은 해당 실험 설정이며 사용자 장비·Sweep 목표로 이식하지 않는다. [§V, Table I]

**저자 Limitation:** 실물 성능과 wiping 밖 복잡한 과업에서의 VLM 시스템 일반화가 미검증이며 사전 waypoint 제공을 가정한다. **Future Work:** hardware 검증, 관측으로부터 waypoint 자동 생성, VLM의 다른 복잡한 과업 적용을 검토한다. [§VI]

**프로젝트 해석:** ‘힘을 낮추거나 접촉만 유지하면서 진행하지 않는 정책’을 방지하는 보상 설계가 직접 유용하다. 다만 wiping waypoint 완료를 물체 변위 성공으로 바꾸어 해석하면 안 된다.

### W4. AFORCE — Learning Robotic Manipulation Skills Using an Adaptive Force-Impedance Action Space

**Maximilian Ulmer, Elie Aljalbout, Sascha Schwarz, Sami Haddadin. arXiv preprint, 2021.** [확인 원문 v2](https://arxiv.org/html/2110.09904v2)

**포함 이유:** measured wrench observation, desired wrench action, low-level force feedback의 차이를 보여주는 보조 사례다.

Simulation wiping에서 **SAC 20 Hz→desired pose+wrench→adaptive force/impedance controller 500 Hz**로 연결한다. Actor/critic MLP는 1024×2이며 force loop와 impedance adaptation이 빠른 접촉 대응을 맡는다. 그러나 simulation actor의 전체 observation 차원·측정 wrench-history 입력 여부는 충분히 명시하지 않는다. [§IV-B, V-B]

실물은 **학습 RL이 아닌 expert high-level policy**다. 20 Hz 관측에 pose·recent external-wrench measurements·wipe centroid가 포함되고, 1 kHz controller는 robot state와 추정 external wrench를 사용한다. Recent measurements의 길이·추정기·필터는 미명시다. 따라서 ‘RL이 F/T history를 받아 실물 전이했다’고 소개하면 안 된다. [§V-A]

**저자 Limitation:** 적응 파라미터 수동 tuning, 잘못된 값의 성능 악화, 반응적인 적응. **Future Work:** 적응 파라미터와 high-level policy 동시 학습, policy의 적응 개입. [§VI]

**프로젝트 해석:** Sensor actor 입력을 바꾸는 실험과 force action/controller를 바꾸는 실험을 분리하는 참고다. 실물 Blind learned-RL Sweeping의 근거로 세지 않는다.

## 6. 반대 근거: Binary가 항상 충분하지는 않다

### C1. Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation

**Jiahe Pan, Stelian Coros, Jitendra Malik, Toru Lin. arXiv preprint, 2026.** [원문 v1](https://arxiv.org/html/2605.28812v1) · [저자 프로젝트](https://mpan31415.github.io/tactile_rep/)

Allegro–XELA uSkin의 blind insertion·ball balancing에서 binary와 **힘 벡터+접촉 중심(CoP)** 등을 비교한다. Asymmetric PPO actor는 proprioception·접촉 표현을, critic은 object GT를 추가 사용한다. GRU와 MLP를 거쳐 관절 목표 증분을 출력한다. [Appendix D–E, PDF pp.14–18]

실물 삽입 6형상×각 10회 성공률은 binary **53%**, CoP **78%**; OOD 초기조건은 **20%**, **63%**였다. 반대로 40% taxel masking에서는 binary **53→52%**, CoP **78→62%**로 상세 표현이 누락에 더 민감했다. [§4.1, Table 1, p.6]

**저자 Limitation:** shear simulation 불일치로 simulation과 실물 모두 normal 성분만 사용한다. Simulation의 target-contact와 실물의 모든 접촉 반응도 다르다. **Future Work:** arm–hand·sensor coverage·다른 센서, IL·실물 RL로 확장. [§3.4, §6, p.8]

**프로젝트 해석:** 이 연구는 과업별 정보 손실을 비교해야 한다는 반대 근거다. 삽입·in-hand를 Sweeping의 필수 과업으로 확대하지 않는다. Inspire의 scalar 영역값에서 같은 CoP가 복원된다는 뜻도 아니다. 공개 정책 코드 링크는 확인하지 못했으며 결과 재현은 수행하지 않았다.

## 7. 두 질문에 대한 종합

### 7.1 Binary tactile의 효용과 후처리

| 질문 | 확인한 답 | 근거·한계 |
| --- | --- | --- |
| 저항식 센서에 실제로 쓰였나? | FSR 전압을 영역별 contact bits로 변환 | B1, B3 |
| 구체적인 처리 순서는? | B1은 125 Hz 측정→LPF→threshold. B3은 voltage threshold와 binary sim mapping | 실물 threshold·LPF 계수는 미명시 |
| 왜 sim-to-real에 유리할 수 있나? | 정확한 force amplitude 매칭 부담을 줄임 | B3 실물 비교가 지지. 물체별 예외 존재 |
| 무엇을 버리나? | 영역 내부 접촉 중심·하중 크기 등 | C1은 상세 표현이 유리한 실제 반례 |
| bits만 넣으면 RL이 쓰나? | 항상 그렇지 않음; history/representation 설계가 중요 | B4의 sim 결과이며 real 증명 아님 |
| pushing에 쓸 수 있나? | Binary 관측으로 실물 pushing을 닫힌루프로 수행한 사례 있음 | B2, 그러나 model-based POMDP·known geometry |

Binary는 **힘값의 정밀 보정 문제를 접촉 검출과 coverage 문제로 바꾸는 선택**으로 보는 것이 적절하다. 신호가 약해 threshold를 넘지 못하거나 비센서 부위에서 접촉하면 정보가 없다. 반면 잘 구분되는 접촉 분포만으로 필요한 행동을 선택할 수 있는 과업에서는 단순 표현이 유리할 수 있다. 이 문단은 위 논문들을 종합한 해석이다.

### 7.2 F/T·wrench를 RL에 녹이는 네 경로

| 경로 | 확인 사례 | Sweeping에서 따로 결정할 것 |
| --- | --- | --- |
| 수치 관측 concat | W1 force3, W2 wrench6, W3 F/T 포함 관측 | 좌표계·보정·정규화·센서 유효성 |
| 보상·cost·종료 | W1 목표 힘 오차, W2 force violation, W3 force/contact reward | 힘 회피가 물체 진행을 방해하지 않는가? |
| motion+순응성 action | W1 pose+stiffness+damping, W2 displacement+stiffness | 센서 비교와 action-space 비교를 분리할 것 |
| 원하는 wrench+빠른 제어 | W4 desired wrench action과 force loop | 측정 wrench의 actor 사용 여부와 분리할 것 |

확인한 핵심 F/T 사례를 ‘wrench history→RNN latent’로 일괄 요약할 수는 없다. W1·W2는 저차원 수치 입력이 명확하고, W3는 history·architecture를 충분히 밝히지 않는다. W4의 recent wrench는 실물 expert 경로다. **문헌에 없는 encoder·window length를 채워 넣지 않는 것**이 이번 조사에서 중요하다.

## 8. 프로젝트에서 검증할 안 — PROPOSED

가장 먼저 비교할 안은 **연속 6D wrist wrench+영역별 binary tactile**이다. Wrench는 부하 크기·방향을 보존하고 tactile은 접촉 분포를 보완하도록 한다. 이 조합의 우월성은 아직 검증되지 않았다.

동일 초기 정보·controller·훈련 조건에서 접촉센서 없는 proprioception, binary-only, continuous-tactile-only, wrench-only, wrench+binary, wrench+continuous를 비교한다. 접촉 threshold·coverage·지연을 변화시키고 물체 변위, 접촉 손실, 하중, 전도, 수행시간을 평가한다. 필요하면 같은 조건에 history만 추가한다.

Binary 후처리의 hysteresis·debounce, wrench의 하중 보정·프레임 변환·정규화, actor/critic 정보 계약과 실험표는 [별도 설계 노트](2026-09-16_binary-tactile-wrench-design-notes.md)에 구체적으로 정리했다. **이 설계 노트의 추가 절차를 논문의 원래 구현으로 인용하지 않는다.**

## 9. 신규 검색에서 제외·보류한 연구

기존 논문은 §2.2에 따라 이미 제외했다. 다음은 검색 중 새로 발견했지만 질문의 직접 근거로 채택하지 않은 사례다.

| 연구 | 판단 |
| --- | --- |
| [Variable Impedance Control in End-Effector Space, 2019](https://arxiv.org/pdf/1906.08880) | §V-C에서 실물 direct force sensing을 쓰지 않는다고 명시. Actor의 RGB+EEF 상태, wiped-state binary를 F/T actor나 binary tactile로 분류하지 않음 |
| [Robotic Table Wiping via RL and Whole-body Trajectory Optimization, 2022](https://arxiv.org/abs/2210.10865) | RL은 영상 mask 기반 waypoint 결정. F/T actor 근거 없고 Blind 조건이 아님 |
| [Adaptive Wiping, 2025](https://arxiv.org/abs/2505.06451) | F/T time-series 표현은 관련 있지만 imitation learning. F/T–RL 신규 핵심 목록 제외 |
| [Learning Force Control, 2020](https://arxiv.org/abs/2003.00628) | F/T+SAC이나 고정밀 assembly 중심. 이번에는 지속 접촉 사례를 우선함 |
| [TACTFUL, 2026](https://arxiv.org/html/2606.24712v1) | UR10e+Inspire·저항식 taxel·Blind 실물 RL로 장비는 가깝지만 continuous tactile와 geometry reconstruction 중심. Binary/F/T 방법 근거로는 제외 |
| [Learning contact-rich whole-body manipulation with example-guided RL, 2025](https://doi.org/10.1126/scirobotics.ads6790) | 저자 [공개 자료](https://datadryad.org/dataset/doi:10.5061/dryad.ncjsxkt80)에 binary-contact 관측 옵션과 Blind whole-body 조작을 확인했으나 출판사 전체 원문 접근 실패. 정확한 threshold·학습조건·저자 한계/향후 연구를 검증하지 못해 상세 선정 보류 |

## 10. 검증 범위와 읽기 순서

**우선 읽기:** B1 DexTouch → W1 CHEQ → W2 SRL-VIC → B2 Koval. 이후 B3의 binary/continuous 비교와 C1의 반대 근거를 함께 읽고, 보상 문제가 생길 때 W3, 표현 활용 문제가 생길 때 B4를 참조한다. W4는 controller/action 설계 참고다.

확인한 공개 버전의 원문·방법·실험·저자 한계/향후 연구를 근거 위치와 연결했다. PDF 원문은 공개 저장소에 복제하지 않는다. 로컬로 확보한 주요 PDF의 SHA256은 다음과 같다.

| 자료 | 확인 파일 해시 |
| --- | --- |
| DexTouch | `55591bc4c907d18eb0d811aab845c477ad30b44265af6de0f3e56bf901935058` |
| Rotating without Seeing | `7be48b3f9573efaf8d53b2abf94f23ae16532d6afa2408bc803bc14d4286a5ba` |
| Enhancing Tactile-based RL | `e51421f53cd0d4b333b05f64adf74fc0f7a52e8ee48c4bbc1c07276a1d0573b2` |
| Beyond Binary | `f022d8c38412db7bbb55839a936b1a11caa9af4fbf4c3b0ffd701da60731e508` |

본 보고서는 신규 문헌을 두 질문에 맞춰 비교한 조사본이다. 첨부 출판본 전체를 대상으로 기존 `papers/` 형식의 개별 정독 노트를 새로 작성한 작업, 코드 재현, 실제 장비 성능 검증과는 구분한다.
