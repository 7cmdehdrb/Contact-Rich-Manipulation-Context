# 문서 구조와 작성·읽기 규칙

[전체 안내](../README.md) · [지침 안내](README.md) · [연구·계획](../01_plan/README.md) · [구현 기록](../02_implementation/README.md) · [정적 자산](../03_assets/README.md)

기준일: 2026-10-14. 사용자가 지정한 네 가지 역할에 따라 이 문서 저장소를 구성한다. 이 규칙은 문서의 위치와 관리 절차를 정하며 연구 방법·수치·실험 성과를 새로 확정하지 않는다. 연구 범위와 근거 구분은 [에이전트 운영 지침](AGENT_RULES.md)을 따른다.

## 네 폴더의 역할

| 폴더 | 저장할 내용 | 판단 기준 |
| --- | --- | --- |
| `00_guidelines/` | 에이전트·문서·개발·workspace 지침, 작성 템플릿, 문서 관리 도구와 그 테스트 | 앞으로 어떻게 읽고 작성하고 검증할지를 정하는가? |
| `01_plan/` | 연구 요약·개요, 회의·결정·다음 작업, 아이디어·설계·구현 계획, 문헌조사, 발표 원고, 과거 설계 | 무엇을 왜 연구하고 어떤 방법을 제안하거나 계획하는가? |
| `02_implementation/` | 확인한 코드·장비 상태, 활성 환경 계약, 개발 로그, 수행한 실험과 재현 문서, 과거 구현 상태 | 실제 작성된 코드와 확인·실행한 내용을 설명하는가? |
| `03_assets/` | 이미지·CSV·XLSX·PDF·영상·서지 파일, 실험 원시 데이터·metadata·run.log | 문서가 참조하는 정적 파일이나 원시 근거인가? |

루트 `README.md`는 전체 탐색 진입점으로, 루트 `AGENTS.md`는 필수 지침을 읽게 하는 짧은 포인터로 유지한다. Git·편집기·에이전트 실행에 필요한 숨김 설정은 그 도구가 요구하는 위치에 둔다. 새 내용별 루트 폴더는 만들지 않고 위 네 폴더 안에서 분류한다.

이 저장소는 문서 전용 submodule이다. 로봇·학습 코드는 workspace의 활성 패키지에 두고, 문서 검사·서지 관리·문서용 그림 생성 도구는 `00_guidelines/scripts/`에 둔다. 코드 workspace와 다른 문서 저장소의 책임 경계는 [Workspace 안내](10_WORKSPACE_GUIDE.md)에서 확인한다.

## 위치를 결정하는 방법

파일 확장자만으로 문서의 위치를 결정하지 않는다. Markdown은 내용의 주된 목적에 따라 지침·계획·구현 중 하나에 둔다. CSV·XLSX 등 정적 자료는 그 자료를 설명하는 Markdown과 연결하되 `03_assets/`에 둔다.

| 내용 또는 경계 사례 | 위치 |
| --- | --- |
| 확정한 연구 방향·설계, 아직 구현하지 않은 인터페이스와 검증 순서 | `01_plan/` |
| 실제 환경 계약을 확인한 문서와 그 안의 미확인 항목·후속 작업 | `02_implementation/` |
| 수행 전 실험 계획 | `01_plan/experiments/` |
| 수행한 실험의 조건·결과·한계·재현 절차 | `02_implementation/experiments/` |
| Omni 보상 개편 계획 | `01_plan/environments/OMNI_REWARD_PLAN.md` |
| 적용된 Omni 환경 설명 | `02_implementation/environments/OMNI_ENVIRONMENT.md` |
| 발표 설계 설명·대본·발표용 연구 메모 | `01_plan/presentation/`, `01_plan/memo/` |
| 과거 설계와 개정 요청 / 과거 구현 상태 | `01_plan/history/` / `02_implementation/history/` |
| 문헌 분석·종합 Markdown / 문헌 비교 데이터·서지 파일 | `01_plan/literature/` / `03_assets/literature/`, `03_assets/bibliography/` |
| 실험의 raw CSV·metadata·실행 log | `03_assets/artifacts/` |

