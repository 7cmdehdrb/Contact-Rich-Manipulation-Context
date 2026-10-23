# 2026-10-23 ObjectRandom-v1 장애물 개수 커리큘럼

[개발 로그](README.md) · [환경 계약·실행](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V1_ENVIRONMENT.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

## 요청과 기준

사용자 요청: `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v1`에 부모와 같은 초기 Gray1/White1 및 1,500 iteration 교대 증가를 사용하되 상한을 Gray8/White8로 확장한다. 기존 자식의 고정7/7 스폰은 해제한다.

기준 workspace commit: `56c26e0ae28f58e4546a7c142d35d24eb75943b2`. 문서 submodule: `7be0afbdd069003ea4ee1faf6c54954c20847605`. 작업 시작 시 두 작업트리는 깨끗했다. 사용자가 적용한 OSC 관성 분리·중력 보상true, 위치/회전 stiffness100/50은 그대로 보존했다.

## 구현과 계약

EnvCfg 직접 부모는 `FusionHoldingOSCV2EnvCfg`, runtime은 `ContactSweepClutterFusionV1_0Env`, PPO는 `FusionHoldingOSCObjectRandomV1PPORunnerCfg`, runner는 `CurriculumOnPolicyRunner`로 유지한다.

`ObjectRandomV1CurriculumCfg`는 부모의 `obstacle_population`을 복사하고 `final_gray=8`, `final_white=8`만 변경한다. 초기1/1, White 시작3,000, Gray 시작4,500, 각 색상 간격3,000은 부모 값이다. EnvCfg 최대 용량은8/8이며 자식의 초기 개수 강제 설정을 제거하여 부모의1/1 초기 reset을 사용한다.

| Iteration | Gray | White |
| --- | --- | --- |
| 0~2,999 | 1 | 1 |
| 3,000 | 1 | 2 |
| 4,500 | 2 | 2 |
| 6,000 | 2 | 3 |
| 7,500 | 3 | 3 |
| 21,000 | 7 | 8 |
| 22,500 이후 | 8 | 8 |

물리 용량은 타겟1+장애물16=17개, 관측은 기존16슬롯64D다. Actor/Critic 원시119D/122D·encoder64→32→16·Action8D·보상·성공·목표 반경 커리큘럼·자산·물성·OBB 배치 검사는 유지한다. 비활성 물체 주차/중력 mask와 진행 중 episode 개수 보존도 부모 구현을 따른다. 증가한 개수는 다음 reset에 반영된다. checkpoint load/rewind는 절대 iteration으로 복원한다.

## 실제 검증

Workspace 루트에서 실행:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_fusion_holding_osc.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v1.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_population.py \
  src/inspire_sweep_baseline/tests/test_object_random_geometry.py
```

최종 결과: **60 passed, 1 warning**,3.89초. warning은 기존 ONNX export deprecation이다. 첫 실행에서는59 passed/1 failed였으며, 실패는 기존 OSC 테스트가 사용자 변경 전 stiffness80/25·중력 보상false를 기대했기 때문이다. 제어 코드를 변경하지 않고 테스트 기대값을 현재100/50·중력 보상true·관성 분리true로 갱신한 뒤 통과했다.

검증은 실제 개수 schedule의 모든 증가 시점·직전/직후·최종 상한·되감기,16슬롯 Gray/White mask, 초기1/1 설정, 기존 모델/PPO/export와 슬롯 용량, 부분 reset, 물체 형상 기하를 포함한다. GPU probe의 설정 기대값도8/8 커리큘럼으로 갱신했다.

`nvidia-smi -L`은 NVIDIA driver 통신 실패였다. GPU Scene 생성·물리 step·16개 랜덤 자산의 실제 OBB 배치 성공률·메모리·장기 학습은 미검증이다. CPU 용량 검사는 모든 랜덤 형상 조합의 배치 가능성을 증명하지 않는다. 기존 배치 실패 시 오류 처리와 목표 고정은 유지한다.

실행 명령과 자산 조건은 [환경 계약](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V1_ENVIRONMENT.md)을 따른다. 학습 로그를 정리하거나 수정하지 않았고 학습도 시작하지 않았다.

정적 검증: 변경 Python3개 AST 구문 검사, 변경 Markdown9개 `check_markdown_math.py`, 상대 파일 링크 검사(누락0), 두 저장소의 `git diff --check`를 통과했다.
