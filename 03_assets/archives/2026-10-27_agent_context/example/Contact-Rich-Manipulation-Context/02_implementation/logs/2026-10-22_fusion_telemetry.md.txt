# Fusion v3의 16환경 F/T·물체 선속도 CSV 수집

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md#contact-sweep-clutter-fusion-v3--2026-10-21) · [실행·CSV 계약](../../../../src/inspire_sweep_baseline/README.md#fusion-v3-ft물체-선속도-csv-수집)

기준일: 2026-10-22. 지정 checkpoint의 16환경 재생과 전체 CSV 검증 완료. F/T 변화량과 물체 속도 페널티를 검토할 원시 CSV를 수집했다. 계수 선택·보상 변경·새 학습은 이번 작업 범위가 아니다.

## 요청과 기준 상태

사용자는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v3`와 `logs/rsl_rl/inspire_contact_sweep_clutter_fusion_v3/2026-10-21_21-55-18/model_7200.pt`를 기준으로 약 16개 환경의 6축 F/T와 각 물체의 XYZ 선속도를 시간별 CSV로 저장하도록 요청했다. 각속도는 기록하지 않는다.

Workspace HEAD는 `a2fcb0b`, 문서 submodule HEAD는 `f5655d0`이다. 시작 시 루트 `PLAN.md`, 문서 로그 색인의 변경과 untracked `2026-10-22_temp_training_log_cleanup.md`가 있었으며 보존했다. 로그 색인의 기존 충돌 표식도 이번 작업에서 수정하지 않았다. 체크포인트 SHA-256은 `0a03579f62e75aadca66f79018c61b0b351cb5b4f7e1f8b44709d7ea6a5a7d10`이다. 학습 로그 정리·수정·정책 export·commit·push를 수행하지 않는다.

## 구현과 계측 계약

- 수집기: [`collect_fusion_telemetry.py`](../../../../src/inspire_sweep_baseline/scripts/collect_fusion_telemetry.py). v3의 등록된 `ContactSweepClutterFusionV3EnvCfg`와 `ContactSweepClutterFusionV3PPORunnerCfg`, 기존 `CurriculumOnPolicyRunner`를 사용한다. 학습과 동일하게 checkpoint iteration 7200을 복원하고 재생 중 고정한다.
- 실행 클래스: [`ContactSweepClutterFusionTelemetryEnv`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/contact_sweep_clutter_fusion_telemetry.py) → `ContactSweepClutterFusionEnv` → Isaac Lab `ManagerBasedRLEnv`. 신규 Gym ID는 추가하지 않는다. 상속된 물리·Scene·Action·관측·보상·커리큘럼·종료 구성을 사용한다.
- 데이터 책임: [`PlaybackTelemetry`와 `PlaybackCSVWriter`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/contact_sweep_clutter_fusion_telemetry.py). 전자는 상태 취득·episode 경계, 후자는 환경별 열의 CSV 스트리밍 저장을 맡는다. 부모 step loop를 복제하지 않는다.
- F/T: 정책과 기존 변화율 비용이 사용하는 `PureWristWrench`의 실제 cached `pure_world`·`pure_eef`. Hand 중력·관성 하중 보정 후 반력이며 힘 N, 모멘트 N·m다. 두 파일 모두 모멘트 원점은 EEF, 부호는 parent-on-child이며 `world`·`eef`는 표현 축이다. 보정 추정은 실물 측정 정확도 검증이 아니다.
- 선속도: `object_collection.data.object_lin_vel_w`. Isaac Lab의 `object_com_lin_vel_w` alias로, 월드 축 COM 선속도 m/s다. Target=`mass_cylinder`, 장애물은 `obstacle_0`·`obstacle_1`·`obstacle_2`이며 각 환경에 4개다. GT 속도를 Actor 입력에 추가하지 않는다.
- 주기: physics 0.01초, control 0.02초. 제어 step의 마지막 물리 substep을 계측하며 모든 physics substep의 100 Hz 기록과 구분한다. `time`은 벽시계가 아닌 누적 시뮬레이션 초이고 첫 행은 0.02초다. 16환경이 같은 시간 행에 들어간다.
- 종료: `_reset_idx`에서 부모 reset 전에 종료 환경을 취득하고, 나머지는 부모 step 직후 취득한다. `sensor_data_fresh`와 capture mask로 누락·중복·reset 값 덮어쓰기를 거부한다. 추가 noisy observation 계산이나 stateful reward 재평가는 하지 않는다.
- 차분: `episodes.csv`의 현재 행 `delta_valid_N=0`은 첫 표본 또는 reset 이후 첫 표본이다. 이 행의 F/T 차분은 제외한다. 기존 변화율 비용의 축과 비교하려면 `wrench_world.csv`의 `(현재−이전)/0.02`를 사용한다. EEF 축의 차분은 Hand 회전에 따른 축 변화도 포함한다.

## 실행과 산출물

현재 호스트의 `/home/min/miniconda3/envs/env_isaaclab/bin/python`을 사용했다. Torch 2.7.0+cu126, RSL-RL 5.0.1, Isaac Sim 5.1, NVIDIA GeForce RTX 3090이다. 샌드박스 안의 첫 GPU 점검은 CUDA unavailable이었으며, 승인된 샌드박스 밖 실행에서 GPU 접근을 확인해 실제 계측했다. 드라이버·패키지·네트워크 설정을 변경하지 않았다.

Workspace 루트에서 실제 실행한 본 수집 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/scripts/collect_fusion_telemetry.py \
  --headless --num_envs 16 --steps 5000 \
  --output-dir outputs/fusion_telemetry/2026-10-22_model7200_dataset
```

