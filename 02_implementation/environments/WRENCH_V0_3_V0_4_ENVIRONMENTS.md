# Inspire-Wrench-v0_3 · v0_4 환경

2026-11-05. 현재 v0_2 코드를 보존하는 직계 파생 두 환경이다. [부모 계약](WRENCH_V0_2_ENVIRONMENT.md) · [개발·검증 기록](../logs/2026-11-05_wrench_v0_3_v0_4_implementation.md).

## 등록·상속

| 항목 | v0_3 | v0_4 |
| --- | --- | --- |
| Gym ID | `Inspire-Wrench-v0_3` | `Inspire-Wrench-v0_4` |
| EnvCfg | `WrenchV0_3EnvCfg(WrenchV0_2EnvCfg)` | `WrenchV0_4EnvCfg(WrenchV0_3EnvCfg)` |
| Reward Cfg | `WrenchV0_3RewardsCfg(WrenchV0_2RewardsCfg)` | `WrenchV0_4RewardsCfg(WrenchV0_3RewardsCfg)` |
| Curriculum Cfg | `WrenchV0_3CurriculumCfg(WrenchV0_2CurriculumCfg)` | v0_3 그대로 |
| Runtime | `runtime.wrench:WrenchEnv` | 동일 |
| PPO | `WrenchV0_3PPORunnerCfg(WrenchV0_2PPORunnerCfg)` | `WrenchV0_4PPORunnerCfg(WrenchV0_3PPORunnerCfg)` |
| 실험명 | `inspire_wrench_v0_3` | `inspire_wrench_v0_4` |

설정은 기존 `envs/wrench_envs.py`, PPO는 `agent/wrench_ppo_cfg.py`, MDP 설정·함수는 각각 기존 역할의 `wrench.py`에 추가했다. 버전별 디렉터리나 별도 runtime은 만들지 않았다.

## v0_3 변경

| 항목 | v0_2 현재 코드 | v0_3 |
| --- | --- | --- |
| `obstacle_population` | 기준 개수 일정 + reset ±1 clamp | 비활성화, 매 reset Gray·White 각각 독립 정수 U{0,1,2,3,4} |
| `target_free_speed` | 0.1→0.02 일정 | 비활성화 |
| `target_speed_penalty.free_speed` | 초기 0.1m/s | 0.02m/s 고정 |
| EEF 높이 | 선반 기준 0.12m 미만 | 0.14m 미만 |
| `robot_action_rate_penalty` Arm | 정책 원시 6D 변화량 | OSC 최종 관절 토크 출력을 한도로 정규화한 6D 변화량 |
| `robot_action_rate_penalty` Hand | 기존 정규화 2D 행동 변화량 | 그대로 |
| `target_goal_first_entry_bonus.free_speed` | 0.01m/s | 0.04m/s |

`goal_reward_height_limit=0.14`이며 부모 초기화와 runtime이 `contact_height_limit`를 같은 값으로 맞춘다. 목표 거리·Hold·실제 접촉 표본의 기존 엄격한 `<` 조건을 유지한다. 정확히 14cm는 불인정이다. v0_2의 목표 내부 접촉 간주 예외는 그대로여서 XY 거리 3cm 미만에서는 높이와 무관하게 접촉 카운트를 인정한다. 최초 진입 및 성공 종료에는 새 높이 조건을 추가하지 않았다.

장애물 reset은 `reset_wrench_uniform_scene`에서 환경별 Gray·White 정수를 독립 추출하고 개수 쌍별로 기존 `reset_wrench_scene`에 전달한다. 부모의 Gray4/White5 물리 용량·10개 물체·비활성 주차와 중력 해제를 유지한다. 요청 개수는 두 색 모두 최대4지만 물리 객체를 줄이지 않는다. OBB 배치 실패 시 실제 배치 수는 요청보다 적을 수 있으며 기존 `Metrics/obstacle_actual_*`, `Metrics/layout_complete`를 확인한다.

방향 커리큘럼은 부모 그대로 30°에서 시작해 10000 iteration에 25°, 이후 3000마다 5°씩 줄어 25000부터 0°다. 각도7개 × 개수25쌍 = **175개 startup bank 단계**를 준비한다. v0_2의75개보다 생성량·저장량이 늘어난다. 단계당 환경별16개 후보, build batch256은 보존했다. 대규모 생성 시간·GPU 메모리는 미검증이다.

Arm 정규화는 실제 OSC 포화 처리와 동일한 한도를 사용한다.

```math
L_j=\max(\mathrm{joint\_effort\_limit}_j\,\mathrm{effort\_limit\_scale},\mathrm{minimum\_effort\_limit}),\qquad
u_{t,j}=\mathrm{clip}(\tau_{t,j}/L_j,-1,1).
```

```math
c_t=0.03\min\left(100,\sum_{j=1}^{6}(u_{t,j}-u_{t-1,j})^2\right)
    +0.03\min\left(100,\sum_{j=1}^{2}(a^{hand}_{t,j}-a^{hand}_{t-1,j})^2\right).
```

