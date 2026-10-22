# 등록 환경 전체의 독립 문서와 변경 계층도

[개발 로그](README.md) · [환경 문서 안내](../environments/README.md) · [환경 계층과 변경 의도](../environments/ENVIRONMENT_EVOLUTION.md)

## 요청과 기준

사용자는 패키지 `__init__.py`에 등록된 모든 환경을 독립 문서에서 확인하고, 계층도에서 부모와의 차이·변경 의도를 파악한 뒤 상대 링크로 상세 설명에 들어가는 문서 집합을 요청했다. 기존 독립 문서는 재작성하지 않고, 추가 문서는 기본 구성·관측·전체 보상 표·특수 보상 설명·종료 표·커리큘럼 표로 간략히 구성했다.

| 기준 | 확인값 |
| --- | --- |
| 날짜 | 2026-10-22, Asia/Seoul |
| 상위 workspace | branch `main`, commit `3bf14a91e5070ec987d02cf1498052a21275b48c` |
| 문서 submodule | branch `main`, commit `68cf3de634fabbc6d48daaf3f8ffca4902beaf8d` |
| 시작 작업트리 | 상위의 untracked `PLAN2.md` 유지; 문서 submodule 변경 없음 |
| 등록 기준 | [활성 패키지 init](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py)의 `gym.register` 29개 |
| 참고 페이지 | [Notion 학습 기록](https://app.notion.com/p/3f7bd3c55e1b80e5a161c6e0dd175773), 마지막 수정 2026-10-22T07:01:01.427Z |

Notion은 반환된 기준 환경·물성·관측·Clutter/Fusion 변경 이유를 참고했다. 응답의 `truncated=true`와 외부 객체 1개 미표시를 확인했으며, 모든 블록·영상·첨부를 확인했다고 주장하지 않는다. 제안·과거 관찰은 현재 코드 설정 및 이번 검증 결과와 구분한다.

## 변경 내용

- 기존 독립 문서 7개(Omni v0/v3, Dex Omni v0, Baseline Tactile, Clutter v1, Fusion v0/v1_0)는 유지했다.
- 초기 Baseline/Omni 6개, Renewal 9개, Contact/Clutter/Fusion 7개 등 총 22개의 간략 독립 문서를 추가했다. 각 파일과 전체 Gym ID는 [등록 매핑](../environments/ENVIRONMENT_EVOLUTION.md#5-전체-등록-id--독립-문서)에 있다.
- 계층 문서에 전체 개요와 세 계열의 Mermaid 흐름도, 부모별 변경 의도, 전체 등록 ID별 링크를 추가했다. 세 독립 EnvCfg 베이스, Renewal v3의 v1 직접 분기, Fusion v0→v2→v3→v1_0 체인을 구분했다.
- 환경 폴더 README와 상위 README·구현 README·활성 환경·로그 색인에 탐색 링크를 추가했다.
- 전체 내부 링크 검사에서 발견한 기존 FT 수집 기록의 끊어진 활성 환경 anchor는, 활성 환경 안내에 FT Test 요약과 독립 문서 링크를 추가해 복구했다.
- 현재 소스와 과거 기록이 다른 Omni v1 Arm 종료 1.5 rad/s, Fusion v0/v2 `push_fast` 1.0 m/s 및 v3 0.8 m/s를 명시했다. 문서화를 이유로 환경 구현이나 과거 기록의 수치를 변경하지 않았다.
- 기존 Omni v3 설명 이후 바뀐 공통 Reaching의 후퇴 비용·초기 근접 분모 처리도 계층 문서에서 현재 코드·새 v4 요약으로 연결했다.

소스 코드·환경 등록·학습 설정·학습 산출물은 변경하지 않았다. `logs/rsl_rl`과 `logs/TEMP` 정리는 수행하지 않았다. 새 commit이나 원격 반영은 수행하지 않았다.

## 실제 검증

| 검사 | 실제 결과 |
| --- | --- |
| 모든 하위 `__init__.py`의 `gym.register` 검색 및 AST 등록 추출 | 등록은 루트 init의 29개이며, 목록 29개·서로 다른 독립 문서 29개와 일치 |
| 새 문서의 필수 항목·표·복귀 링크, 기존 독립 문서 diff | 신규 22개에 요청 항목과 표·계층 복귀 링크 존재; 기존 7개 내용 변경 없음 |
| EnvCfg AST와 Mermaid 상세도 직접 상속 대조 | 상세도 28개 실선 관계 모두 일치; Baseline→Isaac Lab 직접 상속 별도 확인. 개요는 계열 요약으로 명시 |
| 계열별 소스 정독·상속 후 보상 표 대조 | 신규 22개 전체 보상 항목·가중치 확인. 독립 재검토에서 계층도 및 OSC·목표 체류 표본 문서의 의미 오류 없음 |
| 변경 Markdown 수식 검사 | 29개 파일 통과 |
| 변경 Markdown의 내부·workspace 상대 링크 검사 | 29개 파일, 오류 0 |
| 저장소 전체 내부 링크·anchor·데이터셋 검사 | Markdown 314개, CSV 10개, XLSX 5개, 오류 0 |
| 저장소 전체 workspace 외부 링크 검사 | 기존 문서 5개의 미보유 파일 참조 41건. 아래 구분 참조 |
| 공백 검사 | 추적 파일 `git diff --check` 통과; 신규 파일 `git diff --no-index --check /dev/null` 진단 없음 |

문서 검사 명령은 문서 submodule 루트에서 실행했다. 변경 파일만 고르는 아래 명령은 새 파일도 포함한다. 초기에 `git diff --no-index`의 차이 존재 반환값 1을 실패로 처리한 wrapper를 수정해, 실제 공백 진단 유무를 확인했다.

```bash
python 00_guidelines/scripts/check_document_links.py
python 00_guidelines/scripts/check_document_links.py --check-external
git diff --check
python - <<'PY'
import subprocess
from pathlib import Path
changed = subprocess.check_output(
    ['git', 'diff', '--name-only', '--diff-filter=ACMRTUXB'], text=True
).splitlines()
added = subprocess.check_output(
    ['git', 'ls-files', '--others', '--exclude-standard'], text=True
).splitlines()
files = sorted({p for p in changed + added if p.endswith('.md')})
subprocess.run(['python', '00_guidelines/scripts/check_markdown_math.py', *files], check=True)
subprocess.run(['python', '00_guidelines/scripts/check_document_links.py',
                '--check-external', *files], check=True)
for file in files:
    if subprocess.run(['git', 'ls-files', '--error-unmatch', file], capture_output=True).returncode:
        result = subprocess.run(['git', 'diff', '--no-index', '--check', '/dev/null', file],
                                capture_output=True, text=True)
        assert result.returncode in (0, 1) and not result.stdout and not result.stderr
print(f'Changed Markdown: {len(files)}; checks passed')
PY
```

등록 매핑 검사는 workspace 루트에서 `python - <<'PY'`로 실행했다. `ast.parse`로 등록 ID와 EnvCfg entry point를 추출하고, 계층 문서의 등록 표와 집합·개수·파일 유일성을 대조했다. 각 신규 문서의 다섯 필수 항목·표와 복귀 링크를 확인하고, 기존 7개는 `git diff HEAD -- <file>` 출력이 없는지 검사했다. 이어 등록된 클래스의 실제 `.bases`를 추출해 Mermaid 상세도 28개 직접 상속 간선을 비교했다. Simulator를 import하거나 새 테스트 파일을 저장하지 않는 일회성 문서 검사다.

전체 외부 링크의 미보유 41건은 기존 `2026-10-14_omni_immediate_termination.md`, `2026-10-15_dex_omni_rewards.md`, `2026-10-21_clutter_ft_collection.md`, `2026-10-21_clutter_fusion.md`, `2026-10-21_scene_visibility.md`가 가리키는 과거 `logs/TEMP` run, 로컬 DexTouch PDF, `outputs` CSV/JSON/검증 스크립트·그림이다. 이번 작업에서 생성·수정한 문서의 링크 오류는 없다. 미보유 근거를 임의 생성하거나 과거 로그에서 삭제하지 않았다. 전체 검사가 통과했다고 기록하지 않는다.

## 미검증 범위

문서만 변경했으므로 Isaac Sim 시작, train/play, GPU 물리·센서 접촉, 정책 성공률 및 실물 검증은 실행하지 않았다. 코드와 문서의 정적 대조를 학습 성과로 해석하지 않는다. Mermaid의 실제 GitHub 화면 렌더링과 Notion 미반환 블록·외부 객체·영상 내용도 이번 검증 범위에 포함하지 않는다.
