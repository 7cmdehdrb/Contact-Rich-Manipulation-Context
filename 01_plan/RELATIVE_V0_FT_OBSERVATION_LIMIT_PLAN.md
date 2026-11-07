# Relative-v0 기반 F/T 관측·Action Rate 한도 수정 계획

2026-11-07. 최초에는 문서 작성만 요청받았고, 후속으로 사용자가 Relative-v0와 상속 환경의 구현 및 필요시 GPU 스모크를 명시적으로 요청했다. **1·2번을 구현했다.** 적용 내용과 실행 검증은 [구현 기록](../02_implementation/logs/2026-11-07_relative_observation_action_limits.md)을 따른다. 아래는 확정 요구사항과 검증 기준이다.

## 사용자 요청과 적용 범위

기준 환경은 **`Inspire-Wrench-Refactor-Relative-v0`**이다. 부모인 Relative-v0에 변경을 적용하여 그 하위 환경에도 동일한 한도가 적용된다. 사용자 후속 요구에 따라 질량·관성 보정은 clipping 전에 보존하고 검증한다.

현재 활성 하위 환경은 Relative-v2와 Relative-v3다. 별도 계열인 `Inspire-Wrench-Refactor-v0`와 혼동하지 않는다. 새로운 환경 버전을 만들거나 버전별로 독립된 제한값을 복제하지 않는다.

## 1. F/T 관측 한도 설정 — 사용자 확정 요구사항

실제 센서의 관측 한도를 반영하여 힘과 모멘트를 다음 범위로 clipping한다. 아래 한도는 사용자가 지정한 값이며 별도의 제조사 사양 검증을 수행한 것은 아니다.

| 관측 성분 | 하한 | 상한 | 단위 |
| --- | ---: | ---: | --- |
| Fx, Fy, Fz 각각 | -150 | +150 | N |
| Mx, My, Mz 각각 | -8 | +8 | N·m |

- 각 축을 독립적으로 제한한다. 3축 벡터의 norm을150N 또는8N·m로 제한하는 방식이 아니다.
- 범위 안의 값과 정확히 경계에 있는 값은 유지한다. 범위를 넘으면 해당 부호의 경계값으로 포화시킨다.
- 단위는 N과 N·m를 유지한다. 150 또는8로 나누어 무차원화하는 normalization은 이번 요구에 포함하지 않는다.
- Actor와 Critic에 동일한 한도를 적용한다. v2의 별도 Critic 관측도 빠뜨리지 않는다.

예시:

```text
입력: [Fx=200, Fy=-170, Fz=50, Mx=10, My=-9, Mz=2]
출력: [Fx=150, Fy=-150, Fz=50, Mx=8, My=-8, Mz=2]
```

## 현재 코드와 구현 시 적용 방향

현재 F/T 관측 경로는 다음과 같다.

```text
Fixed Joint reaction
→ 손의 중력·관성 보정 및 모멘트 기준점 이동
→ EEF 좌표계의 6D wrench
→ 관측 노이즈
→ Actor/Critic 입력
```

`PureWristWrench`는 보정된 `pure_eef`를 제공하고, 기존 관측 노이즈의 표준편차는 힘0.05N·모멘트0.005N·m다. 직접 관측58D의 마지막6채널이 F/T다. 변경 전에는 요청한 축별 한도가 없었다.

**계획상 적용 위치는 Actor/Critic에 전달되는 최종 F/T 관측 경계**로 둔다. 보정·좌표계·단위를 유지하고 기존 관측 노이즈를 포함한 최종 결과가 범위를 넘지 않도록 한다. 이는 현재 EEF 관측의 한도를 제한하는 구현 방향이며, 센서 원본 좌표에서 먼저 saturation시킨 뒤 보정하는 물리 센서 모델과는 다르다. 사용자가 확정한 수치는 위 표이며, 이 적용 위치는 실제 구현 전에 대조할 설계 사항이다.

구현 시 다음 조건을 만족해야 한다.

