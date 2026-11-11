# 중대 이슈 후속: Semi-Prof Wrench 순서 오류와 5% 상한 제거

2026-11-11. **학습 중단 결함 수정·CPU 검증 완료, GPU 장기 실행 미검증.**

[현재 환경 계약](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#semi-prof-v0-접촉-조건부-정밀-이동과-힘-방향) · [이전 Gaussian 전환 사건](2026-11-11_gaussian_action_clipping_incident.md)

## 증상과 확인된 원인

사용자가 Gaussian 전환 후 Semi-Prof 런타임에서 다음 traceback을 제공했다.

```text
RewardManager.compute
  WrenchMagnitudeChangePenalty.__call__
    WrenchRatePenalty._reward_budget
RuntimeError: WrenchRatePenalty must follow every positive reward term
```

이는 이전 PPO의 비유한 gradient 오류와 별개의 환경 보상 구성 결함이다. `force_direction`은 양의 가중치0.33으로 Semi-Prof 하위 Cfg에 추가됐다. Isaac Lab configclass의 인스턴스 필드 순서에서 새 필드는 부모의 `wrench_change` 뒤에 위치했고, RewardManager는 이 순서로 실행했다.

기존 Wrench 페널티는 현재 에피소드에서 얻은 양의 보상 합계의5%를 누적 비용 상한으로 사용했다. 따라서 같은 step의 모든 양의 보상이 먼저 `_episode_sums`에 반영되어야 했으나, 양의 방향 보상이 뒤에 있었다.

기본 커리큘럼에서 Wrench 가중치는0–1000 iteration 동안0이다. RewardManager는 가중치0 항목을 호출하지 않으므로 초기에는 순서 검사가 실행되지 않는다.250 iteration 간격 보간에 따라 기본 일정의1250 iteration에서 −0.00375로 처음 활성화된다. 사용자 실행의 실제 iteration/override는 제공되지 않았으므로 그 실행이1250이었다고 단정하지 않는다.

## 사용자 후속 지시와 최종 변경

최초 대응으로 방향 보상을 Wrench 앞에 옮겨 오류 재현 회귀를 통과시켰으나, 사용자가 **5%는 강제 규약이 아니므로 상한 자체를 삭제**하도록 지시했다. 최종 구현은 순서 이동을 폐기하고 Semi-Prof의 양의 보상 연동 상한을 제거한다.

| 항목 | 수정 전 | 최종 수정 후 |
| --- | --- | --- |
| Wrench 비용 | 물리 변화 비용을 양의 누적 보상의5%로 추가 제한 | 물리 변화 비용에 기존 가중치·dt 적용 |
| 양의 보상이0인 경우 | 예산0이라 비용0 | 유효한 Wrench 변화가 있으면 비용 발생 |
| 보상 순서 | 모든 양의 보상이 Wrench보다 앞이어야 함 | 양의 보상 조회·순서 검사 자체를 실행하지 않음 |
| Wrench 가중치·커리큘럼 | 기존 일정 | 그대로 유지 |
| 방향 보상 | 고정 가중치0.33 | 그대로 유지. 약10% 수준은 가중치 선정 근거이며 비율 강제가 아님 |
| 정책·관측·액션 | Gaussian + 실행 Clip | 그대로 유지 |

`SweepSimpleSemiProfRewardsCfg.__post_init__`에서 부모 초기화를 보존하고 `wrench_change.params['max_positive_fraction']=None`으로 지정한다. 공유 `WrenchMagnitudeChangePenalty`는 이 값이None이면 `_reward_budget`를 호출하지 않고 변화량 비용을 반환한다. 부모 Finger-v1/v2 및 과거 환경의 기존 계약은 기본값0.05로 보존했다. 이번 적용 범위는 오류가 보고된 Semi-Prof다.

Wrench 변화량 함수 자체의0–1 포화, free threshold·saturation ratio·sharpness, 유효 센서 이력과 reset 처리는 유지한다. 이는 양의 보상에 대한 비율 제한과 별개다. 검사만 제거하고 불완전한 양의 보상 합계를 사용하는 방식은 적용하지 않았다.

## 재현·회귀 검증과 누락 인정

실제 Semi-Prof 보상 Cfg, 실제 커리큘럼 함수, 실제 Wrench 클래스와 체크인된 `RewardManager.compute`를 CPU에서 실행했다. 다른 물리 보상과 센서 입력만 대역으로 공급했다.

- 최초 수정 전: 사용자와 같은 파일·함수·RuntimeError로 재현.
- 5% 제거 전 새 회귀: 양의 보상 유무2조건 모두 실패하여 강제 예산이 남아 있음을 확인.
- 최종 수정 후: iteration0·1000·1250·3000·6000에서 실행 정상. 양의 보상0과 방향 보상만 있는 경우 모두 Wrench 비용 발생, 기존5%를 초과해도 비용이 잘리지 않음, 양의 보상 이름/예산 캐시를 조회하지 않음을 확인.
- 부모 설정 불변, 기존 환경의5% cap·순서 검사 회귀 통과. 공유 함수의None 옵션 외 기존 동작 보존.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple_semi_prof.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_clutter_v2_rewards.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_safety_rewards.py \
  src/inspire_sweep_baseline/tests/test_revision_v1.py \
  -q -p no:cacheprovider --tb=short
```

결과: **92 passed in 10.04s**.

이전 테스트는 보상별 수식과 초기 구성을 검사했으나, 실제 RewardManager 순서 및 Wrench 가중치가0에서 음수로 바뀌는 구간을 함께 검사하지 못했다. 이전 CPU 통과가 이 경로의 정상 동작을 보장하지 않았으며, 이번 활성화 구간 회귀로 누락을 보완했다.

## 영향과 미검증 범위

상한 제거로 양의 보상을 적게 얻는 에피소드에서도 Wrench 페널티가 적용된다. 실제 보상 비중·학습 결과는 달라질 수 있지만 이것이 사용자 지시의 의도다. 임의로 가중치를 재조정하지 않았다.

등록·상속·Scene·관측/행동 차원·OSC·reset·종료·다른 보상·커리큘럼·Gaussian 정책은 보존했다. 새 Gaussian checkpoint의 정책 구조는 바뀌지 않으며, 구 tanh checkpoint 직접 로딩 거부 규칙은 유지한다. GPU 물리 rollout·원격 학습 재실행은 수행하지 않았다. 학습 로그와 사용자 변경을 보존했다.
