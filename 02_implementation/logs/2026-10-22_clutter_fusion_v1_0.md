# Fusion v1.0 — 손 전체 접촉·EEF wrench 변화량·물체 가속도

[개발 로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [패키지 실행 안내](../../../../src/inspire_sweep_baseline/README.md)

기준일: 2026-10-22. 사용자 요청으로 Fusion v3을 직접 상속한 `contact_sweep_clutter_fusion_v1_0`을 추가했다. 이후 v1_1은 이 Env Cfg를 상속할 수 있다. 구현·검증과 장시간 학습 성과는 구분한다.

같은 날 후속 요청으로 [장애물 개수·Goal 접촉 감쇠·자동 학습 복구](2026-10-22_clutter_fusion_v1_0_population_recovery.md)를 추가했다. 아래는 최초 구현·검증 기록이며 현재 물체 수, runtime 클래스, 접촉 rate 및 curriculum 수는 후속 문서를 따른다.

## 기준과 파일

Workspace `main`의 기준 HEAD는 `a2fcb0b77a234a14db8b6fc9c91cfef4c4229092`, 문서 submodule은 `f5655d0f9897708635edbe62b086994cfe5ac46d`, Isaac Lab은 `929f0fe1e9c1699efebf31b2ad0ab723a7d6e7e9`다. 작업 시작 시 PLAN.md, 패키지 README, telemetry 코드·테스트, 문서의 telemetry·reward balance·로그 정리 기록에 사용자 변경이 있었다. 해당 변경과 기존 학습 로그는 보존했다. 커밋·원격 반영은 수행하지 않았다.

| 항목 | 적용 내용 |
| --- | --- |
| Gym ID | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0` |
| Env Cfg | `ContactSweepClutterFusionV1_0EnvCfg` → `ContactSweepClutterFusionV3EnvCfg` |
| 실행 클래스 | 기존 `contact_sweep_clutter_fusion.env:ContactSweepClutterFusionEnv` |
| PPO Cfg | `ContactSweepClutterFusionV1_0PPORunnerCfg` → v3 PPO Cfg |
| Runner | 기존 `CurriculumOnPolicyRunner`, iteration 저장·복원 유지 |
| Experiment | `inspire_contact_sweep_clutter_fusion_v1_0` |
| 새 독립 Manager CFG | `ContactSweepClutterFusionV1_0RewardsCfg`, `TerminationsCfg`, `CurriculumCfg`: 다른 task CFG를 상속하지 않음 |
| Scene | Fusion SceneCfg를 상속하고 손 전체·물체별 필터 ContactSensor 추가 |
| 소스 | [`contact_sweep_clutter_fusion_v1_0/`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_0) |

관측은 policy55D + 초기 obstacles40D, critic 전용 현재 타겟3D, obstacle encoder16D를 유지한다. 기존 17D tactile 관측과 보정 F/T 관측 함수·노이즈는 변경하지 않는다. 새 접촉 ID와 물체 가속도는 보상 계산에만 사용하며 Actor 입력을 늘리지 않는다. Arm6 + Hand2 Action, Joint Position 제어, 50 Hz 제어·100 Hz 물리, 10초 timeout, 물성·초기 배치도 유지한다. 초기 목표 제외각만 reset 전부터 30°로 지정한다.

## 보상 계약

Net Force는 3D 힘 벡터의 Euclidean norm, Net Moment는 3D 모멘트 벡터의 Euclidean norm이다. 여러 접촉 바디의 경우 먼저 월드 XYZ 벡터를 합산하고 norm을 취한다. 따라서 반대 방향 힘은 상쇄되며 바디별 힘 크기의 합과 다르다.

### 손 전체 접촉과 계수

손의 13개 링크 + 17개 tactile pad = 30개 충돌 바디를 `whole_hand_contact`로 읽는다. 손 전체 resultant normal contact force가 **0.01 N 이상**이면 raw reward 1, 그 외 0이다. 기존 Tactile ON과 같이 매 제어 step 일정한 rate를 지급하며, 연속 시간에 따른 ramp나 5초 후 일회성 지급은 추가하지 않는다. RewardManager의 `weight * step_dt` 누적으로 유지 시간이 반영된다. 타겟·장애물·선반·바닥의 접촉을 모두 감지한다.

기존 `contact_any`, `contact_count`, 두 tactile weight 커리큘럼은 새 CFG에 없다. tactile 관측은 기존 센서로 계속 계산한다.

사용자 지정 run `logs/rsl_rl/inspire_contact_sweep_clutter_fusion_v3/2026-10-21_21-55-18`의 TensorBoard `Episode_Reward/*`를 읽기 전용으로 조사했다. 기존 [후반 보상 분석](2026-10-22_fusion_v3_reward_balance.md)과 같은 iteration **6000~7389, 1390개 값**을 사용했다. 로그는 episode 누적값을 최대 episode 시간 10초로 나눈 값이므로 아래 수치는 평균에 10을 곱한 episode 단위다.

| 참조 항목 | 값 |
| --- | --- |
| 양의 보상 합 | +17.900359865 |
| 음의 보상 합 | −4.893792616 |
| 제거되는 기존 tactile 두 항 합 | +0.015728284 |
| tactile 제외 순보상 기준 B | 12.990838965 |
| 새 `hand_contact.weight` | **+0.29 /초** |
| 5초 전체 접촉 시 C | +1.45 |
| C / (B + C) | **10.04097%** |

여기서 ‘전체 보상’은 페널티를 포함한 signed 순보상으로 해석했다. 양의 보상만 분모로 삼으면 비중은 7.49950%다. 새 운동 비용·가속도 비용·접촉 행동이 실제 총보상을 바꾸므로 10%는 참조 run에 대한 초기 계수 보정이며, 새 정책에서 강제되는 비율이나 성능 측정값이 아니다.

재현 명령(Workspace 루트):

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python -B - <<'PY'
from statistics import mean
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
path = 'logs/rsl_rl/inspire_contact_sweep_clutter_fusion_v3/2026-10-21_21-55-18'
ea = EventAccumulator(path, size_guidance={'scalars': 0}).Reload()
values = {tag: mean(x.value for x in ea.Scalars(tag) if 6000 <= x.step <= 7389)
          for tag in ea.Tags()['scalars'] if tag.startswith('Episode_Reward/')}
base = 10 * sum(value for tag, value in values.items()
                if tag.rsplit('/', 1)[1] not in ('contact_any', 'contact_count'))
print(base, 1.45 / (base + 1.45) * 100)
PY
```

### 비타겟 장애물 힘

각 cylinder를 단일 reporting body로 하는 센서 4개를 만들고, 각각 손의 30개 바디를 명시적인 filter로 지정한다. 물체에 작용하는 반력의 부호를 뒤집어 손의 힘으로 표현하고, `target_id`에 해당하는 물체를 환경별로 제외한다. 나머지 장애물 3개의 힘 벡터를 합한 norm이 20 N을 초과하면 비용이 발생한다. 선반·바닥은 이 장애물 비용에 넣지 않으며 기존 선반 보상·종료는 유지한다.

초과량 x = max(NetForce − 20, 0)에 기존 `exponential_joint_speed_cost_limit`의 공통 함수 `0.5 * expm1(2*x)`를 적용하고 raw cost를 100으로 제한한다. weight는 **−1.0**이다. 사용자 미지정 가중치는 같은 지수 joint-speed 비용의 단위 계수를 초기값으로 채택했으며, 실제 접촉 억제 성과로 보정한 값은 아니다.

Isaac Lab `ContactSensor.net_forces_w`와 `force_matrix_w`는 **normal contact force**이고 접선 마찰력은 포함하지 않는다. 전체 6축 외력은 기존 보정 F/T 관측으로 별도 유지한다. 새 보상을 실물 손 전체 force sensor의 검증 결과로 해석하지 않는다.

### EEF wrench 변화량

보정 F/T 관측의 같은 callable과 EEF 기준점·EEF 축 표본을 사용한다. Force/Moment 각각 `abs(norm(current) - norm(previous))`를 계산하며 **dt로 나누지 않는다**. 단위는 N 및 N·m이고, 방향만 변하고 크기가 일정하면 이 비용은 0이다.

무료 구간은 처음 Force50 N, Moment5 N·m이고 커리큘럼으로 10 N·1 N·m까지 감소한다. 기존 normalized exponential 구조를 유지한다. 각 초과량을 `1.5 * 현재 무료 임계값`으로 나누고 force/moment severity의 최댓값을 [0,1]로 제한한 뒤 `expm1(3*severity)/expm1(3)`를 사용한다. 즉 saturation/free ratio는 기존과 같은 **2.5**이며 두 임계값에 따라 함께 변한다. 기존 weight−0.1, 최대 −0.1/초, episode에서 이미 얻은 양의 보상 대비 누적 5% 예산을 유지한다. 예산이 부족하면 실제 비용이 줄어든다.

첫 표본·reset 직후·유효한 이전 표본이 없을 때 차분 비용은 0이다. 부분 reset과 같은 물리 step 재호출은 다른 환경의 history를 다시 차분하지 않는다.

### 물체 가속도

타겟을 포함한 네 물체 각각에 대해 `norm(v_current - v_previous) / step_dt`를 월드 XYZ 선속도로 계산한다. 속력 크기의 차이와 달리 방향 변화도 반영한다. 무료 구간은 0.3 m/s²에서 0.05 m/s²까지 감소한다. 사용자 요청의 감소 단위 `N/m²`는 가속도 문맥에 맞춰 **0.01 m/s²**로 해석했다.

물체별 초과량에 같은 `0.5 * expm1(2*x)`를 적용하고 각 물체 raw cost를 100으로 제한한 뒤 합산한다. 총합에 별도 100 cap을 적용하지 않으며 네 물체 최대 raw cost는 400이다. weight는 **−1.0**으로 같은 joint-speed 비용의 단위 계수를 초기값으로 채택했다. 첫 표본·reset 경계는 제외하며 반복 호출은 동일 값을 사용한다. 학습 성과를 보고 선택한 계수는 아니다.

### 나머지 보상·종료

활성 보상은 17개다. Reaching30, Goal progress100, Goal hold0.9, object−30, shelf collision−0.5, pushing speed−5, arm speed excess−1, shelf failure 일회성−3, EEF speed−1을 유지한다. EEF orientation은 비활성 상태를 유지한다.

Workspace의 명시적 네 항 규칙에 따라 `goal_rewards.action_rate_l2`와 `joint_vel_l2`를 Arm/Hand로 분리한다. 각각 −0.03/−0.03/−0.03/−0.01, raw 변화량·실제 속도의 제곱합과 그룹별 출력 cap100을 사용한다. v3의 통합 action-rate weight 커리큘럼은 새 환경에서 제거하여 고정 계수를 지킨다. 부모 v3는 수정하지 않는다.

독립 TerminationsCfg는 v3의 여섯 종료 조건을 그대로 명시한다: 10초 timeout, 모든 물체 낙하·전도, 타겟 속도0.8 m/s, 선반 충돌/손목 clearance3 cm, Arm 관절 속도5 rad/s, 선반 변위5 cm. 성공 종료는 없다.

## 커리큘럼

0부터 시작하는 PPO Learning iteration을 사용한다. 보상 파라미터 일정은 시작 iteration에서 첫 감소하고, deadzone은 기존 hold 계산처럼 hold 뒤 첫 interval이 끝날 때 감소한다. 절대 iteration으로 재계산하므로 반복 reset이나 checkpoint rewind에서 중복 누적하지 않는다. Goal deadzone은 다음 reset 분포에만 반영된다.

| 항목 | 시작 | 첫 감소 iteration·값 | 간격·감소량 | 최종 iteration·값 |
| --- | --- | --- | --- | --- |
| Deadzone 반각 | 30° | 3500·25° (hold3000) | 500·5° | 6000·0° |
| Goal hold XY tolerance | 0.05 m | 1000·0.04 m | 500·0.01 m | 2500·0.01 m |
| Wrench force 변화량 | 50 N | 1000·49 N | 250·1 N | 10750·10 N |
| Wrench moment 변화량 | 5 N·m | 1000·4.9 N·m | 250·0.1 N·m | 10750·1 N·m |
| Object acceleration | 0.3 m/s² | 1000·0.29 m/s² | 250·0.01 m/s² | 7000·0.05 m/s² |
| Pushing free speed (v3 유지) | 0.1 m/s | 500·0.09 m/s | 200·0.01 m/s | 1700·0.03 m/s |
| Arm free speed (v3 유지) | 1.0 rad/s | 500·0.98 rad/s | 200·0.02 rad/s | 3300·0.7 rad/s |
| EEF free speed (v3 유지) | 1.5 m/s | 500·1.48 m/s | 200·0.02 m/s | 12300·0.3 m/s |

Goal progress의 tolerance는 기존 0.01 m를 유지하고 Goal hold만 변경한다. tactile weight 및 기존 wrench rate/saturation 일정은 없다.

## 실행

Workspace 루트에서 실행한다. 선반이 기본 Nucleus 주소에 없으면 로컬 USD 경로를 `INSPIRE_SWEEP_SHELF_USD_PATH`로 지정한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0 --num_envs 1 \
  --checkpoint "<v1_0-checkpoint.pt>"
```

## 실제 검증

CPU 회귀 테스트(Workspace 루트):

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests
```

**496 passed, 3 warnings, 13.80초.** 경고는 기존 ONNX deprecation이다. 새 v1.0 테스트 35개는 scalar norm 차분/EEF 표본, wrench dt 미적용·지수 상한·예산, 물체별 가속도와 방향 변화·dt·합산, 접촉 force20N 경계·타겟 제외·벡터 상쇄, 부분 reset·같은 step 재호출, 커리큘럼 경계·rewind, 고정 운동 페널티, CFG 상속·등록·부모 격리를 확인한다. 기존 부모 계열·모델 export·telemetry 회귀도 포함한다.

초기 전체 실행은 **495 passed, 1 failed**였다. 기존 `test_termination_debug.py`의 task별 runtime 허용 목록에 새 ID가 없어 실패했으며 새 ID를 등록한 뒤 위 결과를 얻었다. 개발 중 새 가속도 cap 검사의 float32 기대 오차 두 건은 공통 지수 함수의 반올림에 맞춰 assertion 허용오차를 수정했다. production 계산을 회피 수정하지 않았다.

실제 Isaac Sim/PhysX + PPO 검증:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  INSPIRE_SWEEP_SHELF_USD_PATH=/home/min/Desktop/Shelf_USD/Arena/Collected_speedrack_shape/speedrack_shape.usd \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_clutter_fusion_v1_0_probe.py \
  --headless --device cuda:0 --num_envs 4 \
  --output outputs/fusion_v1_0_validation/probe.json \
  > outputs/fusion_v1_0_validation/runtime.log 2>&1
```

RTX3090, seed42, 4환경에서 **passed, exit0**. Sandbox 내부 GPU 조회는 드라이버 접근 실패였고, 같은 GPU 조회 및 probe를 승인된 sandbox 밖 실행으로 검증했다. [Probe 코드](../../../../src/inspire_sweep_baseline/tests/_clutter_fusion_v1_0_probe.py), [결과 JSON](../../../../outputs/fusion_v1_0_validation/probe.json), [stdout](../../../../outputs/fusion_v1_0_validation/runtime.log)에 근거가 있다.

- 실제 관측55/40/3D, Action8D, 보상17개·커리큘럼8개·종료6개와 v3의 관측·Action 보존을 확인했다.
- 손 전체30 body와 물체별 접촉 행렬 `[4,1,30,3]`을 확인했다. 실제 장애물/palm 접촉에서 역방향 필터 force와 전체 손 force가 일치하고, 해당 물체를 target_id로 지정하면 장애물 force만 0이 된다.
- 접촉 fixture의 한 offset에서 4.521N 접촉은 tactile OFF인 상태로 감지되었고, 다른 offset에서는 기존 palm tactile도 ON이었다. 강제 겹침 fixture의 467N·5492N 등 큰 힘은 센서 경로를 확인하기 위한 stress 조건이며 실제 정책 궤적·물리 품질의 근거가 아니다.
- 14개 curriculum 경계·최종 clamp·rewind·진행 중 goal 불변, 12개 정상 제어 step의 finite 관측·보상, 부분/timeout reset의 차분 이력 분리를 확인했다.
- 실제 PPO iteration999/1000, 각 환경4 step, 1 epoch·1 minibatch 업데이트를 수행해 encoder 변화와 iteration1000 커리큘럼 경계를 확인했다. 검증 checkpoint는 `outputs/fusion_v1_0_validation/probe_model_1000.pt`, runner log_dir는 None이다. `logs/rsl_rl`은 쓰거나 이동·삭제하지 않았다.

장시간 학습·성공률 개선·2048환경 처리량·새 정책에서의 10% 접촉 보상 비중·실물 성능은 검증하지 않았다. 새로운 센서의 normal-force 범위와 강제 접촉 fixture의 검증 한계는 위 계약을 따른다.

문서 submodule에서 다음 명령을 실행했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py 01_plan/00_HANDOFF_BRIEF.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-22_clutter_fusion_v1_0.md ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external 01_plan/00_HANDOFF_BRIEF.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-22_clutter_fusion_v1_0.md ../../src/inspire_sweep_baseline/README.md
git diff --check
```

수식 검사 **6개 파일 통과**, 링크 검사 **오류0·내부213·외부 workspace73**, 문서 `git diff --check` 통과. Workspace에서는 `git diff --check -- src/inspire_sweep_baseline`을 실행해 통과했다. 전체 Workspace에는 기존 사용자 PLAN.md whitespace가 있어 수정 범위를 검사했으며, 기존 로그 색인의 충돌 표시도 이번 작업에서 임의 정리하지 않았다.
