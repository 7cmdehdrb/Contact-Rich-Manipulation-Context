# 독립 Sweep v0 환경

## 과업과 설계 목적

`Inspire-Sweep-v0`는 초기 시각 관측과 조작 중 촉각·손목 F/T 피드백을 사용하여 선반 위 타겟을 목표 위치까지 이동시키는 강화학습 환경이다. 타겟과 주변 물체의 실제 상태는 시뮬레이터의 보상·평가에 사용하고, 정책에는 초기 관측을 기준으로 구성한 물체 정보와 로봇·접촉 관측을 제공한다.

사용자는 기존 환경에서 Pull·Push 방향을 제외하면 상당한 과업 성공을 관찰했으나, 목표 방향에 따라 접촉면을 선택하기보다 항상 손등으로 밀려는 편향이 있었다고 보고했다. Sweep-v0는 **타겟을 목표까지 이동시키면서, 방향에 따라 손바닥 또는 손등을 선호하는 행동**을 유도하기 위해 구현했다. 이 관찰은 사용자의 기존 환경에 관한 보고이며, 새 환경의 성능 개선을 확인한 결과는 아니다.

2026-11-20 사용자 보고 기준 `.180`에서 이 환경을 학습 중이다. 계통의 개발 배경·비교 환경·최신 학습 현황은 [Sweep 계통 안내](SWEEP_FAMILY.md)를 기준으로 관리한다.

## 등록과 기준

Task ID는 **`Inspire-Sweep-v0`**, 로그 experiment name은 **`inspire_sweep_v0`**이다. 사용자가 지정한 `Inspire-Sweep-Only-v2-Test-ActionPenalty-LinearReach`의 최종 구성을 기능 기준으로 삼되, 후속 요청에 따라 긴 버전 이름을 이어 붙이지 않고 새 계통으로 선언했다.

- [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_v0_envs.py)의 `SweepEnvCfg`는 `ManagerBasedRLEnvCfg`를 직접 상속한다. 이전 task EnvCfg를 상속하지 않는다.
- [PPO](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/sweep_v0_ppo_cfg.py)의 `SweepPPORunnerCfg`는 `RslRlOnPolicyRunnerCfg`를 직접 상속한다. 기존 PPO와 값은 같고 experiment name만 다르다.
- [Runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/sweep_v0.py)의 `SweepEnv`는 기존 `SweepOnlyEnv`의 검증된 reset·step·접촉 샘플링·지표 수집을 재사용한다. 모든 물리 실행 코드를 복제한 환경은 아니다.
- Scene·Action·Observation·Command·Event·Reward·Termination의 공통 Cfg와 모델을 재사용하되, 새 EnvCfg에서 최종 구성을 명시한다. 기존 `envs/sweep_envs.py`는 과거 baseline이 사용하므로 덮어쓰지 않는다.

## 장면과 초기화

로봇은 UR5e–Axia80–RH56E2 오른손 조합이며, 선반 위의 고정 타겟 슬롯과 최대6개 활성 주변 물체를 사용한다. 물리 collection은 타겟1개와 주변 슬롯16개를 보유하고, 관측 장애물 슬롯도16개다. 비활성 물체는 과업 영역 밖에 주차한다. 물체 형상·크기·질량·마찰 등은 재사용하는 Scene·startup 설정을 따르며 모든 항목을 매 episode마다 다시 추출하는 구성은 아니다.

초기화는 기존 Test의 Finger 방식 배치와 단일 Warp IK를 사용한다. 타겟 초기 XY는 선반 중앙 반지름2cm 영역에서 선택하고, 목표 거리는6–12cm다. 방향 Deadzone은0°다. 선반 경계·RED·물체 간 배치 조건은 유지하지만 일반 물체 옆 IK 환경과 같은 초기 로봇 전체 점유 공간 검사는 하지 않는다.

reset마다 초기 타겟·주변 물체의 관측 대표점을 저장한다. GUI의 빨간 대표점 마커는 초기 관측 위치를 표시하는 비충돌 마커이며, headless에서는 생성하지 않는다. 안정화 단계와 통과 Gate는 없고 처음부터 Sweep 상태다.

