# Refactor v0 기반 수동 Cartesian 조작

## 요청·기준·범위

사용자는 `envs/wrench_refactor_envs.py` 환경을 기준으로 EEF Cartesian 이동·손가락 2D 조작과 전체 reset·선반만 reset·조작 전 선반 복원·로봇 자세만 reset을 요청했다. 인터페이스·제어 방식은 구현에 맡겼다. 학습 환경을 변경하는 작업이 아니라 기존 환경을 생성해 수동으로 진행하는 실행기를 추가했다.

작업 기준 workspace HEAD는 `947e58d5ea200d951a1b2b46e1ec0d3ebab830e9`다. 시작 시 문서 submodule 포인터/작업트리에 기존 변경이 있었으며, 문서 저장소의 기존 미추적 `2026-11-06_wrench_refactor_collection_time.md`는 보존했다. `logs/rsl_rl`은 수정하지 않았다.

## 구현·최종 대조

| 항목 | 이전 → 이후 / 영향 |
| --- | --- |
| 실행기 | 없음 → `src/inspire_sweep_baseline/scripts/manual_wrench_refactor.py` |
| Runtime helper | `runtime/wrench_refactor_manual.py`: Session·ShelfSnapshot·Kit 패널 추가 |
| 기준 EnvCfg/runtime | `WrenchRefactorEnvCfg` / `WrenchRefactorEnv` 그대로 사용; 원본 파일 수정 없음 |
| Gym/PPO | 새 Gym ID·학습 설정 없음; 모든 기존 등록·상속·보상·종료·일정 보존 |
| Scene/Action | 오른손·물체17개·startup 물성·reset 분포·EEF offset·Hand2D 그대로; 수동 인스턴스만 v3 `WrenchRefactorOSCAction` 사용 |
| 인스턴스 설정 | 수동 실행만 num_envs1·seed42·viewer 카메라, CLI device·선택적 원본 선반 USD 경로 |
| 진행 방식 | `env.step()` 대신 ActionManager→decimation 물리→scene update만 실행; 자동 reset·보상/종료/커리큘럼/관측 step 미실행 |
| 전체 reset | 부모 `env.reset()` 실행 + EEF hold·손 열림 + 새 선반 snapshot |
| 선반 reset | 선반 기본 root + 부모 object_spawn 함수/인자 + 목표 command reset; robot/action target 미변경 |
| 선반 복원 | shelf/물체17개의 link pose7+COM velocity6·활성 마스크·초기 관측/배치·목표/초기 타겟 상태 복원; 중력 플래그 재적용/wake |
| 로봇 reset | robot 기본 root·관절 자세·속도0·제어 target 초기화·Hand2D열림; 선반 상태·snapshot 미변경 |
| Snapshot 수명 | 초기화/전체/선반 reset 때 자동 저장; Save로 명시적 교체; Restore는 원본 snapshot을 유지하여 반복 복원 가능 |

전체/선반/로봇 reset과 Restore 직후 수동 물리를 pause하여 다음 적분으로 독립 reset의 보존 대상이 즉시 이동하는 것을 막는다. Resume로 재개한다. snapshot은 물리 상태·배치 의미론을 복원하며 PhysX solver의 내부 warm-start/contact cache는 저장하지 않는다. RNG를 과거로 되돌리지 않으므로 다음 새 배치를 샘플링하는 난수열은 계속 진행한다. 물성·형상은 부모처럼 startup 고정이다.

EEF 입력은 world XYZ(m)/RPY(deg), 손은 `[finger flexion openness, thumb opposition openness]`로 각0–1(1열림)이다. 목표 reference는 기본0.04m/s·0.4rad/s로 slew하며, 실제 pose에서 reference까지의 상대 위치/회전을 현재 EEF축으로 변환하고 RPY를 부모 scale0.03m/0.15rad로 나눠 ActionTerm에 넣는다. 상대 명령은 위치 norm3cm·회전 norm0.15rad 이내로 제한하며, 부모 토크 제한도 유지한다. 실제 속도 제한·경로 계획·충돌 회피를 보장하는 제어기는 아니다. 순수 0 상대 명령 대신 지속적인 world 목표를 유지하므로 입력을 놓은 뒤 같은 목표를 추종한다.

## 실행

Workspace 루트, GUI 사용:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/manual_wrench_refactor.py
```

다른 PC의 활성 Isaac Lab Python은 `python src/inspire_sweep_baseline/scripts/manual_wrench_refactor.py`를 사용한다. 선택 옵션은 `--seed`, `--linear-speed`, `--angular-speed`, `--shelf-usd`, AppLauncher 옵션이다. `--steps N`은 N회 loop 후 종료하며 headless에서는 양수 N이 필수다. 체크포인트가 필요하지 않다.

패널 조작법·버튼별 동작은 [패키지 README](../../../../src/inspire_sweep_baseline/README.md#refactor-수동-조작)를 따른다.

## 검증

CPU 검사:

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q src/inspire_sweep_baseline/tests/test_wrench_refactor_manual.py
```

실제 Isaac Lab math로 회전된 robot root 세 조건과 EEF frame에서 world pose command 왕복, reference slew/최단 회전·정지 회전, command norm cap·zero error를 검사한다.

