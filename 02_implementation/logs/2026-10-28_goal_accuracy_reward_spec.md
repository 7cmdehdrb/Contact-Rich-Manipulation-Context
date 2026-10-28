# Goal Accuracy v0 보상 개선 사양 작성 기록

[개발 사양](../../01_plan/environments/2026-10-28_FINAL_GOAL_ACCURACY_V0_1_REWARD_SPEC.md) · [현재 인계](../../01_plan/00_HANDOFF_BRIEF.md)

## 요청·기준·범위

2026-10-28 사용자 요청에 따라 개발 사양만 작성했다. 2cm 성공 인정, 타겟 Contact, Reaching 목표 반경 분기 제거, r=2cm/R=6cm Hold, 기준 궤적 적분을 맞춘 지수형 Goal Distance를 구체화했다. 이전 대화의 1cm·Goal Distance 유지안은 최신 요청으로 대체한다. 환경 소스·학습 로그·checkpoint는 수정하지 않았다.

Workspace HEAD는 `350db965476f051ba1e1b3e00a7ea6bb377f3ead`, 문서 submodule HEAD는 `548d46ac07df17a39cbf70bdaa9b27ff0727c97d`였다. 시작 시 workspace에는 문서 submodule 포인터 차이가 있었고 문서 내부 작업트리는 깨끗했다. 기존 포인터·커밋은 보존했다.

## 변경 전후·의도·영향

새 계획 문서, PNG 2개, 계산 JSON, 그림 재현 스크립트를 추가하고 계획 색인·인계에 미구현 링크를 추가했다. 현재 구현 명세와 활성 환경 표는 실제 코드의 1cm 계약을 설명하므로 유지했다. 재현 스크립트는 문서 그림 계산용이며 환경을 import하거나 구현하지 않는다.

Goal Distance는 `3.6654400818907504 exp(-20d)`로 정했다. 15cm에서 3초 대기, 3–6초 선형 접근, 6–10초 고정한 기준에서 2cm 도달의 기존 누적 보상 13에 맞췄다. 중심 도달 적분은 18.692183으로 기존 15보다 크다. a=20은 기존 5cm 거리 스케일을 사용한 설계 선택이다.

Contact는 대상만 변경하고 실제 접촉의 freshness·finite·threshold, 목표 간주의 V를 보존한다. Reaching의 near radius 10cm는 목표 반경과 별개로 보존한다. Hold는 내부 식과 속도 감쇠를 유지하고 2–6cm를 연결한다. 파생 Accuracy v1 및 다른 공유 함수 호출자의 기존 동작 보존을 후속 인수 조건으로 명시했다. 보상 지급 변경에 따른 Wrench 예산의 간접 영향도 적었다.

## 검증 명령과 결과

Workspace 루트에서 실행했다.

```bash
MPLCONFIGDIR=/tmp/goal-accuracy-review/mpl /home/min/miniconda3/envs/env_isaaclab/bin/python example/Contact-Rich-Manipulation-Context/03_assets/artifacts/2026-10-28_goal_accuracy_reward_spec/plot_reward_spec.py
```

최초 실행은 설치 NumPy에 `trapezoid`가 없어 실패했다. 동일한 사다리꼴 API인 `trapz`로 그림 스크립트만 수정 후 통과했다. 해석적 적분과 1ms 수치 적분 차이는 두 궤적 모두 1e-6 미만이다. 50Hz 우측 합은 2cm 13.022811, 중심 18.727129로 연속 적분과 차이가 0.2% 미만이다. Hold 경계·총보상 assertion 통과, PNG 두 개의 곡선·축·범례 시각 확인 완료.

