# Holding OSC · ObjectRandom · Final · Revision 9개 환경 비교

기준일: 2026-11-04. 요청한 experiment 9개의 **현재 기본 코드 설정**을 비교한다. 저장된 학습 실행의 Hydra override·체크포인트 설정·당시 코드까지 동일하다는 뜻은 아니다. 학습 성능 순위는 다루지 않는다.

[활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md) · [작성·검증 기록](../logs/2026-11-04_nine_environment_comparison.md)

## 비교 대상과 상속

표의 약칭은 이 문서에서만 사용한다. 사용자가 지정한 문자열은 Gym ID가 아니라 PPO의 `experiment_name`이다.

| 약칭 | 요청한 experiment_name | Gym ID | EnvCfg와 직접 부모 |
| --- | --- | --- | --- |
| H2 | `inspire_contact_sweep_clutter_fusion_holding_osc_v2` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v2` | `FusionHoldingOSCV2EnvCfg` → `FusionHoldingV2EnvCfg` |
| O1 | `inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v1` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v1` | `FusionHoldingOSCObjectRandomV1EnvCfg` → `FusionHoldingOSCV2EnvCfg` |
| O2 | `inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v2` | `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v2` | `FusionHoldingOSCObjectRandomV2EnvCfg` → `FusionHoldingOSCV3EnvCfg` |
| F1 | `inspire_final_v1` | `Isaac-Inspire-Final-v1` | `FinalV1EnvCfg` → `FinalEnvCfg` |
| F2 | `inspire_final_v2` | `Isaac-Inspire-Final-v2` | `FinalV2EnvCfg` → `FinalV1EnvCfg` |
| A1 | `inspire_final_goal_accuracy_v0_1` | `Isaac-Inspire-Final-GoalAccuracy-v0_1` | `FinalGoalAccuracyV0_1EnvCfg` → `FinalGoalAccuracyEnvCfg` |
| A2 | `inspire_final_goal_accuracy_v0_2` | `Isaac-Inspire-Final-GoalAccuracy-v0_2` | `FinalGoalAccuracyV0_2EnvCfg` → `FinalGoalAccuracyV0_1EnvCfg` |
| R0 | `inspire_revision_v0` | `Isaac-Inspire-Revision-v0` | `RevisionEnvCfg` → Isaac Lab `ManagerBasedRLEnvCfg` |
| RT1 | `inspire_revision_test_v1` | `Isaac-Inspire-Revision-Test-v1` | `RevisionV1TestEnvCfg` → `RevisionV1EnvCfg` → `RevisionEnvCfg` |

O2는 O1의 직접 자식이 아니다. Holding-v3의 보상을 OSC-v3를 통해 받고, ObjectRandom의 Scene/Event를 조합한다. Final-v0와 Revision-v0는 독립 EnvCfg 구성이다. Revision은 A2를 기능 기준으로 삼았지만 Final EnvCfg/runtime을 상속하지 않는다. RT1을 R0와 비교할 때는 **Revision-v1의 보상·커리큘럼 변경과 Test의 원통 타겟 고정**을 모두 포함해야 한다.

근거: [등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py), [Holding OSC 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/contact_sweep_clutter_fusion_holding_osc_envs.py), [ObjectRandom 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/contact_sweep_clutter_fusion_holding_osc_object_random_envs.py), [Final 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/final_envs.py), [Revision 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/revision_envs.py).

## 1. 씬 구성 방법

### 1.1 공통 과업과 생성 시점

UR10 계열 Arm과 Inspire Hand로 선반 위 타겟을 목표 XY 위치로 민다. 작업면은 선반 좌표계에서 약 0.40×1.00m, 높이 1.05m다. 타겟 1개와 Gray/White 장애물을 구분하며, 물리적으로 미리 생성한 물체 중 이번 episode에 사용할 물체만 활성화한다. 비활성 물체는 원격 주차하고 중력을 끄며 active mask로 과업 계산에서 제외한다.

**물리 생성 용량, 커리큘럼 요청 수, 배치 후 실제 활성 수, 관측 슬롯 수는 서로 다르다.** 아래 물리 개수는 로봇·선반을 제외한 타겟/장애물 rigid object 수다.

