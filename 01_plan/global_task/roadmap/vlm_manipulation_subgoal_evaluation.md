# VLM Manipulation Sub-goal 평가 재설계 — Occlusion 상위 판단 능력 검증

> 제자가 작성한 초기 실험안("VLM 실험")은 instance geometry(G1) · 관계(G2) · 로봇 실행가능성(G3) 정보를 language 형태로 VLM에 제공했을 때, VLM이 manipulation sub-goal을 얼마나 안정적으로 생성하는지를 ablation(L1~L7)으로 평가하려 했다. 이 문서는 그 설계가 **"VLM이 상위 판단(가리는 물체를 어떻게 처리할지)을 스스로 하는지"를 측정하지 못하는 이유**를 진단하고, 측정 가능하도록 재설계한다.

---

## 0. 배경 및 위치

`research_roadmap.md`의 계층 0(Grounding VLM + RGB-D Perception)은 VLM이 원래 약한 metric 정보(거리·각도)를 별도 perception이 계산해 보완하고, 그 결과를 VLA(계층 1)에게 넘겨 VLA가 접근·재배치·grasp을 **스스로 판단**하도록 설계되어 있다(§1.1, §2.3, §2.7). `vlm_perception_model_evaluation.md`는 그 perception 모듈 자체(계층 0)의 정확도·latency를 평가하는 문서다.

이 문서가 다루는 것은 그 사이에 있는 질문이다 — **perception이 계산한 저차원 정보를 VLM에게 텍스트로 주었을 때, VLM이 그 정보와 이미지를 통합해 "어떤 물체를 어떻게 치워야 목표를 꺼낼 수 있는가"라는 상위 판단을 실제로 해낼 수 있는가.** 이는 로드맵의 VLA 판단 능력을 오픈소스 VLM으로 검증하려는 시도이며, 계층 0 perception 벤치마크와는 독립적으로 설계되어야 한다.

---

## 1. 기존 실험안 요약

- **공통 제공 정보**: task instruction("Retrieve the target object"), 로봇/그리퍼 제약, shelf 좌표계·workspace boundary, SAM instance 번호가 표시된 RGB.
- **G1 (물체 상태)**: `instance_id`, `center_x/y_cm`, `extent_x/y_cm`, `height_cm`.
- **G2 (물체 간 관계)**: `occupied_angular_sectors`(기준 물체 중심에서 이웃이 차지하는 각도 구간), `minimum_surface_gap_cm`.
- **G3 (로봇 행동 가능성)**: `grasp_approach_reachable_sectors`, `executable_push_sectors`, `maximum_safe_distance_cm` — gripper 충돌조건까지 반영한 **결정론적 기하 계산 결과**.
- **Ablation 축**: L1(center) → L2(+extent) → L3(+height) → L4(+G2 각도) → L5(+G2 gap) → L6(+G3 실행가능 섹터) → L7(+G3 방향별 안전거리).
- **Version A/B**: target instance를 알려주지 않고 VLM이 직접 grounding(A) vs target_instance_id를 명시해 grounding 오류를 제거(B).
- **결과**: SIMPLE_DIRECT/CLUTTER_DIRECT는 대체로 높은 성공률, SIMPLE_PUSH/CLUTTER_PUSH는 한 실행에서는 거의 전 구간 0/5, 다른 실행에서는 거의 전 구간 5/5로 관측됨. L1→L7 정보량 증가에 따른 점진적 개선 곡선은 뚜렷하게 나타나지 않음.

---

## 2. 진단 — 왜 "상위 판단"을 측정하지 못하는가

### 2.1 G3가 이미 답을 계산해서 프롬프트 상단에 얹혀 있다

`executable_push_sectors`, `grasp_approach_reachable_sectors`, `maximum_safe_distance_cm`는 물체 배치·gripper 충돌조건까지 반영해 **이미 풀어놓은 기하 문제의 해**다. 이 값을 프롬프트에 포함시키고 "push/grasp 중 무엇을 할지 골라라"라고 물으면, VLM은 이미지 속 가려짐 상황을 스스로 해석해 조치를 판단하는 것이 아니라 **주어진 표에서 조건을 만족하는 행을 찾아내는 symbolic parsing**을 수행하게 된다. `research_roadmap.md` §2.7은 이 값을 "학습 불필요, grounding 모델 + 결정론적 기하 계산"으로 규정하고, 상위 판단은 VLA(계층 1)의 몫으로 명시한다 — G3를 프롬프트로 주고 VLM에게 그 상위 판단을 다시 시키는 것은 이 역할 분담과 어긋난다.

