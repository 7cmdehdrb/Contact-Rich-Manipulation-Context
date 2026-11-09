# Relative-IK-v0_2-Test: 독립 IK·Holding 결합 환경

## 요청과 독립성

2026-11-09 사용자 요청: IK-v0_1의 Scene·센서·EEF OSC·목표/IK reset·대칭 관측과 Holding OSC v2의 보상·페널티를 결합한다. 후속 답변으로 목표 반경은 **3cm**, 실패 종료와 팔 속도 종료 커리큘럼은 **IK-v0_1 유지**, 독립성은 **설정/runtime 독립 선언 + 공통 계산 구현 재사용**으로 확정했다.

- Gym ID: `Inspire-Wrench-Refactor-Relative-IK-v0_2-Test`.
- 실험명: `inspire_wrench_refactor_relative_ik_v0_2-Test`.
- EnvCfg: `WrenchRefactorRelativeIKV0_2TestEnvCfg(ManagerBasedRLEnvCfg)`.
- Runtime: `WrenchRefactorRelativeIKV0_2TestEnv(ManagerBasedRLEnv)`.
- PPO: `WrenchRefactorRelativeIKV0_2TestPPORunnerCfg(RslRlOnPolicyRunnerCfg)`.
- Scene·각 Manager·PPO 설정은 이전 task의 Cfg를 상속하거나 인스턴스화하지 않는다. 센서·제어·배치·보상 함수, spawner 및 대칭 모델 계산 구현은 재사용한다.
- 파일은 기존 역할별 디렉토리에 `wrench_refactor_relative_ik_test.py`로 배치한다. EnvCfg와 PPO는 각각 `_envs.py`, `_ppo_cfg.py` 접미사를 쓴다. 기존 환경의 구현 파일은 변경하지 않는다.

[EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/wrench_refactor_relative_ik_test_envs.py) · [runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/wrench_refactor_relative_ik_test.py) · [검증 로그](../logs/2026-11-09_relative_ik_v0_2_test.md)

## Scene·reset·제어·관측

IK-v0_1과 최종 설정을 전체 대조한다. 원통 타겟1개와 8종×2개의 장애물 후보, 오른손 자산, Axia280g, 선반30kg, 기존 물성·센서·reset 순서를 유지한다. Gray/White 개수는 reset마다 각각0–3 균등 추출하며 물리 후보17개·관측16슬롯을 유지한다. 장애물 증가 일정은 없다.

목표는 시작점에서6–12cm, 허용 방위와 조건부 거리 균등분포다. IK 초기 EEF는 선반 전면 바깥8–10cm·타겟 좌우10–18cm·기본 높이−1~+3cm, 목표 반대편에서 시작한다. 후보1개/IK1회와 양쪽 비물리 표시 박스도 유지한다.

EEF frame OSC와 Hand2D의8D 행동, 위치 scale0.03·회전 scale0.15, Arm 속도3.14rad/s·effort150/150/150/28/28/28Nm, Hand effort10Nm·속도1rad/s를 명시한다. 오른손 자산의 원본 URDF에서 회전 관절12개 모두 effort10·velocity1임을 확인했으며, 기존 실효 제한값과 같다. 물리100Hz·정책50Hz·일반10초 에피소드다.

Actor와 Critic은 **동일한 저장 관측**을 사용한다. policy58D는 팔 위치6·속도6·손 상태2·EEF pose7·초기 타겟3·목표3·이전 행동8·촉각17·F/T6 순서다. 초기 타겟·목표·초기 장애물은 EEF 좌표, EEF pose는 Base 좌표다. 초기 시각 정보의 noise, 촉각 noise, F/T 보정/noise 이후 힘 각 축±150N·모멘트 각 축±8Nm 제한을 보존한다. Critic 전용 현재 타겟/장애물 GT는 없다.

장애물64D를 각 네트워크의64→32→16 인코더로 압축한다. Actor/Critic은 각각 원시122D, MLP 입력74D이며 모델 파라미터를 공유하지 않는다. PPO는 IK-v0_1과 실험명을 제외한 모든 설정이 같다.

