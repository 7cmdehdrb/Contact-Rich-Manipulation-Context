# Inspire-Sweep-Prof-Revision-v0 개발 명세

작성일: 2026-11-23. 관측 정정: 2026-11-24(손 관절 복원·OBB quaternion). 후속 상태: **환경 구현·등록·필수 성능 검증 완료**. 실제 코드 계약과 최종 검증 결과는 [환경 안내](../../02_implementation/environments/PROF_REVISION_V0.md)와 [구현 로그](../../02_implementation/logs/2026-11-23_prof_revision_v0_implementation.md)를 따른다.

`Inspire-Sweep-Single-Contact-v0`의 현재 동작을 기준으로, 초기 관측을 가시 OBB로 바꾸고 손끝 Pose·Contact Formation·증분 Reaching을 추가하는 독립 환경을 만든다. 새 EnvCfg 파일은 `src/inspire_sweep_baseline/inspire_sweep_baseline/envs/prof_revision_envs.py`다. 기존 환경의 Python 상속 계통은 이어받지 않는다.

사용자 후속 확인에 따라 **Actor는 초기 관측 OBB를 유지하고 현재 EEF 좌표로만 변환한다.** 물체의 현재 pose는 보상·성공 판정에만 사용한다. 초기 시각 이후 촉각·F/T를 이용한다는 관측 조건을 유지한다.

기능 정확성과 함께 **1 iteration의 collection time 10초 미만, 권장 5초 이하**를 개발 요구사항으로 둔다. 가시성 필터는 기존 2cm·20%를 고정하지 않고 비슷한 노출 인정 수준을 유지하는 OBB 기반 저비용 방식으로 조정할 수 있다. 손가락 Frame은 다섯 개 모두 동일한 생성 규칙과 계산 경로를 사용한다. 구체적인 성능 측정 조건은 아래 collection 성능 절을 따른다.

## 기준과 변경 범위

기능 기준은 Single Contact **v0**다. v1에서는 Reaching의 대칭 거리 증분 방식만 참조한다. v1의 외접 원 접근점, 구역3 예외, signed 힘 방향 함수, 팔 종료 일회 비용은 가져오지 않는다. Zone3 v0의 목표 방향 제한도 사용하지 않는다.

| 항목 | 현재 Single Contact v0 | Prof Revision v0 |
| --- | --- | --- |
| 등록 ID | `Inspire-Sweep-Single-Contact-v0` | `Inspire-Sweep-Prof-Revision-v0` |
| 계통 | Sweep v0의 자식 | Isaac Lab 기반 직접 구성 |
| 타겟 시각 관측 | 초기 대표 표면점 3D | 초기 가시 OBB 중심·크기·xyzw quaternion 10D |
| 장애물 입력 | `[mask,x,y,z]` × 16 | `[mask,x,y,z,w,d,h,qx,qy,qz,qw]` × 16 |
| 손 관측 | 구동 관절 위치 6D | EEF → 손 관절6D → 손끝 Pose35D |
| 장애물 encoder | 64 → 32 → 16 | **176 → 128 → 64 → 32 → 16**, ReLU |
| Reaching | 현재 실제 기하 중심, 선형 근접 보상, weight 0.8 | 현재 추적 가시 OBB 중심, 10cm 초과 거리의 대칭 증분, weight 4.9 |
| Contact Formation | 없음 | 5개 손끝과 현재 추적 가시 OBB까지 거리 합의 정규화 역수 |
| Sweep 거리 | 현재 실제 기하 중심과 목표의 XY 거리 | 현재 추적 가시 OBB 중심과 목표의 XY 거리 |
| Sweep weight | 진행 +50 / 후퇴 −10 | **진행 +100 / 후퇴 −20** |
| Sweep 접촉 높이 | EEF가 상판 위 12cm 미만 | 해당 제한 제거 |
| 성공 거리 | timeout 시 실제 중심, 코드상 `< 0.03m` | timeout 시 추적 가시 OBB 중심, `<= 0.03m` |
| 나머지 | v0 현재 값 | 아래 보존 계약 적용 |

2026-11-24 사용자 정정으로 기존 손 구동 관절 위치6D를 복원하고 **EEF Pose → 손 관절 → Finger Pose** 순으로 둔다. 타겟·장애물 OBB 방향은 EEF의 기울기까지 표현하도록 yaw에서 xyzw quaternion으로 교체한다. 기존 yaw 관측 checkpoint와 shape·의미가 달라 새 학습이 필요하다.

성공 기준점도 가시 OBB 중심으로 바꾼다. 보상만 바꾸고 성공 판정을 실제 중심에 남기면 “초기에 보였던 부분을 목표로 옮긴다”는 과업과 불일치한다. 경계의 `<=`는 workspace 개발 지침의 목표 도달 규칙을 적용한 새 환경의 의도적 차이다. 기존 v0의 `<`는 수정하지 않는다.

## 독립 환경과 파일 구성

| 역할 | 예정 파일과 클래스 |
| --- | --- |
| EnvCfg | `envs/prof_revision_envs.py`의 `ProfRevisionEnvCfg(ManagerBasedRLEnvCfg)` |
| Runtime | `runtime/prof_revision.py`의 `ProfRevisionEnv(ManagerBasedRLEnv)` |
| Scene | `assets/scenes/prof_revision.py`의 `ProfRevisionSceneCfg(InteractiveSceneCfg)` |
| Manager 구성 | `mdp/{observations,rewards,events,terminations,actions,commands}/prof_revision.py` |
| 관측·보상·reset·종료 함수 | 해당 `mdp/*_functions/prof_revision.py`; 변경이 필요한 역할만 추가 |
| 관측 기하·상태 | `mdp/common/prof_revision_obb.py`, `mdp/common/prof_revision_state.py` |
| PPO | `agent/prof_revision_ppo_cfg.py`의 `ProfRevisionPPORunnerCfg(RslRlOnPolicyRunnerCfg)` |
| 모델·encoder·export | `agent/prof_revision_models.py`; 모델은 `MLPModel`, encoder는 `nn.Module` 기반 |
| 등록 | 기존 패키지 `__init__.py`에 새 ID와 위 entry point 추가 |
| 검증 | `tests/test_prof_revision_*.py`, 필요 시 `scripts/check_prof_revision.py` |

