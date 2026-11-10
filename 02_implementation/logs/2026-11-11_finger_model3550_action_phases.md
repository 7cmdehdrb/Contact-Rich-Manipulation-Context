# 2026-11-11 Finger model3550 접근·밀기·유지 action 실측

사용자가 [전체 action 조사](2026-11-10_finger_model3550_action_diagnostics.md)에 이어 접근→밀기→유지 각각의 수치를 요청했다. 기존 trace에는 접촉과 목표 거리가 없으므로 같은 checkpoint/seed/환경수/step수로 실제 headless PhysX play를 다시 실행하고, 원래 reward 계산 직후·자동 reset 직전에 상태를 추가 수집했다. 환경 제어와 학습 구성은 변경하지 않았다.

## 구간 정의와 해석 범위

현재 정책 자체에는 이 세 구간을 구분하는 별도 상태기가 없다. 동일 정책의 행동을 사후 분석 목적으로 분류한다.

- 접근: 에피소드 시작부터 최초 실제 Contact 인정 전까지.
- 밀기: 최초 Contact 인정 step부터 목표 XY 반경3cm에 처음 들어가기 전까지. 도중 비접촉도 이 작업 구간에 포함한다.
- 유지: 목표에 처음 진입한 뒤 현재 목표 XY 거리<3cm인 step. 안정적인 정지나 계속된 접촉을 전제하지 않는다.
- 목표 밖 재진입 구간: 한번 목표에 진입한 뒤 현재 XY 거리>=3cm인 step. 실제 재진입 성공 여부는 보장하지 않는다.

Contact 인정은 기존 `GoalContactMaintenance`의 실제 접촉 이력3step 중2개와 EEF 높이 조건을 그대로 사용한다. 목표 안에서 강제로 지급하는 reward20을 접촉으로 해석하지 않는다. 상태는 해당 action을 실행한 step 끝에서 측정하므로 경계 action이 새 구간으로 분류된다. Contact 검출 자체도2-of-3 이력으로 인한 약1step 지연이 있을 수 있다.

목표 미도달 에피소드는 접촉 후 실패·정체한 긴 시간까지 밀기 구간으로 남는다. 정상적인 세 구간의 규모를 비교하기 위해 **목표에 한번 도달한 완료89에피소드**를 주 표로 사용하고, 실패 및 부분 에피소드를 포함한 전체48,000샘플 통계도 별도로 보존했다. 목표 한번 도달은 최종 성공을 뜻하지 않는다.

## 목표 도달 완료89에피소드의 구간별 수치

상대 위치 목표는raw×0.03m의3D노름, 회전은raw×0.15rad의RPY를Quaternion/axis-angle로 변환한 뒤의 회전각이다. 현재EEF 기준이며50Hz로 갱신한다. 실제속력은OSC 내부에서 측정한 offset EEF의 속도다. 목표변위를0.02초로 나눈 가상속도가 아니다.

| 구간 | policy 샘플수 | 상대위치 목표 중앙값 / P95 / 최대 | 상대회전 목표 중앙값 / P95 / 최대 | 실제EEF 속력 중앙값 / P95 / 최대 |
| --- | ---: | --- | --- | --- |
| 접근 | 1,182 | 24.52 / 40.32 / 51.05cm | 60.30 / 93.00 / 114.45도 | 96.93 / 145.39 / 176.96cm/s |
| 밀기 | 643 | 11.77 / 17.45 / 32.49cm | 47.46 / 67.97 / 136.32도 | 42.47 / 89.05 / 132.26cm/s |
| 유지 | 39,089 | 1.50 / 3.49 / 13.79cm | 33.89 / 44.94 / 63.94도 | 0.873 / 13.60 / 68.07cm/s |
| 목표 밖 재진입 | 3,586 | 1.33 / 3.36 / 7.81cm | 31.03 / 41.66 / 60.89도 | 1.00 / 9.18 / 28.45cm/s |

각 구간의 전체step을 모은 통계이며, 에피소드별 통계의 평균은 아니다. P95는95백분위수다. 유지 구간은 진입 직후의 감속도 포함하므로 최고속력이0이 아니다. 구간별 상대위치 중앙값을0.03m로 나눈raw 벡터노름은 접근8.17, 밀기3.92, 유지0.50이다.

