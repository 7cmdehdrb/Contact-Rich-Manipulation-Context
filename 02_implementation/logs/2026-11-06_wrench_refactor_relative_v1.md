# Relative-v1: 장애물 Base 관측 단일 변경

2026-11-06. [환경 계약](../environments/WRENCH_REFACTOR_RELATIVE_V1_ENVIRONMENT.md).

## 요청·기준·구현

사용자는 현재 Relative-v0를 상속해 장애물 encoder 입력만 EEF Frame에서 Base Frame으로 바꾸고, 기존 Refactor 장애물 관측과 같게 만들 것을 요청했다. 별도 이름 지정이 없어 `Inspire-Wrench-Refactor-Relative-v1`로 등록했다. 기준 workspace commit은 `093627fdf232360eeac4bf540be833888b1b89a4`다. 시작 시 production 작업트리는 깨끗했고 문서 submodule 포인터만 상위 저장소와 달랐다. 해당 커밋·포인터를 변경하지 않았다.

EnvCfg는 Relative-v0 직접 상속이며 post-init에서 부모 초기화를 끝낸 뒤 `observations.obstacles.initial_positions.func` 하나만 기존 Refactor Actor와 동일한 `initial_obstacle_positions`로 교체했다. 관측 함수·encoder·runtime·reset·Scene·물성·제어·보상·종료·curriculum 코드를 수정하지 않았다. PPO는 Relative-v0 직접 상속이고 experiment_name만 새 버전으로 구분했다.

## 최종 대조 항목

| 범위 | 허용 차이 |
| --- | --- |
| EnvCfg 전체 | 장애물 observation callable1개 |
| Scene / Event / Command / Action / Reward / Termination / Curriculum / runtime | 없음 |
| 직접 policy 관측58D | 없음 |
| 장애물64D | EEF 변환을 제거하고 base snapshot 반환 |
| Actor / Critic / Storage / encoder 모델 | 없음; 공통 policy/obstacles 유지 |
| PPO 전체 | experiment_name만 변경 |
| Gym 등록 | v1 ID와 새 config/runner entry point |
| 기존 v0 및 모든 기존 설정 정의 | 변경 없음 |

요청의 “Refactor와 동일”은 초기 Actor 장애물 관측 callable의 동일성을 뜻한다. Critic의 현재 GT 관측이나 비대칭 입력은 추가하지 않는다. 부호·노이즈·가시성·순서를 다시 계산하지 않고 원래 snapshot을 재사용한다.

## 검증