위 경로는 명세 작성 당시의 구현 계획이며 후속 구현에서 적용했다. GPU OBB 커널은 `mdp/common/prof_revision_obb_gpu.py`, 공통 손끝·OBB 변환은 `mdp/common/prof_revision_geometry.py`에 추가했다. 기존 역할별 디렉토리를 유지하고 파일 이동이나 기존 계열 재구성은 하지 않는다. 새 계열의 추가 버전은 같은 역할별 파일에 둔다.

새 EnvCfg·runtime·SceneCfg·Manager Cfg·state·PPO·모델은 Sweep/Single Contact/Stabilize/Revision/Final/Holding의 환경별 클래스를 상속하지 않는다. 기존 EnvCfg 인스턴스를 복사하여 내부에 숨기는 구성도 사용하지 않는다. `super()`는 새 클래스의 프레임워크 기반 초기화에만 사용한다.

자산 factory, 접촉 센서 reduction, tactile/wrench reader, OSC Action term, 순수 기하 함수, reset 배치·IK helper, 공통 runner는 재사용할 수 있다. 예를 들어 `ContactSamples`와 `ContactSideSweepProgress`의 타겟 접촉 계산은 재사용 가능하다. 다만 필요한 환경 필드·캐시·reset 계약을 명시적으로 제공해야 한다. `SweepSingleContactEnv.step(self, ...)`처럼 이전 runtime 전체를 우회 호출하여 상속 의존성을 대신하는 방식은 사용하지 않는다.

## 가시 OBB 산출

### 정면 관측의 의미

기준 알고리즘은 [observed_obb 관측 구현](../../../../src/observed_obb/observed_obb/observation.py)이다. 이것은 RGB-D 센서 재구성이 아니라 **배치된 물체 bounds에 기반한 기하학적 가시 영역 근사**다. 가시 영역의 의미는 유지하되 노출 인정식과 계산 구현은 아래 범위에서 최적화할 수 있다.

1. 선반 로컬 +X에서 −X 방향으로 바라본다. 정면 가로축은 선반 Y다. 뷰어 카메라나 EEF 방향은 산출 방향에 영향을 주지 않는다.
2. 입력은 타겟과 실제 활성 장애물의 scaled local bounds·초기 pose다. 기하 중심과 asset root를 혼동하지 않는다. 주차된 비활성 후보는 제외한다.
3. 각 물체의 정면 가로 구간에서 가장 앞에 있는 물체가 가린다. **높이 차이는 가림 판정에 사용하지 않는다.** 기존 mesh ray 관측과 이 점이 다르다.
4. 각 연속 가시 조각에 대해 정면에서 충분히 노출되었는지 판정한다. **기존의 2cm 이상 AND 원본 정면 투영 폭의 20% 이상은 비교 기준이며 필수 고정식이 아니다.** 비슷한 인정 수준이라면 OBB에 맞는 투영 폭·노출 비율·투영 면적 등의 판정과 문턱 조정을 허용한다. 최종 선택은 계산 비용과 아래 비교 검증으로 결정한다. 경계값은 포함하고, 탈락한 물체도 다른 물체를 가리는 계산에는 계속 참여한다.
5. 해당 가로 구간으로 원래 footprint를 절단하되 전체 깊이를 유지하고, XY 최소 면적 직사각형과 원래 높이로 OBB를 만든다. `w,d,h`는 이 OBB 축에 대한 전체 변 길이이며 반길이가 아니다.
6. 완전히 보이는 물체는 원래 입력 Box를 유지한다. 부분 가림은 reference와 같은 최소 면적 fit을 사용한다. 후속 구현에서는 면적 차이1e-12 이내의 동률에 가장 작은 canonical yaw를 선택하고0/π/2 근방1e-12 회전도 통일하여 CPU/GPU 결과를 안정화했다. 원본 reference와 최소 면적은 같지만 동률 Box의 방향은 달라질 수 있다. 조각을 합쳐 가려진 부분을 다시 포함시키지 않는다.

전체 깊이·높이 정보가 남는다는 한계도 이 관측 모델의 일부다. 이를 실제 카메라만으로 완전히 추정한 3D 형상이라고 해석하지 않는다. 선반·로봇을 새 occluder로 추가하거나 시각화 패키지의 “부분 가림 장면만 고르는 배치”를 가져오지 않는다.

### 노출 필터의 계산 비용과 선택 기준

우선 후보는 이미 산출한 가시 구간 길이 `L`과 원본 OBB의 정면 투영 폭 `W`를 재사용하는 방식이다. 선반 기준 yaw가 `ψ`이면 `W=|sin ψ|w+|cos ψ|d`로 구할 수 있다. 비율 비교는 나눗셈 없이 `L >= τW`로 수행할 수 있다. 기존 `L >= max(0.02,0.20W)`도 충분히 저렴하면 그대로 사용할 수 있으나, 이 식을 유지하기 위해 별도 mesh ray·고해상도 mask·연결성 계산을 추가하지 않는다. 필터를 통과한 조각에 대해서만 OBB fitting을 수행한다.

OBB 투영 면적 등 다른 판정으로 바꾸는 경우에도 이미 계산한 기하량을 최대한 재사용한다. 높이를 모두 유지하는 현재 근사에서는 면적 비율이 폭 비율과 같아질 수 있으므로, 추가 계산의 실익 없이 표현만 복잡하게 바꾸지 않는다. fitted Box의 전체 폭이나 전체 부피만으로 실제 가려진 조각을 충분히 노출된 것으로 판정해서는 안 된다.

최종 필터의 식·문턱·수치 허용오차는 구현 시 Cfg에 명시하고 episode 중 고정한다. 같은 초기 장면 bank에서 기존 기준과 새 후보의 채택/탈락 일치율, 불일치 조각의 폭·비율, 완전 가림·거의 가림·충분한 노출 사례, 타겟 누락·fallback·슬롯 수 분포 및 계산 시간을 비교한다. 기존 기준과 완전 일치를 요구하지 않지만, 유사한 노출 인정 수준이라는 근거를 기록해야 한다. 특히 장애물을 거의 모두 버리거나 fallback으로 빈 장면을 늘려 성능을 맞추지 않는다.

### 타겟과 장애물 조각

`observed_obb.observe()`의 공개 반환값은 snapshot-local ID만 제공하고 원본 물체 ID를 제거한다. 따라서 반환 ID를 물리 슬롯으로 취급해서는 안 된다. 새 환경 내부 adapter는 가시 구간을 만들 때부터 `source_object_slot`, 가시 폭, 구간 경계를 유지하고 정책 입력 직전에 제거한다. 타겟 조각 선택과 보상용 rigid transform을 위해 이 내부 연결이 필요하다.

