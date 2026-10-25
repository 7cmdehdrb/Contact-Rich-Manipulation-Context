# Holding v4 · OSC v4 · ObjectRandom v3 구현·검증

[환경 계약·명령](../environments/FUSION_HOLDING_V4_FAMILY.md) · [로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

## 요청·기준 상태

사용자가 ObjectRandom-v2 재생에서 `distance_xy=0.011389m`, `required<=0.009750m`, valid=True·failures=none·eligible=False 출력을 제공했다. 이에 새 계열에서 success 종료와 holding 누적 지급 상한을 제거하고 목표 중심 보상·goal 연동 reaching을 요청했다. 이 출력은 당시 반경 밖인 상태를 보여주며 정책 전체의 실패 원인이나 새 학습의 성능을 증명하지 않는다.

Workspace 기준 commit은 `b6910a6c1b480eafcace5cead5695b2dcd657869`, 문서 submodule은 `de5760b6f894294ecd0a9f230a828144dc51b37a`다. 시작 시 기존 IsaacLab untracked 상태, 직전 임시 print의 코드2파일 및 문서 변경이 있었다. 이를 보존하면서 사용자 요청에 따라 해당 print만 주석 처리했다. 학습 로그는 이동·삭제하지 않았다.

## 구현

`FusionHoldingV3EnvCfg` → `FusionHoldingV4EnvCfg` → `FusionHoldingOSCV4EnvCfg` → `FusionHoldingOSCObjectRandomV3EnvCfg`. 세 task와 독립 PPO experiment를 기존 역할별 파일과 패키지 등록에 추가했다. 전체 ID·runtime·runner·입출력·action·scene 계약은 [환경 계약](../environments/FUSION_HOLDING_V4_FAMILY.md)에 정리했다.

- v4 success term은 None이다. 기존 실패와 timeout은 유지한다.
- goal hold는 `goal_settling_centered`: 지급 시간 상한 없이, d<r에서 기존 rate에 `1+(1-d/r)^2`를 곱한다. 최초 구현은 d<=r에서 지급했고, 아래 후속 요청으로 d<=2r까지 확장했다. weight4·기존 radius/speed curriculum을 유지한다.
- reaching은 `ReachingOrGoal`: valid·live goal 반경 조건이 ON이면 인정 반경을0.10→1.0m로 변경한다. 목표 점유를 매 step 재평가하며 새 최단 gap 기록만 지급하고 부분 reset을 계승한다. 목표 진입은 남은 gap 보상을 한 번 지급할 수 있으며 재진입은 같은 기록을 재지급하지 않는다.
- OSC는 기존 `configure_reach_osc`, ObjectRandom은 기존 scene/events/curriculum을 그대로 재사용한다. 비교 검사에서 의도한 reward·termination 차이 이외의 설정 동등성을 확인했다.
- 직전 `[DEBUG-HOLDING-SUCCESS]` print 블록과 ObjectRandom-v2 활성화 줄을 주석 처리했다. 이전 환경의 보상·success 동작 자체는 유지한다.

## 실행한 검사

모든 명령의 작업 디렉터리는 workspace 루트다. Python은 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`, Windows Isaac Sim5.1·D3D12·RTX4070 환경이다.

CPU 최초 검사:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_fusion_holding_v4.py src/inspire_sweep_baseline/tests/test_fusion_holding_v2.py src/inspire_sweep_baseline/tests/test_fusion_holding_v3.py src/inspire_sweep_baseline/tests/test_dex_rewards.py
```

**48 passed in 5.85s**. radius0.02/0.01/0.005에서 중심·경계·외부, 3초 초과 지급, XYZ 속도·유효성, 기본 reaching과의 동등성, goal 전환·재진입·부분 reset·live 반경 변경·접촉 goal 조건 일치와 잘못된 반경 거부를 검사했다.

Holding 전체 및 Dex 보상으로 확대한 첫 검사는69 passed·2 setup errors였다. 기존 `test_fusion_holding_v1`의 tmp_path fixture에서 시스템 Temp의 `pytest-of-3cmde` 디렉터리 접근이 WinError5로 거부되었다. 기존 Temp를 변경하지 않고 새 workspace 출력 디렉터리를 지정해 재실행했다.

```powershell
$taskTestTemp = Join-Path (Get-Location).Path ('outputs/pytest_holding_v4_' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $taskTestTemp) { throw 'Expected a new test directory' }
$holdingTests = (Get-ChildItem src/inspire_sweep_baseline/tests/test_fusion_holding*.py).FullName
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider --basetemp $taskTestTemp $holdingTests src/inspire_sweep_baseline/tests/test_dex_rewards.py
```

재실행 결과: **71 passed, 1 warning in 9.68s**. warning은 기존 ONNX export의 deprecation 안내다.

실제 launcher 검사:

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B src/inspire_sweep_baseline/tests/_fusion_holding_v4_probe.py --headless --device cuda:0
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B src/inspire_sweep_baseline/tests/_fusion_holding_v4_probe.py --headless --device cuda:0 --smoke Holding-OSC-ObjectRandom-v3
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B src/inspire_sweep_baseline/tests/_fusion_holding_v4_probe.py --headless --device cuda:0 --smoke Holding-v4
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B src/inspire_sweep_baseline/tests/_fusion_holding_v4_probe.py --headless --device cuda:0 --smoke Holding-OSC-v4
```

4개 명령 모두 exit0이었다. registry를 통해 세 환경과 PPO를 실제 import·생성하고, 직접 상속·독립 experiment·16슬롯 encoder·네 운동 페널티·이전 설정과의 동등성을 assert했다. 각 환경은 seed42·2개 병렬 환경에서 reset·10 step을 실행하여 관측·보상의 유한성과 success가 active terms에 없는 것을 확인했다. env=0의 episode length를 만료 직전으로 설정하고 다음 step에서 truncated=True가 되는 것도 assert했다.

증거는 workspace `outputs/fusion_holding_v4_validation/config.json`과 각 `Holding-v4.json`·`Holding-OSC-v4.json`·`Holding-OSC-ObjectRandom-v3.json`에 저장했다. stdout은 `outputs/fusion_holding_v4_config_probe.log`, `outputs/fusion_holding_v4_random_smoke.log`, `outputs/fusion_holding_v4_joint_smoke.log`, `outputs/fusion_holding_v4_osc_smoke.log`에 저장했다. 시작 시 기존 MaterialX·deprecated dynamic control·Fabric point-instancer 경고가 있었지만 검사는 통과했다.

## 같은 날 후속: 지급 범위를 2r로 확장

사용자가 v4 holding의 지급 조건을 유효한 물체이고 d<=2r로 변경하도록 명시했다. `goal_settling_centered`에서 기본 감쇠식의 거리 스케일 r는 그대로 두고 최종 지급 범위만2r로 넓혔다. d<r의 중심 강화, weight4, 속도 감쇠·커리큘럼·시간 상한 없음은 동일하다. r<d<=2r에서는 기본 감쇠 보상만 지급한다. d=2r,v=0의 raw rate는0.0625, 가중치 적용 후 초당0.25다. d>2r 또는 무효 상태는0이다. v2/v3와 Contact·Reaching의 goal 반경은 변경하지 않았다. 세 새 환경은 같은 보상을 상속한다.

다음 명령을 실행하여 **36 passed in 5.04s**를 확인했다. radius0.02/0.01/0.005에서 r 안쪽·2r 경계 포함·2r 초과·속도 감쇠·무효 상태·시간 상한 없음·기존 v2/v3 반경 유지·기존 Contact/Reaching 동작을 검사했다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_fusion_holding_v4.py src/inspire_sweep_baseline/tests/test_fusion_holding_v2.py src/inspire_sweep_baseline/tests/test_fusion_holding_v3.py
```

후속 변경 이후 실제 simulator·장기 학습은 재실행하지 않았다. 앞 절의 simulator 결과는 최초 지급 범위 구현에서의 기록이다.

## 미검증

문서 검사도 수행했다. 변경·신규 문서와 패키지 README 등11파일에 `check_markdown_math.py`를 실행해 통과했고, 같은 파일들에 `check_document_links.py --root example/Contact-Rich-Manipulation-Context --check-external`을 실행하여 errors0·internal452·external72를 확인했다. 루트와 문서 submodule의 `git diff --check`도 통과했다. HTTP 원문 검사는 이 링크 검사에 포함되지 않는다.

장기 학습, 이번 새 환경에서의 기존 checkpoint 재생, timeout100% 달성, 실물 성능은 미검증이다. 강제 timeout 검사는 종료 경로의 연결을 보여주며 정책이 자연스럽게 timeout까지 유지할 수 있음을 보여주지 않는다. 후기 ObjectRandom 최대 개수의 반복 reset도 이번에 다시 실행하지 않았다. 기존 랜덤화의 동등성과 초기 reset을 검증한 범위다.
