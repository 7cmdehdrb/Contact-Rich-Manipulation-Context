# Revision-v1 · v1-Test 개발 명세 작성 기록

2026-11-02. **환경 구현 기록이 아니라 설계·수식 검증 기록**이다.

## 요청과 작업 범위

사용자는 Revision-v0를 기반으로 보상 분리, wrist budget 제거, 7개 커리큘럼 고정, 장애물 수 일정, Hold와 일회성 보상을 변경할 Revision-v1 및 타겟만 cylinder인 v1-Test의 개발 명세서를 요청했다. 실제 환경 개발은 금지하고 plot 코드만 허용했다.

- 기준 workspace HEAD: `408d3d9ce947a62f094d6f8c8693be2c07e2e32d`.
- 문서 저장소 HEAD: `1c5de3ad0a1a525c6d79bd083af6e58c9d51aa43`.
- 기존 사용자 파일 `docs/plan/PLAN8.md`, 이전 분석 문서 및 submodule 상태는 보존했다.
- `src/`, Gym 등록, 실제 환경·학습 설정, 학습 로그를 수정하지 않았다. play·환경 import·GPU·학습·rollout은 실행하지 않았다.

## 산출물

- [개발 명세](../../01_plan/environments/2026-11-02_REVISION_V1_SPEC.md).
- [plot 스크립트](../../03_assets/revision_v1_spec/plot_rewards.py): NumPy/Matplotlib만 사용하는 CPU 수식 계산.
- [Hold 위치·속도](../../03_assets/revision_v1_spec/01_hold_curves.png), [Hold 결합 heatmap](../../03_assets/revision_v1_spec/02_hold_heatmaps.png).
- [Object penalty 분리 동등성](../../03_assets/revision_v1_spec/03_object_penalty_split.png), [Wrist budget 제거·접촉 비용](../../03_assets/revision_v1_spec/04_wrench_budget_and_contact.png).
- [커리큘럼](../../03_assets/revision_v1_spec/05_curricula.png), [진입·timeout 이벤트](../../03_assets/revision_v1_spec/06_event_bonuses.png).
- [검증 결과·기준 소스 SHA256](../../03_assets/revision_v1_spec/validation.json), [Hold 수치 CSV](../../03_assets/revision_v1_spec/hold_samples.csv).

## 결정과 요청 대조

| 요구 | 확인·명세 반영 |
| --- | --- |
| Object penalty 3분리 | object_tilt / obstacle_displacement / object_acceleration, weight −30/−150/−0.05. 대상·cap 위치·history 보존 |
| 5% 제한 삭제 | 실제 함수는 wrist wrench임을 확인. 누적 positive budget만 제거하고 raw cap1 유지 |
| 10k 고정 | acceleration −0.05/20, obstacle −0.05/50, wrist −0.1/20/2. obstacle의 12k −0.1/30과 구분 |
| 장애물 일정 | 비동기 질문에 사용자 확인: 10k White, 12k Gray, 14k White. 초기3/3, 최종4/5 |
| Hold 위치 | 3cm 미만 단일 Gaussian raw=2×2^[-4(d/.03)^2], weight8, 중심16·경계 안쪽1 |
| Hold 속도 | max(v−.05,0)에 기존 scale .05 적용. 5cm/s 이하 감쇠 없음 |
| 진입·timeout | 최초 관측 d<3cm +30, 기존 성공 timeout d≤3cm +40. 각 한 번, 부분 reset·동일 step 계약 명시 |
| v1-Test | v1 직접 상속, 타겟 형상만 cylinder. scale·장애물·물성·배치·관측 랜덤화 보존 |

추가 결정은 설계 선택으로 명시했다. Gaussian 계수4는 기존 최대16을 유지하면서 중앙/경계 비율을 기존4:1에서16:1로 키운다. 첫 진입과 Hold의 엄격 경계는 최신 사용자 문구를 따른다. timeout은 “지금처럼”에 따라 기존 inclusive 판정과 bonus를 유지한다. control step 사이에만 통과한 연속 궤적의 검출은 별도 기능이므로 이번 계약에 포함하지 않았으며 샘플링 한계를 명시했다.

기존 문서의 shelf-frame 타겟 yaw=0과 실제 layout 코드를 대조했다. 이전 대화에서 board-frame −90도를 타겟 물리 yaw로 표현한 것은 부정확하다. 신규 명세에는 두 좌표계를 구분하고 v0→v1의 yaw 변경을 포함하지 않았다.

## 실행 검증

workspace 루트에서 실행했다.

```bash
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python \
  example/Contact-Rich-Manipulation-Context/03_assets/revision_v1_spec/plot_rewards.py
```

- Hold 1,002,001개 거리·속도 조합: 모든 값 finite, 범위0~16.
- 경계·단조성·5cm/s plateau·10cm/s half factor 검사 통과.
- 물체 10개 합성 상태 10,000개: 기존 composite와 새3항 합 최대 절대오차 `5.684341886080802e-14`.
- 장애물 일정8개 시점·고정7항의 v0 10k 값 일치 검사 통과.
- PNG6개를 직접 열어 축·범례·수치 범위·곡선 중첩·이벤트 지급을 확인했다.
- Markdown 검사에서 발견한 수식 macro 중괄호와 inline 집합 표기를 수정했다. 최종 변경 Markdown3개 수식 검사 통과, 외부 workspace 링크 포함 검사 errors=0, `git diff --check` 통과. 별도 Markdown 전체 렌더링은 수행하지 않았다.
- 기준 소스8개의 SHA256 재대조가 모두 일치했고, `src/inspire_sweep_baseline`의 diff는 비어 있다. 실제 환경 구현 변경이 없음을 확인했다.

수식 검증은 NumPy로 표현한 기존·새 계약의 비교다. 실제 RewardManager 구현·stateful term·PhysX 센서·초기화·학습의 성공을 검증한 것이 아니다. 개발 단계의 회귀·경계·부분 reset·dt·Test 단일 차이·실제 물리 검증 목록은 명세에 남겼다.

## 최종 변경 범위

새 명세1개, 이 기록1개, plot script와 그림·CSV·JSON을 추가했다. 현재 인계에는 “설계만 완료·미구현” 링크만 추가한다. 기존 활성 환경 안내를 구현 완료로 갱신하거나 v1 코드를 추가하지 않는다. 기록과 그래프는 개발 인계 자료이며 사용자에게 별도 승인이나 실행을 요구하지 않는다.
