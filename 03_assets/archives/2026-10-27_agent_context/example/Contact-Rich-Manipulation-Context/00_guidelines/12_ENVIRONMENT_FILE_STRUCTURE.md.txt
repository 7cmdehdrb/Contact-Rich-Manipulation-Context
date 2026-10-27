# Inspire Sweep 환경 파일 구조

[지침 안내](README.md) · [개발 지침](09_DEVELOPMENT_GUIDE.md) · [활성 환경](../02_implementation/08_ACTIVE_ENVIRONMENTS.md) · [구조 이관 기록](../02_implementation/logs/2026-10-23_environment_structure_migration.md)

기준일: 2026-10-23. 적용 대상은 `src/inspire_sweep_baseline`과 이후 이 패키지에 추가하는 환경이다. 사용자 요청에 따라 환경별 폴더와 패키지 루트의 설정 파일을 역할별 구조로 통합한다. 구조 이관의 실제 검증 상태는 [개발 로그](../02_implementation/logs/2026-10-23_environment_structure_migration.md)에 기록한다.

## 1. 기본 배치

2026-10-27 공통 지침: 아래의 현재 디렉토리 구조를 유지한다. 환경 수정·파생 환경 추가 중 파일·함수 이동이나 재구성을 임의로 수행하지 않는다. 아래 이관·이동 절차는 사용자가 구조 변경을 명시적으로 요청했을 때 적용하며, 일반 기능 수정에 대한 이동 허가가 아니다. 직접 수정과 새 파생 환경 생성의 구분, 부모 보존, 전체 대조와 의도 기록은 [개발 지침](09_DEVELOPMENT_GUIDE.md)을 따른다.

```text
src/inspire_sweep_baseline/
├── README.md
├── pyproject.toml
├── scripts/                       train.py, play.py, 수집·분석 실행기
├── tests/                         CPU 계약 검사와 simulator probe
└── inspire_sweep_baseline/
    ├── __init__.py                Gym 등록
    ├── agent/                    PPO Cfg·정책 모델·runner
    ├── assets/                   USD·형상·스포너·자산 경로·센서 기하
    │   └── scenes/               SceneCfg와 장면 구성 함수
    ├── mdp/
    │   ├── actions/              Action Cfg
    │   ├── action_functions/     Action term 구현
    │   ├── commands/             Command Cfg
    │   ├── command_functions/    Command term 구현
    │   ├── observations/         Observation Cfg
    │   ├── observation_functions/
    │   ├── events/               Event Cfg
    │   ├── event_functions/
    │   ├── rewards/              Reward Cfg
    │   ├── reward_functions/
    │   ├── curricula/            Curriculum Cfg
    │   ├── curriculum_functions/
    │   ├── terminations/         Termination Cfg
    │   ├── termination_functions/
    │   └── common/               여러 MDP 역할이 공유하는 계산·상태·상수
    ├── envs/                     EnvCfg 조합
    └── runtime/                  실제 Env 클래스·lifecycle·telemetry
```

Python 패키지에 필요한 `__init__.py`는 각 폴더에 둘 수 있다. `agent`는 단수이며, `action_functions`와 `curriculum_functions`의 철자를 사용한다. 패키지 바깥의 `scripts/`, `tests/`, `README.md`, `pyproject.toml`은 실행·검증·설치 역할을 유지한다.

## 2. 파일을 배치하는 기준

| 위치 | 포함할 코드 | 책임 경계 |
| --- | --- | --- |
| `agent/` | PPO runner Cfg, actor/critic·obstacle encoder 모델, curriculum을 연결하는 PPO runner | PPO 관련 코드만 둔다. 환경의 reward 계산이나 SceneCfg를 넣지 않는다. |
| `assets/` | 환경 구성 자산, USD 경로, 형상·물성 스포너, tactile geometry | 자산을 생성·참조하는 코드와 정적 데이터를 둔다. |
| `assets/scenes/` | 로봇·물체·센서 배치를 선언하는 SceneCfg, 장면 구성 함수 | EnvCfg에서 재사용할 장면 구성을 담당한다. |
| `mdp/<역할>/` | Manager 그룹 Cfg와 개별 term Cfg | term 순서, 함수 연결, params, weight를 선언한다. 실행 계산은 함수 폴더로 분리한다. |
| `mdp/<역할>_functions/` | 해당 Cfg가 사용하는 함수·상태를 갖는 term 클래스 | 입력과 출력, reset과 cache 갱신 의미를 유지한다. |
| `mdp/common/` | 둘 이상의 MDP 역할이 사용하는 상태 조회, 센서 계산, 기하·용량 상수 | 공유할 필요가 있는 코드만 둔다. 특정 역할의 Cfg를 옮기는 곳이 아니다. |
| `envs/` | Scene·Manager·PPO 등록에서 사용할 EnvCfg 클래스 | 기존 부모를 상속하고 구성요소를 조합한다. runtime Env 구현은 두지 않는다. |
| `runtime/` | ManagerBasedRLEnv 파생 클래스, reset/step 순서, lifecycle·telemetry | 학습 중 실행되는 환경 객체를 담당한다. EnvCfg와 분리한다. |
| 패키지 `__init__.py` | task ID와 runtime·EnvCfg·PPO entry point 등록 | 현재 파일 위치로 등록한다. |

