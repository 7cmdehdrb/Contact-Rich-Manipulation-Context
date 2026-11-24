# Inspire-Sweep-Prof-Revision-v1 개발 명세

작성일: 2026-11-24. 최초에는 명세만 작성했으며, **후속 구현 요청에 따라 환경 구현·등록 및 CPU58개·GPU4환경 smoke·16환경 PPO1회 업데이트 검증을 완료했다.** 장기 행동 개선은 미검증이다. [구현·검증 기록](../../02_implementation/logs/2026-11-24_prof_revision_v1_implementation.md)을 따른다. 아래 예정 표현은 최초 설계 계약이며 실제 상태는 구현 기록을 우선한다.

`Inspire-Sweep-Prof-Revision-v0`를 직접 상속하여 팔 속도 종료 사건 비용을 복원하고, Contact Formation을 손가락별 거리 점수와 양방향 법선 유사도의 곱을 합산하는 보상으로 변경한다. [부모 계약](../../02_implementation/environments/PROF_REVISION_V0.md), [종료 패턴 진단](../../02_implementation/experiments/2026-11-24_prof_revision_stop_termination_diagnosis.md), [명세 작성 기록](../../02_implementation/logs/2026-11-24_prof_revision_v1_spec.md)을 함께 참조한다.

## 1. 확정 범위와 목적

| 항목 | v1 계약 |
| --- | --- |
| 부모 | `ProfRevisionEnvCfg` 직접 상속. Reach5cm v0가 부모가 아니므로 Reaching 허용 반경은 0.10m 유지 |
| 팔 종료 사건 보상 | `arm_joint_failure` 추가. `arm_joint_velocity` 종료가 발생한 transition에 일회 −3.0 |
| 손가락 보상 | 다섯 손가락 각각의 거리 점수 × 각도 유사도를 합산 |
| 각도 유사도 | 지문 Normal과 해당 패드→현재 추적 OBB 중심 방향의 코사인 제곱. 둘 다 EEF 좌표계로 표현 |
| 양면 허용 | 0°·180°에서 1, ±90°에서 0. 지문 면·손등 면을 동일하게 인정 |
| Formation weight | 기존 0.245의 정확히 1.5배인 **0.3675** |
| 거리 척도 | 부모의 `formation_distance_scale=0.05m`를 각 손가락의 거리 점수에 사용 |
| 집계 | **합산**. 1/5 평균화·합산 후 1로 clip·다른 보상 대비 비율 제한을 적용하지 않음 |
| 보존 | 다른 보상·종료·관측·제어·Scene/reset·PPO 수치와 기존 환경 동작 |

첫 번째 변경은 목표 근처에서 저렴한 속도 종료로 후속 손실을 끊는 유인을 줄이기 위한 것이다. 두 번째 변경은 거리만 줄이기 위해 손가락을 펴거나 접는 자세 중 물체 방향과 맞지 않는 자세의 점수를 낮추기 위한 것이다. 사용자 후속 지시에 따라 손등 방향도 인정하므로 이전 제안의 양의 코사인만 인정하는 식·각도 허용구간·접근 보상 혼합 epsilon은 사용하지 않는다. 감싸기 위치 분산항, 손가락별 접촉 강제, goal 정지·유지 보상은 추가하지 않는다.

## 2. 등록·상속과 코드 기준

명세 기준 workspace commit은 `19cac187345419cc08be097d7148052ddf3e383b`, 문서 저장소 commit은 `33858ea1086f22f1154eb799d934475af5de589f`다. 작업트리의 사용자 변경과 별도 진단 문서를 보존한다. 구현 착수 시 실제 작업트리를 다시 대조한다.

| 역할 | 예정 계약 |
| --- | --- |
| Gym ID | `Inspire-Sweep-Prof-Revision-v1` |
| EnvCfg | `ProfRevisionV1EnvCfg(ProfRevisionEnvCfg)` |
| Runtime | 부모 `ProfRevisionEnv` 재사용 |
| Rewards Cfg | `ProfRevisionV1RewardsCfg(ProfRevisionRewardsCfg)` |
| PPO | `ProfRevisionV1PPORunnerCfg(ProfRevisionPPORunnerCfg)` |
| PPO 차이 | `experiment_name='inspire_sweep_prof_revision_v1'`만 변경 |

