# Relative v2_1/v3 왼쪽 접근 실패 진단

## 요청과 범위

사용자 관찰: 오른쪽 목표는 잘 밀지만 왼쪽 목표에서도 타겟 왼쪽으로 접근하여 실패한다. play와 진단 로깅을 명시적으로 허용했고, 아래 체크포인트가 관찰 대상임을 확인했다.

- v2_1: `logs/TEMP/1108/inspire_wrench_refactor_relative_v2_1/2026-11-07_22-43-45/model_9700.pt`
- v3: `logs/TEMP/1108/inspire_wrench_refactor_relative_v3/2026-11-07_18-43-11/model_8700.pt`

분석 당시 workspace HEAD는 `0c3e8d9`. 기존 IsaacLab 작업트리 표시를 보존했다. 이번 작업은 진단이며 활성 환경·보상·PPO·학습 체크포인트·학습 로그를 수정하지 않았다. v2_2 학습이나 보상 수정도 수행하지 않았다.

진단 코드와 원시 로그는 workspace `outputs/relative_left_diagnosis/`에 보존했다. 이 폴더의 probe는 연구용 임시 도구이며 제품 학습 진입점이 아니다. 본 작업의 학습은 실행하지 않았다.

## 재현 조건과 측정

기존 `Inspire-Wrench-Refactor-Relative-v{2_1,3}-Test-{Left,Right}`를 그대로 사용했다. seed42, 각 16환경, deterministic inference, 500 policy steps, dt0.02초, checkpoint iteration curriculum을 적용했다. 물리 장면과 관측 noise는 원래 설정이다. 각 환경의 첫 에피소드만 집계했다. 조기 종료 뒤 자동 reset된 에피소드는 비교에서 제외한다.

좌우는 카메라 기준이 아니라 선반/월드 Y다. Left는 -Y, Right는 +Y. 목표 각도 구간은 기존 방향별 Test 정의를 따른다. 같은 seed의 초기 타겟은 대응하지만 목표에 의존하는 장애물 배치는 일대일 동일하지 않으므로 완전한 거울 실험은 아니다.

접근 판정은 EEF–타겟 XY 거리 10cm 미만, EEF 월드 z<1.21m인 첫 샘플로 정의했다. 이는 분석용 지표이며 실제 contact나 성공 판정과 다르다. `negative_y_near`는 그 시점 EEF.y < target.y인 환경 수다. 별도 `wrong_near_side`는 목표 방향과 EEF–타겟 벡터의 내적이 양수인 수다. 비스듬한 목표에서는 두 지표가 다를 수 있다.

| 정책 | 방향 | 목표 XY 3cm 이내 진입 | 접근 판정 충족 | 그중 타겟 -Y쪽 접근 |
| --- | --- | --- | --- | --- |
| v2_1 / 9700 | Right | 15/16 | 16/16 | 16/16 |
| v2_1 / 9700 | Left | 0/16 | 14/16 | 14/14 |
| v3 / 8700 | Right | 9/16 | 14/16 | 14/14 |
| v3 / 8700 | Left | 0/16 | 16/16 | 16/16 |

3cm 진입은 성공 종료와 구분한다. v2_1 Right의 성공 종료는14/16이었다. v3에는 성공 종료 항 자체가 없다. v2_1 Left의 목표 방향 내적 기준 잘못된 쪽 접근은13/14, v3 Left는16/16이었다.

실행한 재현 판정 명령:

```powershell
python outputs/relative_left_diagnosis/summarize.py --assert-left
```

결과: `AssertionError: LEFT APPROACH FAILURE: majority approach from goal side`. 저장한 실제 rollout에 대해 왼쪽 접근 증상을 재현하는 결정적 검사다. 수정 후 통과 여부는 아직 검사하지 않았다.

## 원인 후보와 대조 결과

검증 전 순위는 (1) 목표와 무관한 초기 접근 정책, (2) 고정 초기 자세와 접근 보상, (3) 관측/목표/제어의 부호 오류였다.

### 1. 고정 초기 자세와 목표 방향을 고려하지 않는 접근 보상이 가장 유력

실측 초기 EEF는 환경 원점을 뺀 좌표로 약 `(-0.3971, -0.1335, 1.2015)m`다. 타겟은 약 `(-0.7, 0, 1.05)m`에 reset된다. 따라서 손은 시작부터 타겟의 -Y쪽으로 약13cm 치우쳐 있다. Right(+Y) 밀기는 현재 쪽에서 바로 접근하면 되지만 Left(-Y) 밀기는 반대편 접근이 필요하다.

