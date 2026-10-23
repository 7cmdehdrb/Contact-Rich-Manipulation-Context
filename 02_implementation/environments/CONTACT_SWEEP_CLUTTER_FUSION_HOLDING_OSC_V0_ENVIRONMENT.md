# Contact Sweep Clutter Fusion Holding OSC v0

[환경 안내](README.md) · [상속 관계](ENVIRONMENT_EVOLUTION.md) · [Holding v0 전체 계약](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V0_ENVIRONMENT.md) · [개발 기록](../logs/2026-10-23_fusion_holding_osc_v0.md)

기준일: 2026-10-23. 등록 ID는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v0`다. Holding v0을 직접 상속하고 Arm Controller만 Joint Position에서 OSC로 바꾼다. 후속 요청으로 명령 좌표계를 EEF에서 Robot Base로, stiffness를200에서100으로 변경했다. 변경·검증은 [Holding v1 계열 개발 기록](../logs/2026-10-23_fusion_holding_v1.md)을 따른다. 참조 `Isaac-Inspire-Sweep-Omni-Renewal-OSC-v0`의 보상·종료·장면은 가져오지 않는다.

## 상속과 실행 클래스

```mermaid
flowchart TD
    V["Fusion v1_0"] --> H["Fusion Holding v0"]
    H --> O["Fusion Holding OSC v0"]
    R["Omni Renewal OSC v0"] -. "Arm OSC 설정만 참조" .-> O
```

`FusionHoldingOSCV0EnvCfg`는 `FusionHoldingV0EnvCfg`를 직접 상속하고 부모 초기화를 완료한 뒤 Arm action과 Arm actuator의 관절 PD gain만 변경한다. Runtime은 `ContactSweepClutterFusionV1_0Env`를 그대로 사용한다. PPO는 `FusionHoldingV0PPORunnerCfg`를 상속하며 experiment 이름만 `inspire_contact_sweep_clutter_fusion_holding_osc_v0`로 분리한다.

## Arm 제어 변경

| 항목 | Holding v0 | Holding OSC v0 |
| --- | --- | --- |
| Arm Action 6D | 기본 관절각 대비 위치 offset | 현재 EEF pose에 Robot Base 축 상대 명령 |
| Action term | JointPositionActionCfg | OperationalSpaceControllerActionCfg |
| 명령 변환 | 기본각 + 0.5 × raw action | 이동 3D ×1.0, 회전벡터 3D ×1.0 |
| 물리 제어 출력 | 관절 위치 목표 | OSC 계산 관절 effort |
| Arm 관절 PD | 부모 설정 | stiffness=0, damping=0 |
| Hand Action 2D | 열림·엄지 대립 | 동일 |

OSC는 `target_types=["pose_rel"]`, `impedance_mode="fixed"`, `motion_stiffness_task=100.0`, `motion_damping_ratio_task=1.0`, `inertial_dynamics_decoupling=True`, `gravity_compensation=True`다. 제어 body와 offset은 기존 `scene.ee_frame.target_frames[0]`에서 가져오므로 Holding의 EEF 기준점을 유지한다.

Arm 0~2번 출력은 상대 이동(m), 3~5번은 axis-angle 회전벡터(rad)다. `task_frame_rel_path=None`으로 이동·회전벡터를 Robot Base 축으로 해석하고, 각 정책 step의 현재 EEF pose(body offset 포함)에 상대 목표를 만든다. EEF가 base 대비 Z축으로90° 회전해도 +X 이동 명령은 base+X 목표를 만든다. 물리 substep에서는 정해진 목표를 추종하며 다음 정책 명령에서 목표를 다시 계산한다. Hand는 기존6~7번 채널을 사용한다. 총 Action 차원은8D, 제어 주기는0.02초, 물리 주기는0.01초다.

참조 Renewal OSC v0과 동일하게 position/orientation scale은1.0이며 별도 명령 norm 제한을 추가하지 않는다. 다른 OSC v2의 bounded action이나5mm/0.025rad 제한을 가져오지 않았다. 예를 들어 이동 raw action0.001은1mm이고1.0은1m의 상대 목표다. 실제 EEF가 한 step에 그 거리를 이동한다는 뜻은 아니다. Gaussian raw action과 기존 raw Action 변화 제곱합 비용은 유지하므로, Arm Action의 차원은 같지만 정책 출력의 물리적 의미가 바뀐다.

## 유지하는 Holding 계약

보상·종료·커리큘럼·관측·Hand·물성·목표 분포는 [Holding 상세 문서](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V0_ENVIRONMENT.md)를 그대로 따른다. 특히 Hand contact weight1.45, push_fast1.0m/s, object 변위계수5.0, 최대Gray5/White5, 1000까지 충격weight0, 거리·속도 정착 보상, 0.5cm·0.01m/s·3초 성공을 유지한다. Actor95D/Critic98D, 실행 중 타겟GT의 Critic 전용 경계도 같다.

Joint Position용 checkpoint는 같은8D 출력이라도 OSC에서 의미가 다르므로 동일 정책 재생으로 간주하지 않는다. 아래 명령은 새 OSC 정책 학습을 시작한다. 장기 안정성·수렴·접촉 성능은 별도 평가 대상이다.

과거 EEF 기준 OSC checkpoint 역시 Base 기준으로 명령 의미가 바뀌므로 같은 동작을 보장하지 않는다. 장애물16슬롯·64D encoder가 필요한 경우 [Holding OSC v1](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_V1_ENVIRONMENT.md)을 사용한다. OSC v0은40D 관측을 유지한다.

## 학습·재생

Windows PowerShell, Workspace 루트:

```powershell
.\IsaacLab\isaaclab.bat -p .\src\inspire_sweep_baseline\scripts\train.py `
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v0 `
  --num_envs 2048 --headless --max_iterations 90000
```

Linux, Workspace 루트:

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v0 \
  --num_envs 2048 --headless --max_iterations 90000
```

재생은 해당 OS launcher에서 `src/inspire_sweep_baseline/scripts/play.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v0 --num_envs 1 --checkpoint "<OSC-checkpoint.pt>" --real-time`을 사용한다. 학습 실행 정책에 따라 `train.py`를 사용하며 자동 복구 실행기는 사용하지 않는다.

Base 기준·stiffness100은 Holding OSC v0, 이를 상속하는 ObjectRandom v0 및 새 OSC v1 계열에 적용한다. 참조 Renewal OSC v0의 설정은 유지한다.

## 구현 근거

- [환경 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/contact_sweep_clutter_fusion_holding_osc_envs.py), [PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/contact_sweep_clutter_fusion_holding_osc_ppo_cfg.py).
- [참조 Renewal OSC](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_renewal_envs.py).
- [최초 구현 기록](../logs/2026-10-23_fusion_holding_osc_v0.md), [현재 Base 기준 제어·검증](../logs/2026-10-23_fusion_holding_v1.md).

직접 파생 환경: [Holding OSC ObjectRandom v0](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V0_ENVIRONMENT.md).
