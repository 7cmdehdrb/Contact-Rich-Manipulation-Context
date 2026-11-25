# Prof Revision v0_3_1 손가락 거리·각도 결합

[환경 계약](../environments/PROF_REVISION_V0.md#prof-revision-v0_3_1) · [계통](../environments/PROF_REVISION_FAMILY.md)

## 요청·해석

2026-11-25 사용자 요청은 `Inspire-Sweep-Prof-Revision-v0_3`를 직접 상속하는 `Inspire-Sweep-Prof-Revision-v0_3_1` 추가다. 손가락 자세 보상에 기존 거리·각도 결합만 도입하고, 관절 속도 사건 비용 등 다른 v1 동작은 가져오지 않는다.

사용자가 지칭한 `Inspire-Sweep-Prof-Revision-Hard-v1`은 현재 저장소의 등록·구현에서 발견되지 않았다. 설명에 해당하는 실제 구현은 `Inspire-Sweep-Prof-Revision-v1`의 `formation_mode='distance_angle_sum'`이다. 해당 함수만 재사용한다고 사용자에게 알리고 진행했다. `ProfRevisionV1EnvCfg` 또는 `ProfRevisionV1RewardsCfg`를 상속하지 않는다. 요청하지 않은 가중치 조정을 피하여 부모 weight0.245를 보존하며, v1의0.3675는 가져오지 않는다.

## 변경 전후

| 항목 | 부모 v0_3 | 자식 v0_3_1 |
| --- | --- | --- |
| 직접 부모 | `ProfRevisionEnvCfg` | `ProfRevisionV0_3EnvCfg` |
| Formation raw | 거리 합에 대한 단일 비율 | 손가락별 거리 점수 × 양방향 각도 정렬 점수의 합 |
| Formation mode | 없음 | `distance_angle_sum` |
| Formation weight | 0.245 | 0.245 보존 |
| 거리 scale | 0.05m | 보존 |
| 관절 종료 사건 비용 | 없음 | 추가 없음 |
| 속도 margin 비용 | 없음 | 추가 없음 |
| TCP 종료 | `wrist_3_link` 선속도 >=4m/s | 전체 상속 |
| Scene·reset | 원통 타겟·장애물0–6개·목표6–12cm | 전체 상속. Hard 설정 미도입 |
| PPO | v0_3 설정 | experiment name만 `inspire_sweep_prof_revision_v0_3_1` |

## 보상식과 영향

현재 물리 타겟에 부착해 추적하는 초기 가시 OBB와 손끝 pad 원점 사이의 외부 최단 3D 거리를 `d_i`로 사용한다. OBB 내부·표면은 거리0이다. pad의 +Z normal과 pad에서 추적 OBB 중심으로 향하는 단위 방향 사이 내적의 제곱을 곱한다. EEF/월드 좌표계 어느 쪽에서 계산해도 같은 full3D 정렬이며, 양면이 모두 유효하다.

```math
r_{\mathrm{old}} = \frac{0.05}{0.05 + \sum_{i=1}^{5} d_i}
```

```math
r_{\mathrm{new}} = \sum_{i=1}^{5}
\frac{0.05}{0.05+d_i}
\left(\hat{\mathbf{n}}_i \cdot \hat{\mathbf{u}}_i\right)^2
```

```math
\Delta R_{\mathrm{formation}} = 0.245\,r_{\mathrm{new}}\,\Delta t,
\qquad \Delta t = 0.02\,\mathrm{s}
```

평균화하지 않는다. 정렬은0/45/90/180도에서1/0.5/0/1이고, 길이1e-8 이하 normal/방향은 정렬0으로 처리한다. 거리0의5개 손가락이 모두 정렬됐을 때 raw 최대5·step 최대0.0245다. 부모 raw 최대1·step 최대0.0049와 다르다. weight를 유지해도 per-finger 합산으로 출력 범위가 달라지므로 보상 크기가 동일하다는 의미는 아니다. 임의 정규화·재가중은 하지 않았다.

## 파일과 전체 대조

- [EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/prof_revision_envs.py): `ProfRevisionV0_3_1EnvCfg(ProfRevisionV0_3EnvCfg)`에 mode1개만 선언했다. RewardsCfg override 없음.
- [PPOCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/agent/prof_revision_ppo_cfg.py): `ProfRevisionV0_3_1PPORunnerCfg(ProfRevisionV0_3PPORunnerCfg)`, experiment name만 분리했다.
- [등록](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/__init__.py): 동일 runtime `runtime.prof_revision:ProfRevisionEnv`로 새 ID를 추가했다.
- [기존 live checker](../../../../src/inspire_sweep_baseline/scripts/check_prof_revision.py)에 새 task와 각도식·weight0.245 검증을 추가했다. 별도 버전 디렉토리·새 MDP 알고리즘은 만들지 않았다.

작업 전 EnvCfg/PPO/등록과 geometry/rewards 해시를 [before](../../../../outputs/prof_revision_v0_3_1_validation/before)에 저장했다. 기존 모든 클래스 정의의 AST, 기존 등록 전체, 공유 geometry/rewards 바이트 해시가 보존됨을 [source_audit.json](../../../../outputs/prof_revision_v0_3_1_validation/source_audit.json)으로 확인했다. 앞서 구현한 Hard 환경 및 이전 사용자 작업은 유지한다.

실제 configclass 대조는 자식 `formation_mode`만 제거했을 때 부모의 전체 `to_dict()`와 정확히 일치한다. 작업 직전 부모 소스를 별도 모듈로 실행해 현재 부모와의 전체 설정 일치도 확인했다. Scene·Command·Event/reset·Observation·Action·모든 Reward의 순서/함수/params/weight·Termination·빈 Curriculum·physics·actuator·sensor·runtime은 동일하다. PPO 전체 설정은 experiment name 외 차이가 없다. 보상16개를 유지하며 기존 v0_3의 팔 관절 속도 L2 비용은 보존한다. v1의 추가 `arm_joint_failure` 및 v0_2의 `arm_joint_velocity_margin`은 없다.

## 실행 검증

Windows11·RTX4070·Isaac Sim5.1 headless와 `env_isaaclab` Python에서 실행했다. 기존 `logs/rsl_rl`에는 쓰지 않고 [검증 폴더](../../../../outputs/prof_revision_v0_3_1_validation)에 결과를 저장한다.

- 기존 관련 검사32개 통과: 거리·각도 경계, 양방향 normal, 손가락별 pairing, degenerate 방향, frame 불변, 실제 geometry 갱신·부분 reset, 기존 보상/모델/PPO gradient/checkpoint/export 검사. [pytest.log](../../../../outputs/prof_revision_v0_3_1_validation/pytest.log).
- 새 환경4개·12 policy step, 부분 reset·강제 자동 timeout·고정 Actor snapshot/실시간 추적 OBB·JIT export 통과. 매 step 월드 기준 pad normal과 현재 중심 방향으로 거리·각도식을 다시 계산해 runtime Formation과 대조했고 실제 RewardManager rate가0.245×raw임을 확인했다. 추가 관절 사건·margin term 부재, 기존 TCP4m/s 경계와 성공 제외 조건도 확인했다. [smoke.json](../../../../outputs/prof_revision_v0_3_1_validation/smoke.json).
- 변경 전 부모 전체 설정 일치, 자식의 mode 단일 차이, 전체 PPO 대조와 모든 기존 소스 정의·등록 보존을 통과했다.
- 부모 v0_3의 기존4환경·12step live 검사도 다시 통과했다. [parent_smoke.json](../../../../outputs/prof_revision_v0_3_1_validation/parent_smoke.json).
- `train.py`로16환경 PPO1회 업데이트와 checkpoint 저장을 통과했다. 출력은 검증 폴더의 `ppo_smoke`이며 기존 학습 로그와 분리했다. checkpoint tensor132개 모두 유한, optimizer step32를 확인했다. [검사 결과](../../../../outputs/prof_revision_v0_3_1_validation/ppo_checkpoint_check.json).

검증 학습 명령은 다음과 같다. `--resilient-attempt-dir`는 기존 train.py의 출력 경로 분리 기능이며, 아래1회 검사는 장기 학습이 아니다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3_1 --num_envs 16 --headless --max_iterations 1 --resilient-attempt-dir outputs/prof_revision_v0_3_1_validation/ppo_smoke --resilient-target-iterations 1
```

장기 학습 성공률·손가락 자세의 실제 개선은 미검증이다. 현재 변경은 보상식을 재사용하며, 앞선 Play 분석에서 보고한 F/T 물리적 충실도 문제를 해결하지 않는다.

## 실행 명령

프로젝트 루트에서 Isaac Lab 환경을 활성화하고 실행한다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3_1 --num_envs 2048 --headless
python src/inspire_sweep_baseline/scripts/check_prof_revision.py --task Inspire-Sweep-Prof-Revision-v0_3_1 --headless --num-envs 4 --output outputs/prof_revision_v0_3_1_validation/smoke.json
```
