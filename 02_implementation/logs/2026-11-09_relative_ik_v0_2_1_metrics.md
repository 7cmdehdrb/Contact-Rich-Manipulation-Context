# Relative-IK-v0_2_1-Test와 부모 학습 Metrics

## 요청·기준·원인

2026-11-09 사용자는 v0_2-Test 직접 상속 환경 v0_2_1-Test를 요청했다. object 혼합 비용을 분리하고 EEF/타겟/팔 초과 속도 비용과 관련 커리큘럼을 제거한다. 별도로 부모 v0_2-Test에 목표 거리와 EEF/물체 속도 등 저비용 Metrics를 추가하고 장애물 개수 지표를 제거하도록 요청했다.

기준 commit은 `ed7572c95d57cb3871149e2fc17c78ead23978a5`다. 작업 시작 시 코드 저장소는 문서 submodule 포인터 외 변경이 없었다. 기존 커밋·포인터·사용자 작업과 `logs/rsl_rl`을 보존한다.

원인: 부모 runtime에 수집 함수와 버퍼는 있었지만 호출자는 성공 종료 함수였다. 성공 종료 제거로 수집이 실행되지 않아 reset에서 별도로 기록하던 장애물 개수/배치 완료 지표만 출력됐다. 새 timeout wrapper는 매 정책 step의 reset 전 상태에서 수집 후 원래 `time_out` 결과를 반환한다. 성공 종료나 실패 판정을 바꾸지 않는다.

[전체 환경 계약·Metrics 정의·학습 명령](../environments/WRENCH_REFACTOR_RELATIVE_IK_V0_2_TEST_ENVIRONMENT.md)

## 변경 전후와 최종 대조

| 범위 | 변경 |
| --- | --- |
| 부모 EnvCfg·Scene·관측·행동·reset·PPO | 그대로 |
| 부모 Reward/Curriculum | 그대로; 기존16개/12개 유지 |
| 부모 Termination | timeout callable에 계측 wrapper만 추가; 결과·time_out flag·10초 제한 동일 |
| 부모 runtime | 미호출 평균/force/moment 버퍼를8개 Metrics 집계로 교체; 장애물 개수/배치 완료 로그 제거 |
| 자식 EnvCfg | `WrenchRefactorRelativeIKV0_2_1TestEnvCfg`가 `WrenchRefactorRelativeIKV0_2TestEnvCfg` 직접 상속 |
| 자식 runtime | 부모 `WrenchRefactorRelativeIKV0_2TestEnv` 공유; Metrics 상속 |
| 자식 object | 기존−30×(tilt+5×displacement)를 object_tilt(−30), obstacle_displacement(−150)로 분리 |
| 자식 속도 비용 | eef_linear_speed/pushing_speed와 eef_free_speed/pushing_free_speed 삭제 |
| arm_speed_excess/arm_free_speed | 부모부터 이미 없으며 자식에서도 없음 |
| 자식 PPO | 부모 직접 상속, experiment_name만 변경 |

자식 Gym ID는 `Inspire-Wrench-Refactor-Relative-IK-v0_2_1-Test`, 실험명은 `inspire_wrench_refactor_relative_ik_v0_2_1-Test`다. 활성 Reward15개, Curriculum10개다. object 분리는 기존 계산 함수를 재사용하며 tilt의 활성 타겟 포함, 변위의 활성 비타겟만 포함,3D 제곱합 후 cap0.04,dt 적용을 보존한다. 상속상 새 term은 보상 목록 끝에 추가되지만 합산값은 부동소수점 오차 범위에서 동등하다. 나머지 보상·일정·종료·자산·관절 한계·관측·목표 분포는 그대로다. 새로운 클래스는 기존 계열의 역할별 파일에 추가했으며 timeout 계산 함수만 해당 역할 디렉토리에 새 파일로 추가했다.

Metrics는 매 정책 step GPU pose/velocity로 계산한다. 별도 센서·가속도 조회, 매step `.item()`/CPU 전송/동기화를 추가하지 않는다. 통계는 reset 전에 기록하며 선택 reset만 버퍼를 초기화한다. 평균/최대값은 에피소드 내 시간 평균/최대 후 reset 에피소드들 사이 평균이다. 목표 체류율은 XY 반경 조건만이고 성공률이 아니다. 물체 속도는 타겟 기준이다. 순간 physics substep 최대나 장애물 전체 속도는 측정하지 않는다. 추가 계측이 불필요한 센서 readback으로 커지지 않도록 기존 미호출 가속도·힘/모멘트 계측은 제거했다.

