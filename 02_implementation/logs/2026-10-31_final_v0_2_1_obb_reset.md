# 2026-10-31 Final v0_2_1 OBB reset 연결

[환경 계약](../environments/FINAL_GOAL_ACCURACY_V0_2_1_ENVIRONMENT.md) · [OBB 모듈](../environments/BBOX_SCENE_LAYOUT.md)

## 요청과 기준

사용자가 `FinalGoalAccuracyV0_2_1EnvCfg`의 씬 랜덤화에 새 OBB 로직을 적용하고, 물체 수 증가 시작·간격을 보존하면서 Gray 4 + White 5 상한을 설정하도록 요청했다. 기존 환경을 직접 수정했으며 새 task를 만들지 않았다. 실행은 Windows 11 / conda `env_isaaclab`에서 수행했다. 학습은 실행하지 않았다.

시작 코드 HEAD는 `ab4a5ba3545a4bcb96e354e7215ef98e71e45df5`다. 직전 작업의 OBB 모듈·테스트·benchmark와 README 및 문서 변경이 작업트리에 남아 있었으며 그대로 이어서 사용했다. 기존 `IsaacLab` 미추적 변경도 보존했다. 로그 정리·커밋은 수행하지 않았다.

## 변경 전후

| 항목 | 변경 전 | 변경 후 |
| --- | --- | --- |
| v0_2_1 배치 | 원형 후보 생성 후 OBB 거절, env별 NumPy 반복 | 물체별 OBB 존·간격·경계 판정, 장면/restart/candidate 텐서화 |
| 타겟 명령의 기하 안전영역 | 원형 외접 반경 기반 | 실제 scaled bounds와 기존 goal root 한계의 교집합 |
| 수량 | 부모에서 4/5 상한 상속 | 자식에서도 4/5 명시, 배치 adapter도 이 상한 보장 |
| 증가 일정 | Gray 2500 / White 2000부터 각 1000마다 +1 | 동일 |
| Gray padding 일정 | fraction 0→0.15로 원형 RED 내부 경계 축소 | 일정·수치는 유지, OBB Gray 바깥 폭 60→69mm로 확장 |
| 실패 슬롯 | 수량 감소 후 연속 슬롯 재배치 | 개별 슬롯 정체성 유지, 실패 슬롯 비활성, 최다 restart 선택 |
| Scene 설정 | 최근 refactor에서 타겟 풀 Scene 선언이 주석 처리됨 | 타겟 풀 Scene 복원, 기존 runtime/타겟 재추첨 계약과 일치 |

Scene 복원은 타겟 종류를 reset마다 바꾸는 기존 v0_2_1 기능과 새 adapter가 요구하는 구성이다. 주석 상태에서는 부모 단일 타겟 Scene이 선택되며, runtime의 `TargetChoice`가 요구하는 복수 후보와 맞지 않았다. 사용자의 최근 코드 형식 변경을 되돌리지 않고 해당 선언만 복원했다.

`final_obb_geometry.py`에 shelf 좌표·asset root·비대칭 bounds 중심·yaw·min-z·논리 슬롯의 변환을 분리했다. 타겟 root의 2cm 원판, yaw=0, 목표 거리 5–15cm, 방향 제외각 커리큘럼을 유지한다. 원형을 가정한 기하 제약만 교체했으므로 세부 명령 분포는 이전과 완전히 동일하지 않다. 타겟·목표는 장애물 실패로 다시 추첨하지 않는다.

runtime 초기화에서 bounds를 device에 캐시하고 reset 시 선택된 타겟 행을 갱신한다. `randomize_final_target_scene`만 새 adapter를 호출한다. 객체 종류 추첨·질량/관성 mapping·물성 randomization·관측 noise/visibility·활성 mask·실제 개수 로그는 유지한다. Gray 슬롯 1–4, White 슬롯 11–15를 사용하며 남은 슬롯은 기존 높이로 격리한다. 물리 36물체 / 논리 21물체 / 장애물 관측 20슬롯의 용량은 바뀌지 않는다.

기존 fraction 커리큘럼의 단위는 그대로 유지하되 의미를 명시적으로 재해석했다. 새 OBB 규칙의 RED 금지를 보존하기 위해 `effective_gray_padding = gray_padding * (1 + gray_red_padding_fraction)`을 사용한다. 실제 파라미터는 이벤트에서 `gray_padding=.06`, `finger_gap=.02`, `placement_candidates=32`, `placement_restarts=4`, `placement_passes=2`로 노출한다.

