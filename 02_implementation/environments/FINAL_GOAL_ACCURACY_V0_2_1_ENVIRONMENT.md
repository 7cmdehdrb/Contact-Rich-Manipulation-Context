# Final GoalAccuracy v0_2_1 구현 계약

[환경 색인](../08_ACTIVE_ENVIRONMENTS.md) · [승인 명세](../../01_plan/environments/2026-10-31_FINAL_GOAL_ACCURACY_V0_2_1_SPEC.md) · [개발·검증 기록](../logs/2026-10-31_final_goal_accuracy_v0_2_1_implementation.md)

2026-10-31 구현. Gym ID는 `Isaac-Inspire-Final-GoalAccuracy-v0_2_1`, EnvCfg의 직접 부모는 `FinalGoalAccuracyV0_2EnvCfg`다. PPO experiment 이름은 `inspire_final_goal_accuracy_v0_2_1`이다.

2026-10-31 후속: [OBB 배치 규칙](BBOX_SCENE_LAYOUT.md)을 이 환경의 reset에 적용했다. [연결 변경·검증 기록](../logs/2026-10-31_final_v0_2_1_obb_reset.md)을 따른다. 다른 버전의 배치 함수는 유지한다.

## 변경 계약

| 항목 | v0_2 | v0_2_1 |
| --- | --- | --- |
| target_contact | 타겟 접촉 OR 목표 점유 | 실제 타겟–손 접촉만 |
| 접촉 weight / 임계값 | 1.45 / 0.01N | 동일 |
| 성공 timeout 보너스 | +30, XY 거리 < 0.02m | +75, XY 거리 <= 0.02m |
| 타겟 종류 | 생성 시 고정 | 첫 reset 및 매 reset 재추첨 |
| 타겟·장애물 배치, 목표 | 원형 존 생성 후 OBB 검사 | 실제 bounds 기반 명령·OBB 존·최소 간격을 텐서로 생성 |

접촉 보상은 새 센서 데이터의 유한한 타겟–손 접촉력 norm이 임계값 이상일 때만 발생한다. 목표에 들어가 있어도 접촉이 없으면 0이다. 선반 또는 장애물에만 손을 비비는 경우 타겟 접촉 보상은 없다. 다른 부모 보상의 발생 여부는 별개다.

timeout 보너스는 기존 종료 term `target_goal_success_at_timeout`을 사용한다. `success_event`가 reward manager의 dt 곱을 상쇄하므로 마지막 transition에 +75가 한 번 지급된다. 다른 종료·보상·보상 순서·커리큘럼 수치·제어·PPO 값은 보존한다. Gray padding 일정의 기하 해석 변경은 아래에 명시한다. 목표 성공률 개선은 아직 검증하지 않았다.

## reset 타겟 풀

기존 후보를 중복 제거한 16개 물리 타겟을 미리 생성한다. cylinder와 cube, 기타 그룹의 확률은 각각 1/3이며 기타 그룹 안에서는 기존 14개 후보를 균등 추첨한다. 연속 동일 종류가 나오는 것은 허용한다. 후보별 ±10% geometry scale은 생성 시 고정이며 reset마다 다시 스케일링하지 않는다. 장애물 종류 역시 부모 방식대로 생성 시 결정된다.

MDP에는 선택된 타겟을 항상 논리 object 0으로 제공한다. 타겟 선택 직후 bounds·scale·기본 질량·관성을 갱신하고 새 OBB 배치 및 부모 물성 reset을 실행한다. pose·velocity 쓰기, 물성 쓰기, 선택 타겟 접촉 센서도 같은 물리 인덱스로 매핑한다. 부분 reset은 지정 env만 변경한다. seed 지정 reset은 별도 타겟 추첨기와 device 배치 추첨기를 재시드한다.

## OBB reset과 수량 일정

전용 adapter는 `mdp/common/final_obb_geometry.py`다. 실제 scale이 적용된 로컬 bounds를 초기화 때 device tensor로 보관하고, 매 reset 선택된 타겟의 bounds만 갱신한다. 비대칭 박스의 중심 offset을 회전시켜 선반 좌표와 board 좌표를 변환한 뒤 실제 root pose로 되돌린다. 높이는 각 물체의 실제 min-z로 정한다. 배치 실패 슬롯은 물체 정체성을 보존한 채 비활성화하며 actual count와 기존 로그에 반영한다.

