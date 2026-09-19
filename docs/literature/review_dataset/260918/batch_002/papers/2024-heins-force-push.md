# Force Push: Robust Single-Point Pushing With Force Feedback

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

## 1. Paper Information

- Paper ID: B026
- Authors: Adam Heins; Angela P. Schoellig
- Year: 2024
- Venue: IEEE Robotics and Automation Letters 9(8), pp.6856–6863
- DOI / arXiv: 10.1109/LRA.2024.3414180 / 미명시
- PDF version: IEEE publisher version; published13June2024; August2024 issue
- Page count: 8
- SHA-256: `93c06694fda20a300d07bb12d3cee8ae06a5edfcc724ccf40ad9fa5410a1f6a7`
- PDF filename: `Heins 및 Schoellig - 2024 - Force Push Robust Single-Point Pushing With Force Feedback.pdf`
- 분석 근거: 선택 PDF 원문을 새로 읽었다. 기존 논문 상세 노트를 근거로 사용하지 않았다. 본문 pp.1–8을 읽고 Fig.12–14의 실물 trajectory/비교/force trace를 렌더 확인했다. PDF 밖 영상은 분석 근거로 사용하지 않았다.

## 2. Relevance to This Review

**Relevant**. Current object pose와 물체 모델 없이 wrist F/T planar force로 single-point pushing을 제어한다. 다만 robot localization, EEF상 알려진 contact point, approximate initial object position, convex·quasistatic 단일 물체라는 제약이 있으므로 force-only라는 표현의 범위를 정확히 분리할 수 있다.

## 3. Task

알려진 평면 경로(직선 및 circular arc)를 따라 단일 slider를 밀어 운반한다. 정확한 object pose/orientation 도달보다 장거리 이동과 합리적 path deviation이 목적이다. Static wall과 slider가 충돌할 때 force를 줄여 계속 밀도록 한다. (§I/III/VII, pp.1–2/6–7)

## 4. Method

### 4.1. Overall Pipeline

Filtered planar force + localized robot pose + desired path → force-angle/path-offset feedback과 contact recovery → obstacle avoidance/admittance → desired EEF velocity → constrained IK-QP → mobile-base velocity. Object pose estimator나 learned policy는 없다. (Fig.3; §IV–V, pp.3–4)

### 4.2. Observation

Task controller는 planar force f, 현재 contact point c의 global position(robot localization+고정 EEF점), desired path를 받는다. Walls가 있는 조건에서는 wall 위치도 알고 있다. Approximate initial slider position은 첫 접촉이 가능하게 배치하는 데 사용하며 online slider pose는 입력하지 않는다. (§III–V, pp.2–4)

### 4.3. Action

Planar desired EEF velocity. Force angle과 path tangent 차, contact point의 lateral path offset으로 pushing angle을 구한다. Contact force가 threshold보다 작으면 이전 방향에서 path-following 방향으로 제한 속도로 회전한다. (§IV-A–B, p.3)

### 4.4. Controller

고정된 UR10 arm을 Ridgeback omnidirectional base에 장착하고 tennis ball EEF로 접촉한다. Arm joints는 움직이지 않고 base만 IK-QP(ProxQP)로 제어한다. Controller100Hz, force약63Hz, base command25Hz, Vicon robot pose100Hz. 높은 force에서 admittance velocity offset을 적용한다. (§IV-C/V/VII, pp.4/6)

### 4.5. Learning / Optimization Method

Hand-designed force-angle feedback + exponential smoothing + contact recovery + admittance + velocity-QP. 학습/RL은 사용하지 않는다. Controller에 slider geometry, inertia, friction model을 넣지 않는다. (§IV–V, pp.3–4)

## 5. Object Information

실행 입력과 학습·평가용 정답을 구분한다.

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | Initial | Approximate initial slider position; 정확한 획득 방식은 미명시 | 초기 배치에만 사용; online pose 없음 | Vicon slider trajectory는 평가 기록용이며 controller 입력 아님 |
| Orientation | 미제공 | Current slider orientation input 없음 | 갱신 없음 | Goal path와 object orientation 목표는 구별 |
| Shape / Geometry | 미제공 | Explicit dimensions/mesh 없음; convex shape 및 single non-articulated body prior | 갱신 없음 | Robot/EEF와 wall geometry는 별도 알고 있음 |
| Physical Parameters | 미제공 | Mass/CoM/inertia/contact·support friction/pressure distribution unknown | 갱신 없음 | Quasistatic 가정은 있음 |

## 6. Missing Object Information and Compensation

Online slider pose 및 물체 동역학 모델 없음 → contact force direction/magnitude + globally localized EEF contact point + desired path → force 방향과 path offset을 피드백하여 stable pushing과 path tracking을 유도한다.

접촉 소실 시 object pose를 재검출하지 않음 → quasistatic이라 물체가 멈춘다는 가정 + 이전 pushing direction + 알려진 path → 다시 접촉하도록 방향을 회복한다. 이는 원문 제어 설계이며 현재 물체 full state 복원은 아니다. (§IV, pp.3–4)

## 7. Tactile

### 7.1. Raw Sensor

사용하지 않음.

### 7.2. Preprocessing

사용하지 않음.

### 7.3. Policy Representation

사용하지 않음.

### 7.4. Retained Information

사용하지 않음.

### 7.5. Removed / Unavailable Information

사용하지 않음.

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

UR10 wrist의 Robotiq FT300; tennis ball contact EEF.

### 8.2. Representation

사용하는 것은 planar force vector f∈R²의 방향·크기이다. Wrist sensor가6축 장치여도 full wrench/moment를 제어 관측으로 쓴 것은 아니다. Exponential smoothing을 simulation/hardware 모두 적용한다.

### 8.3. Role

