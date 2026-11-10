# Simple Semi-Prof-v0 구현·검증

2026-11-11. 요청: 과거 Prof-v1의 목표 근처 왕복·상부 누름 관찰을 바탕으로, 교수님 제안의 접촉 중 접근·방향 정렬 의도를 유지하는 새 환경을 만든다. 기준 source HEAD는 `6cb6c30ef241b15527a6bded759e2636f250d89a`. 시작 시 사용자 변경 `docs/plan/PLAN15.md`가 있었으며 보존했다. 학습 로그는 수정하지 않았다.

## 확정된 의도와 후속 정정

사용자가 Finger-v1 부모, Last Action raw clip·속도 비용−0.06·종료2→1rad/s 일정·기존 timeout 성공 조건을 승인했다. 비접촉 또는 높이 불인정 중의 Distance 개선도 최고 기록에 반영하고 당시 보상은 소멸시키며, 재접촉 시 소급 지급하지 않기로 했다. 방향 보상은 정지 접촉에도 지급하며 속도·진행량 조건을 넣지 않는다. 가중치0.33은 승인된 비교 규모이고 실제 보상 비율을 고정하지 않는다.

후속 지시로 최초 방향 계획의 **초기 고정 방향·3cm 최초 진입 latch**를 폐기했다. 현재 물체→목표 방향으로 매 policy step 계산하고, XY 거리1cm 미만에서는 방향 점수1, 재이탈하면 즉시 정상 각도 계산으로 돌아간다. 추가 지시로 기준 벡터는 XY(Z=0), 실제 힘은 Z 포함3D로 비교한다.1cm 내부 각도 예외와 실제 접촉·수평 합력1N 이상 조건은 유지한다. 따라서 내부 예외에서는 수직 힘도 각도 감점이 없음을 문서·사용자 설명에 명시했다.

## 등록·상속과 전체 계약 대조

- Gym: `Inspire-Sweep-Simple-Semi-Prof-v0`.
- EnvCfg: `SweepSimpleSemiProfEnvCfg(SweepSimpleFingerV1EnvCfg)`.
- Runtime: `SweepSimpleSemiProfEnv(SweepSimpleFingerV1Env)`.
- PPO: `SweepSimpleSemiProfPPORunnerCfg(SweepSimpleFingerV1PPORunnerCfg)`, experiment `inspire_sweep_simple_semi_prof_v0`.

| 구분 | 부모 대비 최종 차이 또는 보존 |
| --- | --- |
| Scene·자산·물리·센서 | 부모 그대로. 기존 타겟/hand PhysX view에서 마찰을 추가로 읽음 |
| Command·Event·reset 배치 | 부모 그대로. 목표6–12cm·Fast 원형 RED/WHITE·Warp IK 유지 |
| Observation·Action | 부모 그대로. policy66+obstacles64, actor/critic 동일, action12, 손6 drive 위치·팔 OSC raw clip·bounded 분포·Last Action tanh 없음 |
| Reach | 부모 `InverseDistanceReach` weight30·near_radius0.1·distance_scale0.1·초기 예산 보존. Prof-v1과 같은 함수. 후퇴 없음 |
| Distance | `DexPlanarGoalProgress`100 → `ContactLogGoalProgress`120. Finger-v2 로그 면적 보정·epsilon0.01을 상속하고 접촉2-of-3/현재 EEF15cm 미만 마스크 추가 |
| 접촉 유지 | `GoalContactMaintenance`0.1 → `None`. 유지 count·목표3cm 우회 없음 |
| 멀어짐 | `RelativeInverseDistance` 함수 그대로, weight−25.94→−31.128 |
| 방향 | `force_direction`0.33 추가. 기존 Prof `direction_deviation`은 상속하지 않음 |
| 그 외 보상 | 부모 callable·순서·params·weight 보존. arm 속도−0.06, hand 속도−0.01, action rate·tilt·장애물·선반·wrench 비용 유지. Holding·가속도는 비활성 유지 |
| Termination·성공·메트릭 | 부모 그대로.10초 timeout, XY<3cm 성공 및 동시 실패 우선. 최근10,000개 완료 에피소드 통계 유지.1cm 방향 예외는 성공 반경이 아님 |
| Curriculum | 부모 전체 유지. arm 종료2rad/s를2000까지 유지,2250부터250마다1/12 감소,5000에서1. DeadZone 및 보상 일정 유지 |
| PPO | 모델·분포·optimizer·rollout 전체 보존, 실험명만 변경 |
| Runtime 추가 | physics substep 힘 수집/평균과 reset 시 선택 환경 버퍼 초기화만 추가 |

공식 configclass 기반 전체 EnvCfg 및 runner 대조로 위 차이 외의 차이가 없음을 확인했다. 변경 파일 안의 기존 top-level 클래스/함수38개는 HEAD와 AST 본문이 동일하다. 새 설정의 변경이 부모 설정에 전파되지 않는 것도 확인했다.

## 보상·수집 구현

Distance의 입력은 현재 타겟 root/link의 노이즈 없는 GT XY 거리다. 기존 `AreaMatchedLogGoalProgress`를 직접 상속하므로 면적 보정·현재 goal reset 시점·dt 상쇄 계약을 유지한다. 접촉은 타겟 hand 필터 법선력 크기 합≥0.01N인 policy sample을3개 저장해2개 이상일 때 인정한다. 현재 step 무접촉도 이전 두 sample이 접촉이면 인정될 수 있다. 높이는 현재 EEF가 초기 선반 표면+0.15m보다 엄격히 낮아야 한다. 보상 count를 별도로 누적하지 않는다. 같은 step 중복 호출은 접촉 이력을 중복 진행시키지 않고, reset은 선택 환경만 초기화한다.

