# 초기 부분 관측 OBB 시각화 개발 명세서

상태: 사용자 확정 요구사항을 명세화했다. 검증 접점도 사용자 확인을 받았다. 이번 작업은 명세서 작성이며 개발 착수가 아니다.

기준: 2026-11-16 설계 확정, 이후 새 패키지 지시 및 검증 접점 확인. [설계 인터뷰](2026-11-16_observed_obb_visualization_design.md)와 [도메인 용어집](../../GLOSSARY.md)을 따른다.

## Problem Statement

연구자는 초기 장면에서 물체의 위치를 점으로 표현하는 현재 방식에서 나아가, 정면 가림으로 실제 관측 가능한 부분을 OBB로 표현했을 때 어떤 결과가 나오는지 확인해야 한다. 타겟뿐 아니라 장애물도 대상이며, 같은 실제 물체가 가림으로 나뉘어 보이면 향후 Perception에서는 하나의 물체라는 보장이 없으므로 각각 독립된 관측 물체로 다뤄야 한다.

현재 필요한 것은 학습이나 제어에 연결된 관측 구현이 아니라, 이 관측 모델을 검토할 충돌 없는 시각화다. reset마다 이미지 렌더링과 이미지 기반 판단을 수행하는 비용은 피해야 한다. 기존 물체 자산과 배치 규칙을 활용하되, 새로운 기능은 기존 패키지에 추가하지 않고 별도 패키지로 개발해야 한다.

## Solution

워크스페이스의 src 아래 새 패키지에 단일 정지 장면 검토 기능을 구성한다. 현재 Simple 계열의 물체 자산과 배치 규칙을 재사용하고, 고정된 정면 관측 시점에서 물체 간 가림을 기하적으로 계산한다.

각 물체를 물체 방향을 따르는 회전 박스로 근사한다. 가림을 유발하는 물체의 높이는 무한으로 간주하고, 보이는 좌우 구간에 해당하는 전체 깊이와 실제 물체 높이를 유지한 관측 잔여 형상을 구한다. 가림으로 떨어진 가시 조각은 별개 관측 물체 후보로 취급한다.

각 조각은 노출 폭 2cm 이상과 노출 비율 20% 이상을 모두 만족해야 한다. 통과한 조각마다 XY 최소 면적 직사각형과 실제 높이를 결합한 OBB를 생성하고, 독립 관측 ID와 함께 선으로 표시한다. 타겟/장애물 역할은 관측 결과에서 판별하지 않는다.

초기 관측 스냅샷은 고정한다. 사용자는 정지 장면을 둘러보고, 원래 전체 박스의 참고 표시를 켜거나 끄며, 수동으로 새 배치를 생성하거나 현재 배치를 재관측할 수 있다. 모든 관측·참고 표시는 충돌과 물리 반응을 갖지 않는다.

## User Stories

아래 사용자 이야기는 합의된 요구사항을 검토 가능한 단위로 나눈 것이다. 가시 조각, 관측 물체, 노출 폭, 노출 비율, 초기 관측 스냅샷은 용어집의 정의를 따른다.

