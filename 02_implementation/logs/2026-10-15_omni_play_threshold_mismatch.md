# Omni 최근 checkpoint 재생의 속도 종료 기준 차이

[로그 목록](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

기록일: 2026-10-15. 대상은 workspace 루트의 `2026-10-14_22-34-42_centered_spawn_goal15cm_arm2rad`이며, 확인한 마지막 checkpoint는 `model_3550.pt`다. 사용자는 Omni v0 재생에서 `env.terminations.hand_velocity.params.threshold=100.0` override를 추가하지 않았다고 확인했다.

## 확인한 사실

`params/env.yaml`을 `yaml.BaseLoader`로 읽었다. 학습 당시 `hand_velocity`의 threshold는 100.0 rad/s다. 현재 `InspireSweepOmniEnvCfg`는 Baseline의 `TerminationsCfg.hand_velocity`를 상속하므로 v0의 기본값은 1.0 rad/s다. 이름과 달리 Arm 6개 관절 중 하나라도 절대 속도가 이 값을 초과하면 종료한다.

`play.py`는 task registry의 환경 Cfg를 생성하고 checkpoint의 정책 가중치를 로드한다. Checkpoint 옆 `params/env.yaml`을 자동 로드하지 않는다. 따라서 사용자가 확인한 실행 조건에서는 학습과 다른 1.0 rad/s 기준이 적용된다.

TensorBoard 원시 이벤트를 `RawEventFileLoader`와 `Event.FromString`으로 순회해 총 3,556개 iteration을 읽었다. 마지막 iteration 3555의 통계는 다음과 같다.

| 종료 항목 | 값 |
| --- | ---: |
| time_out | 0.9941542 |
| shelf_collision | 0.0058458 |
| hand_velocity | 0 |
| object_drop / push_fast / object_outside_shelf / shelf_displacement / success | 모두 0 |

최근 iteration의 평균 에피소드 길이는 약 495–500스텝이다. 이는 학습 당시의 종료 통계이며 이번 GUI 재생의 실제 종료 flag를 기록한 데이터가 아니다. 마지막 iteration의 mean_reward는 약 −4.081e25로 비정상적으로 크지만, 그 값은 checkpoint iteration 3550 이후의 기록이다. 이 값만으로 `model_3550.pt`의 재생 종료 원인을 단정하지 않았다.

체크포인트를 `torch.load(..., map_location="cpu", weights_only=True)`로 읽어 저장된 `iter=3550`을 확인했다. 모델을 PhysX에서 실행하거나 관절 속도를 측정하지는 않았다.

## 판단과 확인 범위

사용자가 override를 생략한 사실과 설정 대조를 근거로, **학습 때 100.0이던 Arm 속도 종료 기준이 재생 때 1.0으로 낮아진 것이 즉시 종료의 가장 유력한 원인**이다. 실제 GUI 재생의 종료 term buffer는 확보하지 않았으므로 다른 종료 항목의 동시 활성화까지 확인한 것으로 보고하지 않는다.

학습과 같은 기준을 사용하려면 v0 play 명령에 다음 Hydra 인자를 추가한다.

```bash
env.terminations.hand_velocity.params.threshold=100.0
```

환경 코드·정책·기존 자산과 사용자 변경은 수정하지 않았다. 새 GPU 재생이나 CPU 회귀 테스트는 실행하지 않았고, 로그 읽기·설정·play 경로·checkpoint metadata 확인만 수행했다. 문서 수식·링크·diff 검사는 작성 후 확인한다.

## 로그 전 구간 재확인과 판단의 한계

사용자가 TensorBoard의 Hand Velocity Termination 0.0을 지적하여 같은 원시 이벤트를 다시 집계했다. 위의 속도 기준 차이는 재생 설정에 관한 가설이며, 학습 로그에서 확인된 종료 원인으로 제시해서는 안 된다.

- 전체 iteration 0–3555의 **3,556개 hand_velocity 값이 모두 정확히 0**이다(min=0, max=0, nonzero=0).
- Checkpoint iteration 3550: `time_out=0.994995117`, `shelf_collision=0.005004883`, 나머지 종료 항목은 모두 0. 평균 에피소드 길이는 495.16스텝(약 9.90초)이다.
- 초기 iteration 1: `shelf_collision=0.998942077`, `push_fast=0.000501845`, `hand_velocity=0`, 평균 길이 15.46스텝이다. 초기 실패의 주된 기록은 shelf_collision이다.
- 학습 전체에서 hand_velocity·object_drop·object_outside_shelf·shelf_displacement·success는 한 번도 비영값으로 기록되지 않았다. Push_fast는 일부 구간에 기록됐으며 최대 통계값은 약 0.03320이다.

`shelf_collision`은 실제 ContactSensor 충돌 bit가 아니라, 아래 조건 중 하나의 OR이다.

1. 선반의 root 6D 속도 벡터 norm이 0.1 초과.
2. 두 가상 finger frame 중 하나라도 선반 기준면(root Z + 1.05 m)보다 1 cm 미만 높이에 있음.
3. 가상 wrist frame이 같은 기준면보다 7 cm 미만 높이에 있음.

초기 선반 root Z=0이면 finger frame의 world Z <1.06 m 또는 wrist frame의 world Z <1.12 m도 이 term을 발생시킨다. 따라서 이 이름만으로 실제 손-선반 접촉이나 힘 임계값 초과를 의미한다고 해석하지 않는다. 기존 이벤트 로그에는 이 세 내부 조건을 분리한 값이 없어 어느 하위 조건인지는 확정할 수 없다.

**로그 기반 결론:** 이 학습 run의 초기 실패는 주로 shelf_collision, 최근 종료는 거의 time_out이다. Hand velocity 종료로 학습이 즉시 끝났다는 근거는 없다. 기존 `play.py`는 episode 종료 flag를 파일에 저장하지 않으며 이 폴더에 별도의 play trace도 없어, 이번 재생의 즉시 종료 항목은 이 학습 로그만으로 확정할 수 없다. 학습·재생 구분과 측정 한계를 우선해 설명한다.

재집계는 Isaac Lab Python에서 `RawEventFileLoader`/`Event.FromString`으로 모든 `Episode_Termination/*`와 episode length를 읽어 count/min/max/nonzero 및 특정 iteration 값을 출력했다(exit 0). 실제 재생은 실행하지 않았다.