`CONFIRMED_DIRECTION`은 계획 폴더에 있을 수 있으며 구현 완료를 뜻하지 않는다. `02_implementation/`에 둔 문서도 모든 내용이 실행 검증된 것은 아니다. 문서 본문에서 코드 확인, 구현 보고, 실제 실행, 미확인을 구분한다.

계획과 구현이 섞인 기존 문서는 주된 목적에 따라 하나의 기준 위치를 정한다. 다른 영역에서는 해당 문서를 링크한다. 서로 다른 질문과 검증 상태를 독립적으로 관리해야 할 때만 문서를 나누고 양쪽을 연결한다. 원문 보존이 목적인 역사 자료는 당시 상태와 명령을 유지하고 현재 문서로 연결한다.

## 작업 전에 읽는 순서

1. 루트 [에이전트 진입점](../AGENTS.md)의 필수 포인터를 따라 [운영 지침](AGENT_RULES.md)을 읽는다.
2. [인계 요약](../01_plan/00_HANDOFF_BRIEF.md), [결정·미정 목록](../01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md), [다음 작업](../01_plan/04_NEXT_ACTIONS.md)을 읽고 현재 담당 연구와 상태를 확인한다.
3. 아래 표에서 작업 종류에 해당하는 문서를 읽고 실제 근거로 이동한다.

| 작업 | 추가로 읽을 문서 |
| --- | --- |
| Markdown 작성·수정 | 이 문서, [Markdown 형식 규칙](rules/document-formatting.md), 대상 폴더의 README |
| 코드 수정·개발 기록 | [개발 지침](09_DEVELOPMENT_GUIDE.md), [코드·장비 상태](../02_implementation/07_CODE_AND_HARDWARE_STATUS.md), [활성 환경](../02_implementation/08_ACTIVE_ENVIRONMENTS.md), 실제 활성 코드 |
| 연구 설계·평가 계획 | [구현·평가 계획](../01_plan/05_IMPLEMENTATION_AND_EVALUATION.md), [발표 안내](../01_plan/presentation/README.md) |
| 문헌조사·논문 정리 | [문헌 안내](../01_plan/literature/README.md), [개별 논문 정독 지침](../01_plan/literature/papers/README.md) |
| 파일 이동·workspace 정리 | 이 문서, [Workspace 안내](10_WORKSPACE_GUIDE.md) |
| 실험 결과 기록 | [연구 로그 템플릿](templates/RESEARCH_LOG.md), [구현 기록 안내](../02_implementation/README.md) |

문헌 안내에서 실제로 읽을 논문으로, 활성 환경 안내에서 실제로 적용된 config·runner·코드로 이어져야 한다. 안내 문서만 읽고 원문이나 실행 조건까지 확인했다고 기록하지 않는다.

## 새 문서와 자산을 추가하는 절차

1. 기존 색인과 관련 문서를 찾아 같은 목적의 기준 문서가 있는지 확인한다. 보완·정정은 그 문서에 반영하고 새 문서가 필요한 경우에만 만든다.
2. 위 분류표로 위치를 정한다. 문서의 기준일·적용 대상·상태·근거와 확인하지 못한 항목을 본문에서 식별할 수 있게 기록한다. 계획값과 실제 수행값은 각각 표시한다.
3. 새 개발 로그는 `02_implementation/logs/YYYY-MM-DD_<topic>.md`, 실험 기록은 `02_implementation/experiments/YYYY-MM-DD_<topic>.md`에 만든다. 실험 계획은 `01_plan/experiments/`에 둔다. 논문 노트는 개별 논문 지침의 이름 규칙을 따른다. 기존 파일명은 연결과 이력에 필요한 경우 유지한다.
4. 이미지·표·영상·원시 데이터는 `03_assets/`의 해당 자료 영역에 두고 문서에서 상대 링크로 연결한다. 정적 자산의 내용·출처·읽는 방법은 관련 Markdown에 남긴다.
5. 대상 영역의 README에 문서를 등록하고 문서 상단에서 해당 안내로 돌아갈 수 있게 연결한다. 문헌 노트는 원래 조사 항목과 양방향으로 연결하고 문헌·조사 그룹·논문 색인을 갱신한다.
6. 연구 결정을 바꾸면 결정 목록을 갱신한다. 범위·우선순위가 바뀌면 인계 요약·다음 작업도 갱신한다. 환경 계약을 바꾸면 활성 환경 안내·개발 로그·관련 패키지 문서를 함께 확인한다.
7. 아래 검증을 완료하고 변경한 내용, 실제로 확인한 검사, 확인하지 못한 항목을 기록한다.

