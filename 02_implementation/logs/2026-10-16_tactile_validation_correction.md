# 촉각 검증 루프 수정과 원본/노출 배치 비교

[개발 로그 목록](README.md) · [초기 구현](2026-10-16_tactile_validation.md) · [초기 시각화](2026-10-16_tactile_visualization.md) · [패키지 안내](../../../../src/inspire_tactile_validation/README.md)

사용자는 검증 패키지에만 수정을 적용하고 `src/inspire_sweep_baseline`을 건드리지 않도록 요청했다. 기존 변경과 결과는 보존했다. baseline의 tactile_env_cfg.py, mdp/tactile_observations.py, assets/robot.py SHA256이 작업 시작/종료 시 일치함을 확인했다. baseline의 기존 README 변경도 유지했다.

## 원인과 변경

이전 검증은 physics dt=0.01, render dt=0.02에서 기본 sim.step()을 호출해 실제 두 physics tick을 진행했다. 외력을 한 번만 공급한 뒤 두 번째 tick의 접촉을 읽고 scene.update에는 0.01만 전달했다. 단일 tick 진단에서 손바닥 hold가 약 0.000246N/bit0에서 1.202N/bit1로 바뀌었다. 초기 72.9%를 센서 미검출률로 해석하면 안 된다.

새 stepping.advance_physics는 sim.step(render=False)로 한 tick 진행하고 실제 clock delta=dt를 검사한 뒤 sensor를 갱신한다. GUI 렌더는 별도이며 시간 진행이 없음을 검사한다. 또한 world gravity=(0,0,0)을 명시해 이전 무접촉 baseline의 약 0.4905N 기준 오프셋을 제거했다.

원본 패드 6개는 부모 hull 안에 있지만 기존 부모 접촉 투영이 이를 보완한다. 수정 후 원본 배치도 85회 모두 검출되어 기본 `--pad-layout original`을 유지했다. 별도 `exposed` 선택 시 패드 mesh와 body를 로컬 +Z로 이동해 최하단이 부모 max Z보다 1mm 위에 오도록 하고 fixed attachment를 재설정한다. 원본 USD 파일에는 쓰지 않는다. 패드 footprint와 ContactSensor 계산은 동일하다. 이동량은 metadata에 기록한다. 원본과 노출 배치는 다른 시험 fixture임을 명시했다.

## 실제 GPU 실행

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  TERM=xterm PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -u -B \
  src/inspire_tactile_validation/scripts/run_probe_test.py \
  --headless --num-envs 85 --repeats 3 --strict
```

RTX3090 / Isaac Sim5.1에서 원본 배치 `outputs/inspire_tactile_validation/2026-10-16_13-33-55`: 255/255 trial 검출, 기준 불일치·오접촉·오채널·복귀 잔류 0, strict exit0. 유효 하중 frame은 8475개이며 8430개 검출(99.469%). 검지3 X−Y+ 모서리의 15/30 frame 검출이 3회 반복돼 45 frame 누락이다. trial-any 통과와 frame 완전 검출을 구분한다.

노출 배치의 동일 명령에 `--pad-layout exposed`를 사용한 `2026-10-16_13-30-20`: 255/255 trial 검출, 8130/8130 유효 frame 검출, 기준 불일치·오접촉·오채널·복귀 잔류0, strict exit0. 첫 85개 smoke와 원본 배치85개 대조도 각각 통과했다. 두 255회 run 모두 원시 42,075 frame을 저장했다. 원본 무접촉 baseline의 contact report와 force balance 최대값은 0이었다.

## 집계·시각화

summary에 유효 하중 frame 수/검출 수/가중 검출률을 추가했다. 두 신규 run의 기존 raw CSV에서 추가 집계만 재생성했고 원시 데이터와 이전 run은 수정하지 않았다. 원본/노출 비교를 통해 원본 형상 검증과 직접 패드 노출 검증을 구분한다.

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_tactile_validation/scripts/plot_results.py \
  --input outputs/inspire_tactile_validation/2026-10-16_13-33-55 \
  --compare-with outputs/inspire_tactile_validation/2026-10-16_13-11-03
```

노출 run도 같은 방식으로 생성했다. 원래 다섯 그림에 전후 비교와 hold 하중/bit duty heatmap을 추가했다. PNG/PDF를 실제 확인하고 trial-any와 frame 검출률, 배치 차이를 주석으로 표시했다. 비교는 솔버 시간·중력·배치 조건이 달라 단일 변수의 정확도 개선치로 해석하지 않는다.

## 검증 명령

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_tactile_validation/tests
```

42 passed (0.09s). 새 테스트는 단일 tick 강제, write/step/update/render 순서, 추가 physics tick 및 렌더 시간 진행 거부, frame 수 가중 집계를 검증한다. 실제 GPU에서도 매 tick clock assertion이 통과했다. GUI 육안 검증과 실물 센서 검증은 수행하지 않았다.
