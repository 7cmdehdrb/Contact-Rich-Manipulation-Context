# Bounding Box 기반 텐서 배치 규칙

[개발·검증 기록](../logs/2026-10-31_bbox_scene_layout.md) · [환경 안내](../08_ACTIVE_ENVIRONMENTS.md)

2026-10-31 최초에는 독립 배치 모듈과 테스트를 구현했다. 이후 사용자 요청으로 [Final v0_2_1](FINAL_GOAL_ACCURACY_V0_2_1_ENVIRONMENT.md)의 reset에 전용 adapter를 연결했다. 다른 환경은 유지한다. `src/scene_randomization/generator.py`, `LOGIC.md`의 RED/Gray/White 의미와 전면 방향 손목 점유 규칙을 참고했다. 구현은 활성 패키지 `mdp/common/bbox_scene_layout.py`에 있으며 참고 패키지를 import하지 않는다.

## 기하 모델과 존

단위는 미터, 기본 작업판은 x=[-0.5, 0.5], y=[0, 0.4]이다. 로봇이 진입하는 전면은 y=0이다. 물체별 로컬 Bounding Box의 XY 반폭과 yaw로 회전 박스인 OBB를 구성한다. 타겟은 yaw를 유지한 채 시작점에서 목표까지 직선으로 이동한다고 가정한다. 높이·기울기·전도·동역학은 모델링하지 않는다.

| 존 | 새 규칙 |
| --- | --- |
| RED | 타겟 OBB의 전체 직선 이동 영역을 전면 방향 -y까지 확장하고 안전 여유를 적용한다. 장애물 OBB의 일부라도 이 영역에 침범하면 거절한다. 생성 상한은 항상 0이다. |
| Gray | RED의 바깥 확장 영역과 밀기 반대편 접근 직사각형을 합친 뒤 RED를 제외한다. 장애물 OBB가 이 상호작용 영역에 걸치면 Gray로 분류한다. |
| White | RED 및 Gray 상호작용 영역과 겹치지 않는 OBB만 허용한다. 실제 동역학적 무간섭을 보증하는 뜻은 아니다. |

이동 영역은 시작·목표 OBB의 convex hull이며 전면 확장도 볼록 영역으로 처리한다. 격자나 원형 외접 반경을 사용하지 않고 분리축 정리(SAT)로 박스와 이동 영역을 판정한다. 후보 중심이 존 바깥에 있더라도 박스 모서리가 RED에 걸리면 거절한다.

타겟–장애물 및 모든 장애물 쌍에는 `finger_gap` 이상의 분리축 간격을 요구한다. 이는 최소 유클리드 표면 간격도 보장하며 모서리 부근에서는 보수적으로 거절할 수 있다. 기본값은 **20mm**이다. 이는 손가락 여유에 대한 설정값이며, 실제 손가락 전체의 진입 경로나 로봇 운동학을 증명하지 않는다. 기존 생성기의 원형 손가락 접근 궤적·셀별 밀도·후방 최소 개수 조건은 새 모듈의 계약에 포함하지 않는다.

## 설정

| 매개변수 | 기본값 | 의미 |
| --- | --- | --- |
| `gray_padding` | 0.060m | RED 외곽에서 Gray 영역을 추가 확장하는 폭. 증가해도 RED는 변하지 않는다. |
| `max_gray` / `max_white` | 4 / 5 | 존별 슬롯 용량 및 생성 상한 |
| `finger_gap` | 0.020m | 초기 OBB 쌍의 최소 간격 |
| `red_margin` | 0.003m | 타겟 이동·손목 점유 영역의 추가 안전 여유 |
| `wall_margin` | 0.005m | 작업판 경계와 박스 사이 여유 |
| `rear_length` / `rear_width` | 0.160 / 0.220m | 밀기 반대편 Gray 접근 직사각형. 둘 중 하나가 0이면 비활성 |
| `candidates` | 32 | 각 슬롯 시도에서 동시에 검사할 위치·yaw 후보 수 |
| `restarts` | 4 | 장면마다 병렬 탐색할 독립 배치 수 |
| `passes` | 2 | 실패 슬롯을 다시 시도하는 횟수 |