`mdp/rewards/wrench_refactor.py`의 `target_reaching`은 weight30이고, 실제 함수는 `mdp/reward_functions/dex_rewards.py:DexReachProgress`다. EEF–현재 타겟의 3D 거리에서10cm를 뺀 값의 새 최솟값 개선량만 보상하며 목표 방향·접촉 면·반대편 staging 위치를 보지 않는다. 같은 거리 개선이면 좌우 어느 면에서 접근해도 동일한 보상을 받는다. 최단거리 접근 이후 반대편으로 도는 동안에는 기존 최솟값을 갱신하지 않는 구간이 생긴다.

실제 첫 에피소드의 평균 누적 reward는 아래와 같다. `RewardManager._step_reward`는 dt로 나눈 값이므로 집계에서 dt0.02를 곱했다.

| 항목 | v2_1 Left | v2_1 Right | v3 Left | v3 Right |
| --- | --- | --- | --- | --- |
| 접근 보상 | +7.709 | +7.607 | +7.826 | +7.378 |
| 거리 보상 | -0.007 | +11.479 | +6.002 | +78.683 |
| 전체 보상 | +6.529 | +122.036 | +11.675 | +75.004 |

실패 방향에서도 빠른 접근의 이득은 유지된다. 양 정책이 초기 -Y쪽 접근을 공통으로 선택하고, v2_1 Left는 접근 후 다수 환경에서 물러나거나 EEF를 높이는 양상을 보였다. 에피소드 마지막에11/16이 EEF 보상 높이14cm보다 위에 있었다. 이는 보상 높이 gate를 피하려는 의도라는 증명이 아니라 관측된 동작이다.

동일 reset 관측에서 다른 입력을 보존하고 goal XYZ만 타겟 ±Y9cm로 바꾼 정책 forward 비교도 수행했다. 초기 Arm6D action의 좌우 cosine 평균은 v2_1 약0.990, v3 약0.999였다(v3 Right 장면 기준). 목표 변화에 완전히 무감각하지는 않지만 초기 접근 동작의 분기는 약하다. Counterfactual 목표는 obstacle layout과 재정합하지 않았으므로 민감도 검사로만 해석한다.

### 2. 왼쪽 접근 자체가 물리적으로 불가능하다는 설명은 지지되지 않음

v2_1 Left 4환경에서 초기240step만 진단용 OSC waypoint 명령으로 교체했다. 초기 손 방향을 유지하고 타겟 기준 `[+.18,+.15,+.20]m`로120step, `[0,+.10,+.12]m`로120step 이동한 뒤 원래 정책에 제어를 넘겼다. 정책·보상·물성은 수정하지 않았다.

- 3/4는 에피소드를 유지한 채 +Y쪽 접근 위치에 도달했다.
- 1/4는 이동 중 물체 넘어짐/기울기 종료가 발생했다. 다른1개는 정책 handoff 후 같은 종료가 발생했다.
- env3은 handoff 후 타겟을 약 `(+4.18,-9.59)cm` 이동시켜 목표 거리 최소1.052cm에 도달했다. 최초 진입 보상+10을 받았지만 안정 유지 성공은 없었다.
- env0도 왼쪽으로 밀었으나 overshoot와 X방향 오차가 남았다.

따라서 적어도 일부 장면에서 오른쪽 접근과 왼쪽 밀기가 가능하다. 왼쪽의 전반적인 도달성·충돌 여유·조작 난도가 오른쪽과 같다는 증거는 아니며,4환경 개입을 성공률 개선 추정으로 사용하지 않는다. handoff 상태는 학습 분포 밖일 수 있다.

### 3. Contact 유지 제거만으로는 공통 문제가 설명되지 않음

v3는 `target_contact=None`인 상태에서도 동일한 잘못된 접근을 보인다. v2_1 Left의 평균 Contact 유지 보상은0.000875로 매우 작았다. 따라서 v2_2의 Contact 유지 제거만으로 접근 방향이 바뀐다고 기대할 근거는 부족하다. v2_2 재학습 효과는 미검증이다.

### 4. cosine 거리 보상의 미세 이동 민감도가 실패 상태를 유지할 수 있음

`RelativeMotionCosineGoalDistance`의1mm는 anchor 갱신 기준이지 최소 보상 이동량이 아니다. 실제 보상은1e-8m보다 큰 변위를 정규화하며 이동량에 비례하지 않는다. v2_1의 누적 변위 cosine도 같은1e-8m 기준을 쓰고 contact gate가 없다.

