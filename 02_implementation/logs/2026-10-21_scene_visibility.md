# Scene Randomization — 35% 전면 가시성과 실행 시간 시각화

[개발 로그](README.md) · [도구 실행·API](../../../../src/scene_randomization/README.md#전면-가시성-판정과-시각화)

기준일: 2026-10-21. 사용자 요청의 코드 추가와 실제 NumPy CPU·Torch CUDA 실행을 완료했다. Workspace HEAD `0e314e9`, 문서 HEAD `a953e0a`를 기준으로 작업했으며 기존 F/T 코드·문서·PLAN·untracked 자산과 로그 색인의 기존 충돌 표식을 보존했다. commit·push·학습 로그 정리는 하지 않았다.

## 구현과 판정 계약

`src/scene_randomization/generator.py`의 기존 `generate_parallel`을 그대로 호출한다. 타겟·장애물 배치, RED/GRAY/WHITE 규칙과 밀기 명령 분포는 변경하지 않았다. 생성 뒤에 가시성 판정을 연결했다.

- `visibility.py`: `classify_visibility`는 NumPy, `classify_visibility_torch`는 입력 Tensor와 같은 CPU/CUDA device에서 실행한다. Torch는 선택 기능으로만 import한다.
- `visualize_visibility.py`: 생성·검증·입력 준비·첫 판정·준비 실행·반복 판정·저장·그림을 분리한 전용 CLI.
- `visibility_plotting.py`: 씬 평면도, 실제 정면 투영과 물체별 가시 비율·시간 시각화.
- `test_visibility.py`: 해석적 가림 사례, 독립 구간 합집합 검증, NumPy/Torch 일치 검사.

시선은 열린 전면 y=0에서 +y로 향하는 평행 투영이다. 동일 높이의 비겹친 실린더가 가정이다. 각 물체가 단독일 때의 정면 투영 면적 대비 실제 보이는 면적 비율이 0.35 이상이면 인식으로 분류한다. 같은 높이이므로 보이는 폭 / 지름과 같다. 실제 카메라 영상의 의미 인식, 원근 또는 선반 상판 가림을 판정하는 모델은 아니다.

각 원의 좌우 경계를 정렬해 인접 구간의 중앙 광선이 처음 맞는 물체를 계산하고 구간 폭을 배정한다. 비겹침 조건에서 구간 내부의 앞뒤 순서가 바뀌지 않으므로 고정 격자 샘플링 오차가 없다. 기본 7물체는 최대 13구간 ×7개 물체다. 입력 기본 감사는 유한값·양의 반지름·비겹침을 확인한다. 검증된 반복 텐서는 `check_inputs=False`로 host 동기화 없이 계산할 수 있다. 비인식 물체도 가림 계산에는 포함하고 목표 위치·Zone은 제외한다.

## 실제 실행

NumPy 1.26.0, Matplotlib 3.10.3, Torch 2.7.0+cu128, float64, seed 20261013, workers 1, 10000씬·씬당 7개 물체, warmup 3회·측정 30회를 사용했다. CUDA는 샌드박스 밖의 NVIDIA GPU에서 실행했다. 설치나 드라이버 변경은 없었다.

```bash
env -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m scene_randomization.visualize_visibility --count 10000 --seed 20261013 --output outputs/scene_visibility/2026-10-21_numpy

env -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m scene_randomization.visualize_visibility --count 10000 --seed 20261013 --backend torch --device cuda:0 --no-plots --output outputs/scene_visibility/2026-10-21_torch_cuda

env -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m unittest scene_randomization.test_generator scene_randomization.test_visibility -v
```

## 시간과 결과

| 측정 | NumPy CPU | Torch CUDA |
| --- | ---: | ---: |
| 10000씬 생성 | 1.935100초 | 1.901303초 |
| 생성 상각 평균 | 0.193510 ms/씬 | 0.190130 ms/씬 |
| 최초 10000씬 판정, 입력 감사 포함 | 36.120 ms | 216.768 ms |
| 준비 후 10000씬 판정 중앙값 | 16.278 ms | 0.258 ms |
| 배치 판정 p95 | 17.235 ms | 0.273 ms |
| 판정 상각 평균 | 1.627756 μs/씬 | 0.025772 μs/씬 |
| 단일 씬 판정 중앙값 | 37.146 μs | 268.323 μs |

CUDA GPU에서 generator가 실행된다는 뜻은 아니며 씬 생성은 두 경우 모두 기존 NumPy CPU 경로다. 단일 씬은 GPU launch/synchronization 비용 때문에 CPU보다 느렸다. 반복 판정 시간에서 입력 준비·전송·감사·저장·그림을 제외했고 CUDA 완료를 동기화했다. 첫 판정에는 입력 감사와 최초 kernel 호출 비용이 포함되어 반복 판정보다 느렸다. 상각 평균을 독립적인 단일 씬 지연으로 해석하지 않는다. 현재 호스트의 측정이며 다른 장비의 성능을 보장하지 않는다.

두 실행 모두 70000개 물체 중 인식 61839개·비인식 8161개였다. 현재 RED의 전면 비움 규칙 때문에 타겟이 잘 보이는 배치가 많으며, 가시성 결과로 씬을 버리거나 다시 생성하지 않았다. 갤러리는 비인식 물체 수 순서에서 고르게 고른 사례로 전체 무작위 표본을 대체하지 않는다.

산출물:

- [갤러리](../../../../outputs/scene_visibility/2026-10-21_numpy/visibility_gallery.png): 녹색 인식·주황 비인식, 물체 ID·가시 비율·생성/판정 시간.
- [상세 씬](../../../../outputs/scene_visibility/2026-10-21_numpy/visibility_scene.png): Scene 19의 평면도·정면 투영·물체별 비율과 35% 기준선.
- [전체 물체 CSV](../../../../outputs/scene_visibility/2026-10-21_numpy/visibility.csv).
- [NumPy 시간·설정](../../../../outputs/scene_visibility/2026-10-21_numpy/report.json), [CUDA 시간·장비](../../../../outputs/scene_visibility/2026-10-21_torch_cuda/report.json).
- [전체 교차 검증](../../../../outputs/scene_visibility/validation.json), [CPU 테스트 stdout](../../../../outputs/scene_visibility/tests.log).

## 검증과 미검증 범위

기존 21개 + 신규 8개, 총 **29개 테스트 통과**. 정확히 35%인 경우, 전면 방향·완전 가림·복수 가림의 합집합·비인식 물체의 가림 유지·padding NaN·빈 active mask·겹친 입력 거절·크기/평행이동·물체 순서 불변·NumPy/Torch CPU 일치를 확인했다. 생성된 128씬은 원 교차 공식을 쓰지 않는 별도 전면 구간 합집합 oracle과 대조했다.

실제 10000씬 CPU/CUDA 실행에서 생성된 좌표·목표·명령이 같고, 70000개 비율 최대 차이 0, 인식 마스크와 최초 교차 물체 ID가 모두 같았다. 두 기하 검증은 통과했으며 비율의 유한값·[0,1] 범위·35% 분류도 검사했다. 저장된 갤러리와 상세 PNG를 직접 열어 전면 방향, 비율·색상·표시 시간과 가림 투영을 확인했다.

실제 카메라 원근, 다른 높이, 물체 겹침·전도, 물체/센서 식별 성능, 활성 RL 환경 연결은 이번 검증 범위가 아니다. 물리적 환경이나 보상 계약도 변경하지 않았다.

문서 검증도 실행했다. 문서 저장소에서 `python 00_guidelines/scripts/check_markdown_math.py 02_implementation/logs/2026-10-21_scene_visibility.md 02_implementation/logs/README.md ../../src/scene_randomization/README.md`는 3파일 통과, `python 00_guidelines/scripts/check_document_links.py --check-external 02_implementation/logs/2026-10-21_scene_visibility.md ../../src/scene_randomization/README.md`는 내부 링크 2개·workspace 파일 링크 10개·오류 0이었다. 두 저장소의 변경 대상 `git diff --check`와 신규 Python 파일의 AST 구문 검사도 통과했다.
