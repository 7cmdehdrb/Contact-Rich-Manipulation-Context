# Contact Sweep v0 독립 기준 환경 구성

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md) · [비교 결과](../../03_assets/artifacts/contact_sweep_2026-10-20/comparison.json)

## 요청과 기준

2026-10-20 사용자 요청: 이전에 구성한 Renewal v3는 보존하고, 복잡한 프로젝트 환경 상속을 끊은 새 Observation·Reward·Termination·Env 등 독립 클래스를 구성해 다음 작업의 기준점으로 삼는다.

Workspace HEAD `2cca359d747edad0782a93119af1992842cb4979`, 문서 submodule HEAD `3773aa5dfe6a1d5f36edd0cdfcbfe7ed0d4b6f10` 위의 작업이다. 앞선 v3 구현과 PPO 진단으로 변경 중인 파일·문서·미추적 자산을 보존했다. 이번 작업은 기존 v3 파일과 그 부모·보상·물성 함수·runner를 수정하지 않고 새 패키지 디렉터리, 등록과 테스트·문서를 추가한다. 커밋·원격 반영은 수행하지 않았다.

## 구성과 독립성

새 task는 **`Isaac-Inspire-Contact-Sweep-v0`**, 실험 폴더는 `logs/rsl_rl/inspire_contact_sweep`다. 코드 위치는 [contact_sweep/](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/contact_sweep_envs.py)다.

| 파일 | 클래스/책임 | 기반 |
| --- | --- | --- |
| `env.py` | `ContactSweepEnv`: 초기 버퍼·센서 freshness·Hand 이력 reset | `ManagerBasedRLEnv` 직접 상속 |
| `env_cfg.py` | `ContactSweepEnvCfg`: Manager 조합·물리·제어 | `ManagerBasedRLEnvCfg` 직접 상속 |
| `scene_cfg.py` | `ContactSweepSceneCfg`: 로봇·물체·선반·촉각 views | `InteractiveSceneCfg` 직접 상속 |
| `observations_cfg.py` | `ContactSweepObservationsCfg`, 내부 `PolicyCfg` | 독립 Cfg, policy는 `ObservationGroupCfg` |
| `actions_cfg.py` | `ContactSweepActionsCfg` | 독립 Cfg |
| `commands_cfg.py` | `ContactSweepCommandsCfg` | 독립 Cfg |
| `events_cfg.py` | `ContactSweepEventsCfg` | 독립 Cfg |
| `rewards_cfg.py` | `ContactSweepRewardsCfg` | 독립 Cfg |
| `terminations_cfg.py` | `ContactSweepTerminationsCfg` | 독립 Cfg |
| `ppo_cfg.py` | `ContactSweepPPORunnerCfg` | `RslRlOnPolicyRunnerCfg` 직접 상속 |
| `common.py` | 기하·질량 상수·Arm 관절 선택 | 공통값 |

새 디렉터리에는 기존 Baseline/Omni/Renewal 환경 Cfg 또는 runtime을 import하는 코드가 없다. 다른 환경의 Cfg를 생성해서 설정을 복사하는 방식도 사용하지 않는다. 기존 자산 모듈, robot factory, source material spawner, MDP 함수·Action/Command term은 조합 가능한 공통 코드로 재사용한다. `DexReachProgress` 등 MDP 계산 자체를 복제하거나 수정한 작업은 아니다. 필수 로컬 `goal_rewards.action_rate_l2`·`joint_vel_l2` 함수와 Arm/Hand 네 계수도 그대로 연결했다.

## 고정한 동작 계약

새 환경은 앞선 [v3 변경](2026-10-20_renewal_v3_reward_mass.md)의 최종 설정을 명시한다.

- Actor/Critic: 동일 policy **57D**. 순서는 Arm 상대 위치 6, 상대 속도 6, 직전 Action 8, 현재 물체 위치 3, 물체 반지름 1, EEF pose 7, 목표 위치 3, 촉각 17, EEF wrench 6이다. 기존 noise와 corruption 설정을 유지한다. 현재 물체 GT를 포함하므로 최종 Blind actor로 해석하지 않는다.
- Action: Arm Joint Position 6D, 초기 관절 위치 +0.5×raw action, Hand openness 2D를 12개 관절로 매핑한다. Arm actuator 속도 제한은 shoulder/elbow 2 rad/s, wrist 4 rad/s다.
- Scene: 같은 로봇 USD·frame·고정 조인트 반력 경로와 17개 패드, 원본 패드+부모 접촉 영역 투영 관측이다. 촉각 임계값은 0.01 N이다.
- Event: 기본 scene reset→목표 물체 스폰→질량/마찰 randomization 순서다. 선반 중앙 반경 2 cm 스폰, 최대 15 cm XY 목표, ±X축 주변 15° 목표 방향 제외 조건을 사용한다. Startup은 원본 재질과 버퍼 준비를 수행한다.
- 질량: 생성 시 0.5475 kg, reset은 기존 bounded Gaussian 샘플×1.5로 0.345–0.750 kg. 마찰 분포·질량에 비례한 관성 갱신을 유지한다.
- Reward: reaching=30, goal_distance=94, Arm/Hand action-rate=−0.03/−0.03, Arm/Hand joint-velocity=−0.03/−0.01, object_tilt=−2, shelf_collision=−0.5, pushing_speed free_speed=0.2/weight=−2/cap=100, arm_speed_excess free_speed=1/weight=−1/cap=100이다. Success/goal_hold 보상은 없다.
- Termination: timeout, object_drop, push_fast(0.8 m/s), shelf_collision(선반 속도 0.1·손목 여유 0.03 m·손가락 검사 없음), hand_velocity라는 기존 이름의 Arm 검사(5 rad/s), shelf_displacement(0.05 m)다. Object outside/success는 활성화하지 않는다.
- 제어: sim dt=0.01 s, decimation=2, 50 Hz 정책, 최대 10초다. PPO는 기존 값과 동일하며 실험 저장 이름을 분리했다.