CPU 회귀66개 통과. 기존 Refactor/Relative-v0 검사와 base 관측의 EEF 이동·회전 불변성, 빈 슬롯0, snapshot 변경 방지를 확인했다.

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench_refactor_relative.py
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python -u src/inspire_sweep_baseline/tests/_wrench_refactor_relative_probe.py --version 1 --num_envs 64 --headless --device cuda:0 --output outputs/wrench_refactor_relative_v1_validation
```

실제 config probe는 v1의 전체 dictionary를 v0와 비교하여 위 callable 이외의 차이를 금지하고, 부모 인스턴스와 새 부모 인스턴스의 불변성 및 직접 상속을 검사했다. PPO 전체도 experiment_name 외 동일성을 검사했다. 모두 통과했다. 첫 검사에서 callable 객체를 `to_dict()`의 직렬화 문자열과 직접 비교한 검증 스크립트 오류가 있었다. 함수 identity를 따로 검사하고 동일한 직렬화 형식끼리 비교하도록 수정했으며 production 환경은 추가 수정하지 않았다.

GPU64 env, seed42에서 iteration0/9999/10000/13000/25000 각각 reset 후36step, 총180step을 통과했다. 매step 장애물 관측이 기존 Refactor의 `initial_obstacle_positions(raw)`와 오차0으로 일치했다. policy58D/obstacles64D, 전체 관측·보상 finite, 미관측 슬롯0, 촉각4상태, 부분 reset의 비대상 보존, EEF OSC, Hand effort10/velocity1을 확인했다. 초기 바닥 정렬 최대 오차0m, 주차 물체 최대 drift7.62939453125e−6m였고 질량·마찰·bounds cache는 보존됐다. 산출물은 workspace `outputs/wrench_refactor_relative_v1_validation/probe_64.json`, `probe_64.log`다.

최종 코드 대조에서 production 변경은 신규 EnvCfg·PPO subclass·Gym 등록 추가뿐이다. HEAD 대비 AST로 기존 EnvCfg 및 PPO 설정 정의가 모두 불변임을 확인했다. 모든 수치·params·보상·종료·curriculum·로그 metric 키가 부모와 같고 등록/실험명 이외 동작 차이는 장애물 관측 callable 하나뿐이다. 변경 Markdown 수식·링크 검사와 양쪽 저장소 `git diff --check`를 통과했다.

v1의2048 env·학습·GUI/play·장기 성능은 이번 변경에서 검증하지 않았다. v0의 이전 대규모/학습 결과를 v1의 실제 실행 결과로 간주하지 않는다. 기존 `logs/rsl_rl`은 수정하지 않았다.

## 후속: arm joint velocity 종료 출력

사용자가 반복되는 속도 종료의 관절명과 실제 속도를 확인하도록 요청했다. 새 환경을 만들지 않고 v1의 termination params에 `print_velocity=True`만 추가했다. 공유 `termination_functions/sweep.py:arm_velocity`에 기본 False인 출력 옵션을 추가했으며 반환 마스크는 기존 `any(abs(velocity)>threshold)`와 같다. 임계값은 3.0 rad/s 그대로다. 초과 관절별 env ID, joint 이름·전체 index, signed/absolute velocity, threshold를 flush=True로 출력한다. 기본 False인 다른 환경은 출력하지 않는다. stdout 출력은 GPU 동기화와 I/O 비용을 추가할 수 있다.

전체 v1 설정을 v0와 CPU dictionary 비교하여 기존 장애물 callable 차이와 새 출력 플래그 외의 차이가 없음을 확인했다. v0/v2의 params와 부모 인스턴스가 변하지 않는 것도 확인했다. 스폰·관측·보상·종료 기준·제어·커리큘럼·PPO 변경 없음. 기존 Sim probe의 허용 차이에도 출력 플래그만 추가했으며 실행하지 않았다.

CPU 검사: `test_task_contract.py`, `test_wrench_refactor.py`, `test_wrench_refactor_relative.py` 합계 79개 통과. 정확히 임계값인 경우 비종료, 양/음 초과 속도, joint ID 재정렬, 제외 관절, 출력 없는 기본 경로와 출력 경로의 동일 마스크를 검사했다. 변경 문서 수식·링크와 양쪽 diff 공백 검사를 수행했다. 사용자 요청에 따라 Sim·Lab·학습은 실행하지 않았고 기존 학습 프로세스 및 로그도 건드리지 않았다. 실행 중 프로세스에는 자동 반영되지 않는다.

## 후속: model_400 wrist3 과속 실측 진단

사용자가 실제 로그를 요청했으므로 이번 진단에서는 앞선 Sim 실행 생략 조건을 갱신하여 단일 환경 headless 재생을 수행했다. `diagnosing-bugs` 절차를 사용했다. 지정 checkpoint `logs/rsl_rl/inspire_wrench_refactor_relative_v1/2026-11-06_20-43-26/model_400.pt`, seed42, physics dt0.01 s, policy dt0.02 s다. 기존 학습 프로세스·checkpoint·logs/rsl_rl에는 쓰지 않았다. production 설정/코드/자산 수정도 없다. 진단 사본은 workspace `outputs/wrist3_diagnosis`에 분리하고 export를 생략했다.

실행 harness는 `outputs/wrist3_diagnosis/replay.py`다. OSC compute 전후의 raw/processed action, pose/velocity, Jacobian, arm inertia, gravity, output torque를 기록했다. 상세 재생에서는 실제 전달된 이전 substep torque, 손 body net force, 실제 joint velocity limit, task-frame와 gain도 기록했다. JSONL은 물리 step 전 값이므로 마지막 terminal 속도는 stdout을 기준으로 센다. baseline 로그에는 사용자가 제공한 +3.529198, −3.188082 rad/s가 동일하게 나타났다.

| 대조 | 정책 step | wrist3 종료 | 다른 속도 종료 |
| --- | --- | --- | --- |
| 원본 재생 | 400 | 11회, 최대 절댓값3.841568 rad/s | 없음 |
| 원본 상세 재생 | 120 | 4회 | 없음 |
| 회전 액션3개만0 | 120 | 1회, +3.031921 rad/s | wrist1 1회 |
| robot collider만 메모리에서 비활성화 | 120 | 0회 | wrist1 4회 |

종료 조건과 threshold는 모든 실험에서 그대로다. 재현 판정 명령 `python outputs/wrist3_diagnosis/check_symptom.py outputs/wrist3_diagnosis/replay.log`는 11회/3.841568을 출력하고 exit1로 증상을 검출했다. 원본400과 상세120의 초반 궤적·종료는 재현됐다.

### 확인한 사항

1. **EEF x축이다.** 측정한 wrist3 Jacobian column을 현재 EEF quaternion으로 역회전하면 선형 성분≈0, 각 성분≈[1,0,0]이다. 이는 axia body 축과 offset EEF 축을 구분해야 한다는 뜻이다. 현재 EEF z 회전만으로 wrist3를 설명하는 전제는 맞지 않는다. Jacobian condition number는 원본400의 분석 가능한 step에서 약8.66–21.0으로, 극단적인 singularity 증폭은 이번 로그의 주된 징후가 아니다. 단위가 섞인 condition number이므로 일반적인 안전 기준으로 해석하지 않는다.
2. **실제 제한은4, 종료는3 rad/s다.** 로드된 joint_vel_limits는 [2,2,2,4,4,4]다. wrist3에 3–4 rad/s가 발생하는 것은 설정상 불가능하지 않다.
3. **접촉으로 동일 입력·상태의 속도 결과가 갈린다.** 원본과 no_contact는 trace index28까지 상태와 raw action이 같다. index28 wrist3 velocity=+0.452593, OSC torque=+0.018992 N·m다. 다음10ms 후 원본은−1.410832 rad/s, no_contact는+0.123336 rad/s다. 해당 step의 raw action도 동일하다. 원본 손 body별 net-force 크기 합은4.693 N, no_contact는0이다. 그다음 원본은+2.307857 rad/s로 반전하고 손 접촉력 크기 합은21.544 N이다. index43→44에서도+2.886960→−1.991769 rad/s로 급변하며 OSC wrist3 torque는−0.048148 N·m다. 따라서 wrist3 OSC torque만으로 실제 속도를 설명할 수 없다.
4. **관성과 외력의 영향이 크다.** arm inertia의 wrist3 diagonal은 예시 구간0.00085–0.00088 kg·m²다. OSC는 task-space inertia와 damping으로 계산된 토크를 출력하며 joint velocity를 직접 제한하지 않는다. 접촉 impulse, 다른 joint와의 결합, 속도 제약을 포함한 실제 dynamics와 OSC의 자유공간 모델은 다르다. `M_arm^-1(tau−g)` 비교는 contact/coriolis/finger dynamics/solver constraints를 생략한 진단용 값이지 완전한 실제 가속도 예측이 아니다.
5. **명령 크기도 크다.** 첫 raw action6D=[9.840859,2.368494,−3.797801,2.422520,1.252317,3.879288]다. 위치 scale0.03을 적용하면 상대 위치 목표≈[0.295226,0.071055,−0.113934] m, RPY scale0.15를 적용하면≈[0.363378,0.187848,0.581893] rad다. 20ms마다 갱신되는 상대 pose 목표이며 속도 명령이 아니다. 관측의 tanh와 별개로 실제 action 경로에는 ±1 clamp/tanh가 없다. 최초 OSC torque6D≈[−60.0208,125.7823,−28.4009,−8.6951,2.5052,0.0612] N·m다. 회전 액션0에서도 과속이 남으므로 회전 명령만의 문제가 아니다. no_contact에서도 wrist1 종료가 남는다는 사실은 정책 명령·다관절 운동 문제까지 해결됐다는 뜻이 아님을 보여준다.

결론: 측정된 wrist3 급변은 큰 정책 이동 명령으로 손이 접촉할 때 생기는 동역학적 반작용이 직접 원인임을 대조로 확인했다. EEF 축 해석도 z→x로 바로잡아야 한다. 제어기의 torque 출력 오류나 Jacobian singularity가 유일 원인이라는 증거는 없다. 물리 solver의 접촉 impulse가 현실적으로 타당한 크기인지, timestep/solver 설정이 얼마나 증폭하는지, 어떤 상대 물체와 어느 접촉점이 지배적인지는 이번 센서 기록만으로 확정하지 않았다. 범위를 넘는 torque clamp/termination 완화/관성/학습 수정은 하지 않았다. collider 비활성화는 원인 분리 실험이며 수정안이 아니다.

향후 수정한다면 액션 범위·상대 pose 목표 크기와 접촉 중 감쇠/속도 보호를 각각 대조해야 한다. 학습된 checkpoint에 action squashing을 곧바로 추가하면 정책 의미가 달라지므로 검증 없이 적용하지 않는다. 이번 요청은 진단이므로 production 회귀 수정은 없고, 실행 결과와 제한만 기록했다.

## 후속: Axia 280 g 적용 및 정책·F/T 실측 검증

사용자는 Axia를 실제 질량280 g으로 반영하고 F/T 캔슬링을 보존하며, 같은 정책 play로 wrist3 현상 완화 여부를 검토하도록 요청했다. 현재 진단 대상 Relative-v1에 직접 적용한다고 알렸으며 공통 환경으로 확대하지 않았다.

### 변경과 전체 대조

`WrenchRefactorRelativeV1EnvCfg.__post_init__`에 `self.scene.robot.spawn.sensor_mass = 0.280`을 추가했다. 기존0.001 kg→0.280 kg이다. 형상·반경41 mm·길이25.4 mm·설치 위치·조인트 연결·재질은 그대로다. PhysX cylinder mass properties로 관성이 함께 생성된다. 실제 로드된 Axia mass는0.2800000012 kg였다. 초기 wrist3 M66은0.0008838734→0.0011183728 kg·m²로 약26.53% 증가했다.

공통 `SENSOR_MASS`와 v0/v2는 변경하지 않았다. v1의 기존 장애물 Base 관측 및 속도 진단 출력도 보존했다. 전체 EnvCfg CPU 비교에서 v0 대비 기존2개 차이와 새 housing mass 외 차이가 없음을 확인했다. parent 및 v2 설정도 보존됐다. 관측·OSC·Action Rate·reward·termination 임계값·reset·spawn timing·curriculum·PPO·모델은 변경하지 않았다. 기존 Sim probe의 허용 차이만 mass를 포함하도록 갱신했으며 그 probe는 이번에 실행하지 않았다.

F/T 측정 joint는 `axia80_measurement_joint`: Axia housing(parent)→inspire_base_link(child)다. 캔슬링 대상은 그 아래 hand30개 body이며 현재 PhysX mass/inertia를 읽는다. housing은 upstream이므로 보정 대상에 넣지 않는 것이 맞다. 보정 코드·노이즈·cache·reset mask는 변경하지 않았다. 실제 보정 대상 질량 합은0.7900000215 kg로 확인됐다.

### 같은 정책 play 결과

기존400step baseline과 동일한 checkpoint model_400, seed42, num_envs1, dt0.01/정책dt0.02, headless CUDA로 실행했다. production 질량 변경 외 동일하다. 진단 사본에서 로그만 추가하며 checkpoint export는 생략한다.

| 지표 | 1 g 기존 | 280 g |
| --- | --- | --- |
| 정책 step | 400 | 400 |
| wrist3 속도 종료 | 11회 | 13회 |
| 최대 종료 절댓값 | 3.841568 rad/s | 3.771384 rad/s |
| 평균 종료 절댓값 | 3.402015 rad/s | 3.447730 rad/s |
| 다른 관절 속도 종료 | 없음 | wrist2 1회(+3.373689 rad/s) |

따라서 이 고정 seed·짧은 구간에서는 **완화가 확인되지 않았다**. 최대 종료 속도만 약1.8% 낮아졌지만 종료 횟수·평균은 줄지 않았다. 여러 seed의 통계적 성능이나 장기학습 효과로 일반화하지 않는다. 질량 변경으로 접촉·reset 시점과 이후 정책/난수 경로가 달라지므로 개별 episode의 일대일 대응도 가정하지 않는다. 사용자 지정 실제 질량이므로0.280 kg을 유지한다. 추가 제어 변경·임계값 완화·재학습은 하지 않았다.

산출물: workspace `outputs/wrist3_diagnosis/mass280.log`, `trace_mass280.jsonl`, `outputs/axia280_validation/play_comparison.json`. 기존 baseline 로그를 덮어쓰지 않았다.

### F/T 실제 물리 검증

기존 `_clutter_v2_wrench_probe.py`의 Newton–Euler 검증 절차를 Relative-v1에 맞춘 진단 사본 `outputs/axia280_validation/wrench_probe.py`로 실행했다. 4환경에서 로봇 물성은280 g 구성 그대로 두고 선반·물체를 멀리 이동시켜 무접촉을 확보했다. 수동 physics advance로 종료/reset 간섭을 제외하고, 센서 자체 raw/support/pure를 직접 읽어 observation noise와 분리했다. 정지 안정화50step+정지 측정40step, arm/hand 운동160step, 안정화60step, 알려진 world 외력·토크70step을 수행했다. 외력은 실제 PhysX body에 적용하고 센서 tensor에 주입하지 않았다. 마지막 실제 reset에서 stale sample이0인지도 확인했다.

| 시험 | 최대 힘 오차/잔차 | 최대 모멘트 오차/잔차 | 기존 허용 기준 |
| --- | --- | --- | --- |
| 무접촉 정지 | 3.77e−6 N | 8.52e−6 N·m | 0.15 N / 0.02 N·m |
| 무접촉 arm/hand 운동 | 3.99e−6 N | 0.000689 N·m | 0.5 N / 0.05 N·m |
| 알려진 외력·토크 | 5.62e−6 N | 0.004708 N·m | 0.15 N / 0.02 N·m |

전체 통과. 손의 무게·관성 제거와 외력 보존, 실제 housing 질량 및 보정 대상 제외, reset mask를 확인했다. 이번 시험은 특정 운동·하중의 범위이며 임의의 모든 접촉이나 실물 센서 정확도까지 보증하지 않는다. 상세 결과 `outputs/axia280_validation/ft_280g.json`, 로그 `ft_280g.log`.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH WRIST_DIAG_MODE=mass280 /home/min/miniconda3/envs/env_isaaclab/bin/python -u outputs/wrist3_diagnosis/replay.py --task Inspire-Wrench-Refactor-Relative-v1 --num_envs 1 --checkpoint logs/rsl_rl/inspire_wrench_refactor_relative_v1/2026-11-06_20-43-26/model_400.pt --headless --device cuda:0 --seed 42 --max_steps 400
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python -u outputs/axia280_validation/wrench_probe.py --num_envs 4 --sensor-mass .280 --output outputs/axia280_validation/ft_280g.json --headless --device cuda:0
```