## 보상과 페널티

Holding OSC v2에서 `arm_speed_excess`를 제외한16개 term을 사용한다. 나머지 순서·계수·params·callable을 유지하며, `goal_hold.position_tolerance=0.03`과 이전 종료 이름에 의존하던 선반 사건 보상의 연결을 조정했다. 사용자 후속 요청에 따라 팔 속도 초과 페널티와 연결된 `arm_free_speed` 커리큘럼을 삭제했다. 속도 제곱 비용인 `arm_joint_velocity`(weight−0.03)와 동명의 실패 종료는 유지한다.

| term | weight | 계약 |
| --- | ---: | --- |
| reaching | 30 | 현재 EEF–타겟3D 최단 거리 개선, near10cm, reward/m |
| goal_distance | 100 | 타겟–목표XY 최단 기록 개선, tolerance0, reward/m |
| goal_hold | 4 | 유효 타겟·거리≤3cm에서 거리/속도 Gaussian 보상, 지급 시간 상한 없음 |
| hand_contact | 1.45 | 손 전체 접촉≥0.01N OR 유효 타겟의 목표 점유; 중복 지급 없음 |
| arm_action_rate | −0.03 | raw Arm 행동 변화 제곱합, cap100 |
| hand_action_rate | −0.03 | raw Hand 행동 변화 제곱합, cap100; IK의 Hand clamp 비용으로 바꾸지 않음 |
| arm_joint_velocity | −0.03 | Arm 속도 제곱합, cap100 |
| hand_joint_velocity | −0.01 | Holding의 HAND_JOINT_NAMES 전체, cap100; IK의 독립6축 비용으로 바꾸지 않음 |
| object | −30 | 활성 물체 tilt +5×활성 비타겟3D 변위 제곱합; 변위합 cap0.04 |
| shelf_collision | −0.5 | 기존 선반 움직임/손가락·손목 근접 비용 |
| pushing_speed | −5 | 타겟3D 선속도 초과 지수 비용 |
| shelf_failure | −3/event | Holding 선반 충돌 predicate만 사건 비용으로 지급 |
| eef_linear_speed | −1 | 실제 EEF점 선속도 초과 지수 비용 |
| obstacle_contact | 0→−0.1 | 활성 비타겟과 손의 합력 초과 비용 |
| object_acceleration | 0→−0.05 | 활성 물체별 가속도 초과 비용 합 |
| wrench_change | 0→−0.1 | 보정된 raw F/T 크기 변화; 양의 누적보상5% 예산 유지 |

일반 항은 RewardManager가 weight×dt를 적용한다. 두 거리 개선 항과 선반 사건은 함수에서 dt를 상쇄한다. Hold는 `4 × 2^(-((d/0.03)^2+(v/s)^2))`의 초당 보상이며 목표 바깥은0이다. 유효성은 Holding의 선반 상대XY·타겟 root Z1.04–1.07m·기울기 조건을 유지한다. 새 원통 타겟은 실제 초기 root Z1.05m로 GPU 호환 검사를 통과했다.

Holding의 `shelf_failure`는 이전 `shelf_collision` 종료 이름을 읽는다. 새 환경은 IK의 통합 `shelf_failure` 종료를 유지하므로 전용 adapter가 **동일한 선반 충돌 predicate**를 직접 평가한다. 속도6D norm>0.1 또는 손목 clearance<0.03m에만−3을 지급한다. 선반 변위5cm 초과만으로는 이 사건 보상을 지급하지 않는다. 이로써 기존 Holding 지급 범위를 보존한다.

Holding의 접촉은 타겟 전용이 아니며 선반 접촉도 포함한다. 목표 점유 시 접촉 없이도 지급한다. EEF 높이14cm gate, cosine 거리, 역방향 거리 페널티, 최초 진입 보너스, 성공 보너스는 사용하지 않는다. 설정에 남은 IK 높이 메타데이터는 Holding 보상에 적용되지 않는다. 관측의 clip/noise는 F/T 보상 원본에 적용하지 않는다.

