# Contact Sweep Clutter v2 — F/T 하중 보정과 변화 비용

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [v1 계약](2026-10-20_contact_sweep_clutter_v1.md)

## 요청과 기준

사용자는 `inspire_contact_sweep_clutter_v1`을 계승하여 보정된 6축 F/T로 기존 관측을 대체하고, 급격한 힘·모멘트 변화의 제곱 비용과 최대 5% 비용 한도를 추가하도록 요청했다. 부드러운 밀기를 방해하지 않는 작은 비용을 요구했다.

작업 시작 workspace commit은 `753e787ce8ded9833282e3290dc63b4ed5956f24`다. 시작 시 상위 저장소에 문서 submodule 참조 변경이 있었고, 문서 저장소 내부 작업트리는 깨끗했다. 기존 변경을 보존하며 commit·push는 수행하지 않는다.

## 등록과 보존 범위

| 항목 | v2 |
| --- | --- |
| Gym ID | `Isaac-Inspire-Contact-Sweep-Clutter-v2` |
| Runtime | `contact_sweep_clutter_v2.env:ContactSweepClutterV2Env` → `ContactSweepClutterV1Env` |
| Cfg | `contact_sweep_clutter_v2.env_cfg:ContactSweepClutterV2EnvCfg` → `ContactSweepClutterV1EnvCfg` |
| PPO | `contact_sweep_clutter_v2.ppo_cfg:ContactSweepClutterV2PPORunnerCfg` → v1 runner |
| 학습 로그 | `logs/rsl_rl/inspire_contact_sweep_clutter_v2` |
| Actor/Critic | `policy57 + obstacles40` / `policy57 + privileged3 + obstacles40` |
| Action | Arm Joint Position 6D + Hand 2D |
| 주기·종료 | physics 0.01초, 제어 0.02초, 최대 10초, v1 실패 종료 상속 |

위 관측 구성·Action·주기는 v1을 유지한다. 변경 항목은 `policy` 끝의 F/T 관측 6D와 새 보상 항 `wrench_change`다. Actor는 타겟의 시작 위치를, Critic은 여기에 현재 위치를 추가하여 사용한다. Arm/Hand 네 운동 페널티의 함수·계수는 유지한다.

## F/T의 의미와 보정

`axia80_feasibility`는 tool-only 측정의 평균을 6축 모두에서 차감한다. v2는 이러한 도구 자체 하중 제거를 위치·자세·손가락 구성이 변하는 Hand에 적용한다. 고정 tare만으로는 자세 변화 이후의 중력 하중과 동작 중 관성 하중을 제거할 수 없으므로, 각 physics step의 강체 상태와 물성을 이용해 Hand 자체를 지지하는 데 필요한 wrench를 계산한다.

보정 대상은 measurement joint 하류의 Hand 13개 링크와 고정 tactile pad 17개, 총 30개 강체다. Axia 하우징과 상류 Arm은 포함하지 않는다. 실제 PhysX 질량·질량중심 관성, 현재 질량중심 위치·선형 가속도·각속도·각가속도를 사용한다. 물체 위치·목표·접촉 상대 ID는 사용하지 않는다. 현재 환경에서 Hand 질량·관성은 고정이므로 최초 조회값을 캐시한다. 이후 Hand 물성을 무작위화한다면 이 값도 다시 조회해야 한다.

EEF를 기준점으로 삼고 월드 축으로 표현한 Hand 자체 하중은 다음과 같다.

```math
\mathbf{F}_{\mathrm{self}}=\sum_i m_i(\mathbf{a}_i-\mathbf{g})
```

```math
\boldsymbol{\tau}_{\mathrm{self}}=
\sum_i\left[
\mathbf{I}_i^W\boldsymbol{\alpha}_i+
\boldsymbol{\omega}_i\times(\mathbf{I}_i^W\boldsymbol{\omega}_i)+
(\mathbf{p}_i-\mathbf{p}_{\mathrm{EEF}})\times m_i(\mathbf{a}_i-\mathbf{g})
\right]
```

```math
\mathbf{W}_{\mathrm{pure}}=\mathbf{W}_{\mathrm{raw}}-\mathbf{W}_{\mathrm{self}}
```

