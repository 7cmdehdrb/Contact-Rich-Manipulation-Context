# 원격 학습 로그 선택 다운로드

## 요청과 변경 의도

사용자는 `irol@192.168.0.250:~/Contact-Rich-Manipulation/logs/rsl_rl/inspire_sweep_single_contact_v0`를 `scp -r`로 받으면서 체크포인트 파일이 지나치게 많다고 보고했다. 각 실행의 1000 단위 체크포인트와 최신 5개만 받고, 저장 위치는 workspace의 `logs/TEMP/오늘날짜`로 자동 지정하도록 요청했다.

기존에는 수동 지정한 `logs/TEMP/wr1123`에 전체 트리를 받았다. 이번에는 [download_training_logs.py](../../../../src/inspire_sweep_baseline/scripts/download_training_logs.py)를 추가했다. 환경·학습 코드·기존 로그는 수정하지 않았다.

## 최종 동작과 사용법

workspace 루트에서 실행한다. 첫 명령은 원격 목록만 조회하며 다운로드하거나 목적지 폴더를 생성하지 않는다. 두 번째 명령이 실제 전송이다.

```bash
python3 src/inspire_sweep_baseline/scripts/download_training_logs.py \
  --host irol@192.168.0.250 \
  --remote-dir '~/Contact-Rich-Manipulation/logs/rsl_rl/inspire_sweep_single_contact_v0' \
  --dry-run

python3 src/inspire_sweep_baseline/scripts/download_training_logs.py \
  --host irol@192.168.0.250 \
  --remote-dir '~/Contact-Rich-Manipulation/logs/rsl_rl/inspire_sweep_single_contact_v0'
```

- `--host`와 `--remote-dir`는 필수 인자이며 고정 서버·폴더 기본값은 없다. 위 명령의 값은 예시로, 실행할 때 원하는 서버와 폴더로 바꾼다. `--host`에는 `user@host` 또는 SSH config alias를 지정하고, `--port`로 기본 22 포트를 변경할 수 있다.
- 기본 저장 경로는 `logs/TEMP/YYYY-MM-DD/<원격 폴더명>`이다. 날짜는 실행 시점 한국 시간 UTC+9이며, 위 예시를 2026-11-23 실행하면 `logs/TEMP/2026-11-23/inspire_sweep_single_contact_v0`다. 현재 작업 디렉터리와 무관하게 스크립트의 workspace를 기준으로 한다. `--dest-root`로 날짜 폴더의 상위 경로를 변경할 수 있다.
- 각 체크포인트 디렉터리에서 파일명 끝의 iteration 숫자로 정렬한다. `--interval 1000`의 배수인 체크포인트와 `--latest 5`의 최신 체크포인트의 합집합을 받는다. `model_0.pt`도 배수에 포함하며 중복 다운로드 목록은 만들지 않는다. 수정 시각이나 문자열 정렬을 사용하지 않는다.
- `.pt` 이외 일반 파일은 모두 받으므로 TensorBoard events, params, git diff, JSON 등은 유지된다. 파일명이 `numerical_failure`로 시작하면 `.pt`도 항상 포함한다. 예를 들어 `numerical_failure.pt`, `numerical_failure.json`, `numerical_failure_123.pt`는 배수·최신 개수 제한 밖에서 보존한다. 해당 파일이 없어도 정상 진행한다. 그 외 끝에 iteration 숫자가 없는 `.pt`는 제외하며 파일명을 출력한다. 심볼릭 링크·빈 디렉터리는 복제하지 않는다.
- SSH로 원격 Python 3에서 읽기 전용 목록을 만들고, NUL 구분 파일 목록을 rsync에 전달한다. 로컬에 Python 3·ssh·rsync, 원격에 Python 3·rsync가 필요하다. 기존 SSH 인증을 사용한다.
- 같은 날 재실행하면 동일 목적지에 rsync의 크기·수정 시각 기준으로 갱신한다. 성장한 events 파일도 갱신한다. 중단된 전송은 `.rsync-partial`을 이용한다. 삭제 옵션이 없어 이미 받은 과거 최신 체크포인트나 사용자 파일은 남는다. 따라서 반복 실행한 목적지에 존재하는 전체 `.pt` 수는 이번 선택 개수보다 많을 수 있다.

## 검증 결과

