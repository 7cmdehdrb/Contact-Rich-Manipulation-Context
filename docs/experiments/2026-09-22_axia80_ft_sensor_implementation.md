# Isaac Lab UR5e–Axia80 F/T feasibility 구현·재현 가이드

문서 ID: `AXIA80-FEASIBILITY-IMPLEMENTATION-2026-09-22`

- 상태: implemented / tested
- 대상: 다른 구현 에이전트가 동일한 Isaac Lab 실험을 재구성하는 경우
- 기준 결과: [Axia80 F/T feasibility 실험 결과](2026-09-22_axia80_ft_sensor_feasibility.md)
- 코드 스냅샷: [artifacts/axia80_feasibility](../../artifacts/axia80_feasibility)

## 1. 구현 목표와 완료 조건

다음 세 실험을 서로의 결과를 덮어쓰지 않는 독립 실행으로 구현한다.

1. 얇은 끝면으로 장착한 수평 cantilever에 `10–500 g`을 올리는 50환경 질량 스윕
2. 같은 tool의 `wrist_3_joint`를 `+10°` Roll하고 수행하는 50환경 질량 스윕
3. `500 g`을 고정하고 Roll×Tilt를 각각 `{-10, -5, 0, 5, 10}°`로 바꾸는 25환경 스윕

구현 완료는 화면에 모델이 보이는 것만으로 판단하지 않는다. 다음 조건을 모두 만족해야
한다.

- Axia80 중심의 fixed measurement joint에서 6축 wrench를 읽는다.
- Raw, tool-only tare, tare-corrected 값을 구분해 저장한다.
- 질량 또는 각도 조합별 환경을 한 번에 vectorize한다.
- 물체가 안정화되지 않거나 미끄러지거나 전도되면 새 CSV를 쓰지 않는다.
- command angle이 아니라 sample별 실제 tool pose와 payload 위치로 기대 wrench를
  계산한다.
- `--strict` 실행이 `PASS`로 종료하고 metadata, CSV, log, plot을 남긴다.
- 순수 Python 계약 테스트 30개가 통과한다.

최초의 broad-face 장착은 이 구현의 재현 대상이 아니다. 최종 형상은 반드시 tool의
`0.012 × 0.120 m` 얇은 끝면을 센서에 붙이는 cantilever 구조여야 한다.

## 2. 검증된 기준 환경

| 항목 | 기준값 |
| --- | --- |
| OS | Ubuntu 22.04 |
| Python | `3.11.15` |
| Isaac Sim | `5.1.0.0` |
| Isaac Lab package | `0.54.4` |
| Isaac Lab source commit | `4e06a8a516a291e9c948edf4eed6ef4c7242c927` |
| UR description | Universal Robots ROS 2 Description `2.13.0` |
| UR description commit | `18e6f603b3ebc2ec479fecb62d6be544b15755e9` |
| NumPy / SciPy | `1.26.0` / `1.15.3` |
| Matplotlib / xacro | `3.10.3` / `2.1.1` |
| Physics rate | `240 Hz` |

Isaac Lab과 UR description은 용량이 큰 외부 runtime 의존성이므로 이 저장소에 복제하지
않는다. 대신 위 commit을 고정한다. 실행 환경은 다음 조건을 만족해야 한다.

```text
<workspace-root>/IsaacLab
<workspace-root>/src/Universal_Robots_ROS2_Description
<contact-repo>/artifacts/axia80_feasibility
```

코드 스냅샷은 `--repo_root <workspace-root>`를 받으므로 Contact 저장소가 workspace
안이나 밖 어디에 있어도 된다. URDF의 mesh 경로는 생성 시 절대경로로 해석되므로 다른
장비에서 기존 `generated/usd`를 복사해 쓰지 말고 URDF/USD를 다시 생성해야 한다.

## 3. 제공된 재현 스냅샷

