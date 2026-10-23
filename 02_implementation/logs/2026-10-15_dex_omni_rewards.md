# DexTouch 기록 갱신 보상을 적용한 Dex Omni 환경

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [패키지 실행 안내](../../../../src/inspire_sweep_baseline/README.md)

기록일: 2026-10-15. 사용자가 제공한 DexTouch PDF의 **과거 최고 달성 상태를 갱신한 만큼만 지급하는 shaping**을 Sweep에 적용했다. 기존 Hand/Arm action·속도 비용, 선반 이동 종료, 물체 종류·스폰 위치를 유지하는 별도 환경이다. 학습 성능 검증은 수행하지 않았다.

## 기준 상태와 출처

- Workspace: `main`, `32076d7`. 작업 시작 시 활성 패키지의 추적 파일 변경은 없었고, 두 문서/참고 submodule 참조 변경과 `.aws` 미추적 항목이 있었다.
- 문서 submodule: `main`, `87b1a2dab7feb7947152b6cb6e7b1b73a051ae78`. 기존 수정·미추적 문서와 자산을 보존하고 필요한 안내·로그만 갱신했다.
- Isaac Lab: `929f0fe1e9c1699efebf31b2ad0ab723a7d6e7e9`. `example/Sweep-Policy`의 현재 commit `baa3740e38c1a693b2094dc4d141b72de0dd3142`와 내용은 변경하지 않았다.
- 원문: [Lee 등, DexTouch (2024), 제공된 PDF](<../../../../Lee 등 - 2024 - DexTouch Learning to Seek and Manipulate Objects With Tactile Dexterity.pdf>), PDF 4쪽/인쇄 페이지 10775, IV-B Reward Design, 식 (1)과 식 (2)의 목표 거리 항. 텍스트 추출과 해당 페이지 전체 렌더링으로 확인했다.

논문의 접근 항은 손끝별 `max(과거 최소 거리 - 현재 거리, 0)`의 합이고, 집기 이후 목표 거리 항도 같은 원리다. 회전 과업은 과거 최대 각도보다 늘어난 양을 사용한다. 집기 전 높이 보상·집기/회전 bonus 등은 별도 항이므로 논문의 모든 보상이 기록 갱신 방식이라고 해석하지 않는다. 논문에 계수의 구체적인 수치는 명시되지 않았다.

**기존 OmniV2도 이미 기록 갱신 방식**이다. V2는 초기 거리로 나눈 진척 비율을 사용하여 접근 최대 30, 목표 이동 최대 40을 지급한다. 이번 변형은 이를 **실제 거리[m] 개선량**으로 바꾸며 에피소드 초기 거리로 정규화하지 않는다. 논문의 집기·들기·문/밸브 회전 과업이나 L1 속도 페널티를 이식하지 않았다.

## 등록·상속·책임

| 항목 | 구현 계약 |
| --- | --- |
| Gym task | `Isaac-Inspire-Dex-Omni-v0` |
| Runtime | `InspireSweepEnv → ManagerBasedRLEnv` |
| Cfg | `InspireDexOmniEnvCfg → InspireSweepOmniV2EnvCfg → InspireSweepOmniV1EnvCfg → InspireSweepOmniEnvCfg → InspireSweepEnvCfg → ManagerBasedRLEnvCfg` |
| Reward Cfg | `DexOmniRewardsCfg → OmniV2RewardsCfg → OmniRewardsCfg` |
| Runner | `inspire_sweep_baseline.agents.rsl_rl_ppo_cfg:InspireSweepPPORunnerCfg`, Baseline과 동일 |
| 변경 코드 | [환경 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_omni_envs.py), [보상 term](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/dex_rewards.py), [등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py) |

새 Cfg는 두 shaping term만 교체한다. `DexReachProgress`는 기존 `ReachProgress`의 reset/FK 갱신을, `DexPlanarGoalProgress`는 `PlanarGoalProgress`의 reset 위치 snapshot을 상속한다. 실행 환경 클래스에 상태나 제어 분기를 추가하지 않았다.