## 실행·검증

Workspace 루트에서 다음 CPU 검증을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_contact_sweep.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py \
  src/inspire_sweep_baseline/tests/test_realistic_physics.py \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_dex_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py
```

**131 passed in 3.24s**. 새 테스트 5개는 다음을 검증한다.

1. 독립 Manager 설정의 v3 일치, 평가 순서, 질량, frame/sensor 설정, 부모·별도 인스턴스의 상태 분리.
2. 동일 입력·난수에서 57D 관측값과 순서 일치, reset 직후 센서 마스킹.
3. AST를 통한 기존 환경 Cfg import·상속 금지와 새 Gym entry point 연결.
4. Framework를 직접 상속한 PPO와 기존 v3 파라미터 일치.
5. Runtime 부분 reset의 freshness·Hand OPEN 이력과 step의 freshness 전환.

```bash
/home/ssu/miniconda3/bin/conda run --no-capture-output -n jd_isaaclab \
  python src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-v0 --num_envs 8 --max_iterations 1 \
  --run_name smoke_contact_reference --headless
```

GPU 8 env에서 PPO 1 iteration 완료, exit 0. Run은 `logs/rsl_rl/inspire_contact_sweep/2026-10-20_13-19-15_smoke_contact_reference`, checkpoint는 `model_0.pt`, stdout 캡처는 `/tmp/contact_sweep_smoke.log`다. Actor/Critic 입력 57D, Actor 출력 8D, Critic 출력 1D를 확인했다. 기존 선반 mass authoring·frame marker·PhysX 설정 경고가 출력됐으나 실행을 완료했다.

동일한 seed=42·8 env·1 iteration의 기존 v3 run `logs/rsl_rl/inspire_dex_tactile_sweep_omni_renewal_v3/2026-10-20_13-12-56_smoke_v3`와 비교했다.

```bash
/home/ssu/miniconda3/envs/jd_isaaclab/bin/python \
  example/Contact-Rich-Manipulation-Context/03_assets/artifacts/contact_sweep_2026-10-20/compare_runs.py \
  logs/rsl_rl/inspire_dex_tactile_sweep_omni_renewal_v3/2026-10-20_13-12-56_smoke_v3 \
  logs/rsl_rl/inspire_contact_sweep/2026-10-20_13-19-15_smoke_contact_reference
```

[재현 스크립트](../../03_assets/artifacts/contact_sweep_2026-10-20/compare_runs.py)와 [결과 JSON](../../03_assets/artifacts/contact_sweep_2026-10-20/comparison.json)을 저장했다.

- 저장 env.yaml은 log_dir를 제외한 모든 값이 일치했다. Observation 항목 순서와 Reward/Event/Termination 평가 순서도 일치했다.
- Agent YAML은 experiment_name/run_name을 제외하고 일치했다.
- 1 iteration 후 Actor/Critic state_dict의 모든 tensor가 완전히 일치하고 최대 절대 차이는 0이었다. 이번 짧은 smoke 조건의 일치이며 전체 seed·장시간 물리 궤적 일치를 보장하지 않는다.

## 새 기준 task 실행 방법

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-v0 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-v0 --num_envs 1 \
  --checkpoint "<checkpoint.pt>" --real-time
```

2048 env 장시간 학습, 실물 성능, GUI play, 학습된 v3 checkpoint의 재생은 미실행이다. TensorBoard 성공률이나 새로운 학습 성과를 입증한 작업은 아니다. 기존 v3는 기존 task ID로 계속 사용할 수 있다.

문서 검증: 변경 Markdown 6개에 대해 `check_markdown_math.py`를 통과했고, workspace 및 문서 submodule의 `git diff --check`도 통과했다. 문서 submodule에서 `python 00_guidelines/scripts/check_document_links.py --check-external`을 실행했으며 기존 문서의 미보유 TEMP 로그 3경로와 DexTouch PDF 1경로 때문에 오류 4개가 남았다. 새 문서·수정 링크의 오류는 보고되지 않았다.
