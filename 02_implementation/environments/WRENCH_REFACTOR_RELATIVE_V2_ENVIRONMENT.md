# Inspire-Wrench-Refactor-Relative-v2

2026-11-07 공통 변경: Relative-v0의 F/T 최종 관측 한도(힘 각 축±150N·모멘트 각 축±8N·m)와 raw Action Rate 그룹별 제곱합 cap100을 상속한다. policy와 critic 모두 보정·좌표변환·noise 이후 제한하며 질량·관성 보정 및 보상/진단용 wrench는 보존한다. [구현·검증](../logs/2026-11-07_relative_observation_action_limits.md).

2026-11-06. Relative-v0를 직접 상속하여 **Critic의 초기 타겟 위치를 현재 타겟 위치로 변경**한다. Actor는 v0의 초기 타겟 위치를 유지한다. 두 위치 모두 현재 EEF 기준 XYZ다. v1을 상속하지 않으므로 장애물도 v0의 EEF 기준 초기 관측을 유지한다.

## 등록과 관측

| 항목 | 설정 |
| --- | --- |
| Gym ID | `Inspire-Wrench-Refactor-Relative-v2` |
| EnvCfg | `WrenchRefactorRelativeV2EnvCfg(WrenchRefactorRelativeEnvCfg)` |
| runtime | `runtime.wrench_refactor:WrenchRefactorEnv` |
| PPO | `WrenchRefactorRelativeV2PPORunnerCfg` |
| experiment_name | `inspire_wrench_refactor_relative_v2` |
| Actor | `policy` 58D + `obstacles` 64D |
| Critic | `critic` 58D + 같은 `obstacles` 64D |
| Rollout Storage | `policy`, `critic`, `obstacles`를 각각 저장 |

58D 직접 관측의 구성·순서는 v0와 같다: arm position 6, arm velocity 6, hand position 2, base 기준 EEF pose 7, 타겟 XYZ 3, EEF 기준 goal XYZ 3, action 8, paired tactile 17, wrist wrench 6. 타겟은 인덱스 `[21:24]`다.

Critic 타겟만 `CurrentObjectPositionInEEF`로 바뀐다. 선택된 target ID의 현재 world 위치를 읽어 현재 EEF 기준으로 표현한다. Actor는 `InitialObjectPositionInEEF`로 reset 후 저장한 초기 위치를 현재 EEF 기준으로 표현한다. 물체만 움직이면 Critic 위치만 변하고, EEF가 움직이거나 회전하면 두 상대 좌표 모두 변한다.

타겟의 base 기준 ±0.01 m 균일 bias를 reset 때 뽑아 유지하는 규칙은 보존한다. Critic 함수는 초기 관측에 초기→현재 변위를 EEF 좌표로 더하여 초기 위치만 현재 위치로 치환한다. 두 직접 관측 그룹은 동일한 corruption 설정을 따르며, 각 그룹의 타겟 bias·촉각·F/T 노이즈 표본은 독립적으로 생성된다. 나머지 관측의 물리량·좌표계·노이즈 분포는 동일하다.

장애물은 동일한 EEF 기준 초기 snapshot 64D를 공유한다. 가시성 선정·확률 변조·mask·순서는 v0 그대로다. 각 네트워크의 독립 encoder는 64→32→16, 본체 입력은 58+16=74D다. Actor export 입력은 기존과 같은 122D다. 별도 GT 장애물 관측은 없다.

## 보존 범위와 실행

[Relative-v0 계약](WRENCH_REFACTOR_RELATIVE_V0_ENVIRONMENT.md)의 scene, 물체 생성·스폰 타이밍, reset, 목표 생성, EEF OSC, hand actuator, action rate, reward, termination, curriculum 및 PPO 수치를 그대로 상속한다. `target_goal_first_entry_bonus`도 10이다. Reward 계산의 GT 사용 방식은 바뀌지 않는다.

학습 진입점은 `src/inspire_sweep_baseline/scripts/train.py`이며 `--task Inspire-Wrench-Refactor-Relative-v2`로 선택한다. 최종 역할은 사용자 확인에 따라 Actor=초기, Critic=현재로 정했다. GPU 스모크를 허용한 이번 변경에서는 실제 관측과 EEF 변환값, 부분 reset 및 스폰 높이까지 검사했다. [최종 개발 로그](../logs/2026-11-06_relative_family_280g_v3.md). 이전 Actor=현재/Critic=초기 버전의 checkpoint는 텐서 차원이 같아도 관측 의미가 다르다.

## 공통 조인트 설정 갱신

v0를 상속하므로6관절 물리 속도 한도는3.14rad/s, effort는150/150/150/28/28/28Nm이다. 속도 종료 임계값은10,000까지4.0rad/s,10,250부터250iteration마다0.05 감소해20,000부터2.0을 유지한다. 관측 분리 등 v2 고유 동작은 그대로다. Axia 질량0.280kg을 v0에서 상속한다. 진단 출력과 종료 제거는 적용하지 않는다.
