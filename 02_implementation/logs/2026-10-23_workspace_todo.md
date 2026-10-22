# 후속 연구·개발 TODO 구체화

[로그 목록](README.md) · [작성한 TODO](../../../../docs/TODO.md)

기준일: 2026-10-23. 사용자 요청으로 workspace `docs/TODO.md`에 OSC, 고밀도 스폰, 실사용 에셋, 현실–시뮬레이션 물성 비교, 논문 가제본의 작업·완료 기준을 작성했다. 저장 위치는 이번 사용자의 명시 지정을 따른다. 환경 구현이나 연구 성과를 추가한 작업은 아니다.

## 기준과 변경

- Workspace 기준 commit: `16a2a3e`; 문서 submodule: `c0e2568`.
- 작업 시작 시 workspace에 기존 삭제 항목, 미추적 `docs/TODO.md`·`docs/plan/`, submodule 참조 차이가 있었다. TODO는 0 byte였으며 기존 변경을 보존했다. 문서 submodule 내부 `git status --short`는 비어 있었다.
- 인계·Workspace·개발 지침, 기존 연구 TODO 및 활성 코드의 Action, OSC, Scene, population, layout, physics를 대조했다.
- Joint Position과 기존 OSC 구현을 구분하고, 0 명령 과속의 기존 미해결 기록을 연결했다. 타겟 포함 7개와 장애물 관측 10개 제한도 구분했다.
- 코드·환경 등록·학습 설정은 변경하지 않았다. 새 실험 조건은 TODO의 제안이며 실제 수행 결과가 아니다.

## 실제 검증

Workspace 루트에서 실행했다.

```powershell
python example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_markdown_math.py docs/TODO.md
git diff --check
```

두 검사 모두 통과했다. 미추적 TODO는 `git diff --check` 대상이 아니므로 PowerShell로 별도 검사했다.

```powershell
$todoText = Get-Content -Raw -Encoding utf8 docs/TODO.md
$todoLinks = [regex]::Matches($todoText, '\]\(([^)]+)\)')
$missingLinks = @($todoLinks | Where-Object { -not (Test-Path -LiteralPath (Join-Path docs $_.Groups[1].Value)) })
if ($missingLinks.Count) { throw 'Missing links' }
$trailing = @(Get-Content -Encoding utf8 docs/TODO.md | Where-Object { $_ -match '\s+$' })
if ($trailing.Count) { throw 'Trailing whitespace' }
```

상대 링크 17개 모두 존재하며 줄 끝 공백은 0개였다. 최초 Python `-c` 링크 검사는 PowerShell 인수 인용 문제로 SyntaxError가 발생해 위 PowerShell 검사로 교체했다. 초기 `rg`의 디렉터리 wildcard 검색도 Windows 경로 오류로 실패해 명시 경로 읽기로 대체했다.

문서만 변경했으므로 CPU 동작 테스트·Isaac Sim·학습·실물 실험은 수행하지 않았다. TODO는 향후 검증 계획이며 제어 안정성·고밀도 성능·실물 재현성을 입증하지 않는다.
