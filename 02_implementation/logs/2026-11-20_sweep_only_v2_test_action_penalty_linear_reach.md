# Sweep Only v2 Test ActionPenalty의 LinearReach 직접 파생 환경

## 요청과 작업 기준

사용자는 `inspire_sweep_only_v2_test_action_penalty`를 상속하는 환경에서 Reach를 앞서 제안한 선형식으로 변경하도록 요청했고 GPU smoke도 허용했다. 합의된 값은 **weight0.8·최대 보상 반경0.10m·선형 감소 폭0.35m**, 보상이0이 되는 거리0.45m다. 앞선 문서의 시간 간격 생략은 수식 표기 규칙이며 RewardManager의 실행 시간 간격 처리를 바꾸라는 지시가 아니다.

새 ID는 `Inspire-Sweep-Only-v2-Test-ActionPenalty-LinearReach`, 로그 이름은 `inspire_sweep_only_v2_test_action_penalty_linear_reach`로 정했다. 부모 Gym ID는 `Inspire-Sweep-Only-v2-Test-ActionPenalty`다. 임의로 기존 v2 환경을 수정하거나 v1 계열을 부모로 선택하지 않았다.

기준 workspace HEAD는 `dd68f9d3e79ee447dcbdab2183a2b32f6ff7fb46`, 문서 submodule HEAD는 `5074b42a1db5861a4f76d8ebeced425d242e9800`이다. 시작 시 workspace에는 문서 submodule 변경만 있었고, 문서 저장소에는 이전 요청으로 작성한 v1-Test 보상 상세 문서·작성 로그·계열 안내 링크 변경이 있었다. 이 작업들은 보존했다. 환경 소스에는 작업 시작 시 미커밋 변경이 없었다.

## 변경과 의도

`SweepOnlyV2TestActionPenaltyLinearReachEnvCfg`는 `SweepOnlyV2TestActionPenaltyEnvCfg`를 **직접 상속**하고 `super().__post_init__()` 후 Reach term 하나를 교체한다. `SweepOnlyV2TestActionPenaltyLinearReachPPORunnerCfg`도 부모 runner를 직접 상속하며 experiment name만 변경한다. Runtime은 기존 `SweepOnlyEnv`다.

현재 EEF–실제 타겟 bounds 중심의 3D 거리를 $\rho_t$라 하면, 시간 간격을 생략한 식은 다음과 같다.

```math
r_{\mathrm{reach},t}=0.8\max\left(
1-\frac{\max(\rho_t-0.10,0)}{0.35},0\right).
```

새 `linear_reach` 함수는 reset 이력 없이 현재 타겟 중심을 읽고0–1의 근접도를 반환한다. 초기 거리·episode 길이 배율을 제거한다. 근접 반경은 유한한0 이상, 감소 폭은 유한한 양수만 허용한다. 함수는 시간 간격으로 나누지 않으며 RewardManager가 기존처럼 policy 시간 간격0.02초를 한 번 곱하므로 실제 최대 step 기여는0.016이다.

| 항목 | 부모 | 자식 | 의도 |
| --- | --- | --- | --- |
| EnvCfg 직접 부모 | v2-Test 기반 ActionPenalty | v2-Test-ActionPenalty | 요청 부모의 구성을 누적 상속 |
| `reaching.func` | `InverseDistanceReach` | `linear_reach` | 현재 거리의 선형 근접도 |
| `reaching.weight` | 30 | 0.8 | 제안한 최대 보상 크기 |
| `near_radius` | 0.10 | 0.10 | 근접 plateau 보존 |
| 거리 모양 파라미터 | `distance_scale=0.10` | `decay_distance=0.35` | 역거리에서 선형 감소로 변경 |
| 초기 거리·episode 길이 배율 | 사용 | 사용하지 않음 | 현재 거리에 동일한 보상 |
| `frame_name` | `ee_frame` | 동일 | EEF 기준점 보존 |
| PPO | 부모 구성 | experiment name만 다름 | 신규 학습 로그 구분 |
| Runtime·Scene·관측·Action·Command·Event·reset·Termination·Curriculum | 부모 구성 | 동일 | 요청 밖의 구성 보존 |
| Sweep·Deadzone·기존 페널티 | 50/−10·count/20·0°·ActionPenalty | 동일 | Reach 외의 학습 조건 보존 |

## 변경 위치

- `mdp/reward_functions/stabilize_sweep.py`: stateless `linear_reach` 함수만 추가.
- `envs/stabilize_sweep_envs.py`: 직접 자식 EnvCfg 추가, Reach term만 교체.
- `agent/stabilize_sweep_ppo_cfg.py`: 직접 자식 runner와 별도 experiment name 추가.
- 패키지 `__init__.py`: 새 ID 등록 하나 추가.
- `tests/test_sweep_only_action_penalty.py`: 회전된 bounds 중심·거리 경계·현재 위치 갱신·초기 배율 독립성과 잘못된 파라미터 검사 추가.
- `scripts/check_sweep_only_linear_reach.py`: 실제 전체 설정 대조와 GPU reset·curve probe·step·부분 reset 실행기 추가.
- 패키지 README·계열 안내·활성 환경 안내·현재 인계: 새 계약과 실행 명령 연결.

## CPU와 기존 코드 보존 검증

workspace 루트에서 실행했다.

```bash
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_only_action_penalty.py -q

CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest \
  src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q
```

