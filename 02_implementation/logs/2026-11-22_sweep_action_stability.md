# 2026-11-22 Sweep 계통 action 안정화

## 요청과 확정 사항

사용자는 직전 진단의 세 환경에 공통 변경을 요청했다. 새 task/version을 만들지 않고 `SweepEnvCfg`를 직접 수정하며, 이 계통 밖에는 변경이 전파되지 않게 했다.

- `Inspire-Sweep-v0`
- `Inspire-Sweep-Single-Contact-v0`
- `Inspire-Sweep-Single-Contact-v1`

요청1의 -0.01 항목은 `hand_joint_velocity`였다. 요청2의 최초 문장은 범위 밖 값을 반대로 취급하는 것으로 읽힐 수 있어 확인했고, 사용자는 **0=펼침·1=굽힘, <0→0 / >1→1 clamp**로 확정했다. 이 해석으로 구현했다. 요청3의 비용 cap과 요청4의 계수는 사용자가 수치 판단을 위임했다. [원인 진단](2026-11-22_wr1122_value_loss_diagnosis.md)을 근거로 변화량 L2와 초과량 L2 모두에 상한을 적용했다.

작업 기준 root HEAD는 `1649acb074c2a780465f81cfee03d73af84e2c04`다. 작업 시작 시 root 소스는 clean, 문서 submodule에는 직전 진단의 미추적 기록이 있었다. 그 기록과 submodule HEAD를 보존했다. `example/Sweep-Policy`, IsaacLab, URDF/USD, 기존 학습 로그·체크포인트는 수정하지 않았다.

## 변경 전후와 적용 범위

| 요청 | 변경 전 | 변경 후 |
| --- | --- | --- |
| 손 관절 속도 | weight -0.01 | **-0.03**; 기존 속도 제곱합/cap100/관절 선택 유지 |
| 손 정책 입력 | 6개 직접 rad, 각 URDF 범위 clamp | **6개 [0,1] 비율**, clamp 후 각 URDF 상한을 곱함 |
| Arm/Hand action-rate | raw 차이 제곱합, weight -0.03, 상한 없음 | weight 유지, **그룹별 raw cap100** |
| Arm/Hand action-limit | raw 초과량 제곱평균, weight -0.03, 상한 없음 | **weight -3.0, 그룹별 raw cap10** |
| 손 action-limit 정규화 | 물리 URDF 폭으로 나눔 | 새 정책 단위에 맞춰 **폭1**로 계산 |

`NormalizedFingerJointPositionAction`을 기존 hand 구현 파일에 추가해 이번 EnvCfg에서만 선택한다. 부모 `FingerJointPositionAction`과 `BoundedFingerJointPositionAction`의 동작은 그대로다. 새 class는 raw action을 정규화 정책 단위로 보관하고, processed action/12관절 target은 rad로 보관한다. 구동 순서, 6개 독립 채널, URDF 상한 `[.5864,1.4381,1.4381,1.4381,1.4381,1.1641]`, mimic index·multiplier, 손 actuator, reset 시0으로 펼침은 유지한다.

공유 `finger_action_rate_l2`에는 `max_cost=None`, `action_limit_excess`에는 `hand_normalized=False,max_cost=None` 선택 인자를 추가했다. 기존 호출의 기본값·숫자 결과는 보존했고, Sweep v0의 부모 설정에서만 새 인자를 넘긴다. 별도 함수 이동이나 새 환경 상속 구조는 만들지 않았다.

## 상한·계수 선정 근거

Arm/Hand 각 그룹의 원본 명령을 a, 이전 명령을 b라 하면 변화량 raw cost는 다음과 같다.

```math
C_{\mathrm{rate}}=\min\left(\sum_{i=1}^{6}(a_i-b_i)^2,100\right).
```

Arm의 합법적인 두 명령 사이 최대 차이 제곱합은 6π²≈59.22, 정규화 Hand는6이다. cap100은 **허용 범위 안의 모든 명령 전환을 그대로 평가**하면서 극단적인 원본 출력만 제한한다. weight -0.03·dt0.02에서 각 항의 step 비용은 [-0.06,0]이다.

초과량은 e=a-clip(a,lower,upper), 전체 허용 폭은 Arm π, Hand1로 둔다.

