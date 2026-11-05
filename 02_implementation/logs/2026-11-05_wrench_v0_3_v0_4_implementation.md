# 2026-11-05 Wrench-v0_3 · v0_4 구현

## 요청·기준

사용자는 v0_2→v0_3→v0_4 직접 상속을 요청했다. v0_3은 장애물/속도 커리큘럼 삭제, Gray·White 각각0–4 균등 추출, 속도 보상 기준0.02m/s 고정, EEF12→14cm, Arm OSC 출력 범위 정규화 변화량·Hand 기존 변화량, 최초 진입 무감쇠 속력1→4cm/s다. v0_4는 Holding 계열의 최단 거리 개선 함수를 사용하고 EEF 높이 조건을 추가한다.

- Workspace 기준 commit: `5fc335cf2f5ba5ef1e117b922901900eeb0351e2`.
- 문서 저장소 기준 commit: `886c835c532153a3d231a96c5b7045150ffb644b`.
- 시작 시 `docs/plan/PLAN11.md` 사용자 변경과 문서 저장소의 미추적 로그3개가 있었다. 모두 보존했다. 커밋·checkout·submodule 포인터 이동은 수행하지 않았다.
- 활성 패키지의 현재 Wrench-v0_2 코드가 기준이다. 문서의 접촉 weight1.45와 달리 코드 weight0.1을 확인하고 코드 값을 상속했다.
- [최종 환경 계약·수식·실행 안내](../environments/WRENCH_V0_3_V0_4_ENVIRONMENTS.md).

## 구현과 의도

기존 역할별 `wrench.py`, `wrench_envs.py`, `wrench_ppo_cfg.py`에 파생 정의를 추가하고 Gym에 `Inspire-Wrench-v0_3`, `Inspire-Wrench-v0_4`를 등록했다. Runtime은 `WrenchEnv` 그대로다. PPO는 각각 직전 부모를 상속해 실험명만 `inspire_wrench_v0_3`, `inspire_wrench_v0_4`로 바꿨다.

| 위치 | 변경 전→후 | 의도·영향 |
| --- | --- | --- |
| `mdp/curricula/wrench.py` | v0_2를 상속, population/free-speed 항을None | 두 커리큘럼과 해당 로그 제거, 방향 일정 보존 |
| `mdp/event_functions/wrench.py` | 새 `reset_wrench_uniform_scene` | 독립 `torch.randint(0,5,(N,2))`, 부분reset·seed·기존 배치 재사용 |
| `envs/wrench_envs.py` | v0_3에서 bank75→175단계 | 각도7개마다 개수25쌍 지원; 물리 용량·후보16개 유지 |
| `envs/wrench_envs.py` | 높이0.12→0.14 | 부모 초기화가 contact 높이도 동기화 |
| `mdp/reward_functions/wrench.py` | 새 `WrenchV0_3ActionRatePenalty` | OSC 최종 토크/실제 joint bound로 정규화, 제어 step 이력·부분reset |
| `mdp/rewards/wrench.py` | free-speed0.1→0.02, 최초 진입0.01→0.04 | 나머지 params·weight 유지 |
| `mdp/reward_functions/wrench.py` | `WrenchV0_4GoalProgress(DexPlanarGoalProgress)` | Holding의 미터 개선량과 reset 수명 재사용, 지급만 높이 gate |
| `mdp/rewards/wrench.py` | v0_4 거리함수·params 변경 | tolerance0, weight3.7 보존 |

Arm의 해석은 정책 pose 입력이 아니라 **OSC가 포화 처리 후 실제 출력하는 관절 토크**다. 각 joint effort limit × effort_limit_scale을 minimum_effort_limit로 하한 처리한 값으로 나눈다. 제어 step 마지막 substep 출력끼리 비교하며 Hand는 부모 `action_rate_l2`를 그대로 사용한다. Arm·Hand 각각0.03, 그룹 cap100, weight−1, dt 계약을 보존했다.

v0_4는 높은 EEF에서 개선된 거리도 에피소드 최단 기록에는 반영하고 보상만0으로 만든다. EEF를 낮춰 과거 개선량을 회수하는 동작을 막으면서 Holding의 에피소드 전체 최단 거리 의미를 유지한다. 초기 거리 정규화는 없고 함수 내 dt 나눗셈을 상속한다. 기존 goal 성공 반경3cm와 새 progress tolerance0은 별도 개념이다.

## 최종 전체 대조

`test_wrench_v1.py`의 실제 official configclass 기반 검사에서 모든 설정을 순서까지 비교했다. leaf 자산·시뮬레이터는 CPU double이다. 아래 변경 필드만 부모 값으로 복원한 뒤 전체 `to_dict()`가 동일함을 확인했다.

| 비교 축 | v0_2→v0_3 | v0_3→v0_4 |
| --- | --- | --- |
| 등록·직접 부모 | 새 EnvCfg/PPO 등록, v0_2 직접 상속 | 새 EnvCfg/PPO 등록, v0_3 직접 상속 |
| Runtime·Scene·물리 용량·Command | 동일 | 동일 |
| Event | spawn callable, 불필요 count params 삭제, bank stages 변경 | 동일 |
| Observation·Action·센서·물성 | 동일 | 동일 |
| 높이 | goal/contact0.14 | 동일 |
| Reward | action-rate callable, speed/entry free_speed | 거리 callable 및 tolerance params만 |
| Reward 이름·순서·weight·나머지 params | 동일, 접촉0.1 유지 | 동일, 거리3.7 유지 |
| Termination | 동일 | 동일 |
| Curriculum | population/free-speed 비활성, 방향 일정 보존 | 동일 |
| PPO·시간 설정 | experiment_name만 변경 | experiment_name만 변경 |
| 로그 | 비활성 curriculum2항 제거, 새 실험명 | 거리 로그의 수치 의미와 실험명 변경 |