| 환경 | 타겟 형상 | 장애물 형상 | 물리 생성 용량 | 장애물 요청 수 G/W | 타겟 초기 위치 |
| --- | --- | --- | ---: | --- | --- |
| H2 | 고정 원통, 반경 4cm·높이 10cm | 원통 | 11 = 1+5+5 | 1/1 → 5/5 | 선반 중심 반경 2cm 원판 |
| O1 | H2와 동일한 원통 | YCB 4종×3개 크기 variant | 17 = 1+8+8 | 1/1 → 8/8 | 중심 반경 2cm |
| O2 | O1과 동일 | O1과 동일 | 17 = 1+8+8 | 1/1 → 6/6 | 중심 반경 2cm |
| F1 | 원통/큐브/랜덤 prop 그룹을 각 1/3로 선택 | YCB 12 variant + 머그·병 | 21 = 1+10+10 | 1/1 → 8/8 | 중심 반경 2cm |
| F2 | F1과 동일 | F1과 동일 | 21 | 1/1 → 8/8 | 중앙 80%와 형상·접근 안전영역의 교집합 |
| A1 | F1 분포 유지; cube variant만 6×8×10cm 직육면체로 변경 | F1과 동일 | 21 | 1/1 → 4/5 | F1과 동일 |
| A2 | A1과 동일 | A1과 동일 | 21 | 1/1 → 4/5 | A1과 동일 |
| R0 | 원통·직육면체·머그·병·YCB 4종, 총 8종 | 타겟과 같은 8종 후보 | 10 = 1+4+5 | 1/1 → 4/5 | 중심 반경 2cm |
| RT1 | 원통 고정; 크기 랜덤화 유지 | R0와 동일 | 10 | 3/3 → 4/5 | R0와 동일 |

A1/A2는 **타겟 전체를 직육면체로 고정하지 않는다.** 선택 목록의 cube 크기만 바꾼다. F2의 중앙 80%는 선반 중심 기준 X±0.16m, Y±0.40m이며, 실제 추출 영역은 물체 크기와 2cm edge clearance 등으로 더 줄어든다.

### 1.2 형상·크기·물성 랜덤화

| 항목 | H2 | O1·O2 | F1·F2·A1·A2 | R0·RT1 |
| --- | --- | --- | --- | --- |
| 종류 선택 | 고정 원통 | 생성 시 장애물 YCB 선택 | 생성 시 타겟·장애물 선택 | 생성 시 물체별 8종 선택; RT1 타겟만 override |
| 크기 | 고정 | 기존 1.5배 확대 기반 YCB의 0.8/0.9/1.0 variant | 기존 variant에 추가 U(0.9,1.1) | 중앙 0.9에 해당하는 기준 형상에 U(0.9,1.1) 한 번 |
| episode 사이 종류/크기 | 유지 | 유지 | 유지 | 유지 |
| reset 시 갱신 | 배치·물성·활성 구성 | 배치·yaw·물성·활성 구성 | 배치·yaw·물성·활성 구성 | 배치·장애물 yaw·물성·활성 구성 |
| 높이 정렬 | 원통 기준 | 형상 bounds 반영 | 확대된 local min-Z 반영 | 확대된 local min-Z 반영 |

물성은 reset에서 질량·마찰을 재추출한다. O1 이후 형상별 관성/질량 비율을 보존하는 물성 함수를 사용한다. 종류·scale을 매 reset 재추첨하는 후속 A2_1이나 후보 풀은 이번 A2에 포함되지 않는다. Revision의 target index는 0으로 유지하며, 16개 관측 슬롯 때문에 16개 장애물을 물리 생성하지 않는다.

### 1.3 배치 알고리즘

H2는 원통 기반 population scene generator를 사용한다. O1/O2는 큰 YCB 형상을 반영하는 `randomize_large_prop_scene`으로 바꾸며, 형상별 footprint와 OBB 비겹침을 검사한다. O2에는 Gray 영역 확대 일정이 추가된다.

F1/F2/A1/A2의 `randomize_final_scene`은 형상·scale을 반영해 타겟과 목표를 정하고 기존 영역 배치에 회전 OBB 비겹침 검사를 결합한다. 요청 수로 배치하지 못한 행은 White, Gray를 번갈아 줄이는 fallback을 사용한다. 따라서 요청한 8/8 또는 4/5가 실제로 모두 놓인다는 보장은 없다. 목표는 방향의 선반 내부 여유에 따라 최대 15cm, 최소 5cm를 확보하며, 무조건 5~15cm 균일 추출이라는 뜻은 아니다.

R0/RT1은 `bbox_scene_layout.generate_layout`을 사용하는 텐서 OBB 배치다. RED는 타겟 이동과 손목 접근에 필요한 금지 영역, Gray는 그 주변과 뒤쪽 접근 영역, White는 나머지 영역이다. **Gray padding은 길이 65mm로 고정**한다. 후보 배치·재시도 결과 중 유효 배치를 선택하고 실제 개수 및 완전 배치 여부를 따로 기록한다. Final의 `0→0.15` padding은 Red 반경 대비 비율이므로 Revision의 65mm와 같은 단위가 아니다.

