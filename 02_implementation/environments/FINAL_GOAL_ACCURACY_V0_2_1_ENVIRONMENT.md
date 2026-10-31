# Final GoalAccuracy v0_2_1 구현 계약

[환경 색인](../08_ACTIVE_ENVIRONMENTS.md) · [승인 명세](../../01_plan/environments/2026-10-31_FINAL_GOAL_ACCURACY_V0_2_1_SPEC.md) · [개발·검증 기록](../logs/2026-10-31_final_goal_accuracy_v0_2_1_implementation.md)

2026-10-31 구현. Gym ID는 `Isaac-Inspire-Final-GoalAccuracy-v0_2_1`, EnvCfg의 직접 부모는 `FinalGoalAccuracyV0_2EnvCfg`다. PPO experiment 이름은 `inspire_final_goal_accuracy_v0_2_1`이다.

## 변경 계약

| 항목 | v0_2 | v0_2_1 |
| --- | --- | --- |
| target_contact | 타겟 접촉 OR 목표 점유 | 실제 타겟–손 접촉만 |
| 접촉 weight / 임계값 | 1.45 / 0.01N | 동일 |
| 성공 timeout 보너스 | +30, XY 거리 < 0.02m | +75, XY 거리 <= 0.02m |
| 타겟 종류 | 생성 시 고정 | 첫 reset 및 매 reset 재추첨 |
| 타겟·장애물 배치, 목표 | 매 reset 재생성 | 부모 로직 유지 |

접촉 보상은 새 센서 데이터의 유한한 타겟–손 접촉력 norm이 임계값 이상일 때만 발생한다. 목표에 들어가 있어도 접촉이 없으면 0이다. 선반 또는 장애물에만 손을 비비는 경우 타겟 접촉 보상은 없다. 다른 부모 보상의 발생 여부는 별개다.

timeout 보너스는 기존 종료 term `target_goal_success_at_timeout`을 사용한다. `success_event`가 reward manager의 dt 곱을 상쇄하므로 마지막 transition에 +75가 한 번 지급된다. 다른 종료·보상·보상 순서·커리큘럼·제어·PPO 값은 보존한다. 목표 성공률 개선은 아직 검증하지 않았다.

## reset 타겟 풀

기존 후보를 중복 제거한 16개 물리 타겟을 미리 생성한다. cylinder와 cube, 기타 그룹의 확률은 각각 1/3이며 기타 그룹 안에서는 기존 14개 후보를 균등 추첨한다. 연속 동일 종류가 나오는 것은 허용한다. 후보별 ±10% geometry scale은 생성 시 고정이며 reset마다 다시 스케일링하지 않는다. 장애물 종류 역시 부모 방식대로 생성 시 결정된다.

MDP에는 선택된 타겟을 항상 논리 object 0으로 제공한다. 타겟 선택 직후 bounds·scale·기본 질량·관성을 갱신하고 부모 배치 및 물성 reset을 실행한다. pose·velocity 쓰기, 물성 쓰기, 선택 타겟 접촉 센서도 같은 물리 인덱스로 매핑한다. 부분 reset은 지정 env만 변경한다. seed 지정 reset은 별도 타겟 추첨기를 재시드한다.

논리 용량은 타겟 1 + 장애물 20 = 21개로 유지된다. 실제 생성 rigid body는 타겟 16 + 장애물 20 = 36개다. 관측은 policy 57D, obstacles 80D, privileged 3D 그대로다. `target_kind_id`는 진단용이며 정책 입력에 추가하지 않는다. 장애물 요청 수 상한 Gray 4 / White 5 및 5000 iteration까지의 부모 일정도 유지한다.

## 비선택 후보 격리와 비용

실행 중 actor 비활성화 또는 collider 변경을 시도한 별도 GPU probe에서 실패가 발생했다. 구현은 물리 인덱스를 고정하고 비선택 후보를 z=110m의 서로 떨어진 위치에 놓으며 속도를 초기화하고 중력을 끈다. 논리 상태·보상·관측에서는 제외한다. **collision enabled 플래그 자체를 끄는 구현은 아니다.** 이는 승인 명세의 격리 목적을 충족하기 위한 구현 조정이며, 명세의 collider 비활성화 표현과 구분한다.

타겟 후보 15개와 접촉 센서·필터가 추가되므로 메모리 및 물리 연산 비용은 부모보다 증가할 수 있다. 4500 iteration에서 후보 풀이 커지거나 새 actor를 생성하지 않는다. 대규모 환경에서 collection 시간 및 메모리 비교는 미검증이다.

## 검증 및 실행

Windows 11 / conda `env_isaaclab`에서 CPU 회귀 78개 통과. 실제 CUDA 환경 2개에서 40회 부분 reset, 0/4000/4500/5000 iteration 설정, step의 유한한 보상, 관측 차원, 비선택 후보 격리를 확인했다. 16개 후보를 모두 강제 선택하여 reset·step 및 비선택 후보의 손 접촉력이 0임을 확인했다. 부모 설정 격리와 PPO 차이도 확인했다.

정책 학습·성공률·실제 선반 마찰 행동 개선·대규모 성능은 미검증이다. 다음 명령은 학습 시작 예시이며 이 작업에서 실행하지 않았다. 환경 수는 장치 용량에 맞게 조절한다.

```powershell
conda activate env_isaaclab
python src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Final-GoalAccuracy-v0_2_1 --num_envs 256 --headless
```
