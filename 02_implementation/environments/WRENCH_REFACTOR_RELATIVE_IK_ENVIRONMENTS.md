# Relative-IK 환경

목표 방향 반대편에서 Arm을 시작하도록 IK 초기 자세를 적용한 Relative 파생 계열이다. [v2_7의 초기 자세 구현](../logs/2026-11-08_relative_v2_7.md)을 재사용하되 아래와 같이 위치 범위와 품질 검사를 확장한다. [구현·검증 기록](../logs/2026-11-08_relative_ik_family.md).

## 공통 계약

- IK-v0은 `WrenchRefactorRelativeV2_7EnvCfg`를 상속한다. 즉 v2_1의 보상과 목표 분포에 목표 방향별 IK 초기화를 적용한다.
- 왼쪽 목표이면 물체 오른쪽, 오른쪽 목표이면 물체 왼쪽에서 시작한다. 정확한 밀기·당기기는 왼쪽 분기다. EEF는 선반 전면 바깥8–10cm, 물체 좌우10–18cm, 기존 기본 EEF 높이 대비−1~+3cm이며 회전은 기존 default 자세다.
- 후보 위치는 각 축 독립 균등분포이며 reset마다 한 번 샘플링하고 IK를 한 번 푼다. 사전 경계 격자·랜덤 지점86,722개와 실제 reset 검증으로 위 범위를 확정했다. 학습 reset에서는 SVD 품질 검사·후보 재추출을 실행하지 않는다. IK 자체의 수렴 검사는 유지하며 실패 시 오류를 발생시킨다. 현재 자산·자세·물체 초기 반경2cm 조건에서의 실험적 검증이며 연속 영역 전체의 수학적 보장은 아니다.
- Actor와 Critic 모두 동일한 `policy`58D와 `obstacles`64D를 입력받는다. 물체 위치는 초기 snapshot만 사용하며 현재 물체 위치를 Critic에 별도로 제공하지 않는다. 기존 Relative-v0의 EEF 상대 관측 정의와 PPO 모델을 사용한다.
- Distance는 시작점 기준 누적 XY 변위 cosine이며 weight5, distance scale0.05다. EEF 높이는 선반 바닥+14cm 미만이어야 한다.
- 역방향 거리 증가 페널티 weight−12.97, Reaching 물체 link 원점 기준10cm/weight30을 유지한다. 임시 Reaching Point 마커는 없다.
- 기존 Scene, Action, 목표 분포, 나머지 보상·실패 종료·커리큘럼·PPO 수치는 보존한다. 일반10초 Timeout을 유지한다.

## 버전별 차이

IK-v0의 `debug_initial_ik_bounds=True`가 IK-v1에도 상속된다. 목표 방향과 관계없이 양쪽 EEF 초기 위치 샘플링 범위를 동시에 표시한다. 물체 오른쪽(+Y)은 하늘색, 왼쪽(−Y)은 주황색이며 각 박스 크기는 기본값에서2×8×4cm다. 1mm 두께의12개 테두리로 각 박스를 표현하며 Collider·RigidBody를 생성하지 않는다. reset 시 실제 IK event의 범위, 물체 초기 Y, 기본 EEF Z + 높이 offset, 선반 pose로 갱신하고 에피소드 중에는 고정한다. 이는 EEF Frame의 후보 위치 샘플링 영역이며 손 전체의 충돌 여유나 로봇 전체 도달 가능 영역을 나타내지는 않는다. 임시 Reaching Point 마커와는 별개다.

| 항목 | IK-v0 | IK-v1 |
| --- | --- | --- |
| 직접 부모 | Relative-v2_7 | IK-v0 |
| Distance 지급 시 접촉 필요 | 아니요 | 현재 step 타겟–손 접촉 필요 |
| Contact 유지 보상 | 유지 | 제거 |
| Hold 보상 | 유지 | 제거 |
| 최초 진입 보상 | 유지 | 제거 |
| 성공 보상 | 유지 | 제거 |
| 목표 내 안정 상태3초 유지 성공 종료 | 유지 | 제거 |
| 일반10초 Timeout·실패 종료 | 유지 | 유지 |

IK-v1의 접촉 조건은 기존 `target_contact_below_height`를 사용한다. 유효한 현재 타겟–손 센서 힘이0.01N 이상이어야 하며 EEF 높이 조건도 유지한다. 이전 접촉 이력이나 목표 영역 내부라는 이유만으로 지급하지 않는다.

기존 Relative-v3는 실시간 이동 cosine 및 Distance weight25를 사용하지만, IK-v1은 요청된 IK-v0 상속과 명시된 변경 항목에 따라 **누적 변위 cosine 및 weight5**를 유지한다. 기존 v3와 보상·종료 제거 목록을 공유하며 완전히 같은 Distance 구성은 아니다.

## 실행

Collection 최적화로 작은 reset 배치는 계산 장치만 변경한다. IK는128개 이하에서 동일한 DLS를 CPU로 계산하고, Refactor 장애물 search는8개 이하에서 CUDA 난수열을 그대로 사용해 CPU로 계산한다. 큰 배치는 기존 GPU 경로다. 환경·학습 설정과 후보 분포·수렴 조건은 유지하며 reset SVD·재추출은 여전히 비활성이다. [전체 함수 프로파일·동등성·성능 비교](../logs/2026-11-08_collection_profile.md).

Isaac Lab Python 환경에서 workspace 루트 기준으로 실행한다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-IK-v0 --headless
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-IK-v1 --headless
```

실험명은 각각 `inspire_wrench_refactor_relative_ik_v0`, `inspire_wrench_refactor_relative_ik_v1`이다. EnvCfg와 RunnerCfg는 기존 `envs/wrench_refactor_envs.py`, `agent/wrench_refactor_ppo_cfg.py`에 추가했으며 runtime은 기존 `WrenchRefactorEnv`다.

## IK-v0_1

`Inspire-Wrench-Refactor-Relative-IK-v0_1` directly inherits IK-v0 and sets only `target_goal_first_entry_bonus` to `None`. All other settings, including both IK boxes, remain unchanged. PPO experiment_name is `inspire_wrench_refactor_relative_ik_v0_1`; training parameters are inherited. [Contract and validation](../logs/2026-11-09_relative_ik_v0_1.md).
