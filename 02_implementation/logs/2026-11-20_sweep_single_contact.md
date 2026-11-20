# Sweep Single Contact v0 구현과 검증

**후속 정정이 최종 기준이다:** 아래 초기 구현의0/20 카운트 표현은 제거했다. 현재 Single Contact는 `contact_recognized: bool`만 가지며 `contact_count` 필드가 없다. 보상에는 boolean의 float 변환1/0만 사용한다. 초기 구현·검증은 경위를 보존한 기록이고 마지막 정정 절이 현재 동작이다.

## 요청·기준

사용자는 `Inspire-Sweep-v0`에서 접촉 카운트 누적을 없앤 새 환경 `Inspire-Sweep-Single-Contact-v0`를 요청했다. 최근3스텝 중2개 접촉이 인정되면 접촉 계수1, 아니면0이며 기존 카운트 표현으로는20/0만 존재한다.

시작 workspace HEAD는 `4ebd90a`, 문서 저장소 HEAD는 `a50c603`이다. 양쪽 작업트리는 깨끗했다. 이전 사용자 직접 푸시 이후의 상태를 보존하며 이번에는 commit·push·학습을 수행하지 않았다.

## 구현과 의도

| 항목 | 부모 Sweep v0 | Single Contact |
| --- | --- | --- |
| ID | `Inspire-Sweep-v0` | `Inspire-Sweep-Single-Contact-v0` |
| EnvCfg | `SweepEnvCfg` | 직접 자식 `SweepSingleContactEnvCfg`, 전체 설정 동일 |
| Runtime | `SweepEnv` | 직접 자식 `SweepSingleContactEnv` |
| 내부 state | `SweepOnlyState` | 직접 자식 `SingleContactSweepState` |
| 접촉 이력 | 최근3 policy step 중2회 | 동일 |
| 카운트 | 인정+1, 미인정-2, 범위0–20 | 인정20, 미인정0 |
| 보상용 접촉 계수 | 인정 시 count/20 | 인정 시 즉시1 |
| PPO | `SweepPPORunnerCfg` | 직접 자식, experiment name만 변경 |
| 로그 | `inspire_sweep_v0` | `inspire_sweep_single_contact_v0` |

`StabilizeState.finish()`의 카운트 갱신·접촉 계수 산출 부분만 `_contact_factor()` hook으로 추출했다. 부모의 식과 연산 순서는 그대로이며, 새 state만 이 hook을 override한다. 거리·접촉 이력·높이·힘 정렬·수평 힘1N·현재 접촉·역방향·거리 갱신 계산을 복제하지 않았다.

새 hook은 `contact_count=20*recognized`, 반환값은 `recognized.float()`다. 설정의 정규화 flag와 관계없이 새 보상 계수가20이 되는 일은 없다. reset에서는 기존 이력과 카운트를0으로 지우고 다음2회 접촉으로 즉시 재인정한다. 부분 reset은 다른 행의 이력을 유지한다.

