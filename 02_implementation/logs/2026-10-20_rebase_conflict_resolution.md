# 문서 Pull/Rebase 충돌 해결

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기록일: 2026-10-20. `git pull origin main --rebase`가 원격 `bf6ec5e` 위에 로컬 `334fe4b`를 재적용하다가 두 문서에서 중단된 상태를 해결했다.

## 처리 범위

- `02_implementation/08_ACTIVE_ENVIRONMENTS.md`: 로컬의 독립 `ContactSweepEnv` 설명과 원격의 종료 진단 이력·현재 print 비활성 상태를 함께 보존했다.
- `02_implementation/logs/README.md`: 원격의 기존 개발 로그 목록과 로컬의 PPO 중단 분석·v3·Contact Sweep 기록을 모두 유지했다.
- 충돌 없이 스테이징된 로컬 변경과 CSV·JSON 원시 자산은 그대로 보존한다. 코드·보상 계수는 변경하지 않는다.

## 실행한 검증

문서 저장소 루트에서 실행했다.

- `python 00_guidelines/scripts/check_document_links.py`: 내부 문서·자산·anchor 및 데이터셋 링크 오류 0개.
- `python 00_guidelines/scripts/check_document_links.py --check-external`: workspace 외부 파일 누락 4개. 기존 10월 14일 로그가 참조하는 학습 디렉터리 3개와 10월 15일 로그의 DexTouch PDF 1개이며 이번 충돌 위치와 무관하다.
- `python 00_guidelines/scripts/check_markdown_math.py <변경 Markdown 경로들>`: 재적용되는 Markdown과 이번 해결 기록 등 총 7개 파일 통과.
- `git diff --check`: 충돌 해결 편집의 공백 검사 통과.
- `git diff --cached --check`: 재적용 중인 원시 CSV 두 파일의 CRLF 줄바꿈을 trailing whitespace로 검출했다. 원본 자산 보존을 위해 줄바꿈은 변경하지 않는다. 수정 Markdown은 별도 staged 공백 검사를 수행한다.

해결 파일을 명시적으로 `git add`하고 `GIT_EDITOR=true git rebase --continue`로 기존 rebase를 완료한다. 완료 후 미병합 항목 부재, main 복귀, 작업트리 상태를 확인한다. 원격 push와 상위 workspace의 submodule 참조 커밋은 수행하지 않는다. 시뮬레이션·학습·실물 시험은 문서 충돌 해결 범위 밖이므로 실행하지 않는다.
