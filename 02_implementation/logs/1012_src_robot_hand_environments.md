# 2026-10-12 — src Robot Hand 환경 구성·추정 목적·재생 명령

> **2026-10-14 보관 안내:** 이 문서는 제목 날짜의 실험·구성·checkpoint 기록이다. 현재 활성 환경 목록은 [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)를 따른다. 당시 `src` 패키지는 `src/trash`로 이동했으며 아래 실행 명령의 옛 경로는 역사적 스냅샷으로 보존한다. 코드 링크는 새 보관 위치로 갱신했다. 참고 환경 명령은 해당 submodule의 문서를 함께 확인한다.


- **상태:** 현재 코드와 저장된 학습 설정을 검토한 환경 목록. 이번 작업에서 학습·재생을 실행하거나 성공률을 평가하지 않음.
- **범위:** `src`에 등록된 Inspire Hand 강화학습 환경 12개. 촉각 확인용 비학습 프로그램은 부록으로 분리함. `example/Sweep-Policy`의 Hand 환경은 [기존 체크포인트 문서](1012_latest_checkpoints_play.md)에서 다룸.
- **목적 표기:** 사용자가 별도로 작성한 실험 의도 대신, 보상·관측·제어·초기화 차이로 판단한 **코드 기반 추정**임. 구현된 구성과 성능 검증 결과를 구분함.
- **로그 검색:** `rsl_rl`, `logs/rsl_rl`에 더해 `logs/backup`도 확인함. 폴더명의 날짜·시각이 가장 최근인 학습을 먼저 선택하고, 그 안에서 숫자가 가장 큰 `model_N.pt`를 선택함.
- **명령 사용:** 저장소 루트 `/home/min/7cmdehdrb/grad`에서 기존 Isaac Lab 가상환경으로 실행함. 체크포인트가 있는 11개 환경의 명령만 작성함.
- **현재 구성과 과거 모델:** 아래 구성은 현재 코드 기준임. 재생 스크립트는 저장된 `env.yaml`을 자동 복원하지 않으며, 확인된 차이는 해당 환경에 별도로 기재함.
- **보상 표기:** 계수는 `RewardTermCfg.weight`임. 일부 계수가 양수여도 함수가 음수를 반환하면 패널티임. Terminal 보상은 `step_dt`를 상쇄하는 함수가 포함되어 있어 계수와 실제 일회성 크기를 구분함.

## 1. 환경 목록과 체크포인트

| 전체 환경 ID | 코드 계열 | 최신 학습 | 최신 체크포인트 | 모델 관측 / Action |
| --- | --- | --- | --- | --- |
| `Isaac-Hand-Manipulation-Test-v0` | `hand_manipulation_test` | `2026-10-02_19-08-51` | `model_1350.pt` | 55D / 8D |
| `Isaac-Hand-Manipulation-Contact-v0` | `hand_manipulation_test` | `2026-10-02_21-41-00` | `model_9050.pt` | 55D / 8D |
| `Isaac-Hand-Manipulation-Push-v0` | `hand_manipulation_test` | `2026-10-05_13-31-47` | `model_1800.pt` | 61D / 8D |
| `Isaac-Hand-Manipulation-Push-v1` | `hand_manipulation_test` | `2026-10-06_13-18-48` | `model_21450.pt` | 64D / 8D |
| `Isaac-Blind-Sweep-Inspire-v0` | `hand_manipulation_rl` | `2026-09-27_16-18-39` | `model_300.pt` | 57D / 8D |
| `Isaac-Blind-Sweep-Inspire-Approach-v0` | `hand_manipulation_rl` | `2026-09-27_17-36-20` | `model_800.pt` | 57D / 8D |
| `Isaac-Blind-Sweep-Inspire-Approach-v1` | `hand_manipulation_rl` | `2026-09-27_21-15-36` | `model_2000.pt` | 60D / 8D |
| `Isaac-Blind-Sweep-Inspire-Approach-v2` | `hand_manipulation_rl` | `2026-09-28_02-45-16` | `model_3300.pt` | 60D / 8D |
| `Isaac-Sweep-Inspire-Right-OSC-v1` | `sweep_inspire_rl` | `2026-10-08_20-54-43_center_reach_separate_reset` | `model_13200.pt` | 48D / 8D |
| `Isaac-Sweep-Inspire-Right-OSC-v2` | `sweep_inspire_rl` | `2026-10-08_16-28-21_wrist_gate_up_alignment` | `model_1900.pt` | 71D / 8D |
| `Isaac-Sweep-Inspire-Right-OSC-v3` | `sweep_inspire_rl` | `2026-10-08_19-37-22_close_sweep_0p5cm_no_sensors` | `model_300.pt` | 48D / 8D |
| `Isaac-Sweep-Inspire-Right-OSC-v4` | `sweep_inspire_rl` | `미확인` | `미확인` | 48D / 8D (현재 설정) |

## 2. 단순 Reach·접촉·Push — hand_manipulation_test

### 공통 구성

