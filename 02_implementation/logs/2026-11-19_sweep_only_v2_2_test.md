# Sweep Only v2_2 Test: v1_2 보상과 Deadzone 제거

## 요청·기준·변경

사용자 요청은 v1_2-Test를 직접 상속하고 동일 보상에서 Deadzone만 제거하는 것이다. 학습 중 GPU 사용 금지와 코드만 수정하는 이전 지시를 유지했다.

Workspace HEAD `126056af622e81d4e3cbe9d9c4e525b8d62952eb`, 문서 저장소 HEAD `299e92466d9130f7d93eedc93052b16066ed4dbc`를 기준으로 기존 미커밋 v1_2 코드·문서 변경과 서브모듈 포인터 차이를 보존했다. 이번 작업 직전 수정 대상 세 Python 파일을 `/tmp/sweep_v2_2_before.json`에 저장해 비교했다.

| 계약 | 부모 v1_2-Test | 자식 v2_2-Test |
| --- | --- | --- |
| Gym ID | Inspire-Sweep-Only-v1_2-Test | Inspire-Sweep-Only-v2_2-Test |
| EnvCfg | SweepOnlyV1_2TestEnvCfg | SweepOnlyV2_2TestEnvCfg, 부모 직접 상속 |
| Runtime | SweepOnlyEnv | 동일 |
| Deadzone | 30° 고정 | 0° 고정 |
| 정방향·역방향 Weight | 100 / −25 | 동일 |
| 접촉 계수 | 원시 카운트 0–20 | 동일 |
| Runner | SweepOnlyV1_2TestPPORunnerCfg | SweepOnlyV2_2TestPPORunnerCfg, 부모 직접 상속 |
| Experiment name | inspire_sweep_only_v1_2_test | inspire_sweep_only_v2_2_test |

역할별 기존 파일 `envs/stabilize_sweep_envs.py`, `agent/stabilize_sweep_ppo_cfg.py`, 패키지 `__init__.py`에 추가했다. 자식 EnvCfg는 부모 post-init 이후 목표 방향 제외 반각만 0으로 설정한다. 방향 커리큘럼은 기존 비활성을 유지한다. Scene·물성·초기화 알고리즘·목표 거리·Observation·Action·모든 Reward·Termination·기타 Curriculum·PPO 설정은 부모에서 변경하지 않았다. runtime·계산 함수 수정은 없다.

## 검증·최종 대조

표준 Python 라이브러리만 사용한 CPU 코드 검사를 통과했다. 실제 파생 클래스 정의를 최소 부모 경계와 함께 실행하여 직접 상속, 100/−25, 정규화 False, Deadzone 0, 부모의 30° 보존을 확인했다. 자식에서 제외 반각만 부모값으로 되돌리면 인스턴스 속성이 동일했다. 이는 전체 Isaac 설정 로드 검증을 대신하지 않는다.

실제 Gym 등록 루프를 register stand-in으로 실행하여 신규 ID의 runtime·EnvCfg·runner 문자열을 확인했다. 신규 클래스와 등록 한 항목을 제외한 AST가 작업 직전 세 파일과 동일하여 부모와 기존 모든 버전이 보존됨을 확인했다. 세 파일 구문 검사도 통과했다. 별도 영구 테스트 파일은 추가하지 않았다.

GPU·torch·Isaac Sim import, 환경 reset/step, 학습 실행은 하지 않았다. 학습 로그·프로세스·체크포인트는 건드리지 않았다. 실제 신규 환경 실행과 성공률·성능은 미검증이다. 실행 안내와 최종 계약은 [환경 설명](../environments/SWEEP_ONLY.md#sweep-only-v2_2-test)에 있다.
