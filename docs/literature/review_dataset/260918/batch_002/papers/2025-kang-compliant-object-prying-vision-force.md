# Robotic Compliant Object Prying Using Diffusion Policy Guided by Vision and Force Observations

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B030
- Authors: Jeon Ho Kang; Sagar Joshi; Ruopeng Huang; Satyandra K. Gupta
- Year: 2025
- Venue: IEEE Robotics and Automation Letters (accepted March 2025; preprint)
- DOI / arXiv: 미명시 / 2503.03998v2
- PDF version: arXiv v2, 18 March 2025; IEEE RA-L accepted preprint
- Page count: 8
- SHA-256: `c7950f1c65a6e981ec170fe08cd13783116924de765b8d0b930cf3dd204f72c6`
- PDF filename: `Kang 등 - 2025 - Robotic Compliant Object Prying Using Diffusion Policy Guided by Vision and Force Observations.pdf`
- 분석 근거: 선택 PDF 원문을 새로 읽었다. 기존 논문 상세 노트를 근거로 사용하지 않았다. PDF 8쪽 전체를 읽었다. Fig. 3의 force–vision cross-attention 구조, Fig. 4–5의 물체·prying 단계, Fig. 6–9와 Table I의 시간·힘·성공률·실패 사례를 렌더링해 확인했다. p.8은 참고문헌이다.

## 2. Relevance to This Review

**Relevant**. KUKA의 end-effector-frame 3축 force, wrist RGB, EEF state를 diffusion policy에 결합하고 vision-only·naive force concatenation·projected force·cross-attention fusion을 각각 120회 비교한다. 현재 vision을 계속 사용하고 tactile은 없지만, 저차원 force가 고차원 vision에 묻히는 문제와 contact mode 전환에서 force가 제공하는 정보를 직접 검증하므로 F/T 역할·표현·sensor-fusion 질문에 직접 유용하다.

## 3. Task

Spring-loaded 또는 tightly fitted casing에서 battery를 빼기 위해 prying tool을 gap에 접근·정렬·삽입하고, 충분한 contact force로 tilt/pry한 뒤 battery를 lift·retract한다. Diffusion inference는 외부 ArUco/object detection이 end effector를 battery 한쪽 끝 근처로 옮긴 뒤 시작한다. (§I/§V-A/§VI-A, PDF pp.1/5–6)

## 4. Method

### 4.1. Overall Pipeline

동기화한 wrist RGB, end-effector-frame 3축 force, 6-DoF EEF state의 최근 2 observations를 사용한다. RGB는 ResNet-18 spatial features, force는 magnitude+direction 4D로 바꿔 512D projection한다. Force query와 image key/value의 4-head cross-attention joint embedding을 EEF state와 concat하고 FiLM-conditioned U-Net diffusion model이 relative-pose action sequence를 예측한다. 16 actions 중 6개를 실행하고 재계획한다. (§III–V, PDF pp.2–5; Fig. 3)

### 4.2. Observation

Observation $O_t=\{\Gamma(I,F),S\}$이다. $I$는 current RGB, $F$는 EEF-frame Cartesian force 3축, $S$는 6-DoF EEF state이며 $n=2$ history를 쓴다. Initial localization은 ArUco/object detection으로 처리하지만 numeric object pose는 policy input으로 명시되지 않는다. (§III/§V-A,C, PDF pp.2/5)

### 4.3. Action

Diffusion policy는 current pose에 대한 6-DoF delta target-pose action sequence를 낸다. Rotation은 continuous 6D representation을 사용한다고 명시하지만 translation과 결합한 최종 action-vector 차원은 미명시이다. Action horizon 16 중 execution horizon 6이다. (§III/§V-C, PDF pp.3/5)

### 4.4. Controller

