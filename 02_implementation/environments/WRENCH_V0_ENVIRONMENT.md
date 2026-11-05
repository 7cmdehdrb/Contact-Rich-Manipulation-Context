# Inspire-Wrench-v0 환경

2026-11-05 문서 안내: v0·v0_1·v0_2·v0_3·v0_4의 공통 구성과 현재 수치·버전별 차이는 [Wrench v0 계열 상세 명세](WRENCH_V0_FAMILY_ENVIRONMENTS.md)에서 함께 확인한다.

최종 통합 명세: [Wrench-v0 전체 환경 및 v1 변경점](WRENCH_V0_V1_ENVIRONMENT.md). 랜덤화·관측·액션·전체 보상·커리큘럼·종료와 최신 v1 스케일/action-rate는 통합 문서를 기준으로 읽는다. 아래는 버전별 구현 배경과 검증 기록을 보존한 설명이다.

2026-11-04 구현. 기능 기준은 `Isaac-Inspire-Revision-Test-v2`이며, **기존 환경 상속을 끊은 독립 환경**이다. [개발·검증 기록](../logs/2026-11-04_wrench_v0_implementation.md) · [기능 기준 Test-v2](REVISION_V2_ENVIRONMENT.md).

## 등록과 독립성

| 항목 | 값 |
| --- | --- |
| Gym ID | `Inspire-Wrench-v0` — 사용자 지정 이름 그대로, Isaac 접두사 없음 |
| EnvCfg | `envs/wrench_envs.py:WrenchEnvCfg(ManagerBasedRLEnvCfg)` |
| Runtime | `runtime/wrench.py:WrenchEnv(ManagerBasedRLEnv)` |
| Scene | `assets/scenes/wrench.py:WrenchSceneCfg(InteractiveSceneCfg)` |
| PPO | `agent/wrench_ppo_cfg.py:WrenchPPORunnerCfg(RslRlOnPolicyRunnerCfg)` |
| experiment_name | `inspire_wrench_v0` |

Scene·Action·Command·Observation·Event·Reward·Termination·Curriculum·PPO 설정은 역할별 `wrench` 파일에서 독립 선언한다. Revision/Final 환경·Scene·PPO Cfg를 상속하거나 인스턴스화하지 않는다. 기존 자산 spawner, `RevisionGoalCommand`, `RevisionModel`, MDP 함수·상태 term·OSC 제어 구현은 재사용한다. 따라서 환경 상속은 없지만 공유 계산 함수와 자산 구현까지 복제한 패키지는 아니다. 기존 Test-v2의 TEMP 출력은 Wrench에 적용되지 않는다.

## 변경 계약

| 항목 | Test-v2 | Wrench-v0 |
| --- | --- | --- |
| 거리·Hold·접촉 EEF 높이 | strict `< 0.095m` | strict `< 0.12m` |
| 성공 조건 | timeout AND XY 거리 ≤3cm | XY 거리 ≤3cm AND world 3D 선속력 ≤0.005m/s, 연속3초 |
| 성공 종료 | `time_out=True` truncation | `target_goal_success`, 실제 termination |
| 성공 보상 | `target_goal_timeout_bonus`, +75 | `target_goal_success_bonus`, +75 |
| 10초 제한 | 목표 거리로 성공/실패 분할 | 연속 성공 미달이면 `target_goal_miss_at_timeout`; 보상 없음 |
| RED 여유 | 3mm | 23mm, 기존보다20mm 확장 |
| 후방 Gray 사각형 | 기존 중심 | 타겟→목표 반대 방향20mm 후퇴, 크기160×220mm 유지 |
| Gray 외곽 여유 | 65mm | 확대된 RED 바깥65mm 유지 |
| 배치 검색 | 매 reset | startup에서 환경별·단계별 후보 생성, reset에서 선택 |
| 물성 샘플 | reset마다 질량·마찰·관성 변경 | startup에서 한 번 샘플링·적용, 환경별 고정 |
| Dead Zone | hold3000, interval500 | 10000에서 첫 −5°, 이후3000마다 −5° |