```math
C_{\mathrm{limit}}=\min\left(\frac{1}{6}\sum_{i=1}^{6}\left(\frac{e_i}{w_i}\right)^2,10\right),
\qquad r_{\mathrm{limit}}=-3.0\times0.02\times C_{\mathrm{limit}}.
```

raw cap10 아래에서는 이전 계수 대비100배의 벌점이다. 6개 채널 모두 허용 폭의10%를 초과하면 step당 -0.0006, 50% 초과이면 -0.015, 100% 초과이면 -0.06이다. 500 step 지속 시 각각 -0.3/-7.5/-30이다. 정상 인접 경계의 제곱 기울기를 유지하면서, RMS 초과량이 전체 폭의 약3.16배를 넘는 극단 꼬리에서는 각 항을 step당 -0.6으로 제한한다.

따라서 action 관련 네 항의 합은 step당 **[-1.32,0]**이다. 이는 action 비용의 경계이며, 나머지 보상·전체 episode return의 경계라고 해석하지 않는다. 계수 -3과 cap10은 정상 보상 규모와 수치 보호를 고려한 초기 선택으로, 장기 성능에 최적이라고 검증한 값은 아니다. 정책 mean/std를 강제로 제한하거나 수치 안전 중단 조건을 완화하지 않았다.

## 보존한 계약과 체크포인트 의미

- Scene·물성·IK/reset·OSC 팔 제어와 ±π/2 제한·모든 종료·성공·커리큘럼·접촉면·Reach/Sweep는 유지했다.
- Actor/Critic 66+64D, 12D 출력, encoder/MLP·Gaussian·PPO·task ID·로그 이름은 유지했다.
- 실제 손 관절 위치 관측은 rad이며, Last Action callable의 기존 ±π/2 압축도 변경하지 않았다. 손 원본 action만 새 정규화 단위를 갖는다.
- 입력/출력 차원이 같아도 **기존 rad 정책 checkpoint의 손 출력 의미는 달라진다.** 자동 변환이나 호환 보장은 제공하지 않으며 새 학습을 기준으로 사용한다.
- 모든 기존 학습 자료는 보존했다. `logs/rsl_rl`에는 쓰지 않았고 검증 학습은 별도 outputs 경로를 사용했다.

## 최종 전체 설정 대조

실제 Isaac App에서 변경 전·후 EnvCfg/PPO 전체를 생성해 canonical JSON으로 저장했다. 세 대상은 각각 다음9개 필드만 달라졌다.

1. hand Action `class_type`
2. hand_joint_velocity weight
3. arm_action_rate max_cost
4. hand_action_rate max_cost
5. arm_action_limit weight
6. hand_action_limit weight
7. arm_action_limit max_cost
8. hand_action_limit max_cost
9. hand_action_limit hand_normalized

세 대상의 모든 PPO 설정은 동일했다. 계통 밖 `Inspire-Sweep-Only-v2-Test-ActionPenalty-LinearReach`와 `Inspire-Stabilize-Sweep-v0`는 전체 EnvCfg/PPO 차이가0이었다. 변경된 공유 함수의 기본 호출은 기존 회귀 검사로 대조했고, 기존 rad hand class 본문은 변경하지 않았다.

[전체 설정 차이](../../../../outputs/sweep_action_stability/config_diff.json) · [변경 전](../../../../outputs/sweep_action_stability/config_before.json) · [변경 후](../../../../outputs/sweep_action_stability/config_after.json).

## 실행한 검증

### CPU

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_sweep_action_stability.py \
  src/inspire_sweep_baseline/tests/test_sweep_only_action_penalty.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_v0.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact_v1.py
```

**76 passed**. 음수/0/1/초과·중간값의 정규화/물리 매핑, 모든6축·mimic, 입력 원본 보존, 기존 rad 동작, 정상 rate 보존·극단 값 cap, limit 양쪽 경계·정규화·cap, dt/weight, 잘못된 cap 거부, 기존 접촉/Reach/Sweep 회귀를 확인했다.

### 실제 GPU 환경

RTX3090·CUDA·seed42·각4환경에서 실행했다. 기본 선반 경로를 그대로 사용했으며 대체 선반을 만들거나 설정하지 않았다.

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_sweep_v0.py \
  --headless --output outputs/sweep_action_stability/sweep_v0_gpu.json
/home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_sweep_v0.py \
  --single-contact --headless --output outputs/sweep_action_stability/single_contact_v0_gpu.json
/home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_sweep_single_contact_v1.py \
  --headless --output outputs/sweep_action_stability/single_contact_v1
```

