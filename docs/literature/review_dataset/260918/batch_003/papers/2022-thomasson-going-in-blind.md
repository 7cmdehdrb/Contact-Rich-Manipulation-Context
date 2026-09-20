# Going In Blind: Object Motion Classification using Distributed Tactile Sensing for Safe Reaching in Clutter

[Batch 안내](../README.md) · [Manifest](../manifest.csv) · [비교표](../tables/paper_comparison.csv) · [횡단 종합](../synthesis/literature-synthesis.md)

분석 ID: `B079`. 제공 PDF 원문을 이번 작업에서 새로 읽었다. 원문 위치는 PDF의 1-based page이며 기존 상세 노트는 근거로 사용하지 않았다.

## 1. Paper Information

- Authors: Rachel Thomasson; Etienne Roberge; Mark R. Cutkosky; Jean-Philippe Roberge
- Year: 2022
- Venue: 2022 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 1440-1446
- DOI / arXiv: 10.1109/IROS47612.2022.9981924 / Not stated
- PDF version: IEEE publisher version
- Page count: 7
- SHA-256: `ed0bccdad5bfedfc7649c9a70ce746f10ba93f5ee7496ca5f057eeb2e4ac2588`
- PDF filename: Thomasson 등 - 2022 - Going In Blind Object Motion Classification using Distributed Tactile Sensing for Safe Reaching in.pdf
- 확인 범위: 전체 본문 PDF pp.1-7; sensor, feature/cue pipeline, assumptions, experiments, failure analysis, conclusion/future work 확인

## 2. Relevance to This Review

`Partially Relevant`

완전한 reactive manipulation policy를 구현하지는 않지만, object identity·pose·mobility를 모르는 clutter reaching에서 distributed tactile history로 immovable/sliding/tipping 접촉을 구분한다. wrist F/T는 분류 입력이 아니라 과부하 정지에만 쓰여 tactile의 spatial-temporal 정보와 global force safety의 실제 역할 분리를 보여준다.

## 3. Task

clutter를 통과해 reaching할 때 계획되지 않은 접촉이 물체를 안전하게 sliding하는지, 위험하게 tipping하는지, 또는 immovable한지를 분류한다. 목표 물체 pose로 밀어 넣는 조작이 아니라 이후 reactive control을 위한 contact safety perception이다.

## 4. Method

### 4.1. Overall Pipeline

distributed capacitive taxels → normalization/interpolation/threshold/contour → center of pressure·area·intensity → RANSAC+piecewise linear temporal cue → hand-designed thresholds → immovable/sliding/tipping class. wrist F/T의 normal force는 30 N 초과 시 데이터 수집 motion을 정지한다. [Secs. III-D-E, IV, PDF pp.4-6]

### 4.2. Observation

분류기는 tactile patch의 spatial feature와 robot motion/time에 따른 변화율·평균을 사용한다. object identity, pose, shape label, mobility는 입력하지 않는다. robot tangential/normal motion progression은 tactile 변화와 결합된다. [Secs. III-C-E, PDF pp.3-4]

### 4.3. Action

실험에서는 사전 지정된 planar Cartesian reaching path를 10 mm/s로 실행한다. 논문은 분류 후 trajectory를 바꾸는 action policy는 구현하지 않는다. [Sec. IV-A, PDF pp.4-5]

### 4.4. Controller

UR16e Cartesian path command; wrist normal force가 30 N을 넘으면 정지한다. reactive replanning/control은 future work이다. [Sec. IV-A.3, PDF p.5]

### 4.5. Learning / Optimization Method

학습 정책이 아닌 rule-based feature/cue extraction과 threshold classification이다. Ground-truth motion classes는 실험 후 수작업으로 지정하며 preliminary data로 thresholds를 정한다. [Sec. IV-A-B, PDF p.5]

## 5. Object Information

| 정보 | 조건 | 획득 방식 | 실행 중 갱신 | 비고 |
| --- | --- | --- | --- | --- |
| Position | 미제공 | object pose tracking 없음 | No | contact patch 위치는 object pose가 아니다. [Secs. III-D-E, PDF p.4] |
| Orientation | 미제공 | object orientation 입력 없음 | No | trajectory/angle을 복원하지 않는다. [Secs. III-C-E, PDF pp.3-4] |
| Shape / Geometry | 미제공 | 실행 분류기에 object identity/shape 입력 없음 | No | convex·rigid·stable support의 class-level assumption은 존재한다. [Sec. III-A,C, PDF p.3] |
| Physical Parameters | 미제공 | mass/friction/mobility 입력 없음 | No | 20 N 초과를 immovable로 정의하지만 parameter 자체를 입력하지 않는다. [Sec. III-A, PDF p.3] |

