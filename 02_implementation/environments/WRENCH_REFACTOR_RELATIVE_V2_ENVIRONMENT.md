# Inspire-Wrench-Refactor-Relative-v2

2026-11-07 파생 **Relative-v2_1** 추가: v2를 직접 상속하여 거리 항만 시작→목표와 시작→현재의 누적 변위 cosine으로 바꾼다. 아래 v2_1 절과 [개발 기록](../logs/2026-11-07_relative_v2_1.md)을 따른다. 기존 v2는 수정하지 않는다.

2026-11-07 후속: Relative-v0의 실시간 이동 cosine(기준점은 XY 이동1mm 이상일 때 갱신)과 `target_inverse_distance`(실제 step 페널티 `−12.97×max(d_t−d_(t−1), 0)`)를 그대로 상속한다. v2의 최초 진입·유지·성공 보상 및 성공 종료는 유지한다. [변경·검증](../logs/2026-11-07_relative_motion_rewards.md).

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

## Relative-v2_1: 시작점 기준 누적 변위 cosine

Gym ID는 `Inspire-Wrench-Refactor-Relative-v2_1`, EnvCfg는 `WrenchRefactorRelativeV2_1EnvCfg(WrenchRefactorRelativeV2EnvCfg)`다. runtime은 동일한 `WrenchRefactorEnv`다. PPO는 `WrenchRefactorRelativeV2_1PPORunnerCfg`가 v2 runner를 직접 상속하며 experiment_name만 `inspire_wrench_refactor_relative_v2_1`로 구분한다.

환경의 유일한 차이는 `target_goal_distance`다. 함수는 `displacement_cosine_goal_distance`, params는 `distance_scale=0.05`, weight는 기존5를 유지한다. 실제 초기 GT 위치를 `p0`, 현재 물체 위치를 `p`, 목표를 `g`라 하면 XY에서 다음과 같다.

```math
c=\cos(\mathbf{g}-\mathbf{p}_0,\mathbf{p}-\mathbf{p}_0),\qquad
r=5\,dt\,e^{-\|\mathbf{g}-\mathbf{p}\|/0.05}cH.
```

H는 기존 EEF 높이 gate다. 목표→현재와 목표→시작을 비교하는 식이 아니다. 시작점은 episode reset에서 저장한 실제 타겟 위치로 고정하며1mm 이동 기준점은 사용하지 않는다. 두 벡터 길이1e−8m 이하이거나 비유한 보상이면0이다. 초기 정지에서0, 초기 목표 방향 직진은+1, 수직 누적 이동은0, 처음부터 반대 방향 이동은−1이다. 목표를 지나도 누적 방향이 같으면+1이며, 목표에 정확히 도달해도 비영 초기→목표 벡터가 같으므로+1이다.

`target_inverse_distance`는 v2의 직전step 거리 증가 비용 `−12.97×max(d_t−d_(t−1),0)`을 그대로 상속한다. 접촉 유지·최초 진입+10·Hold·성공+75와 성공 종료도 유지한다. v3의 성공 항 제거는 적용하지 않는다. 관측은 Actor 초기 타겟 / Critic 현재 타겟, 기타 scene·reset·F/T 보정/clip·raw Action Rate cap·OSC·curriculum·PPO 수치 모두 v2와 동일하다.

목적은 매step 이동 방향 변화에 대한 민감도를 줄이고 이탈 페널티와 함께 잘못된 방향의 밀기를 억제하는 비교 실험이다. 시작점에서의 미소 변위는 여전히 정규화되며, 목표 쪽에서 후퇴하거나 목표를 지나친 경우 cosine이 양수일 수 있다. 역방향 행동 방지와 장기 학습 개선은 구현만으로 보장하지 않는다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-v2_1 --num_envs 2048 --headless
```

## 방향별 Test 평가

2026-11-08: 해당 부모를 직접 상속하는 Right/Pull/Left/Push 환경을 추가했다(v2 계열은 v2_1 기준). [목표 구간·부모 대조·녹화 명령·검증 범위](../logs/2026-11-08_relative_direction_tests.md).

## Relative-v2_2: Contact 유지 보상 제거

2026-11-08: `WrenchRefactorRelativeV2_2EnvCfg`는 v2_1을 직접 상속하고 부모 초기화 후 `self.rewards.target_contact = None`만 설정한다. 거리 보상·Hold·최초 진입·성공·종료·관측·제어·커리큘럼은 v2_1 그대로다.

Gym ID는 `Inspire-Wrench-Refactor-Relative-v2_2`, runtime은 동일한 `WrenchRefactorEnv`다. `WrenchRefactorRelativeV2_2PPORunnerCfg`도 v2_1 runner를 직접 상속하며 experiment_name만 `inspire_wrench_refactor_relative_v2_2`로 구분한다. GPU 스모크는 사용자 요청으로 생략했다. [개발·검증 기록](../logs/2026-11-08_relative_v2_2.md).