- UR5e + Axia80 모티브 F/T 원통 + Inspire 왼손. 원통은 반경 4.1 cm, 길이 2.54 cm, 가상 질량 0.001 kg임. 실제 센서 질량·정확도의 재현 검증은 아님.
- EEF는 Hand local `(0, 0.05, 0.10)`. Arm 6D 위치·회전 증분을 torque OSC로 실행하고 Hand는 공통 굽힘·엄지 opposition 2D를 제어함. 정책 Action `[-1,1]`을 손 개방도 `[0,1]`로 변환하며, synergy 1.5/s·관절 목표 1 rad/s 변화율 제한이 있음.
- 기본 관측 55D: Arm q/dq 12D, 초기 EEF 대비 pose 6D, 실제 Hand synergy 2D, 면 header+Tactile 18D, F/T 6D, 초기 target 위치 3D, 이전 Action 8D. Actor와 Critic은 동일 관측을 사용함.
- Tactile은 실제 손바닥·손가락 패드 17개. F/T는 EEF 기준 reaction wrench이며 손 자중을 포함하고 tare·중력 제거를 하지 않음. 관측 스케일은 힘 40 N·모멘트 4 N·m임.
- 물리 100 Hz·정책 50 Hz, episode 10초. Arm/Hand 속도에 의한 종료는 이 계열에 없음.
- PPO는 ELU MLP `[256,128,64]`, 초기 std 1.0, rollout 36, 8 epochs/4 minibatches, adaptive LR 1e-3, gamma 0.98을 사용함.

근거: [환경·관측 공통 설정](../../../../src/trash/hand_manipulation_test/hand_manipulation_test/env_cfg.py) · [태스크 등록](../../../../src/trash/hand_manipulation_test/hand_manipulation_test/__init__.py)

### 2.1. `Isaac-Hand-Manipulation-Test-v0`

- **구성:** 물리적인 대상 물체·테이블 없이 가상 Reach 목표만 배치함. 목표 X `[-0.77,-0.58]`, Y `[-0.22,0.22]`, Z=1.08 m. 고정 초기 Arm 자세와 Hand 개방도 `(0.5,0.5)`에서 시작함. OSC stiffness=100, 관측 55D / Action 8D.
- **보상:** EEF 목표 거리 `4×exp(-d/0.05)`, 실행 Action 변화량 패널티 계수 0.06. 정렬·접촉·물체 이동 보상은 없음.
- **종료:** 10초 timeout만 사용함. 1 cm 도달은 지표이며 성공 종료를 만들지 않음.
- **목적 — 코드 기반 추정:** 물체 충돌을 제외하고 OSC 도달, Hand 2D 제어, Tactile·F/T 관측 경로가 함께 동작하는지 확인하는 기초 환경.
- **근거:** [Reach 설정](../../../../src/trash/hand_manipulation_test/hand_manipulation_test/config/ur5e/reach_env_cfg.py).
- **최신 학습:** `2026-10-02_19-08-51` / `model_1350.pt`.

```bash
./IsaacLab/isaaclab.sh -p src/hand_manipulation_test/scripts/play.py \
  --task Isaac-Hand-Manipulation-Test-v0 \
  --num_envs 1 \
  --checkpoint "/home/min/7cmdehdrb/grad/logs/rsl_rl/hand_manipulation_test/2026-10-02_19-08-51/model_1350.pt" \
  --real-time
```

### 2.2. `Isaac-Hand-Manipulation-Contact-v0`

- **구성:** 36×100×4 cm 테이블 위에 한 변 6 cm·질량 1 kg 큐브 하나를 놓음. 테이블 중심 X=−0.75 m, 윗면 Z=1.05 m, 큐브 중심 Z=1.08 m. 큐브 XY는 X `[-0.82,-0.63]`, Y `[-0.22,0.22]`에서 샘플링함.
- 손을 물체 뒤 14 cm·큐브 중심 위 10 cm에서 collision-safe IK로 초기화함. Hand 개방도 0.90–0.98. 중앙 손바닥 패드의 충돌 형상을 local +Y로 3.5 cm 노출시킴. 관측 55D / Action 8D.
- **보상:** Reach `4×exp(-d/0.05)` 유지, Action 변화량 패널티 계수 0.001, 유효한 실제 palm–Cube 접촉에 접촉 보상 계수 0.02 추가.
- **종료:** 로봇–테이블 접촉 0.01 N 이상 또는 10초 timeout. 성공 종료는 없음.
- **목적 — 코드 기반 추정:** 테이블을 피하면서 물체에 접근하고 실제 손바닥 패드 접촉을 만들 수 있는지 확인하는 Push 이전 단계.
- **저장 모델과의 차이:** 최신 학습은 테이블 X=−0.70 m·큐브 X `[-0.77,-0.58]`로 저장됨. 현재 위치는 5 cm 이동했으며, 관측·Action 차원은 같지만 당시 장면을 그대로 재현하지는 않음.
- **근거:** [Contact 설정](../../../../src/trash/hand_manipulation_test/hand_manipulation_test/config/ur5e/contact_env_cfg.py).
- **최신 학습:** `2026-10-02_21-41-00` / `model_9050.pt`.

