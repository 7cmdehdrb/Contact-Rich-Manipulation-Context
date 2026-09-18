# 문헌조사 자료

이 디렉터리는 **초기 시각 관측 이후 힘·토크와 촉각으로 수행하는 Blind Sweeping**의 선행연구 조사 자료를 관리한다. 프로젝트의 현재 결정·미정 사양을 보관하는 인계 문서와, 논문 분석 및 연구 제안을 구분한다.

[문서 안내](../README.md) · [조사 그룹](reviews/README.md) · [전체 논문](papers/README.md) · [에이전트 지침](../../AGENTS.md) · [현재 결정](../03_DECISIONS_AND_OPEN_QUESTIONS.md)

## 보고서 색인

[조사 그룹 안내](reviews/README.md)에는 각 보고서와 그 안의 상세 논문 노트를 함께 모았다. 아래 보고서에서도 상단의 논문 바로가기를 이용할 수 있다.

| 조사 기준일 | 보고서 | 범위와 읽을 때의 주의 |
| --- | --- | --- |
| 2026-09-14 | [Blind Sweep을 위한 F/T·촉각 기반 Pushing 문헌 조사](reviews/2026-09-14_blind-sweep-force-torque-tactile.md) | 2022년 이후 SCIE 저널을 대상으로 한 선별 조사. F/T, tactile, 병용을 구분하고 관측→표현→행동의 연결을 비교한다. 직접 pushing과 인접 과업, 원문 확인 범위와 한계를 구분한다. |
| 2026-09-15 | [IROS 2023–2025 Tactile·F/T 기반 RL 관련 논문 제목 선별](reviews/2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md) | 제공된 연도별 CSV의 제목 레코드 4,762건, 고유 제목 4,761개를 의미 기반으로 1차 선별했다. 엄격 일치와 원문 확인 후보를 구분하며, 센서 사용·RL 채택·성과는 원문 검증 전까지 미확정이다. 2026-09-16 사용자 임시 선정 5편과 후속 정독 현황을 §11에 추가했다. |
| 2026-09-16 | [Binary Tactile·F/T 기반 RL 신규 문헌 조사](reviews/2026-09-16_binary-tactile-wrench-rl.md) | 기존 발견 문헌을 제외한 주요 참고 5편·제한적 방법 참고 3편과 Binary 정보 손실 반대 근거 1편. 저항식 센서 이진화, history, force/wrench의 관측·보상·action·controller 연결을 비교한다. RL/POMDP/IL, 실물/sim-only, 직접 pushing/인접 과업을 구분한다. |
| 2026-09-16 | [Binary Tactile·Wrench 입력 처리 및 비교 실험 제안](reviews/2026-09-16_binary-tactile-wrench-design-notes.md) | 위 신규 조사에서 도출한 PROPOSED 문서. 필터·영역 축약·threshold·hysteresis·validity, wrench 보정·좌표계·정규화, actor/critic 경계와 동일 조건의 센서 표현 비교를 구체화한다. 구현·최종 사양·장비 실측 결과가 아니다. |
| 2026-09-17 | [힘·촉각 기반 Sweeping: 선행연구 검토와 적용 방향](reviews/2026-09-17_force-tactile-sweeping-meeting.md) | 9월 18일 미팅 검토 자료. 기존 연구의 접근 → 적용 후보 → 검토 이유를 촉각·F/T·RL 결합·보상별로 정리한다. 확정 사양이나 미팅 결과가 아니며, 상세 노트가 있는 논문은 해당 문서로 연결한다. |
| 2026-09-18 | [Research Motivation 보강: 신규 문헌에서 본 축약 촉각의 보완 구조](reviews/2026-09-18_reduced-tactile-compensation-survey.md) | 기존 저장소에 없던 신규 문헌 4편을 Sider Scholar로 발굴해 비교. Pose·Shape 제공 조건, Binary/저차원 tactile과 함께 쓰는 load·proprioception·history·kinematic prior·privileged information을 분리해 정리한다. |
| 2026-09-16부터 누적 | [사용자 발굴 논문](reviews/user-found-papers.md) | 사용자가 별도로 제공한 논문의 등록·서지·정독 상태와 상세 노트. USER-P 식별자를 유지하며 조사 그룹의 하나로 관리한다. |

