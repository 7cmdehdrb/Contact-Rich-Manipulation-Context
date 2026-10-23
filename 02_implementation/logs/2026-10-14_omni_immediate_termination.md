# Omni 체크포인트의 첫 스텝 종료 진단

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기록일: 2026-10-14. 저장된 TensorBoard 로그와 설정을 확인한 결과이며, 새 시뮬레이션 결과가 아니다. 환경 코드와 종료 기준은 변경하지 않았다.

## 대상과 기준 코드

- Task: `Isaac-Inspire-Sweep-Omni-v0`. `InspireSweepOmniEnvCfg`는 `InspireSweepEnvCfg`를 상속하고, 실행 환경 `InspireSweepEnv`는 Isaac Lab `ManagerBasedRLEnv`를 상속한다.
- Run: [2026-10-14_16-16-28_centered_spawn_goal15cm](../../../../logs/TEMP/2026-10-14_16-16-28_centered_spawn_goal15cm/). 최초 진단 당시 workspace 루트에 있었고 후속 비교 시 `logs/TEMP`로 이동된 것을 확인했다. 마지막 저장 모델은 `model_4100.pt`, 이벤트 로그는 iteration 4137까지 있다.
- 저장 설정: seed 42, 스폰 반경 0.02 m, 목표 거리 0.15 m, physics dt 0.01 s, decimation 2, episode 제한 10 s.
- 현재 workspace commit: `e54ae15bca563cd602b85dbf61f9c594a59a438f`. 기존 `.aws` 삭제 및 미추적 run 폴더를 보존했다. 문서 submodule은 작업 시작 시 변경이 없었다.
- Run의 `git/Contact-Rich-Manipulation.diff`에 기록된 학습 당시 commit은 `c08beb139dcea0927a6e4d728d3c0ec62ad74721`; 현재 코드와 당시 코드의 동일성을 전제로 삼지 않는다.

## 확인한 결과

TensorBoard `EventAccumulator`로 scalar 전체를 읽었다. 각 항목은 4,138개 기록이다.

| 항목 | 전체 기록의 최솟값 / 최댓값 | 해석 |
| --- | --- | --- |
| `Train/mean_episode_length` | 1 / 1 | 학습 전체에서 평균 1 제어 스텝(0.02초) 종료 |
| `Episode_Termination/hand_velocity` | 1 / 1 | 기록된 종료 통계에서 항상 해당 term 활성 |
| `Episode_Termination/success` | 0 / 0 | 성공 기록 없음 |
| object_drop, push_fast, shelf_collision, object_outside_shelf, shelf_displacement | 모두 0 / 0 | 이 run의 종료 원인으로 기록되지 않음 |
| `Train/mean_reward` | 약 −80.2811 / −79.9988 | 거의 항상 실패 이벤트 −80으로 끝남 |

`time_out`은 첫 iteration만 약 0.00004069이고 이후 0이다. 이 예외는 Arm 속도 종료가 항상 1인 사실을 바꾸지 않는다. `Episode_Reward/failure=-8`은 RewardManager가 에피소드 합계를 최대 에피소드 시간 10초로 나눈 값이므로 실제 실패 이벤트는 −80이다.

`hand_velocity`는 이름과 달리 [arm_velocity](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/sweep.py)의 결과다. 저장된 `params/env.yaml`도 Arm 6개 관절 이름을 명시하며, 절대 관절 속도가 하나라도 **1 rad/s 초과**이면 종료한다. YAML의 미해결 `joint_ids: slice(None)`만 보고 모든 손가락을 검사한다고 판단하면 안 된다. Isaac Lab의 `SceneEntityCfg.resolve`가 명시된 관절 이름을 실행 시 인덱스로 해석한다.

## 제어 경로와 확인 한계