공개 관측 패키지는 수정하지 않는다. 새 baseline helper에 필요한 순수 계산을 출처와 함께 옮기거나 재사용하되, 같은 입력과 같은 채택 구간의 Box 기하는 reference와 수치적으로 일치하도록 검증한다. 노출 필터를 바꿔 채택 집합이 달라지는 것은 별도 비교 대상으로 기록하며 오류로 취급하지 않는다. `observed_obb`의 viewer·정지 Scene·배치 선택기는 runtime 의존성에 넣지 않는다.

| 경우 | 처리 |
| --- | --- |
| 타겟 가시 조각 1개 | 해당 OBB를 10D 타겟으로 선택 |
| 타겟 가시 조각 여러 개 | 정면 노출 폭이 가장 큰 조각 1개 선택; 동률이면 선반 Y의 작은 구간 시작점 우선 |
| 선택하지 않은 타겟 조각 | 장애물 슬롯에 넣지 않음 |
| 장애물 한 개가 여러 조각 | 채택 조각마다 별도 슬롯; 동일 물체에 속해도 합치지 않음 |
| 장애물 순서 | 원본 물리 슬롯 오름차순, 그 안에서 가시 구간 시작점 오름차순; reset 이후 고정 |
| 빈 슬롯 | mask 포함 11개 값 모두 0 |
| 타겟 누락 또는 장애물 16슬롯 초과 | 기존 reset의 target-only fallback 보존: 해당 reset 행의 장애물을 비활성화·기존 주차 위치로 옮긴 뒤 1회 재산출; 다시 실패하면 명시적 오류 |

필터 기준을 타겟에도 동일 적용하고, 가장 큰 타겟 조각을 고르는 규칙은 단일 10D 입력을 위한 설계 선택이다. 기존 mesh pixel 면적 대신 새 관측의 정면 폭을 사용한다. OBB 변경으로 fallback 발생 빈도는 달라질 수 있으므로 기록한다. overflow를 조용히 잘라내거나 GT 전체 Box로 대신하지 않는다.

최종 채택 장면마다 OBB snapshot은 **reset 시 한 번만 확정**한다. fallback의 실패 후보 계산은 reset 내부에 한정된다. episode 도중 새 가림, 접촉, 카메라 이동, 성공 구간 진입으로 재산출하지 않는다. 추가 OBB noise·mask flip·슬롯 swap은 넣지 않는다. 현재 v0의 실제 노출 관측도 legacy centroid noise·swap을 사용하지 않는다는 점을 보존한다.

## 초기 관측과 보상용 추적의 분리

월드 좌표계를 W, 현재 EEF를 E, 실제 타겟 rigid link를 O, 가시 OBB를 B라 한다. `T_AB`는 B 좌표를 A 좌표로 옮기는 강체 변환이다. 초기 가시 OBB는 `T_WB(0)`와 크기 `s=(w,d,h)`로 저장한다.

### Actor와 Critic

타겟·장애물 모두 초기 월드 snapshot을 유지한다. 현재 물체 pose를 읽어 Actor 입력을 이동시키지 않는다. 매 관측에서 현재 EEF 역변환만 적용한다.

```math
T_{EB}^{\mathrm{obs}}(t)=T_{WE}(t)^{-1}T_{WB}(0).
```

현재 EEF가 고정된 채 물체만 이동·회전하면 시각 관측은 변하지 않는다. EEF만 움직이면 중심 좌표와 상대 quaternion가 변하며 크기와 mask는 변하지 않는다. Critic도 v0처럼 같은 `policy`, `obstacles` 입력을 사용한다. 별도 현재 타겟 GT·live 장애물 입력을 추가하지 않는다.

### Reaching과 Contact Formation과 Sweeping

초기 관측 Box를 실제 타겟의 link-local 좌표에 고정한다. 실제 COM frame 대신 산출 입력과 일치하는 link frame을 사용한다.

```math
T_{OB}=T_{WO}(0)^{-1}T_{WB}(0),\qquad
T_{WB}^{\mathrm{reward}}(t)=T_{WO}(t)T_{OB}.
```

`T_OB`와 크기는 episode 동안 불변이다. 실제 타겟의 병진·회전에 따라 초기 가시 조각이 함께 이동한다. 왼쪽 일부만 보였다면 바로 그 부분의 중심을 목표로 옮긴다. 관측을 다시 수행하거나 물체 전체 중심으로 복귀하지 않는다. 회전에 의한 조각 중심의 이동도 Sweep 진행에 포함된다.

현재 pose GT는 시뮬레이션 보상·종료·진단 내부에서만 사용한다. 장애물 시각 snapshot은 고정하되 기존 물리 접촉·변위·전도 비용은 계속 실제 물리 객체로 계산한다.

### EEF 기준 OBB quaternion

관측은 전체 상대 회전 `q_EB = conjugate(q_WE) ⊗ q_WB(0)`을 사용한다. 내부 계산은 Isaac Lab wxyz convention이며 출력은 **xyzw**다. quaternion을 unit norm으로 정규화하고 scalar가 양수인 부호를 택한다. scalar가 정확히0이면 첫 nonzero vector 성분이 양수인 부호를 택하여 q와−q가 같은 관측을 만든다. 손끝에도 같은 함수를 사용한다.

EEF roll/pitch를 포함한 회전을 그대로 표현하므로 heading 투영·yaw wrap·투영 퇴화 fallback은 제거한다. 크기는 EEF 축의 AABB가 아닌 OBB 고유 축의 길이를 유지한다. 회전을 바꾸면서 w/d를 교환하거나 Box를 다시 fit하지 않는다. reset 시 서 있는 물체의 정면 가시 footprint를 산출하는 내부 yaw는 그대로 사용하며, 정책에 전달되는 방향 값만 quaternion이다. 보상 거리 계산은 기존 full quaternion을 그대로 사용한다.

## Observation Space

### 입력 순서와 차원

`policy`에는 아래 직접 관측만 넣고, `obstacles`에는 별도 176D tensor를 넣는다. 각 모델의 encoder 결과 16D를 직접 관측 뒤에 연결한다.

