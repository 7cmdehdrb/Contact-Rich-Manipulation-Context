# Revision · Holding · Final 환경 안내

활성 기반 패키지는 `src/inspire_sweep_baseline`이다. **2026-11-01 새 개발 대상은 독립 Revision-v0**이며, 기존 Holding → Final 환경은 비교·기존 학습 재현용으로 보존한다. `src/axia80_feasibility`는 현재 사용하지 않는다. 이 문서는 작업 대상을 찾는 색인이다. 수식·수치·실험 이력은 요청한 환경의 설명과 실제 코드만 확인한다.

## Revision — 독립 신규 환경

`Isaac-Inspire-Revision-v0`는 `envs/revision_envs.py:RevisionEnvCfg`와 `runtime/revision.py:RevisionEnv`를 사용한다. 둘 다 Isaac Lab 기반 클래스를 직접 상속하며 기존 환경 CFG를 부모로 사용하지 않는다. v0_2를 기능 기준으로 중앙 크기 랜덤화·10개 물리 물체·OBB 배치·Actor/Critic 관측 분리·성공 3cm/Hold 8cm·접촉 높이 조건을 적용한다. [환경 명세](environments/REVISION_V0_ENVIRONMENT.md) · [구현 및 검증 상태](logs/2026-11-01_revision_v0_implementation.md).

## Final — 기존 비교 환경

물체 전시: [Shelf Object Gallery](../../../src/shelf_object_gallery/README.md)는 Final과 동일한 선반 위에 절차적 4종과 YCB 상자·캔 4종을 기준 크기 n×m 격자로 보여주는 별도 Isaac Lab 패키지다. 기본 2×4에서 총 8종을 하나씩 표시하며 로봇·학습은 없다. [구현·검증 기록](logs/2026-11-01_shelf_object_gallery.md).

설명 문서 모음: [논문 작성용 환경 근거 자료](../04_article/environment_reference/README.md). [선반 작업 영역과 물체 형상](../04_article/environment_reference/FINAL_SHELF_AND_OBJECT_GEOMETRY.md)은 작업면 경계, 기본 치수·scale, 충돌 형상과 물체 역할 선택을 설명한다.

학습 구조: [Final 계열의 Actor·Critic·관측 MLP와 PPO 손실](../04_article/environment_reference/FINAL_TRAINING_NETWORKS.md)은 최신 GoalAccuracy v0_2_2를 포함한 네트워크 구조, 관측 차원, GAE, 손실별 역전파 경로를 설명한다.

장면 생성: [최종 환경의 Scene Generation and Randomization](../04_article/environment_reference/FINAL_SCENE_GENERATION_AND_RANDOMIZATION.md)은 GoalAccuracy v0_2_2의 타겟·목표 추출, RED/Gray/White OBB 배치 알고리즘, 실패 처리, 형상·크기·물성 무작위화 시점을 설명한다.

상태와 관측: [최종 환경의 State and Privileged Information](../04_article/environment_reference/FINAL_STATE_AND_PRIVILEGED_INFORMATION.md)은 전체 환경 상태, Actor 137D·Critic 140D 관측, 초기 장면 캐시·센서 노이즈, Critic 전용 현재 타겟 XYZ와 부분 관측의 의미를 설명한다.

F/T 센서: [최종 환경의 센서 형상과 Wrench 계측](../04_article/environment_reference/FINAL_FT_SENSOR_AND_WRENCH.md)은 실린더 치수, 측정 고정 관절, EEF 기준점 변환, 손의 중력·관성 보상과 관측 노이즈를 설명한다.

배치 규칙: [OBB 텐서 배치 모듈](environments/BBOX_SCENE_LAYOUT.md)은 **GoalAccuracy v0_2_1 및 그 파생 v0_2_2**에서 사용한다. v0_2_1의 회귀·기하 106개 및 GPU reset 검증은 [연결 기록](logs/2026-10-31_final_v0_2_1_obb_reset.md)을 따른다. v0_2_2의 물리 객체 축소·역할 공유·재질 재사용과 별도 검증은 [구현 기록](logs/2026-10-31_final_v0_2_2_compact_scene.md)을 따른다.

등록 위치는 패키지 `__init__.py`, EnvCfg는 `envs/final_envs.py`다. 아래 ID의 공통 접두사는 `Isaac-Inspire-Final-`이다. 기존 오타 `GoalAccuacy`는 2026-10-28에 `GoalAccuracy`로 교정했다. 기존 v0/v1 동작은 유지한다.