```bash
./IsaacLab/isaaclab.sh -p src/hand_manipulation_test/scripts/play.py \
  --task Isaac-Hand-Manipulation-Contact-v0 \
  --num_envs 1 \
  --checkpoint "/home/min/7cmdehdrb/grad/logs/rsl_rl/hand_manipulation_contact/2026-10-02_21-41-00/model_9050.pt" \
  --real-time
```

### 2.3. `Isaac-Hand-Manipulation-Push-v0`

- **구성:** Contact를 상속한 테이블·6 cm·1 kg 큐브. 초기 큐브 XY는 X `[-0.71,-0.69]`, Y `[-0.06,0.06]`. 월드 ±Y에 ±10° 변동을 주어 20–30 cm 밀도록 명령하며 전체 경로가 테이블 안에 있도록 제한함.
- 초기 손은 물체 뒤 14 cm·큐브 중심 위 10 cm. Hand 개방도는 0.8–1.0, OSC stiffness=200. 접근 목표도 큐브 후면의 중심 Z+10 cm임.
- **관측:** 기본 55D에 방향 sin/cos·거리 3D와 **현재 큐브 위치 3D**를 추가하여 61D / Action 8D. 지속 물체 위치 관측을 사용하는 환경임.
- **보상:** 지속적인 Reach·접촉 보너스를 제거하고 아래 진행·접촉 보상을 사용함.

| 항목 | 계수·방식 |
| --- | --- |
| 접근 potential의 새로운 최고 기록 | 0.05 |
| 목표 방향 진행 potential 차이 | 12.0 |
| 후퇴량 패널티 | 6.0 |
| 최초 유효 접촉 | 0.02, 일회성 |
| 유효 접촉 유지 | 0.005 |
| 3D 손바닥 법선 정렬 오차 | 0.3, 음수 반환 |
| 실행 Action 변화량 | 0.001, 음수 반환 |
| 성공 / 실패 | 일회성 +2 / −2 |

- **진행 보상 게이트:** 실제 palm–Cube 접촉 ≥0.01 N, 손바닥 법선·접촉 힘과 명령 방향의 각도 ≤30°, 같은 구간에서 Cube가 테이블에 지지됨, 실패 없음. 접촉 없는 이동도 진행 기록에 반영하여 나중에 접촉한 뒤 같은 이동량을 보상받는 것을 막음.
- **종료:** 로봇–테이블 접촉, 큐브 footprint의 테이블 경계 이탈(5 mm 여유), 낙하·비정상 상태는 실패. 목표 거리 1 cm 이내·속도 0.02 m/s 이하·접촉 이력과 테이블 지지 조건을 0.2초 유지하면 성공. 최대 10초.
- **목적 — 코드 기반 추정:** 도달·접촉만 유지하는 행동을 줄이고, 실제 접촉과 물체 진행이 연결된 양방향 밀기를 학습하는 환경.
- **근거:** [Push 설정](../../../../src/trash/hand_manipulation_test/hand_manipulation_test/config/ur5e/push_env_cfg.py).
- **최신 학습:** `2026-10-05_13-31-47` / `model_1800.pt`.

```bash
./IsaacLab/isaaclab.sh -p src/hand_manipulation_test/scripts/play.py \
  --task Isaac-Hand-Manipulation-Push-v0 \
  --num_envs 1 \
  --checkpoint "/home/min/7cmdehdrb/grad/logs/rsl_rl/hand_manipulation_push/2026-10-05_13-31-47/model_1800.pt" \
  --real-time
```

### 2.4. `Isaac-Hand-Manipulation-Push-v1`

- **구성:** Push-v0를 상속함. 큐브 XY는 X `[-0.73,-0.67]`, Y `[-0.03,0.03]`, 명령 경로는 테이블 중심 X+5 cm 주변이며 X 변동은 ±2 mm. 방향·거리 범위는 유지함.
- **초기 안전 높이와 접촉 목표를 분리:** 초기화는 물체 뒤 14 cm·큐브 중심 위 10 cm를 유지하되, 실제 접근 목표는 큐브 중심 **Z+2.5 cm**로 낮춤. 오른쪽은 중앙 palm, 왼쪽은 노출된 엄지 4번 패드를 접촉 기준으로 사용함.
- 누적 translation OSC 목표를 현재 EEF에서 최대 6 cm로 제한함. 실제 Cube–패드 반력을 필터·제한하여 제어에 사용하며, F/T 관측 tensor를 제어에 직접 연결하는 방식은 아님. 관측에 누적 목표 오차 3D를 추가하여 64D / Action 8D.
- **보상:** Push-v0의 진행·후퇴·접촉·Action·terminal 보상을 유지함. 정렬 0.3을 새 3D 정렬 함수로 바꾸고, 초기 roll 유지 0.1, raw Action 초과량 0.02, 접촉 거리 1.0, EEF 높이 위험 5.0을 추가함. 위험·오차 함수는 음수를 반환함.
- **추가 종료:** EEF가 테이블 위 25 cm보다 높거나, 손가락 바깥 방향 cosine<0.25, wrist2의 sin(q)≤0.15 또는 비정상 상태. 높이 soft penalty는 테이블 위 15 cm부터 적용함. 기존 진행 게이트·성공 조건은 유지함.
- **목적 — 코드 기반 추정:** 실제로 접촉 가능한 낮은 목표와 누적 OSC 제어로 안정적인 밀기를 만들고, 손의 안쪽 회전·과도한 상승·목표 누적 오차를 줄이는 비교 환경.
- **저장 모델 대조:** 최신 로그에 보관된 패키지 소스와 현재 소스가 일치하며 모델 입력·출력도 64D / 8D로 확인함.
- **근거:** [Push-v1 설정](../../../../src/trash/hand_manipulation_test/hand_manipulation_test/config/ur5e/push_v1_env_cfg.py).
- **최신 학습:** `2026-10-06_13-18-48` / `model_21450.pt`.