```text
artifacts/axia80_feasibility/
├── axia80_feasibility/
│   ├── model.py
│   ├── scene.py
│   ├── measurement.py
│   ├── cantilever_*.py
│   ├── tilted_cantilever_*.py
│   └── wrist_angle_*.py
├── scripts/
│   ├── run_cantilever_payload_test.py
│   ├── run_tilted_cantilever_payload_test.py
│   ├── run_wrist_angle_sweep.py
│   └── plot_*.py
├── tests/
├── results/
└── pyproject.toml
```

주요 파일의 책임은 다음과 같다.

| 파일 | 책임 |
| --- | --- |
| [model.py](../../artifacts/axia80_feasibility/axia80_feasibility/model.py) | UR5e xacro 확장, Axia80 공통 형상, URDF helper |
| [cantilever_model.py](../../artifacts/axia80_feasibility/axia80_feasibility/cantilever_model.py) | 최종 thin-face tool과 기준 자세 생성 |
| [scene.py](../../artifacts/axia80_feasibility/axia80_feasibility/scene.py) | articulation, actuator, payload, ground 설정 |
| [tilted_cantilever_model.py](../../artifacts/axia80_feasibility/axia80_feasibility/tilted_cantilever_model.py) | Wrist3 `+10°` Roll과 고마찰 설정 |
| [wrist_angle_model.py](../../artifacts/axia80_feasibility/axia80_feasibility/wrist_angle_model.py) | Roll×Tilt grid와 joint mapping |
| `*_measurement.py` | 요약, 지표, acceptance 판정 |
| `*_plotting.py` | 기존 summary CSV 기반 plot 생성 |
| `run_*.py` | AppLauncher, physics loop, tare, 배치, 안정화, 기록 |

`model.py`에는 helper의 출발점이 된 예전 broad-face builder도 남아 있다. 최종 실험은
`build_model()`이 아니라 `build_cantilever_model()`,
`build_tilted_cantilever_model()`, `build_wrist_angle_model()` 중 하나를 호출해야 한다.

## 4. 좌표계와 형상을 먼저 고정한다

### 4.1 조립 구조

```text
UR5e base_link ... wrist_3_link/tool0
  └─ fixed: ur5e_to_axia80_cantilever_joint
       └─ axia80_link
            └─ fixed: axia80_cantilever_measurement_joint
                 └─ payload_tool_link
                      └─ contact로 지지되는 payload cube
```

센서 link와 tool link의 frame은 Axia80 중심에서 위치와 방향이 정확히 일치한다.
Tool의 geometry와 center of mass만 센서 앞쪽으로 offset한다. 이렇게 해야 child tool
body의 incoming joint wrench가 별도 frame 변환 없이 Axia80 중심 기준 wrench가 된다.

### 4.2 치수와 물성

| 항목 | 값 |
| --- | ---: |
| Axia80 반지름 | `0.041 m` |
| Axia80 높이 | `0.0254 m` |
| Axia80 simulation mass | `0.001 kg` |
| Tool 크기 `(X,Y,Z)` | `(0.012, 0.120, 0.240) m` |
| Tool 질량 | `0.20 kg` |
| Sensor–tool gap | `0.001 m` |
| Payload cube 한 변 | `0.040 m` |
| Payload 중심의 normal offset `h` | `0.0260 m` |
| Sensor 중심부터 payload 중심까지 `d` | `0.1337 m` |

`0.001 kg` sensor mass는 PhysX rigid body를 안정적으로 유지하기 위한 값이다. 측정
joint보다 상류에 있으므로 tool-side wrench의 payload/tare 결과에는 포함되지 않는다.

### 4.3 센서 좌표계

- `+X`: tool broad face의 위쪽 normal
- `+Z`: 센서에서 tool 끝으로 향하는 cantilever 길이축
- `+Y`: 오른손 좌표계에 따른 옆 방향
- Wrench 순서: `Fx, Fy, Fz, Mx, My, Mz`
- Force 단위: `N`
- Moment 단위: `Nm`

