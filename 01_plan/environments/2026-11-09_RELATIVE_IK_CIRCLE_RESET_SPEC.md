# Relative-IK 원 기반 배치 및 리셋 최적화 개발 명세

작성일: 2026-11-09. 상태: **후속 지시에 따라 Fast-Test 자식 환경에 구현 및 CPU 검증 완료. 실제 자산/GPU 출시 기준은 미검증**.

[현재 인계](../00_HANDOFF_BRIEF.md) · [리셋 비교 분석](../../02_implementation/logs/2026-11-09_reset_performance_comparison.md)

## 1. 목적과 적용 범위

학습 중 IK 표시 비용, 작은 배치의 CPU/GPU 왕복, OBB 반복 탐색, 중복 상태 기록을 줄인다. 배치에는 물체의 Top-Down BBOX 외접원을 사용하고, RED/WHITE 두 영역만 둔다. 매 에피소드 새 배치를 생성하며 공유 장면·유한 초기 상태 풀은 도입하지 않는다.

사용자가 지정한 파일은 `src/inspire_sweep_baseline/inspire_sweep_baseline/envs/wrench_refactor_relative_ik_test_envs.py`다. 코드 기준은 workspace commit `3501ffb`이며 구현 착수 시 HEAD와 실제 설정을 다시 기록한다.

적용 단위는 사용자 후속 지시에 따라 **`Inspire-Wrench-Refactor-Relative-IK-v0_2_2_2-Fast-Test` 새 환경**이다. `WrenchRefactorRelativeIKV0_2_2_2TestEnvCfg`를 직접 상속하며 기존 v0_2_2_2-Test를 보존한다. 최초 명세의 기존 환경 직접 수정 기본값은 이 지시로 대체되었다. [구현 계약](../../02_implementation/environments/WRENCH_REFACTOR_RELATIVE_IK_FAST_TEST_ENVIRONMENT.md) · [검증 기록](../../02_implementation/logs/2026-11-09_relative_ik_fast_test.md).

공유 함수의 기본 동작을 일괄 변경하여 v0_2/v0_2_1/v0_2_2/v0_2_2_1 및 보류된 Reset-Test에 자동 전파하지 않는다. 대상 EnvCfg의 event/backend 선택으로 범위를 한정하고 부모의 구성이 변하지 않게 한다. 다른 버전까지 전환한 것으로 간주하지 않는다.

최초 명세 작성은 문서만 변경했다. 이후 구현 요청으로 Fast-Test 코드·등록·부모를 상속한 runner를 추가했다. 학습 로그는 변경하지 않았다.

## 2. 확정 요구와 설계 기본값

### 2.1 사용자 확정 요구

| 항목 | 최종 요구 |
| --- | --- |
| 학습 중 IK 박스 | 비가시 처리 및 불필요한 갱신 비용 제거 |
| IK | 기존 수식 유지, Warp kernel로 이전 |
| 배치 알고리즘 | 후보/재시작/패스 중심의 무작위 재탐색을 줄이는 안정적 방법 |
| 영역 | GRAY 삭제, RED와 WHITE만 사용 |
| RED | 타겟 외접원의 시작→목표 이동 영역을 선반의 로봇 쪽 앞 경계까지 연장 |
| 물체 영역 | 외접원 반지름에 1cm를 더한 동심원 |
| 물체 배치 | 유효 영역 안에서 확장 원끼리 겹치지 않도록 랜덤 배치 |
| 장애물 개수 | 정수0–6의 균등분포, 각 확률1/7 |
| 불변/중복 처리 | 불변 geometry 캐시, 중복 상태 기록 제거 |

기존 두 개의0–3 추첨을 합산한 삼각형 분포와 이전 답변의 분포 보존 제안은 폐기한다. GRAY/WHITE 카운트를 추첨한 뒤 합치는 구현도 사용하지 않는다.

### 2.2 명세에서 채택한 개발 기본값

아래 항목은 사용자 지정 숫자와 구분되는 설계 결정이다. 구현자는 변경 시 근거와 영향을 기록해야 한다.