`runtime/`, `mdp/common/`, `assets/scenes/`와 `agent/`의 PPO 모델·runner 포함은 이번 구조 검토에서 사용자 확인을 받은 범위다. 이 기준으로도 분류되지 않는 파일은 임의로 끼워 넣거나 새 책임을 만들지 않고 사용자에게 확인한다.

## 3. 계열과 버전을 모으는 방법

같은 기반 구성·인자를 공유하는 v0, v1, v2 등의 클래스는 역할별 동일 파일에 둔다. 버전마다 디렉터리를 만들지 않는다. 파일명은 계열을 표현하고 클래스명은 기존 버전을 식별한다. 예를 들어 Holding v0/v1/v2의 EnvCfg는 `envs/contact_sweep_clutter_fusion_holding_envs.py`, 보상 Cfg는 `mdp/rewards/contact_sweep_clutter_fusion_holding.py`, PPO Cfg는 `agent/contact_sweep_clutter_fusion_holding_ppo_cfg.py`에 둔다.

| 환경 계열 | EnvCfg 파일 |
| --- | --- |
| Baseline·Realistic Physics·Initial Privileged·Baseline Tactile | `envs/sweep_envs.py` |
| Omni·Dex Omni | `envs/sweep_omni_envs.py` |
| Renewal·Dex/Tactile Renewal·Renewal OSC | `envs/sweep_omni_renewal_envs.py` |
| Contact Sweep | `envs/contact_sweep_envs.py` |
| Contact Sweep Clutter·Curriculum·FT Test | `envs/contact_sweep_clutter_envs.py` |
| Contact Sweep Clutter Fusion | `envs/contact_sweep_clutter_fusion_envs.py` |
| Fusion Holding | `envs/contact_sweep_clutter_fusion_holding_envs.py` |
| Fusion Holding OSC | `envs/contact_sweep_clutter_fusion_holding_osc_envs.py` |
| Fusion Holding ObjectRandom 계열 | `envs/contact_sweep_clutter_fusion_holding_osc_object_random_envs.py` |

공유 파일 안에서는 기반 클래스를 먼저 선언하고 파생 클래스를 뒤에 둔다. 같은 이름의 서로 다른 함수가 한 파일로 모이면 이름 충돌을 해소하되 호출 대상과 계산을 바꾸지 않는다. 서로 다른 역할의 코드가 import 순환을 일으키면 공유 계산의 실제 책임을 확인하고 `mdp/common/` 등 승인된 위치로 분리한다. 독립 선언이 계약인 Cfg를 단순히 중복을 줄이기 위해 상속으로 바꾸지 않는다.

## 4. 등록·import·자산 경로

Gym task ID와 클래스의 의미는 유지하고, Python module entry point는 새 위치로 갱신한다. 예를 들어 Holding v2의 EnvCfg entry point는 `inspire_sweep_baseline.envs.contact_sweep_clutter_fusion_holding_envs:FusionHoldingV2EnvCfg`다. PPO의 `class_name` 문자열도 `agent/`의 실제 모델 위치를 가리켜야 한다.

사용자 확인에 따라 이전 module 경로를 유지하는 호환 파일·alias는 만들지 않는다. 현재 코드의 import, scripts, tests, probe, 등록 문자열, 현행 문서 링크를 함께 갱신한다. 과거 로그의 당시 경로·명령·저장된 YAML은 역사적 기록으로 보존한다. 외부 코드가 이전 module 경로를 직접 import하면 새 위치로 수정해야 하며, 과거 설정의 문자열을 다시 import하는 도구도 같은 확인이 필요하다.