```bash
./IsaacLab/isaaclab.sh -p src/hand_manipulation_test/scripts/play.py \
  --task Isaac-Hand-Manipulation-Push-v1 \
  --num_envs 1 \
  --checkpoint "/home/min/7cmdehdrb/grad/rsl_rl/hand_manipulation_push_v1/2026-10-06_13-18-48/model_21450.pt" \
  --real-time
```

## 3. 초기 위치 + 센서 기반 Blind Sweep — hand_manipulation_rl

### 공통 구성

- UR5e + Axia80 모티브 F/T 원통 + Inspire Hand. 가상 제어 프레임 C는 Hand local `(0,0.05,0.10)`임. 36×100×4 cm 판(윗면 Z=1.05 m)에 한 변 6 cm·질량 1 kg 큐브 하나를 놓음.
- 큐브 초기 XY는 X `[-0.77,-0.58]`, Y `[-0.22,0.22]`. 월드 ±Y로 초기 위치에서 18 cm 떨어진 고정 목표를 설정함.
- palm/dorsal 면을 확률 0.5씩 선택함. palm 17채널은 실제 패드이며, dorsal 17채널은 12개 부모 링크 접촉 힘을 재사용하는 근사임. 두 면의 측정 모델은 같지 않음.
- **현재 물체 pose는 정책 관측에 없음.** reset 때 저장된 초기 물체 상대 위치, 방향·거리, 로봇 자기 상태, 선택 면의 header+17bit, F/T 6D, 이전 Action을 관측함. 보상·평가는 Scene GT를 사용하며 Actor와 Critic의 입력은 같음.
- Hand는 Action `[-1,1]`을 개방도 `[0,1]`로 변환하는 2D synergy이며, 변화율은 synergy 1.5/s·관절 목표 1 rad/s. Arm OSC 위치·회전 6D를 합해 전체 Action 8D. 물리 100 Hz·정책 50 Hz, episode 10초.
- 성공은 물체 목표 거리 1 cm 이내. 실패는 tilt>30°, 로봇–판 접촉>10 N, 초기 물체 높이보다 3.5 cm 이상 상승, 판 경계 이탈·초기 접촉 등임. 실패 조건은 physics substep에서 latch되며 성공보다 우선함.
- soft risk는 tilt 12°, 판 접촉 2 N, 물체 상승 1.2 cm부터 증가함. F/T는 C 기준 반력이며 자중을 제거하지 않음.

근거: [기본 환경 설정](../../../../src/trash/hand_manipulation_rl/hand_manipulation_rl/env_cfg.py) · [보상 함수](../../../../src/trash/hand_manipulation_rl/hand_manipulation_rl/mdp/rewards.py) · [태스크 등록](../../../../src/trash/hand_manipulation_rl/hand_manipulation_rl/__init__.py)

### 보상 계수 비교

아래 열의 버전은 각각 다음 전체 ID를 가리킴: 기본 `Isaac-Blind-Sweep-Inspire-v0`, 접근 `Isaac-Blind-Sweep-Inspire-Approach-v0`, 개선 `Isaac-Blind-Sweep-Inspire-Approach-v1`, 강화 `Isaac-Blind-Sweep-Inspire-Approach-v2`.

| 항목 | 기본 | 접근 | 개선 | 강화 |
| --- | ---: | ---: | ---: | ---: |
| 목표 거리 `exp(-d/0.05)` | 4.0 | 4.0 | 4.0 | 12.0 |
| 실제 접촉 법선 정렬 오차 | 0.75 | 0.75 | 0.75 | 4.0 |
| 선택 면 Tactile 미접촉 | 0.40 | 0.40 | 제거 | 제거 |
| 실행 Action 변화량 패널티 | 0.06 | 0.06 | 0.06 | 0.06 |
| 시간 패널티 | 0.20 | 0.20 | 0.20 | 0.20 |
| tilt / 판 접촉 / 물체 상승 risk | 각각 1.0 | 각각 1.0 | 각각 1.0 | 각각 1.0 |
| 성공 terminal | 1.0 | 1.0 | 1.0 | 4.0 |
| 실패 terminal | 1.0 | 1.0 | 1.0 | 1.0 |
| selected surface 접근 occupancy | 없음 | 0.10 | 제거 | 제거 |
| 접근·물체 이동 연계 progress | 없음 | 없음 | 2.0 | 2.0 |
| 첫 유효 Hand–물체 접촉 | 없음 | 없음 | 0.50 | 0.50 |
| 접촉 경로 이하 하강 위험 | 없음 | 없음 | 1.0 | 1.0 |

