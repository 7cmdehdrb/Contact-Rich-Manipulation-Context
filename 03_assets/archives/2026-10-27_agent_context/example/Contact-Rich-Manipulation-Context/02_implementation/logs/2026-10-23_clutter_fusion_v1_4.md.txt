# Fusion v1_4 — v1_0 직접 계승 보상 보정 환경

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-fusion-v1_4--2026-10-23) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md#contact-sweep-clutter-fusion-v1_4)

## 요청·기준과 구현

학습된 v1_0을 이어 보상·페널티 기준을 보정하는 환경을 구성했다. Workspace 기준 commit은 `dab4a8d84efa6b564e91d198cc68f1301115e476`, 문서 submodule 기준은 `c0e2568ce63d76a3f985dd086b6dc910837bcb8b`이다. 시작 시 양쪽에 미커밋 변경이 있었으며 기존 수정과 계측 파일을 보존했다. 학습 로그를 이동·삭제하지 않았다.

등록 ID는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_4`다. `ContactSweepClutterFusionV1_4EnvCfg`와 `ContactSweepClutterFusionV1_4PPORunnerCfg`는 각각 v1_0 클래스를 직접 상속한다. Reward·Termination·Curriculum CFG도 v1_0에서 상속하여 필요한 항만 교체한다. v1_0_x 및 v1_1–v1_3 계열을 참조하지 않는다. Runtime은 `ContactSweepClutterFusionV1_0Env`, runner는 `CurriculumOnPolicyRunner`, experiment는 `inspire_contact_sweep_clutter_fusion_v1_4`다. 소스는 `src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_4/`다.

## 최종 계약

| 항목 | 적용 일정·수치 |
| --- | --- |
| Arm free speed | 1.0, 500에서 0.98로 첫 감소, 이후 기존 기울기 −0.02/200을 250 간격으로 표본화, 3300에서 정확히 0.7 |
| EEF free speed | 1.5, 500에서 1.48로 첫 감소, 이후 −0.02/200 기울기·250 간격, 13300에서 0.2 |
| Pushing free speed | 0.1, 500에서 0.09로 첫 감소, 이후 −0.01/200 기울기·250 간격, 1900에서 0.02 |
| Deadzone | v1_0 그대로: 30°, 3000까지 유지, 3500부터 500마다 5° 감소, 6000에서 0° |
| Object free acceleration | 10000 미만 100, 10000에서 50으로 전환, 12000까지 50, 이후 250 간격 선형 감소, 18000에서 10 |
| Wrench free force change | 10000 미만 5000, 10000에서 200, 12000까지 유지, 이후 250 간격 선형 감소, 18000에서 100 |
| Wrench free moment change | 10000 미만 500, 10000에서 30, 12000까지 유지, 이후 250 간격 선형 감소, 18000에서 20 |
| Goal hold tolerance | 5000 미만 0.0, 5000에서 0.01, 이후 250 간격 선형 감소, 10000에서 0.005 |
| 장애물 | Gray1/White1 시작. White는 3000부터 3000마다 증가하여 12000에 5개. Gray는 4500부터 3000마다 증가하여 13500에 5개. 최종 Target1 포함 11개 |
| Goal hold·Hand contact weight | 각각 0.9→9.0, 0.29→1.45 |
| Push fast | 0.8→1.0 m/s |
| Success | 현재 Goal hold의 XY 반경 안에서 연속 3초 유지하면 일반 termination. 이탈·실패·해당 환경 reset 시 타이머 초기화 |

사용자 문장의 Goal 반경 “증가”는 명시한 0.01→0.005 수치를 우선하여 감소로 구현했다. 반경 0은 Goal hold 보상과 성공 판정 비활성화로 해석했다. 기존 `goal_hold_xy`가 0을 거부하므로 v1_4 전용 wrapper를 사용한다. 성공은 Goal hold와 같은 월드 XY 조건을 사용하며 별도 속도·자세 성공 조건은 추가하지 않는다. 기존 실패가 같은 step에 발생하면 성공은 억제한다. 0.02초 제어 주기에서 연속 150 step이며 timeout이 아닌 종료다.

250 간격과 기존 Arm 도달 시점 3300이 정렬되지 않으므로, 각 ramp의 마지막 구간은 짧게 끝내 정확한 endpoint를 적용한다. EEF·Pushing에도 같은 원칙을 사용한다. 감소율과 500에서의 첫 감소를 보존한다. 가속도·Wrench는 12000에서 유지값으로 ramp를 시작하므로 첫 추가 감소는 12250이다. 모든 일정은 절대 learning iteration에서 계산하므로 resume·rewind 시 같은 값을 복원한다. 큰 초기 임계값은 무한 제한 해제가 아니라 요청한 유한 free threshold다. Wrench는 v1_0과 동일한 **크기 변화량** 비용이며 절대 힘·모멘트 비용으로 바꾸지 않는다.

Scene·Event·관측·Action·제어·물성은 v1_0 계약을 계승한다. Scene capacity는 Gray5/White5이며 10개 장애물 슬롯의 40D 관측 구조를 유지한다. 초기 관측 policy55D·obstacles40D·privileged3D, Action8D와 PPO 구조가 같으므로 v1_0 checkpoint를 불러오는 구성이다. Episode 중 물체 수를 바꾸지 않고 다음 reset에 개수를 반영한다. Hand contact fade=0, 장애물 접촉 free force=2000 및 나머지 보상은 v1_0 그대로다. Arm/Hand raw Action 변화량·실제 관절 속도 제곱합 네 항과 −0.03/−0.03/−0.03/−0.01 계수도 유지한다.

## 실행

Workspace 루트에서 선택한 v1_0 run의 절대 경로와 checkpoint를 지정한다. 학습 실행은 이번 작업에서 수행하지 않았다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_4 \
  --num_envs 2048 --headless --resume \
  --load_run "<v1_0-run-절대경로>" --checkpoint "<model_ITER.pt>"

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_4 \
  --num_envs 1 --checkpoint "<checkpoint-절대경로.pt>"
```

