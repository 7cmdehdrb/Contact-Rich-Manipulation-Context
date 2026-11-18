# OBB 중심 Gaussian 조회 모델과 Reset 가속

## 요청·원인·범위

사용자는 관측별 6.4~29.9초, 5개 합계 약 74.5초가 걸린다고 보고했고 사전 데이터 생성과 방법 변경을 허용하며 매우 빠른 Reset을 요청했다. 별도 `src/centroid_belief` 검토 패키지를 수정했다. 최종 Holding/Final 환경·학습·제어에 연결하지 않았다. 커밋하지 않는다.

기존 128표본 추정기의 CPU 프로파일에서 16.515초 중 differential evolution 누적 15.430초, 최적화 40회, 전체 후보 평가 17,672회였다. 표본 수만 줄여도 최적화 비용은 남는다. 이 프로파일 시간은 계측 오버헤드가 있어 일반 실행 속도와 직접 비교하지 않는다.

## 변경 전후

- 기존: 매 Reset/관측마다 최적화·중요도 표집 후 Gaussian 모멘트 계산. 새 기본 뷰어: 사전 기하 표 조회 후 최대 16개 후보만 정확한 관측 연산으로 재검사한다.
- 8종 OBB 근사 형상, yaw 72개, 횡방향 20분할 절단을 열거한 81,621개 기록을 포함했다. 생성은 CPU 13.175초, 약 776 KiB. 시뮬레이션·학습 없이 생성하며 실행마다 생성하지 않는다.
- 표에는 높이로 정규화한 관측 OBB 특징과 원본 중심 오프셋이 들어간다. yaw 축 교환에 불변인 특징을 사용한다. 런타임에는 관측 목록과 대상 ID만 전달한다. 정답 중심·원본 종류·source ID를 사용하지 않는다.
- 주변 관측의 횡방향 접촉/중첩으로 가림 방향을 판정한다. 높이 범위가 맞는 형상과 절단 방향의 KD-tree에서 가까운 후보를 찾고, 최대 16개의 재관측 오차로 가중치를 정한다.
- 완전 관측 중심의 비중은 최소 50%이며 부분 후보 적합도가 나쁘면 증가한다. 혼합 모멘트를 평균 2개·공분산 3개로 줄인다. 3 mm 바닥 오차 및 높이의 2.5% 격자 오차를 공분산에 더한다.
- 이 비중·공분산은 미보정 근사 설정이다. 기존 importance posterior와 수치적으로 동일한 결과나 빈도론적 90% coverage를 보장하지 않는다. 기존 `estimate()`·`estimate_particles()`와 `--estimator reference`는 비교용으로 보존했다. 빠른 공개 API는 `LookupEstimator.estimate()`와 `estimate_fast()`다.
- 적합 후보가 부족하면 `lookup_low_support` 및 넓은 대체 공분산, 높이가 범위를 벗어나면 `no_template_height_support`를 반환한다. 조회 모델에는 ESS가 없으므로 낮은 ESS 경고는 발생하지 않는다. `estimate_fast()`는 belief만 반환하므로 진단이 필요하면 `LookupEstimator.estimate()`를 사용한다.
- 확대 그림은 Matplotlib/PNG/디스크 I/O 대신 메모리 RGBA로 갱신한다. 3D 재질·Gaussian 및 관측 OBB prim을 재사용한다. 불필요한 관측 OBB prim은 제거하고 Gaussian prim은 숨긴다. 충돌·강체 스키마는 추가하지 않았다.
- 빠른 계산 때문에 작업 thread가 끝났어도 표시 큐가 남을 수 있는 경쟁 조건을 발견했다. `SnapshotRunner.busy`에 미소비 결과 큐도 포함하여 모든 관측 표시 후 완료 처리한다. 최신 요청 우선·취소·이전 스냅샷 폐기는 유지한다.

## 실행 결과

RTX 3090 GUI에서 seed 0으로 10회 실제 배치, 관측, 추정, 3D/확대 이미지 업데이트 및 마지막 `app.update()`를 수행했다. 10회 합계 59개 관측이 모두 로그에 표시됐는지 확인했다.

| 측정 | 결과 |
| --- | --- |
| 첫 Reset, 최초 렌더 준비 포함 | 1,434.5 ms |
| 이후 9회 Reset 중앙값 | 238.0 ms |
| 이후 9회 최소~최대 | 146.4~337.5 ms |
| CPU 표 로드·인덱스 구성 | 33.5 ms, 프로세스당 1회 |
| CPU 기본 36사례 관측별 중앙값/P95 | 10.22/14.40 ms |
| CPU 추가 125사례 관측별 중앙값/P95 | 10.24/13.38 ms |