수평 기준 arm joint pose는 다음과 같다.

```text
shoulder_pan_joint  =  0
shoulder_lift_joint = -pi/2
elbow_joint         = +pi/2
wrist_1_joint       = -pi/2
wrist_2_joint       = +pi
wrist_3_joint       =  0
```

이 자세에서 sensor `+X`가 world 위쪽, sensor `+Z`가 수평 정면을 향해야 한다.

## 5. URDF 생성 절차

구현 순서를 바꾸지 않는다.

1. `Universal_Robots_ROS2_Description`의 `ur_macro.xacro`를 임시 디렉터리에서
   확장한다.
2. `package://ur_description/` mesh URI를 실제 description 경로로 바꾼다.
3. xacro wrapper의 `world` link와 root fixed joint를 제거한다.
4. `tool0` 아래에 Axia80 cylinder link를 fixed joint로 연결한다. Joint translation은
   sensor 높이의 절반인 `0.0127 m`다.
5. Axia80 중심과 동일한 frame에 `payload_tool_link`를 만든다.
6. Tool box와 inertia의 중심만 `+Z=0.1337 m`로 offset한다.
7. Axia80–tool 사이에 `axia80_cantilever_measurement_joint`를 원점 offset 없이 만든다.
8. UR description의 massless TF-only link를 접되 모든 child transform을 보존한다.
9. 모든 mesh 파일 존재 여부와 sensor/tool link 보존 여부를 검사한다.
10. URDF와 model metadata JSON을 생성한다.

Isaac Lab의 URDF converter에서는 `merge_fixed_joints=False`가 필수다. 이를 `True`로
바꾸면 sensor와 tool rigid body 또는 measurement joint가 합쳐져 원하는 wrench를 읽을
수 없다.

## 6. Isaac Lab scene 구성

`InteractiveSceneCfg`에서 환경 수는 실험 parameter 조합 수와 같게 둔다.

### 6.1 Robot articulation

| 설정 | 값 |
| --- | --- |
| `fix_base` | `True` |
| `root_link_name` | `base_link` |
| `merge_fixed_joints` | `False` |
| self collision | `False` |
| collider | `convex_hull` |
| position solver iterations | `32` |
| velocity solver iterations | `4` |
| arm stiffness | `8000.0` |
| arm damping | `400.0` |
| armature | `0.01` |
| simulated velocity limit | `1.0` |

Shoulder/elbow effort limit은 `150 Nm`, 세 wrist joint는 `28 Nm`다. 각 physics step에
같은 joint target을 다시 써서 implicit drive가 자세를 유지하게 한다.

### 6.2 Payload와 contact

Payload는 `0.040 m` cube이고 collision의 `contact_offset=0.0005 m`,
`rest_offset=0`을 사용한다. 수평 시험의 static/dynamic friction은 `1.0/0.8`,
Wrist3 Roll 및 Roll×Tilt 시험은 `2.0/1.5`이며 combine mode는 `max`다.

URDF에서 생성한 tool collision prim에도 실행 후 `collision_enabled=True`,
`contact_offset=0.0005 m`, `rest_offset=0`을 적용한다. 각 environment의 robot prim은
instanceable 상태를 해제하고 sensor/tool prim에 `UsdPhysics.RigidBodyAPI`가 실제로
존재하는지 검사한다.

### 6.3 Simulation

```text
dt = 1 / 240 s
gravity = [0, 0, -9.81] m/s²
render_interval = 4
solve_articulation_contact_last = True
bounce_threshold_velocity = 0.05 m/s
```

환경 간격의 기본값은 `2.0 m`다. `replicate_physics=True`를 사용한다.

## 7. Wrench를 읽는 방법

Tool body ID를 얻은 뒤 다음 tensor의 해당 body 행을 읽는다.

```python
robot.data.body_incoming_joint_wrench_b[:, tool_body_id, :]
```

