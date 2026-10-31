# Final GoalAccuracy v0_2_1 개발 명세

[현재 인계](../00_HANDOFF_BRIEF.md) · [개발 지침](../../00_guidelines/09_DEVELOPMENT_GUIDE.md) · [작성 기록](../../02_implementation/logs/2026-10-31_final_goal_accuracy_v0_2_1_spec.md)

작성일: 2026-10-31. 상태: **후속 사용자 승인으로 구현·등록 완료**. 아래 본문은 승인 당시 개발 계획을 보존한다. 실제 결과와 검증 범위는 [구현 계약](../../02_implementation/environments/FINAL_GOAL_ACCURACY_V0_2_1_ENVIRONMENT.md) 및 [개발 로그](../../02_implementation/logs/2026-10-31_final_goal_accuracy_v0_2_1_implementation.md)를 따른다. 학습은 시작하지 않았다.

구현 조정: GPU probe에서 actor/collider 전환 실패가 관찰되어 물리 인덱스를 고정했다. 비선택 후보는 원격 배치·속도 초기화·중력 해제·논리 제외로 격리한다. 아래 명세와 달리 collider enabled 플래그 자체는 끄지 않는다. 실제 16종 후보 검사에서 비선택 후보의 손 접촉력이 0임을 확인했다.

## 1. 목적과 기준

직접 부모는 `FinalGoalAccuracyV0_2EnvCfg`다. 타겟 접촉 보상에서 목표 점유 대체 조건을 제거하고, timeout 성공 보너스를 +75로 변경하며, 매 에피소드 reset에서 타겟 종류를 재선택한다. 사용자가 관찰한 선반에 손을 비비는 행동은 동기이며, 세 변경이 그 행동을 해결한다는 인과관계나 성공률 향상은 아직 검증하지 않았다.

| 항목 | 부모 v0_2 | 계획 v0_2_1 |
| --- | --- | --- |
| `target_contact` | 실제 타겟 접촉 OR 유효한 목표 점유 | 실제 타겟 접촉만 |
| 접촉 weight / 힘 임계값 | 1.45 / 0.01N | 동일 |
| timeout 성공 보너스 | +30, 성공 timeout AND `d < 0.02m` | **+75**, 성공 timeout인 `d <= 0.02m` |
| 목표 반경 | 0.02m 고정 | 동일 |
| 타겟 형상 선택 | 씬 생성 시 선택, reset 동안 고정 | 첫 reset 및 매 reset에서 재추첨 |
| 타겟·장애물 배치 및 목표 생성 | 매 reset 재생성 | 기존 분포를 사용해 매 reset 재생성 |
| 장애물 종류·크기 | 씬 생성 시 결정 | 부모 방식 유지 |
| 다른 보상·종료·PPO·관측 | 부모 구성 | 의미·차원·수치 유지 |

사용자 요청 2의 `현 기준 cm`는 직전 대화와 실제 부모 코드에 따라 **2cm**로 해석한다. 경계 포함은 프로젝트의 목표 도달 규칙 `d <= r`를 적용한 명세 결정이다. 따라서 보너스 변경은 weight만의 변경이 아니라 부모의 strict 경계 조건을 성공 판정과 일치시키는 변경도 포함한다. 이 차이를 구현 대조에서 누락하지 않는다.

## 2. 등록·상속 계약

아래 이름은 구현 시 사용할 계획 이름이며 아직 등록되어 있지 않다.

| 구분 | 계획 |
| --- | --- |
| Gym ID | `Isaac-Inspire-Final-GoalAccuracy-v0_2_1` |
| EnvCfg | `FinalGoalAccuracyV0_2_1EnvCfg(FinalGoalAccuracyV0_2EnvCfg)` |
| RewardsCfg | `FinalGoalAccuracyV0_2_1RewardsCfg(FinalGoalAccuracyV0_2RewardsCfg)` |
| SceneCfg | `FinalGoalAccuracyV0_1SceneCfg`를 직접 기반으로 한 파생 설정 |
| EventsCfg | 부모가 사용하는 `FinalV1EventsCfg` 기반 파생 설정 |
| runtime | 기존 `FinalGoalAccuracyEnv` 재사용 가능성을 먼저 확인하고, 타겟 선택 lifecycle이 필요하면 이를 상속한 전용 runtime 사용 |
| PPO | `FinalGoalAccuracyV0_2PPORunnerCfg` 상속, experiment 이름만 변경 |
| experiment_name | `inspire_final_goal_accuracy_v0_2_1` |

