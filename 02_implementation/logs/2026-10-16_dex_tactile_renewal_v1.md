# Dex Tactile Renewal v1: 비용 상한·손목 높이·목표 방향

[개발 로그 목록](README.md) · [활성 환경 계약](../08_ACTIVE_ENVIRONMENTS.md) · [사용자 결정](../../01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md)

기준일: 2026-10-16. Workspace `main`, commit `301099db55cea61b7a715fcd8bf0b46d357214b2`. 문서 저장소 commit `92fcd2203c20ec47638474ea2085dd8a8a3d02b3`. 시작 시 문서 submodule 참조 차이 및 앞선 보상 수식 문서 2개·색인 2개의 미커밋 변경이 있었으며 그대로 보존했다.

## 요청과 적용

사용자는 앞으로의 환경 확장 기준을 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v0`로 지정했다. 실행기 기본 task 변경 지시는 아니므로 기본값은 변경하지 않고, 새 `Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1`을 등록했다. 환경 runtime은 `InspireSweepEnv`, Cfg는 `InspireDexTactileSweepOmniRenewalV1EnvCfg(InspireDexTactileSweepOmniRenewalEnvCfg)`다. Runner는 기존 Dex Tactile runner를 상속한 `InspireDexTactileSweepOmniRenewalV1PPORunnerCfg`이며 기본 로그 폴더만 `inspire_dex_tactile_sweep_omni_renewal_v1`로 분리했다.

1. `goal_rewards.exponential_pushing_speed_cost_limit`, `exponential_joint_speed_cost_limit`를 추가했다. 각각 물체 3D 선속도 norm, 선택 Arm 관절 최대 절대속도를 사용하며 임계값 0.3 m/s·1.0 rad/s를 유지한다. `max_cost=100.0`으로 양의 비용을 제한한다. 지수 계산 전에 `0.5 * log(1 + 2 * max_cost)`에 해당하는 초과 속도까지 제한하고 마지막 비용도 clamp하여 큰 입력에서 exp overflow와 반올림 상한 초과를 방지한다. 기존 무제한 함수는 유지하고 v1만 새 함수를 사용한다.
2. `mdp.shelf_collision`에 `wrist_clearance` 매개변수를 추가했다. 기본값은 기존 0.07 m이며 v1에서 0.03 m로 설정한다. 사용자가 기억한 0.7/0.3 대신 실제 구현의 0.07/0.03 m로 해석한 사실을 안내했다. 낮은 기준은 더 가까운 접근을 허용한다. 선반 속도 norm >0.1과 `check_fingers=False`, 선반 변위 0.05 m 종료 등은 유지한다.
3. `randomize_goal_object_scene`에 `excluded_x_half_angle`을 추가했다. 기본값 0은 전방향이며, v1은 `math.radians(15.0)`이다. 사용자의 추가 답변에서 확인한 **선반 로컬 ±X** 각각 ±15°를 제외하고 남은 두 호에서 각도 균등 샘플링한다. ±Y는 허용하며 시계 11–1시를 엄밀하게 해석한 ±30°로 확장하지 않았다. 물체 스폰 원판·최대 거리 0.15 m·가장자리 단축·선반 현재 좌표 변환·부분 reset은 유지한다.

상한 −100은 weight −1.0 적용 후 **시간 곱셈 전의 각 항 값**이다. RewardManager의 `step_dt` 곱셈을 유지하므로 제어 주기 0.02 s에서 항별 스텝 기여 하한은 −2다. 다른 보상을 포함한 전체 reward에 대한 하한은 아니다.

Actor/Critic 57D, 촉각 17채널·0.01 N 판정, 8D Action(Arm Joint Position 6D + Hand 2D), Dex 진행 보상·센서·물성·주기는 부모에서 상속한다. Arm/Hand raw Action 변화 제곱합 −0.03/−0.03 및 실제 관절 속도 제곱합 −0.03/−0.01은 유지한다. 현재 물체 GT를 받는 기준선이며 최종 Blind 정책과 구분한다.

## CPU 검증

Workspace 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider
```

결과: **299 passed, 17 subtests passed in 15.65s**.