Resume는 checkpoint의 iteration과 optimizer 상태를 복원하고 그 시점의 v1_4 커리큘럼을 적용한다. 예를 들어 iteration 16400에서는 이미 Goal 반경이 0.005이고 장애물은 5/5다. 학습된 가중치를 사용하면서 커리큘럼을 0부터 다시 시작하는 동작은 포함하지 않는다. 새 run은 v1_4 experiment 경로에 저장된다.

## 실제 검증과 한계

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_4.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_cfg.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_population.py
```

결과: **47 passed in 3.09s**. 실제 schedule 함수의 경계·중간값·최종 유지·부분 reset 호출·rewind, 공식 configclass를 통한 상속·부모 독립성·가중치·최종 속도 종료값·성공 term 순서, 실제 tensor 기반 3초 타이머·이탈·반경 변경·실패·부분 reset을 검증했다. 타겟/목표 고정 기하 생성기로 128개 Gray5/White5 장면의 배치 인증도 통과했다. 초기 테스트의 fixture import 및 목표 거리 fixture를 수정했으며, 공식 configclass가 class field를 옮기는 동작에 맞춰 부모 term 접근을 인스턴스 기반으로 고쳤다.

`nvidia-smi --query-gpu=name,memory.used,memory.free --format=csv,noheader`는 exit 9로 실패했고 NVIDIA driver와 통신할 수 없다고 출력했다. 따라서 GPU PhysX 실행·실제 checkpoint load·PPO rollout·장시간 학습·성공률 향상은 미검증이다. CPU 기하 인증은 실제 접촉 물리나 11개 물체의 동적 안정성을 증명하지 않는다.

문서 검증은 Workspace 루트에서 아래 명령을 실제 실행했다. 수식 검사는 4파일 통과, 링크 검사는 문서 submodule의 변경 3파일에서 오류 0(내부171·외부42 링크), 두 저장소의 diff whitespace 검사도 통과했다. 새 Python 9파일은 `ast.parse`로 문법을 확인했다.

```bash
python example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_markdown_math.py \
  src/inspire_sweep_baseline/README.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/logs/README.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/logs/2026-10-23_clutter_fusion_v1_4.md
python example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_document_links.py \
  --root example/Contact-Rich-Manipulation-Context --check-external \
  example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/logs/README.md \
  example/Contact-Rich-Manipulation-Context/02_implementation/logs/2026-10-23_clutter_fusion_v1_4.md
git diff --check
git -C example/Contact-Rich-Manipulation-Context diff --check
```
