# Revision-v2 / Revision-Test-v2 환경

2026-11-03 구현. [변경 명세](../../01_plan/environments/2026-11-03_REVISION_V2_SPEC.md) · [개발·검증 기록](../logs/2026-11-03_revision_v2_implementation.md) · [부모 v1 전체 계약](REVISION_V1_ENVIRONMENT.md)

## 등록과 상속

| Gym ID | EnvCfg 직접 부모 | PPO experiment_name |
| --- | --- | --- |
| `Isaac-Inspire-Revision-v2` | `RevisionV2EnvCfg(RevisionV1EnvCfg)` | `inspire_revision_v2` |
| `Isaac-Inspire-Revision-Test-v2` | `RevisionV2TestEnvCfg(RevisionV2EnvCfg)` | `inspire_revision_test_v2` |

두 환경은 기존 `runtime/revision.py:RevisionEnv`를 사용한다. Test는 타겟 슬롯 하나의 형상만 cylinder로 고정한다. 타겟 1개·장애물 후보 9개, 크기 랜덤화와 장애물 난수열은 유지한다. Test-v1의 임시 높이 출력·시각화 면은 포함하지 않는다.

## v1 대비 변경 계약

낮은 EEF 자세에서 목표 접근·체류·접촉을 보상하고, 감속한 최초 진입과 최종 배치 성공을 유도한다. 아래 항목 외 환경·학습 설정은 v1에서 상속한다.

| 항목 | 최종 v2 동작 |
| --- | --- |
| `target_goal_distance` | weight 3.7, 기존 `exp(-d/0.05)` × 현재 EEF 높이 < 0.095m |
| `target_goal_hold` | weight 10, 2.5~3.5cm Smoothstep × 기존 물리 유효성 × 현재 EEF 높이 < 0.095m. 속도 감쇠 없음 |
| `target_contact` | weight 1.45, 기존 최신·유한 실제 타겟 접촉 force norm ≥ 0.01N AND EEF 높이 < 0.095m |
| `target_goal_first_entry_bonus` | strict d < 0.03m 최초 표본에 최대 +25 × 속도 Gaussian 감쇠. 높이 조건 없음 |
| `target_goal_timeout_bonus` | 기존 timeout AND d ≤ 0.03m 조건에 +75. 높이·속도 조건 없음 |
| `object_acceleration_penalty` | free_acceleration 20→15m/s². weight −0.05·물체별 cap 100·기존 함수 유지 |

EEF는 `ee_frame.data.target_pos_w[:, 0, 2]`, 작업면은 `env._revision_initial_shelf_pos[:, 2] + 1.05`다. `RevisionV2EnvCfg.goal_reward_height_limit = 0.095`가 거리·Hold·접촉의 공통 기준이다. 부모 post-init 이후 `contact_height_limit`을 동기화한다. 세 항 모두 strict `<`이며 95mm 경계에서는 미지급한다. 제어 범위를 강제로 제한하는 설정은 아니다.

Hold는 d ≤ 0.025m에서 1, d ≥ 0.035m에서 0이며 중간에서는 u=(d−0.025)/0.01을 사용한 `1−3u²+2u³`다. 기존 `target_measurements`의 물리 유효성·속도 유한성 검사를 유지한다. 유한한 속력 크기는 Hold 값에 영향을 주지 않는다. step_dt=0.02s에서 최대 step 보상은 0.20, d=0.03m에서는 0.10이다. 성공 반경 3cm와 Hold 외곽 반경은 독립적이다.

최초 진입 감쇠는 `exp(-(max(v−0.01,0)/0.02)²)`이며 v는 현재 타겟 world 3D 선속력이다. 최초 진입 시 속도가 비유한이거나 지급액이 0이어도 기회를 소진한다. 같은 step 재조회는 캐시를 사용하며 부분 reset은 해당 환경의 이력만 지운다. 이벤트 raw는 지급액에 step_dt가 중복 적용되지 않도록 dt로 나눈다. 최초 진입과 성공 timeout이 같은 step이면 최대 +100이다.

구현은 기존 `envs/revision_envs.py`, `assets/scenes/revision.py`, `mdp/rewards/revision.py`, `mdp/reward_functions/revision.py`, `agent/revision_ppo_cfg.py`, 패키지 `__init__.py`에 모았다. v1의 post-init이 지정하는 Gaussian용 Hold params는 v2 post-init에서 Smoothstep용 `full_reward_radius`·`outer_radius`로 교체한다.

## 상속하여 유지하는 설정

