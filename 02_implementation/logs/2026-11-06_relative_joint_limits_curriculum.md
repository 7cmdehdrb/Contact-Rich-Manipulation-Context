# Relative 공통 조인트 한계와 속도 종료 커리큘럼

2026-11-06. 대상은 Relative-v0 및 직접 파생 v1/v2다. 새 환경을 만들지 않고 공통 부모에 적용했다. [v0 계약](../environments/WRENCH_REFACTOR_RELATIVE_V0_ENVIRONMENT.md) · [v1 계약](../environments/WRENCH_REFACTOR_RELATIVE_V1_ENVIRONMENT.md) · [v2 계약](../environments/WRENCH_REFACTOR_RELATIVE_V2_ENVIRONMENT.md).

## 사용자 요청과 최종 해석

1. Arm6관절의 물리 속도 한계를 모두3.14rad/s로 설정한다.
2. shoulder_pan, shoulder_lift, elbow, wrist1, wrist2, wrist3 순서 effort를150/150/150/28/28/28Nm로 명시한다.
3. 관절 속도 종료 임계값은4.0rad/s에서2.0까지 감소시킨다. 사용자 확인으로10,000iteration까지 유지하고 첫 감소는10,250, 이후250iteration마다0.05rad/s,20,000부터2.0으로 정했다.
4. 진단 변경을 롤백한다. 단, 사용자가 후속으로 **Axia 질량 유지**를 명시했으므로 기존에280g을 적용한 Relative-v1은0.280kg을 유지한다. v0/v2에는 새로운 질량 변경을 확대하지 않는다.

작업 중 최초 롤백에 질량을 포함했다가 사용자 정정 이후 v1의280g을 복원했다. 최종 상태와 최종 물리 검증은280g이다. 최초1g 조합 검증 산출물은 중간 결과로만 보존한다.

## 구현과 전체 대조

| 범위 | 변경 전 | 최종 |
| --- | --- | --- |
| Relative Arm 물리 속도 | 2/2/2/4/4/4rad/s | 3.14×6rad/s |
| Relative Arm effort | 150/150/150/28/28/28Nm | 같은 값을 Relative에서 명시 |
| 속도 종료 | 고정3.0rad/s | 4.0→2.0rad/s 계단형 일정 |
| 목표 방향 curriculum | 10,000부터3,000마다5도 감소 | 그대로 |
| v1 Axia 질량 | 0.280kg | 유지 |
| v0/v2 Axia 질량 | 0.001kg | 그대로 |
| v1 종료 print | 활성 | 제거 |
| 관측 차이 | v1 Base 장애물, v2 Actor현재/Critic초기 | 그대로 |
| Scene 구성·스폰·reset·목표 생성·reward·OSC·Hand·PPO·runtime | 기존 | 그대로 |

`WrenchRefactorRelativeEnvCfg`에서 arm actuator 한계 및 초기 termination threshold를 설정하고 `WrenchRefactorRelativeCurriculumCfg`를 사용한다. 기존 Refactor 본체/v3_1의 한계·종료·curriculum은 변경하지 않는다. 새 curriculum은 기존 목표 방향 term을 상속하며 추가 term은 `arm_joint_velocity_threshold` 하나다. 실행 함수는 역할에 맞게 `mdp/curriculum_functions/wrench_refactor.py`에 두었다.

절대 `learning_iteration`에서 `max(2.0, 4.0−0.05×max(0,(iteration−10000)//250))`을 재계산한다. float 경계는 소수10자리로 정리한다. 기존 `set_learning_iteration`→CurriculumManager 경로에서 TerminationManager의 `arm_joint_velocity.params.threshold`를 갱신하므로 resume·rewind·반복 reset에 누적 감소가 없다. env_ids의 일부만 reset되어도 공통 threshold 일정은 동일하다. 종료 판정은 엄격한 `abs(qdot)>threshold`다. threshold와 정확히 같으면 종료하지 않는다. 물리 한계3.14는 curriculum과 별개로 고정이다.

진단 print 옵션을 공유 `termination_functions/sweep.py`에서 제거하여 원래 함수 정의로 복원했다. 해당 print 전용 테스트도 제거했다. 시험용 회전액션0·충돌제거·termination제거는 production에 적용된 적이 없으며 활성 환경에는 없다. 과거 `outputs/` 진단 기록은 재현 근거로 보존하고 학습 로그를 삭제하지 않았다.

## 검증

CPU 검사87개 통과:

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q src/inspire_sweep_baseline/tests/test_task_contract.py src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench_refactor_relative.py src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py
```

검사는 일정 경계0/9999/10000/10249/10250/10499/10500/14250/14500/19750/19999/20000/90000 및0으로 되감기, 부분 env_ids와 반복 호출, 실제 arm_velocity 함수의 정확한 경계와 제외된 finger를 포함한다. 전체 설정 비교로 부모 Refactor 보존, v1의 Base 장애물+280g 외 차이 없음, v2의 관측 외 차이 없음을 확인했다. F/T 보정 코드는 변경하지 않았으며 기존 CPU 보정 회귀도 통과했다.

최종 실제 검증은 Relative-v1,2env,CUDA,seed42다. 실제 생성된 PhysX velocity/effort 한계와 housing mass, TerminationManager의 curriculum 경계값, print 옵션 제거를 assert했다. v0/v1/v2 실제 config dictionary도 비교했다. 기존 probe의5개 iteration 상태에서 reset과 각36step, 총180policy step을 수행하고 물체 바닥 정렬·주차 물체 drift·부분reset·고정 물성·관측 차원·EEF OSC도 검사했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python -u src/inspire_sweep_baseline/tests/_wrench_refactor_relative_probe.py --version 1 --num_envs 2 --headless --device cuda:0 --output outputs/relative_joint_limits_validation/axia280
```

최종 산출물은 workspace `outputs/relative_joint_limits_validation/axia280/probe_2.json`, `probe.log`다. 변경 Markdown 수식·링크 및 양쪽 저장소 diff 공백을 검사했다. 패키지 README의 기존 GoalAccuracy v0_2 문서 누락 링크는 범위 밖이므로 유지한다. Markdown 렌더링·대규모환경·장기학습·정책 성능 개선은 검증하지 않았다. 기존 학습 프로세스·checkpoint·logs/rsl_rl은 건드리지 않았다.