1. As a researcher, I want both the target and active obstacles to participate in observation generation, so that I can inspect the entire object arrangement.
2. As a researcher, I want the existing Simple object assets and placement rules to be reused, so that the inspection scene represents the current research environment.
3. As a developer, I want the feature to live in a new package under the workspace source directory, so that development respects the agreed separation from the existing package.
4. As a researcher, I want a single stationary inspection scene, so that I can examine observation geometry without object motion.
5. As a researcher, I want a fixed frontal observation direction, so that occlusion has a consistent meaning.
6. As a researcher, I want visibility to be computed from geometry without images, so that observation generation avoids image rendering and analysis at reset.
7. As a researcher, I want each object's full shape to be approximated by an oriented box, so that the initial implementation has a bounded geometric representation.
8. As a researcher, I want only target–obstacle and obstacle–obstacle occlusion to be considered, so that the first experiment remains within the agreed object-only scope.
9. As a researcher, I want the target to be able to occlude obstacles as well, so that occlusion does not depend on the object's task role.
10. As a researcher, I want occluders to be treated as infinitely tall, so that a low foreground object still hides the corresponding lateral interval of a rear object.
11. As a researcher, I want the complete depth of each visible lateral region to be retained, so that the result follows the agreed depth-known assumption.
12. As a researcher, I want each resulting box to retain its object's actual height, so that infinite occluder height does not produce an infinitely tall observation.
13. As a researcher, I want disconnected visible fragments to become separate observation objects, so that the result does not assume Perception can associate them with one physical object.
14. As a researcher, I want each fragment's exposed width to be evaluated independently, so that disconnected fragments cannot collectively pass a visibility threshold.
15. As a researcher, I want fragments narrower than 2cm to be excluded, so that extremely narrow observations are suppressed.
16. As a researcher, I want fragments exposing less than 20% of their source object's full frontal width to be excluded, so that insufficient relative exposure is also suppressed.
17. As a researcher, I want both exposure conditions to be required and their boundary values to be included, so that inclusion is predictable at the agreed thresholds.
18. As a researcher, I want fully hidden objects to produce no observed OBB, so that hidden full-object geometry is not presented as an observation.
19. As a researcher, I want objects excluded from observation to remain physical occluders, so that filtering does not reveal objects behind them.
20. As a researcher, I want each accepted fragment to receive a newly fitted upright OBB, so that the box represents the clipped shape rather than inheriting the original object's orientation unconditionally.
21. As a researcher, I want independent observation IDs without target or obstacle role assignment, so that the displayed observations do not imply unimplemented semantic recognition.
22. As a researcher, I want source-object correspondence to remain calculation or optional debug information, so that it is not used to merge independent observation objects.
23. As a researcher, I want accepted observed OBBs to be displayed as lines, so that I can inspect their position, extent, and orientation.
24. As a researcher, I want to toggle the original full-box reference display, so that I can compare the observed and unoccluded extents when needed.
25. As a researcher, I want all observation and reference graphics to have no collision or physical response, so that inspection does not change the scene.
26. As a researcher, I want the initial observation snapshot to remain fixed while I move the viewer, so that reviewing the result does not change what was observed.
27. As a researcher, I want manual new placement to refresh both the layout and its observations, so that I can inspect another arrangement.
28. As a researcher, I want manual reobservation to preserve the current placement, so that I can inspect repeatability on the same scene.
29. As a researcher, I want no coordinate noise or random visibility flips, so that identical placements produce identical observation geometry.
30. As a researcher, I want the viewer to work without a policy, checkpoint, training run, or control connection, so that this experiment stays focused on observation visualization.
31. As a developer, I want visibility filtering and OBB construction to reuse the same geometric results, so that redundant scene analysis is avoided.
32. As a developer, I want the complete observation output to be tested through one interface, so that correctness is checked without binding tests to internal algorithm steps.

## Implementation Decisions

### 1. 새 패키지의 책임과 기존 구현 재사용

- 구현은 워크스페이스의 src 아래 새 패키지에서 수행한다. 기존 활성 패키지에 새 환경·관측 term·학습 설정을 추가하는 작업으로 바꾸지 않는다.
- 새 패키지는 장면 준비, 관측 스냅샷 생성, 정지 장면 시각화의 책임을 갖는다. 이 책임 구분이 특정 파일 수·클래스 수·디렉토리 구조를 강제하지는 않는다.
- Simple 계열의 기존 자산과 배치 규칙을 재사용한다. 새 패키지라는 이유로 자산이나 배치 분포를 새로 설계하지 않는다.
- 기존 패키지의 학습·보상·제어·관측 구성은 보존한다. 이번 요구사항은 새 학습 환경 ID를 만들거나 기존 정책 입력을 교체하는 작업이 아니다.
- 새 패키지 이름, 구체적인 함수·클래스 이름, 내부 파일 배치, 조작 키는 이 명세서에서 고정하지 않는다.

