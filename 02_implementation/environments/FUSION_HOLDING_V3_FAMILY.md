# Holding v3 · OSC v3 · ObjectRandom v2

[환경 안내](README.md) · [계열 운영 원칙](FUSION_HOLDING_FAMILY.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [개발·검증](../logs/2026-10-24_fusion_holding_v3.md)

기준일: 2026-10-24. 사용자 요청으로 goal hold 지급 시간을 제한하고, OSC 과업 비교와 Gray 스폰 영역 확장을 위한 세 환경을 추가했다. 정책의 목표 이탈 행동이 해소되었는지는 장기 학습으로 별도 검증한다.

## 등록과 상속

아래 환경명의 공통 접두사는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-`이다. Runtime은 모두 `inspire_sweep_baseline.runtime.contact_sweep_clutter_fusion:ContactSweepClutterFusionV1_0Env`, runner는 `CurriculumOnPolicyRunner`다.

| 환경명 | EnvCfg / 직접 부모 | PPO Cfg / experiment |
| --- | --- | --- |
| `Holding-v3` | `FusionHoldingV3EnvCfg` / `FusionHoldingV2EnvCfg` | `FusionHoldingV3PPORunnerCfg` / `inspire_contact_sweep_clutter_fusion_holding_v3` |
| `Holding-OSC-v3` | `FusionHoldingOSCV3EnvCfg` / `FusionHoldingV3EnvCfg` | `FusionHoldingOSCV3PPORunnerCfg` / `inspire_contact_sweep_clutter_fusion_holding_osc_v3` |
| `Holding-OSC-ObjectRandom-v2` | `FusionHoldingOSCObjectRandomV2EnvCfg` / `FusionHoldingOSCV3EnvCfg` | `FusionHoldingOSCObjectRandomV2PPORunnerCfg` / `inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v2` |

EnvCfg는 각 계열의 `envs/contact_sweep_clutter_fusion_holding*_envs.py`, PPO Cfg는 `agent/contact_sweep_clutter_fusion_holding*_ppo_cfg.py`에 있다. 같은 파일의 이전 버전 등록을 보존한다. 직접 상속은 Holding-v2 → Holding-v3 → OSC-v3 → ObjectRandom-v2다.

## Holding-v3: 에피소드별 지급 시간 상한

[Holding-v2](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V2_ENVIRONMENT.md)의 거리·속도 기반 `goal_settling`을 `CappedGoalSettling` Manager term으로 감싼다. 유효한 선반 위 상태, 공통 XY 목표 반경 안에서 양의 goal hold가 지급되는 제어 step마다 에피소드별 정수 카운트를 증가시킨다. 낮은 보상률이어도 같은 1 step을 소비한다. 보상 크기를 합산해 예산을 소모하는 방식이 아니다.

- 최대 지급 시간은 `max_hold_time=3.0`초다. 목표에서 벗어난 시간에는 카운트를 멈추며, 재진입해도 이전 카운트를 이어 간다.
- 시간 예산 소진 후에는 goal hold만 0이다. 부분 reset은 해당 환경의 카운트만, 전체 episode reset은 전체 카운트를 초기화한다.
- 기본 `step_dt=0.02`초에서는 최대 150 step을 지급한다. dt로 3초가 나누어떨어지지 않으면 마지막 지급 step의 비율만 줄여 실제 적분 시간이 3초를 넘지 않게 한다.
- 기존 거리·속도 shaping과 계수 4를 유지한다. RewardManager가 weight·dt를 한 번 적용한다. 정중앙·정지 상태에서 goal hold 총액은 최대 12다.
- 성공은 기존처럼 공통 반경·XYZ 속도 0.01 m/s 이하·실패 없음 조건을 연속 3초 유지하면 종료한다. 성공 timer와 지급 카운트는 독립적이다. 종료 판정 후 보상 계산 순서에서도 150번째 지급을 받는다.

공통 반경 2→1→0.5 cm 일정, goal distance, 목표 안 손 접촉 간주, 기타 보상·실패·timeout은 v2를 따른다. 손 접촉 간주에는 이번 시간 상한을 적용하지 않는다.

## OSC-v3: 현재 OSC-v2 제어 재사용

Holding-v3를 직접 상속하고 Arm만 OSC로 교체한다. `configure_reach_osc`에 기존 OSC-v2 설정 본문을 옮겨 두 버전이 함께 사용한다. 현재 코드 기준 위치/회전 stiffness는 100/50, damping ratio는 1, 상대 pose의 위치/회전 scale은 0.03/0.15다. RPY 입력, EEF offset, robot-base frame, effort 제한을 유지하며 관성 분리·중력 보상은 true다. Arm 관절 PD stiffness/damping은 0이다. 과거 문서의 80/25·false 표기는 현재 코드와 다르며, 이번 변경으로 제어 수치를 바꾸지 않았다.

## ObjectRandom-v2: 개수와 Gray 영역

ObjectRandom-v1의 원통 타겟, NVIDIA YCB 장애물 4종×크기 3단계, 1.5배 확대, yaw·질량·마찰 reset, OBB 비겹침·선반 검사와 초기 가림 관측을 재사용한다. **활성 개수 상한은 Gray6/White6**이다. 기존 물리 슬롯은8/8, 관측은16슬롯으로 유지하며 남는 슬롯을 비활성화한다. 7/7 반복 reset 검사의 첫 배치에서 실패하여 사용자 지정 분기에 따라6/6으로 낮췄다. [상한 선택·반복 검증 기록](../logs/2026-10-24_object_random_v2_population_cap.md). `ObjectRandomV2CurriculumCfg`가 다음 두 일정을 적용한다.

| iteration | Gray / White | Gray의 Red 방향 확장률 |
| --- | --- | --- |
| 0~2999 | 1 / 1 | 0% |
| 3000 | 1 / 2 | 0% |
| 4000 | 2 / 2 | 0% |
| 5000 | 2 / 3 | 0% |
| 6000 | 3 / 3 | 0%, 확장 시작점 |
| 6250 | 3 / 3 | 0.625% |
| 9000 | 4 / 5 | 7.5% |
| 11000 | 5 / 6 | 12.5% |
| 12000 이후 | 6 / 6, 이후 고정 | 15%, 이후 고정 |

White는 3000부터 2000마다, Gray는 4000부터 2000마다 한 개씩 추가하므로 전체적으로 1000마다 교대 증가한다. Gray 확장률은 6000~12000 사이에서 250 iteration마다 0.625%p씩 증가한다. 6000에서는 0, 첫 양의 값은 6250이다. 두 일정 모두 절대 learning iteration으로 계산해 resume·되감기에도 같은 값을 적용한다. 진행 중인 에피소드의 물체 위치·개수는 유지하고 다음 reset에 반영한다.

15%의 구현 해석은 **기존 Red 제외 반경 10.3 cm의 15%를 안쪽으로 허용**하는 것이다. 최대 패딩은 1.545 cm, Gray 중심의 새 제외 반경은 8.755 cm다. 원래 sweep 경로와 robot 쪽으로 연장된 wrist shadow에 대한 거리 함수를 그대로 사용하고, Gray와 rear Gray 후보의 내측 경계만 바꾼다. Red 면적을 15% 줄이는 의미는 아니다.

초기 구현의 실제2환경·seed42 검사에서는 초기 reset/step과 iteration6000·9000·12000·0의 reset을 통과했다. 당시 최대8/8에 도달한16000에서는200회 안에 비겹침 배치를 찾지 못했다. 이후7/7도 실패하여 현재 상한은6/6이다. **6/6·최대 패딩15%는 asset seed5개·100회 배치 reset·총400장면에서 실패0건**을 확인했다. 모든 장면에 대한 성공 보장은 아니며 [후속 반복 검증과 한계](../logs/2026-10-24_object_random_v2_population_cap.md)를 확인한다.

White 후보는 기존 Red·Gray 분류를 유지한다. Gray 외곽 반경 14 cm, rear 영역·최소 한 개 quota, 물체 간 간격·밀도·접근 경로 certificate·실제 OBB 비겹침과 선반 경계도 유지한다. 따라서 새로 허용한 영역 전체에 물체가 반드시 놓이는 것은 아니다. 로컬 `GrayPaddingLayoutGenerator`가 구역 판정을 확장하며 `src/scene_randomization`의 원본은 읽기 전용이다. 배치 실패 시 타겟·목표를 재추출하거나 개수를 줄이지 않는다.

## 공통 입력·페널티·실행

Actor는 policy 55D와 초기 장애물 64D, Critic은 현재 타겟 XYZ 3D를 추가해 raw 119D/122D다. 독립 64→32→16 장애물 encoder를 거치면 71D/74D다. Actor에 실행 중 타겟 GT를 추가하지 않는다. 행동은 Arm6D+Hand2D이며 Holding-v3는 Joint Position, 나머지는 위 OSC다. 정책 주기·자산 출처·좌표계·물성은 [Holding-v1 계약](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V1_ENVIRONMENT.md)과 [ObjectRandom-v1 계약](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V1_ENVIRONMENT.md)을 따른다.

네 운동 페널티는 로컬 `goal_rewards.action_rate_l2`·`joint_vel_l2`, Arm/Hand raw 제곱합과 실제 관절 속도, 가중치 −0.03/−0.03/−0.03/−0.01을 유지한다. 입력 정규화나 Hand 보상 clamp를 추가하지 않는다.

Workspace 루트에서 Isaac Lab Python, 선반 USD 접근 및 NVIDIA 물체 자산이 필요하다. 기본 Nucleus 선반 주소는 VPN 접근 조건을 확인한다. Windows 실행 예시는 다음과 같다. 환경 수는 처리량 검증값이 아니다.

```powershell
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v3 --num_envs 2048 --headless
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v3 --num_envs 2048 --headless
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v2 --num_envs 256 --headless
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/play.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v2 --num_envs 1 --checkpoint "<checkpoint.pt>"
```

[보상 구현](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/contact_sweep_clutter_fusion_holding_scheduled.py) · [Gray 배치 구현](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/contact_sweep_clutter_fusion_holding_osc_object_random_placement.py) · [커리큘럼 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/contact_sweep_clutter_fusion_holding_osc_object_random.py) · [실제 검증과 한계](../logs/2026-10-24_fusion_holding_v3.md).
