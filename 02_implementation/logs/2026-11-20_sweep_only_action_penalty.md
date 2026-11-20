# Sweep Only: 구동 범위 초과 비용을 사용하는 보존형 파생 환경

## 요청과 기준

사용자는 과거 Sweep Only 환경을 보존하고 별도의 파생 환경에서 팔 6축 ±π/2·손 6축 `[0, 실제 관절 상한]` 실행 제한, 팔/손 구동 범위 초과 비용, 기존 Action L2의 클리핑 전 입력 적용을 요청했다. IsaacLab과 모델 수정은 피한다는 앞선 의도를 유지했다.

기준 root commit은 `23a2f32b875c4343bbb78b3aae2f14e92cbc3600`이다. 시작 시 root에는 문서 submodule 변경만 있었고, 그 안의 인계·활성 안내·계열 설명·11월 19일 문서화 로그에 기존 변경이 있었다. 이를 되돌리지 않고 새 기록을 추가했다. `logs/rsl_rl` 및 기존 학습 로그·checkpoint는 변경하지 않았다.

이전 진단에서 v1-Test·v2-Test의 Actor 출력 과대와 표준편차 증가를 확인했다. 이번 변경은 클리핑으로 가려졌던 원본 액션 초과량에 학습 비용을 부여하는 실험이다. 발산 원인의 완전한 제거 또는 학습 성공을 입증한 결과가 아니다.

## 구현과 최종 계약 대조

