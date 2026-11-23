# Prof Revision v0 구현과 검증

2026-11-23 시작. **2026-11-24 후속 관측 정정은 문서 마지막 절이 우선한다.** 최초 상태: **구현·등록·기능 검증·필수 collection 성능 검증 완료**. [개발 명세](../../01_plan/environments/2026-11-23_PROF_REVISION_V0_SPEC.md)를 기준으로 독립 `Inspire-Sweep-Prof-Revision-v0`을 구현한다. 사용자는 질문 없이 판단하여 완료하고, GPU smoke·실제 collection 시간·기존 loss 발산 이력을 고려하라고 요청했다.

## 작업 기준과 보존 범위

Workspace `main` HEAD `d59007b3a946805c69a7181d5b9d7688dbb0b875`, 문서 submodule `main` HEAD `c66eef0a7638fd901284eef84a3bbbd84c5a36db`. 시작 시 이전 명세·개발 로그·인계 수정과 사용자 미추적 `docs/plan/PLAN20.md`가 있었다. 해당 내용·커밋을 보존한다. 신규 산출물은 `outputs/prof_revision_validation`에 저장하고 기존 `logs/rsl_rl`을 수정·정리하지 않는다.

EnvCfg/runtime/Scene/Manager/state/PPO/model은 기존 환경 클래스를 상속하지 않고 프레임워크를 직접 기반으로 구성했다. 계산 helper·자산 factory·Action term·공통 runner는 재사용한다. 기존 등록 뒤에 새 ID만 추가한다.

## 최초 구현과 판단 (2026-11-23)

- Actor/Critic은 초기 가시 OBB의 월드 snapshot을 현재 EEF 좌표로만 변환한다. 보상·성공은 초기 가시 조각의 target-link-local attachment를 현재 물체 pose로 추적한다.
- 직접99D·장애물128D·embedding16D·본체115D·action12D, encoder128→64→32→16과 독립 Actor/Critic 모델·227D export를 추가했다.
- Reach는10cm 초과 거리 대칭 변화4.9, Formation은 `0.245×0.05/(0.05+거리 합)`의 rate, Sweep100/−20, 높이 gate 제거, timeout 성공은 가시 중심3cm 이하로 구현했다.
- 가시성은 투영 구간과 edge 교차점을 사용하는 reset 전용 GPU 배치 커널로 계산한다. 2cm/20% 필터가 매우 저렴하므로 우선 유지했다. 고해상도 mesh mask·연결성 검사는 수행하지 않는다.
- OBB 최소 면적 해가 여러 개일 때 CPU/GPU의 수치 오차로 서로 다른 최소 직사각형을 선택하는 사례를 발견했다. 면적 차이1e-12 이내의 동률은 가장 작은 canonical yaw를 선택하고0/π/2 근방1e-12 회전도 통일했다. 원본 observed_obb와 최소 면적은 일치하지만 동률 Box 방향이 달라질 수 있다. 새 CPU reference와 GPU는 동일 규칙이다.
- 다섯 손끝은 같은 pad bounds 중점/max-z·pad-local identity 회전·공통 rigid transform과 quaternion 규칙을 사용한다. 실제 오른손 자산에 대응하는 `assets/data/wrench_right_hand/tactile_regions.json`을 사용했다. 명세가 처음 링크한 일반 metadata와 bounds가 소폭 달라 실제 자산 기준으로 선택했다.
- 기존 `finger_frame`은 새 손끝 관측용으로 사용하지 않지만 `ShelfCollisionPenalty`가 두 고정 tool probe를 참조한다. 첫 GPU 초기화에서 의존성 누락을 확인해 기존 Frame을 별도 선반 비용용으로 보존했다.
- NumericalPPO가 장애물4D 묶음을 고정 가정하므로 새8D 입력의 크기/yaw가 두 번째 mask로 잘못 해석될 수 있었다. 모델의 `obstacle_feature_dim`을 읽고 기존 기본값4를 유지하는 변경만 공통 guard에 적용했다. 유효 OBB의 큰 yaw를 검사하고 비유효 슬롯 전체를 무시하는 회귀를 추가했다. 기존 loss ceiling·PPO update·수치 보호 임계값은 그대로다.

## 검증 진행 기록

