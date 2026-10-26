# Isaac-Inspire-Final-v0

기준일: 2026-10-26. [환경 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [구현·검증 로그](../logs/2026-10-26_final_v0.md)

## 목적과 독립 구성

사용자 요청에 따라 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v3`의 현재 설정과 동작을 유지하면서 기존 task의 상속을 끊었다. 새 ID는 `Isaac-Inspire-Final-v0`다. 기존 환경 CFG를 생성·복사하거나 부모의 `__post_init__`를 호출하지 않는다. 이후 원본 CFG의 변경은 Final에 자동으로 전파되지 않는다. 공유 계산 함수·stateful term 구현의 변경은 양쪽에 적용된다.

| 책임 | 새 클래스와 직접 기반 |
| --- | --- |
| 환경 조합 | `FinalEnvCfg(ManagerBasedRLEnvCfg)` |
| 실행 lifecycle | `FinalEnv(ManagerBasedRLEnv)` |
| 장면 | `FinalSceneCfg(InteractiveSceneCfg)` |
| Manager CFG | `FinalObservationsCfg`, `FinalActionsCfg`, `FinalCommandsCfg`, `FinalRewardsCfg`, `FinalTerminationsCfg`, `FinalEventsCfg`, `FinalCurriculumCfg`: 기존 task CFG 상속 없음 |
| 개별 Action·Command CFG | `FinalOSCActionCfg`, `FinalHandActionCfg`, `FinalGoalCommandCfg`: Isaac Lab term CFG 직접 상속 |
| 학습 CFG | `FinalPPORunnerCfg(RslRlOnPolicyRunnerCfg)`, `FinalModelCfg(RslRlMLPModelCfg)` |

[EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/final_envs.py)가 역할별 `mdp/*/final.py`와 `assets/scenes/final.py`를 조합한다. [runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/final.py)은 기존 lifecycle 순서를 독립적으로 선언한다. [PPO](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/final_ppo_cfg.py)는 기존 `CurriculumOnPolicyRunner`와 `ContactSweepClutterFusionModel` 실행 구현을 사용한다. 공통 로봇·물성 spawner와 자산 생성 함수도 재사용한다. 환경 CFG 상속 제거와 Isaac Lab 기반 클래스·공통 계산 구성요소 재사용을 구분한다.

## 보존한 계약

세부 물리·보상 해석은 [기준 ObjectRandom-v3](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V3_ENVIRONMENT.md)와 [v4 공통 보상](FUSION_HOLDING_V4_FAMILY.md)을 따른다. Final 선언의 기준은 이번 작업 시작 시 코드다.

- 관측: policy 55D, 초기 장애물 16슬롯·64D, critic 전용 현재 타겟 3D. Actor/Critic raw 입력 119D/122D, 독립 장애물 encoder 64→32→16 이후 71D/74D. term 순서와 초기 관측 노이즈를 유지한다.
- 제어: Arm 상대 OSC 6D + Hand openness 2D. 위치/회전 scale 0.03/0.15, stiffness 100/50, damping ratio 1, 관성 분리·중력 보상, effort 제한과 Arm PD 0을 유지한다.
- 시간: sim dt 0.01초, decimation 2, 정책 50Hz, episode 10초. 기본 4096환경·간격 2.5m와 PhysX 설정을 유지한다.
- 장면·reset: 타겟 실린더, NVIDIA YCB 4종×3크기, 기존 물성·가림·배치 함수를 사용한다. 물리 용량 Gray8/White8·관측16슬롯, 활성1/1→6/6, Gray 패딩 일정도 같다. Hydra override 후 runtime에서 용량을 다시 구성한다.
- 보상: 새 최단 Goal Distance×100, Reaching×30, 중심 강화·지급 시간 상한 없는 Goal Hold weight4와 d≤2r 지급, Contact weight1.45, 기존 비용과 커리큘럼을 유지한다. Arm/Hand raw action 변화·실제 관절 속도 네 페널티와 계수 −0.03/−0.03/−0.03/−0.01을 보존한다.
- 종료: success term 없음. drop·과속·선반 충돌·Arm 속도·선반 변위 실패와 timeout을 유지한다.
- PPO: 모델 구조·optimizer·학습 일정·관측 그룹은 같다. 식별용 experiment 이름만 `inspire_final_v0`로 분리한다. 기존 학습 로그는 수정하지 않는다.

## 실행

Workspace 루트에서 실행한다. Isaac Lab Python, 동작하는 NVIDIA 드라이버, 로봇·선반 USD 및 NVIDIA YCB 자산 접근이 필요하다. 선반 경로는 기존 `INSPIRE_SWEEP_SHELF_USD_PATH` 규칙을 유지한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Final-v0 --num_envs 256 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Final-v0 --num_envs 1 \
  --checkpoint "<checkpoint.pt>" --real-time
```

Windows에서는 `./IsaacLab/isaaclab.sh`를 `.\IsaacLab\isaaclab.bat`로 바꾸고 명령을 한 줄로 실행한다. 실행기 기본 task는 변경하지 않았다.

## 검증 경계

CPU에서 실제 CFG 선언과 공식 configclass를 실행하여 Manager 값·term 순서·callable, 관측, 장면 재구성, PPO, lifecycle을 비교했다. 자산·simulator 객체 일부는 CPU 대역이며 실제 USD 생성·접촉 물리를 검증한 것은 아니다. Isaac Sim launcher는 NVIDIA 드라이버 미로딩·CUDA 장치 없음으로 검사 본문 전에 종료했다. 실제 import 전체 비교·reset/step·학습·기존 checkpoint 재생은 미검증이다. 정확한 명령과 결과는 [개발 로그](../logs/2026-10-26_final_v0.md)에 기록한다.