근거: [ObjectRandom Scene](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/contact_sweep_clutter_fusion_holding_osc_object_random.py), [Final Scene](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/final.py), [Final reset](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/final.py), [Revision Scene](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/revision.py), [Revision spawner](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/revision_spawners.py), [Revision layout](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/revision_layout.py).

## 2. 관측

### 2.1 차원과 Actor/Critic 정보 경계

9개 모두 Actor는 초기 타겟·초기 장애물 정보와 실행 중 로봇·촉각·F/T 정보를 사용한다. 실시간 타겟 XYZ는 Critic 전용이다. 이번 RT1은 GT Actor 변형이 아니다.

| 환경 | policy | 장애물 슬롯/원시 차원 | Actor 원시 합계 | Critic 원시 합계 | encoder 이후 Actor/Critic MLP 입력 | Critic의 장애물 |
| --- | ---: | --- | ---: | ---: | --- | --- |
| H2 | 55D | 16 / 64D | 119D | 122D | 71D / 74D | Actor와 같은 초기 정보 |
| O1 | 55D | 16 / 64D | 119D | 122D | 71D / 74D | 초기 정보 |
| O2 | 55D | 16 / 64D | 119D | 122D | 71D / 74D | 초기 정보 |
| F1 | 57D | 20 / 80D | 137D | 140D | 73D / 76D | 초기 정보 |
| F2 | 57D | 20 / 80D | 137D | 140D | 73D / 76D | 초기 정보 |
| A1 | 57D | 20 / 80D | 137D | 140D | 73D / 76D | 초기 정보 |
| A2 | 57D | 20 / 80D | 137D | 140D | 73D / 76D | 초기 정보 |
| R0 | 57D | 16 / 64D | 121D | 124D | 73D / 76D | 매 관측 현재 활성 장애물 |
| RT1 | 57D | 16 / 64D | 121D | 124D | 73D / 76D | 매 관측 현재 활성 장애물 |

장애물 한 슬롯은 `[present,x,y,z]` 4D다. Actor와 Critic은 별도 장애물 encoder를 사용하고, 각 encoder가 입력을 16D로 압축한다. Revision Critic은 초기 장애물과 현재 장애물을 모두 이어 붙이는 것이 아니라 **현재 장애물 그룹으로 대체**한다.

### 2.2 policy 관측 내용·순서

| 채널 | H2·O1·O2 | F1·F2·A1·A2 | R0·RT1 |
| --- | --- | --- | --- |
| Arm 위치/속도 6+6D | default 대비 상대값 | 동일 | 실제 관절각·관절속도 |
| Hand 상태 2D | 없음 | 실제 관절에서 계산한 flexion/opposition openness | 동일 |
| EEF pose 7D | robot root 기준 위치3+quaternion4 | 동일 | 동일 |
| 타겟 3D | 초기 root-frame 위치 | 동일 | 동일 |
| 목표 2D | 초기 root-frame 극좌표 | 동일 | 동일 |
| 이전 행동 8D | `bounded_last_action` | Arm·Hand 전체 raw action에 tanh | Final과 동일 |
| 촉각 17D | 접촉 bit, threshold 0.01N | 동일 + bit flip | Final과 동일 |
| 손목 F/T 6D | 보정 wrench | 동일 + Gaussian noise | Final과 동일 |

H2/O1/O2의 순서는 Arm 위치→Arm 속도→이전 행동→초기 타겟→EEF→목표→촉각→F/T다. Final은 이 순서를 유지하고 Hand 상태를 추가한다. Revision은 Arm 위치→Arm 속도→Hand 상태→EEF→초기 타겟→목표→이전 행동→촉각→F/T 순서다. 따라서 57D가 같아도 Final과 Revision의 채널 의미·배열이 동일하지 않다.

### 2.3 노이즈와 초기 캐시

- 초기 타겟 위치에는 축별 ±1cm episode bias를 사용한다. 초기 장애물도 reset에서 ±1cm 좌표 노이즈와 가시성 판정·1% 가시성 반전·10% 인접 교환을 반영한 뒤 캐시한다. Actor의 물체 위치가 이후 실제 움직임을 추적하지 않는다.
- F1 이후 촉각에 셀별 1% bit flip, F/T에 힘 σ=0.05N·모멘트 σ=0.005N·m의 관측 노이즈를 더한다. H2/O1/O2에는 이 추가 센서 노이즈가 없다. 보상 계산용 원본 접촉/센서와 관측 노이즈는 구분한다.
- Revision Critic의 장애물 좌표는 robot root frame의 현재값이며 좌표 노이즈·가시성 필터·가시성 반전이 없다. 활성 장애물만 넣고 타겟·주차 물체는 제외한다. 다만 Y 기준 정렬과 10% 인접 교환은 매 관측 수행하므로 입력 순서는 확률적으로 바뀔 수 있다.
- Critic도 policy 그룹을 공유하므로 모든 Critic 입력이 noise-free라는 뜻은 아니다. 추가 현재 타겟 XYZ와 Revision의 현재 장애물 좌표가 noise-free다.

