# Finger-v0-Wrench 센서 프레임 Wrench OSC

현재 계약: 후속 사용자 요청으로 팔 속도 종료를1.0rad/s로 고정했다. 이후 센서/손 실행 입력 Clip과 tanh 없는 Clip된 Last Action을 적용했다([최신 클리핑 계약](2026-11-11_finger_wrench_action_clipping.md)). 최초 구현의 Clip 없음·Last Action tanh 보존 설명은 이 후속 변경으로 대체된다. 아래 최초 구현의4→2 일정 보존 설명은 마지막 후속 변경 절로 대체된다.

2026-11-11. [환경 계약·실행](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#finger-v0-wrench-센서-프레임-wrench-osc)

## 요청·기준·의도

사용자는 `Inspire-Sweep-Simple-Finger-v0`를 직접 상속하는 `Inspire-Sweep-Simple-Finger-v0-Wrench`를 요청했다. 참고 프로젝트의 OSC Wrench Control을 확인하여 센서 프레임 액션·Wrench OSC로 변경하며, 현재 환경의 프레임 이름을 사용한다. 변경 범위는 팔 제어기다.

작업 시작 workspace HEAD는 `65bb0a395c3b48338ddcef21ed5e27d48d46cf35`이고, 앞선 Gaussian·Raw 분리·5% 상한 제거·Finger-v0-Test 작업이 미커밋 상태다. 이를 보존했다. 참고 submodule HEAD는 `cdc4300c9210b8e5422bd07334afbf729f96c0bd`이다. 참고 소스는 `example/contact_rich_manipulation_task_learning/src/contact_manipulation_symmetric/contact_manipulation_symmetric/config/ur5e/ur5e_env_cfg.py`의 `SensorFrameWrenchAction`과 `UR5eContactManipulationEnvCfg`다. 참고 저장소와 학습 로그를 변경하지 않았다.

## 구현·변경 전후

| 항목 | 부모 Finger-v0 | Finger-v0-Wrench |
| --- | --- | --- |
| EnvCfg | `SweepSimpleFingerEnvCfg` | 이를 직접 상속하는 `SweepSimpleFingerWrenchEnvCfg` |
| runtime | `SweepSimpleFingerEnv` | 동일 runtime 재사용 |
| Action Cfg | `SweepSimpleFingerActionsCfg` | 이를 직접 상속하는 `SweepSimpleFingerWrenchActionsCfg` |
| 팔 Action term | `WrenchRefactorOSCAction` | `SensorFrameWrenchOSCAction` |
| OSC 목표 | EEF `pose_rel`6축 | 센서 `wrench_abs`6축 |
| 제어 원점·축 | AXIA80에서 이동·회전한 EEF | `Robot/axia80_link` 원점·축, offset 없음 |
| 명령 scale | 위치0.03m, RPY0.15rad | 힘10N/모멘트1N·m |
| motion / wrench 축 | 6 / 0 | 0 / 6 |
| 관성 분리 | True | False |
| 중력 보상 / nullspace | True / none | 동일 |
| 힘 feedback gain | 없음 | None, open-loop wrench |
| PPO 설정 | `SweepSimpleFingerPPORunnerCfg` | 직접 파생, 실험명만 `inspire_sweep_simple_finger_v0_wrench` |

기존 역할별 파일 안에 설정과 Action subclass를 추가했다. Gym 등록은 동일 Finger runtime에 새 EnvCfg/runner를 연결한다. 부모 EnvCfg가 후처리에서 EEF offset을 설정하므로, 새 EnvCfg의 `super().__post_init__()` 이후 팔 제어 body를 `axia80_link`, offset을None으로 다시 지정한다. Scene의 EEF frame은 수정하지 않는다.

팔 입력 순서는 `[Fx,Fy,Fz,Mx,My,Mz]`이며 scale을 곱한 값의 단위가 N/N·m다. 참고 구현과 같은 scale을 채택하되, 센서 범위 기반 입력 Clip은 가져오지 않았다. Finger-v0의 Raw Action·Last Action tanh·action-rate 경로를 유지하기 위함이다. 손6축·URDF 목표 제한도 부모 그대로다. 미사용 pose scale 필드는 부모 값을 유지하지만 `wrench_abs` 연산에는 사용되지 않는다.

## 프레임과 모멘트 기준점

현재 Isaac Lab native OSC는 task frame wrench를 root 축으로 변환하면서 센서 위치에 따른 모멘트를 더한다. 반면 articulation geometric Jacobian은 COM 기준이므로 단순 설정 교체만으로는 위치에 따라 불필요한 모멘트가 발생한다. 참고 구현처럼 preprocess에서 기준점을 보정한다.

센서→root 회전을 R, root에서 본 센서 위치를 p, 센서 축으로 표현한 센서→COM 위치를 c라 하면, native 변환 전에 센서 모멘트에서 `(Rᵀp+c)×F`를 뺀다. native 변환 후 최종 wrench는 `F_root=RF`, `M_COM=RM−(Rc)×(RF)`가 된다. 센서 원점의 wrench를 COM Jacobian에 일관되게 적용하는 좌표 변환이다. c는 생성 시 articulation의 `body_com_pos_b`에서 캐시한다.

센서 자세는 policy step의 native `process_actions`에서 갱신한다. root 축 명령은 다음 policy step까지 유지하며, 각 physics step에서 갱신된 Jacobian과 중력으로 effort를 계산한다. 물리 주기0.01초·decimation2·policy 주기0.02초는 그대로다.

기존 `UR10OperationalSpaceControllerAction`을 기반으로 비유한 effort 방어·실제 관절 effort 한계 포화·reset을 유지한다. 측정 F/T 오차를 피드백하는 폐루프 force controller를 추가한 것은 아니다. 참고 구현처럼 `contact_wrench_stiffness_task=None`인 native wrench OSC다.

## 보존 범위·최종 대조

- 부모 Finger-v0 및 기존 자식의 설정과 함수는 변경하지 않았다. 새 자식은 Finger-v0-Test를 상속하지 않는다.
- Scene·자산·물성·초기화·Fast reset·목표 분포·모든 관측·손 제어·모든 보상·종료·커리큘럼을 부모와 대조했다. 새 구성의 차이는 팔 Action뿐이다. PPO는 별도 로그 실험명만 추가한다.
- 관측66+64D·액션12D·Gaussian 초기화·Last Action tanh를 유지한다. 팔 속도 비용−0.03과 초기4rad/s→최저2rad/s 종료 일정도 유지한다.
- 기존 `wrist_wrench` 관측은 `PureWristWrench`가 반환하는 EEF 원점·축 기준 보상된 wrench다. 새 센서 기준 액션과 프레임이 다르지만, 관측을 변경하라는 요청은 없으므로 그대로 유지한다. 기존 Reach/높이 판정·reset IK의 EEF 기준도 보존한다.
- Raw 명령6축의 의미·scale이 pose에서 wrench로 바뀌므로 같은 action-rate 계수라도 실제 물리적 효과는 다르다. 보상 계수를 임의 재조정하지 않았다. 기존 pose checkpoint를 이 ID로 play하면 동일한 제어 실험이 아니다.

## 검증

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

**67 passed in10.90s**.

실제 configclass의 Action 설정·손 설정 보존·PPO 전체 설정 및 EnvCfg 전체 구성과 순서를 확인했다. EnvCfg fixture의 Action leaf는 대역이며, 별도로 실제 Action Cfg를 실행하여 모드·프레임·scale·hand·effort 설정을 검증했다. Gym ID 연결과 직접 부모, 부모 인스턴스·새 부모 인스턴스 불변성도 확인했다.

체크인된 Isaac Lab의 실제 `process_actions`·preprocess·OSC controller를 CPU에서 실행했다. 두 센서 위치·두 회전·비영 COM offset으로 축 회전과 모멘트 원점 보정, raw 샘플 보존을 검증했다. 실제 OSC `Jᵀ wrench + gravity` 및 기존 effort 제출 경로를 실행하여 목표 토크, saturation, zero command의 이전 명령 제거, 비유한 effort 방어를 확인했다. articulation 상태와 센서 pose는 CPU 대역이며 PhysX가 생성한 Jacobian 자체의 정확성을 새로 입증한 것은 아니다.

`nvidia-smi`가 드라이버와 통신하지 못하므로 GPU/PhysX 환경 초기화·센서 frame 생성·play·실제 학습은 미검증이다. 비교 학습에서 성공률·힘 추종·속도·안정성이 개선된다는 주장은 하지 않는다.

## 후속 변경: 팔 속도 종료1.0rad/s 고정

2026-11-11 사용자 명시 요청으로 기존 Wrench ID에 직접 적용했다. 초기4rad/s·최저2rad/s 커리큘럼 대신 처음부터1.0rad/s를 사용하고, `arm_joint_velocity_threshold` 커리큘럼을 비활성화한다. 종료 함수는 그대로여서 팔 관절 중 하나라도 절댓값 속도가1.0rad/s를 초과하면 실패 종료하며, 정확히1.0rad/s 및 손 관절은 이 판정으로 종료하지 않는다.

`SweepSimpleFingerWrenchEnvCfg`에서 기존 Test용 TerminationsCfg/CurriculumCfg를 재사용했다. 환경 자체의 직접 부모는 계속 Finger-v0이며 Test 상속으로 바꾸지 않았다. 제어기·관측·보상·나머지 종료와 커리큘럼·PPO·물리 제한은 변경하지 않았다. 부모 Finger-v0와 다른 자식도 보존했다.

전체 EnvCfg 대조 검사를 갱신하여 허용 차이가 팔 Action·종료 임계값·해당 커리큘럼뿐임을 확인한다. 검증 명령은 앞 절과 같은 환경에서 `test_sweep_simple_finger_wrench.py`와 `test_sweep_simple_finger.py`를 실행한다. **9 passed in3.50s**. 부모 불변성·전체 구성 차이와 기존1.0rad/s 경계 검사, Wrench 제어 회귀를 통과했다. GPU/PhysX·실제 학습은 이번 수정에서도 실행하지 않았다.
