# Relative-IK-v0/v1 구현·검증

## 최종 후속: 사전 검증으로 영역 확정, reset 품질 필터 비활성화

사용자는 매 reset의 SVD·재추출 비용 대신 여러 실험으로 안정적인 영역을 확정하도록 요청했다. 최종 IK-v0/v1은 전면 바깥8–10cm, 물체 좌우10–18cm, 기본 높이−1~+3cm다. 회전은 동일하다. 이전8–13cm의 바깥쪽3cm를 제외했으며 박스는2×8×4cm로 자동 갱신된다. IK-v0 event params에서 max_condition/joint_margin/max_attempts override를 제거하여 기본 `max_condition=None`, `max_attempts=1`을 사용한다. SVD와 후보 재추출 분기는 실행하지 않는다. 후보1개를 샘플링하여 IK를1회 호출하되 solver 내부 반복과 수렴 실패 검사는 유지한다. helper와 선택적 필터 구현은 진단·비교용으로 남아 있다.

### 실험과 선정 근거

- 기존 확대 범위의 필터를 끈 seed102에서 조건수82.10 후보가 나왔다. 단순히 필터만 끄는 방법은 채택하지 않았다.
- 좌우 offset만 좁히거나 높이 상한을+1/+1.5/+2cm로 낮춘 격자도 특이점 근접 후보가 남았다. 선반 local X 약0.311m 부근이 문제였다. 최초 탐색의 Y=0 포함 넓은 격자는 실제 분포 바깥도 포함하므로 최종 근거에서 제외했다.
- 실제 물체 초기 Y 범위±2cm와 offset10–18cm를 합친 두 구간 Y∈[−0.20,−0.08]∪[0.08,0.20], X∈[0.28,0.30], Z∈기본높이+[−0.01,0.03]m를 검증했다.
- 최종 경계 포함 격자37,570개(17×65×17×좌우2)와 seed819/1201/9017의 랜덤49,152개, 합계86,722개 모두 수렴 및 오프라인 품질 기준 통과. 정규화 조건수 최대58.609, 관절 한계 최소 여유0.875rad. 정규화 및 평가 기준은 아래 이전 구현 기록과 동일하다.
- 실제16환경×24개 seed(100–123)에서 필터 유/무 각각384개 초기화 및 직후8step을 수행했다. 양쪽 모두 실패 종료0, 최대 조건수52.631, 최소 관절 여유0.895rad였다. 재추출 없는 최종 설정에서도 검사 기준을 충족했다.

| reset 비교 | 중앙값 | 평균 |
| --- | --- | --- |
| 이전 확대 영역8–13cm + 필터 | 225.00ms | 244.09ms |
| 확정 영역8–10cm + 필터 | 140.28ms | 144.11ms |
| 확정 영역8–10cm, 필터 없음 | 138.55ms | 139.28ms |

동일 RTX4070에서16환경 전체 reset을 CUDA 동기화해 측정했다. 목표·장애물 재배치 등 reset 전체 시간을 포함하며 박스 표시는 비활성화했다. 필터 유/무는 동일 seed와 영역에서 순차 비교했다. 최종 중앙값은 이전 확대 영역 대비 약38% 감소했으나, 이는 전체 rollout collection 처리량 개선율이 아니다. 동일 확정 영역에서 필터 유무 차이는 약1.2%라서 이전 비용 대부분을 SVD 때문이라고 단정하지 않는다. 초기화·캐시·순서 효과가 있는 단일 장비 측정이며 모든 학습 배치 크기에 일반화하지 않는다.

산출물은 workspace `outputs/relative_ik_validation/`의 `calibration_console.txt`, `grid.json`, `grid2.json`, `calibration_final.json`, `calibration_final_console.txt`와 실행 스크립트 `calibrate_final.py`다. 마지막 스크립트의 필터 유 비교는 현재 기본 설정을 명시적으로 override한다. 최종 EnvCfg 전체 비교에서 허용 차이는 reset params뿐이며 나머지 관측·보상·종료·PPO·부모v2_7은 유지한다. CPU93개 테스트를 통과했다. 최종 버전별 probe는 `fixed_v0.txt`, `fixed_v1.txt`로 기록한다.

연속 영역 전체나 임의의 새로운 로봇·선반 자세에 대한 보장은 아니다. 실제 물리 검증은 선택한 배치와 reset 직후의 짧은 동작을 대상으로 하며 장기 학습·전체 collection 벤치마크는 수행하지 않았다. 추후 자산·default 자세·물체 spawn 반경을 변경하면 영역을 재검증해야 한다.

## 후속: 초기 위치 범위 확장과 특이점 근접 후보 제외

사용자가 선반 쪽·높이·좌우 범위를 적절히 넓히되 특이점에 가까운 시작 자세를 고려하도록 요청했다. IK-v0 reset event params만 override하고 IK-v1이 상속한다. v2_7의 기존 분포와 동작은 보존한다.

