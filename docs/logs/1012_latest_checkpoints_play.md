# 2026-10-12 — 로그 문서의 환경별 최신 체크포인트와 재생 명령

- **상태:** 체크포인트 목록과 명령어 정리 완료. 실제 시뮬레이션 재생·녹화는 미실행.
- **대상:** [1009 진행 기록](1009.md), [1010 진행 기록](1010.md)에 명시된 9개 환경.
- **검색 범위:** `/home/min/7cmdehdrb/grad/rsl_rl`, `/home/min/7cmdehdrb/grad/logs/rsl_rl`.
- **선정 기준:** 환경별 학습 폴더명 앞의 `YYYY-MM-DD_HH-MM-SS`를 비교해 가장 최근 학습을 선택한 뒤, 그 안에서 `model_N.pt`의 N이 가장 큰 파일을 선택함. 파일 수정 시각이나 보상 점수로 선택하지 않음.
- 저장된 `params/agent.yaml`의 experiment와 `params/env.yaml`의 관측·보상 구성을 대조함. 선택한 7개 체크포인트의 Actor 입력·출력 크기도 확인함.
- `rsl_rl`와 `logs/rsl_rl`은 서로 다른 위치이며, 아래 명령은 발견한 실제 절대 경로를 사용함.

## 최신 체크포인트 요약

| 학습 환경 ID | 최신 학습 폴더명 | 체크포인트 | Actor 관측 / Action |
| --- | --- | --- | --- |
| `Isaac-Sweep-Inspire-Right-OSC-v1` | `2026-10-08_20-54-43_center_reach_separate_reset` | `model_13200.pt` | 48D / 8D |
| `Isaac-Sweep-Inspire-Right-OSC-v2` | `2026-10-08_16-28-21_wrist_gate_up_alignment` | `model_1900.pt` | 71D / 8D |
| `Isaac-Sweep-Inspire-Right-OSC-v3` | `2026-10-08_19-37-22_close_sweep_0p5cm_no_sensors` | `model_300.pt` | 48D / 8D |
| `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v0` | `2026-10-09_18-09-20_inspire_open_joint_position` | `model_42100.pt` | 32D / 6D |
| `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v1` | `2026-10-09_18-09-55_inspire_hand_2d` | `model_24700.pt` | 34D / 8D |
| `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v2` | `지정 폴더에서 미확인` | `미확인` | 57D / 8D (설정 기준) |
| `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v1-mass` | `2026-10-10_14-32-43_inspire_hand_mass_cylinder` | `model_11750.pt` | 34D / 8D |
| `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v2-mass` | `2026-10-10_21-55-16_inspire_mass_z4cm_correct_alignment` | `model_89999.pt` | 41D / 8D |
| `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v3-mass` | `지정 폴더에서 미확인` | `미확인` | 41D / 8D (설정 기준) |

## 명령어 사용 기준

- 모든 명령은 저장소 루트 `/home/min/7cmdehdrb/grad`에서 실행함. 가상환경은 기존 Isaac Lab 실행 환경을 사용함.
- 실행용은 `--num_envs 1 --real-time`, 녹화용은 `--num_envs 1 --video --video_length 500 --headless`를 사용함. 녹화는 500 policy step으로, 현재 제어 주기 0.02초 기준 약 10초의 시뮬레이션 영상임.
- 영상은 선택한 체크포인트의 학습 폴더 아래 `videos/play/`에 저장됨. `--video`가 카메라 활성화를 자동 처리함.
- OSC 재생 스크립트에 `--video`, `--video_length`와 `--enable-sensor-observations`를 추가함. OSC-v2의 선택된 체크포인트는 Tactile·F/T를 포함한 71D이므로 이 관측 옵션이 필요함. 현재 기본 관측 48D로는 로드할 수 없음.
- 명령은 현재 환경 코드를 사용함. 특히 OSC-v2는 센서 입력 크기를 맞추지만, 10월 8일 당시의 프레임·보상 설정 전체를 자동 복원하지는 않음. 과거 환경의 완전한 재현에는 당시 코드와 저장 설정을 함께 사용해야 함.
- 체크포인트를 찾지 못한 두 환경은 미확인으로 표시하고 명령 형식만 제공함. `<체크포인트_절대경로>`를 실제 파일로 교체하기 전에는 실행할 수 없음.

## 1. `Isaac-Sweep-Inspire-Right-OSC-v1`

- **최신 학습:** `2026-10-08_20-54-43_center_reach_separate_reset`.
- **체크포인트:** `/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_inspire_right_v1/2026-10-08_20-54-43_center_reach_separate_reset/model_13200.pt`.
- **영상 저장 위치:** `/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_inspire_right_v1/2026-10-08_20-54-43_center_reach_separate_reset/videos/play`.

