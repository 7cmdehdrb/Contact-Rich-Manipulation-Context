# 코드·학습·장비 현황

기준일: 2026-09-14. 출처 ID는 [출처 목록](06_SOURCE_REGISTER.md)에 정의한다. **과거 구현 보고, 대화의 설정값, 구매 계획, 실제 확인된 설치·성능을 분리한다.**

## 1. 현재 확인 수준

| 항목 | 확인된 내용 | 확인되지 않은 내용 |
| --- | --- | --- |
| 인계 저장소 | 문서 저장소. 작성 전 main에는 간단한 README만 있었음 | 실제 구현 저장소의 경로·커밋 |
| 기존 Sweeping 기반 | 9/10에 기존 환경을 수정했다는 보고 | 최신 원본 전체, 테스트·checkpoint |
| Arm action/controller | 9/10 Cartesian/OSC 변경 보고 | 현재 배포 controller와 정확한 action semantics |
| Observation | 일부 absolute→relative 변경 보고 | 최신 actor/critic tensor와 GT object state 경로 |
| 초기 상태 | EEF·joint config·물체 위치 randomization 보고 | 실제 approach error에 근거한 분포 |
| 접촉 관측 | 9/10 당시 F/T·tactile 없다고 명시 | 이후 추가 구현 여부 |
| 학습 | 9/11 PPO runner 코드 공유 | 실제 실행 version·num_envs·run·성능 |
| 실물 | 9/14에 센서·Hand가 아직 준비되지 않았다고 보고 | 이후 도착·장착·수신·제어 완료 여부 |
| Sim-to-Real | 9/10은 검증 전 | 성공 결과·종료 기준·안전 개입 기록 |

근거: S-REPO, S-0910, C-PPO, S-0914. 이 표는 현재 코드가 반드시 9/10 그대로라는 뜻이 아니다. **이후 변경을 증명하는 자료를 이번에 확인하지 못했다**는 의미다.

## 2. 보존해야 할 과거 구현 정보

S-0910의 보고에 따르면 joint-space action을 Cartesian/EEF-space와 OSC로 변경했고, 일부 observation을 상대 표현으로 바꾸었다. 넓은 초기 EEF/joint configuration과 랜덤한 물체 배치를 시험했다. 다른 초기 joint state에서도 sweeping을 수행했다는 보고가 있다.

하지만 이 결과는 F/T·tactile 없는 사전 feasibility였다. 새로운 센서 기반 정책의 기여를 입증하지 않는다. 실제 접근 후 pose error 분포도 아직 반영하지 않았다고 정리되어 있다.

이후 TASK 1안은 Cartesian 이동 명령을 Diff-IK 등의 방식으로 관절 명령으로 바꾸는 구상을 제시했다. 이를 OSC에서 Diff-IK로 전환 완료했다는 사실로 바꾸지 않는다. 실제 `policy action → controller → robot command`를 코드에서 확인해야 한다.

## 3. 2026-09-11 PPO 설정 스냅샷

출처 C-PPO. 아래는 프로젝트 대화에서 공유된 설정이며 **최신 권장값 또는 즉시 실행할 코드가 아니다.** import와 version은 제공되지 않았으므로 설치된 API에 맞는지 먼저 확인한다.

```python
@configclass
class UR5eSweepPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 36
    max_iterations = 90000
    save_interval = 50
    experiment_name = "UR5e_shelf_sweep_random"
    run_name = ""

    policy = RslRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_obs_normalization=False,
        critic_obs_normalization=False,
        actor_hidden_dims=[256, 128, 64],
        critic_hidden_dims=[256, 128, 64],
        activation="elu",
    )

    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.005,
        num_learning_epochs=8,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",
        gamma=0.98,
        lam=0.95,
        desired_kl=0.02,
        max_grad_norm=1.0,
    )
```

이 설정만으로는 observation dimension, action dimension, clipping, action scale, control frequency, num_envs, recurrent 사용, reward, termination을 알 수 없다. adaptive schedule에서 실제 learning rate 이력이 어떻게 변했는지도 로그로 확인해야 한다.

F/T·촉각을 추가하면 입력 단위와 분포가 달라질 수 있다. 그렇다고 normalization이나 learning rate를 자동 변경하라는 뜻은 아니다. 먼저 값의 범위와 전처리, 적용 config, rollout·loss·성공/종료 로그를 확인한다. PPO hyperparameter 조정을 센싱 feasibility 검증의 대체물로 사용하지 않는다.

## 4. 하드웨어 계획과 준비 상태

| 구성 | 프로젝트 계획 | 반드시 확인할 것 |
| --- | --- | --- |
| Arm | UR5e, 6축 | 실제 제어 경로, tool frame, 사용 driver·ROS 환경 |
| Wrist F/T | ATI Axia80-M8, Ethernet 방향 | 정확한 주문 모델, calibration, 수신 포맷·단위·주기, 장착·영점 |
| Hand | Inspire Robot Dexterous Hand, 6자유도 전제 | 정확한 모델, 구동 joint mapping, command mode, 전원·통신 |
| Tactile | 17개 센서 영역 전제 | 센서 ID·위치·면적·raw Grid·단위·유효 상태·실효 감지 |
| Camera | 초기 시각 정보 획득 | 최종 perception 구성과 접근 중 관측 시점 |

UR5e–F/T–Hand 구성과 촉각 표현은 S-TASK1, Ethernet 구매 방향은 C-HARDWARE, 실물 미준비 보고는 S-0914가 근거다. 표의 제원을 제조사 최신 데이터시트로 이번에 별도 재검증한 것은 아니다.

과거 대화의 Robotiq 2F-85 부하·모멘트 계산, 다른 카메라·ROS1 Docker 경험, 별도 OSC task의 설정을 현재 Inspire Hand 연구에 그대로 적용하지 않는다. Hand 무게와 center of mass가 다르면 기존 보정·안전 조건의 근거부터 다시 확인해야 한다.

## 5. 다음 구현 에이전트가 먼저 채울 표

| 항목 | 확인값 | 근거 |
| --- | --- | --- |
| 구현 저장소/브랜치/커밋 | 미확인 |  |
| 환경 클래스·등록 task ID | 미확인 |  |
| Isaac Sim / Isaac Lab / RSL-RL version | 미확인 |  |
| OS·Python·ROS·UR driver | 미확인 |  |
| 실행 명령·적용 config | 미확인 |  |
| actor/critic observation term과 shape | 미확인 |  |
| action semantics·scale·frame | 미확인 |  |
| controller·제어/정책/sensor rate | 미확인 |  |
| reward term·계수 | 미확인 |  |
| success/termination/timeout | 미확인 |  |
| initial/reset distribution | 미확인 |  |
| sensor simulation과 GT 분리 | 미확인 |  |
| run·checkpoint·seed·평가 log | 미확인 |  |
| 실물 장비 준비·raw sample | 미확인 |  |

새 에이전트는 이 표의 공백을 상상으로 채우지 않는다. 실제 파일을 읽거나 실행 로그로 확인한 항목만 업데이트한다.