| 항목 | 기본값/정책 |
| --- | --- |
| 공간 분할 | 한 변5mm인 정사각형 셀 |
| 물체 순서 | 반지름 내림차순, 동률은 추첨한 ID 순서 |
| 유효 셀 선택 | 동일 면적 셀 사이 균등 선택, 셀 내부 연속 균등 좌표 |
| 여유 통일 | 타겟 포함 각 물체의 외접원에1cm; 기존 red_margin2.3cm 추가 중첩 없음 |
| 실패 처리 | 개수 축소·목표 재추첨·기본 배치 fallback 없이 명시적 실패; 학습 적용 전 실패 표본 해소 |
| 수치 안전 여유 | 기하 판정에1µm의 보수적 여유; 침범을 허용하는 epsilon 금지 |
| 디버그 | 기본 OFF, play/진단에서 명시적으로 ON 가능 |

5mm 셀과 실패 정책은 성공률이 입증된 결과가 아니다. 검증을 통과하기 전 장기 학습 적용 완료로 선언하지 않는다.

## 3. 보존할 환경 계약

- 로봇·선반·물체 에셋과 collider, 물리 pool17개(타겟1+장애물 후보16), 환경별 형상·scale, 관측16슬롯을 유지한다.
- target kind는 기존 cylinder, 타겟 root의 초기 위치·고정 yaw, 목표 거리6–12cm 및 방향 커리큘럼은 유지한다. 타겟/목표 생성에서 원 반지름으로 기존 안전 범위를 다시 제한하거나 실패 목표를 재추첨하지 않는다.
- 물성은 일반 Test처럼 startup 추첨 후 고정한다. Reset-Test의 매 reset 질량·관성·마찰 재추첨을 가져오지 않는다.
- Actor/Critic 입력·가시성·노이즈·이웃 swap, 행동8D, OSC·Hand 제어·F/T 보정, 센서 구성을 유지한다.
- 대상 버전의 모든 reward·weight·누적 상태·종료·커리큘럼,10초 timeout, physics100Hz/policy50Hz, rollout36 및 PPO 설정을 유지한다.
- 초기 배치 분포는 의도적으로 달라진다. 기존 OBB/GRAY 분포나 전체 학습 trajectory와의 동일성을 주장하지 않는다.
- 공유 scene 교체를 위한 전체 timeout, 실패 종료 지연, reset batch 합치기를 도입하지 않는다.

## 4. 좌표와 불변 geometry

계산은 shelf-local XY에서 수행한다. 유효 선반 직사각형은 기존 기준 `x∈[-0.20,0.20]m`, `y∈[-0.50,0.50]m`이며 로봇 쪽 앞 경계는 `x=+0.20m`다. world/base frame과 혼용하지 않고 최종 pose 기록 시 shelf pose로 변환한다.

초기 upright 자세를 반영한 각 물체의 로컬 BBOX로 다음을 준비한다. XY 중심 offset은 물체 root 기준이다.

```math
o_i=(b_{i,\min,xy}+b_{i,\max,xy})/2
```

```math
h_i=(b_{i,\max,xy}-b_{i,\min,xy})/2,\quad
r_i=\sqrt{h_{i,x}^2+h_{i,y}^2},\quad R_i=r_i+0.01
```

균일 scale에서는 기본 반지름·offset에 scale을 한 번 곱한다. 이미 scaled bounds로 계산했다면 다시 곱하지 않는다. 비균일 scale로 확장할 경우 축별 scaled half extent에서 반지름을 다시 계산해야 한다.

캐시: `radius[N,17]`, `placement_radius[N,17]`, `center_offset[N,17,2]`, `spawn_z[N,17]`, 기존 관측용 geometry, 고정 셀 중심. CUDA 실행에서는 GPU에 유지하며 reset마다 NumPy/CPU로 geometry를 옮기지 않는다.

배치한 원 중심 `c`와 yaw `θ`를 물체 root로 바꾸는 식은 다음과 같다.

```math
p_{root,xy}=c-\mathrm{Rot}(\theta)o_i
```

타겟은 기존 root/goal 생성 결과에서 고정 yaw offset을 더해 원 중심 `c₀,c₁`을 얻는다. 원 배치 도입을 이유로 기존 goal command를 BBOX 중심 좌표로 바꾸지 않는다. 타겟 회전은 기존 고정값이며 장애물 yaw는 위치 결정과 독립적인 연속 균등분포다.

## 5. RED와 WHITE

타겟 원 중심의 시작–목표 선분을 로봇 쪽으로 충분히 연장한 영역을 `Q`라 한다. `b=(1,0)`, `L=max(0,0.20-min(c₀x,c₁x))`로 두면 선분의 모든 점이 선반 앞 경계에 도달하도록 연장된다.

```math
Q=\{(1-t)c_0+tc_1+u b\mid 0\le t\le1,\ 0\le u\le L\}
```