확인한 실제 코드:

- [부모 EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/prof_revision_envs.py), [부모 PPO](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/prof_revision_ppo_cfg.py), [Gym 등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py).
- [현재 Formation 기하 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/prof_revision_geometry.py), [보상 callable](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/prof_revision.py), [보상 Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/prof_revision.py).
- [재사용할 arm_joint_failure](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/stabilize_sweep.py), [Single Contact v1의 기존 −3.0 적용](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_v0_envs.py), [부모 종료 Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations/prof_revision.py).

## 3. 팔 속도 종료 사건 비용

`arm_joint_velocity` 종료 term의 이미 계산된 boolean을 읽는다. 관절 속도를 보상 함수에서 다시 검사하거나 모든 실패 종료에 일괄 벌점을 부과하지 않는다.

```math
I_t=\mathbf{1}[\text{arm\_joint\_velocity termination at }t],\qquad
f_{\mathrm{arm\_joint\_failure}}(t)=\frac{I_t}{\Delta t}.
```

RewardManager는 weight와 policy dt를 곱하므로 실제 transition 기여는 다음과 같다.

```math
\Delta r_{\mathrm{arm\_joint\_failure},t}
=(-3.0)\frac{I_t}{\Delta t}\Delta t=-3.0I_t.
```

기존 함수 `arm_joint_failure(env)`와 weight `-3.0`을 그대로 재사용한다. `Delta t=0.02s`에서도 −0.06이 아닌 −3.0이 되어야 한다. 속도 종료가 없는 step에는 0이며, 자동 reset 이전 terminal transition에 한 번만 지급한다. 다른 실패나 timeout과 동시에 속도 종료가 참이면 이 항도 −3.0을 부과하고, 다른 비용은 기존대로 합산한다.

팔 속도 종료 임계값은 기존 **팔 6개 중 하나라도 절댓값이 1.0rad/s를 초과할 때**를 유지한다. 정확히 1.0rad/s는 이 term의 종료가 아니다. 손 관절 종료를 새로 만들지 않는다. 기존 연속 `arm_joint_velocity` 보상의 weight −0.03 및 cap100도 그대로다. 사건 비용 −3.0과 연속 속도 비용은 서로 다른 항이다.

## 4. 손가락 거리·각도 보상

### 4.1 평가점과 현재 OBB

손가락 순서는 부모와 같은 엄지·검지·중지·약지·소지다. 각 패드 대표점은 부모가 사용하는 distal tactile pad bounds의 x/y 중점·max-z이며, 임의의 fingertip 링크 원점으로 대체하지 않는다.

`p_i^E`는 EEF 좌표계의 패드 대표점, `c^E`는 같은 좌표계로 표현한 **현재 추적 가시 OBB 중심**이다. `_obb_live_pos_w`와 `_obb_live_quat_w`가 나타내는 초기 가시 조각의 현재 부착 위치·회전을 사용한다. 물체 COM, 전체 mesh 중심, 고정 관측용 `_obb_target_pos_w`로 대체하지 않는다. OBB 크기·추적 방식·가림 계산은 부모와 같다.

`n_i^E`는 패드 local +Z를 현재 패드 회전과 EEF 역회전으로 변환한 지문 면 바깥쪽 단위 Normal이다. 기존 패드 프레임을 사용하고 손가락 길이축·EEF 공통축·접촉 힘 방향과 혼동하지 않는다. 모든 방향 계산은 full3D이며 XY 투영을 하지 않는다.

### 4.2 거리 점수

OBB 회전을 `R_B^W`, 중심을 `c^W`, 크기를 `b`라 할 때 부모와 동일한 외부 거리를 사용한다.

```math
\mathbf{x}_i=(R_B^W)^\top(\mathbf{p}_i^W-\mathbf{c}^W),\qquad
d_i=\left\|\max\left(|\mathbf{x}_i|-\frac{\mathbf{b}}{2},0\right)\right\|_2.
```

max와 절댓값은 성분별 연산이다. OBB 표면·내부는 `d_i=0`이다. 이 값은 실제 collision mesh 접촉이나 관통 판정이 아니다.

