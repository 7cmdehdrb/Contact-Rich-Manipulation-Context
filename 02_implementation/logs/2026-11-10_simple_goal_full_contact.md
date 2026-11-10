# 2026-11-10 Simple 목표 내부 접촉 풀 카운트

[환경 설명서](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md)

## 요청·의도와 변경 전후

사용자는 Simple-v0의 타겟이 목표 XY 거리3cm 미만일 때 항상 풀 카운트로 인정하고, Simple-v1/Hard-v0에도 상속 적용하도록 요청했다. 목표 도달 후에는 접촉을 유지하지 않더라도 해당 보상을 계속 받을 수 있게 하는 변경이다.

이전에는 목표 안에서도 실제 접촉2-of-3 인정과 EEF15cm 미만 조건을 만족해야 보상을 지급했다. 이제 Simple 전용 `GoalContactMaintenance`가 기존 `TargetContactDecayMaintenance`를 상속하며, XY 거리<0.03m이면 count와 term 출력 모두20, misses0으로 덮어쓴다. 접촉 여부·접촉 이력·센서 freshness·EEF 높이와 무관한 예외다. 유한 거리만 인정하며 정확히3cm는 제외한다. 목표와의 Z 차이는 사용하지 않는다.

범위 밖에서는 기존 +1/−2(0–20)와 불인정 보상0 규칙을 그대로 사용한다. 목표 내부에서 가짜 접촉 이력을 만들지 않는다. 목표를 벗어나 불인정이면20→18로 감소하고 보상0, 이후 실제 접촉으로 인정되면 잔여 count에서 증가한다. reset은 선택된 환경의 이력과 count를 초기화한다. 동일 step 중복 호출은 추가 증가/감소를 하지 않는다.

weight0.1과 policy dt0.02는 그대로이므로 목표 내부에서는 이 term이 step마다0.04를 기여한다. 목표에서 멀어짐 비용, 다른 보상, timeout 성공/실패 조건은 변경하지 않는다.

## 영향 범위와 전체 대조

`mdp/reward_functions/sweep_simple.py`를 추가하고 `mdp/rewards/sweep_simple.py`의 hand_contact callable만 교체했다. Simple-v0·Simple-v1·Simple-Hard-v0에 적용된다. Prof-v0·Prof-v1·Prof-Hard-v0는 hand_contact=None이라 영향이 없다. 과거 Relative-IK v0_2_2_4/6의 접촉 보상도 보존한다.

기존 Simple와 과거 환경의 전체 설정 대조는 이 의도된 callable 차이만 허용하도록 갱신했다. params·weight·나머지 Manager 구성·PPO·runtime 변경은 없다. 부모/자식 적용 범위를 별도로 검사했다. 기존 미커밋 작업·사용자 문서·학습 로그를 보존했다.

## 검증

`test_sweep_simple.py`, `test_sweep_simple_hard.py`, `test_wrench_refactor_relative_ik_test.py`, `test_fast_reset.py`를 CPU 환경에서 실행했다. 목표 중심/2.9cm/정확히3cm/3.1cm/NaN, 무접촉·높이 초과·stale sensor, 목표 이탈, 재접촉, 부분 reset, step cache, Prof/과거 환경 보존을 검증한다.

첫 실행의 경계 테스트에서 float32의0.03을 float64 상태에 대입하면서 실제 값이3cm보다 작아지는 테스트 데이터 문제가 있었다. 상태와 동일 dtype으로 경계값을 생성하도록 수정했다. 생산 코드의 strict `< .03` 비교는 유지했다.

최종 결과: **80 passed, 2 skipped**, 12.06초. skip은 opt-in 대규모 기하 stress와 native library 경로가 필요한 실제 USD IK 검사다. GPU/PhysX 학습 및 행동 효과는 이번 변경에서 검증하지 않는다.