Reset 측정에는 Isaac Sim 앱 자체의 약 20초 시작 비용과 장면 최초 생성은 포함하지 않는다. GPU 측정 중에는 일부 관측이 수십 ms 걸렸으므로 CPU 독립 측정의 10 ms를 GPU 전체 Reset 시간으로 표현하지 않는다. 원래 사용자 로그와 배치별 관측 수가 모두 같지는 않으며, 전체 속도 배수를 정밀 비교로 해석하지 않는다.

평가에서는 고정 기본 36사례와 표의 yaw/scale 격자와 일치하지 않는 연속 난수 128사례를 생성했다. 후자 중 대상이 2 cm/20% 필터로 제거된 3사례는 추정 대상이 없어 제외하고 125사례를 평가했다. 각 입력을 3회 실행한 중앙값으로 관측별 시간을 집계했다.

| 평가 | 관측 중심 오차 | Gaussian 평균 오차 | 실제 중심의 90% 타원 포함 |
| --- | --- | --- | --- |
| 기본 36개 | 1.078 cm | 0.546 cm | 35/36 |
| 추가 125개 | 0.719 cm | 0.387 cm | 125/125 |

모든 평가에서 관측 중심은 90% 타원 안에 있다. 실패 1개는 가리는 물체가 관측 필터로 누락된 split 사례다. 관측 가림 경계가 없으면 완전 관측으로 근사하므로 이 한계가 유지된다. 이 표는 기존 느린 추정기와의 오차 비교가 아니라 관측 중심 그대로 사용한 경우와의 비교다. 실제 자산 중심의 정확도·실측 noise·확률 보정·모든 배치에 대한 지연 상한은 미검증이다. 실제 GPU 장면에서 일부 `lookup_low_support`가 표시되며 숨기지 않는다.

## 재현·파일·최종 대조

Workspace 루트에서 Isaac Lab Python으로 실행한다.

```bash
OPENBLAS_NUM_THREADS=1 python src/centroid_belief/scripts/show.py --seed 0
OPENBLAS_NUM_THREADS=1 python src/centroid_belief/scripts/show.py --benchmark-resets 10
OPENBLAS_NUM_THREADS=1 python src/centroid_belief/scripts/evaluate_fast.py
python src/centroid_belief/scripts/build_lookup.py
```

빠른 모드에서는 `--samples`를 사용하지 않는다. 기존 모드는 `--estimator reference --samples 128`로 재현한다. 뷰어 사용·API 계약은 [패키지 README](../../../../src/centroid_belief/README.md)에 설명했다. CPU 원시 결과는 `outputs/centroid_fast/metrics.csv`, `summary.json`, `fast_preview.png`; GPU 원시 결과는 같은 폴더의 `viewer_benchmark.log`, `viewer_summary.json`이다. 이전 실험 출력은 보존했다.

추가/수정 범위는 centroid 패키지의 조회 표·생성/평가 스크립트·뷰어·메모리 미리보기·표시·worker 완료 판정·의존성/패키지 데이터·테스트와 observed_obb 표시 prim 재사용 및 계측이다. 관측의 절단·2 cm/20% 기준·배치 표집·baseline 코드는 보존했다. root/docs 저장소 커밋과 사용자 변경·학습 로그는 유지했다. GPU 벤치마크는 자동 종료했다.

검증: USD 표시 테스트 포함 전체 56개 통과(33.08초). 조회의 후보 수 제한·완전 관측 가능성·좌표 이동 불변·동일 OBB 축 표현·지원하지 않는 높이·실제 worker 입력·결과 큐 완료 경쟁 조건·재사용 도형 및 비충돌을 검사했다. 16개 소스 mypy 통과. CPU 미리보기 PNG의 색·경계·축·범례를 직접 확인했다. 문서 수식 2개 파일, 전체 링크 605개 문서(오류 0), 새 로그의 외부 workspace 링크 및 root/docs diff 공백 검사 통과.

추가 배포 검증: 오프라인 wheel 빌드 성공, wheel 내부 `completion_bank.npz`가 원본 793,551 bytes와 바이트 단위로 일치함을 확인했다. 확대 이미지 종횡비 보존은 `ImageWithProvider` 전용 `IwpFillPolicy`를 사용하며 최종 GPU 1회 실행에서 관측 6개 모두 표시 후 정상 종료했다(`viewer_final_smoke.log`).
