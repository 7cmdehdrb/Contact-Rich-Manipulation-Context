# Pre- and Post-Contact Policy Decomposition for Planar Contact Manipulation Under Uncertainty

[배치 안내](../README.md) · [Manifest](../manifest.csv) · [횡단 비교](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: `B035`
- Authors: Michael C. Koval; Nancy S. Pollard; Siddhartha S. Srinivasa
- Year: Not stated
- Venue: Not stated
- DOI / arXiv: Not stated / Not stated
- PDF version: Author-formatted PDF; publication/version identifier Not stated
- Version note: 원문에 publication year/venue/DOI/version 표시가 없어 미명시. 파일명에도 연도 없음; undated identifier 사용.
- Page count: 9
- SHA-256: `6f712f0f2dc6166cbf3dbcee616089ebec24000f4094458708e5e69d243a5c32`
- PDF filename: `Koval 등 - Pre- and Post-Contact Policy Decomposition for Planar Contact Manipulation Under Uncertainty.pdf`
- 읽은 범위: PDF pp.1–9 전체: 방법·정리/오차 bound·실험·한계/향후 연구·참고문헌. Fig.5–6 p.7 렌더 확인. 별도 부록 없음.
- 근거: 이번 배치의 PDF 원문에서 새로 분석했다. 기존 상세 노트는 재사용하지 않았다. 아래 페이지는 PDF 1-based page다.

## 2. Relevance to This Review

**Relevant**. Binary contact만으로 불확실한 object pose를 다루는 closed-loop pushing 연구다. Initial belief, known geometry, quasi-static transition model, contact-manifold particle filter가 축약 sensing을 보완하는 구조를 명시한다. Sparse fingertip sensing에서 information-gathering policy의 필요성을 비교한다.

Screening 위치: Abstract/§I, pp.1–2; §III-A, p.3; §V-A, p.6.

## 3. Task

Planar pushing으로 rectangular box를 hand-relative grasp goal region에 넣는다. Initial pose uncertainty가 있고 tactile feedback을 이용해 빠르고 높은 확률로 grasp를 달성하는 것이 목표다. 검증은 custom 2D simulation이며 Fig.1 사진을 실물 정량 검증으로 취급하지 않는다. (§I, pp.1–2; §V, pp.6–8)

## 4. Method

### 4.1. Overall Pipeline

Initial pose belief → weighted A* move-until-touch trajectory → observed binary contact → MPF belief update + offline SARSOP post-contact policy → hand motion. (§III–V, pp.3–7)

### 4.2. Observation

Policy state is a probability distribution over hand-relative SE(2) pose. Estimator receives action and binary contact observations; true pose is hidden. Full joint configuration is not represented. (§III-A, p.3; §V-A, p.6)

### 4.3. Action

Action=(generalized hand velocity, duration); experiments use five purely translational actions of about 2 cm. (§III-A, p.3; §V-A, p.6)

### 4.4. Controller

Simulated kinematic hand in 2D polygon world; quasistatic object model. Hardware low-level controller is not supplied. MPF uses 500 conventional/50 dual particles and 10% mixing in experiments; belief discretization about 23 ms. (§V, pp.6–7)

### 4.5. Learning / Optimization Method

Non-RL POMDP planning: SARSOP postcontact policy precomputed per hand-object pair, weighted A* precontact search. Reward 0 in goal and −action duration otherwise. Dynamics/observation/reward models are constructed offline by Monte Carlo rollout. (§III-A–IV, pp.3–6)

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Initial; Tracking | Initial pose distribution; contact-action MPF posterior | Belief updated each action | Prior can come from vision in formulation; reported experiments initialize simulated Gaussian beliefs. 근거: §III-A, p.3; §V-A/C, pp.6–7 |
| Orientation | Initial; Tracking | SE(2) belief includes planar object orientation relative to hand | Belief update | Not a numerical vision pose stream or 6D tracker. 근거: §III-A, p.3; §V-A, p.6 |
| Shape / Geometry | 기타 | Known polygonal hand/object geometry; fixed hand configuration | Static model | Post-contact policy is computed once per hand-object pair. 근거: §IV-A, pp.4–5; §V-A, p.6 |
| Physical Parameters | 기타 | Quasistatic transition model with friction/pressure-radius stochastic uncertainty | Sampled model, no measured true parameter updates | Unknown physical properties treated as noise; no actor physical-parameter estimator. 근거: §III-A, p.3; §V-A, p.6 |

## 6. Missing Object Information and Compensation

True pose 미관측 → initial belief + binary contact + known geometry/contact manifold + action/dynamics history → posterior pose belief와 uncertainty-aware policy. Sensor가 줄어들면 deliberate information-gathering action이 uncertainty를 줄인다. 저자들은 sparse-sensor 비교로 이 역할을 설명한다. (§III–VI, pp.3–8)

## 7. Tactile

### 7.1. Raw Sensor

Simulation collision query for n=7 hand links. Sparse comparison activates only two fingertips. No real sensor hardware specification or real trial result. (§V-A/C, pp.6–8)

### 7.2. Preprocessing

Contact/no-contact binary observations; perfect discrimination assumed. Full hand has 20 geometrically feasible patterns among 2^7 potential patterns. (§III-A, p.3; §V-A, p.6)

### 7.3. Policy Representation

Contact pattern updates a pose belief via MPF; policy acts on discretized belief rather than raw force. (§V-A/B, pp.6–7)

### 7.4. Retained Information

Contact presence and sensor/link identity constrain pose to observable contact manifold. (§III-A, p.3; §IV-A, p.4)

### 7.5. Removed / Unavailable Information

Exact pose along a link is not determined. Force magnitude/shear/contact patch are not measured. Perfect no-contact discrimination is an assumption rather than noise-robust experimental finding. (§III-A, p.3)

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

사용하지 않음 / 해당 없음 (§III-A/V-A, pp.3,6)

### 8.2. Representation

사용하지 않음 / 해당 없음 (§III-A/V-A, pp.3,6)

### 8.3. Role

사용하지 않음 / 해당 없음 (§III-A/V-A, pp.3,6)

### 8.4. Required Assumptions

사용하지 않음 / 해당 없음 (§III-A/V-A, pp.3,6)

### 8.5. Reported Limitation / Ambiguity

사용하지 않음 / 해당 없음 (§III-A/V-A, pp.3,6)

## 9. Other Observations

Vision은 초기 belief의 가능한 출처로 제안되지만 실행 중 시각 업데이트는 없다. Robot motion은 hand-relative kinematic action으로 알려져 있으며 full joint proprioception은 model 밖이다. Belief는 과거 sensing/action 정보를 재귀적으로 압축한다. (§III-A, p.3; §V-A, p.6)

## 10. Tactile–Other Modality Relationship

Binary tactile만으로 정확한 pose를 즉시 얻는다고 주장하지 않는다. Known shape와 prior/dynamics 및 belief history가 결합되어 localization을 수행한다. Force/F/T 병용은 없다. Sparse sensing에서 information gathering의 유용성을 비교하지만 continuous-vs-binary tactile 변환 ablation은 아니다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Actor | 해당 없음 | 비-RL 방법 | 해당 없음 | §III–V, pp.2–7; model-based POMDP planning |
| Critic | 해당 없음 | 비-RL 방법 | 해당 없음 | §III–V, pp.2–7; model-based POMDP planning |
| Reward | 해당 없음 | 비-RL 방법 | 해당 없음 | §III–V, pp.2–7; model-based POMDP planning |
| Termination | 해당 없음 | 비-RL 방법 | 해당 없음 | §III–V, pp.2–7; model-based POMDP planning |
| Curriculum | 해당 없음 | 비-RL 방법 | 해당 없음 | §III–V, pp.2–7; model-based POMDP planning |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Uncertainty-aware postcontact policy | Controlled comparison | SARSOP vs QMDP; 250 rollouts, 100 timesteps, discrete beliefs; repeated continuous-belief trials | Mean value −40.27 vs −55.48; SARSOP reaches grasp more quickly/reliably. MPF posterior used in continuous case. | §V-B, PDF p.7; Fig.5 |
| Sparse sensing increases need for information gathering | Sensor ablation; Controlled comparison | Full seven-link sensors vs two fingertips, complete pre/postcontact policy | Full sensing yields similar QMDP/SARSOP success; fingertip-only condition shows SARSOP advantage. Authors explain sideways moves that gather information. Exact endpoint percentages not tabulated. | §V-C/VI, PDF pp.7–8; Fig.6 |
| Geometry/model/history complement binary touch | Author explanation only | MPF and contact-manifold formulation; no geometry/history removal ablation | Binary contact restricts belief support; model and action history propagate it. Perfect contact discrimination and known geometry are required by formulation. | §III-A–V-A, PDF pp.3–6 |

## 13. Author-stated Limitations

Postcontact policy precomputation은 local task에 적합하지만 긴 transit/먼 두 EEF의 coordination에는 부적합하다. Fixed hand geometry, SE(2), discrete actions, global obstacles와 kinematic feasibility의 누락을 명시한다. Uniform discrete transition은 완전한 Markov 보장이 없고 high resolution에서 근사적으로 일치한다고 설명한다. (§I, p.2; §IV-A, p.5; §VI-A, p.8)

## 14. Author-stated Future Work

Precontact feasibility checking 및 postcontact value를 full-configuration search heuristic로 활용, SE(3)/articulated hand 확대, sample-based manifold 또는 continuous POMDP 사용을 제안한다. Online 경험으로 initial belief samples를 보완하는 방향도 언급한다. (§IV-A2, p.5; §VI-A, p.8)

## 15. Review-relevant Findings

- Binary contact는 exact pose가 아니라 contact manifold constraint를 제공한다.
- Known polygon geometry와 initial pose prior가 필요하다.
- Runtime pose belief tracking은 센서 GT tracking과 다르다.
- Sparse fingertip sensing에서 information gathering의 효과가 커졌다.
- Real robot performance와 F/T-only 비교는 없다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / pose | §III-A, p.3; §V-A, p.6 |
| Shape / assumptions | §III-A–IV-A, pp.3–5 |
| Tactile / estimator | §V-A/B, pp.6–7 |
| Reward / planner | §III-A–IV, pp.3–6 |
| Evidence | §V–VI, pp.7–8; Fig.5–6 |
| Limitations / future | §VI-A, p.8 |
