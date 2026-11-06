# Relative 계열 Axia280g 공통화·v1 폐기·v2 관측 정정·v3 추가

2026-11-06. 요청 대상은 `src/inspire_sweep_baseline`의 Relative 계열이다. 기존 작업트리와 문서 submodule 커밋은 보존했으며 `logs/rsl_rl`은 수정하지 않았다.

## 요청·의도·최종 결정

사용자는 Relative-v0부터 Axia 질량280g을 적용하고 F/T 보정을 검증하며, Base 장애물 관측 v1을 삭제하고, v2는 Critic 실시간 타겟 관측만의 효과를 비교하도록 유지하고, v3는 v0의 별도 접촉 유지 보상을 거리 보상 조건으로 합치는 실험을 요청했다. GPU 스모크를 허용했다.

작업 시작 시 v2 코드는 Actor=현재/Critic=초기였다. 질문에 대한 사용자의 명시적 답변 **“이번 목적대로 Actor=초기, Critic=실시간 위치”**에 따라 이를 정정했다. v3 거리 weight는 참조한 Wrench-Refactor-v1의25를 사용하고 Relative-v0의 기존 signed cosine을 보존했다.

## 변경 전후와 영향

| 대상 | 변경 전 | 변경 후 |
| --- | --- | --- |
| Relative-v0 Axia | 0.001kg | 0.280kg |
| Relative-v1 | Base 장애물 관측 +280g | EnvCfg·Gym 등록·runner 삭제 |
| Relative-v2 | Actor 현재 / Critic 초기, Axia1g | Actor 초기 / Critic 현재, 공통 Axia280g |
| Relative-v3 | 없음 | v0 직접 상속, 접촉 유지 삭제, 현재 접촉 조건부 cosine 거리 weight25 |

v0의 `scene.robot.spawn.sensor_mass`만 설정하여 v2·v3와 이후 직접 파생 환경이 상속하게 했다. 비Relative 계열의 질량 상수와 자산 기본값은 보존했다. 실제 하우징 관성은 기존 spawner가 변경된 질량으로 계산한다. 기존 v1 학습 로그·checkpoint는 삭제하지 않았다.

v2의 `policy`는 v0를 그대로 상속하고 `critic.target_obs_state`만 `CurrentObjectPositionInEEF`로 교체했다. 목표·장애물·F/T는 EEF 기준이며 EEF pose만 base 기준이다. 타겟·촉각·F/T noise 분포는 유지하고 policy/critic 그룹의 표본은 기존 분리 구조대로 독립이다. 장애물 관측은 같은64D 텐서를 공유한다. Actor·Critic 모델과 storage의 별도 그룹 라우팅은 기존 v2 구조를 보존했다. 예전 v2 checkpoint와 차원은 같아도 관측 의미는 다르다.

v3의 거리 함수는 v0의 `displacement_cosine_goal_distance`를 호출하고 현재 `target_contact_below_height`가 거짓이면0을 반환한다. 접촉은 fresh 센서·타겟-손 합력0.01N 이상·초기 선반면 대비 EEF 높이14cm 미만을 요구한다. 이전2/3step 유지 판정이나 누적 count, 목표 내부 접촉 면제를 가져오지 않는다. 음수 cosine과 변위0 처리 등 기존 거리 함수의 의미는 보존한다. 별도 `target_contact`만 `None`으로 제거한다.

## 최종 설정 전체 대조

v0 대비 v2는 관측 그룹만, v3는 접촉·거리 보상 두 설정만 다름을 전체 config dictionary로 대조했다. PPO는 v3의 experiment 이름 외 동일하며, v2의 기존 별도 관측 그룹·모델 설정은 유지한다. v1 등록이 없어졌음을 실제 gym registry에서 검사했다.

다음은 기존 설정과 동일하다.

- 물체17개 풀, 타겟·장애물 생성 규칙, 스폰 높이/타이밍, reset·부분 reset, 고정 물성, parking 중력 처리.
- 현재 EEF OSC, raw 정책 action-rate, Hand actuator, 타겟/goal/장애물 좌표계 및 장애물 가시성 선정·확률 변조.
- Arm6관절 물리 속도3.14rad/s, effort150/150/150/28/28/28Nm.
- 속도 종료4.0rad/s를10,000까지 유지,10,250부터250iteration마다0.05 감소,20,000부터2.0 유지. 다른 종료·커리큘럼도 동일.
- v0/v2의 모든 보상, v3의 지정 두 항 이외 보상, 최초 진입10, F/T 보정식과 측정 경계.

## CPU·GPU 검증

