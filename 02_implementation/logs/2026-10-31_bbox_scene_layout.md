# 2026-10-31 OBB 텐서 배치 모듈 구현

[규칙·API·성능 계약](../environments/BBOX_SCENE_LAYOUT.md)

## 요청과 범위

사용자는 `src/scene_randomization`을 참고해 원형 가정을 제거한 Bounding Box 배치, RED/Gray/White, 손가락 최소 간격, Gray padding, 존별 상한, 과밀 시 가능한 수량 반환, reset용 텐서 연산을 요청했다. 후속 답변으로 **모듈과 테스트만 구현**하며 **제한된 반복 탐색의 최다 배치**를 사용하도록 확정했다. 기존 환경 적용이나 학습은 요청 범위에 포함하지 않았다.

코드 기준 HEAD는 `872526029de5852bf219041da682fc72dab1659c`, 문서 HEAD는 `62dadeef00a12740204ba1928343f3c0f7f896cb`다. 시작 시 root의 `IsaacLab` 미추적 변경만 있었으며 보존했다. 문서 작업트리는 깨끗했다. 커밋·학습 로그 정리는 수행하지 않았다.

## 변경과 의도

기존 `final_geometry.py`는 원형 존 생성 후 NumPy OBB 검사를 수행하고 환경별로 반복한다. 새 `mdp/common/bbox_scene_layout.py`는 객체별 OBB와 타겟의 swept OBB를 직접 검사한다. `src/scene_randomization`의 전면 -y 손목 투영, Gray 후방 직사각형 의미는 유지하고 원형 반경·접근 궤적·밀도 제약은 새로운 계약에서 사용하지 않는다. 기존 함수를 덮어쓰지 않았다.

배치 개수 부족 시 기존의 교대 수량 감소 대신 서로 다른 순서의 병렬 restart와 실패 슬롯 재시도를 수행하고 총수 최대 결과를 고른다. RED와 간격을 완화하지 않는다. 불가능성을 증명하거나 연속 공간 최적 개수를 보장하지 않는다는 점을 명시했다. 물체 중심과 asset root가 다른 경우를 위해 bounds offset 변환도 제공했다.

추가 파일은 공통 기하 모듈, `tests/test_bbox_scene_layout.py`, `scripts/benchmark_bbox_layout.py`다. 기존 EnvCfg·runtime·Event·Reward·Termination·Curriculum·PPO·등록·관측에는 차이가 없다. 별도 GPU 학습이나 Isaac Sim 실행 없이 순수 torch CPU/CUDA 규칙을 검증했다.

## 검증과 최적화

초기 CPU/CUDA 20개 테스트 통과 후, 무작위 256장면과 CPU/CUDA 분류 일치 검사를 추가했다. 최종 **22 passed in 3.26s**. 생성기의 반폭 투영 수식을 재사용하지 않는 NumPy polygon hull·vertex projection 및 point-segment 거리로 결과를 독립 검증했다. 거대한 배치 불가능 물체 뒤의 작은 물체도 계속 배치하며, 해당 사례에서 알려진 최대 2개를 모두 배치했다. RED가 전체 작업판을 덮는 사례에서는 0개를 반환했다.

최초 구현의 2048장면 GPU 중앙값은 610.00ms, peak allocated 319.80MiB였다. OBB pairwise SAT의 4축 행렬을 네 개 scalar projection으로 변경하고, RED와 Gray의 동일 swept-volume projection을 한 번만 계산하도록 최적화했다. 같은 예산의 최종 결과는 96.72ms, 103.86MiB다. 후속 테스트를 모두 다시 실행했다. 512장면은 151.28→63.37ms였다. 동일 synthetic 입력·장치에서의 측정이며 독립적인 여러 날짜의 성능 통계는 아니다.

CPU/CUDA 비교, 낮은 탐색 예산, 높은 탐색 예산, 20개 과밀 요청을 benchmark 스크립트로 실행했다. 원본 JSON에 모든 케이스의 min/median/max, 설정, 생성 개수, 완성률, GPU 메모리를 저장했다. 소규모 GPU batch의 변동과 launch overhead도 기록했다. 그림 6개 장면의 박스·타겟 경로·존·수량·축 표기를 직접 확인했다.

실행은 Windows 11 / conda `env_isaaclab`에서 수행했다. Python platform 문자열은 Windows-10-10.0.26300-SP0로 보고되며 사용자 지정 Windows 11과 구분해 원본 JSON에 보존했다. Shapely는 설치되어 있지 않아 새 의존성을 설치하지 않고 독립 NumPy 다각형 검증기를 작성했다.

```powershell
conda run --no-capture-output -n env_isaaclab python -m pytest src/inspire_sweep_baseline/tests/test_bbox_scene_layout.py -q --basetemp outputs/pytest_bbox_layout_optimized
conda run --no-capture-output -n env_isaaclab python src/inspire_sweep_baseline/scripts/benchmark_bbox_layout.py --output outputs/bbox_scene_layout_optimized
```

증거: `outputs/bbox_layout_tests.log`, `outputs/bbox_layout_benchmark.log`, `outputs/bbox_layout_benchmark_optimized.log`, `outputs/bbox_scene_layout_optimized/benchmark.json`, `gallery.png`, `gallery.npz`. 출력물은 로컬 검증 산출물이다.

## 최종 대조와 미검증

요청한 OBB, 존, 최소 간격, padding, 존별 상한, 예산 내 최다 배치, 텐서 연산을 모듈 계약으로 제공했다. 사용자 선택대로 기존 환경 연결은 수행하지 않았다. 보상·학습 구성·원형 생성기 소스·사용자 작업트리·학습 로그 변경은 없다. handoff·환경 색인·패키지 README에는 이 모듈이 아직 환경에 연결되지 않았음을 명시했다.

미검증: 실제 USD 형상별 bounds 정확도와 원점 변환 연결, 실제 reset의 물리 배치와 센서 접촉, 손가락 전체 접근 가능성·손목 운동학, 기울어진 물체의 3D 간섭, 학습 성공률과 collection 시간. 최다 수량은 휴리스틱 결과이며 엄밀한 packing optimum이 아니다. 동시 실행 부하와 장치가 바뀌면 시간도 달라진다.

문서 검사: 변경 문서 저장소 Markdown 4개의 수식·링크 검사 통과(42개 내부 링크, 오류 0), README 수식 검사 및 양쪽 저장소 `git diff --check` 통과. README 전체 링크 검사에서는 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 대상 부재 1건을 확인했다. 새 OBB 문서 링크는 유효하다. 이 기존 누락 파일은 이번 작업에서 생성하거나 변경하지 않았다. Markdown 렌더링은 미확인, 생성된 배치 PNG는 직접 시각 확인했다.