| 시간·규모 | 값 |
| --- | --- |
| 기본 병렬 환경 수 | 2,048 |
| 물리 간격 | 0.01 s / 100 Hz |
| 정책 간격 | 0.02 s / 50 Hz, decimation2 |
| Episode 최대 길이 | 10 s / 정책500스텝 |
| 목표 반경 설정 | 0.03 m; 실제 성공 비교는 아래 종료 조건 참조 |

근거: [Scene](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/stabilize_sweep.py), [Event Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/events/stabilize_sweep.py), [reset 실행](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/stabilize_sweep.py).

## 관측과 신경망

Actor와 Critic은 같은 `policy`66D 및 `obstacles`64D를 입력으로 사용한다. 두 네트워크의 파라미터와 장애물 encoder는 각각 독립적이다.

| 직접 관측 항목 | 차원 | 의미 |
| --- | --- | --- |
| 팔 관절 위치 | 6 | 실제 절대 관절 위치 |
| 팔 관절 속도 | 6 | 실제 관절 속도 |
| 손 구동 관절 위치 | 6 | 엄지 굽힘·검지·중지·약지·소지·엄지 대립 |
| EEF pose | 7 | 로봇 root 기준 위치·quaternion |
| 타겟 관측 대표점 | 3 | 초기 관측점을 현재 EEF frame으로 변환 |
| 목표 위치 | 3 | 현재 EEF frame 기준 |
| 직전 action | 12 | 원시 명령의 관측용 ±π/2 제한값 |
| 촉각 | 17 | 채널별 없음0·손바닥1·손등-1·양면2 |
| 손목 F/T | 6 | 중력·관성 보상 후 관측 noise·clip·정규화한 값 |
| 합계 | 66 | Phase 관측 없음 |

장애물은 `[valid,x,y,z]`16슬롯의64D다. 초기 시각 정보는 episode 중 물체의 실제 이동에 따라 갱신하지 않고, 현재 EEF의 이동·회전에 맞추어 좌표만 변환한다. 따라서 시뮬레이터가 보상 계산에 쓰는 현재 타겟 위치와 정책의 타겟 관측은 구분해야 한다. Critic에도 별도의 실시간 타겟 GT 입력은 없다.

장애물 encoder는 `64 → 32(ReLU) → 16`이며 무효 슬롯을0으로 마스킹한다. 본체 입력은 직접 관측66D와 embedding16D를 합친82D다. Actor는 `82 → 256 → 128 → 64 → 12`, Critic은 `82 → 256 → 128 → 64 → 1`이고 hidden activation은 ELU다. Actor는 Gaussian 정책을 사용하며 초기 표준편차는1이다. 일반 관측 정규화는 꺼져 있고, F/T에만 아래의 명시적 축별 정규화를 적용한다.

근거: [관측 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/stabilize_sweep.py), [모델](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/stabilize_sweep_models.py), [encoder와 모델 본체](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/wrench_refactor_models.py).

## 행동과 제어

액션은 팔6D OSC 상대 pose 명령과 손6D 절대 관절 위치 명령이다. 팔은 실행 직전에 각 축을±π/2로 제한하고 위치 scale0.03·회전 scale0.15를 적용한다. OSC는 고정 impedance, 관성 결합 해제와 중력 보상을 사용한다. 손은 URDF 범위로 제한하고 follower 관절은 기존 mimic 관계를 따른다.

손6축 상한은 `[0.5864,1.4381,1.4381,1.4381,1.4381,1.1641] rad`, 하한은0이다. Runner의 `clip_actions=None`이므로 ActionManager에는 원시12D 명령이 보존된다. 실제 실행은 제한되지만 action-rate와 action-limit 비용은 제한 전 명령으로 계산한다. 두 비용에는 추가 상한을 적용하지 않는다.

근거: [Action Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/actions/stabilize_sweep.py), [실행 직전 팔 제한](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/action_functions/wrench_refactor.py), [손 관절 제어](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/action_functions/sweep_simple.py).

## 방향별 접촉면 계수