높이는 초기 선반 위치 Z + 작업면1.05m 기준 EEF 높이다. `goal_reward_height_limit=0.12`를 공통으로 사용하며, 환경 생성 시 `contact_height_limit`도 동기화하여 Hydra override 이후에도 세 항의 기준이 일치한다. 기존 95mm 제한과 shelf failure 증가의 인과는 사용자의 가설이며 이번 구현으로 입증된 결과가 아니다.

성공 타이머는 제어 step당 한 번 증가한다. step_dt0.02s에서는150회 연속 표본이 필요하다. 거리·속도 조건 이탈 또는 비유한 위치/속도는 해당 행의 타이머를0으로 만든다. 부분 reset은 해당 환경만 초기화한다. 같은 step 재조회는 타이머를 추가로 증가시키지 않는다. 물체 낙하·속도·선반·관절 실패 term을 먼저 계산하며, 같은 step 실패가 있으면 성공과 +75는 억제한다. 성공과10초 제한이 같은 step이면 성공을 우선하여 success termination만 보고한다. 다른 실패와 timeout 동시 발생은 기존 Manager 동작을 유지한다.

+75는 raw 값에 step_dt 역수를 적용하여 RewardManager 적분 후 정확히75가 된다. 최초 목표 진입 보상은 기존 최대+25와 속도 감쇠·1회 latch를 유지한다. 성공 타이머는 높이나 각속도를 추가 조건으로 사용하지 않는다. 최초 진입의 기존 strict d<3cm와 새 성공의 inclusive d≤3cm를 구분한다.

RED는 기존 swept target와 손목 진입 extrusion을 확장한다. **손 진입 후방 사각형 전체를 RED로 바꾸지 않는다.** 후방 사각형은 Gray로 유지하고20mm 후퇴한다. Gray는 RED와의 중첩을 제거한 뒤 판정한다. White도 변경된 RED/Gray 밖으로 밀린다. 최소 물체 간격20mm·보드 wall margin5mm·Gray 패딩65mm는 유지한다. 공용 `LayoutConfig.rear_offset` 기본값은0이므로 기존 환경은 기존 위치를 유지한다.

## 초기화와 reset 수명

| 시점 | 처리 |
| --- | --- |
| Scene 생성·prestartup | 기존 형상/크기 선택, 메타데이터·scaled bounds 준비. 타겟 cylinder, 장애물8종, 크기±10%,10개 물리 객체 |
| startup | 실제 환경별 bounds로9개 커리큘럼 상태×각16개 배치 후보 계산. 물성 buffer 준비 후 질량/마찰 샘플·shape별 관성 적용 |
| reset | 현재 단계의 후보를 균등 복원추출, 물체 pose·속도 초기화·활성 mask·gravity 적용, 목표/초기 관측과 noise·visibility·인접 swap 갱신 |
| step | 기존 물리·OSC·센서·보상·관측, 연속 성공 타이머 계산 |

후보는 각 환경의 실제 형상·크기에 대응한다. 다른 환경의 후보를 가져오지 않는다. 배치 실패 후보도 기존 generator의 best-count 결과 그대로 보관하고 `actual`·`complete`를 기록한다. 유효하지 않은 배치로 개수를 강제로 맞추지 않는다. startup 단계표는 아래 일정의9개 조합이다.

| iteration | Dead Zone 반각 | Gray/White 요청 수 |
| --- | --- | --- |
| 0~9999 | 30° | 3/3 |
| 10000~11999 | 25° | 3/4 |
| 12000~12999 | 25° | 4/4 |
| 13000~13999 | 20° | 4/4 |
| 14000~15999 | 20° | 4/5 |
| 16000~18999 | 15° | 4/5 |
| 19000~21999 | 10° | 4/5 |
| 22000~24999 | 5° | 4/5 |
| 25000 이후 | 0° | 4/5 |

`layout_bank_size=16`, `layout_build_batch_size=256`이다. 2048환경의 기본 bank tensor 크기는57,507,840bytes(약54.84MiB)이며 초기 검색의 임시 tensor는 별도다. 초기화가 더 오래 걸리는 대신 모든 커리큘럼 전환·reset에서 검색을 없앤다. `reset(seed=...)`는 후보 선택/배치 관측용 RNG를 재설정하며 기존 bank나 물성을 재생성하지 않는다. bank를 재현하려면 같은 생성 seed·환경 수·build batch를 사용한다.

