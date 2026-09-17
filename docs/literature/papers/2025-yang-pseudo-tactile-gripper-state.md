# Disambiguate Gripper State in Grasp-Based Tasks — 원문 상세 정리

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 조사 · IROS-S02](../reviews/2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md#iros-s02)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Disambiguate Gripper State in Grasp-Based Tasks: Pseudo-Tactile as Feedback Enables Pure Simulation Learning** |
| 저자 | Yifei Yang, Lu Chen, Zherui Song, Yenan Chen, Wentao Sun, Zhongxiang Zhou, Rong Xiong, Yue Wang |
| 출판 | 2025 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), Hangzhou, China, October 19–25, 2025, pp. 14899–14906 |
| DOI | [10.1109/IROS60139.2025.11246513](https://doi.org/10.1109/IROS60139.2025.11246513) |
| 문헌 관리 식별자 | [IROS 제목 선별 보고서](../reviews/2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md#iros-s02)의 **IROS-S02**. 사용자 임시 선정 목록의 두 번째 논문이며 R1–R7과 별개다. |
| 정리일 | 2026-09-16 |
| 확인한 원문 | 제공된 출판본 PDF 8쪽 전체. 본문 §I–VI, 식 (1), 번호 없는 pose 변환식, Fig. 1–5, Table I–IV, References [1]–[27] |
| 확인하지 않은 자료 | 저자 프로젝트 페이지·보충 영상·코드·설정·체크포인트·원시 데이터, 인용된 선행논문의 개별 원문, 제조사 데이터시트 |
| 원문 PDF SHA-256 | `1cfd60398be38d346147936354116d017f7fafdc026c6df0e917debdd1e49393` |

이 문서는 해당 논문 자체의 문제 상황, Related Works, 환경·센서, 힘·접촉 처리, 학습·제어, 실험, 저자 명시 한계와 향후 연구를 정리한다. 다른 연구의 적용안은 포함하지 않는다. `[원문 §…, PDF p.…]`는 첨부 출판본의 위치이며, **PDF 1–8쪽은 인쇄 페이지 14899–14906**에 대응한다. `[6]` 같은 번호는 원문 참고문헌 번호다. 그림·표·수식은 PDF 렌더링과 대조했으며, 해설용 재구성과 원문에 직접 제시된 내용을 구분한다.

**핵심:** force-controlled gripper의 힘 평형 시 관절각으로 **빈 파지(empty close)**를 검출하고, 저수준 제어기가 정책의 닫기 명령을 덮어써 그리퍼를 실제로 다시 연다. 그러면 정책은 연속 관절각 대신 **파지 결과와 대응하도록 유지된 binary gripper state**를 사용한다. 정책 자체는 RGB 영상·EEF pose·binary gripper state를 받는 **Diffusion Policy 기반 모방학습**이며, 시뮬레이터의 정답 상태를 사용하는 수작업 expert로 생성한 시연에서 학습한다. 별도의 admittance 제어기는 관절 물체의 기구학 오차로 생기는 외력·토크에 대응하여 EEF 궤적을 보정한다. **RL 정책, GAN, 전용 촉각 영상 센서 기반 정책으로 분류하지 않는다.** [원문 §III–IV, Fig. 2–3, PDF pp. 2–5]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 정의·기여와 Related Works |
| 3 | 실험 플랫폼·센서·원문 명시 사양 |
| 4 | pseudo-tactile 정의, 빈 파지 판정과 실제 그리퍼 재개방 |
| 5 | privileged-state expert와 시뮬레이션 시연 생성 |
| 6 | visual/kinematic sim-to-real과 admittance의 힘 처리 |
| 7 | Diffusion Policy 관측·행동·학습 공개 범위 |
| 8–10 | 비교 조건·지표, 전체 정량 결과, ablation |
| 11–13 | 저자 명시 한계·Future Work·미명시 사항과 해석 주의 |
| 14–15 | 원문 위치 안내와 문서 검증 범위 |

## 1. 제시하는 문제 상황

### 1.1 닫힌 그리퍼가 반드시 성공한 파지를 의미하지 않는다

논문의 대상은 **pick-and-lift, drawer-opening, oven-opening**이다. 물체를 집어 올리거나 손잡이를 잡아 당기는 작업에서는, 파지가 성공했는지에 따라 다음 행동이 달라져야 한다. 실패했다면 재시도해야 하고, 성공했다면 lift 또는 pull로 진행해야 한다. [원문 §I, §III, §V-A, PDF pp. 1–3, 6]

하지만 성공 시연을 주로 학습한 imitation learning 정책은 **그리퍼가 닫혔다는 관측과 파지 성공을 강하게 연결**할 수 있다. 실제로는 물체가 미끄러졌거나 손잡이를 잡기 전에 그리퍼가 닫힐 수 있다. 그때 정책이 닫힘만 보고 post-grasp 행동을 출력하면, 아무것도 잡지 않은 채 당기거나 들어 올린다. Fig. 1(a)는 세 과업에서 이런 동작을 보여 준다. [원문 §I·III, Fig. 1, PDF pp. 1–3]

실험에서 사용하는 외란은 **grasping 단계의 서로 다른 시점에 그리퍼를 강제로 닫는 것**이다. 운반 중 slip과 손잡이 이탈은 문제의 동기이며, 실험의 직접적인 외란 프로토콜은 강제 닫기다. 두 가지를 모두 별도로 정량 검증했다고 확대하지 않는다. [원문 §I, §V-A, PDF pp. 1, 6]

### 1.2 grasp state와 gripper state observation의 구분

원문은 다음을 명시적으로 구분한다.

| 용어 | 의미 | 제어에서 필요한 역할 |
| --- | --- | --- |
| Grasp state | 물체를 실제로 파지했는지에 관한 상태 | 재파지와 post-grasp 진행의 판단 기준 |
| Gripper state observation | 그 상태를 판단하려고 정책이 사용하는 관측 | 원래 binary 표현은 열린 상태 0, 닫힌 상태 1 |
| Gripper state ambiguity | 실제 파지 상태가 달라도 같은 닫힘 관측이 나타나는 문제 | empty close와 grasp close를 구분하지 못함 |

Fig. 1(b)의 대응을 정리하면 다음과 같다. 마지막 열은 제안 제어를 거친 관측의 의미를 나타내며, 아래에서 설명하듯 단순한 숫자 치환만이 아니라 **물리적 재개방**을 수반한다. [원문 §III–IV-A, Fig. 1(b)·2, PDF pp. 1–4]

| 실제 상황 | 파지 정답 상태 | 기존 binary 관측 | pseudo-tactile feedback을 적용한 대응 |
| --- | ---: | ---: | --- |
| Empty open | 0 | 0 | 열린 상태로 0 |
| Empty close | 0 | 1 | 다시 열어 empty open으로 전환, 0 |
| Grasp close | 1 | 1 | 파지한 닫힘 상태 유지, 1 |

### 1.3 저자들이 설명하는 원인: 시연자와 정책의 피드백 불일치

저자들은 사람이 teleoperation으로 시연할 때는 촉각 등 피드백으로 파지를 확인하지만, 학습 정책에는 그 피드백이 빠진다고 설명한다. 정책에는 이전 제어 명령에 의존하는 **feedforward binary gripper state**가 남고, 시연 중에는 닫힘과 파지 성공이 일치하므로 이 관계에 과적합한다는 해석이다. 이는 논문이 제시하는 원인 분석이며, 사람의 감각 사용을 별도로 측정한 실험은 아니다. [원문 §I·III, PDF pp. 2–3]

### 1.4 더 많은 데이터·연속 관절각만으로 해결하기 어려운 이유

연속 gripper joint angle을 관측하고 다양한 파지 실패를 학습하면 도움이 될 수 있지만, 저자들은 두 비용을 지적한다. 첫째, 실제 teleoperation 중 의도적으로 실패를 만들고 복구시키는 작업은 자연스러운 데이터 수집을 방해하고 인력이 많이 든다. 둘째, 시뮬레이션에서는 asset의 형상 오차와 물리 엔진의 interpenetration 때문에 같은 물체를 잡아도 실물과 관절각이 달라질 수 있다. [원문 §I, §IV-B, PDF pp. 1, 4]

따라서 연구는 **실패를 모두 학습 데이터에 추가하거나 연속 관측을 늘리는 대신, 하위 제어를 통해 binary 관측의 의미가 유지되게 할 수 있는가**를 다룬다. 저자들의 기여는 pseudo-tactile feedback, 이 피드백을 전제로 한 pure simulation policy learning, 세 실물 과업의 검증으로 구성된다. [원문 §I, PDF p. 2]

## 2. Related Works — 원문의 비교 구도

이 절은 원문 §II의 분류와 설명을 정리한 것이다. 아래 선행논문을 이번 작업에서 개별 정독하거나 구현을 재검증한 것은 아니다.

### 2.1 Imitation Learning for Grasp-Based Manipulation

| 관련 연구 축 | 원문에서 든 예 | 이 논문이 구성한 비교 |
| --- | --- | --- |
| 정책 구조 | ACT [5], Diffusion Policy [6] | action sequence·multimodal action 표현의 발전과 gripper 상태의 모호성을 구분 |
| 관측 표현 확장 | 3D perception [8], language [9]·[10], audio [11] | 관측 표현력을 높이는 방향과 피드백 부재를 하위 제어로 해결하는 방향의 차이 |
| 파지 기반 조작 적용 | pick-and-place [12]·[13], assembly [13]·[14], articulated manipulation [15]·[16] | 파지 성공 판정이 다양한 후속 조작의 공통 문제임을 설명 |
| 대규모 VLA·데이터 | [9]·[10]·[17]–[20], OXE [21], DROID [22] | 대규모 학습의 일반화 가능성을 인정하되 실제 데이터 비용과 sim-to-real을 문제로 제시 |

저자들은 ACT·DP를 새로 대체하는 구조를 제안하기보다 **그 정책들이 사용하는 gripper observation이 실제 grasp state와 일치하는지**를 문제 삼는다. 실험에는 DP, ACT, RDT-1B의 비교가 포함되지만, 모든 VLA나 모든 IL 구조에 대해 보편적인 우열을 입증하는 실험은 아니다. [원문 §II-A, §V, PDF pp. 2, 6–8]

### 2.2 Manipulation with Tactile

원문은 Lin et al. [23]의 두 multifingered hand용 visuotactile 학습과 Huang et al. [24]의 unified 3D visual–tactile 표현을 설명한다. 촉각이 조작에 유용하다는 점을 인정하면서, 전용 센서를 추가하면 비용·통합·calibration·실시간 처리 부담이 생긴다는 점을 비교 근거로 든다. [원문 §I·II-B, PDF p. 2]

본 논문의 대안은 **이미 force control이 가능한 두 손가락 그리퍼의 관절각을 pseudo-tactile로 사용하는 것**이다. 고해상도 촉각이 제공하는 접촉 위치·분포·전단을 모두 대체한다는 주장이 아니라, 이 연구에서 필요한 **빈 파지와 파지한 닫힘의 구분**을 위한 피드백이다. [원문 §IV-A, PDF pp. 3–4]

## 3. 환경·로봇 플랫폼·센서 상세 사양

### 3.1 실물 구성과 실제 사용 정보

| 구성 | 원문에 명시된 내용 | 논문에서의 역할·사양 구분 |
| --- | --- | --- |
| 매니퓰레이터 | Universal Robots **UR5** | EEF 6DoF pose를 관측하고 명령. UR5e로 바꾸어 기록하지 않음 |
| 그리퍼 | **Robotiq 2F-85** | force-controlled two-finger gripper로 설명하며, 힘 평형 시 관절각을 pseudo-tactile로 사용 |
| 외부 카메라 | **Intel RealSense D435i** | RGB 관측을 제공. 제안 정책의 입력은 third-view RGB 320×240 |
| 전용 tactile sensor | 추가 하드웨어 없이 pseudo-tactile을 사용한다고 명시 | 촉각 영상·taxel array를 정책에 입력하는 구성이 아님 |
| 외력·토크 정보 | admittance가 외부 force/torque를 사용한다고 명시 | 측정·추정 장치, 센서 모델과 설치 위치는 미명시 |
| 실제 시연 수집 | Touch teleoperation system | 실물 학습 baseline의 데이터 수집. UMI는 Introduction의 예시이며 실험 장치를 UMI로 바꾸지 않음 |
| 시뮬레이션 | Isaac Sim | 단순 asset 모델링·텍스처와 복잡한 asset 재구성, 상태 기반 expert 시연 생성 |
| 수집 계산 장비 | 단일 GeForce RTX 4060 Ti | oven demo 1,000개를 2시간에 수집한 예. 정책 최적화 시간·하드웨어 전체 사양과 구분 |

[원문 §IV-B·C, §V-A, PDF pp. 4–6]

### 3.2 원문에 없는 하드웨어 수치를 다른 출처로 채우지 않는다

| 확인 항목 | 이 원문에서 확인되는 수준 |
| --- | --- |
| UR5 가반하중·reach·반복정밀도·최대 속도 | 수치 미명시 |
| 2F-85 최대 opening·관절 가동 범위·위치 분해능 | 수치 미명시. 제품명의 숫자를 본문의 측정 사양으로 전환하지 않음 |
| 그리퍼 최대 파지력·힘 측정 범위·힘 분해능·최소 감지력 | 미명시 |
| force threshold와 position threshold | Fig. 2에 명칭이 있으나 수치·단위·설정 방법 미명시 |
| 힘 평형 도달 판정·관절각 필터·debounce | 미명시 |
| 그리퍼·외력 센서의 샘플링률·대역폭·지연 | 미명시 |
| D435i의 최대 영상 해상도·FPS·깊이 정확도 | 미명시. 320×240은 정책에 사용하는 RGB 입력 크기 |
| 전용 F/T sensor의 존재 여부와 사양 | Hardware 항목에서 특정 모델을 명시하지 않음. admittance 식만으로 손목 F/T 장착을 확정할 수 없음 |
| 손끝 압력 분포·접촉 위치의 공간 해상도 | 그러한 센서 출력이나 추정 모듈을 제시하지 않음 |

카메라 모델에 depth·IMU 기능이 있더라도 **정책 입력으로 그 기능을 사용했다고 해석하지 않는다.** 원문이 명시한 제안 정책의 시각 관측은 RGB다. [원문 §IV-C·V-A, PDF pp. 5–6]

### 3.3 과업과 물체 환경

| 과업 | 물체의 운동 성격 | 시연 expert의 post-grasp 동작 |
| --- | --- | --- |
| Pick-and-lift | 자유 물체를 잡아 들어 올림 | 파지 지점에서 EEF를 수직 위로 이동 |
| Drawer-opening | 서랍의 구속된 병진 운동 | cabinet에 수직인 방향으로 뒤로 당김 |
| Oven-opening | 회전 관절이 있는 문 | 문 pose에 따라 아래로 당기는 방향을 바꾸며 근사 원호를 따름 |

원문은 자유 물체와 articulated object를 함께 평가한다. 물체·손잡이의 정량 치수, 질량, 마찰계수, 관절 저항, train/test 형상 목록은 제시하지 않는다. 사진에서 대략적인 외형을 볼 수 있다는 사실과 수치 사양이 보고되었다는 사실을 구분한다. [원문 §IV-B·V-A, Fig. 4–5, PDF pp. 4–6]

## 4. 상세 핵심 메소드 I — Pseudo-Tactile Feedback

### 4.1 pseudo-tactile이 의미하는 물리적 정보

원문은 촉각 센서의 작동을 **물체와 접촉해 힘 평형에 도달했을 때, 변형이 저항·정전용량·영상 등의 측정 변화로 나타나는 것**으로 설명한다. 이에 대응하여 force-controlled gripper의 두 finger를 deformable material로 보고, 그 상태에서의 **gripper joint angle**을 측정 가능한 pseudo-tactile 정보로 해석한다. Fig. 2 상단이 이 비유를 도식화한다. [원문 §I·IV-A, Fig. 2, PDF pp. 2–3]

이 논문에는 관절각을 N 단위 힘으로 변환하는 calibration 식이나, 관절각에서 접촉 wrench를 학습하는 회귀기가 없다. 실제 활용은 **닫힘을 시도한 그리퍼가 물체에 막혀 파지를 유지하는지, 물체 없이 최대 닫힘까지 도달했는지**의 구분이다. 관절각으로 손가락 재료의 탄성 변형량을 별도로 복원했다고도 쓰지 않는다. [원문 §IV-A, PDF pp. 3–4]

### 4.2 Fig. 2의 force loop와 position loop

Fig. 2 하단은 **Force Controller–Force Threshold**와 **Position Controller–Position Threshold**의 두 경로를 표시한다. force feedback은 힘 제어와 연결되고, joint angle이 pseudo-tactile로 position threshold 쪽에 들어간다. 도식에 제어 블록이 있다는 사실을 기록하되, 본문에는 내부 force-control law, 힘을 읽는 방법, 임계값, 전환 timing의 수식이나 코드가 없다. [원문 Fig. 2·§IV-A, PDF pp. 3–4]

따라서 원문으로 재구성할 수 있는 수준은 **힘 제어가 성립하는 그리퍼의 관절 상태를 이용한 규칙 기반 supervision**이다. 이를 PID gain을 포함한 완전한 force/position hybrid controller 구현으로 제시하지 않는다.

### 4.3 빈 파지 검출과 명령 override

저자들의 명시적 규칙은 다음과 같다. **그리퍼가 닫혔지만 관절각이 최대값에 도달하여 물체를 잡지 못했다고 판정하면, 상위 정책의 명령을 덮어쓰고 그리퍼를 강제로 연다.** 이 동작으로 empty close를 empty open으로 바꾼다. [원문 §IV-A, PDF p. 4]

```text
[원문 설명을 재구성한 동작 흐름 — 실행 코드가 아님]

상위 정책이 그리퍼 닫힘을 명령
  → force-controlled gripper의 관절 상태 확인
  → 힘 평형 시의 관절각을 pseudo-tactile 정보로 사용

빈 파지: 관절각이 원문에서 정의한 최대 닫힘에 도달
  → low-level controller가 상위 닫기 명령을 override
  → 실제 그리퍼를 다시 열어 empty open으로 전환
  → 정책은 열린 gripper state를 관측하고 파지를 다시 시도

물체를 잡고 닫힌 상태
  → grasp close를 유지
  → binary closed observation으로 post-grasp 행동 가능
```

여기서 ‘최대 관절각’은 **원문이 설명한 닫힘 기준**이다. 실제 SDK의 register 값, rad/deg 값, 모든 gripper의 좌표 부호에 관한 일반 사양이 아니다. threshold tolerance·상태 확인 주기·재시도 횟수·열림을 유지하는 시간은 미명시다. [원문 §IV-A, Fig. 2, PDF pp. 3–4]

### 4.4 중요한 점: 관측만 바꾸는 것이 아니라 물리적 상태를 바꾼다

이 방법을 “빈 파지를 감지하면 binary 1을 0으로 재라벨링한다”로만 요약하면 핵심 행동을 빠뜨린다. 원문에서는 **그리퍼를 실제로 여는 조치**가 들어간다. 그 결과 재시도에 적합한 empty open 상태로 되돌아가고, 정책이 시연에서 배운 open→grasp→post-grasp 흐름을 다시 사용할 수 있게 한다. [원문 §IV-A, Fig. 2–3, PDF pp. 3–4]

반대로 상위 정책이 pseudo-tactile의 연속 신호를 직접 보고 복구 행동을 새로 학습한 것으로도 해석하지 않는다. **빈 파지 판정과 재개방은 수작업 저수준 규칙**이고, 이후 EEF 이동·다음 파지 시도는 모방학습 정책의 실행이다. arm을 동시에 정지시키는 별도 조건이나 action chunk를 취소하는 구현은 원문에 없다.

### 4.5 왜 binary 표현이 sim-to-real에 도움이 되는가

같은 물체를 잡았을 때 시뮬레이션과 실물의 관절각 수치가 달라도, 두 환경의 관측이 **열림/파지한 닫힘이라는 같은 의미의 binary 값**으로 유지되면 정책이 그 연속 수치 차이를 학습할 필요가 줄어든다. 제안 방식은 empty close를 제거하는 제어 조치와 binary 표현을 함께 사용한다. 단순하게 기존 관절각을 임계값으로 이산화하기만 한 방법과 다르다. [원문 §IV-B, Fig. 3, PDF p. 4]

저자들이 반복해서 사용하는 **noise-free binary gripper state**는 이 방식의 관측 표현을 지칭한다. 원문은 센서 노이즈가 물리적으로 0이라는 실측, 모든 물체에서 오검출률이 0이라는 결과, binary 신호의 완전한 검출 성능을 제시하지 않는다. 카메라와 기구학의 sim-to-real 문제도 별도로 다룬다. [원문 §IV–V, PDF pp. 4–8]

### 4.6 정보가 사용되는 위치

| 정보 | 사용하는 모듈 | 정책에 직접 들어가는가? |
| --- | --- | --- |
| 힘 평형 시 gripper joint angle | pseudo-tactile gripper controller | 제안 정책의 연속 관측에는 포함하지 않음 |
| Binary gripper state | 학습 정책의 관측·행동 | 포함 |
| RGB 영상 | Diffusion Policy | 포함. 초기 한 번만 사용하는 조건이 아님 |
| EEF 6DoF pose | Diffusion Policy | 포함 |
| 외부 force/torque | admittance controller | §IV-C의 정책 입력 목록에는 없음 |
| 시뮬레이터의 물체 pose·joint state | expert trajectory 생성·rollout 성공 판정 | learned policy의 입력과 구분 |

[원문 §IV-A–C, Fig. 3, PDF pp. 3–5]

## 5. 상세 핵심 메소드 II — Pure Simulation 시연 생성

### 5.1 RL이 아니라 상태 기반 expert를 모방한다

학습 데이터는 시뮬레이션의 privileged state를 읽는 **수작업 expert policy**가 만든다. 이 expert는 학습된 critic이나 RL teacher가 아니라, key pose와 단계별 운동 규칙을 사용하는 시연 생성기다. 생성된 시연을 이용한 supervised imitation learning으로 Diffusion Policy를 학습한다. [원문 §IV-B·C, Fig. 3, PDF pp. 4–5]

### 5.2 pre-grasp와 grasp의 object-centric key pose

세 과업을 **pre-grasp, grasp, post-grasp**로 분리한다. pre-grasp와 grasp에는 각각 하나의 object-centric key pose를 사람이 정의한다. 시뮬레이터가 주는 물체의 world pose와 결합하여 EEF의 목표 world pose를 계산한다. [원문 §IV-B, PDF p. 4]

**원문의 번호 없는 pose 변환식:**

$$
T_{WE}=T_{WO}T_{OK}.
$$

| 기호 | 원문에서의 의미 |
| --- | --- |
| $T_{WO}$ | simulator로부터 얻은 관심 물체의 world pose |
| $T_{OK}$ | 사람이 정의한 object-centric key pose |
| $T_{WE}$ | EEF가 도달할 world-frame target pose |

이후 현재 pose에서 target pose까지 interpolation으로 경로를 생성한다. 저자들은 이 단순 보간이 자신의 randomization 중 **90% 이상에 대응**했다고 설명한다. 정확한 randomization 범위·분모, 보간의 회전 표현, 속도 profile, 실패 사례는 미제시다. 이 수치를 임의의 장면에서의 90% 계획 성공률로 확대하지 않는다. [원문 §IV-B, PDF p. 4]

### 5.3 post-grasp는 물체의 기구학을 따르는 규칙

Pick-and-lift는 수직 상승, drawer는 cabinet에 수직인 당김, oven은 문 pose에 따라 방향을 조정하는 근사 원호를 사용한다. 특히 oven의 동적 문 pose는 **simulator의 상태에 접근하는 expert가 시연을 생성할 때 사용하는 정보**다. 실물 learned policy가 정답 hinge pose나 현재 door pose를 별도 입력으로 받는다는 뜻이 아니다. [원문 §IV-B·C, PDF pp. 4–5]

원문은 세 단계의 동작 의미를 밝히지만, 단계별 key pose 수치·전환 threshold·opening angle 또는 lifting height의 목표값은 제공하지 않는다.

### 5.4 rollout 판정·성공 시연의 선별

물체 pose 또는 joint angle을 모니터링하여 rollout 완료를 자동 판정하고, **성공한 rollout만 demonstration으로 보존**한다. 제안 방법의 기본 데이터 생성에서는 gripper disturbance를 넣지 않는다. Fig. 3의 기본 시연 집합은 empty close와 successful grasp가 섞여 들어오는 관측 모호성이 없는 구도로 설명된다. [원문 §IV-B, Fig. 3, PDF p. 4]

후술하는 Table IV의 gripper-randomization dataset은 별도 ablation 조건이다. 이를 제안 방법의 기본 데이터 생성에 섞거나, 기본 방법이 실패 복구 시연을 필수로 수집한다고 쓰지 않는다.

### 5.5 randomization의 범위

| 원문에서 명시한 항목 | 역할 | 공개 수준 |
| --- | --- | --- |
| Object pose | 서로 다른 물체 배치의 시연 | 범위·분포 수치 미명시 |
| Robot pose | 로봇 시작 조건의 다양화 | 관절/EEF randomization의 상세 인코딩 미명시 |
| Lighting | 시각 domain 차이 완화 | 광원 수·밝기·분포 미명시 |
| Texture | 시각 외형 다양화 | texture pool·샘플링 규칙 미명시 |
| Gripper disturbance | 제안 기본 데이터에서는 사용하지 않음 | ablation에서 empty grasp 사례를 추가 |
| Mass·friction·force noise | 기본 randomization 항목으로 제시하지 않음 | 사용했다고 가정하지 않음 |

[원문 §IV-B, Fig. 3, §V-C, PDF pp. 4–5, 7]

### 5.6 수집량·시간: 방법 설명의 예와 본 실험 데이터

| 구분 | 실물 teleoperation | Simulation |
| --- | --- | --- |
| §IV-B의 oven 수집 예시 | 약 3시간에 약 50개 | RTX 4060 Ti 1대로 2시간에 1,000개 |
| §V-A: pick-and-lift | 50개 | 2,000개 |
| §V-A: drawer-opening | 60개 | 2,000개 |
| §V-A: oven-opening | 54개 | 2,000개 |
| §V-A의 수집 시간 설명 | 과업당 약 3–4시간 | 유사한 시간에 과업당 2,000개 |

방법 설명의 1,000개 예시를 최종 실험의 학습량으로 바꾸지 않는다. 또한 위 시간은 **시연 수집 시간**이지 DP network의 training time이 아니다. [원문 §IV-B·V-A, PDF pp. 4, 6]

저자들은 simulation setup과 expert 작성에는 사람의 작업이 필요하다고 인정한다. 이후 수집은 자동화되므로 데이터량 증가에 비례하여 사람의 개입을 늘리지 않아도 된다는 장점이다. **Pure simulation learning은 환경 구축까지 자동이거나, 현실 물체에 관한 정보가 전혀 필요 없다는 뜻이 아니다.** [원문 §IV-B, PDF pp. 4–5]

### 5.7 DAgger·multi-GPU는 사용 실적과 구분

원문은 simulation의 장점으로 **DAgger와 같은 on-policy data collection**, 더 많은 GPU를 이용한 수집 가속을 언급한다. 그러나 본 실험에서 DAgger를 실제 적용한 횟수·절차, multi-GPU 실험 결과를 제시하지 않는다. 이 가능성 언급을 실제 학습 pipeline에 포함시켜 기록하지 않는다. 더 고급 planner를 사용할 수 있다는 문장도 동일하게 구분한다. [원문 §IV-B, PDF pp. 4–5]

## 6. 상세 핵심 메소드 III — Sim-to-Real과 Admittance의 힘 처리

### 6.1 시각적 차이: asset 구축과 randomization

단순한 geometry·texture의 물체는 3D modeling software로 형상을 만들고 Isaac Sim에서 texture를 적용한다. 더 복잡한 oven은 **3D reconstruction으로 textured mesh를 만들고 articulation을 추가**한다. 여기에 pose·lighting·texture randomization을 적용해 visual sim-to-real gap에 대응한다. [원문 §IV-B, PDF p. 5]

Fig. 3의 real-to-sim techniques는 이 현실 물체에 대응하는 simulation asset 구축과 연결해서 읽어야 한다. 본 논문은 real image를 sim image로 바꾸는 GAN을 제시하지 않으며, generator·discriminator·paired image dataset·GAN loss도 없다. **Diffusion Policy의 action 생성과 GAN 기반 image translation은 다른 내용**이다.

### 6.2 기구학적 차이: 잡은 뒤 궤적이 실제 관절축과 맞지 않는 문제

회전 관절 물체에서 simulator와 실제 물체의 joint-axis 위치가 다르면, 정책이 출력한 궤적이 실제 물체의 구속 운동과 어긋날 수 있다. 저자들은 이것이 과도한 stress를 만들어 emergency stop과 실패를 일으킨다고 설명한다. pseudo-tactile은 파지 상태의 모호성을 줄이지만 이 기구학 오차까지 제거하지 않으므로, **admittance를 추가하여 EEF 궤적에 순응성을 부여**한다. [원문 §IV-B, PDF p. 5]

### 6.3 원문 admittance 식과 변수

**원문 식 (1):**

$$
M(\ddot{x}_c-\ddot{x}_d)
+D(\dot{x}_c-\dot{x}_d)
+K(x_c-x_d)
=F_{\mathrm{ext}}.
$$

| 기호 | 원문 설명 |
| --- | --- |
| $x_d,\dot{x}_d,\ddot{x}_d$ | policy output의 목표 궤적과 그 속도·가속도 |
| $x_c,\dot{x}_c,\ddot{x}_c$ | admittance로 조정된 궤적과 그 속도·가속도 |
| $F_{\mathrm{ext}}$ | 외부 force and torque를 나타내는 입력 |
| $M$ | mass matrix |
| $D$ | damping matrix |
| $K$ | stiffness matrix |

원문은 force와 torque를 모두 설명하지만, $x$의 구체적인 pose parameterization, 회전 오차 정의, 행렬 차원·각 축 계수, wrench 좌표계는 명시하지 않는다. 이를 임의의 6×6 diagonal matrix나 특정 SE(3) 제어 구현으로 확정하지 않는다. [원문 §IV-B, 식 (1), PDF p. 5]

### 6.4 측정 힘이 실제 EEF 보정으로 연결되는 방식

다음은 **원문 식 (1)의 대수적 해설**이다. 궤적 correction을 $e=x_c-x_d$로 놓으면,

$$
M\ddot{e}+D\dot{e}+Ke=F_{\mathrm{ext}}.
$$

즉, 외부 force/torque에 대해 보정량의 관성·감쇠·복원 성질을 설정하고, 그 보정량을 목표 pose에 반영한다. 이 구조는 force/torque를 신경망 feature로 붙이는 대신 **policy 이후의 controller에서 motion correction으로 변환**하는 것이다. [원문 §IV-B·Fig. 3의 해설, PDF pp. 4–5]

정상상태에서 보정량의 속도·가속도가 0이고 $K$가 가역이라는 조건을 추가하면,

$$
e=K^{-1}F_{\mathrm{ext}}.
$$

이는 원문이 spring에 비유한 설명을 해석하기 위한 조건부 관계다. 저자들이 이 식으로 gain을 선정했다거나 이 정상상태를 측정했다는 보고는 아니다. 외력이 없을 때 목표 궤적을 따르는 의도 역시 correction의 동적 과도응답까지 즉시 0이라는 의미로 확대하지 않는다.

### 6.5 gripper feedback과 admittance는 다른 두 제어 경로다

| 구분 | Pseudo-tactile gripper controller | Admittance controller |
| --- | --- | --- |
| 해결 문제 | Empty close가 성공한 파지처럼 관측됨 | 기구학 오차가 구속 물체와 과도한 상호작용을 만듦 |
| 핵심 입력 | force-controlled gripper의 힘 평형 시 관절각 | 외부 force/torque와 목표 EEF 궤적 |
| 출력 | 정책의 gripper command를 override한 열기 명령 | 수정된 EEF 궤적 |
| 행동 결과 | 빈 파지에서 재개방·재시도 가능 | 실제 접촉 구속에 순응 |
| 정책에 직접 힘 입력 추가 | 하지 않음 | 정책 입력 목록에 없음 |
| 세부 공개 수준 | 규칙·Fig. 2, 수치 설정 없음 | 식 (1), gain·신호 처리·이산 구현 없음 |

[원문 §IV-A–C, Fig. 2–3, PDF pp. 3–5]

### 6.6 힘 처리에서 확인할 수 없는 부분

원문에는 $F_{\mathrm{ext}}$의 측정·추정 출처, 영점/중력 보상, 필터, 좌표 변환, sampling rate, correction saturation, emergency stop threshold가 없다. **Admittance가 필요하다는 설명과 식이 있다는 사실만으로 전용 손목 F/T 센서나 구체적인 힘 제어 성능을 채워 넣지 않는다.** 또한 admittance를 제거한 별도 정량 ablation은 Table IV에 없다. [원문 §IV-B·V-A·V-C, PDF pp. 5–7]

## 7. 상세 핵심 메소드 IV — Diffusion Policy 학습·실행

### 7.1 관측과 행동

저자들은 multimodal action 표현과 training stability를 이유로 **Diffusion Policy(DP) [6]**를 선택한다. 제안 정책의 입력과 출력은 다음과 같다. [원문 §IV-C, PDF p. 5]

| 구분 | 명시된 구성 | 원문이 밝히지 않은 세부 |
| --- | --- | --- |
| 시각 입력 | Third-view RGB, 320×240 | crop·normalization·augmentation 세부, camera FPS |
| 로봇 입력 | EEF 6DoF pose | 좌표계·회전 인코딩·정규화 |
| 그리퍼 입력 | Binary gripper state | 수신 timing·관측 생성의 코드 경로 |
| 팔 행동 | EEF 6DoF pose | absolute/relative 구현 구분, interpolation·실행 horizon |
| 그리퍼 행동 | Binary gripper state | 출력의 threshold·command 변환 세부 |
| 저수준 처리 | EEF pose는 admittance, gripper command는 pseudo-tactile controller | 두 루프의 주기·동기화·override 중 arm 처리 |

‘6DoF pose + binary’라고 해서 곧바로 scalar 7차원 vector로 확정할 수는 없다. 회전 표현이 명시되지 않았고 DP의 observation/action horizon도 없기 때문이다. EEF pose와 gripper state를 사용하는 조건만 원문대로 기록한다.

### 7.2 DDIM 설정과 학습 공개 범위

| 항목 | 본문에 명시된 내용 |
| --- | --- |
| 학습 패러다임 | Expert demonstration을 이용한 imitation learning |
| 제안 모델 | Diffusion Policy |
| Noise scheduler | DDIM [27] |
| Training diffusion steps | 100 |
| Inference diffusion steps | 16 |
| 시연 데이터 | 과업별 simulation demonstration 2,000개 |
| RL reward·return·PPO 설정 | 해당 방법이 RL이 아니므로 제시하지 않음 |
| DP loss의 명시적 수식 | 본문에 없음. 일반 DP 논문의 식을 이 논문의 구현식으로 보충하지 않음 |
| Architecture 상세·optimizer·learning rate·batch size·epoch | 미명시 |
| Observation/prediction/action horizon·inference rate | 미명시 |
| Checkpoint 선택·train/validation split·seed 수 | 미명시 |

**100/16은 diffusion process의 step 설정이지, epoch 수나 robot rollout 길이, 제어 주파수가 아니다.** 데이터 수집용 GPU와 수집 시간을 network training 성능으로 바꾸어 쓰지 않는다. [원문 §IV-C·V-A, PDF pp. 5–6]

### 7.3 학습에서 실제 동작까지의 전체 연결

```text
[학습]
Isaac Sim의 object pose / joint state
  → 사람이 정의한 key pose + 단계별 expert motion
  → pose·lighting·texture randomization
  → 성공 rollout만 시연 데이터로 보존
  → RGB + EEF pose + binary gripper state에서 DP 학습

[실행]
실물 RGB + EEF pose + binary gripper state
  → Diffusion Policy
      ├─ EEF pose → 외력·토크 기반 admittance → 팔 운동
      └─ gripper command → pseudo-tactile 규칙 → 실제 gripper 운동
                                        ↓
                              빈 파지이면 강제 재개방
                                        ↓
                         변경된 상태를 다음 정책 관측에 반영
```

이 흐름은 Fig. 3과 §IV의 설명을 재구성한 것이다. **Privileged object state는 expert의 정보이며, 학습된 정책에 실물에서 그대로 제공되는 것이 아니다.** 반대로 정책에는 외부 RGB가 계속 입력되므로 외부 시각 없는 tactile-only 제어로도 분류하지 않는다. [원문 Fig. 3·§IV-B–C, PDF pp. 4–5]

## 8. 실험 설계와 평가 지표

### 8.1 실험 질문

§V는 네 가지 질문을 제시한다. pseudo-tactile이 gripper disturbance에 강인하게 만드는지, simulation으로 학습한 시스템이 real demonstration baseline과 비교해 어떻게 동작하는지, simulation data 확장이나 architecture 변경만으로 모호성을 해결할 수 있는지, 대규모 사전학습 VLA를 fine-tuning하면 해결되는지를 평가한다. [원문 §V, PDF p. 6]

### 8.2 baseline 조건

| 방법 | 학습 데이터 | 본문에서 명시한 특징 |
| --- | --- | --- |
| DP-Real | 실물 teleoperation | Continuous gripper joint angle을 관측 |
| ACT-Real | 실물 teleoperation | RGB 640×480 |
| RDT-1B-Real | 실물 teleoperation으로 fine-tuning | RGB 1280×720, continuous gripper joint angle 관측 |
| Ours | Simulation | RGB 320×240·binary state를 받는 DP와 pseudo-tactile feedback |

DP-Real의 영상 크기와 ACT-Real의 gripper 관측 표현을 이 baseline 설명에서 따로 확정하지 않는다. 저자들은 세 baseline의 architecture와 hyperparameter가 다르다고 명시한다. **데이터 출처·양·모델·영상 크기·gripper 표현이 모두 통제된 비교가 아니므로, 전체 성능 차이를 pseudo-tactile 하나의 효과로만 읽지 않는다.** 보다 가까운 비교는 Table IV의 ablation이다. [원문 §V-A·C, PDF pp. 6–7]

### 8.3 시험 횟수와 외란

과업별로 실물 rollout 20회를 수행하며 object pose와 robot initial pose를 무작위화한다. 이 중 10회는 grasping 단계의 서로 다른 시점에 gripper를 강제로 닫는다. 원문은 pose 분포, 강제 닫기 시점의 분포, retry 제한·timeout의 정확한 값을 제시하지 않는다. 각 방법의 비교율은 이 과업별 20회 프로토콜을 바탕으로 읽는다. [원문 §V-A, PDF p. 6]

### 8.4 task·grasp·resilience를 따로 평가한다

| 지표 | 의미 | 주의 |
| --- | --- | --- |
| SR-ND | Gripper disturbance가 없는 task 성공률 | 자연적으로 발생한 정책 오류가 전혀 없다는 뜻은 아님 |
| SR-D | Gripper disturbance를 가한 task 성공률 | 강제 닫기 프로토콜의 결과 |
| SR | 전체 task 성공률 | ND/D의 전체 20회 기준 |
| AT | Task completion 평균 시간 | §V-C에서 **성공한 rollout만 계산**한다고 설명 |
| SR-R | Disturbance resilience 성공률 | 짧은 시간 안에 다시 열고 파지를 재시도하면 성공. 전체 task 완료는 요구하지 않음 |
| GSR-ND | 외란 없는 grasp 성공률 | Post-grasp까지 성공했다는 뜻은 아님 |
| GSR-D | 외란 있는 grasp 성공률 | 파지 단계만 평가 |
| GSR | 전체 grasp 성공률 | Task SR와 분리 |

‘짧은 시간’의 수치, grasp 성공의 세부 판정, lift 높이·drawer 이동 거리·oven 목표 각도와 같은 task 성공 threshold는 미명시다. 원문에 정의된 평가 항목을 넘어서 임의의 성공 조건을 만들지 않는다. [원문 §V-A·C, PDF pp. 6–7]

## 9. 실물 비교 결과 — Table I–III 전체 수치

아래는 원문의 열을 **task 성능**과 **grasp·resilience**로 나누어 옮긴 표다. 성공률은 %, AT만 s다. `—`는 원문에서 시간을 제시하지 않은 경우다. 수치는 재현 실험 결과가 아니라 논문 보고값이다. [원문 Table I–III, PDF p. 6]

### 9.1 Task 성공률·수행 시간

| 과업 | 방법 | SR-ND (%) | SR-D (%) | SR (%) | AT (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| Pick-and-lift | DP-Real | 20 | 0 | 10 | 18.5 |
| Pick-and-lift | RDT-1B-Real | 30 | 10 | 20 | 27.0 |
| Pick-and-lift | Ours | 100 | 80 | 90 | 16.3 |
| Drawer-opening | ACT-Real | 0 | 0 | 0 | — |
| Drawer-opening | DP-Real | 50 | 0 | 25 | 24.6 |
| Drawer-opening | RDT-1B-Real | 50 | 30 | 40 | 28.0 |
| Drawer-opening | Ours | 100 | 80 | 90 | 18.0 |
| Oven-opening | ACT-Real | 50 | 20 | 35 | 34.7 |
| Oven-opening | DP-Real | 60 | 20 | 40 | 68.5 |
| Oven-opening | RDT-1B-Real | 60 | 30 | 45 | 44.4 |
| Oven-opening | Ours | 70 | 90 | 80 | 26.7 |

**Table I에는 ACT-Real의 pick-and-lift 결과 행이 없다.** 결과를 0으로 채우거나 실험하지 않은 이유를 추정하지 않는다. Oven의 Ours에서 SR-D 90%가 SR-ND 70%보다 높게 보고된 순서도 그대로 유지한다.

### 9.2 Grasp 성공률·외란 복구 성공률

| 과업 | 방법 | SR-R (%) | GSR-ND (%) | GSR-D (%) | GSR (%) |
| --- | --- | ---: | ---: | ---: | ---: |
| Pick-and-lift | DP-Real | 10 | 20 | 0 | 10 |
| Pick-and-lift | RDT-1B-Real | 70 | 40 | 10 | 25 |
| Pick-and-lift | Ours | 100 | 100 | 80 | 90 |
| Drawer-opening | ACT-Real | 30 | 0 | 0 | 0 |
| Drawer-opening | DP-Real | 20 | 50 | 0 | 25 |
| Drawer-opening | RDT-1B-Real | 30 | 50 | 30 | 40 |
| Drawer-opening | Ours | 100 | 100 | 80 | 90 |
| Oven-opening | ACT-Real | 30 | 50 | 30 | 40 |
| Oven-opening | DP-Real | 30 | 60 | 20 | 40 |
| Oven-opening | RDT-1B-Real | 60 | 70 | 30 | 50 |
| Oven-opening | Ours | 100 | 70 | 90 | 80 |

### 9.3 저자들의 결과 해석과 성과 범위

**외란 복구:** Ours는 세 과업에서 SR-R 100%를 보고한다. 그러나 전체 task SR는 90%, 90%, 80%다. 따라서 “모든 외란 시험에서 다시 열고 재시도했다”와 “모든 시험에서 물체를 집고 task를 완료했다”는 다른 결과다. [원문 §V-B, Table I–III, PDF pp. 6–7]

**데이터 효율:** 저자들은 simulation expert가 real teleoperation보다 매끄럽고 효율적인 동작을 만들어 준다고 설명한다. Oven의 real 시연은 보통 300 steps를 넘고, simulation 시연 대부분은 200 steps 이하라고 보고한다. 이 step 수를 초 단위로 환산할 제어 주기는 없다. 계산 overhead가 작다는 저자들의 해석도 별도 controller latency 실측과 구분한다. [원문 §V-B, PDF p. 7]

**과업 차이:** baseline에서는 상대적으로 큰 oven handle이 쉽고, 작은 drawer handle 및 변화가 큰 pick-and-lift가 어렵다는 해석을 제시한다. 물체별 치수·난도 실험을 별도로 한 결과라기보다 저자들이 성공률 차이에 붙인 설명이다. [원문 §V-B, PDF p. 7]

**VLA 비교:** fine-tuned RDT-1B-Real이 과업에 따라 DP/ACT보다 복구율이 높았지만 Ours에는 미치지 못했다고 설명한다. 이 결과는 해당 fine-tuning 데이터와 시험 구성에 한정한다. 모든 사전학습 VLA가 동일한 문제를 해결하지 못한다고 일반화하지 않는다. [원문 §V-B, PDF p. 7]

**그림의 역할:** Fig. 4(a)는 같은 종류의 강제 닫기 외란 후 baseline이 post-grasp로 진행하는 예와 Ours가 복구하는 예를 나란히 보여 준다. Fig. 5는 세 과업의 simulation·real rollout을 비교한다. 이 연속 사진에서 보이지 않는 힘 크기·추정 오차·실행 주기를 추출하지 않는다. [원문 Fig. 4–5, PDF pp. 5–6]

## 10. Ablation — 데이터와 정책 구조만 바꾸면 되는가?

### 10.1 조건: 모두 simulation 데이터·같은 입력 종류

Ablation은 **oven-opening의 실물 실행**에서 수행한다. 이 절의 모든 정책은 simulation data, RGB 320×240, binary gripper state를 사용한다. 따라서 Table I–III의 continuous joint-angle baseline 및 고해상도 image 조건과 섞지 않는다. [원문 §V-C, PDF p. 7]

| No. | Architecture | Simulation gripper randomization | Pseudo-tactile feedback |
| --- | --- | --- | --- |
| 1 | DP | 없음 | 없음 |
| 2 | DP | 있음 | 없음 |
| 3 | DP | 없음 | 있음 — 제안 방법 |
| 4 | ACT | 있음 | 없음 |
| 5 | RDT-1B | 있음 | 없음 |

**원문 Table IV의 task 성능:**

| No. | SR-ND (%) | SR-D (%) | SR (%) | AT (s) | SR-R (%) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 50 | 10 | 30 | 19.7 | 30 |
| 2 | 0 | 0 | 0 | — | 100 |
| 3 | 70 | 90 | 80 | 26.7 | 100 |
| 4 | 40 | 40 | 40 | 20.1 | 100 |
| 5 | 0 | 0 | 0 | — | 100 |

**원문 Table IV의 grasp 성능:**

| No. | GSR-ND (%) | GSR-D (%) | GSR (%) |
| --- | ---: | ---: | ---: |
| 1 | 50 | 10 | 30 |
| 2 | 70 | 80 | 75 |
| 3 | 70 | 90 | 80 |
| 4 | 40 | 70 | 55 |
| 5 | 50 | 60 | 55 |

[원문 Table IV, PDF p. 7]

### 10.2 No. 1 vs No. 3 — feedback이 없으면 복구율과 성공률이 감소

동일하게 DP·기본 simulation data를 사용하는 두 조건에서, feedback이 없을 때 SR-R는 30%, 전체 task SR는 30%다. Feedback을 적용한 No. 3은 각각 100%, 80%다. 명시적으로 외란을 주지 않은 SR-ND도 50%에서 70%로 높아진다. 저자들은 정책 자체가 너무 일찍 닫는 경우에도 즉시 다시 시도할 수 있기 때문이라고 설명한다. [원문 §V-C, Table IV, PDF p. 7]

다만 본문은 이 두 조건의 동일 checkpoint 재사용 여부·학습 seed·반복 학습 수를 밝히지 않는다. 비교가 feedback에 집중한다는 점과 모든 학습·실행 변수가 완전히 통제되었다는 주장을 구분한다.

### 10.3 성공한 경우만의 시간 평균: 19.7 s와 26.7 s

Feedback을 사용한 No. 3의 AT는 **26.7 s**로, No. 1의 **19.7 s**보다 길다. 저자들은 AT가 성공 rollout만 집계하며, feedback으로 새로 성공한 시험에는 외란이나 반복 파지 시도가 많은 어려운 사례가 포함되기 때문이라고 설명한다. 이 결과를 “feedback이 모든 조건에서 시간을 단축했다”로 바꾸지 않는다. [원문 §V-C, Table IV, PDF p. 7]

### 10.4 No. 2 — 열고 재시도할 수 있지만, 잡은 뒤 진행하지 못함

Gripper randomization을 넣으면 empty grasp 사례를 학습하므로 닫힘=성공의 잘못된 대응을 깨뜨릴 수 있다. No. 2는 **SR-R 100%, GSR 75%**를 보이지만 **task SR는 0%**다. 저자들은 이제 grasp state의 판정을 미세한 시각 단서가 담당하게 되었고, visual sim-to-real gap 때문에 실제로는 그 판정이 불안정해진다고 설명한다. [원문 §V-C, Table IV, PDF pp. 7–8]

Fig. 4(b)의 순서는 다음과 같다. [원문 §V-C·Fig. 4(b), PDF pp. 5, 7–8]

| 시간 구간 | 보고된 행동 |
| --- | --- |
| 1.5–4 s | Empty grasp에서 gripper를 열어 파지 재시도 |
| 4–9 s | Handle 파지 성공 |
| 9–39 s | 기대한 pull을 하지 못하고 작은 전후 운동·열고 닫기를 반복 |

이 예는 **재개방 행동을 학습하는 문제와, 성공한 파지를 확인하고 post-grasp로 진행하는 문제를 구분**해 보여 준다. 제안 방식은 후자의 상태 단서를 시각에만 맡기지 않도록 저수준 feedback을 사용한다.

### 10.5 No. 4·5 — architecture 변경의 결과를 정확히 읽기

ACT와 RDT-1B로 바꾸고 gripper-randomized simulation data를 사용한 경우에도 SR-R는 100%다. 그러나 task SR는 **ACT 40%, RDT-1B 0%**로, 제안 방법의 80%보다 낮다. [원문 §V-C, Table IV, PDF pp. 7–8]

원문은 architecture 변경이 혼동을 충분히 해결하지 못한다고 설명한다. 그렇다고 **모든 대체 architecture가 단 한 번도 task를 완료하지 못했다**고 옮기면 Table IV의 ACT 40%를 무시한다. 이 구분을 유지한다.

## 11. Limitation — 저자들이 밝힌 제약과 보고된 잔여 실패

### 11.1 독립된 Limitation 절은 없다

원문에는 별도의 Limitation 절이 없고 §VI Conclusion도 기여·성과 요약으로 끝난다. 특히 제안한 pseudo-tactile 판정 자체가 실패하는 물체군이나 조건을 체계적으로 열거하지 않는다. 아래는 **본문이 직접 인정하는 조건·제약과 보고된 결과**이며, 정리자가 새로 만든 고장 시나리오를 저자 주장으로 추가하지 않는다.

### 11.2 본문에서 직접 확인되는 제약

| 항목 | 저자들이 명시한 내용 | 원문 위치 |
| --- | --- | --- |
| Simulation 구축 비용 | 환경과 expert policy 설정에는 인간의 작업이 필요하고, 그 이후 수집이 자동화됨 | §IV-B, PDF pp. 4–5 |
| 남는 visual sim-to-real gap | 현실적인 asset과 randomization으로 완화해야 함 | §IV-B, PDF p. 5 |
| 남는 kinematic sim-to-real gap | 회전축 위치 불일치가 과도한 stress·emergency stop을 만들 수 있어 admittance를 사용 | §IV-B, PDF p. 5 |
| 단순 interpolation의 범위 | 자신들의 randomization 90% 이상에 대응한다고 보고하며, 모든 조건의 성공을 주장하지 않음 | §IV-B, PDF p. 4 |
| 최종 task의 잔여 실패 | Ours의 전체 SR는 pick-and-lift 90%, drawer 90%, oven 80% | Table I–III, PDF p. 6 |

마지막 행은 **보고된 결과의 범위**다. 저자들이 모든 Ours 실패의 원인을 별도로 분류한 것은 아니므로, 이를 threshold 문제·slip·시각 실패 중 하나로 단정하지 않는다. 데이터 randomization과 architecture 변경의 실패는 §V-C의 비교군 결과이며, 제안 controller의 직접적인 실패 분석과 구분한다.

## 12. Future Work — 저자들이 제시한 향후 연구

**원문에 명시된 구체적인 Future Work 계획 없음.** 본문 §I–VI와 Conclusion 전체를 확인했으나, 특정 후속 연구를 하겠다는 계획을 별도 항목으로 제시하지 않는다. 이는 이 연구에 후속 과제가 없다는 뜻이 아니라 논문이 그런 계획을 명시하지 않았다는 뜻이다. [원문 §VI, PDF p. 8]

§IV-B에는 advanced planning, multi-GPU 수집 가속, DAgger와 같은 on-policy 시연 보완을 사용할 수 있다는 **가능성·simulation 장점**이 등장한다. 이를 이번 실험의 구현 완료 항목이나 확정된 Future Work로 바꾸지 않는다. 세 가능성의 구현 세부와 평가 수치는 원문에 없다. [원문 §IV-B, PDF pp. 4–5]

## 13. 미명시 사항·원문 해석 주의사항

### 13.1 재현에 필요한 정보의 공개 수준

| 범주 | 제공된 것 | 부족하거나 미명시인 것 |
| --- | --- | --- |
| Pseudo-tactile | 힘 평형 시 관절각, 최대 닫힘의 빈 파지, 강제 재개방 규칙 | threshold 값·평형 판정·필터·hysteresis·sampling·override 지속시간 |
| Force-controlled gripper | 2F-85라는 모델과 Fig. 2의 제어 구성 | force 신호 출처·controller law·force setting |
| Admittance | 식 (1), policy 이후의 궤적 보정 | wrench 측정원·좌표계·보상·필터·gain·이산 적분·출력 제한 |
| Simulator expert | 세 단계, object-centric key pose 변환, post-grasp 운동 | key pose 값·보간 방식·시간 profile·단계 전환 규칙 |
| Randomization | Object/robot pose, lighting, texture | 분포·범위·sample 비율·train/test 일치 정도 |
| 학습 | DP, DDIM 100/16, 입력·출력, 시연 수 | loss 구현·network 구조·optimizer·epoch·horizon·seed·checkpoint 선택 |
| 평가 | 20회·외란 10회, 8개 지표, Table I–IV | 수치 success threshold·timeout·복구 시간 한계·신뢰구간 |
| 실물 장비 | UR5, 2F-85, D435i, 입력 이미지 크기 | 측정 범위·분해능·sample rate와 로봇 정량 사양 |

이 표는 원문의 공개 범위에 관한 정리이지 저자들이 작성한 Limitation 목록이 아니다. 코드·보충자료를 읽지 않은 상태에서 ‘코드에도 없다’고 단정하지 않는다.

### 13.2 ‘추가 데이터·하드웨어 없음’의 범위

이 표현은 **gripper state disambiguation을 위해 별도 촉각 장치를 달거나 실패·복구 데이터를 추가 수집할 필요가 없다는 제안**과 연결된다. 정책 자체는 시뮬레이션 demonstration을 학습하고, simulation asset과 expert도 준비해야 한다. Main comparison은 Ours가 과업당 2,000개, real baseline이 50–60개 수준을 사용하므로 데이터 양이 같지도 않다. [원문 §IV–V-A, PDF pp. 3–6]

### 13.3 ‘closed는 성공’·‘noise-free’의 읽는 범위

이들은 **빈 닫힘을 재개방으로 바꾸는 low-level controller의 의도된 동작과 관측 의미**다. 논문은 모든 접촉 상황·모든 그리퍼·모든 물체의 판정 정확도를 검증하지 않는다. Fig. 2의 도식만으로 잘못 잡은 대상의 identity 확인, slip 조기 예측, 접촉력 크기 추정까지 포함한 것으로 해석하지 않는다. [원문 §IV-A, Fig. 2, PDF pp. 3–4]

### 13.4 제목의 tactile·simulation learning과 실제 연구 분류

Pseudo-tactile은 전용 tactile array의 분포 신호가 아니고, policy는 RGB를 함께 사용하는 imitation learning이다. 따라서 이 논문을 **tactile-only RL, F/T+tactile raw observation fusion, 고해상도 촉각 pushing**으로 정리하면 원문의 방법과 다르다. 힘·접촉 정보는 gripper override와 별도 admittance에 연결되며 두 역할을 유지해야 한다. [원문 §IV-A–C, PDF pp. 3–5]

### 13.5 Table·본문의 강조를 그대로 수치 주장으로 바꾸지 않기

| 원문 표현·구조 | 해석 시 유지할 점 |
| --- | --- |
| 모든 지표에서 우수하다는 §V-B 서술 | Table III의 GSR-ND는 Ours와 RDT-1B-Real 모두 70%로 동률이다. 모든 cell의 엄격한 우위를 주장하지 않음 |
| ‘Different Policy Architectures Help Little’ | Table IV의 ACT task SR는 40%다. 모두 0%라는 결과가 아님 |
| §V-C의 ‘last four rows’ 표현 | Table IV의 2–5행에는 제안 방법 No. 3도 포함되며, No. 3은 gripper randomization이 없다. 모든 행을 randomized-data 조건으로 묶지 않음 |
| Table I에 ACT-Real 행 없음 | 0%·실험 불가 등의 이유를 임의 추가하지 않음 |
| Ours의 oven SR-D가 SR-ND보다 높음 | 보고값을 유지하되 외란이 성능을 개선한다는 인과 결론을 내리지 않음 |
| 성공률의 큰 차이 | 표본 수와 비교 조건을 함께 적고 통계적 유의성 검정이 있었다고 쓰지 않음 |

[원문 §V-A–C, Table I–IV, PDF pp. 6–8]

## 14. 원문 위치별 다시 읽기 안내

| 찾고 싶은 내용 | 원문 위치 |
| --- | --- |
| Closed observation과 실제 grasp state의 불일치 | Fig. 1(b), §I·III, PDF pp. 1–3 |
| 시연자와 정책의 tactile feedback 차이 | §I·III, PDF pp. 2–3 |
| Tactile sensor–force-controlled gripper의 비유 | Fig. 2 상단, §IV-A, PDF p. 3 |
| Force/position threshold 도식 | Fig. 2 하단, PDF p. 3 |
| 빈 파지에서 실제 gripper open override | §IV-A, PDF p. 4 |
| 학습·실행의 두 controller 경로 | Fig. 3, PDF p. 4 |
| Expert key pose·interpolation·단계별 규칙 | §IV-B, PDF p. 4 |
| 시연 선별·수집량 예시·simulation 준비 비용 | §IV-B, PDF pp. 4–5 |
| Realistic asset·randomization·admittance | §IV-B, 식 (1), PDF p. 5 |
| DP 관측·행동과 DDIM 100/16 | §IV-C, PDF p. 5 |
| 데이터량·baseline·평가·하드웨어 | §V-A, PDF p. 6 |
| 세 과업의 전체 비교 수치 | Table I–III, PDF p. 6 |
| 성공 rollout만으로 AT를 계산하는 설명 | §V-C, PDF p. 7 |
| Randomized data로 복구하지만 post-grasp에 실패 | Fig. 4(b), §V-C, PDF pp. 5, 7–8 |
| Ablation 전체 구성·수치 | Table IV, PDF p. 7 |
| 결론, 구체적 Future Work 미명시 확인 | §VI, PDF p. 8 |

## 15. 정리·검증 범위

첨부 출판본의 8쪽을 읽고 Fig. 1–5, Table I–IV, admittance 식 (1)과 번호 없는 pose 변환식을 렌더링으로 확인했다. 본문 밖의 자료를 이용해 threshold·센서 사양·학습 설정의 빈칸을 채우지 않았다. Related Works는 이 논문이 서술한 비교 구도로 한정했다.

블록 수식은 `$$`, 인라인 수식은 `$…$`를 사용하며 수식용 코드 펜스나 백틱 혼합 표기를 사용하지 않는다. 수식 17개(블록 4개·인라인 13개)의 로컬 MathJax 구문 검사에서 오류가 없었고, 블록 수식 전체의 표시와 표 28개의 열 구조를 확인했다. 실물 결과 표와 admittance 해설의 로컬 브라우저 표시도 확인했다. 실제 GitHub 웹페이지의 최종 표시는 확인하지 못했으며, 논문 코드 실행·모델 재학습·실험 재현은 수행하지 않았다.