Deadzone은 **0°**다. 구역 분류를 위해 목표 방향을 배제하지 않는다. 방향은 reset 때 정해진 `sweep_dir`을 선반 좌표로 변환하여 사용한다. 목표 근처에서 현재 타겟→목표 벡터가 반전해도 episode의 구역은 바뀌지 않는다.

12시는 로봇에서 멀어지는 선반 -X, 3시는 선반 +Y, 6시는 로봇 쪽 선반 +X, 9시는 선반 -Y이다. 12시에서 시계방향으로 잰 각도를 $\phi$라 한다.

| 구역 | 방향·범위 | 각도 폭 | 선호 접촉면 | 손바닥만 접촉 | 손등만 접촉 |
| --- | --- | --- | --- | --- | --- |
| 1 | 12시 중심 ±30° | 60° | 손등 | 0.7 | 1.5 |
| 2 | 3시 방향, 30°와 150° 사이 | 120° | 손등 | 0.7 | 1.5 |
| 3 | 6시 중심 ±30° | 60° | 손바닥 | 1.5 | 0.7 |
| 4 | 9시 방향, -150°와 -30° 사이 | 120° | 손바닥 | 1.5 | 0.7 |

정확히 ±30°는 구역1, 정확히 ±150°는 구역3이다. 사용자가 말한 Pull–Push의 60°는 구역 폭이며, Deadzone을 30°로 복원한다는 의미가 아니다.

계수 $c_t$는 **양의 Sweep 진행 보상**에만 곱한다. $h_t$는 Sweep-v0의 누적 접촉 계수, $a_t$는 부모의 힘 방향 정렬 계수다. 거리 $d_t$는 현재 타겟 bounds 중심과 목표의 XY 거리다. 거리 증분 보상은 실행 함수의 dt 나눗셈과 RewardManager의 dt 곱셈이 상쇄된다.

```math
r_{\mathrm{progress},t}
=50c_t h_t a_t\max(d_{t-1}-d_t,0),
\qquad
r_{\mathrm{retreat},t}=-10\max(d_t-d_{t-1},0).
```

접촉 카운트20·정렬1·1cm 전진이면 선호 접촉은0.75, 반대 접촉은0.35를 받는다. 역방향·Reach·나머지 비용에는 접촉면 계수를 곱하지 않는다.

### 접촉 유지와 힘 방향 정렬

Sweep-v0에는 **누적 Contact Count가 존재한다.** 정책 스텝의 타겟 접촉은 물리 샘플에서 유효한 타겟–손 법선 접촉 하중이0.01N 이상일 때 감지한다. 최근3개 정책 스텝 중 유효 접촉이2회 이상이고 EEF가 상판 위12cm 미만이면 인정값 $B_t=1$로 둔다. 그 밖에는0이다.

```math
K_t=\mathrm{clip}\bigl(K_{t-1}+B_t-2(1-B_t),0,20\bigr),
\qquad h_t=B_t\frac{K_t}{20}.
```

처음 인정되면 $K_t=1$이므로 접촉 계수는0.05이고, 인정이 누적되어20에 이르면1이 된다. 미인정 스텝에서는 카운트가2 감소하고 해당 스텝의 접촉 계수는0이다. reset은 이력과 카운트를 지운다. 이 누적 방식은 아래 Single Contact 자식의 boolean 방식과 다르다.

진행 보상은 현재 스텝의 실제 접촉·유효 데이터·수평 평균 힘1N 이상 조건도 요구한다. 정렬 계수는 현재 타겟→목표 XY 방향과 타겟에 작용한3D 평균 접촉력의 정렬을0–1로 제한한 값이다. 수평 힘만의 코사인과 달리 분모에는3D 힘 크기를 사용한다. 이 힘은 타겟 접촉 센서에서 얻으며, 정책의 손목 F/T 관측과 같은 값이 아니다.

근거: [접촉 샘플](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_contact.py), [이력·카운트·힘 정렬](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_state.py).

### 접촉면의 실제 판정

[새 보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/sweep_contact_preference.py)는 기존 오른손 tactile의 손바닥/손등 표면 기하 계산을 재사용한다. 관측 bit·관측 noise·정규화된 F/T로 접촉면을 추정하지 않는다.

