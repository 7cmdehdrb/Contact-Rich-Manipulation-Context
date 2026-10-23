# Holding v0 PPO 표준편차 오류 조사

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

2026-10-24 정정: 사용자가 실제 오류 run을 `logs/TEMP/2026-10-24_01-45-06`으로 수정했다. 이 문서는 처음 지정된 Holding v0 두 run의 별도 검사 기록이며, 실제 오류의 결론에는 [Holding OSC v2 resume 재조사](2026-10-24_holding_osc_resume_crash_audit.md)를 사용한다. 실제 run에는 큰 value loss 폭증이 있었다.

## 요청과 범위

2026-10-24 사용자 보고: Holding v0 학습이 PPO.update의 actor 재평가 중 `normal expects all elements of std >= 0.0`로 종료됐다. Workspace 기준 commit은 `701701d`이며 이전 작업의 Windows renderer 수정과 문서 변경을 보존했다. 이번에는 학습 코드·보상·checkpoint를 변경하거나 학습을 실행하지 않았다.

로컬 `logs/rsl_rl/inspire_contact_sweep_clutter_fusion_holding_v0`의 두 run `2026-10-23_19-36-56`, `2026-10-23_20-07-11`을 읽었다. 저장 agent 설정은 두 실행 모두 resume=false이고 scalar Gaussian, 관측 정규화=false, Adam, adaptive LR,8epochs·4minibatches다. 사용자가 붙인 traceback이 어느 run에서 발생했는지 보여 주는 별도 오류 파일은 확보하지 못했다.

## 확인한 증거

| run | 마지막 TensorBoard iteration | 마지막 value loss | 마지막 checkpoint | 최소 저장 std |
| --- | --- | --- | --- | --- |
|19-36-56|202|1.25956|model_200.pt|0.081664|
|20-07-11|944|0.841834|model_900.pt|0.046898|

첫 실행5개, 두 번째19개 checkpoint의 전체 tensor를 재귀 검사했다. Actor·Critic·optimizer를 포함해 비유한 tensor는 없었으며 모든 저장 std는 양수였다. 기록된 loss·policy 지표에도 NaN/inf는 없었다. 두 번째 run의 마지막6회 value loss는 약0.72~0.85였다. 따라서 저장된 기록에서 Critic loss 폭발이 먼저 발생했다고 주장할 근거는 없다. 기록은 iteration 완료 시점의 집계이므로 실패 minibatch의 이상치는 배제하지 못한다.

`model_900.pt`의 Arm std6개는 약 `[0.0913,0.2899,0.2670,0.0487,0.0469,0.1083]`, Hand2개는 `[1.1707,1.3743]`다. 평균 std가 약0.42여도 작은 Arm 차원의 상태를 대표하지 않는다. Gaussian differential entropy가 음수라는 사실만으로 오류라고 판단할 수는 없다.

설치된 RSL-RL5.0.1의 GaussianDistribution은 scalar 모드에서 std 자체를 unconstrained Parameter로 학습하고 그대로 Normal에 전달한다. 양수 변환이나 하한이 없고 Normal의 argument validation도 비활성화한다. PPO는 minibatch 업데이트 후 다음 actor 재평가에서 stochastic sample을 수행하므로 직전 optimizer update가 std를 음수/NaN으로 만들면 보고된 위치에서 실패할 수 있다.

CPU에서 `torch.normal`에 std=-1과 std=NaN을 각각 전달해 둘 다 사용자와 같은 RuntimeError 문구를 확인했다. 이는 오류 메시지의 모호성을 재현한 것이며 실제 학습 실패 minibatch를 재현한 것은 아니다.

## 결론과 한계

직접 원인은 정책 sampling에 전달된 std에 음수 또는 NaN이 포함된 것이다. 시작 렌더러 오류와는 다른 실행 단계다. 원인 후보는 scalar std의 음수 진입, 비정상 관측·target·gradient에서의 NaN 전파, 업데이트 자체의 수치 불안정이다. 저장 checkpoint 손상은 이번 검사로 뒷받침되지 않으며 실패 순간 dump가 없어 세 후보를 확정적으로 구분할 수 없다.

다음 진단 지점은 각 minibatch의 forward·backward·optimizer.step 전후다. std8차원의 min/max와 음수·NaN 개수, 관측·values·returns·loss·gradient의 유한성을 기록하고 최초 이상 batch와 직전 모델·optimizer를 보존해야 한다. std를 log parameterization으로 바꾸면 음수 진입은 방지할 수 있지만 NaN·overflow 전파까지 해결하는 것은 아니다. 기존 scalar checkpoint 및 Adam 상태를 그대로 log 파라미터에 재사용하는 것도 동등한 resume이 아니므로 변환 검증 없이 명령 옵션만 바꾸도록 안내하지 않는다.

## 실행한 검증

Workspace 루트에서 아래 읽기 전용 감사 명령을 실행했다. 결과는 workspace의 진단 전용 `outputs/holding_v0_crash_audit/audit.json`에 저장했다. 두 실행의 scalar 전체, checkpoint24개 및 위 음수/NaN std probe를 검사했다. `detail.py`는 마지막 지표와 체크포인트별 Arm std 추이를 출력한다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/holding_v0_crash_audit/audit.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/holding_v0_crash_audit/detail.py
```

실패 순간의 실제 GPU batch 재현, 장기 재학습, std 파라미터 변경은 수행하지 않았다. 학습 로그 이동·삭제도 수행하지 않았다.
