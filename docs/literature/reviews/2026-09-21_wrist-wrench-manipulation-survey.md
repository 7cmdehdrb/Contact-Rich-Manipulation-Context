# 손목 Wrench를 관측·피드백으로 사용하는 Manipulation 연구 조사

[문헌 색인](../README.md) · [조사 그룹](README.md) · [전체 논문](../papers/README.md) · [발표 설계 2.3절](../../presentation/02_Tactile_Representation_and_Policy_Design.md#23-본-연구에서-ft를-추가하는-이유와-한계)

후속 상세 리뷰: [W1 · FoAR](../papers/2025-he-foar.md) · [W4 · Zero-Shot Transfer](../papers/2023-brahmbhatt-zero-shot-haptics-insertion.md) · [W7 · FORGE](../papers/2025-noseworthy-forge.md) · [C1 · Self-Tuning Planner](../papers/2022-kato-self-tuning-haptic-exploration.md) · [연결 문헌 · Lee 2019](../papers/2019-lee-making-sense-vision-touch.md)

- **조사일:** 2026-09-21
- **대상:** `docs/presentation/02_Tactile_Representation_and_Policy_Design.md` §2.3 보강
- **성격:** 원문 기반 비교 조사 및 본문 반영 제안. 개별 논문의 전체 정독 노트나 구현 검증 보고서는 아니다.
- **추가 조사:** 2022년 이후 정식 출판물 중 RL 학습·실행 경로에 F/T 정보를 넣은 사례

## 1. 조사 범위와 선정 기준

[프로젝트 저장소](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context)의 `AGENTS.md`, 문서 형식 규칙, 인계 요약, 결정·미정 항목, 다음 행동, 발표 문서 및 상세 논문 색인을 확인했다. 연구 대상은 초기 시각 정보 이후 연속적인 물체 시각 추적 없이 수행하는 Blind Sweeping 하위 정책이며, 계획 플랫폼은 UR5e–손목 6축 F/T–Inspire Hand다.

이번 질문의 Wrist는 손목 자세나 손목 카메라가 아닌 **손목/말단에 작용하는 힘·모멘트**로 해석했다. 외부 F/T 센서, 로봇 내장 F/T 센서, 관절 토크에서 추정한 말단 외력을 구분한다. 촉각 센서의 기능이나 기여도는 조사 범위에서 제외했다. 복합 센서 논문도 Wrench를 사용하는 분기만 검토했다.

앞선 1차 조사에서는 **2022년 이후 정식 출판된 RA-L, ICRA, IROS, RSS 논문**을 선정했다. SCIE는 저널 색인 분류이므로 학회 논문을 SCIE 논문으로 표현하지 않는다. arXiv는 원문 접근 경로로 사용하고, 정식 출판 여부는 출판사·학회 proceedings·저자 공식 출판 기록으로 별도 확인했다. §6의 RL 후속 조사는 같은 연도·정식 출판 원칙을 유지하면서 Autonomous Robots와 CoRL까지 범위를 넓혔다.

[상세 리뷰 색인](../papers/README.md)의 조사 착수 시점 기존 28편은 제외했다. 특히 Force Push, Pushing in the Dark, Visuo-Force-Tactile Door Opening, Learning Force Control 및 Haninger의 compliant contact primitives를 새 레퍼런스로 재사용하지 않았다. 아래 9편은 조사 착수 시 해당 폴더에 상세 리뷰가 없었다. 이후 사용자가 원문을 제공한 [W1 FoAR](../papers/2025-he-foar.md), [W4 Zero-Shot Transfer](../papers/2023-brahmbhatt-zero-shot-haptics-insertion.md), [W7 FORGE](../papers/2025-noseworthy-forge.md), [C1 Self-Tuning Planner](../papers/2022-kato-self-tuning-haptic-exploration.md)의 상세 노트를 후속으로 추가했다. **SRL-VIC는 기존 조사 목록에서 언급된 후보를 원문으로 재확인한 사례**이며, 완전히 새로 발견한 논문으로 취급하지 않는다. [Lee et al., ICRA 2019](../papers/2019-lee-making-sense-vision-touch.md)은 연도 조건 때문에 이 9편이나 §6의 8편에 포함하지 않고, W5의 Reference [19]에서 확장한 연결 선행문헌으로 §7에 별도 기록한다.

## 2. 핵심 비교표

W1–W7은 측정·추정 힘이 학습 정책의 실행 관측에 들어가는 사례다. C1–C2는 제어기·플래너의 피드백으로 사용하는 보조 사례다. `6D`는 힘 3축과 모멘트 3축, `3D`는 힘 3축만 의미한다.

| ID | 논문·정식 출판 | 신호 출처 / 실제 사용 성분 | 입력과 사용 방식 | 태스크·실행 중 시각 조건 |
| --- | --- | --- | --- | --- |
| W1 | [**FoAR**](../papers/2025-he-foar.md), RA-L 2025 | 외장 OptoForce / 6D | Wrench 이력의 Transformer 표현 → 시각 특징과 결합 → Diffusion Policy; 반응형 동작 보정에도 사용 | Wiping·peeling·chopping / 시각 사용 |
| W2 | **Comp-ACT**, IROS 2024 | UR5e 내장 손목 F/T / 6D | 현재 Wrench + EE pose + 영상 → ACT → 자세·그리퍼·강성 | 삽입·닦기·그리기 / 시각 사용 |
| W3 | **Reactive Diffusion Policy — Force 분기**, RSS 2025 | Flexiv 관절 토크 기반 TCP 추정값 / 6D | 실시간 Wrench → 빠른 GRU 행동 분기; 느린 시각 정책과 결합 | Peeling·wiping·양팔 lifting / 시각 사용 |
| W4 | [**Zero-Shot Transfer of Haptics-Based Object Insertion Policies**](../papers/2023-brahmbhatt-zero-shot-haptics-insertion.md), ICRA 2023 | Franka 제공 말단 외력 추정값 / 6D | 상대 EE pose + Wrench의 8시점 이력 → SAC residual motion | 접시·컵 삽입 / 초기 시각 이후 추적 없음 |
| W5 | **Symmetry-aware RL … with a Soft Wrist**, ICRA 2024 | UR5e의 F/T 센서, soft wrist 상부 / 6D | Arm-tip 위치 + Wrench 및 행동 이력 → recurrent SAC | Peg-in-hole / 정책에 영상 없음; hole 좌표계는 알려짐 |
| W6 | **SRL-VIC**, RA-L 2024 | F/T 입력 명시; 실기 센서 구현 불명확 / 6D | Wrench + EE 위치 → task actor; Wrench → safety/recovery | Blind maze·장애물 밀기 / 시각 없음 |
| W7 | [**FORGE**](../papers/2025-noseworthy-forge.md), RA-L 2025 | Franka 관절 토크 기반 추정 / **3D force** | 힘 + EE 상태 + 부품 pose 추정 + 허용 힘 → recurrent PPO | 삽입·너트 체결 / 부품 pose 추정 사용 |
| C1 | [**A Self-Tuning Impedance-Based Interaction Planner …**](../papers/2022-kato-self-tuning-haptic-exploration.md), RA-L 2022 | Franka 내부 관절 토크 기반 외력 추정 / 평면 힘 중심 | 힘·운동 이력 → 탐색/반동 전환 → 경로·임피던스; 비학습 방법 | Blind maze / 시각 없음 |
| C2 | **Rotating Objects via In-Hand Pivoting …**, IROS 2023 | 외장 Robotiq FT-300 / **수직 Fz** | 측정 Fz와 모델 기대값의 오차 → PI 경로 보정 | 바닥 지지 pivoting / 시각 사용 |

각 행의 서지·원문 근거와 해당 절은 아래 항목에 연결했다. 실행 관측의 일부를 요약한 표이며, 학습용 privileged state나 성공 판정 센서를 actor 입력으로 합쳐 적지 않았다.

## 3. 정책 관측으로 사용하는 핵심 7편

### W1. [FoAR — 외장 손목 센서와 Wrench 이력](../papers/2025-he-foar.md)

**He, Z., et al. “FoAR: Force-Aware Reactive Policy for Contact-Rich Robotic Manipulation.” IEEE Robotics and Automation Letters, 10(6), 5625–5632, 2025.** [상세 노트](../papers/2025-he-foar.md) · [DOI](https://doi.org/10.1109/LRA.2025.3560871) · [저자 출판 기록](https://github.com/Alan-Heoooh/FoAR) · [원문](https://arxiv.org/html/2411.15753v2)

- **센서 → 정책:** Flexiv Rizon의 flange–gripper 사이에 OptoForce를 추가했다. 100 Hz의 200개 Wrench 표본, 약 2초 이력을 인코딩하고 시각 특징과 결합한다. Future contact probability가 높고 현재 힘·모멘트가 threshold보다 작을 때 예측 action의 진행 방향으로 위치 명령을 보정한다. 근거: §III-A–C, §IV-A.
- **검증:** 실제 wiping·peeling·chopping. Table I의 wiping 품질 점수는 RISE 0.500, FoAR 0.875다. 성공률이 아니며, 구조와 보정기도 달라 순수한 센서 추가 효과로 해석할 수 없다.
- **저자 Limitation:** 정적인 F/T 임계값과 단순 위치 제어의 제약. 근거: §V.
- **저자 Future Work:** 순응·하이브리드 제어 및 더 다양한 로봇 형태로 확장. 근거: §V.
- **본 조사 해석:** 외장 손목 F/T를 장착하고 시간 이력을 정책에 넣은 사례로 우선 인용할 만하다. 연속 시각을 사용하므로 Blind Sweeping의 직접 검증은 아니다.

### W2. Comp-ACT — F/T 관측의 포함·제거 비교

**Kamijo, T., Beltran-Hernandez, C. C., and Hamaya, M. “Learning Variable Compliance Control From a Few Demonstrations for Bimanual Robot with Haptic Feedback Teleoperation System.” IROS, 12663–12670, 2024.** [DOI](https://doi.org/10.1109/IROS58592.2024.10801731) · [저자 프로젝트](https://omron-sinicx.github.io/CompACT/) · [원문](https://arxiv.org/html/2406.14990v2)

- **센서 → 정책:** UR5e 내장 6축 F/T와 현재 EE pose·여러 카메라 영상을 ACT에 입력하여 자세·그리퍼·강성을 출력한다. 여러 카메라 시점이나 미래 action chunk를 과거 관측 이력으로 혼동하면 안 된다. 근거: §IV-A, §V-A.
- **검증:** 실물 Table II의 성공률은 F/T 포함/제거 순서로 picking-insertion **70/35%**, 원통 삽입 **100/40%**, 직육면체 삽입 **70/50%**, wiping **70/100%**, drawing **100/100%**다. 근거: §VI-B, PDF p.7.
- **저자 Limitation:** 작업별 compliance mode 사전 지정, stiffness에 한정된 학습, 작업별 정책의 일반화 제약. 근거: §VII.
- **저자 Future Work:** 의도 기반 compliance 추정, 다른 제어 파라미터와 multitask 학습. 근거: §VII.
- **본 조사 해석:** §2.3의 센서 기여 논의에 가장 직접적이다. 다만 제거한 것은 **정책의 F/T 관측**이며, 하위 순응제어기의 힘 피드백까지 제거한 비교가 아니다. 효과가 작업에 따라 달라진다.

### W3. Reactive Diffusion Policy — 관절 토크 기반 Wrench와 빠른 반응

**Xue, H., et al. “Reactive Diffusion Policy: Slow-Fast Visual-Tactile Policy Learning for Contact-Rich Manipulation.” Robotics: Science and Systems, 2025.** [공식 proceedings](https://www.roboticsproceedings.org/rss21/p052.html) · [DOI](https://doi.org/10.15607/RSS.2025.XXI.052) · [원문](https://arxiv.org/html/2503.02881v3)

- **검토 대상:** 제목의 tactile 전체가 아니라 **RDP (Force)** 분기다. Flexiv Rizon 4의 관절 토크에서 RDK가 추정한 TCP 6D Wrench를 사용한다. 외장 F/T 센서 사례가 아니다. 근거: §V-A1.
- **센서 → 정책:** 느린 시각 정책과 빠른 GRU 분기를 결합하여 action chunk 실행 중에도 Wrench로 행동을 갱신한다. 빠른 분기는 실험에서 24 Hz이며 센서 수집·로봇 제어 주기와 다르다. 근거: §IV, Appendix F.
- **검증:** Peeling 점수는 전체 Wrench **0.95**, normal force만 남기면 **0.48**이다. 성공률이 아니다. 이 비교만으로 모멘트의 독립 기여를 분리할 수는 없다. 근거: Appendix G, Table VI.
- **저자 Limitation:** 단일 작업 학습, 두 손가락 시스템, 빠른 분기에 고주파 시각 입력이 없음. 근거: §VI.
- **저자 Future Work:** 지연 감소, dexterous hand와 빠른 시각 반응으로 확장. 근거: §VI.
- **본 조사 해석:** 힘의 크기 하나로 축약하기보다 여러 방향의 반응을 활용할 근거다. Blind 조건의 검증은 아니다.

<a id="w4"></a>

### W4. [Zero-Shot Transfer — 초기 시각 이후 Wrench·고유감각 이력](../papers/2023-brahmbhatt-zero-shot-haptics-insertion.md)

**Brahmbhatt, S., Deka, A., Spielberg, A., and Müller, M. “Zero-Shot Transfer of Haptics-Based Object Insertion Policies.” ICRA, 3940–3947, 2023.** [상세 노트](../papers/2023-brahmbhatt-zero-shot-haptics-insertion.md) · [IEEE 출판 기록](https://ieeexplore.ieee.org/document/10160346/) · [논문](https://arxiv.org/pdf/2301.12587)

- **센서 → 정책:** Franka가 제공하는 추정 말단 6D Wrench와 목표 대비 EE pose의 **8시점 이력**을 SAC에 넣는다. 정책은 residual motion을 출력한다. 초기 목표를 시각으로 정한 뒤 실행 중 object tracking을 사용하지 않는다. 근거: §III, PDF pp.3–4.
- **출처 재확인:** 저자 구현은 `O_F_ext_hat_K`를 관측으로 전달한다. [저자 제어 코드](https://github.com/isl-org/0shot-object-insertion/blob/e916d29e815b46e2f54636d46fff8a92cc698f22/ros_controllers/src/tf_policy_controller.cpp#L241-L247) · [이력 구성 코드](https://github.com/isl-org/0shot-object-insertion/blob/e916d29e815b46e2f54636d46fff8a92cc698f22/ros_controllers/nodes/tf_policy_actionserver_base.py#L99-L129) · [Franka의 추정 Wrench 정의](https://github.com/frankaemika/libfranka/blob/0.9.0/include/franka/robot_state.h#L302-L310). 별도 장착 F/T로 분류하지 않는다.
- **검증:** 접시를 랙에 삽입하고 막힌 슬롯에서 빈 슬롯으로 이동한다. 실물 성공률 **83.3±13.6%**. 이력 제거의 성능 저하를 보이지만 Wrench 제거 실험은 아니다. 근거: Table II, Fig.8.
- **저자 Limitation:** 큰 초기 수평 오차와 일부 base joint 자세에서 실패; OSC 관성 모델 오차 가능성을 논의한다. 근거: §IV, PDF p.6.
- **저자 Future Work:** 이동형 매니퓰레이터와 통합. 근거: §V, PDF p.6.
- **본 조사 해석:** 현재 프로젝트의 초기 시각 이후 제한 관측 조건과 가장 가깝다. 다만 물체를 잡은 삽입 작업이다.

<a id="w5"></a>

### W5. Symmetry-aware RL — F/T·행동 이력의 recurrent policy

**Nguyen, H., Kozuno, T., Beltran-Hernandez, C. C., and Hamaya, M. “Symmetry-aware Reinforcement Learning for Robotic Assembly under Partial Observability with a Soft Wrist.” ICRA, 9369–9375, 2024.** [DOI](https://doi.org/10.1109/ICRA57147.2024.10610103) · [원문](https://arxiv.org/html/2402.18002v2)

- **센서 → 정책:** UR5e에서 soft wrist 앞의 F/T 센서로 6D Wrench를 얻는다. Arm-tip 위치와 Wrench, 행동 이력을 RNN으로 처리하는 SAC가 xyz 변위를 출력한다. 별도 외장 센서 모델을 추가했다고 단정하지 않는다. 근거: §IV Eq.(1), §V-B, §VII-A.
- **검증:** 시각 없는 정책이 작은 진동·미끄러짐으로 구멍을 찾는다. 실물 round→square 전이는 1 mm clearance에서 20/20, 더 좁은 50 μm round 조건은 9/20이다. 근거: §VIII. 시뮬레이션 memoryless 비교는 F/T 제거 비교가 아니다.
- **저자 Limitation:** 최적 성능에 거의 완전한 대칭성이 필요하다. 근거: §IX.
- **저자 Future Work:** 불완전한 대칭을 활용하는 연구의 적용 가능성을 논의한다. 별도의 구체적 실행 계획은 미명시다. 근거: §IX.
- **본 조사 해석:** 힘·모멘트를 명령과 운동의 시간적 맥락에서 사용하는 근거다. Hole 좌표계와 yaw 정렬 가정이 있으므로 미지 물체 pose 복원 사례로 확대하지 않는다.
- **연결 선행문헌:** W5는 vision·F/T·proprioception의 self-supervised 표현 위에서 TRPO insertion policy를 학습한 [Lee et al., ICRA 2019](../papers/2019-lee-making-sense-vision-touch.md)을 Reference [19]로 인용한다. 이 문헌은 2022년 이후 선별 대상은 아니므로 W5와 별도 ID의 정식 후보로 세지 않고 [§7](#ref-w5-19-lee-2019)에 연결한다.

### W6. SRL-VIC — Wrench로 이동량·강성·복구 행동 선택

**Zhang, H., Solak, G., Lahr, G. J. G., and Ajoudani, A. “SRL-VIC: A Variable Stiffness-Based Safe Reinforcement Learning for Contact-Rich Robotic Tasks.” IEEE Robotics and Automation Letters, 9(6), 5631–5638, 2024.** [DOI](https://doi.org/10.1109/LRA.2024.3396368) · [원문](https://arxiv.org/html/2406.13744v1)

- **센서 → 정책:** Task actor에 Wrench 6D + EE 위치 3D를 입력하고, safety critic/recovery actor는 Wrench를 사용한다. 출력은 평면 이동량과 강성이다. 근거: §III-B, PDF pp.3–4.
- **센서 확인 범위:** 논문은 F/T sensor라고 표현하지만 실물 센서 브랜드 및 외장 센서/관절 추정 여부가 명확하지 않다. 따라서 **외장 손목 센서 장착 근거로는 사용하지 않는다.**
- **검증:** 시각 없이 미로를 탐색하며 볼트 더미를 민다. 관측 노이즈를 추가해 재학습한 실물 실험에서 6/6 성공했다. 작은 표본이며 자유 물체 Sweeping과 동일하지 않다. 근거: §IV-C. 강성·복구 ablation이 있고 Wrench 제거 비교는 없다.
- **저자 Limitation:** 학습과 다른 미로 형태에서는 안전 제약을 지켰지만 출구 탐색에 실패했다. 근거: §IV-C, PDF p.8.
- **저자 Future Work:** 더 일반적인 태스크와 model-based RL로 확장. 근거: §V.
- **본 조사 해석:** Wrench의 정책 입력 사례로 적합하다. 관측 이력의 기여를 입증한 논문으로는 분류하지 않는다.

<a id="w7"></a>

### W7. [FORGE — 6D Wrench가 아닌 3D force 관측](../papers/2025-noseworthy-forge.md)

**Noseworthy, M., et al. “FORGE: Force-Guided Exploration for Robust Contact-Rich Manipulation Under Uncertainty.” IEEE Robotics and Automation Letters, 2025.** [상세 노트](../papers/2025-noseworthy-forge.md) · [IEEE 출판 기록](https://ieeexplore.ieee.org/document/10925874/) · [저자 연구실의 출판 확인](https://research.nvidia.com/labs/srl/publication/noseworthy-2025-forge/) · [원문](https://arxiv.org/html/2408.04587v2)

- **센서 → 정책:** Franka 관절 토크 기반 추정값 중 **EE 좌표계 3D force**를 사용한다. EE 상태, 부품 pose 추정, 허용 힘과 함께 recurrent PPO에 입력하여 pose target과 성공 예측을 출력한다. 근거: §II-B, §III–IV.
- **검증:** 실물 M16 너트 체결은 69%, No Force는 40%; peg 삽입은 84/82%다. 효과 크기가 작업별로 다르다. 근거: Table I. 힘 제한 대응·성공 종료 판정도 분석한다: §V-C/D.
- **저자 Limitation:** 큰 pose 오차에서 실패가 증가하고, 큰 학습 pose 노이즈에서는 학습이 불안정하다. 근거: §V-A/B.
- **저자 Future Work:** Torque sensing 및 real-to-sim 모델 조정. 근거: §VII. 따라서 모멘트까지 이미 사용한 사례로 쓰면 안 된다.
- **본 조사 해석:** 관절 토크 기반 말단 힘의 정책 활용 근거다. 부품 pose 정보와 고정된 조립 환경을 사용하므로 일반적인 Blind Sweeping과 구분한다.

## 4. 외력 피드백을 사용하는 보조 2편

<a id="c1"></a>

### C1. [Self-Tuning Interaction Planner — 추정 외력으로 Blind 탐색](../papers/2022-kato-self-tuning-haptic-exploration.md)

**Kato, Y., et al. “A Self-Tuning Impedance-Based Interaction Planner for Robotic Haptic Exploration.” IEEE Robotics and Automation Letters, 7(4), 9461–9468, 2022.** [상세 노트](../papers/2022-kato-self-tuning-haptic-exploration.md) · [DOI](https://doi.org/10.1109/LRA.2022.3190806) · [원문](https://arxiv.org/html/2203.05413v2)

- **센서 → 알고리즘:** Franka 내부 관절 토크로 추정한 외력과 실제 pose를 사용한다. Exploration은 힘이 5 N·7 N에 도달한 두 시점의 실제 위치 차이로 다음 진행 방향을 정한다. 500 ms 동안 실제 변위가 1 mm 미만이면 Bouncing으로 전환하여 외력 방향과 2000-step 운동 추세에서 축별 이동량을 만든다. 계획된 진행 방향에 강성 주축을 맞춰 경로 추종과 횡방향 순응성을 함께 확보한다. 근거: §II-B, §III-A/B, Algorithms 1–2, §IV-B, PDF pp.2–5.
- **검증:** 같은 planner에 high·low·self-tuning impedance를 적용했다. 기본 미로의 평균 힘은 각각 약 23·18·11 N, 최대 추종 오차는 약 0.04·0.10·0.04 m였다. 나사를 추가한 미로에서는 self-tuning만 통과하고 high·low는 큰 힘으로 중단했다. 반복 trial 성공률이나 F/T 제거 ablation은 아니다. 근거: §IV-B, Fig. 6–7, PDF pp.5–6.
- **저자 Limitation:** 힘 임계값의 수동 조정, 강체 환경에 한정. 근거: §V.
- **저자 Future Work:** 3D maze와 시각이 제한된 동물의 haptic navigation 원리 적용. 근거: §V.
- **본 조사 해석:** 외력과 운동 이력을 연결하는 비학습 제어·계획 사례다. 외장 손목 F/T 장착, 학습 정책의 observation이나 학습된 이력 표현의 증거는 아니며, §6의 RL 후보에도 포함하지 않는다. 원문의 차원 표기·threshold 집계·제어 주기 등 재현상의 미명시는 상세 노트에서 구분했다.

### C2. In-Hand Pivoting — 외장 F/T를 수직 경로 보정에 사용

**Xu, S., et al. “Rotating Objects via In-Hand Pivoting Using Vision, Force and Touch.” IROS, 2023.** [DOI](https://doi.org/10.1109/IROS55552.2023.10341505) · [원문](https://arxiv.org/pdf/2303.10865)

- **센서 → 알고리즘:** UR5 손목에 **Robotiq FT-300**을 장착한다. 수직 힘 Fz와 질량·형상·현재 회전각 기반 기대 Fz의 오차로 PI 제어기가 EE 수직 경로를 보정한다. 근거: §III-B, §IV-A, PDF pp.3–5.
- **검토 범위:** 이 논문의 다른 센서는 이번 조사에서 다루지 않는다. 6축 센서를 장착했지만 여기서 확인한 제어 입력은 Fz 한 성분이다.
- **저자 Limitation:** 느린 실행, cuboid와 fiducial marker 조건. 근거: §VI, PDF p.8.
- **저자 Future Work:** Joint velocity control, marker 제거, 다양한 shape 및 force/gripper control 학습화. 근거: §VI.
- **본 조사 해석:** 외장 F/T 추가 사례로는 명확하다. 현재 물체 각도를 시각으로 얻는 모델 기반 제어이며, Wrench를 학습 정책에 입력한 사례는 아니다.

## 5. §2.3에 반영할 핵심과 근거 수준

### 5.1. 우선 인용할 논문

| 뒷받침할 주장 | 우선 근거 | 주장할 수 있는 범위 |
| --- | --- | --- |
| 외장 손목 F/T를 학습 정책 입력으로 사용할 수 있다 | W1 FoAR | 실제 장착과 Wrench 이력 입력 확인 |
| 정책의 F/T 관측이 행동 선택에 기여할 수 있다 | W2 Comp-ACT | 관측 포함·제거 비교; 작업별 개선·악화 모두 존재 |
| 초기 시각 이후 제한 관측으로 접촉 조작이 가능하다 | W4 Zero-Shot Transfer | 초기 목표 정보와 Wrench·고유감각 이력을 사용한 삽입 |
| Wrench는 관측·행동 이력과 함께 사용할 수 있다 | W5 Symmetry-aware RL | Recurrent policy의 명시적 관측·행동 이력 |
| 한 방향 힘으로 축약하면 필요한 정보가 사라질 수 있다 | W3 RDP (Force) | 해당 peeling 설정의 full/normal-only 비교; 모멘트 단독 효과는 미분리 |
| 추정 외력도 정책·제어에 활용된다 | W3·W4·W7, C1 | 외장 F/T와 추정 Wrench를 구분한 사례 |

### 5.2. 본문에 넣을 수 있는 문안 — PROPOSED

> 손목 Wrench를 접촉 조작 정책의 관측으로 사용하는 선행 사례가 존재한다. FoAR는 외장 F/T 센서의 시간 이력을 시각 특징과 결합하고, Zero-Shot Transfer는 초기 시각 정보 이후 말단 pose와 Wrench 이력으로 삽입 행동을 선택한다. Symmetry-aware RL 역시 F/T·고유감각·행동 이력을 이용한 부분 관측 정책을 학습한다. 따라서 본 연구에서 Wrench를 행동과 로봇 운동 이후 나타나는 하중 반응으로 활용하는 설계에는 선행 근거가 있다. [W1](../papers/2025-he-foar.md), [W4](../papers/2023-brahmbhatt-zero-shot-haptics-insertion.md), [W5](https://arxiv.org/html/2402.18002v2)
>
> 다만 F/T 관측의 기여는 작업과 제어 구조에 따라 달라진다. Comp-ACT의 관측 포함·제거 비교에서, F/T를 포함한 정책은 삽입 성공률이 높고 wiping 성공률이 낮았다. 본 연구에서도 Wrench 추가 효과를 실험으로 확인해야 하며, 기존 결과만으로 자유 물체 Sweeping의 성능 향상이나 접촉 위치·물체 상태의 유일한 복원을 주장하지 않는다. [W2](https://arxiv.org/html/2406.14990v2)

위 문안은 이번 조사에서 확인한 **Wrench 측 근거만** 보강한다. Binary 촉각과의 역할 분담 전체를 직접 비교 검증했다는 뜻은 아니다. 센서 조합의 기여와 현재 프로젝트에서의 적절한 observation 설계는 별도의 검증 대상으로 남는다.

### 5.3. 잘못된 인용을 피하기 위한 구분

- **Wrench 출력 ≠ Wrench 관측.** 예를 들어 [ForceMimic, ICRA 2025](https://forcemimic.github.io/)의 주요 HybridIL은 point cloud·TCP pose에서 pose·Wrench 궤적을 출력한다. 측정 Wrench가 주요 정책 입력인 성공 사례로 분류하면 안 된다. 근거: [원문 §III–IV](https://arxiv.org/html/2410.07554v3).
- **6축 센서 ≠ 6축 모두 사용.** C2는 Fz, W7은 3D force만 사용한다.
- **순수 관측 제거 ≠ 전체 시스템 비교.** W2는 정책 관측 비교이고, W1의 RISE 대비 결과는 구조·보정기 차이를 포함한다.
- **이력 효과 ≠ 센서 단독 효과.** W4·W5의 memory 비교는 Wrench 포함·제거 실험과 다르다.
- **유사 작업의 성공 ≠ Blind Sweeping 검증.** 이번 제외 조건 아래 확보한 연구는 surface tool manipulation, 삽입·조립, 미로 탐색, pivoting이다. 새로운 자유 물체 Sweeping 직접 사례를 확보했다고 주장하지 않는다.

## 6. 추가 조사 — RL 학습에서 F/T 정보를 넣은 사례

### 6.1. 추가 선별 기준

이번 후속 조사에서는 단순히 논문 제목이나 시스템에 force가 등장하는지를 세지 않고 다음 조건을 모두 확인했다.

1. **2022년 이후 정식 출판:** 저널 논문 또는 정식 conference proceedings여야 한다. arXiv 단독 공개본은 제외했다.
2. **RL이 행동 정책을 학습:** F/T로 reward만 계산하거나, 고정 제어기·안전 종료에만 사용하는 사례는 제외했다.
3. **F/T가 학습·실행 정보 경로에 포함:** 측정·추정 force/torque가 actor state에 직접 들어가거나, F/T를 입력받은 estimator/context encoder의 출력이 RL 정책을 조건화해야 한다.
4. **상세 리뷰 제외:** 현재 [`docs/literature/papers`](../papers/README.md)에 상세 노트가 있는 논문은 후보에서 제외했다. 기존 조사표에만 있던 W5·W6은 상세 노트가 없으므로 허용했다.
5. **출판 수준:** 저널은 SCIE급 로보틱스 저널을 대상으로 하고, 학회는 SCIE라는 표현을 쓰지 않은 채 ICRA·IROS·CoRL 같은 정식 주요 proceedings를 대상으로 했다.

이 기준은 **raw F/T가 actor에 직접 들어가는 경우**와 **F/T가 만든 추정상태·잠재상태가 actor를 조건화하는 경우**를 구분한다. 후자를 전자와 같은 센서 배선으로 표현하지 않는다.

### 6.2. 조건을 만족한 8편

| ID | 논문·정식 출판 | RL 방법 | F/T 정보가 들어가는 위치 | 태스크·핵심 제약 |
| --- | --- | --- | --- | --- |
| R1 | **Learning Insertion Primitives with Discrete-Continuous Hybrid Action Space for Robotic Assembly Tasks**, ICRA 2022 ([IEEE](https://ieeexplore.ieee.org/document/9811973/) · [원문](https://arxiv.org/html/2110.12618v1)) | TS-MP-DQN | **직접:** state = 상대 pose + peg velocity + external wrench | Peg/connector insertion; nominal hole pose와 impedance controller 사용 |
| R2 | **Symmetry-aware Reinforcement Learning for Robotic Assembly under Partial Observability with a Soft Wrist**, ICRA 2024 ([IEEE](https://doi.org/10.1109/ICRA57147.2024.10610103) · [원문](https://arxiv.org/html/2402.18002v2)) | Recurrent SAC | **직접:** arm-tip 위치 + 6D F/T + action/observation history | Peg-in-hole; 대칭 형상, 알려진 hole frame과 yaw 정렬 가정 |
| R3 | **SRL-VIC**, RA-L 2024 ([IEEE](https://doi.org/10.1109/LRA.2024.3396368) · [원문](https://arxiv.org/html/2406.13744v1)) | SAC task actor + DDPG recovery | **직접:** task actor는 위치 + 6D F/T, safety/recovery network는 6D F/T | Blind maze; 센서 모델·외장/내장 구현은 불명확 |
| R4 | **Guiding Real-World Reinforcement Learning for In-Contact Manipulation Tasks with Shared Control Templates**, Autonomous Robots 2024 ([출판사 원문](https://doi.org/10.1007/s10514-024-10164-6)) | SAC/TQC + shared-control constraints | **직접:** grid-clamp actor에 clamp 위치 + 3D force | 실물 grid-clamp insertion; 알려진 hole frame·orientation constraint·좁은 탐색 영역 사용 |
| R5 | **Learning Visuotactile Estimation and Control for Non-prehensile Manipulation under Occlusions**, CoRL 2024, PMLR 2025 ([공식 proceedings](https://proceedings.mlr.press/v270/ferrandis25a.html) · [원문](https://arxiv.org/abs/2412.13157)) | Recurrent PPO | **간접:** wrist force + EE pose + 마지막 시각 pose → Bayesian recurrent estimator → 추정 object pose·uncertainty가 actor 입력 | 가려진 cuboid pushing; 고정 object/pusher geometry |
| R6 | **Context-Based Meta Reinforcement Learning for Robust and Adaptable Peg-in-Hole Assembly Tasks**, IROS 2025 ([IEEE](https://ieeexplore.ieee.org/document/11247014/) · [저자 출판 기록](https://www.hrl.uni-bonn.de/publications/2025/shokry2025iros) · [원문](https://arxiv.org/html/2409.16208v3)) | PEARL/SAC meta-RL | **간접:** F/T transition을 alternative context encoder에 넣어 task latent를 만들고 actor를 조건화 | Peg-in-hole; estimated hole pose와 초기 task frame 필요 |
| R7 | **Augmenting Robotic Disassembly Skill: Combining Compliance Control Strategy with Reinforcement Learning for Twist-Pulling Disassembly**, IROS 2025 ([IEEE](https://ieeexplore.ieee.org/document/11246037/)) | DDPG | **직접:** flange force/torque + TCP pose | Twist-pull disassembly; 알려진 축·rigid grasp·5 mm lift primitive 사용 |
| R8 | **SAVR: Scooping Adaptation for Variable Food Properties via Reinforcement Learning**, IROS 2025 ([IEEE](https://ieeexplore.ieee.org/document/11247626/)) | PPO + DMP prior | **직접:** 최근 5 step의 6D F/T + EE pose history + segmented image | Food scooping; 초기 RGB-D 정렬과 고정 DMP 구조 사용 |

R1–R4·R7–R8은 force 또는 wrench가 학습 정책의 명시적 state/observation이다. R5는 force가 먼저 물체 pose와 uncertainty를 추정하는 데 쓰이고 actor는 그 추정 결과를 받는다. R6는 F/T가 actor vector에 직접 concatenate되는 대신 context encoder를 통해 task latent를 만든다. 따라서 **“RL 시스템이 F/T를 사용한다”는 8편 모두에 성립하지만, “raw 6D wrench를 actor에 직접 넣는다”는 R1–R3·R8에만 명확히 성립**한다. R4는 3D force, R7은 force/torque를 쓰지만 전체 component 목록이 불명확하다.

### 6.3. 사례별 원문 근거와 해석

#### R1. ICRA 2022 — 외력 Wrench를 상태와 primitive 종료에 함께 사용

- 원문 §IV-A는 state를 상대 pose, peg velocity, external wrench로 정의한다. RL은 discrete primitive 종류와 continuous 속도·contact-force threshold를 함께 선택한다.
- 실물에서는 FANUC와 F/T sensor·impedance controller를 사용하고, simulation에서 배운 정책을 fine-tuning 없이 전이한다. 실물 30회 평가에서 TS-MP-DQN 성공률은 square/triangle/pentagon 각각 96.7/93.3/93.3%, tight round peg 86.7%, waterproof connector 100%, Ethernet connector 86.7%다.
- **해석 한계:** force-only 정책이 아니다. Nominal hole pose, 상대 pose, primitive 구조와 impedance controller가 함께 문제를 단순화하며, Wrench 제거 ablation은 없다.

#### R2. ICRA 2024 — 6D F/T와 행동 이력을 recurrent SAC에 입력

- 원문 Eq.(1)은 observation을 arm-tip 3D 위치, 3D force, 3D torque로 정의하고, recurrent SAC가 전체 action-observation history를 처리한다고 명시한다.
- 실물 UR5e에서 soft wrist 위 F/T sensor를 사용하며 100개 demonstration으로 약 3시간 내 학습한다.
- **해석 한계:** 성능 향상은 symmetry augmentation·auxiliary loss·memory를 포함한 전체 방법의 결과다. F/T 제거 실험이 아니며, 거의 완전한 형상 대칭과 알려진 hole 좌표계를 이용한다.

#### R3. RA-L 2024 — F/T를 task·safety·recovery 세 경로에 사용

- 원문 §III-B는 safety critic/recovery actor의 state를 6D F/T로, task actor의 state를 6D F/T + EE position으로 정의한다. Task actor는 평면 변위와 stiffness를 함께 출력한다.
- 시각 없는 contact-rich maze에서 simulation-to-real 전이를 수행한다. F/T는 행동 선택뿐 아니라 위험 예측과 복구 정책에도 직접 들어간다.
- **해석 한계:** sensor의 구체 모델과 외장/내장 여부가 원문에서 명확하지 않다. Recovery·variable impedance ablation은 있지만 F/T observation 제거 비교는 없다.

#### R4. Autonomous Robots 2024 — 제한된 state/action space에서 실물 SAC 학습

- Grid-clamp 실험의 actor observation은 hole frame의 clamp 3D 위치와 clamp frame의 3D force다. SAC가 3D action을 내고 Shared Control Template가 phase별 6D EE increment와 안전 constraint로 변환한다.
- 실제 DLR SARA에서 약 75 episode, 17분에 insertion을 학습했다. Force-cost 유무 비교의 두 조건 모두 force observation은 유지하므로 이는 sensor-removal ablation이 아니다.
- **해석 한계:** 알려진 target frame, 고정 orientation, 0.8 cm × 0.8 cm × 10 cm 탐색 영역이 강한 task prior다. 논문은 integrated F/T sensor라고만 하므로 손목 장착 모델을 단정하지 않는다.

#### R5. CoRL 2024 — F/T 기반 상태 추정치를 RL loop에 넣는 간접 사례

- Estimator는 마지막 visual object pose, EE pose, EE force, occlusion flag의 이력으로 현재 object pose와 aleatoric/epistemic uncertainty를 예측한다. 이후 이 estimator를 RL loop에 넣어 uncertainty-aware PPO를 다시 학습한다.
- 실물 KUKA iiwa의 wrist F/T와 onboard camera를 사용한다. Hardware 성공은 자연 가림 19/20, 5초 인위 가림 10/10, 전체 가림 7/10이다.
- **해석 한계:** raw force가 최종 actor에 직접 들어간다고 쓰면 안 된다. Actor는 estimator가 만든 pose·uncertainty를 받고, 별도의 force-removal ablation은 없다.

#### R6. IROS 2025 — F/T transition으로 meta-RL의 task latent를 추정

- PEARL은 observation·action·next observation과 context 값으로 task posterior를 만든다. 저자들은 실물에서 기존 context 대신 F/T reading을 받는 alternative context encoder를 학습하고, 그 posterior latent로 policy를 조건화한다.
- UR5e 내장 F/T를 사용해 16,000개 실물 sample로 sensor adaptation을 수행한다. 논문은 training/in-distribution 실물 task에서 100 adaptation step 이내 100% 성공을 보고한다.
- **해석 한계:** F/T는 raw actor observation이 아니라 context encoder 입력이다. Actor는 peg-to-estimated-hole observation과 latent를 사용하며, actual hole pose 없이도 estimated hole pose와 task frame은 필요하다.

#### R7. IROS 2025 — 추정 flange wrench로 rotation center를 학습

- DDPG state는 flange에서 검출한 force/torque와 TCP pose이고, action은 rotation-center offset이다. Reward도 lateral force와 torsional load를 줄이도록 구성한다.
- Franka의 internal torque sensing으로 flange wrench를 얻으므로 별도 손목 F/T 센서 장착 사례로 세지 않는다.
- **해석 한계:** 알려진 twist/pull 축, rigid grasp, fixed lift step, Cartesian impedance와 axial-force rule이 함께 작동한다. 전체 force/torque component와 history는 원문에서 완전히 열거하지 않았다.

#### R8. IROS 2025 — 6D F/T 이력으로 food interaction에 적응

- PPO actor는 최근 5 step의 EE pose와 6D F/T, spoon/food segmentation, target amount와 DMP index를 받으며 DMP의 z-direction correction을 출력한다.
- 실물에서는 spoon과 xArm 사이의 Sunrise Instruments M3712B 6-axis F/T sensor를 사용한다. 10% target tolerance에서 full SAVR/force-only/segmentation-only의 전체 성공률은 36.11/22.22/2.78%다.
- **해석 한계:** F/T 단독보다 multimodal 입력이 낫다는 근거지만 성공률 자체는 낮다. 초기 RGB-D 정렬, segmentation tracking, DMP motion prior와 terminal amount reward가 함께 필요하다.

### 6.4. 확인했지만 포함하지 않은 경계 사례

| 사례 | 제외 이유 |
| --- | --- |
| [Zero-Shot Transfer](../papers/2023-brahmbhatt-zero-shot-haptics-insertion.md), [FORGE](../papers/2025-noseworthy-forge.md) | RL + force 관측 조건에는 맞지만 이미 `docs/literature/papers`에 상세 리뷰가 있어 사용자 지정 제외 조건 적용 |
| **A Residual Reinforcement Learning Method for Robotic Assembly Using Visual and Force Information**, Journal of Manufacturing Systems 2024 ([DOI](https://doi.org/10.1016/j.jmsy.2023.11.008)) | 제목과 달리 PPO actor 입력은 RGB feature뿐이다. F/T는 별도 stage logic·force/admittance controller 입력이므로 엄격 기준 탈락 |
| **Learning Force Control for Legged Manipulation**, ICRA 2024 ([IEEE](https://ieeexplore.ieee.org/document/10611066/) · [원문](https://arxiv.org/html/2405.01402v2)) | F/T sensor 없이 proprioception history로 force를 추정한다. 학습 중 privileged force는 estimator supervision이며 실행 actor의 F/T 입력이 아님 |
| **POMDP-Guided Active Force-Based Search for Robotic Insertion**, IROS 2023 ([IEEE](https://ieeexplore.ieee.org/document/10342421/) · [원문](https://arxiv.org/abs/2404.03943)) | POMDP 분석에서 전략을 유도한 FSM·impedance control 방법이며 RL로 policy를 학습하지 않음 |
| **CHEQ-ing the Box**, **Learning a High-quality Robotic Wiping Policy**, **Reinforcement Learning with Parameterized Manipulation Primitives** | F/T/force를 RL 입력으로 사용하지만 조사일 현재 확인된 버전은 arXiv preprint뿐이어서 정식 출판 필수조건 탈락 |
| **Zero-Shot Transfer of a Tactile-based Continuous Force Control Policy from Simulation to Robot**, IROS 2024 ([IEEE](https://doi.org/10.1109/IROS58592.2024.10802386)) | RL에 연속 force를 넣지만 두 finger의 scalar load-cell 신호이며 손목/말단 F/T 또는 Wrench 조사 범위와 다름 |
| Comp-ACT·Reactive Diffusion Policy·FoAR | F/T를 정책에 넣지만 각각 action-chunk imitation, diffusion/behavior cloning, diffusion policy 계열로 RL 학습 사례가 아님 |

### 6.5. 후속 조사 결론

- 가장 직접적인 선행 근거는 **R1·R2·R3·R8**이다. 이들은 force뿐 아니라 torque를 포함한 Wrench/F/T를 명시적으로 학습 state에 넣는다.
- **R4**는 3D force만 사용하므로 “6D F/T 입력”의 근거로 확대하면 안 된다. **R7**은 force/torque를 사용하지만 component 정의가 불완전하다.
- **R5·R6**는 F/T가 유용한 중간 표현을 만드는 사례다. 각각 object state estimator와 meta-RL context encoder를 통하므로 raw F/T actor input과 분리해 인용해야 한다.
- 직접 사례의 다수는 peg insertion·maze·disassembly처럼 **알려진 task frame, motion primitive, compliance controller**를 함께 사용한다. 따라서 F/T 추가만으로 자유 물체의 pose나 contact location을 복원했다고 결론 내릴 수 없다.
- F/T 제거만을 통제한 ablation은 드물다. R8의 modality ablation은 가장 가깝지만 vision·DMP·reward 구조가 유지되며, full policy도 10% tolerance에서 36.11% 성공에 그친다.

<a id="ref-w5-19-lee-2019"></a>

## 7. 연결 선행문헌 — W5 Reference [19]

**Lee, M. A., Zhu, Y., Srinivasan, K., Shah, P., Savarese, S., Fei-Fei, L., Garg, A., and Bohg, J. “Making Sense of Vision and Touch: Self-Supervised Learning of Multimodal Representations for Contact-Rich Tasks.” ICRA, 8943–8950, 2019.** [상세 노트](../papers/2019-lee-making-sense-vision-touch.md) · [DOI](https://doi.org/10.1109/ICRA.2019.8793485) · [원문](https://arxiv.org/abs/1810.10191)

- **발견·연결 경로:** [W5 Symmetry-aware RL](#w5)의 Reference [19]가 이 ICRA 논문을 직접 인용한다. W4의 Reference [16]은 제목과 저자 구성이 확장된 2020년 IEEE T-RO 후속판을 인용하며, 이번 상세 노트는 사용자가 제공한 **ICRA 2019 출판본**만 다룬다.
- **왜 별도 문헌인가:** 2019년 출판물이어서 본 조사의 2022년 이후 필수조건과 §6의 2022년 이후 RL 후속 선별을 통과하지 않는다. 따라서 W1–W7 또는 R1–R8의 수와 결론을 소급 변경하지 않고, reference chain의 배경 문헌으로만 연결한다.
- **센서 → 표현 → 정책:** 마지막 관절과 peg 사이의 OptoForce에서 1 kHz로 얻은 최근 32개 6D F/T reading, 128×128 RGB와 end-effector proprioception을 각각 인코딩해 128차원 latent로 융합한다. Action-conditional optical flow·다음 contact·sensor-stream temporal alignment를 self-supervision으로 학습한 뒤 encoder를 고정하고, TRPO가 latent에서 3D Cartesian displacement를 출력한다.
- **RL 정보 경계:** Actor는 frozen multimodal latent를 받고, staged reward는 hole-relative peg position을 사용한다. Reward state를 actor observation으로 합쳐 적으면 안 된다. Random·heuristic policy는 representation data 수집기이며 TRPO teacher가 아니다.
- **검증과 해석:** Simulation modality ablation에서 Full model은 약 76% complete insertion으로 baseline보다 높고, 실물 전용 학습은 round/triangular/semicircular peg에서 92/73/71%를 보고한다. Triangular representation+policy를 unseen hexagonal/square peg에 그대로 옮기면 각각 62%, representation만 재사용하고 policy를 새로 학습하면 81/92%다.
- **Wrench 조사에서의 의미:** 이 논문은 손목 6D Wrench가 RL policy의 학습·실행 정보 경로에 들어가는 초기 사례다. 그러나 실행 중 RGB를 계속 사용하고, F/T는 분포형 tactile이 아니며, 3D-printed peg insertion과 3-DoF translation에 한정된다. Blind manipulation이나 2022년 이후 최신 근거로 인용하지 않는다.

## 8. 조사 상태

- 원문에서 센서 출처, 실제 정책·제어 입력, 태스크 및 실물 검증 여부를 확인했다. W1·W4·W7·C1은 첨부 PDF를 후속 정독하여 각각 [FoAR](../papers/2025-he-foar.md), [Zero-Shot Transfer](../papers/2023-brahmbhatt-zero-shot-haptics-insertion.md), [FORGE](../papers/2025-noseworthy-forge.md), [Self-Tuning Planner](../papers/2022-kato-self-tuning-haptic-exploration.md) 상세 노트로 연결했고, W5 Reference [19]의 [Lee et al. 2019](../papers/2019-lee-making-sense-vision-touch.md)은 선별 집계 밖 연결 문헌으로 별도 정독했다. 하드웨어 출처가 불명확한 W6은 그 상태를 명시했다.
- 각 핵심·보조 논문의 저자 Limitation과 Future Work를 분리했다. 위치 표기의 페이지는 원문 PDF 첫 페이지를 1로 세는 기준이다.
- RL 후속 조사에서는 상세 리뷰가 있는 논문을 다시 후보로 세지 않았고, direct actor input과 estimator/context encoder를 통한 indirect input을 분리했다. 정식 출판되지 않은 preprint와 RL이 아닌 학습법도 제외 사유를 남겼다.
- 연구 방향이나 센서 사양을 새로 확정하지 않았다. 이 문서는 §2.3 수정에 사용할 비교 조사와 제안 문안이다.
