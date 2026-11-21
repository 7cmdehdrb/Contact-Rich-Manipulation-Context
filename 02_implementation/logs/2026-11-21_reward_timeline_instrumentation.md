# 보상 timeline 계측·비교 데이터 추출

## 요청·기준

사용자가 `docs/instruction.md`를 근거로 현재 보상 timeline과 교수님 의도 부합 여부를 점검하고, 필요하면 학습 checkpoint들을 비교하며 데이터를 미리 추출해 보관하라고 요청했다. 메인 기준은 `4102344`, 문서 기준은 `85ec22b`다. 시작 시 이전 Play 분석기의 미커밋 수정·집계 실행기·문서와 사용자 미추적 `docs/instruction.md`, IsaacLab의 기존 미추적 설치 출력 파일이 있었다. 모두 보존했다.

대상은 이전 턴과 같은 wr8/`inspire_sweep_single_contact_v0/2026-11-20_20-56-01`의 `Inspire-Sweep-Single-Contact-v0`다. 현재 보상으로 iteration0·1000·4000·8000·12000·15800을 비교한다. 과거 학습 reward log 복원과 현재 설정의 재평가를 구분한다.

## 변경 전후·영향

- 기존 `scripts/analyze_sweep_contact_policy.py`에 선택적 `--reward-timeline`을 추가했다. 기존 접촉면 계측을 활성화하며 이 옵션이 없으면 보상 계측은 설치하지 않는다.
- `scripts/reward_timeline_probe.py`를 추가했다. RewardManager의 기존 callable을 한 번씩 원래 순서로 호출하여 원값을 저장한다. 실제 manager의 가중 rate와 전체 보상을 함께 읽고 dt 적용 항 기여를 저장한다. class term의 reset·cache 속성은 원래 객체에 위임한다. 원래 반환값을 수정하거나 별도 보상을 더하지 않는다.
- 행동·문턱 입력으로 action/이전 action·팔/손 실제 속도·wrench 전후 물리값·장애물 힘/변위·기울기·선반 높이 조건을 추가 저장한다. 진단용 GT를 정책 관측에 넣지 않는다.
- `scripts/analyze_reward_timelines.py`를 추가했다. 공통 초기 episode만 집계하고 raw/applied15항·phase·gate·성공/실패 timeline·함수 곡선·학습단계 비교를 생성한다.
- 출력 폴더의 `prepare_dataset.py`로 원시 trace 해시·schema/단위·조건부 gate·입력 분포·312개 소스/설정 snapshot을 보존했다. 데이터와 보고서는 [실험 기록](../experiments/2026-11-21_single_contact_reward_timeline.md)을 따른다.

환경 패키지 본체의 함수·수치·Manager·관측·액션·보상·종료·PPO·커리큘럼·reset 구성은 변경하지 않았다. 기존 checkpoint와 `logs/rsl_rl`·TEMP 학습 로그는 읽기만 했다. commit·push·재학습은 하지 않았다. 평가 때 기존 분석기의 pair-buffer 축소만 사용하며 이를 기록했다.

## 실제 결과

각128환경·seed1729·500step, 총768개의 초기 episode를 비교했다. 모든 체크포인트의 초기 물리/관측 hash dictionary가 정확히 같았다. 성공률은0/29.69/50.00/44.53/50.78/64.06%였다.15,800의 평균 Reach7.012·Sweep 진행3.251·전체9.543, 목표 밖 정지 구간의 양의 순보상과 목표 이탈 실패의 높은 누적 보상을 확인했다. 교수님 목적과의 차이·원인 가설·미실행 후속 실험은 위 실험 기록에서 설명한다.

원시 trace6개를242,683,843byte 보관했다. 재분석용 manifest·소스 archive·NPZ·CSV·그래프는 `outputs/reward_timeline/model15800_family`에 있다. 최종 결과 폴더는 `reviewed_analysis`다. 이전 `analysis`·`analysis_final`과 실패 console도 삭제하지 않았다.

## 검증과 미검증

실제 RewardManager 전체와 항별 합계의 최대 오차5.96e-8, rate×dt 오차2.98e-8을 확인했다.14개 항의 입력으로부터 재구성한 적용값 최대 오차5.96e-8이었다. 모든 저장 float 유한성·초기 episode128개씩 완료·bank hash 일치·항별step 수를 검사했다.

shelf_collision 원값은 정확히 보존했으나 움직임 proxy의 기준 pose가 실제 class와 달라5mm 문턱 근처51–70frame에서 boolean이 달랐다. 이 항의 입력 독립 검증을 통과했다고 보고하지 않는다. timeline/통계는 정확한 원래 callable 값을 사용한다. 최초 JSON 직렬화 오류는 NumPy 정수를 Python int로 바꾸고 재집계했다. 공통 이동 접촉 표본이0인 초기 정책의 조건부 비율은 빈 값으로 보존했다.

완전한 PhysX solver state 복구, 모든 noise trajectory 일치, 독립 학습 seed·보상 수정·재학습·충격 조건부 probe는 검증하지 않았다. 보상 수정의 인과 효과를 주장하지 않는다.

최종 대조: 환경 패키지 본체 변경0개, 분석기만 선택 옵션 확장·보조 실행기 추가. 원래 checkpoint6개 SHA-256이 모두 일치했다. Python3개 AST 검사, 변경 문서3개 수식 검사, 전체645개 문서 링크 오류0개, 변경 문서 외부 링크 검사 오류0개, 메인·문서 공백 검사 통과.312개 소스/설정 archive의 CRC 검사 통과. 함수·학습단계 비교·성공/정지/접촉 실패 timeline을 실제 PNG로 열어 확인했다. 초기 정책의 접촉 없는 조건부 비율은 결측으로 남겼다.