문서 저장소에서 다음 검사를 실행했다. 수식 검사 4개 파일 통과, 링크 검사 67개 내부 링크·오류 0, `git diff --check` 통과를 확인했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py 01_plan/environments/2026-10-28_FINAL_GOAL_ACCURACY_V0_1_REWARD_SPEC.md 01_plan/00_HANDOFF_BRIEF.md 01_plan/README.md 02_implementation/logs/2026-10-28_goal_accuracy_reward_spec.md
python 00_guidelines/scripts/check_document_links.py --check-external 01_plan/environments/2026-10-28_FINAL_GOAL_ACCURACY_V0_1_REWARD_SPEC.md 01_plan/00_HANDOFF_BRIEF.md 01_plan/README.md 02_implementation/logs/2026-10-28_goal_accuracy_reward_spec.md
git diff --check
```

## 최종 대조·미검증 범위

요청된 반경·Contact·Reaching·Hold·Goal Distance 변경을 사양 변경 표와 일대일 대조했다. 변경 산출물은 문서 및 문서 분석 자료에 한정한다. 실제 코드 구현, 센서 물리 실행, reset/step, 재생, 학습 수렴, 성공률 개선은 미검증이다. 후속 구현 시 전체 Manager·상속·커리큘럼 대조와 계약 검사를 별도로 수행한다.

## 후속 정정: v0_1 파생·이름 교정·수치 변경

동일 날짜의 사용자 정정에 따라 앞 절의 최초 사양을 대체했다. 최신 기준은 연결된 v0_1 개발 사양이며, 이전 수치와 v0 직접 변경 계획은 작성 이력이다.

- 기존 v0·v1은 Gym ID 및 등록 상수의 `Accuacy` 철자를 `Accuracy`로 바꾸는 이름 교정만 명세에 추가했다. 기존 1cm 반경·보상·커리큘럼·관측·제어 동작은 보존한다. Python 클래스와 experiment_name은 이미 올바른 철자이므로 유지한다. 로그·checkpoint의 과거 이름은 바꾸지 않는다.
- 변경 보상은 v0를 직접 상속하는 신규 `Isaac-Inspire-Final-GoalAccuracy-v0_1`에만 적용한다. 새 EnvCfg·RewardsCfg·PPO 설정과 별도 experiment_name을 명시했다. runtime은 부모와 동일하게 재사용한다.
- v0_1 Reaching은 목표 분기 없이 항상 near radius 0.20m다. 기존 보상식·표·인수 조건의 0.10m를 수정했다. 부모의 기존 0.10→1.0m 전환은 보존한다.
- Goal Distance weight는 사용자 지정 3.7로 고정했다. 해석적 적분은 2cm 13.122572, 중심 18.868424이며 50Hz 합은 각각 13.145598, 18.903699다. 기존 2cm 기준 13과의 차이는 약 0.943%로, 정확한 일치 대신 1% 이내 근사 인수 조건으로 수정했다.
- 계획 문서를 `2026-10-28_FINAL_GOAL_ACCURACY_V0_1_REWARD_SPEC.md`로 이름 변경하고 인계·색인·본 로그 링크를 갱신했다. 기존 구현 설명 문서 파일명 교정은 후속 구현 사양에 기록했으며 이번에는 실행하지 않았다.
- 그래프 두 개와 JSON을 weight 3.7로 재생성했다. 수치 적분·경계 assertion을 다시 통과했다. 이번 수정 역시 환경 소스·학습 로그·실제 Gym 등록에는 적용하지 않았다.

후속 문서 검사에서는 위 명령의 계획 파일명을 `2026-10-28_FINAL_GOAL_ACCURACY_V0_1_REWARD_SPEC.md`로 사용한다. 기존과 새 환경의 등록·동작 회귀 검증은 아직 미구현이므로 실행하지 않았다.

후속 정정 검증 결과: 변경 Markdown 4개 수식 검사 통과, 내부 링크 67개·오류 0, `git diff --check` 통과. 재생성한 두 그래프를 열어 weight 3.7 및 갱신 누적값 표시를 확인했다. `src`, `IsaacLab`, `logs`의 diff는 없다.


## 추가 정정: 큐브 기본 치수만 변경

사용자는 기존 ±10% 크기 랜덤화를 확인한 뒤 ±5% variant 추가와 Scene Reset 시 타겟 종류 재선택 지시를 취소했다. 최종 추가 범위는 Accuracy v0_1부터 큐브 타겟을 0.08m 정육면체에서 로컬 XYZ 0.06×0.08×0.10m 직육면체로 바꾸는 사양이다. 기타 타겟·장애물, 연속 Uniform(0.9,1.1) 균일 배율, 생성 시 형상·배율 선택 및 reset 동작은 보존한다.

실제 `assets/final_spawners.py`와 `mdp/event_functions/final.py`, `mdp/events/final.py`를 확인했다. 현재 prestartup의 bounds 갱신과 reset의 `shelf_surface_height - bounds_min_z` 배치 경로를 유지하도록 기록했다. bottom-origin에 반높이를 잘못 더하지 않고 새 footprint로 배치·목표 여유·가림·target_width를 갱신하는 인수 조건을 추가했다. 부모/기존 v1의 공유 cube 기본값은 바꾸지 않도록 명시했다.

사양의 변경 표·구현 접점·Scene/reset 보존 문장·인수 조건과 인계를 함께 갱신했다. 이 변경은 문서만 반영했으며 환경 코드·그래프 계산식·학습 로그는 수정하지 않았다. 형상 생성·실제 collision 접촉·GPU reset 검증은 미실행이며 후속 구현의 검증 항목이다.

이번 추가 정정 검증: 변경 Markdown 3개 수식 검사 통과, 내부 링크 13개·오류 0, `git diff --check` 통과. 형상/배율/reset의 변경·보존 범위를 최신 사용자 지시와 대조했다.


## 추가 정정: Manager term 주체가 드러나는 이름

사용자 요청은 Reward·Curriculum·Termination의 순수 이름 변경이다. 최종 대상은 앞선 사양의 v0_1이며 부모 v0와 기존 v1의 term 이름은 보존한다. 실제 `mdp/rewards/final.py`, `mdp/curricula/final.py`, `mdp/terminations/final.py`와 계산 함수의 대상 selector·문자열 조회를 확인했다.

사양 8.3절에 Reward 11개, 활성 Curriculum 11개와 비활성 2개, Termination 6개의 기존→최종 이름 및 실제 적용 대상을 전부 명시했다. 특히 object_free_speed→target_free_speed, 종료 object_speed→target_speed, object_drop→object_fall_or_tilt로 정정한다. object_penalty는 전체 물체의 기울기·가속도와 장애물 변위가 합쳐진 기존 복합 항이므로 이름·식·구성을 유지하고 내부 범위를 설명했다. Wrench는 wrist, Arm만 검사하는 종료는 arm 주체를 명시했다.

이전의 term 이름 유지·커리큘럼 이름 유지 문장을 최신 사양에 맞게 수정했다. goal_hold 설정 조회, ShelfPenalty의 shelf_termination 조회, curriculum term_name, Wrench 자기 항 참조와 계산 순서, Manager 로그 키의 동시 갱신을 요구했다. 이름 교정 전후 v0_1의 수치·종료 mask·일정 동등성 및 상속된 옛 항 중복 등록 방지를 인수 조건으로 추가했다. 신규 CurriculumCfg·TerminationsCfg를 명시하고, 인계도 갱신했다.

환경 코드·실제 로그는 수정하지 않았다. 수식·계수·스케줄 변경은 이번 이름 교정에 포함되지 않는다. 실제 Manager 구성·문자열 참조 회귀 테스트 및 GPU 실행은 후속 구현에서 검증한다.

이번 이름 교정 사양 검증 결과: 변경 Markdown 3개 수식 검사 통과, 내부 링크 13개·오류 0, `git diff --check` 통과.
