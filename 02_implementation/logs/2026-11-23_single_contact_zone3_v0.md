# Single Contact Zone3 v0 구현·CPU 검증

## 요청과 실험 목적

사용자는 `inspire_sweep_single_contact_v0`를 부모로 당기는 방향인 Zone3만 생성하는 새 환경을 요청했다. 다른 방향에 대한 과적합이 당기기 학습을 방해하는지 살펴보기 위한 실험이다. 같은 요청에서 Sweep 진행·역방향 계수를 두 배로 올리도록 추가 지시했다. 따라서 최종 요청은 방향 제한과 두 weight 변경이며, Single Contact v1의 접근점·signed 방향·팔 종료 사건 비용은 도입하지 않는다.

현재 학습 중이므로 **GPU 테스트를 수행하지 말라**는 사용자 지시를 준수했다. GPU·Isaac Sim·AppLauncher·PhysX·학습·play는 실행하지 않았다. CPU 검사에서는 `CUDA_VISIBLE_DEVICES=''`를 지정했다. 기존 `logs/rsl_rl` 및 `logs/TEMP`는 변경하지 않았다.

기준 root HEAD는 `b705a505fe11ec9e85db66c4f29b47314d1178ae`, 문서 서브모듈 HEAD는 `dda40165854ee7a78dbc01fe69f26a2d3223df66`이다. 시작 시 사용자 `docs/SSH.md` 변경, 이전 작업의 다운로드 스크립트·개발 로그, 문서 서브모듈의 기존 커밋 차이를 보존했다. commit·push·서브모듈 체크아웃은 수행하지 않았다.

## 등록·상속·구현 위치

| 역할 | 최종 구성 |
| --- | --- |
| Task ID | `Inspire-Sweep-Single-Contact-Zone3-v0` |
| EnvCfg | `SweepSingleContactZone3EnvCfg(SweepSingleContactEnvCfg)` |
| Runtime | 부모의 `SweepSingleContactEnv` 그대로 등록 |
| State | 부모의 `SingleContactSweepState` 그대로 사용 |
| Layout | `SingleContactZone3ResetLayout(CircleResetLayout)` |
| Runner | `SweepSingleContactZone3PPORunnerCfg(SweepSingleContactPPORunnerCfg)` |
| 로그 | `inspire_sweep_single_contact_zone3_v0` |

- [환경 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_v0_envs.py): 부모 `__post_init__` 뒤 `events.object_geometry.params.layout_class` 지정, `sweep_progress.weight=100`, `sweep_retreat.weight=-20`만 적용한다. 기존 term을 `replace`하고 params를 새 dict로 복사하여 부모 term을 제자리 수정하지 않는다.
- [새 목표 샘플러](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/sweep_v0_layout.py): 기존 `CircleResetLayout.sample_commands`를 호출할 때 `goal_angle_range=(-π/6,π/6)`만 추가한다. `atan2(Y,X)` 기준 선반 +X/6시 ±30°이므로 기존 `sweep_region`의 Zone3에 해당한다. 12시 기준 각도 ±30°인 Zone1과 혼동하지 않는다.
- [기존 geometry 초기화](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/wrench_refactor_relative_ik_test.py)의 `initialize_fast_geometry(layout_class=...)` 확장점을 그대로 사용한다. reset 함수 인자나 물리 lifecycle은 변경하지 않는다.
- [PPO 설정](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/sweep_v0_ppo_cfg.py): 새 직접 자식의 `experiment_name`만 선언한다.
- [Gym 등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py): 부모 runtime과 새 EnvCfg/Runner를 연결한다. 기존 task 등록은 보존한다.

## 전체 계약 최종 대조

공식 Isaac Lab `configclass`·Manager term과 실제 Scene/EnvCfg 정의를 CPU에서 실행했다. simulator asset leaf·Action 생성자는 기존 CPU 하네스의 대역이다. 부모·자식의 전체 `to_dict()`를 순서까지 비교한 결과 차이는 아래 환경3개 경로뿐이다. Runner는 실제 모든 필드 정의를 실행하되 외부 learner/model leaf는 대역으로 사용하여 전체 dict를 비교했다.

| 항목 | 부모 Single Contact v0 | 새 Zone3 v0 | 판정 |
| --- | --- | --- | --- |
| 목표 방향 | 전 방향 | 선반 +X ±30° 균등 | 요청한 방향 제한 |
| `events.object_geometry.params.layout_class` | 없음, 기본 Circle layout | `SingleContactZone3ResetLayout` | 방향 제한 연결 경로 |
| `sweep_progress.weight` | 50 | 100 | 요청한 두 배 |
| `sweep_retreat.weight` | −10 | −20 | 요청한 두 배 |
| 초기 타겟·목표 거리·선반 경계 | 반지름2cm 원판·6–12cm·기존 safe edge 규칙 | 동일 | 보존 |
| 장애물·reset·IK | 최대6개·Circle 배치·단일 Warp IK·surface snapshot | 같은 알고리즘 | 보존, 새 방향에 따른 결과 변화는 가능 |
| 접촉 | 최근3 policy step 중2회·높이12cm 미만·현재 실제 접촉/유효 힘·인정 계수1/0 | 동일 | 보존 |
| Sweep 함수·면 선호 | 기존 0–1 힘 정렬·Zone3 손바닥1.5/손등0.7/중립1 | 동일 | weight 이외 보존 |
| Reach | 물체 중심 거리10cm plateau·45cm cutoff, weight0.8 | 동일 | 보존 |
| 활성 보상 | 기존15개, 기존 순서 | 동일 | 두 weight 이외 callable/params/weight 불변 |
| 관측·행동 | policy66D + obstacles64D, action12D·손[0,1] | 동일 | GT·접근점·제어 변경 없음 |
| 시간·성공·종료 | dt0.01×decimation2·10초, 기존 timeout3cm 미만 성공·팔1rad/s 초과 종료 등 | 동일 | 부모 판정 보존 |
| 커리큘럼 | 빈 dict | 동일 | 새 일정 없음 |
| PPO | 기존 모델·36step·8epoch/4batch·gamma0.98·save50 등 | 동일 | `experiment_name`만 새 값 |
| 부모·형제 | Sweep v0·Single Contact v0/v1 | 작업 전 정의 유지 | AST·부모 재생성 검사 통과 |