실측 v3 Left env10은 마지막8초(step100~499)에 순변위 약0.944mm인데 거리 보상+15.966을 받았다. 같은 구간 거리 증가 페널티는 약-0.001635이며 최종 목표 오차는 약7.36cm였다. 순변위와 총 이동거리의 차이도 있으므로 로그를 미세 진동만의 증명으로 해석하지 않는다. 다만 목표 미달 상태의 매우 작은 이동에 상당한 보상이 지급되는 것은 확인했다.

v2_1 Left env6은 전체 타겟 순변위 약0.21mm·실제 contact 판정0step인데 거리 보상+3.476이었다. 접촉 없는 settling drift도 누적 cosine에 들어갈 수 있는 계약이다.

이 현상은 좌우 비대칭을 처음 만든 단독 원인으로 확정하지 않는다. 초기 접근 편향 이후 목표를 달성하지 않는 상태에도 보상이 남는 별도 개선 후보다.

### 5. 좌표 부호 오류와 목표 표본 불균형은 현재 증거에서 우선순위가 낮음

실제 정책 입력 `policy[:,24:27]`을 현재 EEF quaternion과 위치로 월드에 역변환했을 때 목표 command와의 최대 차이는 약4.77e-7m였다. Left/Right 물리 목표도 의도한 Y방향이었다. 측정은 reset 시점이며 모든 상태의 통합 검증은 아니다.

목표 샘플러는 동일 난수로 ±방향을 대칭적으로 생성하고, OBB 재시도에서 실패 목표를 재추출하지 않는다. 관련 표본분포·cosine·EEF 제어축·Jacobian CPU 검사34개가 통과했다. 전체 센서/접촉/기구학의 버그 부재를 증명하지는 않는다.

`gamma=.98`, dt.02초이므로1초/2초 뒤 보상의 현재 할인율은 약0.364/0.133이다. 긴 우회 접근의 학습을 더 어렵게 할 수 있지만, gamma만 바꿔 재학습하지 않았으므로 보조 가설이다. rollout36step은 미래 가치를36step으로 잘라내는 뜻이 아니다.

## 권장 변경 순서 — 아직 미적용

1. 목표 방향의 반대편 접근 위치를 명시하는 보상 또는 단계적 접근 과제로 좌우 진입 경로를 학습시킨다. 단순 접근 보상 증량은 현재 잘못된 접근도 강화한다.
2. 초기 자세·시작 접근 측면을 양쪽에 분산하거나 왼쪽 진입 성공 예시/커리큘럼을 제공한다. 우선 장애물 없는 왼쪽 접근부터 확인한 뒤 원래 장면으로 확대한다.
3. 거리 cosine의 초미세 이동 지급을 실제 진행량·정지 임계값과 대조한다. 미세 변위에 방향 점수만 반복 지급하는 계약을 별도 실험으로 분리한다.
4. 이후 discount와 탐색 설정을 검토한다. PPO 전역 수치부터 바꾸면 원인 분리가 어려워진다.

이는 제안이며 활성 환경에 반영하지 않았다. 인과 확정에는 하나씩 변경한 재학습과 여러 seed의 방향별 평가가 필요하다.

## 실행과 산출물

workspace 루트 PowerShell에서 실행했다.

```powershell
$py = 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe'
& $py outputs/relative_left_diagnosis/probe.py --version 2_1 --direction Left --headless
& $py outputs/relative_left_diagnosis/probe.py --version 2_1 --direction Right --headless
& $py outputs/relative_left_diagnosis/probe.py --version 3 --direction Left --headless
& $py outputs/relative_left_diagnosis/probe.py --version 3 --direction Right --headless
& $py outputs/relative_left_diagnosis/probe.py --version 2_1 --direction Left --guided --count 4 --headless
python outputs/relative_left_diagnosis/summarize.py
& $py -m pytest src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench_refactor_relative.py -q --disable-warnings -k 'uniform_angle or left_only_uniform or relative_test_sector or relative_observation or cumulative_displacement_cosine or relative_motion_anchor or eef_command_axes or offset_eef_jacobian'
```

CPU 결과: **34 passed, 53 deselected in 5.58s**. 최초 probe는 기존 play.py의 `handle_deprecated_rsl_rl_cfg` 호출을 빠뜨려 `stochastic` 인자 오류로 실패했다. 진단 스크립트에 같은 변환을 넣어 해결했고 활성 환경은 수정하지 않았다.