반드시 `payload_tool_link`의 incoming wrench를 읽어야 한다. Sensor body의 incoming
wrench나 contact force 합계를 대신 사용하면 같은 물리량이 아니다. 현재 조립에서는
sensor/tool frame이 일치하므로 반환 순서를 그대로 `Fx, Fy, Fz, Mx, My, Mz`로 쓴다.

측정 전 다음 불변조건을 검사한다.

```text
|sensor_position - tool_position| <= 1e-4 m
|quat(sensor) dot quat(tool)| >= 0.999999
```

CSV의 세 값은 다음 의미다.

```text
raw wrench            = incoming fixed-joint wrench
tare wrench           = payload 없이 측정한 tool-only raw 평균
tare-corrected wrench = raw wrench - tare wrench
```

## 8. 공통 실행 상태기계

모든 runner는 아래 순서를 따른다.

1. AppLauncher 인자를 등록하고 CLI 값을 검증한다.
2. URDF와 model metadata를 만든 뒤 AppLauncher로 Kit을 시작한다.
3. `InteractiveScene`을 만들고 robot/payload instance 수를 확인한다.
4. 환경별 payload mass를 PhysX view에 쓰고 inertia를 mass 비율로 함께 조정한다.
5. Payload gravity를 끄고 tool과 떨어진 위치에 parking한다.
6. Robot을 기본 joint target으로 warm-up한다.
7. Payload가 없는 상태에서 기본 `0.75 s`, 즉 180 sample의 tare를 얻는다.
8. Tool frame의 payload 중심 위치에 `0.0005 m` clearance를 더해 cube를 놓고
   gravity를 다시 켠다.
9. 최소 `1.0 s` 이후부터 안정 조건이 `0.5 s` 연속 유지될 때까지 기다린다.
10. 기본 `1.0 s`, 즉 240 sample 동안 wrench와 실제 pose를 기록한다.
11. 측정 구간 전체에서 안정성이 유지됐을 때만 CSV와 plot을 쓴다.
12. 지표와 acceptance를 계산해 metadata와 run log에 `PASS` 또는 `FAIL`을 남긴다.

공통 안정 조건은 상대 선속도 `<=0.005 m/s`, 상대 각속도 `<=0.05 rad/s`다.
수평/단일 Roll의 위치 tolerance는 `0.004 m`, Roll×Tilt는 `0.006 m`다.

## 9. 실험별 구현

### 9.1 수평 질량 스윕

- 환경 수: 50
- 환경–질량 매핑: `env_0=10 g`, ..., `env_49=500 g`
- Tool broad normal: world 위쪽
- Cantilever `+Z`: 수평
- 기대 주 채널:

```text
Fx = m g
My = m g d
d = 0.1337 m
```

질량을 바꿀 때 rigid-body mass만 바꾸지 말고 inertia도 기존 inertia에 mass ratio를
곱해 갱신한다.

### 9.2 Wrist3 `+10°` Roll 질량 스윕

코드의 `tilted_cantilever` 명칭은 이전 명칭을 보존한 것이다. 축 정의상 이 실험은
`wrist_3_joint`가 sensor/tool `+Z` 주위로 회전하는 **Roll**이다. Tilt가 아니다.

```text
wrist_3_joint = +10°
static/dynamic friction = 2.0 / 1.5
```

Nominal 정역학은 다음과 같다.

```text
Fx =  m g cos(roll)
Fy = -m g sin(roll)
Fz =  0
Mx =  d m g sin(roll)
My =  d m g cos(roll)
Mz = -h m g sin(roll)
```

최종 판정에는 nominal 식을 직접 쓰지 않는다. 각 sample에서 world 위쪽 지지력을
현재 tool quaternion의 local frame으로 회전하고, 실제 payload 위치를 이용해
`moment = r × force`를 계산한다.

### 9.3 고정 500 g Roll×Tilt 스윕

