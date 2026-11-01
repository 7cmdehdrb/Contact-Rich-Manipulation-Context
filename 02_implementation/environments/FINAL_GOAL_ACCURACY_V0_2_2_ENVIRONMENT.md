# Final GoalAccuracy v0_2_2 구현 계약

[환경 안내](../08_ACTIVE_ENVIRONMENTS.md) · [부모 v0_2_1](FINAL_GOAL_ACCURACY_V0_2_1_ENVIRONMENT.md) · [개발·검증 기록](../logs/2026-10-31_final_v0_2_2_compact_scene.md)

2026-10-31. `FinalGoalAccuracyV0_2_2EnvCfg`는 `FinalGoalAccuracyV0_2_1EnvCfg`를 직접 상속한다. Gym ID는 `Isaac-Inspire-Final-GoalAccuracy-v0_2_2`, PPO experiment 이름은 `inspire_final_goal_accuracy_v0_2_2`다. 기존 환경의 함수·설정은 수정하지 않았다.

## 목적과 보존 범위

사용자가 요구한 메모리 절약과 생성/reset 비용 감소를 위해, 타겟 후보 전부와 20개 장애물을 따로 두는 구조를 **12개 물체의 역할 공유**로 변경했다. 형상은 초기화 때 생성하며 reset에서 USD 삭제·생성, 충돌 형상 교체 또는 센서 재생성을 하지 않는다.

보상 함수·계수·순서, 종료, action과 제어, PPO 모델과 학습 값, 관측 정의·차원, OBB RED/Gray/White·최소 20mm 간격·Gray padding 일정, 타겟 root/목표 생성 로직, 질량·마찰 분포는 부모를 유지한다. 성공 timeout +75와 실제 타겟–손 접촉만 보상하는 규칙도 같다.

Gray는 2500 iteration부터, White는 2000부터 각각 1000마다 +1 증가한다. 초기 1/1, 최종 4/5다. 장면 용량은 Gray 4·White 5로 줄였지만 관측은 policy 57D / obstacles 80D / privileged 3D를 유지한다. 장애물 관측의 나머지 슬롯은 padding한다.

## 12개 물체와 역할 전환

| 물리 구성 | 수량 | 역할 |
| --- | --- | --- |
| 원통 | 1 | 타겟 전용 |
| 직육면체 | 1 | 타겟 전용, 부모와 같은 크기 |
| 기타 형상 | 10 | 타겟 또는 장애물 |
| 총 물리 물체 | 12 | 최대 활성: 타겟 1 + 장애물 9 |

기타 10개는 기존 14개 후보(크기 변형 포함)에서 생성 시 독립적으로 뽑는다. 같은 종류의 물체가 여러 개 생길 수 있다. 각 물체의 ±10% geometry scale도 생성 시 고정한다.

reset마다 원통/직육면체/기타 타겟 그룹을 각각 1/3 확률로 선택한다. 기타를 선택하면 보유한 10개 중 하나를 균등 선택한다. 남은 기타 물체 중 9개를 무작위 순서로 Gray 4 / White 5 논리 슬롯에 할당하고, 현재 커리큘럼 수량에 맞춰 배치한다. 같은 물리 물체가 타겟과 장애물로 동시에 배치되지 않는다. 원통·직육면체는 장애물에 포함하지 않아 부모의 장애물 후보군을 유지한다.

**형상 목록이 환경별 초기화 때 고정된다는 점은 부모와 다르다.** 부모는 각 환경에 16개 타겟 후보 전부가 있다. 자식은 기타 후보 14종 중 일부만 보유한다. 전체 병렬 환경의 생성 분포는 기존 후보 균등 분포지만, 단일 환경에서의 종류 빈도와 reset 사이 상관관계는 동일하지 않다. 개별 환경이 16종 모두를 경험한다는 보장은 없다. 이 제한으로 사용하지 않는 전체 후보 풀을 줄였다.

원통·직육면체·기타의 타겟 확률과 장애물 후보군을 함께 유지하려면 보조 물체 2개가 필요하다. 따라서 10개가 아닌 12개다. 비선택 2개와 아직 활성화하지 않은 장애물은 원격 배치·중력 해제로 격리한다. 실제 collider/actor는 유지한다.

## 구현과 메모리 관리

`assets/final_compact_spawners.py`는 형상 prototype을 16개 이하로 한 번만 생성한 뒤 필요한 물체 슬롯으로 복제한다. 초기 물리 재질은 마찰·반발·compliance·combine 속성이 모두 같은 경우에만 전역 material로 공유한다. 로봇·선반 역시 자식 전용 spawner에서 복제 전에 재질을 공유한다. 기존 material의 시각 shader는 보존하고 물리 API만 제거한다. 형상 prototype은 prestartup에 삭제한다.

`mdp/common/final_compact_pool.py`는 논리 10역할에서 물리 12물체로의 tensor mapping을 관리한다. 상태 읽기·쓰기, 질량·관성·마찰, 접촉 센서가 동일한 mapping을 사용한다. 쓰기는 후보별 Python 반복 대신 물리 buffer에 scatter 후 한 번 전송한다. 접촉력은 sensor bank에서 한 번 모아 논리 역할별로 선택하고, reset·센서 update 때 cache를 무효화한다.

재질 랜덤화는 부모의 유한 bucket과 Tensor API를 유지한다. 초기 USD 물리 재질 5개라는 측정은 reset 후 PhysX 내부의 모든 material handle이 5개뿐이라는 뜻이 아니다. 64K 오류가 발생했던 대규모 실제 자산 실행까지 재현·검증한 것은 아니다.

## 검증과 제한

Windows 11 / conda `env_isaaclab`에서 CPU/CUDA 회귀 109개 통과. 기존 production class/function 42개의 AST가 기준 HEAD와 동일함을 확인했다. 실제 Isaac Lab 설정 검사에서도 부모들 생성 전후 값과 v0_2_2의 보상·종료·관측·제어·커리큘럼이 보존됨을 확인했다.

실제 선반 Nucleus 서버가 응답하지 않아 **로컬 선반 대체 USD**로 GPU 4 env 및 64 env를 검증했다. 로봇과 물체 형상은 기존 자산을 사용했다. 각 실행에서 30회 full/partial reset, 독립 polygon 배치 검사, finite reward, 센서 역할 mapping, 비대상 env 보존을 확인했다. 64 env에서는 물리 buffer readback으로 역할 전환 후 질량·마찰도 검증했다. 모든 16개 타겟 종류가 전체 64 env에 걸쳐 관찰됐다.

64 env 대체 선반 기준 부모는 물리 물체 36개/env와 초기 USD 물리 재질 2434개, 자식은 12개/env와 재질 5개였다. 정확한 시간·메모리 지표와 실행 조건은 개발 로그를 따른다. 대규모 학습, 원래 선반과의 물리 검증, 2048/4096 env의 총 VRAM 및 64K 한도 재현, 장시간 안정성은 미검증이다.

```powershell
conda activate env_isaaclab
python src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Final-GoalAccuracy-v0_2_2 --num_envs 64 --headless
```

학습 예시이며 이 작업에서 실행하지 않았다. 실제 선반 서버 또는 `INSPIRE_SWEEP_SHELF_USD_PATH`로 지정한 자산에 접근할 수 있어야 한다. 검증용 로컬 선반을 production 기본값으로 바꾸지는 않았다.