1. Relative-v0의 공통 관측 구성에서 한도를 정의하고 v2/v3가 이를 상속한다.
2. 학습 중 관측 노이즈가 활성화된 경우와 평가 중 비활성화된 경우 모두 한도를 보장한다. noise 함수 안에서만 clipping하여 평가 시 제한이 사라지는 구현을 피한다.
3. 노이즈를 더한 뒤 범위 밖으로 다시 벗어나는 일이 없도록 처리 순서를 확인한다. 현재 ObservationManager는 modifier → noise → clip → scale 순으로 처리하므로 modifier만 추가하는 것으로 최종 한도를 보장할 수 없다.
4. F와 M의 서로 다른 한도를 적용한다. 6채널 전체에 동일한 ±150 또는±8을 적용하지 않는다.
5. 공유 센서 reader 또는 공통 ObservationManager를 전역 수정하지 않고 Relative 계열의 관측 경계에 한정한다.
6. 관측 채널 순서·차원·term 이름과 네트워크 입력 구조를 보존한다. NaN을0으로 대체하는 등의 별도 오류 은폐 처리는 추가하지 않는다.

최종 구현은 Relative-v0 EnvCfg의 `wrist_wrench_observation_limits`를 runtime의 `load_managers()`에서 읽어, 각 활성 그룹의 live `wrist_wrench` term에 device tensor clip을 설정한다. 기존 ObservationManager의 noise 다음 clip 단계를 사용하며 공통 manager·reader·noise 함수는 수정하지 않았다. 원래 config에는 직렬화 가능한6개 한도 값이 남고, CPU/GPU용 tensor는 manager가 복제한 runtime config에만 연결한다.

## 버전별 전파 확인

| 환경 | 관측 경로 | 구현 시 확인할 결과 |
| --- | --- | --- |
| Relative-v0 | Actor/Critic 공통 policy | 둘 다 지정 한도 적용 |
| Relative-v2 | Actor policy / 별도 critic | 두 그룹 모두 지정 한도 적용, 타겟 초기/현재 차이 유지 |
| Relative-v3 | v0의 공통 policy 상속 | 지정 한도 적용, v3 보상 차이 유지 |

`WrenchRefactorRelativeV2ObservationsCfg.CriticCfg`는 Relative 공통 PolicyCfg를 상속하므로, 공통 관측 경계에 한도를 연결하는 방식이 전파 의도와 맞는다. 향후 하위 환경이 해당 관측을 override하면 동일 계약을 별도로 확인해야 한다.

## 2. Raw 정책 Action Rate의 그룹별 최대100 복원 — 사용자 확정 요구사항

2026-11-07 후속 요청: 현재 raw 정책 action을 사용하는 방식은 유지하되, Arm과 Hand 각각의 변화량 제곱합에 최대100 조건을 다시 적용한다. OSC 출력 토크 변화량 방식으로 교체하지 않는다.

| 항목 | 현재 | 수정 계획 |
| --- | --- | --- |
| Arm 입력 | 정책 raw action6D | 유지 |
| Hand 입력 | 정책 action2D를 각각[0,1]로 제한 | 유지 |
| Arm 변화량 제곱합 | 상한 없음 | 합산 후 최대100 |
| Hand 변화량 제곱합 | 별도 명시적 상한 없음 | 합산 후 최대100 |
| 계수 | Arm0.03 / Hand0.03 | 유지 |
| reward weight / dt 적용 | -1 / RewardManager가1회 적용 | 유지 |

**100은 raw action 값의 한도나 축별 한도가 아니라, 그룹별 변화량 제곱합의 한도**다. Arm6축을 합산한 값과 Hand2축을 합산한 값에 각각 적용한다. 두 그룹을 합친 뒤100으로 제한하는 방식도 아니다.

구현한 계산의 명세는 다음과 같다. 공유 함수는 선택적 cap 인자를 받고 Relative-v0에서 두 그룹에100을 지정한다.

```python
arm_delta = action[:, :6] - previous[:, :6]
hand_delta = action[:, -2:].clamp(0., 1.) - previous[:, -2:].clamp(0., 1.)

arm_cost = arm_delta.square().sum(-1).clamp_max(100.0)
hand_cost = hand_delta.square().sum(-1).clamp_max(100.0)
cost = 0.03 * arm_cost + 0.03 * hand_cost
```

현재 Hand[0,1] 처리를 유지하면 Hand 변화량 제곱합은 본래 최대2이므로, Hand의 명시적100 제한은 정상 유한 입력에서 수치를 바꾸지 않는다. 이번 변경의 주요 효과는 Arm의 상한 없는 비용을 제한하는 것이다. Hand의 clamp를 제거하라는 요청으로 확대하지 않는다.

