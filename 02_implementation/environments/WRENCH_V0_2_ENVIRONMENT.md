# Inspire-Wrench-v0_2 환경

2026-11-05. [v0 전체 계약](WRENCH_V0_V1_ENVIRONMENT.md)을 직접 상속한 feasibility 환경이다. [개발·검증 기록](../logs/2026-11-05_wrench_v0_2_implementation.md).

## 등록 및 보존 범위

- Gym ID: `Inspire-Wrench-v0_2`.
- EnvCfg: `envs/wrench_envs.py:WrenchV0_2EnvCfg(WrenchEnvCfg)`.
- Runtime: v0의 `runtime/wrench.py:WrenchEnv`.
- Reward/Curriculum: `WrenchV0_2RewardsCfg(WrenchRewardsCfg)`, `WrenchV0_2CurriculumCfg(WrenchCurriculumCfg)`.
- PPO: `WrenchV0_2PPORunnerCfg(WrenchPPORunnerCfg)`, 실험명 `inspire_wrench_v0_2`만 변경.

v0의 Scene·10개 물리 객체·Actor121D/Critic124D·8D action·pose OSC·센서·물성·관측 noise·종료·나머지 보상13항·PPO 수치를 유지한다. 장애물이 없어도 객체는 삭제하지 않고 부모의 비활성 주차·중력 해제를 사용한다. 목표 허용 거리5–15cm, deadzone30°에서10000 iteration에 첫5° 감소하고 이후3000마다 감소하는 일정, target speed 일정도 v0와 같다. v0_1의40° 고정·짧은 목표 거리는 상속하지 않는다.

## 거리 보상

`target_goal_distance`의 weight3.7, scale0.05m, EEF 높이120mm 미만 조건은 유지한다. 거리 감소량이 아니라 부모의 지수 근접도 식에 계수를 곱한다. 초기·현재 타겟과 목표는 world XY이며 초기 위치는 noise 없는 reset snapshot이다.

```math
\alpha_t=\begin{cases}
1,&d_t<0.03\,\mathrm{m},\\
\cos(\mathbf{p}_0-\mathbf{g},\mathbf{p}_t-\mathbf{g}),&d_t\ge0.03\,\mathrm{m}.
\end{cases}
```

```math
r_{\mathrm{distance},t}=3.7\,\Delta t\;\mathbf{1}[h_{\mathrm{EEF},t}<0.12\,\mathrm{m}]\;\alpha_t\exp(-d_t/0.05).
```

접촉 조건은 없다. 정확히3cm부터 signed cosine을 사용하고, 3cm 미만 예외는 사용자 후속 요청을 반영했다. 목표 반대편에서는3cm 밖의 계수가 음수가 될 수 있다. 목표점의 영벡터는 내부 예외로1이며, 외부 영벡터는 PyTorch cosine epsilon 처리로0이다. 비유한 결과는0이다.

## 접촉 유지 보상

기존 `target_contact` term 이름·weight1.45·threshold0.01N을 유지하고 함수만 `WrenchV0_2ContactMaintenance`로 바꾼다.

1. 물리 접촉 표본은 부모 함수 `target_contact_below_height`를 사용한다. fresh 센서, 유한 타겟–손 접촉 합력 norm≥0.01N, EEF 높이120mm 미만을 모두 요구한다.
2. XY 목표 거리3cm 미만이면 힘·freshness·높이와 무관하게 현재 접촉 표본으로 취급하며, 이력이 없어도 **현재 step을 즉시 접촉 인정**한다. 정확히3cm에서는 이 예외가 없다.
3. 현재 포함3개 표본에서2개 이상이 접촉이면 인정한다. 시작/reset 전 표본은False다. 인정할 때 카운트에1을 더하되 최대10으로 제한하고 연속 불인정 횟수를0으로 만든다.
4. 불인정이면 보상은0이고 연속 불인정 횟수에1을 더한다. 1–4회에는 카운트를 보존하고, 5회째에는 카운트를0으로 만든다. 기준은 원시 무접촉5회가 아니라 **윈도우 불인정5회**다.
5. 인정 step의 실제 보상은 `1.45 * 누적 인정 카운트 * dt`. RewardManager가dt를 한 번 곱하며 기본dt는0.02초다. 최대 카운트10이면 step당0.29를 지급한다.

