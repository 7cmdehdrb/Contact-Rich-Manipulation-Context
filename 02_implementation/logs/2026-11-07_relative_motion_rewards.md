# Relative 실시간 이동 cosine·거리 증가 비용·v3 성공 항 제거

2026-11-07. 사용자 요청에 따라 기존 Relative-v0를 직접 수정하고 v2/v3에 상속한다. v3의 추가 보상·종료 제거도 직접 적용한다. 새로운 task ID는 만들지 않는다. 기준 workspace commit은 `9a192b03556a18ff07e0d9edee551888e14a9215`이며 작업 시작 시 root의 기존 변경은 `? IsaacLab`뿐이었다. 해당 변경과 submodule commit, 기존 학습 로그를 보존했다.

## 의도와 최종 변경

이전 cosine은 초기→목표와 초기→현재 누적 변위를 비교하여 현재 접근·이탈 방향을 구분하지 못했다. 이를 현재→목표와 조건부 갱신 기준점→현재의 이동 벡터로 바꾼다. 사용자의 최신 요구를 적용하며, 이전 답변에서 제안한 양의 거리 개선 보상이나 이동량 가중치는 추가하지 않는다.

| 영역 | 변경 전 | 변경 후 |
| --- | --- | --- |
| Relative-v0/v2 거리 | `displacement_cosine_goal_distance`, weight5 | `RelativeMotionCosineGoalDistance`, weight5, XY 기준점 갱신1mm |
| Relative-v3 거리 | 기존 누적 cosine·현재 접촉 gate·weight25 | 같은 새 cosine 클래스, 현재 접촉 gate·weight25 유지 |
| Relative 공통 거리 증가 | 없음 | `target_inverse_distance`, weight−12.97, 직전step 거리 증가만 비용 |
| v3 최초 진입 / Hold / 성공 보상 | +10 / weight10 / +75 | 해당3항 `None`, 매니저에서 제외 |
| v3 성공 종료 | 3cm·5mm/s 이하·3초 유지 | `target_goal_success=None` |
| v0/v2 성공 관련 보상·종료 | 기존 설정 | 유지 |

등록은 `Inspire-Wrench-Refactor-Relative-v0`, `-v2`, `-v3`이며 EnvCfg는 각각 `WrenchRefactorRelativeEnvCfg`, `WrenchRefactorRelativeV2EnvCfg`, `WrenchRefactorRelativeV3EnvCfg`다. v2/v3 모두 v0 직접 상속을 유지한다. 공통 runtime `WrenchRefactorEnv`와 각 기존 PPO runner는 수정하지 않았다.

실행 코드 변경은 기존 세 파일 안에 한정했다.

- `mdp/reward_functions/wrench_refactor.py`: 두 stateful reward term 추가. 이전 Refactor용 누적 cosine 함수는 보존.
- `mdp/rewards/wrench_refactor.py`: `WrenchRefactorRelativeRewardsCfg`로 공통 두 항을 정의하고 v3 보상 Cfg가 상속. v3는 거리 항의 접촉 gate·weight만 재정의.
- `envs/wrench_refactor_envs.py`: v0가 공통 보상 Cfg를 사용. v3 post-init에서 요청한 보상3개·종료1개를 비활성화. 부모 post-init의 기존 항 설정이 끝난 뒤 제거한다.

## 두 위치 이력과 reset

이동 기준점 `a`는 reset의 실제 타겟 XY로 초기화한다. 매 제어step `m=p_t−a`, `q=g−p_t`로 signed cosine을 계산하고, 보상 계산 **후** `||m||>=0.001m`인 환경만 `a=p_t`로 갱신한다. 두 벡터 길이가1e−8m 이하이면 보상0이다. 따라서 정확한 목표점은 방향이 없어0이며, 목표3cm 이내라는 이유로 cosine을1로 바꾸지 않는다. 접촉·높이 gate가 거짓이어도 이력은 갱신한다.

