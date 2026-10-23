# Fusion Holding v1 계열과 OSC Base 기준 제어

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [계층도](../environments/ENVIRONMENT_EVOLUTION.md) · [개발 지침](../../00_guidelines/09_DEVELOPMENT_GUIDE.md)

## 요청과 기준

2026-10-23 사용자 요청으로 Holding의 장애물 encoder를16개 장애물 용량의64→32→16D로 확장한 v1 계열을 추가한다. 기존 환경 ID는 유지한다. 명시적으로 요청한 OSC v0의 이동 기준 EEF→Robot Base 및 stiffness200→100 변경은 기존 v0에도 적용하며 ObjectRandom v0이 상속한다.

작업 시작 기준 workspace는 `main`, commit `e6e36207cfa7ccffd7ba7b249809ffff54df88d4`다. 문서 submodule은 `main`, commit `8987a81fd8e91c0b1fec6da7c31b07a66ac1d9dc`이며 시작 시 내부 변경은 없었다. 이 기록은 이후 작업트리 변경을 설명하며 새 commit·원격 반영을 뜻하지 않는다.

## 환경·상속·등록

| 전체 Gym ID | EnvCfg → 직접 부모 | PPO Cfg |
| --- | --- | --- |
| `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v1` | `FusionHoldingV1EnvCfg` → `FusionHoldingV0EnvCfg` | `FusionHoldingV1PPORunnerCfg` |
| `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v1` | `FusionHoldingOSCV1EnvCfg` → `FusionHoldingV1EnvCfg` | `FusionHoldingOSCV1PPORunnerCfg` |
| `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v1` | `FusionHoldingOSCObjectRandomV1EnvCfg` → `FusionHoldingOSCV1EnvCfg` | `FusionHoldingOSCObjectRandomV1PPORunnerCfg` |

세 등록은 기존 `ContactSweepClutterFusionV1_0Env` runtime과 `CurriculumOnPolicyRunner`를 재사용한다. 각 PPO experiment 이름은 `inspire_contact_sweep_clutter_fusion_holding_v1`, `inspire_contact_sweep_clutter_fusion_holding_osc_v1`, `inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v1`이다. 기존 Holding v0·OSC v0·ObjectRandom v0 ID·직접 상속 관계는 유지한다.

## 구현 계약

- Holding v1은 장애물 관측16슬롯×`[present,x,y,z]`=64D와 Actor/Critic 각각64→32→16D encoder를 사용한다. policy55D·Critic 전용 현재 타겟XYZ3D 및 초기 장애물 가림·노이즈·정렬·인접 교환·episode 고정 규칙을 유지한다. 원시 입력은 Actor119D/Critic122D, 압축 후71D/74D다.
- 관측 용량과 실제 물체 수를 분리한다. Holding/OSC v1은 최대Gray5/White5 및 기존 개수 curriculum을 유지한다. ObjectRandom v1은 Gray7/White7 고정, 개수 curriculum 비활성 상태를 유지하며 남는2슬롯을0으로 채운다.
- OSC v0/v1은 `OperationalSpaceControllerActionCfg`, `task_frame_rel_path=None`, `pose_rel`, fixed impedance·stiffness100·damping ratio1·관성 분리·중력 보상이다. 이동·회전을 Robot Base 축으로 해석하고 현재 EEF pose에 상대 목표를 만든다. position/orientation scale1.0, Arm 관절 PD0, Hand2D와 EEF offset은 유지한다.
- ObjectRandom v1은 기존 YCB4종×크기3단계,1.5배 확대, 평평한 충돌 프록시, OBB 배치, 물체별 관성, reset 물성 갱신을 재사용한다. 새 환경의 부모는 OSC v1이고 ObjectRandom v0 EnvCfg를 상속하지 않는다.
- 보상·종료·성공·나머지 curriculum과 로컬 raw 제곱합 네 운동 비용 및 고정 계수는 유지한다. 기존 학습 로그를 이동·삭제하지 않는다.

v0의40D/56D encoder checkpoint는 v1의64D encoder와 직접 호환되지 않는다. 과거 EEF 기준 OSC checkpoint는 현재 Base 기준 명령과 의미가 달라 같은 동작을 보장하지 않는다. 새 학습 명령은 아래와 같다.