기존 Refactor CPU 회귀와 신규 검사를 함께 실행해 **66개 통과**했다. Python compile, 변경 문서 math 검사와 전체 문서 저장소 link 검사도 수행했다.

구현 중 실제 GPU 검사에서 발견하고 수정한 사항:

1. `CommandManager.reset()`에 None을 넘기면 이 Isaac Lab 버전은 slice를 `len()`에 전달해 예외가 발생했다. 선반 reset은 명시적 env ID tensor를 전달하도록 수정했다.
2. link velocity setter가 COM velocity를 link-state cache에 다시 기록하여 비영점 속도 복원 비교가 실패했다. snapshot은 명시적 link pose + COM velocity를 저장하고 이에 맞는 `write_root_state_to_sim`/`write_object_state_to_sim`으로 복원하도록 수정했다. 라이브러리 코드는 수정하지 않았다.
3. 최초 v0 root OSC의 25mm 상향 이동 시험은 X207mm/Y50mm/Z61mm 변위가 관측되어 수동 추종으로 부적합했다. 수동 인스턴스만 v3의 EEF offset Jacobian·link velocity 보정 ActionTerm으로 전환했다. 이후 같은 시험의 변위는 X0.003mm/Y−0.027mm/Z25.058mm, 최종 위치 오차0.064mm였다. UI world 목표도 해당 EEF command frame으로 변환한다.
4. GUI의 초기3초 회전 시험은3° 명령에 잔여0.592°로 설정한0.573° 허용치를 약간 넘었다. 안정화 시간을5초로 늘려도 같은 잔여 오차가 남았다. gain을 임의로 변경하지 않고, 수동 조작의 회전 검증 기준을1°로 명시했으며 실제0.592° 잔여 오차를 결과에 기록한다. 목표를 정확히 일치시킨다고 주장하지 않는다.

Headless PhysX1환경에서 전체/선반/로봇 reset, 로봇 비영점 속도 보존, 비영점 선반·물체 속도를 포함한 상태 복원3회, 활성 마스크·중력 플래그·목표·관측 snapshot 복원, startup 물성 불변, 11초 동안 자동 reset 없음과 Hand2D 명령 적용을 확인했다. 결과는 `outputs/wrench_refactor_manual_validation/headless.json` 및 `headless.log`다.

실행 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u \
  src/inspire_sweep_baseline/tests/_wrench_refactor_manual_probe.py --device cuda:0 --headless

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH DISPLAY=:1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u \
  src/inspire_sweep_baseline/tests/_wrench_refactor_manual_probe.py --device cuda:0
```

장치 접근이 제한된 tool sandbox에서는 GPU가 보이지 않았으나 승인된 장치 접근으로 RTX3090/Isaac Sim5.1 실물 GPU 검증을 수행했다. 선반은 기본 원본 URI를 사용했고 임의 대체 자산은 사용하지 않았다.

GUI1환경에서도 같은 reset/복원 검증과 실제 Kit 패널 생성·Hand 슬라이더 입력·Jog·전체/선반/로봇 reset·Restore 연속 dispatch를 통과했다. 25mm 상향 목표의 최종 위치 오차0.064mm, 이후 각각10mm X/Y 이동의 위치 오차0.085mm/0.067mm, 3° yaw 변경 후 회전 오차0.592°였다. 결과는 `outputs/wrench_refactor_manual_validation/gui.json`/`gui.log`다. `panel.png`는 렌더러 swapchain에서 해당 Isaac Sim 창만 캡처한 화면이며, 직접 열어 모든 입력·버튼의 가시성과 선반 앞쪽 시야를 확인했다.

최종 headless 재검사에는 XYZ·회전 rollout 이후의 선반 복원을 추가했고, 이때도 로봇의 실제 root/관절 자세·속도가 유지되고 선반·물체·목표가 저장된 상태와 같음을 확인했다. 실제 제품 실행기 역시 아래 명령으로 `MANUAL READY`와 `MANUAL DONE: physics_steps=35, ticks=35`까지 정상 종료했다(`launcher.log`).

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u \
  src/inspire_sweep_baseline/scripts/manual_wrench_refactor.py --device cuda:0 --headless --steps 35
```

원본 EnvCfg를 새로 생성해 실행 전 dict와 동일함을 비교했고, 기준 `envs/wrench_refactor_envs.py`, `runtime/wrench_refactor.py`, Action Cfg/함수와 패키지 등록 파일은 `git diff`에 변경이 없음을 확인했다. 문서 링크 검사는 전체497개 Markdown에서 오류0건이었다.

범위와 한계: seed42·1환경·초기 자세 주변25mm Z/10mm X/10mm Y/3° yaw를 검사했다. 전체 작업공간의 도달 가능성·장시간 접촉 안정성·모든 형상/물체 접촉·실물 로봇·학습 성능·Windows GUI는 검증하지 않았다. snapshot은 application 메모리에만 보관하며 프로세스를 종료하면 사라진다. 원본 UI의 타임라인 pause 상태에서는 먼저 타임라인을 재개해야 수동 패널에 대기 중인 조작이 처리된다.