근거: [Holding 관측](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/contact_sweep_clutter_fusion.py), [Final 관측](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/final.py), [Revision 관측](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/revision.py), [Revision 관측 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/revision.py).

## 3. 보상

### 3.1 핵심 양의 보상

아래 `w`는 RewardManager weight다. 일반적인 연속 보상은 `w × 함수값 × step_dt`로 누적된다. 진행량 및 일회성 보상 함수는 내부에서 dt를 상쇄하므로 `+30`을 매초 지급률로 읽으면 안 된다. `d`는 타겟–목표 XY 거리, `v`는 타겟 속력, `r`은 목표 반경이다.

| 환경 | EEF 접근 | 목표 거리 | Hold | 접촉 | 일회성 보너스 |
| --- | --- | --- | --- | --- | --- |
| H2 | 최단 접근 개선, 10cm·w30 | 새 최단 XY 거리 개선·w100 | r 이내 Gaussian·w4 | 전체 Hand 접촉 OR 목표 점유·w1.45 | 없음 |
| O1 | H2와 동일 | 동일 | 동일 | 동일 | 없음 |
| O2 | H2와 동일 | 동일 | H2 식, episode 누적 지급시간 3초 상한 | 동일 | 없음 |
| F1 | 평소 10cm, 목표 점유 시 1m로 완화·w30 | 최단 거리 개선·w100 | 중심 가중 + 2r까지 외곽 Gaussian·w4 | 전체 Hand 접촉 OR 목표 점유·w1.45 | 없음 |
| F2 | F1과 동일 | 동일 | 동일 | 동일 | 없음 |
| A1 | 고정 10cm·w30 | exp(-d/0.05)·w3.7 | r=2cm, 외곽6cm·w8 | 타겟–Hand 접촉 OR 목표 점유·w1.45 | 없음 |
| A2 | A1과 동일 | 동일 | 동일 | 동일 | 만료 성공 +30, 단 d<2cm |
| R0 | 고정 10cm·w30 | A1과 동일 | r=3cm, 외곽8cm·w8 | 실제 타겟 접촉 AND EEF 높이<120mm·w1.45 | 만료 성공 +30, d≤3cm |
| RT1 | R0와 동일 | 동일 | d<3cm 내부 Gaussian만·w8, 속력≤5cm/s 무감쇠 | R0와 동일 | 최초 d<3cm 진입 +30, 만료 d≤3cm +40 |

접촉 힘 기준은 0.01N이다. Revision 높이는 초기 선반 작업면 대비 EEF 높이이며, 타겟 종류·높이나 이후 선반 이동에 따라 바뀌지 않는다. R0/RT1에서 이 높이 조건은 **접촉 보상**에 적용된다. 목표 거리·Hold에도 95mm 제한을 적용하는 Revision-v2 규칙을 RT1에 가져오면 안 된다.

O2의 3초 상한은 **누적 보상 지급시간**이다. 목표 밖으로 나갔다 돌아와도 소진한 예산이 복원되지 않는다. 반면 성공 종료의 3초는 속도 조건까지 만족하는 연속 체류시간이므로 별도 상태다.

### 3.2 Hold 식 비교

유효한 타겟에 대해 H2/O1의 raw Hold는 다음과 같다. O2는 같은 값에 잔여 지급시간 제한을 적용한다.

```math
H=\mathbf{1}_{d\le r}\exp\left[-\ln 2\left((d/r)^2+(v/s)^2\right)\right]
```

F1/F2는 위 Gaussian을 `d≤2r`까지 지급하고 `d<r`에서 `1+(1-d/r)^2`를 곱한다. 반경과 속도 scale `s`는 커리큘럼으로 줄어든다.

A1/A2/R0는 안쪽 중심 가중 Gaussian과 바깥쪽 제곱 꼬리를 연결한다. A1/A2는 `(r,R)=(0.02,0.06)m`, R0는 `(0.03,0.08)m`, 속도 scale은 모두 0.05m/s다.

```math
H(d,v)=
\begin{cases}
\exp[-\ln2(d/r)^2]\left[1+(1-d/r)^2\right],&d\le r\\
\frac12\left[\max\left(0,\frac{R-d}{R-r}\right)\right]^2,&d>r
\end{cases}
\times\exp[-\ln2(v/0.05)^2]
```