KUKA IIWA 14가 extraction을 수행하고 ABB IRB120은 배터리 운반만 담당한다. Policy는 KUKA만 제어한다. Delta target pose가 실제 KUKA에 적용되는 low-level controller law·gain·rate는 미명시이며, 저자는 속도 향상 선택지로 manipulator velocity와 impedance tuning을 언급한다. (§V-A/§VI-C, PDF pp.4/6)

### 4.5. Learning / Optimization Method

419 demonstration episodes를 hand-guiding 3 Hz로 수집한 뒤 trajectory를 replay하여 사람 없는 RGB·force·state·action을 기록한다. DDPM noise-prediction MSE로 2000 epochs 학습하며 ResNet-18도 end-to-end training한다. Force는 training 중 [0.9,1.2] random scaling과 Gaussian noise $\mathcal{N}(0,0.005)$로 augment한다. (§III–V, PDF pp.3–5)

## 5. Object Information

실행 입력과 학습·평가용 정답을 구분한다.

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 기타 | 매 step wrist RGB에 implicit; numeric object pose vector는 없음. 시작은 ArUco/object detector로 battery 끝 근처에 배치 | RGB는 최근 2 observations로 갱신 | 초기 EEF는 1.0×1.0×2.0 cm 범위에서 변동한다. 지속 영상 관측은 있지만 current position 자체를 제공하거나 추적하는 것으로 코딩하지 않는다. |
| Orientation | 기타 | Current RGB appearance에 implicit; explicit numeric orientation 없음 | RGB는 계속 갱신 | Object·initial robot orientation을 test에서 변화시킨다. 지속 영상 관측은 있지만 current orientation 자체를 제공하거나 추적하는 것으로 코딩하지 않는다. |
| Shape / Geometry | 기타 | Wrist RGB ResNet feature가 casing·battery appearance를 암묵 표현 | 계속 갱신 | Training은 AAA/D와 5 casings; test는 12 objects 및 AA/C를 포함한다. Explicit mesh·CAD·dimension·category input은 없다. |
| Physical Parameters | 미제공 | Compliance, spring force, friction을 explicit actor parameter로 주지 않음 | 3축 measured force가 interaction response를 갱신 | Force augmentation으로 unseen force level에 대한 robustness를 유도한다. |

## 6. Missing Object Information and Compensation

Explicit current object pose·shape model·compliance parameter 대신 current wrist RGB가 geometry와 alignment를, 3-axis force가 contact·traction과 mode change를, EEF state가 motion context를 제공한다. 최근 2 observations가 짧은 temporal context를 주고 force augmentation이 training 범위 밖 force level을 흉내 낸다. 다만 지속 RGB에 의존하므로 blind 실행의 직접 사례가 아니며, force만으로 contact location을 복원하지 않는다. (§III–IV/§VI-D–E, PDF pp.2–4/6–7)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않는다. 논문은 built-in force/torque sensor의 3축 Cartesian force를 contact observation으로 쓰며 distributed/skin/fingertip tactile sensor는 없다. (§III/§V-B, PDF pp.2/5)

### 7.2. Preprocessing

해당 없음.

### 7.3. Policy Representation

해당 없음.

### 7.4. Retained Information

해당 없음.

### 7.5. Removed / Unavailable Information

Tactile coverage·location·pressure 정보는 제공되지 않으며 tactile ablation도 없다.

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

KUKA IIWA 14의 built-in force/torque sensor. Policy는 그중 end-effector-frame 3-axis Cartesian force를 사용한다. 저자는 다른 multi-axis F/T sensor도 사용할 수 있다고 한다. Sensor model·range·resolution·sampling rate는 미명시이다. (§III/§V-B, PDF pp.2/5)

### 8.2. Representation

Force vector를 normalized magnitude $|F|$와 unit direction $\hat{F}$의 4 parameters로 분해한다. Linear layer로 $F_{projected}\in\mathbb{R}^{4\times d}$, $d=512$로 확장하고 4-head cross-attention의 query로 사용한다. Training 중 scale $U[0.9,1.2]$와 Gaussian noise $\mathcal{N}(0,0.005)$를 더한다. (§IV-A–B, PDF pp.3–4)

