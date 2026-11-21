# Single Contact v1 구현·검증

## 요청·기준·의도

사용자는 [최종 명세](../../01_plan/environments/2026-11-21_SINGLE_CONTACT_V1_SPEC.md)에 따른 환경 구현과 관련 테스트·정적 검사를 요청했다. 명세만 작성하던 이전 범위를 이 요청으로 갱신한다. 새 `Inspire-Sweep-Single-Contact-v1`는 `Inspire-Sweep-Single-Contact-v0` 직접 자식이며 기존 계열 파일 배치와 부모 물리 lifecycle을 보존한다. 기준은 root main `4102344`, 문서 저장소 `85ec22b` 및 요청 직전 작업트리다.

이전 분석기 수정·새 분석 스크립트·사용자 `docs/instruction.md`·IsaacLab의 기존 untracked 항목·문서 작업트리 변경을 보존했다. `logs/rsl_rl`과 기존 학습 체크포인트를 변경하지 않았다. 별도 commit/push는 수행하지 않았다.

## 변경 전후와 전체 대조

| 항목 | v0 | v1 |
| --- | --- | --- |
| 등록 | 기존 ID 유지 | `Inspire-Sweep-Single-Contact-v1` 추가 |
| EnvCfg/runtime/state/PPO | 기존 클래스 유지 | 각각 직접 상속한 `SweepSingleContactV1EnvCfg`/`SweepSingleContactV1Env`/`SingleContactV1SweepState`/`SweepSingleContactV1PPORunnerCfg` |
| Reach | live 중심 거리10cm plateau·35cm 선형 감소, weight0.8 | 이동 접근점의5cm 초과 거리 변화/policy dt, weight4.9 |
| 접근 기하 | 별도 접근점 없음 | scaled bounds XY 반폭 norm의 외접 반경. 구역1/2/4는 밀기 반대편, 구역3 전체는12시에서 시계방향+15° 단일점. 회전 독립·중심 이동 추종 |
| 방향 | 3D 힘 norm의 양수 cosine 정렬 | 수평 힘 각도의 `2 exp(-ln(2)(theta/(pi/6))^4)-1` |
| 접촉면 | 선호1.5/반대0.7/중립1 | 같은 실제 표면 하중 혼합. 양수에만 적용, 음수 배율1 |
| Joint | 기존 속도 L2와1rad/s 초과 종료 | 기존 term 그대로 + 실제 종료 flag/dt에 weight−3인 마지막16번째 보상 |
| Scene/Command/Event/reset | 원래 구성 | 동일. 보상 기하만 최종 부모 reset 뒤 초기화 |
| 관측·Action | policy66D·obstacles64D·action12D | 동일. 접근점/GT 입력 추가 없음 |
| 시간·종료·성공 | dt0.01×decimation2·10초·엄격히3cm 미만 timeout 성공 | 동일. 1rad/s 정확히 경계는 팔 종료 아님 |
| Curriculum | 빈 구성 | 동일 |
| PPO | 기존 모델·36step·8epoch/4batch·gamma0.98 등 | experiment name만 `inspire_sweep_single_contact_v1` |

실제 Isaac Lab `to_dict()` 비교에서 v0/v1 전체 환경의 차이는 `sweep_progress` callable, `reaching` callable/params/weight, 신규 `arm_joint_failure`뿐이었다. 원래15개 활성 보상 순서와 나머지 callable/params/weight, 모든 Manager 설정이 일치했다. 부모 객체와 재생성한 부모 객체도 동일했다. PPO 전체 dict는 로그 이름을 제외하고 같았다. 별도 AST 비교로 기존 함수·클래스19개 정의와 기존 등록 호출이 HEAD와 동일함을 확인했다. 부모의 함수 결과는 기존 CPU 회귀 테스트도 통과했다.

## 구현 위치·상태 수명

- [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_v0_envs.py)에서 보상3개 차이만 연결한다. mutable 부모 객체를 제자리 변경하지 않는다.
- [v1 state](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/sweep_v0_state.py)는 기존 boolean 접촉 이력을 상속하고, 부모 `finish`의 previous distance 갱신 전에 거리 변화를 확보한다. `positive`의 의미를 바꾸지 않고 별도 `signed_progress`를 사용한다.
- [runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/sweep_v0.py)은 `_state_type`과 부모 `_reset_idx` 완료 뒤 기하/초기 오차 저장만 추가한다. physics capture/step 루프를 교체하지 않는다. Command reset 이전의 이전 목표를 초기 오차에 사용하지 않는다.
- [보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/stabilize_sweep.py)는 cached 증분/policy dt 및 실제 TerminationManager flag/policy dt를 반환한다. RewardManager의 dt 적용 후 각각4.9×거리 변화, 일회−3이다.
- [접촉면 callable](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/sweep_contact_preference.py)은 부모의 실제 target-only 표면 하중 계산을 재사용하며 policy tick당1회만 조회한다. 초기 구역을 고정하고 양수/음수를 분리한다.
- [계측](../../../../src/inspire_sweep_baseline/scripts/reward_timeline_probe.py)은 reset 이전에 명세9.4의 Reach 기하/오차/증분·방향/접촉 gate·면 배율·양음 기여·Joint event를 같은 시간축으로 저장한다. 초기 EEF world pose와 선반 reference pose도 보관한다. Actor 입력은 변경하지 않는다.

