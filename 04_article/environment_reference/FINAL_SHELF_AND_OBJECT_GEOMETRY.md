# 최종 환경의 선반 작업 영역과 물체 형상

2026-11-01 작업트리의 **`Isaac-Inspire-Final-GoalAccuracy-v0_2_2`** 기준이다. 배치 알고리즘은 **깊이 400 mm × 폭 1,000 mm, 높이 1,050 mm의 작업면**을 사용한다. 대상 물체는 기본 원통·직육면체·기타 물체 중 선택하고, 주변 물체는 상자·캔·머그컵·병으로 구성한다. 시각 형상, 물리 충돌 형상, 배치용 Bounding Box는 서로 구별한다.

## 1. 선반의 크기와 좌표계

| 항목 | 기본 설정 | 의미 |
| --- | --- | --- |
| 작업면 X 반폭 | 0.20 m | 깊이 방향 전체 0.40 m |
| 작업면 Y 반폭 | 0.50 m | 좌우 방향 전체 1.00 m |
| 작업면 Z | 1.05 m | 선반 local 좌표계의 물체 지지면 높이 |
| 선반 기본 위치 | `(-0.7, 0, 0)` m | 병렬 환경 원점에 대한 위치 |
| 선반 기본 회전 | 항등 회전 | 기본 상태에서는 local 축과 world 축이 평행 |

따라서 선반 local 작업면은 `X ∈ [−0.20, +0.20]`, `Y ∈ [−0.50, +0.50]`, `Z = 1.05` m이다. 기본 pose에서 환경 원점을 제외한 world 범위는 `X ∈ [−0.90, −0.50]`, `Y ∈ [−0.50, +0.50]`, `Z = 1.05` m다. 병렬 환경에서는 각 환경 원점만큼 이동한다.

로봇 쪽 전면은 선반 local **+X 경계**다. 배치 모듈은 이를 다음 board 좌표로 바꿔 사용한다.

```math
x_b=y_s,\qquad y_b=0.20-x_s.
```

board의 범위는 `x_b ∈ [−0.50, +0.50]`, `y_b ∈ [0, 0.40]` m이며, `y_b=0`이 전면이다. 두 좌표 표현은 같은 작업면을 뜻한다.

**이 수치는 배치 코드가 사용하는 작업면 정의다.** 선반 전체 프레임의 외형 치수, 판 두께, 상부 판의 위치와 수직 여유 높이는 코드 상수로 정의되어 있지 않고 외부 선반 USD에 의존한다. 기본 자산은 `speedrack_shape.usd`이며 환경변수로 다른 자산을 지정할 수도 있다. 따라서 작업면 깊이·폭을 선반 전체 외곽 치수라고 기술하거나, 확인되지 않은 상부 여유 높이를 수치로 제시하지 않는다. 이번 문서는 원본 외부 USD의 실측 bounds를 확보하지 않았다.

근거: [작업면 상수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/contact_sweep_clutter_fusion.py), [선반 pose와 Scene](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/final.py), [좌표 변환](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/final_obb_geometry.py), [외부 선반 경로](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/paths.py).

## 2. 경계와 실제 배치 가능한 영역

작업면 전체에 물체 중심을 자유롭게 배치하는 방식이 아니다. 물체의 **전체 평면 외곽**이 들어가야 하므로 크기·yaw에 따라 중심의 허용 범위가 달라진다.

| 조건 | 적용 대상 | 기본값·판정 |
| --- | --- | --- |
| 선반 경계 여유 | 대상 물체 시작·목표 | 물체 local bounds와 경계 사이 20 mm |
| 별도 root 제한 | 대상 물체 시작·목표 | local X `[−0.16, +0.16]`, Y `[−0.46, +0.46]` m와 교집합 |
| 초기 위치 범위 | 대상 물체 | 선반 중심 반경 20 mm 원판의 유효 후보 |
| 경계 여유 | 주변 물체 | 회전된 OBB 전체가 경계에서 5 mm 안쪽 |
| 물체 사이 간격 | 초기 대상·주변 물체 및 주변 물체 쌍 | 평면 OBB의 분리축 검사에 20 mm 간격 적용 |
| 접근·이동 공간 | 주변 물체 배치 | 대상 swept OBB를 전면으로 확장한 RED 영역과 3 mm 여유를 침범하지 않음 |
| 지지 높이 | 활성 물체 | root Z를 `1.05 − local_bound_min_z`로 설정 |

대상 물체의 한 축에 대해 local bounds가 `[b_min, b_max]`, 선반 반폭이 h이면 root 허용 범위는 다음과 같다.