RTX3090·driver560.35.03, `/home/min/miniconda3/envs/env_isaaclab/bin/python`에서 실행했다. 실제 Sim은 해당 환경의 bundled Warp를 사용하며, Sim 외 단독 GPU 기하 검사는 환경의 Warp1.15.0을 사용했다. 두 경로의 검증 결과를 구분한다.

기준 Single Contact v0은 동일2048환경·seed42·36step·32iterations를 `train.py`로 실행 완료했다. 원본 `outputs/prof_revision_validation/baseline_train.log`와 별도 출력 경로의 checkpoint를 보존한다. 일부 collection이10초를 초과했으므로 이를 새 환경의 통과 근거로 사용하지 않는다.

단독 GPU OBB100장면 대조에서 최대 corner 오차 약1.12e-8m,2048장면10회 평균 약2.05ms였다. 이는 전체 collection이 아닌 기하 microbenchmark다. 이후 sparse source80장면·CPU 수식/기하·기존 Single Contact v0/v1/Zone3·NumericalPPO를 포함한64개 회귀가 통과했다. 이후 추가 수정은 최종 검사로 재확인한다.

GPU smoke는 실제 등록·설정·manager 구성·관측99/128D를 확인하는 중이며, 첫 시도의 선반 probe 누락을 위처럼 수정했다. 검증 스크립트는 부분 reset 비대상 행·고정 Actor 관측·현재 물체 추적·자동 timeout·JIT export를 검사한다. 최종 결과와 collection·loss 측정은 완료 후 아래에 추가한다.

## 최종 구성 대조와 기능 검증

최종 GPU smoke는 `check_prof_revision.py --headless`로4환경에서 통과했다. 최종 Scene/물리·Action·Command·Event params·기존 비용·기존 실패·PPO 수치를 v0 실제 Cfg와 대조하고, 새 EnvCfg/runtime의 직접 기반 클래스를 확인했다.12step·99D/128D·16개 보상·빈 curriculum·보상 합·손끝 native body pose와의 일치·고정 Actor OBB·타겟 병진/회전에 따른 초기 가시 조각 추적·부분 reset 비대상 행 보존·자동 timeout reset·실제 모델 JIT를 검사했다. 결과는 `outputs/prof_revision_validation/smoke.json`, 원본은 `smoke_final.log`다.

CPU 최종 회귀는200개 통과·3개 skip(이 실행에서 CUDA 숨김),11.47초다. `contract_final_tests_2.log`에 보존했다. 새 GPU OBB의 sparse physical source80장면은 앞선 CUDA 검사에서 별도로 통과했다. 초기 GPU reference100장면 검사와 함께 실제 Sim bundled Warp 실행도 smoke에서 통과했다. CPU 테스트는 signed Reach·2/3 접촉·역방향 비용·회전 비정육면체의 면/모서리/꼭짓점 거리·내부0·EEF tilt·quaternion·목표3cm 경계와 동시 실패를 포함한다.

실제 PPO 단위 검사에서 Actor/Critic 각각 encoder gradient·가중치 갱신·checkpoint 왕복·115D latent·masked row 전체 무시·227D JIT 출력 일치를 확인했다. ONNX exporter로 만든 실제 그래프의 checker와 ONNX reference evaluator 출력을 PyTorch와 대조해 통과했다. ONNX Runtime은 설치되어 있지 않아 해당 엔진의 실행은 하지 않았다.

최종 실제 `params/env.yaml`, `params/agent.yaml`과 baseline의 YAML node를 전체 비교한 결과는 `full_env_config_diff.json`, `full_agent_config_diff.json`에 보존했다. 허용 차이는 초기 OBB/손끝 관측, Reach/Formation/Sweep, 새 reset과 성공 callable, 새 OBB 수치, 제거한 높이·누적 정규화 필드, 새 모델 경로·encoder 폭·실험/출력 경로다. 비활성 `None` term의 생략과 기존 대표점 debug off도 기록했다. Scene·sim·제어·활성 기존 비용·기존 실패·PPO 알고리즘 수치는 동일하다. 기존 등록 prefix도 byte 단위 보존했고, 기존 패키지의 tracked 코드 수정은 새 등록과 NumericalPPO 폭 선택뿐이다. 새 파일들은 별도 추가다.

