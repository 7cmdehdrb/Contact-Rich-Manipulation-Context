# Clutter Fusion v1 수치 일정 변경

이 문서는 최초 v1 구현의 역사 기록이다. 현재는 [Fusion v3](2026-10-21_clutter_fusion_v3.md)으로 이름과 부모를 변경했으며 상속은 v0 → v2 → v3이다. 아래 당시 수치·명령은 현재 실행 안내와 구분한다.

[활성 환경](../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md.txt) · [개발 로그 목록](README.md) · [패키지 계약·실행](../../../../src/inspire_sweep_baseline/README.md#contact-sweep-clutter-fusion-v3--수치-일정-변경)

기준일: 2026-10-21. 사용자 요청에 따라 Fusion v0를 상속한 수치 변형을 구현했다. 학습·정책 성능·실물 검증과 구분한다.

## 기준 코드와 작업트리

- Workspace branch `main`, HEAD: `a9524184a2cdb4cab2bca139a114b7076cbbf7d7`.
- 문서 submodule branch `main`, HEAD: `1f12971369cae13f74b1fd514e043f9eda8f1512`. 시작 시 상위 저장소의 submodule 참조와 달랐으며 내부 작업트리는 clean이었다. checkout·commit·참조 갱신은 수행하지 않았다.
- 시작 시 Fusion `rewards_cfg.py`에 기존 클래스명을 `ddContactSweepClutterFusionRewardsCfg`로 바꾸는 사용자 변경이 있었다. 그 이름은 보존하고 `ContactSweepClutterFusionRewardsCfg` alias를 추가해 부모 Env Cfg의 기존 import를 연결했다. 보상 수치는 수정하지 않았다.

## 환경과 상속

Gym ID는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1`이다. Env는 부모 `ContactSweepClutterFusionEnv`를 재사용한다. 새 `contact_sweep_clutter_fusion_v1`의 `ContactSweepClutterFusionV1EnvCfg`, `ContactSweepClutterFusionV1CurriculumCfg`, `ContactSweepClutterFusionV1PPORunnerCfg`는 각각 Fusion v0의 해당 Cfg를 상속한다. PPO의 experiment 이름은 `inspire_contact_sweep_clutter_fusion_v1`, 실행 runner는 기존 `CurriculumOnPolicyRunner`다.

Scene·물성·reset·policy55D·obstacles40D·Critic의 추가 privileged3D·8D Action·제어·보상 callable·나머지 종료는 부모를 상속한다. `push_fast.speed_condition`만 0.8→1.5 m/s로 변경한다. 통합 action rate의 raw 제곱합과 그룹별 상한, joint velocity의 Arm −0.03·Hand −0.01 효과, wrench weight −0.1·최대 −0.1/초·누적 양의 보상 5% 예산은 부모 설정을 유지한다.

## 적용 일정

0부터 시작하는 Learning iteration을 사용한다. 보상 일정은 iteration 499까지 초기값이며 **500에서 첫 증감**, 이후 지정 간격마다 갱신한다. 반복 reset에 누적 증감하지 않고 iteration에서 값을 직접 재계산한다. Checkpoint 로드·iteration 되감기에도 같은 식을 적용한다.

| 항목 | 초기값 | 증감 | 간격 | 최종값 | 최종 도달 iteration |
| --- | --- | --- | --- | --- | --- |
| pushing free speed | 0.1 m/s | −0.01 | 100 | 0.03 | 1100 |
| arm free speed | 1.0 rad/s | −0.02 | 100 | 0.8 | 1400 |
| action rate weight | −0.03 | −0.005 | 100 | −0.06 | 1000 |
| EEF free speed | 1.5 m/s | −0.02 | 500 | 0.5 | 25000 |
| contact_any weight | 0.4 | +0.02 | 100 | 2.0 | 8400 |
| contact_count weight | 0.4 | +0.02 | 100 | 2.0 | 8400 |
| wrench free force rate | 2000 N/s | −50 | 100 | 500 | 3400 |
| wrench free moment rate | 100 N·m/s | −2.5 | 100 | 25 | 3400 |
| wrench saturation force rate | 5000 N/s | −125 | 100 | 1250 | 3400 |
| wrench saturation moment rate | 250 N·m/s | −6.25 | 100 | 62.5 | 3400 |

EEF는 요청의 “나머지는 같음”에 따라 기존 500 간격을 유지한다. Goal deadzone은 기존 start=60°·hold=1000·decrement=1°를 유지하고 interval만 200→100으로 수정한다. 1100에 59°, 7000에 0°다. Goal 일정은 다음 reset의 샘플링 분포만 바꾸며 진행 중 목표는 유지한다. 기존 runner가 rollout 전에 보상 일정을 적용하며 checkpoint 로드 시 단계를 복원하고 재생 중에는 고정한다.

## 실행

Workspace 루트에서 실행한다. 자산 경로는 부모와 동일하며 필요하면 `INSPIRE_SWEEP_SHELF_USD_PATH`를 지정한다. 기본 선반 경로는 `omniverse://192.168.0.13/Library/Shelf/Arena/Collected_speedrack_shape/speedrack_shape.usd`다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1 --num_envs 1 \
  --checkpoint "<fusion-v1-checkpoint.pt>"
```

위 명령은 실행 안내이며 실제 학습·재생은 수행하지 않았다. 학습 로그 이동·삭제는 수행하지 않았다.

## 실제 검증과 한계

초기 관련 검사에서 아래 명령으로 **45 passed**를 확인했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_curriculum.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_curriculum.py \
  src/inspire_sweep_baseline/tests/test_clutter_v1_curriculum.py
```

v1의 첫 변경·다음 변경·최종값 직전·최종값·상하한 유지·반복/부분 reset·iteration 되감기, contact 동기 증가, wrench free/saturation 관계, 진행 중 목표와 joint velocity 유지, Gym 등록과 부모 초기화·설정 복사 격리를 검사했다. 기존 runner의 실제 CPU PPO·checkpoint 재개·고정 재생 검사도 포함한다.

실제 configclass 상속 검사를 추가한 뒤 루트 README의 전체 CPU 명령(위 명령에서 파일 인수 제거)을 실행한 최초 결과는 **523 passed, 2 failed**였다. 새 v1을 환경군 표에 추가하지 않은 `test_termination_debug.py`를 수정했다. 나머지 실패는 기존 telemetry 테스트가 요구하는 `logs/inspire_contact_sweep_clutter_v1_curriculum/2026-10-20_22-49-30/model_12800.pt` 부재였다. 이 체크포인트를 생성·대체하거나 기존 검사를 수정하지 않았다. 해당 검사 하나만 명시적으로 제외해 재실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  --deselect src/inspire_sweep_baseline/tests/test_clutter_ft_telemetry.py::test_requested_checkpoint_loads_strictly_and_runs_cpu_inference
```

최종 결과는 **524 passed, 1 deselected, 17 subtests passed**(19.54초)이며 Torch ONNX deprecation warning 3개가 있었다. v1 커리큘럼·새 부모 격리 검사, 기존 Fusion 보상·관측·모델 검사도 포함한다. 환경 설정 격리 검사는 실제 configclass와 최소 부모 대역을 사용한 CPU 검사로, 실제 simulator의 Env Cfg 생성과 구분한다.

문서 검사와 문법 검사도 수행했다.

```bash
git diff --check
git -C example/Contact-Rich-Manipulation-Context diff --check

python example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_markdown_math.py \
  src/inspire_sweep_baseline/README.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/logs/README.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/logs/2026-10-21_clutter_fusion_v1.md

python example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_document_links.py \
  --root example/Contact-Rich-Manipulation-Context --check-external \
  example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/logs/README.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/logs/2026-10-21_clutter_fusion_v1.md
```

양쪽 diff 검사와 Markdown 수식 4파일·문서 링크 3파일 검사가 통과했다. 새 v1 Python 5파일과 테스트 1파일을 `ast.parse`로 검사해 총 6파일 문법 통과를 확인했다.

`nvidia-smi --query-gpu=name,memory.free --format=csv,noheader`는 exit 9로 실패했다. NVIDIA driver에 연결할 수 없는 상태이므로 실제 Isaac Sim/PhysX 환경 생성·GPU step·학습·재생은 미실행이다. CPU 검사는 실시간 F/T·접촉 물리·정책 성능을 입증하지 않는다. 학습 run·checkpoint·seed는 생성하지 않았다.
