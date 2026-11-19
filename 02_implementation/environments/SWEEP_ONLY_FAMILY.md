# Inspire-Sweep-Only 계열: 환경 구성·버전 차이·학습 현황

2026-11-19 기준. 환경 구성은 현재 코드에서 확인한 내용이며, 서버별 성공률과 학습 계획은 같은 날 사용자가 전달한 관찰이다. 원격 서버의 로그를 새로 읽거나 학습을 시작한 기록은 아니다. 세부 물리·센서·초기화 구현은 [Sweep Only 상세 설명](SWEEP_ONLY.md)을 참고한다.

## 현재 학습 현황과 다음 실험

| 로그 experiment name | 서버 표기 | 사용자 관찰 | 결정·계획 |
| --- | --- | --- | --- |
| `inspire_sweep_only_v0_test` | `.250` | 학습했으나 성공률이 10%를 넘지 못함 | 보상 계수를 조정한 v1을 추가 |
| `inspire_sweep_only_v1_test` | `.30` | 학습 중이며 성공률이 약 20%까지 상승 | 학습 지속 예정 |
| `inspire_sweep_only_v2_test` | `.180` | 학습했으나 성공률 상승이 관찰되지 않음 | Deadzone 제거 실험을 잠시 보류 |
| `inspire_sweep_only_v1_2_test` | `.180` | 이번 보고에서는 아직 학습 예정 | Deadzone 30°를 유지하고 강화한 보상으로 학습 예정 |
| `inspire_sweep_only_v2_2_test` | 미지정 | 구현된 비교 환경; 학습 결과 보고 없음 | Deadzone 제거 실험 보류 방침에 따라 현재 우선 실행 대상이 아님 |

`.250`, `.30`, `.180`은 사용자가 준 서버 식별 표기를 그대로 사용했다. 전체 IP·run 디렉터리·checkpoint·seed·관측 iteration 및 성공률 집계 창은 이번 보고에 포함되지 않았다. v2의 “상승 없음”은 정확히 0%라는 뜻으로 바꾸지 않는다. v1_2의 “학습 예정”도 학습 개시나 성능 확인으로 기록하지 않는다.

현재 방향은 **`.30`에서 v1 학습을 계속하고, `.180`에서 v1_2를 학습하여 Deadzone 30° 조건의 보상 강화를 먼저 살펴보는 것**이다. v2와 v2_2 환경은 코드에 남아 있지만 Deadzone 제거 실험은 잠시 미룬다. 이 관찰만으로 보상이나 Deadzone이 성공률 변화의 유일한 원인이라고 확정하지 않는다.

## 환경 목록과 버전별 차이

| Gym ID | 직접 부모 | 초기화 / Reach | sweep_progress Weight | 접촉 계수 | sweep_retreat Weight | Deadzone |
| --- | --- | --- | --- | --- | --- | --- |
| `Inspire-Sweep-Only-v0` | StabilizeSweepEnvCfg | 물체 옆 IK / 없음 | 30 | count / 20 | −20 | 30° |
| `Inspire-Sweep-Only-v0-Test` | Sweep-Only-v0 | Finger 방식 / 사용 | 30 | count / 20 | −20 | 30° |
| `Inspire-Sweep-Only-v1-Test` | v0-Test | 부모 유지 | 50 | count / 20 | −10 | 30° |
| `Inspire-Sweep-Only-v1_2-Test` | v1-Test | 부모 유지 | 100 | **count** | −25 | 30° |
| `Inspire-Sweep-Only-v2-Test` | v1-Test | 부모 유지 | 50 | count / 20 | −10 | **0°** |
| `Inspire-Sweep-Only-v2_2-Test` | v1_2-Test | 부모 유지 | 100 | **count** | −25 | **0°** |

표의 계수는 현재 코드값이다. 각 서버에서 과거에 시작한 실행의 정확한 설정은 해당 실행에 저장된 설정으로 확인해야 한다.

