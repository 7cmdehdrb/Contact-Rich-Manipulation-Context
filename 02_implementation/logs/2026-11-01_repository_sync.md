# 작업트리 커밋 및 원격 병합

- 요청: 현재 변경을 루트와 example의 문서 저장소에 commit·push하며, 원격 최신 변경을 pull·merge한 뒤 push한다.
- 범위: 기존 compact 환경·물체 갤러리 코드, 환경 설명·개발 기록 및 최종 수정 예정 문서. 예정 사항의 새 구현 작업은 수행하지 않는다. 다른 submodule HEAD와 학습 로그는 보존한다. IsaacLab의 미추적 `2.7.0+cu128`은 설치 출력 한 줄이 담긴 파일로 커밋에서 제외한다.
- 기준: 루트 HEAD `b0116a7`은 fetch 후 origin/main과 같았다. 문서 HEAD `50f075a`는 origin/main `577ade2`보다 4개 커밋 뒤에 있었다. 문서 로컬 변경은 `2f867b5`로 보존한 뒤 `git pull --no-rebase --no-edit origin main`을 수행했다.
- 충돌 해결: `04_article/README.md`의 동일 위치에 로컬 환경 설명 링크와 원격 Related Works 링크가 추가되어 충돌했다. 양쪽 항목을 원문 그대로 보존하여 해결했다. 원격 Related Works 본문·의도·로그도 병합에 포함한다.
- 검증: compact pool·v0_2_1 회귀·bbox 배치·gallery 배치의 기존 테스트 42개 통과. 로컬 문서 28개 수식 검사와 병합 전 전체 링크 검사 오류 0건, staged diff 공백 검사 통과. 병합 후 수정 문서 2개 수식 검사, 전체 Markdown 442개 링크 검사 오류 0건, staged diff 공백 검사 및 미해결 충돌 없음도 확인했다. 새 GPU rollout·학습·2048 env 검증은 수행하지 않았다.
- 반영 순서: 문서 저장소 병합 커밋을 먼저 push한 후 루트 소스와 문서 submodule 참조를 commit하고 pull·push한다. 원격과 HEAD 일치 및 잔여 작업트리를 마지막으로 확인한다.
