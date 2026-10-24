# Three-view 녹화 대상 설정 — 2026-10-24

[개발 로그 목록](README.md) · [개발 지침](../../00_guidelines/09_DEVELOPMENT_GUIDE.md)

## 요청과 변경

사용자가 환경과 checkpoint를 쉽게 대입하도록 요청했다. 기준 workspace commit은 `e3fe8e3`이며, 작업 시작 시 상위 저장소에는 IsaacLab submodule의 untracked 상태 표시가 있었다. 기존 사용자 변경은 보존했다.

`src/inspire_sweep_baseline/scripts/record_three_views.py` 상단에 `DEFAULT_TASK`와 `DEFAULT_CHECKPOINT`를 추가했다. 기본 환경은 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v1`, checkpoint는 `logs/TEMP/2026-10-24_02-42-20/model_12000.pt`다. 기존 Fusion-v1_0만 허용하던 CLI 제한을 제거했고 `--task`와 `--checkpoint`로 기본값을 각각 덮어쓸 수 있다. 상대 경로는 실행 작업 디렉터리 기준이다.

Runner는 등록된 agent의 `class_name`에 따라 CurriculumOnPolicyRunner, OnPolicyRunner, DistillationRunner 중 선택한다. 환경의 상속·제어·보상·등록은 변경하지 않았다. 카메라 위치·시선·초점거리·투영 설정·선반 기준 top-down 정렬과 녹화 루프는 유지했다.

## 실행

Isaac Lab 실행 환경을 활성화한 뒤 workspace 루트의 PowerShell에서 실행한다. 기본 60초, 1280×720, 세 시점 MP4와 metadata 및 frame CSV를 `outputs/three_view_recordings/<timestamp>`에 저장한다. 해상도는 후속 CUDA 오류 진단과 사용자 허용에 따라1080p에서720p로 변경했다.

```powershell
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/record_three_views.py --headless
```

파일을 편집하지 않고 다른 대상을 선택하는 예:

```powershell
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/record_three_views.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2 --checkpoint "logs/TEMP/2026-10-24_02-43-09/model_8100.pt" --headless
```

## 검증과 한계

### Windows 렌더러 후속 수정

후속 CUDA 오류의 원본 Kit 로그(`kit_20261024_160029.log`)는 D3D12 선택 후 세 render product 초기화 직후 `computeArticulationData: CUDA error 719`로 시작하고 복사 오류가 연쇄 발생했다. 실제1920×1080 preview에서도 같은 실패를 재현했다(`outputs/three_view_repro_full.log`). 당시 `nvidia-smi` 관찰값은11667MiB였다. 해상도만1280×720으로 낮춘 preview는 exit0 및 세PNG 생성에 성공했다(`outputs/three_view_repro_720.log`, `outputs/three_view_recordings/20261024_160413`). GPU 메모리 부담과 연관된 실패로 좁혔으나 CUDA 내부 결함까지 확정한 것은 아니다.

별도 진단 wrapper(`outputs/diagnose_three_view_memory.py`)에서 학습용 aggregate-pair 버퍼 하나만2**28→2**20으로 줄이면1080p preview도 exit0이었다. 사용자가720p를 허용해 `DEFAULT_WIDTH=1280`, `DEFAULT_HEIGHT=720`을 적용했지만, 버퍼를 그대로 둔720p10초 녹화 재시도에서도 초기화 중CUDA719가 발생했다(`outputs/three_view_record_720_10s.log`). 따라서720p만으로 해결됐다고 결론내리지 않는다.

최종 수정은 녹화 실행의 `num_envs=1` 설정에서만 `gpu_found_lost_aggregate_pairs_capacity`를 `min(기존값, 2**20)`으로 제한하고 metadata에 기록한다. 학습 EnvCfg 원본은 변경하지 않는다. 카메라 pose·초점거리·제어·보상·checkpoint는 유지했다. 최초 sandbox 시도는 Kit/OptiX 캐시 쓰기 제한이 있어 중단했고, 실제 비교는 캐시 쓰기가 가능한 실행에서 수행했다. 중단은 이번 진단이 시작한 프로세스에만 적용했다.

재현·비교 명령은 아래와 같다. 모든 실행은 workspace 루트에서 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -u -B`를 사용했다.

```powershell
# 수정 전1080p preview: CUDA719 재현
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -u -B src/inspire_sweep_baseline/scripts/record_three_views.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2 --checkpoint logs/TEMP/2026-10-24_02-46-06/model_13300.pt --seconds 0.04 --headless --preview-only
# 해상도만 변경한 preview: exit0, 실제 영상 재시도는 실패
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -u -B src/inspire_sweep_baseline/scripts/record_three_views.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2 --checkpoint logs/TEMP/2026-10-24_02-46-06/model_13300.pt --seconds 0.04 --headless --preview-only --width 1280 --height 720
# 최종720p + 녹화 전용 버퍼 제한 검증
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -u -B src/inspire_sweep_baseline/scripts/record_three_views.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2 --checkpoint logs/TEMP/2026-10-24_02-46-06/model_13300.pt --seconds 10 --headless
```

