# 현재 개발 인계

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