부분 reset은 해당 환경의 초기 오차·반경·방향·cache만 바꾼다. 같은 step 중복 조회는 같은 값을 반환한다. 마지막 step의 이전 episode 보상을 계산·기록한 뒤 자동 reset하므로 순간이동은 Reach 변화에 포함되지 않는다. 잘못된 Reach 기하/비유한 거리는 환경 ID를 포함한 오류로 진단한다. 무효 힘/목표 거리0은 방향 항만 안전하게 mask하고 기존 후퇴 비용은 유지한다.

## 실행한 테스트·정적 검사

Python은 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`, 작업 디렉터리는 workspace root다.

```powershell
python -m pytest src/inspire_sweep_baseline/tests/test_sweep_single_contact_v1.py src/inspire_sweep_baseline/tests/test_sweep_single_contact.py src/inspire_sweep_baseline/tests/test_sweep_v0.py src/inspire_sweep_baseline/tests/test_stabilize_sweep.py src/inspire_sweep_baseline/tests/test_sweep_only_action_penalty.py src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py src/inspire_sweep_baseline/tests/test_goal_terminations.py -q
python src/inspire_sweep_baseline/scripts/check_sweep_single_contact_v1.py --headless
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Single-Contact-v1 --num_envs 16 --seed 42 --headless --max_iterations 1 --resilient-attempt-dir outputs/sweep_single_contact_v1/training_smoke --resilient-target-iterations 1
```

| 검사 | 결과·근거 |
| --- | --- |
| CPU | **196 passed**,14.54초. Reach5cm 경계·±1cm·3D·왕복·추종·중복조회·부분reset·실제 centroid 경로의 yaw/roll/pitch 독립, 구역3 전체/구역1 일반 규칙·반경 갱신, signed 방향0–180° 단조성·수직 힘 독립·gate·부호·면 배율, 실제 팔 속도 종료 경계와 dt 독립−3, 기존 계열 회귀 |
| GPU | RTX4070·seed42·4환경·11step, reset/부분reset/자동reset, 실제 RewardManager의16개 term·총합·Reach 첫step/telescoping·terminal 이전 오차 사용·보상 cache 검사 |
| Joint event 주입 | 실제 TerminationManager의 해당 term 결과를 테스트용으로 주입하여 auto-reset과 최종−3을 확인. 실제 속도 판정은 CPU의 운영 함수로 별도 검사. 정상 timeout·후속 step Joint 비용0 |
| 학습 smoke |16환경×36step, PPO1회 업데이트(8epoch·4batch). `training_status.json` completed. value loss3.2944·surrogate loss−0.0621·entropy17.0066 유한, 모델 저장 완료 |
| 정적 | 변경 Python10개 `py_compile`, 기존 정의19개·등록 호출 AST 동등성 검사 통과. 전용 linter는 설치되어 있지 않아 실행하지 않음 |
| 문서·diff | 아래 최종 문서 검증 결과에 기록 |

첫 CPU 실행에서는 테스트가 같은 state의 region view를 다시 reset 인자로 전달할 때 PyTorch alias 오류가 드러나 명시적으로 clone했다. 45° 기대값의 수기 근삿값과 object collection의 테스트 fixture 차원도 교정했다. 최종196개는 모두 통과했다. 이는 실제 코드에서 실행한 검증과 테스트 fixture 교정을 구분하기 위한 기록이다.

## 산출물·미검증 범위

- [GPU 검증 요약](../../../../outputs/sweep_single_contact_v1/smoke.json), [trace](../../../../outputs/sweep_single_contact_v1/trace.npz), [초기 장면·world pose](../../../../outputs/sweep_single_contact_v1/initial_scene.npz), [보상 term](../../../../outputs/sweep_single_contact_v1/reward_terms.json).
- [CPU 결과](../../../../outputs/sweep_single_contact_v1_cpu_tests.txt), [GPU console](../../../../outputs/sweep_single_contact_v1_gpu_console.txt), [정적 검사](../../../../outputs/sweep_single_contact_v1/static_checks.json).
- [학습 console](../../../../outputs/sweep_single_contact_v1_training_console.txt), [완료 상태](../../../../outputs/sweep_single_contact_v1/training_smoke/training_status.json), [smoke 모델](../../../../outputs/sweep_single_contact_v1/training_smoke/model_0.pt). 이 파일의0은 runner 저장 iteration 표기이며1회 업데이트가 실행됐다.

장기 학습,2048환경 성능, 새 정책 성공률·구역3 당기기·손바닥/손등 사용 개선·0.8rad/s 초과율·지나침 개선은 미검증이다. 기존 v0 성공82개 재산정의 약3:7은 가중치 초기 근거이며 새 정책에서 비율이나 행동 향상을 보장하지 않는다. 기존 Sweep50/−10 비대칭의 왕복 이득 가능성과 signed 방향의 근거리 복구 억제 위험은 보류된 명세 그대로 남는다. 기존 모델과 관측 차원은 같지만 smoke를 행동 성능 평가로 취급하지 않는다.

최종 문서 검증: 변경한 문서5개의 math 검사, 내부 링크362개·외부 workspace 링크34개 검사(오류0), root와 문서 저장소 git diff --check를 통과했다. 패키지 README의 새 링크2개도 대상 파일/anchor를 확인했다. 최종 GPU trace의 모든 배열이 유한하고 보상 양음 분해가 RewardManager 기여와 일치했다. 저장된 optimizer state의 모든 tensor가 유한하며 step32(8epoch×4batch)로 실제1회 PPO 업데이트를 확인했다.
