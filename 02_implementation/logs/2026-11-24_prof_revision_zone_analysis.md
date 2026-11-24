# Prof Revision 두 학습 정책의 Zone별 보상·손 자세 계측

## 요청·의도

사용자는 `logs/TEMP/2026-11-24`의 두 학습 결과를 대상으로 Joint Termination을 정상적인 평가 종료로 취급하고, Reaching·Sweep 거리/방향/접촉·Hand Tip 거리의 분포와 실제 행동을 네 방향 Zone별로 확인하도록 요청했다. 이번 작업은 보상 수정이나 재학습이 아닌 고정 정책 분석이다.

## 변경 전후와 영향

- 기준 루트 main은 `8ce37bfbfc7df5e85608f7c46f5b62d032e6869a`, 문서 저장소는 `cc69933d013a0a050aa360e2b984cae9ada05337`이다. 시작 시 IsaacLab의 기존 미추적 `2.7.0+cu128`을 보존했다.
- 기존 저장소에는 정지·속도 종료에 관한 문서가 있었지만, 이 PC에는 그 문서가 참조한 `outputs/prof_revision_stop_diagnosis/` 원시 산출물이 없었다. 기존 문서의 수치를 새 계측 결과로 대체하지 않고, 새 출력 폴더에서 재수집했다.
- `outputs/prof_revision_zone_analysis_20261124/`에 계측기·분석기·학습 scalar 추출·보고서 생성·문장 정리 스크립트와 소스 snapshot, 원본 파일 해시, 실제 trace를 추가했다. 활성 패키지·환경·보상·등록·PPO 파일은 수정하지 않았다.
- 문서 저장소에 [실측 보고서](../experiments/2026-11-24_prof_revision_zone_analysis.md)와 [검증·표·그림 자산](../../03_assets/prof_revision_zone_analysis_2026-11-24/)을 추가했다. 기존 파일은 덮어쓰지 않는다. 학습 로그·checkpoint·기존 출력·다른 서브모듈을 정리하거나 이동하지 않았다.
- 사용자 요청대로 원래 종료를 유지한 실제 terminal 상태까지 평가했다. 팔 속도 종료를 timeout으로 바꾸거나 정지 유지 성공으로 재분류하지 않았다. 별도 실패 감점을 추가하지 않고, 평가상 목표 도달은 종료 시 XY 거리≤3cm로 분리했다.

## 실제 실행과 최종 대조

v0 model6100과 Reach5cm model7950을 RTX4070·env_isaaclab Python에서 headless 재생했다. 각 seed42·43,256환경의 첫 episode로 정책마다512회·전체1,024회다. 정상 본 실행4회 모두 exit0·metadata complete·환경별 첫 terminal 수1을 확인했다. 물리 dt0.01s, policy dt0.02s, 원래 관측 noise와 결정론적 inference mean을 사용했다. 초기 관절·물체 state·목표·OBB·가상 Tip·방향 해시는 같은 seed의 두 정책에서 일치했다. checkpoint·학습 event·학습 설정·활성 패키지 Python 소스의 전후 해시도 같았다.

학습 env.yaml과 최종 평가 config의 전체 재귀 대조에서는 환경 수2048→256,seed43 추가,출력 경로,학습 PC→현재 PC의 robot USD 경로,PhysX aggregate-pair capacity2²⁵→2²¹만 달랐다. 보상·종료·관측·제어·reset의 의미상 설정은 같았다. 자산 원본 byte 동일성은 학습 PC 원본이 없어 검증하지 못했고 현재 자산 해시를 기록한다.

계측은 원래 contact.capture를 호출한 후 값을 복사하고 원래 RewardManager.compute를 한 번 호출한 직후, 자동 reset 전에 실제 기여와 물리 상태를 복사했다. 별도 noise 추출·관측 재계산·보상 재호출은 하지 않았다. 다음 episode는 분석에서 제외했다. 접촉 없는 episode는 성과 분모에서 유지하고 밀기 구간·방향 지표는 결측으로 구분했다. 처음에는 접촉 유지율의 조건부 모집단이 숨겨질 수 있어 접촉 개시 표본 수와 힘 방향 유효 표본 수도 명시하도록 보완했다.