## 보상과 유지된 조건

접근 거리는 현재 물체 바닥 원점과 wrist에 고정된 EEF 사이 3D 거리다. 논문의 손끝별 합 대신 기존 EEF 기준을 유지하므로 손가락 굽힘만으로 접근 보상을 얻지 않는다. 물체가 EEF 쪽으로 이동한 상대 접근은 보상될 수 있다. 목표 거리는 물체와 목표 사이 world XY 거리다.

```math
g^{\mathrm{reach}}_t = \max(\|p_{\mathrm{eef},t}-p_{\mathrm{obj},t}\|_2-0.10,0),
\qquad g^{\mathrm{goal}}_t = \max(\|p^{xy}_{\mathrm{obj},t}-p^{xy}_{\mathrm{goal}}\|_2-0.01,0).
```

각 거리의 초기 기록은 reset 상태의 거리이고, 그 이후 보상과 기록은 다음과 같다.

```math
r^k_t = \alpha_k\max(b^k_{t-1}-g^k_t,0),
\qquad b^k_t = \min(b^k_{t-1},g^k_t),
\qquad b^k_0 = g^k_0.
```

계수는 접근 `30 reward/m`, 목표 `300 reward/m`다. **이번 Sweep 비교를 위한 실험 시작값이며 논문에서 가져온 수치가 아니다.** 목표가 15 cm 떨어져 있으면 1 cm 허용 범위까지 개선한 14 cm에 대해 최대 42점이다. 목표 항을 주보상으로 유지하면서 V2의 목표 총량 40에 가까운 크기를 선택했다. 접근 총량은 초기 EEF 거리에서 10 cm를 뺀 값에 30을 곱하므로 고정된 에피소드 예산이 아니다. 같은 1 cm 기록 개선은 초기 거리와 무관하게 접근 0.3점/목표 3점을 지급한다.

이전 기록까지 후퇴·복귀하거나 제자리에 머무르면 0이고, 허용 범위 안에 들어간 뒤에는 해당 기록 보상이 소진된다. 두 보상은 동시에 평가하며 별도 접촉/집기 단계 gate는 추가하지 않는다. 함수가 반환할 때 `step_dt`로 나누어 RewardManager의 곱셈을 상쇄한다.

| 보존 항목 | OmniV2에서 그대로 상속한 값 |
| --- | --- |
| Arm action 비용 | `-0.03 × sum(Δaction_arm²)` |
| Hand action 비용 | `[0,1]`로 제한한 2D 명령의 `-0.03 × mean(Δaction_hand²)` |
| Arm 속도 비용 | 6개 Arm joint의 `-0.03 × sum(qdot²)` |
| Hand 속도 비용 | 12개 Hand joint의 `-0.01 × mean(qdot²)` |
| 기타 보상 | tilt `-2`, shelf collision `-0.5`. `time/success/failure=None` |
| 선반 종료 | 기존 `shelf_collision` 함수·임계값 0.1 및 `shelf_displacement`의 0.05 m 초과. 가상 finger/wrist 높이 검사 포함 |
| 나머지 종료 | V2 전체와 동일. 성공 종료 없음, Arm 속도 3 rad/s 초과, 물체 낙하/기울기·과속·선반 밖·10초 timeout 유지 |
| Scene·spawn | 기존 단일 실린더 반지름 0.04 m/높이 0.10 m, 선반 중앙 반경 0.02 m 원판·높이 1.05 m·random yaw, 전방향 최대 0.15 m 목표 및 가장자리 clipping, 질량·마찰 랜덤화 |
| 관측·행동 | Actor/Critic 41D, 현재 물체 GT 포함. Arm Joint Position 6D + Hand openness 2D. 50 Hz, 10초 에피소드, 기존 PPO |

원래 action 비용은 명령의 절대 크기 자체가 아니라 **연속 명령의 변화량** 비용이다. 사용자의 보존 조건을 따라 그 정의와 가중치를 변경하지 않았다. 이 환경은 현재 물체 GT를 쓰는 기준선이며 새 Blind 정책이나 촉각 구조를 구현한 것이 아니다.

