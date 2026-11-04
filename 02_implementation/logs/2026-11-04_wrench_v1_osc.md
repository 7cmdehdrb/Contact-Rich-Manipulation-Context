# 2026-11-04 Wrench-v1 F/T 기준 closed-loop OSC

## 요청과 기준

사용자의 최신 지시는 **Wrench-v0 직접 수정이 아니라 `Inspire-Wrench-v0`를 직접 상속하는 `Inspire-Wrench-v1` 생성**이다. 변경 범위는 OSC뿐이며, wrench-only·closed-loop·F/T sensor reference가 요구사항이다. 앞선 중단 턴은 코드 읽기만 수행했으므로 v0 OSC를 먼저 수정했다가 되돌린 이력은 없다.

Workspace main HEAD `ba1aa88bf462c5263531379b0a67248ad2439552`, IsaacLab HEAD `929f0fe1e9c1699efebf31b2ad0ab723a7d6e7e9`에서 작업했다. 시작 시 기존215개 생산 소스의 SHA256 및 v0 관련 class AST를 `outputs/wrench_v1_validation/baseline.json`에 저장했다. 이전 턴의 미추적 Wrench-v0 파일과 사용자 TEMP 출력·문서 변경을 보존했다. IsaacLab submodule 작업트리는 변경하지 않았다.

[최종 환경·파라미터 계약](../environments/WRENCH_V1_ENVIRONMENT.md)에서 설정과 실행을 확인할 수 있다.

## 참고 근거와 결정

사용자가 지정한 `IsaacLab/source/isaaclab_tasks`를 검색했다. 실제 UR10 Reach 예제 `manager_based/manipulation/reach/config/ur_10/ur10_osc_reach_env_cfg.py`는 pose-only다. 이 예제의 effort clamp/비유한 처리/saturation 구조를 참고했고, wrench 제어 기준은 다음 실제 파일로 보완했다.

