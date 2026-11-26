# Prof Revision 이동 방향 보상 재평가 기록

2026-11-26 KST. 요청: 힘 방향을 OBB 중심 이동 방향으로 교체할 경우 충분한 보상을 받는지 checkpoint 기반으로 검증.

## 의도와 변경

부모·현재 환경 변경 요청이 아닌 보상 대안 검증으로 해석했다. `v0_3_1/model_15550`의 직전 seed42·43 실제 Play512episode·254,165step을 사용해 같은 궤적에서 보상만 재계산했다. 새 Play·학습은 하지 않았다. 연구 판단을 위해 방향 교체만 수행한 안과 수평 힘1N 조건을 제거한 안을 분리했다.

새 `scripts/report_prof_revision_motion_alignment.py`가 원본·XY/3D이동·힘 조건 유지·1/5mm/s cutoff·전/중간/후 목표 벡터·각도 제거안을 비교한다. 결과는 `outputs/prof_revision_motion_alignment_20261126`의 CSV·JSON·PNG로 저장한다. 별도 scalar 검증기를 같은 output 폴더에 보존했다. [최종 분석](../experiments/2026-11-26_prof_revision_motion_alignment.md)에 식·분모·한계·재현 명령을 기록했다.

## 결과와 영향

원본6.734→각도만 교체6.938(+3.0%)→힘 임계값도 제거7.266(+7.9%). 총 증가0.532의61.6%는 힘 임계값 제거에 해당한다. 변경 후에도 Formation 양의 비중44.6%, Sweep99.0%가 첫2초에 발생한다. 진입 후 실패157건의 평균 순보상도11.801→12.422로 증가한다. 보상 신호 크기는 유지되지만 최종 정착 문제가 해결된다는 증거는 아니다.

기존 환경 함수·Manager 설정·관측·PPO·종료·checkpoint는 수정하지 않았다. 기존 report_prof_revision_play.py 및 방향 분석 스크립트·기존 문서 작업트리와 사용자 PLAN22.md·IsaacLab 상태를 보존했다. 새 분석 스크립트·보고서·이 로그 및 현재 인계만 이번 변경에 해당한다.

## 검증과 미검증

- 원본 Sweep 재구성 step 오차≤1.99e−7, 이동 cosine 거리 항등식 오차≤1.47e−10.
- 전체254,165step 독립 scalar 재검산: episode 보상 최대 오차4.66e−8,512개 총보상 일치, 기존 terminal 성공334건 재확인.
- reset 경계 분리, 첫step512개 최근2/3접촉 거짓·Sweep0, 정지/이탈/비접촉 gating 및 상한 검사 통과.
- checkpoint SHA256 두 입력 동일·현재 파일 일치, 원시 trace 해시를 summary.json에 기록.
- 두 PNG 육안 확인, 방향별 bar 범위 확대하여 범례가 막대를 가리지 않게 수정.
- 새 보상 환경 live 실행·재학습·성공률 개선은 미검증. 최종 문서/구문 검증은 아래 완료 기록 참조.

완료 검증: 분석·독립 검증 Python 두 파일 py_compile 통과. 변경 Markdown3파일 수식 검사 통과, 외부 workspace 포함 링크 오류0(외부13·내부218). 루트·문서 저장소 git diff --check 통과(LF/CRLF 안내만 존재). seed42·43 수집 시점 manifest의 환경 패키지326파일씩을 현재 파일과 SHA256 대조하여 변경0을 확인했다. 원시 데이터와 환경 동작은 보존되어 있다.
