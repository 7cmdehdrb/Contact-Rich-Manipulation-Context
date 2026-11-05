# 2026-11-04 Wrench-v0_1 접촉·각도 feasibility 환경

[환경 계약](../environments/WRENCH_V0_1_ENVIRONMENT.md) · [부모 계약](../environments/WRENCH_V0_V1_ENVIRONMENT.md)

## 요청과 기준

사용자는 `inspire_wrench_v0`를 직접 상속하는 `inspire_wrench_v0_1`을 요청했다. target_contact 제거, target_goal_distance에 이전·현재 접촉의 AND와 목표→시작/현재 위치의 코사인을 곱하고, deadzone 커리큘럼을 제거하여40°로 고정하며 목표 거리 범위를 절반으로 줄인다. 이후 **거리3cm 미만에서 코사인 계수1.0 고정**을 추가 요청했다.

코드 기준 HEAD는 `d2ae15b8303128648be9beb7a163e0b260880043`, 문서 submodule HEAD는 `9800330c647b5202693209acd891da872fcf0a6e`다. 시작 시 README·등록·Wrench EnvCfg/PPO·기존 테스트/probe와 문서 인계·Wrench-v1/v2 설명에 미커밋 변경이 있었다. `.aws` 삭제와 `docs/plan/PLAN11.md`도 기존 상태이며 건드리지 않았다. 변경 기준은 HEAD만이 아니라 작업 시작 시 실제 파일이다. 기존 Python 내용을 `/tmp/wrench_v0_1_before.json`으로 보관해 정의를 대조했다. commit/reset/submodule checkout은 수행하지 않았다.

## 구현과 변경 전후

| 위치 | 변경 | 의도·영향 |
| --- | --- | --- |
| `envs/wrench_envs.py` | `WrenchV0_1EnvCfg(WrenchEnvCfg)` 추가 | v0 직접 상속, 전용 Reward/Curriculum·목표 생성 override |
| `mdp/rewards/wrench.py` | 독립 contact None, distance 전용 stateful term | 활성14개, weight3.7·scale0.05 유지 |
| `mdp/reward_functions/wrench.py` | `WrenchV0_1GoalDistance` 추가 | target/hand 합력≥0.01N의 연속2표본, cosine×부모 proximity, 기존 현재 높이 gate |
| 같은 함수 후속 | 거리<0.03m이면 alpha=1 | 목표 근처 각도 불안정 완화, 경계는 strict이며 접촉·높이는 계속 필요 |
| `mdp/curricula/wrench.py` | v0_1에서 방향 term None | population·target speed 일정 유지 |
| `mdp/event_functions/wrench.py` | 초기화에 stages/min_goal_distance 선택 인자 | 부모 기본9단계/5cm 유지, 자식4단계/2.5cm 사용 |
| `mdp/common/revision_layout.py` | 최소 ray 길이를 기본0.05의 선택 인자로 전환 | 자식 하한0.025 허용, 기존 호출 출력 유지 |
| `agent/wrench_ppo_cfg.py`, 패키지 등록 | v0 runner 직접 상속, Gym 등록 추가 | 실험명 `inspire_wrench_v0_1`, ID `Inspire-Wrench-v0_1` |
| 테스트·probe | 경계/이력/설정/단계 검사, probe에 v0_1 추가 | 기존 테스트의 v0 독립성 검사에서 신규 파생 클래스만 제외 |

목표 상한은 `object_spawn.params.goal_distance`0.15→0.075m이다. 초기화 시 이 값을 bank 생성에 전달한다. 새 bank는 `(40,3,3)`, `(40,3,4)`, `(40,4,4)`, `(40,4,5)`를 모두 준비하므로 population 전환 시 재검색이나 미등록 단계 오류가 없다. 거리 분포를 균등 샘플로 변경하지 않았다.

원본 contact 보상에는 높이 조건이 결합되어 있지만 요청한 접촉 유지 트리거는 force 조건으로 정의했다. 현재 높이 제한은 부모 distance 함수에서 유지하며 이전 높이를 추가 gate로 사용하지 않는다. Signed cosine을 clamp-to-positive하지 않는다. 부모 proximity는 거리 감소량이 아니므로 감소량 보상이나 전진 판정은 추가하지 않았다. 사용자에게 이 해석을 작업 중 안내했다.

초기 구현은 영벡터 cosine을0으로 처리했으나 사용자 후속 지시로 현재 거리3cm 미만은1로 변경했다. 최종 구현에서 정확히 목표점도1이며, 정확히3cm는 원래 코사인이다.

## 최종 전체 대조

- 기존 EnvCfg·Reward/Curriculum Cfg·runtime·Scene·Command·Observation·Action·Termination·PPO 클래스 및 기존 reward 함수는 작업 전 AST와 동일하다. 기존 함수에서 달라진 것은 선택 인자를 추가한 `initialize_wrench_layouts`와 `sample_revision_commands`뿐이다.
- 실제 configclass를 실행하고 자식의 요청된5개 설정 차이(두 보상, 한 커리큘럼, 두 이벤트 params)를 부모 값으로 되돌린 뒤 전체 ordered config가 동일함을 확인했다. Scene 자산/일부 Sim leaf는 CPU 대역이며 실제 GPU 객체 검증은 아니다. 새 인스턴스의 부모 값도 동일하다.
- v1/v2 제어·보상과 등록 회귀가 통과했다. 등록의 runtime은 v0와 같고 EnvCfg/PPO entry point만 새 파생을 가리킨다. PPO는 실험명만 다르다.
- 부모 목표 sampler는 snapshot을 AST로 실행해 seed0/17/42, 각도0/5/10/15/20/25/30°, 상한0.05/0.075/0.15m의63개 조건×256샘플에서 출력 텐서가 정확히 동일했다.
- 활성 reward15→14, contact 로그 제거·distance 이름 유지, deadzone curriculum/log 제거, 나머지 term 순서·callable·params·weight·일정 유지. 상세 최종 수식과 값은 환경 계약에 기록했다.
- 학습 실행 및 `logs/rsl_rl` 수정·정리는 하지 않았다.

