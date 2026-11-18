# Goal Distance 두 방식 비교 그래프

## 요청·의도와 변경

사용자는 Prof-v2와 Finger-ForceDirection-v0의 Goal Distance 보상을 모두 플롯하도록 요청했다. 환경 코드는 수정하지 않고 `outputs/reach_reward_2026-11-14/`에 `plot_goal_rewards.py`, `goal_reward_comparison.png`·PDF·SVG, 거리 sweep·이동 이력 CSV를 추가했다. 기존 사용자 변경과 학습 로그는 보존했다.

## 표현 범위

Prof-v2는 현재 접촉·EEF 높이 조건을 충족한 경우를 가정했다. 실제 정책 스텝 지급량은 다음과 같으며 두 항의 내부 시간 간격 나눗셈과 RewardManager 곱셈은 상쇄된다.

```math
R_t^{\mathrm{Prof}}=120\max(d_{t-1}-d_t,0)
```

```math
R_t^{\mathrm{Finger}}=100\max(m_{t-1}-d_t,0),\qquad m_{t-1}=\min(d_0,\ldots,d_{t-1})
```

왼쪽 패널은 직전 거리 0.10 m·이전 최단 거리 0.08 m를 고정하여 현재 XY 거리를 가로축으로 표시한다. 오른쪽은 같은 예시 궤적 10→8→10→8→6 cm의 실제 스텝 보상을 비교한다. 초기 root 거리에 따른 Reach 보상과 별개의 그래프이며 후퇴·방향·접촉 등 다른 항의 보상·비용은 제외했다.

## 검증·최종 대조

- Matplotlib 실행과 수치 assertion으로 Prof 보상 2.4·0·2.4·2.4, Finger 보상 2·0·0·2를 확인했다.
- 원본 Times New Roman을 적용했다. PDF의 regular·italic Times New Roman 임베드를 `pdffonts`로 확인했다.
- PNG 시각 검토에서 패널 주석과 수식 caption의 겹침을 발견하여 주석을 위로 이동한 뒤 다시 렌더링·확인했다.
- Markdown 수식·문서 링크·공백 검사를 실행했다. GPU·학습은 수행하지 않았다. 예시 궤적은 학습 데이터나 실험 관측이 아니다.

## 재현

```bash
MPLCONFIGDIR=/tmp/reach-mplconfig /home/min/miniconda3/envs/env_isaaclab/bin/python outputs/reach_reward_2026-11-14/plot_goal_rewards.py --font-dir /tmp/reach-times-fonts
```

원본 폰트의 임시 경로와 복구 조건은 [Reach 그래프 기록](2026-11-14_reach_reward_plot.md)을 따른다.
