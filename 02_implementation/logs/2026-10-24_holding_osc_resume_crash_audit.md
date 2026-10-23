# Holding OSC v2 재개 학습의 수치 발산 조사

후속 조사에서 실제 실패 입력과 모델 replay로 raw last_action 관측의 증폭 경로를 확인하고 수정했다. 이 문서는 수정 전 개별 run 감사 기록이며 최신 원인·수정·GPU 검증은 [TEMP 전체 안정성 조사](2026-10-24_temp_training_stability.md)를 따른다.

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [이전 지정 경로 검사](2026-10-24_holding_v0_std_crash_audit.md)

## 대상과 정정

2026-10-24 사용자가 실제 오류 run을 `logs/TEMP/2026-10-24_01-45-06`으로 정정했다. 이전 Holding v0 두 run에서 loss 폭발이 보이지 않았다는 결론은 이 run에 적용하지 않는다. 이번 run은 Holding OSC v2이며 source run `logs/TEMP/2026-10-23_22-20-48`의 `model_2100.pt`에서 resume=true로 재개했다.

저장 Git 기록과 조사 시 Workspace HEAD는 `df95c75`다. 작업 시작 시 이전 조사 문서의 변경이 남아 있었고 보존했다. 학습 코드·설정·checkpoint·로그는 수정하지 않았다.

## 확인된 시간 순서

새 run의 TensorBoard 기록은2100~2341이다.

| iteration | value loss | 해석 |
| --- | --- | --- |
|2100|0.948071|재개 후 첫 기록 |
|2286|183.498|첫100 초과 |
|2287|39693.715|큰 일시적 급등 |
|2317|7728.906|급등 재발 |
|2320|12509.226|반복 불안정 |
|2340|0.295948|마지막 폭증 직전 기록 |
|2341|1.940970093e21|마지막 기록, 심각한 value/target 오차 |

2341에서 평균 std는0.711888, entropy는8.089794, 평균 episode reward는25.290655였으며 learning rate는1e-5였다. 마지막 완료 iteration의 평균 std가 유한하다는 사실은 다음 minibatch의 std가 유효했음을 보장하지 않는다. 정확히 어느 minibatch에서 음수/NaN이 생겼는지는 저장되지 않았다.

source run도2101에서 value loss8.152e7,2102에서4.432e14,2105에서8.524e20,2106에서4.439e29,2107에서NaN을 기록했다. 따라서 재개 전에 이미 value 학습의 수치 불안정이 있었다. resume만의 신규 문제로 단정할 수 없다.

## Checkpoint와 설정 검사

재개 run의 `model_2100.pt`,2150,2200,2250,2300 총5개를 재귀 검사했다. Actor·Critic·optimizer를 포함한 tensor에 NaN/inf가 없었으며 저장 std는 모두 양수였다. 마지막 `model_2300.pt`의 std는 약 `[0.6653,0.4565,0.2895,0.6222,0.6861,0.8214,1.0192,0.9736]`로 최소0.2895다. std가0에 근접했다는 이전 run의 근거를 여기 적용하면 안 된다. Actor·Critic의 최대 파라미터 절댓값도 각각 약7.85·7.99였다. 정상 저장 가중치라도 이상 입력·target·업데이트에서 큰 출력이나 loss가 나올 수 있다.

source agent.yaml과 resume agent.yaml의 차이는 모델 module 경로의 구조 이관, experiment_name, resume/load_run/load_checkpoint뿐이었다. 저장된 PPO 수치 설정과 normalization·distribution 설정은 같았다. `std_type=scalar`, 관측 정규화=false, Adam, adaptive LR,8epochs·4minibatches다. source optimizer LR은1e-5였지만 첫 재개 iteration에 기록된 LR은6.667e-4였다. adaptive LR의 resume 시 동작 차이는 관찰되지만 이번 발산의 단독 원인이라고 확정할 수 없다.

재개 run의 `model_2100.pt`는 원본 파일의 복사가 아니라2100 update 후 다시 저장된 checkpoint다. 두 파일의 가중치 차이만으로 잘못 복원되었다고 해석하지 않는다.

## 결론과 한계

확정된 사실은 **std sampling 오류 전에 value loss가 반복적으로 급등했고 마지막에는1.94e21로 폭증했다**는 것이다. 단순한 scalar std의0 경계 통과보다 더 넓은 학습 수치 불안정을 우선 조사해야 한다. scalar 모드의 양수 보장 부재는 남아 있지만 이것만 바꾸면 해결된다는 근거는 없다. 최종 오류는 std가 음수 또는NaN일 때 모두 발생하며, 실패 순간 std는 확보하지 못했다.

후보는 관측/물리 상태의 이상치, 환경별 reward spike, Critic 예측·bootstrap·return의 이상치, optimizer 업데이트 불안정이다. 설치된 PPO는 환경 reward에 timeout value bootstrap을 더하고 GAE/advantages를 계산한다. 따라서 episode reward 집계가 정상 범위여도 학습 target의 안전성을 보장하지 못한다. Actor/Critic gradient clip은 별도로 수행하므로 Critic gradient가 직접 Actor gradient clip에 섞인다고 설명하지 않는다.

다음 원인 확정에는 rollout의 관측·환경 reward·values·bootstrap 후 reward·returns·advantages와 minibatch의 loss·gradient·std를 순서대로 검사하고 최초 이상 batch 및 직전 모델·optimizer를 보존해야 한다. `check_for_nan=true`만으로 PPO 내부의 큰 유한값·inf·optimizer 이상을 막지는 못한다. 과거 checkpoint로 되돌리는 것만으로 재발이 방지되지 않았다는 이번 기록과도 구분해서 접근한다.

## 실제 실행한 검증

다음은 Workspace 루트에서 실행한 읽기 전용 진단 명령이다. 진단 전용 산출물은 `outputs/holding_osc_resume_crash_audit/`에 저장했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/holding_osc_resume_crash_audit/audit.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/holding_osc_resume_crash_audit/detail.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/holding_osc_resume_crash_audit/compare.py
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/holding_osc_resume_crash_audit/origin.py
```

TensorBoard 전 기록·checkpoint5개·원본 모델2100 비교·원본 run value 추이를 검사했다. CPU의 음수/NaN std synthetic probe는 같은 RuntimeError 문구를 확인했지만 실제 실패 minibatch 재현은 아니다. 실제 GPU 재학습, 실패 시점 replay, 보상/정규화/std 변경은 수행하지 않았다. 로그 정리·이동·삭제도 수행하지 않았다.