## 실행한 검증

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q \
  src/inspire_sweep_baseline/tests/test_wrench_v0_1.py \
  src/inspire_sweep_baseline/tests/test_wrench.py \
  src/inspire_sweep_baseline/tests/test_wrench_v1.py \
  src/inspire_sweep_baseline/tests/test_revision_layout.py \
  src/inspire_sweep_baseline/tests/test_revision_v2.py
```

최종 **76 passed / 6.55s**. 접촉 threshold 바로 아래/같음/위, force cancellation·NaN/Inf·stale, 최초 표본·단절/재접촉·중복 조회·부분/전체 reset·누락 step, 양/직각/음 cosine, 거리 감소 시 보상 증가, 거리0, strict3cm 아래/같음/위, 기존 높이 경계, 생성 단계와 population 전환, 부모 회귀를 검사했다.

초기 실행은 pytest가 ROS의 `launch_testing` 플러그인을 자동 로드하다 `lark` 부재로 시작하지 못했다. 환경 설치는 변경하지 않고 plugin autoload를 끈 위 명령으로 실행했다. 첫 테스트에서 새 fixture의 `object_link_state_w`, population capacity 필드 누락을 수정했다. 이후73개 통과했고 사용자 후속3cm 경계 검사3개를 추가한 최종76개가 통과했다.

`env_isaaclab`의 PyTorch2.7.0+cu126에서 `torch.cuda.is_available()`가False였다. 실제 GPU 초기화·64/2048 rollout·PPO 학습·물리 접촉 지속성과 학습 성능은 미검증이다. `_wrench_probe.py --version v0_1`은 다음 GPU 호스트를 위한 실행기 확장이며 실행 성공으로 보고하지 않는다. 실제 학습은 환경 계약의 `scripts/train.py` 명령을 사용한다.

최종 정적 검사: 변경/신규 Python12개 compile 성공, workspace와 문서 submodule의 `git diff --check` 통과, 변경 Markdown6개 수식 검사 통과. 링크 검사268개 중 기존 README의 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1개를 확인했다. 해당 링크는 이번 추가와 무관한 기존 본문이며 변경하지 않았다. 새 환경·로그·색인 링크에서는 오류가 없었다. Markdown 실제 렌더링은 확인하지 않았다.


## 2026-11-04 후속: 시작 목표 거리 하한4cm

사용자는 초기 목표 허용 거리2.5cm가 성공 반경3cm 안에 들어갈 수 있음을 지적하고4.0–7.5cm를 요청했다. 기존 v0_1에 직접 적용했다. 이번 기준 코드 HEAD는 `c313625fedd3e82263f60e95e5812a4fc026100f`, 문서 HEAD는 `880d11912061dfa9f9b51a9cb58f7b828534e85c`이며 중간 사용자 변경을 유지했다.

`WrenchV0_1EnvCfg.events.layout_bank.params.min_goal_distance`를0.025→0.04m로 변경했다. 상한0.075m,40° 방향,3cm 미만 alpha=1 보상,접촉 조건,부모 v0와 모든 다른 설정은 유지한다. 생성 코드는 이 하한을 startup bank 후보의 유효성 판정에 사용한다. 기존 ray 선택 방식은 유지하며 균등 거리 샘플러로 바꾸지 않는다. 실행 코드 diff는 이 수치1곳뿐임을 확인했다. runtime·Scene·Command·Event callable·관측·Action·Reward·Termination·Curriculum·PPO·등록·로그 키에는 차이가 없다.

기존 검사에4cm/7.5cm 경계와4cm 미만 상한 거부, 모든 population 단계에서 초기 거리>3cm 확인을 반영했다. 위와 같은5개 테스트 파일 명령으로 **78 passed / 6.65s**. 현재 테스트에는 중간 사용자 변경으로 추가된 검사도 포함되어 이전76개와 총수가 다르다. 전체 설정 대조로 부모 보존도 확인했다. 문서·README의 현행 범위를 갱신했으며 앞선2.5cm 구현 설명은 변경 이력으로 남긴다.

새 범위는 환경 재생성 시 startup bank에 적용된다. 이미 실행 중인 프로세스의 bank는 재생성되지 않으므로 재시작이 필요하다. 실제 GPU rollout·학습은 이번에도 실행하지 않았고 `logs/rsl_rl`은 건드리지 않았다.

정적 검증: 변경 Markdown6개 수식 검사와 두 저장소 diff 공백 검사를 통과했다. 링크268개 검사에서는 이전에 기록한 README의 기존 누락 링크1개만 동일하게 남아 있으며 신규 링크 오류는 없다.