결과는 각각 **13 passed / 1.51초**, **95 passed / 6.99초**, 합계108개 통과다. 새 테스트는 EEF가 물체 원점이 아니라 회전된 bounds 중심에서 떨어진 거리를 사용하게 하고, 물체가 움직일 때 즉시 값이 바뀌는지 확인한다. 10cm 바로 위·45cm 바로 아래와 두 경계, 근접·원거리, 초기 거리와 episode 길이가 불필요한 점도 검사했다.

HEAD 대비 AST 비교에서 수정된 production 파일3개에 원래 있던 모든 최상위 함수·클래스의 AST가 동일했다. Gym 등록 파일도 기존 모든 최상위 문장이 그대로이고 마지막에 새 등록 하나만 추가됐음을 확인했다. 기존 함수·클래스·등록의 동작 변경은 없다.

## 실제 GPU smoke와 전체 설정 대조

시작 시 RTX3090의 GPU 메모리 사용은825MiB, 실행 중인 compute process는 없었다. 다음 명령으로 seed42·4환경·8step을 실행했다. 별도 학습은 시작하지 않았다.

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u \
  src/inspire_sweep_baseline/scripts/check_sweep_only_linear_reach.py --headless
```

최종 결과는 **cuda:0·RTX3090에서 통과**다.

1. 실제 registry에서 부모·자식 EnvCfg를 import하고 `to_dict()` 전체를 비교했다. Reach term을 부모 값으로 복원한 비교 dict는 부모 전체 dict와 동일했다. 부모 인스턴스와 새로 만든 부모의 dict도 작업 전 값과 동일했다.
2. PPO 전체 dict는 experiment name만 달랐고 wrapper `clip_actions=None`, 네트워크·분포·학습률·horizon·algorithm은 같았다. EnvCfg·runner의 직접 부모 및 같은 runtime 등록도 확인했다.
3. 실제 타겟 pose·bounds를 재사용하고 EEF만 가상 위치로 둔 GPU probe에서 거리5/10/15/20/30/35/45/60cm의 raw 근접도1/1/6÷7/5÷7/3÷7/2÷7/0/0을 확인했다. 시뮬레이터의 pose buffer를 변경하지 않았다.
4. 실제 physics rollout은 팔 행동0·손 상한의0.1배를 사용했다. 8step 동안 조기 종료 없이 관측66D+64D·보상 유한성·원본 Action 이력을 확인했다. 매 step `reaching`의 가중값이 새 함수값×0.8이고 전체 반환 보상은 manager 가중값 합×policy 시간 간격임을 확인했다.
5. 0번 환경의 부분 reset에서 1번 환경의 물체 상태와 원본 Action이 유지되고 선택된 Action은0으로 초기화됐다. 새 Reach는 reset 이력 없이 유한하며 부분 reset 뒤 추가1step도 통과했다.

이번4환경의 reset 시 EEF–타겟 중심 거리는 약0.33473/0.32965/0.34235/0.35589m, EEF–타겟 원점 거리는0.35100/0.35004/0.36299/0.37559m였다. 이 표본에서 기존 Reach 최대 가중값은 약0.750–0.827이며 새 최대값0.8과 비슷하다. 이는 seed42의4개 환경 관측이며 전체 초기 거리 분포의 통계나 장기 성능을 뜻하지 않는다.

최초 GPU 검사는 `to_dict()`가 callable을 문자열로 직렬화하는 것을 함수 객체로 비교해 assertion에 걸렸다. `SimulationApp.close()`가 종료하며 최초 traceback 출력도 가려져, 검사기에 정리 전 명시적 traceback 출력을 추가했다. 함수 identity는 실제 config 객체에서 확인하도록 검사만 수정한 뒤 전체 GPU 검사를 재실행해 통과했다. 이 문제로 production 환경 코드를 변경하지 않았다. 종료 코드만으로 성공을 판단하지 않고 결과 JSON의 `status=passed`와 각 검증 결과를 확인했다.

결과는 [smoke JSON](../../../../outputs/sweep_only_linear_reach/smoke.json)에 저장했다. stdout은 `/tmp/check_sweep_only_linear_reach.log`이며 임시 경로다. 실행기 자체는 같은 검사를 재현할 수 있도록 scripts에 남겼다.

## 문서·최종 대조와 미검증 범위

새 환경 구성은 [계열 안내](../environments/SWEEP_ONLY_FAMILY.md#linearreach-파생-환경)에 모았다. 새 함수·EnvCfg·runner·등록·테스트·실행기 외의 소스 변경은 없으며 문서의 기존 사용자 작업을 보존했다.

최종 Markdown 수식 검사는 문서4개와 패키지 README를 합친5파일이 통과했다. 문서4개의 링크는 내부344개·외부7개 오류0이다. README까지 포함한5파일 전체 링크 검사에서는 내부490개·외부35개 중 기존 누락 링크1개가 검출됐다. 대상은 README의 과거 v0_2 설명이 가리키는 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md`로, HEAD의 README1538행에 이미 같은 링크가 있고 이번 삽입으로1540행이 됐음을 확인했다. 해당 역사 링크는 요청 범위 밖이므로 보존했으며 신규 LinearReach 링크에는 오류가 없다. Workspace와 문서 저장소의 `git diff --check`는 모두 통과했다.

장기 PPO 학습·성공률·2048환경 성능·학습된 checkpoint의 행동은 미검증이다. 기존 부모의 physics rollout을 별도 실행한 비교 실험은 아니며 부모 보존은 전체 설정 대조와 기존 코드 AST·CPU 회귀로 확인했다. `logs/rsl_rl`·기존 학습 로그·checkpoint·원격 실행 상태는 변경하지 않았다.
