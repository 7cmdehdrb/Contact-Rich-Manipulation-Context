# Prof Revision 정지·속도 종료 진단 기록

2026-11-24 사용자 요청으로 TEMP의 v0 model6100·Reach5cm model7950을 분석했다. 환경 소스·보상·등록·PPO·학습 로그는 보존하고, outputs/prof_revision_stop_diagnosis에 계측 실행기와 증거를 추가했다. 정상 정책은 각384episode, 팔 속도 종료만 해제한 진단은 각128episode를 완료했다.

목표 안에서 싼 속도 종료로 후속 손실을 끊는 구조는 지지되며, 큰 overshoot 후 역방향 비용을 받은 뒤 종료한다는 일반화는 지지되지 않는다. 팔 속도 종료 자체의 일회 비용은0이다. 정확한 수치·명령·변경 전후·초기 계측 실패와 재실행·검증 및 미검증 범위는 [실험 기록](../experiments/2026-11-24_prof_revision_stop_termination_diagnosis.md)에 남겼다.
