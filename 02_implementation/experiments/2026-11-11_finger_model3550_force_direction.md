# 2026-11-11 Finger model3550: 핸드가 타겟에 가하는 합력의 방향

## 결과와 판단

**접촉 중 합력 방향은 실제 밀기 구간에서 초기 위치→목표 방향과 대체로 정렬된다. 방향 보상은 보조항 후보로 타당하지만, 이 관측만으로 학습 개선을 입증한 것은 아니다.**

실제 GPU PhysX play에서 seed42의128환경×10회, seed123의32환경×6회, 총 **1,472개 완료 에피소드·1,427,392개 물리 샘플**을100Hz로 수집했다. 접근·최초 목표 도달 이후·약한 힘·정지 상태를 제외한 **19,273개 샘플, 1,445개 에피소드**에서 수평 코사인 평균 **0.8528**, 중앙값 **0.9493**이었다. 목표 방향과30도 이내72.83%, 반대 방향3.29%다.

같은 조건에서 최종 성공 에피소드의 샘플 평균은0.9121, 실패 에피소드는0.6626이다. 다만 힘 방향, 밀기 속력, 경로, 접촉 시간과 최종 성공은 함께 변하므로 이 차이를 보상 추가의 인과효과로 해석하지 않는다. 최종 성공 집합만 남기지 않았고 실패 샘플도 주 통계에 포함했다.

[분포·힘 임계값·진행량 그림](../../../../outputs/force_direction/analysis/plots/force_alignment.png) · [물체 경로와 실제 힘 방향 예시](../../../../outputs/force_direction/analysis/plots/force_vector_examples.png) · [구간 오염과 접촉 경과 시간](../../../../outputs/force_direction/analysis/plots/screening_and_contact_age.png).

## 어떤 힘인가

타겟 cylinder를 sensor body, 기존30개 hand link/pad를 filter로 하는 기존 PhysX contact view에서 읽었다. **물체가 핸드에서 받는 힘**이며 물체 쪽 reporting force를 그대로 사용한다. 기존 `target_hand_contact_force_w`는 이를 음수로 바꾸어 핸드가 받는 반작용을 반환하므로 이번 방향 계산에는 그 부호를 사용하지 않는다.

```math
\mathbf{F}_{h}(t)=\sum_i\mathbf{F}_{n,i}(t)+\sum_j\mathbf{F}_{f,j}(t)
```

법선 힘과 접선 마찰 힘의 벡터를 각각 합한 뒤 더한다. 모든 접촉 힘의 크기만 더한 값은 합력 방향이 아니다. 여기의 합력에는 선반·다른 물체·중력의 기여가 포함되지 않는다. 따라서 물체의 가속도를 이 힘만으로 설명하거나 이것을 물체에 작용하는 전체 외력이라고 해석하지 않는다.