최적화로 랜덤화의 시간적 분포가 바뀐다. 환경별·단계별 레이아웃은 유한16개 후보를 반복 방문하고, 물성은 환경 수 방향으로 다양하지만 한 환경의 episode 사이에는 고정된다. 2048환경이면 단계별32768개 후보가 있다. 더 많은 후보가 필요하면 `env.layout_bank_size`를 늘릴 수 있으나 startup 시간·메모리가 비례 증가한다. 커리큘럼을 별도 변경할 경우 `LAYOUT_STAGES`도 함께 변경해야 하며, 미리 만들지 않은 조합은 reset에서 명시적으로 오류를 낸다.

## 보존한 전체 계약

- Actor `policy57 + obstacles64 = 121D`, Critic `policy57 + privileged3 + critic_obstacles64 = 124D`. Actor 초기 타겟·초기 장애물, Critic 실시간 타겟XYZ·실시간 활성 장애물을 유지한다. 노이즈·정렬·가시성·swap 계약은 Test-v2와 같다. GT Actor를 추가하지 않는다.
- 관측 순서는 Arm12D → Hand2D → EEF7D → 초기 타겟3D → 목표2D → 이전 행동8D → 촉각17D → F/T6D, 장애물은 별도16슬롯×4D이다.
- 행동8D·기존 OSC·arm stiffness/damping0·position_scale0.03·orientation_scale0.15를 유지한다. physics_dt0.01s, decimation2, episode10s, 환경2048·spacing2.5가 기본이다.
- 타겟 cylinder와 장애물9후보, 자산·scale·바닥 정렬·주차 높이·접촉 센서·PhysX 설정을 유지한다. object_fall_or_tilt(bottom clearance0.01·fail_angle0.9), target_speed1m/s, shelf_failure, arm_joint_velocity5rad/s는 같은 함수·params다.
- 보상15개 순서는 reaching30, distance3.7, hold10, contact1.45, action-rate−1, joint-velocity−1, tilt−30, displacement−150, acceleration−0.05, shelf−1, obstacle-contact−0.05, first-entry25, success75, wrench-change−0.1, target-speed−5다. 성공 보상 이름·trigger 외 term callable/params/weight는 동일하다.
- Hold는2.5~3.5cm Smoothstep·속도 감쇠 없음, first-entry는free_speed0.01·speed_scale0.02m/s, acceleration free15m/s², obstacle-contact free50N, wrench-change free20N/2Nm·budget 없음이다.
- target_free_speed 커리큘럼은 기존0.1→0.02m/s, 장애물 증가는 기존10k/12k/14k를 유지한다.
- PPO rollout36, gamma0.98, lambda0.95, hidden256/128/64, actor/critic 독립 장애물encoder64→32→16, epoch8/minibatch4/lr0.001/adaptive/entropy0.005/clip0.2 등은 동일하다. 실험명만 변경한다.
- 기존 Metrics 이름을 유지한다. 성공 로그는 `Episode_Termination/target_goal_success`, `Episode_Reward/target_goal_success_bonus`로 변경한다.

## 실행과 검증 상태

Workspace 루트의 `env_isaaclab`에서 새 학습을 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-v0 --num_envs 2048 --headless
```

CPU 회귀82개 통과, CUDA 전용4개 skip. 2048환경 크기의 순수 CPU 배치에서 기존 검색4.04s, bank선택 평균0.000234s를 측정했다. **실제 GPU collection time1~2초 달성은 미검증**이다. 현재 호스트에서 NVIDIA 드라이버 연결 불가·`torch.cuda.is_available()==False`여서 실제 Isaac Sim 초기화·rollout·PPO 실행은 수행하지 않았다. 다음 GPU 실행기는 준비했지만 실행하지 않았다.

```bash
python src/inspire_sweep_baseline/tests/_wrench_probe.py \
  --headless --device cuda:0 --num_envs 64
python src/inspire_sweep_baseline/tests/_wrench_probe.py \
  --headless --device cuda:0 --num_envs 2048
```

이 실행기의36step 측정도 zero action이며 policy inference·PPO update를 제외한다. 실제 collection 목표는 최종적으로 `train.py`에서 확인해야 한다. 장기 성공률·shelf failure 감소·유한 후보 반복의 학습 영향은 아직 검증하지 않았다.
