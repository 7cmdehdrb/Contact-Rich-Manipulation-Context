# 사용자 별도 발굴 논문 — 누적 목록

**최초 작성일: 2026-09-16 · 최근 갱신일: 2026-09-18**

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](README.md) · [전체 논문](../papers/README.md)

**상세 노트 바로가기:** [USER-P001 · Gentle Object Retraction](../papers/2026-brouwer-gentle-object-retraction.md) · [USER-P002 · Sim2Real Tactile Manipulation](../papers/2024-su-sim2real-tactile-manipulation.md)

## 1. 이 목록의 범위

이 문서는 **기존 일괄 문헌조사·제목 선별 때 수집된 후보군에 포함되지 않았으며, 이후 사용자가 별도로 찾아 제공한 논문**을 누적 관리한다. 논문의 주제별 비교 보고서가 아니라, 발굴 경로·서지·원문 확보·상세 정리 위치를 연결하는 목록이다.

기존 R1–R7이나 IROS-S01–S05에 새 논문을 억지로 편입하거나, 당시 조사 범위·후보 수·정독 상태를 소급 변경하지 않는다. 기존 목록의 논문을 사용자가 다시 지정한 경우에는 원래 식별자와 노트를 유지하며 별도 발굴 항목으로 중복 등록하지 않는다.

이 목록에 등록되었다는 사실은 논문이 특정 센서를 실제로 사용한다거나, RL 연구·SCIE 논문·Blind manipulation 연구라는 판정을 뜻하지 않는다. **사용자 제공, 원문 확보, 원문 정독, 코드 확인, 프로젝트 적용 판단은 별도 상태**로 관리한다.

## 2. 등록 목록