| 항목 | 이전 | 이후 |
| --- | --- | --- |
| 선반 전면 바깥 거리 | 10–13cm | 8–13cm |
| 물체 좌우 거리 | 10–14cm | 10–18cm |
| 기본 EEF 높이 대비 | −1~+1cm | −1~+3cm |
| 회전 | 기본 자세 고정 | 동일 |
| 양쪽 박스 각각 크기 | 3×4×2cm | 5×8×4cm |

깊이는 이전 v2_7의4–7cm 바깥 후보에서 초기 접촉 문제가 있었던 기록을 고려해8cm까지로 제한했다. 후보 부피는 이전 대비 약6.67배다. 높이 offset1cm와 jitter2cm를 함께 적용하며 박스도 동일한 offset과 범위를 받는다. 목표 좌우 분기·관측·보상·14cm 높이 gate·종료·PPO는 변경하지 않았다.

IK 수렴 후 실제6축 Jacobian의 병진 행을0.3m 특성 길이로 나누어 회전 행과 함께 SVD한다. 정규화 조건수80 이하, 모든 Arm 관절의 하한/상한 여유0.05rad(약2.86도) 이상인 해만 수용한다. 최소 특잇값이1e-8 이하이거나 비유한 값이면 제외한다. 이는 이번 작업의 공학적 필터 기준이며 동역학적 안전성이나 충돌 회피의 보장은 아니다. 부적합 환경만 같은 전용 RNG로 다시 샘플링해 최대16개 후보를 시도하며, 수용된 환경의 후보는 바꾸지 않는다. 끝까지 실패하면 조건을 완화하거나 잘못된 기본 자세로 대체하지 않고 오류를 낸다. 결과 분포는 균등 후보 분포를 품질 조건으로 제한한 분포다.

전체 config 대조는 IK-v0의 reset event params와 기존 시각화 flag·관측 변경만 허용하며 부모 v2_7 보존을 확인한다. CPU93개 테스트 통과, 특이 Jacobian과 관절 한계 근접 후보 제외 테스트를 추가했다. GPU에서 각 버전4환경×32개 seed(42–73), 총256개 초기화의 수렴·조건수·관절 여유와 reset 직후4step 무실패를 확인했다. 양쪽 비물리 박스의 갱신된 크기·EEF 포함·부분 reset 격리, Actor/Critic 모델, 추가32step·일반 Timeout 검사도 통과했다. 출력은 workspace `outputs/relative_ik_validation/expanded_v0.txt`, `expanded_v1.txt`다. 모든 위치·배치의 충돌 부재, 장기 학습 성공률, GUI 가독성은 미검증이다.

## 후속: 양쪽 IK 초기 위치 영역 시각화

사용자 요청에 따라 IK-v0에 `debug_initial_ik_bounds=True`를 추가했으며 IK-v1에 상속된다. 기존의 임시 Reaching Point 미표시 조건은 그대로다. `reset_robot_from_goal_ik`에서 IK 적용 후 동일한 target/default local pose, 선반 pose와 실제 샘플링 params를 runtime 표시 함수에 전달한다. 양쪽 영역을 모두 표시하며 물체 오른쪽은 하늘색, 왼쪽은 주황색이다. default 크기3×4×2cm의 각 박스를1mm 두께12개 Cuboid edge로 그린다. 두 prototype 모두 `collision_props=None`, `rigid_props=None`이고 실제 USD에서도 CollisionAPI/RigidBodyAPI가 없음을 확인한다.

변경 전 IK-v0/v1에는 이 시각화가 없었다. 변경 후 EnvCfg의 추가 차이는 표시 flag 하나이며 기존 전체 dict 대조에 이 flag만 반영했다. 부모 v2_7 및 다른 Relative 환경은 flag가 없어 표시 함수를 호출하지 않는다. 관측·보상·종료·IK 샘플링·PPO 설정은 보존한다. 독립 RNG를 추가로 소비하지 않으며 부분 reset은 해당 환경의 박스만 갱신한다. 현재 물체 이동을 따라가지 않고 해당 에피소드의 초기 샘플링 영역으로 유지한다.

CPU92개 통과. 두 버전의4환경 GPU probe에서 실제 박스의 두 방향·크기, 초기 EEF의 영역 포함, Collider/RigidBody 부재, 부분 reset 격리와 기존32step·모델·Timeout 검증을 실행했다. 로그는 workspace `outputs/relative_ik_validation/bounds_v0.txt`, `bounds_v1.txt`다. GUI 화면의 가독성은 별도 육안 검증하지 않았다. 장기 학습은 실행하지 않았다.

## 요청과 의도

왼쪽 밀기 실패에 초기 Arm 자세가 영향을 주는지 비교할 수 있도록 Relative-IK 계열을 추가했다. v2_7의 목표 반대편 IK 초기화를 재사용하되 Actor/Critic 모두 초기 물체 관측만 받는다. IK-v1은 IK-v0 직접 자식으로 접촉 조건부 Distance와 보상·성공 종료 제거를 적용한다. [최종 환경 계약](../environments/WRENCH_REFACTOR_RELATIVE_IK_ENVIRONMENTS.md).

