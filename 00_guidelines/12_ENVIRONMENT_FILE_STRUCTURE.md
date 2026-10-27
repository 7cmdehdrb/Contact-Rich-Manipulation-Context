# 환경 파일 구조

활성 기반은 `src/inspire_sweep_baseline/inspire_sweep_baseline`이다. 현재 구조를 유지하고, 파일·함수 이동은 명시적인 구조 변경 요청에서만 수행한다. 동작 보존과 전체 대조는 [개발 지침](09_DEVELOPMENT_GUIDE.md)을 따른다.

## 역할별 배치

| 위치 | 책임 |
| --- | --- |
| `envs/` | EnvCfg 상속과 구성요소 조합 |
| `runtime/` | 실제 Env 클래스, reset/step, lifecycle, telemetry |
| `assets/`, `assets/scenes/` | 자산·스포너 및 SceneCfg |
| `mdp/actions/`, `commands/`, `observations/`, `events/`, `rewards/`, `curricula/`, `terminations/` | 역할별 Manager Cfg, term 순서·함수·params·weight |
| `mdp/action_functions/` 등 역할별 `*_functions/` | 실행 함수와 상태를 가진 term 클래스. 커리큘럼은 `curriculum_functions/` |
| `mdp/common/` | 여러 MDP 역할에서 공유하는 계산·상태 |
| `agent/` | PPO 설정·모델·runner |
| 패키지 `__init__.py` | Gym task ID와 runtime·EnvCfg·PPO 등록 |

패키지 바깥의 `scripts/`, `tests/`, `README.md`, `pyproject.toml`은 실행·검증·안내·설치 역할을 유지한다. 같은 계열의 버전은 역할별 같은 파일에 모으고, 버전마다 폴더를 만들지 않는다.

## 현재 계열의 EnvCfg

| 계열 | `envs/` 아래 파일 |
| --- | --- |
| Holding | `contact_sweep_clutter_fusion_holding_envs.py` |
| Holding OSC | `contact_sweep_clutter_fusion_holding_osc_envs.py` |
| Holding ObjectRandom | `contact_sweep_clutter_fusion_holding_osc_object_random_envs.py` |
| Final | `final_envs.py` |

보상·종료·커리큘럼 등도 기존 역할별 파일에 둔다. 예를 들어 Final의 종료 Cfg는 `mdp/terminations/final.py`다. 독립 선언인 Cfg를 중복 제거 목적으로 상속 구조로 바꾸지 않는다.

## 추가·수정 확인

1. 사용자 요청이 기존 환경 직접 수정인지 새 파생 환경 생성인지 구분한다. 요청 밖의 함수·상속·파일 위치는 유지한다.
2. 등록 문자열, import, PPO 모델 경로와 실제 클래스를 확인한다. 자산의 내용·선택 규칙 및 읽기 전용 참조를 보존한다.
3. 전체 Manager 설정과 runtime·PPO를 작업 전후 대조한다. 새 환경은 부모와의 차이 및 부모의 불변성도 확인한다.
4. 변경에 필요한 설정 검사·실제 import·reset/step 검증을 수행하고 실행 범위를 기록한다. 정적 검사를 물리 실행 성공으로 보고하지 않는다.
5. [현재 환경 안내](../02_implementation/08_ACTIVE_ENVIRONMENTS.md), 해당 환경 설명, 개발 로그를 갱신한다.

명시적으로 구조 변경을 요청받았을 때는 이동 전후 symbol·경로 대응표와 설정 스냅샷도 남기고 import·등록·자산 경로를 검증한다. 과거 구조 이관 기록은 [정리 전 백업](../02_implementation/history/2026-10-27_agent_context/README.md)에서 필요할 때만 확인한다.