1. 기존 타겟→핸드 contact matrix에서 직접 pad별 법선 합력의 크기를 손바닥 하중으로 읽는다. unfiltered pad 힘은 선반·장애물을 포함하므로 사용하지 않는다.
2. 각 hand parent 센서의 **타겟 필터만** 선택하여 접촉점·법선힘을 얻는다. 고정 타겟이 collection 첫 슬롯이라는 기준 환경의 계약을 유지한다.
3. `PairedContactRegions`가 pad footprint와 부모 convex hull의 양면으로 각 접촉점을 분류한다. 손바닥17·손등17 채널에 부모 접촉점별 법선힘 크기를 누적한다. 이 점별 누적에서는 서로 반대 방향의 힘을 벡터로 합산하여 상쇄시키지 않는다.
4. 양면이 함께 접촉하면 선호 면과 반대 면의 법선 접촉 하중 비율로 계수를 섞는다.

손바닥·손등 분류 하중을 $L_{p,t}$, $L_{b,t}$라 하고 선호 면 하중을 $L_{*,t}$라 하면 다음과 같다.

```math
c_t=\frac{1.5L_{*,t}+0.7(L_{p,t}+L_{b,t}-L_{*,t})}
{L_{p,t}+L_{b,t}}.
```

양면 하중이 같으면1.1이다. 분류 가능한 접촉이 없으면 중립 계수1이다. 기존 pad footprint 밖의 모서리·측면 접촉에는 선호 가산을 주지 않는다. 기존 Sweep의 접촉·높이·정렬 조건은 그대로이므로 계수만으로 무접촉 진행 보상이 새로 생기지 않는다.

## 보상·페널티 전체 구성

활성 term은15개다. 표의 weight는 코드의 설정값이다. 설명 식에서는 앞선 문서와 같이 시간 간격을 생략할 수 있지만, 실제 실행은 RewardManager가0.02초를 곱한다. 거리 증분 두 항과 사건형 `shelf_failure`는 함수 내부의 dt 나눗셈과 상쇄되므로 이 차이를 함께 기록한다.

| term | weight | 내용·상수 |
| --- | --- | --- |
| `sweep_progress` | +50 | 거리 감소량 × 누적 접촉 계수 × 힘 정렬 × 접촉면 계수; dt 상쇄 |
| `sweep_retreat` | -10 | 목표와의 XY 거리 증가량; dt 상쇄 |
| `reaching` | +0.8 | EEF–현재 타겟 bounds 중심 3D 거리, 10cm plateau·45cm cutoff |
| `arm_action_rate` | -0.03 | 원시 팔 명령의 스텝 간 차이 제곱합 |
| `hand_action_rate` | -0.03 | 원시 손6축 명령의 스텝 간 차이 제곱합 |
| `arm_joint_velocity` | -0.03 | 팔 실제 속도 제곱합, raw cost 상한100 |
| `hand_joint_velocity` | -0.01 | 손 실제 관절 속도 제곱합, raw cost 상한100 |
| `shelf_collision` | -0.5 | 기존 선반 접촉/간섭 비용 |
| `shelf_failure` | -3 | 선반 속도·손목 clearance의 기존 충돌 predicate 사건 비용; dt 상쇄 |
| `obstacle_contact` | -0.04 | 타겟 제외 장애물–손 합력의50N 초과 비용, raw cost 상한100 |
| `wrench_change` | -0.1 | 힘 크기 변화30N·모멘트 크기 변화3Nm 초과 비용 |
| `object_tilt` | -30 | 모든 활성 물체, 5°까지0·0.9rad에서 물체별 최대 비용 |
| `obstacle_displacement` | -150 | 활성 주변 물체의 초기 대비3D 변위 제곱합, 총 상한0.04 |
| `arm_action_limit` | -0.03 | 팔 실행 범위 초과량을 전체 폭π로 나눈 제곱평균 |
| `hand_action_limit` | -0.03 | 손 실행 범위 초과량을 각 URDF 상한으로 나눈 제곱평균 |

물체 현재 중심과 EEF 사이 거리 $
ho_t$에 대한 Reach 원점수는 다음과 같다.

```math
R_{\mathrm{reach},t}=\max\left(1-\frac{\max(\rho_t-0.10,0)}{0.35},0\right).
```

