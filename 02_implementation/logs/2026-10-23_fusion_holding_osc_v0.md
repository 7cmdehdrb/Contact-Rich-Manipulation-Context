# Fusion Holding OSC v0 — 2026-10-23

[개발 로그](README.md) · [환경 설명](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_V0_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

사용자 요청: Holding v0을 직접 상속하고 Arm Controller만 Joint Position에서 OSC로 바꾼다. 참조는 `Isaac-Inspire-Sweep-Omni-Renewal-OSC-v0`다. 기준 Workspace commit은 `95f75646c6c1d358b1e69dd77d8b456ef309ecc2`이며 기존 지침·Holding·문서 작업트리 변경은 보존했다.

등록 ID는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-v0`. `FusionHoldingOSCV0EnvCfg`는 `FusionHoldingV0EnvCfg`를 직접 상속한다. 기존 v1_0 runtime을 사용하고 새 PPOCfg는 Holding PPO의 experiment 이름만 분리한다. 별도 step/reset override는 없다.

참조와 동일한 `OperationalSpaceControllerActionCfg`: pose_rel, fixed impedance, motion stiffness200, damping ratio1, 관성 분리와 중력 보상, 위치·회전 scale1.0. Body/offset은 부모의 EEF FrameTransformer 설정을 그대로 사용한다. OSC effort와 implicit joint PD가 경쟁하지 않도록 Arm actuator stiffness/damping만0으로 변경한다. Hand와 보상·종료·커리큘럼·Scene 물성·관측 등은 유지한다. bounded OSC v2 설정은 적용하지 않았다.

## 실행 검증

```bash
env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B \
  outputs/fusion_holding_osc_v0_validation/smoke.py \
  > outputs/fusion_holding_osc_v0_validation/smoke.log 2>&1
```

결과: exit0, `HOLDING OSC SMOKE PASSED`. 실제 Isaac Lab에서 다음을 검사했다.

- 새 Cfg가 Holding Cfg의 subclass이고, Arm action 설정 전체가 참조 Renewal OSC와 일치한다.
- `to_dict()`로 환경 전체를 비교하여 Arm action과 두 Arm PD gain을 제외한 차이가 없다.
- Gym 등록 ID로 GPU2환경·seed42 생성, 총8D action 확인.
- 16step Arm0/Hand열림, 이후16step Arm X상대이동0.001m/Hand열림으로 총32제어step 실행.
- 보상·관절 위치·applied torque가 모두 finite이며 이 짧은 실행에서 종료 없음.

스크립트·로그·`result.json`은 `outputs/fusion_holding_osc_v0_validation/`에 보존했다. 이것은 제어 연결과 짧은 실행 확인이며 PPO update·장기 학습 수렴·다양한 접촉 상황 안정성·실물 검증은 수행하지 않았다. Joint Position과 OSC는 같은8D라도 Arm 출력 의미가 달라 기존 Joint Position checkpoint의 동등 재생을 보장하지 않는다.

## 문서와 실행 안내

상세 환경 문서, 환경 색인·계층도·등록 표, 부모 Holding의 파생 링크, 패키지 README를 갱신했다. Windows/Linux 학습은 `train.py`를 사용한다. 자동 복구 실행기는 사용하지 않는다.

변경 Markdown 8개에 `check_markdown_math.py` 및 `check_document_links.py --root .` 실행: 수식 검사 통과, 내부 링크448개·오류0. 두 저장소의 `git diff --check` 통과. 외부 URL2개와 브라우저 렌더링은 검증하지 않았다.

## EEF 로컬 명령으로 변경

후속 사용자 요청으로 Holding OSC v0의 명령 축을 base에서 현재 EEF로 변경했다. `EEFRelativeOSCAction`은 기존 OSC Action을 상속하고 `_compute_task_frame_pose`에서 body offset까지 적용된 `_ee_pose_b`를 clone한다. 부모 `process_actions`가 EEF pose를 먼저 갱신하므로 최신 정책 step pose가 기준이다. clone으로 substep 중 EEF buffer 갱신과 분리하여 목표가 계속 이동하는 것을 방지한다. 이동과 axis-angle 회전 모두 EEF 로컬 축이며 raw action은 그대로 보존한다. stiffness·scale·토크 설정·Hand·보상 등은 변경하지 않았다. 참조 Renewal OSC v0도 변경하지 않았다.

검증 명령:

```bash
env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1   /home/min/miniconda3/envs/env_isaaclab/bin/python -B   outputs/fusion_holding_osc_v0_validation/eef_smoke.py   > outputs/fusion_holding_osc_v0_validation/eef_smoke.log 2>&1
```

결과 exit0 및 EEF LOCAL OSC SMOKE PASSED. 실제 OSC Action/Controller에서 identity·Z90° EEF pose를 주입하여 로컬+X 1cm 목표가 각각 base+X·base+Y로 변환되는지 확인했다. 로컬X 회전0.1rad의 목표 quaternion이 `q_EEF × q_delta`인지, EEF buffer를 바꿔도 고정한 task frame이 바뀌지 않는지, raw action이 보존되는지 검사했다. 설정 비교에서는 Arm 외 환경 동일성을 확인하고 참조 Arm 설정도 class_type을 제외하면 동일함을 확인했다. 이후 실제 GPU2환경·32step에서 유한 보상·관절 상태·토크와 종료 없음 확인. 결과는 `outputs/fusion_holding_osc_v0_validation/eef_result.json`에 보존했다. 장기 학습·토크 상한 준수는 이번 검증 범위가 아니다.
