# Revision-v1 / Revision-Test-v1 구현 계약

[개발 명세와 비교 그래프](../../01_plan/environments/2026-11-02_REVISION_V1_SPEC.md) · [개발·리뷰·검증 기록](../logs/2026-11-02_revision_v1_implementation.md) · [부모 v0](REVISION_V0_ENVIRONMENT.md)

2026-11-02 구현. v0를 수정하지 않고 지정 부모의 파생 환경을 추가했다. 이전 명세의 “미구현” 표기는 설계 당시 상태이며, 현재 구현·검증 상태는 이 문서와 개발 로그를 따른다.

## 등록과 상속

| Gym ID | EnvCfg의 직접 부모 | PPO 설정·experiment_name |
| --- | --- | --- |
| `Isaac-Inspire-Revision-v1` | `RevisionV1EnvCfg(RevisionEnvCfg)` | `RevisionV1PPORunnerCfg(RevisionPPORunnerCfg)` · `inspire_revision_v1` |
| `Isaac-Inspire-Revision-Test-v1` | `RevisionV1TestEnvCfg(RevisionV1EnvCfg)` | `RevisionV1TestPPORunnerCfg(RevisionV1PPORunnerCfg)` · `inspire_revision_test_v1` |

두 환경 모두 기존 `runtime.revision:RevisionEnv`를 사용한다. EnvCfg는 `envs/revision_envs.py`, PPO는 `agent/revision_ppo_cfg.py`다. Test의 과업 설정 차이는 `scene.object_collection.rigid_objects.mass_cylinder.spawn.kind_override = "cylinder"` 하나이며, PPO는 저장용 experiment 이름만 다르다.

## 부모에서 보존한 계약

- Actor 121D(policy 57 + obstacles 64), Critic 124D(policy 57 + privileged 3 + critic_obstacles 64), 순서·센서·노이즈·초기/현재 정보 구분 유지. 새로운 entry latch는 관측에 추가하지 않았다.
- Arm OSC/Hand 행동·제어 매핑 유지. 물리 dt 0.01s, decimation 2, control dt 0.02s, episode 10s 유지.
- 물리 객체 10개, 타겟 슬롯 0, 장애물 후보 9개, 관측 슬롯 16개, Gray padding 65mm와 기존 OBB 탐색·fallback 유지.
- Scene 자산·물성·크기 U(0.9,1.1), reset·목표·방향·센서 랜덤화 유지. 종류·크기는 생성 시 고정이며 reset마다 기존 방식으로 위치·활성 구성이 갱신된다.
- 성공/실패/timeout 6개 term과 bootstrapping 유지. Timeout 성공은 유한 XY 거리 3cm 이하이며 Hold/entry의 엄격한 미만 조건과 다르다.
- 목표 거리·접촉·reaching·robot 비용·shelf 비용·target speed 비용 함수와 PPO 수치 유지.

## 보상 변경

아래 값은 RewardManager weight다. 연속 항에는 control dt가 곱해지고 사건 항은 callable 내부에서 dt로 나누므로 1회 금액을 유지한다. 실행 순서는 이 표와 같다.

| 순서 | term | weight | 계약 |
| ---: | --- | ---: | --- |
| 1 | `target_reaching` | 30 | 부모 유지 |
| 2 | `target_goal_distance` | 3.7 | 부모 유지 |
| 3 | `target_goal_hold` | 8 | 아래 Gaussian·free speed |
| 4 | `target_contact` | 1.45 | 부모 유지 |
| 5 | `robot_action_rate_penalty` | −1 | 부모 유지 |
| 6 | `robot_joint_velocity_penalty` | −1 | 부모 유지 |
| 7 | `object_tilt_penalty` | −30 | 활성 모든 물체의 기존 tilt cost |
| 8 | `obstacle_displacement_penalty` | −150 | 활성 비타겟 3D 변위 제곱합, 합산 후 cap 0.04 |
| 9 | `object_acceleration_penalty` | −0.05 | 활성 모든 물체의 기존 COM acceleration cost, free 20, 물체별 cap 100 |
| 10 | `shelf_penalty` | −1 | 부모 유지 |
| 11 | `obstacle_contact_penalty` | −0.05 | 기존 함수, free force 50N, cap 100 |
| 12 | `target_goal_first_entry_bonus` | 30 | 최초 유한 XY 오차 <3cm, event/dt |
| 13 | `target_goal_timeout_bonus` | 40 | 기존 timeout 성공 event/dt |
| 14 | `wrist_wrench_change_penalty` | −0.1 | 기존 raw 곡선, 다른 보상과 budget 연동 삭제 |
| 15 | `target_speed_penalty` | −5 | 기존 함수·free speed 커리큘럼 유지 |

