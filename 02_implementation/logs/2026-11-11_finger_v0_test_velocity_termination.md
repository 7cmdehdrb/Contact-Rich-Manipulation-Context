# Finger-v0-Test 고정 팔 속도 종료 실험

2026-11-11. [환경 안내](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#finger-v0-test-고정-팔-속도-종료-실험)

## 요청과 의도

사용자는 기존 Finger-v0에서 사실상 활용되지 않던 Joint Velocity Termination의 효과를 시험하기 위해, 직접 파생 환경 `Inspire-Sweep-Simple-Finger-v0-Test`를 요청했다. 임계값1.0rad/s를 고정하고 해당 커리큘럼을 사용하지 않는다.

## 변경 전후와 영향

| 항목 | 부모 Finger-v0 | 새 Finger-v0-Test |
| --- | --- | --- |
| 직접 EnvCfg 부모 | Simple-v1 | Finger-v0 |
| 팔 속도 실패 종료 | 초기4.0rad/s, 커리큘럼 최저2.0rad/s | 처음부터1.0rad/s 고정 |
| 임계값 커리큘럼 | 10000 iteration부터250마다0.05 감소 | `arm_joint_velocity_threshold=None` |
| PPO 실험명 | `inspire_sweep_simple_finger_v0` | `inspire_sweep_simple_finger_v0_test` |

기존 `arm_velocity` 함수를 그대로 사용한다. 선택된 팔 관절 중 하나라도 속도 절댓값이1.0rad/s를 **초과**하면 실패 종료한다. 정확히±1.0rad/s는 이 조건으로 종료하지 않으며, 손 관절은 판정에서 제외한다. 종료 조건은 물리 관절 속도 제한이나 제어기 출력 제한을 바꾸지 않는다.

역할별 기존 파일에 Test용 TerminationsCfg·CurriculumCfg·EnvCfg·PPORunnerCfg와 Gym ID를 추가했다. EnvCfg는 `SweepSimpleFingerEnvCfg`를 직접 상속하며, runtime도 부모 `SweepSimpleFingerEnv`를 재사용한다. PPO 설정은 부모에서 실험명만 바꾼다.

관측·액션·Last Action tanh·팔 속도 비용−0.03·다른 보상·Scene·reset·성공 판정·나머지 종료·다른 커리큘럼은 보존한다. 앞서 추가한 Finger-v1/v2·Semi-Prof·Raw 환경이나 Semi-Prof의5% 상한 제거에는 영향을 주지 않는다. 기존 학습 로그는 변경하지 않았다.

## 최종 대조와 검증

실제 configclass로 부모/자식 전체 구성과 순서를 대조하여, 종료 임계값과 해당 커리큘럼 외에는 동일함을 확인했다. 자식 설정 변경 후 기존 부모 인스턴스와 새 부모 인스턴스의 불변성도 검증했다. Gym 등록의 runtime·EnvCfg·PPO 연결, PPO 직접 상속 및 실험명 외 전체 동일성을 확인했다.

실제 종료 함수로±1.0 경계, 양/음 방향 초과, 제외된 손 관절의 큰 속도를 검사했다. Simple·Finger-v0/v1/v2·Semi-Prof 회귀 검사도 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_semi_prof.py \
  -q -p no:cacheprovider --tb=short
```

**65 passed in10.25s**. GPU/PhysX 환경 초기화·실제 play·학습 성능은 미검증이다. 고정 임계값에 따른 실패율이나 정책 속도 개선 효과는 후속 학습에서 확인해야 한다.