```text
Inspire-Sweep-Only-v0
└── v0-Test: Finger 초기화와 Reach 추가
    └── v1-Test: 정방향 50, 역방향 −10
        ├── v1_2-Test: 정방향 100 × 원시 접촉 카운트, 역방향 −25
        │   └── v2_2-Test: v1_2 보상 유지, Deadzone 0°
        └── v2-Test: v1 보상 유지, Deadzone 0°
```

버전 번호가 높다고 모든 앞선 변경을 누적한 것은 아니다. v2는 v1_2의 보상 변경을 포함하지 않으며, v2_2가 강화된 보상과 Deadzone 제거를 함께 가진다. 위 트리는 EnvCfg의 상속 관계다. 모든 Sweep Only 버전은 공통 `SweepOnlyEnv` runtime을 사용한다.

등록 ID의 하이픈과 밑줄은 구분한다. 예를 들어 학습 task는 `Inspire-Sweep-Only-v1_2-Test`, 로그 experiment name은 `inspire_sweep_only_v1_2_test`다. 로그 경로는 `logs/rsl_rl/<experiment_name>/<run>/` 구조다.

근거: [Gym 등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py), [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/stabilize_sweep_envs.py), [PPO·로그 이름](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/stabilize_sweep_ppo_cfg.py).

## 공통 과제와 초기화

UR5e + Axia80 + RH56E2 오른손으로 선반 위 타겟을 목표 XY 위치로 민다. 물리 주기는 100 Hz, 정책 주기는 50 Hz이며 episode는 최대 10초다. 모든 Sweep Only 환경은 Stabilize 보상·안정화 Gate·초기 이동/회전 비용·압착 페널티를 사용하지 않는다. 내부 Sweep 상태는 reset부터 활성이고 Phase는 관측에 포함하지 않는다.

일반 v0는 타겟의 밀기 반대편에 손을 배치하는 IK·충돌 검사를 수행하고 Reaching이 없다. 손은 로봇 기준 왼쪽을 향한 손바닥 방향을 유지하여 목표 방향에 따라 손바닥 또는 손등으로 민다. 초기 손 높이는 실제 충돌 형상 하단과 상판 간격을 기준으로 잡는다. 일반 초기화는 밀기 최소 공간인 RED와 초기 로봇 점유 공간을 제외하여 장애물을 배치한다.

모든 `-Test`는 기존 Finger 방식의 물체 배치·팔 초기화·단일 Warp IK를 공유하고 Reaching을 사용한다. `-Test`는 IK가 전혀 없는 환경이라는 뜻이 아니다. Test 배치는 선반·RED·물체 간 간격을 검사하지만 일반 환경과 같은 초기 로봇 전체 점유 공간 검사는 하지 않는다. 버전별 보상·Deadzone 변경이 이 초기화 차이를 해소하지는 않는다.

타겟 초기 XY는 선반 중앙 반지름 2cm 원판, 목표 거리는 6–12cm다. Deadzone 30°는 선반 로컬 ±X 방향 주변의 목표 방향 제외 반각이다. 목표 방향은 `[30°,150°]`, `[210°,330°]`에서 생성된다. 0°에서는 이 방향 제외 구간만 제거하며 다른 배치 제약은 유지한다. 방향 커리큘럼은 비활성이므로 각 버전의 각도는 고정이다.

물체 크기·질량과 손·선반·물체 마찰의 랜덤화는 공통이며 기본적으로 spawn/startup에서 추출한다. 매 episode마다 물성을 다시 뽑는 구성은 아니다. 물체 배치와 목표는 reset에서 갱신한다. 상세 범위와 일반/Test의 배치 제약은 [상세 환경 설명](SWEEP_ONLY.md)에 있다.

## 관측과 제어

