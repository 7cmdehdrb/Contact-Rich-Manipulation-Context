# 중대 이슈: Finger 계열 PPO gradient 오류와 Gaussian 실행 명령 Clip 전환

2026-11-11. **심각도: 중대 — 학습 중단 및 정책 업데이트 불능.** 코드 수정·CPU 회귀 검증 완료, 원격 GPU 장기 학습 재검증 대기.

[환경 계약](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#finger-v1v2-출력-범위와-정밀-이동후퇴) · [현재 인계](../../01_plan/00_HANDOFF_BRIEF.md) · [개발 로그 색인](README.md)

## 사용자 보고와 영향 범위

사용자는 다른 Linux 컴퓨터에서 Semi-Prof-v0 학습이 약 10 iteration 만에 중단됐다고 보고했다. 처음에는 Finger-v2가 50 iteration 이상 정상 동작했으나, 이어서 같은 오류로 중단됐다고 보고했다. 제공 traceback의 최초 명시적 오류는 아래와 같다.

```text
NumericalTrainingError:
gradient/actor/distribution.log_std_param: invalid or above ceiling None;
indices=[[0], [1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11]];
unsafe training data/update rejected; no automatic restart
```

`NumericalPPO`의 optimizer pre-hook이 비유한 gradient를 검출해 optimizer 적용을 차단했다. 이후 PhysX stage detach/Recursive unload 경고는 종료 과정의 로그이며, 제공 traceback의 직접 중단 원인과 구분한다. `None`은 gradient 상한 검사가 없다는 뜻으로, 이 오류는 유한성 검사 실패다.

동일한 transformed Gaussian을 사용하는 다음 세 환경을 직접 수정했다. 새 task ID는 만들지 않았다.

| 환경 | 적용 경로 |
| --- | --- |
| `Inspire-Sweep-Simple-Finger-v1` | 공통 Gaussian PPO 설정·실행 Clip 런타임 |
| `Inspire-Sweep-Simple-Finger-v2` | Finger-v1 PPO·런타임 상속 |
| `Inspire-Sweep-Simple-Semi-Prof-v0` | Finger-v1 PPO·런타임 상속 |

Finger-v0 및 이전 Simple/Prof/Hard, 다른 과거 OSC 환경의 정책은 수정하지 않았다. 이번 요청의 대상인 Finger-v1에서 도입한 정책 변환·클리핑 계약의 전체 하위 환경을 포함한다. 공유 `NumericalPPO` 변경은 진단 메서드를 제공하는 새 Finger Gaussian에만 활성화된다.

## 확인된 결함과 증거의 한계

기존 구현은 Last Action에서 tanh를 제거하면서, 정책 자체에는 affine tanh 변환을 추가했다. PPO에는 변환된 액션만 저장하고 log probability 평가 시 정규화 → 경계 Clamp → atanh로 원래 Gaussian 샘플을 역복원했다. 사용자의 tanh 삭제 의도와 달랐고, 이 차이를 충분히 설명하지 않은 구현상 문제도 있었다.

Float32에서 tanh가 경계로 포화되면 원래 샘플 정보를 잃는다. 예를 들어 큰 양수 샘플이 동일한 상한 액션이 되고, 역변환은 원래 값 대신 약 7.25 부근을 반환한다. 저장 log probability와 재평가 모두 이 잘못 복원된 샘플을 사용하므로 처음 ratio는 1이지만, 작은 정책 업데이트 후 극단적인 꼬리 확률 변화가 발생할 수 있다.

실제 설치된 RSL-RL PPO + 프로젝트 `NumericalPPO` + Finger 모델을 CPU로 실행한 재현 결과:

| 조건 | 수정 전 결과 |
| --- | --- |
| Gaussian latent 평균0, std1 | 정상 업데이트 |
| 평균10, std0.01 | log probability 차이1237.625 → exp Inf → 동일한12축 log-std gradient 오류 |
| 평균100, std1 | log probability 차이104.23046875 → exp Inf → 동일한12축 log-std gradient 오류 |

entropy 계수를0으로 하거나 adaptive learning rate를 fixed로 바꿔도 실패했다. 3개 분포 조건 × 3개 entropy/schedule 조건에서 **6 실패·3 통과**였다. 입력 관측·보상·액션·파라미터는 유한했다. 따라서 Semi-Prof 힘 보상 전용 경로 없이 공유 정책에서 동일 증상을 재현할 수 있다.

**원격 실행의 `numerical_failure.pt`와 실제 실패 minibatch는 확보하지 못했다.** 위 결과는 실제 코드의 결함과 동일 traceback 재현을 입증하지만, 원격 두 실행의 정확한 샘플·분포 파라미터까지 확인한 것은 아니다. 다른 발산 원인이 모두 배제됐다고 주장하지 않는다.

사용자가 설명한 과거 Raw Action → Last Action → 다음 출력 증폭 문제는 이번 tanh 역복원 결함과 구분한다. 수정에서는 두 경로를 함께 고려하여, 무제한 Gaussian 샘플이 관측·action-rate 비용에 그대로 들어가지 않는 계약을 검증했다.

## 최종 변경 계약

| 항목 | 변경 전 | 변경 후 |
| --- | --- | --- |
| 정책 | Gaussian + affine tanh | 라이브러리의 일반 Gaussian 샘플 |
| PPO 저장 액션 | 변환된 bounded 액션 | Clip 전 원본 Gaussian 샘플 |
| log probability | atanh 역복원 + Jacobian 보정 | 원본 샘플의 Normal log probability |
| entropy·KL | 변환 entropy 표본 추정·latent KL | 일반 Gaussian entropy·KL |
| 실행 입력 | runtime·Action term Clip | 기존 축별 Clip 유지, 원본 텐서를 덮어쓰지 않음 |
| Last Action | bounded raw 값 | 실행용 Clip 후·Scale 전 값 유지. tanh·정규화 없음 |
| Action 비용 | ActionManager 현재·직전 명령 차이 | 현재·직전 모두 실행용 Clip 값임을 회귀 검증. 가중치·cap 유지 |
| 초기 분포 | latent 평균·std1 | 아래 축별 raw 단위 초기화 |
| 체크포인트 | transformed policy | 새 Gaussian 정책. 구 tanh checkpoint 로딩 거부 |

Scale 전 한계는 병진 각 축±0.5, 회전 각 축±π/2, 손6축은 하한0/상한0.5864·1.4381·1.4381·1.4381·1.4381·1.1641rad다. 기존 병진 Scale0.03, 회전 Scale0.15를 이후 적용한다. 손 위치 명령은 기존 rad 단위를 유지한다.

초기 평균은 팔0·손 관절 범위 중앙을 마지막 Linear bias로 지정한다. 마지막 Linear의 가중치는 초기값의0.01배로 하여 초기 상태 의존성을 작게 남긴다. std는 병진0.2, 회전0.5rad, 손 관절 범위 폭/6이다. std는 log parameter의 exp로 학습하며 과거 latent log-std Clamp는 제거한다. 환경 reset 손 자세·명령은 변경하지 않는다. 관측 정규화는 추가하지 않는다.

새 분포 `FingerGaussian`은 sampling/log probability/entropy/KL/결정론적 출력에 라이브러리 Gaussian 구현을 그대로 사용한다. 초기화·진단·구 checkpoint 거부만 추가한다. PPO loss·optimizer·학습률·rollout 설정은 변경하지 않는다.

기존 환경 진입 Clip 덕분에 ActionManager는 실행 명령만 저장한다. Last Action 및 Arm/Hand action-rate는 같은 명령 이력을 사용한다. 로컬 Action term의 방어 Clip과 기존 비유한 입력 처리도 보존한다. NumericalPPO는 새 정책의 원본 샘플/log probability를 검사하며, 잘못된 업데이트의 중단·복구 정책을 유지한다. NaN gradient를0으로 덮거나 배치를 버리거나 자동 재시작하지 않는다.

## 진단과 체크포인트·배포 영향

추가 지표는 `PolicyAction/clip_fraction/<axis>`, `PolicyAction/mean/<axis>`, `PolicyAction/std/<axis>`다.12축별로 policy step의 병렬 환경 평균을 수집하고 TensorBoard logger가 rollout 구간 평균을 기록한다. 단위는 Scale 이전 raw 단위다. GPU 텐서 reduction을 사용하고 지표 계산 자체는 반복적인 CPU readback을 하지 않는다. 기존 로그 지표를 유지하며 step마다 새 dict로 전달해 logger가 이전 값들을 보존한다.

Clip 비율이 높으면 평균이 경계 밖으로 이동했거나 탐색 std가 너무 큰지 조사한다. 이 지표는 보상이 아니며 학습 목적함수를 바꾸지 않는다. 낮은 Clip 비율이나 정밀도 개선을 보장하지 않는다.

구 checkpoint의 `distribution.transform.*` 키를 검출하면 `strict=False`에서도 명확한 오류를 내므로 **직접 Resume하지 않는다.** 이전 정책의 latent 평균은 새 raw 평균과 의미가 다르다. 모델·optimizer 강제 이관은 구현하지 않았다. 새 정책 checkpoint 저장·로드는 검증했다.

Deterministic play는 환경 진입 Clip을 사용한다. JIT/ONNX 정책 export는 일반 Gaussian 평균을 출력하므로 **외부 소비자가 축별 Clip → 기존 Scale을 적용해야 한다.** export 자체가 bounded라는 과거 계약은 폐기한다. JIT 실행 일치와 ONNX exporter 입력130D를 확인했고, ONNX Runtime 실행은 수행하지 않았다.

## 검증

재현 및 수정 후 회귀 명령은 workspace 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_hard.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_semi_prof.py \
  src/inspire_sweep_baseline/tests/test_bounded_ppo_failure.py \
  src/inspire_sweep_baseline/tests/test_numerical_ppo.py \
  -q -p no:cacheprovider --tb=short
```

결과: **82 passed in 10.78s**. 주요 근거:

- 수정 전9조건 중6실패 → 수정 후 동일 분포·PPO 조건9개 모두 통과.
- 실제 런타임 step의 Clip과 실제 Last Action/action-rate 함수를 사용해 큰 ±100 평균의 Raw Action을 두 rollout·두 PPO 업데이트 동안 전달했다. 물리와 관측 결합만 CPU 대역으로 교체했다. 원본 액션·log probability 저장 보존, 관측 제한, 실행 명령이 동일할 때 변화 비용0, 손실 유한성, 진단 지표 보존을 확인했다.
- 독립 `torch.distributions.Normal`과 log probability·entropy·KL 일치, 초기 평균·std, 새 checkpoint 왕복, 구 checkpoint strict/non-strict 거부, 전체 정책 JIT 실행 일치를 확인했다.
- 부모 설정 보존·세 환경의 상속·게이트·접촉·방향 보상·속도 커리큘럼 관련 기존 검사를 포함한다. 일반 PPO의 기존 수치 안전 회귀도 통과했다.
- 임시 `[DEBUG-bounded]` exp 계측은 제거하고 재현 파일은 회귀 테스트로 유지했다.

변경 문서5개의 수식 검사 통과, 내부 링크297개·외부 링크1개 검사 오류0, 코드와 문서 저장소의 `git diff --check` 통과. GPU는 `nvidia-smi`가 드라이버와 통신할 수 없는 상태다. 실제 PhysX reset/rollout, 대규모 Collection Time, 원격 GPU 재현 및 장기 학습 안정성·성공률은 미검증이다. 로그 디렉터리와 기존 학습 파일은 수정·정리하지 않았다.

## 최종 대조와 후속 확인

등록 ID·EnvCfg 상속·Scene·물리 자산·관측 차원·행동 차원·OSC Scale·reset·보상 가중치·성공/종료·커리큘럼은 보존했다. 정책 분포/초기화·구 checkpoint 거부·진단만 바뀌며, 기존 실행 Clip 경로가 새 Gaussian 샘플과 올바르게 분리됨을 확인했다. 문서의 기존 사용자 학습 현황 메모는 보존했다.

후속 학습은 새 run으로 시작하고, 원격에서 기존 중단 iteration을 넘긴 후에도 gradient·loss·Clip 비율·평균·std가 유한한지 확인한다. 재발하면 `numerical_failure.pt/.json`을 확보해 새 사건의 실제 실패 입력과 파라미터를 조사한다. 이 수정 기록을 장기 학습 안정성 검증 완료로 해석하지 않는다.