초기 거리 budget이나 episode 길이로 추가 조정하지 않는다. 실제 최대 Reach 기여는 weight0.8 ×0.02 =0.016/step이다. 목표 점유만으로 별도 Hold·접촉·성공 보너스를 지급하지 않는다. 압착·가속도·안정화 단계 보상도 비활성이다.

F/T 변화 비용은 `abs(norm(current)-norm(previous))`를 사용한다. 방향만 회전하고 크기가 같은 힘에는 변화 비용이 생기지 않는다. 허용값의2.5배에서 raw cost1로 포화하고 지수 sharpness는3이다. 첫 유효 샘플 및 reset 후 비교 샘플이 없는 경우에는 변화 비용을 적용하지 않는다. 양의 보상 누적량에 비례한 budget 제한은 사용하지 않는다.

근거: [보상 Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/stabilize_sweep.py), [거리·ActionLimit·Reach 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/stabilize_sweep.py), [장애물·F/T·물체 비용](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/contact_sweep_clutter_fusion.py).

## 고정 비용과 커리큘럼 제거

기준 환경의 활성 커리큘럼은 아래5개뿐이다. 새 환경의 `curriculum={}`로 모두 삭제하고 첫 스텝부터 다음 값을 사용한다.

| 설정 | 고정값 |
| --- | --- |
| `obstacle_free_force` / obstacle contact `free_force` | 50 N |
| `obstacle_weight` | -0.04 |
| `wrench_free_force_change` | 30 N |
| `wrench_free_moment_change` | 3 Nm |
| `wrench_weight` | -0.1 |

일정 갱신에 의해 나중에 값이 덮어써지지 않는다. 장애물 비용 cap·wrench 지수형 곡선/포화 비율·원시 액션 비용은 기준 환경과 같다.

## 관측 전용 F/T 정규화

물리 단위의 보상된 손목 신호를 $\mathbf{w}_t$, 기존 관측 noise를 $\boldsymbol{\epsilon}_t$라 한다. 축별 관측 한계는 $\mathbf{L}=(150,150,150,8,8,8)$이며, 앞3축은 N, 뒤3축은 Nm다.

```math
\mathbf{o}_{\mathrm{wrench},t}
=\frac{\mathrm{clip}(\mathbf{w}_t+\boldsymbol{\epsilon}_t,-\mathbf{L},\mathbf{L})}{\mathbf{L}}.
```

`PureWristWrench`를 교체하지 않고 `ObservationTermCfg.scale=(1/150,1/150,1/150,1/8,1/8,1/8)`을 사용한다. 실제 ObservationManager는 **물리값 복사 → 기존 noise → 축별 clip → scale** 순서로 처리한다. Actor와 Critic은 같은 policy 관측을 사용하므로 둘 다 이 무차원 값을 받는다.

F/T 변화량 페널티는 물리 callable을 직접 읽으며, ObservationManager의 clip·scale·noise를 거치지 않는다. 따라서 30 N/3 Nm 등의 임계값은 여전히 물리 단위에 적용된다. 접촉면 판정·접촉 하중·물리 제어에도 정규화 값을 사용하지 않는다.

직접 관측66D + 장애물64D, encoder16D, 본체 입력82D, action12D, 모델·PPO는 유지한다. 입력 차원이 같아도 F/T의 의미가 변경됐으므로 기존 정책의 입력 전처리와 호환된다고 간주하지 않는다. 정규화는 큰 입력에 대한 대응이며 모든 학습 발산을 방지한다는 보장은 검증하지 않았다.

## 종료 조건과 성공률

목표에 일찍 도달해도 즉시 성공 종료하지 않는다. 현재 구현은10초 timeout 시 실제 타겟 중심과 목표의 XY 거리가 **엄격히0.03m 미만**이고 같은 스텝에 물리 실패가 없으면 성공으로 판정한다. 정확히3cm는 성공이 아니다. 이는 현재 실행 코드의 비교 연산이며 이 문서 작업에서 변경하지 않았다.