RT1은 다음 식을 사용한다. 정확히 3cm에서 Hold는 0이지만 만료 성공은 인정한다. 중심 정지 시 raw 값은 2이므로 w8 적용 최대 Hold 지급률은 16/초다. A1/A2/R0도 중심 정지 시 같은 최대 지급률을 가진다.

```math
H=\mathbf{1}_{d<0.03}\,2\exp[-4\ln2(d/0.03)^2]
\exp\left[-\ln2\left(\max(0,v-0.05)/0.05\right)^2\right]
```

### 3.3 비용 항과 구성 차이

| 비용 | H2·O1·O2 | F1·F2·A1·A2·R0 | RT1 |
| --- | --- | --- | --- |
| 행동 변화 | Arm/Hand 분리, 각각 −0.03 | `action_rate_penalty` 계열로 병합; 내부 각각 −0.03 | R0 유지 |
| 관절 속도 제곱 | Arm −0.03, Hand −0.01 분리 | 병합; 내부 계수 유지 | R0 유지 |
| Arm 초과속도·EEF 선속도 | 각각 −1, 무료속도 일정 | 두 전용 항 제거; 관절속도 제곱 비용은 유지 | 없음 |
| 물체 기울기·장애물 변위 | `object`, 기울기 −30·변위 실효 −150 | 가속도까지 `object_penalty`에 병합 | 기울기 −30, 변위 −150, 가속도 −0.05의 3개 항 |
| 가속도 비용 | 별도 항, weight 0→−0.05 | 병합 내부 weight 0→−0.05 | 무료 가속도20m/s²·weight−0.05 고정 |
| 타겟 속도 비용 | `pushing_speed`, −5 | 이름 변경, −5 유지 | 동일 |
| 선반 비용 | collision −0.5 + failure 사건 −3 | `shelf_penalty`에 병합 | 동일 |
| 장애물 접촉 비용 | 0→−0.1 schedule | 0→−0.1 schedule | 무료힘50N·weight−0.05 고정 |
| 손목 wrench 변화 | 0→−0.1, 누적 양의 보상 5% 예산 제한 | 같은 예산 제한 | weight−0.1 고정, **양의 보상 예산 제한 제거** |

공통 기울기 무료 구간은 5°, 포화 기준은 0.9rad다. 장애물 변위는 초기 위치 대비 3D 변위 제곱합에 상한 0.04를 적용한다. RT1은 wrench의 예산 제한만 없애고 raw 지수 곡선의 상한은 유지한다. 선반 변위만으로 종료될 때 collision 사건 보상 −3이 자동 추가되는 것은 아니다.

A2의 만료 보너스는 성공 term에 더해 `d<0.02`를 검사한다. 따라서 정확히 2cm는 성공으로 집계되지만 +30은 없다. RT1의 최초 진입 보너스는 episode당 한 번이며 실패와 같은 step에 진입해도 지급될 수 있다. 보너스와 실패 없는 안정적 성공을 동일시하지 않는다.

근거: [Holding 보상](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/contact_sweep_clutter_fusion_holding.py), [Holding 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/contact_sweep_clutter_fusion_holding_scheduled.py), [Final 보상](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/final.py), [Final 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/final.py), [Revision 보상](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/revision.py), [Revision 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/revision.py).

## 4. 커리큘럼

모든 iteration은 runner의 절대 learning iteration이다. 물체 개수·배치는 reset에 반영한다. 표의 시작점/종료점 사이 값은 해당 함수의 구간별 선형 보간과 갱신 간격을 따른다. 매 step 연속 변화라는 뜻이 아니다.

### 4.1 장애물 개수·Gray 영역·목표 반경

