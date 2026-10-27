# Omni v4 — 속도 비용과 종료 조건

[로그 안내](README.md) · [활성 환경](../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md.txt)

기록일: 2026-10-15. 사용자 요청으로 V3를 상속하는 V4를 추가했다. Workspace branch `main`, 기준 commit `4e860134b6def3ec569892e1ce353142b82d1608`, 문서 submodule 기준 commit `501a0936124c98921201c89ba1cd69cf706e6ce7`다. 이번 V4 작업 시작 시 두 저장소의 작업트리는 깨끗했다. 기존 문서와 V1 Arm 속도 1.5 rad/s는 보존하고 V4에서만 override했다.

## 구현 계약

- Gym ID: `Isaac-Inspire-Sweep-Omni-v4`.
- Runtime: `InspireSweepEnv(ManagerBasedRLEnv)`.
- 환경 설정: `InspireSweepOmniV4EnvCfg` → `InspireSweepOmniV3EnvCfg` → `InspireSweepOmniV2EnvCfg` → `InspireSweepOmniV1EnvCfg` → `InspireSweepOmniEnvCfg` → `InspireSweepEnvCfg`.
- 보상 설정: `OmniV4RewardsCfg(OmniV2RewardsCfg)`에 새 속도 비용을 추가하고, V3의 `__post_init__`에서 높이 조건부 reaching 변경을 적용한다.
- PPO: `InspireSweepPPORunnerCfg`. Actor/Critic 41D, action 8D, 제어 주기 0.02 s, episode 10 s를 상속한다.
- `hand_velocity`(실제 Arm) threshold 3.0 rad/s, `push_fast` 0.5 m/s. 각각 엄격한 초과 비교다.
- `object_outside_shelf=None`, `success=None`. 낙하·전도·선반 충돌·선반 이동·timeout은 유지한다.
- `pushing_speed_cost`: 대상 물체의 3D 선속도에서 0.3 m/s 초과분을 0.2 m/s로 나눈 제곱. Weight −0.05이므로 0.5 m/s에서 가중치 적용 값은 −0.05다. 상한 clamp는 없다.
- **−0.05는 RewardManager 시간 곱셈 전 값**으로 해석했다. Dense 비용의 기존 규칙을 유지해 실제 0.02 s step 기여는 −0.001이다. 속도별 표와 train/play 명령은 상단 활성 환경 절에 있다.
- Arm/Hand raw action 변화량·실제 관절속도 제곱합의 네 항과 계수는 모두 보존했다. 이벤트·스폰·물성·관측·actuator도 상속한다.

## 변경 파일

활성 패키지의 `omni_env_cfg.py`, `__init__.py`, `mdp/goal_rewards.py`, `tests/test_omni_configuration.py`, `tests/test_goal_rewards.py`, `README.md`를 수정했다. 활성 환경 표·상속도·실행 명령과 이 로그를 갱신했다.

## 실행한 검사

Workspace 루트:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py \
  src/inspire_sweep_baseline/tests/test_dex_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_events.py
```

결과: **94 passed in 3.17s**. 실제 configclass 상속, 전체 V3 계약 보존과 설정 격리, Gym 등록·runner 연결, 공통 네 비용, 속도 0.3 dead zone·3D norm·제곱 증가·0.5 보정값·시간 곱셈, 0.5/0.501 종료 경계를 확인했다. 기존 progress·목표 reset·실패 조건 회귀 검사도 통과했다.

문서 submodule 루트에서 실행:

```bash
python 00_guidelines/scripts/check_document_links.py --check-external
python 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-15_omni_v4_speed_penalty.md \
  ../../src/inspire_sweep_baseline/README.md
git diff --check
```

전체 링크 검사에서는 기존 `2026-10-15_dex_omni_rewards.md`가 workspace 루트의 미확보 DexTouch PDF를 참조하는 오류 1건을 확인했다. 이번 변경과 무관한 원본 PDF 참조는 수정하지 않았다. 변경한 파일에 한정해 다음 명령으로 다시 검사했다.

```bash
python 00_guidelines/scripts/check_document_links.py --check-external \
  02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-15_omni_v4_speed_penalty.md \
  ../../src/inspire_sweep_baseline/README.md
```

결과: 변경 Markdown 4개 수식 검사 통과, 해당 파일 링크 검사 errors=0. Workspace와 문서 submodule의 `git diff --check` 모두 통과했다.

## 미실행 범위

Isaac Sim의 실제 환경 생성·접촉·GPU 동작, train/play, checkpoint 평가, 실물 실험은 실행하지 않았다. CPU 검증은 비용·등록·상속 계약을 확인하며 학습 성공이나 속도 억제 성능을 입증하지 않는다.