| 순서 | 항목 | 차원 | 단위와 좌표계 및 시점 |
| --- | --- | --- | --- |
| 1 | Arm Joint Position | 6 | rad, 현재 실제 팔 관절값, 기존 관절 순서 |
| 2 | Arm Joint Velocity | 6 | rad/s, 현재 실제 팔 관절값 |
| 3 | EEF Pose | 7 | robot Base 기준 현재 위치·회전, 기존 `(x,y,z,qw,qx,qy,qz)` 보존 |
| 4 | Hand Joint Position | 6 | rad, 기존 `HAND_DRIVE_JOINT_NAMES` 순서: 엄지 굽힘·검지·중지·약지·소지·엄지 대립 |
| 5 | Finger Pose × 5 | 35 | 현재 EEF 기준, 손가락별 `(x,y,z,qx,qy,qz,qw)` |
| 6 | Target Observable OBB | 10 | 초기 snapshot을 현재 EEF로 변환한 `(x,y,z,w,d,h,qx,qy,qz,qw)`, m 및 unit quaternion |
| 7 | Goal Position | 3 | 고정 월드 목표를 현재 EEF로 변환, m |
| 8 | Last Action | 12 | 기존 원본 action 관측 유지 |
| 9 | Tactile | 17 | 기존 paired 상태: 없음0·손바닥1·손등−1·양면2, 기존 noise |
| 10 | Wrench | 6 | 기존 물리 신호 → noise → 축별 clip → 정규화, EEF 센서 계약 보존 |
| 11 | Encoded Obstacles | 16 | 아래176D 장애물 tensor의 학습 embedding |

직접 관측은 `6+6+7+6+35+10+3+12+17+6=108D`, 원시 저장 입력은 `108+176=284D`, encoder 뒤 Actor/Critic MLP 입력은 `108+16=124D`다. Action은 기존 **12D**다. 관측 복원은 제어 자유도를 바꾸지 않는다. phase 관측은 없다.

정확한 policy slice는 팔 위치 `[0:6]`·팔 속도 `[6:12]`·EEF `[12:19]`·손 관절 `[19:25]`·손끝 `[25:60]`·타겟 `[60:70]`·목표 `[70:73]`·action `[73:85]`·tactile `[85:102]`·wrench `[102:108]`다.

EEF 기존 quaternion은 `wxyz`, 새 Finger Pose와 OBB는 **xyzw**다. 새 quaternion은 위 공통 normalize·canonicalize 규칙을 적용하고 EEF 항은 기존 callable을 유지한다. 새 Pose·OBB·손 관절 항에 임의 noise나 scale을 추가하지 않는다. 손 관절은 실제 측정 rad이며 action의 `[0,1]` 비율로 바꾸지 않는다. F/T 한계는 `(150,150,150,8,8,8)`이다.

### 손끝 Pose 기준점

기존 Scene의 `finger_frame`은 손가락 관절을 따라가는 5개 프레임이 아니라 두 개의 고정 tool offset이므로 재사용하지 않는다. 지문 부위에 대응하는 아래 distal tactile pad의 현재 body pose와 pad-local offset을 사용한다.

| 순서 | 손가락 | 기준 body |
| --- | --- | --- |
| 1 | 엄지 | `inspire_thumb_force_sensor_4` |
| 2 | 검지 | `inspire_index_force_sensor_3` |
| 3 | 중지 | `inspire_middle_force_sensor_3` |
| 4 | 약지 | `inspire_ring_force_sensor_3` |
| 5 | 소지 | `inspire_little_force_sensor_3` |

**엄지부터 소지까지 동일한 Frame 생성 함수를 사용한다.** 손가락마다 다른 기준점 선정법·축 재배열·별도 FK 경로를 두지 않는다. 차이는 위 body 이름과 해당 자산의 bounds 값뿐이다. [tactile_regions.json](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/data/wrench_right_hand/tactile_regions.json)의 sensor-body-local `pad_bounds_m`을 공통 입력으로 사용한다.

1. 로컬 원점은 bounds의 x/y 중점과 max-z, 즉 `((xmin+xmax)/2,(ymin+ymax)/2,zmax)`로 정한다. 모든 손가락에서 지문 영역의 표면 대표점을 뜻하며 distal link 원점이나 mesh 최전방 점으로 바꾸지 않는다.
2. 로컬 축은 pad body의 +X/+Y/+Z를 그대로 사용한다. 모든 pad에서 +Z는 바깥 방향이며 오른손 좌표계다. Frame의 pad-local 회전은 identity다. 엄지만 임의로 축을 뒤집거나 별도 yaw offset을 주지 않는다.
3. 현재 pad body를 P, 손끝 Frame을 F라 하면 `T_WF=T_WP T_PF`, `T_EF=T_WE^(-1) T_WF`를 다섯 손가락에 똑같이 적용한다. 동일한 quaternion normalize·부호·xyzw 출력 규칙을 적용한다.
4. body index와 고정 `T_PF`는 시작 시 한 번 계산해 device tensor로 캐시한다. 매 policy step에서는 기존 articulation pose buffer에서 다섯 body를 한 번에 gather하고 `[num_envs,5,...]` 배치 변환으로 계산한다. 관측과 Contact Formation은 이 공통 결과를 재사용하며 부분 reset 시 해당 행만 갱신한다.

손을 열고 굽혔을 때 다섯 기준점과 축 marker가 각각 distal pad를 따라가는지 실제 자산으로 확인한다. 원점·축·transform·quaternion 규칙을 동일 함수의 테스트로 검사한다. 관측용 Frame은 가상 계산 프레임이며, 손가락별 물리 collider·새 센서·매 step USD prim 탐색을 추가하지 않는다.

### 장애물 encoder

각 슬롯은 `[mask,x,y,z,w,d,h,qx,qy,qz,qw]`이며 16개를 슬롯 우선으로 flatten한다. `mask=0`인 행은 **MLP 직전에 전체 11D를 다시 0으로 처리**한다. 좌표만 0으로 바꾸고 크기·quaternion을 남기지 않는다.

권장 기본 구조는 `Linear(176,128) → ReLU → Linear(128,64) → ReLU → Linear(64,32) → ReLU → Linear(32,16)`이다. 마지막 출력에는 activation을 넣지 않는다. 슬롯 구조와 mask가 명시되어 있고 기존 16D embedding을 유지할 수 있어 첫 실험에 적합한 크기다. 16D가 충분하다는 성능 결론은 학습 후 판단한다.

