# Inspire-Wrench-v0_1 환경

2026-11-04. [Wrench-v0 전체 계약](WRENCH_V0_V1_ENVIRONMENT.md)을 직접 상속한 feasibility 환경이다. 접촉 유지와 각도 계수의 효과를 짧은 목표 거리에서 비교한다. [개발·검증 로그](../logs/2026-11-04_wrench_v0_1_implementation.md).

## 등록과 상속

| 항목 | 값 |
| --- | --- |
| Gym ID | `Inspire-Wrench-v0_1` |
| EnvCfg | `envs/wrench_envs.py:WrenchV0_1EnvCfg(WrenchEnvCfg)` |
| Runtime | 부모와 같은 `runtime/wrench.py:WrenchEnv` |
| Reward / Curriculum | `WrenchV0_1RewardsCfg(WrenchRewardsCfg)` / `WrenchV0_1CurriculumCfg(WrenchCurriculumCfg)` |
| PPO | `agent/wrench_ppo_cfg.py:WrenchV0_1PPORunnerCfg(WrenchPPORunnerCfg)` |
| experiment_name | `inspire_wrench_v0_1` |

v1/v2의 wrench 제어를 상속하지 않는다. v0의 pose OSC, Actor121D/Critic124D, 8D action, Scene와 센서, 10개 물리 객체, 물성·관측 noise·reset 수명, 종료와 PPO 수치를 유지한다.

## 부모와의 차이

| 항목 | v0 | v0_1 |
| --- | --- | --- |
| `target_contact` | weight1.45, 독립 보상 | `None`, 활성 term에서 제거 |
| `target_goal_distance` | 높이 제한 아래 지수 거리 보상 | 연속 접촉 AND 기존 높이 제한, 지수 거리 × 각도 계수 |
| 거리 보상 weight / scale | 3.7 / 0.05m | 유지 |
| `target_goal_direction_deadzone` | 30°에서 일정에 따라 감소 | 제거, reset의 제외 반각40° 고정 |
| 목표 거리 허용 범위 | 5–15cm | 4.0–7.5cm |
| 배치 bank 단계 | 각도·개수9조합 | 40°·개수4조합 |
| 학습 실험명 | `inspire_wrench_v0` | `inspire_wrench_v0_1` |

## 거리 보상

시작 타겟 위치는 reset 후 runtime이 저장한 `_initial_object_positions_w`에서 현재 target ID로 읽는다. 목표, 시작 위치, 현재 위치는 모두 world XY를 사용한다. 초기 관측 noise는 보상에 사용하지 않는다.

```math
d_t = \|\mathbf{p}_t-\mathbf{g}\|_2,\qquad
c_t = \mathbf{1}[\text{fresh finite target/hand force}\land\|\mathbf{F}_t\|_2\ge0.01\,\mathrm{N}]
```

```math
\alpha_t = \begin{cases}
1, & d_t < 0.03\,\mathrm{m},\\
\cos(\mathbf{p}_0-\mathbf{g},\mathbf{p}_t-\mathbf{g}), & d_t\ge0.03\,\mathrm{m}.
\end{cases}
```

```math
r_t = 3.7\,\Delta t\;\mathbf{1}[c_{t-1}\land c_t]\;\mathbf{1}[h_{\mathrm{EEF},t}<0.12\,\mathrm{m}]\;\alpha_t\exp(-d_t/0.05).
```

`Delta t`는 RewardManager의 기존 적분이다. 기본 제어 주기는0.02초다. `h_EEF`는 초기 선반 위치와 작업면1.05m 기준 높이다. 현재 높이 제한을 유지하며 이전 높이를 새로운 조건으로 추가하지 않는다. 접촉 트리거는 기존 `target_contact`와 같은 target/hand 필터 합력 norm을 사용하되 높이 판정과 구분한다. 접촉 센서는 접선 마찰을 제외한 normal contact vector를 합산한다. 다른 물체·선반 접촉은 이 트리거를 만족시키지 않는다.

