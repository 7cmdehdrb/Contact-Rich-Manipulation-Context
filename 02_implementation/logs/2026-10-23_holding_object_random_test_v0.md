# 2026-10-23 Holding ObjectRandom Test v0

[개발 로그](README.md) · [환경 계약·train/play](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OBJECT_RANDOM_TEST_V0_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

## 요청과 기준

사용자는 OSC가 아직 불안정하므로 Holding-v2의 Joint Position 제어로 OSC-ObjectRandom-v1과 같은 복잡한 물체 환경을 학습할 수 있는지 검증할 별도 테스트 환경을 요청했다. 이번 작업은 환경 구현이며 장기 학습 결과는 아니다.

기준 workspace commit은 `56c26e0ae28f58e4546a7c142d35d24eb75943b2`, 문서 submodule은 `7be0afbdd069003ea4ee1faf6c54954c20847605`다. 이전 요청의 ObjectRandom-v1 개수8/8·테스트·문서 변경이 미커밋 상태였으며 이를 보존했다. 사용자가 변경한 OSC-v2 제어 설정도 수정하지 않았다.

## 구현 계약

- Task: `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-ObjectRandom-Test-v0`.
- EnvCfg: `FusionHoldingObjectRandomTestV0EnvCfg`는 `FusionHoldingV2EnvCfg`를 직접 상속한다. Runtime은 `ContactSweepClutterFusionV1_0Env`다.
- PPO: `FusionHoldingObjectRandomTestV0PPORunnerCfg`는 `FusionHoldingV2PPORunnerCfg`를 상속하며 experiment 이름만 `inspire_contact_sweep_clutter_fusion_holding_object_random_test_v0`로 분리한다.
- Scene/Event/Curriculum: OSC-ObjectRandom-v1과 같은 설정 클래스를 사용한다. 자산·크기·OBB 배치·reset 물성·Gray1/White1→Gray8/White8·16슬롯을 재사용한다.
- 제어: Holding-v2의 JointPositionActionCfg(scale0.5/default offset), Arm 관절 PD, Hand2D를 그대로 상속한다. OSC 환경의 post-init을 호출하지 않는다.
- 관측·보상·성공: Holding-v2와 같은 입력/encoder·공통 목표 반경·goal_hold4·손 접촉/목표 보상·0.01m/s/3초 성공·네 운동 페널티다. 상세 순서·차원·frame·실행은 [환경 계약](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OBJECT_RANDOM_TEST_V0_ENVIRONMENT.md)을 따른다.

## 실제 검증

Workspace 루트에서 실행:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_fusion_holding_osc.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v2.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v1.py \
  src/inspire_sweep_baseline/tests/test_object_random_geometry.py
```

최종 **45 passed, 1 warning**,4.34초. warning은 기존 ONNX export deprecation이다. 첫 실행44 passed/1 failed는 CPU 테스트의 `_AssetNode`에 없는 `to_dict()` 호출 때문이었다. 테스트 객체의 직접 비교로 수정 후 같은 명령을 통과했다. production 제어 코드 변경은 없었다.

새 환경을 기존 ObjectRandom 개수/Scene 계약 테스트에 함께 넣어8/8 용량·1/1 초기화·모든 증가 경계·상한·되감기·마스크를 확인했다. 직접 Holding-v2 상속, Joint Position 액션과 Arm actuator 보존, PPO 구조 보존·별도 experiment·Gym 등록도 검사했다. 기존 목표 반경·성공/접촉·16슬롯 모델/PPO/export·물체 기하 검사도 통과했다. CPU 테스트는 launcher 의존 자산을 대역으로 사용하며 실물리 실행을 대신하지 않는다.

`_fusion_holding_v1_probe.py`에는 실제 전체 Cfg 비교를 추가했다. Joint 테스트 환경과 OSC-ObjectRandom-v1은 Arm action과 Arm actuator를 제외하면 동일해야 하며, Joint 환경의 action/actuator는 Holding-v2와 같아야 한다. 이 GPU probe는 이번에 실행하지 않았다.

## 미검증

`nvidia-smi -L`은 NVIDIA driver와 통신하지 못했다. GPU Scene 생성·reset/step·PPO 학습·play·장기 성공률·16개 랜덤 물체의 배치 성공률과 처리량은 미검증이다. 따라서 Joint 제어에서 복잡한 환경을 학습할 수 있다는 결론은 아직 내리지 않는다. 다음 확인은 새 환경에서 짧은 GPU 실행 후 독립 학습이며, OSC checkpoint는 Action 의미가 달라 동일 정책 비교에 사용하지 않는다.

학습 실행은 `src/inspire_sweep_baseline/scripts/train.py`를 사용한다. 학습을 시작하거나 로그를 수정·정리하지 않았고 commit/push도 수행하지 않았다.

정적 검사: 이전 요청의 미커밋 변경을 포함한 Python7개 AST 구문 검사, Markdown11개 수식 검사·상대 파일 링크 검사(누락0), 상위/문서 저장소 `git diff --check`를 통과했다.