CPU 회귀는 `test_task_contract.py`, `test_wrench_refactor.py`, `test_wrench_refactor_relative.py`, `test_clutter_v2_wrench.py`의86개가 통과했다. 변경 문서 수식·링크와 양쪽 저장소 diff 공백도 확인했다. README 기존 GoalAccuracy v0_2 링크 누락은 이전부터의 범위 밖 항목으로 남긴다. 기존 학습 프로세스·logs/rsl_rl은 변경하지 않았다. 실물 센서 시험·재학습·여러 seed 장기 성능은 미검증이다.

## 후속: 관절 속도 종료 없이 정책 재생

사용자 요청으로280 g Relative-v1의 진단 실행에서만 `terminations.arm_joint_velocity=None`으로 제거했다. production EnvCfg는 변경하지 않았고 다른 종료·물성·제어·reward는 유지했다. 같은 model_400, seed42, 1환경, 400policy step(800physics step, 8초)을 실행했다. 실제 TerminationManager 활성 목록에서 object_fall_or_tilt, shelf_failure, target_goal_success, timeout만 남았음을 확인했다.

`outputs/wrist3_diagnosis/replay.py`의 `WRIST_DIAG_MODE=no_joint_termination` 분기로 실행하고 매 scene.update 직후 실제 joint_vel 전체를 기록했다. 따라서 마지막 substep 후 자동 reset 이전의 속도도 포함한다. 기존 OSC trace의 pre-physics 최대값과 혼동하지 않는다. 결과는 `velocities_no_joint_termination.jsonl`, `joint_peaks_no_termination.json`, 실행 로그는 `no_joint_termination.log`다.