## 파일 이동과 참조 관리

이동 전에 `git status --short`를 확인하고 기존 작업트리 변경을 보존한다. 파일·내용을 복원하거나 제거하기 전에 이번 이동 대상과 이미 진행된 작업을 구분한다. 원래 경로와 새 경로를 대응시켜 각 파일이 한 위치에 보존됐는지 확인한다.

이동하는 파일뿐 아니라 그 파일을 참조하는 문서·지침·템플릿·스크립트·설정·데이터도 확인한다. 특히 다음 참조를 갱신한다.

- Markdown의 일반·참조형 링크, 이미지 링크와 HTML 자산 경로
- 문서의 인라인 경로와 현재 실행을 안내하는 명령
- 색인·상단 바로가기·역방향 링크·문헌 관리 규칙
- CSV의 `analysis_file`, `analysis_note_path`와 XLSX의 해당 분석 노트 경로
- 스크립트·테스트의 import와 기본 경로, `.gitattributes`의 LFS 대상 경로

저장소 안의 파일은 링크를 작성한 문서의 부모 폴더 기준 상대경로로 연결한다. CSV의 분석 노트 경로도 **각 CSV 파일의 부모 폴더 기준**으로 계산한다. XLSX에 같은 경로 열이 있으면 해당 workbook의 부모 폴더 기준으로 맞춘다. 원본 PDF의 `local_path`, 당시 실행 경로, 해시 등 출처를 추적하는 역사적 값은 현행 링크와 구분해 보존한다.

파일만 이동한 경우 기존 anchor를 보존한다. 제목이나 anchor를 바꾼 경우 이를 참조하는 링크도 수정한다. 상세 문서가 없는 항목은 확보 상태를 적고, 없는 파일을 가리키는 링크나 빈 대체 문서를 만들지 않는다.

workspace 외부 파일로 나가는 링크는 통합 checkout의 실제 상대 위치를 기준으로 계산한다. 이 저장소만 clone한 경우 해당 링크의 미연결은 workspace 의존성으로 설명한다. 저장소 내부 문서와 자산은 단독 clone에서도 연결되어야 한다.

## 검증과 완료 기준

저장소 루트에서 내부 파일·anchor·자산 및 데이터셋의 분석 노트 참조를 검사한다.

```bash
python 00_guidelines/scripts/check_document_links.py
```

통합 workspace에서 저장소 밖 코드·문서 참조도 확인한다.

```bash
python 00_guidelines/scripts/check_document_links.py --check-external
```

`--check-external`은 workspace 파일 링크 확인에 사용한다. 이 옵션의 통과를 HTTP URL이나 논문 원문의 확인으로 기록하지 않는다. 단독 clone에서 workspace 파일을 확인할 수 없으면 그 범위를 기록한다.

이번 작업에서 새로 작성하거나 내용·참조 경로를 수정한 Markdown 파일만 수식 검사에 전달한다. 아래 `<changed-file.md>`는 실제 변경 파일 목록으로 바꾼다.

```bash
python 00_guidelines/scripts/check_markdown_math.py <changed-file.md> [more.md ...]
git diff --check
```

문서 관리 Python 도구를 변경했다면 관련 테스트를 실행한다. 도구와 테스트를 함께 읽고 실행 위치·import 경로를 확인한다. Markdown 수식의 구체적 형식과 오류 수정은 [형식 규칙](rules/document-formatting.md)을 따른다.

문서 도구의 공통 테스트 명령은 저장소 루트에서 다음과 같다. `PYTHONPATH`는 옮긴 `scripts` 모듈을 테스트가 찾게 한다.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=00_guidelines \
  python -B -m unittest discover -s 00_guidelines/tests -v
```

완료는 다음 조건으로 판단한다. 이동 대상이 누락 없이 보존되고, 새 문서가 영역 색인에서 도달 가능하며, 내부 파일·anchor·자산·데이터셋 참조 검사가 통과해야 한다. 기존 경로가 남았다면 역사적 출처인지 외부 자료인지 설명할 수 있어야 한다. 실행한 검사와 미확인 범위를 기록한 뒤 작업을 마친다.
