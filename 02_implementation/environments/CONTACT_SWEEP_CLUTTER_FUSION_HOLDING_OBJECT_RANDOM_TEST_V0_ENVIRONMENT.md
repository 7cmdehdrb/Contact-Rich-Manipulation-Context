# Holding ObjectRandom Test v0

[환경 안내](README.md) · [Holding 계열](FUSION_HOLDING_FAMILY.md) · [부모 Holding v2](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V2_ENVIRONMENT.md) · [물체 랜덤화 기준](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V1_ENVIRONMENT.md) · [개발·검증](../logs/2026-10-23_holding_object_random_test_v0.md)

기준일: 2026-10-23. OSC가 아직 불안정하므로 기존 Joint Position 제어로 복잡한 물체 환경의 학습 가능성을 분리 검증하려는 사용자 요청에 따른 테스트 환경이다. 환경 구현은 학습 가능성이나 성공률을 입증하지 않는다.

## 등록·상속·비교 조건

| 항목 | 설정 |
| --- | --- |
| Task ID | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-ObjectRandom-Test-v0` |
| EnvCfg | `FusionHoldingObjectRandomTestV0EnvCfg` |
| 직접 부모 | `FusionHoldingV2EnvCfg` |
| Runtime | `ContactSweepClutterFusionV1_0Env` |
| PPO / 직접 부모 | `FusionHoldingObjectRandomTestV0PPORunnerCfg` / `FusionHoldingV2PPORunnerCfg` |
| Runner | `CurriculumOnPolicyRunner` |
| Experiment | `inspire_contact_sweep_clutter_fusion_holding_object_random_test_v0` |

OSC 환경을 상속한 뒤 제어를 되돌리는 방식이 아니다. Holding-v2를 직접 상속하여 Joint Position 액션과 Arm actuator PD를 유지한다. 물체 구성만 OSC-ObjectRandom-v1의 `ObjectRandomV1SceneCfg`, `ObjectRandomEventsCfg`, `ObjectRandomV1CurriculumCfg`를 재사용한다. 이 설정 클래스의 import로 OSC EnvCfg의 post-init이 실행되지는 않는다.

## 제어와 입력

Arm은6D `JointPositionActionCfg`, scale0.5, `use_default_offset=True`다. 현재 EEF 상대 pose가 아니라 기본 관절 자세에 대한 관절 목표를 설정한다. Hand는 기존2D openness이며 총 Action8D다. Arm 관절 stiffness/damping은 Holding-v2의 값을 유지하고 OSC처럼0으로 만들지 않는다. 물리 dt0.01초·decimation2·제어 주기0.02초, episode 제한10초를 상속한다.

관측은 policy55D+초기 장애물64D, Critic만 추가 현재 타겟XYZ3D다. Actor/Critic 원시119D/122D, 별도64→32→16 장애물 encoder 적용 후71D/74D를 유지한다. 프레임·노이즈·GT 경계는 [Holding-v2 계약](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V2_ENVIRONMENT.md)을 따른다. OSC checkpoint와 입력 크기가 같아도 Action 의미가 달라 동일 정책으로 비교하지 않고 이 테스트 환경에서 새로 학습한다.

## 물체·보상·종료

OSC-ObjectRandom-v1과 같은 NVIDIA YCB 자산·크기 랜덤화·평평한 충돌 프록시·OBB 배치·reset 시 위치/yaw/질량/마찰·형상별 관성을 사용한다. 타겟은 기존 실린더다. 자산 경로·배치 제약·필요한 Isaac Lab 의존성은 [ObjectRandom-v1 계약](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V1_ENVIRONMENT.md)을 따른다.

용량은Gray8/White8, 관측16슬롯이다.0~2,999는1/1,3,000에White+1,4,500에Gray+1 이후1,500마다 교대 증가한다.21,000에7/8,22,500부터8/8이며 최대 타겟1+장애물16이다. 개수는 각 episode의 reset 때 적용한다.

보상·성공·실패·timeout은 Holding-v2와 같다. 공통 목표 반경2→1→0.5cm, goal_hold 계수4, 실제 접촉 또는 목표 내 접촉 간주, 성공 속도0.01m/s·연속3초를 유지한다. 네 raw 운동 페널티 계수와 나머지 커리큘럼도 유지한다. 따라서 OSC-ObjectRandom-v1과의 의도된 차이는 Arm Action/제어와 Arm 관절 PD다.

## 실행

Ubuntu workspace 루트에서 실행한다. 환경 수256은 예시이며 처리량 검증값은 아니다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-ObjectRandom-Test-v0 \
  --num_envs 256 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-ObjectRandom-Test-v0 \
  --num_envs 1 --checkpoint "<Joint-ObjectRandom-Test-checkpoint.pt>" --real-time
```

[환경 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_object_random_test_v0/env_cfg.py) · [PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_object_random_test_v0/ppo_cfg.py). 실제 학습 성과와 GPU 검증 범위는 [개발 로그](../logs/2026-10-23_holding_object_random_test_v0.md)에서 구분한다.