```math
p_{\min}=\max(-h+0.02-b_{\min},\ p_{\min}^{\mathrm{limit}}),
\qquad
p_{\max}=\min(h-0.02-b_{\max},\ p_{\max}^{\mathrm{limit}}).
```

예를 들어 scale=1인 **직경 80 mm 원통**은 root 기준 X `[−0.14,+0.14]`, Y `[−0.44,+0.44]` m 안에서 경계 조건을 만족한다. **60×80 mm 바닥의 직육면체**는 yaw=0에서 X `[−0.15,+0.15]`, Y `[−0.44,+0.44]` m다. 실제 시작점은 이 범위 전체가 아니라 중심 반경 20 mm 원판에서 추출한다.

주변 물체의 물리 외곽이 들어갈 경계 내부 직사각형은 local X `[−0.195,+0.195]`, Y `[−0.495,+0.495]` m다. 물체 중심 허용 범위는 여기서 회전된 반폭을 더 빼야 한다. 여기에 물체 사이 간격과 RED/Gray/White 조건이 추가되므로, 실제 사용 가능한 배치 영역은 장면마다 달라진다.

이 조건은 **초기 배치의 평면 기하 조건**이다. 경계에 가상 벽을 설치하거나 정책 실행 중 물체 위치를 이 범위로 clamp하지 않는다. 또한 위쪽 선반과의 충돌·로봇 핸드의 전체 3D 접근 궤적·IK 도달성을 배치 알고리즘이 보장하는 것은 아니다. 실제 충돌은 선반 USD와 물체 collider로 계산한다.

근거: [현재 대상·목표 bounds와 배치 adapter](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/final_obb_geometry.py), [경계·분리축·영역 검사](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/bbox_scene_layout.py). 영역 생성·실패 처리는 [장면 생성 문서](FINAL_SCENE_GENERATION_AND_RANDOMIZATION.md)에 상세히 설명한다.

## 3. 물체 형상과 기본 치수

### 3.1 코드에서 직접 생성하는 물체

아래 치수는 추가 scale 적용 전이며, X×Y×Z는 물체 local 외곽 크기다.

| 형상 | 기본 치수 | 충돌 표현 | 역할 |
| --- | --- | --- | --- |
| 기본 원통 | 반지름 40 mm, 직경 80 mm, 높이 100 mm | Isaac Lab 표준 cylinder collider | 대상 전용 후보 |
| 직육면체 | **60×80×100 mm** | 직육면체 convex hull 1개 | 대상 전용 후보 |
| 머그컵 | 손잡이 포함 외곽 **101×70×100 mm** | 바닥 1 + 벽 16 + 손잡이 3 = **20개 convex piece** | 대상 또는 주변 물체 |
| 병 | 최대 직경 60 mm, 높이 **135 mm** | 몸통·어깨·목·뚜껑의 **4개 convex piece** | 대상 또는 주변 물체 |

직육면체는 코드에서 `kind='cube'`라고 부르지만, 현재 GoalAccuracy 계열은 치수를 60×80×100 mm로 덮어쓰므로 정육면체가 아니다.

머그컵의 몸통 외반지름은 35 mm, 내반지름은 29 mm이며 바닥 두께는 6 mm다. 벽은 16개의 볼록 조각으로 만들어 내부 공간을 남기고, 손잡이는 3개의 직육면체로 구성한다. 전체 local bounds는 X `[−47,+54]`, Y `[−35,+35]`, Z `[0,100]` mm다. **root와 Bounding Box 중심이 정확히 일치하지 않으므로** 배치 시 중심 offset을 보정한다.

병은 반지름 30 mm·높이 75 mm의 몸통, 25 mm 높이의 어깨, 반지름 12 mm·높이 25 mm의 목, 반지름 14 mm·높이 10 mm의 뚜껑으로 구성한다. 어깨는 아래 반지름 30 mm에서 위 반지름 12 mm로 줄어든다. 원형 단면 조각은 기본 32각형 mesh로 만들고 각 조각에 convex hull을 적용한다.

기본 원통은 body 원점을 바닥 중심으로 두고, 초기 질량 분포를 아래쪽에 더 집중시킨다. 질량 80%를 아래쪽 높이 20%에, 나머지 20%를 위쪽에 배치한 모델로 COM·관성을 계산한다. 따라서 이 원통도 단순히 균일 밀도 원통이라고 설명하면 정확하지 않다. reset 물성 무작위화는 별도 단계다.

근거: [원통 형상·COM·관성](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/mass_cylinder.py), [머그컵·병·직육면체 생성](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/final_spawners.py), [최종 직육면체 치수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/final.py).

