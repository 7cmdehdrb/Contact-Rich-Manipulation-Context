# Inspire 패키지 Python 캐시 정리

[개발 로그 목록](README.md)

기준일: 2026-10-26. 사용자 요청으로 workspace의 `src/inspire_sweep_baseline/inspire_sweep_baseline` 내부 캐시를 정리했다.
기준은 상위 저장소 `main`의 `5a1b291`, 문서 submodule의 `4e03404`다. 두 저장소에 기존 수정·미추적 파일이 있었으며 보존했다.

## 수행 내용과 결과

Workspace 루트에서 `python -B -`의 표준 입력으로 정리 스크립트를 실행했다.
`os.walk(..., followlinks=False)`로 `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`와 개별 `.pyc`·`.pyo`를 탐색했다.
`git ls-files -z -- src/inspire_sweep_baseline/inspire_sweep_baseline` 결과와 비교해 삭제 대상에 추적 파일이 없음을 확인한 뒤 캐시 디렉터리는 `shutil.rmtree`, 개별 bytecode는 `Path.unlink`로 삭제했다.

- 삭제: `__pycache__` 47개, 내부 캐시 파일 339개, 합계 1,381,306 bytes.
- 삭제 후 같은 범위를 재탐색한 결과 캐시 항목 0개.
- 캐시 외 파일 177개를 삭제 전후 SHA-256 또는 심볼릭 링크 대상으로 비교하여 보존 확인.
- 환경 설정·등록·보상·학습 로그는 변경하지 않았다.

## 검증 명령과 범위

다음 명령을 실행했다. 캐시 탐색은 출력 없이 종료했고, 변경 문서 2개의 수식 검사와 두 저장소의 공백 검사는 통과했다.
전체 문서 링크 검사는 기존 문서가 참조하는 workspace 외부 자료 누락 41건으로 실패했다.
이번에 수정한 두 문서에서는 링크 오류가 보고되지 않았다. 기존 자료 복구는 이번 정리 범위에서 제외했다.

```bash
find src/inspire_sweep_baseline/inspire_sweep_baseline \( -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache \) -o -type f \( -name '*.pyc' -o -name '*.pyo' \) \) -print
git diff --check
cd example/Contact-Rich-Manipulation-Context
python -B 00_guidelines/scripts/check_markdown_math.py 02_implementation/logs/2026-10-26_python_cache_cleanup.md 02_implementation/logs/README.md
python -B 00_guidelines/scripts/check_document_links.py --check-external
git diff --check
```

캐시 삭제만 수행했으므로 pytest·시뮬레이션·학습 실행은 생략했다. Python 실행 시 캐시는 다시 생성될 수 있다.

## 후속 요청: 빈 폴더 정리

같은 날 사용자의 추가 요청으로 같은 패키지 경로 안의 빈 디렉터리 25개를 삭제했다.
Workspace 루트에서 `python -B -`로 `os.walk(root, topdown=False, followlinks=False)`를 실행하고, 패키지 루트를 제외한 실제 빈 디렉터리만 `Path.rmdir()`로 삭제했다.
심볼릭 링크는 따라가거나 삭제하지 않았다. 삭제 전후 파일 177개의 SHA-256 또는 링크 대상을 비교하여 모두 동일함을 확인했고, 재탐색한 빈 디렉터리는 0개였다.

변경한 이 로그의 수식 검사와 두 저장소의 `git diff --check`를 다시 실행해 통과했다.
파일 내용 변경이 없어 pytest·시뮬레이션·학습 실행은 생략했다.
