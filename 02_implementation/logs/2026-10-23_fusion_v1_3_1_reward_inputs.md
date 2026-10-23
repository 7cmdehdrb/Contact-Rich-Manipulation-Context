# Fusion v1_3_1 페널티 입력 계측 — 2026-10-23

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-fusion-v1_3_1--2026-10-22)

## 요청과 대상

사용자 지정 `model_14500.pt`로 16개 환경을 실행하며 환경당 시뮬레이션 약 500초의 EEF 선속력·물체별 Hand 접촉 합력 크기·물체별 COM 가속도 크기·RAW F/T를 수집한다. 환경별 episode와 reset을 분명하게 구분한다. 대상 task는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3_1`, 체크포인트는 `logs/resilient/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_3_1/2026-10-22_10-27-21_5c4cf77b/attempt_000/model_14500.pt`다.

기준 workspace HEAD `16a2a3e`와 기존 모니터링 주석·문서 변경을 보존했다. 체크포인트 SHA-256은 `80f59fb6a947e286f75135055cc023e341b01295788c290debc640d8b468bee9`다. 기존 학습 로그는 읽기 전용이며 보상·종료·정책 입력·계수는 바꾸지 않는다. 이전 v3 F/T 수집기와 별도의 v1_3_1 계측 진입점을 추가했다.

## 실행 클래스와 측정 계약

[`RewardTelemetryEnv`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_v1_0/reward_telemetry.py)는 `ContactSweepClutterFusionV1_0Env`를 상속한다. 등록된 v1_3_1 EnvCfg/PPOCfg와 `CurriculumOnPolicyRunner`로 checkpoint를 복원하며 별도 Gym task ID는 등록하지 않는다. iteration 14500의 커리큘럼을 적용한 뒤 reset하고 첫 측정 episode를 시작한다. 재생 중 iteration은 고정한다. 부모 물리 step loop를 복제하거나 추가 observation·stateful reward를 평가하지 않는다.

`RewardPlaybackTelemetry`는 물리값·경계 취득을, `RewardCSVWriter`는 환경별 CSV와 reset 이벤트 저장을 담당한다. 종료 환경은 `_reset_idx()`의 부모 reset 전에 취득하고 비종료 환경은 부모 step 후에 취득한다. 측정 중에는 freshness·중복·누락·유한값 검사를 수행하며, F/T는 stateful 페널티가 보존한 실제 입력과 정확히 일치하는지도 확인한다.

| 요청 항목 | 수집 열·정의 |
| --- | --- |
| eef_linear_speed | `eef_linear_speed_m_s`: 기존 함수와 동일하게 `norm(body_link_lin_vel + cross(body_link_ang_vel, EEF-body_link 위치))`. COM 속도로 대체하지 않는다. |
| obstacle_contact | `contact_force_N_obj0`~`obj6`: 물체별 `norm(-sum(force_matrix_w, hand filters))`. 타겟도 별도 기록한다. `obstacle_net_force_N`은 기존 함수가 활성 비타겟 벡터를 합한 뒤 취하는 norm이며 물체별 norm 합과 구분한다. |
| object_acceleration | `acceleration_m_s2_obj0`~`obj6`: 마지막 물리 substep의 PhysX `object_com_lin_acc_w` 3D norm. `active_objN`과 `acceleration_valid_objN`으로 비활성·reset 직후 제외 상태를 별도 기록한다. |
| wrench_change | `raw_joint_*`: 보정 전 incoming joint 6축 반력, child joint 원점/축. `raw_eef_*`: 보정 전 반력을 EEF 원점/축으로 변환. `penalty_eef_*`: 실제 페널티에 들어가는 Hand 중력·관성 보정 후 F/T. `penalty_world_*`도 기록한다. |

접촉 센서는 물체와 전체 Hand 사이의 **normal contact force**를 보고한다. 접선 마찰력, 중력, 선반 등 모든 외력을 합한 값이 아니다. F/T 부호는 parent-on-child이며 raw_joint와 EEF 표본은 모멘트 원점이 다르다. 보정 후 힘/모멘트 크기의 절대 변화량도 기록하되 reset 첫 행은 유효하지 않으므로 0으로 표시한다. 변화량은 rate가 아니며 dt로 나누지 않는다.

물체 순서는 obj0=Target `mass_cylinder`, obj1~3=Gray `obstacle_0`~`obstacle_2`, obj4~6=White `obstacle_3`~`obstacle_5`다. 원본 물체 속도 XYZ도 함께 보존한다.

제어 주기 0.02초, 물리 주기 0.01초다. 50Hz로 마지막 물리 substep을 측정하며 100Hz의 모든 물리 substep 기록과 구분한다. 수집 시간은 reset이 일어나도 계속 증가한다. 첫 행은 0.02초, 마지막은 500초다. 초기 목표는 각 환경 25,000행, 합계 400,000개 환경별 표본이었다. 후속 요청에 따른 실제 중단 구간은 아래 결과를 따른다.

## 명령과 파일

GPU 접근은 기본 샌드박스에서 차단됐고 승인된 샌드박스 밖 실행에서 RTX 3090을 확인했다. 드라이버·시스템 설정은 변경하지 않았다. Torch 2.7.0+cu126, RSL-RL 5.0.1, Isaac Sim 5.1 환경이다.

실제 GPU smoke 실행은 본 명령에서 `--steps 100`, 출력 폴더 끝을 `_smoke`로 바꾸어 수행했다. 환경당 2초 수집과 validator를 통과했고 실제 object_drop reset 1건을 포함했다. observations/rewards/actions/terminations/events/commands/curriculum/sim과 agent 설정이 저장된 학습 설정과 일치했다.

본 수집 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/scripts/collect_fusion_reward_inputs.py \
  --headless --num_envs 16 --steps 25000 \
  --output-dir outputs/fusion_reward_inputs/2026-10-23_model14500_dataset
```

