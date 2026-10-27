# 문서 구조와 작성 규칙

[문서 진입점](../AGENTS.md) · [개발 지침](09_DEVELOPMENT_GUIDE.md)

현재 기본 문서는 `src/inspire_sweep_baseline`의 Holding → Final 개발에 필요한 내용으로 제한한다. 관련 없는 과거 환경·연구 이력을 자동으로 읽도록 연결하지 않는다.

| 내용 | 위치 |
| --- | --- |
| 작업·개발·문서 규칙 | `00_guidelines/` |
| 현재 계획·사용자 결정 | `01_plan/` |
| 환경 계약·개발 로그·실행한 검증 | `02_implementation/` |
| 자료·원시 결과·백업 | `03_assets/` |

## 작성·갱신 순서

1. 현재 주제의 기준 문서를 보완하고 같은 내용을 여러 문서에 복제하지 않는다. 에이전트 진입점에는 핵심 규칙과 조건부 읽기 경로만 둔다.
2. 환경 변경은 해당 설명·활성 환경 안내·개발 로그를 갱신한다. 매 수정의 요청 근거·의도·전후 차이·영향·검증을 에이전트 인계용으로 기록한다.
3. 오래된 설명을 기본 문서에서 제거할 때는 원문을 먼저 백업하고 원래 경로·해시·복원 방법을 남긴다. 역사 기록은 현재 지침과 구분한다.
4. [형식 규칙](rules/document-formatting.md)을 적용하고 변경 문서의 링크·anchor·수식을 검사한다.

## 검증과 완료 기준

문서 저장소에서 실행한다.

```bash
python 00_guidelines/scripts/check_markdown_math.py <변경한-md-파일들>
python 00_guidelines/scripts/check_document_links.py
git diff --check
```

외부 workspace 파일까지 변경한 경우 `check_document_links.py --check-external <변경한-md-파일들>`로 해당 링크도 검사한다. 기존 역사 자료의 누락 산출물과 새 링크 오류를 구분한다. 실행 코드 변경이 없는 문서 작업에는 GPU 학습 검증을 요구하지 않는다.
