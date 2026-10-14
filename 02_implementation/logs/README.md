# 개발·실험 진행 로그

[문서 안내](../../01_plan/README.md) · [현재 상태](../07_CODE_AND_HARDWARE_STATUS.md) · [현재 활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [로그 작성 지침](../../00_guidelines/09_DEVELOPMENT_GUIDE.md)

| 기록일 | 문서 | 기록의 범위 |
| --- | --- | --- |
| 2026-10-09 | [OSC와 Hand 이식 진행](1009.md) | Reach·Sweep 실패 관찰, 참고 환경의 Hand 교체·2D action·센서·무거운 물체 확장 |
| 2026-10-10 | [무거운 물체·센서·도달 스킵 환경](1010.md) | 참고 환경 변형의 구현·CPU 검증, 목표 높이·정렬축 수정 |
| 2026-10-12 | [Inspire Hand 단계별 학습 기록](2026-10-12_inspire_hand_training.md) | 원격에 추가된 Hand·센서·관측 제한별 학습 보고와 후속 검증; [구현·검증 TODO](../../01_plan/TODO.md) |
| 2026-10-12 | [당시 src Hand 환경과 재생 명령](1012_src_robot_hand_environments.md) | 현재 보관된 12개 환경의 당시 구성, 저장 설정·checkpoint 비교; 이번 정리의 활성 목록과 구분 |
| 2026-10-12 | [당시 최신 checkpoint와 재생 명령](1012_latest_checkpoints_play.md) | 10월 12일까지 확인한 모델 경로·차원·재생 옵션; 파일 존재가 정책 성공을 입증하지 않음 |
| 2026-10-14 | [Workspace 정리](2026-10-14_workspace_cleanup.md) | 활성 범위·보관 이동·문서 역할 정리와 검증 |
| 2026-10-14 | [문서 네 폴더 재구성](2026-10-14_document_reorganization.md) | 지침·계획·실제 코드 기록·정적 자산 분류, 내부·workspace·CSV/XLSX 참조와 검증 |
| 2026-10-14 | [Baseline 환경 UML](2026-10-14_inspire_sweep_uml.md) | Isaac Lab·PPO 실행 연결, 환경 Cfg 상속·callable 연결과 HTML 검증 |

새 기록은 `YYYY-MM-DD_<topic>.md` 형식으로 만든다. 환경의 상속 관계·전체 task ID·실행 명령·기준 commit·변경과 검증·미확인 항목을 남긴다. 실험 조건과 정량 결과는 `02_implementation/experiments/`에 연결하고, 연구 방향의 변화는 결정·brief·다음 작업 문서도 갱신한다. 과거 로그의 당시 결론은 유지하며 새 관찰은 새 날짜의 기록으로 추가한다.

Pull/rebase 중 문서 이관 충돌의 처리 내역은 [충돌 해결 기록](2026-10-14_rebase_conflict_resolution.md)에 남겼다.