코사인은 원래 정의의 부호를 보존한다. 3cm 이상에서 목표 반대편으로 넘어가면 음수가 될 수 있다. 사용자 후속 지시에 따라 **3cm 미만에서는 방향과 무관하게1**이며 정확히3cm는 코사인을 사용한다. 목표점에서 현재 벡터가0이어도1이다. 3cm 바깥의 영벡터는 PyTorch cosine의 epsilon 처리에 따라0이며, 비유한 보상은0으로 처리한다.

부모의 거리 근접도 식을 유지한다. 따라서 거리 감소량이나 `d_t < d_(t-1)` 조건을 새로 추가하지 않는다. 가까울수록 지수 보상이 커지며, 정지 상태도 접촉·높이·각도 조건이 맞으면 보상을 받을 수 있다.

첫 접촉 표본은 보상이0이고 다음 제어 step도 접촉 중이면 지급한다. 접촉 단절·stale/nonfinite force는 이력을 끊는다. 동일 step의 중복 호출은 이력을 전진시키지 않는다. 부분 reset은 해당 환경의 이력과 cached reward만 초기화한다. 제어 step이 건너뛰면 접촉 유지로 간주하지 않는다. 3cm 미만 alpha override도 접촉·높이 조건을 우회하지 않는다.

Hold, 최초 진입, 연속 정지 성공 보상은 부모 그대로다. 특히 성공은 거리≤3cm·3D 속력≤0.005m/s의 연속3초이며 이번 코사인 경계와 별개다.

## 목표 생성과 커리큘럼

40°는 기존 코드의 ±X축 방향 제외 반각이다. 허용 각도는40–140°와220–320°이며 목표 방향을40° 하나로 고정하는 뜻이 아니다.

거리 샘플러는 방향별 선반 여유까지의 ray를 최대 거리로 제한한다. **4.0–7.5cm 균등분포가 아니다.** 기존 알고리즘을 유지하면서 허용 하한5→4.0cm, 상한15→7.5cm를 변경한다. 중앙 spawn disk2cm, 물체 bounds와 edge clearance2cm는 보존한다. 충분한 여유가 있는 경우7.5cm가 선택된다. 사용자 후속 요청으로 초기 목표 반경3cm 안에서 시작하는 경우를 배제하도록 하한을2.5→4.0cm로 올렸다.

| iteration | 제외 반각 | Gray / White |
| --- | --- | --- |
| 0–9999 | 40° | 3 / 3 |
| 10000–11999 | 40° | 3 / 4 |
| 12000–13999 | 40° | 4 / 4 |
| 14000 이후 | 40° | 4 / 5 |

각 조합별16개 bank 후보를 startup에 생성하고 reset에서 선택한다. v0의9단계를 새 환경에 그대로 쓰면40° 단계가 없으므로, 자식 `events.layout_bank.params.stages`에4단계를 지정한다. 공유 초기화 함수와 목표 샘플러에 선택 인자를 추가했으며 기본값은 부모와 동일하다. 장애물 개수 및 target speed 커리큘럼은 그대로다.

활성 보상은15→14개다. `Episode_Reward/target_contact`와 `Curriculum/target_goal_direction_deadzone`은 사라지고 `Episode_Reward/target_goal_distance`는 이름을 유지한 채 의미가 변경된다. 나머지 보상·종료·metrics 이름은 유지한다.

## 실행과 검증

workspace 루트에서 `env_isaaclab` Python으로 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-v0_1 --num_envs 2048 --headless
```

CPU78개 통과. 접촉 임계값·연속 표본·부분 reset·중복 조회·거리·각도·3cm strict 경계·기존 높이·모든 population 단계 bank·부모 설정 보존을 검사했다. 기존 목표 샘플러도 작업 시작 시 코드와63개 seeded 조건×256개 샘플에서 정확히 동일했다. GPU가 없는 현재 환경에서는 실제 Isaac Sim 초기화·rollout·PPO·성공률 개선을 검증하지 않았다.

GPU 호스트용 실행기는 `v0_1` 옵션을 추가했으며 아직 실행하지 않았다.

```bash
python src/inspire_sweep_baseline/tests/_wrench_probe.py \
  --version v0_1 --headless --device cuda:0 --num_envs 64
```
