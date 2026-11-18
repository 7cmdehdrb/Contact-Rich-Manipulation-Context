# Prof-v2 · Finger-ForceDirection-v0 상세 문서 작성

2026-11-14. [상세 명세](../environments/SWEEP_PROF_V2_AND_FINGER_FORCE_DIRECTION_V0.md) · [Simple 전체 안내](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md)

## 요청·의도

사용자는 두 환경의 구성 방법, Scene 구성과 랜덤화 방법/대상, 관측, 보상을 중심으로 상세 문서를 요청했다. 여러 버전의 변경 이력에서 현재 계약을 조합하지 않아도 두 환경을 직접 이해할 수 있는 문서를 작성했다.

## 변경 전후와 영향

기존 Simple 전체 문서는 17개 ID의 공통 기반과 파생 변경 이력을 설명했다. 새 상세 명세는 요청된 두 환경만 대상으로 실제 활성 구성을 모아 설명한다. 전체 안내와 활성 환경 안내, 개발 로그 색인에서 연결했다. 코드·등록 ID·보상·시뮬레이션·학습 로그는 수정하지 않았다.

## 최종 대조

- Gym/EnvCfg/runtime/PPO 상속과 Prof-v2의 손 6축 변경을 대조했다.
- 생성 시 종류·크기 고정, startup 질량/마찰, 매 reset 배치·목표·IK·관측 오차를 분리했다. 다른 환경의 reset 물성 함수가 활성인 것으로 기재하지 않았다.
- policy 66D + obstacles 64D, 초기 위치 스냅샷과 실시간 센서, Actor/Critic 공통 입력, 현재 손목 관측 Clip을 확인했다.
- Runner Clip 위치·scale 후 범위·Last Action과 최종 손 목표의 차이를 기록했다.
- Reaching의 초기 root 거리 예산과 현재 BBOX 중심 거리, Prof step 접근과 Finger 최고 기록 접근, signed cosine 3D 분모를 대조했다.
- 접촉 유지/Prof/힘 방향의 서로 다른 접촉 센서 집계·이력·높이 조건을 구분했다.
- 12cm 높이, 1cm 보상 예외, 3cm 성공, `<`와 `≤` 경계 차이를 기록했다.
- action-rate 무상한과 다른 비용의 기존 상한·wrench 5% 예산을 구분했다.

## 검증

- 변경 Markdown 5개 수식 검사: 통과.
- 변경 문서 링크 검사(`--check-external`): 내부 링크 249개·외부 workspace 링크 15개, 오류 0.
- 전체 문서 링크 검사: Markdown 586개, 오류 0.
- 문서 저장소 `git diff --check`: 통과.
- 최종 정적 재대조: 최고 기록 접근 수식, 목표 추출 범위, force sample 유효 판정과 접촉 이력 조건 확인.

현재 코드의 정적 대조와 문서 검사 범위다. 이번 작업에서 CPU 동작 테스트·GPU 물리·학습·시각 렌더링은 실행하지 않았다. 이전 구현 로그의 smoke 검증은 링크로 연결하며 장기 수렴이나 정확도 개선의 증거로 확대하지 않았다.
