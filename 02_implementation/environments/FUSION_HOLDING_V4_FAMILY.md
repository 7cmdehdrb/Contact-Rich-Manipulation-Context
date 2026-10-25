# Holding v4 · OSC v4 · ObjectRandom v3

[환경 안내](README.md) · [계열·v3 통합 계약](FUSION_HOLDING_FAMILY.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [개발·검증](../logs/2026-10-25_fusion_holding_v4.md)

기준일: 2026-10-25. 사용자는 ObjectRandom-v2 재생에서 목표 거리 0.011389 m가 live 반경 0.009750 m보다 커서 success가 발생하지 않는 출력을 확인했다. 이번 계열은 success 종료와 goal hold 지급 상한을 제거하고 중심 정착·장기 유지를 학습하도록 변경한다. Timeout 100%는 학습 목표이며 구현·짧은 검사의 달성 결과가 아니다. 실패 종료는 유지한다.

## 등록과 상속

환경명의 공통 접두사는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-`이다. Runtime은 기존 `inspire_sweep_baseline.runtime.contact_sweep_clutter_fusion:ContactSweepClutterFusionV1_0Env`, runner는 `CurriculumOnPolicyRunner`를 재사용한다.

| 환경명 | EnvCfg / 직접 부모 | PPO Cfg / experiment |
| --- | --- | --- |
| `Holding-v4` | `FusionHoldingV4EnvCfg` / `FusionHoldingV3EnvCfg` | `FusionHoldingV4PPORunnerCfg` / `inspire_contact_sweep_clutter_fusion_holding_v4` |
| `Holding-OSC-v4` | `FusionHoldingOSCV4EnvCfg` / `FusionHoldingV4EnvCfg` | `FusionHoldingOSCV4PPORunnerCfg` / `inspire_contact_sweep_clutter_fusion_holding_osc_v4` |
| `Holding-OSC-ObjectRandom-v3` | `FusionHoldingOSCObjectRandomV3EnvCfg` / `FusionHoldingOSCV4EnvCfg` | `FusionHoldingOSCObjectRandomV3PPORunnerCfg` / `inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v3` |

같은 계열의 기존 `envs/contact_sweep_clutter_fusion_holding*_envs.py`와 `agent/contact_sweep_clutter_fusion_holding*_ppo_cfg.py`에 버전을 추가했다. 이전 버전의 task와 보상 계약은 보존하고 임시 success 출력 블록·활성화 줄은 주석 처리했다.

## Holding-v4: 종료와 중심 보상

`FusionHoldingV4TerminationsCfg.success=None`으로 success term을 제거한다. 기존 object drop·push fast·shelf collision·hand velocity·shelf displacement와 timeout을 유지한다. 물체가 goal에 오래 머무는 것만으로 episode를 종료하지 않는다.

`goal_hold`는 상태·시간 예산이 없는 `goal_settling_centered` 함수이며 `max_hold_time` 인자가 없다. 가중치는 4, speed scale s는 초기0.05 m/s이며 기존 커리큘럼에 따라10000 iteration에서0.02 m/s가 된다. 유효한 물체의 XY 목표 거리 d, XYZ 속도 크기 v, live goal 반경 r에 대해 다음 rate를 사용한다.

```math
q(d,v,r)=\exp\left(-\ln(2)\left((d/r)^2+(v/s)^2\right)\right)
```

```math
h(d,v,r)=\begin{cases}
q(d,v,r)\left(1+(1-d/r)^2\right), & \text{valid},\ 0\le d<r,\\
q(d,v,r), & \text{valid},\ r\le d\le 2r,\\
0, & d>2r\text{ 또는 상태 무효}.
\end{cases}
```

추가 multiplier는 구현 선택이다. r 경계에서 1로 연속이고 중심에서 2다. d=0,v=0의 rate는 기존 1에서 2, 가중치를 적용한 초당 값은 4에서 8로 증가한다. d=r,v=0은 rate0.5·초당2다. 2026-10-25 후속 사용자 요청으로 지급 범위를 d<=2r까지 확장했다. r<d<=2r에서는 중심 강화 없이 같은 거리·속도 감쇠를 적용하며, d=2r,v=0은 rate0.0625·초당0.25다. d>2r 또는 상태 무효에서0이다. 오래 유지할수록 시간 상한 없이 누적되며 RewardManager가 weight와 step_dt를 한 번 적용한다. Contact·Reaching의 goal 트리거는 여전히 d<=r다.

## ReachingOrGoal

기존 `DexReachProgress`의 live 물체–고정 wrist EEF 간 XYZ 거리, reset snapshot, 새 최단 거리만 지급하는 방식을 유지한다. `reaching`의 가중치는 30, 일반 `near_radius`는 0.10 m다.

- `hand_contact_or_goal`과 같이 유효한 물체가 `distance_xy <= goal_radius(env)`에 있으면 트리거 ON이다. 속도·실제 접촉·3초 유지 조건은 없다. 별도 episode latch 없이 매 step 재평가한다.
- ON이면 접근 인정 반경을 `goal_near_radius=1.0 m`로 늘린다. 1.0 m는 이번 구현의 기본값으로 Cfg params에서 조절할 수 있다. 유효 gap은 `max(EEF 거리 - 현재 인정 반경, 0)`이다.
- 목표 반경은 reward manager의 `goal_hold.position_tolerance`를 읽으므로 기존 2→1→0.5 cm 커리큘럼과 resume·되감기에 연동된다. goal 밖·무효 상태에서는 0.10 m를 사용한다.
- ON 진입으로 gap이 줄면 남은 reaching 기록을 한 번 지급할 수 있다. 접근 기록은 episode 동안 단조 감소하므로 이탈·재진입·반경 변경으로 같은 progress를 재지급하지 않는다. 부분 reset은 선택된 환경의 기록만 복원한다.

따라서 goal 안에서 손을 계속 더 가까이 붙이는 것으로 추가 reaching 보상을 얻지 않는다. Actor 입력에 새 트리거나 GT 관측을 추가하지 않는다.

## OSC·ObjectRandom과 보존 계약

OSC-v4는 Holding-v4를 직접 상속하고 `configure_reach_osc`만 적용한다. OSC-v3의 frame·RPY·scale·gain·EEF offset·관성 분리·중력 보상·effort 제한을 그대로 사용한다. ObjectRandom-v3는 OSC-v4를 직접 상속하고 ObjectRandom-v2와 같은 scene·events·`ObjectRandomV2CurriculumCfg`를 사용한다. 물리8/8·관측16슬롯, 활성 최대6/6, 개수 교대 일정과 Gray 15% 패딩, 자산·물성·배치 규칙은 동일하다.

공통 입력은 policy55D+초기 장애물64D, Critic에 현재 타겟 XYZ3D 추가로 raw119D/122D이며 encoder 이후71D/74D다. Action은 Arm6D+Hand2D, dt=0.02초다. Holding은 Joint Position이고 나머지 두 환경은 기존 OSC다. 관측·reset·기타 보상·커리큘럼·PPO 및 네 로컬 운동 페널티(raw 제곱합, Arm/Hand 분리, −0.03/−0.03/−0.03/−0.01)는 유지한다.

## 실행

Workspace 루트, Isaac Lab 환경과 기존 선반·물체 자산 접근이 필요하다.

```powershell
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v4 --num_envs 2048 --headless
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v4 --num_envs 2048 --headless
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v3 --num_envs 256 --headless
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/play.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v3 --num_envs 1 --checkpoint "<checkpoint.pt>" --real-time
```

새 experiment마다 학습 결과를 분리한다. 기존 checkpoint 재생은 새 정책의 학습 효과나 timeout 비율을 증명하지 않는다. 실제 실행 범위는 [개발 로그](../logs/2026-10-25_fusion_holding_v4.md)에 기록한다.

## r을 중심으로 본 네 보상

r은 RewardManager의 `goal_hold.params["position_tolerance"]` 현재값이다. d는 타겟 중심과 goal의 world XY 거리다. EEF 거리나 물체 표면 간 거리가 아니다. 타겟 유효성은 position·velocity·goal XY·정렬값이 finite이고, 선반 로컬 |x|≤0.16m, |y|≤0.46m, z∈[1.04,1.07]m, upright alignment≥cos(0.9)인 조건이다.

| 보상 | r의 용도 | 지급 방식·가중치 |
| --- | --- | --- |
| Goal Distance | 사용하지 않음. position_tolerance=0 | DexPlanarGoalProgress의 새 최단 XY 거리 개선량÷dt, weight 100. 1cm 새 개선은 실제 +1 |
| Goal Hold | 감쇠 분모 r, 지급 경계 2r, 중심 강화 경계 r | 위 h×4×dt. 유효하지 않거나 d>2r이면 0 |
| Contact | 유효한 d≤r이면 접촉으로 간주 | fresh·finite 손 전체 접촉력≥0.01N 또는 goal 인정. raw 1×1.45×dt, 중복 지급 없음 |
| Reaching | 유효한 d≤r에서 goal 트리거 ON | EEF-타겟 XYZ 거리의 인정 반경 0.10→1.0m. 새 gap 기록 개선량÷dt, weight 30 |

Goal Distance와 Reaching은 진전 기록을 갱신할 때만 지급하며 멀어졌다 돌아오는 같은 진전은 재지급하지 않는다. Contact·Reaching의 goal 트리거에는 속도·유지 시간 조건이 없다. **r<d≤2r에서는 Holding만 지급 범위에 들어가며 goal 접촉 간주·Reaching 완화는 OFF**다. 실제 손 접촉이 있으면 Contact는 별도로 지급된다. 1.0m는 EEF 접근 인정 거리이며 goal 반경이 아니다.

## 반경 일정과 관련 항목

| learning iteration | r | Holding 지급 경계 2r |
| --- | --- | --- |
| 0~5000 | 0.020m | 0.040m |
| 7500 | 0.015m | 0.030m |
| 10000 | 0.010m | 0.020m |
| 10500 | 0.00975m | 0.01950m |
| 15000 | 0.0075m | 0.0150m |
| 20000 이후 | 0.005m | 0.010m |

FusionHoldingV2CurriculumCfg의 반경 일정은 각 구간에서 매 iteration 선형 보간한다. speed scale s는 6000까지 0.05m/s, 이후 250 iteration 간격 보간으로 10000에 0.02m/s가 된다. checkpoint load 시 학습 iteration에 해당하는 커리큘럼을 복원하며 play에서는 학습 iteration을 계속 증가시키지 않는다.

v4에는 r과 연결된 success 종료가 없다. 이전 v2/v3의 success 코드가 남아 있어도 v4 TerminationsCfg에서는 None이다. 나머지 종료는 10초 timeout, active 물체 drop/tilt(높이 1.04m·기울기 0.9rad 기준), push_fast 1.0m/s, shelf_collision 0.1N·wrist 여유 0.03m·finger 검사 제외, hand_velocity라는 이름의 Arm 6관절 5rad/s 검사, 선반 변위 0.05m다. object_outside_shelf는 None이다.

다른 보상은 r을 직접 읽지 않는다. Wrench 변화 비용의 누적 상한은 양의 에피소드 보상의 5%이므로 r에 따른 양의 보상 변화가 간접적으로 비용 예산에 영향을 준다. goal_deadzone은 목표 방향 각도 제외 일정이며 r과 다르다. 장애물 개수·Gray padding도 r과 독립이다.

Arm/Hand action-rate·joint-velocity 네 비용은 로컬 goal_rewards 함수, raw Action 변화량·실제 관절 속도 제곱합을 사용한다. 계수는 Arm Action/Velocity −0.03/−0.03, Hand Action/Velocity −0.03/−0.01이다. 물체 기울기·변위, 선반 충돌/실패, 물체·Arm·EEF 과속, 장애물 접촉, 물체 가속도, wrench 변화 비용은 상속한다. EEF orientation 보상은 비활성이다. [기존 전체 보상 계약](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V0_ENVIRONMENT.md)의 공통 비용에 이 문서의 네 양의 보상 변경을 적용한다.

## 이론상 최대와 검증 범위

| goal hold만 비교 | Holding-v2 | Holding-v4 |
| --- | --- | --- |
| d=0, v=0 raw 최대 | 1 | 2 |
| weight 적용 최대 rate | 4/s | 8/s |
| dt=0.02초 실제 step 최대 | 0.08 | 0.16 |
| 지급 시간 예산 | 없음 | 없음 |
| 연속 중심·정지 | 3초 success 종료 | 최대 10초 timeout까지 유지 가능 |

v2의 3초 중심·정지 예시는 12지만 모든 궤적의 에피소드 보상 상한을 뜻하지 않는다. 속도 조건으로 success를 피하면서 다른 rate로 더 오래 지급받을 수 있다. v4의 이상적인 10초 중심·정지 합계는 80이다. 두 값에는 도달 시간·다른 보상·비용을 포함하지 않는다.

최초 구현의 CPU 검사 71개와 실제 Isaac Sim 2환경 smoke·강제 timeout 검사가 통과했다. 이후 2r 확장에서는 v2/v3/v4 CPU 회귀 36개가 통과했으며 Sim 재실행은 하지 않았다. 이번 문서 개정은 링크·수식·등록 목록의 정적 검사이며 학습이나 시뮬레이션을 새로 실행하지 않는다.

[Holding-v4 상세](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V4_ENVIRONMENT.md) · [OSC-v4 상세](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_V4_ENVIRONMENT.md) · [ObjectRandom-v3 상세](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V3_ENVIRONMENT.md) · [보상 구현](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/contact_sweep_clutter_fusion_holding_scheduled.py)
