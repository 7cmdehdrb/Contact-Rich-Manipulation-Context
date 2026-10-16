# 체크포인트 재생 배속 옵션

[개발 로그 목록](README.md)

`src/inspire_sweep_baseline/scripts/play.py`에 `--playback-speed`를 추가했다. 기본값은 1.0, 양의 유한수만 허용한다. `--real-time` 사용 시 목표 wall-clock 간격을 step_dt / playback_speed로 설정한다. 경과 시간은 monotonic `time.perf_counter()`로 측정한다. 물리 dt, action, reward, controller는 변경하지 않는다. 기존 사용자 작업과 checkpoint 디렉터리는 보존했다.

검증: Python AST로 실제 CLI 정의와 입력 검증문을 추출해 기본값 1.0, 0.25 입력, 0/-1/nan/inf 거부를 확인했다. 전체 스크립트 compile 및 0.02 / 0.25 = 0.08초 계산을 확인했다. 모두 PASS. Isaac Sim 재생 및 영상 녹화는 실행하지 않았다. 녹화 FPS 변경 기능은 포함하지 않는다.
