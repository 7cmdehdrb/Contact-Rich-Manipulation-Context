# Final v1·v2 환경 계약

[v1 단독 상세 명세: 관측·Scene·Action·Reward·Curriculum·Termination](FINAL_V1_ENVIRONMENT.md)

[환경 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [개발·검증 로그](../logs/2026-10-26_final_v1_v2.md) · [부모 Final v0](FINAL_V0_ENVIRONMENT.md)

기준일: 2026-10-26. 사용자 요청에 따라 `FinalEnvCfg → FinalV1EnvCfg → FinalV2EnvCfg`로 직접 상속한다. 기존 Final v0·Holding·OSC·ObjectRandom의 설정과 계산 함수는 보존한다. 구현·CPU 검사·실제 launcher 설정 import·USD 자산 검증을 수행했으며, GPU 물리 rollout과 학습 수렴은 미검증이다.

## 등록과 실행

| 항목 | v1 | v2 |
| --- | --- | --- |
| Gym task | `Isaac-Inspire-Final-v1` | `Isaac-Inspire-Final-v2` |
| EnvCfg | `FinalV1EnvCfg` | `FinalV2EnvCfg` |
| 직접 부모 | `FinalEnvCfg` | `FinalV1EnvCfg` |
| runtime | `FinalV1Env` → `FinalEnv` | v1과 동일 |
| PPO | `FinalV1PPORunnerCfg` | `FinalV2PPORunnerCfg` |
| experiment | `inspire_final_v1` | `inspire_final_v2` |
| 타겟 위치 | 중심 반경2cm 원판 | 선반 중앙80%와 형상·접근 안전영역의 교집합 |

역할별 기존 `final.py`에 버전 CFG를 모았다. 계산은 `mdp/*_functions/final.py`, 기하는 `mdp/common/final_geometry.py`, 자산은 `assets/final_spawners.py`, 재생 박스는 `assets/final_visualization.py`다. [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/final_envs.py) · [runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/final.py) · [PPO](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/final_ppo_cfg.py).

Workspace 루트에서 실행한다. 아래 환경 수는 실행 예시이며 대규모 성능 검증값이 아니다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Final-v1 --num_envs 256 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Final-v2 --num_envs 256 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Final-v2 --num_envs 1 --checkpoint "<Final-v2-checkpoint.pt>" --real-time
```

v1 재생은 task와 checkpoint를 v1으로 바꾼다. 학습은 `train.py`를 사용한다. 학습 로그는 변경·정리하지 않았다. 외부 선반 USD와 기존 NVIDIA YCB 자산의 접근 조건은 부모와 같다.

## 관측·정책

촉각 17D에는 관측 계산마다 셀별 독립 확률 0.01의 bit flip을 적용한다. F/T 6D에는 평균 0의 독립 가우시안 노이즈를 힘 축별 σ=0.05N, 모멘트 축별 σ=0.005N·m로 더한다. ObservationManager의 noise 단계에서만 적용하여 원본 센서·접촉 및 wrench 보상은 유지한다. v1·v2·Test의 Actor·Critic이 공유하는 policy 관측에 적용하며 reset 원본 0에도 같은 노이즈를 적용한다.

`actions` 8D는 직전 raw Action의 Arm·Hand 전체에 `tanh`를 적용한 피드백이다. v1과 이를 상속하는 v2·Test에 적용하며 실제 Action 처리와 raw Action 변화량 페널티는 유지한다. 관측 순서·차원은 그대로다.

Policy에 실제 Hand 관절 위치로 계산한 `[flexion_openness, thumb_opposition_openness]`를 추가한다. 첫 채널은 11개 굴곡 관절의 실제 위치를 기존 open/closed target 선분에 최소제곱 투영하고, 두 번째는 thumb opposition 관절의 위치를 역정규화한다. 두 관측만 `[0,1]`로 제한한다. Hand action 자체나 페널티 입력을 변경하지 않는다.

| 입력 | v0 | v1·v2 |
| --- | --- | --- |
| policy | 55D | 57D |
| 초기 장애물 `[present,x,y,z]` | 16슬롯·64D | 20슬롯·80D |
| Critic 전용 현재 타겟 위치 | 3D | 3D |
| Actor / Critic 원시 합계 | 119D / 122D | 137D / 140D |
| 장애물16D 임베딩 후 MLP 입력 | 71D / 74D | 73D / 76D |

기존 모델의55D 검사와 이전 checkpoint를 보존하기 위해 새 `FinalV1Model`을 사용한다. 장애물 encoder·MLP·PPO 계수는 유지한다. v0 checkpoint는 새 관측/encoder 차원과 직접 호환되지 않는다. v1·v2는 같은 모델 차원을 쓰지만 초기 위치 분포가 다르다.

## 보상과 이름

| 새 이름 | 부모 항과 계산 |
| --- | --- |
| `hand_reaching` | `reaching` 이름 변경 |
| `goal_distance`, `goal_hold`, `hand_contact` | 기존 식·계수 유지 |
| `action_rate_penalty` | Arm·Hand 각각 raw action 변화량 제곱합을100에서 상한 처리한 뒤 각각−0.03 적용 |
| `joint_velocity_penalty` | 이름으로 선택한 실제 Arm·Hand 관절속도 제곱합을 각각100에서 상한 처리, −0.03/−0.01 적용 |
| `object_penalty` | 기존 `object`×−30 + `object_acceleration`×현재 acceleration weight |
| `shelf_penalty` | 기존 `shelf_failure`×−3 + `shelf_collision`×−0.5 |
| `object_speed_penalty` | `pushing_speed` 이름 변경 |
| `obstacle_contact_penalty` | `obstacle_contact` 이름 변경 |
| `wrench_change_penalty` | `wrench_change` 이름 변경 |

`arm_speed_excess`, `eef_linear_speed`와 연결된 커리큘럼은 v1·v2에서 제거한다. 병합 네 항의 Manager weight는−1이고, 내부 양의 비용에 기존 계수의 절댓값을 반영한다. RewardManager의 dt는 한 번만 적용하며, `shelf_failure`의 일회성−3을 위한 dt 상쇄는 유지한다. **선반 변위만으로 종료될 때 원래 없던 일회성−3을 추가하지 않는다.** 기존 로컬 `action_rate_l2`·`joint_vel_l2`를 호출하며 합산 후 단일 상한·평균·정규화·보상용 Hand clamp를 도입하지 않는다. 이는 네 항을 분리하던 기존 지침에 대한 이번 사용자 명시 병합 요청의 예외이고 이전 환경에는 적용하지 않는다.

가속도 history의 reset/첫 활성화 무효화와 개별 물체100 상한을 유지한다. wrench의 누적 양의 보상5% 예산도 유지한다. Goal 반경의 기준 이름 `goal_hold`를 유지하여 목표 보상·접촉 간주·reaching·success가 같은 live curriculum 값을 읽는다.

## 종료

`object_drop`은 유지한다. `push_fast → object_speed`, `hand_velocity → joint_velocity`로 변경한다. 후자는 기존과 같이 Arm 관절의 threshold5를 검사한다. `shelf_termination`은 기존 shelf collision OR shelf displacement이며 임계값을 바꾸지 않는다.

10초, 즉 현재 설정의500 control step 만료 시 타겟의 월드XY 목표 오차가 현재 `goal_hold.position_tolerance` 이하이면 `success`, 아니면 `time_out`이다. 두 항은 상호 배타적이며 합집합은 기존 timeout과 같다. 속도·추가 체류시간 조건이나 조기 성공 종료를 넣지 않는다. 두 항 모두 `time_out=True`여서 시간 한계의 truncation 및 value bootstrapping을 보존한다. 기존 실패 조건은 그대로 작동한다.

## 물체·크기·시각화

- 장애물: 기존 NVIDIA YCB4종×기존 크기3단계에 머그와 뚜껑 있는 병을 추가한다. 새 물체는 로컬 procedural mesh로 만들며 머그의 빈 내부·손잡이, 병의 몸통·어깨·목·뚜껑을 복수 convex collider로 표현한다.
- 타겟: 실린더·큐브·랜덤 물체 그룹을 각각1/3 확률로 선택한다. 랜덤 그룹에는 기존12 variant와 새 머그·병이 모두 포함된다. 타겟은 collection index0을 유지한다.
- 크기: `object_size_randomization` prestartup Event에서 타겟·장애물 각각을 현재 variant 대비 균일비율 `U(0.9,1.1)`로 확대·축소한다. **종류와 크기는 환경 생성 시 선택하고 episode 중/매 reset마다 다시 조리하지 않는다.** 위치·yaw·질량·마찰은 reset 때 재추출한다. 이는 PhysX 실행 중 USD scale 변경을 피하는 구성이다.
- 모든 형상의 실제 bottom-origin bounds를 저장하고 reset Z를 `shelf_surface_height - scaled_min_z`로 설정한다. 시각·충돌 형상을 함께 확대하고 실린더의 명시 관성은scale²를 적용한다. COM은 prim-local 값을 유지하여 PhysX의 root scale과 이중 적용하지 않는다.
- 스폰 충돌은 실제 회전OBB와2mm 간격으로 검사하고, 초기 가림은 물체별 확대된 외접반경을 사용한다. 타겟·목표·접근 경로도 확대된 형상을 반영한다.
- `play.py`가 새 환경의 `target_bounding_box`를 켜서 노란3D wire box를 생성한다. RigidBody/Collision/Mass API가 없는 순수 BasisCurves이며 타겟을 따라간다. 학습 기본값은false로 박스 prim 자체를 생성하지 않는다. 실제 GPU 화면 외관은 미검증이다.

## 개수 fallback과 v2 위치

물리 용량은 Gray10·White10이며 관측20슬롯과 일치한다. 각 reset은 현재 커리큘럼의 개수를 먼저 시도한다. 실패한 행에 대해서만 White 한 개, Gray 한 개를 교대로 줄이며 다시 시도한다. 다른 행의 배치·진행 중 mask는 바꾸지 않는다. 타겟과 목표도 재추출하지 않는다. 개수 단계마다 최대8회 source generator를 호출하고, 각 호출은scene_attempts4를 사용한다. 가장 낮은0/0 단계는 유효한 단일 타겟 장면을 반환하므로 과밀 배치 실패로 초기화 전체를 중단하지 않는다. 잘못된 자산·설정 오류를 무차별 숨기지는 않는다. 탐색 실패는 최대 물리 수용량의 증명이 아니다.

실제 활성 수는 `Curriculum/obstacle_actual_gray`, `Curriculum/obstacle_actual_white`에 기록한다. 요구 수와 실제 수가 다를 수 있다. 비활성 슬롯은높이100m에 주차하고 중력을 끄며 보상·촉각·관측의 기존 active mask를 적용한다.

v2의 중앙80%는 선반 평면 X±0.16m, Y±0.40m이다. 이를 실제 타겟 footprint·2cm edge clearance·source 접근 경로 safe bounds와 교차한 사각형에서 균일 추출한다. 따라서 큰 물체의 중심은 더 안쪽에 제한된다. 방향은 기존 deadzone curriculum을 따르고, 해당 방향의 선반 내부 ray 길이를 계산하여5~15cm 목표를 준다. 너무 짧은 ray는 방향을 다시 추출하며, 유한 횟수 후에는 공간이 남는 Y방향을 사용한다. 기하적 선반·경로 가능성을 검사한 것이며 전체 Arm IK·접촉 동역학의 성공을 보증한 것은 아니다.

## 커리큘럼

| 이름 | v1·v2 일정 |
| --- | --- |
| `obstacle_population` | 초기1/1, 2000에White2, 3000에Gray2, 이후1000마다 교대 증가. White8은14000, Gray8은15000부터 유지 |
| `obstacle_gray_zone_padding` | 4000의0 →10000의0.15, 1000간격 |
| `wrench_free_force_change` | 3000의50 →10000의20, 250간격 |
| `wrench_free_moment_change` | 3000의5 →10000의2, 250간격 |
| `object_free_acceleration` | 3000의50 →10000의20, iteration마다 선형 |
| `object_acceleration_weight` | 3000의0 →10000의−0.05, iteration마다 선형. 병합 항의 내부 가중치를 갱신 |
| `goal_position_tolerance` | 4000의0.02m →10000의0.01m, iteration마다 선형 후고정 |
| `object_free_speed`, `goal_deadzone`, `goal_speed_scale`, `wrench_weight`, `obstacle_free_force`, `obstacle_weight` | 이름·대상 term 연결을 제외하고 부모 일정 유지 |

모든 일정은 절대 learning iteration을 읽는다. checkpoint 재개·rewind 때 해당 값으로 복원한다. 시작 iteration의 값은 초기값이며 이후 지정 간격부터 감소한다. Gray padding0.15는 현재 타겟 형상에 맞춘 Red 반경의15%다.
