# Contact Sweep 두 환경 통합 문서

[로그 목록](README.md) · [통합 설명](../environments/CONTACT_SWEEP_ENVIRONMENTS.md)

사용자 요청으로 `Isaac-Inspire-Contact-Sweep-v0`와 `Isaac-Inspire-Contact-Sweep-Clutter-v0`를 하나의 환경 설명에 정리했다. 현재 코드와 앞선 검증 기록을 대조해 상속·물성·reset·관측·MLP·제어·보상·종료·PPO·train/play 명령을 기록했다. Clutter의 최신 장애물 3개·RED 반경 10.3 cm와 최초 6개 구성의 검증 이력을 구분한다. 구현 색인과 활성 환경 안내에서 새 문서로 연결했다.

기준 workspace HEAD는 `457c3674c1993daaec8b8062f64f5d368bc7dcd6`, 문서 HEAD는 `e8aba3abbb6a321fdbae0ddc137d1ffee3ff59a4`다. 앞선 작업의 미커밋 변경을 보존했으며 이번 작업은 문서만 추가·수정했다. 환경 코드 변경·새 학습·GPU 재실행은 하지 않았다.

수행한 검사:

- `python 00_guidelines/scripts/check_markdown_math.py 02_implementation/environments/CONTACT_SWEEP_ENVIRONMENTS.md 02_implementation/README.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md`: 3개 통과.
- `python 00_guidelines/scripts/check_document_links.py --check-external`: 새 링크 오류 없음. 기존 TEMP 로그 3건과 DexTouch PDF 1건의 누락은 유지된다.
- 문서 저장소 `git diff --check`: 통과.

브라우저 렌더링은 확인하지 않았다. 이 기록의 이전 학습·물리 검증 수치는 연결된 당시 개발 로그의 수행 범위를 따른다.
