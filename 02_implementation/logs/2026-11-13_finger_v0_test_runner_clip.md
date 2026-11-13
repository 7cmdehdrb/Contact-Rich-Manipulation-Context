# Finger-v0-Test Runner Clip와 Last Action 변경

2026-11-13. 기존 `Inspire-Sweep-Simple-Finger-v0-Test`를 직접 수정했다. [진단 기록](2026-11-13_wr4_numerical_diagnosis.md)에서 확인한 raw 액션 변화 비용 폭증을 막기 위해, 사용자는 Runner의 공통 Action Clip과 Clip 후 Last Action을 요청했다. tanh·별도 액션 비용 상한은 명시적으로 제외했다. Wrench는 보류 대상으로 유지했다.

## 요청 해석과 최종 설정

앞선 논의의 “병진/회전 중 큰 값에 맞춘 공통 clip”을 적용하여 **12축 모두 `clip_actions=π/2`**로 설정했다. 구현 필드명은 `action_clips`가 아니라 `clip_actions`다. 제어기 scale과 물리 관절 한계는 변경하지 않았다.

| 항목 | 변경 전 Test | 변경 후 Test |
| --- | --- | --- |
| Runner `clip_actions` | None | 1.5707963267948966 |
| Clip 위치 | 공통 정책 액션 Clip 없음 | `RslRlVecEnvWrapper.step`, 환경/ActionManager 진입 전 |
| Last Action | manager action에 tanh | manager action 그대로 반환 |
| 정책/rollout 저장값 | 일반 Gaussian 원본 샘플·log-prob | 동일, Clip 전 샘플 보존 |
| action-rate 입력 | 무제한 manager current/previous | wrapper에서 Clip된 manager current/previous |
| action-rate 함수/weight | 팔6·손6 각각 제곱합, −0.03 | 동일 |
| action-rate cap | 없음 | 없음 |
| 팔 scale | 병진0.03, 회전0.15 | 동일 |
| 손 목표 | 기존 URDF 범위·mimic mapping | 동일 |

Test는 기존에도 v1의 `clip_raw_actions` runtime 분기나 `BoundedFingerOSCAction`을 사용하지 않았다. 따라서 다른 환경의 클립 코드를 삭제하지 않고, Test의 Runner 설정에만 제한을 추가했다. `FingerJointPositionAction`의 기존 URDF 목표 제한과 최종 effort 방어는 물리 제어 계약으로 보존했다.

## 실행 순서와 실제 범위

```text
actor Gaussian sample (PPO 저장 원본)
  → RslRlVecEnvWrapper: clamp(-π/2, +π/2)
  → ActionManager: previous/current 저장
  → 팔 OSC scale / 손 URDF 목표 처리
  → action-rate: manager current/previous 제곱 차이
  → Last Action: manager action 그대로
```

| 채널 | manager/Last Action 범위 | 처리 후 명령 |
| --- | --- | --- |
| 병진3축 | 각각±π/2 | 각각±0.0471239m, 약4.71cm |
| 회전3축 | 각각±π/2 | 각각 Euler±0.235619rad, 13.5°; 이후 기존 quaternion/axis-angle 변환 |
| 손6축 | 각각±π/2 | 엄지 굽힘0~0.5864, 검지/중지/약지/소지0~1.4381, 대립0~1.1641rad |

손의 Last Action은 wrapper가 수락한 raw 명령이며 최종 관절 목표가 아니다. 예를 들어 raw−100은 manager/Last Action에서−π/2이고 손 목표는0이다. 이 차이는 사용자 요청대로 Last Action을 별도 가공하지 않은 결과다. 별도 액션 재정규화·축별 재매핑은 추가하지 않았다.

각6축의 action-rate 제곱합은 수학적으로 최대6π²≈59.2176이며, weight−0.03과 dt0.02 적용 시 비용 크기는최대0.0355306이다. 팔·손 합계 최대0.0710612. 함수 안에 최대값을 구현한 것이 아니라 입력 범위에서 도출되는 값이다. 학습된 raw Gaussian 평균/표준편차·엔트로피 및 기존 수치 guard는 그대로다. 이 변경이 그 분포의 장기 확대까지 해결했다고 주장하지 않는다.

## 구현과 전체 대조

기준 HEAD는 `1ab6e579cf1c4f4152954b1c6fb0120a99729eb5`. 시작 시 문서 submodule의 기존 README 수정, `2026-11-11_finger_final_review.md`, 앞선 wr4 진단 기록과 사용자 zip 두 개는 별도 변경 대상에서 제외했다.

활성 패키지의 기존 역할별 파일만 변경했다.

- `agent/sweep_simple_ppo_cfg.py`: Test Runner에만 `clip_actions` 추가.
- `mdp/observation_functions/sweep_simple.py`: manager action을 그대로 반환하는 `raw_previous_action` 추가.
- `mdp/observations/sweep_simple.py`: Test 관측 설정을 부모에서 직접 상속, actions term만 교체.
- `envs/sweep_simple_envs.py`: 기존 Test에 해당 관측 설정 연결.
- `tests/test_sweep_simple_finger.py`: 전체 설정 비교 갱신, 실제 upstream wrapper/manager/OSC 전처리와 보상/관측 연결 검사 추가.