기본 최소 간격은 20mm, Gray 바깥 padding은 60mm, 경계 여유는 장애물 5mm다. 후보 32 × restart 4 × pass 2의 제한 탐색 중 최다 배치를 사용한다. 기존 `gray_red_padding_fraction`의 4000→10000 iteration, 0→0.15 일정은 유지하지만, 새 규칙에서는 `gray_padding × (1 + fraction)`으로 **60→69mm 바깥 확장**한다. RED는 축소하지 않는다.

타겟 root의 기본 2cm 원판 분포, yaw=0, 목표 최대 15cm·최소 5cm, 목표 방향 제외각 커리큘럼은 유지한다. 원형 물체를 가정한 안전 영역만 실제 bounds 및 기존 목표 root 한계의 교집합으로 교체한다. 장애물 배치 실패 때문에 타겟·목표를 다시 뽑지 않는다.

| iteration 구간 | Gray 요청 | White 요청 |
| --- | --- | --- |
| 0–1999 | 1 | 1 |
| 2000–2499 | 1 | 2 |
| 2500–2999 | 2 | 2 |
| 3000–3499 | 2 | 3 |
| 3500–3999 | 3 | 3 |
| 4000–4499 | 3 | 4 |
| 4500–4999 | 4 | 4 |
| 5000 이후 | 4 | 5 |

증가 시작과 1000 iteration 간격은 기존과 같다. 상한은 자식 EnvCfg에도 4/5로 명시했다. 물리 용량·관측 슬롯을 9개로 줄인 것은 아니다. 공간 부족 시 실제 생성 개수는 요청보다 적을 수 있다.

논리 용량은 타겟 1 + 장애물 20 = 21개로 유지된다. 실제 생성 rigid body는 타겟 16 + 장애물 20 = 36개다. 관측은 policy 57D, obstacles 80D, privileged 3D 그대로다. `target_kind_id`는 진단용이며 정책 입력에 추가하지 않는다. 장애물 요청 수 상한 Gray 4 / White 5 및 5000 iteration까지의 부모 일정도 유지한다.

## 비선택 후보 격리와 비용

실행 중 actor 비활성화 또는 collider 변경을 시도한 별도 GPU probe에서 실패가 발생했다. 구현은 물리 인덱스를 고정하고 비선택 후보를 z=110m의 서로 떨어진 위치에 놓으며 속도를 초기화하고 중력을 끈다. 논리 상태·보상·관측에서는 제외한다. **collision enabled 플래그 자체를 끄는 구현은 아니다.** 이는 승인 명세의 격리 목적을 충족하기 위한 구현 조정이며, 명세의 collider 비활성화 표현과 구분한다.

타겟 후보 15개와 접촉 센서·필터가 추가되므로 메모리 및 물리 연산 비용은 부모보다 증가할 수 있다. 4500 iteration에서 후보 풀이 커지거나 새 actor를 생성하지 않는다. 대규모 환경에서 collection 시간 및 메모리 비교는 미검증이다.

## 검증 및 실행

OBB 연결 후 회귀·기하 검사 106개와 실제 GPU 2 env의 40회 부분 reset·16종 타겟 검사를 통과했다. reset 물리 pose의 독립 다각형 검증 및 수량 커리큘럼 경계 검사를 포함한다. 상세 결과는 [OBB 연결 기록](../logs/2026-10-31_final_v0_2_1_obb_reset.md)을 따른다. 아래 78개 결과는 최초 버전 구현 당시 기록이다.

Windows 11 / conda `env_isaaclab`에서 CPU 회귀 78개 통과. 실제 CUDA 환경 2개에서 40회 부분 reset, 0/4000/4500/5000 iteration 설정, step의 유한한 보상, 관측 차원, 비선택 후보 격리를 확인했다. 16개 후보를 모두 강제 선택하여 reset·step 및 비선택 후보의 손 접촉력이 0임을 확인했다. 부모 설정 격리와 PPO 차이도 확인했다.

정책 학습·성공률·실제 선반 마찰 행동 개선·대규모 성능은 미검증이다. 다음 명령은 학습 시작 예시이며 이 작업에서 실행하지 않았다. 환경 수는 장치 용량에 맞게 조절한다.

```powershell
conda activate env_isaaclab
python src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Final-GoalAccuracy-v0_2_1 --num_envs 256 --headless
```
