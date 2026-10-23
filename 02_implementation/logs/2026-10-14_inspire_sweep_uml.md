# Baseline 학습 환경 UML 작성 기록

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [정적 자산](../../03_assets/README.md)

작성일: 2026-10-14. `src/inspire_sweep_baseline`의 현재 학습 환경을 코드에서 확인해 두 개의 UML 차트로 표현했다. 환경·학습 코드와 연구 설계는 변경하지 않았다.

## 결과물

| 차트 | 표현하는 내용 | 그림의 규모 |
| --- | --- | --- |
| [학습 실행과 Isaac Lab 연결](../../03_assets/inspire-sweep-training.html) | task 선택·설정 로딩, 공통 실행 클래스 생성, Wrapper, rollout과 PPO 업데이트 | UML sequence, 참여자 5개·메시지 12개·iteration fragment 1개 |
| [환경 상속과 구성 함수](../../03_assets/inspire-sweep-inheritance.html) | 네 환경 Cfg의 부모, 물성 함수 직접 호출, Manager에 연결하는 관측·goal term | UML class, 환경 Cfg와 기반 클래스 5개·모듈 묶음 2개·관계 8개 |

사용자가 선택한 diagram-design 기본 밝은 스타일을 적용했다. 두 결과물은 CSS와 SVG를 포함한 자체 포함 HTML이며 `doc-wide`의 `1280 × 720` viewBox를 사용한다. 별도 이미지 파일은 생성하지 않았다. 브라우저에서 열 수 있고, 좁은 화면에서는 차트 영역만 가로로 스크롤한다. 기본 Google Fonts를 선언하되 폰트가 없는 환경의 시스템 대체 글꼴도 유지했다.

## 확인한 코드 관계

Task 등록은 [`__init__.py`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py), 환경 생성과 runner 연결은 [`scripts/train.py`](../../../../src/inspire_sweep_baseline/scripts/train.py)를 읽었다. 실행 클래스 [`InspireSweepEnv`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/sweep.py)는 `ManagerBasedRLEnv`를 상속하며 네 task가 이를 공유한다.

Cfg 상속은 다음과 같다.

- `InspireSweepEnvCfg → ManagerBasedRLEnvCfg`
- `InspireSweepRealisticPhysicsEnvCfg → InspireSweepEnvCfg`
- `InspireSweepRealisticInitialPrivilegedEnvCfg → InspireSweepRealisticPhysicsEnvCfg`
- `InspireSweepOmniEnvCfg → InspireSweepEnvCfg`

삼각형은 자식에서 부모를 향한다. Realistic Physics와 Omni는 `__post_init__()`에서 `apply_realistic_physics()`를 직접 호출한다. Omni가 Realistic Physics Cfg를 상속하는 것으로 그리지 않았다. 관측·goal 함수의 연결은 직접 호출과 구분해 Observation/Event/Reward/TerminationManager가 실행할 term의 등록으로 표현했다. `super().__post_init__()` 호출 순서, Event/Observation/Termination Cfg의 추가 상속과 PPO runner 상속은 차트 아래 표에 기록했다.

Isaac Lab의 [`ManagerBasedRLEnv.step()`](../../../../IsaacLab/source/isaaclab/isaaclab/envs/manager_based_rl_env.py), [`RslRlVecEnvWrapper`](../../../../IsaacLab/source/isaaclab_rl/isaaclab_rl/rsl_rl/vecenv_wrapper.py), Hydra 설정 로딩을 확인했다. 학습 루프는 이 Workspace의 Isaac Lab Python 환경에 설치된 **rsl-rl-lib 5.0.1**의 `rsl_rl/runners/on_policy_runner.py`를 읽었다. 설치 버전이 바뀌면 runner 내부 구현은 다시 확인해야 한다.

## 그림에서 묶거나 생략한 내용

AppLauncher·Gym registry·Hydra는 학습 스크립트 참여자에, PPO는 Runner 참여자에 묶었다. Isaac Lab의 여러 Manager·Scene·SimulationContext/PhysX 호출도 실행 계층 참여자에 묶었다. 생성자와 wrapper 초기 reset의 내부 호출, rollout transition 저장·returns 계산·checkpoint 기록은 본문 설명에서 연결했다.

두 번째 차트의 MDP 박스는 주요 관측과 Omni goal 함수를 묶은 모듈 그룹이다. 개별 term 클래스의 전체 계보, 개별 보상 항·임계값·CLI 옵션·PPO 수치 전체는 그림에서 생략하고 [활성 환경 계약](../08_ACTIVE_ENVIRONMENTS.md) 및 코드로 연결했다. 이번 요청의 두 차트 범위를 유지하며 추가 환경이나 성과는 만들지 않았다.

## 검증

`diagram-design/scripts/self_check.py`가 두 HTML 모두 통과했다. 접근성 title·description, 단일 파일 안전성, viewBox 내 콘텐츠를 검사했다. 실제 Chrome 렌더에서 노드 안의 글자 범위와 화살표 라벨 마스크의 노드 겹침을 확인해 발견된 배치를 수정했다. 최종 글자 넘침·라벨 마스크 충돌은 없었다.

공통 레이아웃을 390px viewport에서 확인했다. 페이지 가로 넘침 없이 차트의 1280px 너비를 유지하는 로컬 스크롤이 동작했고, 검증 후 브라우저 크기 설정을 복원했다. 상대 문서·코드 링크, 변경 Markdown의 수식 형식과 whitespace도 검사했다.

이 작업에서는 Isaac Sim의 실제 환경 생성, train/play, GPU 물성 적용 또는 학습 성능 평가를 실행하지 않았다. 그림의 학습 주기는 코드에서 확인한 실행 구조이며 새 실험 결과가 아니다.