## 커리큘럼

학습 iteration 기준이며 성공률 기반 자동 조절은 없다.

- 장애물 증가와 목표 반경 변화: 없음. 반경3cm 고정.
- 방향 제외 반각: 30° 유지,10,000에서25°, 이후3,000마다5° 감소,25,000에서0°.
- 팔 속도 종료:10,000까지4rad/s,10,250부터250마다0.05 감소,20,000부터2rad/s.
- Holding의 보상 관련 일정 중 `arm_free_speed`를 삭제하고 나머지10개는 callable·points·interval까지 보존한다.

| 일정 | 값/끝점 |
| --- | --- |
| EEF free speed | 1.5→500:1.48→13,300:0.2m/s |
| Target free speed | 0.1→500:0.09→1,900:0.02m/s |
| Hold speed scale | 6,000까지0.05→10,000:0.02m/s |
| acceleration free | 3,000까지50→6,000:30,10,000까지유지→12,000:20m/s² |
| force change free | 3,000까지50→6,000:30,10,000까지유지→12,000:20N |
| moment change free | 3,000까지5→6,000:3,10,000까지유지→12,000:2Nm |
| obstacle force free | 3,000까지80→6,000:50,10,000까지유지→12,000:30N |
| acceleration weight | 1,000까지0→3,000:−0.01→6,000:−0.03,10,000까지유지→12,000:−0.05 |
| wrench weight | 1,000까지0→3,000:−0.03→6,000:−0.1 |
| obstacle weight | 1,000까지0→3,000:−0.02→6,000:−0.05,10,000까지유지→12,000:−0.1 |

보상 일정은 구간별250 iteration 단위 보간이며 지정 끝점에서 최종값을 적용한다. 방향과 개수의 reset 계약, 절대 iteration 복원·rewind 동작도 유지한다.

## 종료

성공 종료를 삭제하고 다음4개만 활성화한다.

| term | 조건 |
| --- | --- |
| object_fall_or_tilt | 활성 물체의 실제 bounds bottom<선반 표면−1cm, nonfinite bottom, 또는 tilt≥0.9rad |
| shelf_failure | 선반 속도6D norm>0.1 OR 손목 clearance<3cm OR 선반3D 변위>5cm; finger 검사 없음 |
| arm_joint_velocity | Arm6축 중 절댓값 속도가 현재4→2rad/s 임계값 초과 |
| timeout | 10초, time_out=True |

Holding의 push_fast 및 hand_velocity 종료를 추가하지 않는다. 목표를 안정적으로 유지해도 성공 종료/성공 보너스는 없으며 실패가 없으면 timeout까지 진행한다.

## 공통 학습 Metrics — 2026-11-09 후속

v0_2-Test와 아래 v0_2_1-Test 모두 사용한다. 기존 수집 함수는 성공 종료에서 호출되었으나 성공 종료 제거 후 호출 경로가 없어, 실제로는 장애물 개수/배치 완료만 기록되었다. 이제 timeout wrapper가 매 정책 step의 reset 직전 상태에서 수집하고 원래 `time_out`을 그대로 반환한다. 성공 종료를 복원하지 않으며 실패 조건과10초 제한은 유지한다.

| TensorBoard key (`Metrics/` 접두사) | 의미 |
| --- | --- |
| target_goal_distance_xy_m_mean | 에피소드 내 타겟–목표XY 거리 평균(m) |
| target_goal_distance_xy_m_final | reset 직전 마지막 샘플의 목표XY 거리(m) |
| target_goal_distance_xy_m_min | 에피소드 내 최소 목표XY 거리(m) |
| eef_linear_speed_m_s_mean | 실제 EEF점3D 선속력의 시간 평균(m/s) |
| eef_linear_speed_m_s_episode_max | 실제 EEF점3D 선속력의 에피소드 최대값(m/s) |
| target_linear_speed_m_s_mean | 타겟3D 선속력의 시간 평균(m/s) |
| target_linear_speed_m_s_episode_max | 타겟3D 선속력의 에피소드 최대값(m/s) |
| target_within_goal_radius_fraction_mean | 타겟XY 거리≤3cm인 샘플 비율(0–1) |