물리적 타겟 이동/접근 영역은 `Q`를 반지름 `rₜ`인 원으로 확장한 영역이다. 배치용 RED는 타겟에도1cm를 적용하여 `Q`를 `Rₜ=rₜ+0.01`만큼 확장하고 선반 안으로 잘라 정의한다. WHITE는 선반 내부에서 이 RED를 제외한 영역이다.

장애물 중심 `cᵢ`의 유효 조건:

```math
\mathrm{dist}(c_i,Q)\ge R_t+R_i+\varepsilon
```

따라서 장애물 중심이 WHITE에 있다는 사실만으로는 배치하지 않는다. 확장 원 전체가 RED 밖에 있어야 한다. 장애물 간에는 다음 조건을 적용한다.

```math
\|c_i-c_j\|\ge R_i+R_j+\varepsilon
```

장애물 확장 원 전체가 선반 안에 있어야 한다. 물체끼리 외접원 기준2cm, 장애물과 선반 경계는1cm 여유다. 기존 `finger_gap`, `wall_margin`, `red_margin`을 다시 더하지 않는다. 타겟 시작/목표의 선반 안전성은 기존 생성 규칙을 유지한다.

`Q`는 최대4개 꼭짓점의 볼록 영역이다. 내부점 거리는0, 외부점 거리는 변까지의 최단 거리로 계산한다. 이동 방향과 연장 방향이 평행한 선분 축퇴, 길이0인 변, 정지 목표의 진단 입력도 NaN 없이 처리한다. 포인트마다 Robot Base를 향하는 방사형 연장은 사용하지 않는다.

## 6. 장애물 추첨과 단일 순차 배치

1. 대상 환경마다 정수 `N∼DiscreteUniform{0,…,6}`을 한 번 추첨한다.
2.16개 후보 body에서 `N`개 ID를 중복 없이 균등 선택한다. 큰 물체가 선택될 확률을 낮추지 않는다.
3. 선택된 ID를 반지름 내림차순으로 배치한다. 배열 반환은 원래 body slot 기준으로 복구한다.
4. 각 물체에 대해 선반 경계·RED·이미 배치한 원을 이용해 안전 셀 mask를 계산한다.
5. 안전 셀 한 개를 균등 선택하고, 셀 내부에서 XY를 연속 균등 추첨한다.
6. 최종 중심과 yaw로 root pose를 계산한다. 모든 비활성 body는 기존 주차 pose·gravity 규칙으로 기록한다.

N=0에서는 장애물 배치 계산을 생략하되 타겟/목표/IK/관측 초기화는 수행한다. 최대6개 물체의 순차 의존성은 유지하고, 환경·셀 방향으로 병렬화한다. 전체 환경 크기의 불필요한 scratch 대신 reset batch에 필요한 고정 buffer를 재사용한다.

### 6.1 셀 전체의 안전성

셀 한 변을 `a=0.005m`, 반대각선 길이를 `d=a/√2`로 둔다. 셀 중심 `g`가 다음 조건을 만족할 때만 안전 셀로 선택한다.

- 선반 모든 경계에서 거리 ≥ `Rᵢ+d+ε`.
- `dist(g,Q) ≥ Rₜ+Rᵢ+d+ε`.
- 모든 기배치 물체에 대해 `|g-cⱼ| ≥ Rᵢ+Rⱼ+d+ε`.

이에 따라 셀 내부 어느 좌표를 뽑아도 안전하다. 약16,000개 셀의 거리 검사와 reduction으로 동작한다. 선택은 mask의 누적 개수와 균등 정수 rank 등으로 수행하며 ‘처음 발견한 유효 셀’에 편향시키지 않는다. 배치 원 yaw는 검사하지 않는다.

이는 무작위 후보를 반복 검증하는 방법을 대체하지만 기하 유효성 검사 자체를 없애지는 않는다. WHITE 전체의 정확한 균등분포가 아니라, 각 단계에서 안전 셀의 합집합에 대한 균등분포다. 큰 물체부터 배치하는 순서와 보수적인 경계 제외가 분포에 영향을 준다.

### 6.2 실패 계약

안전 셀이0개인 경우 정상 완료로 처리하지 않는다. 실패한 env ID·seed·N·선택 ID/반지름·target/goal·이미 배치한 중심·실패 순서를 기록하고 명시적 오류를 반환한다. 진단 출력은 실패 시에만 host로 전송한다.