## Reset 경계

Isaac Lab은 Scene/reset event 실행 후 RewardManager를 reset하고 그 뒤 CommandManager를 reset한다. 따라서 목표 term의 reset에서는 이전 에피소드 command를 읽지 않고 새 물체 위치만 저장한다. 첫 보상 호출에서 새 command와 reset 위치를 조합해 기준 거리를 얻어 첫 action의 진행량도 포함한다. 환경별 기록은 부분 reset 대상에만 초기화한다. 접근 reset에서는 robot body pose accessor로 FK를 갱신한 다음 EEF 위치를 읽는다.

## 실제 실행한 검증

작업 디렉터리는 workspace 루트다. 변경 전 다음 명령을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py
```

결과: **2 failed, 34 passed**. 기존 V2 테스트가 과거 `200/400`을 기대하여 현재 코드 `30/40`과 불일치했다. V2의 실행 설정을 바꾸지 않고 테스트 기대값을 `30/40`으로 맞췄다. 패키지 안내의 같은 오래된 수치와 활성 안내의 현재 Arm 속도 기준도 코드에 맞춰 정리했다.

구현 후 개별 `test_dex_rewards.py`: **15 passed**, `test_omni_configuration.py`: **15 passed**. 두 명령 모두 위 환경 변수와 Python 실행 파일을 사용하고 pytest 파일 인수만 해당 파일로 지정했다. 이어서 활성 패키지 전체를 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests
```

결과: **176 passed (7.58초)**. 기록 갱신/후퇴/재방문, 초기 거리가 달라도 같은 개선량에 같은 보상, XY 회전·높이 제외, 근접/목표 포화, 0.01/0.02/0.05초 제어 주기 독립성, 부분 reset과 첫 transition, FK 갱신, 설정 격리, 등록/callable 연결을 검사했다. Dex와 V2의 전체 config를 비교해 두 shaping 항 이외 Scene·Event·관측·행동·종료·페널티가 같음을 확인했다. 이 검사는 CPU 텐서·config 및 정적 자산 검사이며 GPU 접촉 동작을 입증하지 않는다.

문서 submodule 루트에서 이번 작업의 Markdown 4개를 대상으로 다음 검증을 실행했다.

```bash
python3 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-15_dex_omni_rewards.md \
  ../../src/inspire_sweep_baseline/README.md

python3 00_guidelines/scripts/check_document_links.py --check-external \
  02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-15_dex_omni_rewards.md \
  ../../src/inspire_sweep_baseline/README.md
```

수식 검사 **4 files passed**, 링크 검사 **errors 0**(internal 52/external 25)이었다. 패키지 README의 기존 Omni 상세·계획 링크도 현재 문서 위치로 정정했다. Workspace에서 `git diff --check`와 `git -C example/Contact-Rich-Manipulation-Context diff --check`를 실행하여 둘 다 통과했다.

## 실행과 미검증 범위

학습/재생 명령은 [패키지 안내](../../../../src/inspire_sweep_baseline/README.md)와 [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)에 기록했다. workspace 루트에서 `--task Isaac-Inspire-Dex-Omni-v0 --experiment_name inspire_dex_omni`를 사용하고 `--sweep-direction`은 생략한다. 필요하면 접근 가능한 선반 USD를 `INSPIRE_SWEEP_SHELF_USD_PATH`로 지정한다.

이번 작업에서는 Isaac Sim 환경 생성·GPU train/play·새 checkpoint·성공률/seed 비교·실물 실험을 실행하지 않았다. 구현과 CPU 회귀 검사 범위의 결과이며 가중치 수렴성·V2 대비 학습 우위는 미검증이다. 논문의 손끝 shaping을 그대로 복제하거나 연구의 센서 입력·과업 범위를 바꾸지 않았다. 다음 실험은 동일 Scene·PPO 조건에서 V2와 Dex의 접근/목표 보상 및 물체 최종 오차를 비교하는 것이다.
