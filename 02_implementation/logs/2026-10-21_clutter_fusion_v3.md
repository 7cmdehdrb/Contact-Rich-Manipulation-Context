# Fusion v0 → v2 → v3 상속 재구성

[활성 환경](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-fusion-v3--2026-10-21) · [로그 목록](README.md) · [실행·수치 안내](../../../../src/inspire_sweep_baseline/README.md#contact-sweep-clutter-fusion-v3--수치-일정-변경) · [최초 v1 기록](2026-10-21_clutter_fusion_v1.md)

기준일: 2026-10-21. 사용자 요청에 따라 기존 `v0 → v1`, `v0 → v2`를 **`v0 → v2 → v3`**으로 재구성했다. v2는 v0에서 EEF orientation 보상을 제거하고 push_fast 임계값을 1.5로 높인 버전이며, v3은 v2에서 커리큘럼만 변경한다.

## 기준 상태와 변경

- Workspace HEAD: `09348b4dc08b7dda67e7d25a8153997348309d80`.
- 문서 submodule HEAD: `9dfd82aa2c4f16737e737a5a3b533e1e129c7cdf`. 내부 작업트리는 시작 시 clean이었다.
- 시작 시 `contact_sweep_clutter_fusion_v1/curriculum_cfg.py`에는 사용자 수정이 있었다. 200 간격, Arm minimum=0.7, EEF minimum=0.3, wrench 최종값 1000/50/2500/125 등 **현재 작업트리 값**을 보존하여 v3으로 이동했다.
- 기존 Fusion v1의 `push_fast=1.5`는 커리큘럼 외 변경이었다. “v3은 v2에서 커리큘럼만 변경” 조건에 맞춰 이 override를 제거하고 v2의 0.8을 상속한다. 작업 중 사용자에게 이 차이를 알렸다.

패키지 `contact_sweep_clutter_fusion_v1`과 테스트 `test_clutter_fusion_v1_curriculum.py`를 각각 `contact_sweep_clutter_fusion_v3`, `test_clutter_fusion_v3_curriculum.py`로 이동했다. 클래스 이름·Gym ID·experiment 이름의 Fusion v1도 v3으로 변경했으며 v1 등록은 제거했다. 기존 v1 로그·checkpoint는 그대로 보존했고, 최초 개발 로그는 역사 기록으로 표시했다. Commit·submodule 참조 갱신·학습 로그 정리는 수행하지 않았다.

## 최종 계약

| 환경 | Env Cfg 부모 | 변경 |
| --- | --- | --- |
| `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v0` | Isaac Lab `ManagerBasedRLEnvCfg` | 독립 Fusion 기준 |
| `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v2` | `ContactSweepClutterFusionEnvCfg` | `eef_orientation=None`, `push_fast=1.5` |
| `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v3` | `ContactSweepClutterFusionV2EnvCfg` | curriculum을 `ContactSweepClutterFusionV3CurriculumCfg`로 교체 |

PPO Cfg도 Fusion v0 → v2 → v3을 따른다. v3의 experiment 이름은 `inspire_contact_sweep_clutter_fusion_v3`이며, runtime은 기존 `ContactSweepClutterFusionEnv`, runner는 `CurriculumOnPolicyRunner`다. Curriculum Cfg는 v2가 그대로 사용하는 v0의 `ContactSweepClutterFusionCurriculumCfg`를 확장한다. 별도 v2 Curriculum 클래스는 만들지 않는다.

v3의 관측 policy55D·obstacles40D·Critic 추가 privileged3D, Action 8D, 제어·Scene·reset·보상 설정·종료 설정은 v2와 같다. `eef_orientation=None`, `push_fast.speed_condition=1.5`다. 최초 재구성 때는 v0·v2 코드를 유지했으나 후속 요청으로 v2에 push_fast=1.5를 추가했다.

현재 v0/v2의 보상 커리큘럼은 300 간격이며 goal hold=500·interval=200이다. 기존 테스트와 문서가 이전 500 간격·hold=1000을 기대하고 있어, 현재 코드에 맞게 기대값·문서만 수정했다. 이 작업에서 v0의 수치를 바꾼 것은 아니다.

v3 보상 일정은 iteration 500에서 첫 증감 후 200마다 갱신한다. Pushing 0.1→0.03, Arm 1.0→0.7, action weight −0.03→−0.06, EEF 1.5→0.3, contact 두 항 각각 0.4→2.0이다. Wrench free force/moment는 2000/100→1000/50, saturation force/moment는 5000/250→2500/125다. Goal은 ±60°·hold=1000·interval=100으로 1100에서 첫 감소, 7000에 0°다. 세부 증감·최종 도달 iteration은 패키지 안내를 따른다.

## 실행

Workspace 루트에서 부모와 같은 Isaac Lab·자산 설정으로 실행한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v3 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v3 --num_envs 1 \
  --checkpoint "<fusion-v3-checkpoint.pt>"
```

## 실제 검증과 한계

관련 검사를 아래 명령으로 실행하여 **33 passed**(1.65초)를 확인했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v3_curriculum.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_curriculum.py \
  src/inspire_sweep_baseline/tests/test_termination_debug.py
```

최초 관련 검사에서는 v0의 이전 수치를 기대하던 9개 항목이 실패했다. 현재 v0 설정(300 간격·hold=500)을 확인한 뒤 테스트 기대값을 갱신하여 위 결과를 얻었다. v3의 전체 상하한·시작/다음 경계·되감기·반복 reset·goal 유지·joint velocity 유지, v1 등록 부재와 v3 등록, 공식 configclass를 통한 v0→v2→v3 상속·보상 제거·종료값 유지·부모 격리를 검사했다. 전체 Env Cfg 기반 부분은 최소 대역을 사용한 CPU 검사로 실제 simulator 생성과 구분한다.

위 명령에서 파일 인수를 제거한 전체 CPU 검사 결과는 **529 passed, 1 failed, 17 subtests passed**(19.26초)였다. 실패는 기존 `test_clutter_ft_telemetry.py::test_requested_checkpoint_loads_strictly_and_runs_cpu_inference`가 요구하는 다음 체크포인트 부재다.

```text
logs/backup/Isaac-Inspire-Contact-Sweep-Clutter-Curriculum-v1/2026-10-20_22-49-30/model_12800.pt
```

체크포인트를 생성·대체하거나 테스트를 비활성화하지 않았다. ONNX deprecation warning 3개가 있었다. 실제 Isaac Sim/PhysX 환경 생성·GPU 학습·재생·성능 평가는 미실행이며 새 run·checkpoint·seed를 생성하지 않았다.

문서 검증은 `check_markdown_math.py`에 변경 Markdown 6파일을 전달하여 통과했고, `check_document_links.py --root example/Contact-Rich-Manipulation-Context --check-external`에 변경 submodule Markdown 5파일을 전달하여 오류 0건을 확인했다. 양쪽 저장소의 `git diff --check`도 통과했다.

## 후속 요청: v2에 push_fast=1.5 추가

사용자 명시 요청으로 v2의 `__post_init__`에 `self.terminations.push_fast.params["speed_condition"] = 1.5`를 추가했다. v3은 별도 override 없이 1.5를 상속하며, v0는 0.8을 유지한다. v2의 orientation 보상 제거와 v3의 커리큘럼은 유지한다. 상속 검사에서 v3=1.5, v0=0.8과 부모 격리를 확인하도록 기대값을 갱신했다.

위 관련 CPU 검사 명령을 다시 실행한 결과 **33 passed**(1.59초)였다. 실제 GPU 실행은 미검증이다.
