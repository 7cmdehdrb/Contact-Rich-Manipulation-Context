# Finger-v0-Wrench 실행 입력과 Last Action 클리핑

2026-11-11. [현재 환경 계약](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#wrench-실행-입력과-last-action) · [최초 구현·속도 종료 후속](2026-11-11_finger_v0_wrench_osc.md)

## 요청과 참고 구현

사용자가 Wrench 입력 Clip을 참고 예제와 동일하게 적용하고, 손도 URDF 최대 범위로 Clip하며, Last Action에 tanh 대신 Clip된 값을 넣도록 요청했다. 기존 `Inspire-Sweep-Simple-Finger-v0-Wrench`에 직접 적용했다. 부모 Finger-v0 및 다른 환경은 변경하지 않았다.

참고는 `example/contact_rich_manipulation_task_learning/src/contact_manipulation_symmetric/contact_manipulation_symmetric/config/ur5e/ur5e_env_cfg.py`의 `SensorFrameWrenchAction._preprocess_actions`, `mdp/observations.py`의 `wrench_action_limits`/`dynamic_sample`, `mdp/events.py`의 `accepted_actions` 관측 조립이다. 센서 원점 힘·모멘트를 범위 안으로 제한하고, Last Action에는 Scale 이전의 수락된 Raw 입력을 사용한다.

## 변경 전후와 보존 범위

| 항목 | 변경 전 | 변경 후 |
| --- | --- | --- |
| 팔 Raw 입력 | 제한 없음 | ±(20,20,36,8,8,8) |
| 센서 목표 wrench | 명시적 제한 없음 | Fx/Fy±200N, Fz±360N, M각축±8N·m |
| 손 Raw term 이력 | 원본 Raw | URDF 범위로 제한된 Raw |
| 손 실제 목표 | URDF 범위 제한 | 같은 범위 유지 |
| Last Action | tanh(원본 Raw) | Clip 후·Scale 전 Raw12D, tanh 없음 |
| PPO/ActionManager | 원본 샘플 | 유지 |
| action-rate | 원본 Raw 차이, 기존 계수·cap | 유지 |

팔은 기존 `SensorFrameWrenchOSCAction`에서 센서 범위/scale을 캐시하고, native preprocess 전에 out-of-place clamp한다. 이후 native Scale과 기존 센서→COM 모멘트 보정이 적용된다. reference처럼 정책 샘플·ActionManager 이력을 in-place 수정하지 않는다. 실제 관절 토크 포화 및 비유한 effort 방어도 유지한다.

손은 기존 `BoundedFingerJointPositionAction`을 Wrench의 gripper term에만 적용한다. Raw/processed 입력 모두 관절 최소0과 최대값으로 제한하고 기존 mimic mapping을 따른다. 관절 순서와 상한(rad)은 엄지 굽힘0.5864, 검지/중지/약지/소지 각1.4381, 엄지 대립1.1641이다. 활성 패키지의 `HAND_DRIVE_UPPER_LIMITS`와 보관된 원본 `src/trash/inspire_robot/urdf_left_with_force_sensor/urdf/urdf_left_with_force_sensor.urdf`의 해당6개 joint limit을 XML 파싱해 일치함을 확인했다.

새 `SweepSimpleFingerWrenchObservationsCfg`는 Finger 관측을 상속하고 actions term만 `wrench_previous_action`으로 바꾼다. 이 함수는 팔/손 Action term의 수락된 raw_actions를 이어 붙인다. force Scale이나 모멘트 변환이 반영된 processed_actions를 관측하지 않는다. reset에서 term raw history가0이 되므로 Last Action도0이며, 반환 tensor는 이력과 메모리를 공유하지 않는다. 참고의 관측 조립처럼 비유한 관측을 유한값으로 처리한다.

참고 환경의 손 normalized-action 표현은 복사하지 않고 현재 환경의 절대 위치 rad 단위를 유지했다. 또한 요청은 제어 입력과 Last Action 변경이므로 보상 함수·계수는 그대로다. 참고 환경의 action-rate 비용까지 동일하게 바꾼 것은 아니다. 센서/EEF의 물리 프레임·기존 F/T 관측·Gaussian/PPO 초기화·1rad/s 고정 종료·다른 커리큘럼·reset·Scene은 유지한다.

## 최종 대조와 검증

공식 configclass 기반 EnvCfg 전체 비교에서 기존 Wrench 차이에 Last Action callable 변경만 추가했다. 실제 Action Cfg 검사는 gripper class가 bounded로 바뀌고 나머지 설정이 유지됨을 확인한다. 부모 불변성 및 Gym 등록/PPO 구성을 함께 검사했다.

실제 native OSC CPU 경로에서 과대 양/음 입력을 Clip→Scale→모멘트 보정한 결과를 대조하고 원본 샘플 불변성을 확인했다. 큰 위치·힘 값의 float32 모멘트 상쇄 오차 허용은0.3mNm로 명시했다. 손6축 상/하한·mimic 적용 경로·Last Action의 비tanh/비scale·reset 이력0·관측 tensor 비공유를 검증했다. 기존 Wrench 축변환·토크 포화·중력 보상과 다른 Finger/Semi-Prof 회귀도 유지했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_wrench.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_semi_prof.py \
  -q -p no:cacheprovider --tb=short
```

**68 passed in11.34s**. 문서 링크·수식·diff 공백 검사를 수행했다. GPU/PhysX 초기화·실제 학습·checkpoint 재사용은 미검증이다. Last Action 의미가 달라졌으므로 이전 Wrench 정책과 동등한 실행을 보장하지 않는다. 학습 로그와 checkpoint는 수정하지 않았다.