control dt0.02초와 weight-1 기준 Arm 기여의 최대 절댓값은 step당0.06이다. 두 그룹의 cap100만으로 계산한 일반 상한은0.12이지만, 현재 Hand 입력 한도까지 반영하면 합계 최대 절댓값은 **0.0612**다.

Relative-v0의 reward 구성에서 공통 한도를 적용하고 v2/v3가 상속하도록 계획한다. 기존 `policy_action_rate_penalty`는 Refactor-v0_1/v1_1/v2_1/v3_1도 공유하므로, 함수 기본 동작을 무조건 바꿔 상위·다른 환경까지 변경하지 않는다. 구현 시 선택적 한도 인자 등을 검토하여 Relative-v0에서 두 그룹의100을 지정하고 하위에 전파한다. 기존 파일 구조·reset 이전 action 처리·계수·dt 적용은 유지한다.

## 이번 계획에 포함하지 않는 변경

raw Fixed Joint reaction, 손의 질량·관성·중력 보정식, EEF 좌표계, 물리 충돌·관절 한계는 유지한다. F/T 기반 보상과 물리 진단 지표의 입력을 함께 clipping하는 변경도 포함하지 않는다. 진단용 raw/보정 F/T와 모델에 전달된 제한 후 관측은 구분한다.

실제 실행 action의 추가 clipping, 위2번 외의 action-rate 보상 변경, PPO 학습률·entropy·std·value loss 보호 상한 변경, 관측 normalization은 추가하지 않는다. 기존 분석의 수정 후보를 이번 확정 요구사항으로 자동 포함하지 않는다.

## 구현 검증 기준

- 경계값: 각 축의 범위 내부·정확한 경계·양수 초과·음수 초과를 확인한다. 힘과 모멘트별 한도가 다르게 동작해야 한다.
- 순서: 노이즈 활성·비활성 두 경우의 최종 Actor/Critic tensor가 힘±150N, 모멘트±8N·m를 만족해야 한다.
- 상속: v0/v2/v3 실제 관측을 확인하고 v2의 critic 그룹도 포함한다. 타겟 관측 역할과58D/64D 입력 차원은 유지돼야 한다.
- reset: stale sensor masking과 기존 reset 동작을 보존하는지 확인한다.
- Action Rate: Arm/Hand 그룹별 제곱합이100 미만·동일·초과일 때 각각 확인한다. 축별 또는 전체 그룹 합에 cap을 적용하지 않았는지, 계수와 dt가 중복 적용되지 않았는지 확인한다. 실제 Hand clamp 유지로 정상 입력의 제곱합이2 이하인 것도 확인한다.
- 보존: 전후 설정을 대조하여 F/T 관측 한도와 Action Rate 그룹별 cap 외에 reward·action·termination·curriculum·PPO가 달라지지 않았는지 확인한다. v0/v2/v3에 cap이 전파되고 기존 Refactor 계열의 공유 함수 사용에는 변경이 없는지 확인한다.
- 실패 자료 재생: 저장된 v0/v2 failure 입력에 한도를 적용해 실제 정책 출력의 변화를 비교한다. 기존 정책의 offline 재생은 새 한도로 재학습한 성능이나 실제 물리 안정성 검증을 대신하지 않는다.
- 실제 환경 검증 및 별도 학습 요청 시 `src/inspire_sweep_baseline/scripts/train.py`를 사용한다. 장기 학습에서 재발하지 않는지는 별도로 검증한다.

1번은 큰 F/T 입력을 제한하고, 2번은 큰 raw action 변화로 인한 Action Rate 비용을 제한한다. 실제 action 자체를 제한하거나 학습의 모든 수치 문제를 해결하는 것은 아니다. 검증 전에는 중단 문제가 해결됐다고 기록하지 않는다.

## 관련 근거와 상태

- [학습 로그 분석과 실패 재생](../02_implementation/logs/2026-11-07_relative_training_analysis.md)
- [문서 작성 기록](../02_implementation/logs/2026-11-07_relative_ft_limit_plan.md)

현재 구현된 수정 항목은 **1번 F/T 관측 한도 설정**, **2번 raw 정책 Action Rate의 Arm·Hand 그룹별 최대100 복원**이다. 장기 학습 성능과 모든 접촉 상황의 안정성은 별도 검증 대상이다.
