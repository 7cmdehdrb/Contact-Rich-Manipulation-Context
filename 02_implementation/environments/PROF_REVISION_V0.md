# Prof Revision v0 학습 환경

2026-11-25: **[Hard v0_3](#prof-revision-hard-v0_3)** 추가. `v0_3` 직접 상속으로 목표 최소5cm·선반 경계까지, 장애물0–10개, 타겟8종을 사용한다.

[계통 비교·학습 위치·결과 메모](PROF_REVISION_FAMILY.md)

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

## Prof Revision v0_1

`Inspire-Sweep-Prof-Revision-v0_1`은 `ProfRevisionV0_1EnvCfg(ProfRevisionEnvCfg)`의 직접 자식이다. **유일한 환경 동작 차이는 `arm_joint_failure` 사건 비용의 추가**다. `ProfRevisionV0_1RewardsCfg(ProfRevisionRewardsCfg)`는 부모16개 reward를 그대로 상속하고 마지막에 기존 callable `arm_joint_failure`·weight−3.0을 추가한다. 실제 팔 속도 종료 transition에 일회−3.0이 지급되며, callable의 dt 나눗셈과 RewardManager dt가 상쇄된다. 종료 boolean은 기존 `arm_joint_velocity`를 읽고 속도 임계값1.0rad/s 초과는 유지한다.

Formation은 부모의 `0.05/(0.05+sum(d_i))`·weight0.245 그대로다. `formation_mode`를 추가하지 않는다. Reach10cm·Sweep100/−20·면 선호·관측108/176D·Scene/reset·물리·제어·성공/종료·빈 curriculum·PPO 수치도 부모와 같다. v1의 손가락 각도 보상은 상속하지 않으며 부모 v0·Reach5cm v0·v1을 보존한다.

Runtime은 기존 `ProfRevisionEnv`이고 `ProfRevisionV0_1PPORunnerCfg(ProfRevisionPPORunnerCfg)`는 로그 분리를 위해 `experiment_name=inspire_sweep_prof_revision_v0_1`만 변경한다. 선언은 기존 역할별 `prof_revision` 파일에 추가했다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Prof-Revision-v0_1 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/check_prof_revision.py \
  --task Inspire-Sweep-Prof-Revision-v0_1 --num-envs 4 --headless \
  --output outputs/prof_revision_v0_1_validation/smoke.json
```

정확한 실행 결과와 미검증 범위는 [개발·검증 기록](../logs/2026-11-24_prof_revision_v0_1_implementation.md)을 따른다.


## Prof Revision v0_2

`Inspire-Sweep-Prof-Revision-v0_2`는 `ProfRevisionV0_2EnvCfg(ProfRevisionEnvCfg)`로 v0을 직접 상속한다. runtime은 기존 `ProfRevisionEnv`를 재사용하며 `ProfRevisionV0_2RewardsCfg`와 `ProfRevisionV0_2PPORunnerCfg`를 사용한다. 로그 이름은 `inspire_sweep_prof_revision_v0_2`다.

- Sweep 진행은 기존 순수 `sweep_progress`로 교체한다. 손바닥·손등·구역에 무관하게 면 계수1, weight100이다. 기존 접촉 인정·목표 방향 힘 정렬·후퇴 비용을 보존한다.
- `arm_joint_velocity_margin`: 팔6관절 실제 절대 속도 최댓값 v에 대해 `clamp((v−0.8)/0.2,0,1)^2`, weight−3.0이다. RewardManager가 dt를 곱하는 연속 비용이다.
- `arm_joint_failure`: 기존 팔 속도 종료 flag를 읽고 `/dt`를 반환, weight−3.0으로 종료 시 일회−3이다. margin과 합산되어 dt0.02에서는 종료 transition에 새 두 항 합−3.06이다.

활성 보상은18개다. 기존 관절 속도 L2 비용도 유지한다. 속도 종료는 기존대로 **팔 관절 하나라도 절대 속도 >1.0 rad/s**이며 정확히1.0에서는 종료하지 않는다. Formation은 부모 거리 합 식·weight0.245이고 v1 각도 식은 사용하지 않는다. 관측·배치·자산·제어·성공3cm·10초 episode·빈 curriculum·PPO 수치를 모두 상속한다. PPO에서는 실험명만 변경한다.

[개발 명세](../../01_plan/environments/2026-11-24_PROF_REVISION_V0_2_SPEC.md) · [실제 검증과 한계](../logs/2026-11-24_prof_revision_v0_2_implementation.md).

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_2 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/play.py --task Inspire-Sweep-Prof-Revision-v0_2 --checkpoint /absolute/path/to/model.pt --num_envs 1 --real-time
```


## Prof Revision v0_3

`Inspire-Sweep-Prof-Revision-v0_3`는 `ProfRevisionV0_3EnvCfg(ProfRevisionEnvCfg)`로 v0을 직접 상속한다. `ProfRevisionV0_3RewardsCfg`·`ProfRevisionV0_3TerminationsCfg`를 사용하고 runtime은 기존 `ProfRevisionEnv`다. `ProfRevisionV0_3PPORunnerCfg`는 실험명만 `inspire_sweep_prof_revision_v0_3`으로 변경한다.

Sweep 진행은 순수 `sweep_progress`, weight100으로 손바닥·손등·구역의 면 계수를1로 통일한다. 접촉 인정과 목표 방향 힘 정렬은 유지한다. 기존 `arm_joint_velocity` 종료는 None으로 제거하고 `tcp_linear_velocity` 실패 종료를 추가한다.

**TCP는 UR5e 마지막 링크 `wrist_3_link`의 원점**이다. 이 원점의 월드3D 선속도 크기 `norm(body_link_lin_vel_w)`가 **4.0 m/s 이상(>=)**이면 policy step 끝에서 종료한다. 손 쪽 EEF offset, `axia80_link`, 질량중심 속도, 각속도나 개별 축 속도를 사용하지 않는다. Isaac Lab의 `body_link_vel_w` 구현은 COM 속도를 링크 원점으로 보정한다. `body_link_lin_vel_w`의 짧은 docstring에는 COM 표현이 남아 있지만 실제 반환 값은 이 보정된 링크 속도다.

성공은 부모의10초 timeout·목표 XY3cm 이내 조건이며, 같은 step의 낙하/전도·선반·TCP 속도 실패를 제외한다. 상속된 Manager 순서상 success가 새 TCP term보다 먼저 평가될 수 있어, v0_3 전용 성공 함수는 TCP term의 설정된 predicate를 현재 상태에 직접 적용한다. 이전 step flag를 읽거나 삭제된 관절 종료를 참조하지 않는다.

보상16개를 유지하고 새 종료 사건 비용이나0.8 rad/s margin은 추가하지 않는다. 기존 관절 속도 L2 비용은 유지한다. Formation 거리 합 식/weight0.245·관측108/176D·제어·자산·reset·물리·목표3cm·episode10초·빈 curriculum·PPO 수치를 부모에서 상속한다. v0_2와 다른 실험 분기다.

[구현·검증 기록](../logs/2026-11-24_prof_revision_v0_3_implementation.md).

2026-11-25 `model_7650` 실제 Play512회는389회 성공(75.98%), 구역3은39.33%였다. 이동 접촉96.60%이나 Sweep 보상99.86%가 초기2초에 집중되고 목표 진입 후 최종 실패62회가 확인됐다. 약지 중심 자세이며 다지 Formation의 충분성은 입증되지 않았다. 동일 seed 추가 재생에서 큰 접촉력과 거의0인 보정 F/T의 불일치가 재현돼 센서의 물리적 충실도는 미검증이다. 환경·보상·모델은 수정하지 않았다. [정량 보고서·그래프·원시 데이터](../experiments/2026-11-25_prof_revision_v0_3_play_analysis.md) · [계측·검증 기록](../logs/2026-11-25_prof_revision_v0_3_play_analysis.md).

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/play.py --task Inspire-Sweep-Prof-Revision-v0_3 --checkpoint /absolute/path/to/model.pt --num_envs 1 --real-time
```


## Prof Revision Hard v0_3

`Inspire-Sweep-Prof-Revision-Hard-v0_3`는 `ProfRevisionHardV0_3EnvCfg(ProfRevisionV0_3EnvCfg)`의 직접 자식이다. 보상·종료·초기 시각 snapshot·촉각/F/T·관측108/176D·행동12D·물리·PPO는 v0_3를 상속한다. 다음 과업 분포만 확장했다.

| 항목 | Hard 동작 |
| --- | --- |
| 목표 거리 | 타겟 root XY에서 최소5cm. 인위적 최대 거리 없음. 전 방향 각도 균등, 방향별 shape-safe 선반 경계까지 거리 균등 |
| 안전 영역 | 선반 XY `[-.2,.2]×[-.5,.5]m`, 실제 형상·scale·reset yaw·중심 offset을 고려하고 목표 벽 여유2cm 유지 |
| 장애물 | 매 reset 정수0–10개 균등,16개 고정 후보 중 중복 없이 선택 |
| 저비용 배치 | 4,000개 캐시 셀, 큰 box 우선 삽입·객체별 무작위 셀 우선순위, 셀 전체 범위의 연속 jitter. 유효 빈 영역에 분산하며 상호·벽1cm 여유와 기존 +X 압출 접근·밀기 경로 보존 |
| 장애물 자세 | Hard의 밀집 배치에 맞춰 수직축0/90/180/270도에서 선택. 원통·곡면도 실제 bounds box로 보수적 검사 |
| 타겟 종 | cylinder·cube·mug·bottle·003_cracker_box·004_sugar_box·005_tomato_soup_can·002_master_chef_can |
| 형상 수명 | 환경 생성 시 종·scale0.9–1.1 선택, reset에는 pose만 변경. 재선택·recooking 비용 없음 |
| 가시성 | 타겟1 + 장애물10개를 정확한 정면 가림 계산에 포함. 관측16슬롯 초과 시 가장 넓은16조각 유지, 물리 장애물 수 보존 |

Runtime `ProfRevisionEnv`와 물리 풀17개를 그대로 사용한다. `ProfRevisionHardSceneCfg`·`ProfRevisionHardEventsCfg` 및 공통 `ProfRevisionHardLayout`이 Hard 차이를 담당한다. PPO 자식은 `experiment_name=inspire_sweep_prof_revision_hard_v0_3`만 변경한다. 원래 v0_3의 목표6–12cm·원통·장애물0–6개는 유지된다.

Windows11의 프로젝트 루트에서 기존 Isaac Lab 환경을 활성화한 뒤 실행한다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-Hard-v0_3 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/check_prof_revision_hard.py --headless --num-envs 64
```

초기 구현은36개 관련 자동 검사·부모4환경 live 회귀·Hard64환경20회 reset/510step·204,800개 sampler stress를 통과했다. 실제 목표 표본은5.00–47.07cm,2048행 sampler 중앙값은 부모16.36ms/Hard2.46ms였다. 이 값은 배치 helper 실행 시간이며 전체 학습 시간과 구분한다.

2026-11-25 후속 사용자 관찰에 따라 경계 방향 채움으로 생기던 코너·일렬 편향을 수정했다. 캐시 셀은 충돌 검사 가속용으로 유지하고, 각 객체가 공간 방향과 무관한 무작위 셀 우선순위를 사용한다. 요청 개수·물체 선택·yaw·목표 분포·밀기 공간·여유·최대8회 재시도는 보존한다. 실제 자산으로 수정 전·후 각각206,848개 배치 검사에서 실패 없이 개수를 유지했고,2048행 중앙값은2.72→2.74ms였다.37개 관련 검사·64환경20회 reset/100step도 통과했다. [배치 전후 그림](../../../../outputs/prof_revision_hard_scatter_20261125/before_after.png) · [후속 수정·전체 계약 대조](../logs/2026-11-25_prof_revision_hard_v0_3_implementation.md#후속-장애물-분산-배치-수정). Hard의 장기 성공률은 아직 검증하지 않았다.


## Prof Revision v0_3_1

`Inspire-Sweep-Prof-Revision-v0_3_1`는 `ProfRevisionV0_3_1EnvCfg(ProfRevisionV0_3EnvCfg)`의 직접 자식이다. **유일한 환경 설정 차이는 `formation_mode='distance_angle_sum'`**이다. 실제 등록된 Prof Revision v1의 손가락별 거리 점수 × pad normal과 타겟 중심 방향의 양방향 `cos²` 정렬 점수를5개 손가락에 대해 합산한다. 평균화하지 않는다.

Formation 거리 scale0.05m와 weight0.245를 부모에서 유지한다. raw 범위는0–5이며 policy dt0.02s에서 최대 step 기여는0.0245다. v1의 weight0.3675·관절 속도 종료 사건 비용은 가져오지 않는다. 기존 v0_3의 TCP4m/s 종료·성공·전체16개 보상·관측108/176D·행동12D·Scene/reset·목표6–12cm·원통 타겟·장애물0–6개·물리·빈 curriculum·PPO를 모두 상속한다. Hard의 과업 분포는 사용하지 않는다.

사용자가 언급한 `Inspire-Sweep-Prof-Revision-Hard-v1`은 현재 저장소에 없으며, 설명에 맞는 `Inspire-Sweep-Prof-Revision-v1`의 손가락 보상식만 재사용했다. 원래 v0_3 및 Hard v0_3는 보존한다. PPO 자식은 `ProfRevisionV0_3_1PPORunnerCfg(ProfRevisionV0_3PPORunnerCfg)`, 로그 이름은 `inspire_sweep_prof_revision_v0_3_1`이다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3_1 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/check_prof_revision.py --task Inspire-Sweep-Prof-Revision-v0_3_1 --headless --num-envs 4 --output outputs/prof_revision_v0_3_1_validation/smoke.json
```

관련 검사32개·새 환경4개 실제 reset/step·전체 Manager/PPO 대조·부모 변경 전후 대조·16환경 PPO1회 업데이트를 통과했다. 장기 자세 개선과 성공률은 미검증이다. [상세 수식·구현·검증](../logs/2026-11-25_prof_revision_v0_3_1_implementation.md).
