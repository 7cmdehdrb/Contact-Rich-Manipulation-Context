# Initial 관측 이후 Blind Sweep을 위한 F/T·촉각 기반 Pushing 문헌 조사

**조사 기준일: 2026년 9월 14일**  
**범위: 2022년 이후 SCIE 저널 논문. 직접 pushing 연구와 인접 조작 연구를 구분.**

## 1. 결론

초기 정보 이후 물체의 시각적 자세를 계속 관측하지 않고 미는 방법은 이미 존재한다. 따라서 현재 연구에서 먼저 밝힐 것은 ‘Blind로 밀 수 있는가’라는 단일 성공 여부보다, **어떤 힘·접촉 정보를 어떤 표현으로 바꾸어 어떤 운동을 수정하는가**, 그리고 그 연결이 어느 센싱 조건에서 무너지는가다. [R1, R2]

이번에 원문의 pushing 메커니즘까지 확인하여 직접 비교한 논문은 **F/T 센서 기반 1편과 tactile 센서 기반 5편**이다. 실제 F/T와 tactile을 함께 사용한 사례도 확인했지만, 아래 R7은 **문 열기의 실패 복구**이며 자유 물체의 Blind Sweep과는 다르다. **두 센서의 실행 중 결합이 자유 물체 pushing을 어떻게 개선하는지까지 검증된 직접 사례는 이번 확인 범위에서 확보하지 못했다.** 이는 해당 연구가 존재하지 않는다는 증명이나 신규성의 확정이 아니다.

검토 결과에서 구분되는 연결 방식은 다음과 같다.

| 정보 활용 방식 | 관측에서 운동까지의 연결 | 대표 논문 |
| --- | --- | --- |
| 힘 방향을 이용한 조향 | 평면 접촉력 방향 → 경로 방향과의 오차 → pusher 진행 방향 수정 | R1 |
| 접촉 위치를 이용한 재정렬 | 활성 촉각 영역 → 접촉 위치·모서리 접근 → 횡이동·회전 조정 | R2 |
| 접촉 기하·변형을 이용한 servoing | 접촉면 pose·shear 추정 → 목표 접촉 상태와의 오차 → Cartesian 속도 | R3 |
| 접촉 상태를 이용한 정책·미래 예측 | tactile pose 또는 이미지 → 정책/동역학 모델 → 횡이동·yaw 선택 | R4 |
| 촉각 이미지 기반 sim-to-real | 실제 촉각 이미지 → 시뮬레이션 표현 → 학습 정책의 이동·회전 | R5, R6 |
| 센서 결합에 의한 실패 복구 | 접촉 실패 상태 → 환경 모델 보정 → 다음 조작 경로 재계획 | R7, 인접 연구 |

## 2. 조사·분류 기준

### 2.1 프로젝트의 기준

프로젝트의 현재 대상은 **초기 시각 정보와 상위 접근 결과를 받은 뒤, 물체 시각 추적을 갱신하지 않고 수행하는 하위 Sweeping**이다. 시작 시 정확한 접촉, 촉각 영역 접촉, 충분한 힘 신호가 보장된다고 전제하지 않는다. 상위 탐색·접근·복잡한 간섭 판별을 자동으로 현재 연구에 추가하지 않는다. [P1–P3]

UR5e–손목 F/T–Inspire Hand 구성과 17개 촉각 영역의 축약 표현은 프로젝트에서 논의된 계획이다. 특히 ‘17차원 scalar/Boolean’은 실제 센서의 원시 정보와 동일하다고 확정된 사양이 아니다. 아래 적용 제안은 이 미정 상태를 유지한다. [P2, P3]

### 2.2 검색과 검증

Sider Scholar의 OpenAlex 기반 검색과 Scholar 검색으로 `tactile pushing`, `robotic pushing force feedback`, `pushing tactile force torque sensor` 등의 후보를 수집했다. 검색 기간은 2022-01-01부터 조사 기준일까지로 설정했다. 관련성이 낮은 검색 결과와 일부 서지 조회 실패가 있어, 논문 제목·DOI를 출판사, 저자 공개 원문, 대학 연구정보와 대조했다.