저장된 Arm action은 `JointPositionAction`, scale 0.5, `use_default_offset=true`다. 목표는 `default_joint_pos + 0.5 * action`이며 매 스텝 상대 증분이 아니다. Action term `clip`과 runner `clip_actions`는 모두 null이다. Arm actuator의 simulation 속도 한계는 3.14 또는 6.28 rad/s로 종료 기준 1 rad/s보다 높다. 따라서 물리 속도 한계가 종료 기준 초과를 방지하는 구성은 아니다.

1스텝 에피소드와 보상 정규화를 사용하면 `Episode_Reward/arm_joint_velocity`에서 Arm 전체 RMS 속도를 역산할 수 있다. 처음 약 2.711 rad/s, 마지막 약 3.479 rad/s다. 계산은 `sqrt(-logged_reward * 10 / (0.01 * 0.02))`이며, 관절별 최대 속도나 최초 초과 관절을 복원한 것은 아니다.

같은 방법으로 `arm_action_rate`에서 action 변화 RMS를 역산하면 처음 약 1.002, 마지막 약 11.004다. Reset 직후 이전 Arm action이 0이므로 1스텝 에피소드에서 첫 명령 크기의 지표가 된다. 마지막 값은 joint target 변화 RMS 약 5.502 rad에 해당한다. 이는 학습 rollout의 집계이며 `model_4100.pt`의 deterministic play 첫 action을 측정한 값이 아니다.

**확인된 직접 원인:** 학습 전체에서 Arm 속도 종료 조건이 첫 스텝에 활성화된다. 정상적인 Sweep을 학습한 뒤 재생에서만 고장 난 run으로 볼 수 없다.

**미확정 근본 원인:** 초기 정책 명령에 대한 제어 응답, reset 직후 자세·접촉의 튐, 실행 시 관절 mapping 문제 중 어느 것이 최초 속도 초과를 만들었는지는 저장 로그만으로 확정할 수 없다. 무제한 위치 명령과 큰 후반 action은 문제를 지속시키는 경로로 의심되지만 초기 상태의 무입력 안정성을 입증하지 않는다.

## 실제 실행한 검사와 다음 재현

Workspace 루트에서 다음 형식의 명령을 실제 실행해 전체 scalar 수·범위·첫 값·마지막 값을 확인했다.

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python - <<'PY'
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
e = EventAccumulator('2026-10-14_16-16-28_centered_spawn_goal15cm', size_guidance={'scalars': 0})
e.Reload()
for tag in e.Tags()['scalars']:
    if tag.startswith('Episode_Termination/') or tag in ('Train/mean_episode_length', 'Train/mean_reward'):
        values = [item.value for item in e.Scalars(tag)]
        print(tag, len(values), min(values), max(values), values[0], values[-1])