세 환경 모두 통과했다. v0 두 환경은8step·부분 reset, 실제 ActionManager/새 hand term의 raw 보존·normalized→rad 매핑·극단 raw 비용 cap, F/T 관측과 물리 reward 분리를 확인했다. v1은11step·부분 reset·팔 종료 사건 -3 일회·정상 timeout 자동 reset·Reach telescoping을 확인했다. v1이 부모의 공통 변경을 상속하며 기존 세 보상 차이만 갖는 것도 실제 Cfg로 대조했다.

### 저장 실패 배치 GPU 재생

[재생 실행기](../../../../outputs/sweep_action_stability/replay_failures.py)는 기존 실패 모델/관측/원본 action/optimizer를 고정하고 **실제 수정된 비용 함수**로 action 비용을 교체해 GAE 차이를 전파한 뒤 실제 PPO update를 실행했다. t0는 원본 이전 action이 없어 그대로 유지한다. 과거 action을 새 정규화 입력의 극단 stress fixture로 사용한 계산이며, 과거 모델을 새 환경에서 물리적으로 재학습/재생한 결과는 아니다.

| 실패 배치 | 원래 중단 loss | 새 비용식 stress replay loss |
| --- | ---: | ---: |
| Sweep v0 | 1116138.884766 | 0.914729 |
| Single Contact v0 | 2409849.125000 | 0.763209 |
| Single Contact v1 | 1775409.953125 | 9656.257185 |

모두 기존 loss/value ceiling 아래에서 유한한 update를 통과했다. v1의 기존 critic은 이미 큰 값을 내므로 비용 교체 후에도 오차가 크다. 기존 checkpoint가 복구됐다는 주장은 하지 않는다. [재생 원값](../../../../outputs/sweep_action_stability/failure_replay.json).

### train.py 짧은 학습

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Single-Contact-v1 --num_envs 16 --max_iterations 2 --seed 42 --headless \
  --resilient-attempt-dir outputs/sweep_action_stability/train --resilient-target-iterations 2 \
  hydra.run.dir=outputs/sweep_action_stability/hydra_train
```

16환경·36step rollout·2 iteration을 완료했다. value loss는3.645858/2.519642, 모든 loss·checkpoint·Adam state는 유한했다. 두 저장 시점 사이 Actor/Critic 및 각각의 obstacle encoder 파라미터 갱신을 확인했다. private attempt-dir 옵션은 검증 로그를 outputs에 쓰기 위해 사용했으며 supervisor·자동 재시작은 실행하지 않았다.

[학습 검증](../../../../outputs/sweep_action_stability/training_check.json) · [완료 상태](../../../../outputs/sweep_action_stability/train/training_status.json).

원래 세 failure dump와 TensorBoard event의 SHA-256이 직전 진단 때와 같은 것도 확인했다. 원본 체크포인트를 덮어쓰지 않았다.

## 문서·미검증 범위

환경 계약·활성 환경 안내·현재 인계·패키지 README를 갱신했다. 변경한5개 Markdown의 수식 검사와 root/문서 저장소 git diff --check는 통과했다. 전체 문서 저장소 링크 검사도 오류0으로 통과했다. 외부 패키지 README까지 포함한 검사는 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1개를 검출했다(변경 전 HEAD README에도 같은 링크가 있음). 이번 신규 링크는 정상이며, 관련 없는 기존 링크는 수정하지 않았다. 검증 산출물은 [outputs 안내](../../../../outputs/sweep_action_stability/README.md)에 모았다.

장기 학습 수렴·성공률·범위 이탈 빈도의 감소·계수의 최적성·대규모2048환경 학습·기존 checkpoint 재활용은 미검증이다. 이번 변경은 raw cost spike를 유한한 경계 안으로 제한하며 정책 mean/std의 상한이나 모든 수치 실패의 방지를 보장하지 않는다.
