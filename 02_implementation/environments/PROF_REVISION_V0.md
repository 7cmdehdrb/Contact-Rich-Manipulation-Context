# Prof Revision v0 학습 환경

`Inspire-Sweep-Prof-Revision-v0`는 Single Contact v0을 기능 기준으로 만든 독립 환경이다. 초기 정면 가시 OBB, 손끝 Pose, 증분 Reaching과 Contact Formation을 사용한다. 초기 시각 이후 Actor와 Critic은 고정 OBB snapshot을 현재 EEF로만 변환하고, 촉각·손목 F/T와 현재 로봇 상태를 관측한다. 보상·성공은 같은 초기 가시 조각을 물체에 고정해 추적한다.

개발 계약의 수식·모든 보존 조건은 [개발 명세](../../01_plan/environments/2026-11-23_PROF_REVISION_V0_SPEC.md), 실제 실행 결과와 명세 해석은 [개발 로그](../logs/2026-11-23_prof_revision_v0_implementation.md)를 따른다.

## 등록과 구성

| 역할 | 구현 |
| --- | --- |
| Gym ID | `Inspire-Sweep-Prof-Revision-v0` |
| EnvCfg | `envs/prof_revision_envs.py:ProfRevisionEnvCfg`, `ManagerBasedRLEnvCfg` 직접 상속 |
| Runtime | `runtime/prof_revision.py:ProfRevisionEnv`, `ManagerBasedRLEnv` 직접 상속 |
| Scene | `assets/scenes/prof_revision.py:ProfRevisionSceneCfg`, `InteractiveSceneCfg` 직접 상속 |
| PPO | `agent/prof_revision_ppo_cfg.py:ProfRevisionPPORunnerCfg`, 공통 수치 보호 runner 사용 |
| 모델 | `agent/prof_revision_models.py:ProfRevisionModel`, `MLPModel` 직접 상속 |
| State | `mdp/common/prof_revision_state.py:ProfRevisionState`, 독립 선언 |
| 로그 이름 | `inspire_sweep_prof_revision_v0` |

기존 환경의 EnvCfg/runtime/state/model을 상속하지 않는다. 자산 factory·기존 Action term·접촉 reduction·tactile reader·배치/IK helper는 재사용한다. 기존 Single Contact v0/v1/Zone3 설정과 등록은 보존한다.

## 관측과 제어

직접 입력은 **팔 위치6 → 팔 속도6 → EEF Pose7 → 손 구동 관절 위치6 → 손끝 Pose35 → 타겟 OBB10 → 목표3 → Last Action12 → tactile17 → wrench6**의108D다. 손 관절은 기존 `HAND_DRIVE_JOINT_NAMES` 순서(엄지 굽힘·검지·중지·약지·소지·엄지 대립)의 실제 rad 값이다. 손 관절 `[19:25]` 다음에 손끝 `[25:60]`, 타겟 `[60:70]`이 위치한다.

타겟 OBB는 `[x,y,z,w,d,h,qx,qy,qz,qw]`10D, 장애물은 `[mask,x,y,z,w,d,h,qx,qy,qz,qw]×16=176D`다. encoder는 **176→128→64→32→16**이며 Actor/Critic이 각각 독립 학습한다. 본체 입력124D·export 입력284D다. 비유효 슬롯은 quaternion 포함 전체11D를0으로 만든다.

EEF Pose는 기존 Base 기준 wxyz quaternion이다. 손끝은 엄지→검지→중지→약지→소지 순서의 EEF 기준 xyzw Pose다. 다섯 손가락 모두 실제 오른손 distal tactile pad bounds의 x/y 중점·max-z를 원점으로 하고 pad 축을 유지한다. body index와 offset은 시작 시 캐시하고 매 policy step에 한 번 배치 계산하여 보상과 공유한다. 기존 두 고정 `finger_frame` probe는 별개 선반 비용용으로 보존한다.

OBB는 reset 때 선반 +X에서−X 방향의 가시 구간으로 산출한다. 현재 필터는 기존 수준의2cm·20%를 저비용 구간 비교로 유지한다. 가림 계산에 모든 활성 물체가 참여하고 주차 후보는 제외한다. 타겟은 가장 넓은 가시 조각1개, 장애물은 조각별16슬롯이다. 관측용 Box는 episode 동안 월드 고정이다. 보상용 Box는 초기 target-link-local attachment를 따라 병진·회전한다. OBB 방향은 EEF 상대 full3D quaternion을 normalize·부호 canonicalize한 xyzw이며 손끝과 같은 규칙이다. 크기는 OBB 고유 축의 길이를 유지한다. reset 가시 footprint fit 내부의 upright yaw는 유지하고 관측 heading 축약은 제거했다.

