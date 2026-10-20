# Contact Sweep Clutter — 장애물 초기 관측과 학습 임베딩

> 이 문서는 최초 장애물 6개 구성의 구현·검증 기록이다. 같은 날 후속 요청으로 v0의 장애물은 3개, RED 제외 반경은 10.3 cm로 변경했다. 현재 설정은 [후속 로그](2026-10-20_clutter_red_expansion.md)를 따른다.

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-v0--2026-10-20) · [부모 환경](2026-10-20_contact_sweep_reference.md)

## 요청과 확인한 선택

사용자는 새 독립 기준 Contact Sweep을 상속해 장애물 환경을 추가하도록 요청했다. 구현 전에 참고 Scene 생성기와 부모 환경의 차이를 확인하고 다음 답변을 받았다.

- 기존 타겟·목표 분포를 유지하고 `src/scene_randomization`의 장애물 배치 규칙만 적용한다.
- 로봇의 기존 고정 초기 관절 자세를 유지한다.
- 타겟과 모든 장애물의 접촉을 촉각에 반영한다.
- 장애물 위치 관측에는 각 축 ±1 cm 균일 노이즈를 reset 때 한 번 적용하고 고정한다.

참고 생성기 기본값인 장애물 6개를 사용한다. 관측 10칸 중 나머지 4칸은 더미다. 임의의 장애물 개수 분포·새 속도 비용·새 종료 조건은 추가하지 않는다. MLP 구조 선택은 사용자가 허용한 재량이며 `40 → 32(ReLU) → 16`을 채택했다.

기준 workspace commit은 `457c3674c1993daaec8b8062f64f5d368bc7dcd6`, 문서 submodule HEAD는 `e8aba3abbb6a321fdbae0ddc137d1ffee3ff59a4`다. 시작 시 문서 submodule 포인터 변경과 미추적 `src/Universal_Robots_ROS2_Description/`가 있었으며 보존했다. 이번 작업에서 commit·원격 반영은 수행하지 않았다.

## 등록·상속·코드

| 항목 | 구현 |
| --- | --- |
| Task | `Isaac-Inspire-Contact-Sweep-Clutter-v0` |
| Runtime | `ContactSweepClutterEnv(ContactSweepEnv)` |
| 환경 Cfg | `ContactSweepClutterEnvCfg(ContactSweepEnvCfg)` |
| Scene | `ContactSweepClutterSceneCfg(ContactSweepSceneCfg)` |
| Manager | Observation·Event·Reward·Termination은 부모별 Cfg 상속, Action·Command는 그대로 상속 |
| PPO | `ContactSweepClutterPPORunnerCfg(ContactSweepPPORunnerCfg)` |
| 로그 폴더 | `logs/rsl_rl/inspire_contact_sweep_clutter` |

코드는 [`contact_sweep_clutter/`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter)에 모았다. 기존 Contact Sweep·Renewal v3·공유 MDP 함수·실행 스크립트는 수정하지 않았다. 최상위 package 등록에 새 task를 추가했다.

## 장면·reset·물성

부모의 타겟 스폰 원판 반경 0.02 m, 목표 요청 거리 0.15 m와 선반 경계에 따른 거리 단축, 선반 로컬 ±X 각각 ±15° 방향 제외를 유지한다. 부모의 Torch 샘플러 함수를 직접 재사용한다. `reset_all → 타겟·목표 확정 → 장애물 배치 → 초기 관측 저장 → 물성 랜덤화` 순서이며, 이후 CommandManager가 새 타겟 위치와 sweep displacement를 저장한다.

`layout.py`는 checkout의 `src/scene_randomization/generator.py`를 읽기 전용으로 로드한다. 원본의 후보 생성, RED/GRAY/WHITE 판정, 간격·밀도·셀 분포·접근 경로 함수를 사용한다. 고정 타겟·목표를 입력받도록 배치 제어를 구성했다. GRAY 3개(그중 뒤쪽 최소 1개)·WHITE 3개를 생성하며 실패 시 장애물 배치만 재시도한다. 상한 40회 이후에는 `GenerationError`로 실패를 드러내며 명령 변경·제약 완화를 하지 않는다.

원본 좌표는 cm, 현재 선반 좌표는 m다. `(x_cm,y_cm) → (0.20-y_cm/100,x_cm/100)`로 변환하고 선반 pose를 적용한다. 원본 전면 −Y 방향이 실제 로봇 쪽 선반 +X에 대응한다. 원본의 360°·5–20 cm 명령 스케줄 및 넓은 타겟 영역은 적용하지 않는다.

