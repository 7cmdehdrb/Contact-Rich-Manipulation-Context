# Dex Tactile Renewal OSC v2: 명령 상한과 실제 관절 속도

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [사용자 결정](../../01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md)

기준일: 2026-10-18. Workspace `main`, 기준 commit `8b6551b9654a4c7fa11c47f85d0ef8744b659826`, 문서 저장소 기준 commit `51433d8897fa7081eed532117ec66624641ba29e`. 작업 시작 시 상위 저장소에 문서 submodule 참조 차이만 있었고 문서 내부 작업트리는 깨끗했다. 해당 참조 차이를 보존했다. 이번 작업에서 commit·push는 수행하지 않았다.

## 사용자 요청과 구현

직전 구현한 Dex Tactile v2를 상속하고 Arm 제어만 OSC로 교체한다. 기본 구현은 `omni_renewal_osc_env_cfg.py`를 참조하며 stiffness 200→100, 작은 Cartesian 명령 상한을 적용한다. 1.5 rad/s는 사용자가 제시한 대략적인 움직임 수준이며 엄밀한 관절 속도 보장을 요구한 것은 아니다. 이번 요청은 OSC에 대한 action 제한을 명시적으로 허용한다.

- Task: `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2`.
- Runtime: 공통 `InspireSweepEnv`.
- Cfg: `InspireDexTactileSweepOmniRenewalV2OSCEnvCfg(InspireDexTactileSweepOmniRenewalV2EnvCfg)`.
- PPO: `InspireDexTactileSweepOmniRenewalV2OSCPPORunnerCfg`가 v2 runner를 상속하고 experiment 이름만 `inspire_dex_tactile_sweep_omni_renewal_v2_osc`로 바꾼다.
- 코드: [OSC Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/dex_tactile_omni_renewal_v2_osc_env_cfg.py), [제한 action](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/osc_actions.py).

부모의 57D Actor/Critic 관측(현재 물체 GT 포함), 8D 행동 크기·Hand 동작, 촉각 17개·0.01 N 및 F/T, 물성·스폰·전방향 목표·reset, v2 보상 12항(+100 성공·증가하는 체류 보상 포함)·종료 7항을 유지한다. 네 필수 raw Action·실제 관절 속도 제곱합 비용과 계수도 그대로다. Arm 행동 6D의 의미만 Joint Position offset에서 Cartesian 상대 pose로 바뀐다. 기존 `hand_velocity`의 Arm 종료 기준 5.0 rad/s도 유지한다.

OSC는 기존 EEF의 `axia80_link`와 동일한 body-local pose offset, robot root 좌표계의 `pose_rel`, fixed impedance, `motion_stiffness_task=100.0`, damping ratio 1.0, inertial dynamics decoupling 및 gravity compensation을 사용한다. 기존 OSC처럼 Arm implicit PD stiffness/damping만 0으로 바꾸며 effort·velocity limit은 유지한다. 정책 주기 0.02초·물리 주기 0.01초는 바꾸지 않는다.

## 명령 제한 방식과 추정

upstream `OperationalSpaceControllerAction`의 `_preprocess_actions`는 pose에 scale을 곱하지만 `ActionTermCfg.clip`은 적용하지 않는다. 따라서 `position_scale`만 낮추거나 `clip` 필드만 지정하는 것으로 실제 명령 상한을 보장하지 않는다. 로컬 subclass는 upstream 전처리 뒤, `set_command` 이전에 translation·rotation-vector의 norm을 각각 제한한다.

| 항목 | 최종값 |
| --- | --- |
| 위치 scale | 0.005 m/raw action |
| 회전 scale | 0.025 rad/raw action |
| 이동 증분 norm 상한 | 0.005 m = 5 mm |
| 회전 증분 norm 상한 | 0.025 rad ≈1.43° |

상한 이하에서는 선형 scale을 유지하고 초과하면 벡터 방향을 유지해 축소한다. XYZ 각 축에 상한을 적용하는 방식이 아니므로 대각선 명령의 norm도 상한을 넘지 않는다(부동소수점 반올림 수준 제외). Hand 입력과 raw policy action·이전 action 관측·raw action-rate 보상 입력은 그대로 둔다. 현재 EEF를 기준으로 매 정책 스텝 새 목표를 만들므로 누적 도달 범위는 제한하지 않는다. 물리적인 관절 속도 hard limit은 아니다.

관성 decoupling OSC의 motion gain 100과 damping ratio 1에서는 damping gain이 20이다. 작은 상대 pose delta에 대해 준정적 Cartesian 속도를 대략 `(100/20) × delta`로 보면 최종 상한은 이동 0.025 m/s·회전 0.125 rad/s 수준이다. 이는 hold 중인 목표의 연속 동역학과 정책 재명령을 단순화한 추정이다. reset 자세의 실제 EEF Jacobian pseudo-inverse로 64개 포화 방향을 변환한 최대 절대 관절 속도 추정값은 약 0.303 rad/s였다. 특이점·접촉·과도응답을 보장하는 계산은 아니다. 실제 초기 응답 측정과 함께 보수적으로 선정했다.

## GPU 속도 대조 실험

[측정 스크립트](../../../../src/inspire_sweep_baseline/tests/_osc_command_probe.py)는 실제 환경을 생성하고 reset 직후부터 100 정책 스텝(2초)을 실행한다. seed 42·64개 환경, Hand는 열린 명령 1.0이다. `zero`는 Arm 0, `corners`는 6D 부호 조합 64개에 raw 크기 10을 곱하여 양쪽 상한을 포화, `random`은 매 스텝 표준정규 raw 명령이다.

