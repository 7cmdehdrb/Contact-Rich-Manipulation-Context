# Inspire-Sweep-Only 계열: 환경 구성·버전 차이·학습 현황

2026-11-20 최신 사용자 학습 배치는 새 [Sweep 계통 문서](SWEEP_FAMILY.md#현재-학습-현황)를 따른다: `.180`=Inspire-Sweep-v0, `.250`=Inspire-Sweep-Single-Contact-v0. 아래 Sweep Only 서버 현황은 이전 배치의 기록으로 보존한다. 기존 환경의 Pull/Push 외 성공과 손등 편향 관찰·새 선호도 설계의 목적도 새 계통 문서에 정리했다.

2026-11-20: 이 계열의 v2-Test-ActionPenalty-LinearReach를 기능 기준으로 **별도 독립 계통 `Inspire-Sweep-v0`**를 추가했다. 기존 계열은 보존하며 새 EnvCfg/PPO를 직접 선언한다. 접촉면별 Sweep 선호·고정 비용·관측 F/T 정규화는 [Sweep v0 계약](SWEEP_V0.md)을 따른다.

2026-11-20 후속: `Inspire-Sweep-Only-v2-Test-ActionPenalty-LinearReach`는 v2-Test-ActionPenalty를 직접 상속하고 Reach만 선형 근접식으로 바꾼다. [LinearReach 구성·실행](#linearreach-파생-환경)을 참고한다. 기존 서버별 학습 현황은 아래 사용자 보고를 유지한다.

2026-11-20: 기존 6종을 각각 직접 상속하는 `-ActionPenalty` 파생 환경을 추가했다. 서버별 최신 상태는 아래 11월 20일 사용자 보고에 기록했으며, 11월 19일 기록도 과거 이력으로 보존했다. 신규 환경의 구성과 검증은 [ActionPenalty 파생 환경](#actionpenalty-파생-환경)을 따른다. 기존 ID는 수정하지 않았다.

2026-11-20 갱신. 환경 구성은 코드에서 확인한 내용이며, 서버별 성공률과 기대는 아래 날짜별 사용자 관찰이다. 원격 서버의 로그를 새로 읽거나 학습을 시작한 기록은 아니다. 세부 물리·센서·초기화 구현은 [Sweep Only 상세 설명](SWEEP_ONLY.md)을 참고한다.

## 현재 학습 현황: 2026-11-20 사용자 보고

최신 후속 보고에 따라 **보상 계수·접촉 카운트 변경(v1_2)이 효과 없다고 잠정 가정**하고, progress50·retreat−10·count/20 조합의 ActionPenalty 두 환경을 학습 중이다. 이는 실험 진행을 위한 가정이며 변경 효과가 없다는 통계적 결론은 아니다.

| 서버 | 현재 Task ID | 로그 experiment name | 상태 | Deadzone |
| --- | --- | --- | --- | --- |
| `.250` | `Inspire-Sweep-Only-v2-Test-ActionPenalty` | `inspire_sweep_only_v2_test_action_penalty` | 학습 중 | 0° |
| `.180` | `Inspire-Sweep-Only-v1-Test-ActionPenalty` | `inspire_sweep_only_v1_test_action_penalty` | 학습 중 | 30° |
| `.30` | 해당 없음 | 해당 없음 | 학습 없음 | 해당 없음 |

두 실행의 iteration·성공률·seed·새 학습/재개 여부는 미보고다. 원격 실행을 확인하거나 시작한 것이 아니라 사용자 보고를 기록했다. 아래 원본 환경의 결과는 과거 이력이며 현재 서버 배치와 구분한다.

## 과거 이력: 2026-11-20 원본 환경 결과

| 서버 | 로그 experiment name | 중단 여부 | 성공률·진행량 | 해석 경계 |
| --- | --- | --- | --- | --- |
| `.180` | `inspire_sweep_only_v1_2_test` | 중단되지 않음 | 성공률 20% 미만; iteration 미보고 | 높은 보상 설정의 성능이 아직 낮다는 관찰; 수치적 안정성 보장 아님 |
| `.250` | `inspire_sweep_only_v2_test` | 학습 중단 | 약 10k iteration에서 성공률 약 50% | 성능 향상과 학습 중단이 함께 발생 |
| `.30` | `inspire_sweep_only_v1_test` | 학습 중단 | 약 5k iteration에서 성공률 약 20% | 더 상승할 수 있다는 사용자의 기대; 이후 상승은 미검증 |

위 수치는 사용자 보고값이며 이번 문서 갱신에서 원격 로그를 재측정하지 않았다. 성공률 집계 구간·정확한 tag·seed와 v1_2의 진행량은 이번 보고에서 특정되지 않았다. 앞서 로컬 `logs/TEMP/wr6` 진단에서 확인한 마지막 `Metrics/timeout_success_rate` 약28.7%(v1)·67.5%(v2)는 다른 시점/집계일 수 있으므로 위 약20%·50%를 대체하지 않는다. 사용자 보고값과 진단값이 동일한 시점·지표라는 가정으로 비교하지 않는다.

이번 세 실행은 기존 ID의 결과다. 새 `-ActionPenalty` 환경의 학습 성과로 해석하지 않는다. v1과 v2는 각각5k·10k라서 Deadzone만의 효과를 분리할 수 없고, v1_2는 정방향 보상이 v1 대비40배인 반면 후퇴 비용은2.5배여서 접근과 이탈의 상대 균형이 크게 다르다. 가능한 설명과 미확인 사항은 [분석 기록](../logs/2026-11-20_sweep_only_training_status.md)에 구분한다.

## 과거 이력: 2026-11-19 학습 현황과 경위

아래는 당시 보고를 보존한 기록이며 현재 중단 여부는 위 11월 20일 표가 우선한다.

2026-11-19 최종 사용자 보고를 반영했다. 현재 `.30`의 v1-Test, `.180`의 v1_2-Test, `.250`의 v2-Test가 모두 학습 중이다.

| 로그 experiment name | 현재 서버 표기 | 상태 | 사용자 관찰·경위 |
| --- | --- | --- | --- |
| `inspire_sweep_only_v1_test` | `.30` | **학습 중** | 이전 보고에서 성공률 약 20%까지 상승; 학습 계속 진행 |
| `inspire_sweep_only_v1_2_test` | `.180` | **학습 중** | 이전의 학습 예정 상태에서 실제 학습 진행으로 갱신; 최신 성공률 수치는 미보고 |
| `inspire_sweep_only_v2_test` | `.250` | **학습 중** | 초기에는 실패한 것으로 판단했으나 약 2000 iteration부터 성공률 상승 경향을 관찰하여 컴퓨터를 바꿔 시도 중 |
| `inspire_sweep_only_v0_test` | 과거 `.250` | 과거 비교 실행 | 성공률이 10%를 넘지 못해 v1 보상 조정의 계기가 됨; 현재 실행 상태는 별도 보고 없음 |
| `inspire_sweep_only_v2_2_test` | 미지정 | 학습 상태 미보고 | 구현된 비교 환경이며 이번 갱신에서 실행·성능 보고 없음 |

이전 보고에서는 `.180`의 v2-Test 성공률이 오르지 않는 것으로 보여 Deadzone 제거 실험을 잠시 보류하려 했다. 이후 **약 2000 iteration부터 성공률이 올라가는 경향**이 확인되어, 현재는 `.250`으로 컴퓨터를 바꿔 v2-Test를 학습 중이다. 따라서 “Deadzone 제거 실험 보류”는 현재 방침이 아니라 이전 판단이다. v2-Test는 Deadzone 0°·정방향 50·역방향 −10·정규화 접촉 카운트 구성을 그대로 사용한다.

`.250`, `.30`, `.180`은 사용자가 준 서버 식별 표기를 그대로 사용했다. 전체 IP·run 디렉터리·checkpoint·seed·현재 iteration·성공률 집계 창은 이번 보고에 포함되지 않았다. v2의 상승 시작 시점 약 2000 iteration은 사용자 관찰이며 현재 iteration이나 최신 성공률을 뜻하지 않는다. 서버를 바꾼 실행이 새 학습인지 checkpoint 재개인지는 특정하지 않았다.

현재는 Deadzone 30°의 v1·v1_2 보상 비교와 Deadzone 0°의 v2 실험이 함께 진행 중이다. v1의 약 20%는 이전 보고값이며 이번 갱신에서 새 수치를 측정하지 않았다. 이 관찰만으로 보상·Deadzone·컴퓨터 변경이 성공률 변화의 유일한 원인이라고 확정하지 않는다.

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

현재 `.180`에서 학습 중인 v1_2-Test의 실행 명령 예시는 다음과 같다. 기존 학습을 중복 실행하라는 뜻이 아니며, 이번 문서 갱신 중에는 실행하지 않았다.

```bash
conda activate env_isaaclab
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Only-v1_2-Test --num_envs 2048 --headless
```

현재 `.30`의 v1-Test, `.180`의 v1_2-Test, `.250`의 v2-Test가 학습 중이라는 상태를 사용자 보고로 기록했다. 이 문서 갱신에서 프로세스를 시작·중단하거나 checkpoint 재개 방법을 지정하지 않았다.

v1_2·v2_2 추가 때 수행한 코드·CPU 검사와, 사용자가 별도 서버에서 관찰한 학습 결과를 구분한다. 이번 작업은 문서 작성과 코드 대조만 수행했다. GPU·Isaac Sim·원격 서버·학습 로그·학습 프로세스는 변경하지 않았다. 관련 변경 기록은 [v1_2](../logs/2026-11-19_sweep_only_v1_2_test.md), [v2_2](../logs/2026-11-19_sweep_only_v2_2_test.md), [이번 문서화](../logs/2026-11-19_sweep_only_family_documentation.md)에 있다.


## ActionPenalty 파생 환경

`inspire_sweep_only_v1_test_action_penalty`의 15개 보상·페널티와 학습 일정은 [v1-Test-ActionPenalty 보상 상세](SWEEP_ONLY_V1_TEST_ACTION_PENALTY_REWARDS.md)에 정리했다. 해당 문서는 사용자 요청에 따라 시간 간격을 제외하고 각 항을 step t의 식으로 표기한다.

2026-11-20 추가. 기존 환경을 보존하고 실행 액션의 제한 위치와 페널티 입력만 분리한다. 각 EnvCfg와 PPORunnerCfg는 해당 원본을 직접 상속하며 runtime은 공통 `SweepOnlyEnv`다.

| 신규 Task ID | 직접 부모 Task ID | 로그 experiment name |
| --- | --- | --- |
| `Inspire-Sweep-Only-v0-ActionPenalty` | `Inspire-Sweep-Only-v0` | `inspire_sweep_only_v0_action_penalty` |
| `Inspire-Sweep-Only-v1-ActionPenalty` | `Inspire-Sweep-Only-v0` | `inspire_sweep_only_v1_action_penalty` |
| `Inspire-Sweep-Only-v0-Test-ActionPenalty` | `Inspire-Sweep-Only-v0-Test` | `inspire_sweep_only_v0_test_action_penalty` |
| `Inspire-Sweep-Only-v1-Test-ActionPenalty` | `Inspire-Sweep-Only-v1-Test` | `inspire_sweep_only_v1_test_action_penalty` |
| `Inspire-Sweep-Only-v1_2-Test-ActionPenalty` | `Inspire-Sweep-Only-v1_2-Test` | `inspire_sweep_only_v1_2_test_action_penalty` |
| `Inspire-Sweep-Only-v2-Test-ActionPenalty` | `Inspire-Sweep-Only-v2-Test` | `inspire_sweep_only_v2_test_action_penalty` |
| `Inspire-Sweep-Only-v2_2-Test-ActionPenalty` | `Inspire-Sweep-Only-v2_2-Test` | `inspire_sweep_only_v2_2_test_action_penalty` |

### LinearReach 파생 환경

`Inspire-Sweep-Only-v2-Test-ActionPenalty-LinearReach`는 **`Inspire-Sweep-Only-v2-Test-ActionPenalty`를 직접 상속**한다. EnvCfg는 `SweepOnlyV2TestActionPenaltyLinearReachEnvCfg`, PPO runner는 `SweepOnlyV2TestActionPenaltyLinearReachPPORunnerCfg`, runtime은 기존 `SweepOnlyEnv`다. 로그 이름은 `inspire_sweep_only_v2_test_action_penalty_linear_reach`다.

현재 실제 EEF 위치를 $\mathbf{e}_t$, 실제 타겟 bounds 중심을 $\mathbf{p}_t$로 두면, 요청에 따라 시간 간격을 생략한 Reach는 다음과 같다.

```math
\rho_t=\lVert\mathbf{e}_t-\mathbf{p}_t\rVert_2,
\qquad
r_{\mathrm{reach},t}
=0.8\max\left(1-\frac{\max(\rho_t-0.10,0)}{0.35},0\right).
```

10cm 이내에서는 가중값0.8, 10–45cm에서는 선형 감소, 45cm 이상에서는0이다. `linear_reach` 함수는0–1 근접도를 반환하며 `reaching.weight=0.8`, `near_radius=0.10`, `decay_distance=0.35`, `frame_name='ee_frame'`를 사용한다. 초기 root 거리·episode 길이에 따른 배율과 reset 이력을 사용하지 않는다. 현재 bounds 중심을 사용하므로 물체가 움직이면 거리가 갱신된다.

실행에서는 부모와 같이 RewardManager가 policy 시간 간격0.02초를 한 번 곱한다. 따라서 Reach term의 실제 최대 step 기여는0.016이다. 위 식은 앞선 보상 문서·그래프와 동일한 시간 간격 생략 표기다. 거리 증분 보상처럼 새 함수가 시간 간격을 나누는 처리를 추가하지 않는다.

| 항목 | 부모 v2-Test-ActionPenalty | LinearReach 자식 |
| --- | --- | --- |
| Reach 함수 | `InverseDistanceReach` | `linear_reach` |
| Reach weight | 30 | 0.8 |
| 거리 배율 | `distance_scale=0.10`의 역거리 | `decay_distance=0.35`의 선형 감소 |
| 근접 반경·좌표 | 10cm·현재 타겟 bounds 중심 | 동일 |
| 초기 거리·episode 길이 배율 | 사용 | 제거 |
| 다른 보상·ActionPenalty·관측·reset·종료·curriculum | 부모 구성 | 동일 |
| Sweep·Deadzone | 50/−10·count/20·0° | 동일 |
| PPO | 부모 구성 | experiment name만 변경 |

학습은 workspace 루트에서 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Only-v2-Test-ActionPenalty-LinearReach \
  --num_envs 2048 --headless
```

이번 추가로 새 학습을 시작하거나 기존 서버 실행을 바꾸지는 않았다. 실제 전체 설정 대조·CPU·GPU smoke 결과와 미검증 범위는 [개발 로그](../logs/2026-11-20_sweep_only_v2_test_action_penalty_linear_reach.md)에 기록한다.

### 물체 옆 IK와 v1 보상: v1-ActionPenalty

2026-11-20 후속 요청으로 `Inspire-Sweep-Only-v1-ActionPenalty`를 추가했다. `Inspire-Sweep-Only-v0`를 직접 상속하여 물체 옆 IK·충돌 검사·스폰 제외 공간을 유지하고, Sweep 계수만 v1의 **progress50 / retreat−10 / count÷20**으로 맞췄다. Deadzone은30°다. 아래 공통 ActionPenalty 처리도 적용한다. PPO runner는 v0 runner를 직접 상속하고 clip_actions=None·독립 experiment name만 변경한다.

`Inspire-Sweep-Only-v1-Test-ActionPenalty`와의 전체 설정 차이는 **일반 물체 옆 초기화 Event 구성, Reach 없음, 대표점 GUI 마커 기본 비활성**이다. 물체 옆 시작에는 Reach를 사용하지 않는 기존 원칙을 유지한다. 따라서 초기화 이외에 Reach·마커 차이도 있음을 구분한다. 나머지 관측·제어·Sweep 보상·종료·curriculum·모델은 같다. 별도의 `Inspire-Sweep-Only-v1` ID는 만들지 않았다.

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Only-v1-ActionPenalty --num_envs 2048 --headless
```

이번 추가는 특정 서버에서 학습을 시작했다는 보고가 아니다. [개발·검증 기록](../logs/2026-11-20_sweep_only_v1_ik_action_penalty.md)을 참고한다.

### 액션·보상 계약

Runner의 `clip_actions=None`으로 원본 12D 출력을 ActionManager에 전달한다. Manager의 현재·이전 액션은 원본을 보관하며, 실행 직전에 팔 6D만 `[-π/2, π/2]`로 제한한 뒤 기존 OSC의 위치 0.03·회전 0.15 scale을 적용한다. 손 6D는 기존 `FingerJointPositionAction`에서 `[0, URDF 상한]`으로 제한한다. 상한은 엄지 굽힘·검지·중지·약지·소지·엄지 대립 순서로 `[0.5864, 1.4381, 1.4381, 1.4381, 1.4381, 1.1641] rad`이며 follower mimic·구동기 설정은 그대로다. 모든 손 상한이 π/2 미만이므로 같은 유한 정책 액션에 대한 실제 실행 명령은 부모와 같다.

신규 `arm_action_limit`, `hand_action_limit`는 각각 허용 구간 밖으로 나간 양을 구간 전체 폭으로 나눈 뒤 6채널의 제곱평균을 계산한다. 팔 폭은 π, 손 폭은 각 관절 상한이다. 내부와 경계에서는 0이며, 초과량이 두 배면 비용은 네 배다. 각 weight는 **−0.03**으로 시작하며 RewardManager가 policy dt=0.02를 한 번 곱한다. 예를 들어 한 그룹의 모든 채널이 전체 구간 폭만큼 초과하면 해당 term의 step 기여는 −0.0006이다. 계수는 기존 Action 비용을 참고한 초기 실험값이며 장기 안정성이 검증된 값이 아니다.

기존 `arm_action_rate`, `hand_action_rate`는 각각 `sum((a_t - a_prev)^2)`와 weight **−0.03**을 유지하되, 두 액션 모두 **클리핑 전** Manager 이력을 사용한다. 기존 환경에는 별도의 액션 크기 L2 항이 없으며, 이번에도 그 항을 새로 추가하지 않는다. 부분 reset 시 선택된 행의 현재·이전 액션은 기존 Manager reset에 따라 0으로 초기화한다.

Last Action 관측만 기존처럼 원본의 `[-π/2, π/2]` 클리핑값을 반환한다. 원본 출력 확대가 관측으로 그대로 되먹임되지 않도록 기존 의미를 보존한 것이다. 이는 손의 최종 관절 목표각 관측이 아니다. 관측 차원, 표면점, F/T, 촉각, Actor/Critic 구조·분포, entropy coefficient, 학습률, 수치 오류 검사, Sweep/Reach 계수, Deadzone, reset, 종료 및 curriculum은 모두 부모와 같다. IsaacLab과 모델 코드는 수정하지 않았다.

### 학습과 검증

workspace 루트에서 다음과 같이 새 학습을 시작한다. 각 부모의 Task ID 뒤에 `-ActionPenalty`를 붙이면 된다.

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Only-v1-Test-ActionPenalty --num_envs 2048 --headless
```

과도한 원본 출력을 가진 중단 직전 checkpoint를 그대로 재개하면 새 페널티와 Action 변화 비용이 매우 커질 수 있다. 신규 설정은 출력의 수학적 상한이나 학습 발산 방지를 보장하지 않는다. 장기 학습·2048환경 collection time·성공률은 이번 검증 대상이 아니다.

전체 부모/자식 설정 대조, CPU 회귀, 실제 wrapper·reset·step·부분 reset 결과는 [개발 로그](../logs/2026-11-20_sweep_only_action_penalty.md)에 기록한다.
