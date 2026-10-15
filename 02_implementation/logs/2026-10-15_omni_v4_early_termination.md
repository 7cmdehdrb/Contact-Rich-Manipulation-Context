# Omni v4 초기 Arm 속도 종료 — run 비교

[로그 안내](README.md) · [V4 구현](2026-10-15_omni_v4_speed_penalty.md)

기록일: 2026-10-15. 사용자는 원격 V3·Dex에서는 팔이 움직이지만 로컬 V4는 `hand_velocity` 종료가 반복된다고 보고했다. 저장 설정과 TensorBoard의 기록을 읽은 진단이며, 새 시뮬레이션·학습이나 코드 수정은 수행하지 않았다. 실행 중인 학습은 변경하지 않았다.

## 확인한 run

| 위치·run | 확보한 기록 수 또는 마지막 iteration | 평균 episode 길이 마지막 값(step) | Arm 속도 종료 마지막 값 |
| --- | --- | --- | --- |
| 로컬 `inspire_sweep_omni_v4/2026-10-15_20-20-32` | 268개 scalar 기록 시점 | 2.0 | 1.0 |
| 로컬 `inspire_sweep_omni_v3/2026-10-15_19-14-06_height_gated_xy_reach` | 813개 scalar 기록 시점 | 2.0 | 1.0 |
| 로컬 `logs/TEMP2/2026-10-15_16-53-45_dex_best_distance` | 3528개 기록 | 11.55 | 약 0.415 |
| 원격 V3 `2026-10-15_15-32-26_height_gated_xy_reach` | iteration 1566 | 2.0 | 1.0 |
| 원격 V3 `2026-10-15_16-53-58_height_gated_xy_reach` | iteration 7060 | 10.91 | 약 0.459 |

