# 2026-11-05 Wrench v0 계열 상세 문서

## 요청과 작성 기준

사용자의 “Wrench 0 계열 환경에 대한 상세한 문서” 요청에 따라 `v0`, `v0_1`, `v0_2`, `v0_3`, `v0_4`를 하나의 기준 문서로 정리했다. 환경 추가나 보상 변경 요청이 아니므로 실행 코드는 수정하지 않았다.

- Workspace 코드 기준 commit: `c57087aa629ec0d7205a37f44dc3a595ea7974ec`.
- 문서 저장소 기준 commit: `c81a0bfc082686c75a2be2c984a229bc6498322c`.
- 작업 시작 시 workspace에는 문서 submodule의 commit 차이만 표시되었고 문서 저장소 내부 작업트리는 clean이었다. 현재 commit을 유지했으며 checkout·커밋·포인터 갱신은 하지 않았다.
- 현재 인계, 문서 저장소 지침과 대상 환경 실제 코드를 확인했다. 이전 계열은 현재 계산 의존성인 함수·모델만 필요한 범위에서 확인했다.

## 변경 전후와 의도

기존에는 v0/v1 통합 문서와 v0_1·v0_2·v0_3/v0_4 개별 변경 문서로 정보가 분산되어 있었다. 새 [Wrench v0 계열 상세 명세](../environments/WRENCH_V0_FAMILY_ENVIRONMENTS.md)는 공통 환경 전체와 다섯 버전의 최종 차이를 함께 설명한다.

| 내용 | 이번 정리 |
| --- | --- |
| 등록·상속 | v0_1과v0_2가 형제이며 v0_2→v0_3→v0_4라는 직접 상속, Gym/PPO 이름 |
| Scene·randomization | 형상·scale 생성 시 고정, 물성 startup 고정, reset bank 복원, 요청/실제 개수 구분 |
| 관측 | policy57의 정확한 순서, Actor121D/Critic124D, encoder 이후73D/76D, noise·좌표·갱신 시점 |
| 제어 | 모든 v0 계열의 pose OSC, torque limit, Hand 실행 clamp, 관측 tanh와 raw 행동 구분 |
| 보상 | 전체15항의 함수·weight·params·dt, 버전별 거리/접촉 함수·수식·state 수명 |
| action-rate | 기존 raw 정책 입력과 정규화 OSC 출력의 차이, Arm 상한0.06→0.0144/step, 평균 크기 단정 불가 |
| 커리큘럼 | 방향·개수·속도 비용의 정확한 iteration 구간과 비활성 항 |
| 경계·종료 | 거리3cm의 `<`/`<=`, 높이·접촉·속도·기울기·바닥 경계, 성공150표본 |
| 로그 | Episode_Reward가 누적 보상 평균/최대 episode 시간이라는 실제 Manager 계약 |
| 검증 | 이전 CPU103개 결과와 실제 GPU·학습 미검증 상태를 구별 |

개별 환경 문서와 기존 v0/v1 명세에는 새 종합 문서 링크를 추가했다. v0_2 문서의 현재 접촉 weight와 지급액은 실제 코드에 맞춰1.45→0.1, 최대0.29→0.02/step으로 정정했다. 과거 개발 로그 자체는 당시 기록으로 보존했다. 인계·활성 환경 안내·패키지 README에서도 종합 문서로 접근할 수 있게 했다.

## 중요한 대조 결과

1. 모든 대상 버전은 동일 pose OSC다. v0_3의 보상 정규화가 Desired Wrench 제어로의 전환은 아니다.
2. v0_2 이후 contact weight는 실제0.1이며 상한 count10을 유지한다. 독립 접촉 항은 v0_1에만 없다.
3. 목표 내부 예외뿐 아니라2-of-3 과거 접촉 표본 때문에 현재 EEF 높이가 상한 이상이어도 접촉 보상이 지급될 수 있다. 실제 접촉 표본의 높이 gate와 윈도우 인정은 구별해야 한다.
4. Hand 실행은 [0,1] clamp지만 rate penalty는 ActionManager raw2D 차이다. 기존 설명의 “정규화된 Hand”를 raw도 반드시[0,1]이라는 뜻으로 확대하지 않았다.
5. v0_4의 거리 weight3.7과 tolerance0을 확인했다. 미터 개선량의 에피소드 budget 예시는 식의 결과로 표시하고 학습 성능 결론으로 해석하지 않았다.
6. Isaac Lab `RewardManager.reset`의 `episodic_sum_avg / max_episode_length_s`를 확인했다. 예를 들어 성공+75가 단독으로 기록되는 성공 환경 집합의 해당 로그는7.5다.

## 검증과 미검증 범위

현재 EnvCfg, Reward/Curriculum/Termination/Observation/Action/Event/PPO 설정과 실제 계산 함수를 읽어 표·수식·상속·경계·호출 시점을 대조했다. 문서의 새 링크·heading anchor·Markdown 수식 및 `git diff --check`를 검사한다. 최종 검사 결과는 아래에 기록한다.

- 종합 문서681행,12개 본문 절과 목차·상속 Mermaid·버전/보상/경계/실행 표를 작성했다.
- AST로 기본 Reward15개 term 이름이 문서에 모두 있음을 확인했다.
- 실제 `feasibility_layout_stages()`의75단계와 `scheduled_value()`의 문서화된 모든 속도 전환값을 읽기 전용 Python 검사로 확인했다.
- 변경 Markdown10개 `check_markdown_math.py` 통과. 새 문서와 문서 저장소의 변경 문서9개에 대한 `check_document_links.py --check-external`은 오류0건이다.
- 패키지 README까지 포함한 링크 검사는 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1건을 보고했다. 기준 commit의 README에도 같은 링크가 있어 이번 범위에서 변경하지 않았다. 새로 추가한 링크 오류는 없다.
- workspace와 문서 저장소의 `git diff --check` 통과. `src/inspire_sweep_baseline/inspire_sweep_baseline`, `tests`, `scripts` 변경은0건이다.

기존 개발에서 CPU103개를 통과한 기록을 인용했으며 이번 문서 작업에서 회귀 테스트나 GPU 실행·학습을 새로 수행한 것으로 보고하지 않는다. GUI Markdown 렌더링은 확인하지 않았다. `logs/rsl_rl`, checkpoint, 학습 스크립트, 환경 소스는 수정하지 않았다.