자산의 내용·경로 선택 규칙을 구조 이관 중 임의로 변경하지 않는다. `__file__`의 부모 단계 수에 의존하는 경로는 이동 후 실제 대상을 다시 확인한다. 특히 Clutter의 `src/scene_randomization` 읽기 전용 참조, Fusion visibility 참조, 로봇 USD·tactile JSON, `INSPIRE_SWEEP_SHELF_USD_PATH`를 검사한다. `pyproject.toml`의 package discovery와 package data도 새 배치와 일치해야 한다.

## 5. 동작을 보존하는 검증 순서

1. 루트와 관련 submodule의 `HEAD`, 작업트리 변경, 미추적 파일을 기록한다. 기존 사용자 작업과 학습 로그를 보존한다.
2. 이동 전 전체 task 등록, 실제 EnvCfg·PPO 인스턴스, runtime class, 상속, 필드 순서·값·callable을 저장하고 기존 CPU 검사를 실행한다. 기존 실패와 새 실패를 구분한다.
3. 파일·symbol별 이전 위치와 새 위치를 대응시킨다. Cfg와 함수가 섞인 파일은 symbol 단위로 나눈다.
4. 구조와 참조만 변경한다. task ID, 관측·action 순서/차원, 보상·종료·curriculum, reset 순서, PPO 설정, experiment 이름을 보존한다.
5. 실제 Isaac Sim launcher에서 전체 task의 runtime·EnvCfg·PPO를 import하고 설정 스냅샷을 다시 만든다. 이동으로 바뀐 module 경로만 대응시킨 뒤 필드 순서·값·callable·MRO를 비교한다. AST 검사만으로 실제 import 성공을 대신하지 않는다.
6. 변경에 맞는 CPU 계약·모델·checkpoint 검사를 실행한다. 최신 Fusion·Holding 계열은 환경 생성, reset/step, 관측 유한성, PPO 연결과 저장/복원 범위를 별도로 기록한다.
7. 실제 실행한 명령·결과·실패·미검증 범위를 개발 로그에 남기고 현행 문서 링크를 검사한다. 짧은 smoke 결과를 장기 학습 성능으로 해석하지 않는다.

Omni의 로컬 운동 페널티는 이동 후 `mdp/reward_functions/goal_rewards.py`의 `action_rate_l2`·`joint_vel_l2`를 사용한다. raw Action 변화량·실제 관절 속도의 제곱합, Arm/Hand 네 항 분리, −0.03/−0.03/−0.03/−0.01 계수와 기존 출력 상한을 보존한다. 세부 예외·사용자 지정 파생 설정은 [개발 지침](09_DEVELOPMENT_GUIDE.md#omni-운동-페널티-필수-규칙--2026-10-15-사용자-지시)과 해당 환경 계약을 따른다.

## 6. 이관 전 기준과 복구

| 저장소 | 구조 이관 직전 HEAD |
| --- | --- |
| 코드 workspace | `a30d0b4d92a7bd3c50b8d03516f1ada056da85c8` |
| 문서 submodule | `4d1158538eb9e6be69a6e0c18e772696169946cd` |

현재 작업트리를 덮어쓰는 `reset --hard`나 `clean`으로 복구하지 않는다. 아래는 기존 작업을 보존하면서 기준 commit을 별도 디렉터리에서 확인하는 예시이며, 이관 작업에서 실제 실행한 명령은 아니다. 대상 경로가 이미 있으면 비어 있는 다른 경로를 선택한다.

```powershell
git worktree add --detach outputs/recovery/workspace-a30d0b4 a30d0b4d92a7bd3c50b8d03516f1ada056da85c8
git -C example/Contact-Rich-Manipulation-Context worktree add --detach C:/python/Contact-Rich-Manipulation/outputs/recovery/context-4d11585 4d1158538eb9e6be69a6e0c18e772696169946cd
```

복구 checkout의 submodule은 해당 commit이 기록한 상태를 따로 준비하고, 실행할 Python·외부 shelf 자산·checkpoint를 확인한다. 이관 전 미추적 `docs/plan/PLAN5.md`는 위 commit에 포함되지 않으므로 기존 파일을 별도로 보존한다. 학습 로그는 복구 대상 소스와 분리하며 `logs/rsl_rl`을 이동·삭제하지 않는다. 이전 경로가 필요한 과거 분석은 이 기준 checkout에서 재현할 수 있다.
