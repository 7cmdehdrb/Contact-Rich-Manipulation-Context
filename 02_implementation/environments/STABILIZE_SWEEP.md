# Inspire-Stabilize-Sweep-v0

[명세](../../01_plan/environments/2026-11-18_stabilize_sweep_spec.md) · [구현·검증 기록](../logs/2026-11-18_stabilize_sweep_implementation.md)

ForceDirection을 기능 기준으로 삼는 독립 환경이다. 기존 환경 Cfg/runtime 상속 없이 같은 로봇·자산·제어·물성 분포를 사용한다. 단일 정책이 총10초 동안 Stabilize → Sweep을 수행한다.

- 관측: initial visible surface XYZ를 현재 EEF로 변환. 정책67D(단계1D 포함), 장애물 valid+XYZ16슬롯64D, Actor/Critic 동일 입력. 현재 물체 GT는 정책에 제공하지 않는다.
- 행동: 팔6D relative pose OSC + 손6축 절대 rad, Runner clip±π/2. physics100Hz/policy50Hz.
- Gate:100Hz에서30연속 유효 sample, 영구 latch. 통과 step은 Stabilize 보상, 다음 action부터 Sweep.
- 보상: setup/완료1.0, 초기 이동·회전 비용 각각−1.0, 압착−1.0. Sweep30×거리 감소×정규화 접촉×힘 방향, 후퇴−38.91×거리 증가. 기존 공통 비용·일정은 보존하되 새 환경의 F/T5% 상한만 제거한다.
- 성공:10초 timeout, Gate 달성, 현재 centroid XY 거리<3cm, 동시 물리 실패 없음. 조기 목표 성공 종료 없음.

역할별 구현은 활성 패키지의 `stabilize_sweep*.py`에 있으며, 등록은 `inspire_sweep_baseline/__init__.py`, 실제 runtime은 `runtime/stabilize_sweep.py`, PPO는 `agent/stabilize_sweep_ppo_cfg.py`다. 환경 Cfg는 `envs/stabilize_sweep_envs.py`다.

## 실행과 현재 제한

검증은 Isaac Lab Python 환경에서 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless
```

학습 진입점은 기존 `src/inspire_sweep_baseline/scripts/train.py`, task는 `Inspire-Stabilize-Sweep-v0`다. **현재 학습 준비 완료 상태로 간주하지 않는다.** 합의한 초기 자세 조건에서 일부 목표는4후보 IK가 미수렴하여 reset이 의도대로 오류로 끝난다. 사용자는 조건 변경 대신 이 상태를 유지하고 Ticket10의 행동 평가를 미완료로 기록하도록 했다. 실제 Gate 달성과 학습 행동 품질은 미검증이다.

초기 손의 원래0rad 내부 메쉬 겹침은 사용자 승인으로 검사에서 제외하며, 새 팔–팔·팔–손 충돌은 검사한다. 장애물 배치는 한 번, 관측은 최대 두 번이며 미배치 후보만 생략한다. 부분 reset은 다른 환경의 physics를 진행하지 않는다.