- 접촉 법선 정렬은 EEF 축 정렬이 아니라 **실제 Hand→물체 접촉 법선과 미는 방향**의 정렬임. `−(1−dot)/2`, 미접촉 시 0을 반환함.
- Tactile 항목은 `[-1,0]`의 미접촉 패널티이며 접촉 시 0에 가까워짐. 성공 terminal의 실제 일회성 크기는 기본·접근·개선 +2, 강화 +8이며 실패는 −2임.

### 3.1. `Isaac-Blind-Sweep-Inspire-v0`

- **구성:** 공통 조건 그대로 사용. 관측 57D / Action 8D. C를 물체 중심에서 미는 방향 반대쪽 14 cm·위쪽 10 cm에 IK로 초기화함. XYZ jitter `(±4,±4,±3) mm`, 회전 jitter `(±1°,±1°,±2°)`, 초기 Hand 개방도 0.90–0.98.
- Arm translation은 현재 C local frame 기준 `(1.2,1.2,0.8) cm`, rotation은 0.06 rad 증분. OSC stiffness=100, damping ratio=1, **중력 보상 false**.
- **보상:** 비교표의 기본 열. 현재 목표 거리·접촉·위험·종료 신호를 사용함.
- **목적 — 코드 기반 추정:** 온라인 물체 위치 없이 초기 정보·자기 상태·촉각·F/T로 palm/dorsal 양쪽 면을 사용해 큐브를 미는 기본 Blind Sweep 타당성 확인.
- **로그 식별:** runner 이름 `UR5e_shelf_sweep_random`이 example과 중복됨. 동일 이름의 8월 2finger 학습은 제외하고 저장된 Hand 관측·보상으로 환경을 식별함.
- **근거:** [기본 설정](../../../../src/trash/hand_manipulation_rl/hand_manipulation_rl/env_cfg.py).
- **최신 학습:** `2026-09-27_16-18-39` / `model_300.pt`.

```bash
./IsaacLab/isaaclab.sh -p src/hand_manipulation_rl/scripts/play.py \
  --task Isaac-Blind-Sweep-Inspire-v0 \
  --num_envs 1 \
  --checkpoint "/home/min/7cmdehdrb/grad/logs/backup/UR5e_shelf_sweep_random/2026-09-27_16-18-39/model_300.pt" \
  --real-time
```

### 3.2. `Isaac-Blind-Sweep-Inspire-Approach-v0`

- **상속·구성:** `Isaac-Blind-Sweep-Inspire-v0`. 관측 57D / Action 8D와 OSC/PPO 유지. 초기 backoff 14 cm를 유지하고, Hand X가 위를 향하면 물체 중심 +7.5 cm, 아래를 향하면 +10 cm로 초기 높이를 선택함.
- **보상 변경:** 선택한 palm/dorsal 면의 upstream 접근 목표에 occupancy 보상 0.10 추가. capture 1.5 cm, 평면 sigma 8 cm·높이 sigma 3 cm. 물체 안쪽을 지나면 penetration error가 증가함. 다른 항목은 비교표의 접근 열.
- **목적 — 코드 기반 추정:** 접촉 전 접근에 밀집 보상을 제공하고, 손 방향별 초기 높이로 판 충돌 위험을 줄이는 단계.
- **근거:** [Approach-v0 설정](../../../../src/trash/hand_manipulation_rl/hand_manipulation_rl/env_approach_cfg.py).
- **최신 학습:** `2026-09-27_17-36-20` / `model_800.pt`.

```bash
./IsaacLab/isaaclab.sh -p src/hand_manipulation_rl/scripts/play.py \
  --task Isaac-Blind-Sweep-Inspire-Approach-v0 \
  --num_envs 1 \
  --checkpoint "/home/min/7cmdehdrb/grad/logs/backup/UR5e_shelf_sweep_approach/2026-09-27_17-36-20/model_800.pt" \
  --real-time
```

### 3.3. `Isaac-Blind-Sweep-Inspire-Approach-v1`