자식의 weight·중첩 IK params·layout class를 수정한 뒤 기존 부모 객체와 새 부모 객체가 원래 전체 dict를 유지하고, 새 자식도 원래 의도한 전체 dict를 재현함을 확인했다. 기존 클래스6개(EnvCfg3개·Runner3개)와 등록/기타 최상위 호출46개의 AST가 HEAD와 동일하게 남아 있음을 확인했다. 기존 runtime·공유 목표 샘플러·공유 reset·보상 함수 파일은 수정하지 않았다.

## CPU 검사 명령과 결과

workspace 루트에서 실행했다.

```bash
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=2 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact_zone3.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact.py \
  src/inspire_sweep_baseline/tests/test_sweep_v0.py \
  src/inspire_sweep_baseline/tests/test_sweep_single_contact_v1.py \
  src/inspire_sweep_baseline/tests/test_sweep_only_action_penalty.py -q
```

최종 **66 passed, 2.49초**다. 새 검사8개와 기존 회귀58개를 실행했다.

- seed0/42/1123에서 각각2,048개, 총6,144개 목표 방향이 모두 Zone3이었다. 부모와 같은 seed의 초기 타겟 좌표가 정확히 일치하고 generator state도 일치하여 목표 샘플링의 난수 소비량을 보존했다. 원판 반경·목표 거리6–12cm·선반 경계를 확인했다.
- float32/float64에서 −30°·0°·+30° 및 경계 안쪽 방향을 실제 `sweep_region`으로 검사했다. 두 경계 모두 Zone3이다.
- 실제 상속한 `CircleResetLayout.sample`을 CPU에서 부분 ID `[7,1,4]`로 실행하여 물체 배치·활성 개수·목표 방향·원본 bounds 불변을 확인했다. 물리 simulator reset을 실행한 검사는 아니다.
- 전체 Cfg/Runner dict·부모 중첩 설정의 독립성·Gym 등록 문자열·부모 runtime 재사용을 확인했다. 기존 이진 접촉·부분 reset state·v1 보상·접촉면/ActionPenalty 회귀를 함께 검사했다.
- 변경/신규 Python5개는 `compile`로 문법 검사했고 기존 정의/등록의 AST 보존을 검사했다. 실행 중인 학습 프로세스에는 접근하지 않았다.

첫 pytest 시도는 시스템 ROS pytest plugin의 `lark` 미설치로 수집 전에 실패해 plugin 자동 로드를 비활성화했다. CPU 하네스의 layout class 직렬화 기대값과 PPO 대역의 상속된 `policy` annotation을 공식 configclass 규약에 맞춰 수정한 뒤 최종 통과했다. 이 교정 과정에서 운영 코드나 부모 설정을 추가 변경하지 않았다.

## 학습 실행 안내

아래는 사용자 실행용 명령이며 이번 작업에서 실행하지 않았다. 기존 Isaac Lab 의존성이 설치된 환경에서 workspace 루트를 작업 디렉터리로 사용한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Single-Contact-Zone3-v0 --num_envs 2048 --headless
```

학습 로그 경로는 `logs/rsl_rl/inspire_sweep_single_contact_zone3_v0/<실행시각>`이다. 기존 로그를 이동·정리·덮어쓰지 않았다. [환경 계약](../environments/SWEEP_V0.md#single-contact-zone3-v0), 패키지 README·활성 환경 안내·인계 요약·Sweep 계통 색인을 갱신했다.

문서 최종 검증: 변경 Markdown6개의 수식 검사, 문서 저장소 변경5개의 외부 workspace 링크 포함 검사(오류0), 문서 저장소 전체 링크 검사(Markdown656개·오류0), root/문서 저장소 `git diff --check`를 통과했다. README 전체를 외부 경로까지 검사하면 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 링크1개의 누락이 보고된다. 이 링크가 root HEAD에도 있음을 확인했으며 이번 요청 밖이어서 보존했다. README에 추가한 Zone3 계약·개발 로그 링크와 anchor 대상은 존재한다.

## 미검증 범위와 해석

GPU·Isaac Sim을 시작하지 않아 실제 환경 생성·prestartup·물리 reset·IK 도달·전체 장애물 규모의 물리 안정성·PPO 학습은 미검증이다. CPU 검사는 위 순수 tensor 코드와 구성 계약을 확인한다. 새 방향에서 초기 자세 생성/IK가 실제 성공하는지, 당기기 성공률이 개선되는지, 기존 정책이 다른 방향에 과적합했는지는 확인하지 않았다.

이번 환경은 방향 분포와 보상 두 계수를 동시에 바꾼다. 새 학습 성능이 좋아져도 방향 제한만의 효과나 과적합 원인을 단독으로 확정할 수 없다는 실험 해석상의 한계가 있다. 기존의 Sweep 진행/후퇴 비대칭 비율5:1은 유지된다.
