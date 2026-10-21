# Clutter Fusion — 독립 환경과 가림 관측·보상·커리큘럼

[활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [개발 로그](README.md) · [소스](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion)

## 요청과 기준

2026-10-21 사용자는 Clutter Curriculum v1과 Clutter v2를 융합하되 기존 환경/Cfg 상속을 끊는 새 환경을 요청했다. Workspace 기준 commit은 `0e314e91686e8a7b10a8b081d97e776c86cc1479`, 문서 submodule은 `a953e0a880d881f375b665892b382c0d924dfeeb`다. 두 저장소 모두 기존 수정과 미추적 파일이 있었으며 보존했다. 기존 F/T 수집·가시성 구현을 읽기 전용으로 재사용하고 학습 로그는 읽기만 했다.

사용자 후속 확인으로 아래 의미를 확정했다.

- Goal은 초기 타겟→기존 목표점의 변위를 robot-root 축으로 표현한다. 기존 root 원점→goal 관측과 원점 의미는 다르지만 좌표축과 실제 목표점은 유지한다.
- Joint velocity는 Arm −0.03·Hand −0.01로 고정하며 이전 Arm joint velocity 가중치 커리큘럼을 제거한다.
- EEF 속도는 기존 `arm_speed_excess`의 지수식·가중치 −1·cost 상한 100을 사용한다.
- Orientation은 하늘과 EEF +Z 사이 각도 60°부터 시작하여 0°에서 최대다. 약 1%는 기존 로그로 고정 가중치를 산정하는 규모 기준이며 동적 1% 예산이 아니다.
- F/T는 기존 v2 제곱식 항을 대체한다. 제안한 변화율 임계값과 기존 −0.1/초·누적 양의 보상 5% 상한을 승인했다.
- 관측 폭 35%, reset 때 실제 장애물별 1% flip, 두 Contact 항 각각 10배를 승인했다. Goal deadzone 첫 축소는 iteration 1200, 제거 완료는 13000이다.

## 등록·상속·제어

Task는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v0`다. `inspire_sweep_baseline.contact_sweep_clutter_fusion` 안에서 runtime `env:ContactSweepClutterFusionEnv`는 `ManagerBasedRLEnv`를, `env_cfg:ContactSweepClutterFusionEnvCfg`는 `ManagerBasedRLEnvCfg`를 직접 상속한다. Scene은 `InteractiveSceneCfg`, Observation group은 `ObservationGroupCfg`, PPO는 `RslRlOnPolicyRunnerCfg`를 직접 사용한다. 나머지 Manager Cfg는 독립 configclass다.

기존 task Env/Cfg를 상속하지 않는다. 기존의 MDP 함수·센서 term·장면 생성기·학습 iteration runner는 재사용한다. 원래의 raw action/velocity 제곱합 함수를 각각 호출한 뒤 합치며, 새 환경에서만 사용자 지시대로 Manager 항을 통합한다. 이전 Omni 및 Clutter 환경의 네 항 계약은 바꾸지 않는다.

Arm 6D default-offset Joint Position(scale 0.5), Hand 2D openness, 100 Hz 물리·50 Hz 제어, 최대 10초 episode, 네 실린더·촉각 filter·질량/마찰 랜덤화·실패 종료를 유지한다. `CurriculumOnPolicyRunner`가 rollout 전에 zero-based learning iteration을 적용하고 checkpoint load 시 복원한다. 새 PPO Cfg는 `ContactSweepClutterFusionPPORunnerCfg`, experiment name은 `inspire_contact_sweep_clutter_fusion`이다.

## 관측 계약

| 그룹 | 순서와 차원 |
| --- | --- |
| policy 55D | Arm position 6, Arm velocity 6, last action 8, 초기 target XYZ 3, EEF pose 7, goal distance/theta 2, tactile bit 17, 보정 wrist wrench 6 |
| obstacles 40D | 10 × [present, root X, root Y, root Z]. 물리 장애물 3개와 padding 7개 |
| privileged 3D | 현재 target root XYZ, Critic 전용 |

Target width는 제거했다. 타겟의 초기 위치 오차는 기존 episode-fixed ±1 cm 방식이다. Goal 입력은 초기 타겟→goal 벡터를 root 축으로 회전한 뒤 XY norm(m), `atan2(-dy, dx) mod 2π`(rad)로 표현한다. 밀기 0, 오른쪽 π/2, 당기기 π, 왼쪽 3π/2다. 현재 target 위치를 사용하지 않으며 실제 absolute goal command와 보상 목표는 바꾸지 않는다.

가림은 `scene_randomization.visibility.classify_visibility_torch`를 reset마다 한 번 호출한다. 정면 투영에 전체 네 물체를 포함하고 가시 폭 비율 35% 이상인 장애물을 관측한다. 실제 장애물 세 개의 가시성에 각각 Bernoulli(0.01) XOR를 적용한다. 숨긴 슬롯의 네 값은 모두 0이며 padding은 flip하지 않는다. 물리적 장애물과 다른 물체를 가리는 효과는 그대로 남는다. 관측 중에는 이 캐시만 읽으므로 매 step의 기하 판정·추가 시각 추적이 없다.

F/T는 v2 `PureWristWrench`를 그대로 사용한다. Hand 중력·관성 하중을 제거한 EEF 기준점·EEF 축의 6D 반력이다. Actor raw 입력은 95D, Critic은 98D다. 각 40D 장애물 encoder가 별도로 16D를 만들므로 신경망 입력은 Actor 71D·Critic 74D다. 이전 57D policy checkpoint와 입력 계약이 다르므로 새 환경에서 학습한 checkpoint를 사용한다.

## 보상

| 항 | 가중치·의미 |
| --- | --- |
| reaching / goal_distance / goal_hold | 30 / 100 / 0.9, 기존 함수 |
| contact_any / contact_count | 각각 0.16→1.6, 함수는 유지 |
| action_rate | −0.03→−0.06, Arm capped square sum + Hand capped square sum |
| joint_velocity | −0.03 × (Arm capped square sum + Hand capped square sum / 3) |
| object | −30 × (모든 물체 tilt cost + 2.5 × 장애물 displacement cost) |
| shelf_collision / shelf_failure | −0.5 / −3, 기존 함수 |
| pushing_speed / arm_speed_excess | −2 / −1, free speed만 새 curriculum |
| eef_linear_speed | −1, 실제 EEF 점의 3D 선속도에 지수 비용·raw 상한 100 |
| eef_orientation | −0.02, 위쪽 EEF +Z cone의 유한 [0,1] 제곱 비용 |
| wrench_change | −0.1, 아래의 유한 지수 변화율 비용·누적 양의 보상 5% 이내 |

통합하기 전 Arm/Hand raw 제곱합의 각각 100 상한을 유지한다. 합친 후 100으로 다시 자르지 않는다. 따라서 iteration 0의 Action·Joint 보상은 기존 두 항 합과 같고, object 보상은 기존 tilt와 displacement 각각 15배와 같다. Displacement 상한은 기존 0.04 m²를 유지한다. RewardManager가 dt를 한 번 적용하며 shelf failure의 일회성 −3 처리도 유지한다.

EEF 속도는 `axia80_link`의 link-origin 선속도에 각속도와 EEF offset의 외적을 더해 계산한다. COM 속도나 프레임 간 위치 유한차분을 대용하지 않는다. 비용은 `min(0.5 * expm1(2 * max(speed-free_speed,0)),100)`이고 지수 입력부터 제한하여 발산을 막는다.

Orientation에서 `c`는 EEF +Z와 world +Z의 내적이다. `clamp((c-0.5)/0.5,0,1)^2`를 사용한다. 반대 방향 및 60° 밖에는 비용이 없다. 기존 `logs/inspire_contact_sweep_clutter_v1_curriculum/2026-10-20_22-49-30`의 iteration 12300–12800, 501개 `Train/mean_reward` 평균은 약 17.1309였다. 가중치 −0.02는 10초 내내 최악 자세여도 누적 −0.2로 이 기준의 약 1.17%다. 당시 평균 episode는 1.9075초였으므로 그 길이에서의 최대는 약 0.0382다. 향후 실제 보상 대비 정확한 1%를 보장하지 않는다.

## F/T 계수 근거

입력은 사용자가 지정한 `outputs/clutter_ft/2026-10-21_curriculum_model12800_dataset_rates`와 원본 CSV다. 50 Hz 제어 주기에서 유효 rate 79,233행을 사용하고 첫/reset 경계 767행을 제외한다. 힘와 모멘트는 각각 N/s·N·m/s로 처리하며, EEF 축의 회전으로 생기는 변화가 섞이지 않도록 보정된 world axes를 사용한다. 모멘트 기준점은 기존처럼 움직이는 EEF다.

| 분포 | 힘 변화율 | 모멘트 변화율 |
| --- | --- | --- |
| 전체 P95 | 약 280 N/s | 약 16.5 N·m/s |
| 전체 P99 | 약 2327 N/s | 약 96.5 N·m/s |
| 촉각 첫 ON 표본 P95, n=422 | 약 1878 N/s | 약 98 N·m/s |

무료 구간은 힘 2000 N/s·모멘트 100 N·m/s이며 상한 도달 지점은 5000 N/s·250 N·m/s다. 두 축의 정규화 초과량 중 큰 값을 `x`라 하면 raw cost는 `expm1(3*clamp(x,0,1))/expm1(3)`이다. 20 ms 기준 무료 변화량은 40 N·2 N·m, 상한 변화량은 100 N·5 N·m다. 첫 유효 표본은 history만 설정하고 부분 reset·invalid 표본은 경계를 넘어서 차분하지 않는다.

이 후보식은 촉각 첫 ON 표본의 약 93.84%에 비용 0을 부여하고, 전체 표본의 약 1.277%에서 활성화·0.540%에서 raw 상한에 도달한다. 첫 ON은 정상 접촉의 대리 표지이며 비촉각 영역 접촉이나 보정 오차를 구분하는 정답이 아니다. 이 자료만으로 허용/불허 접촉의 정확한 분리를 주장하지 않는다.

[계수 분석 스크립트](../../../../outputs/clutter_fusion_design/analyze_wrench_rates.py) · [분포·원본 해시·후보식 결과](../../../../outputs/clutter_fusion_design/wrench_rate_evidence.json) · [자세 계수 스크립트](../../../../outputs/clutter_fusion_design/calibrate_orientation_weight.py) · [자세 계수 근거](../../../../outputs/clutter_fusion_design/orientation_weight_evidence.json)

## 커리큘럼

| 항 | 시작 | 변화 | 최종·도달 iteration |
| --- | --- | --- | --- |
| pushing free speed | 0.1 m/s | 500마다 −0.01 | 0.05, 2500 |
| arm free speed | 1.0 rad/s | 500마다 −0.02 | 0.8, 5000 |
| 통합 action weight | −0.03 | 500마다 −0.005 | −0.06, 3000 |
| EEF free speed | 1.5 m/s | 500마다 −0.02 | 0.7, 20000 |
| Goal ±X deadzone 반각 | 각각 60° | 1000까지 유지, 1200부터 200마다 −1° | 0°, 13000 |

일정은 현재 iteration에서 절대값으로 재계산한다. reset 횟수로 진도를 누적하지 않는다. Goal 변경은 다음 episode 배치에만 적용하며 이미 생성한 goal을 움직이지 않는다. Joint velocity 가중치 curriculum은 없다. Checkpoint load 전에 만들어진 첫 episode의 목표도 유지하고, 다음 reset부터 복원한 단계의 goal 분포를 사용한다.

## 실행

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v0 --num_envs 2048 --headless

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/play.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v0 --num_envs 1 \
  --checkpoint "<fusion-checkpoint.pt>"
```

## 실제 검증과 한계

현재 호스트의 Torch 2.7.0+cu128·RSL-RL 5.0.1·Isaac Sim 5.1.0 환경을 사용했다. 일반 sandbox에서는 CUDA가 보이지 않아 GPU 검증은 승인된 외부 실행으로 수행했다. 라이브러리 설치·기존 학습 로그 수정은 하지 않았다.

CPU 전체 패키지 검사:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests
```

**440 passed, 3 warnings, 9.77 s.** 새 Fusion 검사 60개를 포함한다. 보상 합 동등성·각 그룹의 상한·15배/10배·가림 양방향 flip·부분 reset·현재 타겟 정보 차단·Goal frame·curriculum 경계·실제 RewardManager의 F/T 예산·EEF quaternion/점 속도·실제 CPU PPO·checkpoint 복원·JIT/ONNX export가 포함된다. 경고 3개는 Torch ONNX deprecation이다.

최초 지정된 `env_isaaclab` Python에는 Torch/NumPy가 없어 기존 수집에 사용했던 `jd_isaaclab`으로 전환했다. 개발 중 model test fixture의 RSL-RL config compatibility 누락, 재사용 sensor term의 import를 CFG 상속으로 잘못 판단한 검사, 오류 메시지 순서 assertion을 수정한 뒤 전체 검사를 통과했다. 기존 task 코드는 수정하지 않았다.

실제 GPU 통합 검사:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  INSPIRE_SWEEP_SHELF_USD_PATH=/home/ssu/Desktop/Contact-Manipulation/asset/Shelf_USD/Arena/Collected_speedrack_shape/speedrack_shape.usd \
  /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/tests/_clutter_fusion_probe.py \
  --headless --num_envs 4 --output outputs/clutter_fusion_validation/probe.json \
  > outputs/clutter_fusion_validation/probe.log 2>&1
```

[최종 JSON](../../../../outputs/clutter_fusion_validation/probe.json)·[stdout](../../../../outputs/clutter_fusion_validation/probe.log): **passed, exit 0**. Seed 42·4환경에서 실제 독립 상속, 기존 Scene/Action/Command/Termination 동등성, policy55/obstacles40/privileged3, 15개 보상 계수, 9개 curriculum 단계, 목표 불변·reset 방향 범위, 18개 물리 제어 step, EEF 속도의 독립 COM transport 대조, F/T 원본 term 공유, 부분/자동 reset을 확인했다. 이어서 PPO iteration 499→500, 각각 4 rollout step·1 epoch·1 minibatch를 실제 실행하여 encoder 업데이트와 커리큘럼 경계를 통과했다. 이 검증 checkpoint는 새 outputs 폴더에만 저장하고 runner의 log_dir는 None이다.

첫 GPU 실행은 환경·센서·커리큘럼 검사를 통과한 뒤 검증 스크립트의 `inference_mode`에서 생성된 lazy physics tensor를 이후 wrapper reset이 수정하면서 실패했다. 검증 구간을 `no_grad`로 고쳐 실제 학습 단계와 연결한 뒤 재실행하여 통과했다. [첫 실패 JSON](../../../../outputs/clutter_fusion_validation/probe_initial_failure.json)·[첫 stdout](../../../../outputs/clutter_fusion_validation/probe_initial_failure.log)은 보존했다. 환경 소스의 회피성 물리 수정은 하지 않았다.

RTX PRO 6000에서 네 물체의 가림 classifier를 20회 측정한 평균은 **4096환경 0.321 ms, 10000환경 0.322 ms**였다. 이는 반복한 유효 장면 batch의 classifier 시간이며 CPU 장애물 배치·reset 전체 시간을 뜻하지 않는다. 매 step에는 classifier를 실행하지 않는다. CPU 전체 visibility helper(1 thread, 준비 10회/측정 100회)의 중앙값은 4096환경 3.174 ms, 10000환경 7.254 ms였다.

GPU의 정지 명령 구간 최대 EEF 속도는 약 0.0119 m/s였고 F/T 비용은 0이었다. 따라서 큰 변화율에서의 비용 증가·극값 상한은 합성 표본의 CPU 수학·실제 RewardManager 검사로 확인한 범위이며 GPU 고충격 접촉을 새로 검증한 것은 아니다. 짧은 PPO는 학습 연결 확인일 뿐 수렴·성공률·자세 개선·F/T 억제 성과를 뜻하지 않는다. 기존 57D 정책 성능 유지, 새 장시간 학습, 실물 캔슬레이션은 미검증이다.

문서 검사(문서 submodule에서 실행):

```bash
python 00_guidelines/scripts/check_markdown_math.py 01_plan/00_HANDOFF_BRIEF.md 01_plan/04_NEXT_ACTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-21_clutter_fusion.md ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external 01_plan/00_HANDOFF_BRIEF.md 01_plan/04_NEXT_ACTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-21_clutter_fusion.md ../../src/inspire_sweep_baseline/README.md
git diff --check
```

수식 검사 6개 파일 통과, 링크 검사 오류 0개(내부 214·외부 workspace 참조 68), Workspace와 문서 submodule의 `git diff --check` 모두 통과했다. 기존 사용자 수정과 문서 색인의 기존 충돌 표시는 별도 정리하지 않았다.
