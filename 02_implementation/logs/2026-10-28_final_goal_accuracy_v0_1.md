# 2026-10-28 Final GoalAccuracy v0_1 구현

[구현 계약](../environments/FINAL_GOAL_ACCURACY_V0_1_ENVIRONMENT.md) · [승인된 개발 사양](../../01_plan/environments/2026-10-28_FINAL_GOAL_ACCURACY_V0_1_REWARD_SPEC.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

## 근거와 범위

사용자가 전체 명세의 실제 구현을 승인했다. 코드 기준 커밋은 `350db965476f051ba1e1b3e00a7ea6bb377f3ead`, 문서 저장소 기준 커밋은 `548d46ac07df17a39cbf70bdaa9b27ff0727c97d`다. 작업 시작 때 문서 저장소에 있던 명세·분석·그래프 변경을 보존하고 구현 상태를 추가했다. 코드와 문서 submodule의 커밋은 만들지 않았다.

정확도 개선을 위해 Accuracy v0를 직접 상속한 `Isaac-Inspire-Final-GoalAccuracy-v0_1`을 추가했다. 기존 v0/v1은 등록 ID의 `Accuacy`를 `Accuracy`로 교정하고 보상·종료·일정을 보존한다. 취소된 ±5% 크기 variant 및 Scene Reset 시 종류 재추첨은 구현하지 않는다. 기존 로그·checkpoint와 학습 로그 디렉터리는 수정하지 않았다.

## 변경 전후와 의도

| 항목 | 변경 전 | v0_1 구현 및 의도 |
| --- | --- | --- |
| 목표 인정 | 1cm | 2cm, Hold·목표 내 Contact 간주·timeout 성공 분할이 같은 반경 조회 |
| Reaching | 목표 반경 연동 | 20cm 고정 near radius, weight 30, 기존 최소 gap 갱신 방식 보존 |
| Goal Distance | 부모 거리 보상 | `3.7 exp(-d/0.05)`의 밀집 보상률, 새 게이트 없음 |
| Goal Hold | 1cm 내부 중심 보상 | r=2cm, R=6cm; 내부 centered score와 외곽 quadratic tail, weight 8, 속력 scale 0.05 |
| Contact | 손의 접촉 판정 | 현재 target_id의 물체–손 접촉 합력만 판정; fresh·finite·0.01N 기준 또는 유효한 목표 내 점유, weight 1.45 |
| 큐브 타겟 | 8×8×8cm | 6×8×10cm; 타겟 cube variant에만 적용 |
| 크기·종류 randomization | 생성 시 기존 배율·종류 선택 | 기존 ±10% 연속 균일 배율과 reset 시 형상·배율 보존 |
| Manager 이름 | 주체 일부 불명확 | 사양의 11 Reward·11 Curriculum·6 Termination 명칭 적용 |
| 새 학습 경로 | 부모 experiment | `inspire_final_goal_accuracy_v0_1`, 나머지 PPO 설정 동일 |

외곽 Hold는 6cm에서 0, 2cm 경계에서 정지 시 초당 4, 중심에서 초당 16이다. 속력 배율과 기존 유효성 V를 유지한다. 성공은 10초 만료에서 XY 거리만으로 분할하며 조기 성공, 저속 또는 유지시간 조건을 추가하지 않는다.

접촉 벡터는 물체별 filter 힘을 먼저 합한 뒤 norm을 계산한다. 환경별 현재 target_id를 선택하므로 선반·장애물 접촉으로 보상을 받지 않는다. 실제 접촉 분기에는 기존에 없던 타겟 유효성·속도·목표 거리 게이트를 넣지 않았다. 목표 내 접촉 간주는 기존 유효성 조건을 유지한다.

## 구현 위치와 참조 연결

기존 역할별 `final.py` 및 `final_envs.py`에 자식 설정을 추가했다. `assets/final_spawners.py`의 cube_size 기본값은 기존 8cm를 보존한다. 새 Scene만 타겟 cube_size를 변경하며 population capacity 재구성에도 이를 다시 적용한다. 시각·충돌 mesh의 치수가 함께 바뀌고 기존 prestartup bounds 및 bottom-origin 배치 경로를 이용한다. 반높이를 임의로 더하지 않는다.

공유 `goal_radius`와 timeout 함수에는 조회할 Hold term 이름을 선택 인자로 추가하고 기본값을 기존 `goal_hold`로 유지했다. ShelfPenalty도 기본 조회 이름은 유지하며 자식만 `shelf_failure`를 전달한다. 세 Wrench 커리큘럼은 새 Reward 이름을 조회한다. 나머지 기존 함수·런타임·metric 집계는 재사용한다.

자식에서 옛 이름의 항은 None 처리했다. 특히 상속 dataclass에서 새 필드가 뒤에 붙는 문제를 방지하기 위해 Reward·Curriculum의 활성 순서를 부모와 동일하게 복원했다. Wrench 비용이 양의 보상 예산을 읽는 순서와 5% 상한을 검사했다. 계산식 변경은 명세에 지정한 항목에만 적용했다.

이름 대응표는 개발 사양 8.3절, 최종 활성 이름과 순서는 구현 계약에 기록했다. `Episode_Reward/*`, `Curriculum/*`, `Episode_Termination/*`는 새 이름을 사용한다. `Metrics/*`와 기존 환경의 term 이름은 유지한다. v0/v1 설명 파일도 `ACCURACY`로 바꾸고 활성 문서·README·인계를 연결했다. 역사 로그 두 개는 깨지는 상대 링크의 파일명만 교정했다.

## 전체 대조

- 실제 Isaac Sim에서 EnvCfg를 생성하여 부모 대비 top-level 차이가 `scene`, `rewards`, `terminations`, `curriculum` 네 그룹뿐임을 확인했다. 관측·행동·이벤트·command·물리·seed·episode 설정은 동일하다.
- PPO 설정 전체 비교에서 experiment_name만 다르다. 기존 runtime class를 재사용한다.
- Scene의 4개 population capacity 구성에서 cube_size를 부모 값으로 복원하면 전체 Scene 설정이 동일하다. 자식 생성 전후 부모 및 기존 v1 구성도 동일하다.
- CPU 비교는 이름 대응 후 보존해야 할 Reward·Curriculum·Termination의 함수·weight·params·순서를 검사한다. 일정 갱신 및 iteration rewind도 확인했다.
- 변경 전 커밋의 Final manager 설정 정의를 로드한 추가 대조에서 기존 Final, FinalV1, Accuracy v0/v1의 존재하는 모든 Reward·Curriculum·Termination 설정이 현재 값·순서와 동일했다. 역할별 3개 검사 통과. V1 Termination은 별도 클래스 없이 부모를 재사용한다.

## 검증 결과

| 검사 | 결과 |
| --- | --- |
| 관련 CPU 회귀·신규 테스트 | 139 passed, 15.65s |
| 공유 goal_radius 기본 인자의 Holding v0/v4 회귀 | 18 passed, 2.75s |
| 변경 전 커밋 Manager 설정 대조 | 3 passed, 1.61s |
| 실제 Isaac Sim 기존 Final 등록·설정·USD 자산 probe | exit 0 |
| 실제 새 EnvCfg/PPO 전체 비교·Scene 재구성·USD 자산 probe | 모든 해당 assert 통과, JSON 저장 |
| 실제 물리 reset/step | 미완료: CUDA 장치 없는 상태에서 초기화가 진행되지 않아 중단 |

CPU 검사에는 Hold 거리·속도·유효성 경계, 현재 target_id 선택·선반/장애물 배제·힘 상쇄·stale/NaN, Contact 목표 간주, 2cm timeout 분할, Reaching 부분 reset, exp 거리 보상 적분, 공식 Manager 인자 검사, Wrench 순서·상한, PPO CPU 업데이트·checkpoint·export가 포함된다. 기준 궤적의 50Hz 우측합은 2cm 도달 13.145598, 중심 도달 18.903699로 승인된 연속 적분과 일치하는 방향이다.

실제 USD 검사에서 0.9/1.0/1.1 배율별 직육면체 치수, CollisionAPI, world 바닥 1.05m 정렬을 확인했다. 회전된 bounds/XY 배치는 CPU 자산 검사에서도 확인했다. 설정/형상 검증은 물리 접촉 또는 학습 성능 검증을 대신하지 않는다.

기본 pytest 실행은 외부 ROS plugin의 `lark` 의존성 누락으로 수집에 실패하여 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`로 실행했다. 기존 mock의 새 선택 인자 미지원과 신규 테스트의 Manager class 인스턴스화 누락은 테스트 harness를 고쳐 재검사했다. 제품 코드를 우회하는 변경은 하지 않았다.

`nvidia-smi` 및 CUDA 초기화에서 사용 가능한 장치가 없었다. `--smoke --device cpu` probe는 설정·USD 검사를 마친 뒤 SimulationContext 초기화에서 완료되지 않았다. timeout 후에도 종료가 지연되어 실행 세션을 중단했다. reset/step·접촉센서의 실제 동작·행동의 부드러움·2cm 성공률·수렴·GPU 학습은 미검증이다. 장기 학습은 실행하지 않았다.

## 재현과 산출물

workspace 루트에서 실행한다.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q \
  src/inspire_sweep_baseline/tests/test_final_accuracy_v0_1.py \
  src/inspire_sweep_baseline/tests/test_final_configuration.py \
  src/inspire_sweep_baseline/tests/test_final_versions.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_contacts.py \
  src/inspire_sweep_baseline/tests/test_goal_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_hold_rewards.py \
  src/inspire_sweep_baseline/tests/test_goal_terminations.py

./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/tests/_final_accuracy_probe.py \
  --headless --device cpu
```

GPU가 있는 환경에서는 같은 probe에 `--device cuda:0 --smoke`를 사용하여 reset·step·커리큘럼·timeout 검사를 이어간다. 학습 명령은 구현 계약을 따른다.

- [CPU 139개 검사 출력](../../03_assets/artifacts/2026-10-28_goal_accuracy_v0_1_implementation/cpu_tests.txt)
- [실제 설정·Scene·USD 검사 JSON](../../03_assets/artifacts/2026-10-28_goal_accuracy_v0_1_implementation/config_and_assets.json)
- [기존 명세의 적분 계산·그래프](../../01_plan/environments/2026-10-28_FINAL_GOAL_ACCURACY_V0_1_REWARD_SPEC.md)

최종 문서 검사: 변경·추가 Markdown 15개 수식 검사 통과, 링크 검사 0 오류(내부 277개·workspace 외부 경로 52개). source/docs `git diff --check` 통과. 문서 파일명 교정에 따른 역사 로그의 앵커 두 개도 새 이름으로 연결했다.
