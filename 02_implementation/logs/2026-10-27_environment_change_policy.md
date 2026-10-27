# 환경 수정 범위와 구성 보존 공통 지침

[개발 로그 목록](README.md) · [개발 지침](../../00_guidelines/09_DEVELOPMENT_GUIDE.md) · [환경 파일 구조](../../00_guidelines/12_ENVIRONMENT_FILE_STRUCTURE.md)

2026-10-27 사용자 요청으로 공통 작업 규칙을 강화했다. 목적은 파생 환경을 만들거나 함수를 정리하는 과정에서 요청하지 않은 구성·동작 변경이 섞이는 일을 막고, 후속 에이전트가 변경 의도를 추적할 수 있게 하는 것이다. 이번 작업 대상은 지침과 기록 문서이며, 실행 코드나 PLAN7은 수정하지 않았다. 작업 시작 전에 있던 GoalAccuracy 코드·문서 수정은 보존했다.

| 이전 지침의 부족한 점 | 반영 내용과 의도 |
| --- | --- |
| 구조 문서에 이관 절차가 있어 일반 기능 수정 중에도 함수 이동을 허용하는 것으로 읽힐 수 있음 | 현재 패키지 디렉토리 구조를 유지하고, 이동·재구성은 명시적인 구조 변경 요청에만 적용 |
| 부모·자식 대조 위주여서 기존 버전 직접 수정 요청의 처리 기준이 부족함 | 직접 수정은 해당 환경의 수정 전·후를 비교하고, 새 파생 환경은 지정 부모 상속과 부모의 작업 전·후 보존을 확인 |
| 함수 재사용 과정의 보상 구성 변경을 충분히 구체화하지 않음 | 요청하지 않은 보상 함수·term·계수·순서와 다른 Manager 구성을 보존. import·기본 인자·reset/cache·dt 변경도 비교 대상에 포함 |
| 최종 비교에서 커리큘럼 세부 항목이 빠질 수 있음 | 모든 Manager·등록·runtime·PPO를 대조하고 커리큘럼 활성 여부·대상·점·간격까지 요청과 대응 |
| 로그의 대상 독자와 수정별 의도 기록이 불분명함 | 에이전트·개발자 인계를 위한 변경 의도·근거·영향·검증 기록을 매 수정에 남기도록 명시 |

목표 도달 기준 `d <= r`와 가변 반경 허용 규칙은 유지했다. 공통 지침의 기존 OOP 문장도 임의의 구성요소 재조합을 허용하지 않도록 맞췄다. 수정한 지침 사이에 직접 수정·부모 보존·구조 이관의 적용 범위가 충돌하지 않는지 대조했다.

문서 저장소에서 실행한 검증:

```bash
python 00_guidelines/scripts/check_markdown_math.py 00_guidelines/09_DEVELOPMENT_GUIDE.md 00_guidelines/12_ENVIRONMENT_FILE_STRUCTURE.md 02_implementation/logs/2026-10-27_environment_change_policy.md 02_implementation/logs/README.md
python 00_guidelines/scripts/check_document_links.py
git diff --check
```

결과는 수식 검사 4개 파일 통과, 내부 링크 오류 0개, diff 공백 검사 통과다. 문서 지침 변경이므로 환경 테스트와 GPU 실행은 수행하지 않았다.

후속 요청으로 workspace 루트 `AGENTS.md`도 개정했다. 에이전트 진입점에서 직접 수정·파생 생성 구분, 부모 보존, 현재 구조 유지, 요청 범위 제한, `d <= r`, 전체 비교와 인계용 로그 의무를 바로 확인하도록 요약했다. 상세 절차는 기존 개발·파일 구조 지침으로 연결하며, 함수 이동을 일반 작업으로 허용하는 것처럼 보이던 포인터 문구를 수정했다.

후속 검증: 문서 저장소에서 `python 00_guidelines/scripts/check_markdown_math.py ../../AGENTS.md 02_implementation/logs/2026-10-27_environment_change_policy.md`로 2개 파일 통과, 양쪽 저장소에서 `git diff --check` 통과. Python의 `Path.is_file()`로 루트 `AGENTS.md`의 상대 링크 7개가 가리키는 파일이 모두 존재함을 확인했다.