Actor와 Critic은 각각 독립 encoder를 가진다. PPO rollout에는 176D 원시 장애물 관측을 저장하고 minibatch마다 encoder를 다시 계산하여 gradient가 전달되도록 한다. embedding을 detach하거나 reset 때만 계산하지 않는다. 모든 슬롯이 비면 입력은 0이며, bias에 의한 학습 가능한 empty-scene embedding은 허용한다.

기존 본체 `[256,128,64]`, ELU, `obs_normalization=False`는 유지한다. 기존 모델은 64D 장애물 shape와 export 입력 폭을 고정하므로 단순 Cfg 수치 변경만으로 재사용하지 않는다. 새 모델·JIT/ONNX export는 `108|176` 경계와 284D 입력을 사용한다. 기존 checkpoint는 입력 의미·shape가 달라 직접 resume 대상으로 삼지 않는다.

## Reward

`Δt=0.02s`는 정책 간격이다. 아래 `R`은 weight와 RewardManager의 dt까지 적용된 **실제 한 step 기여**다. 거리 증분 항은 callable에서 `Δt`로 나누고 Manager에서 한 번 곱한다. Contact Formation은 연속 rate 항이므로 callable에서 dt로 나누지 않는다.

### Reaching

EEF의 현재 위치를 `p_E(t)`, 추적 가시 OBB 중심을 `c_B(t)`라 한다. 3D 거리의 10cm 초과분 감소에는 양의 값, 증가에는 같은 크기의 음의 값을 준다.

```math
d_t=\|p_E(t)-c_B(t)\|_2,\qquad e_t=\max(d_t-0.10,0),
\qquad R_{\mathrm{reach},t}=4.9(e_{t-1}-e_t).
```

권장 초기 weight는 v1과 같은 **4.9**다. 최단 거리 기록·초기 거리 정규화·최대 양수만 취하는 clamp·구역별 접근점·접촉 gate는 사용하지 않는다. 10cm 안에서 이동하거나 정지하면 0이고, 바깥으로 멀어지면 음수가 된다. 물체가 움직여 거리 변화가 생기는 경우도 같은 식을 적용한다.

reset 최종 상태의 `e_0`를 저장하여 첫 step에 가짜 보상이 생기지 않게 한다. policy step마다 이전 값을 한 번만 갱신하며 같은 step의 로깅·중복 조회는 보상을 소모하지 않는다. 종료 step의 보상은 reset 전 타겟 상태로 계산한다.

| 전후 거리 | 실제 Reach 기여 |
| --- | --- |
| 20cm → 19cm | +0.049 |
| 19cm → 20cm | −0.049 |
| 10.5cm → 9.5cm | +0.0245 |
| 9.5cm → 10.5cm | −0.0245 |
| 9cm → 8cm 또는 정지 | 0 |

### Contact Formation

5개 손끝 현재 월드 위치를 `f_i(t)`, 추적 OBB 회전을 `R_WB(t)`, 반크기를 `a=s/2`라 한다. 손끝을 OBB 로컬 좌표로 옮기고, 박스 외부까지의 유클리드 거리를 계산한다.

```math
u_i=R_{WB}(t)^T(f_i(t)-c_B(t)),\qquad
\delta_i=\|\max(|u_i|-a,0)\|_2,\qquad S_t=\sum_{i=1}^{5}\delta_i.
```

면·모서리·꼭짓점 밖에서는 가장 가까운 표면까지 거리다. **표면과 내부에서는 0**이므로 박스 중심에 더 가깝다고 추가 이득을 주지 않는다. signed distance의 절댓값이나 중심점 거리로 대체하지 않는다. 실제 물체 mesh보다 OBB가 크다는 점을 허용한다.

단순 `1/S`의 무한대를 피하면서 거리 합에 반비례하도록 다음 정규화 역수식을 사용한다.

```math
r_{\mathrm{formation},t}=\frac{S_0}{S_0+S_t},\qquad S_0=0.05\ \mathrm{m},
\qquad R_{\mathrm{formation},t}=0.245\,r_{\mathrm{formation},t}\,\Delta t.
```

초기 weight **0.245**, 거리 합 척도 **5cm**를 권장한다. 다섯 손가락의 평균 gap 1cm에서 raw reward가 0.5다. 하나의 손끝만 가장 가깝다는 이유로 나머지 네 손가락을 제외하지 않는다. 접촉 sensor 인정·손가락 normal 정렬·EEF 높이·Reach 내부 여부를 추가 gate로 넣지 않는다.

“Reach의 절반 수준”은 기준 접근 속도 **0.10m/s**에서 맞춘다. 이는 가중치 산정을 위한 설계 기준값이며 실측 속도가 아니다. 10cm 바깥에서 이 속도로 접근하면 Reach는 step당 `4.9×0.10×0.02=0.0098`, Formation 최대는 `0.245×0.02=0.0049`로 절반이다. 두 reward의 시간 성격이 다르므로 weight를 단순히 `4.9/2`로 지정하지 않는다.

| 거리 합 S | raw Formation | 실제 step 기여 |
| --- | --- | --- |
| 0cm | 1 | 0.0049 |
| 5cm | 0.5 | 0.00245 |
| 10cm | 약 0.3333 | 약 0.0016333 |
| 25cm | 약 0.1667 | 약 0.0008167 |

Reach가 0 또는 음수인 step에도 Formation은 양수일 수 있다. 따라서 순간값이나 episode 합을 Reach의 절반으로 제한하지 않는다. 최대 상태로 10초 유지하면 Formation 합은 2.45이므로, 목표 밖에서 손만 유지하는 행동의 보상 비중을 후속 학습에서 확인한다. 현재 명세에 별도의 cap·조기 소멸·progress gate를 추가하지 않는다.

### Sweeping

`g`는 기존 command가 정한 고정 월드 목표다. 거리·현재 목표 방향·reset 시 이전 거리에 모두 추적 가시 OBB 중심을 사용한다.

```math
D_t=\|g_{xy}-c_{B,xy}(t)\|_2,\qquad \Delta D_t=D_{t-1}-D_t,
```

```math
R_{\mathrm{sweep},t}=100\max(\Delta D_t,0)h_t a_t m_t,\qquad
R_{\mathrm{retreat},t}=-20\max(-\Delta D_t,0).
```

