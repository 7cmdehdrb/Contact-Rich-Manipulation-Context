# Holding · Final 환경 안내

활성 기반 패키지는 `src/inspire_sweep_baseline`이며 **Holding → Final 계열이 가장 중요한 최신 환경**이다. `src/axia80_feasibility`는 현재 사용하지 않는다. 이 문서는 작업 대상을 찾는 색인이다. 수식·수치·실험 이력은 요청한 환경의 설명과 실제 코드만 확인한다.

## Final — 최신 중점

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