- 목표 도달:447/512=87.3%,449/512=87.7%. Zone3은46/80=57.5%,41/80=51.3%다.
- 접촉 개시:489/512회·486/512회. 물체에 닿기 전 끝나는23·26회도 모두 성과 집계에 포함했다.
- 다섯 Tip 모두 OBB2cm 이내인 밀기 sample은0개다. 중지 중심 근접과 다른 Tip의 수cm 거리를 분리해 보고했다. 개별 손가락의 실제 힘 분배를 측정했다고 주장하지 않는다.
- numpy 독립 재계산의 최대 절대 보상 오차3.58e−7 이하,Tip–OBB 거리 오차8.95e−8m 이하,접촉 이력 Gate 불일치0개. 원래 총보상과 항별 합 차이3.58e−7 이하. 모든 대상 보상·거리 배열 유한,접촉 sample 유효율·sensor-fresh100%다.
- Zone별 평균·분위수·CSV·그림은 동일한 검토 결과에서 생성했다. 전체 성공률은 Zone별 성공 수를 합산해 대조했고, 손 자세·힘 각도의 결측 분모를 따로 확인했다. 대응episode bootstrap은 기술적 표본 변동 설명이며 훈련 인과로 사용하지 않았다.

## 실패·수정·검증 범위

최초8환경 smoke는 작업용 실행기에 패키지 root가 sys.path로 등록되지 않아 ModuleNotFoundError로 실패했다. 계측기 경로만 고친 두 번째 smoke는15step·보상합 대조를 통과했다. 첫 smoke의 process 반환값만으로 성공 판정하지 않았고 metadata 실패를 확인했다. 본 실행에는 어느 smoke도 포함하지 않았다.

보고서 생성 중 Python 문자열의 LaTeX escape가 변형된 것을 readback에서 발견해 raw 문자열로 수정했다. 문장 간격을 정리하고 표와 실제 보상 수치를 유지했다. 과학 그림은 실제 데이터로 matplotlib에서 생성했다. Zone 개요·힘/손가락 분포·3D Tip 그림을 눈으로 확인했고,3D 그림에서 축/행 제목 간격이 좁아 figure 크기와 tick 수·행 간격을 수정했다. 전체 그림은 동일 생성 경로의 실제 수치이며 렌더링 검수 범위는 최종 확인 목록을 따른다.

검증은 Python AST 구문, 보고서·개발 로그의 수식·내부 및 외부 workspace 링크, 새 파일 공백, 원본 해시 불변 대조로 마무리한다. 실제 수행 결과는 아래에 기록한다. GPU 학습·환경 수정·정지 유지 ablation·실물 실험·다른 checkpoint 모집단·추가된 Hand 보상의 훈련 인과는 미검증이다. 기존 학습 로그와 자산은 보존한다.

최종 검증 결과: 작업 Python6개 AST 구문 통과, 원본333개 파일 해시 불변, 수식6개 raw 문자열과 줄바꿈·제어문자 대조 통과, 새 문서·스크립트의 trailing whitespace 없음. Markdown2개 수식 검사 통과. 전체 문서671개 링크 검사 오류0개(internal5,676개), 새 문서2개의 workspace 외부 링크 포함 검사 오류0개(internal24·external8개)다. 처음 링크 검사에서 표 제목 `[p10,p90](cm)`이 링크로 해석되어 누락 경로로 표시된 문제는 단위 표기를 분리해 해결했다. 루트·문서 저장소 `git diff --check`와 새 Markdown의 no-index 공백 검사에서 공백 오류가 없었다. no-index의1 반환은 새 파일 차이 존재이며 공백 오류 출력은 없었다. 그림7개 모두 최종 내용을 눈으로 확인했고, 마지막3D 그림은 축 글자 잘림과 모서리 tick 겹침까지 수정해 재확인했다.

자산18개 약3.64MB를 문서 저장소에 추가했으며 원시trace와 학습scalar 전체는 출력 폴더에 보존했다. 현재 robot USD·tactile JSON과 분석 스크립트의 해시는 `analysis_sources.json`에 남겼다. 기존 사용자 변경은 그대로이며 이번 분석에 대한 커밋·푸시는 수행하지 않았다.

## 재현과 인계

[보고서의 재현 명령](../experiments/2026-11-24_prof_revision_zone_analysis.md#검증재현한계)과 `outputs/prof_revision_zone_analysis_20261124/collect.py`를 사용한다. 같은 폴더의 `training.py`, `analyze.py`, `extra.py`, `report.py`, `polish.py` 순서로 분석·보고서를 생성한다. 원시 재생은 checkpoint별 두 seed를 수집하고 기존 폴더를 덮어쓰지 않는다. 학습 종료 이벤트의 회피 동기 자체는 이번 요청의 분석 전제이며 다시 인과 검증하지 않았다.
