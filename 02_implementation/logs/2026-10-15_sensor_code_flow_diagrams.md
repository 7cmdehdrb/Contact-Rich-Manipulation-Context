# 패드·F/T 코드 구현 상세 Flow

[로그 안내](README.md) · [정적 자산](../../03_assets/README.md) · [코드 상세 Flow](../../03_assets/inspire-sweep-sensor-code-flows.html) · [기존 전체 Flow](../../03_assets/inspire-sweep-sensor-flows.html)

기준일: 2026-10-15. 사용자는 기존 센서 흐름도보다 패드 자체의 구성과 코드 수준의 구현 방법을 더 구체적으로 설명하는 추가 산출물을 요청했다. 기존 HTML을 유지하고 새로운 자체 포함 HTML에 구조도 1개와 Flowchart 4개를 작성했다. 이전에 사용자가 선택한 기본 스타일과 `doc-wide` 1280×720 크기를 사용했다.

## 대상과 내용

대상은 `src/inspire_sweep_baseline`의 현재 코드다. Workspace `32076d7`, 문서 submodule `87b1a2d`를 기준으로 작업트리를 읽었고, 기존 사용자 변경을 보존했다. 환경·센서·USD 코드는 수정하지 않았다.

| 그림 | 구현 수준의 설명 |
| --- | --- |
| 패드 자산 | 원본 USD의 독립 RigidBody·MassAPI, fixed joint의 body0/body1, visual mesh와 convexHull collider, spawn 시 contact-report API 적용 |
| 영역 생성 | mesh 정점의 sensor-local 변환, XY ConvexHull halfspace, outward facet에서 Z 하한 계산, 부모 collider에서 Z 상한 계산, 표면 probe와 source hash |
| PhysX 연결 | 17-body 직접 view와 12개 단일-parent view, 초기화 시 body index 캐시, raw buffer의 counts/starts gather, reset masking, force scalar × normal |
| 채널 계산 | 점·법선의 로컬 변환, polygon/Z/normal 조건, 정규화 bounds 중심 거리, 단일 채널 배정, index_add_와 직접/투영 Binary OR |
| F/T | Hand rigid body 이동, Axia80 cylinder 생성, 두 고정 조인트의 local pose 작성, incoming-joint wrench에서 자식 행 선택, EEF wrench 변환 |

HTML의 각 그림 아래에는 실제 파일에서 추출한 줄 번호 포함 코드 블록을 넣었다. 손바닥 패드는 pxr로 원본 USD를 직접 열어 확인했다. body에 `PhysicsRigidBodyAPI`와 `PhysicsMassAPI`가 있고 질량은 약 0.001 kg이며, 부모는 `inspire_base_link`다. visual·collision mesh에 각각 저장된 점 항목 96,852개는 taxel 수나 cooked hull의 정점 수를 뜻하지 않는다고 명시했다.

손바닥 영역의 저장 geometry 예와 합성 0.1 N 입력을 사용해 채널 0이 활성화되는 계산을 설명했다. 이 힘은 설명·CPU probe의 입력으로 표시하며 실제 접촉 하중으로 보고하지 않았다. F/T의 1 g 하우징 설정도 현재 코드값과 실물 사양을 구분했다.

## 실행한 검증

Workspace 루트에서 다음 명령을 실행했다.

```bash
/home/min/miniconda3/envs/newton/bin/python -B \
  src/inspire_sweep_baseline/scripts/build_tactile_regions.py --check

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_tactile_geometry.py \
  src/inspire_sweep_baseline/tests/test_tactile_projection.py \
  src/inspire_sweep_baseline/tests/test_observations_and_sensors.py

python3 /home/min/.agents/skills/diagram-design/scripts/self_check.py \
  example/Contact-Rich-Manipulation-Context/03_assets/inspire-sweep-sensor-code-flows.html

sha256sum example/Contact-Rich-Manipulation-Context/03_assets/inspire-sweep-sensor-flows.html
```

결과는 metadata **17 regions / 12 parents / source hashes match**, CPU 검사 **32 passed in 3.32s**, HTML self-check **OK**다. Geometry 테스트는 원본 USD의 각 센서 frame에서 실제 production mapper로 합성 접촉점을 분류한다. GPU solver에서 접촉을 발생시키는 테스트는 아니다.

기존 HTML의 SHA256은 작업 전후 모두 `418b347b9c8c3728b53a0f38266defe986c644b0fa603292f081777586e431e7`로 같았다. 새 HTML과 로그를 추가하고 자산·로그 README에 링크를 등록했다.

문서 submodule 루트의 검사 명령은 다음과 같다.

```bash
python3 00_guidelines/scripts/check_document_links.py --check-external
python3 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/logs/2026-10-15_sensor_code_flow_diagrams.md \
  02_implementation/logs/README.md 03_assets/README.md
git diff --check
```

문서 링크 검사는 **errors: 0**(Markdown 221개, 내부 링크 3,730개, workspace 외부 파일 링크 109개), 수식 검사는 **3 files passed**, 문서 submodule의 `git diff --check`는 통과했다. 별도 Python 정적 검사로 새 HTML의 상대 파일 링크·anchor 존재, 노드 내 Unicode 폭 추정·텍스트 좌표, 직교 경로 명령과 그림별 복잡도 예산을 확인했다. 그림별 노드/화살표 수는 순서대로 **7/6, 6/5, 8/6, 6/5, 6/5**였다.

## 검증 한계

앞선 작업에서 브라우저 보안 정책이 로컬 HTML 탐색을 차단했으므로 우회하거나 재시도하지 않았다. 이번 상세본도 브라우저 화면·실제 웹폰트·인쇄·모바일 렌더링은 확인하지 않았다. 설치된 스킬에 공식 `verify-geometry.py`가 없어 해당 검사는 실행하지 못했다. 자체 정적 검사는 그 공식 검사나 실제 렌더링을 대체하지 않는다.

새 GPU 실행·학습·실물 시험은 수행하지 않았다. PhysX 반력의 실제 기준점·부호 검증, 부모 접촉 투영의 실시간 성능과 GPU 접촉 커버리지는 미검증이다. 현재 부모 투영 filter는 실린더에 한정되며 직접 패드 읽기는 unfiltered라는 구분을 유지한다.