PY
nvidia-smi
```

Scalar 읽기는 exit 0. `nvidia-smi`는 exit 9, NVIDIA driver 통신 실패였다. 현재 머신에서는 GPU 재생·무입력 대조 실험을 실행하지 못했다. CPU 테스트를 새 물리 재현의 대체로 실행하지 않았다.

GPU 머신에서 필요한 다음 진단은 동일 reset·seed에서 Arm action 0/Hand OPEN과 checkpoint action을 각각 적용하고, auto-reset 이전 첫 스텝의 관절 이름·실제 속도·목표각·활성 종료 term을 비교하는 것이다. 전자는 초기 물리 상태, 후자는 정책 명령 기여를 구분한다. 최초 실패 관절과 원인을 확인하기 전에 종료 기준을 임의로 높이거나 제거하지 않는다. 이번 요청에서는 환경 수정·재학습·회귀 테스트를 수행하지 않았다.

문서 검증 명령과 결과는 문서 작성 후 확인했다: 변경 문서 수식 검사, 내부·workspace 링크 검사 및 문서 submodule `git diff --check`.

## 후속: Baseline과 Omni의 대조

사용자가 Baseline에서는 정상 동작했다고 설명하여 저장된 실제 학습 기록을 추가 비교했다. 여기서 Baseline은 `Isaac-Inspire-Sweep-Baseline-v0`를 뜻하며, 더 오래된 참고 task와 구분한다. 환경 코드와 사용자가 변경한 v1 threshold 100.0은 수정하지 않았다.

### 실제 run 비교

| Run | 첫 iteration 평균 길이 | iteration 50 | iteration 4137 | 처음 평균 길이 10스텝 초과 |
| --- | ---: | ---: | ---: | --- |
| [Baseline](../../../../logs/backup/Isaac-Inspire-Sweep-Baseline-v0/2026-10-13_17-00-33_baseline_mass_z9cm_1rad/) | 1 | 464.39 | 449.51 | iteration 28, 13.02스텝 |
| [Realistic Physics](../../../../logs/backup/Isaac-Inspire-Sweep-Realistic-Physics-v0/2026-10-13_17-39-41_realistic_mass_friction/) | 1 | 446.93 | 451.93 | iteration 28, 11.42스텝 |
| Omni v0 | 1 | 1 | 1 | 전체 4,138 iteration에서 없음 |

Baseline와 Realistic도 첫 iteration의 `hand_velocity` 종료 통계는 약 0.999986이다. 따라서 초기에 제한을 넘는 것 자체는 Omni만의 현상이 아니다. 두 비교 run은 빠르게 1스텝 종료를 벗어났고 Omni는 그렇지 못했다. 에피소드 길이 증가는 Sweep 성공을 입증하지 않는다.

추가로 작업 중 생성된 v1 run도 읽었다. `2026-10-14_22-09-16_centered_spawn_goal15cm_arm2rad`의 저장된 threshold는 2.0이며, 확보된 74개 iteration에서 시작과 마지막 평균 길이는 1, hand_velocity는 1이었다(iteration 10 길이 1.01). `2026-10-14_22-13-19_centered_spawn_goal15cm_arm2rad`의 저장 threshold는 100.0이며, 확보된 6개 iteration에서는 해당 종료가 0, 평균 길이는 첫 13.60/마지막 33.04, 성공은 0이다. run 이름만으로 실제 threshold를 판별하면 안 된다. 라이브 run의 후속 기록은 이번 snapshot에 포함되지 않는다.

### 구성·함수 대조

세 run의 `params/env.yaml`을 `yaml.BaseLoader`로 읽어 Python tag를 실행하지 않고 비교했다. Actions, Observations, Commands, robot init_state, robot actuators, reset_all, hand_velocity 설정은 세 run에서 동일했다. 초기 관절각·position action scale·gain·관절 이름 또는 속도 기준 변경으로 차이를 설명할 근거는 없다. 동일 seed라도 reset/RNG 소비 순서가 다르면 정책 초기 가중치나 샘플 action이 동일하다는 뜻은 아니다.

| 항목 | Baseline | Omni v0 | 의미 |
| --- | --- | --- | --- |
| Arm 목표각 | default + 0.5 × action | 동일 | action 크기에 따른 급격한 위치 명령 가능성은 공통 |
| Arm 속도 비용 | −0.03 × 6개 관절 속도 제곱의 합 | −0.01 × 6개 관절 속도 제곱의 평균 | 동일 속도에서 비용 크기가 1/18 |
| Arm action 변화 비용 | −0.03 × 전체 action 변화 제곱의 합 | −0.03 × Arm 6개 변화 제곱의 평균 | Hand 변화 0일 때 Arm 비용 크기가 1/6 |
| 실패 이벤트 | 별도 −80 항 없음 | 종료 시 −80 | 첫 스텝 실패 rollout 대부분에서 큰 공통 비용 |
| 접근·정렬·Homing | dense 접근, 정렬 및 Homing 보상 | 접근 진척만 유지하고 정렬·Homing 제거 | 유용한 자세·명령을 학습하는 신호 변경 |
| 물체 스폰 | X −0.75 ±0.02, Y ±0.02 m | X −0.7/Y 0 기준 R=0.02 m 원판 | 고정 로봇 자세와의 초기 접촉 관계 변경 가능 |
| 물성 | 1 kg 물체/기존 마찰 | 물체 0.230–0.500 kg/마찰 랜덤화 | Realistic 비교 run은 같은 물성 변형에서도 1스텝 종료를 벗어남 |

기존 CPU fixture의 실제 Isaac Lab configclass를 사용해 Baseline/Omni를 인스턴스화하고, 동일 Actions/Observations/Commands/robot init_state/Arm actuator 값을 확인했다. 실제 reward 함수에 Arm 6개 속도 2 rad/s, Arm action 변화 1을 넣어 0.02 s의 weighted reward를 계산했다.

- 속도 비용: Baseline −0.0144, Omni −0.0008 (18배 차이).
- Arm action 변화 비용: Baseline −0.0036, Omni −0.0006 (6배 차이).

검사 명령은 workspace에서 `/home/min/miniconda3/envs/env_isaaclab/bin/python -`로 실행한 CPU harness였다. `tests/conftest.py`의 `load_mdp`, `make_env`, `test_omni_configuration.py`의 `omni_config` fixture를 직접 호출해 production reward 함수를 계산했고 exit 0이었다. 시뮬레이션 재현은 아니다.

로그 비교는 같은 Python으로 `RawEventFileLoader`와 `Event.FromString`을 사용해 각 run의 `*tfevents*` 파일을 순회하고 `Train/mean_episode_length`, `Train/mean_reward`, `Episode_Termination/hand_velocity`, `Episode_Termination/success`를 집계했다(exit 0). 최초 EventAccumulator 비교는 Baseline/Realistic 결과까지 출력한 후 작업 중 이동된 Omni 루트 경로에서 실패했다. 이후 현재 `logs/TEMP` 경로로 다시 읽어 모든 비교를 완료했다.

### 의견과 구분 실험

가장 유력한 가설은 제어기 자체 변경이 아니라 **Omni 보상 변경으로 속도·명령 크기를 낮추는 학습 신호가 약해져 초기 1스텝 실패에서 벗어나지 못한 것**이다. 함수 대조와 두 선행 run의 학습 곡선이 뒷받침하지만 인과관계는 ablation 전까지 미확정이다. 모든 sample에 같은 −80이 지급될 때 그 공통 항만으로 unsafe action의 정도를 구별할 수 없다. 반대로 −80의 존재 자체가 항상 학습 실패를 만든다고 단정하거나, PPO advantage normalization 후 그대로 80배 gradient가 된다고 해석하면 안 된다.

다음 순서의 대조를 제안한다. 구현·실행한 실험이 아니다.

1. 동일한 Arm action 0/Hand OPEN, 초기 상태 및 seed로 Baseline/Realistic/Omni의 첫 관절 속도·접촉을 비교한다. Omni만 움직이면 중앙 스폰·접촉/물성 경로를 먼저 조사한다.
2. Omni의 Arm 속도 비용을 Baseline과 같은 sum/−0.03으로 복원한 실험만 먼저 비교한다. 이후 action 변화 비용을 복원하는 실험은 별도로 수행한다. 초기 1스텝 종료를 벗어나는지가 판정 신호다.
3. 위 결과가 불충분하면 별도 실험에서 실패 이벤트 크기만 변경해 critic 추정과 advantage 분산을 비교한다. 스폰 중심을 −0.75로 바꾸는 실험도 별도로 수행한다.

현재 머신에서 GPU 재현을 못 했으므로 최초 초과 관절·초기 관통 여부·정책 action이 실제 속도를 유발한 경로는 아직 미확인이다. v1의 100.0은 이 종료 term을 대부분 우회하는 진단 조건이며 성공이나 제어 문제 해결의 증거가 아니다.
