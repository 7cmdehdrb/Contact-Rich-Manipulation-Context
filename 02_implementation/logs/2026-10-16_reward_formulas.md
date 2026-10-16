# 접근·목표 진행 보상 4종 수식 문서화

[개발 로그 목록](README.md) · [보상 수식 문서](../environments/REACH_AND_GOAL_REWARD_FORMULAS.md) · [구현 문서 안내](../README.md)

기준일: 2026-10-16. Workspace commit은 `301099db55cea61b7a715fcd8bf0b46d357214b2`, 문서 저장소 commit은 `92fcd2203c20ec47638474ea2085dd8a8a3d02b3`다. 작업 시작 시 상위 저장소의 문서 submodule 참조 차이가 있었고 문서 저장소 작업트리는 깨끗했다.

## 작성 범위

사용자가 지정한 `HeightGatedPlanarReachProgress`, `PlanarGoalProgress`, `DexReachProgress`, `DexPlanarGoalProgress`의 현재 계산식을 별도 문서로 작성했다. 변수·reset·상태 갱신·반경 및 허용 오차·높이 gate·초기 거리 정규화·시간 간격 상쇄·현재 Renewal 가중치·수치 예시를 정리하고 구현 색인에서 연결했다. 환경·보상 코드와 파라미터는 변경하지 않았다.

`HeightGatedPlanarReachProgress`는 최고 XY 기록에서 멀어진 동안 매 스텝 감점하며, 높이 밖의 새 기록도 저장한다. 다른 세 항은 새 최고 기록의 증가분만 지급한다. 이 차이는 구현과 기존 회귀 테스트를 기준으로 설명했다.

## 검증

Workspace 루트에서 실행:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_goal_rewards.py src/inspire_sweep_baseline/tests/test_dex_rewards.py
```

결과: **51 passed in 1.58s**. 현재 테스트를 재실행했으며 문서 전용 신규 테스트는 추가하지 않았다.

문서 저장소 루트에서 실행:

```bash
python 00_guidelines/scripts/check_markdown_math.py 02_implementation/environments/REACH_AND_GOAL_REWARD_FORMULAS.md 02_implementation/README.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-16_reward_formulas.md
python 00_guidelines/scripts/check_document_links.py --check-external
git diff --check
```

수식 검사: 변경한 Markdown 4개 통과. `git diff --check` 통과. 전체 링크 검사는 이번 작업 이전 문서 `2026-10-15_dex_omni_rewards.md` 12행의 DexTouch PDF 누락 링크 1건으로 실패했다. 해당 기존 문서는 수정하지 않았다. 이번 변경 파일만 아래 명령으로 재검사한 결과 내부 링크 77개·workspace 링크 7개, 오류 0건이다.

```bash
python 00_guidelines/scripts/check_document_links.py --check-external 02_implementation/environments/REACH_AND_GOAL_REWARD_FORMULAS.md 02_implementation/README.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-16_reward_formulas.md
```

최초 로그 작성은 작업 디렉터리에 중복 상대경로를 사용해 실패했고, 로그 경로를 바로잡은 뒤 재검사했다.

미검증: Isaac Sim 학습·재생과 실물 성능, GitHub 웹 수식 렌더링. CPU 테스트는 수식에 대응하는 로직의 검증이며 정책 성능을 입증하지 않는다.
