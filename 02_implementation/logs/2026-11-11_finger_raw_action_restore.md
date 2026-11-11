# Finger 계열 Raw Action·Last Action tanh·속도 비용 복원

**후속 결정으로 대체됨:** 사용자가 기존 ID로 play할 수 있도록 원환경 직접 변경을 롤백하고 아래 실험을 별도 Raw ID로 분리했다. 현재 계약은 [환경 분리 기록](2026-11-11_finger_raw_environment_split.md)을 따른다. 이 문서는 분리 전 작업 이력이다.

2026-11-11 사용자 후속 지시. [현재 환경 계약](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#finger-v1v2-출력-범위와-정밀-이동후퇴) · [직전 Gaussian 전환](2026-11-11_gaussian_action_clipping_incident.md) · [Semi-Prof 5% 상한 제거](2026-11-11_semi_prof_reward_order_incident.md)

## 범위와 의도

사용자가 새 환경의 Joint Velocity 비용을0.06에서0.03으로 복구하고 Action Clip을 삭제하며 Last Action에 하이퍼볼릭 탄젠트를 적용하는 구조로 돌아가도록 지시했다. 터미네이션은 유지한다.

직접 적용 대상은 `Inspire-Sweep-Simple-Finger-v1`, 그 하위 `Inspire-Sweep-Simple-Finger-v2`, `Inspire-Sweep-Simple-Semi-Prof-v0`다. Finger-v0 및 다른 환경의 동작은 보존한다. 새 task나 버전을 만들지 않았다.

## 최종 변경

| 항목 | 변경 전 | 변경 후 |
| --- | --- | --- |
| 팔 Joint Velocity 비용 | −0.06 | −0.03; 함수·cap100 유지 |
| 환경 진입 Action | 축별 Clip 후 ActionManager에 전달 | 원본 Raw Action을 그대로 전달 |
| Arm Action term | BoundedFingerOSCAction | Finger-v0의 WrenchRefactorOSCAction |
| Hand Action term | BoundedFingerJointPositionAction | Finger-v0의 FingerJointPositionAction |
| Last Action | Clip 후 Raw Action | 원본 Raw Action에 tanh;12D |
| Action 변화량 비용 | Clip된 명령 차이 | 현재/직전 Raw Action 차이; Arm/Hand 각 weight−0.03·cap100 유지 |
| PPO 저장·확률 계산 | 일반 Gaussian Raw Action | 그대로 유지; tanh/atanh 정책 변환 복원 아님 |
| 액션 진단 | Clip 비율·평균·std | 무의미해진 Clip 비율 제거, 평균·std 유지 |

새 Raw Action Clip을 위한 runtime 전처리, OSC 전용 파일, Hand raw Clip subclass, observation Clip helper와 공통 Clip helper를 제거했다. 역할별 Cfg와 runtime 클래스 이름·상속은 유지하고 부모 구성을 그대로 사용한다. Last Action은 기존 `previous_action_command`를 상속한다.

복원 기준은 Finger-v0의 제어 경로다. **기존 손 관절 목표의 URDF 한계 처리와 mimic 매핑, OSC 토크 한계는 유지**한다. 따라서 손의 Raw Action 이력은 제한하지 않지만 최종 물리 관절 목표는 기존 한계를 따른다. 손 drive6축·정렬·rad 단위와 OSC Scale0.03/0.15는 그대로다. 일반 RSL-RL wrapper의 기본 `clip_actions=None`도 확인했다.

일반 Gaussian의 축별 초기 평균·std, log-std 학습, 구 tanh policy checkpoint 거부 및 NumericalPPO 수치 검사는 유지한다. 손 초기 분포 변경이나 관측 통계 정규화는 추가하지 않는다. Semi-Prof의 Wrench5% 상한 제거도 유지한다.

## 유지한 터미네이션과 환경 계약

팔 관절 속도 종료는 초기2rad/s,2000 iteration부터 감소 일정 시작,2250부터250 iteration마다1/12rad/s씩 감소하여5000에서1rad/s다. 보상 비용을−0.03으로 바꿔도 이 일정은 그대로다. 손 속도 비용−0.01도 유지한다.

각 환경의 Goal Distance·Reach·접촉·방향·성공·후퇴 게이트,10초 timeout·기타 종료, reset·Fast 배치·물리 자산·센서·관측 차원66+64·액션12D는 보존했다. 등록 ID·로그 실험명도 유지한다.

직전 Gaussian 모델과 파라미터 구조는 같지만, 제어·Last Action·Action 비용의 의미는 달라졌다. 따라서 직전 run에서 재개하는 것은 과업 계약이 바뀐 이어 학습이며 동일 조건 재현으로 간주하지 않는다. 구 tanh 정책의 직접 로딩 거부는 그대로다. 외부 export 소비자는 Raw Action 출력과 부모 제어 변환, 다음 관측의 tanh Last Action 계약을 따라야 한다.

## 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_semi_prof.py \
  src/inspire_sweep_baseline/tests/test_bounded_ppo_failure.py \
  src/inspire_sweep_baseline/tests/test_numerical_ppo.py \
  -q -p no:cacheprovider --tb=short
```

**79 passed in 10.65s**. 이후 설정 대조 assertion을 강화하여 부모와 Last Action 함수 동일·속도 비용−0.03을 명시적으로 확인했고 해당 검사1개도 통과했다.

- 원래 범위보다 큰 Raw Action이 runtime에서 잘리지 않고 부모로 전달됨, Last Action은 원본의 tanh와 일치함을 검사했다.
- 실제 Gaussian PPO 저장 액션/log probability를 보존하고, 큰±100 평균의 원본 액션으로 두 rollout·두 PPO 업데이트를 실행했다. 실제 observation/action-rate 함수와 runtime 상속을 사용하되 physics와 관측 결합은 CPU 대역이다. tanh 관측의 유한 범위, Raw Action 차이에 대한 비용과 기존cap100, 손실 유한성을 확인했다.
- 실제 parent Hand term의 raw 이력 보존과 최종 URDF 목표 제한을 확인했다.
- Finger-v1/v2의 기존 속도 종료 일정 경계값, Semi-Prof 상속·Wrench 상한 제거, 그 외 보상 회귀를 포함했다.
- 과거 tanh/atanh 정책의 오류 재현9조건은 일반 Gaussian에서 계속 통과한다. 정책에 tanh를 다시 도입하지 않았다.

GPU/PhysX 실제 제어·장기 학습·속도/정확도 개선은 미검증이다. 학습 로그는 건드리지 않았다. 이번 요청 전 작업트리에 있던 Semi-Prof Wrench 상한 제거 변경을 보존했다. 최신 계약은 이 기록과 현재 환경 문서이며, 이전 중대 이슈 기록의 Clip 계약은 변경 이력으로 남긴다.
