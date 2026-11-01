# 2026-11-01 기준 크기 물체의 선반 전시 패키지

## 요청과 변경 의도

사용자가 코드에서 직접 생성하는 물체를 보여주기 위해 `src` 아래 새 패키지와 Isaac Lab 장면을 요청했다. 동일 선반 위에 기준 크기 물체를 n×m 격자로 배치하며 로봇·학습은 필요하지 않다는 조건이다.

[shelf_object_gallery 패키지](../../../../src/shelf_object_gallery/README.md)를 추가했다. 기존 Final 환경의 클래스나 Gym task를 파생하지 않고 `SimulationContext`와 `InteractiveScene`으로 전시 장면을 구성한다. 기존 source spawner를 재사용하며 절차적 mesh를 복제 구현하지 않는다.

## 변경 전후와 영향

| 항목 | 변경 후 |
| --- | --- |
| 새 패키지 | `src/shelf_object_gallery`, setuptools pyproject와 checkout 직접 실행 지원 |
| 형상 | 원통·직육면체·머그컵·병을 원본 spawner로 생성, scale 1.0 |
| 선반 | Final의 동일 `SHELF_USD_PATH`·pose·작업면 상수 사용, 명시적 `--shelf-usd` 허용 |
| 배치 | 기본 1×4, 행·열·간격 옵션, 비대칭 bounds 중심 보정, 20 mm 경계 여유 |
| 고정 전시 | 물체·선반 kinematic, 물체 종류별 표시 색상 |
| 실행 | AppLauncher와 카메라, 유한 step 검증·USD export·PNG screenshot 옵션 |
| 검증 | 순수 배치 테스트 및 live stage의 실제 치수·높이·고정 pose·로봇 부재 검사 |

격자 크기가 선반보다 크면 물체를 축소하지 않고 오류로 안내한다. 원본 물체의 기준 치수와 collider는 보존한다. `cube`는 GoalAccuracy의 60×80×100 mm 값을 명시한다. 기타 세 물체의 기본 치수는 기존 spawner에서 사용하며 bounds는 실제 mesh vertices에서 구한다.

production 기반 패키지의 기존 미커밋 코드와 독립 submodule HEAD는 변경하지 않았다. 새 패키지와 개발 로그·환경 안내만 추가했다. RL manager·로봇·checkpoint·PPO·학습 로그 생성은 없다.

## 실행

workspace root, Isaac Lab 환경의 Python에서 실행한다.

```powershell
python src/shelf_object_gallery/scripts/show.py
python src/shelf_object_gallery/scripts/show.py --rows 2 --cols 4
python src/shelf_object_gallery/scripts/show.py --headless --steps 20 --validate --screenshot outputs/gallery.png
```

창에서 원본 선반과 기본 물체 4개를 확인할 수 있다. 범주 순서는 전면에서 왼쪽부터 원통·직육면체·머그컵·병이며 큰 격자는 이 순서로 반복한다. 행은 선반 깊이 방향이다.

## 검증과 수정 과정

### 순수 배치 테스트

기본 Python에는 pytest가 없어 최초 명령은 실행되지 않았다. 실제 Isaac Lab conda 환경으로 전환해 아래 테스트를 실행했다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/shelf_object_gallery/tests/test_layout.py -q -p no:cacheprovider
```

1×4·2×4·3×6(간격 10 mm)의 전체 bounds 경계·물체 간 간격·셀 중심·높이, 과밀 배치 오류와 잘못된 인자를 검사한다. 최종 결과는 **8 passed in 0.02s**, exit 0이다.

### 실제 Isaac Sim 실행

Isaac Sim 5.1.0.0, CUDA 사용 가능 RTX 4070, Windows D3D12 환경이다. 초기 원본 접속 여부를 확신하지 못해 기존 로컬 검사용 선반으로 먼저 2×4를 검사했다. 이는 원본 선반 검증과 구별한다.

최초 custom procedural spawner에 regex 경로를 전달하면 USD 경로 오류가 발생했다. 이 장면은 단일 환경이므로 객체별 구체적인 `/World/envs/env_0/object_...` 경로를 전달하도록 수정했다. 원본 spawner는 변경하지 않았다.

이후 원본 `omniverse://192.168.0.13/Library/Shelf/Arena/Collected_speedrack_shape/speedrack_shape.usd`에 접근되어 원본 선반에서 1×4와 2×4를 각각 20 step 진행하고 live geometry 검사를 통과했다. 위치·높이·scale 및 로봇 부재를 검사했다. 원본 선반의 기본 1×4 PNG도 실제 렌더링해 육안 확인했다. 초기 카메라 화면에서 좌우 순서가 설명과 반대임을 확인해 열 방향을 선반 −Y→+Y로 수정했다.

