# Fusion v1_0 독립 환경 설명·버전 비교 정리

[개발 로그 목록](README.md) · [독립 환경 설명](../environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_0_ENVIRONMENT.md) · [버전 비교](../environments/CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md)

기준일: 2026-10-22. Workspace HEAD `a2fcb0b77a234a14db8b6fc9c91cfef4c4229092`의 작업트리에 있는 현재 구현을 읽고 문서화했다. 기존 미커밋 코드·문서 변경을 보존했으며 이번 작업은 실행 코드·학습 설정을 바꾸지 않는다.

사용자가 지정한 환경 설명서의 Scene·Observation·Action·Reward·Termination·Curriculum 구조를 참고하여 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-v1_0`만 설명하는 문서를 작성했다. 다른 버전의 설정을 알아야 이해할 수 있는 비교나 상속 설명을 본문에 넣지 않고, 실제 최종 구성·수식·수치·frame·단위·예외·학습 실행을 명시했다.

버전 비교 문서는 v0 → v2 → v3 → v1_0의 Env/PPO 상속, 활성 항 수, 촉각/손 전체 접촉, Goal 반경, deadzone, 운동 네 항, 장애물 개수, wrench 크기 변화, PhysX 가속도 및 자동 복구 차이를 정리했다. Wrench는 모멘트 기준점이 EEF로 새로 이동한 것이 아니라 표본 축과 변화량 정의가 달라진 것으로 확인했다. 현재 코드의 pushing_speed weight는 v3·v1_0 모두−5이므로 변경점으로 기록하지 않았다.

문서 색인과 활성 환경 안내에서 새 설명서로 연결했다. AST로 실제 CFG의 활성 보상17·종료6·커리큘럼9개를 확인하고 보상·종료 이름이 새 문서에 모두 존재하는지 검사했다. 독립 설명서에 다른 버전 ID·부모 환경 비교가 없음을 텍스트 검사와 본문 검토로 확인했다.

문서 저장소 루트에서 실행한 검사는 다음과 같다.

```bash
python 00_guidelines/scripts/check_markdown_math.py \
  02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_0_ENVIRONMENT.md \
  02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md \
  02_implementation/README.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-22_clutter_fusion_v1_0_documentation.md
python 00_guidelines/scripts/check_document_links.py --check-external \
  02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_0_ENVIRONMENT.md \
  02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_VERSIONS.md \
  02_implementation/README.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md \
  02_implementation/logs/README.md \
  02_implementation/logs/2026-10-22_clutter_fusion_v1_0_documentation.md
git diff --check
```

검사 결과: Markdown 수식6개 파일 통과, 내부 링크181개·workspace 외부 파일 링크50개 검사 오류0, `git diff --check` 통과.

이번 문서 작업에서 학습·GPU simulation을 새로 실행하지 않았다. 설명서에 적은 CPU543개와 GPU 검증은 연결된 앞선 개발 기록의 결과이며, 보상 예시는 수식 계산값이다. 장기 정책 성능이나 실물 동작의 검증으로 해석하지 않는다.

## 보상 비중의 설계 의도 추가

2026-10-22 후속 요청으로 독립 설명서4.9절에 양의 보상 기준 목표 이동 약60%, 목표 유지 약20%, 접근 약10–15%, 접촉 약5–10%의 설명용 비중을 추가했다. 현재 계수와 정상 조작 예시를 요약한 대략적 의도이며 실측값·강제 배분율이 아님을 명시했다. 페널티는 별도의 고정 비중 없이 역할로 설명하고 wrench의 실제5% 예산 제한과 구분했다. 보상 코드·weight는 변경하지 않았다.

독립 설명서에 `check_markdown_math.py`와 `check_document_links.py --check-external`을 실행해 수식 검사 통과·링크 오류0을 확인했고 `git diff --check`도 통과했다. 문서 변경만 수행했으므로 학습·물리 테스트는 재실행하지 않았다.