Pushing angle regulation, force threshold contact detection/recovery, collision 중 overload 완화를 위한 admittance.

### 8.4. Required Assumptions

Pusher-slider single-point contact; convex single non-articulated slider; quasistatic motion; approximate initial slider position; global robot/contact-point localization; contact point는 EEF의 fixed point로 근사. Contact height는 tipping을 피할 만큼 낮고 robot이 원하는 velocity를 낼 공간이 있다고 가정한다. Known contact friction이나 no-slip은 요구하지 않는다.

### 8.5. Reported Limitation / Ambiguity

Force는 noisy하고 contact point의 local information만 제공한다고 저자가 명시한다. Controller는 slider의 특정점(contact point) 경로를 조절할 뿐 centroid/CoM의 정확한 경로를 보장하지 않는다. Unknown shape/pose 때문에 slider-wall collision을 완전히 피할 수 없다. Multi-contact wrench decomposition은 직접 다루지 않는다.

## 9. Other Observations

Robot localization은 Vicon이며 이것을 object pose tracking으로 혼동하지 않는다. Slider Vicon은 평가용이다. Goal은 알려진 path이다. Known wall 위치와 robot body geometry는 robot collision avoidance에 쓴다. History는 smoothing과 previous pushing angle이며 learned recurrent state/action history는 없다. (§IV–V/VII)

## 10. Tactile–Other Modality Relationship

Tactile을 사용하지 않는다. F/T가 접촉 위치를 추정한 것도 아니다. 위치는 localized robot에서 EEF fixed point로 정해지며 force는 그 지점의 방향·하중 cue를 제공한다. Related Work에서 tactile이 줄 수 있는 contact angle/normal과 본 연구의 single force vector를 구별하지만 직접 tactile 비교 실험은 없다. (§II, p.2)

## 11. Training-only / Privileged Information

Actor·Critic·reward·termination·학습 데이터 생성을 따로 기록한다.

| 구분 | GT 사용 여부 | 정보 | 비고 |
| --- | --- | --- | --- |
| Actor | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§VII, p.6) |
| Critic | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§VII, p.6) |
| Reward | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§VII, p.6) |
| Termination | 해당 없음: 비-RL | 해당 없음 | RL 역할은 해당 없음. 학습/추정 supervision은 본문 §4.5에서 별도 구분. (§VII, p.6) |
| Curriculum | 해당 없음: 비-RL | 해당 없음 | 학습 없음. Slider pose의 Vicon은 결과 평가용; robot Vicon은 실행 controller 입력이다. (§VII, p.6) |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| Force feedback의 필요성 | Input ablation; Controlled comparison | Force-feedback vs open-loop path tracking; slider별10 vs5 실물 trajectories | Open-loop는 모두 약2m 내 접촉 소실 실패; 제안법은6m 방 길이를 운반. | §VII; PDF pp.6–7 ; Fig.11 |
| 알 수 없는 slider 조건에 대한 robustness | Controlled comparison | Box/Cylinder별243 initial-state/friction/inertia combinations | 같은 controller parameter로 straight/curved, wall 조건에서 path로 수렴. Simulation의 범위이며 안정성 정리 증명은 아님. | §VI; PDF p.5 ; Table II ; Fig.6–9 |
| Force-based vs position-based controller | Controlled comparison | Force10traj vs motion-capture-position Dipole5traj/condition | Dipole은 position이 CoM과 맞는 조건에서 유리하나 offset Box1에서는 큰 deviation. Force가 모든 조건에서 더 우수하다는 결과는 아님. | §VII; PDF p.7 ; Fig.13 |
| Admittance의 force 감소 효과 | Controlled comparison; Failure analysis | Wall collision with vs without admittance | Without admittance force가150N을 크게 넘어 실험 중단; admittance 사용 최고 peak trial은 그보다 낮음. 이 그림은 두 개 trace 비교로 전체 통계가 아님. | §VII; PDF p.8 ; Fig.14 |

## 13. Author-stated Limitations

실물 경로는 바닥 마찰 교란 때문에6m 내 완벽히 수렴하지 않으며 controller가 추적하는 것은 slider centroid가 아닌 contact point이다. Force가 noisy하고 local information만 준다. Robot은 원하는 EEF velocity를 실현할 충분한 공간이 있어야 한다. 알려지지 않은 slider geometry/pose 때문에 wall collision 자체를 완전히 피할 수 없다. (§IV-C/VII, pp.4/7)

## 14. Author-stated Future Work

더 정교한 contact recovery, 좁은 hallway와 clutter, formal stability proof, interaction으로 성능을 개선하는 force controller, force+vision hybrid를 향후 과제로 제시한다. (§IV-B p.4; §VII–VIII pp.7–8)

## 15. Review-relevant Findings

- Current object pose는 미제공이며 approximate initial position만 사용한다.
- Contact point의 global position은 F/T 역산이 아니라 robot localization과 EEF fixed point에서 얻는다.
- 실행 F/T representation은2D force로 full6D wrench가 아니다.
- Convex/quasistatic/single-body/single-pusher-point 조건을 사용한다.
- Wall과 추가로 접촉해도 성공하는 예가 있으나 arbitrary multi-contact localization을 검증한 것은 아니다.
- Vicon object pose는 평가용이며 robot pose는 실행용이다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation / Object information | §III pp.2; §IV-A p.3; §VII p.6 |
| Tactile | §II p.2: 미사용 |
| F/T / Recovery | §IV pp.3–4; §VII p.6 |
| Reward / Critic | 해당 없음: 비학습 controller |
| Evidence | Fig.11 pp.6; Fig.13 p.7; Fig.14 p.8 |
| Limitation / Future | §IV p.4; §VII–VIII pp.7–8 |
