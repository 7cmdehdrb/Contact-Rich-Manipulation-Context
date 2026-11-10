# Relative-IK-v0_2_2_2-Fast-Test

2026-11-09. 코드 구현 및 CPU 검증 완료. **GPU/PhysX 및 Collection 성능은 미검증**이다.

[개발 명세](../../01_plan/environments/2026-11-09_RELATIVE_IK_CIRCLE_RESET_SPEC.md) · [개발·검증 로그](../logs/2026-11-09_relative_ik_fast_test.md)

## 등록과 상속

| 항목 | 값 |
| --- | --- |
| Gym ID | `Inspire-Wrench-Refactor-Relative-IK-v0_2_2_2-Fast-Test` |
| EnvCfg | `WrenchRefactorRelativeIKV0_2_2_2FastTestEnvCfg` |
| 직계 부모 | `WrenchRefactorRelativeIKV0_2_2_2TestEnvCfg` |
| runtime | `WrenchRefactorRelativeIKV0_2_2_2FastTestEnv` → 부모가 사용하던 `WrenchRefactorRelativeIKV0_2TestEnv` |
| PPO | `WrenchRefactorRelativeIKV0_2_2_2FastTestPPORunnerCfg` → 부모 runner 직접 상속 |
| experiment_name | `inspire_wrench_refactor_relative_ik_v0_2_2_2-Fast-Test` |

부모·기존 형제·보류 Reset-Test의 설정과 reset backend는 보존한다. 환경 수2048,10초 timeout,100Hz physics/50Hz policy,36step rollout과 PPO 수치는 부모와 같다.

## 변경 계약

- IK 박스는 기본 OFF이며 생성·갱신·host 전송 경로를 실행하지 않는다. 명시적으로 debug ON을 설정하면 표시할 수 있다.
- 장애물 수는0–6 균등 추첨한다.16개 후보 중N개를 중복 없이 균등 선택한 뒤 큰 반지름부터 배치한다. GRAY 할당은 없다.
- 물체마다 scaled Top-Down BBOX 외접원과 중심 offset을 startup에서 계산한다. 배치 반지름은 외접원+1cm다.17개 물리 pool·16슬롯 관측·기존 형상/scale은 유지한다.
- RED는 타겟의 시작→목표 중심 선분을 shelf-local +X 앞 경계까지 연장하고 타겟 배치 반지름으로 확장한 영역이다. 장애물 확장 원 전체가 RED 밖·선반 안에 있어야 한다.
- 5mm 셀의 전체가 안전한지 판정한 뒤 균등 셀+셀 내부 연속 좌표를 추첨한다. 원끼리2cm, 장애물과 선반 경계1cm의 최소 여유를 보장하도록 보수적으로 검사한다. 기존 GRAY padding·red_margin·rear_offset은 적용하지 않는다.
- 후보/restart/pass 및 실패 목표 재추첨을 사용하지 않는다. 안전 셀이 없으면 env ID·seed·물체·목표·실패 순서와 함께 오류를 낸다. 개수 축소나 일부 배치 반영은 하지 않는다.
- Warp IK는 원래 USD joint frame·EEF offset·default seed·DLS0.02·step cap0.15·최대80회·위치0.5mm/회전0.003rad 판정을 유지한다. CUDA batch를 CPU로 자동 우회하지 않는다.
- reset은 단일 `object_spawn` 이벤트에서 계산 성공 후 shelf/root·최종 arm+기본 hand·물체 상태를 기록한다. native manager reset 순서는 그대로다. gravity setter는 변경된 행만 호출하고 기존 wake-up 의미는 유지한다.
- 배치 기하와 별개로 기존 가시성 반경을 캐시한다. Actor/Critic 관측·노이즈·swap·F/T·촉각·보상·종료·커리큘럼·Metrics는 부모와 같다. 물성은 startup 고정이다.

구현 파일은 기존 역할별 `wrench_refactor_relative_ik_test` 파일과 `mdp/common/wrench_refactor_layout.py`에 둔다. Warp decorator/kernel은 독립 계산 모듈 `mdp/common/wrench_refactor_warp_ik.py`에서 Fast 경로만 지연 import한다.

배치·goal은 기존 layout generator, IK는 seed+1707 generator를 사용한다. 같은 seed·같은 reset 순서는 재현 가능하지만 변경 전과 전체 RNG 소비/trajectory가 동일하지는 않다. 실행 중 geometry 설정·bounds tensor 또는 캐시된 IK 입력/offset 변경을 감지하면 재생성을 요구하는 오류를 낸다. stage joint frame의 실행 중 직접 편집은 지원하지 않는다.