실제 접촉 신호는 각 물체의 `hand_contact_<object>` 센서에서 현재 target ID를 선택한다. `force_matrix_w`의 손 필터 방향 벡터를 합한 뒤 norm을 취한다. 이는 **normal contact resultant**이며, 접선 마찰이나 각 접촉 norm의 합은 아니다. 반대 방향 힘은 상쇄될 수 있고 선반·비타겟 접촉은 타겟 접촉에 포함되지 않는다. 이 센서 정의는 부모 그대로다.

같은 제어 step의 중복 호출은 상태를 증가시키지 않는다. 부분 reset은 해당 환경의 윈도우·카운트·불인정 횟수·cached reward만 지운다. 평가 step이 건너뛰거나 되감기면 모든 이력을 지우고 새 표본부터 시작한다. 목표 도달 후 성공 종료까지 접촉 카운트가 계속 증가한다. 성공 판정 자체는 부모의 거리≤3cm·3D 속력≤0.005m/s 연속3초를 유지한다.

2026-11-05 후속: 누적 Contact Count는 최대10이다. 임시 진단 `TEMP v0_2 diagnostics` 블록은 값 조회부터 print까지 전체 주석 처리되어 출력·GPU→CPU 조회 비용이 없다. 필요하면 블록의 주석을 해제해 환경0의 누적값·접촉·목표 내부·윈도우·불인정 횟수·원시 보상을 다시 확인할 수 있다.

## 장애물 일정과 랜덤화

부모와 동일하게 White부터 증가시킨다. 아래는 랜덤화 전 **기준 개수**다.

| iteration 시작 | Gray | White |
| --- | --- | --- |
| 0 | -1 | -1 |
| 2000 | -1 | 0 |
| 5000 | 0 | 0 |
| 8000 | 0 | 1 |
| 11000 | 1 | 1 |
| 14000 | 1 | 2 |
| 17000 | 2 | 2 |
| 20000 | 2 | 3 |
| 23000 | 3 | 3 |
| 26000 | 3 | 4 |
| 29000 | 4 | 4 |
| 32000 이후 | 4 | 5 |

reset마다 환경별로 Gray와White에 각각 독립적인 균등 정수−1/0/+1을 더한 **후** Gray0–4, White0–5로 clamp한다. 따라서 iteration0–1999에는 항상0/0이다. 2000부터 White는0 또는1이 가능하고 Gray는0이다. 최종 기준4/5에서도 실제 요청은 Gray3/4, White4/5이며 clamp 때문에 상한의 확률이2/3다. 기존 배치 알고리즘이 실패하면 실제 배치 개수는 요청보다 적을 수 있고 `Metrics/obstacle_actual_*`, `Metrics/layout_complete`로 확인한다.

75개 도달 가능한 각도·랜덤화 개수 조합을 startup bank에 미리 생성한다. 조합별·환경별16개 후보, build batch256 설정은 부모 그대로다. reset에서는 개수 조합별로 묶어 기존 reset을 호출하며 OBB 검색을 수행하지 않는다. 관측 noise·가시성 랜덤화도 부모 함수를 재사용한다. v0의9조합보다 bank 저장 공간·startup 생성량이 증가하며,2048환경에서 실제 시간과 메모리는 미검증이다.

## 로그와 실행

보상15항·로그 term 이름은 그대로다. `Episode_Reward/target_goal_distance`, `Episode_Reward/target_contact`, `Curriculum/obstacle_population`의 의미가 위와 같이 달라진다. 기준 개수는 커리큘럼 로그, 배치된 개수는 기존 metrics를 따른다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-v0_2 --num_envs 2048 --headless
```

GPU 호스트용 probe도 v0_2를 지원한다. 아래는 실행하지 않은 검증 명령이다.

```bash
python src/inspire_sweep_baseline/tests/_wrench_probe.py \
  --version v0_2 --num_envs 64 --headless --device cuda:0
```

CPU87개 통과. 실제 Isaac Sim 초기화·물리 접촉·rollout·PPO·학습 성능은 NVIDIA 드라이버 사용 불가로 미검증이다.
