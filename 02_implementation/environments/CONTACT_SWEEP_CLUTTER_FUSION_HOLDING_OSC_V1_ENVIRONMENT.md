# Contact Sweep Clutter Fusion Holding OSC v1

[환경 안내](README.md) · [상속 관계](ENVIRONMENT_EVOLUTION.md) · [부모 Holding v1](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V1_ENVIRONMENT.md) · [개발·검증](../logs/2026-10-23_fusion_holding_v1.md)

기준일: 2026-10-23. `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v1`의 `FusionHoldingOSCV1EnvCfg`는 **`FusionHoldingV1EnvCfg`를 직접 상속**한다. OSC v0에서 같은 제어 구성을 재사용하며, OSC v0을 부모로 삼지 않는다.

## 제어와 상속 계약

Arm만 `OperationalSpaceControllerActionCfg`로 교체한다. Arm6D는 Robot Base 기준 상대 이동3D(m)·axis-angle 회전3D(rad)이고 position/orientation scale은 각각1.0이다. 현재 EEF pose에 base 축 상대 목표를 만들므로 EEF가 회전해도 base+X 명령은 base+X 방향이다. `task_frame_rel_path=None`, `target_types=["pose_rel"]`, fixed impedance·stiffness100·damping ratio1·관성 분리·중력 보상을 사용한다. Arm actuator의 관절 stiffness/damping은0이며 OSC의 effort와 경쟁하지 않게 한다.

이 설정은 [현행 OSC v0](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_V0_ENVIRONMENT.md)과 같다. Hand2D·EEF body offset·제어주기0.02초·물리주기0.01초를 유지하며 추가 명령 norm 제한은 없다. raw 이동1.0은1m 상대 목표라는 뜻이며 한 step의 실제 이동량이 아니다.

장애물16슬롯64D·encoder64→32→16D·원시 Actor119D/Critic122D와 압축 후71D/74D는 [Holding v1](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V1_ENVIRONMENT.md)을 상속한다. 최대Gray5/White5와 개수 curriculum, 보상·종료·물성·GT 경계도 유지한다. Runtime은 `ContactSweepClutterFusionV1_0Env`, PPO는 `FusionHoldingOSCV1PPORunnerCfg`, runner는 `CurriculumOnPolicyRunner`, experiment 이름은 `inspire_contact_sweep_clutter_fusion_holding_osc_v1`이다.

기존40D encoder checkpoint는 입력 구조가 다르며, Joint Position 또는 과거 EEF 기준 OSC checkpoint는 행동 의미도 다르다. 새 환경에서 학습을 시작한다. 직접 파생은 [OSC ObjectRandom v1](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V1_ENVIRONMENT.md)이다.

## 실행

Workspace 루트, Linux:

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v1 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v1 --num_envs 1 \
  --checkpoint "<Holding-OSC-v1-checkpoint.pt>" --real-time
```

Windows PowerShell에서는 `.\IsaacLab\isaaclab.bat -p .\src\inspire_sweep_baseline\scripts\train.py`와 같은 task/인수를 사용한다. 2048환경은 실행 예시다.

[환경 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_osc_v1/env_cfg.py) · [PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_osc_v1/ppo_cfg.py) · [실제 검증·미검증 범위](../logs/2026-10-23_fusion_holding_v1.md). 장시간 학습 안정성·수렴·실물 성능은 별도 평가 대상이다.