변경 위치는 기존 `envs/sweep_v0_envs.py`, `runtime/sweep_v0.py`, `agent/sweep_v0_ppo_cfg.py`, `__init__.py`와 공통 state hook, 새 `mdp/common/sweep_v0_state.py`다. 의미·수식·제어 스텝·남는 힘 조건은 [환경 계약](../environments/SWEEP_V0.md#single-contact-파생-환경)에 정리했다.

## 전체 대조·CPU 검증

`tests/test_sweep_single_contact.py`에서8개 이력 조합과 초기 카운트0/1/10/19/20을 실제 finish에 제공해 카운트가20/0이고 양의 보상이 이진 계수를 사용하는지 검사했다. 연속 인정·미인정·재접촉, 부모의 누적 증가 유지, 유효 데이터·높이 경계·수평 힘·현재 접촉·역방향 보존, 부분 reset을 검사했다.

```bash
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact.py \
  src/inspire_sweep_baseline/tests/test_sweep_v0.py \
  src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q
```

결과는 **110 passed / 7.40초**다. 새7개, Sweep v0의8개, 기존 Stabilize/Sweep95개를 통과했다. 기존 state의 접촉 카운트·정규화/비정규화·Gate·Sweep 계산의 회귀 검사를 포함한다.

## GPU smoke

기존 GPU smoke 실행기에 `--single-contact` 선택만 추가하여 부모와 같은 전체 검증을 재사용한다.

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u \
  src/inspire_sweep_baseline/scripts/check_sweep_v0.py --single-contact --headless
```

RTX3090·cuda:0·seed42·4환경에서 **reset·8step·부분reset·추가1step 통과**다. [결과 JSON](../../../../outputs/sweep_single_contact/smoke.json)의 `status=passed`를 확인했다. 임시 stdout은 `/tmp/check_sweep_single_contact.log`다.

- 실제 registry에서 EnvCfg의 직접 부모와 전체 `to_dict()`가 Sweep v0와 동일함을 확인했다. 기능 기준 v2 LinearReach와의 기존 전체 설정 대조도 수행했다.
- 실제 runtime state가 `SingleContactSweepState`인지 확인했다. GPU의 별도 state probe에 이력4개를 넣어 카운트[0,20,20,20]과 양의 거리 원점수[0,.01,.01,0]을 확인했다. 마지막 행은 과거2회 인정이지만 현재 무접촉이므로0이다.
- live physics8step의 state 카운트가0 또는20인 것을 확인했다. 관측66D+64D, F/T [-1,1], 보상 유한성, 가중 보상 합과 dt, 기존15개 보상·빈 커리큘럼을 유지했다.
- 관측 전용 F/T scale과 페널티 이력의 물리값 보존 검사를 재사용하여 통과했다. 별도 force impulse를 물리 장면에 가한 검증은 아니다.
- PPO는 직접 부모와 같은 값이고 새 experiment name만 다르다. 부모 환경 설정의 인스턴스·새 인스턴스도 변하지 않았다.

## 영향·미검증·후속

학습·장기 성공률·접촉 유지 행동 개선을 측정하지 않았다. GPU의 이력4개 probe는 수학적 state 검사이고 짧은 live rollout은 장기 접촉 동작의 성능 검증이 아니다. 기존 Sweep v0 및 다른 부모 환경은 누적 contact count 방식을 유지한다. 원본 로그·다른 서브모듈·사용자 작업은 수정하지 않았다.

문서 수식·링크·소스 구문·diff 검사와 최종 보존 대조 결과는 아래에 기록한다.

최종 검사: 기존 EnvCfg·PPO·runtime 클래스와 등록 AST가 그대로이고 새 클래스/등록만 추가된 것을 확인했다. 공통 finish에서 접촉 계수 블록 외의 AST는 동일하며, 추출한 기본 hook의 연산식은 기존 블록과 동일하다. 변경·추가 Python8개를 컴파일했다. 변경 문서4개 수식 및 외부 링크 포함 검사 오류0, 문서 전체 링크 검사 오류0, 양쪽 저장소 `git diff --check` 통과다. README의 신규 상대 링크는 위 계약의 실제 anchor를 가리킨다. 시각 렌더링은 수행하지 않았다.

## 사용자 후속 정정: Contact Count 자체 제거

사용자는0/20이 기존 구조를 설명하기 위한 비유였으며 실제 요구는 Contact Count 대신 접촉 여부라고 명확히 했다. 초기 구현은 보상 계수는1/0이었으나 진단용 `contact_count`에0/20을 남긴 점이 요구 의도와 달랐다.

새 state에서 `contact_count`를 완전히 제거하고 `contact_recognized` boolean을 저장한다. 기본 state의 접촉 상태 초기화·reset을 작은 hook으로 분리하여 자식에는 카운터를 할당하지 않는다. 자식 reset은 boolean을False로 만들고, finish에서는 최근3개 접촉 중2개 인정 및 기존 높이 조건의 결과를 저장한다. 반환 계수만 boolean을float로 변환한다. 부모 기본 hook은 기존 long 카운터의 생성·reset·누적 동작을 그대로 수행한다.

검사도0/20 표현에 의존하지 않도록 변경했다. 모든 이력 조합·기존 boolean 상태True/False에서 결과를 검증하고 자식에 `contact_count`가 존재하지 않음을 명시적으로 검사한다. CPU110개 재검사를6.90초에 통과했다. GPU 검사도 boolean dtype·카운터 필드 부재·접촉 이력 probe·reset 경로를 검사하도록 변경했다. GPU·문서 최종 결과는 이어서 기록한다.

정정 후 GPU 재검증도 통과했다(cuda:0,4환경,8step,부분reset·추가step). 결과 JSON의 probe는 boolean recognition 및 contact_count 부재를 명시한다. 관련 Python4개 컴파일, 변경 문서4개 수식·외부 링크 포함 검사(오류0), 양쪽 저장소 diff 공백 검사를 통과했다. 최종 보상 수치는 초기 이진 계수 구현과 같지만 내부 상태는 카운터 표현 없이 접촉 여부만 가진다.
