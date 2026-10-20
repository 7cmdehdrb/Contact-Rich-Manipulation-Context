# Clutter v1 Curriculum — Learning iteration 기반 네 보상 일정

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-curriculum-v1--2026-10-20) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md#contact-sweep-clutter-curriculum-v1--learning-iteration-기반-보상)

## 요청·기준과 상속

사용자는 현재 v1을 상속하는 별도 환경에서 물체·Arm free speed와 Arm action-rate·joint-velocity 가중치를 Learning iteration 기준으로 감소시키도록 요청했다. Arm 두 가중치 변화는 이번 명시 요청에 따른 예외이며 기존 v1·다른 환경의 계수를 변경하지 않는다.

작업 시작 workspace commit은 `f1a9c709739c0b87ff8f403b2a3d5093cb707895`, IsaacLab은 `929f0fe1e9c1699efebf31b2ad0ab723a7d6e7e9`, 문서 저장소는 `e133c097bbfea954165e346f008921ff9ebf80eb`다. 시작 시 상위 저장소의 문서 submodule 참조와 v1 `rewards_cfg.py`에 기존 변경이 있었다. 이를 보존하며 commit·push는 수행하지 않았다.

Gym ID는 `Isaac-Inspire-Contact-Sweep-Clutter-Curriculum-v1`, 로그 폴더는 `logs/rsl_rl/inspire_contact_sweep_clutter_v1_curriculum`이다. `contact_sweep_clutter_v1_curriculum`의 Env·EnvCfg·RewardsCfg·PPORunnerCfg는 각각 현 v1을 직접 상속한다. 상세 클래스·등록·실행은 [활성 환경](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-curriculum-v1--2026-10-20)에 기록한다.

Actor/Critic 관측, 제어, 물리·reset·종료는 v1과 같다. 네 대상 외의 보상도 상속한다. Hand 가중치는 −0.03/−0.01이며 운동 비용은 기존 로컬 raw 제곱합·출력 상한·RewardManager의 dt 적용을 유지한다.

## 적용 일정

표의 iteration부터 다음 경계 직전까지 해당 값을 사용한다.

| Learning iteration | 물체 free speed (m/s) | Arm free speed (rad/s) | Arm action-rate weight | Arm joint-velocity weight |
| --- | --- | --- | --- | --- |
| 0 | 0.10 | 1.00 | −0.030 | −0.030 |
| 3,000 | 0.09 | 1.00 | −0.035 | −0.035 |
| 5,000 | 0.09 | 0.95 | −0.035 | −0.035 |
| 6,000 | 0.08 | 0.95 | −0.040 | −0.040 |
| 9,000 | 0.07 | 0.95 | −0.045 | −0.045 |
| 10,000 | 0.07 | 0.90 | −0.045 | −0.045 |
| 12,000 | 0.06 | 0.90 | −0.050 | −0.050 |
| 15,000 | 0.05 | 0.85 | −0.055 | −0.055 |
| 18,000 | 0.05 | 0.85 | −0.060 | −0.060 |
| 20,000 이후 | 0.05 | 0.80 | −0.060 | −0.060 |

`curriculum_cfg.py`에 시작값·감소량·주기·하한을 정의한다. 각 항은 `start - decrement * (iteration // interval)`을 하한으로 제한한다. 현재 값에서 반복 차감하지 않으므로 병렬 환경의 부분 reset·같은 iteration 재호출·이전 checkpoint 로드로 일정이 어긋나지 않는다.

## Runner 연결과 재개 의미

설치된 RSL-RL 5.0.1은 `for it in range(start_it, total_it)`에서 rollout·학습을 마친 뒤 `current_learning_iteration = it`를 기록한다. 해당 값을 rollout 중에 그대로 읽으면 한 iteration 늦는다.

`CurriculumOnPolicyRunner`는 `OnPolicyRunner`를 상속하고 VecEnv 전달 어댑터를 사용한다. `learn()` 진입 시 runner의 시작 index와 실제 `num_steps_per_env`를 받으며, 실제 수집 step 수로 각 rollout 시작을 식별한다. PPO loop를 복사하지 않고 `set_learning_iteration(i)`를 첫 보상 계산 전에 호출한다. 기본 36 step을 하드코딩하지 않으며 환경 수·physics step·episode 길이를 사용하지 않는다. 초기 episode 길이 무작위화의 버퍼 대입도 실제 VecEnv에 전달한다.