CPU 검사 **88개 통과**. 실제 함수의 초기/현재 타겟 변환, 관측 그룹·모델·storage·export, v3 현재 접촉 gate와 양수·음수·0변위 cosine, stale·무접촉 시0, 전체 설정 allowlist를 검사했다.

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q src/inspire_sweep_baseline/tests/test_task_contract.py src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench_refactor_relative.py src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py
```

GPU는 각 버전 **2환경×180step**, 총3회 통과했다. 서로 다른 iteration과 부분 reset에서 관측·보상 유한값, EEF OSC, 실물성 readback과 curriculum 경계/되감기, 부모 설정 격리를 확인했다. 모든 환경의 초기 바닥 높이 오차는0m, 주차 물체 최대 drift는3.815e-6m다. 질량 readback은0.2800000012kg이다. v2/v3에서는 실제 반환한 타겟 관측을 초기/현재 world 위치와 저장 bias의 EEF 변환 결과와 매step 직접 대조했다. 세 환경 모두 장애물64D를 EEF 함수값과 대조했다.

| 버전 | policy | critic 전용 | obstacles | 결과 |
| --- | --- | --- | --- | --- |
| v0 | 58D | 없음 | 64D | 통과 |
| v2 | 58D | 58D | 64D | 통과 |
| v3 | 58D | 없음 | 64D | 통과 |

GPU 재현 명령은 version을0/2/3으로 바꿔 실행한다. 결과는 workspace의 `outputs/relative_family_revision/v{version}/probe.log`, `probe_2.json`에 있다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python -u src/inspire_sweep_baseline/tests/_wrench_refactor_relative_probe.py --version 3 --num_envs 2 --headless --device cuda:0 --output outputs/relative_family_revision/v3
```

## F/T 캔슬레이션 확인

실제 Relative-v0의4환경에서 정적40샘플, Arm/Hand 운동160샘플, 기지 외력40샘플을 수집했다. 진단 프로세스에서만 선반·물체를 격리하고 관측 noise를 끄며 직접 물리 step을 진행했다. 실제 환경 설정이나 termination을 변경하지 않았다. probe는 `outputs/relative_family_revision/wrench_probe.py`, 로그는 `ft_280g.log`, 원시 요약은 `ft_280g.json`이며 `status=passed`다.

측정 joint는 Axia→손 경계다. 실제 reader의 downstream 목록에서 Axia가 제외되고 손의 합계 질량이0.7900000215kg인 것을 확인했다. 하우징 중력·관성은 해당 joint의 하위 반력에 직접 포함되지 않으므로 손 보정 합계에 추가하지 않는다. 변경 후 실제 PhysX 질량·관성으로 기존 보정이 동작한다.

| 시험 | 최대 힘 norm 오차/잔차 | 최대 모멘트 norm 오차/잔차 |
| --- | --- | --- |
| 정적 중력 보정 | 3.770e-6N | 8.520e-6Nm |
| Arm·Hand 운동 보정 | 3.990e-6N | 6.886e-4Nm |
| 기지 외력·모멘트 재현 | 5.619e-6N | 4.436e-3Nm |

기지 외력은 실제 손 링크 COM에 가하고 EEF 원점 이동을 포함한 기대 반력과 비교했다. reset 시 wrench0 및 stale 샘플0도 통과했다. 정적/외력 허용오차0.15N·0.02Nm, 동적0.5N·0.05Nm을 모두 만족했다. 시험 중 Arm 최대속도0.167rad/s, Hand1.000rad/s이므로 모든 가능한 고속 접촉에서 오차가 같다고 일반화하지 않는다.

## 코드 리뷰와 미검증 범위

`code-review` skill의 두 축으로 별도 리뷰를 수행했다. 기존 미커밋 작업을 이번 변경으로 오인하지 않도록 시작 시 `/tmp/relative_family_before`에 저장한 작업트리와 `/tmp/relative_family_review.diff`를 고정 비교 기준으로 삼고, 이 대화의 요청·명시적 정정을 요구사항으로 사용했다. 임의 commit이나 외부 issue를 추가로 요구하지 않았다.

- Standards: hard violation0, actionable heuristic0. 기존 역할별 파일·직접 상속·부모 보존 규칙을 준수했다.
- Spec: finding0. 질량 상속·v1 삭제·v2 역할·v3 접촉 gate 및 cosine25·F/T 측정 경계를 검토했다.

후속 자체 대조에서 테스트 주석 오타와 질량 설정 인근 주석 위치를 정리했으며 동작 변경은 없다. 활성 안내·v0/v2 명세를 갱신하고 v1 문서는 폐기 안내로 남겼으며 v3 명세를 추가했다. 변경한 Markdown8개 수식 검사와 root/submodule `git diff --check`는 통과했다. 링크 검사302개 중1개는 작업 전부터 존재한 package README의 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크였으며 시작 snapshot에서도 동일함을 확인했다. 이번 추가·수정 링크에는 오류가 없다. 무관한 링크를 고치지 않고 보존했다. 렌더러에서의 시각 검사는 수행하지 않았다.

2048환경 동시 reset, 장기·다중seed 학습, checkpoint 정책 성능 비교, 고속 충돌 전 구간과 실제 하드웨어 F/T 정확도는 이번 검증 범위에 포함하지 않는다. 기존 학습 로그와 unrelated 환경은 보존했다.