로컬 로그는 `logs/rsl_rl` 아래에서, 원격은 사용자가 제공한 [TensorBoard](http://192.168.0.180:6006/#timeseries)의 읽기 전용 API에서 확인했다. 원격 scalar API는 조회 시 run당 최대 1000개로 샘플링된 데이터를 반환했다. 원격 두 run은 이름이 V3로 같아도 학습 곡선은 다르다. 로컬 V3의 짧은 종료를 사용자가 본 원격 V3의 상태로 일반화하지 않는다.

원격 후반 V3의 `push_fast` 마지막 값은 약 0.989다. 종료 term은 동시에 참일 수 있으므로 이 수치와 `hand_velocity` 약 0.459를 서로 배타적인 종료 비중으로 해석하지 않는다. 물체 이동이 발생한다는 근거이며 Sweep 성공을 입증하지 않는다.

## 저장 설정 대조

로컬 V3와 V4의 `params/env.yaml`을 `yaml.BaseLoader`로 읽어 전체 비교했다. 차이는 log 경로, 새 `pushing_speed` 비용, Arm 속도 1.5 → 3.0, 물체 속도 0.3 → 0.5, 선반 외곽 종료 비활성뿐이었다. PPO 저장 설정은 experiment/run 이름 외에 같았다. 관측·action·로봇·actuator·reset 구성 차이는 없었다.

보관된 Dex run의 저장 Arm 속도 threshold는 **5.0 rad/s**다. 로컬 V4는 **3.0 rad/s**다. Dex와 V4의 Action·Observation 저장 설정은 동일했고 Scene 차이는 로봇 USD의 머신별 절대경로였다. 경로가 같은 자산 내용이라는 보장은 없으므로 USD 파일 해시까지 같다고 판단하지 않는다.

사용자는 원격 현재 코드의 threshold가 **1.5**라고 확인했다. 이는 현재 소스 값이며, 아직 원격 정상 run의 **저장 `params/env.yaml` 값**을 읽은 것은 아니다. 실행 중인 프로세스는 시작 시 읽은 설정을 유지하므로 현재 코드만으로 과거 run threshold를 확정하지 않는다. TensorBoard `/data/plugin/text/tags`는 빈 객체였고 저장 YAML은 이 API에서 제공되지 않았다. 로컬 SSH config도 없어 원격 파일을 직접 읽지 못했다. 해당 YAML의 `hand_velocity` 블록을 사용자에게 요청했다.

## 코드상 확인과 가설

`hand_velocity`는 Arm 실제 관절속도 중 하나라도 threshold를 넘는지 검사한다. Arm Action은 `기본 관절각 + 0.5 × raw action`인 절대 위치 목표이며 속도 제어가 아니다. Action clip과 runner clip은 null이다. 저장된 actuator의 simulation 속도 한계는 Arm 앞 3관절 3.14 rad/s, wrist 3관절 6.28 rad/s다. 그러므로 actuator 속도 제한만으로 V4의 3.0 초과를 방지하지 않는다.

직접 관찰한 현상은 V4가 약 2 step(0.04 s)에서 Arm 속도로 종료된다는 것이다. 왜 정상 원격 run과 달라졌는지에 대한 근본 원인은 아직 미확정이다. 다음 가설을 구분해야 한다.

1. 원격 정상 run의 시작 당시 속도 제한 또는 제어·보상·물리 설정이 현재 소스와 다름: 저장 YAML·코드 revision·USD 해시·Isaac Sim 버전을 비교한다.
2. 초기 정책 명령이 Arm 속도를 유발함: 동일 상태에서 Arm action 0/Hand OPEN과 실제 정책 action의 auto-reset 전 관절속도를 비교한다.
3. 초기 자세·접촉 또는 물리 실행 차이로 무입력에서도 속도가 발생함: 위 무입력 대조에서 속도 초과가 남는지 검사한다.
4. 짧은 접근 진전에 보상이 집중되어 초기 종료 패턴이 학습 중 유지됨: 실제 action·목표각·최초 초과 관절 및 대조 실험이 필요하다. 집계 reward만으로 의도적인 조기 종료나 인과관계를 확정하지 않는다.

V4 `pushing_speed`는 조회한 모든 기록에서 0이다. 이는 Arm 속도와 별개의 물체 속도 항이다. 물체를 빠르게 밀 기회가 충분하지 않은 짧은 episode와 부합한다. 이 항이 모든 transition에서 0이면 정책 loss의 새 직접 보상 신호는 제공하지 않지만, 부수적인 초기화·실행 차이까지 없다는 뜻은 아니다.

## 실제 확인 방법과 범위

로컬은 `/home/min/miniconda3/envs/env_isaaclab/bin/python -`에서 `EventAccumulator(run, size_guidance={'scalars': 0})`로 전체 scalar를 읽고 첫 값·마지막 값·범위를 계산했다. YAML은 같은 Python의 `yaml.load(..., Loader=yaml.BaseLoader)`로 읽어 키별 비교했다. 최근 V4 100개 기록에 대해 `hand_velocity==1`, `pushing_speed==0`, 평균 길이 2.1 step 이하를 assert했고 모두 확인했다. 실시간 로그이므로 표는 조회 snapshot이다.

원격은 Python `urllib.request.urlopen`으로 다음 API를 조회해 exit 0으로 결과를 얻었다.

- `/data/logdir`, `/data/runs`, `/data/plugin/scalars/tags`
- `/data/plugin/scalars/scalars?run=<URL 인코딩한 run>&tag=<URL 인코딩한 scalar>&format=json`
- `/data/plugin/text/tags`

새 GPU 실행·remote shell·checkpoint 재생·물리 재현은 하지 않았다. 정상 원격 run의 저장 YAML·실행 코드·초기 상태별 관절속도를 확보하기 전에는 원인을 threshold 하나로 단정하거나 제한·gain·보상을 변경하지 않는다.

## 후속 확인 — 가져온 원격 run의 저장 설정

사용자가 workspace 루트에 두 원격 run을 제공해 저장 설정·이벤트 로그·Git snapshot을 직접 확인했다. 앞 절의 원격 YAML 미확보 상태는 이 후속 확인으로 해소됐다.

| 제공한 run | 저장된 `hand_velocity.params.threshold` | 마지막 iteration | 마지막 평균 episode 길이 | 마지막 Arm 속도 종료 |
| --- | --- | --- | --- | --- |
| `2026-10-15_16-53-45_dex_best_distance` | **5.0 rad/s** | 6317 | 약 11.73 step | 약 0.548 |
| `2026-10-15_16-53-58_height_gated_xy_reach` | **5.0 rad/s** | 7130 | 약 10.95 step | 약 0.445 |
| 로컬 V4 `2026-10-15_20-20-32` | **3.0 rad/s** | 338 | 2.0 step | 1.0 |

현재 코드의 1.5가 원격 학습 당시 값이라는 해석은 저장 YAML과 일치하지 않았다. 원격 V3의 Git snapshot은 commit `21bbae5f0fcaeaf3eb4014dd92f026b6cae9158c`이며, `git show <commit>:src/inspire_sweep_baseline/inspire_sweep_baseline/omni_env_cfg.py`에서도 당시 V1의 threshold가 **5.0**임을 확인했다. 이 설정은 V3로 상속된다.

실행한 설정·로그 검사는 `/home/min/miniconda3/envs/env_isaaclab/bin/python -`에서 세 run의 `params/env.yaml`을 `yaml.BaseLoader`로 읽고 원격 V3→로컬 V4를 재귀 비교한 것이다. 원격 두 run과 V4의 TensorBoard scalar도 `EventAccumulator`로 전체 읽었다. 모두 exit 0이었다. 해당 비교에서 원격 V3와 로컬 V4의 차이는 다음뿐이었다.

- Arm 속도 종료 **5.0 → 3.0**.
- 물체 속도 종료 0.3 → 0.5, 선반 외곽 종료 비활성, `pushing_speed` 비용 추가.
- 머신별 log_dir와 로봇 USD 절대경로.

Action·Observation·actuator 설정과 그 밖의 설정은 같았다. 자산 경로의 내용·실제 설치 버전은 직접 비교하지 않았다. 저장값은 다음 명령으로도 확인했다.

```bash
rg -n 'threshold: 5.0|threshold: 3.0' \
  2026-10-15_16-53-58_height_gated_xy_reach/params/env.yaml \
  2026-10-15_16-53-45_dex_best_distance/params/env.yaml \
  logs/rsl_rl/inspire_sweep_omni_v4/2026-10-15_20-20-32/params/env.yaml
```

따라서 잘 움직이는 원격 V3·Dex보다 V4의 Arm 속도 제한이 더 엄격하다는 **실제 설정 차이**를 확정했다. 3–5 rad/s 구간의 움직임은 두 원격 run에서 허용되지만 V4에서는 종료된다. 이 차이가 비교 모순을 해소한다. 다만 같은 seed·코드·머신에서 threshold만 바꾼 물리 대조를 수행하지 않았으므로, 이 차이 하나만으로 전체 학습 결과의 인과관계를 입증했다고 기록하지 않는다.

요청한 V4 threshold **3.0은 변경하지 않았다**. 가져온 checkpoint 재생이나 새 GPU 실험도 하지 않았다. 정확한 최초 초과 관절과 정책 action의 기여는 여전히 별도 측정 대상이다.
