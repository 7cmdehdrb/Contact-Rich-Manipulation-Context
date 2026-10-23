# Contact Sweep Clutter Fusion Holding v1

[환경 안내](README.md) · [상속 관계](ENVIRONMENT_EVOLUTION.md) · [부모 Holding v0](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V0_ENVIRONMENT.md) · [개발·검증](../logs/2026-10-23_fusion_holding_v1.md)

기준일: 2026-10-23. `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v1`은 Holding v0의 장애물 관측 용량을16개로 확장한다. `FusionHoldingV1EnvCfg`는 `FusionHoldingV0EnvCfg`를 직접 상속한다. 기존 Holding v0 등록과10슬롯40D 입력은 유지한다.

## 관측과 encoder

각 장애물 슬롯은 `[present, x, y, z]`다. 초기 가시성·위치 노이즈를 반영한 Robot Base 기준 위치와 present bit를 사용하고 episode 동안 고정한다. 부모의 가시 장애물 정렬·압축·인접 교환 규칙을 유지하며 미사용 슬롯은0으로 채운다.

| 구성 | Holding v0 | Holding v1 |
| --- | --- | --- |
| 장애물 관측 용량 | 10슬롯·40D | 16슬롯·64D |
| Actor/Critic 각각의 encoder | 40→32→16D | 64→32→16D |
| 원시 Actor 입력 | policy55D + 장애물40D =95D | policy55D + 장애물64D =119D |
| 원시 Critic 입력 | Actor 입력 + 현재 타겟XYZ3D =98D | Actor 입력 + 현재 타겟XYZ3D =122D |
| 압축 후 Actor/Critic MLP 입력 | 71D/74D | 71D/74D |

PPO의 Actor/Critic 모두16슬롯·hidden32·embedding16을 사용한다. encoder는 ReLU이고 이후 정책/value MLP·PPO hyperparameter는 부모 설정을 따른다. 실행 중 타겟GT는 Critic에만 제공하며 초기 장애물 관측을 현재 위치로 갱신하지 않는다. 첫 encoder layer 크기가 달라 v0 checkpoint를 그대로 resume할 수 없다.

## Scene·제어·보상

16은 관측 용량이며 실제 장애물 수는 부모의 Gray1→5/White1→5 curriculum을 유지한다. 최대 타겟1+장애물10개이며 관측의 남는6슬롯은0이다. 물성·장면·reset·초기 배치와 Arm Joint Position6D + Hand2D 제어는 [Holding v0 전체 계약](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V0_ENVIRONMENT.md)을 따른다.

거리·속도 정착 보상, 초기 충격 비용 warmup, 성공 조건0.5cm·0.01m/s·3초 및 모든 보상·종료·일정을 상속한다. 로컬 `goal_rewards.action_rate_l2`·`joint_vel_l2`의 raw 제곱합 네 항과 Arm−0.03/−0.03·Hand−0.03/−0.01 계수도 유지한다. Runtime은 `ContactSweepClutterFusionV1_0Env`이며 step/reset을 복제하지 않는다.

`FusionHoldingV1PPORunnerCfg`는 Holding v0 PPO에서 관측 용량과 experiment 이름 `inspire_contact_sweep_clutter_fusion_holding_v1`을 변경한다. runner는 `CurriculumOnPolicyRunner`다. 직접 파생 [OSC v1](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_V1_ENVIRONMENT.md)은 Arm 제어를 변경한다.

## 실행

Workspace 루트, Linux:

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v1 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v1 --num_envs 1 \
  --checkpoint "<Holding-v1-checkpoint.pt>" --real-time
```

Windows PowerShell에서는 launcher를 `.\IsaacLab\isaaclab.bat -p .\src\inspire_sweep_baseline\scripts\train.py`로 바꾸고 같은 task/인수를 사용한다. 2048환경은 실행 예시이며 처리량 검증값이 아니다. 새 관측 구조로 학습을 시작한다.

## 구현 근거와 검증 범위

[환경 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_v1/env_cfg.py) · [PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_v1/ppo_cfg.py).

실제 실행 명령·결과·미검증 범위는 [개발 로그](../logs/2026-10-23_fusion_holding_v1.md)에 기록한다. 용량 확대 자체가 학습 수렴·장애물 회피·실물 성능 개선을 입증하지 않는다.
