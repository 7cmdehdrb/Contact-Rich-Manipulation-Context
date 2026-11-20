# wr7 Sweep Only v1 Test ActionPenalty 학습 중단 진단

## 요청과 범위

사용자는 `logs/TEMP/wr7/inspire_sweep_only_v1_test_action_penalty/2026-11-20_13-01-13`의 `loss/value: 1093255.046179087` 중단 원인을 요청했다. 환경·보상·PPO 설정 변경이나 학습 재시작은 수행하지 않았다. 저장된 설정, TensorBoard, 체크포인트, `numerical_failure.pt`를 읽고 CPU에서 실제 모델과 PPO update를 재생했다. 원본 학습 로그는 보존했다.

실행 기록의 코드 커밋은 `bab3f855df95702909b7e5e0815bdc67a24cfcce`, 진단 시작 시 workspace HEAD는 `30b499a427b0b14f3d07a3edc9642801a37c5eb2`이다. 관련 NumericalPPO·모델·관측·액션 페널티 구현을 대조했다. 해당 경로의 보상 파일에는 별도 LinearReach 함수 추가만 있으며, 이번 v1 실행은 기존 InverseDistanceReach를 사용한다.

## 확정된 원인

iteration 7455의 rollout step index 2, env index 744에서 손목 F/T 입력에 Actor가 과도하게 반응했다. 실행되는 명령은 컨트롤러에서 제한되지만, ActionPenalty 환경의 reward는 제한 전 원시 액션과 그 이력을 사용한다. 상한 없는 제곱 액션 비용이 큰 음수 보상을 만들고 GAE target에 전파되어, PPO value loss가 안전 한도 1,000,000을 넘었다. NaN·Inf에 의한 중단은 아니다.

| 관찰 | 값 |
| --- | --- |
| 해당 표본의 힘 입력 [N] | [6.859614, 37.612537, 17.014944] |
| 해당 표본의 모멘트 입력 [Nm] | [-4.734030, 0.806232, -0.226136] |
| 실제 샘플 액션 최대 절댓값 | 9,805.225586 |
| CPU Actor 평균 최대 절댓값 | 9,803.791992 |
| 다음 스텝 실제 액션 최대 절댓값 | 약 1.539 |
| 현재 스텝 저장 보상 | -91,059.460938 |
| 다음 스텝 저장 보상 | -83,664.812500 |
| 최소 return target | -168,951.328125 |
| 업데이트 전 전체 value MSE | 1,093,213.25 |
| env 744 제외 value MSE | 0.01199332345 |
| env 744의 전체 제곱 오차 비중 (float64 집계) | 99.99999890% |

저장 rollout은 36 steps × 2,048 envs이다. 액션 절댓값이 100을 넘는 표본은 [2,744] 하나이고, 보상이 -100보다 작은 표본은 [2,744], [3,744] 두 개뿐이다. 해당 스텝에서 done=0이므로 다음 스텝에도 이전 원시 액션이 action-rate 계산에 남는다. 직전 iteration 7454의 TensorBoard value loss는 0.0003881403이다.

## 가설과 개입 검증

재생으로 같은 value-loss 보호 오류를 확인한 다음, 다음 가설 순서로 검사했다.

1. 관측 변화가 극단 액션과 제곱 액션 비용을 유발했다면 F/T만 교체할 때 출력이 정상 크기로 돌아오고, 실제 액션으로 계산한 비용이 음수 보상을 설명해야 한다.
2. 일반적인 정책 출력 또는 탐색 std 증가가 원인이라면 F/T 교체 후에도 출력이 크거나 std 자체가 수천 수준이어야 한다.
3. 접촉·물리 페널티 또는 커리큘럼 전환이 직접 원인이라면 액션 비용으로 보상을 설명하지 못하거나 중단 시점에 해당 일정이 바뀌어야 한다.

### F/T 입력 개입

다른 124개 입력 값(policy 66 + obstacles 64 중 F/T 6개 제외)과 모델 가중치를 고정하고 F/T만 바꿨다.

| 개입 | Actor 평균 최대 절댓값 | Critic 값 |
| --- | --- | --- |
| 원래 표본 | 9,803.791992 | -3,700.238281 |
| F/T 6개를 직전 스텝 값으로 교체 | 1.915352 | 0.435043 |
| F/T 6개를 0으로 교체 | 1.924874 | 0.436950 |
| 힘 3개만 직전 값으로 교체 | 3,545.792480 | -1,220.732178 |
| 모멘트 3개만 직전 값으로 교체 | 4,508.056641 | -2,355.267334 |
| F/T 6개를 각각 [-1,1]로 제한 | 11.171380 | -37.939789 |

원래 표본의 탐색 std는 채널별 0.305–0.434이다. 극단 액션은 큰 Gaussian 탐색 노이즈보다 Actor 평균 출력에서 발생했다. 같은 표본을 각 체크포인트에 입력했을 때 평균 출력 최대 절댓값은 iteration 0에서 0.551, 1000에서 15.237, 3000에서 798.118, 5000에서 2685.425, 6000에서 5174.372, 7000에서 9661.333이었다. 학습 중 F/T 입력에 대한 큰 출력 반응이 누적된 증거이며, 그 반응이 왜 학습되었는지까지 단일 입력 실험으로 확정하지는 않는다.

