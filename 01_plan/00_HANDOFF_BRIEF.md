# 현재 개발 인계

2026-11-06: **Inspire-Wrench-Refactor-v1** 추가. v0직접상속,접촉유지보상제거·현재step접촉조건부거리보상weight25. [계약](../02_implementation/environments/WRENCH_REFACTOR_V1_ENVIRONMENT.md).

2026-11-06 후속: Refactor의 Hand 관절속도 페널티는 원본 URDF 독립 구동6축만 합산하며 미믹6축을 제외한다. 계수·Arm비용·동작제어·관측·종료·커리큘럼은 유지한다.

2026-11-06 **Refactor GUI32환경 검증 완료**: startup event 인자 오류·주차 물체 중력 갱신/wake 오류 수정. 최종7168배치에서 공중낙하 없음, 주차 drift3.82µm,140만goal방위 편향 검출 없음. 사용자 후속으로 Wrist3−π/2·Arm속도종료3rad/s. 최종32/32목표도달,21/32안정유지성공,실패0. 왼쪽앞면ch0/오른쪽뒷면ch17·접촉F/T약1.2N을확인했다. [시험·실패 이력](../02_implementation/logs/2026-11-06_wrench_refactor_gui_validation.md). 초기 “GPU driver부재”는 sandbox 접근 제한 오판으로 정정한다.