기존 failure/auto-reset을 유지하면서 physics substep의 action 적용 직전과 종료 계산 직전의 최대 절대 Arm 관절 속도를 기록한다. 종료 후 reset된 0 속도만 읽고 정상이라고 해석하지 않는다. 종료 횟수는 여러 episode에 걸친 값이며 성공률이 아니다. 동역학·물성·threshold는 측정을 위해 수정하지 않는다.

실제 실행 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_osc_command_probe.py \
  --headless --num_envs 64 --steps 100 \
  > /tmp/dex_tactile_v2_osc_probe.log 2>&1
```

처음 10 mm/0.05 rad 상한에서는 첫 5스텝(0.1초)의 최대 Arm 속도가 포화 명령 1.784 rad/s·무작위 명령 1.383 rad/s여서 절반으로 낮췄다. 이 첫 결과는 `/tmp/dex_tactile_v2_osc_probe_initial_limits.log`에 남겼다. 최종 5 mm/0.025 rad에서 위 명령을 다시 실행한 결과는 다음과 같다.

| 입력 | 초기 0.1초 최대속도 | 2초 전체 최대속도 | 처음 5 rad/s 초과 control step | Arm 과속 종료 횟수 |
| --- | --- | --- | --- | --- |
| zero | 0.00295 rad/s | 5.303 rad/s | 38 (0.76초) | 128 |
| corners | 0.891 rad/s | 6.076 rad/s | 15 (0.30초) | 280 |
| random | 0.691 rad/s | 6.280 rad/s | 16 (0.32초) | 260 |

최종 processed norm은 translation 약 0.005 m·rotation 약 0.025 rad로 확인됐다. 두 양의 보상·종료·센서 등은 상속했다. 초기 명령 응답을 낮춘 것은 확인했으나 **액션 크기 제한만으로 과속 종료나 정책 학습 실패가 해결됐다고 주장할 수 없다. 0 명령에서도 이후 불안정성이 재현됐다.** 원인은 이 실험에서 확정하지 않았다. 사용자 지정 범위를 넘어 frame 변환·controller 동역학·물리·termination을 추가로 바꾸지는 않았다.

처음 GPU 실행에서는 Action 클래스가 package `actions`에서 export되지 않아 ImportError가 났다. `task_space_actions`에서 구현 클래스를 import하도록 수정한 후 재실행했다. 최종 stdout에는 3개 `OSC_PROBE` 결과가 있고 traceback이 없다. `/tmp` 출력은 영구 추적 자산이 아니므로 위 수치를 본문에 함께 보존한다.

## CPU 및 PPO 실행 검증

관련 CPU 검사:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_bounded_osc.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py
```

초기 제한 구현에서 **17 passed in 3.21s**. 실제 upstream `process_actions`·`_preprocess_actions`와 로컬 subclass를 실행해 scale 이후 controller에 전달되는 상한, 대각선 방향 보존, 작은 명령 선형성·0 명령·이전 target 잔류 없음, raw/input 보존, 잘못된 상한 거부를 검사했다. 실제 configclass로 v2와 diff를 비교해 Arm action·Arm PD 이외의 설정이 같고 부모를 오염시키지 않음을 확인했다. GPU 환경 구성은 별도 실제 실행으로 검증했다.

최종 상한으로 전체 회귀 검사:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider
```

**315 passed, 17 subtests passed in 16.16s**.

최종 환경의 PPO 경로도 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-OSC-v2 \
  --num_envs 8 --max_iterations 1 --headless \
  --experiment_name inspire_dex_tactile_sweep_omni_renewal_v2_osc_smoke \
  --run_name validation > /tmp/dex_tactile_v2_osc_train_smoke.log 2>&1
```

8개 환경·1 iteration·288 transitions와 `model_0.pt` 저장을 완료했다. run 폴더는 `logs/rsl_rl/inspire_dex_tactile_sweep_omni_renewal_v2_osc_smoke/2026-10-18_20-14-08_validation/`다. 평균 episode 길이는 14.31스텝, `Episode_Termination/hand_velocity`는 0.6354였으므로 이 smoke도 유효 정책의 학습 성공을 입증하지 않는다. 성공/유지 보상은 0이었다. 기존 PointInstancer 시각화 경고는 남아 있다.

일반 실행은 [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)를 따른다. 장시간 학습, 유효 정책·성공률·정착/오버슈트 개선, 모든 자세에서의 관절 속도 상한 및 실물 동작은 미검증이다. 특히 0 명령 과속의 원인 분리가 후속 확인 항목이다.

## 문서 검사

문서 저장소 루트에서 변경 Markdown 7개만 검사했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py 01_plan/00_HANDOFF_BRIEF.md 01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md 01_plan/04_NEXT_ACTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-18_dex_tactile_renewal_v2_osc.md ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external 01_plan/00_HANDOFF_BRIEF.md 01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md 01_plan/04_NEXT_ACTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-18_dex_tactile_renewal_v2_osc.md ../../src/inspire_sweep_baseline/README.md
git diff --check
```

수식 검사 7개 통과, 내부 링크 172개·workspace 링크 43개에서 오류 0건. Workspace의 `git diff --check`도 통과했다. GPU PPO run의 `params/env.yaml`에서 local bounded action class·stiffness 100·scale 및 두 norm 상한을 확인했다.