- **상속·구성:** Approach-v0. 초기 backoff를 14→10 cm로 줄임. 초기 고정 precontact frontier 대비 접근 오차 3D를 추가하여 관측 60D / Action 8D.
- translation은 `[world-up, sweep 방향, shelf depth(+X)]` 축으로 `(0.4,1.2,0.4) cm`, rotation은 현재 C 기준 0.03 rad. **중력 보상 true**로 변경함.
- 실제 유효 접촉 시 전진 Action에 따라 최대 10 N preload를 Jacobian transpose로 추가함. Hand–물체 힘<12 N, 판 힘<2 N 조건임. 제어 보조도 포함하므로 보상만 바꾼 환경은 아님.
- **보상 변경:** Tactile·접근 occupancy 제거. 경로 potential 차이 2.0, 최초 유효 접촉 0.50, 경로 이하 하강 위험 1.0 추가. potential의 35%는 접촉 전 손 전진, 나머지는 손 전진과 실제 물체 진행이 모두 있어야 얻음. 횡방향·높이 오차도 차감함.
- **PPO 변경:** 초기 std 1.0→0.5, LR adaptive 1e-3→fixed 3e-4. 나머지 네트워크·rollout 설정 유지.
- **목적 — 코드 기반 추정:** 접촉 직전 정지와 빈 공간 통과를 줄이고, 방향에 따른 탐색 차이·접촉 힘 부족을 보완하여 실제 접촉→물체 이동으로 연결하는 환경.
- **근거:** [Approach-v1 설정](../../../../src/trash/hand_manipulation_rl/hand_manipulation_rl/env_v1_cfg.py) · [접근 보상](../../../../src/trash/hand_manipulation_rl/hand_manipulation_rl/mdp/approach_rewards.py).
- **최신 학습:** `2026-09-27_21-15-36` / `model_2000.pt`.

```bash
./IsaacLab/isaaclab.sh -p src/hand_manipulation_rl/scripts/play.py \
  --task Isaac-Blind-Sweep-Inspire-Approach-v1 \
  --num_envs 1 \
  --checkpoint "/home/min/7cmdehdrb/grad/logs/backup/UR5e_shelf_sweep_approach_v1/2026-09-27_21-15-36/model_2000.pt" \
  --real-time
```

### 3.4. `Isaac-Blind-Sweep-Inspire-Approach-v2`

- **상속·구성:** Approach-v1의 물체·관측 60D·Action 8D·제어·초기화·PPO를 유지함.
- **보상 변경:** 목표 거리 4→12, 접촉 법선 정렬 패널티 0.75→4, 성공 terminal 계수 1→4만 변경함. 실제 성공 보너스는 +2→+8.
- **목적 — 코드 기반 추정:** 접근·접촉에서 머무르는 행동보다 목표까지 계속 밀고 성공 조건에 진입하는 행동을 우선하도록 보상 비중을 높이는 비교 환경.
- **근거:** [Approach-v2 설정](../../../../src/trash/hand_manipulation_rl/hand_manipulation_rl/env_v2_cfg.py).
- **최신 학습:** `2026-09-28_02-45-16` / `model_3300.pt`.

```bash
./IsaacLab/isaaclab.sh -p src/hand_manipulation_rl/scripts/play.py \
  --task Isaac-Blind-Sweep-Inspire-Approach-v2 \
  --num_envs 1 \
  --checkpoint "/home/min/7cmdehdrb/grad/logs/backup/UR5e_shelf_sweep_approach_v2/2026-09-28_02-45-16/model_3300.pt" \
  --real-time
```

## 4. example 보상 기반 OSC 비교 — sweep_inspire_rl

### 공통 구성

- UR5e + Axia80 모티브 F/T 원통 + Inspire Hand. EEF는 Hand local **`(0,0,0.10)`**임.
- Arm nominal Action 6D를 OSC에 전달하지만 **회전 3D 정책 입력은 고정 손 자세 목표로 대체**됨. 정책이 바꾸는 Arm 목표는 XYZ임. Hand 2D를 합해 Action 8D.
- Hand Action은 `0.8+0.2×clip(a,0,1)`로 거의 편 상태만 허용하며 synergy 2/s·관절 목표 1 rad/s 변화율 제한을 사용함.
- 기본 관측 48D: 관절 위치 18D, Arm 속도 6D, 이전 Action 8D, 현재 물체 EEF 상대 위치 3D, width 1D, EEF pose 7D, EEF 상대 goal 3D, 실제 Hand synergy 2D. Tactile 17D·F/T 6D는 구현되어 있지만 기본 관측에서 제외함. 켜면 71D.
- `cup_1` 한 개가 기본이며 catalog 물체 6종 중 선택 가능. 명목 질량 1 kg이며 하단 COM을 별도로 지정하지 않음. 초기 슬롯 XY 주변 ±2 cm·yaw를 샘플링하고 목표는 월드 +Y 18 cm임.
- 초기 EEF는 물체 기준 `(X+1.96 cm, Y−(width+6 cm), Z+12 cm)`에 IK 배치함. XYZ ±2 mm 변동과 물체·선반 clearance 검사를 사용함. 초기화 위치와 Reach 목표는 별개임.
- OSC stiffness=200, damping ratio=1, 중력 보상·inertia decoupling 사용. 물리 100 Hz·정책 50 Hz·10초 episode.
- 종료는 timeout, 물체 Z<1.04 m 또는 roll/pitch>0.9 rad, 물체 선속도>0.3 m/s, 선반 움직임·finger/wrist의 선반 근접, **Arm 6축 중 절대 관절 속도>1 rad/s**임. `hand_velocity`라는 이름이지만 손가락 속도 종료는 아님.

