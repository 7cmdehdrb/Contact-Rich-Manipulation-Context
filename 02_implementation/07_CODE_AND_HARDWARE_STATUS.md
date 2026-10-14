# 코드·학습·장비 현황

[문서 안내](../01_plan/README.md) · [문헌조사](../01_plan/literature/README.md) · [조사 그룹](../01_plan/literature/reviews/README.md)

기준일: 2026-10-14. 출처는 [출처 목록](../01_plan/06_SOURCE_REGISTER.md)을 따른다. **현재 코드 검토, 과거 구현·실행 보고, 별도 센서 시험, 구매 계획, 실제 설치·성능을 분리한다.**

## 현재 코드와 문서의 확인 범위

활성 패키지는 사용자 결정에 따라 `src/inspire_sweep_baseline`, `src/axia80_feasibility`다. 나머지는 `src/trash`에 보존한다. 전체 등록 ID·환경/설정 상속·입출력·실행 명령은 [활성 환경 안내](08_ACTIVE_ENVIRONMENTS.md), workspace 역할과 외부 자산·산출물 위치는 [구조 안내](../00_guidelines/10_WORKSPACE_GUIDE.md)를 따른다.

| 항목 | 현재 확인한 사실 | 추가 확인 또는 적용 경계 |
| --- | --- | --- |
| 활성 학습 코드 | 독립 `inspire_sweep_baseline`에 Baseline·Realistic Physics·Initial Privileged·Omni task가 등록됨 | 등록·정적 계약과 실제 학습 성공을 구분 |
| 환경 상속 | 공통 `InspireSweepEnv`는 Isaac Lab `ManagerBasedRLEnv`를 상속하고, 설정 변형은 공통 기반 설정에서 분기 | 참고 프로젝트에서 가져온 이력과 Python 상속 의존성은 별개 |
| 제어와 관측 | Arm Joint Position 6D + Hand 2D. 기본 baseline은 현재 물체 위치와 tactile/F/T를 포함한 41D | 발표의 57D/8D·OSC 또는 최종 Blind 정책과 동일하지 않음. 변형별 GT 경계는 활성 환경 문서 확인 |
| 센서 검증 코드 | Axia80 정하중·cantilever·tilt·angle sweep 코드와 CPU 계약 검사가 있음 | 실제 물리 응답·새 실행 결과는 simulator 로그로 확인 |
| 센서 실험 기록 | [2026-09-22 구현·재현](experiments/2026-09-22_axia80_ft_sensor_implementation.md)과 [결과](experiments/2026-09-22_axia80_ft_sensor_feasibility.md)가 있음 | 당시 simulation 결과. 구매 실물 센서의 감도·정확도 검증과 구분 |
| 과거 RL 실행 | [10월 로그](logs/README.md)에 Reach/Sweep 실패 관찰, Hand 이식 실험, checkpoint·차원 조사 기록이 있음 | 10월 12일 조사 자체에서 학습·재생·성공률 평가를 실행하지 않음 |
| Scene 도구 | `scene_randomization`의 기하 생성·분포·접근 경로 검사 코드와 설명이 있음 | 실제 로봇 운동학·접촉 물리 및 활성 RL reset 통합과 구분 |
| 실물·실행 기반 | 코드와 문서의 경로·설정은 읽을 수 있음 | 장비 도착·장착·통신, 라이브러리 설치 버전, 외부 선반 asset 가용성, 새 학습·실물 성능은 별도 확인 |

이번 문서 정리는 구현·로그의 누락된 탐색 경로를 연결한 작업이다. 새 학습이나 실물 시험이 수행된 것으로 보고하지 않는다. 이후 결과는 [개발 지침](../00_guidelines/09_DEVELOPMENT_GUIDE.md)에 따라 명령·상속·기준 commit·원시 로그·검증 결과를 연결하여 기록한다.

## 1. 최초 인계 당시 확인 수준 — 2026-09-14

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

근거: S-REPO, S-0910, C-PPO, S-0914. 이 표는 9월 14일 인계의 확인 범위를 보존한다. 이후 코드·센서 구현·실행 기록은 문서 상단과 활성 환경·개발 로그에서 확인한다. 과거의 미확인을 현재 코드 부재로 해석하지 않는다.

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

## 5. 최초 인계의 확인 체크리스트 — 현재 적용값은 활성 환경 안내 참조

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

이 표는 최초 인계에서 남겨 둔 체크리스트다. 현재 코드로 확인한 환경·상속·입출력·실행 항목은 [활성 환경 안내](08_ACTIVE_ENVIRONMENTS.md)에 기록한다. 남은 설치 버전·외부 자산 가용성·실제 평가·실물 데이터를 상상으로 채우지 않는다. 이후 검증은 실제 파일·장비·로그와 연결한다. [S-0910 §13-G]