### 2. 핵심 관측 Interface

- 새 패키지의 관측 Module은 배치된 물체의 기하 정보에서 초기 관측 스냅샷을 생성하는 하나의 Interface를 제공한다. 이 Interface가 계산 검증의 주 Seam이며 사용자 확인을 받았다.
- 입력 의미는 타겟과 활성 장애물의 계산용 회전 박스, 배치 위치·방향·실제 높이, 고정 정면 관측 시점, 노출 기준이다. 장면 준비에서 확보한 좌표와 기하를 일관된 좌표계로 전달한다.
- 출력 의미는 필터를 통과한 관측 물체들의 독립 ID와 OBB다. OBB는 중심 위치, XY 방향, 가로·세로·높이로 표현할 수 있어야 한다. 구체적인 자료형·필드명·직렬화 형식은 고정하지 않는다.
- 한 실제 물체에서 여러 관측 물체가 생길 수 있다. 기존 물체 슬롯 수와 관측 물체 수가 반드시 같다고 가정하지 않는다.
- 원본 물체 대응은 노출 비율 계산과 기하 검증에 사용할 수 있으나, 관측 ID의 병합이나 타겟/장애물 역할 부여에는 사용하지 않는다.
- 기존 가시성 함수는 물체 전체의 노출 비율과 bool을 반환하는 방식이므로, 그것만으로 이번 조각별 OBB 계약을 충족한다고 간주하지 않는다.

### 3. 가림과 관측 잔여 형상

- 실제 물체를 물체 방향을 따르는 전체 회전 박스로 근사한다. 원본 mesh를 정밀 절단하는 기능은 요구하지 않는다.
- 가림은 고정 정면의 평행 시선에 대한 물체 간 앞뒤 관계로 계산한다. 뷰어 시점은 계산 입력이 아니다.
- 가리는 물체의 높이는 무한으로 취급한다. 낮은 앞 물체 때문에 뒤 물체의 윗부분이 따로 관측되는 결과를 만들지 않는다.
- 타겟도 장애물을 가릴 수 있으며 장애물끼리도 가린다. 로봇·손·선반 구조물은 가림에 참여하지 않는다.
- 각 물체의 보이는 좌우 구간을 남기고, 해당 구간에서 원래 계산용 박스가 갖는 전체 앞뒤 깊이와 실제 높이를 유지한다. 정면 표면만 남기는 방식이 아니다.
- 가림으로 떨어진 구간은 서로 다른 가시 조각으로 유지한다. 같은 원본 물체에 속한다는 사실로 떨어진 조각을 합치지 않는다.
- 완전히 가려진 물체는 관측 물체를 생성하지 않는다.

### 4. 노출 필터

가시 조각의 노출 폭을 $w$, 원본 물체의 가림 전 정면 전체 폭을 $W$로 둔다. 폭의 단위는 미터다. 각 조각은 다음 두 조건을 모두 만족해야 한다.

```math
w \geq 0.02 \quad \mathrm{and} \quad w/W \geq 0.20
```

유효한 양의 전체 폭에 대해서는 다음과 같이 비교를 합칠 수 있다.

```math
w \geq \max(0.02,\ 0.20W)
```

- 정확히 2cm 또는 20%인 경계값을 포함한다. 서로 떨어진 조각의 폭이나 비율을 합산하지 않는다.
- 기존 35% 기준을 추가로 적용하지 않는다. 중심 좌표 노이즈와 가시성 무작위 반전도 적용하지 않는다.
- 원본 전체 폭이 2cm보다 작은 물체는 전체가 보여도 제외된다. 이는 합의한 최소 폭의 결과다.
- 관측에서 탈락한 물체도 가림에는 계속 참여한다. 필터 결과로 장면을 먼저 줄여 뒤 물체를 추가 노출시키지 않는다.
- 원본 전체 폭은 이번 시뮬레이터 근사의 계산용 정보다. 실제 Perception이 숨겨진 전체 폭을 이미 안다고 주장하지 않는다.

