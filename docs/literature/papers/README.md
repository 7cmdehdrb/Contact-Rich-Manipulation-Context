# 개별 논문 원문 정독 노트

[문헌조사 자료](../README.md) · [2026-09-14 종합 조사본](../reviews/2026-09-14_blind-sweep-force-torque-tactile.md)

이 폴더는 제공된 논문 원문을 읽고 **그 논문 자체의 문제 상황, 관련 연구, 환경·센서, 핵심 메소드, 실험과 한계**를 정리하는 곳이다. 여러 논문을 비교하거나 프로젝트 적용안을 제안하는 `reviews/`와 구분한다. 개별 노트에는 별도 연구 주제에 억지로 대응시킨 설명을 넣지 않는다.

## 원문 정독 진행 현황

기준일: 2026-09-14. `R1`–`R7`은 위 종합 조사본에서 부여한 식별자다. 다른 조사본의 같은 번호와 혼용하지 않는다. 아래 제목은 해당 조사본과의 대응을 위한 것이다.

| ID | 논문 | 이번 원문 정독 작업의 상태 | 상세 노트 |
| --- | --- | --- | --- |
| R1 | Force Push: Robust Single-Point Pushing With Force Feedback | 이번 작업용 원문 미제공 | — |
| R2 | Pushing in the Dark: A Reactive Pushing Strategy for Mobile Robots Using Tactile Feedback | 제공된 출판본 PDF 8쪽 전체 정독·정리 완료 | [2024 · Ozdamar et al.](2024-ozdamar-pushing-in-the-dark.md) |
| R3 | Pose-and-shear-based tactile servoing | 이번 작업용 원문 미제공 | — |
| R4 | Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing | 이번 작업용 원문 미제공 | — |
| R5 | Tactile Gym 2.0: Sim-to-Real Deep Reinforcement Learning for Comparing Low-Cost High-Resolution Robot Touch | 이번 작업용 원문 미제공 | — |
| R6 | Bi-Touch: Bimanual Tactile Manipulation With Sim-to-Real Deep Reinforcement Learning | 이번 작업용 원문 미제공 | — |
| R7 | Framework for Robot Door Opening Based on Visual, Force, and Tactile Integration | 이번 작업용 원문 미제공 | — |

‘이번 작업용 원문 미제공’은 새로 요청된 첨부 원문 기반 정독 작업의 상태다. 이전 종합 조사에서 어떤 출처도 읽지 않았다는 의미는 아니다. 정독 완료 역시 논문의 코드 실행·실험 재현 완료를 뜻하지 않는다. 제공되지 않은 논문에 빈 노트나 내용이 있는 것처럼 보이는 링크를 만들지 않는다.

## 공통 정리 구조

| 항목 | 기록 내용 |
| --- | --- |
| 논문 정보·출처 | 제목, 저자, 게재 정보, DOI, 읽은 버전·페이지, 확인하지 않은 자료 |
| 제시하는 문제 상황 | 저자들의 동기와 실제 해결 과업, 가정, 범위 밖의 목표 |
| Related Works | 원문이 구성한 비교 구도. 독립 절이 없으면 해당 내용을 담은 절을 명시 |
| 환경·센서 | 로봇, 과업 환경, 센서 원리·배치·측정량, 시뮬레이션/실물의 차이 |
| 힘·접촉 처리 | raw signal → 전처리 → 특징·상태 → 행동의 연결. 힘 측정과 접촉 위치 검출을 구분 |
| 핵심 메소드 | 수식의 변수·좌표계, 제어·정책 구조, 상태 전환, 명령·종료 조건 |
| 실험·결과 | 조건, 비교군, 지표, 수치, 그 결과가 뒷받침하는 범위 |
| 한계·미명시 사항 | 저자들이 남긴 후속 과제, 원문만으로 확인할 수 없는 구현 정보, 표기 불일치 |
| 원문 위치 | 절·페이지·식·그림·표 번호를 연결하여 다시 확인할 수 있게 기록 |

관련 연구는 해당 논문의 설명을 정리한 것인지, 인용된 선행논문을 별도로 읽은 것인지 구분한다. 본문 수식을 대수적으로 풀어 설명할 때에는 원문 식의 해설임을 밝힌다. 미기재 파라미터·센서 사양·성능값을 임의로 보완하지 않는다.

## 파일 관리

파일명은 `게재연도-첫저자-논문주제.md`를 사용한다. R 번호는 기존 종합 조사본에 종속되므로 파일의 고유 이름으로 사용하지 않는다. 동일 논문의 보완·정정은 해당 파일과 Git 이력으로 관리하고, 새 원문을 정리할 때 이 색인의 상태와 링크를 함께 갱신한다.

원문 PDF는 이 저장소에 복제하지 않는다. DOI 등 원문 위치와 확인한 파일의 해시를 노트에 남긴다. 자료를 읽었다는 이유로 프로젝트 결정·구현·실험 상태를 변경하지 않는다.