## 실행

GPU와 기존 asset 경로를 사용할 수 있는 Isaac Lab Python 환경에서 workspace 루트를 기준으로 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Wrench-Refactor-Relative-IK-v0_2_2_2-Fast-Test \
  --num_envs 2048 --headless
```

실제 geometry/부분 reset 검증:

```bash
python src/inspire_sweep_baseline/tests/_wrench_refactor_fast_probe.py \
  --headless --num-envs 64 --layout-samples 100000
```

위 GPU 명령은 이번 환경에서 실행 완료한 명령이 아니다. 현재 `nvidia-smi` 연결 실패·Torch CUDA unavailable·Warp CUDA device 없음으로 실측할 수 없었다. 실제 자산100,000배치·PhysX 부분 reset/rollout·동일 장비 baseline/Fast 각100iteration 성능 비교가 남아 있다. 따라서 코드가 추가되었다는 사실을 장기 학습 준비 완료나 속도 개선 입증으로 해석하지 않는다.

## v0_2_2_3-Fast-Test 파생 환경

`Inspire-Wrench-Refactor-Relative-IK-v0_2_2_3-Fast-Test`는 위 v0_2_2_2-Fast-Test를 직접 상속한다. 접촉 카운트 상한을20으로 늘리고, 최종 불인정마다2를 빼되0 아래로 내려가지 않는다. 최종 불인정 step에는 보상0이며, 재접촉 인정 시 남은 카운트에서+1한 값으로 지급을 재개한다. 초기 선반 표면 기준 EEF 높이15cm 이상도 보상0이다. goal_hold와 goal_speed_scale을 제거하며 나머지 설정은 부모와 같다. [전체 변경·실행·검증](../logs/2026-11-09_relative_ik_v0_2_2_3_fast.md).

## v0_2_2_4 파생 환경

`Inspire-Wrench-Refactor-Relative-IK-v0_2_2_4`는 v0_2_2_3-Fast-Test를 직접 상속한다. 물체 가속도 비용 및 관련 일정 제거,10초 timeout의 XY 거리<3cm 성공 분류와 전용 비율 기록을 추가한다. 기존 접촉/물리/reset/PPO 계약은 유지한다. [전체 변경·실행·검증](../logs/2026-11-09_relative_ik_v0_2_2_4.md).

## v0_2_2_5 파생 환경

`Inspire-Wrench-Refactor-Relative-IK-v0_2_2_5`는 v0_2_2_4를 직접 상속한다. Goal Distance를 현재 타겟 접촉 조건부 policy step 접근량(weight120)으로 교체하고 같은 접촉 조건의 방향 이탈 비용(weight−6)을 추가한다. 기존 후퇴−25.94를 유지하고 접촉 유지 카운트 보상은 제거한다. physics step별 누적은 없으며 나머지 부모 계약은 보존한다. [전체 변경·실행·검증](../logs/2026-11-09_relative_ik_v0_2_2_5.md).

## v0_2_2_6 및 메트릭 후속 변경

v0_2_2_4/runtime의 timeout/success 메트릭을 최근N개 완료 에피소드 창으로 변경했다. 기본N=10,000, 조기 실패도 창에 포함하고 timeout/success count는 해당 창 안에서만 집계한다. v0_2_2_5 및 v0_2_2_6에도 적용된다. 종료/성공 판정은 유지한다.

`Inspire-Wrench-Refactor-Relative-IK-v0_2_2_6`는 v0_2_2_4를 직접 상속하며 Reach만 변경한다. 타겟3D BBOX 중심과 EEF 거리의10cm 바깥 초과량에 대해0.1/(0.1+초과량)의 근접도를 지속 지급한다. weight30과 초기 기존 Reach 최대예산을 기준으로10초 지급률을 정해 총액 상한을 맞췄다. 나머지 보상·일정은 v0_2_2_4와 같다. [수식·규모·검증·실행](../logs/2026-11-09_relative_ik_v0_2_2_6.md).

2026-11-11 후속: v0_2_2_4에 도입했던 스폰 영역 시각화는 Simple 계열의 복제 구현과 함께 완전히 삭제했다. 실제 원형 RED/WHITE 배치·IK·성공 판정은 유지한다. [삭제·검증](../logs/2026-11-11_remove_spawn_region_visualization.md).
