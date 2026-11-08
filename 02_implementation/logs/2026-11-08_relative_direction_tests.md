# Relative 방향별 Test 환경과 녹화

## 요청과 기준

`logs/TEMP/1108`의 Relative-v2_1 및 Relative-v3 체크포인트를 네 방향으로 평가하기 위한 8개 파생 환경이다. 코드 기준 commit은 `2964e09b08d7e7b121e862178f596f24fa69fb70`이다. 작업 시작 시 루트는 IsaacLab의 기존 변경 표시만 있었으며, 문서 저장소의 기존 미추적 `2026-11-08_penalty_data_plots.md`는 보존했다. 체크포인트와 학습 로그는 수정하지 않았다.

## 환경 계약과 최종 대조

전체 ID는 `Inspire-Wrench-Refactor-Relative-{version}-Test-{direction}`이며 version은 `v2_1`, `v3`, direction은 아래 네 가지다. 각각 `WrenchRefactorRelativeV2_1EnvCfg` 또는 `WrenchRefactorRelativeV3EnvCfg`를 직접 상속한다. 설정 클래스는 `WrenchRefactorRelativeV2_1TestRightEnvCfg`와 같은 이름이다.

로봇이 있는 선반 +X 쪽을 6시로 정의한다. 초기 타겟 위치에서 목표 위치로 향하는 벡터를 선반 좌표계로 구분한다. 녹화 카메라 화면의 회전 방향과는 별개다.

| direction | 시계 구간 | 중심 방향 | atan2(Y, X) 각도 |
| --- | --- | --- | --- |
| Right | 2~4시 | +Y | 60~120도 |
| Pull | 4~8시 | +X | -60~60도 |
| Left | 8~10시 | -Y | 240~300도 |
| Push | 10~2시 | -X | 120~240도 |

고정된 한 점이 아니라 해당 각도 구간에서 매 reset 균등 추출한다. 목표 거리 6~12cm, 선반 안전 경계에 따른 조건부 거리 균등 추출, 초기 타겟 반경 2cm를 보존한다. Right/Left는 각각 60도, Pull/Push는 각각 120도 폭이다.

| 항목 | 부모 대비 최종 차이 |
| --- | --- |
| Event/reset | `object_spawn.params.goal_angle_range` 하나 추가 |
| 방향 커리큘럼 | 설정·일정은 상속하되 명시적 각도 구간이 샘플러에서 우선한다. 따라서 checkpoint iteration과 무관하게 Test 구간 고정 |
| Scene/자산/물성/장애물 | 동일. 기존 OBB 배치는 새 목표 방향을 입력받음 |
| Command/Observation/Action | 동일. 관측 차원·순서·noise·OSC 보존 |
| Reward/Termination | 모든 callable·params·weight·판정 보존. v3는 기존대로 성공 종료 없음 |
| 나머지 Curriculum/runtime/로그 키 | 동일. 속도 종료 일정도 보존 |
| PPO | 부모 runner entry point 그대로 재사용. 체크포인트 네트워크 구조 동일 |

공통 `reset_scene`에서 선택 인자를 전달하고 `sample_commands`에서 명시 구간을 적용한다. 기본값 `None`인 기존 환경은 기존 난수 추출 횟수·방향 계산·거리 계산을 유지한다. 부모 EnvCfg 본문은 수정하지 않았으며 실제 설정 사전 전체 비교로 자식의 허용 차이와 부모 인스턴스 불변성을 검사했다. 기존 recorder는 변경하지 않았다.

## 녹화 실행

Workspace 루트에서 Isaac Lab Python으로 아래 PowerShell을 실행한다. 체크포인트는 각 버전의 최근 run에서 가장 큰 iteration을 예시로 선택했다. 성능 우수성을 의미하지 않으며 다른 체크포인트로 교체 가능하다. 각 작업은 기존 recorder를 호출하며 60초 동안 세 시점을 동시에 저장한다.

```powershell
$checkpoints = @{
    v2_1 = 'logs/TEMP/1108/inspire_wrench_refactor_relative_v2_1/2026-11-07_22-43-45/model_9700.pt'
    v3 = 'logs/TEMP/1108/inspire_wrench_refactor_relative_v3/2026-11-07_18-43-11/model_8700.pt'
}
$recordRoot = 'outputs/relative_direction_tests/' + (Get-Date -Format 'yyyyMMdd_HHmmss')
foreach ($version in @('v2_1', 'v3')) {
    foreach ($direction in @('Right', 'Pull', 'Left', 'Push')) {
        python src/inspire_sweep_baseline/scripts/record_three_views.py `
            --task "Inspire-Wrench-Refactor-Relative-$version-Test-$direction" `
            --checkpoint $checkpoints[$version] --seconds 60 --seed 42 --headless `
            --output-dir "$recordRoot/$version-$direction"
        if ($LASTEXITCODE -ne 0) { throw "Recording failed: $version $direction" }
    }
}
```

각 폴더에 `high_angle.mp4`, `rear_eye_level.mp4`, `inside_top_down.mp4`, `frames.csv`, `metadata.json`을 저장한다. 성공하면 총 24개 영상이다. 먼저 한 환경의 렌더링을 확인하려면 같은 명령에 `--preview-only`를 추가한다. 출력 폴더는 기존 폴더를 덮어쓰지 않으므로 매번 새 경로를 사용한다.

## 검증과 한계

CPU 검사 결과 **87 passed (9.91s)**. 다음 CPU 검사에서 기존 회귀, 전체 부모/자식 설정 대조, 8개 등록, 각 구간 20,000표본의 방향 균등성·6~12cm 거리·선반 안전 경계를 검사한다. 제외각 0도/30도 양쪽에서 동일 Test 구간을 확인한다.

```powershell
C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench_refactor_relative.py -q --disable-warnings
```

GPU reset/step, 실제 checkpoint load, 카메라 렌더링과 MP4 생성은 이번 작업에서 실행하지 않았다. 따라서 영상 취득 성공과 방향별 성공률은 미검증이다. 기존 recorder는 영상용이며 성공률 집계 기능을 새로 추가하지 않았다. 동일 seed라도 방향에 따른 OBB 배치 재시도 및 에피소드 종료 차이로 전체 장면이 일대일 대응한다고 보장하지 않는다.