각 항은 **이번 reset에 포함된 에피소드별 통계의 평균**으로 출력한다. 최대값도 전 환경 통합 최대가 아니라 에피소드 최대들의 평균이다. 물체 속도는 타겟 기준이며 장애물 전체 평균이 아니다. 목표 반경 체류율은 XY 조건만 사용하므로 Holding의 자세·높이 유효성 또는 성공률과 다르다. 매 정책 step(20ms)에서 샘플링하므로 physics substep 순간 최대를 보장하지 않는다. 비유한 샘플은 평균·최대 집계에서 제외한다.

기존 `obstacle_actual_gray`, `obstacle_actual_white`, `layout_complete` Metrics는 삭제했다. Episode Reward·Termination 및 CurriculumManager 로그는 유지한다. 추가 센서 조회·가속도 readback·매 step CPU 전송 없이 기존 GPU pose/velocity 버퍼로 계산한다. 기존 미호출 force/moment·가속도 수집 코드는 제거했다. 선택 reset은 선택 환경의 통계만 초기화한다.

256환경·동일 씬의 활성/비활성 교차 측정에서 환경 step 시간 중앙값 증가는 약0.51%였다. 이는 단일 실행의 환경 step 측정이며 전체 PPO Collection Time이나2048환경의 보장은 아니다. [측정 및 검증 기록](../logs/2026-11-09_relative_ik_v0_2_1_metrics.md).

## v0_2_1-Test: 보상 분리와 속도 비용 제거

- Gym ID: `Inspire-Wrench-Refactor-Relative-IK-v0_2_1-Test`.
- 실험명: `inspire_wrench_refactor_relative_ik_v0_2_1-Test`.
- EnvCfg: `WrenchRefactorRelativeIKV0_2_1TestEnvCfg(WrenchRefactorRelativeIKV0_2TestEnvCfg)`.
- Rewards/Curriculum/PPO도 각각 v0_2-Test 설정을 직접 상속한다. runtime은 부모의 `WrenchRefactorRelativeIKV0_2TestEnv`를 공유한다.
- Scene·관측·행동·reset·센서·제어·목표·종료는 부모와 같다. 위 Metrics 개선도 부모로부터 함께 사용한다.

| 부모 term | 자식 변경 |
| --- | --- |
| object: weight−30, tilt+5×displacement | 제거하고 아래 두 항으로 분리 |
| object_tilt | 활성 타겟·장애물 기울기 비용, weight−30, free5°·fail0.9rad |
| obstacle_displacement | 활성 비타겟의 초기 대비3D 변위 제곱합, 합산 후 cap0.04, weight−150 |
| eef_linear_speed / eef_free_speed | 보상·관련 커리큘럼 삭제 |
| pushing_speed / pushing_free_speed | 보상·관련 커리큘럼 삭제 |
| arm_speed_excess / arm_free_speed | 부모에서 이미 삭제되어 자식에도 없음 |

두 분리 항은 기존 계산 함수를 그대로 사용하며 합산 보상은 기존 object와 같다(부동소수점 반올림 오차 범위). 부모의 object 보상과 EEF/타겟 속도 비용은 유지한다. 자식의 활성 보상15개·커리큘럼10개이며 나머지 계수/일정은 부모 그대로다. 속도 제곱 비용 `arm_joint_velocity`, 물체 가속도 비용, 팔 속도 종료는 별도이므로 유지한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-IK-v0_2_1-Test --num_envs 2048 --headless
```

## 실행

Isaac Lab Python 환경에서 workspace 루트 기준:

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-IK-v0_2-Test --num_envs 2048 --headless
```

기존 IK-v0_1과 정책 입력/모델 구조는 같지만 보상 과업은 달라진다. 검증 체크포인트는 학습 성능의 증거가 아니다. 실제 검사 명령·산출물과 미검증 범위는 [개발 로그](../logs/2026-11-09_relative_ik_v0_2_test.md)를 따른다.