`source_snapshot`과 `source_hashes.json`에 새 코드·검사기·테스트 및 두 공통 변경 파일의 snapshot/해시를 보존했다. 최종 학습 실행 중 production 해시가 그대로임을 확인했다. 수식·상대 링크·공백 검증 결과는 작업 종료 전에 최종 갱신한다.

## 실제 실행 명령

모두 workspace 루트에서 실행했다. 검증 학습의 experiment name은 절대 출력 경로로 지정해 기존 `logs/rsl_rl`을 사용하지 않았다. baseline·초기 후보·최종 후보의 결과는 서로 다른 경로에 남긴다.

```bash
PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Single-Contact-v0 --headless --num_envs 2048 \
  --seed 42 --max_iterations 32 \
  agent.experiment_name=/home/min/7cmdehdrb/grad/outputs/prof_revision_validation/baseline
PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Prof-Revision-v0 --headless --num_envs 2048 \
  --seed 42 --max_iterations 32 \
  agent.experiment_name=/home/min/7cmdehdrb/grad/outputs/prof_revision_validation/train_final
/home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/check_prof_revision.py --headless
/home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/summarize_prof_revision_validation.py \
  --log outputs/prof_revision_validation/train_final.log \
  --runs outputs/prof_revision_validation/train_final \
  --baseline-log outputs/prof_revision_validation/baseline_train.log \
  --output outputs/prof_revision_validation/final_summary.json --require-performance
```

CPU 회귀 명령:

```bash
CUDA_VISIBLE_DEVICES='' PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest \
  src/inspire_sweep_baseline/tests/test_prof_revision.py \
  src/inspire_sweep_baseline/tests/test_numerical_ppo.py \
  src/inspire_sweep_baseline/tests/test_sweep_v0.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact_v1.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact_zone3.py \
  src/inspire_sweep_baseline/tests/test_sweep_action_stability.py \
  src/inspire_sweep_baseline/tests/test_fast_reset.py \
  src/inspire_sweep_baseline/tests/test_stabilize_sweep.py \
  src/inspire_sweep_baseline/tests/test_stabilize_sweep_com_cache.py -q --tb=short
```

## 기존 loss 발산 이력과 현재 검증 범위

과거 `wr4` 진단은 유한한 희귀 F/T 입력이 무제한 Gaussian 평균을 크게 증폭하고, 무제한 raw action-rate 비용이 큰 음수 return과 value MSE로 이어진 경우 및 Gaussian 분포 폭증 사례를 구분했다. 이번 구현은 명세대로 v0의 F/T 정규화·action-rate/limit cap·정규화 손 제어를 보존한다. NumericalPPO의 관측·평균·return·value loss ceiling, gradient/optimizer 유한성 검사, 양의 std 보호와 실패 dump를 유지한다. guard를 완화하거나 NaN을 덮거나 실패 batch를 버리거나 자동 재시작하지 않는다.

짧은 PPO와64회(초기32+최종32) 개발 업데이트의 유한성은 장기90,000iteration 안정성이나 sweeping 성공률을 입증하지 않는다. Formation의 목표 밖 정지 유인과16D embedding 충분성도 장기 학습에서 평가해야 한다. 전체 초기화 시간은 collection과 별도로 기록하며, 원본 선반 자산에 접근해 실행했고 대체 자산을 쓰지 않았다.


## 최종 성능과 loss 결과

최종 코드는 `train_final/2026-11-24_00-00-44`에서2048환경·seed42·rollout36·32iterations를 정상 완료했다. 원본은 `train_final.log`, 전체 원값·TensorBoard 범위·체크포인트 검사는 `final_summary.json`에 있다. 초기 후보는 진단 로그 추가 전 실행이고, 아래 완료 판정은 최종 코드 실행에 근거한다.

| 측정 | Single Contact v0 | Prof Revision v0 최종 |
| --- | --- | --- |
| Collection 평균 | 9.077219s | **5.701500s** |
| Collection 중앙값 | 9.727500s | 5.781500s |
| Collection p95 | 10.714s | 6.265s |
| Collection 최대 | 10.816s | **6.654s** |
| 32회 모두10초 미만 | 미충족 | **충족** |
| 32회 모두5초 이하 | 미충족 | **권장 목표 미달** |

