# Holding OSC ObjectRandom v1

[환경 안내](README.md) · [상속 관계](ENVIRONMENT_EVOLUTION.md) · [부모 OSC v1](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_V1_ENVIRONMENT.md) · [물체 랜덤화 원본](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V0_ENVIRONMENT.md) · [개발·검증](../logs/2026-10-23_fusion_holding_v1.md)

기준일: 2026-10-23. `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v1`의 `FusionHoldingOSCObjectRandomV1EnvCfg`는 **`FusionHoldingOSCV1EnvCfg`를 직접 상속**한다. ObjectRandom v0의 Scene·Event·물성·개수 설정을 재사용하며 EnvCfg의 부모는 ObjectRandom v0이 아니다.

## 관측·제어·물체

| 항목 | ObjectRandom v1 |
| --- | --- |
| 장애물 관측 | 16슬롯×4=64D, 실제 장애물14개와 남는2슬롯0 |
| encoder와 입력 | Actor/Critic 각각64→32→16D, raw119D/122D, 압축 후71D/74D |
| Arm / Hand | Robot Base 기준 상대 pose OSC6D·stiffness100 / 기존 Hand2D |
| 물체 수 | iteration0부터 타겟1+Gray7+White7=15개, 개수 curriculum 비활성 |
| 타겟 | 반경4cm·높이10cm 기존 실린더 |
| 장애물 | NVIDIA YCB4종×균일크기3단계, 환경 생성 시 종류·크기 무작위 선택 |
| 매 reset | 기존 rigid body의 위치·yaw·질량·마찰 갱신 |

관측 용량16은 실제 장애물16개를 뜻하지 않는다. 가림·초기 위치 노이즈·정렬·인접 교환과 실행 중 타겟GT의 Critic 전용 경계는 부모를 따른다. ObjectRandom v0의14슬롯56D encoder checkpoint는 v1의64D encoder와 직접 호환되지 않는다.

기존1.5배 확대 비율, 상방 교정, 평평한 상자·32각 원통 충돌 프록시, OBB 비겹침·선반 경계 검사, 형상별 관성, `replicate_physics=False`를 재사용한다. NVIDIA 자산은 첫 Scene 생성 시 읽으며 reset마다 새로 생성하지 않는다. 세부 질량·마찰·배치·자산 경로는 [ObjectRandom v0 상세 계약](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V0_ENVIRONMENT.md)을 따른다. 초기 자산 접근과 대규모 메모리·처리량 조건도 같다.

Holding의 보상·성공·실패·timeout·나머지 curriculum과 네 운동 페널티 계수는 부모 OSC v1을 따른다. Runtime은 `ContactSweepClutterFusionV1_0Env`, PPO는 `FusionHoldingOSCObjectRandomV1PPORunnerCfg`, runner는 `CurriculumOnPolicyRunner`, experiment 이름은 `inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v1`이다.

## 실행

Workspace 루트, Linux:

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v1 \
  --num_envs 256 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v1 \
  --num_envs 1 --checkpoint "<ObjectRandom-v1-checkpoint.pt>" --real-time
```

Windows PowerShell에서는 `.\IsaacLab\isaaclab.bat -p .\src\inspire_sweep_baseline\scripts\train.py`와 같은 task/인수를 사용한다. 256환경은 실행 예시이며 해당 규모 처리량을 검증한 수치가 아니다.

[환경 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_osc_object_random_v1/env_cfg.py) · [PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_osc_object_random_v1/ppo_cfg.py) · [실제 검증·미검증 범위](../logs/2026-10-23_fusion_holding_v1.md). 기존 v0의 물체 안정화 시험은 당시 조건의 결과이며 새 v1 장기 학습·실물 성능을 입증하지 않는다.