실행용:

```bash
./IsaacLab/isaaclab.sh -p src/sweep_inspire_rl/scripts/play.py \
  --task Isaac-Sweep-Inspire-Right-OSC-v1 \
  --num_envs 1 \
  --object-name cup_1 \
  --checkpoint /home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_inspire_right_v1/2026-10-08_20-54-43_center_reach_separate_reset/model_13200.pt \
  --real-time
```

영상 녹화용:

```bash
./IsaacLab/isaaclab.sh -p src/sweep_inspire_rl/scripts/play.py \
  --task Isaac-Sweep-Inspire-Right-OSC-v1 \
  --num_envs 1 \
  --object-name cup_1 \
  --checkpoint /home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_inspire_right_v1/2026-10-08_20-54-43_center_reach_separate_reset/model_13200.pt \
  --video --video_length 500 \
  --headless
```

## 2. `Isaac-Sweep-Inspire-Right-OSC-v2`

- **최신 학습:** `2026-10-08_16-28-21_wrist_gate_up_alignment`.
- **체크포인트:** `/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_inspire_right_v2/2026-10-08_16-28-21_wrist_gate_up_alignment/model_1900.pt`.
- **영상 저장 위치:** `/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_inspire_right_v2/2026-10-08_16-28-21_wrist_gate_up_alignment/videos/play`.
- 이 체크포인트는 71D 센서 관측을 사용하므로 두 명령 모두 `--enable-sensor-observations`를 포함함.

실행용:

```bash
./IsaacLab/isaaclab.sh -p src/sweep_inspire_rl/scripts/play.py \
  --task Isaac-Sweep-Inspire-Right-OSC-v2 \
  --num_envs 1 \
  --object-name cup_1 \
  --enable-sensor-observations \
  --checkpoint /home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_inspire_right_v2/2026-10-08_16-28-21_wrist_gate_up_alignment/model_1900.pt \
  --real-time
```

영상 녹화용:

```bash
./IsaacLab/isaaclab.sh -p src/sweep_inspire_rl/scripts/play.py \
  --task Isaac-Sweep-Inspire-Right-OSC-v2 \
  --num_envs 1 \
  --object-name cup_1 \
  --enable-sensor-observations \
  --checkpoint /home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_inspire_right_v2/2026-10-08_16-28-21_wrist_gate_up_alignment/model_1900.pt \
  --video --video_length 500 \
  --headless
```

## 3. `Isaac-Sweep-Inspire-Right-OSC-v3`

- **최신 학습:** `2026-10-08_19-37-22_close_sweep_0p5cm_no_sensors`.
- **체크포인트:** `/home/min/7cmdehdrb/grad/logs/rsl_rl/UR5e_shelf_sweep_inspire_right_v3/2026-10-08_19-37-22_close_sweep_0p5cm_no_sensors/model_300.pt`.
- **영상 저장 위치:** `/home/min/7cmdehdrb/grad/logs/rsl_rl/UR5e_shelf_sweep_inspire_right_v3/2026-10-08_19-37-22_close_sweep_0p5cm_no_sensors/videos/play`.

실행용:

```bash
./IsaacLab/isaaclab.sh -p src/sweep_inspire_rl/scripts/play.py \
  --task Isaac-Sweep-Inspire-Right-OSC-v3 \
  --num_envs 1 \
  --object-name cup_1 \
  --checkpoint /home/min/7cmdehdrb/grad/logs/rsl_rl/UR5e_shelf_sweep_inspire_right_v3/2026-10-08_19-37-22_close_sweep_0p5cm_no_sensors/model_300.pt \
  --real-time
```

영상 녹화용:

```bash
./IsaacLab/isaaclab.sh -p src/sweep_inspire_rl/scripts/play.py \
  --task Isaac-Sweep-Inspire-Right-OSC-v3 \
  --num_envs 1 \
  --object-name cup_1 \
  --checkpoint /home/min/7cmdehdrb/grad/logs/rsl_rl/UR5e_shelf_sweep_inspire_right_v3/2026-10-08_19-37-22_close_sweep_0p5cm_no_sensors/model_300.pt \
  --video --video_length 500 \
  --headless
```

## 4. `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v0`

- **최신 학습:** `2026-10-09_18-09-20_inspire_open_joint_position`.
- **체크포인트:** `/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_open/2026-10-09_18-09-20_inspire_open_joint_position/model_42100.pt`.
- **영상 저장 위치:** `/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_open/2026-10-09_18-09-20_inspire_open_joint_position/videos/play`.

실행용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v0 \
  --num_envs 1 \
  --checkpoint /home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_open/2026-10-09_18-09-20_inspire_open_joint_position/model_42100.pt \
  --real-time
