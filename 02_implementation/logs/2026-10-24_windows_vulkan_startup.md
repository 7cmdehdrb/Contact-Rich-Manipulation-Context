# Windows Vulkan 초기화 크래시 진단

[개발 로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

## 요청과 기준

2026-10-24, Windows에서 Holding OSC v2 checkpoint 재생이 환경 로드 전에 native crash로 종료되는 문제를 진단했다. Workspace 기준 commit은 `701701d`, 문서 기준 commit은 `cb3636e`다. 작업 시작 시 상위 저장소에는 IsaacLab의 미추적 파일 표시가 있었으며 보존했다. 문서 저장소는 clean이었다.

- task: `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2`
- 설정: `FusionHoldingOSCV2EnvCfg` → `FusionHoldingV2EnvCfg`, runner: `FusionHoldingOSCV2PPORunnerCfg`
- checkpoint: `logs/TEMP/2026-10-23_22-20-48/model_2100.pt`
- 실행 환경: `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`, Python3.11.15, Isaac Sim5.1.0.0, Isaac Lab0.54.4, torch2.7.0+cu128, RSL-RL5.0.1, RTX4070, driver621.01

## 원인과 판별 근거

원래 재생 명령은 `app ready` 직후 native crash로 종료됐다. Sweep 패키지·task·checkpoint 없이 `AppLauncher(headless=False)`만 호출해도 재현했다. 따라서 이번 시작 크래시는 리팩토링된 Sweep 환경 실행에 의존하지 않는다.

Windows Application 이벤트1000에는 `rtx.scenedb.plugin.dll`, exception `0xc0000005`, fault offset `0xe533b`가 반복 기록되어 있었다. Isaac Lab의 `apps/isaaclab.python.kit`는 `app.vulkan=true`를 명시한다. 최소 재현에서 다음을 비교했다.

| 실행 조건 | 실제 결과 |
| --- | --- |
| 기본 Vulkan | `app ready` 후 native crash, `STARTUP_OK` 도달 실패 |
| Vulkan + `--/rtx/scenedb/tlasBufferSize=2000000000` | 동일 crash, Python exit `-1073741819` |
| `--/app/vulkan=false` | `STARTUP_OK`, SimulationApp 종료, Python exit0 |

같은 설치에서 backend만 변경해 성공했다. Conda 환경 재설치를 요구하는 손상 근거는 발견하지 않았으며, 이번 원인은 Isaac Sim5.1의 Vulkan RTX 초기화 경로와 현재 드라이버 조합으로 좁혔다. 드라이버 교체나 DLL 내부 원인까지 검증한 것은 아니다. 사용자는 일반 Isaac Sim도 이미 `isaac-sim.bat --/app/vulkan=false`로 실행해야 켜졌다고 확인했다.

[NVIDIA IsaacSim 이슈517](https://github.com/isaac-sim/IsaacSim/issues/517)에도 동일 계열 SceneDB 시작 크래시와 Windows D3D12 우회가 기록되어 있다. 해당 이슈의595.x 사례와 이 PC의621.01을 동일한 내부 결함이라고 단정하지 않는다.

초기 sandbox 실행에서 Kit·OptiX 캐시 쓰기 PermissionError가 추가로 발생했다. 이는 진단 도구의 쓰기 제한으로, 사용자가 보고한 원인과 구분한다. 이후 실제 재생 검증은 캐시 쓰기가 가능한 실행으로 전환했다.

## 변경

`scripts/cli_args.py`의 `apply_renderer_compatibility()`를 `play.py`와 `train.py`의 AppLauncher 생성 직전에 호출한다. Windows + Isaac Sim5.1에 한해 `--/app/vulkan=false`를 기본 추가한다. 다른 Kit 옵션, 명시적 backend 선택, Linux, 다른 Sim 버전은 보존한다. Isaac Lab submodule과 Conda 설치 파일은 수정하지 않았다.

task 등록·상속·관측·행동·보상·종료와 checkpoint는 변경하지 않았다. 학습 로그 정리는 수행하지 않았다.

## 실행한 검증

Workspace 루트에서 다음 명령을 실행했다. CPU 테스트는9개 통과했으며 변경한 Python3파일의 AST 구문 검사도 통과했다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_renderer_compatibility.py
```

최소 재현 및 실행 로그는 workspace `outputs/startup_diagnosis/`에 남겼다. `minimal.py`, `tlas.py`, `d3d12.py`는 Sweep을 import하지 않는 진단 전용 파일이다. `validate_play.py`는 실제 수정된 `play.py` 소스를 실행하되 무한 재생 loop만128step으로 제한한다. 실제 실행 명령은 다음과 같다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -u outputs/startup_diagnosis/validate_play.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2 --num_envs 1 --checkpoint C:/python/Contact-Rich-Manipulation/logs/TEMP/2026-10-23_22-20-48/model_2100.pt
```

자동 D3D12 선택, SimulationApp 시작 완료, 리팩토링된 task 설정·agent 설정 로드, CUDA 환경 생성 진입까지 확인했다. 이후 기본 선반 주소 `omniverse://192.168.0.13/Library/Shelf/Arena/Collected_speedrack_shape/speedrack_shape.usd`의 `Discovery Failed` 재연결과 서버 응답 대기가 발생했다. 로컬 선반 경로에 대한 User/Machine 환경 변수도 비어 있었다. 사용자는 해당 서버 접근에 VPN이 필요하다고 알리고 VPN을 켰다.

VPN 연결 후 같은 실행이 계속 진행되어 장면 생성, 지정 checkpoint 로드, 정책 재생 loop와 SimulationApp 종료를 통과했고 Python exit0을 확인했다. Kit 로그의 Graphics API는 D3D12였다. 기본 선반 주소 사용 시 VPN 연결이 선행 조건이다. 장기 학습·다른 task 전체·Linux simulator 실행은 이번 검증 범위에 포함하지 않는다.

사용자 요청에 따라 VPN 연결 상태에서 같은 검증 명령을 재실행했다. `play_fixed_retry.log`에서 장면 생성4.11초, 지정 checkpoint 로드, 종료 직전 `PLAY_128_STEPS_OK`, 정상 종료 exit0을 확인했다. SimulationApp의 fast shutdown이 프로세스를 종료하므로 완료 표시는 `env.close()` 직전에 출력하도록 진단 harness에 배치했다. 기본 GUI 경로에서128step 완료를 확인했으며 video/camera 옵션은 사용하지 않았다.

문서 검증은 변경 Markdown4개 수식 검사, 문서 저장소 변경3개와 패키지 README의 링크 검사 오류0, 두 저장소 `git diff --check`를 통과했다. `train.py`는 같은 사전 초기화 함수를 호출하지만 실제 학습 실행은 이번에 수행하지 않았다.
