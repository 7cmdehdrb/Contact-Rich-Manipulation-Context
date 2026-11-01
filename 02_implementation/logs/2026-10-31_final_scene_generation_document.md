# 2026-10-31 최종 환경 장면 생성 문서 작성

## 요청과 의도

사용자가 최신 Final 환경의 Scene Generation and Randomization에 대해 타겟·목표, 배치 영역, 겹침·선반·접근 공간, 개수·형상·크기·물성 무작위화, 배치 실패 처리, 생성 시점과 reset 시점의 차이를 설명하는 문서를 요청했다. 특히 현재 생성 알고리즘의 구체적 설명을 요구했다.

대상은 현재 인계와 실제 등록을 기준으로 `Isaac-Inspire-Final-GoalAccuracy-v0_2_2`로 고정했다. [장면 생성·무작위화 문서](../../04_article/environment_reference/FINAL_SCENE_GENERATION_AND_RANDOMIZATION.md)를 추가하고 [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)에 링크를 추가했다. 기존 BBOX 문서는 순수 모듈 API 계약이므로 수정하지 않았고, 새 문서는 실제 최종 환경의 lifecycle·선택 분포·물성·알고리즘을 연결하는 설명으로 구분했다.

## 변경 전후와 영향

| 변경 전 | 변경 후 | 영향 |
| --- | --- | --- |
| compact 환경 계약과 배치 API 문서에 설명 분산 | 현재 최종 환경 중심의 단일 설명 문서 | 물리 물체·논리 역할·관측 슬롯과 무작위화 시점을 함께 이해 가능 |
| 타겟·목표와 물성은 함수별로 확인 필요 | 단계별 알고리즘, 수식, 커리큘럼 표, 실패 분기 표 추가 | 단순 균등 거리 추출·물체별 독립 질량 등 오해 방지 |
| 활성 환경 안내에 장면 생성 설명 링크 없음 | 새 문서 링크 한 문단 추가 | 기존 사용자 변경 및 앞선 학습 네트워크 문서 링크 유지 |

코드·설정·자산·테스트 파일은 변경하지 않았다. `logs/rsl_rl`은 읽거나 정리하지 않았다. 기존 root와 문서 submodule의 미커밋 변경, submodule HEAD 및 이전 작업의 문서들을 보존했다.

## 코드 확인 범위와 주요 결론

root HEAD는 `b0116a7b3d384dd58e4a3f5909a5ecfa9b90d4e6`, 문서 HEAD는 `50f075a12b06a572980cbd8d4c7bb864279d2f5e`이며, 설명은 미커밋 v0_2_2 구현을 포함한 작업트리를 기준으로 한다.

최종 EnvCfg·SceneCfg·EventCfg와 runtime을 따라 실제 경로를 확인했다. `randomize_final_compact_scene`가 사용하는 `CompactRoleCollection`, `final_obb_geometry`, `bbox_scene_layout`, startup 물성 초기화와 reset 물성 함수, 직접 의존하는 형상 spawner·가시성 함수만 추가로 읽었다. 이전 환경의 역사 문서는 읽지 않았다.

- 12개 물리 물체와 10개 논리 역할, 20개 관측 슬롯은 별개다.
- 기타 14후보에서 환경 생성 시 10개를 중복 허용 추출하고 scale을 고정한다.
- reset 타겟 그룹은 1/3씩이며 기타는 보유 10개에서 선택한다. 단일 환경의 모든 후보 경험은 보장되지 않는다.
- 초기 타겟은 반경 2cm 원판 32후보 중 유효한 첫 후보, 목표는 방향 32후보와 ±선반 Y fallback이다. 목표 거리는 최대 15cm까지 가능한 ray 길이이며 최소 5cm다.
- 방향 제외 반각은 3500에서 첫 감소, 6000에서 0도다. Gray 폭은 5000에서 첫 증가, 10000에서 69mm다.
- RED는 fixed-yaw swept OBB를 board 전면으로 확장한 공간과 3mm 여유다. Gray 후방 직사각형은 별도 금지 영역이 아니다.
- 장애물 20mm 간격은 초기 타겟·장애물 쌍에 적용한다. 전체 타겟 이동 경로에 20mm를 적용하는 것으로 서술하지 않았다.
- 장애물 탐색은 32후보·4 restart·2 pass다. 이미 채택한 배치는 유지하고 실패 슬롯을 재시도하며, 총수 우선·Gray 수 보조 기준으로 한 restart를 선택한다.
- 부족한 장애물은 비활성으로 남긴다. 타겟·목표·간격을 완화하거나 다른 형상으로 교체하지 않는다. 타겟/목표 후보 자체가 불가능하면 오류다.
- 질량은 `1.5 × clip(N(0.365,0.0675²),0.230,0.500)` kg이며 환경별 공통 샘플이다. 형상별 관성은 기본값에서 질량 비율로 재계산한다.
- 마찰은 역할별 4096개 유한 bucket이며 물체용 샘플은 환경 내 물체들에 공통이다. reset에서 반발계수 등을 랜덤화하지 않는다.

### 주요 알고리즘 소스 SHA256

경로 기준: `src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/`.

| 파일 | SHA256 |
| --- | --- |
| `bbox_scene_layout.py` | `9B9D8C4FE83327844DD911B9A717F208AD17996C6BD1B31978DA4E828F9A1CE7` |
| `final_obb_geometry.py` | `ECE8B64015B08CD6EA8BAD4650C0260D9ECF20D986058836A544CD42E7EE53A7` |
| `final_compact_pool.py` | `58A81854C32098435521464C3F7CCE60F8D1B6A9550469B6BEC0ADCAEED0C641` |
| `realistic_physics.py` | `3B2847F4D685917937C50486F16D8BA6DEC89E5F6C321D49FD300FC20E65BC13` |

