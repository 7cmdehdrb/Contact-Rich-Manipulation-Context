# Fusion v1_0 — 장애물 관측 압축·좌우 정렬·순차 교환

[개발 로그 목록](README.md) · [환경 설명](../environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_0_ENVIRONMENT.md#24-주변-장애물-관측--40d) · [버전 비교](../environments/CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md)

기준일: 2026-10-22. Workspace HEAD `b5d22e3ff7f3452b203c0cc8fcd6880fc493c602`에서 사용자 요청으로 기존 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0`의 장애물 관측 순서만 변경했다. Task ID·상속 관계·입력40D는 유지한다.

## 최종 관측 처리

1. Reset에서 활성 장애물의 초기 robot-root XYZ에 축별±1cm 오차를 적용한다.
2. 기하학적 가시성35%와 별도의1% visibility flip으로 관측할 물체를 결정한다. 비활성 물체는 제외한다.
3. 관측 물체만 노이즈 포함 좌표의 **−root Y 오름차순**으로 정렬한다. 로봇이 선반을 향할 때 +root Y는 왼쪽이므로 좌→우 순서다. 동률은 stable sort로 처리한다.
4. 정렬된 물체를 앞쪽에 모으고 뒤는 전부0으로 만든다. Gray/White·물체 ID와 관측 슬롯의 고정 대응은 없다.
5. 점유된 `(0,1)`, `(1,2)`, … 쌍마다 독립10% 확률로 네 값 전체를 교환한다. 한 번의 좌→우 순회이며 뒤 단계는 앞 단계의 교환 결과를 사용한다. 빈 슬롯은 교환하지 않는다.
6. 최종40D는 Actor/Critic이 공유하며 episode 동안 고정한다. 부분 reset은 지정 환경만 재생성한다.

예를 들어 `A B C D X…`에서 첫 교환 후 `B A C D X…`가 되면 다음 쌍은 A/C다. 모든 교환이 발생하면 `B C D A X…`다. 물체가 여러 칸 이동할 수 있지만 mask는 항상 `1,1,…,1,0,…,0`이다. 정렬 뒤의 확률 교환이므로 최종 좌표 순서가 항상 단조일 필요는 없다.

물리적인 물체 컬렉션 순서·target ID·active mask·접촉 필터·보상/종료 대상을 변경하지 않았다. 관측 슬롯 순서와 물체 ID를 분리한다. 숨겨진 물체의 실제 좌표를 정렬에 사용하지 않는다.

구현은 [`events.py`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/contact_sweep_clutter_fusion.py)의 `pack_obstacle_observations`이며 visibility 처리 직후 적용한다. 기본 교환 확률은 [`events_cfg.py`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/events/contact_sweep_clutter_fusion.py)의 `observation_swap_probability=0.1`이다. Hydra에서는 `env.events.object_spawn.params.observation_swap_probability=0`으로 교환만 끄고 정렬·압축은 유지할 수 있다.

## 검증

Workspace 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  -q -p no:cacheprovider src/inspire_sweep_baseline/tests
```

**551 passed, 24.82초**, 기존 ONNX warning3개. 관련 population 단독 검사는28 passed였다. 추가 검사는 좌우 방향·XYZ 보존·빈 suffix, 모든 인접 교환의 연쇄, 0.1 경계의 비교, 빈/단일 관측·동률 순서, 20000개 환경의10% 표본 빈도와 seed 재현, 잘못된 확률 거부를 포함한다. 부분 reset·비활성 물체 제외·목표 분포 회귀도 통과했다.

실제 GPU 검증은 다음 명령으로 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  INSPIRE_SWEEP_SHELF_USD_PATH=/home/min/Desktop/Shelf_USD/Arena/Collected_speedrack_shape/speedrack_shape.usd \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_clutter_fusion_v1_0_probe.py \
  --headless --device cuda:0 --num_envs 4 \
  --output outputs/fusion_v1_0_observation_order_validation/probe.json
```

결과는 **exit0, passed**. [판정 JSON](../../../../outputs/fusion_v1_0_observation_order_validation/probe.json)의 모든 population 단계에서 연속된 presence prefix·빈 슬롯 전체0·활성 물체 수 이하의 관측 수를 확인했다. 물리적 비활성 상태, 실접촉, 가속도 상한, 부분/timeout reset, PPO2499/2500 update와 checkpoint 복원도 통과했다. 정렬·10% 교환의 정확한 수치는 위 CPU 결정적 검사로 확인했다.

환경 설명·버전 비교·활성 환경·패키지 README를 갱신했다. 문서6개의 수식·링크 검사(오류0)와 코드/문서 `git diff --check`가 통과했다. 장기 학습 성능이나 관측 순서 변경 전 정책의 성능은 검증하지 않았다. 기존 학습 로그를 수정하거나 정리하지 않았다.