전체 config 대조에서 부모 Finger-v0와 Test의 차이는 기존 팔 속도 종료1rad/s·해당 커리큘럼 제거에 Last Action callable 변경만 추가됨을 확인했다. Runner 차이는 기존 실험명 외 `clip_actions`만 추가됐다. 부모의 기존·새 인스턴스가 영향을 받지 않음을 검사했다. 테스트용 action leaf double의 한계는 실제 GPU 학습에서 저장된 Action class와 scale로 추가 대조했다.

등록 ID/runtime, Scene/자산/물성, Command/Event/reset, 관측66+64D와 term 순서, 나머지 관측·노이즈, 보상 이름·함수·계수·일정, 종료·커리큘럼, actor/critic 구조와 Gaussian 초기 std/entropy/LR/gamma/lam/rollout 설정은 보존했다. Finger-v0/v1/v2·Raw·Semi-Prof·Wrench 구성은 변경하지 않았다. `train.py`와 `play.py`는 기존 wrapper 연결을 그대로 사용한다.

## CPU 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_wrench.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_semi_prof.py \
  -q -p no:cacheprovider --tb=short
```

**66 passed in10.71s**. 첫 실행에서는 configclass의 callable 직렬화 문자열과 함수 객체를 비교하는 테스트 기대값 오류로1개 실패했다. 실제 callable identity를 별도로 확인하고 직렬화 기대값을 수정한 뒤 전체 명령을 다시 실행했다.

새 경로 검사는 실제 Isaac Lab `RslRlVecEnvWrapper.step`, `ActionManager.process_action`, `OperationalSpaceControllerAction._preprocess_actions` 메서드를 실행한다. PhysX I/O는 double이다. ±9045 수준의 입력·경계값·범위 안 입력으로 다음을 확인했다.

- 원본 샘플은 변경되지 않고 manager/Last Action은±π/2로 제한된다.
- Last Action에 tanh가 없으며 관측 함수 자체는 임의로 clamp하지 않는다.
- current/previous 모두 Clip 후 값이고 action-rate는 그 차이 제곱합을 사용한다.
- Clip 이후에 OSC scale이 적용된다.
- 기존 cap 없는 비용 함수 검사도 유지하여 직접 큰 입력을 주면400을 반환함을 확인했다.

## GPU 실제 학습 smoke

RTX3090, Isaac Sim5.1, seed42. 사용자 GPU 테스트 허용 범위에서 sandbox 밖으로 실행했다. 원본 `logs/rsl_rl` 대신 절대 experiment 경로를 지정했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Simple-Finger-v0-Test \
  --num_envs 64 --headless --max_iterations 2 --seed 42 \
  --experiment_name /home/min/7cmdehdrb/grad/outputs/finger_v0_test_runner_clip/training \
  --run_name smoke
```

**64환경·36step/env·PPO2 iterations 정상 완료, process exit0**. [stdout](../../../../outputs/finger_v0_test_runner_clip/train_stdout.log), [run](../../../../outputs/finger_v0_test_runner_clip/training/2026-11-13_15-44-19_smoke)에 보존했다.

- 실제 `params/agent.yaml`의 `clip_actions=1.5707963267948966` 확인.
- 실제 `params/env.yaml`의 `raw_previous_action`, 기존 `WrenchRefactorOSCAction`/`FingerJointPositionAction`, position0.03/orientation0.15 확인. Test에 `clip_raw_actions` 설정 없음.
- `model_0.pt`와 `model_1.pt` 각각100개 tensor가 모두 유한함을 확인.
- Actor와 Critic의 obstacle encoder weight가 두 checkpoint 사이에 실제 갱신됨을 확인.
- 초기 정책은 팔 속도 실패 종료가 높았으며 짧은 학습 성공을 정책 성능 개선의 증거로 해석하지 않는다.

## 문서와 미검증 범위

현재 인계·활성 환경 안내·Simple 환경 설명·로그 색인에 최신 Test 계약을 반영했다. 기존 진단과 사용자 문서 변경은 보존했다. 변경5개 Markdown 수식 검사, 해당 문서의 외부 경로 포함 링크 검사, 전체580개 Markdown 링크 검사, workspace와 문서 저장소 `git diff --check`를 모두 통과했다. 별도 렌더링은 미검증이다.

장기 학습 안정성, 기존8043회차 실패 상태의 변경된 물리 trajectory 재현, 기존 checkpoint resume/play 성능, export 정책 단독 실행은 미검증이다. export 정책이나 wrapper 없는 직접 환경 호출은 Runner clip을 자동 적용하지 않으므로 동일한 소비자 경계 처리가 필요하다. 기존 checkpoint와 입출력 차원은 같지만 Last Action 표현·실행 범위의 의미가 달라 동작 동일성을 보장하지 않는다.