- Roll: 기준 자세에 대한 `wrist_3_joint` offset
- Tilt: 기준 자세에 대한 `wrist_2_joint` offset
- Grid 순서: Tilt-major row, Roll-minor column
- 환경 수: `5 × 5 = 25`

Nominal force는 다음 관계를 확인하는 참고값이다.

```text
Fx =  m g cos(tilt) cos(roll)
Fy = -m g cos(tilt) sin(roll)
Fz = -m g sin(tilt)

Mx = -d Fy
My =  d Fx - h Fz
Mz =  h Fy
```

최종 expected tare-corrected wrench는 다음 세 항으로 계산한다.

```text
expected = payload wrench at current pose
         + tool wrench at current pose
         - mean tool wrench during tare
```

Tool 자세가 tare 이후 joint load로 미세하게 변하는 효과까지 포함하기 위한 식이다.

## 10. 접촉 유지와 오류 방지 검사

Roll 또는 Tilt 실험에서는 속도만으로 안정성을 판단하지 않는다.

- Tool-local payload 중심 오차
- Tool surface의 Y/Z 접선 변위
- Payload와 tool의 상대 quaternion angle
- Tool 폭과 길이 양쪽의 edge margin
- Broad normal이 여전히 위쪽을 향하는지
- 실제 합성 경사에서 필요한 정지마찰계수

단일 Roll은 downhill displacement `<=0.004 m`, 상대각 `<=2°`, edge margin `>0`을
요구한다. Roll×Tilt는 tangent displacement `<=0.006 m`, 상대각 `<=2°`, 폭/길이
edge margin `>0`을 요구한다. 하나라도 실패하면 측정 CSV 생성을 거부한다.

## 11. Acceptance 기준

### 수평 질량 스윕

- `Fx`와 `My` slope: 이론값의 ±5%
- 두 채널 `R² >= 0.995`
- `Fx` RMSE `<=0.01 N`, 최대 오차 `<=0.02 N`
- `My` RMSE `<=0.005 Nm`, 최대 오차 `<=0.01 Nm`
- 추정 lever arm 오차 `<=0.005 m`
- Cross-axis force `<=0.10 N`, moment `<=0.01 Nm`
- `Fx`, `My` 모두 질량에 따라 엄격히 증가
- 모든 payload 안정화

### Wrist3 `+10°` Roll 질량 스윕

- 실제 pose expected 대비 각 비영점 채널 slope 오차 ±5%
- 각 비영점 채널 model `R² >= 0.995`
- Force/Moment RMSE `<=0.01 N / 0.005 Nm`
- Force/Moment 최대 성분 오차 `<=0.02 N / 0.01 Nm`
- Force와 bending 분산각 오차 각각 `<=0.5°`
- Lever arm 오차 `<=0.005 m`
- 미끄럼, 전도, edge, 방향 및 안정성 조건 전부 통과

### Roll×Tilt 스윕

- Force/Moment component RMSE `<=0.015 N / 0.004 Nm`
- 최대 force/moment component 오차 `<=0.03 N / 0.01 Nm`
- 최대 force/moment vector 오차 `<=0.04 N / 0.015 Nm`
- Force와 moment 방향 오차 각각 `<=0.75°`
- Roll/Tilt tracking 오차 각각 `<=1°`
- 실제 필요 정지마찰계수 `<` 설정 static friction
- 완전한 2D grid와 모든 접촉 안정성 조건 통과

## 12. 실행 명령

아래에서 `<workspace-root>`, `<contact-repo>`, `<isaac-python>`을 실제 절대경로로
바꾼다. `<isaac-python>`은 Isaac Lab과 Isaac Sim이 설치된 Python executable이다.

### 12.1 계약 테스트

이 테스트는 Kit을 시작하지 않는다.

```bash
cd <contact-repo>/artifacts/axia80_feasibility

PYTHONDONTWRITEBYTECODE=1 \
AXIA80_WORKSPACE_ROOT=<workspace-root> \
/usr/bin/python3 -m unittest discover -s tests -p 'test_axia80_*.py'
```

