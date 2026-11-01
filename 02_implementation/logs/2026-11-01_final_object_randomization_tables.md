# Final 물체 무작위화 요약표 작성

- 요청: 현재 환경의 물체 종류·수·크기·질량·마찰 조건을 표로 정리하며 수량은 커리큘럼 최소~최대로 표현한다.
- 산출물: [물체 구성과 무작위화 조건](../../04_article/environment_reference/FINAL_OBJECT_RANDOMIZATION_TABLES.md), 폴더 README에 링크 추가.
- 변경 전후: 기존 장면 생성 상세 문서는 보존하고, 다섯 항목을 빠르게 비교하는 독립 요약표를 추가했다.
- 코드 대조: Final Scene의 12개 보유 물체, CompactRoleCollection의 그룹 1/3 선택과 9개 장애물 역할, Final 커리큘럼의 Gray 1~4/White 1~5, 생성 시 scale, realistic_physics의 분포·4096 분위수 bucket, episode physics의 질량 1.5배와 공유 적용을 확인했다.
- 크기 근거: 절차적 형상 코드와 기존 `outputs/ycb_base_sizes.json` 계측값을 사용했다. YCB 치수는 원본 스캔 크기와 구분했다.
- 추가 계산: Python statistics.NormalDist로 분위수 `inv_cdf(1-0.5/4096)=3.668329285121323` 및 마찰 역할별 최소·최대를 계산했다. 수치는 실행 중 측정값이 아닌 기본 후보 생성식 계산값으로 명시했다.
- 최종 대조: 요청 수 3~10, 장애물 2~9, 고정 물리 물체 12, 배치 실패에 따른 실제 수 감소를 구분했다. 크기 고정 시점, 질량·마찰 공통 적용, YCB 혼합분포를 명시했다.
- 영향: 문서만 추가·수정. 환경 코드·설정·학습 로그·서브모듈 HEAD는 변경하지 않았다.
- 검증: inline 수식 escape를 교정한 뒤 변경 문서 3개 수식 검사 통과. 전체 Markdown 431개 링크 검사 오류 0건, 변경 3문서 외부 파일 포함 링크 검사 오류 0건. `git diff --check` 통과(기존 파일 LF/CRLF 안내만 출력). 시뮬레이터 실행과 학습은 이 문서 작업에서 수행하지 않았다.
