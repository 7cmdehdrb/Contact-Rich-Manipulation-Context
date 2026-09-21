# RL 논문의 Reward Formulation 비교

[문서 안내](../../README.md) · [문헌 색인](../README.md) · [조사 그룹](README.md) · [전체 논문](../papers/README.md)

기준일: **2026-09-21**. 대상 스냅샷: `77adb1e8d3932d55d44ca78e0d19460a953639d4`의 `docs/literature/papers/` 상세 노트 **28편**. 이 중 **RL 학습과 보상 구성요소가 모두 기록된 18편**을 모았다. 나머지 **10편**은 [제외 목록](#excluded)에 사유를 남겼다. 동일 논문이 여러 조사 그룹에 등록되어도 한 편으로 계산한다.

목적은 **각 논문이 무엇을, 어떤 함수와 가중치로, 언제 보상했는지 한곳에서 비교하는 것**이다. 새 논문의 원문 정독이나 본 연구의 reward 제안서가 아니다. 기존 노트에서 보상과 직접 관련된 내용만 재구성했으며, 원문 PDF·보충자료·코드를 이번 작업에서 다시 검증하지 않았다. `review_dataset/`만의 논문과 기존 노트에 없는 외부 연구는 추가하지 않았다.

## 1. 읽는 기준

**수식 제시**는 기존 노트에 해당 식이 전재되어 있다는 뜻이지 전체 구현이 재현 가능하다는 뜻은 아니다. **부분 제시**는 일부 식과 항의 역할이 기록되어 있고, **구조 제시**는 구성요소·조건을 알지만 완전한 계산식은 기록되지 않은 경우다. 원문에 없다고 노트가 명시한 정보와, 단순히 노트에 옮겨 적지 않은 정보를 구분한다.

번호가 있는 원문 식은 그 번호를 표시한다. 문장 설명을 수식화한 경우는 **해설식**이라고 표시한다. 다른 논문의 식·계수로 빈칸을 채우지 않는다. 논문마다 같은 기호가 다른 의미이므로 각 절의 정의를 독립적으로 읽는다.

Task reward, PPO/SAC의 최적화 목적, 표현학습 loss, constrained-RL의 constraint, 별도 controller·fail-safe, 성공 판정은 서로 다르다. 아래에는 **보상 해석에 필요한 경계만** 함께 기록한다. 배포 actor가 볼 수 없는 물체 정답을 학습 reward에서 사용하는 경우도 구분한다.

<a id="overview"></a>

## 2. 전체 비교표

표의 번호는 이 문서 안의 탐색용 번호이며 기존 R·B·USER-P 식별자를 대체하지 않는다.

| 번호 | 논문 / RL | Reward 설계의 중심 | 정리 수준 |
| --- | --- | --- | --- |
| [01](#rw01) | Yang 2023 · Tactile Pushing / SAC·PETS | 먼 목표에서는 방향, 가까운 목표에서는 거리 + 접촉면 정렬 | 수식 제시 |
| [02](#rw02) | Lin 2023 · Bi-Touch / PPO | 과업별 물체 위치·방향 + 양팔 정렬·접촉 위치 + subgoal | 수식 제시; 가중치 미명시 |
| [03](#rw03) | Dengler 2025 · Location-Based Pushing / PPO | 현재 위치·방향 근접도 + 성공·경계 실패 + 장애물 접촉 penalty | 수식·계수 제시; 정규화 세부 미명시 |
| [04](#rw04) | Dadiotis 2025 · Dynamic Goal Pushing / constrained PPO | OBB pose 오차 + surface 접근 + 이동 방향 + action 변화 | 총합·계수와 항의 구조 제시 |
| [05](#rw05) | Bergmann 2025 · Precision-Focused Pushing / SAC·HER | 1 cm 밖 −1, 안 0; 마지막 step의 정밀도 평가 | 수식 제시 |
| [06](#rw06) | Zhao 2024 · Unknown Object Retrieval / SAC | 이동 진전 + 시간 + 힘 구간 + 도달 + 복구 실패 | 수식·계수·조건 제시 |
| [07](#rw07) | Beltran-Hernandez 2020 · Learning Force Control / SAC | 목표 pose·action·접촉 하중의 정규화 + 시간 + safety 결과 | 총합식 제시; mapping·가중치 미명시 |
| [08](#rw08) | Lee 2024 · DexTouch / PPO | 최고 접근·회전 기록 갱신 + 단계별 실행 + bonus | 과업별 수식 제시; 계수 미명시 |
| [09](#rw09) | Wu 2019 · MAT / Soft PPO | Terminal 파지 성공 + 너무 이른 reopen 억제 | 수식·조건 제시 |
| [10](#rw10) | Ding 2021 · Tactile Sim-to-Real / TD3 | 문 각도 + 접근·방향·파지 + 조건부 활성 촉각 수 | 총합·계수 및 tactile 식 제시 |
| [11](#rw11) | Zhang 2025 · Role of Tactile Sensing / SAC·MPO | 사후 파지 유지시간 비율 + 접촉·접근·힘 shaping | 주 보상식 + auxiliary 구조 제시 |
| [12](#rw12) | Su 2024 · Sim2Real Tactile Manipulation / PPO | 양 손끝 접촉 + 위치·각도 목표 + 행동 제곱 penalty | 부분 제시; 각도식 미명시 |
| [13](#rw13) | Yin 2023 · Rotating without Seeing / PPO | 회전 증분 + 병진·낙하·구동 penalty + 손끝 거리 | 수식·계수 제시 |
| [14](#rw14) | Yuan 2024 · Robot Synesthesia / PPO teacher | 회전 + 거리·속도·구동·추종 오차 + 낙하 | 구조 제시 |
| [15](#rw15) | Chen 2025 · ViViDex / PPO state policy | 사람 영상 reference의 손·물체 궤적 + 접촉 수·lift | 단계별 식과 일부 계수 제시 |
| [16](#rw16) | Liu 2024 · Tactile-AIRL / model-based active inference | 목표 진입·거리 또는 촉각 optical-flow entropy | 과업 보상식 제시 |
| [17](#rw17) | Miller 2025 · Enhancing Tactile RL / PPO | Find 거리, Bounce 재접촉, Baoding 가상 목표 전환 | 과업별 구조 제시 |
| [18](#rw18) | Pan 2026 · Beyond Binary / recurrent PPO | Insertion의 정렬·접촉, balancing의 상대 운동·낙하 | 과업별 구조 제시 |

<a id="rw01"></a>

## 3.01. Yang 2023 — Sim-to-Real Tactile Pushing

**출처:** [상세 노트 §6](../papers/2023-yang-sim-to-real-tactile-pushing.md). 원문 §III-B-3–4, 식 (4), PDF p. 4. Model-free SAC와 model-based PETS의 공통 task reward다.

### Reward 식과 전환 조건

$$
r=\begin{cases}-\bigl(g(o_\theta,g_\theta)+g(p_\theta,o_\theta)\bigr),&\lVert o_{xy}-g_{xy}\rVert>d,\\-\bigl(f(o_{xy},g_{xy})+g(p_\theta,o_\theta)\bigr),&\lVert o_{xy}-g_{xy}\rVert\le d.\end{cases}
$$

$p$는 pusher, $o$는 **물체 접촉면**, $g$는 goal이다. 함수 $f$는 Euclidean distance, 함수 $g(\cdot,\cdot)$는 cosine distance다. 접촉면의 위치를 물체 중심 위치로 바꾸어 읽지 않는다.

| 항·조건 | 설계 의도 |
| --- | --- |
| 목표까지 100 mm 초과 | 접촉면 방향을 목표 bearing에 맞춘다. 이 구간에는 목표 위치까지의 Euclidean distance 항이 직접 들어가지 않는다. |
| 목표까지 100 mm 이하 | 목표 부근에서 부적절해지는 bearing 항을 위치 거리 항으로 교체한다. |
| 두 구간의 공통 정렬 항 | Pusher를 접촉면에 수직으로 유지하여 안정적인 pushing을 유도한다. |

**정규화·계수:** 거리·각도 항의 scale 조정과 cosine distance의 상세 구현은 미명시다. **100 mm는 reward 전환 경계**, **25 mm는 접촉 위치의 목표 도달 허용 오차**다.

접촉 유지에는 고정 전진 action도 관여한다. 정렬 reward만으로 접촉을 보장하는 것이 아니며, 뉴턴 단위 힘 제한이나 전도 penalty가 명시된 식은 아니다.

<a id="rw02"></a>

## 3.02. Lin 2023 — Bi-Touch

**출처:** [상세 노트 §5.3–8](../papers/2023-lin-bi-touch.md). 원문 §III-C, 식 (1)–(4), PDF pp. 3–4. 세 과업 모두 PPO다.

공통 각도 오차는 다음과 같다. 위치 항은 **제곱하지 않은 Euclidean norm**이며 $w_j>0$의 실제 값은 미명시다.

$$
S(\phi,\psi)=1-\cos(\phi-\psi).
$$

### Bi-pushing — 물체 pose와 양팔 접촉 정렬

원문 식 (1):

$$
R_t^{\mathrm{BP}}=-w_1\lVert p_t^g-p_t^o\rVert_2-w_2S(\theta_t^g,\theta_t^o)-w_3\sum_{i=1}^{2}S(\theta_t^{e_i},\theta_t^o).
$$

물체 위치·방향을 경로 목표에 맞추고 두 TCP를 접촉면에 정렬한다. $o$는 물체, $g$는 목표, $e_i$는 각 TCP다. 마지막 항은 **양팔 힘의 균등화가 아니라 방향 정렬**이다.

### Bi-reorienting — 중심을 유지하며 회전

원문 식 (2):

$$
R_t^{\mathrm{BR}}=-w_1\lVert p_0^o-p_t^o\rVert_2-w_2S(\theta^g,\theta_t^o)-w_3\sum_{i=1}^{2}S\left(\theta_t^{e_i},(-1)^i(\pi/2+\theta_t^o)\right)-w_4\sum_{i=1}^{2}\lVert p_{\mathrm{ctrl}_i}^{o}-p_t^{e_i}\rVert_2.
$$

초기 중심 이탈, 목표 각도 오차, TCP 방향 오차, 원하는 접촉 위치와 TCP의 거리라는 네 항이다. $p_{\mathrm{ctrl}_i}^{o}$는 **기하학적으로 지정한 원하는 접촉 위치**이며 측정한 CoP가 아니다. 좌우 각도의 부호는 기존 노트의 원문 표기를 유지했다.

실물에서 과도한 압착이 나타난 뒤 저자들은 **큰 접촉 깊이에 대한 penalty 계수를 강화**했다. 다만 강화한 식·계수·깊이 threshold는 미명시다. 동시에 센서 stiffness·damping 수정, 목표 pose 10 steps 유지, 큰 목표 각도의 sampling 비중 증가도 사용했다. 이 변경들을 모두 추가 reward 항으로 간주하지 않는다.

### Bi-gathering — 물체 간 거리와 중간 목표

원문 식 (3):

$$
R_t^{\mathrm{BG}}=-w_1\lVert p_t^{o_1}-p_t^{o_2}\rVert_2-w_2\sum_{i=1}^{2}S(\theta_t^{e_i},\theta_t^{o_i})-w_3\sum_{i=1}^{2}\lVert p_{\mathrm{ctrl}}^{o_i}-p_t^{e_i}\rVert_2.
$$

물체 간 거리, 접촉 방향, 접촉 위치를 함께 다룬다. GUM은 기존 항을 유지하고 target line의 subgoal 및 방향을 추가한다. 원문 식 (4):

$$
R_t^{\mathrm{BG\text{-}GUM}}=R_t^{\mathrm{BG}}-w_4\sum_{i=1}^{N}\lVert p_t^{g_i}-p_t^{o_i}\rVert_2-w_5\sum_{i=1}^{N}S(\theta_t^{o_i},(-1)^i\theta_t^c).
$$

$\theta_t^c$는 target line 방향과 연결되는 표기다. 합의 $N$은 문맥상 두 물체이며, **후보 subgoal 수 $n=10$과 다르다**. Target line 갱신은 75 steps다. 해당 기호의 상세 정의·구현 공백은 상세 노트 §8.3을 따른다.

저자가 “moving sparse goal”이라고 표현해도 식 (3)에는 이미 연속 거리·각도 항이 있다. GUM은 완전한 무보상 구간에 보상을 처음 넣은 것이 아니라 **중간 목표 구조를 보강**한 것이다.

<a id="rw03"></a>

## 3.03. Dengler 2025 — Location-Based Attention Pushing

**출처:** [상세 노트 §7](../papers/2025-dengler-location-based-attention-pushing.md). 원문 §III-B.3, 식 (1), §IV-A, PDF pp. 3–4. PPO의 task reward다.

$$
r_{\mathrm{total}}=r_{\mathrm{term}}+0.1(1-r_{\mathrm{dist}})+0.02(1-r_{\mathrm{ang}})+r_{\mathrm{coll}}.
$$

| 항 | 정의·값 |
| --- | --- |
| $r_{\mathrm{dist}}$ | 물체–목표 Euclidean distance를 [0,1]로 정규화 |
| $r_{\mathrm{ang}}$ | 물체–목표 angular distance를 [0,1]로 정규화 |
| $r_{\mathrm{term}}$ | 성공 +50, workspace 경계 위반 실패 −10 |
| $r_{\mathrm{coll}}$ | Pusher 또는 대상 물체가 장애물에 접촉한 step −5, 없으면 0 |

Dense 항은 **현재의 근접도**이지 이전 step 대비 진전량이 아니다. 충돌 항은 binary 사건에 대한 penalty이며 힘·충격량에 비례하지 않는다. 정규화 분모·각도 wrap·대칭 처리 등은 미명시다.

학습 time limit에는 bootstrap을 사용하므로 timeout을 일괄 −10으로 처리했다고 적지 않는다. 장애물 접촉 penalty와 접촉 즉시 종료도 같은 규칙이 아니다. 물체 위치·방향과 충돌 상태가 보상 계산에 필요하며, tactile 신호로 계산한 보상으로 분류하지 않는다.

<a id="rw04"></a>

## 3.04. Dadiotis 2025 — Dynamic Object Goal Pushing

**출처:** [상세 노트 §6.2–7](../papers/2025-dadiotis-dynamic-object-goal-pushing.md). 원문 §III-D, Table II, PDF p. 4. PPO에 CAT의 constraint 처리를 결합한다.

총합의 표기를 정리하면 다음과 같다.

$$
r_t^{\mathrm{tot}}=2.5r_{1,t}+1.25r_{2,t}+0.156r_{3,t}+0.3r_{4,t}.
$$

| 항 | 보상 구조 | 추가 조건 |
| --- | --- | --- |
| $r_1$ | 물체·목표의 8개 OBB keypoint 차이를 감소 | 성공하면 $r_1=2$ |
| $r_2$ | EEF를 물체 수직 표면에서 샘플링한 reach target으로 유도 | 1,500 iterations 뒤 가중치를 1/4로 감소; 성공 후 직전 값 유지 |
| $r_3$ | 물체 선속도의 **방향**을 물체→목표 방향에 정렬 | 속력 자체를 크게 보상하지 않음; 성공 후 0 |
| $r_4$ | Base·arm command의 연속 step 간 변화 억제 | Action-rate regularization |

Reach target은 학습용 exploration shaping이며 actor에게 준 별도 목표점이 아니다. Reward는 actor 입력에 없는 object geometry·velocity도 활용한다.

**확인 범위:** 기존 노트에는 각 항의 완전한 함수식이 전재되어 있지 않다. 원문 scale $\sigma_1,\sigma_2,\sigma_3,\sigma_{4,a},\sigma_{4,b}$의 수치는 미명시로 기록되어 있다. 거리 항을 임의의 지수함수나 역수함수로 채우지 않는다.

관절·명령·토크 제한, 원하지 않는 충돌, 물체 balance 등 CAT constraint는 위 네 항과 **별도**다. Constraint의 termination probability curriculum을 임의의 가산 penalty로 바꾸지 않는다.

<a id="rw05"></a>

## 3.05. Bergmann 2025 — Precision-Focused Pushing

**출처:** [상세 노트 §11–12](../papers/2025-bergmann-precision-focused-pushing.md). SAC와 HER를 사용하는 goal-conditioned pushing이다.

$$
r(p_o,p_g)=\begin{cases}-1,&\lVert p_o-p_g\rVert_2\ge0.01\\,\\mathrm{m},\\0,&\text{otherwise}.\end{cases}
$$

$p_o,p_g$는 simulator의 물체·목표 중심이다. Numeric object GT는 actor 관측이 아니라 reward 계산에 사용된다.

**1 cm 밖에서는 얼마나 더 가까워졌는지에 따른 차등 보상이 없다.** 1 cm 안에 있을 때만 −1을 받지 않는 구조다. 별도의 방향 정렬·접촉 유지·힘 penalty는 이 식에 없다.

Episode는 항상 **50 environment steps**이며 조기 목표 도달로 바로 끝나지 않는다. 마지막 step에서 1 cm 미만이어야 성공이므로, 잠깐 도달한 뒤 다시 밀어내는 행동과 구분한다. 이 50 steps는 고정된 물리 시간과 같지 않다. 정책이 action duration도 선택하기 때문이다. HER는 학습 기법이지 추가 물리 보상 항이 아니다.

<a id="rw06"></a>

## 3.06. Zhao 2024 — Unknown Object Retrieval

**출처:** [상세 노트 §10–11](../papers/2024-zhao-unknown-object-retrieval.md). 원문 식 (1)–(3), Table I. 실제 로봇 SAC 학습에서 사용하는 다섯 항이다.

$$
r=r_t+r_o+r_f+r_g+r_p.
$$

| 항 | 식·수치 | 적용 조건 |
| --- | --- | --- |
| 시간 $r_t$ | −0.1 | 매 timestep. Backward primitive는 동일 이동의 equivalent timestep 수에 맞춰 과금 |
| 진전 $r_o$ | $5.0d_o$ | 해당 step에서 물체가 intended retrieval direction으로 이동한 거리 |
| 힘 $r_f$ | 아래 구간식 | 최대 normal tactile force에 따라 결정 |
| 목표 $r_g$ | $2.0d_g$ | Terminal distance $d_g$를 달성했을 때만 발행 |
| 복구 실패 $r_p$ | −10.0 | Backward primitive 뒤 정해진 시간 안에 재접촉하지 못했을 때 |

### Force-regulation 구간식

$$
r_f=\begin{cases}0,&f_n^{\max}<f_n^l,\\r_f^h,&f_n^{\max}>f_n^h,\\(f_n^{\max}-f_n^l)^2,&\text{otherwise},\end{cases}\qquad f_n^l=0.2\\,\\mathrm{N},\quad f_n^h=1.5\\,\\mathrm{N},\quad r_f^h=-10.
$$

약한 접촉에는 보상이 없고, 중간 범위에는 **양의 제곱 항**, 상한 초과에는 penalty를 준다. 중간 항은 특정 목표 힘에 대한 음의 제곱 오차가 아니다. 식상 하한으로부터 힘이 증가하면 중간 구간 보상이 커진다.

상한 초과 시 로봇이 압력을 해제하여 하한까지 낮추는 **별도 실행 규칙**도 사용한다. 따라서 force regulation을 reward만의 효과로 설명하지 않는다.

### 진전 측정과 목표 curriculum

$d_o$는 **OptiTrack이 측정한 실제 물체 진전량**이며 EEF 이동이 아니다. OptiTrack은 actor 입력에 들어가지 않고 학습 reward에만 쓰인다. $d_g$는 20 mm에서 시작하여 성공마다 1 mm 증가하고 최대 50 mm가 된다. 이는 평가의 100 mm 조건과 구분한다.

거리 계수는 기존 노트에 제시된 값을 유지했으며 mm↔m 변환을 임의로 적용하지 않았다. 재접촉 시간창·판정 threshold 등은 미명시다.

<a id="rw07"></a>

## 3.07. Beltran-Hernandez 2020 — Learning Force Control

**출처:** [상세 노트 §17–20](../papers/2020-beltran-hernandez-learning-force-control.md). SAC와 position/force 또는 admittance controller를 결합하며 같은 reward 구조를 여러 task에 사용한다.

$$
r(s,a)=w_1L_m\left(\left\|x_e/x_{\max}\right\|_{1,2}\right)+w_2L_m\left(\left\|a/a_{\max}\right\|_2\right)+w_3L_m\left(\left\|F_{\mathrm{ext}}/F_{\max}\right\|_2\right)+w_4\rho+w_5\kappa.
$$

| 성분 | 역할 |
| --- | --- |
| $x_e/x_{\max}$ | 알려진 목표 EEF pose에 대한 오차를 정규화 |
| $a/a_{\max}$ | 큰 action 억제 |
| $F_{\mathrm{ext}}/F_{\max}$ | 큰 접촉 하중 억제 |
| $\rho$ | Step/time penalty |
| $\kappa$ | 완료·safety 결과 |

$$
\kappa=\begin{cases}200,&\text{task completed},\\-10,&\text{safety violation},\\0,&\text{otherwise}.\end{cases}
$$

$L_m$은 reward range로의 선형 mapping이다. Mapping의 구체 범위·계수, $w_i$와 각 정규화 기준값은 노트만으로 완결되지 않는다. $\lVert\cdot\rVert_{1,2}$도 노트 표기를 보존하며 임의로 단일 L2 norm으로 바꾸지 않는다. **200·−10은 $\kappa$ 내부 값**이므로 가중치 $w_5$를 적용한 최종 기여와 구분한다.

실행 전 IK·관절속도 검사에 실패한 action은 차단하고, 접촉 하중 한계 초과 시 episode를 종료한다. 이 fail-safe는 학습 penalty와 별도다. 물체 GT 중심 보상이 아니라 **EEF 목표 오차와 실제 F/T 기반 하중**을 사용하는 사례다.

<a id="rw08"></a>

## 3.08. Lee 2024 — DexTouch

**출처:** [상세 노트 §8](../papers/2024-lee-dextouch.md). 원문 §IV-B, 식 (1)–(4), PDF p. 4. PPO의 접근·조작 reward이며 서로 다른 정책을 강제 전환하는 상태기계로 해석하지 않는다.

전체 구조는 **해설식**이다. $\lambda_v$는 속도 penalty를 나타내기 위한 설명용 기호이며 원문의 명시 계수가 아니다.

$$
r_t=r_{\mathrm{reach},t}+r_{\mathrm{execute},t}-\lambda_v\lVert\dot q_t\rVert_1.
$$

### 공통 접근 — 최고 근접 기록 갱신

원문 식 (1):

$$
r_{\mathrm{reach}}=\sum_{\mathrm{finger}}\alpha_{\mathrm{reach}}\max(d_{\mathrm{closest}}-d,0).
$$

$d$는 현재 손끝–대상 거리, $d_{\mathrm{closest}}$는 episode에서 달성한 최고 근접 기록이다. 후퇴했다가 같은 위치로 돌아오는 것만으로는 새 접근 보상을 얻지 못한다. **이전 step과의 거리 차분과 다르다.** 기록 갱신의 코드 순서는 미명시다.

### 파지·운반

원문 식 (2):

$$
r_{\mathrm{execute}}=(1-\mathbf{1}_{\mathrm{picked}})\alpha_{\mathrm{pick}}h_{\mathrm{obj}}+r_{\mathrm{picked}}+\mathbf{1}_{\mathrm{picked}}\alpha_{\mathrm{goal}}\max(\tilde d_{\mathrm{closest}}-\tilde d,0).
$$

들기 전에는 높이 $h_{\mathrm{obj}}$, 물체가 테이블에서 **10 cm 초과**로 올라간 뒤에는 목표까지의 최고 근접 기록 갱신을 보상한다. Picked 도달 bonus도 있다. 높이 항은 진행 차분이 아니라 현재 높이에 비례한다.

### 문손잡이·문 열기

원문 식 (3):

$$
r_{\mathrm{execute}}=(1-\mathbf{1}_{\mathrm{rotated}})\alpha_{\mathrm{rot}}\max(\phi-\phi_{\max},0)+\mathbf{1}_{\mathrm{rotated}}\alpha_{\mathrm{open}}\max(\psi-\psi_{\max},0)+r_{\mathrm{rotated}}+r_{\mathrm{opened}}.
$$

손잡이 회전 $\phi$가 **1.047 rad, 약 60°**를 넘기 전에는 손잡이 회전 기록을, 이후에는 문 열림 $\psi$의 기록을 보상한다. 문 **0.873 rad, 약 50°** 초과에 opened bonus를 준다. 각 최대값은 현재 시도에서의 기록이다.

### 밸브

원문 식 (4):

$$
r_{\mathrm{execute}}=\alpha_{\mathrm{rot}}\max(\theta-\theta_{\max},0)+r_{\mathrm{success}}.
$$

회전 기록 갱신과 **135° 초과** success bonus다. 상대 가중치·bonus 수치, flag 유지 여부·중복 발행 방지 구현은 미명시다. Door 식 뒤 문장의 picked/rotated 표기 불일치는 상세 노트에 기록되어 있다.

이 보상들은 시뮬레이션의 물체 거리·높이·각도를 사용한다. **Binary tactile만으로 reward를 계산한 연구가 아니다.** 속도 L1 penalty도 접촉력 상한과 같지 않다.

<a id="rw09"></a>

## 3.09. Wu 2019 — MAT

**출처:** [상세 노트 §15–16](../papers/2019-wu-mat-adaptive-tactile-grasping.md). Soft PPO를 쓰는 multi-finger grasping이다.

마지막 lift에서의 terminal reward:

$$
r_{t_{\\mathrm{final}}}=\\mathbf{1}_{\\{\\text{pick-up successful}\\}}.
$$

Terminal 이전에는 원칙적으로 0이지만, 충분히 닫아보지 않고 reopen하면 다음 penalty를 준다.

$$
r_t=-0.05a_t^{\\mathrm{reopen}}\\left(1-\\mathbf{1}_{\\{\\max_{i\\in\\mathrm{grip\\ joints}}[s_t^{\\mathrm{joint\\ angles}}]_i>0.2\\,\\mathrm{rad}\\}}\\right),\\qquad t<t_{\\mathrm{final}}.
$$

따라서 **모든 reopen에 −0.05가 아니다.** 최대 grip joint angle이 0.2 rad를 넘기 전에 reopen할 때만 적용된다. Terminal 성공은 1, 실패는 0이며 별도 실패 −1로 바꾸지 않는다.

촉각 면적·접촉 수·힘 크기를 매 step 최대화하는 dense reward는 이 구조에 없다. Soft PPO의 entropy 항은 정책 최적화 목적이며, 별도 물리적 grasp reward로 합쳐 적지 않는다.

<a id="rw10"></a>

## 3.10. Ding 2021 — Sim-to-Real Transfer with Tactile Sensory

**출처:** [상세 노트 §5.4–5.5](../papers/2021-ding-sim-to-real-tactile-manipulation.md). 원문 §IV-C-c, 식 (4)–(9), PDF p. 4. TD3 door opening이다.

$$
R=5.0r_{\mathrm{door}}+0.4r_{\mathrm{dist}}+0.05r_{\mathrm{ori}}+0.1r_{\mathrm{grasp}}+0.01r_{\mathrm{tactile}}.
$$

| 항 | 보상하는 내용 |
| --- | --- |
| Door | Grasp가 유지될 때 door hinge angle 자체 |
| Distance | Gripper와 knob center의 근접 |
| Orientation | Gripper와 목표 orientation의 정렬 |
| Grasp | 양 finger가 knob에 contact한 상태 |
| Tactile | Grasp 중 문이 열리기 시작했을 때 활성 tactile unit 수 |

활성 수 항의 기본식은 다음과 같다.

$$
r_{\mathrm{tactile}}=\lVert\hat{\mathbf{c}}\rVert_1\quad\text{when grasp is maintained and }\alpha>\alpha_0,\qquad\alpha_0=1.15^\circ.
$$

30개 binary unit의 활성 수이지 압력·힘의 합이 아니다. 조건 없이 접촉 bit 수만 계속 늘리도록 하는 reward로 설명하지 않는다.

**확인 범위:** 기존 노트에는 distance·orientation 등 모든 개별 함수식이 전재되어 있지 않다. 원문 식 (5)–(9)가 없다는 뜻은 아니다. Door angle을 각도 진전량으로, distance 항을 step 차분으로 임의 변환하지 않는다. Actor는 지속적인 knob 상대 위치·hinge angle도 받으므로 Blind actor 사례와 구분한다.

<a id="rw11"></a>

## 3.11. Zhang 2025 — The Role of Tactile Sensing

**출처:** [상세 노트 §3.3–3.4](../papers/2025-zhang-role-of-tactile-sensing.md). 원문 §III-A, Table I, PDF p. 2. SAC·MPO의 reach-and-grasp 비교에 사용한다.

### 주 보상 — rollout 뒤의 파지 안정성 시험

$$
r_{\mathrm{grasp}}=1000\frac{t_{\mathrm{inhand}}}{t_{\mathrm{total}}}.
$$

로봇이 물체를 들어 올리고 orientation을 유지한 채 random force를 가하고 기다린다. 그 시험 중 **양 finger 접촉을 유지한 시간**을 누적한다. 전체 시험시간 대비 유지 비율을 보상하므로 단순한 순간 lift 여부와 다르다. 위 식을 rollout의 매 step마다 지급하는 보상으로 옮기지 않는다.

### 매 step auxiliary reward

Touch, approach, 양쪽 force relation, force threshold 초과 penalty를 사용한다. 기존 노트에는 이 항들의 완전한 식·가중치가 전재되어 있지 않으므로 임의로 force difference나 force norm으로 구체화하지 않는다.

원문 Table I의 관계 $f_{\max}=3f_{\mathrm{penalty}}$는 기록되어 있지만 $f_{\mathrm{penalty}}$의 수치는 미명시다. **사후 안정성 평가 보상과 실행 중 shaping이 결합된 구조**라는 점이 비교의 핵심이다.

<a id="rw12"></a>

## 3.12. Su 2024 — Sim2Real Manipulation on Unknown Objects

**출처:** [상세 노트 §8](../papers/2024-su-sim2real-tactile-manipulation.md). 원문 §IV Reward Function, PDF p. 3의 번호 없는 식. PPO다.

$$
R=w_{\mathrm{contact}}r_{\mathrm{contact}}+w_{\mathrm{position}}r_{\mathrm{position}}+w_{\mathrm{angle}}r_{\mathrm{angle}}-w_{\mathrm{penalty}}r_{\mathrm{penalty}}.
$$

| 항 | 식·값 | 확인 범위 |
| --- | --- | --- |
| Contact | 기본값 0.5 × 접촉 센서 수 0·1·2 | 기여는 0·0.5·1. 힘 크기 추종이 아님 |
| Position | $1-\mathrm{curdist}/\mathrm{initdist}$ | Gripper contact가 있을 때 가중치 10 |
| Angle | 현재·목표 각도 차이; distance와 유사한 구조라는 설명 | 전체 식·정규화·wrap·가중치 미명시 |
| Action penalty | $\lVert a\rVert^2$ | 가중치 0.01. **제곱 norm** |

Position은 초기 거리 대비 현재 근접도이지 직전 step 진전량이 아니다. 원문은 범위 −1~1이라고 서술하지만 표시된 식만으로 하한 −1이 보장되지 않는다. Clipping, 초기 거리 0 처리, 목표 위치 생성법, 무접촉 시 처리도 미명시다.

이 구조를 “접촉 유지 + 위치·각도 목표 + 큰 action 억제”로 읽을 수 있지만, 부족한 angle 식이나 force tracking 항을 만들어 넣지 않는다.

<a id="rw13"></a>

## 3.13. Yin 2023 — Rotating without Seeing

**출처:** [상세 노트 §7](../papers/2023-yin-rotating-without-seeing.md). 원문 §IV-A.3, 식 (1)–(2), PDF p. 4; Appendix D 식 (3)–(9), PDF p. 14. PPO다.

$$
r_t=20r_{\mathrm{rot}}+0.1r_{\mathrm{vel}}+r_{\mathrm{fall}}+0.0003r_{\mathrm{work}}+0.0003r_{\mathrm{torque}}+0.1r_{\mathrm{dist}}.
$$

$$
r_{\mathrm{rot}}=\mathrm{clip}(\Delta\theta,-0.157,0.157),\qquad r_{\mathrm{vel}}=-\lVert\mathbf{v}_t\rVert.
$$

$$
r_{\mathrm{work}}=-\langle|\boldsymbol{\tau}|,|\dot{\mathbf{q}}_t|\rangle,\qquad r_{\mathrm{torque}}=-\lVert\boldsymbol{\tau}\rVert.
$$

$$
r_{\mathrm{dist}}=\mathrm{mean}_{i=0,1,2,3}\left[\mathrm{clip}\left(\frac{0.1}{0.02+4d(\mathbf{x}_{\mathrm{tip}}^i,\mathbf{x}_{\mathrm{obj}})},0,1\right)\right].
$$

| 항 | 의도와 적용 조건 |
| --- | --- |
| Rotation | 원하는 회전축에 수직인 평면에서 pose 변화로 계산한 signed angle increment |
| Velocity | 물체의 병진 운동 억제 |
| Fall | 물체가 손바닥 밖으로 떨어질 때 −50.0; 매 step 상수가 아님 |
| Work | Controller torque와 joint velocity의 성분별 절댓값 곱 억제 |
| Torque | 큰 관절 구동 torque 억제 |
| Distance | 네 손끝이 물체에 가까이 있도록 clipped inverse-distance shaping |

$\Delta\theta$는 **각도 변화**이며 $\Delta t$로 나눈 각속도가 아니다. 저자들은 simulator 각속도 기반 보상에서 나타난 진동 문제 때문에 pose 변화 기반 회전량을 사용했다고 설명한다.

Work 식에는 시간 적분이 없으므로 총 에너지로 바꾸어 부르지 않는다. $\tau$는 **관절 controller torque**이지 손목 외력 torque가 아니다. GT object pose·velocity와 위치 정보가 reward에 사용되며 actor 관측과 분리된다. 낙하·초기 위치 이탈·회전축 이탈의 정확한 reset threshold는 미명시다.

<a id="rw14"></a>

## 3.14. Yuan 2024 — Robot Synesthesia

**출처:** [상세 노트 §7.3–8](../papers/2024-yuan-robot-synesthesia-visuotactile.md). **Privileged-state PPO teacher**의 보상이다. 배포용 visuotactile student는 BC·DAgger로 학습한다.

| 구성요소 | 목적 |
| --- | --- |
| Object rotation angle | 원하는 회전 달성 |
| Object linear velocity penalty | 손 안에서 불필요한 병진 억제 |
| Object–fingertip distance | 손끝과 물체의 상호작용 유지 |
| Joint torque penalty | 큰 구동 억제 |
| Controller work penalty | 과도한 구동 억제 |
| Command–actual control error penalty | 명령과 실제 제어 결과의 불일치 억제 |
| Object drop penalty | 낙하 시 큰 추가 벌점 |

기존 노트는 **weighted sum 구조**를 기록하지만 각 함수의 완전한 형태는 전재하지 않는다. 계수는 원문 본문 미명시로 기록되어 있다. Yin 2023과 항이 유사해도 그 논문의 20·0.1·0.0003을 복사하지 않는다. Teacher reward를 student의 imitation loss와 합쳐 새 reward로 설명하지 않는다.

<a id="rw15"></a>

## 3.15. Chen 2025 — ViViDex

**출처:** [상세 노트 §4.2–4.4](../papers/2025-chen-vividex.md). 원문 §III-B, 식 (2)–(3), PDF p. 3. 사람 영상에서 얻은 reference를 **state-based PPO reward**로 사용한다.

### Pre-grasp

$$
R_p=\sum_{t=1}^{T_p}10\exp\left(-10\left\|\mathbf{x}_{rt}^{t}(\mathbf{q}_r^t)-\hat{\mathbf{x}}_{rt}^{t}\right\|_2^2\right).
$$

현재 robot fingertip position을 reference fingertip position에 맞춘다. 위 식은 한 step 보상이 아니라 **pre-grasp 구간에 대한 합**으로 제시되어 있다.

### Manipulation

$$
R_m=\sum_{t=T_p+1}^{T_r}\left(\lambda_1R_m^h+\lambda_2R_m^o+\lambda_3\mathbf{1}_{\mathrm{cont}}+\lambda_4\mathbf{1}_{\mathrm{lift}}\right).
$$

| 항 | 의미·계수 |
| --- | --- |
| $R_m^h$ | Hand motion reference 추종; $\lambda_1=4$ |
| $R_m^o$ | Object reference pose의 위치·방향 추종; $\lambda_2=10$ |
| $\mathbf{1}_{\mathrm{cont}}$ | **접촉한 fingertip 수**; $\lambda_3=0.5$ |
| $\mathbf{1}_{\mathrm{lift}}$ | Table에서 lift되었을 때 bonus; $\lambda_4$ 미명시 |

$\mathbf{1}_{\mathrm{cont}}$는 기호 모양과 달리 단순 Boolean이 아니라 접촉한 손끝 개수로 설명된다. 기존 노트에 추가 scale $\alpha_1=50,\alpha_2=0.1$이 기록되어 있지만 대응 subterm의 완전한 식은 전재되어 있지 않으므로 임의 위치에 대입하지 않는다.

Reference object trajectory는 평가에만 쓰는 것이 아니라 RL reward의 정답이다. Retargeting optimization의 loss와 최종 visual policy의 imitation loss는 위 reward와 별개다.

<a id="rw16"></a>

## 3.16. Liu 2024 — Tactile Active Inference RL

**출처:** [상세 노트 §8, 탐색 목적의 구분은 §6](../papers/2024-liu-tactile-active-inference-rl.md). 원문 §IV-B, 식 (11), PDF p. 5. Model ensemble·reward model·CEM을 사용하는 model-based active inference RL이다.

$$
r_1=\mathrm{sgn}(\mathrm{get\_target})-\mathrm{dis}(\mathrm{object},\mathrm{target}),\qquad r_2=\mathrm{sgn}(\mathrm{get\_target}),\qquad r_3=-H(y).
$$

| 과업·조건 | 설계 |
| --- | --- |
| Simulation dense pushing | 목표 영역 진입 0/1 + 물체–목표 중심 거리의 음수 |
| Simulation sparse pushing | 목표 영역 진입 0/1만 사용 |
| Real screwing | 하강 방향 tactile optical-flow entropy의 음수 |

여기서 `sgn(get_target)`은 **0/1 판정**으로 설명되며 일반 sign 함수의 −1을 추가하지 않는다. 거리 단위·정규화, 목표 영역 크기, 도달 후 보상 지급·종료 방식은 미명시다.

Real task에서는 하강이 고정되고 회전 증분을 조절한다. $H(y)$는 접촉면 flow의 분포에서 얻는 대리 지표이므로 **뉴턴 단위 shear force**가 아니다. Histogram·log 설정도 충분히 명시되어 있지 않다.

FEEF/CEM의 **expected information gain**은 별도의 탐색 목적이다. 이를 optical-flow entropy와 같은 값으로 취급하거나 임의 가중치로 식 (11)에 더하지 않는다.

<a id="rw17"></a>

## 3.17. Miller 2025 — Enhancing Tactile-based RL

**출처:** [상세 노트 §16.2·17.2·18.2, loss 구분은 §10–15](../papers/2025-miller-enhancing-tactile-rl.md). RoTO의 세 task를 PPO로 학습한다.

| Task | Reward 구성 | Event·조건 |
| --- | --- | --- |
| Find | Object–EEF distance가 작을수록 증가하는 dense reward | Object center GT는 actor에 없고 reward에 사용 |
| Bounce | 마지막 접촉 이후 시간에 비례하는 $r_{\mathrm{air}}$ + bounce bonus $r_{\mathrm{bounce}}$ + fall penalty $r_{\mathrm{fall}}$ | 최소 5 timesteps 무접촉 뒤 재접촉해야 bounce event |
| Baoding | 각 ball–virtual target 거리 + target switch의 rotation bonus + fall penalty | 두 ball 모두 target 1 cm 이내이면 target pair switch; ball distance 15 cm 초과 시 fall penalty |

Baoding은 처음에 두 ball을 잇는 벡터의 xy angular velocity를 최대화했지만, 의도와 다른 전략이 나와 **가상 목표점 추종**으로 변경했다고 기록되어 있다. 최종 reward와 초기 시도를 합산하지 않는다.

기존 노트에는 각 distance 함수·가중치·bonus 값의 전체 식이 전재되어 있지 않다. 15 cm 거리 판정의 기준을 손바닥/두 ball/목표 중 하나로 임의 확정하지 않는다.

TR·FR·FD·TFD는 observation encoder를 학습하는 **auxiliary loss**다. 이 네 손실을 환경이 지급하는 추가 reward로 재분류하지 않는다. 또한 Bounce의 무접촉 시간 보상은 “접촉이 많을수록 항상 좋다”와 다른 task-specific 설계다.

<a id="rw18"></a>

## 3.18. Pan 2026 — Beyond Binary

**출처:** [상세 노트 §8–9·16](../papers/2026-pan-beyond-binary-cop-tactile.md). 원문 Appendix E, Tables 4–6, PDF pp. 16–17. Asymmetric recurrent PPO다.

| Task | 보상 항 | Penalty 항 |
| --- | --- | --- |
| Insertion | Goal distance, terminal success, good contact | Peg rotation deviation, hand DOF deviation |
| Ball balancing | Ball–plate goal distance, plate contact | Relative velocity, plate position/yaw deviation, action difference, ball fall |

보상은 actor가 직접 받지 않는 peg·plate·ball의 simulator task state도 사용한다. **기존 노트는 항의 구조만 기록**하므로 good contact의 정확한 판정, 거리 함수 형태, 계수, success/fall threshold는 이 정리만으로 확정하지 않는다. 원문 Appendix의 표가 없다는 뜻이 아니다.

CoP를 actor 표현으로 쓴다는 사실만으로 “CoP 크기·위치 자체를 직접 최대화하는 reward”라고 해석하지 않는다. Insertion과 balancing은 같은 tactile 표현을 비교하더라도 서로 다른 목표·안정성 항을 사용한다.

<a id="patterns"></a>

## 4. Reward 설계를 유형별로 비교

아래는 앞 절의 보상을 비교한 **정리자의 분류**이며 새 reward 제안이나 성능 순위가 아니다.

### 4.1. 목표에 접근하는 방법이 다르다

| 구조 | 해당 사례 | 구분할 점 |
| --- | --- | --- |
| 현재 오차·현재 근접도 | [Yang](#rw01), [Bi-Touch](#rw02), [Dengler](#rw03), [Su](#rw12), [Liu dense](#rw16) | 가까운 상태 자체의 매 step 보상과, 새 진전량 보상은 다르다. |
| 매 step 물체 진전 | [Zhao](#rw06) | 로봇 이동이 아니라 물체의 의도 방향 이동량을 사용한다. |
| 최고 기록의 양의 갱신 | [DexTouch](#rw08) | 후퇴 후 같은 기록 복귀만으로는 해당 항의 새 보상이 생기지 않는다. |
| 목표 영역 안/밖 | [Bergmann](#rw05), [Liu sparse](#rw16) | Bergmann은 안 0·밖 −1, Liu는 도달 indicator이므로 숫자·누적 의미가 다르다. |
| Terminal 성공 중심 | [MAT](#rw09) | 성공 1·실패 0; 이른 reopen penalty만 추가한다. |
| Reference / subgoal 추종 | [Bi-Touch GUM](#rw02), [ViViDex](#rw15), [Miller Baoding](#rw17) | 움직임을 중간 목표나 시연 궤적으로 구조화한다. |
| 안정성 시험의 유지시간 | [Zhang](#rw11) | 순간 도달보다 사후 외란 아래 파지 유지 비율을 보상한다. |

이 비교는 각 논문의 명시 함수 형태에 근거한다. 모두를 potential-based shaping이라고 부르거나 최적 정책 보존이 증명되었다고 해석하지 않는다.

### 4.2. ‘접촉 reward’의 실제 입력을 구분한다

| 보상에 사용한 정보 | 사례 | 그 정보가 아닌 것 |
| --- | --- | --- |
| 접촉 유무·수·시간 | [Su](#rw12), [Ding](#rw10), [ViViDex](#rw15), [Zhang](#rw11), [Miller Bounce](#rw17) | 압력·법선력의 크기와 같지 않다. |
| 접촉면 정렬·기하학적 접촉 위치 | [Yang](#rw01), [Bi-Touch](#rw02) | 실측 wrench나 양팔 force balance가 아니다. |
| 연속 normal tactile force | [Zhao](#rw06) | Binary 접촉 수 reward와 다르다. |
| 측정 접촉 하중의 정규화 | [Beltran-Hernandez](#rw07) | 관절 구동 torque penalty와 다르다. |
| 양측 force relation·상한 | [Zhang](#rw11) | 기존 노트만으로 정확한 force 함수는 재구성할 수 없다. |
| 촉각 flow entropy | [Liu real](#rw16) | N 단위 shear force나 정보획득 objective와 같지 않다. |
| 장애물 접촉 사건 | [Dengler](#rw03) | 필요한 대상 물체 접촉 전체를 벌점 처리하는 것이 아니다. |
| 관절 torque·work | [Yin](#rw13), [Yuan](#rw14) | 외부 손목 wrench penalty가 아니다. |

### 4.3. 안전·종료·학습 보조를 분리한다

| 구분 | 사례 | 문서에서 유지한 경계 |
| --- | --- | --- |
| Reward + 별도 release | [Zhao](#rw06) | 과부하 penalty와 압력 해제 동작을 따로 기술 |
| Reward + fail-safe | [Beltran-Hernandez](#rw07) | 명령 차단·힘 초과 종료를 보상만의 효과로 서술하지 않음 |
| Reward + constraint | [Dadiotis](#rw04) | CAT의 constraint·termination probability와 네 보상 항 분리 |
| Reward + 최종 시점 성공 검사 | [Bergmann](#rw05) | 일찍 도달한 순간과 마지막 step의 성공 구분 |
| Reward + simulation 변경 | [Bi-Touch](#rw02) | 압착 penalty 강화와 센서 stiffness/damping 변경 분리 |
| Reward + auxiliary loss | [Miller](#rw17) | 표현학습 손실을 task reward에 혼합하지 않음 |
| RL teacher + imitation student | [Yuan](#rw14), [ViViDex](#rw15) | Teacher reward와 student loss 분리 |

### 4.4. 숫자를 옮길 때 확인할 사항

가중치만 비교하면 부족하다. 거리 단위·정규화, action scale, 한 step의 길이, episode horizon, 목표 도달 후 지급 방식이 다르면 같은 계수도 다른 누적 효과를 낸다. 이 문서는 미명시 설정을 통일하여 재계산하지 않았다.

특히 **norm과 squared norm**, **각도와 각속도**, **현재 거리와 차분·최고 기록**, **step 상수와 사건 bonus**, **내부 항 값과 전체 가중 기여**를 구분한다. 자세한 재현이 필요할 때는 각 절에서 표시한 미기재 항목을 원문 또는 해당 버전의 코드로 확인해야 한다.

<a id="excluded"></a>

## 5. 제외한 10편과 경계 사례

상세 노트가 있다는 사실만으로 포함하지 않았다. 아래 제외는 논문의 중요도나 논문 전체의 품질 평가가 아니라 **이번 reward-only 수집 범위**에 따른 것이다.

| 논문 | 제외 사유 |
| --- | --- |
| [Force Push](../papers/2024-heins-force-push.md) | 힘 피드백 기반 제어. 비교 대상인 RL task reward가 아님 |
| [Pushing in the Dark](../papers/2024-ozdamar-pushing-in-the-dark.md) | Reactive pushing 제어. RL 보상 설계가 아님 |
| [Pose-and-shear-based tactile servoing](../papers/2024-lloyd-pose-and-shear-based-tactile-servoing.md) | 추정·servoing 구조. RL reward가 아님 |
| [Visual, Force, and Tactile Door Opening](../papers/2026-simundic-visuo-force-tactile-door-opening.md) | 센싱·계획·재계획 구조. RL reward 비교 대상이 아님 |
| [Pseudo-Tactile Gripper State](../papers/2025-yang-pseudo-tactile-gripper-state.md) | Imitation learning·상태 판정/override 구조. 정책 학습 loss를 RL reward로 취급하지 않음 |
| [Gentle Object Retraction](../papers/2026-brouwer-gentle-object-retraction.md) | Imitation learning. Wrench 사용·impulse 기반 시나리오 선별을 RL reward로 재분류하지 않음 |
| [Differentiable Compliant Contact Primitives](../papers/2024-haninger-differentiable-compliant-contact-primitives.md) | 모델 추정·MPC. Estimation loss나 MPC cost를 RL reward로 바꾸지 않음 |
| [Tactile Gym 2.0](../papers/2022-lin-tactile-gym-2-0.md) | PPO는 확인되지만 상세 노트 §5.1에 reward 항·수식·계수 미제시로 기록. 다른 논문의 보상을 대입하지 않음 |
| [Attention for Robot Touch](../papers/2023-lin-attention-for-robot-touch.md) | DRL 제어를 평가하지만 노트 §8.4에 reward function 미제시로 기록. GAN·VAE loss는 제외 |
| [1 kHz Tactile Insertion](../papers/2024-wu-1khz-tactile-insertion.md) | 경계 사례: 노트 §11은 PIBB/evolution strategy에 의한 skill parameter 최적화와 rollout cost를 기술. 이를 일반적인 stepwise RL reward로 확정하지 않아 본편 제외 |

마지막 PIBB 사례는 parameter-space policy search까지 넓게 묶으면 함께 비교할 수 있다. 그러나 이번 본편에서는 기존 노트가 기술한 **RL reward와 rollout cost의 구분**을 유지했다. 제외했다고 해서 모든 형태의 policy search가 RL과 무관하다고 주장하는 것은 아니다.

## 6. 확인 범위와 갱신 기준

18편의 절은 각 상세 노트로 연결되어 있으며, 개별 논문의 일반 메소드·실험·Limitation·Future Work는 원래 노트를 따른다. 이번 작업으로 기존 28편의 정독 상태나 프로젝트의 reward 사양을 변경하지 않는다.

추가 원문·코드 검증으로 미기재 식이 확보되면 해당 **개별 노트를 먼저 보완**하고 이 비교본을 갱신한다. 이후 새 논문이 추가되면 포함·제외 수와 기준 commit도 함께 수정한다. 이 문서의 표는 특정 시점의 28편에 대한 결과이지 저장소 미래 상태에 자동 연동되는 목록이 아니다.