이89개에서 구간 길이의 에피소드별 중앙값은 접근0.24초, 밀기0.14초, 유지9.60초다. 각 중앙값은 독립적으로 계산되어 더한 값이 정확히10초일 필요는 없다. 밀기에서Contact 인정 비율93.00%, 유지92.60%다. 유지에서도 상대회전 목표 중앙값33.89도와 상대위치1.50cm를 계속 출력하므로, 유지가zero action을 뜻하지는 않는다.

## 실패·부분 포함 전체 통계

16환경×3,000step=48,000샘플, 완료96에피소드와 부분3에피소드. 완료96개 중95개에서Contact 인정,89개에서목표진입. 최초접촉시간 중앙값0.26초(Contact도달95개 기준), 최초목표진입시간 중앙값0.42초(목표도달89개 기준).

| 구간 | 샘플수 | 상대위치 중앙값 / P95 / 최대 | 상대회전 중앙값 / P95 / 최대 | 실제EEF 속력 중앙값 / P95 / 최대 |
| --- | ---: | --- | --- | --- |
| 접근 | 1,358 | 23.92 / 40.29 / 956.81cm | 60.67 / 93.79 / 162.06도 | 95.25 / 144.11 / 335.25cm/s |
| 밀기 | 2,852 | 2.99 / 14.79 / 32.49cm | 36.07 / 57.36 / 136.32도 | 2.53 / 56.39 / 132.26cm/s |
| 유지 | 40,204 | 1.49 / 3.50 / 13.79cm | 33.77 / 44.88 / 63.94도 | 0.882 / 13.84 / 68.07cm/s |
| 목표 밖 재진입 | 3,586 | 1.33 / 3.36 / 7.81cm | 31.03 / 41.66 / 60.89도 | 1.00 / 9.18 / 28.45cm/s |

이전 최대9.568m는 이번에도 재현됐다. 전체step8, env15, episode step8에서 접촉 없이 목표 거리7.393cm인 **접근 구간**이다. 그 에피소드는 목표 미도달이어서89개 주표에는 포함되지 않는다. 실패 포함 전체와 목표 도달 집합의 밀기 중앙값 차이는, 목표 미도달 후 긴 정체 시간을 밀기에서 제외하지 않은 영향이다.

## 재현·변경·검증

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/action_diagnostics/finger_3550_phases/run_probe.py --task Inspire-Sweep-Simple-Finger-v0 --checkpoint logs/TEMP/inspire_sweep_simple_finger_v0/2026-11-10_14-30-35/model_3550.pt --num_envs 16 --seed 42 --max_steps 3000 --headless --kit_args=--/app/vulkan=false
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/action_diagnostics/finger_3550_phases/analyze.py
```

- 원래 play 경로와 이전 조사 하네스를 재사용하고 reward 계산 뒤 read-only hook만 추가했다. process/apply의 제어값은 변경하지 않았다. 추가 상태는 정책 관측에 넣지 않았다. export 생략 및 log_dir를 outputs로 돌리는 이전 방식 유지.
- 체크포인트SHA256 `b64d17711f4c3d797e69e1529e46fe4dea79bdcc1ae0b12e5d6ba9e8e2b59642`, 실행 전후 hash 일치 assert 통과. 기존 로그, 체크포인트, 사용자 변경, 환경 코드 변경 없음.
- play 실행 종료 코드0, 3,000step 완료, action NaN/Inf0. py_compile 통과.
- 48,000개 전부 중복 없이 분류, 집계 샘플 합 일치, processed 위치=raw×0.03 일치, desired pose 거리=processed 위치 노름 일치, 유지 샘플 모두 목표 내부, 접근 샘플 모두 Contact 미인정 검증 통과.
- 미검증: 다른seed, 시각적 재생 관찰, 다른 분류 경계 정의의 민감도, 실제 접촉 발생 시각과 검출 지연 차이, 수정 후 제어 및 학습 결과. 현재 출력의 구간별 정량화이며 인과관계 실험은 수행하지 않았다.

[실행하네스](../../../../outputs/action_diagnostics/finger_3550_phases/run_probe.py) · [분류·집계코드](../../../../outputs/action_diagnostics/finger_3550_phases/analyze.py) · [원시trace](../../../../outputs/action_diagnostics/finger_3550_phases/trace.npz) · [집계JSON](../../../../outputs/action_diagnostics/finger_3550_phases/summary.json) · [전체구간CSV](../../../../outputs/action_diagnostics/finger_3550_phases/phase_summary.csv) · [구간별raw축범위](../../../../outputs/action_diagnostics/finger_3550_phases/phase_raw_ranges.csv) · [에피소드별경계](../../../../outputs/action_diagnostics/finger_3550_phases/episodes.json).