PhysX Tensor API의 incoming joint force는 child joint frame을 기준으로 반환된다. 생성된 measurement joint의 child frame은 `inspire_base_link`와 일치하므로, 해당 자세·원점에서 EEF로 축을 회전하고 모멘트 기준점을 이동한다. Axia 하우징 중심을 원점으로 근사하지 않는다. 관성 텐서는 PhysX의 link 축 표현에서 월드 축 표현으로 회전한다.

Actor/Critic의 `policy.wrist_wrench`는 **EEF 원점·EEF 축의 `[Fx,Fy,Fz,Mx,My,Mz]`이며 단위는 N/N·m**다. 기존 parent-to-child 지지 반력의 부호를 유지하므로, Hand에 가해진 외력과는 반대 부호다. 여기서 보정 후의 `pure`는 모델로 추정한 외부 하중에 대한 반력을 뜻하며, 수치 적분·solver 오차까지 완전히 제거한다는 의미는 아니다. 정확한 Hand 물성·운동 상태를 사용하는 simulator 측 보정이며, 실기에서 같은 정확도를 얻을 수 있는지는 검증하지 않았다.

고정 tare를 수집하지 않으므로 reset 시 접촉 중이더라도 그 접촉력을 기준값에 포함해 제거하지 않는다. reset 직후 아직 갱신되지 않은 관측만 0으로 마스킹하고, 부분 reset에서는 해당 환경의 행만 무효화한다. 관측과 보상은 같은 시점의 보정값을 공유한다.

## 힘·모멘트 변화 페널티

힘과 모멘트는 단위가 다르므로 각각의 허용 범위와 스케일로 계산한다. 변화량은 **제어 step 사이의 차이**이며, 시간으로 나눈 미분값이 아니다. 모멘트 기준점은 EEF로 유지하되 두 시점 모두 월드 축으로 표현해 비교한다. 따라서 EEF 축의 회전만으로 생기는 성분 변화를 충격으로 계산하지 않는다. EEF 기준점이 이동하면서 발생하는 모멘트 변화는 포함된다.

```math
u_F=\frac{\max(\|\mathbf{F}_t^W-\mathbf{F}_{t-1}^W\|-0.5,\ 0)}{5.0},
\qquad
u_\tau=\frac{\max(\|\boldsymbol{\tau}_t^W-\boldsymbol{\tau}_{t-1}^W\|-0.01,\ 0)}{0.1}
```

```math
c_t=\min\left(\frac{u_F^2+u_\tau^2}{2},\ 1\right)
```

| 설정 | 값·의미 |
| --- | --- |
| 힘 변화의 무비용 범위 | 제어 step당 0.5 N 이하 |
| 모멘트 변화의 무비용 범위 | 제어 step당 0.01 N·m 이하 |
| 스케일 | 힘 5 N, 모멘트 0.1 N·m |
| 가중치 | −0.1 |
| 절대 상한 | 초당 −0.1, 0.02초 step당 −0.002, 10초당 −1 |
| 추가 상대 상한 | 실제 누적 양의 보상 합의 5% |

일정한 힘으로 계속 미는 동작에는 변화 페널티가 없다. 힘 변화가 1 N이고 모멘트 변화가 0이면 raw cost는 0.005, 한 step의 비용은 최대 0.00001이다. 이 허용 범위는 초기 실험 설정이며, 학습된 정책의 밀기 동작에 맞춰 최적화한 값은 아니다.

비중 계산의 분모인 전체 보상은 v1 계수 산정과 동일하게 **양의 보상 합**으로 정의한다. 기존 음의 비용까지 차감한 net return은 0이나 음수가 될 수 있으므로 고정 비율의 분모로 사용하지 않는다.

현재 시점까지 누적한 양의 보상을 `P_t`, 직전까지 이 항으로 부과한 누적 비용을 `C_(t-1)`라 하면 실제 비용은 다음과 같이 제한된다.

```math
d_t=\min\left(0.1\,\Delta t\,c_t,\ \max(0.05P_t-C_{t-1},\ 0)\right),
\qquad r_t=-d_t
```

이 제한으로 episode의 모든 시점에서 `C_t <= 0.05 P_t`를 만족한다. 아직 양의 보상을 얻지 못했다면 이 항의 비용도 0이다. 사용하지 않은 비용 한도는 같은 episode 안에서 남지만, 한도 부족으로 부과하지 못한 과거 충격 비용을 나중에 추가 부과하지는 않는다. 조기 종료에도 같은 제약을 유지하며, reset 시 해당 환경의 이력과 비용 한도를 초기화한다.

