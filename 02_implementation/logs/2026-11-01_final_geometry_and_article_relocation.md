# 2026-11-01 선반·물체 형상 설명과 환경 문서 이동

## 요청과 의도

사용자가 선반 크기·경계·작업 영역, 대상·주변 물체의 종류·기본 치수·크기 변형·충돌 형상, 종류별 역할과 선택 방식을 문서로 요청했다. 또한 이 대화에서 요청했던 환경 설명 문서를 모두 `04_article` 안의 서브 폴더로 이동하라고 명시했다.

[선반·물체 형상 문서](../../04_article/environment_reference/FINAL_SHELF_AND_OBJECT_GEOMETRY.md)를 추가하고 [환경 설명 모음](../../04_article/environment_reference/README.md)을 만들었다. 기존 네 문서를 같은 폴더로 이동했다. 해당 폴더의 문서는 코드 근거 설명이며 논문 최종 원고나 확정 연구 결과로 분류하지 않는다. 촉각 구성은 이전 요청에서 별도 문서를 만들지 말라고 했으므로 새 독립 문서로 만들지 않았다.

## 변경 전후와 이동 범위

공통 이전 위치는 `02_implementation/environments`, 새 위치는 `04_article/environment_reference`다.

| 파일 | 처리 |
| --- | --- |
| `FINAL_TRAINING_NETWORKS.md` | 기존 문서 이동 |
| `FINAL_SCENE_GENERATION_AND_RANDOMIZATION.md` | 기존 문서 이동 |
| `FINAL_STATE_AND_PRIVILEGED_INFORMATION.md` | 기존 문서 이동 |
| `FINAL_FT_SENSOR_AND_WRENCH.md` | 기존 문서 이동 |
| `FINAL_SHELF_AND_OBJECT_GEOMETRY.md` | 새 위치에 작성 |
| `README.md` | 새 폴더의 5개 문서 색인 |

기존 환경별 구현 계약·BBOX 모듈 문서와 후속 에이전트용 개발 로그는 기존 위치를 유지했다. 이는 사용자에게 작성해 전달한 설명 문서와 구별한다. 기존 네 문서는 Markdown 링크 destination만 새 위치에 맞췄으며 나머지 본문은 보존했다. 링크 destination을 제거한 전후 문자열의 일치도 프로그램으로 확인했다.

모든 문서의 링크를 원래 위치에서 절대 대상 경로로 해석한 뒤 새 파일 위치 기준으로 다시 계산했다. 이동 문서 내부의 소스·BBOX·구현 계약·로그 링크와, 활성 환경 안내 및 기존 개발 로그 4개의 유입 링크를 수정했다. 과거 실행 기록의 fenced 명령에 들어 있는 옛 경로는 당시 수행 기록이므로 보존했다. 실제 이동은 canonical source/target이 문서 저장소 안인지 확인하고 목적지 파일이 없음을 확인한 뒤 PowerShell `Move-Item -LiteralPath`로 수행했다. recursive 이동·삭제는 없었다.

`04_article/README.md`와 활성 환경 안내에 새 모음과 형상 문서 링크를 추가했다. production 코드·자산·테스트·학습 로그·다른 submodule HEAD는 변경하지 않았다.

## 구현 확인과 문서 내용

- 현재 인계, Final Scene/Env/Event의 실제 경로와 `04_article`의 용어 기준을 확인했다.
- 작업면은 400×1000 mm, local Z 1050 mm다. 전체 선반 외형과 상부 수직 여유는 외부 USD에 의존하므로 작업면 상수와 구별했다.
- 대상 bounds의 20 mm 경계 여유·별도 root 제한, 주변 OBB 5 mm 경계 여유·20 mm 분리 간격·RED를 설명했다. 배치 조건을 가상 벽이나 IK·3D 접근 보장으로 확대하지 않았다.
- 원통 80 mm 직경×100 mm 높이, GoalAccuracy 직육면체 60×80×100 mm, 머그컵 101×70×100 mm, 병 60×60×135 mm의 기본 외곽을 설명했다.
- YCB 4종×3개 size fraction과 uniform fitting 수식을 기록했다. 외부 자산의 미확인 원본 치수를 임의의 실물 치수로 대체하지 않았다.
- mesh/collider/배치 OBB를 구분하고, 머그컵 20조각·병 4조각과 YCB의 box/elliptical-can proxy를 설명했다.
- 물리 12개·논리 10역할·16 variant 후보, 초기 기타 10개 roster의 중복 추출, reset 1/3 범주 선택·조건부 기타 선택·Gray/White 역할 재배정을 설명했다.