조기 종료는 활성 물체 낙하·기울어짐(허용 기울기0.9rad), 기존 선반 실패 조건, 팔 관절 중 하나라도 절대 속도1rad/s를 초과하는 경우다. 속도 종료는 팔6관절 대상이며 손 관절 속도 종료를 추가하지 않는다.

`Metrics/timeout_success_rate`는 최근 완료 episode 최대10,000개의 ring에서 **성공 수 / timeout 수**를 계산한다. 조기 실패는 timeout 분모에 포함되지 않으므로 전체 episode 성공률과 구분해야 한다. 이 값만으로 손바닥·손등 선택 선호도를 확인할 수는 없다.

근거: [종료 Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations/stabilize_sweep.py), [성공 판정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/stabilize_sweep.py), [지표 집계](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/stabilize_sweep.py).

## 학습 설정

| PPO 설정 | 값 |
| --- | --- |
| rollout 길이 | 36 step/environment |
| 최대 iteration / 저장 간격 | 90,000 / 50 |
| epoch / mini-batch 수 | 8 / 4 |
| 초기 learning rate / schedule | 0.001 / adaptive |
| gamma / lambda | 0.98 / 0.95 |
| PPO clip | 0.2 |
| value loss coefficient | 1.0 |
| entropy coefficient | 0.005 |
| desired KL / gradient norm 상한 | 0.02 / 1.0 |

[학습 설정 코드](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/sweep_v0_ppo_cfg.py)를 사용한다. 보상 커리큘럼은 비어 있지만 공통 runner와 수치 보호 경계는 재사용한다. 일반 Actor 출력 자체를 유계화하거나 수치 보호 한도를 올리는 변경은 포함하지 않는다.

## 보존된 기준 구성과 실행

LinearReach weight0.8·10cm plateau·45cm cutoff, Sweep50/−10·count/20, Test 배치·단일 Warp IK·대표 표면점 관측·10초 episode·0.02초 정책 간격, 물성·장애물·ActionPenalty·종료·메트릭은 유지한다. Reach 실제 최대 step 기여는 기존 RewardManager의 dt 적용에 따라0.016이다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-v0 --num_envs 2048 --headless
```

실제 전체 설정 대조·CPU116개·RTX3090 GPU4환경 검증과 미검증 범위는 [개발 로그](../logs/2026-11-20_sweep_v0.md)에 기록했다. 개발 검증에서는 장기 학습 및 방향별 행동 선호도 개선을 측정하지 않았다. 현재 사용자 보고의 학습 진행과 정량 결과는 [계통 문서](SWEEP_FAMILY.md#현재-학습-현황)에 구분한다.

## Single Contact 파생 환경

`Inspire-Sweep-Single-Contact-v0`는 `Inspire-Sweep-v0`를 직접 상속한다. 로그 이름은 `inspire_sweep_single_contact_v0`다. EnvCfg는 `SweepSingleContactEnvCfg`, runtime은 `SweepSingleContactEnv`, PPO Cfg는 `SweepSingleContactPPORunnerCfg`이며 모두 기존 Sweep v0의 역할별 파일에 둔다.

최근3개 **정책 제어 스텝** 중 유효한 타겟 접촉이2회 이상이고 기존 높이 조건을 만족하면, 접촉 계수 $h_t$를 즉시1로 사용한다. 미인정이면0이다. 누적 증가·감소 카운트에 따른 점진적인 보상 증가는 없다.

```math
h_t=\begin{cases}
1,&\text{최근 3스텝 중 2회 이상 접촉 인정 및 기존 높이 조건 충족},\\
0,&\text{그 밖의 경우}.
\end{cases}
```

이 환경에는 `contact_count` 필드가 없다. 최근3스텝의 boolean 접촉 이력으로 `contact_recognized: bool`을 판정하며, 보상 계산에서만 `float(contact_recognized)`로1/0을 얻는다. 누적 증가·감소나0/20 대체 표현을 사용하지 않는다. 양의 Sweep 식의 다른 계수와 방향별 접촉면 계수는 유지한다. 인정 직후, 접촉 카운트가 이미20이었던 부모와 같은 최대 접촉 계수를 받는다.

현재 스텝의 실제 접촉·유효 데이터·수평 평균 힘1N 이상·힘 방향 정렬·타겟→목표 거리 유효성은 별도 기존 조건으로 남는다. 따라서 과거2회 접촉으로 이력 조건이 충족되어도 현재 힘 조건이 충족되지 않으면 양의 Sweep 보상은0이다. 높이는 기존처럼 EEF가 상판 위12cm **미만**이어야 한다.

부모 환경의 누적 방식은 그대로 보존한다. 자식의 역방향·Reach·접촉면 선호·고정 비용·정규화 F/T 관측·ActionPenalty·reset·종료·PPO 값은 보존한다. 자식의 전체 EnvCfg 값은 부모와 동일하며 runtime의 state 종류만 다르다. PPO에서는 로그 이름만 바뀐다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Single-Contact-v0 --num_envs 2048 --headless
```

