# Accuracy v1: 외곽 goal_hold와 속도 커리큘럼 복원

[환경 계약·최종 대조](../environments/FINAL_GOAL_ACCUACY_V1_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

## 요청·기준

- 사용자 관찰: Accuracy v0에서 Final v1 대비 학습이 잘 진행되지 않는 현상. 본 작업은 이 관찰을 검증한 실험이 아니라 요청된 파생 환경 구현이다.
- 요청: Accuracy v1 생성, `goal_speed_scale`·`object_free_speed` 복원, `goal_hold`의 r~2r 외곽 구간 복원, 마지막 Final v1 전체 대조.
- 단위 확인: 사용자가 기존과 같은 **0.01 m(1 cm)** 고정을 선택했다. 최초 메시지의 0.01 cm를 적용하지 않았다.
- 코드 기준 commit: `c47ce9f17e917cd6343a3aeef0e0776a81aaf075`. 작업 전 루트에는 문서 submodule 포인터 차이만 있었고 활성 패키지 변경은 없었다.
- 문서 기준 commit: `0f7ce3fffe0d255d1ab09952726546445ea005a4`, 작업 전 문서 작업트리 clean. 기존 commit과 submodule 포인터를 변경하지 않았다.

## 구현·변경 전후

기존 역할별 Final 파일 5개에 클래스·등록만 추가했다. 신규 `FinalGoalAccuracyV1EnvCfg`는 `FinalGoalAccuracyEnvCfg`를 직접 상속한다. Runtime·종료·계측은 기존 `FinalGoalAccuracyEnv`를 그대로 사용한다. 기존 환경과 공유 함수는 수정하지 않았다.

1. `FinalGoalAccuracyV1RewardsCfg`: v0의 `goal_hold` term을 복사하고 callable만 Final v1의 `goal_settling_centered`로 교체했다. weight 8, r=.01, 초기 speed_scale=.05 유지. 외곽 지급은 Final v1과 같은 `d <= 2r`; 목표 판정은 `d <= r`.
2. `FinalGoalAccuracyV1CurriculumCfg`: `goal_speed_scale`만 Final v1에서 복원. `goal_position_tolerance=None` 유지.
3. `object_free_speed`는 v0에서 이미 활성임을 코드로 확인했다. 동일한 target speed term·일정을 상속하며 중복 term이나 별도 일정을 만들지 않았다.
4. PPO는 v0 상속, experiment만 `inspire_final_goal_accuracy_v1`. Gym ID는 `Isaac-Inspire-Final-GoalAccuacy-v1`.

요청하지 않은 weight·장애물 일정은 v0 값을 보존했다. Final v1에 비해 반경 외에도 weight 8 대 4, 빠른 장애물 증가, 속도 항 이름, 계측 차이가 남는다. 모든 Reward·Curriculum 필드와 다른 Manager·runtime·PPO 차이는 연결된 환경 계약의 최종 대조 표에 기록했다. `goal_radius()`를 사용하는 접촉 간주·Reaching 전환·성공 분류와 wrench의 누적 보상 예산에 대한 간접 영향도 포함했다.

## 검증

실행 명령:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q \
  src/inspire_sweep_baseline/tests/test_final_versions.py \
  src/inspire_sweep_baseline/tests/test_final_configuration.py
```

결과: **48 passed in 12.60s**. 신규 4개 검사와 기존 44개 회귀 검사를 포함한다. 실제 Isaac Lab configclass/term 설정과 production MDP 함수에 대한 CPU harness 검사이며 전체 Simulator 환경 실행은 아니다.

- 전체 보상·커리큘럼 차이 및 순서, 기존 부모 설정의 mutable parameter 격리.
- 목표 경계 바로 아래·같음·바로 위와 2r 경계. 외곽 보상은 복원하되 접촉 간주·성공은 r 이내 유지, 목표 조기 종료 없음, 무효 타겟 보상 없음.
- 두 속도 커리큘럼의 실제 적용 대상과 시작·계단 전환·종료·범위 이후·rewind. 고정 목표 반경 보존.
- 등록 ID·entry point, EnvCfg 직접 부모와 override 범위, PPO experiment 외 동등성.
- 작업 전 174개 Python 소스를 `/tmp/accuracy_v1_baseline.json`에 스냅샷한 뒤 AST로 비교했다. 변경한 5개 파일의 기존 top-level 구문·기존 모든 클래스/함수는 불변이고 새 구문만 추가됐으며 나머지 파일은 내용 동일했다.

첫 pytest 실행은 전역 ROS pytest plugin이 `lark`를 찾지 못해 수집 전에 실패했다. 패키지 추가 설치 없이 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`로 외부 plugin 자동 로딩을 비활성화하여 완료했다. 기본 Python에는 torch가 없으므로 설치된 `env_isaaclab` Python을 사용했다.

GPU 물리·실제 전체 import/reset/step·학습 수렴·정확도 향상·TensorBoard 이벤트 생성은 실행하지 않았으며 CPU 통과로 그 결과를 주장하지 않는다. `logs/rsl_rl`은 읽거나 수정하지 않았다.

문서 저장소에서 아래 명령으로 변경 문서만 검사했다. 수식 검사 6개 파일 통과, 링크 검사 6개 파일·내부 링크 150개·외부 링크 33개에서 오류 0. 루트와 문서 저장소의 `git diff --check`도 통과했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  01_plan/00_HANDOFF_BRIEF.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/environments/README.md \
  02_implementation/environments/FINAL_GOAL_ACCUACY_V1_ENVIRONMENT.md \
  02_implementation/logs/2026-10-27_final_goal_accuracy_v1.md \
  ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external \
  01_plan/00_HANDOFF_BRIEF.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/environments/README.md \
  02_implementation/environments/FINAL_GOAL_ACCUACY_V1_ENVIRONMENT.md \
  02_implementation/logs/2026-10-27_final_goal_accuracy_v1.md \
  ../../src/inspire_sweep_baseline/README.md
git diff --check
```