## 실행 안내

Workspace 루트, Linux. 아래 명령은 재현 안내이며 실행한 검증 명령과 구분한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v1 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v1 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v1 --num_envs 256 --headless
```

Play는 같은 launcher에서 `src/inspire_sweep_baseline/scripts/play.py --task <해당-v1-ID> --checkpoint <해당-v1-checkpoint.pt> --num_envs 1 --real-time`을 사용한다. Windows launcher는 `.\IsaacLab\isaaclab.bat`다. 모든 학습 안내는 `train.py` 정책을 따른다.

## 실제 검증

### CPU 회귀·모델 검증

Workspace 루트에서 다음을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v0.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v1.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_osc.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_models.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_cfg.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_population.py \
  src/inspire_sweep_baseline/tests/test_object_random_geometry.py \
  src/inspire_sweep_baseline/tests/test_bounded_osc.py \
  > outputs/fusion_holding_v1_validation/pytest_final.log 2>&1
```

결과는 **86 passed, 2 warnings, 6.09초**, exit0이다. 경고2개는 upstream Torch ONNX 내보내기 API의 deprecation이다. 검증 범위는 다음과 같다.

- 기존40D/56D 경로와 v1의64→32→16D, Actor/Critic16번째 슬롯의 gradient, 실제 CPU PPO update 및 checkpoint 저장·복원.
- Actor119D 입력의 TorchScript·ONNX 결과 일치, 비활성 슬롯의 NaN 좌표 차단, v0 인스턴스·Actor/Critic 설정 분리.
- 16개 장애물+타겟의 Scene·접촉 필터 구성과17번째 장애물 거부, reset의64D 초기 관측·부분 reset 보존.
- 실제 upstream OSC controller 계산에서 EEF identity/Z90° 모두 Base+X 이동·Base X축 회전, raw action 보존.
- 기존 Holding 보상·성공·일정, 물체 기하 검사와 bounded OSC 회귀.

첫 통합 실행은85 passed/1 failed였다. 실패는 새 테스트가 기존 무작위 기하 생성기에 조밀한16개 배치를 요구하여 발생한 `GenerationError`다. seed42의8+8 및1+15 배치 시도는40회 재시도 한도에 도달했다. 기하 규칙은 변경하지 않고, 전체16슬롯 reset 검사는 명시적인16점 layout을 공급한 뒤 production reset·가시성·state 쓰기 경로를 검증하도록 분리했다. 기본 개수의 실제 기하 reset은 CPU와 아래 GPU에서 그대로 검사했다.

### Isaac Sim GPU 검증

[검증 스크립트](../../../../src/inspire_sweep_baseline/tests/_fusion_holding_v1_probe.py)는 실제 registry로 Cfg·PPO를 불러오고 `gym.make`로 환경을 생성한다. NVIDIA RTX3090, `cuda:0`, seed42, 각2환경·32제어step을 사용했다. 일반 sandbox에서는 GPU driver에 접근하지 못하여 허용된 GPU 접근으로 실행했다. 다음 명령들은 실제 실행한 성공 실행이다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_sweep_baseline/tests/_fusion_holding_v1_probe.py --headless \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v1 \
  --output outputs/fusion_holding_v1_validation/osc_v1.json \
  > outputs/fusion_holding_v1_validation/osc_v1.log 2>&1

set -e
for variant in Holding-v0 Holding-v1 Holding-OSC-v0 Holding-OSC-ObjectRandom-v0 Holding-OSC-ObjectRandom-v1
do
  env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONDONTWRITEBYTECODE=1 \
    /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
    src/inspire_sweep_baseline/tests/_fusion_holding_v1_probe.py --headless \
    --task "Isaac-Inspire-Contact-Sweep-Clutter-Fusion-$variant" \
    --output "outputs/fusion_holding_v1_validation/$variant.json" \
    > "outputs/fusion_holding_v1_validation/$variant.log" 2>&1
done

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_sweep_baseline/tests/_fusion_holding_v1_probe.py --headless \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v1 --full-capacity \
  --output outputs/fusion_holding_v1_validation/holding_v1_capacity16.json \
  > outputs/fusion_holding_v1_validation/holding_v1_capacity16.log 2>&1
