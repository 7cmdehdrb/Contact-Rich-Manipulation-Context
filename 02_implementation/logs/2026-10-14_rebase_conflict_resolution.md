# 문서 이관 후 Pull/Rebase 충돌 해결

[개발 로그](README.md) · [전체 안내](../../README.md) · [문서 구조 규칙](../../00_guidelines/DOCUMENT_STRUCTURE.md)

기록일: 2026-10-14. 사용자가 실행한 `git pull --rebase origin main`에서 원격의 문서 추가와 로컬의 네 폴더 재배치가 겹쳤다. 원격 기준은 `f1033f583eefbe6280111589e684688aca5d5912`, 재적용 중인 로컬 커밋은 `a99cfb658c6c1b345e7e5fc6a26463d094dee480`이다.

## 충돌 원인과 처리

| 충돌 경로 | 원인 | 해결 |
| --- | --- | --- |
| `02_implementation/logs/README.md` | 원격에서 추가한 상세 학습 기록과 로컬의 로그 색인이 같은 이동 대상에 놓임 | 로그 README는 색인으로 유지하고, 상세 원문은 [10월 12일 학습 기록](2026-10-12_inspire_hand_training.md)에 보존 |
| `02_implementation/logs/TODO.md` | 원격이 기존 `docs/logs/` 아래에 추가한 계획 문서의 위치 충돌 | [최종 구현·검증 TODO](../../01_plan/TODO.md)에 보존하고 문서·발표·로그 링크 수정 |
| `docs/README.md` | 로컬의 이동·삭제와 원격의 학습 기록·TODO 색인 행 추가가 겹침 | 원격의 추가 행을 [계획 안내](../../01_plan/README.md)에 통합한 뒤 구경로 제거 |

원격 학습 보고의 수치·실험 결과·가설과 TODO 본문은 그대로 유지했다. 경로와 탐색 연결을 수정한 것이며 새 학습·실물 검증이나 연구 사양의 재확정은 아니다. 원격 TODO의 이관 경로는 자산 폴더의 경로표에도 등록했다. 나머지 이미 적용된 로컬 변경은 유지한다.

수정 전에 충돌 인덱스의 양쪽 원문과 작업트리 파일을 `/tmp/context-rebase-resolution-20261014/`에 백업했다. Git LFS 객체·인덱스는 상위 workspace의 submodule 메타데이터에 있으므로 해당 Git 작업은 그 경로에 접근 가능한 실행 환경에서 수행한다. Git LFS 설정과 자산 내용은 변경하지 않았다.

## 검증과 Rebase 이어가기

저장소 루트에서 변경 문서의 수식·파일/anchor 참조와 충돌 표식을 확인하고, 해결한 경로를 명시적으로 스테이징한다.

```bash
python 00_guidelines/scripts/check_document_links.py --check-external
python 00_guidelines/scripts/check_markdown_math.py \
  01_plan/README.md 01_plan/TODO.md 02_implementation/logs/README.md \
  02_implementation/logs/2026-10-12_inspire_hand_training.md \
  02_implementation/logs/2026-10-14_rebase_conflict_resolution.md
git diff --check
git diff --cached --check
git ls-files -u
GIT_EDITOR=true git rebase --continue
```

완료 판정은 미병합 인덱스 항목이 없고, rebase 상태가 종료되어 `main`으로 복귀하며, 원격 추가 문서와 로컬 폴더 구조가 함께 남는 것이다. 원격 push는 이 요청의 작업에서 수행하지 않는다.

검증 결과: 문서 210개와 데이터셋 CSV/XLSX를 포함한 내부 참조 3,661개, workspace 참조 83개에서 파일·anchor 오류 0개였다. 이번 변경 Markdown 5개의 수식 검사도 통과했다. 원격 학습 기록의 본문은 원문과 같고, TODO는 링크 경로를 제외한 내용이 원문과 같다. 미병합 인덱스와 충돌 표식은 0개다.

전체 staged 공백 검사에서는 이미 재적용되어 있던 세 문서(`OMNI_REWARD_PLAN.md`, 9월 26일 구축 계획, 과거 환경 개정 요청)의 기존 공백·파일 끝 빈 줄을 검출했다. 이들의 본문은 이번 충돌 해결에서 수정하지 않았다. 이번 해결로 수정한 여섯 경로의 staged 공백 검사는 별도로 확인한다.