작업 기준은 workspace HEAD `96f95f5`와 직전 완료된 미커밋 v2_7 구현이다. 기존 변경과 독립 서브모듈 상태를 보존했다. 학습 로그와 체크포인트를 수정하지 않았다.

## 변경 전후와 최종 대조

| 대상 | 변경 내용 |
| --- | --- |
| IK-v0 EnvCfg | v2_7 직접 상속; observations만 기존 Relative-v0 공유 관측으로 교체 |
| IK-v0 PPO | Relative-v0 runner 상속; experiment_name만 변경; Actor/Critic 모두 policy+obstacles |
| IK-v1 EnvCfg | IK-v0 직접 상속; Distance 함수와 params 변경, Contact/Hold/최초 진입/성공 보상 None, target_goal_success 종료 None |
| IK-v1 PPO | IK-v0 runner 직접 상속; experiment_name만 변경 |
| Gym 등록 | `Inspire-Wrench-Refactor-Relative-IK-v0`, `Inspire-Wrench-Refactor-Relative-IK-v1` |
| 재사용 | 기존 IK reset/runtime과 contact_gated_displacement_cosine_goal_distance 함수; 이 요청 때문에 공통 구현을 변경하지 않음 |

사용자의 ‘3초 누적 Timeout’은 기존 코드에서 목표 내부 저속 상태가 연속3초 유지될 때의 `target_goal_success`다. IK-v1에서 이 항만 제거하고 일반10초 `time_out` 및 실패 종료를 유지했다. 역방향 페널티도 유지한다. Reaching은 원래 물체 기준10cm이며 임시 마커는 생성하지 않는다.

기존 Relative-v3는 현재 이동 방향 cosine/weight25지만, 명시된 IK-v0 상속 및 변경 목록에 따라 IK-v1은 누적 cosine/weight5를 유지했다. weight5/25 선택을 선택적 질문으로 제시했고 답변이 없는 상태에서 부모5 유지로 진행한다고 안내했다. 최종 응답에도 이 차이를 명시한다.

## 검증

CPU 검증은 `tests/test_wrench_refactor.py` 및 `tests/test_wrench_refactor_ik.py`에서 **92 passed**다. 전체 설정 dict 비교로 허용한 항목 외 차이가 없고 부모 및 새 부모 인스턴스가 변하지 않았음을 확인했다. 기존 IK FK/Jacobian·수렴 테스트를 함께 실행했다. 추가 수치 테스트는 누적 cosine과 현재 이동 cosine의 구분, 역방향 누적 이동, 목표 안 무접촉, 오래된 센서, EEF 높이 경계를 확인한다.

GPU 검증은 `tests/_wrench_refactor_relative_ik_probe.py`로 버전별4환경/seed42에서 순차 실행했다.

- 실제 Isaac Lab configclass 전체 dict와 PPO 설정 비교 통과.
- Actor/Critic 입력 그룹이 policy+obstacles로 동일하고 별도 critic 현재 타겟 그룹이 없음.
- 실제 물체 위치를 옮긴 뒤에도 초기 물체 관측이 유지됨.
- 실제 Actor/Critic 모델 forward/backward, 출력 크기·finite gradient 확인.
- 각 버전32 control steps 관측·보상 finite, 예상치 못한 종료 없음.
- 에피소드 길이 경계를 설정해 일반10초 Timeout이 두 버전 모두 활성임을 확인.
- 활성 reward/termination 목록 및 임시 Reaching Point 마커 미생성 확인.

출력은 workspace `outputs/relative_ik_validation/v0_console.txt`, `v1_console.txt`다. 각 로그의 `CONFIG_PARENT_SHARED_PPO_OK`, `INITIAL_ONLY_OBS_AND_ACTOR_CRITIC_FORWARD_BACKWARD_OK`, `GPU_IK_SHARED_OBS_32_STEPS_TIMEOUT_OK`를 확인했다. v0 PowerShell stderr 리다이렉션은 Gym의 버전 경고를 NativeCommandError로 기록했으나 모든 probe assertion은 완료했다. v1은 subprocess로 stdout/stderr를 파일에 직접 수집했으며 process exit0이다.

첫 v0 probe는 PPO config의 deprecated `stochastic` 필드를 모델에 직접 전달하여 실패했다. 학습 스크립트와 동일한 `handle_deprecated_rsl_rl_cfg` 변환을 probe에 적용한 뒤 위 검증이 통과했다. 환경이나 PPO 설정을 오류 회피 목적으로 변경하지 않았다.

변경 Markdown4개 수식 검사 및 링크 검사(오류0), workspace와 문서 저장소 `git diff --check`를 통과했다. 문서 실제 렌더링은 검사하지 않았다.

장기 학습, PPO optimizer update, 정책 성공률 및 왼쪽 밀기 개선 여부는 이번 검증에 포함하지 않았다. IK 자체의 다수 seed·4096개 배치·부분 reset 검증은 변경 없이 재사용한 [v2_7 기록](2026-11-08_relative_v2_7.md)을 따른다.