2026-09-14 보고서의 **7–8절은 문헌에서 도출한 해석·연구 제안**이다. 프로젝트의 확정 사양이나 구현 성과로 승격하지 않는다. 각 논문의 본래 목적, 센서 구성, 시각 사용 조건, 제어 방식, 적용 한계는 보고서 본문과 참고문헌을 함께 확인한다. 특정 범주의 직접 사례를 확보하지 못했다는 사실은 그 연구가 존재하지 않는다는 증명이나 신규성 확정이 아니다.

## 개별 논문 원문 정독

종합 비교와 별도로, 제공된 원문을 상세히 읽은 기록은 [개별 논문 색인](papers/README.md)에서 관리한다. 이 노트는 **각 논문 자체의 문제·Related Works·환경·센서·메소드**를 설명하며, 프로젝트 적용안은 포함하지 않는다. 특히 힘·접촉 신호의 전처리와 제어 연결, 수식·상태 전환, 실험 조건을 원문 위치와 함께 기록한다.

| 정리일 | 기존 조사본 ID | 논문·상세 정리 |
| --- | --- | --- |
| 2026-09-14 | R1 | [Force Push — 힘 평활화·조향·접촉 복구·admittance·QP IK·장비 사양과 실험](papers/2024-heins-force-push.md) |
| 2026-09-14 | R2 | [Pushing in the Dark — 정전용량 접촉 검출부터 RPS 속도 제어·재정렬·실험까지](papers/2024-ozdamar-pushing-in-the-dark.md) |
| 2026-09-15 | R3 | [Pose-and-shear-based tactile servoing — TacTip 사양·GDN·SE(3) Bayesian filter·과업별 제어와 부록](papers/2024-lloyd-pose-and-shear-based-tactile-servoing.md) |
| 2026-09-15 | R4 | [Sim-to-Real Tactile Pushing — GAN·PoseNet·관측/보상·SAC·PETS/MPC·장비 사양과 실험](papers/2023-yang-sim-to-real-tactile-pushing.md) |
| 2026-09-15 | R5 | [Tactile Gym 2.0 — 세 센서의 접촉 특성·영상 변환·PPO·하중 실험·한계와 향후 연구](papers/2022-lin-tactile-gym-2-0.md) |
| 2026-09-16 | R6 | [Bi-Touch — 양팔 촉각·과업별 reward·압착 문제·GUM·curriculum·한계와 향후 연구](papers/2023-lin-bi-touch.md) |
| 2026-09-16 | R7 | [Handleless Door Opening — 힘·촉각 실패 검출·카메라 보정·접촉/miss 제약·재계획·한계와 향후 연구](papers/2026-simundic-visuo-force-tactile-door-opening.md) |

R1–R7 전체의 제공·정독 상태는 개별 논문 색인을 따른다. 현재 일곱 편 모두의 첨부 원문 정독·정리가 완료되었다. 이는 각 논문의 코드 실행·실험 재현이나 외부 보충자료 전체의 확인을 뜻하지 않는다.

### IROS 후속 선정 논문 정독

[2026-09-15 제목 선별 보고서](reviews/2026-09-15_iros-2023-2025-tactile-force-torque-rl-title-screening.md)에 2026-09-16 사용자 임시 선정 5편을 기록했다. 아래 ID는 R1–R7과 별개다. 현재 해당 5편 중 4편의 정독이 완료되었으며, 나머지 상태는 [개별 논문 색인](papers/README.md)을 따른다.