## 실행 검증

### 기존 관련 테스트

workspace root에서 실행했다. 기본 Windows pytest 임시 폴더의 이전 접근 문제를 피하기 위해 처음부터 고유한 workspace 임시 경로를 지정했다. 기존 폴더를 삭제하지 않았다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$sceneDocTemp = Join-Path (Get-Location).Path ('outputs/final_scene_doc_pytest_' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $sceneDocTemp) { throw 'Temporary path already exists' }
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_bbox_scene_layout.py src/inspire_sweep_baseline/tests/test_final_obb_layout.py src/inspire_sweep_baseline/tests/test_final_compact_pool.py src/inspire_sweep_baseline/tests/test_realistic_physics.py -q --basetemp $sceneDocTemp
```

결과: **43 passed in 5.20s**, exit 0. CPU/CUDA tensor geometry와 독립 polygon 검사, target/goal 불가능 오류, 실패 슬롯 후속 탐색, 기하 offset·yaw·높이 변환, 역할 분포·중복 방지·부분 mapping, 질량·마찰 분포와 물성 buffer 보존 검사를 포함한다. 물성 테스트는 mock PhysX view 또는 순수 sampler 검증이며 실제 시뮬레이션 물성 측정이 아니다.

### 현재 compact 10역할 adapter 검사

기존 adapter 테스트에는 부모의 21논리슬롯 입력도 포함되어 있어 현재 compact 규격을 별도로 확인했다. production 코드를 별도 module alias로 import하는 stdin Python probe로 다음을 수행했다.

- 64개 합성 장면, 10논리역할, seed 2122.
- XY 반폭 `0.01 + 0.035U`, 중심 offset `0.01(U−0.5)`, bounds의 Z 최저점 −0.007m.
- `max_gray_slots=4`, `max_white_slots=5`, 요청 4/5, `gray_red_padding_fraction=0.15`.
- 실제 `sample_shelf_layout` 호출 후 독립 테스트의 `assert_geometry`로 10슬롯 결과를 재구성하여 검사.
- 선반 경계, RED/Gray/White, 모든 활성 OBB 간 최소 20mm, 타겟 활성, 최저점 높이 1.05m, 비활성 주차 높이 100m 확인.

결과: exit 0, 64개 모두 통과. 이 합성 사례에서 실제 장애물 수의 최솟값과 최댓값은 모두 9였다. 이 결과를 실제 자산의 일반적인 완전 배치율로 해석하지 않는다. production 테스트 파일을 추가하지 않았다.

### 문서 검사

문서 저장소에서 다음 명령을 실행했다.

```powershell
python 00_guidelines/scripts/check_markdown_math.py 02_implementation/environments/FINAL_SCENE_GENERATION_AND_RANDOMIZATION.md 02_implementation/logs/2026-10-31_final_scene_generation_document.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md
python 00_guidelines/scripts/check_document_links.py
python 00_guidelines/scripts/check_document_links.py --check-external 02_implementation/environments/FINAL_SCENE_GENERATION_AND_RANDOMIZATION.md 02_implementation/logs/2026-10-31_final_scene_generation_document.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md
git diff --check
```

결과: 변경 Markdown 3개 수식 검사 통과, 전체 Markdown 420개 및 dataset 링크 검사 오류 0, 변경 문서의 workspace 소스 링크 36개를 포함한 검사 오류 0, diff 공백 검사 통과. Git의 기존 파일 LF→CRLF 안내는 있었지만 공백 오류는 없었다. 실제 Markdown/Mermaid 렌더링 검증과 구분한다. 최종 작업트리 상태도 확인해 production 변경 목록이 시작 시와 동일함을 확인했다.

## 최종 요청 대조와 미검증 범위

| 사용자 요청 | 문서 반영 |
| --- | --- |
| 대상 물체 초기 위치와 목표 | 좌표계·bounds 허용 범위·32후보·ray 길이·fallback·방향 일정 |
| 금지·근접·나머지 영역 | RED·Gray·White 구성과 whole-OBB 판정 |
| 겹침·선반·접근 공간 | SAT 20mm·경계 5/20mm·RED 3mm·3D/IK 보장 범위 구분 |
| 수·종류·크기·배치 무작위화 | 고정 roster·역할 선택·scale·수량 일정·후보 탐색 |
| 질량·마찰 | 정확한 분포·clip·배율·bucket·환경 내 공유와 관성 |
| 불가능 시 처리 | 타겟/목표 오류와 장애물 예산 부족 구분, 실제 수량 감소 |
| 한 번과 매 reset 구분 | lifecycle 표 및 전체 흐름도 |
| 현재 생성 알고리즘 필수 | 현행 adapter·tensor planner에 대응하는 순서·의사코드·탐색 예산 |

미검증: 이번 작업의 Isaac Sim 물리 실행·신규 GPU rollout·학습·성공률·실자산 전체 배치율, Markdown/Mermaid 실제 UI 렌더링. 기존 대체 선반 GPU 결과는 현재 환경 계약에 연결하며 이번 검증으로 재보고하지 않는다. 문서 작업이므로 production 코드 전후 물리 동등성 검사는 수행하지 않았다.
