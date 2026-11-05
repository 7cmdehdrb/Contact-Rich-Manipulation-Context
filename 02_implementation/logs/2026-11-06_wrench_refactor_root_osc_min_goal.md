# Refactor 기반 수정: root-frame OSC 및 목표 최소5cm

2026-11-06. [v0 현재 계약](../environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [소스 부록](../environments/WRENCH_REFACTOR_V0_RECONSTRUCTION.md).

## 요청·의도·범위

사용자는 Refactor의 가장 기본 환경을 직접 수정하여 OSC를 Final·Revision과 같은 방식으로 바꾸고, 시작점 중심 반경5cm 내부를 목표 영역에서 제외하라고 요청했다. 중단된 구현을 재개하면서 공통 클래스 사용이 왼손/오른손 차이를 덮어쓰지 않는지 확인하라고 추가했다. 새 버전 생성이 아니라 v0 직접 수정이며 v1/v2는 이를 상속한다.

기준 root commit a173240d80bdcd5f7567e36cab814480472a2d26. 시작 시 v2 추가에 따른 코드와 문서 변경이 있는 작업트리였다. 기존 변경·독립 문서 submodule·학습 로그는 보존했다.

## 변경 전후·최종 계약 대조

| 항목 | 이전 | 이후 |
| --- | --- | --- |
| 활성 OSC class_type | WrenchRefactorOSCAction | UR10OperationalSpaceControllerAction |
| 상대 명령 기준 축 | 현재 offset EEF | 로봇 root |
| Jacobian·속도 계산 | Refactor 전용 override | Final·Revision 공통 클래스의 Isaac Lab 기본 경로 |
| 제어 위치 | 오른손 axia80_link + EEF offset | 동일 |
| 목표 거리 | U(0,방향별최대거리) | U(0.05,방향별최대거리) |
| 금지 영역 | ±X 방위 부채꼴 | 기존 부채꼴 + 시작점 중심 반경5cm 내부 |
| 오른손 자산·질량·Wrist3·Hand·센서·F/T | 현재 v0 구성 | 동일 |
| OSC gain·scale·토크 제한·주기 | 현재 v0 구성 | 동일 |
| 나머지 Scene·MDP·PPO·상속·등록 | 현재 v0/v1/v2 구성 | 동일 |

변경 소스는 mdp/actions/wrench_refactor.py, mdp/common/wrench_refactor_layout.py, mdp/event_functions/wrench_refactor.py, mdp/events/wrench_refactor.py다. 두 이벤트 경로에 min_goal_distance=0.05를 명시적으로 전달한다. 각 방향에서 최소 거리를 만족할 수 없는 비정상 구성은 방위를 재추첨하지 않고 오류로 처리하여 허용 방위 균등 계약을 보존한다. 5cm 경계는 허용하고 목표 중심의 XY 거리로 판정한다. 목표 구체3cm의 표면까지5cm를 띄우는 의미는 아니다.

공통 OSC 소스를 확인한 결과 손 관절·왼손 자산·왼손 부호는 하드코딩되지 않는다. cfg로 받은 robot/Arm6축/body/offset과 해당 articulation의 Jacobian·질량행렬·중력항을 읽는다. Refactor Scene의 vendor 오른손 USD와 axia80_link offset (0,0,0.1427), quaternion (0.5,-0.5,-0.5,-0.5)를 유지한다. UR10이라는 클래스 이름은 UR10 자산을 불러온다는 의미가 아니다. 기존 Refactor 전용 클래스는 과거 검증 재현용 정의로 남아 있지만 활성 설정에서는 사용하지 않는다.

Final·Revision의 기본 Jacobian/속도 경로까지 일치시키는 요청으로 해석했다. EEF 전용 보정이 물리적으로 개선되었다고 주장하지 않는다. 관측·보상 EEF와 F/T reference는 바꾸지 않았다. 이전 EEF 축 기반 정책 checkpoint는 같은 action을 다른 방향으로 실행할 수 있으므로 재학습 결과와 혼동하지 않는다.

## 검증 및 실패 이력

CPU 회귀181개 통과(24.33초). Refactor/Wrench 전계열 및 tactile 회귀를 실행했다. deadzone0/5/10/15/20/25/30도 각각50,000개(총350,000개)에서 방위 히스토그램·양옆 비율·거리 조건부 균등·최소5cm·선반 경계를 검사했다. 활성 OSC 선언은 Final·Revision과 callable 및 모든 action 인자가 동일함을 비교했다. 이전 EEF 전용 클래스 테스트도 과거 정의 검증으로 남아 있으며 현재 활성 동작의 근거로 사용하지 않는다.

첫 설정 비교 테스트는 CPU fixture가 actions의 Isaac Lab import를 제공하지 않아 실패했다. 선언 AST로 비교하는 검사로 교체한 뒤 Path import 누락도 수정했다. 구현 실패를 테스트 기준 완화로 덮지 않고 실제 GPU의 활성 클래스·root 축 명령 검증을 추가했다. 재개 이전 GPU 시험은 중단되어 결과 파일이 없었으므로 통과로 계산하지 않았다.

오른손 USD probe는 원본 오른손 metadata·30개 hand body·총790g·양의 질량/관성·조인트·F/T 조립 및 선반 MassAPI 회귀를 통과했다. 실제 GPU 시험 결과는 아래에 기록한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench.py src/inspire_sweep_baseline/tests/test_wrench_v0_1.py src/inspire_sweep_baseline/tests/test_wrench_v0_2.py src/inspire_sweep_baseline/tests/test_wrench_v0_3.py src/inspire_sweep_baseline/tests/test_wrench_v1.py src/inspire_sweep_baseline/tests/test_tactile_projection.py src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B src/inspire_sweep_baseline/tests/_wrench_refactor_probe.py --task Inspire-Wrench-Refactor-v2 --num_envs 32 --output outputs/wrench_refactor_validation/root_osc_min5_gpu

/home/min/miniconda3/envs/newton/bin/python -B src/inspire_sweep_baseline/tests/_wrench_refactor_asset_probe.py
```

학습·룰 기반 좌우 밀기 성능은 이번 변경에서 재검증하지 않았다. v0/v1/v2의 보상 함수·weight와 PPO는 이번 변경으로 조정하지 않았다. 기존 목표 영역 그림은 최소 거리0이던 당시 그림이므로 현재 영역 설명으로 사용하지 않는다.

실제 GUI v2 32환경 검증 통과: runtime이 공통 OSC를 인스턴스화하고 오른손 USD·EEF offset을 사용하는지 확인했다. 실제 articulation에서 +X/+Y/+Z 각 명령을 처리하여 원하는 위치 delta가 root 축으로 각각0.03m임을 검증했다. 선반30kg/Hand790g readback·관측74/74/64/64·부분reset·커리큘럼8지점에서 목표 최소5cm와 각36step(총288step) 유한 관측/보상·물성불변을 통과했다. 측정38.86초,reset66.5–80.0ms. v2와 v1의 전체 설정 차이는 기존 거리 callable뿐임도 확인했다. 산출물은 workspace의 `outputs/wrench_refactor_validation/root_osc_min5_gpu/probe_32.json`, `root_osc_min5_cpu.log`, `root_osc_min5_asset.log`, `root_osc_min5_v2_gpu.log`다.

문서 검증: 변경8파일 수식 검사와 양쪽 저장소 diff 공백 검사를 통과했다. 재구성 부록의117개 record 전체 SHA-256 및 Python 문법 검사를 통과했다. 이번 변경의4개 소스 및 reference_config를 갱신했고 기존 v0 전용 재구성 등록은 유지했다. 링크267개 중 새 링크 오류는 없으며 기존 패키지 README의 FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md 누락 링크 한 개는 범위 밖 상태로 기록한다.

기반 v0 자체의 GUI32환경 시험도 동일 검사로 통과했다. 오른손 root축 +X/+Y/+Z·EEF offset·최소 목표5cm·8회 reset/288step·부분reset·질량/물성/관측 차원을 확인했다. 측정38.51초, reset 65.5–81.8ms. 결과 `outputs/wrench_refactor_validation/root_osc_min5_v0_gpu/probe_32.json`, 로그 `root_osc_min5_v0_gpu.log`. v1은 공유 기반 설정과 v2의 부모 보존 검사로 대조했고 별도 GUI 프로세스는 실행하지 않았다.