### 8.3. Role

Vision과 결합해 tool–battery contact 유지, insertion→prying→lifting mode transition, premature prying 방지를 돕는다. Force trend와 peak z component를 human demonstration과 비교한다. (§VI-D–E, PDF pp.6–7)

### 8.4. Required Assumptions

Net 3D EEF force가 task contact 상태를 충분히 반영하고, RGB가 위치·geometry ambiguity를 보완한다는 task-specific 조건이 있다. Low-dynamic, under-10 Hz setting에서 modalities를 action step마다 함께 sample하며 reported precision은 sub-half-second다. (§III/§IV-A, PDF pp.2–3)

### 8.5. Reported Limitation / Ambiguity

3D net force만으로 contact location·individual contact·torque를 구분하지 않는다. Bias removal, filtering, saturation, normalization scale, zero-force direction 처리와 runtime force limit은 미명시이다. 저자도 force observation만으로 demonstration보다 큰 force를 막을 수 없다고 밝힌다. (§IV-B/§VI-D, PDF pp.4/7)

## 9. Other Observations

Current 98×98 cropped wrist RGB를 end-to-end ResNet-18로 encoding하고 global-average pooling+spatial-softmax, GroupNorm을 사용한다. EEF state 6-DoF와 2-step observation history가 함께 들어간다. Initial coarse localization은 ArUco marker 또는 object detector가 담당한다. Previous action input은 미명시이며, action horizon은 history와 구분한다. (§III–V, PDF pp.2–5)

## 10. Tactile–Other Modality Relationship

Vision은 gap·tool·battery의 spatial appearance를, force는 contact/traction과 prying stage를, EEF state는 robot motion context를 제공한다. 단순 4D concatenation이나 linear projection만으로는 force 영향이 약해졌고, force를 query로 하는 cross-attention이 가장 높은 성공률을 보였다. 이 비교는 force 유무와 fusion architecture가 동시에 바뀌는 조건을 분리해 기록해야 하며, tactile은 사용하지 않는다. (§IV-B/§VI-A,D–E, PDF pp.4–7)

## 11. Training-only / Privileged Information

Actor·Critic·reward·termination·학습 데이터 생성을 따로 기록한다.

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | No object GT | Recent RGB, measured 3-axis force, measured EEF state | Continuous vision을 요구하며 numeric GT object pose·physical parameter는 없음. (§III/§V, PDF pp.2–5) |
| Critic | 해당 없음: imitation learning | Diffusion behavior cloning에 critic 없음 | RL critic 또는 asymmetric observation으로 해석하지 않는다. (§III/§V-C, PDF pp.3/5) |
| Reward | 해당 없음: imitation learning | DDPM noise-prediction MSE로 demonstration action을 학습 | Success criterion은 evaluation용이며 reward가 아니다. (§III/§VI-A, PDF pp.3/5) |
| Termination | 미명시 | Policy는 demonstrated multi-step sequence에 따라 lift·retract; explicit learned termination detector 미명시 | 평가 성공은 battery를 완전히 loosen/lift하여 secondary arm tilt 시 bin으로 떨어질 상태인지로 판정한다. (§VI-A, PDF p.5) |
| Curriculum | No GT curriculum | 419 real demonstrations; AAA/D 5 casings; force/image augmentation | Demonstration action과 training/test object split을 사용하며 simulator privileged state는 없다. (§V-C/§VI-A, PDF p.5) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Force fusion architecture가 성공률에 미치는 영향 | Sensor/fusion ablation; Controlled comparison | DP-B vision only / DP-LF 4D force concat / DP-PF projected force / DP-CA cross-attention | 각 model 12 objects×10=120 trials. Overall success 0.39/0.48/0.57/0.96. DP-CA는 vision-only 대비 +57 percentage points, naive force variants 대비 +48/+39 points. | §VI-A; PDF pp.5–7 ; Table I |
| Unseen battery·object 일반화 | Controlled real-world evaluation | AAA/D training; AA/C and most test objects unseen | DP-CA per-battery average AAA 0.90, AA 0.97, C 1.00, D 1.00; overall 0.96. Table에서 *는 in-distribution object다. | §VI-A; PDF p.7 ; Table I |
| Edge-case transfer | Real-world evaluation | Six unseen colors / two or three batteries in series | 각 category 20 trials에서 varying colors 90%, series configurations 95% success. | §VI-B; PDF p.6 ; Fig. 4 |
| Force가 contact mode 전환을 보완 | Failure analysis; Qualitative force trace | Cross-attention force+vision vs vision-only failure example | Force+vision은 insertion 후 prying 시점과 contact 유지 trend를 human demonstration과 유사하게 보이며, vision-only example은 contact loss와 premature/incorrect action을 보인다. Independent force-only causal test는 아니다. | §VI-D–E; PDF pp.6–7 ; Fig. 8–9 |
| Human 대비 time·peak force | Descriptive real-world comparison | 30 iterations per battery type; human kinesthetic demonstration vs robot inference | Robot은 약간 더 오래 걸리고 peak component force는 human 범위와 대체로 유사하다고 보고한다. Exact aggregate 수치는 표로 제공하지 않는다. | §VI-C–D; PDF p.6 ; Fig. 6–7 |

