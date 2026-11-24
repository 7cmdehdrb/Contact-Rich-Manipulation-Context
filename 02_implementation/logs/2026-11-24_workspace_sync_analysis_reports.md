# 원격 변경 병합 및 분석 보고서 동기화

## 요청과 범위

사용자가 현재 원격 내용을 pull·병합·push하도록 요청했다. 인증 문제로 push할 수 없으면 commit까지 완료한다. 로컬 분석 보고서와 자료를 보존하고, 기존 환경 코드·학습 로그·독립 서브모듈의 고정 커밋은 임의 변경하지 않는다.

## 변경 전후

- 루트 저장소: `8ce37bf`에서 `origin/main`의 `c8df111`로 fast-forward 병합했다. 원격 Prof Revision v0_2·v0_3 구현과 관련 변경을 받았으며, 별도의 환경 수정은 하지 않았다.
- 문서 저장소: `cc69933`에서 `origin/main`의 `3f2a98f`로 fast-forward 병합했다. 원격 환경 문서와 로컬 미추적 분석 파일의 경로 충돌은 없었다.
- 로컬 [Zone 분석](../experiments/2026-11-24_prof_revision_zone_analysis.md), [종료 페널티 진단](../experiments/2026-11-24_prof_revision_penalty_diagnosis.md), 각각의 개발 로그와 자료 폴더를 문서 커밋에 포함한다. 분석 결과는 기존 평가 당시 코드와 입력에 대한 기록이며, 이번에 받은 v0_2·v0_3 성능을 평가한 결과가 아니다.
- 루트는 새 문서 커밋을 가리키도록 서브모듈 포인터만 추가 커밋한다. 문서 저장소를 먼저 push하고, 성공하면 루트를 push한다. 원격 인증 실패 시 로컬 커밋을 보존한다.
- IsaacLab `929f0fe1e9`, Sweep-Policy `baa3740`, Universal Robots `18e6f60`은 원래 HEAD를 보존했다. 각 origin을 fetch했으며 지정된 IsaacLab main·Sweep-Policy min에는 추가 변경이 없었다. Universal Robots는 특정 커밋으로 고정되어 있으므로 다른 브랜치로 이동하지 않았다.
- 기존 IsaacLab 미추적 파일 `2.7.0+cu128`은 사용자 작업으로 보존하고 커밋하지 않는다. `logs/rsl_rl` 및 로컬 재생 산출물은 변경·정리하지 않는다.

## 검증과 한계

- 병합 두 건 모두 fast-forward 성공, 충돌 없음.
- `test_prof_revision.py`: CPU 테스트 32개 통과. 기존 ONNX 내보내기 의존성의 DeprecationWarning 1개 발생.
- 분석 문서·기록 4개 Markdown 수식 검사 통과.
- 병합 후 문서 저장소 전체 링크 검사: 679개 Markdown, 내부 링크 5732개, 오류 0개.
- 루트 `git diff --check` 통과. 커밋 전 문서 staged diff와 새 로그의 수식·링크 검사를 추가 수행한다.
- 이번 동기화에서는 GPU 실행·장기 학습을 수행하지 않는다. push 결과와 최종 HEAD·원격 일치 여부는 실행 결과로 별도 확인한다.
