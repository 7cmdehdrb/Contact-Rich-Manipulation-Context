# 코드·학습·장비 현황

[문서 안내](README.md) · [문헌조사](literature/README.md) · [조사 그룹](literature/reviews/README.md)

기준일: 2026-09-14. 출처는 [출처 목록](06_SOURCE_REGISTER.md)을 따른다. **과거 구현 보고, 별도 센서 시험, 설정 코드, 구매 계획, 실제 설치·성능을 분리한다.**

## 1. 현재 확인 수준

| 항목 | 문서·대화로 확인한 내용 | 직접 검증하지 못한 내용 |
| --- | --- | --- |
| 인계 저장소 | 작성 전 main에는 간단한 README만 있던 문서 저장소 | 실제 구현 저장소 경로·커밋 |
| 기존 Sweeping 기반 | 9/10 기존 환경 수정·다른 초기 joint state에서 조작 보고 | 최신 전체 코드·test·checkpoint |
| Arm action/controller | 9/10 Cartesian/OSC 변경 보고 | 현재 controller와 정확한 action semantics |
| Observation | 일부 absolute→relative 변경 보고 | 현재 actor/critic tensor와 GT 경로 |
| 초기 상태 | EEF·joint config·물체 randomization 보고 | 실제 approach error에 근거한 분포 |
| 정책의 접촉 관측 | 9/10 당시 F/T·tactile 미사용 명시 | 그 뒤 추가 구현 여부 |
| 별도 촉각 시험 | 9/10 압저항 센서의 약한 신호·접촉면적 영향 보고 | 원시 로그·정량 감도·정확한 시험 센서 모델 |
| 학습 | 9/11 PPO runner 코드 공유 | 실제 run·version·환경 수·성능 |
| 계획 중 장비 | 9/14 센서·Hand 실물이 아직 준비되지 않았다고 보고 | 이후 도착·장착·수신·제어 완료 여부 |
| Sim-to-Real | 9/10은 검증 전 | 성공 결과·실물 종료·안전 개입 로그 |

근거: S-REPO, S-0910, C-PPO, S-0914. 현재 코드가 반드시 9/10 그대로라는 뜻이 아니다. **이후 변경을 입증하는 코드·로그를 이번에 확인하지 못했다**는 의미다.

## 2. 기존 구현과 센서 시험은 서로 다른 증거

### 2.1 Sweeping 환경의 구현 보고

S-0910 §2에 따르면 joint-space action을 Cartesian/EEF-space와 OSC로 변경했고 일부 observation을 상대 표현으로 바꾸었다. 넓은 초기 EEF/joint configuration과 랜덤 물체 배치를 시험했다. 다른 초기 joint state에서도 sweeping을 수행했다는 보고가 있다.

하지만 F/T·tactile 없는 사전 feasibility였으므로 새로운 센서 기반 Blind 정책의 기여를 입증하지 않는다. 실제 접근 후 pose error 분포도 당시 미반영이었다.

이후 S-TASK1 §5는 Cartesian 이동 명령을 Diff-IK 등의 방식으로 관절 명령으로 바꾸는 구상을 제시한다. 이를 OSC→Diff-IK 전환 완료로 해석하지 않는다. 실제 `policy action → controller → robot command`를 코드에서 확인한다.

### 2.2 압저항 촉각 센서 시험 보고

S-0910 §8에는 별도로 시험 중인 piezoresistive tactile sensor의 sensitivity가 낮다는 보고가 있다. 3D printing과 분동으로 예정 Hand와 유사한 무게를 구성하고, 빠른 이동과 더 무거운 물체 등을 시험했으나 충분한 contact signal이 나오지 않는 경우가 있었다. 넓은 접촉면에서 감지가 어렵고 좁은 면에서 압력이 집중될 때 신호가 상대적으로 잘 나타났다는 설명이다.

