# Relative-IK Fast-Test 구현 기록

## 요청·기준·범위

사용자는 [개발 명세](../../01_plan/environments/2026-11-09_RELATIVE_IK_CIRCLE_RESET_SPEC.md)를 적용하되 기존 v0_2_2_2-Test를 직접 수정하지 않고 **v0_2_2_2-Fast-Test를 직접 상속 파생**하도록 지정했다. 이는 명세 작성 당시의 적용 기본값을 대체한다.

workspace 기준 HEAD는 `3501ffb`다. 기존 root `.gitignore` 변경과 문서 저장소의 미커밋/미추적 명세·분석 문서를 보존했다. `logs/rsl_rl`을 수정하거나 정리하지 않았다. 새 검증 결과는 `outputs/relative_ik_fast_validation`에 저장했다.

[환경 계약·실행](../environments/WRENCH_REFACTOR_RELATIVE_IK_FAST_TEST_ENVIRONMENT.md)

## 변경 전후와 영향

| 항목 | 부모 | Fast |
| --- | --- | --- |
| 등록 | 기존 Test | 새 Fast-Test, EnvCfg/PPO 직접 상속 |
| IK 표시 | 기본 ON | 기본 OFF, 계산/전송 생략 |
| 장애물 수 | U(0..3)+U(0..3) | 단일 U(0..6) |
| 배치 | OBB RED/GRAY/WHITE, 반복 후보 탐색 | 원 기반 RED/WHITE,5mm 안전 셀 단일 순차 배치 |
| 영역별 설정 | Gray3/White3·padding 등 | 기존 필드는 None, 단일 max_obstacles=6 |
| IK | 작은 batch Torch CPU 우회 | 실제 Warp kernel, 입력 tensor device 유지 |
| 상태 기록 | 기본 arm 기록 후 IK 덮어쓰기 | 최종 arm+기본 hand1회 기록 |
| 가시성 geometry | 매 reset NumPy 반경 계산 | 기존 수식의 반경 startup 캐시 |
| 물성/관측/보상/제어 | 기존 계약 | 상속 보존 |

반지름은 scale 반영 bounds에서1회 계산하고 root↔BBOX 중심 offset을 yaw로 변환한다. 기존2.3cm RED margin 대신 타겟 포함1cm 확장 원을 사용한다. 큰 물체부터 배치하지만 선택 ID와 N을 성공하기 쉬운 쪽으로 바꾸지 않는다. 셀 실패는 명시적 오류다.

Warp 구현은 원래 quaternion FK/axis-angle과 DLS 방정식을 사용한다.6×6 양의 정부호 시스템은 kernel 내 Cholesky로 풀고 기존 delta 최대성분 제한을 적용한다. 비교 repo의 damping·rotation weight·seed·허용 오차를 복사하지 않았다. CPU Warp는 검증용 명시적 device이며 GPU 입력의 자동 CPU fallback은 없다.

runtime 공통 부모의 initializer에는 Fast backend일 때만 단일 개수 검증과1D actual population을 사용하는 분기를 추가했다. 일반 부모의 조건·2D 버퍼·동작은 유지한다. 다른 기존 함수/클래스의 AST는 그대로고 추가 정의만 존재함을 검사했다. `parent_ast_comparison.json`에 비교 내역을 저장했다.

최종 설정 비교는 실제 configclass 의미로 EnvCfg/Scene/Manager 정의를 실행하여 events·Fast 설정·비활성화한 legacy fields 외 차이가 없음을 확인했다. 부모 재생성 결과도 동일했다. PPO는 부모 직접 상속에서 experiment_name만 변경한다. 실제 Sim import/registry 및 PPO 전체 대조는 native probe에도 포함했다.

## 수행한 검증

