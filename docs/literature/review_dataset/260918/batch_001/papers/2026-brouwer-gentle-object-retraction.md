# Gentle Object Retraction in Dense Clutter Using Multimodal Force Sensing and Imitation Learning

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B011`
- Authors: Dane Brouwer; Joshua Citron; Heather Nolte; Jeannette Bohg; Mark Cutkosky
- Year: 2026
- Venue: IEEE Robotics and Automation Letters 11(2), 1578–1585
- DOI / arXiv: 10.1109/LRA.2025.3643332 / 미명시
- PDF version: Publisher version. 권·호는 February 2026이다. PDF는 publication 11 December 2025 및 current version 19 December 2025를 별도로 표시한다. 선택된 배치 안에서 동일 논문의 다른 파일은 확인되지 않았다.
- Page count: 8
- SHA-256: `aea8d5dca5fa450d5ca5385d33cfde6963921726202723eee2fd916b24ff093d`
- PDF filename: `Brouwer 등 - 2026 - Gentle Object Retraction in Dense Clutter Using Multimodal Force Sensing and Imitation Learning.pdf`
- 읽은 범위: PDF pp.1–8 전체: 본문·실험·토론·결론·참고문헌. 별도 Appendix 없음. Fig.2·3·6은 렌더링으로 센서/모델 구성과 수치를 교차 확인.
- 근거 원칙: 이번 배치의 해당 PDF에서 새로 추출했다. 기존 상세 노트와 외부 보충자료는 사실 근거로 사용하지 않았다. 아래 페이지는 PDF의 1-based page다.

## 2. Relevance to This Review

**Relevant**. 조밀한 clutter 안에서 물체를 꺼내는 정책에 분포형 triaxial tactile과 joint-torque 기반 추정 wrench를 함께 제공한다. 동일한 imitation-learning 구조에서 각 force modality의 제거 실험을 수행하므로 정보의 역할과 검증 범위를 직접 비교할 수 있다. Binary tactile 연구는 아니며, 현재 RGB 영상도 계속 사용한다.

Screening 근거: Title/Abstract/§I, PDF p.1; §III-A–B, PDF pp.2–3; Fig.3.

## 3. Task

선반 뒤쪽 빨간 target를 찾고 clutter를 통과해 suction으로 획득한 뒤 home으로 retract하여 지정된 drop zone에 둔다. 임무는 임의의 force를 허용하는 회수가 아니라 local peak/contact net load의 제한을 지키는 회수다. 최대 120 s, 과도한 힘과 timeout은 실패로 구분한다. 실험 장면은 38×53×32 cm shelf의 5×7 grid, 25–28개 clutter 물체, 세 종류 target에서 구성하며 점유율은 45–55%다. Task/scene 설정은 정책의 current object state 입력과 별개다. (§IV-A–B, PDF p.4; §V-B, pp.5–6)

## 4. Method

### 4.1. Overall Pipeline

현재 RGB + triaxial tactile image + normalized 6D wrench/7D TCP pose/binary suction acquisition → 과거 관측과 함께 Diffusion Policy → 8D commanded TCP pose·suction → Flexiv controller → robot motion. RGB와 tactile는 각각 별도 pretrained ResNet-18을 사용한다. (Fig.3, §III-B, p.3)

### 4.2. Observation

Policy 입력은 128×128 RGB, 20×5×3 tactile image embedding, TCP frame의 6D estimated wrench, Cartesian position+quaternion의 TCP pose 7D, suction acquisition bit다. Explicit object position/orientation/CAD, robot raw joint vector, goal pose 수치, previous action 입력은 제시하지 않는다. 과거 observation을 함께 사용하지만 설정된 observation horizon 길이는 본문에 미명시다. Fig.3에는 현재와 직전 관측이 도식화되어 있다. Action chunk 8과 observation history 길이는 별개다. (§III-A–B, p.3)

Safety monitor는 policy observation과 분리된다. Wrench/tactile를 masked input으로 제거한 baseline에서도 두 센서의 failure threshold는 동일하게 적용한다. (§IV-B, p.4; §V-A, p.5)

### 4.3. Action

$A_i=[x_i,y_i,z_i,q_{x,i},q_{y,i},q_{z,i},q_{w,i},g_i]$로, commanded Cartesian position, quaternion orientation, binary suction이다. 10 Hz에서 8개 action chunk를 실행해 force reaction을 평가하는 기준 시간은 0.8 s다. (§III-B Eq.(1), p.3; §IV-B, p.4)

### 4.4. Controller

Flexiv ROS interface로 pose를 명령한다. 저수준 제어법·gain의 상세와 별도 learned force controller는 미명시다. Force 기반 monitor는 0.8 s 동안 평균한 net force와 최대 taxel force를 제한한다. Net/peak impulse 임계값은 각각 20.8 Ns/4.8 Ns이며 26 N/6 N에 대응한다. 이 수치는 fragile cup/box 손상 실험으로 정한 본 task의 설정이다. (§III-A, p.2; §IV-B, p.4)

### 4.5. Learning / Optimization Method

Diffusion-policy imitation learning. 100개 실제 시연, 200 epochs, 동일 architecture/hyperparameters로 네 조건을 학습한다. 모든 시연에서 모든 modality를 기록하고 각 실험에서 wrench 또는 tactile를 zero-mask한다. Evaluation에도 동일 mask를 적용한다. 비-RL이며 reward/critic 기반 최적화가 아니다. (§III-B, p.3; §V-A, p.5)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | 실행 중 eye-in-hand RGB의 학습 특징; 명시적 target/obstacle position 수치 없음 | 현재 영상 갱신 | 초기 target 배치/scene generator 설정은 정책의 Initial pose 입력이 아니다. 근거: §III-A–B, pp.2–3; §IV-A, p.4; Fig.3 |
| Orientation | 기타 | 현재 RGB 특징; 명시적 object orientation 수치 없음 | 현재 영상 갱신 | 정책의 quaternion은 로봇 TCP이며 object orientation tracking과 구분한다. 근거: §III-A–B, p.3; Fig.3; Eq.(1) |
| Shape / Geometry | 기타 | RGB 외형; 빨간 target cue; 세 종류 target와 제한된 clutter 물체의 학습 prior | RGB 갱신; 고정 object-set prior | 정책에 full mesh/CAD/dimensions를 제공하는 경로 없음. 실험 shelf/grid 치수는 환경 설정이다. 근거: §III-B, p.3; §IV-A, p.4; §VI–VII, pp.6–7 |
| Physical Parameters | 미제공 | Actor에 물체 mass/friction 등의 수치 입력 없음 | 없음 | 힘 임계값은 fragile cup/box 시험으로 정한다. 물성 추정값이나 물체별 GT가 policy에 들어간다고 쓰지 않는다. 근거: §III-B, p.3; §IV-B, p.4 |

Goal/home/drop zone 및 scene 생성 조건을 current object pose tracking으로 세지 않는다. 현재 RGB가 계속 갱신되므로 blind execution 실험으로도 분류하지 않는다.

## 6. Missing Object Information and Compensation

명시적 target/obstacle pose와 full geometry 미제공 → 현재 RGB 특징 + TCP proprioception + observation history → target와 접근 경로에 반응하는 imitation policy. 저자들은 이를 수치 pose 복원으로 주장하지 않는다.

Occlusion 중 접촉 및 개별 물체 하중 정보 부족 → triaxial tactile + joint-torque estimated wrench → 접촉 후 동작 반응, local peak와 net load 감시. 저자들은 force feedback의 유용성을 sensor ablation으로 검증한다. 다만 각각의 입력이 pose 추정 오차를 얼마만큼 줄였다는 분석은 없다. (§I–II, pp.1–2; §III, pp.2–3; §IV-B, p.4; §V–VI, pp.5–7)

Suction 성공의 시각적 불확실성 → gauge pressure 기반 acquisition bit → 물체 획득 여부 제공. 이 bit는 tactile array를 Binary로 축약한 표현이 아니다. (§III-A, p.3)

## 7. Tactile

### 7.1. Raw Sensor

EEF 양측 비파지 표면에 49-element soft triaxial tactile array를 하나씩 배치한다. 총 98 physical taxels이며 각 taxel에서 3축 force를 얻는다. 최소 검출 변화는 약 0.5 N으로 보고한다. 센서의 상세 sensing principle은 본문에서 확인되지 않는다. (§III-A, pp.2–3; Fig.2)

### 7.2. Preprocessing

각 array에 zero-force taxel 하나를 padding하여 100 pixel로 만든다. x force [−1,1] N→blue, y [−1,1] N→green, z normal [0,−5] N→red, intensity는 [0,255]다. Right array의 y 범위를 반전해 위쪽 force와 intensity 증가를 일치시킨다. Zero shear는 intensity 127에 대응한다. (§III-B, p.3)

### 7.3. Policy Representation

20×5×3 tactile image → 별도 pretrained ResNet-18 → embedding → 다른 modality와 concatenate → diffusion head. Raw vector와 image representation를 이 논문 안에서 비교하지 않는다. (§III-B, p.3; Fig.3)

### 7.4. Retained Information

변환 구조상 taxel의 공간 배열, 국소 normal force 크기, signed shear 성분이 intensity로 남는다. 저자는 local peak force 감시에 tactile의 역할을 명시한다. CNN feature가 모든 물리 정보를 정확히 보존한다는 검증은 없다. (§III-B, p.3; §IV-B, p.4)

### 7.5. Removed / Unavailable Information

Intensity 양자화는 representation 구조상 직접 확인 가능하다. Range 밖 clipping과 CNN 압축에서 소실되는 구체 정보는 미명시다. 비센서면과 arm 접촉 위치/분포는 tactile가 제공하지 못한다. Binary 또는 region-wise 축약은 실험하지 않았으므로 그 성능을 이 결과에서 결론 내리지 않는다. (§III-B, p.3; §IV-B, p.4)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

Flexiv의 built-in joint-torque sensing으로 추정한 dynamics-compensated wrench이며 TCP frame으로 표현한다. Wrist에 설치한 독립 6축 F/T sensor로 분류하지 않는다. (§III-A, p.3)

### 8.2. Representation

Policy에는 6D wrench를 제공한다. Safety monitor는 그 force 세 성분의 norm을 사용한다. Suction cup에서 moment는 작다고 설명한다. Net force와 tactile maximum force 각각에 0.8 s moving average/impulse 기준을 적용한다. (§III-A, p.3; §IV-B, p.4; Fig.3)

### 8.3. Role

Policy observation, excessive-force episode cutoff, force reaction 평가에 사용한다. Net load 감시는 tactile가 없는 arm 접촉도 포괄한다. Policy sensor ablation과 safety sensor 사용을 구분해야 한다. (§IV-B, p.4; §V, pp.5–6)

### 8.4. Required Assumptions

Robot dynamics compensation 및 TCP 좌표변환을 거친 net wrench를 사용한다. 이 논문은 known geometry나 single-contact 가정으로 contact location을 역산하는 방법을 제시하지 않는다. 따라서 F/T-only localization 성립 조건에 해당하는 결과는 없다. (§III-A, p.3)

### 8.5. Reported Limitation / Ambiguity

여러 simultaneous contact에서 net load만으로 각각의 contact magnitude를 알 수 없다는 한계를 명시한다. Wrench의 motion-noise 대비 최소 검출 변화는 약 3.3 N으로 tactile 약 0.5 N보다 크다. Tactile peak 정보가 이를 보완하지만 tactile는 arm 전체를 덮지 못한다. (§III-A, pp.2–3; §IV-B, p.4)

## 9. Other Observations

- Proprioception: joint encoder로 구한 suction TCP position+quaternion 7D. Robot pose이며 object pose가 아니다.
- Vision: 실행 중 현재 eye-in-hand RGB. Red target를 대상으로 학습하며 arbitrary-object segmentation은 future work다.
- History: previous observations를 diffusion head에 제공. 정확한 configured horizon은 미명시.
- Previous Action / recurrent hidden state: 명시적 입력은 미명시.
- State Estimator: built-in wrench estimate와 kinematic TCP pose. Object pose estimator는 제시하지 않음.
- 기타: suction line gauge pressure <−6.9 kPa이면 acquisition bit=1. Goal/home은 task에 정의되지만 별도 numerical goal observation은 없다.

근거: §III-A–B, p.3; Fig.3; §VII, p.7.

## 10. Tactile–Other Modality Relationship

| 추가 정보 | Tactile이 제공하는 정보 | Tactile에서 부족한 정보 | 추가 정보의 역할 | 근거 |
| --- | --- | --- | --- | --- |
| Joint-torque estimated wrench | 센서면의 local triaxial/peak force | Arm 전체 net load 및 비센서 접촉 | 전체 load 감시와 policy feedback | §III-A, p.3; §IV-B, p.4 |
| RGB | 이미 접촉한 표면의 local force | 비접촉 target appearance와 장면 단서 | Target/navigation visual input | §III-B, p.3; Fig.3 |
| TCP proprioception | 접촉 패턴 | Robot tool pose | 공간 동작의 상태 입력 | §III-A–B, p.3 |
| Observation history | 현재 접촉 값 | 시간적 변화 | Diffusion policy 조건화; 개별 history ablation 없음 | Fig.3, p.3 |
| Suction bit | 양측 surface force | Suction acquisition 확인 | 압력 기준 획득 상태 | §III-A, p.3 |

저자들이 명시한 net-versus-local 역할과 policy sensor ablation이 모두 존재한다. 그러나 combined condition의 성공률이 각 단독보다 통계적으로 더 높다는 근거는 없고, combined의 excess-force failures는 단독보다 많다. 따라서 모든 상황에서 상보적 결합의 우월성을 입증한 것으로 일반화하지 않는다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 | 비고 |
| --- | --- | --- | --- | --- |
| Actor | 해당 없음 | 비-RL imitation learning | 해당 없음 | 학습 demonstration은 실측 관측/명령이다. Simulator privileged object GT는 사용하지 않는다. 근거: §III-B, p.3; §IV–V, pp.4–5 |
| Critic | 해당 없음 | 비-RL imitation learning | 해당 없음 | 학습 demonstration은 실측 관측/명령이다. Simulator privileged object GT는 사용하지 않는다. 근거: §III-B, p.3; §IV–V, pp.4–5 |
| Reward | 해당 없음 | 비-RL imitation learning | 해당 없음 | 학습 demonstration은 실측 관측/명령이다. Simulator privileged object GT는 사용하지 않는다. 근거: §III-B, p.3; §IV–V, pp.4–5 |
| Termination | 해당 없음 | 비-RL imitation learning | 해당 없음 | 학습 demonstration은 실측 관측/명령이다. Simulator privileged object GT는 사용하지 않는다. 근거: §III-B, p.3; §IV–V, pp.4–5 |
| Curriculum | 해당 없음 | 비-RL imitation learning | 해당 없음 | 학습 demonstration은 실측 관측/명령이다. Simulator privileged object GT는 사용하지 않는다. 근거: §III-B, p.3; §IV–V, pp.4–5 |

비-RL 항목은 해당 없음으로 유지한다. 별도의 운영상 종료에는 measured net/peak force, suction acquisition 및 120 s 제한이 쓰인다. 이 종료를 simulator GT reward나 RL termination으로 바꾸어 기록하지 않는다.

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Force modality를 정책에 추가하면 baseline보다 성공률이 높음 | Sensor ablation; Sensor combination ablation | 동일 architecture/100 demonstrations/200 epochs; baseline·wrench·tactile·both, 각 40 trials | 성공 15/40, 24/40, 24/40, 27/40. 각 force-aware 조건과 baseline의 pairwise two-sided z-test p<0.05. | §V-A–B, PDF pp.5–6, Fig.6a |
| 결합 sensing은 단독보다 timeout이 적으나 모든 failure가 가장 적지는 않음 | Sensor combination ablation; Failure analysis | 같은 4조건; force threshold와 timeout 공통 | Timeout 10/9/9/2; excess-force 15/7/7/11. Combined timeout 비교에 유의성 표시. Combined excess-force 증가 대 단독은 유의하지 않음; success 단독 대비 유의 우위는 입증되지 않음. | §V-B–VI, PDF pp.6–7, Fig.6a |
| Force feedback가 접촉에 대한 반응과 연관됨 | Controlled comparison; Failure analysis | 과하중 시 0.8 s 안에 0.5 cm 미만 이동한 timesteps를 failure-to-react로 집계 | Baseline 412, wrench 17, tactile 72, combined 22 timesteps. Episode failure 수가 아니다. | §V-B, PDF p.6, Fig.7 |
| Local peak tactile와 net wrench는 서로 다른 safety coverage 제공 | Author explanation only | Net multi-contact load와 local peak load의 정보 범위 비교 | Net load는 개별 동시 접촉 하중을 식별하지 못하고 tactile는 arm 전체를 덮지 못한다. 별도의 contact-localization 정량 ablation은 없다. | §IV-B, PDF p.4 |
| Tactile의 raw-to-image 인코딩 선택 | No supporting evidence (within this paper) | 본 논문에서는 raw vector/다른 representation와 직접 비교하지 않음 | 선행 연구를 근거로 tactile image + ResNet을 선택했다. 이 논문의 representation ablation 결과로 재인용하지 않는다. | §III-B, PDF p.3, Fig.3 |

Combined 27/40과 baseline 15/40의 성공률 차이는 +30 percentage points 또는 baseline 대비 상대 80% 증가다. 단독 대비 combined의 성공률 우월성, representation 축약의 효과, 각 입력의 pose 복원 기여는 직접 검증되지 않았다.

## 13. Author-stated Limitations

- 물체 shape/deformability/optical variability에 대한 일반화는 체계적으로 조사하지 않았다. (§I–II, p.2; §VI, pp.6–7)
- Tactile는 국소 표면만 덮으므로 arm contact를 모두 관측하지 못한다. Threshold는 실험 물체와 손상 기준에 맞춰 정했으며 보편값이 아니다. (§IV-B, p.4)
- 결합 모델의 excess-force failure 증가가 보였으나 유의하지 않다. 더 복잡한 multimodal 입력이 제한된 시연에서 덜 효율적일 수 있다는 저자 해석은 확정된 인과 결과가 아니다. (§VI, p.7)
- Force modality에 따른 동작 차이의 causal explanation에는 추가 실험이 필요하다. (§VI, pp.6–7)

## 14. Author-stated Future Work

저자는 haptic kinesthetic teleoperation/sleeve, 더 많은 reaction DoF와 multifinger manipulation 및 새 acquisition metric, OOD object 평가, red target 제한을 넘는 pretrained segmentation, adaptive gentleness/control barriers, RL fine-tuning, reactive diffusion, tactile play-data encoder, model-based low-level force control과 visual planning의 비교를 향후 방향으로 제시한다. 이 항목들은 본 논문에서 검증한 결과가 아니다. (§VII, p.7)

## 15. Review-relevant Findings

- 실행 중 RGB와 TCP pose를 제공하며 explicit numeric object pose는 입력하지 않는다.
- 두 49-taxel triaxial array를 이미지로 인코딩한다. Binary suction bit와 Binary tactile를 혼동하면 안 된다.
- 6D wrench는 joint torque로부터 추정한다. Wrist 6축 F/T 실험이 아니다.
- 저자는 net multi-contact force ambiguity와 local tactile peak의 역할, tactile coverage 부족을 직접 설명한다.
- 동일 구조의 네 modality 조건을 비교해 baseline 대비 force input의 이점을 보인다.
- 모든 modality masking 조건에서 safety monitor는 두 force source를 사용한다.
- Combined가 단독보다 통계적으로 우수하다는 결론과 Binary tactile 축약의 효과는 이 결과로 입증되지 않는다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / object pose | §III-A–B, PDF pp.2–3; Fig.3 |
| Tactile / preprocessing | §III-A–B, PDF pp.2–3; Fig.2–3 |
| Wrench source / ambiguity | §III-A, PDF p.3; §IV-B, p.4 |
| Action / controller | §III-B Eq.(1), PDF p.3; §IV-B, p.4 |
| Training / GT | §III-B, PDF p.3; §IV–V, pp.4–5; 비-RL |
| Ablation / numerical results | §V–VI, PDF pp.5–7; Fig.6–7 |
| Limitations | §I–II, PDF p.2; §IV-B, p.4; §VI, pp.6–7 |
| Future work | §VII, PDF p.7 |