### 5. OBB 피팅과 계산 공유

- 필터를 통과한 가시 조각에만 OBB를 계산한다. XY 절단 형상을 감싸는 최소 면적 직사각형을 구하고, 실제 물체의 높이를 결합한다. 수직축은 유지한다.
- 잘린 형상에 맞춰 XY 방향을 다시 구한다. 원래 물체의 yaw를 결과에 강제로 유지하지 않는다.
- 같은 원본 물체에서 나온 조각이라도 각각 별개의 OBB를 계산한다.
- 가림 판정, 노출 폭·비율 판정, 형상 절단, OBB 피팅은 같은 기하 결과를 공유한다. 가시성 판정을 별도로 반복하지 않는다.
- 로컬 형상 준비와 배치 후 계산을 구분해 변하지 않는 기하를 재사용한다. 실제 mesh 생성·대량 점군 샘플링·이미지 분석을 전제로 삼지 않는다.
- 구현 권고 흐름은 정면 구간별 가림 계산, 연속된 가시 조각 분리, 노출 필터, 통과한 조각의 바닥면 절단, 최소 면적 직사각형 피팅이다. 이는 합의한 동작을 실현하는 방안이며 특정 라이브러리나 내부 알고리즘을 추가 요구사항으로 고정하지 않는다.
- 회전 박스의 앞뒤 관계를 물체 중심 거리만으로 대신하지 않는다. 기존 원형·비겹침 가시성 계산의 가정을 새 박스 기하에 그대로 적용하지 않는다.
- 동일한 배치와 설정에서는 동일한 관측 기하가 나와야 한다. 최소 면적 방향이 동률인 경우의 표현 선택과 수치 허용오차는 이 계약과 임계값 의미를 보존하는 구현 세부사항이다.

### 6. 표시와 생명주기

- 첫 검토는 하나의 정지 장면이다. 물리 시뮬레이션으로 물체를 움직이지 않는다.
- 초기 장면 배치가 완료되면 초기 관측 스냅샷을 생성하고 유지한다. 프레임마다 현재 물체 상태를 다시 관측하지 않는다.
- 기본 화면에는 통과한 관측 물체의 OBB를 선으로 표시한다. 관측 물체는 독립 ID로 구분하며 타겟/장애물 역할을 표시하지 않는다.
- 원래 전체 박스는 켜고 끌 수 있는 참고 표시다. 참고 표시를 관측 결과에 포함하지 않는다.
- 모든 관측·참고 표시는 충돌과 물리 반응이 없어야 한다.
- 수동 새 배치는 물체 배치를 다시 생성하고 관측도 갱신한다. 수동 재관측은 현재 배치를 유지한 채 관측만 다시 계산한다.
- 뷰어를 회전하거나 참고 표시를 토글해도 관측 스냅샷과 물체 배치는 바뀌지 않는다.
- 실제 원본 물체와의 대응은 선택적인 디버그 정보로만 취급한다. 스냅샷 사이 물체 추적이나 의미 식별은 도입하지 않는다.

## Testing Decisions

### 승인된 검증 Seam

계산 검증은 새 패키지의 '배치된 물체 정보 → 독립 관측 ID와 OBB 스냅샷' Interface 하나를 중심으로 수행한다. 가림 helper, 절단 helper, 피팅 helper의 호출 횟수나 내부 자료구조를 테스트 계약으로 만들지 않는다. 사용자는 이 검증 구성과 표시·토글·재관측의 별도 뷰어 확인에 동의했다.

좋은 테스트는 입력 장면에 대한 관측 물체 개수, 독립성, 필터 통과 여부, OBB의 기하와 유지되는 스냅샷을 확인한다. 예상 결과는 해석적으로 판단할 수 있는 장면이나 구현과 독립된 기하 대조로 구하며, 구현의 동일 계산식을 복사해 정답으로 삼지 않는다.