`gray_padding`은 **길이 단위의 바깥 확장 폭**이다. 기존 Final의 `gray_red_padding_fraction`과 다른 매개변수이므로 기존 값을 그대로 대입하지 않는다. 타겟 이동 거리가 0인 경우 후방 방향은 +x를 기준으로 정의된다.

## 수량 부족 처리와 탐색 예산

환경별 요청 `requested[B,2]`를 존별 상한으로 제한한다. 물체 슬롯은 Gray, White 순서로 제공하며 각 존의 요청 개수만큼 앞 슬롯이 배치 대상이다. Bounding Box는 주어진 슬롯의 물체에 대응하며 다른 형상으로 교체하지 않는다.

각 restart에서 슬롯 순서를 바꿔 탐색한다. 한 물체가 배치되지 않아도 다음 물체를 계속 검사하고, 다음 pass에서 실패 슬롯을 재시도한다. 완료한 restart 중 **총 배치 개수가 가장 큰 결과**를 반환한다. 동률이면 Gray 수가 많은 결과를 선택한다. 서로 다른 restart의 물체를 합치지 않는다. 요청 0개 또는 모든 후보가 불가능한 장면도 정상 반환한다.

사용자가 승인한 기준은 **제한된 탐색에서 찾은 최다 배치**다. 연속 공간의 수학적인 최대 개수 또는 물리적 불가능성을 증명하지 않는다. `complete=False`는 탐색 예산 안에서 요청을 다 채우지 못했다는 뜻이다. 실패 시 타겟·목표·존·간격을 변경하지 않는다. `candidates × restarts × passes`가 시간 대신 일정한 작업량 상한을 설정하며 실제 소요 시간은 장치와 입력 크기에 따라 달라진다.

## API와 reset 연결 준비

`generate_layout`은 순수 PyTorch 함수다. 입력과 반환값은 같은 device에 남는다. 환경·restart·후보를 텐서 축으로 계산하고 Python 반복은 슬롯·pass 축에만 사용한다. 탐색 중 `.cpu()`, `.numpy()`, `.item()` 또는 환경별 Python 반복이 없다. 기본 입력 검증에는 GPU 동기화가 포함되므로 신뢰할 수 있는 전처리 결과를 사용할 때만 `check_inputs=False`를 적용한다.

| 입력 | 형상·의미 |
| --- | --- |
| `target`, `goal` | `[B,2]`, 타겟 footprint 중심의 시작·목표 위치 |
| `target_half` | `[B,2]`, 로컬 XY 박스 반폭 |
| `target_yaw` | `[B]`, 라디안 |
| `obstacle_half` | `[B,max_gray+max_white,2]`, 슬롯별 반폭 |
| `requested` | 정수 `[B,2]`, 생략하면 각 존의 최대 수량 |
| `generator` | 같은 장치의 `torch.Generator`; 상태를 재사용하면 연속 추첨 |

출력은 `LayoutResult`다. `centers[B,M,2]`, `yaw[B,M]`, `active[B,M]`, `zones[M]`, `requested[B,2]`, `actual[B,2]`, `complete[B]`를 제공한다. **비활성 슬롯의 좌표 0은 스폰 위치가 아니다.** 호출자는 `active`를 사용하여 배치하거나 비활성 물체를 격리해야 한다. 원래 슬롯 인덱스는 유지되며, 부분 reset은 해당 env의 입력만 잘라 전달하고 같은 env_ids에 결과를 써야 한다. 생성기는 환경 상태나 입력 tensor를 수정하지 않는다.

비대칭 로컬 박스는 `footprint_from_bounds(bounds, yaw)`로 반폭과 회전된 중심 offset을 계산한다. bounds에는 실제 scale이 이미 한 번 적용돼 있어야 한다. 계획 입력은 `asset_root_xy + offset`, 물리 pose는 `planned_center - offset`으로 변환한다. 타겟 목표도 동일한 기준으로 변환한다.

