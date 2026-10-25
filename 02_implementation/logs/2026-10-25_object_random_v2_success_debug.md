# ObjectRandom-v2 success 종료 임시 출력

[활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md) · [개발 로그 목록](README.md)

## 요청과 기준

사용자가 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v2`에서 성공으로 보이는 상황에도 종료가 반복해서 발생하지 않는다고 보고하여 임시 print 추가를 요청했다. 실제 원인은 아직 확정하지 않았다.

Workspace 기준 commit은 `b6910a6c1b480eafcace5cead5695b2dcd657869`다. 작업 전 루트 상태에는 기존 `IsaacLab` submodule의 untracked 상태가 있었고 문서 submodule은 clean이었다. 기존 사용자 변경과 학습 로그는 보존했다.

## 변경과 사용

상속은 Holding-v2 → Holding-v3 → Holding-OSC-v3 → Holding-OSC-ObjectRandom-v2이며 설정 클래스는 `FusionHoldingOSCObjectRandomV2EnvCfg`다. 등록과 실행 방법은 동일하다.

- `mdp/termination_functions/contact_sweep_clutter_fusion_holding.py`: `HoldingSuccess`와 `ScheduledHoldingSuccess`에 기본 False인 `debug_print` 인자를 추가했다. 기존 판정과 타이머 갱신 후 env=0을 매 호출 출력하며 `flush=True`를 사용한다.
- `envs/contact_sweep_clutter_fusion_holding_osc_object_random_envs.py`: ObjectRandom-v2의 success params에만 `debug_print=True`를 설정했다. 이 설정 줄 또는 `TEMP SUCCESS DEBUG` 출력 블록을 주석 처리하면 출력이 중단된다.

출력 prefix는 `[DEBUG-HOLDING-SUCCESS]`다. `distance_xy`는 월드 XY 목표 거리(m), `speed_xyz`는 실제 3차원 선속도 크기(m/s)이며 각각 `required<=`로 현재 임계값을 표시한다. 목표 반경은 기존대로 reward manager의 live 값을 사용한다. `valid`는 위치·속도·목표의 유한성 및 선반 내 위치·높이·기울기 검사를 합친 결과다. `failures`는 현재 활성 실패 term 이름이며, `eligible`은 유지 시간을 누적할 수 있는지 나타낸다. `hold`와 `steps`는 연속 유지 시간/step 및 요구값이고 조건 이탈 시 0으로 초기화된다. `success`는 실제 반환 판정이다.

저장소 루트의 Isaac Lab 환경에서 기존 checkpoint 재생 명령으로 출력된다.

```powershell
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/play.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v2 --num_envs 1 --checkpoint "logs/TEMP/2026-10-25_01-26-24/model_10500.pt" --real-time
```

이 임시 설정은 해당 환경의 train에도 적용된다. 여러 환경에서도 env=0만 출력하며 매 step CPU 동기화·출력 비용이 있다.

## 실행한 검증과 한계

기본 `python -B -c "import torch, pytest; print('torch', torch.__version__)"`는 torch 미설치로 실패했다. 설치된 `env_isaaclab` Python으로 다음 검사를 실행했다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_fusion_holding_v2.py src/inspire_sweep_baseline/tests/test_fusion_holding_v3.py
```

결과: **24 passed in 5.32s**.

추가로 PowerShell here-string을 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -B -`에 전달하는 일회성 CPU probe를 실행했다. 실제 종료 클래스 AST를 실행하고 measurement/manager 입력을 대체하여 150회 호출 시 150줄 출력·3초 성공, 실패 term의 이름 출력·타이머 초기화, 기본 debug False의 무출력을 assert했다. 결과는 `PASS: per-step output, scheduled threshold, success, failure reset, default silence`였다. 이 검사는 실제 물리·scene 유효성을 재현하지 않는다.

실제 Isaac Sim checkpoint 재생과 사용자 보고 상황의 재현은 미실행이다. 출력 추가를 성공 종료 문제의 수정 또는 원인 규명으로 해석하지 않는다.