기본 checkpoint는 위 지정 파일이며 `--checkpoint`로 다른 파일을 지정할 수 있다. 기본 출력 폴더는 `outputs/fusion_telemetry/<UTC timestamp>`다. 출력 폴더는 새로 생성하며 기존 폴더를 덮어쓰지 않는다. 학습 로그 내부 출력은 거부한다. GUI는 `--headless`를 빼고 `--real-time`으로 실시간 속도를 요청할 수 있다.

| CSV | 스키마 |
| --- | --- |
| [wrench_world.csv](../../../../outputs/fusion_telemetry/2026-10-22_model7200_dataset/wrench_world.csv) | 97열: `time,Fx_0,Fy_0,Fz_0,Mx_0,My_0,Mz_0,...,Mz_15` |
| [wrench_eef.csv](../../../../outputs/fusion_telemetry/2026-10-22_model7200_dataset/wrench_eef.csv) | 97열: 동일 순서, EEF 축 |
| [object_velocity.csv](../../../../outputs/fusion_telemetry/2026-10-22_model7200_dataset/object_velocity.csv) | 193열: `time,vx_Target_0,vy_Target_0,vz_Target_0,vx_obstacle_0_0,...,vz_obstacle_2_15` |
| [episodes.csv](../../../../outputs/fusion_telemetry/2026-10-22_model7200_dataset/episodes.csv) | 97열: 환경마다 episode ID·step·terminated·time_out·delta_valid·target_id |

본 수집은 **5,000행/파일, 환경당 100초, 전체 1,600 환경·초**로 완료했다. 파일 크기는 월드 F/T 10,438,615 bytes, EEF F/T 11,025,382 bytes, 선속도 21,863,360 bytes, episode 2,106,105 bytes다. 생성 산출물은 workspace `outputs`에 보존하며 이 문서에서 연결한다.

