# Dex Tactile Renewal v3: v1 상속과 경험적 보상 비율·질량 조정

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [패키지 안내](../../../../src/inspire_sweep_baseline/README.md)

## 요청과 기준 상태

2026-10-20 사용자 요청으로 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1`에서 직접 파생한 새 환경을 구성했다. Pushing speed free_speed 0.3→0.2 m/s, weight −1→−2, 물체 질량 약 1.5배, reaching을 유지하면서 관측된 reaching:goal_distance 기여 비율을 3:4에 맞추는 것이 요청 범위다. 사용자는 후속 대화에서 goal_distance=94 적용을 확인했다.

Workspace 기준 commit은 `2cca359d747edad0782a93119af1992842cb4979`, 문서 submodule HEAD는 `3773aa5dfe6a1d5f36edd0cdfcbfe7ed0d4b6f10`이다. 이전 PPO 감사 작업으로 변경된 문서 로그·artifacts와 미추적 UR Description 디렉터리를 보존했다. 커밋·원격 반영은 수행하지 않았다.

## 등록·상속·환경 계약

| 항목 | 적용값 |
| --- | --- |
| task ID | `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v3` |
| runtime | `InspireSweepEnv` → `ManagerBasedRLEnv` |
| 환경 Cfg | `InspireDexTactileSweepOmniRenewalV3EnvCfg` → `InspireDexTactileSweepOmniRenewalV1EnvCfg` 직접 상속 |
| runner | `InspireDexTactileSweepOmniRenewalV3PPORunnerCfg` → v1 runner |
| 실험 폴더 | `logs/rsl_rl/inspire_dex_tactile_sweep_omni_renewal_v3` |
| Actor/Critic | 기존 policy 57D, 현재 물체 GT·촉각 17 bit·wrench 포함 |
| 행동 | Arm Joint Position 6D + Hand openness 2D |
| 제어·종료 | 0.02 s 제어 주기, 10초 최대 에피소드, v1 실패·timeout 종료 |

v2는 success/goal_hold 추가 실험이므로 수정하지 않고, 새 v3를 v1에서 직접 분기했다. v3도 success 보상·종료와 goal_hold를 추가하지 않는다. 부모의 스폰·목표 분포, 마찰, 센서·관측·노이즈, action/controller, PPO hyperparameter를 상속한다. 필수 Arm/Hand action-rate 및 joint-velocity 네 함수·그룹·계수를 변경하지 않았다.

## 로그에 근거한 goal weight 산정

근거 run은 workspace의 `logs/2026-10-19_12-15-47`, 마지막 10 iteration **39027–39036**이다. 저장 env.yaml의 `goal_distance` 가중치는 **300.0**이다. 일반 Omni Renewal의 40.0을 Dex 보상 Cfg가 덮어쓴다.

| 항목 | TensorBoard 평균 | 누적 보상 환산(×10초) |
| --- | ---: | ---: |
| reaching | 0.7783182442188263 | 7.783182442188263 |
| goal_distance | 3.314544939994812 | 33.14544939994812 |

Reaching을 유지하며 기존 측정 궤적의 goal 기여를 reaching의 4/3으로 맞춘다.

```math
w_{\mathrm{goal,new}}=300\frac{4}{3}\frac{0.7783182442188263}{3.314544939994812}=93.92761399337607
```

이를 **94.0**으로 반올림했다. 기존 로그에 이 계수를 대입하면 reaching≈7.783, goal≈10.386으로 약 3:4다. 이론상 최대 보상은 계산 근거로 사용하지 않았다. 계수 변경과 동시에 질량·속도 비용도 바뀌므로 새로 학습한 정책의 실제 비율은 변할 수 있다. 같은 로그 집계 창으로 후속 검증이 필요하다.

## 질량과 속도 페널티

Pushing speed는 기존 bounded 지수 함수와 cap=100을 상속하고 free_speed=0.2, weight=−2.0으로 설정했다. 1 step에 RewardManager가 dt=0.02를 곱하므로 이 항의 하한은 −4다. 종료의 물체 과속 임계값 0.8 m/s는 부모 값을 유지한다.

기존 Gaussian 샘플 `clamp(0.365 + 0.0675 × N(0,1), 0.230, 0.500)`에 1.5를 곱한다. 분포 중심은 0.5475 kg, 표준편차 파라미터는 0.10125 kg, 범위는 0.345–0.750 kg다. 실제 표준편차는 clamp 때문에 이 파라미터보다 작다. 생성 mass_props도 0.5475 kg로 맞췄다.

새 `randomize_scaled_episode_physics(env, env_ids, mass_scale=1.0)`가 기존 버퍼 갱신 경로를 재사용한다. v3 reset에 mass_scale=1.5를 넘기고, 기존 `randomize_episode_physics(env, env_ids=None)`는 원래 인터페이스로 scale=1.0 경로를 호출한다. 샘플마다 새로 배율을 적용하므로 reset 반복으로 질량이 누적 증가하지 않는다. 관성은 캐시한 기본 질량·관성 대비 새 질량 비율로 갱신하고 마찰 샘플은 그대로 사용한다.

구현 소스:

- [환경 Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/dex_tactile_omni_renewal_v3_env_cfg.py)
- [물성 이벤트](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/realistic_physics.py)
- [Gym 등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py)
- [PPO Cfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agents/tactile_omni_renewal_ppo_cfg.py)

## 실행한 검증

Workspace 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_realistic_physics.py \
  src/inspire_sweep_baseline/tests/test_tactile_renewal_configuration.py \
  src/inspire_sweep_baseline/tests/test_omni_configuration.py
```

