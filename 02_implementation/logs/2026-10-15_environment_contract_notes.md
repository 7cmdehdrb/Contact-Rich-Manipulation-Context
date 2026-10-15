# Sweep Omni v3·Dex Omni v0 환경 문서 작성

[로그 안내](README.md) · [구현 문서 안내](../README.md)

기록일: 2026-10-15. 사용자 요청에 따라 각 환경의 관측·리워드·터미네이션·이벤트를 독립적인 새 문서로 정리했다. 코드·환경 계약·연구 결정은 변경하지 않았다.

## 기준과 산출물

- Workspace 기준 commit: `21bbae5f0fcaeaf3eb4014dd92f026b6cae9158c`.
- 문서 submodule 기준 commit: `f4b65dc6a1bb33b1f727eb43b077c5ea76cc3a5e`.
- 시작 시 workspace에 `.aws` 삭제와 `omni_env_cfg.py` 수정이 있었다. 해당 변경은 보존했다. 문서 submodule 내부 작업트리는 깨끗했다.
- `omni_env_cfg.py`의 기존 변경은 공백 정리와 Arm 속도 종료 기준 5.0 → **1.5 rad/s**다. 문서에는 HEAD 단독 값 대신 확인 당시 작업트리 값을 사용했다.

| 대상 | 산출물 | 설정 확인 경로 |
| --- | --- | --- |
| `Isaac-Inspire-Sweep-Omni-v3` | [독립 환경 구성 문서](../environments/SWEEP_OMNI_V3_ENVIRONMENT.md) | `InspireSweepOmniV3EnvCfg` → `InspireSweepOmniV2EnvCfg` → `InspireSweepOmniV1EnvCfg` → `InspireSweepOmniEnvCfg` → `InspireSweepEnvCfg` |
| `Isaac-Inspire-Dex-Omni-v0` | [독립 환경 구성 문서](../environments/DEX_OMNI_V0_ENVIRONMENT.md) | `InspireDexOmniEnvCfg` → `InspireSweepOmniV2EnvCfg` → `InspireSweepOmniV1EnvCfg` → `InspireSweepOmniEnvCfg` → `InspireSweepEnvCfg` |

두 환경의 runtime은 `InspireSweepEnv`, runner는 `InspireSweepPPORunnerCfg`다. 각 본문은 다른 환경 문서를 읽지 않아도 관측 순서·차원·좌표계, 최종 활성 보상과 계산식, 종료 기준, 이벤트 mode·reset 순서·분포를 확인할 수 있게 작성했다. 구현 문서 색인과 로그 색인에 등록했다.

## 실제 실행한 CPU 검증

Workspace 루트에서 다음 명령을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_dex_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py \
  src/inspire_sweep_baseline/tests/test_goal_events.py \
  src/inspire_sweep_baseline/tests/test_observations_and_sensors.py \
  src/inspire_sweep_baseline/tests/test_realistic_physics.py
```

결과: **103 passed in 3.17s**. Config 상속과 isolation, 보상 계산·기록 갱신, 종료 경계, 목표 배치, 관측·센서 수학, 질량·마찰 샘플링을 CPU에서 확인했다. 테스트는 기존 검사를 실행했으며 새 테스트나 구현 변경은 추가하지 않았다.

## 문서 검증

문서 submodule 루트에서 실행하는 명령은 다음과 같다.

```bash
python 00_guidelines/scripts/check_document_links.py
python 00_guidelines/scripts/check_document_links.py --check-external
python 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/environments/SWEEP_OMNI_V3_ENVIRONMENT.md \
  02_implementation/environments/DEX_OMNI_V0_ENVIRONMENT.md \
  02_implementation/README.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-15_environment_contract_notes.md
git diff --check
```

결과: 내부 링크 검사와 `--check-external` 검사 모두 **errors=0**(Markdown 225개). 변경한 Markdown **5개 수식 검사 통과**, 문서 submodule의 `git diff --check` 통과. Workspace 밖 링크 검사는 통합 checkout의 파일 존재를 확인한 것이며 HTTP URL을 검증한 결과는 아니다.

## 미검증 범위

Isaac Sim 실행, GPU 접촉·센서 출력 확인, 새 학습·재생, 성공률·실물 검증은 수행하지 않았다. HTTP 링크 렌더링이나 checkpoint 저장 설정도 확인하지 않았다. 코드 정독과 CPU 검사 통과를 정책 성능으로 해석하지 않는다.

## 후속 보완 — reaching 수식 해설

사용자 요청으로 두 환경 문서 각각에 reaching 기호 설명, 거리·최단 기록·보상 계산 순서, 최종 step 보상식과 단계별 수치 예시를 추가했다. Sweep Omni v3에는 초기 거리 정규화와 높이 조건 밖에서 소진되는 기록을, Dex Omni v0에는 3D 거리 개선량(m)과 초기 거리에 따른 보상 총량을 설명했다. Dex 문서의 해당 소제목도 `reaching`으로 정리했다.

문서 submodule 루트에서 실제 실행한 추가 검사:

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/environments/SWEEP_OMNI_V3_ENVIRONMENT.md \
  02_implementation/environments/DEX_OMNI_V0_ENVIRONMENT.md
python 00_guidelines/scripts/check_document_links.py --check-external
git diff --check
```

결과: 두 문서 수식 검사 통과, 링크 검사 errors=0, diff 공백 검사 통과. 수치 예시는 설명용 산술이며 simulation 실험 결과가 아니다. 코드 변경이 없어 CPU 테스트·시뮬레이터 실행은 재수행하지 않았다.
