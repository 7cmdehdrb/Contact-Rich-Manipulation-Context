# Contact Sweep Clutter Fusion v1_1_1

[환경 목록](README.md) · [버전 비교](CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md) · [검증 기록](../logs/2026-10-22_clutter_fusion_v1_1_1.md)

Task ID: `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1_1`. 장애물 접촉 힘과 wrench 변화 비용의 무료 기준을 크게 고정하고, 물체 가속도 커리큘럼을 적용하는 접촉 학습 실험 환경이다.

## 보상과 커리큘럼

| 항목 | 설정 |
| --- | --- |
| Goal hold | 반경1cm 고정, weight0.9, 반경 커리큘럼 없음 |
| Hand contact | 무료 힘이 아닌 접촉 판정 임계값0.01N, weight0.29, fade width0으로 alpha=1 |
| 장애물 접촉 | 무료 힘2000N 고정, weight−1, 커리큘럼 없음 |
| 물체 가속도 | 무료100→5m/s², weight−1, 1000에서 첫 감소·250마다·20000에서5 |
| Wrench 크기 변화 | abs(현재 norm−이전 norm), 무료5000N/500Nm 고정, weight−0.1, 커리큘럼 없음 |

가속도는 PhysX COM 3차원 가속도 norm이며 가속·감속 모두 포함한다. 1000~20000의77회에 균등 감소하므로 회당95/77m/s² 감소한다. 1000 이전만100이며, 20000 이후5로 고정한다. 절대 iteration으로 재계산하므로 checkpoint 복원·되감기에 맞춰 적용된다. 장애물 힘·가속도 비용은 raw cap100(가속도는 물체별), wrench는 raw cap1과 누적 양의 보상5% 예산 제한을 유지한다. 큰 무료 기준은 비용 삭제가 아니며 초과 충격은 여전히 벌점이다.

나머지 보상은 접근30, 목표 거리 개선100(tolerance1cm), Arm/Hand action 변화−0.03/−0.03, Arm/Hand 실제 관절 속도−0.03/−0.01, 물체 기울기·장애물 변위−30, 선반 근접·움직임−0.5, 타겟 속도−5, Arm 속도 초과−1, 선반 실패−3, EEF 속도−1이다. 총17항이다. raw 제곱합 운동 비용과 속도 비용의 상한은100이다.

커리큘럼6항: 장애물 개수, 타겟 무료 속도0.1→0.03m/s, Arm 무료 속도1→0.7rad/s, EEF 무료 속도1.5→0.3m/s, Goal dead zone30→0°, 물체 무료 가속도다. 세 속도 일정은500부터200마다 감소한다. Dead zone은3000까지 유지하고3500부터500마다5° 감소한다. White 장애물은3000·6000, Gray는4500·7500에서 늘어나 시작1+1에서 최종3+3개가 된다.

## Scene·관측·행동·종료

고정 UR5e–Inspire Hand가 선반 위 반경4cm·높이10cm 원통을 민다. Actor는 policy55D와 초기 장애물40D, Critic은 현재 타겟XYZ3D를 추가한다. 초기 시각 관측은 episode 중 갱신하지 않으며17개 tactile bit와 보정 EEF wrench를 사용한다. 장애물 슬롯은 가시성 판정 후 root−Y 순서로 압축하고 점유 인접 쌍을10% 확률로 순차 교환한다.

Action8D는 Arm6D 기본각 대비scale0.5 관절 위치와 Hand2D [0,1] 열림·닫힘 보간이다. 물리100Hz·정책50Hz·최대10초 episode다. 종료6항은 timeout, 활성 물체 낙하/0.9rad 기울기, 타겟 속도0.8m/s 초과, 선반 움직임/손목3cm clearance, Arm 속도5rad/s 초과, 선반 변위5cm 초과다. 목표 도달은 즉시 종료가 아니다.

## PPO와 실행

Actor/Critic [256,128,64] ELU, 장애물 [32]→16 인코더, 초기 std1, rollout36, epoch8, minibatch4, learning rate0.001 adaptive, gamma0.98, lambda0.95, entropy0.005, PPO clip0.2다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train_resilient.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_1_1 \
  --num_envs 2048 --headless --max_iterations 90000
```

가속도 비용 외의 비용·종료 조건도 존재하므로 학습 실패만으로 가속도가 원인이라고 단정할 수 없다. 가속도 비용을 제외한 대조군과 비교해야 원인 분리가 더 명확해진다. 이번 구현에서 simulator·학습은 실행하지 않았다.
