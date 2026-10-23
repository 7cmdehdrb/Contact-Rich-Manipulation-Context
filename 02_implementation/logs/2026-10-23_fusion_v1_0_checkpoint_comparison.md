# Fusion v1_0 체크포인트 계측 비교 — 2026-10-23

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

사용자가 대상을 v1_3_1에서 v1_0으로 정정했다. 지정 TEMP run `2026-10-22_08-34-18_4833cc00/attempt_000`의 최신 저장 파일 `model_16400.pt`와 `model_10000.pt`를 각각16환경·내부 시간60초로 재생한다. 기존 v1_3_1 수집 자료는 이번 통계에 섞지 않는다.

## 구현과 측정 계약

`collect_fusion_reward_inputs.py`에 `--task` 선택을 추가했다. 기본값은 기존 v1_3_1이며 v1_0 선택 시 해당 등록 EnvCfg/runner를 읽는다. `RewardTelemetryEnv`는 기존 v1_0 runtime을 상속하여 reset 전 종료 표본을 보존한다. 보상·관측·물리·종료 함수는 변경하지 않았다.

EEF 속력은 페널티와 동일한 EEF 지점의 선속도 norm이다. 물체 접촉력 원시 CSV는 타겟을 포함한 모든 물체를 보존하되, 통계에서는 `active_objN`과 `target_id`로 활성 비타겟만 선택한다. 물체별 Hand normal contact 합력 크기와 실제 obstacle_contact 입력인 비타겟 벡터 합의 norm을 구분해 제공한다. 마찰 접선력은 이 contact sensor 값에 포함되지 않는다.

가속도는 활성 물체 COM 가속도 norm이며 타겟을 포함한다. 주 통계는 reset 첫 물리 표본을 포함하고, 페널티 유효 표본만 선택한 결과도 보충 CSV로 제공한다. RAW F/T는 보정 전 child joint 원점/축의 반력·모멘트이며 중력·관성 하중을 포함한다. EEF로 이동한 RAW와 보정된 실제 wrench_change 입력은 보충 통계로 구분한다.

임계값 미만을 제외한다: 접촉력0.02N, 가속도0.01m/s², RAW 힘0.2N, RAW 모멘트0.02Nm. 힘과 모멘트 필터는 독립 적용한다. 각 환경의 통과 표본을 동일 가중하여 중앙값·평균·최대를 계산한다. 물체별 표본을 환경별로 합친 통계와 환경·물체별 상세 통계를 모두 저장한다.

## 실행과 검증

실행 Python은 `/home/min/miniconda3/envs/env_isaaclab/bin/python`. GPU 접근이 가능한 실행 권한에서 아래 명령을 두 checkpoint에 각각 실행했다. 출력 폴더는 `outputs/fusion_reward_inputs/2026-10-23_v1_0_model<iteration>_dataset`이다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/scripts/collect_fusion_reward_inputs.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0 \
  --headless --num_envs 16 --steps 3000 \
  --checkpoint logs/TEMP/Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0/2026-10-22_08-34-18_4833cc00/attempt_000/model_<iteration>.pt \
  --output-dir outputs/fusion_reward_inputs/2026-10-23_v1_0_model<iteration>_dataset
```

두 실행 모두 학습 당시 source_env.yaml과 실행 env.yaml의 observations/rewards/actions/terminations/events/commands/curriculum/sim이 일치했다. 환경 수는16으로 변경했다. 커리큘럼은 해당 checkpoint iteration에 고정한다. seed42이지만 리셋 시점이 달라 같은 환경 ID가 동일 episode를 뜻하지 않는다.

CPU 검증 명령: `env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_fusion_reward_inputs.py src/inspire_sweep_baseline/tests/test_fusion_telemetry.py` → **4 passed**.

수집 후 각 폴더에 `scripts/validate_fusion_reward_inputs.py <dataset>` 실행, 통계는 비교 폴더의 `model16400/analyze.py`, `model10000/analyze.py`, `compare.py`, `finalize.py` 순서로 생성한다. 원시 데이터 SHA256, finite 값,3,000행·60초 시간축, episode/reset 경계, termination 원인, 가속도 유효성, 합력 상한, wrench 변화 계산과 통계 CSV 재읽기·독립 평균 검산을 확인한다.

## 결과와 범위

[이미지 모음](2026-10-23_fusion_v1_0_checkpoint_figures.md): PNG23개를 `03_assets/img/2026-10-23_fusion_v1_0_checkpoint_comparison/`에 복제했다. 원본과 복제본의 SHA256 및 모음 문서의 상대 링크를 확인했다.

두 실행 모두 정상 완료했고 validator를 통과했다. 각 환경3,000행·60초, checkpoint당48,000행이다. model_10000은 reset1,261건·관측 episode1,277개, model_16400은 reset1,182건·관측 episode1,196개다. 마지막 표본에서 reset된 경우 다음 빈 episode는 관측 episode에 포함되지 않는다. Markdown 수식 검사4파일 및 두 저장소의 `git diff --check`를 통과했다.

[결과 설명·통계·이미지](../../../../outputs/fusion_reward_inputs/2026-10-23_v1_0_comparison/README.md)에서 두 checkpoint 비교 이미지6개, 개별 checkpoint 이미지, 환경별·환경/물체별 CSV 및 원시 데이터로 이동할 수 있다. 각 원시 폴더의 `metadata.json`은 정확한 실행 명령·checkpoint 해시·단위·좌표계·유효 설정, `resets.csv`와 `episode_index.csv`는 리셋 원인과 episode 구간을 기록한다.

샘플링은50Hz 제어 step의 마지막 물리 substep이다. 최대값은 이 표본의 최대이며 모든 물리 substep의 연속 최댓값은 아니다. 여러 seed 반복 실행 및 학습 성능의 통계적 유의성은 검증하지 않았다.

## 추가 분포 이미지 — 2026-10-23

기존 원시 CSV에서 EEF 속력 전체 표본 및 활성 물체(타겟 포함) 가속도0.01m/s² 이상 표본을 읽어 두 checkpoint의 히스토그램·ECDF와16환경별 히스토그램, 총4개 PNG를 생성했다. 가속도는 reset 첫 표본을 포함하며 기존 통계와 같은 모집단이다. 전체 그래프는 표본 가중이며 환경별 그래프는 각 환경의 통과 표본수를 분모로 정규화한다. 동일 bin·전체 범위를 사용하고 꼬리를 자르지 않았다. 가속도 bin과 가로축은 로그 눈금이다.

실행: `MPLCONFIGDIR=/tmp/fusion_mpl /home/min/miniconda3/envs/env_isaaclab/bin/python -B outputs/fusion_reward_inputs/2026-10-23_v1_0_comparison/distributions.py`. 원본32개 CSV의 SHA256·각3,000행·finite 값·bin 표본수 보존·비율 합100%·복제 PNG 바이트 일치를 검증했다. bin별 count/percent와 분위수 및 검증 기록은 동일 비교 폴더의 `distributions/`에 보존한다. 이미지4개는 저장소 내부 이미지 폴더에 복제하고 [이미지 모음](2026-10-23_fusion_v1_0_checkpoint_figures.md)에 삽입했다.