## 검증

### 기존 관련 테스트

workspace root에서 실행했다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$geometryDocTemp = Join-Path (Get-Location).Path ('outputs/final_geometry_doc_' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $geometryDocTemp) { throw 'Temporary path already exists' }
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_object_random_geometry.py src/inspire_sweep_baseline/tests/test_final_compact_pool.py src/inspire_sweep_baseline/tests/test_final_obb_layout.py src/inspire_sweep_baseline/tests/test_final_versions.py::test_new_shapes_have_closed_convex_pieces_and_flat_bottom -q --basetemp $geometryDocTemp
```

결과: **28 passed in 5.66s**, exit 0. 크기 fitting·충돌 기하, 역할 분포·중복 방지·부분 mapping, shelf adapter의 offset·yaw·높이와 경계, 절차적 convex mesh를 검사했다. 임시 경로는 고유하게 만들었으며 기존 폴더는 삭제하지 않았다.

### 치수 대조

`final_spawners.py`의 `shelf_object_meshes` 함수 AST와 실제 `flat_collision_mesh`를 실행하는 stdin probe로 꼭짓점 min/max를 집계했다. production 파일은 수정하지 않았다.

| 형상 | local min, m | local max, m | 외곽, mm | 조각 수 |
| --- | --- | --- | --- | --- |
| 직육면체 | (−0.03, −0.04, 0) | (0.03, 0.04, 0.10) | 60×80×100 | 1 |
| 머그컵 | (−0.047, −0.035, 0) | (0.054, 0.035, 0.10) | 101×70×100 | 20 |
| 병 | (−0.03, −0.03, 0) | (0.03, 0.03, 0.135) | 60×60×135 | 4 |

probe 출력의 `bounds_mm` 라벨은 m 단위 배열에 붙은 오기였으므로 위 표에서는 실제 단위를 m로 바로 표시했다. `dimensions_mm` 출력은 1000배 변환한 mm 값이며 본문 표와 일치한다.

### 문서 검사

변경 Markdown 전체의 수식 검사, 전체 저장소 링크 검사, 변경 문서의 workspace 외부 링크 검사와 `git diff --check`를 수행하고 결과를 아래에 기록한다. 기존 문서의 이동 전 파일 부재와 이동 후 파일 존재, 비링크 본문 보존도 확인한다.

결과: 변경 Markdown 13개 수식 검사 통과, 전체 Markdown 427개와 dataset 링크 검사 오류 0, 변경 문서의 workspace 링크 120개를 포함한 검사 오류 0, diff 공백 검사 통과. Git의 LF→CRLF 안내만 있었으며 공백 오류는 없었다. 이동 대상 4개는 이전 위치에 남아 있지 않고 새 위치에 존재한다. 새 폴더에는 설명 문서 5개와 색인 README가 있다. 기존 production 변경 목록은 작업 시작 시와 동일하다.

## 미검증 범위

외부 선반 USD의 전체 외형·판 두께·상부 여유 높이, 각 YCB 원본의 실제 bounds 수치는 미측정이다. 작업면과 fitting 공식으로 확인 가능한 범위를 문서에 명시했다. 신규 Isaac Sim stage 생성·GPU rollout·학습·실제 Markdown/Mermaid UI 렌더링은 수행하지 않았다. 기존 대체 선반 실험 결과를 실제 원본 선반 검증으로 취급하지 않았다.
