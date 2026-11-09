# Relative-IK-v0_2-Test 독립 구현·검증

## 요청·확정·기준

사용자는 IK-v0_1의 환경/대칭 관측과 Holding OSC v2의 보상/페널티를 결합한 독립 환경을 요청했다. 후속 질문으로 목표 반경3cm, IK-v0_1 실패 종료/팔 종료 일정 유지, 독립 설정/runtime + 공통 계산 함수 재사용을 확정했다. 성공 종료는 제거한다.

기준 workspace commit은 `6569d69d941670d9d3f3913a9a1608be2092003b`다. 시작 시 workspace에는 문서 submodule 포인터 변경만 있었으며 문서 저장소 자체의 작업트리는 깨끗했다. 해당 포인터·현재 커밋은 보존했고 commit/checkout/reset을 실행하지 않았다. 기존 IK/Holding 코드와 `logs/rsl_rl`을 수정하지 않았다.

[전체 환경 계약](../environments/WRENCH_REFACTOR_RELATIVE_IK_V0_2_TEST_ENVIRONMENT.md)

## 의도·변경 전후·영향

| 영역 | 기준 | 최종 |
| --- | --- | --- |
| 상속/구성 | IK-v0_1의 긴 task 상속 체인 | EnvCfg/runtime은 Isaac Lab 직접 상속; Scene/Manager/PPO 독립 선언 |
| Scene·센서·제어·IK·목표 | IK-v0_1 | 최종 설정 동일 |
| Actor/Critic 관측 | IK-v0_1 공통58D+64D | 동일; 별도 현재 GT 없음 |
| 보상·페널티 | Holding OSC v2 | 전체17term 보존; Hold radius0.03 및 선반 사건 연결만 조정 |
| 접촉/높이 | Holding 전체 손 OR 목표 점유 | 그대로; IK의 타겟 전용/EEF14cm gate를 넣지 않음 |
| 행동/손 속도 비용 | Holding raw Arm/Hand·전체 HAND_JOINT_NAMES | 그대로; IK의 Hand clamp·독립6축 비용을 넣지 않음 |
| 선반 사건 비용 | Holding shelf_collision 종료 flag | 같은 predicate 직접 평가; 변위만으로−3을 추가하지 않음 |
| 보상 커리큘럼 | Holding | 11개 유지; 반경 변화 제거 |
| 장애물/목표 방향 | IK-v0_1 | reset 개수0–3/0–3, 느린 방향 확대 유지 |
| 실패 종료·시간 | IK-v0_1 | 동일, 팔4→2 일정 유지 |
| 성공 종료 | IK-v0_1 연속3초 | 제거; 성공 보너스도 Holding 목록에 없으므로 없음 |
| PPO | IK-v0_1 | 실험명만 변경 |

신규 파일은 기존 역할 디렉토리의 `wrench_refactor_relative_ik_test` 이름으로 추가했다. 기존 파일 수정은 Gym 등록 추가와 패키지 README 링크뿐이다. 새 runtime은 IK reset·관측 clipping·IK 표시·metric/reset 동작을 독립 선언하며 다른 task 전용 진단 분기는 포함하지 않는다.

## 검증 결과

1. 변경 전 관련 CPU 검사98개 통과. 최초 명령은 존재하지 않는 `test_fusion_holding.py`를 지정해 수집 실패했으며 실제 `test_fusion_holding_v2.py`로 정정했다.
2. 신규 CPU 검사18개 통과. 첫 실행에서는 CPU fixture에 noise module 및 stateful reward instance 대역이 빠져11개 실패했다. 실제 runtime 오류가 아니었으며 fixture를 보완해 전부 통과했다.
3. 최종 관련 회귀 **139 passed, 1 warning, 12.31s**. 경고는 기존 ONNX export 테스트의 deprecation이다.
4. 실제 Isaac Sim에서 **전체 EnvCfg 사전 대조**: IK-v0_1 dict를 기준으로 승인된 rewards/terminations/curriculum 변경만 적용한 기대값과 전체 dict 일치. Scene/Action/Command/Event/Observation/sim/메타데이터는 동일하며 부모 재생성 결과도 동일. PPO 전체 dict는 실험명만 다름.
5. RTX3090·기본 원본 선반 자산·seed42·**32환경/120step** rollout 통과. iteration0→1250→6000→12000→25000→0으로 변경해 late penalty 활성화/rewind, 유한 보상·관측, F/T clip을 확인했다. rollout 실패 종료0회. 실패가 없었다는 결과는 무작위 행동 강건성 검증이 아니다.
6. 부분 reset은 선택된 환경의 센서 freshness를 무효화하고 비선택 물체 상태를 보존했다. 관측policy58D/obstacles64D와 행동8D를 실제 확인했다.
7. Holding 유효성: 실제 타겟 초기 root Z는1.04999995m이며 모든 타겟이 유효하다. 목표에 타겟을 정지시킨 fixture에서 Hold raw score>0.99,151회 반복 호출 후에도 지급을 확인했다. 이는 물리3초 유지 실험이 아니라 보상에 누적 시간 상한이 없다는 검사다. 성공 종료가 활성 목록에 없음을 별도로 확인했다.
8. **train.py 32환경·PPO2iteration** 통과. 체크포인트의 모든 tensor(optimizer 포함) 유한값과 model0→model1의 Actor/Critic obstacle encoder 갱신을 확인했다.

샌드박스 내부 `nvidia-smi`는 드라이버 접근에 실패했으나 승인된 샌드박스 밖 실행에서 RTX3090을 확인했다. GPU 부재로 해석하지 않았다.

## 재현 명령