| 환경 | 초기 G/W | Gray 첫 증가/간격/상한 도달 | White 첫 증가/간격/상한 도달 | 최종 G/W | Gray padding | 목표 반경 |
| --- | --- | --- | --- | --- | --- | --- |
| H2 | 1/1 | 4500 / 3000 / 13500 | 3000 / 3000 / 12000 | 5/5 | 추가 확대 일정 없음 | 2cm→1cm→0.5cm |
| O1 | 1/1 | 4500 / 3000 / 22500 | 3000 / 3000 / 21000 | 8/8 | 추가 확대 일정 없음 | H2와 동일 |
| O2 | 1/1 | 4000 / 2000 / 12000 | 3000 / 2000 / 11000 | 6/6 | 6000:0 →12000:0.15, 간격250 | H2와 동일 |
| F1 | 1/1 | 3000 / 2000 / 15000 | 2000 / 2000 / 14000 | 8/8 | 4000:0 →10000:0.15, 간격1000 | 4000:2cm →10000:1cm |
| F2 | 1/1 | F1과 동일 | F1과 동일 | 8/8 | F1과 동일 | F1과 동일 |
| A1 | 1/1 | 2500 / 1000 / 4500 | 2000 / 1000 / 5000 | 4/5 | F1과 동일 | 2cm 고정 |
| A2 | 1/1 | A1과 동일 | A1과 동일 | 4/5 | A1과 동일 | 2cm 고정 |
| R0 | 1/1 | A1과 동일 | A1과 동일 | 4/5 | 65mm 고정, 일정 없음 | 3cm 고정 |
| RT1 | 3/3 | 12000 / 4000 / 12000 | 10000 / 4000 / 14000 | 4/5 | 65mm 고정 | 3cm 고정 |

H2/O1/O2 반경 일정의 정확한 점은 `(0,2cm),(5000,2cm),(10000,1cm),(20000,0.5cm)`이고 간격은 1 iteration이다. RT1 개수는 `0:3/3 →10000:3/4 →12000:4/4 →14000:4/5`다.

### 4.2 보상 파라미터 일정

| 항목 | H2·O1·O2 | F1·F2 | A1·A2·R0 | RT1 |
| --- | --- | --- | --- | --- |
| 타겟 무료속도 | 0:.10, 499:.10, 500:.09, 1900:.02m/s; 간격250 | 동일 | 동일 | 동일 |
| Arm 무료속도 | 0:1, 499:1, 500:.98, 3300:.7rad/s; 간격250 | 없음 | 없음 | 없음 |
| EEF 무료속도 | 0:1.5, 499:1.5, 500:1.48, 13300:.2m/s; 간격250 | 없음 | 없음 | 없음 |
| Hold 속도 scale | 0:.05, 6000:.05, 10000:.02m/s; 간격250 | 동일 | .05m/s 고정 | free=.05, scale=.05 고정 |
| 무료 가속도 | 0:50, 3000:50, 6000:30, 10000:30, 12000:20; 간격250 | 3000:50→10000:20; 간격1 | F1과 동일 | 20 고정 |
| 가속도 weight | 0:0, 1000:0, 3000:−.01, 6000:−.03, 10000:−.03, 12000:−.05; 간격250 | 3000:0→10000:−.05; 간격1 | F1과 동일 | −.05 고정 |
| wrench 무료힘 변화 | 0:50, 3000:50, 6000:30, 10000:30, 12000:20N; 간격250 | 3000:50→10000:20; 간격250 | F1과 동일 | 20N 고정 |
| wrench 무료모멘트 변화 | 위 무료힘 수치의 1/10 N·m | 3000:5→10000:2; 간격250 | F1과 동일 | 2N·m 고정 |
| wrench weight | 0:0, 1000:0, 3000:−.03, 6000:−.1; 간격250 | 동일 | 동일 | −.1 고정 |
| 장애물 무료접촉힘 | 0:80, 3000:80, 6000:50, 10000:50, 12000:30N; 간격250 | 동일 | 동일 | 50N 고정 |
| 장애물 접촉 weight | 0:0, 1000:0, 3000:−.02, 6000:−.05, 10000:−.05, 12000:−.1; 간격250 | 동일 | 동일 | −.05 고정 |
| 목표 방향 deadzone | ±X 주변 제외각30°를 3000까지 유지, 이후500마다5° 감소; 3500 첫 감소·6000에0° | 동일 | 동일 | 동일 |

RT1은 R0의 가속도 2개·장애물 접촉 2개·wrench 3개, 총 7개 schedule을 제거하고 **R0의 10000 iteration 값**으로 고정한다. R0의 최종 12000 값과는 다르다. RT1에 남는 것은 장애물 개수, 타겟 무료속도, 목표 방향 deadzone의 3개 curriculum이다.

`scheduled_value`는 구간 시작점 기준으로 interval을 양자화한다. 예를 들어 타겟 무료속도는 코드상 종료점이 1900이어도 직전 구간에서 값이 계단식으로 변한다. 표의 숫자는 코드의 schedule knot이며 매 iteration의 선형값을 임의로 추정하면 안 된다.

근거: [Holding 일정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/contact_sweep_clutter_fusion_holding.py), [ObjectRandom 일정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/contact_sweep_clutter_fusion_holding_osc_object_random.py), [Final 일정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/final.py), [Revision 일정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curricula/revision.py), [schedule 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/curriculum_functions/contact_sweep_clutter_fusion_holding.py).

## 5. 터미네이션

