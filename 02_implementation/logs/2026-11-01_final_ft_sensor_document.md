# 2026-11-01 최종 환경 F/T 센서와 Wrench 계측 문서 작성

## 요청·의도와 변경 전후

사용자가 해당 최종 환경에서 F/T 센서를 묘사한 실린더의 크기와 wrench 계측 방법을 설명하는 문서를 요청했다. 현재 인계와 코드의 최신 `Isaac-Inspire-Final-GoalAccuracy-v0_2_2`를 대상으로 [F/T 센서·계측 문서](../../04_article/environment_reference/FINAL_FT_SENSOR_AND_WRENCH.md)를 추가했다.

기존 State 문서의 6D 관측 개요에 이어, 이번 문서는 하우징 치수·연결, 측정 원점과 EEF의 차이, 원시 반력 조회, Newton–Euler 보상, 반력 부호 및 관측 노이즈를 설명한다. [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)에 새 문서 링크를 추가했다. production 코드·자산·설정·테스트와 기존 사용자 작업은 수정하지 않았으며 학습 로그도 건드리지 않았다.

## 소스 확인과 주요 결론

- 현재 `assets/robot.py`의 radius 0.041 m, height 0.0254 m, mass 0.001 kg 확인. 실린더 직경은 82 mm이며 실제 하드웨어 질량으로 해석하지 않았다.
- 최신 Final Scene은 `make_robot_cfg`와 기존 EEF 설정을 상속하며 센서 값을 덮어쓰지 않는다.
- 하우징 중심 H는 기존 장착 위치에서 12.7 mm, 측정 관절 J는 25.4 mm, EEF는 155.4 mm다. J→EEF는 130 mm. 이 값은 local Z축 기준이며 world 방향으로 고정되지 않는다.
- incoming wrench는 `inspire_base_link` 이름으로 body index를 찾아 읽으며 sensor housing의 body index를 사용하지 않는다.
- 로컬 Isaac Lab wrapper의 parent-frame 설명과 실제 child-joint-frame 처리의 차이를 발견했다. 공식 PhysX Tensor API 108.0 문서의 `get_link_incoming_joint_force` 정의가 child joint frame임을 확인했다. latest URL은 본문이 없어 버전 고정 문서의 실제 본문을 읽었다. 이 API 의미 확인을 설치 버전 업그레이드나 새 runtime 검증으로 해석하지 않는다.
- 손 13링크와 17 pad의 질량·COM 운동·관성으로 지지 wrench를 계산한다. 상류 housing·arm은 제외한다. raw/support/pure 모두 EEF 기준점에서 world/EEF 축 표현을 구별했다.
- `pure = raw − support`이며 외력과 반대 부호의 반력 residual이다. 초기 tare나 학습 보상기를 쓰지 않는다.
- 관측은 pure_eef에 축별 Gaussian noise를 더한 6D다. reset mask·동일 step 캐시·50 Hz 정책 갱신을 설명했다.

## 검증

workspace root에서 기존 단위 테스트만 실행했다. 고유한 임시 경로를 사용하고 기존 폴더는 삭제하지 않았다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$ftDocTemp = Join-Path (Get-Location).Path ('outputs/final_ft_doc_pytest_' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $ftDocTemp) { throw 'Temporary path already exists' }
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py src/inspire_sweep_baseline/tests/test_final_versions.py::test_wrist_wrench_observation_noise_has_requested_per_axis_sigma -q --basetemp $ftDocTemp
```

결과: **8 passed in 6.87s**, exit 0. Mock robot/PhysX view와 실제 보상 함수의 Newton–Euler 계산, 링크 순서 독립성·상류 질량 제외, 정적·동적 지지 하중 제거, 외력 부호·12.7 mm 원점 혼동 방지, reset 행 masking, 누락 pad 오류, 관측 노이즈를 검사했다. 소스 파일 이름이 이전 계열을 포함하지만 테스트 대상은 현재 Final이 직접 사용하는 공통 보상 모듈이다.

문서 저장소에서 다음을 실행했다.

```powershell
python 00_guidelines/scripts/check_markdown_math.py 02_implementation/environments/FINAL_FT_SENSOR_AND_WRENCH.md 02_implementation/logs/2026-11-01_final_ft_sensor_document.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md
python 00_guidelines/scripts/check_document_links.py
python 00_guidelines/scripts/check_document_links.py --check-external 02_implementation/environments/FINAL_FT_SENSOR_AND_WRENCH.md 02_implementation/logs/2026-11-01_final_ft_sensor_document.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md
git diff --check
```

결과: 변경 Markdown 3개 수식 검사 통과, 전체 Markdown 424개와 dataset 링크 검사 오류 0, 변경 문서의 workspace 링크 16개를 포함한 검사 오류 0, diff 공백 검사 통과. 공식 API URL은 웹 도구로 본문을 직접 확인했으며 링크 검사 도구의 URL 집계를 HTTP 검증으로 해석하지 않는다. 기존 파일의 LF→CRLF 안내만 있었고 공백 오류는 없었다. root production 변경 목록이 작업 시작 시와 동일함을 확인했다.

## 최종 대조와 미검증

요청한 실린더 크기는 반지름·직경·높이와 형상 축으로 명시했고, 계측은 원시 데이터의 출처부터 기준점 이동·보상 수식·부호·노이즈·Actor/Critic 전달까지 포함했다. 하우징 중심을 측정점으로 오해하거나 raw를 순수 외력으로 해석하지 않도록 차이를 설명했다.

이번 작업에서 새 Isaac Sim stage 생성·GPU rollout·학습·실제 센서 비교는 수행하지 않았다. 실제 Markdown/Mermaid UI 렌더링은 미검증이다. 하드웨어 정격·분해능을 추정하지 않았으며 기존 다른 패키지의 과거 센서 실험을 현행 환경의 검증으로 사용하지 않았다.