v0_3를 부모로 삼지 않는다. v0_2 및 다른 기존 환경의 함수 결과·최종 설정·물리 자산을 바꾸지 않는다. 같은 계열의 기존 역할별 파일에 추가하며 파일 이동이나 디렉터리 재편을 하지 않는다.

## 3. 실제 타겟 접촉만 보상

[현재 보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/final.py)의 `target_contact_or_goal`을 부모용으로 보존하고, 자식 전용 접촉 함수를 추가한다. Manager term 이름은 `target_contact`를 유지한다.

```text
contact = sensor_data_fresh
          AND 타겟–손 법선 합력 벡터의 모든 성분이 finite
          AND norm(타겟–손 법선 합력) >= 0.01 N

raw_reward = float(contact)
step_reward = 1.45 * step_dt * raw_reward
```

- 목표 위치·반경·속도·점유 여부를 접촉 보상의 대체 조건으로 사용하지 않는다.
- 실제 접촉 분기에 부모에 없던 높이·기울기·속도·체류시간 조건을 추가하지 않는다.
- 목표 안에서도 손이 떨어지면 접촉 보상은 0이다. 목표 밖이라도 접촉 조건을 만족하면 보상을 받는다.
- 손–선반·손–바닥·손–비타겟 장애물 접촉은 이 항으로 보상하지 않는다.
- 합력은 접촉별 힘 크기의 합이 아니라 법선 힘 벡터를 합친 뒤 취한 norm이다. 반대 힘의 상쇄 특성을 보존하며 접선 마찰력이나 모든 기하학적 접촉을 검출한다는 의미로 확장하지 않는다.
- 새 타겟 선택 후 센서가 fresh해지기 전에는 이전 타겟의 접촉을 보상하지 않는다.

기존 제어 주기 `step_dt=0.02s`에서 조건을 만족한 step의 보상은 0.029다. 목표 유지·거리 보상은 별개이며 타겟 비접촉 상태에서도 부모 조건에 따라 지급된다.

## 4. timeout 성공 보너스 +75

`target_goal_timeout_bonus` 이름을 유지하고, 기존 `success_event`를 `termination_name='target_goal_success_at_timeout'`, weight **75.0**으로 사용한다.

```text
성공 = timeout AND (타겟 현재 world XY와 목표 XY 사이 거리 d <= r)
r = target_goal_hold.params.position_tolerance = 0.02 m
raw_bonus = float(성공) / step_dt
실제 이벤트 보상 = 75 * step_dt * raw_bonus
```

에피소드 종료 전이에서 한 번만 +75를 지급한다. 조기 목표 진입이나 접촉만으로는 지급하지 않는다. 별도 접촉·속도·체류시간·자세 gate를 추가하지 않는다. 성공 term을 그대로 재사용하여 부동소수점 경계 판정을 중복 계산하지 않는다.

| 상태 | 보너스 |
| --- | --- |
| timeout 전, 목표 안 | 0 |
| timeout, `d < 0.02m` | +75 |
| timeout, `d = 0.02m` | +75 |
| timeout, `d > 0.02m` | 0 |
| 실패로 조기 종료, timeout 아님 | 0 |

실패와 timeout이 같은 step에 동시에 성립하는 경우의 처리 우선순위는 부모 termination 계약을 보존한다. 성공·미달 timeout은 기존처럼 truncation으로 처리하고 목표 진입 즉시 종료하지 않는다. 양의 보상 누적을 참조하는 wrist wrench budget이 timeout 보너스를 볼 수 있도록 부모의 보상 계산 순서를 유지한다.

## 5. 타겟 종류 재선택