### 2.2 결과 패턴이 이를 방증한다

SIMPLE_PUSH/CLUTTER_PUSH 조건에서 L1~L7 전 구간이 한 실행에서는 0/5, 다른 실행에서는 5/5로 완전히 saturate되어 있고, 그 사이의 완만한 개선 곡선이 보이지 않는다. Ablation의 원래 목적(정보 계층별 기여도 분리)이 성립하려면 정보량에 비례해 점진적으로 변하는 신호가 있어야 하는데, 지금은 정보량보다 다른 요인(실행 회차, 프롬프트 포맷 등 통제되지 않은 변수)이 결과를 지배하고 있을 가능성이 높다.

### 2.3 image latent space와 language로 주입된 perception 정보공간의 불일치

G1/G2/G3를 텍스트로 주면 VLM이 이를 처리하는 경로는 "이미지 → ViT → latent"가 아니라 "텍스트 → 토큰 임베딩"이다. 현재 설계로는 **image를 완전히 제거하고 동일한 텍스트만 순수 LLM에 주었을 때도 같은 성능이 나올 가능성을 배제할 방법이 없다.** 이 경우 측정되는 것은 "VLM이 시각 정보를 상위 판단에 활용하는 능력"이 아니라 "언어모델이 숫자 표를 읽고 산수·논리를 수행하는 능력"이 된다. `research_roadmap.md` §2.8이 지적하는 "VLA/VLM의 텍스트 출력이 실제 이미지 이해에 grounding되어 있다는 보장은 없다"는 우려와 정확히 같은 문제다.

---

## 3. 재설계 원칙

1. **G3는 프롬프트에서 제거하고 채점 기준(ground truth)으로만 사용한다.** VLM에게 실행 가능 방향을 알려주지 말고, VLM이 이미지 + G1/G2로부터 직접 추론한 결과를 G3(결정론적 계산값)와 비교해 채점한다.
2. **G1/G2는 유지하되 역할을 분명히 한다.** 둘 다 "VLM이 원래 약한 거리·각도 인지"를 보완하는 정당한 스캐폴딩이다. 다만 `occupied_angular_sectors`(G2)는 여유 각도(corridor)의 여집합이므로 답에 근접한 편이다 — 이 정보를 주었을 때 VLM이 "빈 방향"을 스스로 계산해내는지(G3의 `corridor_direction` GT와 비교)를 별도 채점 항목으로 둔다.
3. **Vision 기여도를 반드시 분리한다.** 동일 텍스트 조건에서 image 포함(VLM) 대 image 제거(text-only LLM) 대조군을 나란히 돌려, 정보 수준별로 이미지가 실제로 부가가치를 만드는지 확인한다.
4. **선다형 선택이 아니라 구조화된 생성(open generation)을 채점한다.** "push vs sweep 중 선택"이 아니라 sub-goal을 필드 단위로 생성시키고 GT와 필드별로 비교한다.

---

## 4. 새 프롬프팅 정보 설계

| 계층 | 내용 | 프롬프트 포함 여부 | 근거 |
|---|---|---|---|
| 공통 | task instruction, 로봇/그리퍼 제약, workspace boundary, numbered RGB | 항상 포함 | 로봇·장면 불변 사실 |
| G1 | `center`, `extent`, `height` | ablation 축 | VLM이 원래 약한 metric 인지 보완 |
| G2 | `occupied_angular_sectors`, `minimum_surface_gap` | ablation 축 (corridor 유도는 별도 채점) | VLM이 원래 약한 관계·각도 인지 보완 |
| G3 | `executable_push/grasp_sectors`, `maximum_safe_distance` | **프롬프트에서 제거** → 채점용 GT로만 사용 | 이미 상위 판단의 해를 담고 있어, 주면 평가가 아니라 답안 재현이 됨 |

**출력 스키마 (선다형 → 생성형 전환):**

```json
{
  "target_instance_id": "int",
  "direct_graspable": "bool",
  "blocking_instances": ["id", "..."],
  "action_per_blocker": {"id": "push | sweep | none"},
  "push_direction_deg": {"id": "float"},
  "corridor_direction_deg": "float",
  "confidence": "float"
}
```

