# Revision · Holding · Final 환경 안내

2026-11-06 후속: Refactor의 Hand 관절속도 페널티는 원본 URDF 독립 구동6축만 합산하며 미믹6축을 제외한다. 계수·Arm비용·동작제어·관측·종료·커리큘럼은 유지한다.

2026-11-06 Refactor: Wrist3−π/2, Arm속도종료3rad/s. 실제GUI32환경 mass/readback·7168reset검증 및 좌우촉각시험은 [후속 검증 로그](logs/2026-11-06_wrench_refactor_gui_validation.md)를 따른다. 초기 GPU불가 기록은 sandbox 접근 제한으로 정정했다.

2026-11-05 **Inspire-Wrench-Refactor-v0 후속 수정**: 선반30kg 명시적 MassAPI, 오른손790g 및 관성 보정, EEF기준 OSC/Jacobian/속도, tactile.05N. CPU159개 통과. 문서의114파일을 빈 디렉토리에 복원하여 실제 config import/USD 검사 통과. [재구성 상세 명세](environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [소스 부록](environments/WRENCH_REFACTOR_V0_RECONSTRUCTION.md) · [검증 로그](logs/2026-11-05_wrench_refactor_mass_eef_spec.md). GPU물리 검증은 남아 있다.

2026-11-05: **`Inspire-Wrench-Refactor-v0`**는 기존 Wrench CFG/runtime 상속 없는 독립 구성이다. 오른손 원본,17물체 고정풀,34촉각,Actor/Critic 동일차원,연속 목표 균등 및 요청 보상/종료/커리큘럼을 적용했다. [환경 계약](environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [검증/미검증](logs/2026-11-05_wrench_refactor_v0_implementation.md). 실제 PhysX/학습은 NVIDIA driver 부재로 미검증이다.

2026-11-05: [**Wrench v0 계열 상세 명세**](environments/WRENCH_V0_FAMILY_ENVIRONMENTS.md)를 작성했다. v0~v0_4의 상속·Scene/reset·관측·pose OSC·전체 보상·커리큘럼·종료·PPO·로그 해석을 현재 코드로 대조했다. 접촉 weight0.1, Hand raw rate, 정규화 OSC 토크 rate의 상한/기대값 차이를 명시한다. 문서 작업이며 환경 코드·검증 상태는 변경하지 않았다.

2026-11-05: **Inspire-Wrench-v0_3 → v0_4 추가**. v0_2→v0_3→v0_4 직접 상속. v0_3은 Gray/White 각각0–4 균등 reset·population/free-speed 커리큘럼 제거·속도 기준0.02m/s·EEF14cm·OSC 출력 토크 정규화 변화량·최초 진입 무감쇠4cm/s다. v0_4는 높이 조건을 둔 Holding 최단 거리 개선량으로 교체하며 weight3.7을 유지한다. 실제 부모 접촉 weight0.1도 보존했다. CPU103개 통과, GPU/학습 미실행. [환경·검증 계약](environments/WRENCH_V0_3_V0_4_ENVIRONMENTS.md).

2026-11-05 후속: Wrench-v0_2 Contact Count를 최대10으로 제한하고 임시 print 블록 전체를 주석 처리했다. 접촉 인정·불인정5회 초기화 조건과 weight1.45는 유지한다. 기본dt0.02초에서 접촉 보상 상한은 step당0.29다. CPU89개 통과, GPU/play 미실행.

2026-11-05: **Inspire-Wrench-v0_2** 추가. v0 직접 상속, 접촉 조건 없는 cosine 거리 보상(3cm 미만1), 2-of-3 누적 접촉·불인정5회 초기화, −1/−1 장애물 기준에서2k 시작3k 교대·reset±1 랜덤화. CPU87개 통과, GPU/학습 미검증. [환경·검증 계약](environments/WRENCH_V0_2_ENVIRONMENT.md).

2026-11-04: **Inspire-Wrench-v0_1** 추가. v0 직접 상속, contact 제거·연속 접촉/각도 계수 거리 보상, 거리3cm 미만 alpha=1. Deadzone40° 고정, 목표 허용 거리4.0–7.5cm. CPU78개 통과, GPU/학습 미검증. [환경 계약](environments/WRENCH_V0_1_ENVIRONMENT.md) · [개발 기록](logs/2026-11-04_wrench_v0_1_implementation.md).

2026-11-04: **Inspire-Wrench-v2** 추가. v1 직접 상속, Arm 목표 ±10N/±0.5Nm·보정 후 제한 ±12N/±0.6Nm로1/10 축소. 범위 정규화 action-rate와 Hand/나머지 환경은 상속한다. CPU46개 통과, GPU 미검증. [v2 계약](environments/WRENCH_V0_V1_ENVIRONMENT.md#13-inspire-wrench-v2-v1의-arm-범위를110로-축소).

2026-11-04 문서 통합: [Wrench-v0 전체 명세와 v1 변경점](environments/WRENCH_V0_V1_ENVIRONMENT.md). 현재 코드 기준 랜덤화·관측·액션·15개 보상·커리큘럼·종료·PPO 및 sensor wrench 제어와 정규화 action-rate를 한 문서에 정리했다. 문서 작업이며 환경 코드 변경 없음.

2026-11-04 후속: Wrench-v1의 robot_action_rate_penalty는 Arm Desired Wrench를 정책 목표 범위로 정규화한 [-1,1] 변화량을 사용한다. Hand raw 계산과 계수는 유지하며 CPU44개 통과. v0는 보존했다.

2026-11-04: **`Inspire-Wrench-v1`**은 Wrench-v0 직접 상속이며 OSC만 F/T sensor 중심6축 closed-loop wrench 제어로 변경한다. `[wrench_abs]`, motion6축0, wrench6축1, feedback gain0.2, 명령축별목표 ±100N/±5Nm, 보정 후 명령 제한 ±120N/±6Nm이다. [참고 코드·파라미터·프레임·실행](environments/WRENCH_V1_ENVIRONMENT.md) · [검증 로그](logs/2026-11-04_wrench_v1_osc.md). CPU80개 통과, 실제 GPU 추종/학습은 미검증.

2026-11-04: **`Inspire-Wrench-v0`**는 Test-v2의 독립 후속 환경이다. 이전 환경 상속 없이 직접 구성하며 EEF120mm·연속3초 정지 성공/+75·RED 확장/Gray 후퇴·startup 랜덤화 분리·Dead Zone10k/3k를 적용한다. [전체 계약·실행](environments/WRENCH_V0_ENVIRONMENT.md) · [검증 로그](logs/2026-11-04_wrench_v0_implementation.md). CPU82개 통과, 실제 GPU collection1~2초는 미검증이다.

2026-11-04: `Revision-Test-v2`에 임시 종료 원인 print를 추가했다. `runtime/revision.py`의 `_reset_idx` TEMP 블록에서 환경 ID·step·발동 term 전체를 출력하며, Test-v2-GT·부모 환경은 제외한다. 종료 판정은 유지한다. 후속으로 `shelf_failure`·`object_fall_or_tilt` 함수의 TEMP 블록에서 매 제어 step 현재 값·임계값·개별 판정을 출력한다. 기존 play 프로세스를 재시작하면 적용된다.

활성 기반 패키지는 `src/inspire_sweep_baseline`이다. **2026-11-03 개발 대상은 Revision-v1을 상속한 Revision-v2 / Test-v2**이며, 기존 Holding → Final 환경은 비교·기존 학습 재현용으로 보존한다. `src/axia80_feasibility`는 현재 사용하지 않는다. 이 문서는 작업 대상을 찾는 색인이다. 수식·수치·실험 이력은 요청한 환경의 설명과 실제 코드만 확인한다.

요청 버전 비교: [Holding OSC·ObjectRandom·Final·Revision 9개 환경 비교](environments/HOLDING_FINAL_REVISION_NINE_ENV_COMPARISON.md)는 씬·관측·보상·커리큘럼·터미네이션·기타와 최종 요약 표를 현재 코드 기준으로 정리한다(2026-11-04).

## Revision — 독립 기반과 파생 환경

**Test-v2-GT(2026-11-03):** `Isaac-Inspire-Revision-Test-v2-GT`는 Test-v2 직접 파생이다. Actor에 Critic의 실시간 타겟 XYZ3D만 추가하고 기존 초기 타겟·초기 장애물 관측·Critic·보상·PPO를 보존한다. Actor 원시121→124D·MLP73→76D이며 새 학습용이다. [구현 계약](environments/REVISION_V2_ENVIRONMENT.md#test-v2-gt-실시간-타겟-위치-대조-실험) · [검증 기록](logs/2026-11-03_revision_v2_gt_implementation.md).

**구현(2026-11-03):** `Isaac-Inspire-Revision-v2` / `Isaac-Inspire-Revision-Test-v2`. v1→v2→Test 직접 상속, 거리·Hold·접촉 모두 EEF95mm 미만, Hold는 weight10·2.5~3.5cm Smoothstep·속도 감쇠 없음, 최초 진입은 높이 조건 없이 최대+25×속도 Gaussian 감쇠(free0.01·scale0.02m/s), timeout+75·free acceleration15m/s²다. 기존 속도 커리큘럼과 PPO gamma0.98을 유지한다. Test는 타겟 형상만 cylinder다. [구현 계약·실행](environments/REVISION_V2_ENVIRONMENT.md) · [개발·검증](logs/2026-11-03_revision_v2_implementation.md).

2026-11-03 계측 종료: Test-v1의 EEF 높이 print와90/95/100mm 시각화 면을 모두 주석 처리했다(설정·출력 블록·생성 호출·helper 전체). v2·Test-v2·Test-v2-GT도 활성 임시 계측 코드가 없음을 확인했다. [처리·검증 기록](logs/2026-11-02_revision_v1_implementation.md#2026-11-03-임시-높이-계측-주석-처리).

`Isaac-Inspire-Revision-v1`은 `RevisionV1EnvCfg(RevisionEnvCfg)`, `Isaac-Inspire-Revision-Test-v1`은 `RevisionV1TestEnvCfg(RevisionV1EnvCfg)`다. Test의 유일한 과업 설정 차이는 타겟 형상 cylinder 고정이며 크기·장애물 랜덤화는 유지한다. [v1 독립 상세 문서: 관측·행동·장면·15개 보상·종료·커리큘럼·PPO](environments/REVISION_V1_ENVIRONMENT.md) · [개발·리뷰·검증](logs/2026-11-02_revision_v1_implementation.md).

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