### 5.1 현재 구현 확인

[SceneCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/final.py)는 `MultiAssetSpawnerCfg(random_choice=True)`로 타겟을 생성한다. [타겟 후보 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/final_spawners.py)의 `final_prop_variants(..., target=True)`는 원통·직육면체·기타 물체군을 각각 1/3 확률로 선택하도록 후보를 구성한다. 기타 물체군에는 기존 스캔 물체의 크기 변형과 mug·bottle이 포함된다. **부모가 직육면체만 생성하는 것은 아니다.**

직육면체의 기본 치수만 v0_1에서 0.06 × 0.08 × 0.10m로 조정된다. 추가 균일 크기 배율 0.9~1.1은 `prestartup`의 `randomize_object_sizes`에서 설정되며 reset에서 다시 추첨되지 않는다. [reset 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/final.py)의 `randomize_final_scene`은 이미 생성된 타겟의 경계값으로 배치·목표를 샘플링한다.

### 5.2 기본 설계 해석

추가 사용자 지정이 없으면 **기존 후보군과 선택 확률을 유지하여 reset마다 독립 재추첨**한다. 새로운 자산이나 형상을 추가하지 않는다. 독립 재추첨이므로 직전과 같은 종류가 연속으로 선택될 수 있다. “전부 변경”은 배치와 타겟 종류를 모두 다시 샘플링한다는 뜻으로 해석하며, 연속 중복 금지까지 요구된 것으로 보지 않는다. 직전과 반드시 다른 종류를 원한다는 후속 지정이 있으면 이 절의 선택 분포와 검증 기준을 먼저 수정한다.

타겟 선택은 최초 에피소드와 자동·수동·부분 reset에 모두 적용한다. 에피소드 중에는 타겟 종류를 바꾸지 않는다. 선택 단위는 환경별이며, 일부 env만 reset할 때 다른 env의 타겟·센서·관측·정책 상태를 변경하지 않는다.

별도의 매 reset 연속 크기 배율 재추첨은 추가하지 않는다. 후보 자체의 기존 크기 변형과 0.9~1.1 생성 시 배율은 보존한다. 타겟의 질량·마찰 등은 부모의 reset 물성 분포를 선택된 실제 body에 적용한다. 장애물 종류를 reset마다 재선택하는 기능은 이 요청에 포함하지 않는다.

### 5.3 물리적 교체 설계

`prestartup` 함수를 단순히 reset Event로 옮기거나 `target_id`만 바꾸는 것으로 완료하지 않는다. 실제 시각 형상·충돌 형상·질량/관성·센서 참조가 선택된 물체와 일치해야 한다. 현재 크기 함수는 PhysX 실행 중 호출을 명시적으로 금지한다.

우선 설계는 **초기화 때 타겟 후보 물리 자산을 준비하고 reset에서 선택하는 방식**이다. 타겟 후보용 저장소와 논리적 타겟을 분리하고, 학습에서 보이는 타겟은 항상 한 개로 유지한다. 미선택 후보는 작업 영역·충돌·센서 집계·장애물 관측·보상·종료 검사에서 배제한다. 보관 위치 이동만으로 비활성 처리가 완료됐다고 간주하지 않는다.

기존 코드에는 타겟 슬롯 0, 장애물 슬롯 1 이후, 고정 object collection 순서를 가정한 경로가 있다. 외부 학습 계약은 **논리 타겟 슬롯 0과 기존 장애물 슬롯 수**를 유지한다. 물리 후보의 인덱스가 달라지면 자식 전용 선택/매핑 계층에서 좌표·속도·접촉·geometry metadata·물성 write 대상을 일관되게 연결한다. 풀 후보를 장애물 관측 슬롯에 추가하거나 기존 장애물 일부를 타겟 풀로 전용하지 않는다.

풀의 정확한 PhysX 활성화 방식과 API는 아직 검증하지 않았다. 구현 착수 시 소규모 실제 시뮬레이션으로 충돌 활성화·센서 참조 유지·부분 reset의 독립성을 먼저 검증한다. 이 방식이 지원되지 않으면 대안을 설계하되, 실행 중 USD 교체를 검증 없이 사용하거나 씬 전체를 매 reset 재생성하는 우회로를 채택하지 않는다. 이 명세만으로 Event 함수 하나의 변경으로 구현 가능하다고 판단하지 않는다.

