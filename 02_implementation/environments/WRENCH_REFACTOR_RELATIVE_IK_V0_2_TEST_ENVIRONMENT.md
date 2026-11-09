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

## 실행

Isaac Lab Python 환경에서 workspace 루트 기준:

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-IK-v0_2-Test --num_envs 2048 --headless
```

기존 IK-v0_1과 정책 입력/모델 구조는 같지만 보상 과업은 달라진다. 검증 체크포인트는 학습 성능의 증거가 아니다. 실제 검사 명령·산출물과 미검증 범위는 [개발 로그](../logs/2026-11-09_relative_ik_v0_2_test.md)를 따른다.