### 5.1 성공과 시간 만료

| 환경 | 성공 시점 | 거리 조건 | 추가 성공 조건 | 시간 한계 |
| --- | --- | --- | --- | --- |
| H2 | 조건 충족 즉시 조기 종료 | d≤현재 r, 2→1→0.5cm | 타겟 속력≤0.01m/s로 연속3초, 실패 배제 | 최대10초 |
| O1 | H2와 동일 | 동일 | 동일 | 최대10초 |
| O2 | H2와 동일 | 동일 | 동일; Hold 지급 상한과 별도 | 최대10초 |
| F1 | 10초 만료에서만 성공/미달 분류 | d≤현재 r, 2→1cm | 속도·체류시간 조건 없음 | 10초 |
| F2 | F1과 동일 | 동일 | 동일 | 10초 |
| A1 | 만료에서만 | d≤2cm | 속도·체류시간 조건 없음 | 10초 |
| A2 | A1과 동일 | d≤2cm | 보너스만 strict d<2cm | 10초 |
| R0 | 만료에서만 | 유한한 d≤3cm | 속도·체류시간 조건 없음 | 10초 |
| RT1 | R0와 동일 | 유한한 d≤3cm | 최초 진입 보너스로 조기 종료하지 않음 | 10초 |

Final/Accuracy/Revision의 성공 만료와 미달 만료는 모두 `time_out=True`인 truncation이다. value bootstrapping을 유지한다. 실패는 어느 시점에서든 episode를 끝낼 수 있다. 만료 성공 함수는 위치 기반 분류이므로 동일 step에 실패 term이 켜졌는지는 별도로 보아야 한다.

### 5.2 실패 조건

| 조건 | H2·O1·O2·F1·F2·A1·A2 | R0·RT1 |
| --- | --- | --- |
| 활성 물체 낙하/기울기 | 물체 root 높이 기준1.04m 및 기울기0.9rad | 실제 bounds 바닥이 선반면보다1cm 이상 내려감 또는 기울기0.9rad; 비유한 바닥도 실패 |
| 타겟 고속 | `push_fast` 계열, speed_condition=1.0m/s | 동일 |
| Arm 관절 고속 | threshold=5.0rad/s | 동일 |
| 선반 충돌 | threshold=.1, check_fingers=False, wrist_clearance=.03m | 동일 |
| 선반 변위 | threshold=.05m | 동일 |

Holding은 선반 충돌/변위를 별도 term으로 두고 Final 이후는 하나의 shelf 실패 term으로 묶는다. Holding의 `hand_velocity`라는 이름도 실제 검사 대상은 Arm 관절이다. Revision은 물체 형상·scale을 반영하는 바닥 판정으로 바꿨으므로 root 높이가 서로 다른 에셋을 같은 1.04m로 비교하지 않는다.

근거: [Holding 종료](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations/contact_sweep_clutter_fusion_holding.py), [Final 종료 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/terminations/final.py), [Final 종료 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/final.py), [Revision 종료 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/revision.py).

## 6. 기타

### 6.1 행동·제어·학습

9개 환경의 행동은 Arm 상대 pose 6D + Hand openness 2D의 8D다. Arm은 robot base 기준 OSC, 위치 scale0.03m·회전 scale0.15rad, 위치/회전 stiffness100/50, damping ratio1, 관성 분리·중력 보상을 사용한다. Arm의 경쟁 joint PD gain은 0이다. 센서 기반 정책이지만 별도의 wrench 목표를 지시하는 force-control action은 아니다.

시뮬레이션 dt는 0.01초, decimation2로 정책 dt는 0.02초(50Hz), 최대10초는 500 control step이다. 기본 환경 수는 Holding/ObjectRandom/Final 계열4096, Revision2048이며 실행 인자로 바꿀 수 있다.

PPO의 주요 값은 공통이다: rollout36 step, Actor/Critic MLP `[256,128,64]`·ELU, 장애물 encoder hidden32·ReLU·embedding16, gamma0.98, lambda0.95, learning rate0.001 adaptive, clip0.2, epoch8, minibatch4, entropy0.005. 다만 encoder 입력 크기와 관측 의미는 2절처럼 다르므로 동일 학습 파라미터가 checkpoint 호환성을 뜻하지 않는다.

학습 진입점은 `src/inspire_sweep_baseline/scripts/train.py`다. 해당 experiment의 실제 run을 재현하려면 Gym ID 외에도 저장된 환경·runner 설정, seed, 코드 revision과 자산을 대조해야 한다.

### 6.2 계측·해석 시 주의할 차이