### 5.4 reset 순서와 상태 일관성

1. 종료되는 에피소드의 보상·성공 판정·지표를 기존 타겟 기준으로 확정한다.
2. reset 대상 env의 센서 freshness 및 에피소드 상태를 초기화한다.
3. 새로운 타겟 후보를 추첨하고 실제 body 및 metadata를 선택한다.
4. 새 타겟의 경계값·바닥 높이·폭을 먼저 적용한다.
5. 그 geometry로 타겟·목표·장애물 배치를 새로 샘플링하고 위치·자세·속도를 초기화한다.
6. 선택된 body에 부모의 물성 randomization을 적용한다. 관성이 형상·배율과 일치하는지 확인한다.
7. 활성 마스크, 초기 물체 위치, 목표 command, 타겟 폭, 가림 판정·초기 장애물 관측, 보상 이력을 새 에피소드 상태로 맞춘다.
8. 기존 Actor/Critic 차원과 term 순서를 유지한 첫 관측을 반환한다.

EventManager·CommandManager·RewardManager의 실제 reset 실행 순서와 위 요구를 대조한다. 이전 목표·타겟의 상태가 새 에피소드의 보상이나 관측에 섞이면 실패다. 동일 seed와 동일 reset 호출 순서에서 선택열·배치를 재현할 수 있어야 한다. 후보 추첨용 RNG를 배치 RNG와 분리하여 종류 선택 때문에 기존 배치 샘플러의 확률 규칙이 바뀌지 않도록 한다.

## 6. 보존 항목과 허용 변경 범위

- `target_reaching`: `DexReachProgress`, weight 30, near radius 0.10m.
- `target_goal_distance`: 지수 거리 함수, distance scale 0.05m, weight 3.7. v0_3의 최단 거리 보상으로 교체하지 않는다.
- `target_goal_hold`: weight 8, 내부 0.02m, 외곽 0.06m, speed scale 0.05m.
- 접촉과 timeout 보너스를 제외한 모든 보상·패널티의 callable·params·weight·순서 및 커리큘럼 유지.
- 선반 패널티·종료 조건을 변경하거나 새로운 선반 접촉 패널티를 추가하지 않는다.
- 부모의 timeout 10초, physics dt 0.01초, decimation 2, action·OSC·로봇 설정 유지.
- Actor/Critic 관측의 차원·순서·초기/현재 상태 구분 유지. 타겟 종류 one-hot이나 현재 물체 상태를 Actor에 추가하지 않는다.
- 장애물 관측 20슬롯과 Gray/White 용량 각 10 유지. 활성 요청 수는 기존 일정과 최종 Gray 4·White 5 유지.
- PPO 모델·하이퍼파라미터·rollout 길이 유지. 새 experiment 이름으로 결과를 구분한다.

타겟 물리 자산 선택을 위한 Scene/Event/runtime/센서 매핑 변경은 요구사항 3을 위한 범위로 한정한다. 타겟 후보 수만큼 물리 body와 센서가 늘어날 수 있으므로 계산량·메모리가 부모와 같다고 가정하지 않는다. 관측·보상 수식이 같아도 내부 선택 경로의 변경은 최종 차이 표에 명시한다.

## 7. 구현 파일 계획

| 위치 | 계획 책임 |
| --- | --- |
| `envs/final_envs.py` | v0_2 직계 파생 EnvCfg 구성 |
| `mdp/rewards/final.py` | 접촉 함수 교체, timeout +75, 기존 순서 보존 |
| `mdp/reward_functions/final.py` | 타겟 접촉 전용 함수 |
| `assets/scenes/final.py`, 필요 시 `assets/final_spawners.py` | 부모 후보 정의를 재사용하는 타겟 후보 준비 |
| `mdp/events/final.py`, `mdp/event_functions/final.py` | 자식 전용 reset 선택·배치 동기화 |
| 기존 `mdp/common/` 및 `runtime/final.py` | 필요한 경우에만 자식 전용 물리/논리 매핑과 lifecycle |
| `agent/final_ppo_cfg.py`, `__init__.py` | PPO 파생 설정과 신규 Gym 등록 |
| `tests/` | 경계·부모 회귀·타겟 선택·부분 reset 검사 |