```

영상 녹화용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v0 \
  --num_envs 1 \
  --checkpoint /home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_open/2026-10-09_18-09-20_inspire_open_joint_position/model_42100.pt \
  --video --video_length 500 \
  --headless
```

## 5. `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v1`

- **최신 학습:** `2026-10-09_18-09-55_inspire_hand_2d`.
- **체크포인트:** `/home/min/7cmdehdrb/grad/logs/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v1/2026-10-09_18-09-55_inspire_hand_2d/model_24700.pt`.
- **영상 저장 위치:** `/home/min/7cmdehdrb/grad/logs/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v1/2026-10-09_18-09-55_inspire_hand_2d/videos/play`.

실행용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v1 \
  --num_envs 1 \
  --checkpoint /home/min/7cmdehdrb/grad/logs/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v1/2026-10-09_18-09-55_inspire_hand_2d/model_24700.pt \
  --real-time
```

영상 녹화용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v1 \
  --num_envs 1 \
  --checkpoint /home/min/7cmdehdrb/grad/logs/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v1/2026-10-09_18-09-55_inspire_hand_2d/model_24700.pt \
  --video --video_length 500 \
  --headless
```

## 6. `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v2`

- **체크포인트 미확인:** 지정된 두 폴더에서 이 환경의 학습 기록을 찾지 못함.
- 기대 experiment: `UR5e_shelf_sweep_random_single_inspire_sensors_v2`.
- 아래 두 명령은 실제 체크포인트를 확보한 후 경로를 채워 사용하는 형식임.

실행용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v2 \
  --num_envs 1 \
  --checkpoint "<체크포인트_절대경로>" \
  --real-time
```

영상 녹화용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v2 \
  --num_envs 1 \
  --checkpoint "<체크포인트_절대경로>" \
  --video --video_length 500 \
  --headless
```

## 7. `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v1-mass`

- **최신 학습:** `2026-10-10_14-32-43_inspire_hand_mass_cylinder`.
- **체크포인트:** `/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v1_mass/2026-10-10_14-32-43_inspire_hand_mass_cylinder/model_11750.pt`.
- **영상 저장 위치:** `/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v1_mass/2026-10-10_14-32-43_inspire_hand_mass_cylinder/videos/play`.

실행용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v1-mass \
  --num_envs 1 \
  --checkpoint /home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v1_mass/2026-10-10_14-32-43_inspire_hand_mass_cylinder/model_11750.pt \
  --real-time
```

영상 녹화용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v1-mass \
  --num_envs 1 \
  --checkpoint /home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v1_mass/2026-10-10_14-32-43_inspire_hand_mass_cylinder/model_11750.pt \
  --video --video_length 500 \
  --headless
```

## 8. `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v2-mass`

- **최신 학습:** `2026-10-10_21-55-16_inspire_mass_z4cm_correct_alignment`.
- **체크포인트:** `/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v2_mass/2026-10-10_21-55-16_inspire_mass_z4cm_correct_alignment/model_89999.pt`.
- **영상 저장 위치:** `/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v2_mass/2026-10-10_21-55-16_inspire_mass_z4cm_correct_alignment/videos/play`.

실행용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v2-mass \
  --num_envs 1 \
  --checkpoint /home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v2_mass/2026-10-10_21-55-16_inspire_mass_z4cm_correct_alignment/model_89999.pt \
  --real-time
```

영상 녹화용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v2-mass \
  --num_envs 1 \
  --checkpoint /home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_random_single_inspire_hand_v2_mass/2026-10-10_21-55-16_inspire_mass_z4cm_correct_alignment/model_89999.pt \
  --video --video_length 500 \
  --headless
```

## 9. `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v3-mass`

- **체크포인트 미확인:** 지정된 두 폴더에서 이 환경의 학습 기록을 찾지 못함.
- 기대 experiment: `UR5e_shelf_sweep_random_single_inspire_hand_v3_mass`.
- 아래 두 명령은 실제 체크포인트를 확보한 후 경로를 채워 사용하는 형식임.

실행용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v3-mass \
  --num_envs 1 \
  --checkpoint "<체크포인트_절대경로>" \
  --real-time
```

영상 녹화용:

```bash
./IsaacLab/isaaclab.sh -p example/Sweep-Policy/play.py \
  --task Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v3-mass \
  --num_envs 1 \
  --checkpoint "<체크포인트_절대경로>" \
  --video --video_length 500 \
  --headless
```

## 확인한 범위

- 학습 폴더 날짜, 체크포인트 최대 번호, 저장 설정 및 선택된 체크포인트의 모델 입출력 크기를 확인함. 명령의 셸 문법과 CLI 옵션을 점검함. NVIDIA 드라이버에 접근하지 못해 실제 재생·영상 녹화는 실행하지 못함.