```

모두 exit0 및 `HOLDING FAMILY SMOKE PASSED`를 기록했다. 아래 ID 접미사는 모두 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-` 뒤에 이어진다.

| 환경 접미사 | 장애물 관측 | 생성된 타겟+장애물 | 32step 종료 횟수 |
| --- | --- | --- | --- |
| `Holding-v0` | 40D | 11개 | 0 |
| `Holding-v1` | 64D | 11개 | 0 |
| `Holding-OSC-v0` | 40D | 11개 | 0 |
| `Holding-OSC-v1` | 64D | 11개 | 0 |
| `Holding-OSC-ObjectRandom-v0` | 56D | 15개 | 0 |
| `Holding-OSC-ObjectRandom-v1` | 64D | 15개 | 0 |
| `Holding-v1 --full-capacity` | 64D | 17개 | 0 |

모든 실행에서 policy55D·privileged3D·Action8D, Actor/Critic encoder의 정확한 layer shape와 유한 출력, 보상·관절 위치·applied torque의 유한값, 부분 reset 시 다른 행 보존을 확인했다. OSC 네 환경은 실제 Action에 identity/Z90° EEF pose를 주입해 Base 기준 이동·회전을 검사하고 원래 pose 계산을 복구한 뒤32step을 실행했다. Arm은 앞16step 영 명령, 뒤16step Base+X0.001m 상대 명령이며 Hand는 열림 명령이다.

Cfg 전체 비교에서는 Holding v0→v1, ObjectRandom v0→v1의 차이가 `obstacle_observation_slots`뿐임을 확인했고 모든 요청 직접 상속과 OSC100 설정을 검사했다. `--full-capacity`는 Hydra처럼 Cfg 생성 후8+8 용량으로 바꾸어 runtime이17개 물체와 접촉 필터를 재구성하는지 확인한다. 활성 개수는 초기 curriculum의타겟1+Gray1+White1=3개이므로16개 동시 활성 접촉 성능을 검증한 실행은 아니다.

첫 GPU probe는 테스트 코드에서 `train.py`의 RSL-RL 호환 처리를 빠뜨려 `stochastic` 인자 오류가 발생했다. 호환 처리를 동일하게 적용한 뒤 위 성공 실행을 완료했다. 초기에는 Simulator 종료가 Python 예외를 가려 결과 JSON 없이 exit0이 나왔으므로, probe에 traceback 출력·실패 exit1을 추가했다. 따라서 성공 판정은 종료 코드뿐 아니라 결과 JSON과 성공 표식을 함께 확인했다. 환경 구현의 오류와 검증 스크립트의 오류를 구분한다.

원시 결과는 workspace의 `outputs/fusion_holding_v1_validation/`에 있다. 학습 실행·기존 학습 로그 변경은 수행하지 않았다.

### 문서 검사

패키지 README와 문서 submodule의 변경 Markdown12개에 `check_markdown_math.py` 및 `check_document_links.py --check-external`을 실행했다. 수식 검사 통과, 내부 링크423개·workspace 외부 링크103개·오류0이며 두 저장소의 `git diff --check`도 통과했다. 실제 파일 인수 전체와 명령·출력은 `outputs/fusion_holding_v1_validation/doc_checks.log`에 기록했다. HTTP URL3개와 브라우저 렌더링은 검사하지 않았다.

## 미검증 범위와 후속 확인

16슬롯 관측 용량은16개 장애물의 임의 배치가 모두 기하학적으로 가능하다는 뜻이 아니다. 기본 실제 개수는 Holding/OSC의 최대5+5와 ObjectRandom의7+7을 유지하며, 더 조밀한 배치는 기존 비겹침·접근 공간 제약에서 후보 재시도 한도에 도달할 수 있다.

장시간 PPO 수렴·성공률·접촉 성능,2048/256환경 처리량, 다중 seed와 실물 성능은 이번 설정 변경만으로 입증되지 않는다. 짧은 CPU/GPU 검증의 결과와 이 범위를 구분한다.

상세 계약: [Holding v1](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V1_ENVIRONMENT.md) · [OSC v1](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_V1_ENVIRONMENT.md) · [ObjectRandom v1](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V1_ENVIRONMENT.md) · [현행 OSC v0](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_V0_ENVIRONMENT.md).