기존 함수의 기본 동작을 바꿔 다른 환경으로 차이를 전파하지 않는다. 아직 없는 클래스와 경로를 현재 사용 가능한 구현으로 문서화하지 않는다.

## 8. 수용 기준

### 8.1 CPU·설정 검사

- 목표 안/밖 각각에서 실제 타겟 접촉 유무를 조합한다. 비접촉 목표 점유 보상은 0이어야 한다.
- stale, NaN/Inf, 0.01N 바로 아래·정확히 동일·바로 위, 반대 힘 상쇄를 검사한다.
- 선반·비타겟 접촉만 있고 타겟 접촉이 없으면 0이어야 한다.
- timeout 전/후와 거리 2cm 경계 세 점을 검사한다. dt를 바꿔도 이벤트 총 보너스는 +75다.
- 초기 reset·자동 reset·부분 reset·빈 env_ids·seed 재설정에서 타겟 선택과 상태 초기화를 검사한다.
- 고정 seed 장기 표본으로 원통/직육면체/기타 물체군의 1/3 분포와 기타 후보 내 부모 선택 비율을 검사한다. 동일 후보 연속 선택은 기본 설계에서 오류가 아니다.
- 기존 부모의 전후 설정 동등성과 결과를 회귀 검사한다. 자식과 부모의 차이는 요청된 세 기능 및 그 구현에 필요한 등록·상태 경로로 한정한다.

### 8.2 실제 물리 검사

- 원통·직육면체·기타 물체군으로 반복 전환하고, 시각 형상과 실제 충돌 형상의 일치를 확인한다.
- 손–선반만 접촉, 손–타겟만 접촉, 동시 접촉을 재현해 실제 센서·보상 값을 대조한다.
- 선택 해제한 후보가 관측·접촉·성공/실패 판정에 섞이지 않는지 검사한다.
- geometry에 따른 바닥 관통 방지, target width, 초기 가림 판정, 질량·관성 일치를 확인한다.
- 일부 env reset 동안 나머지 env의 물리 상태와 센서가 영향을 받지 않아야 한다.
- 진단용 `target_kind_id`, 타겟 접촉 여부, 목표 점유 여부를 구분하여 확인한다. 진단값을 정책 관측으로 추가하지 않는다.

### 8.3 성능·학습 평가

동일 장치·num_envs·렌더링·rollout 조건으로 부모와 자식의 collection 시간, reset 시간, GPU 메모리, 물리 오류를 비교한다. 특히 4000/4500/5000 iteration 커리큘럼과 최종 장애물 수에서 검사한다. 장기 반복 reset에서 메모리나 센서 객체 수가 계속 증가하면 실패다. 성능 허용 수치는 사전 측정 후 정하며 이 문서에서 근거 없는 합격 배수를 지정하지 않는다.

학습 검증은 별도 개발 단계에서 `scripts/train.py`를 사용한다. 동일한 목표 반경 2cm와 평가 타겟 분포로 성공률·거리·실패율·선반 접촉 행동을 확인한다. 세 기능을 동시에 바꾸므로 통합 결과만으로 특정 변경의 효과를 분리해 주장하지 않는다. 부모 checkpoint를 새 환경의 학습 완료 결과로 간주하지 않는다.

## 9. 이번 문서 작업의 완료 범위

현재 코드와 저장된 학습 설정을 근거로 계획을 작성했다. 후보 풀 구현 가능성, 실제 센서 전환, 물리 안정성, collection 성능, 학습 성공률은 모두 미검증이다. **이번 작업에서는 소스 코드·자산·학습 설정·학습 로그를 변경하지 않으며 실제 개발·실행에 착수하지 않는다.**
