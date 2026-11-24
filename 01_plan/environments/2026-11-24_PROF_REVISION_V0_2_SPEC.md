# Prof Revision v0_2 개발 명세

작성일: 2026-11-24. 상태: **구현·등록 완료**. 검증 범위는 [구현 기록](../../02_implementation/logs/2026-11-24_prof_revision_v0_2_implementation.md)을 따른다. 아래는 개발 기준이며 장기 행동 개선은 미검증이다.

[부모 환경 계약](../../02_implementation/environments/PROF_REVISION_V0.md) · [작성 근거와 검증](../../02_implementation/logs/2026-11-24_prof_revision_v0_2_spec.md)

## 1. 목적과 범위

사용자는 v1의 종료 사건 비용 도입 후 움직이지 않으려는 경향을 보고했다. 이는 사용자 관찰이며 본 작업에서 정책을 재평가하거나 인과관계를 검증하지 않았다. 종료 직전에만 비용을 주는 방식에 더해, 팔 관절 속도가 0.8 rad/s를 넘으면 위험도를 점진적으로 알리는 비용을 도입한다. 손바닥·손등 선호도 제거한다.

**v0을 직접 상속하는 새 v0_2**를 만든다. 부모 v0을 직접 수정하거나 v0_1/v1을 부모로 삼지 않는다. v1의 손가락 각도 Formation도 가져오지 않는다.

| 항목 | 예정 구성 |
| --- | --- |
| Gym ID | `Inspire-Sweep-Prof-Revision-v0_2` |
| EnvCfg | `ProfRevisionV0_2EnvCfg(ProfRevisionEnvCfg)` |
| Rewards | `ProfRevisionV0_2RewardsCfg(ProfRevisionRewardsCfg)` |
| Runtime | 기존 `runtime.prof_revision:ProfRevisionEnv` 재사용 |
| PPO | `ProfRevisionV0_2PPORunnerCfg(ProfRevisionPPORunnerCfg)` |
| 로그 이름 | `inspire_sweep_prof_revision_v0_2` |

## 2. 면 선호 제거

부모 `sweep_progress`의 `ContactSideSweepProgress`를 기존 순수 `stabilize_sweep.sweep_progress` 함수로 교체한다. weight 100은 보존하고 면 선호 params는 제거한다. 면 계수는 구역·손바닥·손등·미분류 접촉 모두 1.0이다. 면 분류를 수행한 뒤 상쇄할 필요가 없다.

실제 transition 기여는 다음과 같다. d는 추적 가시 OBB 중심과 목표의 XY 거리, c는 기존 접촉 인정, a는 기존 힘 정렬 계수다.

```math
r_{\mathrm{sweep},t}=100\max(d_{t-1}-d_t,0)c_t a_t
```

접촉 최근 3회 중 2회 인정, 현재 힘의 유효성·방향 정렬, 후퇴 비용 −20은 그대로 둔다. **동등한 신호란 손의 접촉 면에 따른 차등을 없앤다는 뜻**이다. 목표 반대 방향 힘까지 동일하게 보상하거나 힘 정렬 계수를 제거한다는 뜻이 아니다. 촉각 관측·물리 센서는 유지한다.

기존 선호 면 1.5 대비 진행 보상은 2/3, 비선호 면 0.7 대비 약 1.429배, 중립 대비 동일하다. 이 스케일 변화는 면 계수 1 통일의 결과이며 weight 100으로 추가 보정하지 않는다.

## 3. 종료 전 속도 비용

### 입력과 집계

새 reward term 이름은 `arm_joint_velocity_margin`으로 한다. 기존 종료와 **동일한 `arm_entity()`의 팔 6관절 실제 joint_vel**을 사용한다. 명령 속도·손가락 속도·EEF 속도가 아니다. 정책 step 종료 시점의 물리 상태를 사용하며 절댓값으로 양·음 방향을 대칭 처리한다.

```math
v_t=\max_{j\in\mathrm{arm}}|\dot q_{j,t}|,
\qquad x_t=\min\left(1,\max\left(0,\frac{v_t-0.8}{1.0-0.8}\right)\right)
```

```math
C_t=x_t^2,\qquad r_{\mathrm{margin},t}=-\lambda_v C_t\Delta t,
\qquad \lambda_v=3.0
```

0.8 이하에서 새 비용은 0이며, 초과 구간은 제곱으로 증가한다. 0.8에서 값과 1차 미분이 연속이고, 0.8–1.0 열린 구간에서 단조 증가한다. 1.0에서 포화하므로 그 지점의 기울기는 연속이 아니다. 전체 구간이 무한 미분 가능한 함수라는 의미로 “부드러움”을 사용하지 않는다.

