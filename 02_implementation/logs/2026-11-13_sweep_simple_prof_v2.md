# Simple Prof-v2: 속도 종료·Runner Clip·접촉 높이

현재 최종 계약은 [손6차원 후속 변경](#후속-변경-prof-v2-손6차원-관측제어)이다. 아래 초기8D 구현·검증은 변경 이력으로 보존한다.

2026-11-13. 사용자 요청으로 `Inspire-Sweep-Simple-Prof-v1`을 직접 상속하는 `Inspire-Sweep-Simple-Prof-v2`를 추가했다. 사용자는 부모 정책이 물체를 위에서 누르며 목표 주변을 빠르게 왕복하고 접근 보상을 반복 수령한다고 보고했다. 이번 변경은 그 행동에 속도·액션·접촉 높이 제약을 적용하는 실험이며, 보상식 자체를 바꾸지 않는다.

[전체 환경 계약](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#prof-v2-속도-제한과-접촉-높이) · [앞선 Finger-v0-Test Runner Clip](2026-11-13_finger_v0_test_runner_clip.md).

## 요청과 최종 설정

| 항목 | 부모 Prof-v1 | 새 Prof-v2 |
| --- | --- | --- |
| EnvCfg 직접 부모 | Prof-v0 | Prof-v1 |
| 팔 속도 실패 종료 | 초기4rad/s, 10000 iteration부터250마다0.05 감소·최소2 | 절댓값>1.0rad/s 고정 |
| 속도 임계값 커리큘럼 | 활성 | 해당 항만 None |
| Runner `clip_actions` | None | 1.5707963267948966, 전체8축 |
| Last Action | tanh(manager action) | manager action 그대로 |
| 접촉 조건부 Goal Distance·방향 비용 EEF 높이 | 선반 표면 기준15cm 미만 | 12cm 미만 |
| 보상 함수·가중치·비용 상한 | 부모 구성 | 동일·새 상한 없음 |
| PPO 실험명 | `inspire_sweep_simple_prof_v1` | `inspire_sweep_simple_prof_v2` |

Last Action은 처음에는 부모 보존으로 준비했지만, 사용자 선택 답변 **“직전 Finger-v0-Test처럼 clip 후 값을 그대로 입력”**을 받아 Prof-v2 전용 관측 설정으로 교체했다. 최종 검증은 그 답변을 반영한 코드 기준이다. Prof-v1의 tanh는 유지한다.

실제 보상 term의 높이는 사용자 추정14cm가 아니라15cm였다. `goal_distance`와 `direction_deviation`의 `eef_height_limit`만0.12로 변경했다. 환경의 일반 `goal_reward_height_limit/contact_height_limit` 필드0.14는 이 두 Prof term의 실제 gate가 아니므로 변경하지 않았다. Prof는 `hand_contact` 보상이 이미 None이며 새로 활성화하지 않았다. 지속 근접 `reaching`과 step별 접근 보상 수식·계수는 유지했다.

## 액션 경로와 영향

```text
Gaussian sample (PPO rollout/log-prob 보존)
  → RslRlVecEnvWrapper clamp(-π/2, +π/2)
  → ActionManager current/previous 저장
  → OSC scale / 기존 손 openness 처리
  → action-rate: bounded current/previous 차이 제곱합
  → Last Action: current 그대로, tanh·추가 Clip 없음
```

Prof는 Finger12D가 아니라 팔6축+손 openness2축의8D다. 모든 raw 채널에 같은 Runner 제한을 적용한다. 병진 scale0.03 이후 축별±0.0471239m, 회전 scale0.15 이후 Euler 축별±0.235619rad(13.5°)이며 이후 기존 quaternion/axis-angle 변환을 수행한다. 손의 기존0~1 openness mapping과 물리 목표 제한은 보존한다. Last Action은 최종 관절 목표가 아니라 wrapper가 수락한 raw 명령이다.

팔 속도 종료는 arm joint만 검사하며 정확히±1rad/s는 허용하고 초과하면 실패 종료한다. 물리 관절 속도 한계나 OSC 속도 제어를1rad/s로 변경하는 작업이 아니다. 높이는 현재 EEF와 초기 선반 표면을 비교하는 strict < 조건이다. 정확히12cm, 비접촉, stale/nonfinite 센서에서는 두 term을 인정하지 않고, 그 사이 움직임을 이후 보상으로 소급하지 않는다.

## 구현·부모 보존·최종 대조

기준 HEAD는 `1ab6e579cf1c4f4152954b1c6fb0120a99729eb5`. 앞선 Finger-v0-Test 수정과 문서 submodule의 기존 수정·미추적 기록은 보존했다. 기존 역할별 파일에 새 자식 설정을 추가했다.

- `__init__.py`: Prof-v2 등록, 공통 `SweepSimpleEnv` runtime 사용.
- `envs/sweep_simple_envs.py`: `SweepSimpleProfV2EnvCfg(SweepSimpleProfV1EnvCfg)` 및 아래 네 설정 연결.
- `mdp/terminations/sweep_simple.py`, `mdp/curricula/sweep_simple.py`: 고정1rad/s와 해당 일정 비활성화.
- `mdp/rewards/sweep_simple.py`: Prof-v1 rewards 직접 상속, 두 height params만 변경.
- `mdp/observations/sweep_simple.py`: 부모 Simple 관측 직접 상속, actions callable만 기존 `raw_previous_action`으로 교체.
- `agent/sweep_simple_ppo_cfg.py`: Prof-v1 Runner 직접 상속, 실험명과 clip_actions만 변경.
- `tests/test_sweep_simple.py`: 전체 config 차이·부모 격리·속도/높이 경계·관측·등록 검사.

전체 config 대조로 위 차이만 확인했다. Scene/자산/물성, Command/Event/reset/IK, 액션8D와 관측58+64D의 순서/차원, 보상 함수/계수, 다른 종료·커리큘럼, Gaussian 분포·모델/encoder·PPO hyperparameters는 유지한다. 자식 설정을 변형해도 기존 및 새 부모 인스턴스가 변하지 않음을 검사했다. 부모 Prof-v1, 형제 Prof-Hard, Finger/Wrench와 공유 runtime/제어/보상 함수는 이번 작업에서 변경하지 않았다.

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

최종 raw Last Action 반영 후 **69 passed in11.36s**. 실제 termination 함수로 ±1 경계/손 제외, 실제 `ContactConditionedSweep`으로12cm 아래/동일/위·접촉/센서 유효성·소급 보상 없음, raw Last Action 그대로 반환 및 부모 tanh 유지, 전체 Env/PPO diff와 등록을 검사했다. 기존 Finger 테스트의 실제 upstream wrapper/ActionManager/OSC 전처리 검사도 통과했다. CPU config/manager 검사는 simulator leaf double을 사용하며 PhysX 실행을 대체하지 않는다.

## GPU 검증

RTX3090, Isaac Sim5.1, seed42. `train.py`와 절대 experiment 경로를 사용해 기존 `logs/rsl_rl`은 건드리지 않았다. 부모 tanh를 임시 상속한 첫 smoke64환경/2iterations도 통과했으나, 최종 결과는 아래 raw Last Action 설정 재실행을 기준으로 한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Simple-Prof-v2 --num_envs 64 --headless \
  --max_iterations 2 --seed 42 \
  --experiment_name /home/min/7cmdehdrb/grad/outputs/sweep_simple_prof_v2/training \
  --run_name raw_last_action_smoke
```

**최종64환경·36step/env·PPO2 iterations 정상 완료, process exit0**. [stdout](../../../../outputs/sweep_simple_prof_v2/train_raw_last_action_stdout.log), [run](../../../../outputs/sweep_simple_prof_v2/training/2026-11-13_15-59-15_raw_last_action_smoke)에 보존했다.

- 실제 저장 YAML에서 clip_actions=π/2, raw_previous_action, 속도 threshold1.0, 해당 curriculum null, 두 height params0.12를 확인했다.
- model_0.pt와 model_1.pt 각각100개 tensor가 모두 유한했다.
- Actor/Critic obstacle encoder weight가 두 checkpoint 사이에 실제 갱신됐다.
- 마지막 iteration의 로그에는 팔 속도 종료 지표0.9787·평균 에피소드 길이7.70step이 기록됐다. 초기 정책에1rad/s 종료가 강하게 작용한 결과이며 정책 성능이나 exploit 해소의 증거로 해석하지 않는다.

## 문서 검증

현재 인계·활성 환경 안내·Simple 설명서(등록16개/상속/Prof-v2 계약)·로그 색인을 갱신했다. 변경5개 Markdown 수식 검사, 외부 workspace 경로를 포함한 해당 문서 링크 검사, 전체581개 Markdown 링크 검사, workspace와 문서 submodule의 git diff --check를 통과했다. 별도 렌더링은 미검증이다.

## 미검증 범위

장기 학습의 수렴·성공률, 위에서 누르기·왕복 행동의 해소, 기존 checkpoint의 resume/play 성능과 export 단독 실행은 미검증이다. 접근 보상은 여전히 step별 개선을 보상하므로 이번 제약만으로 반복 수령 가능성이 사라졌다고 단정하지 않는다. Runner Clip은 실행/비용/Last Action 경계를 제한하며 raw Gaussian 평균·std 자체를 제한하지 않는다. wrapper 없는 직접 환경 호출이나 export 소비자는 Runner Clip을 자동 적용받지 않는다.


## 후속 변경: Prof-v2 손6차원 관측·제어

2026-11-13 사용자 지시: “Finger 과 같이6차원 관측 및 제어로 변경해줘. v2 에만 변경을 가한다.” 기존 Prof-v2를 직접 수정하며 새 ID를 만들지 않았다. 기준은 위 raw Last Action 반영까지의 작업트리이며 HEAD는 동일하다. 앞선 Finger-v0-Test 변경과 다른 환경은 유지했다.

| 항목 | 직전 Prof-v2 | 최종 Prof-v2 |
| --- | --- | --- |
| 손 관측 | hand_configuration2D | 실제 drive6관절 위치 rad |
| 손 액션 | openness2D | 독립 절대 관절 목표6D(rad) |
| 전체 액션 | 8 | 12 |
| 관측 | policy58+obstacles64 | policy66+obstacles64 |
| 모델 | WrenchRefactorRelativeModel, MLP74D | 기존 SweepSimpleFingerModel, MLP82D |
| 액션 변화 비용 | 팔6+손2 제곱합 | 팔6+손6 제곱합, 계수−0.03·무상한 유지 |
| runtime 손 action history reset | 마지막2채널1 | 손6채널0rad |
| EnvCfg/PPO 직접 부모 | Prof-v1 | 동일 |
| clip/Last Action/팔 종료/보상 높이 | ±π/2·raw·1rad/s·12cm | 동일 |

구현은 기존 구성요소를 재사용했다. `SweepSimpleProfV2EnvCfg.actions`에 `SweepSimpleFingerActionsCfg`, 전용 관측 설정의 부모에 `SweepSimpleFingerObservationsCfg`를 연결했다. raw Last Action override는 유지했다. `SweepSimpleProfV2RewardsCfg`의 팔·손 action-rate callable만 `finger_action_rate_l2`로 바꾸어 손6축을 모두 계산한다. 액션 크기 자체가 아니라 current/previous 변화량 비용이라는 기존 의미는 같다.

PPO는 직접 부모 Prof-v1·하이퍼파라미터·Gaussian std1을 유지하며 actor/critic만 기존 Finger 모델 설정을 사용한다. 정의 의존성을 맞추려고 Prof-v2 Runner 선언을 Finger 모델 설정 아래로 이동했고 다른 Runner 값은 변경하지 않았다. 등록 runtime은 Prof-v2에만 `SweepSimpleFingerEnv`를 연결해 기존 손6채널 reset을 사용한다. 이 runtime은 SimpleEnv의 직접 자식이며 속도 종료·보상·추가 raw clip을 바꾸지 않는다. Finger-v1의 bespoke clip runtime을 사용하지 않는다.

Scene/자산·물성·팔 OSC/scale·Command/Event/IK·reset 배치·관측의 나머지 term/순서·기존 보상 함수/계수(액션 차원 대응 제외)·종료·커리큘럼은 유지한다. 현재 Prof-v2의 손 관측/액션/모델·reset 처리만 Finger-v0와 같아지며 Prof의 목표 보상은 유지한다. 손 목표는 URDF 범위로 제한되고 mimic 관절로 매핑되는 기존 Finger 계약이다. 부모 Prof-v1·형제 Prof-Hard는2차원 손과 기존 모델/runtime을 유지한다.

### 손6축 검증

전체 Env/PPO 차이·부모 격리 기대값과 runtime 등록 검사를 갱신했다. wrapper→ActionManager→OSC scale→raw Last Action/무상한 패널티 경로 검사를 Prof-v2에도 실행하도록 매개변수화했다. 기존 실제 Finger 손 mapping·6채널 비용·부분 reset·130D export/모델 gradient 검사도 동일한 재사용 컴포넌트를 검증한다. CPU fixture의 action leaf는 double이므로 실제 클래스/차원 연결은 GPU 저장 설정과 실행 출력으로 대조한다.

위 CPU 검증과 같은5개 파일 명령으로 **70 passed in12.08s**. 초기6축 변경 후69개 통과에 이어 Prof-v2 wrapper 경로 검사를 추가하고 다시 전체70개를 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Simple-Prof-v2 --num_envs 64 --headless \
  --max_iterations 2 --seed 42 \
  --experiment_name /home/min/7cmdehdrb/grad/outputs/sweep_simple_prof_v2/training \
  --run_name six_finger_smoke
```

RTX3090에서64환경·36step/env·2iterations 학습 완료, exit0. [stdout](../../../../outputs/sweep_simple_prof_v2/train_six_finger_stdout.log) · [run](../../../../outputs/sweep_simple_prof_v2/training/2026-11-13_16-22-09_six_finger_smoke).

- 실제 출력의 손 관측6D·policy66D·obstacles64D·actions12D 확인.
- 저장 YAML의 FingerJointPositionAction, hand_drive_positions6관절, raw_previous_action, 양쪽 finger_action_rate_l2와 actor/critic SweepSimpleFingerModel 확인.
- clip_actions=π/2·1rad/s 종료·관련 curriculum null·높이0.12 두 항 확인.
- model_0/model_1 각각100개 tensor 모두 유한, Actor/Critic encoder 실제 갱신 확인.
- actor MLP 입력 weight(256,82), 출력 weight(12,64) 확인.

현재 인계·활성 안내·환경 설명·로그 색인에 손6축 최종 계약을 반영했다. 변경5개 Markdown 수식 검사·외부 경로 포함 링크 검사·전체581개 문서 링크 검사와 양쪽 저장소 git diff --check를 통과했다. 실제 문서 렌더링은 미검증이다.

### 호환성과 미검증

구 Prof-v2의8D 정책 checkpoint는 입출력 차원이 달라 최종12D 환경에 직접 resume/play할 수 없다. 기존 학습 산출물은 보존했고 자동 변환은 구현하지 않았다. 새 학습을 사용한다. 손 액션 수가 늘어 같은 계수여도 손 action-rate 총합의 분포는 달라질 수 있으며 임의로 가중치를 조정하지 않았다. 장기 수렴·정책 성능·왕복 행동 개선은 미검증이다.