| 관리 ID | 등록일 | 논문·게재 정보 | 출처와 정독 상태 | 상세 정리 |
| --- | --- | --- | --- | --- |
| USER-P001 | 2026-09-16 | **Gentle Object Retraction in Dense Clutter Using Multimodal Force Sensing and Imitation Learning** — Brouwer et al., IEEE RA-L 11(2), 1578–1585, 2026. [DOI](https://doi.org/10.1109/LRA.2025.3643332) | 사용자 별도 발굴·출판본 PDF 제공. 8쪽 전체 정독 완료. Limitation·Future Work 포함. 코드·보충 영상 미확인 | [2026 · Brouwer et al.](../papers/2026-brouwer-gentle-object-retraction.md) |
| USER-P002 | 2026-09-18 | **Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning** — Su et al., arXiv:2403.12170v1, 2024-03-18. [v1 원문](https://arxiv.org/abs/2403.12170v1) | 사용자 별도 발굴·arXiv v1 PDF 제공. 8쪽 전체 정독 완료. 저자 명시 한계·향후 공개 계획 포함. 이후 출판본·코드 미확인 | [2024 · Su et al.](../papers/2024-su-sim2real-tactile-manipulation.md) |

현재 등록 2편, 첨부 원문 정독 완료 2편이다. 코드 실행·정책 재학습·실험 재현 완료 수를 뜻하지 않는다.

## 3. 등록 논문별 확인 내용

<a id="user-p001"></a>

### 3.1. USER-P001 — 확인된 내용과 분류 주의

**서지:** D. Brouwer, J. Citron, H. Nolte, J. Bohg, and M. Cutkosky, “Gentle Object Retraction in Dense Clutter Using Multimodal Force Sensing and Imitation Learning,” *IEEE Robotics and Automation Letters*, vol. 11, no. 2, pp. 1578–1585, Feb. 2026. DOI: [10.1109/LRA.2025.3643332](https://doi.org/10.1109/LRA.2025.3643332). 권·호의 게재연도는 2026이며 온라인 출판일은 2025-12-11이다. [첨부 출판본 첫 페이지]

고밀도 캐비닛에서 접촉을 활용해 빨간 목표를 찾아 흡착·인출하는 **실물 시연 기반 Diffusion Policy 연구**다. 실행 중 eye-in-hand vision, TCP pose, binary suction-pressure 관측을 사용하고, 여기에 관절 토크에서 추정한 wrench와 도구 양측의 분포형 3축 tactile을 제공하거나 masking하여 비교한다. **별도 손목 F/T 센서, RL 학습, GAN, 초기 시각 관측만을 사용하는 정책으로 분류하지 않는다.** [첨부 출판본 §III–V, PDF pp. 2–6]

100개 시연으로 네 정책을 학습하고, 같은 40개 신규 장면에서 평가한다. 병용의 전체 성공은 27/40으로 가장 높지만, 과도한 힘 실패는 두 단일 감각 정책보다 많고 완료 시간도 가장 짧지는 않다. ‘80% 향상’은 baseline 15/40 대비 **상대 개선**이다. 센서 사양, 힘 영상 매핑, impulse 기준, 결과의 해석 범위는 [상세 노트](../papers/2026-brouwer-gentle-object-retraction.md)에 기록했다. [첨부 출판본 §V–VII, Fig. 6–7, PDF pp. 5–7]

<a id="user-p002"></a>

### 3.2. USER-P002 — 확인된 내용과 분류 주의

**서지:** E. Su, C. Jia, Y. Qin, W. Zhou, A. Macaluso, B. Huang, and X. Wang, “Sim2Real Manipulation on Unknown Objects with Tactile-based Reinforcement Learning,” arXiv:2403.12170v1, 18 Mar. 2024. [제공 버전](https://arxiv.org/abs/2403.12170v1). 첨부 v1에 없는 학술대회·저널 게재 정보나 DOI는 이후 버전에서 보충하지 않았다.

두 손끝 DIGIT 영상을 **RGB·무접촉 기준 Diff·픽셀별 Binary**로 표현하여, 관절 고유감각·목표 각도와 함께 PPO에 제공하는 pivoting 연구다. Binary는 **각 센서의 64×64 접촉 패턴**이며 센서당 1비트가 아니다. 물체는 처음부터 잡고 있고 gripper width는 고정하며, 정책은 xz 평면 병진과 y축 회전을 제어한다. 제안 방법에 외부 object pose 추정·별도 F/T 입력·GAN은 없다. [첨부 v1 §III–IV, Fig. 1–2, PDF pp. 2–3]

시뮬레이션에서는 접촉력을 선형 매핑으로 변형 깊이에 연결한 뒤 Phong/PyTorch3D로 영상을 만든다. 원문이 주장하는 실물 학습 데이터 불필요와 별개로, 전처리에는 canonical image와 DIGIT별 threshold grid search가 있다. 정책 실물 fine-tuning 부재를 센서별 준비·조정 부재로 확대하지 않는다. [첨부 v1 §III, §V 도입, PDF pp. 2–4]

22개 훈련 물체와 16개 미지 실물 물체를 사용한다. Table I에서 비증강 RGB·Diff·Binary의 실물 성공률은 0.50·0.60·0.80이며, Binary(Aug)도 평균 성공률은 0.80이다. 성공 기준은 **angle deviation 15% 미만이지 15° 미만이 아니다**. Table I·II의 ± 불일치, 불완전 접촉 실패, SB3 기본값만 언급한 학습 설정과 누락된 angle reward 세부는 [상세 노트](../papers/2024-su-sim2real-tactile-manipulation.md)에 분리해 기록했다. 구체적인 후속 연구 확장 대신 환경·학습 코드 공개 계획만 명시한다. [첨부 v1 §IV–VI, Table I–III, PDF pp. 3–6]

## 4. 이후 추가·갱신 규칙

`USER-P001`, `USER-P002`, …처럼 **등록 순서의 고유 ID**를 부여한다. 이 번호는 우선순위나 논문 평가 점수가 아니며, R 번호·IROS-S 번호·논문 자체의 참고문헌 번호와 섞지 않는다. 등록 후 순서를 바꾸어도 ID를 재사용하거나 재번호화하지 않는다.

추가할 때 DOI와 제목·저자·연도를 먼저 대조하여 기존 노트가 있는지 확인한다. 다른 버전이나 중복 파일은 같은 논문의 기존 노트와 확인 범위·Git 이력으로 관리한다. 후속 연구 등 별개의 논문은 별도 항목으로 둔다.

정리 완료 전에는 확인한 수준에 따라 ‘서지만 제공’, ‘원문 확보·정독 대기’, ‘일부 원문 확인’ 등으로 상태를 적는다. 실제 정리 파일이 없으면 상세 정리 칸은 `—`로 두고 가짜 링크나 빈 노트를 만들지 않는다. 사용자 발굴 경위가 따로 제공되지 않았으면 사이트·검색어·발견일을 추정하지 않고 **등록일과 사용자 제공 사실**만 기록한다.

개별 상세 정리는 기존과 동일하게 `docs/literature/papers/게재연도-첫저자-주제.md`에 저장한다. 이 목록에는 서지·출처·상태와 짧은 확인 요지만 두고 상세 본문을 복제하지 않는다. 새 정리본을 추가할 때 이 목록, [조사 그룹 안내](README.md), [전체 논문 색인](../papers/README.md), [문헌 색인](../README.md)의 링크·상태를 함께 갱신한다. 상세 노트에는 이 목록의 해당 USER-P 항목으로 돌아오는 링크를 넣는다.

일괄 조사 목록과 나중에 중복되는 경우에도 원래 발굴 경로와 ID는 보존하고 상호 참조한다. 과거 조사본의 통계를 별도 근거 없이 수정하지 않는다. 단순히 논문을 정리했다는 이유로 프로젝트의 확정 방향·구현 성과·실험 상태를 바꾸지 않는다.

원문 PDF·저작권이 있는 그림 전체·사용자의 무관한 개인정보는 이 목록을 위해 저장소에 복제하지 않는다. 원문은 DOI 등 외부 위치로 연결하고, 상세 노트에 확인 버전·원문 hash·절·페이지 근거를 남긴다. 문서 작성은 [Markdown 형식 규칙](../../../.agents/rules/document-formatting.md)과 [개별 논문 정리 지침](../papers/README.md)을 따른다.

## 5. 변경 이력

| 날짜 | 변경 |
| --- | --- |
| 2026-09-16 | 누적 목록 생성. USER-P001 등록 및 원문 8쪽 상세 정리 연결. 기존 R1–R7·IROS-S01–S05 분류와 분리 |
| 2026-09-17 | 목록을 `reviews/user-found-papers.md`로 이동하고 조사 그룹 안내·상세 노트와 양방향으로 연결. 등록 ID와 기존 내용·정독 상태 유지 |
| 2026-09-18 | USER-P002 등록. arXiv:2403.12170v1 8쪽 상세 정리·고정 anchor·상단 바로가기와 색인 연결 추가. 기존 등록·조사 분류 유지 |
