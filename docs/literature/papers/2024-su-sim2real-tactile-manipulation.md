# Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning — 원문 상세 정리

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [원래 등록 항목: USER-P002](../reviews/user-found-papers.md#user-p002)

## 0. 논문 정보와 확인 범위

| 항목 | 내용 |
| --- | --- |
| 제목 | **Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning** |
| 저자 | Entong Su, Chengzhe Jia, Yuzhe Qin, Wenxuan Zhou, Annabella Macaluso, Binghao Huang, Xiaolong Wang |
| 공동 기여 표기 | Chengzhe Jia, Yuzhe Qin, Wenxuan Zhou, Annabella Macaluso에 † 표시. 첫 페이지의 공동 기여 설명을 따른다. |
| 확인 버전 | **arXiv:2403.12170v1, 2024-03-18**, 사용자 제공 PDF 8쪽 |
| 원문 위치 | [arXiv v1](https://arxiv.org/abs/2403.12170v1) · [v1 PDF](https://arxiv.org/pdf/2403.12170v1) |
| 게재 정보·DOI | 제공된 v1에는 학술대회·저널 게재 정보와 출판사 DOI가 없다. 이후 출판 여부·다른 버전의 변경 사항은 이번 정독에서 확인하지 않았다. |
| 원문이 안내하는 자료 | [저자 프로젝트 페이지](https://tactilerl.github.io/). 주소만 기록하며 페이지·영상·코드의 현재 내용은 별도 확인하지 않았다. |
| 문헌 관리 ID | 사용자 별도 발굴 논문 **USER-P002**. 기존 R1–R7·IROS-S01–S05에 추가하는 항목이 아니다. |
| 정리일 | 2026-09-18 |
| 확인한 범위 | 본문 §I–VI, 번호 없는 reward 수식, Fig. 1–5, Table I–III, References [1]–[51]. 본문은 PDF pp. 1–6, 참고문헌은 pp. 7–8이며 부록은 없다. |
| 확인하지 않은 자료 | 코드·설정·체크포인트·원시 실험 자료·보충 영상, 인용된 선행논문의 개별 원문, 제조사 데이터시트, 최신 출판본 |
| 원문 PDF SHA-256 | `304b60f5e85b07ee0383713a686f2c442d2aad38ea03a6302c5bf3aeaf3ea32a` |

이 문서는 **첨부된 v1 자체**의 문제, 관련 연구, 센서와 접촉 표현, RL 학습, 실험, 저자 명시 한계·향후 계획을 정리한다. 다른 연구 주제에 대한 적용안은 넣지 않는다. `[원문 §…, PDF p.…]`는 첨부 PDF의 위치이며, `[15]` 등은 이 논문의 참고문헌 번호다. 원문 문장을 식으로 풀어 쓴 부분은 **해설용 재구성**으로 구분한다. 원문에 없는 구현값을 일반적인 PPO 설정이나 다른 DIGIT 논문에서 가져오지 않는다.

**핵심:** 두 손끝 DIGIT의 촉각 영상을 RGB·Diff·Binary로 달리 표현하여, 다양한 물체의 **지지면을 이용한 pivoting**을 PPO로 학습하고 실물에 추가 학습 없이 적용한다. Binary는 **센서별 1비트가 아니라 64×64 픽셀의 접촉 패턴**이다. 실행 입력에는 촉각뿐 아니라 관절 고유감각과 목표 각도도 들어간다. 주된 연구 질문은 새로운 RL 알고리즘보다 **어느 촉각 표현이 물체 다양성과 sim-to-real 차이에 강한가**이다. [원문 §I, §III–IV, Fig. 1–2, PDF pp. 1–3]

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1–2 | 문제 정의·실제 과업 범위, Related Work |
| 3–4 | 로봇·센서 사양, 정책 입력과 학습·평가 정보의 구분 |
| 5–6 | 시뮬레이션의 힘→변형→영상, RGB·Diff·Binary·augmentation |
| 7–8 | PPO 구성, randomization, reward 각 항과 미명시 구현 |
| 9–11 | 비교군·평가 정의, Table I–III 전체 수치, 그림 해설 |
| 12–14 | 저자 명시 Limitation, Future Work, 원문 불일치·재현 정보 누락 |
| 15 | 원문 위치와 문서 검증 범위 |

## 1. 제시하는 문제 상황과 실제 과업

### 1.1 문제는 촉각 정책의 미지 물체 일반화와 실물 이전이다

저자들은 촉각으로 물체를 조작하는 정책이 **훈련에서 보지 못한 다양한 물체에도 동작해야 한다**는 문제를 제시한다. 손끝의 부분 접촉만으로 전체 물체의 형상·자세를 먼저 추정하면 추정 오차가 제어에 전달될 수 있다. 반면 촉각 영상에서 행동을 직접 학습하면 명시적인 추정 단계를 피할 수 있으나, 실물 RL에는 많은 상호작용이 필요해 다양한 물체를 충분히 경험시키기 어렵다. [원문 Abstract·§I, PDF p. 1]

이 연구는 다양한 물체와의 상호작용을 시뮬레이션으로 옮긴다. 그러나 시뮬레이션의 조명·젤 변형·영상 형성이 실제 DIGIT와 다르고, 실제 센서끼리도 제조 및 젤 차이가 있다. 따라서 문제는 단순히 시뮬레이터를 사용하는 것에서 끝나지 않는다. **정책에 제공하는 촉각 표현에서 과업에 필요한 접촉 패턴은 남기고, 두 도메인 사이에서 불안정한 영상 세부는 줄여야 한다**는 것이 저자들의 접근이다. [원문 §I, §III-B, PDF pp. 1–3]

### 1.2 Pivoting의 목표와 시작 조건

과업은 그리퍼가 잡고 있는 물체를 **그리퍼에 대한 상대 목표 각도**로 돌리는 것이다. Fig. 1·2·5에는 물체의 다른 부분이 지지면과 접촉하는 초기·최종 상태가 나타난다. 즉, 물체를 공중에서 단순히 손목과 함께 강체 회전시키는 문제나, 바닥 위 자유 물체를 목표 위치까지 운반하는 평면 pushing과는 다르다. [원문 §IV Task Definition, Fig. 1–2·5, PDF pp. 1, 3, 6]

그리퍼 폭은 **초기에 물체를 잡도록 설정하고 조작 중에는 일정하게 유지**한다. 정책은 말단의 평면 병진과 한 축 회전만 제어한다. 초기 파지 자체를 찾는 행동, 손가락 폭을 바꾸는 재파지, 능동적인 파지력 조절은 제시된 action에 포함되지 않는다. [원문 §IV Action Space, PDF p. 3]

### 1.3 논문이 검증하려는 세 가지 질문

| 질문 | 논문의 비교 방식 |
| --- | --- |
| 실행 중 촉각이 필요한가? | 고유감각만의 정책, GT/추정 각도 정책, Point Cloud 정책, 촉각 없는 DAgger student와 비교 |
| 어떤 촉각 표현이 실물 전이에 좋은가? | RGB·Diff·Binary와 각 표현의 augmentation 유무 비교 |
| 물체 다양성이 실제 일반화에 기여하는가? | 단일/다중 category 훈련 및 평가, 미지 실물 물체와 soft supporting surface 평가 |

새로운 PPO 변형을 검증하는 것이 주목적이 아니라는 점은 원문이 action을 단순화한 이유에도 명시되어 있다. 따라서 기여를 특정 RL 업데이트 식의 새로움이나 정량 힘 추종 제어기로 설명하지 않는다. [원문 §IV Action Space, §V, PDF pp. 3–6]

## 2. Related Work — 원문이 구성한 비교 구도

아래는 **이 논문 §II의 설명**을 정리한 것이다. 인용된 모든 선행논문을 이번 작업에서 독립적으로 검증했다는 의미가 아니다.

### 2.1 Vision-based Tactile Sensing

| 연구 흐름 | 원문에서 든 사례 | 이 논문이 제시하는 관계 |
| --- | --- | --- |
| 광학 촉각 센서의 접촉 형상 관측 | GelSight [1], GelSlim [5], GelTip [6], OmniTact [7], TacTip [2], DIGIT [26] | 높은 공간 해상도와 접촉 형상 정보를 활용할 수 있다는 출발점 |
| 촉각→상태 추정→모델 기반 조작 | 접촉점 ICP 기반 pose 추정 [27], cable 조작에서 PCA 기반 접촉 형상 방향 추정 [14], [20] | 고차원 영상을 저차원 상태로 바꾸지만, 국소 관측의 추정 오류와 상세 형상 정보 손실이 있을 수 있다고 설명 |
| 영상→행동의 end-to-end RL | [28]–[31] | 풍부한 입력을 직접 활용할 수 있으나 복잡한 접촉 역학 때문에 sim-to-real 차이가 남음 |
| 가까운 pivoting 사례 | Kim et al. [15], *Simultaneous tactile estimation and control of extrinsic contact* | 실물에서 접촉 변위를 추정하는 접근과 달리, 본 연구는 다종 물체 시뮬레이션 훈련과 표현 선택을 통해 미지 물체로 전이하려 함 |

저자들은 형상·자세 추정이라는 중간 목표를 항상 잘 풀어야 한다는 요구를 줄이고, 최종 조작에 충분한 영상 표현을 직접 정책에 주려 한다. 이는 정책 내부에서 물체 각도나 형상을 정확히 복원한다는 별도의 검증과는 다르다. [원문 §II Vision-based Tactile Sensing, PDF p. 2]

### 2.2 Sim2Real Transfer for Tactile Sensing

| 연구 흐름 | 원문이 설명하는 방법·제약 | 이 논문의 선택 |
| --- | --- | --- |
| 저차원 접촉 이진화 | FSR 이진화 [32], binary contact mode를 이용하는 [33], [34] | 양 도메인을 binary로 맞추는 원리를 고해상도 광학 영상에 적용할 때 어떤 정보를 남길지 검토 |
| 정교한 변형 시뮬레이션 | FEM 및 학습 기반 변형 모델 [35]–[39]. 정확도에 비해 계산비용이 RL에 부담된다고 설명 | 센서 영상의 완벽한 재현보다는 단순한 렌더링과 입력 표현 비교를 채택 |
| 도메인 간 영상 변환 | 자체 수집 데이터와 CycleGAN 등의 방법 [40]–[43] | 제안 방법에는 실제 대응 영상으로 학습하는 GAN을 넣지 않음 |
| 미분 가능한 접촉 시뮬레이션 | penalty 기반 모델 [44] | 원문은 실물의 다종·미지 물체 일반화 검증 범위에 차이가 있다고 설명 |

여기서 FEM·CycleGAN의 제약은 저자들이 문헌을 비교한 맥락이다. 모든 FEM 시뮬레이터나 영상 변환 방법이 일반적으로 사용할 수 없다는 독립적인 결론으로 확대하지 않는다. [원문 §II Sim2Real Transfer for Tactile Sensing, PDF p. 2]

## 3. 환경·로봇·센서와 상세 사양

### 3.1 실제 플랫폼에서 명시된 정보

| 항목 | 원문에서 확인한 내용 | 구분·미명시 사항 |
| --- | --- | --- |
| 로봇 구성 | 로봇 팔과 그리퍼, 양 손끝에 부착한 촉각 센서 2개 | 로봇 팔·그리퍼의 제조사와 모델명은 본문에 명시되지 않음. 그림 외형으로 모델을 지정하지 않음 |
| 촉각 센서 | **DIGIT 2개**, 서로 마주 보는 gripper fingertip에 장착 | Fig. 2와 §III의 설명 |
| 실제 관측 원리 | 접촉으로 바뀌는 젤의 광학 영상을 관측 | 실제 force vector를 N 단위로 회귀하는 센서 처리기를 제안하지 않음 |
| 정책 영상 크기 | **각 이미지 64×64** | 전처리된 정책 입력 해상도. DIGIT 내장 카메라의 native 해상도나 공간 정확도가 아님 |
| 고유감각 | Robot joint proprioceptive states | 관절 위치·속도 등의 정확한 구성과 전체 차원은 미명시 |
| 말단 제어 자유도 | xz 평면 병진, y축 회전 | **과업에서 허용한 3개 운동 성분**이며 팔의 물리적 총 자유도와 구분 |
| 그리퍼 폭 | 초기 파지 이후 고정 | 실제 폭 값·파지력·초기 파지 절차·gripper controller 미명시 |
| 지지면 | 물체 pivoting을 지지하는 표면. 실물에서 solid/soft table 비교 | 마찰계수·강성·표면 재료의 정량 사양 미명시 |
| 외부 object pose 센서 | 제안 촉각 정책은 외부 센서에 의한 물체 pose 추정을 사용하지 않음 | Point Cloud 비교군의 외부 시각 정보와 구분 |
| 각도 평가 장비 | Digital angle finder protractor | 실물 평가용. 모델·분해능·정확도 및 측정 반복 방법 미명시 |

[원문 §III, §IV Observation/Action/Evaluation Metric, Fig. 2–3·5, §V-C, PDF pp. 2–6]

### 3.2 원문에 없는 센서·제어 성능값

| 확인 항목 | 확인 결과 |
| --- | --- |
| 최대 힘·토크 또는 압력 측정 범위 | 미명시 |
| 힘 분해능·최소 검출 힘·정확도·감도 | 미명시 |
| 픽셀당 물리 길이·접촉점 위치 정확도·유효 감지 면적 | 미명시 |
| Native RGB 해상도·bit depth·camera frame rate | 미명시 |
| 센서 처리 지연·정책 주파수·로봇 제어 주파수 | 미명시 |
| 센서 젤의 재료·두께·강성·감쇠·개체별 calibration 수치 | 미명시 |
| 로봇 가반하중·reach·반복정밀도·물리적 최대 속도 | 미명시 |
| 말단 action에서 관절 명령으로 변환하는 IK·servo 구조 | 미명시 |

**64×64 영상, threshold, 평가 오차는 서로 다른 종류의 수치**다. 정책 입력 크기를 힘 분해능으로, 이진화 threshold를 센서의 최소 검출 힘으로, 최종 각도 오차를 센서 정확도로 바꾸어 기록하지 않는다. 제공된 v1에 없는 숫자는 DIGIT 제조사나 다른 논문에서 보충하지 않았다. [원문 §III–V, PDF pp. 2–6]

### 3.3 물체와 시뮬레이션 도구

시뮬레이션은 **SAPIEN**에 광학 촉각 렌더링을 추가한 구성이다. 저자들은 **PartNet과 Breaking Bad**의 다양한 물체를 사용하며, 시뮬레이션 훈련 물체 **22개**, 실물에서 보지 못한 물체 **16개**를 보고한다. Fig. 3(a)의 실물 그룹 표기는 **Spoon, Screwdriver, Pen**이다. 각 물체의 질량·마찰계수·치수 전체 목록과 dataset asset ID는 제공하지 않는다. [원문 §I, §III-A, §IV Domain Randomization, Fig. 3(a), PDF pp. 2–4]

## 4. 관측·학습 정답·평가 정보의 역할

### 4.1 제안 정책의 실행 입력과 출력

| 경로 | 정보 | 역할 |
| --- | --- | --- |
| 촉각 입력 | 두 손끝의 RGB 또는 Diff 또는 Binary 이미지 | 현재 국소 접촉 패턴을 정책에 제공 |
| 수치 입력 | 관절 고유감각, 목표 각도 등 task-related information | 로봇 상태와 목표 조건 제공 |
| 행동 출력 | x·z 방향 병진과 y축 회전 | 물체와 손가락·지지면의 상호작용을 바꾸는 말단 운동 |
| 정책에서 제외한 행동 | Gripper width | 초기에 정하고 조작 중 고정 |

원문이 말하는 **“only tactile”는 외부 물체 시각 추정이 없다는 맥락**으로 읽어야 한다. 실제 Observation Space에는 고유감각과 목표 정보가 포함되므로 “촉각 이미지 외에는 아무 입력도 없다”는 설명은 부정확하다. [원문 §IV, Fig. 2, PDF p. 3]

### 4.2 보상·평가 정보와 실행 관측을 혼동하지 않는다

접촉 센서 수, 물체의 목표 위치에 대한 거리, 현재·목표 각도의 차이는 **시뮬레이션 reward를 계산하는 정보**다. 이런 값이 reward에 사용된다는 사실만으로 현재 물체 GT pose가 제안 actor에 들어간다고 볼 수 없다. 정확한 simulator API와 contact 판정 로직은 원문에 없다. [원문 §IV Reward Function, PDF p. 3]

제안 actor와 critic은 같은 feature를 사용한다고 적혀 있다. 원문에는 critic에 별도의 물체 GT를 넣는 asymmetric actor–critic 구조가 제시되지 않는다. GT angle을 관측하는 것은 **Oracle Angle 비교군**이며, 실제 각도계는 **실물 결과 평가**에 사용한다. [원문 §IV Policy Training·Baselines·Evaluation Metric, PDF pp. 3–4]

## 5. 힘·접촉 정보 처리 I — 시뮬레이션에서 영상을 만드는 과정

### 5.1 물리 엔진의 힘에서 촉각 패턴까지

원문의 렌더링 경로는 다음과 같다.

```text
SAPIEN 물리 엔진의 resultant contact force
 → 힘과 deformation depth 사이의 선형 매핑
 → 적용된 normal force에 따라 렌더링할 물체 위치 조정
 → DIGIT 형상에 맞춘 gel mesh + 3개 광원
 → Phong model을 이용한 RGB tactile rendering
 → 선택한 RGB / Diff / Binary 전처리
 → PPO의 이미지 인코더
```

저자들은 TACTO와 유사한 파이프라인을 SAPIEN에 구현하며, 접촉력을 deformation depth로 바꾸는 **선형 매핑**을 사용한다고 설명한다. 이는 RL 중 모든 피부 변형을 고정밀 FEM으로 계산하는 방식과 다르다. [원문 §III-A, PDF p. 2]

중요한 것은 **힘의 사용 위치**다. 이 힘은 시뮬레이터가 접촉 영상을 생성할 때 사용하는 값이며, 제안 정책이 별도 F/T 센서로 측정해 입력받는 6축 wrench가 아니다. 또 실제 촉각 영상에서 이 매핑을 역으로 풀어 힘을 추정하는 알고리즘도 제시하지 않는다. [원문 §III-A, §IV Observation Space, PDF pp. 2–3]

### 5.2 렌더러 변경의 목적

TACTO의 원래 OpenGL 렌더러 대신 **PyTorch3D**를 사용하여 GPU tensor를 직접 생성한다. 저자들이 명시한 목적은 GPU–CPU 사이의 데이터 전송 overhead를 없애고 영상 생성을 빠르게 하는 것이다. 다만 실제 렌더링 FPS, 기존 방식 대비 배속, 병렬 환경 수, 학습 wall-clock time은 이 v1에 없다. [원문 §III-A, PDF p. 2]

### 5.3 이 설명만으로 재구현할 수 없는 부분

힘→깊이 매핑의 기울기·절편·단위·saturation, 복수 접촉의 합산 방식, gel mesh 세부 수치와 광원 파라미터는 명시되지 않는다. 물리 엔진의 마찰과 **촉각 영상에 나타나는 shear deformation을 어떻게 연결하는지**도 별도 모델로 전개하지 않는다. 따라서 RGB에 전단 방향·크기가 정량적으로 보존된다고 단정할 수 없다. [원문 §III-A의 제시 범위, PDF p. 2]

## 6. 힘·접촉 정보 처리 II — RGB, Diff, Binary

### 6.1 RGB: 광학 영상의 세부를 유지한다

RGB는 센서 또는 시뮬레이터의 원래 촉각 영상을 사용한다. 국소 접촉의 모양뿐 아니라 색·조명·밝기 분포가 함께 들어간다. 원문은 이런 영상 세부의 차이가 실물 전이를 어렵게 하는 요인이라고 설명한다. [원문 §III-B, §V-B, PDF pp. 3, 5–6]

### 6.2 Diff: 현재 영상과 무접촉 기준의 차이를 사용한다

원문의 문장 순서는 **force-free canonical image에서 current image를 빼고**, 각 픽셀의 RGB 값들을 평균하여 grayscale로 만드는 것이다. 이를 식으로만 옮기면 아래와 같다.

**해설용 재구성 — 원문 §III-B의 연산 순서. 원문에 번호가 부여된 수식은 아니다.**

$$
D_t(u,v)=\frac{1}{3}\sum_{c\in\{R,G,B\}}\left[I_{0,c}(u,v)-I_{t,c}(u,v)\right].
$$

여기서 $I_0$는 무접촉 기준 영상, $I_t$는 현재 영상이다. **직전 프레임과의 차분이 아니다.** 따라서 이 Diff만으로 optical flow나 시간 미분 특징을 직접 계산한다고 설명해서는 안 된다. [원문 §III-B, PDF p. 3]

원문은 절댓값 차분, 음수 clipping, unsigned 영상 연산, RGB별 전처리 또는 전체 normalization을 명확히 제시하지 않는다. 위 식은 문장에 적힌 순서를 해설한 것이지 코드의 signed/absolute 처리까지 검증한 구현식은 아니다. Fig. 5의 밝은 contact pattern만 보고 임의로 절댓값을 추가하지 않는다.

### 6.3 Binary: 접촉 패턴을 픽셀별로 남긴다

Binary는 Diff에 threshold $\phi$를 적용하여 **contacted/non-contacted pixel을 구분**한다. 중요한 차이는 다음과 같다.

| 구분 | 이 논문의 Binary |
| --- | --- |
| 이진화 단위 | 각 tactile image의 **픽셀** |
| 공간 정보 | 접촉 영역의 위치·윤곽·방향·공간 배치가 이미지 패턴으로 남음 |
| 제거하는 정보 | Threshold 이후 픽셀 강도의 연속적인 차이 |
| 제시된 입력 크기 | **센서별 64×64 이미지** |
| 해당하지 않는 설명 | “손끝 센서 하나를 접촉/비접촉 1비트로 줄인 정책” |
| 힘에 대한 해석 | Threshold를 넘은 영상 변화 패턴이며 N 단위의 압력·힘 분포가 아님 |

[원문 §III-B, §IV Observation Space, Fig. 2·5, PDF pp. 3, 6]

Threshold는 각 DIGIT의 제조 차이와 noise를 고려해 **센서별로 grid search**한다. Threshold를 올리면 noise를 줄일 수 있지만 일부 접촉 정보도 놓칠 수 있다는 trade-off를 저자들이 명시한다. 정확한 threshold 값, 탐색 범위·간격, 선택 지표, calibration에 사용한 표본 수는 없다. [원문 §III-B, PDF p. 3]

이 연구에서 Binary의 장점은 관측 벡터의 길이를 반드시 작게 만든다는 것이 아니다. 정책은 여전히 공간 패턴을 가진 영상을 받는다. **광학 세부를 덜 보존하는 표현이 실물에서 더 안정적일 수 있는지**가 비교의 핵심이다. [원문 §I·III-B·V-B, PDF pp. 2–3, 5–6]

### 6.4 양 손끝의 좌우 정렬

오른쪽 그리퍼의 tactile image를 **수평 flip**하여 왼쪽과 각도 정보의 방향을 맞춘다. 서로 마주 보는 손끝에서 얻은 거울상 표현을 정렬하는 조치다. 이 전처리와 두 이미지에 대한 encoder 공유를 함께 기록하되, 논문이 별도로 tactile correspondence loss를 학습했다고 설명하지 않는다. [원문 §III-B, §IV Policy Training, PDF p. 3]

### 6.5 Augmentation과 표현 자체를 분리한다

| 위치 | 원문에 적힌 처리 | 상세값 확인 수준 |
| --- | --- | --- |
| §III-B | Diff·Binary 이미지를 0–1 사이에서 random scaling | 무엇을 어떻게 scaling하는지 세부 연산은 미명시. 이를 특정 geometric resize 범위로 확정하지 않음 |
| §IV Baselines의 Aug 조건 | Random scale, erase | 적용 확률·erase 크기·sampling 분포·처리 순서 미명시 |
| RGB의 추가 Aug | Brightness, contrast, color hues 조정 | 조정 범위 미명시 |
| 결과 비교 | 각 표현의 비증강 조건과 `(Aug)` 조건을 구분 | Table I의 행 구분을 유지 |

§III-B의 일반적인 augmentation 설명과 §IV의 명시적 비증강/증강 비교는 함께 읽어야 한다. 모든 Binary 결과가 증강 정책인 것은 아니다. **Table III의 정책명은 Tactile-Binary이며 `(Aug)`가 붙어 있지 않다.** [원문 §III-B·IV·V-B–C, Table I·III, PDF pp. 3–6]

### 6.6 “실물 학습 데이터 없음”과 센서 전처리 준비는 별개다

저자들은 실제 데이터로 학습하는 domain translation network 없이 시뮬레이션에서 정책을 학습하고 실물에서 fine-tuning하지 않는다고 설명한다. 동시에 실제 적용되는 표현에는 **무접촉 기준 영상과 센서별 threshold 선택**이 있다. 그러므로 이 주장을 “기준 영상 취득이나 센서별 조정조차 전혀 필요 없다”로 확장하지 않는다. Threshold grid search에 어떤 데이터를 사용했는지는 명시되지 않아, 그 비용이나 데이터 규모를 추정할 수 없다. [원문 §III, §III-B, §V 도입, PDF pp. 2–4]

GAN·CycleGAN은 §II의 선행연구에 등장할 뿐 **제안 파이프라인에는 없다**. 따라서 이번 논문에는 GAN loss나 sim-real 대응 영상 dataset을 학습하는 절차를 찾아 채울 이유가 없다. [원문 §II–IV, PDF pp. 2–4]

## 7. PPO 학습과 환경 randomization

### 7.1 네트워크와 행동 결정

```text
왼손끝 / 오른손끝 DIGIT 영상
 → 동일 종류의 RGB / Diff / Binary 표현
 → 오른손끝 영상의 수평 flip
 → 두 이미지에 가중치를 공유하는 encoder 적용
 → 관절 고유감각의 MLP feature와 결합
 → 같은 feature를 사용하는 actor와 critic
    ├─ actor: 허용된 x·z 병진, y축 회전 행동
    └─ critic: PPO 학습을 위한 가치 평가
```

Observation에는 목표 각도도 포함되지만, 목표를 어느 layer·branch에서 결합하는지까지는 설명하지 않는다. Encoder의 layer 수·채널·feature 차원, actor/critic MLP 크기, action distribution, frame stack·recurrent model은 미명시다. ConvNeXt는 **Angle Estimator 비교군**의 backbone이지 제안 tactile encoder의 명시된 구조가 아니다. [원문 §IV Policy Training·Baselines, PDF pp. 3–4]

정책은 명시적인 contact state classifier나 물체 각도 estimator를 먼저 출력하지 않고, 이미지와 고유감각에서 행동을 학습한다. “접촉 모양이 바뀌어 행동이 보정된다”는 설명은 이 입력→정책 경로와 ablation이 뒷받침하지만, 정책 내부가 특정 힘·마찰·각도를 따로 계산한다는 기계적 해석은 원문이 검증하지 않는다. [원문 §I·IV–V, PDF pp. 1, 3–6]

### 7.2 원문이 제시한 환경 변화 범위

| 항목 | 원문 범위·구성 | 해석상 주의 |
| --- | --- | --- |
| 물체 데이터 | PartNet·Breaking Bad의 다양한 물체 | 정확한 asset ID 미명시 |
| 훈련 물체 수 | 22개 | Category당 개수·분할 목록 미명시 |
| 지지면 높이 | 로봇 base에 대해 **0–20 cm** | 물체 높이나 센서 압입 깊이가 아님 |
| 물체 길이 | **13–18 cm** | 질량 randomization 범위와 혼동하지 않음 |
| 초기 물체 pose | Gripper에 대해 **165–195°** | 본문이 제시한 상대 각도 범위 |
| 목표 상대 각도 | **90–150°** | 월드 기준 절대 자세가 아니라 그리퍼 상대 목표 |
| 실제 평가 물체 | 보지 못한 16개 물체 | 모든 category·모든 물성 일반화를 뜻하지 않음 |
| 질량·마찰·관성·젤 물성 randomization | 별도 수치 미명시 | 형상 다양성으로 경험한 변화와 명시적 물성 sampling을 구분 |

범위는 그대로 기록하되, 원문이 명시하지 않은 uniform/Gaussian 분포나 모든 변수의 독립 sampling을 추가하지 않는다. [원문 §I, §IV Domain Randomization, Fig. 3(a), PDF pp. 2–4]

### 7.3 실제 학습 설정의 공개 수준

PPO를 사용하고 **5 seeds**로 훈련하며, Stable-Baselines3의 **default hyperparameter**를 사용했다고 적혀 있다. 그러나 라이브러리 version, 초기 learning rate, rollout length, batch size, epoch 수, discount, clipping·entropy coefficient 등을 이 v1의 표나 configuration으로 제시하지 않는다. 현재 라이브러리의 기본값을 확인하여 논문에 보고된 값처럼 대입하지 않았다. [원문 §IV Policy Training, PDF p. 3]

Fig. 4에는 reward와 success rate의 학습 곡선이 있지만, 이를 근거로 전체 simulation step 수·병렬 환경 수·GPU 모델·학습 시간을 확정할 수 없다. 도표의 0–400 가로축 수치에 대응하는 단위가 명료하게 정의되어 있지 않다. [원문 Fig. 4, PDF p. 5]

## 8. Reward — 어떤 상호작용을 학습하도록 했는가

### 8.1 총 보상

**원문 §IV의 번호 없는 reward 식**

$$
R=w_{\mathrm{contact}}r_{\mathrm{contact}}
+w_{\mathrm{position}}r_{\mathrm{position}}
+w_{\mathrm{angle}}r_{\mathrm{angle}}
-w_{\mathrm{penalty}}r_{\mathrm{penalty}}.
$$

원문은 접촉, 목표 위치에 대한 거리, 목표 각도, 행동 크기의 네 항을 사용한다. 아래에서는 직접 제시한 값과 설명만 있는 부분을 분리한다. [원문 §IV Reward Function, PDF p. 3]

### 8.2 Contact: 양 손끝 접촉을 유지하는 유인

접촉 보상의 기본값은 +0.5이며, 접촉하는 tactile sensor의 수에 따라 가중치를 0·1·2로 둔다.

**원문 설명의 수식화**

$$
r_{\mathrm{contact}}=0.5,\qquad
w_{\mathrm{contact}}\in\{0,1,2\}.
$$

따라서 이 항의 기여는 접촉 수에 따라 0·0.5·1이 된다. 이는 명시된 값의 대수적 해설이다. 목적은 처음 잡은 물체와의 접촉을 유지하여 회전 중 손끝이 떨어지는 것을 줄이는 것이다. **접촉력의 크기를 목표값에 맞추거나 압력을 일정하게 만드는 reward는 아니다.** 접촉 여부의 세부 simulator 판정 기준은 없다. [원문 §IV Contact, PDF p. 3]

### 8.3 Distance: 목표 위치까지의 거리 비율

**원문에 직접 제시된 식**

$$
r_{\mathrm{position}}=1-\frac{\mathrm{curdist}}{\mathrm{initdist}}.
$$

`curdist`와 `initdist`는 목표 위치까지의 현재·초기 거리다. 원문은 gripper contact가 있을 때 **가중치 10**을 사용하고, 목표에 가까워지는 경우를 보상하고 멀어지는 경우를 벌점으로 설명한다. 회전 중 접촉 유지와 목표 각도 도달에 기여하도록 둔 항이다. [원문 §IV Distance-based reward, PDF p. 3]

초기 거리와 같으면 0, 목표 거리 0이면 1, 초기보다 멀면 음수가 된다. 이 역시 원문 식의 해설이다. 다만 **target position의 생성법, 물체의 어느 점을 기준으로 하는지, contact가 없을 때의 항 처리**는 구체적이지 않다. 목표가 각도로 주어지는 과업이라고 해서 target position을 임의의 기하학 식으로 만들어 채워 넣지 않는다.

원문은 이 보상의 범위를 −1~1이라고 서술하지만, 표시된 식만으로 하한 −1이 보장되는 것은 아니다. 예를 들어 현재 거리가 초기 거리의 두 배를 넘으면 −1보다 작아진다. **Clipping·거리 제한·초기 거리 0 처리의 구현은 미명시**다. 원문 서술과 식의 표현 범위를 함께 기록한다.

### 8.4 Angle: 설명은 있으나 완전한 계산식·가중치는 없다

현재 각도와 목표 각도의 차이를 이용하고 distance 항과 비슷한 구조라고 설명한다. 그러나 **각도 항의 전체 식, 정규화 분모, wrap 처리, 가중치 수치**는 없다. 따라서 거리 식을 그대로 복사한 angle reward나 임의의 가중치를 이 논문의 확정 수식으로 적지 않는다. [원문 §IV Angle-based reward, PDF p. 3]

### 8.5 Action penalty: 원문은 norm의 제곱이다

**원문에 직접 제시된 식 — PDF에서 위첨자 2 확인**

$$
r_{\mathrm{penalty}}=\lVert a\rVert^{2},\qquad
w_{\mathrm{penalty}}=0.01.
$$

본문의 2는 아래첨자 norm 종류가 아니라 **위첨자 제곱**이다. 즉 이를 제곱 없는 L2 norm으로 옮기지 않는다. 이 항은 행동 크기를 억제하지만, action 단위·scaling이 미명시이므로 물리적인 속도·힘 상한을 보장하는 항으로 해석할 수 없다. [원문 §IV Action penalty, PDF p. 3]

### 8.6 학습 목표와 힘 제어의 경계

네 항은 **접촉을 유지하면서 물체의 목표 위치·각도로 이동하고 큰 행동을 피하는 것**을 유도한다. 여기에는 측정 wrench 추종 오차, 법선력 허용 구간, shear force penalty나 impulse threshold가 명시되어 있지 않다. 제안 정책이 촉각으로 상호작용을 보정한다는 것과, 물리 단위의 힘을 명시적으로 최적화한다는 것은 다르다. [원문 §IV Reward Function, PDF p. 3]

## 9. 비교군과 평가 방법

### 9.1 비교군별로 무엇을 바꾸는가

| 비교군 | 관측·구조 | 비교가 확인하는 지점 |
| --- | --- | --- |
| w/o Tactile | Proprioception만 사용하는 것으로 설명 | 실행 중 tactile을 제거한 경우. 목표 정보의 별도 처리 세부는 생략됨 |
| Oracle Angle | GT angle로 훈련 | 시뮬레이션에서 정확한 각도 관측을 사용할 때의 기준 |
| Angle Estimator | Binary 촉각 이미지에서 ConvNeXt로 object-in-hand pose/angle 추정 후 Oracle Angle 정책 사용 | 명시적 각도 추정 경유와 end-to-end tactile 정책의 차이 |
| PCA Angle | 촉각 영상에 PCA를 적용해 방향을 구한 뒤 Oracle Angle 정책 사용 | 접촉 패턴의 주방향이 물체 각도를 충분히 설명하는가 |
| Point Cloud | 지지 테이블을 제외한 point cloud, PointNet backbone | 외부 시각 관측으로 학습한 정책과의 비교 |
| DAgger | Tactile-Binary(Aug) teacher가 촉각 없는 student를 지도 | 훈련 시 tactile teacher의 지도가 실행 중 tactile을 대체하는가 |
| RGB·Diff·Binary | 영상 표현을 변경 | 광학 세부 보존 정도의 효과 |
| 각 표현의 `(Aug)` | 영상 augmentation 추가 | 표현 자체와 증강의 효과를 분리 |

[원문 §IV Baselines, §V-A, PDF pp. 4–5]

DAgger는 **비교군**이지 제안 PPO 정책 전체의 훈련법이 아니다. 또 Angle Estimator의 architecture를 제안 정책의 encoder로 옮기거나, Oracle Angle의 GT 입력을 모든 정책의 관측으로 확장해서는 안 된다.

### 9.2 성공 판정과 평가 수

원문은 angle deviation을 현재·목표 회전각의 차이를 **비율**로 표시한 지표라고 설명하고, 그 값이 **15% 미만이면 성공**이라고 정의한다. **15° 미만이 아니다.** 정확한 비율의 분모는 수식으로 제시하지 않으므로 허용 각도를 degree로 환산하지 않는다. [원문 §IV Evaluation Metric, PDF p. 4]

시뮬레이션은 5개 훈련 seed의 평균 성공률·오차를 사용한다. §V-A는 평가 episode 수가 **시뮬레이션 500, 실물 30**이라고 설명한다. §IV는 실물에서 총 30 episodes를 평가했다고 적는다. 표의 모든 행·물체·seed에 대해 이 수가 어떻게 배분되는지와 표의 ±가 어떤 반복 집계에서 계산되었는지는 명확하지 않다. [원문 §IV Evaluation Metric, §V-A Evaluation Variation, PDF pp. 4–5]

이 외에 지지면 일반화 실험에서는 **정책당 10 trials**를 언급한다. 이를 앞의 30 episodes와 합쳐 임의의 전체 시험 수를 만들지 않는다. 훈련·실행 episode의 최대 길이, 접촉 소실·낙하의 종료 조건, 실제 정책을 중단하는 로직 역시 미명시다. [원문 §V-C, PDF p. 6]

## 10. 실험 결과 — 전체 표와 해석 범위

### 10.1 Table I: 비교군 결과

아래 두 표는 원문 Table I을 읽기 위해 나눈 것이다. Deviation의 단위는 %, Success는 0–1 비율이며, **± 표기는 원문대로 유지**한다. `—`는 해당 셀에 결과가 없다는 뜻이지 성공률 0이 아니다.

| 방법 | Sim. deviation | Sim. success | Real deviation | Real success |
| --- | --- | --- | --- | --- |
| w/o Tactile | 34.84% ± 35.38% | 0.32 ± 0.23 | 23.55% ± 8.00% | 0.33 ± 0.09 |
| DAgger | 17.14% ± 3.04% | 0.66 ± 0.05 | 18.05% ± 10.04% | 0.50 ± 0.09 |
| Angle Estimator | — | — | 21.66% ± 10.98% | 0.60 ± 0.08 |
| Point Cloud | 16.2% ± 2.14% | 0.62 ± 0.010 | 19.32% ± 2.14% | 0.50 ± 0.11 |
| PCA Angle | — | — | 30.19% ± 14.32% | 0.23 ± 0.14 |
| Oracle Angle | 9.22% ± 1.43% | 0.96 ± 0.02 | — | — |

[원문 Table I 상단, PDF p. 5]

Oracle Angle은 시뮬레이션에서 0.96이지만, 실제 각도 추정을 앞에 붙이면 ConvNeXt는 0.60, PCA는 0.23이다. 저자들은 실제 noise 등으로 인한 추정 정확도 저하를 원인으로 설명하며, Fig. 3(b)에 PCA 성공·실패의 접촉 패턴과 추정 방향을 보여 준다. 이는 모든 estimator가 불필요하다는 결론이 아니라 **이 비교에서 사용한 추정 경유 방식의 결과**다. [원문 §V-A, Fig. 3(b), PDF pp. 4–5]

Point Cloud의 실물 성공률은 0.50이다. 저자들은 시뮬레이션과 실제 물체의 크기·형상 차이를 주요 실패 원인으로 설명한다. DAgger student는 teacher의 시뮬레이션 성능에 가까운 0.66을 얻었으나 실물에서는 0.50이 된다. 따라서 저자들의 해석은 **훈련 시 tactile teacher를 쓰는 것만으로 실행 중 tactile의 역할이 대체되지 않았다**는 것이다. [원문 §V-A, Fig. 3(c), PDF pp. 4–5]

### 10.2 Table I: 표현과 augmentation

| 촉각 표현 | Sim. deviation | Sim. success | Real deviation | Real success |
| --- | --- | --- | --- | --- |
| RGB | 14.34% ± 2.22% | 0.64 ± 0.10 | 18.03% ± 7.42% | 0.50 ± 0.14 |
| Diff | 15.67% ± 3.33% | 0.67 ± 0.10 | 16.04% ± 4.00% | 0.60 ± 0.04 |
| Binary | 15.31% ± 1.21% | 0.65 ± 0.05 | 12.25% ± 3.70% | 0.80 ± 0.04 |
| RGB (Aug) | 13.19% ± 2.77% | **0.75 ± 0.05** | 11.56% ± 6.44% | 0.76 ± 0.06 |
| Diff (Aug) | 14.35% ± 2.49% | 0.67 ± 0.03 | 14.51% ± 3.78% | 0.66 ± 0.09 |
| Binary (Aug) | **12.98% ± 2.47%** | 0.69 ± 0.07 | **11.15% ± 3.34%** | **0.80 ± 0.02** |

[원문 Table I 하단, PDF p. 5]

**비증강 표현의 시뮬레이션 성능은 비슷하지만 실물 성능은 크게 갈린다.** RGB·Diff·Binary의 시뮬레이션 성공률은 0.64·0.67·0.65인 반면 실물은 0.50·0.60·0.80이다. 이것이 정보를 더 세밀하게 유지한 표현이 반드시 실물에서 더 좋은 것은 아니라는 원문의 핵심 근거다. [원문 §V-B, Table I, PDF pp. 5–6]

증강의 효과는 RGB에서 가장 크다. 실물 성공률이 **0.50→0.76**, deviation이 **18.03%에서 11.56%로** 변한다. Binary는 실물 성공률 평균이 **0.80으로 동일**하고 deviation이 **12.25%에서 11.15%로** 감소한다. Diff도 성공률은 0.60→0.66이지만 시뮬레이션 deviation은 15.67%→14.35%로 변하는 등 지표별로 효과를 읽어야 한다. [원문 §V-B, Table I, PDF pp. 5–6]

따라서 “Binary가 모든 조건·지표에서 RGB보다 낫다”는 요약은 맞지 않는다. 증강 RGB의 시뮬레이션 성공률 0.75는 증강 Binary의 0.69보다 높다. 실물에서는 Binary 두 조건이 최고 성공률 평균을 공유한다. 저자들은 증강이 픽셀 값보다 접촉 패턴에 집중하도록 돕는다고 해석하지만, encoder 내부의 주목 영역을 별도로 정량 검증하지는 않는다. [원문 §V-B, PDF pp. 5–6]

### 10.3 Table II: 단일 category와 다중 category

`훈련 category`는 원문 Table II의 Method 아래 Objects 열이다. **Single category도 여러 물체 instance를 포함**한다. 물체 단 하나로 학습한 정책과 여러 물체 정책의 비교로 축약하지 않는다. [원문 §V-C, Table II caption, PDF pp. 5–6]

| 평가 category | 관측 | 훈련 category | Sim. deviation | Sim. success | Real deviation | Real success |
| --- | --- | --- | --- | --- | --- | --- |
| Single | w/o Tactile | Single | 24.45% ± 14.37% | 0.52 ± 0.37 | 26.68% ± 8.01% | 0.36 ± 0.09 |
| Single | Binary (Aug) | Single | 8.23% ± 1.14% | 0.91 ± 0.02 | 14.03% ± 4.60% | 0.54 ± 0.07 |
| Multi | w/o Tactile | Single | 72.12% ± 11.58% | 0.30 ± 0.05 | 23.55% ± 8.0% | 0.33 ± 0.16 |
| Multi | Binary (Aug) | Single | 46.71% ± 13.99% | 0.42 ± 0.13 | 21.72% ± 6% | 0.53 ± 0.19 |
| Multi | w/o Tactile | Multi | 34.84% ± 35.38% | 0.32 ± 0.23 | 23.55% ± 8.00% | 0.33 ± 0.09 |
| Multi | Binary (Aug) | Multi | **12.98% ± 2.47%** | **0.69 ± 0.07** | **11.15% ± 3.34%** | **0.80 ± 0.08** |

[원문 Table II, PDF p. 5]

다중 category 평가에서 Binary(Aug)의 single-category 훈련과 multi-category 훈련을 비교하면, 실물 성공률이 **0.53→0.80**, deviation이 **21.72%에서 11.15%로** 개선된다. 반면 촉각 없는 정책은 표에서 실물 성공률 평균이 0.33으로 같다. 저자들은 다양한 물체 학습과 tactile의 결합이 일반화에 도움이 된다고 해석한다. [원문 §V-C, Table II, PDF pp. 5–6]

Single-category 훈련의 single-category 평가에서도 실물 성공률은 0.54이며 시뮬레이션 0.91과 차이가 있다. 표에 없는 **multi-category 훈련→single-category 평가** 결과를 추정하지 않는다. 마지막 셀의 ±0.08은 Table I의 대응 행 ±0.02와 다르므로 두 표를 임의로 통일하지 않았다.

### 10.4 Table III: 미지 지지면

| 정책 | Solid deviation | Solid success | Soft deviation | Soft success |
| --- | --- | --- | --- | --- |
| w/o Tactile | 23.55% ± 8.00% | 0.33 ± 0.09 | 22.26% ± 11.70% | 0.21 ± 0.14 |
| Tactile-Binary | **12.25% ± 3.7%** | **0.80 ± 0.04** | **11.60% ± 3.83%** | **0.76 ± 0.09** |

[원문 Table III, PDF p. 6]

Binary의 실물 성공률은 soft surface에서 0.80→0.76으로 감소하지만 촉각 없는 정책의 0.21보다 높다. 이 결과는 원문에서 시험한 서로 다른 지지면에 대한 적응을 뒷받침한다. **마찰계수·강성 범위를 직접 식별하거나 제어한 결과**, 모든 종류의 지지면을 포괄한 결과는 아니다. 또 성공률 하락과 달리 평균 deviation은 두 정책 모두 조금 작아지므로 “모든 지표가 악화했다”고 표현하지 않는다. [원문 §V-C, Table III, PDF p. 6]

### 10.5 실물 성공률이 시뮬레이션보다 높은 이유에 관한 저자 설명

Binary 계열은 실물 성공률이 시뮬레이션보다 높게 나온다. 저자들은 **500회 대 30회라는 평가 규모 차이와 시뮬레이션의 더 다양한 물체·시나리오**를 가능한 이유로 든다. 이는 같은 분포의 paired test에서 현실이 본질적으로 더 쉽다고 증명한 결과가 아니다. 평가 구성 차이와 transfer 성능을 구분한다. [원문 §V-A Evaluation Variation, PDF p. 5]

## 11. 그림에서 확인할 수 있는 내용

| 그림·위치 | 읽을 내용 | 확대 해석하지 않을 내용 |
| --- | --- | --- |
| Fig. 1, p. 1 | 다양한 물체의 초기·최종 pivoting, 시뮬레이션 훈련과 실물 실행 | 그림의 성공 예시를 전체 실험 성공률로 사용하지 않음 |
| Fig. 2, p. 3 | 양 손끝 tactile, robot proprioception·target, policy와 action의 연결 | 외형으로 robot model을 추정하거나 tactile-only를 고유감각 부재로 해석하지 않음 |
| Fig. 3(a), p. 4 | 시뮬레이션·실물 물체 집합과 실물 category 표기 | 물체 사진을 질량·마찰·정확한 형상 모델의 명세로 취급하지 않음 |
| Fig. 3(b)–(c), p. 4 | PCA 방향 추정의 성공·실패, Point Cloud 정책 실패 예 | 이 그림만으로 모든 estimator 또는 vision 정책의 일반적 열세를 주장하지 않음 |
| Fig. 4, p. 5 | w/o tactile, RGB(Aug), Oracle angle, Point Cloud, DAgger의 학습 곡선 | 모든 tactile variant의 개별 곡선을 제시한 것은 아님 |
| Fig. 5, p. 6 | 각 손끝의 실제·시뮬레이션 RGB, Diff, Binary contact pattern | Binary mask의 정답 대비 IoU나 힘 추정 정확도를 평가한 그림이 아님 |

Fig. 4 caption은 tactile 정책들의 곡선 경향이 유사하여 **RGB(Aug)만 대표로 표시**한다고 설명한다. Fig. 5에는 RGB 조명·색 차이가 크더라도 Diff·Binary에서 접촉 윤곽이 드러나는 예가 나타난다. 그러나 이 그림들만으로 정책 내부의 물리 상태 추정이나 표현의 모든 정보를 복원할 수 있다는 주장을 하지는 않는다. [원문 Fig. 4–5 captions, PDF pp. 5–6]

## 12. Limitation — 저자들이 밝힌 한계·실패 조건

원문에는 독립된 Limitation 절이 없다. 다음은 본문이 **직접 설명한 제약·실패 원인·평가 차이**다. 정리자가 찾은 구현 누락은 다음 절들과 구분한다.

| 저자 명시 내용 | 조건·이유 | 원문 위치 |
| --- | --- | --- |
| 시뮬레이션과 실제 DIGIT의 광학 차이 | 조명·색·픽셀 차이, 제조 및 젤 variation으로 RGB 전이 성능이 제한됨 | §III-B, §V-B, pp. 3, 5–6 |
| Binary threshold의 trade-off | Noise를 줄이는 대신 일부 접촉 정보를 놓칠 수 있음 | §III-B, p. 3 |
| 불안정한 grip | 접촉 패턴이 불완전해져 tactile 정책 실패 | §V-C Failure Cases, p. 6 |
| 불완전하거나 특이한 contact | 좋지 않은 tactile feedback을 제공하여 실패 | §V-C Failure Cases, p. 6 |
| 단일 category 정책의 일반화 저하 | 실물에서 다양한 물체 geometry를 다루기 어려움 | §V-C, Table II, pp. 5–6 |
| 각도 추정 비교군의 실물 열세 | 실제 noise 등이 angle estimation과 task success에 영향을 준다고 설명 | §V-A, Fig. 3(b), p. 4 |
| Point Cloud 비교군의 실패 | 훈련/실물 물체 사이 크기·형상 차이 | §V-A, Fig. 3(c), p. 4 |
| 시뮬레이션/실물 평가 구성 차이 | 500 대 30 episodes, 시뮬레이션의 더 다양한 평가 조건 | §V-A Evaluation Variation, p. 5 |

단순화한 action과 고정 gripper width도 저자들이 명시한 과업 설계다. 다만 이를 저자들이 “향후 반드시 해제할 한계”라고 선언한 것은 아니므로, 미래 확장 계획으로 바꾸어 쓰지 않는다. [원문 §IV Action Space, PDF p. 3]

## 13. Future Work — 원문에 명시된 계획

§VI에는 **시뮬레이션 환경과 training pipeline의 코드를 공개하겠다는 계획**이 있다. 이는 첨부 v1이 작성될 당시의 공개 의사이며, 현재 공개 여부를 이번에 확인한 것은 아니다. [원문 §VI Conclusion, PDF p. 6]

그 밖에 특정 새 과업·센서·제어 자유도·학습 알고리즘을 개발하겠다는 **구체적인 향후 연구 계획은 이 v1에 명시되어 있지 않다**. Threshold 적응, 더 정밀한 힘 추정, 능동 재파지 등을 정리자의 생각으로 추가하여 저자의 Future Work처럼 서술하지 않는다. 계획이 없다는 기록은 연구에 발전 여지가 없다는 판단이 아니라 확인 범위의 보고다.

## 14. 미명시 사항과 원문 내부 주의사항

### 14.1 명칭·표·수식의 확인 사항

| 항목 | 원문에서 확인되는 차이·누락 | 이 정리의 처리 |
| --- | --- | --- |
| Tactile-Depth와 Binary | §IV Baselines 7·8은 Depth를 나열하지만 §III-B와 Table I의 세 표현은 RGB·Diff·Binary | Depth라는 네 번째 방법의 메소드·결과를 만들어 넣지 않음 |
| Table I·II의 실물 성공률 ± | Multi-category Binary(Aug)는 평균 0.80이 같지만 ±0.02와 ±0.08로 다름 | 각 표 수치를 그대로 보존; 표본·집계 원인은 미확인 |
| 지지면 비교의 정책명 | §V-C는 RGB, Binary, Binary를 중복 나열하고 Table III는 w/o Tactile·Binary 두 행만 제시 | 정량 표는 Table III를 따르고 본문의 명칭 차이를 기록 |
| Distance reward 범위 | 본문은 −1~1, 표시 식은 거리 제한 없이 그 범위를 보장하지 않음 | Clip 또는 거리 제한을 임의로 추가하지 않음 |
| Action penalty 위첨자 | PDF 원문은 norm의 제곱 | 텍스트 추출의 `2`를 norm의 아래첨자로 오독하지 않음 |
| Angle deviation 정규화 | 비율과 15% 기준은 있지만 분모 수식 없음 | 15°나 특정 degree 오차로 환산하지 않음 |
| Diff의 부호·강도 처리 | Canonical에서 current를 뺀다고 설명하나 abs·clipping·정규화 생략 | 원문 연산 순서와 실제 코드 확인 범위를 구분 |
| Real-data-free의 범위 | 실제 학습 데이터가 없다고 설명하면서 canonical image·sensor별 threshold grid search를 사용 | 정책 학습·실물 fine-tuning 부재와 센서 전처리 준비를 분리 |

[원문 §III-B·IV·V, Table I–III, PDF pp. 3–6]

### 14.2 재현에 필요한데 이 v1에 없는 정보

| 범주 | 미명시 항목 |
| --- | --- |
| 센서·로봇 | 정확한 팔·그리퍼 모델, 가반하중·reach, sensor native resolution·frame rate·range·accuracy, force calibration |
| Rendering | 힘→깊이 계수와 saturation, mesh·광원·Phong 설정, shear 처리, 렌더링/physics timestep·병렬화 수 |
| 전처리 | Threshold grid, 선택 목적함수·표본, Diff clipping, normalization, augmentation 확률·크기·순서 |
| PPO | SB3 version·완전한 hyperparameter, network layer·feature 차원, total steps·training time |
| 관측·행동 | Joint state의 정확한 구성, 목표 결합 위치, history, action의 단위·범위·servo 및 IK 경로 |
| Reward | Angle 항 전체 식·가중치, target position 생성, 비접촉 처리, 거리 clipping·0 분모 처리 |
| 종료·평가 | 최대 episode 길이, drop/contact-loss 종료, 실물 중단 기준, deviation 분모, 실물 ± 산출 방식·시험 배분 |
| 물체·지지면 | Asset ID와 train/test split, category별 개수, 물체 질량·마찰·관성, solid/soft surface 물성 |

이 정보가 **코드나 다른 버전에도 없다**고 주장하는 것이 아니다. 이번에 읽은 첨부 v1의 재현 정보 범위를 나타낸다. 실험을 재실행하거나 공개 코드를 확인한 결과와 구분한다.

## 15. 원문 위치와 문서 검증 범위

### 15.1 원문을 다시 읽을 때의 위치

| 찾을 내용 | 원문 위치 |
| --- | --- |
| 문제 동기·22개 훈련/16개 실물 물체 | Abstract·§I, pp. 1–2 |
| Related Work 두 흐름 | §II, p. 2 |
| 힘→deformation depth·Phong·PyTorch3D | §III-A, p. 2 |
| RGB·Diff·Binary·threshold·right-image flip | §III-B, p. 3 |
| Task·Observation·Action·Randomization·PPO | §IV, p. 3 |
| Reward 각 항과 action norm 제곱 | §IV Reward Function, p. 3 |
| 비교군·성공 지표·각도계 | §IV Baselines/Evaluation Metric, p. 4 |
| 물체 예시·PCA/Point Cloud 실패 | Fig. 3, p. 4 |
| 표현·비교군 결과 전체 | Table I, p. 5 |
| Single/Multi category 결과 | Table II, p. 5; §V-C, p. 6 |
| 학습 곡선·평가 구성 차이 | Fig. 4, §V-A, p. 5 |
| 실제/시뮬레이션 촉각 표현 예시 | Fig. 5, p. 6 |
| 지지면 결과·tactile 실패·공개 계획 | Table III, §V-C·VI, p. 6 |
| 인용 문헌 | References [1]–[51], pp. 7–8 |

### 15.2 검증 범위

첨부 PDF 8쪽의 본문·표·그림을 렌더링과 대조했다. 특히 action penalty의 제곱 표기와 Table I–III의 값을 시각적으로 확인했다. 수식 8개(블록 5개·인라인 3개)의 로컬 MathJax 구문 검사와 렌더링을 확인했다. 표 21개의 열 구조를 검사하고 결과표의 로컬 표시를 확인했다. 새 노트와 사용자 발굴 목록·색인 사이의 새 파일 링크 및 고정 anchor도 점검했다.

이는 논문 코드 실행, 정책 재학습, 실물 실험 재현 또는 GitHub 웹페이지의 실제 최종 표시까지 검증했다는 뜻이 아니다. 분석과 업로드에 직접 관계없는 기존 논문·프로젝트 결정은 수정하지 않는다.