| Arm 관절 | 최대 절댓값(rad/s) |
| --- | --- |
| wrist3 | 4.0000038 (signed −4.0000038, physics step640) |
| wrist2 | 4.0000024 |
| wrist1 | 4.0000014 |
| shoulder_pan | 2.0000033 |
| elbow | 2.0000026 |
| shoulder_lift | 2.0000021 |

손 관절 중 최대는little_1의1.035589 rad/s였다. 전체 최대는wrist3의약4 rad/s지만 wrist1/2도4에 도달했다. 이는 기존 PhysX 실제 속도 제한 [2,2,2,4,4,4]에 도달한 결과다. termination만 제거했으며 물리 속도 제한은 그대로이므로 무제한 동역학의 최대 속도를 측정한 것은 아니다. 수e−6 수준의 한계 초과는 수치 오차 범위다.

wrist3가3 rad/s를 넘는 샘플은46/800개, 연속 구간12개, 최장14physics step(약0.14초)이었다. 초반의1–2step 스파이크뿐 아니라 후반에는 지속되는 초과도 있었다. episode step 감소로 확인되는 reset은1회였으며, 다른 종료 조건은 유지되므로 완전히 무종료인 장시간 궤적은 아니다. 중간 진행보고의3.62 rad/s는560샘플 시점 값이며 위 수치가 최종800샘플 결과다.

진단 설정 변경만 수행했고 환경의 영구 종료 조건은 보존했다. 장기·여러 seed·물리 속도 제한 제거는 이번 실험 범위가 아니다. 기존 학습·checkpoint·logs/rsl_rl은 변경하지 않았다. 변경 로그의 수식·링크 및 저장소 diff 공백을 확인했다.