**이 결과의 대상은 당시 시험 센서다.** 예정된 Inspire Hand의 tactile 17개 영역 또는 Axia80의 실효 감도를 측정한 결과로 전용하지 않는다. 구체적인 force threshold·정확도·주기 수치는 raw와 시험 조건 없이 만들지 않는다.

교수는 센서 자체 개발에 과도하게 매몰되지 말고, wrist F/T·joint torque·무게·마찰·접촉면적 조정 등의 대안을 검토할 수 있다고 했다. 이는 대안 후보이지 모든 방법이 검증됐다는 뜻은 아니다. 조건을 변경해 감지가 쉬워진 시험과 원래 가벼운 물체 조건을 구분해 보고해야 한다.

## 3. 2026-09-11 PPO 설정 스냅샷

출처 C-PPO: 현재 제공된 프로젝트 대화의 코드. **최신 권장값 또는 바로 실행할 코드가 아니다.** import·설치 version·실제 run 적용 여부는 먼저 확인한다.

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

이 설정만으로 observation/action dimension, action scale, control frequency, num_envs, reward, termination을 알 수 없다. 여기서 `clip_param`은 PPO 설정이지 실제 robot action clipping을 설명하는 값이 아니다. 실제 learning rate의 변화도 로그로 확인한다.

F/T·촉각을 추가하면 입력 단위·분포가 달라질 수 있지만, normalization이나 learning rate를 자동 변경하라는 뜻은 아니다. 입력 범위·전처리·적용 config·rollout·loss·성공/종료 로그를 먼저 확인한다. PPO 조정을 센싱 feasibility 검증의 대체물로 삼지 않는다.

## 4. 하드웨어 계획과 준비 상태

| 구성 | 프로젝트 계획 | 실제 확인할 것 |
| --- | --- | --- |
| Arm | UR5e, 6축 | 제어 경로·tool frame·driver·ROS 환경 |
| Wrist F/T | ATI Axia80-M8, Ethernet 구매 방향 | 주문 모델·calibration·raw 포맷·단위·주기·장착·영점 |
| Hand | Inspire Robot Dexterous Hand, 6자유도 전제 | 모델·구동 joint mapping·command mode·전원·통신 |
| Tactile | Hand의 17개 센서 영역 전제 | 위치·면적·raw Grid·단위·유효 상태·실효 감지 |
| Camera | 초기 시각 정보 획득 | 실제 perception 구성·관측 시점·접근 오차 |

장비 구성과 tactile 표현은 S-TASK1, Ethernet 방향은 C-HARDWARE, 실물 미준비 보고는 S-0914가 근거다. 제조사 최신 데이터시트로 제원을 별도 재검증한 것은 아니다.

S-0910 §11에서 업체 답변 기준 약 4주, **2026년 10월 중순 도착 가능성**이 논의됐고 계약 절차도 남아 있었다. 이는 당시의 예상이다. 확정 배송일이나 지금의 납기로 취급하지 않는다. 장비가 없더라도 simulation·초기조건·reward·sensor 관련 검토를 진행할 수 있다는 지시를 함께 보존한다.

이전 Robotiq 2F-85 조건의 부하·모멘트 계산이나 별도 ROS1 Docker·OSC task 설정을 현재 Inspire Hand 시스템에 자동 적용하지 않는다. Hand의 질량·질량중심·장착이 다르면 부하 보정과 안전 조건의 근거도 재확인한다.

## 5. 다음 구현 에이전트가 채울 표

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
| 기존 압저항 센서 시험 모델·raw log | 미확인 |  |
| 신규 Hand·F/T 준비·raw sample | 미확인 |  |

공백을 상상으로 채우지 않는다. 실제 파일·장비·로그로 확인한 항목만 업데이트한다. 새 방향이 나왔다는 이유로 이미 구축 중인 관련 기반 전체를 폐기하지 않고 필요한 변경을 분리한다. [S-0910 §13-G]
