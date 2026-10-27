# Workspace 구성과 문서 지도

[현재 인계](../01_plan/00_HANDOFF_BRIEF.md) · [환경 안내](../02_implementation/08_ACTIVE_ENVIRONMENTS.md)

2026-10-27 기준. 활성 기반 패키지는 `src/inspire_sweep_baseline`, 최신 중점 계열은 Holding → Final이다. `src/axia80_feasibility`는 사용하지 않는다.

| 경로 | 현재 역할 |
| --- | --- |
| `src/inspire_sweep_baseline/inspire_sweep_baseline` | 환경·Manager·Scene·runtime·PPO 구현 |
| `src/inspire_sweep_baseline/scripts` | `train.py`, `play.py`, 요청된 진단 실행기 |
| `src/inspire_sweep_baseline/tests` | 설정·수식·경계·실행 검증 |
| `IsaacLab` | 시뮬레이션·학습 프레임워크 |
| `example/Contact-Rich-Manipulation-Context` | 지침·환경 설명·개발 기록을 관리하는 독립 문서 저장소 |
| `logs`, `outputs` | 학습·검증 산출물. 소스 변경이나 문서 정리의 대상이 아님 |

실제 코드가 참조하는 공용 기하 도구와 보관 자산은 의존성으로 유지한다. 과거 패키지가 디스크에 있다는 이유로 활성 개발 대상에 포함하지 않는다. `src/trash`는 기본 빌드·테스트 탐색에서 제외한다.

문서는 `00_guidelines/`(규칙), `01_plan/`(계획), `02_implementation/`(구현·검증), `03_assets/`(자료·백업)에 둔다. [파일 구조](12_ENVIRONMENT_FILE_STRUCTURE.md)와 [문서 구조](DOCUMENT_STRUCTURE.md)를 작업에 맞게 읽는다.

서브모듈은 독립 저장소이므로 각 HEAD와 작업트리를 확인하고 사용자 변경을 보존한다. 이번 정리에서 실제 코드·자산·패키지를 이동하거나 삭제하지 않는다. 학습 로그 정리는 명시적으로 요청된 경우에만 [정리 지침](11_TRAINING_LOG_CLEANUP.md)을 적용하며 `logs/rsl_rl`은 건드리지 않는다.