기존 선반 좌표를 연결할 경우 board 좌표는 `(shelf_y, 0.20 - shelf_x)`이고 yaw는 `shelf_yaw - pi/2`다. 역변환은 `(0.20 - board_y, board_x)`다. 방향과 단위를 변환하지 않고 기존 shelf XY를 바로 전달하면 전면 점유 방향이 틀어진다. USD bounds 읽기와 scale 적용은 초기화 또는 타겟 선택 시에 처리하고, reset hot path에는 device tensor를 전달한다. v0_2_1 연결은 `final_obb_geometry.py`와 [별도 검증 기록](../logs/2026-10-31_final_v0_2_1_obb_reset.md)을 따른다.

```python
from inspire_sweep_baseline.mdp.common.bbox_scene_layout import LayoutConfig, generate_layout

cfg = LayoutConfig(gray_padding=0.06, max_gray=4, max_white=5)
result = generate_layout(target, goal, target_half, target_yaw, obstacle_half,
                         cfg=cfg, requested=requested, generator=rng)
# result.active인 슬롯만 result.centers / result.yaw를 사용한다.
```

위 import는 Isaac Lab 환경의 패키지 초기화 이후 사용한다. 시뮬레이터 없이 실행하는 검증 도구는 모듈 파일을 직접 로드한다.

## 검증·성능

conda `env_isaaclab`, PyTorch 2.7.0+cu128, RTX 4070에서 **22개 테스트 통과**. 별도 NumPy 다각형 vertex projection·선분 거리 검사로 304개 장면(CPU 24 + CUDA 24 + 무작위 256)의 박스 경계·존·최소 간격을 검사했다. 이외에 수량 상한·불가능 물체 후속 배치·0개·seed·입력 불변·비대칭 bounds·padding 단조성·퇴화 경로·CPU/CUDA 판정 일치를 검사했다.

다음은 최적화 후 기본 설정(4 Gray + 5 White, 32 후보 × 4 restart × 2 pass)의 5회 측정 중앙값이다. 입력 생성·검증·시각화·물리 reset은 제외하고 CUDA 완료를 동기화했다.

| 장치 | 장면 수 | 배치 생성 시간 |
| --- | --- | --- |
| CPU, 4 threads | 1 | 25.97ms |
| CPU, 4 threads | 512 | 468.61ms |
| RTX 4070 | 512 | 63.37ms |
| RTX 4070 | 2048 | 96.72ms |

2048장면에서 PyTorch peak allocated memory는 약 103.86MiB였다. GPU 전체 메모리나 Isaac Sim 메모리 수치가 아니다. 작은 GPU batch는 kernel launch 비용과 실행 변동이 커서 CPU보다 빠르다고 가정하면 안 된다.

512장면 기본 설정의 마지막 측정 배치는 전부 4+5개를 채웠다. 예산을 16 후보 × 1 restart × 1 pass로 낮추면 31.45ms였지만 요청 완성률은 48.83%였다. 10+10개 과밀 요청에서는 138.85ms, 평균 Gray 8.61 / White 10.00개, 요청 완성률 12.89%였다. 이는 정해진 synthetic 분포의 결과이며 실제 asset 및 학습 collection 성능으로 일반화하지 않는다.

```powershell
conda run --no-capture-output -n env_isaaclab python -m pytest src/inspire_sweep_baseline/tests/test_bbox_scene_layout.py -q --basetemp outputs/pytest_bbox_layout_check
conda run --no-capture-output -n env_isaaclab python src/inspire_sweep_baseline/scripts/benchmark_bbox_layout.py --output outputs/bbox_scene_layout_check
```

workspace의 `outputs/bbox_scene_layout_optimized/benchmark.json`, `gallery.png`, `gallery.npz`에 측정·배치 예시를 저장했다. 그림 배경은 점 footprint의 존이며 실제 장애물은 전체 OBB로 검사한다. 이 절의 측정은 독립 모듈 기준이며 v0_2_1 reset 연결 결과는 위 별도 검증 기록에 구분했다. 정책 학습은 실행하지 않았다.
