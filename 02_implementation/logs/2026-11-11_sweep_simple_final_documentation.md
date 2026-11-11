# Sweep Simple 최종 환경 문서 갱신

2026-11-11. [현재 환경 설명서](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md)

## 요청과 변경

사용자의 최종 환경 문서 갱신 요청에 따라 등록15개 환경 설명서를 현재 코드와 대조했다. 기존 Wrench/Test 상세 절과 상속도·ID표는 유지하고, 최신 추가 환경을 문서 상단에 명시했다. Finger9개 환경의 팔 제어·프레임·실행 Clip·Last Action·팔 속도 비용·종료 임계값을 한 표로 비교했다.

기존 공통 보존 계약의 OSC gains 설명에 Wrench 예외를 명시하고, Test와 Wrench가 독립적인 Finger-v0 자식임을 강조했다. Wrench의 센서 기준 액션과 EEF 기준 관측을 구분했다. v1의 정책 출력 자체가 제한되는 것으로 오해할 수 있는 요약을 실행 raw Clip으로 정정했다. v2 게이트 성공 조건이 Raw-v2에도 상속됨을 명시했다.

코드 위치 안내에 Wrench 모멘트 보정 및 Test 종료/커리큘럼 설정을 추가했다. 과거110/119개 CPU 검사와 최신 Test65개·Wrench67개 회귀 검사의 범위를 구분했다. 사용자 학습 현황 메모와 역사 개발 로그는 보존했다.

## 대조와 검증

`envs/sweep_simple_envs.py`, `mdp/actions/sweep_simple.py`, `mdp/terminations/sweep_simple.py`, `mdp/curricula/sweep_simple.py`의 직접 부모·OSC 모드·프레임·scale·종료 임계값·일정을 대조했다. 기존 구현 로그의 테스트 수와 미검증 범위를 확인했다. 문서 링크·수식 검사 및 diff 공백 검사를 수행했다.

문서만 수정했다. 환경 코드·체크포인트·학습 로그 변경 없음. 이번 작업에서 CPU 회귀나 GPU 학습을 재실행하지 않았고, 이전 검증 결과를 인용했다. GPU/PhysX 실행 미검증 상태는 유지된다.
