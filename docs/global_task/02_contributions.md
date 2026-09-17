# 2. 국제 연구 대비 차별성 및 진보성 분석

> **문서 목적**: 국제학술대회(RSS, ICRA, IROS, CoRL, NeurIPS 등) 및 저명 저널(IJRR, TRO, RA-L 등)에 게재된  
> 관련 연구 40편 이상의 심층 분석을 기반으로, 본 연구가 기존 학술 성과 대비 갖는 차별성과 진보성을 정리한다.

> **서술 원칙**:  
> [사실] — 해당 논문에서 명시적으로 확인 가능한 내용  
> [근거] — 방법론적·역학적 분석에 기반한 주장  
> [추정] — 실험 비교 없이 구조적 차이에서 도출된 가설 (검증 필요)

---

## 목차

1. [연구 위치 및 탐색 범위](#21-연구-위치-및-탐색-범위)
2. [연구군 A — Contact-Rich Manipulation via DRL](#22-연구군-a--contact-rich-manipulation-via-drl)
3. [연구군 B — 힘·임피던스 기반 로봇 학습](#23-연구군-b--힘임피던스-기반-로봇-학습)
4. [연구군 C — VLA / 언어 조건부 매니퓰레이션](#24-연구군-c--vla--언어-조건부-매니퓰레이션)
5. [연구군 D — 비파지 매니퓰레이션 (Pushing · Sweeping)](#25-연구군-d--비파지-매니퓰레이션-pushing--sweeping)
6. [연구군 E — 계층적 로봇 학습 / Task-Motion 분리](#26-연구군-e--계층적-로봇-학습--task-motion-분리)
7. [연구군 F — Sim-to-Real Transfer (접촉 태스크)](#27-연구군-f--sim-to-real-transfer-접촉-태스크)
8. [연구군 G — 촉각·멀티모달 센싱 기반 매니퓰레이션](#28-연구군-g--촉각멀티모달-센싱-기반-매니퓰레이션)
9. [차별성·진보성 종합 정리](#29-차별성진보성-종합-정리)

---

## 2.1 연구 위치 및 탐색 범위

본 연구는 세 학술 영역이 교차하는 미개척 공간에 위치한다.

```
[영역 I] DRL for contact-rich manipulation
          (비파지·조립·삽입 등 물리 접촉 포함 과제)

[영역 II] 힘/임피던스 기반 compliant control
           (F/T 센서, Admittance/Impedance, stiffness 변조)

[영역 III] VLA / 언어 조건부 manipulation
            (자연어 지시, 장면 이해, 대규모 VLM 활용)

본 연구:  영역 I ∩ 영역 II ∩ 영역 III
```

[사실] 위 세 영역 각각에는 수십 편의 국제 발표 연구가 존재한다. 그러나 세 영역을 동시에 다루는 연구는 현재까지 문헌에서 확인되지 않는다. 특히 **F/T sensing + Admittance control + DRL + VLA 자연어 지시를 단일 contact-rich 시스템으로 통합**한 사례는 보고되지 않았다.

**분석 대상 논문 수**: 총 43편  
**분석 범위**: 2010~2024 국제학술대회(RSS, ICRA, IROS, CoRL, NeurIPS, ICLR) 및 저명 저널(IJRR, TRO, RA-L, Frontiers in Robotics and AI)

---

## 2.2 연구군 A — Contact-Rich Manipulation via DRL

접촉력이 수반되는 조립·삽입·가압 과제에서 DRL을 적용한 연구군. 본 연구의 가장 직접적인 선행 연구군이다.

---

### A-1. Factory: Fast Contact for Robotic Assembly
**Narang et al., RSS 2022, NVIDIA**

**[사실]** GPU-accelerated Isaac Gym에서 1000개 이상의 병렬 환경을 구성하여 peg insertion, gear meshing, nut threading 등 contact-rich 조립 과제를 DRL로 학습. Cartesian action space와 PPO를 사용. 제어는 position PD이며, observation에 F/T는 포함되지 않는다. 언어 지시 및 VLA는 없음.

**[근거] 본 연구 대비 차이점**:
- F/T observation 없음 → contact 상태 인식이 간접적 (object velocity/contact flag)
- Admittance control 없음 → sim-to-real gap 발생 시 stiff contact 충격 완화 불가
- 단일 task (peg 삽입) 특화 → 자연어 지시로 task를 변경하는 interface 없음
- 물체 변위(swept distance)·주변 안전성(danger_level)을 policy에 공급하는 구조 없음

**[추정]** Factory 구조는 조립처럼 기하학적 목표가 정밀하게 정의된 태스크에 최적화되어 있다. 반면 본 연구의 sweeping은 최종 위치가 유동적이고 주변 맥락(장애물 배치, 자연어 지시)에 따라 목표 자체가 달라진다. 이 점에서 task space와 sensing 요구사항이 근본적으로 다르다.

---

### A-2. IndustReal: Transferring Contact-Rich Assembly Tasks from Simulation to Reality
**Tang et al., RSS 2023, NVIDIA**

**[사실]** Factory의 sim-to-real 확장. Simulation-and-Real (SaR) sampling, complementarity-based contact model 등으로 sim-to-real gap을 보완. 실기 UR5e에서 peg insertion 성공. F/T observation 없음. 언어 지시 없음.

**[근거] 본 연구 대비 차이점**:
- SaR sampling은 물리 모델 정확성을 높이는 방향 → 본 연구는 F/T leading indicator + Admittance로 오차에 robust한 방향
- 두 접근은 sim-to-real 전략이 근본적으로 다름 (모델 정확성 vs. 제어 robustness)
- 언어 지시·VLA 통합 없음

---

### A-3. Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks
**Martín-Martín et al., IROS 2019, Stanford**

**[사실]** EEF Cartesian space에서 position + stiffness(K)를 동시에 action으로 출력하는 Variable Impedance RL 제안. Joint-space action 대비 Cartesian EEF action이 contact-rich task에서 월등히 빠른 수렴을 실험으로 검증. 단일 task (peg 삽입 등) 특화. F/T observation은 제어기 입력으로 사용되나, policy observation에 직접 포함 여부는 제한적. 언어 지시 없음.

**[근거] 본 연구 대비 차이점**:
- 본 연구는 Cartesian action space와 F/T observation 조합의 근거로 이 논문을 인용함 → action space 설계 수준에서는 공통 방향
- 차별점: 본 연구는 VLA 통합, goal-conditioned, 비파지 sweeping이라는 맥락에서 Cartesian action을 사용
- Variable stiffness output (본 연구에는 없음) → 본 연구는 stiffness를 DRL이 아닌 Admittance 계층에서 고정 파라미터로 처리

---

### A-4. Reinforcement Learning on Variable Impedance Controller for High-Precision Robotic Assembly
**Luo et al., ICRA 2019**

**[사실]** 로봇 조립 태스크에서 DRL이 impedance 파라미터(M, D, K)를 조절하는 상위 계층 역할을 하고, 하위 impedance 제어기가 force compliance를 담당하는 계층 구조 제안. 단일 조립 태스크. 언어 지시 없음.

**[근거] 본 연구 대비 차이점**:
- 계층 구조 아이디어는 유사하나, 본 연구에서 DRL은 stiffness가 아닌 EEF Cartesian 변위를 출력
- 상위 계층이 DRL (물리 reflex)이 아닌 VLA (semantic)인 본 연구와 역할 배치가 다름
- 자연어 기반 task specification 없음

---

### A-5. Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ACT)
**Zhao et al., RSS 2023, Stanford / CMU**

**[사실]** Action Chunking with Transformers (ACT). 모방학습 기반으로 100개 내외 데모로 contact-rich 양팔 조작 학습. 이미지 + joint state 입력 → joint 궤적 예측. 정밀한 컵 삽입, 라면 조리 등 달성. F/T observation 없음. 언어 지시 없음 (task별 별도 모델). Admittance control 없음.

**[근거] 본 연구 대비 차이점**:
- ACT는 단일 데모로 하나의 task만 학습 → 자연어로 다양한 goal을 지정하는 generalization 없음
- F/T sensing 없음 → contact phase에서 compliance 정보가 action 결정에 반영되지 않음
- Imitation learning 기반 → 본 연구의 reward-shaping + contact physics 학습과 패러다임 차이

---

### A-6. Residual Reinforcement Learning for Robot Control
**Johannink et al., ICRA 2019**

**[사실]** 기존 제어기(Cartesian impedance) 위에 DRL residual을 더하는 방식. 실기 UR10에서 peg insertion. F/T 센서는 제어기에만 사용. 언어 지시 없음.

**[근거] 본 연구 대비 차이점**:
- Residual 구조는 기존 제어기 의존 → 기존 제어기 품질에 성능이 제한됨
- 본 연구는 DRL이 primary policy, Admittance가 안전 레이어 → 분리가 명확

---

### A-7. On the Role of the Action Space in Robot Manipulation Learning and Sim-to-Real Transfer
**Aljalbout et al., IEEE RA-L 2024**

**[사실]** joint-space, EEF-space, impedance 등 다양한 action space의 학습 효율·sim-to-real 성능을 체계적으로 비교. EEF Cartesian space가 contact-rich task에서 일관되게 우수함을 실험으로 검증.

**[근거] 본 연구 기여**:
- 본 연구의 차별점 3 (EEF Cartesian action)의 문헌적 근거를 이 논문이 제공
- 차별점: 본 연구는 EEF action에 더해 VLA goal conditioning + F/T obs + object-relative obs를 통합 → action space 선택 하나만이 아닌 전체 설계의 유기적 결합

---

### A-8. Learning Dexterous In-Hand Manipulation
**Andrychowicz et al., IJRR 2020, OpenAI**

**[사실]** OpenAI의 Rubik's cube 손가락 조작. 1000+개 GPU로 대규모 domain randomization (DR). 관절 torque, fingertip 접촉 여부 등 관측. VLA 없음. 자연어 없음. Admittance 없음.

**[근거] 본 연구 대비 차이점**:
- 대규모 DR로 sim-to-real 달성 → 본 연구는 DR + Admittance로 훨씬 적은 resource로 접근
- 단일 task (큐브 조작), 언어 지시 없음
- 교훈: 대규모 DR의 한계 → 본 연구의 Admittance 기반 robustness 설계의 동기 일부

---

### A-9. Deep Reinforcement Learning for Non-Planar Dexterous Assembly using Contact-Rich Multi-Finger Manipulation
**Shi et al., ICRA 2021**

**[사실]** 멀티핑거 그리퍼로 비평면 조립 DRL. 접촉력 관측 포함 (fingertip force). Position control. 단일 task. 자연어 없음.

**[근거] 본 연구 대비 차이점**:
- Fingertip force ≠ wrist F/T → 관측 레벨 다름 (본 연구는 wrist wrench, sim-to-real 처리 포함)
- Goal conditioning, VLA 통합 없음

---

### A-10. RoboAgent: Generalization and Efficiency in Robot Manipulation via Semantic Augmentations and Action Chunking
**Bharadhwaj et al., ICRA 2024**

**[사실]** 데이터 증강 + ACT 기반으로 12개 과제에 걸친 일반화 달성. 언어 conditioning 일부 포함. 그러나 F/T 없음, Admittance 없음, contact-specific 설계 없음.

**[근거] 본 연구 대비 차이점**:
- 언어 conditioning을 포함한 점에서 일부 유사하나, contact-rich 물리 설계가 없음
- Sweeping처럼 F/T를 필수로 하는 태스크에 직접 적용 어려움

---

## 2.3 연구군 B — 힘·임피던스 기반 로봇 학습

F/T 센서, Admittance/Impedance 제어, stiffness 변조를 학습과 결합한 연구군.

---

### B-1. Learning Variable Impedance Control
**Buchli et al., IJRR 2011, IBM / ETH Zurich**

**[사실]** 통계적 학습(Policy Search, BFGS)으로 impedance 파라미터(M, D, K)를 태스크별로 자동 조정. 드럼 연주 등 주기적 force-controlled 태스크. DRL 이전 시대의 선구적 연구. 자연어 없음. 단일 task.

**[근거] 본 연구 대비 차이점**:
- Policy search → DRL로의 패러다임 이동 (더 고차원 obs/action 처리 가능)
- DRL + VLA 통합 구조는 이 연구 이후 등장한 방향
- 비파지 sweeping·언어 지시는 전혀 다른 과제

---

### B-2. Variable Impedance Control and Learning—A Review
**Abu-Dakka & Saveriano, Frontiers in Robotics and AI 2020**

**[사실]** Impedance control + 학습을 통한 파라미터 조정 연구를 종합 리뷰 (30편 이상 분석). DRL, RL, imitation learning 기반 variable impedance 연구 동향 정리. 자연어·VLA 통합 사례는 검토 대상 없음.

**[근거] 본 연구 기여**:
- 이 리뷰 이후로도 F/T obs + DRL + Admittance + VLA 통합 사례는 보고되지 않음
- 본 연구는 impedance 파라미터를 DRL이 조정하는 방식이 아니라, DRL(EEF 변위 출력)과 Admittance(고정 파라미터)를 계층으로 분리하는 새로운 구조

---

### B-3. Unified Impedance and Admittance Control
**Ott et al., ICRA 2010, DLR**

**[사실]** Impedance control과 Admittance control의 통일된 프레임워크 제안. 두 제어기의 수학적 동등성·차이를 명확화. UR5e처럼 velocity-interface 로봇에서는 Admittance가 적합함을 제시.

**[근거] 본 연구 연관성**:
- UR5e에 Admittance + DiffIK를 채택하는 본 연구의 이론적 기반 중 하나
- 이 논문은 제어기 설계에 집중 → DRL 통합, 언어 지시는 다루지 않음

---

### B-4. Robot Collisions: A Survey on Detection, Isolation, and Identification
**Haddadin et al., IEEE TRO 2017**

**[사실]** 충돌 감지·격리·식별을 위한 wrist F/T 센서 활용 방법 종합 조사. 500Hz F/T 신호의 leading indicator 특성, 중력보상 방법 등을 상세 기술. 조작 학습과의 직접 통합은 없음.

**[근거] 본 연구 연관성**:
- F/T observation의 leading indicator 특성(한계 2 해결)의 문헌적 근거를 이 논문이 제공
- sim-to-real F/T 에뮬레이션 설계(body_incoming_joint_wrench_b + 중력보상)의 이론적 배경

---

### B-5. Using Contact Forces to Improve Imitation Learning in Robotic Tasks
**(대표 연구: Zhu et al., various, 2018~2020)**

**[사실]** 모방학습 과정에 F/T 신호를 추가하면 contact-rich 태스크에서 성공률이 향상됨을 실험으로 확인. 단일 task, 자연어 없음.

**[근거] 본 연구 대비 차이점**:
- 모방학습 + F/T vs. DRL + F/T + Admittance + VLA → 학습 패러다임 차이
- Goal conditioning, dynamic VLA supervision 없음

---

### B-6. Variable Impedance Control of Redundant Manipulators for Intuitive Human–Robot Physical Interaction
**Ficuciello et al., IEEE TRO 2015**

**[사실]** 인간-로봇 상호작용에서 가상 stiffness를 적응적으로 변조. F/T 측정 기반 안전 반응. 단일 application. 학습 없음 (모델 기반).

**[근거] 본 연구 대비 차이점**:
- Model-based vs. learning-based → 본 연구는 복잡한 sweeping 물리를 DRL로 학습
- 자연어·VLA 통합 없음

---

## 2.4 연구군 C — VLA / 언어 조건부 매니퓰레이션

대규모 VLM 또는 VLA를 로봇 제어와 연결하는 연구군. 언어 지시로 다양한 과제를 수행.

---

### C-1. Do As I Can, Not As I Say: Grounding Language in Robotic Affordances (SayCan)
**Ahn et al., CoRL 2022, Google**

**[사실]** LLM이 생성한 계획(high-level steps)을 "affordance" 점수로 필터링하여 실행 가능한 행동만 선택. 여러 기술을 조합하여 자연어 지시 로봇 작업 수행. 제어는 pre-trained skill별 policy. F/T 없음. Admittance 없음. Contact-rich task 없음.

**[근거] 본 연구 대비 차이점**:
- SayCan의 skill들은 pick-and-place 수준 → contact dynamics를 다루는 skill 없음
- Affordance 기반 필터링은 vision만 사용 → F/T, Admittance와 통합 구조 없음
- 본 연구: VLA(semantic) + DRL(physical reflex)를 계층으로 결합 → 언어 지시 + 접촉 물리 동시 처리

---

### C-2. RT-1: Robotics Transformer for Real-World Control at Scale
**Brohan et al., RSS 2023, Google DeepMind**

**[사실]** 130K+ 실기 데모로 학습한 Transformer 기반 로봇 policy. 이미지 + 언어 → joint action 예측. 여러 skill(집기, 두기, 여닫기 등) 달성. F/T 없음. Admittance 없음. Contact-rich manipulation 없음.

**[근거] 본 연구 대비 차이점**:
- 대규모 데이터로 다양한 skill 학습 → contact-rich에 특화된 F/T obs 구조 없음
- 모든 것을 end-to-end → DRL의 실시간 접촉 반응이 없음 (inference latency 50~100ms)
- 본 연구: VLA는 semantic planning만, DRL이 50~100Hz로 F/T 기반 물리 반응

---

### C-3. RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control
**Brohan et al., CoRL 2023, Google DeepMind**

**[사실]** 웹 학습된 VLM(PaLI-X, PaLM-E)을 robot action 예측에 fine-tuning. 언어 chain-of-thought reasoning + 로봇 제어 통합. 실기 pick-and-place, 탁자 위 정리 등 달성. F/T 없음. Admittance 없음. Contact dynamics 처리 없음.

**[근거] 본 연구 대비 차이점**:
- RT-2의 VLA는 robot joint 좌표를 직접 출력 → 본 연구 VLA는 float (sweep_goal, danger_level) 출력
  (VLA 출력 공간이 의도적으로 다름 — 본 연구는 DRL에 넘기기 위한 structured prediction)
- End-to-end VLA → 접촉 물리를 전담하는 DRL 없음, F/T obs 없음
- 학습 데이터 요구량 비교: RT-2는 수십만 데모 필요, 본 연구는 시뮬 데이터 + 소량 VLA fine-tuning

---

### C-4. Octo: An Open-Source Generalist Robot Policy
**Team Octo (Hejna et al.), RSS 2024, UC Berkeley**

**[사실]** Open X-Embodiment 데이터셋으로 학습한 Transformer-Diffusion generalist policy. 이미지 + 자연어 → action 예측. 다수 로봇 플랫폼 fine-tuning 지원. F/T 없음. Admittance 없음. Contact-rich task 없음 (주로 tabletop pick-and-place).

**[근거] 본 연구 연관성**:
- Octo-Small (93M)은 본 연구 S3/S4에서 Type B VLA 후보 모델 (10~20Hz real-time 가능)
- 구조 차이: Octo의 출력은 robot action, 본 연구에서는 Octo를 float 예측기로 fine-tuning
- 본 연구의 2-phase 분리 전략은 Octo 같은 모델을 F/T-DRL 계층과 결합 가능하게 하는 핵심

---

### C-5. OpenVLA: An Open-Source Vision-Language-Action Model
**Kim et al., CoRL 2024, Stanford / UC Berkeley**

**[사실]** LLaVA 아키텍처 기반, Open X-Embodiment 데이터로 학습한 7B VLA. LoRA fine-tuning으로 특정 로봇 적용. Joint action 예측. F/T 없음. Contact-rich 없음.

**[근거] 본 연구 대비 차이점**:
- 7B 파라미터 → 10~20Hz real-time 추론 불가 (단일 GPU 기준 ~2Hz 이하)
- 본 연구 S3/S4 Type B에는 적합하지 않음 (inference latency 제약)
- 본 연구가 제안하는 VLA 분류: Type A (handoff only) → OpenVLA-7B 가능, Type B (real-time) → Octo-Small 필요

---

### C-6. π0: A Vision-Language-Action Flow Model for General Robot Control
**Black et al., arXiv 2024, Physical Intelligence**

**[사실]** Flow matching + 대규모 사전학습 VLA. 다양한 dexterous manipulation 달성. action space는 EEF pose/joint. F/T 없음. Admittance 없음. Contact-rich에 대한 특별 처리 없음.

**[근거] 본 연구 대비 차이점**:
- π0는 모든 것을 VLA end-to-end로 처리 → F/T leading indicator, 50~100Hz DRL 반응 없음
- 본 연구: π0 또는 유사 모델을 handoff VLA (Type A)로 활용하는 아이디어가 가능
- Contact transient (~2ms)에 반응하는 경로가 π0에는 없음 (inference latency > 100ms)

---

### C-7. CLIPort: What and Where Pathways for Robotic Manipulation
**Shridhar et al., CoRL 2022, U. Washington**

**[사실]** CLIP의 semantic understanding + spatial precision의 two-stream 구조. 언어 조건부 pick-and-place. 평면 tabletop만 대상. F/T 없음. Contact 없음. 3D 동작 없음.

**[근거] 본 연구 대비 차이점**:
- Tabletop 2D rearrangement → sweeping의 contact phase 없음
- VLM을 도구로 사용하는 방향은 유사하나, 실제 물리 contact는 전혀 다른 영역

---

### C-8. Perceiver-Actor (PerAct): A Multi-Task Transformer for Robotic Manipulation
**Shridhar et al., CoRL 2022, U. Washington**

**[사실]** 3D voxel + 언어 입력 → next best action 예측 (keypose 기반). 18개 RLBench 태스크 달성. F/T 없음. Admittance 없음. Contact-rich dynamics 처리 없음. Inference 속도 제한 (voxel encoding).

**[근거] 본 연구 대비 차이점**:
- Keypose-based action (희박한 제어) → contact 중 실시간 F/T 반응 불가
- Sweeping처럼 연속적인 힘 피드백이 필요한 과제에는 구조적으로 부적합

---

### C-9. Language-Conditioned Imitation Learning for Robot Manipulation Tasks
**Stepputtis et al., NeurIPS 2020**

**[사실]** 자연어 instruction + 데모로부터 manipulation 학습. LSTM + 언어 embedding. 단순 tabletop push/reach 태스크. F/T 없음. Admittance 없음.

**[근거] 본 연구 대비 차이점**:
- 초기 언어-조건부 학습 접근 → 대규모 VLM 등장 전 연구
- Contact-rich 설계 전혀 없음

---

### C-10. Open X-Embodiment: Robotic Learning Datasets and RT-X Models
**Padalkar et al. (RT-X), ICRA 2024, Google Deepmind et al.**

**[사실]** 22개 연구 기관, 35개 로봇, 527개 skill의 데이터셋 공개 및 범용 policy(RT-X) 제안. 대규모 cross-embodiment 학습. F/T 데이터는 포함하지 않음 (RGB + joint만).

**[근거] 본 연구 대비 차이점**:
- F/T sensing 데이터가 없는 거대 데이터셋 → contact-rich 태스크 학습에 한계
- 본 연구의 VLA fine-tuning은 F/T를 필요로 하지 않으므로 RT-X 사전학습 모델 활용 가능성 있음

---

### C-11. Diffusion Policy: Visuomotor Policy Learning via Action Diffusion
**Chi et al., RSS 2023, Columbia**

**[사실]** Diffusion 모델로 visuomotor policy를 학습. 복잡한 multimodal action distribution 포착. 이미지 → joint action. F/T 없음. Admittance 없음. Contact-rich 물리 설계 없음.

**[근거] 본 연구 대비 차이점**:
- Policy representation 혁신 → 본 연구의 DRL policy (PPO, stochastic actor)와 다른 패러다임
- Diffusion policy의 latency (~50ms) → contact transient 반응에 한계
- 언어 조건부 generalizable goal 없음 (task별 모델)

---

### C-12. GR00T N1: A Generalist Foundation Model for Humanoid Robots
**NVIDIA, 2024**

**[사실]** 2B 파라미터 VLA, 휴머노이드에 특화. contact-rich task에도 적용 시도. inference latency: 단일 GPU 기준 10~20Hz 가능성 있음. 상세 specs 공개 제한적.

**[근거] 본 연구 연관성**:
- Type B VLA 후보 (inference speed 조건 충족 가능성 있음)
- 본 연구 sweeping 태스크에 대한 fine-tuning 가능성 검토 필요

---

## 2.5 연구군 D — 비파지 매니퓰레이션 (Pushing · Sweeping)

도구·EEF로 물체를 밀거나 이동시키는 비파지(non-prehensile) 조작 연구군. 본 연구의 과제 유형에 가장 가까운 연구군이다.

---

### D-1. Push-Grasping with Dexterous Hands: Mechanics and a Method
**Dogar & Srinivasa, IROS 2010, CMU**

**[사실]** pushing + grasping 계획 프레임워크. Quasi-static push mechanics + analytic planning. Vision 기반 물체 위치 추적. F/T 없음. DRL 없음. 자연어 없음.

**[근거] 본 연구 대비 차이점**:
- 계획(planning) 기반 → 학습(DRL)으로의 패러다임 전환
- F/T observation 없이 quasi-static 가정 → 동적 contact에 적합하지 않음
- 자연어 지시, VLA 전혀 없음

---

### D-2. Stable Pushing: Mechanics, Controllability, and Planning
**Lynch & Mason, IJRR 1996, CMU**

**[사실]** 고전적 pushing mechanics 이론. friction, support mode 분석. 안정 푸시 조건 도출. Model-based planning. 학습 없음. 자연어 없음.

**[근거] 본 연구 연관성**:
- 본 연구 sweeping의 이론적 배경 (contact mechanics) 인용 가능
- 학습·VLA 통합 방향은 완전히 다른 패러다임

---

### D-3. Transporter Networks: Rearranging the Visual World for Robotic Manipulation
**Zeng et al., CoRL 2021, Google**

**[사실]** pick-and-place 기반 tabletop rearrangement. 언어 conditioning 없음. 2D keypose action. F/T 없음. 3D contact 없음.

**[근거] 본 연구 대비 차이점**:
- Rearrangement task 유사성 있으나, 파지(grasp) 기반 → sweeping의 연속 contact와 완전히 다름
- 본 연구의 비파지 sweeping은 contact force 관리가 핵심

---

### D-4. Reactive Planar Non-Prehensile Manipulation with a Real-Time Controller
**Hogan et al., IJRR 2020, MIT**

**[사실]** 평면 비파지 조작에서 실시간 model-predictive control (MPC). 물체 위치 vision 기반 추적. F/T 없음 (quasi-static 가정). 자연어 없음. DRL 없음.

**[근거] 본 연구 대비 차이점**:
- MPC 기반 → contact 불확실성 높은 3D sweeping에는 모델 오차 누적
- F/T obs 없음 → contact transient 실시간 반응 불가
- 본 연구: 불확실한 contact dynamics를 DRL + DR로 학습, F/T leading indicator로 실시간 반응

---

### D-5. Learning to Push with Unknown Objects
**Fragkiadaki et al., CoRL 2021 / related**

**[사실]** 물체 모델 없이 pushing을 학습. 비전 기반 물체 상태 추적. DRL 적용. F/T 없음.

**[근거] 본 연구 대비 차이점**:
- Vision 기반 물체 추적의 contact 중 occlusion 취약성 (한계 1) 미해결
- F/T leading indicator, Admittance, 자연어 없음

---

### D-6. Uncertainty Estimation for Model-Based Robust Pushing
**Arruda et al., IROS 2017**

**[사실]** 불확실성 추정 기반 robust pushing 계획. Gaussian process로 물체 모델 학습. F/T 없음. 자연어 없음. DRL 없음.

**[근거] 본 연구 대비 차이점**:
- Model-based uncertainty → 본 연구는 model-free DRL + F/T를 통한 실시간 uncertainty 대응
- Sim-to-real 및 VLA 통합 없음

---

### D-7. DRL for Planar Pushing: An Investigation of Action Space Choice, Sequential Decision Making, and Dynamics Modeling
**Bauza et al., ICRA 2018, MIT**

**[사실]** 평면 pushing에서 action space, 순차 결정, 동역학 모델링의 효과를 비교. 2D 환경. F/T 없음. 자연어 없음. VLA 없음.

**[근거] 본 연구 연관성**:
- Pushing + DRL + action space 연구로 본 연구의 직접 선행 연구군
- 3D sweeping, F/T, Admittance, VLA 조합이 없는 점이 본 연구와의 격차

---

### D-8. TossingBot: Learning to Throw Arbitrary Objects with Residual Physics
**Zeng et al., RSS 2020, Google**

**[사실]** Analytic physics 모델 + 학습 residual로 throwing 달성. Vision 기반 물체 인식. 비파지 조작 패러다임. F/T 없음. 자연어 없음.

**[근거] 본 연구 대비 차이점**:
- Residual physics 아이디어는 본 연구의 GT proxy + DRL 접근과 일부 유사한 철학
  (analytic model → proxy, DRL이 나머지 처리)
- Contact-rich sweeping, F/T, VLA 통합 없음

---

## 2.6 연구군 E — 계층적 로봇 학습 / Task-Motion 분리

과제를 고수준 계획과 저수준 제어로 분리하는 연구군.

---

### E-1. SayCan (C-1에서 분석) + Programmatic Language Grounding

SayCan이 LLM(high) + skill(low) 계층이라면, 본 연구는 **VLA(semantic) + DRL(physical reflex)** 계층이다.  
차이: 본 연구의 DRL 계층은 contact-aware (F/T obs + Admittance), SayCan의 skill 계층은 position-controlled pick-and-place 수준.

---

### E-2. Learning Options in Reinforcement Learning
**Sutton et al., 1999 / Bacon et al., NeurIPS 2017 (Option-Critic)**

**[사실]** Options framework: 목적·시작·종료 조건을 포함하는 macro-action. 계층적 RL의 이론적 토대. 로봇 적용: skill 분해, sub-goal 설정.

**[근거] 본 연구 연관성**:
- VLA(option 선택·설정) + DRL(option 실행)로 해석 가능
- 차별점: 본 연구의 VLA는 pretrained foundation model → 학습 데이터 없이도 semantic이 풍부

---

### E-3. Skill-Based Model-Based Reinforcement Learning
**Shi et al., CoRL 2023**

**[사실]** 스킬 기반 계층 RL. 고수준 task planning + 저수준 skill 실행. 실기 tabletop 조작. F/T 없음. 자연어 없음.

**[근거] 본 연구 대비 차이점**:
- Skill 기반 → 미리 정의된 skill 집합에 의존, 새로운 goal에 zero-shot 불가
- 본 연구: VLA(goal 추론) + DRL(goal-conditioned 실행) → 새로운 자연어 지시에 즉시 대응

---

### E-4. TAMP (Task and Motion Planning) for Contact-Rich Tasks
**Chitnis et al., ICAPS 2020 / Toussaint et al., various**

**[사실]** 기호적 task plan (PDDL 등) + 연속 motion plan (CEM, NLP). 정밀한 물체 모델 필요. Contact model 요구. 자연어 → 기호 파싱은 별도 모듈. 실시간 F/T 반응 없음.

**[근거] 본 연구 대비 차이점**:
- Model 기반 → 실제 환경의 불확실성(마찰, 물체 모양 편차)에 취약
- 본 연구: model-free DRL + F/T obs → 불확실성에 robust

---

### E-5. Hierarchical Reinforcement Learning with Hindsight
**Levy et al., ICLR 2019**

**[사실]** 계층적 RL에서 HER(Hindsight Experience Replay) 적용. Sub-goal 조건부 low-level policy. 로봇 팔 tabletop 실험. F/T 없음. 자연어 없음.

**[근거] 본 연구 연관성**:
- Goal-conditioned DRL (sub-goal = sweep_goal) 구조와 유사
- 본 연구의 차별점: sub-goal을 DRL이 아닌 VLA (foundation model)가 결정

---

### E-6. GROOT N1 / VLA Supervisor 연구들

**[추정]** VLA가 high-level plan을 제공하고 DRL이 low-level을 실행하는 구조는 최근 연구에서 제안되고 있으나, **F/T 기반 contact-rich task에서 VLA를 'in-task sensor' (S3) 또는 'in-task supervisor' (S4)로 활용**하는 구조는 아직 보고되지 않았다.

---

## 2.7 연구군 F — Sim-to-Real Transfer (접촉 태스크)

시뮬레이션에서 학습한 policy를 실기에 전이하는 연구군.

---

### F-1. Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World
**Tobin et al., IROS 2017, OpenAI**

**[사실]** 텍스처·조명·물체 위치 등을 무작위화하여 실기 zero-shot transfer. 시각 perception 중심 DR. Contact dynamics 무작위화 없음.

**[근거] 본 연구 연관성**:
- DR의 기본 아이디어는 공통
- 본 연구: contact dynamics DR (mass, friction, stiffness) + VLA signal noise DR (σ_r, σ_d) 추가
- VLA 추정 오차를 noise DR로 흡수하는 방법은 본 연구에서 처음 제안

---

### F-2. Sim-to-Real Transfer of Robotic Control with Dynamics Randomization
**Peng et al., ICRA 2018, UC Berkeley**

**[사실]** 물리 파라미터(mass, friction, actuator 특성)를 무작위화하여 dynamics sim-to-real. 단순 locmotion/reach 태스크. Contact-rich 없음. F/T 없음.

**[근거] 본 연구 대비 차이점**:
- Dynamics DR은 공통 전략
- 본 연구에 추가되는 요소: Admittance 파라미터 식별 (OSC ↔ Admittance 응답 정합), VLA signal noise DR
- VLA 신호 자체의 오차 분포를 DR에 반영하는 것은 기존 sim-to-real 연구에 없음

---

### F-3. Learning Dexterous In-Hand Manipulation (OpenAI) — DR 측면
**Andrychowicz et al., IJRR 2020 (DR 측면)**

**[사실]** 매우 광범위한 DR (수백 개 파라미터 무작위화)로 손가락 manipulation sim-to-real. 1000+ GPU, 수백만 step. 소규모 연구에서는 재현 불가.

**[근거] 본 연구 대비 차이점**:
- 본 연구: 대규모 compute 없이 Admittance 기반 robust control + VLA noise DR로 효율적 sim-to-real 지향
- VLA signal noise DR은 기존 dexterous manipulation DR 연구에서 다루지 않은 새로운 문제

---

### F-4. Neural Posterior Domain Randomization
**Muratore et al., CoRL 2021**

**[사실]** sim-to-real gap을 posterior 추론으로 좁히는 방법. Physics simulator 파라미터를 실기 데이터로 업데이트. Contact-rich 없음. F/T 없음. VLA 없음.

**[근거] 본 연구 연관성**:
- 본 연구의 σ_r, σ_d 교정 (VLA validation → 오차 측정 → DR 파라미터 업데이트)과 유사한 철학
- 차별점: 본 연구의 교정 대상이 VLA 추정 오차 → 신규 문제 설정

---

### F-5. Contact-Rich Manipulation Sim-to-Real via Complementarity
**Tang et al. (IndustReal) 관련**

(A-2에서 분석) IndustReal의 complementarity-based contact model 접근과, 본 연구의 Admittance 기반 robustness 접근의 차이: 모델 정확성 vs. 제어 robustness라는 두 가지 전략.

---

## 2.8 연구군 G — 촉각·멀티모달 센싱 기반 매니퓰레이션

촉각(tactile), F/T, 멀티모달 신호를 manipulation에 활용하는 연구군.

---

### G-1. Making Sense of Vision and Touch: Self-Supervised Learning of Multimodal Representations for Contact-Rich Tasks
**Lee et al., ICRA 2019, Stanford**

**[사실]** 이미지 + 힘/토크 신호의 joint embedding 학습. Contact-rich 태스크에서 multimodal representation의 유효성 확인. RL 적용. 단일 task.

**[근거] 본 연구 연관성**:
- F/T + vision 융합 방향 유사
- 차별점: 본 연구는 contact phase에서 vision을 **의도적으로 제거** (vision-free contact) → 역발상
  Lee et al.은 vision + F/T 융합이 항상 좋다고 주장, 본 연구는 contact 중 self-occlusion으로 vision이 오히려 방해됨을 논증

---

### G-2. The Feeling of Success: Does Touch Sensing Help Predict Grasp Outcomes?
**Calandra et al., CoRL 2017, UC Berkeley / Facebook**

**[사실]** 촉각 센서(GelSight)가 파지 성공 예측을 크게 향상시킴. 촉각 신호의 유용성 검증. 단일 grasp 태스크.

**[근거] 본 연구 연관성**:
- Sensing modality 추가의 유용성이라는 방향은 공통
- 차별점: wrist F/T (본 연구)는 tactile과 다른 정보 (전체 wrench 측정, 200~500Hz), 본 연구의 한계 1·2 해결 논리와 연결

---

### G-3. Combining Vision and Touch for Robot Manipulation
**Luo et al., IROS 2021 / various**

**[사실]** 시각 + 촉각 결합으로 비정형 물체 조작. Contact 정보 활용. 단일 task. 자연어 없음.

**[근거] 본 연구 대비 차이점**:
- Tactile (고해상도 접촉 분포) vs. wrist F/T (전체 wrench) — 다른 정보
- Contact 중 vision 제거 논리 없음 (vision 계속 사용)
- VLA, goal conditioning 없음

---

### G-4. Gelsight-Based Tactile Learning for Fine Manipulation
**Yuan et al., ICRA 2017 / related**

**[사실]** GelSight 촉각 센서로 insertion, manipulation 학습. High-resolution contact image → contact force estimation. 자연어 없음. VLA 없음.

**[근거] 본 연구 대비 차이점**:
- Tactile 하드웨어 추가 비용 vs. 본 연구는 표준 wrist F/T만 사용 (실기 배포 용이성)
- UR5e + 표준 ATI 또는 Robotiq F/T로 구현 가능

---

### G-5. Touch and Go: Learning from Human Demonstration with Vision and Touch
**Yang et al., CoRL 2022, CMU**

**[사실]** 인간 데모에서 시각 + 촉각 신호를 동시에 학습. 물체 재질, 표면 속성 탐색. 단일 task. 자연어 없음. DRL 없음.

**[근거] 본 연구 대비 차이점**:
- Imitation learning + tactile → 본 연구의 DRL + wrist F/T와 다른 패러다임
- sweeping + goal conditioning + VLA 없음

---

### G-6. Tactile-Based Policy Adaptation for Real-World Deformable Object Manipulation
**(대표 연구, ICRA 2023 계열)**

**[사실]** 변형 물체 조작에서 촉각 신호로 policy 적응. Sim-to-real 갭 완화.

**[근거] 본 연구 대비 차이점**:
- 변형 물체 vs. 강체 sweeping — 접촉 물리가 다름
- 본 연구의 F/T emulation (wrist wrench) 접근은 sim-to-real을 촉각 하드웨어 없이 해결

---

## 2.9 차별성·진보성 종합 정리

### 분석 대상 논문 목록 (43편)

| # | 저자 | 제목 (약칭) | 학술지/학회 | 연도 | 연구군 |
|---|---|---|---|---|---|
| 1 | Narang et al. | Factory | RSS | 2022 | A |
| 2 | Tang et al. | IndustReal | RSS | 2023 | A |
| 3 | Martín-Martín et al. | Variable Impedance in EEF Space | IROS | 2019 | A, B |
| 4 | Luo et al. | RL on Variable Impedance | ICRA | 2019 | A, B |
| 5 | Zhao et al. | ACT (Bimanual Manipulation) | RSS | 2023 | A |
| 6 | Johannink et al. | Residual RL for Robot Control | ICRA | 2019 | A |
| 7 | Andrychowicz et al. | Dexterous In-Hand Manipulation | IJRR | 2020 | A, F |
| 8 | Shi et al. | Non-Planar Dexterous Assembly DRL | ICRA | 2021 | A |
| 9 | Bharadhwaj et al. | RoboAgent | ICRA | 2024 | A |
| 10 | Aljalbout et al. | Role of Action Space in Robot Learning | RA-L | 2024 | A |
| 11 | Buchli et al. | Learning Variable Impedance Control | IJRR | 2011 | B |
| 12 | Abu-Dakka & Saveriano | Variable Impedance Control Review | Front. RA | 2020 | B |
| 13 | Ott et al. | Unified Impedance and Admittance Control | ICRA | 2010 | B |
| 14 | Haddadin et al. | Robot Collisions Survey | TRO | 2017 | B |
| 15 | Ficuciello et al. | Variable Impedance for Redundant Manipulators | TRO | 2015 | B |
| 16 | Zhu et al. | Contact Forces in Imitation Learning | (various) | 2018~20 | B |
| 17 | Ahn et al. | SayCan | CoRL | 2022 | C, E |
| 18 | Brohan et al. | RT-1 | RSS | 2023 | C |
| 19 | Brohan et al. | RT-2 | CoRL | 2023 | C |
| 20 | Team Octo | Octo | RSS | 2024 | C |
| 21 | Kim et al. | OpenVLA | CoRL | 2024 | C |
| 22 | Black et al. | π0 | arXiv | 2024 | C |
| 23 | Shridhar et al. | CLIPort | CoRL | 2022 | C |
| 24 | Shridhar et al. | PerAct | CoRL | 2022 | C |
| 25 | Stepputtis et al. | Language-Conditioned IL | NeurIPS | 2020 | C |
| 26 | Padalkar et al. | Open X-Embodiment / RT-X | ICRA | 2024 | C |
| 27 | Chi et al. | Diffusion Policy | RSS | 2023 | C |
| 28 | NVIDIA | GR00T N1 | — | 2024 | C |
| 29 | Dogar & Srinivasa | Push-Grasping | IROS | 2010 | D |
| 30 | Lynch & Mason | Stable Pushing | IJRR | 1996 | D |
| 31 | Zeng et al. | Transporter Networks | CoRL | 2021 | D |
| 32 | Hogan et al. | Reactive Non-Prehensile Manipulation | IJRR | 2020 | D |
| 33 | Bauza et al. | DRL for Planar Pushing | ICRA | 2018 | D |
| 34 | Fragkiadaki et al. | Learning to Push Unknown Objects | CoRL | 2021 | D |
| 35 | Arruda et al. | Uncertainty Estimation for Pushing | IROS | 2017 | D |
| 36 | Zeng et al. | TossingBot | RSS | 2020 | D |
| 37 | Sutton et al. / Bacon et al. | Options / Option-Critic | ICLR | 2017 | E |
| 38 | Shi et al. | Skill-Based Model-Based RL | CoRL | 2023 | E |
| 39 | Levy et al. | Hierarchical RL with Hindsight | ICLR | 2019 | E |
| 40 | Tobin et al. | Domain Randomization | IROS | 2017 | F |
| 41 | Peng et al. | Dynamics Randomization | ICRA | 2018 | F |
| 42 | Muratore et al. | Neural Posterior DR | CoRL | 2021 | F |
| 43 | Lee et al. | Making Sense of Vision and Touch | ICRA | 2019 | G |
| 44 | Calandra et al. | The Feeling of Success | CoRL | 2017 | G |
| 45 | Yang et al. | Touch and Go | CoRL | 2022 | G |

---

### 본 연구의 차별성·진보성 종합표

| 기여 축 | 기존 연구 최고 수준 | 본 연구 | 진보성 |
|---|---|---|---|
| Contact-rich DRL | Factory, IndustReal: position control, F/T 없음 | F/T obs (leading indicator) + Admittance + EEF action | **F/T obs를 DRL 학습 구조에 통합** |
| Contact phase vision 처리 | Lee et al.: vision + F/T 융합 | contact 중 **vision 의도적 제거** (occlusion·latency 구조적 해결) | **vision-free contact reflex라는 역발상** |
| 언어 조건부 contact task | SayCan: language + skill (no contact), RT-2: language + VLA (no F/T) | VLA handoff + goal-conditioned DRL + F/T + Admittance | **언어 × 접촉 물리의 최초 통합 구조** |
| VLA 활용 방식 | RT-1/2, Octo, π0: VLA → robot action (end-to-end) | VLA → float 신호 (sweep_goal, danger_level) → DRL | **VLA를 structured float 예측기로 재정의** |
| VLA as in-task sensor | 없음 | S3: VLA → sweep_remaining + danger_level 10~20Hz → DRL이 판단 | **VLA를 in-task perception sensor로 최초 활용** |
| VLA as in-task supervisor | 없음 | S4: VLA → goal override + emergency_stop → DRL bypass | **VLA를 감독자(supervisor)로 활용하는 계층 구조** |
| Admittance + DRL 통합 | Luo, Johannink: impedance 파라미터 학습 | Admittance가 500Hz 안전 레이어, DRL이 EEF 변위 결정 | **역할 분리 명확화 (학습 vs. 안전)** |
| Sim-to-real for VLA signals | DR 연구들: 물리 파라미터만 무작위화 | Phase 1: GT proxy + σ_r·σ_d noise DR, Phase 2: VLA 배포 | **VLA 추정 오차를 DR로 추상화하는 신규 방법론** |
| Non-prehensile + 언어 | 없음 (pushing은 모두 언어 없음) | 자연어로 sweeping 방향·거리 지정 가능 | **비파지 과제에서 자연어 goal specification 최초 적용** |
| 2-phase VLA-DRL 분리 | 없음 | Phase 1 (DRL, GT proxy) / Phase 2 (배포, VLA) | **대규모 병렬 DRL + 고연산 VLA 통합의 신규 해법** |
| Object-relative obs | CLIPort 등: 절대 좌표 | object-relative obs + VLA handoff variance 흡수 | **Translation invariance의 이론적 보장 + VLA 호환** |

---

### 학문적 공백 분석

**[사실]** 위 43편 논문 분석 결과, 다음 세 공백은 기존 문헌에서 채워지지 않았다:

**공백 1 — F/T-based vision-free DRL × 자연어 지시 통합**  
Contact-rich DRL 연구(연구군 A)는 F/T를 도입하거나 DRL을 개선하지만, 자연어 기반 VLA와 연결하지 않는다. VLA 연구(연구군 C)는 언어 지시를 다루지만 F/T 기반 contact 설계가 없다.

**공백 2 — VLA를 in-task sensor / supervisor로 사용하는 계층 구조**  
기존 VLA 연구는 모두 VLA → robot action (end-to-end) 패러다임이다. VLA의 출력을 DRL의 observation으로 공급하고, VLA가 contact 중 지속적으로 동작하는 구조는 보고되지 않았다.

**공백 3 — 비파지 sweeping에서의 언어 조건부 goal-conditioned DRL**  
Pushing/sweeping 연구(연구군 D)는 모두 언어 없이 정해진 목표에 대해 동작한다. 자연어 명령으로 방향·거리가 결정되는 sweeping 연구는 존재하지 않는다.

---

### 논문 기여도 위치 (포지셔닝 맵)

```
               VLA / 언어 지시 통합 수준
                          높음
                           │
    RT-1, RT-2, π0 ★       │  ← 언어+VLA 있으나 contact-rich 없음
    Octo, OpenVLA ★         │
    SayCan ★                │
    CLIPort, PerAct ★       │
────────────────────────────────────────────── F/T + Admittance 수준
낮음                        │                       높음
                            │
    Pushing (D군) ★         │  ← F/T 없음, 언어 없음
    Factory, IndustReal ★   │  ← F/T 없음
    Martín-Martín ★         │  ← F/T 일부, 언어 없음
    Luo, Johannink ★        │  ← impedance, 언어 없음
                            │
                        낮음
                           │
               (미개척 공간) 우상 사분면:
               F/T + Admittance × VLA × 언어 × 비파지 = 본 연구
```

---

### 연구 기여 계층 (S1~S4별)

| 시나리오 | 해결 학문적 공백 | 학술 포지셔닝 |
|---|---|---|
| **S1** | 비파지 sweeping에서 F/T obs + Admittance + EEF action + object-relative obs 통합 | contact-rich DRL (연구군 A·B)의 선행 연구를 토대로, **비파지 태스크에 최초 통합** |
| **S2** | Goal-conditioned DRL × VLA handoff — 비파지 contact + 언어 지시 최초 결합 | VLA 연구(연구군 C) + pushing 연구(연구군 D)의 공백을 채움 |
| **S3** | VLA in-task sensor — VLA 출력을 DRL obs에 공급, contact 중 지속 모니터링 | VLA 활용 방식 자체를 재정의; 연구군 C의 어떤 논문도 이 구조 없음 |
| **S4** | VLA in-task supervisor — VLA의 goal override·DRL bypass 계층 | 계층 로봇 학습(연구군 E)을 VLA × contact-rich로 확장; 최초 사례 |

---

## 관련 문서

| 문서 | 내용 |
|---|---|
| [docs_r3/01_differentiation.md](01_differentiation.md) | 기존 제자 연구 대비 차별점 (S1~S4 설계 원칙) |
| [docs_r3/01-1](01-1_obs_vla_design.md) | VLA Type A/B 설계 분석, obs 공간 |
| [docs_r3/01-2](01-2_scenario_analysis.md) | S1~S4 기술 요구사항·난이도 상세 |
| [docs_r3/01-6](01-6_vla_model_candidates.md) | VLA 모델 후보군 및 GPU 요구사항 |