`h_t`는 최근 3 policy step 중 유효 타겟 접촉이 2회 이상일 때 1인 boolean 접촉 계수다. 누적 count나 count/20은 사용하지 않는다. **EEF 높이 조건을 제거**한다. 현재 스텝 실제 접촉·데이터 유효성·평균 수평 접촉력 1N 이상·유효 목표 방향 조건은 보존한다.

`a_t`는 v0와 같은 0–1 힘 정렬 계수다. 현재 OBB 중심에서 목표로 향하는 XY 단위벡터와 타겟에 작용하는 평균 힘의 내적을 **3D 평균 힘 크기**로 나눈 뒤 `[0,1]`로 clamp한다. 유효 목표 거리가 `1e-12m` 이하이면 방향 가산은 0으로 둔다. v1의 signed 30°/p4 식은 사용하지 않는다.

`m_t`는 v0의 접촉면 선호다. 초기 command의 선반 기준 방향으로 구역을 정하고, 구역1/2 손등·구역3/4 손바닥에 1.5, 반대 면에 0.7, 분류 불가에 1을 적용한다. 현재 OBB가 목표를 지나쳤다고 구역이 바뀌지 않는다. 역방향 비용은 접촉·힘 정렬·면 선호와 무관한 현재 v0 계약을 유지한다.

현재 실제 중심을 반환하는 공용 `centroid()`를 바꾸지 않는다. 새 중심 helper를 Reach·Formation·Sweep·성공·목표 거리 지표에 명시적으로 연결한다. 접촉 torque의 물리 기준점과 활성 물체 변위·전도 비용은 기존 실제 기하/COM 기준을 유지한다.

### EEF 높이 제한 제거 범위

현재 보상 목록에는 독립된 `eef_z` 비용이 없다. 제한은 `StabilizeState.finish()`의 접촉 인정식 `eef_z < shelf_z + 0.12`에 들어 있다. 새 state에서는 이 비교와 보상용 높이 필드를 제거한다. `height_limit=inf`로 기존 계통을 우회하는 구현은 하지 않는다.

선반 충돌 비용·손목 clearance를 포함한 선반 실패 판정·물체 낙하와 전도·팔 속도 종료는 보존한다. 사용자의 “EEF Z 제한 삭제”를 선반 보호나 물리 실패 조건 전부 삭제로 확대하지 않는다.

### 보존할 비용과 활성 term

기존 15개 활성 보상의 순서를 유지하고 새 `contact_formation`을 마지막에 추가하여 **총 16개**로 구성한다. 아래 항은 callable·params·weight까지 현재 v0와 일치해야 한다.

| 항목 | 보존 값 |
| --- | --- |
| Arm/Hand action rate | 각각 −0.03, 원시 action 차이 제곱합, raw cap 100 |
| Arm/Hand joint velocity | 각각 −0.03, 실제 관절 속도 제곱합, raw cap 100 |
| Shelf collision / failure | −0.5 / −3, 기존 callable·사건 dt 상쇄 보존 |
| Obstacle contact | −0.04, free force 50N, raw cap 100 |
| Wrench change | −0.1, free force change 30N·moment change 3Nm, saturation 2.5·sharpness 3, budget 없음 |
| Object tilt | −30, free angle 5°·fail angle 0.9rad |
| Obstacle displacement | −150, 총 제곱변위 cap 0.04 |
| Arm/Hand action limit | 각각 −3, raw cap 10; 손 normalized `[0,1]` |

Hold·별도 성공 보너스·단계 전환·압착·물체 가속도 비용은 추가하지 않는다. v1의 `arm_joint_failure` −3도 추가하지 않는다.

## Reset과 실행 순서

1. 새 독립 runtime의 필수 버퍼를 Manager 구성 전에 할당한다. 모든 초기 tensor는 finite 값으로 채우고 초기화 이전의 OBB를 실제 유효 관측으로 처리하지 않는다.
2. v0의 활성 자산·배치·목표·단일 Warp IK를 사용해 reset 대상 행만 준비한다. 원형 타겟 위치·목표 방향·6–12cm 목표 거리 분포를 유지한다. 목표를 OBB 중심 기준으로 재추출하거나 OBB offset만큼 이동시키지 않는다. 따라서 가시 중심에서 본 초기 목표 거리는 원래 샘플 거리와 다를 수 있다.
3. 해당 배치로 가시 OBB와 물리 source 연결을 만들고 필요하면 기존 target-only fallback을 적용한다. legacy 대표점 관측을 먼저 계산해 그 fallback이 장면을 바꾸도록 두지 않는다. 기존 reset 함수 전체를 호출한 뒤 OBB를 덧씌우는 방식은 부적합하다.
4. 최종 물리 pose·active mask·gravity·주차 위치·command를 확정한다. 초기 월드 OBB snapshot, 타겟 `T_OB`, mask·slot 순서를 저장한다.
5. 현재 EEF·손끝 pose를 읽고 `e_0`, `D_0`를 저장한다. 해당 행의 접촉 이력·물리 샘플·보상 캐시·metrics·손 이전 action을 초기화한다.
6. 물리 substep마다 실제 타겟 접촉을 capture한다. decimation 2의 마지막 sample에서 현재 추적 OBB로 policy-step Sweep 상태를 한 번 갱신한다. full rigid orientation을 사용하는 Formation·Reach도 같은 최종 상태 기준이다.
7. terminal 상태에서 종료·보상·지표를 계산한 뒤 해당 행만 자동 reset한다. terminal step의 이전 episode OBB를 새 snapshot으로 조기에 덮어쓰지 않는다.

모든 per-env cache는 부분 reset에서 해당 행만 바뀐다. `common_step_counter`만 전역적으로 초기화하거나 reset과 함께 비대상 행의 distance history를 지우지 않는다. reset은 물리 simulation step을 추가하지 않는다. step 경로에서는 OBB fitting·CPU NumPy 전송·USD 탐색을 하지 않는다.

새 OBB helper의 CPU reference는 작은 장면 검증에 사용할 수 있다. 학습 경로에서는 reset 대상 행을 batch 처리하고 정적 기하·body index·고정 Frame offset을 캐시한다. GPU 최적화 후에도 동일 채택 구간의 Box 기하는 reference와 수치적으로 일치해야 한다. 노출 필터 변경은 별도 비교 검증을 따른다. reset의 OBB 산출과 fallback 비용도 아래 collection 시간 목표에 포함한다.

## Collection 성능 요구사항

