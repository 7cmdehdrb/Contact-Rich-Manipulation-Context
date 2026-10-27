# 현재 개발 인계

[환경 안내](../02_implementation/08_ACTIVE_ENVIRONMENTS.md) · [개발 지침](../00_guidelines/09_DEVELOPMENT_GUIDE.md)

2026-10-27 사용자 지정 범위: **`src/inspire_sweep_baseline`이 기반 패키지이며 Holding → Final 계열이 최신 중점 환경**이다. 

- 과업: 선반 위 타겟을 목표 XY 위치로 밀며 촉각·손목 F/T를 사용하는 조작 정책을 학습한다. 초기 장면 정보와 실행 중 현재 상태의 Actor/Critic·보상 사용 범위는 대상 버전에서 확인한다.
- 개발 흐름: Holding → Holding OSC → Holding OSC ObjectRandom의 구성을 바탕으로 Final을 개발했다. 이는 개발 흐름이며 모두 직접 Python 상속 관계라는 뜻은 아니다. Final v0는 독립 구성이고, Final v1과 그 파생 환경이 현재 핵심 비교 대상이다.
- 요청 대상: Final-v1, v1-1, Test-v1, GoalAccuacy-v0, v2/Test-v2 등을 서로 혼동하지 않는다. 등록 ID와 부모를 실제 코드에서 확인한다.
- 2026-10-27 추가: [GoalAccuacy-v1](../02_implementation/environments/FINAL_GOAL_ACCUACY_V1_ENVIRONMENT.md)은 Accuracy v0를 상속해 1cm 고정 반경을 유지하며 외곽 goal_hold·goal_speed_scale을 복원한다. object_free_speed는 v0에서도 활성이다. Final v1과의 잔여 차이·검증 범위는 해당 명세를 따른다.
- 계약: 목표 도달은 `d <= r`. 직접 수정 요청은 해당 버전에 적용하고 새 파생 요청은 부모를 보존한다. 완료 전 모든 설정·함수·커리큘럼·로그 차이를 요청과 대조한다.
- 실행: `scripts/train.py`와 `scripts/play.py`를 사용한다. 검증 상태·상세 명령은 대상 환경 설명과 해당 개발 로그에서 확인한다.