`force_matrix_w`/`net_forces_w`는 설치된 Isaac Lab 구현에서 법선 성분만 제공한다. 마찰은 기존 view의 `get_friction_data(dt=0.01)`로 별도 읽었다. 상세 contact buffer의 scalar force×normal로 법선을 재구성했고, friction anchor별 벡터도 재집계했다. dt0.01을 명시해 단위를 impulse가 아닌 **N**으로 변환한다. [NVIDIA PhysX Tensor API](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.3/extensions/runtime/source/omni.physics.tensors/docs/api/python.html#omni.physics.tensors.impl.api.RigidContactView.get_friction_data)와 설치된107.3 계열 API 및 Isaac Lab 소스를 대조했다.

## 기준 벡터와 오염 제거

각 episode의 첫 물리 step 전에 초기 물체 root 위치를 고정했다. 목표는 기존 `target_goal_pos`다.

```math
\mathbf{g}_0=\mathbf{p}_{goal}-\mathbf{p}_{initial},\qquad
c_{3D}(t)=\frac{\mathbf{F}_{h}(t)\cdot\mathbf{g}_0}{\|\mathbf{F}_{h}(t)\|\|\mathbf{g}_0\|}
```

원시 힘·위치는 world 좌표다. 초기 선반 quaternion으로 회전해 선반XY 평면에 투영한 `c_XY`도 계산했다. 실제 초기→목표 벡터의 선반Z 성분은 전 샘플에서0이었다. `c_3D`는 누르는 힘까지 고려하고, `c_XY`는 평면 밀기 방향을 본다. 현재 위치→목표 벡터, 물체COM 속도와의 코사인도 비교용으로 남겼다.

주 분석 조건은 다음과 같다.

1. 최초 핸드 접촉 이후이며 **아직 목표 반경3cm에 한 번도 들어가지 않은 구간**. 한번 들어간 뒤 밖으로 나간 구간도 제외한다.
2. 현재 접촉이 실제로 존재: hand filter별 법선 벡터의 크기 합>=0.01N, sensor fresh.
3. 현재 물리 샘플과 그 policy step 시작 시점의 목표XY 거리 모두>3cm.
4. 물체XY 속력>=0.01m/s. 정지 지지·유지력을 섞지 않기 위한 분석용 조건이다.
5. 합력 크기 및 수평 합력 크기 모두>=1N.0에 가까운 힘의 방향을 정의하거나 임의로0점 처리하지 않는다.

이전 구간 조사와 달리 이번 contact onset은100Hz의 순간 실제 접촉으로 정의했다.2-of-3 policy 접촉 인정은 사용하지 않았다. 첫 접촉 충격을 포함한 주 통계와 최초20/50ms를 제외한 민감도를 모두 계산했다.

| 누적 조건 | 남은 물리 샘플 |
| --- | ---: |
| quota 내 원시 샘플 | 1,427,392 |
| 최초 접촉 이후·최초 목표 진입 전 | 73,150 |
| 현재도 실제 접촉·fresh·목표 밖 | 62,447 |
| XY 속력>=1cm/s | 23,463 |
| 합력/수평 합력>=1N | **19,273** |

최초 목표 진입 후 내부1,130,171개, 재이탈186,167개, 접촉 전37,904개는 주 분석에 포함되지 않는다. **원시 파일에서는 이들을 삭제하지 않았다.**

## 코사인과 힘의 분포

| 계산 | 평균 | 중앙값 | P05 | P95 |
| --- | ---: | ---: | ---: | ---: |
| 법선+마찰 합력, 초기→목표XY | **0.8528** | **0.9493** | 0.4327 | 0.9995 |
| 법선+마찰 합력, 초기→목표3D | 0.8245 | 0.9038 | 0.3165 | 0.9879 |
| 법선만, 초기→목표XY | 0.9138 | 0.9627 | 0.6722 | 0.9996 |
| 법선+마찰 합력, 현재→목표XY | 0.8144 | 0.9561 | -0.3816 | 0.9996 |

주 조건에서 총 힘 중앙값2.824N, P95 13.033N, 최대71.588N이다. 선반Z 힘 중앙값-0.554N으로 아래로 누르는 성분이 존재한다. 마찰 벡터 크기/합력 크기의 중앙값은0.334다. 이 비율은 힘 크기의 단순 구성비가 아니며, 벡터 합에서 상쇄가 있어1을 넘을 수도 있다.

법선만 사용하면 평균이0.061 높아져 정렬도를 과대평가한다. 평면 밀기 방향이 목적이라면XY 합력 보상이 더 직접적이며,3D 코사인은 수평 오정렬과 수직 누르기를 함께 벌점화한다.

샘플 가중 평균0.8528과 별개로, 에피소드별 평균을 동일 가중하면 **0.9098**이다. 일부 실패 episode에 낮은 정렬도의 느린 밀기가 오래 지속되어 두 통계가 달라진다. seed별 환경 block을 재추출하고 그 안의 episode를 함께 보존한2,000회 bootstrap의 해당 동일가중 평균95% 구간은 **[0.9027,0.9161]**이다. 이 구간은 수집된 두 seed의 조건부 불확실성이며 새 환경/정책에 대한 일반화 구간이 아니다.

| seed | 완료 episode | 원시 물리 샘플 | 분석 샘플 / episode | XY 평균 / 중앙값 |
| --- | ---: | ---: | ---: | ---: |
| 42 | 1,280 | 1,239,206 | 16,694 / 1,254 | 0.8481 / 0.9493 |
| 123 | 192 | 188,186 | 2,579 / 191 | 0.8837 / 0.9495 |

목표 사분면별 평균은Q1 0.7718/Q2 0.8882/Q3 0.8372/Q4 0.9153이다. 모든 방향의 정렬이 같다는 결론은 아니다. seed의 환경수·episode 수가 달라 seed별 차이를 짝지어진 실험으로 해석하지 않는다.

## 임계값과 구간 정의에 대한 민감도

같은 구간·속력>=1cm/s에서 수평 힘 임계값만 바꿨다.

| 최소 수평 힘 | 샘플 | XY 평균 | 음수 비율 |
| --- | ---: | ---: | ---: |
| 0.01N | 23,463 | 0.8514 | 3.08% |
| 0.1N | 23,345 | 0.8511 | 3.09% |
| 0.5N | 22,297 | 0.8495 | 3.18% |
| 1N | 19,273 | 0.8528 | 3.29% |
| 2N | 12,678 | 0.9081 | 0.58% |
| 5N | 2,813 | 0.9117 | 0.07% |
| 10N | 1,262 | 0.9167 | 0.08% |

0.01–1N의 임계값에서는 결론이 거의 같다. 거의0인 힘 때문에 정렬이 높게 보이는 결과는 아니다.2N 이상에서는 반대 방향 힘이 더 드물다.

| 주 조건에서의 변경 | 샘플 | XY 평균 |
| --- | ---: | ---: |
| 속력 조건 없음 | 25,025 | 0.6656 |
| 속력>=2cm/s | 18,370 | 0.8987 |
| 속력>=5cm/s | 17,902 | 0.9115 |
| 목표 거리>4cm | 17,463 | 0.8647 |
| 목표 거리>5cm | 14,986 | 0.8902 |
| 최초 접촉20ms 제외 | 16,132 | 0.8415 |
| 최초 접촉50ms 제외 | 12,477 | 0.8119 |

첫 접촉 충격을 제외해도 양의 정렬은 남는다. 다만 지속되는 느린 밀기까지 포함할수록 정렬도가 낮다. 접촉 후0.02–0.05초 평균0.9427,0.05–0.1초0.9405,0.2–1초0.6046,1–10초0.0514였다. 후반부는 목표에 빠르게 도달하지 못한 episode가 선택된 조건부 집합으로, 동일 episode의 보편적 시간 경과라고 해석하지 않는다.

목표 도달 이후도 섞어 힘>=1N인 접촉을 전부 계산하면272,393개에서 평균 **-0.0352**가 된다. 목표 내부 접촉만224,512개에서 **-0.1286**이다. 낮은 힘뿐 아니라 **도달 후 비영 힘의 지지·보정 상태**도 방향 통계를 크게 바꾼다.

## 보상으로 사용할 때의 의미

최종 성공1,154episode의 분석 샘플14,693개 평균0.9121, 실패318episode 중 분석 조건을 충족한291episode의4,580개 평균0.6626이다. 나머지27episode는 조건을 충족하는 샘플이 없었다. 낮은 정렬도가 성공/실패를 구별하는 관측 신호라는 근거는 있다.

반대 방향634개 중97개는 현재 위치→목표 방향과의 내적이 양수다. 고정 초기→목표 벡터에 반대라고 해서 모든 힘이 잘못된 보정은 아니다. 속도 반대 힘도23개 있어 감속/제동 가능성을 배제할 수 없다. 이 데이터만으로 개별 접촉의 역할을 확정하지 않는다.

따라서 아래 적용 조건이 합리적인 후보이며 **아직 보상은 추가하지 않았다**.

- 물체가 핸드에서 받는 **법선+마찰 합력의 선반XY 방향**을 사용한다. 기존 핸드 반작용 함수의 부호를 그대로 쓰지 않는다.
- 실제 타겟 접촉, 유의한 수평 힘, 목표 외부 조건으로 gate한다. 목표 도달 후 계속 정렬을 요구하지 않는다.3cm 근방의 감속까지 과도하게 벌주지 않도록 거리 gate의 완화 폭도 검토한다.
- cosine 자체는 bounded한 보조 신호로 사용하고, 힘 크기에 비례해 보상하지 않는다. 큰 힘을 더 내는 별도 유인을 만들지 않는다.
- 분석의 속력 gate를 그대로 학습 gate로 복사하는 것은 별도 판단이다. 정지마찰을 이겨 밀기 시작하는 유효한 힘도 속력0에서 발생할 수 있다. 기존 목표 진행/거리 보상과 함께 정지한 채 힘만 주는 행동을 확인해야 한다.
- 고정 초기 벡터를 쓸지 현재 목표 벡터를 쓸지 결정한다. 고정 벡터는 원래 밀기 방향을 보존하지만, 빗나간 뒤 되돌리는 힘 일부를 벌줄 수 있다.
- 정책50Hz의 두 물리 step을 평균/impulse 합산하는 구현도 후보로 검토할 수 있다. 두 step 모두 주 조건을 만족한 동일8,021쌍에서 평균 합력의 코사인 평균0.8761, 마지막 step만의 평균0.8738로 전체 방향은 유사했다. 이 부분집합을 주 통계19,273개와 직접 비교해 우열을 주장하지 않는다.

효과 검증은 동일 부모 환경에서 보상 유무를 비교하는 후속 학습 실험이 필요하다. 완료율·최종 오차·속력·힘 크기·접촉 유지와 보정 구간의 변화를 함께 확인해야 한다. 이번에는 항/가중치/환경 계약을 수정하지 않았다.

## 원시 데이터·재현·검증

체크포인트는 `logs/TEMP/inspire_sweep_simple_finger_v0/2026-11-10_14-30-35/model_3550.pt`, SHA256 `b64d17711f4c3d797e69e1529e46fe4dea79bdcc1ae0b12e5d6ba9e8e2b59642`, iteration3550이다. 두 실행 모두 checkpoint curriculum 적용 후 reset하여 수집을 시작했다. headless 결정적 policy inference이며 기존 관측 노이즈는 유지한다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/force_direction/collect.py --checkpoint logs/TEMP/inspire_sweep_simple_finger_v0/2026-11-10_14-30-35/model_3550.pt --output outputs/force_direction/seed42 --num_envs 128 --episodes 10 --headless --kit_args=--/app/vulkan=false
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/force_direction/collect.py --checkpoint logs/TEMP/inspire_sweep_simple_finger_v0/2026-11-10_14-30-35/model_3550.pt --output outputs/force_direction/seed123 --seed 123 --num_envs 32 --episodes 6 --headless --kit_args=--/app/vulkan=false
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/force_direction/analyze.py outputs/force_direction/seed42 outputs/force_direction/seed123 --output outputs/force_direction/analysis
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/force_direction/plot.py outputs/force_direction/analysis --runs outputs/force_direction/seed42 outputs/force_direction/seed123
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/force_direction/audit.py
```

수집 output은 기존 경로를 덮어쓰지 않도록 `exist_ok=False`다. 재수집 시 새 output 이름을 사용한다.

- [seed42 metadata](../../../../outputs/force_direction/seed42/metadata.json), [seed123 metadata](../../../../outputs/force_direction/seed123/metadata.json), 각 하위 `raw/physics_*.npz`:126개 chunk, 합계380,915,450bytes. 물리 sample 후·reset 전에 기록한다. quota 완료 환경의 남은 bookkeeping 행은 `keep=False`로 표시하므로 이 mask를 적용해야 한다.
- 원시 보존 항목: hand filter별 normal/friction 벡터·count, native contact scalar force/normal/point/separation, friction force/anchor point, 물체 초기/현재 pose·선속도/각속도, goal, 선반 quaternion, policy action12채널, EEF 속도, episode·policy·physics 식별자. 유효 contact/anchor의 sparse record는 각각 **4,535,805 / 4,110,694개**다. buffer의 미사용 capacity slot은 저장하지 않았다.
- [전체 비교 CSV.gz](../../../../outputs/force_direction/analysis/all_samples.csv.gz):1,427,392행. 조건을 충족하지 않는 상태와 정의 불가 cosine도 보존한다. [밀기 CSV](../../../../outputs/force_direction/analysis/pushing_samples.csv):19,273행. 파생 CSV의 `force_x/y/z_N`는 초기 선반축이며, raw NPZ의 접미사`_w`는 world축이다. phase0/1/2/3은 접근/최초목표전접촉이후/최초진입후내부/최초진입후외부다.
- [전체 파생 NPZ](../../../../outputs/force_direction/analysis/derived_all.npz), [episode별 비교 CSV](../../../../outputs/force_direction/analysis/episode_comparison.csv), [집계 JSON](../../../../outputs/force_direction/analysis/summary.json), [raw 파일별 SHA256](../../../../outputs/force_direction/analysis/raw_manifest.csv), [최종 audit](../../../../outputs/force_direction/analysis/audit.json).
- 법선 point 재구성의 최대 오차0.0001221N, 마찰 재구성 오차0.0N. force NaN/Inf0. exported force·고정 단위벡터로XY/3D cosine 재계산 일치, 분류·filter flow·샘플수 일치, checkpoint 전후hash 일치.
- 학습 저장 설정과 actions/observations/rewards/terminations/curriculum/decimation·physics dt의 의미가 동일하다. curriculum points의 tuple/list 직렬화 차이만 정규화해서 비교했다. sensor 설정이나 물리 파라미터는 바꾸지 않았다. source commit과 기존 작업트리 상태는 audit에 기록했다.
- pilot과 interim은 계측/분석 검사용이며 위 최종 통계에 섞지 않았다. 실행 코드·기존 학습로그·사용자 변경은 보존했다. 그림은 실제 PNG를 열어 검사했고, vector 예시는 방향만 비교하도록 화살표 길이를1.5cm로 정규화했음을 표시했다. 상세 step은 전부 raw에 남아 있다.

미검증 범위: 다른 checkpoint, 학습 보상 추가의 효과, 실기, 모든 접촉 역할의 인과적 분류, 정지 상태에서 보상을 주었을 때의 행동. 수집 중 PhysX의 기존 velocity-update 관련 warning은 있었으며 해당 설정을 변경하지 않았다. 원시 pose 기반 목표 진행량과COM 속도를 모두 보존해 속도만으로 결론을 내리지 않았다.