```math
D_i=\frac{\sigma_d}{\sigma_d+d_i},\qquad \sigma_d=0.05\;\mathrm{m}.
```

`d_i=0, 0.05, 0.10m`에서 `D_i=1, 1/2, 1/3`이다. 원래 거리 자체를 양의 보상에 곱하지 않는다. 부모의 0.05m 수치를 유지하되 적용 위치가 거리 합의 분모에서 손가락별 분모로 바뀌므로, 부모와 동일한 거리 감쇠 곡선이라는 의미는 아니다.

### 4.3 EEF 좌표계의 양방향 각도 유사도

물체 방향 벡터는 EEF 원점→OBB 중심이 아니라 **각 패드→OBB 중심**이다. 두 벡터 모두 EEF 좌표계로 표현한다.

```math
\mathbf{v}_i^E=\mathbf{c}^E-\mathbf{p}_i^E,\qquad
s_i=\frac{(\mathbf{n}_i^E)^\top\mathbf{v}_i^E}
{\|\mathbf{n}_i^E\|_2\|\mathbf{v}_i^E\|_2},\qquad
A_i=s_i^2=\cos^2\theta_i.
```

| 각도 | 0° | ±45° | ±90° | ±135° | ±180° |
| --- | --- | --- | --- | --- | --- |
| `A_i` | 1 | 0.5 | 0 | 0.5 | 1 |

계산에는 acos가 필요하지 않다. 정규화 내적을 수치 오차 방지용으로 `[-1,1]`에 clip한 뒤 제곱한다. 음수를 0으로 먼저 자르거나 지문/손등별로 다른 계수를 적용하지 않는다. 각도 exponent는 2로 고정한다.

수치 보호는 `epsilon=1e-8`로 정한다. 방향 벡터 norm이 `1e-8m` 이하이면 방향이 정의되지 않으므로 해당 `A_i=0`으로 둔다. Normal norm이 `1e-8` 이하인 경우도 0이다. 분모를 먼저 안전하게 clamp하여 NaN을 만들지 않는다. 이는 각도 보상에 양의 바닥값을 더하는 epsilon 혼합과 다르다. 정상 quaternion에서 Normal은 단위 벡터이며, quaternion 유한성·정규화와 xyzw/wxyz 변환은 별도로 검증한다.

### 4.4 합산·가중치·dt

```math
F_{v1}=\sum_{i=1}^{5}D_iA_i,\qquad 0\le F_{v1}\le5,
```

```math
w_f=1.5\times0.245=0.3675,\qquad
\Delta r_{\mathrm{formation},t}=0.3675F_{v1,t}\Delta t.
```

term 이름 `contact_formation`을 유지한다. callable은 rate인 `F_v1`을 반환하며 dt로 나누지 않는다. 거리와 방향을 각각 합산한 뒤 곱하지 않고, 같은 손가락의 `D_i A_i`를 먼저 계산한다. 모든 손가락의 weight는 동일하다. 실제 접촉 여부·힘 크기·진행 여부로 추가 gate를 적용하지 않는다.

| 수치 | v0 | v1 |
| --- | --- | --- |
| raw 식 | `0.05/(0.05+sum(d_i))` | `sum(0.05/(0.05+d_i) * A_i)` |
| raw 최대 | 1 | 5 |
| weight | 0.245 | 0.3675 |
| 최대 보상률 | 0.245/s | 1.8375/s |
| policy step 0.02s의 최대 기여 | 0.0049 | 0.03675 |
| 10초 동안 이론적 최대 누적 | 2.45 | 18.375 |

**1.5배는 weight의 배율이다. 전체 이론적 최대는 합산 범위 변화까지 포함해 7.5배다.** 실제 평균 보상이나 행동 개선 폭을 1.5배로 단정하지 않는다. 사용자가 합산을 지정했으므로 이를 숨기기 위해 평균화하거나 weight를 5로 나누지 않는다. raw=1은 v1의 최대값이 아니며, 만점 달성의 어려움을 보상하는 의도와 수치 범위를 구분한다.

## 5. 부모와의 최종 차이 및 보존 계약