본 문서는 메커니즘 중심의 선별 조사다. 모든 데이터베이스의 전수검색, 독립적인 이중 선별, 전체 WoS accession number의 확보를 수행한 체계적 문헌고찰은 아니다. SCIE 여부는 저널의 공개 색인 안내로 확인했으며, Impact Factor 보유만으로 판단하지 않았다. 직접 비교 논문의 저널은 IEEE Robotics and Automation Letters와 The International Journal of Robotics Research이고, 인접 결합 사례는 IEEE Access다. [J1–J3]

### 2.3 센서와 정보의 구분

**F/T 기반:** 별도의 F/T 센서 측정이 실행 중 제어에 기여하는 경우다. 장비가 6축이어도 알고리즘이 평면 힘 두 성분만 사용한다면 그 사실을 따로 기록한다.

**Tactile 기반:** 접촉면의 분포·위치·변형·이미지를 센서로 읽는 경우다. 촉각으로 힘을 추정하는 것은 이 범주이지, 그 자체로 ‘F/T와 tactile 동시 사용’이 아니다. TacTip·DIGIT의 내부 카메라는 피부 변형을 읽는 센서 구성요소이며, 외부 장면·물체를 촬영하는 온라인 vision과 구분한다. [R3–R6]

**둘 다:** 실제 F/T와 tactile이 각각 있고 실행 중 역할이 확인되는 경우다. 촉각 센서의 학습·교정 정답을 얻으려고만 F/T를 사용한 경우, 두 개의 촉각 센서를 사용한 경우, 시뮬레이션 contact force를 reward에만 넣은 경우는 포함하지 않는다.

‘시각 없이 수행’은 로봇의 자기 위치·관절 상태·목표 위치까지 없다는 뜻도 아니다. 특히 모바일 로봇의 자기 위치 추정과 조작 대상의 온라인 자세 추정은 별개다.

## 3. F/T 센서를 사용하는 경우

### R1. Force Push: Robust Single-Point Pushing With Force Feedback

**Heins & Schoellig, IEEE RA-L 9(8):6856–6863, 2024.** DOI: `10.1109/LRA.2024.3414180`

**원래 목적:** 상세 물체 모델 없이 단일 접촉으로 경로를 따라 미는 반응형 제어다. 준정적 운동·볼록 물체 등의 가정이 있다.

**정보 → 행동:** 실제 F/T의 **평면 힘 벡터**를 평활화하고, 힘 방향과 경로 방향의 차이 및 pusher 횡오차로 조향한다.

$$
\[
\theta_p=\theta_d+(k_f+1)(\theta_f-\theta_d)+k_c\Delta_c
\]
$$

단순히 힘 방향을 따라가는 것이 아니라, 방향 편차를 증폭한 조향으로 접촉 기하를 바꾸어 경로로 복귀시킨다. 약한 힘에서는 접촉 회복으로 전환하고, 과도한 힘에서는 admittance 보정으로 감속·역방향 성분을 만든다. Cartesian 속도가 관절 속도로 변환된다. [R1, §III]

**경계:** 온라인 물체 pose가 필요 없는 직접 선행이지만 6축 전체의 필요성을 입증하지는 않는다. 힘 방향≠물체 orientation이고, pusher 경로 추종≠물체 중심의 정확한 목표 변위 달성이다.

## 4. Tactile 센서를 사용하는 경우

### R2. Pushing in the Dark: A Reactive Pushing Strategy for Mobile Robots Using Tactile Feedback

**Ozdamar et al., IEEE RA-L 9(8):6824–6831, 2024.** DOI: `10.1109/LRA.2024.3414279`

**원래 목적:** 온라인 물체 pose 없이 큰 물체를 목표로 미는 **모바일 베이스** 제어다. 매니퓰레이터 손 조작은 아니다.