첫 iteration0도6.654s로 포함했다. 출력 반올림 상한0.0005s를 더해도10초 미만이다. 자동/부분 reset·최종 OBB fitting·diagnostics·policy/value 추론·물리·센서·관측·보상을 포함한다. 정상 timeout 완료 지표도0보다 큰 값을 기록했다. reset OBB 관측의 rollout 집계 범위는 약5.286–5.959ms, 평균 슬롯은 약2.824–2.872, target-only fallback 비율은 이 seed에서0이었다. 이는 모든 seed에서 fallback이 없다는 뜻은 아니다.

초기화는 별도다. 최종 scene 생성38.492s·simulation start106.771s였으며 collection 목표의 수집 구간에 섞지 않았다. 학습 구간 전체 wall time과 learning time은 원본 로그에 별도로 남긴다. 동일 RTX3090·i9-9900K·driver560.35.03에서 측정했으며, 런타임은 CPU powersave 경고를 출력했다. 시스템 성능 모드·물리·환경 수·rollout·장애물 상한·접촉 계산을 낮추지 않았다. 다른 장비와 장기 학습의 시간 보장은 아니다.

최종32회 TensorBoard의 모든 scalar가 유한했다. value loss 범위는 **0.0000366420–0.0580811**, surrogate loss는−0.0749707–−0.00772280, entropy는8.45883–16.9515였다. 최종 `model_31.pt`의 모델과 optimizer 텐서·기타 float가 모두 유한했고 NumericalPPO 실패 dump는 없었다. `model_0.pt` 대비 Actor/Critic 장애물 encoder 가중치가 각각 갱신되었다. PPO update 전후의 실제 gradient 유한성은 기존 NumericalPPO guard가 모든 minibatch에서 검사했다. 기존 guard ceiling을 높이지 않았다.

## 최종 요청 대조와 인계

| 사용자 요구 | 구현과 증거 |
| --- | --- |
| 새 계열·정확한 ID·envs 새 파일 | 등록 entry point·독립 EnvCfg/runtime/Scene/model/PPO, `isolation_audit.json`과 GPU 실제 생성 |
| 초기 가시 OBB·Actor 초기 관측 유지 | GPU 배치 기하·CPU 대조·source mapping·mask·snapshot 고정 및 추적 병진/회전 smoke |
| 7D 타겟·8×16 장애물·encoder | 실제99/128D 관측·115D latent·227D export·encoder gradient/checkpoint 검사 |
| 손가락 Frame 생성 통일 | 실제 오른손 distal pad5개·동일 원점/축/변환·native body pose 대조·회전/EEF tilt 검사 |
| 대칭 Reach·10cm·가시 중심 | state 경계/부호 검사·실제 reward manager·reset history |
| Formation 표면 거리 합 역수·내부0·보조 수준 | bounded 역수·회전 비정육면체의 내부/면/모서리/꼭짓점 검사·0.245 rate |
| Sweep 가시 중심·2배·높이 gate 삭제 | 추적 local attachment·100/−20·독립 boolean2/3 state·기존 방향/면 callable 보존 |
| 빠른 collection·loss 주의 | 최종32회 모두10초 미만·권장5초 미달 구분·실제 loss/optimizer/checkpoint 검사 |
| 기존 환경 보존 | 모든 설정 차이 대조·기존 등록 prefix·공통 guard 기본4 유지·기존 계열 CPU 회귀 |
| 질문 없이 판단·근거 기록 | 필터 유지·OBB 동률·실제 오른손 metadata·기존 선반 probe를 위에 기록 |

새 환경·소스·README·환경 안내·명세·현재 인계를 정리했다. 기존 학습 로그·사용자 파일·submodule HEAD를 보존했다. 최종 문서 검사는 마지막 기록을 따른다.


최종 native 손끝 pose를 `smoke_frames.json`에도 저장하고 `finger_frames.png`로 다섯 원점과 로컬XYZ 축을 시각화해 확인했다. 동일 규칙으로 생성된 네 손가락과 엄지의 실제 pad body 방향 차이를 유지한다. 이 그림은 native Pose 좌표의 marker 검토이며 실제 렌더링 mesh와의 육안 중첩 검사는 아니다. `smoke_frames.log`의 동일 기능 검사가 다시 통과했다. 이 후속 변경은 검사기의 pose 기록만 추가했으며 최종32회 학습의 production 소스는 바뀌지 않았다.