### 관측 Module의 외부 동작 검증

| 사례 | 확인할 결과 |
| --- | --- |
| 기준을 만족하는 완전 가시 물체 | 원래 박스 형상을 감싸는 하나의 관측 OBB |
| 완전 가림 | 관측 물체와 OBB 없음 |
| 한쪽 부분 가림 | 남은 구간의 전체 깊이와 실제 높이에 맞춘 OBB |
| 중앙 가림으로 양쪽 분리 | 서로 다른 관측 ID와 OBB, 원본 물체 기준 병합 없음 |
| 낮은 앞 물체와 높은 뒤 물체 | 뒤 물체의 윗부분이 별도 가시 영역이 되지 않음 |
| 타겟이 장애물 앞에 있음 | 역할에 관계없이 타겟이 장애물을 가림 |
| 회전된 박스의 부분 가림 | 절단 형상에 최소 면적 OBB 피팅, 원본 yaw 강제 없음 |
| 전체 폭 6cm, 조각 폭 1.9cm | 비율이 충분해도 최소 폭 미달로 제외 |
| 전체 폭 20cm, 조각 폭 3cm | 최소 폭을 만족해도 비율 15%로 제외 |
| 전체 폭 10cm, 조각 폭 2cm | 두 경계값을 만족하므로 포함 |
| 전체 폭 10cm, 조각 폭이 2cm 바로 아래/위 | 아래는 제외, 위는 포함 |
| 전체 폭 20cm, 조각 폭이 4cm 바로 아래/정확히 같음/위 | 비율 경계에 따라 제외/포함/포함 |
| 전체 폭 20cm, 양쪽 조각이 각각 3cm | 각 조각이 15%이므로 둘 다 제외, 합산 30% 적용 금지 |
| 전체 폭 2cm 미만, 완전 가시 | 최소 폭 미달로 제외 |
| 노출 기준에 미달한 물체가 앞에 있음 | 관측에서 제외돼도 뒤 물체에 대한 가림 효과 유지 |
| 동일 배치 재관측 | 동일한 관측 기하, 무작위 노이즈·반전 없음 |

OBB의 동등한 방향 표현이 여러 개일 수 있는 장면에서는 특정 내부 꼭짓점 순서 대신 실제로 감싸는 영역과 동작의 결정성을 검증한다. 수치 허용오차가 합의된 폭·비율 임계값을 임의로 넓히는 수단이 되어서는 안 된다.

### 검토 실행기와 뷰어 확인

- 기존 Simple 자산·배치 규칙을 사용한 단일 장면이 정책·checkpoint 없이 열리는지 확인한다.
- 물체가 움직이지 않는 정지 상태에서 최종 관측 OBB와 선택적인 전체 박스 참고 표시를 확인한다.
- 선 표시의 위치·크기·방향과 계산된 OBB가 일치하는지 확인한다.
- 관측·참고 marker에 충돌과 물리 반응이 없고, 표시 토글이 물체 배치나 관측 결과를 바꾸지 않는지 확인한다.
- 뷰어 회전이 초기 관측 스냅샷을 갱신하지 않는지 확인한다.
- 수동 새 배치와 현재 배치 재관측이 합의한 서로 다른 동작을 수행하는지 확인한다.
- 기존 패키지의 학습·제어·관측 구성에 변경이 생기지 않았는지 변경 범위를 대조한다.

### 참고할 기존 검증 방식

- 기존 scene randomization의 가시성 검사는 정면 가림의 해석적 예제, 임계값 경계, 두 가림 구간의 중복 처리, 관측 제외 물체의 가림 유지 등을 확인한다. 이번 조각별 박스 검증에 참고하되 기존 원형 형상과 35% 기준은 가져오지 않는다.
- 기존 OBB 배치 검사는 독립적인 다각형 구성·투영을 이용해 계산 결과를 대조한다. OBB 기하 테스트에서 구현과 독립된 기대값을 구하는 선례로 삼는다.
- 기존 초기 가시성 검사는 관측 스냅샷의 유지와 입력 읽기로 상태가 갱신되지 않는 동작을 확인한다. 이번 정지 스냅샷 생명주기 검증에 참고한다.