### 3.2 외부 YCB 시각 자산을 사용하는 물체

| 자산 | 형상 종류 | 크기 variant | 물리 충돌 형상 |
| --- | --- | --- | --- |
| `003_cracker_box` | 크래커 상자 | 0.8, 0.9, 1.0 | 평평한 바닥의 직육면체 proxy |
| `004_sugar_box` | 설탕 상자 | 0.8, 0.9, 1.0 | 평평한 바닥의 직육면체 proxy |
| `005_tomato_soup_can` | 수프 캔 | 0.8, 0.9, 1.0 | 32각형 타원기둥 proxy |
| `002_master_chef_can` | 캔 | 0.8, 0.9, 1.0 | 32각형 타원기둥 proxy |

4개 자산에 3개 크기 variant를 적용하므로 **12개 후보**다. 여기에 머그컵과 병을 더한 **14개 기타 후보**, 그리고 기본 원통·직육면체까지 포함하면 **16개 variant 후보**가 된다. 서로 다른 의미상의 형상 종류는 8종이다.

YCB 자산은 먼저 X축으로 −90° 회전해 세운 후 시각 bounds를 측정한다. 이때 원본 크기를 `(d_x,d_y,d_z)`, 크기 variant를 f라 하면 다음 단일 scale로 모든 축을 함께 조정한다.

```math
s_{\mathrm{fit}}=1.5f\min\left(
\frac{0.04}{\sqrt{d_x^2+d_y^2}/2},\frac{0.12}{d_z}\right),
\qquad f\in\{0.8,0.9,1.0\}.
```

최종 기본 치수는 `s_fit × (d_x,d_y,d_z)`다. 가로세로 비율은 유지하며, 추가 random scale 전의 XY 외접반경은 최대 `60f` mm, 높이는 최대 `180f` mm다. 두 상한을 항상 동시에 채우는 것은 아니다. 자산별 정확한 수치 치수는 실제 참조 USD의 bounds에 의해 결정되므로, 제품 실물 치수나 다른 YCB 배포본의 치수를 대신 사용하지 않는다.

시각용 스캔 자산의 기존 collider는 끄고, 계산된 치수에 맞춘 **별도의 평평한 바닥 collision mesh**를 만든다. 상자는 직육면체, 캔은 X·Y 반폭을 각각 반지름으로 쓰는 타원기둥이며 convex hull을 적용한다. 따라서 스캔 표면의 미세한 요철이나 바닥 불균일성이 충돌 형상에 그대로 반영되지는 않는다.

근거: [자산 목록·직립 변환·시각/충돌 분리](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/contact_sweep_clutter_fusion_holding_osc_object_random_spawners.py), [크기 정규화와 평평한 collider](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/contact_sweep_clutter_fusion_holding_osc_object_random_geometry.py).

## 4. 크기 변형과 충돌·배치 형상의 차이

환경 생성 시 **각 물리 객체에 독립적인 균등 scale `U(0.9,1.1)`**을 한 번 추출한다. X·Y·Z에 같은 값을 적용하므로 비율은 보존한다. 시각 형상과 collider를 함께 확대·축소하며, 시뮬레이션 시작 전 적용한 뒤 reset에서는 유지한다.

| 물체 | ±10% 적용 후 치수 범위 |
| --- | --- |
| 원통 | 직경 72–88 mm, 높이 90–110 mm |
| 직육면체 | X 54–66, Y 72–88, Z 90–110 mm |
| 머그컵 전체 외곽 | X 90.9–111.1, Y 63–77, Z 90–110 mm |
| 병 | 최대 직경 54–66 mm, 높이 121.5–148.5 mm |
| YCB 자산 | `a × s_fit × (d_x,d_y,d_z)`, `a ∈ [0.9,1.1]` |

위 범위의 각 축은 독립 추출하지 않는다. 예를 들어 직육면체의 X가 54 mm이면 같은 scale=0.9에 의해 Y=72 mm, Z=90 mm가 된다. YCB의 경우 f=1에서 추가 scale까지 고려한 상한은 XY 외접반경 66 mm, 높이 198 mm다. 이는 모든 YCB 물체의 동일한 실제 크기를 뜻하지 않는다.

세 가지 형상의 역할은 다음과 같다.

| 형상 표현 | 쓰임 |
| --- | --- |
| 시각 geometry | 화면에 보이는 스캔·절차적 mesh |
| 물리 collider | PhysX 접촉·충돌·마찰 계산. 머그컵·병은 여러 convex piece |
| 배치용 OBB | scale 적용 local bounds를 yaw로 회전한 평면 외곽. 선반 경계·물체 사이 간격·영역 검사 |

