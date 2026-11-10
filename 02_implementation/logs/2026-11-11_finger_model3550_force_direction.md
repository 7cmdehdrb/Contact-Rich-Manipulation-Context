# 2026-11-11 Finger model3550 접촉 합력 방향 조사

## 요청과 작업 범위

사용자가 미는 동안 핸드가 타겟 물체에 가하는 최종 합력의 방향과 초기 물체 위치→목표점 벡터의 코사인 유사도를 최대한 원시 데이터로 비교하도록 요청했다. 목적은 방향 정렬 보상 항의 타당성 검사이며, 접근·목표 도달·미약한 힘으로 통계가 오염되지 않게 하는 조건이다.

환경이나 보상은 수정하지 않았다. `outputs/force_direction/`에 수집·집계·그림·audit 스크립트를 추가하고 기존 registered Finger-v0와 checkpoint3550을 실제 GPU PhysX에서 실행했다. 기존 파일 구조, submodule 커밋, 사용자 작업과 `logs/rsl_rl`은 보존했다.

## 구현과 전후 대조

- 이전 계측에는 접촉 합력 원시 데이터가 없어 별도 수집했다. 기존 object→hand filter의 물체 쪽 native PhysX view를 읽어 법선 및 마찰을 각각 보존한다. 기존 helper의 음수 반작용 부호는 사용하지 않는다.
- policy 입력·action 처리·제어·reward 결과는 유지하고, scene.update 뒤100Hz 읽기 hook과 reset 전 종료 정보 읽기 hook만 설치했다. sensor cfg를 변경하거나 새 sensor를 생성하지 않았다. 실행 후 hook을 해제한다.
- sparse contact point의 scalar/normal/point/separation과 friction vector/anchor,30개 hand filter별 벡터, 상태·action·goal·초기위치 등을 raw chunk로 저장했다. 미접촉·목표 도달 후·약한 힘 데이터도 보존한다.
- seed42 128환경×10회와 seed123 32환경×6회,1,472개 완료 episode·1,427,392개 물리 샘플. 주 분석은 최초 목표 진입 전 현재 접촉, 목표XY 거리>3cm, 물체XY 속력>=1cm/s, 수평 합력>=1N 등으로19,273개를 선택했다. 민감도와 실패 episode도 포함했다.
- 학습 저장 구성과 actions/observations/rewards/terminations/curriculum/decimation·physics dt가 일치했다. curriculum의 list/tuple 직렬화만 정규화했다. checkpoint 전후 SHA256은 `b64d17711f4c3d797e69e1529e46fe4dea79bdcc1ae0b12e5d6ba9e8e2b59642`로 동일했다.
- source commit `f75b3b09b402a0ecfdf3a378b5678fc6165e9a9e`, 시작 시의 기존 source 작업트리 변경 목록은 최종audit와 같다. 조사 산출물 외 source 파일 변경 없음.

## 결과와 검증

수평 합력 코사인 평균0.8528/중앙값0.9493,3D 평균0.8245. 법선만 사용하면XY 평균0.9138로 높아진다. 성공 episode의 샘플 평균0.9121, 실패0.6626. 목표 도달 후 접촉을 섞은 전체 contact 평균은-0.0352여서 구간 분리의 영향이 크다.

방향 항은 bounded 보조항 후보지만, 학습 효과나 최적 weight는 검증하지 않았다. fixed 초기 벡터를 쓰면 되돌리는 힘 일부를 벌줄 수 있고, 속력 gate를 학습에 그대로 쓰면 정지마찰에서 밀기 시작하는 신호를 잃을 수 있음을 기록했다.

- 두 실제 수집 모두 정상 종료·환경별 완료 quota 충족.
- 법선 point 독립 재구성과 matrix의 최대 차이0.0001221N, friction 재구성 차이0.0N, 힘 NaN/Inf0.
- 파생 force·초기 단위벡터로XY/3D cosine 재계산 일치, filter flow·최종 샘플수·설정 대조·checkpoint hash 일치.
- raw126파일별 SHA256 manifest 작성. 전체 CSV.gz 및 filtered CSV, episode CSV, NPZ, JSON 제공.
- plot3종의 PNG를 열어 축·레이블·조건·벡터 방향을 확인했다. 예시 quiver는 크기가 아니라 방향 비교용 정규화임을 표시했다.
- collector/analyzer/plot/audit 스크립트의 py_compile 통과. 전체/밀기 CSV를 실제로 읽어 행 수1,427,392/19,273 일치를 확인했다.
- 변경 문서2개의 수식·외부 파일 링크·whitespace 검사 통과. 전체 문서 저장소561개 Markdown 및 dataset 링크 검사도 오류0건이었다.

상세 수치·공식·재현 명령·원시 데이터 링크와 미검증 범위는 [실험 결과](../experiments/2026-11-11_finger_model3550_force_direction.md)에 모았다. [최종 audit](../../../../outputs/force_direction/analysis/audit.json)에서 모든 data/config 검사 결과를 확인할 수 있다.

미검증: 방향 보상 추가 후 학습 성능, 다른 checkpoint, 실기, 각 접촉의 인과적 역할, 제안한 gate/weight의 최적성. 이번 작업은 조사이며 보상 구현 변경을 수행하지 않았다.