## 6. Missing Object Information and Compensation

Object identity·pose·mobility·shape parameter 미제공
→ distributed tactile contact patch의 위치·면적·강도와 그 temporal trend + robot motion
→ 물체 궤적을 복원하지 않고 immovable/sliding/tipping class로 접촉 안전성을 판정한다. [Secs. III-C-E, PDF pp.3-4]

Global force의 spatial/motion ambiguity
→ tactile patch center와 gravity-direction movement
→ tipping과 sliding을 구분한다. wrist F/T는 이 판정에 사용하지 않고 30 N safety stop만 담당한다. [Secs. IV-A-C, PDF pp.5-6]

## 7. Tactile

### 7.1. Raw Sensor

Allegro Hand 앞·뒤·측면을 덮는 flexible fringe-field mutual-capacitance skin. 실험한 back-of-hand patch는 3×3 mm taxels, 4 taxels/cm², 10 Hz이며 normal pressure에 따른 capacitance counts를 낸다. [Sec. II, PDF pp.2-3]

### 7.2. Preprocessing

normalize해 grayscale image로 만들고 bicubic interpolation, fixed threshold, image moments, disjoint contour의 convex hull을 적용한다. feature time series는 RANSAC outlier removal 뒤 두 구간 piecewise-linear least-squares로 fit한다. [Secs. III-D-E, PDF p.4]

### 7.3. Policy Representation

center of pressure (Cx,Cy), contact patch area, activated taxel intensity와 각 feature의 segment slope/mean. robot normal/tangential progression 대비 cue를 사용한다. [Secs. III-D-E, PDF p.4]

### 7.4. Retained Information

접촉 위치, 영역 크기, pressure-related intensity, gravity/tangential 방향 patch motion과 시간 추세를 남긴다. [Secs. III-D-E, PDF p.4]

### 7.5. Removed / Unavailable Information

feature aggregation 후 raw taxel pattern의 세부 texture는 직접 사용하지 않으며 sensor는 shear를 측정하지 않는다. object identity와 정확한 trajectory/pose는 복원하지 않는다. [Secs. III-D-E and V, PDF pp.4,7]

## 8. Force / F/T / Wrench

### 8.1. Sensor Source

UR16e wrist의 integrated F/T sensor. tactile skin과 구분된다. [Sec. IV-A.3, PDF p.5]

### 8.2. Representation

sensor surface normal 방향 force의 scalar threshold 30 N. 분류 feature에는 포함되지 않는다. [Sec. IV-A.3, PDF p.5]

### 8.3. Role

과도한 하중에서 robot motion을 정지시키는 safety/data-collection termination. object-motion classification이나 contact localization에는 사용하지 않는다. [Sec. IV-A.3, PDF p.5]

### 8.4. Required Assumptions

normal-force 방향이 sensor frame과 정렬되고 calibrated wrist F/T가 전체 interaction load를 반영한다는 통상적 실험 설정 외 구체 가정은 원문에서 미명시이다. [Sec. IV-A.3, PDF p.5]

### 8.5. Reported Limitation / Ambiguity

저자는 force threshold보다 object motion을 안전성 지표로 쓰는 이유를 설명한다. 동일 force라도 sliding 또는 tipping일 수 있어 wrist net force만으로 motion class를 구분하지 않는다. [Introduction and Related Work, PDF pp.1-2]

## 9. Other Observations

- Proprioception: commanded robot normal/tangential motion 또는 motion progression을 tactile feature 변화와 비교한다.
- Vision: 사용하지 않는다.
- History: feature의 slope/mean을 두 구간 시간/robot-motion window로 fit하므로 temporal history를 명시적으로 사용한다.
- Previous action: 별도 vector는 없지만 commanded trajectory progression이 cue 계산에 들어간다.
- State estimator: 정확한 pose estimator 대신 discrete object-motion classifier이다.

## 10. Tactile–Other Modality Relationship

Tactile은 접촉의 공간 위치와 시간에 따른 patch movement를 제공해 sliding/tipping/immovable를 분류한다. Proprioception은 patch movement가 robot tangential motion 때문인지 object motion 때문인지 해석하는 기준이다. Wrist F/T는 30 N overload stop만 담당하며, tactile이 F/T에 없는 local patch motion을 추가한다. 이 역할 분담은 같은 classifier에서 sensor-combination ablation으로 검증된 것은 아니며 설계와 실험 절차에서 직접 확인된다.

