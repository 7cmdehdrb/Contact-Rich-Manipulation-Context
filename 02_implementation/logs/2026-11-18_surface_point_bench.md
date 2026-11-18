# 정면 대표 표면점과 관측 OBB 비교 벤치

## 요청·범위

사용자는 실제 환경에서는 segmentation/depth로 얻을 “정면에서 보이는 표면의 대표 좌표”를 이미지 생성 없이 기하적으로 테스트하고, 추정 위치의 시각 표시와 기존 3D bounding box를 함께 비교하도록 요청했다.

별도 `src/surface_point` 패키지를 추가했다. 기존 `observed_obb`·`centroid_belief`·baseline 및 학습 환경의 코드·데이터를 변경하지 않았다. Simple의 자산과 정지 배치만 읽기 전용으로 재사용하며 최종 환경·정책·제어에 연결하지 않았다. 커밋하지 않는다.

첫 벤치의 형상은 기존 관측과 동일한 upright OBB 근사다. 실제 메쉬 표면을 교차 검사한 결과가 아님을 UI·README·사용자 진행 설명에 명시했다. Fixture 장면은 실제 표시도 박스로 만들어 형상과 계산이 일치한다. Simple 장면에서는 박스 앞면의 점이 곡면 메쉬에서 떠 보일 수 있다.

## 계산과 비교 계약

관측자는 +X에서 −X를 바라보는 고정 직교 투영이다. XY 형상 경계와 교차점에서 Y를 나누고 박스 상하단에서 Z를 나눠 유한한 높이의 정면 가림을 계산한다. 픽셀 그리드·이미지·segmentation 모델·depth 렌더링은 사용하지 않는다.

같은 물체의 노출 셀들을 변을 공유하는 4방향 연결로 묶어 독립 관측으로 취급한다. 각 연결 영역의 YZ bbox 중심에서 대상이 실제 첫 표면인지 확인한다. 중심이 가려진 경우 가까운 노출 셀 내부로 보정하고 최대 1 μm 안쪽 여유를 둔다. 그 Y에서 원본 박스 앞면 X를 계산해 XYZ 표면점을 반환한다. 기존 2 cm·20% 횡폭 필터를 유지하며 면적/높이 필터는 추가하지 않았다.

기존 OBB 관측은 기존 함수를 그대로 호출한다. 기존은 가림 물체 높이 무한, 새 방식은 실제 박스 높이 유한이다. 따라서 낮은 장애물 위쪽으로 연결되는 영역에서는 관측 개수부터 달라질 수 있다. 비교를 위해 기존 결과를 새 방식에 맞춰 수정하지 않는다.

- 빨간 구: 대표 표면점. 중심은 계산 위치 그대로, 반지름 4 mm의 비충돌 표시.
- 초록 선: 기존 부분 관측 3D OBB.
- 파란 구·선: 대응 OBB 중심과 새 점 사이 차이.
- 주황 선: 원본 전체 OBB 참고.
- `center delta`: 기존 OBB 중심과 표면점 사이 3D 거리. 표면과 내부 중심이므로 0을 목표로 하는 오차가 아니다.
- `front delta`: 같은 YZ에서 기존 OBB 앞면 X와 표면점 X 사이 절대 차이.
- `center correction`: bbox 중앙에서 실제 노출 영역으로 이동한 YZ 거리.

대응은 벤치 내부 source index와 횡방향 노출 구간으로 평가하며, 새 관측 ID와 기존 관측 ID를 같다고 가정하지 않는다. source index는 비교 메타데이터이고 `SurfaceObservation`에 포함하지 않는다. 대응이 없으면 `unmatched`로 남기며 다른 물체에 강제 대응하지 않는다.

## 실행과 산출물

Workspace 루트에서 실행한다.

```bash
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/surface_point/scripts/show.py --scene simple --seed 0
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/surface_point/scripts/show.py --scene fixtures
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/surface_point/scripts/evaluate.py
```

뷰어는 새 배치/다음 fixture·재관측·각 표시 토글·정면/사선 카메라 버튼을 제공한다. 일반 실행은 닫을 때까지 유지한다. `--validate`는 여러 배치에서 재관측 결정성·토글·비충돌을 검사하고 JSON 기록 후 자동 종료한다.

사용법과 API는 [패키지 README](../../../../src/surface_point/README.md)에 정리했다. `outputs/surface_point/`의 `comparison.png/pdf`, `metrics.csv`, `fixtures.json`은 CPU 사례 결과이고, `fixtures_gpu.json`, `simple_gpu.json`은 GPU 검증의 원시 결과다.

## 실제 검증

- 새 geometry 7개 및 기존 observed_obb 22개, 총 29개 테스트 통과(0.17초). 앞면 위치, 분리 관측, 중심이 가려지는 경우의 보정, 완전 가림, 이동 불변, 회전 박스 표면 소속, 다른 물체가 앞에서 가리지 않는 조건, 기존 무한 높이와의 차이를 검사했다.
- 신규 6개 Python 소스 mypy 통과.
- CPU 7개 fixture에서 geometry 비교 약 0.61~1.40 ms. 이는 작은 박스 사례이며 전체 GUI Reset 시간이 아니다.
- RTX 3090 실제 GUI에서 7개 fixture 및 Simple 6개 배치를 각각 재관측했다. 모든 재관측 결과가 동일했고 표시 토글, 정면/사선 전환, marker·OBB에 충돌/강체 스키마가 없음을 확인했다.
- Simple 새 배치 6개에서 35개 표면점 생성, 평가 대응 누락 0. 새 배치/재관측 총 12회 geometry 계산 중앙값 8.74 ms, 최소 6.54 ms, 최대 19.41 ms. 자산 초기 로드·배치·렌더링 시간은 이 수치에서 제외했다.
- Simple의 대응 OBB 앞면과 새 점의 최대 깊이 차이는 약 8.76 mm. 같은 원본 박스에서 유도된 두 근사 관측 간 비교이며 실제 메쉬 정확도를 입증하지 않는다.
- 독립 CPU 비교 그림을 직접 확인했다. 가림 없는 두께 10 cm 박스에서 중심 차이 50 mm·앞면 차이 0, 중앙 구멍 사례에서 중심 보정 30.001 mm, 낮은 장애물 사례에서 새 2개/기존 3개 관측을 확인했다.
- GPU 테스트 과정에서 소문자 up-axis 문자열 오류를 발견해 USD 토큰으로 수정한 뒤 두 장면 검증을 재실행했다. 최종 검증 로그에는 성공 메시지가 있다.

## 최종 대조·미검증

추가 파일은 독립 패키지의 기하 계산·비교 표시·고정 사례·GUI/CPU 실행·테스트·README와 인계/개발 로그다. 기존 관측·Gaussian·baseline 코드는 유지했다. 기존 사용자 문서 변경·서브모듈 HEAD·학습 로그를 보존했다.

실제 메쉬, 원근·센서 잡음, 현실 segmentation, 물리 움직임, 학습 성능, 최종 환경 연결은 미검증/미구현이다. 비교용 원본 index는 관측 입력으로 노출하지 않는다. 변경 Markdown 3개 수식 검사 통과, 전체 608개 문서 링크 오류 0, 외부 workspace 링크 오류 0, root/docs diff 공백 검사 통과. 검증 자동 실행은 종료했고 사용자 확인용 Simple 뷰어는 별도로 실행해 두었다. 실제 화면에서 빨간 표면점과 OBB·수치 패널을 확인했으며 뷰어 창 캡처는 `outputs/surface_point/viewer.png`에 저장했다.