**정보 → 행동:** 42개 정전용량 taxel을 필터링·임계값 처리한다. 하나가 활성화되면 해당 위치, 여러 개면 양 끝 활성 taxel의 중점을 대표 접촉 위치로 사용한다. 접촉이 중앙에서 벗어날수록 횡이동 비중을 높인다. 모서리 부근에서는 재정렬 상태로 전환해 회전을 억제하고 접촉을 중앙으로 이동시킨다. 목표 방향은 로봇의 자기 위치와 대표 접촉점으로 계산한다. 정밀한 힘 복원보다 **접촉 위치→횡이동·회전**이 핵심이다. [R2]

**경계:** 영역별 scalar/Boolean의 활용 사례지만 베이스의 커버리지와 부분 촉각 손은 다르다. 종료도 대표 접촉점 기준이므로 물체 전체 pose 달성으로 해석하지 않는다.

### R3. Pose-and-shear-based tactile servoing

**Lloyd & Lepora, IJRR 43(7), 2024.** DOI: `10.1177/02783649231225811`

**원래 목적:** 물체·표면 추종과 단일/양팔 pushing을 포괄하는 촉각 servoing이다. Shear를 잡음이 아닌 제어 정보로 활용한다.

**정보 → 행동:** TacTip 이미지로 접촉면 깊이·기울기와 접촉 후 shear를 확률적으로 추정한다. 로봇 운동을 결합한 Bayesian filtering으로 추정을 안정화하고, 기준 접촉 상태와의 오차를 PID 기반 Cartesian 속도로 변환한다. Pushing에서는 여기에 전진 feedforward와 목표 정렬용 횡방향 제어를 더한다. 즉 **접촉 유지와 목표 진행을 별도 제어 성분으로 결합**한다. [R3]

**경계:** 물체 전체 pose보다 제어에 필요한 국소 접촉 상태를 추정한다. 고해상도 피부 변형에서 얻는 pose/shear가 17개 압력 scalar에서도 복원된다는 보장은 없다. 지지면·물체 형태에 따른 실패도 있어 보편적인 전도 방지 성능으로 확대할 수 없다.

### R4. Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing

**Yang et al., IEEE RA-L 8(9):5480–5487, 2023.** DOI: `10.1109/LRA.2023.3295236`

**원래 목적:** 임의 목표를 향한 tactile pushing에서 관측 표현과 model-free/model-based 방법을 비교한다.

**정보 → 행동:** ① 이미지→sim 표현→SAC, ② 이미지→PoseNet의 국소 접촉면 pose→SAC, ③ 같은 pose·로봇 상태→확률적 ensemble 동역학→PETS/CEM-MPC를 비교한다. MPC는 후보 행동의 접촉 상태 변화를 예측하고 첫 행동 실행 후 재계획한다. 접촉면 법선–목표 방향 및 pusher–접촉면의 정렬을 reward로 연결한다. **횡이동·yaw가 정책 행동이고 전진 증분은 고정**이다. [R4, §III–IV]

**경계:** Tactile pose는 물체 중심 pose가 아니다. 안정적인 초기 접촉을 전제하며 고정 전진 때문에 일부 가까운 목표는 도달하기 어렵다. 외부 ArUco는 평가용이지 actor 입력이 아니다.

### R5. Tactile Gym 2.0: Sim-to-Real Deep Reinforcement Learning for Comparing Low-Cost High-Resolution Robot Touch

**Lin et al., IEEE RA-L 7(4):10754–10761, 2022.** DOI: `10.1109/LRA.2022.3195195`

**원래 목적:** TacTip·DIGIT·DigiTac과 저가 로봇을 비교하는 sim-to-real 플랫폼이다. Pushing은 여러 평가 과업 중 하나다.

**정보 → 행동:** 실제 촉각 이미지를 시뮬레이션 접촉 깊이 표현으로 변환하고 PPO가 TCP 이동·회전을 결정한다. 명시적 상태 추정보다 학습 표현을 사용하므로 정책 내부의 물리적 추론까지 설명했다고 과장하면 안 된다.