제어는 팔6D OSC·손6D normalized `[0,1]`, 총12D다. wrapper action clip 없이 Action term에서 실행 범위를 적용한다. Last Action 관측 clip과 원본 action 비용·cap은 기존 v0과 같다. F/T는 기존 noise 후±150N/±8Nm clip을 적용하고 축별 한계로 나눈다. 기존66D/64D 및 이전 Prof Revision99D/128D checkpoint는 직접 resume하지 않는다. 관측·인코더 shape가 달라 새 학습을 시작한다.

## 보상과 종료

| 항목 | 실제 동작 |
| --- | --- |
| Reaching | 현재 EEF–추적 가시 OBB 중심의10cm 초과 거리 감소/증가에 대칭 기여 `4.9×(이전 초과분−현재 초과분)` |
| Contact Formation | 손끝5개에서 추적 OBB 외부까지 거리 합 S. 내부/표면은 거리0. 실제 step 기여 `0.245×0.05/(0.05+S)×0.02` |
| Sweep 진행 | 추적 가시 중심–목표 XY 거리 감소량×boolean 접촉×기존 힘 정렬×면 선호, weight100 |
| Sweep 후퇴 | 같은 거리 증가량의 비용, weight−20 |
| 높이 | Sweep 접촉 인정의 EEF12cm 조건 제거 |
| 기존 비용 | Action rate/limit·관절 속도·선반 충돌/실패·장애물 접촉/변위·F/T 변화·물체 전도 보존 |
| 성공 | 10초 timeout에서 추적 가시 중심의 목표 XY 거리3cm 이하, 동시 물리 실패 제외 |
| 실패 | 활성 물체 낙하/전도·선반 실패·팔 관절 속도1rad/s 초과, 기존 계약 |

Reaching/Sweep 거리 증분과 사건 비용은 callable의 dt 나눗셈과 RewardManager dt가 상쇄된다. Formation은 bounded rate다. Formation weight는0.10m/s 접근 속도에서 최대 기여가 Reach 절반이 되도록 잡았으며, 정지할 때도 양수일 수 있다. v1의 signed 힘 방향·구역별 접근점·추가 팔 종료 비용은 사용하지 않는다.

Scene의 자산·물성, 타겟 원통, 활성 장애물 최대6개, 전 방향 목표6–12cm·초기 타겟 반경2cm·단일 Warp IK, 물리0.01s/정책0.02s,10초 episode, 빈 curriculum, 본체256/128/64와 PPO 설정을 유지한다.

## 실행과 검증

Workspace 루트에서 기존 Isaac Lab 환경을 활성화한 뒤 실행한다. 원본 선반과 YCB 자산에 접근할 수 있어야 하며, 경로는 기존 `INSPIRE_SWEEP_SHELF_USD_PATH` 또는 자산 루트 설정을 사용한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Prof-Revision-v0 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/check_prof_revision.py --headless
```

Collection 완료 기준은2048환경×36policy step·iteration0부터 연속32회 모두10초 미만이며 권장은5초 이하이다. 자동reset·OBB 계산·추론·물리·센서·보상·관측을 포함하고 PPO update는 별도 보고한다. `scripts/summarize_prof_revision_validation.py`는 실제 로그·TensorBoard·checkpoint의 시간·유한성·encoder 변경을 검사한다. GPU smoke와 CPU 검증, 실제 collection 결과·미검증 범위의 최종 상태는 위 개발 로그에 기록한다.

2026-11-24 관측 정정 후 CPU202개·GPU4환경 smoke·2048환경×36step×32회 재검증을 통과했다. collection 평균5.7823초·최대6.609초로 전부10초 미만이며 권장5초는 미달이다. 단기 loss/모델/optimizer/checkpoint 유한성을 확인했고 장기 성공률은 미검증이다.

## Reach5cm v0

`Inspire-Sweep-Prof-Revision-Reach5cm-v0`는 `ProfRevisionReach5cmEnvCfg(ProfRevisionEnvCfg)`의 직접 자식이다. **유일한 환경 동작 차이는 `reach_near_radius=0.10→0.05m`**다. 부모의 Reach식·weight4.9·가시 OBB 목표점·Formation·Sweep·관측108/176D·성공3cm·나머지 Scene/Manager/runtime/PPO 설정을 그대로 상속한다. 부모10cm는 유지한다.

Runtime은 부모 `ProfRevisionEnv`를 재사용한다. `ProfRevisionReach5cmPPORunnerCfg(ProfRevisionPPORunnerCfg)`는 로그 분리를 위해 `experiment_name=inspire_sweep_prof_revision_reach5cm_v0`만 변경한다. 클래스는 기존 `envs/prof_revision_envs.py`·`agent/prof_revision_ppo_cfg.py`에 추가했다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Prof-Revision-Reach5cm-v0 --num_envs 2048 --headless
```