## 13. Author-stated Limitations

저자들은 force를 observation으로 넣는 것만으로 generated action이 demonstration보다 큰 force를 내지 않도록 보장할 수 없으며, 단순 maximum external-force controller는 diffusion trajectory를 바꾸어 success를 낮출 수 있다고 밝힌다. Test는 주로 single-layer product의 depth range에 한정되고, deeper casing은 sharper metal tool와 battery-puncture safety measure가 필요하다. Tight-tolerance AAA에서는 작은 tool-gap misalignment가 주요 실패 원인이며, demonstration trajectory replay도 initial perturbation 때문에 30회 중 0–2회 실패할 수 있다. Robot inference에는 초기 idle action과 약 1초 inference step이 있어 human guidance보다 느렸고, 저자들은 안전을 위해 속도·impedance 조정을 적용하지 않았다. (§V-B/§VI-A,C–D, PDF pp.5–7)

## 14. Author-stated Future Work

Force threshold를 task success를 해치지 않고 강제하는 방법을 연구할 계획이다. 또한 battery prying 밖의 추가 contact-rich task를 탐색하고 baseline과의 더 포괄적인 비교로 framework applicability를 검증하겠다고 한다. (§VI-D/§VII, PDF p.7)

## 15. Review-relevant Findings

- Runtime actor는 current RGB, EEF-frame 3-axis force, EEF state의 2-step history를 사용하므로 blind 정책이 아니다.
- Built-in F/T의 6축 전체가 아니라 Cartesian force 3축만 사용하고, torque·contact location은 제공하지 않는다.
- Force magnitude+direction 4D를 단순 concat한 조건도 vision-only보다 +9 points였지만 cross-attention은 +57 points로 차이가 컸다.
- Force는 contact 유지와 insertion→prying mode transition을 보완하지만 RGB와 함께 평가되어 force-only sufficiency는 증명하지 않는다.
- 비-RL imitation learning이므로 critic·reward·curriculum GT 항목은 해당하지 않으며 evaluation success와 구분된다.
- Runtime force limit, sensor 사양·filter·bias 처리, exact low-level controller는 미명시이다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Problem / observation definition | §I/§III, PDF pp.1–3 |
| Force preprocessing / cross-attention | §IV, PDF pp.3–4; Fig. 3 |
| Hardware / data / training | §V, PDF pp.4–5 |
| Success ablation / failure modes | §VI-A, PDF pp.5–7; Table I |
| Force traces / mode transition | §VI-C–E, PDF pp.6–7; Fig. 6–9 |
| Limitations / Future Work | §VI-D/§VII, PDF p.7 |
