# 촉각 v0 지수 비용 통합 및 중복 v1 삭제

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [직전 부모 적용 정정](2026-10-16_renewal_exponential_parent_scope.md)

기준일: 2026-10-16. Workspace 기준 commit은 `38920288f1b5748c046eb4a5965c28a3f851d187`이며 앞선 미커밋 변경을 보존했다. 이번 변경도 미커밋이다.

## 적용

사용자는 남은 일반 Tactile v0의 제곱 비용도 exp로 변경하고 중복된 두 Tactile v1 환경을 삭제하도록 요청했다.

[촉각 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_renewal_envs.py)의 `InspireTactileSweepOmniRenewalEnvCfg`에 `rewards: ExponentialSpeedRewardsCfg`를 지정했다. Dex 촉각 v0는 이미 Dex 부모에서 같은 설정을 상속한다. 현재 네 환경은 모두 같은 지수 속도 비용을 사용한다.

| Gym ID | exp 비용 적용 경로 |
| --- | --- |
| Isaac-Inspire-Sweep-Omni-Renewal-OSC-v0 | 공통 ExponentialSpeedRewardsCfg 지정 |
| Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0 | Dex rewards가 공통 Cfg 상속 |
| Isaac-Inspire-Tactile-Sweep-Omni-Renewal-v0 | 공통 ExponentialSpeedRewardsCfg 지정 |
| Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v0 | Dex 부모에서 상속 |

물체 속도 임계값 0.3m/s, Arm 6개 관절의 최대 절대 속도 임계값 1.0rad/s를 사용한다. 양의 비용은 `expm1(2 * max(x - t, 0)) / 2`, weight는 두 항 모두 -1.0이며 기존 step_dt 처리를 유지한다. 일반 촉각 v0에서 두 속도 항 외 보상·관측 57D·행동 8D·센서·제어·물성·reset·이벤트·종료는 바꾸지 않았다. 종료는 물체 >0.8m/s, Arm 관절 절대 속도 >5.0rad/s다. 기존 제곱 함수와 일반 Sweep Renewal v0의 제곱 비용은 보존한다.

다음 두 환경의 task 상수·Gym 등록·export, v1 전용 Cfg 파일, 전용 PPO 두 클래스와 v1 전용 검사 파일을 삭제했다.

- Isaac-Inspire-Tactile-Sweep-Omni-Renewal-v1
- Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1

상속·설정 격리 검사는 v0 검사로 옮겼으며, v0 등록이 존재하고 v1 등록이 없는지도 확인한다. 현행 README·활성 환경 표·상속 그림·실행 명령에서 v1을 제거했다. 과거 실행 결과와 개발 로그는 당시 기록으로 보존하고 현재 v0 안내를 연결했다. 삭제된 Cfg에 대한 문서 링크는 역사적 경로 문자열로 변경했다.

## 실제 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  TERM=xterm PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Tactile-Sweep-Omni-Renewal-v0 \
  --num_envs 8 --max_iterations 1 \
  --experiment_name tactile_v0_exp_cleanup_smoke --run_name sweep --headless
```

전체 패키지는 **215 passed, 1 failed**다. 실패는 이전부터 존재한 `test_renewal_composes_complete_v4_behavior_without_v4_inheritance`의 Renewal/V4 완전 동등성 가정이며 이번 변경과 별개다. 새 v0 비용·파생 상속·등록 삭제·설정 격리와 수치 검사는 통과했다.

RTX 3090 / Isaac Sim 5.1에서 변경된 일반 Tactile v0를 8개 환경으로 PPO 1 iteration 실행했고 종료 코드 0으로 완료했다. 관측 57D·행동 8D와 두 exp 함수의 저장 설정을 확인했다. 결과는 `logs/rsl_rl/tactile_v0_exp_cleanup_smoke/2026-10-16_15-12-07_sweep/`에 있으며 `params/env.yaml`, `params/agent.yaml`, `model_0.pt`, TensorBoard event, `run.log`를 포함한다. 상위 폴더에 `cpu_tests.log`를 보존했다.

변경 코드 문법·diff, 변경 Markdown 수식·링크도 검사했다. 장시간 학습 수렴과 대규모 환경 성능은 미검증이다. 촉각 v0 실행 명령은 [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)을 따른다.