## 11. Training-only / Privileged Information

| 구분 | GT 사용 여부 | 정보 | 실행 시 필요 여부 / 비고 |
| --- | --- | --- | --- |
| Actor | Not applicable | 비-RL | 비-RL rule-based classifier. 수작업 class labels는 평가/threshold 선정에 사용되며 실행 센서 입력과 구분한다. [전체 PDF pp.1-7] |
| Critic | Not applicable | 비-RL | 비-RL rule-based classifier. 수작업 class labels는 평가/threshold 선정에 사용되며 실행 센서 입력과 구분한다. [전체 PDF pp.1-7] |
| Reward | Not applicable | 비-RL | 비-RL rule-based classifier. 수작업 class labels는 평가/threshold 선정에 사용되며 실행 센서 입력과 구분한다. [전체 PDF pp.1-7] |
| Termination | Not applicable | 비-RL | 비-RL rule-based classifier. 수작업 class labels는 평가/threshold 선정에 사용되며 실행 센서 입력과 구분한다. [전체 PDF pp.1-7] |
| Curriculum | Not applicable | 비-RL | 비-RL rule-based classifier. 수작업 class labels는 평가/threshold 선정에 사용되며 실행 센서 입력과 구분한다. [전체 PDF pp.1-7] |

## 12. Evidence for the Added Information

| 주장/역할 | Evidence Type | 비교 조건 | 결과 | 원문 위치 |
| --- | --- | --- | --- | --- |
| tactile spatial-temporal cues로 object-motion class를 구분한다. | Controlled comparison | immovable vs sliding vs tipping; simple vs diverse objects | prototypical objects 98%, diverse real-world objects 92% combined accuracy. | Sec. IV-C; PDF PDF p.6 ; Fig. 9 |
| convex/rigid assumptions 위반이 ambiguity를 만든다. | Failure analysis | rigid convex prototypes vs deformable/concave objects | coffee-bean bag deformation과 lemonade concavity에서 tipping을 sliding으로 오분류했다. | Sec. IV-C; PDF PDF p.6 ; Fig. 9 |
| tactile patch motion이 tipping cue이다. | Controlled comparison | analytic curved-sensor model vs measured patch movement | 서로 다른 접촉 높이에서 empirical trend가 model과 비교되며 slope 1-5 threshold를 설정했다. | Sec. IV-B; PDF PDF p.5 ; Fig. 7 |

## 13. Author-stated Limitations

모델은 quasi-static planar motion, sensorized contact, convex·rigid object와 stable support를 가정한다. corner 주위의 sensor-orthogonal tip은 검출되지 않았고, deformable/granular 또는 concave object는 patch motion 가정을 깨뜨려 오분류했다. full-hand reactive reaching은 아직 구현되지 않았다. [Secs. III-A, IV-C, PDF pp.3,6]

## 14. Author-stated Future Work

full sensor network에 classifier를 적용하고 dangerous motion에서 trajectory를 바꾸는 reactive controller를 개발한다. constrained object probing, normal+tangential cue 및 shear를 결합해 더 상세한 trajectory를 추정하는 방향을 제시한다. [Sec. V, PDF pp.6-7]

## 15. Review-relevant Findings

- object identity, current pose, mobility는 제공하지 않는다.
- tactile center/area/intensity의 temporal trends가 누락된 object motion state를 보완한다.
- wrist F/T는 30 N safety stop에만 쓰고 object-motion classifier에는 쓰지 않는다.
- tactile은 F/T net load에 없는 local contact-patch motion을 제공한다.
- 다양한 objects에서 92% 분류 정확도와 assumption-violation failure analysis를 보고한다.

## 16. Important Source Locations

| 내용 | 원문 위치 |
| --- | --- |
| Observation | Secs. III-D-E, PDF p.4 |
| Object pose | Introduction/Sec. III-C, PDF pp.1,3 |
| Tactile | Secs. II-III, PDF pp.2-4 |
| F/T | Sec. IV-A.3, PDF p.5 |
| Reward | 해당 없음 |
| Critic | 해당 없음 |
| Ablation | Sec. IV-C, PDF p.6; Fig. 9 |
| Limitation | Secs. III-A, IV-C and V, PDF pp.3,6-7 |