`object_penalty`는 비활성이다. 분리된 3항의 합은 같은 고정 파라미터에서 기존 composite와 같다. 기존 순수 함수와 `ObjectAccelerationPenalty`를 재사용해 mask, 첫 유효 sample 억제, 물체 활성 전환, 부분 reset/cache를 유지했다.

Hold의 원시 보상은 다음과 같다. d는 XY 거리, v는 기존 측정의 3D 선속도 크기이며 기존 bbox bottom·tilt·active·finite 유효성 조건을 그대로 적용한다.

```math
H(d,v)=\mathbf{1}_{d<0.03}\,2\,2^{-4(d/0.03)^2}\,
2^{-\left(\max(0,v-0.05)/0.05\right)^2}
```

가중 rate는 중앙 16, 1.5cm에서 8, 3cm 바로 안쪽 약 1, 3cm 이상 0이다. 0.05m/s까지 속도 감쇠가 없다. `goal_hold_outer_radius=None`은 호환 필드이며 reward params에서는 outer_radius를 제거했다.

손목은 `IndependentWrenchMagnitudeChangePenalty`로 분리했다. 같은 EEF 센서에서 force/moment의 벡터 크기 차이를 사용하며 free 20N/2Nm, saturation ratio 2.5, sharpness 3, raw cap 1이다. 가중 step 최대 비용 크기는 0.002다. 다른 보상·누적액·순서를 읽지 않는다. v0의 기존 budget 함수는 수정하지 않았다.

`FirstGoalEntryBonus`는 env별 bool과 동일 step cache를 소유한다. 첫 진입 후 이탈·재진입해도 재지급하지 않고 해당 env reset에서만 초기화한다. 속도·높이·Hold 유효성·실패 여부로 entry를 막지 않는다. 매 control step의 상태만 판정하므로 sample 사이 통과까지 검출하지는 않는다. 최초 진입과 timeout 동시 발생 시 +70, 이전 진입 후 timeout 성공 시 그 step에는 +40이다. timeout 이전 실패 step에서 첫 진입하면 +30이다. 정확히 3cm는 entry 없이 timeout +40만 가능하다.

## 커리큘럼

삭제한 7개 term은 `None`으로 비활성화한다. 상수 schedule로 남기지 않는다. 고정값은 object acceleration −0.05/free 20, obstacle contact −0.05/free 50N, wrist −0.1/free 20N/2Nm다. **Obstacle contact의 12k 값인 −0.1/free 30N을 사용하지 않는다.**

활성 커리큘럼은 `obstacle_population`, `target_free_speed`, `target_goal_direction_deadzone`의 3개다. 뒤 두 항은 부모 callable·params·일정을 그대로 유지한다.

| iteration | Gray 요청 | White 요청 |
| --- | ---: | ---: |
| 0~9999 | 3 | 3 |
| 10000~11999 | 3 | 4 |
| 12000~13999 | 4 | 4 |
| 14000 이후 | 4 | 5 |

기존 population 함수에 각 역할 interval 4000, White start 10000, Gray start 12000을 전달한다. 합쳐서 2000마다 교대 증가한다. 초기 reset params도 3/3이다. 변경은 다음 reset에 적용하며 진행 중 에피소드의 mask는 바꾸지 않는다. 배치 실패 fallback 때문에 실제 수는 요청보다 적을 수 있으며 기존 actual population/layout complete 계측을 유지한다.

## Test의 타겟 고정

`RevisionV1TestSceneCfg(RevisionSceneCfg)`가 기존 10개 슬롯을 보존하고 타겟 spawner만 cylinder로 지정한다. 기준 반지름 0.04m·높이 0.10m에 U(0.9,1.1) scale을 계속 적용한다. 장애물은 8종 그대로다.

Spawner의 optional `kind_override` 기본값은 None이다. 기존 kind 추첨을 소비한 뒤 선택값만 교체해 이후 scale·장애물 난수열을 보존한다. 타겟 bbox·관성·배치가 형상에 따라 달라지는 것은 의도한 차이다.

## 실행과 검증

Workspace 루트에서 Isaac Lab Python 환경을 활성화하고 실행한다. 실행 전 서버 에셋 경로와 GPU를 확인한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Revision-v1 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Revision-Test-v1 --num_envs 2048 --headless
```

실제로 수행한 CPU·GPU·PPO 범위와 리뷰 결과는 [개발 로그](../logs/2026-11-02_revision_v1_implementation.md)에 기록한다. 짧은 smoke는 장기 성공률·중앙 정밀 정지 개선을 입증하지 않는다.