N 축소, 다른 body로 교체, target/goal 재추첨, 기존 후보/restart/pass 반복으로의 은밀한 fallback은 금지한다. 일부만 성공한 배치를 PhysX에 적용하지 않는다. 계산 실패가 manager/reset 전체의 transactional rollback을 보장한다는 뜻은 아니며, 해당 실행은 오류로 종료한다.

‘셀 없음’은 실제 연속 공간에 해가 없다는 증명이 아니다. 원의 보수성·격자 해상도·앞선 랜덤 배치의 공간 분절을 구분해 분석한다. 실패가 발생하면5mm 셀 세분화 또는 배치 방식 보완을 검증 단계에서 검토하고 명세에 반영한 뒤 적용한다. 반복 난수 재추첨으로 실패를 숨겨 분포를 바꾸지 않는다.

장기 학습 투입 조건은 §11의 사전검증 통과다. 임의 형상·개수에 대해 무재시도 완전 배치를 수학적으로 보장한다고 표현하지 않는다.

## 7. Warp IK 계약

기존 `ResetArmIK`의 USD 기반 고정/가동 joint frame과 EEF offset을 그대로 사용한다. 고정 joint를 접을 경우 기존 FK와 동등함을 먼저 검증한다. 비교 repo의 로봇 치수·solver 수치를 복사하지 않는다.

| 항목 | 보존값 |
| --- | --- |
| 초기 관절 | 현재 default seed |
| 목표 위치/자세 | 기존 목표 조건부 EEF 샘플러와 기본 orientation |
| 반복 상한 | 80 |
| DLS | `Jᵀ (JJᵀ + 0.02² I)⁻¹ e`에 해당하는 선형계 풀이 |
| 관절 변화 제한 | 각 반복 delta의 최대 절대성분0.15rad |
| 위치/회전 허용 오차 | 각각 `<0.0005m`, `<0.003rad` |
| 관절 제한 | 현재 joint position limits clamp |
| 품질/재추첨 | 현재처럼 SVD 검사 OFF, 목표 후보1회 |

inverse 행렬을 명시적으로 생성하지 않고 선형계를 푼다. quaternion 순서·정규화·axis-angle branch·작은 각도 처리를 기존 함수와 맞춘다. 환경별 커널 내부에서 FK/Jacobian/DLS를 반복하며 완료 행의 관절값은 고정한다. 반복마다 CPU 성공 여부를 읽지 않는다.

GPU 입출력은 관절각·valid·position_error·rotation_error다. 실제 관절 기록은 전체 계산 성공 후1회 수행한다. 최종 실패 검사에서 필요한1회 host 동기화는 허용한다. CPU 기준 solver는 검증용으로 유지하며 학습의 작은 batch를 자동 CPU 우회하지 않는다. unsupported backend는 명시적으로 구분하고 조용한 fallback은 두지 않는다.

수식 동등성을 요구하되 FP32 연산 순서 차이에 따른 bit-exact 일치는 요구하지 않는다. 수렴 경계에서 성공 판정이 달라지는 사례는 별도 분석하고 허용 오차를 임의로 완화하지 않는다.

## 8. 표시·캐시·상태 반영

학습 기본값에서는 IK 박스의 생성·좌표 갱신·GPU→CPU 전송·`visualize` 호출을 모두 건너뛴다. visibility만 OFF하고 기존 연산을 계속하지 않는다. play/진단의 명시적 debug ON은 지원하며, 학습 재현 설정에 flag를 기록한다. 다른 센서/marker는 이번 변경으로 일괄 비활성화하지 않는다.

리셋 계산에 필요한 shelf/robot 기준 pose는 복구할 default pose에서 가져온다. 실패 직전 shelf가 움직였더라도 그 위치를 새 배치 계산 기준으로 쓰지 않는다. 최종 상태 기록 전 계산을 수행할 수 있도록 world/local 변환을 분리한다.

```text
불변 geometry/IK 상수 준비(startup)
  → reset 대상의 target/goal/N/ID 추첨
  → 원 기반 배치 + Warp IK 계산
  → 성공 검사
  → shelf/robot root 복구, 최종 arm+기본 hand 관절 기록
  → 물체 최종 pose/zero velocity 기록, gravity/wake 적용
  → 필요한 link transform/sensor cache 갱신
  → 초기 가시성/관측 snapshot 및 native manager reset
  → 기존 episode metrics/action history 정리
```

