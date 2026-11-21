# 독립 Sweep v0 환경

## 등록과 기준

Task ID는 **`Inspire-Sweep-v0`**, 로그 experiment name은 **`inspire_sweep_v0`**이다. 사용자가 지정한 `Inspire-Sweep-Only-v2-Test-ActionPenalty-LinearReach`의 최종 구성을 기능 기준으로 삼되, 후속 요청에 따라 긴 버전 이름을 이어 붙이지 않고 새 계통으로 선언했다.

- [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_v0_envs.py)의 `SweepEnvCfg`는 `ManagerBasedRLEnvCfg`를 직접 상속한다. 이전 task EnvCfg를 상속하지 않는다.
- [PPO](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/sweep_v0_ppo_cfg.py)의 `SweepPPORunnerCfg`는 `RslRlOnPolicyRunnerCfg`를 직접 상속한다. 기존 PPO와 값은 같고 experiment name만 다르다.
- [Runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/sweep_v0.py)의 `SweepEnv`는 기존 `SweepOnlyEnv`의 검증된 reset·step·접촉 샘플링·지표 수집을 재사용한다. 모든 물리 실행 코드를 복제한 환경은 아니다.
- Scene·Action·Observation·Command·Event·Reward·Termination의 공통 Cfg와 모델을 재사용하되, 새 EnvCfg에서 최종 구성을 명시한다. 기존 `envs/sweep_envs.py`는 과거 baseline이 사용하므로 덮어쓰지 않는다.

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

계수 $c_t$는 **양의 Sweep 진행 보상**에만 곱한다. $h_t$는 부모의 접촉 카운트 계수, $a_t$는 부모의 힘 방향 정렬 계수다. 거리 증분 보상은 실행 함수의 dt 나눗셈과 RewardManager의 dt 곱셈이 상쇄된다.

```math
r_{\mathrm{progress},t}
=50c_t h_t a_t\max(d_{t-1}-d_t,0),
\qquad
r_{\mathrm{retreat},t}=-10\max(d_t-d_{t-1},0).
```

접촉 카운트20·정렬1·1cm 전진이면 선호 접촉은0.75, 반대 접촉은0.35를 받는다. 역방향·Reach·나머지 비용에는 접촉면 계수를 곱하지 않는다.

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

## 보존된 기준 구성과 실행

LinearReach weight0.8·10cm plateau·45cm cutoff, Sweep50/−10·count/20, Test 배치·단일 Warp IK·대표 표면점 관측·10초 episode·0.02초 정책 간격, 물성·장애물·ActionPenalty·종료·메트릭은 유지한다. Reach 실제 최대 step 기여는 기존 RewardManager의 dt 적용에 따라0.016이다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-v0 --num_envs 2048 --headless
```

실제 전체 설정 대조·CPU116개·RTX3090 GPU4환경 검증과 미검증 범위는 [개발 로그](../logs/2026-11-20_sweep_v0.md)에 기록했다. 장기 학습 및 방향별 행동 선호도 개선은 측정하지 않았다.

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

[개발·검증 기록](../logs/2026-11-20_sweep_single_contact.md): CPU110개, GPU4환경 reset·8step·부분reset·추가1step·직접 이력 probe 통과. 장기 학습은 실행하지 않았다.

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
