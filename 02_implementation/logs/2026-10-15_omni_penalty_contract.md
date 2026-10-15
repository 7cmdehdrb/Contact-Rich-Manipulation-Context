# Omni 공통 Action Rate·Velocity 페널티 계약

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [필수 개발 지침](../../00_guidelines/09_DEVELOPMENT_GUIDE.md)

## 요청과 기준

2026-10-15 사용자 요청: Omni 베이스 및 모든 파생 환경의 Action Rate·Velocity를 참고 Inspire와 같은 제곱합으로 통일한다. Hand 항은 별도로 유지하며 참고 환경 함수를 import하지 않는다. 앞으로도 해당 페널티를 반드시 사용하도록 지침에 명시한다.

기준은 루트 main `58055ab`, 문서 main `5cdb281`, 참고 Sweep-Policy `baa3740`이다. 시작 시 사용자 작업 파일에 Omni v1의 속도 종료 임계값 3→5 rad/s 변경이 있었고 이를 보존했다. 미추적 `src/Universal_Robots_ROS2_Description/`도 수정하지 않았다.

## 최종 구현

활성 패키지 `mdp/goal_rewards.py`에 `action_rate_l2`와 `joint_vel_l2`를 새로 정의했다. 전자는 Arm 6D/Hand 2D raw 명령 변화량을 각각 제곱합한다. Hand 보상 입력 clamp를 하지 않는다. 후자는 이름으로 선택한 Arm 6개/Hand 12개 실제 관절 속도를 각각 제곱합한다. 평균·기준값 정규화·함수 내부 dt 처리는 없다. RewardManager가 weight와 step_dt를 한 번 곱한다.

`OmniRewardsCfg`의 Arm Action/Velocity weight는 −0.03/−0.03, Hand Action/Velocity는 −0.03/−0.01로 유지한다. 기존 Arm 수치는 동일하며, Hand Action은 범위 내 같은 변화에 대해 이전 평균 대비 2배, Hand Velocity는 이전 평균 대비 12배가 된다. 범위 밖 raw Hand 변화도 이제 비용에 포함된다. 기존 normalized 함수는 과거 저장 설정 참조를 위해 보존하지만 활성 Omni 설정에서는 사용하지 않는다.

적용 환경은 `Isaac-Inspire-Sweep-Omni-v0/v1/v2/v3` 및 `Isaac-Inspire-Dex-Omni-v0`이다. 보상 상속은 `OmniRewardsCfg → OmniV2RewardsCfg → DexOmniRewardsCfg`, 환경 상속은 `InspireSweepOmniEnvCfg → V1 → V2 → V3/Dex`를 유지한다. Gym 등록, runtime `InspireSweepEnv`, PPO runner, train/play 명령은 기존 활성 환경 안내와 같다. Reaching·Goal·종료·제어 설정은 이번 변경 대상이 아니다. CPU 검증은 실제 속도 종료 현상의 해결을 입증하지 않는다.

루트 AGENTS와 개발 지침에 필수 사용 함수·계산식·그룹·계수를 명시했다. 향후 파생에도 적용하며 사용자 명시 지시 없이 구조·계수를 바꾸거나 제거하지 않는다.

## 실행 검증

저장소 루트에서 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests
```

결과: **185 passed in 6.44s**. 새 검증은 raw Hand 범위 밖 변화, Arm/Hand 분리와 전체 Action 제곱합 일치, 비연속 관절 선택, 모든 Omni 파생의 함수·계수·매개변수 상속을 포함한다. 기존 Dex 검사 중 3 rad/s를 고정했던 단언은 부모 v2와 동일함을 검사하도록 바꿔 사용자 임계값 변경을 보존했다.

변경한 Markdown 8개에 `check_markdown_math.py` 실행: 8개 통과. 같은 8개에 `check_document_links.py --root example/Contact-Rich-Manipulation-Context --check-external` 실행: 오류 0, 내부 링크 104개·workspace 링크 37개 확인. 루트·문서 저장소의 `git diff --check`도 통과했다.

시뮬레이터 학습·play·물리 접촉 및 종료율 재측정은 실행하지 않았다. 기존 checkpoint의 성능 개선이나 Hand Velocity 종료 해결은 미검증이다. 이번 변경의 commit/push는 수행하지 않았다.