**핵심 관찰:** DIGIT의 가벼운 물체 pushing 실패에 대해 저자들은 피부 변형 부족·표현 변환 문제를 제시했다. 무게를 추가하면 재학습 없이 회복됐다. **접촉→변형→표현** 단계에서 관측이 부족할 수 있다는 근거다. [R5]

**경계:** 물체를 무겁게 하는 것은 진단용 조건 변경이지, 가벼운 물체를 조작해야 하는 프로젝트의 해결책 자체는 아니다.

### R6. Bi-Touch: Bimanual Tactile Manipulation With Sim-to-Real Deep Reinforcement Learning

**Lin et al., IEEE RA-L 8(9):5472–5479, 2023.** DOI: `10.1109/LRA.2023.3295991`

**원래 목적:** Bi-pushing·bi-reorienting·bi-gathering을 수행하는 양팔 촉각 시스템이다. 단일 손 Sweep이나 F/T–tactile 융합 연구가 아니다.

**정보 → 행동:** 두 TacTip 이미지를 각각 sim 표현으로 변환하고 로봇 상태와 함께 PPO에 제공한다. Bi-pushing에서는 **각 팔의 TCP 이동·yaw를 합친 4차원 행동**을 결정한다. 목표 위치·orientation 보상에 양쪽 TCP–접촉면 법선 정렬 보상을 더해 접촉 유지를 유도한다. [R6]

**경계:** 두 접촉 관측을 공동 행동으로 연결하지만 명시적인 힘 평형·torque 분배 추정을 입증하지는 않는다. GT 기반 학습 reward와 실행 actor 관측도 구분해야 한다. Goal-update 방법은 bi-gathering에 해당하며 bi-pushing의 기법으로 소개하지 않는다.

R3–R6은 저자·연구실이 겹치는 계열이다. 네 독립 연구팀의 재현 결과로 해석하지 않는다.

## 5. F/T와 Tactile을 모두 사용하는 경우

### 5.1 직접 pushing 사례의 확인 결과

이번 조사에서는 **실제 F/T와 실제 tactile을 실행 중 결합하여 자유 물체를 Blind로 미는 제어 연결까지 확인된 2022년 이후 SCIE 사례를 확보하지 못했다.** 따라서 세 번째 분류를 채우기 위해 다음을 넣지 않았다.

- TacTip에서 force/shear를 추정하는 R3을 ‘두 센서 사용’으로 재분류하지 않는다.
- 두 TacTip을 사용하는 R6을 ‘F/T+tactile’로 재분류하지 않는다.
- F/T가 tactile 학습용 정답이나 보상 계산에만 사용되는 경우를 실행 중 융합으로 보지 않는다.

### R7. Framework for Robot Door Opening Based on Visual, Force, and Tactile Integration — 인접 연구

**Šimundić et al., IEEE Access 14:11110–11128, 2026.** DOI: `10.1109/ACCESS.2026.3655617`

**원래 목적:** 손잡이 없는 캐비닛 문의 좁은 틈에서 발생하는 실패를 복구한다. UR5·3D 카메라·실제 F/T·tactile을 사용한다.

**정보 → 행동:** 저자 자료에서 확인되는 연결은 **접촉 누락·손실·충돌 검출→실패 정보→카메라 파라미터 보정→환경 모델 갱신→문 열기 경로 재계획**이다. 센서 결합은 연속 속도의 직접 계산보다 다음 행동의 기하학적 조건을 바꾸는 데 기여한다. [R7]

**경계:** 자유 물체 pushing이 아니라 구속된 문 열기이며 실패 뒤 시각 모델을 갱신한다. 현재 프로젝트에 재보정·재접근 기능을 추가해야 한다는 결론은 아니다.

**확인 한계:** 정식 게재·센서 구성·실패 복구 연결은 확인했다. 접근 제한으로 개별 센서의 임계값·제어식·융합 ablation까지 전체 원문 검증을 마치지는 못했다. 따라서 센서별 정량 기여나 특정 연속 force-control 법칙은 주장하지 않는다.

## 6. 비슷해 보이지만 직접 근거로 사용하지 않은 논문

