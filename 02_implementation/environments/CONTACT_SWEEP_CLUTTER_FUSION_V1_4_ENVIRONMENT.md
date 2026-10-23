# Contact Sweep Clutter Fusion v1_4

[환경 안내](README.md) · [환경 계층](ENVIRONMENT_EVOLUTION.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-fusion-v1_4--2026-10-23) · [구현·검증 기록](../logs/2026-10-23_clutter_fusion_v1_4.md)

**기준일: 2026-10-23.** Task ID는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_4`다. 학습된 v1_0을 이어 보상과 페널티 허용 기준을 보정하는 환경이다. 아래는 현재 코드의 계약이며 성공률이나 학습 성능 향상이 검증되었다는 뜻은 아니다.

## 상속과 구성

[EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_4/env_cfg.py)의 `ContactSweepClutterFusionV1_4EnvCfg`는 [v1_0](CONTACT_SWEEP_CLUTTER_FUSION_V1_0_ENVIRONMENT.md)을 직접 상속한다. Reward·Termination·Curriculum CFG도 각각 v1_0의 해당 CFG를 상속하고 변경 항만 교체한다. v1_1–v1_3 계열의 선형 보간·접촉 fade 설정을 계승하지 않는다.

Runtime은 공용 `ContactSweepClutterFusionV1_0Env`, runner는 `CurriculumOnPolicyRunner`다. [PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_4/ppo_cfg.py)은 `ContactSweepClutterFusionV1_0PPORunnerCfg`를 직접 상속하며 experiment 이름만 `inspire_contact_sweep_clutter_fusion_v1_4`로 분리한다.

| 계약 | 최종 구성 |
| --- | --- |
| 관측 | v1_0의 policy 55D·초기 장애물 40D·privileged 3D 유지. Actor는 타겟 초기 위치를 사용하며 Critic용 현재 XYZ와 구분한다. |
| 행동·제어 | v1_0의 Joint Position Action 8D(Arm 6D + Hand 2D), 제어 주기 0.02초 유지 |
| Scene·reset | 타겟·목표 분포, 물성·센서·Event는 v1_0 계승. Gray/White capacity를 각각 5개로 확장하며 기존 10슬롯·40D 장애물 관측 구조 유지 |
| 장애물 수 | Gray 1·White 1 시작, 최종 Gray 5·White 5·Target 1. 개수 변경은 다음 reset에서 반영 |
| 성공 | 현재 Goal hold 반경 안에서 연속 3초 유지하면 종료. 기존 실패·timeout도 유지 |

## v1_0에서 바뀐 보상과 종료

[보상 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_4/rewards_cfg.py)은 Goal hold 가중치를 0.9→9.0, Hand contact를 0.29→1.45로 높인다. Goal 반경이 0이면 전용 `scheduled_goal_hold_xy`가 0을 반환하여 목표 체류 보상과 성공 판정을 비활성화한다. 양수이면 기존 월드 XY 거리 판정을 사용한다.

나머지 보상은 v1_0에서 상속한다. Reaching 30, Goal distance 100, Object −30, Shelf collision −0.5, Pushing speed −5, Arm speed excess −1, Shelf failure −3, EEF linear speed −1, Obstacle contact −1, Object acceleration −1, Wrench change −0.1을 유지한다. EEF orientation은 비활성이다. Hand contact fade width는 0, 장애물 접촉 free force는 2000 N이다. Wrench 비용의 입력은 힘·모멘트 **크기의 변화량**이며 절대 wrench 크기나 변화율로 바뀌지 않는다.

운동 페널티는 로컬 `mdp/goal_rewards.py`의 raw Action 변화량·실제 관절 속도 제곱합을 사용한다. Arm Action/Velocity −0.03/−0.03, Hand Action/Velocity −0.03/−0.01을 유지하며 각 비용 출력 상한은 100이다. 평균·정규화·보상 입력 Hand clamp를 추가하지 않는다.

[종료 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_4/terminations_cfg.py)의 `push_fast`는 0.8→1.0 m/s다. 부모 `__post_init__` 적용 후 v1_4에서 다시 1.0을 지정한다. [GoalHoldSuccess](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_4/mdp.py)는 실행 시점의 Goal hold 반경을 읽어 연속 150 제어 step을 검사한다. 목표 이탈·실패·해당 환경 reset 시 카운터를 초기화한다. `object_drop`, `push_fast`, `shelf_collision`, `hand_velocity`, `shelf_displacement`가 같은 step에 발생하면 성공을 억제한다. 성공은 timeout이 아닌 일반 termination이며 별도 속도·자세 성공 조건은 없다. 이는 GT 기반 학습 종료이며 실물 Blind 종료 검증과 구분한다.

## 커리큘럼

[CurriculumCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_4/curriculum_cfg.py)의 일정은 절대 learning iteration 기준이다. [staged_reward_threshold](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_4/curriculum.py)는 ramp를 250 iteration 간격으로 표본화하고 사이 값은 유지한다. 250 격자에 맞지 않는 종료점도 지정 iteration에서 정확히 적용한다.

| 항목 | 일정 |
| --- | --- |
| Arm free speed (rad/s) | 1.0 시작, 500에서 0.98, 이후 기울기 −0.02/200을 250 간격 적용, 3300에서 0.7 |
| EEF free speed (m/s) | 1.5 시작, 500에서 1.48, 이후 −0.02/200을 250 간격 적용, 13300에서 0.2 |
| Pushing free speed (m/s) | 0.1 시작, 500에서 0.09, 이후 −0.01/200을 250 간격 적용, 1900에서 0.02 |
| Object free acceleration (m/s²) | 10000 미만 100, 10000에서 50, 12000까지 유지, 이후 250 간격 감소하여 18000에서 10 |
| Wrench free force change (N) | 10000 미만 5000, 10000에서 200, 12000까지 유지, 이후 250 간격 감소하여 18000에서 100 |
| Wrench free moment change (N·m) | 10000 미만 500, 10000에서 30, 12000까지 유지, 이후 250 간격 감소하여 18000에서 20 |
| Goal hold 반경 (m) | 5000 미만 0, 5000에서 0.01, 이후 250 간격 감소하여 10000에서 0.005 |
| Goal deadzone | v1_0 계승: 30°를 3000까지 유지, 3500부터 500마다 5° 감소하여 6000에서 0° |
| 장애물 population | White는 3000부터 3000마다 1개 증가하여 12000에서 5개, Gray는 4500부터 3000마다 증가하여 13500에서 5개 |

가속도·wrench ramp의 첫 추가 감소는 12250이다. 큰 초기 허용 기준도 유한한 값이며 비용 제거를 뜻하지 않는다. Resume·rewind 시에는 저장된 절대 iteration으로 일정을 다시 계산한다.

## 실행과 검증 범위

Workspace 루트에서 v1_0 checkpoint를 이어 학습하는 명령이다. 경로 자리표시자는 실제 run과 checkpoint로 교체한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_4 \
  --num_envs 2048 --headless --resume \
  --load_run "<v1_0-run-절대경로>" --checkpoint "<model_ITER.pt>"

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_4 \
  --num_envs 1 --checkpoint "<checkpoint-절대경로.pt>"
```

Resume는 optimizer와 iteration을 복원한다. 예를 들어 iteration 16400에서 재개하면 Goal 반경 0.005 m·Gray 5/White 5 일정이 적용되며 커리큘럼을 0부터 시작하지 않는다. 관측·정책 구조는 v1_0 checkpoint를 이어받도록 유지되어 있으나 실제 checkpoint load 성공과는 구분한다.

[기존 구현 기록](../logs/2026-10-23_clutter_fusion_v1_4.md)은 CPU 47개 검사 통과와 Gray 5/White 5의 128개 장면 기하 인증을 보고한다. 당시 GPU driver 접근 실패로 실제 checkpoint load·PhysX·PPO rollout·장시간 학습·성공률 향상은 미검증이었다. 이번 문서 작업은 소스·상속 대조와 문서 검사만 수행했으며 학습·재생을 새로 실행하지 않았다. [문서화 검증 기록](../logs/2026-10-23_clutter_fusion_v1_4_documentation.md)에 기준 commit과 실제 검사 명령을 남긴다.