| 정리일 | 후속 선정 ID | 논문·상세 정리 |
| --- | --- | --- |
| 2026-09-16 | IROS-S01 | [Attention for Robot Touch — ConDepNet·TacSalNet·VAE 잡음 생성·GAN 손실·PID/DRL 연결·한계와 향후 연구](papers/2023-lin-attention-for-robot-touch.md) |
| 2026-09-16 | IROS-S02 | [Pseudo-Tactile Gripper State — 빈 파지 판정·재개방 override·시뮬레이션 시연·DP·admittance·ablation과 한계](papers/2025-yang-pseudo-tactile-gripper-state.md) |
| 2026-09-16 | IROS-S03 | [Location-Based Attention Pushing — 실시간 pose·occupancy grid·categorical PPO·리워드·randomization·DFT·실물 검증과 한계](papers/2025-dengler-location-based-attention-pushing.md) |
| 2026-09-16 | IROS-S05 | [Tactile-AIRL — 접촉 깊이·optical-flow entropy·FEEF·모델 앙상블·CEM·과업별 reward·실물 학습과 한계](papers/2024-liu-tactile-active-inference-rl.md) |

### 사용자 별도 발굴 논문

기존 일괄 조사 후보군 밖에서 사용자가 별도로 찾아 제공한 논문은 [사용자 별도 발굴 누적 목록](reviews/user-found-papers.md)으로 관리한다. 발굴 경로·서지·정독 상태를 유지하며, 기존 R1–R7 및 IROS-S01–S05의 분류와 집계를 소급 변경하지 않는다.

| 정리일 | 관리 ID | 논문·상세 정리 |
| --- | --- | --- |
| 2026-09-16 | USER-P001 | [Gentle Object Retraction — 분포형 3축 힘 영상·관절 토크 기반 wrench·Diffusion Policy·impulse 기준·실물 ablation·한계와 향후 연구](papers/2026-brouwer-gentle-object-retraction.md) |
| 2026-09-18 | USER-P002 | [Sim2Real Tactile Manipulation — arXiv v1·DIGIT 접촉 패턴 이진화·힘 기반 렌더링·PPO/reward·다종 물체·실물 전이·한계와 공개 계획](papers/2024-su-sim2real-tactile-manipulation.md) |

### Binary Tactile·F/T 조사 후속 원문 정독

[2026-09-16 신규 문헌 조사](reviews/2026-09-16_binary-tactile-wrench-rl.md)에 포함된 논문의 첨부 원문(PDF) 후속 정독이다. 기존 조사 ID를 유지하며, 새 논문 발굴 건수로 중복 집계하지 않는다.

| 정리일 | 조사본 ID | 논문·상세 정리 |
| --- | --- | --- |
| 2026-09-17 | B1 | [DexTouch — FSR 16bit·LPF/threshold·비대칭 PPO·관절 제어·보상식·감도/배치/F/T ablation·실물 평가·한계와 향후 연구](papers/2024-lee-dextouch.md) |
| 2026-09-17 | B3 | [Rotating without Seeing — arXiv v4·FSR 이진화·4프레임 관측·비대칭 PPO·상대 관절 목표·보상식·binary/continuous 실물 비교·한계와 향후 연구](papers/2023-yin-rotating-without-seeing.md) |

## 폴더와 파일명 규칙

| 경로 | 역할·파일명 |
| --- | --- |
| [README.md](README.md) | 문헌조사 전체 입구와 상세 정리 목록 |
| [reviews/README.md](reviews/README.md) | 조사 그룹별 안내와 논문 바로가기 |
| `reviews/YYYY-MM-DD_topic-slug.md` | 날짜별 조사·선별 보고서와 명시적으로 구분한 설계 제안 |
| [reviews/user-found-papers.md](reviews/user-found-papers.md) | 사용자 발굴 논문을 등록일별로 추가하는 고정 경로 |
| [papers/README.md](papers/README.md) | 논문 제목·원래 조사·정독 상태·상세 노트 색인과 작성 지침 |
| `papers/YYYY-firstauthor-paper-slug.md` | 게재연도·첫저자·주제로 식별하는 개별 논문 노트 |

여러 논문을 묶는 조사·선별·발굴 목록은 `reviews/`에 모으고, 논문 자체의 상세 정리는 `papers/`에 둔다. 발굴 경로가 다르다는 이유로 별도 폴더를 만들지 않는다. `user-found-papers.md`는 누적 목록이므로 날짜 접두사 없이 같은 경로를 유지한다.