배치용 OBB는 머그컵 내부나 손잡이 구멍 같은 빈 공간까지 외곽 직사각형으로 감싼다. 이는 접촉 계산을 직사각형으로 바꾼다는 뜻이 아니다. 배치 후 실제 물리 접촉은 각 collider에서 계산한다. Bounding Box의 최소 Z를 사용하여 물체가 작업면에 놓이도록 하므로, root가 항상 시각적 중심이나 COM인 것도 아니다.

근거: [prestartup scale과 bounds 저장](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/final.py), [현재 OBB adapter](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/final_obb_geometry.py).

## 5. 물체 종류별 역할과 선택 방식

현재 환경은 **물리 객체 12개를 생성해 유지하고, reset마다 그중에서 10개 논리 역할을 정한다.**

| 구분 | 물리 보유 구성 | 역할 |
| --- | --- | --- |
| 전용 객체 1 | 기본 원통 1개 | 원통 범주가 선택되면 대상 물체 |
| 전용 객체 2 | 60×80×100 mm 직육면체 1개 | 직육면체 범주가 선택되면 대상 물체 |
| 기타 객체 | 14개 기타 후보에서 중복 허용으로 추출한 10개 | 대상 또는 주변 물체 |

기타 객체의 형상 variant와 모든 객체의 scale은 환경 생성 시 정해진다. 동일한 형상이 여러 번 뽑힐 수 있으며 한 환경이 기타 14개 후보를 모두 보유하는 것은 아니다.

reset에서는 다음 순서로 역할을 정한다.

1. **원통 / 직육면체 / 기타** 범주 중 하나를 각각 1/3 확률로 선택한다.
2. 기타 범주이면 해당 환경이 보유한 기타 객체 10개 중 하나를 균등하게 대상 물체로 선택한다.
3. 기타 객체 중 대상 물체와 겹치지 않도록 9개를 무작위 순서로 뽑는다. 원통·직육면체가 대상이면 기타 10개 중 9개, 기타가 대상이면 남은 9개 전부다.
4. 그 9개에 Gray 4개·White 5개 역할을 부여한다. 실제 활성 개수는 커리큘럼 요청 수와 배치 성공 결과에 따라 결정한다.

**기본 원통·직육면체 전용 객체는 주변 물체로 쓰지 않는다.** 다만 주변 물체에는 원통과 비슷한 캔이나 직육면체 모양의 YCB 상자가 포함될 수 있다. 형상 이름과 역할을 혼동하지 않아야 한다.

Gray/White는 종류·재질을 뜻하지 않고 **배치 역할**이다. Gray는 RED 바깥의 근접 영역, White는 나머지 허용 영역에 배치한다. 같은 머그컵이나 캔이 에피소드에 따라 대상·Gray·White 역할을 바꿀 수 있다. 활성 수 상한은 대상 1 + Gray 4 + White 5 = **10개**다. 배치 실패 슬롯과 선택되지 않은 물체는 원격 주차하고 중력을 끄며, 역할이나 물리 인덱스를 유지한다.

기타 대상의 종류 분포는 그 환경의 초기 보유 목록에 조건부로 결정된다. 예를 들어 같은 캔 variant를 여러 개 보유했다면 해당 variant가 더 자주 선택될 수 있다. 매 reset마다 전체 14개 후보에서 새 형상을 만드는 분포와는 다르다.

근거: [12개 보유 객체 구성](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/final.py), [prototype 선택·복제](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/final_compact_spawners.py), [역할 선택·중복 방지·주차](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/final_compact_pool.py). 상세 일정과 물성 무작위화는 [장면 생성 문서](FINAL_SCENE_GENERATION_AND_RANDOMIZATION.md)를 따른다.

## 6. 확인 범위

관련 기하·역할·OBB adapter·convex piece 테스트 **28개가 통과**했다. 절차적 mesh의 꼭짓점을 직접 집계하여 직육면체 60×80×100 mm·1조각, 머그컵 101×70×100 mm·20조각, 병 60×60×135 mm·4조각도 확인했다.

외부 선반 USD의 전체 외곽·상부 여유 높이와 YCB 원본별 실제 bounds 수치는 이번 작업에서 측정하지 않았다. 새 Isaac Sim rollout·학습도 실행하지 않았다. 근거·검증·문서 이동 기록은 [개발 로그](../../02_implementation/logs/2026-11-01_final_geometry_and_article_relocation.md)에 남긴다.