[개발·검증 기록](../logs/2026-11-20_sweep_single_contact.md): CPU110개, GPU4환경 reset·8step·부분reset·추가1step·직접 이력 probe 통과. 이 결과는 개발 시점의 smoke 검사이며, 현재 사용자 보고로는 `.250`에서 학습 중이다. [현재 학습 현황](SWEEP_FAMILY.md#현재-학습-현황)을 참조한다.

## Single Contact v1

`Inspire-Sweep-Single-Contact-v1`는 Single Contact v0를 직접 상속한다. EnvCfg/runtime/state/PPO는 각각 기존 역할별 파일의 `SweepSingleContactV1EnvCfg`, `SweepSingleContactV1Env`, `SingleContactV1SweepState`, `SweepSingleContactV1PPORunnerCfg`다. 학습 로그 이름은 `inspire_sweep_single_contact_v1`이다. [확정 명세](../../01_plan/environments/2026-11-21_SINGLE_CONTACT_V1_SPEC.md)의 식과 부호·reset 계약을 구현했으며 부모는 보존했다.

| 변경 | 실제 동작 |
| --- | --- |
| Reaching | 현재 EEF에서 이동 접근점까지3D 거리의5cm 초과분 감소/증가에 대칭 보상/비용. weight4.9, 반환값은 거리 변화/policy dt |
| 접근점 | scaled local bounds의 직립XY 외접 원, 반경과 선반 기준 방향은 reset 때 고정. 물체 중심의 병진만 추종 |
| 구역 | 구역1/2/4는 초기 밀기 반대편. 구역3 전체는12시에서 시계방향+15° 단일점. 물체 회전 독립 |
| Sweep | 수평 힘 각도에30°/p4 signed 지수 함수. 기존 접촉/높이/1N gate 유지. 양수에만 면 계수1.5/0.7/중립1 적용, 음수는 배율1 |
| Joint 비용 | 기존 `arm_joint_velocity` 종료의 실제 boolean을 읽어 마지막 step에만−3. 기존1rad/s 초과 종료·속도L2 비용 유지 |
| 나머지 | 원래15개 보상 순서 보존, 새 비용을16번째로 추가. 관측66+64D·action12D·reset/물성·10초·성공 엄격히3cm 미만·모든 종료·빈 커리큘럼 유지. PPO는 로그 이름만 변경 |

기하와 초기 Reach 오차는 부모의 최종 배치·Command reset 뒤 저장한다. 부분 reset은 해당 행만 바꾸며 step cache로 중복 조회와 면 하중 중복 질의를 막는다. 부모 physics capture/step 루프를 복제하지 않는다. 거리별 혼합·감속·손끝 비용·주먹 강제·관측 GT 추가는 없다. 기존 Sweep50/−10 비대칭에 따른 왕복 이득 가능성은 보류된 문제로 남는다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Single-Contact-v1 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/check_sweep_single_contact_v1.py --headless
```

CPU196개와 GPU4환경 reset/11step/부분reset/팔 종료·정상 timeout 자동reset, `train.py`의16환경·36step rollout·PPO1회 업데이트를 통과했다. 부모 Cfg 전체와 비교해 요청한3개 보상 차이만 확인했다. [개발 로그·정확한 명령·한계](../logs/2026-11-21_single_contact_v1_implementation.md). 장기 학습이나 행동 개선의 검증 결과는 아니다.
