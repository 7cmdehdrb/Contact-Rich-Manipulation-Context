# Relative-v0 F/T 관측 한도·Action Rate cap 구현

2026-11-07. [확정 계획](../../01_plan/RELATIVE_V0_FT_OBSERVATION_LIMIT_PLAN.md)에 대한 사용자의 후속 구현 요청을 적용했다. Relative-v0와 이를 상속하는 v2/v3가 대상이다. 사용자는 Windows GPU/VPN 정상 연결과 필요시 스모크를 허용했고, F/T 제한에도 질량·관성 보정이 보존돼야 한다고 명시했다.

기준 commit은 `eb95e4281a0188cb12d7fcf42072df1984fa25ac`이다. 작업 시작 시 제품 코드는 clean이고 IsaacLab의 기존 untracked 작업과 이 대화에서 작성한 미추적 문서가 있었다. 기존 변경을 보존한 채 이번 변경은 미커밋 작업트리에 남겼다.

## 변경 전후와 적용 경계

| 대상 | 이전 | 이후 |
| --- | --- | --- |
| 최종 F/T 관측 | 축별 한도 없음 | Fx/Fy/Fz 각각±150N, Mx/My/Mz 각각±8N·m |
| Arm raw action 변화량 제곱합 | cap 없음 | 최대100 |
| Hand clamp action 변화량 제곱합 | 명시적 cap 없음 | 최대100, 기존[0,1] 처리 유지 |

`envs/wrench_refactor_envs.py`의 Relative-v0에 `wrist_wrench_observation_limits=(150,150,150,8,8,8)`와 reward 인자 `arm_max_cost=hand_max_cost=100`을 정의했다. v2/v3는 별도 제한값을 복제하지 않고 이 설정을 상속한다. v3의 reward class 교체 후에도 부모 post-init이 해당 action-rate 인자를 적용한다.

`runtime/wrench_refactor.py`의 `load_managers()`에서 한도 설정이 있는 경우 모든 활성 관측 그룹의 `wrist_wrench` term에 device tensor clip을 연결한다. 기존 ObservationManager의 **func → modifier → noise → clip → scale** 중 clip을 사용한다. 따라서 noise가 켜지거나 꺼져도 최종 한도를 보장한다. manager가 복제한 live config에만 tensor를 붙이며 원래 EnvCfg는 직렬화 가능한 tuple을 유지한다. 관측58D·64D 및 term 이름·순서는 그대로다.

원시 반력이나 보정 성분을 먼저 자르지 않는다. `PureWrenchReader`의 실제 PhysX 질량·관성, 중력·가속도·회전항, 기준점 이동과 좌표변환은 변경하지 않았다. `PureWristWrench.__call__()`의 직접 반환과 `world_wrench()`도 그대로이므로 보상과 물리 진단은 제한 전 보정값을 계속 읽는다. policy와 v2 critic 모두 동일 한도를 적용한다.

`mdp/reward_functions/wrench_refactor.py`의 공유 `policy_action_rate_penalty()`에 선택적 그룹별 cap 인자를 추가했다. 기본값None을 유지하여 Refactor-v0_1/v1_1/v2_1/v3_1에는 기존 uncapped 동작이 남는다. Relative-v0만100을 지정한다. raw Arm, clamp Hand, 계수0.03/0.03, weight-1, RewardManager의 dt 적용은 유지했다. 실제 action 자체를 clipping하거나 OSC 토크 변화량으로 바꾸지 않았다.

Hand 제곱합은 기존[0,1] 처리로 최대2이며 dt0.02초 기준 전체 action-rate step 비용의 최대 절댓값은0.0612다. 기준 이하 sample에서는 기존 함수값을 보존한다.

## CPU 및 설정 검증

기존 Isaac Lab conda Python으로 다음3개 파일 **82개 통과**:

```powershell
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -m pytest -q src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench_refactor_relative.py src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py
```

그룹별 합산 cap 경계·상한 초과·독립 cap·입력 불변·비Relative default 보존, runtime의 policy/critic clip 연결과 raw reader 보존, v0/v2/v3 전체 설정 차이, 부모 격리 및 Newton–Euler 보정 검사를 포함한다. 최초 실행은81통과/1실패였고, 기존 테스트의 Linux 경로 문자열 가정으로 Windows의 backslash 경로가 실패한 것이었다. 해당 assertion을 `Path(...).as_posix()`로 바꿔 재실행했다. 제품 동작 변경은 없다.

## GPU 스모크

Windows RTX4070에서 기존 `_wrench_refactor_relative_probe.py`로 버전별2환경×180step을 검증한다. 실제 manager에서 과대 F/T를 입력하는 진단 fixture로 noise 유/무 모두 최종 clip을 대조한다. 단순히 자연 rollout이 범위를 넘지 않는지만 검사하지 않는다. 설정 전체 allowlist·비Relative 부모 격리·부분 reset·차원·유한값·물성·EEF OSC·커리큘럼 경계를 함께 확인한다.

```powershell
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -u src/inspire_sweep_baseline/tests/_wrench_refactor_relative_probe.py --version 0 --num_envs 2 --headless --device cuda:0 --output outputs/relative_limits_validation/v0
```

version과 output을2/3으로 바꾸어 하위 환경도 실행한다. 결과는 [검증 산출물 폴더](../../../../outputs/relative_limits_validation)에 저장한다. v0 첫 실행은 모든 assertion과 최종 JSON을 완료했지만 PowerShell의 native stderr 리다이렉션 실행이exit1을 반환했다. 이후 실행은 Python subprocess로 stdout/stderr를 동일 파일에 저장하고 실제 subprocess 종료 코드를 별도 확인한다. 최초 v0를 정상 process exit로 주장하지 않는다.

