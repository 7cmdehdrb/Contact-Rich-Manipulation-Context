# Final GoalAccuacy v0: 1cm 목표 정확도

[개발 로그 목록](README.md) · [환경 계약](../environments/FINAL_V1_V2_ENVIRONMENTS.md#final-goalaccuacy-v0--1cm-정확도) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기준일: 2026-10-27. 코드 workspace HEAD `efc0965`, 문서 submodule HEAD `7059478`. 작업 시작 시 두 저장소에 이미 미커밋 변경이 있었으며, 특히 Final v1-1, Final Test v1과 진단 코드·문서는 기존 사용자 작업으로 보존했다. 이번 구현은 이 상태의 현재 파일을 기준으로 덧붙였다. 학습 로그는 정리하거나 변경하지 않았다.

## 요청과 구현

Final v1의 목표 근접 후 1cm 미만 정확도가 부족하다는 사용자 관찰을 바탕으로, `Isaac-Inspire-Final-GoalAccuacy-v0`를 v1 직접 파생으로 추가했다. 독립 `FinalGoalAccuracyEnvCfg`, 각 Manager Cfg, `FinalGoalAccuracyEnv` runtime, PPO experiment, Gym 등록을 연결했다. Actor 57D·장애물20슬롯80D·Critic 현재 타겟 위치3D·OSC Arm/Hand action 8D, Scene·reset fallback·그 밖의 종료는 v1과 같다. 현재 타겟 상태는 여전히 Critic·보상·평가에 쓰이며, 새 Metric은 Actor 관측에 추가하지 않는다.

최초 구현에서는 Goal 속도 척도0.05m/s, 위치 허용 반경0.01m, 타겟 무료 속도0.1m/s를 시작부터 고정하고 세 일정을 제거했다. 장애물은 초기 Gray1/White1에서 2000에 White2, 2500에 Gray2, 이후 전체500 iteration마다 교대로 증가하여 8000에 White8, 8500에 Gray8이 된다. 기존 개수 fallback은 물리 배치 실패 시 그대로 적용한다.

최초 구현에서는 `goal_hold`의 1~2r 구간 보상을 없애고 유효 타겟 `d < r`에서만 지급했다. 성공·목표 안 접촉 간주도 같은 엄격 경계와 1cm 반경을 사용하며, 성공 판정은 v1처럼 XY 위치만 읽었다. Hand–타겟 Reaching 인정 반경 둘 다1cm로 조정했다. 물리적 손 접촉 임계값0.01N과 별도다. 목표 보상 weight4→8, 이름을 바꾼 `target_speed_penalty` weight−5→−10으로 두었다. 이는 당시의 초기 보정이며 학습 결과 기반 최적 계수가 아니다. 아래 후속 수정이 현재 코드 계약을 대체한다.

매 종료 판정 step에서 타겟–목표 XY 거리, 실제 EEF 선속도, 타겟 선속도·선가속도, 보정 F/T 관측의 힘·모멘트 크기를 수집한다. reset 때 시간 평균 또는 에피소드 최대값을 종료된 환경 사이에서 평균해 `Metrics/` 스칼라로 기록한다. 비유한 샘플은 제외한다. 장애물 실제 배치 개수는 `Curriculum/`에서 `Metrics/`로 옮겼다. 각 키와 단위는 [환경 계약](../environments/FINAL_V1_V2_ENVIRONMENTS.md#final-goalaccuacy-v0--1cm-정확도)을 따른다.

## 검증

작업 초기의 Final CPU 검사에서는 기존 정적 테스트가 새 파생 클래스 이름을 모르는 문제로 39개 통과·1개 실패였다. 정적 검사의 허용 대상을 새 클래스로 확장하고, 커리큘럼 경계·엄격한 목표 경계·Metric reset 로그 검사를 추가했다. 이후 실행한 검증 결과를 아래에 기록한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_final_versions.py \
  src/inspire_sweep_baseline/tests/test_final_configuration.py \
  -q -p no:cacheprovider
```

결과: **43개 통과**. `python -m compileall -q src/inspire_sweep_baseline/inspire_sweep_baseline/{envs,agent,mdp,runtime} src/inspire_sweep_baseline/tests/test_final_versions.py`, `python 00_guidelines/scripts/check_document_links.py`(내부 오류0개), 변경한 문서4개의 `check_markdown_math.py`, 양쪽 저장소 `git diff --check`도 통과했다. `check_document_links.py --check-external`은 기존 로그가 가리키는 현재 작업트리의 누락 산출물41개로 실패했다. 이 목록에는 이번에 추가한 파일이 없다. 실제 Isaac Sim GPU reset/rollout, 장기 학습, 1cm 성공률과 TensorBoard 이벤트 파일 생성은 아직 검증하지 않았다. CPU 계약 검사와 학습 정확도 향상은 구분한다.

## 학습 실행

Workspace 루트에서 다음 명령을 사용한다. 새 experiment 이름으로 기록되므로 기존 v1 로그를 변경하지 않는다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Final-GoalAccuacy-v0 --num_envs 256 --headless
```

## 후속 독립 상세 문서

같은 날 [Final GoalAccuacy v0 독립 명세](../environments/FINAL_GOAL_ACCUACY_V0_ENVIRONMENT.md)를 추가했다. v1 문서와 같은 수준으로 관측 순서·차원·노이즈, Scene·배치 fallback·물성, 8D Action과 OSC, 전체 보상식과 1cm 경계, 활성 커리큘럼10개, 종료 분류, TensorBoard Metric의 계산·집계·단위를 기록했다. 환경 문서 목록·활성 환경·계열 요약·패키지 README에서 이 문서로 연결했다. 기존 학습 코드는 이 문서 작업에서 변경하지 않았다.

문서 submodule에서 `python 00_guidelines/scripts/check_document_links.py`는 내부 오류0개, `python 00_guidelines/scripts/check_markdown_math.py`는 새 독립 문서·환경 안내·계열 문서·문서 목록·이 개발 로그의 5개 파일에 대해 통과했다. 루트와 문서 submodule의 `git diff --check`도 통과했다. `check_document_links.py --check-external`은 기존 역사 로그가 참조하는 누락 산출물41건으로 실패했으며 새 문서의 경로는 해당 목록에 없다. 문서 작업 후 GPU 실행·학습은 새로 수행하지 않았다.

## 후속 수정: Final-v1 수치 복원과 `d ≤ 1cm` 경계 통일

사용자 후속 지시에 따라 최초 구현에서 과하게 변경한 항목을 되돌렸다. `hand_reaching`과 `hand_contact`는 Final-v1의 함수·계수를 그대로 상속한다. Reaching의 EEF–타겟 3D 인정 반경은 평소0.10m, 유효한 타겟–목표 XY 거리 `d ≤ 0.01m`에서1.0m다. Hand 접촉 보상은 실제 유효 접촉 또는 동일한 목표 점유에서 지급한다. 목표 첫 진입 때 Reaching의 남은 접근 진전을 한 번 지급할 수 있으나, 최저 gap 기록 때문에 재진입으로 반복 지급하지 않는다.

`goal_hold`는 기존의 `2r` 바깥 구간 제거와 +8 계수를 유지하면서 cutoff를 `d ≤ 0.01m`로 맞췄다. 만료 성공과 불성공 분류도 `d ≤ 0.01m`와 그 여집합으로 통일했다. 성공 함수는 기존 지표 수집을 수행한 뒤 Final-v1의 만료 성공 함수를 호출한다. 성공 분류는 여전히 타겟 유효성·속도를 검사하지 않고 XY 거리만 검사한다.

`target_speed_penalty`는 Final-v1 `object_speed_penalty`와 동일한 함수·weight−5·파라미터를 사용한다. `object_free_speed` 커리큘럼도 Final-v1의 `(0:0.1), (499:0.1), (500:0.09), (1900:0.02)`와 interval250을 복원하고 갱신 대상 이름만 바꿨다. Goal 속도 척도0.05m/s와 목표 반경0.01m의 커리큘럼 삭제, 장애물 개수 일정, TensorBoard 지표는 유지한다.

CPU 검증은 다음 명령으로 관련 테스트 **56개 통과**를 확인했다. 테스트는 `d=0.01m`에서 Reaching 반경 전환·Goal hold·접촉 간주·만료 성공이 모두 인정되는지, 밖에서 불인정되는지, Reaching 재진입에 중복 지급이 없는지, 타겟 속도 비용과 일정이 Final-v1과 같은지를 확인한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_final_versions.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v4.py \
  src/inspire_sweep_baseline/tests/test_final_configuration.py \
  -q -p no:cacheprovider
```

이번 후속 수정에 대해서는 Isaac Sim GPU rollout, TensorBoard 이벤트 파일 생성, 학습 수렴과 1cm 달성률을 실행하지 않았다.

문서 submodule에서 `python 00_guidelines/scripts/check_document_links.py`는 내부 오류0개, `python 00_guidelines/scripts/check_markdown_math.py 02_implementation/environments/FINAL_GOAL_ACCUACY_V0_ENVIRONMENT.md 02_implementation/environments/FINAL_V1_V2_ENVIRONMENTS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/2026-10-27_final_goal_accuracy.md`는 4개 통과했다. 루트와 문서 submodule의 `git diff --check`도 통과했다.

## Final-v1 ↔ GoalAccuracy-v0 최종 차이 대조

후속 사용자 지시에 따라 원래 `PLAN7.md` 요청과 최신 결정을 구분했다. 최초 계획의 `object_free_speed` 삭제와 `d < r` 표기는 최신 결정에서 각각 **Final-v1 속도 일정 유지**와 **`d <= r`**로 대체됐다. 아래는 현재 코드의 최종 활성 계약을 부모와 대조한 결과다.

| 범위 | 부모 Final-v1 대비 GoalAccuracy-v0의 실제 차이 | 최신 요청 대응 |
| --- | --- | --- |
| Gym·EnvCfg·runtime·PPO | 독립 task ID, 파생 EnvCfg/runtime, 독립 experiment 이름 | 새 환경 등록·학습 로그 분리 |
| Scene·Event·reset·Observation·Action·PPO 모델 | 차이 없음. 같은 부모 구성 상속 | 요청 외 계약 보존 |
| `goal_hold` | 반경0.02m·속도 척도0.05m/s 시작 → 0.01m·0.05m/s 고정, 지급 cutoff `d <= 2r` → `d <= r`, weight4→8 | 두 Goal 커리큘럼 제거·외곽 보상 제거·계수 조정 |
| `hand_reaching`·`hand_contact` | 함수·params·weight 차이 없음. 고정된 `r`을 읽으므로 목표 점유 범위만 초반 부모와 다름 | 부모 기능 보존·`d <= r` 공유 |
| 타겟 속도 비용 | `object_speed_penalty` 비활성, 같은 함수·params·weight−5를 `target_speed_penalty` 이름으로 등록 | 이름만 변경 |
| 커리큘럼 13항 | `obstacle_population` 첫 Gray3000→2500·색별 interval2000→1000; `goal_speed_scale`·`goal_position_tolerance` 비활성; `object_free_speed` 값·interval 동일, 갱신 대상만 새 term 이름으로 변경. 나머지 9항 동일 | 장애물 빈도·Goal 고정·속도 비용 일정 유지 |
| 성공·불성공 만료 | `d <= r`와 여집합 판정 함수·시간 한계 동일. GoalAccuracy는 성공 함수에서 지표를 수집한 뒤 부모 함수를 호출 | 목표 경계 통일·지표 수집 |
| TensorBoard | 부모의 실제 장애물 수 키를 `Curriculum/`에서 `Metrics/`로 이동; 목표 거리·EEF/타겟 속도·타겟 가속도·F/T 최대값 추가 | 요청 지표 기록 |

이 대조에서 사용자 요청과 연결되지 않는 활성 보상·커리큘럼·종료·관측·행동 변경은 확인되지 않았다. CPU 설정·경계·일정 검사는 위의 56개 테스트에 포함됐으며, 시뮬레이터 물리·학습 결과의 동등성은 검증하지 않았다.