| 논문 | 원래 기여와 제외 이유 |
| --- | --- |
| Learning adaptive reaching and pushing skills using contact information, Frontiers in Neurorobotics, 2023 | 접촉력을 이용한 학습 보상 설계가 핵심이다. 이를 실행 중 실제 F/T 피드백으로 Blind pushing하는 근거로 사용하지 않았다. [E1] |
| Zero Moment Two Edge Pushing of Novel Objects With Center of Mass Estimation, IEEE TASE, online 2022 | 질량중심 추정과 두 모서리 pushing의 기계적 구성이다. 시각으로 측정한 물체 운동을 사용하는 방법을 제목의 힘·모멘트 때문에 F/T sensing으로 분류하지 않았다. [E2] |
| ViTacGen: Robotic Pushing with Vision-to-Touch Generation, IEEE RA-L, 2025 | 실제 촉각 하드웨어 없이 vision으로 tactile 표현을 생성하는 것이 목적이다. 온라인 vision을 사용하는 장점을 무시하고 tactile-only Blind 연구로 소개하지 않았다. [E3] |
| An ultralight, tiny, flexible six-axis force/torque sensor enables dexterous fingertip manipulations, Nature Communications, 2025 | 소형 6축 센서와 조작 시연이 핵심이다. 힘 신호를 측정·기록했다는 사실만으로 그 신호가 자율 pushing의 폐루프 제어를 결정했다고 인정하지 않았다. [E4] |

여기서 ‘제외’는 연구의 질이 낮다는 뜻이 아니라, 이번에 묻는 **센서 관측에서 pushing 행동까지의 인과 경로**를 직접 입증하는 자료가 아니라는 뜻이다.

## 7. 프로젝트에 가져올 수 있는 해석과 제안

**아래는 문헌 비교에서 도출한 제안이며, 교수 지시·구현 완료·최종 사양이 아니다.**

### 7.1 먼저 ‘어떤 정보를 잃으면 어떤 행동을 못 하는가’를 정의한다

| 필요한 판단 | 우선 검토할 표현 | 연결할 운동 | 선행연구에서의 출발점 |
| --- | --- | --- | --- |
| 실제 접촉이 성립했는가 | 보정 F/T 크기·변화, tactile 활성, 센서 유효성 | 접근 지속/감속/접촉 회복 | R1, R2 |
| 접촉이 손의 어느 쪽으로 이동하는가 | 활성 영역 위치·변화, 가능한 경우 국소 압력 분포 | 횡방향 이동·yaw 보정 | R2 |
| 접촉면에 대해 잘 정렬되어 있는가 | 추정 가능한 법선·기울기·shear | 접촉 유지 자세·속도 보정 | R3, R4 |
| 현재 운동이 과도한 저항을 만드는가 | 보정 wrench, 방향·크기 변화 | 속도 제한·순응적 보정 | R1 |
| 촉각 관측 자체가 충분한가 | 물체별 신호 대 잡음, 변형량, 사각지대, 누락 | 관측 신뢰도 반영·보수적 전환 | R5에서 도출한 검증 질문 |
| 목표 물체가 실제로 이동했는가 | 별도 상태 추정 또는 실행 종료 가설의 검증 | 종료/지속 판단 | 접촉점 기반 목표와 물체 목표를 구분해야 함 |

여기서 normal/shear 추정은 실제 센서가 제공하는 정보로 가능할 때만 채택한다. 17개 영역의 scalar에서 고해상도 TacTip의 정보를 그대로 복원할 수 있다고 가정하지 않는다.

### 7.2 결합의 이유는 단순한 차원 증가가 아니라 모호성 감소여야 한다

단순한 준정적 모델에서 하중·영점 등의 보정이 이루어졌다고 가정하면 손목 측정은 대략 다음 형태다.

\[
\mathbf F=\sum_i\mathbf f_i,\qquad
\boldsymbol\tau=\sum_i\mathbf r_i\times\mathbf f_i+\sum_i\mathbf m_i.
\]