이번 rollout F/T 채널 절댓값의 중앙값은 0.0077315, 99% 분위수는 0.1162613이다. N/Nm를 합친 입력 수치 분포이며 물리적 합력 통계는 아니다. 관측 정규화는 비활성화되어 있고, runtime의 F/T 제한은 힘 ±150 N, 모멘트 ±8 Nm이다. 이번 입력은 그 범위 안에 있어 제한되지 않는다. 이는 센서 값 자체가 오류라는 증거가 아니라 해당 rollout의 대부분 입력보다 큰 접촉 입력이라는 의미이다.

### 실제 액션 보상 항 재계산

현재 소스의 `finger_action_rate_l2`, `action_limit_excess` 함수 본문을 그대로 실행하고 저장 액션·직전 액션을 제공했다. 아래는 weight -0.03과 실제 RewardManager의 step dt=0.02를 포함한 step 기여량이다. 이전 논문 수식에서 dt를 생략한 표기와 실제 학습 계산을 구분한다.

| 항 | step 2 / env 744 | step 3 / env 744 |
| --- | --- | --- |
| arm action rate | -6,183.444824 | -6,180.218262 |
| hand action rate | -77,527.421875 | -77,484.625000 |
| arm action limit | -104.231911 | 0 |
| hand action limit | -7,244.374512 | -0.000445 |
| 네 항 합계 | -91,059.473122 | -83,664.843706 |
| 저장 총 보상과 합계의 차이 | +0.012184 | +0.031206 |

접촉·기울기 등 다른 항은 이 두 거대 음수 보상을 설명할 필요가 없을 정도로 잔여 기여가 작다. 비용 계산에는 상한이 없다. 물리 실행 명령을 제한하는 것만으로 원시 액션 기반 reward와 prev_action의 크기를 제한할 수 없다.

7455 시점의 wrench weight=-0.1, obstacle weight=-0.05, free force/moment change=30 N/3 Nm, obstacle free force=50 N이며 이 구간은 일정이 유지된다. 해당 iteration의 커리큘럼 변경으로 급락한 것이 아니다.

### PPO 재생과 대조

[재생 스크립트](../../../../outputs/diagnostics/wr7_v1_action_penalty/replay.py)와 [입력·보상 개입 스크립트](../../../../outputs/diagnostics/wr7_v1_action_penalty/ablation.py)는 원본 로그를 읽기만 한다. Simulator를 실행하지 않고 실제 SweepOnlyModel, RolloutStorage, NumericalPPO를 사용한다.

```bash
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python outputs/diagnostics/wr7_v1_action_penalty/replay.py
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python outputs/diagnostics/wr7_v1_action_penalty/replay.py --exclude-env-744
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python outputs/diagnostics/wr7_v1_action_penalty/ablation.py
```

- 전체 rollout: `loss/value: 1093222.8404152389; unsafe training data/update rejected; no automatic restart` 재현. exit code 2는 재현 성공을 나타내는 의도된 실패 반환이다.
- env 744를 제외한 실제 PPO update: value loss=0.01196046837, 오류 없이 통과.
- 두 스텝의 액션 비용을 return에서 선형 GAE 계수 gamma×lambda=0.98×0.95로 역산해 제거하면 업데이트 전 MSE는 186.65617이다. 이 값은 기존의 비정상 Critic 추정값을 그대로 남긴 반사실 계산이며, 수정된 환경의 학습 결과가 아니다.

전체 CPU update는 GPU 원 실행과 bit 단위 동일 재생은 아니다. dump에 없는 old log probability/distribution parameters를 업데이트 전 Actor로 재계산했으며, 원 RNG·GPU 연산 순서도 보존되지 않았다. 같은 유형의 오류와 근접한 집계 손실을 재현하고 입력·비용·환경 제거 개입으로 원인 경로를 확인했다.

## 영향·최종 대조·미검증

환경 및 학습 소스 변경은 없다. 진단 스크립트·출력과 이 개발 로그만 추가했다. 원본 checkpoints, params, TensorBoard와 다른 사용자 변경을 보존했다. GPU 학습, 물리 장면 재생, 재학습은 수행하지 않았다.

확정 범위는 F/T 입력 → 큰 Actor 평균 출력 → 제한 전 액션의 제곱 비용 → return 급락 → value-loss 보호 종료 경로다. F/T 순간값이 실제 접촉 충격인지, 보상된 센서 계산의 과도응답인지, PhysX 접촉 이상인지는 원시 물리 상태·접촉 기록이 dump에 없어 구분할 수 없다. 정규화 부재와 제한 없는 출력/비용은 코드상 확인되지만 각각의 개선 효과는 재학습으로 검증해야 한다. 안전 한도만 높이는 것은 이 경로를 해결하지 않는다.

## 산출물 검증

`replay.py --only-trigger`로 실제 [2,744] 표본 하나와 해당 시점의 return/value를 유지한 최소 PPO update도 실행했다. value loss=27,307,923,456으로 같은 보호 오류를 재현했다. 집계 크기는 단일 표본으로 축소했으므로 원래 전체 rollout 평균과 비교할 수 없다.

진단 스크립트 2개의 Python 컴파일, 이 문서의 Markdown 수식 검사, 외부 산출물 링크 검사(오류 0), 양쪽 저장소 `git diff --check`를 통과했다. 문서 렌더링은 검사하지 않았다. 작업 중 나타난 별도 사용자 파일 `docs/plan/PLAN19.md`는 수정하지 않았다.
