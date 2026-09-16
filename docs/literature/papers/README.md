# 개별 논문 원문 정독 노트

[문헌조사 자료](../README.md) · [2026-09-14 종합 조사본](../reviews/2026-09-14_blind-sweep-force-torque-tactile.md)

이 폴더는 제공된 논문 원문을 읽고 **그 논문 자체의 문제 상황, 관련 연구, 환경·센서, 핵심 메소드, 실험, 저자들이 밝힌 Limitation과 Future Work**를 정리하는 곳이다. 여러 논문을 비교하거나 프로젝트 적용안을 제안하는 `reviews/`와 구분한다. 개별 노트에는 별도 연구 주제에 억지로 대응시킨 설명을 넣지 않는다.

## 원문 정독 진행 현황

기준일: 2026-09-16. `R1`–`R7`은 위 종합 조사본에서 부여한 식별자다. 다른 조사본의 같은 번호와 혼용하지 않는다. 아래 제목은 해당 조사본과의 대응을 위한 것이다.

| ID | 논문 | 이번 원문 정독 작업의 상태 | 상세 노트 |
| --- | --- | --- | --- |
| R1 | Force Push: Robust Single-Point Pushing With Force Feedback | 제공된 출판본 PDF 8쪽 전체 정독·정리 완료 | [2024 · Heins & Schoellig](2024-heins-force-push.md) |
| R2 | Pushing in the Dark: A Reactive Pushing Strategy for Mobile Robots Using Tactile Feedback | 제공된 출판본 PDF 8쪽 전체 정독·정리 완료 | [2024 · Ozdamar et al.](2024-ozdamar-pushing-in-the-dark.md) |
| R3 | Pose-and-shear-based tactile servoing | 제공된 출판본 PDF 32쪽, 본문·Appendix A–D 정독·정리 완료 | [2024 · Lloyd & Lepora](2024-lloyd-pose-and-shear-based-tactile-servoing.md) |
| R4 | Sim-to-Real Model-Based and Model-Free Deep Reinforcement Learning for Tactile Pushing | 제공된 출판본 PDF 8쪽 전체 정독·정리 완료 | [2023 · Yang et al.](2023-yang-sim-to-real-tactile-pushing.md) |
| R5 | Tactile Gym 2.0: Sim-to-Real Deep Reinforcement Learning for Comparing Low-Cost High-Resolution Robot Touch | 제공된 출판본 PDF 8쪽 전체 정독·정리 완료. Limitation·Future Work 포함 | [2022 · Lin et al.](2022-lin-tactile-gym-2-0.md) |
| R6 | Bi-Touch: Bimanual Tactile Manipulation With Sim-to-Real Deep Reinforcement Learning | 제공된 출판본 PDF 8쪽 전체 정독·정리 완료. Limitation·Future Work 포함 | [2023 · Lin et al.](2023-lin-bi-touch.md) |
| R7 | Framework for Robot Door Opening Based on Visual, Force, and Tactile Integration | 제공된 출판본 PDF 19쪽, 본문·Appendix A–B 정독·정리 완료. Limitation·Future Work 포함 | [2026 · Šimundić et al.](2026-simundic-visuo-force-tactile-door-opening.md) |

‘이번 작업용 원문 미제공’은 새로 요청된 첨부 원문 기반 정독 작업의 상태다. 이전 종합 조사에서 어떤 출처도 읽지 않았다는 의미는 아니다. 정독 완료 역시 논문의 코드 실행·실험 재현 완료를 뜻하지 않는다. 제공되지 않은 논문에 빈 노트나 내용이 있는 것처럼 보이는 링크를 만들지 않는다.

## IROS 2023–2025 후속 사용자 임시 선정