기준 결과는 `Ran 30 tests`와 `OK`다.

### 12.2 수평 질량 스윕

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  MPLCONFIGDIR=/tmp/axia80-cantilever-mpl \
  <isaac-python> \
  <contact-repo>/artifacts/axia80_feasibility/scripts/run_cantilever_payload_test.py \
  --repo_root <workspace-root> \
  --headless --device cuda:0 --strict --force_conversion \
  --output_dir <contact-repo>/artifacts/axia80_feasibility/reruns/cantilever
```

### 12.3 Wrist3 `+10°` Roll 질량 스윕

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  MPLCONFIGDIR=/tmp/axia80-roll10-mpl \
  <isaac-python> \
  <contact-repo>/artifacts/axia80_feasibility/scripts/run_tilted_cantilever_payload_test.py \
  --repo_root <workspace-root> \
  --headless --device cuda:0 --strict --force_conversion \
  --output_dir <contact-repo>/artifacts/axia80_feasibility/reruns/wrist3_roll10
```

### 12.4 500 g Roll×Tilt 스윕

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  MPLCONFIGDIR=/tmp/axia80-roll-tilt-mpl \
  <isaac-python> \
  <contact-repo>/artifacts/axia80_feasibility/scripts/run_wrist_angle_sweep.py \
  --repo_root <workspace-root> \
  --headless --device cuda:0 --strict --force_conversion \
  --output_dir <contact-repo>/artifacts/axia80_feasibility/reruns/roll_tilt
```

`--force_conversion`은 첫 실행 또는 URDF 변경 후 한 번 사용한다. 같은 output directory에
Roll×Tilt 결과가 이미 있으면 runner가 덮어쓰기를 거부한다. 새 경로를 쓰는 것이
원칙이며, 의도적으로 교체할 때만 `--overwrite`를 추가한다.

## 13. Isaac Lab 화면으로 확인

`--headless`를 제거하면 창이 열린다. 25환경 전체보다 다음 3×3 grid가 방향 확인에
편하다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  MPLCONFIGDIR=/tmp/axia80-roll-tilt-visual-mpl \
  <isaac-python> \
  <contact-repo>/artifacts/axia80_feasibility/scripts/run_wrist_angle_sweep.py \
  --repo_root <workspace-root> \
  --device cuda:0 --strict \
  --roll_angles_deg -10 0 10 \
  --tilt_angles_deg -10 0 10 \
  --warmup_seconds 3 \
  --min_settle_seconds 3 \
  --stable_window_seconds 2 \
  --sample_duration 10 \
  --output_dir <contact-repo>/artifacts/axia80_feasibility/reruns/roll_tilt_visual
```

화면에서 다음을 확인한다.

- Tool의 얇은 끝면이 sensor에 붙어 있다.
- 수평 기준에서 넓은 면 normal이 하늘을 향한다.
- Roll은 tool 길이축 주위로 판을 기울인다.
- Tilt는 tool 길이축 자체를 위아래로 기울인다.
- Payload가 tool 폭/길이 edge를 넘어가지 않는다.

## 14. Plot만 다시 만들기

Isaac Lab 없이 summary CSV만으로 plot을 재생성할 수 있다.

```bash
/usr/bin/python3 \
  <contact-repo>/artifacts/axia80_feasibility/scripts/plot_wrist_angle_results.py \
  <contact-repo>/artifacts/axia80_feasibility/results/wrist_angle_sweep_500g_roll_tilt_10deg/axia80_wrist_angle_summary.csv \
  --output_prefix /tmp/axia80_wrist_angle

/usr/bin/python3 \
  <contact-repo>/artifacts/axia80_feasibility/scripts/plot_wrist_angle_fixed_sweeps.py \
  <contact-repo>/artifacts/axia80_feasibility/results/wrist_angle_sweep_500g_roll_tilt_10deg/axia80_wrist_angle_summary.csv \
  --output_dir /tmp/axia80_fixed_sweeps
```