최종 문서 검증: 변경 문서5개와 패키지 README의 수식 형식 검사를 통과했다. 새 명세·환경 안내·구현 로그의 내부7개/외부14개 링크 오류0, 인계·활성 환경 안내의 내부371개 링크 오류0이다. README 전체 링크 검사에서는 기존 HEAD부터 있던 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 링크1개가 누락된 것을 확인했고 이번 작업의 새 링크는 유효하다. 이 역사 링크는 요청 밖이므로 수정하지 않았다. workspace/문서 저장소 `git diff --check`, 신규 소스 줄 끝 공백, compileall 검사 통과. 최종 benchmark32회·유한 checkpoint·두 encoder 갱신·GPU smoke·production source 해시를 다시 대조해 통과했다.


## 2026-11-24 관측 정정

사용자는 여섯 판단 사항을 검토한 뒤 손 관절6D 복원과 타겟·장애물 방향의 yaw→quaternion 교체를 요청했다. 타겟의 가장 넓은 가시 조각 선택, Formation 식/weight, 가시 중심을 따르는 보상·성공 판정, 다섯 손가락 공통 Frame 규칙은 그대로 승인했다. 새 버전을 만들지 않고 `Inspire-Sweep-Prof-Revision-v0`를 직접 수정했다.

| 항목 | 수정 전 | 수정 후 |
| --- | --- | --- |
| policy 순서 | 팔 위치·속도→EEF→손끝→타겟→목표→action→tactile→wrench | 팔 위치·속도→EEF→**손 관절→손끝**→타겟→목표→action→tactile→wrench |
| 손 관절 | 없음 | 기존 `hand_drive_positions`·6D 실제 rad·`HAND_DRIVE_JOINT_NAMES` 순서 재사용 |
| Target OBB | xyz·wdh·heading7D | xyz·wdh·xyzw quaternion10D |
| 장애물 row | mask·xyz·wdh·heading8D | mask·xyz·wdh·xyzw quaternion11D |
| 장애물 encoder | 128→64→32→16 | **176→128→64→32→16**, ReLU·최종16D activation 없음 |
| policy / obstacles / 본체 / export | 99 / 128 / 115 / 227D | **108 / 176 / 124 / 284D** |
| 수치 guard | 모델 폭8 | 모델 `obstacle_feature_dim=11`, 공통 guard 구현·기존 기본4는 불변 |
| 방향 계산 | OBB x축의 EEF XY 투영 heading·퇴화 fallback | EEF 역 quaternion×초기 OBB quaternion·정규화·부호 canonicalize·xyzw |

손 관절 slice는 `[19:25]`, Finger Pose는 `[25:60]`, 타겟은 `[60:70]`이다. 손 관절은 엄지 굽힘·검지·중지·약지·소지·엄지 대립 순서이며 normalized action 비율로 바꾸지 않는다. EEF Pose 항은 기존 Base 기준 wxyz를 유지하고 새 OBB quaternion은 손끝과 동일한 xyzw 규칙이다. q와−q의 관측을 같게 하며 scalar=0은 첫 nonzero vector 성분으로 부호를 정한다.

reset에서 서 있는 물체의 정면 footprint·노출 폭을 계산하는 내부 yaw는 유지한다. 이번 변경은 EEF 상대 방향을 축약하지 않도록 하는 것으로, 물체가 서 있어도 EEF가 기울어지는 경우 전체 회전을 표현한다. 크기는 OBB 고유 축의 길이를 유지하고 EEF AABB로 바꾸지 않는다. 기존 reset OBB 기하·캐시·물체 attachment·보상용 quaternion은 변경하지 않는다.

최종 production 변경은 `mdp/observations/prof_revision.py`, `mdp/common/prof_revision_geometry.py`, `agent/prof_revision_models.py`, `agent/prof_revision_ppo_cfg.py`의4파일이다. 관측/모델 테스트·GPU smoke 검사기·README·현재 계약 문서도 갱신했다. 기존 모든 Python 파일의 작업 시작 해시를 저장해 그 외 production 파일의 불변을 확인했다. Scene/sim·Action·Command·Event/reset·보상16항·Termination·Curriculum·runtime·등록·PPO 알고리즘 수치는 수정 전과 동일하다. 새 모델의 인코더 hidden dim만 `[64,32]`→`[128,64,32]`로 변경했다. 이전99/128D checkpoint는 호환되지 않아 새 학습을 시작해야 한다.

