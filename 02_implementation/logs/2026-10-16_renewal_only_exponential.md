# Renewal 기본 속도 비용 exp 통일 및 중복 클래스 삭제

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [앞선 촉각 v0 통합](2026-10-16_tactile_v0_exponential_cleanup.md)

기준일: 2026-10-16. Workspace 기준 commit은 `38920288f1b5748c046eb4a5965c28a3f851d187`이다. 기존 미커밋 변경을 보존했으며 이번 작업도 미커밋이다.

## 사용자 지정 범위와 코드

사용자는 `OmniRenewalRewardsCfg`의 기본 속도 초과 비용을 exp로 변경하고 파생 환경의 적용을 검토하도록 요청했다. 적용 범위는 **Renewal 계열만**이다. 중복된 `ExponentialSpeedRewardsCfg`는 삭제한다.

[OmniRenewalRewardsCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/sweep_omni_renewal.py)에 두 항을 직접 정의했다.

| 항 | 함수 | 임계값 | weight |
| --- | --- | --- | --- |
| pushing_speed | exponential_pushing_speed_cost | 대상 물체 3D 선속도 0.3m/s | -1.0 |
| arm_speed_excess | exponential_joint_speed_cost | Arm 6개 최대 절대 관절 속도 1.0rad/s | -1.0 |

두 양의 비용은 `expm1(2 * max(x - t, 0)) / 2`이며 기존 RewardManager의 step_dt 곱셈을 유지한다. 임계값 이하에서는 0이고 초과하면 지수적으로 증가한다. 기존 제곱 속도 함수와 네 운동 제곱합 페널티 함수·계수는 보존한다.

`ExponentialSpeedRewardsCfg`를 삭제하고 OSC·일반 Tactile의 불필요한 rewards 재지정을 제거했다. `DexOmniRenewalRewardsCfg`는 `OmniRenewalRewardsCfg`를 직접 상속하고 reaching·goal_distance만 교체한다. 따라서 다음과 같이 적용된다.

| 환경 | rewards 경로 |
| --- | --- |
| Isaac-Inspire-Sweep-Omni-Renewal-v0 | OmniRenewalRewardsCfg 직접 사용 |
| Isaac-Inspire-Dex-Sweep-Omni-Renewal-v0 | DexOmniRenewalRewardsCfg가 기본 rewards 상속 |
| Isaac-Inspire-Tactile-Sweep-Omni-Renewal-v0 | 일반 Renewal 부모에서 상속 |
| Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v0 | Dex Renewal 부모에서 상속 |
| Isaac-Inspire-Sweep-Omni-Renewal-OSC-v0 | 일반 Renewal 부모에서 상속 |

관측·센서·제어·물성·이벤트·종료 및 다른 보상은 변경하지 않았다. 손가락 높이 종료 비활성 설정도 유지한다. Omni v4를 포함한 **Renewal 밖의 환경은 기존 설정**이다. `omni_env_cfg.py`가 HEAD와 동일함을 `git diff --exit-code`로 확인했다. 중복 Tactile v1 두 개는 앞선 요청대로 삭제된 상태를 유지한다.

## 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests
```

최종 결과는 **218 passed**다. 기본 Cfg의 두 함수·임계값·weight를 확인하고 일반 Renewal·Dex·Tactile·Dex Tactile의 최종 term이 기본 Cfg와 같은지 비교했다. OSC 상속·제어 설정 검사도 통과했다. Renewal 설정에 제곱 속도 함수를 다시 연결하는지 AST로 검사한다. Omni v4는 기존 제곱 함수·가중치·수치 검사로 복원 여부를 확인했다.

기존 Renewal/V4 동등성 검사는 현재 차이인 두 exp 비용, 선반 손가락 검사 비활성, 물체 속도 종료 0.8, 목표 마커 및 비활성 None 필드 생략을 명시하여 나머지 설정을 비교하도록 정정했다. 실제 환경의 기존 종료·보상을 바꾸어 검사를 맞추지 않았다.

일반 Renewal의 기본 비용 변경 후 다음 실제 GPU 실행도 완료했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  TERM=xterm PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Sweep-Omni-Renewal-v0 \
  --num_envs 8 --max_iterations 1 \
  --experiment_name renewal_all_exp_smoke --run_name sweep --headless
```

RTX 3090 / Isaac Sim 5.1에서 종료 코드 0으로 PPO 1 iteration을 완료했다. 관측 41D·행동 8D와 저장된 두 exp 함수·임계값·weight를 확인했다. 산출물은 `logs/rsl_rl/renewal_all_exp_smoke/2026-10-16_15-17-40_sweep/`이며 이름은 당시 실행 명령 그대로 보존한다. 이 실행 이후 중복 rewards 클래스 삭제와 파생 참조 정리를 수행하고 최종 CPU 검사를 추가 완료했다. 최종 CPU 출력은 상위 `cpu_tests.log`, 실제 실행 출력은 해당 run의 `run.log`에 저장했다.

변경 문법·diff와 문서 수식·링크도 검사했다. 장시간 학습 수렴과 실물 성능은 미검증이다. 기존 제곱 함수의 보존은 과거 환경의 재현을 위한 것이며 Renewal에서 호출하지 않는다.
