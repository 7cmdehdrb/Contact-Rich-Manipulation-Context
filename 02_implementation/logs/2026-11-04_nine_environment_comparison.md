# 9개 Holding·Final·Revision 환경 비교 문서 작성

## 요청·기준

사용자가 지정한 9개 experiment를 씬 구성·관측·보상·커리큘럼·터미네이션·기타로 비교하고 최종 요약 표를 요청했다. [비교 문서](../environments/HOLDING_FINAL_REVISION_NINE_ENV_COMPARISON.md)를 추가했다. 환경 수정이나 새 환경 생성 작업이 아니다.

기준 workspace commit은 `ba1aa88bf462c5263531379b0a67248ad2439552`다. 시작 시 문서 submodule의 2026-11-04 로그 분류 관련 untracked 6개 파일을 보존했다. 실행 코드와 `logs/rsl_rl`은 변경하지 않았다.

## 의도·전후·영향·최종 대조

기존에는 요청한 정확한 9개 버전을 같은 항목으로 비교하는 문서가 없었다. EnvCfg 직접 부모, 실제 manager 설정·계산 함수·PPO 등록을 대조하여 상세6개 항목과 최종9행 표를 추가했다. 기존 개별 명세와 과거 실행 결과는 수정하지 않았다.

O2의 OSC-v3 상속, F2 배치 차이, A1의 현재 Reaching10cm와 cube variant만 변경하는 구성, Accuracy 장애물4/5 상한, A2의 strict 만료 보너스, Revision의 독립 구성·현재 장애물 Critic, Test-v1의 Revision-v1 상속 변경·120mm 접촉 제한·strict Hold/진입을 명시했다. 물리 생성 수·요청 수·실제 수·관측 슬롯, 초기 관측·현재 GT, 보상률·사건 보상, 누적 Hold 지급·연속 성공 체류시간을 구분했다.

## 검증과 미검증

등록·EnvCfg·Scene/Event·Observation·Reward·Curriculum·Termination·PPO/runtime을 읽고 정적으로 대조했다. 첫 문서 검사 호출은 작업 디렉터리에 중복 상대 경로를 붙여 로그 파일 생성에 실패했다. 경로를 정정한 뒤 아래 검사를 수행했다. 결과는 아래 후속 기록에 남긴다.

```bash
python 00_guidelines/scripts/check_markdown_math.py 02_implementation/environments/HOLDING_FINAL_REVISION_NINE_ENV_COMPARISON.md 02_implementation/logs/2026-11-04_nine_environment_comparison.md
python 00_guidelines/scripts/check_document_links.py
python 00_guidelines/scripts/check_document_links.py --check-external 02_implementation/environments/HOLDING_FINAL_REVISION_NINE_ENV_COMPARISON.md 02_implementation/logs/2026-11-04_nine_environment_comparison.md
git diff --check
```

GPU 시뮬레이션·학습·checkpoint 호환성 실행·성능 순위・각 run의 과거 override 복원·Markdown 화면 렌더링은 미검증이다. 정적 코드 계약 비교를 물리 동작이나 장기 성공률 검증으로 취급하지 않는다.

## 검사 결과

수식 검사2개 파일 통과. 전체 문서 링크 검사460개 문서에서 오류0, 신규 두 문서의 외부 코드 링크 포함 검사에서 오류0을 확인했다. workspace와 문서 저장소 `git diff --check`도 통과했다. 최종 검색성을 위해 활성 환경 안내에 비교 문서 링크를 추가했으며 추가 후 변경3개 문서를 재검사했다.