물체 collection index 0은 파란 타겟, index 1–6은 주황 장애물이다. 모두 반지름 0.04 m·높이 0.10 m·밑면 중심 origin·동일한 bottom-heavy 질량 분포와 충돌 설정이다. 환경별 reset 샘플을 한 번 생성하고 질량·관성·마찰을 모든 실린더에 동일하게 적용한다. 질량 중심 0.5475 kg·범위 0.345–0.750 kg 및 기존 선반·Hand 마찰 분포를 유지한다. PhysX의 object-major 순서에 맞춰 부분 reset 행만 갱신한다.

장애물 배치는 별도 지속 NumPy RNG를 사용한다. `reset(seed=...)`를 명시하면 이 RNG도 함께 재초기화한다. 평상시 자동 reset은 RNG 스트림을 이어간다.

## 관측·학습·보상·종료

| 단계 | 차원·동작 |
| --- | --- |
| 기존 `policy` | 57D, 순서·노이즈·실시간 타겟 관측 유지 |
| 새 `obstacles` | 40D, `[HEADER,x,y,z] × 10`, 타겟 제외 |
| 실제 슬롯 | 앞 6칸 HEADER=1, robot-root frame의 초기 밑면 중심 위치(m) |
| 더미 슬롯 | 뒤 4칸 HEADER와 좌표 모두 0 |
| 노이즈 | 실제 슬롯 위치에 reset당 한 번 ±0.01 m, 이후 이동·재관측에도 고정 |
| MLP | 40→32(ReLU)→16, 더미는 인코딩 전 마스킹 |
| 정책·가치망 입력 | 기존 57D + 임베딩 16D = 73D |
| Actor/Critic | 각각 별도 인코더, 같은 정보 사용, PPO와 함께 학습 |
| rollout·export | 원시 57+40=97D 저장/입력. JIT/ONNX는 `[policy57,obstacles40]` 순서 |

PPO 미니배치에서 인코더를 다시 실행하므로 encoder parameter에 gradient가 전달된다. Checkpoint는 인코더와 optimizer를 포함한다. 최종 출력 Action 8D, 본체 MLP 256/128/64 ELU 및 기존 PPO hyperparameter를 유지한다. 단일 물체 checkpoint와 모델 구조가 다르다.

`object_tilt`는 기존의 free angle 5°·fail angle 0.9 rad로 계산한 **물체별 bounded 제곱 비용**을 7개 모두 더하고 기존 weight −2를 적용한다. 단순 각도 합이나 평균으로 변경하지 않는다. 합 비용 범위는 [0,7]이다. `object_drop`는 어떤 물체든 기존 높이 1.04 m 미만 또는 선반 법선 대비 tilt ≥0.9 rad이면 True다.

17D 직접 패드 센서는 기존 방식이며, 손가락 본체 투영 sensor filter에 7개 물체를 포함한다. 촉각에 물체 ID를 추가하지 않는다. 각 부모 body의 contact buffer만 물체 수에 맞춰 확장한다. `pushing_speed`·`push_fast`는 타겟만 검사한다. 필수 Arm/Hand action-rate·joint-velocity 네 항과 −0.03/−0.03/−0.03/−0.01 계수, 물리적 관절 속도 제한 2/2/2/4/4/4 rad/s 및 Hand 1 rad/s를 상속한다.

## 실행과 검증

저장소 루트에서 실행한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-v0 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-v0 --num_envs 1 \
  --checkpoint "<clutter-checkpoint.pt>" --real-time
```

실제 CPU 회귀 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_clutter_reset.py \
  src/inspire_sweep_baseline/tests/test_clutter_layout.py \
  src/inspire_sweep_baseline/tests/test_clutter_models.py \
  src/inspire_sweep_baseline/tests/test_contact_sweep_clutter_mdp.py \
  src/inspire_sweep_baseline/tests/test_contact_sweep.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py \
  src/inspire_sweep_baseline/tests/test_realistic_physics.py \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py \
  src/inspire_sweep_baseline/tests/test_tactile_projection.py \
  src/scene_randomization/test_generator.py
```

결과: **168 passed, 9 subtests passed**, 6.23초. [CPU 출력](../../03_assets/artifacts/contact_sweep_clutter_2026-10-20/cpu.log). Torch ONNX 내부 deprecation warning 1건. 실제 RSL-RL 5.0.1 PPO 업데이트로 Actor/Critic 인코더 gradient·가중치 변경, checkpoint와 optimizer 복원, JIT 및 ONNX ReferenceEvaluator 출력 동등성을 검사했다. 부모 설정 보존·원본 기하 검증·부분 reset·노이즈 범위·초기 관측 고정·전체 물체 tilt/drop·PhysX 인덱싱도 포함한다. 초기 설정 테스트에서 CPU stub에 `to_dict()`가 없던 검사 코드 오류는 stub의 속성 사전 비교로 수정했다. 최종 reset 인자 검증 보완 후 `test_clutter_reset.py`를 재실행해 3개가 다시 통과했다.