- Python 본문 및 원격 inventory 코드의 컴파일, `--help`, 잘못된 interval/latest/host 인자의 오류 처리를 확인했다.
- 임시 디렉터리에서 SSH만 로컬 실행 대역으로 교체하고 실제 rsync를 사용해 전체 CLI 전송을 검증했다. 두 run의 독립 선택, 1000 배수와 최신 5개의 합집합, 숫자 순서, latest 0, 일반적인 번호 없는 `.pt` 제외를 확인했다.
- 공백·세미콜론을 포함한 원격 디렉터리, 공백·개행을 포함한 상대 경로에서 선택 파일과 다운로드 내용이 정확히 일치했다. `.pt`라는 이름의 디렉터리 안에 있는 설정 파일도 보존됐다.
- dry-run의 목적지 미생성, 동일 파일 재전송 시 수정 시각 보존, 성장한 events 갱신, 기존 로컬 파일 비삭제, 심볼릭 링크 제외를 확인했다. 전송 실험은 시스템 임시 디렉터리 안에서 수행하고 자동 제거했다.
- 기존 `logs/TEMP/wr1123/inspire_sweep_single_contact_v0`는 목록만 읽었다. `2026-11-20_20-56-01`은 번호 있는 체크포인트 600개에서 35개, `2026-11-22_17-14-33`은 306개에서 21개를 선택했다. 후속 수정 후에는 `numerical_failure.pt`까지 포함하여 `.pt` 총 907개 중 57개를 선택하며, 기타 파일을 포함한 전체 선택은 66개다.
- 변경 문서의 Markdown 수식 검사와 외부 코드 링크 검사, 문서 저장소 전체 링크 검사(Markdown 655개, 오류 0개), 양쪽 저장소의 `git diff --check`를 통과했다. 최종 작업트리 변경은 새 실행기와 이 개발 로그뿐이며 기존 문서 서브모듈 커밋 차이는 보존했다.

## 후속 요청 반영: 장애 파일 보존과 원격 위치 명시

사용자가 `numerical_failure`는 있을 때 반드시 포함해야 하며 서버·대상 폴더가 바뀔 수 있다고 명확히 했다. 초기 구현은 번호 없는 `.pt`를 모두 제외했고 `.250`의 특정 폴더를 기본값으로 사용했다. 이를 `numerical_failure` 접두어 파일은 선택 제한과 무관하게 포함하고, `--host`·`--remote-dir`를 필수 인자로 받도록 수정했다. 기존 날짜 경로·체크포인트 선택 규칙·rsync 전송·기존 파일 보존은 유지했다.

후속 검증에서는 임시 SSH 대역과 실제 rsync로 서버 이름과 원격 폴더를 모두 바꾼 두 실행을 확인했다. 장애 파일 3종이 있는 경우 모두 전송됐고, 없는 경우도 정상 완료됐다. dry-run·재실행과 파일 내용 일치도 확인했다. latest 0에서 숫자 있는 장애 파일도 빠지지 않고 일반 체크포인트 최신 개수를 소모하지 않음을 확인했다. host/path 인자 누락은 네트워크 접속 전에 argparse 오류로 종료했다. 기존 로컬 목록에서 장애 `.pt`·JSON의 선택을 확인했다. 이번 후속 작업에서도 실제 원격 접속·다운로드 및 기존 학습 로그 수정은 수행하지 않았다.

## 영향과 미검증 범위

새 다운로드 실행기만 추가했고 기존 `logs/TEMP`, `logs/rsl_rl`, 환경 구성·보상·PPO·학습 실행기는 변경하지 않았다. 코드 저장소와 문서 서브모듈의 기존 커밋·사용자 변경을 보존했다.

실제 `.250` SSH 접속·인증·원격 도구 설치 상태·다운로드는 실행하지 않았다. 학습 중의 원격 트리는 원자적 스냅샷이 아니므로 목록 조회 이후 생성된 파일은 다음 실행에서 선택된다. 전송 중 원격 파일의 삭제·쓰기 또는 디스크·네트워크 오류로 실패할 수 있으며, 실패는 종료 코드와 메시지로 표시된다. 저장 중인 최신 체크포인트의 일관성 검사와 torch 로딩 검증은 수행하지 않는다. GPU·Isaac Sim·학습 검증은 이번 실행기 변경 범위에 필요하지 않아 수행하지 않았다.