- 기존 Refactor·Relative-IK Test·IK·OBB·grouped reset와 새 Fast CPU 회귀를 실행했다. 최종 결과는 아래 검사 결과 절에 기록한다.
- Warp CPU에서 실제 kernel을 컴파일/실행했다. 합성 chain batch1/4/8/16/64/128/2048의 기존 solver와 valid/관절각/최종 EEF 오차를 대조했다. 비항등 fixed joint frame과 도달 불가능 입력도 검사했다.
- 실제 패키지 로봇 USD를 CPU에서 열고 생산 코드의 Axia fixed-joint 구성 helper로 센서 연결을 재현했다. 실제 USD joint frame·기본 자세·초기 EEF 샘플 영역의2048개 입력에서 두 solver 성공 판정 일치, 모두 수렴했다. 최대 관절각 차이7.7486e-6rad, 원래 FK로 재계산한 위치 오차 최대0.000497603m, 회전 오차 최대0.000150056rad였다. 이는 PhysX로 스폰한 검증이 아니라 USD/FK/Warp CPU 검증이다. 결과: `usd_ik_cpu.json`.
- 합성 offset BBOX, scale0.9–1.1, 목표 방향 deadzone0–30도를 사용한100,000배치에서 실패0, actual=N, 선반 경계·원 간 비침범을 확인했다. N별 횟수는14210/14177/14286/14473/14407/14325/14122다. 실행 약328초. 결과: `synthetic_layout_stress.json`. **실제 물체 USD geometry100,000표본을 대체하지 않는다.**
- 작은 배치에서는 SciPy bounded least-squares를 독립 RED 거리 검사기로 사용했다. 전체 셀 선택 함수의 결과를 다시 호출하는 자기검증과 구분한다. RED 선분 축퇴·내부·재현성·공간 부족 오류를 검사했다.
- 통합 reset event는 실제 함수와 CPU scene writer double로 검사했다. 선택 환경의 최종 관절1회 기록·기본 hand·zero object velocity·기본 shelf 복구·비선택 상태 보존을 확인했다. IK 실패 시 물리 writer 호출 전에 오류가 발생함도 검사한다. 이는 native PhysX 검증이 아니다.
- 100,000배치 이후 안전 mask/prefix/distance scratch를 최대64행으로 재사용하고 유효셀 선택을 동등한 searchsorted로 바꿨다. 변경 후 회귀에서 기하·재현성 검사를 다시 수행했다. 큰 스트레스 결과는 동일 배치 알고리즘의 scratch 재사용 전 실행이다.

CPU 재현 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_fast_reset.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_ik.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor.py \
  src/inspire_sweep_baseline/tests/test_bbox_scene_layout.py \
  src/inspire_sweep_baseline/tests/test_grouped_reset_pool.py -q -p no:cacheprovider
```

큰 합성 배치 검사는 같은 Python으로 `FAST_LAYOUT_STRESS=100000`을 설정하고 `test_fast_reset.py -k large_circle_stress`를 실행한다. 실제 USD 검사는 설치된 `omni.usd.libs` extension을 PYTHONPATH에, 그 bin과 conda lib를 LD_LIBRARY_PATH에 추가하여 `test_fast_reset.py -k actual_usd`를 실행했다. Warp 테스트 cache는 `/tmp/inspire_fast_warp_cache`다.

## GPU 제약과 남은 검증

현재 `nvidia-smi`가 드라이버와 통신하지 못하고 Torch `cuda.is_available()`은 False, Warp는 CPU device만 제공한다. 기존 분석의 다른 장비 성능을 새 환경 개선율로 사용하지 않는다. GPU 학습·Collection 측정은 실행하지 않았다.

`tests/_wrench_refactor_fast_probe.py`는 native registry/전체 설정·실제 자산100,000배치·물성 불변·부분 reset 비선택 행 보존·timeout 포함180step 확인용이다. 이 스크립트의 실제 GPU 실행과 모델/환경을 고정한100iteration 비교가 남아 있다. 실제 물체 배치 불가능 사례가 발견되면 N/목표를 재추첨하는 fallback 대신 명세의 실패 처리/보완 절차를 따른다.

코드 및 CPU 검증 완료와 별개로 명세의 실제 자산·GPU 출시 기준은 충족 여부를 확인하지 못했다. 장기 안정성·정책 성과·Collection 개선은 미검증이다.

## 최종 검사 결과

- 전체 CPU 회귀: **156 passed, 8 skipped** (13.98초). 선택 실행이 필요한 스트레스/USD 검사 및 기존 선택 검사는 기본 실행에서 skip된다.
- IK 실패 시 물리 writer 미호출 assertion을 추가한 최종 Fast 재검사: **8 passed, 2 skipped** (4.54초). 두 skip은 별도 실행하여 통과한100,000배치/실제 USD 검사다.
- 문서 수식·내부 링크 검사와 workspace/문서 저장소 `git diff --check`를 수행했다.
- 사용자 기존 `.gitignore` 변경과 문서 submodule 작업트리를 보존했다. 커밋·학습·로그 정리는 수행하지 않았다.