방향 힘은 타겟 물체가 받는 부호의 법선+마찰 합력이다. 핸드 쪽 반력을 반환하는 기존 helper를 재사용하지 않는다. 기존 native view의 `get_contact_force_matrix(dt=physics_dt)` 및 `get_friction_data(dt=physics_dt)`를 사용한다. 설치된 PhysX107.3 Python API와 Isaac Lab contact sensor의 view·buffer shape를 직접 대조했다. 이 API 정적 확인은 실제 PhysX 실행 검증과 구분한다.

마찰은 native count/start가 가리키는 각 filter의 유효 anchor만 Warp kernel로 합산한다. CPU 회수·유효 contact 수의 host 동기화·전체 padding 스캔은 없다. 미사용 buffer의 NaN/큰 값은 읽지 않으며, 잘못된 범위나 사용 중 nonfinite anchor는 해당 pair를 무효화한다. Torch와 같은 CUDA stream을 사용하고, CPU는 동일 Warp kernel로 검증했다. 정상 물리 범위를 벗어나는 힘 또는 buffer overflow 상황의 GPU 동작은 검증하지 않았다.

runtime은 부모 `step()` 호출 동안 instance-local `scene.update`를 감싸 원래 update 직후 수집한다. 원래 manager/recorder/종료·보상·reset·관측 순서를 복제하거나 바꾸지 않는다. `finally`로 원래 update를 복구하고, physics counter로 중복 수집을 방지한다. policy counter·decimation sample 수를 확인해 신선한 평균만 사용한다. episode reset은 완료 episode 결과를 부모가 기록한 뒤 선택 환경의 힘 버퍼를 비운다. 다음 policy step은 모든 힘 버퍼를 새로 시작한다.

정책 step의2개 물리 sample에서3D 벡터를 평균한 뒤 현재 평면 목표 방향과 각도를 계산한다.1cm 이상에서 `max(0,1−angle/(π/2))²`,90도 이상0이다.1cm 미만은 점수1이지만 실제 접촉과 수평 합력1N 이상이 필요하다. 함수 내부에는 dt·weight를 곱하지 않으며 RewardManager가0.33과0.02s를 곱한다. 최대 방향 지급은 step당0.0066이다. 각도 점수는 힘 최소화나 모멘트 비용을 대체하지 않는다.

## 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple_semi_prof.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_hard.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  src/inspire_sweep_baseline/tests/test_fast_reset.py \
  -q -p no:cacheprovider
```

최종 전체 CPU 검사 결과: **119개 통과·2개 skip**. 기존 환경 AST38개 불변 검사도 통과했다. 변경 Markdown5개 수식 검사와 내부 링크262개 검사(오류0), 문서 저장소 및 수정 source 범위의 whitespace 검사도 통과했다. workspace 전체 diff 검사는 기존 사용자 변경 `docs/plan/PLAN15.md:60`의 trailing whitespace를 보고했으며 해당 파일은 수정하지 않았다.

검증 항목:

- 부모 전체 구성·직접 상속·분리된 config 객체·Gym/runner 등록.
- 2-of-3 이력·중복 호출·현재15cm 경계·비접촉/높이 미충족 개선분 소멸·왕복 재지급 방지·부분 reset.
- 0~180도 각도·1N 경계·1cm 바로 아래/정확히/밖·재이탈·현재 목표 방향 반전·무접촉/비유한 값.
- 평면 기준과3D 힘 비교: 동일 수평/수직 크기에서0.25, 상향/하향 대칭, 큰 수직력 감점,1cm 내부 예외 유지.
- 법선+마찰 합산·물체 쪽 부호·반대 substep 상쇄·회전 좌표·freshness·N 단위 dt 전달.
- Warp anchor 집계의 빈 contact·잘못된 범위·사용/미사용 NaN·미사용 큰 값 격리.
- 부모 step의 reward 전에 수집 완료·부모 outcome 기록 후 reset·예외 시 hook 복구.
- 기존 Finger/Simple/Prof/Hard/Relative-IK/Fast 회귀 포함.

개발 중 테스트 fixture의 float64 goal과 실제 float32 quaternion 불일치, mock Gaussian config signature를 정정했다. 회전 후 정확히1N 비교의 float32 반올림을 피하도록 회전 테스트에는1.01N을 사용하고, 정확한1N 경계는 identity frame에서 별도 검증했다. 마찰 집계는 전역 prefix 차분에서 미사용 큰 값이 유효 작은 힘의 정밀도를 손상할 수 있어, 실제 anchor만 읽는 Warp 집계로 바꿨다. CPU compilation에서 Warp range 인자를 int32로 명시 변환한 뒤 재검증했다.

## 미검증·실행

`nvidia-smi`가 드라이버와 통신하지 못해 native Isaac Sim/PhysX 환경 reset-step, CUDA kernel 실행, GPU Collection Time, 실제 법선·마찰 계측, 학습 성공률·누름/tilt 억제 효과는 미검증이다. CPU에서의 tensor/설정 검증은 실제 학습 성능을 입증하지 않는다. 실제 학습 checkpoint 전이도 실행하지 않았다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Semi-Prof-v0 --headless
```

설명서는 [Simple 환경 문서](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#semi-prof-v0-접촉-조건부-정밀-이동과-힘-방향)에 추가했다. [방향 계획](../../01_plan/FORCE_DIRECTION_REWARD_PLAN.md)은 최신 명세를 앞에 추가하고 최초 원문을 역사 자료로 보존했다.
