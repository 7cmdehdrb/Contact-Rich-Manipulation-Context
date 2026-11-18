# Reach 보상 거리 그래프

## 요청·의도

사용자는 현재 EEF–타겟 3차원 거리를 가로축, 스텝 보상을 세로축으로 표시하고 caption·라벨에 Times New Roman을 요구했다. 직전 지시에 따라 시간 간격 계수를 생략한 식을 시각화했다.

## 변경 전후·영향

환경 코드·설정 수정 없이 workspace의 `outputs/reach_reward_2026-11-14/`에 재현용 `plot_reach_reward.py`, PNG·PDF·SVG와 CSV를 추가했다. 기존 사용자 변경과 학습 로그는 보존했다. 초기 root 거리 미지정에 따라 0.20·0.30·0.50 m를 명시적인 예시 곡선으로 사용했다.

```math
B_0=\max(D_{\mathrm{root},0}-0.10,0),\qquad B_t=\max(D_t-0.10,0)
```

```math
R_t=\frac{0.3B_0}{0.10+B_t}
```

초기 거리는 EEF–물체 root 기준이며 현재 거리는 EEF–실시간 BBOX 중심 기준이다. 가로축 범위는 0–0.60 m다. 사용자 요청에 따른 시간 계수 생략 표현이므로 실제 RewardManager의 시간 적분 적용 후 값과 구별한다. Finger-v2 후퇴 단계 전환은 표현하지 않는다.

## 검증·최종 대조

- `env_isaaclab` Python과 Matplotlib 3.10.3으로 생성했다.
- Microsoft Core Fonts 배포의 Times New Roman 원본을 `/tmp/reach-times-fonts/`로 추출하여 프로세스에만 등록했다. 시스템 폰트 설치는 수행하지 않았다.
- 0.10 m 이내 plateau, 이후 단조 감소와 0.20 m 지점의 수치를 assertion으로 확인했다.
- PNG를 직접 확인하여 라벨·범례·수식의 겹침과 잘림이 없음을 확인했다.
- `pdffonts`에서 TimesNewRomanPSMT와 TimesNewRomanPS-ItalicMT만 사용·임베드됨을 확인했다.
- Markdown 수식 검사와 변경 로그 공백 검사를 통과했다. 문서 링크 검사 결과는 실행 출력에 보존했다.
- GPU·학습 검증은 수행하지 않았다. 본 작업은 분석용 산출물 생성이며 정책 동작 변경은 없다.

## 재현

```bash
MPLCONFIGDIR=/tmp/reach-mplconfig /home/min/miniconda3/envs/env_isaaclab/bin/python outputs/reach_reward_2026-11-14/plot_reach_reward.py --font-dir /tmp/reach-times-fonts
```

폰트 디렉토리는 Times.TTF·Timesi.TTF 등을 포함해야 하며 임시 파일 삭제 후에는 같은 폰트를 다시 준비해야 한다.
