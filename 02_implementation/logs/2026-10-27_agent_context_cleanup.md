# 2026-10-27 에이전트 컨텍스트 정리

## 요청·의도

사용자가 `src/axia80_feasibility`를 사용하지 않으며 `src/inspire_sweep_baseline`을 기반으로 Holding → Final에 집중한다고 지정했다. 매 작업마다 과거 환경과 연구 자료를 연쇄적으로 읽던 진입 문서를 축약하고, 기존 환경 설명은 복구 가능한 원문으로 분리한다.

## 변경·보존 범위

- 루트와 문서 저장소의 AGENTS, 인계, Workspace·개발·파일 구조·문서 작성 지침, README, 활성 환경 및 로그 색인을 정리했다. 시작 시 인계만 읽고 나머지는 작업에 맞게 선택한다.
- 활성 환경 안내는 Holding·Final 등록·상속·실행·비교 기준만 유지했다. Holding → Final 개발 흐름과 Final v0의 독립 구성을 구분했다.
- 이전 계열 설명·규칙은 현행 진입 문서에서 제거했다. 기존 코드·개별 과거 문서·학습 로그는 보존했다. 삭제된 절을 참조하던 과거 문서 링크만 원문 백업으로 변경했다.
- 원문은 [백업 색인](../history/2026-10-27_agent_context/README.md)과 SHA-256 manifest에 보존했다. 작업 시작 시 존재했던 미커밋 변경도 포함한다.
- 직접 수정/새 환경 생성 구분, 부모 보존, 현재 디렉토리 구조 유지, 목표 도달 `d <= r`, 모든 커리큘럼 포함 전체 대조, 매 수정 의도 기록을 유지했다.
- 실행 코드와 `docs/plan/PLAN7.md`는 수정하지 않았다. 환경 동작·상속·리워드 변경은 없다.

## 검증

검증 결과는 아래에 기록한다. 문서 정리 작업이므로 Isaac Sim·학습 테스트는 실행하지 않는다.

- 核심 진입·지침 13개: 2,250줄 → 365줄(약 84% 축소). 로그 색인은 별도로 축약했다.
- 백업 manifest의 37개 원문을 Python `hashlib.sha256` 및 바이트 수로 재검사: 모두 일치.
- 문서 저장소에서 `python 00_guidelines/scripts/check_document_links.py`: Markdown 391개, 내부 링크 4,567개, 데이터셋 링크 포함 오류 0.
- `python 00_guidelines/scripts/check_markdown_math.py <변경한 39개 문서 경로>`: 39개 통과. 경로 목록은 manifest의 source 37개와 새 백업 색인·현재 로그다.
- `python 00_guidelines/scripts/check_document_links.py --check-external <현행 진입 문서·색인 16개>`: 오류 0. 경로 목록은 manifest의 첫 14개 source와 새 백업 색인·현재 로그다.
- 같은 외부 링크 검사를 변경한 전체 39개 문서에 적용하면 과거 `2026-10-21_clutter_ft_collection.md`의 `outputs/clutter_ft/` 산출물 24개가 없다. 백업 원문에도 동일한 참조가 있음을 확인했다. 이번 정리에서 생성·삭제한 산출물이 아니므로 역사적 링크를 보존한다.
- 과거 문서 23개의 원문·수정본을 비교해 링크 목적지 외 본문이 동일함을 검사했다. 삭제된 절의 링크 24개를 백업으로 연결했다.
- 루트와 문서 저장소에서 `git diff --check`: 통과. 루트 작업트리 변경 대상은 `AGENTS.md`와 문서 submodule뿐이다.
- 미검증: 외부 URL의 네트워크 접근성, Isaac Sim 실행 및 학습 성능. 문서만 변경했으므로 환경 전후 실행 비교는 해당하지 않는다.