최종10초 실행은 exit0, `outputs/three_view_recordings/20261024_160716/metadata.json`의 `status=complete`, `frames=500`, 해상도1280×720을 확인했다. `outputs/three_view_record_720_buffer_10s.log`에100~500프레임 진행이 남아 있다. 녹화 중 GPU 사용량 관찰값은5166MiB였다. `python -B -`(env_isaaclab Python)에 imageio 검사 코드를 전달하여 세MP4 각각500프레임·50FPS·10초, 첫/마지막 프레임 decode와 비단색 이미지, CSV500행을 모두 확인했다. 로그의CUDA 오류는 없었다. 현재 checkpoint의10초 녹화 검증이며60초·다른 task의 장기 동작은 미검증이다. 위 초기 수정 당시의 미검증 기록과 구분한다.

동일 env_isaaclab Python으로 `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'` 설정 후 `-B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_renderer_compatibility.py`를 재실행해9개 통과(0.08초)를 확인했다. 기본720p·명시적1080p 옵션 파싱, 구문 검사, HEAD 대비 카메라 생성·pose·intrinsic·정렬 코드 동일성도 stdin AST 검사로 통과했다. Markdown 검사와 두 저장소의 `git diff --check`도 통과했다.

사용자가 제공한 로그에서 `rtx.scenedb.plugin.dll`과 Hydra engine 초기화 중 native crash를 확인했다. [기존 Windows Vulkan 진단](2026-10-24_windows_vulkan_startup.md)에 따라 `play.py`가 쓰는 `cli_args.apply_renderer_compatibility(args)`를 녹화 스크립트의 AppLauncher 생성 직전에 추가했다. Windows + Isaac Sim5.1에서 명시적 backend 지정이 없으면 `--/app/vulkan=false`를 추가한다. 기존 명시적 backend와 다른 플랫폼·버전의 처리는 공통 함수를 따른다.

`python -B -`로 실제 main 함수의 사전 초기화 문장을 AST 추출하여 실행하고 AppLauncher 경계에서 Kit 인자를 검사했다. 출력 폴더 생성·checkpoint 접근·실제 simulator 시작은 제외했다. 수정 전에는 빈 Kit 인자로 AssertionError, 수정 후에는 `--/app/vulkan=false`와 카메라 활성화를 확인하여 PASS였다. 이는 누락된 초기화 호출의 재현이며 native crash 자체의 재현은 아니다. 실제 GPU 녹화와 영상 생성은 미검증이다. 카메라 위치·초점거리·정렬은 변경하지 않았다.

기본 `python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_renderer_compatibility.py`는 pytest 미설치로 실패했다. `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'` 설정 후 `& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_renderer_compatibility.py`로 재실행하여9개 통과(0.05초)를 확인했다.

후속 요청으로 파일 상단에 `DEFAULT_SECONDS = 60.0`을 추가했다. `--seconds`는 이 기본값을 덮어쓰며 기존 양수·유한값·제어 주기 배수 검증을 유지한다. 카메라 설정은 변경하지 않았다. `python -B -`로 AST 기반 compile 및 기본60초, CLI120초·2.5초 파싱을 검사하여 PASS를 확인했고 `git diff --check`도 통과했다. 실제 녹화는 실행하지 않았다.

- `python -B -`: stdin으로 AST 기반 검사를 실행했다. Python compile, 기본 CLI 파싱·checkpoint 파일 존재, OSC-v2로 CLI 덮어쓰기·파일 존재, HEAD 대비 카메라 생성·정렬 소스 동일성 모두 PASS.
- `git diff --check`: 통과. Windows checkout의 LF→CRLF 변환 안내만 출력했다.
- `python -B example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_markdown_math.py example/Contact-Rich-Manipulation-Context/02_implementation/logs/2026-10-24_three_view_recording_config.md example/Contact-Rich-Manipulation-Context/02_implementation/logs/README.md`: 2개 문서 통과.
- `git -C example/Contact-Rich-Manipulation-Context diff --check`: 통과.
- Isaac Sim 실행, 모델 로드, 영상 인코딩 및 다른 runner의 실제 동작은 미검증이다. 이 변경은 새 학습이나 정책 성능을 입증하지 않는다. 학습 로그와 checkpoint는 수정하지 않았다.
