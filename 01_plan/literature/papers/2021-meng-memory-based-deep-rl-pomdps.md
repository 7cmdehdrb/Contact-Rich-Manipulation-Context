# Memory-based Deep Reinforcement Learning for POMDPs — 원문 정독 노트

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [전체 논문](README.md) · [사용자 발굴 원래 항목: USER-P004](../reviews/user-found-papers.md#user-p004)

**정리일: 2026-10-08 · 분류: 사용자 발굴 논문 USER-P004 · 사용자 내용 확인: 미확인**

## 1. 서지·확인 버전·읽은 범위

| 항목 | 확인 내용 |
| --- | --- |
| 제목 | *Memory-based Deep Reinforcement Learning for POMDPs* |
| 저자 | Lingheng Meng, Rob Gorbet, Dana Kulić |
| 게재 | 2021 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS 2021). 첨부 첫 페이지의 게재 승인 문구와 [저자 publication page](https://linghengmeng.github.io/publications/meng-2021-iros/)에서 확인 |
| 정독 버전 | 사용자 제공 2102.12344v5.pdf, arXiv:2102.12344v5, 2021-09-13. IEEE 출판본과 동일한 편집본이라고 가정하지 않음 |
| DOI·출판본 페이지 | 이번 정독에서는 미확인. 첨부 arXiv 버전과 저자 게재 안내의 정보만 기록 |
| 원문 | [arXiv v5](https://arxiv.org/abs/2102.12344v5) · [v5 PDF](https://arxiv.org/pdf/2102.12344v5) |
| 저자 공개 구현 | [LinghengMeng/LSTM-TD3](https://github.com/LinghengMeng/LSTM-TD3). 논문에 명시된 구현 위치이며 이번 작업에서 코드 검증·실행·재학습은 수행하지 않음 |
| 정독 범위 | PDF 15쪽 전체: 본문·참고문헌 pp. 1–8, Supplementary Material pp. 1–7에 해당하는 PDF pp. 9–15. 핵심 구조도·하이퍼파라미터·결과 표는 렌더링과 추출 텍스트를 대조 |
| SHA-256 | 8f49bebbc525a935eb919c42cf49773a8f0c62a64e0f283a3d5ef2665d503386 |

이하 **본문 p. n은 PDF p. n**, **보충 p. n은 PDF p. n+8**을 뜻한다. 본문과 보충자료에 같은 번호의 Figure/Table이 있으므로 구분해서 표기한다. 아래 Related Work는 이 논문이 설명한 선행연구의 위치를 정리한 것이며, 인용된 모든 선행논문을 별도로 정독했다는 뜻이 아니다.

## 2. 핵심 요약과 분류

이 논문은 **현재 관측만으로 상태를 알기 어려운 연속 제어에서, 과거 관측·행동을 LSTM으로 처리하는 actor와 critic을 TD3로 직접 학습**한다. 현재 입력의 특징을 추출하는 별도 MLP 경로를 두고, 과거의 memory feature와 결합해 행동 또는 Q 값을 출력한다. 6개 PyBullet-Gym 태스크에서 원래 관측과 네 종류의 부분 관측을 비교한다. [본문 §I, §IV–VI; 보충 Table II]

| 확인 질문 | 판정과 근거 |
| --- | --- |
| 논문의 메인이 RL 정책이며 직접 학습하는가? | **예.** LSTM-TD3의 정책·가치함수 구조와 학습, 성능·일반화·ablation이 중심이다 |
| 여러 policy backbone/입력 구조를 비교하는가? | **예, 범위를 명시해야 한다.** Feedforward TD3, 관측을 이어 붙이는 TD3-OW, 관측·행동을 이어 붙이는 TD3-OW-AddPastAct, LSTM-TD3를 비교한다. DDPG·SAC도 포함하지만 이들은 학습 알고리즘까지 달라진다 |
| MLP·LSTM·CNN을 모두 동일 조건으로 비교하는가? | **아니오.** 직접적인 CNN·Transformer backbone 실험은 없다. TD3 대 LSTM-TD3에서도 memory뿐 아니라 현재 특징 분리·fusion 구조가 달라져, 모든 결과를 순수한 backbone 교체 효과로 환원할 수 없다 |
| 학습 전용 privileged information을 활용하는가? | **그런 방법으로 제시되지 않는다.** Actor와 critic 모두 해당 실험 조건의 관측과 이력을 사용한다. Critic에만 원래의 완전 상태를 주는 asymmetric 구성, privileged teacher, 특권 상태 복원용 별도 감독 모듈이 없다 |
| 실물에서 특권 정보 없이 동작함을 검증했는가? | **아니오.** 본 논문의 검증은 시뮬레이션이다. 부분 관측에 대한 강건성을 실물 배포·sim-to-real 성공으로 바꾸어 해석하지 않는다 |

따라서 이 논문은 **RL 정책의 feedforward/stacking/recurrent 구조 비교**에 해당한다. History에서 학습되는 latent memory를 물리 상태의 정답 추정치나 privileged-information adaptation module로 부르지 않는다. [본문 식 (1)–(6), Fig. 1–2, §V]

## 3. 문제 정의와 저자들이 주장하는 Contribution

완전 관측 MDP에서는 현재 입력만으로 의사결정에 필요한 상태를 표현할 수 있다고 가정한다. 실제 센서의 잡음·누락, 관측 설계에서 중요한 변수를 빼놓은 경우에는 같은 현재 관측에서도 필요한 행동이 달라질 수 있다. 저자들은 환경 모델과 명시적 belief-state 추정기를 먼저 설계하지 않고, RL 목적에 유용한 과거 정보를 recurrent network가 추출하게 한다. 이는 정확한 belief distribution 복원이나 POMDP 최적성의 보장이 아니다. [본문 §I–III]

저자들이 내세우는 기여는 다음 세 가지로 정리된다.

1. **연속 제어용 LSTM-TD3:** Actor와 critic에 memory extraction을 넣고 TD3의 가치 과대추정 완화 장치를 결합한다. 저자들은 RDPG의 개선으로 위치시킨다. LSTM과 TD3 자체를 새로 발명했다는 주장은 아니다.
2. **관측 가능성에 따른 비교:** 원래 MDP와 속도 제거·관측 전체 누락·관측 잡음·일부 항목 누락을 비교하여, 부분 관측에서 memory가 도움이 되고 MDP에서도 경쟁력 있는 성능을 유지한다고 주장한다.
3. **구성요소 및 일반화 분석:** Double critics, target policy smoothing, current feature extraction, past actions의 역할과 학습·평가 관측 조건 및 history length 변화의 영향을 살핀다.

기여의 근거는 실험이다. 특히 “모든 POMDP에서 항상 우월” 또는 “각 구성요소가 모든 태스크에서 반드시 최고 수익을 만든다”는 결론은 보충 표의 예외와 맞지 않는다. 해당 범위는 §9–10에서 별도로 대조한다. [본문 §I, §VI–VIII; 보충 §II]

## 4. Related Work — 저자들의 문제 설정

| 계열 | 논문에서 설명하는 방식 | 이 논문이 구분하는 지점 |
| --- | --- | --- |
| Model-based belief-state POMDP 방법 | 과거 행동·관측으로 가능한 상태에 대한 믿음을 추정하고 이를 이용해 정책·가치를 구함 | 저자들은 환경 모델·상태 공간에 대한 지식과 작은 문제 규모에 대한 의존을 동기로 지적 |
| DRQN 및 게임용 recurrent DQN | DRQN은 DQN의 convolution 이후 첫 FC layer를 LSTM으로 교체. 관련 FPS 연구는 보조 게임 특징 학습을 추가 | 주로 과거 관측을 사용하고 discrete action을 다룸 |
| ADRQN | Memory에 과거 행동도 포함 | 행동 이력의 필요성을 뒷받침하지만 discrete control 실험 |
| RDPG | Deterministic policy gradient를 LSTM으로 확장한 continuous control | 앞선 실험의 action dimension이 상대적으로 작고, 후속 bipedal 연구는 한 태스크에 집중했다고 지적 |
| Continuous memory + guided policy search | 관측·행동에 연속 memory state를 확장하여 정책을 학습 | 저자들은 해당 접근의 선형 정책 최적화와 일반화 제약을 지적 |
| TD3 | 두 critic의 작은 target Q를 사용하고 delayed update·target smoothing을 적용 | 이 논문은 recurrent actor–critic에 이를 결합하여 RDPG 계열의 과대추정 문제를 완화하려 함 |

이 표의 선행연구 평가는 **저자들이 본문 §I–III에서 제시한 설명**이다. 이 노트가 각 계열 전체에 대해 새로 검증한 성능 순위는 아니다.

## 5. 수행한 Task와 관측 환경

### 5.1. 태스크·실험 플랫폼

PyBullet-Gym은 OpenAI Gym MuJoCo 계열 태스크를 BulletPhysics에서 구현한 환경으로 소개된다. 논문은 원래 버전을 MDP로 두고 관측 변형을 추가한다. 아래 6개 태스크가 보충 Table II에 포함된다. 본문 Fig. 3의 예시 그림은 이 중 5개이므로, 그림만 보고 전체 태스크 수를 5개로 집계하지 않는다. [본문 §V, Fig. 3; 보충 Table II]

| 환경 | 수행 과업 |
| --- | --- |
| HalfCheetahPyBulletEnv-v0 | HalfCheetah 연속 운동 제어 |
| AntPyBulletEnv-v0 | Ant 다관절 이동 제어 |
| Walker2DPyBulletEnv-v0 | Walker2D 보행 제어 |
| HopperPyBulletEnv-v0 | Hopper 이동·균형 제어 |
| InvertedPendulumPyBulletEnv-v0 | 단일 역진자 균형 유지 |
| InvertedDoublePendulumPyBulletEnv-v0 | 이중 역진자 균형 유지 |

실물 로봇, 카메라 영상 encoder, 손목 6축 F/T, 실제 tactile array를 사용한 실험은 없다. “Sensor missing/noise”는 **환경 observation vector에 적용한 변형**이며 특정 센서의 고장·물리 측정 오차를 실측한 결과가 아니다. 환경별 관측 차원·항목 전체, action 차원·물리 단위·scale, 제어 주기·low-level controller 세부는 첨부 논문에서 미명시다.

### 5.2. 네 가지 POMDP 구성

| 조건 | 원래 관측에 가하는 처리 | 주 비교 설정 | 저자들이 모사하려는 상황 |
| --- | --- | --- | --- |
| MDP | 원래 관측 그대로 사용 | — | 완전 관측 기준 |
| POMDP-RV | 모든 velocity-related observation entry 제거 | — | 중요한 상태 변수가 빠진 관측 설계 |
| POMDP-FLK | 한 시점의 **관측 벡터 전체**를 확률적으로 0으로 설정 | $p_{\mathrm{flk}}=0.2$ | 전송 중 전체 센서 정보 손실 |
| POMDP-RN | 관측의 각 entry에 Gaussian noise 추가 | $\sigma_{\mathrm{rn}}=0.1$ | 센서 잡음 |
| POMDP-RSM | 각 observation entry를 확률적으로 0으로 설정 | $p_{\mathrm{rsm}}=0.1$ | 일부 센서 항목 손실 |

원문의 RN 표기는 $\epsilon\sim\mathcal{N}(0,\sigma_{\mathrm{rn}})$다. 분산·표준편차 표기 관례를 이 노트에서 임의로 바꾸지 않는다. RV는 입력 차원 자체가 달라지고, FLK/RN/RSM은 차원을 유지한다. 0으로 대체된 항목에 별도의 missing mask를 추가하는 설계는 설명하지 않는다. 이 실험을 질량·마찰 등 dynamics domain randomization으로 분류하지 않는다. [본문 Table I, §V, PDF pp. 3–4]

## 6. Main Method — 입력에서 행동까지

### 6.1. 현재 입력과 과거 이력을 분리

시점 $t$의 입력은 현재 관측 $o_t$와, 현재 시점 이전의 observation–action pair를 모은 길이 $l$의 history $h_t^l$이다.

```math
h_t^l=(o_{t-l},a_{t-l},\ldots,o_{t-1},a_{t-1}).
```

이는 본문 식 (1)의 정상 history 구간을 풀어 쓴 것이다. $h_t^l$은 **입력 시퀀스**를 뜻하며 LSTM 내부 hidden state의 기호가 아니다. 논문은 history를 사용하지 않는 경우 관측·행동과 같은 차원의 zero-valued dummy vector를 넣는다. Algorithm 1은 episode 종료 후 환경과 history를 reset한다. 초기 시점에 $t<l$인 경우의 정확한 padding·길이 처리, 학습용 hidden-state 초기화와 burn-in 구현 세부는 식·의사코드만으로 완전히 명시되지 않는다. [본문 식 (1), Algorithm 1]

### 6.2. 세 경로의 순서

| 단계 | Actor | Critic |
| --- | --- | --- |
| 1. Memory extraction, ME | 과거 각 시점의 관측·행동을 결합해 FC와 LSTM으로 처리 | 같은 종류의 history를 critic 자신의 FC와 LSTM으로 처리 |
| 2. Current feature extraction, CFE | 현재 $o_t$를 별도 FC로 변환 | 현재 $(o_t,a_t)$를 결합한 뒤 별도 FC로 변환 |
| 3. Perception integration, PI | ME와 CFE 출력을 concatenate하고 FC 층들을 통과 | Critic의 ME와 CFE 출력을 concatenate하고 FC 층들을 통과 |
| 4. 출력 | 연속 행동 $\mu(o_t,h_t^l)$ | 행동가치 $Q_j(o_t,a_t,h_t^l)$ |

Fig. 1–2는 FC의 ReLU, actor 말단의 tanh, critic 말단의 linear activation을 구분한다. 보충 Table I의 LSTM-TD3 구조는 actor·critic 모두 **ME: [128]+[128], CFE: [128], PI: [128,128]**로 기록되며, ME는 FC와 LSTM 순서다. Baseline actor·critic은 **[256,256]**이다. 저자들은 TD3와 파라미터 수가 비슷하도록 골랐다고 쓰지만, 정확히 같은 파라미터 수나 같은 실행 시간으로 통제했다고 보고하지 않는다. [본문 Fig. 1–2, §V; 보충 §I, Table I]

원문 식 (2)–(3)의 구체적인 계산 흐름을 다음처럼 다시 쓸 수 있다. $\mathrm{concat}$은 두 특징 벡터를 이어 붙이는 연산이다.

```math
\mu(o_t,h_t^l)=
\mu^{\mathrm{pi}}\left(
\mathrm{concat}\left[\mu^{\mathrm{me}}(h_t^l),\mu^{\mathrm{cf}}(o_t)\right]\right).
```

```math
Q_j(o_t,a_t,h_t^l)=
Q_j^{\mathrm{pi}}\left(
\mathrm{concat}\left[Q_j^{\mathrm{me}}(h_t^l),Q_j^{\mathrm{cf}}(o_t,a_t)\right]\right).
```

현재 관측을 과거 시퀀스와 함께 한 경로에만 넣는 대신, **현재 관측의 특징을 직접 전달하는 경로**를 둔 것이 핵심이다. 저자들은 현재와 과거를 구분하고 불필요한 memory 정보의 간섭을 줄이려는 설계라고 설명한다. Actor와 critic의 memory component는 공유하지 않으며, 각각 정책과 가치 예측에 필요한 표현을 학습할 수 있다. [본문 §IV-A, §VII-B; 보충 §II-E]

### 6.3. Action과 실행 순서

Algorithm 1을 따라 학습 중 한 interaction을 정리하면 다음과 같다.

1. 현재 관측 $o_t$와 history $h_t^l$로 actor의 연속 행동을 계산한다.
2. 데이터 수집 중에는 actor output에 Gaussian exploration noise를 더한다.
3. 행동을 환경의 step에 전달하고 $o_{t+1},r_t,d_t$를 받는다.
4. Transition $(o_t,a_t,r_t,o_{t+1},d_t)$를 replay buffer에 저장한다.
5. Episode가 끝나면 환경·history를 reset한다. 그렇지 않으면 history에서 가장 오래된 pair를 빼고 $(o_t,a_t)$를 추가한다.
6. Replay에서 transition과 대응 history를 묶어 뽑아 critic과 actor를 업데이트한다.

평가·행동 선택에 필요한 것은 actor와 입력 history다. Critic, target network, replay buffer는 학습에 쓰인다. **학습 시 privileged input을 받은 actor를 별도 추정기로 대체하는 단계가 없다.** Actor 출력의 실제 actuator별 변환, action-limit clipping 및 환경 termination/time-limit 구분은 논문의 의사코드에서 상세히 풀어 쓰지 않는다. [본문 §IV, Algorithm 1]

## 7. 학습 신호 — TD target·critic loss·actor objective

### 7.1. Critic target과 손실

다음 식은 본문 식 (4)–(5)의 변수 의존성을 명시한 재표기다. $Q_j^{-}$와 $\mu^{-}$는 target network, $d_t$는 terminal flag, $\gamma$는 discount factor다.

```math
\widetilde{a}_{t+1}=\mu^{-}(o_{t+1},h_{t+1}^l)+\epsilon,\qquad
\epsilon\sim\mathrm{clip}\left(\mathcal{N}(0,\sigma),-c,c\right).
```

```math
y_t=r_t+\gamma(1-d_t)
\min_{j\in\{1,2\}}Q_j^{-}(o_{t+1},\widetilde{a}_{t+1},h_{t+1}^l).
```

```math
\mathcal{L}_{Q_j}=
\mathbb{E}_{\mathcal{B}}\left[
\left(Q_j(o_t,a_t,h_t^l)-y_t\right)^2\right].
```

$\mathcal{B}$는 replay에서 뽑은 mini-batch다. 다음 시점의 history는 현재 pair를 추가한 sliding window다. 두 target critic의 작은 값을 사용해 낙관적인 가치 추정의 영향을 줄이며, target action 주변에 제한된 잡음을 넣는 target policy smoothing으로 매우 좁은 행동 영역의 잘못된 높은 Q에 의존하는 현상을 완화한다. $d_t=1$이면 bootstrap 항은 사라진다. 이 target은 **원래의 숨은 상태 정답 없이 관측·history·reward로 계산**한다.

여기서 $\epsilon$은 TD target 계산용 잡음이다. 실제 경험 수집에 추가하는 exploration noise와 역할·설정이 다르다. 원문 식 (5)는 noise의 clip을 쓰지만 최종 action을 환경의 유효 범위로 clip하는 식까지 제시하지 않는다.

### 7.2. Actor와 memory의 학습

본문 식 (6)을 Fig. 2의 $Q_1$ 선택에 맞춰 쓰면 다음과 같다.

```math
\max_{\theta^\mu}\;
\mathbb{E}_{\mathcal{B}}\left[
Q_1\left(o_t,\mu_{\theta^\mu}(o_t,h_t^l),h_t^l\right)\right].
```

이 단계에서는 critic의 파라미터를 고정하고, actor가 출력한 행동에 대한 Q의 gradient를 actor로 전달한다. Actor의 PI뿐 아니라 CFE·ME도 정책 목적에 맞게 함께 학습된다. 본문은 두 critic 중 하나를 사용할 수 있다고 설명하고 Fig. 2는 $Q_1$을 사용한다.

따라서 memory는 **state reconstruction label이나 supervised estimation loss로 학습되지 않는다.** Critic memory는 TD loss, actor memory는 Q를 높이는 policy objective의 영향을 받는다. 별도 auxiliary reconstruction·contrastive loss, teacher imitation, adaptation loss는 제시하지 않는다. [본문 §IV-B, 식 (4)–(6), Fig. 2]

### 7.3. Reward·학습 입력의 경계

논문은 환경이 반환한 reward를 사용하지만 **6개 태스크의 reward 구성식·가중치·성공 threshold를 열거하지 않는다.** 위의 critic loss와 actor objective는 학습 최적화 식이지 환경 reward의 정의가 아니다. Reward 계산에 환경 내부 상태가 필요할 수 있다는 사실과, 그 상태를 actor/critic 입력으로 제공하는 것은 구분해야 한다. 첨부 원문은 privileged critic·teacher를 사용한다고 기술하지 않는다.

원문이 명시한 주요 설정은 다음과 같다. [보충 §I, Table I]

| 설정 | 값 |
| --- | --- |
| Discount $\gamma$ / batch size | 0.99 / 100 |
| Replay buffer size | $10^6$ |
| Random start steps / update-after steps | 10,000 / 1,000 |
| Optimizer / actor·critic learning rate | Adam / 각각 $10^{-3}$ |
| Target network update rate $\tau$ | 0.005 |
| LSTM-TD3 exploration noise | 0.1 |
| Target actor noise / noise clip boundary | 0.2 / 0.5 |
| TD3·LSTM-TD3 policy update delay | 2 |
| 주 history length 비교 | 0, 1, 3, 5; 대표 제안 모델은 $l=5$ |
| 일반 비교 곡선 | 최대 $10^6$ environment steps |

Algorithm 1은 actor·target update의 delay 조건을 생략한 간략 의사코드이며, 실제 설정값은 보충 Table I의 delay 2를 함께 읽어야 한다. 긴 history $l=10,50,100$ 실험은 추가 계산 비용 때문에 $10^6$ step까지 모두 실행하지 않았다고 보충 Fig. 3 caption이 명시한다. 이를 동일 훈련량 비교로 집계하지 않는다.

## 8. Baseline과 비교가 실제로 바꾸는 것

| 비교군 | 정책 입력·처리 | 확인하려는 차이 |
| --- | --- | --- |
| DDPG, TD3, SAC | 현재 관측을 feedforward network에 제공 | Memory 없는 DRL 기준. 알고리즘도 서로 다름 |
| TD3-OW | 현재 관측과 history window의 과거 관측을 concatenate | 학습되는 recurrent memory 없이 관측 stacking만으로 충분한가 |
| TD3-OW-AddPastAct | 현재 관측에 과거 관측·행동을 concatenate | 단순 stacking에도 과거 행동을 추가하면 도움이 되는가 |
| LSTM-TD3(0/1/3/5) | 현재 특징과 LSTM history feature를 별도 처리·결합 | Recurrent 구성과 history 길이의 효과 |
| Full−PA | LSTM-TD3 history에서 과거 행동만 제거 | Recurrent memory에서 action history가 기여하는가 |

TD3-OW는 CNN temporal encoder가 아니다. LSTM-TD3(0)도 ME branch 자체를 제거한 모델이 아니다. Zero-valued dummy history를 넣더라도 가중치·bias와 gradient 때문에 memory output이 0이라고 보장되지 않아 표준 TD3와 동일한 baseline으로 볼 수 없다. [본문 §V, §VI-A]

본문은 TD3-OW에 과거 행동을 단순 추가할 때 성능이 낮아질 수 있는 반면, LSTM history에는 도움이 된다고 설명한다. 즉, “정보를 더 넣는가”뿐 아니라 **그 정보를 어떤 구조로 처리하는가**가 실험 변수다. 현재 특징 경로도 동시에 다르므로 정확한 파라미터·구조 통제 없이 LSTM layer만의 인과 효과라고 과장하지 않는다. [본문 §VI-A, §VII-C]

## 9. 실험 결과와 해석 범위

### 9.1. Metric·반복 수

저자들은 **4개 random seed를 바탕으로 10 evaluation episode의 return을 평균**한다고 설명한다. 학습 곡선은 비교를 쉽게 하기 위해 평균만 표시한다. 보충 Table II는 **Maximum Average Return**을 보고하고 ±를 1 standard deviation이라고 정의한다. 따라서 아래 수치는 최종 checkpoint의 return이나 성공률이 아니다. Seed별 최대값을 취한 후 평균하는지, 평균 곡선의 최대 시점에서 집계하는지 등 세부 집계 순서는 caption만으로 완전히 설명되지 않는다. 유의성 검정·신뢰구간도 별도로 보고하지 않는다. [본문 §V, Fig. 4 caption; 보충 Table II]

### 9.2. 대표 결과 — 이득과 예외를 함께 기록

다음은 보충 Table II의 수치를 그대로 발췌한 것이다. FLK/RN/RSM 설정은 §5.2와 같고, LSTM은 history length 5다. 서로 다른 태스크의 return 절댓값을 직접 성능 순위로 비교하지 않는다.

| 태스크·조건 | TD3 | TD3-OW | LSTM-TD3(5) | 읽을 수 있는 결과 |
| --- | --- | --- | --- | --- |
| Ant · MDP | 2433.5 ± 288.5 | 2289.5 ± 154.8 | 2574.9 ± 79.0 | MDP에서도 경쟁력 있는 예 |
| Ant · FLK | 654.4 ± 1.6 | 1390.5 ± 736.6 | 2036.7 ± 73.5 | 전체 관측 누락에서 recurrent 방식의 높은 수익 |
| Hopper · FLK | 401.1 ± 39.8 | 1353.0 ± 467.8 | 2264.6 ± 72.3 | 관측 stacking 대비로도 개선 |
| Hopper · RN | 644.2 ± 46.5 | 962.0 ± 10.5 | 1635.8 ± 180.7 | 관측 잡음 조건의 개선 |
| InvertedDoublePendulum · RV | 953.6 ± 92.0 | 7998.1 ± 653.7 | 9358.9 ± 0.3 | 속도 제거에서 history의 큰 효과 |
| HalfCheetah · MDP | 1311.9 ± 49.7 | 1265.5 ± 8.9 | 1223.0 ± 582.3 | LSTM이 최고가 아니며 변동도 큼 |
| HalfCheetah · RV | 1151.7 ± 74.9 | 1161.3 ± 17.2 | 918.4 ± 44.0 | 본문도 인정하는 성능 저하 |
| HalfCheetah · FLK | 82.4 ± 45.7 | 1559.61 ± 559.9 | 848.1 ± 60.2 | LSTM은 TD3보다 높지만 **stacking보다 낮음** |
| InvertedPendulum · RN | 342.8 ± 46.8 | 1000.0 ± 0.0 | 752.6 ± 428.5 | Stacking이 더 높은 또 다른 예 |

이득은 특히 관측 누락·잡음으로 현재 입력만의 정보가 부족한 조건에서 나타난다. 다만 본문 §VI-A의 포괄적인 우월성 서술과 보충 표의 **maximum metric**을 동일한 주장으로 읽어서는 안 된다. 여러 조건에서 TD3-OW나 다른 baseline이 더 높거나 비슷하다. 표의 ±만으로 통계적 유의성을 판단할 수도 없다.

### 9.3. 관측 조건을 바꾼 일반화

본문 Fig. 5는 Ant에서 MDP·FLK·RN·RSM 중 한 조건으로 학습하고 다른 조건에서 평가한다. RV는 관측 차원이 달라 제외한다. 저자들은 MDP 학습 후 관측이 나빠지면 TD3·TD3-OW·LSTM-TD3 모두 저하되지만 LSTM-TD3가 상대적으로 강건하며, FLK로 학습한 정책은 MDP 평가에서 더 높은 성능을 낼 수 있다고 보고한다. [본문 §VI-B, PDF p. 6]

이는 **같은 태스크의 관측 변형 사이 전이**다. 다른 로봇·새 물리 dynamics·새 과업으로의 전이, 실제 센서 고장 복구 또는 real-robot generalization을 평가한 것은 아니다.

### 9.4. 관측 가능성과 history 길이

보충자료는 Ant의 RN·RSM 강도를 높이며 성능 저하를 조사한다. FLK 확률 0.05에서는 history 3·5가 0·1보다 좋고, 0.1에서는 5가 3보다 유리하다. 0.2에서 history 5의 성능도 낮아지며, **0.5·0.8에서는 조사한 길이 모두 태스크에 실패**한다고 저자들이 설명한다. 긴 memory가 심한 정보 손실을 항상 보상하지는 못한다. [보충 §II-B–C, Fig. 1–3, PDF pp. 9–11]

또한 학습 history length와 다른 길이로 평가한다. 조사한 범위에서는 평가 history를 늘릴 때 성능이 유지되는 경향이 있지만, 줄일 때에는 크게 떨어지는 경우와 유지되는 경우가 섞인다. 저자들은 이 분석의 최대 학습 길이가 5임을 명시한다. 이는 길이 변경에 대한 관찰이지 자동으로 최적 길이를 선택하는 알고리즘의 검증이 아니다. [보충 §II-D, Fig. 5, PDF pp. 11–13]

## 10. Ablation — 메소드의 어느 부분을 검증하는가

| 조건 | 제거·교체한 내용 | 저자들의 해석 |
| --- | --- | --- |
| Full−DC | Double critics 제거 | 가치 추정·학습 안정성에 중요한 요소 |
| Full−TPS | Target policy smoothing 제거 | DC보다 최고 성능에 대한 영향이 작지만 안정화에 기여 |
| Full−DC−TPS | DC와 TPS 모두 제거 | 저자들이 LSTM-DDPG, 즉 RDPG와 유사한 형태로 부르는 비교. TD3 장치의 기여 평가 |
| Full−CFE | 현재 특징 추출기를 없애고 raw 현재 관측, critic에는 현재 행동도 memory feature에 직접 결합 | 현재 특징을 별도로 처리하는 경로가 특히 MDP 성능 유지에 중요 |
| Full−PA | Memory 입력에서 과거 행동 제외 | 현재 상태를 이해하는 데 과거 행동이 필요한 태스크에서 기여 |

[본문 §VII, Fig. 6–7; 보충 §II-F, Table III, Fig. 7]

구체적으로 보충 Table III의 Ant–MDP는 Full **2574.9 ± 79.0**, Full−CFE **1510.8 ± 421.4**다. InvertedDoublePendulum–RV는 Full **9358.9 ± 0.3**, Full−PA **5568.0 ± 4941.9**로, CFE와 action history에 대한 저자들의 설명을 뒷받침하는 예다.

반대로 HalfCheetah–MDP에서는 Full **1223.0 ± 582.3**보다 Full−PA **1469.6 ± 637.5**의 maximum average return이 높다. Ant–RSM에서도 Full **1324.9 ± 313.6**보다 Full−PA **1817.6 ± 66.4**가 높다. 따라서 **“모든 구성요소가 모든 조건에서 수치적으로 우월하다”는 결론은 피한다.** Learning curve의 안정성에 대한 주장과 maximum return 표의 순위는 다른 관점이다.

Full−CFE는 현재 관측을 제거한 ablation이 아니다. Raw 현재 입력은 여전히 전달된다. Full−PA도 현재 critic action을 제거한 조건이 아니라 **과거 action sequence**를 제거한 조건이다.

## 11. 저자들이 밝힌 Limitation

독립적인 Limitations 절은 없지만 본문 결론과 보충자료가 다음 제약을 명시한다. 아래는 정리자의 추가 비판과 구분한 저자 서술이다.

| 한계 | 저자 서술의 요지 | 근거 |
| --- | --- | --- |
| Memory 해석의 어려움 | 학습된 memory가 어떤 숨은 상태를 의미하는지 알기 어렵다. 해석을 돕는 목적·제약이 없는 현재 loss만으로 의미를 부여하기 어렵다고 설명 | 본문 §VIII, PDF pp. 7–8; 보충 §II-E, PDF p. 12 |
| 고정 history length | $l=5$가 제시한 태스크에는 효과적이어도 더 오래된 정보에 의존하는 태스크에서 충분하다는 보장이 없음 | 본문 §VIII, PDF p. 8 |
| 긴 history의 계산 비용 | 학습·추론 시간과 자원이 증가. 10·50·100 history 실험을 모두 동일한 100만 step까지 실행하지 못함 | 본문 §VIII; 보충 Fig. 3 caption, PDF p. 11 |
| 심한 관측 손실 | 작은 관측 저하는 견디지만 손실이 커지면 LSTM-TD3도 저하. Ant의 높은 FLK 확률에서 시험한 길이 모두 실패 | 보충 §II-B–C, PDF pp. 9–10 |
| Velocity 제거에서 제한적인 이득 | HalfCheetah·Ant에서 memory의 효과가 작거나 저하될 수 있음을 논의. 높은 sampling rate와 짧은 구간에서 속도 변화가 작다는 설명은 저자들의 가설 | 본문 §VI-A, PDF pp. 4–6 |
| 평가 history 길이 일반화의 범위 | 더 짧은 evaluation history는 성능을 보장하지 못하며, 해당 분석의 최대 training history는 5 | 보충 §II-D, PDF p. 12 |

LSTM-TD3(0)의 zero dummy 입력에서도 비영 memory와 seed 민감도가 생길 수 있다는 설명 역시 본문 §VI-A에 있다. 보충 §II-D–E는 actor memory 평균이 0 근처라는 관찰만으로 “과거를 무시한다”는 의미를 확정할 수 없다고 주의를 둔다.

## 12. 저자들이 제시한 Future Work

다음은 구현·검증 완료가 아닌 향후 연구 제안이다. [본문 §VIII, PDF p. 8; 보충 §II-D–E, PDF p. 12]

1. **해석 가능한 memory:** Cost function에 적절한 제약을 넣어 memory 의미를 해석하고 관측 설계 이해에 활용하는 방향.
2. **동적인 history length 적응:** 성능과 학습·의사결정 시간을 함께 고려하여 길이를 조정하는 방법.
3. **더 오래된 정보가 필요한 POMDP 평가:** 현재의 짧은 history benchmark를 넘어선 복잡한 태스크 검증.
4. **SAC와 LSTM의 결합:** 다른 off-policy 알고리즘으로 확장.
5. **CFE를 분리한 TD3-OW 비교:** LSTM-TD3의 이득 중 별도 현재 특징 경로의 역할을 더 분리해서 평가.
6. **더 긴 training history의 일반화 분석:** 최대 길이 5인 학습·평가 길이 교차 실험을 넓혀 추가 통찰을 얻는 방향.

저자들은 이 논문에서 새 실물 로봇 배포 계획이나 구체적인 센서 제품·배치 계획을 제시하지 않는다.

## 13. 정리자가 구분한 미명시 사항·표기 주의

이 절은 저자들의 Limitation 목록과 별개의 원문 확인 기록이다.

| 항목 | 확인 결과와 해석 제한 |
| --- | --- |
| 물리 reward·관측·action 명세 | 환경별 전체 벡터 항목·차원, reward 항·가중치, 물리 action scale, controller frequency 미명시. 공개 환경의 일반 관행으로 채워 넣지 않음 |
| Privileged information | 수식상 actor·critic 모두 관측/history를 사용. 학습 전용 완전 상태 입력이나 이를 복원하는 모듈이 없는 만큼, privileged-information 기법의 성공 사례로 분류하지 않음 |
| 순수 backbone 비교 | Memory/CFE/PI 구조가 함께 바뀌고 파라미터 수는 “비슷하게” 선택. 동일 용량의 MLP·LSTM·CNN을 통제한 비교는 아님 |
| History 초기화 | 식 (1)은 $l,t\geq1$에서 과거 $l$개 pair를 쓰지만 $t<l$의 구체적인 padding 구현과 recurrent hidden-state 초기화/burn-in을 충분히 적지 않음 |
| Algorithm 1의 생략 | Actor·target update의 delay 조건이 의사코드에 없지만 보충 Table I에는 delay 2가 있음. 의사코드 한 줄만으로 매 step actor update라고 단정하지 않음 |
| 함수 합성 표기 | 식 (2)–(3)의 첫 줄 합성 기호보다 둘째 줄의 “ME와 CFE를 병렬 계산한 뒤 concatenate→PI” 및 Fig. 1–2를 기준으로 정보 흐름을 설명 |
| Maximum return 집계 | 보충 Table II·III는 최종 return이 아닌 maximum average return. Seed·episode·checkpoint의 정확한 집계 순서를 추가로 추정하지 않음 |
| Table II·III의 미세 불일치 | InvertedDoublePendulum–MDP의 Full은 보충 Table II에서 9359.77 ± 0.1, Table III에서 9359.73 ± 0.1. 하나로 임의 통일하지 않음 |
| 보충자료의 내부 참조 오류 | 보충 §II-D에는 dummy history 정의를 가리키는 “Eq. ??”가 남아 있음. 본문 식 (1)과 대조하되 원문이 수정되어 있다고 쓰지 않음 |
| Overestimation 해석 | 보충 §II-E는 평균 return과 예측 Q의 추세가 비슷하다는 관찰로 과대추정 문제가 없다고 해석. 이 노트는 이를 별도의 정확한 Q 오차 측정이나 일반적 부재 증명으로 확대하지 않음 |
| 검증 범위 | Simulation의 관측 교란 실험. 실물 센서 보정, sim-to-real, 새로운 물리 분포의 일반화 및 실제 제어 지연 측정은 보고하지 않음 |

이 노트는 논문 자체의 방법과 근거를 정리하며 프로젝트의 확정 설계·구현 상태를 변경하지 않는다.

## 14. 원문 근거 위치와 확인 상태

| 확인 내용 | 원문 위치 |
| --- | --- |
| 연구 동기·기여·Related Work | 본문 §I–II, PDF pp. 1–2 |
| MDP/POMDP·TD3 배경 | 본문 §III, PDF p. 2 |
| Architecture·history·loss·target·actor objective | 본문 §IV, Fig. 1–2, 식 (1)–(6), PDF pp. 1–3 |
| Interaction·replay·reset 순서 | 본문 Algorithm 1, PDF p. 4 |
| 환경·관측 변형·baseline·평가 반복 | 본문 §V, Table I, Fig. 3, PDF pp. 3–4 |
| 주 결과·관측 조건 교차 평가 | 본문 §VI, Fig. 4–5, PDF pp. 4–6 |
| DC/TPS/CFE/PA ablation | 본문 §VII, Fig. 6–7, Table II, PDF pp. 6–7 |
| 저자 한계·향후 연구 | 본문 §VIII, PDF pp. 7–8 |
| 구조 크기·학습 hyperparameter | 보충 §I, Table I, PDF p. 9 |
| 전체 6개 태스크의 maximum return·관측 손실 강도 | 보충 Table II, Fig. 1–2, PDF p. 10 |
| 긴 history의 계산 비용·추가 learning curve | 보충 Fig. 3–4, PDF p. 11 |
| 학습/평가 history 길이·memory 해석 | 보충 §II-D–E, Fig. 5–6, PDF pp. 11–14 |
| 전체 ablation 표와 추가 곡선 | 보충 Table III, Fig. 7, PDF pp. 13, 15 |

**확인 상태:** 첨부 v5 본문·보충자료 정독 및 상세 리뷰 작성 완료. 코드 정독·실행, 정책 재학습, 실험 재현은 미수행. 사용자에게 리뷰 내용 확인을 받은 상태는 아니며, 저장소 반영 승인은 내용 확인과 구분한다.

**문서 검사:** 변경 Markdown 5개를 대상으로 저장소 수식 검사기와 diff 공백 검사를 수행하고, 상대 링크·anchor 및 USER-P004 양방향 연결을 확인했다. 원문 PDF 구조도·표의 렌더링 대조와 GitHub Markdown의 웹 렌더링은 별개이며, 후자의 실제 브라우저 표시는 이번 작업에서 확인하지 않았다.