| ID 접미사 | 설정 상속 | 용도·설명 |
| --- | --- | --- |
| `v0` | `FinalEnvCfg` → Isaac Lab `ManagerBasedRLEnvCfg` | [독립 기반 구성](environments/FINAL_V0_ENVIRONMENT.md) |
| `v1` | `FinalV1EnvCfg` → `FinalEnvCfg` | [Final v1 상세](environments/FINAL_V1_ENVIRONMENT.md) |
| `v1-1` | `FinalV1EnvCfg` 파생 | 지수형 goal distance 보상. [변형 비교](environments/FINAL_V1_V2_ENVIRONMENTS.md) |
| `Test-v1` | `FinalV1EnvCfg` 파생 | object penalty 분리 계측. [변형 비교](environments/FINAL_V1_V2_ENVIRONMENTS.md) |
| `GoalAccuracy-v0` | `FinalV1EnvCfg` 파생 | [1cm 정확도 환경](environments/FINAL_GOAL_ACCURACY_V0_ENVIRONMENT.md) |
| `GoalAccuracy-v0_1` | `FinalGoalAccuracyEnvCfg` 파생 | [2cm 목표·타겟 접촉·연속 Hold·지수 거리·직육면체](environments/FINAL_GOAL_ACCURACY_V0_1_ENVIRONMENT.md) |
| `GoalAccuracy-v0_2_1` | `FinalGoalAccuracyV0_2EnvCfg` 파생 | [실제 타겟 접촉만·timeout +75·매 reset 타겟 종류 재추첨](environments/FINAL_GOAL_ACCURACY_V0_2_1_ENVIRONMENT.md) |
| `GoalAccuracy-v0_2_2` | `FinalGoalAccuracyV0_2_1EnvCfg` 파생 | [물리 객체 12개·역할 공유·prototype/재질 재사용, 보유 형상 내 타겟 재선택](environments/FINAL_GOAL_ACCURACY_V0_2_2_ENVIRONMENT.md) |
| `GoalAccuracy-v0_3` | `FinalGoalAccuracyV0_2EnvCfg` 파생 | [3cm 목표·접촉 weight 1/4·최단 거리 갱신·timeout +100](environments/FINAL_GOAL_ACCURACY_V0_3_ENVIRONMENT.md); 부모 v0_2는 v0_1에 timeout +30 추가 |
| `GoalAccuracy-v1` | `FinalGoalAccuracyEnvCfg` 파생 | [1cm 고정 + 외곽 보상·goal speed 일정 복원, Final v1 대조](environments/FINAL_GOAL_ACCURACY_V1_ENVIRONMENT.md) |
| `v2` | `FinalV1EnvCfg` 파생 | 타겟 배치 영역 변경. [변형 비교](environments/FINAL_V1_V2_ENVIRONMENTS.md) |
| `Test-v2` | Final v2 파생 | 최종 장애물 개수로 시작. [변형 비교](environments/FINAL_V1_V2_ENVIRONMENTS.md) |

Holding → Final은 개발 흐름을 뜻한다. Final v0는 Holding EnvCfg를 직접 상속하지 않는다. Final 내부 버전의 직접 부모와 최종 활성 설정을 구분하여 확인한다.

2026-10-30: **GoalAccuracy v0·v1·v0_1·v0_2·v0_3 공통**으로 장애물 요청 수는 5000 iteration의 Gray 4·White 5가 상한이다. 이후 증가하지 않는다. Final v1 등 Accuracy 밖 환경은 기존 일정을 유지한다. [변경·검증 기록](logs/2026-10-30_goal_accuracy_population_cap.md).

## Holding — 기반 계열

아래 ID의 공통 접두사는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-`이다.

| ID 접미사 | EnvCfg 위치·상속 | 상세 안내 |
| --- | --- | --- |
| `v0` ~ `v4` | `envs/contact_sweep_clutter_fusion_holding_envs.py`; v1부터 직전 Holding 버전 상속 | [v0](environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V0_ENVIRONMENT.md), [v1](environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V1_ENVIRONMENT.md), [v2](environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V2_ENVIRONMENT.md), [v3](environments/FUSION_HOLDING_V3_FAMILY.md), [v4](environments/FUSION_HOLDING_V4_FAMILY.md) |
| `OSC-v0` ~ `OSC-v4` | `envs/contact_sweep_clutter_fusion_holding_osc_envs.py`; 각각 같은 번호 Holding 상속 | [OSC v0](environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_V0_ENVIRONMENT.md), [OSC v1](environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_V1_ENVIRONMENT.md), v2 이후는 해당 Holding 계열 설명 참조 |
| `OSC-ObjectRandom-v0` ~ `OSC-ObjectRandom-v3` | `envs/contact_sweep_clutter_fusion_holding_osc_object_random_envs.py`; 각각 OSC v0/v2/v3/v4 상속 | [v0](environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V0_ENVIRONMENT.md), [v1](environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V1_ENVIRONMENT.md), [v2](environments/FUSION_HOLDING_V3_FAMILY.md), [v3](environments/FUSION_HOLDING_V4_FAMILY.md) |
| `ObjectRandom-Test-v0` | ObjectRandom 계열 파일; Holding v2 상속 | [테스트 환경](environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OBJECT_RANDOM_TEST_V0_ENVIRONMENT.md) |

Holding v0의 외부 기반 클래스는 코드의 실제 MRO로 확인한다. 이전 계열 코드는 현재 환경의 의존성을 확인할 때만 읽는다.

## 실행

workspace 루트에서 Isaac Lab 의존성이 설치된 Python을 사용한다. 아래는 명령 예시이며 실행 성능 검증 결과가 아니다. 옵션과 설치 절차는 workspace 루트 `README.md`를 따른다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Final-GoalAccuracy-v0 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/play.py --task Isaac-Inspire-Final-GoalAccuracy-v0 --num_envs 16 --checkpoint /absolute/path/to/model.pt
```

학습에는 `train.py`를 사용한다. `train_resilient.py`는 사용 중단 상태로 보존한다. checkpoint의 환경·관측·정책 구성과 현재 task의 호환성을 확인한다.

## 수정·비교 기준

[개발 지침](../00_guidelines/09_DEVELOPMENT_GUIDE.md)에 따라 요청한 버전만 수정하고 부모를 보존한다. 목표 도달은 XY 거리 `d <= r`를 사용한다. 고정값과 커리큘럼 값, EEF 접근 반경을 혼동하지 않는다.

완료 전 등록·상속·Scene·Command·Event·Observation·Action·Reward·Termination·Curriculum·runtime·PPO·로그의 모든 차이를 요청과 대조한다. 특히 커리큘럼의 삭제·대상 term·시점·간격·최종값을 누락하지 않는다. 검증 명령과 미검증 범위는 해당 개발 로그에 남긴다.

이전 환경 목록과 상세 비교는 [정리 전 백업](history/2026-10-27_agent_context/README.md)에 보존했다. 과거 환경 조사 요청이 있을 때만 읽는다.