**정확한 구현과 collection 성능을 함께 완료 조건으로 삼는다. 1 iteration의 collection time은 10초 미만이어야 하며, 권장 목표는 5초 이하이다.** 이는 아직 달성한 측정값이 아니라 구현·최적화·실측으로 충족해야 할 요구사항이다.

### 측정 구간과 실행 조건

| 항목 | 기준 |
| --- | --- |
| 실행 | `scripts/train.py`, headless, 기본 2048환경, rollout 36 policy step, action/관측/물리/PPO 설정은 본 명세 그대로 |
| Collection 구간 | 실제 runner의 한 rollout 수집 구간. 정책·value 추론, 장애물 encoder, env.step, 물리·센서·보상·관측·rollout 저장 및 수집 중 발생한 자동/부분 reset 비용 포함 |
| Reset 비용 | 배치·IK·가시 OBB 생성·필터·fallback·snapshot 저장을 포함. reset이 없는 step만 골라 측정하지 않음 |
| 별도 보고 | 초기 simulator 생성·최초 reset·compile 시간, PPO learning time, logging/checkpoint 비용, 전체 iteration wall time |
| 환경 기록 | GPU/CPU·드라이버·Isaac Lab/PyTorch 버전·소스 commit·seed·thread 설정·동시 부하·debug/영상 설정과 측정 명령 |
| 비교 | 같은 장비·설정에서 `Inspire-Sweep-Single-Contact-v0`도 측정하여 collection 절대 시간과 증가분을 함께 기록 |

사용자가 말한 iteration 시간 목표는 **collection time**에 적용한다. 전체 iteration 시간은 collection 외 PPO update·logging 등을 포함하므로 분리해서 보고한다. 초기화가 끝난 뒤 첫 rollout인 iteration 0은 측정에 포함하며, 수집 중의 첫 kernel 실행이나 reset을 warmup이라는 이유로 사후 제외하지 않는다. 별도 steady-state 측정을 추가할 수 있으나 필수 판정을 대체하지 않는다.

### 통과 판정

최소 **iteration 0부터 연속 32회**의 실제 학습 collection 시간을 누락 없이 기록한다. 이 구간은 1152 policy step으로 기본 episode 500step을 넘으므로 정상 timeout과 자동 reset도 검증할 수 있다. 실제 reset 수·원인·batch 크기, 장애물 수와 OBB 조각 수를 함께 기록하고 정상 timeout 사례가 없으면 해당 부하를 추가 검증한다.

- 필수: 측정한 **모든 iteration이 10초 미만**. 평균만 10초 미만인 결과는 통과가 아니다.
- 권장: 같은 측정 구간의 **모든 iteration이 5초 이하**. 5초 초과·10초 미만이면 필수 통과와 권장 미달을 구분한다.
- 통계: 평균·중앙값·p95·최대와 iteration별 원값, baseline 대비 증가량을 기록한다. 소수점 반올림 로그만 있으면 반올림 오차 상한을 더해 경계를 판정한다.
- 정확한 계측: GPU 비동기 실행으로 시간이 과소 계상되지 않도록 runner의 timing 경계를 확인하고 필요 시 구간 경계에서 동기화해 대조한다. step마다 불필요한 강제 동기화를 넣지 않는다. baseline도 같은 방법으로 측정한다.
- 검증 범위: 장비가 달라지면 그 장비의 수치를 별도로 기록한다. baseline이 빠르다는 이유로 새 환경의 목표 달성을 추정하지 않는다. 성능 미측정 또는 10초 이상이면 성능 조건 미완료로 남긴다.

### 구현 우선순위

관측·보상은 device tensor의 batch 연산으로 계산하고, 다섯 손끝 pose 및 현재 추적 OBB transform을 policy step당 한 번 계산해 공유한다. OBB 관측 생성은 reset 행에만 적용한다. row별 Python loop·반복 CPU↔GPU 전송·`.item()`/`.tolist()`에 의한 잦은 동기화·USD/mesh 재탐색을 학습 경로에서 줄인다. CPU reference의 scene별 호출을 그대로 2048환경의 최종 학습 경로로 채택하지 말고 실측으로 판단한다.

병목은 물리·접촉 reduction·기존 접촉면 분류·OBB reset·손끝 변환·관측/보상·encoder로 나누어 진단한다. 기존 helper를 재사용해도 그 비용은 전체 목표에 포함된다. profiling 실행과 정상 학습 성능 측정을 분리하고, debug marker·영상은 두 환경 모두 끈 실제 headless 학습 조건에서 측정한다. 상세 진단은 집계·샘플링하여 host readback이 collection 병목이 되지 않게 한다.

환경 수·rollout 길이·물리 substep·활성 장애물 상한을 줄이거나 접촉·충돌 검사·보상을 생략하여 통과시키지 않는다. 허용된 OBB 노출 필터 변경은 위의 유사성 검증을 함께 충족해야 한다. 비용을 PPO update나 background 작업으로 옮겨 collection만 빠르게 보이게 하지 않도록 전체 iteration wall time도 대조한다.

## 성공 판정과 보존할 환경 설정

성공은 10초 timeout 시 추적 가시 OBB 중심과 목표의 XY 거리가 **3cm 이하**이고 같은 step에 물리 실패가 없는 경우다. 조기 목표 진입으로 episode를 끝내지 않는다. `target_goal_distance_xy_m`과 within-radius 지표도 동일 중심·동일 `<=`를 사용한다. 실제 물체 중심의 거리가 필요하면 별도 GT 진단 이름으로만 기록한다.

| 항목 | 계약 |
| --- | --- |
| 로봇·물체·선반 | 현재 v0의 자산과 물성, 타겟 원통, 고정 물리 pool 17개, 활성 장애물 최대6개 유지 |
| 물리/정책 간격 | 0.01s / 0.02s, decimation 2 |
| Episode | 10초, 500 policy step |
| 기본 병렬 수/간격 | 2048 / 2.5m |
| 제어 | 팔6D OSC, 손6D `[0,1]` 비율, 0 펼침·1 굽힘 |
| Action clip | PPO wrapper clip 없음, 실행 한계는 Action term에서 적용 |
| 초기 배치·IK | 현재 v0의 전 방향 Test reset·원형 타겟 반경2cm·단일 Warp IK 유지 |
| 실패 | 활성 물체 낙하/기울기0.9rad, 기존 선반 실패, 팔6관절 중 절대 속도1rad/s 초과 |
| 성공률 | 최근 최대10,000 완료 episode ring, 성공 수/timeout 수; 조기 실패를 timeout 분모에 추가하지 않음 |
| Curriculum | 빈 구성, 보상·장애물 일정 추가 없음 |
| PPO | rollout36, max iteration90,000, save50, epoch8, minibatch4, lr0.001 adaptive |
| PPO 추가 값 | gamma0.98, lambda0.95, clip0.2, value1, entropy0.005, KL0.02, grad norm1, init std1 |
| 로그 이름 | `inspire_sweep_prof_revision_v0` |