부모 재생성 결과도 기준과 동일했다. 추가로 `git show HEAD:<file>`의 기존 class/function AST를 현재 코드와 비교해 **기존27개 정의, 변경한 production7개 파일에서 불변**을 확인했다. 기존 등록·runtime·공유 OSC·Holding 함수도 변경하지 않았다. 요청하지 않은 디렉터리 이동이나 물리 객체 축소는 없다.

## 검증과 실패 이력

처음 기본 Python에는 pytest가 없었다. 기존 검증에 사용하던 `env_isaaclab` Python과 plugin autoload 비활성 설정으로 전환했다. 패키지를 설치하지 않았다.

기존 `test_wrench_v0_2.py:94`에 단독 `d`가 기준 commit부터 있어 collection이 NameError로 중단됐다. 해당 오타 한 줄만 제거했다. 기존 부모/자식 비교는 접촉 weight가 같다고 가정했지만 기준 코드 v0_2는0.1이므로 실제0.1을 명시적으로 검사하고 비교할 때 해당 term을 복원하도록 고쳤다. production 부모 코드를 수정한 것이 아니다.

기존 회귀4파일은 **89 passed in 11.25s**였다. 신규 검사 최초 실행은 float64 fixture 위치와 부모 float32 이력의 혼합 때문에 반복 호출에서 약1e−9 잔차를 보고3개가 실패했다. 실제 Isaac과 동일한 float32 위치/goal fixture로 맞췄으며 production 계산은 변경하지 않았다.

최종 실행:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q \
  src/inspire_sweep_baseline/tests/test_wrench.py \
  src/inspire_sweep_baseline/tests/test_wrench_v0_1.py \
  src/inspire_sweep_baseline/tests/test_wrench_v0_2.py \
  src/inspire_sweep_baseline/tests/test_wrench_v0_3.py \
  src/inspire_sweep_baseline/tests/test_wrench_v1.py
```

**103 passed in 18.29s**. 검증 내용:

- 부모/자식 전체 설정·등록·PPO 상속·부모 불변성.
- 두 독립 균등 정수 추출의 seeded 결과,25쌍 도달, 선택 행만reset, 빈reset 난수 보존.
- 175개 실제 CPU OBB bank 생성 및 모든 키 샘플, 활성 수/실제 개수/요청 상한.
- 임의 joint 순서·환경별 effort limit·effort scale을 적용한 토크 정규화, 원시 Arm 입력 무관성, Hand 변화·cap, 중복 호출·부분reset·전체reset.
- 14cm 직전·정확히·직후의 거리·실제 접촉 높이 경계.
- 최초 진입 속력1/4/6cm/s, 최대+25·감쇠·재지급 방지.
- 최단 거리 개선·정지·후퇴·복귀·높은 EEF 개선 소비·부분reset/새goal 첫 행동·목표 중심·dt0.01/0.02/0.05.
- 기존 v0/v0_1/v0_2/v1/v2 보상·상태·일정 회귀.

공식 `manager_based_rl_env.py`에서 마지막 `apply_action` 후 `common_step_counter` 증가, `reward_manager.compute` 순서임을 읽어 OSC 출력 샘플 시점을 확인했다. `tests/_wrench_probe.py`에 v0_3/v0_4의 실제 시뮬레이터용 설정 비교·활성 커리큘럼·고정 속도·개수 상한 검사를 추가했다. 이 probe는 이번 환경에서 실행하지 않았다.

변경 Python 전체(신규 테스트와 GPU probe 포함)의 `compile` 및 workspace/문서 저장소 `git diff --check`를 확인했다. 변경 Markdown5개의 수식 검사는 통과했다. 링크 검사에서 새 링크 오류는 없으며, 기존 패키지 README의 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 링크1개가 존재하지 않는 파일을 가리키는 것으로 검출됐다. `git show HEAD:src/inspire_sweep_baseline/README.md`에서도 같은 링크를 확인했으므로 이번 범위에서 변경하지 않았다.

## 미검증 범위·후속

`nvidia-smi`는 NVIDIA 드라이버와 통신할 수 없다는 오류(exit9)를 반환했다. 실제 Isaac Sim 초기화·물리 rollout/접촉·GPU 부분reset·PPO·학습·2048환경 생성 시간/메모리는 미실행이다. 특히175개 bank는75개인 부모보다 startup 생성량과 메모리가 증가하므로 GPU 호스트에서 확인해야 한다. CPU bank 검사는 GPU rollout을 대체하지 않는다.

학습 명령은 환경 계약의 `scripts/train.py`를 따른다. 학습·play 프로세스나 checkpoint를 만들지 않았고 `logs/rsl_rl`은 건드리지 않았다. 기존 사용자 변경·문서 미추적 파일은 보존했다.
