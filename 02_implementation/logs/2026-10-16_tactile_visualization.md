# 촉각 검증 결과 시각화

[개발 로그 목록](README.md) · [검증 구현](2026-10-16_tactile_validation.md)

사용자 요청에 따라 `scripts/plot_results.py`를 추가했다. 원시 데이터는 수정하지 않고 최신 날짜 run `outputs/inspire_tactile_validation/2026-10-16_13-11-03` 하나만 사용했다. summary/trials/sample의 건수·ID·frame 수 일치를 확인하고, 255회/42,075 frame에서 PNG 5개 및 통합 PDF를 생성했다.

전체/채널별 상태, 17×15 위치·반복 결과, 유효 접촉을 분모로 한 채널 혼동행렬(미관측 NA), 결정적으로 선택한 trial 0·1의 힘/bit 시계열, trial별 hold 중앙값 산점도를 포함한다. 검출 66, 기준 불일치 186, 오접촉 3을 원본 집계와 대조했다. detected 상태에도 기준 불일치가 겹치며 clean pass 0임을 표시했다. 예시의 무접촉 baseline 힘 평형선이 약 0.49N인 점을 주석으로 명시하고 calibrated contact reference로 해석하지 않는다.

실행 명령:

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python -B src/inspire_tactile_validation/scripts/plot_results.py
```

정상 종료. PNG를 실제 열어 레이블·legend·축·데이터를 확인했고 최초 overview의 잘린 왼쪽 라벨은 여백을 늘려 수정했다. 재시뮬레이션은 수행하지 않았다. 과학적 그림 산출물로 PNG/PDF를 제공하며 새 시각화 전용 테스트는 추가하지 않았다.