- `IsaacLab/source/isaaclab/test/controllers/test_operational_space.py:608`, `test_franka_wrench_abs_closed_loop`: wrench_abs, motion 전축0, wrench 전축1, force gain0.2, moment gain0. 공식 테스트는 torque 측정 부재 때문에 moment feedback을0으로 둔다.
- `IsaacLab/scripts/tutorials/05_controllers/run_osc.py:127`: hybrid pose+wrench, force gain0.1, z 목표10N. v1의10N force 명령 scale은 이 크기에서 출발하되 이번 과업에서 최적값으로 검증한 것은 아니다.
- `IsaacLab/source/isaaclab/isaaclab/controllers/operational_space.py:455`: `desired + Kp*(desired-current)` 후 J transpose. 기본 구현은 current force3D만 받고 moment를 desired로 채워 moment error를0으로 만든다.
- [공식 OSC 설명](https://isaac-sim.github.io/IsaacLab/main/source/how-to/run_osc.html), [공식 설정 API](https://isaac-sim.github.io/IsaacLab/main/_modules/isaaclab/controllers/operational_space_cfg.html)를 2026-11-04 검색·확인했다. closed-loop 기본 경로가 linear force에만 적용된다는 설명이 로컬 구현과 일치한다. 로컬 IsaacLab 코드를 실행 계약의 기준으로 사용했다.
- [NVIDIA Tensor API](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.0/extensions/runtime/source/omni.physics.tensors/docs/api/python.html)는 fixed-base Jacobian에서 base row 제외 및 world link velocity 매핑을 설명한다. 이번 제어 body는 중심 COM의 기존 sensor cylinder이며, body frame Jacobian을 sensor 축으로 회전한다.

결정: IsaacLab 또는 USD를 수정하지 않고 로컬6축 wrench OSC를 작성한다. `OperationalSpaceControllerCfg`를 설정 컨테이너로 사용하고 전용 ActionTerm이 검증한다. 기본 OSC 인스턴스가 moment까지 지원하는 것처럼 가장하거나, gain만 지정하고 moment feedback을 빠뜨리지 않는다. 기존 보상/관측 F/T 코드를 변경하지 않고 동일한 `PureWrenchReader`에 센서 reference pose를 공급한다.

## 구현 전후와 전체 대조

| 항목 | v0 | v1·영향 |
| --- | --- | --- |
| EnvCfg | 독립 `WrenchEnvCfg` | `WrenchV1EnvCfg(WrenchEnvCfg)` 직접 상속 |
| 등록 | Inspire-Wrench-v0 | 신규 Inspire-Wrench-v1, runtime 동일 |
| PPO | inspire_wrench_v0 | 실험명 inspire_wrench_v1만 변경, 수치/모델 동일 |
| Action | arm6 pose_rel + hand2 | arm6 wrench_abs + 기존 hand2 |
| 축 | motion6축1, wrench6축0 | motion6축0, wrench6축1 |
| feedback | pose/velocity | 센서의 보정된6축 wrench, physics100Hz |
| gain | motion stiffness/damping | force/moment P gain 전부0.2, FF 포함 |
| 명령 범위 | position_scale0.03/orientation_scale0.15 | normalized[-1,1], force축±10N·moment축±1Nm |
| 제어 원점 | axia80+EEF142.7mm offset | axia80 housing 중심, body_offset=None |
| 명령 축 | base-frame pose 증분 | 현재 sensor-frame wrench 성분. 매 substep sensor 자세 사용 |
| 동역학 | inertial decoupling True, gravity True | inertial decoupling False(미사용), gravity True |
| nullspace/arm actuator PD | none / 0,0 | 그대로 |
| finite/effort clamp | 비유한 effort0, 실제 joint limit | 유지, 비유한 raw action도0effort로 거부 |
| reset | v0 Action 상태 초기화 | 새 Action 상태·측정 freshness 선택행 초기화 |
| Scene·센서·관측 | v0 | 동일. ee_frame/관측F/T의 EEF 기준 유지 |
| 보상·종료·커리큘럼·bank·물성 | v0 | 모든 설정/callable/params/weight 동일 |
| timestep/decimation | 0.01s/2 | 동일 |
| runtime·기존 파일 | v0·기존 Revision | 동일 |

생산 파일 변경은 기존 `mdp/actions/wrench.py`, `envs/wrench_envs.py`, `agent/wrench_ppo_cfg.py`, 패키지 `__init__.py`에 v1 선언/등록을 추가한 것이다. 기존 v0 class AST는 전부 동일하다. 신규 `mdp/action_functions/wrench.py`는 simulator adapter, 신규 `mdp/common/wrench_control.py`는 torch 전용6축 FF+P/J transpose 계산이다. 파일 구조를 이동하지 않았다.

기본 OSC와 다른 점은 문서에 명시했다. 새 경로는 full6D measured wrench를 사용하고, task frame translation을 root 원점까지의 wrench shift로 넣지 않는다. sensor 원점 Jacobian과 sensor 원점 wrench를 직접 맞춘다. 기존 측정 joint의 child 원점은 sensor center와12.7mm 다르므로 기존 reader가 그 고정 오프셋만 보정한다. 실제 제조사 F/T frame이 sensor center와 같다고 가정하지 않으며 hardware adapter가 보정해야 한다.

raw reaction에서 downstream hand gravity/inertia를 제거한 값은 robot-on-environment 부호다. 실물 장치의 environment-on-tool 출력은 반전해야 한다. gravity compensation 토크는 이 측정 보정과 역할이 다르다. 센서 원시 수치를 tool 무게가 포함된 채로 feed back하지 않는다.

## 실제 검증

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OMP_NUM_THREADS=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q \
  src/inspire_sweep_baseline/tests/test_wrench_v1.py \
  src/inspire_sweep_baseline/tests/test_wrench.py \
  src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_osc.py \
  src/inspire_sweep_baseline/tests/test_revision_v2.py \
  src/inspire_sweep_baseline/tests/test_revision_layout.py \
  src/inspire_sweep_baseline/tests/test_revision_observations.py
```

**80 passed,6.09s**, `outputs/wrench_v1_validation/tests_final.txt`.

검증 세부:

- 실제 로컬 Isaac `OperationalSpaceController`를 CPU로 실행하여 force gain0.2/moment gain0일 때 새 함수 출력과 기존 wrench-only compute 출력이 일치한다. 모멘트 gain0.2 적용 후 차이는 정확히 추가 모멘트 feedback 항이다.
- 6축 각각 desired=current이면 feedforward만, 측정 부족이면 증가, 과도하면 감소한다. J transpose 가상일 검사는 joint power와 sensor power가 일치하고 g(q)가 한 번만 더해짐을 확인한다.
- 실제 `SensorFrameWrenchAction` 생성/process/apply/reset과 실제 `PureWrenchReader`를 실행했다. ActionTerm 기반형 및 PhysX view만 CPU double이다.32body중 downstream30개 support 제거,12.7mm moment transport, world origin(2,3,4)에서 잘못된 root moment가 생기지 않음, 비정렬 joint index 매핑을 확인했다.
- 현재 sensor yaw90°에서 sensor+X가 world+Y effort로 변환되는지 확인했다. 물리 substep마다 feedback 변경, partial reset 행만 첫 sample 무효화, 다른 행의 명령/feedback 유지, 다음 substep 재활성화를 확인했다.
- normalized clip과 N/Nm scale, raw action 보존, 비유한 raw 입력 거부, 실제 joint effort clamp·saturation을 확인했다.
- 실제 configclass와 실제 v0/v1 EnvCfg post-init을 실행하고 **child의 arm_action만 parent로 교체하면 전체 설정이 같음**을 확인했다. Sim assets/독립 검증 관측그룹은 CPU double이며 실제 Isaac Sim 전체 구성 검증과는 구별한다. parent 인스턴스 재생성 값도 같다.
- v1 직접 상속·등록·PPO 실험명만 변경을 확인했다. 기존 v0 독립성/AST 검사는 새 v1 클래스만 비교 범위에서 제외하여 v0 보호를 유지했다. 기존 FT 보정·Holding OSC·Revision 회귀도 통과했다.

기존 생산 소스 중 변경된4파일 외 **211파일 SHA256 동일**, v0 관련 기존 class AST 동일. 기존파일4개+신규controller/test/probe4개 compile8파일 통과. 결과는 `outputs/wrench_v1_validation/source_audit.json`이다.

## 미검증과 후속 실행

이번에도 `nvidia-smi`는 NVIDIA 드라이버와 통신할 수 없다고 반환했다. 실제 Isaac Sim 초기화·6축 접촉 추종·PPO 학습·collection 시간·모멘트 gain 안정성은 실행하지 않았다.80개 CPU 검증이 물리 접촉 시 진동이나 장기 학습 성능을 입증하지 않는다.

기존 `tests/_wrench_probe.py`에 `--version v1`을 추가했다. 기본 v0 경로는 보존했다. v1 실제 전체 Cfg 차이는 `actions.arm_action`만 허용하고, 실제 controller feedback·effort가 finite인지와 joint limit을 지키는지 확인하도록 준비했다. 이 probe는 **미실행**이다. 명령은 환경 계약에 있다.

훈련은 `scripts/train.py --task Inspire-Wrench-v1`을 사용한다. 검증용 짧은 학습을 수행할 때는 `--resilient-attempt-dir outputs/wrench_v1_training/smoke`로 기록할 수 있다. 이번에는 실행하지 않았고 `logs/rsl_rl`을 수정하지 않았다.

다음 물리 검증에서는 정적인 알려진 외력/모멘트를 가해 F/T 부호·12.7mm reference와 torque 추종을 먼저 확인해야 한다. 이후 desired/current6축 오차·포화율·진동·zero command drift를 확인한다. force gain0.2는 예제에서 출발한 값, moment gain0.2와±1Nm는 새 초기 설계값이다. 성공률이나 안정성을 검증한 최종 튜닝 값으로 기록하지 않는다.

## 문서 검사

변경 Markdown5파일 수식 검사, 환경 계약/개발 로그/인계/활성 안내4파일의 내부·외부 파일 링크94개 검사, workspace·문서 저장소 `git diff --check`를 통과했다. 외부 웹 URL4개는 링크 검사기의 HTTP 검증 대상이 아니며 참고 문서 검색으로 확인했다. README의 이번 신규 링크는 해당 환경 계약으로 연결된다. 기존 v0 작업 때 기록한 과거 Accuracy-v0_2 문서 누락 링크는 이번에도 변경하지 않았다.

## 2026-11-04 후속: 계측 범위150N/8Nm 반영

사용자가 확인한 계측 범위 안에 여유를 두도록 v1에 직접 적용했다. 목표 스케일10N/1Nm →100N/5Nm, 보정 후 제한 없음 →축별120N/6Nm. 게인0.2 유지 시 측정0 최대목표는120N/6Nm다. sensor_wrench_efforts의 선택적 clamp는 Jacobian 변환과 중력 보상 전에 적용하며 v1 Action이 설정값을 전달한다. 양수/유한 설정 검사도 추가했다. 이 제한은 명령에만 적용하며 실제 충격력·합력·보정 전 센서 하중을 보장하지 않는다. 하드웨어 정격 검증이나 종료 조건 추가는 수행하지 않았다.

변경 전 기준은 같은 날 v1 구현의 미커밋 작업트리다. 최종 대조: production 변경은 mdp/actions/wrench.py의 v1 scale/limit, mdp/action_functions/wrench.py의 limit 검증/전달, mdp/common/wrench_control.py의 선택적 clamp뿐이다. 부모 v0 설정·Scene·보상·종료·reset·PPO·등록은 보존했다. 테스트의 기존 목표 기대값을 갱신하고 반대 방향 피드백에서 양/음 명령 포화와 중력 보상 순서를 검증했다.

검증 명령: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OMP_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q src/inspire_sweep_baseline/tests/test_wrench_v1.py src/inspire_sweep_baseline/tests/test_wrench.py`. 결과43 passed (4.38s). GPU rollout/접촉 안정성/실물 및 학습은 미검증. 학습 로그와 사용자 변경은 유지했다.

## 2026-11-04 후속: Desired Wrench의 정규화 action rate

사용자 요청에 따라 v1의 robot_action_rate_penalty Arm 부분을 변경했다. 기존은 클리핑 전 raw 정책 출력의 차이였으며, 이후는 정책 목표 범위로 정규화한 Desired Wrench 차이다. 물리 스케일은 상쇄되므로 raw를 실제 Action과 동일하게 clip한 뒤 normalized_wrench_limit으로 나눠 [-1,1]에 매핑한다. Hand raw 계산·그룹계수0.03·상한100·weight=-1·dt 처리는 보존한다. measured/보정 후 wrench는 사용하지 않는다.

최종 대조: WrenchV1RewardsCfg를 같은 rewards/wrench.py에 추가하고 v1 EnvCfg에서 선택했다. 기존 v0 RewardsCfg와 부모 EnvCfg는 보존했다. 직전 미커밋 작업트리 대비 production 변경은 reward 함수/설정/v1 EnvCfg뿐이다. OSC/스케일·Scene·관측·다른 보상·종료·커리큘럼·reset·PPO는 변경하지 않았다. 기존 GPU probe의 허용 차이에 해당 reward callable만 추가했다.

검증: 앞 절과 동일한 pytest 명령으로44 passed (4.55s). 테스트는 포화된 raw2→3의 목표 변화0, -1→1 경계, 힘/모멘트 상대변화 동일 비용, 비단위 raw limit 정규화, Hand raw 계산 유지 및 v0 대비 arm/reward 외 전체 설정 동일성을 확인했다. GPU rollout/학습은 미수행이다. 학습 로그는 변경하지 않았다.

## 2026-11-04 최종 통합 환경 문서 작성

사용자가 Wrench-v0 전체 환경과 v1 변경점을 한 문서로 요청하여 [최종 통합 명세](../environments/WRENCH_V0_V1_ENVIRONMENT.md)를 작성했다. 기준은 기존 미커밋 v0/v1 구현 및 scale100N/5Nm·명령 제한120N/6Nm·정규화 action-rate 후속 변경까지 반영한 현재 작업트리다. 기존 버전별 문서는 유지하고 통합 문서를 안내한다.

EnvCfg·Scene·Event·관측·액션·보상·커리큘럼·종료·PPO와 해당 공유 구현을 직접 확인했다. 특히 물성 startup 고정, 환경 내 공통 질량, 유한16개 bank, raw와 Desired Wrench 구분, Critic policy noise 공유, 최초 진입 strict 경계, 실제 bbox 바닥 조건, shelf6D 속도 norm 및 비용 proxy1.06m, 무료 속도의 계단 보간을 명시했다. v1은 OSC 외 action-rate 보상도 달라졌음을 반영했다.

최종 대조: 추가/수정은 통합 Markdown·버전별 안내·handoff·활성 환경 안내·README·본 로그뿐이며 환경 코드/테스트/학습 로그는 이번 문서 작업에서 변경하지 않았다. 과거 CPU 검증 결과와 미수행 GPU/실물 결과를 분리했고 새 시뮬레이션/학습/CPU 회귀를 수행한 것으로 기록하지 않았다. 문서 수식 형식·상대 링크·diff 공백 검사는 아래 최종 결과를 따른다.

문서 검증 결과: 변경 Markdown7개 math check 통과. 문서 저장소6개 파일의 링크137개를 workspace 외부 경로까지 확인하여 오류0(HTTP URL4개는 fetch하지 않음). root/docs `git diff --check` 통과. README 전체 링크는 기존에 기록된 무관한 GoalAccuracy 문서 누락을 재검사/수정하지 않고, 이번 추가 링크의 대상 존재를 확인했다. 코드와 문서의 수치·표·경계 최종 대조를 완료했다.