검증 산출물은 기존 산출물을 보존하는 별도 `outputs/prof_revision_quaternion_validation`에 저장한다. `before_hashes.json`, `before/`, `after/`, `after_hashes.json`, `changes.patch`, `changed_files.json`에 변경 전후와 전체 코드 범위를 기록한다. workspace/문서 submodule HEAD와 사용자 파일·기존 `logs/rsl_rl`을 보존했다.

### 관측 정정 검증 명령

```bash
CUDA_VISIBLE_DEVICES='' PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest \
  src/inspire_sweep_baseline/tests/test_prof_revision.py \
  src/inspire_sweep_baseline/tests/test_numerical_ppo.py \
  src/inspire_sweep_baseline/tests/test_sweep_v0.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact_v1.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact_zone3.py \
  src/inspire_sweep_baseline/tests/test_sweep_action_stability.py \
  src/inspire_sweep_baseline/tests/test_fast_reset.py \
  src/inspire_sweep_baseline/tests/test_stabilize_sweep.py \
  src/inspire_sweep_baseline/tests/test_stabilize_sweep_com_cache.py -q --tb=short
PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/check_prof_revision.py --headless \
  --output outputs/prof_revision_quaternion_validation/smoke.json
PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Prof-Revision-v0 --headless --num_envs 2048 \
  --seed 42 --max_iterations 32 \
  agent.experiment_name=/home/min/7cmdehdrb/grad/outputs/prof_revision_quaternion_validation/train
```

CPU 회귀202개 통과·3개 skip(CUDA 비표시),12.65초를 `regression_tests.log`에 기록했다. EEF+90°pitch·OBB+90°yaw의 알려진 상대 자세,8개 꼭짓점 world 좌표 복원·q/−q 동일성·unit norm·비유효 장애물11값 전체mask를 검사했다. Actor/Critic encoder PPO 갱신·저장/로드·284D JIT·ONNX checker/reference evaluator·NumericalPPO11D row 해석도 통과했다. 첫 pytest 시작은 자동 로드된 ROS plugin의 `lark` 미설치로 실패하여 기존 검사와 동일한 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`로 정상 실행했다. 패키지를 설치하거나 실행 환경을 변경하지 않았다.

실제4환경 GPU smoke는 `smoke.log`·`smoke.json`에 기록하고 통과했다.108/176D·term 순서와 각 폭·손 관절slice와 실제 관절값·손끝slice와 공통cache·유효 OBB quaternion norm·보상16항·기존 설정 보존·snapshot 고정·물체 추적·부분reset·자동timeout reset·실제 모델JIT를 확인했다.


### 관측 정정 최종 성능과 전체 대조

최종108/176D 코드를2048환경·seed42·rollout36·iteration0~31에서 실제 학습했다. `train.log`와 `summary.json`에 전체 collection 원값·TensorBoard scalar 범위·checkpoint 검사를 남겼다. collection **평균5.7823초·최대6.609초**, 중앙값5.8915초·p95 6.233초로32회 전부10초 미만이다. iteration0·정상timeout·자동reset이 포함된다. 권장5초 이하는 전 구간에서 충족하지 못했다. 같은 RTX3090·i9-9900K·driver560.35.03과 원본 자산을 사용했고 환경 수·rollout·장애물 상한·물리·센서/접촉 연산을 낮추지 않았다. 초기화는 collection과 구분하여 원본 로그에 기록했다.

모든 TensorBoard scalar와 최종 모델·optimizer·checkpoint 텐서가 유한했다. value loss 범위는0.0000289537–0.0621515, 두 encoder는 model0→31에서 각각 갱신되었으며 numerical failure dump는 없었다. 최종 checkpoint는 `outputs/prof_revision_quaternion_validation/train/2026-11-24_00-20-12/model_31.pt`다. 장기 안정성·성공률·Formation 비율과16D embedding 충분성은 이번32회 검증으로 판단하지 않는다. ONNX는 exporter/checker/reference evaluator 검증이며 별도 ONNX Runtime 실행은 하지 않았다.

실제 실행의 전체 `params/env.yaml`·`params/agent.yaml`을 이전Prof Revision 최종 실행과 대조했다. `full_env_config_diff.json`의 차이는 손 관절term 추가와 검증log_dir뿐이고, `full_agent_config_diff.json`의 차이는 Actor/Critic encoder hidden dims 및 검증experiment_name뿐이다. 코드의 term 순서·OBB 표현/shape·export·guard row 폭 차이는 GPU smoke와 단위 검사로 확인했다. 기존 등록·독립 상속·Scene/sim·Command·Event/reset·Action·보상16항·종료·빈Curriculum·runtime·PPO 알고리즘·수치guard를 변경하지 않았고, 모든 기존 Python 파일의 작업 시작/완료 해시로4개 production 파일 외의 불변을 확인했다. 전체 대조 결과는 사용자 요구와 일치한다.

요약 검증 명령:

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/summarize_prof_revision_validation.py \
  --log outputs/prof_revision_quaternion_validation/train.log \
  --runs outputs/prof_revision_quaternion_validation/train \
  --output outputs/prof_revision_quaternion_validation/summary.json --require-performance
/home/min/miniconda3/envs/env_isaaclab/bin/python \
  outputs/prof_revision_quaternion_validation/config_diff.py
```