최종 **50 passed in 2.81s**. 실제 configclass로 v1→v3 전체 설정 차이·부모 격리·Gym/runner 연결·경험적 비율을 확인했다. 물성 테스트는 동일 random seed로 기본/1.5배 이벤트의 질량·관성을 비교하고 부분 reset, 비선택 행, 반복 reset 비누적, 마찰 불변, 잘못된 배율 거부를 확인한다. 기존 Omni 설정·운동 페널티 검사도 포함했다. 최초 추가 테스트에서는 부모에 없는 success 속성에 직접 접근해 실패했고, 미존재도 비활성으로 처리하도록 검사만 수정했다.

```bash
/home/ssu/miniconda3/bin/conda run --no-capture-output -n jd_isaaclab \
  python src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v3 \
  --num_envs 8 --max_iterations 1 --run_name smoke_v3 --headless
```

**GPU 8 env·PPO 1 iteration 완료, exit 0.** Actor 입력 57D·출력 8D, Critic 입력 57D·출력 1D를 확인했다. 성공 run은 `logs/rsl_rl/inspire_dex_tactile_sweep_omni_renewal_v3/2026-10-20_13-12-56_smoke_v3`, checkpoint는 `model_0.pt`, 캡처 stdout은 `/tmp/renewal_v3_smoke_retry.log`다. 저장 env.yaml에서 goal weight=94, pushing free_speed=0.2/weight=−2, spawn mass=0.5475, reset mass_scale=1.5와 새 callable을 확인했다.

첫 GPU 시도는 `env_ids=None`과 추가 optional mass_scale을 같은 event signature에 둬 EventManager의 인자 검사에서 거부됐다. `/tmp/renewal_v3_smoke.log`에 기록되어 있다. 기본 event 인터페이스를 보존하고 새 scaled event의 env_ids를 필수 인자로 분리한 뒤 위 최종 시도를 통과했다. Framework 자체는 수정하지 않았다. 기존 선반 mass authoring·frame marker·PhysX 설정 경고는 출력됐으나 학습 1 iteration은 완료했다.

## 실행 안내와 미검증 범위

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v3 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v3 \
  --num_envs 1 --checkpoint "<v3-checkpoint.pt>" --real-time
```

2048 env 장시간 학습, 새 정책의 보상 비율·성공률·PPO 안정성, GUI play와 실물 성능은 검증하지 않았다. smoke checkpoint는 실행 연결 검증용이며 성능을 입증하지 않는다.

문서 검증은 변경 Markdown 4개에 대한 `check_markdown_math.py`, workspace 및 문서 submodule의 `git diff --check`를 통과했다. 문서 submodule에서 `python 00_guidelines/scripts/check_document_links.py --check-external`을 실행한 결과 기존 문서의 미보유 TEMP 로그 3경로·DexTouch PDF 1경로가 보고됐다. 이번 추가·수정 링크의 오류는 없었다.