기준일: 2026-09-16. 아래 목록은 [IROS 제목 선별 보고서 §11](../reviews/2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md#11-사용자-임시-선정-및-후속-원문-정독--2026-09-16-추가)의 사용자 임시 선정 5편이다. `IROS-S01`–`IROS-S05`는 위 `R1`–`R7`과 별개이며, 임시 선정은 직접적인 과업 적합성이나 센서·RL 사용의 검증 완료를 뜻하지 않는다. 번호는 사용자 목록의 순서다.

| ID | 논문 | 원문 정독 상태 | 상세 노트 |
| --- | --- | --- | --- |
| IROS-S01 | Attention for Robot Touch: Tactile Saliency Prediction for Robust Sim-to-Real Tactile Control | 제공된 출판본 PDF 7쪽 전체 정독·정리 완료. Limitation·Future Work 포함 | [2023 · Lin et al.](2023-lin-attention-for-robot-touch.md) |
| IROS-S02 | Disambiguate Gripper State in Grasp-Based Tasks: Pseudo-Tactile as Feedback Enables Pure Simulation Learning | 제공된 출판본 PDF 8쪽 전체 정독·정리 완료. 저자 명시 제약·Future Work 확인 결과 포함 | [2025 · Yang et al.](2025-yang-pseudo-tactile-gripper-state.md) |
| IROS-S03 | Learning Goal-Directed Object Pushing in Cluttered Scenes With Location-Based Attention | 제공된 출판본 PDF 7쪽 전체 정독·정리 완료. 저자 명시 제약·Future Work 확인 결과 포함 | [2025 · Dengler et al.](2025-dengler-location-based-attention-pushing.md) |
| IROS-S04 | Multi-Fingered Dragging of Unknown Objects and Orientations Using Distributed Tactile Information Through Vision-Transformer and LSTM | 이번 후속 정독용 원문 미제공 | — |
| IROS-S05 | Tactile Active Inference Reinforcement Learning for Efficient Robotic Manipulation Skill Acquisition | 제공된 출판본 PDF 6쪽 전체 정독·정리 완료. 저자 명시 제약·Future Work 확인 결과 포함 | [2024 · Liu et al.](2024-liu-tactile-active-inference-rl.md) |

## 사용자 별도 발굴 논문

기존 일괄 조사 후보군에 없었으며 사용자가 별도로 제공한 논문은 [별도 발굴 누적 목록](../collections/user-found-papers.md)에 등록한다. 아래 `USER-P` 식별자는 R1–R7·IROS-S01–S05와 독립적이며, 등록 경로를 나타낼 뿐 방법론·연구 적합성의 확정을 뜻하지 않는다.

| ID | 논문 | 원문 정독 상태 | 상세 노트 |
| --- | --- | --- | --- |
| USER-P001 | Gentle Object Retraction in Dense Clutter Using Multimodal Force Sensing and Imitation Learning | 제공된 출판본 PDF 8쪽 전체 정독·정리 완료. Limitation·Future Work 포함 | [2026 · Brouwer et al.](2026-brouwer-gentle-object-retraction.md) |

## 공통 정리 구조

| 항목 | 기록 내용 |
| --- | --- |
| 논문 정보·출처 | 제목, 저자, 게재 정보, DOI, 읽은 버전·페이지, 확인하지 않은 자료 |
| 제시하는 문제 상황 | 저자들의 동기와 실제 해결 과업, 가정, 범위 밖의 목표 |
| Related Works | 원문이 구성한 비교 구도. 독립 절이 없으면 해당 내용을 담은 절을 명시 |
| 환경·센서 | 로봇·제어 DOF, 과업 환경, 센서 원리·배치·측정량. 원문에 명시된 최대 측정 범위·분해능·공간 해상도·정확도·감도·주파수·커버리지와 로봇 상세 사양을 기록하고, 장비 사양·실험 설정·시뮬레이션/실물을 구분 |
| 힘·접촉 처리 | raw signal → 전처리 → 특징·상태 → 행동의 연결. 힘 측정과 접촉 위치 검출을 구분 |
| 핵심 메소드 | 수식의 변수·좌표계, 제어·정책 구조, 상태 전환, 명령·종료 조건 |
| 실험·결과 | 조건, 비교군, 지표, 수치, 그 결과가 뒷받침하는 범위 |
| Limitation — 저자들이 밝힌 한계 | 저자들이 명시한 방법·실험·적용 범위의 한계와 그 조건·이유. 원문 위치를 함께 기록 |
| Future Work — 저자들이 제시한 향후 연구 | 저자들이 제안한 개선·확장 방향과 해결할 후속 과제. 계획과 구현·검증된 성과를 구분하고 원문 위치를 기록 |
| 미명시 사항·원문 주의사항 | 원문만으로 확인할 수 없는 구현 정보·사양, 표기 불일치. 저자 명시 한계와 구분 |
| 원문 위치 | 절·페이지·식·그림·표 번호를 연결하여 다시 확인할 수 있게 기록 |

관련 연구는 해당 논문의 설명을 정리한 것인지, 인용된 선행논문을 별도로 읽은 것인지 구분한다. 본문 수식을 대수적으로 풀어 설명할 때에는 원문 식의 해설임을 밝힌다. 미기재 파라미터·센서 사양·성능값을 임의로 보완하지 않는다.

센서의 해상도·최대 측정 범위 등이 원문에 없으면 ‘미명시’로 남긴다. 제어용 접촉 threshold를 센서 최소 검출 성능으로, admittance threshold를 최대 측정 범위로, 실험 측정 제공률을 제조사 최대 샘플링률로 바꾸어 기록하지 않는다. 외부 데이터시트는 별도로 확인한 경우에만 별도 출처로 구분한다.

문서 형식은 [최신 Markdown 규칙](../../../.agents/rules/document-formatting.md)을 따른다. 현재 규칙은 블록 수식을 별도 줄의 `$$`로, 인라인 수식을 `$…$`로 작성하며, 수식용 코드 펜스와 백틱을 섞은 인라인 수식을 사용하지 않는다. 원문 식 번호는 블록 밖에 표시하고, 구문 검사와 렌더링 확인 범위를 기록한다. 로컬 검사 통과와 실제 GitHub 웹페이지 표시 확인을 구분한다.

## Limitation 및 Future Work 정리 기준

**2026-09-15 사용자 지시에 따라 추가한 필수 항목이다. 이후 새로 작성하는 논문 정리부터 적용하며, 이미 완료한 R1–R4 정리본과 기존 종합 조사본은 이번 지침 변경의 소급 수정 대상에서 제외한다.** 기존 정리 상태를 미완료로 바꾸거나 이 항목 추가를 위해 과거 문서를 일괄 수정하지 않는다.

Limitation과 Future Work를 각각 식별 가능한 항목 또는 하위 절로 구분한다. 독립된 Limitation/Future Work 절이 없더라도 Discussion, Conclusion 및 다른 본문에 저자들이 명시한 내용을 확인하고, 실제 근거가 있는 절·페이지를 기록한다. 한계와 후속 과제의 연결은 저자들이 설명한 범위 안에서 정리한다.

저자들이 밝힌 한계와 정리자가 발견한 미명시 정보·표기 불일치·추론을 섞지 않는다. 정리자의 비판이나 프로젝트 적용안을 저자들의 Limitation 또는 Future Work로 바꾸어 서술하지 않는다. 향후 계획·가능성·기대는 이미 구현하거나 검증한 성과와 구분한다.

해당 항목을 원문에서 찾을 수 없으면 ‘원문에 명시된 Limitation 없음’ 또는 ‘원문에 명시된 Future Work 없음’으로 기록한다. 이는 연구에 한계나 향후 과제가 전혀 없다는 뜻이 아니다. 원문 일부만 확인한 경우에는 미확인 범위를 표시하고, 전체 원문에 해당 내용이 없다고 단정하지 않는다.

## 파일 관리

파일명은 `게재연도-첫저자-논문주제.md`를 사용한다. R 번호는 기존 종합 조사본에 종속되므로 파일의 고유 이름으로 사용하지 않는다. 동일 논문의 보완·정정은 해당 파일과 Git 이력으로 관리하고, 새 원문을 정리할 때 이 색인의 상태와 링크를 함께 갱신한다.

원문 PDF는 이 저장소에 복제하지 않는다. DOI 등 원문 위치와 확인한 파일의 해시를 노트에 남긴다. 자료를 읽었다는 이유로 프로젝트 결정·구현·실험 상태를 변경하지 않는다.