검증 범위는 기존 비용과 포화 전 일치, 임계값 이하 0, 음수 방향 속도, 선택 Arm 분리, 큰 값·무한대 입력에서 유한한 비용과 상한 100, 사용자 지정 상한, invalid parameter, 실제 dt 적용값이다. 목표 샘플링은 20,000개 방향의 금지 구간 배제·허용 구간 균등성·회전된 선반 좌표·물체 원판·보드 안 목표·부분 reset을 확인했다. 손목 기준 완화와 strict 경계, 선반 선속도·각속도 종료 유지도 확인했다. 전체 설정 비교로 v0 불변 및 v1의 요청된 차이만 적용되는지, Gym·PPO 등록을 확인했다.

최초 관련 테스트는 82 passed·1 failed였다. 실패는 테스트에서 `configclass.to_dict()`의 함수 직렬화 문자열에 함수 객체를 비교한 오류였다. 직접 callable identity 검사와 직렬화 문자열 비교를 분리한 뒤 위 전체 검사가 통과했다.

## GPU 실행 확인

최초 기본 명령은 비대화형 셸의 `TERM=dumb`에서 `isaaclab.sh`의 `tabs 4`가 실패하여 Python 실행 전에 종료했다. 환경 기본 conda 경로 대신 프로젝트 Isaac Lab conda를 명시하고 `TERM=xterm`으로 다시 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  TERM=xterm CONDA_PREFIX=/home/min/miniconda3/envs/env_isaaclab \
  ./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1 \
  --num_envs 8 --max_iterations 1 \
  --experiment_name inspire_dex_tactile_sweep_omni_renewal_v1_smoke \
  --run_name validation --headless \
  > /tmp/dex_tactile_renewal_v1_smoke.log 2>&1
```

RTX 3090 / Isaac Sim 5.1에서 **exit 0**, 1 iteration 완료. 로그에서 policy shape 57, Actor/Critic 입력 57D, Actor 출력 8D, 활성 보상 10개, 두 속도 비용 weight −1.0을 확인했다. 학습 구간 6.0초이며 전체 simulator 초기화 시간을 포함한 수치가 아니다.

Run: `logs/rsl_rl/inspire_dex_tactile_sweep_omni_renewal_v1_smoke/2026-10-16_20-03-41_validation`. `params/env.yaml`, `params/agent.yaml`, TensorBoard event, `model_0.pt`, `git/grad.diff`가 생성됐다. 명령의 `--experiment_name`은 짧은 실행 확인용이며, 일반 v1 학습의 기본 폴더와 분리했다. 원시 표준출력은 위 `/tmp` 파일로 보존했으며 영구 추적 자산은 아니다.

일반 실행 명령:

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Dex-Tactile-Sweep-Omni-Renewal-v1 \
  --num_envs 2048 --headless
```

## 문서 검사와 한계

문서 저장소 루트에서 다음을 실행했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py 01_plan/00_HANDOFF_BRIEF.md 01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-16_dex_tactile_renewal_v1.md ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external 01_plan/00_HANDOFF_BRIEF.md 01_plan/03_DECISIONS_AND_OPEN_QUESTIONS.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-16_dex_tactile_renewal_v1.md ../../src/inspire_sweep_baseline/README.md
git diff --check
```

변경 Markdown 6개 수식 검사 통과, 내부 링크 142개·workspace 링크 33개 오류 0건. Workspace와 문서 저장소의 `git diff --check` 통과. 최초 문서 검사에서 경로·수식 escape 오류를 발견해 수정한 뒤 재검사했다. 기존 보상 수식 문서는 이번 환경 추가와 무관하게 보존했다.

GPU run의 저장된 `params/env.yaml`에서도 두 `_limit` callable·상한 100·weight −1.0, `wrist_clearance=0.03`, `excluded_x_half_angle=0.2617993877991494`를 확인했다.

미검증: 2048개 환경 장시간 학습·재개·재생 성능, 수렴·성공률, 실물 동작. 짧은 실행 확인은 이전 학습 중단 원인의 확정이나 장시간 안정성을 입증하지 않는다.
