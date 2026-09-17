# 조사 그룹 안내

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](../papers/README.md)

각 조사 보고서의 상단에서 논문별 상세 노트로 이동할 수 있다. 아직 개별 노트가 없는 논문은 **상세 노트 미작성**으로 표시한다. 보고서 안의 요약·원문 확인과 첨부 원문(PDF) 전체 정독은 서로 다른 기록이다.

## 조사별로 찾기

| 조사 그룹 | 대상과 식별자 | 상세 정리로 바로 이동 |
| --- | --- | --- |
| [Blind Sweep의 F/T·촉각 Pushing](2026-09-14_blind-sweep-force-torque-tactile.md) | 2026-09-14 조사, R1–R7 | [Force Push](../papers/2024-heins-force-push.md) · [Pushing in the Dark](../papers/2024-ozdamar-pushing-in-the-dark.md) · [Pose/Shear Servoing](../papers/2024-lloyd-pose-and-shear-based-tactile-servoing.md) · [Tactile Pushing RL](../papers/2023-yang-sim-to-real-tactile-pushing.md) · [Tactile Gym 2.0](../papers/2022-lin-tactile-gym-2-0.md) · [Bi-Touch](../papers/2023-lin-bi-touch.md) · [Door Opening](../papers/2026-simundic-visuo-force-tactile-door-opening.md) |
| [IROS 2023–2025 제목 선별·후속 정독](2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md) | 2026-09-15 조사, 후속 선정 IROS-S01–S05 | [Attention for Robot Touch](../papers/2023-lin-attention-for-robot-touch.md) · [Pseudo-Tactile](../papers/2025-yang-pseudo-tactile-gripper-state.md) · [Location-Based Pushing](../papers/2025-dengler-location-based-attention-pushing.md) · [Tactile-AIRL](../papers/2024-liu-tactile-active-inference-rl.md). S04: 상세 노트 미작성 |
| [Binary Tactile·F/T 기반 RL](2026-09-16_binary-tactile-wrench-rl.md) | 2026-09-16 조사, B1–B4·W1–W4·C1 | [B1 · DexTouch](../papers/2024-lee-dextouch.md) · [B3 · Rotating without Seeing](../papers/2023-yin-rotating-without-seeing.md). 다른 항목은 보고서의 비교표·요약 참조 |
| [사용자 발굴 논문](user-found-papers.md) | 등록일별 누적, USER-P 식별자 | [USER-P001 · Gentle Object Retraction](../papers/2026-brouwer-gentle-object-retraction.md) |

논문 제목은 [전체 논문 색인](../papers/README.md)에서도 검색할 수 있다. R·IROS-S·B/W/C·USER-P는 각 조사·목록에서 부여한 식별자이며, 새로운 논문 순위나 재분류가 아니다.

## 조사에서 나온 설계 제안

| 문서 | 근거 조사 | 읽을 때의 구분 |
| --- | --- | --- |
| [Binary Tactile·Wrench 입력 처리 및 비교 실험 제안](2026-09-16_binary-tactile-wrench-design-notes.md) | [Binary Tactile·F/T 조사](2026-09-16_binary-tactile-wrench-rl.md) | PROPOSED. 문헌의 방법과 프로젝트에 대한 제안을 구분하며, 구현 완료·최종 사양으로 읽지 않음 |
| [힘·촉각 기반 Sweeping — 9월 18일 미팅 검토 자료](2026-09-17_force-tactile-sweeping-meeting.md) | [F/T·촉각 Pushing 조사](2026-09-14_blind-sweep-force-torque-tactile.md) · [Binary Tactile·F/T 조사](2026-09-16_binary-tactile-wrench-rl.md) | 기존 접근과 적용 후보·검토 이유를 정리한 논의 자료. 확정 사양·미팅 결과와 구분 |

## 추가·갱신 원칙

새 논문 노트는 `../papers/`에 하나만 만들고, 이 안내의 해당 그룹·원래 보고서의 논문 항목·[전체 논문 색인](../papers/README.md)에서 같은 파일로 연결한다. 상세 노트 상단에는 원래 보고서의 논문 위치로 돌아가는 링크를 둔다. 전체 절차는 [문서 연결 관리](../README.md#literature-navigation)를 따른다.

사용자 발굴 목록은 이 폴더의 [user-found-papers.md](user-found-papers.md)에서 관리한다. 별도 폴더나 상세 본문 복사본을 추가하지 않는다.