workspace 루트, `/home/min/miniconda3/envs/env_isaaclab/bin/python`을 사용했다. CPU 검사는 ROS 경로/자동 pytest plugin을 제외했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v0.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v1.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v2.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_osc.py -q -p no:cacheprovider

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_wrench_refactor_relative_ik_test_probe.py \
  --headless --num-envs 32

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-Refactor-Relative-IK-v0_2-Test \
  --num_envs 32 --headless --max_iterations 2 \
  --resilient-attempt-dir outputs/relative_ik_v0_2_test_validation/train \
  --resilient-target-iterations 2
```

`train.py`의 기존 출력 경로 옵션만 이용해 `logs/rsl_rl` 대신 outputs에 저장했다. 사용 중단된 별도 train_resilient.py는 실행하지 않았다.

## 산출물·최종 대조·미검증

- `outputs/relative_ik_v0_2_test_validation/result.json`: 설정 대조, 활성 term, GPU rollout/reset 결과.
- `outputs/relative_ik_v0_2_test_validation/checkpoint_validation.json`: 유한값과 두 인코더 갱신.
- `outputs/relative_ik_v0_2_test_validation/train/`: params YAML, model_0.pt/model_1.pt, training_status.json.
- 실행 stdout: `/tmp/ik_v0_2_test_probe.log`, `/tmp/ik_v0_2_test_train.log`.
- 기존 소스 파일의 reward/control/scene 변경 없음. 등록13줄 추가와 README 안내만 기존 코드 저장소 파일에 반영했다.
- 신규 CPU 검사에서 전체 보상·관측·이벤트·실패 종료·커리큘럼을 대조하고, radius 바로 아래/경계/바깥,25k direction·20k termination cutoff·rewind·선반 변위만 발생한 경우를 확인했다.
- 미검증: 기본2048환경에서의 대규모 실행/collection 성능, 장기 학습 수렴/정지 정밀도, 실물 실행. 짧은 학습 체크포인트는 정책 성능을 입증하지 않는다.

문서 최종 검사: 변경 문서4개의 Markdown math 검사 통과, 내부 링크184개/외부 workspace 링크3개 오류0, 양쪽 저장소 `git diff --check` 통과. 신규 Python14개 AST 문법 검사 통과.

## 후속 요청: 팔 속도 초과 비용 제거·관절 제한 확인

사용자는 `arm_speed_excess` 삭제, `arm_joint_velocity` 실패 종료와 그 커리큘럼 및 UR5e effort/velocity를 IK-v0_1과 일치시키고, Hand 제한을 원본 URDF에 맞추도록 요청했다. 아래 내용이 앞선 최초 구현의17개 보상·11개 보상 일정 기록을 대체하는 현재 계약이다.

- 변경 전→후: `arm_speed_excess`(weight−1)와 연결된 `arm_free_speed` 일정을 제거했다. 활성 보상17→16개, 보상 관련 일정11→10개이며 전체 커리큘럼은12개다. 별도 속도 제곱 비용 `arm_joint_velocity`(weight−0.03)는 유지한다.
- 종료와 종료 일정은 이미 IK-v0_1과 같아 보존했다. 팔6축 중 절댓값 속도가 임계값을 넘으면 종료하며, 초기4rad/s,10,000까지 유지,10,250부터250iteration마다0.05 감소,20,000부터2rad/s다.
- UR5e 제한도 이미 IK-v0_1과 같아 보존했다. effort150/150/150/28/28/28Nm, velocity 전 관절3.14rad/s다.
- 손은 원본 URDF의12개 회전 관절 모두 effort10Nm·velocity1rad/s다. 사용자의 추정1.0/0.5와 다르므로 실제 URDF 값을 따른다. 기존 effort10과 공통 로봇 설정에서 받은 velocity1은 이미 일치했고, 새 환경에 velocity1을 명시하여 계약을 고정했다. 물리 제한값의 실효 변경은 없다.
- 원본은 `/tmp/inspire_urdf_right_with_force_sensor.zip` 내 `urdf_right_with_force_sensor/urdf/urdf_right_with_force_sensor.urdf`다. SHA256 `b7997a6087e8c0cded03aff557e07ca82b8793b2b5b3f95ec3566318a13f5f7f`가 패키지 `assets/data/wrench_right_hand/tactile_regions.json`의 `source_zip_sha256`과 같음을 확인했다. 다른 손 모델의 수치를 사용하지 않았다.
- 변경 범위: 신규 Test 환경의 rewards/curricula/EnvCfg, 기존에 추가한 CPU/GPU 검증 파일과 현재 환경 문서·인계 색인이다. 기존 IK/Holding 환경과 원본 URDF/USD는 수정하지 않았다.

검증: 신규 Test+Refactor CPU 검사 **104 passed, 8.86s**. GPU RTX3090에서 **4환경·120step** 실행 통과. 전체 EnvCfg 및 PPO 대조·부모 보존, 삭제된 reward/curriculum의 활성 목록 제외, 실제 PhysX `get_dof_max_forces`/`get_dof_max_velocities`의 팔/손 값 일치를 검사했다. iteration 변경·rewind·부분 reset·보상/관측 유한성도 통과했다. 결과는 `outputs/relative_ik_v0_2_test_validation/arm_limits/result.json`, stdout은 `/tmp/ik_v0_2_test_arm_limits_probe.log`다. Hold 반복 호출 검사의 범위는 앞선 기록과 같다.

GPU 재현은 위 probe 명령에서 `--num-envs 4 --output outputs/relative_ik_v0_2_test_validation/arm_limits`를 사용한다. 이번 후속 변경 후 PPO 학습은 다시 실행하지 않았으며, 장기 학습과 대규모 환경 성능은 미검증이다.