## 검증·성능

- CPU **107 passed, 9.64s**: 기존 Refactor 회귀, 전체 Manager 계약, 자식 변경 범위/부모 불변, 분리 전후 비용 합산, 경계/일정, 실제 runtime 함수의 시간 평균·peak·부분 reset·비유한 입력을 검사했다.
- 자식 GPU RTX3090 **256환경·120step** 정상 실행 및 별도 benchmark320step. 전체 EnvCfg를 부모에 요청 차이만 적용한 기대 사전과 대조했고 PPO는 실험명만 다름을 확인했다. 부모와 IK-v0_1의 기존 비교도 timeout 계측 차이 외 그대로 통과했다.
- GPU에서 실제 PhysX 팔/손 effort·velocity 제한, 활성 보상/일정/종료, 분리 비용 합산, 유한 관측/보상, iteration 변경/rewind, Metrics8개와 선택 reset 격리, 강제 timeout 판정 직전 거리 수집을 확인했다.
- **Metrics 비용:** 같은 자식 씬에서 활성/비활성을 교차한8블록×40step(각 상태4블록), 블록 경계에만 CUDA synchronize. 환경 step 평균시간의 블록 중앙값은 비활성63.059ms, 활성63.378ms, 차이+0.319ms/**+0.505%**였다. policy 추론·PPO 업데이트·logger 비용을 포함한 전체 Collection Time 측정은 아니다. 단일 실행이며 블록별 변동이 있어 통계적 유의성을 주장하지 않는다. 이 범위에서 과도한 비용 증가는 관찰하지 않아8개 Metrics를 유지했다.
- 자식 **train.py 32환경·2iteration** 통과. TensorBoard 이벤트에서8개 Metrics, 분리된 두 Episode_Reward 로그, 삭제 항의 부재, 모든 기록 scalar의 유한값을 확인했다. 실제 timeout 에피소드에서도 지표가 출력됐다.

## 재현 명령·산출물

workspace 루트에서 실행한다. Python은 `/home/min/miniconda3/envs/env_isaaclab/bin/python`이며 ROS 환경변수는 제외했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor.py -q -p no:cacheprovider

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_wrench_refactor_relative_ik_test_probe.py \
  --headless --num-envs 256 --child --benchmark \
  --output outputs/relative_ik_v0_2_1_test_validation

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-Refactor-Relative-IK-v0_2_1-Test \
  --num_envs 32 --headless --max_iterations 2 \
  --resilient-attempt-dir outputs/relative_ik_v0_2_1_test_validation/train \
  --resilient-target-iterations 2
```

산출물은 `outputs/relative_ik_v0_2_1_test_validation/result.json`, `training_log_validation.json`, `train/`이다. stdout은 `/tmp/ik_v0_2_1_probe.log`, `/tmp/ik_v0_2_1_train.log`에 보존했다. 장기 학습 수렴·정책 성능,2048환경 Collection 성능, 실물 실행은 미검증이다. 짧은 학습은 로그 연결 검증이며 성능 증거가 아니다.

추가 최종 대조: 부모 v0_2-Test도 별도 GPU4환경·120step 검증을 통과했다.16개 기존 보상·12개 일정·기존 종료 결과와8개 Metrics/부분 reset을 확인했다. 산출물은 `outputs/relative_ik_v0_2_1_test_validation/parent/result.json`, stdout은 `/tmp/ik_v0_2_metrics_probe.log`다. 재현은 위 probe 명령에서 `--child --benchmark`를 빼고 `--num-envs 4 --output outputs/relative_ik_v0_2_1_test_validation/parent`를 사용한다.

문서·정적 최종 검사: 변경 Python AST 검사 통과, 변경 문서4개 math 검사 통과, 내부 링크190개 오류0, 코드/문서 저장소 `git diff --check` 통과. 원본 IK-v0_1 및 Holding 구현은 변경하지 않았다.