## v0_2_1-Reset-Test: 그룹별 초기 조건 공유·물성 재추첨

Gym ID는 `Inspire-Wrench-Refactor-Relative-IK-v0_2_1-Reset-Test`, 실험명은 `inspire_wrench_refactor_relative_ik_v0_2_1-Reset-Test`다. `WrenchRefactorRelativeIKV0_2_1ResetTestEnvCfg`는 v0_2_1-Test를 직접 상속하며 보상·관측·액션·종료·커리큘럼·PPO 수치는 그대로다. runtime은 기존 v0_2-Test runtime을 상속해 명시적 seed reset 때 추가 난수 스트림과 저장 목록을 초기화한다.

초기화 규칙만 다음처럼 변경한다.

| 설정 | 초기 비교용 기본값 | 의미 |
| --- | ---: | --- |
| reset_size_groups | 16 | `env_id % 16`으로 같은 크기 구성을 공유;2048환경이면 그룹당128환경 |
| reset_pool_capacity | 8 | 그룹마다 저장할 배치·목표·초기 IK 묶음 개수 |
| reset_pool_refresh_interval | 32 | 목록이 찬 뒤 해당 그룹이 참여하는 reset 호출32회마다 한 묶음 교체 |

그룹 수·저장 수·교체 주기는 성능 측정으로 확정된 최적값이 아니라 변경 가능한 실험 기본값이다. 물체17슬롯의 각 크기는0.9–1.1 균등 추출하며 같은 그룹에서 슬롯별로 동일하다. 그룹끼리는 다른 구성을 사용하고 크기는 실행 중 고정한다. 형상 목록·충돌 물성·관절 한계·센서 구성은 유지한다.

처음에는 그룹이 reset에 참여할 때마다 부모의 원래 배치/IK 알고리즘으로 한 묶음을 만들어 최대8개를 채운다. 같은 그룹의 동시 reset 대상은 한 묶음을 공유한다. 이후 기존 묶음 중 균등 선택하며, 매32회 한 묶음을 새로 만들어 순환 교체한다. **장애물 개수8개라는 뜻이 아니다.** 기존 Gray/White 각각0–3개 분포와 목표 생성 규칙을 사용하지만, 환경 사이 초기 조건의 상관 및 재사용이 생긴다. 저장되는 것은 물체 상태·활성 목록·목표 변위·로봇 관절각·IK 진단/표시 정보이며 관측 노이즈와 물성은 저장해 재사용하지 않는다.

목표 방향을 포함한 배치/IK 파라미터가 바뀌면 전체 저장 목록을 비우고 현재 규칙으로 다시 채운다. iteration rewind에도 동일하게 적용한다. 실제 상태는 선택된 reset 환경에만 쓴다. 저장된 위치에는 환경 원점 이동을 적용하고 모든 물체/팔 속도를 초기화한다. 관측 스냅샷·노이즈·가시성·액션/보상 이력·Metrics는 기존 lifecycle에 따라 새로 만든다.

질량은 각 reset 환경의17개 물체별로 독립 균등 추첨(0.230–0.500kg×1.5)한다. 관성은 각 물체의 최초 형상별 관성에 질량 비율을 적용한다. 선반·물체·손의 정적/동적 마찰도 기존 균등 material bucket에서 다시 고른다. 이미 생성된 PhysX 버퍼의 대상 행만 갱신하며 재질 생성과 전체 readback을 반복하지 않는다. 선반 질량30kg과 로봇 질량·관절 설정은 그대로다. 부모 v0_2_1-Test는 여전히 startup에서만 물성을 정한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-Refactor-Relative-IK-v0_2_1-Reset-Test \
  --num_envs 2048 --headless