- [본 수집 metadata](../../../../outputs/fusion_telemetry/2026-10-22_model7200_dataset/metadata.json): `status=complete`, iteration 7200, checkpoint 해시·좌표계·단위·물체 순서·적용 reward 설정·열 정의.
- [본 수집 stdout](../../../../outputs/fusion_telemetry/2026-10-22_model7200_dataset.log): 실제 GPU 초기화와 5,000 step 완료 기록.
- [원본 학습 설정 대조](../../../../outputs/fusion_telemetry/2026-10-22_model7200_dataset/source_config_match.json): observations/rewards/actions/terminations/events/commands/curriculum/sim의 8개 구성과 agent 설정이 일치했다. Scene은 환경 수와 생성 시 확장되는 prim path 표현을 정규화한 뒤 일치했다. YAML은 `yaml.BaseLoader`로 값만 읽어 비교했으며 config 객체를 실행하지 않았다. 원본 `source_env.yaml`·`source_agent.yaml`과 수집 설정 `env.yaml`·`agent.yaml`을 같은 폴더에 보존했다.
- [CSV·설정·코드·checkpoint manifest](../../../../outputs/fusion_telemetry/2026-10-22_model7200_dataset/manifest.json): 파일 크기와 SHA-256. 수집 후 checkpoint 해시가 시작 값과 동일함을 확인했다.

## 검증

16환경·20 step의 [실제 GPU smoke metadata](../../../../outputs/fusion_telemetry/2026-10-22_model7200_smoke/metadata.json)와 [검증 결과](../../../../outputs/fusion_telemetry/2026-10-22_model7200_smoke/validation.json)는 complete/passed다. 각 파일 20행, 16환경·물체 4개, F/T 두 좌표계 norm 일치·유한값·시각 정렬을 확인했다. 이 짧은 실행에는 terminal transition이 없었다.

CPU 검증은 다음 명령을 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  -q -p no:cacheprovider src/inspire_sweep_baseline/tests
```

[CPU stdout](../../../../outputs/fusion_telemetry/pytest.log): **461 passed**, 기존 ONNX deprecation 경고 3개. 추가 검사는 부분 reset 시 terminal F/T·4개 물체 선속도 보존, 환경·물체·축별 CSV 열 대응, reset 차분 분리, missing/duplicate/stale/nonfinite 거부, 덮어쓰기 방지, 부모 lifecycle 호출 순서를 확인한다. 이후 validator의 reset 오류 거부 검사를 보강하고 해당 파일을 재실행해 **3 passed**를 확인했다. 합성 fixture는 물리 데이터가 아니며 실제 GPU 결과와 구분한다.

본 CSV의 전체 검사 명령:

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  src/inspire_sweep_baseline/scripts/validate_fusion_telemetry.py \
  outputs/fusion_telemetry/2026-10-22_model7200_dataset
```

[전체 검증 결과](../../../../outputs/fusion_telemetry/2026-10-22_model7200_dataset/validation.json)는 **passed**다. 4파일 각 5,000행, 정확한 스키마·환경별 열 순서·유한값·모든 파일의 0.02초 시각 정렬·episode 연속성·월드/EEF 힘 및 모멘트 norm 일치를 확인했다. **종료 직전 전이 160개**가 보존되었고, 초기/episode 첫 표본 160개의 `delta_valid=0`을 확인했다. 환경마다 마지막 행도 terminal을 보존하며 그 뒤 reset 상태는 기록하지 않는다. 이 검증은 CSV 일관성 검사이며 물리 모델의 실물 정확도 검증과 구분한다.

변경 문서 4파일의 Markdown 수식 검사는 통과했고, 링크 검사는 내부 169개·workspace 외부 파일 83개·오류 0이었다. 검사 명령은 문서 저장소에서 다음과 같다.

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/logs/2026-10-22_fusion_telemetry.md \
  02_implementation/logs/README.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external \
  02_implementation/logs/2026-10-22_fusion_telemetry.md \
  02_implementation/logs/README.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  ../../src/inspire_sweep_baseline/README.md
```

변경 대상의 두 저장소 `git diff --check`는 통과했다. Workspace 전체 검사에서는 기존 사용자 변경 `PLAN.md:3`의 trailing whitespace가 보고되어 해당 파일을 수정하지 않고 이번 변경 범위만 확인했다.

여러 seed·checkpoint의 비교, 보상 계수 산정·변경·학습, 실물 센서 보정 성능은 검증하지 않는다. 본 CSV는 지정 정책의 단일 seed 재생 데이터다.