### 성능 확인과 검증 상태

startup의 고정 기하 준비, 배치 후 가림·필터·OBB 계산, 표시 갱신 비용을 구분해 측정한다. 가시성 계산을 재사용하고 작은 조각을 피팅 전에 제외하는 설계의 실제 비용을 확인한다. 합의하지 않은 시간 한도, 처리량 수치, 필수 GPU 사용을 수락 조건으로 추가하지 않는다.

계산은 향후 다중 환경 적용을 고려하되 첫 시각화의 범위는 단일 장면이다. 성능 확인을 위해 학습을 실행하지 않는다. 이 명세서 작성 시점에는 기능 구현, 기하 테스트, 뷰어 실행, 성능 측정을 수행하지 않았다.

## Out of Scope

- 강화학습 실행, checkpoint 사용, 정책·Actor/Critic 관측 연결, 보상·종료·커리큘럼 변경.
- 로봇 제어, Sweeping 동작, 접촉 안정화 학습, 물리 시뮬레이션을 통한 물체 이동.
- 기존 패키지 안에 새 환경 또는 관측 기능을 추가하는 개발.
- 실제 RGB/depth 이미지 생성·분석, 카메라 센서 기반 가시성 판단, 실제 Perception 모델 실행.
- 원본 mesh 기반 정밀 가림, 가려진 좌우 영역의 형상 복원, 실제 물체 전체를 다시 관측한 것처럼 처리하는 보정.
- 로봇·손·선반 구조물의 가림, 높이 차이에 따라 윗부분을 드러내는 가림 모델.
- 분리된 가시 조각의 동일 물체 연결, 타겟/장애물 의미 판별, 스냅샷 간 추적.
- 수직축까지 기울이는 일반 3D OBB 탐색, 좌표 노이즈, 무작위 가시성 반전.
- 프레임마다 갱신하는 온라인 시각 관측, 새로운 자산·배치 분포, 새로운 학습 환경.
- 합의하지 않은 UI 기능, 데이터 저장·내보내기 기능, 고정 패키지명·함수명·조작 키, 수치 성능 보장.

## Further Notes

- 사용자는 설계를 확정한 뒤 개발 명세서 작성을 요청했고, 구현 위치를 src 아래 새 패키지로 지정했다. 이 명세서는 그 지시를 반영하며 새 코드나 패키지를 생성했다는 뜻이 아니다.
- OBB는 회전 박스 근사에서 잘린 관측 잔여 형상을 감싸는 표현이다. 실제 물체 mesh의 부분 관측 OBB를 정확하게 재현했다고 주장하지 않는다.
- 노출 비율 계산에 필요한 원본 전체 폭은 시뮬레이터에서 얻는다. 향후 실제 Perception의 동일 정보 취득 문제를 이번 단계에서 해결한 것으로 보지 않는다.
- 독립 관측 ID의 구체적인 번호·표시 순서는 기능 요구사항이 아니다. 떨어진 조각을 합치지 않고 독립 관측 물체로 유지한다는 의미를 보존한다.
- 특정 내부 알고리즘, 패키지 이름, 함수 이름, 조작 키 등 합의하지 않은 구현 선택은 이 문서에서 추가로 확정하지 않는다. 선택 시에는 합의된 외부 동작과 기존 패키지 보존을 지킨다.
- 문서는 로컬 문서 저장소에서 관리한다. 프로젝트의 이슈 게시 대상이 지정된 설정은 확인되지 않았다. `to-spec`의 게시 단계는 대상 설정 후 `ready-for-agent` 라벨을 적용하는 것으로 남기며, 현재 게시 완료로 기록하지 않는다.