## 15. 다른 에이전트가 자주 틀릴 지점

1. **Wrist3를 Tilt로 부르지 않는다.** Legacy 파일명은 `tilted`지만 축 정의상
   `wrist_3_joint`는 Roll, `wrist_2_joint`는 Tilt다.
2. **Broad face를 sensor에 붙이지 않는다.** `0.012 × 0.120 m` 끝면을 장착한다.
3. **Tool 폭을 `0.160 m`로 되돌리지 않는다.** 최종값은 self-overlap을 줄인
   `0.120 m`다.
4. **Fixed joint를 merge하지 않는다.** `merge_fixed_joints=False`가 F/T 측정의
   전제다.
5. **Sensor frame과 world frame을 혼동하지 않는다.** 로그는 sensor-local이다.
6. **Raw를 payload 반력으로 쓰지 않는다.** Raw에는 `0.20 kg` tool 자중이 포함된다.
7. **Mass만 바꾸고 inertia를 그대로 두지 않는다.** PhysX mass ratio로 inertia도
   함께 갱신한다.
8. **Tare 중 payload gravity를 켜지 않는다.** Payload는 parking하고 gravity를 끈다.
9. **Command angle만으로 센서 오차를 계산하지 않는다.** 실제 pose expected를 쓴다.
10. **안정화 직후 한 frame만 저장하지 않는다.** 연속 안정 window와 1초 sample
    window 전체를 검사한다.
11. **미끄러진 환경의 CSV를 남기지 않는다.** 실패 시 기록을 거부해야 한다.
12. **Rigid model에서 실제 처짐이 보인다고 주장하지 않는다.** 현재 구현은 bending
    moment 전달을 측정하며 탄성 변형을 모델링하지 않는다.

## 16. 다른 에이전트에 전달할 구현 계약

다른 에이전트에는 다음 조건을 그대로 전달하면 된다.

```text
Contact-Rich-Manipulation-Context의
docs/experiments/2026-09-22_axia80_ft_sensor_implementation.md와
artifacts/axia80_feasibility를 기준 구현으로 사용한다.

UR5e tool0 아래에 radius 0.041 m, height 0.0254 m인 Axia80 cylinder를 붙이고,
센서 중심의 fixed measurement joint 아래에 (X,Y,Z)=(0.012,0.120,0.240) m,
mass 0.20 kg인 tool을 얇은 끝면으로 장착한다. Sensor/tool frame은 센서 중심에서
일치시키고 geometry/COM만 +Z로 offset한다. merge_fixed_joints=False를 유지한다.

Wrench는 payload_tool_link의 body_incoming_joint_wrench_b에서 읽고 tool-only tare를
뺀다. +X는 위쪽 broad-face normal, +Z는 cantilever 정면, +Y는 옆 방향이다.
Wrist3는 Roll, Wrist2는 Tilt다. 수평 10–500 g, Wrist3 Roll +10° 10–500 g,
500 g Roll×Tilt 5×5 실험을 vectorized하게 구현한다. 실제 sample pose로 expected
wrench를 계산하고 안정화·미끄럼·전도·edge 검사를 통과한 경우에만 CSV를 쓴다.
제공된 30개 계약 테스트와 strict acceptance를 모두 통과시킨다.
```

## 17. 재현 범위의 한계

이 구현은 rigid-body fixed-joint reaction의 좌표계, 부호와 정적 하중 분배를 검증한다.
실물 Axia80의 calibration matrix, noise, quantization, bandwidth, filtering, latency,
bias/temperature drift, saturation과 overload는 포함하지 않는다. Inspire Robot을 실제
tool로 교체할 때에는 질량, center of mass, collision geometry와 sensor-to-tool
transform을 실측값으로 바꾸고 같은 tare/actual-pose/acceptance 절차를 다시 적용해야
한다.