기존 `reset_scene_to_default`의 기본 arm write 후 IK write를 합치되 root·hand·속도·position/velocity/effort target과 action reset의 최종 효과를 보존한다. native manager 순서를 임의로 재배치하거나 manager reset을 삭제하지 않는다. 추가 물리 step이나 settle simulation은 넣지 않는다.

gravity flag는 실제 변경된 행의 setter만 줄일 수 있다. 활성 물체 wake-up과 주차 물체의 중력 해제 의미는 보존한다. 타 환경의 flag·상태를 쓰지 않는다. scene 공유 kinematic 전환은 도입하지 않는다.

가시성에 필요한 고정 반경/geometry도 startup에 캐시하되 기존 가시성 수식을 그대로 사용한다. 배치 반지름 `R`로 가시성 반경을 바꾸거나 관측 노이즈를 캐시하지 않는다. 불변 default FK·limits 캐시에는 명시적 무효화 조건을 둔다. geometry/scale/관절 frame 변경 시 재생성하며 지원하지 않는 실행 중 변경은 오류로 알린다.

## 9. 설정과 코드 책임

기존 역할별 디렉토리와 파일을 유지한다. 명세상 설정명은 `max_obstacles=6`, `placement_clearance=0.01`, `layout_cell_size=0.005`, `layout_geometry_epsilon=1e-6`, `reset_ik_backend="warp"`, `debug_initial_ik_bounds=False`다.

대상 경로에서는 `max_gray_obstacles`, `max_white_obstacles`, `gray_padding`, `rear_offset`, 영역별 requested/actual count를 사용하지 않는다. `max_white_obstacles=6`처럼 기존 구역 할당을 이름만 바꿔 유지하지 않는다. RED/WHITE는 공간 설명에만 사용하며 개수 추첨은 단일 N이다. shared/legacy 경로에 필요한 옛 필드는 다른 환경 보존을 위해 남길 수 있으나 대상 runtime에 영향을 주지 않게 한다.

| 위치 | 변경 책임 |
| --- | --- |
| `envs/wrench_refactor_relative_ik_test_envs.py` | 대상 버전에 새 reset 설정/이벤트 선택, 부모 불변 |
| `assets/scenes/wrench_refactor_relative_ik_test.py` | 대상의 단일 개수 설정 수용,17body/16관측슬롯 보존 |
| `mdp/events/wrench_refactor_relative_ik_test.py` | 대상 전용 reset event 연결 |
| `mdp/event_functions/wrench_refactor_relative_ik_test.py` | 계산/최종 상태 기록/초기 snapshot 통합 |
| `mdp/common/wrench_refactor_layout.py` | 원 기반 배치 backend, 기존 OBB 경로 보존 |
| `mdp/common/wrench_refactor_ik.py` | 기존 수식의 Warp backend와 기준 solver |
| `runtime/wrench_refactor_relative_ik_test.py` | 대상 count 계약·debug gate·캐시 lifecycle, 기존 metrics 보존 |
| `tests/` | 기하·분포·IK 대조·부분 reset·범위 보존 검증 |

보상·종료·정책 모델 구현을 성능 최적화에 편승해 바꾸지 않는다. 새 reset 통계가 필요하면 진단 실행에 기록하고 기존 학습 Metrics 의미를 변경하지 않는다.

## 10. 난수와 재현성

N·ID·배치 셀·셀 내부 좌표·yaw는 seed에 의해 재현 가능해야 한다. target/goal/IK 샘플러의 분포는 보존한다. 기존 배치 RNG 호출 수가 달라지므로 이전 구현과 동일 seed의 전체 trajectory가 같다고 요구하지 않는다.

새 구현 내에서는 같은 seed·설정·reset 순서의 결과를 재현해야 한다. GPU buffer bucket/padding 변경으로 실제 환경의 난수를 추가 소비하지 않는다. 가능하면 layout과 goal/IK 난수 스트림을 분리하되 seed 매핑을 명시하고 테스트한다. 개수/ID 추첨을 성공하기 쉬운 구성으로 재가중하지 않는다.

## 11. 검증 및 완료 기준

### 11.1 정적·기하·통계