이는 접촉점별 힘과 모멘트가 합쳐진 값이다. 여러 접촉 분포가 같은 손목 wrench를 만들 수 있으므로, F/T만으로 ‘어느 손가락이 어디에 닿았는지’를 일반적으로 유일하게 결정할 수는 없다. 반대로 부분적으로 부착된 tactile이 0이어도 비센서 영역의 접촉은 남을 수 있다. 이 식과 다음 가설은 본 보고서의 일반 역학적 해석이지, R1–R7이 해당 Inspire Hand에서 검증한 결과가 아니다.

**검증할 결합 가설:** F/T는 전체 부하·저항 변화에, tactile은 접촉 위치·분포 변화에 기여하도록 한다. 두 관측의 조합이 접촉 위치 불확실성이나 사각지대에서 운동 수정을 개선하는지를 측정한다. 예를 들어 ‘F/T는 반응하는데 tactile은 약하다’를 비센서 접촉의 *후보*로 해석할 수 있지만, 센서 이상·보정 오차·약한 접촉 등과 구별하는 추가 검증 없이 확정하면 안 된다.

F/T 상승을 곧바로 주변 물체 충돌이라고 이름 붙이는 것도 잘못이다. 저항 증가, 마찰 변화, 자세 변화, 다중 접촉 등 구분되지 않는 원인이 남을 수 있다. 현재 연구에 복잡한 간섭 분류를 먼저 추가하기보다, 기본 조작에서 어떤 모호성이 실제 실패를 유발하는지부터 확인하는 편이 타당하다.

### 7.3 학습 전에 관측 표현의 후보를 비교한다

첫 비교는 `raw F/T + raw tactile`이라는 단일 안으로 고정하기보다 다음 두 수준을 구분하는 것이 유용하다.

**최소 가공 표현:** 하중·영점 보정 wrench, 영역별 tactile 값, 센서 유효성·sample age. 원시 신호에 가까워 정보 손실은 적지만 학습이 좌표계·잡음·접촉 의미를 함께 해결해야 한다.

**의미를 부여한 표현:** 활성 접촉 영역, 접촉 위치의 좌우 편향, wrench 방향·크기, 접촉 유지 오차 등. R1–R4처럼 어떤 운동을 바꿀 것인지 설명하기 쉽지만, 실제 센서로 추정 가능한 값인지 검증해야 한다.

두 표현이 꼭 별도 정책이어야 하는 것은 아니다. raw 신호와 추정 상태를 함께 쓰거나 추정 모듈의 보조학습을 비교할 수 있다. History·RNN도 확정하지 않고, 순간 관측으로 구분할 수 없는 상태가 실제 실패를 만드는 경우에 필요성을 시험한다.

### 7.4 성공률뿐 아니라 ‘센서 때문에 바뀐 행동’을 남긴다

동일한 초기 정보·로봇 상태·목표·제어 경로에서 무접촉센서 기준선, F/T-only, tactile-only, 결합 정책을 비교하는 실험을 제안한다. 무접촉센서 기준선은 안전 감독까지 제거한다는 뜻이 아니다.

단순히 결합 정책의 성공률이 높다는 결과보다 다음 연결이 기록되어야 한다.

> 접촉이 측면으로 이동했다 → tactile 표현이 변했다 → 횡이동/yaw 보정이 발생했다 → 접촉 손실이 감소했다.
>
> 저항이 증가했다 → 보정 F/T가 변했다 → 속도가 감소했다 → 과도한 하중이 줄면서 물체 이동이 유지됐다.

특정 채널을 가리거나 지연시키는 비교는 그 채널의 기여를 시험하는 방법이다. 다만 평가 시 갑작스러운 입력 제거 자체가 학습 분포 밖 교란이므로, 해당 센서 없이 훈련한 정책과 평가 시 채널을 제거한 정책은 구분한다.