구현은 RewardManager가 이미 계산한 양의 보상 누적값을 읽으며, 내부 상태를 가진 progress term을 다시 평가하지 않는다. 이 항은 모든 양의 보상 항 뒤에 배치하고, 순서가 잘못되면 오류를 발생시킨다. 첫 유효 F/T 표본은 이력 초기화에만 사용해 초기값 0과의 차이를 충격으로 계산하지 않는다.

v1 계수 산정의 참고 양의 보상 22.117462에 대한 절대 상한 1.0의 비율은 약 4.52%다. 참고값과의 비교에 더해 위의 실제 누적 양의 보상 기반 한도로도 5%를 제한한다.

## 실행

Workspace 루트에서 실행한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-v2 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-v2 --num_envs 1 \
  --checkpoint "<clutter-v2-checkpoint.pt>" --real-time
```

입력 차원은 v1과 같지만 F/T의 의미가 달라지므로 v2로 새로 학습하는 것을 기본으로 한다. v1 checkpoint의 이어 학습·재생 품질은 이번 작업에서 확인하지 않았다.

## 검증

다음 CPU 명령을 실행해 관측 공유·reset 이력과 보상 비용 한도에 대한 **18개 테스트 통과**를 확인했다.

```bash
env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_clutter_v2_observations.py \
  src/inspire_sweep_baseline/tests/test_clutter_v2_rewards.py
```

실제 RewardManager의 `compute`·`reset`을 사용하는 CPU 검증으로 실제 양의 보상에 따른 누적 5% 한도, 절대 비용 상한, 무비용 범위·제곱식, 초기 관측 조회, 관측·보상의 동일 표본 공유, 전체·부분 reset을 확인했다. 이 결과는 물리적 보정 정확도의 검증과 구분한다.

전체 패키지 CPU 검증은 **345개 통과**, 기존 ONNX deprecation 경고 2개였다. [CPU stdout](../../03_assets/artifacts/contact_sweep_clutter_v2_2026-10-20/pytest.log). 추가된 25개 검사는 보정 수학 7개, 보상 14개, 관측 4개다. 초기 작성 중 RewardManager 테스트용 import fixture와 등록 runtime 목록의 누락을 수정한 뒤 전체 검사를 통과했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests \
  > outputs/contact_sweep_clutter_v2_2026-10-20/pytest.log 2>&1

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/bin/conda run --no-capture-output -n env_isaaclab \
  python -u src/inspire_sweep_baseline/tests/_clutter_v2_wrench_probe.py \
  --headless --num_envs 4 \
  --output outputs/contact_sweep_clutter_v2_2026-10-20/wrench_probe.json \
  > outputs/contact_sweep_clutter_v2_2026-10-20/wrench_probe.log 2>&1

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  /home/min/miniconda3/bin/conda run --no-capture-output -n env_isaaclab \
  python -u src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-v2 --num_envs 8 \
  --max_iterations 2 --run_name smoke_clutter_v2 --headless \
  > outputs/contact_sweep_clutter_v2_2026-10-20/train_smoke.log 2>&1
```

실제 PhysX 검사는 seed 42, 4환경에서 수행했다. 무접촉 검증을 위해 선반·물체를 옮겨 격리하고, 실제 팔·손가락 운동과 알려진 외력·모멘트를 이용했다. 센서 tensor에 가짜 값을 직접 주입하지 않았다. [검사 JSON](../../03_assets/artifacts/contact_sweep_clutter_v2_2026-10-20/wrench_probe.json), [stdout](../../03_assets/artifacts/contact_sweep_clutter_v2_2026-10-20/wrench_probe.log).

| 물리 검사 | 최대 힘 잔차·오차 | 최대 모멘트 잔차·오차 |
| --- | --- | --- |
| 정적 무접촉 보정, 제어 40 step | 0.00000621 N | 0.00000104 N·m |
| 팔·손가락 동작 중 보정, 제어 160 step | 0.00000538 N | 0.001207 N·m |
| 알려진 외력·모멘트 주입, 안정 후 40 step | 0.00000502 N | 0.000103 N·m |

정적 raw 힘은 최대 8.6165 N이었다. 운동 검사에서는 관절 위치 변화가 최대 0.6626 rad였으며, 힘·모멘트 보정은 초기 정적 tare에 의존하지 않았다. 외력 검사는 축별 5 N 및 여러 축의 0.1–0.2 N·m급 모멘트를 PhysX에 적용하여 반력 부호와 EEF 기준점 변환까지 확인했다.