- 대상/부모/Reset-Test의 전체 EnvCfg·Manager·PPO 차이를 저장하고 요청된 항목만 달라짐을 확인한다.
- N0–6 각 확률1/7, 평균3을 확인한다. 기존 분포와 평균은 같지만 분산은2.5→4로 달라진다. ID 비복원 균등 선택과 반지름 정렬의 분리를 검증한다.
- 각 형상과 scale 양끝의 BBOX 모서리를 yaw 회전시켜 외접원 포함을 확인한다. 중심 offset과 scale 이중 적용을 검사한다.
- 독립 검사기로 원 간·RED·경계 침범, root↔center 왕복, 선반 바닥 정렬, 비활성 주차를 검사한다. 구현과 같은 mask 함수를 재호출하는 검사만으로 끝내지 않는다.
- RED 축퇴·모든 목표 방향·최소/최대 목표 거리·접선 경계·셀 모서리·N0/6·최대 반지름 조합을 포함한다.
- 실제 자산 geometry로 최소100,000개 초기 배치와 별도 최대 크기/방향 스트레스 표본을 검사한다. 모든 완료 표본의 actual=N, 충돌0, 실패0을 출시 기준으로 삼는다. 유한 표본 성공은 모든 입력의 가능성 증명이 아니다.
- 실패 표본이 나오면 원인과 수정 내용을 명세/로그에 남기고 전체 검사를 다시 수행한다. 실패 표본을 버리고 성공 표본만 집계하지 않는다.

### 11.2 IK와 실제 reset

- 같은 목표·seed·limits의 기존/Warp FK, Jacobian, 최종 pose, valid 판정을 batch1/4/8/16/64/128/2048에서 대조한다. 도달 불가능·관절 경계·회전 오차 경계를 포함한다.
- 모든 accepted 해는 원래 위치0.5mm/회전0.003rad 기준을 만족해야 한다. 관절각 차이·최대 오차·판정 불일치는 수치로 기록하고 해석한다.
- 실제 Isaac Sim에서 초기 전체 reset, 단일/부분/연속 reset, timeout/실패 자동 reset을 실행한다. 비선택 환경의 pose·속도·관절·물성·관측 cache는 보존한다.
- final arm+hand·root·속도·target, contact sensor/EEF frame·관측 snapshot·command·reward 상태·metrics를 확인한다. 유한 observation/reward와 오류 없는 rollout을 확인한다.

### 11.3 성능

`src/inspire_sweep_baseline/scripts/train.py`를 사용한다. 장비·환경 수·seed·checkpoint·policy 단계·dt/decimation·rollout·debug flag를 기록한다. 검증 출력은 `outputs`에 저장하고 `logs/rsl_rl`은 변경/정리하지 않는다.

기준선, 표시만 OFF, Warp IK, 원 배치, 중복 쓰기 제거를 단계별 측정한다. 기하 분포가 달라지는 원 배치 단계는 동일 trajectory A/B가 아님을 표시한다. component benchmark에는 동일 입력을 재생하고 end-to-end는 실제 자동 reset을 포함한다.

JIT/graph 준비·초기화와 steady-state를 분리하며 워밍업 후 최소100iteration, 가능하면3개 seed를 사용한다. Collection과 전체 iteration의 median/p95, reset batch 분포, 각 stage 시간, 메모리, 실패 수를 기록한다. 작은 batch1–16과 전체2048을 모두 측정한다.

성능 통과 조건은 동일 장비의 반복 측정에서 baseline 변동을 넘어 Collection과 전체 iteration 시간이 감소하는 것이다. 감소율을 실제 숫자로 보고하고 병목이 다른 곳으로 이동하면 명시한다. 수배 향상이나1–2초 달성을 사전에 보장하지 않는다.

## 12. 구현 순서와 인계

1. 대상 설정 snapshot과 실제 baseline 계측.
2. 학습 IK debug 경로 차단.
3. geometry/기본 FK/가시성 불변값 캐시와 독립 기하 검증.
4. Warp IK 구현·기준 solver 대조.
5. 단일 N 추첨·RED/WHITE 원 배치 구현 및 실패 표본 검증.
6. 중복 상태 기록 통합·부분 reset/manager 순서 검증.
7. 실제 train.py 비교와 전체 계약 대조, 환경 문서·개발 로그 갱신.

개발자는 배치 반지름 확장, RED margin 교체, 장애물 수 분포 변경이 과업 난이도에 영향을 준다는 점을 결과 해석에 포함한다. 학습 속도 개선과 정책 성공률 개선은 별도 검증이다.

현재 완료한 것은 요구/수식/범위/실패 정책/검증 기준의 문서화다. Warp 실행, 실제 원 배치 성공률, PhysX 동등성, Collection 개선은 모두 미검증이다.
