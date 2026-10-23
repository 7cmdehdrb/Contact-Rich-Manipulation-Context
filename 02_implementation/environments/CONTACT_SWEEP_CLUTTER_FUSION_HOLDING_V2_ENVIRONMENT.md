# Fusion Holding v2

2026-10-24 수치 안정성 변경: 상속하는 이전 action8D 관측은 raw action을 `[-1,1]`로 제한한 복사본이다. 보상용 raw action·실제 Action term 입력은 유지한다. 기존 checkpoint는 구조상 로드 가능하지만 범위 밖 관측의 의미가 달라지므로 원래 동작과 동등하다고 간주하지 않는다. [피드백 발산 재현·공통 PPO 방어·검증](../logs/2026-10-24_temp_training_stability.md).

[환경 안내](README.md) · [계열과 상속](FUSION_HOLDING_FAMILY.md) · [부모 Holding v1](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V1_ENVIRONMENT.md) · [개발·검증](../logs/2026-10-23_fusion_holding_v2.md)

기준일: 2026-10-23. 사용자 요청과 공통 반경 확인에 따라 목표 유지 보상·성공·접촉 간주 범위를 통일했다. 구현 계약이며 학습 성능 향상은 미검증이다.

## 등록과 상속

| 항목 | 값 |
| --- | --- |
| Task | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v2` |
| EnvCfg | `FusionHoldingV2EnvCfg`, 직접 부모 `FusionHoldingV1EnvCfg` |
| Runtime | `ContactSweepClutterFusionV1_0Env` |
| PPO | `FusionHoldingV2PPORunnerCfg`, 부모 `FusionHoldingV1PPORunnerCfg` |
| Runner / experiment | `CurriculumOnPolicyRunner` / `inspire_contact_sweep_clutter_fusion_holding_v2` |
| 파생 경로 | Holding-v1 → Holding-v2 → Holding-OSC-v2 → Holding-OSC-ObjectRandom-v1 |

관측·제어·Scene·reset은 Holding v1을 상속한다. Actor는 policy55D와 초기 장애물64D, Critic은 추가 현재 타겟XYZ3D를 사용한다. 원시119D/122D, 별도64→32→16 장애물 encoder 적용 후71D/74D다. 보상용 현재 타겟 정보는 Actor에 추가하지 않는다. Arm Joint Position6D+Hand2D, 프레임·scale·정책 주기·자산·물성·가림·초기 노이즈는 [부모 계약](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V1_ENVIRONMENT.md)을 따른다. Gray/White 각1→5, 최대10개 장애물과16슬롯 용량도 유지한다.

## 공통 목표 반경

| Learning iteration | 반경 |
| --- | --- |
| 0~5,000 | 0.02 m |
| 5,000~10,000 | 0.02 → 0.01 m, iteration마다 선형 감소 |
| 10,000~20,000 | 0.01 → 0.005 m, iteration마다 선형 감소 |
| 20,000 이후 | 0.005 m |

`goal_hold.params.position_tolerance`를 단일 기준으로 사용한다. 커리큘럼은 절대 iteration으로 재계산하며 checkpoint load·되감기에도 같은 값을 복원한다. 기존 `goal_position_scale` 일정은 제거하고 속도 척도 일정은 유지한다. 거리 판정은 월드 XY 원의 경계를 포함한다.

목표 유지 보상은 유효한 선반 위 상태이고 거리≤반경일 때 `exp(-ln(2) * ((거리/반경)^2 + (XYZ선속도/속도척도)^2))`다. 계수는2→4이며 RewardManager가 dt를 한 번 곱한다. 기존3배 cutoff는 새 함수에서 사용하지 않는다. 목표 정중앙·정지 상태의 최대 보상은4/초,3초 동안12다. 반경 안이라고 항상 최대 보상을 주지는 않는다.

성공은 같은 반경 안, XYZ 선속도≤0.01m/s, 기존 선반 위치·높이·기울기 유효성, 실패 없음 조건을 연속3초 유지할 때다. 속도·실패·유지 시간은 v1과 같다. 반경 축소 후 현재 위치가 범위를 벗어나면 누적 시간은 초기화된다. 성공 보너스는 추가하지 않는다.

## 손 접촉 보상

새 `hand_contact_or_goal`은 다음 두 조건의 OR을0/1로 반환한다. 계수1.45/초를 유지하고 중복 합산하지 않는다.

- 최신·유한 whole-hand 합력의 크기가0.01N 이상이면 실제 접촉으로 인정한다.
- 목표 유지 보상과 같은 유효 상태·거리 반경 안이면 접촉 없이도 인정한다. 성공 속도 조건과3초 유지는 요구하지 않는다.

`goal_contact_fade_width` 인수와 거리 감쇠 로직은 새 함수에 없다. 목표 내 접촉 간주는 센서 freshness와 무관하며, 촉각 관측을 조작하지 않는다. 보상용 상태 판정에만 사용한다. 실패 판정은 그대로 적용된다.

나머지 보상 구성, 충격 warmup·속도 일정·개수 일정·Goal deadzone, 네 raw 운동 페널티의 계수는 부모를 유지한다.

## 파생 환경 변경

OSC-v2는 EnvCfg와 PPO 모두 Holding-v2를 직접 상속한다. UR10 Reach 기반 RPY 입력, 위치/회전 stiffness80/25, scale0.03/0.15, effort 제한, 관성 분리·중력 보상false, Arm PD0은 유지한다.

ObjectRandom-v1은 EnvCfg와 PPO 모두 OSC-v2를 직접 상속한다. 전용 `ObjectRandomV1CurriculumCfg`는 Holding-v2 커리큘럼에서 개수 최종값만 Gray8/White8로 확장한다. 초기1/1에서 White3,000·Gray4,500부터 교대로 증가하며, NVIDIA 자산·reset·물성·16슬롯은 유지하며 새 목표 반경·보상·성공과 OSC-v2 제어를 전달한다. 기존 OSC-v1 기반 ObjectRandom 체크포인트는 입력 차원이 같아도 제어 의미가 달라 같은 동작을 보장하지 않는다.

## 실행

Workspace 루트의 Isaac Lab 환경에서 실행한다. 환경 수는 예시이며 처리량 검증값이 아니다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v2 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v1 --num_envs 256 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v2 \
  --num_envs 1 --checkpoint "<Holding-v2-checkpoint.pt>" --real-time
```

[환경 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/contact_sweep_clutter_fusion_holding_envs.py) · [목표·접촉 보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/contact_sweep_clutter_fusion_holding_scheduled.py) · [성공 판정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/contact_sweep_clutter_fusion_holding.py) · [공통 목표 반경](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/contact_sweep_clutter_fusion_holding.py) · [실제 검증과 미검증 범위](../logs/2026-10-23_fusion_holding_v2.md).
