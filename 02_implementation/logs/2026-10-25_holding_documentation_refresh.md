# Holding 계열 문서 최신화

날짜: 2026-10-25. 범위는 문서 개정이며 환경 코드·학습 로그는 변경하지 않는다.

## 변경

- [환경 계층](../environments/ENVIRONMENT_EVOLUTION.md)에 최신 세 환경과 테스트 분기 등록을 반영했다.
- [Holding 공통 문서](../environments/FUSION_HOLDING_FAMILY.md)에 기존 v3 문서를 병합했다. 기존 파일은 링크 보존용 이동 안내로 유지한다.
- 최신 세 환경의 개별 설명을 추가하고 [v4 공통 계약](../environments/FUSION_HOLDING_V4_FAMILY.md)에 네 보상, r/2r, 유효성, 커리큘럼, 종료, 이론상 최대를 정리했다.
- v2·ObjectRandom-v1의 오래된 OSC 수치를 현재 공통 구성에 맞추고 환경·활성·로그 색인을 연결했다.

## 근거와 검증

활성 패키지의 등록·EnvCfg 직접 상속·보상 함수·Manager CFG·OSC 구성·커리큘럼을 대조했다. 이전 작업의 수정 사항은 보존했다. 실행한 정적 검사와 결과는 아래에 기록한다.

실제 Sim smoke는 최초 v4 구현 시점의 결과이고, 후속 2r 확장은 CPU 검사 결과다. 이번 문서 작업에서는 학습·Sim·실기 실행을 반복하지 않았다. 장기 학습의 timeout 100% 달성, 처리량, 실기 성능은 미검증이다.

Workspace 루트 PowerShell에서 실행했다.

```powershell
python outputs/audit_holding_docs.py
python example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_document_links.py --root example/Contact-Rich-Manipulation-Context --check-external example/Contact-Rich-Manipulation-Context/02_implementation/environments example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md example/Contact-Rich-Manipulation-Context/02_implementation/logs/README.md example/Contact-Rich-Manipulation-Context/02_implementation/logs/2026-10-25_holding_documentation_refresh.md
$files = Get-ChildItem example/Contact-Rich-Manipulation-Context/02_implementation/environments -Filter '*HOLDING*.md' | ForEach-Object FullName
python example/Contact-Rich-Manipulation-Context/00_guidelines/scripts/check_markdown_math.py @files example/Contact-Rich-Manipulation-Context/02_implementation/environments/ENVIRONMENT_EVOLUTION.md example/Contact-Rich-Manipulation-Context/02_implementation/environments/README.md example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md example/Contact-Rich-Manipulation-Context/02_implementation/logs/README.md example/Contact-Rich-Manipulation-Context/02_implementation/logs/2026-10-25_holding_documentation_refresh.md
git -C example/Contact-Rich-Manipulation-Context diff --check
git diff --check
```

결과: AST로 등록 ID 상수를 해석한 51개 ID가 계층 문서에 모두 존재하며 최신 3개 EnvCfg의 직접 부모도 일치했다. 링크 검사 58문서·내부 링크 692개·workspace 외부 경로 338개, 오류 0건. Markdown 수식 검사 19문서 통과. 두 저장소 diff 검사는 공백 오류 없이 통과했으며 기존 수정 파일의 LF→CRLF 안내만 출력했다. HTTP URL 접속과 GitHub 실제 수식 렌더링은 검사하지 않았다. AST 감사 스크립트는 로컬 outputs 산출물이며 패키지를 import하거나 Sim을 시작하지 않는다.