```

Hydra 설정 override 예: `env.reset_size_groups=16 env.reset_pool_capacity=8 env.reset_pool_refresh_interval=32`. 비교 시 초기 그룹별8회 생성 구간과 재사용 구간을 구분한다. 방향 커리큘럼이 바뀐 직후에도 생성 비용이 다시 발생한다. 사용자가 Collection Time을 비교할 예정이며 개선율은 아직 측정하지 않았다. [구현·검증 기록](../logs/2026-11-09_relative_ik_reset_test.md).


## v0_2_2-Test: 타겟 접촉 카운트 실험

`Inspire-Wrench-Refactor-Relative-IK-v0_2_2-Test`는 **일반 v0_2_1-Test를 직접 상속**한다. Reset-Test는 사용자가 효과가 크지 않다고 평가해 잠정 보류했으며, 새 환경에 그룹/캐시 reset을 적용하지 않는다. 실험명은 `inspire_wrench_refactor_relative_ik_v0_2_2-Test`다.

사용자 목적은 EEF/타겟 속도 초과 비용 없이 접촉 유지 보상으로 타겟의 빠른 이동·넘어짐을 줄일 수 있는지 비교하는 것이다. 이 가설의 성립은 아직 검증하지 않았다.

부모 대비 `hand_contact` 한 항만 변경한다. term 이름은 로그 연속성을 위해 유지하고, 함수는 `TargetContactMaintenance`, weight는 **0.1**, 접촉 임계값은0.01N이다.

| 단계 | 정확한 조건 |
| --- | --- |
| 원시 접촉 | 현재 타겟–손 접촉력의 벡터 합 크기≥0.01N, 최신 센서, 유한 힘 |
| 접촉 범위 | 타겟만 인정; 장애물/선반 접촉 제외 |
| EEF 높이 | 초기 선반 표면 위15cm 미만; 경계 포함 그 이상/비유한 값이면 즉시 불인정 |
| 목표 점유 | 접촉을 대신하지 않음; 목표3cm 안이어도 실제 접촉 필요 |
| 인정 창 | 현재 포함 최근3개 정책 step에서 원시 접촉2개 이상 |
| 카운트 | 인정된 창마다1 증가, 최대10 |
| 불인정 창 | 보상0;4회까지 카운트 보존,5회 연속 불인정이면0으로 초기화 |
| 에피소드 reset | 선택 환경의 history/count/misses/보상 캐시 초기화 |

최근 창의 판정이므로 현재 접촉이 없어도 직전2step 접촉이 남아 있으면 한 step 인정될 수 있다. 같은 step에 함수를 재호출해도 증가하지 않으며, step 평가가 누락되면 연속성을 보장할 수 없어 history/count를 초기화한다. 인정이 다시 나오면 연속 불인정 횟수는0으로 돌아간다.

RewardManager의 dt 적용 후 `0.1 × count × 0.02`가 지급되므로 최대 **0.02/step(초당1.0)**이다. 부모의 이진 보상 최대0.029/step보다 상한도 낮아진다. 처음부터 계속 접촉하면 원시 접촉 두 번째 step부터 count1로 지급한다. 목표 점유 보상 `goal_hold` 자체는 부모 그대로 유지한다.

Refactor 계열의 카운트 버퍼·선택 reset 구현을 재사용하되 사용자 확정에 따라 타겟 접촉만 사용하고 목표 점유 우회를 제거했다. 후속 요청으로 Contact 전용 `eef_height_limit=0.15`를 추가했다. 초기 선반 표면 기준 높이를 원시 접촉과 현재 창 인정에 모두 적용하므로 이전 접촉 이력이 남아 있어도15cm 이상에서는 즉시 보상0이고,5회 연속 불인정이면 카운트가 초기화된다. 다른 보상의 높이 설정은 바꾸지 않는다. 원래 Refactor 함수나 다른 환경의 보상은 수정하지 않았다. Scene·센서·관측·액션·목표·나머지 보상14개·종료4개·커리큘럼10개·PPO 수치는 부모와 같다. eef_linear_speed/pushing_speed/arm_speed_excess는 계속 비활성이다. 질량·마찰은 일반 부모처럼 startup에서만 설정된다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-Refactor-Relative-IK-v0_2_2-Test \
  --num_envs 2048 --headless
```

[구현·검증 기록](../logs/2026-11-09_relative_ik_v0_2_2_contact.md)
