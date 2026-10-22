# Contact Sweep Clutter Fusion v1_3_1

[환경 안내](README.md) · [버전 비교](CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md) · [구현·검증](../logs/2026-10-22_clutter_fusion_v1_3_1.md)

Task ID는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3_1`다. 초기 접촉 탐색을 허용하면서 장애물 접촉 힘·물체 가속도·wrench 변화의 무료 기준을 매 iteration 구간별 선형 보간으로 낮추는 환경이다. 학습 개선 여부는 아직 검증하지 않았다.

## 구성과 입력·행동

고정 base UR5e와 Inspire Hand가 선반 위 원통형 타겟을 지정된 world XY 목표로 민다. 원통은 반경 4cm·높이 10cm이며 목표 거리 설정은 15cm다. 시작 배치는 Gray 장애물 1개, White 장애물 1개, 타겟 1개다. White는 3000·6000, Gray는 4500·7500 iteration에서 하나씩 늘어 최종 3+3+1개가 된다. 비활성 슬롯은 물리 보상·종료·관측에서 제외한다. 개수 변경은 각 환경의 다음 reset에 적용된다.

Actor 입력은 policy 55D와 초기 장애물 40D이고, Critic에는 현재 타겟 XYZ 3D가 추가된다. policy는 고유감각·초기 타겟·목표·17개 tactile bit·보정 EEF wrench를 사용한다. 장애물 관측은 reset 시 가시성·노이즈를 반영한 뒤 root −Y 오름차순으로 압축하고 점유 인접 슬롯을 왼쪽부터 10% 확률로 순차 교환한다. 실행 중 시각 위치를 갱신하지 않는다.

Action은 Arm 6D와 Hand 2D, 총 8D다. Arm은 기본 관절각에 scale 0.5를 적용한 관절 위치 명령, Hand는 [0,1]로 제한한 열림·닫힘 목표 보간이다. 물리 100Hz, 정책 50Hz, episode 최대 10초다.

## 보상

총 17개 항이다. Goal hold 인정 반경은 초기2cm, 5000까지 유지 후10000에서1cm,20000에서0.5cm로 선형 감소한다. 접촉 fade width는 초기0.001m,5000까지 유지 후10000에서0.01m로 선형 증가한다. alpha=clamp((d−r)/width,0,1)이며 d는 world XY 목표 거리, r은 현재 Goal hold 반경이다. Goal 설정을 매 계산에서 직접 읽어 커리큘럼과 동기화한다.

| 항목 | Weight | 계산·무료 기준 |
| --- | ---: | --- |
| reaching | 30 | EEF–물체 거리 최고 기록 개선, near radius 10cm |
| goal_distance | 100 | 목표 XY 거리 최고 기록 개선, tolerance 1cm |
| goal_hold | 0.9 | 위 인정 반경 안에서 매 step 지급 |
| hand_contact | 0.29 | 손 전체 합력 norm ≥0.01N인 유효·fresh 표본에 alpha 적용 |
| arm_action_rate / hand_action_rate | −0.03 / −0.03 | raw Action 변화 제곱합, 각 raw cap 100 |
| arm_joint_velocity / hand_joint_velocity | −0.03 / −0.01 | 실제 관절 속도 제곱합, 각 raw cap 100 |
| object | −30 | 모든 활성 물체 기울기 + 2.5×장애물 변위 제곱합(cap 0.04) |
| shelf_collision | −0.5 | 선반 움직임·손가락/손목 근접 |
| pushing_speed | −5 | 타겟 3D 속도 무료 0.1→0.03m/s |
| arm_speed_excess | −1 | 최대 Arm 관절 속도 무료 1→0.7rad/s |
| shelf_failure | −3 | 선반 실패 사건 |
| eef_linear_speed | −1 | EEF 3D 선속도 무료 1.5→0.3m/s |
| obstacle_contact | −1 | 비타겟 접촉 합력 크기 무료 200→100→50N |
| object_acceleration | −1 | PhysX COM 3D 가속도 norm, 물체별 무료 100→20→10→5m/s² |
| wrench_change | −0.1 | abs(현재 norm−이전 norm), 무료 힘 1000→500→100→5N·모멘트 100→50→10→0.5Nm |

접촉 보상은 목표 물체 외의 접촉도 인정한다. 가속·감속은 같은 비용이다. 비타겟 힘·가속도·속도 비용은 무료 기준 초과량에 지수적으로 증가하며 raw cap 100이다. 가속도는 물체별 비용을 합한다. Wrench는 관측과 같은 EEF 기준 표본이며 raw cap 1, 누적 양의 보상 5% 예산 제한을 유지한다. RewardManager는 weight와 dt를 한 번 적용하고, 거리 개선 보상 함수는 dt를 상쇄하여 weight가 거리당 보상이 되도록 한다.

## 커리큘럼과 종료

새 무료 기준은 다음 point를 사용한다. 첫 point까지 초기값을 유지하고 각 point 사이를 선형 보간하며 마지막 point 이후는 최종값을 유지한다. 250 iteration 주기나 계단은 없다. 매 학습 iteration에 갱신한다.

| 무료 기준 | Points (iteration, 값) |
| --- | --- |
| 장애물 힘 N | (1000,200), (5000,100), (10000,50) |
| Wrench 힘 변화 N | (1000,1000), (5000,500), (10000,100), (20000,5) |
| Wrench 모멘트 변화 Nm | (1000,100), (5000,50), (10000,10), (20000,0.5) |
| 물체 가속도 m/s² | (2000,100), (5000,20), (10000,10), (20000,5) |

구간 왼쪽을 (a,x), 오른쪽을 (b,y), 현재 iteration을 i라고 하면 `x + (y-x)*(i-a)/(b-a)`다. 따라서 첫 point에서 값이 갑자기 감소하지 않는다. 절대 iteration으로 계산하므로 checkpoint 복원·되감기·부분 reset에도 같은 값이다. Goal hold points는(5000,0.02),(10000,0.01),(20000,0.005)m, contact fade width points는(5000,0.001),(10000,0.01)m다. 커리큘럼은 총11항이다. Goal progress 자체 tolerance는1cm로 유지하며 Goal hold와 별개다.

기타 일정: 타겟·Arm·EEF 무료 속도는 500부터 200마다 각각 0.01·0.02·0.02 감소한다. 목표 방향 dead zone은 30°로 3000까지 유지, 3500부터 500마다 5° 감소하여 6000에서 0°다.

종료 조건은 시간 만료, 활성 물체 낙하/0.9rad 이상 기울기, 타겟 속도 0.8m/s 초과, 선반 속도/손목 3cm clearance 위반, Arm 관절 속도 5rad/s 초과, 선반 변위 5cm 초과의 6개다. Goal 도달로 즉시 종료하지 않는다. 장애물 변위·기울기 비용과 속도·높이 종료는 여전히 활성화되어 있다.

## PPO와 실행

Actor/Critic [256,128,64] ELU, 장애물 [32]→16 인코더, 초기 Gaussian std 1.0, rollout 36, epoch 8, minibatch 4, learning rate 0.001 adaptive, gamma 0.98, lambda 0.95, entropy 0.005, PPO clip 0.2다. 자동 복구 launcher는 checkpoint iteration의 커리큘럼을 적용한 뒤 reset한다.

Workspace 루트에서:

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train_resilient.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3_1 \
  --num_envs 2048 --headless --max_iterations 90000
```

실행 코드는 공용 `ContactSweepClutterFusionV1_0Env`, 설정은 `ContactSweepClutterFusionV1_3_1EnvCfg`, PPO는 `ContactSweepClutterFusionV1_3_1PPORunnerCfg`다. 보상·커리큘럼 CFG는 독립 선언이다. [소스](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_3_1/env_cfg.py)를 기준으로 한다. IsaacLab·Sim 실행과 실제 학습은 이번 작업에서 수행하지 않았다.
