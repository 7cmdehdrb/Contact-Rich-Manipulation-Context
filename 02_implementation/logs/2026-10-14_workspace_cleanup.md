# Workspace 패키지와 문서 정리 기록

[개발 로그 목록](README.md) · [Workspace 안내](../../00_guidelines/10_WORKSPACE_GUIDE.md) · [개발 지침](../../00_guidelines/09_DEVELOPMENT_GUIDE.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기록일: 2026-10-14. 사용자가 지정한 두 활성 패키지를 남기고, 전체 프로젝트 문서·참고 환경 설명·일반 지식의 보관 위치를 구분했다. 이 작업은 패키지와 문서 정리이며 새로운 정책의 학습 성능이나 실물 검증 결과가 아니다.

## 기준 코드 상태

| 저장소 | 작업 시작 기준 revision |
| --- | --- |
| 상위 Workspace, `main` | `953c34f6edf23b2b38ebf78f13fac7c30244568b` |
| Contact-Rich-Manipulation-Context | `94333d2fe714f9951cb561ee51322017c4fcc3bc` |
| Sweep-Policy | `25866dcffe940ff2c44b610a44a174819cb6671a` |
| IsaacLab | `929f0fe1e9c1699efebf31b2ad0ab723a7d6e7e9` |
| UR Description | `18e6f603b3ebc2ec479fecb62d6be544b15755e9` |

시작 시 Baseline의 코드·테스트·README 수정과 Omni 관련 신규 파일, 루트 문서의 `docs/` 이동 흔적이 있었다. 해당 사용자 변경을 보존했다. 문서 및 참고 코드 서브모듈은 시작 시 변경이 없었다. 이번 결과는 커밋하지 않은 로컬 작업트리 변경이다.

## 패키지와 탐색 경로

`src`에는 `inspire_sweep_baseline`, `axia80_feasibility`, `trash`만 남겼다. 과거 패키지·실험 디렉터리 11개와 namespace/cache를 `src/trash`로 이동했다. 비활성 환경의 루트 Python 테스트·분석 도구 6개는 `src/trash/workspace_tests`로 옮겼다. 전체 목록은 [보관 안내](../../../../src/trash/README.md)에 있다.

UR Description은 서브모듈을 유지하면서 `git mv`로 `src/trash/Universal_Robots_ROS2_Description`에 이동했다. `.gitmodules` 경로와 Git의 worktree 정보를 같이 갱신했다. 문서 전용 Context와 참고용 Sweep-Policy는 기존 서브모듈 등록을 유지한다.

`src/trash`와 `example`, 그리고 `build`, `install`, `log`, `logs`, `outputs`, `videos`, `reports`에 `COLCON_IGNORE`, `AMENT_IGNORE`, `CATKIN_IGNORE`를 두었다. `.gitignore` 예외를 추가해 표식을 Git 추적 대상에 포함할 수 있도록 했다. `logs`의 옛 학습 source 복사본도 `colcon`에 발견되는 것을 확인하여 산출물 디렉터리까지 제외했다. 기존 빌드·학습·실험 산출물은 보존했다.

루트 `pytest.ini`는 `tests`, `src/inspire_sweep_baseline/tests`, `scene_randomization`을 기본 탐색하고 보관·참고·framework·산출물 트리를 제외한다. 활성 패키지는 현재 Python/Isaac Lab 패키지이며 ROS 패키지로 colcon에 등록되지 않는다.

## 이동으로 달라진 자산 참조

Axia80의 `model.py`와 `cantilever_model.py`가 사용하는 UR Description 경로 및 root 탐색 조건을 새 보관 위치로 바꿨다. 생성된 URDF 5개에도 옛 절대 mesh 경로가 남아 있어 경로 부분만 갱신하고 모든 mesh 파일의 존재를 검사했다. 모델 형상·질량·제어 설정은 바꾸지 않았다. 다른 위치로 checkout하거나 USD 캐시가 남으면 활성 스크립트의 모델 생성 및 `--force_conversion` 절차를 따른다.

Sweep-Policy의 Inspire USD·센서 source resolver와 해당 자산을 확인하는 기존 테스트 3개도 `src/trash/hand_manipulation_rl`로 바꿨다. 옛 YAML 예제 경로와 현재 controller 설정에 맞지 않는 주석은 실제 코드 기준으로 고쳤다. 학습 설정과 실행 로직의 변경은 없다. 상세 내용과 확인한 기존 불일치는 [Sweep-Policy 개발 로그](../../../Sweep-Policy/docs/DEVELOPMENT_LOG.md)에 있다.

## 문서 정리

- 상위 README를 현행 Workspace 진입점으로 작성하고 `AGENTS.md`를 추가했다.
- 전체 연구 Flow·패키지 역할·개발 지침·상속·실행 명령을 이 문서 저장소에서 연결했다.
- 이전 루트 README 설계안과 7월 TODO, 과거 환경 수정 요청은 [역사 자료](../../01_plan/history/README.md)에 보존했다. 과거 Blind Sweeping 구현 계획도 [실험·설계 기록](../../01_plan/experiments/2026-09-26_blind_sweeping_build_plan.md)으로 옮겼다.
- Baseline의 Omni 상세와 보상 계획을 [환경 구성](../environments/OMNI_ENVIRONMENT.md), [보상 초안](../../01_plan/environments/OMNI_REWARD_PLAN.md)으로 모으고 패키지 README에서 연결했다.
- 루트 `docs/PLAY.md`는 활성 환경의 실행 안내에 통합했다. 루트 `docs/TODO.md`와 `tests`의 연구 Markdown 두 개는 이관 후 원본을 정리했다.
- 참고 프로젝트의 일반 ROS/Python 설명은 [상위 일반 지식](../../../../docs/ROS2_PYTHON_ENVIRONMENTS.md)으로 옮겨 핵심 조건만 남겼다. SSH/PPTP 문서 형식도 정리했다.
- Context 안에 있던 Axia80 실행 코드 스냅샷 28개 파일은 [보관 위치](../../../../src/trash/context_artifacts/axia80_feasibility)로 옮겼다. CSV·metadata·run log는 `03_assets/artifacts/axia80_feasibility/results`에 유지하고 과거 실험 문서의 링크를 갱신했다. 문서 검사 도구는 문서 관리 용도로 유지한다.

## 실행한 검증

아래 명령은 상위 Workspace 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider

colcon list --base-paths src
colcon list --base-paths .
git submodule status
git diff --check
git diff --cached --check
```

| 검사 | 결과 |
| --- | --- |
| 활성 패키지·Scene 기본 테스트 | **135 passed, 26 subtests passed**, 10.40초 |
| 위 suite 중 활성 패키지 지정 검사 | 114 passed, 17 subtests passed |
| `colcon list`, `src` 및 Workspace 전체 | 둘 다 검색 패키지 없음 |
| 기존 이동 파일 내용 비교 | 2,214개 파일 SHA-256 일치, 누락·내용 변경 0개 |
| Context 코드 스냅샷 이동 비교 | 28개 파일 SHA-256 일치 |
| URDF mesh 경로 | 생성 URDF 5개 갱신 및 참조 파일 존재 확인 |
| 서브모듈 | 네 저장소 revision 유지, UR Description의 새 경로에서 Git 접근 정상 |

ROS `launch_testing`의 외부 pytest plugin이 Isaac Lab 환경에서 `lark` 누락으로 수집에 간섭하므로 위 테스트는 ROS 경로와 자동 plugin 로딩을 제외했다. 시스템·공통 Python 환경에 패키지를 추가 설치하지 않았다.

참고 Sweep-Policy는 관련 검사 14 passed, 2 skipped, 14 subtests passed였다. 이 환경의 `pxr` 부재로 USD topology 두 검사는 skip됐다. 과거 v1 tuple action scale과 v2 absolute OSC를 기대하는 기존 계약 테스트는 각각 1개 실패했으며 현재 config의 동작은 이번 작업 전과 동일하다. 해당 과거 기대값과 실제 구현의 차이는 참고 프로젝트 개발 로그에 기록했다.

문서 232개의 로컬 링크 3,162개와 anchor 링크 303개를 검사해 누락 0개를 확인했다. 변경 Markdown 58개의 수식 검사와 상위 Workspace·Context·Sweep-Policy의 작업트리/인덱스 whitespace 검사도 통과했다. 없어진 문서는 현재 자료로 연결하거나 미확보임을 기록했으며 빈 구현·성과 문서는 만들지 않았다.

## 확인 범위

이번 정리에서 Isaac Sim의 GPU 환경 생성·학습·재생, 선반 자산 서버 접속, Axia80 하중 시뮬레이션 재실행이나 실물 로봇·센서 시험은 수행하지 않았다. 이전에 설치하거나 source한 ROS overlay는 파일 이동만으로 사라지지 않으므로 활성 실행 환경은 [상위 README](../../../../README.md)의 안내를 따른다.
