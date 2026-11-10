# Finger-v1/v2 구현과 검증

[환경 계약](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#finger-v1v2-출력-범위와-정밀-이동후퇴) · [환경 안내](../08_ACTIVE_ENVIRONMENTS.md)

## 요청·확정 사항

기준 root commit `f75b3b0`. 사용자 요청은 `Inspire-Sweep-Simple-Finger-v0`를 직접 상속한 v1과, v1을 직접 상속한 v2의 추가다. 기존 `docs/plan/PLAN15.md` 및 문서 submodule 변경을 보존했다. 학습 로그와 기존 환경은 수정하지 않았다.

구현 전 질문에 대해 사용자가 다음을 확정했다.

- Arm 제한은 scale 전 raw Translation±0.5, Rotation±π/2이다. 기존 scale 후±1.5cm/±13.5도. 손도 URDF/Articulation joint 범위로 제한한다.
- 목표 XY2cm 미만 **연속3초** 후 게이트를 영구 유지한다. 달성 전 이탈하면 timer0. 이후 이탈해도 해제하지 않는다.
- 후퇴 목표는 지정된 물체 목표에서 초기 물체 방향으로5cm, 초기 선반 윗면+8cm 높이. 후퇴 Reach의 최대 보상 반경은2cm.
- Distance는2cm에서 끝내지 않고 **중심0cm까지** 계속 지급한다. 직전 합의의 누적 보상 곡선 면적 일치형 로그 변환을 적용한다.

게이트 활성화는 즉시 종료를 뜻하지 않는다. 기존10초 timeout과 실패 우선 처리를 보존하면서 success 거리 조건만 게이트 이력으로 교체한다.

## 전체 대조

| 구성 | v0 → v1 | v1 → v2 |
| --- | --- | --- |
| EnvCfg/runtime | 직접 상속; runtime 입력 clip | 직접 상속; gate 생성/부분 reset |
| Scene/자산/물성/Fast reset | 동일 | 동일. 후퇴 좌표만 reset 때 추가 캐시 |
| Commands/목표 분포 | 동일 | 동일 |
| Observation | Last Action tanh→bounded raw. 나머지 term/순서/차원 동일 | 동일. 게이트·후퇴 좌표·현재 타겟 GT 추가 없음 |
| Action | 정책 출력12축 범위 제한, runtime/term 입력 clip. 원래 scale/gains 보존 | 동일 |
| Rewards | 팔 joint velocity weight−0.03→−0.06 | Distance/Reach/Contact 세 callable·필요 params만 변경 |
| 기타 비용 | action-rate raw 제곱합·cap/weight와 hand velocity−0.01 등 동일 | `target_inverse_distance` 선형−25.94 포함 그대로 |
| Termination | 팔속도 초기2rad/s | success만 timeout & gate & 무실패 |
| Curriculum | 팔속도2→1,2000–5000,250주기 | 동일. Holding/가속도 일정 없음 |
| Metrics | 기존 최근10,000개 집계·키 동일 | success 분류 의미 변경. 목표3cm 점유 시간 metric은 보존 |
| PPO | Actor distribution만 bounded Gaussian, 실험명 변경 | 실험명만 변경 |
| 모델 구조 | policy66+obstacles64, encoder64→16, MLP256/128/64, output12 유지 | 동일 |

Scene/Command/Event/reset의 기존 기하·난수·IK 구성, 손 stiffness1.2/damping0.06/effort10/velocity1과 팔 물리 velocity3.14는 보존한다. 속도 종료 threshold는0–2000에서2.0,2250에서1.9166666667,4750에서1.0833333333,5000부터1.0이다. 이는 물리 속도를 강제로1.0으로 제한하는 변경과는 다르다.

## 정책 출력과 클리핑

새 `agent/sweep_simple_distributions.py`의 `FingerBoundedGaussian`이 각 축 범위로 affine tanh 변환을 수행한다. 학습 샘플·deterministic 출력·JIT/ONNX export 경로가 동일 변환을 사용한다. Last Action에는 별도 tanh를 적용하지 않는다. Env 입력/ActionTerm의 raw 이력/관측도 동일 범위로 방어적으로 clip한다. rate 비용은 실제로 허용된 raw 명령 이력을 읽는다.

PPO likelihood는 역변환과 log-Jacobian을 사용하며, KL은 underlying Normal의 정확한 KL을 사용한다. entropy는 Normal entropy에 Jacobian의 재매개화 표본 추정치를 더한다. float32 포화 endpoint의 역변환에는1e-6 clamp를 사용한다. 표준편차는 log parameter로 양수 보장, latent log-std [−5,2] 제한. std 진단은 latent Normal 단위다. 이는 출력 범위를 보장하지만 모든 학습 발산을 방지한다는 뜻은 아니다.

손 경계는 원본 오른손 URDF 수치를 공유 상수로 사용한다. 실제 오른손 합성 USD의 각도 한계와 rad 변환 대조도 통과했다. 기존 mimic 비율과12개 physical joint target mapping은 유지한다.

## v2 보상·상태

`FingerRetreatState`를 Reach/Contact/success가 공유한다. 같은 `common_step_counter`에서는 timer를 한 번만 갱신한다. 게이트는150개 연속 policy sample에서 XY<0.02m이면 활성화되며, 정확히0.02m는 이탈이다. NaN/Inf 거리도 달성 전 timer를 지운다. 활성화 후에는 거리와 무관하게 유지한다. reset sample 자체에는 체류 시간을 부여하지 않는다.

후퇴 목표는 지정 goal 기준으로 계산하며 실제 gate 순간의 물체 위치를 따라 움직이지 않는다. 높이는 부모의 초기 선반 표면 기준을 사용한다. Reach의 초기 예산·weight30·distance_scale0.1을 유지하고 활성화 이후에만 target과 near_radius를 교체한다. Contact는 기존2-of-3/+1/−2 규칙을 유지하되, 기존3cm 우회 대신 게이트가 count/reward20을 보장한다. 접촉 history를 가짜 표본으로 채우지 않는다.

Distance는 노이즈 없는 현재 타겟 link origin의 world XY 거리다. epsilon1cm, 초기 거리별 누적 곡선 면적 보정이며, 초기9cm에서 기존 총9→제안13.92398이 된다. 기존과 동일하게 에피소드 최고 기록 개선만 지급하고 dt 중복 곱을 상쇄한다. 초기 거리가0이면 유한한0, 매우 짧은 거리의 상쇄 오차는 series와 float64 계산으로 처리한다.2cm 안/게이트 후에도 중심 방향 개선 보상은 유효하다.

게이트 성공은 후퇴 완료를 요구하지 않는다.10초 timeout에서 gate를 평가하며 동시 실패는 우선한다. 게이트 달성 후 조기실패하면 timeout 성공에는 포함하지 않는다. 부모 runtime이 종료 결과를 집계한 **뒤** 선택된 환경의 gate/timer/target을 reset한다.

## 검증

다음 명령으로 기존 회귀와 새 검증을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_hard.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  src/inspire_sweep_baseline/tests/test_fast_reset.py \
  -q -p no:cacheprovider
```

reset 집계 순서·XY/첫 transition·action config 대조까지 포함한 위 최종 전체 명령 결과는 **110개 통과·2개 skip**이다. root HEAD와 기존 클래스/함수47개 AST 본문이 동일함도 별도 확인했다. 수정 Markdown 수식과 문서 저장소 내부 링크 검사(오류0), root/문서 diff whitespace 검사도 통과했다.

- 공식 configclass/Manager Cfg와 Sim/Scene leaf doubles로 부모 전체 구성·term 순서·callable·params·weight·일정·독립성 대조. v1/v2 Gym 등록과 runner 상속 확인.
- clipping 전후 실제 수치, OSC scale 적용 순서, raw Last Action, 손 URDF/USD 한계·follower target 유지 검증.
- bounded 분포 log-prob를 PyTorch TransformedDistribution과 대조, KL/finite entropy/극단 입력 bounds 확인.
- 실제 설치된 RSL-RL PPO의 CPU rollout/update, actor parameter 갱신, checkpoint save/load, full actor JIT 출력 일치, ONNX 입력130D 확인. ONNX runtime 실행은 아님.
- gate 경계 바로 아래/정확히/위,149/150회, 중복 호출, 이탈·재진입, activation latch, 선택 reset, target 좌표 및 parent outcome 집계 순서 검증.
- Distance 초기6/9/12cm에서 수치 적분으로 면적 일치, 가까울수록 민감도 증가, 왕복 재지급 방지, XY/GT source와 새 goal 첫 transition 확인.
- 기존 v0/Simple/Prof/Hard/Relative-IK/Fast 회귀 포함. 초기 실패는 테스트 harness의 time_out placeholder와 float64 fixture/step_dt 누락이었으며 실제 함수·float32 상태를 사용하도록 수정했다. 역사 상속 검사에서 공유 Action 연산 구현 상속과 환경 Cfg/runtime 상속을 구분했다.

## 미검증·실행

현재 `nvidia-smi`가 드라이버와 통신하지 못한다. native Isaac Sim 환경 import/PhysX reset-step·GPU rollout·후퇴 경로·성공률·학습 안정성·실물 속도는 미검증이다. CPU PPO 테스트는 물리 학습 성능의 증거가 아니다. 출력·종료 변경이 현실적인 속도를 달성하는지는 실제 rollout에서 확인해야 한다.

v0 checkpoint는 분포 저장 parameter와 Last Action 의미가 달라 무변환 resume 대상이 아니다. v1/v2는 모델 구조가 같지만 본 작업에서는 실제 학습 checkpoint 전이를 수행하지 않았다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Finger-v1 --headless
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Finger-v2 --headless
```

## 환경 안내 문서 후속 정리

사용자의 문서 갱신 요청에 따라 `SWEEP_SIMPLE_ENVIRONMENTS.md`에 Finger-v0/v1/v2의 액션·속도·보상·성공 조건 비교 표를 추가했다. 기존 공통 설명의 “Finger도3cm 접촉 예외 상속”을 v0/v1로 한정하고, v2의 연속3초 게이트 예외를 명시했다. 모든 관측을 clip한다는 오해를 피하도록 Last Action만 구분했으며, 물리 속도 제한과 종료 임계값, PPO 하이퍼파라미터와 정책 분포 변경을 분리해서 설명했다. 체크포인트 호환 범위와 최종 CPU 검사110개 통과·2개 skip도 일치시켰다.

환경 코드·동작 변경은 없다. 문서의 상세 v1/v2 명세와 비교 표·공통 계약을 최종 대조했다. 수정한 두 문서의 수식·내부 링크 및 whitespace 검사를 수행하며, 문서만 수정하므로 CPU 회귀는 재실행하지 않는다. GPU/물리 학습 미검증 범위는 위와 동일하다.