1mm 조건은 갱신 조건만이다. 1mm 미만의 벡터도 매step 정규화·평가한다. 1mm 미만의 잔여 변위에서 멈추면 해당 기준점 대비 방향은 계속 남고, 기준점 갱신 전의 작은 방향 전환도 직전step 방향과 다를 수 있다. 사용자 지정 방식의 특성이며 임의 deadband나 필터를 추가하지 않았다.

거리 증가 비용은 별도의 이전 위치 `p_(t−1)`를 매step 저장하여 `max(||p_t−g||−||p_(t−1)−g||,0)`을 계산한다. 목표는 기존 command 계약대로 episode 동안 고정되어 있어 이는 정확히 `max(d_t−d_(t−1),0)`이다. 접촉·높이 gate를 두지 않는다. reset manager 순서는 물체 배치 event → reward reset → command reset이므로, reward reset에서 새 물체 위치를 저장하고 다음 계산에서 새 goal을 사용한다. reset 순간의 먼 위치 변화나 이전 goal 때문에 가짜 비용이 생기지 않는다.

두 항은 환경별 step cache를 사용한다. 같은step 중복 호출은 동일 결과이며, 부분 reset은 해당 환경의 위치와 cache만 초기화한다. 실제 GPU 환경에서도 새 스폰 위치와 두 이력을 비교하고 다른 환경의 이력이 보존되는지 검사했다.

## 계수 산정과 dt

기준은 Relative-v0의 기존 거리 항만이다. 높이 gate는 참, 목표로 직진하여 cosine=1,10cm에서0cm까지3초 등속 이동을 가정한다. 접촉 유지·최초 진입·Hold·성공 보상은 분모에 포함하지 않는다.

```math
d(t)=0.1\left(1-\frac{t}{3}\right),\qquad
R=\int_0^3 5e^{-d(t)/0.05}\,dt
=7.5(1-e^{-2})=6.484985.
```

누적10cm 이탈 비용을 위 누적 보상의20%로 맞춘다. `w=−0.2×R/0.1=−12.96997075…`를 소수점 둘째 자리까지 반올림하여 **−12.97**로 설정했다. 실제 한step 보상은 다음과 같다.

```math
r_t=-12.97\max(d_t-d_{t-1},0).
```

RewardManager가 함수 반환값에 `weight×step_dt`를 곱하므로 함수는 증가량을 `step_dt`로 나누어 반환한다. 따라서 dt를 이중 적용하지 않으며 1mm 이탈의 실제 비용은−0.01297, 총10cm 이탈은−1.297이다. 거리 감소·정지는0이다. coefficient는 환경별 재산정 없이 v2/v3에 그대로 상속한다. v3의 거리 weight25 기준으로20%가 되는 계수는 아니다.

적분 기준으로20%이며,50Hz 이산 표본과 목표 정확히 도착한step의 cosine0 때문에 실제 scripted trajectory 누적 비율은 약간 달라질 수 있다. 실제 학습에서의 보상 비중을20%로 강제하는 규칙도 아니다.

## 전체 계약 최종 대조

실제 Cfg 전체 dictionary allowlist 비교로 기존 Relative-v0 대 비Relative 부모 차이에 이번 거리 항 교체·신규 항만 추가됨을 확인했다. v2는 v0의 관측 차이만 유지하고, v3는 기존 접촉 유지 제거·거리 weight/gate 외 요청한3개 보상과1개 종료 제거만 추가한다. 비Relative 부모를 새로 생성해 원래 설정이 유지되는지도 비교했다.

Scene·물체/goal 배치·물성·reset event·관측/차원/noise·OSC·Hand·F/T 보정/clip·Action Rate cap·나머지 보상·실패 종료·두 curriculum·등록·runtime·PPO는 변경하지 않았다. 보상 수는 v0/v2가13→14, v3가12→10이다. v3는 성공으로 조기 종료하지 않으며 실패가 없을 때10초 timeout까지 계속한다. 물체 낙하·기울기, 선반 실패, Arm 속도 종료는 그대로 활성이다.