초기 배치 검사 성공 후 Isaac Sim 종료가 지연됐다. 임시 faulthandler trace로 `sim.stop()`이 Isaac Lab `_app_control_on_stop_handle_fn`의 render loop를 호출하는 것을 확인했다. `sim.clear_instance()`로 STOP 구독을 해제한 뒤 timeline을 정지하도록 순서를 수정했다. 임시 traceback timer와 `skip_cleanup` 우회 시도는 최종 코드에서 제거했고, 기본 cleanup과 `wait_for_replicator=False`로 정상 종료했다. 지연 중이던 자체 테스트 프로세스만 command line을 확인하고 종료했으며 최종 검증 프로세스는 자연 종료했다.

산출물은 workspace `outputs`의 `shelf_object_gallery*.log`, `shelf_object_gallery.png`, `shelf_gallery_fixture.usda`다. 임시 fixture를 원본 선반이라고 보고하지 않는다.

## 완료 기록과 미검증 범위

최종 검증 명령은 다음과 같다. 원본 선반을 사용했으며 두 실행 모두 검사 메시지를 출력하고 **exit 0으로 자연 종료**했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe src/shelf_object_gallery/scripts/show.py --headless --steps 20 --validate --screenshot outputs/shelf_object_gallery.png
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe src/shelf_object_gallery/scripts/show.py --headless --rows 2 --cols 4 --steps 20 --validate
```

최종 로그는 `outputs/shelf_object_gallery_verified.log`와 `outputs/shelf_object_gallery_2x4_verified.log`다. 1280×720 PNG의 실물체 표시·기준 선반·순서·로봇 부재를 직접 확인했다. 실행 종료 뒤 해당 gallery Python 프로세스가 남아 있지 않음도 확인했다.

문서 검사: 새 로그·활성 환경 안내·패키지 README 총 3개 수식 검사 통과, 전체 Markdown 428개 및 dataset 링크 검사 오류 0, 변경 docs의 workspace 링크 2개를 포함한 검사 오류 0, root와 문서 저장소의 `git diff --check` 통과. 처음 README 검사 경로를 잘못 지정한 명령은 실패했으며 절대 경로로 수정 후 통과했다. Git의 LF→CRLF 안내는 기존 작업트리 파일에 관한 것이고 공백 오류는 없었다. 최종 root 상태는 기존 변경 목록에 `src/shelf_object_gallery/`만 추가된 상태다.

GUI 장시간 조작·다른 OS와 GPU·패키지 wheel 설치는 미검증이다. 이번 장면의 고정 물체를 동적 조작 환경의 접촉·정책 성능 검증으로 해석하지 않는다. 기존 Final 환경의 설정·관측·보상·커리큘럼·학습 로그는 유지한다.

## 후속 수정: 외부 YCB 자산 4종 추가

사용자가 `--rows 2 --cols 4` 실행에는 외부 자산까지 포함해야 한다고 정정했다. 최초 구현이 절차적 물체만 반복했던 누락을 수정했다. 기존 4종 뒤에 `003_cracker_box`, `004_sugar_box`, `005_tomato_soup_can`, `002_master_chef_can`을 추가하고 기본 행 수를 1→2로 바꿨다. 기본 실행과 지정된 2×4 실행에서 전면 절차적 4종·후면 YCB 4종을 하나씩 표시한다. 더 큰 격자는 전체 8종을 반복한다.

YCB는 기존 Final의 `ShelfPropCfg`를 직접 재사용해 `size_fraction=1.0`, 원본 텍스처·시각 mesh와 box/can collider로 생성한다. 별도 ±10% scale은 적용하지 않는다. 배치 bounds를 고정 치수로 복사하지 않고, 시뮬레이션 시작 전에 원본 spawner를 임시 경로에서 생성해 실제 bounds를 측정한다. 임시 prim은 제거하고 전시 객체만 PhysX 초기화에 남긴다. 실자산 검증은 시각 mesh와 proxy collider 존재, 자산 ID, 치수·높이·고정 위치까지 확인하도록 확장했다.

패키지 README·metadata·활성 환경 안내를 갱신했다. 실제 Final spawner와 환경은 변경하지 않았다. 순수 배치 테스트에 8종 전체 구성과 반복 순서를 추가했고, 현행 자산 크기를 반영한 경계·간격 검사도 유지했다.

검증: 배치 테스트 **9 passed in 0.03s**, exit 0. 원본 선반·원본 YCB를 사용하는 아래 실행의 최종 결과는 이어서 기록한다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe src/shelf_object_gallery/scripts/show.py --rows 2 --cols 4 --headless --steps 20 --validate --screenshot outputs/shelf_object_gallery_all8.png
```

결과: 원본 선반에서 8종을 한 번씩 생성해 20 step 후 live 검증 통과, **exit 0 정상 종료**. 로그 `outputs/shelf_object_gallery_all8.log`의 row 0은 절차적 4종, row 1은 YCB 4종이다. `outputs/shelf_object_gallery_all8.png`를 직접 열어 8종 배치와 YCB 텍스처를 확인했다. 각 YCB의 실제 bounds·원본 시각 mesh·별도 collider·asset ID가 검증됐다. 변경 Markdown 3개 수식 검사와 관련 workspace 링크 검사 오류 0, docs diff 공백 검사도 통과했다. 기존 GUI 장시간 조작·다른 OS/GPU의 미검증 범위는 유지한다.