부모 16개 reward term을 보존하면서 `contact_formation`의 값·weight를 변경하고 `arm_joint_failure` 하나를 추가하여 총 17개로 구성한다. 기존 term 상대 순서는 유지하고 새 사건 비용은 마지막에 추가한다.

| 구성 | 보존 계약 |
| --- | --- |
| Reaching | 중심까지 3D 거리의 0.10m 초과분에 대한 signed 증분, weight4.9 |
| Sweep | 진행100·후퇴−20, boolean 접촉·힘 정렬·추적 가시 중심 기준 유지 |
| 면 선호 | 구역1/2 손등·구역3/4 손바닥, 선호1.5·반대0.7·미분류1 유지 |
| 다른 비용 | arm/hand action-rate·joint-velocity·action-limit, shelf_collision/failure, obstacle_contact/displacement, wrench_change, object_tilt의 callable·params·weight 보존 |
| 종료 | 팔 속도1.0rad/s 초과·낙하/전도·선반 실패·timeout·success 보존 |
| 성공 | 10초 timeout에서 목표 XY 거리 0.03m 이하, 동시 물리 실패 제외 |
| 관측 | policy108D·obstacles176D, Actor/Critic 입력 순서·frame·noise·clip·encoder 동일 |
| 시각 정보 경계 | Actor/Critic에 현재 OBB나 새 Normal 관측을 추가하지 않음. 현재 상태는 보상 계산에서만 사용 |
| 제어 | 팔6D OSC·손6D normalized 동작·Action 실행 clip·Last Action 의미 보존 |
| Scene/reset | 자산·물성·활성 물체 수·배치·가시 OBB 산출·Warp IK·목표 분포 보존 |
| 시간/PPO | sim dt0.01·decimation2·episode10s, 빈 curriculum, gamma0.98 및 나머지 PPO 수치 보존 |

새 각도 항은 Normal 부호에 대칭이므로 기존 손등 선호와 공존할 수 있다. 앞선 대화의 지문 면만 허용하는 제안에 대한 면 선호 변경 권고는 이번 최종 식에는 적용하지 않는다. 기존 구역별 선호 자체를 중립화하거나 뒤집지 않는다.

## 6. 구현 배치와 lifecycle 계약

현재 역할별 파일 구조를 유지한다. EnvCfg·Rewards Cfg·PPO 자식은 각 기존 `prof_revision` 파일에 추가하고 패키지 `__init__.py`에 새 Gym 등록을 추가한다. 버전별 디렉토리나 복제 runtime은 만들지 않는다.

`mdp/common/prof_revision_geometry.py`의 현재 step 기하 계산을 활용한다. 권장 방식은 v1에만 `formation_mode='distance_angle_sum'`을 선언하고, 기존 환경에는 필드 부재 시 부모 거리 합 계산을 그대로 실행하는 것이다. 새 계산은 같은 파일의 순수 배치 helper로 분리하고 `update_geometry`에서 v1 모드에만 호출한다. 부모의 원래 계산 경로·함수 결과를 보존한다. `contact_formation(env)`는 `_formation`을 반환하는 기존 callable을 재사용할 수 있다.

현재 추적 OBB와 손끝 Pose 갱신 후, reward 계산 전에 `_formation`을 계산한다. 센서별 body ID·offset을 매 step 재탐색하거나 CPU 왕복을 추가하지 않는다. reset/부분 reset 시 선택한 env의 값만 갱신한다. 보상 계산을 위해 step·물리·reset을 추가 호출하지 않는다.

`ProfRevision/formation_raw`에는 v1의 실제 `F_v1`, `ProfRevision/contact_formation_step_reward`에는 실제 weighted dt 기여를 기록한다. 기존 `finger_gap_sum_m`과 개별 gap 로그는 거리 진단용으로 유지한다. `Episode_Reward/arm_joint_failure`는 RewardManager가 생성하는 새 term 로그를 사용한다. 추가 진단에서 `D_i`, `A_i`, `D_i A_i`를 확인할 수 있어야 하며 정상 학습의 관측이나 물리 동작을 바꾸지 않는다.

