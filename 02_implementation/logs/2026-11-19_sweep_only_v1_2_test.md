# Sweep Only v1_2 Test: 원시 접촉 카운트와 보상 계수

## 요청과 기준

사용자는 학습 중인 GPU를 사용하지 않고 v1-Test를 직접 상속한 v1_2-Test를 추가하도록 요청했다. 역방향 −25, 정방향 100, 접촉 계수의 20 나눗셈 제거가 확정 요구다. 앞선 분석에서 제안한 1500/−75는 적용하지 않는다.

Workspace 기준 commit은 `126056af622e81d4e3cbe9d9c4e525b8d62952eb`, 문서 저장소 기준은 `299e92466d9130f7d93eedc93052b16066ed4dbc`다. 시작 시 코드 작업트리는 깨끗했고 문서 서브모듈 포인터 차이가 있었으며 이를 보존했다. 학습 로그·프로세스·체크포인트를 수정하거나 정리하지 않았다.

## 구현과 최종 대조

| 계약 | v1-Test | v1_2-Test |
| --- | --- | --- |
| Gym ID | Inspire-Sweep-Only-v1-Test | Inspire-Sweep-Only-v1_2-Test |
| EnvCfg | SweepOnlyV1TestEnvCfg | SweepOnlyV1_2TestEnvCfg, v1 직접 상속 |
| Runtime | SweepOnlyEnv | 동일 |
| PPO | SweepOnlyV1TestPPORunnerCfg | SweepOnlyV1_2TestPPORunnerCfg, v1 직접 상속 |
| 로그 experiment name | inspire_sweep_only_v1_test | inspire_sweep_only_v1_2_test |
| sweep_progress Weight | 50 | 100 |
| 접촉 계수 | count / 20 | count |
| sweep_retreat Weight | −10 | −25 |
| Deadzone | 30° 고정 | 동일; v2를 상속하지 않음 |

설정은 기존 `envs/stabilize_sweep_envs.py`, PPO는 `agent/stabilize_sweep_ppo_cfg.py`, 등록은 패키지 `__init__.py`에 추가했다. 공유 EnvCfg의 `sweep_normalize_contact_count` 기본값은 True이며 새 자식만 False다. 기존 runtime의 finish 호출이 이 값을 전달하고 `mdp/common/stabilize_sweep_state.py`는 False일 때 정규화 없이 카운트를 float로 사용한다. 설정 필드가 없는 기존 CPU fixture에서도 기본 True로 동작한다.

카운트 상한 20, 2-of-3 접촉 판정, 카운트 증가 1·감소 2, 12cm 높이 조건, 힘·방향 계수, 이전 거리 갱신 및 부분 reset은 유지했다. 동일 상태에서 정방향은 `100 * delta_positive * count * alignment`, 역방향은 `-25 * delta_negative`다. 기존 v1 대비 정방향 40배·역방향 2.5배이며 실제 학습 행동·수령액이 같은 배수라는 주장은 아니다.

상속과 diff를 대조한 결과 Scene·물성·초기화·Command·Observation·Action·Reach 및 나머지 Reward·Termination·Curriculum은 그대로다. PPO는 experiment name만 다르다. 부모 v1과 기존 v2 클래스 정의는 변경 전과 AST가 동일하다. 새 설정 기본값 True의 상태 계산 결과도 변경 전 코드와 같음을 CPU로 확인했다. Deadzone은 `StabilizeSweepTestEventsCfg`가 복사하는 `SweepSimpleEventsCfg.object_spawn`의 0.5235987755982988 rad이며 방향 커리큘럼은 비활성이다.

## 검증

GPU·Isaac Sim·학습을 실행하지 않았다. CPU 환경변수는 `CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`이다.

```bash
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest \
  src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q \
  -k 'sweep_height_setting or family_runtime or sweep_only or contact_decay or sweep_reward'
```

결과: 10 passed, 85 deselected. 최초 실행은 시스템 ROS pytest 플러그인의 `lark` 미설치로 수집 전에 실패했다. 설치·환경 변경 없이 외부 플러그인 자동 로드만 끄고 위 명령으로 통과했다.

추가 임시 검사 `/tmp/check_sweep_v1_2.py`는 실제 상태 클래스 정의를 CPU에서 실행했다. 초기 카운트 0–20, 전진·후퇴·정지, 정상/비스듬한/역방향 힘, 높이 경계·초과, 접촉 없음의 378행 조건에서 정방향 40배·역방향 2.5배, 기존 기본 동작과의 일치, 부분 reset을 확인했다. 자식 설정 정의 실행과 등록·runner·runtime 전달·구문을 정적으로 확인했다. CUDA 초기화 없음과 Isaac Sim import 없음도 확인했다. 전체 Isaac 환경 구성 로드와 물리 실행을 대신하는 검사는 아니다.

변경 Markdown 5개 수식 검사, 문서 저장소 변경 4개 파일의 링크 검사(오류 0), workspace·문서 저장소 `git diff --check`를 통과했다.

신규 ID의 실제 reset·step·학습 성능 및 성공률은 사용자 요청에 따라 미검증이다. 실행 명령과 계약은 [환경 설명](../environments/SWEEP_ONLY.md#sweep-only-v1_2-test)에 기록했다.
