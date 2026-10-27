# Inspire Hand 촉각 벡터 검증 패키지

[개발 로그 목록](README.md) · [활성 환경과 명령](../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md.txt) · [패키지 안내](../../../../src/inspire_tactile_validation/README.md)

기준 workspace commit `80a1b96e872ff78afe71a10b5a07a06a10df2190`. 작업 시작 당시 패키지 README와 문서 submodule에 있던 사용자 변경을 보존했다. 사용자 요청으로 활성 범위에 새 `src/inspire_tactile_validation` 패키지를 추가했다. 기존 RL 환경·센서·자산 파일은 수정하지 않았다.

## 구현

Isaac Lab AppLauncher/SimulationContext/InteractiveScene 기반 standalone이다. production USD를 읽기 전용 참조해 30개 Hand body와 12개 Hand 관절·17개 패드 fixed joint를 유지하고 Arm을 활성 물리에서 제거한다. 실제 손바닥 패드 법선을 +Z로 정렬해 base를 고정한다. Hand fully-open 목표와 PD·노력/속도 제한은 기존 환경에서 복사한다. 중력을 끄고 sleeping을 비활성화한 시험 fixture다.

17개 패드 각각 실제 polygon의 중앙·inset 모서리 4개를 만든다. 85개 env에서 각각 다른 위치를 누르고 반복한다. probe는 radius 0.75mm, cylinder length 30mm capsule, mass 50g다. capped 100N/m Cartesian servo와 inertia-scaled orientation servo로 접근·유지·복귀하며, 누르는 동안 pose를 순간이동시키지 않는다.

관측은 기존 `ProjectedTactileContactBits`를 수정 없이 사용한다. 직접 패드 + 부모 링크 contact projection을 재사용하고 상대 필터만 probe로 바꾼다. 독립 probe contact tensor에서 목표 body·XY 영역·0.05N 하중을 확인한다. 막대 외력·속도에서 계산한 force balance도 로그에 남겨, 기준 contact sensor가 잘못된 값을 보고할 가능성을 구분한다. 접촉 centroid는 body별 평균으로 개별 접촉점과 구분한다. 기준 영역 판정에 원래 reader의 Z/normal 조건을 재사용하지 않는다.

무접촉·하중 부족·오접촉·센서 미검출·기준 힘 불일치를 구분하고 원시 CSV, trial CSV, 17×17 confusion, summary JSON, 소스 해시와 옵션 metadata를 저장한다. 보고기의 정상 판정은 trial-any 검출뿐 아니라 채널 선택성·무접촉 오검출·복귀 잔류·기준 불일치도 검사한다.

## 실제 GPU 실행

실제 launcher 경로를 명확히 하기 위해 다음 명령을 실행했다. 일반 사용자는 패키지 README의 IsaacLab launcher 명령을 사용한다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  TERM=xterm PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_tactile_validation/scripts/run_probe_test.py \
  --headless --num-envs 85 --repeats 3 \
  --output-dir outputs/inspire_tactile_validation/validation_255_01
```

RTX 3090 / Isaac Sim 5.1 / CUDA에서 255/255 trial, 42,075 frame 수집 완료. `status_counts`는 detected 66, reference_mismatch 186, miscontact 3이다. 독립 유효 loaded trial은 66이고 그 안에서 target bit는 모두 검출됐지만, 검출 trial에도 hold 기준 불일치가 남아 clean pass는 0이다. 전체 판정은 inconclusive다. 총 252 trial에서 하나 이상의 hold 기준 불일치가 기록됐다. **66/66만 보고 정확도 100%로 결론 내리지 않는다.**

`balance_palm_02`의 손바닥 중앙 hold 예: 명령 힘 약 0.733N, force balance 약 0.733N, probe speed 약 0.00024m/s, contact report 약 0.000023N이었다. TGS 외력 반복 적용(`force_iterations_palm_01`), PGS(`pgs_palm_01`), sleeping 비활성화(`awake_palm_01`) 대조에서 불일치는 해소되지 않았다. 원인은 아직 확정하지 않았다. 외력·가속도 평형은 외부 실제 force sensor 정답과 동일하지 않다.

초기 시도에서 모든 clone의 root를 같은 local pose로 쓰는 문제가 있어 env_origins를 더하도록 수정했다. 매 batch reset 이후 FK 안정화, parent와 pad에 전달된 하중의 분리, footprint 검증, retract 성공 제외, 기준 불일치 진단을 추가했다. 초기 디버그 산출물은 위 경로에 보존했으며 최종 255회와 혼합 집계하지 않는다.

3 env로 10개 위치를 검사한 `batch_strict_10_01`에서 3+3+3+1 batch와 10개만의 결과 저장을 확인했다. 초기 strict 종료 코드가 Kit shutdown에서 0으로 덮이는 문제를 발견해 Kit post_quit에 exit code를 먼저 전달하도록 수정했다. 종료 시 standalone의 pause loop를 비활성화해 앱 정리가 끝나도록 했다.

## CPU 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_tactile_validation/tests
```

Footprint 내부·모서리 생성, invalid input, 미접촉/센서 miss 구분, body 오접촉, 유효 분모, 복귀-only 검출 제외, 기준 불일치와 집계 출력을 검증했다. 최종 실행 수치는 아래 후속 검증에 기록한다.

## 한계

실제 GPU 시뮬레이션과 데이터 수집은 실행했다. 실물 센서·압력 calibration·연속 힘 정확도 검증은 수행하지 않았다. GUI 육안 확인은 수행하지 않았고 palm-up pose·Hand-only topology는 코드/물리 상태로 확인했다. 시험 fixture와 기존 RL의 중력·외력/솔버 조건 차이를 패키지 README에 명시했다. 기준 불일치가 해결되기 전 전체 촉각의 정상 동작을 확정할 수 없다.

## 후속 검증 결과

최종 CPU: 38 passed (0.07s). `strict_exit_05_02`에서 2 env에 5개 위치를 2+2+1 batch로 실행했고, 의도적으로 짧은 접촉 시퀀스로 invalid 결과가 생겼을 때 실제 프로세스 exit code 2를 확인했다. 이 run은 코드/CSV 구조 및 종료 코드 검사이며 센서 성능 집계에는 사용하지 않는다. clone별 Hand root의 환경 상대 pose 동일성 assertion도 통과했다.