RewardManager의 `Episode_Reward/*`는 최대 episode 길이로 정규화된 값이다. 부모와 같은 10초 설정에서 episode당 금액을 해석할 때 10을 곱한다. −3.0 사건 한 번만 발생한 episode의 `arm_joint_failure` 로그는 −0.3에 해당한다.

## 7. 구현 후 수용 검사

아래는 구현의 수용 조건이다. 명세 작성 당시에는 미실행이었으며, 후속 구현에서 실행한 검사와 장기 학습의 미검증 범위는 구현 기록에 구분했다.

1. 전체 설정 대조: 부모→v1의 차이를 두 보상 변경·v1 선택 field·등록/로그 이름으로 제한한다. 부모 v0와 Reach5cm v0의 기존 reward 결과·등록·구성 보존을 별도로 검증한다.
2. 사건 비용: 종료 boolean 거짓/참에서 0/−3.0, 여러 dt에서도 −3.0, 다른 실패 단독일 때 0, 동시 실패 시 합산, terminal 자동 reset 뒤 재지급 없음. 속도 threshold 직전·정확히1.0·직후도 확인한다.
3. 거리·방향: 표의 거리와 각도 값, Normal 반전 불변성, 모든 점/회전의 공통 강체 변환 불변성, XY가 아닌 3D 방향, EEF 원점 대신 손가락 위치가 방향 원점인지 확인한다.
4. 합산: 한 손가락만 `D=A=1`이면 raw1, 다섯 개 모두이면 raw5·step0.03675. 모든 방향 수직이면 raw0. 서로 다른 손가락의 거리/방향을 교차 결합하지 않는지 확인한다.
5. 경계·유한성: OBB 표면/내부 거리0, 중심과 패드 일치 시 A0, 아주 작은 벡터, quaternion 순서·회전, batch/부분 reset·cached 값의 유한성 및 최신성 확인.
6. Isaac Sim smoke: 동일 초기 scene에서 부모의 관측·action 해석·물리·종료 조건 보존, 실제 지문 Normal 및 세 가지 push 방향에서 개별 기여 확인. reward 합계와 반환 reward, 자동 reset 직전 로그가 일치해야 한다.
7. 학습 검증: 실제 재학습 후 방향별 속도 종료율·목표 진입률·목표 체류·timeout 성공률·손가락별 D/A/DA·실제 접촉 면·episode별 두 변경 항의 기여를 비교한다. 고정 checkpoint에 새 보상을 계산하는 것만으로 행동 개선을 입증하지 않는다.

관측/네트워크 shape가 동일하더라도 기존 v0 checkpoint는 이전 목적의 정책이다. 새 학습을 기본 비교로 하고, 별도 fine-tune 실험은 초기 checkpoint·optimizer 복원 여부를 명시한다. 명세 작성 때는 학습을 실행하지 않았고, 후속 구현 검증에서는 새 초기값으로 PPO1회만 실행했다. 장기 학습은 수행하지 않았다.

구현 후 등록된 환경의 학습 실행 명령:

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Prof-Revision-v1 --num_envs 2048 --headless
```

## 8. 알려진 한계

코사인 제곱은 지문/손등을 구별하지 않고, 가까운 여러 손가락이 한쪽 면에 모이는 자세도 허용한다. 실제 접촉·마찰·힘의 균형이나 안정적인 감싸기를 보장하는 식은 아니다. 추적 가시 OBB의 중심 방향은 실제 표면 법선과 다를 수 있다. 지문 패드 대표점은 손등 표면 대표점과도 다르므로, 양면 각도 대칭이 거리 평가점까지 대칭으로 바꾸는 것은 아니다.

Formation은 정지 중에도 양의 rate를 지급한다. 합산과 weight 증가로 목표 밖에서 자세 보상을 얻으며 머무는 유인이 커질 수 있으므로, 학습 후 진행·체류 행동과 보상 비중을 함께 확인한다. 이번 명세에서 이를 이유로 사용자 지정 weight·합산·다른 항을 임의로 조정하지 않는다. −3.0 사건 비용과 새 Formation이 기존 종료 패턴을 제거하거나 안정적인 자세를 학습시킨다는 성능 주장은 아직 미검증이다.
