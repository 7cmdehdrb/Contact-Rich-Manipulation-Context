# Renewal 17채널 촉각 환경 추가

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md)

기준일: 2026-10-16. Workspace `main` 기준 commit은 `80a1b96e872ff78afe71a10b5a07a06a10df2190`, 문서 submodule 기준은 `8b25029f37644ed6c287cebba68188ece01ddea5`다. 양쪽 모두 기존 미커밋 변경을 보존했으며 이번 작업도 미커밋 상태다.

## 요청과 구현

사용자는 Sweep Renewal과 Dex Sweep Renewal을 각각 상속하고, 검증 standalone처럼 17개 독립 촉각 입력을 갖는 환경을 요청했다. 힘 기준은 0.01 N 이상이고 출력은 0.0 또는 1.0이다. 센서·관측 이외에는 부모를 유지한다.

| Gym ID | Cfg와 직접 부모 | PPO Cfg |
| --- | --- | --- |
| `Isaac-Inspire-Tactile-Sweep-Omni-Renewal-v0` | `InspireTactileSweepOmniRenewalEnvCfg(InspireSweepOmniRenewalEnvCfg)` | `InspireTactileSweepOmniRenewalPPORunnerCfg` |
| `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v0` | `InspireDexTactileSweepOmniRenewalEnvCfg(InspireDexSweepOmniRenewalEnvCfg)` | `InspireDexTactileSweepOmniRenewalPPORunnerCfg` |

실행 클래스는 양쪽 모두 `InspireSweepEnv(ManagerBasedRLEnv)`다. [새 Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/tactile_omni_renewal_env_cfg.py)는 기존 `TactileSweepSceneCfg`와 `ProjectedTactileContactBits`를 재사용하고 임계값만 0.01 N으로 설정한다. 부모 Renewal·Dex Renewal·OSC Cfg와 기존 Baseline Tactile, 원본 로봇 USD는 수정하지 않았다. 새 Cfg가 각 부모의 최신 보상·종료·물성 적용을 그대로 상속한다. EEF 및 목표 디버그 표시도 부모 설정을 유지한다.

## 센서와 관측 계약

Standalone의 기본 `--pad-layout original`과 같은 원본 패드 17개, 직접 ContactSensor 하나와 부모 링크 ContactSensor 12개를 사용한다. 원본 패드 collider를 유지하고 접촉 view만 구성한다. 별도의 노출 검증 fixture나 무중력·고정 palm-up 자세를 RL로 가져오지 않는다. 기존 제어·관절·자산·질량·관성·충돌·reset·중력은 유지한다.

직접 패드 NetForce의 3D norm과 센서 영역 내 부모 접촉력 벡터합의 3D norm을 각각 임계값과 비교한다. 하나라도 0.01 N 이상이면 1.0, 둘 다 미만이면 0.0이다. 두 경로를 서로 더하지 않고 OR로 결합한다. 부모 접촉의 공간 영역·Z·법선 판정은 기존 검증 판독기와 같다. 직접 경로는 충돌 상대 제한이 없고, 부모 영역 투영 경로는 GPU 호환성 때문에 대상 `mass_cylinder` 접촉만 사용한다. 센서 영역 밖의 부모 접촉을 무조건 감지하는 구현이 아니다.

17개 순서는 palm 1개, thumb 1–4, index·middle·ring·little 각각 1–3이며 PhysX body 순서와 독립적이다. 기존 policy term 순서에서 tactile만 1D → 17D로 바뀐다. Actor/Critic은 같은 `policy` 57D를 받고, Action은 Arm 관절 위치 6D + Hand 2D다. 그 외 관측·노이즈는 부모와 같다. reset 직후 미갱신 환경 행은 0이다. 기존 41D checkpoint는 입력 차원이 다르므로 새 정책을 학습한다.

보상·종료·이벤트와 네 운동 페널티는 각 부모에서 상속한다. PPO는 baseline 설정 그대로이고 기본 실험 폴더만 `inspire_tactile_sweep_omni_renewal`, `inspire_dex_tactile_sweep_omni_renewal`로 분리한다.

## 실제 실행 검증

다음 명령은 workspace 루트에서 실제 실행했다. 로컬 Isaac Lab Python을 사용하고 ROS overlay와 pytest 외부 플러그인을 제외했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests
```

결과는 **205 passed, 2 failed**다. 새 환경 검사 7개는 통과했다. 기존 센서 및 영역 투영 검사도 통과했다. 두 실패는 이번에 수정하지 않은 기존 검사다. `test_renewal_composes_complete_v4_behavior_without_v4_inheritance`는 현재 Renewal의 독립 보상·종료·시각화 설정을 이전 V4와 동일하다고 가정한다. `test_dex_renewal_changes_exactly_the_two_dex_reward_terms`의 마지막 격리 검사는 `arm_speed_excess.weight=-0.03`을 가정하지만 현재 부모 코드는 -0.1이다. 부모를 유지하라는 요청에 따라 실제 보상이나 해당 기존 검사는 변경하지 않았다. 새 검사는 현재 각 부모의 전체 설정과 비교하여 센서·tactile 관측 외 변경이 없는지 확인한다.

새 검사에는 57D 전체 관측 조립, 0.0099/0.01/0.0101 N 경계, PhysX 순서 역전, reset NaN 마스킹, 직접 접촉이 없는 매몰 palm의 부모 영역 투영, 상속 및 설정 인스턴스 격리, 등록·PPO 계약이 포함된다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  TERM=xterm PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Tactile-Sweep-Omni-Renewal-v0 \
  --num_envs 8 --max_iterations 1 \
  --experiment_name tactile_renewal_smoke --run_name sweep --headless

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  TERM=xterm PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v0 \
  --num_envs 8 --max_iterations 1 \
  --experiment_name tactile_renewal_smoke --run_name dex --headless
```

RTX 3090 / Isaac Sim 5.1에서 두 명령 모두 종료 코드 0, PPO 1 iteration 완료다. 각 8개 환경 × 36 policy step을 수집했다. Observation Manager의 policy 57D·tactile 17D, Actor/Critic MLP 입력 57D, Actor 출력 8D를 실제 로그에서 확인했다. Physics dt 0.01s, policy/render dt 0.02s를 유지한다. 첫 무작위 정책의 짧은 종료는 성능 평가로 해석하지 않는다.

산출물은 workspace의 `logs/rsl_rl/tactile_renewal_smoke/2026-10-16_13-49-37_sweep/`와 `2026-10-16_13-50-18_dex/`에 있으며 `params/env.yaml`, `params/agent.yaml`, `model_0.pt`, TensorBoard event를 포함한다. 두 실행의 `run.log`와 상위 `cpu_tests.log`에도 실제 출력을 보존했다. 코드 문법·diff 검사와 변경 문서 수식·링크 검사도 수행했다.

## 실행 안내와 미확인 범위

정식 task별 학습 명령과 기본 로그 위치는 [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)과 [패키지 README](../../../../src/inspire_sweep_baseline/README.md)에 있다. 새 학습 입력 연결까지 검증했으며 장시간 학습 수렴, 2048개 이상 환경의 처리량, RL 장면 전체에 대한 접촉 정확도와 실물 센싱 성능은 검증하지 않았다. 이전 standalone 검증의 99.47%는 원본 배치·0.05 N 시험 결과이며, 이번 0.01 N RL 설정에 대한 측정 정확도로 전용하지 않는다.