산출물은 `v2_1_Left.jsonl`, `v2_1_Right.jsonl`, `v3_Left.jsonl`, `v3_Right.jsonl`, `v2_1_Left_Guided.jsonl`, 각 console 로그, counterfactual JSON, `summary.json`, `cpu_checks.txt`다. JSONL은 pre-step 위치·goal·EEF·contact와 해당 action 이후 reward·done을 기록한다. terminal step의 물리 위치는 자동 reset 전에 별도로 수집하지 않았으므로 최소 거리는 관측한 pre-step 표본 기준이다. guided counterfactual은 기본 Left 파일명으로 저장되며 최초 기본 Left에는 해당 probe가 없었다. Right counterfactual16환경 파일을 본문의 민감도 수치에 사용했다.

최종 대조: 활성 코드 변경 없음, 기존 부모·자식 환경 및 PPO·termination·curriculum 보존. 진단만으로 수정 완료나 학습 개선을 주장하지 않는다. Markdown·링크·diff 검사를 수행했다.

## 후속: 이전 Wrench / Holding OSC에서는 문제가 없었다는 사용자 관찰

사용자가 이전 계열은 좌우 동작에 문제가 없었다고 설명하여 관련 현행 코드를 직접 비교했다. 정확한 성공 버전·checkpoint는 아직 특정하지 않았으므로 아래는 계열 전체에 대한 인과 확정이 아니다. 추가 GPU 실험이나 환경 수정은 하지 않았다.

중요한 정정: 이전 `WrenchRewardsCfg`에도 동일한 `DexReachProgress`, weight30, near_radius0.10이 있다. 따라서 방향 무관 접근 보상과 초기 위치의 비대칭만으로 신규 퇴화를 설명할 수 없다. 이는 편향의 유지 요인으로 보고, 변경된 계약을 우선 조사해야 한다.

| 변경 축 | 이전 코드 | 현재 Relative v2_1/v3 | 해석 |
| --- | --- | --- | --- |
| 목표 표현 | Wrench와 Holding Fusion: 초기 타겟→목표 거리와 root 기준 방위각2D | 현재 EEF 기준 목표XYZ, 초기 타겟XYZ를 별도 제공 | 고정된 방향 신호가 손 자세에 따라 변하는 두 좌표의 관계로 바뀜 |
| 위치 명령축 | Wrench-v0 및 Holding OSC v0~v4의 현재 구성: root 기준 | `WrenchRefactorOSCAction`: 매step EEF 기준 | 손 회전과 이동 명령의 세계 방향이 결합됨. Wrench-v1/v2는 별도 wrench 제어이므로 이 비교에 포함하지 않음 |
| 손 자세·형상 | 공통 make_robot_cfg의 wrist3 약+45도와 기존 자산 | Refactor wrist3 -90도, vendor right-hand 자산 | 접촉 면·형상과 탐색 난도의 비대칭 가능성. 위치 차이를 wrist3만의 결과로 단정하지 않음 |
| 거리 보상 | Wrench-v0는 proximity, v0_4는 episode-best 실제 거리 개선량; 다른 버전은 cosine도 사용 | 정규화 cosine 방향 보상 | 모든 이전 Wrench에 없던 기능이라고 일반화하면 안 됨. 정확한 비교 버전이 필요 |

후속 우선 가설은 명시적 목표 방향 표현의 소실과 EEF 명령축 변경에 따른 학습 난도 증가, 손 자세·자산 변경에 따른 물리적 비대칭이다. 현재 입력에도 목표 방향 정보는 남아 있다. EEF 기준 목표XYZ와 초기 타겟XYZ의 차이를 통해 복원할 수 있으므로 정보 누락이나 불가능한 학습이라고 표현하지 않는다. 초기 타겟에는 reset 고정 noise가 포함된다.

구분 실험은 기존 정책의 관측/제어 의미를 실행 중 바꿔 평가하지 않고, 별도 실험 환경에서 재학습해야 한다. 우선 현재 관측에 episode-fixed 목표 방향(sin/cos 또는 단위벡터)만 추가한 실험, 다음으로 root-frame action만 복원한 실험을 분리한다. 손 자세·자산 비교는 그다음 독립 변수로 둔다. 정확히 잘 됐던 이전 task ID와 checkpoint를 특정하면 비교 범위를 더 줄일 수 있다.
