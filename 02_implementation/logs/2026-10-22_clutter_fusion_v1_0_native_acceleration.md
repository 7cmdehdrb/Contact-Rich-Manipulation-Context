# Fusion v1.0 — 가속도 비용 상한·PhysX 직접 가속도

[개발 로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [앞선 수정](2026-10-22_clutter_fusion_v1_0_population_recovery.md)

2026-10-22 사용자 요청으로 기존 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0`의 가속도 비용 발산 방지와 Isaac Lab 직접 가속도 API를 확인했다. Workspace HEAD는 `a2fcb0b77a234a14db8b6fc9c91cfef4c4229092`이며 앞선 미커밋 환경 구현·사용자 변경을 보존했다. 새 task·CFG·상속 관계는 추가하지 않는다.

## 상한 점검

기존 `ObjectAccelerationPenalty`는 `_exponential_speed_excess_limit`을 사용한다. `max_cost=100.0`이고, 지수 평가 전에 초과량을 `0.5 * log(201)` 이하로 제한한 뒤 출력도100으로 제한한다. 따라서 유한한 매우 큰 입력뿐 아니라 norm overflow도 exp overflow로 이어지지 않는다. NaN/Inf 가속도 크기는 양의 무한대로 변환하여 유효한 활성 샘플의 비용을100으로 포화시킨다.

```text
a = norm(acceleration_xyz)
excess = clamp(a - free_acceleration, 0, 0.5 * log(201))
cost_per_object = min(0.5 * expm1(2 * excess), 100)
cost = sum(cost_per_object for eligible active objects)
```

상한은 weight·RewardManager의 step_dt 적용 전 raw 값이다. 시작3개 물체이면 합계 최대300, 최종7개이면700이다. 별도의 합계 clamp는 없지만 물체 수와 물체당 상한으로 전체 비용도 유한하다. 현재 포화 가속도는 `free_acceleration + 2.65165` m/s²로 시작 약2.95165, 최종 약2.70165다. 사용자 조건은 **상한이 없을 때만0.5m/s²에서 MAX를 설정**하는 것이므로, 이미 존재하는 상한·지수 곡선·weight−1·임계값 커리큘럼은 유지했다.

## Isaac Lab API와 변경

로컬 framework의 [`RigidObjectCollectionData`](../../../../IsaacLab/source/isaaclab/isaaclab/assets/rigid_object_collection/rigid_object_collection_data.py)는 `object_com_lin_acc_w`를 제공한다. 형태는 `[num_envs, num_objects, 3]`, 단위는 m/s²이며 월드 좌표계의 질량중심 선가속도다. `object_com_acc_w`가 `root_physx_view.get_accelerations()`를 조회하고 linear XYZ를 노출한다. 별도 센서를 추가할 필요가 없다.

[`reward_functions.py`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_0/reward_functions.py)의 가속도 입력을 해당 API로 교체하고 `_previous_velocity`와 `/step_dt` 차분을 제거했다. 벡터 norm을 사용하여 가속·감속·방향 변화 모두 양의 크기로 평가한다. `_previous_valid`는 속도 이력이 아니라 reset/새 활성화의 첫 샘플 제외용 boolean으로만 유지한다. 부분 reset·동일 step 캐시·비활성 물체 제외도 유지한다.

샘플링 의미는 바뀐다. 이전 값은 제어 주기의 속도 차분으로 얻은 평균 가속도였고, 현재 값은 마지막 물리 step의 PhysX 가속도다. 제어 주기 내 모든 substep의 최대값이나 평균을 누적하지 않는다. 학습된 정책의 보상 분포나 장시간 안정성이 동일하다는 주장은 하지 않는다.

## 실제 검증

Workspace 루트에서 다음 CPU 명령을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  -q -p no:cacheprovider src/inspire_sweep_baseline/tests
```

결과: **543 passed, 23.77초**, 기존 ONNX deprecation warning3개. 변경 보상 단독 검사도26 passed였다. 가속도 벡터 norm·양/음 대칭, 속도 값과 step_dt에 독립적인 직접 입력, 매우 큰 값·NaN/±Inf의 상한, 활성 물체별 합산, 부분 reset과 새 활성화의 첫 샘플 제외를 검사했다.

다음 실제 GPU 명령도 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  INSPIRE_SWEEP_SHELF_USD_PATH=/home/min/Desktop/Shelf_USD/Arena/Collected_speedrack_shape/speedrack_shape.usd \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_clutter_fusion_v1_0_probe.py \
  --headless --device cuda:0 --num_envs 4 \
  --output outputs/fusion_v1_0_native_acceleration_validation/probe.json
```

결과: **exit0, passed**. [판정 JSON](../../../../outputs/fusion_v1_0_native_acceleration_validation/probe.json)에11개 검사를 기록했다. 직접 API와 PhysX 원본 XYZ 일치, 실제 비용과 독립 지수식 일치, 활성 수×100 상한,12개 물리 step, 부분/timeout reset, 장애물 개수 전체 경계·실제 손 접촉, PPO2499/2500 update 및2500 checkpoint 커리큘럼 복원을 통과했다. 산출물은 새 outputs 폴더에 기록했고 기존 학습 로그는 변경하지 않았다.

활성 코드·문서의 `git diff --check`와 변경 문서5개의 수식·링크 검사는 모두 통과했다(링크 오류0). 전체 학습·장기간 발산 여부·정책 성능은 이번 짧은 검증 범위에 포함하지 않는다.