새 로그는 Reach의 거리·초과분·증분, Formation의 손가락별 gap·합·raw·실제 기여, Sweep의 가시 중심 거리·진행·후퇴·접촉·정렬·면 계수, OBB 생성시간·조각 수·fallback 수를 구분한다. 기존 학습 로그는 정리하거나 덮어쓰지 않는다.

## 구현 후 검증 기준

아래 검사는 **향후 구현의 완료 조건**이다. 문서 작성만으로 통과했다고 간주하지 않는다.

| 영역 | 필수 검증 |
| --- | --- |
| 등록·상속 | 새 ID만 추가, EnvCfg/runtime/model/PPO/Scene/state MRO에 기존 환경 계통 없음 |
| 전체 차이 | v0와 모든 Manager term·순서·params·weight, Scene·Action·Command·Event·종료·PPO를 비교하고 이 명세의 차이에만 대응 |
| 기존 환경 보존 | 수정 전후 Single Contact v0/v1/Zone3 및 공유 함수 caller의 설정·동작 보존 |
| OBB reference | 완전 노출·부분 가림·분리 조각·높이 다른 가림·회전 Box·선반 변환에 대해 동일 채택 구간의 Box 기하와 수치적으로 일치; 필터 변경에 따른 집합 차이는 별도 기록 |
| 필터 경계와 비용 | 최종 선택식의 문턱 아래/동일/위, 기존2cm·20%와 장면 bank 비교·가림 수준별 판정·fallback 분포·계산 시간, 탈락 물체의 occlusion 참여, 비활성 후보 제외 |
| 타겟 선택 | 가장 넓은 조각과 동률, source mapping, target-only fallback, 16슬롯 경계 |
| Snapshot 고정 | 물체만 움직이면 Actor OBB 불변; EEF만 움직이면 중심·quaternion 변환, 크기·mask·순서 불변 |
| 보상 추적 | 타겟 병진·회전으로 초기 일부가 이동, local `T_OB`와 크기 불변, 새 시야로 재산출하지 않음 |
| 자세 표현 | EEF roll/pitch·전체3D Box 꼭짓점 복원·quaternion 순서/부호·unit norm |
| 손끝 | 엄지→소지 순서, 모든 손가락에 동일 원점·축·transform·quaternion 생성 함수, 열린 손/굽힌 손/팔만 이동, pad 위치·축 marker, 관측과 보상 공통 결과 일치 |
| Shape와 encoder | policy108·obstacles176·latent124·action12·export284·손 관절→손끝 순서, invalid slot 쓰레기값 완전 차단, 전부 빈 장면 |
| 학습 연결 | actor/critic encoder 각각 gradient와 가중치 갱신, rollout 관측으로 재계산, 저장/로드·JIT 및 ONNX 사용 시 해당 export 검증 |
| Reach | 10cm 경계·양/음 대칭·정지0·왕복 합0·reset 첫 step·중복 조회·terminal step |
| Formation | 회전 박스 면/모서리/꼭짓점·내부/중심0거리, 다섯 거리 합, S=0 유한값, 단조 감소, dt 한 번 적용 |
| Sweep | 동일 입력에서 +50→+100·−10→−20 정확히2배, 가시 중심 변경·회전 offset, 이력2/3·현재힘·v0 방향·면 선호 보존 |
| 높이 | 같은 접촉·힘·진행 입력에서 EEF 상대 높이12cm 아래/동일/위의 보상 gate 결과 동일; 실제 고도 차이로 생긴 접촉 변화와 구분 |
| 성공 | OBB 중심 목표거리3cm 아래/동일/위, timeout 전후, 실제 중심과 OBB 중심이 다른 fixture, 동시 실패 제외 |
| Lifecycle | 전체/부분/자동 reset, 비대상 행 불변, 이전 distance·contact·snapshot 누출 없음 |
| 실제 실행 | 작은 GPU 환경 reset/step·부분reset·timeout, 2048환경 초기화/reset 비용, `train.py` 짧은 PPO 업데이트와 finite 결과 |
| Collection 성능 | 동일 장비 v0 대조, 2048환경×36step·iteration0부터 연속32회 전부10초 미만·권장5초 이하, 자동reset 포함·통계/원시 로그/전체 iteration 시간·측정 환경 기록 |

CPU 수식·계약 검사 후 GPU smoke와 짧은 학습을 수행한다. 장기 성공률, Contact Formation의 실제 비중, 목표 밖 정지 유인, 16D embedding의 충분성은 별도 실험 결과로 판단한다. GPU smoke 통과를 장기 학습 개선으로 보고하지 않는다.

등록된 환경의 학습 명령은 다음과 같다. 실제 검증 실행 조건과 산출물은 구현 로그를 따른다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Prof-Revision-v0 --num_envs 2048 --headless
```

## 코드 근거와 관련 기록

- [Single Contact v0/v1 EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_v0_envs.py), [runtime 진입점](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/sweep_v0.py), [공통 lifecycle](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/stabilize_sweep.py)
- [관측 구성](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations/stabilize_sweep.py), [초기 대표점 변환](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observation_functions/stabilize_sweep.py), [기존 encoder와 export](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/wrench_refactor_models.py)
- [Single Contact state와 v1 Reach](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/sweep_v0_state.py), [접촉 높이와 Sweep 상태](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_state.py), [보상 함수](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/stabilize_sweep.py), [면 선호](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/reward_functions/sweep_contact_preference.py)
- [reset과 fallback](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/stabilize_sweep.py), [기존 성공 판정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/termination_functions/stabilize_sweep.py), [기존 환경 계약](../../02_implementation/environments/SWEEP_V0.md)
- [명세 작성 개발 로그](../../02_implementation/logs/2026-11-23_prof_revision_v0_spec.md)