근거: [공통·버전 설정](../../../../src/trash/sweep_inspire_rl/sweep_inspire_rl/env_cfg.py) · [실제 Action 처리](../../../../src/trash/sweep_inspire_rl/sweep_inspire_rl/mdp/actions.py) · [보상·게이트](../../../../src/trash/sweep_inspire_rl/sweep_inspire_rl/mdp/rewards.py)

### 보상 — OSC-v2·OSC-v3·OSC-v4 공통

| 항목 | 계수·방식 |
| --- | --- |
| Reach | +3.0 × `exp(-10×EEF 목표 거리)` |
| 손 자세 정렬 | +2.0 × signed square(Hand local +X와 선반 +Z의 내적), 회전행렬 열 사용 |
| Sweeping | +6.0 × 목표 거리·물체 Y 속도 shaping |
| Action Rate | −0.03 × 전체 8D Action 차이 제곱합 |
| Joint Velocity | −0.03 × 이름으로 선택한 Arm 6축 속도 제곱합 |
| 선반 충돌·근접 | −0.5 |
| 비목표 물체 이동 | −0.5, 현재 단일 물체에서는 0 |

- 밀기 게이트는 **EEF–접근 목표 XYZ 거리<4 cm AND wrist Y 오차<4 cm**. 목표 거리 3 cm 미만인 별도 goal 구간은 게이트 없이 `2×exp(-5d)`를 사용함.
- 게이트 구간은 `1−d/0.18+속도 보너스`. 물체 |Y속도|가 0.05–0.1 m/s 사이면 +0.5, 0.1 m/s 이상이면 −0.5임. Homing·Sweeping Height 보상은 현행 설정에서 없음.

### 4.1. `Isaac-Sweep-Inspire-Right-OSC-v1`

- **구성:** Reach 목표는 물체 중앙 XY, episode 초기 물체 Z+7.5 cm. 초기화는 공통의 떨어진 위치에서 시작함.
- **보상:** Reach 계수 +3만 사용함. Action Rate·속도·정렬·Sweep·충돌 보상도 없음. 공통 종료 조건은 유지함.
- **목적 — 코드 기반 추정:** 다른 보상과의 충돌을 제거하고 중앙 XY Reach 보상만으로 접촉을 유도할 수 있는지 확인하는 환경.
- **최신 학습:** `2026-10-08_20-54-43_center_reach_separate_reset` / `model_13200.pt`.

```bash
./IsaacLab/isaaclab.sh -p src/sweep_inspire_rl/scripts/play.py \
  --task Isaac-Sweep-Inspire-Right-OSC-v1 \
  --num_envs 1 \
  --checkpoint "/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_inspire_right_v1/2026-10-08_20-54-43_center_reach_separate_reset/model_13200.pt" \
  --object-name cup_1 \
  --real-time
```

### 4.2. `Isaac-Sweep-Inspire-Right-OSC-v2`

- **구성:** Reach와 밀기 게이트 중심은 `(물체 X−2 cm, 물체 Y−width, 현재 물체 Z+7.5 cm)`. 현재 관측은 기본 48D이고 보상은 공통 표와 같음.
- **목적 — 코드 기반 추정:** example의 접근·밀기 보상을 Hand·OSC·낮은 Z 조건으로 옮긴 기준 환경.
- **최신 모델의 중요한 차이:** 저장 당시 관측은 **71D**, EEF는 `(0,0.05,0.10)`, 초기화 clearance는 4 cm, 게이트는 XY norm, wrist 목표 offset은 −5 cm, Reach Z는 초기 물체 기준으로 고정, Sweeping Height 패널티 −1이었음. 현재 구성은 위 공통 설명과 다름.
- 아래 명령의 `--enable-sensor-observations`는 모델 입력 차원만 맞춤. 당시 환경을 완전히 재현하려면 해당 학습 시점의 코드·설정을 사용해야 함.
- **최신 학습:** `2026-10-08_16-28-21_wrist_gate_up_alignment` / `model_1900.pt`.

```bash
./IsaacLab/isaaclab.sh -p src/sweep_inspire_rl/scripts/play.py \
  --task Isaac-Sweep-Inspire-Right-OSC-v2 \
  --num_envs 1 \
  --checkpoint "/home/min/7cmdehdrb/grad/rsl_rl/UR5e_shelf_sweep_inspire_right_v2/2026-10-08_16-28-21_wrist_gate_up_alignment/model_1900.pt" \
  --object-name cup_1 \
  --enable-sensor-observations \
  --real-time
```

### 4.3. `Isaac-Sweep-Inspire-Right-OSC-v3`

- **구성:** OSC-v2를 상속하고 Reach·밀기 게이트의 Y offset을 width에서 **0.5 cm**로 변경함. X−2 cm·Z+7.5 cm, 보상 표·게이트 반경은 유지함.
- **목적 — 코드 기반 추정:** 물체 옆에서 멈추는 현상에 접근 offset이 미치는 영향을 극단적인 근접 목표로 확인하는 비교 환경.
- **저장 모델과의 차이:** 관측 48D·주요 게이트 설정은 맞지만, 당시 reset clearance 4 cm가 현재 6 cm임.
- **최신 학습:** `2026-10-08_19-37-22_close_sweep_0p5cm_no_sensors` / `model_300.pt`.