## 검증

Windows11 / RTX4070 / `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`에서 수행했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench_refactor_relative.py src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py -q
```

**85 passed**. 1mm 직전·정확한 경계·직후, sub-mm 평가, 기준점 갱신 전/후, 중복 호출, 목표 초과·되돌아오기·직각 이동·정확한 목표점, 직전step 거리 증감, dt 상쇄, 부분/전체 reset, 새로운 goal, 무접촉 비용, v3 무접촉 중 이력 갱신, 계수 산정 및 비Relative 보존을 검사했다. 첫 실행은84통과·1실패였다. double 위치 fixture에 float32 목표를 넣어 직각 cosine에4.77e−10이 남은 정밀도 불일치였으며 fixture dtype을 일치시켜 해결했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe src/inspire_sweep_baseline/tests/_wrench_refactor_relative_probe.py --version 0 --num_envs 2 --headless --device cuda:0 --output outputs/relative_motion_validation/v0
```

`--version`을0/2/3, output을각각v0/v2/v3로 바꾸어 세 번 실행했고 모두exit0이다. 버전별 **2환경×180step**의 유한값·실제 전체 설정·부모 격리·부분 reset·두 위치 이력·관측/noise 이후 F/T clip·고정 물성·EEF OSC·커리큘럼 경계를 검사했다. v3 실제 매니저에서 성공 관련4항 부재 및150step 시 timeout 거짓/500step 시 timeout 참을 확인했다. 이 timeout 검사는 목표를 현재 타겟에 맞추고 counter를 지정한 매니저 검사이며, 물리적으로3초 유지한 정책의 성공률 시험이 아니다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-v3 --num_envs 32 --headless --device cuda:0 --max_iterations 2 --resilient-attempt-dir outputs/relative_motion_validation/train_v3 --resilient-target-iterations 2
```

**32환경×2 PPO iteration 완료**, exit0, `training_status.json` completed/last_iteration1, `model_1.pt` 저장. checkpoint를 `weights_only=True`로 로드하여100개 텐서의 finite를 확인했다. value loss는0.0118/0.0209이며 새 penalty가 실제 학습 로그에 기록된다. 저장된 env.yaml에서도 새 클래스·anchor_distance0.001·weight−12.97 및 v3의4개 null 항을 확인했다. 기존 worker 출력 경로 옵션만 사용했으며 supervisor를 실행하지 않았다. `logs/rsl_rl`에는 쓰지 않았다. 검증 산출물은 workspace `outputs/relative_motion_validation`에 버전별log/JSON과 학습 상태·checkpoint로 남긴다.

## 미검증 범위와 인계

장기 학습 안정성·성공률·미세 왕복 유인·정책의 실제 당기기 개선은 아직 검증하지 않았다. v0/v2 PPO 업데이트는 이번에 별도로 실행하지 않았고 실제 rollout 및 공통 함수 시험을 수행했다. F/T 질량·관성 보정 코드는 변경하지 않아 전 작업의 물리 보정 검증 결과를 유지하며 이번에 별도의 동적 wrench fixture를 재실행하지 않았다. 변경은 새 프로세스에서 환경을 생성할 때 적용된다.

환경 설명·패키지 README·인계·활성 안내를 갱신했다. 변경한7개 Markdown 수식 검사 통과, 문서 저장소515개 Markdown 전체 링크 검사 errors0, 양쪽 `git diff --check` 통과. README 외부 경로 확장 검사는 기존 누락 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 한 건을 보고한다. 이 오류는 이전 개발 로그에도 확인된 기존 항목이며 이번 새 링크는 통과했다. 문서 렌더링 화면 검사는 별도로 수행하지 않았다.