출력은 `outputs/fusion_reward_inputs/2026-10-23_model14500_dataset`다. 기존 폴더를 덮어쓰지 않는다.

- [데이터 설명](../../../../outputs/fusion_reward_inputs/2026-10-23_model14500_dataset/DATA_README.md): 열·단위·물체 ID·pandas 읽기 예시.
- `env_00.csv`~`env_15.csv`: 각 환경의 모든 물리 표본·episode ID/step·종료 bit·delta validity.
- `resets.csv`: 종료 시각, 환경 ID, 끝난/다음 episode ID, 종료 원인. 동일 step의 복수 원인은 모두 기록한다.
- `episode_index.csv`: validator가 만든 환경·episode별 시작/끝·표본 수·완료 여부·종료 원인.
- `environment_summary.csv`: 환경별 행 수·reset 횟수·최대 관측값.
- `metadata.json`: 상태·checkpoint 해시·복원 iteration·적용 threshold·스키마·좌표계·샘플링 계약.
- `source_env.yaml`/`source_agent.yaml`: 학습 당시 저장 설정. `env.yaml`/`agent.yaml`: 실제 수집 초기 설정.
- [본 수집 stdout](../../../../outputs/fusion_reward_inputs/2026-10-23_model14500_dataset.log).

## 검증

CPU 검증 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_fusion_reward_inputs.py \
  src/inspire_sweep_baseline/tests/test_fusion_telemetry.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_contacts.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_object_state.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_rewards.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_safety_rewards.py
```

**62 passed in 2.49s**. 합성 표본으로 EEF 각속도 transport, 물체별 벡터합 norm, native 가속도 norm, reset 첫 표본 유효성, 종료 표본의 partial reset 이후 보존을 확인했다. 첫 CPU 실행에서는 Boolean 값을 Float 버퍼에 대입한 dtype 오류를 발견해 명시적 dtype 변환으로 수정한 뒤 통과했다.

본 수집 종료 후 전체 CSV 검증 명령:

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/scripts/validate_fusion_reward_inputs.py \
  outputs/fusion_reward_inputs/2026-10-23_model14500_dataset
```

전체 검증은 schema·행 수·시간 정렬·유한값·episode/step 연속성·reset 이벤트/종료 bit 대응·차분 경계·가속도 유효성·합력의 삼각 부등식·EEF/world F/T norm 일치·보정 후 norm 변화량 재계산을 검사한다. 결과는 수집 완료 후 아래에 기록한다.

## 본 수집 결과

사용자가 본 수집 도중 150~200초 구간에서 중단하도록 요청했다. 해당 Python 프로세스에 SIGINT를 보내 **환경당162.14초, 8,107개 제어 step**에서 종료했다. 16개 CSV 모두 같은 시간 범위·행 수·91열을 갖고 전체 표본 수는 **129,712개**다. CSV와 색인 합계 크기는172,500,470 bytes다.

전체 validator 결과는 **passed**다. reset **257건**, 관측 episode **273개**를 기록했다. 환경0~10·12~15는 각각16회, 환경11은17회 reset됐다. 원본의 마지막 표본은 정상적인 episode 중간일 수 있으므로 episode_index의 completed=False로 구분한다. 이는 500초를 완료한 데이터가 아니며 사용자 수정 범위를 충족한162.14초 데이터다.

Kit의 SIGINT fast shutdown이 Python 수집기의 최종 metadata 기록을 건너뛰어 초기 running JSON이 남았다. 이를 metadata_at_start.json으로 보존하고, 모든 실제 CSV를 읽어 확인한 행 수·시간과 user-stop 상태를 metadata.json에 기록했다. 스키마·runtime·threshold 정보는 같은 checkpoint/registry config로 완료한 smoke 기록에서 복원했으며 그 출처를 명시했다. 실제 full 실행의 source/config 대조 결과는 observations/rewards/actions/terminations/events/commands/curriculum/sim·agent 모두 일치다. 초기 환경 수2048→16만 수집 규모에 맞게 조정했다. checkpoint 해시는 중단 후에도 시작값과 동일했다.

[데이터 설명](../../../../outputs/fusion_reward_inputs/2026-10-23_model14500_dataset/DATA_README.md) · [환경0 CSV](../../../../outputs/fusion_reward_inputs/2026-10-23_model14500_dataset/env_00.csv) · [Reset 이력](../../../../outputs/fusion_reward_inputs/2026-10-23_model14500_dataset/resets.csv) · [Episode 색인](../../../../outputs/fusion_reward_inputs/2026-10-23_model14500_dataset/episode_index.csv) · [전체 검증](../../../../outputs/fusion_reward_inputs/2026-10-23_model14500_dataset/validation.json).

코드·데이터·설정 SHA-256은 manifest.json으로 보존한다. 문서 수식 검사와 두 저장소의 git diff --check를 통과했다. 실물 F/T 정확도·성공률 평가는 이번 수집으로 검증하지 않는다.
