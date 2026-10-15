# Tactile·F/T 센서 구현 흐름도

[로그 안내](README.md) · [정적 자산](../../03_assets/README.md) · [흐름도 HTML](../../03_assets/inspire-sweep-sensor-flows.html)

기준일: 2026-10-15. 사용자가 `diagram-design` 스킬로 요청한 `src/inspire_sweep_baseline`의 Tactile·F/T 구현 Flow를 실제 작업트리 코드 기준으로 작성했다. 사용자가 기본 스타일을 선택했다. HTML 안에 1280×720 정적 SVG 두 개와 코드 근거를 포함한다.

## 기준과 변경

Workspace HEAD는 `32076d7`, 문서 submodule HEAD는 `87b1a2d`다. 문서와 Sweep-Policy submodule에는 기존 사용자 변경이 있었으며 보존했다. 이번 변경은 HTML 자산, 이 로그, 두 색인의 링크 추가다. 센서·환경 코드와 자산 geometry는 변경하지 않았다.

- Tactile: `Isaac-Inspire-Sweep-Baseline-Tactile-v0`의 17개 pad 직접 법선 접촉력과 12개 parent view의 실린더 접촉점 투영을 표시했다. 영역별 합산·별도 threshold·Binary OR·57D 관측 연결을 설명한다. 기본 `Isaac-Inspire-Sweep-Baseline-v0`의 손바닥 1D와 전체 관측 41D는 별도 설명으로 구분한다.
- F/T: Axia80 body와 고정 조인트 생성, 자식 `inspire_base_link`의 incoming-joint 반력 선택, 부모 `axia80_link`에서 EEF로의 회전과 모멘트 이동, 6D 관측 연결을 표시했다.
- 공통: reset 행의 0 마스킹, 물리 100 Hz와 정책 50 Hz를 명시했다. 현재 물체 위치를 사용하는 관측을 최종 Blind 관측과 구분한다.

기준 코드는 [tactile_env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/tactile_env_cfg.py), [tactile_observations.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/tactile_observations.py), [sensors.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/sensors.py), [observations.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/observations.py), [robot.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/robot.py), [env.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/env.py), [env_cfg.py](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/env_cfg.py)다. 로컬 [Isaac Lab 반력 API](../../../../IsaacLab/source/isaaclab/isaaclab/assets/articulation/articulation_data.py)의 부모 body frame 설명도 대조했다.

## 실행 검증

Workspace 루트에서 다음 명령을 실행했다.

```bash
python3 /home/min/.agents/skills/diagram-design/scripts/self_check.py \
  example/Contact-Rich-Manipulation-Context/03_assets/inspire-sweep-sensor-flows.html

env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_observations_and_sensors.py \
  src/inspire_sweep_baseline/tests/test_tactile_observations.py \
  src/inspire_sweep_baseline/tests/test_tactile_projection.py \
  src/inspire_sweep_baseline/tests/test_tactile_configuration.py \
  src/inspire_sweep_baseline/tests/test_tactile_gpu_filters.py
```

HTML self-check는 통과했고 CPU 테스트는 **64 passed in 3.80s**였다. 입력 순서·reset 마스킹·힘 변환·영역 투영·설정·GPU 필터 계약의 CPU 검증이며 실제 GPU 접촉 실험은 아니다.

문서 submodule 루트에서 다음 검사를 실행했다.

```bash
python3 00_guidelines/scripts/check_document_links.py --check-external
python3 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/logs/2026-10-15_sensor_flow_diagrams.md \
  02_implementation/logs/README.md 03_assets/README.md
git diff --check
```

문서 링크 검사 결과는 **errors: 0**(Markdown 220개, 내부 링크 3,723개, workspace 외부 파일 링크 109개), Markdown 수식 검사는 **3 files passed**였다. Workspace와 문서 submodule의 `git diff --check`도 통과했다. HTML의 상대 파일 링크와 내부 anchor를 별도 Python 검사로 확인했다. SVG는 각각 Tactile 7 nodes / 7 arrows, F/T 6 nodes / 5 arrows로 예산 안에 있으며, Unicode 문자 폭 추정과 노드 경계, 직교 경로 명령을 정적으로 검사했다. 이는 실제 글꼴 렌더링이나 전체 connector geometry 공식 검사를 대체하지 않는다.

## 미검증 범위

Browser 스킬로 로컬 HTML의 렌더링 확인을 시도했으나 브라우저 URL 보안 정책이 `file://` 탐색을 거부했다. 우회하지 않았다. 따라서 실제 화면·웹폰트 로딩·브라우저별 인쇄·모바일 표시 검증은 미완료다. Google Fonts 연결이 없으면 로컬 대체 서체를 사용하도록 HTML에 명시했다. 설치된 diagram-design에는 `verify-geometry.py`가 없어 해당 공식 geometry checker는 실행하지 않았다.

이번 작업은 CPU 코드와 정적 문서를 확인했다. PhysX의 실제 반력 기준점·부호·크기, GPU 접촉점 수집·FPS, 학습·정책 성공률과 실물 센서 특성은 새로 검증하지 않았다. 특히 F/T 그림의 F 기준점은 현재 코드가 사용하는 Axia80 body 위치를 나타낸다.