최대값 집계는 종료의 any-joint 조건과 대응한다. 합산하지 않으므로 여러 관절이 같은 위험 속도일 때 새 비용이 관절 수만큼 증가하지 않는다. 최대 관절이 바뀌는 지점의 미분 불연속은 허용한다. PPO는 물리 상태에 대한 이 함수의 미분을 직접 역전파하지 않는다.

**초기 설계 제안값**은 weight −3.0, free_speed 0.8, limit_speed 1.0이다. 사용자 지정은 0.8 시작점과 점진적 증가 의도이며, 제곱·최대값 집계·weight는 이 명세의 설계 선택이다. 최적값이나 정지 경향 개선이 실험적으로 확인된 값은 아니다.

보상 함수는 무차원 C만 반환한다. RewardManager가 weight와 policy dt를 한 번 적용한다. `/dt`로 나누지 않는다. 파라미터는 유한하고 `0 <= free_speed < limit_speed`여야 하며, limit_speed는 종료 threshold와 같음을 설정 검사한다.

| 최대 절대 팔 속도(rad/s) | C | 새 비용/초 | 새 비용/step(dt=0.02s) |
| --- | --- | --- | --- |
| 0.80 이하 | 0 | 0 | 0 |
| 0.85 | 0.0625 | −0.1875 | −0.00375 |
| 0.90 | 0.25 | −0.75 | −0.015 |
| 0.95 | 0.5625 | −1.6875 | −0.03375 |
| 1.00 이상 | 1 | −3.0 | −0.06 |

연속 비용은 체류 시간에 비례한다. 예를 들어 최대 속도 0.9를 1초 유지하면 새 비용 합은 −0.75다. 기존 `arm_joint_velocity` L2 비용(weight −0.03, raw cap 100)도 보존되어 더해진다. 따라서 0.8 이하에서 **전체 속도 비용**이 0이라는 뜻은 아니다.

### 종료 사건 비용

`arm_joint_failure`를 weight −3.0으로 추가한다. 기존 함수를 재사용하여 이미 계산된 `arm_joint_velocity` 종료 flag를 읽고 `flag / step_dt`를 반환한다. RewardManager 적용 후 실제 사건 기여는 −3.0이다.

```math
r_{\mathrm{joint},t}=-3x_t^2\Delta t-3\,\mathbf{1}[\mathrm{arm\_joint\_velocity\ termination}]
```

위 식은 새 두 항의 합이며 기존 L2 등 다른 비용은 포함하지 않는다. 종료 step에도 두 항을 모두 적용한다. dt=0.02이고 팔 속도 종료 시 새 두 항의 합은 −3.06이다. 큰 overshoot에서는 margin을 1로 포화하여 수치 폭증을 막으며 사건 비용은 별도로 남긴다.

기존 종료 조건 `any(abs(joint_vel) > 1.0)`을 보존한다. 정확히 1.0에서는 연속 비용 최대지만 속도 종료는 발생하지 않는다. 1.0 초과 시 종료·사건 비용이 발생한다. 성공·timeout·낙하·선반 종료만으로 `arm_joint_failure`를 부과하지 않는다. 다른 종료와 속도 종료가 동시에 참이면 사건 비용은 한 번만 부과한다.

본 설계는 종료 사건의 불연속 −3을 완전히 없애는 설계가 아니다. 사전 신호를 추가하고 사건 비용을 유지한다는 사용자 의도로 해석했다. 0.8에서 1.0까지 한 policy step에 뛰면 중간 구간을 실제로 경험하지 않을 수 있다. 별도 substep 감시·제어 속도 제한·action 변경은 포함하지 않는다.

## 4. 전체 변경 대조와 보존 계약

| 구성 | 부모 → v0_2 |
| --- | --- |
| Sweep 진행 | 면 선호 class → 순수 진행 함수, 면 params 삭제, weight 100 유지 |
| Margin 비용 | 없음 → 최대 팔 속도 기반 정규화 제곱, weight −3.0 |
| Joint 종료 사건 비용 | 없음 → 기존 arm_joint_failure, weight −3.0 |
| 활성 reward 수 | 16 → 18 |
| Formation | 부모 `0.05 / (0.05 + 손끝5개 OBB 거리 합)`, weight 0.245 유지 |
| Reaching | 추적 가시 중심까지 10cm 초과 거리의 대칭 증분, weight 4.9 유지 |
| 나머지 15개 부모 reward | callable·params·weight·순서 보존; 새 두 항은 뒤에 추가 |
| 종료 | 팔 속도 >1.0, 낙하/전도·선반·10초 timeout·timeout 시 성공 판정 모두 보존 |
| 관측 | Actor/Critic policy 108D·obstacles 176D, 초기 snapshot/실시간 보상 추적 구분·F/T·촉각 유지 |
| 행동·제어 | 팔 OSC6D·손 normalized6D, dt 0.01·decimation2·policy dt0.02 유지 |
| Scene·Command·Event·reset | 자산·물성·분포·목표3cm·Warp IK·가시성·배치 모두 상속 |
| Curriculum·runtime | 빈 curriculum·기존 runtime 유지 |
| PPO·네트워크 | gamma0.98 포함 모든 수치·구조 유지, 실험명만 변경 |

