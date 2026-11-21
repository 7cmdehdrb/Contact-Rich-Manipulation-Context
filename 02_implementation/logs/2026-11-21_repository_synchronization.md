# 원격 변경 병합과 로컬 수정 보존

## 요청·시작 상태

사용자는 현재 수정을 고려한 pull·merge·commit을 요청했고, push는 인증이 가능하면 수행해도 된다고 했다. 상위 저장소는 `main`의 `f3059f3`, 문서 저장소는 `main`의 `8dfcb81`이었다. 상위 저장소에는 `docs/plan/PLAN19.md`의 F/T 변화량 페널티 clipping 수정 요청과 문서 submodule 포인터 차이가 있었다. 문서에는 인계·활성 환경 안내·Sweep Only 계통·Sweep v0 상세의 수정4건, Sweep 계통 설명·개발 로그의 새 파일2건이 있었다.

사용자 변경은 먼저 상위 저장소 `2583046`, 문서 저장소 `ffd48ed`로 각각 커밋했다. PLAN19는 요청 문구 그대로 보존했으며 이번 동기화에서 F/T 보상 함수를 추가 수정하지 않았다. 추적 파일의 binary diff와 문서 새 파일의 별도 백업도 `/tmp/grad-sync-QZ7Rujvk`에 보관했다.

## 가져오기·병합 전후

Git HTTPS fetch는 Username 인증 실패, SSH는 publickey 인증 실패였다. 연결된 GitHub 도구의 읽기 API로 원격 Git commit·tree·blob을 받아 로컬 객체 저장소에 가져왔다. 모든 객체는 원본 SHA-1 일치를 확인한 후 기록했으며 원본 커밋의 부모·메시지·작성자·시각을 보존했다. 별도 commit을 만들어 원격 이력을 대체하지 않았다. 원격 URL과 인증 설정은 변경하지 않았다.

| 저장소 | 가져온 main | 시작점 이후 원격 변경 | 병합 결과 |
| --- | --- | --- | --- |
| 상위 코드 | `df5197f9b516a7349c0ebe466602551315805a1e` | 2개 커밋: 접촉 정책 분석, Single Contact v1·reward timeline 도구 | 로컬 PLAN19 커밋과 내용 충돌 없이 병합 |
| 문서 | `e22ff54531647e0c678f9cf0d5675205ce5dbc7f` | 2개 커밋: LinearReach 분석, Single Contact v1 명세·구현·평가 | 기존 상세 문서와 새 원격 기록을 함께 병합 |

문서 충돌은 `01_plan/00_HANDOFF_BRIEF.md`, `02_implementation/08_ACTIVE_ENVIRONMENTS.md`, `02_implementation/environments/SWEEP_V0.md`의3곳이었다. 인계·활성 환경 안내는 원격의11월21일 기록을 먼저 두고 로컬의11월20일 사용자 보고를 이어 보존했다. Sweep v0 상세는 로컬의 보완된 설명·학습 보고를 유지하고 원격의 Single Contact v1 절을 추가했다. 서로 다른 날짜의 실행·학습 기록을 덮어쓰지 않았다.

상위 저장소의 문서 포인터는 원격 코드 커밋이 가리킨 `85ec22b`보다 최신인 문서 병합 커밋으로 갱신한다. IsaacLab·Sweep-Policy·Universal Robots 서브모듈은 시작 HEAD를 유지한다. 환경 코드·분석 도구는 원격 원문을 그대로 반영하며 별도 기능 변경은 하지 않았다. `logs/rsl_rl`과 학습 산출물은 수정하거나 정리하지 않았다.

## 검증·한계

- 가져온 두 원격 HEAD에 `git fsck --connectivity-only --no-dangling` 통과. 원격 객체의 내용·해시 및 Git 이력 연결을 확인했다.
- CPU 회귀: 아래4개 파일에서 **140 passed / 7.35초**. GPU를 숨기고 기존 검증용 Python 환경에서 실행했다.
- 변경 문서15개의 수식 검사와 전체 내부 링크 검사(652개 Markdown, 오류0건), 최종 diff 공백 검사를 통과했다. 충돌 표시를 제거하고3개 충돌 경로를 해결하여 문서 병합을 완료했다.
- 변경 Python14개는 AST 문법 검사를 통과했고 원격 `origin/main`의 원문과 byte 단위로 일치했다.
- 기본 Python에는 torch가 없었고, Isaac Lab Python에서 최초 pytest 실행은 ROS 자동 plugin의 lark 누락으로 collection 전에 실패했다. 기존 개발 기록의 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` 설정으로 재실행한 결과가 위140개 통과다. 패키지 설치나 환경 수정은 하지 않았다.
- GPU·Isaac Sim·학습·Play는 실행하지 않았다. 원격 문서의 GPU·학습 수치는 원격에서 기록한 기존 결과이며 이번 머신에서 재현한 결과가 아니다.
- CLI push는 인증할 수 없다. GitHub commit 생성 도구도 기존 로컬 커밋의 작성자·시각을 지정할 수 없어 동일 커밋을 그대로 올리는 수단으로 사용하지 않았다. 사용자가 문서 저장소를 먼저 push하고 상위 저장소를 이어 push할 수 있도록 로컬 병합 커밋을 남긴다.

```bash
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact_v1.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact.py \
  src/inspire_sweep_baseline/tests/test_sweep_v0.py \
  src/inspire_sweep_baseline/tests/test_stabilize_sweep.py
```