## 질량·관성 보정의 실제 물리 검증

새 `_wrench_refactor_relative_wrench_probe.py`는 현재 Relative-v0의4환경에서 선반·물체를 진단 프로세스 안에서만 격리하고 실제 physics를 진행한다. 정책 관측의 noise는 끈다. **clip 이전 residual을 검사**하므로 한도로 잘라서 보정 오차를 숨기지 않는다. 매step 최종 관측이 동일 보정 sample의 clip 결과인지도 대조한다.

```powershell
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -u src/inspire_sweep_baseline/tests/_wrench_refactor_relative_wrench_probe.py --headless --device cuda:0 --output outputs/relative_limits_validation/ft.json
```

실제 subprocess exit0, `status=passed`. 실제 손 합계 질량0.7900000215kg, Axia 하우징0.2800000012kg이며 하우징은 측정 joint 상위이므로 손 보정 목록에서 제외된다. 정적 raw 힘 norm은7.74980N로 중력 부하가 실제 존재했다.

| 시험 | sample 수 | 최대 힘 norm 잔차/오차 | 최대 모멘트 norm 잔차/오차 | 허용오차 |
| --- | ---: | ---: | ---: | --- |
| 정적 중력 보정 | 40×4환경 | 2.963e-6N | 8.511e-6N·m | 0.15N / 0.02N·m |
| Arm·Hand 운동 보정 | 160×4환경 | 4.624e-6N | 6.494e-4N·m | 0.5N / 0.05N·m |
| 알려진 외력·모멘트 | 40×4환경 | 5.473e-6N | 4.426e-3N·m | 0.15N / 0.02N·m |

외력은 실제 손 링크 COM에 가하고 EEF 원점으로 모멘트를 이동한 기대 반력과 비교했다. 측정치와 기대치의 부호·기준점도 검증했다. 시험 중 전체 관절 최대속도는 약1.000003rad/s다. 수치 오차가 완전히0이라는 의미가 아니라, 기존 허용오차 안에서 중력·관성 제거와 외력 보존을 확인했다. 고속 충돌·모든 자세에서 동일 오차를 보증하지 않는다.

## 기존 실패 자료 재생

원본 `logs/TEMP/relative`의 failure 덤프를 읽기 전용으로 로드하고 업데이트 직전 모델 및 저장 action에 변경을 적용했다. [재생 수치](../../../../outputs/relative_limits_validation/replay_effect.json).

| 실패 자료 | 기존 Arm 정책 평균 최대 절댓값 | F/T clip 후 평균 최대 절댓값 | 기존 최대 action-rate step 비용 | 그룹 cap 후 비용 |
| --- | ---: | ---: | ---: | ---: |
| v0 | 11,981.53 | 1,821.14 | 185,699.78 | 0.0612 |
| v2 | 7,403.10 | 2,617.86 | 62,790.54 | 0.0612 |

action-rate 비용은 reset 경계가 아닌 저장된 인접 action에 실제 수정 함수를 적용했다. F/T clip 후 정책 출력 비교와 저장 action 비용 비교는 별도 개입이다. 새로운 action으로 물리를 재생하거나 바뀐 rollout return을 재계산한 결과가 아니다. F/T clipping만으로 기존 정책의 큰 action이 모두 없어지지는 않는다.

## 최종 대조와 미검증 범위

제품 코드 변경은 EnvCfg·runtime 관측 clip 연결·reward 함수의 선택적 cap에 한정한다. USD·공통 센서/보정·noise·모델/PPO·물성·reset·termination·curriculum·v3 고유 보상은 보존한다. 기존 IsaacLab 서브모듈의 사용자 작업과 `logs/rsl_rl`은 건드리지 않았다. 학습 로그를 정리하거나 checkpoint를 수정하지 않았다.

v0/v2/v3의2환경×180step 전체 probe 검사가 통과했다. v2/v3 subprocess exit0이며, v0도 후속 실제 학습 스모크에서 process exit0을 확인했다. 세 환경의 초기 바닥 높이 오차0m, 주차 물체 최대 drift3.815e-6m다.

추가로 `train.py`에서 Relative-v0 **32환경×2 PPO iteration**을 완료했다. `training_status.json`은completed/last_iteration1이고 유한 checkpoint 저장 검사까지 통과했다. 원본 `logs/rsl_rl`에 쓰지 않도록 기존 worker의 출력 경로 인자를 사용했으며 자동 재시작 supervisor는 실행하지 않았다.

```powershell
& 'C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe' -u src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-v0 --num_envs 32 --headless --device cuda:0 --max_iterations 2 --resilient-attempt-dir outputs/relative_limits_validation/train_v0 --resilient-target-iterations 2
```

학습 YAML에서도 그룹 cap100과6축 F/T 한도의 직렬화를 확인했다. 보정 구현·reader·noise 파일의 diff는 없고, 변경 제품 코드 전체를 요청의 두 항목과 대조했다. 변경 문서의 math 검사, 전체514문서 링크 검사 및 root/docs `git diff --check`가 통과했다. 별도 문서 렌더링 검사는 수행하지 않았다. 장기 학습·여러 seed·고속 충돌 전 범위·실제 센서 하드웨어 정확도는 검증 범위 밖이다.

패키지 README 갱신 후 변경8문서 math 검사는 통과했다. README까지 확장한 외부 링크 검사에서는 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1개가 검출됐다. 작업 전 HEAD에도 동일 링크가 있음을 확인했으며 이번 변경 링크에는 오류가 없다. 무관한 과거 링크는 수정하지 않았다.