평가는 **물체 변위, 접촉 손실, 과도한 힘, 전도, 수행 시간**을 구분하고, 약한 신호·비센서 접촉·초기 접촉 오차별로 실패를 나눈다. 학습용 GT reward, 평가용 GT, 실행 actor의 정보를 분리한다. 특히 **손이 목표 거리만큼 움직였다는 사실을 물체의 목표 변위 달성으로 대체하지 않는다.** [P2, P3]

## 8. 현재 연구 질문의 권장 표현

> **초기 시각 관측 이후 물체 상태를 갱신하지 않는 조건에서, 제한된 손목 F/T와 부분 촉각 관측을 어떤 접촉 표현으로 결합해야 접촉 유지와 목표 방향 진행을 안정적으로 수행할 수 있는가? 그리고 약한 신호·센서 사각지대·초기 접촉 오차에서 각 센서의 기여와 한계는 무엇인가?**

이 표현은 특정 clutter 과업이나 새로운 controller를 미리 확정하지 않는다. 이미 존재하는 Blind pushing을 출발점으로 인정하면서, 프로젝트에서 실제로 검증해야 할 **관측 정보·표현·행동 수정의 연결**을 연구 대상으로 둔다.

## 9. 참고문헌과 확인 경로

### 직접 비교 논문

