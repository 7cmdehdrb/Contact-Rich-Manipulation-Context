# Finger-ForceDirection-v0: 보상1cm·성공3cm 분리

2026-11-13. 사용자 요청으로 `Inspire-Sweep-Simple-Finger-v0-Test`의 직접 자식 `Inspire-Sweep-Simple-Finger-ForceDirection-v0`을 추가했다. 부모가 안정적으로 동작한다는 가정 아래 접촉력 방향 보상으로 정확도를 높이는 실험이다. 부모 안정성을 확정하거나 현재 .180/.250 학습 상태를 변경하지 않았다. 사용자가 최종 이름을 `Finger-ForceDirection-v0`로 지정하여 등록 ID·설정 클래스·실험명을 맞췄다. 최초 제안 이름의 임시 smoke 산출물은 보존하고, 최종 이름으로 재검증했다.

[최종 환경 설명](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#finger-forcedirection-v0-1cm-보상과-3cm-성공).

## 변경 기준과 요청 해석

코드 기준 HEAD는 `9e0328fccb3e4c4cb2e5bccab57d605139e0e48b`; 시작 시 source 작업트리는 깨끗했다. 문서 submodule의 기존 학습 현황 갱신·미추적 로그는 보존했다. 리뷰 범위는 `git diff 9e0328fccb3e4c4cb2e5bccab57d605139e0e48b -- src/inspire_sweep_baseline`이다.

| 항목 | 부모 Test | 새 환경 |
| --- | --- | --- |
| EnvCfg 직접 부모 | Finger-v0 | Finger-v0-Test |
| 힘 방향 보상 | 없음 | 기존 Semi-Prof 함수, weight0.33·수평 최소1N·방향 예외1cm |
| 무조건 접촉 보상 반경 | XY<3cm | XY<1cm |
| 성공 종료 | timeout, XY<3cm, 실패 없음 | 동일 |
| 목표 내부 비율 메트릭 | XY≤3cm | 동일 |
| timeout 성공률 | 성공 종료 결과 집계 | 동일 |
| 손 관측·액션/전체 관측 | drive6·action12/policy66+obstacles64 | 동일 |
| Runner Clip/Last Action | ±π/2/raw 그대로 | 동일 |
| 팔 속도 종료/해당 일정 | >1rad/s/None | 동일 |
| action-rate | 팔/손6축 제곱합, cap 없음 | 동일 |
| PPO | 부모 모델·분포·하이퍼파라미터 | 실험명만 `_force_direction` 추가 |

1cm는 방향 각도 예외와 접촉 간주용이며 성공 반경을 바꾸지 않는다. 부모의 정확한 비교 연산자도 보존했다. 정확히1cm에서 보상 예외는 없고, 정확히3cm에서는 목표 내부 비율에만 포함되며 성공 종료는 아니다. 보상 예외를 만족하지 않아도 실제 접촉/힘이 올바르면 정상 보상을 받을 수 있다.

힘 방향은 기존 함수가 정의한 현재 목표 방향을 사용한다. 물체에 작용하는 손 접촉의 법선+마찰 합력을 physics substep마다 수집하고 현재 policy step에서 평균한다. 선반 XY 기준의 현재 물체→목표 방향과3D 힘을 비교하므로 수직 성분도 감점에 반영된다. 각도0/45/90도 점수는1/0.25/0, weight0.33·dt는 RewardManager가 적용한다. XY<1cm에서는 각도만 무시하며 실제 접촉, 유효한 샘플, 수평 합력≥1N은 계속 요구한다.1cm 예외는 latch가 아니어서 다시 멀어지면 즉시 각도 계산을 따른다.

## 구현·최종 전체 대조

- `mdp/reward_functions/sweep_simple.py`: 기존 `GoalContactMaintenance`에 `goal_radius=.03` 선택 인자를 추가했다. 기본값·연산자·접촉 이력·count+1/−2·cache/reset을 보존하고 새 자식만 `.01`을 전달한다. 성공용 cfg와 연결하지 않는다.
- `mdp/rewards/sweep_simple.py`: `SweepSimpleFingerForceDirectionRewardsCfg`가 부모의 유효 `SweepSimpleFingerRewardsCfg`를 상속한다. `force_direction` 추가와 `hand_contact.params.goal_radius=.01`만 바꾼다. 새 양의 항은 `wrench_change` 직전에 삽입하고 기존 항 사이 상대 순서는 유지한다.
- 기존 Wrench의 양의 보상 연동5% 예산을 유지했다. 새 양의 항을 맨 뒤에 추가하면 커리큘럼으로 비용이 켜질 때 순서 검사에 실패하므로 위치를 명시했다. 기존 비용 함수·가중치·예산 파라미터는 그대로이며, 새 양의 보상이 예산 합계에 포함되는 것은 기존 정의에 따른 변화다. Semi-Prof의 예산 제거는 가져오지 않았다.
- `envs/sweep_simple_envs.py`: Test 직접 상속, rewards만 교체.
- `runtime/sweep_simple.py`: Test가 실제 사용하는 `SweepSimpleFingerEnv`의 직접 자식에 force sampler만 연결. 기존 Semi-Prof의 작은 scoped scene-update hook과 sampler를 재사용하는 동일 패턴이며, Finger-v1의 raw clip runtime을 상속하지 않는다. 예외 시 hook 복원과 부분 reset을 유지한다. 기존 runtime 클래스는 수정하지 않았다.
- `agent/sweep_simple_ppo_cfg.py`: Test Runner 직접 상속, 실험명만 `inspire_sweep_simple_finger_force_direction_v0`으로 변경.
- `__init__.py`: 새 ID/EnvCfg/runtime/PPO 연결.

전체 설정 비교에서 EnvCfg 차이는 위 두 보상 항, PPO 차이는 실험명뿐이다. 자식 인스턴스를 수정해도 기존 및 새 Test 인스턴스가 바뀌지 않는다. Scene/자산/물성/센서, Action/Observation, Command/Event/IK/reset 배치, 나머지 Reward 함수·params·weight, Termination/Curriculum, 모델·초기 Gaussian std·클립·PPO 값과 부모 경계 동작은 보존했다. 추가 센서 쿼리는 힘 방향 보상에 필요한 실행 비용이다. 반경3cm를1cm로 전역 변경하거나 새 관측을 Actor에 제공하지 않았다.

## CPU 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_wrench.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_semi_prof.py \
  -q -p no:cacheprovider --tb=short
```

**최종 이름 반영 후76 passed in12.49s** (이름 변경 전76 passed in12.15s). 새 경계 fixture 초기 실행에서는 float32 거리값을 float64 위치에 복사한 경계 오차, 기본 CPU timeout no-op, 합성 robot/EEF 텐서 dtype 불일치를 순서대로 확인했다. 위치 dtype의 경계값과 설치된 실제 Isaac Lab timeout 함수, 일관된 metric 텐서 dtype을 사용하도록 fixture를 수정했다. 경계 기대값을 완화하지 않았다. 이후 해당 파일17개와 전체76개가 통과했다.

- 부모·자식 전체 Env/PPO 차이, 직접 상속·등록·부모 격리.
- 거리0.009999/0.01/0.010001/0.02/0.029999/0.03/0.030001m에서 실제 contact, force reward, success termination, runtime metric 함수 대조.2cm에서 성공 판정은 가능하지만 무조건 보상 예외는 없음을 확인.
- 비접촉·높이 초과에서도1cm 안은 contact20, 나가면 해제·count감쇠·동일 step cache 유지. force는 실제 접촉/힘 조건 유지.
- 기존 힘 각도·수직 힘·목표 overshoot·약한 힘·stale/NaN·물리 substep 평균·friction 유효 범위·부분 reset 검사를 재사용.
- 새 runtime의 physics 수집→reward→reset 순서 및 정상/예외 모두 hook 복원 검사.
- **실제 RewardManager**에서 iteration0/1000/1250/3000/6000 커리큘럼을 적용해 Wrench 비용 활성화 후도 정상 계산, 새 힘 보상 포함5% 예산 유지 확인. 방향 보상0/1 양쪽 검사.

CPU simulator asset/scene 일부는 double이며 실제 PhysX를 대체하지 않는다.

## GPU 검증

RTX3090·Isaac Sim5.1, seed42. 기존 학습 로그에 쓰지 않고 절대 experiment 경로를 사용했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONUNBUFFERED=1 /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/scripts/train.py \
  --task Inspire-Sweep-Simple-Finger-ForceDirection-v0 \
  --num_envs 64 --headless --max_iterations 2 --seed 42 \
  --experiment_name /home/min/7cmdehdrb/grad/outputs/finger_force_direction_v0/training \
  --run_name smoke
```

**64환경·36step/env·PPO2 iterations 정상 완료, exit0**. [stdout](../../../../outputs/finger_force_direction_v0/train_stdout.log) · [run](../../../../outputs/finger_force_direction_v0/training/2026-11-13_18-08-42_smoke).

저장 YAML에서 두 보상 반경0.01, 성공 cfg/command 반경0.03, 힘 가중치0.33·수평 최소1N, force-before-wrench 순서·기존5% 예산, clipπ/2·raw Last Action·1rad/s 종료·해당 curriculum null을 확인했다. model_0/model_1 각각100개 tensor 모두 유한하고 Actor/Critic encoder가 실제 갱신됐다. Actor MLP 입력(256,82), 출력(12,64)도 부모와 같다.

초기 무작위 정책의 force_direction 에피소드 로그는0이며, 이 smoke만으로 정렬 보상에 의해 행동이 개선됐거나 실제 접촉 양의 보상 상황이 충분히 발생했다고 주장하지 않는다. 실제 물리 호출 경로는 실행했고, 비영점 보상/각도/경계는 CPU 합성 힘 검사로 확인했다.

## 코드리뷰

`code-review` 스킬로 기준 HEAD 대비 Standards와 Spec을 독립 검토했다. 사용자가 요구한 검토→문서 갱신 순서를 따랐다.

- **Standards:** 직접 상속·부모 보존·역할 배치 위반 없음. 리뷰 중 새 경계 테스트의 timeout stub 실패를P2로 지적받았으며 실제 timeout 함수 연결·dtype 보정 후76개 통과로 해결했다. 후속 재검토에서 미해결0건. 작은 sampling hook 중복은 기존 runtime 변경을 피하기 위한 합리적 범위 제한으로 판단했다.
- **Spec:** 누락·오구현·범위 확장 발견0건. 보상1cm와 종료/메트릭3cm, 부모 Clip/LastAction/속도/PPO, 유효 접촉·수평1N 요구를 확인했다. 기존 `<`/`≤` 경계 차이와 장기 성능 미검증을 문서에 명시하도록 반영했다.

## 문서와 한계

현재 인계·활성 환경·Simple 설명서/상속도/등록17개·로그 색인을 갱신했다. 현재 .180 Test·.250 Prof-v2 학습 현황은 유지하고 새 환경의 장기 학습 개시를 추정하지 않았다.

장기 안정성·목표 정확도 향상, 실제 비영점 접촉에서의 힘 방향 통계·학습 성능, 부모 checkpoint resume/play/export 및 대규모 환경 처리량은 미검증이다. 이번 구현은 신규 학습 smoke 기준이며 모델 차원이 같다는 것만으로 정책 전이 성능을 보장하지 않는다.

변경5개 Markdown 수식 검사·외부 경로 포함 링크 검사·전체583개 문서 링크 검사·양쪽 git diff --check를 통과했다. 별도 렌더링은 미검증이다. 최종 이름 변경 후도 같은 검사를 다시 통과했다. 초기 검사 명령의 잘못된 작업 디렉터리는 문서 저장소로 정정해 실행했다.
