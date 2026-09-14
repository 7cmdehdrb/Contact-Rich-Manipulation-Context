# 연구 기록 템플릿

이 파일은 빈 양식이다. 아래 예시는 실행 결과가 아니다. 새 기록은 날짜와 ID를 가진 별도 Markdown 파일로 저장하고 관련 결정·코드·실험을 연결한다.

## 1. 실험 기록

```text
Experiment ID:
제목:
날짜:
상태: planned / running / completed / failed / blocked
질문 또는 검증할 가설:
연결된 결정/미정 ID:
근거 문서:

구현 저장소 / branch / commit:
환경·runner config:
실행 명령:
OS / Python / simulator / Isaac Lab / RSL-RL / ROS version:
checkpoint:
seed:
환경 수 / training steps / evaluation episodes:

태스크와 목표:
물체 / 질량 / geometry / 선반 / 마찰:
값의 출처: measured / manufacturer / assumed
접근·reset 분포:
초기 접촉 여부:

Actor 입력:
Critic 입력:
Reward에 쓰는 GT:
Evaluation에 쓰는 GT:
Oracle 정보 여부:
실제 종료 / oracle termination / 안전 감독의 구분:

센서 모델·위치·커버리지:
Raw 형상·단위·frame:
전처리·filter·normalization:
Timestamp / sampling / latency / validity:
Action 의미·차원·frame·scale:
Controller / hand mode:

비교 조건:
바꾼 변수:
고정한 변수:
Train/test 분리:

성공 정의와 임계값 근거:
측정 지표:
결과:
실패 사례:
안전 개입:
통계·불확실성:
원시 로그 / 가공 로그 / 영상 / plot 경로:

해석:
결과가 입증하지 못하는 것:
다음 변경:
```

## 2. 실패·장애 기록

```text
Failure ID:
날짜 / Experiment ID:
현상:
재현 조건:
최초 발생 시점:

실제로 관측한 사실:
확인하지 못한 항목:
현재 가설:

점검:
- 물리 연결·전원·장착:
- 센서 raw·유효 상태·timestamp:
- frame·단위·영점·부하 보정:
- controller·명령:
- observation·reward·termination:
- software/environment:

수정한 파일·설정:
수정 전후 차이:
검증한 테스트:
실행하지 못한 테스트:
정상 복구 여부:
되돌리는 방법:
근본 원인: confirmed / suspected / unknown
연구적 시사점:
```

원인 불명인데 정상 소프트웨어라고 단정하지 않는다. 반대로 원인 불명이라는 이유로 시스템 환경을 무작정 변경하지 않는다. 센서 사각지대와 통신 누락, 실제 접촉 실패와 정책 실패를 가능한 범위에서 분리한다.

## 3. 센서·접촉 확인 기록

```text
Sensor Test ID:
장비 정확한 모델 / firmware / 통신:
장착 상태·sensor frame:
Hand 자세 / 실제 접촉면:
센서 영역 ID·위치·방향·면적:
Raw Grid shape / 단위:
Scalar 또는 Boolean 축약 방식:

접촉 조건:
물체·선반 조건:
실제 접촉의 확인 방법:
F/T raw:
F/T 보정 후:
Tactile raw:
Tactile 전처리 후:
Robot state·action:
Timestamp·실제 수신 간격:
통신 validity / sample age:

접촉이 있는데 신호가 없는 경우:
무접촉인데 신호가 있는 경우:
실효 감지·noise 판단 근거:
시뮬레이션 모델과 차이:
가정으로만 남는 항목:
```

평가용 실제 접촉 위치·물체 ID를 actor 입력으로 복사하지 않는다. 감지 threshold는 이 기록 또는 별도 근거와 연결한다.

## 4. 미팅·결정 기록

```text
Meeting ID / 날짜:
대상: 석사생 1 / 공통 기반 / 별도 프로젝트
원본 또는 정리본 위치:
자료 성격: 원본 STT / 미팅 정리 / 대화 메모

학생이 제시한 안:
교수 또는 사용자의 피드백:
실제로 합의한 방향:
검증된 실험 사실:
정리자의 해석:

기존 결정을 대체하는 내용:
유지되는 내용:
보류되는 내용:
미정 사항:
다음 과제:
완료 기준:
갱신할 결정 ID와 문서:
```

최종 제안이라는 제목만으로 합의로 올리지 않는다. 다른 학생·환경 자동화·CU 논의는 본 연구에 직접 영향을 주는 부분만 분리해 연결한다.

## 5. 에이전트 작업 인계

```text
작업 날짜:
사용자 요청:
읽은 문서와 코드:
기준 commit:

요청 범위:
확인한 현재 상태:
이번에 수행한 변경:
생성·수정한 파일:
테스트 결과:
실행하지 못한 것과 이유:
새로 확인된 사실:
제안만 한 사항:
미해결 ID:

다음 에이전트가 먼저 할 일:
현재 하지 말아야 할 일:
되돌리기 또는 이어가기 기준:
결과 commit / 로그:
```
