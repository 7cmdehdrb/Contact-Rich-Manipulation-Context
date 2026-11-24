# Prof Revision v1 개발 명세 작성

작성일: 2026-11-24. 상태: **명세 작성만 완료, 환경 미구현**.

## 요청과 근거

사용자는 Prof Revision v0 직접 자식 v1의 개발 명세를 요청했다. 기존 Single Contact v1에 존재하는 `arm_joint_failure`를 적용하고, 손가락별 거리 점수와 각도 유사도의 곱을 합산하며 Formation weight를 기존 대비 1.5배로 정하도록 지시했다. 각도 유사도는 직전 합의한 코사인 제곱으로 0°/180° 최대·±90° 최소다.

기준 workspace commit `19cac187345419cc08be097d7148052ddf3e383b`, 문서 commit `33858ea1086f22f1154eb799d934475af5de589f`. 기존 사용자 변경 `docs/SSH.md`, submodule 상태 및 앞선 종료 진단 문서 두 개를 보존했다.

## 변경 전후와 영향

- [개발 명세](../../01_plan/environments/2026-11-24_PROF_REVISION_V1_SPEC.md)를 새로 작성하고 현재 인계·활성 환경 안내에 미구현 계획 링크를 추가했다.
- 팔 종료 비용은 실제 기존 함수와 Cfg를 읽어 일회 −3.0·dt 상쇄·기존 종료 boolean 재사용으로 확정했다.
- 손가락 항은 `sum(0.05/(0.05+d_i) * cos(theta_i)^2)`, weight0.3675로 확정했다. 좌표계·패드별 방향 원점·현재 추적 OBB·정규화·퇴화 벡터 처리·reset/telemetry 계약을 명시했다.
- 합산 raw 최대5이므로 전체 최대 보상률은 기존의7.5배임을 명시했다. 사용자 지시 없이 평균화·재조정하지 않았다.
- 부모는 Reach5cm 변형이 아닌 Prof Revision v0이며 Reach10cm·면 선호·관측·물리·PPO를 보존한다. 실제 코드·등록·학습 로그는 변경하지 않았다.

## 최종 대조와 검증

실제 부모 EnvCfg/runtime/geometry/reward/termination/PPO와 Single Contact v1 사건 비용을 읽어 명세와 대조했다. 개발 지침·파일 구조·문서 규칙을 확인했다. 변경 범위는 명세·작성 로그·미구현 계획 링크이며, 소스 구현이 없으므로 실제 부모→v1 설정 동등성은 향후 구현의 수용 검사로 남겼다.

문서 검사 명령:

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  01_plan/environments/2026-11-24_PROF_REVISION_V1_SPEC.md \
  02_implementation/logs/2026-11-24_prof_revision_v1_spec.md \
  01_plan/00_HANDOFF_BRIEF.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md
python 00_guidelines/scripts/check_document_links.py --check-external \
  01_plan/environments/2026-11-24_PROF_REVISION_V1_SPEC.md \
  02_implementation/logs/2026-11-24_prof_revision_v1_spec.md \
  01_plan/00_HANDOFF_BRIEF.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md
git diff --check
```

검증 결과: 변경 Markdown4개 수식 검사 통과, 링크 검사 오류0개(외부10·내부383), workspace와 문서 저장소의 `git diff --check` 통과. `git diff -- src/inspire_sweep_baseline` 출력이 없어 활성 소스 변경이 없음을 확인했다. 문서 변경만 검사했으며 실제 Markdown 렌더링·GPU·Isaac Sim·PPO·학습은 미실행이다. 행동 개선·성공률·보상 비중은 미검증이다.

## 후속 구현

같은 날 별도 구현 요청으로 환경 구현·등록·단기 검증을 수행했다. 위 내용은 명세 작성 당시의 기록이며, 현재 상태는 [구현·검증 기록](2026-11-24_prof_revision_v1_implementation.md)을 따른다.