환경 setter는 `CurriculumManager.compute()`를 통해 실행 중인 `RewardManager`의 term을 갱신한다. 현재 episode에도 즉시 반영한다. 일반 reset에서도 네 항이 동일 절대값을 계산한다. CurriculumManager가 네 현재값을 TensorBoard의 `Curriculum/*`로 기록한다.

`load()`는 checkpoint 내부 `iter`를 반영하고 재생은 그 단계에 고정한다. RSL-RL의 원래 재개 동작대로 저장된 index에서 다시 시작하며 임의로 `+1`하지 않는다. `learn()`이 끝나면 어댑터의 자동 진행도 중지한다. 환경만 직접 생성하면 초기 iteration 0이며 다른 실행기는 setter를 연결해야 한다. 기본 train/play는 PPO Cfg의 `class_name="CurriculumOnPolicyRunner"`를 처리한다.

## 검증

CPU 검증 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_clutter_v1_curriculum.py \
  src/inspire_sweep_baseline/tests/test_clutter_v1_models.py \
  src/inspire_sweep_baseline/tests/test_clutter_v1_rewards.py \
  src/inspire_sweep_baseline/tests/test_clutter_v1_shelf_failure.py \
  src/inspire_sweep_baseline/tests/test_contact_sweep.py
```

최종 결과는 **57 passed, 1 warning (3.55초)**다. 경고는 기존 ONNX export의 PyTorch deprecation이다. 첫 검사에서 테스트가 이미 소비된 RSL-RL config dict를 두 번째 runner에 재사용해 두 건의 `KeyError: class_name`이 발생했으며, 테스트가 runner별 config 사본을 전달하도록 수정한 뒤 통과했다.

검사 범위는 일정 경계·하한·반복 reset·과거 단계 복원, 기존 보상 함수·상한 보존, 실제 configclass 기반 v1 보상 상속과 인스턴스 격리, 등록·실행기 선택이다. 실제 설치된 RSL-RL runner와 v1 Actor/Critic 모델로 CPU toy VecEnv에서 2·4 step rollout, 2,999→3,000 및 4,999→5,000 경계, 학습·checkpoint 저장·load·재개·재생 고정을 검사한다. 물리 시뮬레이션 성능 검사가 아니다.

GPU lifecycle 시도:

```bash
timeout 90s env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_clutter_v1_curriculum_probe.py \
  --headless --device cuda:0 --output /tmp/clutter_v1_curriculum_probe.json \
  > /tmp/clutter_v1_curriculum_probe.log 2>&1
```

현재 세션에는 `/dev/nvidia*`가 없고 `nvidia-smi`는 driver 통신 실패를 반환했다. Isaac Sim도 `cudaErrorNoDevice`, `No CUDA devices found`, `Unable to create PxCudaContextManager`를 출력했다. 프로세스 exit code는 0이었으나 완료 JSON이 생성되지 않았으므로 GPU lifecycle은 통과하지 않았다. 이 실행으로 환경의 실제 물리·장기 학습 성공을 주장하지 않는다. Probe는 GPU 사용 가능 시 동일 명령으로 config 상속·네 값의 실제 manager 반영·부분 reset·유한 관측/보상을 검증하도록 남긴다.

문서·정적 검사:

- 새 환경·runner·실행기·검증 파일 12개의 Python AST parsing 통과.
- `git diff --check` 및 문서 저장소의 `git diff --check` 통과.
- `check_markdown_math.py`에 변경한 Markdown 5개를 전달하여 통과.
- 문서 저장소 전체 `python 00_guidelines/scripts/check_document_links.py --check-external`은 기존 파일의 외부 자료 누락 4건으로 실패했다. `2026-10-14_omni_immediate_termination.md`의 과거 로그 폴더 3개와 `2026-10-15_dex_omni_rewards.md`의 DexTouch PDF이며 이번 변경 링크 오류는 보고되지 않았다.
- 변경 문서만 대상으로 `python 00_guidelines/scripts/check_document_links.py --check-external 01_plan/00_HANDOFF_BRIEF.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-20_clutter_v1_curriculum.md`를 실행한 결과 4파일·내부 링크 146개·외부 파일 링크 36개, 오류 0개로 통과했다.

장기 학습, 실제 속도 감소와 목표 유지 성능, 다중 GPU 학습은 미검증이다. 커리큘럼의 정확한 적용과 정책 성능 향상은 별개다.
