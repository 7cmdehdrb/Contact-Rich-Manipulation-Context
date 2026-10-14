# 문서 저장소 네 폴더 재구성

[전체 안내](../../README.md) · [개발 로그](README.md) · [구조 규칙](../../00_guidelines/DOCUMENT_STRUCTURE.md) · [결정 목록](../../01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md)

기록일: 2026-10-14. 근거: S-DOC-STRUCTURE-20261014의 사용자 요청. 대상은 문서 저장소의 폴더 구성·문서 생산/읽기 규칙·참조 경로다.

## 기준 상태와 보존 범위

문서 저장소의 기준 branch는 `main`, HEAD는 `94333d2fe714f9951cb561ee51322017c4fcc3bc`다. 작업 시작부터 문서 수정·새 workspace 안내·Axia80 Python snapshot 삭제 등 앞선 미커밋 변경이 있었다. 현재 작업트리 내용을 기준으로 이관했고, 삭제된 코드 snapshot을 되살리거나 앞선 수정 내용을 되돌리지 않았다.

이관 전 실제 파일 314개를 경로·SHA-256으로 기록했다. 캐시를 제외한 이 파일들은 모두 새 위치에 보존되었다. 경로표는 [document-path-map.csv](../../03_assets/repository/document-path-map.csv)에 저장소 루트 기준으로 남긴다. 루트 `AGENTS.md` 본문은 `00_guidelines/AGENT_RULES.md`로 옮기고 루트에는 필수 지침 포인터를 새로 만들었다.

## 변경 내용

| 위치 | 관리 대상 |
| --- | --- |
| `00_guidelines/` | 프로젝트·문서·개발·workspace 지침, 템플릿, 문서 도구·테스트 |
| `01_plan/` | 아이디어·연구 설계·계획·문헌·발표·과거 설계 |
| `02_implementation/` | 실제 코드 설명·활성 환경·개발 로그·수행한 실험·과거 구현 상태 |
| `03_assets/` | 이미지·CSV·XLSX·PDF·영상·서지·실험 원시 근거 |

발표와 9월 26일 환경 구축안은 계획으로, 9월 22일 Axia80 실험과 적용 Omni 환경은 구현 기록으로 분류했다. Omni 보상 초안은 계획에 연결한다. 폴더 변경은 연구의 방법·임계값·성과를 새로 확정하는 결정이 아니다. 폴더별 README와 전체 진입점을 연결하고, 새 에이전트의 필수 읽기·문서 생산·이동·검증 절차를 구조 규칙에 정리했다.

Markdown 일반·이미지·참조형 링크와 HTML 경로를 새 위치에서 계산했다. 코드 workspace로 나가는 상대 링크도 확인했다. CSV 10개와 XLSX 5개의 `analysis_file`·`analysis_note_path`는 각 파일의 부모 폴더 기준으로 분석 노트에 연결한다. `.gitattributes`의 PDF·영상 LFS 패턴도 새 경로로 바꾸었다.

상위 workspace의 `README.md`, `AGENTS.md`, `docs/README.md`, 두 활성 패키지 README, `src/trash/README.md`, `src/trash/inspire_tactile/README.md`의 진입 참조를 수정했다. 마지막 파일의 두 상대 링크는 이번 이관 이전부터 깊이가 틀렸으며 현재 workspace에서 해결되도록 함께 고쳤다. 그 밖의 로봇·학습 코드와 실행 계약은 변경하지 않았다.

Review Dataset `local_path`, BibTeX의 Windows Zotero 원본 경로, 실험 metadata·run.log의 당시 실행 경로는 provenance로 보존한다. 해당 논문 원문 PDF는 이번 작업에서 새로 확보하지 않았다. 현재 자산 위치와 이러한 출처 기록의 구분은 [자산 안내](../../03_assets/README.md)에 남겼다.

## 검증 명령과 결과

아래 명령은 문서 저장소 루트에서 실행했다.

```bash
python 00_guidelines/scripts/check_document_links.py --check-external
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=00_guidelines \
  python -B -m unittest discover -s 00_guidelines/tests -v
xargs -d '\n' python 00_guidelines/scripts/check_markdown_math.py \
  < 03_assets/repository/reorganization-changed-markdown.txt
git diff --check
```

수식 검사 목록은 이 작업 시작 시점의 내용과 비교해 내용·참조가 바뀐 Markdown 및 새 문서만 포함한다. 단순 경로 이동만 있는 기존 논문 노트는 수식 일괄 보완 대상으로 삼지 않았다. 링크 검사는 전체 문서·정적 자산·분석 노트의 파일과 anchor를 검사한다. HTTP URL에 접속하거나 논문 원문을 정독한 검사와 구분한다.

| 검사 | 실제 결과 |
| --- | --- |
| 파일 보존과 루트 폴더 | 이관 전 314개 모두 새 위치 존재. 숨김 설정을 제외한 루트 폴더는 지정한 4개 |
| 전체 문서와 참조 | Markdown 207개, 내부 참조 3,629개, 외부 workspace 참조 83개. 파일·anchor 오류 0개 |
| 문서 탐색 도달성 | 루트 README·AGENTS에서 Markdown 207개 모두 도달. 미연결 0개 |
| 데이터셋 참조 | CSV 10개·XLSX 5개에서 각각 분석 노트 경로 326개 정상 연결 |
| CSV·XLSX 내용 보존 | CSV의 다른 13,151개 값, XLSX의 다른 37,663개 셀값(숫자 791개 포함) 동일. Worksheet XML도 경로 문자열 외 동일 |
| 원시 자산 보존 | 데이터셋 비교 파일을 제외한 정적 자산 91개 SHA-256 동일 |
| 문서 도구 테스트 | 16개 모두 통과 |
| 변경 Markdown 수식 | 저장소 내부 146개와 외부 수정 문서 7개 통과 |
| 수정 형식 | `git diff --check` 통과. 새 파일을 포함한 변경 줄의 공백도 별도 확인 |

검사 과정에서 참조를 수정한 네 Markdown에 있던 기존 수식 문법 오류를 발견했다. Inline delimiter는 named macro로, 중복 display delimiter는 `math` fence로 고쳐 수식의 내용·수치는 유지했다. 기존 수식 테스트의 기대값도 현재 검사기가 반환하는 두 진단(여러 물리적 줄·Markdown 구조 문법)에 맞추어 갱신했다. 이번 작업과 무관한 기존 논문 노트의 내용을 일괄 보완하지 않았다.

외부 수정 문서의 수식 검사 명령도 실행했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  ../../README.md ../../AGENTS.md ../../docs/README.md \
  ../../src/inspire_sweep_baseline/README.md \
  ../../src/axia80_feasibility/README.md ../../src/trash/README.md \
  ../../src/trash/inspire_tactile/README.md
```

## 미실행 항목과 다음 행동

Isaac Sim train/play, 새 정책·센서 시뮬레이션, 실물 센서·로봇 시험, HTTP 링크 상태 확인, Git commit·push는 수행하지 않았다. 이번 결과는 문서 배치와 연결·검사 도구의 검증이며 새로운 연구 성능 결과가 아니다.

이후 문서는 구조 규칙에 따라 네 영역 안에 작성한다. 연구 결정은 결정 목록에, 코드·실험 상태는 구현 기록에 반영하고 관련 색인·역방향 링크·자산 참조를 함께 갱신한다.
