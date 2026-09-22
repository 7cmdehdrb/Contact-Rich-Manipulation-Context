# Framework for Robot Door Opening Based on Visual, Force, and Tactile Integration — 원문 상세 정리

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 조사 · R7](../reviews/2026-09-14_blind-sweep-force-torque-tactile.md#r7)

> **사용자 확인 상태:** **미확인** — 상세 리뷰는 작성되었지만, 사용자가 아직 직접 확인하지 않은 논문이다. (2026-09-22)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Framework for Robot Door Opening Based on Visual, Force, and Tactile Integration** |
| 저자 | Valentin Šimundić, Luka Petrović, Matej Džijan, Robert Cupec |
| 출판 | IEEE Access, Volume 14, 11110–11128, 2026 |
| DOI | [10.1109/ACCESS.2026.3655617](https://doi.org/10.1109/ACCESS.2026.3655617) |
| 출판 이력 | 접수 2025-11-28, 승인 2026-01-08, 온라인 출판 2026-01-19, current version 2026-01-23 |
| 기존 조사본 식별자 | [2026-09-14 문헌조사](../reviews/2026-09-14_blind-sweep-force-torque-tactile.md#r7)의 **R7** |
| 정리일 | 2026-09-16 |
| 확인한 원문 | 제공된 출판본 PDF 19쪽 전체. 본문 §I–VIII, Appendix A–B, 식 (1)–(33), Algorithm 1–2, Fig. 1–14, Table 1–5, References [1]–[39] |
| 확인하지 않은 자료 | 인용된 선행논문의 개별 원문, 저자 공개 코드·실행 설정·원시 실험 로그, 보충 영상, 제조사 데이터시트 |
| 원문 PDF SHA-256 | `bd087fc82028a8d1b677ef51dcaaecc814c89d493347214d020002ff04e8f227` |

이 문서는 논문 자체의 문제 상황, Related Research, 환경·센서, 힘·촉각 처리, 카메라 보정·계획 방법, 실험, 저자 명시 Limitation과 Future Work를 정리한다. 다른 연구 주제에 대한 적용안은 포함하지 않는다. `[원문 §…, PDF p.…]`는 첨부 출판본의 위치이며, **PDF 1–19쪽은 인쇄 페이지 11110–11128**에 대응한다. 참고문헌 번호 `[36]` 등과 기존 조사본의 R 번호를 구분한다.

본문·수식·실험 수치는 첨부 출판본을 기준으로 한다. 서지 식별은 IEEE Xplore 검색 결과 및 [저자 소속 기관 FERIT의 연구 소개](https://www.ferit.unios.hr/research-groups/IG04/research/robot-door-opening-based-on-visual-force-and-tactile-integration)로도 대조했다. 외부 페이지의 내용을 이용해 원문에 없는 센서 사양이나 구현 파라미터를 보충하지 않았다. 그림·표·수식은 PDF 렌더링으로 대조했으며, 대수적 해설은 별도 실험·구현 결과가 아니다.

**핵심 구분:** 이 연구는 F/T와 tactile을 받는 강화학습 정책이나 연속 힘 추종 제어기를 학습하는 연구가 아니다. **힘·촉각으로 실패 사건을 검출하고, 그때의 도구 pose 또는 실패 경로를 기하학적 제약으로 바꾼 뒤, 카메라의 내·외부 파라미터를 보정하여 다음 문 열기 경로를 다시 계획하는 방법**이다. 힘 방향으로 접촉면 후보를 제거하는 기법과 그리퍼 전체 촉각을 이용한 정확한 접촉점 검출은 현재 구현이 아니라 향후 연구다. [원문 §III–IV, §VIII, PDF pp. 3–8, 17]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 상황·기여와 원문의 관련 연구 구도 |
| 3 | 로봇·센서·환경 상세 사양 및 정보의 역할 |
| 4 | 상태기계와 힘·촉각 신호의 사건 변환 |
| 5–8 | 12차원 카메라 보정, 접촉·miss 제약, 후보 탐색, 부록의 점·평면 변환 |
| 9 | 문 모델과 접근·삽입·열기 경로 생성 |
| 10–11 | 시뮬레이션·실물 실험 조건, 결과, 계산 시간, 기존 연구와의 비교 |
| 12–13 | 저자들이 밝힌 Limitation과 Future Work |
| 14–16 | 재현에 필요한 미명시 사항, 원문 표기 주의, 근거 위치, 요약 |

## 1. 제시하는 문제 상황

### 1.1 손잡이 없는 문은 단순히 앞에서 밀면 열리는 문과 다르다

대상은 **손잡이 없는 캐비닛 문**이다. 그리퍼를 문짝과 캐비닛 고정부 사이의 좁은 틈으로 넣고, 문짝 뒷면에 접촉하여 열어야 한다. 손잡이를 잡는 기존 방법이나 큰 문을 앞에서 밀어 여는 방법만으로는 이 좁은 삽입 문제를 해결하기 어렵다는 것이 저자들의 출발점이다. [원문 §I, PDF pp. 1–2]

원문은 전체 동작을 `pull open`으로 설명하면서, 도구가 문짝 뒷면을 개방 방향으로 미는 국소 상호작용에는 `push`도 사용한다. 따라서 **문짝 뒷면의 접촉을 이용해 힌지 축 주위로 문을 여는 과업**으로 이해해야 한다. 손잡이를 지속 파지하는 과업이나 자유 물체를 평면에서 운반하는 과업으로 바꾸어 설명하지 않는다. [원문 §III-C, §IV-C, §V-B, PDF pp. 5, 7, 9–10]

### 1.2 실패의 주된 원인을 카메라 calibration 오차로 설정한다

저자들은 RGB-D로 재구성한 환경 모델의 오류 원인을 세 가지로 구분한다.

| 오류 원인 | 원문의 설명 | 이 연구에서의 처리 범위 |
| --- | --- | --- |
| Camera measurement noise | 평균 0이고 공간적으로 고주파인 측정 noise | 많은 점으로 평면을 추정하면 상당 부분 상쇄된다고 가정 |
| Calibration error | 부정확한 카메라 내·외부 파라미터에 의한 systematic bias | 제안한 보정 방법의 직접 대상 |
| Segmentation error | 점을 실제 객체 표면에 잘못 할당하는 오류 | segmentation 알고리즘 자체는 제안하지 않음 |

이는 모든 현실 환경에서 calibration 오차가 항상 지배적이라는 보편적 실험 결론이 아니다. **표면 대응은 이미 올바르게 얻었지만 그 좌표·평면 파라미터가 잘못된 경우**를 주요 문제로 설정한 것이다. [원문 §I, §IV-A, PDF pp. 2, 5]

### 1.3 같은 실패를 반복하지 않기 위해 무엇을 고치는가

틀린 모델로 경로를 계획하면 빈 공간이라고 예상한 곳에서 충돌하거나, 문에 닿아야 하는 동작이 허공을 지나갈 수 있다. 이때 단순히 다른 방향으로 재시도하는 대신, **그 실패를 발생시킨 카메라 파라미터를 수정**한다. 보정된 파라미터로 모델의 점·평면과 문 pose를 갱신하고, 다시 경로를 계산한다. 이전 장면의 실패 기록도 유지하여 다음 장면의 첫 시도부터 활용한다. [원문 §III, §IV-D, §V-C, PDF pp. 3–4, 8, 10]

저자들이 제시하는 기여는 힘·촉각을 포함하는 실패 복구 프레임워크, 실패 상호작용에 근거한 카메라 보정 방법, 그리고 시뮬레이션·실물 평가다. **RL의 reward·policy architecture·GAN 학습법은 이 논문의 메소드가 아니다.** [원문 §I, §VII-D, PDF pp. 2, 16–17]

### 1.4 주요 전제

| 전제 | 의미와 적용 범위 |
| --- | --- |
| Eye-in-hand RGB-D | 카메라가 로봇 말단에 고정되어 있고, 말단–카메라 관계를 보정 대상으로 삼음 |
| Polyhedral environment | 환경을 꼭짓점·평면·그 대응으로 표현하며, 모델 face와 실제 face의 대응이 성립한다고 가정 |
| Convex tool contact model | 환경과 접촉하는 도구 부분은 하나의 convex polyhedron으로 근사 |
| Miss의 단순 운동 | 원문에서 전개한 motion envelope는 convex 도구·대상과 도구의 선형 이동을 가정 |
| 알려진 로봇 운동학·TCP | FK·IK를 계산할 수 있고, 말단에 대한 그리퍼 fingertip pose를 알고 있다고 가정 |
| 문 기구 모델 | 강체 문짝이 고정된 힌지 축 주위로 회전 |
| 실패 사건의 검출 | 충돌 또는 기대한 접촉의 부재를 검출할 수 있으나, 충돌의 정확한 feature 대응은 모름 |

[원문 §III-A, §IV-A–D, §V-A–B, PDF pp. 4–10]

## 2. Related Research — 원문이 구성한 비교 구도

이 절은 **본 논문의 저자들이 관련 연구를 어떻게 설명하는지**를 정리한다. 인용된 모든 연구를 별도로 정독하여 검증한 비교표가 아니다.

### 2.1 Visuo-force-tactile sensor fusion

원문의 §II-A는 다음 네 계열을 다룬다.

| 계열 | 원문에서 든 연구·방법 | 저자들이 설정하는 비교점 |
| --- | --- | --- |
| 공동 표현과 end-to-end 학습 | Huang [12]의 3D 시각·촉각 표현과 imitation learning, Hansen [13]의 tactile gating·augmentation, Sferrazza [14]의 masked multimodal 표현, Li [15]의 audio 추가 | 데이터·시연 수요, 실물 데이터 부족, 학습의 실무적 어려움 |
| 기하·최적화 기반 결합 | Caddeo [16]의 tactile contact 예측과 기하 제약, Nonnengießer [17]의 depth/tactile point cloud와 ICP, Li [18]의 접촉·충돌에 의한 pose 정제 | 작은 물체에서의 결과를 문·서랍 같은 큰 대상에 확대할 때의 불확실성 |
| 시각과 고유감각·힘 기반 적응 | Sampath [19]의 grasp 조정, Gupta [21]의 whole-body planning 보정, Wang [6]의 haptic door opening, Wei [9]의 힘을 고려한 생성 궤적 | 행동·궤적 적응과 비교해, 본 연구는 카메라 miscalibration 자체를 보정 대상으로 삼음 |
| 지각·재구성 | Murali [22]의 vision/tactile point cloud 결합, Fang [23]의 tactile normal을 이용한 3D Gaussian Splatting | 표면 재구성과 지각의 개선이라는 인접 목적 |

저자들은 기존 연구가 정확한 camera calibration을 전제하거나 오류를 지각·정책 학습의 문제로 취급하는 경우가 많다고 주장한다. 이 평가는 원문이 설정한 연구 동기이며, 모든 인용 방법이 동일한 전제를 가진다는 별도 검증 결과는 아니다. [원문 §II-A, PDF pp. 2–3]

### 2.2 Manipulation with failure recovery

| 계열 | 원문의 사례 | 본 논문이 강조하는 차이 |
| --- | --- | --- |
| 계획·계층적 recovery | Ahmad [24]의 behavior tree/motion generator, Pan [25]의 실패를 고려한 TAMP, Ratner [26]의 control discrepancy를 이용한 planning | 오류를 감지한 뒤 계획에 반영하는 공통점. 정확한 실패 검출·분류가 필요하다는 점을 지적 |
| 접촉·힘 활용 | Ren [27]의 collision-inclusive 조작, Jiang [28]의 의도적 비파지 접촉, Gavura [29]·Limoyo [30]의 접촉 기반 calibration | 본 연구는 문 열기의 **실패 중 얻은 상호작용**을 카메라 보정에 사용 |
| 학습 기반 recovery | Ak [31]의 failure prevention, Chen [32]의 VLM recovery | 데이터 요구와 미지 실패 상황에 대한 일반화 문제를 동기로 제시 |
| 시스템 수준 fault handling | Galbally [33]의 Elly, Burgess-Limerick [34]의 이동 중 recovery, Goller [35]의 MPC fault handling | 특정 실패 유형·사전 지식에 대한 의존성을 비교 대상으로 삼음 |

[원문 §II-B, PDF p. 3]

### 2.3 사용한 기반 기법과 제안한 부분의 구분

문 인식과 현재 상태 재추정은 DDD [36]의 THD·SE 방법을 사용한다. Depth model은 [37], convex object의 교차 판정 관련 근거는 [38], collision checking은 FCL [39]에 의존한다. 이 기법들을 모두 새로 개발한 것이 아니다. 제안의 중심은 **실패 사건에서 접촉·miss 제약을 만들고, 접촉 대응의 모호성을 탐색하면서 카메라 보정값을 찾는 구조**다. [원문 §III-A·E, §IV, §V-B, PDF pp. 4–10]

## 3. 환경과 로봇·센서 상세 사양

### 3.1 실물 구성과 원문에 명시된 사양

| 구성 | 원문에 명시된 내용 | 장비 성능 수치의 확인 범위 |
| --- | --- | --- |
| 로봇 | 테이블에 고정된 **Universal Robots UR5** | 가반하중·reach·반복정밀도·관절 속도 등 수치 미명시. UR5e로 바꾸지 않음 |
| 그리퍼 | **Robotiq 3-Finger Gripper** | 개구 범위·최대 grasp force·구동 속도·손가락별 DOF 수치 미명시 |
| 손목 F/T | **Robotiq FT300-S**, 로봇 손목에 장착 | 축별 측정 범위·힘/토크 분해능·정확도·sample rate·대역폭 미명시 |
| 촉각 | **XELA uSPa 44**, 그리퍼 fingertip에 장착한 단일 촉각 센서 | taxel 수·배열·축별 raw 출력·공간 해상도·측정 범위·분해능·sample rate 미명시 |
| 시각 | 말단에 장착한 **RGB-D/3D camera**. Fig. 1에서 `LiDAR Camera`로 표시 | 제조사·정확한 모델명·RGB/depth 해상도·frame rate·정밀도·FOV·측정 거리 미명시 |
| 계산 환경 | **AMD Ryzen 9 7900, RAM 32 GB, Docker container** | §VII-C의 보정 계산 시간 측정 환경. 제어 loop 주파수와 구분 |

[원문 Fig. 1, §IV-A, §VI-B, §VII-C, PDF pp. 2, 5, 11–12, 15]

사진의 외형이나 모델명의 숫자에서 사양을 추정하지 않는다. 예를 들어 `uSPa 44`라는 이름만으로 이 논문이 4×4 taxel 배열이나 특정 측정 범위를 보고했다고 서술하지 않는다. 카메라도 사진에서 특정 제품처럼 보인다는 이유로 모델을 확정하지 않는다.

### 3.2 힘·촉각 사용에 필요한 성능·처리 정보의 공개 수준

| 확인 항목 | 본문에서 확인한 내용 |
| --- | --- |
| F/T의 사용 목적 | 접근·삽입 중 external force에 의한 충돌 검출 |
| F/T 판정 기준 | predefined force threshold 초과. **수치, norm/축 선택, 방향별 조건 미명시** |
| 토크 채널 사용 | F/T 장비는 명시하지만 별도의 torque 기반 판정식이나 보정항은 제시하지 않음 |
| 영점·중력·도구 부하 보정 | 미명시 |
| 필터·noise 처리 | F/T/tactile의 filter 종류, window, cutoff 미명시 |
| 촉각 판정 기준 | significant tactile feedback으로 기대한 문 접촉을 확인. **수치·taxel 축약·시간 window 미명시** |
| 접촉 이력 | 처음부터 접촉이 없었는지, 접촉 후 사라졌는지를 구분하여 상태 전환 |
| 정확한 접촉점 | 현재 구현은 충돌 지점의 tool/environment feature 대응을 직접 알지 못함 |
| 센서 동기화·지연 | timestamp 정렬, 수신 주기, stop latency 미명시 |
| 힘의 방향 활용 | 현재 보정 알고리즘의 입력으로 쓰는 식은 없으며, 후보 제거에 사용할 것을 Future Work로 제시 |

[원문 §III-D–E, §IV-D, §VIII, PDF pp. 5, 8, 17]

따라서 본 논문으로부터 **“F/T 최소 감지 힘은 몇 N”**, **“몇 Hz로 힘을 조절한다”**, **“촉각 pressure map을 이렇게 합산한다”** 같은 명세를 얻을 수 없다. 검출용 threshold와 센서의 물리적 최소 검출 성능도 구분해야 한다.

### 3.3 실물 캐비닛과 배치

Table 2는 실물 캐비닛의 다음 값들을 제시한다.

| 항목 | 값 |
| --- | --- |
| Width | 0.395 m |
| Height | 0.495 m |
| 테이블 위 배치 x | −0.35–0.0 m |
| 테이블 위 배치 y | 0.4–0.8 m |
| z축 주위 회전 | −60°–60° |
| 목표 문 열림 각도 | 45° |
| 캐비닛 깊이·문짝 두께·틈 폭 | 미명시 |
| 문짝 질량·힌지 마찰·복원 토크 | 수치 미명시 |

배치는 위 범위의 수치를 만족하는 것만으로 허용되지 않는다. 바닥판 네 모서리가 테이블 위에 있어야 하며, 문이 열리면서 로봇 base와 충돌하지 않아야 하고, planner가 적어도 하나의 유효 궤적을 생성할 수 있어야 한다. [원문 §VI-B, Table 2, PDF p. 12]

### 3.4 정보별 역할

| 정보 | 어디에 사용하는가 | 혼동하지 말아야 할 내용 |
| --- | --- | --- |
| 초기 RGB-D sequence | THD로 문짝·힌지·크기 등의 모델 생성 | policy 학습용 시연 trajectory가 아님 |
| 재촬영한 RGB-D image | contact loss 후 현재 문 상태 재추정 | 전 과정 vision-free가 아님 |
| 손목 force | 접근·삽입 충돌을 검출하여 정지·보정을 시작 | force vector를 그대로 LM cost에 넣는 구조가 아님 |
| fingertip tactile | opening 중 접촉 성립·miss·contact loss를 구분 | 전체 그리퍼의 정밀 접촉 위치 지도라고 보고하지 않음 |
| 로봇 joint state/FK·TCP transform | 실패 시 도구 pose와 경로의 기하 기록, 경로 생성 | 센서가 측정한 실제 contact point와 다름 |
| 과거 scene·실패 trace | 현재 보정 시 함께 사용 | 신경망 replay buffer나 RL policy update가 아님 |
| GT cabinet model | simulation 오류 생성·평가, 실물 pose 오차 비교 | 실행 중 완전한 정답 모델이 알려진 것으로 해석하지 않음 |

[원문 §III–VII, PDF pp. 3–15]

## 4. 핵심 메소드 1 — 힘·촉각을 실패 사건과 상태 전환으로 바꾸기

### 4.1 정상 실행 순서

Fig. 2의 finite-state machine은 다음 순서로 진행한다.

```text
Door Detection
 → Environment Model
 → Path Planning
 → Approach Path
 → Insertion Path
 → Opening Path
```

시작 시 DDD의 **Teaching by Human Demonstration(THD)**를 이용한다. RGB-D로 사람이 문을 열고 닫는 모습을 관측하여, 조작할 문과 그 크기·회전축 pose·문짝 offset을 얻는다. **제안한 보정법이 policy learning을 요구하지 않는다는 사실과, 초기 문 검출 모듈에 인간 시연이 쓰인다는 사실은 양립한다.** 시스템 전체가 시연을 전혀 사용하지 않는다고 요약하면 안 된다. [원문 §III-A, PDF p. 4]

### 4.2 단계별 감시 조건과 실패 복구

| 실행 단계 | 주 감시 정보 | 실패 판정 | 기록·다음 동작 |
| --- | --- | --- | --- |
| Approach | 손목 F/T의 external force | predefined threshold를 초과하는 접촉 | 로봇 정지 → 실패 도구 pose 기록 → Correction → 모델 갱신 → 재계획 |
| Insertion | 손목 F/T의 external force | 틈에 삽입하면서 threshold 초과 | 정지·보정·재계획으로 전환 |
| Opening: 처음부터 접촉 없음 | fingertip tactile | 기대한 접촉의 significant feedback이 없음 | `miss`로 기록 → Correction → 모델 갱신 → 재계획 |
| Opening: 접촉 후 소실 | fingertip tactile의 성립·소실 이력 | 있었던 접촉이 사라짐 | `contact loss` → Recapture → Correction 및 모델 갱신 → 재계획 |
| 정상 진행 | 계획 경로와 감시 조건 | 해당 단계가 성공적으로 끝남 | 다음 정상 상태로 전이 |

[원문 Fig. 2, §III-D–E, PDF pp. 4–5]

정지 임계값의 실제 수치나 검출식을 원문이 주지 않으므로, 여기서 임의로 힘 norm·hysteresis·filter를 추가하지 않는다. `significant tactile feedback`의 구현도 raw taxel 합계인지, 최대값인지, 특정 방향 성분인지 알 수 없다.

### 4.3 Miss와 contact loss를 다르게 처리하는 이유

처음부터 문을 놓쳤다면 계획과 실물의 불일치를 **“그 경로 동안 도구가 문에 닿지 않았다”**는 제약으로 사용할 수 있다. 반면 문을 일부 연 뒤 접촉이 사라지면, 힌지의 힘으로 문이 다시 닫히거나 다른 각도로 움직일 수 있다. 이때 과거의 문 상태만 유지한 채 재계획하지 않고, **단일 RGB-D image에서 DDD의 State Estimation(SE)으로 현재 문 configuration을 다시 얻는다.** Fig. 2에서 contact loss가 직접 Correction으로 가지 않고 Recapture를 거치는 이유다. [원문 §III-E, Fig. 2, PDF pp. 4–5]

원문은 contact loss도 missed contact로 취급한다고 설명하지만, 움직이는 문에서 어떤 경로 구간을 선택하여 miss envelope로 구성하는지의 세부 절차까지 독립 수식으로 제공하지 않는다. 상태 전환의 설명과 제약의 실제 생성 구현을 구분해야 한다. [원문 §III-D, §IV-C–D, §V-C, PDF pp. 5, 7–10]

### 4.4 센서에서 최적화로 전달되는 것은 무엇인가

보정에 사용하는 execution trace에는 충돌의 경우 **실패 순간 도구 pose**, miss의 경우 **접촉했어야 하는 path segment**가 기록된다. 각 실패는 해당 문 상태·capture pose를 가진 scene에 연결된다. [원문 §IV-D, §V-C, PDF pp. 8, 10]

```text
F/T threshold 초과
 → 충돌 사건
 → 실패 시 도구 pose + 알려진 도구 형상
 → 가능한 tool/environment 접촉 feature 후보
 → 실제로 접촉했음을 설명하는 기하학적 제약

Tactile의 기대 접촉 부재
 → miss 사건
 → 실행한 경로 구간 + 알려진 도구 형상
 → motion envelope
 → 해당 이동 부피와 대상이 겹치지 않음을 설명하는 제약
```

즉, 측정 force magnitude와 tactile intensity를 회귀 입력으로 넣어서 카메라 correction vector를 바로 출력하는 모델이 아니다. **센서는 실제 세계에서 일어난 사건을 알려 주고, 로봇 기하와 scene 모델이 그 사건을 수학적 제약으로 표현한다.** [원문 §IV-C–D, PDF pp. 6–8]

### 4.5 현재 사용하지 않는 힘·촉각 정보

제안된 cost에는 force vector, torque vector, tactile image, pressure distribution, slip velocity 항이 없다. F/T로부터 접촉 법선을 직접 추정하지도 않는다. 정밀 접촉점이 불명확하기 때문에 후보를 탐색하며, 저자들은 힘 방향이나 더 넓은 촉각 coverage로 이 모호성을 줄이는 것을 후속 연구로 남긴다. [원문 식 (9), §VIII, PDF pp. 8, 17]

## 5. 핵심 메소드 2 — 카메라 correction vector의 정의

### 5.1 환경 모델

환경 모델 $A$는 vertices, supporting planes, vertex–plane associations로 이루어진다. 각 face의 supporting plane은 다음과 같다.

**원문 식 (1)**

$$
n^{T}p=d.
$$

$n$은 unit normal, $d$는 기준 원점에서 normal 방향의 signed plane offset이다. 모델의 face 대응 자체는 맞고, calibration 때문에 $n$, $d$, vertex 좌표가 틀렸다는 설정이다. [원문 §IV-A, PDF p. 5]

### 5.2 Intrinsic correction

원래 intrinsic matrix $K$와 correction matrix $L$은 다음과 같다.

**원문 §IV-A의 정의 및 식 (2)–(3)**

$$
K=
\begin{bmatrix}
f_x&0&u_c\\
0&f_y&v_c\\
0&0&1
\end{bmatrix},
\qquad
L=
\begin{bmatrix}
g_x&0&h_x\\
0&g_y&h_y\\
0&0&0
\end{bmatrix},
\qquad K'=K+L.
$$

$g_x,g_y$는 focal-length 성분에, $h_x,h_y$는 principal-point 성분에 가산되는 보정값이다. 이 정의에는 별도의 radial/tangential distortion coefficient 보정항이 없다. [원문 §IV-A, PDF pp. 5–6]

### 5.3 Depth correction

저자들은 [37]의 disparity 기반 depth model을 사용한다. $\delta$는 disparity, $z_r$는 reference plane과 관련된 값, $\lambda$는 depth camera parameter다.

**원문 식 (4)–(5)**

$$
z=\frac{z_r}{1+\frac{z_r}{\lambda}\delta}
=\frac{\lambda}{\delta+\kappa},
\qquad \kappa=\frac{\lambda}{z_r}.
$$

**원문 식 (6)–(7)**

$$
\kappa'=\kappa+\lambda g_z,
\qquad
\lambda'=\lambda(1+h_z).
$$

$g_z,h_z$는 단순한 xyz translation offset이 아니라 **depth 복원 함수의 파라미터 보정**이다. Fig. 1의 장비는 LiDAR camera로 표기되지만, [37]의 모델을 해당 실물 카메라 raw 값에 연결하는 장치별 절차는 본문에 상세히 나오지 않는다. [원문 §IV-A, PDF p. 6]

### 5.4 Extrinsic correction

$R,t$는 원래 camera-to-end-effector 회전·이동 관계이고, $\phi$는 correction rotation vector, $s$는 correction translation이다.

**원문 식 (8) 및 직후 정의**

$$
R'=R\Delta R(\phi),
\qquad t'=t+s.
$$

회전 보정은 원문처럼 오른쪽에 곱한다. 임의로 $\Delta R(\phi)R$로 바꾸면 같은 식이 아니다. [원문 §IV-A, PDF p. 6]

### 5.5 전체 12차원 보정값

$$
x=
\begin{bmatrix}
g_x&g_y&g_z&h_x&h_y&h_z&
\phi_x&\phi_y&\phi_z&s_x&s_y&s_z
\end{bmatrix}^{T}.
$$

이 $x$를 바꾸면 여러 face와 vertex가 **동일한 camera correction에 따라 함께 변환**된다. 실패한 지점 하나의 문 pose만 독립적으로 이동시키는 것과 다르다. 로봇의 기구학 파라미터나 도구 TCP 자체의 오차를 함께 추정하는 변수는 이 보정 벡터에 포함되지 않는다. [원문 §IV-A–B, §V-B–C, PDF pp. 6, 9–10]

## 6. 핵심 메소드 3 — 충돌과 miss를 기하학적 제약으로 만들기

### 6.1 Feature와 접촉 후보

도구의 feature는 $f^t$, 환경의 feature는 $f^e$로 표기하며 vertex·edge·face를 가리킨다. $k$번째 실패를 설명하는 후보 하나를 $c_k=(f_k^t,f_k^e)$로 쓴다. 여기서 후보는 센서가 알려 준 정답 접촉점이 아니라 **도구 pose와 환경 모델에서 고려하는 가능한 기하학적 대응**이다. [원문 §IV-C–D, PDF pp. 6–8]

충돌에는 vertex–face와 edge–edge contact를 고려한다. 환경 vertex와 도구 face의 접촉도 가능하다고 설명한다. Fig. 3은 이 두 종류가 같은 알고리즘에서 후보가 되는 것을 보여 준다. [원문 §IV-C, Fig. 3, PDF p. 6]

### 6.2 Vertex–face contact

도구 vertex의 위치를 $p_k$, 후보 환경 face의 plane을 $(n_k,d_k)$로 쓰면 orthogonal distance는 다음과 같다.

**원문 §IV-C의 번호 없는 수식**

$$
e(c_k)=n_k^{T}p_k-d_k.
$$

이 값만 0으로 만들어서는 실제 polygon face 위의 접촉인지 확인할 수 없다. 무한 평면 위에 있지만 유한 face 경계 밖에 있을 수 있기 때문이다. 원문은 인접 face의 plane 집합 $N(f_k^e)$를 이용한 lateral distance도 둔다.

$$
\gamma(c_k)=\max\left\{
0,\max_{(n,d)\in N(f_k^e)}(n^{T}p_k-d)
\right\}.
$$

원문 설명상 vertex의 직교 투영이 face 경계 안에 있으면 $\gamma=0$이다. 따라서 $e$는 supporting plane과의 불일치를, $\gamma$는 유효 접촉 feature의 경계 조건을 반영한다. $e$는 위 식상 signed quantity이며 cost에서 제곱된다. [원문 §IV-C, PDF p. 7]

### 6.3 Edge–edge contact

두 후보 edge에 수직인 unit vector를 $n_k$, edge 위의 closest points를 $p_k^t,p_k^e$라고 한다.

$$
e(c_k)=n_k^{T}(p_k^t-p_k^e),
$$

$$
\gamma(c_k)=
\left\lVert
(I-n_kn_k^{T})(p_k^t-p_k^e)
\right\rVert.
$$

첫 값은 두 edge를 포함하는 평행 평면 사이의 separation을, 두 번째는 그 방향을 제거한 평면에서의 투영점 간 차이를 표현한다. **같은 무한 평면 조건을 만족하는 것과 실제 유한 edge끼리 만나는 것을 구분**하는 역할이다. [원문 §IV-C, PDF p. 7]

### 6.4 Miss: 관측되지 않은 접촉도 정보로 사용한다

Fig. 4에서는 현재 모델이 문을 지날 것으로 예측한 경로를 도구가 실행했지만 실제 문에는 닿지 않는다. 이때 관측은 특정 접촉점이 아니라 **실행 구간 전체에서의 비접촉**이다. [원문 Fig. 4, §IV-C, PDF p. 7]

저자들은 그 구간의 모든 tool pose가 차지한 영역을 포함하는 최소 부피를 **motion envelope**라고 한다. Convex 도구·대상과 선형 tool motion을 가정하여 convex polyhedron으로 다룬다. 실제 접촉이 없었다면 corrected target과 이 envelope는 겹치지 않아야 한다.

Envelope face의 plane을 $(n_k,d_k)$, target vertices를 $P_{\mathrm{tgt}}$라 하면 다음과 같은 separating face 조건을 제시한다.

$$
\min_{p\in P_{\mathrm{tgt}}}(n_k^{T}p-d_k)>0.
$$

해당 최소값을 만드는 target vertex를 선택한다.

$$
p_k^e=\underset{p\in P_{\mathrm{tgt}}}{\arg\min}
(n_k^{T}p-d_k).
$$

원문의 distance-to-miss는 다음과 같다.

$$
\gamma(c_k)=\max(0,d_k-n_k^{T}p_k^e).
$$

즉, **지나갔는데도 안 닿았다는 관측을 설명하도록 모델의 겹침을 줄인다.** 그 결과 다음 planner가 더 실제적인 문 위치에 맞춰 접촉 경로를 만든다. Miss를 처리하는 목적은 재계획에서도 영원히 문을 피하게 하는 것이 아니라, 과거의 비접촉 경로와 양립하는 환경 모델을 얻는 것이다. [원문 §IV-C–D, PDF pp. 7–8]

원문은 separating-axis 방식의 edge 기반 miss constraint도 가능하다고 언급하지만 수식은 생략한다. 또한 miss에 대한 $e(c_k)$의 별도 정의는 주지 않는다. 따라서 구현을 확인하지 않고 “miss에서는 $e=0$으로 코딩했다”고 확정할 수 없다.

### 6.5 이상적 조건과 실제 최적화의 차이

이상적으로 모든 기록을 만족하는 보정값은 다음 조건을 충족한다.

$$
e(c_k,x)=0,
\qquad \gamma(c_k,x)=0,
\qquad k=1,\ldots,M.
$$

실제로는 noise와 모델 오차 때문에 모든 조건을 정확히 맞추기 어려우므로, 다음 절의 합성 cost를 최소화한다. Miss의 엄격한 부등식과 $\gamma=0$은 경계 접촉에서 완전히 같은 조건은 아니며, 원문은 그 경계의 numerical margin을 주지 않는다. [원문 §IV-C–D, PDF pp. 7–8]

## 7. 핵심 메소드 4 — 보정 최적화와 모호한 접촉 대응의 탐색

### 7.1 고정한 후보 조합에 대한 cost

$M$개 실패 사건에서 후보를 하나씩 고른 contact sequence를 $c=(c_1,\ldots,c_M)$라고 한다.

**원문 식 (9)**

$$
E(x;A,c)=
\sum_{k=1}^{M}e^{2}(c_k,x)
+\beta\sum_{k=1}^{M}\gamma^{2}(c_k,x)
+\alpha x^{T}\Sigma^{-1}x.
$$

| 항 | 역할 |
| --- | --- |
| orthogonal residual 제곱합 | 충돌 시 실제 접촉과 모델의 plane/edge separation을 맞춤 |
| lateral/miss residual 제곱합 | 유효 feature 겹침 또는 관측한 비접촉을 설명. $\beta$를 크게 두어 강조한다고 서술 |
| Mahalanobis regularization | 초기 camera parameters에서 지나치게 멀어지는 correction을 억제 |

$\alpha$가 크면 원래 calibration에 대한 신뢰가 커져 작은 correction을 선호한다. $\Sigma$는 파라미터 공간의 Mahalanobis 항에 사용되지만, full matrix와 실제 설정을 명시하지 않는다. 이 행렬을 측정 F/T covariance로 해석할 근거도 없다. 고정된 후보 조합의 $x$ 최적화에는 **Levenberg–Marquardt**를 사용한다. [원문 §IV-D, PDF p. 8]

### 7.2 왜 최적화 변수 $x$만 찾으면 끝나지 않는가

충돌 센서는 도구의 어느 vertex·edge가 어느 환경 face·edge와 닿았는지 알려 주지 않는다. 따라서 $k$번째 실패의 가능한 후보 집합 $\theta_k$에서 올바른 대응도 골라야 한다.

모든 실패에서 후보를 하나씩 선택하는 조합 수는 각 후보 수의 곱으로 증가한다. 원문은 모든 조합마다 LM을 풀어 최저 cost를 고르는 방식이 실패 횟수 $M$에 따라 지수적으로 비싸진다는 점을 지적한다. [원문 §IV-D, PDF p. 8]

### 7.3 Algorithm 1: OptimizationStep

실패 하나가 새로 들어올 때마다 다음 과정을 수행한다.

| 단계 | 원문 절차의 해설 |
| --- | --- |
| 입력 | environment $A$, 과거 후보 집합, 새 후보 집합 $\theta_M$, 이전에 저장한 $(c,x)$ 쌍들 $X_{M-1}$, $N_{\mathrm{samp}}$, $N_{\mathrm{best}}$ |
| 조합 생성 | Algorithm 2로 평가할 후보 sequence 집합 $C$를 만듦 |
| 연속 최적화 | 각 sequence마다 식 (9)를 최소화하는 correction을 계산 |
| 최선 correction | 평가한 sequence 가운데 가장 낮은 cost의 correction을 채택 |
| 기록 유지 | 낮은 cost의 $N_{\mathrm{best}}$개 sequence와 correction을 다음 단계에 보존 |
| 다음 시도 | corrected environment로 경로를 재계획 |

[원문 Algorithm 1, §IV-D, PDF p. 8]

여기서 “optimal”은 원문이 사용하는 명칭이다. 후보를 sampling하고 연속 문제에는 LM을 사용하므로, 이 절차가 모든 가능한 대응과 correction에 대해 전역 최적임을 보장하는 증명을 원문이 제시한 것은 아니다.

### 7.4 Algorithm 2: ContactCombinations

이 알고리즘은 **과거의 좋은 해를 확장하는 조합**과 **새로 무작위 탐색한 조합**을 함께 고려한다.

**과거 해의 확장:** 저장된 각 $(c,x)$에 대해 $A$를 보정하고, 새 실패의 후보 $z\in\theta_M$별 residual을 계산한다. 원문 Algorithm 2 line 21은 다음 기준으로 하나를 고른다.

$$
z^{\ast}=\underset{z\in\theta_M}{\arg\min}
\max\{e(z,x),\gamma(z,x)\}.
$$

이 $z^{\ast}$를 기존 sequence에 붙인다. 위 heuristic은 원문 그대로이며, signed $e$에 절댓값이나 제곱을 임의로 넣지 않았다. 식 (9)의 제곱합 cost와는 다른 선택 기준이다.

**무작위 탐색:** 나머지 $N_{\mathrm{samp}}-\lvert X\rvert$개는 각 실패의 후보 집합에서 하나씩 무작위 선택하여 만든다. 전체 조합 수가 이 budget보다 작으면 가능한 조합을 모두 사용한다. [원문 Algorithm 2, §IV-D, PDF pp. 8–9]

$N_{\mathrm{samp}}$는 검토할 조합 수를 제한하고, $N_{\mathrm{best}}$는 다음 보정까지 유지할 좋은 해의 수를 정한다. **$N_{\mathrm{best}}=0$은 실패 이력 자체를 지우는 것이 아니라, 과거의 낮은 cost 대응 조합을 재사용하지 않고 무작위 조합 선택에 의존하는 조건**이다. [원문 §IV-D, §VII-A, PDF pp. 8–9, 12–14]

### 7.5 장면 간 누적이 가능한 이유

새 cabinet을 관측하거나 기존 문의 각도가 바뀌면 새 scene을 만든다. Scene geometry는 해당 capture pose의 말단 frame에서 표현하고, 실패마다 scene을 연결한다. 과거 scene의 도구 pose·실패 기록을 보존하여 현재 correction의 cost에 함께 반영한다. [원문 §IV-D, §V-C, PDF pp. 8, 10]

이 구조의 기대는 **한 장면에서 발생한 실패를 이용해 센서 model을 개선하면 다른 장면에서도 이득을 얻는다**는 것이다. 따라서 뒤쪽 scene의 높은 첫 시도 성공률은 앞선 실패 데이터를 사용한 상태의 결과다. 각각을 아무 사전 보정도 없는 독립적인 zero-shot 시행으로 해석하지 않는다. [원문 §VI-B, §VII-A–B, PDF pp. 12–15]

## 8. 핵심 메소드 5 — 보정된 카메라로 vertex와 plane을 갱신하기

이 절은 Appendix A–B를 풀어 설명한다. 점 좌표를 직접 고치는 단계가 없으면, 카메라 $x$를 최적화하더라도 planner에 사용할 새로운 cabinet geometry를 만들 수 없다.

### 8.1 점 좌표의 원래 복원식

이미지의 homogeneous coordinate를 $\tilde m$, camera frame depth를 ${}^{C}z$로 쓴다.

**원문 식 (16)–(17), (19)–(20)**

$$
{}^{C}p={}^{C}zK^{-1}\tilde m,
\qquad p=R\,{}^{C}p+t
={}^{C}zRK^{-1}\tilde m+t,
$$

$$
p'={}^{C}z'R'K'^{-1}\tilde m+t'.
$$

$p$와 $p'$는 같은 image point를 원래/보정된 camera parameters로 계산한 말단 frame 좌표다. [원문 Appendix A, PDF pp. 17–18]

### 8.2 Intrinsic·extrinsic 효과를 $D(x)$에 모은다

**원문 식 (21)–(22) 및 식 (18) 아래 정의**

$$
D(x)=R\Delta R(\phi)(K+L)^{-1}KR^{T},
$$

$$
p'=\frac{{}^{C}z'}{{}^{C}z}D(x)(p-t)+t'.
$$

이 관계는 기존 모델 vertex를 다시 raw image에서 읽지 않고 correction에 따라 변환하는 데 사용된다. $D$는 회전행렬 하나가 아니라 intrinsic 변화까지 들어간 행렬이다. [원문 Appendix A, PDF pp. 17–18]

### 8.3 Depth ratio의 유도

**원문 식 (23)–(26)**

$$
\delta=\frac{\lambda}{z}-\kappa
=\frac{\lambda'}{z'}-\kappa',
$$

$$
\frac{{}^{C}z'}{{}^{C}z}
=\frac{\lambda'}{\lambda}
+\frac{\kappa-\kappa'}{\lambda}\,{}^{C}z'
=(1+h_z)-g_z\,{}^{C}z'.
$$

**원문 식 (27)**

$$
p'=\bigl((1+h_z)-g_z\,{}^{C}z'\bigr)D(x)(p-t)+t+s.
$$

보정된 depth가 $p'$에 의존하므로, 원문은 이를 말단 좌표로 다시 표현한다.

**원문 식 (28)–(30)**

$$
{}^{C}z'=
\begin{bmatrix}0&0&1\end{bmatrix}{}^{C}p',
\qquad
{}^{C}p'=\Delta R^{T}(\phi)R^{T}(p'-t-s).
$$

[원문 Appendix A, PDF p. 18]

### 8.4 최종 vertex correction

다음 정의를 사용한다.

$$
a(x)=g_z\begin{bmatrix}0&0&1\end{bmatrix}
\Delta R^{T}(\phi)R^{T},
\qquad
b(x)=a(x)(t+s)+1+h_z.
$$

**원문 식 (18)**

$$
p'=\bigl(b(x)-a(x)p'\bigr)D(x)(p-t)+t+s.
$$

$a$는 row vector, $b$는 scalar다. 따라서 $a(x)p'$는 scalar이며, 이 식은 depth correction 때문에 단순 강체 좌표변환에 그치지 않는다. 원문은 이 최종식에 $\kappa,\lambda$의 절댓값이 남지 않는다고 지적한다. [원문 Appendix A, PDF p. 17]

**대수적 해설:** $u=D(x)(p-t)$라고 놓으면 식 (18)은 아래처럼 정리할 수 있다.

$$
(I+u\,a(x))p'=b(x)u+t+s.
$$

이는 식 (18)의 직접적인 대수적 재배열이며 저자의 별도 번호식은 아니다. 계수행렬이 가역인 경우 선형계를 풀어 $p'$를 얻을 수 있다는 뜻이다. 저자 코드가 실제로 어떤 solver와 예외 처리를 쓰는지는 확인하지 않았다.

### 8.5 Plane correction

원문 식 (31)은 corrected plane을 다음과 같이 적는다.

**원문 식 (31)과 정의**

$$
\eta^{T}p=\rho,
$$

$$
\eta=\bigl(D^{-1}(x)-t\,a(x)\bigr)^{T}n+d\,a^{T}(x),
$$

$$
\rho=b(x)d+n^{T}\bigl(D^{-1}(x)(t+s)-b(x)t\bigr).
$$

그 후 $\eta$와 $\rho$를 $\lVert\eta\rVert$로 나누어 unit normal $n'$와 offset $d'$를 얻는다고 설명한다. 단순히 vertex들만 옮기는 것이 아니라, **접촉 residual 계산과 경로 생성에 필요한 plane normal·offset도 함께 수정**하는 단계다. [원문 Appendix B, PDF p. 18]

유도에서는 다음 역관계를 원래 plane 식에 넣는다.

**원문 식 (32)–(33)**

$$
p=\frac{D^{-1}(x)(p'-(t+s))}{b(x)-a(x)p'}+t,
$$

$$
\frac{n^{T}D^{-1}(x)(p'-(t+s))}{b(x)-a(x)p'}
+n^{T}t=d.
$$

**표기 주의:** 식 (31)은 $p$로 인쇄되어 있지만 직전 설명은 corrected plane이며, 식 (33)의 정리 대상 좌표는 $p'$다. 이 문서에서는 원문 식 (31)의 표기를 그대로 보존하고, $p/p'$ 혼용을 별도 주의사항으로 기록한다. [원문 Appendix B, PDF p. 18]

## 9. 핵심 메소드 6 — 보정된 모델에서 실제 문 열기 궤적까지

### 9.1 문 모델의 frame

| Frame·변수 | 정의 |
| --- | --- |
| $S_B$ | robot base |
| $S_E$ | robot end effector |
| $S_C$ | camera |
| $S_{E,\mathrm{capture}}$ | 해당 cabinet을 관측했을 때의 end-effector frame |
| $S_A$ | 힌지 axis frame. 원점이 축에 있고 z축이 회전축과 평행 |
| $S_{A'}$ | 문짝과 함께 z축 주위로 회전하는 frame |
| $S_L$ | door leaf frame |
| $S_D$ | 문짝 뒷면의 접촉 기준점 frame |
| $S_{\mathrm{TCP}}$ | gripper fingertip frame |
| $l=[l_x,l_y,l_z]^T$ | 원문이 정의한 문 크기 |
| $r=[r_x,r_y]^T$ | 힌지에 대한 문짝 상대 위치 |
| $\varphi$ | 문의 열림 각도. 닫힘은 0 |

여기서 문 각도 scalar $\varphi$와 camera correction rotation vector $\phi$를 구분한다. [원문 §V-A–B, PDF pp. 9–10]

### 9.2 힌지 회전과 접촉 기준점

**원문 식 (10)**

$$
{}^{A}T_{A'}(\varphi)=
\begin{bmatrix}R_z(\varphi)&0\\0&1\end{bmatrix}.
$$

원문은 닫힌 상태에서 $S_D$의 관계를 다음과 같이 준다.

**원문 식 (11), 인쇄 표기 유지**

$$
{}^{A'}T_D=
\begin{bmatrix}
0&0&-\mu&r_x-\mu\frac{s_x}{2}\\
\mu&0&0&r_y-\frac{s_y}{2}\\
0&-1&0&\frac{s_z}{2}\\
0&0&0&1
\end{bmatrix}.
$$

$\mu=-1$은 축이 문짝 왼쪽, $\mu=1$은 반대쪽이다. **직전 문 크기는 $l$로 정의했지만 이 식의 성분은 $s_x,s_y,s_z$로 인쇄되어 있다.** 앞 절의 camera translation correction $s$와 동일한 물리량으로 해석하지 않으며, 원문 기호 불일치로 남긴다. [원문 §V-A, Fig. 5, PDF p. 9]

### 9.3 Base frame에서의 문 운동

**원문 식 (12)–(13)**

$$
{}^{B}T_A=
{}^{B}T_{E,\mathrm{capture}}\,{}^{E}T_C\,{}^{C}T_A,
$$

$$
{}^{B}T_D(\varphi)=
{}^{B}T_A\,{}^{A}T_{A'}(\varphi)\,{}^{A'}T_D.
$$

카메라 보정 후에는 cabinet feature와 base에 대한 axis pose도 갱신한다. 즉, 접촉으로 보정한 camera transform이 최종적으로 이 kinematic chain과 경로 생성에 영향을 준다. [원문 §V-B–C, PDF pp. 9–10]

### 9.4 Contact pose 후보 생성

문짝 뒷면의 수직선에서 접촉 위치를 sampling하고, 여러 gripper orientation을 결합해 $^{D}T_{\mathrm{TCP}}$ 후보를 만든다. FCL로 그리퍼–문짝 collision을 검사하여 유효한 후보만 남긴다. Fig. 5의 진한 초록색 선이 이 sampling 구간이다. [원문 §V-B, PDF pp. 9–10]

높이·각도의 정확한 간격과 후보 수는 본문에 주어지지 않는다. 이 방법이 특정 접촉 위치를 센서로 추정해 즉시 선택하는 것과도 다르다. **업데이트된 모델에서 후보를 생성하고 기하학적으로 검증**한다.

### 9.5 접촉점에서 역으로 approach·insertion 위치 계산

실행은 approach → insertion → contact 순서지만, 생성은 contact pose에서 뒤로 계산한다.

| 생성 단계 | 원문 규칙 |
| --- | --- |
| Contact → insertion | TCP의 음의 z방향으로 후퇴. 그리퍼 bounding sphere가 cabinet outer/top face의 plane과 교차하지 않을 때까지 이동 |
| Insertion → approach | $S_D$의 음의 z방향으로 후퇴. bounding sphere가 문 앞면 plane과 교차하지 않는 위치를 approach point로 설정 |

원문 Fig. 6은 두 후퇴 방향이 서로 다른 frame을 기준으로 한다는 점을 보여 준다. 이를 그냥 “같은 방향으로 두 번 후퇴”로 바꾸면 안 된다. [원문 §V-B, Fig. 6, PDF p. 10]

### 9.6 Door-opening pose와 joint trajectory

**원문 식 (14)**

$$
{}^{B}T_E(\varphi_k)=
{}^{B}T_D(\varphi_k)\,
{}^{D}T_{\mathrm{TCP}}\,
\bigl({}^{E}T_{\mathrm{TCP}}\bigr)^{-1}.
$$

각 door angle에서 IK로 $q_k$를 구한다.

**원문 식 (15)**

$$
Q=(q_{\mathrm{approach}},q_{\mathrm{insertion}},q_0,\ldots,q_{n-1}).
$$

환경·self collision을 검사하고, joint-space의 점들 사이 Chebyshev distance가 45° threshold 이내인 경로를 남긴다고 설명한다. 이는 원문이 smoothness를 설명하는 조건이며, 시간 파라미터화·가속도·jerk 한계나 저수준 controller의 수식까지 제공한 것은 아니다. **경로의 45° 조건과 실험의 목표 문 열림 45°는 다른 값**이다. [원문 §V-B, PDF p. 10]

실험에서는 feasible trajectory/contact point를 무작위 선택한다. 원문에 최단거리·최소토크 기준으로 하나를 최적 선택한다는 규칙은 없다. [원문 §VI-A–B, PDF pp. 11–12]

## 10. 실험 구성 — 학습 환경이 아니라 보정 알고리즘 평가

### 10.1 RL·GAN과 구분

이 논문에 RL reward, PPO/SAC 설정, GAN loss가 없는 것은 세부 학습법을 생략했기 때문이 아니라 **제안 방법 자체가 그런 학습을 사용하지 않기 때문**이다. 식 (9)는 각 실패 후의 camera correction을 구하는 최적화 cost다. Offline calibration도 policy training이 아니라 같은 보정 절차를 미리 수행하는 단계다. [원문 §IV-D, §VI-B, §VII-D, PDF pp. 8, 12, 16–17]

### 10.2 Simulation scene와 camera error 생성

시뮬레이션에서는 polyhedral cabinet의 크기와 pose를 로봇 reach 안에서 uniform sampling한다. Camera reference parameters는 실물 RGB-D 시스템의 값을 이용하고, calibration perturbation으로 만들어진 **estimated geometry**로 경로를 계획한다. 실제 tool–cabinet 관계는 GT geometry로 평가한다. [원문 §VI-A, PDF p. 11]

Table 1의 perturbation parameter와 variance 대응은 다음과 같다.

| 보정 파라미터 계열 | 원문의 variance 기호 |
| --- | --- |
| $g_x,g_y$ | $\sigma_{g,xy}^{2}$ |
| $h_x,h_y$ | $\sigma_{h,xy}^{2}$ |
| $g_z$ | $\sigma_{g,z}^{2}$ |
| $h_z$ | $\sigma_{h,z}^{2}$ |
| $\phi_x,\phi_y,\phi_z$ | $\sigma_{\phi}^{2}$로 대응 표기 |
| $s_x,s_y,s_z$ | $\sigma_s^{2}$ |

Intrinsic correction과 translation correction은 zero-mean normal distribution에서 표본을 만든다고 설명한다. Orientation은 **unit sphere의 방향 $u$를 선택하고 scalar $\psi\sim\mathcal{N}(0,\sigma_\phi^2)$를 곱한 rotation vector**로 생성한다고 서술한다. 이를 별도 근거 없이 독립 xyz rotation noise로 바꾸지 않는다. [원문 §VI-A, Table 1, PDF p. 11]

Estimated model과 GT model의 대응 vertex 간 최대 거리가 $d_{\mathrm{vtx}}$보다 크면 해당 camera perturbation을 버리고 다시 sampling한다. 따라서 큰 calibration noise 조건도 **vertex 오차 상한으로 제한된 분포**다. [원문 §VI-A, PDF p. 11]

### 10.3 Simulation의 성공 기준은 전체 45° opening이 아니다

시뮬레이션에서 평가하는 action은 단순화된 두 단계다.

| 단계 | 내용 |
| --- | --- |
| 1 | 도구를 door contact point 근처까지 배치 |
| 2 | 문짝을 개방 방향으로 미는 동작 |

경로 시작점은 contact point에서 end-effector z축을 따라 0.4 m 떨어져 있고, 끝점은 door leaf에 수직인 방향으로 0.4 m 떨어진다. **첫 단계에서 의도치 않게 충돌하지 않고, 두 번째 단계에서 문짝 뒷면에 접촉하면 성공**이다. 첫 단계 충돌 또는 두 번째 단계 miss이면 보정·재계획한다. [원문 §VI-A, PDF p. 11]

한 scene에서 최대 **8 actions**까지 실행하며 그 안에 성공하지 못하면 실패다. 이는 뒤의 실물 45° door-opening 검증과 같은 물리적 완료 기준이 아니다. 시뮬레이션 성공률을 “힌지 동역학을 포함해 문을 목표 각도까지 완전히 연 비율”로 확대하지 않는다.

### 10.4 Ablation의 데이터 구조

각 설정은 **1000 cabinet configurations = 50 sequences × 20 scenes**로 평가한다. Sequence 시작 시 camera parameters를 perturb하고 execution trace를 비운다. 같은 sequence의 뒤쪽 scene에는 이전 scene에서 축적한 실패 trace를 사용한다. 파라미터는 하나씩 바꾸고 나머지는 baseline으로 유지한다. [원문 §VII-A, PDF p. 12]

**Table 3 — 실험 범위와 baseline**

| 파라미터 | 시험한 값 | Baseline |
| --- | --- | --- |
| $\sigma_{g,xy}$ | 2%, 5%, 10% | **5%** |
| $\sigma_{g,z}$ | 1%, 2%, 5% | **2%** |
| $\sigma_\phi$ | 1°, 2°, 3° | **2°** |
| $d_{\mathrm{vtx}}$ | 4 cm, 5 cm, 6 cm | **4 cm** |
| $\alpha$ | $10^{-4},10^{-5},10^{-6},10^{-7}$ | **$10^{-6}$** |
| $N_{\mathrm{best}}$ | 0, 50, 100, 500, 750 | **500** |

위 percentage·기호는 표의 표기를 따른다. 본문은 variance라는 말도 사용하지만 Table 3은 $\sigma$로 쓰고 있으며, 일부 percentage의 정규화 기준도 명확하게 전개하지 않는다. 이를 임의의 절댓값 camera parameter variance로 환산하지 않는다. [원문 §VI-A, §VII-A, Table 1·3, PDF pp. 11–13]

$N_{\mathrm{samp}}$, $\beta$, $\Sigma$ 전체, 표에 시험값이 없는 다른 camera perturbation variance들의 구체적인 설정은 본문에서 확인되지 않는다.

### 10.5 Real-world experiment 1: 사전 보정 없이 시작

같은 캐비닛을 테이블 위의 10개 무작위 pose에 배치한다. 각 pose에서 무작위 contact point를 고르고 문을 45° 연다. 첫 scene은 초기 visual estimate만 사용한다. 실패하면 보정하여 같은 위치에서 재시도하고, 성공한 후 다음 scene으로 이동한다. 다음 scene의 첫 행동에는 과거 보정 정보가 이미 반영된다. [원문 §VI-B2, PDF p. 12]

### 10.6 Real-world experiment 2: offline calibration을 먼저 수행

먼저 3개 무작위 cabinet pose에서 문짝 뒷면의 위·중간·아래 세 위치에 성공적으로 접촉하는 절차를 수행한다. 실패마다 보정하고 tactile이 접촉을 확인할 때까지 재시도한다. 그 후 얻은 correction으로 실험 1과 **동일한 10개 cabinet pose**에서 45° opening을 수행하며, 여기에서도 실패 시 추가 보정한다. [원문 §VI-B2, PDF p. 12]

따라서 비교는 **보정 없음 vs 보정 있음이 아니라, 온라인 보정만 vs 사전 접촉 보정 후 온라인 보정**이다. 두 실험 모두 실패 복구 기능을 사용한다. 별도 calibration target을 쓰지 않고 환경 내 cabinet으로 보정한다는 것이 저자들이 설명한 실무적 장점이다.

## 11. 실험 결과와 해석 범위

### 11.1 Simulation: camera perturbation

아래는 Table 4의 값을 그대로 옮긴 것이다. `Collisions`·`Misses`는 실행 중 발생한 모든 사건 수가 아니라, **8 actions 안에 성공하지 못한 task의 최종 실패 유형별 수**다. [원문 §VII-A, PDF p. 13]

| 설정 | Successes | Collisions | Misses | Success rate |
| --- | --- | --- | --- | --- |
| Baseline | 996 | 4 | 0 | 99.6% |
| $\sigma_{g,xy}=2\%$ | 998 | 2 | 0 | 99.8% |
| $\sigma_{g,xy}=10\%$ | 997 | 3 | 0 | 99.7% |
| $\sigma_{g,z}=1\%$ | 999 | 1 | 0 | 99.9% |
| $\sigma_{g,z}=5\%$ | 997 | 3 | 0 | 99.7% |
| $\sigma_\phi=1^\circ$ | 995 | 4 | 1 | 99.5% |
| $\sigma_\phi=3^\circ$ | 998 | 2 | 0 | 99.8% |
| $d_{\mathrm{vtx}}=5\,\mathrm{cm}$ | 990 | 8 | 0 | 99.0% |
| $d_{\mathrm{vtx}}=6\,\mathrm{cm}$ | 995 | 5 | 0 | 99.5% |

**원문 불일치:** $d_{\mathrm{vtx}}=5$ cm 행은 990+8+0=998이어서 “각 설정 1000건”과 합계가 맞지 않는다. 이 문서는 collision을 임의로 10으로 고치거나 누락된 두 건을 다른 범주에 배정하지 않았다. 또한 본문의 “above 99%”와 이 행의 정확히 99.0%를 구분한다. [원문 Table 4, PDF p. 13]

### 11.2 Simulation: optimization parameter

| 설정 | Successes | Collisions | Misses | Success rate |
| --- | --- | --- | --- | --- |
| Baseline | 996 | 4 | 0 | 99.6% |
| $\alpha=10^{-4}$ | 988 | 12 | 0 | 98.8% |
| $\alpha=10^{-5}$ | 997 | 3 | 0 | 99.7% |
| $\alpha=10^{-7}$ | 996 | 4 | 0 | 99.6% |
| $N_{\mathrm{best}}=0$ | 964 | 30 | 6 | 96.4% |
| $N_{\mathrm{best}}=50$ | 994 | 6 | 0 | 99.4% |
| $N_{\mathrm{best}}=100$ | 996 | 4 | 0 | 99.6% |
| $N_{\mathrm{best}}=750$ | 996 | 4 | 0 | 99.6% |

과거의 낮은 cost 조합을 보존하지 않는 $N_{\mathrm{best}}=0$에서 성능이 가장 크게 떨어진다. 저자들은 이것을 **유망한 대응 조합의 재사용이 다음 correction을 좋은 해로 유도한다는 근거**로 설명한다. 큰 $\alpha$의 저하는 초기 calibration을 너무 신뢰하면 필요한 correction을 충분히 하지 못하기 때문이라고 해석한다. [원문 §VII-A, Table 4, PDF p. 13]

이 비교는 force-only/tactile-only ablation이 아니다. 센서 두 종류를 결합했기 때문에 성능이 몇 % 올랐다는 정량 결과로 바꾸어 해석하지 않는다.

### 11.3 Fig. 8–10: 시도 횟수가 줄어드는 양상

Fig. 8은 성공하기까지의 action 수 분포를, Fig. 9는 sequence 안의 scene index에 따른 평균 action 수를 보여 준다. 초기 scene에서는 correction이 없어 여러 번 시도하지만, 실패 정보를 축적한 뒤에는 대부분 적은 action으로 성공한다. 원문은 모든 설정에서 90% 이상이 2 actions 안에 성공한다고 서술한다. [원문 §VII-A, Fig. 8–9, PDF pp. 13–14]

단, 변화는 완전히 단조롭지 않다. Fig. 9에서 scene별 반등이 있으며, $N_{\mathrm{best}}=0$은 뒤쪽 scene으로 갈수록 action 수가 증가하는 경향을 보인다. Fig. 10은 baseline에서 첫 scene보다 뒤쪽 scene의 첫 시도 성공이 많아지는 것을 보여 준다. 정확한 bar count 전체는 표로 제공하지 않으므로, 여기서 그림을 통해 정수 데이터를 복원해 채우지는 않는다. [원문 Fig. 8–10, PDF p. 14]

### 11.4 Real-world: 최종 성공과 첫 시도 성공을 분리

| 비교 항목 | 사전 calibration 없음 | 사전 calibration 있음 |
| --- | --- | --- |
| 운영 단계의 평가 pose | 10개 | 동일한 10개 |
| 최종 door-opening 성공 | 10/10 | 10/10 |
| 첫 action 성공 — **본문 보고값** | 6/10 | 9/10 |
| 실패 시 처리 | 온라인 correction·재시도 | 온라인 correction·재시도 |
| 별도 사전 수집 | 없음 | 3개 cabinet pose에서의 접촉 보정. 본문은 26 actions라고 보고 |

[원문 §VII-B, PDF pp. 14–15]

100%는 **재시도를 포함한 최종 task 성공률**이다. 한 번의 동작으로 전부 성공했다는 의미도, 10종류 캐비닛으로 일반화했다는 의미도 아니다. 하나의 실물 cabinet을 여러 pose에 배치한 실험이며, offline calibration의 사전 접촉 비용도 존재한다.

**Fig. 11과 본문의 차이:** Fig. 11을 보면 사전 calibration 3 scenes의 표시값은 10·7·8 actions로 읽혀 합계 25가 되고, 이후 blue curve는 모두 1 action으로 보인다. 이는 본문의 26 actions·9/10 first-action successes와 일치하지 않는다. 위 표는 본문 보고값을 유지한 것이며, 그림값으로 본문을 수정하지 않았다. 원시 로그 확인 없이는 어느 쪽이 맞는지 확정할 수 없다. [원문 §VII-B, Fig. 11, PDF pp. 14–15]

### 11.5 모델 오차가 완전히 사라져야 성공하는 것은 아니다

실물 모델 정확도 지표는 **corrected door leaf의 $S_D$ 원점과 GT의 대응점 사이 Euclidean distance**다. 각 scene에서 첫 action 이전에 측정한다. 전체 vertex 오차나 full 6D pose error를 합친 값이 아니다. [원문 §VII-B, Fig. 12, PDF pp. 14–15]

저자들은 두 전략의 평균 distance가 3 cm 미만이라고 보고한다. 일부 scene의 큰 오차는 door height estimation 오류에서 비롯됐다고 설명하며, 틈의 허용 여유 때문에 해당 방향의 오차가 문 열기를 방해하지 않을 수 있다고 지적한다. **실패를 일으키지 않는 방향의 estimation error는 correction을 유발하지 않는다.** 따라서 성공률이 높다는 것만으로 camera의 모든 파라미터가 실제 값으로 정확히 복원됐다고 해석할 수 없다. [원문 §VII-B, PDF p. 15]

### 11.6 계산 시간

측정 대상은 실패 후 실행하는 **Algorithm 1의 correction step**이다. 전체 문 열기 시간이나 sensor-to-command latency가 아니다. 환경은 Ryzen 9 7900, RAM 32 GB, Docker이고 baseline 설정을 사용했다. [원문 §VII-C, PDF p. 15]

Fig. 14는 누적 실패 수 $M$이 늘어날수록 correction time이 대략 선형으로 증가하는 결과를 보여 준다. $N_{\mathrm{samp}}$를 고정하여 전체 후보 조합을 전수 조사하지 않기 때문이라고 설명한다. 초기 두 번은 가능한 조합이 budget보다 적어 시간이 짧다. [원문 §VII-C, Fig. 14, PDF pp. 15–16]

원문은 `average execution time per unsuccessful action`을 **67.91 ms/action**으로 보고한다. 그러나 Fig. 14의 correction time은 후반부에서 약 2초까지 늘어난다. 따라서 이 수치를 **각 correction 호출이 언제나 67.91 ms 안에 끝난다거나 제어 loop가 약 15 Hz라는 뜻으로 바꾸면 안 된다.** 해당 평균의 정규화·집계 구현은 코드 확인 없이는 추가 확정할 수 없다.

### 11.7 기존 문 열기 방법과의 비교

원문의 Table 5는 다음을 보고한다. 외부 연구를 동일 로봇·동일 문·동일 uncertainty에서 다시 실행한 head-to-head 실험이 아니라, **기존 문헌의 결과와 구조를 모은 비교**다.

| 원문의 방법 구분 | 센싱 | Recovery 설명 | 원문이 인용한 Sim / Real 성공률 |
| --- | --- | --- | --- |
| Kang [8], position-force | RGB-D, F/T | Table 5에는 별도 failure recovery 없음으로 분류 | — / 100%, 4 trials |
| Kang [8], RL | LiDAR, proprioception | Table 5에는 없음으로 분류 | 92% / 100%, 1 trial |
| Wang [6] | RGB-D, joint current | Table 5에는 없음으로 분류 | — / 90%, 20 trials |
| Vats [7] | proprioception | learned recovery policy | 92.4% / 81%, 70 trials |
| 본 연구 | RGB-D, F/T, tactile | camera model correction | 99.6% / 100%, 10 trials |

[원문 §VII-D, Table 5, PDF pp. 15–17]

Table 5의 platform dependence High/Low는 저자의 정성 분류이지 별도 측정 지표가 아니다. 본 연구의 “learning-based가 아님”도 **제안된 recovery/correction의 성격**을 뜻하며, 초기 문 검출에 THD를 사용하는 사실을 지우지 않는다. 실험 과업·대상·재시도 한도·noise 종류·평가 분모가 서로 달라, 성공률 숫자만으로 일반적인 성능 우열을 확정하지 않는다.

## 12. Limitation — 저자들이 밝힌 한계와 범위 제한

### 12.1 정확한 접촉 대응이 불명확하다

Conclusion에서 명시한 핵심 한계는 **도구와 환경 사이의 정확한 접촉 위치를 모른다는 것**이다. 모든 가능한 contact candidates를 고려해야 하므로 계산 비용이 증가한다. 현재 시스템이 단일 tactile sensor를 장착했다는 사실이 곧 모든 충돌 위치를 직접 알 수 있다는 뜻은 아니다. [원문 §VIII, PDF p. 17]

### 12.2 보정 대상은 calibration 중심이며, segmentation 문제는 제외한다

원문은 segmentation 방법을 제안하지 않고, 모델 face와 실제 face가 대응한다고 가정한다. Camera random noise가 plane fitting으로 줄어든다는 전제 아래 systematic calibration error를 중심으로 다룬다. 따라서 잘못된 객체 인식·face association까지 자동으로 고치는 프레임워크라고 확장해서는 안 된다. [원문 §I, §IV-A, PDF pp. 2, 5]

이 항목은 저자들이 명시한 **문제 범위·가정**이며, Conclusion에 별도 Limitation으로 이름 붙인 첫 항목과 구분한다.

### 12.3 실패하지 않으면 남은 오차는 수정하지 않는다

저자들은 실패를 일으키지 않는 방향의 오차가 남을 수 있고, 그런 경우 camera parameter correction을 시도하지 않는다고 명시한다. 목적은 모든 방향의 metrology 정확도를 보장하는 것이 아니라, 실제 조작 실패를 줄이는 것이다. [원문 §VII-B, PDF p. 15]

### 12.4 기하·운동 모델의 범위

도구·대상은 polyhedral rigid-body 표현을 사용하고, miss constraint의 전개에서는 convexity와 선형 tool motion을 가정한다. 다양한 형태의 모든 물체나 비선형 운동 envelope에 대해 똑같은 수식이 그대로 성립한다고 입증한 것은 아니다. [원문 §IV-C, §VIII, PDF pp. 6–7, 17]

## 13. Future Work — 저자들이 제시한 향후 연구

### 13.1 Force vector로 접촉면 후보를 줄이기

저자들은 **contact force가 보통 surface normal과 정렬된다는 가정**을 활용하여, 측정한 힘 방향과 후보 surface normal을 비교하는 geometric consistency check를 제안한다. 맞지 않는 후보를 버리면 탐색 공간과 계산 시간을 줄일 수 있다는 구상이다. [원문 §VIII, PDF p. 17]

중요한 점은 이것이 **현재 식 (9)·Algorithm 1–2에서 이미 구현·검증된 필터가 아니라는 것**이다. Force direction threshold, 마찰에 의한 접선 성분 처리, 후보 축소율·시간 개선의 정량 결과는 제시하지 않는다.

### 13.2 Gripper 전체의 촉각 coverage와 정확한 contact localization

그리퍼 전체 표면을 덮고 접촉점을 정확히 제공하는 tactile sensors를 사용하면 실제 contact feature를 식별하는 데 도움이 될 것이라고 제안한다. 현재 한 fingertip의 sensor가 수행하는 접촉 유무 감시와 구분해야 한다. [원문 §VIII, PDF p. 17]

### 13.3 다른 조작 과업·로봇·센서로의 확대

저자들은 rigid polyhedral tool과 target object로 모델링 가능한 다른 조작에도 correction method가 적용 가능하다고 주장한다. 로봇 kinematic model을 교체하면 다른 플랫폼으로 옮길 수 있고, 접촉을 검출하는 다른 센서도 사용할 수 있다는 것이 원문 설명이다. [원문 §VIII, PDF p. 17]

이는 **제안한 표현과 모듈 구조의 확장 가능성**이며, 여러 로봇·다수 센서 제품·다른 조작 과업에서 transfer 실험을 수행했다는 뜻은 아니다. 실제 검증된 실물 플랫폼은 본문에 보고된 UR5 구성이다.

## 14. 미명시 사항과 원문 표기·수치 주의사항

이 절은 저자 명시 Limitation/Future Work와 분리한 **정리자의 원문 확인 기록**이다.

### 14.1 재현에 필요한데 본문만으로 확정할 수 없는 것

| 영역 | 미명시 또는 설명이 제한된 항목 |
| --- | --- |
| 센서 사양 | F/T·tactile의 범위·분해능·주파수·정확도, tactile taxel 배열·축·raw 단위, 정확한 camera model |
| Force/tactile preprocessing | 영점·중력 보정, filtering, threshold 수치·norm·축, 지속 시간·hysteresis, sensor fault 처리 |
| 도구 상태 기록 | 센서 timestamp와 tool pose 동기화, 충돌 정지 지연의 보상 |
| Contact candidates | feature 후보의 정확한 생성·사전 제거 규칙, edge 평행·수치 퇴화 처리 |
| Miss constraints | 생략된 edge 기반 분리 조건, miss의 orthogonal residual 정의, motion-envelope 수치 margin |
| Contact loss | 문 state 변경과 연결된 실패 구간의 구체적인 envelope 생성 절차 |
| 최적화 | $N_{\mathrm{samp}}$·$\beta$ 실사용 값, $\Sigma$ 전체, LM 초기값·damping·종료 조건·유효성 bound |
| 시뮬레이션 | 전체 cabinet size sampling 범위, 일부 noise variance 수치·percentage 정규화 기준, 접촉·힌지 동역학 설정 |
| Planning | 후보 높이·각도 간격, tool bounding-sphere 반지름, IK solver, 경로 시간 파라미터화 |
| 실물 제어 | 명령 인터페이스, control/feedback rate, 속도·가속도 제한, 별도 impedance/admittance 사용 여부 |
| 실물 평가 | 정량 contact force trace, 센서별 제거 비교, GT 모델 취득·정밀도, 운영 단계의 명시적 재시도 상한 |
| 계산 시간 | 67.91 ms/action 집계의 상세 정규화 코드 |

논문 첫머리의 공개 구현 링크는 [저자 GitLab 저장소](https://gitlab.com/vsimundic/visuo-force-tactile-door-opening)다. 이번 노트는 그 저장소의 코드를 읽거나 실행한 분석이 아니다. 위의 미명시 항목이 공개 코드에도 없다는 뜻은 아니다.

### 14.2 표기·설명 불일치

| 위치 | 원문에서 확인되는 문제 | 이 문서의 처리 |
| --- | --- | --- |
| 식 (11), §V-A | 문 크기는 $l$로 정의하지만 matrix에는 $s_x,s_y,s_z$ 사용. 앞의 camera translation correction도 $s$ | 식을 보존하고 다른 물리량을 동일시하지 않음 |
| 식 (31), Appendix B | corrected plane을 설명하지만 좌표를 $p$로 표기. 유도식 (33)은 $p'$로 정리됨 | 인쇄식 유지·prime 혼용 주의 |
| Algorithm 1 lines 4–7 | 계산한 후보는 $x_c^\ast$이나 비교·최솟값 갱신 줄은 $x^\ast$로 인쇄 | 의도는 본문 설명으로 해설하되 그대로 실행 가능한 검증 코드라고 하지 않음 |
| Algorithm 2 line 16 | $(c,x)\in\lvert X\rvert$처럼 집합의 원소가 아니라 cardinality 표기 사용 | 저장된 $(c,x)$ 쌍에 대한 반복이라는 본문 설명과 함께 기록 |
| Algorithm 2 line 21 | signed $e$와 nonnegative $\gamma$의 max로 새 후보를 선택 | 임의로 absolute/squared residual로 수정하지 않음 |
| Miss inequality와 penalty | strict separation은 $>0$, $\gamma=0$은 경계에서도 가능 | 실제 margin·접촉 tolerance 미확인 |
| Depth notation | §IV-A에서 $\delta$는 disparity인데 Appendix A 첫 문장은 depth라고 표현 | 정의된 depth model을 기준으로 설명하고 raw interface는 미확인 |
| Table 3·§VII-A·D | 표의 $\sigma$와 본문의 variance 표현이 혼용되고, p. 13에는 percentage perturbation을 degree로 적은 부분 존재 | Table 3의 %·° 표기를 기준으로 보존 |
| Table 4, $d_{\mathrm{vtx}}=5$ cm | 성공·충돌·miss 합계 998, 전체 1000과 불일치 | 990·8·0 그대로 기록 |
| §VII-A와 Table 4 | camera 설정 모두 `above 99%`라는 서술과 정확히 99.0% 행 | 표의 정확한 값 우선 표시 |
| §VII-B와 Fig. 11 | 본문은 offline 26 actions 및 이후 9/10 첫 시도 성공. 그림은 초기 10·7·8, 이후 모두 1로 읽힘 | 본문 보고값과 그림의 차이를 나란히 기록 |
| §VI-A와 §VII-D | 첫 설명은 8 actions 한도, 비교 설명에는 8 failed actions라고 표현 | 실험 절의 8 total actions 정의를 채택하고 혼용 기록 |
| Table 5의 성공률 비교 | 다른 문·다른 로봇·다른 평가 조건의 문헌 결과 병치 | 동일 조건 재실험이나 센서 결합 정량 ablation으로 해석하지 않음 |

### 14.3 결과가 직접 입증하지 않는 것

높은 성공률은 본 실험의 correction·retry 체계가 잘 작동했음을 뒷받침한다. 하지만 **힘을 연속 제어하여 충격을 줄였다는 정량 결과**, **F/T와 tactile의 각 기여율**, **카메라의 모든 true parameter를 식별했다는 증명**, **어떤 segmentation 오류도 복구한다는 보장**은 제시하지 않는다. 이것은 원문에 없는 성과를 추가하지 않기 위한 구분이며, 저자들이 스스로 목록화한 Limitation과는 다르다.

## 15. 원문을 다시 읽기 위한 위치 안내

| 찾을 내용 | 원문 위치 |
| --- | --- |
| 문제 상황·오류 유형·기여 | §I, PDF pp. 1–2 |
| 센서 fusion·failure recovery 관련 연구 | §II-A–B, PDF pp. 2–3 |
| 센서 장착 사진 | Fig. 1, PDF p. 2 |
| FSM·regular/error transitions | §III, Fig. 2, PDF pp. 3–5 |
| F/T 충돌·tactile miss/loss·Recapture | §III-D–E, PDF p. 5 |
| 내·외부 camera correction 정의 | §IV-A, 식 (1)–(8), PDF pp. 5–6 |
| Vertex–face·edge–edge·motion envelope | §IV-C, Fig. 3–4, PDF pp. 6–7 |
| Cost와 contact sequence sampling | §IV-D, 식 (9), Algorithm 1–2, PDF pp. 8–9 |
| Door model·frame | §V-A, 식 (10)–(12), Fig. 5, PDF p. 9 |
| Contact pose·approach/insertion·IK trajectory | §V-B, 식 (13)–(15), Fig. 6, PDF p. 10 |
| Scene·failure trace 누적 | §V-C, PDF p. 10 |
| Simulation perturbation·8-action 기준 | §VI-A, Table 1, Fig. 7, PDF p. 11 |
| 실물 센서명·cabinet 값·offline calibration | §VI-B, Table 2, PDF pp. 11–12 |
| Ablation 조건·수치 | §VII-A, Table 3–4, PDF pp. 12–13 |
| Action 수의 변화 | Fig. 8–10, PDF p. 14 |
| Real first-try·최종 성공·모델 오차 | §VII-B, Fig. 11–13, PDF pp. 14–16 |
| 계산 시간 | §VII-C, Fig. 14, PDF pp. 15–16 |
| 기존 방법의 문헌 비교 | §VII-D, Table 5, PDF pp. 15–17 |
| 명시 Limitation·Future Work | §VIII, PDF p. 17 |
| Vertex correction 유도 | Appendix A, 식 (16)–(30), PDF pp. 17–18 |
| Plane correction 유도 | Appendix B, 식 (31)–(33), PDF p. 18 |
| References | PDF pp. 18–19 |

## 16. 논문 내용만으로 정리한 결론

이 연구의 감각–행동 연결은 **센서 신호 → 실패 사건 → 도구 pose/경로의 기하학적 제약 → 카메라 보정 → 환경·문 모델 갱신 → 새 joint trajectory**다. F/T는 접근·삽입의 충돌을, fingertip tactile은 opening의 기대 접촉·접촉 소실을 감시한다. 정확한 접촉 위치가 불명확하므로 여러 feature 조합을 탐색하며, 이전의 낮은 cost 조합을 보존해 계산량과 성공률 사이를 조정한다.

실험은 이 correction이 과거 실패를 활용해 다음 scene의 시도 횟수를 줄일 수 있음을 보여 준다. 다만 simulation은 뒤쪽 문 면에 성공적으로 접촉하는 단순화된 시험이고, 실제 45° door opening은 하나의 cabinet을 여러 pose에 놓은 실험이다. 힘 방향 활용과 gripper 전체의 정밀 촉각은 구현한 메소드가 아니라 미래의 개선 방향이다. [원문 §III–VIII, PDF pp. 3–17]

---

### 문서 검증 기록

2026-09-16: 수식 214개(블록 38개, 인라인 176개)의 로컬 MathJax 구문 검사에서 오류가 없었고, 블록 수식 전체를 SVG로 렌더링하여 확인했다. 표 25개의 열 구조를 점검하고 로컬 Chromium에서 수식·표가 포함된 문서 표시를 확인했다. 원문 이미지 19쪽을 확인했으며, 원문 내부 불일치는 위 14절에 남겼다. 이 검사는 논문 알고리즘의 실행·재현이나 실제 GitHub 웹페이지의 최종 표시 확인을 의미하지 않는다.