v1의 모든 기존 reward·Action·event·종료·command·scene 설정 보존, F/T만 교체한 관측 구성, 실제 `env.step`의 공유 샘플·초기 차분 제외·부분/자동 reset, 비용 상한과 누적 양의 보상 예산도 통과했다. 정상 작은 동작 4 step에서 신규 비용은 0이었으며, 양의 비용과 포화·예산 경계는 CPU 및 아래 PPO 로그로 확인했다.

최초 외력 fixture는 IsaacLab `set_external_force_and_torque`에 `positions`를 함께 전달했다. 해당 버전의 WrenchComposer가 이 경우 지정 토크를 덮어써 기대 모멘트와 맞지 않았다. 프레임워크는 수정하지 않고, 매 physics step에 PhysX Tensor API로 글로벌 힘·모멘트와 COM 작용점을 직접 주입하도록 검증 코드를 수정했다. 허용 오차를 넓히지 않았으며 수정 후 검사를 통과했다. 최초 실패 JSON·stdout은 workspace `outputs/contact_sweep_clutter_v2_2026-10-20/wrench_probe_initial_fixture.*`에 보존했다.

Kit의 빠른 종료가 실패 exit code를 0으로 가리는 문제도 확인했다. `fast_shutdown=False`로 시험한 실행은 모든 검사와 JSON `passed` 기록 후 종료 처리 중 segmentation fault(exit 139)가 발생했다. 해당 기록은 `wrench_probe_graceful_shutdown.*`로 보존했다. 최종 검증 스크립트는 성공 시 기본 fast shutdown을 사용하고, 실패 시 JSON·traceback 저장 및 flush 후 명시적으로 exit 1로 종료한다. 이 최종 스크립트도 위 명령으로 재실행하여 **14개 검사·JSON passed·exit 0**을 확인했다. 환경과 학습 실행기의 종료 방식은 변경하지 않았다.

PPO run은 `logs/rsl_rl/inspire_contact_sweep_clutter_v2/2026-10-20_21-08-32_smoke_clutter_v2`다. 8환경 ×36 step ×2 iteration = **576 transitions**를 실행했고, `model_0.pt`·`model_1.pt` 각각 모델·optimizer의 tensor 100개가 모두 유한했다. [PPO stdout](../../03_assets/artifacts/contact_sweep_clutter_v2_2026-10-20/train_smoke.log).

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/analyze_clutter_rewards.py \
  --log-dir logs/rsl_rl/inspire_contact_sweep_clutter_v2/2026-10-20_21-08-32_smoke_clutter_v2 \
  --output outputs/contact_sweep_clutter_v2_2026-10-20/smoke_reward_analysis.json
```

[보상 분석 JSON](../../03_assets/artifacts/contact_sweep_clutter_v2_2026-10-20/smoke_reward_analysis.json)에서 2개 iteration의 기록 평균은 양의 합 0.0661540, `wrench_change` −0.000808787로 약 1.22%였다. 이는 최대 episode 시간으로 나누어 기록된 값의 iteration 평균이며, 두 iteration만으로 학습 성능이나 최종 보상 비율을 판단하지 않는다. 기존 Arm 속도 비용은 변경하지 않았다.

장기 학습, 밀기 성공률, 충돌 회피로의 편향, 실물 모델 오차·센서 잡음·미지 payload에 대한 보정 성능은 짧은 CPU/PhysX/PPO 검사로 입증하지 않는다.

문서 저장소에서 아래 두 명령을 실행했다. 변경 Markdown 7개의 수식 검사와 링크 검사(내부 231개·workspace 외부 53개, 오류 0), 양쪽 저장소의 `git diff --check`가 통과했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  01_plan/00_HANDOFF_BRIEF.md 01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md \
  01_plan/04_NEXT_ACTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-20_contact_sweep_clutter_v2.md \
  ../../src/inspire_sweep_baseline/README.md

python 00_guidelines/scripts/check_document_links.py --check-external \
  01_plan/00_HANDOFF_BRIEF.md 01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md \
  01_plan/04_NEXT_ACTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-20_contact_sweep_clutter_v2.md \
  ../../src/inspire_sweep_baseline/README.md
```