## 5. 구현 위치

패키지 기준 기존 역할별 파일에 추가하고 폴더를 신설하지 않는다.

- `envs/prof_revision_envs.py`: v0 직접 자식 EnvCfg.
- `mdp/rewards/prof_revision.py`: 자식 RewardsCfg와 세 term 차이.
- `mdp/reward_functions/prof_revision.py`: margin 함수 추가. 상태 누적·reset cache 없이 배치 계산.
- `agent/prof_revision_ppo_cfg.py`: 부모 PPO 직접 자식, 실험명만 분리.
- `__init__.py`: 새 Gym 등록 추가.
- `tests/test_prof_revision.py`, `scripts/check_prof_revision.py`: 수식 경계·부모 대조·실제 reward/종료 검증 확장.
- 구현 후 패키지 README·부모 계약의 파생 항목·활성 환경 안내·인계·개발 로그 갱신.

## 6. 구현 시 검증 기준

1. 모든 Manager·runtime·PPO 최종 설정을 부모와 대조한다. 위 차이만 허용하고 기존 v0/v0_1/v1/Reach5cm의 설정·동작 보존을 검사한다.
2. 속도 0, ±0.8 바로 아래/정확히/바로 위, ±0.9, ±1.0 아래/정확히/초과, 큰 overshoot의 유한값·단조성·포화를 검사한다. 한 관절과 여러 관절 초과·손만 빠른 경우를 구분한다.
3. 여러 dt에서 margin은 시간 적분 비용, 종료는 dt 무관 일회 −3임을 검사한다. 기존 L2 비용 중복 누락 여부와 종료 flag별 지급 조건도 확인한다.
4. 동일 progress/contact/alignment에 면·구역만 바꾸어 Sweep 보상이 동일함을 확인한다. 부모 면 선호 결과는 보존되어야 한다.
5. 실제 GPU 소수 환경 reset/step·부분 reset·자동 reset에서 관측 유한값, 18개 활성 term, reward 총합, 종료 transition 비용을 확인한다. 테스트용 속도 경계 주입과 실제 정책에 의한 종료 검증은 구분해 기록한다.
6. 짧은 PPO smoke는 `train.py`로 수행하고 학습·체크포인트 유한값을 확인한다. 이 검증만으로 장기 행동 개선을 주장하지 않는다.

장기 비교는 동일 seed·학습 예산에서 v0/v0_1/v0_2의 성공률·목표 진입률·최종 거리·목표 방향 순이동량·미진행 episode 비율·팔 속도 종료율·0.8 초과 체류 시간과 margin/사건/기존 L2 비용을 따로 기록한다. 종료율 감소가 단순 무동작 때문인지 반드시 확인한다. 목표 밖 미진행은 예를 들어 연속 1초 동안 순거리 감소가 1mm 이하인 구간으로 사전 정의하고 세 환경에 동일하게 적용한다.

새 비용을 더한다고 움직임이 회복된다는 보장은 없다. 특히 면 선호 제거로 기존 선호 동작의 양의 보상이 감소한다. 종료 비용만 문제였는지, 기존 Formation의 정지 보상이 영향을 주는지 등은 비교 실험에서 확인하며 본 버전에서는 추가 보상을 임의로 바꾸지 않는다.

## 7. 구현 후 실행 예시

다음은 구현된 v0_2 실행 명령이다. 새 학습을 기준으로 비교하며 기존 checkpoint의 구조적 로드 가능성을 성능 호환으로 해석하지 않는다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_2 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/play.py --task Inspire-Sweep-Prof-Revision-v0_2 --checkpoint /absolute/path/to/model.pt --num_envs 1 --real-time
```

초기 명세 작성 때는 코드 열람·수식 수치 대조·문서 검사만 수행했다. 후속 구현·실행 결과와 미검증 범위는 구현 기록에 분리해 기록한다.