원본 독립 검증기로 추가 검사한 seed 20261020의 부모 분포 **10,000개 장면이 모두 통과**했고 타겟·Goal 입력을 정확히 보존했다. 모두 첫 배치 시도에서 성공했다. 생성 시간 2.114초, 평균 0.2114 ms/Scene. 최소 물체 표면 간격 1.60077 cm, 손목 투영 여유 0.30058 cm, 접근 경로–장애물 여유 0.10059 cm다. [원시 배치 검증](../../03_assets/artifacts/contact_sweep_clutter_2026-10-20/layout_benchmark.json).

실제 GPU PPO smoke:

```bash
/home/ssu/miniconda3/bin/conda run --no-capture-output -n jd_isaaclab \
  python src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-v0 --num_envs 8 \
  --max_iterations 1 --run_name smoke_clutter --headless
```

종료 코드 0, seed 42, 8 env ×36 steps=288 transitions, PPO 1 iteration 완료. Run은 `logs/rsl_rl/inspire_contact_sweep_clutter/2026-10-20_13-48-42_smoke_clutter`, checkpoint는 `model_0.pt`다. [stdout 보관본](../../03_assets/artifacts/contact_sweep_clutter_2026-10-20/train_smoke.log). Value loss 126.1448, surrogate loss 0.1055로 유한하며 학습 가능한 두 encoder를 포함한 73D 정책·가치망을 생성했다. 저장된 Actor/Critic tensor는 모두 유한하며 각 state dict에 encoder tensor 4개가 포함됐다.

추가 실제 PhysX lifecycle 검증 명령:

```bash
/home/ssu/miniconda3/bin/conda run --no-capture-output -n jd_isaaclab \
  python -u src/inspire_sweep_baseline/tests/_clutter_lifecycle_probe.py \
  --headless --num_envs 4 --output /tmp/contact_clutter_probe.json
```

Lifecycle 검증은 종료 코드 0으로 통과했다. [원시 JSON](../../03_assets/artifacts/contact_sweep_clutter_2026-10-20/lifecycle.json)과 [stdout](../../03_assets/artifacts/contact_sweep_clutter_2026-10-20/lifecycle.log)을 보관했다.

- 4 env ×7개 물체의 **실제 PhysX** 질량·관성·마찰 동일성과 Arm/Hand 속도 제한을 확인했다.
- policy 57D, obstacles 40D, 실제 6칸·더미 4칸과 초기 노이즈 최대 0.0099345 m를 확인했다.
- 동일 `reset(seed=42)`의 위치·초기 관측 재현, reset 없는 20개 환경 전이 동안 관측 고정, `[1,3]` 부분 reset에서 나머지 물리 상태·물성·관측 보존을 확인했다.
- Command가 초기 타겟+sweep displacement와 일치하고, 장애물 낙하·전도 조작에서 해당 종료와 tilt 합산이 작동했다.
- 12개 부모 촉각 sensor 모두 filter column 7개를 가지며 실제 장애물 접촉으로 palm bit가 활성화됐다. 접촉 열별 누적 수는 `[0,12,0,0,0,0,0]`으로 타겟 접촉 없이 `obstacle_0`만 접촉했다.

이 검사는 명시적으로 상태를 조작한 계약 검사다. 초기 접촉 probe에서는 물체와 부모 body 접촉은 있었지만 접촉점이 palm footprint 밖이라 bit가 켜지지 않았다. probe의 실린더 면 정렬·접촉 위치를 조정한 최종 실행이 통과했으며 환경 런타임이나 센서 판정을 완화하지 않았다. 첫 실패에서는 buffered traceback이 종료 과정에 숨겨져 probe에 traceback flush를 추가했다.

변경 Markdown 7개 수식 검사와 양쪽 저장소 `git diff --check`가 통과했다. 문서 링크 검사 `python 00_guidelines/scripts/check_document_links.py --check-external`는 기존 `logs/TEMP` 3건과 DexTouch PDF 1건의 누락만 보고했다. 신규 문서·artifact 링크 누락은 없다.

## 검증 범위의 한계

장면 기하는 로봇 전체의 IK·접근 경로 충돌을 보장하지 않는다. 이 환경은 사용자 선택대로 기존 로봇 초기 자세를 사용한다. 짧은 PPO smoke는 초기화·물리·학습 연결 검증이며 장기간 학습 안정성, 장애물 회피 성공률, 수천 환경 규모 처리량, 실물 전이는 검증하지 않았다. 현재 타겟 GT 관측이 남으므로 완전한 Blind 정책 성능으로 해석하지 않는다.