2026-11-05 Refactor 후속: 선반30kg MassAPI 생성 순서 수정, 오른손 공식 촉각형 총790g에 mass/inertia 비례 보정, EEF task frame·Jacobian·velocity 통일, tactile.05N. CPU159개 및 문서에서114파일 복원/import/USD 검사 통과. GPU물리 미검증. [상세 명세](../02_implementation/environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [변경/검증 기록](../02_implementation/logs/2026-11-05_wrench_refactor_mass_eef_spec.md).

2026-11-05: **`Inspire-Wrench-Refactor-v0` 독립 CFG/runtime 추가**. 오른손 ZIP 원본·실제17물체(8종×2장애물+원통타겟), 초기 물성 고정/높이 캐시·reset0–3/0–3, 방향/조건부 거리 균등, 앞뒤 tactile34, Actor/Critic raw74/MLP90을 구성했다. 출력 토크 정규화·목표 내부도 EEF14cm 제한·거리weight5·진입+15·speed/acceleration 제거를 반영했다. CPU/오른손USD/실제 설정 import 통과, GPU driver 부재로 PhysX/학습 미검증. [전체 계약](../02_implementation/environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [검증 로그](../02_implementation/logs/2026-11-05_wrench_refactor_v0_implementation.md).

2026-11-05: [**Wrench v0 계열 상세 명세**](../02_implementation/environments/WRENCH_V0_FAMILY_ENVIRONMENTS.md)를 작성했다. v0~v0_4의 상속·Scene/reset·관측·pose OSC·전체 보상·커리큘럼·종료·PPO·로그 해석을 현재 코드로 대조했다. 접촉 weight0.1, Hand raw rate, 정규화 OSC 토크 rate의 상한/기대값 차이를 명시한다. 문서 작업이며 환경 코드·검증 상태는 변경하지 않았다.

2026-11-05: **Inspire-Wrench-v0_3 → v0_4 추가**. v0_2→v0_3→v0_4 직접 상속. v0_3은 Gray/White 각각0–4 균등 reset·population/free-speed 커리큘럼 제거·속도 기준0.02m/s·EEF14cm·OSC 출력 토크 정규화 변화량·최초 진입 무감쇠4cm/s다. v0_4는 높이 조건을 둔 Holding 최단 거리 개선량으로 교체하며 weight3.7을 유지한다. 실제 부모 접촉 weight0.1도 보존했다. CPU103개 통과, GPU/학습 미실행. [환경·검증 계약](../02_implementation/environments/WRENCH_V0_3_V0_4_ENVIRONMENTS.md).

2026-11-05 후속: Wrench-v0_2 Contact Count를 최대10으로 제한하고 임시 print 블록 전체를 주석 처리했다. 접촉 인정·불인정5회 초기화 조건과 weight1.45는 유지한다. 기본dt0.02초에서 접촉 보상 상한은 step당0.29다. CPU89개 통과, GPU/play 미실행.

2026-11-05: **Inspire-Wrench-v0_2** 추가. v0 직접 상속, 접촉 조건 없는 cosine 거리 보상(3cm 미만1), 2-of-3 누적 접촉·불인정5회 초기화, −1/−1 장애물 기준에서2k 시작3k 교대·reset±1 랜덤화. CPU87개 통과, GPU/학습 미검증. [환경·검증 계약](../02_implementation/environments/WRENCH_V0_2_ENVIRONMENT.md).

2026-11-04: **Inspire-Wrench-v0_1** 추가. v0 직접 상속, 독립 contact 보상 제거·거리 보상에 연속 접촉과 signed cosine 적용. 사용자 후속 지시로 거리3cm 미만 alpha=1, 기존 높이/계수 유지. Deadzone40° 고정·목표 허용 거리4.0–7.5cm. CPU78개 통과, GPU/학습 미검증. [환경 계약](../02_implementation/environments/WRENCH_V0_1_ENVIRONMENT.md) · [개발 기록](../02_implementation/logs/2026-11-04_wrench_v0_1_implementation.md).

2026-11-04: **Inspire-Wrench-v2** 추가. v1 직접 상속, Arm 목표 ±10N/±0.5Nm·보정 후 제한 ±12N/±0.6Nm로1/10 축소. 범위 정규화 action-rate와 Hand/나머지 환경은 상속한다. CPU46개 통과, GPU 미검증. [v2 계약](../02_implementation/environments/WRENCH_V0_V1_ENVIRONMENT.md#13-inspire-wrench-v2-v1의-arm-범위를110로-축소).

2026-11-04 문서 통합: [Wrench-v0 전체 명세와 v1 변경점](../02_implementation/environments/WRENCH_V0_V1_ENVIRONMENT.md). 현재 코드 기준 랜덤화·관측·액션·15개 보상·커리큘럼·종료·PPO 및 sensor wrench 제어와 정규화 action-rate를 한 문서에 정리했다. 문서 작업이며 환경 코드 변경 없음.

2026-11-04 후속: Wrench-v1의 robot_action_rate_penalty는 Arm Desired Wrench를 정책 목표 범위로 정규화한 [-1,1] 변화량을 사용한다. Hand raw 계산과 계수는 유지하며 CPU44개 통과. v0는 보존했다.

2026-11-04: **`Inspire-Wrench-v1` 추가, v0 보존**. v0 직접 상속, OSC만 sensor-center6축 closed-loop wrench로 변경했다. `wrench_abs`, motion0/wrench1, P gain0.2, 목표 ±100N/±5Nm, 보정 후 명령 제한 ±120N/±6Nm, gravity True. 기본 Isaac OSC의 force3D-only 제한 때문에 full6D F/T feedback/J-transpose 경로를 로컬 구현했다. 기존 Scene·관측/보상 EEF frame·PPO 수치는 유지한다. CPU80개 통과, GPU 접촉 추종/학습·gain 안정성은 미검증. [환경·참고 구현·파라미터](../02_implementation/environments/WRENCH_V1_ENVIRONMENT.md) · [개발 기록](../02_implementation/logs/2026-11-04_wrench_v1_osc.md).

2026-11-04: **`Inspire-Wrench-v0` 독립 환경 추가**. Test-v2를 의미론적 기준으로 삼되 EnvCfg/runtime/Scene/Manager/PPO 설정 상속은 끊었다. EEF120mm·3cm/0.005m/s 연속3초 success termination/+75, RED20mm 확장·후방 Gray20mm 후퇴, startup 배치 bank·물성 고정, Dead Zone10k 첫−5°/이후3k 간격이다. CPU82개 통과·CUDA4개 skip. GPU 드라이버 불가로 실제 초기화/rollout/PPO와 collection1~2초는 미검증. [환경 계약](../02_implementation/environments/WRENCH_V0_ENVIRONMENT.md) · [구현·검증 로그](../02_implementation/logs/2026-11-04_wrench_v0_implementation.md).

2026-11-04: `Revision-Test-v2`에 임시 종료 원인 print를 추가했다. `runtime/revision.py`의 `_reset_idx` TEMP 블록에서 환경 ID·step·발동 term 전체를 출력하며, Test-v2-GT·부모 환경은 제외한다. 종료 판정은 유지한다. 후속으로 `shelf_failure`·`object_fall_or_tilt` 함수의 TEMP 블록에서 매 제어 step 현재 값·임계값·개별 판정을 출력한다. 기존 play 프로세스를 재시작하면 적용된다.

- 2026-11-03 **Test-v1 임시 계측 비활성화**: EEF 높이 print 설정·분기,90/95/100mm 시각화 생성 호출·helper 전체를 주석 처리했다. v2·Test-v2·Test-v2-GT에는 활성 출력·면 생성 코드가 없다. 보상 계산은 보존했으며 CPU회귀20개 통과. [기록](../02_implementation/logs/2026-11-02_revision_v1_implementation.md#2026-11-03-임시-높이-계측-주석-처리).

- 2026-11-03 **Test-v2-GT 추가**: `Isaac-Inspire-Revision-Test-v2-GT`, Test-v2 직접 상속. Actor에 기존 Critic의 noise-free root-frame 타겟 XYZ3D를 추가한다. Actor 초기 장애물·초기 타겟 정보와 Critic·보상·PPO는 유지한다. Actor 원시124D·MLP76D, GT 전용 새 학습용이다. CPU33개, GPU64 env32step·부분reset·JIT, PPO2iterations·checkpoint·GT 입력 가중치 갱신을 확인했다. [구현 계약](../02_implementation/environments/REVISION_V2_ENVIRONMENT.md#test-v2-gt-실시간-타겟-위치-대조-실험) · [검증 상태](../02_implementation/logs/2026-11-03_revision_v2_gt_implementation.md).

- 2026-11-03 **Revision-v2 / Test-v2 구현·smoke 완료**: [구현 계약](../02_implementation/environments/REVISION_V2_ENVIRONMENT.md). v1→v2→Test 직접 상속, 거리·Hold·접촉 EEF95mm 미만, Hold weight10·2.5~3.5cm Smoothstep·속도 감쇠 제거, 최초 진입 최대+25×속도 감쇠(free0.01·scale0.02m/s, 높이 무관), timeout+75, free acceleration15m/s²다. 최초 진입은 지급액과 무관하게 기회를 소진한다. 기존 속도 커리큘럼·PPO gamma0.98·부모 정의를 유지했다. Test는 타겟만 원통이며 임시 높이 출력·면은 포함하지 않는다. CPU86개, v2 GPU64/2048·Test64 rollout/부분reset, 실제 EEF·접촉·Hold 지급액, train.py PPO2iterations(v2 2048/Test64)와 유한 checkpoint·두 encoder 갱신 검증을 통과했다. 실제 검증 상태·명령·산출물은 [개발 로그](../02_implementation/logs/2026-11-03_revision_v2_implementation.md)를 따른다. 장기 성능은 미검증.

- 2026-11-02 **Revision-v1 독립 상세 문서 확장**: [환경 상세](../02_implementation/environments/REVISION_V1_ENVIRONMENT.md)에 Actor/Critic 관측 채널·noise·frame, 8D 제어, 형상/물성/reset, 15개 보상 수식·dt·경계, 종료·커리큘럼·PPO를 완결적으로 정리했다. 코드 변경·추가 GPU 실행 없음. [작성 기록](../02_implementation/logs/2026-11-02_revision_v1_standalone_document.md).

- 2026-11-02 **Revision-v1 / Revision-Test-v1 구현·리뷰·smoke 완료**: [구현 계약](../02_implementation/environments/REVISION_V1_ENVIRONMENT.md). v0→v1→Test 직접 상속, object 비용3분리, wrist budget 제거·cap 유지, 7개 schedule 정확한10k 값 고정, 장애물3/3→10k3/4→12k4/4→14k4/5, 3cm 내부 Gaussian Hold·5cm/s 무감쇠, 최초 진입+30/timeout+40을 구현했다. Test는 타겟 kind만 cylinder이며 scale·장애물 난수열을 보존했다. CPU111개, v1 GPU64/2048·Test64 초기화/rollout/부분reset, 실제70/40/30 지급·자동reset, train.py PPO2iterations(v1 2048/Test64)를 통과했다. 두 축 리뷰 잔여 지적0건. [개발·검증 기록](../02_implementation/logs/2026-11-02_revision_v1_implementation.md). 장기 성공률·정밀정지 개선은 미검증. `play.py`는 실행하지 않았고 `logs/rsl_rl`은 보존했다. [기존 개발 명세·그래프](environments/2026-11-02_REVISION_V1_SPEC.md)의 미구현 표기는 설계 당시 상태다.

- 2026-11-01 **독립 Revision-v0 구현**: 최신 사용자 지시에 따라 `Isaac-Inspire-Revision-v0`를 새로 등록했다. 기능 기준은 v0_2이며 기존 Final/Holding CFG·runtime 상속 없이 직접 구성했다. 기존 환경은 보존했다. [Revision 명세](../02_implementation/environments/REVISION_V0_ENVIRONMENT.md) · [구현·리뷰·검증 로그](../02_implementation/logs/2026-11-01_revision_v0_implementation.md).
- 중앙 크기 기준 단일 ±10%, 물리 물체 10개, Gray 65mm 고정 OBB 배치, Actor121D/Critic124D(별도 실시간 장애물), 성공3cm/Hold8cm, 실제 접촉 AND 고정 EEF 높이120mm를 적용했다. 120mm는 8종 기준 높이 평균118.1546mm 및 실제 손 collider의 바닥 여유를 기준으로 정했다. 종류·크기는 생성 시 고정하고 reset마다 배치·활성 구성을 바꾼다.
- CPU20개, 64 env의 8종×정확한 크기 양끝, 2048 env 초기화·sparse/dense35step·부분reset6회, `train.py` 2048 env PPO2iterations 및 유한 체크포인트·두 인코더 갱신 검증을 통과했다. PhysX found/lost aggregate pair 버퍼를 `2**28`에서 기본 `2**25`로 조정했다. 실제 PhysX 접촉 fixture도 EEF 약97~98mm에서 보상1, 약148.5mm에서 보상0을 확인했고 낮은 자세의 손 바닥 여유는 약37mm였다. 학습 후 상부 누르기 감소·장기 성능은 검증하지 않았다. 실험 범위와 재현 명령은 위 개발 로그를 따른다. 산출물은 `outputs/revision_validation`, `outputs/revision_training`에 있으며 `logs/rsl_rl`은 수정하지 않았다.

아래는 Revision 구현 전 요구 확정과 기존 환경의 이력이다.

- 2026-11-01 **최종 8항목 대조·계획 정정, 코드 미반영**: [통합 수정 예정](FINAL_YCB_SIZE_RANDOMIZATION_FIX.md)을 사용자 최종 의도에 맞춰 재작성했다. **v0_2 기준·v0_2_1 구현 참고 금지**는 유지한다. 이전 계획의 원통 알고리즘·size_fraction=1.0 기준·필수 1/8 균등/매 reset 전부 재추출·고정 125 mm 임계값은 이번 정정으로 대체한다.
- 배치 기준은 `outputs/bbox_scene_layout`의 **OBB 기반 텐서 배치**, 독립 구현 `mdp/common/bbox_scene_layout.py`다. `wrist_downward_v2`는 선행 원통 알고리즘이며 적용 대상으로 잘못 특정했던 설명을 정정했다. **Gray 패딩 65 mm 고정·패딩 커리큘럼 삭제**, 장애물 개수 커리큘럼 Gray 1~4 / White 1~5는 유지한다.
- 크기는 기존 YCB 3단계 0.8/0.9/1.0의 **중앙 0.9를 새 기준 크기**로 삼고 Mesh·에셋 모두 각 기준 대비 U(0.9,1.1)을 한 번 적용한다. 타겟·장애물 모두 8종 사용 가능하며 특별한 reset 방식은 강제하지 않는다. 다양한 종류·크기·배치 경험과 scale 반영 바닥 정렬을 검증한다.
- 관측은 조인트→EEF→초기 타겟→목표→이전 행동→센서→장애물 순서, 실제 Arm 값·Hand 2D·16슬롯을 유지한다. Critic은 현재 타겟 3D와 **실제 배치된 활성 장애물만** 현재 좌표로 관측한다. 미사용·주차 후보 제외, 가시성 필터/반전 없음. 기존 정렬·10% 인접 교환 유지, Critic 노이즈/갱신 주기는 구현 시 명시한다.
- 성공 3 cm·Hold 외곽 8 cm·접촉 AND 고정 EEF 높이 제한 계획을 유지한다. **높이는 중앙 크기 반영 후 평균을 재계산하고 바닥 충돌/상부 누르기를 함께 확인해 확정**한다. 공중 스폰·발사·비타겟 bbox 표시·과다 사전 등록을 재발 방지 항목으로 기록했다. **실제 2048 env 초기화·reset·rollout·짧은 학습 검증**이 필요하며 layout benchmark로 대체하지 않는다. 과거 구현 이력은 아래에 보존한다.

- 2026-10-31 추가: [GoalAccuracy v0_2_2](../02_implementation/environments/FINAL_GOAL_ACCURACY_V0_2_2_ENVIRONMENT.md)는 v0_2_1의 새 직계 파생이다. 물리 객체 36→12, prototype cache·전역 물리 재질 공유·텐서 역할 재할당을 사용한다. 기존 환경 정의 42개는 AST 대조로 보존을 확인했다. 보상·관측·OBB 규칙·Gray 4/White 5 일정은 유지하지만 환경별 초기 보유 형상이 고정되어 reset 간 종류 분포의 상관은 달라진다. CPU 109개 및 GPU 4/64 env 반복 reset 검증 통과. 원래 선반 서버가 응답하지 않아 GPU 실행은 로컬 대체 선반을 사용했으며 학습·대규모 collection은 미검증이다. [구현·비교 기록](../02_implementation/logs/2026-10-31_final_v0_2_2_compact_scene.md).

- 2026-10-31 후속 적용: 사용자 요청으로 [OBB 배치 규칙](../02_implementation/environments/BBOX_SCENE_LAYOUT.md)을 **FinalGoalAccuracyV0_2_1EnvCfg reset에 연결**했다. Gray 2500 / White 2000부터 각 1000마다 증가, 4/5 상한 유지. 최소 간격 20mm, Gray 바깥 padding 60→69mm. 주석 처리된 타겟 풀 Scene도 runtime 계약에 맞춰 복원했다. 회귀·기하 106개와 GPU 2 env의 부분 reset 40회·타겟 16종 검사 통과. 다른 환경은 유지하며 학습·대규모 collection은 미검증. [연결·검증 기록](../02_implementation/logs/2026-10-31_final_v0_2_1_obb_reset.md).

- 2026-10-31 구현: [GoalAccuracy v0_2_1 계약](../02_implementation/environments/FINAL_GOAL_ACCURACY_V0_2_1_ENVIRONMENT.md). v0_2 직계 파생으로 실제 타겟 접촉만 보상, timeout +75(2cm 경계 포함), 매 reset 기존 분포에서 타겟 종류를 재추첨한다. CPU 78개 및 GPU 2 env / 부분 reset 40회 / 전체 16후보 검사 통과. 고정 풀 때문에 물리 물체가 21→36개로 증가한다. 비선택 후보는 원격 배치·중력 해제·논리 제외하며 collider flag는 유지한다. 대규모 성능과 학습은 미검증. [개발·검증 기록](../02_implementation/logs/2026-10-31_final_goal_accuracy_v0_2_1_implementation.md).

[환경 안내](../02_implementation/08_ACTIVE_ENVIRONMENTS.md) · [개발 지침](../00_guidelines/09_DEVELOPMENT_GUIDE.md)

2026-10-27 사용자 지정 범위: **`src/inspire_sweep_baseline`이 기반 패키지이며 Holding → Final 계열이 최신 중점 환경**이다. 

- 과업: 선반 위 타겟을 목표 XY 위치로 밀며 촉각·손목 F/T를 사용하는 조작 정책을 학습한다. 초기 장면 정보와 실행 중 현재 상태의 Actor/Critic·보상 사용 범위는 대상 버전에서 확인한다.
- 개발 흐름: Holding → Holding OSC → Holding OSC ObjectRandom의 구성을 바탕으로 Final을 개발했다. 이는 개발 흐름이며 모두 직접 Python 상속 관계라는 뜻은 아니다. Final v0는 독립 구성이고, Final v1과 그 파생 환경이 현재 핵심 비교 대상이다.
- 요청 대상: Final-v1, v1-1, Test-v1, GoalAccuracy-v0, v2/Test-v2 등을 서로 혼동하지 않는다. 등록 ID와 부모를 실제 코드에서 확인한다.
- 2026-10-27 추가: [GoalAccuracy-v1](../02_implementation/environments/FINAL_GOAL_ACCURACY_V1_ENVIRONMENT.md)은 Accuracy v0를 상속해 1cm 고정 반경을 유지하며 외곽 goal_hold·goal_speed_scale을 복원한다. object_free_speed는 v0에서도 활성이다. Final v1과의 잔여 차이·검증 범위는 해당 명세를 따른다.
- 계약: 목표 도달은 `d <= r`. 직접 수정 요청은 해당 버전에 적용하고 새 파생 요청은 부모를 보존한다. 완료 전 모든 설정·함수·커리큘럼·로그 차이를 요청과 대조한다.
- 실행: `scripts/train.py`와 `scripts/play.py`를 사용한다. 검증 상태·상세 명령은 대상 환경 설명과 해당 개발 로그에서 확인한다.

- 2026-10-30 후속: [Accuracy 물체 수 상한 변경](../02_implementation/logs/2026-10-30_goal_accuracy_population_cap.md). 공통 부모 및 모든 하위 환경(v0·v1·v0_1·v0_2·v0_3)의 최종 장애물 요청 수를 **Gray 4·White 5**로 고정했다. 5000 iteration까지 기존 일정, 이후 추가 증가 없음. 물체 용량·관측 슬롯·Gray padding 등 다른 설정은 유지한다.

- 2026-10-30: 수락된 [Accuracy v0_3 개발 명세](environments/2026-10-30_FINAL_GOAL_ACCURACY_V0_3_SPEC.md)대로 v0_2를 직접 상속하여 구현했다. 접촉 OR 목표 점유 유지·weight 1/4, 최단 거리 갱신 보상·허용 거리 0·weight 100, timeout +100, 목표 반경 3cm다. [구현 계약](../02_implementation/environments/FINAL_GOAL_ACCURACY_V0_3_ENVIRONMENT.md)에 CPU·실제 설정 검증과 독립 리뷰 결과를 기록했다. GPU 부재로 실제 물리·학습은 미검증이다. Reaching은 현재 부모 코드 10cm를 보존한다.

- 2026-10-28: [Accuracy v0_1 구현 계약](../02_implementation/environments/FINAL_GOAL_ACCURACY_V0_1_ENVIRONMENT.md)을 추가했다. v0를 상속하여 2cm 목표, 타겟 Contact, 고정 20cm Reaching, 6cm 외곽 Hold, 지수 거리 weight 3.7, 0.06×0.08×0.10m 큐브 타겟을 적용한다. 기존 ±10% 크기 랜덤화와 reset은 유지한다. Manager 이름은 [개발 사양 8.3절](environments/2026-10-28_FINAL_GOAL_ACCURACY_V0_1_REWARD_SPEC.md)의 대상별 명칭으로 교정했다. 기존 v0/v1은 Gym ID의 Accuacy→Accuracy 이름만 교정하고 동작은 보존했다. 설정·USD·CPU 검증과 미완료 물리 검증을 구현 로그에서 구분한다.