Accuracy와 Revision은 거리·EEF/타겟 속도·타겟 가속도·실제 장애물 수·F/T 최대값 등 runtime metric을 기록한다. 총 보상만으로 정확도를 비교하면 거리 보상 형태, Hold 지급시간, 만료 보너스, wrench 예산 제한의 차이가 섞인다. 성공률 비교 역시 Holding의 연속 정지 성공과 Final/Revision의 만료 위치 성공을 같은 지표로 취급하면 안 된다.

RT1의 임시 EEF 높이 print와 90/95/100mm 시각화 면은 현재 주석 처리되어 있다. 현재 RT1 과업 설정은 Revision-v1에서 타겟 종류만 원통으로 바꾸며, 크기와 장애물 랜덤화는 유지한다.

현재 코드와 이전 설명이 다른 주요 항목은 다음과 같다.

- A1/A2 Reaching은 **10cm**다. 초기 명세의 20cm 표기를 현재값으로 사용하지 않는다.
- A1/A2 장애물 최종 요청 수는 **4/5**다. 과거 문서에 남은 8/8 증가 일정을 적용하지 않는다.
- A2는 **strict 2cm 만료 +30**이다. A2_1의 inclusive +75·타겟 후보 풀·새 OBB reset을 적용하지 않는다.
- RT1은 **120mm 접촉 높이**, 내부 Gaussian Hold, 최초 +30·만료 +40이다. Revision-v2의95mm·Smoothstep·+25/+75와 구분한다.

근거: [Final PPO](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/final_ppo_cfg.py), [Revision PPO](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/revision_ppo_cfg.py), [Final runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/final.py), [Revision runtime](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/revision.py).

## 최종 요약 테이블

원시 관측은 Actor/Critic 순서, G/W는 커리큘럼의 최종 **요청** 수다. 실제 배치 개수는 더 적을 수 있다.

| 환경 | 씬 구성 핵심 | 관측 A/C | 보상 핵심 | 커리큘럼 핵심 | 터미네이션 핵심 | 기타 핵심 |
| --- | --- | --- | --- | --- | --- | --- |
| H2 | 원통 장면·물리11개 | 119/122D, 초기 장애물16슬롯 | 거리 개선 + 내부 Hold w4 + Hand 접촉/목표 점유 | G/W5/5, 반경2→0.5cm | 저속 연속3초 조기 성공 | 비교군 중 기본 원통 OSC |
| O1 | YCB 장애물·물리17개 | H2 동일 | H2 동일 | G/W8/8, 반경2→0.5cm | H2 동일 | H2에 장애물 형상 다양성 추가 |
| O2 | O1과 같은 물리17개 | H2 동일 | Hold 누적 지급3초 제한 | G/W6/6, Gray 비율0→.15 | H2 동일 | 보상 지급3초와 성공 체류3초는 별도 |
| F1 | 타겟 다양화·±10%·물리21개 | 137/140D, 초기 장애물20슬롯 | 중심/외곽 Hold·비용 병합·Arm/EEF 추가속도 항 제거 | G/W8/8, 반경2→1cm | 10초 만료 위치 성공 | Hand 상태·센서 노이즈 추가 |
| F2 | F1 + 타겟 중앙80% 안전영역 | F1 동일 | F1 동일 | F1 동일 | F1 동일 | F1 대비 과업 차이는 타겟 초기 위치 |
| A1 | F1 + cube variant6×8×10cm | F1 동일 | 지수 거리w3.7·Hold2/6cm·타겟 접촉/목표 점유 | G/W4/5, 반경2cm 고정 | 만료 d≤2cm | Reaching 현재10cm |
| A2 | A1 동일 | F1 동일 | A1 + 만료 +30(d<2cm) | A1 동일 | A1 동일 | 성공 경계와 보너스 경계가 다름 |
| R0 | 8종·중앙크기±10%·물리10개·OBB | 121/124D, Critic 현재 장애물 | Hold3/8cm·실제 접촉+높이<120mm·만료+30 | G/W4/5, Gray65mm·반경3cm 고정 | 만료 d≤3cm, bounds 낙하 | 독립 구성·실제 Arm 관측 |
| RT1 | R0 장면, 타겟 원통 고정 | R0 동일 | 내부 Gaussian Hold·최초+30/만료+40·비용3분리·wrench budget 제거 | 3/3→4/5, 7개 schedule을10k 값으로 고정 | R0 동일; Hold/진입은d<3cm | R0 대비 Revision-v1 변경까지 포함 |

이 문서는 현재 코드의 정적 대조 결과다. 새 시뮬레이션·학습·성능 실험은 수행하지 않았다. 보상이나 씬 변경의 설계 의도를 학습 성능 향상으로 해석하지 않는다.