**[R1]** Adam Heins and Angela P. Schoellig. *Force Push: Robust Single-Point Pushing With Force Feedback*. IEEE Robotics and Automation Letters, 9(8):6856–6863, 2024. DOI: 10.1109/LRA.2024.3414180.  
[출판 정보](https://doi.org/10.1109/LRA.2024.3414180) · [저자 공개 원문](https://arxiv.org/pdf/2401.17517)

**[R2]** Idil Ozdamar, Doganay Sirintuna, Robin Arbaud, and Arash Ajoudani. *Pushing in the Dark: A Reactive Pushing Strategy for Mobile Robots Using Tactile Feedback*. IEEE Robotics and Automation Letters, 9(8):6824–6831, 2024. DOI: 10.1109/LRA.2024.3414279.  
[출판 정보](https://doi.org/10.1109/LRA.2024.3414279) · [저자 공개 원문](https://arxiv.org/pdf/2403.09305)

**[R3]** John Lloyd and Nathan F. Lepora. *Pose-and-shear-based tactile servoing*. The International Journal of Robotics Research, 43(7), 2024. DOI: 10.1177/02783649231225811.  
[출판 정보](https://doi.org/10.1177/02783649231225811) · [저자 공개 원고: 제목 표기가 정식판과 다름](https://arxiv.org/pdf/2306.08560)

**[R4]** Max Yang et al. *Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing*. IEEE Robotics and Automation Letters, 8(9):5480–5487, 2023. DOI: 10.1109/LRA.2023.3295236.  
[출판 정보](https://doi.org/10.1109/LRA.2023.3295236) · [저자 공개 원문](https://arxiv.org/pdf/2307.14272)

**[R5]** Yijiong Lin, John Lloyd, Alex Church, and Nathan F. Lepora. *Tactile Gym 2.0: Sim-to-Real Deep Reinforcement Learning for Comparing Low-Cost High-Resolution Robot Touch*. IEEE Robotics and Automation Letters, 7(4):10754–10761, 2022. DOI: 10.1109/LRA.2022.3195195.  
[출판 정보](https://doi.org/10.1109/LRA.2022.3195195) · [저자 공개 원문](https://arxiv.org/pdf/2207.10763)

**[R6]** Yijiong Lin et al. *Bi-Touch: Bimanual Tactile Manipulation With Sim-to-Real Deep Reinforcement Learning*. IEEE Robotics and Automation Letters, 8(9):5472–5479, 2023. DOI: 10.1109/LRA.2023.3295991.  
[출판 정보](https://doi.org/10.1109/LRA.2023.3295991) · [저자 공개 원문](https://arxiv.org/pdf/2307.06423) · [연구실 서지](https://sites.google.com/view/bi-touch/)

### 실제 F/T+tactile 병용: 인접 과업

**[R7]** Valentin Šimundić, Luka Petrović, Matej Džijan, and Robert Cupec. *Framework for Robot Door Opening Based on Visual, Force, and Tactile Integration*. IEEE Access, 14:11110–11128, 2026. DOI: 10.1109/ACCESS.2026.3655617.  
[출판 정보](https://doi.org/10.1109/ACCESS.2026.3655617) · [저자 프로젝트](https://multi-contact-door.github.io/) · [소속기관 연구 설명](https://www.ferit.unios.hr/research-groups/IG04/research/robot-door-opening-based-on-visual-force-and-tactile-integration)

### 범주 혼동을 방지하기 위한 대조 문헌

**[E1]** Shuaijun Wang et al. *Learning adaptive reaching and pushing skills using contact information*. Frontiers in Neurorobotics, 17:1271607, 2023. DOI: 10.3389/fnbot.2023.1271607.  
[원문](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2023.1271607/full)

**[E2]** Ziyan Gao, Armağan Elibol, and Nak Young Chong. *Zero Moment Two Edge Pushing of Novel Objects With Center of Mass Estimation*. IEEE Transactions on Automation Science and Engineering, online 2022. DOI: 10.1109/TASE.2022.3208739. 온라인 공개 연도와 최종 권·호 연도를 구분한다.  
[출판 정보](https://doi.org/10.1109/TASE.2022.3208739) · [저자 공개 원문](https://dspace.jaist.ac.jp/dspace/bitstream/10119/18155/1/T-ASE%20final%20version.pdf)

**[E3]** *ViTacGen: Robotic Pushing with Vision-to-Touch Generation*. IEEE Robotics and Automation Letters, 2025. DOI: 10.1109/LRA.2025.3621941.  
[출판 정보](https://doi.org/10.1109/LRA.2025.3621941) · [저자 공개 초록](https://arxiv.org/abs/2510.14117)

**[E4]** Qian Mao et al. *An ultralight, tiny, flexible six-axis force/torque sensor enables dexterous fingertip manipulations*. Nature Communications, 16:5693, 2025. DOI: 10.1038/s41467-025-60861-8.  
[출판사 원문](https://www.nature.com/articles/s41467-025-60861-8)

### 저널 색인 확인

**[J1]** IEEE Robotics and Automation Society, RA-L FAQ. SCI Expanded에 2017년 Vol. 2 No. 1부터 포함된다는 안내.  
[공식 안내](https://www.ieee-ras.org/publications/ra-l/faq/)

**[J2]** DESY Library, *The International Journal of Robotics Research* catalogue. Science Citation Index Expanded/Clarivate Master Journal List 연결 확인.  
[도서관 저널 레코드](https://bib-pubdb1.desy.de/record/12372)

**[J3]** IEEE Access, Bibliometrics—Indexing Information. Science Citation Index Expanded 명시.  
[공식 안내](https://ieeeaccess.ieee.org/about/bibliometrics/)

### 프로젝트 기준 자료

**[P1]** Contact-Rich-Manipulation-Context, AGENTS.md.  
[프로젝트 지침](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/AGENTS.md)

**[P2]** docs/00_HANDOFF_BRIEF.md 및 docs/03_DECISIONS_AND_OPEN_QUESTIONS.md, 기준일 2026-09-14.  
[인계 요약](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/00_HANDOFF_BRIEF.md) · [현재 결정과 미정 사항](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/03_DECISIONS_AND_OPEN_QUESTIONS.md)

**[P3]** docs/04_NEXT_ACTIONS.md, 기준일 2026-09-14.  
[다음 작업](https://github.com/7cmdehdrb/Contact-Rich-Manipulation-Context/blob/main/docs/04_NEXT_ACTIONS.md)

---

**증거 취급:** 논문의 정식 저널 게재 정보와 공개 저자 원문을 연결했다. 공개 원고와 출판본의 판본 차이를 동일한 별도 논문으로 중복 계산하지 않았다. R1–R6은 방법·실험 본문을 확인했으며, R7은 명시한 제한 범위의 인접 참고다. 본 보고서의 센서 결합·실험 설계 제안은 해당 연구실의 실물 장비에서 검증된 결과가 아니다.
