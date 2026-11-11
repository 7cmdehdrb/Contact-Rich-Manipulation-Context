# 원환경 play 복원과 Raw Action 실험 ID 분리

2026-11-11. [현재 환경 비교·play 안내](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#raw-파생-환경과-원환경-play) · [분리 전 직접 수정 이력](2026-11-11_finger_raw_action_restore.md) · [Semi-Prof5% 상한 제거](2026-11-11_semi_prof_reward_order_incident.md)

## 요청과 의도

사용자는 직전의 Clip 제거·Last Action tanh·팔 Joint Velocity 비용−0.03 변경을 원환경에서 롤백하고 다른 ID로 분리하도록 요청했다. 기존 환경을 기존 조건으로 play하기 위함이다. 단, Wrench5% 상한 제거는 원환경에 적용하는 것이 맞다고 명시했다.

따라서 일반 Gaussian 전환은 되돌리지 않고, 그 이후의 Raw Action 복원 실험만 분리한다. 과거 tanh/atanh 정책으로 되돌리는 작업이 아니다.

## 원환경과 새 등록

| 원환경 ID | 직접 상속하는 새 ID | 새 experiment_name |
| --- | --- | --- |
| `Inspire-Sweep-Simple-Finger-v1` | `Inspire-Sweep-Simple-Finger-Raw-v1` | `inspire_sweep_simple_finger_raw_v1` |
| `Inspire-Sweep-Simple-Finger-v2` | `Inspire-Sweep-Simple-Finger-Raw-v2` | `inspire_sweep_simple_finger_raw_v2` |
| `Inspire-Sweep-Simple-Semi-Prof-v0` | `Inspire-Sweep-Simple-Semi-Prof-Raw-v0` | `inspire_sweep_simple_semi_prof_raw_v0` |

| 항목 | 원환경으로 복원한 계약 | Raw 실험 계약 |
| --- | --- | --- |
| 실행 액션 | 기존 축별 raw Clip 후 Scale | 추가 raw Clip 없이 부모 Scale |
| Last Action | Clip 후 raw 값 | 원본 Raw Action의 tanh |
| Action 변화 비용 | Clip 후 현재·직전 명령 차이 | 원본 현재·직전 Raw Action 차이 |
| 팔 Joint Velocity 비용 | −0.06 | −0.03 |
| Gaussian·PPO·초기 분포 | 기존 일반 Gaussian·원본 샘플 | 동일 |
| 속도 터미네이션 | 초기2rad/s,2000–5000/250 간격으로1rad/s까지 감소 | 각 부모 그대로 |
| Semi-Prof Wrench5% 상한 | 제거 상태 유지 | 부모에서 제거 상태 상속 |

손6자유도·관측66+64D·액션12D·OSC Scale0.03/0.15·물리 손 관절 목표/토크 한계는 모두 유지한다. Raw Action 차이 비용에도 기존 Arm/Hand weight−0.03 및cap100을 적용한다. 다른 보상 가중치·함수·게이트·reset·Scene·물성·커리큘럼·종료는 각 부모 계약 그대로다.

## 구현과 전체 대조

기존 역할별 파일 안에 Raw EnvCfg3개, Raw reward Cfg3개, Raw PPO runner Cfg3개 및 등록을 추가했다. 원환경에서 삭제했던 Clip helper·Action subclass·Last Action 함수는 복원했다. 사용자 작업트리에 있던 Wrench 상한 제거 변경은 보존했다.

- EnvCfg는 각각 해당 원환경을 직접 상속한다. Raw-v2는 Raw-v1이 아니라 Finger-v2의 후퇴·성공 계약을 상속한다.
- runtime의 `clip_raw_actions` 기본값은True다. Raw EnvCfg만False로 지정한다. Raw는 Finger-v0 Action/Observation Cfg를 사용하므로 term 내부 추가 raw Clip도 없다.
- 기존 runtime3개를 재사용한다. 분기 이후 정상적인 부모 step을 계속 호출하여 Finger-v2 retreat state 및 Semi-Prof scene-update 힘 수집·부분 reset을 유지한다.
- Raw reward Cfg는 각 부모를 상속하고 팔 Joint Velocity weight만−0.03으로 바꾼다. Semi-Prof 원환경의 `max_positive_fraction=None`은 유지된다.
- Raw PPO 설정은 각 부모를 상속하고 실험명을 분리한다. Raw에는 실제 실행 Clip이 없으므로 `report_clip_fraction=False`; mean/std는 양쪽 모두 기록한다. 정책 파라미터·초기화·log probability·네트워크는 동일하다.
- 원환경의 Gaussian state_dict 키·형태는 변경하지 않았다. 진단 여부는 비파라미터 설정이다. 기존 원환경의 출력·관측 처리는 직전 Gaussian Clip 버전으로 돌아갔다.

기존 로그 디렉터리·checkpoint 파일을 이동하거나 정리하지 않았다. 원환경 ID와 로그 실험명은 유지한다. 새 실험 로그는 별도 experiment_name 아래 기록된다.

## Play와 체크포인트 의미

사용자가 이전 Gaussian Clip 정책을 확인하려면 **기존 ID**로 실행한다. 아래 checkpoint는 실제 파일 경로로 바꾼다.

```bash
python src/inspire_sweep_baseline/scripts/play.py --task Inspire-Sweep-Simple-Semi-Prof-v0 --checkpoint "/absolute/path/model_XXXX.pt" --num_envs 16
```

Finger-v1/v2는 task를 해당 기존 ID로 지정한다. 새로운 Raw 실험 학습은 다음과 같다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Semi-Prof-Raw-v0 --num_envs 2048 --headless
```

원환경과 Raw는 모델 차원이 같지만 관측·제어 의미가 다르다. 원환경 정책을 Raw ID로 play하면 같은 조건의 재현이 아니다. 구 tanh 변환 정책 checkpoint의 거부는 유지하며, 그 checkpoint를 일반 Gaussian으로 자동 변환하지 않는다. 사용자 실제 checkpoint를 확보하여 GPU play한 것은 아니다.

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

**83 passed in 11.52s**.

- 세 Raw EnvCfg의 직접 부모·전체 구성 차이를 대조: actions/observations/clip flag/팔 속도 비용 외 동일, 부모 설정은 변하지 않음.
- Gym ID·runtime/EnvCfg/PPO entry point·독립 experiment_name·진단 설정 검증.
- 실제 runtime step을 Clip True/False로 각각 실행해 ActionManager 입력·Last Action·action-rate·원본 PPO 저장·진단 지표를 검증했다. 물리/관측 결합은 CPU 대역이며 두 rollout·두 실제 PPO 업데이트의 유한성을 확인했다.
- 기존 속도 종료 경계값·v2 후퇴 게이트·Semi-Prof 힘 수집·보상·5% 상한 제거 회귀 유지.
- 일반 Gaussian 분포·기존 gradient 오류 재현9조건·checkpoint 저장/로드·전체 JIT 출력 일치 확인.

GPU/PhysX 실제 환경 초기화·학습·사용자 checkpoint play는 미검증이다. 새 ID별 실제 학습 성능이나 Collection Time 개선을 주장하지 않는다. 현재 기준 문서와 인계는 이번 분리 결과로 갱신하고, 분리 전 직접 수정 로그에는 후속 결정으로 대체됐음을 명시했다.
