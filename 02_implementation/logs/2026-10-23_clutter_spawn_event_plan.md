# 스폰 규칙 고도화와 Event 개발 계획 작성

[로그 목록](README.md) · [개발 계획](../../01_plan/environments/CLUTTER_SPAWN_EVENT_PLAN.md) · [요청 TODO](../../../../docs/TODO.md)

기준일: 2026-10-23. 사용자 요청으로 영역별 개수 파라미터화, RED 금지·최소 거리 불변, 배치 부족 시 유효 부분 결과 반환을 reset Event 개발 계획으로 정리했다. 실제 코드 구현 요청은 없으며 계획 문서만 작성했다.

## 기준과 확인한 내용

- Workspace commit: `703ac8864fa8c0e4606fbf67fd5629fb367e96c4`.
- 문서 submodule commit: `7fd20636009427d2960f1194b84353c71adfced3`.
- 시작 시 양쪽 `git status --short` 출력은 비어 있었다. `git submodule status`에서 문서 저장소는 상위 기록과 다른 commit을 가리켰으며 그 checkout을 유지했다.
- 인계·Workspace·개발·문서 지침, TODO, 기존 계획, Fusion v1_0의 population/layout/events/scene/env, 공통 Clutter 생성기와 테스트, 참고 기하 생성기, 모델/export와 Isaac Lab reset 순서를 읽었다.
- 현재 개수 설정은 이미 존재하지만 부족한 부분 배치 반환은 없고, 10 장애물·40D 제한이 여러 경로에 있음을 확인했다. RED 중심 금지 영역, 1.6 cm 표면 간격과 10.3 cm RED 팽창 반경을 구분했다.
- 계획에 요청/실제/capacity 분리, rear의 GRAY 부분집합 의미, 환경별 mask, 유한 탐색, 감소의 증명 여부, Event 적용 순서, 관측·센서·checkpoint 의존 작업과 검증 기준을 포함했다.
- TODO에 계획 링크를 추가하고 계획 색인·결정 목록·로그 색인을 연결했다. 환경 등록과 실제 계약은 변경하지 않아 활성 환경 문서는 수정하지 않았다.

## 실제 검증

문서 저장소에서 다음 명령을 실행했다.

```powershell
python 00_guidelines/scripts/check_document_links.py --check-external
python 00_guidelines/scripts/check_document_links.py
```

- 내부 검사: Markdown 331개, CSV 10개, XLSX 5개를 검사하여 오류 0개.
- 전체 외부 경로 포함 검사: 오류 66개로 실패했다. 이번 수정 대상 밖의 과거 로그가 참조하는 `logs/TEMP`, `logs/backup`, `outputs` 산출물 및 PDF 등이 현재 checkout에 없다. 해당 이력과 파일은 수정하지 않았다.

Workspace 루트에서 수정한 Markdown 6개를 명시하여 다음 검사를 실행했다. 아래 배열은 실제 검사에 전달한 파일 목록이며 긴 명령을 재현하기 쉽게 묶은 표기다.

```powershell
$spawnDocs = @(
  'docs/TODO.md',
  'example/Contact-Rich-Manipulation-Context/01_plan/environments/CLUTTER_SPAWN_EVENT_PLAN.md',
  'example/Contact-Rich-Manipulation-Context/01_plan/README.md',
  'example/Contact-Rich-Manipulation-Context/01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md',
  'example/Contact-Rich-Manipulation-Context/02_implementation/logs/2026-10-23_clutter_spawn_event_plan.md',
  'example/Contact-Rich-Manipulation-Context/02_implementation/logs/README.md'
)
python example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_markdown_math.py @spawnDocs
python example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_document_links.py --root example/Contact-Rich-Manipulation-Context --check-external @spawnDocs
git diff --check
git -C example/Contact-Rich-Manipulation-Context diff --check
```

수식/Markdown 검사 6개 통과, 변경 문서의 외부 경로 포함 링크 검사 오류 0개(외부 파일 링크 21개·내부 링크 185개), 양쪽 diff 공백 검사 통과. Git의 LF→CRLF 안내는 있었으며 검사 오류는 아니었다. 미추적 새 문서 2개는 `git diff --check`에 포함되지 않아 아래 PowerShell 검사도 실행했다.

```powershell
$spawnPlanFiles = @(
  'example/Contact-Rich-Manipulation-Context/01_plan/environments/CLUTTER_SPAWN_EVENT_PLAN.md',
  'example/Contact-Rich-Manipulation-Context/02_implementation/logs/2026-10-23_clutter_spawn_event_plan.md'
)
foreach ($spawnPlanFile in $spawnPlanFiles) {
  $spawnPlanTrailing = @(Get-Content -Encoding UTF8 -LiteralPath $spawnPlanFile | Where-Object { $_ -match '\s+$' })
  if ($spawnPlanTrailing.Count) { throw "Trailing whitespace: $spawnPlanFile" }
}
```

새 문서의 줄 끝 공백은 0개였다. 최초 소스 탐색에서 추정한 생성기·EnvCfg·하위 README 경로 일부가 없어 읽기에 실패했으며, `rg --files`와 실제 import 경로로 위치를 확인하여 정정했다. 초기 PowerShell 읽기의 한글 표시 문제는 UTF-8을 명시하여 해결했다.

## 미검증 범위

문서만 변경했으므로 CPU 동작 테스트·Isaac Sim·학습·실물 실험은 실행하지 않았다. 새 배치 규칙의 구현, 20개 수용 여부, 실제 최대 개수와 고밀도 성능은 검증하지 않았다. 테스트 사례와 성능 측정 항목은 앞으로 실행할 계획이다. 코드·참고 생성기·학습 로그는 수정하지 않았다.
