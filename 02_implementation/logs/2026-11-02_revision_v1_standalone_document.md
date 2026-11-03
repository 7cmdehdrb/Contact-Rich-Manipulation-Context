# Revision-v1 독립 상세 문서 작성

## 요청·범위

사용자는 `Isaac-Inspire-Revision-v1`의 관측·보상 등 환경 구성 전체를 설명하는 독립 문서를 요청했다. 기존 [Revision-v1 환경 문서](../environments/REVISION_V1_ENVIRONMENT.md)를 변경점 요약에서 최종 환경 전체 설명으로 확장했다. v0 문서나 개발 명세를 먼저 읽지 않아도 이해할 수 있도록 구성했다. 환경 소스·설정·학습 로그는 수정하지 않았다.

## 변경 전후와 근거

이전 문서는 v0 대비 변경점, v1/Test 상속 및 보상 weight 중심이었다. 새 문서는 일반 v1을 주제로 다음을 완결적으로 기술한다.

- 좌표계, 로봇 초기 자세, EEF 기준점, 접촉·F/T 센서와 noise 적용 경계.
- policy57D 각 인덱스·단위·frame·갱신 주기, Actor 초기 장애물64D, Critic 현재 타겟3D/장애물64D, 정렬·가시성·노이즈·encoder.
- 8D 행동, root 기준 상대 OSC, Hand 실제 openness와 명령의 차이, torque 제한.
- 8종 형상·scale, 물리 슬롯과 관측 슬롯, OBB 배치·부분 배치, reset 수명, episode 질량·마찰 분포.
- 15개 보상의 전체 수식과 weight/dt 처리, mask·cap·first-sample history, entry/timeout 경계와 동시 실패.
- 6개 종료, 3개 활성 커리큘럼, 고정 파라미터, PPO와 로그 해석·실행 명령.

Revision EnvCfg·Manager CFG·runtime과 실제 호출되는 공통 함수까지 대조했다. 특히 `shelf_penalty`는 단순 힘 비용으로 요약하지 않고 실제 선반 속도/손목 높이 predicate와 근접 비용을 설명했다. 목표 방향 제외각은 코드상3500에서 첫 감소임을 명시했다. Hold free speed0.05와 후반 target speed penalty free0.02는 별개임을 명시했다. 일반 v1의 `mass_cylinder` 이름은 타겟 형상 고정을 뜻하지 않는다.

## 검증

변경 문서의 Markdown 수식·상대 및 외부 workspace 링크 검사, docs `git diff --check`를 수행했다. 수식 표의 Hold16/8/1, 속도 감쇠1/0.5/0.0625, 사건30/40/70, dt0.02 비용 cap과 커리큘럼 보간값을 실제 함수식과 대조했다. 기존 구현 검증 결과는 구현 로그를 근거로 표시했으며 문서 작성 중 GPU나 학습을 새로 실행하지 않았다.

기존 환경 문서 경로를 유지하여 README·handoff·색인의 링크를 보존했다. 활성 환경 색인에 독립 상세 문서 범위를 표시하고 인계에 작성 사실을 추가했다. Test는 비교 설명1문단만 포함하며 본문의 모든 수치·관측은 일반 v1 기준이다.