최종 문서 수식 검사6개 통과, 변경한 문서 저장소5개 파일의 내부378개·외부15개 링크 오류0, workspace/문서 저장소 `git diff --check` 통과다. README 링크 검사의 오류1개는 기존 HEAD부터 있던 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크이며 새 링크 오류는 없다. 새 Python 구문·줄 끝 공백·학습 전후 전체 소스 해시 대조도 통과했다.


## 2026-11-24 Reach5cm v0 직접 파생 추가

사용자는 방금 환경을 상속한 v0를 추가하고 Reaching 인정 반경만10→5cm로 바꾸며 GPU 테스트 없이 가볍게 수정하라고 요청했다. 부모 ID가 이미v0이므로 새 ID는 `Inspire-Sweep-Prof-Revision-Reach5cm-v0`로 정했다. 이전 작업트리·workspace/submodule HEAD와 사용자 파일·학습 로그를 보존했다.

`ProfRevisionReach5cmEnvCfg(ProfRevisionEnvCfg)`에 `reach_near_radius: float=0.05` 한 항만 선언했다. 부모 클래스·함수·관측·Scene/Action/Command/Event/reset·보상16항의 함수/params/weight·성공/실패/timeout·빈curriculum·runtime·모델·PPO 알고리즘은 그대로다. 부모 반경은0.10m로 유지한다. 새 runner는 부모를 직접 상속하고 기록용 experiment_name만 `inspire_sweep_prof_revision_reach5cm_v0`로 분리한다. 등록 runtime은 부모와 같은 `runtime.prof_revision:ProfRevisionEnv`이며 신규 EnvCfg/runner entry point만 지정했다.

코드 변경은 기존 역할별 파일3개에 자식2개와 신규 등록을 추가한 것뿐이다. 작업 시작 전체 Python 해시 및3파일 원본을 `outputs/prof_revision_reach5cm_static_validation/before_hashes.json`·`before/`에 저장했다. 추가 후 모든 기존 Python 파일을 대조하여 그3파일 외에는 차이가 없고,3파일도 기존 bytes를 prefix로 완전히 보존함을 확인했다. 자식 EnvCfg의 유일한 override가0.05인 것, runner의 유일한 override가 로그 이름인 것, 기존 runtime 재사용·등록 entry point·리터럴 ID 중복 없음을 AST로 확인했다. 결과는 `static_validation.json`에 기록했다. 초기 AST 검사기는 기존 동적 등록의 kwargs까지 literal_eval하여 실패했으며, 해당 검사를 리터럴 ID의 신규/부모 등록에 한정해 수정한 뒤 통과했다. production 수정은 필요하지 않았다.

GPU·torch·Warp·Isaac Sim을 실행/초기화하지 않았고 학습·play·collection 측정도 하지 않았다. 표준 라이브러리 구문/AST·해시·공백 검사만 수행했다. 상속 선언에 따른 전체 구성 보존을 확인한 정적 검사이며 실제 Sim import/reset/step 검증은 미실행이다. 기존 부모의 실측 시간을 새 자식의 검증 결과로 사용하지 않는다. 환경 계약·활성 환경 안내·현재 인계·README를 갱신했다.

후속 문서 검증: 변경 Markdown5개 수식 검사 통과, 문서 저장소4개 파일의 내부378개·외부1개 링크 오류0, workspace/문서 저장소 `git diff --check` 통과.