```bash
./IsaacLab/isaaclab.sh -p src/sweep_inspire_rl/scripts/play.py \
  --task Isaac-Sweep-Inspire-Right-OSC-v3 \
  --num_envs 1 \
  --checkpoint "/home/min/7cmdehdrb/grad/logs/rsl_rl/UR5e_shelf_sweep_inspire_right_v3/2026-10-08_19-37-22_close_sweep_0p5cm_no_sensors/model_300.pt" \
  --object-name cup_1 \
  --real-time
```

### 4.4. `Isaac-Sweep-Inspire-Right-OSC-v4`

- **구성:** OSC-v2를 상속하고 Reach·밀기 게이트의 Y offset을 **0.8×width**로 변경함. 다른 공통 설정과 관측 48D / Action 8D는 유지함.
- **목적 — 코드 기반 추정:** 표준 width offset과 극단적인 0.5 cm 사이에서 조금 더 안쪽으로 접근할 때 밀기 유도가 개선되는지 비교하는 환경.
- **실행 명령:** 검색 범위에서 체크포인트 미확인. 경로를 임의로 채운 명령은 작성하지 않음.

## 5. 과거 로그와 현재 등록의 구분

- `Isaac-Sweep-Inspire-Right-OSC-v0`, `Isaac-Sweep-Inspire-Right-OSC-v5`의 과거 로그는 남아 있지만 현재 등록과 재생 스크립트의 task 목록에는 없음. 현행 구성으로 자동 대응시키거나 다른 버전 ID로 실행하는 명령은 작성하지 않음.
- `example/Sweep-Policy`의 `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v3`와 `Isaac-Sweep-Object-UR5e-Random-Single-Inspire-Open-v3-mass`는 별개이며 이 문서의 OSC-v3와도 다름.
- 저장된 모델이 있다는 사실만으로 성공·수렴했다고 판단하지 않음. 위 목록에는 smoke/validation 기록도 존재하며, 가장 최근 날짜와 checkpoint 번호로 선택함.

## 6. 부록 — 비학습 촉각 점검 프로그램

### 자동 개폐 `src/inspire_tactile/scripts/play.py`

- **환경 이름:** 등록된 Gym task ID 없음. UR5e+Inspire 자동 개폐 촉각 데모.
- **구성:** Arm 자세 고정, 손만 open→close→hold→release를 11초 주기로 반복. 받침대 위 지름 8 cm·높이 9 cm·질량 0.32 kg 실린더를 사용함.
- **센서·보상:** 17채널 Tactile. 기본 projected 모드는 부모 링크의 실제 접촉점을 센서 영역에 배정하는 근사이며 raw 패드 모드와 구분함. 기본 접촉 임계값 0.01 N. PPO·Action 정책·학습 보상은 없음.
- **목적 — 코드 기반 추정:** 파지·해제 시 촉각의 출력과 비센서 링크 접촉·센서 커버리지를 점검하는 프로그램. JSONL 실행 로그는 있지만 학습 체크포인트는 없음.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_tactile/scripts/play.py
```

### 수동 조작 `src/inspire_tactile/scripts/manual.py`

- **환경 이름:** 등록된 Gym task ID 없음. Inspire 관절·촉각 수동 점검 모드.
- **구성:** 위 장면을 공유하고 자동 개폐·주기적 reset은 사용하지 않음. 기본 12관절 독립 조작과 원래 mimic 연동 모드를 선택할 수 있음. 12개의 시뮬레이션 관절이 실제 Hand의 독립 구동 자유도가 12라는 뜻은 아님.
- **보상·목적 — 코드 기반 추정:** 보상 없음. 요청 관절각·실제 관절각·촉각 출력의 대응을 확인함. 기본 목표 변화율 0.6 rad/s. JSONL 실행 로그가 있으며 PPO 체크포인트는 없음.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_tactile/scripts/manual.py
```

근거: [촉각 데모 설명](../../../../src/trash/inspire_tactile/README.md) · [장면 구성](../../../../src/trash/inspire_tactile/inspire_tactile/scene.py)

`src/axia80_feasibility`는 Axia80+직육면체 tool의 하중 실험이며 Robot Hand를 장착하는 강화학습 환경이 아니어서 제외함. `sweep_rl`, `sweep_jh`, `sweep_shelve_force`의 확인된 환경은 Robotiq 2finger 구성으로 이번 Hand 목록에서 제외함.

## 7. 확인한 범위

- 12개 Gym 등록 ID, 관측·Action·보상·종료·초기화 구성, 실제 play 옵션을 확인함.
- 선택된 11개 checkpoint를 CPU에서 읽어 모델 입출력 크기를 대조함. 커맨드에 사용한 모든 파일 경로와 셸 문법을 확인함.
- 이번 문서는 구성 목록이며 새 성능 평가가 아님. 실제 Isaac Sim 재생과 녹화는 실행하지 않음.