- Actor 그룹 policy 57D + obstacles 64D, Critic 전용 privileged 3D + critic_obstacles 64D. 입력 의미·순서·노이즈·현재 타겟 GT의 Critic 전용 계약은 v1과 같다.
- 8D 행동·OSC·자산·물성·배치·reset·종료 판정, physics_dt 0.01s·step_dt 0.02s·에피소드 10s를 유지한다.
- 보상 term 15개의 이름·순서를 유지한다. 변경하지 않은 9개 항의 callable·params·weight는 같다.
- 장애물 요청은 Gray/White 3/3 → 10k 3/4 → 12k 4/4 → 14k 4/5다. 배치 실패 시 실제 수는 요청보다 적을 수 있다.
- `target_free_speed`의 0.1→0.02m/s 커리큘럼과 goal direction deadzone 커리큘럼을 유지한다.
- PPO gamma 0.98·GAE lam 0.95 등 모든 학습 설정을 유지하고 experiment_name만 분리한다.

## 실행

Workspace 루트, `env_isaaclab` 환경에서 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Revision-v2 --num_envs 2048 --headless

python src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Revision-Test-v2 --num_envs 2048 --headless

python src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Revision-Test-v2 \
  --checkpoint <Test-v2-checkpoint.pt> --num_envs 1 --real-time
```

CPU86개, v2 GPU64/2048·Test64 초기화/rollout/부분reset, 실제 EEF·접촉·Hold 지급액 검사, 두 환경의 PPO2iterations와 체크포인트 저장을 통과했다. 실제 실행 범위와 산출물은 [개발·검증 기록](../logs/2026-11-03_revision_v2_implementation.md)을 따른다. 짧은 실행 검증은 장기 성공률이나 상부 누르기 감소를 입증하지 않는다.


## Test-v2-GT: 실시간 타겟 위치 대조 실험

`Isaac-Inspire-Revision-Test-v2-GT`는 `RevisionV2TestGTEnvCfg(RevisionV2TestEnvCfg)`로 직접 상속한다. 성공률 저하에 실시간 타겟 위치 관측의 부재가 기여하는지 확인하기 위한 대조 환경이다. 보상·장면·제어·종료·커리큘럼은 Test-v2와 동일하다.

변경은 **Actor가 Critic의 현재 타겟 위치3D를 추가로 받는 것**이다. 기존 `privileged.target_position`과 `object_position_in_root`를 그대로 사용하여 매 관측 시 robot root 좌표계의 XYZ(m)를 제공한다. 해당 그룹은 noise·corruption이 없다. 기존 초기 타겟 관측과 그 노이즈, Actor의 초기 장애물64D, Critic의 현재 장애물64D는 유지한다. 속도·자세 등 다른 실시간 타겟 정보는 추가하지 않는다.

| 구성 | Test-v2 | Test-v2-GT |
| --- | --- | --- |
| Actor 그룹 | policy + obstacles | policy + privileged + obstacles |
| Actor 원시 입력 | 57 + 64 = 121D | 57 + 3 + 64 = 124D |
| Actor MLP 입력 | 57 + 장애물 embedding16 = 73D | 57 + 3 + embedding16 = 76D |
| Critic 그룹·차원 | policy + privileged + critic_obstacles, 원시124D·MLP76D | 동일 |
| Actor 모델 | RevisionModel | RevisionGTModel(RevisionModel) |
| PPO runner | RevisionV2TestPPORunnerCfg | RevisionV2TestGTPPORunnerCfg(RevisionV2TestPPORunnerCfg) |
| experiment_name | inspire_revision_test_v2 | inspire_revision_test_v2_gt |

EnvCfg 전체 값은 부모와 같다. 관측 생성은 그대로 두고 runner의 Actor 그룹 선택만 확장한다. 기존 모델의 strict 57D Actor 계약을 보존하기 위해 GT 전용 파생 모델을 사용한다. Actor의 첫 linear 입력만76D로 확장되며 hidden layers256/128/64·독립 장애물encoder64→32→16·PPO gamma0.98·lam0.95 등은 같다. Critic에는 타겟 위치를 중복 추가하지 않는다.

Actor 입력 차원이 달라 Test-v2 checkpoint를 그대로 resume할 수 없다. 같은 seed·환경 수·학습 iteration 조건으로 새 학습을 시작하여 비교한다. GT가 더 좋은 결과를 내면 현재 위치 정보 부족이 기여했음을 뒷받침하지만, GT도 실패한다는 결과만으로 보상만이 원인이라고 단정할 수는 없다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Revision-Test-v2-GT --num_envs 2048 --headless

python src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Revision-Test-v2-GT \
  --checkpoint <Test-v2-GT-checkpoint.pt> --num_envs 1 --real-time
```

[GT 구현·검증 기록](../logs/2026-11-03_revision_v2_gt_implementation.md)을 따른다.
