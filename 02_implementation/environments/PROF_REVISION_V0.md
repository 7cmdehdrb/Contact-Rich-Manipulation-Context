# Prof Revision v0 학습 환경

2026-11-27: **[v0_3_4](#prof-revision-v0_3_4)** 추가. 일반 v0_3_3 상속, retreat−100·팔/손 비용 통합·접촉과 방향 판정 통일·허용 접촉5N/손목 변화5N·0.3Nm.

2026-11-26: **Contact Formation 사진 환경**은 [별도 standalone 실행 파일](../logs/2026-11-26_contact_formation_photography.md)로 제공한다. v0_3_2 학습 설정·리워드·Gym 등록은 변경하지 않는다. 후속: 위·옆 접근 × 가까움·6cm 추가 이격의4개 자세를 버튼으로 선택한다(`--pose`, `--retreat-cm`).

2026-11-26: **[v0_3_2](#prof-revision-v0_3_2)** 추가. v0_3_1 직접 상속, 거리 기반 힘 방향 완화·정밀 거리 증분·보상 비중 변경을 적용한다.

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

초기 구현 시 관련 검사32개·새 환경4개 실제 reset/step·전체 Manager/PPO 대조·부모 변경 전후 대조·16환경 PPO1회 업데이트를 통과했다. [상세 수식·구현·검증](../logs/2026-11-25_prof_revision_v0_3_1_implementation.md).

2026-11-26 `model_15550`을 seed42·43/64환경/첫4완료episode로 평가했다.334/512성공(65.23%),491건 목표 진입 중157건 최종 실패였다. 방향별 성공률은−X83.87%·+Y73.01%·+X51.11%·−Y54.82%다. 거리×각도 합산 수식은 일치하지만 Formation이 양의 예산46.2%·비접촉 지급22.3%를 차지해 실제 손가락 접촉·최종 정착과 구분해야 한다. 환경/weight는 바꾸지 않았다. [방향별 최종 위치·접촉·16항·손가락 보고서](../experiments/2026-11-26_prof_revision_v0_3_1_play_analysis.md) · [검증](../logs/2026-11-26_prof_revision_v0_3_1_play_analysis.md). 장기 최종 성능과 부모 대비 개선은 이 특정 checkpoint 평가로 확정하지 않는다.

## Prof Revision v0_3_2

`Inspire-Sweep-Prof-Revision-v0_3_2`는 `ProfRevisionV0_3_2EnvCfg(ProfRevisionV0_3_1EnvCfg)`로 직접 상속한다. Runtime은 `ProfRevisionV0_3_2Env(ProfRevisionEnv)`, 상태는 `ProfRevisionPrecisionState(ProfRevisionState)`다. 원통 타겟·목표6–12cm·장애물0–6개·기존 배치·초기 관측·108/176D 입력·12D 행동·물리·성공3cm·10초episode·TCP4m/s 종료와 PPO 수치를 보존한다.

| 보상 항 | weight | 변경 |
| --- | ---: | --- |
| sweep_progress | +100 | 가중 거리H 개선×유효 현재 접촉×최근2/3접촉×B |
| sweep_retreat | −40 | 동일H 증가; 접촉·힘과 무관 |
| reaching | +9.8 | 기존 signed 거리 증분 함수·params 유지 |
| contact_formation | +0.1715 | 부모 손가락별 거리×양방향cos² 합 유지 |
| obstacle_displacement | −300 | 기존 reset 대비3D 제곱변위 합·raw cap0.04m² 유지 |

나머지11개 보상과 빈curriculum은 부모 그대로다. `S(u)=3u²−2u³`와clip을 이용해 현재 목표 XY 거리3–6cm 사이에서 힘 정렬 비중을1→0으로 낮춘다. `B=1−alpha+alpha*A`,3cm 이하B=1,6cm 이상B=A다. 힘이 반대여도 가까워지는 실제 이동·유효 접촉이 있어야 양의 보상을 받는다.

```math
u=\mathrm{clip}(d/0.06,0,1),\qquad
H(d)=d+0.06\left(u-u^3+\frac{u^4}{2}\right),\qquad
\Delta H=H(d_{t-1})-H(d_t)
```

```math
r_{\mathrm{progress}}=100\max(\Delta H,0)CB,\qquad
r_{\mathrm{retreat}}=-40\max(-\Delta H,0)
```

H의 미분은 중심2·3cm1.5·6cm 이상1이며, 중심까지 거리 개선·이탈 민감도가 연속적으로 변한다. 위 식은dt 적용 후의step 보상이고, callable은 거리 증분을dt로 나눈다. +100/−40은 비대칭이므로 닫힌 왕복 무이익을 보장하지 않는다. 정지 자체의 양의 보상은 추가하지 않는다.

기존 거리·힘 정렬 로그를 보존하고 `ProfRevisionPrecision/`에alpha·거리 민감도·B·정밀 진행/이탈·거리 구간 비중·설정값을 추가했다. 자동reset 전 terminal 값을 기록한다. PPO는v0_3_1 직접 자식인 `ProfRevisionV0_3_2PPORunnerCfg`로 실험명만 `inspire_sweep_prof_revision_v0_3_2`다.

[개발명세·cap 조사](../../01_plan/environments/2026-11-26_PROF_REVISION_V0_3_2_SPEC.md) · [최종 대조·실행 검증](../logs/2026-11-26_prof_revision_v0_3_2_implementation.md). 장기 성공률·감속/정착 개선은 미검증이다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3_2 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/check_prof_revision_precision.py --headless --num-envs 16
```

## Prof Revision v0_3_3

`Inspire-Sweep-Prof-Revision-v0_3_3`은 `ProfRevisionV0_3_3EnvCfg(ProfRevisionV0_3_2EnvCfg)`로 직접 상속한다. 목표 근처 왕복으로 진행 보상을 반복 획득하는 행동을 억제하도록 `ProfRevisionV0_3_3RewardsCfg(ProfRevisionV0_3_2RewardsCfg)`에서 `sweep_retreat` weight만 −40에서 −120으로 높인다. 함수 `precision_sweep_retreat`와 params는 그대로다.

동일한 가중 거리 H를 왕복할 때 Sweep 두 항의 합은 최대 `(100−120)×ΔH = −20×ΔH`다. 이는 Sweep 왕복 이익 제거이며 Formation 등 다른 보상을 포함한 전체 수익이나 실제 정책의 흔들림 완전 제거를 보장하지 않는다. 장기학습 행동 개선은 미검증이다.

Scene·Command·Event/reset·Observation·Action·나머지15개 Reward·Termination·빈 Curriculum·정밀 거리/접촉/힘 gate·성공 XY 3cm·TCP4m/s 종료·telemetry를 모두 보존한다. Runtime은 부모의 `ProfRevisionV0_3_2Env`를 그대로 사용한다. PPO는 `ProfRevisionV0_3_3PPORunnerCfg(ProfRevisionV0_3_2PPORunnerCfg)`이며 실험명만 `inspire_sweep_prof_revision_v0_3_3`이다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3_3 --num_envs 2048 --headless
```

[변경 근거·최종 계약·검증 범위](../logs/2026-11-26_prof_revision_v0_3_3_implementation.md).

## Prof Revision Hard v0_3_3

`Inspire-Sweep-Prof-Revision-Hard-v0_3_3`은 `ProfRevisionHardV0_3_3EnvCfg(ProfRevisionV0_3_3EnvCfg)`다. 이미 존재하는 일반 v0_3_3과 구분하여 Hard 이름을 사용한다. 보상은 일반 v0_3_3과 전체 동일하며 역방향−120·진행+100·Reach9.8·Formation0.1715·장애물변위−300(cap0.04)이다.

Scene 생성 조건만 기존 `ProfRevisionHardV0_3EnvCfg`에서 재사용한다. `ProfRevisionHardSceneCfg`로 타겟8종을 선택하고 `ProfRevisionHardEventsCfg`의 reset/geometry 초기화를 적용한다. 목표 최소5cm·상한 없음(선반 유효 영역 안), 장애물0–10개, 배치 격자1cm와 capacity10을 사용한다. 기존17개 물리 바디/16개 장애물 관측 슬롯은 유지된다. Hard의 초기화 및 reset 이벤트는 Scene 분포 구현에 필수이며 보상 변경이 아니다.

관측·행동·물리·정밀 상태·성공3cm·TCP4m/s 종료·커리큘럼·runtime은 일반 v0_3_3 그대로다. runtime `ProfRevisionV0_3_2Env`를 재사용한다. PPO는 `ProfRevisionHardV0_3_3PPORunnerCfg(ProfRevisionV0_3_3PPORunnerCfg)`이며 실험명만 `inspire_sweep_prof_revision_hard_v0_3_3`이다. 장기학습 성능은 미검증이다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-Hard-v0_3_3 --num_envs 2048 --headless
```

[최종 대조·검증](../logs/2026-11-26_prof_revision_hard_v0_3_3_implementation.md).

## Prof Revision v0_3_3-IK

`Inspire-Sweep-Prof-Revision-v0_3_3-IK`은 `ProfRevisionV0_3_3IKEnvCfg(ProfRevisionV0_3_3EnvCfg)`다. 일반 v0_3_3을 직접 상속하며 Hard 분포를 가져오지 않는다. 변경은 시작 팔 관절 상태의 선택뿐이다. 손가락 초기값·EEF 방향·높이 범위·원통 타겟·목표6–12cm·장애물0–6개·보상 전체(역방향−120 포함)·관측·행동·종료·커리큘럼·PPO 수치를 보존한다.

2026-11-26 그림 확인 후 사용자 지시에 따라 기존 RED/외부 IK의 두 좁은 영역을 섞던 방식에서 **선반 전면 안팎의 연속 영역**으로 직접 수정했다. EEF의 shelf-local Y는 선반 전체 폭 `[-0.5,0.5]m`, X는 `min(타겟 시작X, 목표X)`부터 `max(로봇 base_link의 shelf-local X,0.30m)`까지다. 현재 기본 배치에서 베이스 X는0.7m다. 이전 그림의 RED 내부 위치와 기존 외부 IK 범위를 모두 포함하며 두 영역 사이와 좌우 양쪽도 샘플링한다. 높이와 손 방향은 그대로다. 이는 명시된 전면 영역 안에서 유효한 위치를 선택하는 것이며 로봇의 전체3D 도달 공간을 완전히 열거하는 것은 아니다.

`initial_pose_mode=front_area`, `front_y_bounds=(-0.5,0.5)`를 사용한다. 50:50 우선 선택은 제거했다. 넓은 영역에서24개를 병렬 생성해 EEF 예비 경로 검사 후4개를 기존 외부2개와 함께 Warp IK에 보낸다. 넓은 영역의 유효 후보를 우선하고, 없으면 안전한 기존 외부 IK로 대체한다. 새 영역은 훨씬 넓으므로 이전 RED 근처의 실제 선택 빈도는 낮아질 수 있다.

시작점·목표·장애물은 재추첨하지 않는다. 후보 생성과 FK/충돌 검사는 GPU batch로 계산하며 실제 USD 로봇 충돌 상자와 관절 변환을 최초1회 cache한다. 타겟·활성 장애물·선반과 겹치는 팔/손 후보를 보수적으로 거절한다. 시작→목표 구간은 타겟 반경·손 전체 충돌 상자의 XY 크기를 고려해 모든 후보(대체 후보 포함)에서 제외한다. 수렴한 관절 상태만 물리에 기록하고 추가 물리 step은 없다. 기본6후보와 필요한 행의8모서리 recovery 예산을 모두 소진하면 안전하지 않은 자세를 쓰지 않고 오류를 보고한다. 별도 RNG로 기존 물체/목표 추첨을 보존한다.

runtime은 부모 `ProfRevisionV0_3_2Env`를 사용한다. PPO는 `ProfRevisionV0_3_3IKPPORunnerCfg(ProfRevisionV0_3_3PPORunnerCfg)`이며 실험명만 `inspire_sweep_prof_revision_v0_3_3_ik`다. `Reset/front_selected_fraction`, `legacy_fallback_fraction`, `red_selected_fraction`, `pose_candidates`, `pose_recovery_fraction`, `pose_collision_rejected_fraction`, `ik_attempts`로 선택과 예산을 추적한다. `red_selected_fraction`은 넓힌 영역의 후보 종류가 아니라 실제 기존 RED polygon에 들어간 EEF의 비율이다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3_3-IK --num_envs 2048 --headless
```

[구현 근거·변경 이력·새 성능 비교·그림·미검증 범위](../logs/2026-11-26_prof_revision_v0_3_3_ik_implementation.md).

## Prof Revision v0_3_3-IK-v1

`ProfRevisionV0_3_3IKV1EnvCfg(ProfRevisionV0_3_3EnvCfg)`는 일반 v0_3_3 직접 자식이다. 기존 v0_3_3-IK의 넓은 전면 영역은 보존하고, 사용자 승인 그림의 선반 내부 중심 영역만 새 환경에 적용했다. 타겟 원통·목표6–12cm·장애물0–6개·108/176D 입력·12D 행동·물리·성공 XY3cm·TCP4m/s 종료·전체 Reward/Termination/Curriculum·PPO 수치는 v0_3_3 그대로다. 진행+100·역방향−120·Reach9.8·Formation0.1715·장애물변위−300(raw cap0.04)와 나머지11개 보상 및 순서를 유지한다.

EEF 후보는 shelf-local **X=[−0.20,+0.30]m, Y=[−0.25,+0.25]m**다. 선반 전면 X=+0.20m부터 기존 시작위치까지10cm의 진입 구간을 포함한다. 높이 범위·손가락 초기값·손 방향은 부모와 같다. `initial_pose_mode=shelf_area_v1`, `initial_x_bounds=(-0.2,0.3)`, `front_y_bounds=(-0.25,0.25)`만 reset IK params에 추가한다. 위치 오차 허용0.5mm를 고려해 사각창 안쪽1mm를 여유로 두며 외부 대체/복구 후보에도 동일 범위를 적용한다.

기존 cache된 실제 로봇 collision box·전체링크 FK·Warp IK를 재사용한다. 기본6후보(창 내부4+기존 위치2), 기본 후보가 모두 탈락한 행만8모서리 recovery를 검사한다. 2026-11-27 학습1438 iter 이후 후보 소진 오류를 재현해 현 IK-v1에 직접 복구를 추가했다. 앞선14개가 모두 탈락한 행만 승인된 동일 XY창·기존 높이 구간의9×9×3 결정적 격자를 검사한다. 최대3회×81후보 batch로 미해결 행만 처리하며 성공 행은 다음 batch에서 제외한다. 모든 단계에서 동일한 IK 오차·전체링크 충돌·이동 경로 검사를 통과해야 한다. 최종 격자도 모두 실패하면 오류로 종료한다. 일반 후보 선택과 기존033-IK 경로는 유지한다. `Reset/pose_grid_recovery_fraction`으로 추가 복구 비율을 기록하고 `pose_candidates`/`ik_attempts`에도 실제 추가 계산량을 포함한다. 팔/손과 타겟·활성장애물·선반의 겹침 및 물체 시작→목표 구간을 피한다. 물체/목표 분포를 다시 뽑지 않고 선택된 최종 관절만 쓰며 추가 physics step은 없다. 후보창 전체의 도달가능성을 보장하는 것은 아니며 유효 후보만 선택한다.

Gym은 기존 미버전 이름 `...-IK`와 같은 계열의 `...-IK-v1`을 동시에 일반 등록할 수 없으므로 **새 환경에만 namespace**를 둔다. 실제 task ID는 아래 명령과 같이 `inspire_sweep_baseline/`을 포함한다. 기존 ID는 그대로 보존하며 기존 IK를 새 버전으로 자동 치환하지 않는다. train/play의 CLI helper는 namespace 경로를 Hydra config group으로 등록하는 호환 처리를 한다. namespace 없는 모든 기존 task는 Isaac Lab의 원래 decorator 경로 그대로다.

runtime은 기존 `ProfRevisionV0_3_2Env`, PPO는 `ProfRevisionV0_3_3IKV1PPORunnerCfg(ProfRevisionV0_3_3PPORunnerCfg)`이며 실험명만 `inspire_sweep_prof_revision_v0_3_3_ik_v1`이다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task inspire_sweep_baseline/Inspire-Sweep-Prof-Revision-v0_3_3-IK-v1 --num_envs 2048 --headless
```

[전체 계약·기존환경 보존·실제범위·성능·미검증](../logs/2026-11-27_prof_revision_v0_3_3_ik_v1_implementation.md).

## Prof Revision v0_3_4

`Inspire-Sweep-Prof-Revision-v0_3_4`는 일반 `ProfRevisionV0_3_3EnvCfg`를 직접 상속한다. Runtime `ProfRevisionV0_3_4Env`는 부모가 사용하던 `ProfRevisionV0_3_2Env`를 상속하고 상태 생성만 교체한다. 원통 타겟·장애물0–6개·목표6–12cm·기존 reset·108/176D 관측·12D 행동·물리dt0.01s/정책dt0.02s·10초episode·성공XY거리≤3cm·TCP4m/s 종료를 보존한다. IK/Hard 변형은 도입하지 않는다.

| 보상 이름 | 의미 | weight |
| --- | --- | ---: |
| sweep_progress | 가중 거리H 개선×현재 유효 접촉×최근2/3접촉×거리별 힘 방향 계수 | +100 |
| sweep_retreat | 같은H의 증가; 접촉·힘과 무관 | −100 |
| reaching | EEF와 현재 추적OBB 중심 사이10cm 초과 거리의 signed 감소량 | +9.8 |
| action_rate | 팔·손 명령 변화량 제곱합; 각 그룹cap100 후 합산 | −0.03 |
| joint_velocity | 팔6·손12관절 속도 제곱합; 각 그룹cap100 후 합산 | −0.03 |
| shelf_collision | 선반 움직임·손가락/손목의 선반 접근 비용 | −0.5 |
| shelf_failure | 기존 선반 충돌 실패 조건 사건 비용 | −3 |
| obstacle_contact | 비타겟 장애물에 대한 손 합력의5N 초과 지수 비용; raw cap100 | −0.04 |
| wrench_change | 손목 힘 크기 변화5N/모멘트 크기 변화0.3Nm 초과; raw cap1 | −0.1 |
| object_tilt | 타겟·활성 장애물의5° 초과 기울기 | −30 |
| obstacle_displacement | 활성 비타겟의reset 대비3D 제곱변위 합; raw cap0.04m² | −300 |
| arm_action_limit | 팔 원본 명령의 실행 한계 초과량 | −3 |
| hand_action_limit | 손 원본 명령의 실행 한계 초과량 | −3 |
| contact_formation | 5개 패드의OBB 근접도×양방향cos² 합 | +0.1715 |

부모의 팔/손 action-rate2개를 `action_rate`1개, 팔/손 joint-velocity2개를 `joint_velocity`1개로 합쳤다. 두 종류는 명령 변화량과 실제 속도로 의미가 달라 각각 유지한다. 그룹별cap100을 보존하므로 각 통합raw 최대200이고 기존 총 비용을 유지한다. 로그도4개에서2개로 통합한다. 빈curriculum·나머지 보상 함수와 수치·PPO 모델/알고리즘은 동일하다.

접촉은 기존 physics substep의 타겟 법선 하중 합≥0.01N 및 유효성으로 판정한다. 방향 계산의 별도 평균 수평 합력≥1N 조건을 제거하고 그 현재 접촉 마스크를 사용한다. 평균 합력은 상쇄·substep 평균으로0.01N 미만일 수 있어 별도0.01N 문턱도 두지 않는다. 합력0은 정렬0, 반대 방향도 정렬0이며, 기존3–6cm 힘 방향 완화와 최근2/3접촉 조건을 유지한다.

손목 허용량은 벡터 차이 크기가 아닌 `abs(norm(current)-norm(previous))`다. 정책dt20ms 기준5N·0.3Nm이며, 기존saturation_ratio2.5에 따라12.5N·0.75Nm에서raw1에 도달한다. 장애물 접촉·손목 보상 weight와 장애물 이동 비용은 부모 값 그대로다.

PPO는 `ProfRevisionV0_3_4PPORunnerCfg(ProfRevisionV0_3_3PPORunnerCfg)`이고 실험명만 `inspire_sweep_prof_revision_v0_3_4`로 분리했다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3_4 --num_envs 2048 --headless
```

장기 학습 결과는 미검증이다. [전체 변경 대조·검증·한계](../logs/2026-11-27_prof_revision_v0_3_4_implementation.md).