G3(및 G2 기반 corridor 계산)로 만든 GT와 필드별로 비교한다. 즉 G3는 정답지로 숨겨두고, VLM이 그 정답지를 얼마나 스스로 재현/근사하는지를 재는 구조로 뒤집는다.

---

## 5. 실험 매트릭스

| 축 | 조건 |
|---|---|
| 모달리티 | (a) VLM: numbered RGB + text 정보 / (b) LLM 대조군: 동일 text, 이미지 제거(blank) |
| 정보 계층 | L0(공통 정보만) → L1(+G1) → L2(+G1+G2) — **G3는 항상 제외** |
| Target 인지 | Version A(unknown/grounding) / Version B(known) — 기존 설계 유지 |

**해석 규칙:**

- L0에서 VLM(a) 성능이 낮다 → VLM은 순수 vision만으로는 가림·거리 인지가 약하다는 원 문제의식이 재확인됨.
- L1/L2로 갈수록 VLM(a)만 개선되고 LLM(b)은 정체 → 이미지와 텍스트 정보가 실제로 통합(cross-modal binding)되고 있다는 증거.
- L1/L2에서 VLM(a) ≈ LLM(b) → 이미지가 기여하는 바가 없다는 뜻. 이 경우 "VLM 평가"가 아니라 "LLM의 표 읽기 평가"였다는 결론이 되며, image encoding 경로(ViT → latent) 자체가 병목이라는 방향으로 논문 프레이밍을 재조정해야 한다.

---

## 6. 평가지표 — floor/ceiling 방지

기존의 "5회 중 성공 횟수" 방식은 관측된 것처럼 쉽게 saturate된다. 대신:

- **필드별 채점**: `blocking_instances` precision/recall, `action_per_blocker` 분류 정확도, `push_direction_deg` / `corridor_direction_deg` 각오차(G3 GT 대비).
- **occlusion_ratio · 클러터 밀도로 층화**: `vlm_perception_model_evaluation.md` §4.4가 계층 0 자체 평가에 쓰는 원칙을 동일하게 적용.
- **표본 확대**: 현재 씬 수(조건당 ~10)로는 신뢰구간이 넓어 실행 간 결과가 극단적으로 갈릴 수 있다(관측된 0/5 vs 5/5 패턴). 조건당 최소 수십~200 trial을 권장(계층 0 프로토콜과 동일 기준, `vlm_perception_model_evaluation.md` §5).
- **(선택) downstream 실행 검증**: 예측된 sub-goal을 시뮬레이터에서 실제로 실행해 성공 여부를 확인 — `vlm_perception_model_evaluation.md` §4.4의 "오프라인 지표-downstream 성공률 상관관계 검증"과 동일한 논리를 sub-goal 예측에도 적용하면, 필드 단위 정답 일치가 실제 성공률과 얼마나 상관있는지까지 보일 수 있다.

---

## 7. 로드맵과의 연결

이 문서의 결과는 두 방향으로 쓰인다.

- VLM(image+text)이 LLM(text-only) 대비 유의미하게 우수하다면 → `research_roadmap.md` §2.8의 "이중 모델(순수 VLM이 기호 판단 담당)" 경로가 오픈소스 모델로도 성립함을 뒷받침하는 근거가 된다.
- 그렇지 않다면 → 계층 0 payload 설계(§2.3)를 VLA에 그대로 넘기고, 기호 판단을 별도 LLM에 위임하는 아키텍처 선택이 오히려 정당화된다 — 즉 어느 결과가 나오든 로드맵의 계층 설계 결정에 직접 반영 가능하다.

---

## 부록. 기존 실험안 대비 변경 요약

| 항목 | 기존 | 재설계 |
|---|---|---|
| G3 처리 | 프롬프트에 포함(L6/L7) | 프롬프트에서 제거, 채점 GT로만 사용 |
| 출력 형식 | push/sweep 등 보기 중 선택 | 구조화된 sub-goal 생성(JSON) 후 필드별 채점 |
| 모달리티 대조군 | 없음 | VLM(image+text) vs LLM(text-only) 필수 추가 |
| 지표 | 5회 중 성공 횟수(이진) | 필드별 정확도/각오차 + occlusion·클러터 층화 |
| 표본 규모 | 조건당 ~10 씬 | 조건당 최소 수십~200 trial 권장 |