| 항목 | 모든 Sweep Only 버전의 공통 구성 |
| --- | --- |
| Actor·Critic | 같은 관측 항목과 차원을 사용하는 대칭 구성; 네트워크 파라미터는 별개 |
| 직접 관측 | 팔 관절 절대 위치·속도, 손 주 구동 6관절 절대 위치, EEF pose, 타겟 대표점, 목표, 직전 action, tactile, wrench의 66D |
| 장애물 | `[Mask,x,y,z] × 16`의 64D, MLP `64 → 32 → 16` 인코딩 |
| 모델 본체 입력 | 직접 관측 66D + 장애물 embedding 16D = 82D; export 입력은 130D |
| 물체 위치 | reset 시 정면에서 관측 가능한 대표 표면점을 저장하고 현재 EEF frame으로 변환 |
| EEF pose | 로봇 root frame 기준 |
| Tactile | 손바닥 17·손등 17 bit를 17D로 결합; 기본 관측에는 bit별 1% flip |
| Wrench | 손의 중력·관성 보상 후 EEF 기준 변환·관측 noise·축별 clip; 힘 ±150N, 모멘트 ±8N·m |
| Action | 팔 6D OSC + 손 6D Joint Position Control |
| Action clip | PPO runner의 실행 wrapper `clip_actions=π/2`; Gaussian 출력 자체를 유계로 만드는 것은 아님 |

대표점은 가시 mask 면적 중심에 가까운 유효 표면점이다. 물체 전체 centroid나 2D bounding box 중앙과 항상 같지는 않다. 초기 월드 위치를 고정하므로 물체가 이동해도 물체 위치 관측은 갱신하지 않고, EEF 이동·회전에 따른 좌표 변환만 갱신한다. 목표도 EEF 기준으로 제공한다. 보상·성공 판정에는 관측용 초기 대표점 대신 실제 현재 타겟 위치를 사용한다.