`WrenchV0_3ActionRatePenalty`가 제어 step의 마지막 물리 substep 출력 토크를 읽는다. 물리 substep 사이의 토크 변화량을 합산하지 않는다. 부분 reset은 해당 Arm 이력만0으로 초기화하며, 같은 제어 step 재호출은 상태를 전진시키지 않는다. Hand는 기존 `action_manager.action/prev_action`의 마지막2차원을 그대로 사용한다. weight−1, Arm/Hand 계수0.03, 그룹별 cap100, RewardManager의 dt 한 번 적용을 유지한다. 제어기·정책 액션 자체는 바꾸지 않았다.

최초 진입 보상은 기존 최대+25와 `speed_scale=0.02m/s`를 유지한다. 3D 속력4cm/s까지 무감쇠이며 초과분에 기존 Gaussian 감쇠를 적용한다. 최초 진입 기회 소진·재진입 중복 지급 방지 역시 부모 그대로다.

## v0_4 변경

v0_3에서 `target_goal_distance`의 callable과 params만 바꾼다. Holding v0~v4 및 대응 OSC·ObjectRandom 계열의 `DexPlanarGoalProgress`를 상속하는 `WrenchV0_4GoalProgress`를 사용한다. `position_tolerance=0.0`으로 목표 중심까지 개선량을 계산한다. 기존 weight **3.7**은 유지하며 Holding의 다른 계수는 가져오지 않았다.

```math
d_t=\|\mathbf{p}_{t,xy}-\mathbf{g}_{xy}\|,\quad
b_t=\min(d_0,d_1,\ldots,d_t),\quad
r_t=3.7\,(b_{t-1}-b_t)\,\mathbf{1}[h_{EEF,t}<0.14\,\mathrm{m}].
```

이는 미터 단위의 에피소드 최단 거리 개선량이다. 초기 거리로 정규화하지 않으며, 지수 근접도·cosine 계수·접촉 조건은 사용하지 않는다. 함수가 개선량을 `step_dt`로 나누고 RewardManager가 다시 곱하므로 최종 보상은 위 식과 같다. 정지·후퇴·기존 최단 거리까지 복귀에는 지급하지 않는다. reset 시 타겟 위치를 저장하고 첫 평가 때 새 goal을 사용하므로 첫 행동의 개선량을 포함한다. 부분 reset은 선택 환경만 초기화한다.

높이 조건은 지급에 적용하되 최단 거리 기록은 매 평가 갱신한다. 따라서 높이가14cm 이상일 때 달성한 개선량은 나중에 EEF를 낮춰도 지급하지 않는다. 이 규칙은 에피소드 전체 최단 거리라는 의미를 유지한다.

## 부모 보존과 로그

Scene·Command·Observation·Action·Termination·runtime·센서·물성·시간 설정·나머지 Reward와 PPO 수치를 보존한다. Actor121D/Critic124D, action8D, 정책 dt0.02초, 10초 에피소드, 성공 거리≤3cm·3D 속력≤0.005m/s 연속3초 및 성공+75는 그대로다. v0_3/v0_4 모두 보상15항이고 커리큘럼은 방향1항만 활성이다. 두 삭제 항의 `Curriculum/*` 로그는 더 이상 생성되지 않는다. 기존 보상 로그 이름은 유지하고 새 PPO 실험명으로 구분한다.

**현재 코드 기준 주의:** 기준 commit의 v0_2 `target_contact.weight`는 **0.1**이다. 이전 인계·v0_2 설명의1.45는 현재 코드와 다르다. 이번 두 환경은 실제0.1을 그대로 상속하며 카운트 상한10, 기본 dt에서 최대 step당0.02다. 부모 수치를 변경하지 않았다.

## 실행·검증

workspace 루트에서 Isaac Lab Python을 사용한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-v0_3 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-v0_4 --num_envs 2048 --headless
```

CPU **103개 통과**: 실제 설정 decorator와 Manager term 기반 전체 부모/자식 설정 대조, 기존 환경 회귀, 균등 정수 추출·seed·부분reset, 175개 배치 bank 생성/샘플, 토크 범위·Hand·이력, 높이·속도 경계, 거리 개선량·dt·부분reset을 확인했다. GPU probe도 `--version v0_3` 또는 `v0_4`를 지원한다.

```bash
python src/inspire_sweep_baseline/tests/_wrench_probe.py --version v0_3 --num_envs 64 --headless --device cuda:0
python src/inspire_sweep_baseline/tests/_wrench_probe.py --version v0_4 --num_envs 64 --headless --device cuda:0
```

NVIDIA 드라이버 사용 불가로 실제 Isaac Sim 초기화·물리 rollout·PPO·학습·2048환경 성능은 미실행이다. 위 train/probe 명령은 실행 안내이며 성공 기록이 아니다.
