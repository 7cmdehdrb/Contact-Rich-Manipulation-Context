# Clutter Fusion v2 — EEF 자세 보상 제거

[활성 환경](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-fusion-v2--2026-10-21) · [로그 목록](README.md) · [패키지 실행 안내](../../../../src/inspire_sweep_baseline/README.md#contact-sweep-clutter-fusion-v2--eef-자세-보상-제거)

기준일: 2026-10-21. 최초 요청으로 Fusion v1을 상속하여 EEF orientation 보상을 제거했다. 같은 날 후속 사용자 지시에 따라 **현재 부모는 Fusion v0**로 변경했다. push_fast=1.5를 추가했던 요청은 사용자 정정으로 취소하고, v2는 0.8을 유지하며 v3에서만 1.5를 적용한다. 아래 환경 계약은 현재 기준이며 최초 검사 결과는 별도로 구분한다.

## 코드와 상속

Workspace HEAD는 `de92db4d487b94f63b9baee03f6e16c412556076`, 문서 submodule HEAD는 `1cf505b09963d4c1ef3a6df71f376d75922f766e`다. 시작 시 문서 submodule은 상위 참조와 달랐고 내부 작업트리는 clean이었다. 기존 미추적 `.vscode/extensions.json`을 보존했다. Commit·checkout·학습 로그 정리는 수행하지 않았다.

Gym ID는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v2`다. `contact_sweep_clutter_fusion_v2.env_cfg:ContactSweepClutterFusionV2EnvCfg`는 Fusion v0의 `ContactSweepClutterFusionEnvCfg`를 직접 상속하고 부모 초기화 이후 `self.rewards.eef_orientation = None`만 적용한다. Weight 0이 아니라 term을 비활성화하므로 RewardManager가 해당 callable을 실행하지 않는다.

Runtime은 기존 `contact_sweep_clutter_fusion.env:ContactSweepClutterFusionEnv`다. `contact_sweep_clutter_fusion_v2.ppo_cfg:ContactSweepClutterFusionV2PPORunnerCfg`는 Fusion v0의 `ContactSweepClutterFusionPPORunnerCfg`를 직접 상속하고 실험 폴더 이름만 `inspire_contact_sweep_clutter_fusion_v2`로 분리한다. 정책·PPO·iteration runner의 동작 변경은 없다.

관측 policy55D·obstacles40D·Critic 추가 privileged3D, Action 8D, 제어·Scene·reset·나머지 보상과 커리큘럼은 v0를 상속한다. v0·v1의 설정은 수정하지 않는다. v0의 5개 커리큘럼(속도·action rate 500 간격, goal deadzone 200 간격)을 사용하며, v1의 추가 contact·wrench 커리큘럼은 적용하지 않는다.

## 직접 연관된 종료 조건 확인

부모의 `eef_orientation`은 `eef_upward_z_orientation_cost`로 EEF +Z와 월드 +Z의 각도를 평가한다. Fusion의 termination 목록에는 이 각도나 함수를 사용하는 항목이 없다.

- `object_drop`: 모든 물체의 높이·전도 각도. EEF 자세 조건이 아니다.
- `shelf_collision`: 선반 이동 속도·손목 높이. EEF 자세를 직접 판정하지 않는다.
- `push_fast`, `hand_velocity`(실제 Arm 관절 속도), `shelf_displacement`, `time_out`: 각각 물체 속도·Arm 속도·선반 이동·시간 조건이다.

따라서 제거할 직접 연관 termination은 없고 모든 종료 조건을 v0에서 상속한다. `push_fast.speed_condition=0.8`이며 v3은 이를 1.5로 override한다. 코드 근거는 Fusion의 `terminations_cfg.py`, 로컬 `mdp/terminations.py`, `contact_sweep_clutter/mdp.py`다.

## 실행

Workspace 루트에서 부모와 같은 Isaac Lab·자산 설정으로 실행한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v2 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v2 --num_envs 1 \
  --checkpoint "<fusion-v2-checkpoint.pt>"
```

## 실제 검증과 한계

최초 v1 상속 구현 당시 다음 CPU 검사는 **44 passed**(1.84초)였다. 등록 runtime군 검사에 v2를 추가했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_curriculum.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_curriculum.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_safety_rewards.py \
  src/inspire_sweep_baseline/tests/test_termination_debug.py
```

추가로 `env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -`의 일회성 heredoc으로 공식 Isaac Lab `configclass`와 실제 Fusion rewards 설정·v2 초기화 코드를 실행했다. Simulator 의존성은 대역으로 제공했다. 부모 설정과 비교하여 `rewards.eef_orientation=None`만 달라지는지, 부모 보상이 보존되는지, 부모 초기화가 실행되는지, 새 인스턴스가 격리되는지 확인했다. 실제 Gym registry에서도 v1/v2 runtime 일치와 v2 Env/PPO entry point를 확인하여 통과했다.

`check_markdown_math.py`로 변경 Markdown 4파일, `check_document_links.py --root example/Contact-Rich-Manipulation-Context --check-external`로 변경 문서 submodule Markdown 3파일을 검사하여 오류 0건을 확인했다. 양쪽 저장소 `git diff --check`도 통과했다. 실제 Isaac Sim/PhysX 환경 생성·GPU 학습·재생은 이번 작업에서 실행하지 않았다. Run·checkpoint·seed를 생성하지 않았으며 보상 제거의 학습 성능 효과는 미검증이다.

## 후속 변경: Fusion v0 직접 상속 검증

동일 HEAD·기존 작업트리에서 Env/PPO import와 기반 클래스를 v0로 바꾸고 패키지 설명을 갱신했다. Gym ID·실행 명령·experiment 이름과 `eef_orientation=None`은 유지했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_curriculum.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_safety_rewards.py \
  src/inspire_sweep_baseline/tests/test_termination_debug.py
```

결과는 **31 passed**(1.47초)였다. 별도의 Python heredoc 검사에서 실제 v0 reward·termination·curriculum 설정과 공식 `configclass`를 사용하고 simulator 의존성·전체 부모 Env Cfg는 대역으로 제공했다. 실제 v2 코드 실행 결과가 부모 대비 orientation 보상 제거만 달라지는지, `push_fast=0.8`, 커리큘럼 5개·pushing minimum=0.05·goal interval=200, 부모 격리와 초기화 실행을 확인했다. AST의 실제 import 경로·기반 클래스와 v0 PPO 직접 상속·v2 experiment 이름도 확인하여 통과했다. 실제 simulator 실행 검증은 수행하지 않았다.