`-Test`의 GUI에서 기본 활성인 빨간 대표점 마커는 물리적 상호작용이 없고 초기 월드 위치에 남는다. 일반 v0에서는 기본 비활성이며 headless에서는 표시하지 않는다. 센서·관측의 세부 범위와 구현 한계는 [상세 관측 설명](SWEEP_ONLY.md#정면-대표-표면점)을 따른다.

## Sweeping과 역 Sweeping

$d_t$는 실제 현재 타겟 centroid와 목표의 XY 거리, $c_t$는 0–20 접촉 카운트, $a_t$는 0–1 힘 방향 정렬 계수다. 접촉 계수 $h_t$는 해당 step의 접촉 인식 조건을 만족하면 버전에 따라 $c_t/20$ 또는 $c_t$, 불만족하면 0이다.

```math
r_{\mathrm{progress},t}=w_p\max(d_{t-1}-d_t,0)h_ta_t
```

```math
r_{\mathrm{retreat},t}=w_r\max(d_t-d_{t-1},0)
```

거리 항은 함수의 dt 나눗셈과 RewardManager의 dt 곱셈이 상쇄되므로 위 값이 step 보상이다. $w_r$는 음수다.

최근 3 policy interval 중 2개 이상 접촉이 인정되고 EEF가 상판 위 12cm 미만이면 카운트를 1 올린다. 불인정이면 2 낮추고 0–20으로 제한한다. 정방향은 현재 접촉·유효 데이터·수평 평균 힘 1N 이상 조건도 필요하다. 방향 계수는 타겟→목표 XY 방향과 3D 평균 힘의 정렬을 사용한다. 접촉 유지 시간만으로 독립적인 양의 보상을 지급하지 않는다.

역방향은 거리 증가량만 보고 접촉·힘 방향·높이 조건을 요구하지 않는다. 직전 거리 기준이므로 후퇴한 뒤 재접근하면 정방향 보상이 다시 발생할 수 있다. 기존 Finger의 최고 접근 기록 갱신 보상과 이 점이 다르다.

| 비교 | 정방향 변화 | 역방향 페널티 절댓값 변화 |
| --- | --- | --- |
| v0-Test → v1-Test | 50/30배 | 10/20 = 0.5배 |
| v1-Test → v1_2-Test | 정규화 제거 20배 × Weight 2배 = **40배** | 25/10 = **2.5배** |
| v1-Test → v2-Test | 동일 식·계수 | 동일 식·계수 |
| v1_2-Test → v2_2-Test | 동일 식·계수 | 동일 식·계수 |

배율은 동일 상태·접촉 이력·힘 방향에서의 비교다. 목표 분포와 학습 행동이 달라지면 episode 누적 보상이 같은 배수로 변한다는 뜻은 아니다. 예를 들어 접촉 카운트 20·정렬 1·유효 조건에서 1cm 전진의 보상은 v1에서 0.5, v1_2에서 20이다. 1cm 후퇴는 각각 −0.1, −0.25다.

Test의 Reaching은 모든 버전에서 동일하게 Weight 30을 사용하고 타겟–EEF 거리 10cm 이내에서 근접 계수가 최대다. 초기 거리 budget에 따른 지급률을 사용하므로 실제 수령액은 정책·episode 길이에 따라 다를 수 있다. 일반 v0에는 Reaching이 없다.

보조 비용은 action 변화, 팔·손 관절 속도, 선반 충돌·실패, 장애물 접촉력, 보정 F/T 크기 변화, 활성 물체 기울기, 장애물 이동량이다. 장애물 접촉과 F/T 변화의 허용값·Weight 커리큘럼은 모든 버전에서 같다. 처음부터 모든 보조 비용의 Weight가 최종값인 것은 아니다. 상세 수치·일정은 [보상 설명](SWEEP_ONLY.md#보조-비용)과 [커리큘럼](SWEEP_ONLY.md#curriculum)에 있다.

근거: [Reward 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/stabilize_sweep.py), [실제 카운트·방향·거리 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_state.py).

## 종료와 성공률 해석

모든 버전은 팔 관절 중 하나라도 절대 속도가 1 rad/s를 초과하거나, 활성 물체가 넘어지거나 떨어지거나, 선반 실패 조건에 도달하면 조기 종료한다. 속도 종료는 손 관절이 아니라 팔 관절 대상이다.

목표에 일찍 도달해도 즉시 성공 종료하지 않는다. 10초 timeout 시 실제 타겟–목표 XY 거리가 **엄격히 3cm 미만**이고 같은 step에 물리 실패가 없으면 성공이다. 이 조건은 현재 실제 코드이며, 정확히 3cm인 경우 성공이 아니다. 추가 성공 bonus는 없다.

`Metrics/timeout_success_rate`는 최근 완료 episode 최대 10,000개에서 **timeout 성공 수 / timeout 수**다. 조기 실패는 그 분모에서 제외되므로 전체 episode 성공 비율과 다르다. 위 사용자 보고의 10%·20%에 어떤 집계 지표를 사용했는지는 이번 전달에서 별도로 특정되지 않았다. 따라서 수치를 그대로 보존하고 다른 성공률 지표로 환산하지 않았다.

## 실행과 현재 검증 범위

`.180`에서 예정한 환경의 실행 명령은 다음과 같다. 이 문서 작성 중에는 실행하지 않았다.

```bash
conda activate env_isaaclab
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Only-v1_2-Test --num_envs 2048 --headless
```

v1의 학습 지속은 사용자가 운영 중인 `.30` 실행에 대한 계획이다. 이 문서가 새 v1 프로세스를 시작하거나 checkpoint 재개 방법을 지정한 것은 아니다.

v1_2·v2_2 추가 때 수행한 코드·CPU 검사와, 사용자가 별도 서버에서 관찰한 학습 결과를 구분한다. 이번 작업은 문서 작성과 코드 대조만 수행했다. GPU·Isaac Sim·원격 서버·학습 로그·학습 프로세스는 변경하지 않았다. 관련 변경 기록은 [v1_2](../logs/2026-11-19_sweep_only_v1_2_test.md), [v2_2](../logs/2026-11-19_sweep_only_v2_2_test.md), [이번 문서화](../logs/2026-11-19_sweep_only_family_documentation.md)에 있다.
