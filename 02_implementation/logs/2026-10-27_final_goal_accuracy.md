# Final GoalAccuacy v0: 1cm 목표 정확도

[개발 로그 목록](README.md) · [환경 계약](../environments/FINAL_V1_V2_ENVIRONMENTS.md#final-goalaccuacy-v0--1cm-정확도) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기준일: 2026-10-27. 코드 workspace HEAD `efc0965`, 문서 submodule HEAD `7059478`. 작업 시작 시 두 저장소에 이미 미커밋 변경이 있었으며, 특히 Final v1-1, Final Test v1과 진단 코드·문서는 기존 사용자 작업으로 보존했다. 이번 구현은 이 상태의 현재 파일을 기준으로 덧붙였다. 학습 로그는 정리하거나 변경하지 않았다.

## 요청과 구현

Final v1의 목표 근접 후 1cm 미만 정확도가 부족하다는 사용자 관찰을 바탕으로, `Isaac-Inspire-Final-GoalAccuacy-v0`를 v1 직접 파생으로 추가했다. 독립 `FinalGoalAccuracyEnvCfg`, 각 Manager Cfg, `FinalGoalAccuracyEnv` runtime, PPO experiment, Gym 등록을 연결했다. Actor 57D·장애물20슬롯80D·Critic 현재 타겟 위치3D·OSC Arm/Hand action 8D, Scene·reset fallback·그 밖의 종료는 v1과 같다. 현재 타겟 상태는 여전히 Critic·보상·평가에 쓰이며, 새 Metric은 Actor 관측에 추가하지 않는다.

Goal 속도 척도0.05m/s, 위치 허용 반경0.01m, 타겟 무료 속도0.1m/s를 시작부터 고정하고 세 일정을 제거했다. 장애물은 초기 Gray1/White1에서 2000에 White2, 2500에 Gray2, 이후 전체500 iteration마다 교대로 증가하여 8000에 White8, 8500에 Gray8이 된다. 기존 개수 fallback은 물리 배치 실패 시 그대로 적용한다.

`goal_hold`의 1~2r 구간 보상을 없애고 유효 타겟 `d < r`에서만 지급한다. 성공·목표 안 접촉 간주도 같은 엄격 경계와 1cm 반경을 사용하며, 성공 판정은 v1처럼 XY 위치만 읽는다. Hand–타겟 Reaching 인정 반경 둘 다1cm로 조정했다. 물리적 손 접촉 임계값0.01N과 별도다. 목표 보상 weight4→8, 이름을 바꾼 `target_speed_penalty` weight−5→−10으로 두었다. 이는 허용 영역 축소와 무료 속도 확대에 따른 초기 보정이며 학습 결과 기반 최적 계수가 아니다. 다른 보상·운동 페널티 계수는 유지한다.

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
