# 물체 스폰 영역 시각화 전체 삭제

2026-11-11 사용자 요청: 베이스 환경에 있는 물체 스폰 영역 가시화는 의미가 없어 관련 코드를 모두 삭제한다. 새 환경을 추가하지 않고 현재 활성 패키지의 해당 기능을 직접 제거했다. 작업 시작 시 앞선 Semi-Prof 구현 변경과 사용자 `docs/plan/PLAN15.md` 변경이 있었으며 보존했다.

## 변경 전후·범위

기존에는 `play.py`가 `debug_spawn_regions=True`로 설정하고, reset 시 최초4개 환경의 RED/WHITE·장애물 점유 영역을 비물리 marker로 표시했다. `train.py`는 이 설정을False로 강제했다. 독립 Simple 베이스와 과거 Relative-IK v0_2_2_4 런타임에 같은 표시 코드가 각각 있었다.

다음 표시 전용 구성은 모두 삭제했다.

- 두 runtime의 `_update_spawn_regions`와 reset 호출, marker·표시용 위치/색상 버퍼 생성.
- 두 EnvCfg의 `debug_spawn_regions`, `debug_spawn_max_envs`.
- 공용 `spawn_region_classes` 표시 분류 함수.
- train/play의 표시 활성화·비활성화 분기.
- 삭제된 표시 전용 테스트2개와 기존 config 비교/fixture의 표시 옵션.

Simple-v0와 그 파생 Simple/Prof/Hard/Finger/Semi-Prof 전체, Relative-IK v0_2_2_4와 그 파생 환경에 적용된다. 기존 Gym ID·상속 관계는 유지한다. 실제 `CircleResetLayout`의 RED/WHITE 배치 판정·간격·난수·셀 캐시, Warp IK, 보상·관측·액션·종료·커리큘럼·PPO는 변경하지 않는다. 목표/EEF 프레임·타겟 BBOX·로봇 초기 IK 박스는 물체 스폰 영역 표시와 별개라 보존한다.

## 검증·최종 대조

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple_semi_prof.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger_versions.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_fast_reset.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  -q -p no:cacheprovider
```

결과 **106개 통과·2개 skip**. 기존 전체 설정·부모 관계 대조, reset 및 timeout 통계, 실제 배치 기하·보상·Semi-Prof 회귀를 포함한다. 표시만 검증하던 테스트2개는 기능과 함께 제거했으며 새 테스트는 추가하지 않았다. source에서 표시 설정·함수·버퍼 이름을 검색해 남은 참조가 없음을 확인했다. 실제 배치 클래스의 AST도 HEAD와 동일함을 확인했다.

수정 source 범위와 문서 저장소 whitespace, 변경 문서의 수식·링크를 검사했다. 이전 개발 로그의 당시 구현 설명은 역사 기록으로 보존하고, 현재 환경 설명서·README·인계·활성 환경 안내에는 삭제 사실을 반영했다. native GPU/PhysX·play 렌더링은 드라이버 연결 불가로 실행하지 않았다. 이번 작업은 학습 로그를 수정하지 않는다.
