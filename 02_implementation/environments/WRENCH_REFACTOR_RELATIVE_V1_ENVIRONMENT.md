# Inspire-Wrench-Refactor-Relative-v1 — 폐기

2026-11-06 사용자 요청으로 Gym 등록, EnvCfg, PPO runner를 삭제했다. 이 ID는 더 이상 실행 가능한 환경이 아니다.

기존 v1은 Relative-v0의 장애물 관측을 Base 기준으로 바꾼 실험이었다. 현재 활성 계열은 [v0](WRENCH_REFACTOR_RELATIVE_V0_ENVIRONMENT.md), [v2](WRENCH_REFACTOR_RELATIVE_V2_ENVIRONMENT.md), [v3](WRENCH_REFACTOR_RELATIVE_V3_ENVIRONMENT.md)이며 모두 EEF pose를 제외한 공간 관측을 EEF 기준으로 사용한다. Axia280g은 v0로 옮겨 공통 상속한다.

기존 학습 로그와 checkpoint는 보존했다. 이전 v1 checkpoint는 장애물 좌표계 의미가 다르므로 활성 환경 정책과 동등하게 취급하지 않는다. [과거 구현·진단 기록](../logs/2026-11-06_wrench_refactor_relative_v1.md)은 역사 자료로 유지한다. [폐기·계열 재구성 기록](../logs/2026-11-06_relative_family_280g_v3.md).
