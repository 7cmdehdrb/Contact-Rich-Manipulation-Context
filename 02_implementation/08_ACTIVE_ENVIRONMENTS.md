# 활성 환경의 상속·등록·실행

[문서 안내](../docs/README.md) · [Omni v2 개발 로그](../docs/logs/2026-10-15_omni_v2_rewards.md) · [Baseline 패키지 안내](../../../src/inspire_sweep_baseline/README.md)

기준일: 2026-10-15. 현재 체크아웃에서 확인한 활성 Baseline 계열을 기록한다. 이번 작업의 구현·검증 범위는 Omni v2 보상과 기존 환경의 회귀 검사이며, 학습 성능 검증은 수행하지 않았다. Axia80 실행은 [패키지 안내](../../../src/axia80_feasibility/README.md)를 따른다.

## 상속과 등록

모든 아래 Gym 환경의 entry point는 `inspire_sweep_baseline.env:InspireSweepEnv`다. 등록은 [패키지 초기화](../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py), Omni 설정은 [omni_env_cfg.py](../../../src/inspire_sweep_baseline/inspire_sweep_baseline/omni_env_cfg.py)에 있다.

| 환경 ID | 설정 클래스 | 부모 설정 |
| --- | --- | --- |
| `Isaac-Inspire-Sweep-Baseline-v0` | `InspireSweepEnvCfg` | Isaac Lab `ManagerBasedRLEnvCfg` |
| `Isaac-Inspire-Sweep-Omni-v0` | `InspireSweepOmniEnvCfg` | `InspireSweepEnvCfg` |
| `Isaac-Inspire-Sweep-Omni-v1` | `InspireSweepOmniV1EnvCfg` | `InspireSweepOmniEnvCfg` |
| `Isaac-Inspire-Sweep-Omni-v2` | `InspireSweepOmniV2EnvCfg` | `InspireSweepOmniV1EnvCfg` |

Omni v1의 현재 Arm 속도 종료 임계값은 3 rad/s이며 v2가 그대로 상속한다. v2는 `OmniV2RewardsCfg`를 사용하고, v0/v1의 보상 설정과 상태는 공유하여 수정하지 않는다. 물체 spawn 반경 2cm, 최대 목표 이동 15cm, live-object 41D 관측, Arm 6 + Hand 2 action, 50Hz 제어와 10초 제한을 상속한다. 목표는 episode 동안 고정된다. 목표 방향은 선반 평면 전방향이며 가장자리 여유에 따라 이동 거리가 짧아질 수 있다.

Runner는 네 환경 모두 `InspireSweepPPORunnerCfg`다. v2의 변경 범위는 보상이며, PPO·행동 분포·controller 설정은 그대로다. v2 로그를 분리하려면 아래 experiment 이름을 지정한다.

## v2 보상 계약

현재 EEF 위치를 `e_t`, 현재 물체 바닥 중심을 `p_t`, reset 거리를 `D_0`라고 할 때:

```math
D_t = \max(\|e_t-p_t\|_2-0.10,0)
```

```math
B_t = \min(B_{t-1},D_t), \qquad R_{\mathrm{reach},t}=200\frac{B_{t-1}-B_t}{\max(D_0,10^{-6})}
```

`B_0=D_0`이다. 누적 최대 +200이며 초기에 이미 10cm 이내이면 접근 보상 budget은 0이다. 물체와 EEF가 같은 거리를 유지하거나 후퇴 후 이전 기록까지만 돌아오면 지급하지 않는다. 물체가 손 쪽으로 접근해도 상대 거리 감소로 기록된다.

목표 `g`까지 초기 XY 거리를 `L_0`, 현재 거리를 `L_t`라고 할 때:

```math
Q_t=\min\left(1,\max\left(0,\frac{L_0-L_t}{\max(L_0-0.01,10^{-6})}\right)\right)
```

```math
H_t=\max(H_{t-1},Q_t), \qquad R_{\mathrm{sweep},t}=400(H_t-H_{t-1})
```

`H_0=0`이며 초기에 목표 허용 오차 안이면 보상을 지급하지 않는다. `L_0`는 reward reset 때 저장한 물체 위치와 새 episode의 목표로 계산해 command reset 순서의 영향을 피하고 첫 transition의 이동도 반영한다. 두 progress 함수는 정규화한 진전 증가량을 `step_dt`로 나눠 반환한다. RewardManager의 `weight * step_dt` 적용 후 위 지급 식이 된다.

Reaching +200과 Sweeping +400은 실험 기본값이다. 접촉 전 접근에 양의 신호를 주고, 접근 이후에는 물체 목표 진전으로 추가 보상을 얻도록 설계했다. 행동 변화·관절 속도 비용은 v1과 동일하게 상속하며 변경하지 않는다. 자세한 계수는 [패키지 안내](../../../src/inspire_sweep_baseline/README.md#omni-v2-현재-물체-접근과-목표-이동-진전)를 따른다. `time`, `success`, `failure` 보상은 `None`이다. 후속 사용자 요청에 따라 v2는 `terminations.success=None`으로 성공 종료도 제거한다. 목표 도달 후에도 계속 실행하며 실패·시간 초과 종료 조건은 유지한다. v0/v1의 성공 종료는 유지한다.

## 실행과 검증

Workspace 루트에서 실행한다. 접근 가능한 선반 USD와 Isaac Lab 실행 환경이 필요하다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Sweep-Omni-v2 --num_envs 2048 \
  --experiment_name inspire_sweep_omni_v2 \
  --run_name live_reach200_sweep400 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Sweep-Omni-v2 --num_envs 1 \
  --experiment_name inspire_sweep_omni_v2 \
  --checkpoint "<v2-checkpoint.pt>" --real-time
```

`--sweep-direction`은 지정하지 않는다. CPU 검증 명령·결과·미검증 범위는 [개발 로그](../docs/logs/2026-10-15_omni_v2_rewards.md)에 남긴다. 보상 수치, 학습 수렴, 실물 안전성은 별개 검증 대상이다.