## 검증

CPU/CUDA 기하·기존 보상·종료·설정 회귀 **106 passed in 18.02s**. 새 shelf adapter 테스트는 비대칭 bounds offset, 회전, z 접지 높이, 개수 상한, 실패 슬롯 정체성, seed 재현, 불가능한 타겟 명시적 오류를 검사한다. 기하 검증기는 최종 pose를 별도 NumPy 다각형·선분 거리 검사로 재검산한다.

실제 Isaac Lab CUDA 환경 2개에서 다음을 통과했다.

- 40회 부분 reset 후 비대상 env 상태와 타겟 종류 보존.
- 각 reset의 실제 물리 pose를 선반 좌표로 읽어 RED·Gray/White·20mm 간격·경계·min-z·비활성 슬롯 격리 검사.
- 0, 1999, 2000, 2499, 2500, 2999, 3000, 3499, 3500, 3999, 4000, 4499, 4500, 4999, 5000, 10000 iteration의 수량 요청 확인.
- 16개 타겟 후보 각각 강제 선택 후 reset 기하 검사 및 step의 finite reward 확인.
- 비선택 타겟의 손 force matrix 0, 관측 차원 policy 57 / obstacles 80 / privileged 3 유지.
- 실제 EnvCfg 직접 상속, 부모 v0/v0_1/v0_2/v0_3/v1 생성 전후 설정 격리, 부모 대비 PPO experiment 이름만 차이, 보상 2개 기존 차이 유지, 모든 curriculum 최종 설정 동일 확인.

부분 reset 평균은 약 0.10092초였다. 2 env 중 1 env를 reset한 진단 실행의 측정이며 rollout collection 성능 비교가 아니다. 이전 원형 reset 측정과 같은 날짜·부하·검증 조건을 통제한 A/B benchmark가 아니므로 속도 개선으로 보고하지 않는다. 대규모 환경 reset은 미검증이다.

```powershell
conda run --no-capture-output -n env_isaaclab python -m pytest src/inspire_sweep_baseline/tests/test_final_obb_layout.py src/inspire_sweep_baseline/tests/test_bbox_scene_layout.py src/inspire_sweep_baseline/tests/test_final_accuracy_v0_2_1.py src/inspire_sweep_baseline/tests/test_final_accuracy_v0_1.py src/inspire_sweep_baseline/tests/test_final_versions.py -q --basetemp outputs/pytest_final_obb_integration
conda run --no-capture-output -n env_isaaclab python -u src/inspire_sweep_baseline/tests/_final_accuracy_v0_2_1_probe.py --headless --device cuda:0 --smoke --output-dir outputs/final_obb_integration
```

산출물은 workspace `outputs/final_obb_tests.log`, `outputs/final_obb_probe.log`, `outputs/final_obb_integration/config.json`, `outputs/final_obb_integration/smoke.json`이다. 기존 probe 결과를 덮어쓰지 않았다. `V0_2_1_CONFIG_PASS`, `V0_2_1_SMOKE_PASS`와 정상 프로세스 종료를 확인한다. 시각화 point-instancer의 기존 Fabric 경고가 있었으나 검사 실패나 CUDA 오류는 없었다.

## 최종 대조와 미검증

변경된 기존 production 파일은 대상 EnvCfg, 대상 이벤트 설정·함수, 대상 runtime의 bounds cache 및 seed다. 공통 부모 배치·다른 환경·보상·종료·제어·PPO·관측 정의는 변경하지 않았다. 수량 커리큘럼은 이미 요청과 동일했으므로 유효 일정 변경 없이 자식 상한을 명시했다. 새 순수 기하 adapter 및 검증 파일은 기존 역할 디렉토리에 추가했다.

미검증: 장시간 정책 학습과 성공률, 실제 손가락 접근 가능성, 실제 동역학 중 박스 밖의 움직임/전도, 대규모 collection 시간·메모리. 초기 직립 OBB가 안전하다는 것과 학습 중 충돌이 없다는 것은 구분한다. 배치 수량은 승인된 제한 탐색의 최다 결과이며 전역 packing 최적성을 보장하지 않는다.

문서 검사: 이번 변경 문서 5개의 수식·링크 검사 통과(내부 링크 52개, 오류 0), README 수식 검사 및 양쪽 저장소 `git diff --check` 통과. README 전체 링크 검사는 이전 작업에서도 확인한 기존 v0_2 문서 대상 부재 1건만 보고했다. 새 링크는 유효하다. Markdown 렌더링은 미검증이다.