날짜별 조사 파일명은 **조사 기준일 + 영문 소문자 주제명**으로 작성하고 주제명 내부는 하이픈으로 구분한다. `final`, `latest`, `수정본(2)`처럼 내용을 식별하기 어려운 이름은 사용하지 않는다. 조사 기간·범위가 달라진 후속 보고서는 새 기준일의 파일로 추가하고 이전 보고서와 연결한다.

개별 노트는 **논문 게재연도 + 첫저자 + 논문 주제명**으로 이름을 정한다. R·IROS-S·B/W/C·USER-P 식별자는 원래 조사와의 대응에 사용한다. 같은 논문을 다른 조사에서도 다루면 기존 노트로 연결하고 본문을 복제하지 않는다. 보완·정정은 같은 파일의 Git 이력으로 관리한다.

<a id="literature-navigation"></a>

## 문서 연결 관리

새 노트를 추가하거나 옮길 때 다음 연결을 한 작업에서 갱신한다.

1. **원래 보고서 → 상세 노트:** 보고서 상단의 바로가기와 해당 논문 항목에 실제 파일 링크를 넣는다. 후보가 많은 표에는 상세 노트 칸을 두며, 미작성 항목에는 빈 링크 대신 `미작성` 또는 `—`를 쓴다.
2. **상세 노트 → 원래 보고서:** 노트 상단에 문서 안내·문헌 색인·전체 논문·원래 조사 항목 링크를 둔다. 조사 항목은 `r1`, `iros-s01`, `b1`, `user-p001`처럼 제목 변경의 영향을 덜 받는 고정 anchor로 연결한다.
3. **색인 → 두 문서:** [조사 그룹 안내](reviews/README.md), [전체 논문 색인](papers/README.md), 이 문서의 해당 그룹을 갱신한다. 새 조사 그룹이면 보고서 색인에도 등록한다.
4. **파일 이동:** 저장소 전체에서 이전 경로로 향하는 링크와 파일 관리 규칙을 함께 바꾼다. 정독 상태·등록 ID·기존 조사 통계는 경로 이동만으로 변경하지 않는다.
5. **검증:** Markdown 내부 링크의 파일·anchor가 실제로 존재하는지, 새 노트가 색인에서 도달 가능한지, 상세 노트에서 원래 조사로 돌아갈 수 있는지 확인한다. `git diff --check`로 수정 형식도 확인한다.

조사 보고서가 보유한 최초 선별 기록과 후속 정독 상태는 날짜를 구분한다. 링크 추가를 과거 시점의 정독 완료나 실험 재현으로 바꾸어 기록하지 않는다.

## 자료와 출처 관리

종합 보고서에는 논문 고유의 목적과 확인된 방법을 먼저 쓰고, 프로젝트에 대한 해석·제안은 별도로 표시한다. 개별 원문 정독 노트에는 해당 논문의 내용만 정리한다. DOI, 저자 공개 원문, 확인 범위와 접근 제한을 유지한다. 논문 식별자 `R1`, `E1` 등은 해당 보고서 안에서만 유효하며, 다른 보고서나 프로젝트 출처 ID와 혼용하지 않는다.

논문 PDF를 이 저장소에 복제하지 않고 출판사 또는 저자 공개 원문으로 연결한다. 프로젝트의 방향이나 사양을 변경하는 결정이 실제로 내려진 경우에만 [결정 목록](../03_DECISIONS_AND_OPEN_QUESTIONS.md)과 관련 인계 문서를 갱신한다. 문헌조사 보고서나 원문 정독 노트를 등록했다는 이유만으로 실험이나 구현 작업을 완료 처리하지 않는다.


## 메모

- [ ] GAN을 사용하는 경우, Simulation Data를 기반으로 한 Generator가 생성한 이미지가 현실과 비슷하다고 판단할 Discriminator가 필요한데, 이 데이터 셋은 어떻게 확보하는가?
- [ ] 