6개 원본 ID 각각에 `-ActionPenalty`를 붙였다. EnvCfg와 PPO runner 모두 대응 원본을 직접 상속한다. 전체 ID·로그 이름·사용 명령은 [계열 안내](../environments/SWEEP_ONLY_FAMILY.md#actionpenalty-파생-환경)에 있다.

| 항목 | 부모 | 파생 환경 | 의도·영향 |
| --- | --- | --- | --- |
| wrapper clip_actions | π/2 | None | ActionManager에 원본 출력 전달 |
| 팔 Action class | WrenchRefactorOSCAction | SweepOnlyClippedOSCAction | 기존 OSC 호출 전에 6축 ±π/2 제한; scale·frame·제어기는 그대로 |
| 손 Action | FingerJointPositionAction | 동일 | 원래 있던 URDF 한계·mimic 적용; 실제 상한 6개 모두 π/2 미만 |
| ActionManager 이력 | wrapper 클리핑 후 값 | 원본 값 | 현재·이전 모두 보존, partial reset은 기존 manager 사용 |
| arm/hand_action_limit | 없음 | 각 weight −0.03 | 범위 초과량/전체 구간 폭의 제곱평균, cap 없음 |
| arm/hand_action_rate | 클리핑 후 차이 L2 | 원본 차이 L2 | 함수·각 weight −0.03·dt 처리·term 이름 유지 |
| Last Action 관측 함수 | raw_previous_action | legacy_clipped_previous_action | wrapper 제거 후에도 기존 ±π/2 관측값 유지 |
| PPO experiment_name | 원본 이름 | 원본 이름 + _action_penalty | 로그 분리 |
| 나머지 | 부모 구성 | 동일 | 전체 dict 대조로 확인 |

`Action L2`는 실제 기존 코드상 `sum((a_t-a_prev)^2)`인 변화 비용이다. 별도의 원점 기준 `sum(a^2)` 비용은 추가하지 않았다. 신규 범위 초과 비용은 정상 구동 구간의 굽힘이나 OSC 명령에는 0이다. 팔은 전체 폭 π, 손은 각 상한으로 나눈다. 신규 계수 −0.03은 기존 Action 비용을 참고한 초기값이며 조정된 최적값이 아니다. RewardManager가 dt=0.02를 한 번 적용한다.

동일한 유한 원본 입력에 대한 실행 명령은 부모와 동일하다. 손 구동 상한이 모두 π/2 미만이므로 부모의 공통 clip을 제거해도 기존 손 한계가 같은 최종 각도를 만든다. Last Action 관측도 기존과 동일한 ±π/2 클리핑값이며, 이번에 최종 손 관절 목표각으로 바꾸지 않았다.

Scene·Command·Event·reset·물체 스폰·IK·표면점·관측 차원·F/T·촉각·Sweep/Reach/후퇴 계수·Deadzone·종료·Curriculum·runtime은 보존했다. actor/critic·분포·학습률·entropy·수치 오류 검사는 변경하지 않았다. IsaacLab 소스와 모델 소스 변경은 없다.

## 변경 위치

- `envs/stabilize_sweep_envs.py`: 6개 직접 자식, 파생 전용 구성 연결.
- `agent/stabilize_sweep_ppo_cfg.py`: 대응 runner의 clip 해제와 별도 로그 이름.
- `mdp/action_functions/wrench_refactor.py`: 기존 OSC를 상속한 실행 제한 클래스.
- `mdp/reward_functions/stabilize_sweep.py`, `mdp/rewards/stabilize_sweep.py`: 초과량 계산과 두 term 구성.
- `mdp/observation_functions/stabilize_sweep.py`: 기존 Last Action 출력 범위 보존.
- 패키지 `__init__.py`: 새 Task ID 등록.
- `tests/test_sweep_only_action_penalty.py`: 경계·정규화·원본 보존·팔 제한·손 mimic 검사.
- `scripts/check_sweep_only_action_penalty.py`: 실제 전체 구성 대조와 wrapper/reset/step/부분 reset 검사.

## 검증

workspace 루트에서 실행했다.

```bash
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_sweep_only_action_penalty.py src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_sweep_only_action_penalty.py --headless

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_sweep_only_action_penalty.py --headless --task Inspire-Sweep-Only-v0-ActionPenalty --output /tmp/sweep_only_action_penalty_ik.json
```

- CPU **100 passed / 11.21초**. 최초 신규 테스트는 구성 실행 도구가 dict 대신 SimpleNamespace를 반환하는 것을 잘못 처리해 1개 실패했다. 테스트 접근 방식을 수정한 뒤 모두 통과했으며 production 구현 변경은 없었다.
- 실제 Isaac Sim·RTX 3090: **v1-Test-ActionPenalty와 v0-ActionPenalty 각각 seed42·2환경·wrapper 3step 통과**. Test/물체 옆 IK 초기화 모두 실행했다.
- 6쌍의 실제 EnvCfg·PPORunnerCfg를 import하고 `to_dict()` 전체를 비교했다. 위 변경 표의 leaf와 신규 두 term을 제외한 차이는 없었다. 직접 부모 관계·등록 runtime·별도 로그 이름도 확인했다.
- 새 자식 생성 전후 부모 인스턴스와 재생성된 부모 전체 설정이 동일했다. 변경된 production Python 파일의 기존 모든 최상위 class/function AST가 HEAD와 동일함도 확인했다.
- 원본 ±200 입력에서 Manager 이력·입력 tensor가 변하지 않고 팔은 ±π/2, 손은 URDF 한계로 제한됨을 실제 Action term에서 확인했다. 이 극단 입력은 처리와 비용만 검사하고 physics step에는 적용하지 않았다.
- 선택한 한 행의 reset에서 현재·이전 원본 이력은 0, 다른 행 이력은 유지됨을 확인했다.
- 실제 step은 팔0·손 상한의1.1배를 사용했다. 관측66D+64D·유한 보상·원본 Manager 입력·상한 손 목표·초과 비용0.01·가중 비용률−0.0003을 확인했다. 비선택 신규 버전4종의 물리 실행은 별도 반복하지 않았다.
- 결과 JSON은 `/tmp/sweep_only_action_penalty.json`, `/tmp/sweep_only_action_penalty_ik.json`; stdout은 `/tmp/check_sweep_only_action_penalty.log`, `/tmp/check_sweep_only_action_penalty_ik.log`에 기록했다. 임시 산출물은 장기 보존 자료가 아니다.
- 변경 문서4개의 Markdown 수식 검사와 링크 검사(내부329·외부6, 오류0), root·문서 저장소의 `git diff --check`를 통과했다.

## 미검증과 후속 확인

장기 PPO 학습·2048환경 성능·성공률·엔트로피 및 출력 규모의 안정화는 미검증이다. 큰 출력이 있는 기존 checkpoint 재개는 큰 새 비용을 유발할 수 있으며 이번에 수행하지 않았다. 수치 오류 검사를 우회하지 않는다. 원본 출력이 보상에서 억제되는지는 향후 새 학습에서 확인해야 한다.