2026-11-24 사용자 지시로 GPU·Isaac Sim·학습을 실행하지 않았다. 표준 라이브러리 AST/해시 대조에서 부모 직접 상속·단일 field override·동일 runtime·기존 코드 보존·등록 경로를 확인했다. 위 명령은 실행 예시이며 이 자식의 collection 시간이나 학습 결과를 검증한 기록이 아니다.

## Prof Revision v1

`Inspire-Sweep-Prof-Revision-v1`은 `ProfRevisionV1EnvCfg(ProfRevisionEnvCfg)`의 직접 자식이다. `ProfRevisionV1RewardsCfg(ProfRevisionRewardsCfg)`는 기존16개 term의 상대 순서를 유지하면서 `contact_formation`을 변경하고 마지막에 `arm_joint_failure`를 추가한다. 최종17개 term이며 runtime은 부모 `ProfRevisionEnv`를 재사용한다. `ProfRevisionV1PPORunnerCfg(ProfRevisionPPORunnerCfg)`는 `experiment_name=inspire_sweep_prof_revision_v1`만 변경한다.

팔 종료 사건 비용은 기존 `arm_joint_failure(env)`로 `termination_manager.get_term('arm_joint_velocity') / step_dt`를 읽고 weight−3.0을 적용하여 실제 종료 step에 일회−3.0이다. 팔 속도 종료 임계값1.0rad/s 초과와 연속 속도 비용−0.03·cap100은 보존한다.

Formation은 지문 패드 대표점에서 현재 추적 가시 OBB까지 부모와 같은 외부 거리 `d_i`를 사용한다. 지문 패드 local +Z Normal과 각 패드→현재 추적 OBB 중심 방향을 EEF 좌표계에서 비교한다.

```math
F_{v1}=\sum_{i=1}^{5}\frac{0.05}{0.05+d_i}\cos^2\theta_i,\qquad
\Delta r_{\mathrm{formation},t}=0.3675F_{v1,t}\Delta t.
```

0°/180°는1·±90°는0으로 지문/손등을 모두 인정한다. raw 범위0–5, weight0.3675이며 평균화하지 않는다. 최대 보상률1.8375/s·policy step0.02s에서 최대0.03675로 전체 이론적 최대는 부모의7.5배다. 방향/Normal norm이1e−8 이하이면 그 손가락 각도 점수는0이다. 실제 접촉·힘·이동 gate와 감싸기 분산항은 추가하지 않았다.

v1만 `formation_mode='distance_angle_sum'`을 선언한다. 공유 기하 함수는 해당 모드에서만 새 식을 사용하고, 필드가 없는 부모·Reach5cm는 원래 계산을 유지한다. Reach10cm·성공3cm·기존 손바닥/손등 면 선호·관측108/176D·Scene/reset·제어·PPO 수치는 부모와 같다. 현재 물체 상태를 Actor/Critic 입력에 추가하지 않는다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Prof-Revision-v1 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/check_prof_revision.py \
  --task Inspire-Sweep-Prof-Revision-v1 --num-envs 4 --headless \
  --output outputs/prof_revision_v1_validation/smoke.json
```

CPU58개·GPU4환경 smoke·16환경PPO1회 업데이트 검증을 통과했다. 별도 v0 고정 정책을 사용한 실제 팔 속도 종료4건에서 일회−3.0을 확인했다. 부모/v1 전체 설정 및 PPO 대조, Reach5cm 보존, 부분/자동reset·frozen Actor OBB·현재 OBB 추적·보상 합계·JIT export를 검증했다. 장기 자세/성공률 개선·2048환경 collection은 미검증이다. [정확한 명세](../../01_plan/environments/2026-11-24_PROF_REVISION_V1_SPEC.md) · [실행·검증 기록](../logs/2026-11-24_prof_revision_v1_implementation.md).
